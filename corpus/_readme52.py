# -*- coding: utf-8 -*-
"""README 记账: 51 条 → 52 条。合计数字全部由 audit 表、metrics 普查、四份 raw 回算与 _b52* 快照复算, 不手填。
B52 特有的一环: 本文件第四次把四份源量一遍——分层机器(组标签⇎数据行)、三层排序键、缩写闭合三口径、
集合差与四种粒度、检查器的字段引用、配方片段里的字面计数、锚的三口径与命中列都在此另写一份,
再与建条目侧扁平契约 `corpus/_b52flat.json`、审计器侧快照 `corpus/_b52audit.json` 逐键对表;
“组织键住在被跳过的那一层”“真值输入在库 0 份”这类断言因此是当场数出来的, 不是转述。"""
import collections, glob, io, json, os, re, subprocess, sys
import ast
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
t = io.open(F, encoding='utf-8').read()
NL = u'\n'
TAB = u'\t'
TAG, ENTRY = u'B52', u'corpus/babeltele/B52_perishable_table_vs_its_checker.md'
TZ = u'corpus/raw/tz'
PATHS = [u'%s/zonenow.tab' % TZ, u'%s/zone1970.tab' % TZ, u'%s/checknow.awk' % TZ, u'%s/Makefile' % TZ]
TAGS = [u'N', u'Z', u'K', u'M']
CN = [u'时效表', u'姊妹表', u'检查器', u'构建器']
RAWS = PATHS + [u'%s/zone.tab' % TZ]
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')

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
cells = lambda k: [x.strip() for x in row[k].split(u'|')]
b52, b51 = cells(u'B52'), cells(u'B51')
b52_dig, b52_enc, b52_ret, b52_raw, b52_uniq, b52_blocks, b52_cpu, b52_soft = (
    int(b52[0]), int(b52[1]), b52[2], b52[3], int(b52[4]), int(b52[5]), b52[6], int(b52[10]))
b51_enc, b51_ret = int(b51[1]), b51[2]
assert NENT == 52, NENT
assert b52_soft == 0 and not re.search(u'^\\s+B52 \\[', p.stdout, re.M), (b52, soft_all)
assert [int(x) for x in b52[7:10]] == [0, 0, 0], b52
assert b52_enc == json.load(io.open(u'corpus/_b52checks.json', encoding='utf-8'))[u'enc_chars'] \
    and b52_enc == 8044 and b52_dig == 3320
assert b52_ret == u'%.1f%%' % (100.0 * b52_enc / b52_dig)
PROOF_B52 = len(re.findall(u'^  \u2713 .*B52V\\(', p.stdout, re.M))
assert PROOF_B52 > 0 and not re.search(u'\u2717.*B52V\\(', p.stdout), PROOF_B52
ZSOFT = sorted([k for k in row if k != u'ALL' and int(cells(k)[10]) == 0], key=lambda x: int(x[1:]))
assert all(k in ZSOFT for k in (u'B45', u'B46', u'B47', u'B49', u'B50', u'B51', u'B52'))
assert u'B48' not in ZSOFT and len(ZSOFT) == 41, (len(ZSOFT), ZSOFT)

m = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/metrics.py'],
                   capture_output=True, text=True, encoding='utf-8')
cen = dict((mm.group(1), int(mm.group(2))) for mm in
           re.finditer(r'^\s{2}([A-Za-z\-]+)\s+([\d ]+)$', m.stdout, re.M))
assert len(cen) == 18, sorted(cen)

# ---------- 第四次独立测量: 四份源 + 第三表 ----------
TXT = [io.open(x, encoding='utf-8').read() for x in RAWS]
TTAB = TXT[0]
BY = [os.path.getsize(x) for x in RAWS[:4]]


def nn(x):
    """非空行序列(与门槛同口径: 只看是否有非空白内容)。"""
    return [l for l in x.split(NL) if l.strip()]


LX = [nn(x) for x in TXT]
COM = [[l for l in LX[i] if l[0] == u'#'] for i in range(5)]
DAT = [[l for l in LX[i] if l[0] != u'#'] for i in range(5)]
R4 = {u'bytes': BY,
      u'chars': [len(x) for x in TXT[:4]],
      u'nonempty': [len(LX[i]) for i in range(4)],
      u'com': [len(COM[i]) for i in range(4)],
      u'dat': [len(DAT[i]) for i in range(4)],
      u'tabline': [sum(1 for l in LX[i] if TAB in l) for i in range(4)],
      u'nonascii': [sum(1 for c in TXT[i] if ord(c) > 127) for i in range(4)],
      u'nsrc': 4}

fld = lambda ls: [l.split(TAB) for l in ls]
D4 = [fld(DAT[i]) for i in range(4)]
TR = fld(DAT[4])
cnt = lambda rows, n: sum(1 for r in rows if len(r) == n)
R4[u'fldn4'] = cnt(D4[0], 4)
R4[u'fldz3'], R4[u'fldz4'] = cnt(D4[1], 3), cnt(D4[1], 4)
R4[u'fldt3'], R4[u'fldt4'] = cnt(TR, 3), cnt(TR, 4)
R4[u'nowrows'] = R4[u'rows'] = len(D4[0])
R4[u'zrows'], R4[u'trows'] = len(D4[1]), len(TR)

TAGRE = re.compile(u'^# ([-+]\\d\\d(?::\\d\\d)?)(?:/([-+]\\d\\d(?::\\d\\d)?))?(.*)$')


def o2m(o):
    sgn = -1 if o[0] == u'-' else 1
    hh, _, mm = o[1:].partition(u':')
    return sgn * (int(hh) + (int(mm) / 60.0 if mm else 0))


GRP = []
for i, l in enumerate(LX[0]):
    g = TAGRE.match(l)
    if g:
        rest = g.group(3)
        ab = u''
        if rest[:3] == u' - ':
            ab = rest[3:]
            ab = u'' if ab[0] == u'(' else ab.split(u' (')[0]
        GRP.append([l, g.group(1), g.group(2), ab, [], i])
idxs = [g[5] for g in GRP]
for k, g in enumerate(GRP):
    hi = idxs[k + 1] if k + 1 < len(idxs) else len(LX[0])
    g[4] = [r for r in fld([x for x in LX[0][g[5] + 1:hi] if x[0] != u'#'])]
assert len(GRP) == 91 and sum(len(g[4]) for g in GRP) == 91, (len(GRP), sum(len(g[4]) for g in GRP))
RO = [g[4][0] for g in GRP]
EXN = [r[2] for r in RO]
SEQ = [o2m(g[1]) for g in GRP]
OK = collections.Counter(SEQ)
R4.update({u'tags': len(GRP),
           u'grpmax': max(len(g[4]) for g in GRP),
           u'dupn': len(EXN) - len(set(EXN)),
           u'duptag': len(GRP) - len(set(g[0] for g in GRP)),
           u'inv': sum(1 for i in range(90) if SEQ[i] > SEQ[i + 1]),
           u'offkinds': len(OK), u'maxperoff': max(OK.values()),
           u'repeated': len([v for v in OK.values() if v > 1]),
           u'offpairkinds': len(set((g[1], g[2] or u'') for g in GRP)),
           u'dstg': sum(1 for g in GRP if g[2]), u'abg': sum(1 for g in GRP if g[3]),
           u'nonint': sum(1 for g in GRP if u':' in g[1] or u':' in (g[2] or u'')),
           u'minutes': len(set(g[1].split(u':')[1] for g in GRP if u':' in g[1]) |
                           set(g[2].split(u':')[1] for g in GRP if g[2] and u':' in g[2])),
           u'offfirst': SEQ[0], u'offlast': SEQ[-1],
           u'k2inv': sum(1 for i in range(90) if SEQ[i] == SEQ[i + 1] and GRP[i][2] and not GRP[i + 1][2])})
STEP = collections.Counter(round(o2m(g[2]) - o2m(g[1]), 2) for g in GRP if g[2])
R4[u'step1'], R4[u'step2'], R4[u'step05'], R4[u'stepneg1'] = STEP[1.0], STEP[2.0], STEP[0.5], STEP[-1.0]
K3P = [(GRP[i][3], GRP[i + 1][3]) for i in range(90)
       if GRP[i][1] == GRP[i + 1][1] and (GRP[i][2] or u'') == (GRP[i + 1][2] or u'')
       and GRP[i][3] and GRP[i + 1][3]]
R4[u'k3pairs'], R4[u'k3inv'] = len(K3P), sum(1 for a, b in K3P if a > b)

PAR = lambda s: re.findall(u'\\(([^()]*)\\)', s)
CMT = [r[3] for r in RO]
WT = [g for g in GRP if g[3]]
R4[u'withpar'] = sum(1 for g in GRP if PAR(g[4][0][3]))
R4[u'withfirst'] = R4[u'withpar']
R4[u'eqfirst'] = sum(1 for g in WT if g[3] == (PAR(g[4][0][3]) or [u''])[0])
R4[u'eqlast'] = sum(1 for g in WT if g[3] == (PAR(g[4][0][3]) or [u''])[-1])
R4[u'inany'] = sum(1 for g in WT if g[3] in PAR(g[4][0][3]))
GAP = [(g[4][0][2], g[3], PAR(g[4][0][3])) for g in WT if g[3] not in PAR(g[4][0][3])]
EXPZ = set(g[4][0][2] for g in GRP if u'until' in g[0])
R4.update({u'gaps': len(GAP), u'gapnopar': sum(1 for g in GAP if not g[2]),
           u'gaptense': sum(1 for g in GAP if g[0] in EXPZ),
           u'gapspace': sum(1 for g in GAP if g[2] and g[0] not in EXPZ and
                            u''.join(g[1].split()) in [u''.join(q.split()) for q in g[2]]),
           u'reverse': sum(1 for g in GRP if not g[3] and PAR(g[4][0][3])),
           u'nparen': sum(len(PAR(c)) for c in CMT), u'twopar': sum(1 for c in CMT if len(PAR(c)) > 1)})
assert R4[u'gapnopar'] + R4[u'gaptense'] + R4[u'gapspace'] == R4[u'gaps'], R4
ISO = re.compile(u'\\d{4}-\\d{2}-\\d{2}')
IL = [(l[0] == u'#', ISO.search(l).group(0), l) for l in LX[0] if ISO.search(l)]
R4.update({u'iso': len(IL), u'isoc': sum(1 for x in IL if x[0]), u'isod': sum(1 for x in IL if not x[0]),
           u'dateskinds': len(set(x[1] for x in IL)), u'expire': len([x for x in IL if u'until' in x[2] and x[0]]),
           u'until_n': len([x for x in IL if u'until' in x[2]]),
           u'untillines': len([x for x in IL if u'until' in x[2]]),
           u'bdyear': int([x[1] for x in IL if u'Eggert' in x[2]][0][:4]),
           u'predyear': int(re.findall(u'from (\\d{4}) on', TTAB)[0]),
           u'pred': len([l for l in LX[0] if u'agree from now on' in l]),
           u'pred70': len([l for l in LX[1] if u'agreed since 1970' in l]),
           u'nowon_n': TTAB.count(u'from now on'), u'nowon_k': TXT[2].count(u'from now on')})
BD = date(*[int(x) for x in [x[1] for x in IL if u'Eggert' in x[2]][0].split(u'-')])
UT = date(*[int(x) for x in [x[1] for x in IL if u'until' in x[2]][0].split(u'-')])
ZBD = date(*[int(x) for x in ISO.search([l for l in LX[1] if u'Eggert' in l][0]).group(0).split(u'-')])
R4[u'gapday'], R4[u'gapbir'] = (UT - BD).days, (ZBD - BD).days
R4[u'y1970_n'], R4[u'y1970_m'] = TTAB.count(u'1970'), TXT[3].count(u'1970')
R4[u'irr_n'] = TTAB.count(u'irrelevant')
R4[u'xx_n'], R4[u'xx_m'] = TTAB.count(u'XX'), TXT[3].count(u'XX')
R4[u'col1kind'] = len(set(r[0] for r in RO))
C4 = [r[3] for r in RO]
R4.update({u'c4_kind': len(set(C4)), u'c4semi': sum(1 for x in C4 if u';' in x),
           u'c4par': sum(1 for x in C4 if u'(' in x),
           u'c4both': sum(1 for x in C4 if u';' in x and u'(' in x)})
OFFSH = re.compile(u'(?<![0-9:+-.])[-+]\\d\\d(:\\d\\d)?(?![0-9])')
R4[u'rowoffcmt'] = sum(1 for r in RO if OFFSH.search(r[3]))
R4[u'rowoffzone'] = sum(1 for r in RO if OFFSH.search(r[2]))
R4[u'rowoffany'] = sum(1 for r in RO if any(OFFSH.search(x) for x in r[1:]))
R4[u'lead0'] = sum(1 for r in RO if re.search(u'[-+]0\\d', r[1]))
R4[u'lead0c'] = sum(len(re.findall(u'[-+]0\\d', r[1])) for r in RO)
LL = re.compile(u'^([-+]\\d+)([-+]\\d+)$')
R4[u'mixed'] = sum(1 for r in RO
                   if (len(LL.match(r[1]).group(1)[1:]) == 4) != (len(LL.match(r[1]).group(2)[1:]) == 5))
R4[u'cw11'] = sum(1 for r in RO if len(r[1]) == 11)
R4[u'cw15'] = sum(1 for r in RO if len(r[1]) == 15)

ZR = D4[1]
ZN = dict((r[2], r) for r in ZR)
NZ = [r for r in RO if r[2] in ZN]
TN = [r[2] for r in TR]
RN, RZ = set(EXN), set(ZN)
R4.update({u'shared': len(NZ), u'coordeq': sum(1 for r in NZ if r[1] == ZN[r[2]][1]),
           u'cceq': sum(1 for r in NZ if r[0] == ZN[r[2]][0]),
           u'only70': len(RZ - RN), u'onlytab': len(set(TN) - RN),
           u'zkind': len(set(r[0] for r in ZR)), u'zmulti': sum(1 for r in ZR if u',' in r[0]),
           u'dup70': len(ZR) - len(RZ),
           u'z4empty': sum(1 for r in ZR if len(r) < 4 or not r[3].strip()),
           u'z4has': sum(1 for r in NZ if len(ZN[r[2]]) > 3 and ZN[r[2]][3].strip())})
ZSQ = [r[0].split(u',')[0] for r in ZR]
R4[u'zinv'] = sum(1 for i in range(len(ZSQ) - 1) if ZSQ[i] > ZSQ[i + 1])


def PN(s):
    """本脚本自己的一份归一: 大小写、引号、连接号、空白与非常用字符。"""
    s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
    s = re.sub(u"[’'\"‘“”`´]+", u'', s)
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


def shg(rows, n=5):
    w = [x for r in rows for x in re.findall(u'[a-z0-9]+',
                                             (TAB.join(r) if isinstance(r, list) else r).lower())]
    return set(tuple(w[i:i + n]) for i in range(len(w) - n + 1))


R4.update({u'grainline': len(set(PN(TAB.join(r)) for r in RO) & set(PN(TAB.join(r)) for r in ZR)),
           u'graincoord': R4[u'coordeq'], u'grainzone': len(RN & RZ),
           u'grainc4': len(set(PN(r[3]) for r in RO) &
                           set(PN(r[3]) for r in ZR if len(r) > 3 and r[3].strip())),
           u'grainshang': len(shg(RO) & shg(ZR)), u'shn': len(shg(RO)), u'shz': len(shg(ZR)),
           u'sht': len(shg(TR)), u'sh3n': len(shg(RO, 3)), u'sh3c': len(shg(COM[0], 3)),
           u'sh3nc': len(shg(RO, 3) & shg(COM[0], 3)), u'sh2nc': len(shg(RO, 2) & shg(COM[0], 2)),
           u'sh3zc': len(shg(ZR, 3) & shg(COM[0], 3)), u'shself': len(shg(RO) & shg(COM[0])),
           u'z4kind': len(set(PN(r[3]) for r in ZR if len(r) > 3 and r[3].strip()))})
R4[u'c4eq'] = len(set(PN(r[3]) for r in RO) & set(PN(r[3]) for r in ZR if len(r) > 3 and r[3].strip()))

K = TXT[2]
KD = NL.join(LX[2])
R4.update({u'klines': len(LX[2]), u'kcom': len(COM[2]), u'kskip': len(re.findall(u'\\[\\^#\\]', KD)),
           u'kprintf': len(re.findall(u'printf "', KD)),
           u'kprintfk': len(set(re.findall(u'printf "([^"]*)"', KD))),
           u'kexit': len(re.findall(u'exit status', KD)), u'kstatus': len(re.findall(u'status = 1', KD)),
           u'kunset': len([v for v in (u'now', u'now_out', u'zdump_table')
                           if not re.search(u'^\\s*%s\\s*=' % v, KD, re.M)]),
           u'kzonedata': len(re.findall(u'zone_data\\[zone\\]', KD)),
           u'kzonenowd': len(re.findall(u'zonenow\\[data\\]', KD)),
           u'kident': len(re.findall(u'identical from now on', KD)),
           u'knodata': len(re.findall(u'no data', KD)),
           u'zdumptable_k': len(re.findall(u'\\bzdump_table\\b', KD)),
           u'kzdumpnow': len(re.findall(u'zdump-now', KD))})
for n, c in ((0, u'kref0'), (1, u'kref1'), (2, u'kref2'), (3, u'kref3'), (4, u'kref4')):
    R4[c] = len(re.findall(u'\\$%s(?![0-9])' % n, KD))
R4[u'kgtline'] = 1 + [i for i, l in enumerate(LX[2]) if u'getline <zdump_table' in l][0]
R4[u'kfsline'] = 1 + [i for i, l in enumerate(LX[2]) if l.strip().startswith(u'FS = ')][0]

MD = TXT[3]
ml = MD.split(NL)
a = [i for i, l in enumerate(ml) if l.startswith(u'now.ck:')][0]
b = [i for i in range(a + 1, len(ml)) if ml[i].strip() and ml[i][:1] not in u' \t#'][0]
BLKR = NL.join(ml[a:b])
PREQ = ml[a].split()[1:]
R4.update({u'mck': len(re.findall(u'^([\\w.]+\\.ck):', MD, re.M)),
           u'mprereq': len(PREQ),
           u'mprereqok': len([x for x in PREQ if os.path.exists(u'%s/%s' % (TZ, x))]),
           u'mmkdir': len(re.findall(u'mkdir \\$@d', BLKR)), u'mrm': len(re.findall(u'rm -fr \\$@d', BLKR)),
           u'mzic': len(re.findall(u'\\./zic -d \\$@d', BLKR)),
           u'mmvout': len(re.findall(u'mv \\$@\\.out \\$@', BLKR)),
           u'mawkcall': len(re.findall(u'-f checknow\\.awk', BLKR)),
           u'mtablearg': len(re.findall(u'-f checknow\\.awk zonenow\\.tab', BLKR)),
           u'mhorizons': len(re.findall(u'\\./zdump -i -t ', BLKR)),
           u'msysv': len(re.findall(u'SysVzone\\[', BLKR)), u'mfinds': len(re.findall(u'\\$\\(find ', BLKR)),
           u'mnontab': len(re.findall(u"! -name '\\*\\.tab'", BLKR)),
           u'mdollarnow': len(re.findall(u'\\$\\$now', BLKR)),
           u'myears': int(re.findall(u'^CHECK_NOW_FUTURE_YEARS = (\\d+)$', MD, re.M)[0]),
           u'mbig': int(re.findall(u'(\\d{4})\\+ years', MD)[0]),
           u'mckfiles': len(glob.glob(u'corpus/**/now.ck', recursive=True)),
           u'mzdfiles': len(glob.glob(u'corpus/raw/**/*zdump*', recursive=True)),
           u'zdumpnow_m': MD.count(u'zdump-now'), u'zdumptable_m': MD.count(u'zdump_table'),
           u'cknow_m': MD.count(u'checknow.awk'),
           u'selfname_n': TTAB.count(u'zone1970.tab'), u'selfname_z': TXT[1].count(u'zone1970.tab'),
           u'selfname_m': MD.count(u'zone1970.tab')})
R4[u'mprereqmiss'] = R4[u'mprereq'] - R4[u'mprereqok']
R4[u'msecs'] = R4[u'myears'] * 366 * 86400
R4[u'msecs365'] = R4[u'myears'] * 365 * 86400
R4[u'mdiff'] = R4[u'msecs'] - R4[u'msecs365']
R4[u'mratio'] = R4[u'mbig'] / R4[u'myears']
CROSS = [u'zdump_table', u'zdump-now.tab', u'zdump-1970.tab', u'from now on',
         u'agree from now on', u'irrelevant and ignored', u'XX', u'Pacific/Kiritimati',
         u'-1416-17042', u'+12:45/+13:45', u'zone1970.tab', u'zonenow.tab',
         u'checknow.awk', u'now.ck', u'until 2026-11-01']
FULLP = [PN(x) for x in TXT[:4]]
HITS = [sum(1 for i in range(4) if PN(c) in FULLP[i]) for c in CROSS]
R4.update({u'hitkinds': len(CROSS), u'hitsingle': sum(1 for h in HITS if h == 1),
           u'hitcross': sum(1 for h in HITS if h > 1), u'hitnone': sum(1 for h in HITS if h == 0)})

MM = json.load(io.open(u'corpus/_b52meas.json', encoding='utf-8'))
FLAT = json.load(io.open(u'corpus/_b52flat.json', encoding='utf-8'))
AA = json.load(io.open(u'corpus/_b52audit.json', encoding='utf-8'))
CH = json.load(io.open(u'corpus/_b52checks.json', encoding='utf-8'))
AM = CH[u'ameta']
HC = MM[u'meas'][u'hit']
assert list(HC) == CROSS and [(0 if v == u'—' else len(v)) for v in HC.values()] == HITS, (list(HC), HITS)
flat_ = lambda v: v if isinstance(v, list) else [v]
eqx = lambda a, c: [round(float(x), 2) for x in a] == [round(float(x), 2) for x in c]
KS = sorted(R4)
BAD4 = [(k, R4[k], FLAT.get(k)) for k in KS if k not in FLAT or not eqx(flat_(R4[k]), flat_(FLAT[k]))]
assert not BAD4, BAD4[:6]
INAA = [k for k in KS if k in AA]
BAD4A = [(k, R4[k], AA[k]) for k in INAA if not eqx(flat_(R4[k]), flat_(AA[k]))]
assert not BAD4A, BAD4A[:6]
N4, V4, NA4 = len(KS), sum(len(flat_(R4[k])) for k in KS), len(INAA)
AONLY = [k for k in AA if k not in FLAT]
NA_AONLY = len(AONLY)

# ---------- 锚: 三口径 ⇎ 命中列(本脚本第三份归一) ----------
md = io.open(ENTRY, encoding='utf-8').read()
ENC = re.search(u'## ⟪BabelTele⟫\n(.*?)\n\n## ⛓解读注', md, re.S).group(1)
DIG = re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\n\n## ⟪BabelTele', md, re.S).group(1)
body = ENC
CITES = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', body)
atoms = [a for _, a in CITES]
labels = [tg for tg, _ in CITES]
NOCC, DIST = len(atoms), len(set(atoms))
assert (NOCC, DIST) == (AM[u'anchor_total'], AM[u'anchor_distinct']) == (56, 50), (NOCC, DIST)
NLAB = collections.Counter(labels)
assert set(NLAB) == set(TAGS) and sum(NLAB.values()) == NOCC
REG = [x.rstrip(NL) for x in io.open(u'corpus/_atoms52.txt', encoding='utf-8') if x.strip()]
assert sorted(set(atoms)) == sorted(REG), (len(REG), DIST)
own = collections.OrderedDict()
for tg, a in CITES:
    own.setdefault(tg, [])
    if a not in own[tg]:
        own[tg].append(a)
ALLA = [a for t in TAGS for a in own[t]]
fold = lambda s: re.sub(u'\\s+', u' ', s).strip()
ex = sum(1 for t in TAGS for a in own[t] if a in TXT[TAGS.index(t)])
fo = sum(1 for t in TAGS for a in own[t] if fold(a) in fold(TXT[TAGS.index(t)]))
no_ = sum(1 for t in TAGS for a in own[t] if PN(a) in FULLP[TAGS.index(t)])
assert (ex, fo, no_) == (len(ALLA),) * 3, (ex, fo, no_)
HIT = [sum(1 for i in range(4) if PN(a) in FULLP[i]) for a in ALLA]
D1, D2, D3, D4_ = [HIT.count(k) for k in (1, 2, 3, 4)]
CHECKS = len(ALLA) * 4
assert (D1, D2 + D3, D4_, CHECKS) == (AM[u'anchor_single'], AM[u'anchor_cross'],
                                      AM[u'anchor_all4'], AA[u'checks']) == (43, 7, 0, 200), \
    (D1, D2, D3, D4_, CHECKS)
ac = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/atomcheck.py', u'B52', u'corpus/_atoms52.txt'],
                    capture_output=True, text=True, encoding=u'utf-8')
AK, AB_ = (int(x) for x in re.search(r'ok=(\d+) bad=(\d+)', ac.stdout).groups())
assert (AK, AB_) == (len(REG), 0), ac.stdout[-400:]

# ---------- DERIV 结构(从 audit.py 现读, 不手填) ----------
AUD = io.open(u'corpus/audit.py', encoding='utf-8').read()
st = AUD.index(u"DERIV['B52'] = ")
en = AUD.index(u"\nDERIV['", st + 10)
D52 = ast.literal_eval(AUD[AUD.index(u'{', st):en].strip().rstrip(u','))
DJ = json.load(io.open(u'corpus/_deriv52.json', encoding='utf-8'))
KEYS = len(D52)
assert KEYS == len(DJ) == CH[u'deriv_keys'], (KEYS, len(DJ))
ZERO = D52[u'0']
ZT = len(ZERO.split(u'+'))
assert ZT == CH[u'zero_terms'], (ZT, len(DJ[u'0'].split(u'+')))
FAMS = collections.Counter()
IDX = PLAIN = NRND = 0
for v in D52.values():
    for n in ast.walk(ast.parse(v, mode='eval')):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            FAMS[n.func.id] += 1
            if n.func.id == u'B52V':
                IDX += len(n.args) > 1
                PLAIN += len(n.args) == 1
            if n.func.id == u'round':
                NRND += 1
OPS = collections.Counter(type(n.op).__name__ for v in D52.values()
                          for n in ast.walk(ast.parse(v, mode='eval')) if isinstance(n, ast.BinOp))
CL = CH[u'collisions']
COLL = {}
for v, n in CL:
    COLL.setdefault(v, []).append(n)
NCG, NCV = len(COLL), len(CL)
ONEC = len(COLL.get(u'1', [])) + 1
assert NCG == 24 and NCV == 92 and ONEC == 21 and NCV == sum(len(v) for v in COLL.values()), (NCG, NCV)
UNREF_B52 = KEYS - PROOF_B52
ZPAIRS = set((k, int(i)) for k, i in re.findall(u"B52V\\('([a-z_0-9]+)',\\s*(\\d+)\\)", ZERO))
assert all(FLAT[k][i] == 0 for k, i in ZPAIRS if isinstance(FLAT.get(k), list)), \
    [q for q in ZPAIRS if isinstance(FLAT.get(q[0]), list) and FLAT[q[0]][q[1]]]

# ---------- 条目结构 ----------
GLOS = len([l for l in body.split(NL) if l.strip()])
NSKEL = len(re.findall(u'[①-⑳]', [l for l in body.split(NL) if l.startswith(u'∴')][0]))
NSTEP = len(re.findall(u'第[一二三四五六]步', body))
IN_LAT = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
OUT_ALL = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
TAG_LAT = len(labels)
OUT_LAT = OUT_ALL - TAG_LAT
BLOCKS = len(re.findall(u'### ⟦', DIG))
DL, EL = len(DIG.replace(NL, u'')), len(ENC.replace(NL, u''))
DIGHIT = len([a for a in atoms if fold(a) in fold(DIG)])
assert (BLOCKS, EL) == (4, b52_enc), (BLOCKS, EL)
RAW_SUM = sum(FLAT[u'chars'])
assert b52_raw == u'%.3f%%' % (100.0 * b52_enc / sum(FLAT[u'bytes'])), b52_raw

# ---------- 全库字母账 ----------
mm2 = re.search(u'第二代（B11–B51）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
                u'全库合计 \\*\\*([\\d ]+)／([\\d ]+)\\*\\*', t)
assert mm2, u'第二代行未命中'
prev_in, prev_out = int(mm2.group(1).replace(u' ', u'')), int(mm2.group(2).replace(u' ', u''))
FIRST_IN, FIRST_OUT = 121, 2195
assert prev_in + FIRST_IN == int(mm2.group(3).replace(u' ', u'')), mm2.group(3)
assert prev_out + FIRST_OUT == int(mm2.group(4).replace(u' ', u'')), mm2.group(4)
assert cen[u'Latin'] - prev_in - prev_out - FIRST_IN - FIRST_OUT == IN_LAT + OUT_ALL, (
    cen[u'Latin'], prev_in, prev_out, IN_LAT, OUT_ALL)
in_lat, out_lat = prev_in + IN_LAT, prev_out + OUT_ALL
OLD_PROOFS = int(re.search(u'当前 \\*\\*51 条语料／(\\d+) 条\\*\\*推导', t).group(1))
assert proofs == OLD_PROOFS + PROOF_B52, (OLD_PROOFS, proofs, PROOF_B52)

cen_s = (u'Latin %s · Han %s · Gen-Punct %s · Arrows %s · CJK-Punct %s · Fullwidth %s · Emoji %s · Math %s · '
         u'Greek %s · Misc-Symbols %s · Dingbats %s · Geometric %s · Hiragana %s · Katakana %s · '
         u'MathAlnum %s · EnclosedIdeo %s · EnclosedSuppl %s · Comb-Diacritic %s') % tuple(
    fmt(cen[k]) for k in [u'Latin', u'Han', u'Gen-Punct', u'Arrows', u'CJK-Punct', u'Fullwidth', u'Emoji',
                          u'Math', u'Greek', u'Misc-Symbols', u'Dingbats', u'Geometric', u'Hiragana',
                          u'Katakana', u'MathAlnum', u'EnclosedIdeo', u'EnclosedSuppl', u'Comb-Diacritic'])

S4 = u' ⇎ '.join(u'`raw/tz/%s`（%s ⟦%s⟧: %s 字节／非空 %d 行／数据 %d 行）'
                 % (os.path.basename(PATHS[i]), CN[i], TAGS[i], fmt(BY[i]),
                    R4[u'nonempty'][i], R4[u'dat'][i]) for i in range(4))
GR4 = u'%d⇎%d⇎%d⇎%d' % (R4[u'grainline'], R4[u'graincoord'], R4[u'grainzone'], R4[u'grainshang'])
LST = lambda k: u' ⇎ '.join(str(x) for x in R4[k])
PR = io.open(u'corpus/_probe52_run.txt', encoding='utf-8').read()
L2, L3, L4 = [x for x in PR.split(NL) if x[:2] in (u'二.', u'三.', u'四.')]
GF = (int(re.search(u'输出 (\\d+) 行全是', L2).group(1)),
      int(re.search(u'no data (\\d+) 行', L3).group(1)),
      int(re.search(u'identical from now on (\\d+) 行', L3).group(1)),
      int(re.search(u'合成的 (\\d+) 钟表', L4).group(1)),
      int(re.search(u'输出 (\\d+) 行', L4).group(1)),
      int(re.search(u'退出码 (\\d+)', L4).group(1)))
assert GF == (R4[u'dat'][0], R4[u'dat'][0] - 2, 1, R4[u'dat'][0], 0, 0), GF
assert [int(re.search(u'退出码 (\\d+)', x).group(1)) for x in (L2, L3)] == [1, 1], (L2, L3)

# ---------- 全库计数成对替换 ----------
PAIRS = [
 (u'共 **51 条**（`babeltele/B01..B51`）', u'共 **%d 条**（`babeltele/B01..B52`）' % NENT),
 (u'**PASS**（51 条）', u'**PASS**（%d 条）' % NENT),
 (u'当前 **51 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (OLD_PROOFS, OLD_PROOFS),
  u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs)),
 (u'第二代（B11–B51）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B52）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'新建的 B51 同样为空——它的小整数全在四源 × 四种粒度的矩阵上, 已折进 128 枚推导键（其中 108 枚被正文点名逐条打勾, '
  u'余 20 枚登记在同值折等里、由 _b51_scan 照样复算））未逐位核验，',
  u'新建的 B51 同样为空——它的小整数全在四源 × 四种粒度的矩阵上, 已折进 128 枚推导键（其中 108 枚被正文点名逐条打勾, '
  u'余 20 枚登记在同值折等里、由 _b51_scan 照样复算）；新建的 B52 同样为空——它的小整数全在四份源 × 四层文体的矩阵上, '
  u'已折进 %d 枚推导键（其中 %d 枚被正文点名逐条打勾, 余 %d 枚登记在同值折等里、由 _b52_scan 照样复算））未逐位核验，'
  % (KEYS, PROOF_B52, UNREF_B52)),
 (u'（其后 B45／B46／B47／B49／B50／B51 同样为 0；只有 B48 有 1 项，即上面那条条目号 48）',
  u'（其后 B45／B46／B47／B49／B50／B51／B52 同样为 0；只有 B48 有 1 项，即上面那条条目号 48）'),
 (u'是**待核列为 0** 的 40 条条目里最连续的十二条',
  u'是**待核列为 0** 的 %d 条条目里最连续的十二条' % len(ZSOFT)),
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
    if l.startswith(u'| **合计（51 条）**'):
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

KEYLINE = u'B51 把轴换成**同一台机器 ⇎ 同一道题的第二次抽签**'
for i, l in enumerate(R):
    if KEYLINE in l and l.rstrip().endswith(u'不是转述。'):
        R[i] = l.rstrip().rstrip(u'。；') + u'；' + (
            u'B52 把轴换成**一张表 ⇎ 判它的程序 ⇎ 它要的那份不存在的表**（登记 %d 条锚全部逐字回源 ok=%d bad=%d，'
            u'正文标注 %d 处／%d 个不同串，四个源标签 %s 各 %d–%d 条）：这条把“不可核”当成被写下来的事实——'
            u'把整张时效表撑起来的偏移值在它 %d 行数据的注释列与时区名列里各出现 %d/%d 次，'
            u'而检查器给注释层的待遇是 %d 枚“非注释才处理”的谓词，它从 ⟦K⟧⟨zone = $3⟩ 起笔只读第 3 列'
            u'（\\$3 %d 处 ⇎ 整行 \\$0 %d 处 ⇎ 第 1/2/4 列各 %d/%d/%d 次）；'
            u'写在注释里的三级排序键反过来全部可验且零违例（%d/%d/%d，第三级可比较相邻对 %d 组），'
            u'缩写闭合的三种口径给出同一个数（%d/%d/%d），缺口 %d 分三类（写法 %d ⇎ 时态 %d ⇎ 无括号 %d）；'
            u'两张表说的是同一批钟而“同一批”只到坐标与时区名为止：共有 %d 枚里坐标一致 %d ⇎ 国码一致 %d，'
            u'四种粒度的逐字复现 %s（⇎ 与第三表五词串 %d，而时效表数据层与它自己的注释层五词串共有 %d 枚）；'
            u'真值输入在库 %d 份 ⇎ 产物 %d 份 ⇎ 配方前置 %d 项实有 %d 项缺 %d 项 ⇎ 起点取自墙钟（\\$\\$now %d 处）'
            u'⇒ “从现在起一致”这一谓词不可由在库文件判定，本条把它写进判词而不写成待核，门槛里没有一项替它背书。'
            u'保留率 %s（字节口径 %s，四份源合计 %s 字符 ⇎ 磁盘 %s 字节）是对照条的必然读数：'
            u'窗口按锚点截取且把制表符折成空格（两份表原文 %d 行带制表符 ⇎ 窗口 %d 行），'
            u'而“穿层命中矩阵 %d 串（单层 %d ⇎ 多层 %d ⇎ 不中 %d）”要跨四层做集合运算才看得见；'
            u'“判词到底怎么走”只有把检查器真跑一遍才知道，本条为此现跑四遍 gawk（缺表→不返回、空表→%d 行 no data、'
            u'两钟表→%d 行 no data ⇎ %d 行 identical、%d 钟表全异→%d 行且退出码 %d），'
            u'这四遍依赖外部解释器与本机路径，所以只写在 ⛓解读注里、不进判词也不进门槛；'
            u'本脚本第四次独立测量这四份源（分层机器、三层排序键、闭合三口径、集合差与四种粒度、检查器与配方的字面计数、'
            u'锚的归一函数都在此另写一份，%d 组量 %d 枚值与建条目侧扁平契约逐键相等、其中 %d 枚另与审计器快照相等），'
            u'所以上面这些零不是转述。'
            % (len(REG), AK, AB_, NOCC, DIST, u'／'.join(TAGS), min(NLAB.values()), max(NLAB.values()),
               R4[u'rows'], R4[u'rowoffcmt'], R4[u'rowoffzone'], R4[u'kskip'],
               R4[u'kref3'], R4[u'kref0'], R4[u'kref1'], R4[u'kref2'], R4[u'kref4'],
               R4[u'inv'], R4[u'k2inv'], R4[u'k3inv'], R4[u'k3pairs'],
               R4[u'eqfirst'], R4[u'eqlast'], R4[u'inany'], R4[u'gaps'],
               R4[u'gapspace'], R4[u'gaptense'], R4[u'gapnopar'],
               R4[u'shared'], R4[u'coordeq'], R4[u'cceq'], GR4, R4[u'sht'], R4[u'sh3nc'],
               R4[u'mzdfiles'], R4[u'mckfiles'], R4[u'mprereq'], R4[u'mprereqok'], R4[u'mprereqmiss'],
               R4[u'mdollarnow'], b52_ret, b52_raw, fmt(RAW_SUM), fmt(sum(BY)),
               R4[u'tabline'][0] + R4[u'tabline'][1], 0,
               R4[u'hitkinds'], R4[u'hitsingle'], R4[u'hitcross'], R4[u'hitnone'],
               GF[0], GF[1], GF[2], GF[3], GF[4], GF[5], N4, V4, NA4))
        done.append(u'口径段')
        break
assert u'口径段' in done, u'口径段未命中'

GEN = (u'**B52 把对照轴换成一张时效表、检查这张表的程序、它要的那份不存在的输出表与调用它的构建配方**：'
       u'%s。同目录的 `zone.tab`（%d 行数据）与 `version` 只进集合与口径对照，不作锚源。'
       u'四份的注释⇎数据分层悬殊（注释 %s ⇎ 数据 %s，非空行 %s，带制表符的行 %s），只有表有“字段数”这件事：'
       u'时效表 %d/%d 行齐四列 ⇎ 姊妹表三列 %d ⇎ 四列 %d ⇎ 第三表 %d／%d；'
       u'时效表 %d 枚组标签与 %d 行数据严格 1:1，沿标签读下去偏移从 %+d 单调升到 %+d（逆序 %d 对），'
       u'偏移只有 %d 种却撑起 %d 组（同偏移最多 %d 组），而这个组织键在数据行的注释列出现 %d 次、在时区名列出现 %d 次。'
       u'正文标注 %d 处／%d 个不同串（%s；登记表 %d 条经 atomcheck 真跑全部命中），'
       u'判词 %d 行, 骨架 %d 条, 方法 %d 步, DERIV %d 键（%d 枚被正文点名逐条机检 ⇎ %d 枚只登记在同值折等里）, '
       u'0 键折 %d 项（三层逆序 ⇎ 偏移在数据列 ⇎ 国码一致 ⇎ 层内五词串 ⇎ zdump 表在库 ⇎ now.ck 在库 ⇎ '
       u'检查器说出表名 ⇎ 锚四源全中 ⇎ 锚错配 等）, 归一式 %d 枚（除 %d ⇎ 乘 %d ⇎ 加 %d）; '
       u'同值折等 %d 个值上共 %d 次登记（最扎眼的是值 1 由 %d 处不同事实共用）。'
       u'关键结论: 一张表的组织键、有效期与判据分别住在注释层、未来与库外三处, 三处都不在“可机检的现在”里, '
       u'而能机检的部分（排序、列口径、集合、闭合度）在本条全部交出零违例。'
       u'可核性分三档: 第一档 %d 枚推导进门槛; 第二档由集合运算得出（时效表 %d 枚时区名是姊妹表的真子集, '
       u'后者多 %d 枚 ⇎ 第三表多 %d 枚, 而反向一枚也不多）; 第三档“从现在起一致”不可由在库文件判定——'
       u'能判它的那份 zdump 表在库 %d 份、每次构建由配方现造现删（建 %d 次 ⇎ 删 %d 次）, '
       u'起点又取自构建当天的墙钟, 前瞻跨度 %d 年 ⇎ 注释自认 %d 年以上（差 %d 倍）, '
       u'秒数按 366 天取整 %d ⇎ 按 365 天 %d, 差 %d 秒恰为 %d 天。'
       u'同名不同层当场可数: %d 枚关键串按折叠后原样判一遍, 命中单层 %d ⇎ 多层 %d ⇎ 不中 %d; '
       u'姊妹表从不提名自己（体内 %d 次）⇎ 在时效表 %d 次 ⇎ 在构建器 %d 次, 而真值表名在检查器只有变量名 %d 次。'
       u'%d 条去重锚 × %d 份源＝%d 次成员检查里错配 %d 条, 命中列 单层 %d ⇎ 两层 %d ⇎ 三层 %d ⇎ 四源 %d——'
       u'归属由正文标签现推, 不由旁注文件说了算。'
       ) % (S4, R4[u'trows'], LST(u'com'), LST(u'dat'), LST(u'nonempty'), LST(u'tabline'),
            R4[u'fldn4'], R4[u'rows'], R4[u'fldz3'], R4[u'fldz4'], R4[u'fldt3'], R4[u'fldt4'],
            R4[u'tags'], R4[u'rows'], R4[u'offfirst'], R4[u'offlast'], R4[u'inv'],
            R4[u'offkinds'], R4[u'tags'], R4[u'maxperoff'], R4[u'rowoffcmt'], R4[u'rowoffzone'],
            NOCC, DIST, u' '.join(u'⟦%s⟧ %d' % (x, NLAB[x]) for x in TAGS), len(REG),
            GLOS, NSKEL, NSTEP, KEYS, PROOF_B52, UNREF_B52, ZT,
            NRND, OPS[u'Div'], OPS[u'Mult'], OPS[u'Add'], NCG, NCV, ONEC,
            PROOF_B52, R4[u'nowrows'], R4[u'only70'], R4[u'onlytab'],
            R4[u'mzdfiles'], R4[u'mmkdir'], R4[u'mrm'], R4[u'myears'], R4[u'mbig'], R4[u'mratio'],
            R4[u'msecs'], R4[u'msecs365'], R4[u'mdiff'], R4[u'mdiff'] // 86400,
            R4[u'hitkinds'], R4[u'hitsingle'], R4[u'hitcross'], R4[u'hitnone'],
            R4[u'selfname_z'], R4[u'selfname_n'], R4[u'selfname_m'], R4[u'zdumptable_k'],
            DIST, 4, CHECKS, AM[u'anchor_err'], D1, D2, D3, D4_)

for i, l in enumerate(R):
    if l.startswith(u'**B51 把对照轴换成同一台机器与同一道题的第二次抽签**'):
        R[i] = l + u'\n\n' + GEN
        done.append(u'B52 段')
        break
assert u'B52 段' in done, u'B52 段未命中'

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B51 | %s（新建' % fmt(b51_enc)):
        ins.append((i + 1, u'| B52 | %s（新建, 时效表⇎检查它的 awk⇎它要的那份不存在的 zdump 表 %d 处标注／%d 个不同串（登记 %d 条锚全命中）: '
                           u'四源四色锚位 zonenow.tab ⟦N⟧ ⇎ zone1970.tab ⟦Z⟧ ⇎ checknow.awk ⟦K⟧ ⇎ Makefile ⟦M⟧; '
                           u'最强一环是“组织键住在被跳过的那一层”: %d 枚组标签撑起 %d 行（逆序 %d ⇎ %d ⇎ %d）而该键在数据列出现 %d 次, '
                           u'检查器只读第 3 列（\\$3 %d 处 ⇎ \\$0 %d 处 ⇎ 第 1/2/4 列 %d/%d/%d 次）+ %d 枚非注释谓词整层跳过注释; '
                           u'缩写闭合三口径 %d/%d/%d, 缺口 %d 分三类 %d⇎%d⇎%d; '
                           u'真值输入在库 %d 份 ⇎ 产物 %d 份 ⇎ 配方前置缺 %d 项 ⇎ 起点取自墙钟 %d 处 ⇒ 判词不可由在库文件判定, 本条如实写成判词而不假装机检; '
                           u'DERIV %d 键（正文点名 %d ⇎ 仅登记 %d）, 0 键折 %d 项, B52V %d 次（带格号 %d ⇎ 标量 %d）, 归一式 %d 枚; 同值折等 %d 组; '
                           u'集合: 共有 %d 枚坐标一致 %d ⇎ 国码一致 %d, 四种粒度 %s ⇎ 与第三表 %d ⇎ 层内五词串 %d; '
                           u'穿层矩阵 %d 串 单层 %d ⇎ 多层 %d ⇎ 不中 %d（姊妹表自名 %d 次）; '
                           u'锚命中列 单层 %d ⇎ 两层 %d ⇎ 三层 %d ⇎ 四源 %d, 检查 %d 次错配 %d） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为记号名、字段引用与英文原词） | %s | %s |'
                           % (fmt(b52_enc), NOCC, DIST, len(REG),
                              R4[u'tags'], R4[u'rows'], R4[u'inv'], R4[u'k2inv'], R4[u'k3inv'], R4[u'rowoffcmt'],
                              R4[u'kref3'], R4[u'kref0'], R4[u'kref1'], R4[u'kref2'], R4[u'kref4'], R4[u'kskip'],
                              R4[u'eqfirst'], R4[u'eqlast'], R4[u'inany'], R4[u'gaps'],
                              R4[u'gapspace'], R4[u'gaptense'], R4[u'gapnopar'],
                              R4[u'mzdfiles'], R4[u'mckfiles'], R4[u'mprereqmiss'], R4[u'mdollarnow'],
                              KEYS, PROOF_B52, UNREF_B52, ZT, FAMS[u'B52V'], IDX, PLAIN, NRND, NCG,
                              R4[u'shared'], R4[u'coordeq'], R4[u'cceq'], GR4, R4[u'sht'], R4[u'sh3nc'],
                              R4[u'hitkinds'], R4[u'hitsingle'], R4[u'hitcross'], R4[u'hitnone'], R4[u'selfname_z'],
                              D1, D2, D3, D4_, CHECKS, AM[u'anchor_err'],
                              NOCC, fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b52_ret, fmt(b52_dig))))
    elif l.startswith(u'| B51 | %s | %s' % (fmt(b51_enc), b51_ret)):
        ins.append((i + 1, u'| B52 | %s | %s | %s（字节口径; 四份源合计 %s 字符 ⇎ 磁盘 %s 字节——'
                           u'判词要在同一套分区的四层文体（表 ⇎ 姊妹表 ⇎ 程序 ⇎ 配方）之间来回数“谁读得到哪一层”'
                           u'（分层机器 ⇎ 三层排序键 ⇎ 集合差 ⇎ 穿层矩阵），而摘要段只索引锚点触到的窗口并把制表符折成空格，'
                           u'故保留率 %s 属对照条的必然读数，按“%d 枚推导键支撑 %d 行判词”来读；'
                           u'原料本身极不均（四份 %s ⇎ %s ⇎ %s ⇎ %s 字节，注释 %s ⇎ 数据 %s 行），'
                           u'但最重的三判都不在任何窗口里：组织键住在被检查器整层跳过的那一层（偏移在数据列 %d 次 ⇎ 注释层 %d 枚组标签）、'
                           u'谓词的有效期住在未来（%d 处 until 条款 ⇎ 比落款晚 %d 天）、'
                           u'判它的那份真值住在库外（zdump 表 %d 份 ⇎ 每次构建现造现删 ⇎ 起点取自墙钟 %d 处）；'
                           u'“判词到底怎么走”只有真跑检查器才看得见（缺表不返回 ⇎ 空表 %d 行 no data ⇎ 两钟表 %d 行 identical ⇎ '
                           u'%d 钟表 %d 行且退出码 %d），这四遍依赖外部解释器与本机路径，慢且不可移植，'
                           u'只在 `corpus/_fill52.py` 里跑并如实注明，条目正文改用四份源上可复算的字面计数；'
                           u'工具侧第四套实现的比对（%d 组量 ⇎ %d 枚值，其中 %d 枚同时与审计器快照相等）写在 ⛓解读注与本脚本, 不冒充机检） | %d | %s |'
                           % (fmt(b52_enc), b52_ret, b52_raw, fmt(RAW_SUM), fmt(sum(BY)),
                              b52_ret, KEYS, GLOS,
                              fmt(BY[0]), fmt(BY[1]), fmt(BY[2]), fmt(BY[3]), LST(u'com'), LST(u'dat'),
                              R4[u'rowoffcmt'], R4[u'tags'], R4[u'expire'], R4[u'gapday'],
                              R4[u'mzdfiles'], R4[u'mdollarnow'], GF[0], GF[2], GF[3], GF[4], GF[5],
                              N4, V4, NA4, b52_uniq, b52_cpu)))
    elif l.startswith(u'| B51 | `raw/cot/math_subsets.md`'):
        ins.append((i + 1, u'| B52 | ' + S4 + u'（同目录另有 `zone.tab`（%d 行数据）与 `version` 两份, 只进集合与口径对照, 不作锚源） | '
                           u'一张表 ⇎ 判它的程序 ⇎ 它要的那份不存在的表 ⇒ 组织键住在被跳过的那一层: %d 枚组标签⇎%d 行数据严格 1:1, '
                           u'偏移 %+d→%+d 三级排序零违例（%d/%d/%d, 第三级可比较对 %d 组）, 而该键在数据列 %d 次; '
                           u'检查器读法: \\$3 %d ⇎ \\$0 %d ⇎ 其余列 %d/%d/%d, 真值取用 %d 处 ⇎ 输出文本建索引 %d 处, 判定动作 %d 类; '
                           u'集合与粒度: 共有 %d 枚坐标一致 %d ⇎ 国码一致 %d, 四种粒度 %s ⇎ 与第三表 %d ⇎ 层内五词串 %d; '
                           u'缩写闭合 %d/%d/%d, 缺口 %d（写法 %d ⇎ 时态 %d ⇎ 无括号 %d）, 反向 %d; '
                           u'时效: ISO 日期 %d 处全在注释层（数据 %d）⇎ 只有 %d 个取值 ⇎ %d 行带 until 条款 ⇎ 条款距本表落款 %d 天 ⇎ 姊妹表落款比本表落款晚 %d 天; '
                           u'构建器: 前瞻 %d 年 ⇎ 自认 %d+ 年（%d 倍）⇎ 366 天口径 %d 秒 ⇎ 365 天 %d 秒差 %d ⇎ 前置 %d 项缺 %d 项 ⇎ '
                           u'建 %d 删 %d ⇎ 真值在库 %d 份 ⇎ 起点取自墙钟 %d 处 ⇒ “从现在起一致”写进判词而不写成待核 |'
                           % (R4[u'trows'], R4[u'tags'], R4[u'rows'], R4[u'offfirst'], R4[u'offlast'],
                              R4[u'inv'], R4[u'k2inv'], R4[u'k3inv'], R4[u'k3pairs'], R4[u'rowoffcmt'],
                              R4[u'kref3'], R4[u'kref0'], R4[u'kref1'], R4[u'kref2'], R4[u'kref4'],
                              R4[u'kzonedata'], R4[u'kzonenowd'], R4[u'kprintfk'],
                              R4[u'shared'], R4[u'coordeq'], R4[u'cceq'], GR4, R4[u'sht'], R4[u'sh3nc'],
                              R4[u'eqfirst'], R4[u'eqlast'], R4[u'inany'], R4[u'gaps'],
                              R4[u'gapspace'], R4[u'gaptense'], R4[u'gapnopar'], R4[u'reverse'],
                              R4[u'iso'], R4[u'isod'], R4[u'dateskinds'], R4[u'untillines'],
                              R4[u'gapday'], R4[u'gapbir'],
                              R4[u'myears'], R4[u'mbig'], R4[u'mratio'], R4[u'msecs'], R4[u'msecs365'],
                              R4[u'mdiff'], R4[u'mprereq'], R4[u'mprereqmiss'],
                              R4[u'mmkdir'], R4[u'mrm'], R4[u'mzdfiles'], R4[u'mdollarnow'])))
    elif l.startswith(u'python -X utf8 corpus/_readme51.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_pick52.py                # 选锚: 每条锚由规则从四层(表⇎姊妹表⇎程序⇎配方)截出, 分层机器 ⇎ 三层排序键 ⇎ 集合差 ⇎ 四种粒度 ⇎ 穿层矩阵全部现算, 落 %d 条候选池(正文只用其中 %d 条)\n'
                    u'python -X utf8 corpus/_mkB52.py                 # 建条目: 四色锚位(N=时效表, Z=姊妹表, K=检查器, M=构建器), 零项折进一枚 0 键(%d 项), 同值冲突 %d 组逐个登记含义\n'
                    u'python -X utf8 corpus/_wire52.py                # 把 _B52 与 B52V 接进 audit.py(审计器侧另算一套), DERIV %d 键; 插门前先把扁平契约 %d 枚键与每条算式在扫描器上预演, 值不符当场停机\n'
                    u'python -X utf8 corpus/_mkdigest3.py B52 <entry> N <raw/tz/zonenow.tab> 40 90 Z ... K ... M ...   # 四源分节摘要(%d 节 ⇎ 窗口把制表符折成空格: 两份表原文 %d 行带制表符 ⇎ 窗口 0 行)\n'
                    u'python -X utf8 corpus/atomcheck.py B52 corpus/_atoms52.txt   # 登记 %d 条锚逐字回源 ok=%d bad=%d（正文标注 %d 处／%d 个不同串）\n'
                    u'python -X utf8 corpus/_fill52.py                # ⛓解读注: 三套实现对表(扁平 %d 键 ⇎ 审计器独有 %d 键) + 本注第四遍现取现算 %d 组 %d 值, 并把检查器真跑四遍(缺表挂起 ⇎ 空表 %d 行 no data ⇎ 两钟表同串 %d+%d ⇎ 全不同 %d 枚 %d 行且退出码 %d)\n'
                    u'python -X utf8 corpus/_readme52.py              # 记账: 本脚本再独立测量四份源(分层机器 ⇎ 三层排序键 ⇎ 闭合三口径 ⇎ 集合差与四种粒度 ⇎ 检查器与配方字面计数 ⇎ 锚归一函数皆另写一份), %d 组量 %d 枚值与两份快照逐键对表(%d 枚三边相等), 故 README 里的“零违例”与“在库 0 份”不是转述'
                    % (len(MM[u'pool']), DIST, ZT, NCG, KEYS, len(FLAT),
                       BLOCKS, R4[u'tabline'][0] + R4[u'tabline'][1],
                       len(REG), AK, AB_, NOCC, DIST,
                       len(FLAT), NA_AONLY, N4, V4, GF[0], GF[1], GF[2], GF[3], GF[4], GF[5],
                       N4, V4, NA4)))
assert len(ins) == 4, [x[1][:30] for x in ins]
for pos, txt_ in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt_)
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if not l.startswith((u'| B51 |', u'**B51', u'B51 '))
        and re.search(u'51 条|B01\\.\\.B51|%s|%s 条|%s|%s|%%s（新建|%%d 键' % (
            re.escape(fmt(b51_enc)), OLD_PROOFS, re.escape(fmt(prev_in)), re.escape(fmt(prev_out))), l)]
print(u'README %d 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 摘要 %s 编码 %s 保留 %s 码点 %s 推导 %d 待核 %d｜'
      u'待核 0 的条目 %d 条｜第二代 %s／%s｜三层逆序 %d/%d/%d 缺口 %d(%d+%d+%d) 闭合 %d/%d/%d｜'
      u'DERIV %d 键 点名 %d 未点名 %d 0 键 %d 项｜第四套 %d 组 %d 值(三边相等 %d 枚)'
      % (NENT, u'/'.join(done), len(left), fmt(dig_all), fmt(enc_all), ret_all, fmt(uniq_all), proofs,
         soft_all, len(ZSOFT), fmt(in_lat), fmt(out_lat),
         R4[u'inv'], R4[u'k2inv'], R4[u'k3inv'], R4[u'gaps'], R4[u'gapspace'], R4[u'gaptense'],
         R4[u'gapnopar'], R4[u'eqfirst'], R4[u'eqlast'], R4[u'inany'],
         KEYS, PROOF_B52, UNREF_B52, ZT, N4, V4, NA4))
for l in left:
    print(u'  ' + l[:150])
print(u'B52: enc %s dig %s ret %s raw %s uniq %d blocks %d cpu %s soft %d｜锚 %d 条 引用 %d 处 去重 %d 标签 %s｜'
      u'四源 字节 %s 非空 %s 数据 %s 注释 %s 制表行 %s｜组 %d 行 %d 逆序 %d 偏移 %d 种 最多 %d 组 键在数据列 %d'
      u'｜集合 共有 %d 坐标 %d 国码 %d only70 %d onlytab %d｜粒度 %s 串库 %d/%d/%d 层内 %d'
      u'｜检查器 行 %d printf %d exit %d \\$3 %d \\$0 %d FS 行 %d getline 行 %d zdump_table %d'
      u'｜配方 ck %d 前置 %d/%d/%d 建 %d 删 %d zic %d 调用 %d 表名 %d 墙钟 %d 年 %d/%d 秒 %d/%d/%d 在库 %d/%d'
      u'｜穿层 %d 单 %d 多 %d 无 %d 姊妹自名 %d/%d/%d'
      u'｜锚三口径 %d/%d/%d 检查 %d 命中列 1:%d 2:%d 3:%d 4:%d｜digest %d 节 含换行 %d 去换行 %d 编码 %d 窗口命中 %d'
      % (fmt(b52_enc), fmt(b52_dig), b52_ret, b52_raw, b52_uniq, b52_blocks, b52_cpu, b52_soft,
         len(REG), NOCC, DIST, u' '.join(u'%s:%d' % (x, NLAB[x]) for x in TAGS),
         [fmt(x) for x in BY], R4[u'nonempty'], R4[u'dat'], R4[u'com'], R4[u'tabline'],
         R4[u'tags'], R4[u'rows'], R4[u'inv'], R4[u'offkinds'], R4[u'maxperoff'], R4[u'rowoffcmt'],
         R4[u'shared'], R4[u'coordeq'], R4[u'cceq'], R4[u'only70'], R4[u'onlytab'],
         GR4, R4[u'shn'], R4[u'shz'], R4[u'sht'], R4[u'sh3nc'],
         R4[u'klines'], R4[u'kprintf'], R4[u'kexit'], R4[u'kref3'], R4[u'kref0'],
         R4[u'kfsline'], R4[u'kgtline'], R4[u'zdumptable_k'],
         R4[u'mck'], R4[u'mprereq'], R4[u'mprereqok'], R4[u'mprereqmiss'],
         R4[u'mmkdir'], R4[u'mrm'], R4[u'mzic'], R4[u'mawkcall'], R4[u'mtablearg'], R4[u'mdollarnow'],
         R4[u'myears'], R4[u'mbig'], R4[u'msecs'], R4[u'msecs365'], R4[u'mdiff'],
         R4[u'mzdfiles'], R4[u'mckfiles'],
         R4[u'hitkinds'], R4[u'hitsingle'], R4[u'hitcross'], R4[u'hitnone'],
         R4[u'selfname_z'], R4[u'selfname_n'], R4[u'selfname_m'],
         ex, fo, no_, CHECKS, D1, D2, D3, D4_,
         BLOCKS, len(DIG), DL, EL, DIGHIT))
