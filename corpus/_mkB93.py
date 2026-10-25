# -*- coding: utf-8 -*-
"""B93 建条遍(第二套实现): 同一批定义, 另一套算法, 逐键与采集遍 _pick93.py 对账.

题面: “IPv6 重复地址检测到底试几次、每次隔多久”——4862(SLAAC: 写成变量 DupAddrDetectTransmits 并给
Default: 1, 间隔整个交回 4861 的 RetransTimer, 本文一枚毫秒也不赋) ⇎ 4861(邻居发现: 只有它把常量印成数,
同一张 §10 表里 毫秒 ⇎ 秒 ⇎ 次数 ⇎ 无量纲 四种口径并排) ⇎ 4429(Optimistic DAD: 主张删掉 RetransTimer 这段延迟)
⇎ ip-sysctl(dad_transmits Default: 1 ⇎ accept_dad 的 1: Enable DAD (default); 这份里没有 use_dad 也没有 retrans_time)
⇎ systemd_network5(IPv6 侧不填数交回内核, IPv4 侧反而给数: defaults to 200 milliseconds, 同一行另印
between 1 millisecond and 60 seconds 两种单位)。

十处换算法不换定义:
①切行: 本遍游标扫描逐段切 ⇎ 采集遍 split('\n'); ②折平: re.sub(\\s+) 再 strip ⇎ ' '.join(split());
③找针: 前视 finditer 收每一个起点(可重叠) ⇎ 游标 find 环步进针长(不重叠); ④词界: 就地邻位函数判 ⇎ 逐枚 isalpha;
⑤行定位: 全篇折平面+一张全局区间表取首枚 ⇎ 4 行滑窗各建一张区间表; ⑥段窗定界: 谓词生成器 next() 求终点 ⇎ while 游标;
⑦默认值位: 表驱动 first-match 一条链 ⇎ 五条 if 各一条正则; ⑧单位换算表: 由 秒 出发的因子链派生 ⇎ 查现成毫秒表;
⑨跨份同值对: 先按折算值分组再组内配对 ⇎ 全局双重循环; ⑩HTML 层: 游标收标签跨度累加 ⇎ findall 后 sum(len).
所有正文数字由 V()/J()/EXPR() 注册后插值, 一枚都不手打; 锚一律由面上位置导出; 键名等于所量之物。
对账结果写回 corpus/_b93meas.json, 现量落 corpus/_b93flat.json。"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'4862', u'4861', u'4429', u'sysctl', u'sysd']
NSRC = 5
YR = [2006, 2007, 2006, 2023, 2023]
PATH = [u'corpus/raw/dad6/rfc4862.txt', u'corpus/raw/dad6/rfc4861.txt', u'corpus/raw/dad6/rfc4429.txt',
        u'corpus/raw/dad6/ip-sysctl.txt', u'corpus/raw/dad6/systemd_network5.txt']
STRIPPED = u'corpus/raw/dad6/systemd_network5.html'
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire93.py 把这一段 ⇎ 前面的模块级前奏一并机械切进 _b93_scan)


def rd(p):
    return io.open(p, 'rb').read()


def cut_lines(t):
    """游标切行: 每次只找一个换行符的位置, 就地切片(采集遍是一条 split)。"""
    out, a = [], 0
    while True:
        j = t.find(NL, a)
        if j < 0:
            out.append(t[a:])
            return out
        out.append(t[a:j])
        a = j + 1


def dr(y):
    return y[:len(y) - 1] if y[len(y) - 1:] == u'\r' else y


def pnorm(s):
    return re.sub(u'\\s+', u' ', s).strip().lower()


OCC = {}


def occ_pos(s, w):
    """前视捕获组 finditer: 每个起点都收, 因此可重叠(采集遍的游标环步进一枚针长, 读不到重叠)。"""
    rx = OCC.get(w)
    if rx is None:
        rx = OCC[w] = re.compile(u'(?=(' + re.escape(w) + u'))')
    return [m.start(1) for m in rx.finditer(s)]


def cnt_ub(s, w, kind):
    tst = (lambda c: c.isalpha()) if kind == u'alpha' else (
        (lambda c: c.isdigit()) if kind == u'digit' else (lambda c: c.isalnum()))
    n, c, ln = len(w), 0, len(s)
    for j in occ_pos(s, w):
        a, b = j - 1, j + n
        if (a < 0 or not tst(s[a])) and (b >= ln or not tst(s[b])):
            c += 1
    return c


def runs_of_digits(x):
    n, run = 0, 0
    for c in x:
        if u'0' <= c <= u'9':
            run += 1
        elif run:
            n += 1
            run = 0
    return n + (1 if run else 0)


RX_FOOT = re.compile(u'\\[Page \\d+\\]')
RX_HDRO = re.compile(u'^\\s*([A-Z][a-z\\u2019-]+, et al\\.|[A-Z][a-zA-Z]+ +[A-Za-z ]*?(?:19|20)\\d\\d) +'
                     u'(Standards Track|Informational|Experimental|[A-Z][a-z]+ \\d+)?')
RX_HDT = re.compile(u'^RFC\\d+ +\\S.*((19|20)\\d\\d)\\s*$')
RX_IETF = re.compile(u'^\\s*(Internet Engineering Task Force|Network Working Group)\\s*$')
RX_KEY = re.compile(u'^[a-z][a-z_0-9]* - (INTEGER|BOOLEAN|STRING|DWORD)\\s*$')
RX_OPT = re.compile(u'^\\s{4,}[A-Za-z][A-Za-z0-9]*= *$')
RX_ADD = re.compile(u'^\\s*Added in version \\d+\\.\\s*$')


def foot(x):
    """页脚标记: 游标定 ‘[Page ’ 起点, 逐字符收数字, 再验紧跟的 ’]’(采集遍是一条 search 正则)。"""
    i = 0
    while True:
        j = x.find(u'[Page ', i)
        if j < 0:
            return False
        k, d = j + 6, 0
        while k < len(x) and x[k] >= u'0' and x[k] <= u'9':
            k += 1
            d += 1
        if d and x[k:k + 1] == u']':
            return True
        i = j + 1


def hdr_old(x):
    return RX_HDRO.match(x) is not None and RX_FOOT.search(x) is not None


def hdr_title(x):
    return RX_HDT.match(x) is not None


def ietf_line(x):
    return RX_IETF.match(x) is not None


def keylin(x):
    return RX_KEY.match(x) is not None


def optlin(x):
    return RX_OPT.match(x) is not None


def addedlin(x):
    return RX_ADD.match(x) is not None


def ffline(x):
    return len(x) == 1 and ord(x[0]) == 12


def blankish(x):
    return re.fullmatch(u'\\s*', x) is not None


FORMS = [(u'页脚 [Page n]', foot), (u'旧式眉行', hdr_old), (u'标题眉行', hdr_title),
         (u'IETF/NWG 独立行', ietf_line), (u'换页符独占行', ffline), (u'空行', blankish),
         (u'Added in version n.', None)]
SHM = []           # 壳形布尔矩阵(在面建好之后填): SHM[k][i] = 第 k 形在第 i 份的命中行数


def is_shell(x, i):
    return (foot(x) or hdr_old(x) or hdr_title(x) or ietf_line(x) or ffline(x) or blankish(x)
            or (i == 4 and addedlin(x)))


def line_face(t):
    """全篇折平面 + (面偏移 → 原行) 区间表: 一次建好, 供所有行定位复用。"""
    offs, pos, seg = [], 0, []
    for i, l in enumerate(t.split(NL)):
        c = pnorm(dr(l))
        if not c:
            continue
        offs.append((pos, pos + len(c), i))
        seg.append(c)
        pos += len(c) + 1
    return u' '.join(seg), offs


def line_at(offs, s0):
    lo, hi, cand = 0, len(offs) - 1, None
    while lo <= hi:                       # 区间表二分定位(采集遍是线性筛起点)
        mid = (lo + hi) // 2
        if offs[mid][0] <= s0:
            cand = offs[mid][2]
            lo = mid + 1
        else:
            hi = mid - 1
    return cand


RX_DH = re.compile(u'(\\w)- (\\w)')

B = [rd(p) for p in PATH]
HB = rd(STRIPPED)
T = [b.decode('utf-8') for b in B]        # 严格解码(采集遍是 errors='replace')
HT = HB.decode('utf-8')
RAWL = [cut_lines(t) for t in T]
L = [[dr(y) for y in RAWL[i]] for i in range(NSRC)]
FACE, OFFS = [], []
for i in range(NSRC):
    fc, of = line_face(T[i])
    FACE.append(fc)
    OFFS.append(of)
FOL = [pnorm(T[i]) for i in range(NSRC)]
FOC = [re.sub(u'\\s+', u' ', T[i]).strip() for i in range(NSRC)]      # 保大小写折平
for k, (nm, fn) in enumerate(FORMS):
    if nm == u'Added in version n.':
        SHM.append([len([x for x in L[i] if addedlin(x)]) if i == 4 else 0 for i in range(NSRC)])
    else:
        SHM.append([len([x for x in L[i] if fn(x)]) for i in range(NSRC)])

# ---------- 0. 面量 ⇎ 行式 ⇎ 换页账 ----------
F['bytes'] = [len(B[i]) for i in range(NSRC)]
F['bytes_stat'] = [os.path.getsize(p) for p in PATH]
F['cp'] = [len(T[i]) for i in range(NSRC)]
F['n_lf'] = [sum([1 for c in T[i] if c == NL]) for i in range(NSRC)]
F['n_cr'] = [sum([1 for c in T[i] if c == u'\r']) for i in range(NSRC)]
F['splitnl'] = [F['n_lf'][i] + 1 for i in range(NSRC)]
F['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
F['readlines'] = [len(list(io.open(PATH[i], encoding='utf-8', newline=NL))) for i in range(NSRC)]
BOUNDS = u'\x0b\x0c\x1c\x1d\x1e\x1f\x85\u2028\u2029'
F['othsep'] = [sum([1 for c in T[i] if c in BOUNDS]) for i in range(NSRC)]
F['ff'] = [len(occ_pos(T[i], u'\x0c')) for i in range(NSRC)]
F['ff_led'] = [len([x for x in L[i] if x[:1] == u'\x0c']) for i in range(NSRC)]
F['ff_before_nl'] = [sum([1 for k in range(len(T[i]) - 1)
                          if T[i][k] == u'\x0c' and T[i][k + 1] == NL]) for i in range(NSRC)]
F['trailing_nl'] = [1 if T[i][len(T[i]) - 1:] == NL else 0 for i in range(NSRC)]
F['ff_at_eof'] = [1 if T[i][len(T[i]) - 1:] == u'\x0c' else 0 for i in range(NSRC)]
F['blank'] = [len([x for x in L[i] if blankish(x)]) for i in range(NSRC)]
F['nonblank'] = [len([x for x in L[i] if not blankish(x)]) for i in range(NSRC)]
F['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
ML = []
for i in range(NSRC):
    m = 0
    for x in L[i]:
        n = 0
        for c in x:
            n += 1
        if n > m:
            m = n
    ML.append(m)
F['maxlen_scan'] = ML
F['tab'] = [sum([1 for c in T[i] if c == u'\t']) for i in range(NSRC)]
F['tab_led'] = [len([x for x in L[i] if x.startswith(u'\t')]) for i in range(NSRC)]
F['nonascii'] = [sorted(set([ord(c) for c in T[i] if ord(c) > 127])) for i in range(NSRC)]
F['na_total'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(NSRC)]
F['bom'] = [1 if T[i][:1] and ord(T[i][0]) == 65279 else 0 for i in range(NSRC)]
F['utf8_extra'] = [F['bytes'][i] - F['cp'][i] for i in range(NSRC)]
F['fold_eq'] = [1 if u' '.join(T[i].lower().split()) == FOL[i] else 0 for i in range(NSRC)]
F['row_ledger'] = [F['blank'][i] + F['nonblank'][i] - F['splitnl'][i] for i in range(NSRC)]
F['read_vs_split'] = [F['readlines'][i] + F['trailing_nl'][i] - F['splitnl'][i] for i in range(NSRC)]
F['lines_ruler_diff'] = [F['splitlines'][i] - F['splitnl'][i] - (F['ff_before_nl'][i] - F['trailing_nl'][i])
                         for i in range(NSRC)]
print(u'0 面量: 字节 %s ⇎ 码位 %s ⇎ 换行 %s ⇎ split(nl) %s ⇎ splitlines %s ⇎ 其他界符 %s'
      % (F['bytes'], F['cp'], F['n_lf'], F['splitnl'], F['splitlines'], F['othsep']))
print(u'  两把长度尺同值 %s ⇎ 折平两路同面 %s' % (F['bytes'] == F['bytes_stat'], sum(F['fold_eq'])))

# ---------- 0b. HTML 档 ----------
def tag_spans(s):
    """游标收标签跨度: 逐枚定 ‘<’ 与紧随的 ‘>’ , 累加跨度长度(采集遍是 findall 后 sum(len))。"""
    n, tot, i = 0, 0, 0
    while True:
        a = s.find(u'<', i)
        if a < 0:
            return n, tot
        b = s.find(u'>', a)
        if b < 0:
            return n, tot
        n += 1
        tot += b - a + 1
        i = b + 1


F['tag_n'], F['tag_chars'] = tag_spans(HT)
F['ent_n'] = len(re.findall(u'&[A-Za-z#0-9]+;', HT))
F['html_bytes'] = len(HB)
F['html_cp'] = len(HT)
F['html_lines'] = len(cut_lines(HT))
F['html_lf'] = sum([1 for c in HT if c == NL])
F['stripped_cp'] = F['cp'][4]
F['html_minus_stripped'] = F['html_cp'] - F['stripped_cp']
F['own_detag_cp'] = F['html_cp'] - F['tag_chars']
F['disk_vs_own'] = F['own_detag_cp'] - F['cp'][4]
print(u'0b HTML: 原文 %d 字节／%d 码位 ⇎ 标签 %d 枚吃 %d ⇎ 盘上剥壳面 %d ⇎ 本遍自剥 %d ⇎ 差 %d ⇎ 实体 %d'
      % (F['html_bytes'], F['html_cp'], F['tag_n'], F['tag_chars'], F['cp'][4], F['own_detag_cp'],
         F['disk_vs_own'], F['ent_n']))

# ---------- 1. 壳形矩阵 ⇎ 容斥 ----------
F['foot_page'] = SHM[0]
F['hdr_old'] = SHM[1]
F['hdr_title'] = SHM[2]
F['ietf_alone'] = SHM[3]
F['ff_led_line'] = SHM[4]
F['blank_shell'] = SHM[5]
F['added_lines'] = SHM[6]
F['key_lines'] = [len([x for x in L[i] if keylin(x)]) for i in range(NSRC)]
F['opt_lines'] = [len([x for x in L[i] if optlin(x)]) for i in range(NSRC)]
F['pgnum'] = [len([x for x in L[i] if x.strip() != u'' and runs_of_digits(x) == 1
                   and len([c for c in x if not (c.isdigit() or c.isspace())]) == 0]) for i in range(NSRC)]
F['shell_lines'] = [len([1 for x in L[i] if is_shell(x, i)]) for i in range(NSRC)]
F['body_lines'] = [len([1 for x in L[i] if not is_shell(x, i)]) for i in range(NSRC)]
REP = []
for i in range(NSRC):
    r = 0
    for x in L[i]:
        h = 0
        for fn in (foot, hdr_old, hdr_title, ietf_line, ffline, blankish):
            if fn(x):
                h += 1
        if i == 4 and addedlin(x):
            h += 1
        if h > 1:
            r += h - 1
    REP.append(r)
F['shell_repeat'] = REP
F['shell_pred_sum'] = [sum([SHM[k][i] for k in range(len(SHM))]) for i in range(NSRC)]
F['shell_led'] = [F['shell_pred_sum'][i] - F['shell_repeat'][i] - F['shell_lines'][i] for i in range(NSRC)]
print(u'1 壳形: 页脚 %s 旧式眉 %s 键行 %s 选项行 %s Added 行 %s 独立页码行 %s 缩进打头行 %s'
      % (F['foot_page'], F['hdr_old'], F['key_lines'], F['opt_lines'], F['added_lines'],
         F['pgnum'], F['tab_led']))
print(u'  壳行 %s ⇎ 六形之和 %s ⇎ 重数 %s ⇎ 容斥差 %s' % (F['shell_lines'], F['shell_pred_sum'],
                                                        F['shell_repeat'], F['shell_led']))

# ---------- 2. 义务词两档 ⇎ 出现尺两把 ----------
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY', u'MUST NOT be', u'NOT RECOMMENDED']
F['ob_line'] = [[sum([cnt_ub(x, w, u'alpha') for x in L[i]]) for w in OB] for i in range(NSRC)]
F['ob_fold'] = [[cnt_ub(FOC[i], w, u'alpha') for w in OB] for i in range(NSRC)]
F['ob_non'] = [[FOC[i].count(w) for w in OB] for i in range(NSRC)]
F['ob_ruler_diff'] = [F['ob_fold'][i][k] - F['ob_non'][i][k] for i in range(NSRC) for k in range(len(OB))]
F['ob_wrap'] = [F['ob_fold'][i][k] - F['ob_line'][i][k] for i in range(NSRC) for k in range(len(OB))]
F['ob_wrap2'] = [sum([F['ob_fold'][i][k] - F['ob_line'][i][k] for k in range(len(OB))]) for i in range(NSRC)]
F['kw_all'] = [len(re.findall(u'(?i)\\b(must|should|may)\\b', T[i])) for i in range(NSRC)]
F['kw_caps'] = [len(re.findall(u'\\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY)\\b', T[i])) for i in range(NSRC)]
F['kw_low_only'] = [F['kw_all'][i] - F['kw_caps'][i] for i in range(NSRC)]
F['dbl_space'] = [len(re.findall(u'(?<=\\S)  +(?=\\S)', T[i])) for i in range(NSRC)]
DSF = [len(re.findall(u'(?<=\\S)  +(?=\\S)', FOC[i])) for i in range(NSRC)]
F['dbl_space_fold'] = DSF
F['dbl_space_eaten'] = [F['dbl_space'][i] - DSF[i] for i in range(NSRC)]
print(u'2 义务词 逐行 %s ⇎ 折平 %s ⇎ 跨行涨量 %s' % (F['ob_line'], F['ob_fold'], F['ob_wrap2']))
print(u'  重叠尺比不重叠尺多读 %s ⇎ 双空格被折平吃掉 %s' % (sum(F['ob_ruler_diff']), F['dbl_space_eaten']))

# ---------- 3. 判词针四档 ----------
SHP = [pnorm(NL.join([x for x in L[i] if not is_shell(x, i)])) for i in range(NSRC)]
SHT, DHT, DEHS, DEHF = [], [], [], []
for i in range(NSRC):
    s2, n2 = RX_DH.subn(u'\\1-\\2', SHP[i])
    SHT.append(s2)
    DEHS.append(n2)
    s3, n3 = RX_DH.subn(u'\\1-\\2', FOL[i])
    DHT.append(s3)
    DEHF.append(n3)
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
F['needle_n'] = len(NEEDLES)
F['dehyphen_chars'] = [len(SHP[i]) - len(SHT[i]) for i in range(NSRC)]
F['dehyphen_edits'] = DEHS
F['dehyphen_fold_edits'] = DEHF
N4 = []
for nd in NEEDLES:
    q = pnorm(nd)
    r = []
    for i in range(NSRC):
        cl = len([1 for x in L[i] if q in pnorm(x)])
        cf = FOC[i].lower().count(q)
        cs = SHP[i].count(q)
        ct = SHT[i].count(q)
        r.append([cl, cf, cs, ct])
    N4.append(r)
F['needles4'] = N4
F['needle_src'] = [[LBL[i] for i in range(NSRC) if r[i][2] > 0] for r in N4]
F['needle_src_dehy'] = [[LBL[i] for i in range(NSRC) if r[i][3] > 0] for r in N4]
F['needle_wrap_kinds'] = len([1 for r in N4 if any(r[i][1] > 0 and r[i][0] == 0 for i in range(NSRC))])
F['needle_dehy_kinds'] = len([1 for r in N4 if any(r[i][3] > 0 and r[i][2] == 0 for i in range(NSRC))])
F['needle_line_only'] = len([1 for r in N4 if any(r[i][0] > 0 and r[i][1] == 0 for i in range(NSRC))])
print(u'3 判词针 %d 枚: 换行涨量 %d 种 ⇎ 去连字独读 %d 种 ⇎ 只逐行档读到 %d 种'
      % (F['needle_n'], F['needle_wrap_kinds'], F['needle_dehy_kinds'], F['needle_line_only']))

# ---------- 4. 行定位(全篇面 + 全局区间表) ----------
def find_line(i, nd, dehy=False):
    q = pnorm(nd)
    fc = DHT[i] if dehy else FACE[i]
    of = OFFS[i]
    ps = occ_pos(fc, q)
    if not ps:
        return -1
    return line_at(of, ps[0])


def find_body(i, nd):
    """同一句先在目录页出现: 取最后一个命中, 且该行不得是目录点线行。"""
    q = pnorm(nd)
    ps = occ_pos(FACE[i], q)
    got = -1
    for p in ps:
        ln = line_at(OFFS[i], p)
        if ln is None or not toc_line(L[i][ln]):
            got = ln
    return got


PINL = []
for k, r in enumerate(N4):
    shy = any(r[i][2] > 0 for i in range(NSRC))
    dhy = any(r[i][3] > 0 and r[i][2] == 0 for i in range(NSRC))
    if not (shy or dhy):
        continue
    for i in range(NSRC):
        a = find_line(i, NEEDLES[k])
        dh = 1
        if a < 0:
            a = find_line(i, NEEDLES[k], dehy=True)
            dh = 2
        if a >= 0:
            PINL.append([LBL[i], NEEDLES[k], a + 1, dh])
F['pin_lines'] = PINL
F['pin_dh2'] = len([x for x in PINL if x[3] == 2])
F['pin_kinds'] = len(set([x[1] for x in PINL]))
print(u'4 锚定行 %d 条(去连字档 %d 条 ⇎ 不同针 %d 枚)' % (len(PINL), F['pin_dh2'], F['pin_kinds']))

# ---------- 5. 数值×单位: 严 ⇎ 宽两轨 ----------
RX_STRICT = re.compile(u'(?<![A-Za-z0-9])(\\d[\\d,]*(?:\\.\\d+)?)[ ]?'
                       u'(milliseconds|millisecond|seconds|second|transmissions|probes|messages)(?![A-Za-z])')
RX_LOOSE = re.compile(u'(\\d[\\d,]*(?:\\.\\d+)?)\\.? ?'
                      u'(milliseconds|millisecond|seconds|second|transmissions|probes|messages|ms|sec|s)')
F['numunit_strict'] = [[list(z) for z in sorted(set(RX_STRICT.findall(T[i])))] for i in range(NSRC)]
F['numunit_loose'] = [[list(z) for z in sorted(set(RX_LOOSE.findall(FOL[i])))] for i in range(NSRC)]
F['strict_n'] = [len(RX_STRICT.findall(T[i])) for i in range(NSRC)]
F['loose_n'] = [len(RX_LOOSE.findall(FOL[i])) for i in range(NSRC)]
F['loose_short_n'] = [len([z for z in RX_LOOSE.findall(FOL[i]) if z[1] in (u'ms', u'sec', u's')])
                      for i in range(NSRC)]
F['loose_all_short'] = [F['loose_short_n'][i] == F['loose_n'][i] for i in range(NSRC)]
F['comma_nums'] = [sorted(set(re.findall(u'(?<![\\d.])(\\d{1,3},\\d{3}(?:,\\d{3})?)', T[i])))
                   for i in range(NSRC)]
F['dotfrac_nums'] = [sorted(set(re.findall(u'(?<![\\d.)])\\.(\\d+)', T[i]))) for i in range(NSRC)]
F['dotlead_unit'] = [[list(z) for z in sorted(set(re.findall(
    u'(?<![\\d])\\.(\\d+)(?: )?(milliseconds|millisecond|seconds|second)(?![A-Za-z])', T[i])))]
    for i in range(NSRC)]
F['range_nums'] = [sorted(set(re.findall(u'(\\d+\\.\\.\\d+|1\\.\\.\\.\\d+)', T[i]))) for i in range(NSRC)]
F['percent'] = [sorted(set(re.findall(u'(\\d+%)', T[i]))) for i in range(NSRC)]
F['fraction'] = [sorted(set(re.findall(u'\\((\\d/\\d)\\)', T[i]))) for i in range(NSRC)]
UN = u'(milliseconds|millisecond|seconds|second|transmissions|probes|messages|hours|hour|minutes|minute|days|day)'
F['glued_unit'] = [[list(z) for z in sorted(set(re.findall(u'(?<![A-Za-z0-9])(\\d+)(' + UN + u')(?![A-Za-z])', T[i])))]
                   for i in range(NSRC)]
F['spaced_unit'] = [[list(z) for z in sorted(set(re.findall(u'(?<![A-Za-z0-9])(\\d+) (' + UN + u')(?![A-Za-z])', T[i])))]
                    for i in range(NSRC)]
F['hex_default'] = [sorted(set(re.findall(
    u'(?m)^[ \\t]*Default[^\\n]*?(0x[0-9A-Fa-f]+|INT_MAX|UINT_MAX)', T[i]))) for i in range(NSRC)]
F['dig_ipv_noise'] = [len(re.findall(u'(?i)(?:ipv|ip)(\\d)', T[i])) for i in range(NSRC)]
F['dig_all'] = [[len(re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', T[i])), F['dig_ipv_noise'][i]] for i in range(NSRC)]
F['unit_in_keyname'] = [sorted(set(re.findall(u'([A-Za-z0-9]*(?:Sec|Millis|Usec|Ms))[ =]', T[i])))
                        for i in range(NSRC)]
print(u'5 严轨枚数 %s ⇎ 宽轨枚数 %s ⇎ 宽轨走短单位的 %s ⇎ 全短的 %s'
      % (F['strict_n'], F['loose_n'], F['loose_short_n'], F['loose_all_short']))
print(u'  千分位 %s ⇎ 前导点 %s ⇎ 粘连单位 %s ⇎ 键名带单位 %s'
      % (F['comma_nums'], F['dotfrac_nums'], [len(z) for z in F['glued_unit']],
         [len(z) for z in F['unit_in_keyname']]))

# ---------- 6. 单位换算(因子链派生表) ----------
MS = 1.0                                    # 基准单位取毫秒, 其余全由因子链派生(采集遍是一张现成的毫秒表)
SINGLE = {u'nanosecond': MS / 1000.0 / 1000.0, u'millisecond': MS, u'second': MS * 1000.0,
          u'minute': 60 * MS * 1000.0, u'hour': 60 * 60 * MS * 1000.0, u'day': 24 * 60 * 60 * MS * 1000.0}
UNIT = {}
for _k, _v in SINGLE.items():
    UNIT[_k] = _v
    UNIT[_k + u's'] = _v
UNIT[u'ms'] = SINGLE[u'millisecond']
UNIT[u'ns'] = SINGLE[u'nanosecond']
TU = u'(ns|nanoseconds|ms|milliseconds|millisecond|seconds|second|minutes|minute|hours|hour|days|day)'
DUALRE = re.compile(u'(\\d[\\d,]*) ' + TU + u' ?\\((\\d[\\d,]*) ' + TU + u'\\)')
DUALIM = re.compile(u'(\\d[\\d,]*) ?\\((\\d[\\d,]*) ' + TU + u'\\)')


def numv(s):
    return float(s.replace(u',', u''))


DUAL = []
for i in range(NSRC):
    for x in L[i]:
        m = DUALRE.search(x)
        if m:
            DUAL.append([LBL[i], m.group(0).strip(), numv(m.group(1)), m.group(2),
                         numv(m.group(3)), m.group(4),
                         numv(m.group(1)) * UNIT[m.group(2)] == numv(m.group(3)) * UNIT[m.group(4)]])
F['dual_unit_lines'] = DUAL
F['dual_prove'] = [z[6] for z in DUAL]
F['dual_gloss_forms'] = sorted(set(u'%g %s' % (z[4], z[5]) for z in DUAL))
F['dual_plural_at_one'] = len([z for z in DUAL if z[4] == 1 and z[5].endswith(u's')])
DUAL2 = []
BLK = []
cur = None
for x in L[3]:
    if keylin(x):
        cur = [x.split(u' - ')[0], []]
        BLK.append(cur)
    elif cur is not None:
        cur[1].append(x)
for k, body in BLK:
    m = re.search(u'\\((in )(milliseconds|seconds)\\)', u' '.join(body))
    d = [z for z in body if re.search(DUALIM, z)]
    if m and d:
        mm = DUALIM.search(d[0])
        DUAL2.append([k, mm.group(0).strip(), m.group(2), numv(mm.group(1)),
                      numv(mm.group(2)), mm.group(3),
                      numv(mm.group(1)) * UNIT[m.group(2)] == numv(mm.group(2)) * UNIT[mm.group(3)]])
F['dual_implicit_lines'] = DUAL2
CONV = []
RX_CONV = re.compile(u'(?<![A-Za-z0-9])(\\d[\\d,]*(?:\\.\\d+)?)([ ]?)(nanoseconds|milliseconds|millisecond'
                     u'|seconds|second|minutes|minute)(?![A-Za-z])')
for i in range(NSRC):
    for m in RX_CONV.finditer(T[i]):
        CONV.append([LBL[i], m.group(1), m.group(3), numv(m.group(1)) * UNIT[m.group(3)] / (MS * 1000.0),
                     m.group(2) == u''])
F['unit_conv'] = CONV
F['conv_glued_n'] = len([z for z in CONV if z[4]])
F['conv_spaced_n'] = len([z for z in CONV if not z[4]])
GRP = {}
for a in range(len(CONV)):
    GRP.setdefault(CONV[a][3], []).append(a)
SAME = {}
seen = set()
for val in GRP:
    idxs = GRP[val]
    for a in range(len(idxs)):
        for b in range(a + 1, len(idxs)):
            p, q = CONV[idxs[a]], CONV[idxs[b]]
            if p[0] == q[0] or p[1] == q[1]:
                continue
            pair = (u'%s:%s %s' % (p[0], p[1], p[2]), u'%s:%s %s' % (q[0], q[1], q[2]))
            if pair in seen:
                continue
            seen.add(pair)
            SAME.setdefault(val, []).append(pair)
for k in SAME:
    SAME[k].sort(key=lambda pr: (pr[0], pr[1]))
F['conv_same'] = dict((str(k), SAME[k]) for k in sorted(SAME))
F['conv_same_n'] = sum(len(v) for v in SAME.values())
F['conv_vals'] = sorted(set([z[3] for z in CONV]))
print(u'6 换算 %d 组(空格 %d ⇎ 粘连 %d) ⇎ 折算后去重值 %d 枚 ⇎ 跨份同值对 %d 组 %d 对'
      % (len(CONV), F['conv_spaced_n'], F['conv_glued_n'], len(F['conv_vals']),
         len(F['conv_same']), F['conv_same_n']))
print(u'  面内自证双单位行 %d ⇎ 隐式外单位行 %d ⇎ 值为 1 仍写复数 %d'
      % (len(DUAL), len(DUAL2), F['dual_plural_at_one']))

# ---------- 7. 参数名拼写族: 三把名尺 ----------
NAMES = [u'DupAddrDetectTransmits', u'dad_transmits', u'use_dad', u'accept_dad', u'optimistic_dad',
         u'enhanced_dad', u'IPv6DuplicateAddressDetection', u'DuplicateAddressDetection',
         u'IPv4DuplicateAddressDetectionTimeoutSec', u'IPv6RetransmissionTimeSec',
         u'RetransTimer', u'RETRANS_TIMER', u'MAX_RTR_SOLICITATION_DELAY', u'DELAY_FIRST_PROBE_TIME',
         u'MAX_MULTICAST_SOLICIT', u'MAX_UNICAST_SOLICIT', u'mcast_solicit', u'ucast_solicit',
         u'app_solicit', u'router_solicitations', u'router_solicitation_interval',
         u'retrans_time', u'RetryCount', u'MAX_RTR_SOLICITATIONS']
NRM = [pnorm(x.replace(u'_', u' ')) for x in NAMES]
F['name_raw'] = [[T[i].count(x) for x in NAMES] for i in range(NSRC)]
F['name_ci'] = [[FOL[i].count(pnorm(x)) for x in NAMES] for i in range(NSRC)]
F['name_norm'] = [[cnt_ub(FOL[i], nrm, u'none') for nrm in NRM] for i in range(NSRC)]
F['name_absent'] = [x for x in NAMES if not any([occ_pos(T[i], x) for i in range(NSRC)])]
F['name_n'] = len(NAMES)
print(u'7 名族 %d 枚: 一枚也不出的 %s ⇎ 驼峰名只在 sysd %s ⇎ 下划线名只在 sysctl %s'
      % (len(NAMES), F['name_absent'],
         [NAMES[k] for k in range(len(NAMES)) if sum(F['name_raw'][i][k] for i in range(4)) == 0
          and F['name_raw'][4][k] > 0],
         [NAMES[k] for k in range(len(NAMES)) if sum(F['name_raw'][i][k] for i in range(3)) == 0
          and F['name_raw'][3][k] > 0]))

# ---------- 8. 默认值句式 ----------
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
F['shape_lbls'] = [s[0] for s in SHAPES]
SN = []
for i in range(NSRC):
    rowx, numrow = [], []
    for mk, rx in SHAPES:
        hits = rx.findall(T[i])
        rowx.append(len(hits))
        numrow.append(len([z for z in hits if re.match(u'^[-.\\d]', u'%s' % (z,))]))
    SN.append(rowx)
    F.setdefault('default_val_is_num', []).append(numrow)
F['shape_n'] = SN
F['default_gloss'] = [len(re.findall(u'(?m)^[ \\t]*Default: +\\d \\(', T[i])) for i in range(NSRC)]
F['shape_face_kinds'] = [len([1 for v in F['shape_n'][i] if v]) for i in range(NSRC)]
MARKS = [u'Default:', u'Default :', u'Defaults to', u'defaults to', u'Default value is',
         u'Functional default:', u'By default', u'by default']
NOVAL = {u'By default', u'by default'}
RULES = [
    (u'数+单位(括号换算)', re.compile(u'^(\\d[\\d,]*(?:\\.\\d+)?) (' + TU + u') ?\\((\\d[\\d,]*) (' + TU + u')\\)'),
     lambda m, w: [m.group(1), m.group(2), m.group(3), m.group(4)]),
    (u'数+单位', re.compile(u'^(\\d[\\d,]*(?:\\.\\d+)?) (' + TU + u')\\b'), lambda m, w: [m.group(1), m.group(2)]),
    (u'变量名+单位', re.compile(u'^([A-Z][A-Z_0-9]{3,}) (' + TU + u')\\b'), lambda m, w: [m.group(1), m.group(2)]),
    (u'算式', re.compile(u'^\\d[\\d,]*(?:\\.\\d+)? ?\\* ?[A-Za-z]'),
     lambda m, w: [(w[0] + u' ' + w[1] + u' ' + w[2]) if len(w) > 2 else m.string]),
    (u'裸数(括号注)', re.compile(u'^\\d[\\d,]* \\('), lambda m, w: [w[0]]),
    (u'裸数', re.compile(u'^\\d[\\d,]*(?:\\.\\d+)?[.,]?(?=\\s|$)'), lambda m, w: [m.group(0).strip(u'.,')]),
]


def slot_shape(s):
    s = s.strip()
    w = s.split()
    for kind, rx, gk in RULES:                  # 表驱动一条链, 首条命中即返(采集遍是五条 if 各配一条正则)
        if kind == u'裸数':
            m = rx.match(w[0]) if w else None
        else:
            m = rx.match(s)
        if m:
            return kind, gk(m, w)
    if w and w[0].strip(u'.,').upper() in (u'TRUE', u'FALSE'):
        return u'布尔字', [w[0].strip(u'.,')]
    if w and w[0].strip(u'.,').lower() in (u'unset', u'none', u'enabled', u'disabled', u'ipv4', u'ipv6'):
        return u'开关/交回字', [w[0].strip(u'.,')]
    return u'散文/交回', [w[0] if w else s]


DSLOT = {}
for i in range(NSRC):
    rowsx, seen2 = [], set()
    for mk in MARKS:
        for m in re.finditer(re.escape(mk) + u'[ \\t]+([^\\n]{0,70})', FOC[i]):
            slot = m.group(1).strip()
            sh, toks = (u'无值位', [u'-']) if mk in NOVAL else slot_shape(slot)
            key = (mk, slot)
            if key in seen2:
                continue
            seen2.add(key)
            rowsx.append([mk, sh, toks, slot])
    DSLOT[LBL[i]] = rowsx
F['default_slots'] = DSLOT
F['default_slot_kinds'] = dict((k, sorted(set(z[1] for z in v))) for k, v in DSLOT.items())
F['default_slot_n'] = dict((k, len(v)) for k, v in DSLOT.items())
F['default_slot_all'] = sum(F['default_slot_n'].values())
print(u'8 默认句式 %s' % F['shape_lbls'])
for i in range(NSRC):
    print(u'   %-7s %s ⇎ 位上形状 %d 种 %s' % (LBL[i], F['shape_n'][i], len(F['default_slot_kinds'][LBL[i]]),
                                             F['default_slot_kinds'][LBL[i]]))

# ---------- 8b. sysctl 键块 ⇎ 相关键默认值 ----------
DK = {}
_cur = [None]
for x in L[3]:
    if keylin(x):
        _cur[0] = x.split(u' - ')[0]
        DK[_cur[0]] = []
    elif _cur[0] is not None:
        DK[_cur[0]].append(x)
F['sysctl_keys'] = len(DK)
F['sysctl_key_types'] = dict((x.split(u' - ')[0], x.split(u' - ')[1].strip()) for x in L[3] if keylin(x))
REL = sorted([k for k in DK if u'dad' in k or u'_solicit' in k or k.startswith(u'router_solicitation')
              or k == u'retrans_time'])
F['sysctl_rel_keys'] = REL
F['sysctl_rel_body'] = dict((k, re.sub(u'\\s+', u' ', u' '.join(DK[k])).strip()) for k in REL)
F['sysctl_rel_nlines'] = dict((k, len(DK[k])) for k in REL)


def tok(s):
    m = re.match(u'([^ .;,)]+)', s)
    return m.group(1) if m else s


DEF = {}
for k in REL:
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
F['sysctl_defaults'] = dict((k, [re.sub(u'[.,;]$', u'', v[0]) if v[0] else None, v[1]]) for k, v in DEF.items())
F['sysctl_rel_num'] = len([k for k in REL if (F['sysctl_defaults'][k][0] or u'').isdigit()])
F['sysctl_rel_noval'] = len([k for k in REL if F['sysctl_defaults'][k][0] is None])
print(u'8b sysctl 键 %d 块 ⇎ 相关键 %d 枚 ⇎ 默认位是数 %d ⇎ 一个也不给 %d'
      % (F['sysctl_keys'], len(REL), F['sysctl_rel_num'], F['sysctl_rel_noval']))

# ---------- 9. 引用边 ----------
RXN_SP = re.compile(u'RFC (\\d{4})')
RXN_NS = re.compile(u'RFC(\\d{4})')
F['ref_spaced'] = [sorted(set(RXN_SP.findall(T[i]))) for i in range(NSRC)]
F['ref_glued'] = [sorted(set(RXN_NS.findall(T[i]))) for i in range(NSRC)]
F['ref_n'] = [[len(RXN_SP.findall(T[i])), len(RXN_NS.findall(T[i]))] for i in range(NSRC)]
F['ref_only_glued'] = [sorted(set(F['ref_glued'][i]) - set(F['ref_spaced'][i])) for i in range(NSRC)]
print(u'9 引用: 带空格去重 %s ⇎ 粘连去重 %s ⇎ 只粘连 %s'
      % ([len(z) for z in F['ref_spaced']], [len(z) for z in F['ref_glued']], F['ref_only_glued']))

# ---------- 10-11. 段窗定界 ⇎ 窗内普查 ----------
IDX = dict((LBL[i], i) for i in range(NSRC))
VARRE = re.compile(u'\\b(MAX_[A-Z_]+|MIN_[A-Z_]+|RETRANS_TIMER|REACHABLE_TIME|RTR_[A-Z_0-9]+'
                   u'|DELAY_FIRST_PROBE_TIME|DupAddrDetectTransmits|RetransTimer)\\b')


def secnum(x):
    m = re.match(u'^(\\d+(?:\\.\\d+)*\\.?)\\s\\s+(?=[A-Z])', x.lstrip())
    return m.group(1) if m else None


def toc_line(x):
    return re.search(u'\\.\\s+\\.\\s+\\d+\\s*$', x) is not None


def window(i, a, kind):
    """同一段窗, 五种定界谓词各一条生成器: 取第一个满足停止谓词的行号(采集遍是 while 游标)。"""
    n = len(L[i])
    if kind == u'sec':
        p0 = secnum(L[i][a])
        return next((b for b in range(a + 1, n + 1)
                     if b == n or (secnum(L[i][b]) is not None and not secnum(L[i][b]).startswith(p0))), n)
    if kind == u'para':
        return next((b for b in range(a + 1, n + 1)
                     if b == n or blankish(L[i][b]) or L[i][b].strip() == u'\x0c'), n)
    if kind == u'label':
        return next((b for b in range(a + 1, n + 1)
                     if b == n or re.match(u'^[A-Za-z ]+constants:$', L[i][b].strip())
                     or secnum(L[i][b]) is not None), n)
    if kind == u'key':
        return next((b for b in range(a + 1, n + 1) if b == n or keylin(L[i][b])), n)
    return next((b for b in range(a + 1, n + 1) if b == n or optlin(L[i][b])), n)


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
F['win_heads'] = W
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
    txt = NL.join(L[i][a:b])
    cln = NL.join([x for x in L[i][a:b] if not is_shell(x, i)])
    nu = sorted(set(RX_STRICT.findall(txt)))
    nuc = sorted(set(RX_STRICT.findall(cln)))
    var = sorted(set(VARRE.findall(txt)))
    varc = sorted(set(VARRE.findall(cln)))
    dig = sorted(set(re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', txt)))
    digc = sorted(set(re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', cln)))
    shn = len([1 for x in L[i][a:b] if is_shell(x, i)])
    CW.append([tag, kind, head, a + 1, b, len(nu), len(var), len(dig), nu, var, dig,
               len(nuc), len(varc), len(digc), nuc, varc, digc, shn])
F['win_census'] = CW
F['win_numless_with_var'] = [[z[0], z[1], z[2]] for z in CW if z[5] == 0 and z[6] > 0]
F['win_var_kinds'] = sorted(set(v for z in CW for v in z[9]))
F['win_shell_lines'] = [[z[0], z[2], z[17]] for z in CW if z[17] > 0]
F['win_n'] = len(CW)
F['win_kinds'] = sorted(set(z[1] for z in CW))
F['win_strict_eaten'] = sum(z[5] - z[11] for z in CW)
F['win_dig_eaten'] = sum(len(z[10]) - len(z[15]) for z in CW)
print(u'11 段窗 %d 个(定界谓词 %s): 严轨窗内 %d ⇎ 摘壳后 %d ⇎ 只变量无数字的窗 %d 个'
      % (F['win_n'], F['win_kinds'], sum(z[5] for z in CW), sum(z[11] for z in CW),
         len(F['win_numless_with_var'])))

# ---------- 12. 4861 §10 常量表 ----------
CTRX = re.compile(u'^\\s*([A-Z][A-Z_0-9]+)\\s+(\\d[\\d,]*(?:\\.\\d+)?|\\.\\d+)'
                  u'( (milliseconds|millisecond|seconds|second|transmissions))?\\s*$')
ca = find_body(1, u"10.  Protocol Constants")
cb = window(1, ca, u'sec')
CT = [[m.group(1), m.group(2), m.group(4) if m.group(4) else u'无量纲', a + 1]
      for a, m in ((a, CTRX.match(L[1][a])) for a in range(ca, cb)) if m]
CTF = [[m.group(1), m.group(2), m.group(4) if m.group(4) else u'无量纲', a + 1]
       for a, m in ((a, CTRX.match(L[1][a])) for a in range(len(L[1]))) if m]
F['const_rows'] = CT
F['const_rows_doc'] = CTF
INW = set([tuple(z[:3]) for z in CT])
F['const_unit_kinds'] = sorted(set(z[2] for z in CT))
F['const_comma_rows'] = [z[0] for z in CT if u',' in z[1]]
F['const_dot_rows'] = [z[0] for z in CT if z[1].startswith(u'.')]
F['const_out_of_win'] = [[z[0], z[1], z[3]] for z in CTF if tuple(z[:3]) not in INW]
F['const_n_ms'] = len([z for z in CT if z[2].startswith(u'milli')])
F['const_n_tr'] = len([z for z in CT if z[2] == u'transmissions'])
F['const_n_sec'] = len([z for z in CT if z[2].startswith(u'second')])
F['const_n_dim'] = len([z for z in CT if z[2] == u'无量纲'])
F['const_retrans'] = [z for z in CT if z[0] == u'RETRANS_TIMER']
F['const_dad'] = [z[0] for z in CT if u'DUP' in z[0] or u'ADDR' in z[0]]
print(u'12 §10 窗内常量行 %d ⇎ 全篇 %d ⇎ 窗外出身 %s ⇎ 毫秒 %d/秒 %d/次数 %d/无量纲 %d'
      % (len(CT), len(CTF), F['const_out_of_win'], F['const_n_ms'], F['const_n_sec'],
         F['const_n_tr'], F['const_n_dim']))

# --- PICK BEGIN --- (与采集遍逐键对账: 同一把定义, 第二套实现)
PK = json.load(io.open(u'corpus/_b93meas.json', encoding='utf-8'))
PAIRK = [
    (u'bytes', u'bytes'), (u'cp', u'cp'), (u'n_lf', u'n_lf'), (u'n_cr', u'n_cr'),
    (u'splitlines', u'splitlines'), (u'splitnl', u'splitnl'), (u'readlines', u'readlines'),
    (u'ff', u'ff'), (u'ff_led', u'ff_led'), (u'ff_before_nl', u'ff_before_nl'),
    (u'trailing_nl', u'trailing_nl'), (u'ff_at_eof', u'ff_at_eof'),
    (u'blank', u'blank'), (u'nonblank', u'nonblank'), (u'maxlen', u'maxlen'), (u'tab', u'tab'),
    (u'tab_led', u'tab_led'), (u'bom', u'bom'), (u'utf8_extra', u'utf8_extra'),
    (u'nonascii', u'nonascii'), (u'na_total', u'na_total'), (u'row_ledger', u'row_ledger'),
    (u'read_vs_split', u'read_vs_split'),
    (u'foot_page', u'foot_page'), (u'hdr_old', u'hdr_old'), (u'hdr_title', u'hdr_title'),
    (u'ietf_alone', u'ietf_alone'), (u'key_lines', u'key_lines'), (u'opt_lines', u'opt_lines'),
    (u'added_lines', u'added_lines'), (u'pgnum', u'pgnum'), (u'shell_lines', u'shell_lines'),
    (u'body_lines', u'body_lines'),
    (u'html_bytes', u'html_bytes'), (u'html_cp', u'html_cp'), (u'html_lines', u'html_lines'),
    (u'html_lf', u'html_lf'), (u'tag_n', u'tag_n'), (u'tag_chars', u'tag_chars'),
    (u'ent_n', u'ent_n'), (u'stripped_cp', u'stripped_cp'),
    (u'html_minus_stripped', u'html_minus_stripped'),
    (u'ob_line', u'ob_line'), (u'ob_fold', u'ob_fold'), (u'ob_wrap', u'ob_wrap'),
    (u'kw_all', u'kw_all'), (u'kw_caps', u'kw_caps'), (u'kw_low_only', u'kw_low_only'),
    (u'dbl_space', u'dbl_space'), (u'dbl_space_eaten', u'dbl_space_eaten'),
    (u'dehyphen_chars', u'dehyphen_chars'), (u'dehyphen_edits', u'dehyphen_edits'),
    (u'needles4', u'needles4'), (u'needle_src', u'needle_src'),
    (u'needle_src_dehy', u'needle_src_dehy'), (u'needle_wrap_kinds', u'needle_wrap_kinds'),
    (u'needle_dehy_kinds', u'needle_dehy_kinds'), (u'pin_lines', u'pin_lines'),
    (u'numunit_strict', u'numunit_strict'), (u'numunit_loose', u'numunit_loose'),
    (u'strict_n', u'strict_n'), (u'loose_n', u'loose_n'), (u'loose_short_n', u'loose_short_n'),
    (u'loose_all_short', u'loose_all_short'), (u'comma_nums', u'comma_nums'),
    (u'dotfrac_nums', u'dotfrac_nums'), (u'dotlead_unit', u'dotlead_unit'),
    (u'range_nums', u'range_nums'), (u'percent', u'percent'), (u'fraction', u'fraction'),
    (u'glued_unit', u'glued_unit'), (u'spaced_unit', u'spaced_unit'), (u'hex_default', u'hex_default'),
    (u'dig_all', u'dig_all'), (u'dig_ipv_noise', u'dig_ipv_noise'),
    (u'unit_in_keyname', u'unit_in_keyname'),
    (u'dual_unit_lines', u'dual_unit_lines'), (u'dual_prove', u'dual_prove'),
    (u'dual_gloss_forms', u'dual_gloss_forms'), (u'dual_plural_at_one', u'dual_plural_at_one'),
    (u'dual_implicit_lines', u'dual_implicit_lines'), (u'unit_conv', u'unit_conv'),
    (u'conv_glued_n', u'conv_glued_n'), (u'conv_spaced_n', u'conv_spaced_n'),
    (u'conv_same', u'conv_same'),
    (u'name_raw', u'name_raw'), (u'name_ci', u'name_ci'), (u'name_norm', u'name_norm'),
    (u'name_absent', u'name_absent'),
    (u'shape_lbls', u'shape_lbls'), (u'shape_n', u'shape_n'),
    (u'default_val_is_num', u'default_val_is_num'), (u'default_gloss', u'default_gloss'),
    (u'default_slots', u'default_slots'), (u'default_slot_kinds', u'default_slot_kinds'),
    (u'default_slot_n', u'default_slot_n'),
    (u'sysctl_keys', u'sysctl_keys'), (u'sysctl_key_types', u'sysctl_key_types'),
    (u'sysctl_rel_keys', u'sysctl_rel_keys'), (u'sysctl_rel_body', u'sysctl_rel_body'),
    (u'sysctl_rel_nlines', u'sysctl_rel_nlines'), (u'sysctl_defaults', u'sysctl_defaults'),
    (u'ref_spaced', u'ref_spaced'), (u'ref_glued', u'ref_glued'), (u'ref_n', u'ref_n'),
    (u'win_heads', u'win_heads'), (u'win_census', u'win_census'),
    (u'win_numless_with_var', u'win_numless_with_var'), (u'win_var_kinds', u'win_var_kinds'),
    (u'win_shell_lines', u'win_shell_lines'),
    (u'const_rows', u'const_rows'), (u'const_rows_doc', u'const_rows_doc'),
    (u'const_unit_kinds', u'const_unit_kinds'), (u'const_comma_rows', u'const_comma_rows'),
    (u'const_dot_rows', u'const_dot_rows'), (u'const_out_of_win', u'const_out_of_win'),
]
AGREE, DIFFK = [], []
for mk_k, pk_k in PAIRK:
    if mk_k not in F or pk_k not in PK:
        DIFFK.append(mk_k + u'?' + pk_k)
        continue
    a, b = F[mk_k], PK[pk_k]
    if mk_k == u'needles4':
        a = [[[y for y in t] for t in r] for r in a]
    # 两遍各自在内存里持元组, 采集遍经 JSON 落盘只剩表: 按落盘后的形状比, 不比容器型
    a = json.loads(json.dumps(a, ensure_ascii=False))
    (AGREE if a == b else DIFFK).append(mk_k)
F['pick_agree'] = len(AGREE)
F['pick_diff'] = len(DIFFK)
F['pick_diffk'] = sorted(DIFFK)
F['pick_pairs'] = len(PAIRK)
print(u'PICK 对账: %d 键符 ⇎ %d 键不符 %s' % (F['pick_agree'], F['pick_diff'], sorted(DIFFK)[:12]))
def dw(a, b, pre=u''):
    if type(a) is not type(b):
        print(u'   %s 型不符 %s ⇎ %s' % (pre, type(a), type(b)))
        return
    if isinstance(a, dict):
        for k in sorted(set(list(a.keys()) + list(b.keys()))):
            if a.get(k) != b.get(k):
                dw(a.get(k), b.get(k), pre + u'[' + u'%s' % (k,) + u']')
    elif isinstance(a, list):
        if len(a) != len(b):
            print(u'   %s 长度不符 %d ⇎ %d' % (pre, len(a), len(b)))
        for j in range(min(len(a), len(b))):
            if a[j] != b[j]:
                dw(a[j], b[j], pre + u'/' + u'%d' % (j,))
    else:
        print(u'   %s 本遍 %s ⇎ 采集 %s' % (pre, repr(a)[:200], repr(b)[:200]))


if DIFFK:
    for k in sorted(DIFFK)[:6]:
        pk = k.split(u'?')[0]
        if pk in F and pk in PK:
            dw(F[pk], PK[pk], pk)
# --- PICK END ---

# ---------- 布尔门(每道都能失败) ----------
G = []
G.append((u'字节两把尺同值(面内长度 ⇎ 文件系统大小)', F['bytes'] == F['bytes_stat']))
G.append((u'最长行两把尺同值(切片求长 ⇎ 逐字符计长)', F['maxlen'] == F['maxlen_scan']))
G.append((u'折平两路逐份同面(re.sub ⇎ split/join)', sum(F['fold_eq']) == NSRC))
G.append((u'空行+非空行回总行', all([F['row_ledger'][i] == 0 for i in range(NSRC)])))
G.append((u'splitlines 与 split(换行) 之差 = 换页后随换行−尾换行',
          all([F['lines_ruler_diff'][i] == 0 for i in range(NSRC)])))
G.append((u'readlines 加尾换行回总行', all([F['read_vs_split'][i] == 0 for i in range(NSRC)])))
G.append((u'壳账容斥逐份归零', all([F['shell_led'][i] == 0 for i in range(NSRC)])))
G.append((u'壳行加正文行回总行', all([F['shell_lines'][i] + F['body_lines'][i] == F['splitnl'][i]
                                     for i in range(NSRC)])))
G.append((u'非换行的其他界符一枚也没有(只有换页符)',
          [F['othsep'][i] == F['ff'][i] for i in range(NSRC)]))
G.append((u'前四份面纯 ASCII(UTF-8 涨字节只在网页那一份)', sum([F['utf8_extra'][i] for i in range(4)]) == 0))
G.append((u'盘上剥壳面 ≠ 本遍自剥面(序列化不等)', F['disk_vs_own'] != 0))
G.append((u'重叠尺与不重叠尺对义务词同数', sum([abs(x) for x in F['ob_ruler_diff']]) == 0))
G.append((u'去连字改一处少一字符(空格)⇎ 次数与字符数同',
          F['dehyphen_chars'] == F['dehyphen_edits']))
G.append((u'面内自证双单位行非空且全自证', len(F['dual_prove']) > 0 and all(F['dual_prove'])))
G.append((u'隐式外单位行非空且全自证', len(F['dual_implicit_lines']) > 0
          and all([z[6] for z in F['dual_implicit_lines']])))
G.append((u'同一张 §10 表里四种单位口径并排', F['const_n_ms'] > 0 and F['const_n_sec'] > 0
          and F['const_n_tr'] > 0 and F['const_n_dim'] > 0))
G.append((u'§10 表每行的值折算为正数', all([numv(z[1]) > 0 for z in F['const_rows']])))
G.append((u'RETRANS_TIMER 只在 §10 表里印成数', len(F['const_retrans']) == 1
          and F['const_retrans'][0][2] == u'milliseconds'))
G.append((u'4862 全篇没有一处 数字×时长单位(严轨)', sum([len(z) for z in F['numunit_strict'][0]]) == 0))
G.append((u'4429 同样一处也不给', F['strict_n'][2] == 0))
G.append((u'sysd 一份通篇无义务词', sum(F['ob_fold'][4]) == 0 and sum(F['ob_line'][4]) == 0))
G.append((u'4862 提 RetransTimer 而不印常量名 RETRANS_TIMER',
          F['name_raw'][0][NAMES.index(u'RetransTimer')] > 0
          and F['name_raw'][0][NAMES.index(u'RETRANS_TIMER')] == 0))
G.append((u'use_dad ⇎ retrans_time ⇎ RetryCount 五份零枚', len(F['name_absent']) == 3
          and sorted(F['name_absent']) == [u'RetryCount', u'retrans_time', u'use_dad']))
G.append((u'去连字档独读的针存在', F['needle_dehy_kinds'] > 0))
G.append((u'被硬换行劈开的针存在', F['needle_wrap_kinds'] > 0))
G.append((u'有窗只印变量不印数字×单位', len(F['win_numless_with_var']) > 0))
G.append((u'窗内严轨数与去重表长同路', sum([abs(z[5] - len(z[8])) + abs(z[6] - len(z[9]))
                                            + abs(z[7] - len(z[10])) for z in F['win_census']]) == 0))
G.append((u'sysctl 相关键十枚', len(F['sysctl_rel_keys']) == 10))
G.append((u'dad_transmits 的默认位在两档里都是 1(数 ⇎ 布尔字)',
          F['sysctl_defaults'][u'dad_transmits'][0] == u'1'))
G.append((u'sysd 的 IPv6 选项行不填数而 IPv4 选项行填数',
          F['opt_lines'][4] > 0 and F['cp'][4] > 0
          and len([z for z in F['numunit_strict'][4] if z[1] == u'milliseconds']) > 0))
G.append((u'与采集遍逐键全符', F['pick_diff'] == 0 and F['pick_agree'] == F['pick_pairs']))
F['bool_all_n'] = len(G)
F['bool_green'] = len([x for x in G if x[1]])
F['bool_red'] = [x[0] for x in G if not x[1]]
F['gate_keys'] = len(G)
print(u'布尔门 %d 道 ⇎ 红 %s' % (len(G), F['bool_red']))
for nm, ok in G:
    if not ok:
        print(u'   红: %s' % nm)

# ---------- 恒等式(逐条现算必须归零) ----------
ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"sum(F['row_ledger'])", u'行账: 空行 + 非空行 − 总行, 逐份相减')
Z(u"sum([F['splitlines'][i] - F['splitnl'][i] - (F['ff_before_nl'][i] - F['trailing_nl'][i]) for i in range(5)])",
  u'两把行尺之差 = 换页后随换行 − 尾换行(逐份)')
Z(u"sum(F['read_vs_split'])", u'readlines + 尾换行 − 总行')
Z(u"sum(F['shell_led'])", u'壳账容斥: 六形之和 − 重数 − 壳行')
Z(u"sum([F['shell_lines'][i] + F['body_lines'][i] - F['splitnl'][i] for i in range(5)])",
  u'壳行 + 正文行 = 总行')
Z(u"sum(F['utf8_extra']) - sum([F['bytes'][i] - F['cp'][i] for i in range(5)])",
  u'字节 − 码位 = UTF-8 涨字节')
Z(u"F['html_cp'] - F['tag_chars'] - F['own_detag_cp']", u'HTML 码位 − 标签吃掉的 = 本遍自剥面')
Z(u"F['html_cp'] - F['cp'][4] - F['html_minus_stripped']", u'原文 − 盘上剥壳面 = 差')
Z(u"sum([F['nonblank'][i] - (F['splitnl'][i] - F['blank'][i]) for i in range(5)])",
  u'非空行两路(逐行判空 ⇎ 总数减空行)')
Z(u"sum(F['ob_wrap']) - (sum([sum(x) for x in F['ob_fold']]) - sum([sum(x) for x in F['ob_line']]))",
  u'义务词跨行涨量 = 两档总量之差')
Z(u"sum(F['kw_low_only']) - (sum(F['kw_all']) - sum(F['kw_caps']))", u'只小写 = 大小写不分 − 全大写')
Z(u"sum(F['dehyphen_chars']) - sum(F['dehyphen_edits'])",
  u'去连字吃掉的字符数 = 改动次数(一次改动吃一枚空格)')
Z(u"len(F['name_absent']) - len([k for k in range(F['name_n']) "
  u"if sum([F['name_raw'][i][k] for i in range(5)]) == 0])",
  u'一枚也不出的名: 清单路 ⇎ 名族矩阵路')
Z(u"F['needle_n'] - len(F['needles4'])", u'针数 ⇎ 四档表行数两路各自数出')
Z(u"sum([len(x) for x in F['needle_src']]) - len([1 for k in range(F['needle_n']) for i in range(5) "
  u"if F['needles4'][k][i][2] > 0])", u'摘壳档归属表长 = 非零格数')
Z(u"sum([len(x) for x in F['needle_src_dehy']]) - len([1 for k in range(F['needle_n']) for i in range(5) "
  u"if F['needles4'][k][i][3] > 0])", u'去连字档归属表长 = 非零格数')
Z(u"len(F['pin_lines']) - (len([1 for x in F['pin_lines'] if x[3] == 1]) + F['pin_dh2'])",
  u'锚行条目两档之和 = 条目数')
Z(u"F['conv_glued_n'] + F['conv_spaced_n'] - len(F['unit_conv'])", u'换算两组相加回总数')
Z(u"len(F['dual_prove']) - len(F['dual_unit_lines'])", u'自证布尔表 ⇎ 双单位行数同路')
Z(u"sum(F['default_slot_n'].values()) - len([z for k in F['default_slots'] for z in F['default_slots'][k]])",
  u'默认值位条数两路各自数出')
Z(u"F['needle_wrap_kinds'] - len([1 for k in range(F['needle_n']) "
  u"if any([F['needles4'][k][i][1] > 0 and F['needles4'][k][i][0] == 0 for i in range(5)])])",
  u'被硬换行劈开的针种数: 汇总路 ⇎ 逐枚现筛路')
Z(u"F['sysctl_keys'] - len(F['sysctl_key_types'])", u'键块数: 游标建行 ⇎ 逐行筛键')
Z(u"sum([z[5] for z in F['win_census']]) - sum([len(z[8]) for z in F['win_census']])",
  u'窗内严轨: 计数路 ⇎ 去重表路')
Z(u"F['win_strict_eaten'] + sum([z[11] for z in F['win_census']]) - sum([z[5] for z in F['win_census']])",
  u'摘壳吃掉的严轨枚数 + 摘壳后 = 摘壳前')
Z(u"len(F['const_rows_doc']) - len(F['const_rows']) - len(F['const_out_of_win'])",
  u'常量表: 全篇 = 窗内 + 窗外')
Z(u"F['const_n_ms'] + F['const_n_sec'] + F['const_n_tr'] + F['const_n_dim'] - len(F['const_rows'])",
  u'四种口径逐行相加回表行数')
Z(u"F['pick_pairs'] - F['pick_agree'] - F['pick_diff']", u'对账: 键对 = 符 + 不符')
Z(u"F['bool_green'] - F['bool_all_n']", u'布尔门全绿')
for e, w in ZID:
    v = eval(e, {u'F': F, u'range': range, u'sum': sum, u'len': len, u'max': max, u'abs': abs})
    if v != 0:
        print(u'ZID 不平: %s ⇒ %s' % (w, v))
        raise SystemExit(1)
print(u'恒等式 %d 条全平' % len(ZID))
F['zid_scan_n'] = len(ZID)
F['scan_key_n'] = len(F)
# --- SCAN END --- (以上由 _wire93.py 机械切进 _b93_scan; 以下为建条目侧登记与发射)

BB93 = lambda name, i=None: (F[name] if i is None else F[name][i])


def _ev(e):
    return eval(e, {u'B93V': BB93, u'NSRC': NSRC, u'range': range, u'F': F, u'len': len, u'sum': sum})


FN = u'B93V'
_to_v = re.compile(r"(?:F)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B93V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(5)').replace(u'NSRC', u'5')


K_, ZERO, COLL, SEENX = {}, [], {}, {}


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K_:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K_.setdefault(s, (expr, note))
    return


def V(name, i=None, note=u''):
    if name not in F:
        raise AssertionError(u'无此键 ' + name)
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def J(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LBL[i])) for i in range(NSRC))


def JL(name, note=u''):
    return V(name, None, note) if isinstance(F[name], (list, dict)) else J(name, note)


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


ZV = []
for e, w in ZID:
    v = to_v(e.replace(u'\n', u''))
    if eval(v, {FN: BB93, u'range': range, u'sum': sum, u'len': len, u'max': max, u'abs': abs}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))
    reg(str(_ev(e)), v, w)


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB93}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([str(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


for k, v in dump_deriv().items():
    DER[k] = v

PK[u'pick_agree'] = F['pick_agree']
PK[u'pick_diff'] = F['pick_diff']
PK[u'pick_diffk'] = F['pick_diffk']
PK[u'pick_pairs'] = F['pick_pairs']
PK[u'pick_from'] = u'corpus/_mkB93.py'
json.dump(PK, io.open(u'corpus/_b93meas.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)

print(u'第二遍量测完成: 扁平键 %d ⇎ 恒等式 %d 全平 ⇎ 布尔门 %d 全绿 ⇎ 针 %d ⇎ 对账 %d 符 %d 不符 ⇎ 已写回 _b93meas.json'
      % (len(F), len(ZID), F['bool_all_n'], F['needle_n'], F['pick_agree'], F['pick_diff']))
io.open(u'corpus/_b93flat.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True))

exec(io.open(u'corpus/_mk93emit.py', encoding='utf-8').read())