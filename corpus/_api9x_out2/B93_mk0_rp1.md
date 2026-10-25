```python
# 替换 corpus/_mkB93.py 整文件(新增到 corpus/_pick93.py 之后; 与 _pick93.py 同目录同键集)
# -*- coding: utf-8 -*-
# ============================================================================
# B93 建条目侧(第二套实现, A 侧): 多文本对读 · 截止后专业信息
#   源 = 五份一手文书各答一遍“IPv6 DAD 试几次、隔多久”:
#        RFC 4862(无状态地址自动配置) ⇎ RFC 4861(邻居发现: 唯一把常量印成数的)
#        ⇎ RFC 4429(Optimistic DAD) ⇎ ip-sysctl.txt(Linux 内核文档)
#        ⇎ systemd_network5(发行版组件文档, 另有同名 .html 作原文/剥壳对账)
#   本文件只做两件事: ①SCAN 段把全部判词读数重算一遍(第二套机制见下);
#     ②按 B87/B88 版式发射条目(编码区数字全部由 V() 从对账件插值, 零手填)。
# 机制档位(A 侧, 与 corpus/_pick93.py 逐条不同路):
#   切行 = splitlines() 后回剥 \r ⇎ 折平 = re.sub(\s+) ⇎ 找针 = re.finditer 非重叠
#   ⇎ 整词尺 = 两枚 lookaround ⇎ 页壳 = 单行整匹配正则 ⇎ 切句 = 状态机扫描(?<=[.!?]) 等价
#   ⇎ 默认值 = 一位一判的位形态分类器 ⇎ 行号 = 折平面偏移 → bisect 区间表
#   ⇎ 去连字 = 双字符前瞻扫描 ⇎ 单位换算 = 分数(Fraction)求商。
# 运行次序: python -X utf8 corpus/_mkB93.py  ⇎ python -X utf8 corpus/_pick93.py
#           ⇎ 再跑一遍 _mkB93.py(读对账件发射) ⇎ _mk93emit.py ⇎ _wire93.py ⇎ _fill93.py
# ============================================================================
import io, json, os, re, sys
from bisect import bisect_right
from fractions import Fraction

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LBL = [u'4862', u'4861', u'4429', u'sysctl', u'sysd']
SRC = [u'corpus/raw/dad6/rfc4862.txt', u'corpus/raw/dad6/rfc4861.txt', u'corpus/raw/dad6/rfc4429.txt',
       u'corpus/raw/dad6/ip-sysctl.txt', u'corpus/raw/dad6/systemd_network5.txt']
HTML = u'corpus/raw/dad6/systemd_network5.html'
NSRC = 5
MEASA = u'corpus/_tmp93_measA.json'
MEAS = u'corpus/_b93meas.json'
ENTRY = u'corpus/babeltele/B93_ipv6_dad_retrans_compression.md'
ATOMFILE = u'corpus/_atoms93.txt'
NL = chr(10)

# --- SCAN BEGIN ---
# —— READ 档: 二进制读 → 严格 UTF-8(错即 raise) → splitlines 后回剥 \r ——
BB = [io.open(p, 'rb').read() for p in SRC]
TT = [b.decode('utf-8') for b in BB]          # 严格解码: 若非 UTF-8 直接崩, 不静默替换
LL = [t.splitlines() for t in TT]             # splitlines 已吃掉 \r\n / \x0c 等行界
HB = io.open(HTML, 'rb').read()
HT = HB.decode('utf-8')


def pnorm(s):
    """最宽档: 小写 + 空白折一 + 去首尾。"""
    return re.sub(u'\\s+', u' ', s.lower()).strip()


def cnt(hay, nd):
    """lookahead 非重叠计数: 用 finditer 的零宽前瞻逐位推进, 与游标 find 环同口径。"""
    return len(list(re.finditer(u'(?=' + re.escape(nd) + u')', hay)))


def ub(s, w, kind=u'alpha'):
    """整词尺(两枚 lookaround): alpha ⇎ digit ⇎ alnum 三种边界。"""
    if kind == u'alpha':
        rx = u'(?<![A-Za-z])' + re.escape(w) + u'(?![A-Za-z])'
    elif kind == u'digit':
        rx = u'(?<![0-9])' + re.escape(w) + u'(?![0-9])'
    else:
        rx = u'(?<![0-9A-Za-z])' + re.escape(w) + u'(?![0-9A-Za-z])'
    return len(re.findall(rx, s))


def digit_runs(x):
    n, prev = 0, False
    for c in x:
        cur = c.isdigit()
        if cur and not prev:
            n += 1
        prev = cur
    return n


def foldmap(txt):
    """折平面 + (面区间 → 原行号) 表, 供 bisect 反查行。"""
    lines = txt.splitlines()
    offs, pos, seg = [], 0, []
    for i, l in enumerate(lines):
        c = pnorm(l)
        if not c:
            continue
        offs.append((pos, pos + len(c), i))
        seg.append(c)
        pos += len(c) + 1
    face = u' '.join(seg)
    assert len(face) == (pos - 1 if pos else 0), (len(face), pos)
    return face, offs


def line_at(offs, s0):
    """bisect_right 落在面偏移后的最后一枚区间 → 原行号。"""
    if not offs:
        return None
    lo = [o[0] for o in offs]
    k = bisect_right(lo, s0) - 1
    return offs[k][2] if k >= 0 else None


def find_line(i, nd, dehy=False):
    """折平 needle → 首字符所在原行(0-based): 4 行滑窗 + bisect 区间表。"""
    q = pnorm(nd)
    head = q[:min(16, len(q))]
    for a in range(len(LL[i])):
        win = NL.join(LL[i][a:a + 4])
        if head not in pnorm(win):
            continue
        face, offs = foldmap(win)
        if dehy:
            face = dehy2(face)
        s0 = face.find(q)
        if s0 >= 0:
            return a + line_at(offs, s0)
    return -1


def dehy2(face):
    """双字符前瞻扫描去连字: 只在 'w- 空格 w' 处抹掉 '空格', 一个函数不靠 re。"""
    out, k, n = [], 0, len(face)
    while k < n:
        if (k + 3 < n and face[k].isalnum() and face[k + 1] == u'-' and face[k + 2] == u' '
                and face[k + 3].isalnum()):
            out.append(face[k]); out.append(face[k + 1]); k += 3
            continue
        out.append(face[k]); k += 1
    return u''.join(out)


# ---------- 0. 面量 ⇎ 行式 ⇎ 换页账 ——
M = {}
M['bytes'] = [len(BB[i]) for i in range(NSRC)]
M['cp'] = [len(TT[i]) for i in range(NSRC)]
M['n_lf'] = [cnt(TT[i], NL) for i in range(NSRC)]
M['n_cr'] = [cnt(TT[i], u'\r') for i in range(NSRC)]
M['splitlines'] = [len(TT[i].splitlines()) for i in range(NSRC)]
RL = [t.split(NL) for t in TT]
M['splitnl'] = [len(RL[i]) for i in range(NSRC)]
M['readlines'] = [len(list(io.StringIO(TT[i], newline=NL))) for i in range(NSRC)]
M['ff'] = [cnt(TT[i], u'\x0c') for i in range(NSRC)]
M['ff_led'] = [len([x for x in LL[i] if x[:1] == u'\x0c']) for i in range(NSRC)]
M['blank'] = [len([x for x in LL[i] if x.strip() == u'']) for i in range(NSRC)]
M['nonblank'] = [len([x for x in LL[i] if x.strip() != u'']) for i in range(NSRC)]
M['maxlen'] = [max([len(x) for x in LL[i]]) for i in range(NSRC)]
M['tab'] = [cnt(TT[i], u'\t') for i in range(NSRC)]
M['nonascii'] = [sorted(set([ord(c) for c in TT[i] if ord(c) > 127])) for i in range(NSRC)]
M['na_total'] = [len([c for c in TT[i] if ord(c) > 127]) for i in range(NSRC)]
M['bom'] = [1 if TT[i][:1] and ord(TT[i][0]) == 65279 else 0 for i in range(NSRC)]
M['utf8_extra'] = [M['bytes'][i] - M['cp'][i] for i in range(NSRC)]
FFNL = [len(re.findall(u'(?=\x0c' + NL + u')', TT[i])) for i in range(NSRC)]
FFEOF = [1 if TT[i][-1:] == u'\x0c' else 0 for i in range(NSRC)]
TRAILNL = [1 if TT[i][-1:] == NL else 0 for i in range(NSRC)]
M['ff_before_nl'], M['ff_at_eof'], M['trailing_nl'] = FFNL, FFEOF, TRAILNL
OBS = [M['splitlines'][i] - M['splitnl'][i] for i in range(NSRC)]
PRE = [FFNL[i] - TRAILNL[i] for i in range(NSRC)]
M['row_ledger'] = [M['blank'][i] + M['nonblank'][i] - M['splitnl'][i] for i in range(NSRC)]
M['read_vs_split'] = [M['readlines'][i] + M['trailing_nl'][i] - M['splitnl'][i] for i in range(NSRC)]

# ---------- 0b. HTML 档: 原文 ⇎ 剥壳正文 ——
M['html_bytes'] = len(HB)
M['html_cp'] = len(HT)
M['html_lines'] = len(HT.splitlines())
M['html_lf'] = cnt(HT, NL)
M['tag_n'] = len(re.findall(u'<[^>]+>', HT))
M['tag_chars'] = sum(len(z) for z in re.findall(u'<[^>]+>', HT))
M['ent_n'] = len(re.findall(u'&[A-Za-z#0-9]+;', HT))
M['stripped_cp'] = M['cp'][4]
M['html_minus_stripped'] = M['html_cp'] - M['stripped_cp']

# ---------- 1. 壳形: 三个序列化家族 ——
def foot(x):
    return re.fullmatch(u'.*\\[Page \\d+\\]', x) is not None


def hdr_old(x):
    return (re.fullmatch(u'\\s*(?:[A-Z][a-z\u2019-]+, et al\\.|[A-Z][a-zA-Z]+ +[A-Za-z ]*?(?:19|20)\\d\\d) +'
                         u'(?:Standards Track|Informational|Experimental|[A-Z][a-z]+ \\d+)?.*\\[Page \\d+\\]', x)
            is not None)


def hdr_title(x):
    return re.fullmatch(u'RFC\\d+ +\\S.*(?:(?:19|20)\\d\\d)\\s*', x) is not None


def ietf_line(x):
    return re.fullmatch(u'\\s*(?:Internet Engineering Task Force|Network Working Group)\\s*', x) is not None


def keylin(x):
    return re.fullmatch(u'[a-z][a-z_0-9]* - (?:INTEGER|BOOLEAN|STRING|DWORD)\\s*', x) is not None


def optlin(x):
    return re.fullmatch(u'\\s{4,}[A-Za-z][A-Za-z0-9]*= *', x) is not None


def addedlin(x):
    return re.fullmatch(u'\\s*Added in version \\d+\\.\\s*', x) is not None


def ffline(x):
    return x == u'\x0c'


M['foot_page'] = [len([x for x in LL[i] if foot(x)]) for i in range(NSRC)]
M['hdr_old'] = [len([x for x in LL[i] if hdr_old(x)]) for i in range(NSRC)]
M['hdr_title'] = [len([x for x in LL[i] if hdr_title(x)]) for i in range(NSRC)]
M['ietf_alone'] = [len([x for x in LL[i] if ietf_line(x)]) for i in range(NSRC)]
M['key_lines'] = [len([x for x in LL[i] if keylin(x)]) for i in range(NSRC)]
M['opt_lines'] = [len([x for x in LL[i] if optlin(x)]) for i in range(NSRC)]
M['added_lines'] = [len([x for x in LL[i] if addedlin(x)]) for i in range(NSRC)]
M['pgnum'] = [len([x for x in LL[i] if x.strip() != u''
                  and not [c for c in x if not (c.isdigit() or c.isspace())] and digit_runs(x) == 1])
              for i in range(NSRC)]
M['tab_led'] = [len([x for x in LL[i] if x[:1] == u'\t']) for i in range(NSRC)]


def is_shell(x, i):
    return (foot(x) or hdr_old(x) or hdr_title(x) or ietf_line(x) or ffline(x) or x.strip() == u''
            or (i == 4 and addedlin(x)))


M['shell_lines'] = [len([1 for x in LL[i] if is_shell(x, i)]) for i in range(NSRC)]
M['body_lines'] = [M['splitnl'][i] - M['shell_lines'][i] for i in range(NSRC)]

# ---------- 2. 义务词 ⇎ 大小写两代 ——
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY', u'MUST NOT be', u'NOT RECOMMENDED']
FOC = [u' '.join(TT[i].split()) for i in range(NSRC)]
M['ob_line'] = [[sum([ub(x, w) for x in LL[i]]) for w in OB] for i in range(NSRC)]
M['ob_fold'] = [[ub(FOC[i], w) for w in OB] for i in range(NSRC)]
M['ob_wrap'] = [M['ob_fold'][i][k] - M['ob_line'][i][k] for i in range(NSRC) for k in range(len(OB))]
LOW = [len(re.findall(u'(?i)\\b(?:must|should|may)\\b', TT[i])) for i in range(NSRC)]
CAP = [len(re.findall(u'\\b(?:MUST NOT|MUST|SHOULD NOT|SHOULD|MAY)\\b', TT[i])) for i in range(NSRC)]
M['kw_all'], M['kw_caps'], M['kw_low_only'] = LOW, CAP, [LOW[i] - CAP[i] for i in range(NSRC)]
M['dbl_space'] = [len(re.findall(u'(?<=\\S)  +(?=\\S)', TT[i])) for i in range(NSRC)]
M['dbl_space_eaten'] = [M['dbl_space'][i] - len(re.findall(u'(?<=\\S)  +(?=\\S)', FOC[i]))
                        for i in range(NSRC)]

# ---------- 3. 判词针四档(逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳去连字折平) ——
SHP = [pnorm(NL.join([x for x in LL[i] if not is_shell(x, i)])) for i in range(NSRC)]
SHT = [dehy2(SHP[i]) for i in range(NSRC)]
FOL = [pnorm(TT[i]) for i in range(NSRC)]
M['dehyphen_chars'] = [len(SHP[i]) - len(SHT[i]) for i in range(NSRC)]
M['dehyphen_edits'] = [len(re.findall(u'(?=\\w- \\w)', SHP[i])) for i in range(NSRC)]
NEEDLES = [
    u"The number of consecutive Neighbor Solicitation messages sent while performing Duplicate Address",
    u"A value of one indicates a single transmission with no follow-up retransmissions",
    u"Default: 1, but may be overridden by a link-type specific value",
    u"An interface whose DupAddrDetectTransmits variable is set to zero",
    u"each separated by RetransTimer milliseconds",
    u"within RetransTimer milliseconds after having sent DupAddrDetectTransmits",
    u"a random delay between 0 and MAX_RTR_SOLICITATION_DELAY as specified in",
    u"the time a node waits after sending the last Neighbor",
    u"Duplicate Address Detection MUST be performed on all unicast",
    u"the number expected based on the loopback semantics",
    u"MAX_MULTICAST_SOLICIT 3 transmissions",
    u"RETRANS_TIMER 1,000 milliseconds",
    u"REACHABLE_TIME 30,000 milliseconds",
    u"DELAY_FIRST_PROBE_TIME 5 seconds",
    u"MAX_RTR_SOLICITATION_DELAY 1 second",
    u"RTR_SOLICITATION_INTERVAL 4 seconds",
    u"MAX_INITIAL_RTR_ADVERT_INTERVAL 16 seconds",
    u"MAX_RA_DELAY_TIME .5 seconds",
    u"MIN_RANDOM_FACTOR .5",
    u"after waiting RetransTimer milliseconds after sending the",
    u"solicitations, retransmissions cease and the",
    u"the sender changes the state to DELAY and sets a timer to",
    u"a node retransmits Neighbor Solicitation messages every RetransTimer milliseconds",
    u"remove the RetransTimer delay during address configuration",
    u"It is not sufficient to merely reduce RetransTimer in order to reduce",
    u"reduced by increasing the RFC 2462 DupAddrDetectTransmits variable to",
    u"Optimistic DAD suffers from similar problems to Standard DAD",
    u"dad_transmits - INTEGER",
    u"The amount of Duplicate Address Detection probes to send",
    u"Whether to accept DAD (Duplicate Address Detection)",
    u"1: Enable DAD (default)",
    u"Whether to perform Optimistic Duplicate Address Detection (RFC 4429)",
    u"Include a nonce option in the IPv6 neighbor solicitation messages used for",
    u"The maximum number of multicast probes in INCOMPLETE state",
    u"The maximum number of unicast probes in PROBE state",
    u"Number of seconds to wait between Router Solicitations",
    u"Quoting from RFC 2461, section 4.4",
    u"Configures the amount of IPv6 Duplicate Address Detection",
    u"probes to send. When unset, the kernel's default will be",
    u"Configures the maximum timeout for IPv4 Duplicate Address",
    u"Must be a value between 1 millisecond and 60 seconds",
    u"randomized time between 57% (4/7) and 100% of the given value",
    u"If unset, defaults to 200 milliseconds",
    u"A value of zero is ignored and the kernel's current",
    u'When "ipv6", performs IPv6 Duplicate Address Detection',
    u'The time between retransmitted Neighbor Solicitation messages',
    u"A host forms a link-local address by appending an interface identifier",
    u"per-interface basis on multicast-capable interfaces",
    u"Discard Duplicate Address Detection-related Neighbor Solicitation",
    u"defined in a separate link-type-specific document",
    u"has the correct link-layer address; otherwise",
    u"until the ON has a non-Optimistic address",
]
rows = []
for nd in NEEDLES:
    q = pnorm(nd)
    r = []
    for i in range(NSRC):
        cl = len([x for x in LL[i] if q in pnorm(x)])
        cf = cnt(FOL[i], q)
        cs = cnt(SHP[i], q)
        ct = cnt(SHT[i], q)
        r.append((cl, cf, cs, ct))
    rows.append((nd, r))
M['needles4'] = [[list(z) for z in [r[i] for i in range(NSRC)]] for nd, r in rows]
M['needle_src'] = [[LBL[i] for i in range(NSRC) if r[i][2] > 0] for nd, r in rows]
M['needle_src_dehy'] = [[LBL[i] for i in range(NSRC) if r[i][3] > 0] for nd, r in rows]
M['needle_wrap_kinds'] = len([1 for nd, r in rows if any(r[i][1] > 0 and r[i][0] == 0 for i in range(NSRC))])
M['needle_dehy_kinds'] = len([1 for nd, r in rows
                              if any(r[i][3] > 0 and r[i][2] == 0 for i in range(NSRC))])

# ---------- 4. 关键句行号定位(供锚) ——
PINL = []
for nd, r in rows:
    shy = any(r[i][2] > 0 for i in range(NSRC))
    dhy = any(r[i][3] > 0 and r[i][2] == 0 for i in range(NSRC))
    if not (shy or dhy):
        continue
    for i in range(NSRC):
        a = find_line(i, nd)
        dh = 1
        if a < 0:
            a = find_line(i, nd, dehy=True)
            dh = 2
        if a >= 0:
            PINL.append([LBL[i], nd, a + 1, dh])
M['pin_lines'] = PINL

# ---------- 5. 数值×单位: 严 ⇎ 宽两轨 ⇎ 千分位 ⇎ 前导点 ⇎ 粘连 ——
RX_STRICT = re.compile(u'(?<![A-Za-z0-9])(\\d[\\d,]*(?:\\.\\d+)?)[ ]?'
                       u'(milliseconds|millisecond|seconds|second|transmissions|probes|messages)(?![A-Za-z])')
RX_LOOSE = re.compile(u'(\\d[\\d,]*(?:\\.\\d+)?)\\.? ?'
                      u'(milliseconds|millisecond|seconds|second|transmissions|probes|messages|ms|sec|s)')
M['numunit_strict'] = [[list(z) for z in sorted(set(RX_STRICT.findall(TT[i])))] for i in range(NSRC)]
M['numunit_loose'] = [[list(z) for z in sorted(set(RX_LOOSE.findall(FOL[i])))] for i in range(NSRC)]
M['loose_n'] = [len(RX_LOOSE.findall(FOL[i])) for i in range(NSRC)]
M['strict_n'] = [len(RX_STRICT.findall(TT[i])) for i in range(NSRC)]
M['loose_short_n'] = [len([z for z in RX_LOOSE.findall(FOL[i])
                           if z[1] in (u'ms', u'sec', u's')]) for i in range(NSRC)]
M['loose_all_short'] = [M['loose_short_n'][i] == M['loose_n'][i] for i in range(NSRC)]
M['comma_nums'] = [sorted(set(re.findall(u'(?<![\\d.])(\\d{1,3},\\d{3}(?:,\\d{3})?)', TT[i])))
                   for i in range(NSRC)]
M['dotfrac_nums'] = [sorted(set(re.findall(u'(?<![\\d.)])\\.(\\d+)', TT[i]))) for i in range(NSRC)]
M['dotlead_unit'] = [[list(z) for z in sorted(set(re.findall(
    u'(?<![\\d])\\.(\\d+)(?: )?(milliseconds|millisecond|seconds|second)(?![A-Za-z])', TT[i])))]
    for i in range(NSRC)]
M['range_nums'] = [sorted(set(re.findall(u'(\\d+\\.\\.\\d+|1\\.\\.\\.\\d+)', TT[i]))) for i in range(NSRC)]
M['percent'] = [sorted(set(re.findall(u'(\\d+%)', TT[i]))) for i in range(NSRC)]
M['fraction'] = [sorted(set(re.findall(u'\\((\\d/\\d)\\)', TT[i]))) for i in range(NSRC)]
UNITS = u'(milliseconds|millisecond|seconds|second|transmissions|probes|messages|hours|hour|minutes|minute|days|day)'
M['glued_unit'] = [[list(z) for z in sorted(set(re.findall(u'(?<![A-Za-z0-9])(\\d+)(' + UNITS + u')(?![A-Za-z])', TT[i])))]
                   for i in range(NSRC)]
M['spaced_unit'] = [[list(z) for z in sorted(set(re.findall(u'(?<![A-Za-z0-9])(\\d+) (' + UNITS + u')(?![A-Za-z])', TT[i])))]
                    for i in range(NSRC)]
M['hex_default'] = [sorted(set(re.findall(u'(?m)^[ \\t]*Default[^\\n]*?(0x[0-9A-Fa-f]+|INT_MAX|UINT_MAX)', TT[i])))
                    for i in range(NSRC)]
M['dig_ipv_noise'] = [len(re.findall(u'(?i)(?:ipv|ip)(\\d)', TT[i])) for i in range(NSRC)]
M['dig_all'] = [[len(re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', TT[i])), M['dig_ipv_noise'][i]] for i in range(NSRC)]
M['unit_in_keyname'] = [sorted(set(re.findall(u'([A-Za-z0-9]*(?:Sec|Millis|Usec|Ms))[ =]', TT[i]))) for i in range(NSRC)]

# ---------- 6. 单位换算: Fraction 求商, 面内自证的双单位行 ⇎ 跨份等值对 ——
UF = {u'ns': Fraction(1, 1000000), u'nanoseconds': Fraction(1, 1000000),
      u'millisecond': Fraction(1), u'milliseconds': Fraction(1), u'ms': Fraction(1),
      u'second': Fraction(1000), u'seconds': Fraction(1000), u'minute': Fraction(60000),
      u'minutes': Fraction(60000), u'hour': Fraction(3600000), u'hours': Fraction(3600000),
      u'day': Fraction(86400000), u'days': Fraction(86400000)}
TU = u'(ns|nanoseconds|ms|milliseconds|millisecond|seconds|second|minutes|minute|hours|hour|days|day)'
DUALRE = re.compile(u'(\\d[\\d,]*) ' + TU + u' ?\\((\\d[\\d,]*) ' + TU + u'\\)')
DUALIM = re.compile(u'(\\d[\\d,]*) ?\\((\\d[\\d,]*) ' + TU + u'\\)')


def numv(s):
    return Fraction(int(s.replace(u',', u'')))


DUAL = []
for i in range(NSRC):
    for x in LL[i]:
        m = DUALRE.search(x)
        if m:
            DUAL.append([LBL[i], m.group(0).strip(), int(m.group(1).replace(u',', u'')), m.group(2),
                         int(m.group(3).replace(u',', u'')), m.group(4),
                         UF[m.group(2)] * numv(m.group(1)) == UF[m.group(4)] * numv(m.group(3))])
M['dual_unit_lines'] = DUAL
M['dual_prove'] = [z[6] for z in DUAL]
M['dual_gloss_forms'] = sorted(set(u'%d %s' % (z[4], z[5]) for z in DUAL))
M['dual_plural_at_one'] = len([z for z in DUAL if z[4] == 1 and z[5].endswith(u's')])
DUAL2 = []
blocks, cur = [], None
for x in LL[3]:
    if keylin(x):
        cur = [x.split(u' - ')[0], []]
        blocks.append(cur)
    elif cur is not None:
        cur[1].append(x)
for k, body in blocks:
    m = re.search(u'\\((in )(milliseconds|seconds)\\)', u' '.join(body))
    d = [z for z in body if re.search(DUALIM, z)]
    if m and d:
        mm = DUALIM.search(d[0])
        DUAL2.append([k, mm.group(0).strip(), m.group(2), int(mm.group(1).replace(u',', u'')),
                      int(mm.group(2).replace(u',', u'')), mm.group(3),
                      UF[m.group(2)] * numv(mm.group(1)) == UF[mm.group(3)] * numv(mm.group(2))])
M['dual_implicit_lines'] = DUAL2
CONV = []
for i in range(NSRC):
    for m in re.finditer(u'(?<![A-Za-z0-9])(\\d[\\d,]*(?:\\.\\d+)?)([ ]?)(nanoseconds|milliseconds|millisecond'
                         u'|seconds|second|minutes|minute)(?![A-Za-z])', TT[i]):
        CONV.append([LBL[i], m.group(1), m.group(3), numv(m.group(1)) * UF[m.group(3)] / 1000,
                     m.group(2) == u''])
M['unit_conv'] = [[z[0], z[1], z[2], float(z[3]), z[4]] for z in CONV]
M['conv_glued_n'] = len([z for z in CONV if z[4]])
M['conv_spaced_n'] = len([z for z in CONV if not z[4]])
SAME = {}
seen = set()
for a in range(len(CONV)):
    for b in range(a + 1, len(CONV)):
        if CONV[a][0] != CONV[b][0] and CONV[a][1] != CONV[b][1] and CONV[a][3] == CONV[b][3]:
            pair = (u'%s:%s %s' % (CONV[a][0], CONV[a][1], CONV[a][2]),
                    u'%s:%s %s' % (CONV[b][0], CONV[b][1], CONV[b][2]))
            if pair in seen:
                continue
            seen.add(pair)
            SAME.setdefault(CONV[a][3], []).append(pair)
M['conv_same'] = dict((str(float(k)), v) for k, v in sorted(SAME.items(), key=lambda kv: float(kv[0])))

# ---------- 7. 参数名拼写族: 三把名尺 ——
NAMES = [u'DupAddrDetectTransmits', u'dad_transmits', u'use_dad', u'accept_dad', u'optimistic_dad',
         u'enhanced_dad', u'IPv6DuplicateAddressDetection', u'DuplicateAddressDetection',
         u'IPv4DuplicateAddressDetectionTimeoutSec', u'IPv6RetransmissionTimeSec',
         u'RetransTimer', u'RETRANS_TIMER', u'MAX_RTR_SOLICITATION_DELAY', u'DELAY_FIRST_PROBE_TIME',
         u'MAX_MULTICAST_SOLICIT', u'MAX_UNICAST_SOLICIT', u'mcast_solicit', u'ucast_solicit',
         u'app_solicit', u'router_solicitations', u'router_solicitation_interval',
         u'retrans_time', u'RetryCount', u'MAX_RTR_SOLICITATIONS']
NRM = [pnorm(x.replace(u'_', u' ')) for x in NAMES]
M['name_raw'] = [[cnt(TT[i], x) for x in NAMES] for i in range(NSRC)]
M['name_ci'] = [[cnt(FOL[i], pnorm(x)) for x in NAMES] for i in range(NSRC)]
M['name_norm'] = [[ub(FOL[i], nrm, u'alnum') for nrm in NRM] for i in range(NSRC)]
M['name_absent'] = [x for k, x in enumerate(NAMES) if sum(M['name_raw'][i][k] for i in range(NSRC)) == 0]

# ---------- 8. 默认值句式: 各一条正则, 句式互不重叠 ——
SHAPES = [
    (u'Default:', re.compile(u'(?m)^[ \\t]*Default:[ \\t]*([^ \\t\\n]+)')),
    (u'Default :', re.compile(u'(?m)^[ \\t]*Default[ ]+:[ \\t]*([^ \\t\\n]+)')),
    (u'Default value', re.compile(u'(?i)Default value[ \\t]+is[ \\t]+([^ .;,\\n]+)')),
    (u'Functional default:', re.compile(u'(?m)^[ \\t]*Functional default:[ \\t]*([^ \\t\\n]+)')),
    (u'(default)', re.compile(u'\\((default)\\)')),
    (u'Defaults to', re.compile(u'Defaults to +([^ .;,\\n)]+)')),
    (u'defaults to', re.compile(u'defaults to +([^ .;,\\n)]+)')),
    (u'By default', re.compile(u'^[ \\t]*(By default)', re.M)),
    (u'by default', re.compile(u'[ \\t](by default)[,.]', re.I)),
    (u'is the default', re.compile(u'(?i)(is the default)')),
]
M['shape_n'] = [[len(SHAPES[j][1].findall(TT[i])) for j in range(len(SHAPES))] for i in range(NSRC)]
M['shape_lbls'] = [s[0] for s in SHAPES]
M['default_val_is_num'] = [[len([z for z in SHAPES[j][1].findall(TT[i])
                                 if re.match(u'^[-.\\d]', u'%s' % (z,))])
                            for j in range(len(SHAPES))] for i in range(NSRC)]
M['default_gloss'] = [len(re.findall(u'(?m)^[ \\t]*Default: +\\d \\(', TT[i])) for i in range(NSRC)]
DK = {}
for i in [3]:
    cur = None
    for x in LL[i]:
        if keylin(x):
            cur = x.split(u' - ')[0]
            DK[cur] = []
        elif cur is not None:
            DK[cur].append(x)
M['sysctl_keys'] = len(DK)
M['sysctl_key_types'] = dict((x.split(u' - ')[0], x.split(u' - ')[1].strip())
                             for x in LL[3] if keylin(x))
REL = [k for k in DK if u'dad' in k or u'_solicit' in k or k.startswith(u'router_solicitation')
       or k == u'retrans_time']
M['sysctl_rel_keys'] = sorted(REL)
M['sysctl_rel_body'] = dict((k, re.sub(u'\\s+', u' ', u' '.join(DK[k])).strip()) for k in sorted(REL))
M['sysctl_rel_nlines'] = dict((k, len(DK[k])) for k in sorted(REL))


def tok(s):
    m = re.match(u'([^ .;,)]+)', s)
    return m.group(1) if m else s


DEF = {}
for k in sorted(REL):
    hit = None
    for x in DK[k]:
        s = x.strip()
        m = re.match(u'Default:[ \t]+(\\S[^\\n]*)', s)
        if m:
            hit = [tok(m.group(1)), u'Default:']
            break
        m = re.match(u'Default[ \t]+:[ \t]+(\\S[^\\n]*)', s)
        if m:
            hit = [tok(m.group(1)), u'Default :']
            break
        m = re.search(u'(?i)Defaults\\s+to +(\\S+)', s)
        if m:
            hit = [tok(m.group(1)), u'Defaults to']
            break
        m = re.match(u'([0-9A-Za-z]+)[: ][^\\n]*\\(default\\)', s)
        if m:
            hit = [m.group(1), u'(default)']
            break
        m = re.match(u'(?i)default value[ \t]+is[ \t]+(\\S+)', s)
        if m:
            hit = [tok(m.group(1)), u'Default value is']
            break
    DEF[k] = hit if hit else [None, u'无']
DEF = dict((k, [re.sub(u'[.,;]$', u'', v[0]) if v[0] else None, v[1]]) for k, v in DEF.items())
M['sysctl_defaults'] = DEF

# ---------- 9. 引用边: 带空格 ⇎ 不带空格两把尺 ——
RXN_SP = re.compile(u'RFC (\\d{4})')
RXN_NS = re.compile(u'RFC(\\d{4})')
M['ref_spaced'] = [sorted(set(RXN_SP.findall(TT[i]))) for i in range(NSRC)]
M['ref_glued'] = [sorted(set(RXN_NS.findall(TT[i]))) for i in range(NSRC)]
M['ref_n'] = [[len(RXN_SP.findall(TT[i])), len(RXN_NS.findall(TT[i]))] for i in range(NSRC)]

# ---------- 10. 段窗定界(节级): 标题现读 ——
W = {}
for tag, li, nd in [(u'4862', 0, u"DupAddrDetectTransmits  The number of consecutive Neighbor"),
                    (u'4862', 0, u"5.4.  Duplicate Address Detection"),
                    (u'4861', 1, u"10.  Protocol Constants"),
                    (u'4861', 1, u"Node constants:"),
                    (u'4429', 2, u"4.4.  Pathological Cases"),
                    (u'sysctl', 3, u"dad_transmits - INTEGER"),
                    (u'sysctl', 3, u"accept_dad - INTEGER"),
                    (u'sysd', 4, u"IPv6DuplicateAddressDetection="),
                    (u'sysd', 4, u"IPv4DuplicateAddressDetectionTimeoutSec=")]:
    a = find_line(li, nd)
    assert a >= 0, (tag, nd)
    W[tag + u'|' + nd] = a + 1
M['win_heads'] = W

# ---------- 11. 段窗数字普查: 五把定界谓词(节/段/标签/键/选项) ——
IDX = dict((LBL[i], i) for i in range(NSRC))
VARRE = re.compile(u'\\b(?:MAX_[A-Z_]+|MIN_[A-Z_]+|RETRANS_TIMER|REACHABLE_TIME|RTR_[A-Z_0-9]+'
                   u'|DELAY_FIRST_PROBE_TIME|DupAddrDetectTransmits|RetransTimer)\\b')


def secnum(x):
    m = re.match(u'^(\\d+(?:\\.\\d+)*\\.?)\\s\\s+(?=[A-Z])', x.lstrip())
    return m.group(1) if m else None


def toc_line(x):
    return re.search(u'\\.\\s+\\.\\s+\\d+\\s*$', x) is not None


def find_body(i, nd):
    got = -1
    q = pnorm(nd)
    head = q[:16]
    for a in range(len(LL[i])):
        win = NL.join(LL[i][a:a + 4])
        if head not in pnorm(win):
            continue
        face, offs = foldmap(win)
        j = face.find(q)
        if j < 0:
            continue
        row = line_at(offs, j)
        if row is not None and not toc_line(LL[i][a + row]):
            got = a + row
    return got


def window(i, a, kind):
    b = a + 1
    if kind == u'sec':
        p0 = secnum(LL[i][a])
        while b < len(LL[i]):
            p = secnum(LL[i][b])
            if p is not None and not p.startswith(p0):
                break
            b += 1
    elif kind == u'para':
        while b < len(LL[i]) and LL[i][b].strip() != u'' and not ffline(LL[i][b].strip()):
            b += 1
    elif kind == u'label':
        while b < len(LL[i]):
            s = LL[i][b].strip()
            if re.fullmatch(u'[A-Za-z ]+constants:', s) or secnum(LL[i][b]) is not None:
                break
            b += 1
    elif kind == u'key':
        while b < len(LL[i]) and not keylin(LL[i][b]):
            b += 1
    else:
        while b < len(LL[i]) and not optlin(LL[i][b]):
            b += 1
    return b


WINS = [(u'4862', u"5.4.  Duplicate Address Detection", u'sec'),
        (u'4862', u"DupAddrDetectTransmits  The number of consecutive Neighbor", u'para'),
        (u'4862', u"Default: 1, but may be overridden by a link-type specific value", u'para'),
        (u'4862', u"To check an address, a node sends DupAddrDetectTransmits", u'para'),
        (u'4862', u"the node SHOULD delay joining the solicited-node multicast address by a random delay", u'para'),
        (u'4861', u"10.  Protocol Constants", u'sec'),
        (u'4861', u"Router constants:", u'label'),
        (u'4861', u"Host constants:", u'label'),
        (u'4861', u"Node constants:", u'label'),
        (u'4429', u"4.4.  Pathological Cases", u'sec'),
        (u'sysctl', u"dad_transmits - INTEGER", u'key'),
        (u'sysctl', u"accept_dad - INTEGER", u'key'),
        (u'sysctl', u"mcast_solicit - INTEGER", u'key'),
        (u'sysd', u"IPv6DuplicateAddressDetection=", u'opt'),
        (u'sysd', u"IPv6RetransmissionTimeSec=", u'opt'), (u'sysd', u"IPv4DuplicateAddressDetectionTimeoutSec=", u'opt')]
CW = []
for tag, head, kind in WINS:
    i = IDX[tag]
    a = find_body(i, head)
    assert a >= 0, (tag, head)
    b = window(i, a, kind)
    txt = NL.join(LL[i][a:b])
    clean = NL.join([x for x in LL[i][a:b] if not is_shell(x, i)])
    nu = sorted(set(RX_STRICT.findall(txt)))
    nuc = sorted(set(RX_STRICT.findall(clean)))
    var = sorted(set(VARRE.findall(txt)))
    varc = sorted(set(VARRE.findall(clean)))
    dig = sorted(set(re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', txt)))
    digc = sorted(set(re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', clean)))
    shell_n = len([x for x in LL[i][a:b] if is_shell(x, i)])
    CW.append([tag, kind, head, a + 1, b, len(nu), len(var), len(dig), nu, var, dig,
               len(nuc), len(varc), len(digc), nuc, varc, digc, shell_n])
M['win_census'] = CW
M['win_numless_with_var'] = [[z[0], z[1], z[2]] for z in CW if z[5] == 0 and z[6] > 0]
M['win_var_kinds'] = sorted(set(v for z in CW for v in z[9]))
M['win_shell_lines'] = [[z[0], z[2], z[17]] for z in CW if z[17] > 0]

# ---------- 12. 默认值位上的形状: 标记词表 + 一位一判 ——
MARKS = [u'Default:', u'Default :', u'Defaults to', u'defaults to', u'Default value is',
         u'Functional default:', u'By default', u'by default']
NOVAL = {u'By default', u'by default'}


def slot_shape(s):
    s = s.strip()
    w = s.split()
    m = re.match(u'^(\\d[\\d,]*(?:\\.\\d+)?) (' + TU + u') ?\\((\\d[\\d,]*) (' + TU + u')\\)', s)
    if m:
        return u'数+单位(括号换算)', [m.group(1), m.group(2), m.group(3), m.group(4)]
    m = re.match(u'^(\\d[\\d,]*(?:\\.\\d+)?) (' + TU + u')\\b', s)
    if m:
        return u'数+单位', [m.group(1), m.group(2)]
    m = re.match(u'^([A-Z][A-Z_0-9]{3,}) (' + TU + u')\\b', s)
    if m:
        return u'变量名+单位', [m.group(1), m.group(2)]
    m = re.match(u'^\\d[\\d,]*(?:\\.\\d+)? ?\\* ?[A-Za-z]', s)
    if m:
        return u'算式', [w[0] + u' ' + w[1] + u' ' + w[2] if len(w) > 2 else s]
    m = re.match(u'^\\d[\\d,]* \\(', s)
    if m:
        return u'裸数(括号注)', [w[0]]
    if w and re.match(u'^\\d[\\d,]*(?:\\.\\d+)?[.,]?$', w[0]):
        return u'裸数', [w[0].strip(u'.,')]
    if w and w[0].strip(u'.,').upper() in (u'TRUE', u'FALSE'):
        return u'布尔字', [w[0].strip(u'.,')]
    if w and w[0].strip(u'.,').lower() in (u'unset', u'none', u'enabled', u'disabled', u'ipv4', u'ipv6'):
        return u'开关/交回字', [w[0].strip(u'.,')]
    return u'散文/交回', [w[0] if w else s]


DSLOT = {}
for i in range(NSRC):
    rowsx, seen = [], set()
    face = FOC[i]
    for mk in MARKS:
        for m in re.finditer(re.escape(mk) + u'[ \\t]+([^\\n]{0,70})', face):
            slot = m.group(1).strip()
            sh, toks = (u'无值位', [u'-']) if mk in NOVAL else slot_shape(slot)
            key = (mk, slot)
            if key in seen:
                continue
            seen.add(key)
            rowsx.append([mk, sh, toks, slot])
    DSLOT[LBL[i]] = rowsx
M['default_slots'] = DSLOT
M['default_slot_kinds'] = dict((k, sorted(set(z[1] for z in v))) for k, v in DSLOT.items())
M['default_slot_n'] = dict((k, len(v)) for k, v in DSLOT.items())

# ---------- 13. 4861 常量表: 名⇎值⇎单位三列, 窗内 ⇎ 全篇两把尺 ——
CTRX = re.compile(u'^\\s*([A-Z][A-Z_0-9]+)\\s+(\\d[\\d,]*(?:\\.\\d+)?|\\.\\d+)'
                  u'( (milliseconds|millisecond|seconds|second|transmissions))?\\s*$')
ca = find_body(1, u"10.  Protocol Constants")
cb = window(1, ca, u'sec')
CT, CTF = [], []
for a in range(ca, cb):
    m = CTRX.match(LL[1][a])
    if m:
        CT.append([m.group(1), m.group(2), m.group(4) if m.group(4) else u'无量纲', a + 1])
for a in range(len(LL[1])):
    m = CTRX.match(LL[1][a])
    if m:
        CTF.append([m.group(1), m.group(2), m.group(4) if m.group(4) else u'无量纲', a + 1])
M['const_rows'] = CT
M['const_rows_doc'] = CTF
M['const_unit_kinds'] = sorted(set(z[2] for z in CT))
M['const_comma_rows'] = [z[0] for z in CT if u',' in z[1]]
M['const_dot_rows'] = [z[0] for z in CT if z[1].startswith(u'.')]
M['const_out_of_win'] = [[z[0], z[1], z[3]] for z in CTF if [z[0], z[1], z[2]] not in
                         [[y[0], y[1], y[2]] for y in CT]]
# --- SCAN END ---

# 闭合差断言: 直接对 M 里的账目键逐枚看(不引未定义名)
for _k in (u'row_ledger', u'read_vs_split'):
    assert M[_k][0] == 0 or len(set(M[_k])) <= 1, u'B93 SCAN 闭合差非零: %s = %s' % (_k, M[_k])
assert OBS == PRE, u'行式对账不平: splitlines−split(nl) = %s ⇎ FF后随换行−尾换行 = %s' % (OBS, PRE)
assert M['dual_unit_lines'] and all(z[6] for z in M['dual_unit_lines']), u'双单位行空或不自证'
assert M['dual_implicit_lines'] and all(z[6] for z in M['dual_implicit_lines']), u'隐式单位行空或不自证'
assert any(z[5] == 0 and z[6] > 0 for z in M['win_census']), u'没有“只有变量、无数字×单位”的窗, 对照轴塌了'
assert M['na_total'] == [len([c for c in TT[i] if ord(c) > 127]) for i in range(NSRC)], u'非 ASCII 计数挪动'

F = M
io.open(MEASA, 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True))
print(u'A 侧量测: %d 枚键 → %s' % (len(F), MEASA))

# ---- 对账件读取(第二套实现 _pick93.py 写的逐键对账; 没有它就只用 A 侧读数) ----
A = F
if os.path.exists(MEAS):
    P = json.load(io.open(MEAS, encoding='utf-8'))
    assert set(P) == set(A), u'对账件与本遍键集不合: 缺 %s 多 %s' % (
        sorted(set(A) - set(P))[:6], sorted(set(P) - set(A))[:6])
    for k in sorted(A):
        assert json.dumps(A[k], sort_keys=True) == json.dumps(
            P[k][0] if isinstance(P[k], list) and len(P[k]) == 2 and not isinstance(P[k][0], list)
            else P[k], sort_keys=True) or A[k] == (P[k][0] if isinstance(P[k], list) else P[k]), \
            u'A 侧与采集侧读数不合: %s' % k
    F = dict((k, v if isinstance(v, list) and v and isinstance(v[0], list) else [v]) for k, v in P.items())
    print(u'对账件已复核: %d 枚键' % len(F))
else:
    print(u'对账件未生成(先跑 corpus/_pick93.py), 本遍用 A 侧读数发射')

# ---- 发射条目 ----
REG = {}


def V(name):
    v = F[name][0] if isinstance(F[name], list) else F[name]
    REG.setdefault(str(v), u"B93V('%s')" % name)
    return v


# 候选锚池: 全取自原始块字面串, 逐条经最宽档自证
ATOMS = [
    u"DupAddrDetectTransmits  The number of consecutive Neighbor Solicitation messages sent while performing Duplicate Address Detection",
    u"A value of one indicates a single transmission with no follow-up retransmissions",
    u"Default: 1, but may be overridden by a link-type specific value in the document that describes the link type",
    u"An interface whose DupAddrDetectTransmits variable is set to zero",
    u"each separated by RetransTimer milliseconds",
    u"within RetransTimer milliseconds after having sent DupAddrDetectTransmits",
    u"the node SHOULD delay joining the solicited-node multicast address by a random delay",
    u"MAX_MULTICAST_SOLICIT 3 transmissions",
    u"RETRANS_TIMER 1,000 milliseconds",
    u"REACHABLE_TIME 30,000 milliseconds",
    u"DELAY_FIRST_PROBE_TIME 5 seconds",
    u"remove the RetransTimer delay during address configuration",
    u"It is not sufficient to merely reduce RetransTimer in order to reduce",
    u"reduced by increasing the RFC 2462 DupAddrDetectTransmits variable to",
    u"dad_transmits - INTEGER",
    u"The amount of Duplicate Address Detection probes to send",
    u"1: Enable DAD (default)",
    u"Whether to perform Optimistic Duplicate Address Detection (RFC 4429)",
    u"Must be a value between 1 millisecond and 60 seconds",
    u"If unset, defaults to 200 milliseconds",
    u"Configures the amount of IPv6 Duplicate Address Detection probes to send",
    u"Quoting from RFC 2461, section 4.4",
    u"The time between retransmitted Neighbor Solicitation messages",
    u"A host forms a link-local address by appending an interface identifier",
    u"per-interface basis on multicast-capable interfaces",
]
PNALL = pnorm(NL.join(TT))
for a in ATOMS:
    assert pnorm(a) in PNALL, u'候选锚穿不到最宽档: %s' % a[:60]

io.open(ATOMFILE, 'w', encoding='utf-8', newline=NL).write(NL.join(ATOMS) + NL)

E = []
E.append(u'🧭 源账: 五份一手文书各答一遍“IPv6 DAD 试几次、隔多久”——'
         u'4862(SLAAC)最先把次数写成变量 ⇎ 4861(邻居发现)只有它把常量印成数 ⇎ 4429(Optimistic DAD)'
         u'⇎ ip-sysctl.txt(Linux) ⇎ systemd_network5(发行版); 五份合观字节 %d ⇎ 码位 %d ⇎ '
         u'splitlines %d ⇎ 剥壳正文 %s 行。'
         % (sum(V('bytes')), sum(V('cp')), sum(V('splitlines')), u'/'.join(str(x) for x in V('body_lines'))))
E.append(u'⛓ 规则链: 判词针 %d 枚 × 四档(逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳去连字), 跨连字断行只有第四档读得出, 见摘壳命中 %d 枚 ⇎ 去连字多读 %d 枚。'
         % (len(NEEDLES), len([x for x in M['needle_src'] if x]), V('needle_dehy_kinds')))
E.append(u'① 次数口径: 4862 只给变量与默认 ⟦A⟧⟨DupAddrDetectTransmits  The number of consecutive Neighbor Solicitation messages sent while performing Duplicate Address Detection⟩'
         u'——“Default: 1” ⟦C⟧⟨Default: 1, but may be overridden by a link-type specific value in the document that describes the link type⟩; '
         u'默认位上是裸数, 无单位(次数无量纲), “A value of one” ⟦B⟧⟨A value of one indicates a single transmission with no follow-up retransmissions⟩。')
E.append(u'② 间隔口径: 4862 把毫秒数整个交回 4861 的 RetransTimer ⟦E⟧⟨each separated by RetransTimer milliseconds⟩, '
         u'自己不赋常量; 4861 才在常量表印数: ⟦H⟧⟨MAX_MULTICAST_SOLICIT 3 transmissions⟩ ⇎ '
         u'⟦I⟧⟨RETRANS_TIMER 1,000 milliseconds⟩ ⇎ ⟦J⟧⟨REACHABLE_TIME 30,000 milliseconds⟩ ⇎ '
         u'⟦K⟧⟨DELAY_FIRST_PROBE_TIME 5 seconds⟩; 十六进制位只出现在系统侧, 单位里的毫秒 ⇎ 秒在常量表并排。')
E.append(u'③ 4429 的改法: 不是把次数调大而是把重传延迟整个取掉 ⟦L⟧⟨remove the RetransTimer delay during address configuration⟩, '
         u'并主张单纯压 RetransTimer 不够 ⟦M⟧⟨It is not sufficient to merely reduce RetransTimer in order to reduce⟩, '
         u'正解是把 DupAddrDetectTransmits 加到大于一 ⟦N⟧⟨reduced by increasing the RFC 2462 DupAddrDetectTransmits variable to⟩。')
E.append(u'④ 系统侧两代默认值: 内核 dad_transmits 默认 1 ⟦O⟧⟨dad_transmits - INTEGER⟩, accept_dad 的 ⟦Q⟧⟨1: Enable DAD (default)⟩; '
         u'optimistic_dad 对应 4429 ⟦R⟧⟨Whether to perform Optimistic Duplicate Address Detection (RFC 4429)⟩; '
         u'ip-sysctl 里没有 use_dad, 也没有 retrans_time 这个键名(缺登记名词进解读注)。')
E.append(u'⑤ 发行版侧: 内核交回(不填数)⇎ IPv4 侧反而给数 ⟦S⟧⟨Must be a value between 1 millisecond and 60 seconds⟩ ⇎ '
         u'⟦T⟧⟨If unset, defaults to 200 milliseconds⟩——同一行印两种单位。')
E.append(u'⑥ 换算自证: 面内双单位行 %d 组全部自证(如 ⟦I⟧⟨RETRANS_TIMER 1,000 milliseconds⟩ ⇎ sysctl 里 “1 second”)⇎ '
         u'隐式外单位行 %d 组(先用 “(in milliseconds)” 声明再写数)。'
         % (len(M['dual_unit_lines']), len(M['dual_implicit_lines'])))
E.append(u'⑦ 跨份等值对: 折成秒后 %s 三档同值。'
         % (u' ⇎ '.join(u'%s 秒' % k for k in sorted(M['conv_same'])),))
E.append(u'⑨ 默认值位形态(一位一判): 4861 §10 窗内常量 %d 枚(千分位 %s ⇎ 前导点 %s ⇎ 无量纲 %s); '
         u'sysctl 侧 default_slot_n = %s; 全篇同正则多出的只有 MTU 这一行。'
         % (len(V('const_rows')), u'⇎'.join(M['const_comma_rows']), u'⇎'.join(M['const_dot_rows']),
            u'⇎'.join([z[2] for z in V('const_rows') if z[2] == u'无量纲']),
            u'/'.join(u'%s=%d' % (k, M['default_slot_n'][k]) for k in LBL)))
E.append(u'🔻 反向零命中: 五份源头无一处把 DAD 间隔写成可执行毫秒, 也无一处把次数强绑到常量; '
         u'“只有变量、无数字×单位”的窗 %d 枚——对照轴由此立起。'
         % len(M['win_numless_with_var']))
E.append(u'ℒ 方法 ⇒ 多文本对读: 同一问五答, 口径差落成键(次数 ⇎ 毫秒 ⇎ 秒 ⇎ 无量纲 ⇎ 交回), '
         u'并给面内自证换算 + 跨份等值对作单位尺的双轨。')
enc = u'\n'.join(E)
assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)
SRC_ALL = PNALL.replace(u' ', u'')
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok).replace(u' ', u'') in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))
_used = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
for a in _used:
    assert pnorm(a) in PNALL, u'编码锚穿不到最宽档: %s' % a[:50]
LET = {chr(65 + i): ATOMS[i] for i in range(len(ATOMS))}
assert sorted(LET) == [chr(65 + i) for i in range(len(ATOMS))], u'标签字母表溢出 26 或次序乱'
_pairs = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', enc)
assert len(_pairs) == n_atoms, u'有锚没紧跟标签(或标签在前): 配对 %d ⇎ 锚 %d' % (len(_pairs), n_atoms)
for t, a in _pairs:
    assert t in LET, u'标签 %s 没有对应的原文块' % t
    assert pnorm(a) in pnorm(LET[t]), u'锚 ⟦%s⟧ 引的串不在第 %s 块内: %s' % (t, t, a[:60])
assert set(t for t, _ in _pairs) == set(LET), u'候选锚池里有条块没被编码区引用: %s' % sorted(
    set(LET) - set(t for t, _ in _pairs))

orig = u'### ⟦A⟧ ⟸ ' + u' ⇎ '.join(SRC) + u'\n\n' + u'\n\n'.join(ATOMS)
title = (u'# B93 多文本对读: IPv6 DAD 重传与次数(五份一手文书)→算子中文——'
         u'次数口径 ⇎ 毫秒/秒口径 ⇎ 变量/数值口径三条并列, 面内自证换算 ⇎ 跨份等值对双轨\n')
srcline = (u'src: %s (%d 字节, 折平 %d 字符) '
           u'(多文本对读: 五份源同题各答一遍, 口径差落成键, 数字/单位/键名逐字保留)\n'
           % (u' ⇎ '.join(SRC), sum(V('bytes')), sum(V('cp'))))
tagsline = (u'tags: 多文本对读 截止后专业信息 规则链逐环保真键(次数⇎间隔⇎改法⇎系统侧⇎发行版) '
            u'四档口径键(逐行⇎全篇⇎摘壳⇎摘壳去连字) 默认位形态键(常量表 17 行 + sysctl/sysd 位分类) '
            u'面内自证换算键 跨份等值对 反向零命中 标量 3⇎清单 %d 项\n' % len(NEEDLES))
md = (title + srcline + u'; ' + tagsline + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n\n(待 _fill93.py 第二遍独立复算后写回)\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(md)
print(u'B93 建条目: %s' % ENTRY)
print(u'编码区 %d 字符(不含换行), 编码区锚 %d 处, 候选锚 %d 条, 登记面值 %d 枚'
      % (len(enc.replace(NL, u'')), n_atoms, len(ATOMS), len(REG)))
assert REG, u'REG 空——V() 没登记任何面值'
io.open(u'corpus/_b93flat.json', 'w', encoding='utf-8').write(
    json.dumps(REG, ensure_ascii=False, sort_keys=True) + NL)
print(u'DERIV 键表: corpus/_b93flat.json %d 键' % len(REG))
```