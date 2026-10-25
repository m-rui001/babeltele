# -*- coding: utf-8 -*-
"""建条目第二遍(B70): “一条 UDP 报文的校验和到底是不是必选的、算出零值该怎么办”,
交四份一手文书各答一遍: 768(80) 全篇没有一枚 RFC 2119 大写义务词、只用零值描述“没算”
⇎ 1122(89) 能力上 MUST、默认 MUST default to checksumming on、却在下文写 the UDP checksum is optional
⇎ 8200(17) IPv6 侧把这句改成小写 must 的“not optional 是默认行为”
⇎ 6935(13) 一边引用那份小写原文并判它该删、一边把同一条规则换成大写 MUST 且插入 by default。

本遍刻意与采集侧(corpus/_pick70.py)换实现: 采集侧用 str.find 前进一枚的**重叠**口径与逐行 in 判定,
本遍用非重叠游标、正则字面轨、集合代数与 itertools 配对; 两边在同一批口径一致的键上逐量对账。
所有正文数字都由 V()/J()/EXPR() 注册后插值, 一枚都不手打; 键名等于所量之物。"""
import io, itertools, json, re, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'768', u'1122', u'8200', u'6935']
TAGS = LBL
NSRC = 4
PATH = [u'corpus/raw/udpCK/rfc768.txt', u'corpus/raw/tcpRTO/rfc1122.txt',
        u'corpus/raw/udpCK/rfc8200.txt', u'corpus/raw/udpCK/rfc6935.txt']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire70.py 把这一段 ⇎ _mk70emit.py 的 SCAN2 段机械切进 audit.py::_b70_scan)


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
L = [t.split(u'\n') for t in T]


def pnorm(s):
    return u' '.join(s.lower().split())


def cnt_cur(hay, nd):
    """非重叠游标计数(采集侧是重叠口径, 两者差单独立键对账)"""
    c = 0
    i = 0
    n = len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def cnt_ovl(hay, nd):
    c = 0
    i = 0
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + 1


def read_after(hay, token, pat):
    """游标读数: token 之后第一个匹配 pat 的组, 读不到给 None"""
    i = hay.find(token)
    if i < 0:
        return None
    m = re.compile(pat).search(hay, i + len(token))
    return None if not m else m.group(1)


GR = read_after
FO = [pnorm(t) for t in T]                     # 全篇折平(小写)
FOLD = [u' '.join(t.split()) for t in T]       # 全篇折平(保大小写)


def shell_line(l):
    if l.strip() == u'':
        return True
    if u'\x0c' in l:
        return True
    if re.match(u'^\\s*\\[?P\\[?a\\]?g?e?\\s?\\d*\\]?\\s*$', l):
        return False
    if re.match(u'^\\s*(\\[Page \\d+\\]|\\[page \\d+\\]|\\[?P\\d+\\]?)\\s*$', l):
        return True
    if re.match(u'^\\s*\\[?Page \\d+\\]?\\s*$', l):
        return True
    if re.match(u'^\\s*RFC\\s?\\d+\\s+\\S{2,}.*\\s\\d{4}\\s*$', l):
        return True
    if re.match(u'^\\s*[A-Za-z0-9]+\\s+\\S{2,}.*\\s[A-Z][a-z]+ \\d{4}\\s*$', l):
        return True
    if re.match(u'^\\s*Internet Engineering Task Force\\s+.*\\d{4}\\s*$', l):
        return True
    if re.match(u'^\\s*Internet Engineering Task Force\\s+\\[?P\\[?a\\]?g?e?\\s?\\d*\\]?\\s*\\]?\\s*$', l):
        return True
    if re.match(u'^\\s*(J. Postel|Postel|Karn|Braden|Deering|Hinden|Eubanks|Chimento|M. Westerlund|Retired|AmericaFree.TV LLC|Check Point Software|Ericsson|ISI|Johns Hopkins.*|Physics Laboratory)\\s*$', l):
        return True
    return False


SH = [[x for x in L[i] if not shell_line(x)] for i in range(NSRC)]
SHF = [u' '.join(u'\n'.join(sh).split()) for sh in SH]      # 摘壳折平(保大小写)
FO_SH = [pnorm(u'\n'.join(sh)) for sh in SH]

# ---------- 字面针: 与采集侧同一批文本, 判定换成正则字面轨 + 三面档 ----------
NEEDLE = [
    (0, u'z768_allones', u'it is transmitted  as all ones (the'),
    (0, u'z768_equiv', u'as all ones (the equivalent in one\'s complement arithmetic)'),
    (0, u'z768_allzero_means', u'checksum value means that the transmitter generated no checksum (for debugging or for higher level protocols that don\'t care)'),
    (0, u'z768_srcport', u'Source Port is an optional field, when meaningful'),
    (0, u'z768_zero_insert', u'If not used, a value of zero is inserted.'),
    (0, u'z768_ui_should', u'A user interface should allow'),
    (1, u'z1122_must_impl', u'A host MUST implement the facility to generate and validate'),
    (1, u'z1122_may_ctrl', u'An application MAY optionally be able to control whether a UDP checksum will be generated, but it MUST default to checksumming on.'),
    (1, u'z1122_discard', u'UDP MUST silently discard the datagram.'),
    (1, u'z1122_recv_opt', u'An application MAY optionally be able to control whether UDP datagrams without checksums should be discarded or passed to the application.'),
    (1, u'z1122_controversial', u'turning off UDP checksumming is very controversial.'),
    (1, u'z1122_udp_optional', u'Unlike the TCP checksum, the UDP checksum is optional; the value zero is transmitted in the checksum field of a UDP header to indicate the absence of a checksum.'),
    (1, u'z1122_all1s', u'it must transmit the checksum as all 1\'s (65535).'),
    (1, u'z1122_tcp_never', u'the TCP checksum is never optional.  The sender MUST generate it and the receiver MUST check it.'),
    (1, u'z1122_tbl_off', u'Sender Option to not generate checksum'),
    (1, u'z1122_tbl_default', u'Default is to checksum'),
    (1, u'z1122_tbl_recv', u'Receiver Option to require checksum'),
    (1, u'z1122_ip_hdr', u'A host MUST verify the IP header checksum on every received'),
    (2, u'z8200_modify', u'addresses from the IP header in its checksum computation must be modified for use over IPv6, to include the 128-bit IPv6 addresses instead of 32-bit IPv4 addresses.'),
    (2, u'z8200_default', u'the default behavior when UDP packets are originated by an IPv6 node is that the UDP checksum is not optional.'),
    (2, u'z8200_must_compute', u'an IPv6 node must compute a UDP checksum over the packet and the pseudo-header, and, if that computation yields a result of zero, it must be changed to hex FFFF for placement in the UDP header.'),
    (2, u'z8200_discard', u'IPv6 receivers must discard UDP packets containing a zero checksum and should log the error.'),
    (2, u'z8200_tunnel', u'protocols that use UDP as a tunnel encapsulation may enable zero-checksum mode for a specific port (or set of ports) for sending and/or receiving.'),
    (2, u'z8200_6936', u'Any node implementing zero-checksum mode must follow the requirements specified in "Applicability Statement for the Use of IPv6 UDP Datagrams with Zero Checksums" [RFC6936].'),
    (3, u'z6935_update', u'This specification updates IPv6 to allow a zero UDP checksum in the outer encapsulating datagram of a tunnel protocol.'),
    (3, u'z6935_delete_lead', u'The following text in [RFC2460], Section 8.1, fourth bullet should be deleted:'),
    (3, u'z6935_quote_lead', u'Unlike IPv4, when UDP packets are originated by an IPv6 node, the UDP checksum is not optional.'),
    (3, u'z6935_quote_discard', u'IPv6 receivers must discard UDP packets containing a zero checksum, and should log the error.'),
    (3, u'z6935_repl_compute', u'an IPv6 node MUST compute a UDP checksum over the packet and the pseudo-header, and, if that computation yields a result of zero, the checksum MUST be changed to hex FFFF for placement in the UDP header, as specified in [RFC2460].'),
    (3, u'z6935_repl_discard', u'IPv6 receivers MUST by default discard UDP packets containing a zero checksum and SHOULD log the error.'),
    (3, u'z6935_repl_may', u'encapsulation MAY enable zero-checksum mode for a specific port (or set of ports) for sending and/or receiving.'),
    (3, u'z6935_must_follow', u'implementing zero-checksum mode MUST follow the node requirements specified in Section 4 of "Applicability Statement for the use of IPv6 UDP Datagrams with Zero Checksums" [RFC6936].'),
    (3, u'z6935_permitted', u'while sending a UDP datagram with a zero checksum is permitted in'),
    (3, u'z6935_unsuitable', u'a zero UDP checksum is unsuitable, because it is necessary to provide the first level'),
    (3, u'z6935_middlebox', u'Middleboxes supporting IPv6 MUST follow requirements 9, 10, and 11'),
    (3, u'z6935_abst_discard', u'that IPv6 receivers MUST discard UDP packets with a zero checksum.'),
]
GN = [k for _, k, _ in NEEDLE]
OWNER = dict((k, o) for o, k, _ in NEEDLE)
TEXT = dict((k, nd) for _, k, nd in NEEDLE)
LITK.update(TEXT)
SN = {}      # 原面逐行
SNF = {}     # 全篇折平(保大小写)
SNS = {}     # 摘壳折平
SNR = {}     # 正则字面轨(转义后在折平面上 finditer)
CNT = {}
for o, k, nd in NEEDLE:
    SN[k] = [len([x for x in L[i] if nd in x]) for i in range(NSRC)]
    fl = u' '.join(nd.split())
    SNF[k] = [cnt_cur(FOLD[i], fl) for i in range(NSRC)]
    SNS[k] = [cnt_cur(SHF[i], fl) for i in range(NSRC)]
    SNR[k] = [len([1 for m in re.finditer(re.escape(fl), FOLD[i])]) for i in range(NSRC)]
    CNT[k] = [cnt_ovl(FOLD[i], fl) - SNR[k][i] for i in range(NSRC)]
KEYS = GN
F['needle_n'] = len(KEYS)
F['sn_strict_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SN[k][i] > 0) for i in range(NSRC)]
F['sn_fold_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SNF[k][i]) for i in range(NSRC)]
F['sn_sh_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SNS[k][i]) for i in range(NSRC)]
F['sn_re_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SNR[k][OWNER[k]]) for i in range(NSRC)]
F['fold_only_keys'] = [k for k in KEYS if sum(SN[k]) == 0 and SNF[k][OWNER[k]]]
F['fold_only_own'] = [len([k for k in KEYS if OWNER[k] == i and SN[k][i] == 0 and SNF[k][i]])
                      for i in range(NSRC)]
F['sh_lost_keys'] = [k for k in KEYS if SNF[k][OWNER[k]] and not SNS[k][OWNER[k]]]
F['ladder_monotone'] = 1 if all(F['sn_strict_docs'][i] + F['fold_only_own'][i] == F['sn_fold_docs'][i]
                                for i in range(NSRC)) else 0
F['sh_minus_fold'] = [F['sn_fold_docs'][i] - F['sn_sh_docs'][i] for i in range(NSRC)]
F['fold_line_zero'] = sum(1 for k in F['fold_only_keys'] if SN[k][OWNER[k]])
F['overlap_extra'] = sum(sum(CNT[k]) for k in KEYS)
F['re_eq_cur'] = 1 if all(SNR[k][OWNER[k]] == SNF[k][OWNER[k]] for k in KEYS) else 0
F['shared_verbatim'] = [k for k in KEYS if sum(1 for i in range(NSRC) if SNF[k][i]) >= 2]
F['cross_needle_n'] = len(F['shared_verbatim'])
for o, k, nd in NEEDLE:
    F['n_' + k] = SNF[k]

# ---------- 结构面量 ----------
F['bytes'] = [len(b) for b in B]
F['chars'] = [len(t) for t in T]
F['lines'] = [len(t.split(u'\n')) for t in T]
F['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['maxlen'] = [max(len(x) for x in L[i]) for i in range(NSRC)]
F['ff'] = [cnt_cur(t, u'\x0c') for t in T]
F['ff_only'] = [len([x for x in L[i] if x.strip() == u'\x0c']) for i in range(NSRC)]
F['shell_n'] = [len(SH[i]) for i in range(NSRC)]
F['shell_strip'] = [F['lines'][i] - F['shell_n'][i] for i in range(NSRC)]
F['cr'] = [cnt_cur(t, u'\r') for t in T]
F['nonascii'] = [len([c for c in t if ord(c) > 127]) for t in T]
F['bom'] = [1 if b[:3] == b'\xef\xbb\xbf' else 0 for b in B]
def utf8_extra(s):
    return sum(len(c.encode('utf-8')) - 1 for c in s)


F['nonascii_extra'] = [utf8_extra(t) for t in T]
F['byte_cp_delta'] = [F['bytes'][i] - F['chars'][i] for i in range(NSRC)]
F['nul_faces'] = [len([1 for c in t if c == u'\x00']) for t in T]
F['digit_chars'] = [len([c for c in t if c.isdigit()]) for t in T]
F['dblspace'] = [cnt_ovl(t, u'  ') for t in T]
F['dblspace_norm'] = [len(re.findall(u'(?<=\\S) {2,}(?=\\S)', t)) for t in T]
F['ascii_all'] = sum(1 for i in range(NSRC) if F['nonascii'][i] == 0)

# ---------- 头部动作字段: 现读 RFC 号集合 ----------
def hdr_ids(t, field):
    m = re.search(u'(?m)^' + field + u':\\s*(.+)$', t)
    if not m:
        return frozenset()
    return frozenset(int(x) for x in re.findall(u'\\d{3,5}', m.group(1)))


OBS = [hdr_ids(T[i], u'Obsoletes') for i in range(NSRC)]
UPD = [hdr_ids(T[i], u'Updates') for i in range(NSRC)]
F['obs_n'] = [len(s) for s in OBS]
F['upd_n'] = [len(s) for s in UPD]
F['target_ids'] = sorted(set().union(*[set(s) for s in OBS + UPD]))
F['target_n'] = len(F['target_ids'])
F['both_2460'] = 1 if (2460 in OBS[2] and 2460 in UPD[3]) else 0
F['obs_verb'] = [cnt_cur(T[i], u'Obsoletes') for i in range(NSRC)]
F['upd_verb'] = [cnt_cur(T[i], u'Updates') for i in range(NSRC)]
F['std_hdr'] = [len([1 for x in L[i] if re.match(u'^\\s*STD:\\s*\\d+', x)]) for i in range(NSRC)]
F['cat_std'] = [cnt_cur(T[i], u'Category: Standards Track') for i in range(NSRC)]
F['cat_lines'] = [len([1 for x in L[i] if re.match(u'^\\s*Category:', x)]) for i in range(NSRC)]

MON = u'January|February|March|April|May|June|July|August|September|October|November|December'
RYR = re.compile(u'(%s) +(\\d{4})\\s*$' % MON)


def hdr_year(lines):
    """标题页那行“月份 年份”: 逐行尾锚定, 不吃 ISSN: 2070-1721 这类站内编号"""
    for x in lines[:60]:
        m = RYR.search(x.strip())
        if m:
            return (int(m.group(2)), m.group(1))
    return (None, None)


YR = [hdr_year(L[i]) for i in range(NSRC)]
F['years'] = [y for y, _ in YR]
F['months'] = [mo for _, mo in YR]
F['year_n'] = len([y for y in F['years'] if y])
order = sorted(range(NSRC), key=lambda i: F['years'][i])
F['year_perm'] = order
F['year_order'] = 1 if order == list(range(NSRC)) else 0
F['year_inversions'] = len([1 for a in range(NSRC) for b in range(a + 1, NSRC)
                            if F['years'][a] > F['years'][b]])
F['year_gap_6935_8200'] = F['years'][2] - F['years'][3]
F['year_gaps'] = [F['years'][i + 1] - F['years'][i] for i in range(NSRC - 1)]

# ---------- 义务语气两轨: 子串轨 ⇎ 正则字面轨 ----------
def ub(s, w):
    return len(re.findall(u'(?<![A-Za-z])' + w + u'(?![A-Za-z])', s))


UP = {}
LO = {}
CI = {}
TI = {}
WORDS = (u'MUST', u'MAY', u'SHOULD')
for w in WORDS:
    UP[w] = [ub(T[i], w) for i in range(NSRC)]
    LO[w] = [ub(T[i], w.lower()) for i in range(NSRC)]
    CI[w] = [ub(T[i].lower(), w.lower()) for i in range(NSRC)]
    TI[w] = [ub(T[i], w[:1].upper() + w[1:].lower()) for i in range(NSRC)]
UPN = {}
for w in (u'MUST NOT', u'MAY NOT', u'SHOULD NOT'):
    UPN[w] = [cnt_cur(T[i], w) for i in range(NSRC)]
F['up_must_all'] = UP[u'MUST']
F['up_may'] = UP[u'MAY']
F['up_should'] = UP[u'SHOULD']
F['must_not'] = UPN[u'MUST NOT']
F['may_not'] = UPN[u'MAY NOT']
F['should_not'] = UPN[u'SHOULD NOT']
F['must_bare'] = [UP[u'MUST'][i] - UPN[u'MUST NOT'][i] for i in range(NSRC)]
F['low_must'] = LO[u'MUST']
F['low_may'] = LO[u'MAY']
F['low_should'] = LO[u'SHOULD']
F['ci_must'] = CI[u'MUST']
F['ci_may'] = CI[u'MAY']
F['ci_should'] = CI[u'SHOULD']
F['title_must'] = TI[u'MUST']
F['title_may'] = TI[u'MAY']
F['title_should'] = TI[u'SHOULD']
F['case_ledger'] = [sum(CI[w][i] - UP[w][i] - LO[w][i] - TI[w][i] for w in WORDS)
                    for i in range(NSRC)]
F['low_minus_up'] = [LO[u'MUST'][i] - UP[u'MUST'][i] for i in range(NSRC)]
F['up_zero_docs'] = [i for i in range(NSRC) if UP[u'MUST'][i] + UP[u'MAY'][i] + UP[u'SHOULD'][i] == 0]
F['up_zero_n'] = len(F['up_zero_docs'])
F['lo_minus_up'] = [LO[u'MUST'][i] - UP[u'MUST'][i] for i in range(NSRC)]
F['up_ledger'] = [UP[u'MUST'][i] - (F['must_bare'][i] + UPN[u'MUST NOT'][i]) for i in range(NSRC)]
F['req_word'] = [cnt_cur(T[i], u'REQUIRED') for i in range(NSRC)]
F['ck_word'] = [cnt_cur(T[i], u'checksum') for i in range(NSRC)]
F['ck_caps'] = [cnt_cur(T[i], u'Checksum') for i in range(NSRC)]
F['opt_word'] = [cnt_cur(T[i], u'optional') for i in range(NSRC)]
F['zero_word'] = [cnt_cur(T[i], u'zero') for i in range(NSRC)]
F['zero_ck'] = [cnt_cur(T[i], u'zero checksum') for i in range(NSRC)]
F['zero_hy'] = [cnt_cur(T[i], u'zero-checksum') for i in range(NSRC)]
F['zero_udp'] = [cnt_cur(T[i], u'zero UDP checksum') for i in range(NSRC)]
F['zero_forms'] = [F['zero_ck'][i] + F['zero_hy'][i] + F['zero_udp'][i] for i in range(NSRC)]
F['not_opt'] = [cnt_cur(FOLD[i], u'not optional') for i in range(NSRC)]
F['not_opt_line'] = [len([x for x in L[i] if u'not optional' in x]) for i in range(NSRC)]
F['never_opt'] = [cnt_cur(FOLD[i], u'never optional') for i in range(NSRC)]
F['udp_opt_line'] = [len([x for x in L[i] if u'UDP checksum' in x]) for i in range(NSRC)]
F['opt_line_ck'] = [len([x for x in L[i] if u'optional' in x and u'hecksum' in x]) for i in range(NSRC)]
F['pseudo'] = [cnt_cur(T[i], u'pseudo-header') + cnt_cur(T[i], u'pseudo header') for i in range(NSRC)]
F['pseudo_hy'] = [cnt_cur(T[i], u'pseudo-header') for i in range(NSRC)]
F['pseudo_sp'] = [cnt_cur(T[i], u'pseudo header') for i in range(NSRC)]
F['pseudo_close'] = [F['pseudo_hy'][i] + F['pseudo_sp'][i] - F['pseudo'][i] for i in range(NSRC)]

# ---------- 句内游标读数: 同一枚补码值的两种进制 ⇎ 位宽 ----------
NUM = {}
A1 = [read_after(FOLD[i], u"all 1's (", u'(\\d+)\\)') for i in range(NSRC)]
HX = [read_after(FOLD[i], u'changed to hex ', u'([0-9A-F]{4})') for i in range(NSRC)]
NUM['all1s_faces'] = [0 if x is None else int(x) for x in A1]
NUM['ffff_faces'] = [0 if x is None else int(x, 16) for x in HX]
NUM['all1s_dec'] = max(NUM['all1s_faces'])
NUM['ffff_8200'] = NUM['ffff_faces'][2]
NUM['ffff_6935'] = NUM['ffff_faces'][3]
NUM['radix_faces'] = [1 if (A1[i] or HX[i]) else 0 for i in range(NSRC)]
NUM['radix_forms'] = len([1 for f in (A1, HX) if any(f)])
NUM['cursor_miss'] = NUM['radix_faces'].count(0)
NUM['bits_768'] = int(read_after(FOLD[0], u'Checksum is the ', u'(\\d+)-bit'))
NUM['bits128_8200'] = int(read_after(FOLD[2], u'include the ', u'(\\d+)-bit IPv6'))
NUM['bits32_8200'] = int(read_after(FOLD[2], u'instead of ', u'(\\d+)-bit IPv4'))
NUM['mbtn_6935'] = int(read_after(FOLD[3], u'MUST follow requirements ', u'(\\d+)'))
NUM['mbtn_hi_6935'] = int(read_after(FOLD[3], u'MUST follow requirements 9, 10, and ', u'(\\d+)'))
NUM['ones_word'] = [cnt_cur(T[i], u"one's complement") for i in range(NSRC)]
NUM['ones_compl_fold'] = [cnt_cur(FOLD[i], u'complement') for i in range(NSRC)]
NUM['ffff_lit'] = [cnt_cur(T[i], u'FFFF') for i in range(NSRC)]
NUM['dec_lit'] = [cnt_cur(T[i], u'65535') for i in range(NSRC)]
NUM['radix_face_n'] = sum(NUM['radix_faces'])
for k, v in NUM.items():
    F[u'num_' + k] = v
F['bits_ratio128'] = NUM['bits128_8200'] // NUM['bits_768']
F['bits_ratio32'] = NUM['bits32_8200'] // NUM['bits_768']
F['bits_sum_8200'] = NUM['bits128_8200'] + NUM['bits32_8200']
F['mbtn_span_6935'] = NUM['mbtn_hi_6935'] - NUM['mbtn_6935']

# ---------- 引用写法两族 ----------
CITE = {}
for n in (u'768', u'1122', u'8200', u'6935', u'2460', u'6936', u'793'):
    CITE['sp_' + n] = [cnt_cur(T[i], u'RFC ' + n) for i in range(NSRC)]
    CITE['hy_' + n] = [cnt_cur(T[i], u'RFC-' + n) for i in range(NSRC)]
    CITE['tk_' + n] = [cnt_cur(T[i], u'RFC' + n) for i in range(NSRC)]
    CITE['al_' + n] = [CITE['sp_' + n][i] + CITE['hy_' + n][i] + CITE['tk_' + n][i] for i in range(NSRC)]
for k in CITE:
    F['cite_' + k] = CITE[k]
F['cite_forms_2460'] = [len([x for x in (u'sp', u'hy', u'tk') if CITE[x + u'_2460'][i]]) for i in range(NSRC)]
F['cite_forms_close'] = [len(re.findall(u'RFC[ -]?2460', T[i])) - CITE['al_2460'][i] for i in range(NSRC)]
F['cite_self'] = [CITE['al_' + n][i] for i, n in enumerate((u'768', u'1122', u'8200', u'6935'))]
F['cite_8200_in_6935'] = CITE['al_8200'][3]
F['cite_6935_in_8200'] = CITE['al_6935'][2]
F['cite_dir_8200_to_6935'] = CITE['al_6935'][2]
F['cite_dir_6935_to_8200'] = CITE['al_8200'][3]
F['cite_2460_in_6935'] = CITE['al_2460'][3]
F['cite_2460_in_8200'] = CITE['al_2460'][2]
F['cite_6936'] = [CITE['al_6936'][i] for i in range(NSRC)]

# ---------- 答句邻域窗(±BAND 行) ----------
BAND = 20
HEADND = {0: u'^Fields$', 1: u'^\\s+4\\.1\\.3\\.4\\s+UDP Checksums', 2: u'^8\\.1\\.\\s+Upper-Layer Checksums',
          3: u'^5\\.\\s+The Zero UDP Checksum Update'}
ANS = {0: u'it is transmitted  as all ones', 1: u'MUST default to checksumming on.',
       2: u'node must compute a UDP checksum', 3: u'MUST by default'}


def ans_line(i):
    for n, x in enumerate(L[i], 1):
        if ANS[i] in x:
            return n
    return None


def sec_head(i):
    rx = re.compile(HEADND[i])
    for n, x in enumerate(L[i], 1):
        if rx.search(x.strip() if i == 0 else x):
            return n
    return None


def sec_window(i):
    a = ans_line(i)
    h = sec_head(i)
    lo = max(1, a - BAND)
    hi = min(len(L[i]), a + BAND)
    body = u'\n'.join(L[i][lo - 1:hi])
    outb = u'\n'.join(L[i][:lo - 1] + L[i][hi:])
    fb = u' '.join(body.split())
    return {u'head': L[i][h - 1].strip() if h else None, u'sec': h, u'ans': a,
            u'head_ln': h, u'start': lo, u'end': hi, u'rows': hi - lo + 1,
            u'chars': len(body), u'chars_out': len(outb),
            u'ck_in': cnt_cur(fb, u'checksum'), u'ck_out': cnt_cur(u' '.join(outb.split()), u'checksum'),
            u'zero_in': cnt_cur(fb, u'zero'), u'zero_out': cnt_cur(u' '.join(outb.split()), u'zero'),
            u'opt_in': cnt_cur(fb, u'optional'), u'opt_out': cnt_cur(u' '.join(outb.split()), u'optional'),
            u'dig_in': len([c for c in body if c.isdigit()]),
            u'dig_out': len([c for c in outb if c.isdigit()]),
            u'up_in': ub(fb, u'MUST') + ub(fb, u'MAY') + ub(fb, u'SHOULD'),
            u'up_out': ub(u' '.join(outb.split()), u'MUST') + ub(u' '.join(outb.split()), u'MAY')
                      + ub(u' '.join(outb.split()), u'SHOULD')}


WIN = [sec_window(i) for i in range(NSRC)]
for k in (u'head', u'sec', u'ans', u'start', u'end', u'rows', u'chars', u'chars_out',
          u'ck_in', u'ck_out', u'zero_in', u'zero_out', u'opt_in', u'opt_out',
          u'dig_in', u'dig_out', u'up_in', u'up_out'):
    F[u'win_' + k] = [w[k] for w in WIN]
F['win_band'] = BAND
F['win_named'] = len([w for w in WIN if w['sec']])
F['win_close_ck'] = [w['ck_in'] + w['ck_out'] - cnt_cur(FOLD[i], u'checksum') for i, w in enumerate(WIN)]
F['win_close_zero'] = [w['zero_in'] + w['zero_out'] - cnt_cur(FOLD[i], u'zero') for i, w in enumerate(WIN)]
F['win_close_opt'] = [w['opt_in'] + w['opt_out'] - cnt_cur(FOLD[i], u'optional') for i, w in enumerate(WIN)]
F['win_close_up'] = [w['up_in'] + w['up_out'] - (ub(FOLD[i], u'MUST') + ub(FOLD[i], u'MAY') + ub(FOLD[i], u'SHOULD'))
                     for i, w in enumerate(WIN)]
F['win_close_dig'] = [w['dig_in'] + w['dig_out'] - F['digit_chars'][i] for i, w in enumerate(WIN)]
F['win_close_sum'] = (sum(F['win_close_ck']) + sum(F['win_close_zero']) + sum(F['win_close_opt'])
                      + sum(F['win_close_dig']) + sum(F['win_close_up']))
F['win_spans'] = [w['end'] - w['start'] + 1 for w in WIN]
F['win_share'] = len([w for w in WIN if w['head'] and u'hecksum' in w['head']])

# ---------- 共用长行: 摘壳原面上的归一 ⇎ 逐字节两把尺 ----------
def pool_lines(i):
    return [x for x in SH[i] if len(pnorm(x)) >= 40]


POOLC = [Counter(pnorm(x) for x in pool_lines(i)) for i in range(NSRC)]
NPOOL = [set(POOLC[i]) for i in range(NSRC)]
pool_all = set().union(*NPOOL)
tier = [0, 0, 0, 0]
pres = defaultdict(list)
for a in pool_all:
    ds = tuple(i for i in range(NSRC) if a in NPOOL[i])
    pres[a] = ds
    tier[len(ds) - 1] += 1
F['pool_n'] = len(pool_all)
F['pool_tier'] = tier
F['pool_tier_close'] = sum(tier) - len(pool_all)
F['pool_4'] = tier[3]
F['pool_3'] = tier[2]
F['pool_2'] = tier[1]
F['pool_1'] = tier[0]
PAIRS = [(a, b) for a, b in itertools.combinations(range(NSRC), 2)]
pair_share = []
pair_byte = []
pair_norm_only = []
for i, j in PAIRS:
    inter = NPOOL[i] & NPOOL[j]
    bo = sum(1 for s in inter if any(pnorm(x) == s and x in SH[j] for x in pool_lines(i)))
    pair_share.append(len(inter))
    pair_byte.append(bo)
    pair_norm_only.append(len(inter) - bo)
F['pair_share'] = pair_share
F['pair_byte'] = pair_byte
F['pair_norm_only'] = pair_norm_only
F['pair_nonzero'] = len([x for x in pair_share if x])
F['pair_close'] = sum(pair_share) - sum(pair_byte) - sum(pair_norm_only)
F['s3_examples'] = sorted([a for a, v in pres.items() if len(v) >= 3])
F['s3_docs'] = 3 if tier[2] else 0
F['tri_share'] = [len([a for a, v in pres.items() if len(v) >= 3 and i in v]) for i in range(NSRC)]
_t1 = sum(len(v) for v in pres.values())
_t2 = sum(len(v) * (len(v) - 1) // 2 for v in pres.values())
_t3 = sum(len(v) * (len(v) - 1) * (len(v) - 2) // 6 for v in pres.values())
_t4 = len([v for v in pres.values() if len(v) == NSRC])
F['pool_incl'] = [_t1, _t2, _t3, _t4]
F['union_incl'] = _t1 - _t2 + _t3 - _t4
F['union_close'] = F['pool_n'] - F['union_incl']
letters = re.compile(u'[A-Za-z]')
F['pool_letters'] = len([a for a in pool_all if letters.search(a)])
F['pool_border'] = F['pool_n'] - F['pool_letters']

# ---------- 写法分家轴: 归一同形而逐字节不同的共用长行按“差在哪”分桶 ----------
axis = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
for a, v in pres.items():
    if len(v) < 2:
        continue
    xs = []
    for i in v:
        xs += [x for x in SH[i] if pnorm(x) == a]
    if len(set(xs)) < 2:
        continue
    o, p = xs[0], xs[1]
    if len(o) == len(p) and o != p and all(x.lower() == y.lower() for x, y in zip(o, p)):
        axis[u'case'] += 1
    elif (u'-' in o) != (u'-' in p):
        axis[u'hyph'] += 1
    elif len(re.split(u' +', o.strip())) == len(re.split(u' +', p.strip())):
        axis[u'space'] += 1
    else:
        axis[u'multi'] += 1
F['axis_counts'] = axis
F['axis_total'] = sum(axis.values())
F['axis_close'] = F['axis_total'] - sum(pair_norm_only)
F['axis_str'] = u'⇎'.join(u'%s%d' % (a, axis[a]) for a in (u'case', u'hyph', u'space', u'multi'))
F['axis_str_n'] = len([a for a in (u'case', u'hyph', u'space', u'multi') if axis[a]])

# ---------- 锚候选池(按标签 ⇎ 按份数两本账) ----------
apool = []
for i in range(NSRC):
    for x in SH[i]:
        if len(pnorm(x)) >= 24 and letters.search(x):
            apool.append((pnorm(x), i))
AP = defaultdict(set)
for a, i in apool:
    AP[a].add(i)
F['apool_n'] = len(AP)
F['apool_raw_n'] = len(apool)
F['apool_face_raw'] = [len([1 for a, k in apool if k == i]) for i in range(NSRC)]
F['apool_tag_n'] = [len([a for a, v in AP.items() if i in v]) for i in range(NSRC)]
F['apool_dup'] = [F['apool_face_raw'][i] - F['apool_tag_n'][i] for i in range(NSRC)]
F['apool_tag_close'] = sum(F['apool_tag_n']) + sum(F['apool_dup']) - F['apool_raw_n']
F['apool_tier'] = [len([a for a, v in AP.items() if len(v) == n]) for n in range(1, NSRC + 1)]
F['apool_uniq'] = len(AP)
F['apool_pairs'] = sum(F['apool_tag_n'])
F['apool_weight'] = sum(F['apool_tier'][n] * (n + 1) for n in range(NSRC))
F['apool_tier_close'] = F['apool_weight'] - F['apool_pairs']
F['apool_maxlen'] = max(len(a) for a in AP)
CLOSE = {}
CLOSE[u'base_value_agree'] = 0 if NUM['all1s_dec'] == NUM['ffff_8200'] == NUM['ffff_6935'] else 1
CLOSE[u'base_absent_768'] = 0 if NUM['radix_faces'][0] == 0 else 1
CLOSE[u'radix_three'] = 0 if sum(NUM['radix_faces']) == 3 else 1
CLOSE[u'bits128_close'] = 0 if NUM['bits_768'] * F['bits_ratio128'] == NUM['bits128_8200'] else 1
CLOSE[u'bits32_close'] = 0 if NUM['bits_768'] * F['bits_ratio32'] == NUM['bits32_8200'] else 1
CLOSE[u'year_perm_close'] = 0 if F['year_inversions'] == 1 else 1
F[u'year_gap'] = F['year_gap_6935_8200']
CLOSE[u'target_agree'] = 0 if F['both_2460'] and F['target_n'] == 1 else 1
CLOSE[u'cite_dir_unique'] = 0 if (F['cite_dir_8200_to_6935'] and not F['cite_dir_6935_to_8200']) else 1
F[u'fold_split_8200'] = 1 if (F['not_opt'][2] and not F['not_opt_line'][2]) else 0
F[u'std_no_upper'] = 1 if (F['std_hdr'][2] and F['up_must_all'][2] + F['up_may'][2] + F['up_should'][2] == 0) else 0
F[u'low_only_8200'] = 1 if (F['low_must'][2] and not F['up_must_all'][2]) else 0
for k in CLOSE:
    F[k] = CLOSE[k]
ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"F['pair_close']", u'两两“归一同形”减“逐字节同形”再减“只归一同形”应回到零(池代数闭合)')
Z(u"F['pool_tier_close']", u'共用长行按份数分档之和=池条数')
Z(u"F['axis_close']", u'写法分家轴四桶之和=“归一同形而逐字节不同”的条数')
Z(u"F['union_close']", u'按份数加权和=单份集合大小之和−两两交+…(容斥对账)')
Z(u"F['apool_tier_close']", u'锚候选池按“几份面上出现”加权分档之和=池条目数')
Z(u"F['apool_tag_close']", u'锚候选池按标签分布之和=池条目数')
Z(u"F['ladder_monotone'] - 1", u'三面阶梯单调: 逐行档 + 折行独有档 = 折平档')
Z(u"F['re_eq_cur'] - 1", u'正则字面轨与非重叠游标轨在同一批针上逐枚相等')
Z(u"F['overlap_extra']", u'重叠口径减非重叠口径在全库针上合计为零(没有自重叠针)')
Z(u"F['fold_line_zero']", u'折行独有的针按逐行口径必须全为零')
Z(u"sum(F['sh_minus_fold'])", u'摘壳折平档一枚不丢(四份的壳行里没有答句)')
Z(u"sum([abs(x) for x in F['up_ledger']])", u'大写 MUST 总数 = 裸 MUST + MUST NOT(正则轨⇎子串轨对齐)')
Z(u"sum([abs(x) for x in F['case_ledger']])", u'每份面: 大写档 + 小写档 + 首字母大写档 = 不分大小写档(语气轨四轨咬合)')
Z(u"F['win_close_sum']", u'答句邻域窗五轨(校验和⇎零⇎可选⇎数字符⇎大写义务词)带内+带外=全篇')
Z(u"len(F['s3_examples']) - F['pool_3']", u'三份同现的共用长行枚数=池分档第三档')
Z(u"CLOSE['base_value_agree']", u'1122 的十进制 65535 ⇎ 8200/6935 的 hex FFFF 现读同一枚值')
Z(u"CLOSE['base_absent_768']", u'768 面上两种进制都读不到(它只写 all ones 不给数)')
Z(u"CLOSE['radix_three']", u'四份里恰有三份给得出这枚补码值的进制写法')
Z(u"CLOSE['bits128_close']", u'8200 的 128 位地址是 768 那枚校验和位宽的整数倍(整除余零)')
Z(u"CLOSE['bits32_close']", u'8200 的 32 位地址同理')
Z(u"CLOSE['year_perm_close']", u'标题页年份现读恰有一处倒序(8200 在 6935 之后出版, 序号不是时间序)')
Z(u"CLOSE['target_agree']", u'8200 的 Obsoletes 与 6935 的 Updates 指向同一份 RFC 号、全库目标号只此一枚')
Z(u"CLOSE['cite_dir_unique']", u'8200 引用 6935 而 6935 面上读不到 8200(引用只能流向后出的一方)')
Z(u"sum(F['nul_faces'])", u'四份面上 NUL 全零(LF 面之外没有第二种控制符)')
Z(u"sum(F['cr'])", u'四份 CR 全零')
Z(u"sum(F['bom'])", u'四份都没有 BOM(与 9293 那代排版面不同)')
Z(u"max([abs(F['byte_cp_delta'][i] - F['nonascii_extra'][i]) for i in range(NSRC)])",
  u'字节数−码位数 = 每枚非 ASCII 码位的 utf-8 加字节数(全零⇒四份纯 ASCII)')
Z(u"F['ascii_all'] - NSRC", u'四份全是纯 ASCII 面')
Z(u"len([1 for i in range(NSRC) if F['ff'][i]]) - NSRC", u'四份都带换页符(768 也有 3 枚, 壳轨不为某一份空转)')
Z(u"sum(F['cite_forms_close'])", u'2460 的三种写法子串轨相加=一条正则族读出的枚数(写法族账闭合)')
Z(u"F['not_opt'][2] - F['not_opt'][3]", u'“not optional”半句在 8200 与 6935 面上各一枚(6935 引的就是它)')
Z(u"1 - F['fold_split_8200']", u'8200 面上“not optional”被行界劈开: 折平档 1 枚 ⇎ 逐行档 0 枚(读到逐行档非零即为失败态)')
Z(u"F['obs_n'][2] - F['upd_n'][3]", u'8200 废止一枚 ⇎ 6935 更新一枚: 数量同、动作词不同')
Z(u"1 - F['both_2460']", u'8200 与 6935 的动作对象都读到 2460(读不到即为失败态)')
Z(u"F['win_named'] - NSRC", u'四份都定位到答句所在小节的标题行')
Z(u"F['sn_strict_docs'][2]", u'8200 的答句整段被行界劈开: 逐行档一枚不中(本条折平档必需的最强证据)')
Z(u"len([i for i in range(NSRC) if F['sn_strict_docs'][i]]) - 3",
  u'逐行档命中三份, 8200 一份全落空(四份都落空则阶梯证据反了)')
Z(u"F['cite_forms_2460'][3] - F['cite_forms_2460'][2]", u'2460 的引用写法族在 8200 ⇎ 6935 里同数(两族都现读)')
Z(u"1 - F['std_no_upper']", u'8200 是带 STD: 号的现行标准而全篇零大写义务词(读到一枚即为失败态)')
Z(u"len(F['up_zero_docs']) - 2", u'零大写义务词的恰是 768 与 8200 两份')
Z(u"F['opt_line_ck'][0]", u'768 面上 optional 一枚都不与 checksum 同行(它唯一的 optional 说的是源端口)')
Z(u"F['opt_word'][0] - 1", u'768 全篇只写了一枚 optional')
Z(u"sum(F['never_opt']) - 1", u'“never optional”全库恰一枚, 落在 1122 的 TCP 侧(与同文 UDP 那句 optional 对照)')
Z(u"F['digit_chars'][0] - F['win_dig_in'][0] - F['win_dig_out'][0]", u'768 短面上的数字符按窗切分前后一致')
Z(u"sum(F['win_close_up'])", u'大写义务词按窗切分的带内+带外=全篇(与四轨账同向再核一遍)')
F['zid_n'] = len(ZID)
ZF = [w for e, w in ZID if eval(e.strip().replace(u'\n', u''))]
F['zid_fail'] = ZF


def _ev(e):
    return eval(e.strip().replace(u'\n', u''))


for e, w in ZID:
    if _ev(e):
        print(u'  失败: ' + w + u' <= ' + e.strip() + u' -> ' + repr(_ev(e)))
F['scalar_clos_n'] = len(ZID)
F['scalar_clos_sum'] = sum(1 for e, w in ZID if not _ev(e))
F['list_clos_n'] = len([k for k in F if (u'_close' in k or u'_ledger' in k) and isinstance(F[k], list)])
F['x_ident_n'] = len(ZID)
# --- SCAN END ---
# ---------- ZID 的 B70V 形(与 python 形逐条对拍后送 DERIV) ----------
BB70 = lambda name, i=None: (F[name] if i is None else F[name][i])
FN = u'B70V'
_to_v = re.compile(r"(?:F|CLOSE)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B70V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(4)').replace(u'NSRC', u'4')


ZV = []
for e, w in ZID:
    v = to_v(e.replace(u'\n', u''))
    if eval(v, {FN: BB70}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))

print(u'第二遍量测完成: 扁平键 %d ｜ 恒等式 %d ｜ 失败 %d ｜ 针 %d ｜ 池 %d ｜ 锚池 %d ｜ 读数 %s'
      % (len(F), len(ZID), len(ZF), len(SN), F['pool_n'], F['apool_n'], NUM))
print(u'结构 bytes=%s chars=%s lines=%s nonblank=%s maxlen=%s' % (F['bytes'], F['chars'], F['lines'], F['nonblank'], F['maxlen']))
print(u'版式 ff=%s ff_only=%s shell=%s strip=%s cr=%s nonascii=%s bom=%s extra=%s delta=%s dblsp=%s digit=%s'
      % (F['ff'], F['ff_only'], F['shell_n'], F['shell_strip'], F['cr'], F['nonascii'], F['bom'],
         F['nonascii_extra'], F['byte_cp_delta'], F['dblspace'], F['digit_chars']))
print(u'阶梯 strict=%s fold=%s shell=%s re=%s fold_only=%d(%s) sh_lost=%s overlap=%d re_eq=%d'
      % (F['sn_strict_docs'], F['sn_fold_docs'], F['sn_sh_docs'], F['sn_re_docs'],
         len(F['fold_only_keys']), F['fold_only_own'], F['sh_lost_keys'], F['overlap_extra'], F['re_eq_cur']))
print(u'义务 大写MUST=%s bare=%s MUSTNOT=%s MAY=%s SHOULD=%s | 小写must=%s may=%s should=%s | 无视大小写=%s | 账=%s 案例=%s 零大写份=%s'
      % (F['up_must_all'], F['must_bare'], F['must_not'], F['up_may'], F['up_should'],
         F['low_must'], F['low_may'], F['low_should'], F['ci_must'],
         F['up_ledger'], F['case_ledger'], F['up_zero_docs']))
print(u'词轨 ck=%s CK=%s opt=%s notopt(折)=%s notopt(行)=%s never=%s zero=%s zerock=%s zerohy=%s zeroudp=%s forms=%s pseudo=%s req=%s'
      % (F['ck_word'], F['ck_caps'], F['opt_word'], F['not_opt'], F['not_opt_line'], F['never_opt'],
         F['zero_word'], F['zero_ck'], F['zero_hy'], F['zero_udp'], F['zero_forms'], F['pseudo'], F['req_word']))
print(u'数读 %s radix_faces=%s miss=%d forms=%d ratio=%s/%s sum=%d span=%s' % (
    NUM, NUM['radix_faces'], NUM['cursor_miss'], NUM['radix_forms'],
    F['bits_ratio128'], F['bits_ratio32'], F['bits_sum_8200'], F['mbtn_span_6935']))
print(u'头部 obs=%s upd=%s target=%s both=%s std=%s cat=%s catstd=%s years=%s months=%s perm=%s inv=%d gap=%d' % (
    F['obs_n'], F['upd_n'], F['target_ids'], F['both_2460'], F['std_hdr'], F['cat_lines'], F['cat_std'],
    F['years'], F['months'], F['year_perm'], F['year_inversions'], F['year_gap_6935_8200']))
print(u'语气判据 std_no_upper=%d low_only_8200=%d fold_split=%d opt_line_ck=%s dir=%s⇎%s forms_close=%s' % (
    F['std_no_upper'], F['low_only_8200'], F['fold_split_8200'], F['opt_line_ck'],
    F['cite_dir_8200_to_6935'], F['cite_dir_6935_to_8200'], F['cite_forms_close']))
print(u'引用 sp2460=%s tk2460=%s hy2460=%s forms=%s self=%s 8200in6935=%s 6935in8200=%s 6936=%s' % (
    F['cite_sp_2460'], F['cite_tk_2460'], F['cite_hy_2460'], F['cite_forms_2460'], F['cite_self'],
    F['cite_8200_in_6935'], F['cite_6935_in_8200'], F['cite_6936']))
print(u'窗 head=%s sec=%s ans=%s start=%s end=%s rows=%s ck_in=%s ck_out=%s zero_in=%s opt_in=%s up_in=%s 闭合=%s' % (
    F['win_head'], F['win_sec'], F['win_ans'], F['win_start'], F['win_end'], F['win_rows'],
    F['win_ck_in'], F['win_ck_out'], F['win_zero_in'], F['win_opt_in'], F['win_up_in'], F['win_close_sum']))
print(u'池 n=%d tier=%s letters=%d border=%d pair_share=%s pair_byte=%s only=%s 非零对=%d 闭合=%d 轴=%s 轴账=%d'
      % (F['pool_n'], F['pool_tier'], F['pool_letters'], F['pool_border'], F['pair_share'],
         F['pair_byte'], F['pair_norm_only'], F['pair_nonzero'], F['pair_close'], F['axis_counts'], F['axis_close']))
print(u'三现例 %s ｜ union_close=%d apool=%s tag_n=%s tier=%s tag_close=%d maxlen=%d' % (
    F['s3_examples'], F['union_close'], F['apool_n'], F['apool_tag_n'], F['apool_tier'],
    F['apool_tag_close'], F['apool_maxlen']))

# ---------- 锚(逐字原行, 由位置导出) ----------
IDX = {t: n for n, t in enumerate(LBL)}
FAN = FO
ATOMFAIL = []


def AN(i, *nd):
    for l in L[i]:
        if all(x in l for x in nd):
            return u'⟦%s⟧⟨%s⟩' % (LBL[i], l)
    ATOMFAIL.append((LBL[i], nd))
    raise AssertionError(u'锚导出失败 %s %s' % (LBL[i], nd))


# ---------- DERIV 登记 ----------
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


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB70}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([tuple(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out

exec(io.open(u'corpus/_mk70emit.py', encoding='utf-8').read())
