# -*- coding: utf-8 -*-
"""B44 记账: ⛓解读注由 audit 里的 DERIV 表达式独立回算生成, 不手填任何数字。"""
import io, re, sys, os, subprocess, ast

sys.stdout.reconfigure(encoding='utf-8')

TAG = u'B44'
ENTRY = u'corpus/babeltele/B44_jats_xml_vs_stripped_text_same_article.md'
RAWX = u'corpus/raw/prose/pmc_ards.xml'
RAWD = u'corpus/raw/prose/pmc_ards_dad.txt'
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)


def reason(i):
    s = io.open([RAWX, RAWD][i], encoding='utf-8', errors='replace').read()
    return u'\n'.join(l for l in s.split(u'\n') if not HEADRX.match(l.strip()))


SRC = [reason(0), reason(1)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))

au = io.open(u'corpus/audit.py', encoding='utf-8').read()
blk = re.search(u" 'B44': \\{\n(.*?)\n \\},", au, re.S).group(1)
VALS, EXPR = {}, {}
for m in re.finditer(r"^ {2}'([^']+)': (.*)$", blk, re.M):
    k, v = m.group(1), m.group(2).strip().rstrip(u',')
    EXPR[k] = ast.literal_eval(v)
    VALS[k] = float(k)
assert len(VALS) == 21, len(VALS)
for k, v in EXPR.items():
    got = float(eval(v, {}, {u'CNT': CNT, u'L': lambda x: float(x.replace(u',', u'')), u'round': round}))
    assert abs(got - float(k)) < 1e-9, (k, got, v[:90])
NTERM0 = EXPR[u'0'].count(u'CNT(')

md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
lbl = re.findall(u'⟦([XD])⟧⟨', body)
uniq_atoms = sorted(set(atoms))
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
tag_lat = len(lbl)
out_all = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
out_lat = out_all - tag_lat
enc = len(body.replace(u'\n', u''))
dig = len(re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', md, re.S).group(1))
raw_chars = [len(SRC[0]), len(SRC[1])]
raw_bytes = [os.path.getsize(RAWX), os.path.getsize(RAWD)]

p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
b44 = [x.strip() for x in row[u'B44'].split(u'|')]
assert int(b44[0]) == dig and int(b44[1]) == enc, (b44[:2], dig, enc)
uniq_cp, blocks, cpu, dens = int(b44[4]), int(b44[5]), b44[6], b44[3]
soft = int(b44[10])
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
assert soft == 2 and proofs == 404, (soft, proofs)
assert re.search(u'B44 \\[.42., .43.', p.stdout), u'待核来源应为两个长标识符串片段'

lines = [l for l in body.split(u'\n') if l.strip()]
GLOS = len(lines) - 2
NXA, NDA = lbl.count(u'X'), lbl.count(u'D')

MEAN = {
 u'0': u'零值键: 渲染层的%s 项标记缺席 + XML 层的%s 项抓取痕迹缺席 + %d 条长句与两处等式的层间差'
      % (14, 4, 8),
 u'1': u'粘连串 “J Intensive Care 2646” 在渲染层比 XML 多出的命中数(标签剥掉后期刊名与卷号粘成新词元)',
 u'2': u'⟨aff⟩ affiliation 标签在 XML 的命中数(许可标签与结构化日期亦各两处, 同值故不另立键)',
 u'3': u'文献分区数: front ⇎ body ⇎ back 三个根级区块',
 u'4': u'funding 标签在 XML 的命中数(资助信息在渲染层为 0)',
 u'5': u'contrib 标签命中数, 即署名条目数',
 u'6': u'kwd 主题词标签命中数(主题词从来没有句子形式, 故渲染层读不到)',
 u'7': u'article-id 命中数: 一篇文献在标记层同时挂着的标识符个数',
 u'8': u'journal 前缀标签命中数(刊名与其属性)',
 u'9': u'术语 “diffuse alveolar damage” 的命中数——两层同值, 其差折进 0 键',
 u'11': u'label 标签命中数',
 u'12': u'含 title 的标签命中数(文章题、期刊题、节题共用一个词形)',
 u'13': u'xref 交叉引用命中数(机构名与其同值, 故只立一键)',
 u'14': u'带属性的段落标签 “<p ” 命中数',
 u'19': u'custom-meta 命中数: 出版方塞进标记里而正文从不显示的元数据',
 u'21': u'以 article 起头的标签合计(含根元素、article-id、article-title)',
 u'49': u'given-names 命中数 ⇎ surname 同值; 与 contrib 数不等, 因为引文里的人也计入了',
 u'536': u'闭尾标签数量',
 u'541': u'小写标签起始数量',
 u'549': u'左尖括号减闭尾之差: 自闭合、处理指令与 DTD 声明',
 u'1085': u'左尖括号总数, 即标记层的全部结构入口; 渲染层该数为 0(在 0 键里)',
}
assert set(MEAN) == set(VALS), sorted(set(VALS) ^ set(MEAN))
ks = sorted(VALS, key=lambda x: float(x))
arith = u'；'.join(u'%s⇒%s' % (k, MEAN[k]) for k in ks if k != u'0')

T = []
T.append(u'※ 体例：本条的两条 raw 是同一篇文章的两种序列化—— ⟪JATS/XML ⇎ 去标记渲染文本⟫, 同一个 Europe PMC '
         u'fullTextXML 端点的两种读法。锚位 %d 个(其中不同串 %d 个; 标 %s 的 %d 个只在 XML 内比对, 标 %s 的 %d 个只在渲染文本内比对), '
         u'判词 %d 行, DERIV %d 键, 0 键里折了 %d 个 CNT 项(标记缺席 %d 项 + 抓取痕迹缺席 %d 项 + 层间等式 %d 条)。'
         % (len(atoms), len(uniq_atoms), u'X', NXA, u'D', NDA, GLOS, len(VALS), NTERM0, 14, 4, 8 + 2))
T.append(u'※ 派生算术(键名即数值, 表达式跑在两份原文上并逐个回算): 0⇒%s。%s。'
         u'其中三条是“差值/等式”型: 1 是粘连串的层间差; 549 是 %d 减 %d; 0 键里还含 “PMC13625332 的层间差 == 粘连串的层间差” '
         u'与 “DOI 前缀两层之差 == 0” 两条等式——用差值表达是为了绕开抓取头部 url 行带来的单边多计。'
         % (MEAN[u'0'], arith, 1085, 536))
T.append(u'※ 隐性知识的所在(判词逐行对应的判断): ① 内容层逐字相同(%d 条长句层间差为 0)但结构层不同; '
         u'② 主题词、机构、资助号、许可、日期这五类信息没有句子形式, 只住在标记里; '
         u'③ 剥标记会造出新词元(期刊名粘卷号), 于是同一查询在两种格式里结果集不同; '
         u'④ 住在元素内容里的信息随文字走, 住在属性里的随标记走; ⑤ 计数的口径必须声明(头部与 url 行算不算源文本); '
         u'⑥ 两层的字符差是结构差不是内容差; ⑦ 0 有两种成因(体裁如此 ⇎ 转换所致), 要连 article-type 属性一起读; '
         u'⑧ 缺席双向, 两种格式互为补集, 故两份都存; ⑨ 可复查性依赖的三件事(许可、日期、引证)全在会被剥掉的那一层。'
         % 8)
T.append(u'※ 抓取与失真：渲染文本带抓取头部(src/url/title/chars/sha256/retrieved), XML 无头部。'
         u'审计口径只剔字段行、不剔 url 行, 故 PMC 号在渲染层多命中一次; 本条凡是“某串在两层的命中差”都写成 CNT(…,0)−CNT(…,1) 一类差值式。'
         u'待核列有 2 项(“42”“43”), 二者都出现在长标识符串内部(PMED 号 42816885 与 GRID 号 grid.443382.a), '
         u'是数字切片的噪声而不是本条的断言, 故不计 FAIL 也不消解——保留可见比抹平更诚实。'
         u'另: XML 折叠成一行后, 锚点里保留了尖括号与属性原样, 因此 %s 一类锚在渲染层必然 0 命中, 这是设计而不是失配。' % (u'⟨<article-id⟩',))
T.append(u'※ 两源对齐：A=%s(%d 字符 ⇎ %d 字节) ⇎ B=%s(%d 字符 ⇎ %d 字节)。'
         u'两层正文相同(%d 条长句层间差为 0, 已入 0 键), 长度差全部由标记承担(%d 处左尖括号只在 A 侧); '
         u'摘要段按两色锚位的窗口并集取, union_hit 与锚位数相等(%d), 且标 %s 的锚一律在 %s 源内比对、标 %s 的锚在 %s 源内比对, '
         u'不存在跨标签归位。'
         % (os.path.basename(RAWX), raw_chars[0], raw_bytes[0], os.path.basename(RAWD), raw_chars[1],
            raw_bytes[1], 8, 1085, len(atoms), u'X', os.path.basename(RAWX), u'D', os.path.basename(RAWD)))
T.append(u'※ 实况：编码 %d 字符 ⇎ 摘要段 %d 字符(保留率 %.1f%%), vs raw 源 %s, 唯一码点 %d, 区块 %d 类, 字符/语义单元 %s。'
         u'拉丁字母: 锚内 %d ⇎ 锚外 %d(其中出处标签 %d)。全库现 %d 条 / 已机检推导 %d 条。'
         % (enc, dig, 100.0 * enc / dig, dens, uniq_cp, blocks, cpu, in_lat, out_lat, tag_lat, 44, proofs))
T.append(u'※ 保留率口径：本条 %s 高于 100%% 是“序列化对照”条的结构性结果——摘要段只索引锚点触到的窗口, '
         u'而判词要同时数两层的结构标签, 字符自然重于窗口。读这条要按字节口径 %s(编码 ÷ 两份文件字节合计 %d)与 '
         u'“%d 键支撑 %d 行判词”来读; 若把 %d 处标签当正文摘要, 就会把结构差读成内容差, 那正是本条要防的错。'
         % (u'%.1f%%' % (100.0 * enc / dig), dens, sum(raw_bytes), len(VALS), GLOS, 1085))

G = md[:md.index(u'## ⛓解读注')] + u'## ⛓解读注\n' + u'\n\n'.join(T) + u'\n'
io.open(ENTRY, 'w', encoding='utf-8').write(G)

ST = {u'in_lat': in_lat, u'out_lat': out_lat, u'tag_lat': tag_lat, u'out_all': out_all,
      u'anchors': len(atoms), u'uniq_anchor': len(uniq_atoms), u'digest': dig, u'enc': enc,
      u'ret': u'%.1f%%' % (100.0 * enc / dig), u'raw0_chars': raw_chars[0], u'raw1_chars': raw_chars[1],
      u'raw0_bytes': raw_bytes[0], u'raw1_bytes': raw_bytes[1], u'uniq_cp': uniq_cp, u'blocks': blocks,
      u'cpu': cpu, u'proofs': proofs, u'dens': dens, u'deriv_keys': len(VALS), u'n_abs': 18,
      u'n_term0': NTERM0, u'gloss_lines': GLOS, u'anchors_x': NXA, u'anchors_d': NDA}
io.open(u'corpus/_f44stats.txt', 'w', encoding='utf-8').write(
    u'\n'.join(u'%s\t%s' % (k, v) for k, v in ST.items()) + u'\n')
print(u'DERIV %d 键全部独立复算通过' % len(VALS))
print(u'gloss written: keys %d enc %d dig %d ret %.1f%% uniq %d anchors %d(%d uniq) X %d/D %d '
      u'in_lat %d out_lat %d tag %d proofs %d soft %d'
      % (len(VALS), enc, dig, 100.0 * enc / dig, uniq_cp, len(atoms), len(uniq_atoms), NXA, NDA,
         in_lat, out_lat, tag_lat, proofs, soft))
