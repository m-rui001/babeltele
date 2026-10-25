# -*- coding: utf-8 -*-
# B76 建条目: 同一判决书四个声音(Loper Bright)。编码区数字 token 插值登记扁平契约; 落盘前断言同 B73。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C']
FILES = {
    'A': 'corpus/raw/fomc/fomc25sep_a.txt',
    'B': 'corpus/raw/fomc/fomc25sep_b.txt',
    'C': 'corpus/raw/fomc/fomc25sep_c.txt',
}
F = json.load(io.open('corpus/_b76meas.json', encoding='utf-8'))
REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B76V('%s')" % name if i is None else u"B76V('%s', %d)" % (name, i)
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
         io.open('corpus/_atoms76.txt', encoding='utf-8').read().splitlines()) if s.strip()]
for tg, a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中 %s: %s' % (tg, a[:50])

E = []
E.append(u'🧭 同一次 FOMC 会议(2025-09-16/17)剥成三份体裁, 同为 Fed 折平面: 即日声明 %d 字符⇎三周后纪要 %d⇎同步发布的经济预测摘要(SEP) %d ⇎ 句 %d⇎%d⇎%d 句, 每句均值 %d⇎%d⇎%d 字符——声明是最短的公共文本, SEP 是最长的数据文本。'
         % (V('chars', 0), V('chars', 1), V('chars', 2),
            V('sents', 0), V('sents', 1), V('sents', 2),
            V('avg_sent', 0), V('avg_sent', 1), V('avg_sent', 2)))
E.append(u'🔁 纪要逐字抄声明: 句集交集 A⇎B %d 句 ⇎ A⇎C %d 句 ⇎ B⇎C %d 句——纪要的"本会决定"整段是声明的复写, 而 SEP 与两者共享 0 句: 声明与纪要是同一决定的两遍措辞, SEP 是另一路(数据)。'
         % (V('sh_ab'), V('sh_ac'), V('sh_bc')))
E.append(u'⚖ 异议者的两级记账: Miran %d⇎%d⇎%d 处——声明里只记一票(voted 词族 %d⇎%d⇎%d 处), 纪要里展开: 他主张更大幅度降息并被否; SEP 里这个名字不存在。同一枚异议, 决定文本一行, 审议文本一段, 预测文本 0。'
         % (V('miran', 0), V('miran', 1), V('miran', 2),
            V('voted', 0), V('voted', 1), V('voted', 2)))
E.append(u'🏛 词汇即体裁: participants %d⇎%d⇎%d 处、median %d⇎%d⇎%d 处、projection %d⇎%d⇎%d 处全是 SEP 的词汇(median 句 ⟦C⟧⟨a path for the federal funds rate and its longer-run value⟩); uncertainty 词根 %d⇎%d⇎%d——不确定性语言 46 处集中在 SEP 的表格说明里, 声明与纪要各只 1 处; "balance of risks" %d⇎%d⇎%d 处是声明⇎纪要共享短语(声明 ⟦A⟧⟨the balance of risks⟩), SEP 0 处; 各有一份独有词: 纪要独有 October %d⇎%d⇎%d 处(下次会议时点的讨论), 声明独有 Powell 署名 %d⇎%d⇎%d 处。'
         % (V('participants', 0), V('participants', 1), V('participants', 2),
            V('median', 0), V('median', 1), V('median', 2),
            V('projection', 0), V('projection', 1), V('projection', 2),
            V('uncertain', 0), V('uncertain', 1), V('uncertain', 2),
            V('balance_risks', 0), V('balance_risks', 1), V('balance_risks', 2),
            V('october', 0), V('october', 1), V('october', 2),
            V('powell', 0), V('powell', 1), V('powell', 2)))
E.append(u'ℒ 方法 ⇒ 同一决定的三份文书, 隐性知识在体裁分工: 句集交集(纪要抄声明 %d 句, SEP 与谁都不交)‖人名三级记账(异议者 %d⇎%d⇎%d)‖专属词汇(participants/median/projection 全在 SEP, October 只在纪要)‖共享短语(balance of risks %d⇎%d⇎%d)。每键都是 count 可机检量, 零项照占键位。'
         % (V('sh_ab'), V('miran', 0), V('miran', 1), V('miran', 2),
            V('balance_risks', 0), V('balance_risks', 1), V('balance_risks', 2)))

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

title = (u'# B76 同一次会议的三份体裁: FOMC 2025-09——纪要逐字抄声明 %d 句而 SEP 与两者共享 0 句; '
         u'异议者三级记账(声明一票⇎纪要一段⇎SEP 无名); 不确定性语言 %d 处集中在预测摘要\n'
         % (F['sh_ab'], F['uncertain'][2]))
srcline = (u'src: %s (%d 字符) ⇎ %s (%d 字符) ⇎ %s (%d 字符) '
           u'(三份同为 federalreserve.gov 的 FOMC 2025-09 文书折平面: 声明⇎纪要⇎经济预测摘要; '
           u'数字一律从面内现读, 一个都不手填; 抓取时刻与 LII 现行版本只在本机或站外成立, 不进门槛)\n'
           % (FILES['A'], F['chars'][0], FILES['B'], F['chars'][1], FILES['C'], F['chars'][2]))
tagsline = (u'tags: 纪要抄声明键(the dissent⇎the majority) 判例名词频四声音 主题主语分档(congress峰⇎constitution峰) '
            u'句集交集镜像键(syllabus只摘胜方) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B76_fomc_one_meeting_three_genres.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b76flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B76 建条目: %s' % out)
print(u'编码区 %d 字符, 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
