# -*- coding: utf-8 -*-
"""README 记账: 48 条 → 49 条。合计数字全部由 audit 表、metrics 普查、三份 raw 回算与 _f49stats 复算, 不手填。
B49 特有的一环: 这里把检查器再真跑五遍——两份配置各 0 字节、换一枚比较符得 158 行、坏一条守卫得 312 行、
打开提示得 stdout 2 行——并与 _b49battery.json 逐项相等; README 里那句“判决的正常形态是空”因此不是转述。"""
import io, os, re, sys, json, ast, hashlib, subprocess, tempfile, collections

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
t = io.open(F, encoding='utf-8').read()

TAG, ENTRY = u'B49', u'corpus/babeltele/B49_table_checker_and_checked_data.md'
RT, RC, RZ = (u'corpus/raw/tz/zone1970.tab', u'corpus/raw/tz/checktab.awk', u'corpus/raw/tz/europe')
RAWS = [RT, RC, RZ]
TZDIR = u'corpus/raw/tz'
DATA = [u'africa', u'antarctica', u'asia', u'australasia', u'europe', u'northamerica',
        u'southamerica', u'etcetera', u'factory', u'backward']
EXTRA = [u'iso3166.tab', u'zone1970.tab', u'zone.tab', u'checktab.awk']
NL, TAB, BS = u'\n', u'\t', u'\\'
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)

# ---------- audit / metrics ----------
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-600:]
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
dig_all, enc_all, ret_all, uniq_all = (int(allc[0].replace(u' ', u'')), int(allc[1].replace(u' ', u'')),
                                       allc[2], int(allc[4]))
soft_all = int(re.search(u'提示\\(不计入 FAIL, 1-2 位结构计数未逐位核验\\): 共 (\\d+) 个', p.stdout).group(1))
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
NENT = len(row) - 1
cells = lambda tag: [x.strip() for x in row[tag].split(u'|')]
b49, b48 = cells(u'B49'), cells(u'B48')
b49_enc, b49_dig, b49_ret, b49_raw, b49_uniq, b49_blocks, b49_cpu, b49_soft = (
    int(b49[1]), int(b49[0]), b49[2], b49[3], int(b49[4]), int(b49[5]), b49[6], int(b49[10]))
b48_enc, b48_dig, b48_ret = int(b48[1]), int(b48[0]), b48[2]
assert NENT == 49, NENT
assert b49_soft == 0 and not re.search(u"^\\s+B49 \\[", p.stdout, re.M), (b49, soft_all)
assert int(b49[7]) == 0 and int(b49[8]) == 0 and int(b49[9]) == 0, b49
ZSOFT = sorted([k for k in row if k != u'ALL' and int(cells(k)[10]) == 0], key=lambda x: int(x[1:]))
assert all(k in ZSOFT for k in (u'B32', u'B43', u'B45', u'B46', u'B47', u'B49'))
assert u'B48' not in ZSOFT and len(ZSOFT) == 38, (u'B49 待核列为空', len(ZSOFT))

m = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/metrics.py'],
                   capture_output=True, text=True, encoding='utf-8')
cen = dict((mm.group(1), int(mm.group(2))) for mm in
           re.finditer(r'^\s{2}([A-Za-z\-]+)\s+([\d ]+)$', m.stdout, re.M))
assert len(cen) == 18, sorted(cen)


def loadstat(fn):
    d = {}
    for l in io.open(fn, encoding='utf-8').read().split(u'\n'):
        if u'\t' in l:
            k, v = l.split(u'\t')
            d[k] = v
    return d


ST = loadstat(u'corpus/_f49stats.txt')
NUM = lambda k: int(ST[k])
DERIV_KEYS, NTERM0, NPRIM0, COIN = NUM(u'deriv_keys'), NUM(u'n_term0'), NUM(u'n_prim0'), NUM(u'coin')
ANCH, UANCH = NUM(u'anchors'), NUM(u'uniq_anchor')
ANCH_T, ANCH_C, ANCH_Z = NUM(u'anchor_t'), NUM(u'anchor_c'), NUM(u'anchor_z')
GLOS, BODY = NUM(u'gloss_lines'), NUM(u'body_chars')
assert ANCH_T + ANCH_C + ANCH_Z == ANCH == UANCH, (ANCH_T, ANCH_C, ANCH_Z, ANCH, UANCH)
assert b49_enc == 13279 and b49_dig == 3400
assert b49_ret == u'%.1f%%' % (100.0 * b49_enc / b49_dig)

# ---------- 三口径与形状: 独立回算(与 _mkB49 / audit 内 B49_* 同规则的第三条路) ----------
rd = lambda f: io.open(f, encoding='utf-8', errors='replace').read()
TXT = [rd(x) for x in RAWS]
LINES = [x.split(NL) for x in TXT]
SRC = [NL.join(l for l in LINES[i] if not HEADRX.match(l.strip())) for i in range(3)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
CNTF = lambda pat, i: len(re.findall(pat, TXT[i], re.I))
RCOT = lambda i: len(SRC[i].strip())
FULL = [len(TXT[i]) for i in range(3)]
BYTES = [os.path.getsize(x) for x in RAWS]
NLINES = [len(LINES[i]) - 1 for i in range(3)]
DROP = [len([l for l in LINES[i] if HEADRX.match(l.strip())]) for i in range(3)]
NASC = [len(re.findall(u'[^\x00-\x7f]', TXT[i])) for i in range(3)]
NASC_R = [len(re.findall(u'[^\x00-\x7f]', SRC[i])) for i in range(3)]
ITAB = [x.count(TAB) for x in TXT]
ITAB_R = [x.count(TAB) for x in SRC]
SHA = [hashlib.sha256(open(x, 'rb').read()).hexdigest() for x in RAWS]
sp = lambda k: tuple(int(x) for x in ST[k].split(u' '))
assert tuple(NLINES) == sp(u'lines') == (375, 228, 4212)
assert tuple(DROP) == sp(u'dropped') == (63, 7, 2897)
assert tuple(RCOT(i) for i in range(3)) == sp(u'rcot') == (14482, 4967, 40303)
assert tuple(FULL) == sp(u'full') == (17536, 5377, 187806)
assert tuple(BYTES) == sp(u'bytes') == (17592, 5377, 188472)
assert SHA[0][:12] + u' ' + SHA[1][:12] + u' ' + SHA[2][:12] == ST[u'sha']
assert BYTES[1] == FULL[1] == 5377 and NASC[1] == 0
assert (NASC[0], NASC_R[0], NASC[1], NASC[2], NASC_R[2]) == sp(u'nascii') == (38, 18, 0, 666, 2)
assert (ITAB[0], ITAB_R[0], ITAB[1], ITAB_R[1], ITAB[2], ITAB_R[2]) == sp(u'itab')
assert BYTES[0] - FULL[0] == 56 and BYTES[2] - FULL[2] == NASC[2] == 666
X2 = 2 * NASC[0] - (BYTES[0] - FULL[0])
assert X2 == 20 and NASC[0] - X2 == 18, (X2, NASC[0])

# 表: 不看程序的复算
ZL = [l for l in LINES[0] if l[:1] != u'#' and l.strip()]
ZR = [l.split(TAB) for l in ZL]
C4 = [r for r in ZR if len(r) == 4]
C3 = [r for r in ZR if len(r) == 3]
FIRST = [r[0].split(u',')[0] for r in ZR]
EQ = len([i for i in range(1, len(FIRST)) if FIRST[i] == FIRST[i - 1]])
LESS = len([i for i in range(1, len(FIRST)) if FIRST[i] < FIRST[i - 1]])
GREAT = len([i for i in range(1, len(FIRST)) if FIRST[i] > FIRST[i - 1]])
NAIVE = len([i for i in range(1, len(ZR)) if ZR[i][0] < ZR[i - 1][0]])
assert (len(ZR), len(C4), len(C3)) == (NUM(u'rows'), NUM(u'c4'), NUM(u'c3')) == (312, 201, 111)
assert (EQ, GREAT, LESS) == (NUM(u'eqfirst'), NUM(u'gtfirst'), NUM(u'lessfirst')) == (158, 153, 0)
assert EQ + GREAT + LESS == len(ZR) - 1 and NAIVE == NUM(u'naive') == 6
assert all(FIRST[i] == FIRST[i - 1] for i in range(1, len(ZR)) if ZR[i][0] < ZR[i - 1][0])
RXMIN = u'^[-+][0-9][0-9][0-5][0-9][-+][01][0-9][0-9][0-5][0-9]$'
RXSEC = u'^[-+][0-9][0-9][0-5][0-9][0-5][0-9][-+][01][0-9][0-9][0-5][0-9][0-5][0-9]$'
MINC = len([r for r in ZR if re.match(RXMIN, r[1])])
SECC = len([r for r in ZR if re.match(RXSEC, r[1])])
assert (MINC, SECC, len(ZR) - MINC - SECC) == sp(u'coord') + (0,) == (265, 47, 0)
assert ITAB_R[0] == 3 * len(C4) + 2 * len(C3) == 825
# 表的散文与程序的记号: 词面交集双向为空
PHR = [u'if and only if', u'single tab', u'(?i)sorted', u'populous', u'geographical']
W0 = sum(CNT(p, 0) for p in PHR)
W1 = sum(CNT(p, 1) for p in PHR)
assert (W0, W1) == (0, 0)
assert [CNTF(p, 0) for p in PHR] == [1, 1, 1, 2, 1]
CCREF = [c for r in ZR for c in r[0].split(u',')]
USED = collections.Counter(CCREF)
ISOR = [l.split(TAB) for l in rd(u'corpus/raw/tz/iso3166.tab').split(NL) if l[:1] != u'#' and l.strip()]
assert (len(CCREF), len(set(CCREF)), len(ISOR),
        len([x for x in ISOR if x[0] not in USED])) == (
    NUM(u'ccref'), NUM(u'ccd'), NUM(u'isorows'), NUM(u'unref')) == (423, 247, 249, 2)
COMMA = [r for r in ZR if len(r) > 3 and r[3].strip()]
BARE = [r for r in ZR if len(r) < 4 or not r[3].strip()]
MULTI = [r for r in ZR if max(USED.get(c, 0) for c in r[0].split(u',')) > 1]
assert (len(COMMA), len(MULTI), len(BARE), len(ZR) - len(MULTI)) == (201, 201, 111, 111)
SLACK = len([r for r in COMMA if max(USED.get(c, 0) for c in r[0].split(u',')) <= 1])
VMISS = len([r for r in BARE if max(USED.get(c, 0) for c in r[0].split(u',')) > 1])
assert (SLACK, VMISS) == (0, 0)
assert len(ZR) - len(set(r[2] for r in ZR)) == 0

# 数据: 照程序的取列法
EL = [l.split() for l in LINES[2] if l.split() and l.split()[0][:1] != u'#']
IND = len([l for l in LINES[2] if l.strip() and l[:1] != u'#' and l.split()[0][:1] == u'#'])
HASH0 = len([l for l in LINES[2] if l[:1] == u'#'])
ZBLANK = NLINES[2] - DROP[2] - len(EL)
ZON = [t for t in EL if t[0] == u'Zone']
RUL = [t for t in EL if t[0] == u'Rule']
LNK = [t for t in EL if t[0] == u'Link']
CON = [t for t in EL if t[0] not in (u'Zone', u'Rule', u'Link')]
assert (len(EL), IND, HASH0, ZBLANK) == (NUM(u'el'), NUM(u'indented'), NUM(u'hash0'),
                                         NUM(u'blankz')) == (1020, 7, 2890, 295)
assert len(EL) + IND == 1027
assert (len(ZON), len(RUL), len(LNK), len(CON)) == (65, 515, 0, 440)
assert (CNT(u'(?m)^Zone' + TAB, 2), CNT(u'(?m)^Zone ', 2)) == (29, 36)
assert (CNT(u'(?m)^Rule' + TAB, 2), CNT(u'(?m)^Rule ', 2)) == (503, 12)
assert CNTF(u'(?m)^' + TAB, 2) == len(CON) + IND == 447
SO = [t[2] for t in ZON if len(t) > 2] + [t[0] for t in CON]
assert (len(SO), len([s for s in SO
                      if not re.match(u'^-?1?[0-9](:[0-5][0-9](:[0-5][0-9])?)?$', s)])) == (505, 0)
assert len(SO) == len(ZON) + len(CON) == 505
RDEF = set(t[1] for t in RUL)
LET = set(t[1] for t in RUL if len(t) >= 10 and t[9] != u'-')
USEC, PCTK = collections.Counter(), set()
for ev in EL:
    if ev[0] == u'Zone':
        if len(ev) > 3:
            USEC[ev[3]] += 1
        if len(ev) > 4 and u'%' in ev[4]:
            PCTK.add(ev[3])
    elif ev[0] not in (u'Rule', u'Link'):
        if len(ev) > 1:
            USEC[ev[1]] += 1
        if len(ev) > 2 and u'%' in ev[2]:
            PCTK.add(ev[1])
assert (len(RDEF), len(LET), len([k for k in RDEF if USEC.get(k, 0) == 1]),
        len([k for k in RDEF if USEC.get(k, 0) == 0]), len([k for k in LET if k not in PCTK]),
        len([k for k in USEC if k not in RDEF])) == (30, 29, 13, 0, 0, 3)
assert sp(u'rdef') == (30, 29, 13) and NUM(u'phantom') == 3
GD, GU, GL, GP, GM = set(), set(), set(), set(), set()
for f in DATA:
    for l in rd(u'%s/%s' % (TZDIR, f)).split(NL):
        tk = l.split()
        if not tk or tk[0][:1] == u'#':
            continue
        if tk[0] == u'Rule':
            GD.add(tk[1])
            if len(tk) >= 10 and tk[9] != u'-':
                GL.add(tk[1])
            if len(tk) > 5:
                GM.add(tk[5])
        elif tk[0] != u'Link':
            if tk[0] == u'Zone':
                if len(tk) > 3:
                    GU.add(tk[3])
                if len(tk) > 4 and u'%' in tk[4]:
                    GP.add(tk[3])
            else:
                if len(tk) > 1:
                    GU.add(tk[1])
                if len(tk) > 2 and u'%' in tk[2]:
                    GP.add(tk[1])
assert (len(GD), len(GL), len([k for k in GD if k not in GU]), len([k for k in GL if k not in GP]),
        len(GM)) == (135, 103, 0, 0, 12)
assert sp(u'gdef') == (len(GD), len(GL))
assert len(GD) - len(GL) == 32
assert (len(set(t[5] for t in RUL if len(t) > 5)), len(GM),
        CNT(u'monthabbr\\["[A-Z][a-z]{2}"\\] = 1', 1)) == (11, 12, 12)

# 程序: 三套账
STMTS = []
for mo in re.finditer(u'(?m)^[ \t]*printf ', TXT[1]):
    j, frags = mo.end(), []
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
FF = [s[0] for s in STMTS]
PR, TEXTS = len(STMTS), len(set(FF))
WLINE = len([f for f in FF if f.startswith(u'%s:%d')])
RD_, POUT = CNT(u'/dev/stderr', 1), len([s for s in STMTS if not s[1]])
ST_ = CNT(u'status = 1', 1)
assert (PR, TEXTS, WLINE, PR - WLINE, RD_, POUT, ST_) == (18, 17, 15, 3, 14, 4, 17)
PLOG = sp(u'printf')
assert PLOG == (PR, TEXTS, WLINE, PR - WLINE, RD_, POUT, ST_)
assert [f for f, c in collections.Counter(FF).items() if c > 1] == [u'%s:%d: wrong number of columns\\n']
assert PR == CNT(u'(?m)^[ \t]*printf ', 1) == CNTF(u'(?m)^[ \t]*printf ', 1) == len(STMTS)
assert PR == TEXTS + 1 == RD_ + POUT == WLINE + (PR - WLINE) and ST_ == PR - 1
assert sp(u'prog') == (2, 2, 1, 1, 12, 2, 1, 2, 3, 1, 1, 3, 1, 35, 2)
FSN, GLC = CNT(u'(?m)^[ \t]*FS = ', 1), CNT(u'(?m)getline <', 1)
assert (FSN, GLC) == (2, 2)
assert (CNT(u'zone_table == "zone.tab"', 1), CNT(u'zonenow.tab', 1), CNT(u'"backward"', 1),
        CNT(u'"Europe/Simferopol"', 1), CNT(u'want_warnings', 1), CNT(u'\\\\t', 1)) == (2, 3, 1, 1, 3, 1)
assert (CNT(u'%s', 1), CNT(u'%d', 1), CNT(u'wrong number of columns', 1)) == (35, 16, 2)
assert sp(u'months') == (11, 12, 12)

# 姊妹表: Simferopol 特例的权重
TABL = rd(u'corpus/raw/tz/zone.tab').split(NL)
TNON = [(i, l.split(TAB)) for i, l in enumerate(TABL, 1) if l[:1] != u'#' and l.strip()]
SIMROW = [i for i, l in enumerate(TABL, 1) if u'Simferopol' in l and l[:1] != u'#'][0]
SIMVIOL = [i for k in range(1, len(TNON)) for i, r in [TNON[k]]
           if r[0].split(u',')[0] < TNON[k - 1][1][0].split(u',')[0]
           and TNON[k - 1][1][2] == u'Europe/Simferopol'][0]
assert (len(TNON), SIMROW, SIMVIOL) == sp(u'zone_tab') == (418, 336, 337)
assert NUM(u'data') == len(DATA) == 10

# ---------- 检查器真跑: 五格与电池对表 ----------
BASE = {f: open(os.path.join(TZDIR, f), 'rb').read() for f in DATA + EXTRA}
PROG = BASE['checktab.awk']
CW = BASE['checktab.awk'].decode('utf-8').replace('\r\n', '\n')


def run(prog, zt, warn=0):
    d = tempfile.mkdtemp()
    io.open(os.path.join(d, 'checktab.awk'), 'wb').write(prog)
    for f in DATA + [x for x in EXTRA if x != 'checktab.awk']:
        io.open(os.path.join(d, f), 'wb').write(BASE[f])
    q = subprocess.run([u'gawk', u'-f', u'checktab.awk', u'-v', u'iso_table=iso3166.tab',
                        u'-v', u'zone_table=%s' % zt, u'-v', u'want_warnings=%d' % warn] + DATA,
                       cwd=d, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (q.returncode, len([x for x in q.stderr.decode('utf-8', 'replace').split(u'\n') if x]),
            len([x for x in q.stdout.decode('utf-8', 'replace').split(u'\n') if x]),
            len(q.stderr), len(q.stdout))


BAT = json.load(io.open(u'corpus/_b49battery.json', encoding='utf-8'))
GVER = subprocess.run([u'gawk', u'-W', u'version'], capture_output=True, text=True,
                      encoding='utf-8', errors='replace').stdout.split(NL)[0]
JOBS = [(u'base_zone1970.tab', PROG, u'zone1970.tab', 0), (u'base_zone.tab', PROG, u'zone.tab', 0),
        (u'c_cc_lt', CW.replace(u'if (cc < cc0 \\\n\t\t    && !(zone_table == "zone.tab"',
                                u'if (cc <= cc0 \\\n\t\t    && !(zone_table == "zone.tab"')
         .encode('utf-8'), u'zone1970.tab', 0),
        (u'c_seen_off', CW.replace(u'if (tz && tz ~ /\\// && tz !~ /^Etc\\//) {',
                                   u'if (0 && tz && tz ~ /\\// && tz !~ /^Etc\\//) {').encode('utf-8'),
         u'zone1970.tab', 0),
        (u'c_warn_on', PROG, u'zone1970.tab', 1)]
RUNS = {}
for key, prog, zt, warn in JOBS:
    rc, ne, no, be, bo = run(prog, zt, warn)
    RUNS[key] = (rc, ne, no, be, bo)
    assert (rc, ne, no, be, bo) == (BAT[key][u'exit'], BAT[key][u'nerr'], BAT[key][u'nout'],
                                    BAT[key][u'bytes_err'], BAT[key][u'bytes_out']), (key, RUNS[key])
assert RUNS[u'base_zone1970.tab'] == (0, 0, 0, 0, 0) == RUNS[u'base_zone.tab']
assert RUNS[u'c_cc_lt'][1] == EQ == 158 and RUNS[u'c_seen_off'][1] == len(ZR) == 312
assert RUNS[u'c_warn_on'][2] == NUM(u'unref') == 2 and RUNS[u'c_warn_on'][0] == 0
assert BAT[u'c_iso_lt'][u'nerr'] == BAT[u'c_usedmax'][u'nerr'] == BAT[u'c_backward'][u'nerr'] == 0
assert BAT[u'c_exempt_dead'][u'nerr'] == 1 and BAT[u'c_cc_lt_zonetab'][u'nerr'] == 169 \
    and BAT[u'c_cc_lt_noexempt'][u'nerr'] == 170
assert BAT[u'c_nf3'][u'nerr'] == len(ISOR) == 249
assert BAT[u'd_duprow'][u'nerr'] == 0 and BAT[u'd_duprow'][u'nout'] == 1 \
    and BAT[u'd_duprow'][u'exit'] == 1 and BAT[u'd_ruleunused'][u'nout'] == 2
assert all(BAT[k][u'nerr'] == BAT[k][u'nout'] == 0 for k in BAT if k.startswith(u'crlf'))
N17 = len([k for k in BAT if k.startswith(u'd_')])
N12 = len([k for k in BAT if k.startswith(u'c_')])
NCRLF = len([k for k in BAT if k.startswith(u'crlf')])
assert (N17, N12, NCRLF, len(BAT)) == (17, 12, 5, 38), (N17, N12, NCRLF, len(BAT))
# 破坏按“动的是哪一份原料”分三档: 表侧 / 码表侧 / 数据文件侧
DORDER = [u'd_coord', u'd_order', u'd_misscomment', u'd_extracomment', u'd_unknowncc', u'd_fivecol',
          u'd_duprow', u'd_extracol', u'd_lower', u'd_dupcode', u'd_samename', u'd_swap',
          u'd_rename', u'd_stdoff', u'd_month', u'd_ruleunused', u'd_ruleletters']
assert sorted(DORDER) == sorted([k for k in BAT if k.startswith(u'd_')])
NTAB, NISO, NDATA = len(DORDER[:7]), len(DORDER[7:12]), len(DORDER[12:])
assert (NTAB, NISO, NDATA) == (7, 5, 5)
NBASE = len([k for k in BAT if k.startswith(u'base_')])
NREST = len([k for k in BAT if k == u'restore'])
NWARN = len(BAT) - (NTAB + NISO + NDATA + N12 + NCRLF + NBASE + NREST)
assert (NBASE, NREST, NWARN) == (2, 1, 1), (NBASE, NREST, NWARN)
assert u'warn_off_flag' in BAT
BATC = sorted(k for k in BAT if k.startswith(u'c_'))

# ---------- DERIV 0 键原语计数(从 audit.py 现读, 不手填) ----------
AUD = io.open(u'corpus/audit.py', encoding='utf-8').read()
ZERO = re.search(r"'B49': \{\n  '0': ('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"),", AUD).group(1)
ZEXP = ast.literal_eval(ZERO)
PCCNT = len(re.findall(u"(?<!F)CNT\\(", ZEXP))
PCCNTF = len(re.findall(u"CNTF\\(", ZEXP))
PCB49 = len(re.findall(u"B49V\\(", ZEXP))
assert (PCCNT, PCCNTF, PCB49) == (27, 9, 157)
assert PCCNT + PCCNTF + PCB49 == NPRIM0 == NUM(u'n_prim0')

# 加法项的三种口径(全部从 audit.py 的现文本量出, 不手填):
#   朴素按字面 '+' 切 / 只在括号深度 0 且字面量外切 / 生成脚本侧的 AB 项数(记在 _f49stats)
def _terms(e):
    out, buf, depth, q, esc, lit, deep = [], [], 0, None, False, 0, 0
    for ch in e:
        if q:
            buf.append(ch)
            if ch == u'+' and not esc:
                lit += 1
            if esc:
                esc = False
            elif ch == u'\\':
                esc = True
            elif ch == q:
                q = None
            continue
        if ch in (u'"', u"'"):
            q = ch
        elif ch == u'(':
            depth += 1
        elif ch == u')':
            depth -= 1
        elif ch == u'+' and depth == 0:
            out.append(u''.join(buf))
            buf = []
            continue
        elif ch == u'+':
            deep += 1
        buf.append(ch)
    out.append(u''.join(buf))
    return out, lit, deep

TERM0, LITPLUS, DEEPLUS = _terms(ZEXP)
NDEP0 = len(TERM0)
NAIVEPLUS = len(ZEXP.split(u'+'))
assert (NDEP0, NAIVEPLUS) == (129, 131)
assert NAIVEPLUS - NDEP0 == LITPLUS + DEEPLUS == 2
assert NDEP0 > NTERM0 and NTERM0 == NUM(u'n_term0')
TR = ast.parse(ZEXP, mode='eval')
def _leaves(n):
    return _leaves(n.left) + _leaves(n.right) if isinstance(n, ast.BinOp) else 1
NLEAF = _leaves(TR.body)
FAM = collections.Counter(n.func.id for n in ast.walk(TR)
                          if isinstance(n, ast.Call) and isinstance(n.func, ast.Name))
OPS = collections.Counter(type(n.op).__name__ for n in ast.walk(TR) if isinstance(n, ast.BinOp))
NFILE = FAM[u'B49_LINES'] + FAM[u'B49_DROP'] + FAM[u'B49_BYTES']
assert (FAM[u'CNT'], FAM[u'CNTF'], FAM[u'B49V'], len(FAM)) == (PCCNT, PCCNTF, PCB49, 7)
assert NLEAF == sum(FAM.values())
assert NLEAF - 1 == OPS[u'Add'] + OPS[u'Sub'] + OPS[u'Mult']

fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')

# ---------- 条目结构 ----------
md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
labels = re.findall(u'⟦([TCZ])⟧⟨', body)
uniq_atoms = sorted(set(atoms))
NOCC = len(atoms)
DIST = len(set(atoms))
assert (NOCC, DIST) == (118, 49), (NOCC, DIST)
NLAB = dict((c, labels.count(c)) for c in u'TCZ')
assert (NLAB[u'T'], NLAB[u'C'], NLAB[u'Z']) == (30, 74, 14), NLAB
assert sum(NLAB.values()) == NOCC == len(labels)
# 登记表(逐字命中机检的输入)与正文引用是两回事: 51 条全部命中 raw, 正文引用其中 49 条
REG = [x.rstrip(NL) for x in io.open(u'corpus/_atoms49.txt', encoding=u'utf-8') if x.strip()]
assert (len(REG), len(set(REG))) == (ANCH, UANCH) == (51, 51)
UNCITED = len([x for x in REG if x not in set(atoms)])
assert UNCITED == 2
# 逐字回源不是转述: 这里真跑一遍 atomcheck
ac = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/atomcheck.py', u'B49', u'corpus/_atoms49.txt'],
                    capture_output=True, text=True, encoding=u'utf-8')
AK, AB_ = (int(x) for x in re.search(r'ok=(\d+) bad=(\d+)', ac.stdout).groups())
assert (AK, AB_) == (len(REG), 0), ac.stdout[-400:]
IN_LAT = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
OUT_ALL = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
TAG_LAT = len(labels)
OUT_LAT = OUT_ALL - TAG_LAT
CRZERO = max(BAT[k][u'nerr'] + BAT[k][u'nout'] for k in BAT if k.startswith(u'crlf'))
# 摘要段与正文的比对只能按空白折叠做(表行以制表符分列, 摘要每行前加缩进): 精确子串只命中 1 处
_fold = lambda s: re.sub(u'\\s+', u' ', s)
DIG = md[:md.index(u'## ⟪BabelTele⟫')]
DIGHIT = len([a for a in atoms if _fold(a) in _fold(DIG)])
assert (DIGHIT, NOCC) == (104, 118), (DIGHIT, NOCC)
EXACT = len([a for a in atoms if a in DIG])
assert EXACT == 1

mm = re.search(u'第二代（B11–B48）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
               u'全库合计 \\*\\*([\\d ]+)／([\\d ]+)\\*\\*', t)
assert mm, u'第二代行未命中'
prev_in, prev_out = int(mm.group(1).replace(u' ', u'')), int(mm.group(2).replace(u' ', u''))
FIRST_IN, FIRST_OUT = 121, 2195
assert prev_in + FIRST_IN == int(mm.group(3).replace(u' ', u'')), mm.group(3)
assert prev_out + FIRST_OUT == int(mm.group(4).replace(u' ', u'')), mm.group(4)
assert cen[u'Latin'] - prev_in - prev_out - FIRST_IN - FIRST_OUT == IN_LAT + OUT_ALL, (
    cen[u'Latin'], prev_in, prev_out, IN_LAT, OUT_ALL)
in_lat, out_lat = prev_in + IN_LAT, prev_out + OUT_ALL
OLD_PROOFS = int(re.search(u'当前 \\*\\*48 条语料／(\\d+) 条\\*\\*推导', t).group(1))
assert proofs == OLD_PROOFS + 65, (OLD_PROOFS, proofs)

RCOT_SUM, BYTES_SUM = sum(RCOT(i) for i in range(3)), sum(BYTES)
cen_s = (u'Latin %s · Han %s · Gen-Punct %s · Arrows %s · CJK-Punct %s · Fullwidth %s · Emoji %s · Math %s · '
         u'Greek %s · Misc-Symbols %s · Dingbats %s · Geometric %s · Hiragana %s · Katakana %s · '
         u'MathAlnum %s · EnclosedIdeo %s · EnclosedSuppl %s · Comb-Diacritic %s') % tuple(
    fmt(cen[k]) for k in [u'Latin', u'Han', u'Gen-Punct', u'Arrows', u'CJK-Punct', u'Fullwidth', u'Emoji',
                          u'Math', u'Greek', u'Misc-Symbols', u'Dingbats', u'Geometric', u'Hiragana',
                          u'Katakana', u'MathAlnum', u'EnclosedIdeo', u'EnclosedSuppl', u'Comb-Diacritic'])

# ---------- 全库计数成对替换 ----------
PAIRS = [
 (u'共 **48 条**（`babeltele/B01..B48`）', u'共 **%d 条**（`babeltele/B01..B49`）' % NENT),
 (u'**PASS**（48 条）', u'**PASS**（%d 条）' % NENT),
 (u'当前 **48 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (OLD_PROOFS, OLD_PROOFS),
  u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs)),
 (u'第二代（B11–B48）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B49）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'残余提示（不计 FAIL）：%d 个 1–2 位结构计数' % soft_all,
  u'残余提示（不计 FAIL）：%d 个 1–2 位结构计数' % soft_all),
 (u'B48 的 `48` 是条目号自身与助手名 `B48_*` 里那两个数字, '
  u'同样不是量在三份源上的断言）未逐位核验，',
  u'B48 的 `48` 是条目号自身与助手名 `B48_*` 里那两个数字, '
  u'同样不是量在三份源上的断言；新建的 B49 待核列为空——它把两位以内的结构计数全部折进了 DERIV）未逐位核验，'),
 (u'B32／B33／B34／B35／B36／B37／B38／B39／B40／B41／B42／B43 是**待核列为 0** 的 37 条条目里最连续的十二条'
  u'（其后 B45／B46／B47 同样为 0；新建的 B48 有 1 项，即上面那条条目号 48）',
  u'B32／B33／B34／B35／B36／B37／B38／B39／B40／B41／B42／B43 是**待核列为 0** 的 %d 条条目里最连续的十二条'
  u'（其后 B45／B46／B47／B49 同样为 0；只有 B48 有 1 项，即上面那条条目号 48）' % len(ZSOFT)),
]
for old, new in PAIRS:
    n = t.count(old)
    if n != 1:
        print(u'注意: 未命中或多处 -> %r (%d)' % (old[:50], n))
    assert n >= 1, old[:50]
    t = t.replace(old, new, 1)

R = t.split(u'\n')
done = []
for i, l in enumerate(R):
    if l.startswith(u'| **合计（48 条）**'):
        R[i] = (u'| **合计（%d 条）** | **%s** | **%s**（摘要段合计 %s） | — | **%s** | — |'
                % (NENT, fmt(enc_all), ret_all.strip(u'*'), fmt(dig_all), fmt(uniq_all)))
        done.append(u'合计')
        break
for i, l in enumerate(R):
    if l.startswith(u'Latin ') and u'· Han ' in l:
        R[i] = cen_s
        done.append(u'普查')
        break
for i, l in enumerate(R):
    if l.startswith(u'唯一码点 '):
        R[i] = u'唯一码点 %s / %s ≈ %.1f%%' % (fmt(uniq_all), fmt(enc_all), 100.0 * uniq_all / enc_all)
        done.append(u'唯一码点')
        break
for i, l in enumerate(R):
    if u'B48 把轴换成**输入 ⇎ 生成它的程序 ⇎ 程序的产物**' in l and l.rstrip().endswith(u'都不在任何窗口里。'):
        R[i] = l.rstrip() + (
            u'B49 把轴换成**表 ⇎ 检查这张表的程序 ⇎ 它检查的数据**（登记 %d 条锚全部逐字回源 ok=%d bad=%d，正文标注 %d 处／%d 个不同串：表侧 %d ⇎ 程序侧 %d ⇎ 数据侧 %d）：'
            u'这一条的联结既非生成也非引用，而是**定义权**——程序的唯一产物是判决，而判决的正常形态是空'
            u'（本机 %s 对 %d 份数据跑基线：exit %d、两条流各 %d 字节），于是可核性又长出一环：反向对照。'
            u'%d 格破坏（表侧 %d ⇎ 码表侧 %d ⇎ 数据侧 %d ⇎ 码侧变异 %d ⇎ CRLF %d ⇎ 基线 %d ⇎ 还原 %d ⇎ 警告开关 %d）逐格真跑，'
            u'数字全部取自那次的输出：把排序那枚 `cc < cc0` 换成 `<=` 当场报 %d 行——恰是相邻相等首码对数 %d；'
            u'把码表侧的 `<=` 换成 `<` 报 %d 行，因为码表本无重复码；一条 `!~ /^Etc\\//` 守卫同时守两个方向，'
            u'坏它则 %d 行齐发（＝表行数）而“no data for”归零；把表行原地复制一行，失败落在 stdout 而非 stderr'
            u'（%d 条发射里走 stdout 的有 %d 条，该格 exit %d ⇎ stderr %d 行 ⇎ stdout %d 行）——'
            u'只读 stderr 的调用方会看见“毫无诊断却失败”。'
            u'两层宽度也只在执行里：改死 zone.tab 的豁免串报 %d 行（住在第 %d 行前一行、报在第 %d 行，全表 %d 行仅此一处），'
            u'改死 backward 的豁免串报 %d 行（Link 行本文件 %d 处，这条支路在当前配置下是死的）。'
            u'形状那三层照例分开: 口径 %s ⇎ 全文 %s ⇎ 磁盘 %s, 差成因不同（表 %d 枚非 ASCII 里 %d 枚住注释、字节差 %d；'
            u'数据 %d 枚每枚多一字节而差恰等于它）；注释有三种口径（行首 %d ⇎ 缩进 %d ⇎ 审计剔 %d），'
            u'复算时按行首过滤会得 %d 行非注释 ⇎ 照程序的定义 %d 行, 差的正是那 %d 行。'
            u'保留率 %s（字节口径 %s，三个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节）仍是对照条的必然读数：'
            u'最重的那几判（基线空输出、比较符容忍度、豁免权重、聚合型不变量的“最后一根支持者”）都不在任何窗口里。'
            % (ANCH, AK, AB_, NOCC, DIST, NLAB[u'T'], NLAB[u'C'], NLAB[u'Z'], GVER.split(u',')[0], NUM(u'data'),
               RUNS[u'base_zone1970.tab'][0], RUNS[u'base_zone1970.tab'][3],
               len(BAT), NTAB, NISO, NDATA, N12, NCRLF, NBASE, NREST, NWARN,
               RUNS[u'c_cc_lt'][1], EQ, BAT[u'c_iso_lt'][u'nerr'], RUNS[u'c_seen_off'][1],
               PR, POUT, BAT[u'd_duprow'][u'exit'], BAT[u'd_duprow'][u'nerr'], BAT[u'd_duprow'][u'nout'],
               BAT[u'c_exempt_dead'][u'nerr'], SIMROW, SIMVIOL, len(TNON),
               BAT[u'c_backward'][u'nerr'], len(LNK),
               fmt(RCOT(0)), fmt(RCOT(1)), fmt(RCOT(2)),
               NASC[0], NASC[0] - NASC_R[0], BYTES[0] - FULL[0], NASC[2],
               HASH0, IND, DROP[2], len(EL) + IND, len(EL), IND,
               b49_ret, b49_raw, fmt(RCOT_SUM), fmt(BYTES_SUM)))
        done.append(u'口径段')
        break
assert u'口径段' in done, u'口径段未命中'

GEN = (u'**B49 把对照轴换成表、检查这张表的程序与它检查的数据**：`raw/tz/zone1970.tab`（表, 口径内 %s 字符⇎全文 %d⇎磁盘 %d 字节, '
       u'被剔 %d/%d 行, 数据 %d 行＝四列 %d ⇎ 三列 %d, 首码相邻 相等 %d ⇎ 变大 %d ⇎ 变小 %d, 坐标 分形式 %d ⇎ 秒形式 %d ⇎ 不合 %d, '
       u'国家码引用 %d 次／去重 %d 种）⇎ `raw/tz/checktab.awk`（检查器, 口径内 %s⇎%d⇎%d——纯 ASCII 故字符＝字节, 被剔 %d/%d 行, '
       u'printf %d 条 ⇎ 拼全字面量后的诊断文本 %d 种 ⇎ 置失败码 %d 条 ⇎ 走 stderr %d ⇎ 走 stdout %d ⇎ 带行号 %d ⇎ 只报名字 %d, '
       u'FS 赋值 %d 次 ⇎ 循环外 getline %d 处自建计数器）⇎ `raw/tz/europe`（数据, 口径内 %s⇎%d⇎%d, 被剔 %d/%d 行＝行首注释 %d ⇎ 缩进注释 %d ⇎ 空行 %d, '
       u'非注释 %d＝Zone %d ⇎ Rule %d ⇎ 续行 %d ⇎ Link %d, STDOFF 受检 %d 值全合, 规则名 定义 %d ⇎ 带字母 %d ⇎ 恰用一次 %d ⇎ 幻影键 %d）。'
       u'正文标注 %d 处／%d 个不同串（⟦T⟧ %d ⇎ ⟦C⟧ %d ⇎ ⟦Z⟧ %d；登记表 %d 条经 atomcheck 真跑全部命中, 其中 %d 条只登记未在正文引用）, 判词 %d 行, DERIV %d 键, '
       u'0 键展开 %d 处原语调用（CNT %d ⇎ CNTF %d ⇎ B49V %d ⇎ L %d ⇎ 文件级 %d）, 加法项三种口径 %d⇎%d⇎%d——朴素切多出 %d 段（字面量里的加号 %d ＋括号内的加号 %d）, 深度 0 切比生成侧项数多出 %d 段是若干项自身即和式; 运算符 %d 加⇎%d 减⇎%d 乘; 另有同值折等式 %d 组）。'
       u'关键结论: 检查器不产出文件, 它的全部输出是判决, 而干净运行的判决形态是空——本机 %s 对 %d 份数据跑 zone1970/tab 与 zone/tab 两份配置, '
       u'exit %d、两条流各 %d 字节; 因此每条不变量只能靠破坏来点名。电池共 %d 格（表侧 %d ⇎ 码表侧 %d ⇎ 数据侧 %d ⇎ 码侧 %d ⇎ CRLF %d ⇎ 基线 %d ⇎ 还原 %d ⇎ 警告开关 %d）, '
       u'逐条破坏的字符串一律取自真实行, 原料逐字节复制进临时目录: 排序宽容量在一枚比较符里——`cc < cc0` 换 `<=` 报 %d 行＝相邻相等首码 %d 对, '
       u'而整列字面乱序另有 %d 处（其首码无一例外全相等, 程序一行不报）, 码表侧 `<=` 换 `<` 报 %d 行; '
       u'第 4 列那条 iff 不变量两边违规各 %d ⇎ %d 而**余量 %d**（带注释却引用不足的行数为 0, 真分支从未被走到）; '
       u'一条 `!~ /^Etc\\//` 守卫坏掉 ⇒ %d 行齐发＝表行数而“no data for”归零; '
       u'原地复制表行的那格失败落在 stdout 而非 stderr（%d 条发射里走 stdout 的有 %d 条；该格 exit %d ⇎ stderr %d ⇎ stdout %d）; '
       u'豁免按调用配置分死活: 改死 zone.tab 特例报 %d 行（前一行住在第 %d 行、报第 %d 行, 全表 %d 行仅此一处需要它）⇎ 改死 backward 报 %d 行'
       u'（本文件 Link %d 处, 两个层面都是死的）。'
       u'三套账与两种宽度: 文本 %d 种 ⇎ 发射点 %d ⇎ 流向 %d＋%d, 带行号 %d ⇎ 只报名字 %d, 同一句“列数不对”在两条循环各写一次'
       u'（%d 与 %d 之差即全部来源）; 码表 %d 行里未被任何表行引用 %d 种, 而这笔账住在提示级——默认开关让整条支路 0 行, 打开后 stdout 多 %d 行且 exit 仍 %d。'
       u'字面层的两种分隔符在同一份数据里并存: Zone 行首 tab %d ⇎ 空格 %d, Rule %d ⇎ %d, 全靠 FS 换回空格被宽恕; '
       u'行首带制表符的线 %d＝续行 %d＋缩进注释 %d。注释的第三种口径: 行首 %d ⇎ 缩进 %d ⇎ 审计剔除 %d, '
       u'非注释按行首过滤数得 %d ⇎ 照程序的第一列定义 %d。')
for i, l in enumerate(R):
    if l.startswith(u'**B48 把对照轴换成输入、生成它的程序与程序的产物**'):
        R[i] = l + u'\n\n' + GEN % (
            fmt(RCOT(0)), FULL[0], BYTES[0], DROP[0], NLINES[0], len(ZR), len(C4), len(C3),
            EQ, GREAT, LESS, MINC, SECC, len(ZR) - MINC - SECC, len(CCREF), len(set(CCREF)),
            fmt(RCOT(1)), FULL[1], BYTES[1], DROP[1], NLINES[1], PR, TEXTS, ST_, RD_, POUT, WLINE, PR - WLINE,
            FSN, GLC,
            fmt(RCOT(2)), FULL[2], BYTES[2], DROP[2], NLINES[2], HASH0, IND, ZBLANK,
            len(EL), len(ZON), len(RUL), len(CON), len(LNK), len(SO), len(RDEF), len(LET),
            len([k for k in RDEF if USEC.get(k, 0) == 1]), len([k for k in USEC if k not in RDEF]),
            NOCC, DIST, NLAB[u'T'], NLAB[u'C'], NLAB[u'Z'], ANCH, UNCITED, GLOS, DERIV_KEYS,
            NLEAF, PCCNT, PCCNTF, PCB49, FAM[u'L'], NFILE,
            NAIVEPLUS, NDEP0, NTERM0, NAIVEPLUS - NDEP0, LITPLUS, DEEPLUS, NDEP0 - NTERM0,
            OPS[u'Add'], OPS[u'Sub'], OPS[u'Mult'], COIN,
            GVER.split(u',')[0], NUM(u'data'), RUNS[u'base_zone.tab'][0], RUNS[u'base_zone.tab'][3],
            len(BAT), NTAB, NISO, NDATA, N12, NCRLF, NBASE, NREST, NWARN,
            RUNS[u'c_cc_lt'][1], EQ, NAIVE, BAT[u'c_iso_lt'][u'nerr'],
            VMISS, SLACK, SLACK, RUNS[u'c_seen_off'][1], PR, POUT,
            BAT[u'd_duprow'][u'exit'], BAT[u'd_duprow'][u'nerr'], BAT[u'd_duprow'][u'nout'],
            BAT[u'c_exempt_dead'][u'nerr'], SIMROW, SIMVIOL, len(TNON), BAT[u'c_backward'][u'nerr'], len(LNK),
            TEXTS, PR, RD_, POUT, WLINE, PR - WLINE, PR, TEXTS,
            len(ISOR), NUM(u'unref'), RUNS[u'c_warn_on'][2], RUNS[u'c_warn_on'][0],
            CNT(u'(?m)^Zone' + TAB, 2), CNT(u'(?m)^Zone ', 2), CNT(u'(?m)^Rule' + TAB, 2), CNT(u'(?m)^Rule ', 2),
            CNTF(u'(?m)^' + TAB, 2), len(CON), IND, HASH0, IND, DROP[2], len(EL) + IND, len(EL))
        done.append(u'B49 段')
        break
assert u'B49 段' in done, u'B49 段未命中'

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B48 | %s（新建' % fmt(b48_enc)):
        ins.append((i + 1, u'| B49 | %s（新建, 表⇎检查器⇎数据 %d 处标注／%d 个不同串（登记 %d 条锚全命中, %d 条未引用）: '
                           u'zone1970.tab ⟦T⟧ ⇎ checktab.awk ⟦C⟧ ⇎ europe ⟦Z⟧; '
                           u'最强一环是反向对照——程序的唯一产物是判决而干净运行两条流各 %d 字节, 于是 %d 格破坏逐格真跑取证; '
                           u'一个零键展开 %d 处原语调用（CNT %d ⇎ CNTF %d ⇎ B49V %d ⇎ L %d ⇎ 文件级 %d）, 加法项三口径 %d⇎%d⇎%d（前两差 %d＝字面量加号 %d＋括号内加号 %d, 后两差 %d＝项内和式）; 同值折等式 %d 组; '
                           u'排序宽容住在一枚比较符里: `cc < cc0` 换 `<=` 报 %d 行＝相邻相等首码 %d 对, 码表侧换 `<` 报 %d 行; '
                           u'报文三套账: 文本 %d 种 ⇎ 发射点 %d ⇎ 流向 stderr %d＋stdout %d, 错误可以走 stdout（原地复制一行: exit %d、stderr %d、stdout %d）; '
                           u'豁免按配置分死活: 改死 zone.tab 特例 %d 行 ⇎ 改死 backward %d 行; 一条守卫坏掉则 %d 行齐发＝表行数） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为表头字段名、awk 记号与数据行的列词） | %s | %s |'
                           % (fmt(b49_enc), NOCC, DIST, ANCH, UNCITED, RUNS[u'base_zone1970.tab'][3], len(BAT),
                              NLEAF, PCCNT, PCCNTF, PCB49, FAM[u'L'], NFILE,
                              NAIVEPLUS, NDEP0, NTERM0, NAIVEPLUS - NDEP0, LITPLUS, DEEPLUS, NDEP0 - NTERM0, COIN,
                              RUNS[u'c_cc_lt'][1], EQ, BAT[u'c_iso_lt'][u'nerr'],
                              TEXTS, PR, 14, 4, BAT[u'd_duprow'][u'exit'], BAT[u'd_duprow'][u'nerr'],
                              BAT[u'd_duprow'][u'nout'],
                              BAT[u'c_exempt_dead'][u'nerr'], BAT[u'c_backward'][u'nerr'],
                              RUNS[u'c_seen_off'][1],
                              NOCC, fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b49_ret, fmt(b49_dig))))
    elif l.startswith(u'| B48 | %s | %s' % (fmt(b48_enc), b48_ret)):
        ins.append((i + 1, u'| B49 | %s | %s | %s（字节口径; 三个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节——'
                           u'判词要在三份文件之间来回数（复算 ⇎ 执行 ⇎ 破坏），而摘要段只索引锚点触到的窗口，'
                           u'故保留率 %s 属对照条的必然读数，按“%d 键支撑 %d 行判词”来读；'
                           u'原料本身不小（表 %s 字符、检查器 %s、数据 %s 在口径内），'
                           u'但“程序替别的表写的豁免在当前配置下是死的”这一判既不在表里也不在数据里，只能执行出来；'
                           u'工具侧 %d 格破坏的原始输出写在 ⛓解读注, 不冒充机检） | %d | %s |'
                           % (fmt(b49_enc), b49_ret, b49_raw, fmt(RCOT_SUM), fmt(BYTES_SUM),
                              b49_ret, DERIV_KEYS, GLOS,
                              fmt(RCOT(0)), fmt(RCOT(1)), fmt(RCOT(2)), len(BAT),
                              b49_uniq, b49_cpu)))
    elif l.startswith(u'| B48 | `raw/tz/leap-seconds.list`'):
        ins.append((i + 1, u'| B49 | `raw/tz/zone1970.tab`（表, 口径内 %s 字符⇎全文 %d⇎磁盘 %d, 被剔 %d/%d 行, '
                           u'数据 %d 行＝四列 %d ⇎ 三列 %d, 首码相邻 %d/%d/%d, 坐标 %d⇎%d⇎%d, 引用 %d 次／%d 种）⇎ '
                           u'`raw/tz/checktab.awk`（检查器, 口径内 %s⇎%d⇎%d, 被剔 %d/%d 行, printf %d ⇎ 文本 %d ⇎ status %d ⇎ stderr %d ⇎ stdout %d, '
                           u'FS %d 次 ⇎ getline 读两张表 ⇎ 自建 NR）⇎ '
                           u'`raw/tz/europe`（数据, 口径内 %s⇎%d⇎%d, 被剔 %d/%d 行, 非注释 %d＝Zone %d ⇎ Rule %d ⇎ 续行 %d ⇎ Link %d, '
                           u'STDOFF %d 全合, 规则名 %d／%d／%d／幻影 %d） | 表 ⇎ 检查器 ⇎ 数据 ⇒ 定义权: '
                           u'基线空输出（exit %d、两条流各 %d 字节, %s）⇒ 证据只能靠破坏; '
                           u'散文版语法与运算符版用词交集为空（“当且仅当”⇎“单制表符”⇎“排序”⇎“最大城市”四句在表的口径内共 %d 处、在程序里共 %d 处）; '
                           u'排序有两层读数（相邻首码 相等 %d ⇎ 变大 %d ⇎ 变小 %d，而整列字面比较乱序另有 %d 处，其首码无一例外全相等）; '
                           u'iff 不变量两边违规 %d ⇎ %d 而余量 %d; 报文三套账 %d⇎%d⇎%d＋%d、定位符两宽度 %d⇎%d; '
                           u'聚合型不变量只能破坏最后一根支持者（改定义行 0 报 ⇎ 改唯一用法 %d 行, 只报名字）; '
                           u'豁免权重 %d ⇎ %d; 注释三口径 %d⇎%d⇎%d（按行首复算会多数 %d 行）; '
                           u'字节⇎字符⇎口径三层差成因各异（%d 枚非 ASCII 差 %d ⇎ %d 枚恰差 %d）; CRLF 不是不变量（%d 格改动后两条流全 %d 行） ⇒ '
                           u'哪一列合法、什么算有序、注释该不该在, 全由那 %d 行里的 %d 条发射与几枚比较符决定 |'
                           % (fmt(RCOT(0)), FULL[0], BYTES[0], DROP[0], NLINES[0], len(ZR), len(C4), len(C3),
                              EQ, GREAT, LESS, MINC, SECC, len(ZR) - MINC - SECC, len(CCREF), len(set(CCREF)),
                              fmt(RCOT(1)), FULL[1], BYTES[1], DROP[1], NLINES[1], PR, TEXTS, ST_, RD_, POUT,
                              FSN,
                              fmt(RCOT(2)), FULL[2], BYTES[2], DROP[2], NLINES[2], len(EL), len(ZON), len(RUL),
                              len(CON), len(LNK), len(SO), len(RDEF), len(LET),
                              len([k for k in RDEF if USEC.get(k, 0) == 1]),
                              len([k for k in USEC if k not in RDEF]),
                              RUNS[u'base_zone.tab'][0], RUNS[u'base_zone.tab'][3], GVER.split(u',')[0],
                              W0, W1, EQ, GREAT, LESS, NAIVE, VMISS, SLACK, SLACK,
                              TEXTS, PR, RD_, POUT, WLINE, PR - WLINE,
                              BAT[u'd_ruleletters'][u'nout'], BAT[u'c_exempt_dead'][u'nerr'],
                              BAT[u'c_backward'][u'nerr'], HASH0, IND, DROP[2], IND,
                              NASC[0], BYTES[0] - FULL[0], NASC[2], BYTES[2] - FULL[2], NCRLF, CRZERO,
                              NLINES[1], PR)))
    elif l.startswith(u'python -X utf8 corpus/_fill48.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_mkB49.py                # 建条目: 三色锚位(T=表／C=检查器／Z=被检查的数据), '
                    u'三口径、不看程序的复算与程序内部三套账全部由 raw 回算\n'
                    u'python -X utf8 corpus/_mkdigest3.py B49 <entry> T <raw/tz/zone1970.tab> 40 90 '
                    u'C <raw/tz/checktab.awk> 60 120 Z <raw/tz/europe> 40 120   # 三源分节摘要, 每源按命中锚各自分块; 空白折叠比对下正文 %d 处标注命中摘要段 %d 处(精确子串仅 %d 处——表行以制表符分列, 摘要另加缩进)\n'
                    u'python -X utf8 corpus/atomcheck.py B49 corpus/_atoms49.txt       # 登记 %d 条锚逐字回源 ok=%d bad=%d（正文标注 %d 处／%d 个不同串）\n'
                    u'python -X utf8 corpus/_probe49k.py             # 工具侧电池 %d 格: 原料逐字节复制进临时目录, 逐条破坏数据(%d)也逐条改坏程序(%d), '
                    u'外加 CRLF %d 格、基线 %d 格、还原 %d 格与警告开关 %d 格, 结果落 corpus/_b49battery.json\n'
                    u'python -X utf8 corpus/_fill49.py               # ⛓解读注: 每个工具侧数字取自那份电池, 不手填; '
                    u'形状数与执行数分栏, 其中换比较符一行 %d＝相邻相等首码 %d ⇎ 改死守卫一行 %d＝表行数 %d 两处两侧同数\n'
                    u'python -X utf8 corpus/_readme49.py             # 记账: 本脚本再把检查器真跑 %d 遍并与电池逐格对表, 故 README 里的执行断言不是转述'
                    % (NOCC, DIGHIT, EXACT, ANCH, AK, AB_, NOCC, DIST,
                       len(BAT), N17, N12, NCRLF, NBASE, NREST, NWARN,
                       RUNS[u'c_cc_lt'][1], EQ, RUNS[u'c_seen_off'][1], len(ZR), len(JOBS))))
assert len(ins) == 4, [x[1][:30] for x in ins]
for pos, txt in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt)
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if not l.startswith((u'| B48 |', u'**B48', u'B48 '))
        and re.search(u'48 条|B01\\.\\.B48|%s|516 条|%s|%s|%%s' % (
            re.escape(fmt(b48_enc)), re.escape(fmt(prev_in)), re.escape(fmt(prev_out))), l)]
print(u'README %d 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 摘要 %s 编码 %s 保留 %s 码点 %s 推导 %d 待核 %d｜'
      u'待核 0 的条目 %d 条｜第二代 %s／%s｜基线 %d 字节/流 换符 %d 行 坏守卫 %d 行'
      % (NENT, u'/'.join(done), len(left), fmt(dig_all), fmt(enc_all), ret_all, fmt(uniq_all), proofs,
         soft_all, len(ZSOFT), fmt(in_lat), fmt(out_lat),
         RUNS[u'base_zone1970.tab'][3], RUNS[u'c_cc_lt'][1], RUNS[u'c_seen_off'][1]))
for l in left:
    print(u'  ' + l[:150])
print(u'B49: enc %s dig %s ret %s raw %s uniq %d blocks %d cpu %s soft %d｜锚 %d(T %d/C %d/Z %d)/%d 串 标签 %d/%d/%d 判词 %d｜'
      u'DERIV %d 键, 0 键 %d 项(CNT %d/CNTF %d/B49V %d＝%d 次) 同值 %d 组｜'
      u'行 %s 剔 %s 口径 %s 全文件 %s 字节 %s 非ASCII %s/%s 制表 %s/%s｜'
      u'表 %d 四 %d 三 %d 首码 %d/%d/%d 乱 %d 坐标 %d/%d 引用 %d/%d 码表 %d 未引 %d｜'
      u'程序 printf %d 文本 %d 行号 %d/%d 流 %d/%d status %d｜数据 非注释 %d 缩进 %d 行首 %d 空 %d '
      u'Zone %d/%d/%d Rule %d/%d/%d 续 %d/%d STDOFF %d｜规则 %d/%d/%d 幻影 %d 全局 %d/%d/%d 月 %d/%d/%d｜'
      u'zone.tab %d Simferopol %d 报 %d｜电池 %d 格(数据 %d/码 %d/CRLF %d)｜gawk %s'
      % (fmt(b49_enc), fmt(b49_dig), b49_ret, b49_raw, b49_uniq, b49_blocks, b49_cpu, b49_soft,
         ANCH, ANCH_T, ANCH_C, ANCH_Z, UANCH, NLAB[u'T'], NLAB[u'C'], NLAB[u'Z'], GLOS,
         DERIV_KEYS, NTERM0, PCCNT, PCCNTF, PCB49, NPRIM0, COIN,
         NLINES, DROP, [RCOT(i) for i in range(3)], FULL, BYTES, NASC, NASC_R, ITAB, ITAB_R,
         len(ZR), len(C4), len(C3), EQ, GREAT, LESS, NAIVE, MINC, SECC,
         len(CCREF), len(set(CCREF)), len(ISOR), NUM(u'unref'),
         PR, TEXTS, WLINE, PR - WLINE, 14, 4, PLOG[6],
         len(EL), IND, HASH0, ZBLANK,
         len(ZON), CNT(u'(?m)^Zone' + TAB, 2), CNT(u'(?m)^Zone ', 2),
         len(RUL), CNT(u'(?m)^Rule' + TAB, 2), CNT(u'(?m)^Rule ', 2),
         len(CON), CNTF(u'(?m)^' + TAB, 2), len(SO),
         len(RDEF), len(LET), len([k for k in RDEF if USEC.get(k, 0) == 1]),
         len([k for k in USEC if k not in RDEF]), len(GD), len(GL), len(GM),
         len(set(t[5] for t in RUL if len(t) > 5)), len(GM), 12,
         len(TNON), SIMROW, SIMVIOL, len(BAT), N17, N12, NCRLF, GVER))
