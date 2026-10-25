# -*- coding: utf-8 -*-
"""B52 ⛓解读注: 只写工具侧现算的数, 每个数都由本脚本重新测一遍并 assert, 不手填。
四套实现: 采集侧 corpus/_pick52.py ⇎ 建条目侧 corpus/_mkB52.py(落扁平契约 corpus/_b52flat.json)
⇎ 审计器侧 corpus/audit.py::_b52_scan()(快照落 corpus/_b52audit.json) ⇎ 本注自己从四份 raw 现取的第三遍。
另: 第三档谓词“从现在起一致”只能现跑——本注用 gawk 按配方原话调用检查器四遍, 逐遍记账并落 corpus/_probe52_run.txt。"""
import ast, io, json, os, re, shutil, subprocess, sys
import glob as GL

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B52_perishable_table_vs_its_checker.md')
M = json.load(io.open(os.path.join(C, u'_b52meas.json'), encoding='utf-8'))
CH = json.load(io.open(os.path.join(C, u'_b52checks.json'), encoding='utf-8'))
DJ = json.load(io.open(os.path.join(C, u'_deriv52.json'), encoding='utf-8'))
FLAT = json.load(io.open(os.path.join(C, u'_b52flat.json'), encoding='utf-8'))
ATOMS = [x for x in io.open(os.path.join(C, u'_atoms52.txt'), encoding='utf-8').read().split(NL) if x.strip()]
MEAS, TAGS, PATHS = M[u'meas'], M[u'tags'], M[u'paths']
TABP = u'corpus/raw/tz/zone.tab'

# ---------- 审计器自己的快照 ----------
SNAP = os.path.join(C, u'_b52audit.json')
code = (u"import sys,json;sys.path.insert(0,'corpus');import audit;"
        u"json.dump(audit._B52, open(sys.argv[1],'w',encoding='utf-8'), ensure_ascii=False)")
r = subprocess.run([sys.executable, '-X', 'utf8', '-c', code, SNAP],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-800:]
AUDOUT = r.stdout
A = json.load(io.open(SNAP, encoding='utf-8'))

# ---------- 第一对齐: 扁平契约 ⇎ 审计器快照 ----------
aslist_ = lambda v: v if isinstance(v, list) else [v]
rnd = lambda v: [round(float(x), 4) for x in aslist_(v)]
DIFF = []
MISS = [k for k in sorted(FLAT) if k not in A]
for k in sorted(FLAT):
    if rnd(FLAT[k]) != rnd(A[k]):
        DIFF.append((k, FLAT[k], A[k]))
assert not MISS, MISS
assert not DIFF, DIFF
NF = len(FLAT)
NLIST = len([k for k in FLAT if isinstance(FLAT[k], list)])
VALS = sum(len(aslist_(v)) for v in FLAT.values())
AONLY = sorted(set(A) - set(FLAT))

# ---------- 第二对齐: 本注从四份 raw 现取的第三遍 ----------
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
T = [RD(p) for p in PATHS]
TABB = RD(TABP)
NB = lambda x: [l.rstrip(u'\r') for l in x.split(NL) if l.strip()]
LN = [NB(t) for t in T]
DATA = [[x for x in LN[i] if not x.startswith(u'#')] for i in range(4)]
COM = [[x for x in LN[i] if x.startswith(u'#')] for i in range(4)]
TLD = [x for x in NB(TABB) if not x.startswith(u'#')]
COL = lambda rows, n: [x for x in rows if len(x.split(u'\t')) > n]


def zonekey(rows, i=2):
    o = {}
    for x in rows:
        p = x.split(u'\t')
        if len(p) > i:
            o[p[i]] = p
    return o


NZ, ZZ, TZ_ = zonekey(DATA[0]), zonekey(DATA[1]), zonekey(TLD)
SH = sorted(set(NZ) & set(ZZ))
REC = []
_li = [i for i, x in enumerate(T[3].split(NL)) if x.startswith(u'now.ck:')][0]
for x in T[3].split(NL)[_li + 1:]:
    if not x.startswith(u'\t'):
        break
    REC.append(x)
RECR = u'\n'.join(REC)
KD = LN[2]
P3 = {}
P3[u'bytes'] = [os.path.getsize(p) for p in PATHS]
P3[u'chars'] = [len(x) for x in T]
P3[u'nonempty'] = [len(LN[i]) for i in range(4)]
P3[u'com'] = [len(COM[i]) for i in range(4)]
P3[u'dat'] = [len(DATA[i]) for i in range(4)]
P3[u'tabline'] = [sum(1 for x in LN[i] if u'\t' in x) for i in range(4)]
P3[u'nonascii'] = [sum(1 for ch in T[i] if ord(ch) > 127) for i in range(4)]
P3[u'fldn4'] = len(COL(DATA[0], 3))
P3[u'fldz3'] = len([x for x in DATA[1] if len(x.split(u'\t')) == 3])
P3[u'fldz4'] = len([x for x in DATA[1] if len(x.split(u'\t')) == 4])
P3[u'fldt3'] = len([x for x in TLD if len(x.split(u'\t')) == 3])
P3[u'fldt4'] = len([x for x in TLD if len(x.split(u'\t')) == 4])
P3[u'nowrows'] = len(NZ)
P3[u'zrows'] = len(ZZ)
P3[u'trows'] = len(TZ_)
P3[u'shared'] = len(SH)
P3[u'coordeq'] = len([z for z in SH if NZ[z][1] == ZZ[z][1]])
P3[u'cceq'] = len([z for z in SH if NZ[z][0] == ZZ[z][0]])
P3[u'only70'] = len(set(ZZ) - set(NZ))
P3[u'onlytab'] = len(set(TZ_) - set(NZ))
P3[u'xx_n'] = T[0].count(u'XX')
P3[u'until_n'] = T[0].count(u'until')
P3[u'irr_n'] = T[0].count(u'irrelevant')
P3[u'nowon_n'] = T[0].count(u'from now on')
P3[u'nowon_k'] = T[2].count(u'from now on')
P3[u'y1970_n'] = T[0].count(u'1970')
P3[u'y1970_m'] = T[3].count(u'1970')
P3[u'selfname_z'] = T[1].count(u'zone1970.tab')
P3[u'selfname_n'] = T[0].count(u'zone1970.tab')
P3[u'selfname_m'] = T[3].count(u'zone1970.tab')
P3[u'zdumptable_k'] = T[2].count(u'zdump_table')
P3[u'zdumpnow_m'] = T[3].count(u'zdump-now.tab')
P3[u'cknow_m'] = T[3].count(u'checknow.awk')
P3[u'iso'] = len(re.findall(u'\\d{4}-\\d{2}-\\d{2}', T[0]))
P3[u'isoc'] = len(re.findall(u'\\d{4}-\\d{2}-\\d{2}', u'\n'.join(COM[0])))
P3[u'klines'] = len(KD)
P3[u'kcom'] = len([x for x in KD if x.startswith(u'#')])
P3[u'kref0'] = len(re.findall(u'\\$0(?![0-9])', T[2]))
P3[u'kref3'] = len(re.findall(u'\\$3(?![0-9])', T[2]))
P3[u'kskip'] = T[2].count(u'[^#]')
P3[u'knodata'] = len([x for x in KD if u'no data' in x])
P3[u'kexit'] = len([x for x in KD if re.search(u'exit status', x)])
P3[u'kprintf'] = len(re.findall(u'printf', T[2]))
P3[u'kgtline'] = [i + 1 for i, x in enumerate(KD) if u'getline <zdump_table' in x][0]
P3[u'kfsline'] = [i + 1 for i, x in enumerate(KD) if re.search(u'^\\s*FS = ', x)][0]
P3[u'mmkdir'] = len([x for x in REC if u'mkdir $@d' in x])
P3[u'mrm'] = len([x for x in REC if u'rm -fr $@d' in x])
P3[u'mzic'] = len([x for x in REC if u'./zic -d $@d' in x])
P3[u'mmvout'] = len([x for x in REC if u'mv $@.out $@' in x])
P3[u'mdollarnow'] = RECR.count(u'$$now')
P3[u'mfinds'] = RECR.count(u'$(find ')
P3[u'mhorizons'] = len([x for x in REC if u'./zdump -i -t' in x])
P3[u'mawkcall'] = len([x for x in REC if u'-f checknow.awk' in x])
P3[u'mtablearg'] = len([x for x in REC if u'-f checknow.awk zonenow.tab' in x])
P3[u'mnontab'] = len([x for x in REC if u"! -name '*.tab'" in x])
P3[u'msysv'] = RECR.count(u'SysVzone[')
P3[u'myears'] = int(re.findall(u'CHECK_NOW_FUTURE_YEARS = (\\d+)', T[3])[0])
P3[u'mbig'] = int(re.findall(u'(\\d{4})\\+ years', T[3])[0])
P3[u'mratio'] = P3[u'mbig'] // P3[u'myears']
P3[u'msecs'] = eval(re.findall(u'CHECK_NOW_FUTURE_SECS = (.*)', T[3])[0].replace(u'$(CHECK_NOW_FUTURE_YEARS)',
                                                                               str(P3[u'myears'])).replace(u'$$', u''))
P3[u'msecs365'] = P3[u'myears'] * 365 * 24 * 60 * 60
P3[u'mdiff'] = P3[u'msecs'] - P3[u'msecs365']
P3[u'mprereq'] = len(re.findall(u'^now\\.ck: (.*)$', T[3], re.M)[0].split())
P3[u'mprereqmiss'] = len([p for p in re.findall(u'^now\\.ck: (.*)$', T[3], re.M)[0].split()
                         if not os.path.exists(u'corpus/raw/tz/' + p)])
P3[u'mck'] = len(re.findall(u'^([\\w.]+\\.ck):', T[3], re.M))
P3[u'mzdfiles'] = len(GL.glob(u'corpus/raw/**/*zdump*', recursive=True))
P3[u'mckfiles'] = len(GL.glob(u'corpus/**/now.ck', recursive=True))
P3[u'nsrc'] = len(PATHS)
BAD3 = [(k, P3[k], FLAT[k]) for k in sorted(P3) if rnd(P3[k]) != rnd(FLAT[k])]
assert not BAD3, BAD3
NT3 = len(P3)
VAL3 = sum(len(aslist_(v)) for v in P3.values())

# ---------- 第三档: 现跑检查器四遍 ----------
AWKBIN = shutil.which(u'gawk') or shutil.which(u'awk')
assert AWKBIN, u'no awk'
SC2 = u'TZ.now.ckd/America/Vancouver\n2026-01-01T00:00:00Z UTC +00 one\n' \
      u'TZ.now.ckd/America/Edmonton\n2026-01-01T00:00:00Z UTC +00 one\n'
io.open(os.path.join(C, u'_probe52_syn2.tab'), 'w', encoding='utf-8', newline=NL).write(SC2)
FL91 = []
for i, z in enumerate([NZ[k][2] for k in sorted(NZ)]):
    FL91.append(u'TZ.now.ckd/%s' % z)
    FL91.append(u'2026-%02d-%02dT00:00:00Z UTC +%02d seq%d' % (i % 12 + 1, i % 28 + 1, i % 14, i))
io.open(os.path.join(C, u'_probe52_full.tab'), 'w', encoding='utf-8', newline=NL).write(NL.join(FL91) + NL)
io.open(os.path.join(C, u'_probe52_empty.tab'), 'w', encoding='utf-8').write(u'')


def runk(tab, now_out=None, tmo=6):
    args = [AWKBIN, u'-v', u'zdump_table=' + tab, u'-v', u'now=1730000000']
    if now_out:
        args += [u'-v', u'now_out=' + now_out]
    args += [u'-f', u'corpus/raw/tz/checknow.awk', u'corpus/raw/tz/zonenow.tab']
    if now_out and os.path.exists(now_out):
        os.remove(now_out)
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=tmo,
                           encoding='utf-8', errors='replace')
        out = [x for x in p.stdout.splitlines() if x.strip()]
        return dict(exit=p.returncode, out=out, hang=False,
                    nowout=(len(NB(RD(now_out))) if now_out and os.path.exists(now_out) else 0))
    except subprocess.TimeoutExpired:
        return dict(exit=None, out=[], hang=True, nowout=0)


R1 = runk(u'corpus/_probe52_absent.tab')
R2 = runk(u'corpus/_probe52_empty.tab', now_out=u'corpus/_probe52_empty.out')
R3 = runk(u'corpus/_probe52_syn2.tab', now_out=u'corpus/_probe52_syn2.out')
R4 = runk(u'corpus/_probe52_full.tab', now_out=u'corpus/_probe52_full.out')
ND = lambda R: len([x for x in R[u'out'] if x.endswith(u': no data')])
ID = lambda R: len([x for x in R[u'out'] if u'identical from now on' in x])
MISS2 = [z for z in sorted(NZ) if z not in (u'America/Vancouver', u'America/Edmonton')]
assert R1[u'hang'] and R1[u'exit'] is None, R1
assert R2[u'exit'] == 1 and ND(R2) == FLAT[u'dat'][0] and ID(R2) == 0 and R2[u'nowout'] == 0, R2
assert R3[u'exit'] == 1 and ND(R3) == FLAT[u'dat'][0] - 2 and ID(R3) == 1 and R3[u'nowout'] == 1, R3
assert R4[u'exit'] == 0 and len(R4[u'out']) == 0, R4
assert len(MISS2) == ND(R3), (len(MISS2), ND(R3))
TR = (u'# B52 第三档现跑记录(由 corpus/_fill52.py 生成, gawk 版本见下)\n' +
      u'版本: ' + subprocess.run([AWKBIN, u'--version'], capture_output=True, text=True,
                              encoding='utf-8', errors='replace').stdout.splitlines()[0] + NL +
      u'调用一律为: ' + AWKBIN + u' -v zdump_table=<表> -v now=1730000000 [-v now_out=<旁出文件>] '
      u'-f corpus/raw/tz/checknow.awk corpus/raw/tz/zonenow.tab\n' +
      u'一. zdump_table 指向库里不存在的路径(=时效表此刻的真值输入状态, 库内 *zdump* 0 份): '
      u'6 秒内不返回, 强杀; 未打印任何行, 未创建旁出文件。原因在检查器自己的写法: '
      u'BEGIN 里是 while (getline <zdump_table), 文件打不开时 gawk 每次得 -1, 循环不退。\n' +
      u'二. zdump_table 为存在的空文件: 退出码 %d, 输出 %d 行全是“%%s: no data”, 旁出文件未创建。\n' % (
          R2[u'exit'], ND(R2)) +
      u'三. zdump_table 为合成的两钟表(America/Vancouver ⇎ America/Edmonton 从现在起同一串输出): '
      u'退出码 %d, no data %d 行 ⇎ identical from now on %d 行, 旁出文件 %d 行。\n' % (
          R3[u'exit'], ND(R3), ID(R3), R3[u'nowout']) +
      u'四. zdump_table 为合成的 91 钟表(每枚钟一串互不相同的输出): 退出码 %d, 输出 %d 行。\n' % (
          R4[u'exit'], len(R4[u'out'])) +
      u'结论: 检查器本身可用(四), 库内跑不出任何判词只因缺真值(一、二); 三说明它判的确实是“输出序列相同”。'
      u'合成表 corpus/_probe52_syn2.tab ⇎ corpus/_probe52_full.tab 是为本注现造的假数据, 不在四份源之列, 不进门槛。')
io.open(os.path.join(C, u'_probe52_run.txt'), 'w', encoding='utf-8', newline=NL).write(TR)
assert u'%%' not in TR

# ---------- 锚: 三口径 + 命中列 ----------
TT = io.open(ENTRY, encoding='utf-8').read()
ENC = re.search(u'## ⟪BabelTele⟫\\n(.*?)\\n\\n## ⛓解读注', TT, re.S).group(1)
DIG = re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', TT, re.S).group(1)
CITES = re.findall(u'⟦([NZKM])⟧⟨([^⟨⟩]+)⟩', ENC)
assert len(CITES) == CH[u'anchor_total'], (len(CITES), CH[u'anchor_total'])
norm_strict = lambda s: re.sub(u'\\s+', u' ', s).strip()


def pn(s):
    out = []
    for ch in s:
        t = ch.lower()
        for a, b in ((u'’', u"'"), (u'‘', u"'"), (u'“', u'"'), (u'”', u'"'), (u'´', u'')):
            t = t.replace(a, b)
        t = t.replace(u'"', u'').replace(u"'", u'')
        for d in u'‐‑‒–—―−':
            t = t.replace(d, u'-')
        for x in t:
            k = x if ((x.isalnum() and x.isascii()) or u'一' <= x <= u'鿿' or x in u' -.') else u' '
            if k != u' ' or (out and out[-1][0] != u' '):
                out.append((k, 0))
    return u''.join(c for c, _ in out)


FULLT = [RD(p) for p in PATHS]
SRCT = [norm_strict(x) for x in FULLT]
PNR = [pn(x) for x in FULLT]
own = dict((t, []) for t in TAGS)
for tg, a in CITES:
    if a not in own[tg]:
        own[tg].append(a)
ALLA = [a for t in TAGS for a in own[t]]
exact = sum(1 for t in TAGS for a in own[t] if a in FULLT[TAGS.index(t)])
folded = sum(1 for t in TAGS for a in own[t] if norm_strict(a) in SRCT[TAGS.index(t)])
normed = sum(1 for t in TAGS for a in own[t] if pn(a) in PNR[TAGS.index(t)])
assert normed == len(ALLA), (normed, len(ALLA))
assert len(set(ALLA)) == CH[u'anchor_distinct'] == len(ATOMS), (len(set(ALLA)), len(ATOMS))
HITN = [sum(1 for i in range(4) if pn(a) in PNR[i]) for a in ALLA]
DTHIT = [len([1 for h in HITN if h == k]) for k in (1, 2, 3, 4)]
AM = CH[u'ameta']
assert DTHIT[0] == AM[u'anchor_single'] and DTHIT[0] + DTHIT[1] + DTHIT[2] + DTHIT[3] == len(ALLA), DTHIT
assert DTHIT[3] == AM[u'anchor_all4'] and DTHIT[1] + DTHIT[2] == AM[u'anchor_cross'], (DTHIT, AM)
if exact == folded == normed == len(ALLA):
    TAIL = (u'三口径在这批上完全重合(锚全部落在原文自己的字形与排版上), 留三口径是为了换一批抓取时能立刻量出'
            u'引号/连接号/空白造成的失配条数。')
else:
    TAIL = (u'门槛按③判: ①比③少 %d 条、②比③少 %d 条, 差额来自原文混用的同形异码引号、破折号与制表符两侧空白'
            u'(不写口径就会把这类锚判成失配)。' % (normed - exact, normed - folded))
CROSSATOM = [a for a, h in zip(ALLA, HITN) if h > 1]

# ---------- 门槛 ----------
g = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
GT = g.stdout
GATE = re.search(u'保真门槛\\(T1 字面 \\+ T2 推导 \\+ T3 码位\\): (PASS|FAIL)', GT)
ROWS = len(re.findall(u'^\\| B\\d+ \\|', GT, re.M))
HINTS = int(re.search(u'提示\\(不计入 FAIL[^)]*\\): 共 (\\d+) 个', GT).group(1))
ROW = [l for l in GT.split(NL) if l.startswith(u'| B52 ')][0].split(u'|')
CELLS = [x.strip() for x in ROW[9:13]]
assert GATE and GATE.group(1) == u'PASS' and all(x == u'0' for x in CELLS), (GATE and GATE.group(0), CELLS, GT[-1500:])
PROOFS = len(re.findall(u'^  ✓ .*B52V' + chr(92) + u'(', GT, re.M))
assert PROOFS > 0 and not re.search(u'✗.*B52V' + chr(92) + u'(', GT), PROOFS
_A = io.open(u'corpus/audit.py', encoding='utf-8').read()
_st = _A.index(u"DERIV['B52'] = ")
_en = _A.index(u"\nDERIV['", _st + 10)
_D = ast.literal_eval(_A[_A.index(u'{', _st):_en].strip().rstrip(u','))
assert len(_D) == len(DJ) == CH[u'deriv_keys'], (len(_D), len(DJ))
UNREF = len(DJ) - PROOFS
ZT = len(DJ[u'0'].split(u'+'))
assert ZT == CH[u'zero_terms'], (ZT, CH[u'zero_terms'])

# ---------- 形状 ----------
COLL = {}
for v, n in CH[u'collisions']:
    COLL.setdefault(v, []).append(n)
BIG = sorted(COLL.items(), key=lambda x: -len(x[1]))[:4]
BLK = len(re.findall(u'### ⟦', DIG))
assert BLK == 4, BLK
DW, DL = len(DIG), len(DIG.replace(NL, u''))
DGL = len(DIG.split(NL))
EL = len(ENC.replace(NL, u''))
assert EL == CH[u'enc_chars'], (EL, CH[u'enc_chars'])
FULL4 = sum(FLAT[u'chars'])
TABSRC = sum(1 for x in DIG.split(NL) if u'\t' in x)
assert TABSRC == 0 and DIG.count(u'\t') == 0 and min(FLAT[u'tabline'][0], FLAT[u'tabline'][1]) > 0, \
    (TABSRC, FLAT[u'tabline'])
RAWSTR = u' ⇎ '.join(str(x) for x in FLAT[u'bytes'])

NOTE = u'''\
## ⛓解读注

**这四份数是怎么来的**: 时效表 `corpus/raw/tz/zonenow.tab` ⇎ 姊妹表 `zone1970.tab` ⇎ 检查器 `checknow.awk` ⇎ 构建配方 `Makefile`, 字节 {RAWSTR}; 同目录的 `zone.tab`(418 行数据)与 `version` 只进集合与口径对照, 不作锚源。同一个数由三套独立实现各算一遍再对齐: 采集侧 `corpus/_pick52.py`(落 `corpus/_b52meas.json`, 附候选锚池 {POOLN} 条供挑引文), 建条目侧 `corpus/_mkB52.py`(把要写进正文的每个数落成扁平契约 `corpus/_b52flat.json`, {NF} 枚键), 审计器侧 `corpus/audit.py::_b52_scan()`(只读四份 raw 与条目正文, 快照落 `corpus/_b52audit.json`)。
本注写这行时把三方又对齐了一次: 扁平契约 {NF} 枚键({NLIST} 枚是逐源列表, 合计 {VALS} 个标量)在审计器快照里逐键等值, 无一失配; 审计器另算 {AONLYN} 枚只它自己有的键({AONLY}), 其中锚统计由建条目侧从正文现推的 {NDIST} 条去重串独立对账。`corpus/_wire52.py` 在把扫描器插进门槛之前先跑这同一场对账, 不符就当场停机, 所以门槛里那份 `_b52_scan` 与正文里的数不会是两套口径。
第四遍是本注自己写的: 不读上面任何 JSON, 直接从四份 raw 现取现算 {NT3} 组量({VAL3} 个标量——字节、行、列、集合交差、词频、配方片段内的字面计数), 与扁平契约逐一对上; 三遍互不相读而结果相同, 才敢说这些数没有口径漂移。

**第三档: 只能现跑, 不能进门槛**: 正文里那句“从现在起一致”要靠一份 zdump 输出表来判, 而库里 `*zdump*` {MZF} 份、产物 `now.ck` {CKF} 份, 门槛只能数出这两个零。判词本身到底会怎么走, 只有把 `checknow.awk` 真的跑一遍才知道, 于是本注现跑四遍(`{AWKV}`, 记账落 `corpus/_probe52_run.txt`):
① 照配方的样子把 `zdump_table` 指到一个不存在的路径(= 此刻这份库的真实状态)——gawk {HANGT} 秒内不返回, 强杀, 一行判词都没打印: 检查器的 BEGIN 写的是 `while (getline <zdump_table)`, 文件打不开时每次得 -1, 循环根本不退。这是“缺真值”的第二个含义: 不是判不出, 而是连判都不启动。
② 换成存在的空表——退出码 {R2E}, 打印 {R2ND} 行“`%s: no data`”, 即 {DATAN} 枚钟一枚也没被看过; 旁出文件不创建。
③ 换成本注现造的两钟表(Vancouver ⇎ Edmonton 从现在起同一串输出, `corpus/_probe52_syn2.tab`)——退出码 {R3E}, `no data` {R3ND} 行(={DATAN}-{R3NDH}) ⇎ `identical from now on` {R3ID} 行, 旁出文件 {R3NO} 行。这一遍才看见它真正在比什么: 不是行与行的文字, 而是“输出序列的等价类”。
④ 换成 91 枚钟各一串互不相同输出的合成表(`corpus/_probe52_full.tab`)——退出码 {R4E}, 输出 {R4L} 行: 检查器本身完好, 库里跑不出判词纯粹因为缺那份真值输入。
这四遍依赖外部解释器与本机路径, 换机器就可能换结果, 所以一律不写进判词、不进门槛; 两份合成表是假数据, 不在四份源之列。

**锚的三口径**(正文“源标签紧接原子引文”的配对 {NAT} 处 ⇎ 跨标签去重 {NDIST} 条 ⇎ 候选清单 {NATOMS} 条, 每标签 {TAGN}):
① 连空格与字形都不改的逐字命中其标注那一层的 {EX}/{NA};
② 只折叠空白后命中 {FO}/{NA};
③ 再加撇号引号剔除、连接号归一与大小写归一(即 `audit.py` 的 `prose_norm`)后命中 {NO}/{NA}。{TAIL}
命中列分布(按③对四份源逐一判成员, 共 {CHK} 次检查): 恰落一层 {DS} 条 ⇎ 落多层 {DC} 条 ⇎ 四层全落 {D4} 条 ⇎ 错配 {DERR} 条。
“四层全落 = 0”是结构而不是巧合: 四份源是同一套分区的四层不同文体, 一条串若能同时落在表、姊妹表、awk 与配方里, 它必短到没有信息量; 反过来, 那 {DC} 条多层串({CROSSEX})正是“同名不同层”的实证——同一个 `zdump_table`、同一句 from now on、同一个表名在标签层、程序层与配方层各写一遍, 正文按标签分别引用, 归属由正文现推而不是由旁注文件说了算。

**三档可核性落在哪**: 第一档 {PROOFS} 枚推导在门槛里逐枚复算(本条 DERIV 共 {DK} 键, 其中 {UNREF} 枚登记着没有单独写成数字的量, 审计器照样复算它们), 四份源的字节/行/列口径、组标签机器的 1:1、三层排序键的逆序({INV3})、缩写闭合三口径({EQ3})、坐标两种宽度({CWW})、检查器与配方的每处计数都在这一档。第二档只能由集合运算得出: 时效表的 {NOWR} 枚时区名是姊妹表 `zone1970.tab` 的真子集(后者多 {ONLY70} 枚, 反向一枚也不多), 同样是 `zone.tab` 的子集(它多 {ONLYTAB} 枚); 两表与时效表共有的 {SH} 枚里坐标全同 {COORDEQ} 枚而国码全不同 {CCEQ} 枚; 四种粒度的共有量 {GR4}(依次是逐行 ⇎ 坐标 ⇎ 时区名 ⇎ 上行串)。第三档就是上面那四遍现跑——它与 B48/B49 的分界正在于此: B48 的产物可重建、B49 的不变量可回交机检, 本条的谓词既不入库又随墙钟漂移({DOLLARNOW} 处 `$$now`, 起点 {PREREQMISS} 项前置在库里缺着), 所以正文把它写成判词而不是待核项, 门槛里也没有一项替它背书。

**digest 侧**: 摘要段四节(`### ⟦标签⟧ ⟸ 文件`), 含换行 {DW} 字符(审计表“摘要段”一栏就是这个数), 去换行 {DL}; 编码区去换行 {EL}。于是“vs 摘要段”按表口径 {R1p} ⇎ 按两侧都去换行 {R2p}——两栏之差只是 {DNL} 枚换行的归属, 两个数在此都登记; 而编码区对四份源全文({FULL4} 字符)是 {R3p}。这个比例是本条的形状所在: 结论不住在窗口里——“组织键住在被跳过的那一层”“三级排序零违例”“缺口 {GAPS} 分三类”“真值输入在库 {MZF} 份”都要跨四层做集合运算才成立, 摘要窗口只装得下它们的引文证据, 而且窗口把制表符折成空格——{DGL} 行里带制表符的 {TABSRC} 枚, 两份表原文却有 {TABT} 行带制表符; 于是列结构在 digest 里根本看不见, 两种坐标宽度、组标签与三层排序键都只能靠编码区的引文加集合运算复算, 而不是靠读窗口看出来的。

**同一个数的不同含义**(同值冲突 {NCOLL} 次登记、铺在 {NCG} 个值上, DERIV 一个值只留一枚键, 所以下面这些说法在门槛里会互相顶掉, 只能靠注里的上下文区分): {BIGSTR}。最扎眼的是 {ONEN}, 上面那串键名翻成事实就是: 它在 {ONEC} 处不同的事实现场成立(半小时 DST 步长 1 组 ⇎ 两小时步长 1 组 ⇎ 一枚以上括号的行 1 处 ⇎ 非注释才处理的谓词 1 枚 ⇎ mkdir 1 次 ⇎ 表名在检查器里 1 次……)。零同样拥挤: `%s` 一枚键折 {ZT} 个零项(三层逆序 0 ⇎ 偏移出现在数据列 0 次 ⇎ 国码一致 0 ⇎ 层内五词串 0 ⇎ zdump 表在库 0 份 ⇎ now.ck 0 份 ⇎ 检查器里 “zdump-now” 0 次 ⇎ 锚四源全中 0 ⇎ 锚错配 0 等), 它们合起来才是本条最硬的一句“能判它的那份文件不存在”。

**跑法**: `python -X utf8 corpus/audit.py` ⇒ B52 行 T1 编码失配 {C0} ⇎ T2 原文失配 {C1} ⇎ T3 码位 {C2} ⇎ 小整数待核 {C3}; 门槛 {GATEV}, 全库 {ROWS} 条, 软提示 {HINTS} 枚。
`python -X utf8 corpus/atomcheck.py B52 corpus/_atoms52.txt` ⇒ ok={NATOMS} bad=0(工具侧独立实现的逐字校验)。
`python -X utf8 corpus/_wire52.py` 重复运行先摘旧块再插新块(幂等), 且插门前把扁平契约 {NF} 枚键与 DERIV {DK} 条算式在刚写好的扫描器上预演一遍, 值不符就当场停机。
`python -X utf8 corpus/_fill52.py` 即本注: 每次都重跑三遍对齐、四遍现跑与门槛, 所以这段里的数不是手填的, 也不能过期。
'''.format(
    RAWSTR=RAWSTR, POOLN=len(M.get(u'pool', [])), NF=NF, NLIST=NLIST, VALS=VALS,
    AONLYN=len(AONLY), AONLY=u'、'.join(u'`%s`' % k for k in AONLY),
    NDIST=CH[u'anchor_distinct'], NT3=NT3, VAL3=VAL3,
    MZF=FLAT[u'mzdfiles'], CKF=FLAT[u'mckfiles'],
    AWKV=subprocess.run([AWKBIN, u'--version'], capture_output=True, text=True,
                        encoding='utf-8', errors='replace').stdout.splitlines()[0],
    HANGT=u'6', R2E=R2[u'exit'], R2ND=ND(R2), DATAN=FLAT[u'dat'][0],
    R3E=R3[u'exit'], R3ND=ND(R3), R3NDH=2, R3ID=ID(R3), R3NO=R3[u'nowout'],
    R4E=R4[u'exit'], R4L=len(R4[u'out']),
    NAT=len(CITES), NATOMS=len(ATOMS), TAGN=u' '.join(u'%s:%d' % (t, CH[u'tag_counts'][t]) for t in TAGS),
    EX=exact, NA=len(ALLA), FO=folded, NO=normed, TAIL=TAIL,
    CHK=AM[u'checks'], DS=AM[u'anchor_single'], DC=AM[u'anchor_cross'], D4=AM[u'anchor_all4'],
    DERR=AM[u'anchor_err'], CROSSEX=u' ⇎ '.join(u'`%s`' % x for x in CROSSATOM[:6]) + (u' 等' if len(CROSSATOM) > 6 else u''),
    PROOFS=PROOFS, DK=len(DJ), UNREF=UNREF, INV3=u'%d/%d/%d' % (FLAT[u'inv'], FLAT[u'k2inv'], FLAT[u'k3inv']),
    EQ3=u'%d/%d/%d' % (FLAT[u'eqfirst'], FLAT[u'eqlast'], FLAT[u'inany']),
    CWW=u'%d⇎%d' % (FLAT[u'cw11'], FLAT[u'cw15']),
    ONLY70=FLAT[u'only70'], ONLYTAB=FLAT[u'onlytab'], SH=FLAT[u'shared'], COORDEQ=FLAT[u'coordeq'],
    NOWR=FLAT[u'nowrows'],
    CCEQ=FLAT[u'cceq'], GR4=u'%d⇎%d⇎%d⇎%d' % (FLAT[u'grainline'], FLAT[u'graincoord'], FLAT[u'grainzone'], FLAT[u'grainshang']),
    DOLLARNOW=FLAT[u'mdollarnow'], PREREQMISS=FLAT[u'mprereqmiss'],
    DW=DW, DL=DL, EL=EL, R1p=u'%.1f%%' % (100.0 * EL / DW), R2p=u'%.1f%%' % (100.0 * EL / DL),
    DNL=DW - DL, FULL4=FULL4, R3p=u'%.2f%%' % (100.0 * EL / FULL4), GAPS=FLAT[u'gaps'],
    TABSRC=TABSRC, NCOLL=len(CH[u'collisions']), NCG=len(COLL),
    BIGSTR=u'；'.join(u'值 %s 由 %d 处不同事实共用(%s)' % (v, len(ns) + 1, u'、'.join(ns[:6]) + (u'…' if len(ns) > 6 else u''))
                     for v, ns in BIG),
    ONEN=u'值 1', ONEC=len(COLL.get(u'1', [])) + 1, ZT=ZT,
    DGL=DGL, TABT=FLAT[u'tabline'][0] + FLAT[u'tabline'][1],
    C0=CELLS[0], C1=CELLS[1], C2=CELLS[2], C3=CELLS[3], GATEV=GATE.group(1), ROWS=ROWS, HINTS=HINTS)

assert u'{' not in NOTE and u'}' not in NOTE, [x for x in re.findall(u'[{}]', NOTE)][:2]
assert u'%s' not in (NOTE.replace(u'`%s: no data`', u'').replace(u'`%s` 一枚键折', u'')), u'未填的占位'
head = TT[:TT.index(u'## ⛓解读注')]
tail = TT[TT.index(u'## ⛓解读注'):]
cut = tail.find(u'\n\n## ', 1)
assert tail.startswith(u'## ⛓解读注')
rest = tail[cut + 1:] if cut >= 0 else u''
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(head + NOTE.rstrip(NL) + rest)
print(u'注已写 %s ｜ 三方对齐 扁平 %d 键/%d 值 + 审计器独有 %d 键 ｜ 第三遍 %d 组/%d 值 ｜ 现跑 4 遍(挂起/退出 1,91 行/退出 1,89+1/退出 0)' % (
    ENTRY, NF, VALS, len(AONLY), NT3, VAL3))
print(u'锚 三口径 %d⇎%d⇎%d ／%d ｜ 命中列 %s ｜ 门槛 %s 全库 %d 条 提示 %d ｜ 推导点名 %d／%d 键 ｜ digest %d 节 %d 字符 ⇎ 编码 %d(%.1f%%)' % (
    exact, folded, normed, len(ALLA), DTHIT, GATE.group(1), ROWS, HINTS, PROOFS, len(DJ), BLK, DL, EL, 100.0 * EL / DL))
