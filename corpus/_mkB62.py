# -*- coding: utf-8 -*-
"""B62 建条目(第二遍现算, 五源): ⟦A⟧rfc2581(1999) ⇎ ⟦B⟧rfc3390(2002) ⇎ ⟦C⟧rfc5681(2009) ⇎ ⟦D⟧rfc6928(Experimental, 十倍) ⇎ ⟦E⟧rfc9002(QUIC)。
主轴: 新建连接在第一个 RTT 里允许立刻发出多少字节——⟦A⟧ 把答案钉在 2 段并逐字否决那枚方程(“We do NOT allow this change”),
⟦B⟧ 把同一枚方程(同带标号 (1))改成标准, ⟦C⟧ 保留 ⟦B⟧ 的两枚阈值 1095/2190 却把中间档换成随 SMSS 增长的 3*SMSS 并整枚删掉 4380,
⟦D⟧ 把系数换成 10、上限换成 14600 且自称“patterned after RFC 3390”, ⟦E⟧ 换掉计量单位(不再提 MSS)改说 ten times max_datagram_size 并以 14,720 封顶。
第二遍的独立性: 采集侧(_pick62.py)用 re.findall/前后瞻与集合运算, 本遍一律换成游标档(find 循环 + 逐字符判邻)、
方程解析档(把 min (c*MSS, max (k*MSS, B)) 的两个系数与常数帽当结构解析出来而非数正则命中)、
折叠面档与手工词界分类; 形状量用逐字符计数与数换行而非 len/split; 搬运账用排序后两指针求交而非 set&。
两遍只在定义一致处对账, 对账表 corpus/_b62meas.json 逐键比; 采集侧独有的三枚键(sha256 签名、两份档位原始行清单)不参与对账, 因其算法即口径。
抓取时刻、rfc-editor.org 现行状态页、勘误表与是否另有新版本只在本机或站外成立, 不进门槛。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
NSRC = 5
ENTRY = u'%s/babeltele/B62_tcp_initial_window_five_answers.md' % C
PATH = [u'corpus/raw/tcpiw/rfc2581.txt', u'corpus/raw/tcpiw/rfc3390.txt', u'corpus/raw/tcpiw/rfc5681.txt',
        u'corpus/raw/tcpiw/rfc6928.txt', u'corpus/raw/tcpiw/rfc9002.txt']
TAGS = [u'A', u'B', u'C', u'D', u'E']
LB = dict(zip(TAGS, [u'99 两段', u'02 方程', u'09 三段表', u'13 十倍', u'21 QUIC']))
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN --- (corpus/_wire62.py 把这一段机械切进 audit.py::_b62_scan)
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
    """游标档: find 循环取出现位置(采集侧用 str.count / re.findall)。to=None 时必须honour frm。"""
    out, k = [], s.find(sub, frm)
    lim = len(s) if to is None else to
    while k >= 0 and k < lim:
        out.append(k)
        k = s.find(sub, k + 1)
    return out


def occ(s, sub, frm=0, to=None):
    return len(pos(s, sub, frm, to))


def cut(s, a, b):
    return s[a:b] if b is not None else s[a:]


def numpos(t, num):
    """独立数 token: 前不接数字/逗号/句点、后不接数字(采集侧 (?<![\\d,.])N(?![\\d]))。"""
    out, k = [], t.find(num)
    while k >= 0:
        e = k + len(num)
        prev = t[k - 1] if k else u''
        nxt = t[e] if e < len(t) else u''
        if prev not in DIG + u',.' and nxt not in DIG:
            out.append((k, e))
        k = t.find(num, k + 1)
    return out


def runs(t, lo, hi):
    """值域档: 逐字符扫出 4~5 位数字串, 按前后字符判独立, 取 lo..hi 内的去重值。"""
    out, i, n = {}, 0, len(t)
    while i < n:
        if t[i] in DIG:
            j = i
            while j < n and t[j] in DIG:
                j += 1
            prev = t[i - 1] if i else u''
            nxt = t[j] if j < n else u''
            if prev not in DIG + u',.' and nxt not in DIG and 4 <= j - i <= 5:
                v = int(t[i:j])
                if lo <= v <= hi:
                    out[v] = 1
            i = j
        else:
            i += 1
    return sorted(out)


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


def wcount(s, word, ci=False):
    w = word.lower() if ci else word
    return len([x for x in wtok(s) if (x.lower() if ci else x) == w])


def paircount(s, a, b):
    """相邻词对档(采集侧 \\binitial\\s+window\\b): 词流里 a 紧跟 b。"""
    ws = [x.lower() for x in wtok(s)]
    n = 0
    for k in range(len(ws) - 1):
        if ws[k] == a and ws[k + 1] == b:
            n += 1
    return n


def is_hdr(l):
    if l[:4] != u'RFC ':
        return False
    k = 4
    while k < len(l) and l[k] in DIG:
        k += 1
    return k - 4 == 4 and l[k:k + 1] in (u' ', u'') and l[k:].strip() != u''


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


def is_foot(l):
    s = l.strip()
    return page_end(s, True) or page_end(s, False)


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
four(u'bom', lambda i: 1 if RAWB[i][:3] == b'\xef\xbb\xbf' else 0)
four(u'hdr', lambda i: len([l for l in LST[i] if is_hdr(l)]))
four(u'foot', lambda i: len([l for l in LST[i] if is_foot(l)]))
four(u'foot_brk', lambda i: len([l for l in LST[i] if page_end(l.strip(), True)]))
four(u'foot_old', lambda i: len([l for l in LST[i] if page_end(l.strip(), False)
                                 and not page_end(l.strip(), True)]))
four(u'hdr_title', lambda i: len([l for l in LST[i] if is_hdr(l) and u'Initial Window' in l]))
F[u'pagelines'] = [F[u'hdr'][i] + F[u'foot'][i] for i in range(NSRC)]
F[u'sig'] = [hashlib.blake2b(RAWB[i], digest_size=8).hexdigest() for i in range(NSRC)]
F[u'sig_distinct'] = len(set(F[u'sig']))
F[u'chars_split'] = [len(x) for x in TXT]
F[u'lines_nl'] = [len(x.split(NL)) for x in TXT]
F[u'rec_close'] = [F[u'chars'][i] - F[u'chars_split'][i] + F[u'lines'][i] - F[u'lines_nl'][i]
                   for i in range(NSRC)]
four(u'iw_word_nos', lambda i: sum(1 for l in LST[i] if not (is_hdr(l) or is_foot(l))
                                   for _ in pos(l.lower(), u'initial window')))
F[u'w_iw_word'] = [occ(LOW[i], u'initial window') for i in range(NSRC)]
F[u'iw_word_gap'] = [F[u'w_iw_word'][i] - F[u'iw_word_nos'][i] for i in range(NSRC)]
F[u'trail_is_foot'] = [F[u'trail'][i] - F[u'foot'][i] for i in range(NSRC)]


# ---- 字面族 ----
LITK = {u'4380': u'4380', u'2190': u'2190', u'1095': u'1095', u'14600': u'14600', u'14720': u'14720',
        u'c14600': u'14,600', u'c14720': u'14,720', u'1500': u'1500', u'1460': u'1460', u'1200': u'1200',
        u'333': u'333', u'4k': u'4K', u'2smss': u'2*SMSS', u'4smss': u'4*SMSS', u'2mss': u'2*MSS',
        u'4mss': u'4*MSS', u'10mss': u'10*MSS', u'2sp_smss': u'2 * SMSS', u'3sp_smss': u'3 * SMSS',
        u'4sp_smss': u'4 * SMSS', u'minp': u'min (', u'maxp': u'max (', u'p1': u'(1)'}
for k in sorted(LITK):
    four(u'lit_' + k, lambda i, k=k: occ(TXT[i], LITK[k]))
for k in (u'4380', u'2190', u'1095', u'14600', u'14720', u'1500', u'1460', u'1200'):
    four(u'tok_' + k, lambda i, k=k: len(numpos(TXT[i], k)))
four(u'tok_c14720', lambda i: len(pos(TXT[i], u'14,720')))
four(u'tok_c14600', lambda i: len(pos(TXT[i], u'14,600')))
for k in (u'14600', u'14720', u'1460'):
    F[u'subgap_' + k] = [F[u'lit_' + k][i] - F[u'tok_' + k][i] for i in range(NSRC)]
F[u'bare_only_14600'] = [F[u'lit_14600'][i] - F[u'lit_c14600'][i] for i in range(NSRC)]
F[u'comma_only_14720'] = [F[u'lit_c14720'][i] - F[u'lit_14720'][i] for i in range(NSRC)]
F[u'nb_lo'] = 1095      # 值域档下界: 面内最矮的一枚阈值(下方 x_c_lo_bound 现读, 恒等式核它)
F[u'nb_hi'] = 14720     # 值域档上界: 21 QUIC 的封顶值(下方 x_e_capnum 现读, 恒等式核它)
for i in range(NSRC):
    F[u'numband_' + TAGS[i].lower()] = runs(TXT[i], F[u'nb_lo'], F[u'nb_hi'])
    F[u'numband_n_' + TAGS[i].lower()] = len(F[u'numband_' + TAGS[i].lower()])

# ---- 规范窗(取最后一处命中, 回溯到最近编号标题, 前推到编号不同的下一标题) ----
RULE = {u'A': u'IW, the initial value of cwnd, MUST be less',
        u'B': u'The upper bound for the initial window is given more precisely',
        u'C': u'IW, the initial value of cwnd, MUST be set',
        u'D': u'More precisely, the upper bound for the initial window',
        u'E': u'Initial and Minimum Congestion Window'}


def headnum(l):
    """编号标题: 行首至多四空格, 数字组(可带小节点), 可选尾点, 再接空白与非空题文; 返回编号串或 None。"""
    n = 0
    while n < len(l) and l[n] == u' ' and n < 5:
        n += 1
    if n > 4 or n >= len(l) or l[n] not in DIG:
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
                break   # “1.  Title”: 尾点后不接数字, 编号到此为止
            continue
        seg += (u'.' if seg else u'') + d
        break
    if seg.endswith(u'.'):
        seg = seg[:-1]
    if j < len(l) and l[j] in u' \t' and l[j:].strip():
        return seg
    return None


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
    b = len(ls)
    for n in range(r + 1, len(ls)):
        m = headnum(ls[n])
        if m is not None and len(ls[n].strip()) > 3 and m != na:
            b = n
            break
    SECW.append((a, b))
    SECN.append(na)
F[u'sec_w'] = SECW
F[u'sec_num'] = SECN
four(u'sec_hit', lambda i: len([n for n, l in enumerate(LST[i]) if RULE[TAGS[i]] in l]))
F[u'sec_a'] = [w[0] for w in SECW]
F[u'sec_b'] = [w[1] for w in SECW]
OFF = []
for i in range(NSRC):
    o, s = [], 0
    for l in LST[i]:
        o.append(s)
        s += len(l) + 1
    OFF.append(o)
F[u'sec_len'] = [sum(len(x) + 1 for x in LST[i][SECW[i][0]:SECW[i][1]]) - 1 for i in range(NSRC)]


def wend(i):
    """规范窗末字节偏移(下一标题行的行首−1); 窗到文末时取全篇长度。"""
    b = SECW[i][1]
    return OFF[i][b] - 1 if b < len(OFF[i]) else len(TXT[i])


for i in range(NSRC):
    F[u'sec_off_' + TAGS[i].lower()] = (OFF[i][SECW[i][0]], wend(i))
WINS = [(u'4380', u'4380'), (u'2190', u'2190'), (u'1095', u'1095'), (u'14600', u'14600'),
        (u'c14720', u'14,720'), (u'minp', u'min ('), (u'maxp', u'max (')]
for k, s in WINS:
    F[u'secw_' + k] = [occ(TXT[i], s, OFF[i][SECW[i][0]], wend(i)) for i in range(NSRC)]
    F[u'outw_' + k] = [F[u'lit_' + k][i] - F[u'secw_' + k][i] for i in range(NSRC)]

# ---- 方程解析档: min (C*VAR, max (K*VAR, B)) ----
VAR = (u'MSS', u'SMSS')


def parse_eq(t):
    """游标+逐字符: 从 'min (' 起解析系数、变量名、内层 max 的系数与常数帽。返回结构化清单。"""
    out = []
    for p in pos(t, u'min ('):
        j = p + 5
        if j < len(t) and t[j] == u' ':
            j += 1
        c = u''
        while j < len(t) and t[j] in DIG:
            c += t[j]
            j += 1
        if not c or t[j:j + 1] != u'*':
            continue
        j += 1
        v = u''
        while j < len(t) and t[j] in ALW:
            v += t[j]
            j += 1
        if v not in VAR:
            continue
        q = t.find(u', max (', j)
        if q < 0 or q - j > 4:
            continue
        m = q + 7
        if t[m:m + 1] == u' ':
            m += 1
        k = u''
        while m < len(t) and t[m] in DIG:
            k += t[m]
            m += 1
        if not k or t[m:m + 1] != u'*':
            continue
        m += 1
        v2 = u''
        while m < len(t) and t[m] in ALW:
            v2 += t[m]
            m += 1
        if v2 not in VAR:
            continue
        q2 = t.find(u', ', m)
        if q2 < 0 or q2 - m > 3:
            continue
        b = u''
        n = q2 + 2
        while n < len(t) and t[n] in DIG:
            b += t[n]
            n += 1
        if not b:
            continue
        lb = t.find(u')', n)
        out.append((int(c), v, int(k), v2, int(b), t[n:n + 6]))
    return out


EQS = [parse_eq(TXT[i]) for i in range(NSRC)]
F[u'x_eq'] = [u' '.join(u'%d*%s/%d*%s/%d' % (e[0], e[1], e[2], e[3], e[4]) for e in EQS[i]) or u'无'
              for i in range(NSRC)]
F[u'x_eq_n'] = [len(EQS[i]) for i in range(NSRC)]
F[u'x_eq_coef'] = [EQS[i][0][0] if EQS[i] else 0 for i in range(NSRC)]
F[u'x_eq_inner'] = [EQS[i][0][2] if EQS[i] else 0 for i in range(NSRC)]
F[u'x_eq_cap'] = [EQS[i][0][4] if EQS[i] else 0 for i in range(NSRC)]
F[u'x_eq_var'] = [EQS[i][0][1] if EQS[i] else u'' for i in range(NSRC)]
F[u'x_eq_varlen'] = [len(F[u'x_eq_var'][i]) if i < NSRC else 0 for i in range(NSRC)]
F[u'x_eq_unit'] = [EQS[i][0][5] if EQS[i] else u'' for i in range(NSRC)]
F[u'x_eq_close'] = [F[u'lit_minp'][i] - F[u'x_eq_n'][i] for i in range(NSRC)]
F[u'x_ab_var_diff'] = F[u'x_eq_varlen'][0] - F[u'x_eq_varlen'][1]
F[u'x_coef_ratio'] = [F[u'x_eq_coef'][i] * 100 // F[u'x_eq_inner'][i] if F[u'x_eq_inner'][i] else 0
                      for i in range(NSRC)]

# ---- 针族(游标档代正则) ----
NEED = [(u'min4', u'min (4*'), (u'min10', u'min (10*'), (u'cap4380', u'max (2*MSS, 4380'),
        (u'cap14600', u'max (2*MSS, 14600)'), (u'ten_mds', u'ten times the maximum datagram size'),
        (u'dont_allow', u'We do NOT allow this change'), (u'udp8', u'8-byte overhead'),
        (u'tcp20', u'20-byte overhead'), (u'large_of', u'the larger of'),
        (u'two_smss', u'less than or equal to 2*SMSS'), (u'skel', u'represents a change from'),
        (u'change2', u'which specified that the congestion window be'),
        (u'synack', u'MUST NOT increase the size of the congestion window')]
for k, s in NEED:
    four(u'n_' + k, lambda i, s=s: occ(TXT[i], s))
    four(u'n_' + k + u'_ci', lambda i, s=s: occ(LOW[i], s.lower()))


def segcount(t, num):
    """“N segments”/“ten segments”档: 逐字符在词流里找数词+segments。"""
    ws = wtok(t.lower())
    return len([k for k in range(len(ws) - 1) if ws[k] == num and ws[k + 1] == u'segments'])


F[u'n_seg10'] = [segcount(TXT[i], u'10') + segcount(TXT[i], u'ten') for i in range(NSRC)]
F[u'x_seg_small'] = [segcount(TXT[i], u'2') + segcount(TXT[i], u'4') for i in range(NSRC)]


def skel_cite(i):
    """“represents a change from” 之后紧跟的那行里的上游编号(逐字符读数字, 不手填)。"""
    for n, l in enumerate(LST[i]):
        if u'represents a change from' in l and n + 1 < len(LST[i]):
            nx = LST[i][n + 1]
            p = nx.find(u'RFC ')
            if p >= 0:
                d, q = u'', p + 4
                while q < len(nx) and nx[q] in DIG:
                    d += nx[q]
                    q += 1
                return d
    return u''


F[u'x_skel_cite'] = [skel_cite(i) for i in range(NSRC)]
for k in (u'tier2190', u'tier1095'):
    s = (u'2190 bytes' if k == u'tier2190' else u'1095 bytes')
    four(u'w_' + k, lambda i, s=s: occ(TXT[i], s))
four(u'w_iw_of', lambda i: occ(TXT[i], u'IW, the initial value of cwnd'))
four(u'w_mustnot_seg', lambda i: occ(TXT[i], u'MUST NOT be more than'))

SN = [(u'min4', u'min (4*'), (u'min10', u'min (10*'), (u'cap4380', u'max (2*MSS, 4380'),
      (u'cap14600', u'max (2*MSS, 14600)'), (u'seg10', u'10 segments'), (u'two_smss', u'2*SMSS'),
      (u's4smss', u'4*SMSS'), (u's4mss', u'4*MSS'), (u'dont_allow', u'We do NOT allow this change'),
      (u'large_of', u'the larger of'), (u'udp8', u'8-byte overhead'), (u'tcp20', u'20-byte overhead'),
      (u'ten_times', u'ten times the maximum datagram size'), (u'iw_of', u'IW, the initial value of cwnd'),
      (u'skel', u'represents a change from')]
for k, s in SN:
    F[u's_' + k] = [occ(TXT[i], s) for i in range(NSRC)]
    F[u's_' + k + u'_fold'] = [occ(FO[i], s) for i in range(NSRC)]
    F[u'wrap_gap_' + k] = [F[u's_' + k + u'_fold'][i] - F[u's_' + k][i] for i in range(NSRC)]
F[u'wrap_pin_n'] = len(SN)
F[u'wrap_pin_hit'] = len([k for k, s in SN if max(F[u'wrap_gap_' + k]) > 0])
F[u'wrap_gap_total'] = sum([sum(F[u'wrap_gap_' + k]) for k, s in SN])

# ---- 语汇 ----
WK = [(u'mss', u'MSS'), (u'smss', u'SMSS'), (u'mds', u'max_datagram_size'), (u'datagram', u'datagram'),
      (u'iw', u'IW'), (u'cwnd', u'cwnd'), (u'initwin_lower', u'initial window'),
      (u'initwin_caps', u'Initial Window'), (u'icw', u'initial congestion window'),
      (u'slow_start', u'slow start'), (u'slowstart_hy', u'Slow-Start'), (u'slowstart_flat', u'SlowStart')]
for k, s in WK:
    four(u'v_' + k, lambda i, s=s: occ(TXT[i], s))
F[u'v_smss_ci'] = [occ(LOW[i], u'smss') for i in range(NSRC)]
F[u'v_iw_word'] = [paircount(TXT[i], u'initial', u'window') for i in range(NSRC)]
F[u'v_seg_word'] = [len([x for x in wtok(TXT[i]) if x.lower() == u'segment' or x.lower() == u'segments'])
                    for i in range(NSRC)]

# ---- 义务词 ----
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED'):
    four(u'u_' + w.replace(u' ', u'_').lower(), lambda i, w=w: occ(TXT[i], w))
F[u'oblig_up'] = [F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i] for i in range(NSRC)]
for w in (u'must', u'should', u'may'):
    four(u'l_' + w, lambda i, w=w: wcount(TXT[i], w))
F[u'oblig_low'] = [F[u'l_must'][i] + F[u'l_should'][i] + F[u'l_may'][i] for i in range(NSRC)]
four(u'rfc2119_ref', lambda i: occ(TXT[i], u'2119'))
four(u'key_words_boiler', lambda i: occ(TXT[i], u'key words') + occ(TXT[i], u'Key words'))

# ---- 身份 ----
HK = [(u'cat_std', u'Category: Standards Track'), (u'cat_exp', u'Category: Experimental'),
      (u'cat_info', u'Category: Informational'), (u'cat_hist', u'Category: Historic'),
      (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'), (u'issn_hdr', u'ISSN:')]
for k, s in HK:
    four(k, lambda i, s=s: occ(TXT[i], s))
four(u'obsoleted_by', lambda i: occ(LOW[i], u'obsoleted by'))
four(u'errata', lambda i: occ(LOW[i], u'errata'))
for n in (u'2581', u'3390', u'5681', u'6928', u'9002', u'2414', u'2001', u'2988', u'6298', u'1122'):
    four(u'cite_' + n, lambda i, n=n: occ(TXT[i], u'RFC ' + n) + occ(TXT[i], u'RFC' + n))

# ---- 档位表解析: B 的三段 ⇎ C 的三段 ----
def nums_in(s):
    """一行里逐字符切出的数字串(按出现次序)——阈值不再手填。"""
    out, d = [], u''
    for ch in s + u' ':
        if ch in DIG:
            d += ch
        elif d:
            out.append(int(d))
            d = u''
    return out


def iflines(i, kw):
    return [l for l in LST[i] if l.strip().lower().startswith(u'if ') and kw in l]


def iwlines(i):
    return [l for l in LST[i] if l.strip().startswith(u'IW = ')]


BT = [l for l in LST[1] if u'then win <= ' in l]
CT = iwlines(2)
F[u'x_b_caps'] = [u'; '.join(l.strip() for l in BT)]
F[u'x_c_caps'] = [u'; '.join(l.strip() for l in CT)]
F[u'x_b_mid_const'] = len([l for l in BT if u'win <= 4380' in l])
F[u'x_c_mid_grow'] = len([l for l in CT if u'3 * SMSS' in l])
F[u'x_b_tiers_n'] = len(BT)
F[u'x_c_tiers_n'] = len(CT)
F[u'tier_norm_same'] = len(set(pnorm(l) for l in BT) & set(pnorm(l) for l in CT))
for k, s in ((u'const_cap', u'win <= 4380'), (u'grow_cap', u'3 * SMSS'), (u'ifparen', u'If (MSS'),
             (u'ifsmss', u'If SMSS'), (u'ifsmsq', u'if SMSS'), (u'lesscap', u'less than or equal to 2*SMSS')):
    four(u'tier_' + k, lambda i, s=s: occ(TXT[i], s))
# 阈值两侧的符号: B 用严格 <, C 用 <= —— 于是 SMSS=2190 这一点点上分档边界
F[u'x_b_strict'] = len([l for l in iflines(1, u'MSS') if u' < ' in l])
F[u'x_c_le'] = len([l for l in iflines(2, u'SMSS') if u'<=' in l])
F[u'x_c_upper_lt'] = occ(TXT[2], u'SMSS > 2190 bytes')

# ---- 由面内数字现算的桥(全部只用五份里读到的数, 不手填) ----
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
        # 千分位: 逗号后恰有三位数字、再后不是数字, 才算同一个数的一节
        if t[j] == u',' and t[j + 1:j + 4].isdigit() and t[j + 4:j + 5] not in DSET:
            d += t[j + 1:j + 4]
            j += 4
            continue
        break
    return int(d) if d else 0


def num_before(t, needle):
    """针之前紧贴的那串数字(逐字符回退)。"""
    p = t.find(needle)
    if p < 1:
        return 0
    j = p
    while j > 0 and t[j - 1] in DIG:
        j -= 1
    d = t[j:p]
    return int(d) if d else 0


W2N = {u'twice': 2, u'ten': 10, u'three': 3, u'four': 4, u'two': 2, u'seven': 7}


def word_before(t, needle):
    """针之前紧贴的那个英文词(小写)——面里 IW 倍数写作 “ten times” 而非 “10 times”。"""
    p = t.find(needle)
    if p < 0:
        return u''
    j = p
    while j > 0 and t[j - 1] in WCH:
        j -= 1
    e = j
    while j > 0 and t[j - 1].isalpha():
        j -= 1
    return t[j:e].lower()


def word_after(t, needle):
    """针之后紧贴的那个英文词(小写)。"""
    p = t.find(needle)
    if p < 0:
        return u''
    j = p + len(needle)
    while j < len(t) and t[j] in WCH:
        j += 1
    s = j
    while j < len(t) and t[j].isalpha():
        j += 1
    return t[s:j].lower()


F[u'x_e_tenword'] = word_before(TXT[4], u'times the maximum')
F[u'x_e_twiceword'] = word_after(TXT[4], u'bytes or ')
F[u'x_e_ten'] = W2N.get(F[u'x_e_tenword'], 0)
F[u'x_e_twice'] = W2N.get(F[u'x_e_twiceword'], 0)
F[u'x_b_pkgnum'] = num_after(TXT[1], u'Sending a ')
F[u'x_b_mssnum'] = num_after(TXT[1], u'(MSS) of')
# 阈值与乘数: 从 B、C 的 If 行与 IW 行现读, 一个都不手填
BI = iflines(1, u'MSS')
CI = iflines(2, u'SMSS')
F[u'x_b_if'] = [nums_in(l) for l in BI]
F[u'x_c_if'] = [nums_in(l) for l in CI]
F[u'x_b_if_n'] = len(BI)
F[u'x_c_if_n'] = len(CI)
F[u'x_c_iw_mult'] = [num_after(l, u'IW = ') for l in CT]
F[u'x_c_seg_cap'] = [num_before(l, u' segments') for l in CT if u' segments' in l]
F[u'x_c_mid_mult'] = F[u'x_c_iw_mult'][1] if len(F[u'x_c_iw_mult']) > 1 else 0
F[u'x_c_hi_mult'] = F[u'x_c_iw_mult'][0] if F[u'x_c_iw_mult'] else 0
F[u'x_c_hi_bound'] = F[u'x_c_if'][0][0] if CI and F[u'x_c_if'][0] else 0
F[u'x_b_hi_bound'] = F[u'x_b_if'][-1][0] if BI and F[u'x_b_if'][-1] else 0
F[u'x_c_lo_bound'] = F[u'x_c_if'][-1][0] if CI and F[u'x_c_if'][-1] else 0
F[u'x_b_lo_bound'] = F[u'x_b_if'][0][0] if BI and F[u'x_b_if'][0] else 0
F[u'x_thresh_close'] = F[u'x_c_hi_bound'] - F[u'x_b_hi_bound']
F[u'x_lo_close'] = F[u'x_c_lo_bound'] - F[u'x_b_lo_bound']
F[u'x_c_mid_ub'] = F[u'x_c_if'][1][1] if len(F[u'x_c_if']) > 1 and len(F[u'x_c_if'][1]) > 1 else 0
F[u'x_c_mid_ub_close'] = F[u'x_c_mid_ub'] - F[u'x_c_hi_bound']
F[u'x_e_capnum'] = num_after(TXT[4], u'the larger of ')
F[u'x_e_ovhnum'] = num_before(TXT[4], u'-byte overhead of UDP')
F[u'x_e_ovhtcp'] = num_before(TXT[4], u'-byte overhead for TCP')
F[u'x_e_floornum'] = num_after(TXT[4], u'payload of at least ')
F[u'x_b_three'] = F[u'x_eq_cap'][1] // F[u'x_b_mssnum']
F[u'x_b_close'] = F[u'x_eq_cap'][1] - F[u'x_b_mssnum'] * F[u'x_b_three']
F[u'x_d_ten'] = F[u'x_eq_cap'][3] // F[u'x_b_mssnum']
F[u'x_d_close'] = F[u'x_eq_cap'][3] - F[u'x_b_mssnum'] * F[u'x_d_ten']
F[u'x_e_bridge'] = F[u'x_e_capnum'] - F[u'x_eq_cap'][3]
F[u'x_e_ovh'] = F[u'x_e_ovhtcp'] - F[u'x_e_ovhnum']
F[u'x_e_seg'] = F[u'x_e_ten']
F[u'x_e_close'] = F[u'x_e_bridge'] - F[u'x_e_seg'] * F[u'x_e_ovh']
F[u'x_e_break'] = F[u'x_e_capnum'] // F[u'x_e_twice']
F[u'x_e_break_close'] = F[u'x_e_break'] * F[u'x_e_twice'] - F[u'x_e_capnum']
F[u'x_e_twice_at_floor'] = F[u'x_e_twice'] * F[u'x_e_floornum']
F[u'x_e_binds'] = 1 if F[u'x_e_twice_at_floor'] < F[u'x_e_capnum'] else 0
F[u'x_e_iw'] = F[u'x_e_floornum'] * F[u'x_e_ten']
F[u'x_c_upper_at2190'] = F[u'x_c_mid_mult'] * F[u'x_c_hi_bound']
F[u'x_b_at_hi'] = min(F[u'x_eq_coef'][1] * F[u'x_c_hi_bound'],
                      max(F[u'x_eq_inner'][1] * F[u'x_c_hi_bound'], F[u'x_eq_cap'][1]))
F[u'x_widen'] = F[u'x_c_upper_at2190'] - F[u'x_b_at_hi']
F[u'x_at1460_b'] = min(F[u'x_eq_coef'][1] * F[u'x_b_mssnum'],
                       max(F[u'x_eq_inner'][1] * F[u'x_b_mssnum'], F[u'x_eq_cap'][1]))
F[u'x_at1460_c'] = F[u'x_c_mid_mult'] * F[u'x_b_mssnum']
F[u'x_at1460_close'] = F[u'x_at1460_b'] - F[u'x_at1460_c']
MU = F[u'x_c_iw_mult']
SG = F[u'x_c_seg_cap']
F[u'x_c_top_at_hi'] = F[u'x_c_hi_mult'] * F[u'x_c_hi_bound']
F[u'x_c_lo_at_lo'] = (MU[-1] if MU else 0) * F[u'x_c_lo_bound']
F[u'x_c_span_close'] = F[u'x_c_top_at_hi'] - F[u'x_c_lo_at_lo']
F[u'x_c_cap_close'] = F[u'x_c_top_at_hi'] - F[u'x_eq_cap'][1]
F[u'x_c_seg_gap'] = sum(abs(MU[n] - SG[n]) for n in range(len(SG)))
F[u'x_c_mult_delta'] = (MU[-1] - MU[0]) if MU else 0
F[u'x_c_bound_delta'] = F[u'x_c_lo_bound'] - F[u'x_c_hi_bound']
F[u'x_c_dir_opp'] = 1 if (F[u'x_c_mult_delta'] > 0) != (F[u'x_c_bound_delta'] > 0) else 0
F[u'x_bom_bytes'] = F[u'bytes'][4] - F[u'chars'][4]
F[u'x_oblig_spread'] = F[u'oblig_up'][4] - F[u'oblig_up'][1]
F[u'x_a_gap'] = 0
_ee = [n for n, l in enumerate(LST[0]) if u'IW = min (4*SMSS' in l]
_rr = [n for n, l in enumerate(LST[0]) if u'We do NOT allow' in l]
_ru = [n for n, l in enumerate(LST[0]) if RULE[u'A'] in l]
if _ee and _rr and _ru:
    F[u'x_a_gap'] = _rr[0] - _ee[0]
    F[u'x_a_order'] = 1 if _ru[0] < _ee[0] < _rr[0] else 0
F[u'x_b_after'] = 0
_bq = [n for n, l in enumerate(LST[1]) if u'min (4*MSS' in l]
_bj = [n for n, l in enumerate(LST[1]) if u'represents a change from' in l]
if _bq and _bj:
    F[u'x_b_after'] = _bj[0] - _bq[0]
F[u'x_d_after'] = 0
_dq = [n for n, l in enumerate(LST[3]) if u'min (10*MSS' in l]
_dj = [n for n, l in enumerate(LST[3]) if u'represents a change from' in l]
if _dq and _dj:
    F[u'x_d_after'] = _dj[0] - _dq[0]
F[u'x_after_spread'] = F[u'x_b_after'] - F[u'x_d_after']

# 面内现读数之间的恒等式(全归零, 由门槛重算; 一项不成立即门槛失败)
ZID = [(u"B62V('x_eq_cap', 1)-B62V('x_b_mssnum')*B62V('x_b_three')", u'02 方程: 4380=1460×3'),
       (u"B62V('x_eq_cap', 3)-B62V('x_b_mssnum')*B62V('x_d_ten')", u'13 十倍: 14600=1460×10'),
       (u"B62V('x_e_capnum')-B62V('x_eq_cap', 3)-B62V('x_e_ten')*(B62V('x_e_ovhtcp')-B62V('x_e_ovhnum'))",
        u'字节桥: 14720=14600+10×(20−8)'),
       (u"B62V('x_c_upper_at2190')-B62V('x_widen')-B62V('x_eq_cap', 1)", u'加宽: 6570−2190=4380'),
       (u"B62V('x_e_break')*B62V('x_e_twice')-B62V('x_e_capnum')", u'翻倍档咬合点×twice=封顶值'),
       (u"B62V('x_e_iw')-B62V('x_e_floornum')*B62V('x_e_ten')", u'最小载荷档: 12000=1200×ten'),
       (u"B62V('x_at1460_c')-B62V('x_b_mssnum')*B62V('x_c_mid_mult')", u'09 在 1460 档=1460×3'),
       (u"B62V('x_at1460_b')-B62V('x_at1460_c')", u'常见 MSS 处两表同值'),
       (u"B62V('x_eq_coef', 3)-B62V('x_e_seg')", u'13 的方程系数 ⇎ 21 的英文数词同为 ten'),
       (u"B62V('x_c_hi_bound')-B62V('x_b_hi_bound')", u'上档阈值两份现读同值 2190'),
       (u"B62V('x_c_lo_bound')-B62V('x_b_lo_bound')", u'下档阈值两份现读同值 1095'),
       (u"B62V('x_c_mid_ub')-B62V('x_c_hi_bound')", u'09 中间档上界=高档下界(<= 与 > 同点)'),
       (u"B62V('x_c_top_at_hi')-B62V('x_eq_cap', 1)", u'09 高档阈值×本档系数=02 的常数帽 4380'),
       (u"B62V('x_c_top_at_hi')-B62V('x_c_lo_at_lo')", u'09 表两端各自算回同一枚 4380'),
       (u"B62V('x_c_seg_gap')", u'09 每档的段数上限恰等于同档的 SMSS 倍数'),
       (u"B62V('nb_lo')-B62V('x_c_lo_bound')", u'值域下界=面内现读的最矮阈值'),
       (u"B62V('nb_hi')-B62V('x_e_capnum')", u'值域上界=21 QUIC 面内现读的封顶值'),
       (u"B62V('lit_1095', 1)-B62V('lit_1095', 2)", u'两枚阈值在两份里各出现两次'),
       (u"B62V('lit_2190', 1)-B62V('lit_2190', 2)", u'同上·2190 档')]
F[u'x_ident_n'] = len(ZID)

# ---- 搬运账(排序两指针求交, 不用集合运算符) ----
NRM = pnorm
GE40 = []
GE40N = []
for shell, store in ((True, GE40), (False, GE40N)):
    for i in range(NSRC):
        s = set()
        for l in LST[i]:
            if not shell and (is_hdr(l) or is_foot(l)):
                continue
            n = NRM(l)
            if len(l.strip()) >= 40 and len(n) >= 40:
                s.add(n)
        store.append(sorted(s))


def m_iset(a, b):
    """两份有序清单的公共项(两指针, 不落集合)。"""
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


def m_inter(a, b):
    return len(m_iset(a, b))


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
            F[u'share_%s%s%s' % (TAGS[a].lower(), TAGS[b].lower(), suf)] = m_inter(SS[a], SS[b])
    F[u'union_abcd' + suf] = m_union(SS[0], SS[1], SS[2], SS[3])
    F[u'only_c' + suf] = len([x for x in SS[2] if x not in SS[0] and x not in SS[1] and x not in SS[3]])
    F[u'only_d' + suf] = len([x for x in SS[3] if x not in SS[0] and x not in SS[1] and x not in SS[2]])
    F[u'only_e' + suf] = len([x for x in SS[4] if x not in SS[0] and x not in SS[1]
                              and x not in SS[2] and x not in SS[3]])
    bc = m_iset(SS[1], SS[2])
    bcd = m_iset(bc, SS[3])
    bce = m_iset(bc, SS[4])
    F[u'share_bc_plus' + suf] = len(bcd) + len(bce) - len(m_iset(bcd, bce))
F[u'ABC_inter'] = m_inter(m_iset(GE40[0], GE40[1]), GE40[2])
F[u'union_abc'] = m_union(GE40[0], GE40[1], GE40[2])
F[u'union_abcde'] = m_union(GE40[0], GE40[1], GE40[2], GE40[3], GE40[4])
F[u'union_abc_nos'] = m_union(GE40N[0], GE40N[1], GE40N[2])
F[u'abc_incl'] = (F[u'lines_ge40'][0] + F[u'lines_ge40'][1] + F[u'lines_ge40'][2]
                  - F[u'share_ab'] - F[u'share_ac'] - F[u'share_bc'] + F[u'ABC_inter'])
F[u'abc_close'] = F[u'abc_incl'] - F[u'union_abc']
F[u'abc_close_nos'] = ((F[u'lines_ge40_nos'][0] + F[u'lines_ge40_nos'][1] + F[u'lines_ge40_nos'][2]
                        - F[u'share_ab_nos'] - F[u'share_ac_nos'] - F[u'share_bc_nos']
                        + m_inter(m_iset(GE40N[0], GE40N[1]), GE40N[2])) - F[u'union_abc_nos'])
F[u'shell_delta'] = [F[u'lines_ge40'][i] - F[u'lines_ge40_nos'][i] for i in range(NSRC)]
F[u'union_delta'] = F[u'union_abcde'] - F[u'union_abcd']

# ---- 锚候选行 ----
NLITS = (u'4380', u'2190', u'1095', u'14600', u'14,720', u'14,600', u'SMSS', u'MSS', u'IW')
four(u'num_lines', lambda i: len([l for l in LST[i] if len(l.strip()) >= 55
                                  and any(x in l for x in NLITS)]))
for i in range(NSRC):
    F[u'num_lines_' + TAGS[i].lower()] = F[u'num_lines'][i]

# ---- 锚池: 按“这条锚在几份文书里逐字再现”分层 ----
SPECIAL = (u'4380', u'14600', u'14,720', u'1095', u'2190', u'SMSS', u'MSS', u'IW', u'min (',
           u'max_datagram_size', u'segments', u'Initial Window', u'datagram')
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


CLOSK = sorted([k for k in F if (u'_close' in k or k.endswith(u'_ledger'))
                and isinstance(F[k], (int, float)) and not isinstance(F[k], bool)])
F[u'scalar_clos_n'] = len(CLOSK)
F[u'scalar_clos_sum'] = sum(F[k] for k in CLOSK)
F[u'scalar_clos_list'] = CLOSK
F[u'list_clos_n'] = len([k for k in F if (u'_close' in k or k.endswith(u'_ledger')) and isinstance(F[k], list)])
# --- SCAN END ---

# ---------- DERIV 登记与正文模板 ----------
K, ZERO, COLL, SEENX = {}, [], {}, {}
G, LINES, MISSING = {}, [], []
FN = u'B62V'


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
        nums = [eval(e, {u'B62V': BB62}) for e in exprs]
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


BB62 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B62V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
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
        val = eval(args[0], {u'F': F, u'B62V': BB62, u'len': len, u'max': max, u'min': min,
                             u'round': round, u'repr': repr})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]

    def rep(m):
        c = m.group(1).strip()
        if HELP.match(c):
            return eval(c, {u'V': V, u'JOIN': JOIN, u'CLOS': CLOS, u'CLOS4': CLOS4, u'TOK': TOK, u'AT': AT})
        if u'B62V(' not in c:
            return m.group(0)
        assert BARE.match(BCALL.sub(u'0', c)), c
        val = eval(c, {u'B62V': BB62})
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
G[u'A_rule'] = AT(u'own', u'A', u'MUST be less than or equal to 2*SMSS')
G[u'A_eq'] = AT(u'own', u'A', u'IW = min (4*SMSS')
G[u'A_rej'] = AT(u'own', u'A', u'We do NOT allow')
G[u'A_nonstd'] = AT(u'own', u'A', u'non-standard, experimental TCP extension')
G[u'B_eq'] = AT(u'own', u'B', u'min (4*MSS')
G[u'B_1460'] = AT(u'own', u'B', u'1460 bytes')
G[u'B_mid'] = AT(u'own', u'B', u'then win <= 4380')
G[u'B_hi'] = AT(u'own', u'B', u'then win <= 2 * MSS')
G[u'B_sk'] = AT(u'own', u'B', u'represents a change from')
G[u'C_set'] = AT(u'own', u'C', u'MUST be set using the following')
G[u'C_mid'] = AT(u'own', u'C', u'IW = 3 * SMSS bytes')
G[u'C_up'] = AT(u'own', u'C', u'If SMSS > 2190 bytes')
G[u'C_lo'] = AT(u'own', u'C', u'if SMSS <= 1095 bytes')
G[u'D_eq'] = AT(u'own', u'D', u'min (10*MSS')
G[u'D_pat'] = AT(u'own', u'D', u'It is patterned after')
G[u'D_14600'] = AT(u'own', u'D', u'maximum 14600 B')
G[u'D_sk'] = AT(u'own', u'D', u'which specified that the congestion window be')
G[u'E_head'] = AT(u'own', u'E', u'Initial and Minimum Congestion Window')
G[u'E_ten'] = AT(u'own', u'E', u'ten times the maximum datagram size')
G[u'E_cap'] = AT(u'own', u'E', u'the larger of 14,720 bytes')
G[u'E_ovh'] = AT(u'own', u'E', u'8-byte overhead')
G[u'E_1200'] = AT(u'own', u'E', u'payload of at least 1200')
G[u'AC_iw'] = AT(u'2', u'A', u'IW, the initial value of cwnd')

# ---------- 正文 ----------
LINE(u'🧭', u"五源字节 {JOIN('bytes')}: 99 两段 ⇎ 02 方程 ⇎ 09 三段表 ⇎ 13 十倍 ⇎ 21 QUIC; 面内字符 {JOIN('chars')} ⇎ 原文件行 {JOIN('lines')} ⇎ 非空行 {JOIN('nonblank')} ⇎ 最长行 {JOIN('maxlen')} 列。"
     u"五份同为 RFC Editor 纯文本, 却在同一介质里分成两种序列化: 分页行(页眉+页脚) {JOIN('pagelines')} 行——前四份每页重印抬头与页脚, QUIC 档 {V('pagelines', 4)} 行(页眉 {V('hdr', 4)} ⇎ 页脚 {V('foot', 4)}), 一行也没有。"
     u"编码层也不齐: UTF-8 BOM {CLOS4('bom', '带 BOM')} 份 ⇎ 非 ASCII 字符 {JOIN('nonascii')} 枚 ⇎ 面内字节减字符 {V('x_bom_bytes')} 字节(QUIC 档)。"
     u"回车符 {CLOS4('cr', '回车符')} 枚 ⇎ 行尾空格 {JOIN('trail')} 处 ⇎ 页脚行 {JOIN('foot')} 处, 两者之差 {CLOS4('trail_is_foot', '行尾空格减页脚')}——尾部空白全落在页脚那行的对齐空格上。五份签名 {V('sig_distinct')} 种(blake2b 前 16 位)。")

LINE(u'📐', u"答案由一条方程给还是由一张表给: 把 min (C*VAR, max (K*VAR, B)) 当结构解析(游标逐字符, 非正则命中), 五份各自解出 {JOIN('x_eq')}; "
     u"外层系数 {JOIN('x_eq_coef')} ⇎ 内层系数 {JOIN('x_eq_inner')} ⇎ 常数帽 {JOIN('x_eq_cap')}。99 两段解出的是它自己逐字否决的那一枚 {A_eq}; 02 方程把同一枚改成标准 {B_eq}; "
     u"09 三段表解出 {V('x_eq_n', 2)} 枚——它整篇唯一的 min ( 是另一条增量式 {V('secw_minp', 2)} 处, 与初窗无关, 于是这一份根本没有初窗方程, 只有三行表 {C_mid}; "
     u"13 十倍把系数换成 {V('x_eq_coef', 3)}、帽换成 {D_eq}; 21 QUIC {V('x_eq_n', 4)} 枚——它连 MSS 这个量都不用了(MSS 字样 {V('v_mss', 4)} 处), 改说 {E_ten}。"
     u"同一句式骨架在两份“加大初窗”文书里逐字复写: “represents a change from”{JOIN('n_skel')} 处, 其后紧跟的上游编号 {B_sk} ⇎ {D_sk}——被改的那一句本身没改。")

LINE(u'⚖', u"否决写在标准里: 99 两段先给现行上限 {A_rule}, 再引出一枚“非标准的实验性扩展”{A_nonstd}, 方程 {A_eq} 之后第 {V('x_a_gap')} 行落刀 {A_rej}; "
     u"三处行号序 {CLOS('x_a_order', u'规则⇎方程⇎否决的先后')}——规则在前、方程居中、否决在后, 一段里同时读完“现在允许多少”和“三年后会允许多少”。"
     u"02 方程把同一条方程原样搬来做标准上限 {B_eq}: 与 99 两段的写法只差变量名——SMSS 换成 MSS, 长度差 {CLOS('x_ab_var_diff', '同一方程的变量名差')} 个字母; "
     u"并且它自己算出为什么是 4380: {B_1460}——1460×3=4380, 桥闭合 {CLOS('x_b_close', '4380−1460×3')}, 倍数 {V('x_b_three')}。"
     u"“This upper bound for the initial window size represents a change from”这一句在两份“加大初窗”的文书里逐字同现: 13 十倍落在方程后第 {V('x_d_after')} 行 {D_sk}, 02 方程落在方程后第 {V('x_b_after')} 行 {B_sk}, 距离差 {CLOS('x_after_spread', '改自句距离差')} 行——02 方程在方程与“改自”句之间先塞进了 1460→4380 那段推导。")

LINE(u'🔁', u"同阈值不同形状: 1095 与 2190 这两枚阈值只在 02 方程与 09 三段表里成对出现, 字面 1095 {JOIN('lit_1095')} ⇎ 2190 {JOIN('lit_2190')} 处, "
     u"而 4380 在 09 三段表里 {V('lit_4380', 2)} 处——一份换了形状的文书可以一个数字都不留。两表逐行对照: 02 方程的三行档位 {V('x_b_tiers_n')} 行(常数帽 {V('x_b_mid_const')} 行 {B_mid} ⇎ 上档 {B_hi}), "
     u"09 三段表三行 {V('x_c_tiers_n')} 行(增长帽 {V('x_c_mid_grow')} 行 {C_mid} ⇎ 上档 {C_up} ⇎ 下档 {C_lo}); 两表归一化后同值行 {CLOS('tier_norm_same', '两表同值行')} 行——一行也不共用。"
     u"分档边界的符号也不同: 02 方程中间档用严格不等号 {V('x_b_strict')} 行 ⇎ 09 三段表用 <= {V('x_c_le')} 行 ⇎ 上档用 > {V('x_c_upper_lt')} 行, 于是 SMSS=2190 这唯一一点上两份给出的答案不同: "
     u"02 方程走 {V('x_c_hi_bound')} 那一档 2×{V('x_c_hi_bound')}={V('x_b_at_hi')}, 09 三段表把它算进中间档 3×{V('x_c_hi_bound')}={V('x_c_upper_at2190')}, 即比 {V('x_b_at_hi')} 多 {CLOS('x_widen', '同阈值处的加宽量')} 字节(+50%), 而库里没有任何一行写着这件事。"
     u"这张表的方向与方程族相反: 三行的倍数沿档为 {V('x_c_iw_mult', 0)}⇎{V('x_c_iw_mult', 1)}⇎{V('x_c_iw_mult', 2)}, 同档的段数上限为 {V('x_c_seg_cap', 0)}⇎{V('x_c_seg_cap', 1)}⇎{V('x_c_seg_cap', 2)}(逐档相减合计 {CLOS('x_c_seg_gap', '倍数列减段数列')}), "
     u"而它比对的 SMSS 阈值从 {V('x_c_hi_bound')} 降到 {V('x_c_lo_bound')}——倍数在升、阈值在降, 方向相反位 {V('x_c_dir_opp')}, 报文段越小则一次允许发出的段数越多; 方程族做不出这一档, 一份只有一个外层系数 {V('x_eq_coef', 1)}。"
     u"更绕的是这张表从两端各自算回同一枚数: 高档 {V('x_c_hi_mult')}×{V('x_c_hi_bound')}={V('x_c_top_at_hi')} ⇎ 下档 {V('x_c_iw_mult', 2)}×{V('x_c_lo_bound')}={V('x_c_lo_at_lo')}, 两端差 {CLOS('x_c_span_close', '09 表两端之差')} ⇎ 与 02 方程常数帽差 {CLOS('x_c_cap_close', '表顶端减方程帽')}——{V('x_eq_cap', 1)} 被复原了两次, 而它在这一份里字面 {V('lit_4380', 2)} 处。"
     u"反过来在常见 MSS=1460 处两份闭合: 02 方程 {V('x_at1460_b')} ⇎ 09 三段表 {V('x_at1460_c')}, 差 {CLOS('x_at1460_close', '常见 MSS 处两表差')}——分歧只在 1460 之上。")

LINE(u'🧪', u"数字写法分档(与 B61 相反的倒置): 14600 在 13 十倍只以不带千分位的面目出现 {JOIN('lit_14600')} 处 ⇎ 带逗号 {JOIN('lit_c14600')} 处, 差 {CLOS4('bare_only_14600', '只带裸写')}; "
     u"14,720 在 21 QUIC 反过来: 带逗号 {JOIN('lit_c14720')} 处 ⇎ 裸写 {JOIN('lit_14720')} 处, 差 {CLOS4('comma_only_14720', '只带千分位')}——同库相邻两档对同一个数千分位的取舍相反。"
     u"把这两枚大数按“子串档 − 独立 token 档”相减: 14600 差 {CLOS4('subgap_14600', '14600 子串−token')} ⇎ 14,720 差 {CLOS4('subgap_14720', '14720 子串−token')}——两份各只认一种写法, 相减全为零; 唯独 1460 不是: 它在 13 十倍 {V('lit_1460', 3)} 处子串 ⇎ {V('tok_1460', 3)} 处独立, 差 {V('subgap_1460', 3)}——那两处全是 14600 的前缀, 搜 1460 会把它读成“13 十倍也讲 1460”。"
     u"值域档另算(两端都取面内读数, 不是随手划的区间): 下界=最矮的一枚阈值 {V('nb_lo')}, 上界=21 QUIC 的封顶 {V('nb_hi')}, "
     u"其间独立整数去重 99 {V('numband_n_a')} ⇎ 02 {V('numband_n_b')} ⇎ 09 {V('numband_n_c')} ⇎ 13 {V('numband_n_d')} ⇎ 21 {V('numband_n_e')} 枚。"
     u"4K 字样只在 02 方程 {JOIN('lit_4k')} 处; 333(毫秒)只在 21 QUIC {JOIN('lit_333')} 处; 1200(UDP 最小净载荷){JOIN('lit_1200')} 处也在 21 QUIC {E_1200}。")

LINE(u'⛓', u"折行通道(原面逐字面 ⇎ 整篇空白折平后逐字面): 本条 {V('wrap_pin_n')} 枚针里只有 {V('wrap_pin_hit')} 枚被排版折断——“10 segments”原面 {JOIN('s_seg10')} 处 ⇎ 折平 {JOIN('s_seg10_fold')} 处, 差 {CLOS4('wrap_gap_seg10', '折行补回')}, 全库折行差合计 {V('wrap_gap_total')} 处; "
     u"其余各档差(逐份展开) min (4* {CLOS4('wrap_gap_min4', '方程头差')} ⇎ 常数帽 {CLOS4('wrap_gap_cap4380', '常数帽差')} ⇎ 否决句 {CLOS4('wrap_gap_dont_allow', '否决句差')} ⇎ the larger of {CLOS4('wrap_gap_large_of', '封顶句差')} ⇎ 十倍句 {CLOS4('wrap_gap_ten_times', '十倍句差')}, "
     u"即方程、否决句与 QUIC 的封顶句在每一份里都整行连着写——可判性不靠折平。"
     u"页眉才是这条库里的隐形通道: “initial window”忽略大小写含壳面 {JOIN('w_iw_word')} 处 ⇎ 去壳面 {JOIN('iw_word_nos')} 处, 差 {CLOS4('iw_word_gap', '页眉贡献的出现处')}, "
     u"恰等于页眉里印着标题“Initial Window”的行数 {JOIN('hdr_title')}——02 方程与 13 十倍同名(都叫 Increasing TCP's Initial Window), 于是这两份的词频被每页重印的抬头抬高, 另三份一字不抬。"
     u"同一件事在搬运账上却是负的: 去页眉页脚只挪动长行集合 {CLOS4('shell_delta', '含壳−去壳')} 行——每页重印的同一条页眉在集合里去重成一条。词频被壳抬高、集合不被壳抬高, 两档必须分别立键。")

LINE(u'📏', u"义务词体例在此不成差轴(与 B61 相反): 2119 规定的四枚全大写词五份皆有——MUST {JOIN('u_must')} ⇎ SHOULD {JOIN('u_should')} ⇎ MAY {JOIN('u_may')} ⇎ MUST NOT {JOIN('u_must_not')} 处, 全大写族合计 {JOIN('oblig_up')} 处; "
     u"小写词界档 must {JOIN('l_must')} ⇎ should {JOIN('l_should')} ⇎ may {JOIN('l_may')}, 三词合计 {JOIN('oblig_low')} 处——大小写两档同时立键才读得出“这一代文档守体例”。"
     u"关键词样板(key words)五份同为 {JOIN('key_words_boiler')} 处 ⇎ 编号 2119 被引用 {JOIN('rfc2119_ref')} 次, 抬头与样板齐备; "
     u"真正差的是密度而非规矩: 全大写族从 02 方程的 {V('oblig_up', 1)} 处到 21 QUIC 的 {V('oblig_up', 4)} 处, 相差 {V('x_oblig_spread')} 处, 而 02 方程是一份“只改一句上限”的短文。")

LINE(u'🗓', u"计量单位的换代写在词频里: MSS {JOIN('v_mss')} ⇎ SMSS {JOIN('v_smss')} ⇎ max_datagram_size {JOIN('v_mds')} ⇎ datagram {JOIN('v_datagram')} ⇎ IW {JOIN('v_iw')} ⇎ cwnd {JOIN('v_cwnd')} 处。"
     u"09 三段表是 SMSS 用得最重的一份({V('v_smss', 2)} 处)而 02 方程 {V('v_smss', 1)} 处——同一批阈值, 一份按“协商出的段大小”写, 一份按“MSS”写; "
     u"21 QUIC 把三者全换掉: MSS {V('v_mss', 4)} ⇎ SMSS {V('v_smss', 4)} ⇎ max_datagram_size {V('v_mds', 4)} 处, 缩写 IW 也弃用({V('v_iw', 4)} 处)——单位换了, 所以 4380/14600 这类“按段大小算出的常数”在它那侧只能用字节面给出 {E_cap}。"
     u"两条上限之间有一座写在面里的桥: 13 十倍给 14600 {D_14600} ⇎ 21 QUIC 给 14,720, 差 {CLOS('x_e_bridge', '字节差')} 字节 = 每包 {CLOS('x_e_ovh', '开销差')} 字节 × {V('x_e_seg')} 包, 闭合 {CLOS('x_e_close', '桥闭合')}; "
     u"那句“UDP 的 8 字节开销比 TCP 的 20 字节小”{E_ovh} 就是这座桥的文字版。21 QUIC 的另一半上限“twice the maximum datagram size”只在 max_datagram_size 超过 {CLOS('x_e_break', '两倍档咬合点')} 时才咬人 {CLOS('x_e_break_close', '翻倍档闭合')}; "
     u"按其自己规定的最小载荷 1200 字节现算初窗 {CLOS('x_e_iw', '1200×10')} 字节, 仍小于 14,720——最小情形走十倍档。")

LINE(u'🧾', u"身份与成熟度是独立的一轴: 抬头“Category: Standards Track”{JOIN('cat_std')} 处 ⇎ “Category: Experimental”{JOIN('cat_exp')} 处 ⇎ Informational {JOIN('cat_info')} ⇎ Historic {JOIN('cat_hist')}——"
     u"五份里只有 13 十倍印实验轨({V('cat_exp', 3)} 处), 而它给的 14600 后来被 21 QUIC 沿用为字节桥的基准: 实验档把数字抬得最高, 标准档不动。"
     u"废止链: Obsoletes 头 {JOIN('obs_hdr')} 处 ⇎ Updates 头 {JOIN('upd_hdr')} 处 ⇎ “obsoleted by”{JOIN('obsoleted_by')} 处 ⇎ 勘误提及 {JOIN('errata')} 处 ⇎ ISSN 头 {JOIN('issn_hdr')} 处。"
     u"引用计数: RFC 2581 {JOIN('cite_2581')} ⇎ 3390 {JOIN('cite_3390')} ⇎ 5681 {JOIN('cite_5681')} ⇎ 6928 {JOIN('cite_6928')} ⇎ 9002 {JOIN('cite_9002')} 次——"
     u"最新的 21 QUIC 引 6928 {V('cite_6928', 4)} 次却一份也没被引(自引 {V('cite_9002', 4)}), 而 13 十倍把“patterned after RFC 3390”写进摘要 {D_pat}。"
     u"含关键数字的长行(≥55 字符) 99 {V('num_lines_a')} ⇎ 02 {V('num_lines_b')} ⇎ 09 {V('num_lines_c')} ⇎ 13 {V('num_lines_d')} ⇎ 21 {V('num_lines_e')} 行: 02 方程只有 {V('num_lines_b')} 行带数, 因为它全文的答案就一行方程; 21 QUIC {V('num_lines_e')} 行。")

LINE(u'⇄', u"整行搬运(行长 ≥40 且归一化非空, 排序后两指针求交): 99⇎02 {V('share_ab')} ⇎ 99⇎09 {V('share_ac')} ⇎ 99⇎13 {V('share_ad')} ⇎ 99⇎21 {V('share_ae')} ⇎ "
     u"02⇎09 {V('share_bc')} ⇎ 02⇎13 {V('share_bd')} ⇎ 02⇎21 {V('share_be')} ⇎ 09⇎13 {V('share_cd')} ⇎ 09⇎21 {V('share_ce')} ⇎ 13⇎21 {V('share_de')} 行。"
     u"搬运的方向与“谁抄谁”相反: 09 三段表与 99 两段共用 {V('share_ac')} 行, 却只与把它改成标准的 02 方程共用 {V('share_bc')} 行——"
     u"09 是把 99 的拥塞控制正文收编成一份总表, 而非把 02 的那一行方程改写; 三份同现 {V('ABC_inter')} 行, 容斥给出的三份并集 {V('abc_incl')} 行 ⇎ 并集实数 {V('union_abc')} 行, 闭合 {CLOS('abc_close', '三代容斥闭合')}(去壳档另算 {CLOS('abc_close_nos', '去壳容斥闭合')})。"
     u"只在本份 {V('only_c')} ⇎ {V('only_d')} ⇎ {V('only_e')} 行; 02⇎09⇎(13|21) 三三同现 {V('share_bc_plus')} 行; 四份并集 {V('union_abcd')} 行 ⇎ 五份并集 {V('union_abcde')} 行, 加进 21 QUIC 只多 {V('union_delta')} 行。"
     u"去页眉页脚只挪动长行集 {CLOS4('shell_delta', '壳内独有长行')} 行(含壳集 {JOIN('lines_ge40')} ⇎ 去壳集 {JOIN('lines_ge40_nos')})。"
     u"99⇎21 只共用 {V('share_ae')} 行 ⇎ 13⇎21 共用 {V('share_de')} 行: 相隔二十二年的两份几乎无一行相同。")

LINE(u'ℒ', u"方法 ⇒ 面对“同一问题五份文书”, 先问答案是方程还是表: 本条把初窗做成结构解析谓词(从 'min (' 起逐字符读系数、变量、内层 max 与常数帽), 于是“这一份给不给方程”有可判口径({JOIN('x_eq')}), "
     u"“4380 这个词还在不在”是另一回事({JOIN('lit_4380')} 处, 09 三段表 {V('lit_4380', 2)} 处)。其次把窗口判据定死: 规范句按整行扫取最后一处命中(目录页也印同名句), 回溯到最近编号标题、前推到编号不同的下一标题, 行号 {JOIN('sec_a')}–{JOIN('sec_b')}, 窗长 {JOIN('sec_len')} 字符; "
     u"窗内⇎窗外分档读 4380({JOIN('secw_4380')}⇎{JOIN('outw_4380')})与 14,720({JOIN('secw_c14720')}⇎{JOIN('outw_c14720')}), 才读得出“QUIC 只在那一节里给过一次数”。"
     u"再次把量测自身的失效做成键: 1460 的子串−token 差({JOIN('subgap_1460')} 处全落在 14600 里), 页眉对词频的抬高({JOIN('iw_word_gap')})与页眉对集合搬运的零影响({JOIN('shell_delta')})同时登记; "
     u"五枚闭合项(4380−1460×{V('x_b_three')}={V('x_b_close')}, 14600−1460×{V('x_d_ten')}={V('x_d_close')}, {V('x_e_bridge')}−{V('x_e_seg')}×{V('x_e_ovh')}={V('x_e_close')}, "
     u"{V('x_at1460_b')}−{V('x_at1460_c')}={V('x_at1460_close')}, 池分层 {V('pool_close')})恒零也占键位, 读得出“这里本可能出错”; "
     u"另有 {V('x_ident_n')} 条由面内现读数构成的恒等式(4380={V('x_b_mssnum')}×{V('x_b_three')}、14600={V('x_b_mssnum')}×{V('x_d_ten')}、{V('x_e_capnum')}={V('x_eq_cap', 3)}+{V('x_eq_coef', 3)}×({V('x_e_ovhtcp')}−{V('x_e_ovhnum')})……)逐条送门槛重算。")

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 五源各 {JOIN('chars')} 字符, 窗口只能取锚点触到的行(窗长 {JOIN('sec_len')} 字符 ⇎ 全篇 {JOIN('chars')} 字符); 本条的结论几乎全是跨文书的量: "
     u"“否决句与它否决的方程同在一份标准里”要 99 两段的三处行号同现(间隔 {V('x_a_gap')} 行), 同阈值不同形状要两张表逐行并排(02 {V('x_b_tiers_n')} 行 ⇎ 09 {V('x_c_tiers_n')} 行 ⇎ 归一同值 {V('tier_norm_same')} 行), "
     u"加宽 50% 这件事在库里零字面痕迹——只能由 3×2190 与 4380 现算({V('x_widen')} 字节); 字节桥要跨两份文档取 14600、14,720 与 8/20 两个开销数({V('x_e_bridge')}={V('x_e_seg')}×{V('x_e_ovh')}); "
     u"千分位取舍要相邻两档相反({V('bare_only_14600', 3)}⇎{V('comma_only_14720', 4)}); 搬运账要五份行集全量(四份并集 {V('union_abcd')} 行)。读它请按“这个数由哪份文书、以方程还是表格、在页眉还是正文里给出”来读, 而不是按“少抄了多少原文”。", **{})

assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
for _e, _n in ZID:
    assert eval(_e, {u'B62V': BB62}) == 0, _n
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
       u'all5': len([a for a in ANCH if len(HITC[a]) == NSRC])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'],
         u'anchor_all5': CLS[u'all5'], u'checks': DIST * NSRC}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all5'] == DIST
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
json.dump(DERIV, io.open(u'corpus/_deriv62.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b62flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms62.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[' + u''.join(TAGS) + u']⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == n]))
                       for c, n in ((u'single', 1), (u'two', 2), (u'three', 3),
                                    (u'four', 4), (u'five', 5))),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
      u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': NSRC, u'flat': F,
      u'closure_keys': [k for k in F if k.endswith(u'close')]}
json.dump(CH, io.open(u'corpus/_b62checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 字符／非空行 %d／初窗方程 %s／4380×14600×14720 %d⇎%d⇎%d)' % (
        os.path.basename(PATH[i]), F[u'bytes'][i], F[u'chars'][i], F[u'nonblank'][i], F[u'x_eq'][i],
        F[u'lit_4380'][i], F[u'lit_14600'][i], F[u'lit_c14720'][i]) for i in range(NSRC)) +
    u' (五份 RFC Editor 纯文本面, 全 LF; 前四份分页重印页眉页脚, QUIC 档不分页并带 UTF-8 BOM。'
    u'数字一律从面内现读, 一个都不手填; 抓取时刻、官网现行状态与勘误表是否已挂新版只在本机或站外成立, 不进门槛)\n')
联结 = (u"；联结不是“同一份数据的两种序列化”, 而是“新建连接在第一个 RTT 里允许立刻发出多少字节”在五份一手规范里的五种答法: "
        u"结构解析现读 99 两段 %s ⇎ 02 方程 %s ⇎ 09 三段表 %s ⇎ 13 十倍 %s ⇎ 21 QUIC %s; "
        u"99 两段把同一枚方程写成“非标准的实验性扩展”并逐字否决(“We do NOT allow this change”, 距方程 %d 行), 三年后 02 方程把它原样立为标准(只把 SMSS 改成 MSS, 差 %d 个字母); "
        u"09 三段表保住 1095⇎2190 两枚阈值却删光 4380(字面 %d⇎%d⇎%d 处), 中间档换成 3*SMSS——在 SMSS=2190 这一点上比 02 方程多放行 %d 字节(+50%%), 库里无一行记载; "
        u"13 十倍把系数抬到 %d、帽抬到 14600(自称 patterned after RFC 3390), 21 QUIC 弃用 MSS 改说 ten times max_datagram_size 并以 14,720 封顶: 14,720−14600=%d=%d×(20−8) 是它自己写明的 UDP⇎TCP 开销桥; "
        u"千分位取舍在相邻两档相反: 14600 只裸写 %d 处 ⇎ 14,720 只带逗号 %d 处, 而 1460 的 %d 处“命中”全是 14600 的前缀; "
        u"义务词体例在此反不构成差轴(全大写 MUST 族 %d⇎%d⇎%d⇎%d⇎%d 处); 成熟度独立成轴: 抬数最高的一份是唯一印着 Experimental 的 13 十倍(抬头 %d 处); "
        u"整行共用 99⇎09 %d 行 ⇎ 02⇎09 %d 行 ⇎ 02⇎13 %d 行 ⇎ 99⇎21 %d 行, 而去页眉页脚只挪动 %d⇎%d⇎%d⇎%d⇎%d 行——词频被页眉抬高 %d⇎%d⇎%d⇎%d⇎%d 处, 集合不抬。\n") % (
    F[u'x_eq'][0], F[u'x_eq'][1], F[u'x_eq'][2], F[u'x_eq'][3], F[u'x_eq'][4],
    F[u'x_a_gap'], F[u'x_ab_var_diff'],
    F[u'lit_4380'][0], F[u'lit_4380'][1], F[u'lit_4380'][2], F[u'x_widen'],
    F[u'x_eq_coef'][3], F[u'x_e_bridge'], F[u'x_e_seg'],
    F[u'bare_only_14600'][3], F[u'comma_only_14720'][4], F[u'subgap_1460'][3],
    F[u'oblig_up'][0], F[u'oblig_up'][1], F[u'oblig_up'][2], F[u'oblig_up'][3], F[u'oblig_up'][4],
    F[u'cat_exp'][3],
    F[u'share_ac'], F[u'share_bc'], F[u'share_bd'], F[u'share_ae'],
    F[u'shell_delta'][0], F[u'shell_delta'][1], F[u'shell_delta'][2], F[u'shell_delta'][3],
    F[u'shell_delta'][4],
    F[u'iw_word_gap'][0], F[u'iw_word_gap'][1], F[u'iw_word_gap'][2], F[u'iw_word_gap'][3],
    F[u'iw_word_gap'][4])
title = (u'# B62 新建连接在第一个 RTT 里能立刻发多少字节，五份规范五种答法：2 段 ⇎ 方程 4380 ⇎ 删掉 4380 的三段表 ⇎ 十倍 14600 ⇎ 换掉 MSS 的 14,720（同一条方程先被逐字否决、三年后原样立为标准，中间档加宽 %d 字节在库里零字面）\n' % (
    F[u'x_widen']))
text = (title + srcline + 联结 +
        u'tags: 初窗方程结构解析(min×max 两系数与常数帽) 否决句与方程同行距 同阈值不同形状两表逐行 边界符号严格⇎闭档 '
        u'加宽只可复算 千分位裸写⇎带逗号相邻两档相反 子串被长数吞没(1460∈14600) 页眉抬词频⇎集合不抬双档 '
        u'UDP⇎TCP 开销字节桥 义务词体例不成差轴 成熟度独立轴(唯一 Experimental 那份抬数最高) 整行容斥 换计量单位致常数失效 '
        u'锚归属由正文现推 闭合账 标量 %d⇎清单 %d 项\n' % (F[u'scalar_clos_n'], F[u'list_clos_n']) +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill62.py 从 corpus/_b62checks.json 与 corpus/_deriv62.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两至四源 %d ⇎ 五源 %d ⇎ 错配 %d ｜ 池内取用 %d／池 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all5'], len(ERR), CH[u'pool_used'], F[u'pool_n']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(F)))
print(u'方程解析 %s ⇎ 系数 %s ⇎ 帽 %s ⇎ min( 闭合 %s' % (
    F[u'x_eq_n'], F[u'x_eq_coef'], F[u'x_eq_cap'], F[u'x_eq_close']))
print(u'窗 %s ⇎ 窗长 %s ⇎ 4380 窗内 %s 窗外 %s ⇎ 14,720 窗内 %s' % (
    F[u'sec_a'], F[u'sec_len'], F[u'secw_4380'], F[u'outw_4380'], F[u'secw_c14720']))
print(u'桥: b3=%d close=%d d10=%d close=%d e=%d/%d/%d close=%d 加宽=%d 1460处=%d/%d' % (
    F[u'x_b_three'], F[u'x_b_close'], F[u'x_d_ten'], F[u'x_d_close'], F[u'x_e_bridge'],
    F[u'x_e_seg'], F[u'x_e_ovh'], F[u'x_e_close'], F[u'x_widen'], F[u'x_at1460_b'], F[u'x_at1460_c']))
print(u'页眉抬词 %s ⇎ 集合挪 %s ⇎ 闭合键 %d 项 ⇎ 附录标量合计 %d' % (
    F[u'iw_word_gap'], F[u'shell_delta'], F[u'scalar_clos_n'], F[u'scalar_clos_sum']))
MEASP = u'corpus/_b62meas.json'
COLONLY = (u'sig_sha256_16', u'tier_lines_b', u'tier_lines_c', u'arith_caps', u'arith_tiers', u'arith_check',
           u'sig_distinct_check')
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
    print(u'两侧对账(五份纯文本面): 采集键 %d ／ 采集侧独有关 %d(+%d 项声明) ／ 不符 %d ｜ %s' % (
        len(M), len(MISS), len(COLONLY), len(TIE), TIE[:12]))
    print(u'  采集侧独有(正则族/独立档, 建条目侧另立口径): %s' % (MISS[:14],))
else:
    print(u'两侧对账: 无 corpus/_b62meas.json(采集侧未跑)')
