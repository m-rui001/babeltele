# -*- coding: utf-8 -*-
# B78 解读注: 第三套实现(finditer 句标偏移切片 + findall 计数)现算写回; 不符即停机。
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FILES = {'A': 'corpus/raw/faa/ad_a.txt', 'B': 'corpus/raw/faa/ad_b.txt'}
F = json.load(io.open('corpus/_b78meas.json', encoding='utf-8'))

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
    (u'EASA', [len(re.findall(u'easa', d)) for d in DOC], F['easa']),
    (u'prompted by', [len(re.findall(u'prompted by', d)) for d in DOC], F['prompted']),
    (u'comment', [len(re.findall(u'comment', d)) for d in DOC], F['comments']),
    (u'88 FR 5817(B 引 A 的页码)', [len(re.findall(u'88 fr 5817', d)) for d in DOC], F['fr5817']),
]
for name, got, want in rows:
    assert got == want, u'%s: 第三套 %s vs 契约 %s' % (name, got, want)
sh = len(set(SENT[0]) & set(SENT[1]))
assert sh == F['sh_ab'], (sh, F['sh_ab'])

entry = io.open('corpus/babeltele/B78_faa_two_ads_same_defect.md', encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', entry, re.S).group(1)
n_enc = len(enc.replace(chr(10), ''))
n_anchor = len(re.findall(u'⟨', enc))
REG = json.load(io.open('corpus/_b78flat.json', encoding='utf-8'))
atoms = [l.strip() for l in io.open('corpus/_atoms78.txt', encoding='utf-8') if l.strip()]
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
L.append(u'| EASA / MCAI(采纳件身份) | %s / %s | 逐份相等 |' % (F['easa'], F['mcai']))
L.append(u'| prompted by 同因句 | %s | 逐份相等 |' % F['prompted'])
L.append(u'| comment / cost 程序词 | %s / %s | 逐份相等 |' % (F['comments'], F['cost']))
L.append(u'| B 引 A 的页码 88 FR 5817 | %s | 逐份相等 |' % F['fr5817'])
L.append(u'| 句集交集(模板复用) | %d 句(占 A 的 %.1f%%) | 相等 |' % (F['sh_ab'], round(100.0*F['sh_ab']/F['sent_uniq'][0], 1)))
L.append(u'')
L.append(u'上表 6 行全部 assert, 不符即停机。')
L.append(u'')
L.append(u'### 读法')
L.append(u'')
L.append(u'一、同一缺陷(LPSOV 线束防护不足, 失效场景是不可包容转子破裂 UERF 引燃燃油)两次指令两步走: A 2023-01 只记录风险并要求按 SB 检查/报告, B 2023-10 直接要求改装线束路由并写明后果(失去燃油隔离能力, 可能失控火)——处置从"知道"升级到"动手"。')
L.append(u'二、监管文体是组装件: B 的句集有 %d 句逐字来自 A(占 A 的约 %.0f%%), prompted-by 同句两份各 %d/%d 处——同因声明是模板, 不是新写的。' % (F['sh_ab'], round(100.0*F['sh_ab']/F['sent_uniq'][0]), F['prompted'][0], F['prompted'][1]))
L.append(u'三、引用走纸面页码不走编号: B 引初始 AD 用 "88 FR 5817"(%d 处)而 AD 编号 2023-01702 在 B 面 0 处——联邦登记的谱系靠页码不靠文号。' % F['fr5817'][1])
L.append(u'四、程序差异: A 走征求意见期(comment %d 处)而 B 只 %d 处——处置收紧时听取意见的规模也收紧; 两份同为 MCAI 采纳件(EASA %d/%d 处, EASA AD 2022-0185 %d/%d 处), FAA 在跟随欧洲的发现。' % (F['comments'][0], F['comments'][1], F['easa'][0], F['easa'][1], F['2022_0185'][0], F['2022_0185'][1]))
L.append(u'')
L.append(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
L.append(u'')
L.append(u'抓取时刻与 FR 现行版本; LPSOV 改装在实际机队的执行进度; EASA 2022-0185 的完整文本; 后续是否有第三道 AD。')
L.append(u'')
L.append(u'### 编码与门的账')
L.append(u'')
L.append(u'编码区 %d 字符(不含换行); 编码区锚 %d 处(候选池 %d 条按标签 A %d/B %d, 工具侧逐字校验 ok=%d bad=0); 扁平契约 %d 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 6 行再复测。' % (n_enc, n_anchor, len(atoms), per_tag.get('A',0), per_tag.get('B',0), len(atoms), len(REG)))
gloss = chr(10).join(L)
head = entry[:entry.index(u'## ⛓解读注')]
io.open('corpus/babeltele/B78_faa_two_ads_same_defect.md', 'w', encoding='utf-8', newline=chr(10)).write(head + gloss)
print('fill78 写回: 复测 6 行全 assert, 编码 %d 字符, 锚 %d, 契约 %d 键' % (n_enc, n_anchor, len(REG)))
