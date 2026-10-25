# -*- coding: utf-8 -*-
"""B65 现探(采集侧, 只测量不设门槛): 四份 HTTP/1.1 纯文本对"同一个客户端对同一台服务器最多该同时开几条连接、
空闲连接该不该有个超时"的答法。
⟦A⟧rfc2068(1997, 初版 HTTP/1.1: 给数 "SHOULD maintain AT MOST 2") ⇎ ⟦B⟧rfc2616(1999, Obsoletes: 2068,
同一个 2 但义务句式翻成 "SHOULD NOT maintain more than 2") ⇎ ⟦C⟧rfc7230(2014, Obsoletes: 2145, 2616,
明文撤数 "does not mandate a particular maximum") ⇎ ⟦D⟧rfc9112(2022, STD: 99, 撤数句与 C 逐字同, 分歧改在
head-of-line 那段的算法描述与分节排印)。
主轴答数: AT MOST 2(A) ⇎ not more than 2(B) ⇎ 不设上限只说 ought to limit(C) ⇎ 同 C 逐字(D)。
次轴(同一批文件回答的第二个问题): 超时句三代变形——A "no requirements on the length of this time-out"
⇎ B 起插 "(or existence)" ⇎ C/D 把 time-out 改拼 timeout; 以及重试粒度 A "request method is idempotent"
⇎ B "request sequence is idempotent"(折行处)。
采集侧一律 re.findall / 子串计数; 键名只允许 [a-z0-9_](门槛的 B65V('…') 引用式只认这个字符集)。
三处版式断层最容易读错: 四份都是行式 RFC 排版 ⇒ 大量整句被硬断行(主轴十二枚针在原面一律零命中, 只有折平档可读);
C 把 A/B 的 §8.1.4 拆成 §6.4 Concurrency ⇎ §6.5 Failures and Timeouts 两节; D 又把这两节挪到 §9.4 ⇎ §9.5,
且把语义推给 [HTTP] 那份兄弟规范(自身篇幅只有 B 的四分之一, 且完全没有页眉/页脚/换页符/点线目录)。
另: 归一口径(剥掉非 a-z0-9)会说某些长行四份同现, 原面按拼写分家——A/B 写 time-out 而 C/D 写 timeout。
抓取时刻、rfc-editor.org 此刻给这四份挂的状态、各家浏览器实际每域开几条连接、现网服务器空闲超时配多少秒,
都不可由在库文件判定, 不进这张表。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NL = u'\n'
TAGS = (u'A', u'B', u'C', u'D')
PATH = [u'corpus/raw/httpKA/rfc2068.txt', u'corpus/raw/httpKA/rfc2616.txt',
        u'corpus/raw/httpKA/rfc7230.txt', u'corpus/raw/httpKA/rfc9112.txt']
N = 4
G = {}
REC = []


def put(k, v, note=u''):
    G[k] = v
    REC.append((k, note))


RB = [open(p, 'rb').read() for p in PATH]
T = [r.decode('utf-8-sig') for r in RB]
FO = [u' '.join(t.split()) for t in T]
LST = [t.split(NL) for t in T]

# ---- 形状 ----
put('bytes', [len(r) for r in RB], u'面内字节')
put('chars', [len(t) for t in T], u'码点数(已去 BOM)')
put('lines', [len(l) for l in LST], u'')
put('nonblank', [len([l for l in L if l.strip()]) for L in LST], u'判空按 strip() 同义即 isspace()')
put('maxlen', [max([len(l) for l in L]) for L in LST], u'')
put('trail', [len([l for l in L if l != l.rstrip()]) for L in LST], u'')
put('cr', [t.count(u'\r') for t in T], u'')
put('nonascii', [len([c for c in t if ord(c) > 127]) for t in T], u'utf-8-sig 解码后计数')
put('bom', [1 if r[:3] == b'\xef\xbb\xbf' else 0 for r in RB], u'UTF-8 BOM')
put('formfeed', [t.count(u'\x0c') for t in T], u'换页符')
put('nonblank_asciib', [len([l for l in L if l.strip(u' \t\r')]) for L in LST],
    u'手写空判口径(只认 空格/制表/回车): 把换页符独占行算作非空')
put('ff_only_lines', [len([l for l in L if l.strip(u' \t\r') and not l.strip()]) for L in LST],
    u'仅由 \x0c 之类“空格类但非 空格/制表/回车”的字符独占的行数')
put('nb_gap', [G[u'nonblank_asciib'][i] - G[u'nonblank'][i] for i in range(N)], u'两口径之差, 应等于 ff_only_lines')

HDR_SP = re.compile(r'^RFC \d{4}(?!\d)(?: |$)')
HDR_NS = re.compile(r'^RFC\d{4}(?!\d)(?: |$)')
FOOT_BRK = re.compile(r'\[Page \d+\]$')


def is_hdr(l):
    return bool(HDR_SP.match(l) or HDR_NS.match(l))


def is_foot(l):
    return bool(FOOT_BRK.search(l.strip()))


put(u'hdr_sp', [len([l for l in L if HDR_SP.match(l) and l[8:].strip()]) for L in LST], u'页眉 “RFC nnnn”(带空格)')
put(u'hdr_ns', [len([l for l in L if HDR_NS.match(l)]) for L in LST], u'页眉 “RFCnnnn”(不带空格)')
put(u'hdr', [len([l for l in L if is_hdr(l)]) for L in LST], u'两档之和')
put(u'foot', [len([l for l in L if is_foot(l)]) for L in LST], u'`[Page n]` 页脚行')
put(u'pg', [t.count(u'[Page ') for t in T], u'“[Page ” 子串出现处')
put(u'pagelines', [h + f for h, f in zip(G['hdr'], G['foot'])], u'')
put(u'pages_est', [max(h, f) for h, f in zip(G['hdr'], G['foot'])], u'页数估计')
put(u'sig_sha256_16', [hashlib.sha256(r).hexdigest()[:16] for r in RB], u'采集侧 sha256; 建条目侧换 blake2b 另立键')
put(u'sig_distinct', len(set(G['sig_sha256_16'])), u'')

# ---- 字面出现处(主轴: 并发连接数) ----
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
    u'msghttp': u'message/http', u'apchttp': u'application/http',
    u'payloadblk': u'has a large payload blocks subsequent', u'bigcontent': u'transfers very large content would block',
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
    u'idemmethods': u'idempotent methods', u'idemhave': u'have idempotent methods',
    u'retransseq': u'automatically retransmit an aborted sequence of',
}
for k, s in sorted(LITK.items()):
    put(u'lit_' + k, [t.count(s) for t in T], u'字面 %r' % s)
put(u'lit_two_both', [G[u'lit_atmost2'][i] + G[u'lit_more2'][i] for i in range(N)],
    u'两式“2 上限”句合计(应 A 1 ⇎ B 1 ⇎ C 0 ⇎ D 0)')
put(u'lit_hyphen_gap', [G[u'lit_timeout_h'][i] for i in range(N)], u'带连字符 time-out 出现处')
put(u'lit_plain_in_ab', [G[u'lit_timeout_p'][i] - G[u'lit_timeout_h'][i] for i in range(N)],
    u'timeout 总形 − time-out 形(即无连字符形的上界)')

# ---- 答数所在句: 原面 ⇎ 折平 两档 ----
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
    a = [t.count(s) for t in T]
    nf = u' '.join(s.split())
    b = [x.count(nf) for x in FO]
    put(u's_' + k, a, u'原面 %r' % s[:34])
    put(u's_' + k + u'_fold', b, u'折平')
    put(u'wrapgap_' + k, [b[i] - a[i] for i in range(N)], u'折平−原面')
put(u'wrap_sn_n', len(SN), u'')
put(u'wrap_sn_hit', len([1 for k, _ in SN if any(G[u'wrapgap_' + k])]), u'跨行有差的针数')
put(u'wrap_sn_total', sum(sum(G[u'wrapgap_' + k]) for k, _ in SN), u'')
# 断行位置: 行尾连字符 ⇎ 下一行以小写续写 ⇎ 折平后留下的伪形
put(u'hyb_eol', [len(re.findall(u'(?m)^.*-$', t)) for t in T], u'以连字符结尾的行数')
put(u'hyb_cont', [len([1 for a, b in zip(L, L[1:]) if a.endswith(u'-') and b.strip()[:1].islower()])
                  for L in LST], u'其中下一行以小写字母起头(逐对计数, 连续劈行不吞)')
put(u'srv_side_raw', [t.count(u'server-side') for t in T], u'原面 “server-side”')
put(u'srv_side_art', [x.count(u'server- side') for x in FO], u'折平伪形 “server- side”')
# 同一枚节标题的两种排版写法: 原面按写法取针, 折平档把两写法并成一式
for _k, _one, _two in ((u'c64', u'6.4. Concurrency', u'6.4.  Concurrency'),
                       (u'd94', u'9.4. Concurrency', u'9.4.  Concurrency')):
    put(u'ch_' + _k, [t.count(_one) for t in T], u'原面单空格 %r' % _one)
    put(u'ch_' + _k + u'_two', [t.count(_two) for t in T], u'原面双空格 %r' % _two)
    put(u'ch_' + _k + u'_fold', [x.count(_one) for x in FO], u'折平后按单空格形数')
put(u'ch_fold_gain', [G[u'ch_c64_fold'][i] - G[u'ch_c64'][i] for i in range(N)], u'14 目录行使折平档多读的枚数')
put(u'ch_d94_gain', [G[u'ch_d94_fold'][i] - G[u'ch_d94'][i] for i in range(N)], u'22 只有折平档读得到标题')
put(u'ch_fold_eq', [G[u'ch_c64_fold'][i] + G[u'ch_d94_fold'][i] - G[u'ch_c64'][i] - G[u'ch_c64_two'][i]
                    - G[u'ch_d94'][i] - G[u'ch_d94_two'][i] for i in range(N)], u'折平读数-两种写法读数之和')
# 折行通道也会藏针: 这些字面串在原面被硬断行劈开
for _k in (u'abortedseq', u'seqidem', u'sidec', u'sided'):
    _n = u' '.join(LITK[_k].split())
    put(u'lit_' + _k + u'_fold', [x.count(_n) for x in FO], u'折平档重数 %r' % _n)
put(u'abortedseq_wrap', [G[u'lit_abortedseq_fold'][i] - G[u'lit_abortedseq'][i] for i in range(N)],
    u'“aborted sequence of requests” 靠折行才读到的枚数')
# 答数所在行(1 起): 各份用它自己的字面形状去找
RULE = [u'SHOULD maintain AT MOST 2 connections', u'SHOULD NOT maintain more than 2 connections',
        u'As a result, this specification does not mandate',
        u'As a result, this specification does not mandate']
for i, s in enumerate(RULE):
    nf = u' '.join(s.split())
    hits = [n + 1 for n, l in enumerate(LST[i]) if s in l]
    hitsf = [n + 1 for n, l in enumerate(LST[i]) if nf in u' '.join(l.split())]
    put(u'ans_line_' + TAGS[i].lower(), hits, u'答数行(原面, 1 起) %r' % s)
    put(u'ans_linefold_' + TAGS[i].lower(), hitsf, u'答数行(先在行内折平再找)')
put(u'ans_lit_present', [1 if RULE[i] in T[i] else 0 for i in range(N)], u'')
put(u'ans_fold_present', [1 if u' '.join(RULE[i].split()) in FO[i] else 0 for i in range(N)], u'折平后命中')
put(u'ans_gap', [G[u'ans_fold_present'][i] - G[u'ans_lit_present'][i] for i in range(N)], u'')

# 只在一档可读的针: 严格档 ⇎ 容行档 各自能读到的份数
put(u'sn_strict_docs', [len([1 for k, _ in SN if G[u's_' + k][i]]) for i in range(N)], u'严格档读到针的份数')
put(u'sn_fold_docs', [len([1 for k, _ in SN if G[u's_' + k + u'_fold'][i]]) for i in range(N)], u'容行档读到针的份数')
put(u'sn_only_fold', [k for k, _ in SN
                      if any(G[u'wrapgap_' + k]) and sum(G[u's_' + k]) == 0], u'原面零命中而折平有命中的针')

# ---- 小节编号: 同一答数句在四份里挂的节号 ----
SEC = {
    u'practical': re.compile(u'^\\s*8\\.1\\.4\\s'),
    u'concurrency': re.compile(u'^\\s*(6\\.4|9\\.4)\\.?\\s+Concurrency'),
    u'failures': re.compile(u'^\\s*(6\\.5|9\\.5)\\.?\\s+Failures and Timeouts'),
    u'persistence': re.compile(u'^\\s*(6\\.2|9\\.3)\\.?\\s+Persistence'),
    u'estab': re.compile(u'^\\s*(6\\.3|9\\.1)\\.?\\s+Establishment'),
    u'teardown': re.compile(u'^\\s*(6\\.7|9\\.6)\\.?\\s+Tear-down'),
}
for k, rx in sorted(SEC.items()):
    rows = [[n + 1 for n, l in enumerate(L) if rx.match(l)] for L in LST]
    put(u'sec_' + k, [len(r) for r in rows], u'正文标题命中数(不含目录)')
    put(u'sec_' + k + u'_line', rows, u'行号(1 起)')
TOC = re.compile(u'^\\s*[0-9]+(\\.[0-9]+)*\\.?\\s+\\S.*\\.{3,}\\d+\\s*$')
put(u'toc_lines', [len([l for l in L if TOC.match(l)]) for L in LST], u'目录点线行')

# ---- 义务词 / 语汇 ----
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED', u'RECOMMENDED', u'MAY NOT'):
    put(u'u_' + w.replace(u' ', u'_').lower(), [t.count(w) for t in T], u'')
put(u'oblig_up', [G[u'u_must'][i] + G[u'u_should'][i] + G[u'u_may'][i] for i in range(N)], u'')
for w in (u'must', u'should', u'may'):
    put(u'lo_' + w, [len(re.findall(u'(?<![A-Za-z])' + w + u'(?![A-Za-z])', t)) for t in T],
        u'全小写形且前后不接字母(大写 2119 关键词不计)')
put(u'oblig_low', [G[u'lo_must'][i] + G[u'lo_should'][i] + G[u'lo_may'][i] for i in range(N)], u'小写档合计')
put(u'rfc2119_ref', [t.count(u'2119') for t in T], u'')
WK = [(u'persist', u'persistent'), (u'conn', u'connection'), (u'client', u'client'), (u'server', u'server'),
      (u'proxy', u'proxy'), (u'timeoutw', u'timeout'), (u'keepw', u'keep'), (u'retry', u'retry'),
      (u'retransmit', u'retransmi'), (u'idem', u'idempotent'), (u'browser', u'browser'),
      (u'congest', u'congestion'), (u'state', u'state')]
for k, s in WK:
    put(u'v_' + k, [t.count(s) for t in T], u'')

# ---- 文档身份 / 世代引用 ----
HK = [(u'cat_std', u'Category: Standards Track'), (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'),
      (u'std_hdr', u'STD:'), (u'bcp_hdr', u'BCP:'), (u'issn_hdr', u'ISSN:'), (u'req_rc', u'Request for Comments:'),
      (u'obsoleted_by', u'obsoleted by'), (u'ise', u'Internet Engineering Task Force (IETF)'),
      (u'in_scope', u'It is beyond the scope of this specification')]
for k, s in HK:
    put(k, [t.count(s) for t in T], u'')
put(u'obsoleted_by', [len(re.findall(u'(?i)obsoleted by', t)) for t in T], u'')
for n in (u'2068', u'2616', u'2145', u'7230', u'7231', u'9110', u'9112', u'2119', u'7235'):
    put(u'cite_' + n, [len(re.findall(u'RFC ?' + n + u'(?!\\d)', t)) for t in T], u'')
put(u'cite_http_brk', [t.count(u'[HTTP]') for t in T], u'把语义推给兄弟规范的方括号引用')
put(u'cite_rfc_brk', [len(re.findall(u'\\[RFC ?\\d+\\]', t)) for t in T], u'[RFC nnnn] 式引用')

# ---- 搬运账(整行归一) ----
NRM = lambda l: re.sub(u'[^a-z0-9]', u'', l.lower())


def line_set(i, shell=True, m=40):
    out = set()
    for l in LST[i]:
        if not shell and (is_hdr(l) or is_foot(l)):
            continue
        n = NRM(l)
        if len(l.strip()) >= m and len(n) >= m:
            out.add(n)
    return out


for shell, suf in ((True, u''), (False, u'_nos')):
    S = [line_set(i, shell) for i in range(N)]
    put(u'lines_ge40' + suf, [len(s) for s in S], u'')
    for a in range(N):
        for b in range(a + 1, N):
            put(u'share_%s%s%s' % (TAGS[a].lower(), TAGS[b].lower(), suf), len(S[a] & S[b]), u'')
    put(u'union_all' + suf, len(set().union(*S)), u'')
    put(u'only_a' + suf, len(S[0] - S[1] - S[2] - S[3]), u'')
    put(u'only_d' + suf, len(S[3] - S[0] - S[1] - S[2]), u'')
    put(u'share_ab' + suf, len(S[0] & S[1]), u'')
    put(u'share_cd' + suf, len(S[2] & S[3]), u'')
put(u'shell_delta', [G[u'lines_ge40'][i] - G[u'lines_ge40_nos'][i] for i in range(N)], u'')
put(u'share_cd_delta', G[u'share_cd'] - G[u'share_cd_nos'], u'')

# ---- 锚池: 长行按“在几份里逐字再现”分档 ----
tier = [0, 0, 0, 0]
CNT = {}
for i in range(N):
    for l in LST[i]:
        n = NRM(l)
        if len(l.strip()) >= 55 and len(n) >= 55 and not (is_hdr(l) or is_foot(l)):
            CNT.setdefault(n, set()).add(i)
for n in CNT:
    tier[len(CNT[n]) - 1] += 1
put(u'pool_n', len(CNT), u'长行候选池(去页眉页脚, 归一后长度>=55)')
put(u'pool_tier', tier, u'按“在几份里逐字再现”分档 1⇎2⇎3⇎4')
put(u'pool_tier_close', sum(tier) - len(CNT), u'分档闭合差')
put(u'pool_share4', sorted(n for n in CNT if len(CNT[n]) == 4)[:6], u'四份同现样例(排序后取前六)')
put(u'pool_share1_2068', len([n for n in CNT if len(CNT[n]) == 1 and CNT[n] == {0}]), u'只在 A 逐字再现')
put(u'pool_share1_2616', len([n for n in CNT if len(CNT[n]) == 1 and CNT[n] == {1}]), u'只在 B')
put(u'pool_share1_7230', len([n for n in CNT if len(CNT[n]) == 1 and CNT[n] == {2}]), u'只在 C')
put(u'pool_share1_9112', len([n for n in CNT if len(CNT[n]) == 1 and CNT[n] == {3}]), u'只在 D')
put(u'pool_share2_ab', len([n for n in CNT if CNT[n] == {0, 1}]), u'')
put(u'pool_share2_cd', len([n for n in CNT if CNT[n] == {2, 3}]), u'')
# 归一口径下“四份同现”的长行, 拿原面逐份再验一次拼写: 连字符 time-out ⇎ timeout 会把同现拆成两代
S4 = [n for n in CNT if len(CNT[n]) == 4]
put(u'nonascii_cp', [[hex(ord(c)) for c in t if ord(c) > 127] for t in T], u'去 BOM 后仍 >U+007F 的码点')


def raw_forms(i, norm):
    """归一长行回原面取**逐字节**写法: 该份里所有“去非 a-z0-9 后等于 norm”的行原样收进集合。"""
    return set(l for l in LST[i] if NRM(l) == norm)


def axis_of(norm):
    """四份写法压成一根轴: 先只忽略大小写, 再连字符一起忽略, 最后连空格一起忽略;
    第一次压到同形的那一步就是差异所在的轴——压不到同形者记 multi, 不许有。"""
    fs = set()
    for i in range(N):
        fs |= raw_forms(i, norm)
    if len(fs) < 2:
        return u''
    if len(set(f.lower() for f in fs)) == 1:
        return u'case'
    if len(set(f.lower().replace(u'-', u'') for f in fs)) == 1:
        return u'hyph'
    if len(set(re.sub(u'\s+', u' ', f.lower().replace(u'-', u'')) for f in fs)) == 1:
        return u'space'
    return u'multi'


B4 = [n for n in S4 if set.intersection(*[raw_forms(i, n) for i in range(N)])]
put(u'share4_byte4', len(B4), u'归一四份同现 ⇎ 逐字节也同形')
put(u'share4_notbyte', len(S4) - len(B4), u'归一同现但原面分家的长行')
for _a in (u'case', u'hyph', u'space', u'multi'):
    put(u'share4_axis_' + _a, len([n for n in S4 if axis_of(n) == _a]), u'写法差落在 %s 轴' % _a)
put(u'share4_axis_close', (G[u'share4_axis_case'] + G[u'share4_axis_hyph'] + G[u'share4_axis_space']
                           + G[u'share4_axis_multi'] - G[u'share4_notbyte']), u'轴账闭合差')
put(u'share4_diff', sorted([[axis_of(n), n] for n in S4 if axis_of(n)]),
    u'每根分家长行差在哪根轴上(连字符 ⇎ 大小写 ⇎ 句后空格)')


ORDER = [k for k, _ in REC]
MISS = [k for k in ORDER if not re.match(r'^[a-z0-9_]+$', k)]
io.open(u'corpus/_b65meas.json', 'w', encoding='utf-8').write(
    json.dumps(dict((k, G[k]) for k in ORDER), ensure_ascii=False, indent=0, sort_keys=True))
print(u'%s = rfc%s' % (u' ⇎ '.join(TAGS), u' ⇎ rfc'.join((u'2068', u'2616', u'7230', u'9112'))))
print(u'非 [a-z0-9_] 键名: %s' % (MISS or u'无'))
for k in (u'bytes', u'chars', u'lines', u'nonblank', u'nonblank_asciib', u'ff_only_lines', u'nb_gap', u'maxlen',
          u'trail', u'cr', u'nonascii', u'bom', u'formfeed', u'hdr_sp', u'hdr_ns', u'hdr', u'foot', u'pg',
          u'pagelines', u'pages_est', u'sig_distinct'):
    print(u'%-22s %s' % (k, G[k]))
print(u'--- 字面 ---')
for k in sorted(LITK):
    print(u'%-22s %s' % (u'lit_' + k, G[u'lit_' + k]))
print(u'%-22s %s' % (u'lit_two_both', G[u'lit_two_both']))
print(u'--- 主线跨行(原面/折平/差) ---')
for k, s in SN:
    print(u'%-12s s %s fold %s gap %s' % (k, G[u's_' + k], G[u's_' + k + u'_fold'], G[u'wrapgap_' + k]))
print(u'%-22s %s hit %s total %s' % (u'wrap_sn_n', G[u'wrap_sn_n'], G[u'wrap_sn_hit'], G[u'wrap_sn_total']))
print(u'%-22s %s fold %s only_fold %s' % (u'sn_strict_docs', G[u'sn_strict_docs'], G[u'sn_fold_docs'],
                                          G[u'sn_only_fold']))
print(u'--- 节号 ---')
for tg in TAGS:
    print(u'%-16s 原面 %s 折平 %s' % (u'ans_line_' + tg.lower(), G[u'ans_line_' + tg.lower()],
                                      G[u'ans_linefold_' + tg.lower()]))
print(u'%-22s %s / fold %s / gap %s' % (u'ans_lit_present', G[u'ans_lit_present'],
                                         G[u'ans_fold_present'], G[u'ans_gap']))
for k in sorted(SEC):
    print(u'%-22s %s line %s' % (u'sec_' + k, G[u'sec_' + k], G[u'sec_' + k + u'_line']))
print(u'%-22s %s' % (u'toc_lines', G[u'toc_lines']))
print(u'--- 义务/语汇 ---')
for w in (u'must_not', u'must', u'should_not', u'should', u'may', u'required', u'recommended', u'may_not'):
    print(u'%-22s %s' % (u'u_' + w, G[u'u_' + w]))
print(u'%-22s %s' % (u'oblig_up', G[u'oblig_up']))
for w in (u'must', u'should', u'may'):
    print(u'%-22s %s' % (u'lo_' + w, G[u'lo_' + w]))
print(u'%-22s %s' % (u'oblig_low', G[u'oblig_low']))
for k, s in WK:
    print(u'%-22s %s' % (u'v_' + k, G[u'v_' + k]))
print(u'--- 身份/引用 ---')
for k, s in HK:
    print(u'%-22s %s' % (k, G[k]))
for n in (u'2068', u'2616', u'2145', u'7230', u'7231', u'9110', u'9112', u'2119', u'7235'):
    print(u'%-22s %s' % (u'cite_' + n, G[u'cite_' + n]))
print(u'%-22s %s / %s' % (u'cite_http_brk', G[u'cite_http_brk'], G[u'cite_rfc_brk']))
print(u'--- 搬运 ---')
for suf in (u'_nos', u''):
    print(u'%-16s %s only_a %s only_d %s ab %s cd %s union %s' % (
        u'lines_ge40' + suf, G[u'lines_ge40' + suf], G[u'only_a' + suf], G[u'only_d' + suf],
        G[u'share_ab' + suf], G[u'share_cd' + suf], G[u'union_all' + suf]))
print(u'%-22s %s / cd %s' % (u'shell_delta', G[u'shell_delta'], G[u'share_cd_delta']))
print(u'--- 锚池 ---')
print(u'%-22s %s tier %s close %s' % (u'pool_n', G[u'pool_n'], G[u'pool_tier'], G[u'pool_tier_close']))
print(u'%-22s %s %s %s %s | ab %s cd %s' % (u'only_2068/2616/7230/9112', G[u'pool_share1_2068'],
                                            G[u'pool_share1_2616'], G[u'pool_share1_7230'], G[u'pool_share1_9112'],
                                            G[u'pool_share2_ab'], G[u'pool_share2_cd']))
print(u'share4 byte4 %s ⇎ 分家 %s ｜ 轴 %s' % (G[u'share4_byte4'], G[u'share4_notbyte'], {a: G[u'share4_axis_' + a] for a in (u'case', u'hyph', u'space', u'multi')}))
for ax, n in G[u'share4_diff']:
    print(u'  分家 %-6s :: %s' % (ax, n[:78]))
print(u'%-22s %s' % (u'nonascii_cp', G[u'nonascii_cp']))
print(u'四份同现样例: ' + u' ⇑ '.join(x[:70] for x in G[u'pool_share4'][:3]))
print(u'已写 corpus/_b65meas.json ｜ 键 %d' % len(ORDER))
