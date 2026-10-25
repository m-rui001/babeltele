# -*- coding: utf-8 -*-
"""B65 建条目(第二遍现算, 四源): ⟦A⟧rfc2068(1997) ⇎ ⟦B⟧rfc2616(1999, Obsoletes: 2068)
⇎ ⟦C⟧rfc7230(2014, Obsoletes: 2145, 2616) ⇎ ⟦D⟧rfc9112(2022, STD: 99)。
主轴: 同一个客户端对同一台服务器最多该同时开几条连接——A 把 2 写成“SHOULD maintain AT MOST 2”;
B 留着同一个 2 却把义务翻成“SHOULD NOT maintain more than 2”; C 明文撤数(“does not mandate a particular maximum”);
D 的撤数句与 C 逐字同现, 分歧挪到紧接其后的论证段(C “has a large payload blocks” ⇎ D “transfers very large content would block”)。
第二遍的独立性: 采集侧(_pick65.py)用正则与集合运算; 本遍换成游标档(find 循环逐处数)、逐字符形状档(页眉/页脚按字符类判)、
整行搬运的 bisect 档、数字由句子内游标解析(A ⇎ B 的“2”都不是手填)、义务词大小写档按词界扫小写形、
窗口档先定位正文标题行再按行切。两遍只在定义一致处对账, 逐键比 corpus/_b65meas.json。
抓取时刻、官网现行状态、各家浏览器实际每域开几条、现网服务器空闲超时配多少秒都只在本机或站外成立, 不进门槛。"""
import io, os, re, sys, json, hashlib
from bisect import bisect_left

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
NSRC = 4
ENTRY = u'%s/babeltele/B65_http_connection_ceiling_four_answers.md' % C
PATH = [u'corpus/raw/httpKA/rfc2068.txt', u'corpus/raw/httpKA/rfc2616.txt',
        u'corpus/raw/httpKA/rfc7230.txt', u'corpus/raw/httpKA/rfc9112.txt']
TAGS = [u'A', u'B', u'C', u'D']
LB = dict(zip(TAGS, [u'97 最多二', u'99 不得超', u'14 撤上限', u'22 同句撤']))
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN --- (corpus/_wire65.py 把这一段机械切进 audit.py::_b65_scan)
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


def occ(s, sub):
    return len(pos(s, sub))


def isdig(c):
    return u'0' <= c <= u'9'


def rfcnum_at(s, k):
    """s[k:] 形如 'RFC' + 可选一枚空格 + 四位数 + 非数字 ⇒ 返回 (编号, 消耗长度) 否则 None(游标档, 不用正则)。"""
    if not s.startswith(u'RFC', k):
        return None
    j = k + 3
    if j < len(s) and s[j] == u' ':
        j += 1
    d = u''
    while j < len(s) and isdig(s[j]) and len(d) < 5:
        d += s[j]
        j += 1
    if len(d) != 4:
        return None
    if j < len(s) and isdig(s[j]):
        return None
    return d, j - k


def cite(t, n):
    c, k = 0, 0
    while True:
        i = t.find(u'RFC', k)
        if i < 0:
            return c
        g = rfcnum_at(t, i)
        if g and g[0] == n:
            c += 1
        k = i + 3


def hdr_sp_line(l):
    """带空格页眉 “RFC nnnn …”: 行首 RFC+空格+四位+空格或行尾, 且其后还有内容。"""
    if not l.startswith(u'RFC '):
        return False
    d = u''
    k = 4
    while k < len(l) and isdig(l[k]):
        d += l[k]
        k += 1
    return len(d) == 4 and (k >= len(l) or l[k] == u' ') and bool(l[8:].strip())


def hdr_ns_line(l):
    if not l.startswith(u'RFC'):
        return False
    d = u''
    k = 3
    while k < len(l) and isdig(l[k]):
        d += l[k]
        k += 1
    return len(d) == 4 and (k >= len(l) or l[k] == u' ')


def foot_line(l):
    """页脚: 行尾的 “[Page n]”(署名行与它同处一行, 故只看尾部)。"""
    s = l.strip()
    k = s.find(u'[Page ')
    if k < 0 or not s.endswith(u']'):
        return False
    mid = s[k + 6:-1]
    return bool(mid) and all(isdig(x) for x in mid)


def is_hdr(l):
    return hdr_sp_line(l) or hdr_ns_line(l)


def is_foot(l):
    return foot_line(l)


# ---- 形状 ----
four(u'bytes', lambda i: len(RAWB[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'lines', lambda i: len(LST[i]))
four(u'nonblank', lambda i: len([l for l in LST[i] if l.strip()]))
four(u'maxlen', lambda i: max(len(l) for l in LST[i]))
four(u'trail', lambda i: len([l for l in LST[i] if l != l.rstrip()]))
four(u'cr', lambda i: occ(TXT[i], u'\r'))
four(u'nonascii', lambda i: len([ch for ch in TXT[i] if ord(ch) > 127]))
four(u'bom', lambda i: 1 if RAWB[i][:3] == b'\xef\xbb\xbf' else 0)
four(u'formfeed', lambda i: occ(TXT[i], u'\x0c'))
four(u'nonblank_asciib', lambda i: len([l for l in LST[i] if l.strip(u' \t\r')]))
four(u'ff_only_lines', lambda i: len([l for l in LST[i] if l.strip(u' \t\r') and not l.strip()]))
four(u'nb_gap', lambda i: F[u'nonblank_asciib'][i] - F[u'nonblank'][i])
four(u'hdr_sp', lambda i: len([l for l in LST[i] if hdr_sp_line(l)]))
four(u'hdr_ns', lambda i: len([l for l in LST[i] if hdr_ns_line(l) and l[7:].strip()]))
F[u'hdr_ns'] = [len([l for l in LST[i] if hdr_ns_line(l)]) for i in range(NSRC)]
four(u'hdr', lambda i: F[u'hdr_sp'][i] + F[u'hdr_ns'][i])
four(u'foot', lambda i: len([l for l in LST[i] if is_foot(l)]))
four(u'pg', lambda i: occ(TXT[i], u'[Page '))
four(u'pagelines', lambda i: F[u'hdr'][i] + F[u'foot'][i])
four(u'pages_est', lambda i: max(F[u'hdr'][i], F[u'foot'][i]))
F[u'sig'] = [hashlib.blake2b(r, digest_size=8).hexdigest() for r in RAWB]
F[u'sig_distinct'] = len(set(F[u'sig']))
four(u'toc_lines', lambda i: len([l for l in LST[i]
                                  if (u'...' in l) and l.rstrip()[-1:].isdigit()
                                  and (l.lstrip()[:1].isdigit() or l.lstrip().startswith(u'.'))]))
four(u'nonascii_cp', lambda i: [hex(ord(ch)) for ch in TXT[i] if ord(ch) > 127])
F[u'bc_delta'] = [F[u'bytes'][i] - F[u'chars'][i] for i in range(NSRC)]
F[u'nonascii_utf8_extra'] = [sum(len(ch.encode(u'utf-8')) - 1 for ch in TXT[i] if ord(ch) > 127)
                             for i in range(NSRC)]
F[u'enc_close'] = [F[u'bc_delta'][i] - (3 * F[u'bom'][i] + F[u'nonascii_utf8_extra'][i])
                   for i in range(NSRC)]

# ---- 字面(与采集侧同一批针, 本遍用游标档重数) ----
LITK = {
    u'atmost2': u'AT MOST 2', u'more2': u'more than 2 connections', u'singleuser': u'single-user client',
    u'pn': u'2*N connections', u'shouldlimit': u'SHOULD limit the number',
    u'simcon': u'simultaneous connections', u'simopen': u'simultaneous open connections',
    u'oughttolimit': u'ought to limit', u'specnum': u'specific number of connections',
    u'impractical': u'impractical for many applications', u'nomandate': u'does not mandate a particular maximum',
    u'conservative': u'conservative when opening multiple connections',
    u'headol': u'head-of-line', u'dos': u'denial-of-service',
    u'timeout_h': u'time-out', u'timeout_p': u'timeout', u'orx': u'(or existence)',
    u'leno': u'no requirements on the length', u'graceful': u'issue a graceful',
    u'sustain': u'sustain persistent connections', u'atleastone': u'at least one request per connection',
    u'abortedreq': u'aborted request', u'abortedseq': u'aborted sequence of requests',
    u'methodid': u'request method is idempotent',
    u'keepa_upper': u'Keep-Alive', u'keepa_lower': u'keep-alive', u'closeopt': u'"close"',
    u'persistent': u'persistent connections', u'recovery': u'asynchronous close events',
    u'nu': u'N is the number of simultaneously',
    u'asares': u'As a result, this specification',
    u'ingeneral': u'In General', u'msghttp': u'message/http', u'apchttp': u'application/http',
    u'payloadblk': u'has a large payload blocks subsequent',
    u'bigcontent': u'transfers very large content would block',
    u'sidec': u'undesirable side effects in congested networks',
    u'sided': u'Furthermore, using multiple connections can cause undesirable side',
    u'congnet': u'in congested networks',
    u'srvto_h': u'usually have some time-out value', u'srvto_p': u'usually have some timeout value',
    u'removed2': u'limit of two connections per server has been removed',
    u'seqretry': u'idempotent sequence of requests is no longer required',
    u'retrydef': u'automatically retry a sequence of outstanding',
    u'sec922': u'Section 9.2.2 of [HTTP]',
    u'avoidcong': u'avoid congestion of the Internet',
    u'seqidem': u'request sequence is idempotent',
    u'idemmethods': u'idempotent methods',
    u'idemhave': u'have idempotent methods',
    u'retransseq': u'automatically retransmit an aborted sequence of',
}
for k, s in sorted(LITK.items()):
    four(u'lit_' + k, lambda i, s=s: occ(TXT[i], s))
F[u'lit_two_both'] = [F[u'lit_atmost2'][i] + F[u'lit_more2'][i] for i in range(NSRC)]
F[u'lit_hyphen_gap'] = [F[u'lit_timeout_h'][i] for i in range(NSRC)]
F[u'lit_plain_in_ab'] = [F[u'lit_timeout_p'][i] - F[u'lit_timeout_h'][i] for i in range(NSRC)]
# 句式极性: 同一枚 2 分别挂在哪种义务句式下, 以及两式互不侵入
four(u'pol_a', lambda i: occ(TXT[i], u'SHOULD maintain AT MOST'))
four(u'pol_b', lambda i: occ(TXT[i], u'SHOULD NOT maintain more than'))
F[u'pol_own'] = [F[u'pol_a'][0], F[u'pol_b'][1], 0, 0]
F[u'pol_cross_ab'] = F[u'pol_b'][0]
F[u'pol_cross_ba'] = F[u'pol_a'][1]
F[u'pol_cross_close'] = F[u'pol_b'][0] + F[u'pol_a'][1]
F[u'proxy_cd_sum'] = F[u'lit_pn'][2] + F[u'lit_pn'][3]
four(u'gen_h', lambda i: 1 if F[u'lit_timeout_h'][i] else 0)
four(u'gen_p', lambda i: 1 if F[u'lit_timeout_p'][i] else 0)
F[u'gen_split_close'] = [F[u'gen_h'][i] + F[u'gen_p'][i] - 1 for i in range(NSRC)]

# ---- 重试判据与超时值句: 字面档之外再立折平档(劈行会藏针, 也会丢针) ----
for _k in (u'abortedseq', u'seqidem', u'sidec', u'sided'):
    four(u'lit_' + _k + u'_fold', lambda i, _k=_k: occ(FO[i], u' '.join(LITK[_k].split())))
F[u'srvto_pair_close'] = [F[u'lit_srvto_h'][i] + F[u'lit_srvto_p'][i] - 1 for i in range(NSRC)]
F[u'abortedseq_wrap'] = [F[u'lit_abortedseq_fold'][i] - F[u'lit_abortedseq'][i] for i in range(NSRC)]
F[u'seqidem_wrap'] = [F[u'lit_seqidem_fold'][i] - F[u'lit_seqidem'][i] for i in range(NSRC)]
F[u'sided_wrap'] = [F[u'lit_sided_fold'][i] - F[u'lit_sided'][i] for i in range(NSRC)]
F[u'sidec_wrap'] = [F[u'lit_sidec_fold'][i] - F[u'lit_sidec'][i] for i in range(NSRC)]
# 97 面读不到“序列幂等” ⇎ 99 面读不到“方法幂等”(两式折平档也不侵入)
F[u'retry_form_close'] = F[u'lit_seqidem_fold'][0] + F[u'lit_methodid'][1]
# 撤数宣告只写在 14 的变更附录, 22 不再复述
F[u'rem_decl_close'] = F[u'lit_removed2'][2] + F[u'lit_removed2'][3] - 1
F[u'retrydef_close'] = F[u'lit_retrydef'][0] + F[u'lit_retrydef'][1] + F[u'lit_retrydef'][2]
F[u'sec922_close'] = F[u'lit_sec922'][0] + F[u'lit_sec922'][1] + F[u'lit_sec922'][2]
# 幂等判据回摆: 14⇎22 的重试句改用 “have idempotent methods”, 前两代一律零字面
F[u'idemhave_ab_close'] = F[u'lit_idemhave'][0] + F[u'lit_idemhave'][1]
F[u'idem_cd_n'] = F[u'lit_idemhave'][2] + F[u'lit_idemhave'][3]

# ---- 上限数字由句子内游标解析(不手填) ----
def parse_ceiling(txt, lead):
    k = -1
    while True:
        k = txt.find(lead, k + 1)
        assert k >= 0, lead
        if isdig(txt[k + len(lead)]):
            break
    j = k + len(lead)
    d = u''
    while j < len(txt) and isdig(txt[j]):
        d += txt[j]
        j += 1
    assert d, lead
    return int(d), j


F[u'a_ceil'], _ = parse_ceiling(TXT[0], u'AT MOST ')
F[u'b_ceil'], _ = parse_ceiling(TXT[1], u'more than ')
F[u'ceil_close'] = F[u'a_ceil'] - F[u'b_ceil']
four(u'ceil_docs', lambda i: 1 if (F[u'lit_atmost2'][i] or F[u'lit_more2'][i]) else 0)
F[u'ceil_docs_n'] = sum(F[u'ceil_docs'])
four(u'nomandate_docs', lambda i: 1 if occ(TXT[i], LITK[u'nomandate']) else 0)
F[u'nomandate_docs_n'] = sum(F[u'nomandate_docs'])
F[u'ceil_nomandate_ledger'] = F[u'ceil_docs_n'] + F[u'nomandate_docs_n'] - NSRC

# ---- 答数句(原面 ⇎ 折平 两档) ----
SN = [
    (u'a2', u'A single-user client SHOULD maintain AT MOST 2 connections with any server or proxy.'),
    (u'b2', u'A single-user client SHOULD NOT maintain more than 2 connections with any server or proxy.'),
    (u'proxy', u'A proxy SHOULD use up to 2*N connections to another server or proxy, where N is the number of '
               u'simultaneously active users.'),
    (u'remove', u'Previous revisions of HTTP gave a specific number of connections as a ceiling, but this was found '
                 u'to be impractical for many applications.'),
    (u'c_nmand', u'As a result, this specification does not mandate a particular maximum number of connections'),
    (u'hol_c', u'to avoid the "head-of-line blocking" problem, wherein a request that takes significant server-side '
               u'processing and/or has a large payload blocks subsequent requests on the same connection.'),
    (u'hol_d', u'processing and/or transfers very large content would block subsequent requests on the same '
               u'connection.'),
    (u'cd_same', u'Previous revisions of HTTP gave a specific number of connections as a ceiling, but this was found '
                 u'to be impractical for many applications. As a result, this specification does not mandate a '
                 u'particular maximum number of connections but, instead, encourages clients to be conservative when '
                 u'opening multiple connections.'),
    (u'a_len', u'The use of persistent connections places no requirements on the length of this time-out for '
               u'either the client or the server.'),
    (u'b_len', u'The use of persistent connections places no requirements on the length (or existence) of this '
               u'time-out for either the client or the server.'),
    (u'cd_len', u'The use of persistent connections places no requirements on the length (or existence) of this '
                u'timeout for either the client or the server.'),
    (u'grace_it', u'wishes to time-out it SHOULD issue a graceful close'),
    (u'grace_that', u'A client or server that wishes to time out SHOULD issue a graceful close on the connection'),
    (u'grace_trac', u'close on the transport connection'),
    (u'grace_conn', u'issue a graceful close on the connection'),
    (u'a_retry', u'retransmit the aborted request without user interaction so long as the request method is '
                 u'idempotent'),
    (u'b_retry', u'retransmit the aborted sequence of requests without user interaction so long as the request '
                 u'sequence is idempotent'),
    (u'sust', u'A server SHOULD sustain persistent connections, when possible'),
    (u'oneper', u'Servers SHOULD always respond to at least one request per connection'),
    (u'dosnote', u'such as an excessive number of open connections from a single client'),
    (u'hol', u'Multiple connections are typically used to avoid the "head-of-line'),
    (u'tline_h', u'Servers will usually have some time-out value beyond which they will'),
    (u'tline_p', u'Servers will usually have some timeout value beyond which they will'),
]
for k, s in SN:
    four(u's_' + k, lambda i, s=s: occ(TXT[i], s))
    nf = u' '.join(s.split())
    four(u's_' + k + u'_fold', lambda i, nf=nf: occ(FO[i], nf))
    four(u'wrapgap_' + k, lambda i, k=k: F[u's_' + k + u'_fold'][i] - F[u's_' + k][i])
F[u'wrap_sn_n'] = len(SN)
F[u'wrap_sn_hit'] = len([1 for k, _ in SN if any(F[u'wrapgap_' + k])])
F[u'wrap_sn_total'] = sum(sum(F[u'wrapgap_' + k]) for k, _ in SN)
four(u'sn_strict_docs', lambda i: len([1 for k, _ in SN if F[u's_' + k][i]]))
four(u'sn_fold_docs', lambda i: len([1 for k, _ in SN if F[u's_' + k + u'_fold'][i]]))

# ---- 连字符断行: 同一批词在两代排版里的劈行位置(纯序列化事实) ----
four(u'hyb_eol', lambda i: len([l for l in LST[i] if l.endswith(u'-')]))
four(u'hyb_cont', lambda i: len([1 for a, b in zip(LST[i], LST[i][1:])
                                if a.endswith(u'-') and b.lstrip()[:1].islower()]))
four(u'srv_side_raw', lambda i: occ(TXT[i], u'server-side'))
four(u'srv_side_art', lambda i: occ(FO[i], u'server- side'))
F[u'srv_side_sum'] = [F[u'srv_side_raw'][i] + F[u'srv_side_art'][i] for i in range(NSRC)]
F[u'srv_side_cd_close'] = F[u'srv_side_sum'][2] + F[u'srv_side_sum'][3] - 2

# ---- 同一个节标题的两种排版写法: 原面按写法取针, 折平档把两写法并成一式 ----
CCH = [(u'c64', u'6.4. Concurrency', u'6.4.  Concurrency'),
       (u'd94', u'9.4. Concurrency', u'9.4.  Concurrency')]
for _k, _one, _two in CCH:
    four(u'ch_' + _k, lambda i, s=_one: occ(TXT[i], s))
    four(u'ch_' + _k + u'_two', lambda i, s=_two: occ(TXT[i], s))
    four(u'ch_' + _k + u'_fold', lambda i, s=_one: occ(FO[i], s))
F[u'ch_fold_gain'] = [F[u'ch_c64_fold'][i] - F[u'ch_c64'][i] for i in range(NSRC)]
F[u'ch_d94_gain'] = [F[u'ch_d94_fold'][i] - F[u'ch_d94'][i] for i in range(NSRC)]
F[u'ch_fold_eq'] = [F[u'ch_c64_fold'][i] + F[u'ch_d94_fold'][i]
                    - F[u'ch_c64'][i] - F[u'ch_c64_two'][i] - F[u'ch_d94'][i] - F[u'ch_d94_two'][i]
                    for i in range(NSRC)]
F[u'sn_only_fold'] = [k for k, _ in SN if any(F[u'wrapgap_' + k]) and sum(F[u's_' + k]) == 0]
F[u'wrap_onlyfold_n'] = len(F[u'sn_only_fold'])
# 拼写分家在整句档上的读数: 带连字符句 ⇎ 不带连字符句 各自只活一代
F[u'tline_both_docs'] = [1 if (F[u's_tline_h_fold'][i] or F[u's_tline_p_fold'][i]) else 0 for i in range(NSRC)]
F[u'tline_pair_close'] = [F[u's_tline_h_fold'][i] + F[u's_tline_p_fold'][i] - 1 for i in range(NSRC)]
F[u'cd_verdict_same'] = F[u's_cd_same_fold'][2] + F[u's_cd_same_fold'][3]
F[u'cd_prose_diff'] = F[u's_hol_c_fold'][2] + F[u's_hol_d_fold'][3]
F[u'hol_excl'] = F[u'lit_payloadblk'][3] + F[u'lit_bigcontent'][2]
F[u'cd_verdict_same_minus_hol'] = F[u'cd_verdict_same'] - F[u'cd_prose_diff']
four(u'grace_docs', lambda i: 1 if (F[u's_grace_it_fold'][i] or F[u's_grace_that_fold'][i]) else 0)
F[u'grace_all_close'] = sum(F[u'grace_docs']) - NSRC
F[u'grace_pair_close'] = [F[u's_grace_it_fold'][i] + F[u's_grace_that_fold'][i] - 1 for i in range(NSRC)]
F[u'grace_trac_close'] = [F[u's_grace_trac'][i] + F[u's_grace_conn_fold'][i] - 1 for i in range(NSRC)]
F[u'wrap_proxy_ab'] = F[u'wrapgap_proxy'][0] + F[u'wrapgap_proxy'][1]
F[u'wrap_hit_minus_onlyfold'] = F[u'wrap_sn_hit'] - F[u'wrap_onlyfold_n']

# ---- 小节编号: 同一答数句挂在哪一节 ----
SECP = [(u'practical', [(u'8.1.4', None)]),
        (u'concurrency', [(u'6.4', u'Concurrency'), (u'9.4', u'Concurrency')]),
        (u'failures', [(u'6.5', u'Failures and Timeouts'), (u'9.5', u'Failures and Timeouts')]),
        (u'persistence', [(u'6.2', u'Persistence'), (u'9.3', u'Persistence')]),
        (u'estab', [(u'6.3', u'Establishment'), (u'9.1', u'Establishment')]),
        (u'teardown', [(u'6.7', u'Tear-down'), (u'9.6', u'Tear-down')])]


def sec_hit(l, pfx, title):
    s = l.lstrip()
    if not s.startswith(pfx):
        return False
    r = s[len(pfx):]
    if r.startswith(u'.'):
        r = r[1:]
    if not r[:1].isspace():
        return False
    return True if title is None else r.lstrip().startswith(title)


for key, cands in SECP:
    rows = [[n + 1 for n, l in enumerate(LST[i]) if any(sec_hit(l, p, t) for p, t in cands)]
            for i in range(NSRC)]
    F[u'sec_' + key] = [len(r) for r in rows]
    F[u'sec_' + key + u'_line'] = rows
four(u'sec_keys', lambda i: len([1 for k in (u'practical', u'concurrency', u'failures') if F[u'sec_' + k][i]]))
F[u'sec_pair_close'] = [(F[u'sec_practical'][i] + F[u'sec_concurrency'][i] + F[u'sec_failures'][i])
                         - 2 * F[u'sec_keys'][i] for i in range(NSRC)]
F[u'sec_keys_ledger'] = sum(F[u'sec_keys']) - 6

# ---- 答数行定位 ----
RULE = [u'SHOULD maintain AT MOST 2 connections', u'SHOULD NOT maintain more than 2 connections',
        u'As a result, this specification does not mandate',
        u'As a result, this specification does not mandate']
for i, s in enumerate(RULE):
    nf = u' '.join(s.split())
    F[u'ans_line_' + TAGS[i].lower()] = [n + 1 for n, l in enumerate(LST[i]) if s in l]
    F[u'ans_linefold_' + TAGS[i].lower()] = [n + 1 for n, l in enumerate(LST[i])
                                             if nf in u' '.join(l.split())]
four(u'ans_lit_present', lambda i: 1 if RULE[i] in TXT[i] else 0)
four(u'ans_fold_present', lambda i: 1 if u' '.join(RULE[i].split()) in FO[i] else 0)
four(u'ans_gap', lambda i: F[u'ans_fold_present'][i] - F[u'ans_lit_present'][i])
F[u'ans_line_n'] = [len(F[u'ans_line_' + t.lower()]) for t in TAGS]
F[u'ans_line_close'] = sum(F[u'ans_line_n']) - NSRC

# ---- 窗口: 正文标题行起到下一节标题 ----
def is_sec_head(l):
    s = l.rstrip()
    if not s or s != l.strip() and False:
        return False
    t = l.lstrip()
    k = 0
    while k < len(t) and (isdig(t[k]) or t[k] == u'.'):
        k += 1
    if k == 0 or not t[k:k + 1].isspace():
        return False
    rest = t[k:].lstrip()
    return bool(rest) and rest[0].isupper() and len(rest) < 46 and u'...' not in l


def window(i):
    """返回 (标题行号, 止行号, 窗文本): 标题行取该节正文里第二次出现的那枚(第一次在目录)。"""
    for key in (u'practical', u'concurrency'):
        ls = F[u'sec_' + key + u'_line'][i]
        if len(ls) >= 2:
            h = ls[-1] - 1
            j = h + 1
            while j < len(LST[i]) and not (is_sec_head(LST[i][j]) and j > h):
                j += 1
            return h, j, NL.join(LST[i][h:j])
    raise AssertionError(i)


for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED', u'RECOMMENDED', u'MAY NOT'):
    four(u'u_' + w.replace(u' ', u'_').lower(), lambda i, w=w: occ(TXT[i], w))
F[u'oblig_up'] = [F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i] for i in range(NSRC)]

WIN = [window(i) for i in range(NSRC)]
four(u'sec_head', lambda i: LST[i][WIN[i][0]].strip())
four(u'sec_len', lambda i: len(WIN[i][2]))
four(u'sec_a', lambda i: WIN[i][0] + 1)
four(u'sec_b', lambda i: WIN[i][1])
for w in (u'MUST', u'SHOULD', u'MAY'):
    four(u'secw_' + w.lower(), lambda i, w=w: occ(WIN[i][2], w))
    four(u'outw_' + w.lower(), lambda i, w=w: occ(NL.join(LST[i][:WIN[i][0]] + LST[i][WIN[i][1]:]), w))
    four(u'win_close_' + w.lower(), lambda i, w=w: F[u'secw_' + w.lower()][i] + F[u'outw_' + w.lower()][i]
         - occ(TXT[i], w))
four(u'secw_ought', lambda i: occ(WIN[i][2], u'ought to'))
four(u'outw_ought', lambda i: occ(NL.join(LST[i][:WIN[i][0]] + LST[i][WIN[i][1]:]), u'ought to'))
four(u'secw_atmost', lambda i: occ(WIN[i][2], u'AT MOST'))
four(u'secw_nomandate', lambda i: occ(WIN[i][2], LITK[u'nomandate']))
four(u'secw_lit_pn', lambda i: occ(WIN[i][2], LITK[u'pn']))
four(u'main6_fold', lambda i: len([1 for k in (u'a2', u'b2', u'proxy', u'remove', u'c_nmand', u'cd_len')
                                if F[u's_' + k + u'_fold'][i]]))
four(u'sn_other_fold', lambda i: F[u'sn_fold_docs'][i] - F[u'main6_fold'][i])
for _w in (u'must', u'should', u'may'):
    F[u'%s_win_close' % _w] = [F[u'secw_' + _w][i] + F[u'outw_' + _w][i] - F[u'u_' + _w][i]
                          for i in range(NSRC)]
F[u'must_win_close_sum'] = sum(F[u'must_win_close'])

# ---- 义务词: 全小写词界形(大写 2119 档已在节窗测量前立键) ----


def low_word(t, w):
    """全小写且前后不接字母(大写形与复合词都不算): 逐字符词界档。"""
    c, k = 0, t.find(w)
    while k >= 0:
        a = t[k - 1] if k > 0 else u''
        b = t[k + len(w)] if k + len(w) < len(t) else u''
        alpha = lambda x: bool(x) and (u'a' <= x <= u'z' or u'A' <= x <= u'Z')
        if not alpha(a) and not alpha(b) and t[k:k + len(w)] == w:
            c += 1
        k = t.find(w, k + 1)
    return c


for w in (u'must', u'should', u'may'):
    four(u'lo_' + w, lambda i, w=w: low_word(TXT[i], w))
F[u'oblig_low'] = [F[u'lo_must'][i] + F[u'lo_should'][i] + F[u'lo_may'][i] for i in range(NSRC)]
F[u'rfc2119_ref'] = [occ(TXT[i], u'2119') for i in range(NSRC)]
WK = [(u'persist', u'persistent'), (u'conn', u'connection'), (u'client', u'client'), (u'server', u'server'),
      (u'proxy', u'proxy'), (u'timeoutw', u'timeout'), (u'keepw', u'keep'), (u'retry', u'retry'),
      (u'retransmit', u'retransmi'), (u'idem', u'idempotent'), (u'browser', u'browser'),
      (u'congest', u'congestion'), (u'state', u'state')]
for k, s in WK:
    four(u'v_' + k, lambda i, s=s: occ(TXT[i], s))

# ---- 文档身份 / 世代引用 ----
HK = [(u'cat_std', u'Category: Standards Track'), (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'),
      (u'std_hdr', u'STD:'), (u'bcp_hdr', u'BCP:'), (u'issn_hdr', u'ISSN:'), (u'req_rc', u'Request for Comments:'),
      (u'obsoleted_by', u'obsoleted by'), (u'ise', u'Internet Engineering Task Force (IETF)'),
      (u'in_scope', u'It is beyond the scope of this specification')]
for k, s in HK:
    four(k, lambda i, s=s: occ(TXT[i], s))
four(u'obsoleted_by', lambda i: len(pos(LOW[i], u'obsoleted by')))
SELFN = [u'2068', u'2616', u'7230', u'9112']
for n in (u'2068', u'2616', u'2145', u'7230', u'7231', u'9110', u'9112', u'2119', u'7235'):
    four(u'cite_' + n, lambda i, n=n: cite(TXT[i], n))
F[u'cite_self'] = [cite(TXT[i], SELFN[i]) for i in range(NSRC)]
F[u'selfcite_ledger'] = [F[u'cite_self'][i] - F[u'hdr'][i] for i in range(NSRC)]
F[u'selfcite_close3'] = sum(F[u'selfcite_ledger'][:3])
four(u'cite_http_brk', lambda i: occ(TXT[i], u'[HTTP]'))
four(u'cite_rfc_brk', lambda i: len([1 for k in pos(TXT[i], u'[RFC')
                                     if TXT[i][k + 4:k + 5] in (u' ', None) or isdig(TXT[i][k + 4:k + 5])
                                     and TXT[i].find(u']', k) - k <= 10]))


def rfcbracket(t):
    c, k = 0, t.find(u'[RFC')
    while k >= 0:
        g = rfcnum_at(t, k + 1)
        if g and t[k + 1 + g[1]:k + 1 + g[1] + 1] == u']':
            c += 1
        k = t.find(u'[RFC', k + 1)
    return c


F[u'cite_rfc_brk'] = [rfcbracket(TXT[i]) for i in range(NSRC)]

# ---- 搬运(整行归一; 本遍用 bisect 档求交) ----
def line_index(i, shell=True):
    seen = {}
    for l in LST[i]:
        if not shell and (is_hdr(l) or is_foot(l)):
            continue
        n = pnorm(l)
        if len(l.strip()) >= 40 and len(n) >= 40:
            seen[n] = 1
    return sorted(seen)


def raw_index(i):
    seen = {}
    for l in LST[i]:
        if len(l.strip()) >= 40 and len(pnorm(l)) >= 40:
            seen[l] = 1
    return sorted(seen)


GE40 = [line_index(i, True) for i in range(NSRC)]
GE40N = [line_index(i, False) for i in range(NSRC)]
GERAW = [raw_index(i) for i in range(NSRC)]


def bis_iset(a, b):
    out, m = [], 0
    for x in a:
        k = bisect_left(b, x)
        if k < len(b) and b[k] == x:
            out.append(x)
            m += 1
    return out


def n_union(*sets):
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
            F[u'share_%s%s%s' % (TAGS[a].lower(), TAGS[b].lower(), suf)] = len(bis_iset(SS[a], SS[b]))
    F[u'union_all' + suf] = n_union(*SS)
    F[u'only_a' + suf] = len([x for x in SS[0] if not any(x in SS[j] for j in (1, 2, 3))])
    F[u'only_d' + suf] = len([x for x in SS[3] if not any(x in SS[j] for j in (0, 1, 2))])
F[u'union_abc'] = n_union(GE40[0], GE40[1], GE40[2])
F[u'union_delta'] = F[u'union_all'] - F[u'union_abc']
F[u'shell_delta'] = [F[u'lines_ge40'][i] - F[u'lines_ge40_nos'][i] for i in range(NSRC)]
F[u'share_cd_delta'] = F[u'share_cd'] - F[u'share_cd_nos']
F[u'abcd_incl'] = (sum(F[u'lines_ge40'])
                   - sum(F[u'share_%s%s' % (TAGS[a].lower(), TAGS[b].lower())]
                         for a in range(NSRC) for b in range(a + 1, NSRC))
                   + len(bis_iset(bis_iset(GE40[0], GE40[1]), GE40[2]))
                   + len(bis_iset(bis_iset(GE40[0], GE40[1]), GE40[3]))
                   + len(bis_iset(bis_iset(GE40[0], GE40[2]), GE40[3]))
                   + len(bis_iset(bis_iset(GE40[1], GE40[2]), GE40[3]))
                   - len(bis_iset(bis_iset(bis_iset(GE40[0], GE40[1]), GE40[2]), GE40[3])))
F[u'abcd_close'] = F[u'abcd_incl'] - F[u'union_all']
F[u'y_ab_byte_shared'] = len(bis_iset(GERAW[0], GERAW[1]))
F[u'y_ab_norm_only'] = F[u'share_ab'] - F[u'y_ab_byte_shared']
F[u'y_cd_byte_shared'] = len(bis_iset(GERAW[2], GERAW[3]))
F[u'y_cd_norm_only'] = F[u'share_cd'] - F[u'y_cd_byte_shared']
NLITS = (u'AT MOST', u'more than 2', u'does not mandate', u'ought to limit', u'2*N', u'time-out', u'timeout')
four(u'num_lines', lambda i: len([l for l in LST[i] if len(l.strip()) >= 55
                                  and any(x in l for x in NLITS)]))

# ---- 锚池(与采集侧同定义: 去页壳、归一长度>=55) ----
CNT = {}
for i in range(NSRC):
    for l in LST[i]:
        n = pnorm(l)
        if len(l.strip()) >= 55 and len(n) >= 55 and not (is_hdr(l) or is_foot(l)):
            if n not in CNT:
                CNT[n] = set()
            CNT[n].add(i)
F[u'pool_n'] = len(CNT)
F[u'pool_tier'] = [len([1 for n in CNT if len(CNT[n]) == k]) for k in range(1, NSRC + 1)]
F[u'pool_tier_close'] = sum(F[u'pool_tier']) - F[u'pool_n']
for n in range(1, NSRC + 1):
    F[u'pool_%d' % n] = F[u'pool_tier'][n - 1]
F[u'pool_share1_2068'] = len([n for n in CNT if CNT[n] == {0}])
F[u'pool_share1_2616'] = len([n for n in CNT if CNT[n] == {1}])
F[u'pool_share1_7230'] = len([n for n in CNT if CNT[n] == {2}])
F[u'pool_share1_9112'] = len([n for n in CNT if CNT[n] == {3}])
F[u'pool_share2_ab'] = len([n for n in CNT if CNT[n] == {0, 1}])
F[u'pool_share2_cd'] = len([n for n in CNT if CNT[n] == {2, 3}])
S4 = [n for n in CNT if len(CNT[n]) == 4]


def face_raw(i, norm):
    out = []
    for l in LST[i]:
        if pnorm(l) == norm:
            out.append(l)
    return out


def raw_common(rows):
    common = set(rows[0])
    for r in rows[1:]:
        common = common & set(r)
    return common


def write_axes(rows):
    forms = []
    for r in rows:
        for l in r:
            if l not in forms:
                forms.append(l)
    if len(forms) < 2:
        return []
    if len(set(f.lower() for f in forms)) == 1:
        return [u'case']
    if len(set(f.lower().replace(u'-', u'') for f in forms)) == 1:
        return [u'hyph']
    if len(set(u' '.join(f.lower().replace(u'-', u'').split()) for f in forms)) == 1:
        return [u'space']
    return [u'multi']


S4R = [(n, [face_raw(i, n) for i in range(NSRC)]) for n in S4]
F[u'share4_byte4'] = len([1 for n, rows in S4R if raw_common(rows)])
F[u'share4_notbyte'] = len(S4R) - F[u'share4_byte4']
for _a in (u'case', u'hyph', u'space', u'multi'):
    F[u'share4_axis_' + _a] = len([1 for n, rows in S4R if write_axes(rows) == [_a]])
F[u'share4_axis_close'] = (F[u'share4_axis_case'] + F[u'share4_axis_hyph'] + F[u'share4_axis_space']
                           + F[u'share4_axis_multi'] - F[u'share4_notbyte'])
F[u'pool_share4'] = sorted(n for n in CNT if len(CNT[n]) == NSRC)[:6]
F[u'share4_diff'] = sorted([[u'+'.join(write_axes(rows)), n] for n, rows in S4R if write_axes(rows)])
assert F[u'share4_byte4'] + F[u'share4_notbyte'] == F[u'pool_4']
assert F[u'share4_axis_close'] == 0 and F[u'share4_axis_multi'] == 0

# ---- 候选锚(整行, 含短行里的 SPECIAL 标记) ----
SPECIAL = (u'AT MOST', u'Münster', u'more than 2', u'2*N', u'time-out', u'timeout', u'ought to limit', u'does not mandate',
           u'Keep-Alive', u'keep-alive', u'head-of-line', u'graceful', u'idempotent', u'persistent connections',
           u'8.1.4', u'9.4.', u'MUST', u'SHOULD', u'aborted')
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
F[u'apool_n'] = len(POOLC)
four(u'apool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
for n in range(1, NSRC + 1):
    F[u'apool_%d' % n] = len([p for p in POOLC if p[1] == n])


ATOMFAIL = []


def ATOMSEL(kind, tag, *needles):
    ok = (lambda n: n == 1) if kind == u'own' else (lambda n: n == int(kind))
    got = [p for p in POOLC if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
    if not got:
        got = [p for p in POOLC if p[0] == tag and all(x in p[2] for x in needles)]
    if not got:
        ATOMFAIL.append((kind, tag, needles))
        return None
    return max(got, key=lambda x: (len(x[2]), x[2]))


USEDATOM = []
ANCHORX = []


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    if x is None:
        return u'⟦%s⟧⟨MISSING⟩' % tag
    USEDATOM.append(x[2])
    ANCHORX.append((tag, x[1], x[2]))
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


CLOSK = sorted([k for k in F if (u'_close' in k or u'_ledger' in k)
                and isinstance(F[k], (int, float)) and not isinstance(F[k], bool)])
F[u'scalar_clos_n'] = len(CLOSK)
F[u'scalar_clos_sum'] = sum(F[k] for k in CLOSK)
F[u'list_clos_n'] = len([k for k in F if (u'_close' in k or u'_ledger' in k) and isinstance(F[k], list)])

ZID = [(u"B65V('ceil_close')", u'A ⇎ B 的上限同为一枚 2(两式由句内游标解析)'),
       (u"B65V('ceil_nomandate_ledger')", u'给数的份数+撤数的份数=四份'),
       (u"B65V('pol_cross_close')", u'A 句式在 B 面 ⇎ B 句式在 A 面 都零字面'),
       (u"B65V('proxy_cd_sum')", u'代理侧 2*N 句在 C ⇎ D 整句删除'),
       (u"B65V('gen_split_close', 0)+B65V('gen_split_close', 1)+B65V('gen_split_close', 2)+B65V('gen_split_close', 3)",
        u'每份都恰好落进一种拼写档'),
       (u"B65V('tline_pair_close', 0)+B65V('tline_pair_close', 1)+B65V('tline_pair_close', 2)+B65V('tline_pair_close', 3)",
        u'超时那一句按拼写分两代, 每份各一枚'),
       (u"B65V('wrap_sn_hit')-B65V('wrap_onlyfold_n')", u'有跨行差的针原面一律零命中'),
       (u"B65V('cd_verdict_same')-B65V('cd_prose_diff')", u'撤数句 C⇎D 逐字同现 ⇎ 论证段各一枚'),
       (u"B65V('hol_excl')", u'C 的大 payload 句不在 D ⇎ D 的 very large content 句不在 C'),
       (u"B65V('ans_line_close')", u'四份各有一枚答数行'),
       (u"B65V('sec_pair_close', 0)+B65V('sec_pair_close', 1)+B65V('sec_pair_close', 2)+B65V('sec_pair_close', 3)",
        u'每枚在册标题都是目录+正文成对出现'),
       (u"B65V('sec_keys_ledger')", u'97⇎99 各 1 节 ⇎ 14⇎22 各 2 节, 合计六节'),
       (u"B65V('lit_two_both', 2)+B65V('lit_two_both', 3)", u'撤数的两份里“2 上限”句零字面'),
       (u"B65V('hdr_ns')[0]+B65V('hdr_sp')[0]+B65V('hdr_ns')[1]+B65V('hdr_sp')[1]+B65V('hdr_ns')[2]+B65V('hdr_sp')[2]+B65V('hdr_ns')[3]+B65V('hdr_sp')[3]-B65V('hdr',0)-B65V('hdr',1)-B65V('hdr',2)-B65V('hdr',3)",
        u'页眉两档之和=页眉总数(逐份)'),
       (u"B65V('ff_foot_sum')", u'换页符总数=页脚行数(合计)'),
       (u"B65V('pg_foot_sum')", u'“[Page ” 子串处数=页脚行数(合计)'),
       (u"B65V('nb_ff_sum')", u'两口径非空行之差=换页符独占行数(合计)'),
       (u"B65V('pagelines_close')", u'页壳行两档之和=页眉+页脚'),
       (u"B65V('oblig_up_close')", u'大写三词合计逐份闭合'),
       (u"B65V('oblig_low_close')", u'小写词界三词合计逐份闭合'),
       (u"B65V('must_win_close',0)+B65V('must_win_close',1)+B65V('must_win_close',2)+B65V('must_win_close',3)",
        u'窗内+窗外=MUST 全篇(逐份)'),
       (u"B65V('should_win_close',0)+B65V('should_win_close',1)+B65V('should_win_close',2)+B65V('should_win_close',3)",
        u'窗内+窗外=SHOULD 全篇(逐份)'),
       (u"B65V('may_win_close',0)+B65V('may_win_close',1)+B65V('may_win_close',2)+B65V('may_win_close',3)",
        u'窗内+窗外=MAY 全篇(逐份)'),
       (u"B65V('selfcite_close3')", u'A ⇎ B ⇎ C 的自编号出现处恰为页眉数'),
       (u"B65V('abcd_close')", u'四份长行容斥=并集实数'),
       (u"B65V('pool_tier_close')", u'锚池分层穷尽'),
       (u"B65V('share4_axis_close')", u'四份同现长行的写法差各落一根轴'),
       (u"B65V('share4_byte4')+B65V('share4_notbyte')-B65V('pool_4')", u'归一同现=逐字节同形+有写法差, 两档穷尽四档池'),
       (u"B65V('enc_close',0)+B65V('enc_close',1)+B65V('enc_close',2)+B65V('enc_close',3)",
        u'字节−码位差=BOM 三字节+非 ASCII 的 UTF-8 扩展字节'),
       (u"B65V('y_ab_norm_only')-(B65V('share_ab')-B65V('y_ab_byte_shared'))", u'A⇎B 搬运: 仅归一同=归一同−逐字节同'),
       (u"B65V('y_cd_norm_only')-(B65V('share_cd')-B65V('y_cd_byte_shared'))", u'C⇎D 搬运同式'),
       (u"B65V('lit_plain_in_ab',0)+B65V('lit_plain_in_ab',1)+B65V('lit_timeout_h',0)+B65V('lit_timeout_h',1)",
        u'A ⇎ B 里不带连字符的 timeout 形=超时形总数−带连字符形'),
       (u"B65V('keepa_ab_lower_zero')", u'小写连接选项形在 A ⇎ B 零字面'),
       (u"B65V('nonascii_cp_close')", u'非 ASCII 码点数=去 BOM 后计数'),
       (u"B65V('d_shell_zero')", u'D 没有页眉/页脚/换页符'),
       (u"B65V('grace_all_close')", u'优雅关闭句四份各有且只有一种主语写法'),
       (u"B65V('grace_pair_close',0)+B65V('grace_pair_close',1)+B65V('grace_pair_close',2)+B65V('grace_pair_close',3)",
        u'两代主语式逐份互斥(合计零侵入)'),
       (u"B65V('grace_trac_close',0)+B65V('grace_trac_close',1)+B65V('grace_trac_close',2)+B65V('grace_trac_close',3)",
        u'transport connection ⇎ 只说 connection 两档逐份互斥'),
       (u"B65V('srv_side_cd_close')", u'14 把 server-side 留在行内 ⇎ 22 把它劈在行尾, 两份各一枚'),
       (u"B65V('wrapgap_a2',0)+B65V('wrapgap_b2',1)+B65V('wrapgap_proxy',0)+B65V('wrapgap_proxy',1)"
        u"+B65V('wrapgap_grace_it',0)+B65V('wrapgap_grace_it',1)-6",
        u'97⇎99 的上限句/代理句/优雅关闭句各劈一行(六处)'),
       (u"B65V('wrapgap_cd_same',2)+B65V('wrapgap_cd_same',3)+B65V('wrapgap_hol_c',2)+B65V('wrapgap_hol_d',3)"
        u"+B65V('wrapgap_grace_that',2)+B65V('wrapgap_grace_that',3)+B65V('wrapgap_grace_conn',2)"
        u"+B65V('wrapgap_grace_conn',3)-8",
        u'14⇎22 的撤数段/论证句/新主语式各劈一行(八处)'),
       (u"B65V('srvto_pair_close',0)+B65V('srvto_pair_close',1)+B65V('srvto_pair_close',2)"
        u"+B65V('srvto_pair_close',3)", u'“服务器有超时值”那句每份恰有一种拼写'),
       (u"B65V('retry_form_close')", u'97 面读不到序列幂等式 ⇎ 99 面读不到方法幂等式'),
       (u"B65V('rem_decl_close')", u'撤销二连接上限的宣告只出现在 14 ⇎ 22 不复述'),
       (u"B65V('retrydef_close')", u'“自动重试一串未完成请求”的条件句式只在 D 面'),
       (u"B65V('sec922_close')", u'向 [HTTP] §9.2.2 的委派只写在 22, 前三份零字面'),
       (u"B65V('idemhave_ab_close')", u'“have idempotent methods” 在 97⇎99 零字面'),
       (u"B65V('ch_fold_gain',2)-1", u'14 的目录行用单空格写法, 折平档因此多读一枚'),
       (u"B65V('ch_d94',0)+B65V('ch_d94',1)+B65V('ch_d94',2)+B65V('ch_d94',3)",
        u'单空格写法在四份原面都读不到 22 的节标题'),
       (u"B65V('ch_d94_gain',3)-2", u'22 的标题只有折平档能用单空格针读到(两枚)'),
       (u"B65V('ch_fold_eq',0)+B65V('ch_fold_eq',1)+B65V('ch_fold_eq',2)+B65V('ch_fold_eq',3)",
        u'折平档读数=两种原面写法读数之和'),
       (u"B65V('abortedseq_wrap',2)-1", u'14 面上的 “aborted sequence of requests” 只从折行通道读到'),
       (u"B65V('abortedseq_wrap',0)+B65V('abortedseq_wrap',1)+B65V('abortedseq_wrap',3)",
        u'其余三份该串不靠折行')]
F[u'x_ident_n'] = len(ZID)
F[u'pagelines_close'] = sum(F[u'pagelines']) - sum(F[u'hdr']) - sum(F[u'foot'])
F[u'ff_foot_sum'] = sum(F[u'formfeed']) - sum(F[u'foot'])
F[u'pg_foot_sum'] = sum(F[u'pg']) - sum(F[u'foot'])
F[u'nb_ff_sum'] = sum(F[u'nb_gap']) - sum(F[u'ff_only_lines'])
F[u'oblig_up_close'] = sum(F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i] - F[u'oblig_up'][i]
                           for i in range(NSRC))
F[u'oblig_low_close'] = sum(F[u'lo_must'][i] + F[u'lo_should'][i] + F[u'lo_may'][i] - F[u'oblig_low'][i]
                            for i in range(NSRC))
F[u'keepa_ab_lower_zero'] = F[u'lit_keepa_lower'][0] + F[u'lit_keepa_lower'][1]
F[u'nonascii_cp_close'] = sum(F[u'nonascii'][i] - len(F[u'nonascii_cp'][i]) for i in range(NSRC))
F[u'd_shell_zero'] = F[u'hdr'][3] + F[u'foot'][3] + F[u'formfeed'][3] + F[u'trail'][3]
# --- SCAN END ---

# ---------- DERIV 登记与正文模板 ----------
K_, ZERO, COLL, SEENX = {}, [], {}, {}
G, LINES, MISSING = {}, [], []
FN = u'B65V'


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
        nums = [eval(e, {u'B65V': BB65}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([tuple(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


VKMISS = []


def V(name, i=None, note=u''):
    if name not in F:
        VKMISS.append((name, i))
        return u'?'
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


BB65 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B65V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
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
        val = eval(args[0], {u'F': F, u'B65V': BB65, u'len': len, u'max': max, u'min': min,
                             u'round': round, u'repr': repr})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]

    def rep(m):
        c = m.group(1).strip()
        if HELP.match(c):
            return eval(c, {u'V': V, u'JOIN': JOIN, u'CLOS': CLOS, u'CLOS4': CLOS4, u'TOK': TOK, u'AT': AT})
        if u'B65V(' not in c:
            return m.group(0)
        assert BARE.match(BCALL.sub(u'0', c)), c
        val = eval(c, {u'B65V': BB65})
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
G[u'A_atmost'] = AT(u'own', u'A', u'AT MOST 2 connections')
G[u'A_proxy2n'] = AT(u'own', u'A', u'2*N connections to another')
G[u'A_leno'] = AT(u'own', u'A', u'no requirements on the length of this')
G[u'A_retry'] = AT(u'own', u'A', u'aborted request without user')
G[u'A_idem'] = AT(u'own', u'A', u'request method is')
G[u'A_cong'] = AT(u'own', u'A', u'avoid congestion of the Internet')
G[u'A_timeoutline'] = AT(u'4', u'A', u'usually have some time-out value')
G[u'B_notmore'] = AT(u'own', u'B', u'maintain more than 2 connections')
G[u'B_orx'] = AT(u'3', u'B', u'length (or existence) of')
G[u'B_retry'] = AT(u'own', u'B', u'aborted sequence of requests')
G[u'B_2n'] = AT(u'2', u'B', u'2*N connections')
G[u'B_atleast'] = AT(u'2', u'B', u'always respond to at least one request')
G[u'C_nomandate'] = AT(u'own', u'C', u'does not mandate a particular maximum')
G[u'C_ceiling'] = AT(u'2', u'C', u'a specific number of connections as a')
G[u'C_payload'] = AT(u'own', u'C', u'has a large payload blocks')
G[u'C_sustain'] = AT(u'own', u'C', u'sustain persistent connections, when possible')
G[u'C_concurrency'] = AT(u'own', u'C', u'Concurrency')
G[u'C_dos'] = AT(u'2', u'C', u'characteristic of a denial-of-service attack')
G[u'C_removed'] = AT(u'own', u'C', u'limit of two connections per server has been removed')
G[u'C_retrans'] = AT(u'own', u'C', u'automatically retransmit an aborted sequence of')
G[u'D_content'] = AT(u'own', u'D', u'transfers very large content would block')
G[u'D_since'] = AT(u'own', u'D', u'Furthermore, using multiple connections can cause')
G[u'D_94'] = AT(u'own', u'D', u'9.4.')
G[u'D_nmand'] = AT(u'2', u'D', u'does not mandate a particular maximum')
G[u'D_retrydef'] = AT(u'own', u'D', u'automatically retry a sequence of outstanding')
G[u'D_umlaut'] = AT(u'own', u'D', u'48155')

if ATOMFAIL:
    for kind, tag, needles in ATOMFAIL:
        print(u'--- MISS kind=%s tag=%s needles=%s' % (kind, tag, needles))
        for nd in needles:
            tk = sorted(nd.replace(u'(', u'').replace(u')', u'').split(), key=len)[-1]
            for p in [q for q in POOLC if q[0] == tag and tk in q[2]][:4]:
                print(u'    cross=%s |%s|' % (p[1], p[2]))
    raise SystemExit(1)
for a in ANCHORX:
    print(u'ANCHOR %s cross=%s |%s|' % a)

# ---------- 正文 ----------
LINE(u'🧭', u"四源字节 {JOIN('bytes')} ⇎ 面内字符 {JOIN('chars')} ⇎ 原文件行 {JOIN('lines')} ⇎ 非空行 {JOIN('nonblank')} ⇎ 最长行 {JOIN('maxlen')} 列: 97 最多二 ⇎ 99 不得超 ⇎ 14 撤上限 ⇎ 22 同句撤。"
     u"体量三代收缩: 97 {V('bytes',0)} 字节 ⇎ 99 {V('bytes',1)} 字节(同题正文的第二版) ⇎ 14 {V('bytes',2)} ⇎ 22 {V('bytes',3)}——末两份合起来还不如 99 一份, 因为 22 把语义推给兄弟规范([HTTP] 引 {V('cite_http_brk',3)} 处, 前两份 {V('cite_http_brk',0)}⇎{V('cite_http_brk',1)} 处)。"
     u"版式分两代: 前三份靠换页符分页——换页符 {JOIN('formfeed')} ⇎ 方括号页脚 {JOIN('foot')} ⇎ “[Page ” 子串 {JOIN('pg')} 处(合计闭合 {CLOS('ff_foot_sum','换页符−页脚')} ⇎ {CLOS('pg_foot_sum','页脚两档')}), 页眉两档带空格 {JOIN('hdr_sp')} ⇎ 不带空格 {JOIN('hdr_ns')} ⇎ 合计 {JOIN('hdr')}(闭合 {CLOS('pagelines_close','页壳行')}); "
     u"22 一份页壳全空({CLOS('d_shell_zero','D 无页壳')} 行), 点线目录行 {JOIN('toc_lines')} 也归它独零。非空行两口径: isspace 判空 {JOIN('nonblank')} ⇎ 只认空格/制表/回车 {JOIN('nonblank_asciib')}, 差 {JOIN('nb_gap')} 恰为换页符独占行 {JOIN('ff_only_lines')}(闭合 {CLOS('nb_ff_sum','两口径之差')})。"
     u"编码层: BOM {CLOS4('bom','带 BOM')} 份 ⇎ 非 ASCII 码点 {JOIN('nonascii')} 枚(码位清单 {V('nonascii_cp')}, 闭合 {CLOS('nonascii_cp_close','码点账')}), 字节−码位差 {JOIN('bc_delta')} 由 BOM 三字节与一枚两字节变音符解释(闭合 {CLOS('enc_close','编码差')}); 四份签名 {V('sig_distinct')} 种(blake2b 前 16 位)。")

LINE(u'📐', u"上限数字由句内游标解析, 不手填: 97 那枚 {A_atmost} 读回 {V('a_ceil')} 条, 99 那枚 {B_notmore} 读回 {V('b_ceil')} 条, 两数之差闭合 {CLOS('ceil_close','同为一枚 2')}; 给数的份数 {V('ceil_docs_n')} ⇎ 撤数的份数 {V('nomandate_docs_n')}, 相加对四份闭合 {CLOS('ceil_nomandate_ledger','给数⇎撤数分账')}。"
     u"同一枚 2 挂在不同义务句式下: 97 写 “SHOULD maintain AT MOST {V('a_ceil')}”(本面 {V('pol_a',0)} 处) ⇎ 99 写 “SHOULD NOT maintain more than {V('b_ceil')}”(本面 {V('pol_b',1)} 处); 两式互不侵入——99 面里 97 句式 {V('pol_cross_ab')} 处 ⇎ 97 面里 99 句式 {V('pol_cross_ba')} 处(合计闭合 {CLOS('pol_cross_close','句式互斥')})。"
     u"代理侧另有一枚乘法: 97 写 {A_proxy2n} ⇎ 99 面上同一句 {B_2n}(“2*N connections” 出现处 {JOIN('lit_pn')}), 14 与 22 整句删除(后两份合计 {CLOS('proxy_cd_sum','代理句撤净')}), 连乘数 N 的释义行(“N is the number of simultaneously”)也只活在 {JOIN('lit_nu')} 处⇎前两份。"
     u"撤数不是沉默而是明写: 14 {C_nomandate} ⇎ 22 收下同一句 {D_nmand}, “specific number of connections” {JOIN('lit_specnum')} ⇎ “impractical for many applications” {JOIN('lit_impractical')} ⇎ “does not mandate a particular maximum” {JOIN('lit_nomandate')}——三枚都在 0⇎0⇎1⇎1 档上。"
     u"可“谁宣告把这枚数撤掉”只写了一次: 14 的变更附录 {C_removed}(“limit of two connections per server has been removed” {JOIN('lit_removed2')} 处, 14⇎22 合计对一枚闭合 {CLOS('rem_decl_close','撤数宣告只在 14')})——22 已经不需要解释这件事。")

LINE(u'⚖', u"头条不是“哪个数更大”, 而是“有没有数”: 97 把 2 写成上限 {A_atmost} ⇎ 99 把 2 写成禁令 {B_notmore} ⇎ 14 撤掉数字并解释为什么 {C_ceiling}(这句 22 逐字收下) ⇎ 22 只重写紧跟其后的论证句 {D_content}。"
     u"两代的分歧位置可以逐句判: 把撤数整段(三句连排)当针, 折平档命中 {V('s_cd_same_fold',2)}⇎{V('s_cd_same_fold',3)} 枚 ⇎ 紧接其后的 head-of-line 论证段却各写各的——14 {C_payload} {V('s_hol_c_fold',2)} 枚 ⇎ 22 {D_content} {V('s_hol_d_fold',3)} 枚, 两数之差闭合 {CLOS('cd_verdict_same_minus_hol','撤数句同⇎论证段异')}; "
     u"反向验一次互斥: 14 面里读不到 22 的字面 ⇎ 22 面里读不到 14 的字面(合计 {CLOS('hol_excl','论证句互斥')})。"
     u"次轴(超时那一句)同样分家: 97 {A_leno} 而 99 在同句里插进“(or existence)” {B_orx}——插语出现处 {JOIN('lit_orx')}; 到 14⇎22 这一句还在而拼写换档: “time-out” {JOIN('lit_timeout_h')} ⇎ “timeout” {JOIN('lit_timeout_p')}, 每份恰好落进一档(逐份闭合 {CLOS4('gen_split_close','拼写分代')}); 把整句当针则带连字符版折平 {JOIN('s_tline_h_fold')} ⇎ 不带连字符版 {JOIN('s_tline_p_fold')}, 两份各一枚(闭合 {CLOS('tline_pair_close','超时句两代')}); 同一句“服务器总会有自己的超时值”在锚池里属四份同现档 {A_timeoutline}(归一只留字母数字, 连字符因此消失) ⇎ 原面字面却按世代分家: “have some time-out value” {JOIN('lit_srvto_h')} ⇎ “have some timeout value” {JOIN('lit_srvto_p')}(逐份闭合 {CLOS4('srvto_pair_close','超时值句拼写')})。")

LINE(u'🔁', u"换代链上谁改了谁: 97→99 是废止式改写(99 抬头 `Obsoletes:` {JOIN('obs_hdr')} 处), 99→14 又一枚 Obsoletes 并同时 Updates {JOIN('upd_hdr')}(14 更新的是另一份规范), 22 不再写 Obsoletes 而挂 STD: 99({JOIN('std_hdr')} 处)。正文里“obsoleted by”字样 {JOIN('obsoleted_by')} 处。"
     u"重试粒度改了一格: 97 说中止的是“那一次请求” {A_retry} 且以方法判幂等 {A_idem}(字面 “request method is idempotent” {JOIN('lit_methodid')} 处), 99 把它扩成一串 {B_retry}(“aborted sequence of requests” 原面 {JOIN('lit_abortedseq')} ⇎ 折平 {JOIN('lit_abortedseq_fold')}), 幂等判据随之从方法挪到序列——“request sequence is idempotent” 在四份原面一律零字面, 折平档也只读到 99 的 {V('lit_seqidem_fold',1)} 枚; 97 面读不到序列式 ⇎ 99 面读不到方法式(合计 {CLOS('retry_form_close','判据互斥')})。"
     u"判据在下一代摆回方法: 14 面上那一串还在, 却被劈在行界——严格档 {V('lit_abortedseq',2)} 处 ⇎ 折平档 {V('lit_abortedseq_fold',2)} 枚 {C_retrans}(逐份差 {JOIN('abortedseq_wrap')}), 条件改写成 “have idempotent methods”(原面 {JOIN('lit_idemhave')} 处, 前两代合计 {CLOS('idemhave_ab_close','方法条件式零字面')}); 22 不再自己裁决, 只把条件推给兄弟规范 {D_retrydef}(“Section 9.2.2 of [HTTP]” {JOIN('lit_sec922')} 处, 前三份合计 {CLOS('sec922_close','委派只写在 22')})。 变更附录里 14 还把这两件事并写一行 {C_removed}(“idempotent sequence of requests is no longer required” {JOIN('lit_seqretry')} 处 ⇎ 上限已撤句同一行)。"
     u"义务档位也换代: 14⇎22 新加一句 14 {C_sustain} ⇎ 97⇎99 全无(“sustain persistent connections” {JOIN('lit_sustain')}); 97⇎99 那句“至少应答一次” {B_atleast} 在两份里各 {JOIN('lit_atleastone')} 处而 14⇎22 撤走(合计 {EXPR(F[u'lit_atleastone'][2]+F[u'lit_atleastone'][3], u\"B65V('lit_atleastone',2)+B65V('lit_atleastone',3)\", u'一次应答句在 14⇎22 零字面')} 处)。"
     u"字面世代账: 大写头字段 Keep-Alive {JOIN('lit_keepa_upper')} 处 ⇎ 小写连接选项 keep-alive {JOIN('lit_keepa_lower')} 处——前两份只写大写形(小写合计闭合 {CLOS('keepa_ab_lower_zero','小写形世代')}); 引号形 \"close\" 选项 {JOIN('lit_closeopt')} 处从 3⇎3 涨到 18⇎16, 因为 14⇎22 把连接选项写进语法产生式。")

LINE(u'🧪', u"窗口口径: 答数句所在节 97⇎99 是 §8.1.4 Practical Considerations, 14 拆成 §6.4 Concurrency ⇎ §6.5 Failures and Timeouts, 22 再挪到 §9.4 ⇎ §9.5——本遍把窗定为“正文标题行起到下一节标题行”, 窗标题 {JOIN('sec_head')} ⇎ 窗长 {JOIN('sec_len')} 字符; 窗起行 {JOIN('sec_a')} ⇎ 窗止行 {JOIN('sec_b')}, 另立六枚主线针档(上限两句⇎代理乘法⇎撤数句⇎撤数宣告⇎不再强制⇎两句长度句), 按折平在本面命中的枚数 {JOIN('main6_fold')} ⇎ 其余主线针 {JOIN('sn_other_fold')} 枚——两档之和即容行档针数 {JOIN('sn_fold_docs')}, 注意这六枚是按**本面命中**计而非按窗内计。"
     u"窗内外义务词分档: MUST 窗内 {JOIN('secw_must')} ⇎ 窗外 {JOIN('outw_must')}(逐份闭合 {CLOS('oblig_up_close','大写三词')} ⇎ 窗账 {CLOS('must_win_close_sum','MUST 窗账')}), SHOULD {JOIN('secw_should')} ⇎ {JOIN('outw_should')}, MAY {JOIN('secw_may')} ⇎ {JOIN('outw_may')}; “ought to” 窗内 {JOIN('secw_ought')} ⇎ 窗外 {JOIN('outw_ought')}——14⇎22 的答数句用的是 ought to 而不是 2119 大写词。"
     u"上限字面在窗内的分布可判: “AT MOST” 窗内 {JOIN('secw_atmost')} 处 ⇎ 撤数式窗内 {JOIN('secw_nomandate')} 处 ⇎ 代理乘法窗内 {JOIN('secw_lit_pn')} 处——97⇎99 的三条都在同一个 §8.1.4 窗里, 14 把它们拆到两节, 22 又把两节并排进 §9。"
     u"含关键数字的长行(≥55 字符且含 AT MOST/more than 2/does not mandate/ought to limit/2*N/time-out/timeout 之一) {JOIN('num_lines')} 行。")

LINE(u'⛓', u"折行通道是本条的主通道: {V('wrap_sn_n')} 枚针里 {V('wrap_sn_hit')} 枚有差, 折平−原面合计 {V('wrap_sn_total')} 处, 而这 {V('wrap_sn_hit')} 枚针在原面一律零命中(针数闭合 {CLOS('wrap_hit_minus_onlyfold','跨行差全为折行')})——严格档读到的针数逐份只有 {JOIN('sn_strict_docs')}, 容行档读到 {JOIN('sn_fold_docs')}。"
     u"最锋利的一例: 97 的上限句从 “AT MOST” 处劈行, 把整句照抄进 needle 在原面 {V('s_a2',0)} 处 ⇎ 折平 {V('s_a2_fold',0)} 处; 99 同句 {V('s_b2',1)} ⇎ {V('s_b2_fold',1)}; 代理乘法句 {V('s_proxy',0)}⇎{V('s_proxy',1)} ⇎ 折平 {V('s_proxy_fold',0)}⇎{V('s_proxy_fold',1)}(合计差 {CLOS('wrap_proxy_ab','代理句劈行')})。"
     u"同一条“优雅关闭”四份都在, 但主语式换了两代: 97⇎99 写 “wishes to time-out it SHOULD issue a graceful close”(折平 {JOIN('s_grace_it_fold')} 处) ⇎ 14⇎22 改写成 “A client or server that wishes to time out SHOULD issue a graceful close on the connection”(折平 {JOIN('s_grace_that_fold')} 处), 每份恰好落进一档(逐份闭合 {CLOS4('grace_pair_close','主语式互斥')}), 四份齐账入 {CLOS('grace_all_close','优雅关闭句四份都有')}; 宾语的 “transport” 二字也随世代脱落: 原面 “close on the transport connection” {JOIN('s_grace_trac')} 处 ⇎ 折平 “graceful close on the connection” {JOIN('s_grace_conn_fold')} 处(逐份闭合 {CLOS4('grace_trac_close','transport 换代')})。"
     u"断行位置本身是排版世代的读数: 行尾带连字符的行 {JOIN('hyb_eol')} 行 ⇎ 其下一行以小写字母续写 {JOIN('hyb_cont')} 行——97⇎99 劈得最碎, 14⇎22 只剩十分之一; 同一枚 “server-side” 在 14 面行内 {V('srv_side_raw',2)} 处 ⇎ 在 22 面被劈成 “server- side” {V('srv_side_art',3)} 处, 两式之和逐份 {JOIN('srv_side_sum')}(撤数那两份的闭合 {CLOS('srv_side_cd_close','同词换断行位')})。"
     u"页眉是隐形通道, 只抬高自编号词频: 自编号 {JOIN('cite_self')} 处对页眉 {JOIN('hdr')} 处逐份作差 {JOIN('selfcite_ledger')}(前三份闭合 {CLOS('selfcite_close3','自编号=页眉')})——22 没有页眉, 那 {V('selfcite_ledger',3)} 处才是真引用。"
     u"折平档不是包含关系, 而是写法并档: 同一枚节标题有两种排版, 14 的 {C_concurrency} 用单空格形(目录行) ⇎ 正文标题用双空格形, 两式在原面各 {V('ch_c64',2)}⇎{V('ch_c64_two',2)} 枚 ⇎ 折平后并成一式 {V('ch_c64_fold',2)} 枚(差 {V('ch_fold_gain',2)} 枚); 22 没有目录行 {D_94}——标题一律双空格, 单空格针在原面 {V('ch_d94',3)} 枚 ⇎ 折平档 {V('ch_d94_fold',3)} 枚(差 {V('ch_d94_gain',3)} 枚)。逐份验并档: 折平读数−两种写法读数之和 {CLOS4('ch_fold_eq','写法并档')}。"
     u"锚池按“归一长行压在几份里”分层: 仅一份 {V('pool_1')} ⇎ 两份 {V('pool_2')} ⇎ 三份 {V('pool_3')} ⇎ 四份 {V('pool_4')} 条, 合计 {V('pool_n')} 条, 闭合 {CLOS('pool_tier_close','池分层')}；四份同现只保证归一同形——逐字节仍同形的只剩 {V('share4_byte4')} 条, 其余 {V('share4_notbyte')} 条各差在一根写法轴上: 大小写 {V('share4_axis_case')} ⇎ 连字符 {V('share4_axis_hyph')} ⇎ 句后空格 {V('share4_axis_space')} ⇎ 跨两根轴 {V('share4_axis_multi')}(轴账闭合 {CLOS('share4_axis_close','写法轴')}): 连字符那枚正是超时句 time-out⇎timeout, 空格两枚是 14⇎22 在句点后补的第二只空格。")

LINE(u'📏', u"义务词不成差轴, 成轴的是大小写两档的迁移: 全大写 MUST {JOIN('u_must')} ⇎ SHOULD {JOIN('u_should')} ⇎ MAY {JOIN('u_may')} ⇎ MUST NOT {JOIN('u_must_not')} ⇎ REQUIRED {JOIN('u_required')} ⇎ RECOMMENDED {JOIN('u_recommended')}, 三词合计 {JOIN('oblig_up')}(闭合 {CLOS('oblig_up_close','大写合计')}); 全小写词界形 must {JOIN('lo_must')} ⇎ should {JOIN('lo_should')} ⇎ may {JOIN('lo_may')}, 合计 {JOIN('oblig_low')}(闭合 {CLOS('oblig_low_close','小写合计')})。"
     u"小写形从 97 的 {V('oblig_low',0)} 处塌到 14⇎22 的 {V('oblig_low',2)}⇎{V('oblig_low',3)} 处, 而大写三词同期从 {V('oblig_up',0)}⇎{V('oblig_up',1)} 降到 {V('oblig_up',2)}⇎{V('oblig_up',3)}——两份新规范字数更少, 大写密度反而更高: 每千字大写 97 {EXPR(int(round(F[u'oblig_up'][0]*1000.0/F[u'chars'][0])), u\"int(round(B65V('oblig_up',0)*1000/B65V('chars',0)))\", u'每千字大写义务密度')}/99 {EXPR(int(round(F[u'oblig_up'][1]*1000.0/F[u'chars'][1])), u\"int(round(B65V('oblig_up',1)*1000/B65V('chars',1)))\", u'每千字大写义务密度')}/14 {EXPR(int(round(F[u'oblig_up'][2]*1000.0/F[u'chars'][2])), u\"int(round(B65V('oblig_up',2)*1000/B65V('chars',2)))\", u'每千字大写义务密度')}/22 {EXPR(int(round(F[u'oblig_up'][3]*1000.0/F[u'chars'][3])), u\"int(round(B65V('oblig_up',3)*1000/B65V('chars',3)))\", u'每千字大写义务密度')}。"
     u"RFC 2119 被引 {JOIN('rfc2119_ref')} 次; “ought to limit” {JOIN('lit_oughttolimit')} ⇎ “SHOULD limit the number” {JOIN('lit_shouldlimit')}——同一句劝告在两代里换了一套措辞档位, 两式互不重叠(0⇎0⇎2⇎2 对 1⇎1⇎0⇎0)。")

LINE(u'🗓', u"字样世代账: persistent connections {JOIN('lit_persistent')} ⇎ 归一后同现的 timeout 家族 {JOIN('lit_timeout_p')} ⇎ connection 词干 {JOIN('v_conn')} ⇎ client {JOIN('v_client')} ⇎ server {JOIN('v_server')} ⇎ proxy {JOIN('v_proxy')} 处——proxy 从 99 的 {V('v_proxy',1)} 处一路掉到 22 的 {V('v_proxy',3)} 处, 它谈代理最少。"
     u"retransmi 词干 {JOIN('v_retransmit')} 处(22 已经 {V('v_retransmit',3)} 处——它把重试条件整体推给兄弟规范, 委派句 “Section 9.2.2 of [HTTP]” 只在它面上 {V('lit_sec922',3)} 处), idempotent {JOIN('v_idem')} 处, congestion {JOIN('v_congest')} 处(97⇎99 的“避免拥塞”告诫在 14⇎22 换成 “in congested networks” {JOIN('lit_congnet')} 处)。"
     u"“denial-of-service” {JOIN('lit_dos')} 处 ⇎ 14 {C_dos} ⇎ 22 {D_since} ⇎ “such as an excessive number of open connections” 折平 {JOIN('s_dosnote_fold')} 处 ⇎ head-of-line {JOIN('lit_headol')} 处——这三样都是 14⇎22 新加进并发节的论证, 97⇎99 一个都没写。"
     u"97 独有的收尾句 {A_cong}(“avoid congestion of the Internet or other networks” {JOIN('lit_avoidcong')} 处)到 99 就被截短, 池内仅一份的长行 97 独占 {V('pool_share1_2068')} 条; 14⇎22 的完整短语 “undesirable side effects in congested networks” 原面 {JOIN('lit_sidec')} ⇎ 折平 {JOIN('lit_sidec_fold')}(22 那枚是劈行读回来的, 逐份差 {JOIN('sidec_wrap')} 枚), 而 22 的 “Furthermore, using multiple connections can cause…” 原面 {JOIN('lit_sided')} ⇎ 折平 {JOIN('lit_sided_fold')} 处(差 {JOIN('sided_wrap')} 枚)。")

LINE(u'🧾', u"身份与废止链独立一轴: Category: Standards Track {JOIN('cat_std')} 处 ⇎ Obsoletes 头 {JOIN('obs_hdr')} ⇎ Updates 头 {JOIN('upd_hdr')} ⇎ STD: 头 {JOIN('std_hdr')} ⇎ BCP: 头 {JOIN('bcp_hdr')} ⇎ ISSN 头 {JOIN('issn_hdr')} ⇎ Request for Comments 行 {JOIN('req_rc')}(四份都有) ⇎ IETF 抬头 {JOIN('ise')}(0⇎0⇎1⇎1, 前两代写 Network Working Group)。"
     u"“超出本规范范围”句式 {JOIN('in_scope')} 处只在 14⇎22; 22 把语义推给兄弟规范的具名引用 [HTTP] {JOIN('cite_http_brk')} 处 ⇎ [RFC nnnn] 式引用 {JOIN('cite_rfc_brk')} 处(97 {V('cite_rfc_brk',0)} ⇎ 99 {V('cite_rfc_brk',1)} ⇎ 14 {V('cite_rfc_brk',2)} ⇎ 22 {V('cite_rfc_brk',3)}——方括号引用族是 14 引入、22 沿用而改为具名)。"
     u"引用网: RFC 2068 {JOIN('cite_2068')} ⇎ 2616 {JOIN('cite_2616')} ⇎ 2145 {JOIN('cite_2145')} ⇎ 7230 {JOIN('cite_7230')} ⇎ 7231 {JOIN('cite_7231')} ⇎ 9110 {JOIN('cite_9110')} ⇎ 9112 {JOIN('cite_9112')} ⇎ 2119 {JOIN('cite_2119')} ⇎ 7235 {JOIN('cite_7235')} 次; 22 引 14 {V('cite_7230',3)} 次而引 99 {V('cite_2616',3)} 次——两代之间断了线, 97 的页眉号 {V('cite_2068',0)} 处几乎全是页壳。"
     u"22 的独一枚变音符落在编辑地址行 {D_umlaut}(码位 U+00FC), 加上 UTF-8 BOM {V('bom',3)} 枚——四份里只有它有非 ASCII 面。")

LINE(u'⇄', u"整行搬运(≥40 字符、归一只留 a-z0-9、bisect 档求交): 97⇎99 {V('share_ab')} ⇎ 97⇎14 {V('share_ac')} ⇎ 97⇎22 {V('share_ad')} ⇎ 99⇎14 {V('share_bc')} ⇎ 99⇎22 {V('share_bc') if False else V('share_bd')} ⇎ 14⇎22 {V('share_cd')} 行。"
     u"跨代两两搬运的极差很大: 97⇎99 {V('share_ab')} 行(同一条款的第二版, 逐字节复写 {V('y_ab_byte_shared')} 行 ⇎ 只在归一档相同 {CLOS('y_ab_norm_only','仅归一同')} 行) ⇎ 14⇎22 只 {V('share_cd')} 行(逐字节 {V('y_cd_byte_shared')} ⇎ 仅归一 {CLOS('y_cd_norm_only','CD 仅归一')}), 说明 22 不是 14 的复写本而是重写本; 去页眉页脚只挪动 {CLOS4('shell_delta','含壳−去壳')} 行(14 那一行正是它自己的页壳差异)。"
     u"四份并集 {V('union_all')} 行 ⇎ 三份(去 22)并集 {V('union_abc')} 行 ⇒ 加进 22 多 {V('union_delta')} 行; 容斥给 {V('abcd_incl')} ⇎ 实数 {V('union_all')}(闭合 {CLOS('abcd_close','容斥')})。只在本份的长行: 97 {V('only_a')} 行 ⇎ 22 {V('only_d')} 行(池口径)。")

LINE(u'ℒ', u"方法 ⇒ 面对“同一问题四代文书”, 先问答案是不是一个数: 本遍把上限数字做成句内游标解析档(“AT MOST ” ⇎ “more than ” 之后连读数字), 于是 2⇎2 同值 ⇎ 句式互斥都是可判口径({V('a_ceil')}⇎{V('b_ceil')}); 把义务句式做成极性对(本句式计 ⇎ 对方句式在自己面内计), 换代改写才有互斥证据; 把整节做成窗口(标题行→下一标题行), “答数句在窗内 ⇎ 义务句在窗外”才可分档; 把搬运分两把尺(归一行 ⇎ 逐字节行), 才看得出 22 是重写而非复写。"
     u"严格档 ⇎ 容行档在本条不是冗余: 主轴 {V('wrap_sn_n')} 枚针里 {V('wrap_sn_hit')} 枚只有折平档读得到, 若只按行搜整句, 四份的答数句一律零命中。{V('x_ident_n')} 条恒等式全部由面内现读构成并送门槛重算, 标量闭合 {V('scalar_clos_n')} 枚 ⇎ 总账 {CLOS('scalar_clos_sum','闭合合计')} ⇎ 清单闭合 {V('list_clos_n')} 枚。")

LINE(u'✂️', u"为什么这份编码比答题窗口长 ⇒ 四源各 {JOIN('chars')} 字符 ⇎ 答题窗各 {JOIN('sec_len')} 字符: 窗只占全篇的千分位(97 {EXPR(int(F[u'sec_len'][0]*1000//F[u'chars'][0]), u\"B65V('sec_len',0)*1000//B65V('chars',0)\", u'窗占比千分位')}‰ ⇎ 99 {EXPR(int(F[u'sec_len'][1]*1000//F[u'chars'][1]), u\"B65V('sec_len',1)*1000//B65V('chars',1)\", u'窗占比千分位')}‰ ⇎ 14 {EXPR(int(F[u'sec_len'][2]*1000//F[u'chars'][2]), u\"B65V('sec_len',2)*1000//B65V('chars',2)\", u'窗占比千分位')}‰ ⇎ 22 {EXPR(int(F[u'sec_len'][3]*1000//F[u'chars'][3]), u\"B65V('sec_len',3)*1000//B65V('chars',3)\", u'窗占比千分位')}‰)。"
     u"答数只有一枚 2, 但“它写在散文还是禁令里、代理乘几条、被谁删掉、超时句改了几次拼写、义务词换了几档措辞”要跨四份并排读: 97⇎99 的两式互斥({V('pol_cross_close')} 处交叉命中) ⇎ 14⇎22 的撤数句逐字同现({V('cd_verdict_same')} 枚)而论证段各一枚({V('cd_prose_diff')}); 拼写分家(time-out {V('lit_timeout_h',0)}+{V('lit_timeout_h',1)} ⇎ timeout {V('lit_timeout_p',2)}+{V('lit_timeout_p',3)} 处)。"
     u"读它请按“这个答案是数字还是撤数、句子挂在哪种义务句式下、在哪一代被劈行排版、被谁重写”来读, 而不是按“少抄了多少原文”。")

if VKMISS:
    for nm in sorted(set(x[0] for x in VKMISS)):
        print(u'NOKEY %s %s' % (nm, [y[1] for y in VKMISS if y[0] == nm][:4]))
    raise SystemExit(1)
assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
ZFAIL = []
for _e, _n in ZID:
    _v = eval(_e, {u'B65V': BB65})
    if _v != 0:
        ZFAIL.append((_n, _e, _v))
    else:
        reg(u'0', _e, _n)
if ZFAIL:
    for _n, _e, _v in ZFAIL:
        print(u'ZFAIL %s |%s| = %s' % (_n, _e, _v))
    raise SystemExit(1)
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


# ---- 整串打印的列表键: 元素也是判词里的字面数, 按下标补登记算式 ----
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
    got = [e for e in ELEMS.get(s, []) if eval(e, {u'B65V': BB65}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, NOEXPR
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
# 反向对照扫出的"纯复述点"(算式就是 B65V('x') 本身): 换成用别的读数现算的关系式,
# 值不变⇒条目正文一字不动, 但任一分量读数漂移都会让这条判定倒。
REL = {u'2328': u"B65V('pool_share1_2068')+B65V('pool_share1_2616')"
                 u"+B65V('pool_share1_7230')+B65V('pool_share1_9112')",
        u'1218': u"B65V('pool_n')-B65V('pool_1')-B65V('pool_3')-B65V('pool_4')",
        u'3572': u"sum(B65V('pool_tier'))",
        u'8258': u"B65V('union_all')-B65V('union_delta')",
        u'345': u"B65V('share_ab')-B65V('y_ab_byte_shared')",
        u'470': u"B65V('y_cd_byte_shared')+B65V('y_cd_norm_only')",
        u'700': u"B65V('pool_1')-B65V('pool_share1_2616')-B65V('pool_share1_7230')"
                u"-B65V('pool_share1_9112')",
        u'2301': u"B65V('y_ab_byte_shared')+B65V('y_ab_norm_only')"}
for _k, _e in REL.items():
    assert _k in DERIV, _k
    assert eval(_e, {u'B65V': BB65, u'sum': sum}) == int(_k), (_k, eval(_e, {u'B65V': BB65, u'sum': sum}))
    DERIV[_k] = _e
json.dump(DERIV, io.open(u'corpus/_deriv65.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b65flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms65.txt', 'w', encoding='utf-8', newline=NL).write(
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
json.dump(CH, io.open(u'corpus/_b65checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 字符／原行 %d／非空行 %d／上限 %s／页眉 %d⇎页脚 %d⇎换页 %d)' % (
        os.path.basename(PATH[i]), F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        (u'%d 条' % F[u'a_ceil'] if i == 0 else u'%d 条' % F[u'b_ceil']) if i < 2 else u'不设数',
        F[u'hdr'][i], F[u'foot'][i], F[u'formfeed'][i])
    for i in range(NSRC)) +
    u' (四份 RFC Editor 纯文本面, 全 LF; 22 带 UTF-8 BOM 与唯一一枚非 ASCII 码点 U+00FC, 且完全没有页眉/页脚/换页符/点线目录。'
    u'数字一律从面内现读或句内游标解析, 一个都不手填; 抓取时刻、官网现行状态、浏览器实际每域开几条连接、'
    u'现网服务器空闲超时配多少秒只在本机或站外成立, 不进门槛)\n')
联结 = (u"；联结不是“同一份数据的两种序列化”, 而是“同一个客户端对同一台服务器最多该同时开几条连接”在四份一手 HTTP/1.1 规范里的四种答法: "
        u"句内游标解析出 97 最多二 %d 条 ⇎ 99 不得超 %d 条(两式分别为 “SHOULD maintain AT MOST %d” ⇎ “SHOULD NOT maintain more than %d”, 交叉命中 %d+%d=%d 处), "
        u"而 14 ⇎ 22 撤掉数字: “does not mandate a particular maximum” 字面 %d⇎%d⇎%d⇎%d 处, 撤数整段(三句连排)折平档在 14 ⇎ 22 各 %d 枚, "
        u"可两代紧接着的 head-of-line 论证段各写各的(14 大 payload 句 %d 枚 ⇎ 22 very large content 句 %d 枚, 互斥合计 %d); "
        u"代理侧的 “2*N connections” 出现处 %d⇎%d⇎%d⇎%d——14 与 22 整句删除; 超时那一句三代变形: 97 “no requirements on the length of this time-out” ⇎ "
        u"99 插 “(or existence)”(%d 处) ⇎ 14⇎22 改拼 timeout, 带连字符形 %d⇎%d⇎%d⇎%d 处 ⇎ 无连字符形 %d⇎%d⇎%d⇎%d 处, 每份恰好落进一档; "
        u"重试粒度: 97 中止“那一次请求”且按方法判幂等(%d 处) ⇎ 99 扩成“那一串请求”并按序列判幂等(%d 处), 新措辞在四份原面一律零字面; "
        u"措辞档位换代: “SHOULD limit the number” %d⇎%d⇎%d⇎%d ⇎ “ought to limit” %d⇎%d⇎%d⇎%d, 大写义务三词合计 %d⇎%d⇎%d⇎%d ⇎ 全小写词界形 %d⇎%d⇎%d⇎%d; "
        u"版式两代: 页壳三档 %d⇎%d⇎%d⇎%d ⇎ %d⇎%d⇎%d⇎%d ⇎ %d⇎%d⇎%d⇎%d(页眉/页脚/换页符), 点线目录行 %d⇎%d⇎%d⇎%d, 22 的页壳与目录全零而独带一枚 BOM 与 U+00FC; "
        u"整行搬运: 97⇎99 归一 %d 行(逐字节 %d ⇎ 仅归一同 %d) ⇎ 14⇎22 归一 %d 行(逐字节 %d ⇎ 仅归一同 %d)——22 是重写本而不是复写本。\n") % (
    F[u'a_ceil'], F[u'b_ceil'], F[u'a_ceil'], F[u'b_ceil'], F[u'pol_cross_ab'], F[u'pol_cross_ba'], F[u'pol_cross_close'],
    F[u'lit_nomandate'][0], F[u'lit_nomandate'][1], F[u'lit_nomandate'][2], F[u'lit_nomandate'][3],
    F[u'cd_verdict_same'] // 2, F[u's_hol_c_fold'][2], F[u's_hol_d_fold'][3], F[u'hol_excl'],
    F[u'lit_pn'][0], F[u'lit_pn'][1], F[u'lit_pn'][2], F[u'lit_pn'][3],
    F[u'lit_orx'][1],
    F[u'lit_timeout_h'][0], F[u'lit_timeout_h'][1], F[u'lit_timeout_h'][2], F[u'lit_timeout_h'][3],
    F[u'lit_timeout_p'][0], F[u'lit_timeout_p'][1], F[u'lit_timeout_p'][2], F[u'lit_timeout_p'][3],
    F[u'lit_methodid'][0], F[u'lit_abortedseq'][1],
    F[u'lit_shouldlimit'][0], F[u'lit_shouldlimit'][1], F[u'lit_shouldlimit'][2], F[u'lit_shouldlimit'][3],
    F[u'lit_oughttolimit'][0], F[u'lit_oughttolimit'][1], F[u'lit_oughttolimit'][2], F[u'lit_oughttolimit'][3],
    F[u'oblig_up'][0], F[u'oblig_up'][1], F[u'oblig_up'][2], F[u'oblig_up'][3],
    F[u'oblig_low'][0], F[u'oblig_low'][1], F[u'oblig_low'][2], F[u'oblig_low'][3],
    F[u'hdr'][0], F[u'hdr'][1], F[u'hdr'][2], F[u'hdr'][3],
    F[u'foot'][0], F[u'foot'][1], F[u'foot'][2], F[u'foot'][3],
    F[u'formfeed'][0], F[u'formfeed'][1], F[u'formfeed'][2], F[u'formfeed'][3],
    F[u'toc_lines'][0], F[u'toc_lines'][1], F[u'toc_lines'][2], F[u'toc_lines'][3],
    F[u'share_ab'], F[u'y_ab_byte_shared'], F[u'y_ab_norm_only'],
    F[u'share_cd'], F[u'y_cd_byte_shared'], F[u'y_cd_norm_only'])
title = (u'# B65 同一个客户端对同一台服务器最多该同时开几条连接，四份规范四种答法：AT MOST 2 ⇎ NOT more than 2 ⇎ 明文撤数 ⇎ 撤数同句而论证改写（数字没变、句式翻转，最后两代干脆不给数）\n')
text = (title + srcline + 联结 +
        u'tags: 上限在散文⇎在禁令 句内游标解析数字 义务句式极性对(互斥零侵入) 代理乘法句整段删除 '
        u'撤数句两代逐字同现⇎论证段各一枚 超时句拼写分代(time-out⇎timeout) (or existence) 插语 '
        u'重试粒度 方法⇎序列 折行通道为主档(严格档读到针数⇎容行档) 优雅关闭句主语式两代 '
        u'ought to⇎SHOULD 措辞档位迁移 大写义务⇎小写词界两档 每千字大写密度 自编号=页眉 '
        u'窗口档 窗内⇎窗外义务词 页壳三档世代(22 全零) BOM+U+00FC 独一枚 归一⇎字节两把搬运尺 '
        u'锚池分层闭合 归一四份同现⇎逐字节同形(差轴: 大小写⇎连字符⇎句后空格) 闭合账 标量 %d⇎清单 %d 项⇎恒等式 %d 条\n' % (
            F[u'scalar_clos_n'], F[u'list_clos_n'], F[u'x_ident_n']) +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill65.py 从 corpus/_b65checks.json 与 corpus/_deriv65.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两至三源 %d ⇎ 四源 %d ⇎ 错配 %d ｜ 池内取用 %d／池 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], len(ERR), CH[u'pool_used'], F[u'pool_n']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(F)))
print(u'上限 %d ⇎ %d ⇎ 撤数 %d ⇎ 交叉 %d ｜ 窗 %s ⇎ 标题 %s' % (
    F[u'a_ceil'], F[u'b_ceil'], F[u'nomandate_docs_n'], F[u'pol_cross_close'],
    F[u'sec_len'], F[u'sec_head']))
print(u'拼写分代: time-out %s ⇎ timeout %s ⇎ 每份一档闭合 %s' % (
    F[u'lit_timeout_h'], F[u'lit_timeout_p'], F[u'gen_split_close']))
print(u'跨行: 针 %d 有差 %d 合计 %d ｜ 严格档 %s ⇎ 容行档 %s' % (
    F[u'wrap_sn_n'], F[u'wrap_sn_hit'], F[u'wrap_sn_total'], F[u'sn_strict_docs'], F[u'sn_fold_docs']))
print(u'搬运 ab %d(字节 %d 仅归一 %d) cd %d(字节 %d 仅归一 %d) 并集 %d/%d 容斥闭合 %d' % (
    F[u'share_ab'], F[u'y_ab_byte_shared'], F[u'y_ab_norm_only'], F[u'share_cd'],
    F[u'y_cd_byte_shared'], F[u'y_cd_norm_only'], F[u'union_abc'], F[u'union_all'], F[u'abcd_close']))
print(u'义务 大写 %s ⇎ 小写 %s ｜ 窗内 %s/%s/%s ⇎ 窗外 %s/%s/%s' % (
    F[u'oblig_up'], F[u'oblig_low'], F[u'secw_must'], F[u'secw_should'], F[u'secw_may'],
    F[u'outw_must'], F[u'outw_should'], F[u'outw_may']))
print(u'池 %s tier %s 闭合 %d ｜ 自编号账 %s' % (F[u'pool_n'], F[u'pool_tier'], F[u'pool_tier_close'],
                                                 F[u'selfcite_ledger']))
print(u'闭合键 %d 项 ⇎ 恒等式 %d 条 ⇎ 标量合计 %d ⇎ 清单闭合 %d' % (
    F[u'scalar_clos_n'], F[u'x_ident_n'], F[u'scalar_clos_sum'], F[u'list_clos_n']))
MEASP = u'corpus/_b65meas.json'
COLONLY = (u'sig_sha256_16',)
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
    print(u'  采集侧独有(正则族/独立档, 建条目侧另立口径): %s' % (MISSK[:16],))
else:
    print(u'两侧对账: 无 corpus/_b65meas.json(采集侧未跑)')
