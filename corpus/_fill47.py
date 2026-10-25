# -*- coding: utf-8 -*-
"""B47 记账: ⛓解读注的每个数都在这里独立回算一遍(不读建条目那条路的任何中间变量), 不手填。
两个源: U=corpus/raw/UnicodeData.txt(逐码位定义表) ⇎ S=corpus/raw/scripts.txt(由它派生的脚本分类表)。
工具侧结论(展开算术、造名逐行核对、字节/sha/注释行)在这里重算并写进注里。"""
import io, re, sys, os, ast, hashlib, subprocess, collections

sys.stdout.reconfigure(encoding='utf-8')

TAG = u'B47'
ENTRY = u'corpus/babeltele/B47_definition_table_vs_derived_table.md'
RU = u'corpus/raw/UnicodeData.txt'
RS = u'corpus/raw/scripts.txt'
RAWS = [RU, RS]
LU, LS = u'U', u'S'
HEADRX = re.compile(u'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
NL = u'\n'
TOTAL = 0x110000


def reason(i):
    s = io.open(RAWS[i], encoding='utf-8', errors='replace').read()
    return NL.join(l for l in s.split(NL) if not HEADRX.match(l.strip()))


SRC = [reason(0), reason(1)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
CNTS = lambda pat, i: len(re.findall(pat, SRC[i]))          # 区分大小写
CNTF = lambda pat, i: len(re.findall(pat, io.open(RAWS[i], encoding='utf-8', errors='replace').read(), re.I))
RCOT = lambda i: len(SRC[i].strip())
L = lambda x: float(x.replace(u',', u''))

# ---------- 定义表侧 ----------
ROWU = u'(?m)^[0-9A-F]{4,6};'
EXACT14 = u'(?m)^(?:[^;\\n]*;){14}[^;\\n]*$'
AT15 = u'(?m)^(?:[^;\\n]*;){15}'
N_ROWU, N_SEMIU, N_E14 = CNT(ROWU, 0), CNT(u';', 0), CNT(EXACT14, 0)
assert (N_ROWU, N_SEMIU, N_E14, CNT(AT15, 0)) == (40575, 568050, 40575, 0)
assert CNT(u';Cn;', 0) == 0 and CNT(u'U\\+', 0) == 0 and CNT(u'_', 0) == 0
assert CNT(u'\\[\\d+\\]', 0) == 0 and CNT(u'\\.\\.', 0) == 0
N_EMPT4 = CNT(u'(?m);;;;$', 0)
assert N_EMPT4 == 37586
N_CTRL, N_CC = CNT(u'<control>', 0), CNT(u';Cc;', 0)
assert (N_CTRL, N_CC, CNT(u';Co;', 0)) == (65, 65, 6)
N_MN, N_LO, N_ND = CNT(u';Mn;', 0), CNT(u';Lo;', 0), CNT(u';Nd;', 0)
assert (N_MN, N_LO, N_ND) == (2059, 21759, 770)
N_LT_U, N_MARK = CNT(u'<', 0), CNT(u'<[^>]*, (?:First|Last)>', 0)
assert (N_LT_U, CNT(u'>', 0), N_MARK) == (3938, 3938, 40)
assert (CNT(', First>', 0), CNT(', Last>', 0)) == (20, 20)
assert (CNT(u'L&', 0), CNT(u';L&;', 0), CNT(u'; Han #', 0)) == (0, 0, 0)
assert (CNT(u'Han', 0), CNT(u'HYPHEN', 0), CNT(u';HYPHEN;', 0)) == (1391, 21, 1)
assert (CNT(u'LATIN', 0), CNT(u'SQUARED', 0)) == (1928, 372)
K4E00 = re.escape(u'CJK UNIFIED IDEOGRAPH-4E00')
assert (CNT(K4E00, 0), CNT(K4E00, 1)) == (1, 1)
assert (CNT(u'[^\x00-\x7f]', 0), CNT(u'[^\x00-\x7f]', 1), CNT(u'\t', 0), CNT(u'\t', 1)) == (0, 0, 0, 0)
assert (CNT(u'Unicode', 0), CNT(u'17\\.0\\.0', 0), CNT(u'Date:', 0)) == (0, 0, 0)
assert (CNTF(u'Unicode', 0), CNTF(u'17\\.0\\.0', 0), CNTF(u'Date:', 0)) == (0, 0, 0)
# 字段类分布(定义侧)
GC_U = collections.Counter()
NAME_U, MARK_U = {}, {}
for l in SRC[0].split(NL):
    m = re.match(u'^([0-9A-F]{4,6});([^;]*);([^;]*);', l)
    if m:
        GC_U[m.group(3)] += 1
        NAME_U[int(m.group(1), 16)] = m.group(2)
        mm = re.match(u'^<([^>]*), (First|Last)>$', m.group(2))
        if mm:
            MARK_U.setdefault(mm.group(1), {})[mm.group(2)] = int(m.group(1), 16)
assert sum(GC_U.values()) == 40575
print(u'gc_u kinds %d %s' % (len(GC_U), GC_U.most_common(5)))
assert len(MARK_U) == 20

# ---------- 派生表侧 ----------
ROWS_S = u'(?m)^[0-9A-F]{4,6}(?:\\.\\.[0-9A-F]{4,6})?[ \t]*;'
RANGE = u'(?m)^[0-9A-F]{4,6}\\.\\.[0-9A-F]{4,6}[ \t]*;'
SINGLE = u'(?m)^[0-9A-F]{4,6}[ \t]+;'
N_ROWS, N_RNG, N_SGL = CNT(ROWS_S, 1), CNT(RANGE, 1), CNT(SINGLE, 1)
assert (N_ROWS, N_RNG, N_SGL, CNT(u';', 1)) == (2287, 1460, 827, 2287)
assert (CNT(u'\\.\\.', 1), CNT(u'\\[\\d+\\]', 1)) == (2920, 1460)
H = lambda gc: u'# %s ' % gc
assert (CNT(H(u'L&'), 1), CNT(H(u'Mn'), 1), CNT(H(u'Lo'), 1), CNT(H(u'Nd'), 1), CNT(H(u'Cc'), 1)) == (157, 373, 557, 72, 2)
assert (CNT(u'; Common #', 1), CNT(u'; Inherited #', 1), CNT(u'; Latin #', 1)) == (613, 36, 61)
assert (CNT(u'_', 1), CNT(u'<', 1), CNT(u'HYPHEN', 1)) == (307, 4, 17)
assert (CNT(u'LATIN', 1), CNT(u'SQUARED', 1), CNT(u'; Common #', 1)) == (141, 4, 613)
assert (CNT(u'Unknown', 1), CNT(u'@missing', 1)) == (0, 0)
assert (CNTF(u'Unknown', 1), CNTF(u'@missing', 1), CNTF(u'Unicode', 1)) == (2, 1, 11)
assert (CNTF(u'17\\.0\\.0', 1), CNTF(u'Date:', 1)) == (1, 1)
NU_RC, NS_RC = RCOT(0), RCOT(1)
NU_FULL, NS_FULL = [len(io.open(p, encoding='utf-8', errors='replace').read()) for p in RAWS]
N_BYTES = [os.path.getsize(p) for p in RAWS]
SHA = [hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in RAWS]
DROPPED = [len(io.open(p, encoding='utf-8', errors='replace').read().split(NL)) -
           len(SRC[i].split(NL)) for i, p in enumerate(RAWS)]
assert (NU_RC, NS_RC, NU_FULL, NS_FULL) == (2198208, 178503, 2198209, 192458)
assert (N_BYTES[0], N_BYTES[1], NS_FULL - NS_RC, DROPPED[0], DROPPED[1]) == (2198209, 192460, 13955, 0, 368)
assert N_BYTES[0] == NU_FULL and N_BYTES[1] - NS_FULL == 2
RCOT_SUM = NU_RC + NS_RC
DROP_LINES = [l for l in io.open(RS, encoding='utf-8', errors='replace').read().split(NL) if l.strip().startswith(u'#')][:6]
DROPCH = [sum(len(l) + 1 for l in io.open(p, encoding='utf-8', errors='replace').read().split(NL)
               if HEADRX.match(l.strip())) for p in RAWS]
TAILWS = [len(SRC[i]) - len(SRC[i].strip()) for i in range(2)]
assert (DROPCH[0], TAILWS[0]) == (0, 1) and NU_FULL - NU_RC == TAILWS[0]
assert (DROPCH[1], TAILWS[1], DROPCH[1] + TAILWS[1]) == (13946, 9, NS_FULL - NS_RC), (DROPCH, TAILWS)

# ---------- 展开算术(与 audit 里 B47_* 那条路无关, 这里重摊一遍) ----------
PTS, SELFN, SCRIPTV, GC_S = set(), 0, set(), collections.Counter()
RROWS, SROWS = [], []
for l in SRC[1].split(NL):
    m = re.match(u'^([0-9A-F]{4,6})(?:\\.\\.([0-9A-F]{4,6}))?[ \t]*;', l)
    if not m:
        continue
    lo, hi = int(m.group(1), 16), int(m.group(2) or m.group(1), 16)
    PTS.update(range(lo, hi + 1))
    g = l.split(u'#')[0].split(u';')
    if len(g) > 1:
        SCRIPTV.add(g[1].strip())
    n = re.search(u'\\[(\\d+)\\]', l)
    if n:
        SELFN += int(n.group(1))
        RROWS.append((lo, hi, l))
    else:
        SELFN += 1
        SROWS.append((lo, hi, l))
    mm = re.search(u'# *([A-Za-z&]+) ', l)
    if mm:
        GC_S[mm.group(1)] += 1
ASSIGN, SCRIPTS, SELF = len(PTS), len(SCRIPTV), SELFN
UCODES = set(NAME_U)
NOROW, IN_UCD = len(PTS - UCODES), len(PTS & UCODES)
ONLY = sorted(UCODES - PTS)
assert (ASSIGN, SCRIPTS, SELF, NOROW, IN_UCD, len(ONLY)) == (159866, 174, 159866, 119303, 40563, 12)
assert IN_UCD + len(ONLY) == N_ROWU and ASSIGN - NOROW == IN_UCD
SPAN = sum(hi - lo + 1 for lo, hi, _ in RROWS) + len(SROWS)
assert SPAN == ASSIGN
COV, PEND = 0, {}
BLOCKS = []
for nm, d in MARK_U.items():
    COV += d[u'Last'] - d[u'First'] + 1
    BLOCKS.append((nm, d[u'First'], d[u'Last']))
assert COV == 258847 and len(BLOCKS) == 20
UNCOVERED = TOTAL - ASSIGN
assert UNCOVERED == 954246
MKEND = set()
for _nm, _a, _b in BLOCKS:
    MKEND.update((_a, _b))
ORPH = set(ONLY)
assert ORPH <= MKEND
ORPH_PAIRS = sorted(_nm for _nm, _a, _b in BLOCKS if _a in ORPH or _b in ORPH)
COVER_PAIRS = len([1 for _nm, _a, _b in BLOCKS if _a in PTS and _b in PTS])
assert (len(ORPH_PAIRS), COVER_PAIRS) == (6, 14)

# ---------- 造名逐行核对(工具侧) ----------
GCRX = re.compile(u'# *([A-Za-z&]+) *(?:\\[(\\d+)\\] *)?(.*)$')
sb = rb = 0
bad_rows, gen_pref = [], collections.Counter()
for l in SRC[1].split(NL):
    m = re.match(u'^([0-9A-F]{4,6})(?:\\.\\.([0-9A-F]{4,6}))?[ \t]*;[^#]*#', l)
    if not m:
        continue
    g = GCRX.search(l)
    lo, hi = int(m.group(1), 16), int(m.group(2) or m.group(1), 16)
    nm = g.group(3) if g else u''
    if hi == lo:
        if nm == NAME_U.get(lo):
            sb += 1
        else:
            bad_rows.append((u'single', format(lo, u'X'), nm, NAME_U.get(lo, u'?')))
    elif u'..' in nm:
        a, b = nm.split(u'..', 1)
        da, db = NAME_U.get(lo, u'?'), NAME_U.get(hi, u'?')
        if a == da and b == db:
            rb += 1
            continue
        for x, y in ((a, da), (b, db)):
            if x != y:
                mm = re.match(u'^(.*?)([0-9A-F]{4,6})$', x)
                if mm and mm.group(2) == format(lo if x == a else hi, u'X'):
                    gen_pref[mm.group(1)] += 1
        bad_rows.append((u'range', format(lo, u'X') + u'..' + format(hi, u'X'), a, da, b, db))
    else:
        bad_rows.append((u'range_noellipsis', format(lo, u'X'), nm))
assert sb == 827 and rb == 1446
NGEN = len([x for x in bad_rows if x[0] == u'range'])
assert (len(bad_rows), NGEN) == (14, 14)
CLS = collections.Counter()
for x in bad_rows:
    s = u'|'.join(x)
    CLS[u'control' if u'<control-' in s else u'hangul' if u'HANGUL SYLLABLE' in s else u'ideograph'] += 1
ONEEND = [x for x in bad_rows if (x[2] != x[3]) != (x[4] != x[5])]
assert CLS[u'control'] == 2 and CLS[u'hangul'] == 1 and CLS[u'ideograph'] == 11
assert len(ONEEND) == 1 and sum(gen_pref.values()) == 21
UND_CS, UND_CI = CNTS(u'UND', 0), CNT(u'UND', 0)
assert UND_CS == 406
CTRLGEN = u'<control-0000>..<control-001F>'
assert CNT(re.escape(CTRLGEN), 0) == 0 and CNT(re.escape(CTRLGEN), 1) == 1

# ---------- 与 audit 里那条 B47_* 路对表 ----------
au = io.open(u'corpus/audit.py', encoding='utf-8').read()
blk = re.search(u" 'B47': \\{\n(.*?)\n \\},", au, re.S).group(1)
VALS, EXPR = {}, {}
for m in re.finditer(r"^ {2}'([^']+)': (.*)$", blk, re.M):
    k = m.group(1)
    EXPR[k] = ast.literal_eval(m.group(2).strip().rstrip(u','))
    VALS[k] = float(k)
assert len(VALS) == 37
P2 = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)


def _rr(p):
    s = io.open(p, encoding='utf-8', errors='replace').read()
    return NL.join([l for l in s.split(NL) if not P2.match(l.strip())])


ENV = {u'CNT': CNT, u'L': L, u'RCOT': RCOT, u'round': round,
       u'B47_ASSIGN': lambda: ASSIGN, u'B47_NOROW': lambda: NOROW, u'B47_NOUCD': lambda: len(ONLY),
       u'B47_INUCD': lambda: IN_UCD, u'B47_MARKCOV': lambda: COV, u'B47_SELFN': lambda: SELF,
       u'B47_SCRIPTS': lambda: SCRIPTS}
for k, v in EXPR.items():
    got = float(eval(v, {}, ENV))
    assert abs(got - float(k)) < 1e-9, (k, got, v[:90])
NTERM0 = EXPR[u'0'].count(u'CNT(')


def split0(e):
    out, cur, depth, instr = [], u'', 0, False
    for c in e:
        if c == u"'":
            instr = not instr
        if not instr:
            if c == u'(':
                depth += 1
            elif c == u')':
                depth -= 1
            elif c == u'+' and depth == 0:
                out.append(cur)
                cur = u''
                continue
        cur += c
    out.append(cur)
    return [t.strip() for t in out if t.strip()]


NTERMS0 = len(split0(EXPR[u'0']))
BST = dict(l.split(u'\t') for l in io.open(u'corpus/_f47stats.txt', encoding='utf-8').read().split(NL) if u'\t' in l)
NABSEQ, NEQSEQ = int(BST[u'n_absent']), int(BST[u'n_equ'])
NTERMS0 = NABSEQ + NEQSEQ
assert len(split0(EXPR[u'0'])) >= NTERMS0 and NTERM0 >= NTERMS0
assert NEQSEQ + 1 < NTERM0
DIFFTERM = len([1 for k, e in EXPR.items() if k != u'0' and u'-' in re.sub(u"'[^']*'", u'', e)])
print(u'DERIV %d 键回算通过; 0 键 %d 项(缺席 %d + 等式 %d, CNT 原语 %d 次); 差值型键 %d'
      % (len(VALS), NTERMS0, NABSEQ, NEQSEQ, NTERM0, DIFFTERM))

# ---------- 条目结构 ----------
md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
labels = re.findall(u'⟦([US])⟧⟨', body)
uniq_atoms = sorted(set(atoms))
assert len(uniq_atoms) == 18
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
tag_lat = len(labels)
out_all = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
out_lat = out_all - tag_lat
enc = len(body.replace(NL, u''))
dig = len(re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\n\n## ⟪BabelTele', md, re.S).group(1))
lines = [l for l in body.split(NL) if l.strip()]
assert lines[0].startswith(u'🧭') and lines[-1].startswith(u'✂')
GLOS = len(lines)
NLU = dict((c, labels.count(c)) for c in u'US')
CROSS = len([a for a in uniq_atoms if CNT(re.escape(a), 0) > 0 and CNT(re.escape(a), 1) > 0])
assert (GLOS, CROSS) == (12, 0)
assert abs(enc - int(BST[u'body_chars'])) <= GLOS + 1

p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-800:]
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
b47 = [x.strip() for x in row[u'B47'].split(u'|')]
allr = [x.strip() for x in row[u'ALL'].split(u'|')]
assert int(b47[0]) == dig and int(b47[1]) == enc, (b47[:2], dig, enc)
uniq_cp, blocks, cpu, dens = int(b47[4]), int(b47[5]), b47[6], b47[3]
soft = int(b47[10])
assert soft == 0, soft
assert not re.search(u'^\\s+B47 \\[', p.stdout, re.M), u'B47 不该出现在待核清单'
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
prev = dict(l.split(u'\t') for l in io.open(u'corpus/_f46stats.txt', encoding='utf-8').read().split(NL) if u'\t' in l)
assert proofs > int(prev[u'proofs']), (proofs, prev[u'proofs'])

MEAN = {
 u'0': u'零值键: 缺席型 %d 项(定义侧: 未分配类 Cn、十五分号的行、裸点号、方括号自报、下划线、U+ 前缀、非 ASCII 码点、制表符、'
      u'“; Han #”“; Latin #”“; Common #”、L&(两个位置: 字段式与整体子串)、Co 式注释、造名的端点串(GREEK CAPITAL LETTER SHO.. 与 '
      u'<control-0000>..<control-001F>)、口径内的 Unicode/17.0.0/Date; 派生侧: U+ 前缀、Unicode 与版本与日期与 Scripts-17、'
      u'Unknown、@missing、非 ASCII 码点) + 等式与“恰好 N 处”型 %d 条(尖括号左右配平、First⇎Last 各 20、control⇎Cc 同为 65、'
      u'分号总数⇎十四倍行数、行数与数据行配平、两点号⇎两倍区间、方括号⇎区间、区间+单点⇎总行、分号⇎总行、'
      u'同一个 CJK UNIFIED IDEOGRAPH-4E00 两边各一处、若干“恰好一处”、定义行数⇎(在派生集内 + 集外)、自报和⇎展开和、'
      u'Copyright 两边同为 2)' % (NABSEQ, NEQSEQ),
 u'2': u'派生表里 Cc 式注释的行数(控制字符塌成两行) ⇎ 定义表逐位 65 行',
 u'4': u'派生表口径内的左尖括号数, 全在那两行造出来的控制名里 ⇎ 定义表 %d' % N_LT_U,
 u'6': u'定义表 Co 字段的行数(私有区标记端点), 派生表连 Co 式注释都没有',
 u'12': u'有定义行却不被任何脚本区间覆盖的码位数; 它们全是端点标记行, 出自 %s 这 6 对' % u'/'.join(
     x.replace(u' ', u'')[:3] for x in ORPH_PAIRS),
 u'17': u'HYPHEN 在派生表的命中数(全在名字列) ⇎ 定义表作字段恰好一处',
 u'20': u'端点标记配成的对数(First 与 Last 各 20 行, 等式折在 0 键)',
 u'21': u'HYPHEN 在定义表的子串命中数 ⇎ 作字段名恰好一处',
 u'36': u'“; Inherited #”的行数: 继承脚本被单列成一个值',
 u'40': u'定义表的端点标记行数(<X, First> 与 <X, Last>), 替 %d 个位置说话' % COV,
 u'61': u'“; Latin #”的行数 ⇎ LATIN 作子串在定义表 %d 处' % CNT(u'LATIN', 0),
 u'65': u'定义表 <control> 标记数, 恰等于 ;Cc; 的行数(等式在 0 键)',
 u'72': u'派生表 Nd 式注释行数 ⇎ 定义表 ;Nd; %d 行' % N_ND,
 u'157': u'派生表 L& 式注释行数——合成类, 定义表里既作字段 0 也作子串 0',
 u'174': u'派生表出现的脚本值个数(要展开行才能数全, 由审计器复算)',
 u'307': u'派生表的下划线数 ⇎ 定义表 0 处: 脚本值是标识符, 定义表没有这一列',
 u'373': u'派生表 Mn 式注释行数 ⇎ 定义表 ;Mn; %d 行' % N_MN,
 u'557': u'派生表 Lo 式注释行数 ⇎ 定义表 ;Lo; %d 行' % N_LO,
 u'613': u'“; Common #”的行数, 派生表最大的一个脚本值',
 u'770': u'定义表 ;Nd; 的行数',
 u'827': u'派生表单点行数(既没有两点号也没有方括号) ⇎ 区间行 %d' % N_RNG,
 u'1391': u'大小写折叠后 Han 作子串在定义表的命中数, 全在字符名里 ⇎ “; Han #”0 次',
 u'1460': u'派生表区间行数 ⇎ 方括号自报同为 %d ⇎ 两点号 %d = 两倍' % (CNT(u'\\[\\d+\\]', 1), CNT(u'\\.\\.', 1)),
 u'1928': u'LATIN 在定义表的子串命中数(字符名与分解字段) ⇎ 派生表 %d' % CNT(u'LATIN', 1),
 u'2059': u'定义表 ;Mn; 的行数',
 u'2287': u'派生表数据行数 = %d 区间 + %d 单点; 它的分号总数也恰好是这个数(每行一个)' % (N_RNG, N_SGL),
 u'2920': u'派生表两点号总数, 每区间行两次: 一次连码位, 一次连名字',
 u'3938': u'定义表左尖括号数(控制名标记、区间端点标记、兼容分解标记三种用途) ⇎ 派生表 %d' % CNT(u'<', 1),
 u'21759': u'定义表 ;Lo; 的行数, 也就是需要展开而不是逐行才能看完的那一类',
 u'37586': u'定义表以四个空字段收尾的行数(字段密度先于内容定出表的种类)',
 u'40575': u'定义表数据行数; 分号总数 %d 恰是它的十四倍' % N_SEMIU,
 u'119303': u'派生表归了类却没有定义行的码位数(住在 20 对端点之间)',
 u'159866': u'派生表展开后的被归类码位数 = 自报数之和 = 区间跨度之和(两条等式在 0 键)',
 u'178503': u'派生表审计口径内字符数(RCOT) ⇎ 全文件 %d ⇎ 磁盘 %d' % (NS_FULL, N_BYTES[1]),
 u'258847': u'20 对端点标记替多少个位置说话(要展开两端的差才知道)',
 u'568050': u'定义表分号总数 = %d 行 × 14 字段分隔' % N_ROWU,
 u'2198208': u'定义表审计口径内字符数(RCOT) ⇎ 全文件 %d ⇎ 磁盘 %d(纯 ASCII 才让后两者相等)' % (NU_FULL, N_BYTES[0]),
}
assert set(MEAN) == set(VALS), sorted(set(VALS) ^ set(MEAN))
ks = sorted(VALS, key=lambda x: float(x))
arith = u'；'.join(u'%s⇒%s' % (k, MEAN[k]) for k in ks if k != u'0')

T = []
T.append(u'※ 体例：本条两个源是**定义与被它派生的分类**——⟪UnicodeData.txt 逐码位定义表 ⇎ Scripts-17.0.0.txt 脚本分类表⟫。'
         u'锚位 %d 个(不同串 %d 个；标 %s 的 %d 个、标 %s 的 %d 个，平均长度 %d 字符——锚是整行，最长 %d、最短 %d)，'
         u'判词 %d 行，DERIV %d 键，0 键折了 %d 个加法项(缺席 %d 项、等式与“恰好 N 处” %d 项；这些项里 CNT 原语出现 %d 次)。'
         u'与上一条正好相反：B46 的两个源从没共享过任何一种连接键拼法，本条的连接键(裸十六进制码位)两边同一种拼法'
         u'(“U 加号”式前缀两边都 0 次)，可拼法一致仍接不住——派生侧归了类的 %d 个点里有 %d 个在定义侧根本没有行。'
         % (len(atoms), len(uniq_atoms), LU, NLU[LU], LS, NLU[LS],
            sum(len(a) for a in atoms) // len(atoms), max(len(a) for a in atoms), min(len(a) for a in atoms),
            GLOS, len(VALS), NTERMS0, NABSEQ, NEQSEQ, NTERM0, ASSIGN, NOROW))
T.append(u'※ 派生算术(键名即数值，表达式跑在两份原文上并逐个回算)：0⇒%s。%s。'
         u'%d 个键里减法式 %d 个，其余是直接计数或展开复算；所有等式与“恰好 N 处”都折进 0 键，因为键名就是数值，'
         u'两个同值的断言会抢同一个键。' % (MEAN[u'0'], arith, len(VALS), DIFFTERM))
T.append(u'※ 展开算术为什么交给函数：区间和自报数都能数，合起来覆盖多少点要摊开才知道。审计器里 B47_* 那几个函数复算出 '
         u'assigned %d ⇎ 无行 %d ⇎ 有行且在派生集内 %d ⇎ 无人认领 %d ⇎ 标记覆盖 %d ⇎ 脚本值 %d ⇎ 自报和 %d；'
         u'本注独立重摊一遍(不同的解析路径)，七个数全同。两条配平因此成立且在 0 键：'
         u'%d(定义行)= %d(派生集内) + %d(集外)，%d(派生点)= %d(有行) + %d(无行)。'
         u'更硬的是那 %d 个“有行无人认领”的码位：%s，它们一个不落地全是 <X, First>/<X, Last> 端点标记行，'
         u'出自 6 对标记(%s)，而另外 14 对标记的两端都被脚本区间覆盖——'
         u'也就是说：定义表只为“代理区与私有区”留下没人认领的端点，正是要按缺席来定义的那两处。'
         % (ASSIGN, NOROW, IN_UCD, len(ONLY), COV, SCRIPTS, SELF,
            N_ROWU, IN_UCD, len(ONLY), ASSIGN, IN_UCD, NOROW, len(ONLY),
            u' '.join(format(x, u'X') for x in ONLY), u' ⇎ '.join(ORPH_PAIRS)))
T.append(u'※ 派生表整体覆盖了多少：全集 %d 个码位里被区间点到 %d 个，剩下 %d 个位置没有任何数据行——'
         u'它们只由一句注释兜住(“# @missing: 0000..10FFFF; Unknown”)，那句是注释行，故口径内 Unknown 0 次 ⇎ 全文件 2 次、'
         u'@missing 0 次 ⇎ 全文件 1 次(这两个等式的口径内一半在 0 键，文件内一半只有工具能报)。'
         u'派生表注释里的类记号共 %d 种，前十种：%s；定义表字段里的类共 %d 种，前五种：%s。'
         u'两份表用的类字母表并不一样大：派生侧把三类字母并成 L&(注释 %d 行)，定义侧逐码位赋类时写不出它。'
         % (TOTAL, ASSIGN, UNCOVERED, len(GC_S),
            u' '.join(u'%s %d' % (k, v) for k, v in GC_S.most_common(10)), len(GC_U),
            u' '.join(u'%s %d' % (k, v) for k, v in GC_U.most_common(5)), CNT(H(u'L&'), 1)))
T.append(u'※ 造名逐行核对(工具侧，CNT 量不到，要按整行解析两份表)：单点行 %d 行的名字列与定义表该码位的名字**逐字相符 %d 行**；'
         u'区间行 %d 行两端都相符 %d 行，不相符 %d 行，且这 %d 行全部可归因于“造名”——按成因分：'
         u'控制类 %d 行(写成 <control-0000>..<control-001F> 那样，那一整串在定义表 0 次)、'
         u'音节类 %d 行(HANGUL SYLLABLE GA..HIH ⇎ 定义表两端是 <Hangul Syllable, First/Last>)、'
         u'汉字与表意文字类 %d 行(CJK UNIFIED IDEOGRAPH-xxxx.. 与 TANGUT IDEOGRAPH-xxxx..)；'
         u'造出的名字里“前缀 + 码位十六进制”这种拼法命中 %d 次，前缀分布 %s。'
         u'%d 行里只有一行是一端相符(17000..18AFF：右端 TANGUT COMPONENT-768 是定义表里的真名，左端才是造出来的)。'
         u'另有一行把三个定义块并成一个区间(31350..33479 左端是 Extension H 的 First、右端是 Extension J 的 Last)——'
         u'派生表的区间边界不按定义表的块边界走。没有一行不相符是解释不了的(0 行)，这是本条能给出的最强的一条“派生”证据。'
         % (N_SGL, sb, N_RNG, rb, NGEN, NGEN, CLS[u'control'], CLS[u'hangul'], CLS[u'ideograph'],
            sum(gen_pref.values()), u' '.join(u'%s×%d' % (k, v) for k, v in gen_pref.most_common()), len(bad_rows)))
T.append(u'※ 一台真数字的假阳性机器(子串 ⇎ 字段)：Han 作子串(大小写折叠)在定义表 %d 处 ⇎ “; Han #”0 处；'
         u'HYPHEN 作子串 %d ⇎ 作字段恰好 %d；LATIN %d ⇎ %d(两表)；SQUARED %d ⇎ %d；'
         u'最巧的一条是 CJK UNIFIED IDEOGRAPH-4E00 在两份表里**各命中一次**(0 键核对)，'
         u'可成因完全不同——定义表那次住在“SQUARED CJK UNIFIED IDEOGRAPH-4E00”这个兼容字符的名字后半，'
         u'派生表那次才是区间行造出来的端点名。附带一条只属于工具侧的观察：审计器 CNT 一律做大小写折叠，而这两个源的名字列整列大写，'
         u'所以“UND 这三个字母”在定义表区分大小写是 %d 处(全在 POUND SIGN、SPACING UNDERSCORE 这类名字里)，'
         u'折叠后也是 %d 处——两种口径撞成同一个数，恰是因为名字列没有小写；'
         u'同一个子串问题因此在核对工具自己嘴里也有一次，报数必须说明是哪一种口径。'
         % (CNT(u'Han', 0), CNT(u'HYPHEN', 0), CNT(u';HYPHEN;', 0), CNT(u'LATIN', 0), CNT(u'LATIN', 1),
            CNT(u'SQUARED', 0), CNT(u'SQUARED', 1), UND_CS, UND_CI))
T.append(u'※ 可核性的三级阶梯：① 纯 CNT 可核——行数、分号密度(十四 ⇎ 一)、两点号与方括号的配平、类名在两表里的身份、'
         u'子串假阳性、%d 个键里的全部直接计数；② 需要展开或外部断言——%d/%d/%d/%d/%d/%d 六个数(区间展开、双向差集、标记覆盖、'
         u'自报和、脚本值数，交给审计器里的 B47_* 函数)；③ 只属于工具侧——字节数 %d ⇎ %d、全文件字符数 %d ⇎ %d、'
         u'被口径剔掉的行数 %d ⇎ %d、两份文件的 sha256、造名逐行核对的 %d/%d 分配、'
         u'“命中一次住在哪一列”这种位置判断( CNT 数命中，不看列)。'
         % (len(VALS) - 6, ASSIGN, NOROW, IN_UCD, COV, SELF, SCRIPTS,
            N_BYTES[0], N_BYTES[1], NU_FULL, NS_FULL, DROPPED[0], DROPPED[1], rb, NGEN))
T.append(u'※ 口径与 0 的两重成因：派生侧有三个字符数——口径内 %d ⇎ 全文件 %d ⇎ 磁盘 %d，'
         u'第一个差 %d 摊开来＝被剔掉的 %d 行注释含各自换行 %d ＋ 尾部空白 %d(文件名、日期、版权、@missing 都在那些行里)，'
         u'第二个差 %d 是那两个非 ASCII 字节'
         u'(版权行里的 © 与 ®，口径内非 ASCII 为 0 但文件里有)。定义侧是另一种干净：口径内 %d ⇎ 全文件 %d ⇎ 磁盘 %d，'
         u'三者只差结尾换行，因为它整个文件没有表头，字节数等于字符数。'
         u'于是“文件里没有版本信息”(定义侧，全文件 0)与“版本信息被口径剔掉了”(派生侧，口径内 0 ⇎ 文件内 Unicode %d 次、'
         u'版本 1 次、日期 1 次)在机检里长得一模一样，必须分别写明——本条把这两个 0 都折在 0 键里，把成因写在注里。'
         % (NS_RC, NS_FULL, N_BYTES[1], NS_FULL - NS_RC, DROPPED[1], DROPCH[1], TAILWS[1],
            N_BYTES[1] - NS_FULL,
            NU_RC, NU_FULL, N_BYTES[0], CNTF(u'Unicode', 1)))
T.append(u'※ 字段密度先于内容：定义表每行十四 ⇎ 派生表每行一，两个数都是 CNT 键(%d ⇎ %d)，比值不写数字而由两次计数撑起；'
         u'定义表 %d 行里有 %d 行以四个空字段收尾——一张表把“没有内容”写成可见的密度，'
         u'另一张把“很多码位”写成一个省略号。同一件事在字节层也要报口径：两份表口径内都纯 ASCII，'
         u'可派生侧文件比字符多 %d 个字节，那 %d 个字节正是被口径剔掉的注释行。'
         % (N_SEMIU, CNT(u';', 1), N_ROWU, N_EMPT4, N_BYTES[1] - NS_FULL, N_BYTES[1] - NS_FULL))
T.append(u'※ 两源对齐与工具侧复现：摘要段 union_hit=%d 与锚位数相等(重复引用的锚位 %d 个，不同串 %d 个)，'
         u'摘要段 %d 字符 ⇎ 两源口径内合计 %d 字符(比它小两个数量级)；同时能在两份表里找到的锚串 %d 个——'
         u'两份表字面上几乎不共享任何东西，共享的只有码位这个概念。'
         u'标签归位仍是作者的职责：atomcheck 与 audit 都把同一 tag 的两个源拼在一起比对字面，⟦%s⟧/⟦%s⟧ 写反不会 FAIL，'
         u'本条机检 ok=%d/%d。另有一次外部复现：让本地免费模型不看本库代码、只照十道题独立写一份核对脚本，'
         u'它交回的第一版把区间行的行首正则少写了一个可选组，于是 %d 行里只认出 %d 行(区间一行不认)——'
         u'正是本条判词⑤警告的那类解析错误；补上可选组后它与本条在 %d 个量上逐个同值(包括那 %d 个无人认领的码位清单)。'
         % (len(atoms), len(atoms) - len(uniq_atoms), len(uniq_atoms), dig, RCOT_SUM, CROSS, LU, LS,
            len(uniq_atoms), len(uniq_atoms), N_ROWS, N_SGL, 21, len(ONLY)))
T.append(u'※ 隐性知识的所在(判词逐行对应的判断)：① 键拼法相同只算一半成功，另一半是对方是否为这个键开行；'
         u'② 压缩装置各有可数的记号(端点标记对 ⇎ 两点号 + 方括号 + 造名省略号)；③ 字段数即格式(每行十四 ⇎ 每行一)；'
         u'④ 命中一次也可能是错觉，要看命中住在哪一列；⑤ 子串检索会造一台真数字的假阳性机器；'
         u'⑥ 派生表会**生成**定义表按格式写不出的串与类，反向核对要预先排除；'
         u'⑦ 0 有两种成因(真的没有 ⇎ 被口径剔掉)，而“纯 ASCII”必须报口径；'
         u'⑧ 双向缺席且不对称(标记端点无人认领 ⇎ 标记内部没有定义行，私有区一边有行、一边拒绝归类)；'
         u'⑨ 自报数与展开算术相等这件事数不出来，只能交给函数；⑩ 造名核对里 14 行不符全部可归因于生成规则，'
         u'这才叫“派生”而不是“抄写”。与上一条的分工：B46 数的是同一标识符的三种拼法与同一内容的两种说法，'
         u'本条数的是同一份数据的两种**表形状**(按行定义 ⇎ 按区间派生)，判据不重叠。')
T.append(u'※ 实况：编码 %d 字符 ⇎ 摘要段 %d 字符(保留率 %s)，vs raw 源 %s，唯一码点 %d，区块 %d 类，字符/语义单元 %s。'
         u'拉丁字母：锚内 %d ⇎ 锚外 %d(其中标签 %d)。全库现 %d 条 / 已机检推导 %d 条 / 全库保留率 %s。'
         u'B47 的小整数待核为 0 项。'
         % (enc, dig, b47[2], dens, uniq_cp, blocks, cpu, in_lat, out_lat, tag_lat,
            len(row) - 1, proofs, allr[2]))
T.append(u'※ 保留率口径：本条 %s 是全库最高一档——摘要段只装锚点触到的 %d 行窗口(共 %d 字符)，'
         u'而原料是两份百万级字符的表(口径内合计 %d)。读它要按“%d 键支撑 %d 行判词”来读，不是按“少说了多少话”：'
         u'判词里最重的那几条(十万级码位在定义侧无行、造名核对、双向差集)住在展开算术里，不住在任何窗口里；'
         u'若只留定义表而丢掉派生表，本条一半的数就失去了对照物——被派生者不在场，派生本身也就无从证明。'
         % (b47[2], len(atoms), dig, RCOT_SUM, len(VALS), GLOS))

G = md[:md.index(u'## ⛓解读注')] + u'## ⛓解读注\n' + (NL + NL).join(T) + NL
io.open(ENTRY, 'w', encoding='utf-8').write(G)

ST = {u'anchors': len(atoms), u'uniq_anchor': len(uniq_atoms), u'digest': dig, u'enc': enc,
      u'ret': b47[2], u'dens': dens, u'uniq_cp': uniq_cp, u'blocks': blocks, u'cpu': cpu,
      u'proofs': proofs, u'gloss_lines': GLOS, u'deriv_keys': len(VALS),
      u'n_term0': NTERM0, u'n_terms0': NTERMS0, u'n_absent': NABSEQ, u'n_equ': NEQSEQ, u'n_diff': DIFFTERM,
      u'rcot_u': NU_RC, u'rcot_s': NS_RC, u'rcot_sum': RCOT_SUM, u'full_u': NU_FULL, u'full_s': NS_FULL,
      u'bytes_u': N_BYTES[0], u'bytes_s': N_BYTES[1], u'dropped_u': DROPPED[0], u'dropped_s': DROPPED[1],
      u'sha_u': SHA[0], u'sha_s': SHA[1], u'assign': ASSIGN, u'norow': NOROW, u'in_ucd': IN_UCD,
      u'noucd': len(ONLY), u'only_ucd_hex': u' '.join(format(x, u'X') for x in ONLY),
      u'markcov': COV, u'selfsum': SELF, u'scripts_n': SCRIPTS, u'uncovered': UNCOVERED,
      u'orphan_pairs': u' ⇎ '.join(ORPH_PAIRS), u'cover_pairs': COVER_PAIRS,
      u'single_named_ok': sb, u'range_both_ok': rb, u'range_bad': NGEN,
      u'bad_ctrl': CLS[u'control'], u'bad_hangul': CLS[u'hangul'], u'bad_ideo': CLS[u'ideograph'],
      u'gen_prefix': u' '.join(u'%s×%d' % (k, v) for k, v in gen_pref.most_common()),
      u'gc_u_kinds': len(GC_U), u'gc_s_kinds': len(GC_S),
      u'und_cs': UND_CS, u'und_ci': UND_CI, u'unk_file_s': CNTF(u'Unknown', 1),
      u'miss_file_s': CNTF(u'@missing', 1), u'anchor_u': NLU[LU], u'anchor_s': NLU[LS],
      u'in_lat': in_lat, u'out_lat': out_lat, u'tag_lat': tag_lat, u'all_ret': allr[2],
      u'all_enc': allr[1], u'all_digest': allr[0], u'all_cp': allr[4], u'cross_atoms': CROSS,
      u'head_lines': u' ⫽ '.join(x.strip()[:44] for x in DROP_LINES)}
io.open(u'corpus/_f47stats.txt', 'w', encoding='utf-8').write(
    NL.join(u'%s\t%s' % (k, v) for k, v in dict(BST, **ST).items()) + NL)
print(u'gloss written: keys %d enc %d dig %d ret %s uniq %d anchors %d(%d uniq) U/S %d/%d '
      u'in_lat %d out_lat %d proofs %d bad_name %d/%d und %d/%d'
      % (len(VALS), enc, dig, b47[2], uniq_cp, len(atoms), len(uniq_atoms), NLU[LU], NLU[LS],
         in_lat, out_lat, proofs, rb, NGEN, UND_CS, UND_CI))
