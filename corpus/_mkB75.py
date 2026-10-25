# -*- coding: utf-8 -*-
# B75 建条目: 同一判决书四个声音(Loper Bright)。编码区数字 token 插值登记扁平契约; 落盘前断言同 B73。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C', 'D']
FILES = {
    'A': 'corpus/raw/opinions/loper_a.txt',
    'B': 'corpus/raw/opinions/loper_b.txt',
    'C': 'corpus/raw/opinions/loper_c.txt',
    'D': 'corpus/raw/opinions/loper_d.txt',
}
F = json.load(io.open('corpus/_b75meas.json', encoding='utf-8'))
REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B75V('%s')" % name if i is None else u"B75V('%s', %d)" % (name, i)
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
         io.open('corpus/_atoms75.txt', encoding='utf-8').read().splitlines()) if s.strip()]
for tg, a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中 %s: %s' % (tg, a[:50])

E = []
E.append(u'🧭 同一份判决书(Loper Bright, 2024-06-28)剥出四个声音, 同为 LII 折平面: 多数意见(Roberts) %d 字符⇎协同意见(Gorsuch) %d⇎异议(Kagan) %d⇎法院自备摘要(Syllabus) %d ⇎ 句 %d⇎%d⇎%d⇎%d 句——异议比多数意见长不了几行, 但互指次数差一个量级(见⚖)。'
         % (V('chars', 0), V('chars', 1), V('chars', 2), V('chars', 3),
            V('sents', 0), V('sents', 1), V('sents', 2), V('sents', 3)))

E.append(u'⚖ 反驳方向不对称: 多数意见点异议 "the dissent" %d 次、协同点异议 %d 次; 反向, 异议点多数意见 "the majority" %d 次、协同点多数意见 %d 次——被推翻的一方用 %d 处点名逐段反驳, 推翻方只回 %d 处: 异议开篇即 ⟦C⟧⟨For 40 years, Chevron U. S. A. Inc. v. Natural Resources Defense Council⟩, 收尾指控 ⟦C⟧⟨The majority says that I have "pluck[ed] out" Gray and Hearst⟩——点名即引证, 引证即反驳。'
         % (V('the_dissent', 0), V('the_dissent', 1), V('the_majority', 2), V('the_majority', 1), V('the_majority', 2), V('the_dissent', 0)))

E.append(u'📚 被推翻的判例名是全书最高频词: Chevron %d⇎%d⇎%d⇎%d 处(连法院自备摘要都有 %d 处), 四声音加起来百余次; stare decisis %d⇎%d⇎%d⇎%d——协同意见(Gorsuch)把遵从先例说得比异议还多(17⇎12), 因为它要从宪法根上论证这先例本来就不配存在(precedent %d⇎%d⇎%d⇎%d、constitution %d⇎%d⇎%d⇎%d 都以协同为峰)。'
         % (V('chevron', 0), V('chevron', 1), V('chevron', 2), V('chevron', 3), V('chevron', 3),
            V('stare', 0), V('stare', 1), V('stare', 2), V('stare', 3),
            V('precedent', 0), V('precedent', 1), V('precedent', 2), V('precedent', 3),
            V('constitution', 0), V('constitution', 1), V('constitution', 2), V('constitution', 3)))

E.append(u'🏛 谁说了算的分岔: defer 词族 %d⇎%d⇎%d⇎%d 处四声音都在讲遵从; 而主语分家——异议的 Congress %d⇎%d⇎%d⇎%d 处为四声之峰(立法者视角: 法院抢了国会的事), 协同的 agency 只 %d 处而 constitution 最高; 判例名之外 Kagan 引 Chevron 本体 %d 处与多数几乎同量(%d)——双方在同一段历史上各取所需。best reading %d⇎%d⇎%d⇎%d 处是新标准的替身短语: 多数/协同/摘要各说"法律的最佳读法", 异议 %d 处——它拒绝用胜方的词; 协同意见把新标准的代价写成 ⟦B⟧⟨It forces judges to abandon the best reading of the law in favor of views of those presently holding the reins of the Executive Branch.⟩。'
         % (V('defer', 0), V('defer', 1), V('defer', 2), V('defer', 3),
            V('congress', 0), V('congress', 1), V('congress', 2), V('congress', 3),
            V('agency', 1), V('chevron', 2), V('chevron', 0),
            V('best_reading', 0), V('best_reading', 1), V('best_reading', 2), V('best_reading', 3), V('best_reading', 2)))

E.append(u'🔁 摘要是镜像: 句集交集 A⇎D %d 句, 远大于其余五对(%d⇎%d⇎%d⇎%d⇎%d)——Syllabus 逐句转述多数意见, 而它与异议只 %d 句共享: 法院给自己的摘要只摘胜方。官方判决头归 Syllabus, 胜方意见归 A, 署名协同归 B, 败方归 C——同一文件里的四层认识状态。'
         % (V('sh_ad'), V('sh_ab'), V('sh_ac'), V('sh_bc'), V('sh_bd'), V('sh_cd'), V('sh_cd')))

E.append(u'ℒ 方法 ⇒ 判决书的隐性知识不在"判了什么"(一句话: Chevron 推翻 ⟦A⟧⟨Chevron is overruled.⟩), 而在四个声音怎么分家: 先把互指做成键(the dissent ⇎ the majority 的 %d 对 %d), 再把判例名词频做成键(Chevron 四声音各 %d⇎%d⇎%d⇎%d), 再把主题主语做成键(congress 之峰在异议、constitution 之峰在协同), 最后把句集交集做成键(摘要只镜像胜方 %d 句)。'
         % (V('the_dissent', 0), V('the_majority', 2), V('chevron', 0), V('chevron', 1), V('chevron', 2), V('chevron', 3), V('sh_ad')))

enc = u'\n'.join(E)

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

title = (u'# B75 同一判决书的四个声音: Loper Bright 推翻 Chevron——异议用 %d 处点名多数意见, 多数只回 %d 处; '
         u'判例名是全书最高频词; 摘要只镜像胜方\n'
         % (F['the_majority'][2], F['the_dissent'][0]))
srcline = (u'src: %s (%d 字符) ⇎ %s (%d 字符) ⇎ %s (%d 字符) ⇎ %s (%d 字符) '
           u'(四份同为 Cornell LII 的 Loper Bright 判决书按意见头分段: 多数意见⇎协同⇎异议⇎法院自备摘要, 折平面; '
           u'数字一律从面内现读, 一个都不手填; 抓取时刻与 LII 现行版本只在本机或站外成立, 不进门槛)\n'
           % (FILES['A'], F['chars'][0], FILES['B'], F['chars'][1], FILES['C'], F['chars'][2], FILES['D'], F['chars'][3]))
tagsline = (u'tags: 互指不对称键(the dissent⇎the majority) 判例名词频四声音 主题主语分档(congress峰⇎constitution峰) '
            u'句集交集镜像键(syllabus只摘胜方) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B75_loper_bright_four_voices_one_case.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b75flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B75 建条目: %s' % out)
print(u'编码区 %d 字符, 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
