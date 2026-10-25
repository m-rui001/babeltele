# -*- coding: utf-8 -*-
"""采集遍(B93, 第一套实现): “IPv6 重复地址检测到底试几次、每次隔多久”由五份一手文书各答一遍.

4862(SLAAC 规范: 把次数写成变量 DupAddrDetectTransmits 并给 “Default: 1”, 把间隔整个交回 4861 的 RetransTimer,
本文一个毫秒数也不赋) ⇎ 4861(邻居发现: 只有它把常量印成数——RETRANS_TIMER 1,000 milliseconds ⇎
DELAY_FIRST_PROBE_TIME 5 seconds ⇎ MAX_MULTICAST_SOLICIT 3 transmissions, 同一张表里秒 ⇎ 毫秒 ⇎ 次数三种口径并排)
⇎ 4429(Optimistic DAD: 主张 “remove the RetransTimer delay”, 并把漏检概率的解法写成把次数加到大于 1)
⇎ ip-sysctl.txt(Linux 内核文档: dad_transmits “Default: 1” ⇎ accept_dad 的 “1: Enable DAD (default)” ⇎
optimistic_dad/enhanced_dad; 这份里没有 use_dad, 也没有 retrans_time——缺登记的谓词只能进解读注)
⇎ systemd_network5(发行版组件文档: IPv6DuplicateAddressDetection= 不填数(交回内核), IPv4 侧反而给数:
“defaults to 200 milliseconds” 且同一行印 “between 1 millisecond and 60 seconds” 两种单位).

采集遍的实现口径(建条侧要在同一把定义上换成另一套算法):
①切行 = split(NL) 后逐行手工剥 \\r; ②折平 = ' '.join(lower().split()); ③找针 = 游标 find 环(非重叠);
④整词尺 = 命中位置读左右邻的 isalpha/isdigit 表; ⑤页壳 = 整行序列正则逐路判; ⑥切句 = (?<=[.!?]) + 的正则;
⑦默认值 = 每种句式各一条正则; ⑧行号 = 4 行滑窗 + 折平区间表取满足起点的最后一段; ⑨去连字 = 一条 (\\w)- (\\w) 正则;
⑩单位换算 = 查单位表求商. 所有正文数字由本遍量出后落 JSON, 一枚都不手打。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'4862', u'4861', u'4429', u'sysctl', u'sysd']
SRC = [u'corpus/raw/dad6/rfc4862.txt', u'corpus/raw/dad6/rfc4861.txt', u'corpus/raw/dad6/rfc4429.txt',
       u'corpus/raw/dad6/ip-sysctl.txt', u'corpus/raw/dad6/systemd_network5.txt']
HTML = u'corpus/raw/dad6/systemd_network5.html'
NSRC = 5
M = {}


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in SRC]
T = [b.decode('utf-8', 'replace') for b in B]
RAWL = [t.split(NL) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]
HB = rd(HTML)
HT = HB.decode('utf-8', 'replace')


def pnorm(s):
    return u' '.join(s.lower().split())


def cnt_cur(hay, nd):
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def ub(s, w, kind=u'alpha'):
    """词界尺: 两侧都不是字母(alpha) ⇎ 都不是数字(digit) ⇎ 都不是字母数字(alnum)。"""
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if kind == u'alpha':
            ok = not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha())
        elif kind == u'digit':
            ok = not (a >= 0 and s[a].isdigit()) and not (b < len(s) and s[b].isdigit())
        else:
            ok = not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())
        if ok:
            c += 1
        i = j + 1


def foldmap(txt):
    """折平面 + (面偏移 → 原行) 区间表: 只数非空格字符, 段间一枚空格。"""
    lines = txt.split(NL)
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


def line_of_face(offs, s0):
    cand = [o[2] for o in offs if o[0] <= s0]
    return cand[-1] if cand else None


def find_line(i, nd, dehy=False):
    """折平 needle → needle 首字符所在原行(0-based): 4 行滑窗在折平面上试.
    dehy=True 时先在折平面上做去连字(只用于跨连字断行的针)."""
    q = pnorm(nd)
    head = q[:min(16, len(q))]
    for a in range(len(L[i])):
        win = NL.join(L[i][a:a + 4])
        if head not in pnorm(win):
            continue
        face, offs = foldmap(win)
        if dehy:
            face = RX_DH.sub(u'\\1-\\2', face)
        s0 = face.find(q)
        if s0 >= 0:
            return a + line_of_face(offs, s0)
    return -1


def digit_runs(x):
    n, prev = 0, False
    for c in x:
        cur = c.isdigit()
        if cur and not prev:
            n += 1
        prev = cur
    return n


# ---------- 0. 面量 ⇎ 行式 ⇎ 换页账 ----------
M['bytes'] = [len(B[i]) for i in range(NSRC)]
M['cp'] = [len(T[i]) for i in range(NSRC)]
M['n_lf'] = [cnt_cur(T[i], NL) for i in range(NSRC)]
M['n_cr'] = [cnt_cur(T[i], u'\r') for i in range(NSRC)]
M['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
M['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
M['readlines'] = [len([1 for _ in io.StringIO(T[i], newline=NL)]) for i in range(NSRC)]
M['ff'] = [cnt_cur(T[i], u'\x0c') for i in range(NSRC)]
M['ff_led'] = [len([x for x in L[i] if len(x) and ord(x[0]) == 12]) for i in range(NSRC)]
M['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
M['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
M['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
M['tab'] = [cnt_cur(T[i], u'\t') for i in range(NSRC)]
M['nonascii'] = [sorted(set([ord(c) for c in T[i] if ord(c) > 127])) for i in range(NSRC)]
M['na_total'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(NSRC)]
M['bom'] = [1 if T[i][:1] and ord(T[i][0]) == 65279 else 0 for i in range(NSRC)]
M['utf8_extra'] = [M['bytes'][i] - M['cp'][i] for i in range(NSRC)]
print(u'0 面量:', json.dumps(dict((k, M[k]) for k in
      ['bytes', 'cp', 'n_lf', 'n_cr', 'splitlines', 'splitnl', 'readlines', 'ff', 'ff_led',
       'blank', 'nonblank', 'maxlen', 'tab', 'bom', 'utf8_extra'])))
FFNL = [len(re.findall(u'(?=\x0c' + NL + u')', T[i])) for i in range(NSRC)]
FFEOF = [1 if T[i][-1:] == u'\x0c' else 0 for i in range(NSRC)]
TRAILNL = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
M['ff_before_nl'], M['ff_at_eof'], M['trailing_nl'] = FFNL, FFEOF, TRAILNL
OBS = [M['splitlines'][i] - M['splitnl'][i] for i in range(NSRC)]
PRE = [FFNL[i] - TRAILNL[i] for i in range(NSRC)]
print(u'  行式对账 splitlines−split(nl) =', OBS, u' 预测 FF后随换行−尾换行 =', PRE)
assert OBS == PRE, u'行式对账不平'
M['row_ledger'] = [M['blank'][i] + M['nonblank'][i] - M['splitnl'][i] for i in range(NSRC)]
M['read_vs_split'] = [M['readlines'][i] + M['trailing_nl'][i] - M['splitnl'][i] for i in range(NSRC)]

# ---------- 0b. HTML 档: 原文 ⇎ 剥壳正文两字符数 ----------
M['html_bytes'] = len(HB)
M['html_cp'] = len(HT)
M['html_lines'] = len(HT.split(NL))
M['html_lf'] = cnt_cur(HT, NL)
M['tag_n'] = len(re.findall(u'<[^>]+>', HT))
M['tag_chars'] = sum(len(z) for z in re.findall(u'<[^>]+>', HT))
M['ent_n'] = len(re.findall(u'&[A-Za-z#0-9]+;', HT))
M['stripped_cp'] = M['cp'][4]
M['html_minus_stripped'] = M['html_cp'] - M['stripped_cp']
print(u'0b HTML 档: 原文 %d 字节／%d 码位／%d 行 ⇎ 剥壳正文 %d 码位 ⇎ 标签 %d 枚吃 %d 码位 ⇎ 实体 %d 枚 ⇎ 差 %d'
      % (M['html_bytes'], M['html_cp'], M['html_lines'], M['stripped_cp'],
         M['tag_n'], M['tag_chars'], M['ent_n'], M['html_minus_stripped']))

# ---------- 1. 壳形: 三个序列化家族 ----------
def foot(x):
    return re.search(u'\\[Page \\d+\\]', x) is not None


def hdr_old(x):
    """旧式 RFC Editor 眉行: “…, et al.   Standards Track   [Page n]” 或 “… <标题> <月 年>”. """
    return re.match(u'^\\s*([A-Z][a-z\\u2019-]+, et al\\.|[A-Z][a-zA-Z]+ +[A-Za-z ]*?(?:19|20)\\d\\d) +'
                    u'(Standards Track|Informational|Experimental|[A-Z][a-z]+ \\d+)?', x) is not None and foot(x)


def hdr_title(x):
    return re.match(u'^RFC\\d+ +\\S.*((19|20)\\d\\d)\\s*$', x) is not None


def ietf_line(x):
    return re.match(u'^\\s*(Internet Engineering Task Force|Network Working Group)\\s*$', x) is not None


def keylin(x):
    return re.match(u'^[a-z][a-z_0-9]* - (INTEGER|BOOLEAN|STRING|DWORD)\\s*$', x) is not None


def optlin(x):
    return re.match(u'^\\s{4,}[A-Za-z][A-Za-z0-9]*= *$', x) is not None


def addedlin(x):
    return re.match(u'^\\s*Added in version \\d+\\.\\s*$', x) is not None


def ffline(x):
    return x == u'\x0c'


M['foot_page'] = [len([x for x in L[i] if foot(x)]) for i in range(NSRC)]
M['hdr_old'] = [len([x for x in L[i] if hdr_old(x)]) for i in range(NSRC)]
M['hdr_title'] = [len([x for x in L[i] if hdr_title(x)]) for i in range(NSRC)]
M['ietf_alone'] = [len([x for x in L[i] if ietf_line(x)]) for i in range(NSRC)]
M['key_lines'] = [len([x for x in L[i] if keylin(x)]) for i in range(NSRC)]
M['opt_lines'] = [len([x for x in L[i] if optlin(x)]) for i in range(NSRC)]
M['added_lines'] = [len([x for x in L[i] if addedlin(x)]) for i in range(NSRC)]
M['pgnum'] = [len([x for x in L[i] if x.strip() != u''
                  and not [c for c in x if not (c.isdigit() or c.isspace())] and digit_runs(x) == 1])
              for i in range(NSRC)]
M['tab_led'] = [len([x for x in L[i] if x[:1] == u'\t']) for i in range(NSRC)]
print(u'1 壳形: 页脚 [Page n]', M['foot_page'], u' 旧式眉', M['hdr_old'], u' 标题眉', M['hdr_title'],
      u' IETF/NWG 独立行', M['ietf_alone'], u' 键行', M['key_lines'], u' 选项行', M['opt_lines'],
      u' Added 行', M['added_lines'], u' 独立页码行', M['pgnum'], u' 缩进打头行', M['tab_led'])


def is_shell(x, i):
    """壳 = 页脚/眉/换页/空行; sysd 那份另把 “Added in version n.” 版本号尾注算进壳."""
    return (foot(x) or hdr_old(x) or hdr_title(x) or ietf_line(x) or ffline(x) or x.strip() == u''
            or (i == 4 and addedlin(x)))


M['shell_lines'] = [len([1 for x in L[i] if is_shell(x, i)]) for i in range(NSRC)]
M['body_lines'] = [M['splitnl'][i] - M['shell_lines'][i] for i in range(NSRC)]
print(u'  壳行合计:', M['shell_lines'], u' 剥壳正文行:', M['body_lines'])

# ---------- 2. 义务词 ⇎ 大小写两代 ----------
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY', u'MUST NOT be', u'NOT RECOMMENDED']
FL = [pnorm(T[i]) for i in range(NSRC)]
FOC = [u' '.join(T[i].split()) for i in range(NSRC)]      # 保大小写折平: 大写义务词只能在保架面上量
M['ob_line'] = [[sum([ub(x, w) for x in L[i]]) for w in OB] for i in range(NSRC)]
M['ob_fold'] = [[ub(FOC[i], w) for w in OB] for i in range(NSRC)]
M['ob_wrap'] = [M['ob_fold'][i][k] - M['ob_line'][i][k] for i in range(NSRC) for k in range(len(OB))]
LOW = [len(re.findall(u'(?i)\\b(must|should|may)\\b', T[i])) for i in range(NSRC)]
CAP = [len(re.findall(u'\\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY)\\b', T[i])) for i in range(NSRC)]
M['kw_all'], M['kw_caps'], M['kw_low_only'] = LOW, CAP, [LOW[i] - CAP[i] for i in range(NSRC)]
M['dbl_space'] = [len(re.findall(u'(?<=\\S)  +(?=\\S)', T[i])) for i in range(NSRC)]
M['dbl_space_eaten'] = [M['dbl_space'][i] - len(re.findall(u'(?<=\\S)  +(?=\\S)', FOC[i]))
                        for i in range(NSRC)]
print(u'2 义务词 逐行:', M['ob_line'])
print(u'  折平:', M['ob_fold'], u' 跨行涨量:', M['ob_wrap'])
print(u'  整词大小写不分:', LOW, u' 全大写:', CAP, u' 只小写:', M['kw_low_only'])
print(u'  行内双空格:', M['dbl_space'], u' 折平吃掉:', M['dbl_space_eaten'])

# ---------- 3. 判词针四档(逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳去连字折平) ----------
RX_DH = re.compile(u'(\\w)- (\\w)')
SHP = [pnorm(NL.join([x for x in L[i] if not is_shell(x, i)])) for i in range(NSRC)]
SHT = [RX_DH.sub(u'\\1-\\2', SHP[i]) for i in range(NSRC)]
FOL = [pnorm(T[i]) for i in range(NSRC)]
DEH = [RX_DH.sub(u'\\1-\\2', FOL[i]) for i in range(NSRC)]
M['dehyphen_chars'] = [len(SHP[i]) - len(SHT[i]) for i in range(NSRC)]
M['dehyphen_edits'] = [len(re.findall(u'(\\w)- (\\w)', SHP[i])) for i in range(NSRC)]
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
    # 跨连字断行的针: 只有第 4 档(摘壳+去连字)读得出
    u"A host forms a link-local address by appending an interface identifier",
    u"per-interface basis on multicast-capable interfaces",
    u"Discard Duplicate Address Detection-related Neighbor Solicitation",
    u"defined in a separate link-type-specific document",
    u"has the correct link-layer address; otherwise",
    u"until the ON has a non-Optimistic address",
]
print(u'3 判词针四档:')
rows = []
for nd in NEEDLES:
    q = pnorm(nd)
    r = []
    for i in range(NSRC):
        cl = len([x for x in L[i] if q in pnorm(x)])
        cf = cnt_cur(FOL[i], q)
        cs = cnt_cur(SHP[i], q)
        ct = cnt_cur(SHT[i], q)
        r.append((cl, cf, cs, ct))
    rows.append((nd, r))
    print(u'   %-58s %s  摘壳命中=%s 去连字新读=%s' % (
        nd[:58], r, [LBL[i] for i in range(NSRC) if r[i][2] > 0],
        [LBL[i] for i in range(NSRC) if r[i][3] > 0 and r[i][2] == 0]))
M['needles4'] = [[list(z) for z in [r[i] for i in range(NSRC)]] for nd, r in rows]
M['needle_src'] = [[LBL[i] for i in range(NSRC) if r[i][2] > 0] for nd, r in rows]
M['needle_src_dehy'] = [[LBL[i] for i in range(NSRC) if r[i][3] > 0] for nd, r in rows]
M['needle_wrap_kinds'] = len([1 for nd, r in rows if any(r[i][1] > 0 and r[i][0] == 0 for i in range(NSRC))])
M['needle_dehy_kinds'] = len([1 for nd, r in rows
                              if any(r[i][3] > 0 and r[i][2] == 0 for i in range(NSRC))])

# ---------- 4. 关键句行号定位(供锚) ----------
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
            print(u'4 %s L%d%s «%s»' % (LBL[i], a + 1, u'' if dh == 1 else u'(去连字档)', nd[:60]))
M['pin_lines'] = PINL

# ---------- 5. 数值×单位: 严 ⇎ 宽两轨 ⇎ 千分位 ⇎ 前导点 ⇎ 粘连 ----------
RX_STRICT = re.compile(u'(?<![A-Za-z0-9])(\\d[\\d,]*(?:\\.\\d+)?)[ ]?'
                       u'(milliseconds|millisecond|seconds|second|transmissions|probes|messages)(?![A-Za-z])')
RX_LOOSE = re.compile(u'(\\d[\\d,]*(?:\\.\\d+)?)\\.? ?'
                      u'(milliseconds|millisecond|seconds|second|transmissions|probes|messages|ms|sec|s)')
for i in range(NSRC):
    st = sorted(set(RX_STRICT.findall(T[i])))
    lo = sorted(set(RX_LOOSE.findall(FL[i])))
    print(u'5 %s 严轨 %s' % (LBL[i], st))
    print(u'   %s 宽轨 %d 式' % (LBL[i], len(lo)))
M['numunit_strict'] = [[list(z) for z in sorted(set(RX_STRICT.findall(T[i])))] for i in range(NSRC)]
M['numunit_loose'] = [[list(z) for z in sorted(set(RX_LOOSE.findall(FL[i])))] for i in range(NSRC)]
M['loose_n'] = [len(RX_LOOSE.findall(FL[i])) for i in range(NSRC)]
M['strict_n'] = [len(RX_STRICT.findall(T[i])) for i in range(NSRC)]
M['loose_short_n'] = [len([z for z in RX_LOOSE.findall(FL[i])
                           if z[1] in (u'ms', u'sec', u's')]) for i in range(NSRC)]
M['loose_all_short'] = [M['loose_short_n'][i] == M['loose_n'][i] for i in range(NSRC)]
print(u'5 严轨枚数 %s ⇎ 宽轨枚数 %s ⇎ 宽轨里走短单位(ms/sec/s)的 %s ⇎ 全是短单位的 %s'
      % (M['strict_n'], M['loose_n'], M['loose_short_n'], M['loose_all_short']))
M['comma_nums'] = [sorted(set(re.findall(u'(?<![\\d.])(\\d{1,3},\\d{3}(?:,\\d{3})?)', T[i])))
                   for i in range(NSRC)]
M['dotfrac_nums'] = [sorted(set(re.findall(u'(?<![\\d.)])\\.(\\d+)', T[i]))) for i in range(NSRC)]
M['dotlead_unit'] = [[list(z) for z in sorted(set(re.findall(
    u'(?<![\\d])\\.(\\d+)(?: )?(milliseconds|millisecond|seconds|second)(?![A-Za-z])', T[i])))]
    for i in range(NSRC)]
M['range_nums'] = [sorted(set(re.findall(u'(\\d+\\.\\.\\d+|1\\.\\.\\.\\d+)', T[i]))) for i in range(NSRC)]
M['percent'] = [sorted(set(re.findall(u'(\\d+%)', T[i]))) for i in range(NSRC)]
M['fraction'] = [sorted(set(re.findall(u'\\((\\d/\\d)\\)', T[i]))) for i in range(NSRC)]
UNITS = u'(milliseconds|millisecond|seconds|second|transmissions|probes|messages|hours|hour|minutes|minute|days|day)'
M['glued_unit'] = [[list(z) for z in sorted(set(re.findall(u'(?<![A-Za-z0-9])(\\d+)(' + UNITS + u')(?![A-Za-z])', T[i])))]
                   for i in range(NSRC)]
M['spaced_unit'] = [[list(z) for z in sorted(set(re.findall(u'(?<![A-Za-z0-9])(\\d+) (' + UNITS + u')(?![A-Za-z])', T[i])))]
                    for i in range(NSRC)]
M['hex_default'] = [sorted(set(re.findall(u'(?m)^[ \\t]*Default[^\\n]*?(0x[0-9A-Fa-f]+|INT_MAX|UINT_MAX)', T[i])))
                    for i in range(NSRC)]
M['dig_ipv_noise'] = [len(re.findall(u'(?i)(?:ipv|ip)(\\d)', T[i])) for i in range(NSRC)]
M['dig_all'] = [[len(re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', T[i])), M['dig_ipv_noise'][i]] for i in range(NSRC)]
M['unit_in_keyname'] = [sorted(set(re.findall(u'([A-Za-z0-9]*(?:Sec|Millis|Usec|Ms))[ =]', T[i]))) for i in range(NSRC)]
print(u'  千分位:', M['comma_nums'], u' 前导点小数:', M['dotfrac_nums'])
print(u'  区间:', M['range_nums'], u' 百分数:', M['percent'], u' 分数:', M['fraction'])
print(u'  粘连单位(数字紧跟单位词):', M['glued_unit'])
print(u'  前导点小数×单位:', M['dotlead_unit'])
print(u'  带空格单位:', [[len(z) for z in M['spaced_unit'][i]] for i in range(NSRC)])
print(u'  单位写进键名:', M['unit_in_keyname'])
print(u'  十六进制默认值:', M['hex_default'])
print(u'  数字普查: 总枚数 %s 其中 IPv4/IPv6 里的版本号数字 %s' % (M['dig_all'], M['dig_ipv_noise']))

# ---------- 6. 单位换算: 面内自证的双单位行 ⇎ 跨份等值对 ----------
UNIT = {u'ns': 0.000001, u'nanoseconds': 0.000001, u'millisecond': 1.0, u'milliseconds': 1.0, u'ms': 1.0,
        u'second': 1000.0, u'seconds': 1000.0, u'minute': 60000.0, u'minutes': 60000.0,
        u'hour': 3600000.0, u'hours': 3600000.0, u'day': 86400000.0, u'days': 86400000.0}
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
M['dual_unit_lines'] = DUAL
M['dual_prove'] = [z[6] for z in DUAL]
M['dual_gloss_forms'] = sorted(set(u'%g %s' % (z[4], z[5]) for z in DUAL))
M['dual_plural_at_one'] = len([z for z in DUAL if z[4] == 1 and z[5].endswith(u's')])
print(u'6 面内自证换算行(两单位同印): %s' % (json.dumps(DUAL, ensure_ascii=False),))
print(u'  自证成立 %d/%d; 括号内单位形 %s; 值为 1 仍写复数的 %d 枚'
      % (len([z for z in DUAL if z[6]]), len(DUAL), M['dual_gloss_forms'], M['dual_plural_at_one']))
assert DUAL and all(z[6] for z in DUAL), u'双单位行空或有不自证的'
# 6b 外单位不印在数上, 只写在正文别处(隐式外单位): 靠 "(in milliseconds)" 这句自证
DUAL2 = []
blocks, cur = [], None
for x in L[3]:
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
        DUAL2.append([k, mm.group(0).strip(), m.group(2), numv(mm.group(1)),
                      numv(mm.group(2)), mm.group(3),
                      numv(mm.group(1)) * UNIT[m.group(2)] == numv(mm.group(2)) * UNIT[mm.group(3)]])
M['dual_implicit_lines'] = DUAL2
print(u'6b 隐式外单位自证行: %s' % (json.dumps(DUAL2, ensure_ascii=False),))
assert DUAL2 and all(z[6] for z in DUAL2), u'隐式单位行空或不自证'
CONV = []
for i in range(NSRC):
    for m in re.finditer(u'(?<![A-Za-z0-9])(\\d[\\d,]*(?:\\.\\d+)?)([ ]?)(nanoseconds|milliseconds|millisecond'
                         u'|seconds|second|minutes|minute)(?![A-Za-z])', T[i]):
        CONV.append([LBL[i], m.group(1), m.group(3), numv(m.group(1)) * UNIT[m.group(3)] / 1000.0,
                     m.group(2) == u''])
M['unit_conv'] = CONV
M['conv_glued_n'] = len([z for z in CONV if z[4]])
M['conv_spaced_n'] = len([z for z in CONV if not z[4]])
print(u'  数值×时长单位 %d 组(空格 %d ⇎ 粘连 %d); 折成秒后去重值 %s'
      % (len(CONV), M['conv_spaced_n'], M['conv_glued_n'], sorted(set(z[3] for z in CONV))))
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
M['conv_same'] = dict((str(k), v) for k, v in sorted(SAME.items()))
print(u'  跨份换算后同值: %s' % (json.dumps(M['conv_same'], ensure_ascii=False),))

# ---------- 7. 参数名拼写族: 三把名尺 ----------
NAMES = [u'DupAddrDetectTransmits', u'dad_transmits', u'use_dad', u'accept_dad', u'optimistic_dad',
         u'enhanced_dad', u'IPv6DuplicateAddressDetection', u'DuplicateAddressDetection',
         u'IPv4DuplicateAddressDetectionTimeoutSec', u'IPv6RetransmissionTimeSec',
         u'RetransTimer', u'RETRANS_TIMER', u'MAX_RTR_SOLICITATION_DELAY', u'DELAY_FIRST_PROBE_TIME',
         u'MAX_MULTICAST_SOLICIT', u'MAX_UNICAST_SOLICIT', u'mcast_solicit', u'ucast_solicit',
         u'app_solicit', u'router_solicitations', u'router_solicitation_interval',
         u'retrans_time', u'RetryCount', u'MAX_RTR_SOLICITATIONS']
NRM = [pnorm(x.replace(u'_', u' ')) for x in NAMES]
M['name_raw'] = [[cnt_cur(T[i], x) for x in NAMES] for i in range(NSRC)]
M['name_ci'] = [[cnt_cur(FL[i], pnorm(x)) for x in NAMES] for i in range(NSRC)]
M['name_norm'] = [[ub(FL[i], nrm, u'none') for nrm in NRM] for i in range(NSRC)]
print(u'7 参数名(字面尺):')
for k, x in enumerate(NAMES):
    print(u'   %-34s %s' % (x, [M['name_raw'][i][k] for i in range(NSRC)]))
M['name_absent'] = [x for k, x in enumerate(NAMES) if sum(M['name_raw'][i][k] for i in range(NSRC)) == 0]
print(u'  一枚也不出的名:', M['name_absent'])

# ---------- 8. 默认值句式: 各一条正则, 句式互不重叠 ----------
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
M['shape_n'] = [[len(SHAPES[j][1].findall(T[i])) for j in range(len(SHAPES))] for i in range(NSRC)]
M['shape_lbls'] = [s[0] for s in SHAPES]
M['default_val_is_num'] = [[len([z for z in SHAPES[j][1].findall(T[i])
                                 if re.match(u'^[-.\\d]', u'%s' % (z,))])
                            for j in range(len(SHAPES))] for i in range(NSRC)]
M['default_gloss'] = [len(re.findall(u'(?m)^[ \\t]*Default: +\\d \\(', T[i])) for i in range(NSRC)]
print(u'8 默认句式枚数(逐份):', M['shape_lbls'])
for i in range(NSRC):
    print(u'   %-7s %s' % (LBL[i], M['shape_n'][i]))
print(u'  默认值位上是数字的:', M['default_val_is_num'], u' 带括注的 Default: n (…):', M['default_gloss'])
DK = {}
for i in [3]:
    cur = None
    for x in L[i]:
        if keylin(x):
            cur = x.split(u' - ')[0]
            DK[cur] = []
        elif cur is not None:
            DK[cur].append(x)
M['sysctl_keys'] = len(DK)
M['sysctl_key_types'] = dict((x.split(u' - ')[0], x.split(u' - ')[1].strip())
                             for x in L[3] if keylin(x))
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
    for x in DK[k]:                                        # 逐行判, 不跨行吞前一个数字
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
print(u'  相关键与默认值:')
for k in sorted(REL):
    print(u'   %-30s %-10s %-14s %s' % (k, str(DEF[k][0]), DEF[k][1], M['sysctl_key_types'].get(k, u'-')))

# ---------- 9. 引用边: 带空格 ⇎ 不带空格两把尺 ----------
RXN_SP = re.compile(u'RFC (\\d{4})')
RXN_NS = re.compile(u'RFC(\\d{4})')
for i in range(NSRC):
    sp = sorted(set(RXN_SP.findall(T[i])))
    ns = sorted(set(RXN_NS.findall(T[i])))
    print(u'9 %s 引用(带空格) %s ｜ 粘连 %s ｜ 只在粘连档 %s' % (LBL[i], sp, ns, sorted(set(ns) - set(sp))))
M['ref_spaced'] = [sorted(set(RXN_SP.findall(T[i]))) for i in range(NSRC)]
M['ref_glued'] = [sorted(set(RXN_NS.findall(T[i]))) for i in range(NSRC)]
M['ref_n'] = [[len(RXN_SP.findall(T[i])), len(RXN_NS.findall(T[i]))] for i in range(NSRC)]

# ---------- 10. 段窗定界(节级): 标题现读 ----------
def blk(i, a, b):
    return NL.join(L[i][a:b])


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
    print(u'10 [%s L%d] %s' % (tag, a + 1, nd[:60]))
M['win_heads'] = W

# ---------- 11. 段窗数字普查: 五把定界谓词(节/段/标签/键/选项) ----------
IDX = dict((LBL[i], i) for i in range(NSRC))
VARRE = re.compile(u'\\b(MAX_[A-Z_]+|MIN_[A-Z_]+|RETRANS_TIMER|REACHABLE_TIME|RTR_[A-Z_0-9]+'
                   u'|DELAY_FIRST_PROBE_TIME|DupAddrDetectTransmits|RetransTimer)\\b')


def secnum(x):
    m = re.match(u'^(\\d+(?:\\.\\d+)*\\.?)\\s\\s+(?=[A-Z])', x.lstrip())
    return m.group(1) if m else None


def toc_line(x):
    return re.search(u'\\.\\s+\\.\\s+\\d+\\s*$', x) is not None


def find_body(i, nd):
    """同一 needle 可能先在目录页出现: 取最后一个窗口命中, 且该行不得是目录点线行."""
    got = -1
    for a in range(len(L[i])):
        win = NL.join(L[i][a:a + 4])
        if pnorm(nd)[:16] not in pnorm(win):
            continue
        f, offs = foldmap(win)
        if f.find(pnorm(nd)) >= 0 and not toc_line(L[i][a + (line_of_face(offs, f.find(pnorm(nd))) or 0)]):
            got = a + line_of_face(offs, f.find(pnorm(nd)))
    return got


def window(i, a, kind):
    """五种定界写法共用一个游标: 各自的停止谓词不同, 定义同一个“这一段”."""
    b = a + 1
    if kind == u'sec':
        p0 = secnum(L[i][a])
        while b < len(L[i]):
            p = secnum(L[i][b])
            if p is not None and not p.startswith(p0):
                break
            b += 1
    elif kind == u'para':
        while b < len(L[i]) and L[i][b].strip() != u'' and not ffline(L[i][b].strip()):
            b += 1
    elif kind == u'label':
        while b < len(L[i]):
            s = L[i][b].strip()
            if re.match(u'^[A-Za-z ]+constants:$', s) or secnum(L[i][b]) is not None:
                break
            b += 1
    elif kind == u'key':
        while b < len(L[i]) and not keylin(L[i][b]):
            b += 1
    else:
        while b < len(L[i]) and not optlin(L[i][b]):
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
    txt = NL.join(L[i][a:b])
    clean = NL.join([x for x in L[i][a:b] if not is_shell(x, i)])
    nu = sorted(set(RX_STRICT.findall(txt)))
    nuc = sorted(set(RX_STRICT.findall(clean)))
    var = sorted(set(VARRE.findall(txt)))
    varc = sorted(set(VARRE.findall(clean)))
    dig = sorted(set(re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', txt)))
    digc = sorted(set(re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', clean)))
    shell_n = len([x for x in L[i][a:b] if is_shell(x, i)])
    CW.append([tag, kind, head, a + 1, b, len(nu), len(var), len(dig), nu, var, dig,
               len(nuc), len(varc), len(digc), nuc, varc, digc, shell_n])
    print(u'11 %-7s %s L%d-%d «%s» 严轨 %d 变量 %d 数字 %s ⇎ 摘壳后 %d/%d/%d'
          % (tag, kind, a + 1, b, head[:36], len(nu), len(var), dig[:10], len(nuc), len(varc), len(digc)))
M['win_census'] = CW
M['win_numless_with_var'] = [[z[0], z[1], z[2]] for z in CW if z[5] == 0 and z[6] > 0]
M['win_var_kinds'] = sorted(set(v for z in CW for v in z[9]))
M['win_shell_lines'] = [[z[0], z[2], z[17]] for z in CW if z[17] > 0]
print(u'  窗内“严轨零命中、只有变量”的: %s' % (json.dumps(M['win_numless_with_var'], ensure_ascii=False),))
print(u'  窗内出现过的变量名: %s' % (M['win_var_kinds'],))
print(u'  窗内混进的壳行: %s' % (json.dumps(M['win_shell_lines'], ensure_ascii=False),))
assert any(z[5] == 0 and z[6] > 0 for z in CW), u'没有“只有变量、无数字×单位”的窗, 对照轴塌了'

# ---------- 12. 默认值位上的形状: 标记词表 + 一位一判 ----------
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
print(u'12 默认值位形状:')
for i in range(NSRC):
    cnt = {}
    for z in DSLOT[LBL[i]]:
        cnt[z[1]] = cnt.get(z[1], 0) + 1
    print(u'   %-7s 共 %d 行 %s' % (LBL[i], len(DSLOT[LBL[i]]), cnt))
    for z in DSLOT[LBL[i]]:
        if z[1] in (u'变量名+单位', u'算式', u'散文/交回', u'开关/交回字', u'数+单位(括号换算)'):
            print(u'      %-16s %s' % (z[1], z[3][:56]))

# ---------- 13. 4861 常量表: 名⇎值⇎单位三列, 窗内 ⇎ 全篇两把尺 ----------
CTRX = re.compile(u'^\\s*([A-Z][A-Z_0-9]+)\\s+(\\d[\\d,]*(?:\\.\\d+)?|\\.\\d+)'
                  u'( (milliseconds|millisecond|seconds|second|transmissions))?\\s*$')
ca = find_body(1, u"10.  Protocol Constants")
cb = window(1, ca, u'sec')
CT, CTF = [], []
for a in range(ca, cb):
    m = CTRX.match(L[1][a])
    if m:
        CT.append([m.group(1), m.group(2), m.group(4) if m.group(4) else u'无量纲', a + 1])
for a in range(len(L[1])):
    m = CTRX.match(L[1][a])
    if m:
        CTF.append([m.group(1), m.group(2), m.group(4) if m.group(4) else u'无量纲', a + 1])
M['const_rows'] = CT
M['const_rows_doc'] = CTF
print(u'13 §10 窗内常量行 %d 枚 ⇎ 全篇同正则 %d 枚; 带 ms %d; 带 transmissions %d; 无量纲 %d'
      % (len(CT), len(CTF), len([z for z in CT if z[2].startswith(u'milli')]),
         len([z for z in CT if z[2] == u'transmissions']), len([z for z in CT if z[2] == u'无量纲'])))
for z in CT:
    print(u'   L%-6d %-34s %-10s %s' % (z[3], z[0], z[1], z[2]))
M['const_unit_kinds'] = sorted(set(z[2] for z in CT))
M['const_comma_rows'] = [z[0] for z in CT if u',' in z[1]]
M['const_dot_rows'] = [z[0] for z in CT if z[1].startswith(u'.')]
M['const_out_of_win'] = [[z[0], z[1], z[3]] for z in CTF if [z[0], z[1], z[2]] not in
                         [[y[0], y[1], y[2]] for y in CT]]
print(u'  千分位行:', M['const_comma_rows'], u' 前导点行:', M['const_dot_rows'])
print(u'  全篇多出的行:', M['const_out_of_win'])

json.dump(M, io.open(u'corpus/_b93meas.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
print(u'已落 corpus/_b93meas.json ｜ 键 %d' % len(M))
