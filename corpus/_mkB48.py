# -*- coding: utf-8 -*-
"""B48 输入 ⇎ 生成它的程序 ⇎ 程序吐出的产物: leap-seconds.list ⇎ leapseconds.awk ⇎ leapseconds。
联结是因果的, 而且本机可执行复现(gawk 跑一遍, 产物散列与在库那份逐字节相同)。
所有数字由 raw 现算; 条目里的每个数要么是 raw 字面, 要么进 DERIV。"""
import io, re, sys, os, hashlib

sys.stdout.reconfigure(encoding='utf-8')

RI = u'corpus/raw/tz/leap-seconds.list'
RA = u'corpus/raw/tz/leapseconds.awk'
RL = u'corpus/raw/tz/leapseconds'
RAWS = [RI, RA, RL]
ENTRY = u'corpus/babeltele/B48_input_program_and_its_output.md'
LI, LA, LL = u'I', u'A', u'L'
NL = u'\n'
TAB = u'\t'
BS = u'\\'
HEADRX = re.compile(u'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)

TXT = [io.open(p, encoding='utf-8', errors='replace').read() for p in RAWS]
LINES = [t.split(NL) for t in TXT]
SRC = [NL.join(l for l in LINES[i] if not HEADRX.match(l.strip())) for i in range(3)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
CNTF = lambda pat, i: len(re.findall(pat, TXT[i], re.I))
RCOT = lambda i: len(SRC[i].strip())
NLINES = [len(x) - 1 for x in LINES]
DROP = [len([l for l in LINES[i] if HEADRX.match(l.strip())]) for i in range(3)]
BYTES = [os.path.getsize(p) for p in RAWS]
SHA = [hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in RAWS]

# ---------- 模式 ----------
P_DATA = u'(?m)^' + u'\\d{10}' + u'[ \\t]+' + u'\\d+' + u'[ \\t]+#'
P_LEAP = u'(?m)^Leap' + TAB
P_JUN30 = u'(?m)^Leap' + TAB + u'\\d{4}' + TAB + u'Jun' + TAB + u'30' + TAB
P_DEC31 = u'(?m)^Leap' + TAB + u'\\d{4}' + TAB + u'Dec' + TAB + u'31' + TAB
P_60, P_59 = u'23:59:60', u'23:59:59'
P_PLUS = TAB + u'\\+' + TAB + u'S'
P_MINUS = TAB + u'\\-' + TAB + u'S'
P_TAB = TAB
P_ESCT = BS + BS + u't'
P_ESCQ = BS + BS + u'"'
P_ESCN = BS + BS + u'n'
P_CONT = BS + BS + NL
P_PCT, P_PCTD, P_PCTS, P_PCT4, P_PCT2 = u'%', u'%d', u'%s', u'%\\.4d', u'%\\.2d'
P_PRINT = u'(?m)^[ \\t]*print[ \\t"]'
P_PRINTF = u'(?m)^[ \\t]*printf[ \\t"]'
P_PEMPTY = u'print ""'
P_MAIN = u'printf "Leap'
P_SIGN = u'sign = "23:59:'
P_DEAD = u'No Expires line|time unknown'
P_EL, P_LL = u'EXPIRES_LINE', u'last_lines'
P_MON = u'monthabbr\\[ ?\\d+\\] = '
P_MDT = u'ss_mon_days\\[ ?\\d+\\] = '
P_MD31 = P_MDT + u'31'
P_MD30 = P_MDT + u'30'
P_MD28 = P_MDT + u'28'
P_JAN, P_JUL, P_DEC, P_JUNE, P_JUN = u'Jan', u'Jul', u'Dec', u'June', u'Jun'
P_MEND = u'Day Month Year'
P_PD = u'This file is in the public domain'
P_QJAN = u'"1 Jan 1972"'
P_UPDT, P_EXPO, P_HASH = u'Updated through IERS', u'File expires on', u'a9bad145'
P_LESE = u'Leap' + BS + BS + u't'
P_EXP10, P_EXP53, P_Y2216, P_BIG = u'10\\*\\*10', u'2\\*\\*53', u'2216', u'285,428,681'
P_NEXP = u'(?m)^' + u'#Expires '
P_BEXP = u'(?m)^Expires '
P_Y1980, P_Y2017, P_37 = u'1980', u'2017', u'37'
P_10 = u'(?m)^[0-9A-Za-z]' + TAB

# ---------- 现算 ----------
N_DATA = CNT(P_DATA, 0)
N_LEAP, N_JUN, N_DEC = CNT(P_LEAP, 2), CNT(P_JUN30, 2), CNT(P_DEC31, 2)
N_JAN_I, N_JUL_I, N_JUN_I = CNT(P_JAN, 0), CNT(P_JUL, 0), CNT(P_JUN, 0)
N_JAN_A, N_JUL_A, N_JUN_A = CNT(P_JAN, 1), CNT(P_JUL, 1), CNT(P_JUN, 1)
N_JAN_L, N_JUL_L, N_DEC_L = CNT(P_JAN, 2), CNT(P_JUL, 2), CNT(P_DEC, 2)
N_60_A, N_59_A, N_60_L, N_59_L = CNT(P_60, 1), CNT(P_59, 1), CNT(P_60, 2), CNT(P_59, 2)
N_PLUS_L, N_MINUS_L, N_PLUS_A, N_MINUS_A = CNT(P_PLUS, 2), CNT(P_MINUS, 2), CNT(P_PLUS, 1), CNT(P_MINUS, 1)
N_TAB_I0, N_TAB_A, N_TAB_L, N_TAB_IF = CNT(P_TAB, 0), CNT(P_TAB, 1), CNT(P_TAB, 2), CNTF(P_TAB, 0)
N_ESCT, N_ESCQ, N_ESCN, N_CONT = CNT(P_ESCT, 1), CNT(P_ESCQ, 1), CNT(P_ESCN, 1), CNT(P_CONT, 1)
N_PCT, N_PCTD, N_PCTS, N_PCT4, N_PCT2 = (CNT(P_PCT, 1), CNT(P_PCTD, 1), CNT(P_PCTS, 1),
                                         CNT(P_PCT4, 1), CNT(P_PCT2, 1))
N_PRINT, N_PRINTF, N_PEMPTY, N_MAIN = CNT(P_PRINT, 1), CNT(P_PRINTF, 1), CNT(P_PEMPTY, 1), CNT(P_MAIN, 1)
N_SIGN = CNT(P_SIGN, 1)
N_DEAD, N_EL, N_LL = CNT(P_DEAD, 1), CNT(P_EL, 1), CNT(P_LL, 1)
N_MON, N_MDT, N_MD31, N_MD30, N_MD28 = CNT(P_MON, 1), CNT(P_MDT, 1), CNT(P_MD31, 1), CNT(P_MD30, 1), CNT(P_MD28, 1)
N_JUNE = [CNT(P_JUNE, i) for i in range(3)]
N_JUNE_F = [CNTF(P_JUNE, i) for i in range(3)]
N_PD = [CNT(P_PD, i) for i in range(3)]
N_PD_F = [CNTF(P_PD, i) for i in range(3)]
N_UPDT = [CNT(P_UPDT, i) for i in range(3)]
N_UPDT_F = [CNTF(P_UPDT, i) for i in range(3)]
N_EXPO_F = [CNTF(P_EXPO, i) for i in range(3)]
N_MEND = [CNT(P_MEND, i) for i in range(3)]
N_HASH = [CNT(P_HASH, i) for i in range(3)]
N_HASH_F = [CNTF(P_HASH, i) for i in range(3)]
N_LESE_A, N_LESE_L = CNT(P_LESE, 1), CNT(P_LESE, 2)
N_NEXP_L, N_BEXP_L, N_NEXP_A = CNT(P_NEXP, 2), CNT(P_BEXP, 2), CNT(P_NEXP, 1)
N_NEXP_LF = CNTF(P_NEXP, 2)
N_1980_I, N_1980_L, N_2017_I, N_2017_L = CNT(P_Y1980, 0), CNT(P_Y1980, 2), CNT(P_Y2017, 0), CNT(P_Y2017, 2)
N_37_I, N_37_L = CNT(P_37, 0), CNT(P_37, 2)
N_1010_A, N_253_A, N_2216_A, N_BIG_A = CNT(P_EXP10, 1), CNT(P_EXP53, 1), CNT(P_Y2216, 1), CNT(P_BIG, 1)
N_1010_AF, N_253_AF, N_2216_AF, N_BIG_AF = CNTF(P_EXP10, 1), CNTF(P_EXP53, 1), CNTF(P_Y2216, 1), CNTF(P_BIG, 1)
N_QJAN = [CNTF(P_QJAN, i) for i in range(3)]
N_59_LF, N_60_LF = CNTF(P_59, 2), CNTF(P_60, 2)
N_JAN_LF, N_PCT_L, N_ESCT_L, N_ESCT_IF = CNTF(P_JAN, 2), CNT(P_PCT, 2), CNT(P_ESCT, 2), CNTF(P_ESCT, 0)
N_10_I = CNT(P_10, 0)
print(u'体量 行 %s 被剔 %s 口径字符 %s 全文件 %s 字节 %s' %
      (NLINES, DROP, [RCOT(i) for i in range(3)], [len(TXT[i]) for i in range(3)], BYTES))
print(u'行列: 输入数据 %d 产物 %d Jun %d Dec %d | 月名口径 I=%s A=%s L(Jan,Jul,Dec)=%d/%d/%d' %
      (N_DATA, N_LEAP, N_JUN, N_DEC, (N_JAN_I, N_JUL_I, N_JUN_I), (N_JAN_A, N_JUL_A, N_JUN_A),
       N_JAN_L, N_JUL_L, N_DEC_L))
print(u'June %s/%s 公有领域 %s/%s Updated %s/%s 列名 %s 哈希 %s 负到期 %s/%s 1980 %d/%d 2017 %d/%d 37 %d/%d'
      % (N_JUNE, N_JUNE_F, N_PD, N_PD_F, N_UPDT, N_UPDT_F, N_MEND, N_HASH, N_NEXP_L, N_NEXP_LF,
         N_1980_I, N_1980_L, N_2017_I, N_2017_L, N_37_I, N_37_L))
print(u'转义: ' + repr(((N_TAB_I0, N_TAB_A, N_TAB_L, N_TAB_IF), (N_ESCT, N_ESCQ, N_ESCN, N_CONT),
                        (N_PCT, N_PCTD, N_PCTS, N_PCT4, N_PCT2),
                        (CNTF(P_ESCT, 1), N_ESCT_L, N_ESCT_IF, N_PCT_L, N_LESE_L))))
print(u'语句: print=%d printf=%d 空=%d 主printf=%d sign=%d 死支=%d EL=%d LL=%d 表=%d/%d(31×%d,30×%d,28×%d)' %
      (N_PRINT, N_PRINTF, N_PEMPTY, N_MAIN, N_SIGN, N_DEAD, N_EL, N_LL, N_MON, N_MDT, N_MD31, N_MD30, N_MD28))
print(u'60/59 口径A=%d/%d L=%d/%d | 全文L=%d/%d | +S口径L=%d -S口径L=%d | 引号字面 %s | 10**10全文A=%d'
      % (N_60_A, N_59_A, N_60_L, N_59_L, N_60_LF, N_59_LF, N_PLUS_L, N_MINUS_L, N_QJAN, N_1010_AF))
assert (N_DATA, N_LEAP, N_JUN, N_DEC, N_JUN + N_DEC) == (28, 27, 11, 16, 27)
assert (N_JAN_I, N_JUL_I, N_JUN_I, N_JAN_A, N_JUL_A, N_JUN_A) == (17, 11, 0, 2, 1, 1)
assert (N_JAN_L, N_JUL_L, N_DEC_L) == (0, 0, 16)
assert (N_60_A, N_59_A, N_60_L, N_59_L) == (2, 2, 27, 0)
assert (N_60_LF, N_59_LF) == (28, 1)
assert (N_PLUS_L, N_MINUS_L, N_PLUS_A, N_MINUS_A) == (27, 0, 1, 1)
assert (N_TAB_I0, N_TAB_A, N_TAB_L, N_TAB_IF) == (0, 31, 162, 66)
assert (N_ESCT, N_ESCQ, N_ESCN, N_CONT) == (15, 8, 6, 8)
assert (N_PCT, N_PCTD, N_PCTS, N_PCT4, N_PCT2) == (30, 4, 5, 3, 14)
assert (N_PCT_L, N_ESCT_L, N_LESE_A, N_LESE_L, N_10_I) == (0, 0, 1, 0, 0)
assert (N_PRINT, N_PRINTF, N_PEMPTY, N_MAIN, N_SIGN) == (56, 5, 7, 1, 2)
assert (N_DEAD, N_EL, N_LL) == (3, 2, 3)
assert (N_MON, N_MDT, N_MD31, N_MD30, N_MD28) == (12, 11, 7, 4, 0)
assert (N_JUNE, N_JUNE_F) == ([0, 0, 0], [5, 0, 1])
assert (N_PD, N_PD_F) == ([0, 1, 0], [1, 2, 1])
assert (N_UPDT, N_UPDT_F, N_EXPO_F, N_MEND, N_HASH) == ([0, 0, 0], [1, 0, 1], [1, 0, 1], [0, 0, 0], [0, 0, 0])
assert (N_HASH_F, (N_NEXP_L, N_BEXP_L, N_NEXP_A, N_NEXP_LF)) == ([1, 0, 0], (0, 0, 0, 2))
assert (N_1980_I, N_1980_L, N_2017_I, N_2017_L) == (1, 0, 1, 0)
assert (N_37_I, N_37_L) == (3, 0)
assert (N_1010_A, N_253_A, N_2216_A, N_BIG_A) == (0, 0, 0, 0)
assert (N_1010_AF, N_253_AF, N_2216_AF, N_BIG_AF) == (2, 3, 2, 1)
assert N_QJAN == [0, 0, 1]
assert (NLINES[0], NLINES[1], NLINES[2]) == (120, 256, 86)
assert (DROP[0], DROP[1], DROP[2]) == (92, 61, 51)
assert (RCOT(0), RCOT(1), RCOT(2)) == (1035, 6464, 809)

# ---------- 展开核对: 复刻 awk 自己的日历 ⇎ 逐行对账 ----------
ABBR = u'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(u' ')
MOND = [31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31]


def cal(s):
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
    return (1600 + qc * 400 + ce * 100 + qy * 4 + yr, mm, day + 1,
            (s // 3600) % 24, (s // 60) % 60, s % 60)


DATA_ROWS = [l.split() for l in LINES[0] if l[:1].isdigit()]
LEAP_ROWS = [l.split(TAB) for l in SRC[2].split(NL) if l.startswith(u'Leap')]
assert (len(DATA_ROWS), len(LEAP_ROWS)) == (28, 27)
TAI = [int(r[1]) for r in DATA_ROWS]
TAI_MIN, TAI_MAX, TAI_SPAN = min(TAI), max(TAI), max(TAI) - min(TAI) + 1
assert (TAI_MIN, TAI_MAX, TAI_SPAN) == (10, 37, 28)
PAIRS = []
for k in range(1, len(DATA_ROWS)):
    c = cal(int(DATA_ROWS[k][0]) - 1)
    lbl = DATA_ROWS[k][3:6]
    out = LEAP_ROWS[k - 1]
    ok = (u'%d' % c[0], ABBR[c[1] - 1], u'%d' % c[2],
          u'%02d:%02d:%02d' % (c[3], c[4], c[5] + 1)) == tuple(out[1:5])
    PAIRS.append((ok, c, lbl, out))
ROWS_OK = len([1 for x in PAIRS if x[0]])
MSHIFT = len([1 for ok, c, lbl, o in PAIRS if o[2] != lbl[1]])
YSHIFT = len([1 for ok, c, lbl, o in PAIRS if o[1] != lbl[2]])
DSHIFT = len([1 for ok, c, lbl, o in PAIRS if o[3] != lbl[0]])
FLOTF = sorted(set(len(o) for o in [x[3] for x in PAIRS]))
assert ROWS_OK == 27 and (MSHIFT, YSHIFT, DSHIFT) == (27, 16, 27)
assert FLOTF == [7]
assert [p[3][2] for p in PAIRS].count(u'Jun') == 11 and [p[3][2] for p in PAIRS].count(u'Dec') == 16
assert [p[3][1] for p in PAIRS if p[3][2] == u'Dec'].count(u'1972') == 1

# BEGIN 的 print 逐条发射 ⇎ 产物头部逐行
blk = TXT[1].split(u'BEGIN {')[1].split(NL + u'}')[0]
EMIT = []
for l in blk.split(NL):
    s = l.strip()
    if s.startswith(u'print "'):
        lit = s[s.index(u'"') + 1:s.rindex(u'"')]
        for a, b in ((BS + u'n', NL), (BS + u't', TAB), (BS + u'"', u'"'), (BS + BS, BS)):
            lit = lit.replace(a, b)
        EMIT.append(lit)
BPRINT = len(EMIT)
HEADOK = len([k for k, e in enumerate(EMIT) if LINES[2][k] == e])
BLANKHEAD = len([e for e in EMIT if e == u''])
assert (BPRINT, HEADOK, BLANKHEAD) == (40, 40, 5)
ENDBLANK = TXT[1].split(u'END {')[1].split(NL + u'}')[0].count(u'print ""')
assert (N_PEMPTY, BLANKHEAD + ENDBLANK) == (7, 5 + 2)
ENDLINES = NLINES[2] - BPRINT - N_LEAP
assert ENDLINES == 19
TAILN = len([l for l in LINES[2][-3:] if l and l in TXT[0]])
assert TAILN == 2
UP = re.search(u'(?m)^#\\$[ \\t]+(\\d+)', TXT[0]).group(1)
EX = re.search(u'(?m)^#@[ \\t]+(\\d+)', TXT[0]).group(1)
PU = re.search(u'(?m)^#updated (\\d+)', TXT[2]).group(1)
PE = re.search(u'(?m)^#expires (\\d+)', TXT[2]).group(1)
EPOCH = ((1970 - 1900) * 365 + 17) * 24 * 60 * 60
GAP = int(EX) - int(UP)
YEARSEC = 365 * 24 * 60 * 60
SHORT = YEARSEC - GAP
assert (int(UP) - int(PU), int(EX) - int(PE)) == (EPOCH, EPOCH)
assert (EPOCH, GAP, SHORT) == (2208988800, 30816903, 719097)
assert (cal(0)[0], cal(EPOCH)[0], cal(10 ** 10)[0], cal(2 ** 53)[0]) == (1900, 1970, 2216, 285428681)
assert (cal(int(UP))[:4], cal(int(EX))[:4]) == ((2026, 7, 6, 7), (2027, 6, 28, 0))
print(u'对账: 吻合 %d/%d 月换 %d 年换 %d 日换 %d | BEGIN %d 发射 %d 空 %d 尾部 %d 行 | END %d 行 | DTAI %d..%d'
      % (ROWS_OK, N_LEAP, MSHIFT, YSHIFT, DSHIFT, BPRINT, HEADOK, BLANKHEAD, TAILN, ENDLINES, TAI_MIN, TAI_MAX))
print(u'日历: epoch %d 年 %d 间隔 %d 短 %d (%.2f 天) | 10**10→%d 2**53→%d'
      % (EPOCH, cal(EPOCH)[0], GAP, SHORT, GAP / 86400.0, cal(10 ** 10)[0], cal(2 ** 53)[0]))

# ---------- 锚点 ----------
AN, LBL = {}, {}


def pick(txt, needle, key, color):
    hits = [l for l in txt.split(NL) if needle in l]
    assert len(hits) == 1, (key, needle, len(hits))
    lit = hits[0]
    assert txt.count(lit) == 1 and 12 <= len(lit) <= 460, (key, len(lit), txt.count(lit))
    AN[key], LBL[key] = lit, color


pick(TXT[0], u'2272060800', u'i_row_first', LI)
pick(TXT[0], u'2287785600', u'i_row_jul72', LI)
pick(TXT[0], u'3692217600', u'i_row_last', LI)
pick(TXT[0], u'#NTP Time', u'i_header', LI)
pick(TXT[0], u'and September', u'i_pref', LI)
pick(TXT[0], u'theoretically possible', u'i_neg', LI)
pick(TXT[0], u'#h', u'i_hash', LI)
pick(TXT[0], u'3992312697', u'i_updated', LI)
pick(TXT[0], u'4023129600', u'i_expires', LI)
pick(TXT[0], u'This file is in the public domain', u'i_public', LI)
pick(TXT[0], u'MJD = X/86400', u'i_mjd', LI)
pick(TXT[1], u'# Generate zic format', u'a_title', LA)
pick(TXT[1], u'# exact integer arithmetic', u'a_horizon', LA)
pick(TXT[1], u'print "# Allowance', u'a_first_print', LA)
pick(TXT[1], u'print "# This file is in the public domain', u'a_public_print', LA)
pick(TXT[1], u'print "# Typical lines', u'a_typical', LA)
pick(TXT[1], u'Leap' + TAB + u'YEAR' + TAB + u'MON' + TAB + u'DAY' + TAB + u'23:59:60', u'a_pos_shape', LA)
pick(TXT[1], u'sign = "23:59:60', u'a_live_sign', LA)
pick(TXT[1], u'sign = "23:59:59', u'a_dead_sign', LA)
pick(TXT[1], u'printf "Leap', u'a_one_statement', LA)
pick(TXT[1], u'sstamp_to_ymdhMs(NTP_timestamp - 1', u'a_minus1', LA)
pick(TXT[1], u'if (old_TAI_minus_UTC) {', u'a_guard', LA)
pick(TXT[1], u'monthabbr[ 1] = "Jan"', u'a_jan_def', LA)
pick(TXT[1], u'monthabbr[ 6] = "Jun"', u'a_jun_def', LA)
pick(TXT[1], u'monthabbr[ 7] = "Jul"', u'a_jul_def', LA)
pick(TXT[1], u'ss_mon_days[ 9] = 31', u'a_mond', LA)
pick(TXT[1], u'epoch_minus_NTP =', u'a_epoch', LA)
pick(TXT[1], u'No Expires line', u'a_dead1', LA)
pick(TXT[1], u'#(updated time unknown)', u'a_dead2', LA)
pick(TXT[1], u'printf "%sExpires', u'a_expires_fmt', LA)
pick(TXT[1], u'ss_NTP = 109513', u'a_ntp', LA)
pick(TXT[1], u'printf "' + BS + u'n%s", last_lines', u'a_copier', LA)
pick(TXT[1], u'[Uu]pdated through', u'a_finder', LA)
pick(TXT[2], u'# Allowance for leap seconds', u'l_first_line', LL)
pick(TXT[2], u'# This file is in the public domain', u'l_public', LL)
pick(TXT[2], u'The first (', u'l_named_row', LL)
pick(TXT[2], u'# Typical lines', u'l_typical', LL)
pick(TXT[2], u'Leap' + TAB + u'YEAR' + TAB + u'MON' + TAB + u'DAY' + TAB + u'23:59:60', u'l_pos_shape', LL)
pick(TXT[2], u'23:59:59', u'l_neg_shape', LL)
pick(TXT[2], u'Leap' + TAB + u'1972' + TAB + u'Jun', u'l_row_first', LL)
pick(TXT[2], u'Leap' + TAB + u'2016' + TAB + u'Dec', u'l_row_last', LL)
pick(TXT[2], u'#Expires 2027', u'l_commented_expires', LL)
pick(TXT[2], u'#updated 1783323897', u'l_updated', LL)
pick(TXT[2], u'#expires 1814140800', u'l_expires', LL)
pick(TXT[2], u'Updated through IERS', u'l_tail_bulletin', LL)
pick(TXT[2], u'File expires on', u'l_tail_expiry', LL)
pick(TXT[2], u'# This file is generated automatically', u'l_generated', LL)
pick(TXT[2], u'# All leap-seconds are Stationary', u'l_stationary', LL)
pick(TXT[2], u'a bit less than one year', u'l_year_note', LL)
for k, v in AN.items():
    assert v in ([TXT[0], TXT[1], TXT[2]][{LI: 0, LA: 1, LL: 2}[LBL[k]]]), (k, v[:40])
ANCH, UANCH = len(AN), len(set(AN.values()))
NI_AN = len([k for k, x in LBL.items() if x == LI])
NA_AN = len([k for k, x in LBL.items() if x == LA])
NL_AN = ANCH - NI_AN - NA_AN
print(u'anchors=%d uniq=%d I=%d A=%d L=%d 平均长度=%.0f' %
      (ANCH, UANCH, NI_AN, NA_AN, NL_AN, sum(len(v) for v in AN.values()) / float(ANCH)))

# ---------- 判词 ----------
G = []


def A(head, items, gloss):
    G.append(u'%s %s ⇒ %s' % (head, u' ‖ '.join([u'⟦%s⟧⟨%s⟩' % (LBL[k], AN[k]) for k in items]), gloss))


A(u'🧭 体例', [u'i_row_first', u'a_one_statement', u'l_row_first'],
  u'三个源排在同一条因果链上: 输入 ⟦%s⟧⟨%s⟩(NIST/IERS 的 leap-seconds.list, 数据 %d 行, 每行“NTP 秒 ⇎ DTAI 秒 ⇎ # 日 月 年”) '
  u'⇎ 程序 ⟦%s⟧⟨%s⟩(%d 行 awk, 全部数据行只由那一句 printf 发射) ⇎ 产物 ⟦%s⟧⟨%s⟩(zic 格式的 leapseconds, 数据 %d 行)。'
  u'与上一条“目录行 ⇎ 它指着的原文”不同: 那里的联结要读者按字段重建, 这里的联结可以**执行**——本机用 gawk 把程序跑在输入上, '
  u'所得与在库那份逐字节相同(散列写在 src 行, 版本与命令写在解读注)。于是可核性升到四级: 能数的记号 ⇎ 能展开复算的 ⇎ 能执行复现的 ⇎ 只有工具知道的。'
  u'审计口径把三份文件的注释行各剔掉 %d/%d/%d 行(输入与产物的绝大部分都是注释), 口径内只剩可行文字: %d ⇎ %d ⇎ %d 字符。'
  u'与本库另一条时区条(比同一份输入的不同时刻)也不同: 本条比同一时刻上的三个不同角色。'
  % (LI, AN[u'i_row_first'], N_DATA, LA, AN[u'a_one_statement'], NLINES[1], LL, AN[u'l_row_first'], N_LEAP,
     DROP[0], DROP[1], DROP[2], RCOT(0), RCOT(1), RCOT(2)))
A(u'✂️ 一句程序撑起二十七行', [u'a_one_statement', u'a_guard', u'i_row_first', u'l_row_first'],
  u'产物的 %d 行数据全部出自程序里**那一句** ⟦%s⟧⟨%s⟩(整份文件它只出现一次, 0 键核对)。'
  u'程序的行首发射语句: print ⟦%s⟧⟨%s⟩ 起共 %d 条, printf 共 %d 条(两个数各自回源, 求和留给读者), 要交代 %d 行产物: '
  u'BEGIN 块 %d 条 print 与产物头 %d 行**按序逐行相等**(助手 B48_HEADOK 逐条比对), 其中 %d 条是空行发射; '
  u'两端抽样: 产物首行 ⟦%s⟧⟨%s⟩ ⇎ 程序 ⟦%s⟧⟨%s⟩, 产物 ⟦%s⟧⟨%s⟩ ⇎ 程序 ⟦%s⟧⟨%s⟩; '
  u'剩下的 %d 行由 END 块产出, 而 %d = %d − %d − %d(减法即证, 写在 0 键里)。'  u'输入却有 %d 行数据: 差额一行不丢, 是被守卫 ⟦%s⟧⟨%s⟩ 吃掉的——首行 ⟦%s⟧⟨%s⟩ 只标“现行 UTC 定义的起点”, 不是闰秒; '
  u'产物 ⟦%s⟧⟨%s⟩ 那种“带真数值的行”在程序里 0 处(程序只持有带说明符的骨架)。'
  u'判词: 生成器的压缩不在字符层而在**语句层**——“文件有多少行”要换成“多少条发射语句 × 各跑几次”, 而次数由守卫决定。'
  % (N_LEAP, LA, AN[u'a_one_statement'], LA, AN[u'a_first_print'], N_PRINT, N_PRINTF, NLINES[2],
     BPRINT, HEADOK, BLANKHEAD,
     LL, AN[u'l_first_line'], LA, AN[u'a_first_print'], LL, AN[u'l_typical'], LA, AN[u'a_typical'],
     ENDLINES, ENDLINES, NLINES[2], BPRINT, N_LEAP, N_DATA,
     LA, AN[u'a_guard'], LI, AN[u'i_row_first'], LL, AN[u'l_row_first']))
A(u'📉 一整列数字被压成一个符号', [u'i_row_last', u'l_row_first', u'a_live_sign', u'a_dead_sign'],
  u'输入的第二列是 TAI−UTC: ⟦%s⟧⟨%s⟩ 那行的 10 起、到 37 止, %d 个数**逐个连续**(要读完整列才知道, 助手 B48_TAISPAN 复算)。'
  u'程序只问“比上一行大还是小”, 于是产物每行只留下那一个**符号**: ⟦%s⟧⟨%s⟩ 里的加号 %d 处, '
  u'减号写法 ⟦%s⟧⟨%s⟩ 在产物里 0 处(0 键)——不是不能有: 程序两种时刻各备一次(⟦%s⟧⟨%s⟩ 那种正号形式 %d 处 ⇎ 负号形式 %d 处, 等式在 0 键), '
  u'只是 %d 行数据里没有一次遇上。输入还专门写着 ⟦%s⟧⟨%s⟩ 一句“理论上可以有负闰秒”。'
  u'数值一个都没过去: 37 在产物口径内 0 处(0 键); 分隔符也换了层——输入数据行用空格(口径内制表符 0 处 ⇎ 整份文件 %d 个全在注释行里), '
  u'产物用制表符 %d 个 = 每行 %d 个 × %d 行(等式在 0 键)。'
  u'判词: 说“丢了信息”要具体到哪一列、留下了那一列的什么投影——这里留下一列的**差分符号**, 丢掉整列的**大小与刻度**。'
  % (LI, AN[u'i_row_last'], TAI_SPAN, LL, AN[u'l_row_first'], N_PLUS_L,
     LA, AN[u'a_dead_sign'], LA, AN[u'a_pos_shape'], N_60_A, N_59_A, N_DATA,
     LI, AN[u'i_neg'], N_TAB_IF, N_TAB_L, 6, N_LEAP))
A(u'📅 减一秒把每个日期的名字都改了', [u'i_row_jul72', u'l_row_first', u'a_minus1', u'l_named_row'],
  u'第二行数据 ⟦%s⟧⟨%s⟩ 的注释写着“1 Jul 1972”, 产物对应行却是 ⟦%s⟧⟨%s⟩——差在程序那句 ⟦%s⟧⟨%s⟩: '
  u'它换算的是**端点前一秒**, 于是每一行都退回上一天。逐行核对 %d 行(助手把 awk 自己的日历照抄进审计器复算): '
  u'月份标签 %d/%d 行被改掉、日 %d/%d 行被改掉、年 %d/%d 行被改掉, 而被改年的恰是那 %d 个“1 Jan”开头的行(1 月 1 日减一秒退到前一年)。'
  u'词汇因此整批换人: 输入口径内只有 Jan %d 处、Jul %d 处, Jun 0 处、Dec 0 处; 产物反过来只有 Jun %d 处、Dec %d 处, Jan/Jul 各 0 处(全在 0 键)。'
  u'最硬的两枚证物是年份: 输入的“1 Jan 1980”与“1 Jan 2017”在口径内各 1 处, 而 1980 与 2017 在产物里各 0 处——'
  u'它们被换算成了 1979 与 2016。产物里那条“形状示范”行 ⟦%s⟧⟨%s⟩ 唯一, 而它写的时刻在数据行里逐字重演 %d 次; '
  u'换号示范 ⟦%s⟧⟨%s⟩ 那种时刻在数据行 0 处(全文件仅 %d 处, 就是这条示范本身)。'
  u'判词: 换算不改数据、只改**名字**, 而且改得逐行都是同一方向; 若按字符串把两份表的日期对齐, 会得到“零行相同”的假结论。'
  % (LI, AN[u'i_row_jul72'], LL, AN[u'l_row_first'], LA, AN[u'a_minus1'], ROWS_OK,
     MSHIFT, N_LEAP, DSHIFT, N_LEAP, YSHIFT, N_LEAP, N_DEC,
     N_JAN_I, N_JUL_I, N_JUN, N_DEC_L, LL, AN[u'l_pos_shape'], N_60_L,
     LL, AN[u'l_neg_shape'], N_59_LF))
A(u'🗝 程序自带另一套月份词汇', [u'a_jan_def', u'a_jun_def', u'a_jul_def', u'a_mond'],
  u'产物的月名不来自输入, 来自程序的表: ⟦%s⟧⟨%s⟩ 起共 %d 条 monthabbr 定义(条数在 0 键核对), '
  u'产物只用到 Jun 与 Dec, 其余 %d 个名字在产物口径内 0 处; 连输入自己写的 Jan/Jul 也是经这张表**翻译**后才可能进产物, '
  u'而翻译结果是别的名字(见上条)。程序还定义着输入用不到的 Jul ⟦%s⟧⟨%s⟩。'
  u'另一张表更见结构: 月长表 ⟦%s⟧⟨%s⟩ 只有 %d 条(31 出现 %d 次、30 出现 %d 次, 28 一次也没有, 0 键), '
  u'因为程序把年从三月起算、二月被“闰四年多一天”吸收——十二个月名 ⇎ 十一个月长, 差的那一处也在 0 键。'
  u'判词: 三份文件各有一套时间词汇, 交集近空; “谁的词进了产物”要看程序里那张表, 而不是输入里的写法。'
  % (LA, AN[u'a_jan_def'], N_MON, N_MON - 2, LA, AN[u'a_jul_def'],
     LA, AN[u'a_mond'], N_MDT, N_MD31, N_MD30))
A(u'🔀 同一个句子, 三份文件三种拼法', [u'i_public', u'a_public_print', u'l_public', u'l_named_row'],
  u'“公有领域”那句声明在三份文件里都在: 口径内 %d ⇎ %d ⇎ %d(输入与产物那两处都是注释行, 被口径剔掉), '
  u'全文件 %d ⇎ %d ⇎ %d ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩。四份副本(程序两份)里审计口径只看见一份——口径 ⇎ 全文必须成对报。'
  u'引号又是另一层: 程序把引号写成转义形式(转义引号 %d 处), 于是“带引号的 1 Jan 1972”这个字面在输入与程序里 0 处、在产物里恰好 1 处 ⟦%s⟧⟨%s⟩; '
  u'而这 1 处是程序对**输入格式**的描述, 不是任何一行数据。'
  u'分隔符同理换层: 程序里 %d 个转义制表符 ⇎ 产物 0 个(它只有真制表符 %d 个); '
  u'百分号 %d 枚: 说明符四型 %%d %d、%%s %d、%%.4d %d、%%.2d %d, 余下 4 枚是取余运算符(总数减五段为 0 写在 0 键) ⇎ 产物 0 枚——说明符全被值换掉。'
  u'判词: 同一句话在链上每走一站就换一次拼法; 逐字比对必须先把“转义层”剥掉, 否则三处都在的句子会报成“两边都没有”。'
  % (N_PD[0], N_PD[1], N_PD[2], N_PD_F[0], N_PD_F[1], N_PD_F[2],
     LI, AN[u'i_public'], LA, AN[u'a_public_print'], LL, AN[u'l_public'],
     N_ESCQ, LL, AN[u'l_named_row'], N_ESCT, N_TAB_L, N_PCT, N_PCTD, N_PCTS, N_PCT4, N_PCT2))
A(u'🫥 拷贝的两行在口径里两边都是 0', [u'i_hash', u'a_copier', u'l_tail_bulletin', u'i_pref'],
  u'产物末尾 %d 行 ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩ 逐字来自输入(助手在全文里比对, 命中 %d 行), 由程序那句 ⟦%s⟧⟨%s⟩ 原样搬运; '
  u'而在审计口径里这两串在两份文件里**都是** 0——两个 0 数字相同, 关系却是拷贝; 数数看不到, 必须比全文。'
  u'输入的完整性自证 ⟦%s⟧⟨%s⟩ 那行哈希: 口径内 0 ⇎ 全文 1, 程序既不读也不写, 产物里 0 处(两条 0 成因不同)。'
  u'程序用来“捡回这两行”的正则 ⟦%s⟧⟨%s⟩ 又是一种拼法(带方括号与 [Uu] 式类), 它的字面在输入里 0 处——规则与数据互不见对方的写法。'
  u'输入还写着 ⟦%s⟧⟨%s⟩(首选六月与十二月), 可它自己的数据行只有 Jan 与 Jul 两种标签, June 这个词在两份表的数据侧 0 处(全文 %d ⇎ 0 ⇎ %d)。'
  u'判词: “两边都是 0”至少有三种成因(真没有 ⇎ 被口径剔掉 ⇎ 换了拼法), 本条把三种各自成对报出, 不让它们共用一个结论。'
  % (TAILN, LL, AN[u'l_tail_bulletin'], LL, AN[u'l_tail_expiry'], TAILN,
     LA, AN[u'a_copier'], LI, AN[u'i_hash'], LA, AN[u'a_finder'], LI, AN[u'i_pref'],
     N_JUNE_F[0], N_JUNE_F[2]))
A(u'⏳ 程序说自己活到哪一年, 用它自己的日历能核', [u'a_horizon', u'a_ntp', u'a_epoch', u'l_updated', u'l_expires'],
  u'程序头部 ⟦%s⟧⟨%s⟩ 作两个断言: POSIX 要求 awk 精确整数只到 10**10 秒(即“只活到 %d 年”), 而实际的 double 实现到 2**53 秒(即 %d 年)。'
  u'这两个数不在产物里, 在程序里也只活在**被口径剔掉的注释**中(口径内 10**10 与 2**53 各 0 处, 全文 %d ⇎ %d 处; 2216 与 285,428,681 口径内也各 0, 全文 %d ⇎ %d)。'
  u'但不必信权威: 把程序自带的日历(⟦%s⟧⟨%s⟩ 的 109513 日纪元 + 四百年/百年/四年/年降档)照抄进审计器, '
  u'10**10 秒落在 %d、2**53 秒落在 %d, 与散文逐字相等(两条等式各是一个键)。'
  u'同一套算术还核住封套: 输入的 #$ ⇎ #@ 两枚 NTP 秒 ⟦%s⟧⟨%s⟩ ⇎ ⟦%s⟧⟨%s⟩ 与产物 ⟦%s⟧⟨%s⟩ ⇎ ⟦%s⟧⟨%s⟩ 之间, 恰好差程序 ⟦%s⟧⟨%s⟩ 那行的 %d(=七十年 × 每天 86400 秒, 其中十七个闰日); '
  u'而两枚时间戳相隔 %d 秒, 比整年少 %d 秒(%.2f 天), 产物注释 ⟦%s⟧⟨%s⟩ 说的“略少于一年”在这一份数据上成立。'
  u'判词: 程序对**自身寿命**的断言住在散文里, 却能用它自己的算法复算; 换掉算法就不再是同一份产物——可执行性正是这类条目的裁判。'
  % (LA, AN[u'a_horizon'], cal(10 ** 10)[0], cal(2 ** 53)[0], N_1010_AF, N_253_AF, N_2216_AF, N_BIG_AF,
     LA, AN[u'a_ntp'], cal(10 ** 10)[0], cal(2 ** 53)[0],
     LI, AN[u'i_updated'], LI, AN[u'i_expires'], LL, AN[u'l_updated'], LL, AN[u'l_expires'], LA, AN[u'a_epoch'],
     EPOCH, GAP, SHORT, GAP / 86400.0, LL, AN[u'l_year_note']))
A(u'🚫 三向缺席, 方向各不相同', [u'a_dead1', u'a_dead2', u'a_expires_fmt', u'l_commented_expires', u'i_header'],
  u'程序有而产物无: %d 条死支发射各 1 处 ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩(外加第三句“expires 未知”), 产物 0 处——'
  u'它们对应的条件在 %d 行数据里没有一次成立; 标识符更是整批消失(EXPIRES_LINE %d 处、last_lines %d 处、monthabbr 定义 %d 条, 产物全 0)。'
  u'产物有而程序无: %d 行 ⟦%s⟧⟨%s⟩ 的具体日期、%d 个制表符、输入的列名头 ⟦%s⟧⟨%s⟩(“Day Month Year”三个词程序从未写过, 三份文件的口径内都是 0)。'
  u'输入有而两边无: 那行哈希、#$ 与 #@ 两枚秒的**写法**(程序只按行首字符匹配, 从不复写这两枚)。'
  u'还有一处开关只能反推: 产物的到期行 ⟦%s⟧⟨%s⟩ 带着注释符, 而“不带注释符的 Expires 行”两份文件都 0 处——'
  u'程序那句三元 ⟦%s⟧⟨%s⟩ 运行时取了加“#”的一支(调用时没给 EXPIRES_LINE), 这条**分支选择**在两份文件里都只留下结果、不留痕迹。'
  u'判词: 三份文件互不包含, 连方向也不对称; 缺席要按“谁的哪种写法”分列, 一句“产物缺原文”会把三种缺席糊成一个。'
  % (2, LA, AN[u'a_dead1'], LA, AN[u'a_dead2'], N_DATA, N_EL, N_LL, N_MON,
     N_LEAP, LL, AN[u'l_row_last'], N_TAB_L, LI, AN[u'i_header'],
     LL, AN[u'l_commented_expires'], LA, AN[u'a_expires_fmt']))
A(u'∴ 骨架', [u'i_mjd', u'l_stationary', u'a_typical'],
  u'① 因果链可以执行复现, 这比“展开复算”更高一级: 跑上游工具得到同一散列, 联结就不靠读者重建; '
  u'② 生成器的账按**语句 × 次数**记, 不按行数记(%d 条 print ⇎ %d 条 printf ⇒ 产物 %d 行, 其中一句跑 %d 次, 守卫吃掉一次); '
  u'③ 丢列 ≠ 丢全部: %d 个整数的列被压成 %d 个差分符号, 说清“留下什么投影”才算说清压缩; '
  u'④ 一次换算(减一秒)能把 %d/%d 行的月名与 %d/%d 行的年名改掉, 而词汇来自程序的表不是输入; '
  u'⑤ 同一句话在链上换拼法(转义引号、转义制表符、说明符 ⇎ 真制表符与值), 逐字比对会在三份文件间全盘失明; '
  u'⑥ “两边都是 0”可能是拷贝(同被口径剔掉的行), 数数看不到, 要全文比; '
  u'⑦ 程序对自身的断言(活到 %d 年、七十年含十七闰日、略少于一年)可由它自己的算法复算, 不必引外部权威; '
  u'⑧ 死支与未取的三元支在产物里是 0, 而 0 不代表能力不存在; '
  u'⑨ 输入自带的完整性哈希不被搬运, 产物的可信度只剩外部散列——四级可核性要分开报。'
  u'判词: “一个源 ⇎ 另一个源”在这里不够用; 要报的是“谁生成谁、生成时哪一列被投影、哪一层被换写、哪一支没被走到”。'
  % (N_PRINT, N_PRINTF, NLINES[2], N_LEAP, TAI_SPAN, N_PLUS_L, MSHIFT, N_LEAP, YSHIFT, N_LEAP,
     cal(10 ** 10)[0]))
A(u'ℒmethod', [u'i_row_jul72', u'a_one_statement', u'l_row_last', u'a_finder'],
  u'读“输入 ⇎ 生成它的程序 ⇎ 程序的产物”: 第一步先确认联结**能不能执行**——若上游工具在本机可用, 就把它当作最强的核验(散列相等即可销案), '
  u'不能执行才退回“按程序算法复算 + 逐行对账”; 第二步把程序的发射语句列成表(每条 print 一次 ⇎ 每条在循环里的 printf 跑 n 次), '
  u'用“语句 × 次数 + 守卫”解释产物的行数, 而不是直接数行; '
  u'第三步对每一列数据问三个问题: 它过去了吗 ⇎ 它以什么投影过去(差分符号、常量、被丢弃) ⇎ 它的**写法**换没换(空格 ⇎ 制表符、字面 ⇎ 转义); '
  u'第四步凡跨三份文件搜词一律同时报“口径内 ⇎ 全文”, 并对每个“两边都是 0”查明是缺、是被剔、还是换拼法; '
  u'第五步把程序散文里的自述寿命/纪元拿它自己的算法复算一遍(⟦%s⟧⟨%s⟩ 那种换算要连“-1”一起照抄)。'
  u'核验口径: ⟦%s⟧⟨%s⟩ 一类标 %s 只在输入内数, ⟦%s⟧⟨%s⟩ 一类标 %s 只在程序内数, ⟦%s⟧⟨%s⟩ 一类标 %s 只在产物内数; '
  u'程序用来抓注释的正则 ⟦%s⟧⟨%s⟩ 与它抓到的行是两套写法, 不可互推。'
  % (LA, AN[u'a_minus1'], LI, AN[u'i_row_jul72'], LI, LA, AN[u'a_one_statement'], LA, LL, AN[u'l_row_last'], LL,
     LA, AN[u'a_finder']))
A(u'✂️ 为什么这份编码比摘要窗口长', [u'l_generated', u'a_title'],
  u'三份原料都很小: 口径内 %d ⇎ %d ⇎ %d 字符, 而判词要说的是**一条因果链上的对账**: '
  u'发射语句的账、列的投影、换算带来的改名、转义层、口径看不见的拷贝。摘要段只能取锚点触到的窗口 ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩, '
  u'而“%d 行逐行等于输入减一秒再走程序自带日历”“%d 条发射与产物头 %d 行按序相等”这类结论住在展开与执行里, 不住在任何窗口里。'
  u'本条三份文件都很小(磁盘 %s ⇎ %s ⇎ %d 字节), 保留率因此天然偏高——读它要按“四级可核性各占几项”来读, 而不是按“少说了多少话”。'
  % (RCOT(0), RCOT(1), RCOT(2),
     LL, AN[u'l_generated'], LA, AN[u'a_title'], ROWS_OK, BPRINT, HEADOK,
     BYTES[0], BYTES[1], BYTES[2]))

BODY = NL.join(G)
GLOS = len(G)
HEAD_MD = (u'# B48 输入 ⇎ 生成它的程序 ⇎ 程序的产物：三份文件讲同一件事，可谁都不按对方的写法写它\n\n'
           u'src: %s (NIST/IERS 的 leap-seconds.list, 数据 %d 行, 行格式“NTP 秒 ⇎ DTAI ⇎ # 日 月 年”, '
           u'口径内 %d 字符 ⇎ 全文件 %d 字符 ⇎ 磁盘 %d 字节, 注释行 %d 行被口径剔掉, 纯 ASCII(转义制表符 0 处而真制表符 %d 处全在注释里), '
           u'sha256 %s) ⇎ %s (把它转成 zic 格式的 leapseconds.awk, %d 行, 发射语句 %d 条(print %d ⇎ printf %d), '
           u'口径内 %d 字符 ⇎ 全文件 %d 字符 ⇎ 磁盘 %d 字节, sha256 %s) ⇎ %s (产物 leapseconds, %d 行(数据 %d 行 ⇎ 头部 %d 行由 BEGIN 逐行发射 ⇎ 尾部 %d 行由 END 产出), '
           u'口径内 %d 字符 ⇎ 全文件 %d 字符 ⇎ 磁盘 %d 字节, sha256 %s)\n'
           u'；联结可执行复现: 本机 gawk 把程序跑在输入上所得与在库产物逐字节相同(版本、命令与散列等式见 ⛓解读注, 属工具侧断言); '
           u'展开复算的十个数(吻合 %d/%d ⇎ 月改 %d ⇎ 年改 %d ⇎ 日改 %d ⇎ DTAI 连续 %d ⇎ BEGIN 按序 %d ⇎ 空行 %d ⇎ 纪元差 %d ⇎ 间隔 %d)由 audit.py 里的 B48_* 函数独立复算\n'
           u'tags: 因果链 ⇎ 可执行复现 语句×次数 列投影 差分符号 减一秒换算 词汇表 转义层 口径⇎全文 三向缺席\n\n'
           % (RI, N_DATA, RCOT(0), len(TXT[0]), BYTES[0], DROP[0], N_TAB_IF, SHA[0],
              RA, NLINES[1], N_PRINT + N_PRINTF, N_PRINT, N_PRINTF, RCOT(1), len(TXT[1]), BYTES[1], SHA[1],
              RL, NLINES[2], N_LEAP, BPRINT, ENDLINES, RCOT(2), len(TXT[2]), BYTES[2], SHA[2],
              ROWS_OK, N_LEAP, MSHIFT, YSHIFT, DSHIFT, TAI_SPAN, HEADOK, BLANKHEAD, EPOCH, GAP))
MD = (HEAD_MD + u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + BODY +
      u'\n\n## ⛓解读注\n<!--FILL-->\n')
io.open(ENTRY, u'w', encoding='utf-8').write(MD)
print(u'entry written: %s body_chars=%d anchors=%d gloss_lines=%d' % (ENTRY, len(BODY), ANCH, GLOS))

# ---------- DERIV(键名即数值; 等式/缺席/“恰好一处”折进 0 键) ----------
D2 = {}


def put(val, expr):
    f = float(val)
    k = u'%d' % f if f == int(f) else u'%g' % f
    assert k not in D2, (k, expr[:70], D2.get(k))
    D2[k] = expr
    return k


def CE(pat, i):
    return u"CNT(%r,%d)" % (pat, i)


def CF(pat, i):
    return u"CNTF(%r,%d)" % (pat, i)


put(TAI_SPAN, u'B48_TAISPAN()')
put(N_LEAP, CE(P_LEAP, 2))
put(N_JUN, CE(P_JUN30, 2))
put(N_DEC, CE(P_DEC31, 2))
put(N_JAN_I, CE(P_JAN, 0))
put(N_PCT4, CE(P_PCT4, 1))
put(N_PCTD, CE(P_PCTD, 1))
put(N_ESCQ, CE(P_ESCQ, 1))
put(N_MON, CE(P_MON, 1))
put(N_PCT2, CE(P_PCT2, 1))
put(N_ESCT, CE(P_ESCT, 1))
put(ENDLINES, u'B48_ENDLINES()')
put(N_PCT, CE(P_PCT, 1))
put(BPRINT, u'B48_BPRINT()')
put(DROP[2], u'B48_DROP(2)')
put(N_PRINT, CE(P_PRINT, 1))
put(DROP[1], u'B48_DROP(1)')
put(N_TAB_IF, CF(P_TAB, 0))
put(NLINES[2], u'B48_LINES(2)')
put(DROP[0], u'B48_DROP(0)')
put(NLINES[0], u'B48_LINES(0)')
put(N_TAB_L, CE(P_TAB, 2))
put(NLINES[1], u'B48_LINES(1)')
put(RCOT(2), u'RCOT(2)')
put(RCOT(0), u'RCOT(0)')
put(RCOT(1), u'RCOT(1)')
for _i in range(3):
    put(BYTES[_i], u'B48_BYTES(%d)' % _i)
put(cal(10 ** 10)[0], u'B48_Y10()')
put(EPOCH, u'B48_EPOCH()')
put(24 * 60 * 60, u"L('24')*L('60')*L('60')")
put(GAP, u'B48_GAP()')
put(SHORT, u'B48_SHORT()')
put(cal(2 ** 53)[0], u'B48_Y53()')
put(round(GAP / 86400.0, 2), u'round(B48_GAP()/86400,2)')

AB = [
    # 真缺席(口径内 0 处)
    CE(P_JUN, 0), CE(P_DEC, 0), CE(P_MEND, 0), CE(P_MEND, 1), CE(P_MEND, 2),
    CE(P_TAB, 0), CE(P_HASH, 0), CE(P_HASH, 2), CE(P_PCT, 2), CE(P_ESCT, 2), CE(P_LESE, 2),
    CE(P_NEXP, 2), CE(P_BEXP, 2), CE(P_NEXP, 1), CE(P_MD28, 1), CE(P_37, 2),
    CE(P_MINUS, 2), CE(P_59, 2), CE(P_JAN, 2), CE(P_JUL, 2), CE(P_Y1980, 2), CE(P_Y2017, 2),
    CE(P_LEAP, 1),
    CE(P_EXP10, 1), CE(P_EXP53, 1), CE(P_Y2216, 1), CE(P_BIG, 1), CE(P_JUNE, 1), CE(P_JUNE, 2),
    CF(P_QJAN, 0), CF(P_QJAN, 1), CF(P_ESCT, 0), CF(P_ESCT, 2), CF(P_JUNE, 1),
    # 恰好一处
    CE(P_MAIN, 1) + u'-L(\'1\')', CF(P_QJAN, 2) + u'-L(\'1\')',
    CE(P_LESE, 1) + u'-L(\'1\')', CE(u'ss_NTP = 109513', 1) + u'-L(\'1\')',
    # 有意义的等式(全部折进同一个 0 键)
    CE(P_DATA, 0) + u'-' + u'B48_TAISPAN()',
    u'(' + CE(P_JUN30, 2) + u'+' + CE(P_DEC31, 2) + u'-' + CE(P_LEAP, 2) + u')',
    CE(P_DEC, 2) + u'-' + CE(P_DEC31, 2),
    CE(P_JUL, 0) + u'-' + CE(P_JUN30, 2),
    CE(P_60, 2) + u'-' + CE(P_LEAP, 2),
    CE(P_PLUS, 2) + u'-' + CE(P_60, 2),
    CF(P_60, 2) + u'-' + CE(P_60, 2) + u'-L(\'1\')',
    CE(P_TAB, 2) + u'-6*' + CE(P_LEAP, 2),
    CE(P_60, 1) + u'-' + CE(P_59, 1),
    CE(P_PLUS, 1) + u'-' + CE(P_MINUS, 1),
    CF(P_PD, 0) + u'-' + CE(P_PD, 0) + u"-L('1')",
    CF(P_PD, 2) + u'-' + CE(P_PD, 2) + u"-L('1')",
    CE(P_PCT, 1) + u'-' + CE(P_PCTD, 1) + u'-' + CE(P_PCTS, 1) + u'-' + CE(P_PCT4, 1) + u'-' + CE(P_PCT2, 1) + u"-L('4')",
    CE(P_MON, 1) + u'-' + CE(P_MDT, 1) + u'-L(\'1\')',
    u'(' + CE(P_MD31, 1) + u'+' + CE(P_MD30, 1) + u'-' + CE(P_MDT, 1) + u')',
    CE(P_PEMPTY, 1) + u'-' + u'B48_BLANKHEAD()' + u'-' + u'B48_ENDBLANK()',
    CF(P_PD, 1) + u'-' + CE(P_PD, 1) + u'-L(\'1\')',
    # 展开/对账/算术
    u'B48_ROWSOK()-' + CE(P_LEAP, 2),
    u'B48_MSHIFT()-B48_ROWSOK()',
    u'B48_DSHIFT()-B48_ROWSOK()',
    u'B48_YSHIFT()-' + CE(P_DEC31, 2),
    u'B48_HEADOK()-B48_BPRINT()',
    u'B48_LINES(2)-B48_BPRINT()-' + CE(P_LEAP, 2) + u'-B48_ENDLINES()',
    u'B48_EPOCH()-(L(\'365\')*(L(\'1970\')-L(\'1900\'))+L(\'17\'))*L(\'86400\')',
    u'L(\'3992312697\')-L(\'1783323897\')-B48_EPOCH()',
    u'L(\'4023129600\')-L(\'1814140800\')-B48_EPOCH()',
    u'(B48_GAP()+B48_SHORT()-L(\'365\')*L(\'86400\'))',
    u'B48_Y10()-L(\'2216\')',
    u'B48_Y53()-L(\'285,428,681\')',
]
put(0, u'+'.join(AB))
NTERMS0 = len(AB)
NPRIM0 = D2[u'0'].count(u'CNT(') + D2[u'0'].count(u'CNTF(')
print(u'DERIV keys=%d / 0 键 %d 项(CNT/CNTF 原语 %d 次)' % (len(D2), NTERMS0, NPRIM0))

EV = {u'CNT': CNT, u'CNTF': CNTF, u'L': lambda x: float(x.replace(u',', u'')),
      u'RCOT': lambda i: RCOT(i), u'round': round,
      u'B48_LINES': lambda i: NLINES[i], u'B48_DROP': lambda i: DROP[i],
      u'B48_TAISPAN': lambda: TAI_SPAN, u'B48_ROWSOK': lambda: ROWS_OK,
      u'B48_MSHIFT': lambda: MSHIFT, u'B48_YSHIFT': lambda: YSHIFT, u'B48_DSHIFT': lambda: DSHIFT,
      u'B48_BPRINT': lambda: BPRINT, u'B48_HEADOK': lambda: HEADOK, u'B48_BLANKHEAD': lambda: BLANKHEAD,
      u'B48_TAILN': lambda: TAILN, u'B48_EPOCH': lambda: EPOCH, u'B48_GAP': lambda: GAP,
      u'B48_ENDBLANK': lambda: ENDBLANK,
      u'B48_SHORT': lambda: SHORT, u'B48_Y10': lambda: cal(10 ** 10)[0], u'B48_Y53': lambda: cal(2 ** 53)[0],
      u'B48_ENDLINES': lambda: ENDLINES, u'B48_BYTES': lambda i: BYTES[i]}
for t in AB:
    v0 = eval(t, {}, EV)
    if abs(v0) > 1e-12:
        print(u'0 键项非零: %-78s -> %s' % (t[:78], v0))
for k, v in D2.items():
    got = eval(v, {}, EV)
    assert abs(got - float(k)) < 1e-9, (k, got, v[:140])
print(u'DERIV 独立回算通过; 键 %s' % u' '.join(sorted(D2, key=lambda x: float(x))))

BLOCK = u" 'B48': {" + NL + NL.join(u"  %r: %r," % (k, v) for k, v in
                                    sorted(D2.items(), key=lambda x: float(x[0]))) + NL + u" }," + NL
SRC48 = u"SRC['B48'] = ['%s', '%s', '%s']" % (RI, RA, RL) + NL
HELPER = u'''# B48: 输入 ⇎ 程序 ⇎ 产物。逐行对账与发射记账在审计器里独立复算(照抄程序自带的日历), 使“减一秒改名”“BEGIN 逐行发射”都是机检项
def _b48_scan():
    def rd(p):
        return open(p, encoding='utf-8', errors='replace').read()
    I, AW, O = rd('corpus/raw/tz/leap-seconds.list'), rd('corpus/raw/tz/leapseconds.awk'), rd('corpus/raw/tz/leapseconds')
    abbr = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')
    mond = [31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31]

    def cal(s):
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
            if day < mond[mo]:
                break
            day -= mond[mo]
            mo += 1
        if mo <= 9:
            mm = mo + 3
        else:
            mm = mo - 9
            yr += 1
        return (1600 + qc * 400 + ce * 100 + qy * 4 + yr, mm, day + 1, (s // 3600) % 24, (s // 60) % 60, s % 60)
    drows = [l.split() for l in I.split('\\n') if l[:1].isdigit()]
    head = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
    reason = '\\n'.join(l for l in O.split('\\n') if not head.match(l.strip()))
    lrows = [l.split('\\t') for l in reason.split('\\n') if l.startswith('Leap')]
    tai = [int(r[1]) for r in drows]
    ok = sh_m = sh_y = sh_d = 0
    for k in range(1, len(drows)):
        c = cal(int(drows[k][0]) - 1)
        out = lrows[k - 1]
        if ('%d' % c[0], abbr[c[1] - 1], '%d' % c[2], '%02d:%02d:%02d' % (c[3], c[4], c[5] + 1)) == tuple(out[1:5]):
            ok += 1
        sh_m += out[2] != drows[k][4]
        sh_y += out[1] != drows[k][5]
        sh_d += out[3] != drows[k][3]
    blk = AW.split('BEGIN {')[1].split('\\n}')[0]
    emit = []
    for l in blk.split('\\n'):
        s = l.strip()
        if s.startswith('print "'):
            lit = s[s.index('"') + 1:s.rindex('"')]
            for a, b in (('\\\\n', '\\n'), ('\\\\t', '\\t'), ('\\\\"', '"'), ('\\\\\\\\', '\\\\')):
                lit = lit.replace(a, b)
            emit.append(lit)
    ol = O.split('\\n')
    headok = len([k for k, e in enumerate(emit) if ol[k] == e])
    blank = len([e for e in emit if e == ''])
    up = int(re.search(r'(?m)^#\\$[ \\t]+(\\d+)', I).group(1))
    ex = int(re.search(r'(?m)^#@[ \\t]+(\\d+)', I).group(1))
    epoch = ((1970 - 1900) * 365 + 17) * 24 * 60 * 60
    tail = len([l for l in ol[-3:] if l and l in I])
    endblank = AW.split('END {')[1].split('\\n}')[0].count('print ""')
    return dict(tai_span=max(tai) - min(tai) + 1, ok=ok, sh_m=sh_m, sh_y=sh_y, sh_d=sh_d,
               bprint=len(emit), headok=headok, blank=blank, tail=tail, endlines=len(ol) - 1 - len(emit) - len(lrows),
               epoch=epoch, gap=ex - up, short=365 * 24 * 60 * 60 - (ex - up),
               endblank=endblank, y10=cal(10 ** 10)[0], y53=cal(2 ** 53)[0])


_B48 = _b48_scan()
B48_TAISPAN = lambda: _B48['tai_span']
B48_ROWSOK = lambda: _B48['ok']
B48_MSHIFT = lambda: _B48['sh_m']
B48_YSHIFT = lambda: _B48['sh_y']
B48_DSHIFT = lambda: _B48['sh_d']
B48_BPRINT = lambda: _B48['bprint']
B48_HEADOK = lambda: _B48['headok']
B48_BLANKHEAD = lambda: _B48['blank']
B48_ENDBLANK = lambda: _B48['endblank']
B48_TAILN = lambda: _B48['tail']
B48_EPOCH = lambda: _B48['epoch']
B48_GAP = lambda: _B48['gap']
B48_SHORT = lambda: _B48['short']
B48_Y10 = lambda: _B48['y10']
B48_Y53 = lambda: _B48['y53']
B48_ENDLINES = lambda: _B48['endlines']
B48_BYTES = lambda i: os.path.getsize(SRC['B48'][i])
B48_LINES = lambda i: len(open(SRC['B48'][i], encoding='utf-8', errors='replace').read().split('\\n')) - 1
B48_DROP = lambda i: len([l for l in open(SRC['B48'][i], encoding='utf-8', errors='replace').read().split('\\n')
                         if re.match(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', l.strip(), re.I)])

'''

AU = u'corpus/audit.py'
s = io.open(AU, encoding='utf-8').read()
if u"SRC['B48']" not in s:
    i0 = s.index(u"SRC['B47']")
    e0 = s.index(NL, i0) + 1
    s = s[:e0] + SRC48 + s[e0:]
if u'def _b48_scan' not in s:
    i1 = s.index(u'DERIV = {')
    s = s[:i1] + HELPER + s[i1:]
if u'CNTF=lambda' not in s:
    T0 = u"CNT=lambda pat, i: len(re.findall(pat, _reason(tag, i), re.I)),"
    assert s.count(T0) == 1, s.count(T0)
    s = s.replace(T0, T0 + NL + u"               CNTF=lambda pat, i: len(re.findall(pat, open(SRC[tag][i], encoding='utf-8', errors='replace').read(), re.I)),", 1)
TAIL = u"B47_SCRIPTS=B47_SCRIPTS)"
if u'B48_ROWSOK=B48_ROWSOK' not in s:
    assert s.count(TAIL) == 1, s.count(TAIL)
    s = s.replace(TAIL, TAIL[:-1] + u", B48_TAISPAN=B48_TAISPAN, B48_ROWSOK=B48_ROWSOK, B48_MSHIFT=B48_MSHIFT,"
                                    u" B48_YSHIFT=B48_YSHIFT, B48_DSHIFT=B48_DSHIFT, B48_BPRINT=B48_BPRINT,"
                                    u" B48_HEADOK=B48_HEADOK, B48_BLANKHEAD=B48_BLANKHEAD, B48_TAILN=B48_TAILN,"
                                    u" B48_ENDBLANK=B48_ENDBLANK,"
                                    u" B48_EPOCH=B48_EPOCH, B48_GAP=B48_GAP, B48_SHORT=B48_SHORT,"
                                    u" B48_Y10=B48_Y10, B48_Y53=B48_Y53, B48_LINES=B48_LINES, B48_DROP=B48_DROP,"
                                    u" B48_ENDLINES=B48_ENDLINES, B48_BYTES=B48_BYTES)", 1)
if u"'B47'}" in s and u"'B48'}" not in s:
    s = s.replace(u"'B47'}", u"'B47', 'B48'}", 1)
s = re.sub(u" 'B48': \\{" + NL + u".*?" + NL + u" \\}," + NL, lambda m: BLOCK, s, count=1, flags=re.S)
if u"'B48': {" not in s:
    k0 = s.index(u'DERIV = {' + NL) + len(u'DERIV = {' + NL)
    s = s[:k0] + BLOCK + s[k0:]
io.open(AU, 'w', encoding='utf-8').write(s)

AC = u'corpus/atomcheck.py'
a = io.open(AC, encoding='utf-8').read()
if u"SRC['B48']" not in a:
    i2 = a.index(u"SRC['B47']")
    a = a[:i2] + SRC48 + a[i2:]
    io.open(AC, 'w', encoding='utf-8').write(a)
io.open(u'corpus/_atoms48.txt', 'w', encoding='utf-8').write(NL.join(sorted(set(AN.values()))) + NL)
ST = [(u'anchors', ANCH), (u'uniq_anchor', UANCH), (u'anchor_i', NI_AN), (u'anchor_a', NA_AN), (u'anchor_l', NL_AN),
      (u'deriv_keys', len(D2)), (u'n_term0', NTERMS0), (u'n_prim0', NPRIM0), (u'gloss_lines', GLOS),
      (u'body_chars', len(BODY)), (u'lines', u' '.join(str(x) for x in NLINES)),
      (u'dropped', u' '.join(str(x) for x in DROP)), (u'rcot', u' '.join(str(RCOT(i)) for i in range(3))),
      (u'full', u' '.join(str(len(TXT[i])) for i in range(3))), (u'bytes', u' '.join(str(x) for x in BYTES)),
      (u'data_rows', N_DATA), (u'leap_rows', N_LEAP), (u'jun30', N_JUN), (u'dec31', N_DEC),
      (u'tai_min', TAI_MIN), (u'tai_max', TAI_MAX), (u'tai_span', TAI_SPAN),
      (u'rows_ok', ROWS_OK), (u'mshift', MSHIFT), (u'yshift', YSHIFT), (u'dshift', DSHIFT),
      (u'bprint', BPRINT), (u'headok', HEADOK), (u'blankhead', BLANKHEAD), (u'endlines', ENDLINES),
      (u'tailn', TAILN), (u'epoch', EPOCH), (u'gap', GAP), (u'short', SHORT), (u'gap_days', u'%.2f' % (GAP / 86400.0)),
      (u'y10', cal(10 ** 10)[0]), (u'y53', cal(2 ** 53)[0]), (u'cal_updated', u'%s' % (cal(int(UP)),)),
      (u'cal_expires', u'%s' % (cal(int(EX)),)),
      (u'print_stmts', N_PRINT), (u'printf_stmts', N_PRINTF), (u'pempty', N_PEMPTY), (u'endblank', ENDBLANK), (u'sign', N_SIGN),
      (u'dead', N_DEAD), (u'expires_line', N_EL), (u'last_lines', N_LL), (u'monthabbr', N_MON),
      (u'mon_days', N_MDT), (u'md31', N_MD31), (u'md30', N_MD30), (u'md28', N_MD28),
      (u'pct', N_PCT), (u'pctd', N_PCTD), (u'pcts', N_PCTS), (u'pct4', N_PCT4), (u'pct2', N_PCT2),
      (u'esc_t', N_ESCT), (u'esc_q', N_ESCQ), (u'esc_n', N_ESCN), (u'cont', N_CONT),
      (u'tab_i0', N_TAB_I0), (u'tab_a', N_TAB_A), (u'tab_l', N_TAB_L), (u'tab_if', N_TAB_IF),
      (u'june_i_full', N_JUNE_F[0]), (u'qjan_l', N_QJAN[2]), (u'59_l_full', N_59_LF), (u'60_l_full', N_60_LF),
      (u'y1980_i', N_1980_I), (u'y2017_i', N_2017_I), (u'n37_i', N_37_I), (u'up_i_full', N_UPDT_F[0]),
      (u'sha_i', SHA[0]), (u'sha_a', SHA[1]), (u'sha_l', SHA[2])]
io.open(u'corpus/_f48stats.txt', 'w', encoding='utf-8').write(NL.join(u'%s\t%s' % (k, v) for k, v in ST) + NL)
print(u'wired B48: audit SRC/CNTF/HELPER/DERIV(%d keys) + atomcheck SRC + _atoms48.txt(%d uniq)' % (len(D2), UANCH))
