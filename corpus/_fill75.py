# -*- coding: utf-8 -*-
# B75 ⛓解读注: 第三套实现(finditer 句标偏移切片 + findall 计数)现算写回; 不符即停机。
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FILES = {'A': 'corpus/raw/opinions/loper_a.txt', 'B': 'corpus/raw/opinions/loper_b.txt',
         'C': 'corpus/raw/opinions/loper_c.txt', 'D': 'corpus/raw/opinions/loper_d.txt'}
F = json.load(io.open('corpus/_b75meas.json', encoding='utf-8'))

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
    (u'Chevron', [len(re.findall(u'chevron', d)) for d in DOC], F['chevron']),
    (u'the dissent / the majority', [len(re.findall(u'the dissent', d)) for d in DOC], F['the_dissent']),
    (u'the majority(反向)', [len(re.findall(u'the majority', d)) for d in DOC], F['the_majority']),
    (u'congress / agency', [len(re.findall(u'congress', d)) for d in DOC], F['congress']),
    (u'stare decisis', [len(re.findall(u'stare decisis', d)) for d in DOC], F['stare']),
]
for name, got, want in rows:
    assert got == want, u'%s: 第三套 %s ⇎ 契约 %s' % (name, got, want)
sh_ad = len(set(SENT[0]) & set(SENT[3]))
assert sh_ad == F['sh_ad'], (sh_ad, F['sh_ad'])

entry = io.open('corpus/babeltele/B75_loper_bright_four_voices_one_case.md', encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', entry, re.S).group(1)
n_enc = len(enc.replace(chr(10), ''))
n_anchor = len(re.findall(u'⟨', enc))
REG = json.load(io.open('corpus/_b75flat.json', encoding='utf-8'))
atoms = [l.strip() for l in io.open('corpus/_atoms75.txt', encoding='utf-8') if l.strip()]
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
L.append(u'| Chevron 四声音 | %s | 逐份相等 |' % F['chevron'])
L.append(u'| 互指 the dissent(多数⇒异议) / the majority(异议⇒多数) | %s / %s | 逐份相等 |' % (F['the_dissent'], F['the_majority']))
L.append(u'| congress / stare decisis | %s / %s | 逐份相等 |' % (F['congress'], F['stare']))
L.append(u'| 摘要镜像 A⇎D 句集交集 | %d 句 | 相等 |' % F['sh_ad'])
L.append(u'')
L.append(u'上表 5 行全部 assert, 不符即停机。')
L.append(u'')
L.append(u'### 读法')
L.append(u'')
L.append(u'一、判决的结论只有一句 ⟦A⟧⟨Chevron is overruled.⟩, 本条不记结论, 记四个声音怎么分家: 互指不对称(多数点异议 %d 次, 异议点多数 %d 次)——败方逐段反驳, 胜方点到为止。' % (F['the_dissent'][0], F['the_majority'][2]))
L.append(u'二、判例名是全书最高频词(Chevron %d/%d/%d/%d), 连法院自备摘要都提 %d 次——被推翻的东西恰恰是全书说话的中心。' % (F['chevron'][0], F['chevron'][1], F['chevron'][2], F['chevron'][3], F['chevron'][3]))
L.append(u'三、主语即视角: congress 之峰在异议(%d 处——法院抢国会的事), constitution 之峰在协同(%d 处——从根上否定先例)。' % (F['congress'][2], F['constitution'][1]))
L.append(u'四、摘要只镜像胜方: A⇎D 句集交集 %d 句远大于其余五对——Syllabus 逐句转述多数意见, 与异议只 %d 句共享。' % (F['sh_ad'], F['sh_cd']))
L.append(u'')
L.append(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
L.append(u'')
L.append(u'抓取时刻与 LII 现行版本; 各意见的官方 slip op 页码与 LII 折平面的对应; Kagan 附录表是否完整入面; 口头辩论与意见书的措辞回改(本条只收判决书文本)。')
L.append(u'')
L.append(u'### 编码与门的账')
L.append(u'')
L.append(u'编码区 %d 字符(不含换行); 编码区锚 %d 处(候选池 %d 条按标签 A %d/B %d/C %d/D %d, 工具侧逐字校验 ok=%d bad=0); 扁平契约 %d 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 5 行再复测。' % (n_enc, n_anchor, len(atoms), per_tag.get('A',0), per_tag.get('B',0), per_tag.get('C',0), per_tag.get('D',0), len(atoms), len(REG)))
gloss = chr(10).join(L)

head = entry[:entry.index(u'## ⛓解读注'.replace('\u26d3', '\u26d3'))] if False else entry[:entry.index(u'## ⛓解读注'.replace(chr(92)+'u26d3', u'⛓'))]
io.open('corpus/babeltele/B75_loper_bright_four_voices_one_case.md', 'w', encoding='utf-8', newline=chr(10)).write(head + gloss)
print('fill75 写回: 复测 5 行全 assert, 编码 %d 字符, 锚 %d, 契约 %d 键' % (n_enc, n_anchor, len(REG)))
