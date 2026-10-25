# -*- coding: utf-8 -*-
"""B63 建条目(第二遍现算, 四源): ⟦A⟧rfc1122(1989 主机要求回溯稿) ⇎ ⟦B⟧rfc2988(2000) ⇎ ⟦C⟧rfc6298(2011, Obsoletes: 2988 / Updates: 1122) ⇎ ⟦D⟧rfc9002(2021, QUIC 丢包恢复)。
主轴: 还没有 RTT 样本时第一个重传超时设多久——⟦A⟧ 在初始化清单里写 (b) RTO = 3 seconds, ⟦B⟧ 把同一个 3 秒接过来当规则 (2.1),
⟦C⟧ 把它降到 1 秒、却把 3 秒原样留在 (5.7) 的 SYN 回退 MUST 里(字面出现次数反而涨到九处), ⟦D⟧ 干脆不给超时数值: 它给初始 RTT 333 毫秒,
再宣称“results in a PTO of 1 second”——由它自己的常数复算得 999(实数档)⇎ 997(rttvar 先取整档), 宣称与算法差 1~3 毫秒, 库里无一行记这件事。
第二遍的独立性: 采集侧(_pick63.py)用 re.findall/前后瞻与集合运算; 本遍一律换成游标档(find 循环+逐字符判邻)、
时长扫描档(逐字符切“数字+空白+单位词”再归一到毫秒, 并给每个 token 打上“跨行”⇎“小数割裂”两枚标志)、
和式解析档(把 X <- B + max (G, K*V) 与 PTO = s + max(4*v, kGranularity) + max_ack_delay 拆成结构而非数正则命中)、
形状量用逐字符计数与数换行; 搬运账用排序后两指针求交。
两遍只在定义一致处对账, 逐键比 corpus/_b63meas.json; 采集侧独有的键(sha256 签名、原始条款行清单)算法即口径, 不参与对账。
抓取时刻、rfc-editor.org 此刻给这四份挂的状态、各实现里 TCP_RTO_MIN 的实际取值只在本机或站外成立, 不进门槛。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
NSRC = 4
ENTRY = u'%s/babeltele/B63_tcp_initial_rto_four_answers.md' % C
PATH = [u'corpus/raw/tcpRTO/rfc1122.txt', u'corpus/raw/tcpRTO/rfc2988.txt', u'corpus/raw/tcpRTO/rfc6298.txt',
        u'corpus/raw/tcpiw/rfc9002.txt']
TAGS = [u'A', u'B', u'C', u'D']
LB = dict(zip(TAGS, [u'89 三秒', u'00 三秒', u'11 一秒', u'21 三百三']))
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN --- (corpus/_wire63.py 把这一段机械切进 audit.py::_b63_scan)
WCH = u' \t\n\x0b\x0c\r'
DIG = u'0123456789'
DSET = frozenset(DIG)
ALW = DIG + u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
RAWB = [io.open(p, 'rb').read() for p in PATH]
TXT = [r.decode('utf-8-sig') for r in RAWB]
LST = [t.split(NL) for t in TXT]
LOW = [t.lower() for t in TXT]
FO = [u' '.join(t.split()) for t in TXT]
F = {}


def pnorm(s):
    o = []
    for c in s.lower():
        if (u'a' <= c <= u'z') or (u'0' <= c <= u'9'):
            o.append(c)
    return u''.join(o)


FAN = [pnorm(t) for t in TXT]


def four(name, f, n=NSRC):
    F[name] = [f(k) for k in range(n)]
    return F[name]


def pos(s, sub, frm=0, to=None):
    """游标档: find 循环取出现位置(采集侧用 str.count / re.findall)。to=None 时必须 honour frm。"""
    out, k = [], s.find(sub, frm)
    lim = len(s) if to is None else to
    while k >= 0 and k < lim:
        out.append(k)
        k = s.find(sub, k + 1)
    return out


def occ(s, sub, frm=0, to=None):
    return len(pos(s, sub, frm, to))


def is_alpha(ch):
    return (u'a' <= ch <= u'z') or (u'A' <= ch <= u'Z')


# ---- 形状档(逐字符计数、数换行, 而非 len/split) ----
four(u'bytes', lambda i: os.path.getsize(PATH[i]))
four(u'chars', lambda i: sum(1 for _ in TXT[i]))
four(u'chars_no_nl', lambda i: sum(1 for ch in TXT[i] if ch != NL))
four(u'lines', lambda i: TXT[i].count(NL) + 1)
four(u'nonblank', lambda i: len([l for l in LST[i] if l.strip()]))
four(u'maxlen', lambda i: max([len(l) for l in LST[i]]))
four(u'trail', lambda i: len([l for l in LST[i] if l != l.rstrip()]))
four(u'cr', lambda i: occ(TXT[i], u'\r'))
four(u'nonascii', lambda i: len([ch for ch in TXT[i] if ord(ch) > 127]))
four(u'nonascii_raw', lambda i: len([ch for ch in RAWB[i].decode('utf-8', 'replace') if ord(ch) > 127]))
four(u'bom', lambda i: 1 if RAWB[i][:3] == b'\xef\xbb\xbf' else 0)
four(u'formfeed', lambda i: sum(1 for ch in TXT[i] if ch == u'\x0c'))
F[u'chars_split'] = [len(x) for x in TXT]
F[u'lines_nl'] = [len(x.split(NL)) for x in TXT]
F[u'rec_close'] = [F[u'chars'][i] - F[u'chars_split'][i] + F[u'lines'][i] - F[u'lines_nl'][i]
                   for i in range(NSRC)]
F[u'sig'] = [hashlib.blake2b(RAWB[i], digest_size=8).hexdigest() for i in range(NSRC)]
F[u'sig_distinct'] = len(set(F[u'sig']))


# ---- 壳档: 页眉“带空格 ⇎ 不带空格”两档, 页脚“方括号 ⇎ 旧式 ⇎ 左侧 IETF 字样”三档 ----
def hdr_at(l, sp):
    """页眉判定(逐字符): 'RFC'[空格]四位编号(后面不是数字), 再接空白或行尾; sp 档另要求编号后余文非空。"""
    if l[:3] != u'RFC':
        return False
    k = 3
    if sp:
        if k >= len(l) or l[k] != u' ':
            return False
        k += 1
    d = 0
    while k < len(l) and l[k] in DIG:
        k += 1
        d += 1
    if d != 4:
        return False
    if k < len(l) and l[k] in DIG:
        return False
    if k >= len(l):
        return not sp
    if l[k] != u' ':
        return False
    return bool(l[k + 1:].strip()) if sp else True


def page_end(s, brk):
    e = -1
    if brk:
        if not s.endswith(u']'):
            return False
        e = s.rfind(u'[Page ')
        tail = s[e + 6:] if e >= 0 else u''
        if e < 0 or not tail.endswith(u']'):
            return False
        tail = tail[:-1]
    else:
        e = s.rfind(u'Page ')
        tail = s[e + 5:] if e >= 0 else u''
    if e < 0 or tail == u'':
        return False
    for ch in tail:
        if ch not in DIG:
            return False
    pre = s[e - 1:e]
    return pre in (u' ', u'[', u'')


def is_hdr(l):
    return hdr_at(l, True) or hdr_at(l, False)


def is_foot(l):
    s = l.strip()
    return page_end(s, True) or page_end(s, False)


four(u'hdr_sp', lambda i: len([l for l in LST[i] if hdr_at(l, True)]))
four(u'hdr_ns', lambda i: len([l for l in LST[i] if hdr_at(l, False) and not hdr_at(l, True)]))
four(u'hdr', lambda i: len([l for l in LST[i] if is_hdr(l)]))
four(u'foot', lambda i: len([l for l in LST[i] if is_foot(l)]))
four(u'foot_brk', lambda i: len([l for l in LST[i] if page_end(l.strip(), True)]))
four(u'foot_ietf', lambda i: len([l for l in LST[i] if page_end(l.strip(), True)
                                  and l.strip().startswith(u'Internet Engineering Task Force')]))
four(u'foot_old', lambda i: len([l for l in LST[i] if page_end(l.strip(), False)
                                 and not page_end(l.strip(), True)]))
F[u'pagelines'] = [F[u'hdr'][i] + F[u'foot'][i] for i in range(NSRC)]
F[u'pages_est'] = [F[u'formfeed'][i] if F[u'formfeed'][i] else max(F[u'hdr'][i], F[u'foot'][i])
                   for i in range(NSRC)]
F[u'hdr_ledger'] = [F[u'hdr_sp'][i] + F[u'hdr_ns'][i] - F[u'hdr'][i] for i in range(NSRC)]
F[u'hdr_ledger_sum'] = sum(F[u'hdr_ledger'])
F[u'ff_foot_sum'] = sum(F[u'formfeed'][i] - F[u'foot'][i] for i in range(NSRC))
F[u'trail_foot_sum'] = sum(F[u'trail'][i] - F[u'foot'][i] for i in range(NSRC))
F[u'ietf_vs_ff'] = [F[u'foot_ietf'][i] - F[u'formfeed'][i] for i in range(NSRC)]
F[u'ietf_vs_ff_sum'] = sum(F[u'ietf_vs_ff'])
# 壳对“本编号被印了多少次”的抬高: A 面里 '1122' 的子串档 − 页眉档 − 抬头 Request for Comments 行
F[u'a_self_lit'] = occ(TXT[0], u'1122')
F[u'a_shell_1122_sp'] = occ(TXT[0], u'Request for Comments: 1122')
F[u'a_1122_resid'] = F[u'a_self_lit'] - F[u'hdr_ns'][0] - F[u'a_shell_1122_sp']

# ---- 字面族(子串档) ----
LITK = {u'3seconds': u'3 seconds', u'1second': u'1 second', u'333ms': u'333 ms', u'1ms': u'1 ms',
        u'200ms': u'200 ms', u'rtoarrow': u'RTO <- ', u'rtovalue': u'RTO = ', u'setrto': u'set RTO',
        u'inirto': u'initial RTO', u'rounded': u'rounded up', u'kgran': u'kGranularity',
        u'kinirtt': u'kInitialRtt', u'smoothed': u'smoothed_rtt', u'rttvar_l': u'rttvar',
        u'rttvar_u': u'RTTVAR', u'srtt': u'SRTT', u'pto': u'PTO', u'rto': u'RTO', u'4xrttvar': u'4*rttvar',
        u'4k_rttvar': u'4 * rttvar', u'backoff': u'backing off',
        u'commab': u'less than 1 second then the', u'commac': u'less than 1 second, then the',
        u'revert': u'MUST be re-initialized to 3 seconds', u'onesecclaim': u'a PTO of 1 second',
        u'tcpinitrto': u"TCP's initial", u'jaco': u'Jacobson', u'333full': u'333 milliseconds',
        u'half': u'rttvar = kInitialRtt / 2', u'pto_eq': u'PTO = smoothed_rtt',
        u'smoothinit': u'smoothed_rtt = kInitialRtt'}
for k in sorted(LITK):
    four(u'lit_' + k, lambda i, k=k: occ(TXT[i], LITK[k]))
F[u'assign_forms'] = [F[u'lit_rtoarrow'][i] + F[u'lit_rtovalue'][i] for i in range(NSRC)]
F[u'assign_gap'] = [F[u'lit_rtoarrow'][i] - F[u'lit_rtovalue'][i] for i in range(NSRC)]
F[u'floor_forms_gap'] = [F[u'lit_commab'][i] + F[u'lit_commac'][i] for i in range(NSRC)]
F[u'unit_both_333'] = [1 if F[u'lit_333ms'][i] and F[u'lit_333full'][i] else 0 for i in range(NSRC)]

# ---- 时长扫描档(逐字符: 数字串→空白→单位词, 归一到毫秒; 采集侧用 DUR 正则) ----
UNITS = [(u'milliseconds', 1), (u'millisecond', 1), (u'ms', 1), (u'seconds', 1000), (u'second', 1000),
         (u'sec', 1000), (u'useconds', 0), (u'usecond', 0)]


def unit_at(t, k):
    for nm, mul in UNITS:
        if t[k:k + len(nm)] == nm:
            e = k + len(nm)
            if e >= len(t) or not is_alpha(t[e]):
                return nm, e
    return None, k


def dur_scan(t):
    """返回 [(毫秒, token 起点, 数字串, 单位名, 跨行标志, 小数割裂标志)]; 非重叠、由左而右, 与正则 finditer 同定义。"""
    out, i, n = [], 0, len(t)
    while i < n:
        if t[i] in DIG:
            j = i + 1
            while j < n and (t[j] in DIG or t[j] == u','):
                j += 1
            k = j
            while k < n and t[k] in WCH:
                k += 1
            nm, e = unit_at(t, k)
            if nm is not None:
                frac = 1 if (i >= 2 and t[i - 1] == u'.' and t[i - 2] in DIG) else 0
                out.append((int(t[i:j].replace(u',', u'')) * dict(UNITS)[nm], i, t[i:j], nm,
                            1 if NL in t[j:k] else 0, frac))
                i = e
                continue
        i += 1
    return out


DURS = [dur_scan(t) for t in TXT]
for i in range(NSRC):
    vs = sorted(set(x[0] for x in DURS[i] if x[0] > 0))
    F[u'durms_' + TAGS[i].lower()] = vs
    F[u'durms_n_' + TAGS[i].lower()] = len(vs)
    F[u'durlit_' + TAGS[i].lower()] = len(DURS[i])
F[u'durlit'] = [F[u'durlit_' + TAGS[i].lower()] for i in range(NSRC)]
F[u'durms_n'] = [F[u'durms_n_' + TAGS[i].lower()] for i in range(NSRC)]
F[u'dur_ms_lo'] = min([min(F[u'durms_' + TAGS[i].lower()]) for i in range(NSRC)])
F[u'dur_ms_hi'] = max([max(F[u'durms_' + TAGS[i].lower()]) for i in range(NSRC)])
F[u'dur_ratio'] = [F[u'dur_ms_hi'] // F[u'dur_ms_lo']]
for k, s in ((u'seconds', u'second'), (u'ms', u'ms'), (u'mill word', u'millisecond')):
    F[u'unit_' + k.replace(u' ', u'_')] = [occ(TXT[i], s) for i in range(NSRC)]
# 伪值两路: 跨行 token(数与单位被换行拆开) ⇎ 小数割裂 token("2.5 seconds" 被读成 5 秒)
F[u'y_dur_wrap'] = [len([x for x in DURS[i] if x[4]]) for i in range(NSRC)]
F[u'y_dur_frac'] = [len([x for x in DURS[i] if x[5]]) for i in range(NSRC)]
F[u'y_dur_frac_vals'] = [sorted(set(x[0] for x in DURS[i] if x[5])) for i in range(NSRC)]
F[u'y_dur_frac_only'] = [len([v for v in F[u'durms_' + TAGS[i].lower()]
                              if v in F[u'y_dur_frac_vals'][i]]) for i in range(NSRC)]
F[u'y_dur_wrap_ms'] = [sorted(set(x[0] for x in DURS[i] if x[4])) for i in range(NSRC)]
F[u'y_unit_used'] = [sorted(set(x[3] for x in DURS[i])) for i in range(NSRC)]
F[u'y_unit_n'] = [len(F[u'y_unit_used'][i]) for i in range(NSRC)]
# 归一后值为零的 token(“RTT = 0 seconds”⇎“1.0”被读成“0 seconds”): 单位存在但量是零
F[u'y_dur_zero'] = [len([x for x in DURS[i] if x[0] == 0]) for i in range(NSRC)]
F[u'y_dur_zero_wrap'] = [len([x for x in DURS[i] if x[0] == 0 and x[4]]) for i in range(NSRC)]
F[u'y_dur_zero_frac'] = [len([x for x in DURS[i] if x[0] == 0 and x[5]]) for i in range(NSRC)]
# 89 三秒的初始化清单把 RTT 置零⇎21 三百三把初始 RTT 置 333: 同一格的两种填法
F[u'y_rtt0'] = [occ(TXT[i], u'RTT = 0 seconds') for i in range(NSRC)]

# ---- 规范窗(取最后一处命中, 回溯到最近编号标题, 前推到“首个标题文本首 token 不同”的下一标题) ----
RULE = {u'A': u'(b)  RTO = 3 seconds', u'B': u'set RTO <- 3 seconds (per RFC 1122',
        u'C': u'set RTO <- 1 second', u'D': u'SHOULD be set to 333 milliseconds'}


def headnum(l):
    """编号标题(逐字符): 任意前导空白(含换页符), 数字组可带小节点, 可选尾点, 再接空白与非空题文; 返回编号串或 None。"""
    n = 0
    while n < len(l) and l[n] in WCH:
        n += 1
    if n >= len(l) or l[n] not in DIG:
        return None
    j, seg = n, u''
    while True:
        d = u''
        while j < len(l) and l[j] in DIG:
            d += l[j]
            j += 1
        if not d:
            return None
        if j < len(l) and l[j] == u'.':
            seg += (u'.' if seg else u'') + d + u'.'
            j += 1
            if j >= len(l) or l[j] not in DIG:
                break
            continue
        seg += (u'.' if seg else u'') + d
        break
    if seg.endswith(u'.'):
        seg = seg[:-1]
    k = j
    while k < len(l) and l[k] in WCH:
        k += 1
    if k == j or k >= len(l):
        return None
    return seg


SECW, SECN = [], []
for i in range(NSRC):
    ls = LST[i]
    hits = [n for n, l in enumerate(ls) if RULE[TAGS[i]] in l]
    assert hits, TAGS[i]
    r = hits[-1]
    a = None
    for n in range(r, -1, -1):
        if headnum(ls[n]) is not None and len(ls[n].strip()) > 3:
            a = n
            break
    if a is None:
        a = r
    na = headnum(ls[a])
    pre = ls[a].strip().split(u' ')[0]
    b = len(ls)
    for n in range(r + 1, len(ls)):
        if headnum(ls[n]) is None or len(ls[n].strip()) <= 3:
            continue
        s = ls[n].strip()
        if s == ls[a].strip() or s.startswith(pre):
            continue
        b = n
        break
    SECW.append((a, b))
    SECN.append(na)
F[u'sec_w'] = SECW
F[u'sec_num'] = SECN
four(u'sec_hit', lambda i: len([n for n, l in enumerate(LST[i]) if RULE[TAGS[i]] in l]))
F[u'sec_a'] = [w[0] for w in SECW]
F[u'sec_b'] = [w[1] for w in SECW]
F[u'sec_head'] = [LST[i][SECW[i][0]].strip()[:64] for i in range(NSRC)]


def subitem(l):
    """(a)/(b) 式子条目: 前导空白后接 '(字母)' 或 '字母)', 再接空白与非空。"""
    n = 0
    while n < len(l) and l[n] in WCH:
        n += 1
    if n < len(l) and l[n] == u'(':
        n += 1
    if n >= len(l) or not (u'a' <= l[n] <= u'z'):
        return False
    n += 1
    if n >= len(l) or l[n] != u')':
        return False
    n += 1
    if n >= len(l) or l[n] not in WCH:
        return False
    k = n
    while k < len(l) and l[k] in WCH:
        k += 1
    return k < len(l)


F[u'sec_sub'] = [len([l for l in LST[i][SECW[i][0]:SECW[i][1]] if subitem(l)]) for i in range(NSRC)]
OFF = []
for i in range(NSRC):
    o, s = [], 0
    for l in LST[i]:
        o.append(s)
        s += len(l) + 1
    OFF.append(o)
F[u'sec_len'] = [len(NL.join(LST[i][SECW[i][0]:SECW[i][1]])) for i in range(NSRC)]
for i in range(NSRC):
    F[u'sec_len_' + TAGS[i].lower()] = F[u'sec_len'][i]


def wend(i):
    """规范窗末字节偏移(下一标题行的行首−1); 窗到文末时取全篇长度。"""
    b = SECW[i][1]
    return OFF[i][b] - 1 if b < len(OFF[i]) else len(TXT[i])


for i in range(NSRC):
    F[u'sec_off_' + TAGS[i].lower()] = (OFF[i][SECW[i][0]], wend(i))
WINS = [(u'3seconds', u'3 seconds'), (u'1second', u'1 second'), (u'333ms', u'333 ms'),
        (u'333full', u'333 milliseconds'), (u'rtoarrow', u'RTO <- '),
        (u'rounded', u'rounded up'), (u'kgran', u'kGranularity')]
for k, s in WINS:
    F[u'secw_' + k] = [occ(TXT[i], s, OFF[i][SECW[i][0]], wend(i)) for i in range(NSRC)]
    F[u'outw_' + k] = [F[u'lit_' + k][i] - F[u'secw_' + k][i] for i in range(NSRC)]
# 窗内⇎窗外的时长档(值域档不看位置, 窗档看位置)
F[u'y_dur_win'] = [sorted(set(x[0] for x in DURS[i] if x[0] > 0
                              and OFF[i][SECW[i][0]] <= x[1] < wend(i))) for i in range(NSRC)]
F[u'y_dur_out'] = [sorted(set(x[0] for x in DURS[i] if x[0] > 0
                              and not (OFF[i][SECW[i][0]] <= x[1] < wend(i)))) for i in range(NSRC)]
F[u'y_dur_win_n'] = [len(x) for x in F[u'y_dur_win']]
F[u'y_dur_out_n'] = [len(x) for x in F[u'y_dur_out']]
# 窗内⇎窗外的义务词与措辞档
for k, s in ((u'may', u'MAY'), (u'must', u'MUST'), (u'should', u'SHOULD'), (u'inirto', u'initial RTO'),
             (u'threesec', u'3 seconds'), (u'appendix', u'Appendix')):
    F[u'y_secw_' + k] = [occ(TXT[i], s, OFF[i][SECW[i][0]], wend(i)) for i in range(NSRC)]
    F[u'y_outw_' + k] = [occ(TXT[i], s) - F[u'y_secw_' + k][i] for i in range(NSRC)]

# ---- 和式解析档: X <- B + max (A, C*V) [+ E] ----
def parse_term(s):
    s = s.strip()
    star = s.find(u'*')
    if star > 0:
        return (s[:star], s[star + 1:])
    return (u'', s)


def is_maxnode(tm):
    """取大档: 以 max 起头且括号里带一枚逗号(排除 QUIC 的变量名 max_ack_delay)。"""
    if not tm.startswith(u'max'):
        return False
    q = tm.find(u'(')
    if q < 0:
        return False
    return u',' in tm[q + 1:tm.rfind(u')')]


def parse_sum_lines(ls):
    """逐字符拆“行首名 <-/= 右侧和式”: 和式按深度 0 的 ' + ' 分列, max 括号拆两参数。"""
    res = []
    for l in ls:
        s = l.strip()
        if not (s.startswith(u'RTO') or s.startswith(u'PTO')):
            continue
        p = 3
        while p < len(s) and (s[p] == u' ' or s[p] == u'\t'):
            p += 1
        if s[p:p + 2] == u'<-':
            op = u'<-'
            p += 2
        elif s[p:p + 1] == u'=':
            op = u'='
            p += 1
        else:
            continue
        rhs = s[p:].strip()
        terms, buf, d = [], [], 0
        for ch in rhs:
            if ch == u'(':
                d += 1
            elif ch == u')':
                d -= 1
            if ch == u'+' and d == 0 and buf and buf[-1] == u' ':
                terms.append(u''.join(buf[:-1]).strip())
                buf = []
                continue
            buf.append(ch)
        terms.append(u''.join(buf).strip())
        terms = [x for x in terms if x]
        lhs, base, tail, mfirst, msecond, coef, mvar = s[:3], u'', u'', u'', u'', u'', u''
        mi = -1
        for x in terms:
            if is_maxnode(x):
                mi = terms.index(x)
                break
        for z, tm in enumerate(terms):
            if is_maxnode(tm):
                q = tm.find(u'(')
                inner = tm[q + 1:tm.rfind(u')')]
                a1, a2 = inner.split(u',', 1)
                mfirst = a1.strip()
                msecond = a2.strip()
                cc, vv = parse_term(a1.strip())
                if cc:
                    coef, mvar = cc, vv
                else:
                    cc, vv = parse_term(a2.strip())
                    coef, mvar = cc, vv
            elif mi < 0 or z < mi:
                base = base + u'+' + tm if base else tm
            else:
                tail = tail + u'+' + tm if tail else tm
        res.append((lhs, op, len(terms), mfirst, msecond, coef, mvar, base, tail))
    return res


SUMS = [parse_sum_lines(LST[i]) for i in range(NSRC)]
F[u'y_sum_n'] = [len(SUMS[i]) for i in range(NSRC)]
F[u'y_sum_op'] = [SUMS[i][0][1] if SUMS[i] else u'' for i in range(NSRC)]
F[u'y_sum_lhs'] = [SUMS[i][0][0] if SUMS[i] else u'' for i in range(NSRC)]
F[u'y_sum_nterms'] = [SUMS[i][0][2] if SUMS[i] else 0 for i in range(NSRC)]
F[u'y_sum_mfirst'] = [SUMS[i][0][3] if SUMS[i] else u'' for i in range(NSRC)]
F[u'y_sum_msecond'] = [SUMS[i][0][4] if SUMS[i] else u'' for i in range(NSRC)]
F[u'y_sum_coef'] = [SUMS[i][0][5] if SUMS[i] else u'' for i in range(NSRC)]
F[u'y_sum_mvar'] = [SUMS[i][0][6] if SUMS[i] else u'' for i in range(NSRC)]
F[u'y_sum_base'] = [SUMS[i][0][7] if SUMS[i] else u'' for i in range(NSRC)]
F[u'y_sum_tail'] = [SUMS[i][0][8] if SUMS[i] else u'' for i in range(NSRC)]
F[u'y_sum_tail_n'] = [1 if F[u'y_sum_tail'][i] else 0 for i in range(NSRC)]
F[u'y_sum_var_first'] = [1 if u'*' in F[u'y_sum_mfirst'][i] else 0 for i in range(NSRC)]
F[u'y_sum_shape'] = [u'%s%s%s+%s' % (F[u'y_sum_lhs'][i], F[u'y_sum_op'][i], F[u'y_sum_mfirst'][i],
                                     F[u'y_sum_msecond'][i]) if SUMS[i] else u'无和式' for i in range(NSRC)]
F[u'y_coef_num'] = [int(F[u'y_sum_coef'][i]) if F[u'y_sum_coef'][i] and F[u'y_sum_coef'][i] in DIG else 0
                    for i in range(NSRC)]
F[u'y_coef_islit'] = [1 if F[u'y_sum_coef'][i] and F[u'y_sum_coef'][i] in DIG else 0 for i in range(NSRC)]

# ---- 面内现读的数值针(全部游标档, 不手填) ----
def num_after(t, needle):
    """针之后第一串数字(跳过空白, 认千分位逗号: 逗号后恰接三位数字才算同一个数)。"""
    p = t.find(needle)
    if p < 0:
        return 0
    j = p + len(needle)
    while j < len(t) and t[j] in WCH:
        j += 1
    d = u''
    while j < len(t):
        if t[j] in DIG:
            d += t[j]
            j += 1
            continue
        if t[j] == u',' and t[j + 1:j + 4].isdigit() and t[j + 4:j + 5] not in DSET:
            d += t[j + 1:j + 4]
            j += 4
            continue
        break
    return int(d) if d else 0


def num_before(t, needle):
    p = t.find(needle)
    if p < 1:
        return 0
    j = p
    while j > 0 and t[j - 1] in DIG:
        j -= 1
    d = t[j:p]
    return int(d) if d else 0


def dur_after(t, needle, rng=240):
    """针之后第一个“数字(+空白)+单位词”并归一到毫秒; 复用同一个扫描器, 故跨行的数⇎单位也算一枚 token。
    返回 (毫秒, 数字串, 单位名, 跨行标志)。"""
    p = t.find(needle)
    if p < 0:
        return (0, u'', u'', 0)
    seg = t[p + len(needle): p + len(needle) + rng]
    got = dur_scan(seg)
    if not got:
        return (0, u'', u'', 0)
    g = got[0]
    return (g[0], g[2], g[3], g[4])


ANSN = {u'A': u'(b)  RTO = ', u'B': u'set RTO <- ', u'C': u'set RTO <- ', u'D': u'SHOULD be set to '}
ANS = [dur_after(TXT[i], ANSN[TAGS[i]]) for i in range(NSRC)]
F[u'y_ans_ms'] = [ANS[i][0] for i in range(NSRC)]
F[u'y_ans_num'] = [ANS[i][1] for i in range(NSRC)]
F[u'y_ans_unit'] = [ANS[i][2] for i in range(NSRC)]
F[u'y_ans_wrap'] = [ANS[i][3] for i in range(NSRC)]
# 答数行里单位词的单复数随数值变(C 写 second, 其余写复数)
F[u'y_ans_unit_sing'] = [1 if F[u'y_ans_unit'][i] == u'second' else 0 for i in range(NSRC)]
F[u'y_ans_distinct'] = len(set(F[u'y_ans_ms']))
F[u'y_ans_max'] = max(F[u'y_ans_ms'])
F[u'y_ans_min'] = min(F[u'y_ans_ms'])
F[u'y_ans_ratio'] = F[u'y_ans_max'] // F[u'y_ans_min']
F[u'y_ans_rem'] = F[u'y_ans_max'] - F[u'y_ans_ratio'] * F[u'y_ans_min']
# 宣称档: D 的“1 秒”是宣称值(算法给 999/997)
CLAIM = [dur_after(TXT[i], u'starting with a PTO of ')[0] for i in range(NSRC)]
F[u'y_claim_ms'] = [c if c else F[u'y_ans_ms'][i] for i, c in enumerate(CLAIM)]
F[u'y_claim_distinct'] = len(set(F[u'y_claim_ms']))
F[u'y_claim_vs_ans'] = F[u'y_claim_distinct'] - F[u'y_ans_distinct']
# 上限针: A 的 240 秒(数与单位跨行) ⇎ B/C 的“至少 60 秒”
F[u'y_a_cap'] = dur_after(TXT[0], u'upper bound should be ')
F[u'y_a_cap_ms'] = F[u'y_a_cap'][0]
F[u'y_a_cap_wrap'] = F[u'y_a_cap'][3]
F[u'y_a_mult'] = num_before(TXT[0], u'*MSL, i.e., 240')
F[u'y_a_msl_word'] = occ(TXT[0], u'MSL')
F[u'y_bc_cap_ms'] = [dur_after(TXT[i], u'provided it is at least ')[0] for i in range(NSRC)]
F[u'y_bc_cap_wrap'] = [dur_after(TXT[i], u'provided it is at least ')[3] for i in range(NSRC)]
F[u'y_cap_ref_ms'] = F[u'y_bc_cap_ms'][1]
F[u'y_cap_ratio'] = F[u'y_a_cap_ms'] // F[u'y_cap_ref_ms']
F[u'y_cap_rem'] = F[u'y_a_cap_ms'] % F[u'y_cap_ref_ms']
F[u'y_a_cap_win'] = occ(TXT[0], u'upper bound should be ', OFF[0][SECW[0][0]], wend(0))
F[u'y_bc_cap_win'] = [occ(TXT[i], u'provided it is at least ', OFF[i][SECW[i][0]], wend(i))
                      for i in range(NSRC)]
# 89 的两枚散文推荐值(它们进了 89 的时长取值集, 却不属重传超时): 重组定时器上限 ⇎ 告知应用交付问题的 R2 下限
F[u'y_a_reass_hi'] = dur_after(TXT[0], u'value lie between 60 seconds and ')
F[u'y_a_reass_hi_ms'] = F[u'y_a_reass_hi'][0]
F[u'y_a_r2'] = dur_after(TXT[0], u'The value of R2 SHOULD')
F[u'y_a_r2_ms'] = F[u'y_a_r2'][0]
assert (F[u'y_a_reass_hi_ms'], F[u'y_a_r2_ms']) == (120000, 100000), F[u'y_a_reass_hi_ms']
assert F[u'y_a_r2'][3] == 0 and F[u'y_a_reass_hi'][3] == 1
F[u'y_a_reass_hi_wrap'] = F[u'y_a_reass_hi'][3]
# 地板针: B/C 的同一条 (2.4) 上取整条款, 面内现读同一枚 1 秒
F[u'y_floor_ms'] = [dur_after(TXT[i], u'rounded up to ')[0] for i in range(NSRC)]
F[u'y_floor_wrap'] = [dur_after(TXT[i], u'rounded up to ')[3] for i in range(NSRC)]
F[u'y_bc_floor_close'] = F[u'y_floor_ms'][1] - F[u'y_floor_ms'][2]
F[u'y_c_floor_eq_init'] = F[u'y_floor_ms'][2] - F[u'y_ans_ms'][2]
F[u'y_b_floor_gap'] = F[u'y_ans_ms'][1] - F[u'y_floor_ms'][1]
# 零方差兜底: B/C 写成散文 MUST, D 写进 max() 里
F[u'y_roundg'] = [occ(TXT[i], u'MUST be rounded to G seconds') for i in range(NSRC)]
F[u'y_gransym'] = [occ(TXT[i], u'G seconds') for i in range(NSRC)]
F[u'y_d_mad0'] = occ(TXT[3], u'max_ack_delay in the PTO period computation is set to 0')
F[u'y_d_floor'] = occ(TXT[3], u'PTO period MUST be at least kGranularity')
F[u'y_d_gran'] = dur_after(TXT[3], u'Section 6.1.2 recommends a value of ')[0]
F[u'y_d_gran_unit'] = dur_after(TXT[3], u'Section 6.1.2 recommends a value of ')[2]
F[u'y_d_kinit'] = num_after(TXT[3], u'Section 6.2.2 is ')
F[u'y_d_kinit_lit'] = occ(TXT[3], u'is 333 ms')
F[u'y_bc_kdef'] = [num_after(TXT[i], u'where K = ') for i in range(NSRC)]
F[u'y_c_kdef'] = F[u'y_bc_kdef'][2]
F[u'y_b_kdef'] = F[u'y_bc_kdef'][1]
F[u'y_b_kdef_close'] = F[u'y_b_kdef'] - F[u'y_c_kdef']
F[u'y_d_k'] = num_before(TXT[3], u'*rttvar')
F[u'y_k_close'] = F[u'y_c_kdef'] - F[u'y_d_k']
F[u'y_klit_sp'] = F[u'lit_4k_rttvar']
F[u'y_klit_ns'] = F[u'lit_4xrttvar']
F[u'y_klit_close'] = [F[u'lit_4k_rttvar'][i] - F[u'lit_4xrttvar'][i] for i in range(NSRC)]
F[u'y_half_c'] = num_after(TXT[2], u'RTTVAR <- R/')
F[u'y_half_b'] = num_after(TXT[1], u'RTTVAR <- R/')
F[u'y_half_d'] = num_after(TXT[3], u'rttvar = kInitialRtt / ')
F[u'y_half_close'] = F[u'y_half_c'] - F[u'y_half_d']
F[u'y_b_c_half_close'] = F[u'y_half_b'] - F[u'y_half_c']
# C 的 (5.7) 回退值 ⇎ D 的 PTO 复算
F[u'y_c_revert_ms'] = dur_after(TXT[2], u're-initialized to ')[0]
F[u'y_c_revert_wrap'] = dur_after(TXT[2], u're-initialized to ')[3]
F[u'y_c_revert_eq_a'] = F[u'y_c_revert_ms'] - F[u'y_ans_ms'][0]
F[u'y_c_revert_eq_b'] = F[u'y_c_revert_ms'] - F[u'y_ans_ms'][1]
F[u'y_c_may_still'] = occ(TXT[2], u'MAY still use')
F[u'y_b_may_still'] = occ(TXT[1], u'MAY still use')
F[u'y_c_may_still_fold'] = occ(FO[2], u'MAY still use this value')
F[u'y_c_lower_note'] = occ(TXT[2], u'Rationale for Lowering the Initial RTO')
F[u'y_a_varfrom'] = occ(TXT[0], u'will result in this RTO')
F[u'y_bc_varfrom'] = [occ(TXT[i], u'will result in this RTO') for i in range(NSRC)]
# PTO 复算(全部由面内现读的 333/1/4 三枚常数导出, 一个都不手填)
F[u'y_d_pto_exact'] = F[u'y_ans_ms'][3] + (F[u'y_d_k'] * F[u'y_ans_ms'][3]) // 2
F[u'y_d_pto_int'] = F[u'y_ans_ms'][3] + F[u'y_d_k'] * (F[u'y_ans_ms'][3] // 2)
F[u'y_d_claim_ms'] = CLAIM[3]
F[u'y_d_gap_exact'] = F[u'y_d_claim_ms'] - F[u'y_d_pto_exact']
F[u'y_d_gap_int'] = F[u'y_d_claim_ms'] - F[u'y_d_pto_int']
F[u'y_d_three'] = F[u'y_d_k'] // 2 + 1
F[u'y_d_gran_binds'] = 1 if F[u'y_d_k'] * F[u'y_ans_ms'][3] // 2 < F[u'y_d_gran'] else 0
F[u'y_d_var_int'] = F[u'y_ans_ms'][3] // 2
F[u'y_d_var_frac'] = F[u'y_ans_ms'][3] - 2 * F[u'y_d_var_int']
F[u'y_d_pto_spread'] = F[u'y_d_pto_exact'] - F[u'y_d_pto_int']
F[u'y_dur_ratio'] = F[u'dur_ms_hi'] // F[u'dur_ms_lo']
F[u'y_dur_rem'] = F[u'dur_ms_hi'] % F[u'dur_ms_lo']
# 四枚闭合位: 两端、上限、倍率全部由面内现读闭合, 不引外数
F[u'y_d_three_close'] = F[u'y_d_pto_exact'] - F[u'y_d_three'] * F[u'y_ans_ms'][3]
F[u'durlo_gran_close'] = F[u'dur_ms_lo'] - F[u'y_d_gran']
F[u'durhi_cap_close'] = F[u'dur_ms_hi'] - F[u'y_a_cap_ms']
F[u'y_cap_ratio_close'] = F[u'y_a_cap_ms'] - F[u'y_cap_ratio'] * F[u'y_cap_ref_ms']

# ---- 跨行 ⇎ 原面(采集侧同定义: 整篇空白折平后逐字面) ----
SN = [(u'init3', u'set RTO <- 3 seconds (per RFC 1122'), (u'init1', u'set RTO <- 1 second'),
      (u'floor', u'Whenever RTO is computed, if it is less than 1 second'),
      (u'rounded', u'RTO SHOULD be rounded up to 1 second'),
      (u'revert', u'MUST be re-initialized to 3 seconds'),
      (u'v3', u'(b)  RTO = 3 seconds'), (u'ms333', u'SHOULD be set to 333 milliseconds'),
      (u'claim1s', u'a PTO of 1 second'),
      (u'pto_eq', u'PTO = smoothed_rtt + max(4*rttvar, kGranularity) + max_ack_delay'),
      (u'half', u'rttvar = kInitialRtt / 2'), (u'tcpinit', u"as recommended for TCP's initial"),
      (u'cite6298', u'see Section 2 of [RFC6298]'), (u'granrec', u'recommends a value of 1 ms'),
      (u'backoff5', u'the "backing off" on repeated')]
for k, s in SN:
    F[u's_' + k] = [occ(TXT[i], s) for i in range(NSRC)]
    F[u's_' + k + u'_fold'] = [occ(FO[i], u' '.join(s.split())) for i in range(NSRC)]
    F[u'wrap_gap_' + k] = [F[u's_' + k + u'_fold'][i] - F[u's_' + k][i] for i in range(NSRC)]
F[u'wrap_pin_n'] = len(SN)
F[u'wrap_pin_hit'] = len([1 for k, _ in SN if max(F[u'wrap_gap_' + k]) > 0])
F[u'wrap_gap_total'] = sum([sum(F[u'wrap_gap_' + k]) for k, _ in SN])

# ---- 语汇 ----
WK = [(u'rto', u'RTO'), (u'pto', u'PTO'), (u'retrans', u'retransmi'), (u'rtt', u'RTT'),
      (u'rtt_low', u'rtt'), (u'clock', u'clock granularity'), (u'gran', u'granularity'),
      (u'initrto_cap', u'Initial RTO'), (u'initrto_low', u'initial RTO'), (u'timer', u'timer'),
      (u'persist', u'persistent'), (u'probe', u'probe'), (u'slowstart', u'slow start'),
      (u'congest', u'congestion control'), (u'variance', u'variance'), (u'backoff_word', u'back off')]
for k, s in WK:
    four(u'v_' + k, lambda i, s=s: occ(TXT[i], s))
F[u'y_case_gap_rttvar'] = [F[u'lit_rttvar_u'][i] - F[u'lit_rttvar_l'][i] for i in range(NSRC)]
F[u'y_name_family'] = [F[u'lit_srtt'][i] + F[u'lit_rttvar_u'][i] for i in range(NSRC)]
F[u'y_name_family_l'] = [F[u'lit_smoothed'][i] + F[u'lit_rttvar_l'][i] for i in range(NSRC)]

# ---- 义务词 ----
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED'):
    four(u'u_' + w.replace(u' ', u'_').lower(), lambda i, w=w: occ(TXT[i], w))
F[u'oblig_up'] = [F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i] for i in range(NSRC)]


def wtok(s):
    out, buf = [], []
    for ch in s + u' ':
        if ch in ALW or ch == u'_':
            buf.append(ch)
        else:
            if buf:
                out.append(u''.join(buf))
                buf = []
    return out


def wcount(s, word):
    return len([x for x in wtok(s) if x == word])


for w in (u'must', u'should', u'may'):
    four(u'l_' + w, lambda i, w=w: wcount(TXT[i], w))
F[u'oblig_low'] = [F[u'l_must'][i] + F[u'l_should'][i] + F[u'l_may'][i] for i in range(NSRC)]
four(u'rfc2119_ref', lambda i: occ(TXT[i], u'2119'))
four(u'key_words_boiler', lambda i: occ(TXT[i], u'key words') + occ(TXT[i], u'Key words'))
F[u'y_secw_must_not'] = [occ(TXT[i], u'MUST NOT', OFF[i][SECW[i][0]], wend(i)) for i in range(NSRC)]
F[u'y_oblig_win'] = [F[u'y_secw_may'][i] + F[u'y_secw_must'][i] + F[u'y_secw_should'][i]
                     for i in range(NSRC)]

# ---- 身份 ----
HK = [(u'cat_std', u'Category: Standards Track'), (u'cat_exp', u'Category: Experimental'),
      (u'cat_info', u'Category: Informational'), (u'cat_hist', u'Category: Historic'),
      (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'), (u'issn_hdr', u'ISSN:'),
      (u'rfc_hdr', u'RFC Internet Engineering Task Force'), (u'braden_foot', u'Braden'),
      (u'editor_hdr', u'Editor'), (u'req_rc', u'Request for Comments:')]
for k, s in HK:
    four(k, lambda i, s=s: occ(TXT[i], s))
four(u'obsoleted_by', lambda i: occ(LOW[i], u'obsoleted by'))
four(u'errata', lambda i: occ(LOW[i], u'errata'))
four(u'std_lvl', lambda i: occ(TXT[i], u'Standards Track'))


def cite_occ(t, n, sp=True):
    """'RFC'[至多一个空格]编号, 且编号后不是数字(采集侧写成 RFC ?n 加“后不是数字”的前瞻)。"""
    out, k = 0, t.find(u'RFC')
    while k >= 0:
        p = k + 3
        if sp and p < len(t) and t[p] == u' ':
            p += 1
        if t[p:p + len(n)] == n and (p + len(n) >= len(t) or t[p + len(n)] not in DIG):
            out += 1
        k = t.find(u'RFC', k + 1)
    return out


for n in (u'1122', u'1123', u'2988', u'6298', u'9002', u'793'):
    four(u'cite_' + n, lambda i, n=n: cite_occ(TXT[i], n))
four(u'cite_1122_sp', lambda i: occ(TXT[i], u'RFC 1122'))
four(u'cite_1122_ns', lambda i: occ(TXT[i], u'RFC1122'))
four(u'cite_ns_1122', lambda i: F[u'cite_1122_sp'][i] + F[u'cite_1122_ns'][i])
F[u'y_cite_ledger_1122'] = [F[u'cite_1122'][i] - F[u'cite_1122_sp'][i] - F[u'cite_1122_ns'][i]
                            for i in range(NSRC)]

# ---- 搬运账(归一只留 a-z0-9; 排序两指针求交, 不用集合运算符) ----
GE40, GE40N, GERAW = [], [], []
for shell, store in ((True, GE40), (False, GE40N)):
    for i in range(NSRC):
        seen = {}
        for l in LST[i]:
            if not shell and (is_hdr(l) or is_foot(l)):
                continue
            n = pnorm(l)
            if len(l.strip()) >= 40 and len(n) >= 40:
                seen[n] = 1
        store.append(sorted(seen))
for i in range(NSRC):
    seen = {}
    for l in LST[i]:
        if len(l.strip()) >= 40 and len(pnorm(l)) >= 40:
            seen[l] = 1
    GERAW.append(sorted(seen))


def m_iset(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out


def m_isub(a, b):
    """a 里有、b 里没有(两指针)。"""
    i = j = 0
    out = []
    while i < len(a):
        while j < len(b) and b[j] < a[i]:
            j += 1
        if j < len(b) and b[j] == a[i]:
            i += 1
            continue
        out.append(a[i])
        i += 1
    return out


def m_union(*sets):
    seen = {}
    for s in sets:
        for x in s:
            seen[x] = 1
    return len(seen)


F[u'lines_ge40'] = [len(s) for s in GE40]
F[u'lines_ge40_nos'] = [len(s) for s in GE40N]
for suf, SS in ((u'', GE40), (u'_nos', GE40N)):
    for a in range(NSRC):
        for b in range(a + 1, NSRC):
            F[u'share_%s%s%s' % (TAGS[a].lower(), TAGS[b].lower(), suf)] = len(m_iset(SS[a], SS[b]))
    F[u'union_abc' + suf] = m_union(SS[0], SS[1], SS[2])
    F[u'union_abcd' + suf] = m_union(SS[0], SS[1], SS[2], SS[3])
    F[u'only_b' + suf] = len([x for x in SS[1] if x not in SS[0] and x not in SS[2]])
    F[u'only_c' + suf] = len([x for x in SS[2] if x not in SS[0] and x not in SS[1] and x not in SS[3]])
    F[u'only_d' + suf] = len([x for x in SS[3] if x not in SS[0] and x not in SS[1] and x not in SS[2]])
    abc = m_iset(m_iset(SS[1], SS[2]), SS[3])
    abd = m_iset(m_iset(SS[1], SS[2]), SS[0])
    F[u'share_bc_plus' + suf] = len(abc) + len(abd) - len(m_iset(abc, abd))
F[u'shell_delta'] = [F[u'lines_ge40'][i] - F[u'lines_ge40_nos'][i] for i in range(NSRC)]
F[u'union_delta'] = F[u'union_abcd'] - F[u'union_abc']
F[u'BC_inter'] = len(m_iset(GE40[1], GE40[2]))
F[u'ABC_inter'] = len(m_iset(m_iset(GE40[0], GE40[1]), GE40[2]))
F[u'abcd_incl'] = (F[u'lines_ge40'][0] + F[u'lines_ge40'][1] + F[u'lines_ge40'][2] + F[u'lines_ge40'][3]
                   - F[u'share_ab'] - F[u'share_ac'] - F[u'share_ad'] - F[u'share_bc'] - F[u'share_bd']
                   - F[u'share_cd']
                   + len(m_iset(m_iset(GE40[0], GE40[1]), GE40[2]))
                   + len(m_iset(m_iset(GE40[0], GE40[1]), GE40[3]))
                   + len(m_iset(m_iset(GE40[0], GE40[2]), GE40[3]))
                   + len(m_iset(m_iset(GE40[1], GE40[2]), GE40[3]))
                   - len(m_iset(m_iset(m_iset(GE40[0], GE40[1]), GE40[2]), GE40[3])))
F[u'abcd_close'] = F[u'abcd_incl'] - F[u'union_abcd']
# 归一档 ⇎ 字节档: 同一份搬运账在对换行不敏感⇎逐字节两种口径下各算一次
F[u'y_bc_byte_shared'] = len(m_iset(GERAW[1], GERAW[2]))
F[u'y_bc_norm_only'] = F[u'share_bc'] - F[u'y_bc_byte_shared']
F[u'y_a_sent_in_bc'] = [occ(TXT[i], u'The smoothed variance is to be') for i in range(NSRC)]
F[u'y_a_rule_line'] = LST[0][max([n for n, l in enumerate(LST[0]) if RULE[u'A'] in l])]
F[u'y_a_rule_in_bc'] = [len([1 for l in LST[i] if pnorm(F[u'y_a_rule_line']) in pnorm(l)])
                        for i in (1, 2, 3)]
F[u'y_only_bcd'] = F[u'only_b'] + F[u'only_c'] + F[u'only_d']

# ---- B ⇎ C 条款逐行对照(废止链上的标点差) ----
F[u'y_floor_lines'] = [len([l for l in LST[i] if u'rounded up' in l]) for i in range(NSRC)]
FL = [(i, n, l) for i in range(NSRC) for n, l in enumerate(LST[i]) if u'rounded up' in l]
FB = [l for i, n, l in FL if i == 1]
FC = [l for i, n, l in FL if i == 2]
F[u'floor_pair'] = [len(FB), len(FC)]
F[u'floor_same_bytes'] = [len([1 for a, b in zip(FB, FC) if a == b])]
F[u'floor_same_norm'] = [len([1 for a, b in zip(FB, FC) if pnorm(a) == pnorm(b)])]
F[u'floor_diff_bytes'] = [len([1 for a, b in zip(FB, FC) if a != b])]
F[u'floor_close'] = F[u'floor_same_norm'][0] - F[u'floor_same_bytes'][0] - F[u'floor_diff_bytes'][0]
AI = []
for i in (1, 2):
    hits = [n for n, l in enumerate(LST[i]) if u'Whenever RTO is computed' in l]
    assert hits, TAGS[i]
    AI.append(hits[-1])
PAIR = [(LST[1][AI[0] + k], LST[2][AI[1] + k]) for k in range(4)
        if AI[0] + k < len(LST[1]) and AI[1] + k < len(LST[2])]
F[u'align_n'] = len(PAIR)
F[u'align_same_bytes'] = len([1 for a, b in PAIR if a == b])
F[u'align_punct_only'] = len([1 for a, b in PAIR if a != b and pnorm(a) == pnorm(b)])
F[u'align_norm_diff'] = len([1 for a, b in PAIR if pnorm(a) != pnorm(b)])
F[u'align_close'] = (F[u'align_same_bytes'] + F[u'align_punct_only'] + F[u'align_norm_diff']
                     - F[u'align_n'])
F[u'align_char_delta'] = sum(len(b) - len(a) for a, b in PAIR)
F[u'align_comma'] = len([1 for a, b in PAIR if b.count(u',') - a.count(u',') == 1])
F[u'y_clause_pair_n'] = len(PAIR)

# ---- 锚候选行 ----
NLITS = (u'RTO', u'PTO', u'3 seconds', u'1 second', u'333', u'kGranularity', u'kInitialRtt')
four(u'num_lines', lambda i: len([l for l in LST[i] if len(l.strip()) >= 55
                                  and any(x in l for x in NLITS)]))
for i in range(NSRC):
    F[u'num_lines_' + TAGS[i].lower()] = F[u'num_lines'][i]

# ---- 锚池: 按“这条锚在几份文书里逐字再现”分层 ----
SPECIAL = (u'RTO', u'PTO', u'3 seconds', u'1 second', u'333', u'SRTT', u'RTTVAR', u'kGranularity',
           u'kInitialRtt', u'Jacobson', u'Karn', u'backing off', u'initial RTO', u'rounded up',
           u'milliseconds', u'smoothed_rtt')
POOL = set()
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if pnorm(l):
            POOL.add((t, l))
POOL = sorted(POOL)
CROSS = dict(((t, x), sum(1 for k in range(NSRC) if pnorm(x) in FAN[k])) for (t, x) in POOL)
POOLC = [(t, CROSS[(t, x)], x) for (t, x) in POOL]
F[u'pool_n'] = len(POOLC)
four(u'pool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
for n in range(1, NSRC + 1):
    F[u'pool_%d' % n] = len([p for p in POOLC if p[1] == n])
F[u'pool_tiers'] = [F[u'pool_%d' % n] for n in range(1, NSRC + 1)]
F[u'pool_close'] = sum(F[u'pool_tiers']) - F[u'pool_n']
F[u'pool_maxlen'] = max(len(p[2]) for p in POOLC)


def ATOMSEL(kind, tag, *needles):
    ok = (lambda n: n == 1) if kind == u'own' else (lambda n: n == int(kind))
    got = [p for p in POOLC if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
    if not got:
        got = [p for p in POOLC if p[0] == tag and all(x in p[2] for x in needles)]
    assert got, (kind, tag, needles)
    return max(got, key=lambda x: (len(x[2]), x[2]))


USEDATOM = []


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    USEDATOM.append(x[2])
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


CLOSK = sorted([k for k in F if (u'_close' in k or u'_resid' in k or u'_ledger' in k)
                and isinstance(F[k], (int, float)) and not isinstance(F[k], bool)])
F[u'scalar_clos_n'] = len(CLOSK)
F[u'scalar_clos_sum'] = sum(F[k] for k in CLOSK)
F[u'scalar_clos_list'] = CLOSK
F[u'list_clos_n'] = len([k for k in F if (u'_close' in k or u'_ledger' in k) and isinstance(F[k], list)])

# ---- 面内现读数之间的恒等式(全归零, 由门槛重算) ----
ZID = [(u"B63V('y_ans_max')-B63V('y_ans_ratio')*B63V('y_ans_min')-B63V('y_ans_rem')",
        u'跨度: 3000=9×333+3'),
       (u"B63V('y_d_pto_exact')-B63V('y_d_three')*B63V('y_ans_ms', 3)", u'坍缩: PTO=3×初始 RTT'),
       (u"B63V('y_d_claim_ms')-B63V('y_d_pto_exact')-B63V('y_d_gap_exact')", u'宣称⇎实数复算'),
       (u"B63V('y_d_claim_ms')-B63V('y_d_pto_int')-B63V('y_d_gap_int')", u'宣称⇎取整复算'),
       (u"B63V('y_d_pto_spread')-(B63V('y_d_gap_int')-B63V('y_d_gap_exact'))", u'两种取法之差=两枚差之差'),
       (u"B63V('y_ans_ms', 3)-2*B63V('y_d_var_int')-B63V('y_d_var_frac')",
        u'333 是奇数: 半值取整必留余数(333−2×166−1)'),
       (u"B63V('y_d_k')-B63V('y_c_kdef')", u'C 写作符号 K、D 写作字面 4, 两处现读同值'),
       (u"B63V('y_b_kdef')-B63V('y_c_kdef')", u'被废止者⇎废止者: K 的定义值同'),
       (u"B63V('y_klit_close', 0)+B63V('y_klit_close', 1)+B63V('y_klit_close', 2)+B63V('y_klit_close', 3)",
        u'乘号带空格⇎不带空格: 四份里两种拼法各计一次, 逐份相等'),
       (u"B63V('y_half_c')-B63V('y_half_d')", u'首个样本⇎无样本: 方差除数同为 2'),
       (u"B63V('y_half_b')-B63V('y_half_c')", u'B⇎C 的方差除数同值'),
       (u"B63V('y_c_revert_eq_a')", u'C 的 (5.7) 回退值=A 的初值 3000 毫秒'),
       (u"B63V('y_c_revert_eq_b')", u'同一枚 3000 也是 B 的初值'),
       (u"B63V('y_bc_floor_close')", u'B⇎C 的上取整地板同值(1000 毫秒)'),
       (u"B63V('y_c_floor_eq_init')", u'C 的地板恰等于它自己的初值: 降无可降'),
       (u"B63V('dur_ms_hi')-B63V('y_dur_ratio')*B63V('dur_ms_lo')-B63V('y_dur_rem')",
        u'值域两端之比(240000=240000×1+0)'),
       (u"B63V('dur_ms_lo')-B63V('y_d_gran')", u'值域下界=D 面内现读的时钟粒度'),
       (u"B63V('dur_ms_hi')-B63V('y_a_cap_ms')", u'值域上界=A 面内现读的 RTO 上限'),
       (u"B63V('y_a_cap_ms')-B63V('y_cap_ratio')*B63V('y_cap_ref_ms')-B63V('y_cap_rem')",
        u'上限之比: 240 秒 ⇎ 60 秒'),
       (u"B63V('y_ans_ms', 2)-B63V('y_claim_ms', 3)", u'C 的答数=D 宣称的 PTO(1 秒)'),
       (u"B63V('y_claim_distinct')-2", u'按宣称档只有两值: 3000⇎1000'),
       (u"B63V('align_close')", u'条款对照三分档穷尽'),
       (u"B63V('floor_close')", u'上取整条款字节档⇎归一档穷尽'),
       (u"B63V('a_1122_resid')", u'A 的自编号=页眉+抬头行'),
       (u"B63V('ff_foot_sum')", u'换页符总数=页脚行数(三份分页档)'),
       (u"B63V('trail_foot_sum')", u'行尾空格行数=页脚行数'),
       (u"B63V('ietf_vs_ff', 0)", u'89 三秒: 页脚左侧印 IETF 的行数=换页符数'),
       (u"B63V('hdr_ledger_sum')", u'页眉两档之和=页眉总数'),
       (u"B63V('abcd_close')", u'四份长行容斥=并集实数'),
       (u"B63V('pool_close')", u'锚池分层穷尽')]
F[u'x_ident_n'] = len(ZID)
# --- SCAN END ---

# ---------- DERIV 登记与正文模板 ----------
K, ZERO, COLL, SEENX = {}, [], {}, {}
G, LINES, MISSING = {}, [], []
FN = u'B63V'


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K.setdefault(s, (expr, note))


def dump_deriv():
    out = dict((k, v[0]) for k, v in K.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {u'B63V': BB63}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([tuple(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


def V(name, i=None, note=u''):
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


def CLOS(key, note):
    return V(key, None, note)


def CLOS4(key, note):
    return u' ⇎ '.join(V(key, i, u'%s·%s' % (note, LB[t])) for i, t in enumerate(TAGS))


TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


def JOIN(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LB[t])) for i, t in enumerate(TAGS))


BB63 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B63V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
BARE = re.compile(r'^[0-9+\-*/().,\s]*$')
HELP = re.compile(u"^(V|JOIN|CLOS|CLOS4|TOK|AT)\\(")
_Q = u'"\''


def _split_top(s):
    out, buf, d, q = [], u'', 0, None
    for ch in s:
        if q:
            buf += ch
            if ch == q:
                q = None
            continue
        if ch in _Q:
            q = ch
            buf += ch
            continue
        if ch in u'([{':
            d += 1
        elif ch in u')]})':
            d -= 1
        if ch == u',' and d == 0:
            out.append(buf)
            buf = u''
            continue
        buf += ch
    out.append(buf)
    return [x.strip() for x in out]


def _unlit(x):
    t = x[1:] if x[:1] == u'u' else x
    assert t[0] in _Q and t[-1] == t[0], x
    return t[1:-1]


def _inline(t):
    while True:
        i = t.find(u'{EXPR(')
        if i < 0:
            break
        j = t.index(u'(', i)
        d, k = 0, j
        q = None
        while True:
            c = t[k]
            if q:
                if c == q:
                    q = None
                k += 1
                continue
            if c in _Q:
                q = c
                k += 1
                continue
            if c == u'(':
                d += 1
            elif c == u')':
                d -= 1
                if d == 0:
                    break
            k += 1
        if t[k + 1] != u'}':
            raise AssertionError((u'EXPRSCAN', repr(t[i:k + 4]), repr(t[j + 1:k])))
        args = _split_top(t[j + 1:k])
        assert len(args) == 3, args
        val = eval(args[0], {u'F': F, u'B63V': BB63, u'len': len, u'max': max, u'min': min,
                             u'round': round, u'repr': repr})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]

    def rep(m):
        c = m.group(1).strip()
        if HELP.match(c):
            return eval(c, {u'V': V, u'JOIN': JOIN, u'CLOS': CLOS, u'CLOS4': CLOS4, u'TOK': TOK, u'AT': AT})
        if u'B63V(' not in c:
            return m.group(0)
        assert BARE.match(BCALL.sub(u'0', c)), c
        val = eval(c, {u'B63V': BB63})
        reg(str(val), c.strip(), c.strip())
        return str(val)
    return re.sub(r'\{([^{}]*)\}', rep, t)


class _Ctx(dict):
    def __missing__(self, k):
        MISSING.append(k)
        return u'§' + k


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + _inline(tmpl)).format_map(_Ctx(dict(G, **kw))))

# ---------- 锚(位置由池现推, 不手打) ----------
G[u'A_rule'] = AT(u'own', u'A', u'(b)  RTO = 3 seconds')
G[u'A_varinit'] = AT(u'own', u'A', u'will result in this RTO')
G[u'A_cap'] = AT(u'own', u'A', u'MSL, i.e., 240')
G[u'A_msl'] = AT(u'own', u'A', u'value of 2 minutes for MSL')
G[u'A_reasm'] = AT(u'own', u'A', u'between 60 seconds and 120')
G[u'A_frac'] = AT(u'own', u'A', u'less than 0.5 seconds')
G[u'A_backoff'] = AT(u'own', u'A', u'exponential backoff')
G[u'A_karn'] = AT(u'own', u'A', u"Karn's algorithm and Jacobson's")
G[u'A_rtt0'] = AT(u'own', u'A', u'RTT = 0 seconds')
G[u'B_init3'] = AT(u'own', u'B', u'set RTO <- 3 seconds (per RFC 1122')
G[u'B_heart'] = AT(u'own', u'B', u'between 2.5 seconds and 3')
G[u'B_sum'] = AT(u'2', u'B', u'RTO <- SRTT + max (G, K*RTTVAR)')
G[u'B_var'] = AT(u'2', u'B', u'RTTVAR <- R/2')
G[u'C_var'] = AT(u'2', u'C', u'RTTVAR <- R/2')
G[u'C_sum'] = AT(u'2', u'C', u'RTO <- SRTT + max (G, K*RTTVAR)')
G[u'B_kdef'] = AT(u'2', u'B', u'where K = 4')
G[u'B_roundg'] = AT(u'2', u'B', u'MUST be rounded to G seconds')
G[u'B_cap60'] = AT(u'2', u'B', u'provided it is at least 60')
G[u'B_floor'] = AT(u'2', u'B', u'(2.4) Whenever RTO is computed')
G[u'B_rounded'] = AT(u'2', u'B', u'RTO SHOULD be rounded up to 1 second')
G[u'C_init1'] = AT(u'own', u'C', u'set RTO <- 1 second')
G[u'C_prev3'] = AT(u'own', u'C', u'used an initial')
G[u'C_maystill'] = AT(u'own', u'C', u'MAY still use')
G[u'C_revert'] = AT(u'own', u'C', u'MUST be re-initialized to 3 seconds')
G[u'C_gran'] = AT(u'2', u'C', u'There is no requirement for the clock granularity')
G[u'C_appendix'] = AT(u'own', u'C', u'Rationale for Lowering the Initial RTO')
G[u'C_floor'] = AT(u'2', u'C', u'(2.4) Whenever RTO is computed')
G[u'C_backoff'] = AT(u'own', u'C', u'the "backing off" on repeated')
G[u'D_rule333'] = AT(u'own', u'D', u'SHOULD be set to 333 milliseconds')
G[u'D_claim'] = AT(u'own', u'D', u'a PTO of 1 second')
G[u'D_sum'] = AT(u'own', u'D', u'PTO = smoothed_rtt + max(4*rttvar')
G[u'D_half'] = AT(u'own', u'D', u'rttvar = kInitialRtt / 2')
G[u'D_granfloor'] = AT(u'own', u'D', u'PTO period MUST be at least kGranularity')
G[u'D_granrec'] = AT(u'own', u'D', u'recommends a value of 1 ms')
G[u'D_kinirtt'] = AT(u'own', u'D', u'Section 6.2.2 is 333 ms')
G[u'D_mad0'] = AT(u'own', u'D', u'computation is set to 0')
G[u'D_cite6298'] = AT(u'own', u'D', u'see Section 2 of [RFC6298]')
G[u'B_backoff'] = AT(u'2', u'B', u'"backing off" on repeated')

# ---------- 正文 ----------
LINE(u'🧭', u"四源字节 {JOIN('bytes')} ⇎ 面内字符 {JOIN('chars')} ⇎ 原文件行 {JOIN('lines')} ⇎ 非空行 {JOIN('nonblank')} ⇎ 最长行 {JOIN('maxlen')} 列: 89 三秒 ⇎ 00 三秒 ⇎ 11 一秒 ⇎ 21 三百三。量级差全在“是不是专文”——89 是整本主机需求书, 体量 {B63V('bytes',0)//B63V('bytes',1)} 倍于 00, 答数只写在 §{V('sec_head',0)} 的 {V('sec_len',0)} 字符里(窗行号 {V('sec_a',0)}–{V('sec_b',0)}); 四份答题窗 {JOIN('sec_len')} 字符几乎等长, 两端只差 {B63V('sec_len',0)-B63V('sec_len',3)}, 窗行号 {V('sec_a',1)}–{V('sec_b',1)} ⇎ {V('sec_a',2)}–{V('sec_b',2)} ⇎ {V('sec_a',3)}–{V('sec_b',3)}, 窗标题 {V('sec_head',1)} ⇎ {V('sec_head',2)} ⇎ {V('sec_head',3)}——后两份的标题只差一个句点。窗内子条目数 {JOIN('sec_sub')}(只有 89 那一节还分 (a)(b) 两子条), 答数 needle 在窗内命中 {JOIN('sec_hit')} 处。"
     u"版式分三代(同介质内部分裂): 无空格页眉“RFCnnnn”{JOIN('hdr_ns')} 行 ⇎ 带空格“RFC nnnn”{JOIN('hdr_sp')} 行 ⇎ 合计 {JOIN('hdr')} 行, 两式之和减页眉总数闭合 {CLOS('hdr_ledger_sum','页眉记账')}; 方括号页脚 {JOIN('foot_brk')} 行, 但只有 89 在页脚左侧重印机构名 {JOIN('foot_ietf')} 行, 后两份改印署名(Braden 字样 {JOIN('braden_foot')} 处 ⇎ Editor {JOIN('editor_hdr')} 处); 换页符 ⇎ 页脚行 ⇎ 行尾空格行三本账逐份相等(闭合 {CLOS('ff_foot_sum','换页符−页脚')} ⇎ {CLOS('trail_foot_sum','行尾空格−页脚')}), 唯机构名页脚减换页符 {JOIN('ietf_vs_ff')}——每页重印机构名的只有 89; 版面行 {JOIN('pagelines')} ⇎ 估计页 {JOIN('pages_est')}, 21 三百三三者全 {V('formfeed',3)}(不分页)。"
     u"编码层: UTF-8 BOM {CLOS4('bom','带 BOM')} 份 ⇎ 非 ASCII 码点 {JOIN('nonascii')} 枚(按 utf-8 硬解则 {JOIN('nonascii_raw')} 枚, BOM 自身被算进去)⇎ 字节减字符 {B63V('bytes',3)-B63V('chars',3)} 字节(全在 21 三百三); 回车符 {CLOS4('cr','回车符')} 枚 ⇎ 去换行后字符 {JOIN('chars_no_nl')}; 四份签名 {V('sig_distinct')} 种(blake2b 前 16 位)——同一问题的四份文书在字节层无一相同。")

LINE(u'📐', u"答数这一行是句子还是可解析的式子: 把“行首是 RTO/PTO、后接 <- 或 =”的行做结构解析(深度 0 的 ' + ' 分列、max 括号按逗号拆两参数), 四份各解出 {JOIN('y_sum_n')} 行, 形状 {V('y_sum_shape',0)} ⇎ {V('y_sum_shape',1)} ⇎ {V('y_sum_shape',2)} ⇎ {V('y_sum_shape',3)}。89 {V('y_sum_n',0)} 行: 它只给新建连接的初始化清单 {A_rule}, 同列还写着 {A_rtt0}, 算法本体让读者去执行 Karn 与 Jacobson {A_karn}——问“设多久”它答一个数, 问“这数怎么算出来”它不给式子。00 与 11 把同一条和式在本份内复写 {V('y_sum_n',1)}⇎{V('y_sum_n',2)} 遍 {B_sum}{C_sum}(首次样本时、每次更新后、以及“方差项须凑成 G 秒”那一遍 {B_roundg}); 21 只写 {V('y_sum_n',3)} 遍 {D_sum}。"
     u"符号 ⇎ 字面: 方差倍数在 00/11 是符号 K 并在下一行定义 {B_kdef}(现读 {V('y_b_kdef')} ⇎ {V('y_c_kdef')}, 两份彼此闭合 {CLOS('y_b_kdef_close','B⇎C 的 K')}), 在 21 直接写死成 {V('y_d_k')}, 与符号档闭合 {CLOS('y_k_close','符号 K ⇎ 字面 4')}; 字面 4 的两种拼法只在 21 同现且等量——紧凑 '4*rttvar' {JOIN('y_klit_ns')} 处 ⇎ 带空格 '4 * rttvar' {JOIN('y_klit_sp')} 处, 逐份差 {CLOS4('y_klit_close','两种拼法之差')}, 而 00/11 两种字面都不写({V('y_klit_ns',1)}⇎{V('y_klit_ns',2)} 处), 它只写符号 K*RTTVAR。"
     u"max() 的两参数换了序: 00/11 首格是时钟粒度 {V('y_sum_mfirst',2)} ⇎ 次格是方差项 {V('y_sum_msecond',2)}, 21 反过来 {V('y_sum_mfirst',3)} ⇎ {V('y_sum_msecond',3)}——乘积项占首格的位数 {JOIN('y_sum_var_first')}(只有 21 为 1): 取大档的“谁在第一格”随语言换代, 判据本身没换。和式项数 {JOIN('y_sum_nterms')} ⇎ 基底 {V('y_sum_base',1)}⇎{V('y_sum_base',3)} ⇎ 尾项 21 独有 {V('y_sum_tail',3)}({CLOS4('y_sum_tail_n','带尾项')} 份); 而 21 又在同一节把这一尾项在 Initial/Handshake 空间置零 {D_mad0}(现读 {V('y_d_mad0')} 处)——它多加的那一项在最需要初值的场合恰好吃掉一个自由度。"
     u"赋值符也换了一代: 'RTO <- ' {JOIN('lit_rtoarrow')} 处 ⇎ 'RTO = ' {JOIN('lit_rtovalue')} 处 ⇎ 两式合计 {JOIN('assign_forms')} ⇎ 差 {JOIN('assign_gap')}——89 只用等号 {V('lit_rtovalue',0)}, 00/11 各用箭头 {V('lit_rtoarrow',1)}⇎{V('lit_rtoarrow',2)}, 21 两者皆 {V('assign_forms',3)}(它的等号挂在 PTO 行首)。")

LINE(u'⚖', u"3 秒在废止链上搬了一次家, 数字却没搬: 89 把它写成新建连接的初值 {A_rule}, 并当场倒推方差 {A_varinit}(the smoothed variance is to be initialized to the value that will result in this RTO)——先定 RTO 再凑方差, 与后三份“先定方差再算 RTO”方向相反; 这句倒推只属 89, 逐份出现处 {JOIN('y_a_sent_in_bc')}(89 现读 {V('y_a_varfrom')} 处 ⇎ 后三份合计 {B63V('y_bc_varfrom',1)+B63V('y_bc_varfrom',2)+B63V('y_bc_varfrom',3)} 处)。00 原样接过 {B_init3}, 只补一句心跳定时器的实测值落在 2.5 与 3 秒之间、因此 2.5 秒的下界也可接受 {B_heart}; 11 把答数降到 1 秒 {C_init1}, 却在同页承认上一版用的是 3 秒 {C_prev3}, 并在 (5.7) 留一枚条件回退 {C_revert}(SYN 超时后传数据时必须重新置回 3 秒)。"
     u"于是 3 秒的字面在 11 里不减反增: '3 seconds' {JOIN('lit_3seconds')} 处, 而它的规范窗(§2 基本算法)内只 {V('secw_3seconds',2)} 处 ⇎ 窗外 {V('outw_3seconds',2)} 处——这一枚数被搬出答题的那一节, 落到 (5.7) 与附录 {C_appendix}; 窗档记 {JOIN('y_secw_threesec')} ⇎ 窗后 {JOIN('y_outw_threesec')}, 同一分档在 00 不成立({V('y_secw_threesec',1)} ⇎ {V('y_outw_threesec',1)})。附录字样在窗外的分布 {JOIN('y_outw_appendix')} ⇎ 窗内 {JOIN('y_secw_appendix')}。"
     u"复算核对: 11 的回退值面内现读 {V('y_c_revert_ms')} 毫秒, 与 89 的初值 {V('y_ans_ms',0)} 闭合 {CLOS('y_c_revert_eq_a','回退 ⇎ 89 初值')} ⇎ 与 00 的初值 {V('y_ans_ms',1)} 闭合 {CLOS('y_c_revert_eq_b','回退 ⇎ 00 初值')}——同一枚 3000 隔了 11 年又出现在废止它的那份文书里, 且现读不跨行 {V('y_c_revert_wrap')}。降下来写成明文许可 {C_maystill}(MAY still use this value, or any other value > 1 second): 现读 {V('y_c_may_still')} 处 ⇎ 00 {V('y_b_may_still')} 处 ⇎ 折平后 {V('y_c_may_still_fold')} 处(此句在 11 整行连着写); 降的理由另有专节 {C_appendix}(现读 {V('y_c_lower_note')} 处)。")

LINE(u'🔁', u"1 秒 ⇎ 333 毫秒, 两份“降低”文书降的是不同的量。11 把答数与自己的地板叠在一起: 初值 {V('y_ans_ms',2)} 毫秒 ⇎ (2.4) 上取整地板 {V('y_floor_ms',2)} 毫秒 {C_floor}, 闭合 {CLOS('y_c_floor_eq_init','地板 ⇎ 初值')}——降低到底即止; 00 的地板同为 {V('y_floor_ms',1)} 毫秒却比它自己的答数低 {CLOS('y_b_floor_gap','00 答数 − 地板')} 毫秒, 两份地板彼此闭合 {CLOS('y_bc_floor_close','B ⇎ C 地板')}; 同一句散文 {B_rounded} 在两份里服务相反的距离, 逐份地板行数 {JOIN('y_floor_lines')} ⇎ 'rounded up' {JOIN('lit_rounded')} 处 ⇎ 窗内 {JOIN('secw_rounded')} ⇎ 窗外 {JOIN('outw_rounded')}。"
     u"21 降的是初始 RTT {V('y_ans_ms',3)} 毫秒 {D_rule333}, 它的超时不写死而由本份三枚常数复算: 初值 {V('y_ans_ms',3)} ⇎ 方差倍数 {V('y_d_k')} ⇎ 粒度 {V('y_d_gran')}。半值取整档 {V('y_d_var_int')} 毫秒(333 是奇数, 余 {V('y_d_var_frac')} 落在半值上)⇒ {V('y_d_pto_int')} 毫秒; 半值不取整⇒ {V('y_d_pto_exact')} 毫秒。而它自己写的是 {D_claim}——宣称 {V('y_d_claim_ms')} 毫秒, 与实数档差 {V('y_d_gap_exact')} ⇎ 与取整档差 {V('y_d_gap_int')}, 两档彼此差 {V('y_d_pto_spread')} 毫秒; 库里没有任何一行写着这三毫秒, 'a PTO of 1 second' 全库只 {V('lit_onesecclaim',3)} 处。宣称档与答数档的枚数 {V('y_claim_distinct')} ⇎ {V('y_ans_distinct')} 种(差 {V('y_claim_vs_ans')}): 独立宣称句只属 21, 其余三份该档回落为答数, 故此档只在 21 上与复算对撞。"
     u"结构上这条和式在初值处坍缩成 {V('y_d_three')}×初始 RTT(闭合 {CLOS('y_d_three_close','PTO ⇎ 3×初值')}), 因为 max() 的粒度档不咬人({V('y_d_gran_binds')}: 4×半值 ≥ {V('y_d_gran')}), 兜底另有散文 {D_granfloor}(The PTO period MUST be at least kGranularity, 现读 {V('y_d_floor')} 处)。同一件兜底在 TCP 族是条款 {B_roundg}(the variance term MUST be rounded to G seconds): {JOIN('y_roundg')} 处 ⇎ 21 {V('y_roundg',3)} 处——散文 ⇎ max() 之别。粒度有没有数值也不同: 00/11 通篇只把 G 当秒数引用 {JOIN('y_gransym')} 处而不赋值, 21 给了 {D_granrec}({V('y_d_gran')} {V('y_d_gran_unit')}); 21 的初始 RTT 与首样本同形: {D_half}(除数现读 {V('y_half_d')})。")

LINE(u'🧪', u"时长要先归一才可比: 逐字符扫“数字串→空白→单位词”再折成毫秒, 四份取值集 {V('durms_a')} ⇎ {V('durms_b')} ⇎ {V('durms_c')} ⇎ {V('durms_d')} 毫秒(出现处含重复 {JOIN('durlit')} 处 ⇎ 去重后 {JOIN('durms_n')} 枚)。两端 {V('dur_ms_lo')} ⇎ {V('dur_ms_hi')} 毫秒, 比 {V('y_dur_ratio')} 倍余 {V('y_dur_rem')}, 两端各自闭合 {CLOS('durlo_gran_close','下界 ⇎ 粒度')} ⇎ {CLOS('durhi_cap_close','上界 ⇎ 89 上限')}——下界恰是 21 现读的 kGranularity {V('y_d_gran')}, 上界恰是 89 自述的 RTO 上限 {V('y_a_cap_ms')} 毫秒(由 {A_cap} 现读, 跨行标志 {V('y_a_cap_wrap')})。单位种类逐份 {JOIN('y_unit_n')} 种, 21 用 {V('y_unit_used',3)}; 'millisecond' 词形 {JOIN('unit_mill_word')} 处 ⇎ 'ms' {JOIN('unit_ms')} ⇎ 'second'族 {JOIN('unit_seconds')} 处。"
     u"两枚伪值必须点名: 其一, 小数被割——数字串从 0.5 与 2.5 的小数点后起读, 于是 5000 毫秒进了 89 与 00 的取值集({JOIN('y_dur_frac')} 枚这种 token ⇎ 11/21 {V('y_dur_frac',2)}⇎{V('y_dur_frac',3)} 枚), 值集 {V('y_dur_frac_vals')} ⇎ 其中只由割裂贡献的独立值 {JOIN('y_dur_frac_only')} 枚——89 与 00 谁也没说过 5 秒。其二, 数与单位被排版拆开: {JOIN('y_dur_wrap')} 枚 token 跨行, 其值 {V('y_dur_wrap_ms')}——89 的 240 秒上限 {A_cap} 与 00/11 的 60 秒上限 {B_cap60}(跨行标志 {V('y_bc_cap_wrap',1)}⇎{V('y_bc_cap_wrap',2)})全在这一档, 按行扫的复算者一个都读不到; 答数行自身跨行标志 {JOIN('y_ans_wrap')}、地板行 {JOIN('y_floor_wrap')} 全为零, 即四份的答数都可由行内直读, 只有上限读不到。另 {JOIN('y_dur_zero')} 枚 token 折出零值(“RTT = 0 seconds”{A_rtt0} 与一条被折行的小数尾), 其中跨行 {JOIN('y_dur_zero_wrap')} ⇎ 割小数 {JOIN('y_dur_zero_frac')}——零值 token 只属 89(现读 {JOIN('y_rtt0')} 处)。"
     u"窗档回答“这条时长属于哪个子系统”: 逐份窗内 {JOIN('y_dur_win_n')} 枚 ⇎ 窗外 {JOIN('y_dur_out_n')} 枚; 89 的窗内只剩 {V('y_dur_win',0)} ⇎ 窗外 {V('y_dur_out',0)}——那批窗外值里 60 ⇎ 120 秒属重组定时器(上限现读 {V('y_a_reass_hi_ms')} 毫秒, 数与单位跨行 {V('y_a_reass_hi_wrap')} 枚)⇎ 100 秒属“告知应用交付问题”的 R2 下限({V('y_a_r2_ms')} 毫秒) {A_reasm} ⇎ 小于 0.5 秒的下界 {A_frac}, 与重传超时无关——00 的取值全落在窗内({V('y_dur_win',1)} 枚档 {JOIN('y_dur_win_n')} ⇎ 窗外 {V('y_dur_out',1)} 枚), 11 则同值跨两档({V('y_dur_win',2)} ⇎ {V('y_dur_out',2)})。上限本身也换过答案: 89 说上限应为 2*MSL {A_msl}(倍数现读 {V('y_a_mult')} ⇎ MSL 字样 {V('y_a_msl_word')} 处)即 240 秒 ⇎ 00/11 的 (2.5) 只把上限写成一条许可——A maximum value MAY be placed on RTO provided it is at least 60 seconds {B_cap60}; 现读之比 {V('y_cap_ratio')} 倍余 {V('y_cap_rem')}(闭合 {CLOS('y_cap_ratio_close','240 ⇎ 60')} 毫秒), 这句在窗内命中 {JOIN('y_bc_cap_win')} 处 ⇎ 89 的上限句 {V('y_a_cap_win')} 处。")

LINE(u'⛓', u"折行通道(原面逐字面 ⇎ 整篇空白折平后逐字面): 本条 {V('wrap_pin_n')} 枚针里只有 {V('wrap_pin_hit')} 枚被排版折断——00 三秒把 backing off on repeated 那句拆在两行 {B_backoff}(原面 {JOIN('s_backoff5')} 处 ⇎ 折平 {JOIN('s_backoff5_fold')} 处, 逐份补回 {CLOS4('wrap_gap_backoff5','折行补回')}), 11 一秒同句整行连着写 {C_backoff}; 其余各针的逐档差合计 {V('wrap_gap_total')} 处, 即答题句 ⇎ 地板句 ⇎ 回退句 ⇎ 和式行 ⇎ 333 毫秒句 ⇎ 宣称句各档折行差 {V('wrap_gap_init3',0)} ⇎ {V('wrap_gap_init1',2)} ⇎ {V('wrap_gap_floor',1)} ⇎ {V('wrap_gap_revert',2)} ⇎ {V('wrap_gap_pto_eq',3)} ⇎ {V('wrap_gap_ms333',3)} ⇎ {V('wrap_gap_claim1s',3)} 全为零, 四份的答题句都整行连着写——本条的可判性不靠折平。"
     u"页眉是另一条隐形通道, 且只抬高“自编号被印多少次”: 89 面内 '1122' 子串 {V('a_self_lit')} 处 = 无空格页眉 {V('hdr_ns',0)} 行 + 抬头 Request for Comments 行 {V('a_shell_1122_sp')} 处, 残余 {CLOS('a_1122_resid','自编号残余')}; 引用档 RFC 1122 {JOIN('cite_1122')} 次里 89 的 {V('cite_1122',0)} 次全是自己页眉的复写(无空格式 {JOIN('cite_ns_1122')} ⇎ 带空格 {JOIN('cite_1122_sp')} 处), 三份账逐份闭合 {CLOS4('y_cite_ledger_1122','两式相加 ⇎ 总数')}。"
     u"锚池按“这条锚在几份文书里逐字再现”分层: 仅一份 {V('pool_1')} ⇎ 两份 {V('pool_2')} ⇎ 三份 {V('pool_3')} ⇎ 四份 {V('pool_4')} 条, 合计 {V('pool_n')} 条 ⇎ 逐份 {JOIN('pool_tag_n')}, 分层闭合 {CLOS('pool_close','池分层')}; 同一件事在搬运账上却是负的: 去页眉页脚只挪动长行集合 {CLOS4('shell_delta','含壳 − 去壳')} 行——每页重印的同一条页眉在集合里去重成一条。词频被壳抬高 {V('a_self_lit')} 处 ⇎ 集合只抬 {B63V('shell_delta',0)+B63V('shell_delta',1)+B63V('shell_delta',2)+B63V('shell_delta',3)} 行, 两档必须分别立键。")

LINE(u'📏', u"义务词体例在此仍不成差轴, 成轴的是“答数旁边有没有 MAY”: 全大写 MUST {JOIN('u_must')} ⇎ SHOULD {JOIN('u_should')} ⇎ MAY {JOIN('u_may')} ⇎ MUST NOT {JOIN('u_must_not')} 处, 其中 MUST ⇎ SHOULD ⇎ MAY 三词合计 {JOIN('oblig_up')} 处(MUST NOT 不在这一档); 小写词界档 must {JOIN('l_must')} ⇎ should {JOIN('l_should')} ⇎ may {JOIN('l_may')}, 合计 {JOIN('oblig_low')} 处——89 三秒的 {V('oblig_up',0)} 处大写是整本需求书的量, 不能与三份单主题文书比密度; 它给初值的那两行挂的是 SHOULD(全大写 SHOULD 面内 {V('u_should',0)} 处 ⇎ 窗内 {V('y_secw_should',0)} 处)。"
     u"可比的是窗口内的情态: 窗内 MUST {JOIN('y_secw_must')} ⇎ SHOULD {JOIN('y_secw_should')} ⇎ MAY {JOIN('y_secw_may')}, 三词合计 {JOIN('y_oblig_win')} ⇎ 窗外 MAY {JOIN('y_outw_may')} ⇎ 窗外 MUST {JOIN('y_outw_must')}。89 的答题窗内 MAY {V('y_secw_may',0)} 处(答数行只带 SHOULD, 见 {A_rule}); 11 在答数旁边就写着 MAY {C_maystill}({V('y_secw_may',2)} 处); 21 的窗内 {V('y_secw_may',3)} 处都在“复用的连接可以沿用上一条的最终 RTT”一句里({D_rule333} ⇎ {D_claim} 之间), 而窗内 MUST NOT 只有它写了 {V('y_secw_must_not',3)} 处。"
     u"RFC 2119 被引 {JOIN('rfc2119_ref')} 次 ⇎ 关键词样板 {JOIN('key_words_boiler')} 处: 89 三秒两者皆 {V('rfc2119_ref',0)}——它早于 2119, 却照用大写体例 {V('u_must',0)} 处 MUST; 21 三百三引 {V('rfc2119_ref',3)} 次最多。答数句的强度也换了代: 89 用 SHOULD(初始化清单), 00/11 把首次测量写成 MUST {B_sum}, 21 把 333 毫秒写成 SHOULD——同一格“初值”在四份里分别挂 SHOULD ⇎ MUST ⇎ MUST ⇎ SHOULD。")

LINE(u'🗓', u"变量名换了整套: SRTT {JOIN('lit_srtt')} ⇎ RTTVAR {JOIN('lit_rttvar_u')} ⇎ rttvar {JOIN('lit_rttvar_l')} ⇎ smoothed_rtt {JOIN('lit_smoothed')} ⇎ PTO {JOIN('lit_pto')} ⇎ RTO {JOIN('lit_rto')} 处; 大写族合计 {JOIN('y_name_family')} ⇎ 小写族合计 {JOIN('y_name_family_l')}, 同份两套之差 {JOIN('y_case_gap_rttvar')}——00/11 只有大写一套({V('lit_rttvar_l',1)}⇎{V('lit_rttvar_l',2)} 处小写), 21 只有小写一套({V('lit_rttvar_u',3)} 处大写), 89 三秒连变量名都不给(SRTT/RTTVAR 各 {V('lit_srtt',0)}⇎{V('lit_rttvar_u',0)} 处, 它只写 RTT 与 RTO)。"
     u"单位换代是可判的而不是修辞: 00/11 的粒度是散文里的符号 G({JOIN('y_gransym')} 处 G seconds 而不赋值), 21 的粒度是有名有数的 kGranularity {JOIN('lit_kgran')} 处, 窗内 {V('secw_kgran',3)} ⇎ 窗外 {V('outw_kgran',3)}——它的答数句根本不提粒度。'initial RTO' {JOIN('lit_inirto')} 处, 窗内 {JOIN('y_secw_inirto')} ⇎ 窗外 {JOIN('y_outw_inirto')}(11 一秒把这词组主要写在附录), 大写 Initial RTO {JOIN('v_initrto_cap')} 处 ⇎ 小写 {JOIN('v_initrto_low')}。"
     u"初值 ⇎ 首样本的形状却相同: 11 一秒首次测量写作 {C_var}(方差除数现读 {V('y_half_c')})⇎ 21 三百三无样本时写作 {D_half}(除数 {V('y_half_d')}, 同份内 'smoothed_rtt = kInitialRtt' 字面 {V('lit_smoothinit',3)} 处), 两处闭合 {CLOS('y_half_close','C ⇎ D 方差除数')} ⇎ 00⇎11 闭合 {CLOS('y_b_c_half_close','B ⇎ C 方差除数')}——QUIC 把 TCP 的“第一个样本如何初始化”拿来当“没有样本时”的答案, 名字换了、结构没换; 而 89 在同一份清单里把样本本身置零 {A_rtt0}(逐份现读 {JOIN('y_rtt0')} 处), 这是第三种填法。方差一词 {JOIN('v_variance')} 处 ⇎ 时钟字样 {JOIN('v_clock')} ⇎ granularity 字样 {JOIN('v_gran')} 处。"
     u"333 的两种拼法只在 21 内部对立: 333 milliseconds {V('lit_333full',3)} 处且全在窗内({V('secw_333full',3)} ⇎ 窗外 {V('outw_333full',3)}, 正文 §6.2.2 {D_rule333})⇎ 333 ms {V('lit_333ms',3)} 处全在窗外({V('outw_333ms',3)}, 附录里“Section 6.2.2 is 333 ms”{D_kinirtt}); 两种拼法同现的文书 {CLOS4('unit_both_333','全称 ⇎ 缩写同现')} 份, kInitialRtt 字样 {JOIN('lit_kinirtt')} 处 ⇎ 'TCP's initial RTO' 指涉 {JOIN('lit_tcpinitrto')} 处。")

LINE(u'🧾', u"身份与废止链是独立一轴, 且 89 三秒在轴外: 抬头 Category: Standards Track {JOIN('cat_std')} 处 ⇎ Experimental {JOIN('cat_exp')} ⇎ Informational {JOIN('cat_info')} ⇎ Historic {JOIN('cat_hist')}——1989 年的文书还没有这行抬头(Standards Track 字样 {JOIN('std_lvl')} 次是页眉重印的账)。废止链两枚头都只有 11 一秒印着: Obsoletes {JOIN('obs_hdr')} ⇎ Updates {JOIN('upd_hdr')}(它同时废止 00、更新 89), 而正文里 obsoleted by {JOIN('obsoleted_by')} 处——废止方向只能从抬头读, 从正文读不出; 勘误提及 {JOIN('errata')} 处(11 ⇎ 21 各 {V('errata',2)}⇎{V('errata',3)} 处指向站外, 站外事实不进门槛)。ISSN 头 {JOIN('issn_hdr')} 处只有后两份有 ⇎ Request for Comments: 行 {JOIN('req_rc')} 处四份都有。"
     u"引用网: RFC 2988 {JOIN('cite_2988')} ⇎ 6298 {JOIN('cite_6298')} ⇎ 1122(带空格)⇎ 1122(无空格) {JOIN('cite_1122_sp')} ⇎ 793 {JOIN('cite_793')} 次——21 三百三引 6298 {V('cite_6298',3)} 次却不引 2988({V('cite_2988',3)} 次), 它那句 {D_cite6298}(see Section 2 of [RFC6298])是全库唯一一条跨族(TCP ⇎ QUIC)的答数依据; 11 一秒引 2988 {V('cite_2988',2)} 次(废止对象)⇎ 引 1122 {V('cite_1122_sp',2)} 次(更新对象), 00 三秒引 1122 {V('cite_1122_sp',1)} 次(它接过的正是这一家), 而 21 引 1122 {V('cite_1122_sp',3)} 次——跨族文书不再引 1989 那一本。该引用句的原面 ⇎ 折平现读 {JOIN('s_cite6298')} ⇎ {JOIN('s_cite6298_fold')} 处(逐份折行差 {CLOS4('wrap_gap_cite6298','引用句折行')})。"
     u"含关键数字的长行(≥55 字符且含 RTO/PTO/3 seconds/1 second/333/kGranularity/kInitialRtt 之一) {JOIN('num_lines')} 行: 89 三秒 {V('num_lines_a')} 行最少(它只列初值), 21 三百三 {V('num_lines_d')} 行最多(它的超时侧要连 PTO、拥塞窗口与附录 pseudocode 一起写: PTO 字样 {V('v_pto',3)} 处 ⇎ persistent congestion {V('v_persist',3)} ⇎ probe {V('v_probe',3)} ⇎ slow start {V('v_slowstart',3)} ⇎ retransmi 词干 {V('v_retrans',3)} 处)。")

LINE(u'⇄', u"整行搬运(行长 ≥40、归一化只留 a-z0-9、排序后两指针求交): 89⇎00 {V('share_ab')} ⇎ 89⇎11 {V('share_ac')} ⇎ 89⇎21 {V('share_ad')} ⇎ 00⇎11 {V('share_bc')} ⇎ 00⇎21 {V('share_bd')} ⇎ 11⇎21 {V('share_cd')} 行。1989 与它的两位后继之间零共用行(89 的 {V('lines_ge40',0)} 条长行里没有一个字节出现在后三份里: 它把同一条规则写成 (b) 子条目 {A_rule}, 后继各自重写成整句), 三份两两交的三三同现 {V('ABC_inter')} ⇎ 00∩11 之外再同现 {V('share_bc_plus')} 行 ⇎ 00∩11 本身 {V('BC_inter')} 行。"
     u"连 00 逐字引它的那句也没复写——检验在库可判: 89 答数行整行归一后作为子串出现在后三份的行中 {V('y_a_rule_in_bc',0)}⇎{V('y_a_rule_in_bc',1)}⇎{V('y_a_rule_in_bc',2)} 次, 而它的倒推句只在本份 {JOIN('y_a_sent_in_bc')} 处。00⇎11 的 {V('share_bc')} 行才是真搬运, 但这一档是归一化的: 逐字节全等只有 {V('y_bc_byte_shared')} 行 ⇎ 归一后同值而字节不同 {CLOS('y_bc_norm_only','只在归一档相同')} 行(缩进与标点把“同一行”分成两档)。11⇎21 共用 {V('share_cd')} 行 ⇎ 00⇎21 只 {V('share_bd')} 行: QUIC 那一份与它引用的 11 一秒反而更像。"
     u"只在本份 {V('only_b')} ⇎ {V('only_c')} ⇎ {V('only_d')} 行(三份合计 {V('y_only_bcd')} 行); 四份并集 {V('union_abcd')} 行 ⇎ 三份 TCP 并集 {V('union_abc')} 行 ⇒ 加进 21 只多 {V('union_delta')} 行; 容斥给出的四份并集 {V('abcd_incl')} 行 ⇎ 实数 {V('union_abcd')} 行, 闭合 {CLOS('abcd_close','四份容斥')}; 长行基数逐份 {JOIN('lines_ge40')} ⇎ 去壳 {JOIN('lines_ge40_nos')} 行。"
     u"条款逐行对照(00 ⇎ 11 的 (2.4) 段): 对齐 {V('align_n')} 行里字节全等 {V('align_same_bytes')} ⇎ 仅标点差 {V('align_punct_only')} ⇎ 归一也不同 {V('align_norm_diff')}, 闭合 {CLOS('align_close','对照三分档')}; 那一处标点差正是 11 在 less than 1 second 之后补的逗号(00 的无逗号写法 {V('lit_commab',1)} 处 ⇎ 11 的带逗号写法 {V('lit_commac',2)} 处 ⇎ 两式在本份合计 {JOIN('floor_forms_gap')}), 字符净差 {V('align_char_delta')} ⇎ 含逗号的对齐行 {V('align_comma')} 行; 地板句 00 {V('floor_pair',0)} 行 ⇎ 11 {V('floor_pair',1)} 行, 逐行比 byte 同 {V('floor_same_bytes',0)} ⇎ 归一同 {V('floor_same_norm',0)} ⇎ 字节不同 {V('floor_diff_bytes',0)}, 闭合 {CLOS('floor_close','地板句对照')}。")

LINE(u'ℒ', u"方法 ⇒ 面对“同一问题四份文书”, 先问答数是句子还是可解析的式子: 本条把超时和式做成结构解析谓词(行首名 + <-/= + 深度 0 的 ' + ' 分列 + max 括号拆两参数), 于是“谁用符号谁用字面”“max 两参数换了序”“谁多一项”都有可判口径({JOIN('y_sum_shape')}), “K 是不是 4”另由定义行现读({V('y_c_kdef')} ⇎ {V('y_d_k')})。其次把单位归一做成扫描档而不是查表: 逐字符切数字串→空白→单位词, 顺手给每个 token 打上“跨行”⇎“小数割裂”两枚标志, 值域集 ⇎ 出现处两档并立({JOIN('durms_n')} 枚 ⇎ {JOIN('durlit')} 处), 再按规范窗切一刀(窗内 {JOIN('y_dur_win_n')} ⇎ 窗外 {JOIN('y_dur_out_n')}), 才读得出 89 三秒的 120 ⇎ 100 秒属于别的子系统。"
     u"再次把量测自身的失效做成键: 归一档 {V('share_bc')} ⇎ 字节档 {V('y_bc_byte_shared')} 两把尺同时登记; 宣称值 {V('y_d_claim_ms')} ⇎ 两种复算 {V('y_d_pto_exact')}⇎{V('y_d_pto_int')} 三键并立(差值 {V('y_d_gap_exact')} ⇎ {V('y_d_gap_int')} 毫秒恒不为零, 谁复算谁撞); 折行差只在 {V('wrap_pin_hit')}/{V('wrap_pin_n')} 枚针上非零 ⇎ 页眉差只在自编号一档抬高词频。{V('x_ident_n')} 条由面内现读数构成的恒等式(3000={V('y_ans_ratio')}×{V('y_ans_min')}+{V('y_ans_rem')} ⇎ {V('y_d_pto_exact')}={V('y_d_three')}×{V('y_ans_ms',3)} ⇎ {V('y_c_revert_ms')}={V('y_ans_ms',0)} ⇎ {V('dur_ms_hi')}={V('y_a_cap_ms')} ⇎ {V('dur_ms_lo')}={V('y_d_gran')} ⇎ {V('y_a_cap_ms')}={V('y_cap_ratio')}×{V('y_cap_ref_ms')})逐条送门槛重算, 标量闭合 {V('scalar_clos_n')} 枚 ⇎ 总账 {CLOS('scalar_clos_sum','闭合合计')} ⇎ 列表闭合 {V('list_clos_n')} 枚。")

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 四源各 {JOIN('chars')} 字符 ⇎ 答题窗各 {JOIN('sec_len')} 字符: 89 三秒的全篇是 00 三秒的 {B63V('chars',0)//B63V('chars',1)} 倍, 两窗却只差 {B63V('sec_len',0)-B63V('sec_len',1)} 字符。答数只占一行, 但“这一行是句子还是式子、单位怎么写、地板在哪里、兜底在散文 ⇎ 在 max()、宣称与复算差几毫秒”要跨四份并排读: 宣称 ⇎ 复算的三毫秒在库里零字面痕迹, 只能由 {V('y_ans_ms',3)}×{V('y_d_three')} 现算; 3 秒搬家要靠窗 ⇎ 窗外分档({V('secw_3seconds',2)} ⇎ {V('outw_3seconds',2)})才看得见; 00 ⇎ 11 的“只差一个逗号”要靠对照窗口逐行比({V('align_n')} 行里字节全等 {V('align_same_bytes')} ⇎ 仅标点差 {V('align_punct_only')}); 伪值 5000 毫秒要靠给 token 打标志({JOIN('y_dur_frac')} 枚)才能排除; 四份并集要全量行集({V('union_abcd')} 行)。读它请按“这个数由哪份文书、在窗内 ⇎ 窗外、以符号 ⇎ 字面、连着 ⇎ 跨行写出”来读, 而不是按“少抄了多少原文”。")

assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
for _e, _n in ZID:
    assert eval(_e, {u'B63V': BB63}) == 0, _n
    reg(u'0', _e, _n)
body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCH if 1 < len(HITC[a]) < NSRC]),
       u'all4': len([a for a in ANCH if len(HITC[a]) == NSRC])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'],
         u'anchor_all4': CLS[u'all4'], u'checks': DIST * NSRC}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all4'] == DIST
for n, v in sorted(AMETA.items()):
    reg(str(v), u"%s('%s')" % (FN, n), TOKV.get(n, n))
for n in AMETA:
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
assert u'◘' not in body, u'锚统计量占位符未回填'
for n in AMETA:
    F[n] = v = AMETA[n]
    reg(str(v), u"%s('%s')" % (FN, n), n)
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv63.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b63flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms63.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[' + u''.join(TAGS) + u']⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == n]))
                       for c, n in ((u'single', 1), (u'two', 2), (u'three', 3), (u'four', 4))),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
      u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': NSRC, u'flat': F,
      u'closure_keys': [k for k in F if k.endswith(u'close')]}
json.dump(CH, io.open(u'corpus/_b63checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 字符／非空行 %d／答数 %d 毫秒／和式 %d 行／页眉 %d⇎页脚 %d⇎换页 %d)' % (
        os.path.basename(PATH[i]), F[u'bytes'][i], F[u'chars'][i], F[u'nonblank'][i],
        F[u'y_ans_ms'][i], F[u'y_sum_n'][i], F[u'hdr'][i], F[u'foot'][i], F[u'formfeed'][i])
    for i in range(NSRC)) +
    u' (四份 RFC Editor 纯文本面, 全 LF; 89 分页数按换页符计 %d 页且页脚左侧印 IETF, 00/11 分页 %d⇎%d 页, 21 不分页并带 UTF-8 BOM。'
    u'数字一律从面内现读, 一个都不手填; 抓取时刻、官网现行状态与各实现里 TCP_RTO_MIN 的实际取值只在本机或站外成立, 不进门槛)\n' % (
        F[u'pages_est'][0], F[u'pages_est'][1], F[u'pages_est'][2]))
联结 = (u"；联结不是“同一份数据的两种序列化”, 而是“还没有 RTT 样本时第一个重传超时设多久”在四份一手规范里的四种答法: "
        u"面内现读答数 89 三秒 %s ⇎ 00 三秒 %s ⇎ 11 一秒 %s ⇎ 21 三百三 %s 毫秒; "
        u"3 秒在废止链上搬了家而数字没变——11 把答数降到 1 秒(“3 seconds”字面却从 %d 处涨到 %d 处), 因为它是把那枚 3 秒挪进 (5.7) 的 SYN 回退 MUST(现读 %d 毫秒, 与 89 的初值闭合), 规范窗内只剩 %d 处、窗外 %d 处; "
        u"21 三百三给的是初始 RTT %s 毫秒而非超时: 用它自己的常数复算 PTO=%d(半值不取整)⇎%d(取整), 而它宣称 %d 毫秒——差 %d⇎%d 毫秒, 库里无一行记载, 结构上 PTO 恰为初值的 %d 倍; "
        u"同一条和式写三遍: 00/11 用符号 max (G, K*RTTVAR) 并定义 K=%d ⇎ 21 写死 max(4*rttvar, kGranularity)(现读 %d), max 两参数换了序、末尾多一项 max_ack_delay; "
        u"时长得先归一才可比: 取值集两端之比 %d 倍(下界=21 的时钟粒度 %d 毫秒 ⇎ 上界=89 自述的 RTO 上限 %d 毫秒), 而伪值 5000 毫秒来自小数点把 “0.5/2.5 seconds” 割成 “5 seconds”(共 %d⇎%d 枚), 240 秒⇎60 秒两枚上限的数与单位全被排版拆在两行(共 %d⇎%d⇎%d⇎%d 枚跨行 token); "
        u"00⇎11 的 (2.4) 条款 %d 行里 %d 行逐字节全等、%d 行只差一个逗号(归一后同值)——废止者与被废止者在字节档只差一个字面; "
        u"整行搬运: 89 与后三份零共用行(%d⇎%d⇎%d), 00⇎11 归一后 %d 行 ⇎ 逐字节只 %d 行, 11⇎21 %d 行; 版式三代: 页眉无空格 %d ⇎ 有空格 %d⇎%d ⇎ 不分页 %d, 换页符⇎页脚⇎行尾空格三本账逐份相等(合计闭合 %d⇎%d)。\n") % (
    u'%d(%s)' % (F[u'y_ans_ms'][0], F[u'y_ans_unit'][0]), u'%d(%s)' % (F[u'y_ans_ms'][1], F[u'y_ans_unit'][1]),
    u'%d(%s)' % (F[u'y_ans_ms'][2], F[u'y_ans_unit'][2]), u'%d(%s)' % (F[u'y_ans_ms'][3], F[u'y_ans_unit'][3]),
    F[u'lit_3seconds'][0], F[u'lit_3seconds'][2], F[u'y_c_revert_ms'],
    F[u'secw_3seconds'][2], F[u'outw_3seconds'][2],
    F[u'y_ans_ms'][3], F[u'y_d_pto_exact'], F[u'y_d_pto_int'], F[u'y_d_claim_ms'],
    F[u'y_d_gap_exact'], F[u'y_d_gap_int'], F[u'y_d_three'],
    F[u'y_c_kdef'], F[u'y_d_k'],
    F[u'dur_ratio'][0], F[u'dur_ms_lo'], F[u'dur_ms_hi'],
    F[u'y_dur_frac'][0], F[u'y_dur_frac'][1],
    F[u'y_dur_wrap'][0], F[u'y_dur_wrap'][1], F[u'y_dur_wrap'][2], F[u'y_dur_wrap'][3],
    F[u'align_n'], F[u'align_same_bytes'], F[u'align_punct_only'],
    F[u'share_ab'], F[u'share_ac'], F[u'share_ad'],
    F[u'share_bc'], F[u'y_bc_byte_shared'], F[u'share_cd'],
    F[u'hdr_ns'][0], F[u'hdr_sp'][1], F[u'hdr_sp'][2], F[u'hdr'][3],
    F[u'ff_foot_sum'], F[u'trail_foot_sum'])
title = (u'# B63 没有 RTT 样本时第一个重传超时设多久，四份规范四种答法：3 秒 ⇎ 3 秒 ⇎ 1 秒 ⇎ 333 毫秒（3 秒被搬进回退条款而数字不动，宣称的 1 秒比自己的算法多 %d 毫秒，库里零字面）\n' % (
    F[u'y_d_gap_exact']))
text = (title + srcline + 联结 +
        u'tags: 答数句子⇎和式结构解析(深度0分列+max拆参数) 符号K⇎字面4 max两参数换序 3秒搬家(窗内⇎窗外) '
        u'宣称⇎复算差毫秒(取整两档) 时长归一毫秒 小数点割裂伪值 数⇎单位跨行伪值 值域档混入别子系统 '
        u'上限240⇎60秒 归一⇎字节两把搬运尺 逗号级条款差 B⇎C 义务词窗内⇎窗外 粒度散文MUST⇎max兜底 '
        u'变量名换代SRTT⇎smoothed_rtt 333全称⇎缩写 版式三代 换页⇎页脚⇎行尾空格三账闭合 锚归属由正文现推 '
        u'闭合账 标量 %d⇎清单 %d 项⇎恒等式 %d 条\n' % (F[u'scalar_clos_n'], F[u'list_clos_n'], F[u'x_ident_n']) +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill63.py 从 corpus/_b63checks.json 与 corpus/_deriv63.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两至三源 %d ⇎ 四源 %d ⇎ 错配 %d ｜ 池内取用 %d／池 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], len(ERR), CH[u'pool_used'], F[u'pool_n']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(F)))
print(u'答数 %s ms ⇎ 单位 %s ⇎ 去重 %d ⇎ 跨度 %d=%d×%d+%d' % (
    F[u'y_ans_ms'], F[u'y_ans_unit'], F[u'y_ans_distinct'], F[u'y_ans_max'], F[u'y_ans_ratio'],
    F[u'y_ans_min'], F[u'y_ans_rem']))
print(u'和式 %s ⇎ 参数 %s/%s ⇎ 系数 %s ⇎ 尾项 %s' % (
    F[u'y_sum_n'], F[u'y_sum_mfirst'], F[u'y_sum_msecond'], F[u'y_sum_coef'], F[u'y_sum_tail']))
print(u'PTO 复算: init=%d k=%d gran=%d ⇒ 实数 %d ⇎ 取整 %d ⇎ 宣称 %d (差 %d/%d, 倍数 %d)' % (
    F[u'y_ans_ms'][3], F[u'y_d_k'], F[u'y_d_gran'], F[u'y_d_pto_exact'], F[u'y_d_pto_int'],
    F[u'y_d_claim_ms'], F[u'y_d_gap_exact'], F[u'y_d_gap_int'], F[u'y_d_three']))
print(u'时长档: %s ⇎ 窗内 %s ⇎ 窗外 %s ⇎ 跨行 %s ⇎ 小数 %s ⇎ 端点 %d/%d' % (
    [F[u'durms_' + t.lower()] for t in TAGS], F[u'y_dur_win'], F[u'y_dur_out'], F[u'y_dur_wrap'],
    F[u'y_dur_frac'], F[u'dur_ms_lo'], F[u'dur_ms_hi']))
print(u'上限: A %d(跨行 %d) ⇎ B/C %s ratio %d rem %d ⇎ 回退 %d' % (
    F[u'y_a_cap_ms'], F[u'y_a_cap_wrap'], F[u'y_bc_cap_ms'], F[u'y_cap_ratio'], F[u'y_cap_rem'],
    F[u'y_c_revert_ms']))
print(u'搬运: share %s ⇎ 归一⇎字节 B/C %d⇎%d ⇎ 并集 %d/%d ⇎ 容斥闭合 %d' % (
    [F[u'share_%s%s' % (TAGS[a].lower(), TAGS[b].lower())] for a in range(NSRC) for b in range(a + 1, NSRC)],
    F[u'share_bc'], F[u'y_bc_byte_shared'], F[u'union_abc'], F[u'union_abcd'], F[u'abcd_close']))
print(u'对照: 行数 %d ⇎ 字节同 %d ⇎ 仅标点 %d ⇎ 归一异 %d ⇎ 闭合 %d ⇎ 上取整 %s' % (
    F[u'align_n'], F[u'align_same_bytes'], F[u'align_punct_only'], F[u'align_norm_diff'],
    F[u'align_close'], F[u'floor_same_bytes']))
print(u'壳: 页眉 %s/%s ⇎ 页脚 %s ⇎ 换页 %s ⇎ IETF %s ⇎ 自编号残余 %d' % (
    F[u'hdr_ns'], F[u'hdr_sp'], F[u'foot'], F[u'formfeed'], F[u'foot_ietf'], F[u'a_1122_resid']))
print(u'窗 %s ⇎ 长 %s ⇎ 子条目 %s ⇎ 3seconds 窗内 %s 窗外 %s' % (
    F[u'sec_a'], F[u'sec_len'], F[u'sec_sub'], F[u'secw_3seconds'], F[u'outw_3seconds']))
print(u'闭合键 %d 项 ⇎ 恒等式 %d 条 ⇎ 标量合计 %d ⇎ 清单闭合 %d' % (
    F[u'scalar_clos_n'], F[u'x_ident_n'], F[u'scalar_clos_sum'], F[u'list_clos_n']))
MEASP = u'corpus/_b63meas.json'
COLONLY = (u'sig_sha256_16', u'floor_lines', u'clause_lines')
if os.path.exists(MEASP):
    M = json.load(io.open(MEASP, encoding='utf-8'))
    TIE, MISS = [], []
    for k in sorted(M):
        if k in COLONLY:
            continue
        if k not in F:
            MISS.append(k)
            continue
        got = F[k]
        if isinstance(got, tuple) or (isinstance(got, list) and any(isinstance(x, tuple) for x in got)):
            got = json.loads(json.dumps(got))
        if got != M[k]:
            TIE.append((k, u'建=%s 采=%s' % (got, M[k])))
    print(u'两侧对账(四份纯文本面): 采集键 %d ／ 采集侧独有关 %d(+%d 项声明) ／ 不符 %d ｜ %s' % (
        len(M), len(MISS), len(COLONLY), len(TIE), TIE[:12]))
    print(u'  采集侧独有(正则族/独立档, 建条目侧另立口径): %s' % (MISS[:14],))
else:
    print(u'两侧对账: 无 corpus/_b63meas.json(采集侧未跑)')
