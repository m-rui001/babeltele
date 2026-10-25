# -*- coding: utf-8 -*-
# B79 建条目: 同一判决书四个声音(Loper Bright)。编码区数字 token 插值登记扁平契约; 落盘前断言同 B73。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C']
FILES = {
    'A': 'corpus/raw/changelog/sqlite_a.txt',
    'B': 'corpus/raw/changelog/sqlite_b.txt',
    'C': 'corpus/raw/changelog/sqlite_c.txt',
}
F = json.load(io.open('corpus/_b79meas.json', encoding='utf-8'))
REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B79V('%s')" % name if i is None else u"B79V('%s', %d)" % (name, i)
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
         io.open('corpus/_atoms79.txt', encoding='utf-8').read().splitlines()) if s.strip()]
for tg, a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中 %s: %s' % (tg, a[:50])

E = []
E.append(u'🧭 同一页更新日志(SQLite changes.html)切出的三个版本段, 同为 sqlite.org 折平面: 补丁版 3.54.1 %d 字符⇎特性版 3.54.0 %d⇎旧线补丁 3.53.4 %d ⇎ 句 %d⇎%d⇎%d 句——特性版的条目量是补丁版的十倍。'
         % (V('chars', 0), V('chars', 1), V('chars', 2),
            V('sents', 0), V('sents', 1), V('sents', 2)))

E.append(u'🔁 动词即版本类型: fix %d⇎%d⇎%d 处 ⇎ add %d⇎%d⇎%d 处、improve %d⇎%d⇎%d 处——补丁版只修不添, 特性版只添不修(0 处 fix); optimize 词族 %d⇎%d⇎%d 处全在特性版——它的优化正是两道补丁要修的回归来源。句集交集 A⇎B %d⇎A⇎C %d⇎B⇎C %d: 每版条目独立, 更新日志不复制自己。'
         % (V('fix', 0), V('fix', 1), V('fix', 2),
            V('add', 0), V('add', 1), V('add', 2),
            V('improve', 0), V('improve', 1), V('improve', 2),
            V('optimize', 0), V('optimize', 1), V('optimize', 2),
            V('sh_ab'), V('sh_ac'), V('sh_bc')))

E.append(u'⚖ 补丁指向母版的三种形态: A 指名道姓 ⟦A⟧⟨Fixes other problems in 3.54.0 reported by users.⟩(母版名 %d⇎%d⇎%d 处, reported by users %d⇎%d⇎%d 处)并另给溢出细节 ⟦A⟧⟨Fix a possible heap-buffer overflow on 32-bit builds.⟩(heap %d⇎%d⇎%d、32-bit %d⇎%d⇎%d); C 连修五版的整条谱系 ⟦C⟧⟨Fixes for problems in 3.53.0 (and 3.53.1, 3.53.2, and 3.53.3) mostly coming from AIs.⟩(lineage 3.53.3 %d⇎%d⇎%d 处)——并说出全书最刺眼的一句: 问题大多来自 AI。'
         % (V('ref_540', 0), V('ref_540', 1), V('ref_540', 2),
            V('reported_users', 0), V('reported_users', 1), V('reported_users', 2),
            V('heap', 0), V('heap', 1), V('heap', 2),
            V('bit32', 0), V('bit32', 1), V('bit32', 2),
            V('lineage', 0), V('lineage', 1), V('lineage', 2)))

E.append(u'🏛 体例指纹: 三段各有 Hashes: SQLITE_SOURCE_ID %d⇎%d⇎%d 处与 SHA3-256 %d⇎%d⇎%d 处——发布身份靠哈希锚定; 特性版的手写破损语法 "is now be" %d⇎%d⇎%d 处与 "The replaces" %d⇎%d⇎%d 处——条目写得快, 语法来不及修; 旧线补丁的 AI 自白 from AIs %d⇎%d⇎%d 处。'
         % (V('source_id', 0), V('source_id', 1), V('source_id', 2),
            V('hashes', 0), V('hashes', 1), V('hashes', 2),
            V('broken1', 0), V('broken1', 1), V('broken1', 2),
            V('broken2', 0), V('broken2', 1), V('broken2', 2),
            V('ais', 0), V('ais', 1), V('ais', 2)))

E.append(u'ℒ 方法 ⇒ 更新日志的隐性知识在版本类型与谱系指向: 动词分布把补丁版⇎特性版做成键(fix %d⇎%d⇎%d vs add %d⇎%d⇎%d), 句集交集把条目独立性做成键(%d/%d/%d), 指向母版的引用把谱系做成键(3.54.0 %d⇎%d⇎%d、3.53.3 %d⇎%d⇎%d), 语法破损与 AI 自白把书写过程做成键。'
         % (V('fix', 0), V('fix', 1), V('fix', 2), V('add', 0), V('add', 1), V('add', 2),
            V('sh_ab'), V('sh_ac'), V('sh_bc'),
            V('ref_540', 0), V('ref_540', 1), V('ref_540', 2),
            V('lineage', 0), V('lineage', 1), V('lineage', 2)))

enc = ''.join(E)

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

title = (u'# B79 同一页更新日志的三个版本段: SQLite 3.54.1⇎3.54.0⇎3.53.4——补丁版只修不添(%d/%d/%d 处 fix)而特性版只添不修, 旧线补丁自白问题大多来自 AI\n' % (F['fix'][0], F['fix'][1], F['fix'][2]))
srcline = (u'src: %s (%d 字符) ⇎ %s (%d 字符) ⇎ %s (%d 字符) '
           u'(三份同为 sqlite.org changes.html 的版本段: 补丁 3.54.1 ⇎ 特性 3.54.0 ⇎ 旧线补丁 3.53.4; '
           u'数字一律从面内现读, 一个都不手填; 抓取时刻与站点现行版本只在本机或站外成立, 不进门槛)\n'
           % (FILES['A'], F['chars'][0], FILES['B'], F['chars'][1], FILES['C'], F['chars'][2]))
tagsline = (u'tags: 动词分布键(fix⇎add) 谱系指向键(补丁指名母版) AI自白键 体例哈希锚 语法破损键 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B79_sqlite_changelog_three_releases.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b79flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B79 建条目: %s' % out)
print(u'编码区 %d 字符, 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
