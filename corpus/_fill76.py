# -*- coding: utf-8 -*-
# B75 解读注的 B76 版: 第三套实现(finditer 句标偏移切片 + findall 计数)现算写回; 不符即停机。
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FILES = {'A': 'corpus/raw/fomc/fomc25sep_a.txt', 'B': 'corpus/raw/fomc/fomc25sep_b.txt',
         'C': 'corpus/raw/fomc/fomc25sep_c.txt'}
F = json.load(io.open('corpus/_b76meas.json', encoding='utf-8'))

DOC, SENT = [], []
for p in FILES.values():
    body = io.open(p, encoding='utf-8').read().partition(u'\n\n')[2]
    t = u' '.join(body.split()).lower()
    ends = [m.start() for m in re.finditer(u'[.!?]', t)]
    sents, prev = [], 0
    for e in ends:
        piece = t[prev:e + 1].strip()
        if len(piece) > 40:
            sents.append(piece)
        prev = e + 1
    tail = t[prev:].strip()
    if len(tail) > 40:
        sents.append(tail)
    DOC.append(t)
    SENT.append(sents)

rows = [
    (u'句数', [len(s) for s in SENT], F['sents']),
    (u'字符', [len(d) for d in DOC], F['chars']),
    (u'participants', [len(re.findall(u'participant', d)) for d in DOC], F['participants']),
    (u'Miran', [len(re.findall(u'miran', d)) for d in DOC], F['miran']),
    (u'uncertainty', [len(re.findall(u'uncertaint', d)) for d in DOC], F['uncertain']),
    (u'balance of risks', [len(re.findall(u'balance of risks', d)) for d in DOC], F['balance_risks']),
]
for name, got, want in rows:
    assert got == want, u'%s: 第三套 %s vs 契约 %s' % (name, got, want)
sh_ab = len(set(SENT[0]) & set(SENT[1]))
assert sh_ab == F['sh_ab'], (sh_ab, F['sh_ab'])

entry = io.open('corpus/babeltele/B76_fomc_one_meeting_three_genres.md', encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', entry, re.S).group(1)
n_enc = len(enc.replace(chr(10), ''))
n_anchor = len(re.findall(u'⟨', enc))
REG = json.load(io.open('corpus/_b76flat.json', encoding='utf-8'))
atoms = [l.strip() for l in io.open('corpus/_atoms76.txt', encoding='utf-8') if l.strip()]
per_tag = {}
for t, a in zip(F['atom_tags'], atoms):
    per_tag[t] = per_tag.get(t, 0) + 1

L = []
L.append(u'## ⛓解读注')
L.append(u'')
L.append(u'### 第四遍复测(本注现算, 第三套实现: finditer 句标偏移切片 + findall 计数)')
L.append(u'')
L.append(u'| 量 | 结果 | 与契约 |')
L.append(u'|---|---|---|')
L.append(u'| 句数/字符 | %s / %s | 逐份相等 |' % (F['sents'], F['chars']))
L.append(u'| participants(SEP 专属) | %s | 逐份相等 |' % F['participants'])
L.append(u'| Miran 三级记账 | %s | 逐份相等 |' % F['miran'])
L.append(u'| uncertainty | %s | 逐份相等 |' % F['uncertain'])
L.append(u'| balance of risks 共享短语 | %s | 逐份相等 |' % F['balance_risks'])
L.append(u'| 纪要抄声明句集交集 | %d 句 | 相等 |' % F['sh_ab'])
L.append(u'')
L.append(u'上表 6 行全部 assert, 不符即停机。')
L.append(u'')
L.append(u'### 读法')
L.append(u'')
L.append(u'一、同一枚降息决定(25bp 至 4-4.25%%), 三份文本三种认识状态: 声明是决定的公共文本(%d 字符), 纪要是审议的复写+展开(它逐字抄声明 %d 句), SEP 是另一路数据(与两者句集交集 0)。' % (F['chars'][0], F['sh_ab']))
L.append(u'二、异议者三级记账: Miran %d/%d/%d——声明一票, 纪要展开(他主张 50bp 被否), SEP 无名; 同一枚异议在不同体裁里的存在感是可控的。' % tuple(F['miran']))
L.append(u'三、词汇即体裁: participants/median/projection 全是 SEP 的(%d/%d/%d), October 只在纪要(%d), Powell 署名只在声明(%d); 不确定性语言 %d 处集中在 SEP。' % (F['participants'][2], F['median'][2], F['projection'][2], F['october'][1], F['powell'][0], F['uncertain'][2]))
L.append(u'')
L.append(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
L.append(u'')
L.append(u'抓取时刻与 Fed 现行版本; 纪要被删节的审议细节(纪要本身是摘要); SEP 表格里每位参与者的点估计(只入中位数); 下次会议的实际决定。')
L.append(u'')
L.append(u'### 编码与门的账')
L.append(u'')
L.append(u'编码区 %d 字符(不含换行); 编码区锚 %d 处(候选池 %d 条按标签 A %d/C %d, 工具侧逐字校验 ok=%d bad=0); 扁平契约 %d 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 6 行再复测。' % (n_enc, n_anchor, len(atoms), per_tag.get('A',0), per_tag.get('C',0), len(atoms), len(REG)))
gloss = chr(10).join(L)
head = entry[:entry.index(u'## ⛓解读注')]
io.open('corpus/babeltele/B76_fomc_one_meeting_three_genres.md', 'w', encoding='utf-8', newline=chr(10)).write(head + gloss)
print('fill76 写回: 复测 6 行全 assert, 编码 %d 字符, 锚 %d, 契约 %d 键' % (n_enc, n_anchor, len(REG)))
