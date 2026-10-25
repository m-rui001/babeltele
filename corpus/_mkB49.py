# -*- coding: utf-8 -*-
"""B49 表 ⇎ 检查这张表的程序 ⇎ 程序所检查的数据: zone1970.tab ⇎ checktab.awk ⇎ europe。
联结不是"谁生成谁"而是"谁给谁定性": 程序的唯一产物是判决, 判决的正常形态是空。
所有数字由 raw 现算; 条目里的每个数要么是 raw 字面, 要么进 DERIV/0 键。
反向对照与码侧变异的**执行输出**属工具侧, 只出现在 src 行与 ⛓解读注; 但它们的规模在 raw 侧
有同值可证(158 = 相邻相等首码对数 ⇎ 249 = 码表行数 ⇎ 312 = 表行数)。"""
import io, re, sys, os, json, hashlib, collections

sys.stdout.reconfigure(encoding='utf-8')

RT = u'corpus/raw/tz/zone1970.tab'
RC = u'corpus/raw/tz/checktab.awk'
RZ = u'corpus/raw/tz/europe'
RI = u'corpus/raw/tz/iso3166.tab'
RZT = u'corpus/raw/tz/zone.tab'
RAWS = [RT, RC, RZ]
ENTRY = u'corpus/babeltele/B49_table_checker_and_checked_data.md'
LT, LC, LZ = u'T', u'C', u'Z'
NL, TAB, BS = u'\n', u'\t', u'\\'
DATA = [u'africa', u'antarctica', u'asia', u'australasia', u'europe', u'northamerica',
        u'southamerica', u'etcetera', u'factory', u'backward']
HEADRX = re.compile(u'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
rd = lambda p: io.open(p, encoding='utf-8', errors='replace').read()

TXT = [rd(p) for p in RAWS]
LINES = [t.split(NL) for t in TXT]
SRC = [NL.join(l for l in LINES[i] if not HEADRX.match(l.strip())) for i in range(3)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
CNTF = lambda pat, i: len(re.findall(pat, TXT[i], re.I))
RCOT = lambda i: len(SRC[i].strip())
NLINES = [len(x) - 1 for x in LINES]
DROP = [len([l for l in LINES[i] if HEADRX.match(l.strip())]) for i in range(3)]
FULL = [len(t) for t in TXT]
BYTES = [os.path.getsize(p) for p in RAWS]
SHA = [hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in RAWS]
NASCII = [len(re.findall(u'[^\x00-\x7f]', TXT[i])) for i in range(3)]
NASCII_R = [len(re.findall(u'[^\x00-\x7f]', SRC[i])) for i in range(3)]
ITAB = [t.count(TAB) for t in TXT]
ITAB_R = [s.count(TAB) for s in SRC]
NASC_L = len([l for l in SRC[2].split(NL) if any(ord(c) > 127 for c in l)])

# ---------- 模式 ----------
P_ROW_T = u'(?m)^[A-Z][A-Z][0-9A-Za-z,]*' + TAB
P_ISO2 = u'(?m)^[A-Z][A-Z]' + TAB
P_PRINTF = u'(?m)^[ \t]*printf '
P_STATUS = u'status = 1'
P_RED = u'/dev/stderr'
P_ESC = u'\\\\t'
P_FS = u'(?m)^[ \t]*FS = '
P_GETLINE = u'(?m)getline <'
P_INR = u'iso_NR\\+\\+'
P_ZNR = u'zone_NR\\+\\+'
P_MON = u'monthabbr\\["[A-Z][a-z]{2}"\\] = 1'
P_D0 = u'\\$0 ~ /\\^#/'
P_D1 = u'\\$1 ~ /\\^#/'
P_ZT = u'zone_table == "zone.tab"'
P_ZN = u'zonenow.tab'
P_BK = u'"backward"'
P_SIM = u'"Europe/Simferopol"'
P_WANT = u'want_warnings'
P_ZONE = u'(?m)^Zone' + TAB
P_RULE = u'(?m)^Rule'
P_LINK = u'(?m)^Link'
P_CONT = u'(?m)^' + TAB
P_PCT, P_PCTD = u'%s', u'%d'
P_IFO, P_UTF, P_STAB = u'if and only if', u'UTF', u'single tab'
P_SORT, P_POPU, P_GEO = u'(?i)sorted', u'populous', u'geographical'
P_WNC = u'wrong number of columns'
P_OOO = u'out of order'
P_INVC = u'invalid coordinates'
P_NOZONE = u'no Zone table for'
P_NODATA = u'no data for'
P_DUPZ = u'duplicate Zone'
RXMIN = u'^[-+][0-9][0-9][0-5][0-9][-+][01][0-9][0-9][0-5][0-9]$'
RXSEC = u'^[-+][0-9][0-9][0-5][0-9][0-5][0-9][-+][01][0-9][0-9][0-5][0-9][0-5][0-9]$'
P_ZTAB = u'(?m)^Zone' + TAB
P_ZSPC = u'(?m)^Zone '
P_RTAB = u'(?m)^Rule' + TAB
P_RSPC = u'(?m)^Rule '

# ---------- 表: 不看程序的独立复算 ----------
ZL = [l for l in LINES[0] if l[:1] != u'#' and l.strip()]
ZR = [l.split(TAB) for l in ZL]
C4 = [r for r in ZR if len(r) == 4]
C3 = [r for r in ZR if len(r) == 3]
COMMA = [r for r in ZR if len(r) > 3 and r[3].strip()]
BARE = [r for r in ZR if len(r) < 4 or not r[3].strip()]
FIRST = [r[0].split(u',')[0] for r in ZR]
EQ = len([i for i in range(1, len(FIRST)) if FIRST[i] == FIRST[i - 1]])
LESS = len([i for i in range(1, len(FIRST)) if FIRST[i] < FIRST[i - 1]])
GREAT = len([i for i in range(1, len(FIRST)) if FIRST[i] > FIRST[i - 1]])
NAIVE = len([i for i in range(1, len(ZR)) if ZR[i][0] < ZR[i - 1][0]])
EQTIE = len([i for i in range(1, len(ZR)) if ZR[i][0] < ZR[i - 1][0] and FIRST[i] == FIRST[i - 1]])
CCREF = [c for r in ZR for c in r[0].split(u',')]
USED = collections.Counter(CCREF)
CCD = len(set(CCREF))
ISOR = [l.split(TAB) for l in rd(RI).split(NL) if l[:1] != u'#' and l.strip()]
CCUNREF = len([x for x in ISOR if x[0] not in USED])
MULTI = [r for r in ZR if max(USED.get(c, 0) for c in r[0].split(u',')) > 1]
SLACK = len([r for r in COMMA if max(USED.get(c, 0) for c in r[0].split(u',')) <= 1])
VMISS = len([r for r in BARE if max(USED.get(c, 0) for c in r[0].split(u',')) > 1])
MINC = len([r for r in ZR if re.match(RXMIN, r[1])])
SECC = len([r for r in ZR if re.match(RXSEC, r[1])])
BADC = len(ZR) - MINC - SECC
DUPN = len(ZR) - len(set(r[2] for r in ZR))
NAMES = set(r[2] for r in ZR)
TABL = rd(RZT).split(NL)
TABROWS = len([l for l in TABL if l[:1] != u'#' and l.strip()])
SIMROW = [i for i, l in enumerate(TABL, 1) if u'Simferopol' in l and l[:1] != u'#'][0]
TNON = [(i, l.split(TAB)) for i, l in enumerate(TABL, 1) if l[:1] != u'#' and l.strip()]
SIMVIOL = [i for k in range(1, len(TNON)) for i, r in [TNON[k]]
           if r[0].split(u',')[0] < TNON[k - 1][1][0].split(u',')[0]
           and TNON[k - 1][1][2] == u'Europe/Simferopol'][0]

# ---------- 数据: 照程序的取列法 ----------
EL = [l.split() for l in LINES[2] if l.split() and l.split()[0][:1] != u'#']
IND = len([l for l in LINES[2] if l.strip() and l[:1] != u'#' and l.split()[0][:1] == u'#'])
HASH0 = len([l for l in LINES[2] if l[:1] == u'#'])
ZBLANK = NLINES[2] - DROP[2] - len(EL)
ZON = [t for t in EL if t[0] == u'Zone']
RUL = [t for t in EL if t[0] == u'Rule']
LNK = [t for t in EL if t[0] == u'Link']
CON = [t for t in EL if t[0] not in (u'Zone', u'Rule', u'Link')]
ZTAB = CNT(P_ZTAB, 2)
ZSPC = CNT(P_ZSPC, 2)
RTAB = CNT(P_RTAB, 2)
RSPC = CNT(P_RSPC, 2)
CONTAB = CNTF(P_CONT, 2)
SO = [t[2] for t in ZON if len(t) > 2] + [t[0] for t in CON]
RXSO = re.compile(u'^-?1?[0-9](:[0-5][0-9](:[0-5][0-9])?)?$')
SOBAD = len([s for s in SO if not RXSO.match(s)])
RDEF = set(t[1] for t in RUL)
LET = set(t[1] for t in RUL if len(t) >= 10 and t[9] != u'-')
USEC, PCTK = collections.Counter(), set()
for t in EL:
    if t[0] == u'Zone':
        if len(t) > 3:
            USEC[t[3]] += 1
        if len(t) > 4 and u'%' in t[4]:
            PCTK.add(t[3])
    elif t[0] != u'Rule' and t[0] != u'Link':
        if len(t) > 1:
            USEC[t[1]] += 1
        if len(t) > 2 and u'%' in t[2]:
            PCTK.add(t[1])
UNUSED = len([k for k in RDEF if USEC.get(k, 0) == 0])
ONCE = len([k for k in RDEF if USEC.get(k, 0) == 1])
PHANT = len([k for k in USEC if k not in RDEF])
LETNOP = len([k for k in LET if k not in PCTK])
MONSET = set(t[5] for t in RUL if len(t) > 5)
ZNAMES = set(t[1] for t in ZON)
ZMISS = len([n for n in ZNAMES if n not in NAMES])
GDEF, GUSE, GLET, GPCT, GMON = set(), set(), set(), set(), set()
for f in DATA:
    for l in rd(u'corpus/raw/tz/' + f).split(NL):
        t = l.split()
        if not t or t[0][:1] == u'#':
            continue
        if t[0] == u'Rule':
            GDEF.add(t[1])
            if len(t) >= 10 and t[9] != u'-':
                GLET.add(t[1])
            if len(t) > 5:
                GMON.add(t[5])
        elif t[0] != u'Link':
            if t[0] == u'Zone':
                if len(t) > 3:
                    GUSE.add(t[3])
                if len(t) > 4 and u'%' in t[4]:
                    GPCT.add(t[3])
            else:
                if len(t) > 1:
                    GUSE.add(t[1])
                if len(t) > 2 and u'%' in t[2]:
                    GPCT.add(t[1])
GUNUSED = len([k for k in GDEF if k not in GUSE])
GLETNOP = len([k for k in GLET if k not in GPCT])

# ---------- 程序内部 ----------
PR = CNT(P_PRINTF, 1)
ST = CNT(P_STATUS, 1)
RD_ = CNT(P_RED, 1)
STMTS = []
for m in re.finditer(u'(?m)^[ \t]*printf ', TXT[1]):
    j, frags = m.end(), []
    while True:
        while TXT[1][j] in u' \t' + BS + NL:
            j += 1
        if TXT[1][j] != u'"':
            break
        k = j + 1
        while TXT[1][k] != u'"':
            k += 2 if TXT[1][k] == BS else 1
        frags.append(TXT[1][j + 1:k])
        j = k + 1
    STMTS.append((u''.join(frags), u'/dev/stderr' in TXT[1][j:j + 120]))
FULLF = [s[0] for s in STMTS]
TEXTS = len(set(FULLF))
WLINE = len([f for f in FULLF if f.startswith(u'%s:%d')])
NOLINE = PR - WLINE
POUT = len([s for s in STMTS if not s[1]])
DUPW = [f for f, k in collections.Counter(FULLF).items() if k > 1]
FSN, GL, INR, ZNR = CNT(P_FS, 1), CNT(P_GETLINE, 1), CNT(P_INR, 1), CNT(P_ZNR, 1)
MONC = CNT(P_MON, 1)
D0, D1 = CNT(P_D0, 1), CNT(P_D1, 1)
ZTC, ZNC, BKC, SIMC, WANTC = CNT(P_ZT, 1), CNT(P_ZN, 1), CNT(P_BK, 1), CNT(P_SIM, 1), CNT(P_WANT, 1)
ESCT = CNT(P_ESC, 1)
PCTS, PCTDC = CNT(P_PCT, 1), CNT(P_PCTD, 1)
WNC = CNT(P_WNC, 1)
assert PR == len(STMTS) == len(FULLF)

# ---------- 词面交集 ----------
W = {}
for nm, pat in ((u'ifo', P_IFO), (u'utf', P_UTF), (u'stab', P_STAB), (u'sort', P_SORT),
                (u'popu', P_POPU), (u'geo', P_GEO)):
    W[nm] = (CNT(pat, 0), CNTF(pat, 0), CNT(pat, 1))
    assert W[nm][:2] == (0, 1) and W[nm][2] == 0 or nm == u'popu', (nm, W[nm])
assert W[u'popu'] == (0, 2, 0) and W[u'utf'] == (0, 1, 0)
assert CNT(P_OOO, 0) == 0 and CNT(P_INVC, 0) == 0 and CNT(P_NOZONE, 0) == 0
assert CNT(P_NODATA, 0) == 0 and CNT(P_WNC, 0) == 0 and CNT(P_DUPZ, 0) == 0
assert CNT(u'STDOFF', 0) == 0 and CNT(P_INVC, 1) == 1 and CNT(P_NOZONE, 1) == 1
assert CNT(P_DUPZ, 1) == 1 and CNT(P_NODATA, 1) == 1

print(u'体量 行 %s 被剔 %s 口径 %s 全文 %s 字节 %s 非ASCII %s/%s 制表 %s/%s' %
      (NLINES, DROP, [RCOT(i) for i in range(3)], FULL, BYTES, NASCII, NASCII_R, ITAB, ITAB_R))
print(u'表 %d 四列 %d 三列 %d 首码 %d/%d/%d 整列乱 %d 同首码 %d 坐标 %d/%d/%d 重名 %d'
      % (len(ZR), len(C4), len(C3), EQ, GREAT, LESS, NAIVE, EQTIE, MINC, SECC, BADC, DUPN))
print(u'引用 %d 去重 %d 码表 %d 未引用 %d 有注释 %d 无注释 %d 跨行 %d 缺 %d 余量 %d'
      % (len(CCREF), CCD, len(ISOR), CCUNREF, len(COMMA), len(BARE), len(MULTI), VMISS, SLACK))
print(u'europe 非注释 %d 缩进 %d 行首 %d 空行 %d Zone %d Rule %d Link %d 续行 %d STDOFF %d 不合 %d'
      % (len(EL), IND, HASH0, ZBLANK, len(ZON), len(RUL), len(LNK), len(CON), len(SO), SOBAD))
print(u'分隔符混用 Zone 行首 tab %d ⇎ 空格 %d｜Rule tab %d ⇎ 空格 %d｜行首 tab 线 %d = 续行 %d + 缩进注释 %d'
      % (ZTAB, ZSPC, RTAB, RSPC, CONTAB, len(CON), IND))
print(u'规则 定义 %d 未用 %d 一次 %d 字母 %d 字母无%% %d 幻影 %d 月 %d 全局 %d/%d/%d/%d 月 %d'
      % (len(RDEF), UNUSED, ONCE, len(LET), LETNOP, PHANT, len(MONSET),
         len(GDEF), GUNUSED, len(GLET), GLETNOP, len(GMON)))
print(u'zone.tab 行 %d Simferopol %d 违规 %d｜Zone 名不在表 %d' % (TABROWS, SIMROW, SIMVIOL, ZMISS))
print(u'程序 printf %d 文本 %d 重复 %s 带行号 %d 不带 %d stderr %d stdout %d status %d'
      % (PR, TEXTS, [d[:32] for d in DUPW], WLINE, NOLINE, RD_, POUT, ST))
print(u'程序 FS %d getline %d 计数 %d/%d 月表 %d 注释 %d/%d zt %d zn %d bk %d simf %d want %d 转义t %d %%s %d %%d %d'
      % (FSN, GL, INR, ZNR, MONC, D0, D1, ZTC, ZNC, BKC, SIMC, WANTC, ESCT, PCTS, PCTDC))

# ---------- 断言 ----------
assert (NLINES[0], NLINES[1], NLINES[2]) == (375, 228, 4212)
assert (DROP[0], DROP[1], DROP[2]) == (63, 7, 2897)
assert (RCOT(0), RCOT(1), RCOT(2)) == (14482, 4967, 40303)
assert FULL == [17536, 5377, 187806] and BYTES == [17592, 5377, 188472]
assert (NASCII[0], NASCII_R[0], NASCII[1], NASCII[2], NASCII_R[2]) == (38, 18, 0, 666, 2)
assert NASC_L == 2
assert (BYTES[0] - FULL[0], BYTES[1] - FULL[1], BYTES[2] - FULL[2]) == (56, 0, 666)
assert (ITAB[0], ITAB_R[0], ITAB[1], ITAB_R[1], ITAB[2], ITAB_R[2]) == (833, 825, 404, 394, 8346, 7402)
assert (len(ZL), len(ZR), len(C4), len(C3), len(COMMA), len(BARE)) == (312, 312, 201, 111, 201, 111)
assert ITAB_R[0] == 3 * len(C4) + 2 * len(C3) and ITAB[0] - ITAB_R[0] == 8
assert (EQ, GREAT, LESS, EQ + GREAT + LESS) == (158, 153, 0, 311)
assert (NAIVE, EQTIE) == (6, 6)
assert (MINC, SECC, BADC, DUPN) == (265, 47, 0, 0) and MINC + SECC == len(ZR)
assert (len(CCREF), CCD, len(ISOR), CCUNREF) == (423, 247, 249, 2)
assert (len(MULTI), VMISS, SLACK) == (201, 0, 0)
assert (len(EL), IND, HASH0, ZBLANK) == (1020, 7, 2890, 295)
assert NLINES[2] == len(EL) + IND + HASH0 + ZBLANK and DROP[2] == HASH0 + IND
assert (len(ZON), len(RUL), len(LNK), len(CON), len(SO), SOBAD) == (65, 515, 0, 440, 505, 0)
assert (ZTAB, ZSPC, RTAB, RSPC, CONTAB) == (29, 36, 503, 12, 447)
assert ZTAB + ZSPC == len(ZON) and RTAB + RSPC == len(RUL) and CONTAB == len(CON) + IND
assert (len(RDEF), UNUSED, ONCE, len(LET), LETNOP, PHANT, len(MONSET)) == (30, 0, 13, 29, 0, 3, 11)
assert u'Jan' not in MONSET and u'Jan' in GMON and len(GMON) == 12
assert (len(GDEF), GUNUSED, len(GLET), GLETNOP) == (135, 0, 103, 0)
assert ZMISS == 0 and (TABROWS, SIMROW, SIMVIOL) == (418, 336, 337)
assert (PR, TEXTS, WLINE, NOLINE, RD_, POUT, ST) == (18, 17, 15, 3, 14, 4, 17)
assert len(DUPW) == 1 and DUPW[0] == u'%s:%d: wrong number of columns\\n'
assert PR == RD_ + POUT and PR == WLINE + NOLINE and ST == PR - 1
assert (FSN, GL, INR, ZNR, MONC) == (2, 2, 1, 1, 12)
assert (D0, D1, ZTC, ZNC, BKC, SIMC, WANTC, ESCT) == (2, 1, 2, 3, 1, 1, 3, 1)
assert (PCTS, PCTDC, WNC) == (35, 16, 2)

# ---------- 助手值(与 audit.py 里 _b49_scan 同口径) ----------
HV = {u'rows': len(ZR), u'c4rows': len(C4), u'c3rows': len(C3), u'comrows': len(COMMA),
      u'barerows': len(BARE), u'multirows': len(MULTI), u'slack': SLACK, u'viol': VMISS,
      u'dupname': DUPN, u'eqfirst': EQ, u'gtfirst': GREAT, u'lessfirst': LESS, u'naive': NAIVE,
      u'eqtie': EQTIE, u'mincoord': MINC, u'seccoord': SECC, u'badcoord': BADC,
      u'ccref': len(CCREF), u'ccdistinct': CCD, u'isorows': len(ISOR), u'unref': CCUNREF,
      u'iso2': len([l for l in rd(RI).split(NL) if re.match(P_ISO2, l)]),
      u'itab': ITAB[0], u'itab_r': ITAB_R[0], u'itab_c': ITAB[1], u'itab_c_r': ITAB_R[1],
      u'itab_z': ITAB[2], u'itab_z_r': ITAB_R[2],
      u'el': len(EL), u'indented': IND, u'hash0': HASH0, u'blankz': ZBLANK,
      u'zone': len(ZON), u'rule': len(RUL), u'link': len(LNK), u'cont': len(CON),
      u'zone_tab': ZTAB, u'zone_sp': ZSPC, u'rule_tab': RTAB, u'rule_sp': RSPC,
      u'cont_tab': CONTAB,
      u'stdoff': len(SO), u'stdoff_bad': SOBAD, u'rdef': len(RDEF), u'runused': UNUSED,
      u'rletters': len(LET), u'rletnop': LETNOP, u'phantom': PHANT, u'once': ONCE,
      u'months_eu': len(MONSET), u'mondef': MONC, u'months_all': len(GMON),
      u'zone_missing': ZMISS, u'gdef': len(GDEF), u'gunused': GUNUSED, u'gletters': len(GLET),
      u'gletnop': GLETNOP, u'printf': PR, u'texts': TEXTS, u'wline': WLINE, u'noline': NOLINE,
      u'stderr': RD_, u'stdout': POUT, u'status': ST, u'wnc': WNC, u'fs': FSN, u'd0': D0,
      u'd1': D1, u'zt': ZTC, u'zn': ZNC, u'bk': BKC, u'simf': SIMC, u'want': WANTC,
      u'esc_t': ESCT, u'pcts': PCTS, u'pctd': PCTDC, u'inr': INR, u'znr': ZNR, u'gl': GL,
      u'tabrows': TABROWS, u'simrow': SIMROW, u'simviol': SIMVIOL, u'ndata': len(DATA),
      u'nascii_t': NASCII[0], u'nascii_t_r': NASCII_R[0], u'nascii_z': NASCII[2],
      u'nascii_z_r': NASCII_R[2], u'nascii_z_rows': NASC_L, u'threebyte': (BYTES[0] - FULL[0]) - NASCII[0],
      u'bytesgap_t': BYTES[0] - FULL[0], u't_full': FULL[0], u'c_full': FULL[1], u'z_full': FULL[2]}

# ---------- 锚点 ----------
AN, LBL = {}, {}


def pick(txt, needle, key, color, cnt=1):
    hits = [l for l in txt.split(NL) if needle in l]
    assert len(hits) == cnt, (key, needle, len(hits))
    lit = hits[0]
    assert txt.count(lit) == cnt, (key, len(lit), txt.count(lit))
    assert 8 <= len(lit) <= 460, (key, len(lit))
    AN[key], LBL[key] = lit, color


pick(TXT[0], u'Columns are separated by', u't_sep', LT)
pick(TXT[0], u'present if and only if', u't_iff', LT)
pick(TXT[0], u'The table is sorted', u't_sort', LT)
pick(TXT[0], u'most-populous city is used', u't_popu', LT)
pick(TXT[0], u'ISO 6709 sign-degrees-minutes-seconds', u't_coord', LT)
pick(TXT[0], u'All text uses', u't_utf', LT)
pick(TXT[0], u'#codes', u't_cols', LT)
pick(TXT[0], u'Europe/Andorra', u't_ad', LT)
pick(TXT[0], u'Antarctica/Mawson', u't_aq', LT)
pick(TXT[0], u'Antarctica/Troll', u't_troll', LT)
pick(TXT[0], u'Asia/Dubai', u't_dubai', LT)
pick(TXT[0], u'CH,DE,LI' + TAB + u'+4723', u't_ch', LT)
pick(TXT[0], u'Africa/Johannesburg', u't_last', LT)
pick(TXT[1], u'Check tz tables', u'c_title', LC)
pick(TXT[1], u'FS = "' + BS + u't"', u'c_fs_tab', LC)
pick(TXT[1], u'FS = " "', u'c_fs_sp', LC)
pick(TXT[1], u'if (cc < cc0', u'c_lt', LC)
pick(TXT[1], u'if (cc <= cc0)', u'c_le', LC)
pick(TXT[1], u'used_max <= 1 && comments', u'c_unneed', LC)
pick(TXT[1], u'missing comment for', u'c_miss', LC)
pick(TXT[1], u'NF != 3 && NF != 4', u'c_wnc', LC)
pick(TXT[1], u'unknown country code', u'c_unknownc', LC)
pick(TXT[1], u'invalid coordinates', u'c_invc', LC)
pick(TXT[1], u'unlikely STDOFF', u'c_stdoff', LC)
pick(TXT[1], u'tricky month', u'c_tricky', LC)
pick(TXT[1], u'no data for', u'c_nodata', LC)
pick(TXT[1], u'no Zone table for', u'c_nozone', LC)
pick(TXT[1], u'duplicate Zone from line', u'c_dupz', LC)
pick(TXT[1], u'Rule never used', u'c_never', LC)
pick(TXT[1], u'Rule contains letters never used', u'c_letters', LC)
pick(TXT[1], u'no Zone entries for', u'c_warn', LC)
pick(TXT[1], u'Europe/Simferopol', u'c_simf', LC)
pick(TXT[1], u'special case for Crimea', u'c_crim', LC)
pick(TXT[1], u'while (getline <iso_table)', u'c_gi', LC)
pick(TXT[1], u'while (getline <zone_table)', u'c_gz', LC)
pick(TXT[1], u'tz2NR[tz] = zone_NR', u'c_tz2nr', LC)
pick(TXT[1], u'monthabbr["Jan"]', u'c_jan', LC)
pick(TXT[1], u'$1 ~ /^#/', u'c_d1', LC)
pick(TXT[1], u'$0 ~ /^#/', u'c_d0', LC, 2)
pick(TXT[1], u'exit status', u'c_exit', LC)
pick(TXT[1], u'want_warnings = -1', u'c_want', LC)
pick(TXT[1], u'if (tz && tz', u'c_both', LC)
pick(TXT[1], u'FILENAME != "backward"', u'c_back', LC)
pick(TXT[2], u'Zone' + TAB + u'Europe/London', u'z_london', LZ)
pick(TXT[2], u'Zone' + TAB + u'Europe/Tirane', u'z_tirane', LZ)
pick(TXT[2], u'Rule' + TAB + u'Eire' + TAB + u'1971', u'z_eire', LZ)
pick(TXT[2], u'Rule' + TAB + u'Albania' + TAB + u'1940', u'z_albania', LZ)
pick(TXT[2], u'EET' + TAB + u'2001 Jan', u'z_jan', LZ)
pick(TXT[2], u'Zone' + TAB + u'Europe/Athens', u'z_athens', LZ)
pick(TXT[2], u'# T' + u'\u00f3' + u'rshavn', u'z_faroe', LZ)
pick(TXT[2], u'Rule SovietZone' + TAB + u'1945' + TAB + u'only' + TAB + u'-' + TAB + u'May', u'z_soviet', LZ)
for k, v in AN.items():
    assert v in ([TXT[0], TXT[1], TXT[2]][{LT: 0, LC: 1, LZ: 2}[LBL[k]]]), (k, v[:40])
ANCH, UANCH = len(AN), len(set(AN.values()))
NT_AN = len([k for k, x in LBL.items() if x == LT])
NC_AN = len([k for k, x in LBL.items() if x == LC])
NZ_AN = ANCH - NT_AN - NC_AN
print(u'anchors=%d uniq=%d T=%d C=%d Z=%d' % (ANCH, UANCH, NT_AN, NC_AN, NZ_AN))
assert (ANCH, UANCH, NT_AN, NC_AN, NZ_AN) == (51, 51, 13, 30, 8)

# ---------- 判词 ----------
G = []


def A(head, items, gloss, *args):
    # 格式在调用点完成: 参数与占位符不符时 % 运算符自己抛 TypeError, 这里只保证没有第三种形态
    assert not args, (head, len(args))
    G.append(u'%s %s ⇒ %s' % (head, u' ‖ '.join([u'⟦%s⟧⟨%s⟩' % (LBL[k], AN[k]) for k in items]),
                              gloss))


A(u'🧭 体例', [u't_cols', u'c_exit', u'z_london'],
  u'三个源不是同一条链上的三站, 而是同一件事的三个角色: 表 ⟦%s⟧⟨%s⟩(%d 行数据: 带注释 %d ⇎ 不带注释 %d, '
  u'即四列 ⇎ 三列两种形状) ⇎ 检查器 ⟦%s⟧⟨%s⟩(%d 行 awk, %d 条 printf, 拼全续行后 %d 种诊断文本) ⇎ '
  u'被它检查的数据 ⟦%s⟧⟨%s⟩(%d 行 = 行首注释 %d ⇎ 缩进注释 %d ⇎ 空行 %d ⇎ 非注释 %d, 其中 Zone %d ⇎ Rule %d ⇎ 续行 %d ⇎ Link %d)。'
  u'与上一条“输入 ⇎ 程序 ⇎ 产物”不同: 这里的程序**不产出文件**, 它的唯一输出是判决, 而判决的正常形态是空——'
  u'干净运行 exit 0 且两条流各 0 字节(命令、版本与逐条破坏的输出写在 ⛓解读注, 属工具侧断言)。'
  u'于是可核性又长出一环: 记号可数 ⇎ 展开复算 ⇎ 执行复现 ⇎ **反向对照**(原料逐字节复制进临时目录, '
  u'既破坏数据也破坏程序, 看它精确报出哪一行、走哪条流)。审计口径从三份原料各剔注释 %d ⇎ %d ⇎ %d 行, '
  u'口径内留 %d ⇎ %d ⇎ %d 字符(数据侧那个“缩进注释 %d”与检查器被剔的 %d 行同数, 是巧合不是同一件事)。'
  % (LT, AN[u't_cols'], len(ZR), len(COMMA), len(BARE), LC, AN[u'c_exit'], NLINES[1], PR, TEXTS,
     LZ, AN[u'z_london'], NLINES[2], HASH0, IND, ZBLANK, len(EL), len(ZON), len(RUL), len(CON), len(LNK),
     DROP[0], DROP[1], DROP[2], RCOT(0), RCOT(1), RCOT(2), IND, DROP[1]))

A(u'✂️ 表把语法写在被口径剔掉的那 ' + str(DROP[0]) + u' 行里',
  [u't_sep', u't_iff', u't_sort', u'c_le'],
  u'表的注释把自己的写法讲得很清楚: ⟦%s⟧⟨%s⟩(列用单个制表符分隔) ⇎ ⟦%s⟧⟨%s⟩(第 4 列“当且仅当”) ⇎ '
  u'⟦%s⟧⟨%s⟩(按国家码排序) ⇎ ⟦%s⟧⟨%s⟩(取最大城市)。这些句子在**审计口径里全是 0**, 在全文里各 1 处'
  u'(“populous” 那组 2 处); 而程序里它们的字面也全是 0——程序不引用表的散文, 它另写一套: '
  u'制表符写成真制表符(全文件 %d 枚, 口径 %d 枚), “当且仅当”拆成两条支路 ⟦%s⟧⟨%s⟩ 与 ⟦%s⟧⟨%s⟩, '
  u'排序只剩一个比较符 ⟦%s⟧⟨%s⟩。'
  u'反方向也空: 拼全后的 %d 种诊断文本没有一个字面出现在表的口径里; 只有 ⟦%s⟧⟨%s⟩ 这种通用句在程序里写了 %d 遍'
  u'(两条循环各一遍)——它正是“文本 %d 种 ⇎ 发射点 %d 个”那 %d 之差的全部来源。'
  u'判词: 一份表有两种规格——散文版给人读, 运算符版给机器执行, 两者用词互不见; '
  u'要证明“程序真的照散文检查”, 搜词一行也证不了, 只能复算或破坏。'
  % (LT, AN[u't_sep'], LT, AN[u't_iff'], LT, AN[u't_sort'], LT, AN[u't_popu'],
     ITAB[1], ITAB_R[1], LC, AN[u'c_unneed'], LC, AN[u'c_miss'], LC, AN[u'c_le'],
     TEXTS, LC, AN[u'c_wnc'], WNC, TEXTS, PR, PR - TEXTS))

A(u'📐 排序的宽容住在一枚比较符里', [u't_aq', u't_dubai', u'c_lt', u'c_le'],
  u'程序对“排好序”的要求只有这么多: ⟦%s⟧⟨%s⟩ —— 取每行**第一个**国家码, 只报“比上一行小”。'
  u'在这份表上相邻首码是 相等 %d ⇎ 变大 %d ⇎ 变小 %d(%d 行给出 %d 个相邻对, 三数之和的等式在 0 键)。'
  u'整列字面比较却有 %d 处“乱序”: 例如 ⟦%s⟧⟨%s⟩ 排在 ⟦%s⟧⟨%s⟩ 之后——首码同为 AQ, 整列字面反而小; '
  u'这 %d 处的首码无一例外全部相等(两个数在 0 键相等), 所以程序一行也没报。'
  u'散文还写着后半句(国家内部按人口与地理), 那半句在程序里没有任何诊断文本接待。'
  u'同一个程序紧挨着的另一条循环写的是 ⟦%s⟧⟨%s⟩: 码表侧不许相等(相等即 duplicate), 表侧允许。'
  u'两枚比较符谁也不能换成对方, 只能做实验量(工具侧): 把表侧的 < 改成 <=, 干净库当场报 %d 行——'
  u'恰是那 %d 对相等首码; 把码表侧的 <= 改成 <, 一行不报(码表本无重复码)。'
  u'判词: “这张表排好序了”至少有两种读数(首码非降 ⇎ 整列升序), 程序实现的是较弱那种; '
  u'较弱那种正是散文里“国家内部次序”自由度的容身之处——**运算符的必要性是数据的性质, 不是代码的性质**。'
  % (LC, AN[u'c_lt'], EQ, GREAT, LESS, len(ZR), len(ZR) - 1, NAIVE,
     LT, AN[u't_aq'], LT, AN[u't_dubai'], NAIVE, LC, AN[u'c_le'], EQ, EQ))

A(u'🔗 第 4 列是引用数的函数, 而且贴边无余量', [u't_ch', u't_last', u'c_unneed', u'c_miss'],
  u'散文 ⟦%s⟧⟨%s⟩ 说第 4 列“当且仅当国家有多时区时才出现”; 程序把它拆成两条: '
  u'⟦%s⟧⟨%s⟩(该无而有 ⇒ unnecessary) 与 ⟦%s⟧⟨%s⟩(该有而无 ⇒ missing), 判据是“本行某个码被几行引用”。'
  u'不看程序独立复算: 国家码共被引用 %d 次、去重 %d 种, 码表 %d 行里未被任何表行引用的 %d 种; '
  u'至少一个码跨多行的行 %d ⇎ 带注释的行 %d ⇎ 无注释的行 %d, 两个方向的违规各 %d ⇎ %d; '
  u'更狠的是**余量** %d —— 带注释而引用数不足的行数为 0, 即这条不变量在真数据上是贴边的, '
  u'“unnecessary” 那一支在整份库上从未被走到, 只有凭空给 ⟦%s⟧⟨%s⟩ 那样的行加一枚注释它才开口(注里有那次运行)。'
  u'跨行引用与注释还差一层: 程序要**读完整个表循环**才知道引用数, 于是这段判断写在循环之外, 用 '
  u'input_ccs / input_comments 两张数组整表回填, 行号取自自建的 zone_NR 而不是文件行号。'
  u'判词: iff 型不变量要报三件事——两边各几枚违规、单侧余量几行、以及实现它需要多少事后状态; '
  u'只报“%d ⇎ %d 相等”会把“贴边”与“宽松”混为一谈。'
  % (LT, AN[u't_iff'], LC, AN[u'c_unneed'], LC, AN[u'c_miss'],
     len(CCREF), CCD, len(ISOR), CCUNREF, len(MULTI), len(COMMA), len(BARE), VMISS, SLACK, SLACK,
     LT, AN[u't_last'], len(COMMA), len(MULTI)))

A(u'🗂 发射点、文本种数与流向是三套账', [u'c_dupz', u'c_nodata', u'c_never', u'c_tz2nr'],
  u'%d 条 printf 分三层数: 拼全相邻字面量后是 %d 种文本(差的 %d 条就是 ⟦%s⟧⟨%s⟩, 两条循环各写一遍); '
  u'按流分 ⟦%s⟧⟨%s⟩ 那 %d 条 ⇎ 直接进 stdout 的 %d 条; 按失败码分 %d 条写 status = 1 ⇎ %d 条不写。'
  u'“错”与“走哪条流”因此无关: 原地复制一行表(工具侧) ⇒ 失败码 1、stderr 0 行、stdout 1 行, '
  u'那句是 ⟦%s⟧⟨%s⟩ ——只读 stderr 的调用方会看见“毫无诊断却失败”。'
  u'定位符分两种宽度: %d 条带“表名:行号” ⇎ %d 条只带名字(⟦%s⟧⟨%s⟩ 与 END 的 ⟦%s⟧⟨%s⟩); '
  u'前者里数据侧错误用 FILENAME/FNR(⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩), 表侧用自建 zone_NR, '
  u'还有一支在 END 里回查 ⟦%s⟧⟨%s⟩ 才凑出行号, 码表侧同构地用 cc2NR。'
  u'判词: “程序说了什么”按文本种数记账, “怎么找到说话对象”按定位符宽度记账, “送到哪里”按流记账; '
  u'三套账混成一套就会得出“错误都到 stderr”这种错话。'
  % (PR, TEXTS, PR - TEXTS, LC, AN[u'c_wnc'], LC, AN[u'c_nodata'], RD_, POUT, ST, PR - ST,
     LC, AN[u'c_dupz'], WLINE, NOLINE, LC, AN[u'c_nodata'], LC, AN[u'c_never'],
     LC, AN[u'c_tricky'], LC, AN[u'c_stdoff'], LC, AN[u'c_tz2nr']))

A(u'🧪 一条不变量一枚诊断: 破坏分三档', [u'c_invc', u'c_stdoff', u'c_tricky', u't_troll'],
  u'把 %d 种诊断文本当作不变量的枚举, 每种各造一次破坏(破坏串一律取自真实行, 原料逐字节复制进临时目录), '
  u'结果按三档分: **局部形状类**一触一报——秒形式坐标 ⟦%s⟧⟨%s⟩ 那种(表里 %d 行用秒形式 ⇎ %d 行用分形式 ⇎ 不合式 0 行)'
  u'里插一位、表的第 4 列加一枚野注释、码表某行多一列, 各报一行 ⟦%s⟧⟨%s⟩ 型; '
  u'STDOFF 改坏报的是**数据文件**的行号(本文件受检的 STDOFF 值 %d 个全部合式, 见 ⟦%s⟧⟨%s⟩); '
  u'月列改成非月名 ⇒ ⟦%s⟧⟨%s⟩。'
  u'**关系类**会级联: 把一个码换成不存在的 QQ, 除了 ⟦%s⟧⟨%s⟩ 还连带把下一行挤成乱序; '
  u'把码表首字母改小写同时触发码形与排序两条。'
  u'**全局聚合类**要挑对下手点(见下条)。还原之后重新运行仍是两条流各 0 字节——电池没留下痕迹。'
  u'判词: 诊断行数与破坏大小不成比例, “报了几行”不能当严重度, 必须按不变量的类型分列报告; '
  u'而“哪些形状根本没被检查”要反过来问: 表 %d 行里四列 %d ⇎ 三列 %d, 列数只被允许这两种, '
  u'第五种形状在程序里没有文本接待它。'
  % (TEXTS, LC, AN[u'c_invc'], SECC, MINC, LC, AN[u'c_wnc'], len(SO), LZ, AN[u'z_athens'],
     LC, AN[u'c_tricky'], LC, AN[u'c_unknownc'], len(ZR), len(C4), len(C3)))

A(u'📏 聚合型不变量的可破坏点是“最后一根支持者”', [u'z_albania', u'z_eire', u'c_letters', u'c_never'],
  u'END 的三条支路按**名字**聚合: 十份数据共定义规则名 %d 种, 全部被用到(定义未用 %d 种); '
  u'带字母的 %d 种全部有带 %% 的用法(字母而无 %% 者 %d 种; 定义与带字母之差 %d 枚就是不带字母的规则名)。'
  u'本文件单看: 定义 %d 种 ⇎ 带字母 %d 种 ⇎ 恰被用一次 %d 种, 其中不带字母的只有一个, 就是 ⟦%s⟧⟨%s⟩ 那一族。'
  u'我第一次破坏选的是定义行: 把某条 Rule 的字母列改成别的字母 ⇒ 不报错, 因为同名规则的另一行早已把字母登记进 '
  u'ruleLetters, 聚合表看不出差别——**破坏一个聚合不变量不能改它的任意一支支持者**。'
  u'正确的点是它唯一那次用法: ⟦%s⟧⟨%s⟩ 这类行的格式列里 %%s 换成普通串 ⇒ stdout 一行 ⟦%s⟧⟨%s⟩; '
  u'再把一个恰用一次且不带字母的名字换成 - ⇒ ⟦%s⟧⟨%s⟩, 两条都只报名字不报行号。'
  u'顺带: 程序把**每一行续行**的第 2 列都当规则名登记, 于是 ruleUsed 里混进 %d 枚从未定义过的幻影键'
  u'(本文件续行 %d 行, 大多是年份或 -); 这不是 bug, 因为 END 只遍历 ruleDefined ——'
  u'“幻影键无害”依赖另一条不变量, 这层依赖只在读代码时才看得见。'
  u'判词: 行级编辑与名级聚合之间隔着一张哈希表; 逐行读原文与搜词都找不到“谁是最后一根支持者”, 只能把聚合关系复算出来。'
  % (len(GDEF), GUNUSED, len(GLET), GLETNOP, len(GDEF) - len(GLET), len(RDEF), len(LET), ONCE,
     LZ, AN[u'z_eire'], LZ, AN[u'z_albania'], LC, AN[u'c_letters'], LC, AN[u'c_never'],
     PHANT, len(CON)))

A(u'🫥 程序替另外两张表写着豁免, 而它们在当前配置下是死的', [u'c_simf', u'c_back', u'c_both', u't_dubai'],
  u'程序里点名了别的表: ⟦%s⟧⟨%s⟩ 型判断 %d 处(zone.tab 的 Crimea 特例与 Link 支)、zonenow.tab %d 处'
  u'(XX 码豁免、注释规则豁免、zoneSeen 豁免)、⟦%s⟧⟨%s⟩ %d 处、特例名 ⟦%s⟧⟨%s⟩ %d 处。'
  u'三张表都真跑过(工具侧): 配 zone1970.tab ⇎ zone.tab ⇎ zonenow.tab 的基线**各**是两条流 0 字节; '
  u'把特例字符串改坏并以 zone.tab 运行 ⇒ 恰好 1 行, 报在第 %d 行, 而 ⟦%s⟧⟨%s⟩ 那行住在第 %d 行——'
  u'豁免写在**前一行**身上, 报的是**后一行**(RU 排在 UA 之后, 全表 %d 行仅此一处需要它); '
  u'把 ⟦%s⟧⟨%s⟩ 的豁免改坏 ⇒ 0 行, 因为在 zone1970 配置下 Link 支整条不执行(它自己也被 zone.tab 守卫): '
  u'本文件的 Link 行 %d 处, 于是这条支路在两个层面上都是死的。'
  u'更狠的一枚: ⟦%s⟧⟨%s⟩ 那条件同时守着数据→表与表→数据两个方向, 把它改坏后 zoneSeen 不再登记, '
  u'END 对表里全部 %d 个名字各报一次 ⟦%s⟧⟨%s⟩, 而“no data for”同时归零——一条条件, 一灭整个方向。'
  u'判词: 死支要按**当前调用配置**说, 不能按文件全局说; 一条豁免的价值等于它救下的行数, '
  u'而这个数只能执行出来, 读代码只会得到“这里有特例”而不知其权重。'
  % (LC, AN[u'c_simf'], ZTC, ZNC, LC, AN[u'c_back'], BKC, LC, AN[u'c_simf'], SIMC,
     SIMVIOL, LT, AN[u't_dubai'], SIMROW, TABROWS, LC, AN[u'c_back'], len(LNK),
     LC, AN[u'c_both'], len(ZR), LC, AN[u'c_nozone']))

A(u'🔀 两次 FS 切换、注释的三种口径与数据的两种分隔符', [u'c_fs_tab', u'c_fs_sp', u'c_d1', u'z_jan'],
  u'程序里有 %d 次 FS 赋值: BEGIN 开头 ⟦%s⟧⟨%s⟩, BEGIN 结尾 ⟦%s⟧⟨%s⟩。两张表用 '
  u'⟦%s⟧⟨%s⟩ ⇎ ⟦%s⟧⟨%s⟩ 在循环外读入, 并自建计数器(%d 处 ⇎ %d 处)——因为 NR 要留给 %d 份数据文件。'
  u'切换的后果是 NF 的含义翻面: 表侧 NF 是形状不变量(%d 行四列 ⇎ %d 行三列, 口径内制表符 %d 枚 = %d×3+%d×2), '
  u'数据侧 NF 毫无意义——行尾注释也是字段; 而“空白成串即一列”的劈法给了数据写法自由度: '
  u'本文件 %d 个 Zone 行里 %d 个用制表符分开首两列 ⇎ %d 个用空格, %d 个 Rule 行是 %d ⇎ %d(⟦%s⟧⟨%s⟩ 那行就用空格), '
  u'把这些行挪到表侧的 FS 下立刻不满足 ⟦%s⟧⟨%s⟩; 行首带制表符的线共 %d 条 = 续行 %d + 缩进注释 %d。'
  u'注释的定义也不止一种: 表循环用 ⟦%s⟧⟨%s⟩ 那种整行行首式 %d 处(同一条语句在两处逐字重复), 主规则用 ⟦%s⟧⟨%s⟩ 第一列式 %d 处; '
  u'本文件里以制表符缩进再以 # 开头的注释恰好 %d 行——按第一列它们仍是注释, 按行首它们不是。'
  u'我第一版复算就按行首过滤, 得到 %d 行非注释 ⇎ 照程序的定义 %d 行, 差的正是这 %d 行; '
  u'而审计口径(去掉前导空白再匹配)与程序一致: 剔除 %d = 行首 %d + 缩进 %d。'
  u'顺带一枚同名不同命: 程序的月表 ⟦%s⟧⟨%s⟩ 定 %d 个名字, 本文件的 Rule 行只用 %d 个(缺 Jan), '
  u'十份数据合起来才用满 %d 个——而 ⟦%s⟧⟨%s⟩ 那种 Jan 坐在续行的 until 段里(续行的第 4 列起才是日期), '
  u'程序只对 Rule 行的第 6 列查月名, 于是那一次也没被看过。'
  u'判词: 同一份数据在不同 FS 下是两种文本; “注释行”有三种彼此不同的口径, 复算前必须选定一种并写明, '
  u'否则 %d 与 %d 都会“正确”, 只是不在同一件事上正确。'
  % (FSN, LC, AN[u'c_fs_tab'], LC, AN[u'c_fs_sp'], LC, AN[u'c_gi'], LC, AN[u'c_gz'], INR, ZNR, len(DATA),
     len(C4), len(C3), ITAB_R[0], len(C4), len(C3),
     len(ZON), ZTAB, ZSPC, len(RUL), RTAB, RSPC, LZ, AN[u'z_soviet'], LC, AN[u'c_wnc'],
     CONTAB, len(CON), IND,
     LC, AN[u'c_d0'], D0, LC, AN[u'c_d1'], D1, IND,
     len(EL) + IND, len(EL), IND, DROP[2], HASH0, IND,
     LC, AN[u'c_jan'], MONC, len(MONSET), len(GMON), LZ, AN[u'z_jan'],
     len(EL) + IND, len(EL)))

A(u'🌐 字符 ⇎ 字节 ⇎ 口径: 三层各有各的差', [u't_utf', u'c_want', u't_cols'],
  u'表的散文 ⟦%s⟧⟨%s⟩ 声明“全部文本用 UTF-8”, 而程序对此 0 处校核(“UTF” 在程序内 0 处)。'
  u'字节层能核: 检查器 %d 字符 ⇎ %d 字节(纯 ASCII, 两层相等); 表 %d 字符 ⇎ %d 字节, 差 %d, '
  u'而全文非 ASCII 字符 %d 枚 ⇒ 差不等于枚数, 因为里面混着三字节排版符: 设双字节 x 枚、三字节 y 枚, '
  u'x+y=%d ⇎ x+2y=%d ⇒ y 由这两数相减得出(等式在 0 键); 数据 %d 字符 ⇎ %d 字节差 %d 而它恰有非 ASCII %d 枚 '
  u'⇒ 每枚多 1 字节, 全为双字节。'
  u'同一批字符再切一层: 表的非 ASCII 口径内只剩 %d(其余住在注释里), 数据剩 %d 枚、只住在 %d 行的**行尾**注释里'
  u'(⟦%s⟧⟨%s⟩ 那两行的地名带 ó 与 å)——搜“人名里的重音字母”在口径内几乎搜不到, 而它正是这份语料被采集的理由'
  u'(口径内那两个数各与别的量巧合同值, 是三回事)。'
  u'转义层照例要点名: 程序里真制表符 %d 枚(缩用) ⇎ 口径 %d 枚 ⇎ 字面反斜杠 t 仅 1 枚(就是 ⟦%s⟧⟨%s⟩ 那一行); '
  u'格式符 %%s %d 枚 ⇎ %%d %d 枚, 报文文本都靠它们拼装。'
  u'判词: “同一份文件”至少有三层长度(口径 ⇎ 全文字符 ⇎ 磁盘字节), 每层的差各有各的成因(注释 ⇎ 编码宽度); '
  u'报数时哪一层要写出来, 否则 %d 与 %d 会看着像同一种东西。'
  % (LT, AN[u't_utf'], BYTES[1], FULL[1], FULL[0], BYTES[0], BYTES[0] - FULL[0],
     NASCII[0], NASCII[0], BYTES[0] - FULL[0], FULL[2], BYTES[2], BYTES[2] - FULL[2], NASCII[2],
     NASCII_R[0], NASCII_R[2], NASC_L, LZ, AN[u'z_faroe'], ITAB[1], ITAB_R[1], LC, AN[u'c_fs_tab'], PCTS, PCTDC,
     NASCII[2], BYTES[0] - FULL[0]))

A(u'⚖ 告警是唯一不置失败码的输出, 而其默认值让整条支路死掉', [u'c_warn', u'c_want', u't_ad'],
  u'%d 条发射里只有 ⟦%s⟧⟨%s⟩ 不写 status = 1(其余 %d 条都写), 它也就不参与 ⟦%s⟧⟨%s⟩。'
  u'把开关打开(want_warnings=1)后运行仍 exit 0, 只是 stdout 多 %d 行——'
  u'内容恰好是“码表里没被任何表行引用的码”: 独立复算 %d 枚, 与程序输出的行数相等(等式在 0 键; '
  u'其中一枚的表行形如 ⟦%s⟧⟨%s⟩ 那样的多码行才把 BV 之外的码带进引用数)。'
  u'而默认值 ⟦%s⟧⟨%s⟩ 让整条支路在常规调用里 0 行: 同一个变量在程序里出现 %d 次(缺省赋值、判断、循环各一)。'
  u'更深一层: 告警的行号来自 cc2NR[cc] —— 那是码表循环结束时替每枚码记住的行号, '
  u'而 END 里遍历的是 `for (cc in cc2name)`: 哈希序, 于是两行告警的先后不保证与文件序一致(逐字节比较时要把这两行排序)。'
  u'判词: 程序把“规矩”分成两级——违反即失败 ⇎ 只是提示, 而提示级默认关闭; '
  u'“码表里有整行没人引用”正住在提示级, 所以只跑默认配置的读者会以为码表 %d 行全都被用上了。'
  % (PR, LC, AN[u'c_warn'], ST, LC, AN[u'c_exit'], CCUNREF, CCUNREF, LT, AN[u't_ch'],
     LC, AN[u'c_want'], WANTC, len(ISOR)))

A(u'∴ 骨架', [u'c_exit', u't_iff', u'c_lt', u'z_london'],
  u'① 检查器的产物是**空**: 干净运行两条流各 0 字节、exit 0, 所以它的“正确输出”没有正面证据, 只能靠反向对照取证; '
  u'② 表的语法有散文版与运算符版两套(全文 1 处 ⇎ 口径 0 处 ⇎ 程序内 0 处), 用词交集为空; '
  u'③ 排序读数有两层(首码非降 %d+%d ⇎ 整列升序还多出 %d 处), 程序实现较弱那层; '
  u'④ iff 型不变量要报违规数与**余量**(此处两个方向与余量皆 0), 贴边的真分支在只读数据的审计里隐形; '
  u'⑤ 报文三套账: 文本种数 %d ⇎ 发射点 %d ⇎ 流向 %d/%d, 错误可以走 stdout; '
  u'⑥ 定位符两种宽度 %d/%d, 同一句“列数不对”在两条循环里各写一次, 而“no data for”丢弃了行号; '
  u'⑦ 豁免按调用配置分死活(zone.tab 特例值 1 行 ⇎ backward 特例值 0 行), 一条条件可同时守两个方向(坏之则 %d 行齐发); '
  u'⑧ 聚合型不变量只能破坏“最后一根支持者”(名而无行号), 且其无害性依赖另一条不变量(幻影键 %d 枚); '
  u'⑨ FS 换两次 ⇒ NF 的含义翻面, 注释行三种口径差 %d 行; '
  u'⑩ 字符/字节/口径三层, 差各有成因(%d ⇎ %d 的成因不同); '
  u'⑪ 提示级默认关(%d 枚未引用码), 只跑默认配置会把提示级的账整个漏掉。'
  u'判词: “表 ⇎ 检查表的程序”之间没有生成关系, 只有**定义权**: 哪一列合法、什么算有序、注释该不该在, '
  u'全由那 %d 行里的 %d 枚 ⟦%s⟧⟨%s⟩ 与几枚比较符决定; 报告它们必须同时报“代码写了什么 ⇎ 数据满足到什么程度”。'
  % (EQ, GREAT, NAIVE, TEXTS, PR, RD_, POUT, WLINE, NOLINE, len(ZR), PHANT, IND,
     NASCII[2], BYTES[0] - FULL[0], CCUNREF, NLINES[1], TEXTS, LC, AN[u'c_dupz']))

A(u'ℒ 方法', [u't_sep', u'c_le', u'c_dupz', u'z_tirane'],
  u'读“表 ⇎ 检查这张表的程序 ⇎ 它检查的数据”: 第一步**先跑**, 不要先读——干净运行的 0 字节确立了基准, '
  u'此后每个数都是相对基准的偏离; 第二步把程序的发射点列成三套账(文本种数 %d / 发射点 %d / 流向 %d+%d), '
  u'“%d 种诊断文本”就是不变量的枚举, 比读控制流可靠; '
  u'第三步为每种不变量造一次破坏, 破坏串一律从真实行里取, 并按“局部 ⇎ 关系 ⇎ 全局聚合”分档记录它报几行、报哪一行、走哪条流; '
  u'第四步反过来破坏**程序**: 换一枚比较符、改一个字符串字面量、坏掉一条守卫条件, 数报文行数——'
  u'这一步量出的是“数据对代码的容忍度”(相等首码 %d 对 ⇎ 改符后报 %d 行, 同一个数在 raw 侧与执行侧各得一遍) '
  u'与“每条豁免的权重”(1 行 ⇎ 0 行); '
  u'第五步所有形状数(行数列数、引用数、坐标两型、STDOFF 受检值)一律在**不看程序**的情况下复算, '
  u'再与程序的红绿灯对照, 差集就是散文与代码的分歧处。'
  u'核验口径: ⟦%s⟧⟨%s⟩ 一类表内散文按“全文”数(口径为 0), ⟦%s⟧⟨%s⟩ 一类程序记号按口径数, '
  u'⟦%s⟧⟨%s⟩ 一类数据记号要注意缩进注释那 %d 行(与审计口径的剔法一致, 与“行首字符”的剔法差 %d)。'
  % (TEXTS, PR, RD_, POUT, TEXTS, EQ, EQ, LT, AN[u't_sep'], LC, AN[u'c_le'], LC, AN[u'c_dupz'], IND, IND))

A(u'✂️ 为什么这份编码比摘要窗口长', [u'c_title', u't_cols', u'z_soviet'],
  u'三份原料的口径长度是 %d ⇎ %d ⇎ %d 字符: 检查器最小(%d 行), 却独家持有全部 %d 种诊断文本与两枚比较符; '
  u'表与数据都很大, 而它们**说出规矩**的部分恰是审计口径剔掉的注释行(%d 行 ⇎ %d 行)。'
  u'摘要段只能取锚点触到的窗口 ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩, 但本条的结论不住在窗口里: '
  u'“%d 对相等首码恰好被 < 放过”“注释与引用两个方向各 0 违规且余量 0”“一条守卫条件同时决定两个方向的 %d 行”, '
  u'这些要么要复算, 要么要执行, 要么要破坏。读它请按“四种可核性各占几项”来读, 而不是按“少说了多少原文”。'
  u'与上一条同为 tz 材料而不同题: 那条比同一时刻上的三个角色(输入/程序/产物, 程序**产出字节**), '
  u'本条比同一份表上的**定义权归属**(程序只产出判决); 与本库另一条比同一名字在不同载体里的形态也不同——'
  u'这里没有名字的形状, 只有形状的合法性。'
  % (RCOT(0), RCOT(1), RCOT(2), NLINES[1], TEXTS, DROP[0], DROP[2],
     LC, AN[u'c_title'], LT, AN[u't_cols'], EQ, len(ZR)))

BODY = NL.join(G)
GLOS = len(G)
BAT = json.load(io.open(u'corpus/_b49battery.json', encoding='utf-8'))
BATT = [u'd_' + x for x in (u'coord', u'order', u'misscomment', u'extracomment', u'unknowncc',
                           u'fivecol', u'duprow', u'extracol', u'lower', u'dupcode', u'samename',
                           u'swap', u'rename', u'stdoff', u'month', u'ruleunused', u'ruleletters')]
BATC = sorted(k for k in BAT if k.startswith(u'c_'))
assert len(BATT) == 17 and all(k in BAT for k in BATT) and len(BATC) == 12
NTAB = len([k for k in BATT[:7]])
NISO = len(BATT[7:12])
NDATA = len(BATT[12:])
assert BAT['restore']['nerr'] == 0 and BAT['restore']['bytes_err'] == 0
HEAD_MD = (u'# B49 表 ⇎ 检查这张表的程序 ⇎ 它检查的数据：规矩写在程序里，程序写在破坏里\n\n'
           u'src: %s (zone1970.tab, %d 行数据 = 四列 %d ⇎ 三列 %d; 首码相邻 相等 %d ⇎ 变大 %d ⇎ 变小 %d, '
           u'整列字面乱序 %d 处而首码全相等; 坐标 分形式 %d+秒形式 %d+不合 0, 国家码引用 %d 次去重 %d 种, '
           u'码表 %d 行里未被引用 %d 种; 口径内 %d 字符 ⇎ 全文 %d ⇎ 磁盘 %d 字节, 注释 %d 行被口径剔掉'
           u'(其中“当且仅当”等散文在口径内 0 处), 非 ASCII %d 枚其中 %d 枚在注释, 真制表符 %d ⇎ 口径 %d, sha256 %s) ⇎ '
           u'%s (checktab.awk, %d 行 awk: printf %d 条 ⇎ 拼全相邻字面量 %d 种诊断文本 ⇎ %d 条置失败码 ⇎ %d 条走 stderr ⇎ '
           u'%d 条走 stdout ⇎ %d 条带“表名:行号”而 %d 条只带名字; FS 两次赋值 ⇎ 两张表用 getline 在循环外读入并自建计数器; '
           u'口径内 %d 字符 ⇎ 全文 %d ⇎ 磁盘 %d 字节(纯 ASCII: 字符=字节), sha256 %s) ⇎ %s (europe, %d 行 = '
           u'行首注释 %d ⇎ 缩进注释 %d ⇎ 空行 %d ⇎ 非注释 %d(Zone %d ⇎ Rule %d ⇎ 续行 %d ⇎ Link %d); '
           u'STDOFF 受检 %d 值全合, 规则名定义 %d 种全无未用、带字母 %d 种全有 %% 用法、恰用一次 %d 种, 幻影键 %d 枚; '
           u'口径内 %d 字符 ⇎ 全文 %d ⇎ 磁盘 %d 字节, 非 ASCII %d 枚, sha256 %s)\n'
           u'；联结是“定义权”而非因果: 本机 gawk 5.3.2 对十份数据跑基线得 exit 0 且两条流各 0 字节; '
           u'反向对照逐条破坏(表侧 %d ⇎ 码表侧 %d ⇎ 数据侧 %d ⇎ 还原 1)与码侧变异 %d 类(换比较符 / 改豁免串 / 坏守卫条件 / 关记录) '
           u'分别得 0 ⇎ 1 ⇎ 2 ⇎ 3 ⇎ %d ⇎ %d ⇎ %d 行诊断, 其中 %d = 相邻相等首码对数 ⇎ %d = 码表行数 ⇎ %d = 表行数——'
           u'执行结果属工具侧断言, 逐条见 ⛓解读注; 形状数由 audit.py 里的 B49_* 从三份 raw 复算\n'
           u'tags: 定义权 ⇎ 不变量 判决即空输出 反向对照 码侧变异 比较符=容忍度 iff贴边 两种定位符宽度 stdout上的错误 聚合键 豁免按配置分死活 FS两层 注释三口径 字符⇎字节⇎口径\n\n'
           % (RT, len(ZR), len(C4), len(C3), EQ, GREAT, LESS, NAIVE, MINC, SECC, len(CCREF), CCD,
              len(ISOR), CCUNREF, RCOT(0), FULL[0], BYTES[0], DROP[0], NASCII[0], NASCII_R[0],
              ITAB[0], ITAB_R[0], SHA[0],
              RC, NLINES[1], PR, TEXTS, ST, RD_, POUT, WLINE, NOLINE, RCOT(1), FULL[1], BYTES[1], SHA[1],
              RZ, NLINES[2], HASH0, IND, ZBLANK, len(EL), len(ZON), len(RUL), len(CON), len(LNK),
              len(SO), len(RDEF), len(LET), ONCE, PHANT, RCOT(2), FULL[2], BYTES[2], NASCII[2], SHA[2],
              NTAB, NISO, NDATA, len(BATC), BAT['c_cc_lt']['nerr'], BAT['c_nf3']['nerr'],
              BAT['c_seen_off']['nerr'], EQ, len(ISOR), len(ZR)))
MD = (HEAD_MD + u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + BODY +
      u'\n\n## ⛓解读注\n<!--FILL-->\n')
io.open(ENTRY, 'w', encoding='utf-8').write(MD)
print(u'entry written: %s body_chars=%d gloss=%d anchors=%d' % (ENTRY, len(BODY), GLOS, ANCH))

# ---------- DERIV ----------
D2 = {}
COIN = []
EXTRA = []


def fmt(v):
    f = float(v)
    return u'%d' % f if f == int(f) else u'%g' % f


def put(val, expr):
    """同值不同事: 第一个量占键, 其余折成 0 键里的一条等式, 并在 COIN 里点名。"""
    k = fmt(val)
    if k in D2:
        EXTRA.append(u'%s-%s' % (D2[k], expr))
        COIN.append((k, D2[k], expr))
        return k
    D2[k] = expr
    return k


def CE(pat, i):
    return u"CNT(%r,%d)" % (pat, i)


def CF(pat, i):
    return u"CNTF(%r,%d)" % (pat, i)


def V(name):
    return u"B49V(%r)" % name


def L(x):
    return u"L(%r)" % str(x)


BL = lambda i: u"B49_LINES(%d)" % i
BD = lambda i: u"B49_DROP(%d)" % i
BB = lambda i: u"B49_BYTES(%d)" % i
RCX = lambda i: u"RCOT(%d)" % i
ad = lambda *p: u'+'.join(p)


def df(a, *rest):
    # 减法必须逐项加括号: a-(b+c) 与 a-b+c 不是同一件事, 而 0 键只看数值
    s = a
    for r in rest:
        s += u'-(%s)' % r if (u'+' in r or u'-' in r) else u'-%s' % r
    return s


ml = lambda a, b: u'(%s)*(%s)' % (a, b)

BLT = chr(92) + u't'  # 写进 audit.py 的字面 \\t: findall 解释回制表符

HVP = [(u'rows', len(ZR)), (u'c4rows', len(C4)), (u'c3rows', len(C3)), (u'comrows', len(COMMA)),
       (u'barerows', len(BARE)), (u'multirows', len(MULTI)), (u'eqfirst', EQ), (u'gtfirst', GREAT),
       (u'lessfirst', LESS), (u'naive', NAIVE), (u'mincoord', MINC), (u'seccoord', SECC),
       (u'ccref', len(CCREF)), (u'ccdistinct', CCD), (u'isorows', len(ISOR)),
       (u'itab', ITAB[0]), (u'itab_r', ITAB_R[0]), (u'itab_c', ITAB[1]), (u'itab_c_r', ITAB_R[1]),
       (u'itab_z', ITAB[2]), (u'itab_z_r', ITAB_R[2]),
       (u'el', len(EL)), (u'indented', IND), (u'hash0', HASH0), (u'blankz', ZBLANK),
       (u'zone', len(ZON)), (u'zone_tab', ZTAB), (u'zone_sp', ZSPC),
       (u'rule', len(RUL)), (u'rule_tab', RTAB), (u'rule_sp', RSPC),
       (u'cont', len(CON)), (u'cont_tab', CONTAB), (u'stdoff', len(SO)),
       (u'rdef', len(RDEF)), (u'rletters', len(LET)), (u'once', ONCE), (u'phantom', PHANT),
       (u'months_eu', len(MONSET)), (u'months_all', len(GMON)), (u'gdef', len(GDEF)),
       (u'gletters', len(GLET)), (u'printf', PR), (u'texts', TEXTS), (u'wline', WLINE),
       (u'noline', NOLINE), (u'stderr', RD_), (u'stdout', POUT), (u'status', ST),
       (u'wnc', WNC), (u'fs', FSN), (u'd0', D0), (u'd1', D1), (u'zt', ZTC), (u'zn', ZNC),
       (u'bk', BKC), (u'simf', SIMC), (u'want', WANTC), (u'esc_t', ESCT), (u'inr', INR),
       (u'znr', ZNR), (u'gl', GL), (u'mondef', MONC), (u'pcts', PCTS), (u'pctd', PCTDC),
       (u'tabrows', TABROWS), (u'simrow', SIMROW), (u'simviol', SIMVIOL), (u'ndata', len(DATA)),
       (u'nascii_t', NASCII[0]), (u'nascii_t_r', NASCII_R[0]), (u'nascii_z', NASCII[2]),
       (u'nascii_z_r', NASCII_R[2]), (u'nascii_z_rows', NASC_L),
       (u'threebyte', (BYTES[0] - FULL[0]) - NASCII[0]),
       (u'bytesgap_t', BYTES[0] - FULL[0]),
       (u't_full', FULL[0]), (u'c_full', FULL[1]), (u'z_full', FULL[2])]
for nm, val in HVP:
    if val:
        put(val, V(nm))

# 同一枚数值的第二种记法(正则现算 ⇎ 结构现算 / 口径 ⇎ 全文 / 字符 ⇎ 磁盘字节)
# 占不到键的都折成 0 键等式; 值为 0 的量不设键, 由 0 键里的 B49V 项单独证明
put(len(RUL), CE(P_RULE, 2))
put(len(ZON), CE(u'(?m)^Zone', 2))
put(len(EL) + IND, ad(V(u'el'), V(u'indented')))
put(len(CON), CE(P_CONT, 2))
put(RTAB, CE(P_RTAB, 2))
put(ZTAB, CE(P_ZTAB, 2))
put(len(ZR) - 1, df(V(u'rows'), L(1)))
put(len(GDEF) - len(GLET), df(V(u'gdef'), V(u'gletters')))
put(PR, CF(P_PRINTF, 1))
put(FULL[1], BB(1))
for i in range(3):
    put(NLINES[i], BL(i))
    put(DROP[i], BD(i))
    put(RCOT(i), RCX(i))
put(BYTES[0], BB(0))
put(BYTES[2], BB(2))

AB = [
    # 缺席: 表的散文词在程序口径里 0
    CE(P_IFO, 1), CE(P_UTF, 1), CE(P_STAB, 1), CE(P_SORT, 1), CE(P_POPU, 1), CE(P_GEO, 1),
    CE(u'coordinates', 0),
    # 缺席: 程序的诊断文本在表口径里 0
    CE(P_DUPZ, 0), CE(P_OOO, 0), CE(P_INVC, 0), CE(P_NOZONE, 0), CE(P_NODATA, 0), CE(P_WNC, 0),
    CE(u'STDOFF', 0), CE(u'tricky month', 0), CE(u'unlikely STDOFF', 0),
    # 缺席: 数据里没有的形状
    CE(P_LINK, 2), CF(P_LINK, 2), CE(u'(?m)^Jan' + TAB, 2), CE(P_ZONE + u'Etc/', 2),
    CE(u'(?i)single[ \t]+tab', 1),
    # 全文口径对照: 散文各 1 处( populous 2 处)而口径 0 处
    df(CF(P_IFO, 0), L(1)), df(CF(P_UTF, 0), L(1)), df(CF(P_STAB, 0), L(1)),
    df(CF(P_SORT, 0), L(1)), df(CF(P_POPU, 0), L(2)), df(CF(P_GEO, 0), L(1)),
    df(CF(u'coordinates', 0), L(1)),
    # 零: 表侧形状
    df(V(u'c4rows'), V(u'comrows')), df(V(u'comrows'), V(u'multirows')),
    df(V(u'rows'), V(u'c4rows'), V(u'c3rows')), df(V(u'barerows'), V(u'c3rows')),
    df(V(u'rows'), CE(P_ROW_T, 0)),
    df(V(u'itab_r'), ml(L(3), V(u'c4rows')), ml(L(2), V(u'c3rows'))),
    df(V(u'itab'), V(u'itab_r'), L(8)),
    df(V(u'itab_c'), V(u'itab_c_r'), L(10)),
    V(u'slack'), V(u'viol'), V(u'dupname'), V(u'badcoord'), V(u'lessfirst'),
    df(ad(V(u'eqfirst'), V(u'gtfirst'), V(u'lessfirst')), df(V(u'rows'), L(1))),
    df(V(u'naive'), V(u'eqtie')), df(V(u'unref'), L(2)), df(V(u'iso2'), V(u'isorows')),
    # 零: 数据侧
    df(ad(V(u'el'), V(u'indented'), V(u'hash0'), V(u'blankz')), BL(2)),
    df(ad(V(u'hash0'), V(u'indented')), BD(2)),
    df(V(u'cont_tab'), ad(V(u'cont'), V(u'indented'))),
    df(ad(V(u'zone_tab'), V(u'zone_sp')), V(u'zone')),
    df(ad(V(u'rule_tab'), V(u'rule_sp')), V(u'rule')),
    df(V(u'stdoff'), V(u'zone'), V(u'cont')),
    V(u'link'), V(u'stdoff_bad'), V(u'runused'), V(u'rletnop'), V(u'gunused'), V(u'gletnop'),
    V(u'zone_missing'),
    df(V(u'phantom'), L(3)), df(V(u'once'), L(13)), df(V(u'gdef'), V(u'gletters'), L(32)),
    df(V(u'nascii_z_r'), V(u'nascii_z_rows')),
    # 零: 程序侧三套账
    df(V(u'printf'), V(u'stderr'), V(u'stdout')),
    df(V(u'printf'), V(u'wline'), V(u'noline')),
    df(V(u'printf'), V(u'status'), L(1)),
    df(V(u'printf'), V(u'texts'), L(1)),
    df(V(u'wnc'), L(2)), df(V(u'fs'), L(2)), df(V(u'd0'), L(2)), df(V(u'd1'), L(1)),
    df(V(u'zt'), L(2)), df(V(u'zn'), L(3)), df(V(u'bk'), L(1)), df(V(u'simf'), L(1)),
    df(V(u'want'), L(3)), df(V(u'esc_t'), L(1)), df(V(u'inr'), L(1)), df(V(u'znr'), L(1)),
    df(V(u'gl'), L(2)), df(V(u'ndata'), L(10)),
    df(ad(V(u'months_eu'), L(1)), V(u'mondef')), df(V(u'months_all'), V(u'mondef')),
    df(V(u'mondef'), CE(P_MON, 1)),
    # 零: 字符 ⇎ 字节 ⇎ 口径
    df(BB(1), V(u'c_full')),
    df(BB(2), V(u'z_full'), V(u'nascii_z')),
    df(BB(0), V(u't_full'), V(u'bytesgap_t')),
    df(V(u'bytesgap_t'), V(u'nascii_t'), V(u'threebyte')),
    df(V(u'threebyte'), V(u'nascii_t_r')),
    df(V(u'simviol'), V(u'simrow'), L(1)),
]
AB += EXTRA
put(0, u'+'.join(AB))
NTERMS0 = len(AB)
NPRIM0 = D2[u'0'].count(u'CNT(') + D2[u'0'].count(u'CNTF(') + D2[u'0'].count(u'B49V(')
print(u'DERIV keys=%d / 0 键 %d 项(CNT %d CNTF %d B49V %d)' %
      (len(D2), NTERMS0, D2[u'0'].count(u'CNT('), D2[u'0'].count(u'CNTF('), D2[u'0'].count(u'B49V(')))
print(u'同值折等式 %d 组: %s' % (len(COIN), u' '.join(u'%s(%s)' % (c[0], c[2][:14]) for c in COIN)))

EV = {u'CNT': CNT, u'CNTF': CNTF, u'L': lambda x: float(str(x).replace(u',', u'').replace(u"'", u'')),
      u'RCOT': RCOT, u'B49V': lambda k: HV[k], u'B49_LINES': lambda i: NLINES[i],
      u'B49_DROP': lambda i: DROP[i], u'B49_BYTES': lambda i: BYTES[i]}
for t in AB:
    v0 = eval(t, {}, EV)
    if abs(v0) > 1e-12:
        print(u'0 键项非零: %-64s -> %s' % (t[:64], v0))
for k, v in D2.items():
    got = eval(v, {}, EV)
    assert abs(got - float(k)) < 1e-9, (k, got, v[:150])
print(u'DERIV 独立回算通过; 键 %s' % u' '.join(sorted(D2, key=lambda x: float(x))))

BLOCK = u" 'B49': {" + NL + NL.join(u"  %r: %r," % (k, v) for k, v in
                                   sorted(D2.items(), key=lambda x: float(x[0]))) + NL + u" }," + NL
SRC49 = u"SRC['B49'] = ['%s', '%s', '%s']" % (RT, RC, RZ) + NL
HELPER = u'''# B49: 表 ⇎ 检查这张表的程序 ⇎ 它检查的数据。形状数在审计器里独立复算, 使"改一枚比较符"与"注释的三种口径"都是机检项
def _b49_scan():
    N, T = chr(10), chr(9)
    B = chr(92)
    H = re.compile('^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
    DATA = ['africa', 'antarctica', 'asia', 'australasia', 'europe', 'northamerica',
            'southamerica', 'etcetera', 'factory', 'backward']
    def rd(p):
        return open(p, encoding='utf-8', errors='replace').read()
    def tally(xs):
        d = {}
        for x in xs:
            d[x] = d.get(x, 0) + 1
        return d
    P = SRC['B49']
    FT = [rd(p) for p in P]
    LS = [t.split(N) for t in FT]
    RS = [N.join(l for l in LS[i] if not H.match(l.strip())) for i in range(3)]
    RXMIN = '^[-+][0-9][0-9][0-5][0-9][-+][01][0-9][0-9][0-5][0-9]$'
    RXSEC = '^[-+][0-9][0-9][0-5][0-9][0-5][0-9][-+][01][0-9][0-9][0-5][0-9][0-5][0-9]$'
    RXSO = re.compile('^-?1?[0-9](:[0-5][0-9](:[0-5][0-9])?)?$')
    zrows = [l.split(T) for l in LS[0] if l[:1] != '#' and l.strip()]
    first = [r[0].split(',')[0] for r in zrows]
    ccs = [c for r in zrows for c in r[0].split(',')]
    used = tally(ccs)
    isor = [l.split(T) for l in rd('corpus/raw/tz/iso3166.tab').split(N) if l[:1] != '#' and l.strip()]
    iso2 = len([l for l in rd('corpus/raw/tz/iso3166.tab').split(N)
                if re.match('^[A-Z][A-Z]' + T, l)])
    c4 = [r for r in zrows if len(r) == 4]
    c3 = [r for r in zrows if len(r) == 3]
    comma = [r for r in zrows if len(r) > 3 and r[3].strip()]
    bare = [r for r in zrows if len(r) < 4 or not r[3].strip()]
    multi = [r for r in zrows if max(used.get(c, 0) for c in r[0].split(',')) > 1]
    pairs = range(1, len(first))
    dl = [l.split() for l in LS[2] if l.split() and l.split()[0][:1] != '#']
    zon = [t for t in dl if t[0] == 'Zone']
    rul = [t for t in dl if t[0] == 'Rule']
    lnk = [t for t in dl if t[0] == 'Link']
    con = [t for t in dl if t[0] not in ('Zone', 'Rule', 'Link')]
    so = [t[2] for t in zon if len(t) > 2] + [t[0] for t in con]
    rdef = set(t[1] for t in rul)
    let = set(t[1] for t in rul if len(t) >= 10 and t[9] != '-')
    usec, pctk = tally([]), set()
    gdef, guse, glet, gpct, gmon = set(), set(), set(), set(), set()
    for t in dl:
        if t[0] == 'Zone':
            if len(t) > 3:
                usec[t[3]] = usec.get(t[3], 0) + 1
            if len(t) > 4 and '%' in t[4]:
                pctk.add(t[3])
        elif t[0] != 'Rule' and t[0] != 'Link':
            if len(t) > 1:
                usec[t[1]] = usec.get(t[1], 0) + 1
            if len(t) > 2 and '%' in t[2]:
                pctk.add(t[1])
    for f in DATA:
        for l in rd('corpus/raw/tz/' + f).split(N):
            t = l.split()
            if not t or t[0][:1] == '#':
                continue
            if t[0] == 'Rule':
                gdef.add(t[1])
                if len(t) >= 10 and t[9] != '-':
                    glet.add(t[1])
                if len(t) > 5:
                    gmon.add(t[5])
            elif t[0] != 'Link':
                if t[0] == 'Zone':
                    if len(t) > 3:
                        guse.add(t[3])
                    if len(t) > 4 and '%' in t[4]:
                        gpct.add(t[3])
                else:
                    if len(t) > 1:
                        guse.add(t[1])
                    if len(t) > 2 and '%' in t[2]:
                        gpct.add(t[1])
    znames = set(t[1] for t in zon)
    tnames = set(r[2] for r in zrows)
    ztl = rd('corpus/raw/tz/zone.tab').split(N)
    tn = [(i, l.split(T)) for i, l in enumerate(ztl, 1) if l[:1] != '#' and l.strip()]
    stmts = []
    for m in re.finditer('(?m)^[ \\t]*printf ', FT[1]):
        j, frags = m.end(), []
        while True:
            while FT[1][j] in ' \\t' + B + N:
                j += 1
            if FT[1][j] != '"':
                break
            k = j + 1
            while FT[1][k] != '"':
                k += 2 if FT[1][k] == B else 1
            frags.append(FT[1][j + 1:k])
            j = k + 1
        stmts.append((u''.join(frags), '/dev/stderr' in FT[1][j:j + 120]))
    texts = [s[0] for s in stmts]
    wline = len([f for f in texts if f.startswith('%s:%d')])
    ind = lambda i, s: len(re.findall(s, RS[i], re.I))
    nasc = lambda t: len([c for c in t if ord(c) > 127])
    return dict(rows=len(zrows), c4rows=len(c4), c3rows=len(c3), comrows=len(comma),
               barerows=len(bare), multirows=len(multi),
               slack=len([r for r in comma if max(used.get(c, 0) for c in r[0].split(',')) <= 1]),
               viol=len([r for r in bare if max(used.get(c, 0) for c in r[0].split(',')) > 1]),
               dupname=len(zrows) - len(tnames),
               eqfirst=len([i for i in pairs if first[i] == first[i - 1]]),
               gtfirst=len([i for i in pairs if first[i] > first[i - 1]]),
               lessfirst=len([i for i in pairs if first[i] < first[i - 1]]),
               naive=len([i for i in range(1, len(zrows)) if zrows[i][0] < zrows[i - 1][0]]),
               eqtie=len([i for i in range(1, len(zrows))
                          if zrows[i][0] < zrows[i - 1][0] and first[i] == first[i - 1]]),
               mincoord=len([r for r in zrows if re.match(RXMIN, r[1])]),
               seccoord=len([r for r in zrows if re.match(RXSEC, r[1])]),
               badcoord=len(zrows) - len([r for r in zrows
                                          if re.match(RXMIN, r[1]) or re.match(RXSEC, r[1])]),
               ccref=len(ccs), ccdistinct=len(set(ccs)), isorows=len(isor), iso2=iso2,
               unref=len([r for r in isor if r[0] not in used]),
               itab=FT[0].count(T), itab_r=RS[0].count(T), itab_c=FT[1].count(T),
               itab_c_r=RS[1].count(T), itab_z=FT[2].count(T), itab_z_r=RS[2].count(T),
               el=len(dl), indented=len([l for l in LS[2] if l.strip() and l[:1] != '#'
                                         and l.split()[0][:1] == '#']),
               hash0=len([l for l in LS[2] if l[:1] == '#']),
               blankz=len([l for l in LS[2][:-1] if not H.match(l.strip()) and not l.split()]),
               zone=len(zon), rule=len(rul), link=len(lnk), cont=len(con),
               zone_tab=ind(2, '(?m)^Zone' + T), zone_sp=ind(2, '(?m)^Zone '),
               rule_tab=ind(2, '(?m)^Rule' + T), rule_sp=ind(2, '(?m)^Rule '),
               cont_tab=len([l for l in LS[2] if l[:1] == T]),
               stdoff=len(so), stdoff_bad=len([s for s in so if not RXSO.match(s)]),
               rdef=len(rdef), runused=len([x for x in rdef if usec.get(x, 0) == 0]),
               rletters=len(let), rletnop=len([x for x in let if x not in pctk]),
               phantom=len([x for x in usec if x not in rdef]),
               once=len([x for x in rdef if usec.get(x, 0) == 1]),
               months_eu=len(set(t[5] for t in rul if len(t) > 5)),
               months_all=len(gmon), gdef=len(gdef), gunused=len([x for x in gdef if x not in guse]),
               gletters=len(glet), gletnop=len([x for x in glet if x not in gpct]),
               zone_missing=len([n for n in znames if n not in tnames]),
               tabrows=len(tn),
               simrow=[i for i, l in enumerate(ztl, 1) if 'Simferopol' in l and l[:1] != '#'][0],
               simviol=[i for k in range(1, len(tn)) for i, r in [tn[k]]
                        if r[0].split(',')[0] < tn[k - 1][1][0].split(',')[0]
                        and tn[k - 1][1][2] == 'Europe/Simferopol'][0],
               printf=len(stmts), texts=len(set(texts)), wline=wline, noline=len(stmts) - wline,
               stderr=len([s for s in stmts if s[1]]), stdout=len([s for s in stmts if not s[1]]),
               status=ind(1, 'status = 1'), wnc=ind(1, 'wrong number of columns'),
               fs=ind(1, '(?m)^[ ' + T + ']*FS = '), d0=RS[1].count('$0 ~ ' + chr(47) + '^#' + chr(47)),
               d1=RS[1].count('$1 ~ ' + chr(47) + '^#' + chr(47)),
               zt=ind(1, 'zone_table == ' + chr(34) + 'zone.tab' + chr(34)),
               zn=ind(1, 'zonenow.tab'), bk=ind(1, chr(34) + 'backward' + chr(34)),
               simf=ind(1, chr(34) + 'Europe/Simferopol' + chr(34)), want=ind(1, 'want_warnings'),
               esc_t=RS[1].count(B + 't'), inr=ind(1, 'iso_NR' + B + '+' + B + '+'),
               znr=ind(1, 'zone_NR' + B + '+' + B + '+'), gl=ind(1, '(?m)getline <'),
               mondef=len([l for l in RS[1].split(N) if l.strip().startswith('monthabbr[')]),
               pcts=RS[1].count('%s'), pctd=RS[1].count('%d'), ndata=len(DATA),
               nascii_t=nasc(FT[0]), nascii_t_r=nasc(RS[0]), nascii_z=nasc(FT[2]),
               nascii_z_r=nasc(RS[2]),
               nascii_z_rows=len([l for l in RS[2].split(N) if nasc(l) > 0]),
               threebyte=(os.path.getsize(P[0]) - len(FT[0])) - nasc(FT[0]),
               bytesgap_t=os.path.getsize(P[0]) - len(FT[0]),
               t_full=len(FT[0]), c_full=len(FT[1]), z_full=len(FT[2]))


_B49 = _b49_scan()
B49V = lambda k: _B49[k]
B49_LINES = lambda i: len(open(SRC['B49'][i], encoding='utf-8', errors='replace').read().split(chr(10))) - 1
B49_DROP = lambda i: len([l for l in open(SRC['B49'][i], encoding='utf-8', errors='replace').read().split(chr(10))
                         if re.match(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)',
                                     l.strip(), re.I)])
B49_BYTES = lambda i: os.path.getsize(SRC['B49'][i])

'''

AU = u'corpus/audit.py'
s = io.open(AU, encoding='utf-8').read()
if u"SRC['B49']" not in s:
    i0 = s.index(u"SRC['B48']")
    e0 = s.index(NL, i0) + 1
    s = s[:e0] + SRC49 + s[e0:]
MARK = u'# B49: 表 ⇎ 检查这张表的程序'
if MARK not in s:
    i1 = s.index(u'DERIV = {')
    s = s[:i1] + HELPER + s[i1:]
else:
    i1 = s.index(MARK)
    e1 = s.index(u'DERIV = {')
    s = s[:i1] + HELPER + s[e1:]
TAIL = u"B48_BYTES=B48_BYTES)"
if u'B49V=B49V' not in s:
    assert s.count(TAIL) == 1, s.count(TAIL)
    s = s.replace(TAIL, TAIL[:-1] + u", B49V=B49V, B49_LINES=B49_LINES, B49_DROP=B49_DROP,"
                                    u" B49_BYTES=B49_BYTES)", 1)
if u"'B48'}" in s and u"'B49'}" not in s:
    s = s.replace(u"'B48'}", u"'B48', 'B49'}", 1)
s = re.sub(u" 'B49': \\{" + NL + u".*?" + NL + u" \\}," + NL, lambda m: BLOCK, s, count=1, flags=re.S)
if u"'B49': {" not in s:
    k0 = s.index(u'DERIV = {' + NL) + len(u'DERIV = {' + NL)
    s = s[:k0] + BLOCK + s[k0:]
io.open(AU, 'w', encoding='utf-8').write(s)

AC = u'corpus/atomcheck.py'
a = io.open(AC, encoding='utf-8').read()
if u"SRC['B49']" not in a:
    i2 = a.index(u"SRC['B48']")
    a = a[:i2] + SRC49 + a[i2:]
    io.open(AC, 'w', encoding='utf-8').write(a)
io.open(u'corpus/_atoms49.txt', 'w', encoding='utf-8').write(NL.join(sorted(set(AN.values()))) + NL)
ST = [(u'anchors', ANCH), (u'uniq_anchor', UANCH), (u'anchor_t', NT_AN), (u'anchor_c', NC_AN),
      (u'anchor_z', NZ_AN), (u'deriv_keys', len(D2)), (u'n_term0', NTERMS0), (u'n_prim0', NPRIM0),
      (u'coin', len(COIN)), (u'gloss_lines', GLOS), (u'body_chars', len(BODY)),
      (u'lines', u' '.join(str(x) for x in NLINES)), (u'dropped', u' '.join(str(x) for x in DROP)),
      (u'rcot', u' '.join(str(RCOT(i)) for i in range(3))),
      (u'full', u' '.join(str(x) for x in FULL)), (u'bytes', u' '.join(str(x) for x in BYTES)),
      (u'sha', u' '.join(x[:12] for x in SHA)),
      (u'rows', len(ZR)), (u'c4', len(C4)), (u'c3', len(C3)),
      (u'eqfirst', EQ), (u'gtfirst', GREAT), (u'lessfirst', LESS), (u'naive', NAIVE),
      (u'coord', u'%d %d' % (MINC, SECC)), (u'ccref', len(CCREF)), (u'ccd', CCD),
      (u'isorows', len(ISOR)), (u'unref', CCUNREF),
      (u'el', len(EL)), (u'indented', IND), (u'hash0', HASH0), (u'blankz', ZBLANK),
      (u'zone', u'%d %d %d' % (len(ZON), ZTAB, ZSPC)), (u'rule', u'%d %d %d' % (len(RUL), RTAB, RSPC)),
      (u'cont', u'%d %d' % (len(CON), CONTAB)), (u'stdoff', len(SO)),
      (u'rdef', u'%d %d %d' % (len(RDEF), len(LET), ONCE)), (u'phantom', PHANT),
      (u'gdef', u'%d %d' % (len(GDEF), len(GLET))), (u'months', u'%d %d %d' % (len(MONSET), MONC, len(GMON))),
      (u'printf', u'%d %d %d %d %d %d %d' % (PR, TEXTS, WLINE, NOLINE, RD_, POUT, ST)),
      (u'prog', u'%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d'
       % (FSN, GL, INR, ZNR, MONC, D0, D1, ZTC, ZNC, BKC, SIMC, WANTC, ESCT, PCTS, WNC)),
      (u'nascii', u'%d %d %d %d %d' % (NASCII[0], NASCII_R[0], NASCII[1], NASCII[2], NASCII_R[2])),
      (u'itab', u'%d %d %d %d %d %d' % (ITAB[0], ITAB_R[0], ITAB[1], ITAB_R[1], ITAB[2], ITAB_R[2])),
      (u'zone_tab', u'%d %d %d' % (TABROWS, SIMROW, SIMVIOL)), (u'data', str(len(DATA)))]
io.open(u'corpus/_f49stats.txt', 'w', encoding='utf-8').write(NL.join(u'%s\t%s' % (k, v) for k, v in ST) + NL)
print(u'wired B49: audit SRC/B49V/HELPER/DERIV(%d keys) + atomcheck SRC + _atoms49.txt(%d uniq)'
      % (len(D2), UANCH))
