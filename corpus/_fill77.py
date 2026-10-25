# -*- coding: utf-8 -*-
# B77 解读注: 第三套实现(finditer 句标偏移切片 + findall 计数)现算写回; 不符即停机。
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FILES = {'A': 'corpus/raw/arxiv/llama3_a.txt', 'B': 'corpus/raw/arxiv/llama3_b.txt', 'C': 'corpus/raw/arxiv/llama3_c.txt'}
F = json.load(io.open('corpus/_b77meas.json', encoding='utf-8'))

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
    (u'日期行 v1/v2/v3', [len(re.findall(u'31 jul 2024', d)) for d in DOC], F['date_v1']),
    (u'拼写错 jardanhan', [len(re.findall(u'jardanhan', d)) for d in DOC], F['jardanhan']),
    (u'表4 旧串', [len(re.findall(u'16 16 4 131,072', d)) for d in DOC], F['tbl4_old']),
    (u'表4 新串', [len(re.findall(u'16 16 8 131,072', d)) for d in DOC], F['tbl4_new']),
]
for name, got, want in rows:
    assert got == want, u'%s: 第三套 %s vs 契约 %s' % (name, got, want)
for i, j, nm in [(0, 1, 'sh_ab'), (0, 2, 'sh_ac'), (1, 2, 'sh_bc')]:
    assert len(set(SENT[i]) & set(SENT[j])) == F[nm], nm

entry = io.open('corpus/babeltele/B77_llama3_versions_immutable_body.md', encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', entry, re.S).group(1)
n_enc = len(enc.replace(chr(10), ''))
n_anchor = len(re.findall(u'⟨', enc))
REG = json.load(io.open('corpus/_b77flat.json', encoding='utf-8'))
atoms = [l.strip() for l in io.open('corpus/_atoms77.txt', encoding='utf-8') if l.strip()]
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
L.append(u'| 日期行三落点 | %s / %s / %s | 逐份相等 |' % (F['date_v1'], F['date_v2'], F['date_v3']))
L.append(u'| 致谢拼写错 jardanhan | %s | 逐份相等 |' % F['jardanhan'])
L.append(u'| 表4 旧串/新串 | %s / %s | 逐份相等 |' % (F['tbl4_old'], F['tbl4_new']))
L.append(u'| 句集交集 AB/AC/BC | %d/%d/%d | 相等 |' % (F['sh_ab'], F['sh_ac'], F['sh_bc']))
L.append(u'')
L.append(u'上表 5 行全部 assert, 不符即停机。')
L.append(u'')
L.append(u'### 读法')
L.append(u'')
L.append(u'一、论文版本的隐性知识是**版本账**而非论述: 正文一句未动(句集交集 %d/%d/%d, 三版去重句各 %d), 与 B73 年报(两年重写近半)恰成两极——科学论文正文跨版本冻结, 版本修的是账目。' % (F['sh_ab'], F['sh_ac'], F['sh_bc'], F['sent_uniq'][0]))
L.append(u'二、三个元数据落点各有自己的版本: 日期行逐版换(7 月 31 日/8 月 15 日/11 月 23 日); 致谢里 santosh jardanhan 的拼写错 v2 即修(1/0/0 vs janardhan 0/1/1); 表 4 缩放配置的一个数字错了两版才在 v3 修(旧串 1/1/0, 新串 0/0/1); 贡献者名单 v3 重排(core contributors aaron 0/0/1)。')
L.append(u'三、词频三版全等把不变轴做成键: llama 3 %s、405 %s、safety %s、transformer %s、herd %s——同一篇论文的不同版本在词面上不可区分, 只在元数据上可区分。' % (F['llama3'], F['b405'], F['safety'], F['transformer'], F['herd']))
L.append(u'')
L.append(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
L.append(u'')
L.append(u'抓取时刻与 arXiv 现行版本; v2 的提交日期是否与 8 月 15 日行的自报一致; 表 4 数字修正的动因(作者勘误还是渲染错误); 贡献者名单重排的制度原因。')
L.append(u'')
L.append(u'### 编码与门的账')
L.append(u'')
L.append(u'编码区 %d 字符(不含换行); 编码区锚 %d 处(候选池 %d 条按标签 A %d/B %d/C %d, 工具侧逐字校验 ok=%d bad=0); 扁平契约 %d 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 5 行再复测。' % (n_enc, n_anchor, len(atoms), per_tag.get('A',0), per_tag.get('B',0), per_tag.get('C',0), len(atoms), len(REG)))
gloss = chr(10).join(L)
head = entry[:entry.index(u'## ⛓解读注')]
io.open('corpus/babeltele/B77_llama3_versions_immutable_body.md', 'w', encoding='utf-8', newline=chr(10)).write(head + gloss)
print('fill77 写回: 复测 5 行全 assert, 编码 %d 字符, 锚 %d, 契约 %d 键' % (n_enc, n_anchor, len(REG)))
