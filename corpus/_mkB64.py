# -*- coding: utf-8 -*-
"""B64 建条目(第二遍现算, 四源): ⟦A⟧rfc2131(1997, DHCPv4) ⇎ ⟦B⟧rfc3315(2003, DHCPv6) ⇎ ⟦C⟧rfc7083(2013, 只动这一枚参数) ⇎ ⟦D⟧rfc8415(2018, Obsoletes: 3315)。
主轴: 报文发出去没人应答时, 重传退避的封顶在哪一秒——⟦A⟧ 把翻倍序列写死在散文里“up to a maximum of 64 seconds”;
⟦B⟧ 在 §5.5 参数表给 SOL_MAX_RT 120 secs(全文只两枚“120 secs”, 恰是 SOL ⇎ INF 两行), 客户端无从改变;
⟦C⟧ 把同一枚表的同一行用 OLD:/NEW: 重印一遍(120→3600, 比值 30), 并新开一条可下发的选项, 值域 60..86400;
⟦D⟧ 把缺省接成 3600 secs, 收下 C 的选项与越界丢弃句, 同时把 C 从未提过的 REL/DEC_MAX_RC 从 5 改成 4。
第二遍的独立性: 采集侧(_pick64.py)用正则与集合运算; 本遍换成游标档(find 循环)、逐字符形状档、表行的逐列切分档(先按 '|' 再按字符类)、
OLD:/NEW: 的标签配对档、退避序列的面内仿真档(从 4 起翻倍至 64, 不手填)。两遍只在定义一致处对账, 逐键比 corpus/_b64meas.json。
抓取时刻、官网现行状态、各家客户端把 SOL_MAX_RT 实际记多久都只在本机或站外成立, 不进门槛。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
NSRC = 4
ENTRY = u'%s/babeltele/B64_dhcp_retransmit_cap_four_answers.md' % C
PATH = [u'corpus/raw/dhcp/rfc2131.txt', u'corpus/raw/dhcp/rfc3315.txt',
        u'corpus/raw/dhcp/rfc7083.txt', u'corpus/raw/dhcp/rfc8415.txt']
TAGS = [u'A', u'B', u'C', u'D']
LB = dict(zip(TAGS, [u'97 六十四', u'03 一百二', u'13 倍三十', u'18 可下发']))
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN --- (corpus/_wire64.py 把这一段机械切进 audit.py::_b64_scan)
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


# ---- 形状档(逐字符) ----
def shape(i):
    ln = nb = nb2 = ff = cr = na = 0
    ws = True
    asc = True
    hard = False
    for ch in TXT[i]:
        if ch == NL:
            ln += 1
            if not ws:
                nb += 1
            if not asc:
                nb2 += 1
            if ws and hard:
                ff += 1
            ws = True
            asc = True
            hard = False
            continue
        if not ch.isspace():
            ws = False
        if ch not in u' \t\r':
            asc = False
            if ch.isspace():
                hard = True
        if ch == u'\r':
            cr += 1
        if ord(ch) > 127:
            na += 1
    ls = LST[i]
    tail = ls[-1]
    if tail:
        ln += 1
        if not tail.isspace():
            nb += 1
            nb2 += 1
        elif tail.strip(u' \t\r'):
            nb2 += 1
            ff += 1
    return dict(bytes=len(RAWB[i]), chars=len(TXT[i]), lines=len(ls), nonblank=nb,
                nonblank_asciib=nb2, ff_only_lines=ff, cr=cr, nonascii=na,
                bom=1 if RAWB[i][:3] == bytes([239, 187, 191]) else 0,
                formfeed=len([ch for ch in TXT[i] if ord(ch) == 12]),
                maxlen=max(len(l) for l in ls),
                trail=len([l for l in ls if l != l.rstrip()]))


SH = [shape(i) for i in range(NSRC)]
for k in SH[0]:
    F[k] = [SH[i][k] for i in range(NSRC)]
F[u'nb_gap'] = [F[u'nonblank_asciib'][i] - F[u'nonblank'][i] for i in range(NSRC)]
F[u'bytes_span'] = max(F[u'bytes']) - min(F[u'bytes'])
F[u'chars_no_nl'] = [sum(1 for ch in TXT[i] if ch != NL) for i in range(NSRC)]
F[u'rec_close'] = [F[u'lines'][i] - (TXT[i].count(NL) + 1) for i in range(NSRC)]
F[u'sig'] = [hashlib.blake2b(RAWB[i], digest_size=8).hexdigest() for i in range(NSRC)]
F[u'sig_distinct'] = len(set(F[u'sig']))


def hdr_at(l, sp):
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
    if d != 4 or (k < len(l) and l[k] in DIG):
        return False
    if k >= len(l):
        return not sp
    if l[k] != u' ':
        return False
    return bool(l[k + 1:].strip()) if sp else True


def page_end(s, brk):
    if brk:
        if not s.endswith(u']'):
            return False
        e = s.rfind(u'[Page ')
        if e < 0:
            return False
        tail = s[e + 6:-1]
    else:
        e = s.rfind(u'Page ')
        tail = s[e + 5:] if e >= 0 else u''
    if e < 0 or tail == u'':
        return False
    for ch in tail:
        if ch not in DIG:
            return False
    return s[e - 1:e] in (u' ', u'[', u'')


def is_hdr(l):
    return hdr_at(l, True) or hdr_at(l, False)


def is_foot(l):
    return page_end(l.strip(), True) or page_end(l.strip(), False)


four(u'hdr_sp', lambda i: len([l for l in LST[i] if hdr_at(l, True)]))
four(u'hdr_ns', lambda i: len([l for l in LST[i] if hdr_at(l, False) and not hdr_at(l, True)]))
four(u'hdr', lambda i: len([l for l in LST[i] if is_hdr(l)]))
four(u'foot', lambda i: len([l for l in LST[i] if is_foot(l)]))
four(u'foot_brk', lambda i: len([l for l in LST[i] if page_end(l.strip(), True)]))
four(u'pg', lambda i: occ(TXT[i], u'[Page '))
F[u'pagelines'] = [F[u'hdr'][i] + F[u'foot'][i] for i in range(NSRC)]
F[u'pages_est'] = [F[u'formfeed'][i] if F[u'formfeed'][i] else max(F[u'hdr'][i], F[u'foot'][i])
                   for i in range(NSRC)]
F[u'hdr_ledger'] = [F[u'hdr_sp'][i] + F[u'hdr_ns'][i] - F[u'hdr'][i] for i in range(NSRC)]
F[u'hdr_ledger_sum'] = sum(F[u'hdr_ledger'])
F[u'ff_foot_sum'] = sum([F[u'formfeed'][i] - F[u'foot'][i] for i in range(NSRC)])
F[u'nb_ff_sum'] = sum(F[u'nb_gap'][i] - F[u'ff_only_lines'][i] for i in range(NSRC))
F[u'pg_foot_sum'] = sum(F[u'pg'][i] - F[u'foot'][i] for i in range(NSRC))

# ---- 字面族(与采集侧同名同义) ----
LITK = {
    u'max64': u'maximum of 64 seconds', u'd64': u'64 seconds', u'd4s': u'4 seconds', u'd8s': u'8 seconds',
    u'reback': u'randomized exponential backoff', u'retrans': u'retransmi', u'solmaxrt': u'SOL_MAX_RT',
    u'infmaxrt': u'INF_MAX_RT', u'reqmaxrt': u'REQ_MAX_RT', u'renmaxrt': u'REN_MAX_RT', u'rebmaxrt': u'REB_MAX_RT',
    u'reqmaxrc': u'REQ_MAX_RC', u'relmaxrc': u'REL_MAX_RC', u'decmaxrc': u'DEC_MAX_RC', u'cnfmaxrt': u'CNF_MAX_RT',
    u'solmaxdelay': u'SOL_MAX_DELAY', u'soltimeout': u'SOL_TIMEOUT', u'rectimeout': u'REC_TIMEOUT',
    u's120': u'120 secs', u's3600': u'3600 secs', u's600': u'600 secs', u's1sec': u'1 sec',
    u'v86400': u'86400', u'v604800': u'604800', u'v3600': u'3600', u'v120': u'120',
    u'clamp': u'60 <=', u'ignore': u'MUST ignore any', u'irt': u'IRT', u'irc': u'IRC',
    u'infreq': u'Information-request', u'ta': u'IA_TA', u'pd': u'IA_PD',
    u't1': u'T1', u't2': u'T2', u'p50': u'50%', u'p875': u'87.5', u'p05': u'0.5', u'p08': u'0.8',
    u'infin': u'infinity', u'ffffffff': u'0xffffffff', u'preferre': u'shortest preferred lifetime',
    u'leasedur': u'lease duration', u'oldlbl': u'OLD:', u'newlbl': u'NEW:',
    u'discard': u'discards the IA', u'optionreq': u'Option Request option',
}
for k in sorted(LITK):
    four(u'lit_' + k, lambda i, k=k: occ(TXT[i], LITK[k]))
F[u'lit_durdef'] = [occ(TXT[i], u'0.5 * duration_of_lease') for i in range(NSRC)]
F[u'lit_durdef875'] = [occ(TXT[i], u'0.875 * duration_of_lease') for i in range(NSRC)]
F[u'lit_durdef875_fold'] = [occ(FO[i], u'0.875 * duration_of_lease') for i in range(NSRC)]
F[u'lit_durdef875_gap'] = [F[u'lit_durdef875_fold'][i] - F[u'lit_durdef875'][i] for i in range(NSRC)]
F[u'lit_durdef875_gap_sum'] = sum(F[u'lit_durdef875_gap'])
F[u'lit_durword'] = [occ(TXT[i], u'duration_of_lease') for i in range(NSRC)]
F[u'lit_t1def'] = [occ(TXT[i], u'T1 defaults') + occ(TXT[i], u'T2 defaults') for i in range(NSRC)]
F[u'lit_sameacross'] = [occ(TXT[i], u'the same values across all IAs') for i in range(NSRC)]
F[u'lit_iface'] = [occ(TXT[i], u'applies only to the network interface') for i in range(NSRC)]
F[u'lit_retain'] = [occ(TXT[i], u'this value is expected to be retained') for i in range(NSRC)]
F[u'lit_retain_sp'] = [occ(TXT[i], u'retained for as long as practically possible') for i in range(NSRC)]
F[u'lit_srt_minus_irt'] = [F[u'lit_solmaxrt'][i] - F[u'lit_irt'][i] for i in range(NSRC)]

# ---- 参数表档(逐字符切列: 先按 '|' 分格, 无 '|' 则按字符类切 “名 / 数 / 单位 / 述”) ----
K = [u'SOL_MAX_RT', u'INF_MAX_RT', u'REN_MAX_RT', u'REB_MAX_RT', u'REQ_MAX_RT', u'SOL_TIMEOUT',
     u'REQ_TIMEOUT', u'REB_TIMEOUT', u'INF_TIMEOUT', u'REL_TIMEOUT', u'DEC_TIMEOUT', u'CNF_TIMEOUT',
     u'REC_TIMEOUT', u'SOL_MAX_DELAY', u'CNF_MAX_DELAY', u'INF_MAX_DELAY', u'CNF_MAX_RD',
     u'REQ_MAX_RC', u'REL_MAX_RC', u'DEC_MAX_RC', u'CNF_MAX_RC', u'REC_MAX_RC', u'MAX_RC']


def cell(l):
    """一行切成 (名, 秒值) 或 None: 竖线档按 | 分格, 空白档按 “大写下划线名 + 数 + 单位” 直读。"""
    s = l.strip()
    if not s:
        return None
    if u'|' in s:
        g = [x.strip() for x in s.split(u'|')]
        g = [x for x in g if x]
        if len(g) < 2:
            return None
        nm = g[0]
        q = 0
        while q < len(g[1]) and g[1][q] in WCH:
            q += 1
        dig = u''
        while q < len(g[1]) and (g[1][q] in DIG or g[1][q] == u','):
            dig += g[1][q]
            q += 1
        v = dig
    else:
        j, buf = 0, []
        while j < len(s) and s[j] in WCH:
            j += 1
        while j < len(s) and (s[j] in ALW or s[j] == u'_'):
            buf.append(s[j])
            j += 1
        nm = u''.join(buf)
        d = []
        while j < len(s) and s[j] in WCH:
            j += 1
        while j < len(s) and (s[j] in DIG or s[j] == u','):
            d.append(s[j])
            j += 1
        v = u''.join(d)
    if not nm or nm != nm.upper():
        return None
    if len([ch for ch in nm if ch in ALW or ch == u'_']) < 3:
        return None
    if not v or any(ch not in DIG for ch in v):
        return None
    return nm, int(v)


def tables(i):
    out, cur = [], None
    for n, l in enumerate(LST[i]):
        s = l.strip()
        if (u'Parameter' in s and u'Default' in s and len(s) < 96):
            if cur is not None and cur[1]:
                out.append((cur[0], dict(cur[1])))
            cur = [n, {}]
            continue
        if cur is None:
            continue
        if not s:
            continue
        c = cell(l)
        if c:
            cur[1][c[0]] = c[1]
            continue
        if re.match(u'^\\d+\\.\\d+', s) and cur[1]:
            out.append((cur[0], dict(cur[1])))
            cur = None
    if cur is not None and cur[1]:
        out.append((cur[0], dict(cur[1])))
    return out


TB = [tables(i) for i in range(NSRC)]
four(u'tbl_n', lambda i: len(TB[i]))
F[u'tbl_rows'] = [[len(d) for _, d in TB[i]] for i in range(NSRC)]
F[u'tbl_start'] = [[st for st, _ in TB[i]] for i in range(NSRC)]
F[u'tbl_rows_0'] = [(r[0] if r else 0) for r in F[u'tbl_rows']]
F[u'tbl_row_delta'] = F[u'tbl_rows_0'][3] - F[u'tbl_rows_0'][1]
for k in K:
    F[u'pv_' + k.lower()] = [sorted(set(d[k] for _, d in TB[i] if k in d)) for i in range(NSRC)]
BD = [(k, TB[1][0][1].get(k), TB[3][0][1].get(k)) for k in K] if (TB[1] and TB[3]) else []
BD = [x for x in BD if x[1] is not None and x[2] is not None]
F[u'bd_n'] = len(BD)
F[u'bd_same'] = len([x for x in BD if x[1] == x[2]])
F[u'bd_diff'] = [[x[0], x[1], x[2]] for x in BD if x[1] != x[2]]
F[u'bd_ratio'] = [x[2] // x[1] for x in BD if x[1] and x[2] % x[1] == 0]
F[u'bd_close'] = F[u'bd_same'] + len(F[u'bd_diff']) - F[u'bd_n']
F[u'bd_pv_same'] = len([k for k in K if F[u'pv_' + k.lower()][1] and F[u'pv_' + k.lower()][3]
                        and F[u'pv_' + k.lower()][1] == F[u'pv_' + k.lower()][3]])
F[u'bd_diff_n'] = len(F[u'bd_diff'])
F[u'bd_unproposed'] = [x[0] for x in F[u'bd_diff'] if x[0] not in (u'SOL_MAX_RT', u'INF_MAX_RT')]
F[u'bd_unproposed_n'] = len(F[u'bd_unproposed'])
F[u'cap_ratio_d_b'] = (F[u'pv_sol_max_rt'][3][0] // F[u'pv_sol_max_rt'][1][0]
                       if F[u'pv_sol_max_rt'][1] and F[u'pv_sol_max_rt'][3] else 0)

# ---- OLD:/NEW: 配对档(C 把同一枚表行重印一遍) ----
LBL = (u'OLD:', u'NEW:')


def oldnew(i):
    rows = []
    for n, l in enumerate(LST[i]):
        s = l.strip()
        if s in LBL:
            rows.append((n, s))
    out = []
    k = 0
    while k + 1 < len(rows) and rows[k][1] == u'OLD:' and rows[k + 1][1] == u'NEW:':
        na, nb = rows[k][0], rows[k + 1][0]
        wa = NL.join(LST[i][na + 1:na + 4])
        wb = NL.join(LST[i][nb + 1:nb + 4])
        ca, cb = cell(wa.split(NL)[0] if NL in wa else wa), cell(wb.split(NL)[0])
        if ca:
            nm = ca[0]
        else:
            nm = u''
            jj = 0
            while jj < len(wa) and not nm:
                if not (u'A' <= wa[jj] <= u'Z'):
                    jj += 1
                    continue
                st = jj
                while jj < len(wa) and (u'A' <= wa[jj] <= u'Z' or wa[jj] in DIG or wa[jj] == u'_'):
                    jj += 1
                if jj - st >= 3:
                    nm = wa[st:jj]
        out.append([nm, ca[1] if ca else None, cb[1] if cb else None, nb - na])
        k += 2
    return out, len(rows)


ON = {}
for i, t in enumerate(TAGS):
    pr, nr = oldnew(i)
    ON[t] = pr
    F[u'on_pair_' + t.lower()] = pr
    F[u'on_n_' + t.lower()] = nr
F[u'on_changed'] = [p[0] for p in ON[u'C'] if p[1] and p[2] and p[1] != p[2]]
F[u'on_ratio'] = [p[2] // p[1] for p in ON[u'C'] if p[1] and p[2] and p[2] % p[1] == 0]
F[u'on_span'] = sum(p[3] for p in ON[u'C'])
F[u'on_changed_n'] = len(F[u'on_changed'])
F[u'on_ratio_cap_close'] = (F[u'on_ratio'][0] - F[u'cap_ratio_d_b']) if F[u'on_ratio'] else 1

# ---- 答数档(面内游标现读, 全部毫秒) ----
UNITS = [(u'milliseconds', 1), (u'millisecond', 1), (u'secs', 1000), (u'seconds', 1000),
         (u'sec', 1000), (u'second', 1000), (u'ms', 1)]


def unit_at(t, k):
    for nm, mul in UNITS:
        if t[k:k + len(nm)] == nm:
            e = k + len(nm)
            if e >= len(t) or not is_alpha(t[e]):
                return nm, e
    return None, k


def dur_after(t, needle, rng=240):
    p = t.find(needle)
    if p < 0:
        return (0, u'', u'', 0)
    j = p + len(needle)
    while j < len(t) and t[j] in WCH:
        j += 1
    d = u''
    while j < len(t) and (t[j] in DIG or t[j] == u','):
        d += t[j]
        j += 1
    if not d:
        return (0, u'', u'', 0)
    w = NL in t[p + len(needle):j]
    k = j
    while k < len(t) and t[k] in WCH:
        k += 1
    nm, e = unit_at(t, k)
    v = int(d.replace(u',', u''))
    mul = dict(UNITS)[nm] if nm else 0
    w = w or (nm is not None and NL in t[j:k])
    return ((v * mul if nm else 0), d, nm or u'', 1 if w else 0)


def dur_near(t, needle, span=64):
    """needle 命中后在 span 个字符内读第一枚“数字+单位”, 跨过被排到下一行的动词与空白。"""
    p = t.find(needle)
    if p < 0:
        return (0, u'', u'', 0)
    w = t[p + len(needle):p + len(needle) + span]
    q = 0
    while q < len(w) and w[q] not in DIG:
        q += 1
    if q >= len(w):
        return (0, u'', u'', 0)
    return dur_after(w[q:], u'')


def dur_tagged(t, tag, word, span=96):
    """从每一处 tag 出发, 在 span 个字符内找 word, 找到就读它后面的第一枚数字+单位。"""
    k = t.find(tag)
    while k >= 0:
        seg = t[k + len(tag):k + len(tag) + span]
        if word in seg:
            return dur_near(seg, word)
        k = t.find(tag, k + 1)
    return (0, u'', u'', 0)


ANSN = {u'A': u'up to a maximum of ', u'B': u'SOL_MAX_RT      ',
        u'D': u'| SOL_MAX_RT      | '}
ANS = []
for _i, _t in enumerate(TAGS):
    ANS.append(dur_tagged(TXT[_i], u'NEW:', u'SOL_MAX_RT') if _t == u'C'
               else dur_after(TXT[_i], ANSN[_t]))
F[u'y_ans_ms'] = [ANS[i][0] for i in range(NSRC)]
F[u'y_ans_num'] = [ANS[i][1] for i in range(NSRC)]
F[u'y_ans_unit'] = [ANS[i][2] for i in range(NSRC)]
F[u'y_ans_wrap'] = [ANS[i][3] for i in range(NSRC)]
F[u'y_ans_s'] = [F[u'y_ans_ms'][i] // 1000 for i in range(NSRC)]
F[u'y_ans_distinct'] = len(set(F[u'y_ans_ms']))
F[u'y_ans_max'] = max(F[u'y_ans_ms'])
F[u'y_ans_min'] = min(F[u'y_ans_ms'])
F[u'y_ans_ratio'] = F[u'y_ans_max'] // F[u'y_ans_min']
F[u'y_ans_rem'] = F[u'y_ans_max'] - F[u'y_ans_ratio'] * F[u'y_ans_min']
F[u'y_ans_span_close'] = F[u'y_ans_max'] - F[u'y_ans_ratio'] * F[u'y_ans_min'] - F[u'y_ans_rem']
F[u'y_cd_ans_close'] = F[u'y_ans_ms'][2] - F[u'y_ans_ms'][3]
F[u'y_bc_ans_gap'] = F[u'y_ans_ms'][1] - F[u'y_ans_ms'][0]
F[u'y_db_ans_gap'] = F[u'y_ans_ms'][3] - F[u'y_ans_ms'][1]
# A 的退避序列仿真: 首值 4 秒、每次翻倍、封顶 64 秒, 全部面内现读
F[u'y_a_first'] = dur_near(TXT[0], u'the delay before the first retransmission SHOULD')[0]
F[u'y_a_next'] = dur_near(TXT[0], u'The delay before the next retransmission SHOULD')[0]
F[u'y_a_first_wrap'] = dur_near(TXT[0], u'the delay before the first retransmission SHOULD')[3]
F[u'y_a_next_wrap'] = dur_near(TXT[0], u'The delay before the next retransmission SHOULD')[3]
seq, s = [], F[u'y_a_first']
while s and s <= F[u'y_ans_ms'][0]:
    seq.append(s)
    s *= 2
F[u'a_seq_ms'] = seq
F[u'a_seq'] = [x // 1000 for x in seq]
F[u'a_seq_n'] = len(seq)
F[u'a_doublings'] = len(seq) - 1
F[u'a_ratio'] = seq[-1] // seq[0] if seq else 0
F[u'a_seq_close'] = (seq[-1] - F[u'y_ans_ms'][0]) if seq else 1
F[u'a_seq_next_close'] = (seq[1] - F[u'y_a_next']) if len(seq) > 1 else 1
F[u'a_ratio_pow_close'] = F[u'a_ratio'] - 2 ** F[u'a_doublings']
F[u'a_cap_x_first_close'] = F[u'y_a_first'] * F[u'a_ratio'] - F[u'y_ans_ms'][0]
F[u'a_first_lit'] = [occ(TXT[i], u'randomized by the value of a uniform') for i in range(NSRC)]
F[u'a_cap_ratio_d_b'] = F[u'y_ans_ms'][3] // max(F[u'y_ans_ms'][0], 1)
def num_before(t, needle):
    p = t.find(needle)
    if p < 0:
        return 0
    j = p
    while j and t[j - 1] in WCH:
        j -= 1
    k = j
    while k and t[k - 1] in DIG:
        k -= 1
    return int(t[k:j]) if j > k else 0


def num_after(t, needle):
    p = t.find(needle)
    if p < 0:
        return 0
    j = p + len(needle)
    while j < len(t) and t[j] in WCH:
        j += 1
    k = j
    while k < len(t) and t[k] in DIG:
        k += 1
    return int(t[j:k]) if k > j else 0


F[u'clamp_lo'] = [num_before(TXT[i], u' <= "value" <= ') for i in range(NSRC)]
F[u'clamp_hi'] = [num_after(TXT[i], u' <= "value" <= ') for i in range(NSRC)]
F[u'clamp_span'] = max(F[u'clamp_hi']) // max([x for x in F[u'clamp_lo'] if x])
F[u'clamp_span_close'] = F[u'clamp_span'] * max([x for x in F[u'clamp_lo'] if x]) - max(F[u'clamp_hi'])
F[u'y_clamp_lit'] = [occ(TXT[i], u'60 <= "value" <= 86400') for i in range(NSRC)]
F[u'clamp_cd_lo_close'] = F[u'clamp_lo'][2] - F[u'clamp_lo'][3]
F[u'clamp_cd_hi_close'] = F[u'clamp_hi'][2] - F[u'clamp_hi'][3]
F[u'y_clamp_86400'] = [occ(TXT[i], u'or more than 86400') for i in range(NSRC)]
F[u'y_ignore_srt'] = [occ(TXT[i], u'MUST ignore any SOL_MAX_RT') for i in range(NSRC)]
F[u'y_ignore_inf'] = [occ(TXT[i], u'MUST ignore any INF_MAX_RT') for i in range(NSRC)]
F[u'y_must_ignore_n'] = [occ(TXT[i], u'MUST ignore any') for i in range(NSRC)]

# ---- C ⇎ D 的夹逼句逐行对照(C 先写, D 复写) ----
def clamp_lines(i, needle):
    return [l for n, l in enumerate(LST[i]) if needle in l]


CS = clamp_lines(2, u'60 <= "value"')
DS = clamp_lines(3, u'60 <= "value"')
F[u'y_cd_lines'] = [len(CS), len(DS)]
PAIR = [(a, b) for a, b in zip(CS, DS)]
F[u'al_n'] = len(PAIR)
F[u'al_same_bytes'] = len([1 for a, b in PAIR if a == b])
F[u'al_punct_only'] = len([1 for a, b in PAIR if a != b and pnorm(a) == pnorm(b)])
F[u'al_norm_diff'] = len([1 for a, b in PAIR if pnorm(a) != pnorm(b)])
F[u'al_close'] = F[u'al_same_bytes'] + F[u'al_punct_only'] + F[u'al_norm_diff'] - F[u'al_n']
F[u'al_char_delta'] = sum(len(b) - len(a) for a, b in PAIR)
# 同一句“越界丢弃”在两份里的散文档: 逐字面 ⇎ 折平
SN = [(u'c120', u'values of SOL_MAX_RT and INF_MAX_RT to be 120 seconds.'),
      (u'c3600', u'every 3600 seconds rather than every'),
      (u'clampfull', u'MUST be in this range: 60 <= "value" <= 86400'),
      (u'ignorefull', u'MUST ignore any SOL_MAX_RT option values that are less'),
      (u'max64full', u'The retransmission delay SHOULD be doubled with\n   subsequent retransmissions up to a maximum of 64 seconds.'),
      (u'max64sp', u'The retransmission delay SHOULD be doubled with subsequent retransmissions up to a maximum of 64 seconds.'),
      (u'retainfull', u'this value is expected to be retained for as long as practically possible'),
      (u'samefull', u'The T1/T2 times set in each applicable IA option for a Reply MUST be'),
      (u'discfull', u'If a client receives an IA_NA with T1 greater than T2'),
      (u'reback', u'client MUST adopt a retransmission strategy that incorporates a'),
      (u'ifacefull', u'An updated SOL_MAX_RT value applies only to the network interface')]
for k, s in SN:
    F[u's_' + k] = [occ(TXT[i], s) for i in range(NSRC)]
    F[u's_' + k + u'_fold'] = [occ(FO[i], u' '.join(s.split())) for i in range(NSRC)]
    F[u'wrapgap_' + k] = [F[u's_' + k + u'_fold'][i] - F[u's_' + k][i] for i in range(NSRC)]
F[u'wrap_sn_n'] = len(SN)
F[u'wrap_sn_hit'] = len([1 for k, _ in SN if max(F[u'wrapgap_' + k]) > 0])
F[u'wrap_sn_total'] = sum([sum(F[u'wrapgap_' + k]) for k, _ in SN])
TN = [(u'p05', u'0.5'), (u'p08', u'0.8'), (u'ld', u'lease duration'),
      (u'spl', u'shortest preferred lifetime'), (u'userval', u'MUST use the'),
      (u'zerorule', u'are set to 0')]
for k, s in TN:
    F[u'n_' + k] = [occ(TXT[i], s) for i in range(NSRC)]
    F[u'n_' + k + u'_fold'] = [occ(FO[i], u' '.join(s.split())) for i in range(NSRC)]
    F[u'wrap_' + k] = [F[u'n_' + k + u'_fold'][i] - F[u'n_' + k][i] for i in range(NSRC)]
F[u'wrap_pin_n'] = len(TN)
F[u'wrap_pin_hit'] = len([1 for k, _ in TN if max(F[u'wrap_' + k]) > 0])
F[u'wrap_total'] = sum([sum(F[u'wrap_' + k]) for k, _ in TN])

# ---- 规范窗(答数行回溯到最近编号标题) ----
RULE = {u'A': u'up to a maximum of 64 seconds', u'B': u'SOL_MAX_RT      120 secs',
        u'C': u'SOL_MAX_RT     3600 secs', u'D': u'| SOL_MAX_RT      | 3600 secs'}


def headnum(l):
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
    SECN.append(headnum(ls[a]))
F[u'sec_w'] = [list(w) for w in SECW]
F[u'sec_num'] = SECN
F[u'sec_a'] = [w[0] for w in SECW]
F[u'sec_b'] = [w[1] for w in SECW]
F[u'sec_head'] = [LST[i][SECW[i][0]].strip()[:64] for i in range(NSRC)]
four(u'sec_hit', lambda i: len([n for n, l in enumerate(LST[i]) if RULE[TAGS[i]] in l]))
OFF = []
for i in range(NSRC):
    o, s = [], 0
    for l in LST[i]:
        o.append(s)
        s += len(l) + 1
    OFF.append(o)


def wend(i):
    b = SECW[i][1]
    return OFF[i][b] - 1 if b < len(OFF[i]) else len(TXT[i])


F[u'sec_len'] = [len(NL.join(LST[i][SECW[i][0]:SECW[i][1]])) for i in range(NSRC)]
for i in range(NSRC):
    F[u'sec_len_' + TAGS[i].lower()] = F[u'sec_len'][i]
    F[u'sec_off_' + TAGS[i].lower()] = [OFF[i][SECW[i][0]], wend(i)]
WINS = [(u'solmaxrt', u'SOL_MAX_RT'), (u'infmaxrt', u'INF_MAX_RT'), (u'v86400', u'86400'),
        (u's120', u'120 secs'), (u's3600', u'3600 secs'), (u'ignore', u'MUST ignore any'),
        (u't1', u'T1'), (u'infin', u'infinity')]
for k, s in WINS:
    F[u'secw_' + k] = [occ(TXT[i], s, OFF[i][SECW[i][0]], wend(i)) for i in range(NSRC)]
    F[u'outw_' + k] = [F[u'lit_' + k][i] - F[u'secw_' + k][i] for i in range(NSRC)]
for k, s in ((u'may', u'MAY'), (u'must', u'MUST'), (u'should', u'SHOULD'), (u'should_not', u'MUST NOT')):
    F[u'y_secw_' + k] = [occ(TXT[i], s, OFF[i][SECW[i][0]], wend(i)) for i in range(NSRC)]
    F[u'y_outw_' + k] = [occ(TXT[i], s) - F[u'y_secw_' + k][i] for i in range(NSRC)]

# ---- 时长扫描档(逐字符; 与采集侧的正则档同定义) ----
def dur_scan(t):
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
                out.append((int(t[i:j].replace(u',', u'')) * dict(UNITS)[nm], i, t[i:j], nm,
                            1 if NL in t[j:k] else 0))
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
F[u'dur_ms_lo'] = min([min(F[u'durms_' + TAGS[i].lower()]) for i in range(NSRC)])
F[u'dur_ms_hi'] = max([max(F[u'durms_' + TAGS[i].lower()]) for i in range(NSRC)])
F[u'dur_ratio'] = [F[u'dur_ms_hi'] // F[u'dur_ms_lo']]
F[u'dur_rem'] = [F[u'dur_ms_hi'] % F[u'dur_ms_lo']]
F[u'y_dur_wrap'] = [len([x for x in DURS[i] if x[4]]) for i in range(NSRC)]
F[u'y_dur_wrap_ms'] = [sorted(set(x[0] for x in DURS[i] if x[4])) for i in range(NSRC)]
F[u'y_unit_used'] = [sorted(set(x[3] for x in DURS[i])) for i in range(NSRC)]
F[u'y_unit_n'] = [len(F[u'y_unit_used'][i]) for i in range(NSRC)]
F[u'y_dur_win'] = [sorted(set(x[0] for x in DURS[i] if x[0] > 0
                              and OFF[i][SECW[i][0]] <= x[1] < wend(i))) for i in range(NSRC)]
F[u'y_dur_out'] = [sorted(set(x[0] for x in DURS[i] if x[0] > 0
                              and not (OFF[i][SECW[i][0]] <= x[1] < wend(i)))) for i in range(NSRC)]
F[u'y_dur_win_n'] = [len(x) for x in F[u'y_dur_win']]
F[u'y_dur_out_n'] = [len(x) for x in F[u'y_dur_out']]

# ---- 语汇 / 义务词 / 身份 / 引用 ----
WK = [(u'dhcp', u'DHCP'), (u'dhcp4', u'DHCPv4'), (u'dhcp6', u'DHCPv6'), (u'solicit', u'Solicit'),
      (u'renew', u'Renew'), (u'rebind', u'Rebind'), (u'inform', u'Information-request'),
      (u'timeout', u'timeout'), (u'timer', u'timer'), (u'backoff', u'backoff'),
      (u'retransword', u'retransmission'), (u'admin', u'administrator'), (u'traffic', u'traffic'),
      (u'interface', u'interface'), (u'server', u'server'), (u'client', u'client')]
for k, s in WK:
    four(u'v_' + k, lambda i, s=s: occ(TXT[i], s))
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED'):
    four(u'u_' + w.replace(u' ', u'_').lower(), lambda i, w=w: occ(TXT[i], w))
F[u'oblig_up'] = [F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i] for i in range(NSRC)]
F[u'y_oblig_win'] = [F[u'y_secw_may'][i] + F[u'y_secw_must'][i] + F[u'y_secw_should'][i]
                    for i in range(NSRC)]


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


for w in (u'must', u'should', u'may'):
    four(u'l_' + w, lambda i, w=w: len([x for x in wtok(TXT[i]) if x == w]))
F[u'oblig_low'] = [F[u'l_must'][i] + F[u'l_should'][i] + F[u'l_may'][i] for i in range(NSRC)]
four(u'rfc2119_ref', lambda i: occ(TXT[i], u'2119'))
HK = [(u'cat_std', u'Category: Standards Track'), (u'cat_bcp', u'Category: Best Current Practices'),
      (u'cat_info', u'Category: Informational'), (u'cat_exp', u'Category: Experimental'),
      (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'), (u'issn_hdr', u'ISSN:'),
      (u'req_rc', u'Request for Comments:')]
for k, s in HK:
    four(k, lambda i, s=s: occ(TXT[i], s))
four(u'obsoleted_by', lambda i: occ(LOW[i], u'obsoleted by'))


def cite_occ(t, n, sp=True):
    out, k = 0, t.find(u'RFC')
    while k >= 0:
        p = k + 3
        if sp and p < len(t) and t[p] == u' ':
            p += 1
        if t[p:p + len(n)] == n and (p + len(n) >= len(t) or t[p + len(n)] not in DIG):
            out += 1
        k = t.find(u'RFC', k + 1)
    return out


for n in (u'2131', u'2132', u'3315', u'7083', u'8415', u'4941', u'6221', u'7542', u'2119'):
    four(u'cite_' + n, lambda i, n=n: cite_occ(TXT[i], n))
four(u'cite_3315_sp', lambda i: occ(TXT[i], u'RFC 3315'))
four(u'cite_3315_ns', lambda i: occ(TXT[i], u'RFC3315'))
F[u'cite_ns_3315'] = [F[u'cite_3315_sp'][i] + F[u'cite_3315_ns'][i] for i in range(NSRC)]
F[u'y_cite_ledger_3315'] = [F[u'cite_3315'][i] - F[u'cite_3315_sp'][i] - F[u'cite_3315_ns'][i]
                            for i in range(NSRC)]
F[u'y_cite_ledger_3315_sum'] = sum(F[u'y_cite_ledger_3315'])
F[u'y_self_lit'] = [occ(TXT[i], n) for i, n in ((0, u'2131'), (1, u'3315'), (2, u'7083'), (3, u'8415'))]

# ---- 搬运账(归一只留 a-z0-9; 排序两指针求交) ----
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
    F[u'only_c' + suf] = len([x for x in SS[2] if x not in SS[0] and x not in SS[1] and x not in SS[3]])
    F[u'share_bd' + suf] = len(m_iset(SS[1], SS[3]))
F[u'shell_delta'] = [F[u'lines_ge40'][i] - F[u'lines_ge40_nos'][i] for i in range(NSRC)]
F[u'union_delta'] = F[u'union_abcd'] - F[u'union_abc']
F[u'abcd_incl'] = (sum(F[u'lines_ge40'])
                   - F[u'share_ab'] - F[u'share_ac'] - F[u'share_ad'] - F[u'share_bc'] - F[u'share_bd']
                   - F[u'share_cd']
                   + len(m_iset(m_iset(GE40[0], GE40[1]), GE40[2]))
                   + len(m_iset(m_iset(GE40[0], GE40[1]), GE40[3]))
                   + len(m_iset(m_iset(GE40[0], GE40[2]), GE40[3]))
                   + len(m_iset(m_iset(GE40[1], GE40[2]), GE40[3]))
                   - len(m_iset(m_iset(m_iset(GE40[0], GE40[1]), GE40[2]), GE40[3])))
F[u'abcd_close'] = F[u'abcd_incl'] - F[u'union_abcd']
F[u'y_bd_byte_shared'] = len(m_iset(GERAW[1], GERAW[3]))
F[u'y_bd_norm_only'] = F[u'share_bd'] - F[u'y_bd_byte_shared']
F[u'y_cd_byte_shared'] = len(m_iset(GERAW[2], GERAW[3]))
F[u'y_cd_norm_only'] = F[u'share_cd'] - F[u'y_cd_byte_shared']
NLITS = (u'SOL_MAX_RT', u'64 seconds', u'120', u'3600', u'86400', u'T1', u'T2')
four(u'num_lines', lambda i: len([l for l in LST[i] if len(l.strip()) >= 55
                                  and any(x in l for x in NLITS)]))
for i in range(NSRC):
    F[u'num_lines_' + TAGS[i].lower()] = F[u'num_lines'][i]

# ---- 锚池 ----
SPECIAL = (u'SOL_MAX_RT', u'INF_MAX_RT', u'64 seconds', u'120 secs', u'3600 secs', u'86400',
           u'OLD:', u'NEW:', u'infinity', u'duration_of_lease', u'retransmi', u'60 <=',
           u'MUST ignore any', u'Parameter')
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
F[u'list_clos_n'] = len([k for k in F if (u'_close' in k or u'_ledger' in k) and isinstance(F[k], list)])

ZID = [(u"B64V('y_ans_max')-B64V('y_ans_ratio')*B64V('y_ans_min')-B64V('y_ans_rem')",
        u'跨度: 3 600 000=56×64 000+16 000'),
       (u"B64V('y_cd_ans_close')", u'C 的 NEW 行 ⇎ D 的缺省表行同值'),
       (u"B64V('cap_ratio_d_b')*B64V('y_ans_ms', 1)-B64V('y_ans_ms', 3)", u'表间之比×03 值=18 值'),
       (u"B64V('bd_close')", u'B ⇎ D 同名参数: 同+异=总数'),
       (u"B64V('on_ratio_cap_close')", u'C 的 OLD→NEW 比值=D 表对 B 表的比值'),
       (u"B64V('al_close')", u'夹逼句对照三分档穷尽'),
       (u"B64V('a_ratio')-2**B64V('a_doublings')", u'末项/首项=2^(翻倍次数)'),
       (u"B64V('a_seq_close')", u'仿真末项=A 面内现读的封顶 64 秒'),
       (u"B64V('a_seq_next_close')", u'仿真第二项=A 面内现读的下次重传 8 秒'),
       (u"B64V('a_cap_x_first_close')", u'首值×末首比=封顶'),
       (u"B64V('a_seq_n')-B64V('a_doublings')-1", u'序列项数=翻倍次数+1'),
       (u"B64V('nb_ff_sum')", u'两口径非空行之差=换页符独占行数'),
       (u"B64V('ff_foot_sum')", u'换页符总数=页脚行数'),
       (u"B64V('pg_foot_sum')", u'“[Page ” 子串处数=页脚行数'),
       (u"B64V('hdr_ledger_sum')", u'页眉两档之和=页眉总数'),
       (u"B64V('abcd_close')", u'四份长行容斥=并集实数'),
       (u"B64V('pool_close')", u'锚池分层穷尽'),
       (u"B64V('y_cite_ledger_3315_sum')", u'3315 引用两式相加=引用总数(四份)'),
       (u"B64V('bd_unproposed_n')-2", u'D 自改的两枚恰是 C 没提的 REL/DEC'),
       (u"B64V('on_changed_n')-2", u'C 只改动 SOL/INF 两枚'),
       (u"B64V('lit_durdef875_gap', 0)-B64V('lit_durdef875_fold', 0)", u'A 的 T2 式只在折平档命中(原面 0)'),
       (u"B64V('clamp_span_close')", u'夹逼上下界之比×下界=上界'),
       (u"B64V('y_clamp_lit', 2)-B64V('y_clamp_lit', 3)", u'C ⇎ D 的夹逼字面同现枚数'),
       (u"B64V('wrap_sn_total')-B64V('wrapgap_max64sp', 0)-B64V('wrapgap_retainfull', 3)",
        u'主线跨行差只在 A 的封顶句 ⇎ D 的保留句'),
       (u"B64V('clamp_cd_lo_close')", u'夹迫下界 C⇎D 同值'),
       (u"B64V('clamp_cd_hi_close')", u'夹迫上界 C⇎D 同值'),
       (u"B64V('tbl_row_delta')-B64V('tbl_rows_0', 3)+B64V('tbl_rows_0', 1)", u'D 表比 B 表多出的行数')]
F[u'x_ident_n'] = len(ZID)
# --- SCAN END ---

# ---------- DERIV 登记与正文模板 ----------
K_, ZERO, COLL, SEENX = {}, [], {}, {}
G, LINES, MISSING = {}, [], []
FN = u'B64V'


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


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {u'B64V': BB64}) for e in exprs]
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


BB64 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B64V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
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
        val = eval(args[0], {u'F': F, u'B64V': BB64, u'len': len, u'max': max, u'min': min,
                             u'round': round, u'repr': repr})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]

    def rep(m):
        c = m.group(1).strip()
        if HELP.match(c):
            return eval(c, {u'V': V, u'JOIN': JOIN, u'CLOS': CLOS, u'CLOS4': CLOS4, u'TOK': TOK, u'AT': AT})
        if u'B64V(' not in c:
            return m.group(0)
        assert BARE.match(BCALL.sub(u'0', c)), c
        val = eval(c, {u'B64V': BB64})
        reg(str(val), c.strip(), c.strip())
        return str(val)
    return re.sub(r'\{([^{}]*)\}', rep, t)


class _Ctx(dict):
    def __missing__(self, k):
        MISSING.append(k)
        return u'§' + k


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + _inline(tmpl)).format_map(_Ctx(dict(G, **kw))))

# ---------- 锚 ----------
G[u'A_cap64'] = AT(u'own', u'A', u'up to a maximum of 64 seconds')
G[u'A_reback'] = AT(u'own', u'A', u'randomized exponential backoff')
G[u'A_first4'] = AT(u'own', u'A', u'delay before the first retransmission')
G[u'A_t1def'] = AT(u'own', u'A', u'0.5 * duration_of_lease')
G[u'A_durword'] = AT(u'own', u'A', u'duration_of_lease')
G[u'B_tablerow'] = AT(u'own', u'B', u'SOL_MAX_RT      120 secs')
G[u'B_infbrow'] = AT(u'own', u'B', u'INF_MAX_RT      120 secs')
G[u'B_renrow'] = AT(u'own', u'B', u'REN_MAX_RT      600 secs')
G[u'B_relrow'] = AT(u'own', u'B', u'REL_MAX_RC')
G[u'C_old'] = AT(u'own', u'C', u'SOL_MAX_RT      120 secs')
G[u'C_new'] = AT(u'own', u'C', u'SOL_MAX_RT     3600 secs')
G[u'C_r30'] = AT(u'own', u'C', u'every 3600 seconds rather than every')
G[u'C_clamp'] = AT(u'own', u'C', u'60 <= "value" <= 86400')
G[u'C_why'] = AT(u'own', u'C', u'reducing the aggregated traffic')
G[u'D_default'] = AT(u'own', u'D', u'| SOL_MAX_RT      | 3600 secs')
G[u'D_option'] = AT(u'own', u'D', u'override the')
G[u'D_ignore'] = AT(u'own', u'D', u'MUST ignore any SOL_MAX_RT')
G[u'D_retain'] = AT(u'own', u'D', u'this value is expected to be retained')
G[u'D_iface'] = AT(u'own', u'D', u'applies only to the network interface')
G[u'D_relrow'] = AT(u'own', u'D', u'REL_MAX_RC')
G[u'D_samets'] = AT(u'own', u'D', u'the same values across all IAs')
G[u'D_discard'] = AT(u'0', u'D', u'discards the IA')

# ---------- 正文 ----------
LINE(u'🧭', u"四源字节 {JOIN('bytes')} ⇎ 面内字符 {JOIN('chars')} ⇎ 原文件行 {JOIN('lines')} ⇎ 非空行 {JOIN('nonblank')} ⇎ 最长行 {JOIN('maxlen')} 列: 97 六十四 ⇎ 03 一百二 ⇎ 13 倍三十 ⇎ 18 可下发。体量差在“是不是一整本”: 97 是 v4 协议正文 {V('bytes',0)} 字节／{V('lines',0)} 行, 13 只谈一枚参数 {V('bytes',2)} 字节／{V('lines',2)} 行——四份相差 {V('bytes_span')} 字节。答数窗 {JOIN('sec_len')} 字符(窗行号 {V('sec_a',0)}–{V('sec_b',0)} ⇎ {V('sec_a',1)}–{V('sec_b',1)} ⇎ {V('sec_a',2)}–{V('sec_b',2)} ⇎ {V('sec_a',3)}–{V('sec_b',3)}), 窗标题 {V('sec_head',0)} ⇎ {V('sec_head',1)} ⇎ {V('sec_head',2)} ⇎ {V('sec_head',3)}; needle 在窗内命中 {JOIN('sec_hit')} 处。"
     u"版式: 无空格页眉 {JOIN('hdr_ns')} 行 ⇎ 带空格 {JOIN('hdr_sp')} 行 ⇎ 合计 {JOIN('hdr')} 行(两式之差闭合 {CLOS('hdr_ledger_sum','页眉记账')}); 方括号页脚 {JOIN('foot')} 行 ⇎ “[Page ” 子串 {JOIN('pg')} 处(闭合 {CLOS('pg_foot_sum','页脚两档')}), 四份全靠换页符分页: 换页符 {JOIN('formfeed')} ⇎ 页脚 {JOIN('foot')} ⇎ 行尾空格 {JOIN('trail')} 三式逐份全等(合计闭合 {CLOS('ff_foot_sum','换页符−页脚')}); 非空行有两个口径——按 isspace 判空得 {JOIN('nonblank')}, 只认空格/制表/回车得 {JOIN('nonblank_asciib')}, 差 {JOIN('nb_gap')} 恰是换页符独占行 {JOIN('ff_only_lines')} 行(闭合 {CLOS('nb_ff_sum','两口径之差')})。编码层: BOM {CLOS4('bom','带 BOM')} 份 ⇎ 非 ASCII 码点 {JOIN('nonascii')} 枚 ⇎ 回车 {CLOS4('cr','回车符')} 枚, 四份签名 {V('sig_distinct')} 种(blake2b 前 16 位)。")

LINE(u'📐', u"答数是怎么写出来的: 97 把它埋在散文里 {A_cap64}——同一段先给首枚延时 {A_first4}, 再要求“每次翻倍”, 于是序列由面内仿真得出: {V('a_seq')} 秒共 {V('a_seq_n')} 项 ⇎ 翻倍 {V('a_doublings')} 次 ⇎ 末项÷首项={V('a_ratio')}(与答数闭合 {CLOS('a_seq_close','仿真末项⇎封顶')}。03/18/13 把答数写成表格行: 逐字符切列后 97 的表块 {V('tbl_n',0)} 张 ⇎ 03 {V('tbl_n',1)} 张 {V('tbl_rows_0',1)} 行 ⇎ 13 {V('tbl_n',2)} 张 ⇎ 18 {V('tbl_n',3)} 张 {V('tbl_rows_0',3)} 行(表头行号 {V('tbl_start',1)} ⇎ {V('tbl_start',3)}), 18 比 03 多出 {V('tbl_row_delta')} 行。"
     u"表格是可比性的前提: 03 ⇎ 18 都有值的同名参数 {V('bd_n')} 枚, 其中 {V('bd_same')} 枚逐字同值 ⇎ {V('bd_diff_n')} 枚不同 {V('bd_diff')}(同+异−总 闭合 {CLOS('bd_close','表对照')}), 整除比值列 {V('bd_ratio')}。两枚 120→3600 的比是 {V('cap_ratio_d_b')} 倍, 另两枚是 5→4。"
     u"13 不参与表格, 它把 03 的那两行原样重印再改: OLD:/NEW: 标签 {V('on_n_c')} 枚, 成对解出 {V('on_pair_c')}(前缀/后缀两对无秒数, 行距合计 {V('on_span')}), 改动参数 {V('on_changed')} ⇎ 比值 {V('on_ratio')}——比值与 18 的表间比闭合 {CLOS('on_ratio_cap_close','C 的 NEW 比 D 的表')}。可 18 落地的不止这两枚: 它自己另改了 {V('bd_unproposed_n')} 枚 {V('bd_unproposed')}, 13 通篇没提(REL/DEC_MAX_RC 由 5 改 4)。")

LINE(u'⚖', u"三枚答数(64 ⇎ 120 ⇎ 3600 秒)不在同一量纲上比大小, 得先问“封顶管的是哪一步”: 97 管的是 v4 客户端自己翻倍的上限 {A_cap64}, 它同一份里对“何时续租”另有 T1/T2 缺省式 {A_t1def}(基准写作标识符 {A_durword}, 面内 {V('lit_durword',0)} 处); 03 把 v6 的重传封顶写进参数表 {B_tablerow}, 同表另一枚 120 秒是 {B_infbrow}, 全文“120 secs”字面 {JOIN('lit_s120')} 处恰为这两行, 其余上限另档(600 秒 {B_renrow} ⇎ 次数封顶 {B_relrow}); 13 把 120 判为“在真实部署里太小” {C_why}, 于是逐行重印 {C_old}→{C_new}, 并给出换算句 {C_r30}; 18 收下缺省 {D_default}, 又把决定权交给网络 {D_option}。"
     u"答数逐份现读(毫秒): {JOIN('y_ans_ms')} ⇎ 单位 {JOIN('y_ans_unit')} ⇎ 去重 {V('y_ans_distinct')} 枚; 两端之比 {V('y_ans_ratio')} 倍余 {V('y_ans_rem')}(闭合 {CLOS('y_ans_span_close','跨度')}))。13 ⇎ 18 的答数彼此闭合 {CLOS('y_cd_ans_close','C⇎D 同值')}——提案与标准在数值上无差, 差在“谁来写这行”: 03 只有表, 18 有表 ⇎ 有选项 ⇎ 有丢弃句。")

LINE(u'🔁', u"换代链上谁改了什么: 03 {B_tablerow} 把值钉成常量(SOL_MAX_RT 字样全篇只 {JOIN('lit_solmaxrt')} 处, 03 的 {V('lit_solmaxrt',1)} 处都在表与其提及行), 13 用一整个选项把它变可下发(SOL_MAX_RT {V('lit_solmaxrt',2)} 处 ⇎ IRT 词根 {V('lit_irt',2)} 处, 差 {V('lit_srt_minus_irt',2)}) ⇎ 18 两处都留(表 {V('lit_solmaxrt',3)} ⇎ IRT {V('lit_irt',3)}, 差 {V('lit_srt_minus_irt',3)}), 而 97 通篇 {JOIN('lit_solmaxrt')} 处——它连这个词都没有, 它有自己的 {A_cap64}。"
     u"18 复写 13 的夹逼句: 含夹逼式的行 13 {V('y_clamp_lit',2)} 行 ⇎ 18 {V('y_clamp_lit',3)} 行, 逐行对照 {V('al_n')} 行里字节全等 {V('al_same_bytes')} ⇎ 仅标点差 {V('al_punct_only')} ⇎ 归一也不同 {V('al_norm_diff')}(闭合 {CLOS('al_close','夹逼句对照')}), 字符净差 {V('al_char_delta')}。"
     u"下发不等于照收: 18 在收下选项的同时写下越界即弃 {D_ignore} ⇎ 同份另一枚 {V('y_ignore_inf',3)} 处(INF_MAX_RT 档), 全篇 MUST ignore any {JOIN('y_must_ignore_n')} 处 ⇎ 13 {V('y_must_ignore_n',2)} 处; “or more than 86400” {JOIN('y_clamp_86400')} 处。窗口内 ⇎ 窗外: SOL_MAX_RT 在窗内 {JOIN('secw_solmaxrt')} ⇎ 窗外 {JOIN('outw_solmaxrt')}, “86400” 窗内 {JOIN('secw_v86400')} ⇎ 窗外 {JOIN('outw_v86400')}——18 的答数窗只吞下表格那一行, 选项正文整节落在窗外。")

LINE(u'🧪', u"封顶的存活期与作用域是 18 独有的两条: 值要留住 {D_retain} ⇎ 只在触发它的那块接口生效 {D_iface}(现读各 {V('lit_retain',3)} ⇎ {V('lit_iface',3)} 处), 13 一条都没写({V('lit_retain',2)} ⇎ {V('lit_iface',2)} 处)——提案只改数值, 标准还得回答“这条覆盖算谁的”。"
     u"时长要归一才可比: 逐字符扫“数字→空白→单位”折成毫秒, 取值集 {V('durms_a')} ⇎ {V('durms_b')} ⇎ {V('durms_c')} ⇎ {V('durms_d')}(出现处含重复 {V('durlit_a')}+{V('durlit_b')}+{V('durlit_c')}+{V('durlit_d')} 枚, 单位种类 {JOIN('y_unit_n')} 种), 两端 {V('dur_ms_lo')} ⇎ {V('dur_ms_hi')} 毫秒, 比 {V('dur_ratio')} 倍余 {V('dur_rem')}。跨行 token(数与单位被排版拆开) {JOIN('y_dur_wrap')} 枚, 其值 {V('y_dur_wrap_ms')}——97 的答数行 {A_cap64} 里“64”与“seconds”同行 {V('y_ans_wrap',0)}, 表格三份的答数行同样不跨行 {V('y_ans_wrap',1)}⇎{V('y_ans_wrap',2)}⇎{V('y_ans_wrap',3)}。"
     u"窗档: 逐份窗内 {JOIN('y_dur_win_n')} 枚 ⇎ 窗外 {JOIN('y_dur_out_n')} 枚。97 的窗外那一把值属于 v4 的其它定时器(退避/重绑), 与“封顶”无关——把整篇的值域当答案会读出另一个问题。")

LINE(u'⛓', u"折行通道: 本遍 {V('wrap_sn_n')} 枚主线针里 {V('wrap_sn_hit')} 枚有差, 逐档合计 {V('wrap_sn_total')} 处——97 的封顶句被排版从 “doubled with” 处劈到下一行: 把换行照抄进 needle 才命中 {V('s_max64full',0)} 处, 按单空格搜整句则原面 {V('s_max64sp',0)} 处 ⇎ 折平 {V('s_max64sp_fold',0)} 处; 18 的保留句同样劈行(原面 {V('s_retainfull',3)} ⇎ 折平 {V('s_retainfull_fold',3)}), 而 13 的 OLD:/NEW: 行、03 的表行、18 的夹逼⇎丢弃句都整行连着写。次轴 {V('wrap_pin_n')} 枚针里 {V('wrap_pin_hit')} 枚有差, 合计 {V('wrap_total')} 处: 97 的 T2 缺省式 “0.875 * duration_of_lease” 把乘数留在上一行、基准词挪到下一行(原面 {V('lit_durdef875',0)} 处 ⇎ 折平 {V('lit_durdef875_fold',0)} 处, 逐份差 {JOIN('lit_durdef875_gap')}, 合计 {V('lit_durdef875_gap_sum')}), 按行搜该字面的复算者读不到它。"
     u"页眉是隐形通道, 只抬高自编号词频: 四份面内自编号子串 {JOIN('y_self_lit')} 处, 引用两式相加与总数逐份闭合(合计差 {V('y_cite_ledger_3315_sum')} )。锚池按“在几份里逐字再现”分层: 仅一份 {V('pool_1')} ⇎ 两份 {V('pool_2')} ⇎ 三份 {V('pool_3')} ⇎ 四份 {V('pool_4')} 条, 合计 {V('pool_n')} 条, 闭合 {CLOS('pool_close','池分层')}。")

LINE(u'📏', u"义务词不成差轴, 成轴的是“答数旁边站着 MUST 还是 MAY”: 全大写 MUST {JOIN('u_must')} ⇎ SHOULD {JOIN('u_should')} ⇎ MAY {JOIN('u_may')} ⇎ MUST NOT {JOIN('u_must_not')} 处, 三词合计 {JOIN('oblig_up')}; 小写词界档 must {JOIN('l_must')} ⇎ should {JOIN('l_should')} ⇎ may {JOIN('l_may')} ⇎ 合计 {JOIN('oblig_low')}。窗内 ⇎ 窗外: MUST {JOIN('y_secw_must')} ⇎ {JOIN('y_outw_must')}, SHOULD {JOIN('y_secw_should')} ⇎ {JOIN('y_outw_should')}, MAY {JOIN('y_secw_may')} ⇎ {JOIN('y_outw_may')}, 窗内三词合计 {JOIN('y_oblig_win')}——97 的答数句挂 SHOULD(散文), 18 的答数行只是表里一个数, 它的义务句全在窗外那一节({D_ignore})。RFC 2119 被引 {JOIN('rfc2119_ref')} 次。")

LINE(u'🗓', u"参数名整套换代是可判的: SOL_MAX_RT {JOIN('lit_solmaxrt')} ⇎ INF_MAX_RT {JOIN('lit_infmaxrt')} ⇎ REQ_MAX_RT {JOIN('lit_reqmaxrt')} ⇎ REN_MAX_RT {JOIN('lit_renmaxrt')} ⇎ REB_MAX_RT {JOIN('lit_rebmaxrt')} ⇎ REC_TIMEOUT {JOIN('lit_rectimeout')} 处; 次数封顶一族 REQ_MAX_RC {JOIN('lit_reqmaxrc')} ⇎ REL_MAX_RC {JOIN('lit_relmaxrc')} ⇎ DEC_MAX_RC {JOIN('lit_decmaxrc')}——97 两个家族都不写(各 {V('lit_reqmaxrc',0)}⇎{V('lit_relmaxrc',0)}⇎{V('lit_decmaxrc',0)} 处), 它用散文与“maximum of 64 seconds”表达同一件事。字样档: retransmi 词干 {JOIN('lit_retrans')} ⇎ Solicit {JOIN('v_solicit')} ⇎ Information-request {JOIN('lit_infreq')} ⇎ Renew {JOIN('v_renew')} ⇎ Rebind {JOIN('v_rebind')} 处; 13 只谈两枚参数, 它的 Solicit {V('v_solicit',2)} 次是四份最少。"
     u"infinity 一族的两种写法: 'infinity' {JOIN('lit_infin')} 处 ⇎ '0xffffffff' {JOIN('lit_ffffffff')} 处 ⇎ 97 把它用在“无限租约”那一行, 03/18 用于寿命与 T1/T2; “shortest preferred lifetime” {JOIN('lit_preferre')} 处 ⇎ v4 的 duration_of_lease {JOIN('lit_durword')} 处——同一个“什么时候续租”问题, v4 用租约时长、v6 用首选寿命作基准。")

LINE(u'🧾', u"身份与废止链独立一轴: Category: Standards Track {JOIN('cat_std')} 处 ⇎ Informational {JOIN('cat_info')} ⇎ Experimental {JOIN('cat_exp')}; Obsoletes 头 {JOIN('obs_hdr')} 处(97 抬头一枚 ⇎ 18 废止 03)⇎ Updates 头 {JOIN('upd_hdr')} 处(只有 13 写它更新 03)⇎ ISSN {JOIN('issn_hdr')} ⇎ Request for Comments 行 {JOIN('req_rc')} 处四份都有; 正文里 obsoleted by {JOIN('obsoleted_by')} 处(全在 18 的对照附录)。"
     u"引用网: RFC 2131 {JOIN('cite_2131')} ⇎ 3315 {JOIN('cite_3315')} ⇎ 7083 {JOIN('cite_7083')} ⇎ 8415 {JOIN('cite_8415')} ⇎ 2132 {JOIN('cite_2132')} ⇎ 4941 {JOIN('cite_4941')} 次——13 通篇引 03 {V('cite_3315',2)} 次却零次引 18(它早五年), 18 引 13 {V('cite_7083',3)} 次把提案收进标准, 03 引 97 {V('cite_2131',1)} 次。含关键数字的长行(≥55 字符且含 SOL_MAX_RT/64 seconds/120/3600/86400/T1/T2 之一) {JOIN('num_lines')} 行: 97 {V('num_lines_a')} ⇎ 03 {V('num_lines_b')} ⇎ 13 {V('num_lines_c')} ⇎ 18 {V('num_lines_d')}。")

LINE(u'⇄', u"整行搬运(≥40 字符、归一只留 a-z0-9、排序两指针求交): 97⇎03 {V('share_ab')} ⇎ 97⇎13 {V('share_ac')} ⇎ 97⇎18 {V('share_ad')} ⇎ 03⇎13 {V('share_bc')} ⇎ 03⇎18 {V('share_bd')} ⇎ 13⇎18 {V('share_cd')} 行。跨代的两行搬运是 03⇎18 的 {V('share_bd')} 行(表行被逐字节复写: 字节档 {V('y_bd_byte_shared')} 行 ⇎ 只在归一档相同 {CLOS('y_bd_norm_only','仅归一同')} 行), 而提案⇎标准 13⇎18 只有 {V('share_cd')} 行(字节档 {V('y_cd_byte_shared')})——13 用自己的行重印 03 的表, 复写发生在句内不在整行。四份并集 {V('union_abcd')} 行 ⇎ 三份(去 18)并集 {V('union_abc')} 行 ⇒ 加进 18 多 {V('union_delta')} 行; 容斥给 {V('abcd_incl')} ⇎ 实数 {V('union_abcd')}(闭合 {CLOS('abcd_close','容斥')} )。只在本份的长行: 13 {V('only_c')} 行。去页眉页脚只挪动 {CLOS4('shell_delta','含壳−去壳')} 行。")

LINE(u'ℒ', u"方法 ⇒ 面对“同一参数四份文书”, 先问答数在哪种载体里: 本遍把表格做成逐字符切列的谓词(竖线档/空白档两式), 于是“同名参数换了值”“谁多了几行”都是可判口径({V('bd_diff')}); 把 OLD:/NEW: 做成标签配对档, 提案的改动量才有枚数({V('on_pair_c')}); 把 97 的散文翻倍做成仿真档(首值面内现读, 翻倍至封顶), “64 秒”才不是孤立字面。其次把“复写”分两把尺: 整行归一档 {V('share_bd')} ⇎ 逐字节档 {V('y_bd_byte_shared')} ⇎ 夹逼句逐行档 {V('al_same_bytes')}/{V('al_n')}; 宣称与实算之间没有第三把尺可偷——{V('on_ratio')} 倍的改动在 18 落地成 {V('cap_ratio_d_b')} 倍, 两者闭合 {CLOS('on_ratio_cap_close','提案⇎标准之比')}。{V('x_ident_n')} 条恒等式全部由面内现读构成并送门槛重算, 标量闭合 {V('scalar_clos_n')} 枚 ⇎ 总账 {CLOS('scalar_clos_sum','闭合合计')} ⇎ 清单闭合 {V('list_clos_n')} 枚。")

LINE(u'✂️', u"为什么这份编码比答题窗口长 ⇒ 四源各 {JOIN('chars')} 字符 ⇎ 答题窗各 {JOIN('sec_len')} 字符: 18 的全篇是 13 的 {B64V('chars',3)//B64V('chars',2)} 倍, 两窗只差 {B64V('sec_len',3)-B64V('sec_len',2)} 字符。答数各占一行, 但“这一行在表里 ⇎ 在散文里、被谁重印、越界了怎么办、覆盖留住多久、以及标准还自己多改了两枚没人提的参数”要跨四份并排读: 13 的 30 倍改动与 18 的自改 {V('bd_unproposed_n')} 枚在库里是两处不同的字面, 只能逐枚列 {V('bd_diff')}; 97 的 64 秒要靠翻倍仿真({V('a_seq')})才看得出它是序列末项; T2 缺省式要靠折平档({V('lit_durdef875_gap',0)})才读得到。读它请按“这个数由哪份文书、在表内 ⇎ 选项内、整行复写 ⇎ 句内复写、被谁重印”来读, 而不是按“少抄了多少原文”。")

assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
for _e, _n in ZID:
    assert eval(_e, {u'B64V': BB64}) == 0, _n
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
for n in AMETA:
    F[n] = v = AMETA[n]
    reg(str(v), u"%s('%s')" % (FN, n), n)


# ---- 整串打印的列表键: 其中的元素也是判词里的字面数, 按下标补登记算式 ----
# 只补“在正文里出现 ⇎ 不在四份面上逐字出现 ⇎ 还没有算式”的数, 面内字面走 T1 不占 DERIV 键
def _walk(v, path):
    if isinstance(v, list):
        for i, x in enumerate(v):
            for it in _walk(x, path + (i,)):
                yield it
    elif isinstance(v, int) and not isinstance(v, bool):
        yield v, path


def _expr(k, path):
    head = u"%s('%s'%s)" % (FN, k, (u', ' + repr(path[0])) if path else u'')
    return head + u''.join(u'[%d]' % i for i in path[1:])


ELEMS = {}
for kk, vv in F.items():
    for num, pp in _walk(vv, ()):
        if num >= 100:
            ELEMS.setdefault(str(num), []).append(_expr(kk, pp))
SRC_HARD = set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', u''.join(TXT)))
BODY_HARD = sorted(set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', body)
                       if len(m.group(0).rstrip(u'.')) >= 3), key=lambda x: (len(x), x))
NOEXPR = []
for s in BODY_HARD:
    if s in K_ or s in SRC_HARD:
        continue
    got = [e for e in ELEMS.get(s, []) if eval(e, {u'B64V': BB64}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, NOEXPR
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv64.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b64flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms64.txt', 'w', encoding='utf-8', newline=NL).write(
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
json.dump(CH, io.open(u'corpus/_b64checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 字符／非空行 %d／答数 %d 秒／表行 %s／页眉 %d⇎页脚 %d⇎换页 %d)' % (
        os.path.basename(PATH[i]), F[u'bytes'][i], F[u'chars'][i], F[u'nonblank'][i],
        F[u'y_ans_s'][i], (F[u'tbl_rows'][i][0] if F[u'tbl_rows'][i] else u'—'), F[u'hdr'][i], F[u'foot'][i], F[u'formfeed'][i])
    for i in range(NSRC)) +
    u' (四份 RFC Editor 纯文本面, 全 LF, 无 BOM、无非 ASCII 码点; 分页一律按换页符计 %d⇎%d⇎%d⇎%d 页。'
    u'数字一律从面内现读, 一个都不手填; 抓取时刻、官网现行状态与各客户端实际把 SOL_MAX_RT 记多久只在本机或站外成立, 不进门槛)\n' % (
        F[u'pages_est'][0], F[u'pages_est'][1], F[u'pages_est'][2], F[u'pages_est'][3]))
联结 = (u"；联结不是“同一份数据的两种序列化”, 而是“报文发出去没人应答时重传退避封顶多久”在四份一手规范里的四种答法: "
        u"面内现读 97 六十四 %d 秒 ⇎ 03 一百二 %d 秒 ⇎ 13 倍三十 %d 秒 ⇎ 18 可下发 %d 秒"
        u"(单位 %s ⇎ %s ⇎ %s ⇎ %s, 去重 %d 枚, 两端比 %d 倍余 %d); "
        u"97 的 64 秒是翻倍序列的末项: 首值现读 %d 秒, 下次重传 %d 秒, 序列 %s 共 %d 项 ⇎ 翻倍 %d 次 ⇎ 末/首=%d=2^%d, "
        u"它连 SOL_MAX_RT 这个词都只出现 %d 处; 03 把答数钉成参数表里的一行(“120 secs”全文 %d 处, 恰是 SOL ⇎ INF 两行), 客户端无从改变; "
        u"13 用 OLD:/NEW: 把同一行重印成 %d→%d 秒(比值 %d, 改动 %d 枚), 另开出可下发的选项、值域 %d..%d(上下界比 %d); "
        u"18 收下同一枚 %d 秒却另有来历: 与 03 同名的参数 %d 枚里 %d 枚逐字同值 ⇎ %d 枚改动 %s, 其中 %d 枚是 18 自己改的、13 通篇没提; "
        u"可下发不等于照收: 18 的夹逼句与 13 逐行对照 %d 行, 字节全等 %d ⇎ 仅标点差 %d ⇎ 归一也不同 %d(闭合 %d), 字符净差 %+d; "
        u"“越界即弃”句 18 %d 处 ⇎ 13 %d 处, 而覆盖的存活期与接口作用域只有 18 写(%d⇎%d 处); "
        u"次轴“多久去续租”: 97 用 T1=0.5×duration_of_lease ⇎ T2=0.875×(同一标识符全篇 %d 处), 其 T2 式被排版劈在两行(原面 %d ⇎ 折平 %d); "
        u"v6 三份改用 shortest preferred lifetime 作基准(%d⇎%d⇎%d 处)并把 T1/T2 交给服务器下发; "
        u"整行搬运: 03⇎18 归一 %d 行(逐字节 %d ⇎ 仅归一同 %d) ⇎ 13⇎18 归一 %d 行(逐字节 %d)——提案的复写在句内不在整行; "
        u"版式: 四份全靠换页符分页(%d⇎%d⇎%d⇎%d 页), 非空行两口径差 %d⇎%d⇎%d⇎%d 行恰为换页符独占行。\n") % (
    F[u'y_ans_s'][0], F[u'y_ans_s'][1], F[u'y_ans_s'][2], F[u'y_ans_s'][3],
    F[u'y_ans_unit'][0], F[u'y_ans_unit'][1], F[u'y_ans_unit'][2], F[u'y_ans_unit'][3],
    F[u'y_ans_distinct'], F[u'y_ans_ratio'], F[u'y_ans_rem'],
    F[u'y_a_first'] // 1000, F[u'y_a_next'] // 1000, u'→'.join([str(x) for x in F[u'a_seq']]),
    F[u'a_seq_n'], F[u'a_doublings'], F[u'a_ratio'], F[u'a_doublings'], F[u'lit_solmaxrt'][0],
    F[u'lit_s120'][1],
    F[u'on_pair_c'][0][1], F[u'on_pair_c'][0][2], F[u'on_ratio'][0], F[u'on_changed_n'],
    F[u'clamp_lo'][2], F[u'clamp_hi'][2], F[u'clamp_span'],
    F[u'y_ans_s'][3], F[u'bd_n'], F[u'bd_same'], len(F[u'bd_diff']),
    u' ⇎ '.join([u'%s %d→%d' % (x[0], x[1], x[2]) for x in F[u'bd_diff']]), F[u'bd_unproposed_n'],
    F[u'al_n'], F[u'al_same_bytes'], F[u'al_punct_only'], F[u'al_norm_diff'], F[u'al_close'],
    F[u'al_char_delta'],
    F[u'y_ignore_srt'][3], F[u'y_ignore_srt'][2], F[u'lit_retain'][3], F[u'lit_iface'][3],
    F[u'lit_durword'][0], F[u'lit_durdef875'][0], F[u'lit_durdef875_fold'][0],
    F[u'lit_preferre'][1], F[u'lit_preferre'][2], F[u'lit_preferre'][3],
    F[u'share_bd'], F[u'y_bd_byte_shared'], F[u'y_bd_norm_only'],
    F[u'share_cd'], F[u'y_cd_byte_shared'],
    F[u'pages_est'][0], F[u'pages_est'][1], F[u'pages_est'][2], F[u'pages_est'][3],
    F[u'nb_gap'][0], F[u'nb_gap'][1], F[u'nb_gap'][2], F[u'nb_gap'][3])
title = (u'# B64 报文没人应答时重传退避封顶多久，四份规范四种答法：64 秒 ⇎ 120 秒 ⇎ 3600 秒 ⇎ 60–86400 秒可下发（提案改两枚、标准落地四枚，越界的服务器值被当场丢弃）\n')
text = (title + srcline + 联结 +
        u'tags: 答数在表里⇎在散文里 翻倍序列仿真(首值现读) OLD:/NEW: 标签配对 提案比值⇎标准比值 '
        u'同名参数逐枚对照(同⇎异闭合) 标准自改未提案参数 夹逼句整行对照(字节⇎标点⇎归一) 越界即弃 '
        u'覆盖存活期⇎接口作用域 时长归一毫秒 数⇎单位跨行 T2 缺省式折行伪零 值域混入别子系统 '
        u'义务词窗内⇎窗外 自编号词频 归一⇎字节两把搬运尺 版式两口径非空行闭合 锚归属由正文现推 '
        u'闭合账 标量 %d⇎清单 %d 项⇎恒等式 %d 条\n' % (F[u'scalar_clos_n'], F[u'list_clos_n'], F[u'x_ident_n']) +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill64.py 从 corpus/_b64checks.json 与 corpus/_deriv64.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两至三源 %d ⇎ 四源 %d ⇎ 错配 %d ｜ 池内取用 %d／池 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], len(ERR), CH[u'pool_used'], F[u'pool_n']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(F)))
print(u'答数 %s s ⇎ 单位 %s ⇎ 去重 %d ⇎ 跨度 %d=%d×%d+%d' % (
    F[u'y_ans_s'], F[u'y_ans_unit'], F[u'y_ans_distinct'], F[u'y_ans_max'], F[u'y_ans_ratio'],
    F[u'y_ans_min'], F[u'y_ans_rem']))
print(u'表: 块 %s ⇎ 行 %s ⇎ 同名 %d 同 %d 异 %s ⇎ 未提案改动 %s' % (
    F[u'tbl_n'], F[u'tbl_rows'], F[u'bd_n'], F[u'bd_same'], F[u'bd_diff'], F[u'bd_unproposed']))
print(u'OLD/NEW: 标签 %s ⇎ 对 %s ⇎ 比值 %s' % (
    [F[u'on_n_' + t.lower()] for t in TAGS], ON[u'C'], F[u'on_ratio']))
print(u'夹逼对照 %d 行: 字节同 %d ⇎ 标点 %d ⇎ 归一异 %d ⇎ 闭合 %d ⇎ 字差 %d' % (
    F[u'al_n'], F[u'al_same_bytes'], F[u'al_punct_only'], F[u'al_norm_diff'], F[u'al_close'],
    F[u'al_char_delta']))
print(u'退避仿真: 首值 %d ⇎ 序列 %s ⇎ 翻倍 %d ⇎ 末/首 %d' % (
    F[u'y_a_first'], F[u'a_seq'], F[u'a_doublings'], F[u'a_ratio']))
print(u'时长档 %s ⇎ 窗内 %s ⇎ 窗外 %s ⇎ 跨行 %s ⇎ 端点 %d/%d' % (
    [F[u'durms_' + t.lower()] for t in TAGS], F[u'y_dur_win_n'], F[u'y_dur_out_n'],
    F[u'y_dur_wrap'], F[u'dur_ms_lo'], F[u'dur_ms_hi']))
print(u'搬运 share %s ⇎ 字节档 BD %d/%d ⇎ CD %d/%d ⇎ 并集 %d/%d ⇎ 容斥闭合 %d' % (
    [F[u'share_%s%s' % (TAGS[a].lower(), TAGS[b].lower())] for a in range(NSRC) for b in range(a + 1, NSRC)],
    F[u'share_bd'], F[u'y_bd_byte_shared'], F[u'share_cd'], F[u'y_cd_byte_shared'],
    F[u'union_abc'], F[u'union_abcd'], F[u'abcd_close']))
print(u'壳: 页眉 %s/%s ⇎ 页脚 %s ⇎ [Page 子串 %s ⇎ 换页 %s ⇎ 两口径非空行差 %s ⇎ 换页独占 %s' % (
    F[u'hdr_ns'], F[u'hdr_sp'], F[u'foot'], F[u'pg'], F[u'formfeed'], F[u'nb_gap'], F[u'ff_only_lines']))
print(u'窗 %s ⇎ 长 %s ⇎ SOL_MAX_RT 窗内 %s 窗外 %s' % (
    F[u'sec_a'], F[u'sec_len'], F[u'secw_solmaxrt'], F[u'outw_solmaxrt']))
print(u'闭合键 %d 项 ⇎ 恒等式 %d 条 ⇎ 标量合计 %d ⇎ 清单闭合 %d' % (
    F[u'scalar_clos_n'], F[u'x_ident_n'], F[u'scalar_clos_sum'], F[u'list_clos_n']))
MEASP = u'corpus/_b64meas.json'
COLONLY = (u'sig_sha256_16', u'union_all', u'sig_distinct')
if os.path.exists(MEASP):
    M = json.load(io.open(MEASP, encoding='utf-8'))
    TIE, MISSK = [], []
    for k in sorted(M):
        if k in COLONLY:
            continue
        if k not in F:
            MISSK.append(k)
            continue
        got = F[k]
        if isinstance(got, tuple) or (isinstance(got, list) and any(isinstance(x, tuple) for x in got)):
            got = json.loads(json.dumps(got))
        if got != M[k]:
            TIE.append((k, u'建=%s 采=%s' % (got, M[k])))
    print(u'两侧对账(四份纯文本面): 采集键 %d ／ 采集侧独有关 %d(+%d 项声明) ／ 不符 %d ｜ %s' % (
        len(M), len(MISSK), len(COLONLY), len(TIE), TIE[:12]))
    print(u'  采集侧独有(正则族/独立档, 建条目侧另立口径): %s' % (MISSK[:14],))
else:
    print(u'两侧对账: 无 corpus/_b64meas.json(采集侧未跑)')
