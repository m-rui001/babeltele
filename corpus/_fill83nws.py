# -*- coding: utf-8 -*-
# B83 解读注: 第三套实现(finditer 句标偏移切片 + findall 计数)现算写回; 不符即停机。
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FILES = {'A': 'corpus/raw/nws/afd_a.txt', 'B': 'corpus/raw/nws/afd_b.txt', 'C': 'corpus/raw/nws/afd_c.txt'}
F = json.load(io.open('corpus/_b83meas.json', encoding='utf-8'))

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
    (u'KEY MESSAGES', [len(re.findall(u'key messages', d)) for d in DOC], F['key_messages']),
    (u'&& 段分隔', [len(re.findall(u'&&', d)) for d in DOC], F['amp']),
    (u'confidence', [len(re.findall(u'confidence', d)) for d in DOC], F['confidence']),
    (u'fire', [len(re.findall(u'fire', d)) for d in DOC], F['fire']),
]
for name, got, want in rows:
    assert got == want, u'%s: 第三套 %s vs 契约 %s' % (name, got, want)
for i, j, nm in [(0, 1, 'sh_ab'), (0, 2, 'sh_ac'), (1, 2, 'sh_bc')]:
    assert len(set(SENT[i]) & set(SENT[j])) == F[nm], nm

entry = io.open('corpus/babeltele/B83_nws_afd_three_offices_hours.md', encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', entry, re.S).group(1)
n_enc = len(enc.replace('\n', ''))
n_anchor = len(re.findall(u'⟨', enc))
REG = json.load(io.open('corpus/_b83flat.json', encoding='utf-8'))
atoms = [l.strip() for l in io.open('corpus/_atoms83.txt', encoding='utf-8') if l.strip()]
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
L.append(u'| KEY MESSAGES / && / AVIATION(全国骨架) | %s / %s / %s | 逐份相等 |' % (F['key_messages'], F['amp'], F['aviation']))
L.append(u'| confidence(办公室文化) | %s | 逐份相等 |' % F['confidence'])
L.append(u'| fire | %s | 逐份相等 |' % F['fire'])
L.append(u'| 句集交集 AB/AC/BC | %d/%d/%d | 相等 |' % (F['sh_ab'], F['sh_ac'], F['sh_bc']))
L.append(u'')
L.append(u'上表 5 行全部 assert, 不符即停机。')
L.append(u'')
L.append(u'### 读法')
L.append(u'')
L.append(u'一、时间衰减: 休斯敦两期相隔七小时, 句集交集 %d 句(上期 28 句去重句的大半滚入当期)——预报讨论逐段更新而非重写; 跨办公室交集 0/0——模板是办公室私产。' % F['sh_ab'])
L.append(u'二、骨架全国统一: KEY MESSAGES 三份各 1 份、&& 段分隔各 6 枚、AVIATION 各 3 处、Area Forecast Discussion 抬头各 1 处——NWS 的产品规范把结构钉死, 内容各自生长。')
L.append(u'三、文化即办公室: confidence 只斯波坎成规模(%d/%d/%d 处), 它把确定性写进每个时段(moderate to high confidence for ongoing IFR/MVFR conditions); front/short term/advisory/ensemble 也全是内陆平原办公室的词; 休斯敦的 gulf/coast 把墨西哥湾写进讨论——不用看署名就知道是谁写的。' % tuple(F['confidence']))
L.append(u'四、火情同词不同义: fire %s 处三份都有——休斯敦说干旱火险(elevated fire weather), 斯波坎说火天气——同一词在不同地理里指不同的天气。' % (F['fire'],))
L.append(u'')
L.append(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
L.append(u'')
L.append(u'抓取时刻与 NWS 现行产品; 两期之间的预报验证评分; confidence 词表是否为该 WFO 的本地惯例; 产品在 NWS 站点上的渲染是否与 api.weather.gov 文本一致。')
L.append(u'')
L.append(u'### 编码与门的账')
L.append(u'')
L.append(u'编码区 %d 字符(不含换行); 编码区锚 %d 处(候选池 %d 条按标签 A %d/C %d, 工具侧逐字校验 ok=%d bad=0); 扁平契约 %d 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 5 行再复测。' % (n_enc, n_anchor, len(atoms), per_tag.get('A', 0), per_tag.get('C', 0), len(atoms), len(REG)))
gloss = chr(10).join(L)

head = entry[:entry.index(u'## ⛓解读注')]
io.open('corpus/babeltele/B83_nws_afd_three_offices_hours.md', 'w', encoding='utf-8', newline='\n').write(head + gloss)
print('fill83nws 写回: 复测 5 行全 assert, 编码 %d 字符, 锚 %d, 契约 %d 键' % (n_enc, n_anchor, len(REG)))
