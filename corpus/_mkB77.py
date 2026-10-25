# -*- coding: utf-8 -*-
# B77 建条目: 同一判决书四个声音(Loper Bright)。编码区数字 token 插值登记扁平契约; 落盘前断言同 B73。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C']
FILES = {
    'A': 'corpus/raw/arxiv/llama3_a.txt',
    'B': 'corpus/raw/arxiv/llama3_b.txt',
    'C': 'corpus/raw/arxiv/llama3_c.txt',
}
F = json.load(io.open('corpus/_b77meas.json', encoding='utf-8'))
REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B77V('%s')" % name if i is None else u"B77V('%s', %d)" % (name, i)
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
         io.open('corpus/_atoms77.txt', encoding='utf-8').read().splitlines()) if s.strip()]
for tg, a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中 %s: %s' % (tg, a[:50])

E = []
E.append(u'🧭 同一篇论文(The Llama 3 Herd of Models, arXiv 2407.21783)的三个版本, 同为 arxiv 原生 HTML 折平面: v1 %d 字符⇎v2 %d⇎v3 %d ⇎ 句 %d⇎%d⇎%d 句(三版句数完全相同), 每句均值 %d⇎%d⇎%d。'
         % (V('chars', 0), V('chars', 1), V('chars', 2),
            V('sents', 0), V('sents', 1), V('sents', 2),
            V('avg_sent', 0), V('avg_sent', 1), V('avg_sent', 2)))

E.append(u'🔁 正文不可变: 句集交集 A⇎B %d 句 ⇎ A⇎C %d 句 ⇎ B⇎C %d 句, 而三版去重句各 %d——互差只有个位数句, 且逐一看是元数据句(日期行/致谢/贡献者名单), 正文论述一句未动。词频三版全等: "llama 3 " %d⇎%d⇎%d 处、405 %d⇎%d⇎%d 处、safety %d⇎%d⇎%d 处、transformer %d⇎%d⇎%d 处、herd of models %d⇎%d⇎%d 处——与 B73 的 10-K(两年重写 47.8%% 句)恰成两极: 科学论文的正文跨版本冻结, 版本修的不是文本是账目。'
         % (V('sh_ab'), V('sh_ac'), V('sh_bc'), V('sent_uniq', 0),
            V('llama3', 0), V('llama3', 1), V('llama3', 2),
            V('b405', 0), V('b405', 1), V('b405', 2),
            V('safety', 0), V('safety', 1), V('safety', 2),
            V('transformer', 0), V('transformer', 1), V('transformer', 2),
            V('herd', 0), V('herd', 1), V('herd', 2)))

E.append(u'🗓 三个改动各落在哪一版: 日期行逐版独占——⟦A⟧⟨[cs.AI] 31 Jul 2024 The Llama 3 Herd of Models⟩ ⇎ ⟦B⟧⟨[cs.AI] 15 Aug 2024 The Llama 3 Herd of Models⟩ ⇎ ⟦C⟧⟨[cs.AI] 23 Nov 2024 The Llama 3 Herd of Models⟩(date_v1 %d⇎%d⇎%d 处 ⇎ date_v2 %d⇎%d⇎%d ⇎ date_v3 %d⇎%d⇎%d)。拼写错误致谢在 v2 即修: santosh jardanhan %d⇎%d⇎%d 处 ⇎ santosh janardhan %d⇎%d⇎%d 处。表 4 的缩放配置数字 v3 才修: "16 16 4 131,072" %d⇎%d⇎%d 处 ⇎ "16 16 8 131,072" %d⇎%d⇎%d 处——一个数字(批量配置)错了两版才被发现。贡献者名单 v3 重排: "core contributors aaron" %d⇎%d⇎%d 处。'
         % (V('date_v1', 0), V('date_v1', 1), V('date_v1', 2),
            V('date_v2', 0), V('date_v2', 1), V('date_v2', 2),
            V('date_v3', 0), V('date_v3', 1), V('date_v3', 2),
            V('jardanhan', 0), V('jardanhan', 1), V('jardanhan', 2),
            V('janardhan', 0), V('janardhan', 1), V('janardhan', 2),
            V('tbl4_old', 0), V('tbl4_old', 1), V('tbl4_old', 2),
            V('tbl4_new', 0), V('tbl4_new', 1), V('tbl4_new', 2),
            V('core_aaron', 0), V('core_aaron', 1), V('core_aaron', 2)))

E.append(u'ℒ 方法 ⇒ 论文版本的隐性知识不在"改了什么论述"(论述零改动), 而在版本账: 句集交集把正文冻结性做成键(%d⇎%d⇎%d, 互差个位数), 词频全等把不变轴做成键(llama 3 %d⇎%d⇎%d 等五族逐版相同), 三个元数据落点各自成键(日期行逐版独占、拼写错 v2 修、表 4 数字 v3 修)。'
         % (V('sh_ab'), V('sh_ac'), V('sh_bc'),
            V('llama3', 0), V('llama3', 1), V('llama3', 2)))

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

srcline = (u'src: %s (%d 字符) ⇎ %s (%d 字符) ⇎ %s (%d 字符) '
           u'(三份同为 arxiv 原生 HTML 折平面: arXiv 2407.21783 的 v1⇎v2⇎v3; '
           u'数字一律从面内现读, 一个都不手填; 抓取时刻与 arXiv 现行版本只在本机或站外成立, 不进门槛)\n'
           % (FILES['A'], F['chars'][0], FILES['B'], F['chars'][1], FILES['C'], F['chars'][2]))
tagsline = (u'tags: 正文冻结键(句集交集互差个位数) 词频全等轴 元数据三落点键(日期/拼写/表4) '
            u'锚归属由正文现推 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B77_llama3_versions_immutable_body.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b77flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B77 建条目: %s' % out)
print(u'编码区 %d 字符, 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
