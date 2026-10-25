# -*- coding: utf-8 -*-
# B46 描述与被描述者: bioRxiv recent 接口的目录页 ⇎ 其中一行所指的那篇原文抽取文本
# 两个源本该靠一个 DOI 相连; 而这个 DOI 在两份文件里是两种拼法 —— “连接”本身就是本条的第一条结论。
import io, re, sys, os, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')

RJ = u'corpus/raw/api/bio_recent_2026w01.json'               # 目录页: 自我报告的封套 + 三十行记录
RP = u'corpus/raw/prose/biorxiv_bacterial_organelles.txt'   # 被封套指着的那篇原文(B16 同源)
ENTRY = u'corpus/babeltele/B46_catalog_row_vs_the_paper_it_names.md'
LE, LP = u'E', u'P'
HEADRX = r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)'
BS = u'\\'
EN = u'\u2013'
CN = {1: u'一', 2: u'两', 3: u'三', 4: u'四', 5: u'五', 6: u'六', 7: u'七', 8: u'八', 11: u'十一',
      12: u'十二', 17: u'十七', 19: u'十九', 21: u'二十一'}


def reason(raw):
    s = io.open(raw, encoding='utf-8', errors='replace').read()
    return u'\n'.join([l for l in s.split(u'\n') if not re.match(HEADRX, l.strip(), re.I)])


BJ = io.open(RJ, encoding='utf-8').read()
BP = reason(RP)
TP = io.open(RP, encoding='utf-8', errors='replace').read()
RJ_, RP_ = len(BJ.strip()), len(BP.strip())
FULLJ, FULLP = len(BJ), len(TP)
SHA = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
BSZ = lambda p: os.path.getsize(p)
SHAJ, SHAP = SHA(RJ), SHA(RP)
CNT = lambda pat, i: len(re.findall(pat, [BJ, BP][i], re.I))
CJ = lambda lit: CNT(re.escape(lit), 0)
CP = lambda lit: CNT(re.escape(lit), 1)
COLL = lambda s: re.sub(r'\s+', u' ', s).strip()
PC = COLL(BP)

# ---------- 同一个标识符的三种拼法 ----------
DOI_PLAIN = u'10.1101/2025.09.22.677801'
DOI_ESC = u'10.1101' + BS + u'/2025.09.22.677801'
P_PLAIN, P_ESC = re.escape(DOI_PLAIN), re.escape(DOI_ESC)
N_PLAIN_J, N_PLAIN_P = CNT(P_PLAIN, 0), CNT(P_PLAIN, 1)
N_ESC_J, N_ESC_P = CNT(P_ESC, 0), CNT(P_ESC, 1)
assert (N_PLAIN_J, N_PLAIN_P, N_ESC_J, N_ESC_P) == (0, 41, 1, 0), (
    N_PLAIN_J, N_PLAIN_P, N_ESC_J, N_ESC_P)
ESC_SL = BS + BS + u'/'
N_ESCSL, N_SLASH = CNT(ESC_SL, 0), CNT(u'/', 0)
assert (N_ESCSL, N_SLASH) == (303, 303)
P_U = BS + BS + u'u[0-9a-f]{4}'
P_NA = u'[^' + BS + u'x00-' + BS + u'x7f]'
N_UESC, N_NA_J, N_NA_P = CNT(P_U, 0), CNT(P_NA, 0), CNT(P_NA, 1)
assert (N_UESC, N_NA_J, N_NA_P) == (6, 0, 331)
N_EN_P, N_EN_J, N_HYP_J, N_LT_J, N_LT_P = CNT(EN, 1), CNT(EN, 0), CNT(u' - ', 0), CNT(u'<', 0), CNT(u'<', 1)
assert (N_EN_P, N_EN_J, N_HYP_J, N_LT_J, N_LT_P) == (45, 0, 2, 4, 0)

# ---------- 封套自报 ⇎ 载荷 ----------
D = json.loads(BJ)
ROWS = D['collection']
ENVD = D['messages'][0]
ENV = BJ[BJ.index(u'{"status"'):BJ.index(u'"total":"575"}') + len(u'"total":"575"}')]
S_SRV = re.escape(u'"server":"bioRxiv"')
N_SRV = CNT(S_SRV, 0)
N_CAT = CNT(re.escape(u'"category"'), 0)
N_DATE1 = CNT(re.escape(u'"date":"2026-01-01"'), 0)
N_DATEO = CNT(u'"date":"2026-01-0[2-5]"', 0)
N_DAY = CNT(u'2026-01-0', 0)
N_IVEND = CNT(u'2026-01-05', 0)
S_NA = re.escape(u'"published":"NA"')
N_NA = CNT(S_NA, 0)
S_PDOI = u'"published":"10' + BS + u'.'
N_PDOI = CNT(S_PDOI, 0)
N_PDATE = CNT(u'"published":"20', 0)
N_P1101 = CNT(S_PDOI + u'(?:1101|64898)', 0)
S_FUT = u'"published":"[^",]*2026' + BS + u'.'
N_FUT = CNT(S_FUT, 0)
N_BARE = CNT(u'":' + BS + u'd', 0)
N_QUOTED = CNT(u'":"' + BS + u'd', 0)
N_COUNTSTR = CNT(re.escape(u'"count":"'), 0)
N_NULLW, N_NULLV = CNT(u'null', 0), CNT(u'":null', 0)
N_PAGE = CNT(u'"next"|"page"|"limit"|"offset"', 0)
EARLY = u'content' + BS + BS + u'/early'
N_EARLY = CNT(EARLY, 0)
N_EARLYP = CNT(EARLY + u'[^"]*10' + BS + u'.1101', 0)
N_1101 = CNT(u'10' + BS + u'.1101', 0)
N_64898 = CNT(u'10' + BS + u'.64898', 0)
N_64898_P = CNT(u'10' + BS + u'.64898', 1)
N_V2 = CNT(re.escape(u'"version":"2"'), 0)
N_V1 = CNT(re.escape(u'"version":"1"'), 0)
N_V1P = CNT(u'677801v1', 1)
N_WT2 = CNT(u'v2', 1)
S_LIC30 = re.escape(u'"license":"cc')
N_LIC30 = CNT(S_LIC30, 0)
S_LICND = re.escape(u'"license":"cc_by_nc_nd"')
N_LICND = CNT(S_LICND, 0)
S_CCBY = re.escape(u'CC-BY-NC-ND')
N_CCBY_P, N_CC_J, N_UNDER_J = CNT(S_CCBY, 1), CNT(u'cc_by', 1), CNT(u'cc_by_nc_nd', 0)
assert (N_SRV, N_CAT, N_DATE1, N_DATEO, N_DAY, N_IVEND) == (30, 31, 30, 0, 32, 1)
assert (N_NA, N_PDOI, N_PDATE, N_P1101, N_FUT) == (22, 8, 0, 0, 2)
assert (N_BARE, N_QUOTED, N_COUNTSTR, N_NULLW, N_NULLV, N_PAGE) == (1, 103, 0, 1, 0, 0)
assert (N_EARLY, N_EARLYP, N_1101, N_64898, N_64898_P) == (30, 0, 17, 13, 0)
assert (N_V2, N_V1, N_V1P, N_WT2) == (19, 6, 1, 3)
assert (N_LIC30, N_LICND, N_CCBY_P, N_CC_J, N_UNDER_J) == (30, 11, 40, 0, 11)
assert (N_SRV, N_LIC30, N_EARLY, N_DATE1) == (30, 30, 30, 30)
assert N_NA + N_PDOI == N_SRV
PUBS = [r['published'] for r in ROWS if str(r['published']).startswith(u'10.')]
PUB_PRE = sorted(set(p.split(u'/')[0] for p in PUBS))
ROW = [r for r in ROWS if DOI_PLAIN in r['doi']][0]
assert (len(PUBS), len(PUB_PRE)) == (8, 6)
assert ROW[u'version'] == u'2' and ROW[u'published'] == u'NA' and ROW[u'license'] == u'cc_by_nc_nd'
assert isinstance(ENVD[u'count'], int) and isinstance(ENVD[u'total'], str)
assert (ENVD[u'count'], ENVD[u'total'], ENVD[u'count_new_papers']) == (30, u'575', u'397')
D367, D178, D545 = 397 - N_SRV, 575 - 397, 575 - N_SRV
assert (D367, D178, D545) == (367, 178, 545)
CHP = int(re.search(u'chars: (\\d+)', TP).group(1))
D73 = RP_ - CHP
assert (CHP, D73) == (80626, 73), (CHP, D73)

# ---------- 摘要 ⇎ 原文摘要 ----------
TITLE, ABST = ROW[u'title'], ROW[u'abstract']
N_TIT_P, N_TIT_J = CP(TITLE), CJ(TITLE)
assert (N_TIT_P, N_TIT_J) == (2, 1)
SENT = [s.strip() for s in re.split(r'(?<=[.;:?!])\s', ABST) if len(s.strip()) >= 40]
HIT = [s for s in SENT if COLL(s) in PC]
OUT = [s for s in SENT if COLL(s) not in PC]
assert (len(SENT), len(HIT), len(OUT)) == (7, 5, 2), (len(SENT), len(HIT), len(OUT))
GLUE_P = u'carboxysomes-CO2'          # 抽取文本里的写法: 连字符不留空格
GLUE_J = u'carboxysomes - CO2'         # 目录里的写法: 连字符两侧补出空格
K_PROD_J, K_PROD_P = CJ(u'heterologously produced'), CP(u'heterologously produced')
K_EXPR_J, K_EXPR_P = CJ(u'heterologously expressed'), CP(u'heterologously expressed')
K_GLUEP_J, K_GLUEP_P = CJ(GLUE_P), CP(GLUE_P)
K_GLUEJ_J, K_GLUEJ_P = CJ(GLUE_J), CP(GLUE_J)
assert (K_PROD_J, K_PROD_P, K_EXPR_J, K_EXPR_P) == (1, 0, 0, 1)
assert (K_GLUEP_J, K_GLUEP_P, K_GLUEJ_J, K_GLUEJ_P) == (0, 1, 1, 0)
N_CO2_P = CP(u'CO2')
N_CO2S_P = CP(u'CO' + u'\u2082')
N_CO2_J = CJ(u'CO2')
assert (N_CO2_P, N_CO2S_P, N_CO2_J) == (3, 5, 1)
INST = ROW[u'author_corresponding_institution']
N_INST_J, N_INST_P = CJ(INST), CP(INST)
N_AA_J, N_AA_P = CNT(u'Ann Arbor', 0), CNT(u'Ann Arbor', 1)
N_MICH_J, N_MICH_P = CNT(u'Michigan', 0), CNT(u'Michigan', 1)
CORR = ROW[u'author_corresponding']
N_CORR_J, N_CORR_P = CJ(u'"author_corresponding":"' + CORR + u'"'), CP(CORR)
assert (N_INST_J, N_INST_P, N_AA_J, N_AA_P, N_MICH_J, N_MICH_P) == (1, 0, 1, 5, 1, 7)
assert (N_CORR_J, N_CORR_P) == (1, 2)
N_SURN = len(ROW[u'authors'].split(u';'))
assert CJ(u'heterologously produced') + CP(u'heterologously expressed') == 2

# ---------- 锚点: 全部是两份原文里的逐字片段 ----------
AN, LBL = {}, {}


def JL(lit, key):
    assert BJ.count(lit) == 1, (key, BJ.count(lit))
    assert 12 <= len(lit) <= 460, (key, len(lit))
    AN[key], LBL[key] = lit, LE


def JSPAN(start, end, key):
    a = BJ.index(start)
    b = BJ.index(end, a) + len(end)
    seg = BJ[a:b]
    assert 12 <= len(seg) <= 460, (key, len(seg))
    AN[key], LBL[key] = seg, LE


def PS(lit, key):
    k = BP.index(lit)
    a = BP.rfind(u'\n', 0, k) + 1
    b = BP.find(u'\n', k)
    seg = BP[a:b].strip()
    assert lit in seg and 12 <= len(seg) <= 460, (key, len(seg))
    AN[key], LBL[key] = seg, LP


def JSPAN2(needle, left, right, key):
    k = BJ.index(needle)
    seg = BJ[BJ.rfind(left, 0, k):BJ.index(right, k) + len(right)]
    assert BJ.count(seg) == 1 and 12 <= len(seg) <= 460, (key, len(seg))
    AN[key], LBL[key] = seg, LE


JSPAN(u'{"status"', u'"total":"575"}', u'env')
JL(u'"doi":"' + DOI_ESC + u'"', u'doi_j')
JSPAN2(u'2025.09.22.677801.source.xml', u'"jatsxml"', u'.source.xml"', u'jats')
JSPAN(u'"title":"' + TITLE[:18], u'Vecchiarelli, A. G."', u'head')
JL(u'"author_corresponding_institution":"' + INST + u'"', u'inst')
JL(u'"author_corresponding":"' + CORR + u'"', u'corr')
JL(u'"published":"10.1016' + BS + u'/j.cell.2026.05.017"', u'fut')
JL(u'"doi":"10.64898' + BS + u'/2025.12.28.696719"', u'doi6')
JSPAN(u'"doi":"' + DOI_ESC + u'"', u'"version":"2"', u'date_v')
JSPAN(u'"doi":"' + DOI_ESC + u'"', u'"category":"microbiology"', u'lic_j')
JL(GLUE_J, u'hyp')
JL(u'SCN' + BS + u'u03b1 gene family', u'alpha')
JL(u'Ma' + BS + u'u0308yra' + BS + u'u0308npa' + BS + u'u0308a', u'umlaut')
JSPAN(u'FDR ', u'10-10)', u'cmp')
JL(u'"published":"NA","server":"bioRxiv"}]}', u'na')
PS(DOI_PLAIN, u'doi_p')
PS(u'CC-BY-NC-ND 4.0 International license', u'lic_p')
PS(TITLE, u'tit_p')
PS(u'heterologously expressed', u'expr')
PS(GLUE_P, u'dash')
PS(u'Michigan; Ann Arbor, MI 48108, USA', u'aff')
PS(u'WarpTools v2.0.0', u'wt')
for k, v in AN.items():
    assert v in ([BJ, BP][0 if LBL[k] == LE else 1]), (k, v[:40])
print(u'anchors=%d uniq=%d avg=%.0f' % (len(AN), len(set(AN.values())),
                                        sum(len(v) for v in AN.values()) / float(len(AN))))

# ---------- 判词 ----------
L = []


def A(head, items, gloss):
    L.append(u'%s %s ⇒ %s' % (head, u' ‖ '.join([u'⟦%s⟧⟨%s⟩' % (LBL[k], AN[k]) for k in items]), gloss))


A(u'🧭 体例', [u'env', u'doi_j', u'doi_p'],
  u'两个源: 一个是目录页(自我报告的封套 ⟦%s⟧⟨%s⟩ 加三十行记录), 一个是其中某行所指的那篇原文的抽取文本 ⟦%s⟧⟨%s⟩。'
  u'两者本该靠一个 DOI 相连, 可这个 DOI 在两份文件里是两种拼法——目录里带反斜杠转义 ⟦%s⟧⟨%s⟩, 原文里是真斜杠 ⟦%s⟧⟨%s⟩。'
  u'与上一条(同一个名字的三种对象)分工: 那条比文件与文件, 这条比**描述与被描述者**: 目录能说出原文说不出来的事'
  u'(送达日期、许可码、版本号、有没有期刊版), 而它对自身载荷的报告又处处对不上。'
  % (LE, AN[u'env'], LP, AN[u'doi_p'], LE, AN[u'doi_j'], LP, AN[u'doi_p']))
A(u'🔑 一把钥匙开不了两扇门锁', [u'doi_j', u'doi_p', u'jats'],
  u'原文那把写法在目录里 0 次, 目录那把写法在原文里 0 次(两个 0 都在 0 键); 反过来看: 同一标识符在原文命中 %d 处'
  u'(⟦%s⟧⟨%s⟩ 那样的页脚, 另加 url 行), 在目录里只命中 %d 处(⟦%s⟧⟨%s⟩)。'
  u'目录里还有第三种拼法: ⟦%s⟧⟨%s⟩ 这个 URL 把注册前缀整个丢掉(带前缀的写法在三十条该字段里 0 命中), 原位换上的是送达日期, 而斜杠依旧带转义。'
  u'判词: 连接键在两份文件里没有一次按同一种写法出现; “这两份讲的是同一件事”只能由读者重建, '
  u'机器按字面联结会两手空空。凡要跨源对齐, 先各数一遍对方拼法的命中数, 再决定靠什么联结。'
  % (N_PLAIN_P, LP, AN[u'doi_p'], N_ESC_J, LE, AN[u'doi_j'], LE, AN[u'jats']))
A(u'🗓 窗口 ⇎ 交付', [u'env', u'date_v'],
  u'封套声明的窗口 ⟦%s⟧⟨%s⟩ 含两个端点, 而三十行的 date 字段全是同一天 ⟦%s⟧⟨%s⟩: “2026-01-0” 这种日期前缀全目录 %d 处'
  u'(三十行加两个端点), 端点之后那四天在 date 字段里 0 命中(0 键)。反过来, 原文口径内“%s”这种送达日期 0 次(0 键)。'
  u'四个口径的 30 之间——记录数、date 值、license 值、jatsxml 路径前缀——三条等式全折在 0 键里。'
  u'判词: 声明的区间与交付的区间可以差掉大半, 目录不会承认这件事; 拿到“五天的窗口”只得到第一天, '
  u'错不在抓取失败, 在于把“最新一批”读成“整个窗口”。'
  % (LE, AN[u'env'], LE, AN[u'date_v'], N_DAY, u'2026-01-01'))
A(u'🧾 三个自报数字互不相等', [u'env', u'fut'],
  u'封套给了三个数: count=%d(本页行数)、count_new_papers=%s、total=%s。三个两两之差都是机检键: %d、%d、%d。'
  u'只有第一个能在本文件内核对(它等于记录数), 后两个是“本文件之外还有多少”的断言, 本条把它们交给工具侧而不是机检侧。'
  u'更细的口径线索: 全目录只有 %d 处**裸数字**字段(正是 count), 另有 %d 处“引号里以数字开头”的值, 而 “count” 从不写成字符串(0 键)——'
  u'一个接口在同一个对象里同时用整型与字符串表达“数”。'
  u'判词: 自我报告的字段要按“能否在本文件内核对”分档; 能核对的写成等式, 不能核对的原样留着并标明它不能核对。'
  % (30, u'397', u'575', D367, D178, D545, N_BARE, N_QUOTED))
A(u'🕳 published 这个字段里没有时间', [u'na', u'fut', u'doi_j'],
  u'字段名叫 published, 里面 %d 处是占位串 ⟦%s⟧⟨%s⟩, %d 处是**另一个注册号**(期刊 DOI, ⟦%s⟧⟨%s⟩), '
  u'日期形式 0 处(0 键); 两者相加恰等于记录数(等式在 0 键)。那八个 DOI 分属六家注册机构, 与本页两个前缀'
  u'(⟦%s⟧⟨%s⟩ 与 ⟦%s⟧⟨%s⟩ 两家)无一重合(0 键); 其中 %d 处内含 2026.05 一类字样, 比声明窗口的末尾还晚四个月(“恰好两处”在 0 键里核对)。'
  u'判词: published 不是“何时发表”, 而是“有没有期刊版、它的号是多少”——字段名说意图, 值说另一件事; '
  u'按字段名做年份分布统计会得出一条不存在的时间轴。'
  % (N_NA, LE, AN[u'na'], N_PDOI, LE, AN[u'fut'], LE, AN[u'doi_j'], LE, AN[u'doi6'], N_FUT))
A(u'✍️ 目录里的“摘要”不是引文', [u'head', u'expr', u'dash', u'hyp'],
  u'把 ⟦%s⟧⟨%s⟩ 那段的摘要按句切开发进原文里找: 七句里五句逐字命中(只忽略空白差异), 两句不命中, 而两句的成因不同。'
  u'其一是换一个词: 目录写 “heterologously **produced** carboxysomes”(该串在原文 0 次), 原文写 '
  u'“heterologously **expressed**”(⟦%s⟧⟨%s⟩, 该串在目录 0 次)——两边各命中一处, 两个“恰好一处”折在 0 键里。'
  u'其二是改标点: 原文那一行 ⟦%s⟧⟨%s⟩ 里连字符两侧不留空格, 目录同一处写成 ⟦%s⟧⟨%s⟩ 并把空格补出来; '
  u'两种写法在对方文件里各 0 次(0 键), 而“带空格”这种写法全目录也只有两处(原文 0 次)。'
  u'还要加一层: 原文里排版的短横(–)共 %d 处, 全是数字区间那种样式, 目录里 0 处(0 键); '
  u'而这一句的插入语在抽取文本里已经塌成 ASCII 连字符——同一段话在三个层次里有三种标点。'
  u'判词: 索引里的摘要是一段**改写**而不是引用; 不做逐句对齐, 没人会发现一个形容词被换掉——“引文核对”能发现的正是这种改写。'
  % (LE, AN[u'head'], LP, AN[u'expr'], LP, AN[u'dash'], LE, AN[u'hyp'], N_EN_P))
A(u'🏷 两套词汇, 双向缺席', [u'lic_j', u'lic_p', u'inst', u'aff'],
  u'许可: 目录用码 ⟦%s⟧⟨%s⟩(三十行各带一个 license 值, 其中这个码 %d 行), 原文用散文 ⟦%s⟧⟨%s⟩(每页页脚重复, 共 %d 处); '
  u'两种写法在对方文件里各 0 次(0 键)。机构: 目录把两个字段粘成一串 ⟦%s⟧⟨%s⟩, 原文写 ⟦%s⟧⟨%s⟩——'
  u'粘起来那串在原文 0 次, 而“Ann Arbor”“Michigan”两个零件在原文分别 %d ⇎ %d 处(目录里各 1 处, 两条等式在 0 键)。'
  u'作者也一样: 目录给通讯作者整名 ⟦%s⟧⟨%s⟩(该整名在原文命中两处, “恰好两处”折在 0 键), 而 authors 那一串十二人的“姓, 首字母.”式名'
  u'在原文 0 处命中(0 键)。'
  u'判词: 描述层与被描述层各用一套词汇; 任何按目录字段做的聚合都不能与原文对账, 除非先建词汇映射——而映射不住在这两份文件里。'
  % (LE, AN[u'lic_j'], N_LICND, LP, AN[u'lic_p'], N_CCBY_P, LE, AN[u'inst'], LP, AN[u'aff'],
     N_AA_P, N_MICH_P, LE, AN[u'corr']))
A(u'🔀 版本与字符系统', [u'tit_p', u'wt', u'alpha', u'umlaut'],
  u'版本号: 目录这一行写着 version=2(全目录 %d 行写 2、六行写 1, 后者折在 0 键里核对), 而我们手里那份自称 v1'
  u'(字面串 677801v1 在原文口径内恰好一处, 也在 0 键里); '
  u'更要紧的是原文里 “v2” 这个字串有三处(“恰好三处”折在 0 键), 说的全是别人的软件(⟦%s⟧⟨%s⟩ 那样)——同一个词形在一句里指三种东西。'
  u'标题: 目录的标题在原文里原样命中 %d 处 ⟦%s⟧⟨%s⟩, 目录自己则 1 处(等式在 0 键)。'
  u'字符系统: 目录整份是纯 ASCII(非 ASCII 码点 0 个), 六个非 ASCII 字符全以 \\u 转义存活(⟦%s⟧⟨%s⟩ 那个希腊字母、'
  u'⟦%s⟧⟨%s⟩ 那五个组合变音符), 而原文有 %d 个非 ASCII 码点直接写在地上; 目录里 %d 个斜杠全部写成转义形式, 裸斜杠 0 处(等式在 0 键)。'
  u'连化学式也是两种存活: 原文里带下标的 CO₂ 五处(0 键)⇎ 平写的 CO2 %d 处, 目录那一处正是平写的。'
  u'判词: 同一批字符有两种存活方式, 按字面比对时它们互相看不见; 要做字符级对齐, 得先把转义解开再折叠。'
  % (N_V2, LP, AN[u'wt'], N_TIT_P, LP, AN[u'tit_p'], LE, AN[u'alpha'],
     LE, AN[u'umlaut'], N_NA_P, N_ESCSL, N_CO2_P))
A(u'📏 口径有三种', [u'tit_p'],
  u'同一份原文有三个字符数: 抽取头自记 %d ⇎ 审计口径内(剔掉 # 起始行与 src/title/chars/retrieved/note 那几行) %d ⇎ 整份文件的字符数'
  u'(第三个数住在口径之外, 只能由工具侧报出, 见解读注); '
  u'前两者之差 %d 恰是 url 那一行的长度——而 url 行不在剔除名单里。这个等式在本条里核对(键 %d), '
  u'“恰是 url 行长度”那半句要靠本地脚本量长度, CNT 只会数命中不会量长度, 故属工具侧。'
  u'于是“原文没有标题”与“原文写着标题”同时为真: 抽取头里那一行 title 记的是文件名(它整行都在口径之外, 因而无法作锚), '
  u'正文第一行才是真正的标题 ⟦%s⟧⟨%s⟩。判词: 凡报“共 N 字符”必须同时报口径; 凡遇 0, 先问它是不是住在被剔掉的那几行里。'
  % (CHP, RP_, D73, 73, LP, AN[u'tit_p']))
A(u'🚫 缺席是双向的', [u'cmp', u'doi6'],
  u'目录侧的 0: 裸斜杠、非 ASCII 码点、短横连接号、带横杠的许可散文、真斜杠写法的 DOI、日期形式的 published、'
  u'与本页前缀重合的期刊 DOI、窗口内后四天、next/page/limit/offset 这类分页键、作为 JSON 值的 null(“null”这个词有一处, 在散文里)。'
  u'原文侧的 0: 转义斜杠与转义写法的 DOI、下划线式许可码、带空格的连接号写法、另一个注册前缀 ⟦%s⟧⟨%s⟩ 那种号段、'
  u'published／total／count 这些字段名、粘在一起的机构串、送达日期那串字符、尖括号(目录里 %d 处 ⟦%s⟧⟨%s⟩ 全是数学比较号, 不是标记)。'
  u'缺席项与等式全部折进一个 0 键(逐项列在解读注里)。'
  u'判词: 目录与原文互不包含, 两份都得存; “哪一项在谁那里为 0”就是描述层与被描述层之间的边界。'
  % (LE, AN[u'doi6'], N_LT_J, LE, AN[u'cmp']))
A(u'∴ 骨架', [],
  u'① 连接键要在两边按同一种写法出现才叫能联结, 拼法差异让机器两手空空; ② 窗口声明与交付内容可以差掉大半, 目录不会承认; '
  u'③ 自我报告按“能否在本文件内核对”分档, 不可核对的原样留着并标明; ④ 同一对象里整型与字符串并存, 数字的类型不是语义; '
  u'⑤ 字段名说意图, 值说另一件事(published 里没有时间); ⑥ 索引里的摘要是改写而不是引文, 逐句对齐才看得见一词之差; '
  u'⑦ 标点与重音有两种存活方式(转义 ⇎ 直接写), 字面比对时互相看不见; ⑧ 描述层与被描述层各用一套词汇, 映射不住在这两份文件里; '
  u'⑨ 词形会碰撞(版本号 v2 ⇎ 软件版本 v2), 同名不同所指要在同一份文件里分辨; ⑩ 0 有两种成因(没有 ⇎ 被口径剔掉), '
  u'出处头自记的字符数又是第三种口径; ⑪ 双向缺席 ⇒ 目录与原文互不包含, 两份都得存。')
A(u'ℒmethod', [u'head', u'lic_p', u'expr'],
  u'读“目录条目 ⇎ 它指着的原文”: 第一步把连接键在两边的**字面拼法**各数一遍, 求双侧 0 命中, 再决定靠什么联结'
  u'(本条靠标题与摘要的近似对齐, 而不是 DOI 字面); 第二步把封套的三个自报数与载荷行数并排, 只承认可在本文件内核对的那一个, '
  u'其余两差写成减法式; 第三步把目录字段逐类落到原文里找对应词形(许可码 ⇎ 许可散文、机构串 ⇎ 机构行、作者串 ⇎ 作者段), '
  u'记录双向缺席并建立词汇映射; 第四步把“看上去是引文”的长字段按句切分做逐字对齐, 并把不命中分成标点差异与词差异两类, 各留一个例子; '
  u'第五步凡遇 0, 先查它是否住在被剔掉的出处头里(本条的 title 与 chars 两处正是如此)。'
  u'核验口径: ⟦%s⟧⟨%s⟩ 一类锚取自目录的单行 JSON(整份只有一行, 锚内空白已折叠), ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩ 取自抽取文本的行内片段; '
  u'标 %s 只在目录内比对, 标 %s 只在原文内比对, 不互换。'
  % (LE, AN[u'head'], LP, AN[u'lic_p'], LP, AN[u'expr'], LE, LP))
A(u'✂️ 为什么这份编码比摘要窗口长', [u'env', u'doi_p'],
  u'本条是对照条: 判词要在目录与原文之间来回数(三种拼法、两套词汇、双向缺席), 而摘要段只索引锚点触到的窗口。'
  u'窗口放不下的是“同一件事在两个层次里的两种说法”这类关系本身——⟦%s⟧⟨%s⟩ 里那三个自报数与 ⟦%s⟧⟨%s⟩ 那四十一处页脚'
  u'分住两个源, 没有任何一个窗口同时装着它们。所以保留率高于全库属结构性读数, 按“键数支撑判词行数”与 vs raw 的命中率来读, '
  u'不是按“少说了多少话”。'
  % (LE, AN[u'env'], LP, AN[u'doi_p']))

BODY_MD = u'\n'.join(L)
HEAD_MD = (u'# B46 一行目录与它指着的原文：%d 行 JSON 里那把钥匙，在原文那一侧换了拼法\n\n'
           u'src: %s (bioRxiv recent 接口目录页, 封套自报 count %d ⇎ count_new_papers %s ⇎ total %s, 数据 %d 行, '
           u'口径内 %d 字符 ⇎ 文件 %d 字节, sha256 %s) ⇎ '
           u'%s (该行所指原文的抽取文本, B16 同源, 口径内 %d 字符 ⇎ 全文件 %d 字符 ⇎ 出处头自记 %d, sha256 %s)'
           u'；目录页自身不带出处头, 故它的窗口与总数属工具侧断言\n'
           u'tags: 元数据 ⇎ 原文 连接键拼法 自我报告 字段词汇 改写而非引文 双向缺席 计数口径\n\n'
           % (N_SRV, RJ, 30, u'397', u'575', N_SRV, RJ_, BSZ(RJ), SHAJ,
              RP, RP_, FULLP, CHP, SHAP))
MD = (HEAD_MD + u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + BODY_MD +
      u'\n\n## ⛓解读注\n<!--FILL-->\n')
io.open(ENTRY, u'w', encoding='utf-8').write(MD)
print(u'entry written: %s body_chars=%d anchors=%d gloss_lines=%d' %
      (ENTRY, len(BODY_MD), len(AN), len(L)))

# ---------- DERIV(键名即数值) ----------
NL = chr(10)
D2 = {}


def put(val, expr):
    k = (u'%g' % float(val))
    assert k not in D2, (k, expr[:70], D2.get(k))
    D2[k] = expr
    return k


SRVE = u'CNT(%r,0)' % S_SRV
put(N_ESC_J, u'CNT(%r,0)' % P_ESC)
put(N_CO2_P, u"CNT('CO2',1)")
put(N_TIT_P, u'CNT(%r,1)' % re.escape(TITLE))
put(N_LT_J, u"CNT('<',0)")
put(N_AA_P, u"CNT('Ann Arbor',1)")
put(N_UESC, u'CNT(%r,0)' % P_U)
put(N_MICH_P, u"CNT('Michigan',1)")
put(N_PDOI, u'CNT(%r,0)' % S_PDOI)
put(N_LICND, u'CNT(%r,0)' % S_LICND)
put(N_64898, u'CNT(%r,0)' % (u'10' + BS + u'.64898'))
put(N_1101, u'CNT(%r,0)' % (u'10' + BS + u'.1101'))
put(N_V2, u'CNT(%r,0)' % re.escape(u'"version":"2"'))
put(N_NA, u'CNT(%r,0)' % S_NA)
put(N_SRV, SRVE)
put(N_CAT, u'CNT(%r,0)' % re.escape(u'"category"'))
put(N_DAY, u"CNT('2026-01-0',0)")
put(N_CCBY_P, u'CNT(%r,1)' % S_CCBY)
put(N_PLAIN_P, u'CNT(%r,1)' % P_PLAIN)
put(N_EN_P, u'CNT(%r,1)' % EN)
put(D73, u'RCOT(1)-L(%r)' % (u'%d' % CHP))
put(N_QUOTED, u'CNT(%r,0)' % (u'":"' + BS + u'd'))
put(D178, u'L(%r)-L(%r)' % (u'575', u'397'))
put(N_ESCSL, u'CNT(%r,0)' % ESC_SL)
put(N_NA_P, u'CNT(%r,1)' % P_NA)
put(D367, u'L(%r)-%s' % (u'397', SRVE))
put(D545, u'L(%r)-%s' % (u'575', SRVE))
put(RJ_, u'RCOT(0)')
put(RP_, u'RCOT(1)')

AB = [
    u'CNT(%r,0)' % P_NA,                                   # 目录非 ASCII
    u'CNT(%r,0)' % EN,                                     # 目录无短横连接号
    u'CNT(%r,0)' % S_CCBY,                                 # 目录无带横杠的许可散文
    u"CNT('cc_by',1)",                                     # 原文无下划线式许可码
    u'CNT(%r,1)' % P_ESC,                                   # 原文无转义写法的 DOI
    u'CNT(%r,0)' % P_PLAIN,                                 # 目录无真斜杠写法的 DOI
    u'CNT(%r,0)' % re.escape(GLUE_P),                       # 目录无无空格粘连式写法
    u'CNT(%r,1)' % re.escape(GLUE_J),                       # 原文无带空格的连接号写法
    u'CNT(%r,1)' % re.escape(u'heterologously produced'),   # 原文无 produced
    u'CNT(%r,0)' % re.escape(u'heterologously expressed'),  # 目录无 expressed
    u'CNT(%r,0)' % (EARLY + u'[^"]*10' + BS + u'.1101'),  # URL 丢掉注册前缀
    u'CNT(%r,1)' % (u'10' + BS + u'.64898'),                 # 原文无第二个前缀
    u'CNT(%r,0)' % u'"date":"2026-01-0[2-5]"',              # 窗口后四天
    u'CNT(%r,0)' % u'"published":"20',                      # published 无日期形式
    u'CNT(%r,0)' % (S_PDOI + u'(?:1101|64898)'),            # 期刊 DOI 与前缀不重合
    u'CNT(%r,0)' % re.escape(u'"count":"'),                 # count 从不写成字符串
    u'CNT(%r,0)' % u'":null',                               # 没有 JSON null 值
    u'CNT(%r,0)' % u'"next"|"page"|"limit"|"offset"',       # 没有分页键
    u"CNT('<',1)",                                          # 原文无尖括号
    u'CNT(%r,1)' % re.escape(INST),                          # 原文无粘连机构串
    u'CNT(%r,1)' % re.escape(ROW[u'authors']),               # 原文无那串分号式作者名
    u'CNT(%r,1)' % re.escape(u'2026-01-01'),                 # 原文口径内无送达日期
]
EQ = [
    u'CNT(%r,0)-CNT(%r,0)' % (u'/', ESC_SL),                 # 斜杠全是转义形式
    u'CNT(%r,0)-%s' % (EARLY, SRVE),
    u'CNT(%r,0)-%s' % (S_LIC30, SRVE),
    u'CNT(%r,0)-%s' % (re.escape(u'"date":"2026-01-01"'), SRVE),
    u'%s-(CNT(%r,0)+CNT(%r,0))' % (SRVE, u'10' + BS + u'.1101', u'10' + BS + u'.64898'),
    u'CNT(%r,0)-%s-L(%r)' % (re.escape(u'"category"'), SRVE, u'1'),
    u'%s-CNT(%r,0)-CNT(%r,0)' % (SRVE, S_NA, S_PDOI),        # 占位串 + 期刊 DOI = 记录数
    u"CNT(%r,0)-L('1')" % (u'":' + BS + u'd'),               # 唯一一处裸数字字段
    u"CNT('677801v1',1)-L('1')",                             # 那份自称 v1 恰好一处
    u"CNT('2026-01-05',0)-L('1')",                           # 窗口末端只出现一次
    u"CNT('null',0)-CNT(%r,0)-L('1')" % u'":null',           # null 只在散文里
    u"CNT(%r,0)-L('2')" % S_FUT,                             # 晚于窗口的期刊 DOI 恰好两处
    u"CNT(' - ',0)-L('2')",                                   # 目录里带空格连接号恰好两处
    u'CNT(%r,0)-L(%r)' % (re.escape(TITLE), u'1'),           # 目录里标题串恰好一处
    u'CNT(%r,0)-CNT(%r,1)' % (re.escape(u'heterologously produced'), re.escape(u'heterologously expressed')),
    u'CNT(%r,0)-CNT(%r,0)' % (re.escape(u'Ann Arbor'), re.escape(INST)),
    u"CNT('Michigan',0)-CNT('Ann Arbor',0)",
    u"CNT(%r,1)-L('1')" % re.escape(GLUE_P),                 # 原文那处粘连写法恰好一处
    u"CNT(%r,0)-L('1')" % re.escape(GLUE_J),                 # 目录那处带空格写法恰好一处
    u"CNT(%r,1)-L('2')" % re.escape(CORR),                   # 通讯作者整名在原文两处
    u"CNT(%r,0)-L('1')" % re.escape(u'"author_corresponding":"' + CORR + u'"'),
    u"CNT(%r,0)-L('6')" % re.escape(u'"version":"1"'),       # 写 version 1 的有六行
    u"CNT('CO₂',1)-L('5')",                            # 带下标的化学式五处
    u"CNT('v2',1)-L('3')",                                   # 原文里的 v2 字串三处全是软件版本
]
put(0, u'+'.join(AB + EQ))
NTERM0 = D2[u'0'].count(u'CNT(')
print(u'DERIV keys=%d / 0 键 CNT 项=%d (缺席 %d 项 + 等式 %d 项)' % (
    len(D2), NTERM0, len(AB), len(EQ)))
for t in AB + EQ:
    v0 = eval(t, {}, {u'CNT': CNT, u'L': lambda x: float(x.replace(u',', u'')),
                      u'RCOT': lambda i: [RJ_, RP_][i], u'round': round})
    if abs(v0) > 1e-12:
        print(u'0 键项非零: %-70s -> %s' % (t[:70], v0))
for k, v in D2.items():
    got = eval(v, {}, {u'CNT': CNT, u'L': lambda x: float(x.replace(u',', u'')), u'RCOT': lambda i: [RJ_, RP_][i],
                       u'round': round})
    assert abs(got - float(k)) < 1e-9, (k, got, v[:120])
print(u'DERIV 全部独立回算通过')

BLOCK = u" 'B46': {" + NL + NL.join(u"  %r: %r," % (k, v) for k, v in
                                    sorted(D2.items(), key=lambda x: float(x[0]))) + NL + u" }," + NL
SRC46 = u"SRC['B46'] = ['%s', '%s']" % (RJ, RP) + NL

AU = u'corpus/audit.py'
s = io.open(AU, encoding='utf-8').read()
if u"SRC['B46']" not in s:
    i0 = s.index(NL + u'ATOM = {')
    s = s[:i0 + 1] + SRC46 + s[i0 + 1:]
if u"'B45'}" in s and u"'B46'}" not in s:
    s = s.replace(u"'B45'}", u"'B45', 'B46'}", 1)
s = re.sub(u" 'B46': \\{" + NL + u".*?" + NL + u" \\}," + NL, lambda m: BLOCK, s, count=1, flags=re.S)
if u"'B46': {" not in s:
    k0 = s.index(u'DERIV = {' + NL) + len(u'DERIV = {' + NL)
    s = s[:k0] + BLOCK + s[k0:]
io.open(AU, 'w', encoding='utf-8').write(s)

AC = u'corpus/atomcheck.py'
a = io.open(AC, encoding='utf-8').read()
if u"SRC['B46']" not in a:
    i2 = a.index(u"SRC['B45']")
    a = a[:i2] + SRC46 + a[i2:]
    io.open(AC, 'w', encoding='utf-8').write(a)
io.open(u'corpus/_atoms46.txt', 'w', encoding='utf-8').write(NL.join(sorted(set(AN.values()))) + NL)
ST = [(u'anchors', len(AN)), (u'uniq_anchor', len(set(AN.values()))), (u'deriv_keys', len(D2)),
      (u'n_term0', NTERM0), (u'n_absent', len(AB)), (u'n_equ', len(EQ)), (u'gloss_lines', len(L)),
      (u'n_sent', len(SENT)), (u'n_sent_hit', len(HIT)), (u'n_sent_out', len(OUT)),
      (u'n_pub', len(PUBS)), (u'n_pub_pre', len(PUB_PRE)), (u'n_surn', N_SURN),
      (u'rcot_j', RJ_), (u'rcot_p', RP_), (u'full_j', FULLJ), (u'full_p', FULLP),
      (u'bytes_j', BSZ(RJ)), (u'chars_hdr', CHP), (u'd73', D73), (u'd367', D367),
      (u'd178', D178), (u'd545', D545), (u'n_escsl', N_ESCSL), (u'n_na_p', N_NA_P),
      (u'n_en_p', N_EN_P), (u'n_hyp_j', N_HYP_J), (u'n_quoted', N_QUOTED), (u'n_bare', N_BARE),
      (u'n_plain_p', N_PLAIN_P), (u'n_esc_j', N_ESC_J), (u'n_licnd', N_LICND), (u'n_ccby_p', N_CCBY_P),
      (u'n_lt_j', N_LT_J), (u'n_wt2', N_WT2), (u'n_v2', N_V2), (u'n_v1', N_V1),
      (u'body_chars', len(BODY_MD)), (u'sha_j', SHAJ), (u'sha_p', SHAP)]
io.open(u'corpus/_f46stats.txt', 'w', encoding='utf-8').write(
    NL.join(u'%s\t%s' % (k, v) for k, v in ST) + NL)
print(u'wired B46: audit SRC/ATOM/DERIV(%d keys) + atomcheck SRC + _atoms46.txt(%d uniq)' %
      (len(D2), len(set(AN.values()))))
