# -*- coding: utf-8 -*-
# B47 定义 ⇎ 派生: UnicodeData.txt(逐码位定义表, 无表头) ⇎ Scripts.txt(由它派生的区间分类表)
# 连接键(十六进制码位)这次两边同拼法, 可派生侧仍有十一万余点在定义侧根本没有行——“键对得上”不等于“表接得住”。
import io, re, sys, os, hashlib

sys.stdout.reconfigure(encoding='utf-8')

RU = u'corpus/raw/UnicodeData.txt'
RS = u'corpus/raw/scripts.txt'
ENTRY = u'corpus/babeltele/B47_definition_table_vs_derived_table.md'
LU, LS = u'U', u'S'
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)


def reason(p):
    s = io.open(p, encoding='utf-8', errors='replace').read()
    return u'\n'.join([l for l in s.split(u'\n') if not HEADRX.match(l.strip())])


FU = io.open(RU, encoding='utf-8', errors='replace').read()
FS = io.open(RS, encoding='utf-8', errors='replace').read()
BU, BS_ = reason(RU), reason(RS)
NU_FULL, NS_FULL = len(FU), len(FS)
NU_RC, NS_RC = len(BU.strip()), len(BS_.strip())
BYTES = [os.path.getsize(RU), os.path.getsize(RS)]
SHA = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
CNT = lambda pat, i: len(re.findall(pat, [BU, BS_][i], re.I))
CNTF = lambda pat, i: len(re.findall(pat, [FU, FS][i], re.I))
DROPPED_S = len([l for l in FS.split(u'\n') if HEADRX.match(l.strip())])
DROPPED_U = len([l for l in FU.split(u'\n') if HEADRX.match(l.strip())])

# ---------- 定义表侧 ----------
ROWU = u'(?m)^[0-9A-F]{4,6};'
EXACT14 = u'(?m)^(?:[^;\n]*;){14}[^;\n]*$'
AT15 = u'(?m)^(?:[^;\n]*;){15}'
EMPTY4 = u'(?m);;;;$'
CTRL = u'<control>'
CC = u';Cc;'
CN = u';Cn;'
CO = u';Co;'
MN = u';Mn;'
LO = u';Lo;'
ND = u';Nd;'
MARK = u'<[^>]*, (?:First|Last)>'
FIRSTM = u', First>'
LASTM = u', Last>'
LT_U, GT_U = CNT(u'<', 0), CNT(u'>', 0)
N_ROWU, N_SEMIU, N_E14, N_A15 = CNT(ROWU, 0), CNT(u';', 0), CNT(EXACT14, 0), CNT(AT15, 0)
N_EMPT4, N_CTRL, N_CC, N_CN, N_CO = CNT(EMPTY4, 0), CNT(CTRL, 0), CNT(CC, 0), CNT(CN, 0), CNT(CO, 0)
N_MN, N_LO, N_ND = CNT(MN, 0), CNT(LO, 0), CNT(ND, 0)
N_MARK, N_FIRST, N_LAST = CNT(MARK, 0), CNT(FIRSTM, 0), CNT(LASTM, 0)
N_UNDU, N_UNDS = CNT(u'_', 0), CNT(u'_', 1)
N_DDU, N_DDS = CNT(u'\.\.', 0), CNT(u'\.\.', 1)
N_BRKU, N_BRKS = CNT(u'\[\d+\]', 0), CNT(u'\[\d+\]', 1)
N_UPLU, N_UPLS = CNT(u'U\+', 0), CNT(u'U\+', 1)
N_HYP_U, N_HYPF_U, N_HYP_S = CNT(u'HYPHEN', 0), CNT(u';HYPHEN;', 0), CNT(u'HYPHEN', 1)
N_HAN_U, N_HANS_U = CNT(u'Han', 0), CNT(u'; Han #', 0)
N_LATU, N_LATU_S = CNT(u'LATIN', 0), CNT(u'LATIN', 1)
N_CJK_U, N_CJK_S = CNT(u'CJK UNIFIED IDEOGRAPH', 0), CNT(u'CJK UNIFIED IDEOGRAPH', 1)
KEY4E00 = u'CJK UNIFIED IDEOGRAPH-4E00'
N_4E00_U, N_4E00_S = CNT(KEY4E00, 0), CNT(KEY4E00, 1)
N_LANDU = CNT(u'L&', 0)
N_COPY_U, N_COPY_S = CNT(u'Copyright', 0), CNT(u'Copyright', 1)
N_UNI_U, N_UNI_S = CNT(u'Unicode', 0), CNT(u'Unicode', 1)
N_VER_U, N_VER_S = CNT(u'17\.0\.0', 0), CNT(u'17\.0\.0', 1)
N_DATE_U, N_DATE_S = CNT(u'Date:', 0), CNT(u'Date:', 1)
N_NAU, N_NAS = CNT(u'[^\x00-\x7f]', 0), CNT(u'[^\x00-\x7f]', 1)
assert (N_ROWU, N_SEMIU, N_E14, N_A15, N_EMPT4) == (40575, 568050, 40575, 0, 37586)
assert (N_CTRL, N_CC, N_CN, N_CO) == (65, 65, 0, 6)
assert (N_MN, N_LO, N_ND) == (2059, 21759, 770)
assert (N_MARK, N_FIRST, N_LAST, LT_U, GT_U) == (40, 20, 20, 3938, 3938)
assert (N_UNDU, N_UNDS, N_DDU, N_DDS, N_BRKU, N_BRKS) == (0, 307, 0, 2920, 0, 1460)
assert (N_UPLU, N_UPLS) == (0, 0)
assert (N_HYP_U, N_HYPF_U, N_HYP_S) == (21, 1, 17)
assert (N_HAN_U, N_HANS_U, N_LATU, N_LATU_S) == (1391, 0, 1928, 141)
assert (N_CJK_U, N_CJK_S, N_4E00_U, N_4E00_S) == (52, 22, 1, 1)
assert (N_LANDU, N_COPY_U, N_COPY_S) == (0, 2, 2)
assert (N_UNI_U, N_UNI_S, N_VER_U, N_VER_S, N_DATE_U, N_DATE_S) == (0, 0, 0, 0, 0, 0)
assert (N_NAU, N_NAS, DROPPED_U, DROPPED_S) == (0, 0, 0, 368)
assert (NU_RC, NS_RC, NU_FULL, NS_FULL) == (2198208, 178503, 2198209, 192458)
assert (BYTES[0], BYTES[1]) == (2198209, 192460)
N_UNI_FILE, N_VER_FILE, N_DATE_FILE = CNTF(u'Unicode', 1), CNTF(u'17\.0\.0', 1), CNTF(u'Date:', 1)
assert (N_UNI_FILE, N_VER_FILE, N_DATE_FILE) == (11, 1, 1)
assert NS_FULL - NS_RC == 13955 and BYTES[1] - NS_FULL == 2 and BYTES[0] == NU_FULL
N_UNK_S, N_MISS_S = CNT(u'Unknown', 1), CNT(u'@missing', 1)
N_UNK_FILE, N_MISS_FILE = CNTF(u'Unknown', 1), CNTF(u'@missing', 1)
print(u'unknown scope %d file %d / missing scope %d file %d' % (N_UNK_S, N_UNK_FILE, N_MISS_S, N_MISS_FILE))
assert (N_UNK_S, N_MISS_S, N_MISS_FILE) == (0, 0, 1)

# ---------- 派生表侧 ----------
ROWS_S = u'(?m)^[0-9A-F]{4,6}(?:\.\.[0-9A-F]{4,6})?[ \t]*;'
RANGE = u'(?m)^[0-9A-F]{4,6}\.\.[0-9A-F]{4,6}[ \t]*;'
SINGLE = u'(?m)^[0-9A-F]{4,6}[ \t]+;'
S_SEMI = CNT(u';', 1)
N_LT_S, N_GT_S = CNT(u'<', 1), CNT(u'>', 1)
N_ROWS, N_RNG, N_SGL = CNT(ROWS_S, 1), CNT(RANGE, 1), CNT(SINGLE, 1)
N_COMMON, N_INHER, N_LATIN_R = CNT(u'; Common #', 1), CNT(u'; Inherited #', 1), CNT(u'; Latin #', 1)
H = lambda gc: u'# %s ' % gc
N_LENS, N_MNS, N_LOS, N_NDS, N_CCS = CNT(H(u'L&'), 1), CNT(H(u'Mn'), 1), CNT(H(u'Lo'), 1), \
    CNT(H(u'Nd'), 1), CNT(H(u'Cc'), 1)
N_COS = CNT(H(u'Co'), 1)
assert (N_ROWS, N_RNG, N_SGL, S_SEMI) == (2287, 1460, 827, 2287)
assert (N_LT_S, N_GT_S) == (4, 4)
assert (N_COMMON, N_INHER, N_LATIN_R) == (613, 36, 61)
assert (N_LENS, N_MNS, N_LOS, N_NDS, N_CCS, N_COS) == (157, 373, 557, 72, 2, 0)
assert N_RNG + N_SGL == N_ROWS and N_BRKS == N_RNG and N_DDS == 2 * N_RNG

# ---------- 区间展开与两表对账(条目侧算一遍, 审计器侧由 B47_* 助手独立复算) ----------
def rows_of(txt):
    out = []
    for l in txt.split(u'\n'):
        m = re.match(u'^([0-9A-F]{4,6})(?:\.\.([0-9A-F]{4,6}))?[ \t]*;', l)
        if m:
            lo = int(m.group(1), 16)
            hi = int(m.group(2) or m.group(1), 16)
            n = re.search(u'\[(\d+)\]', l)
            g = l.split(u'#')[0].split(u';')
            out.append((lo, hi, n.group(1) if n else None, g[1].strip() if len(g) > 1 else u'', l))
    return out


RS_ROWS = rows_of(BS_)
assert len(RS_ROWS) == N_ROWS
PTS = set()
for r in RS_ROWS:
    PTS.update(range(r[0], r[1] + 1))
ASSIGN = len(PTS)
SCRIPTS = len(set(r[3] for r in RS_ROWS))
UCODES = set(int(l.split(u';')[0], 16) for l in BU.split(u'\n') if re.match(u'^[0-9A-F]{4,6};', l))
assert len(UCODES) == N_ROWU
NOROW = len(PTS - UCODES)
IN_UCD = len(PTS & UCODES)
NOUCD = len(UCODES - PTS)
SELF = sum(int(r[2]) for r in RS_ROWS if r[2] is not None) + len([1 for r in RS_ROWS if r[2] is None])
SPANS = sum(r[1] - r[0] + 1 for r in RS_ROWS)
pend, blocks = {}, []
for l in BU.split(u'\n'):
    m = re.match(u'^([0-9A-F]{4,6});<([^>]*), (First|Last)>;', l)
    if m:
        c, side = int(m.group(1), 16), m.group(3)
        if side == u'First':
            pend[m.group(2)] = c
        else:
            blocks.append((m.group(2), pend.pop(m.group(2)), c))
MARKCOV = sum(b[2] - b[1] + 1 for b in blocks)
assert (ASSIGN, SCRIPTS, NOROW, IN_UCD, NOUCD) == (159866, 174, 119303, 40563, 12)
assert (SELF, SPANS, MARKCOV, len(blocks)) == (159866, 159866, 258847, 20)
assert IN_UCD + NOUCD == N_ROWU and ASSIGN - NOROW == IN_UCD
ONLY_UCD = u' '.join(u'%X' % x for x in sorted(UCODES - PTS))
assert len(ONLY_UCD.split()) == 12
MKEND = set()
for _nm, _a, _b in blocks:
    MKEND.update((_a, _b))
ORPH = UCODES - PTS
assert ORPH <= MKEND
ORPH_PAIRS = sorted(set(_nm for _nm, _a, _b in blocks if _a in ORPH or _b in ORPH))
COVER_PAIRS = len([1 for _nm, _a, _b in blocks if _a in PTS and _b in PTS])
UNCOVERED = 0x110000 - ASSIGN
assert (len(ORPH_PAIRS), COVER_PAIRS, UNCOVERED) == (6, 14, 954246)
print(u'orphan pairs %s / covered_pairs %d / uncovered %d' % (ORPH_PAIRS, COVER_PAIRS, UNCOVERED))
ENDP = u'GREEK CAPITAL LETTER SHO'
E_U, E_S = CNT(re.escape(ENDP + u';'), 0), CNT(re.escape(ENDP + u'..'), 1)
E_JU = CNT(re.escape(ENDP + u'..'), 0)
print(u'endpoint probe E_U=%s E_S=%s E_JU=%s' % (E_U, E_S, E_JU))
assert (E_U, E_S, E_JU) == (1, 1, 0)
SQL = [l for l in BU.split(u'\n') if KEY4E00 in l]
assert len(SQL) == 1
SQUARED_ROW = SQL[0]
assert u'SQUARED' in SQUARED_ROW and u'4E00' in SQUARED_ROW
N_SQ_U, N_SQ_S = CNT(u'SQUARED', 0), CNT(u'SQUARED', 1)
assert (N_SQ_U, N_SQ_S) == (372, 4)
CCROW = [r[4] for r in RS_ROWS if H(u'Cc') in r[4]]
assert len(CCROW) == 2
print(u'cc rows %r' % (CCROW,))
CTRLROW = [x for x in CCROW if x.startswith(u'0000..001F')][0]
CTRLGEN = re.search(u'<[^>]*>\.\.<[^>]*>', CTRLROW).group(0)
assert CNT(re.escape(CTRLGEN), 0) == 0 and CNT(re.escape(CTRLGEN), 1) == 1

# ---------- 锚点 ----------
AN, LBL = {}, {}


def UL(prefix, key):
    hits = [l for l in FU.split(u'\n') if l.startswith(prefix)]
    assert len(hits) == 1, (key, prefix, len(hits))
    lit = hits[0].rstrip()
    assert FU.count(lit) == 1 and 12 <= len(lit) <= 460, (key, len(lit))
    AN[key], LBL[key] = lit, LU


def SA(prefix, key):
    hits = [l for l in FS.split(u'\n') if l.startswith(prefix)]
    assert len(hits) == 1, (key, prefix, len(hits))
    lit = hits[0].rstrip()
    assert FS.count(lit) == 1 and 12 <= len(lit) <= 460, (key, len(lit))
    AN[key], LBL[key] = lit, LS


UL(u'4E00;', u'han_first')
UL(u'9FFF;', u'han_last')
UL(u'20000;', u'extb_first')
UL(u'0041;', u'lat_a')
UL(u'0000;', u'ctrl0')
UL(u'2011;', u'nobreak')
UL(u'00AD;', u'softhy')
UL(u'E000;', u'pua_first')
AN[u'squared'] = SQUARED_ROW
assert FU.count(SQUARED_ROW) == 1 and 12 <= len(SQUARED_ROW) <= 460
LBL[u'squared'] = LU
UL(u'03F7;', u'sho_row')
SA(u'4E00..9FFF', u'han_range')
SA(u'20000..2A6DF', u'extb_range')
SA(u'0000..001F', u'ctrl_range')
SA(u'0020', u'space_row')
SA(u'0041..005A', u'lat_range')
SA(u'1A56', u'taim')
SA(u'11DE0..11DE9', u'tolong')
SA(u'03F7..03FF', u'greek_range')
for k, v in AN.items():
    assert v in ([FU, FS][0 if LBL[k] == LU else 1]), (k, v[:40])
ANCH, UANCH = len(AN), len(set(AN.values()))
NU_AN = len([k for k, x in LBL.items() if x == LU])
NS_AN = ANCH - NU_AN
print(u'anchors=%d uniq=%d U=%d S=%d avg=%.0f squared=%r' %
      (ANCH, UANCH, NU_AN, NS_AN, sum(len(v) for v in AN.values()) / float(ANCH), AN[u'squared']))

# ---------- 判词 ----------
L = []


def A(head, items, gloss):
    L.append(u'%s %s ⇒ %s' % (head, u' ‖ '.join([u'⟦%s⟧⟨%s⟩' % (LBL[k], AN[k]) for k in items]), gloss))


A(u'🧭 体例', [u'han_first', u'han_range'],
  u'两个源: 一个是逐码位的定义表 ⟦%s⟧⟨%s⟩(每行一个码位、十五个字段、无表头无注释), 一个是**由它派生**的分类表 '
  u'⟦%s⟧⟨%s⟩(每行一个区间或单点, 把码位归给某个脚本, 全表 %d 个脚本值)。与上一条(目录行 ⇎ 它指着的原文)正好相反: '
  u'这里的连接键是十六进制码位, 两边同一种拼法(“U 加号”式前缀两边都 0 次, 0 键), 机器一行就能对上; '
  u'可对上键不等于接得住表——派生表归了类的 %d 个码位里, 有 %d 个在定义表里没有自己的行(定义表只写区间的两端)。'
  % (LU, AN[u'han_first'], LS, AN[u'han_range'], SCRIPTS, ASSIGN, NOROW))
A(u'🔇 定义表用缺席来定义', [u'han_first', u'han_last', u'pua_first', u'ctrl0'],
  u'定义表 %d 行, 未分配的码位**根本不开行**(类字段为 Cn 的行 0 次, 0 键), 于是“一段连续码位”靠两行端点标记顶替: '
  u'形如 ⟦%s⟧⟨%s⟩ 与 ⟦%s⟧⟨%s⟩ 的标记行共 %d 行, 配成 %d 对(First 与 Last 各 %d 行, 等式在 0 键), '
  u'替 %d 个位置说话(这个总数要展开区间才知道, 审计器用 B47_MARKCOV 独立复算)。名字也能整列塌成一个标记: '
  u'控制字符写成 ⟦%s⟧⟨%s⟩ 那样, 尖括号包住的 control 标记共 %d 处, 与类字段 Cc 的行数 %d 完全相等(等式在 0 键); '
  u'私有区也只有端点行 ⟦%s⟧⟨%s⟩, 类字段 Co 共 %d 行。'
  u'每行的字段数固定得可怕: 分号共 %d 处, 恰为行数 %d 的十四倍, 而含十五个分号的行 0 处; 另有 %d 行以四个空字段收尾。'
  u'判词: 定义表的压缩装置是“端点 + 标记 + 空字段”, 它说的话比它写的行多出一个数量级。'
  % (N_ROWU, LU, AN[u'han_first'], LU, AN[u'han_last'], N_MARK, N_FIRST, N_FIRST, MARKCOV,
     LU, AN[u'ctrl0'], N_CTRL, N_CC, LU, AN[u'pua_first'], N_CO, N_SEMIU, N_ROWU, N_EMPT4))
A(u'✂️ 派生表的三件压缩装置', [u'han_range', u'lat_range', u'space_row'],
  u'派生表 %d 行里, %d 行是区间(两点之间写连写符号)、%d 行是单点(既没有连写符号, 也没有自报方括号) ⟦%s⟧⟨%s⟩; '
  u'每行只有一个分号 ⇎ 定义表每行十四(两个数都是 CNT 键, 比值不写数字)。'
  u'最省心的一例: 定义表为二十六个大写字母逐位开行 ⟦%s⟧⟨%s⟩, 派生表用一行区间把它收走 ⟦%s⟧⟨%s⟩。'
  u'区间行自带一句自检: 方括号里的点数共 %d 处, 恰好等于区间行数 %d(单点行一处也没有, 0 键)——“有跨度才需要自报”。'
  u'最妙的是连写符号在同一行里出现两次: 一次连码位, 一次连名字 ⟦%s⟧⟨%s⟩, 故全表它共 %d 处 = 区间行数的两倍(0 键)。'
  u'把区间行的自报数相加、单点行各算一点得 %d, 与端点算术之和相同(两边都由审计器展开区间复算, 差 0 在 0 键)。'
  u'判词: 派生表用“区间 + 自报数 + 造名省略号”三件装置压缩, 每件装置都能被数出来; 而“装置合起来覆盖多少点”只能展开才知道。'
  % (N_ROWS, N_RNG, N_SGL, LS, AN[u'space_row'], LU, AN[u'lat_a'], LS, AN[u'lat_range'],
     N_BRKS, N_RNG, LS, AN[u'han_range'], N_DDS, ASSIGN))
A(u'🔗 同一个汉字区, 两边差一万倍', [u'han_range', u'han_first', u'han_last', u'squared'],
  u'派生表那一行 ⟦%s⟧⟨%s⟩ 自报 %s 个点; 定义表为这一整段只写了两行 ⟦%s⟧⟨%s⟩ 与 ⟦%s⟧⟨%s⟩, 中间一个也没有。'
  u'更要紧的是名字: 派生表给两端**造**出 “%s..” 这种名串, 而这个字面在定义表里并非 0——它恰好命中一次(0 键核对), '
  u'命中处却是另一个字符的名字 ⟦%s⟧⟨%s⟩ 的后半(它的兼容分解字段又指回同一个码位)。两边各命中一次, 差为 0 而成因完全不同: '
  u'一处是造名的省略号, 一处是“带方框的汉字”那种兼容字符。'
  u'判词: “在另一份文件里 0 次”不是唯一的安全结论; 命中一次同样可能是错觉, 得看它住在哪一列里。'
  % (LS, AN[u'han_range'], u'[20992]', LU, AN[u'han_first'], LU, AN[u'han_last'],
     KEY4E00, LU, AN[u'squared']))
A(u'🪞 省略号造出的串, 定义表按格式写不出', [u'greek_range', u'sho_row'],
  u'能核对的那一半造名: 派生表 ⟦%s⟧⟨%s⟩ 把两端的点名连起来写, 端点名“%s”在定义表里确实独占一行 ⟦%s⟧⟨%s⟩'
  u'(两边各恰好一处, 两条等式都折在 0 键), 但连写带省略号的那种串在定义表里 0 次(0 键)——'
  u'定义表里没有“区间”这个书写装置, 于是它写不出自己派生表的行名。'
  u'逐对核对“区间两端的点名是否真等于该码位的定义名”要按整行解析两份表, CNT 量不到, 属工具侧(两份表的逐行核对结果在解读注里报明)。'
  u'判词: 派生表不只搬运定义表的内容, 它还**生成**定义表按格式写不出的字符串; 这类串在反向核对里必须预先排除, 否则会被误判成“原文没有”。'
  % (LS, AN[u'greek_range'], ENDP, LU, AN[u'sho_row']))
A(u'🏷 词汇不跨界, 而子串会造假冒阳性', [u'taim', u'tolong', u'softhy', u'nobreak'],
  u'脚本值是标识符, 定义表里没有对应字段: “分号 Han 井号”这种写法在定义表 0 次, 可把大小写折叠后拿 Han 当**子串**去搜, '
  u'定义表里有 %d 处命中——全在字符名里(HANGUL、YI 那些名字都含这三个字母)。'
  u'同一件事在字段式匹配里就干净了: HYPHEN 作子串 %d 处 ⟦%s⟧⟨%s⟩ ⇎ 作字段名恰好一处 ⟦%s⟧⟨%s⟩(0 键); '
  u'派生表里它 %d 处, 全在名字列里。'
  u'下划线更是硬界限: 定义表 0 处 ⇎ 派生表 %d 处, 因为脚本值写成 ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩ 这样。'
  u'判词: 跨表检索要用字段式模式而不是子串; 子串会造出一台假阳性机器, 它报的每一个数都是真的, 也全都是错的。'
  % (N_HAN_U, N_HYP_U, LU, AN[u'softhy'], LU, AN[u'nobreak'], N_HYP_S, N_UNDS,
     LS, AN[u'taim'], LS, AN[u'tolong']))
A(u'🧮 同一套类名在两表里的两种身份', [u'ctrl_range', u'greek_range'],
  u'派生表把定义表的类抄进行尾注释: Mn 式 %d 处、Lo 式 %d 处、Nd 式 %d 处 ⟦%s⟧⟨%s⟩, '
  u'而定义表那边这些类住在字段里: %d、%d、%d 行——“注释行 ⇎ 定义行”之差, 六个数各自都是 CNT 键。'
  u'最硬的一条是合成类: L& 式注释在派生表 %d 处 ⟦%s⟧⟨%s⟩, 在定义表里既作字段 0 次、作注释也 0 次(0 键)——'
  u'L& 是字母、标记、数字三类的并, 定义表按码位逐个赋类时写不出这种值。'
  u'反向也成立: 控制类在定义表逐位列了 %d 行, 在派生表塌成 %d 行 ⟦%s⟧⟨%s⟩(那一行的名字也是造出来的, '
  u'连控制字符名都带上尖括号与连写符号, 而那整串在定义表 0 次); 私有区在定义表有 %d 行, 在派生表连 Co 式注释都 0 处(0 键)——它被有意不归类。'
  u'判词: 字段身份与注释身份不能互推; 派生表能写出定义表写不出的类, 定义表能列出派生表拒绝归类的位置。'
  % (N_MNS, N_LOS, N_NDS, LS, AN[u'greek_range'], N_MN, N_LO, N_ND,
     N_LENS, LS, AN[u'greek_range'], N_CC, N_CCS, LS, AN[u'ctrl_range'], N_CO))
A(u'🗓 出处住在被剔掉的行里', [u'space_row'],
  u'派生表在审计口径内 %d 字符, 而整份文件比这长约一万四千字符: 相差的是三百六十八行注释, '
  u'它的文件名、日期行、版权行、还有一句“其余没被任何区间点到的码位一律算 Unknown”的兜底行, 全在这些注释里'
  u'(口径内 Scripts-17、17.0.0、Date、Unicode、Unknown、@missing 这些串一律 0 次, 0 键; '
  u'文件里确实写着——版本与日期各一处, Unicode 十一处: 这几个数只有工具能报, 见解读注)。'
  u'那句兜底行一句话顶住了派生表没有为它们开行的全部剩余位置, 数量约九十五万四千个, 而两份表里都没有写这个数(要补集算术才得, 见解读注)。'
  u'定义表那边是另一种 0: 它整个文件就没有表头, 所以同样的串在口径内 0、在全文件也 0。'
  u'两个 0 数字相同, 成因不同, 必须分别写明。'
  u'字符系统同样要报口径: 两份表口径内的非 ASCII 码点都是 0(0 键), 可派生侧文件的字节数比字符数多二——'
  u'那两个字节正是被剔掉的版权行里的符号; 定义侧字节与字符相等。'
  u'判词: “这份文件是纯 ASCII”只有带着口径才成立; 而“文件里没有版本信息”与“版本信息被口径剔掉了”在机检里长得一模一样。'
  % NS_RC)
A(u'🚫 双向缺席, 而且不对称', [u'extb_first', u'extb_range', u'ctrl_range'],
  u'定义侧有而派生侧无: %d 个码位有定义行却不被任何脚本认领(它们正是代理区与私有区那些标记块的两端, 逐个码位列在解读注); '
  u'造名省略号 0 处、下划线 0 处、区间连写符号 0 处。'
  u'派生侧有而定义侧无: 归了类的 %d 个点里有 %d 个没有定义行(它们住在 %d 对端点之间, ⟦%s⟧⟨%s⟩ 那样); '
  u'“分号 Han 井号”式脚本值 0 处、L& 式合成类 0 处、方括号自报 0 处。'
  u'共同的缺失也算一条: 两份表都不写 U 加号前缀(两边各 0)。'
  u'尖括号数量差三个量级: 定义侧 %d 处(三种用途: 控制名标记、区间端点标记、兼容分解标记)⇎ 派生侧 %d 处'
  u'(全在 ⟦%s⟧⟨%s⟩ 那种造出来的名字里)。'
  u'判词: 两份表互不包含, 连“包含”的方向也不对称——定义表行少话多, 派生表行少点密, 谁都不是谁的子集。'
  % (NOUCD, ASSIGN, NOROW, N_FIRST, LS, AN[u'extb_range'], LT_U, N_LT_S, LS, AN[u'ctrl_range']))
A(u'∴ 骨架', [],
  u'① 键拼法相同只算一半成功, 另一半是“对方有没有为这个键开一行”(定义表按缺席定义, 十万级码位在它那里不存在); '
  u'② 压缩装置各有可数的记号: 端点标记对 ⇎ 区间连写符号 + 自报方括号 + 造名省略号; '
  u'③ 字段数即格式: 每行十四 ⇎ 每行一, 分号密度先于内容定出表的种类; '
  u'④ 命中一次也可能是错觉(造名字串住在另一个字符的名字里), 要看命中在哪一列; '
  u'⑤ 子串检索会造一台真数字的假阳性机器(%d 处 Han), 跨表匹配须用字段式模式; '
  u'⑥ 派生表会**生成**定义表按格式写不出的串与类(L&), 反向核对要预先排除; '
  u'⑦ 0 有两种成因(真的没有 ⇎ 被审计口径剔掉的注释行), 而“纯 ASCII”必须报口径; '
  u'⑧ 双向缺席且不对称: 标记端点无人认领 ⇎ 标记内部没有定义行, 私有区一边有行、一边拒绝归类; '
  u'⑨ 自报数与展开算术相等(%d)这件事 CNT 数不出来, 交给审计器里的区间展开函数; 能数的记号与必须展开的结论分列。'
  % (N_HAN_U, ASSIGN))
A(u'ℒmethod', [u'han_first', u'squared', u'space_row', u'taim'],
  u'读“定义表 ⇎ 由它派生的分类表”: 第一步先数**每行的分隔符密度**(十四 ⇎ 一)定出表的种类, 再决定按行读还是按区间读; '
  u'第二步找定义表里的“标记行装置”(形如尖括号加 First/Last 的端点对、整列塌成 control 的名字、以空字段收尾的行), '
  u'它们告诉你哪些码位是被范围而不是被行定义的; 第三步把派生表的区间行展开成点集, 与定义表的码位集合做双向差集, '
  u'并把三种数分开报: 能数的记号 ⇎ 要展开才知道的 ⇎ 只有工具知道的; '
  u'第四步凡跨表搜词一律用字段式模式而非子串, 并对每个“恰好命中一次”问它住在哪一列; '
  u'第五步把出处信息(版本、日期、版权)按“口径内 ⇎ 文件内”分别报数, 两个 0 分开写。'
  u'核验口径: ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩ 取自定义表的整行, ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩ 取自派生表的整行; '
  u'标 %s 只在定义表内数, 标 %s 只在派生表内数, 不互换。'
  % (LU, AN[u'han_first'], LU, AN[u'squared'], LS, AN[u'space_row'], LS, AN[u'taim'], LU, LS))
A(u'✂️ 为什么这份编码比摘要窗口长', [u'han_first', u'han_range'],
  u'本条的两个源都是纯文本表, 口径内合计约二百三十七万六千余字符(确数、字节数与它们在全库里的体量排位见解读注), 而判词要说的是**表的形状**: '
  u'端点标记 ⇎ 区间行、字段密度、造名省略号、双向差集。摘要段只能取锚点触到的行 ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩, '
  u'而“十万级码位在定义侧没有行”这类结论住在展开算术里, 不住在任何窗口里。'
  u'所以摘要段那千五百余字符与原料之比不到千分之一——这是“用二百万字符的原料换十二行判断”的结构性读数, 不是漏说了多少话。'
  % (LU, AN[u'han_first'], LS, AN[u'han_range']))

BODY_MD = u'\n'.join(L)
GLOS = len(L)
HEAD_MD = (u'# B47 定义表 ⇎ 由它派生的分类表：连接键两边同一种拼法，可十万级码位在定义表里根本没有行\n\n'
           u'src: %s (UnicodeData.txt 逐码位定义表, %d 数据行 × 15 字段, 口径内 %s 字符 ⇎ 全文件 %s 字符 ⇎ 磁盘 %s 字节, '
           u'纯 ASCII(字节数=字符数), 无表头无注释(被口径剔掉的行 0), sha256 %s) ⇎ '
           u'%s (Scripts-17.0.0.txt 派生分类表, 数据 %d 行(区间 %d ⇎ 单点 %d), 口径内 %s 字符 ⇎ 全文件 %s 字符 ⇎ 磁盘 %s 字节'
           u'(字节比字符多 2, 那两个字节住在被口径剔掉的 %d 行注释里: 文件名/日期/版权都在注释中, 故口径内“Unicode”0 次而文件内 11 次), '
           u'sha256 %s)\n'
           u'；两份表都没有出处头之外的自记数; 区间展开的五个数(assigned %d ⇎ 无行 %d ⇎ 无人认领 %d ⇎ 标记覆盖 %d ⇎ 脚本值 %d)'
           u'由 audit.py 里的 B47_* 函数独立复算, 端点名逐对核对与“14 ⇎ 1 的比值”属工具侧断言, 见 ⛓解读注\n'
           u'tags: 定义 ⇎ 派生 压缩装置 字段密度 造名省略号 子串假阳性 双向差集 计数口径\n\n'
           % (RU, N_ROWU, format(NU_RC), format(NU_FULL), format(BYTES[0]), SHA(RU),
              RS, N_ROWS, N_RNG, N_SGL, format(NS_RC), format(NS_FULL), format(BYTES[1]), DROPPED_S, SHA(RS),
              ASSIGN, NOROW, NOUCD, MARKCOV, SCRIPTS))
MD = (HEAD_MD + u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + BODY_MD +
      u'\n\n## ⛓解读注\n<!--FILL-->\n')
io.open(ENTRY, u'w', encoding='utf-8').write(MD)
print(u'entry written: %s body_chars=%d anchors=%d gloss_lines=%d' % (ENTRY, len(BODY_MD), ANCH, GLOS))

# ---------- DERIV(键名即数值; 等式/缺席/“恰好一处”折进 0 键) ----------
NL = chr(10)
D2 = {}


def put(val, expr):
    f = float(val)
    k = u'%d' % f if f == int(f) else u'%g' % f
    assert k not in D2, (k, expr[:70], D2.get(k))
    D2[k] = expr
    return k


def CE(pat, i):
    return u"CNT(%r,%d)" % (pat, i)


put(N_ROWU, CE(ROWU, 0))
put(N_SEMIU, CE(u';', 0))
put(N_EMPT4, CE(EMPTY4, 0))
put(N_MARK, CE(MARK, 0))
put(N_FIRST, CE(FIRSTM, 0))
put(N_CTRL, CE(CTRL, 0))
put(N_CO, CE(CO, 0))
put(N_MN, CE(MN, 0))
put(N_LO, CE(LO, 0))
put(N_ND, CE(ND, 0))
put(LT_U, CE(u'<', 0))
put(N_HYP_U, CE(u'HYPHEN', 0))
put(N_HAN_U, CE(u'Han', 0))
put(N_LATU, CE(u'LATIN', 0))
put(NU_RC, u'RCOT(0)')
put(N_ROWS, CE(ROWS_S, 1))
put(N_RNG, CE(RANGE, 1))
put(N_SGL, CE(SINGLE, 1))
put(N_DDS, CE(u'\.\.', 1))
put(N_UNDS, CE(u'_', 1))
put(N_COMMON, CE(re.escape(u'; Common #'), 1))
put(N_INHER, CE(re.escape(u'; Inherited #'), 1))
put(N_LATIN_R, CE(re.escape(u'; Latin #'), 1))
put(N_LENS, CE(re.escape(H(u'L&')), 1))
put(N_MNS, CE(re.escape(H(u'Mn')), 1))
put(N_LOS, CE(re.escape(H(u'Lo')), 1))
put(N_NDS, CE(re.escape(H(u'Nd')), 1))
put(N_CCS, CE(re.escape(H(u'Cc')), 1))
put(N_LT_S, CE(u'<', 1))
put(N_HYP_S, CE(u'HYPHEN', 1))
put(NS_RC, u'RCOT(1)')
put(ASSIGN, u'B47_ASSIGN()')
put(NOROW, u'B47_NOROW()')
put(NOUCD, u'B47_NOUCD()')
put(MARKCOV, u'B47_MARKCOV()')
put(SCRIPTS, u'B47_SCRIPTS()')

AB = [
    CE(CN, 0), CE(AT15, 0), CE(u'_', 0), CE(u'\.\.', 0), CE(u'\[\d+\]', 0),
    CE(u'U\+', 0), CE(u'U\+', 1), CE(u'Unicode', 0), CE(u'Unicode', 1),
    CE(u'17\.0\.0', 0), CE(u'17\.0\.0', 1), CE(u'Date:', 0), CE(u'Date:', 1),
    CE(u'Scripts-17', 1), CE(u'Unknown', 1), CE(u'@missing', 1),
    CE(u'[^\x00-\x7f]', 0), CE(u'[^\x00-\x7f]', 1),
    CE(re.escape(u'; Han #'), 0), CE(u'L&', 0), CE(re.escape(u';L&;'), 0),
    CE(re.escape(H(u'L&')), 0), CE(re.escape(u'; Latin #'), 0), CE(re.escape(u'; Common #'), 0),
    CE(re.escape(H(u'Co')), 1), CE(re.escape(ENDP + u'..'), 0), CE(re.escape(CTRLGEN), 0),
    CE(u'\t', 0), CE(u'\t', 1),
]
EQ = [
    CE(u'>', 0) + u'-' + CE(u'<', 0),
    CE(u'>', 1) + u'-' + CE(u'<', 1),
    CE(FIRSTM, 0) + u'-' + CE(LASTM, 0),
    CE(CTRL, 0) + u'-' + CE(CC, 0),
    CE(u';', 0) + u'-14*' + CE(EXACT14, 0),
    CE(EXACT14, 0) + u'-' + CE(ROWU, 0),
    CE(u'\.\.', 1) + u'-2*' + CE(RANGE, 1),
    CE(u'\[\d+\]', 1) + u'-' + CE(RANGE, 1),
    CE(RANGE, 1) + u'+' + CE(SINGLE, 1) + u'-' + CE(ROWS_S, 1),
    CE(u';', 1) + u'-' + CE(ROWS_S, 1),
    CE(re.escape(KEY4E00), 0) + u'-' + CE(re.escape(KEY4E00), 1),
    CE(re.escape(KEY4E00), 0) + u'-L(\'1\')',
    CE(re.escape(KEY4E00), 1) + u'-L(\'1\')',
    CE(re.escape(u';HYPHEN;'), 0) + u'-L(\'1\')',
    CE(re.escape(ENDP + u';'), 0) + u'-L(\'1\')',
    CE(re.escape(ENDP + u'..'), 1) + u'-L(\'1\')',
    CE(re.escape(CTRLGEN), 1) + u'-L(\'1\')',
    CE(ROWU, 0) + u'-B47_INUCD()-B47_NOUCD()',
    u'B47_ASSIGN()-B47_INUCD()-B47_NOROW()',
    u'B47_SELFN()-B47_ASSIGN()',
    CE(u'Copyright', 0) + u'-' + CE(u'Copyright', 1),
]
put(0, u'+'.join(AB + EQ))
NTERMS0 = len(AB) + len(EQ)
NPRIM0 = D2[u'0'].count(u'CNT(')
print(u'DERIV keys=%d / 0 键 %d 个加法项(CNT 原语 %d 次)' % (len(D2), NTERMS0, NPRIM0))
EV = {u'CNT': CNT, u'L': lambda x: float(x.replace(u',', u'')),
      u'RCOT': lambda i: [NU_RC, NS_RC][i], u'round': round,
      u'B47_ASSIGN': lambda: ASSIGN, u'B47_NOROW': lambda: NOROW, u'B47_NOUCD': lambda: NOUCD,
      u'B47_INUCD': lambda: IN_UCD, u'B47_MARKCOV': lambda: MARKCOV, u'B47_SELFN': lambda: SELF,
      u'B47_SCRIPTS': lambda: SCRIPTS}
for t in AB + EQ:
    v0 = eval(t, {}, EV)
    if abs(v0) > 1e-12:
        print(u'0 键项非零: %-72s -> %s' % (t[:72], v0))
for k, v in D2.items():
    got = eval(v, {}, EV)
    assert abs(got - float(k)) < 1e-9, (k, got, v[:120])
print(u'DERIV 全部独立回算通过; 键 %s' % u' '.join(sorted(D2, key=lambda x: float(x))))

BLOCK = u" 'B47': {" + NL + NL.join(u"  %r: %r," % (k, v) for k, v in
                                    sorted(D2.items(), key=lambda x: float(x[0]))) + NL + u" }," + NL
SRC47 = u"SRC['B47'] = ['%s', '%s']" % (RU, RS) + NL
HELPER = u'''# B47: 派生表的区间展开由审计器自己复算(纯函数, 与条目无关), 使“十万级码位在定义侧无行”也是机检项
def _b47_scan():
    head = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)

    def rr(p):
        s = open(p, encoding='utf-8', errors='replace').read()
        return '\\n'.join([l for l in s.split('\\n') if not head.match(l.strip())])
    U, S = rr('corpus/raw/UnicodeData.txt'), rr('corpus/raw/scripts.txt')
    pts, selfn, scripts, codes = set(), 0, set(), set()
    for l in S.split('\\n'):
        m = re.match('^([0-9A-F]{4,6})(?:\\\\.\\\\.([0-9A-F]{4,6}))?[ \\\\t]*;', l)
        if not m:
            continue
        lo = int(m.group(1), 16)
        hi = int(m.group(2) or m.group(1), 16)
        pts.update(range(lo, hi + 1))
        n = re.search(r'\\[(\\d+)\\]', l)
        selfn += int(n.group(1)) if n else 1
        g = l.split('#')[0].split(';')
        if len(g) > 1:
            scripts.add(g[1].strip())
    for l in U.split('\\n'):
        if re.match('^[0-9A-F]{4,6};', l):
            codes.add(int(l.split(';')[0], 16))
    cov, pend = 0, {}
    for l in U.split('\\n'):
        m = re.match('^([0-9A-F]{4,6});<([^>]*), (First|Last)>;', l)
        if m:
            c = int(m.group(1), 16)
            if m.group(3) == 'First':
                pend[m.group(2)] = c
            else:
                cov += c - pend.pop(m.group(2)) + 1
    return pts, codes, selfn, scripts, cov


_B47_PTS, _B47_CODES, _B47_SELFN, _B47_SCRIPTS, _B47_COV = _b47_scan()
B47_ASSIGN = lambda: len(_B47_PTS)
B47_NOROW = lambda: len(_B47_PTS - _B47_CODES)
B47_NOUCD = lambda: len(_B47_CODES - _B47_PTS)
B47_INUCD = lambda: len(_B47_PTS & _B47_CODES)
B47_MARKCOV = lambda: _B47_COV
B47_SELFN = lambda: _B47_SELFN
B47_SCRIPTS = lambda: len(_B47_SCRIPTS)

'''

AU = u'corpus/audit.py'
s = io.open(AU, encoding='utf-8').read()
if u"SRC['B47']" not in s:
    i0 = s.index(NL + u"SRC['B46']")
    s = s[:i0 + 1] + SRC47 + s[i0 + 1:]
if u'def _b47_scan' not in s:
    i1 = s.index(u'DERIV = {')
    s = s[:i1] + HELPER + s[i1:]
TAIL = u"B45_AONLY=B45_AONLY, B45_NONLY=B45_NONLY, B45_AFLAT=B45_AFLAT)"
if u'B47_ASSIGN=B47_ASSIGN' not in s:
    assert s.count(TAIL) == 1, s.count(TAIL)
    s = s.replace(TAIL, TAIL[:-1] + u", B47_ASSIGN=B47_ASSIGN, B47_NOROW=B47_NOROW, B47_NOUCD=B47_NOUCD,"
                                    u" B47_INUCD=B47_INUCD, B47_MARKCOV=B47_MARKCOV, B47_SELFN=B47_SELFN,"
                                    u" B47_SCRIPTS=B47_SCRIPTS)", 1)
if u"'B46'}" in s and u"'B47'}" not in s:
    s = s.replace(u"'B46'}", u"'B46', 'B47'}", 1)
s = re.sub(u" 'B47': \\{" + NL + u".*?" + NL + u" \\}," + NL, lambda m: BLOCK, s, count=1, flags=re.S)
if u"'B47': {" not in s:
    k0 = s.index(u'DERIV = {' + NL) + len(u'DERIV = {' + NL)
    s = s[:k0] + BLOCK + s[k0:]
io.open(AU, 'w', encoding='utf-8').write(s)

AC = u'corpus/atomcheck.py'
a = io.open(AC, encoding='utf-8').read()
if u"SRC['B47']" not in a:
    i2 = a.index(u"SRC['B46']")
    a = a[:i2] + SRC47 + a[i2:]
    io.open(AC, 'w', encoding='utf-8').write(a)
io.open(u'corpus/_atoms47.txt', 'w', encoding='utf-8').write(NL.join(sorted(set(AN.values()))) + NL)
ST = [(u'anchors', ANCH), (u'uniq_anchor', UANCH), (u'anchor_U', NU_AN), (u'anchor_S', NS_AN),
      (u'deriv_keys', len(D2)), (u'n_term0', NTERMS0), (u'n_prim0', NPRIM0), (u'n_absent', len(AB)),
      (u'n_equ', len(EQ)), (u'gloss_lines', GLOS), (u'body_chars', len(BODY_MD)),
      (u'rows_u', N_ROWU), (u'semi_u', N_SEMIU), (u'empt4', N_EMPT4), (u'mark', N_MARK),
      (u'pairs', N_FIRST), (u'ctrl', N_CTRL), (u'co', N_CO), (u'mn', N_MN), (u'lo', N_LO),
      (u'nd', N_ND), (u'lt_u', LT_U), (u'lt_s', N_LT_S), (u'hyp_u', N_HYP_U), (u'hypf_u', N_HYPF_U),
      (u'hyp_s', N_HYP_S), (u'han_sub', N_HAN_U), (u'latin_u', N_LATU), (u'latin_s', N_LATU_S),
      (u'cjk_u', N_CJK_U), (u'cjk_s', N_CJK_S), (u'k4e00', N_4E00_U), (u'sq_u', N_SQ_U), (u'sq_s', N_SQ_S),
      (u'rows_s', N_ROWS), (u'rng', N_RNG), (u'sgl', N_SGL), (u'dotdot', N_DDS), (u'brk', N_BRKS),
      (u'und_s', N_UNDS), (u'common', N_COMMON), (u'inher', N_INHER), (u'latinr', N_LATIN_R),
      (u'lens', N_LENS), (u'mns', N_MNS), (u'los', N_LOS), (u'nds', N_NDS), (u'ccs', N_CCS),
      (u'rcot_u', NU_RC), (u'rcot_s', NS_RC), (u'full_u', NU_FULL), (u'full_s', NS_FULL),
      (u'bytes_u', BYTES[0]), (u'bytes_s', BYTES[1]), (u'dropped_s', DROPPED_S), (u'rcot_sum', NU_RC + NS_RC),
      (u'uni_file', N_UNI_FILE), (u'ver_file', N_VER_FILE), (u'date_file', N_DATE_FILE),
      (u'assign', ASSIGN), (u'scripts_n', SCRIPTS), (u'norow', NOROW), (u'in_ucd', IN_UCD),
      (u'noucd', NOUCD), (u'markcov', MARKCOV), (u'selfsum', SELF), (u'spans', SPANS),
      (u'endpoint_u', E_U), (u'endpoint_s', E_S), (u'only_ucd_hex', ONLY_UCD),
      (u'unk_file_s', N_UNK_FILE), (u'miss_file_s', N_MISS_FILE), (u'uncovered', UNCOVERED),
      (u'orphan_pairs', u' '.join(ORPH_PAIRS)), (u'cover_pairs', COVER_PAIRS),
      (u'squared_row', SQUARED_ROW), (u'ctrlgen', CTRLGEN),
      (u'cc_rows', u' ⇎ '.join(x[:46] for x in CCROW)), (u'sha_u', SHA(RU)), (u'sha_s', SHA(RS))]
io.open(u'corpus/_f47stats.txt', 'w', encoding='utf-8').write(NL.join(u'%s\t%s' % (k, v) for k, v in ST) + NL)
print(u'wired B47: audit SRC/HELPER/DERIV(%d keys) + atomcheck SRC + _atoms47.txt(%d uniq)' % (len(D2), UANCH))
print(u'rcot %d/%d full %d/%d bytes %d/%d 展开 %d/%d/%d/%d/%d 自报 %d 标记覆盖 %d' %
      (NU_RC, NS_RC, NU_FULL, NS_FULL, BYTES[0], BYTES[1], ASSIGN, NOROW, IN_UCD, NOUCD, SCRIPTS, SELF, MARKCOV))
