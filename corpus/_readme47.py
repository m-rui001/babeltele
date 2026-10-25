# -*- coding: utf-8 -*-
"""README 记账: 46 条 → 47 条。合计数字全部由 audit 表、metrics 普查、raw 回算与 _f47stats 复算, 不手填。"""
import io, re, sys, os, ast, collections, subprocess

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
t = io.open(F, encoding='utf-8').read()

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
b47, b46 = cells(u'B47'), cells(u'B46')
b47_enc, b47_dig, b47_ret, b47_raw, b47_uniq, b47_blocks, b47_cpu, b47_soft = (
    int(b47[1]), int(b47[0]), b47[2], b47[3], int(b47[4]), int(b47[5]), b47[6], int(b47[10]))
b46_enc, b46_dig, b46_ret = int(b46[1]), int(b46[0]), b46[2]
assert b47_soft == 0, b47
assert NENT == 47, NENT
assert int(b47[7]) == 0 and int(b47[8]) == 0 and int(b47[9]) == 0, b47
assert not re.search(u'^\\s+B47 \\[', p.stdout, re.M), u'B47 不该出现在待核清单'

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


ST = loadstat(u'corpus/_f47stats.txt')
NUM = lambda k: int(ST[k])
IN_LAT, OUT_LAT, TAG_LAT = NUM(u'in_lat'), NUM(u'out_lat'), NUM(u'tag_lat')
OUT_ALL = OUT_LAT + TAG_LAT
ANCH, UANCH = NUM(u'anchors'), NUM(u'uniq_anchor')
ANCH_U, ANCH_S = NUM(u'anchor_u'), NUM(u'anchor_s')
DERIV_KEYS, NTERM0, NTERMS0 = NUM(u'deriv_keys'), NUM(u'n_term0'), NUM(u'n_terms0')
NABS, NEQU, NDIFF, GLOS = NUM(u'n_absent'), NUM(u'n_equ'), NUM(u'n_diff'), NUM(u'gloss_lines')
assert NABS + NEQU == NTERMS0 and NABS == 29 and NEQU == 21, (NABS, NEQU)

# —— 两个源的全部计数现算, 与 _mkB47/_fill47 同一口径 ——
RU = u'corpus/raw/UnicodeData.txt'
RS = u'corpus/raw/scripts.txt'
RAWS = [RU, RS]
TXT = [io.open(x, encoding='utf-8', errors='replace').read() for x in RAWS]
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
SRC = [u'\n'.join(l for l in x.split(u'\n') if not HEADRX.match(l.strip())) for x in TXT]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
CNTS = lambda pat, i: len(re.findall(pat, SRC[i]))
RCOT = lambda i: len(SRC[i].strip())
BYTES = [os.path.getsize(x) for x in RAWS]
FULL = [len(x) for x in TXT]
DROP = [len(TXT[i].split(u'\n')) - len(SRC[i].split(u'\n')) for i in range(2)]
DROPLINES = [[l for l in TXT[i].split(u'\n') if HEADRX.match(l.strip())] for i in range(2)]
DROPCH = [sum(len(l) + 1 for l in DROPLINES[i]) for i in range(2)]      # 被剔行含各自换行
TAILWS = [len(SRC[i]) - len(SRC[i].strip()) for i in range(2)]
assert DROPCH[1] + TAILWS[1] == FULL[1] - RCOT(1), (DROPCH, TAILWS)
assert DROPCH[0] == 0 and FULL[0] - RCOT(0) == TAILWS[0] == 1     # 定义侧只差一个结尾换行

UROW = u'(?m)^[0-9A-F]{4,6};'
SROW = u'(?m)^[0-9A-F]{4,6}(?:\\.\\.[0-9A-F]{4,6})?[ \t]*;'
SRNG = u'(?m)^[0-9A-F]{4,6}\\.\\.[0-9A-F]{4,6}[ \t]*;'
SSGL = u'(?m)^[0-9A-F]{4,6}[ \t]+;'
_URX = re.compile(UROW, re.I)
_SRX = re.compile(SROW, re.I)
N_U = len(SRC[0].split(u'\n'))
NROWS_U, NROWS_S = CNT(UROW, 0), CNT(SROW, 1)
N_RNG, N_SGL = CNT(SRNG, 1), CNT(SSGL, 1)
SEMI_U, SEMI_S = CNT(u';', 0), CNT(u';', 1)
EMPT4 = CNT(u'(?m)^.*;;;;$', 0)
MARK, NFIRST, NLAST = CNT(u'<[^>]*, (?:First|Last)>', 0), CNT(u', First>', 0), CNT(u', Last>', 0)
CTRL, CC, CO = CNT(u'<control>', 0), CNT(u';Cc;', 0), CNT(u';Co;', 0)
LT_U, LT_S = CNT(u'<', 0), CNT(u'<', 1)
DOT_U, DOT_S, BRK_S = CNT(u'\\.\\.', 0), CNT(u'\\.\\.', 1), CNT(u'\\[\\d+\\]', 1)
HYP_U, HYPF_U, HYP_S = CNT(u'HYPHEN', 0), CNT(u';HYPHEN;', 0), CNT(u'HYPHEN', 1)
HAN_SUB, HAN_FIELD = CNT(u'Han', 0), CNT(u';\\ Han\\ \\#', 0)
UND_U, UND_S = CNT(u'_', 0), CNT(u'_', 1)
CLS_U = dict((k, CNT(u';' + k + u';', 0)) for k in (u'Mn', u'Lo', u'Nd', u'Cn'))
CLS_S = dict((k, CNT(u'\\#\\ ' + k + u'\\ ', 1)) for k in (u'Mn', u'Lo', u'Nd', u'Cc', u'Co'))
LAND_S, LAND_U = CNT(u'\\#\\ L\\&\\ ', 1), CNT(u'L&', 0)
Cn_F, UPLUS = CLS_U[u'Cn'], CNT(u'U\\+', 0) + CNT(u'U\\+', 1)

# 区间展开: 派生表点集 ⇎ 定义表码位集
def ucd_codes():
    s = set()
    for l in SRC[0].split(u'\n'):
        mm2 = _URX.match(l)
        if mm2:
            s.add(int(l.split(u';')[0], 16))
    return s


pts, selfn, scriptv, cov = set(), 0, set(), set()
urows, srows = [], []
for l in SRC[1].split(u'\n'):
    if _SRX.match(l):
        srows.append(l)
        field, rest = l.split(u';', 1)
        script = rest.split(u'#')[0].strip()
        scriptv.add(script)
        if u'..' in field:
            a, b = field.split(u'..')
            a, b = int(a, 16), int(b, 16)
            n = int(re.search(u'\\[(\\d+)\\]', rest).group(1))
            selfn += n
            pts.update(range(a, b + 1))
            cov.update(range(a, b + 1))
        else:
            pts.add(int(field, 16))
            selfn += 1
for l in SRC[0].split(u'\n'):
    if _URX.match(l):
        urows.append(l)
CODES = ucd_codes()
# 20 对端点标记覆盖的位置
PAIRNAMES = set()
ENDPTS = {}
for l in urows:
    mm2 = re.search(u'<[^>]*, (?:First|Last)>', l)
    if mm2:
        nm = mm2.group(0)[1:-1].rsplit(u', ', 1)[0]
        ENDPTS.setdefault(nm, {})[u'Last' if u'Last>' in mm2.group(0) else u'First'] = int(l.split(u';')[0], 16)
        PAIRNAMES.add(nm)
MARKCOV = 0
for nm, v in ENDPTS.items():
    MARKCOV += v[u'Last'] - v[u'First'] + 1
ASSIGN, IN_UCD = len(pts), len(pts & CODES)
NOROW, NOUCD = len(pts - CODES), len(CODES - pts)
SCRIPTS, SELFN = len(scriptv), selfn
UNCOVERED = 0x110000 - ASSIGN

# 造名逐行核对: 单点行名字逐字 ⇎ 区间行两端点名（与 _fill47 同一算法）
NAME_U = dict((int(l.split(u';')[0], 16), l.split(u';')[1]) for l in urows)
GCRX = re.compile(u'# *([A-Za-z&]+) *(?:\\[(\\d+)\\] *)?(.*)$')
sb = rb = 0
bad_rows, gen_pref = [], collections.Counter()
for l in SRC[1].split(u'\n'):
    ms = re.match(u'^([0-9A-F]{4,6})(?:\\.\\.([0-9A-F]{4,6}))?[ \t]*;[^#]*#', l)
    if not ms:
        continue
    g = GCRX.search(l)
    lo, hi = int(ms.group(1), 16), int(ms.group(2) or ms.group(1), 16)
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
                mx = re.match(u'^(.*?)([0-9A-F]{4,6})$', x)
                if mx and mx.group(2) == format(lo if x == a else hi, u'X'):
                    gen_pref[mx.group(1)] += 1
        bad_rows.append((u'range', format(lo, u'X') + u'..' + format(hi, u'X'), a, da, b, db))
    else:
        bad_rows.append((u'range_noellipsis', format(lo, u'X'), nm))
NGEN = len([x for x in bad_rows if x[0] == u'range'])
NCLS = collections.Counter()
for x in bad_rows:
    s = u'|'.join(x)
    NCLS[u'control' if u'<control-' in s else u'hangul' if u'HANGUL SYLLABLE' in s else u'ideograph'] += 1
sgl_ok, rng_both, bad = sb, rb, len(bad_rows)
assert (sb + rb + bad, NGEN) == (NROWS_S, 14), (sb, rb, bad)
assert (NCLS[u'control'], NCLS[u'hangul'], NCLS[u'ideograph']) == (2, 1, 11)
assert (N_SGL - sgl_ok, N_RNG - rng_both) == (0, bad)

assert (NROWS_U, NROWS_S, N_RNG, N_SGL) == (40575, 2287, 1460, 827), (NROWS_U, NROWS_S, N_RNG, N_SGL)
assert (SEMI_U, EMPT4, N_U - 1) == (568050, 37586, 40575) and SEMI_U == 14 * NROWS_U
assert (SEMI_S - NROWS_S, DOT_S - 2 * N_RNG, BRK_S - N_RNG) == (0, 0, 0)
assert (MARK, NFIRST, NLAST, len(ENDPTS)) == (40, 20, 20, 20)
assert (CTRL, CC, CO) == (65, 65, 6) and CTRL - CC == 0
assert (LT_U, LT_S, DOT_U) == (3938, 4, 0)
assert (HYP_U, HYPF_U, HYP_S, UND_U, UND_S) == (21, 1, 17, 0, 307)
assert (HAN_SUB, HAN_FIELD, Cn_F, UPLUS) == (1391, 0, 0, 0)
assert (CLS_U[u'Mn'], CLS_U[u'Lo'], CLS_U[u'Nd'], CLS_U[u'Cn']) == (2059, 21759, 770, 0)
assert (CLS_S[u'Mn'], CLS_S[u'Lo'], CLS_S[u'Nd'], CLS_S[u'Cc'], CLS_S[u'Co'], LAND_S, LAND_U) == (373, 557, 72, 2, 0, 157, 0)
assert (ASSIGN, IN_UCD, NOROW, NOUCD, SCRIPTS, SELFN) == (159866, 40563, 119303, 12, 174, 159866)
assert (MARKCOV, UNCOVERED) == (258847, 954246)
assert (sgl_ok, rng_both, bad) == (827, 1446, 14), (sgl_ok, rng_both, bad)
assert (RCOT(0), RCOT(1), FULL[0], FULL[1], BYTES[0], BYTES[1], DROP[0], DROP[1]) == (
    2198208, 178503, 2198209, 192458, 2198209, 192460, 0, 368)
assert FULL[1] - RCOT(1) == 13955 and BYTES[1] - FULL[1] == 2
for k, v in {u'rows_u': NROWS_U, u'rows_s': NROWS_S, u'rng': N_RNG, u'sgl': N_SGL,
             u'semi_u': SEMI_U, u'empt4': EMPT4, u'mark': MARK, u'ctrl': CTRL, u'co': CO,
             u'lt_u': LT_U, u'lt_s': LT_S, u'dotdot': DOT_S, u'brk': BRK_S,
             u'hyp_u': HYP_U, u'hypf_u': HYPF_U, u'hyp_s': HYP_S, u'han_sub': HAN_SUB,
             u'und_s': UND_S, u'mn': CLS_U[u'Mn'], u'lo': CLS_U[u'Lo'],
             u'nd': CLS_U[u'Nd'], u'lens': LAND_S, u'mns': CLS_S[u'Mn'], u'los': CLS_S[u'Lo'],
             u'nds': CLS_S[u'Nd'], u'ccs': CLS_S[u'Cc'], u'assign': ASSIGN, u'norow': NOROW,
             u'noucd': NOUCD, u'in_ucd': IN_UCD, u'scripts_n': SCRIPTS, u'selfsum': SELFN,
             u'pairs': len(ENDPTS), u'spans': ASSIGN,
             u'markcov': MARKCOV, u'uncovered': UNCOVERED, u'rcot_u': RCOT(0), u'rcot_s': RCOT(1),
             u'full_u': FULL[0], u'full_s': FULL[1], u'bytes_u': BYTES[0], u'bytes_s': BYTES[1],
             u'dropped_s': DROP[1], u'rcot_sum': RCOT(0) + RCOT(1),
             u'single_named_ok': sgl_ok, u'range_both_ok': rng_both, u'range_bad': bad}\
        .items():
    assert NUM(k) == v, (k, ST.get(k), v)

# audit.py 里的 DERIV 键名与 0 键项数
B47BLK = re.search(u" 'B47': \\{\n(.*?)\n \\},",
                   io.open(u'corpus/audit.py', encoding='utf-8').read(), re.S).group(1)
KS = u'／'.join(sorted([k for k in re.findall(r"^ {2}'([^']+)':", B47BLK, re.M)], key=lambda x: float(x)))
assert len(KS.split(u'／')) == DERIV_KEYS == 37, KS
EXPR = ast.literal_eval(u'{' + B47BLK + u'}')


def split0(s):
    out, depth, cur = [], 0, u''
    for ch in s:
        if ch == u'(':
            depth += 1
        elif ch == u')':
            depth -= 1
        if ch == u'+' and depth == 0:
            out.append(cur)
            cur = u''
        else:
            cur += ch
    out.append(cur)
    return [x for x in out if x.strip()]


def bare_cnt(x, arg):
    x = x.strip()
    if not x.startswith(u'CNT(') or not x.endswith(u',%s)' % arg):
        return False
    depth = 0
    for j, ch in enumerate(x):
        if ch == u'(':
            depth += 1
        elif ch == u')':
            depth -= 1
            if depth == 0:
                return j == len(x) - 1
    return False


T0 = split0(EXPR[u'0'])
ABS0 = [x for x in T0 if bare_cnt(x, u'0')]
ABS1 = [x for x in T0 if bare_cnt(x, u'1')]
# 0 键里 “+” 既作缺席项的分隔符也写进等式(A+B-C), 故 split0 会比 50 项多切出等式的片段;
# 纯缺席项按第二参数归边: 0=定义表口径, 1=派生表口径; 以 '(?m) 开头的行式模式是区间行数(值 1460), 属等式片段。
ABS1 = [x for x in ABS1 if not x.strip().startswith(u"CNT('(?m)")]
assert len(ABS0) + len(ABS1) == NABS, (len(ABS0), len(ABS1))
assert EXPR[u'0'].count(u'CNT(') == NTERM0 == 61
# 定义侧(第二参 0) ⇎ 派生侧(第二参 1)的缺席类
AESC, APAP = len(ABS0), len(ABS1)
assert AESC == 19 and APAP == 10 and len(T0) >= NTERMS0, (AESC, APAP, len(T0))
assert (b47_enc, b47_dig) == (NUM(u'enc'), NUM(u'digest')) and b47_ret == ST[u'ret']
assert (b47_uniq, b47_blocks) == (NUM(u'uniq_cp'), NUM(u'blocks')) and b47_raw == ST[u'dens']
assert float(b47_cpu) == float(ST[u'cpu']) and NUM(u'cross_atoms') == 0


def fmt(n):
    return u'{:,}'.format(int(n)).replace(u',', u' ')


mm = re.search(u'第二代（B11–B46）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
               u'全库合计 \\*\\*([\\d ]+)／([\\d ]+)\\*\\*', t)
assert mm, u'第二代行未命中'
prev_in, prev_out = int(mm.group(1).replace(u' ', u'')), int(mm.group(2).replace(u' ', u''))
FIRST_IN, FIRST_OUT = 121, 2195
assert prev_in + FIRST_IN == int(mm.group(3).replace(u' ', u'')), mm.group(3)
assert prev_out + FIRST_OUT == int(mm.group(4).replace(u' ', u'')), mm.group(4)
assert cen[u'Latin'] - prev_in - prev_out - FIRST_IN - FIRST_OUT == IN_LAT + OUT_ALL, (
    cen[u'Latin'], prev_in, prev_out, IN_LAT, OUT_ALL)
in_lat, out_lat = prev_in + IN_LAT, prev_out + OUT_ALL

cen_s = (u'Latin %s · Han %s · Gen-Punct %s · Arrows %s · CJK-Punct %s · Fullwidth %s · Emoji %s · Math %s · '
         u'Greek %s · Misc-Symbols %s · Dingbats %s · Geometric %s · Hiragana %s · Katakana %s · '
         u'MathAlnum %s · EnclosedIdeo %s · EnclosedSuppl %s · Comb-Diacritic %s') % tuple(
    fmt(cen[k]) for k in [u'Latin', u'Han', u'Gen-Punct', u'Arrows', u'CJK-Punct', u'Fullwidth', u'Emoji',
                          u'Math', u'Greek', u'Misc-Symbols', u'Dingbats', u'Geometric', u'Hiragana',
                          u'Katakana', u'MathAlnum', u'EnclosedIdeo', u'EnclosedSuppl', u'Comb-Diacritic'])

S46 = loadstat(u'corpus/_f46stats.txt')
PAIRS = [
 (u'共 **46 条**（`babeltele/B01..B46`）', u'共 **%d 条**（`babeltele/B01..B47`）' % NENT),
 (u'**PASS**（46 条）', u'**PASS**（%d 条）' % NENT),
 (u'当前 **46 条语料／%s 条**推导全部通过（audit 自报“已机检的推导 %s 条”）' % (S46[u'proofs'], S46[u'proofs']),
  u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs)),
 (u'第二代（B11–B46）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B47）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'：%d 个 1–2 位结构计数（B03' % soft_all, u'：%d 个 1–2 位结构计数（B03' % soft_all),
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
    if l.startswith(u'| **合计（46 条）**'):
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
    if u'B45 把同一根轴推到**同一个名字底下的三种对象**' in l and l.rstrip().endswith(u'仍是对照条的必然读数。'):
        R[i] = l.rstrip() + (u'B47 把轴换到**定义表 ⇎ 由它派生的分类表**（%d 锚 ⇎ %d 个不同串，定义侧 %d ⇎ 派生侧 %d）：'
                             u'连接键是十六进制码位，两边同一种拼法（“U 加号”式前缀两边各 %d 次，0 键），'
                             u'可对上键不等于接得住表——派生表归类的 %s 个点里有 %s 个在定义表没有自己的行，'
                             u'反向 %d 个码位有行却无人认领（正是 %d 对端点标记里 %d 对的两端）；'
                             u'字段密度先定表的种类（每行 %d 个分号 ⇎ 每行 %d）；命中一次也可能是错觉：'
                             u'造名字串在定义表恰好 %d 处，住在另一个字符的名字里；'
                             u'子串会造一台真数字的假阳性机器（Han %d 处 ⇎ 字段式 “; Han #” %d 次）。'
                             u'保留率 %s（字节口径 %s，两个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节）仍是对照条的必然读数：'
                             u'“十万级码位在定义侧不存在”住在展开算术里，不住在任何窗口里。'
                             % (ANCH, UANCH, ANCH_U, ANCH_S, UPLUS, fmt(ASSIGN), fmt(NOROW), NOUCD,
                                len(ENDPTS), len(ENDPTS) - 6, 14, 1, 1, HAN_SUB, HAN_FIELD,
                                b47_ret, b47_raw, fmt(RCOT(0) + RCOT(1)), fmt(BYTES[0] + BYTES[1])))
        done.append(u'口径段')
        break
assert u'口径段' in done, u'口径段未命中'

GEN = (u'**B47 把对照轴换成定义表与被它派生的分类表**：逐码位定义表 `raw/UnicodeData.txt`'
       u'（口径内 %s 字符＝全文件 %d＝磁盘 %d 字节，纯 ASCII，无表头无注释故被剔 %d 行，数据 %s 行 × %d 字段）⇎ '
       u'由它派生的脚本分类表 `raw/scripts.txt`（口径内 %s 字符⇎全文件 %d⇎磁盘 %d，两个口径差 %d 全住在被剔的 %d 行注释里，'
       u'数据 %s 行＝区间 %d ⇎ 单点 %d）。锚位 %d 个（⟦U⟧ %d ⇎ ⟦S⟧ %d）／%d 个不同串, 判词 %d 行, DERIV %d 键, '
       u'0 键折 %d 个加法项（定义侧缺席 %d 类 + 派生侧缺席 %d 类 + 等式与“恰好 N 处” %d 条; 这些项里 CNT 原语出现 %d 次）。'
       u'关键结论: 连接键两边同拼法（U 加号式前缀两边各 0 次）而 %s 个已归类码位里 %s 个在定义表没有行——'
       u'定义表按缺席定义（Cn 字段 0 行），一段连续码位靠 %d 行端点标记（配成 %d 对, First 与 Last 各 %d 行）顶替, '
       u'它们替 %s 个位置说话; 反向 %d 个码位有行却不被任何脚本认领, 正是代理区与私有区那 %d 对标记的两端, '
       u'另有 %s 个位置只由一行兜底注释说话, 而那行被审计口径剔掉——两个 0 数字相同成因不同。'
       u'派生表三件压缩装置各自可数: 区间行自带方括号自报 %d 处＝区间行数, 连写符号同行两次全表 %d＝区间行数两倍, '
       u'单点行两处都没有; 自报数相加与端点展开同为 %s（差 0）。字段密度: 定义表分号 %s＝行数 %s 的十四倍而'
       u'“含十五个分号的行”0 处、以四个空字段收尾的行 %s 处; 派生表每行一个分号。'
       u'同一套类名在两表身份不同: “# L& ”注释 %d 处 ⇎ 定义表 L& %d 次（合成类按码位写不出）, '
       u'控制类字段 %d 行 ⇎ 注释 %d 行, 私有区 %d 行 ⇎ 注释 %d 处; Mn/Lo/Nd 三个类名两侧各一套数（%d⇎%d、%d⇎%d、%d⇎%d）。'
       u'词汇与子串的教训: 脚本值是标识符而定义表无对应字段（“; Han #”%d 次）, 可 Han 作子串在定义表命中 %d 处——'
       u'全在字符名里; HYPHEN 子串 %d ⇎ 字段恰好 %d、下划线定义侧 %d ⇎ 派生侧 %d; '
       u'派生表造出的名字串在定义表恰好命中 %d 次而命中处是另一个字符（带方框的汉字）的名字后半。'
       u'造名逐行核对属工具侧: 单点 %d／%d 逐字等于定义名, 区间两端点名 %d／%d 一致, '
       u'另 %d 行例外全部归因于 control／Hangul／CJK 三种造名装置; '
       u'字节数、全文件字符数、被剔行数、两个 sha256 与“两个口径差 %d＝被剔注释行含换行 %d ＋尾部空白 %d”这一分解都写在 src 行与 ⛓解读注, 不冒充机检。')
for i, l in enumerate(R):
    if l.startswith(u'**B46 把对照轴换成描述与被描述者**'):
        R[i] = l + u'\n\n' + GEN % (
            fmt(RCOT(0)), FULL[0], BYTES[0], DROP[0], fmt(NROWS_U), 14,
            fmt(RCOT(1)), FULL[1], BYTES[1], FULL[1] - RCOT(1), DROP[1], fmt(NROWS_S), N_RNG, N_SGL,
            ANCH, ANCH_U, ANCH_S, UANCH, GLOS, DERIV_KEYS, NTERMS0, AESC, APAP, NEQU, NTERM0,
            fmt(ASSIGN), fmt(NOROW), MARK, len(ENDPTS), NFIRST, fmt(MARKCOV), NOUCD, 6, fmt(UNCOVERED),
            BRK_S, DOT_S, fmt(SELFN), fmt(SEMI_U), fmt(NROWS_U), fmt(EMPT4),
            LAND_S, LAND_U, CC, CLS_S[u'Cc'], CO, CLS_S[u'Co'],
            CLS_U[u'Mn'], CLS_S[u'Mn'], CLS_U[u'Lo'], CLS_S[u'Lo'], CLS_U[u'Nd'], CLS_S[u'Nd'],
            HAN_FIELD, HAN_SUB, HYP_U, HYPF_U, UND_U, UND_S, 1,
            sgl_ok, N_SGL, rng_both, N_RNG, bad,
            FULL[1] - RCOT(1), DROPCH[1], TAILWS[1])
        done.append(u'B47 段')
        break
assert u'B47 段' in done, u'B46 段未命中'

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B46 | %s（新建' % fmt(b46_enc)):
        ins.append((i + 1, u'| B47 | %s（新建, 定义表⇎派生分类表 %d 锚／%d 个不同串: 逐码位定义表 ⟦U⟧ ⇎ 脚本分类表 ⟦S⟧; '
                           u'连接键两边同拼法(U+ 前缀两边各 0), 可 %s 个归类点里 %s 个在定义侧无行 ⇒ 键同≠表接得住; '
                           u'一个零键折 %d 个加法项（定义侧缺席 %d 类 ⇎ 派生侧缺席 %d 类 ⇎ 等式与“恰好 N 处” %d 条, '
                           u'CNT 原语 %d 次）; 字段密度 每行 %d 个分号⇎每行 %d（分号总数 %s＝行数 %s 的十四倍）; '
                           u'端点标记 %d 行配 %d 对替 %s 个位置说话, 反向 %d 个码位无人认领; '
                           u'造名核对(工具侧) 单点 %d／%d ⇎ 区间两端 %d／%d, 例外 %d 行; '
                           u'子串假阳性机器: Han %d 处⇎字段 %d 次、下划线 %d⇎%d） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为码位十六进制串与两份表里的名字/类字段） | %s | %s |'
                           % (fmt(b47_enc), ANCH, UANCH, fmt(ASSIGN), fmt(NOROW), NTERMS0, AESC, APAP, NEQU, NTERM0,
                              14, 1, fmt(SEMI_U), fmt(NROWS_U), MARK, len(ENDPTS), fmt(MARKCOV), NOUCD,
                              sgl_ok, N_SGL, rng_both, N_RNG, bad,
                              HAN_SUB, HAN_FIELD, UND_U, UND_S,
                              ANCH, fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b47_ret, fmt(b47_dig))))
    elif l.startswith(u'| B46 | %s | %s' % (fmt(b46_enc), b46_ret)):
        ins.append((i + 1, u'| B47 | %s | %s | %s（字节口径; 两个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节——'
                           u'定义表按缺席写区间、派生表按区间归了十万级没有定义的码位, 判词要展开两份表才数得出, '
                           u'故保留率 %s 属对照条的结构性读数, 按“%d 键支撑 %d 行判词”来读） | %d | %s |'
                           % (fmt(b47_enc), b47_ret, b47_raw, fmt(RCOT(0) + RCOT(1)), fmt(BYTES[0] + BYTES[1]),
                              b47_ret, DERIV_KEYS, GLOS, b47_uniq, b47_cpu)))
    elif l.startswith(u'| B46 | `raw/api/bio_recent_2026w01.json`'):
        ins.append((i + 1, u'| B47 | `raw/UnicodeData.txt`（逐码位定义表, 口径内 %s 字符＝全文件 %d＝磁盘 %d, '
                           u'被剔注释 0 行, 数据 %s 行 × %d 字段, 端点标记 %d 行／%d 对）⇎ '
                           u'`raw/scripts.txt`（由它派生的脚本分类表, 口径内 %s 字符⇎全文件 %d⇎磁盘 %d, '
                           u'被剔 %d 行注释即版本/日期/版权所在, 数据 %s 行＝区间 %d ⇎ 单点 %d, 脚本值 %d 个） | '
                           u'定义 ⇎ 派生: 连接键同拼法(U+ 两边 0)而归类 %s 点中 %s 个无定义行, 反向 %d 码位有行无人认领'
                           u'(即 %d 对标记的两端), %s 个位置只靠被口径剔掉的兜底注释说话; '
                           u'压缩装置可数性: 定义表 Cn 0 行、每行 %d 分号⇎每行 %d、空字段收尾 %s 行 ⇎ 派生表方括号自报 %d＝区间行数、'
                           u'连写符号 %d＝两倍区间行数; 自报和与端点展开同为 %s(差 0); '
                           u'类名两种身份: “# L& ”%d⇎定义表 L& %d、控制类 %d 行⇎%d 行、私有区 %d 行⇎注释 %d 处; '
                           u'子串假阳性: Han %d⇎字段 %d、HYPHEN %d⇎字段 %d、下划线 %d⇎%d; '
                           u'命中一次的错觉: 造名字串定义侧 %d 处住在另一字符名里; '
                           u'尖括号 %s⇎%d; ⇒ 两份表互不包含且方向不对称, 谁都不是谁的子集 |'
                           % (fmt(RCOT(0)), FULL[0], BYTES[0], fmt(NROWS_U), 14, MARK, len(ENDPTS),
                              fmt(RCOT(1)), FULL[1], BYTES[1], DROP[1], fmt(NROWS_S), N_RNG, N_SGL, SCRIPTS,
                              fmt(ASSIGN), fmt(NOROW), NOUCD, 6, fmt(UNCOVERED),
                              14, 1, fmt(EMPT4), BRK_S, DOT_S, fmt(SELFN),
                              LAND_S, LAND_U, CC, CLS_S[u'Cc'], CO, CLS_S[u'Co'],
                              HAN_SUB, HAN_FIELD, HYP_U, HYPF_U, UND_U, UND_S, 1,
                              fmt(LT_U), LT_S)))
    elif l.startswith(u'python -X utf8 corpus/_fill46.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_mkB47.py                # 建条目: 双色锚位(U=定义表／S=派生表), '
                    u'字段密度、端点标记配对、区间展开与双向差集全部由 raw 回算\n'
                    u'python -X utf8 corpus/_mkdigest3.py B47 <entry> U <raw/UnicodeData.txt> 160 220 '
                    u'S <raw/scripts.txt> 140 200   # 两源分节摘要 union_hit %d/%d, 每源按命中锚各自分块\n'
                    u'python -X utf8 corpus/atomcheck.py B47 corpus/_atoms47.txt       # %d 个不同锚串逐字回源 ok=%d bad=0(条目内锚位 %d 个)\n'
                    u'python -X utf8 corpus/_fill47.py               # ⛓解读注: %d 个键逐个复算并与键名断言; 0 键 %d 个加法项(CNT 原语 %d 次); '
                    u'待核 0 项; 区间展开的 %d⇎%d 与造名逐行核对 %d/%d⇎%d/%d 归工具侧与审计器内 B47_* 函数, sha256、字节数、被剔 %d 行注释在注里明写不冒充机检'
                    % (ANCH, ANCH, UANCH, UANCH, ANCH, DERIV_KEYS, NTERMS0, NTERM0,
                       ASSIGN, NOROW, sgl_ok, N_SGL, rng_both, N_RNG, DROP[1])))
assert len(ins) == 4, [x[1][:30] for x in ins]
for pos, txt in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt)
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if re.search(u'46 条|B01\\.\\.B46|%s|447 条|%s|%s|%%s' % (
            re.escape(fmt(int(S46[u'enc']))), re.escape(fmt(prev_in)), re.escape(fmt(prev_out))), l)]
print(u'README %d 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 编码 %s 摘要 %s 保留 %s 码点 %s 推导 %d 待核 %d｜第二代 %s／%s'
      % (NENT, u'/'.join(done), len(left), fmt(enc_all), fmt(dig_all), ret_all, fmt(uniq_all), proofs,
         soft_all, fmt(in_lat), fmt(out_lat)))
for l in left:
    print(u'  ' + l[:150])
print(u'B47: enc %s dig %s ret %s raw %s uniq %d blocks %d cpu %s｜锚 %d(U %d/S %d)/%d 串 判词 %d｜'
      u'DERIV %d 键, 0 键 %d 项(缺席 %d+%d, 等式 %d, CNT %d 次), 差值键 %d｜'
      u'字段 %d⇎%d 分号 %s/%s 空尾 %s｜展开 %s/%s/%d/%s/%d/%s｜标记 %d/%d 对｜造名 %d/%d⇎%d/%d(%d)｜'
      u'子串 %d/%d⇎%d/%d｜类名 %d⇎%d｜口径 %d/%d/%d/%d⇎%d/%d/%d/%d'
      % (fmt(b47_enc), fmt(b47_dig), b47_ret, b47_raw, b47_uniq, b47_blocks, b47_cpu,
         ANCH, ANCH_U, ANCH_S, UANCH, GLOS,
         DERIV_KEYS, NTERMS0, AESC, APAP, NEQU, NTERM0, NDIFF,
         14, 1, fmt(SEMI_U), fmt(NROWS_U), fmt(EMPT4),
         fmt(ASSIGN), fmt(NOROW), NOUCD, fmt(MARKCOV), SCRIPTS, fmt(UNCOVERED),
         MARK, len(ENDPTS), sgl_ok, N_SGL, rng_both, N_RNG, bad,
         HAN_SUB, HAN_FIELD, UND_U, UND_S, LAND_S, LAND_U,
         RCOT(0), FULL[0], BYTES[0], DROP[0], RCOT(1), FULL[1], BYTES[1], DROP[1]))
