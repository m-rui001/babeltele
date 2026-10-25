# -*- coding: utf-8 -*-
"""README 记账: 47 条 → 48 条。合计数字全部由 audit 表、metrics 普查、三份 raw 回算与 _f48stats 复算, 不手填。
B48 特有的一环: 这里再真执行一次生成器(gawk -f 程序 输入), 与在库产物比 sha256——README 里那句“可执行复现”因此不是转述。"""
import io, re, sys, os, ast, hashlib, subprocess, tempfile

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
t = io.open(F, encoding='utf-8').read()

TAG, ENTRY = u'B48', u'corpus/babeltele/B48_input_program_and_its_output.md'
RI, RA, RL = (u'corpus/raw/tz/leap-seconds.list', u'corpus/raw/tz/leapseconds.awk',
              u'corpus/raw/tz/leapseconds')
RAWS = [RI, RA, RL]
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
b48, b47 = cells(u'B48'), cells(u'B47')
b48_enc, b48_dig, b48_ret, b48_raw, b48_uniq, b48_blocks, b48_cpu, b48_soft = (
    int(b48[1]), int(b48[0]), b48[2], b48[3], int(b48[4]), int(b48[5]), b48[6], int(b48[10]))
b47_enc, b47_dig, b47_ret = int(b47[1]), int(b47[0]), b47[2]
assert NENT == 48, NENT
assert b48_soft == 1, b48
assert re.search(u"^\\s+B48 \\['48'\\]$", p.stdout, re.M), u'B48 的待核项应恰为条目号 48'
assert int(b48[7]) == 0 and int(b48[8]) == 0 and int(b48[9]) == 0, b48
ZSOFT = sorted([k for k in row if k != u'ALL' and int(cells(k)[10]) == 0], key=lambda x: int(x[1:]))

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


ST = loadstat(u'corpus/_f48stats.txt')
S47 = loadstat(u'corpus/_f47stats.txt')
NUM = lambda k: int(ST[k])
IN_LAT, OUT_LAT, TAG_LAT = NUM(u'in_lat'), NUM(u'out_lat'), NUM(u'tag_lat')
OUT_ALL = OUT_LAT + TAG_LAT
ANCH, UANCH = NUM(u'anchors'), NUM(u'uniq_anchor')
ANCH_I, ANCH_A, ANCH_L = NUM(u'anchor_i'), NUM(u'anchor_a'), NUM(u'anchor_l')
DERIV_KEYS, NTERM0, NTERMS0 = NUM(u'deriv_keys'), NUM(u'n_prim0'), NUM(u'n_terms0')
NABS, NEQU, GLOS = NUM(u'n_absent'), NUM(u'n_equ'), NUM(u'gloss_lines')
assert NABS + NEQU == NTERMS0 and NABS == 34 and NEQU == 33, (NABS, NEQU)
assert ANCH_I + ANCH_A + ANCH_L == UANCH and TAG_LAT == ANCH, (ANCH_I, ANCH_A, ANCH_L)
assert (b48_enc, b48_dig) == (NUM(u'enc'), NUM(u'digest')) and b48_ret == ST[u'ret']
assert (b48_uniq, b48_blocks) == (NUM(u'uniq_cp'), NUM(u'blocks')) and b48_raw == ST[u'dens']
assert float(b48_cpu) == float(ST[u'cpu']) and NUM(u'cross_atoms') == 0

# ---------- 三份 raw 独立回算(与 _mkB48 / _fill48 同规则, 第三条路) ----------
full = lambda i: io.open(RAWS[i], encoding='utf-8', errors='replace').read()
reason = lambda i: NL.join(l for l in full(i).split(NL) if not HEADRX.match(l.strip()))
SRC = [reason(i) for i in range(3)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
CNTF = lambda pat, i: len(re.findall(pat, full(i), re.I))
RCOT = lambda i: len(SRC[i].strip())
BYTES = [os.path.getsize(x) for x in RAWS]
FULLN = [len(full(i)) for i in range(3)]
SHA = [hashlib.sha256(open(x, 'rb').read()).hexdigest() for x in RAWS]
NLINES = [len(full(i).split(NL)) - 1 for i in range(3)]
DROP = [len([l for l in full(i).split(NL) if HEADRX.match(l.strip())]) for i in range(3)]
assert NLINES == [int(x) for x in ST[u'lines'].split(u' ')] == [120, 256, 86]
assert DROP == [int(x) for x in ST[u'dropped'].split(u' ')] == [92, 61, 51]
assert [RCOT(i) for i in range(3)] == [int(x) for x in ST[u'rcot'].split(u' ')] == [1035, 6464, 809]
assert FULLN == BYTES == [int(x) for x in ST[u'bytes'].split(u' ')] == [5065, 9448, 3694]
assert SHA[0] == ST[u'sha_i'] and SHA[1] == ST[u'sha_a'] and SHA[2] == ST[u'sha_l']
assert [CNT(u'[^\x00-\x7f]', i) for i in range(3)] == [0, 0, 0]
RCOT_SUM, BYTES_SUM = sum(RCOT(i) for i in range(3)), sum(BYTES)
assert (RCOT_SUM, BYTES_SUM) == (NUM(u'rcot_sum'), NUM(u'bytes_sum')) == (8308, 18207)
# 被剔字符 = 注释行含各自换行 + 尾部空白(三份都要拆得开)
DROPCH = [sum(len(l) + 1 for l in full(i).split(NL) if HEADRX.match(l.strip())) for i in range(3)]
TAILWS = [len(SRC[i]) - len(SRC[i].strip()) for i in range(3)]
for i in range(3):
    assert DROPCH[i] + TAILWS[i] == FULLN[i] - RCOT(i), i

# 数据行与 TAI 跨度
DATA = [l.split() for l in full(0).split(NL) if l[:1].isdigit()]
assert len(DATA) == NUM(u'data_rows') == 28
TAI = sorted(int(r[1]) for r in DATA)
assert TAI == list(range(NUM(u'tai_min'), NUM(u'tai_max') + 1)) == list(range(10, 38))
ABB = u'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(u' ')
MOND = [31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31]


def cal(s):                                       # 程序自带的 1900 纪元历, 逐档降下来
    day = 109513 + s // 86400
    qc = day // 146097
    day -= qc * 146097
    ce = day // 36524
    ce -= ce == 4
    day -= ce * 36524
    qy = day // 1461
    day -= qy * 1461
    yr = day // 365
    yr -= yr == 4
    day -= yr * 365
    mo = 0
    while mo < 11:
        if day < MOND[mo]:
            break
        day -= MOND[mo]
        mo += 1
    if mo <= 9:
        mm = mo + 3
    else:
        mm = mo - 9
        yr += 1
    return (1600 + qc * 400 + ce * 100 + qy * 4 + yr, mm, day + 1, (s // 3600) % 24)


LROWS = [l.split(TAB) for l in reason(2).split(NL) if l.startswith(u'Leap')]
assert len(LROWS) == NUM(u'leap_rows') == 27
N_LEAP = len(LROWS)
N_MAIN = len([l for l in SRC[1].split(NL) if l.strip().startswith(u'printf "Leap')])
assert (N_MAIN, NUM(u'dead'), NUM(u'sign')) == (1, 3, 2)
OKN = len([1 for k in range(1, 28)
           if (u'%d' % cal(int(DATA[k][0]) - 1)[0], ABB[cal(int(DATA[k][0]) - 1)[1] - 1],
               u'%d' % cal(int(DATA[k][0]) - 1)[2], u'%02d:59:60' % cal(int(DATA[k][0]) - 1)[3])
           == tuple(LROWS[k - 1][1:5])])
SHM = len([1 for k in range(1, 28) if LROWS[k - 1][2] != DATA[k][4]])
SHY = len([1 for k in range(1, 28) if LROWS[k - 1][1] != DATA[k][5]])
SHD = len([1 for k in range(1, 28) if LROWS[k - 1][3] != DATA[k][3]])
assert (OKN, SHM, SHY, SHD) == (NUM(u'rows_ok'), NUM(u'mshift'), NUM(u'yshift'), NUM(u'dshift')) == (27, 27, 16, 27)
JUN, DEC = CNT(u'(?m)^Leap\\t\\d+\\tJun\\t30\\t', 2), CNT(u'(?m)^Leap\\t\\d+\\tDec\\t31\\t', 2)
assert (JUN, DEC, JUN + DEC) == (NUM(u'jun30'), NUM(u'dec31'), 27)
assert (CNT(u'Jan', 2), CNT(u'Jul', 2), CNT(u'Jun', 0)) == (0, 0, 0)

# 语句 × 次数
blk = full(1).split(u'BEGIN {')[1].split(NL + u'}')[0]
EMIT = [l for l in blk.split(NL) if l.strip().startswith(u'print "')]
HEADOK = 0
for k, l in enumerate(EMIT):
    s = l.strip()
    lit = s[s.index(u'"') + 1:s.rindex(u'"')]
    for a, b in ((BS + u'n', NL), (BS + u't', TAB), (BS + u'"', u'"'), (BS + BS, BS)):
        lit = lit.replace(a, b)
    if full(2).split(NL)[k] == lit:
        HEADOK += 1
assert (len(EMIT), HEADOK) == (NUM(u'bprint'), NUM(u'headok')) == (40, 40)
BLANKHEAD = len([l for l in EMIT if l.strip() == u'print ""'])
ENDL = NLINES[2] - 40 - 27
ENDLANK = full(1).split(u'END {')[1].split(NL + u'}')[0].count(u'print ""')
assert (BLANKHEAD, ENDL, ENDLANK) == (NUM(u'blankhead'), NUM(u'endlines'), NUM(u'endblank')) == (5, 19, 2)
TAIL = full(2).split(NL)[67:67 + ENDL]
TB = len([l for l in TAIL if l == u''])
COPY = len([l for l in TAIL[-2:] if l in full(0).split(NL)])
assert (TB, COPY) == (NUM(u'tail_blank'), NUM(u'tail_copy')) == (3, 2)
N_PRINT, N_PRINTF = CNT(u'(?m)^[ \t]*print[ \t"]', 1), CNT(u'(?m)^[ \t]*printf[ \t"]', 1)
assert (N_PRINT, N_PRINTF, CNT(u'print ""', 1)) == (56, 5, 7)
assert (CNT(u'10\\*\\*10', 1), CNT(u'2\\*\\*53', 1)) == (0, 0)
assert (CNTF(u'10\\*\\*10', 1), CNTF(u'2\\*\\*53', 1), CNTF(u'2216', 1), CNTF(u'285,428,681', 1)) == (2, 3, 2, 1)
Y10, Y53 = cal(10 ** 10)[0], cal(2 ** 53)[0]
assert (Y10, Y53) == (NUM(u'y10'), NUM(u'y53')) == (2216, 285428681)

# 转义与说明符
PCTK = {k: CNT(u'%' + k, 1) for k in (u'd', u's', BS + u'.4d', BS + u'.2d')}
N_PCT, N_MOD = CNT(u'%', 1), CNT(u'% ', 1)
assert sum(PCTK.values()) == 26 and N_PCT == 30 and N_PCT == 26 + N_MOD == 26 + 4
assert (CNT(BS + BS + u't', 1), CNT(BS + BS + u'"', 1)) == (NUM(u'esc_t'), NUM(u'esc_q')) == (15, 8)
assert (CNT(TAB, 0), CNTF(TAB, 0), CNT(TAB, 2), CNT(TAB, 1)) == (0, 66, 162, 31)
assert CNT(TAB, 2) == 6 * 27
PMON = u'monthabbr\\[ ?\\d+\\] = '
PMDT = u'ss_mon_days\\[ ?\\d+\\] = '
assert (CNT(PMON, 1), CNT(PMDT, 1)) == (NUM(u'monthabbr'), NUM(u'mon_days')) == (12, 11)
assert (CNT(PMDT + u'31', 1), CNT(PMDT + u'30', 1), CNT(PMDT + u'28', 1)) == (7, 4, NUM(u'md28'))
assert (CNT(u'June', 1), CNT(u'June', 2), CNTF(u'June', 0)) == (0, 0, 5)
N_JUNE_F = [CNTF(u'June', i) for i in range(3)]
assert N_JUNE_F == [NUM(u'june_i_full'), 0, 1] == [5, 0, 1]
N_JUL0 = CNT(u'Jul', 0)
assert (N_JUL0, CNT(u'Jul', 2), CNT(u'Jan', 2)) == (11, 0, 0)
DAY1900 = 109513
assert CNT(u'%d' % DAY1900, 1) == 1

# 封套: 纪元与两枚秒
EUPD = int(re.search(u'#updated +([0-9]+)', full(2)).group(1))
EEXP = int(re.search(u'#expires +([0-9]+)', full(2)).group(1))
STAMP = [int(l.split()[1]) for l in full(0).split(NL)
         if re.match(u'^#[^A-Za-z0-9]\\s+([0-9]{9,10})$', l)]
assert len(STAMP) == 2, STAMP
INUPD, INEXP = STAMP
assert (INUPD, INEXP, EUPD, EEXP) == (3992312697, 4023129600, 1783323897, 1814140800)
EPOCH = INUPD - EUPD
assert EPOCH == INEXP - EEXP == NUM(u'epoch') == ((1970 - 1900) * 365 + 17) * 86400 == 2208988800
GAP, SHORT = INEXP - INUPD, 365 * 86400 - (INEXP - INUPD)
assert (GAP, SHORT, round(GAP / 86400.0, 2)) == (NUM(u'gap'), NUM(u'short'), float(ST[u'gap_days'])) \
    == (30816903, 719097, 356.68)

# ---------- 真执行一次 ----------
GVER = subprocess.run([u'gawk', u'-W', u'version'], capture_output=True, text=True,
                      encoding='utf-8', errors='replace').stdout.split(NL)[0]
with tempfile.NamedTemporaryFile(suffix=u'.out', delete=False) as tf:
    tmp = tf.name
try:
    with open(tmp, 'wb') as fo:
        subprocess.run([u'gawk', u'-f', RA, RI], stdout=fo, check=True)
    RB = hashlib.sha256(open(tmp, 'rb').read()).hexdigest()
finally:
    os.unlink(tmp)
assert RB == SHA[2] == ST[u'repro_sha'], (RB, SHA[2])
assert GVER == ST[u'gawk'].split(NL)[0]

fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')


# ---------- 条目结构(标签 occurrence 与锚内/锚外拉丁) ----------
md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
labels = re.findall(u'⟦([IAL])⟧⟨', body)
uniq_atoms = sorted(set(atoms))
assert len(atoms) == ANCH and len(uniq_atoms) == UANCH, (len(atoms), len(uniq_atoms))
NLAB = dict((c, labels.count(c)) for c in u'IAL')
B_IN = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
B_OUTALL = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
assert (B_IN, B_OUTALL - len(labels), len(labels)) == (IN_LAT, OUT_LAT, TAG_LAT), (B_IN, B_OUTALL)
assert (len(uniq_atoms), UANCH, ANCH, len(labels)) == (49, 49, 102, 102)

mm = re.search(u'第二代（B11–B47）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
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

assert all(k in ZSOFT for k in (u'B32', u'B43', u'B45', u'B46', u'B47'))
assert u'B44' not in ZSOFT and u'B48' not in ZSOFT and len(ZSOFT) == 37

# ---------- 全库计数成对替换 ----------
PAIRS = [
 (u'共 **47 条**（`babeltele/B01..B47`）', u'共 **%d 条**（`babeltele/B01..B48`）' % NENT),
 (u'**PASS**（47 条）', u'**PASS**（%d 条）' % NENT),
 (u'当前 **47 条语料／%s 条**推导全部通过（audit 自报“已机检的推导 %s 条”）' % (S47[u'proofs'], S47[u'proofs']),
  u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs)),
 (u'第二代（B11–B47）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B48）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'残余提示（不计 FAIL）：16 个 1–2 位结构计数',
  u'残余提示（不计 FAIL）：%d 个 1–2 位结构计数' % soft_all),
 (u'B44 的 `42／43` 则是长标识符串 42816885（PMED 号）与 grid.443382.a（机构号）内部的数字切片, '
  u'是锚点原样带来的噪声而不是本条断言, 故不消解）未逐位核验，',
  u'B44 的 `42／43` 则是长标识符串 42816885（PMED 号）与 grid.443382.a（机构号）内部的数字切片, '
  u'是锚点原样带来的噪声而不是本条断言, 故不消解；B48 的 `48` 是条目号自身与助手名 `B48_*` 里那两个数字, '
  u'同样不是量在三份源上的断言）未逐位核验，'),
 (u'B32／B33／B34／B35／B36／B37／B38／B39／B40／B41／B42／B43 是仅有的十二条**待核列为 0** 的条目',
  u'B32／B33／B34／B35／B36／B37／B38／B39／B40／B41／B42／B43 是**待核列为 0** 的 %d 条条目里最连续的十二条'
  u'（其后 B45／B46／B47 同样为 0；新建的 B48 有 1 项，即上面那条条目号 48）' % len(ZSOFT)),
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
    if l.startswith(u'| **合计（47 条）**'):
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
    if u'B47 把轴换到**定义表 ⇎ 由它派生的分类表**' in l and l.rstrip().endswith(u'不住在任何窗口里。'):
        R[i] = l.rstrip() + (
            u'B48 把轴换成**输入 ⇎ 生成它的程序 ⇎ 程序的产物**（%d 锚 ⇎ %d 个不同串，输入侧 %d ⇎ 程序侧 %d ⇎ 产物侧 %d）：'
            u'这一条的联结不用重建——把程序跑在输入上，stdout 与在库产物 sha256 逐字节相同（`%s`，%s），'
            u'“谁生成谁”因此是可重演的事件而不是叙述；可数的那一层仍然全在：'
            u'生成器的账要按**语句 × 次数**记而不是按行数记（BEGIN %d 条 print ⇎ 产物头 %d 行按序逐条相等，'
            u'主循环 %d 条 printf 跑 %d 次——输入 %d 行数据里守卫吃掉首行，END 产 %d 行），'
            u'死支 %d 条 print 在产物里 0 处，0 不代表能力不存在；'
            u'转义层两侧正相反：程序写 \\t %d 枚而产物落真制表符 %d＝6×%d，说明符四型（计数 %d、%d、%d、%d）加取余 %d 枚＝百分号 %d 枚全被值换掉，产物 0 枚；'
            u'程序对自己寿命的断言（10**10⇎2**53 秒）住在被口径剔掉的注释里（口径 0 ⇎ 全文 %d⇎%d），'
            u'却能用它自带的 %d 日纪元历复算出 %d 年与 %d 年；两枚 NTP 封套秒与产物两枚 POSIX 秒恰差纪元 %s＝(70×365+17)×86400，'
            u'间隔 %s 秒＝%s 天，比整年少 %s 秒——“略少于一年”在这一份数据上成立。'
            u'保留率 %s（字节口径 %s，三个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节）仍是对照条的必然读数：'
            u'最重的那几判（执行、逐日对账 %d/%d、纪元、转义层）都不在任何窗口里。'
            % (ANCH, UANCH, ANCH_I, ANCH_A, ANCH_L, RB[:16] + u'…', GVER.split(u',')[0],
               len(EMIT), HEADOK, N_MAIN, N_LEAP, len(DATA), ENDL, NUM(u'dead'),
               NUM(u'esc_t'), CNT(TAB, 2), N_LEAP, PCTK[u'd'], PCTK[u's'], PCTK[BS + u'.4d'], PCTK[BS + u'.2d'],
               N_MOD, N_PCT, CNTF(u'10\\*\\*10', 1), CNTF(u'2\\*\\*53', 1),
               DAY1900, Y10, Y53, fmt(EPOCH), fmt(GAP), ST[u'gap_days'], fmt(SHORT),
               b48_ret, b48_raw, fmt(RCOT_SUM), fmt(BYTES_SUM), OKN, N_LEAP))
        done.append(u'口径段')
        break
assert u'口径段' in done, u'口径段未命中'

GEN = (u'**B48 把对照轴换成输入、生成它的程序与程序的产物**：NIST/IERS 闰秒表 `raw/tz/leap-seconds.list`'
       u'（口径内 %s 字符⇎全文件 %d⇎磁盘 %d 字节，纯 ASCII，%d 行里 %d 行是被剔的注释，数据 %d 行，TAI %d..%d 逐个连续）⇎ '
       u'zic 用的转换器 `raw/tz/leapseconds.awk`（口径内 %s⇎%d⇎%d，%d 行里 %d 行注释——版本行与“POSIX 只活得到 10**10 秒、'
       u'实际 double 到 2**53 秒”那段寿命散文都在注释里，口径内两处各 0）⇎ 产物 `raw/tz/leapseconds`'
       u'（口径内 %s⇎%d⇎%d，%d 行里 %d 行注释，数据 %d 行＝Jun 30 %d ⇎ Dec 31 %d）。'
       u'锚位 %d 个（⟦I⟧ %d ⇎ ⟦A⟧ %d ⇎ ⟦L⟧ %d）／%d 个不同串, 判词 %d 行, DERIV %d 键, '
       u'0 键折 %d 个加法项（纯缺席 %d 类 + 等式与“恰好 N 处/差值” %d 条; 这些项里 CNT/CNTF 原语出现 %d 次）。'
       u'关键结论: 三份文件排在一条因果链上, 而这条链的第一手联结**可以执行**——`gawk -f 程序 输入` 的 stdout '
       u'与在库产物 sha256 逐字节相同（%s，%s），复现失败才是异常；执行之外的第二条路是逐日对账: '
       u'产物 %d 行按程序的日历逐一等于“输入第 k 行时间戳减一秒后落到的月日秒”, 吻合 %d/%d, 其中月名被改 %d 行、'
       u'年被改 %d 行（恰等于 Dec 31 行数）、日被改 %d 行; 输入侧 %d 个 Jul 1 行 ⇒ 产物侧 %d 个 Jun 30 行, '
       u'而 Jun 这个词在输入数据侧 0 处（全文三份 %d ⇎ %d ⇎ %d）——“把闰秒挪到月末”这件事在输入里根本没有词面痕迹。'
       u'生成器的账按语句 × 次数: BEGIN %d 条 print ⇎ 产物头部 %d 行（按序逐条全等）, 其中空行 %d 枚; '
       u'主循环 %d 条 printf 跑 %d 次（守卫 `k>1` 吃掉首行, %d 行数据 ⇒ %d 行产物）; END 产 %d 行（末尾 %d 行逐字拷自输入）; '
       u'死支 %d 条 print 与未取的三元支在产物里各 0 处——缺席不等于无能。'
       u'转义与格式层: 程序里 \\t %d 枚、引号转义 %d 枚, 产物里真制表符 %d 枚＝每行 6 × %d 行, 而输入口径内 0 枚（全文 %d 枚全住注释）; '
       u'百分号 %d 枚＝说明符四型（%%d %d、%%s %d、%%.4d %d、%%.2d %d）+ 取余 %d, 产物 0 枚。'
       u'纪元的两条等式: 输入 #$⇎#@ 两枚 NTP 秒、产物 #updated⇎#expires 两枚 POSIX 秒, 上下各差 %s＝(%d−%d)×365+%d 天 ×86400; '
       u'两枚之间相隔 %s 秒＝%s 天, 比整年少 %s 秒。程序散文里的 %d 年与 %d 年用它自带历（%d 日纪元 + 四百年/百年/四年降档）复算得出。'
       u'工具侧另有一层: 字节数与全文件字符数在纯 ASCII 下相等, 被剔行数 %d⇎%d⇎%d 与三口径分解写进 ⛓解读注而不冒充机检; '
       u'输入的完整性自证那行哈希（全文 %d ⇎ 口径 0）程序既不读也不写, 产物的可信度因此只剩外部散列。')
for i, l in enumerate(R):
    if l.startswith(u'**B47 把对照轴换成定义表与被它派生的分类表**'):
        R[i] = l + u'\n\n' + GEN % (
            fmt(RCOT(0)), FULLN[0], BYTES[0], NLINES[0], DROP[0], len(DATA), NUM(u'tai_min'), NUM(u'tai_max'),
            fmt(RCOT(1)), FULLN[1], BYTES[1], NLINES[1], DROP[1],
            fmt(RCOT(2)), FULLN[2], BYTES[2], NLINES[2], DROP[2], N_LEAP, JUN, DEC,
            ANCH, ANCH_I, ANCH_A, ANCH_L, UANCH, GLOS, DERIV_KEYS, NTERMS0, NABS, NEQU, NTERM0,
            RB[:16] + u'…', GVER.split(u',')[0],
            N_LEAP, OKN, N_LEAP, SHM, SHY, SHD, N_JUL0, JUN, N_JUNE_F[0], N_JUNE_F[1], N_JUNE_F[2],
            len(EMIT), HEADOK, BLANKHEAD, N_MAIN, N_LEAP, len(DATA), N_LEAP, ENDL, COPY, NUM(u'dead'),
            NUM(u'esc_t'), NUM(u'esc_q'), CNT(TAB, 2), N_LEAP, CNTF(TAB, 0), N_PCT,
            PCTK[u'd'], PCTK[u's'], PCTK[BS + u'.4d'], PCTK[BS + u'.2d'], N_MOD,
            fmt(EPOCH), 1970, 1900, 17, fmt(GAP), ST[u'gap_days'], fmt(SHORT), Y10, Y53, DAY1900,
            DROP[0], DROP[1], DROP[2], CNTF(u'a9bad145', 0))
        done.append(u'B48 段')
        break
assert u'B48 段' in done, u'B48 段未命中'

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B47 | %s（新建' % fmt(b47_enc)):
        ins.append((i + 1, u'| B48 | %s（新建, 输入⇎程序⇎产物 %d 锚／%d 个不同串: '
                           u'leap-seconds.list ⟦I⟧ ⇎ leapseconds.awk ⟦A⟧ ⇎ 产物 leapseconds ⟦L⟧; '
                           u'最强一环是可执行复现——gawk 把程序跑在输入上, stdout 与在库产物 sha256 逐字节相同; '
                           u'一个零键折 %d 个加法项（纯缺席 %d 类 ⇎ 等式与“恰好 N 处/差值” %d 条, CNT/CNTF 原语 %d 次）; '
                           u'生成器的账按语句×次数: BEGIN %d 条 print ⇎ 产物头 %d 行按序全等、主循环 %d 条 printf 跑 %d 次'
                           u'（输入 %d 行数据、守卫吃掉首行）、END %d 行、死支 %d 条在产物全 0; '
                           u'转义层两侧相反: 程序 \\t %d ⇎ 产物真制表符 %d＝6×%d、说明符 %d＋取余 %d＝百分号 %d ⇎ 产物 0; '
                           u'封套两条等式: 两枚 NTP 秒与两枚 POSIX 秒各差纪元 %s, 间隔 %s 秒＝%s 天） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为月名、awk 关键字与两份表里的字段词） | %s | %s |'
                           % (fmt(b48_enc), ANCH, UANCH, NTERMS0, NABS, NEQU, NTERM0,
                              len(EMIT), HEADOK, N_MAIN, N_LEAP, len(DATA), ENDL, NUM(u'dead'),
                              NUM(u'esc_t'), CNT(TAB, 2), N_LEAP, sum(PCTK.values()), N_MOD, N_PCT,
                              fmt(EPOCH), fmt(GAP), ST[u'gap_days'],
                              ANCH, fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b48_ret, fmt(b48_dig))))
    elif l.startswith(u'| B47 | %s | %s' % (fmt(b47_enc), b47_ret)):
        ins.append((i + 1, u'| B48 | %s | %s | %s（字节口径; 三个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节——'
                           u'判词要在三份文件之间来回数（执行复现、逐日对账、纪元换算、转义层），而摘要段只索引锚点触到的窗口，'
                           u'故保留率 %s 属对照条的必然读数，按“%d 键支撑 %d 行判词”来读；'
                           u'原料本身小（输入 %s 字符、程序 %s、产物 %s 在口径内），这条不靠收窄窗口买指标） | %d | %s |'
                           % (fmt(b48_enc), b48_ret, b48_raw, fmt(RCOT_SUM), fmt(BYTES_SUM),
                              b48_ret, DERIV_KEYS, GLOS,
                              fmt(RCOT(0)), fmt(RCOT(1)), fmt(RCOT(2)), b48_uniq, b48_cpu)))
    elif l.startswith(u'| B47 | `raw/UnicodeData.txt`'):
        ins.append((i + 1, u'| B48 | `raw/tz/leap-seconds.list`（输入, 口径内 %s 字符⇎全文件 %d⇎磁盘 %d, '
                           u'被剔 %d/%d 行, 数据 %d 行, TAI %d..%d, #$⇎#@ 两枚 NTP 秒）⇎ '
                           u'`raw/tz/leapseconds.awk`（zic 的转换器, 口径内 %s⇎%d⇎%d, 被剔 %d/%d 行——版本与寿命散文都在注释里, '
                           u'print %d ⇎ printf %d, 百分号 %d, \\t %d, monthabbr %d ⇎ ss_mon_days %d）⇎ '
                           u'`raw/tz/leapseconds`（产物, 口径内 %s⇎%d⇎%d, 被剔 %d/%d 行, 数据 %d 行＝Jun 30 %d ⇎ Dec 31 %d, '
                           u'制表符 %d＝6×%d） | 输入 ⇎ 程序 ⇎ 产物: 联结可执行（gawk 重跑得同一 sha256 %s）; '
                           u'逐日对账 %d/%d、月改 %d、年改 %d（＝Dec 31 行数）、日改 %d; '
                           u'语句×次数: 头部 %d⇎%d 按序全等、单条 printf 跑 %d 次、END %d 行含空行 %d 枚（其中 1 枚来自 printf 的转义换行）、'
                           u'末尾 %d 行逐字拷自输入而两份口径内同为 0; '
                           u'输入侧 %d 个 Jul 1 ⇒ 产物侧 %d 个 Jun 30, 而 June 在两份表的数据侧 0 处 ⇒ 挪月末这件事没有词面痕迹; '
                           u'死支 %d 条 print 产物 0（缺席≠无能）; 纪元 %s＝上下两差、间隔 %s 秒＝%s 天、比整年少 %s 秒; '
                           u'程序散文的 %d⇎%d 年由其自带 %d 日历复算; ⇒ 三份文件互不包含, 而“谁生成谁”第一次不必由读者重建 |'
                           % (fmt(RCOT(0)), FULLN[0], BYTES[0], DROP[0], NLINES[0], len(DATA),
                              NUM(u'tai_min'), NUM(u'tai_max'),
                              fmt(RCOT(1)), FULLN[1], BYTES[1], DROP[1], NLINES[1], N_PRINT, N_PRINTF, N_PCT,
                              NUM(u'esc_t'), NUM(u'monthabbr'), NUM(u'mon_days'),
                              fmt(RCOT(2)), FULLN[2], BYTES[2], DROP[2], NLINES[2], N_LEAP, JUN, DEC,
                              CNT(TAB, 2), N_LEAP, RB[:8] + u'…',
                              OKN, N_LEAP, SHM, SHY, SHD, len(EMIT), HEADOK, N_LEAP, ENDL, TB, COPY,
                              N_JUL0, JUN, NUM(u'dead'), fmt(EPOCH), fmt(GAP), ST[u'gap_days'],
                              fmt(SHORT), Y10, Y53, DAY1900)))
    elif l.startswith(u'python -X utf8 corpus/_fill47.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_mkB48.py                # 建条目: 三色锚位(I=输入／A=程序／L=产物), '
                    u'行数三口径、语句×次数发射、逐日对账与纪元算术全部由 raw 回算\n'
                    u'python -X utf8 corpus/_mkdigest3.py B48 <entry> I <raw/tz/leap-seconds.list> 0 0 '
                    u'A <raw/tz/leapseconds.awk> 0 0 L <raw/tz/leapseconds> 0 0   # 三源分节摘要 union_hit %d/%d, 每源按命中锚各自分块\n'
                    u'python -X utf8 corpus/atomcheck.py B48 corpus/_atoms48.txt       # %d 个不同锚串逐字回源 ok=%d bad=0(条目内锚位 %d 个)\n'
                    u'python -X utf8 corpus/_fill48.py               # ⛓解读注: %d 个键逐个复算并与键名断言; 0 键 %d 个加法项(CNT/CNTF 原语 %d 次); '
                    u'待核 1 项(条目号 48 在助手名里); 本条另有一环: 脚本真跑 `gawk -f leapseconds.awk leap-seconds.list` '
                    u'并与在库产物比 sha256(逐字节相同), 复现值 %s; 逐日对账 %d/%d、月年日改名 %d/%d/%d 归审计器内 B48_* 函数与这条第二路'
                    % (ANCH, ANCH, UANCH, UANCH, ANCH, DERIV_KEYS, NTERMS0, NTERM0,
                       RB[:16] + u'…', OKN, 27, SHM, SHY, SHD)))
assert len(ins) == 4, [x[1][:30] for x in ins]
for pos, txt in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt)
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if re.search(u'47 条|B01\\.\\.B47|%s|479 条|%s|%s|%%s' % (
            re.escape(fmt(int(S47[u'enc']))), re.escape(fmt(prev_in)), re.escape(fmt(prev_out))), l)]
print(u'README %d 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 编码 %s 摘要 %s 保留 %s 码点 %s 推导 %d 待核 %d｜'
      u'待核 0 的条目 %d 条｜第二代 %s／%s｜执行复现 %s'
      % (NENT, u'/'.join(done), len(left), fmt(enc_all), fmt(dig_all), ret_all, fmt(uniq_all), proofs,
         soft_all, len(ZSOFT), fmt(in_lat), fmt(out_lat), RB[:16]))
for l in left:
    print(u'  ' + l[:150])
print(u'B48: enc %s dig %s ret %s raw %s uniq %d blocks %d cpu %s soft %d｜锚 %d(I %d/A %d/L %d)/%d 串 标签 %d/%d/%d 判词 %d｜'
      u'DERIV %d 键, 0 键 %d 项(缺席 %d, 等式/差值 %d, 原语 %d 次)｜'
      u'行 %s 剔 %s 口径 %s 全文件 %s 字节 %s｜对账 %d/%d 月 %d 年 %d 日 %d｜Jun %d Dec %d｜'
      u'print %d printf %d 空 %d(%d+%d) 头 %d/%d END %d(空 %d 拷 %d)｜%% %d=%s+4 \\t %d 引号 %d｜'
      u'纪元 %s 间隔 %s=%s 天 短 %s｜10**10→%d 2**53→%d｜gawk %s'
      % (fmt(b48_enc), fmt(b48_dig), b48_ret, b48_raw, b48_uniq, b48_blocks, b48_cpu, b48_soft,
         ANCH, ANCH_I, ANCH_A, ANCH_L, UANCH, NLAB[u'I'], NLAB[u'A'], NLAB[u'L'], GLOS,
         DERIV_KEYS, NTERMS0, NABS, NEQU, NTERM0,
         NLINES, DROP, [RCOT(i) for i in range(3)], FULLN, BYTES,
         OKN, 27, SHM, SHY, SHD, JUN, DEC,
         N_PRINT, N_PRINTF, NUM(u'pempty'), BLANKHEAD, ENDLANK, 40, HEADOK, ENDL, TB, COPY,
         N_PCT, PCTK, NUM(u'esc_t'), NUM(u'esc_q'),
         EPOCH, GAP, ST[u'gap_days'], SHORT, Y10, Y53, GVER))
