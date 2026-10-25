# -*- coding: utf-8 -*-
"""B52 选锚 + 现算: 一张会过期的分区表 ⇎ 检查它的 awk ⇎ 生成它真值输入的 Makefile ⇎ 它的姊妹表。
四个源: ⟦N⟧ raw/tz/zonenow.tab ⇎ ⟦Z⟧ raw/tz/zone1970.tab ⇎ ⟦K⟧ raw/tz/checknow.awk ⇎ ⟦M⟧ raw/tz/Makefile
锚不手抄: 全部由本脚本按行规则从四个源里切出, 命中列由 prose_norm 折叠后逐字搜索现推。
“从现在起一致”这一谓词不可由在库文件判定: 检查器的真值输入 zdump-now.tab 只在构建目录里生成又删除,
本脚本只量“它在库内为 0 份”与两遍调用的口径差, 不假装机检。
所有发布数字写进 _b52meas.json; audit 侧 _b52_scan 独立复写同一套算法, 三边不符就证明失败。"""
import io, os, re, sys, glob, json, datetime
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = u'corpus'
TZ = u'%s/raw/tz' % C
TAGS = [u'N', u'Z', u'K', u'M']
PATHS = [u'%s/zonenow.tab' % TZ, u'%s/zone1970.tab' % TZ,
         u'%s/checknow.awk' % TZ, u'%s/Makefile' % TZ]
NL = u'\n'
RD = lambda p: io.open(os.path.join(ROOT, p), encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATHS]
TTAB = RD(u'%s/zone.tab' % TZ)
VER = RD(u'%s/version' % TZ).strip()


def pn(s):
    """与 audit.prose_norm 同一口径: 忽略大小写/引号/破折号/空白, 只保留词序。"""
    s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
    s = re.sub(u'[’\'"\u2018\u2019`´]+', u'', s)
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


def lines(x):
    return [l.rstrip(u'\r') for l in x.split(NL) if l.strip()]


def com_dat(ls):
    return [x for x in ls if x.startswith(u'#')], [x for x in ls if not x.startswith(u'#')]


L = [lines(t) for t in TXT]
COM, DAT = zip(*[com_dat(L[i]) for i in range(4)])
STAT = dict((TAGS[i], {
    u'bytes': os.path.getsize(os.path.join(ROOT, PATHS[i])),
    u'chars': len(TXT[i]),
    u'nonempty': len(L[i]),
    u'com': len(COM[i]),
    u'dat': len(DAT[i]),
    u'tabline': sum(1 for x in L[i] if u'\t' in x),
    u'nonascii': sum(1 for ch in TXT[i] if ord(ch) > 127),
}) for i in range(4))
TL = lines(TTAB)
TC, TD = com_dat(TL)
FLD = dict((TAGS[i], dict(sorted(Counter(len(x.split(u'\t')) for x in DAT[i]).items()))) for i in (0, 1))
FLD[u'T'] = dict(sorted(Counter(len(x.split(u'\t')) for x in TD).items()))
assert STAT[u'N'][u'dat'] == 91 and STAT[u'N'][u'com'] == 211, STAT[u'N']
assert STAT[u'Z'][u'dat'] == 312 and len(TD) == 418, (STAT[u'Z'], len(TD))

# ---------- ⟦N⟧ 的组标签机器: 排序键只活在注释层 ----------
def parse_tag(line):
    m = re.match(u'^# ([-+]\\d{2}(?::\\d{2})?)(?:/([-+]\\d{2}(?::\\d{2})?))?(.*)$', line)
    if not m:
        return None
    rest = m.group(3)
    ab = u''
    if rest.startswith(u' - '):
        ab = rest[3:]
        ab = u'' if ab.startswith(u'(') else ab.split(u' (')[0]
    return (m.group(1), m.group(2), ab, rest)


def hh(o):
    s = -1 if o[0] == u'-' else 1
    p = o[1:].split(u':')
    return s * (int(p[0]) + (int(p[1]) / 60.0 if len(p) > 1 else 0))


GRP, UNTAGGED, BARE, OTHER = [], 0, 0, 0
for x in L[0]:
    if x.startswith(u'#'):
        p = parse_tag(x)
        if p:
            GRP.append([x, p[0], p[1], p[2], []])
        elif x.strip() == u'#':
            BARE += 1
        else:
            OTHER += 1
    else:
        if not GRP:
            UNTAGGED += 1
        else:
            GRP[-1][4].append(x.split(u'\t'))
assert UNTAGGED == 0 and len(GRP) == 91, (UNTAGGED, len(GRP))
assert sum(len(c[4]) for c in GRP) == 91
assert sorted(Counter(len(c[4]) for c in GRP).items()) == [(1, 91)]
R0 = [c[4][0] for c in GRP]                      # 每组恰一行 ⇒ 标签序⇎行序是同一序列
SIZES = dict(sorted(Counter(len(c[4]) for c in GRP).items()))
SEQ = [hh(c[1]) for c in GRP]
INV = sum(1 for i in range(len(SEQ) - 1) if SEQ[i] > SEQ[i + 1])
OFFKIND = dict(sorted(Counter(SEQ).items()))
REPEATED = [k for k, v in OFFKIND.items() if v > 1]
DSTG = sum(1 for c in GRP if c[2])
ABG = sum(1 for c in GRP if c[3])
DUP_TAG = len(GRP) - len(set(c[0] for c in GRP))
NONINT = sum(1 for c in GRP if u':' in c[1] or (c[2] and u':' in c[2]))
MINUTES = sorted(set(int(o.split(u':')[1]) for c in GRP for o in [c[1], c[2] or u''] if u':' in o))

# ---------- 缩写闭合: 标签里的缩写 ⇎ 同行注释里的第一枚括号 ⇎ 末枚括号 ----------
def parens(comment):
    return re.findall(u'\\(([^()]*)\\)', comment)


def par_ab(comment):
    p = parens(comment)
    return p[-1] if p else u''


def first_ab(comment):
    p = parens(comment)
    return p[0] if p else u''


WITH_TAG = [c for c in GRP if c[3]]
WITH_PAR = [c for c in GRP if par_ab(c[4][0][3])]
WITH_FIRST = [c for c in GRP if first_ab(c[4][0][3])]
EQ_FIRST = sum(1 for c in WITH_TAG if c[3] == first_ab(c[4][0][3]))
EQ_LAST = sum(1 for c in WITH_TAG if c[3] == par_ab(c[4][0][3]))
IN_ANY = sum(1 for c in WITH_TAG if c[3] in parens(c[4][0][3]))
GAPLIST = [(c[4][0][2], c[3], parens(c[4][0][3])) for c in WITH_TAG if c[3] not in parens(c[4][0][3])]
REVERSE = sum(1 for c in GRP if not c[3] and parens(c[4][0][3]))
NPAREN = sum(len(parens(c[4][0][3])) for c in GRP)
TWO_PAR = sum(1 for c in GRP if len(parens(c[4][0][3])) > 1)

# ---------- 组标签自述的过期: 三行的标签⇎注释指向两个时刻 ----------
EXPIRE = [(c[4][0][2], c[3], first_ab(c[4][0][3]), c[1], c[2]) for c in GRP if u'until' in c[0]]

# 缺口分三类: 注释里无括号 ⇎ 标签⇎注释指着两个时刻(带 until 条款) ⇎ 只差空白(写法)
EXPZ = set(x[0] for x in EXPIRE)
GAP_NOPAR = sum(1 for g in GAPLIST if not g[2])
GAP_TENSE = sum(1 for g in GAPLIST if g[0] in EXPZ)
GAP_SPACE = sum(1 for g in GAPLIST if g[2] and g[0] not in EXPZ
                and u''.join(g[1].split()) in [u''.join(p.split()) for p in g[2]])
assert GAP_NOPAR + GAP_TENSE + GAP_SPACE == len(GAPLIST), (GAP_NOPAR, GAP_TENSE, GAP_SPACE, len(GAPLIST))

# ---------- 声明的三层排序键(规则 3)是否可机检且成立 ----------
STEP = dict(sorted(Counter(round(hh(c[2]) - hh(c[1]), 2) for c in GRP if c[2]).items()))
K2INV = sum(1 for i in range(len(GRP) - 1)
            if GRP[i][1] == GRP[i + 1][1] and GRP[i][2] and not GRP[i + 1][2])
K3PAIRS = [(GRP[i][3], GRP[i + 1][3]) for i in range(len(GRP) - 1)
           if GRP[i][1] == GRP[i + 1][1] and (GRP[i][2] or u'') == (GRP[i + 1][2] or u'')
           and GRP[i][3] and GRP[i + 1][3]]
K3INV = sum(1 for a, b in K3PAIRS if a > b)
MAXPEROFF = max(OFFKIND.values())
OFFPAIRK = len(set((c[1], c[2] or u'') for c in GRP))

# ---------- 偏移值在数据层可见吗 ----------
OFFSHAPE = re.compile(u'(?<![0-9:+-.])[-+]\\d{2}(?::\\d{2})?(?![0-9])')
row_off_any = sum(1 for f in R0 if any(OFFSHAPE.search(x) for x in f[1:]))
row_off_cmt = sum(1 for f in R0 if OFFSHAPE.search(f[3]))
row_off_zone = sum(1 for f in R0 if OFFSHAPE.search(f[2]))
tag_off_lines = len(GRP)
hdr = [x for x in COM[0] if x.startswith(u'#XX')]
assert len(hdr) == 1 and hdr[0] == u'#XX\tcoordinates\tTZ\tcomments', hdr

# ---------- 坐标形状: 同一列的两种书写法 ----------
def latlon(c):
    m = re.match(u'^([-+]\\d+)([-+]\\d+)$', c)
    return (m.group(1)[1:], m.group(2)[1:]) if m else (None, None)


CW = dict(sorted(Counter(len(f[1]) for f in R0).items()))
LATW = dict(sorted(Counter(len(latlon(f[1])[0]) for f in R0).items()))
LONW = dict(sorted(Counter(len(latlon(f[1])[1]) for f in R0).items()))
LATL = sorted(set(len(latlon(f[1])[0]) for f in R0))
LONL = sorted(set(len(latlon(f[1])[1]) for f in R0))
LEAD0 = sum(1 for f in R0 if re.search(u'[-+]0\\d', f[1]))
LEAD0C = sum(1 for f in R0 for c in latlon(f[1]) if c and c[0] == u'0')
MIXED = sum(1 for f in R0 if (len(latlon(f[1])[0]) == 4) != (len(latlon(f[1])[1]) == 5))
NAST = dict((TAGS[i], sorted(set(ch for ch in TXT[i] if ord(ch) > 127))) for i in range(4))
BADPARSE = [f[1] for f in R0 if None in latlon(f[1])]
assert not BADPARSE, BADPARSE

# ---------- 第四列(注释列)口径: 表自述“每行非空” ----------
C4 = [f[3] for f in R0]
assert all(C4) and all(len(f) == 4 for f in R0)
C4SEMI = sum(1 for x in C4 if u';' in x)
C4PAR = sum(1 for x in C4 if u'(' in x)
C4BOTH = sum(1 for x in C4 if u';' in x and u'(' in x)
C4KIND = len(set(C4))

# ---------- ISO 日期: 全在注释层 ----------
ISO = re.compile(u'\\d{4}-\\d{2}-\\d{2}')
ISOL = [(x.startswith(u'#'), ISO.search(x).group(0), x) for x in L[0] if ISO.search(x)]
ISO_C = sum(1 for x in ISOL if x[0])
DATES = sorted(set(x[1] for x in ISOL))
UNTIL = [x[2] for x in ISOL if u'until' in x[2]]
BDAY = [x[2] for x in ISOL if u'Eggert' in x[2]]
ZDAY = [ISO.search(x).group(0) for x in L[1] if ISO.search(x)]
ZBD = [x for x in L[1] if u'Eggert' in x]
GAP_DAY = (datetime.date(2026, 11, 1) - datetime.date(2023, 12, 18)).days
GAP_BIR = (datetime.date(2025, 5, 15) - datetime.date(2023, 12, 18)).days

# ---------- 谓词句: 现在时预测 ⇎ 过去时已然 ----------
PRED = [x for x in L[0] if u'agree from now on' in x]
PRED70 = [x for x in L[1] if u'agreed since 1970' in x]
NOWPH = [x for x in L[0] if u'now' in x]
assert len(PRED) == 2 and len(PRED70) >= 1, (len(PRED), len(PRED70))

# ---------- ⟦Z⟧ 的第一列: 真国码 ⇎ ⟦N⟧ 恒等 XX ----------
COL1 = [f[0] for f in R0]
assert set(COL1) == {u'XX'}
ZROWS = [x.split(u'\t') for x in DAT[1]]
Z1 = [f[0] for f in ZROWS]
ZMULTI = sum(1 for c in Z1 if u',' in c)
ZKIND = len(set(Z1))
ZSEQ = [c.split(u',')[0] for c in Z1]
ZINV = sum(1 for i in range(len(ZSEQ) - 1) if ZSEQ[i] > ZSEQ[i + 1])
Z4EMPTY = sum(1 for f in ZROWS if len(f) < 4 or not f[3].strip())
Z4KIND = len(set(pn(f[3]) for f in ZROWS if len(f) > 3 and f[3].strip()))
ZN = dict((f[2], f) for f in ZROWS)
TROWS = [x.split(u'\t') for x in TD]
EX_NOW = [f[2] for f in R0]
EX_70 = [f[2] for f in ZROWS]
EX_TAB = [f[2] for f in TROWS]
NZ = [f for f in R0 if f[2] in ZN]
assert len(NZ) == 91, len(NZ)
COORD_EQ = sum(1 for f in NZ if f[1] == ZN[f[2]][1])
CC_EQ = sum(1 for f in NZ if f[0] == ZN[f[2]][0])
C4_EQ = sum(1 for f in NZ if len(ZN[f[2]]) > 3 and pn(f[3]) == pn(ZN[f[2]][3]))
Z4HAS = sum(1 for f in NZ if len(ZN[f[2]]) > 3 and ZN[f[2]][3].strip())
ONLY70 = sorted(set(EX_70) - set(EX_NOW))
ONLYTAB = sorted(set(EX_TAB) - set(EX_NOW))
DUPN = len(EX_NOW) - len(set(EX_NOW))
DUP70 = len(EX_70) - len(set(EX_70))
DUPTAB = len(EX_TAB) - len(set(EX_TAB))

# ---------- 逐字复现的几种粒度: ⟦N⟧ 数据层 ⇎ ⟦Z⟧ 数据层 ----------
def toks(s):
    return re.findall(u'[a-z0-9]+', s.lower())


def shingle(ls, n=5):
    w = [t for l in ls for t in toks(l)]
    return set(tuple(w[i:i + n]) for i in range(len(w) - n + 1))


NRAW = [u'\t'.join(f) for f in R0]
ZRAW = [u'\t'.join(f) for f in ZROWS]
TRAW = [u'\t'.join(f) for f in TROWS]
GR = {
    u'line': len(set(pn(x) for x in NRAW) & set(pn(x) for x in ZRAW)),
    u'coord': COORD_EQ,
    u'zone': len(set(EX_NOW) & set(EX_70)),
    u'c4': len(set(pn(x) for x in C4) & set(pn(f[3]) for f in ZROWS if len(f) > 3 and f[3].strip())),
    u'shang': len(shingle(NRAW) & shingle(ZRAW)),
    u'shang_nt': len(shingle(NRAW) & shingle(TRAW)),
    u'shang_self': len(shingle(NRAW) & shingle(COM[0])),
}
SHN, SHZ, SHT = len(shingle(NRAW)), len(shingle(ZRAW)), len(shingle(TRAW))
FULL = [pn(t) for t in TXT]
COMT = [x.lstrip(u'#').strip() for x in COM[0]]
SH3 = {
    u'n_c3': len(shingle(NRAW, 3)), u'c_c3': len(shingle(COMT, 3)),
    u'nc3': len(shingle(NRAW, 3) & shingle(COMT, 3)),
    u'nc2': len(shingle(NRAW, 2) & shingle(COMT, 2)),
    u'zc3': len(shingle(ZRAW, 3) & shingle(COMT, 3)),
}

# ---------- 同一个名字能穿过几层: 折叠后的命中矩阵 ----------
CROSS = [u'zdump_table', u'zdump-now.tab', u'zdump-1970.tab', u'from now on',
         u'agree from now on', u'irrelevant and ignored', u'XX', u'Pacific/Kiritimati',
         u'-1416-17042', u'+12:45/+13:45', u'zone1970.tab', u'zonenow.tab',
         u'checknow.awk', u'now.ck', u'until 2026-11-01']
HIT = dict((t, u''.join(TAGS[k] for k in range(4) if pn(t) in FULL[k]) or u'—') for t in CROSS)

# ---------- ⟦K⟧ 检查器: 读了哪几列, 真值从哪来 ----------
KD = u'\n'.join(L[2])
FREF = sorted(set(re.findall(u'\\$(\\d)', KD)))
FREFC = dict((n, len(re.findall(u'\\$%s(?![0-9])' % n, KD))) for n in (u'0', u'1', u'2', u'3', u'4'))
FSLINE = [i + 1 for i, x in enumerate(L[2]) if re.search(u'^\\s*FS = ', x)]
GTLINE = [i + 1 for i, x in enumerate(L[2]) if u'getline <zdump_table' in x]
assert len(FSLINE) == 1 and len(GTLINE) == 1 and GTLINE[0] < FSLINE[0], (FSLINE, GTLINE)
FSVAL = re.findall(u'FS = "([^"]*)"', KD)
BLK = TXT[3].split(u'now.ck:', 1)[1].split(u'\ntables.ck:', 1)[0]
EXT = sorted(set(re.findall(u'-v (\\w+)=', BLK)))
EXTH = dict((v, len(re.findall(u'\\b%s\\b' % v, KD))) for v in EXT)
ASSIGNED = set(re.findall(u'^\\s*(\\w+)\\s*=', KD, re.M))
UNSET = sorted(v for v in (u'now', u'now_out', u'zdump_table') if v not in ASSIGNED)
PRINTF = re.findall(u'printf "([^"]*)"', KD)
PQTY = sorted(set(PRINTF))
STATUS = len(re.findall(u'status = 1', KD))
EXITL = len(re.findall(u'exit status', KD))
SKIPR = len(re.findall(u'\\[\\^#\\]', KD))
ZDNOW = len(re.findall(u'zdump-now', KD))
ZONEDATA = len(re.findall(u'zone_data\\[zone\\]', KD))
ZONENOWD = len(re.findall(u'zonenow\\[data\\]', KD))
IDENT = len(re.findall(u'identical from now on', KD))
NODATA = len(re.findall(u'no data', KD))
LINES_K = len(L[2])
KCOM = [x for x in L[2] if x.startswith(u'#')]

# ---------- ⟦M⟧ 构建器: 真值输入的生与死 ----------
MD = TXT[3]
MKPR = re.findall(u'^now\\.ck: (.*)$', MD, re.M)[0].split()
MKPR_OK = [p for p in MKPR if os.path.exists(os.path.join(ROOT, TZ, p))]
CKTARGET = re.findall(u'^([\\w.]+\\.ck):', MD, re.M)
RMN = len(re.findall(u'rm -fr \\$@d', BLK))
MKDIRN = len(re.findall(u'mkdir \\$@d', BLK))
ZIC = len(re.findall(u'\\./zic -d \\$@d', BLK))
ZDUMP2 = re.findall(u'\\./zdump -i -t ([^ \\)]*)', BLK)
NOWS = re.findall(u'^CHECK_NOW_TIMESTAMP = (.*)$', MD, re.M)
YEARS = int(re.findall(u'^CHECK_NOW_FUTURE_YEARS = (\\d+)$', MD, re.M)[0])
DAYSEC = 24 * 60 * 60
SECS = YEARS * 366 * DAYSEC
SECS365 = YEARS * 365 * DAYSEC
BIG = int(re.findall(u'(\\d{4})\\+ years', MD)[0])
GLOBS = re.findall(u'-name (\\S+)', BLK)
FINDS = len(re.findall(u'\\$\\(find ', BLK))
ZDFILES = glob.glob(os.path.join(ROOT, C, u'raw', u'**', u'*zdump*'), recursive=True)
CKFILES = glob.glob(os.path.join(ROOT, C, u'**', u'now.ck'), recursive=True)
CKLINE = re.findall(u'^check: (.*)$', MD, re.M)[0].split()
MVOUT = len(re.findall(u'mv \\$@\\.out \\$@', BLK))
DOLLARNOW = len(re.findall(u'\\$\\$now', BLK))
NONTAB = len(re.findall(u"! -name '\\*\\.tab'", BLK))
AWKCALL = len(re.findall(u'-f checknow\\.awk', BLK))
TABLEARG = len(re.findall(u'-f checknow\\.awk zonenow\\.tab', BLK))
SYNV = len(re.findall(u'SysVzone\\[', BLK))

# ---------- 词条出现矩阵(原样, 不折叠) ----------
TOK = [u'zdump_table', u'zdump-now.tab', u'zdump-1970.tab', u'now.ck', u'checknow.awk',
       u'zonenow.tab', u'zone1970.tab', u'from now on', u'XX', u'irrelevant', u'1970', u'until']
OCC = dict((t, [TXT[i].count(t) for i in range(4)]) for t in TOK)

# ---------- 候选锚池: 按规则切, 命中列现推 ----------
CAND = []


def add(kind, i, s, nmin=16):
    s = s.strip()
    if len(s) < nmin or NL in s:
        return
    n = pn(s)
    h = tuple(k for k in range(4) if n and n in FULL[k])
    if not h:
        return
    cl = u'single' if len(h) == 1 else (u'all4' if len(h) == 4 else u'cross')
    CAND.append((kind, TAGS[i], s, u''.join(TAGS[k] for k in h), cl, len(s)))


# 1) ⟦N⟧ 头部四条改动句 + 实验句 + 谓词句 + 列头行
for x in COM[0]:
    if re.match(u'^# [1-4]\\.', x) or u'experimental' in x or u'irrelevant' in x:
        add(u'header_rule', 0, x, nmin=12)
for x in PRED + NOWPH + BDAY + UNTIL:
    add(u'predicate', 0, x, nmin=12)
add(u'colhdr', 0, hdr[0])
# 2) 组标签: 首末、半小时/45 分钟、最长的、前 12 个
add(u'tag_first', 0, GRP[0][0])
add(u'tag_last', 0, GRP[-1][0])
for c in GRP:
    if u':' in c[1] or (c[2] and u':' in c[2]):
        add(u'tag_nonint', 0, c[0])
for c in sorted(GRP, key=lambda c: -len(c[0]))[:6]:
    add(u'tag_longest', 0, c[0])
for c in GRP[:12]:
    add(u'tag_head', 0, c[0], nmin=8)
# 3) 数据行: 前 6 行 ⇎ 最长的 5 行 ⇎ 15 字符坐标行 ⇎ 带分号行
for f in R0[:6] + sorted(R0, key=lambda f: -len(u'\t'.join(f)))[:5] + \
         [f for f in R0 if len(f[1]) == 15][:3] + [f for f in R0 if u';' in f[3]][:4]:
    add(u'row_n', 0, u'\t'.join(f), nmin=10)
# 4) ⟦Z⟧: 同一时区的对应行(第一列真国码 ⇎ XX) + 最长国码行 + 表头与谓词句
for f in NZ[:6] + sorted(ZROWS, key=lambda f: -len(f[0]))[:4] + ZROWS[:3]:
    add(u'row_z', 1, u'\t'.join(f), nmin=10)
add(u'pred_z', 1, PRED70[0], nmin=12)
for x in COM[1][:8] + ZBD[:1]:
    add(u'header_z', 1, x, nmin=12)
for x in [y for y in COM[1] if re.match(u'^# [1-4]\\.', y)]:
    add(u'header_z_num', 1, x, nmin=12)
# 5) ⟦K⟧: 跳过注释的那句、只读第三列、真值输入的入口、四条 printf、退出
SEL = [x for x in L[2] if re.search(u'\\[\\^#\\]', x)] + \
      [x for x in L[2] if re.search(u'zone = \\$3', x)] + \
      [x for x in L[2] if u'getline <zdump_table' in x] + \
      [x for x in L[2] if x.strip().startswith(u'printf')] + \
      [x for x in L[2] if re.search(u'FS = ', x)] + \
      [x for x in L[2] if u'exit status' in x] + \
      [x for x in L[2] if u'zonenow[data]' in x] + \
      [x for x in L[2] if u'status = 1' in x] + KCOM + \
      [x for x in L[2] if u'sub(/' in x]
for x in SEL:
    add(u'awk_rule', 2, x, nmin=8)
# 6) ⟦M⟧: 依赖行、两遍调用的 horizon、真值输入的生成与删除、28 ⇎ 2800、日期现取
for x in L[3]:
    if (u'now.ck' in x or u'zdump-now' in x or u'zdump-1970' in x or u'CHECK_NOW' in x or
            u'2800+' in x or u'-t $$now' in x or u'-t 0,$$future' in x or
            u'-f checknow.awk' in x or u'mkdir $@d' in x or u'rm -fr $@d' in x or
            u'mv $@.out' in x or u'./zic' in x):
        add(u'make_rule', 3, x, nmin=8)

# 7) 跨层短锚: 同一个对象在不同层里的写法, 命中列即“能穿过几层”
for f in R0[:4]:
    add(u'cross_coord', 0, f[1], nmin=8)
    add(u'cross_zone', 0, f[2], nmin=8)
for t in (u'from now on', u'agree from now on', u'irrelevant and ignored', u'until 2026-11-01'):
    add(u'cross_phrase', 0, t, nmin=8)
for t in (u'zdump_table', u'zdump-now.tab', u'now.ck', u'checknow.awk', u'-v zdump_table',
          u'FS = "\\t"', u'identical from now on'):
    add(u'cross_code', 3, t, nmin=6)
for c in GRP:
    if u'until' in c[0]:
        add(u'expire_pair', 0, c[4][0][3], nmin=10)

seen, POOL = set(), []
for c in CAND:
    if c[2] in seen:
        continue
    seen.add(c[2])
    POOL.append(c)

out = [u'%3d %-14s ⟦%s⟧ [%s:%s] %d %s' % (n, k, t, h, cl, ln, s.replace(u'\t', u' ⇥ ')[:110])
       for n, (k, t, s, h, cl, ln) in enumerate(POOL)]
io.open(os.path.join(ROOT, C, u'_pool52.txt'), 'w', encoding='utf-8', newline='\n').write(NL.join(out) + NL)

MEAS = {
    u'version': VER, u'stat': STAT, u'fld': FLD,
    u'grp_sizes': SIZES, u'grp': len(GRP), u'rows': len(R0),
    u'off_kinds': len(OFFKIND), u'off_repeat': len(REPEATED),
    u'dst_groups': DSTG, u'ab_groups': ABG, u'dup_tag': DUP_TAG,
    u'bare_hash': BARE, u'other_com': OTHER,
    u'with_par': len(WITH_PAR), u'with_first': len(WITH_FIRST), u'with_tag': len(WITH_TAG),
    u'eq_first': EQ_FIRST, u'eq_last': EQ_LAST, u'in_any': IN_ANY,
    u'gap_list': GAPLIST, u'reverse_gap': REVERSE, u'nparen': NPAREN, u'two_par': TWO_PAR,
    u'gap_nopar': GAP_NOPAR, u'gap_tense': GAP_TENSE, u'gap_space': GAP_SPACE,
    u'expire': EXPIRE, u'step': STEP, u'k2inv': K2INV, u'k3pairs': len(K3PAIRS), u'k3inv': K3INV,
    u'max_per_off': MAXPEROFF, u'off_pair_kinds': OFFPAIRK,
    u'inv': INV, u'zinv': ZINV, u'off_first': SEQ[0], u'off_last': SEQ[-1],
    u'nonint': NONINT, u'minutes': MINUTES,
    u'row_off_any': row_off_any, u'row_off_cmt': row_off_cmt, u'row_off_zone': row_off_zone,
    u'coord_w': CW, u'lat_w': LATW, u'lon_w': LONW, u'latl': LATL, u'lonl': LONL,
    u'lead0': LEAD0, u'lead0c': LEAD0C, u'mixed': MIXED, u'nast': NAST,
    u'c4_semi': C4SEMI, u'c4_par': C4PAR, u'c4_both': C4BOTH, u'c4_kind': C4KIND,
    u'iso': len(ISOL), u'iso_c': ISO_C, u'iso_d': len(ISOL) - ISO_C, u'dates': DATES,
    u'until': len(UNTIL), u'gap_day': GAP_DAY, u'gap_bir': GAP_BIR,
    u'pred': len(PRED), u'pred70': len(PRED70), u'nowph': len(NOWPH),
    u'col1_kind': len(set(COL1)), u'z_multi': ZMULTI, u'z_kind': ZKIND,
    u'z4_empty': Z4EMPTY, u'z4_has': Z4HAS, u'z4_kind': Z4KIND,
    u'coord_eq': COORD_EQ, u'cc_eq': CC_EQ, u'c4_eq': C4_EQ,
    u'n_shared': len(NZ), u'only70': len(ONLY70), u'onlytab': len(ONLYTAB),
    u'dupn': DUPN, u'dup70': DUP70, u'duptab': DUPTAB,
    u'grain': GR, u'sh_n': SHN, u'sh_z': SHZ, u'sh_t': SHT, u'sh3': SH3, u'hit': HIT,
    u'k_fref': FREF, u'k_frefc': FREFC, u'k_fs': FSVAL, u'k_fsline': FSLINE[0],
    u'k_gtline': GTLINE[0], u'k_ext': EXT, u'k_exth': EXTH, u'k_unset': UNSET,
    u'k_printf': len(PRINTF), u'k_printf_kinds': len(PQTY), u'k_status': STATUS,
    u'k_exit': EXITL, u'k_skip': SKIPR, u'k_zdumpnow': ZDNOW, u'k_zone_data': ZONEDATA,
    u'k_zonenowd': ZONENOWD, u'k_ident': IDENT, u'k_nodata': NODATA,
    u'k_lines': LINES_K, u'k_com': len(KCOM),
    u'm_prereq': len(MKPR), u'm_prereq_ok': len(MKPR_OK),
    u'm_prereq_missing': sorted(set(MKPR) - set(MKPR_OK)),
    u'm_ck': len(CKTARGET), u'm_rm': RMN, u'm_mkdir': MKDIRN, u'm_zic': ZIC,
    u'm_horizon': ZDUMP2, u'm_years': YEARS, u'm_secs': SECS, u'm_secs365': SECS365,
    u'm_big_years': BIG, u'm_ratio': BIG // YEARS, u'm_names': sorted(set(GLOBS)),
    u'm_finds': FINDS, u'm_zdump_files': len(ZDFILES), u'm_ck_files': len(CKFILES),
    u'm_check_deps': CKLINE, u'm_mvout': MVOUT, u'm_dollarnow': DOLLARNOW,
    u'm_nontab': NONTAB, u'm_awkcall': AWKCALL, u'm_tablearg': TABLEARG, u'm_sysv': SYNV,
    u'occ': OCC, u'anchors_pool': len(POOL),
}
json.dump(dict(meas=MEAS, tags=TAGS, paths=PATHS,
               pool=[(k, t, s, h, c, l) for (k, t, s, h, c, l) in POOL]),
          io.open(os.path.join(ROOT, C, u'_b52meas.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

P = lambda *a: print(u' '.join(str(x) for x in a))
P(u'版本文件 %s ｜ 四源字节 %s ｜ 非 ASCII %s' % (VER, [STAT[t][u'bytes'] for t in TAGS],
                                          [STAT[t][u'nonascii'] for t in TAGS]))
P(u'非空=注释+数据: %s' % u' ⇎ '.join(u'%s %d=%d+%d' % (
    TAGS[i], STAT[TAGS[i]][u'nonempty'], STAT[TAGS[i]][u'com'], STAT[TAGS[i]][u'dat']) for i in range(4)))
P(u'含制表符的行 %s ｜ 每行字段数 N%s ⇎ Z%s ⇎ T%s' % (
    [STAT[t][u'tabline'] for t in TAGS], FLD[u'N'], FLD[u'Z'], FLD[u'T']))
P(u'N 组: 标签 %d ⇎ 行 %d, 组内行数 %s ｜ 单调 %s 首末 %s⇎%s 逆序 %d ｜ 重复标签行 %d' % (
    len(GRP), len(R0), SIZES, INV == 0, SEQ[0], SEQ[-1], INV, DUP_TAG))
P(u'Z 排序: 国码逆序 %d ｜ 偏移层无(第一列多码 %d, 种类 %d)' % (ZINV, ZMULTI, ZKIND))
P(u'偏移种类 %d(重复 %d) ｜ 非整点 %d(分钟位 %s) ｜ 带第二偏移 %d ｜ 带缩写 %d ｜ 裸# %d ｜ 其他注释 %d' % (
    len(OFFKIND), len(REPEATED), NONINT, MINUTES, DSTG, ABG, BARE, OTHER))
P(u'缩写闭合: 标签带缩写 %d ⇎ 同行有括号 %d ⇎ 第一枚即标签缩写 %d ⇎ 末枚 %d ⇎ 出现在任一括号 %d ｜ 缺口 %d %s ｜ 反向 %d ｜ 括号总数 %d(多枚 %d)' % (
    len(WITH_TAG), len(WITH_PAR), EQ_FIRST, EQ_LAST, IN_ANY, len(GAPLIST), GAPLIST, REVERSE, NPAREN, TWO_PAR))
P(u'自述过期: %d 行 %s' % (len(EXPIRE), EXPIRE))
P(u'三层排序键: 键1 偏移逆序 %d ｜ 键2 DST⇎无DST 逆序 %d ｜ 键3 缩写可比对 %d 逆序 %d' % (INV, K2INV, len(K3PAIRS), K3INV))
P(u'DST 步长分布 %s ｜ 同一偏移最多拆 %d 组 ｜ 偏移对种类 %d' % (STEP, MAXPEROFF, OFFPAIRK))
P(u'偏移值可见性: 任一数据列 %d 行 ｜ 注释列 %d ｜ 时区名列 %d ｜ 标签行 %d' % (
    row_off_any, row_off_cmt, row_off_zone, tag_off_lines))
P(u'坐标宽度 %s ｜ 纬数字位 %s ⇎ 经数字位 %s ｜ 前导零 %d 行 ｜ 不可解析 %s' % (
    CW, LATW, LONW, LEAD0, BADPARSE))
P(u'第四列: 非空 %d/91, 取值 %d 种 ｜ 分号 %d ｜ 括号 %d ｜ 两者 %d' % (
    len(C4), C4KIND, C4SEMI, C4PAR, C4BOTH))
P(u'ISO 日期 %d 处(注释 %d ⇎ 数据 %d), 取值 %s ｜ until %d ｜ 生日句 %s' % (
    len(ISOL), ISO_C, len(ISOL) - ISO_C, DATES, len(UNTIL), BDAY))
P(u'日期差: 生日⇎令日 %d 天 ｜ 两份表生日差 %d 天 (N %s ⇎ Z %s)' % (GAP_DAY, GAP_BIR, DATES, ZDAY))
P(u'谓词句: “agree from now on” %d 句 ⇎ “agreed since 1970” %d 句 ｜ 含 now 的行 %d' % (
    len(PRED), len(PRED70), len(NOWPH)))
P(u'Z 第四列: 空 %d/312, 非空取值 %d 种 ⇎ N 空 0/91' % (Z4EMPTY, Z4KIND))
P(u'共有 %d 个时区: 坐标一致 %d ⇎ 国码一致 %d ⇎ 第四列一致 %d ｜ Z 有注释的 %d' % (
    len(NZ), COORD_EQ, CC_EQ, C4_EQ, Z4HAS))
P(u'集合: now %d(重名 %d) ⊂ 1970 %d(重名 %d) 差 %d ｜ now ⊂ tab %d(重名 %d) 差 %d' % (
    len(EX_NOW), DUPN, len(ZROWS), DUP70, len(ONLY70), len(TROWS), DUPTAB, len(ONLYTAB)))
P(u'粒度(N数据 ⇎ Z数据): 整行 %d ⇎ 坐标 %d ⇎ 时区名 %d ⇎ 第四列 %d ⇎ 五词串 %d' % (
    GR[u'line'], GR[u'coord'], GR[u'zone'], GR[u'c4'], GR[u'shang']))
P(u'五词串总量 N %d ⇎ Z %d ⇎ T %d ｜ N⇎T 共有 %d ｜ N数据⇎N注释 %d' % (
    SHN, SHZ, SHT, GR[u'shang_nt'], GR[u'shang_self']))
P(u'K: 行 %d(注释 %d), 字段引用 %s 计数 %s ｜ FS=%s 在第 %d 行 ⇎ getline 在第 %d 行' % (
    LINES_K, len(KCOM), FREF, FREFC, FSVAL, FSLINE[0], GTLINE[0]))
P(u'K: externals %s 命中 %s ｜ 未赋值 %s ｜ printf %d 条(%d 型) ｜ status=1 ×%d ｜ exit %d ｜ /^[^#]/ ×%d' % (
    EXT, EXTH, UNSET, len(PRINTF), len(PQTY), STATUS, EXITL, SKIPR))
P(u'K: zone_data[zone] %d ⇎ zonenow[data] %d ｜ zdump-now %d ｜ no data %d ｜ identical from now on %d' % (
    ZONEDATA, ZONENOWD, ZDNOW, NODATA, IDENT))
P(u'M: now.ck 前置 %d 项, 在库 %d, 缺 %s ｜ .ck 目标 %s ｜ check 依赖 %s' % (
    len(MKPR), len(MKPR_OK), sorted(set(MKPR) - set(MKPR_OK)), CKTARGET, CKLINE))
P(u'M: horizon %s ｜ find %d 次 -name %s ｜ zic %d ｜ mkdir %d ⇎ rm %d ｜ mv %d ⇎ $$now %d 次' % (
    ZDUMP2, FINDS, sorted(set(GLOBS)), ZIC, MKDIRN, RMN, MVOUT, DOLLARNOW))
P(u'M: 年数 %d ⇎ %d+ (倍 %d) ｜ 秒 %d ⇎ 365 天口径 %d 差 %d ｜ checknow 调用 %d 遍(带表 %d 遍)' % (
    YEARS, BIG, BIG // YEARS, SECS, SECS365, SECS - SECS365, AWKCALL, TABLEARG))
P(u'M: 库内 *zdump* %d 份 ｜ now.ck %d 份 ｜ SysVzone %d 处 ｜ 排除 *.tab %d 处' % (
    len(ZDFILES), len(CKFILES), SYNV, NONTAB))
P(u'词频矩阵: %s' % u' ‖ '.join(u'%s %s' % (t, OCC[t]) for t in TOK))
P(u'穿层矩阵: %s' % u' ‖ '.join(u'%s→%s' % (t, HIT[t]) for t in CROSS))
P(u'短粒度串: 数据层三元 %d ⇎ 注释层三元 %d ｜ 共有 三元 %d ⇎ 二元 %d ⇎ Z注释⇎N注释 %d' % (
    SH3[u'n_c3'], SH3[u'c_c3'], SH3[u'nc3'], SH3[u'nc2'], SH3[u'zc3']))
P(u'候选锚池 %d 条 → corpus/_pool52.txt' % len(POOL))
P(u'  按命中档 %s' % dict(sorted(Counter(c[4] for c in POOL).items())))
P(u'  按归属源 %s' % dict(sorted(Counter(c[1] for c in POOL).items())))
