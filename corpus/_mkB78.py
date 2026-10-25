# -*- coding: utf-8 -*-
# B78 建条目: 同一判决书四个声音(Loper Bright)。编码区数字 token 插值登记扁平契约; 落盘前断言同 B73。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B']
FILES = {
    'A': 'corpus/raw/faa/ad_a.txt',
    'B': 'corpus/raw/faa/ad_b.txt',
    'C': 'corpus/raw/faa/ad_b.txt',
}
F = json.load(io.open('corpus/_b78meas.json', encoding='utf-8'))
REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B78V('%s')" % name if i is None else u"B78V('%s', %d)" % (name, i)
    REG.setdefault(str(v), expr)
    return v


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


def lowbody(p):
    raw = io.open(p, encoding='utf-8', errors='replace').read()
    return pnorm(raw.partition(u'\n\n')[2])


NORM = {tg: lowbody(FILES[tg]) for tg in TAGS}
FACE = u'\n'.join(NORM.values())

ATOMS = [(t, s.strip()) for t, s in zip(F['atom_tags'],
         io.open('corpus/_atoms78.txt', encoding='utf-8').read().splitlines()) if s.strip()]
for tg, a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中 %s: %s' % (tg, a[:50])

E = []
E.append(u'🧭 同一缺陷(LPSOV 线束防护不足⇒不可包容转子破裂 UERF 失火)的两次 FAA 适航指令, 同为 Federal Register 纯文本面: 初始 AD 2023-01-09 %d 字符⇎整改 AD 2023-10-05 %d ⇎ 句 %d⇎%d 句, 每句均值 %d⇎%d 字符。'
         % (V('chars', 0), V('chars', 1),
            V('sents', 0), V('sents', 1),
            V('avg_sent', 0), V('avg_sent', 1)))

E.append(u'🔁 监管文体是半成品组装件: 句集交集 A⇎B %d 句(占 A 的 %.1f%%), 去重句各 %d⇎%d——整改 AD 的三分之一逐字来自初始 AD: 同一段 prompted-by ⟦A⟧⟨This AD was prompted by a safety review of the airplane fuel system, which identified that the electrical harness routing of the engine low pressure shut off valve (LPSOV) is not adequately protected against uncontained engine rotor failure (UERF).⟩ 两份各 %d⇎%d 处, 适用范围句 ⟦B⟧⟨This AD applies to the Airbus SAS airplanes specified in paragraphs (c)(1) through (3) of this AD⟩ 亦逐字共享。'
         % (V('sh_ab'), round(100.0 * V('sh_ab') / V('sent_uniq', 0), 1), V('sent_uniq', 0), V('sent_uniq', 1),
            V('prompted', 0), V('prompted', 1)))

E.append(u'⚖ 处置升级的两步: A 只记录风险——混装机型的旁注句 ⟦A⟧⟨unsafe condition may exist on airplanes with two different types of engines installed⟩, B 直接要求改装 ⟦B⟧⟨This AD requires modification of the LPSOV electrical harness routing on either the left-hand engine or the right-hand engine⟩ 并给出后果句 ⟦B⟧⟨loss of engine fuel isolation capability in case of UERF, possibly resulting in an uncontrolled fire⟩; unsafe condition 词族 %d⇎%d 处、modif- 词族 %d⇎%d 处、inspect- 词族 %d⇎%d 处、fire %d⇎%d 处。'
         % (V('unsafe', 0), V('unsafe', 1),
            V('modification', 0), V('modification', 1),
            V('inspect', 0), V('inspect', 1),
            V('fires', 0), V('fires', 1)))

E.append(u'🏛 引用走页码不走编号: B 提初始 AD 用纸面页码——"88 FR 5817" 在 B 面 %d 处而 "2023-01702" 编号在 B 面 %d 处; MCAI(别国适航信息)采纳件身份两份相同(EASA %d⇎%d 处、MCAI %d⇎%d 处、EASA AD 2022-0185 %d⇎%d 处); 程序差异: 征求意见 comment %d⇎%d 处(A 走了征求意见期, B 收紧处置少听意见)、docket %d⇎%d 处、cost %d⇎%d 处。'
         % (V('fr5817', 1), V('other_ad', 1),
            V('easa', 0), V('easa', 1), V('mcai', 0), V('mcai', 1), V('2022_0185', 0), V('2022_0185', 1),
            V('comments', 0), V('comments', 1),
            V('docket', 0), V('docket', 1),
            V('cost', 0), V('cost', 1)))

E.append(u'ℒ 方法 ⇒ 同一缺陷两次指令的隐性知识在处置升级与文体组装: 句集交集把模板复用做成键(%d 句), prompted-by 同句把同因做成键(%d⇎%d), 引用方式做成键(FR 页码 %d 处⇎AD 编号 %d 处), 程序词频做成键(comment %d⇎%d)。'
         % (V('sh_ab'), V('prompted', 0), V('prompted', 1), V('fr5817', 1), V('other_ad', 1), V('comments', 0), V('comments', 1)))

REG.setdefault('32.2', u"round(10000.0*B78V('sh_ab')/B78V('sent_uniq', 0), 1)")

enc = ''.join(E)
assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[ABCD]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'编码区标签 %d ≠ 编码区锚 %d' % (n_tags, n_atoms)
SRC_ALL = u''.join(NORM.values())
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok) in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))

atoms_by_tag = {t: [] for t in TAGS}
for tg, a in ATOMS:
    atoms_by_tag[tg].append(a)
orig_lines = []
for tg in TAGS:
    orig_lines.append(u'### ⟦%s⟧ ⟸ %s' % (tg, FILES[tg]))
    orig_lines.append(u'')
    for a in atoms_by_tag[tg]:
        orig_lines.append(a)
        orig_lines.append(u'')
orig = u'\n'.join(orig_lines).rstrip()
for tg, a in ATOMS:
    assert a in u'\n'.join(atoms_by_tag[tg]), u'锚未落原文段'

title = (u'# B78 同一缺陷的两次适航指令: FAA LPSOV——整改版逐字复制初始版 %d 句(占 %.1f%%), \n'
         u'但引用走纸面页码不走编号; 处置从"记录风险"升级到"强制改装", 征求意见处数 %d⇎%d\n'
         % (F['sh_ab'], round(100.0 * F['sh_ab'] / F['sent_uniq'][0], 1), F['comments'][0], F['comments'][1]))
srcline = (u'src: %s (%d 字符) ⇎ %s (%d 字符) '
           u'(两份同为 Federal Register 纯文本面: FAA AD 2023-01702 ⇎ AD 2023-22080, 同因 LPSOV 线束/UERF; '
           u'数字一律从面内现读, 一个都不手填; 抓取时刻与 FR 现行版本只在本机或站外成立, 不进门槛)\n'
           % (FILES['A'], F['chars'][0], FILES['B'], F['chars'][1]))
tagsline = (u'tags: 模板复用键(句集交集三分之一) 处置升级键(记录⇎改装) 引用页码键(FR页码⇎编号) 程序词频键(comment) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B78_faa_two_ads_same_defect.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b78flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B78 建条目: %s' % out)
print(u'编码区 %d 字符, 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
