# -*- coding: utf-8 -*-
# B70 pass 1 (collection): "is the UDP checksum mandatory, and what does a zero value mean?"
# 768 (1980) vs 1122 (1989, IPv4 requirements) vs 8200 (2017, IPv6) vs 6935 (2013, update of 2460).
# Independent implementation of the caliber definitions; dumps corpus/_b70meas.json.
from __future__ import print_function
import io, json, re

PATHS = [u'corpus/raw/udpCK/rfc768.txt', u'corpus/raw/tcpRTO/rfc1122.txt',
         u'corpus/raw/udpCK/rfc8200.txt', u'corpus/raw/udpCK/rfc6935.txt']
LBL = [u'768', u'1122', u'8200', u'6935']

def fold(s):
    return re.sub(u'\\s+', u' ', s).strip()

def occ(h, n):
    c = i = 0
    while True:
        j = h.find(n, i)
        if j < 0:
            return c
        c += 1
        i = j + 1

HDR = [re.compile(u'^\\s*Internet Engineering Task Force\\s+\\[?Page \\d+\\]?\\s*$'),
       re.compile(u'^\\s*Internet Engineering Task Force\\s+.*\\[Page \\d+\\]\\s*$'),
       re.compile(u'^\\s*RFC\\s?\\d+\\s+\\S.*\\s\\d{4}\\s*$'),
       re.compile(u'^\\s*RFC\\s?\\d+\\s+\\S.*\\s(\\d{4}|[A-Z][a-z]+ \\d{4})\\s*$'),
       re.compile(u'^\\s*[A-Za-z0-9]+\\s+\\S.*\\s[A-Z][a-z]+ \\d{4}\\s*$'),
       re.compile(u'^\\s*\\[Page \\d+\\]\\s*$'),
       re.compile(u'^\\s*Karn\\s*$'),
       re.compile(u'^\\s*Postel\\s*$')]
FOOT = [re.compile(u'^\\s*\\[?Page \\d+\\]?\\s*$'), re.compile(u'^\\s*\\[Page \\d+\\]\\s*$')]

def is_shell(l):
    if l.strip() == u'':
        return True
    if u'\x0c' in l:
        return True
    for r in HDR + FOOT:
        if r.match(l):
            return True
    return False

R = []
T = []
L = []
FO = []
FSH = []
SH = []
for p in PATHS:
    b = io.open(p, 'rb').read()
    t = b.decode('latin-1')
    ls = t.split(u'\n')
    sh = [x for x in ls if not is_shell(x)]
    R.append({'path': p, 'BS': len(b), 'LN': t.count(u'\n') + 1,
              'FF': occ(t, u'\x0c'), 'CR': occ(t, u'\r'),
              'NB': len([x for x in ls if x.strip() != u'']),
              'SH_N': len(sh), 'SHFF': len([x for x in sh if u'\x0c' in x]),
              'NONASCII': len([c for c in t if ord(c) > 127]),
              'DIGITS': len([c for c in t if c.isdigit()]),
              'DSPACE': len([1 for m in re.finditer(u'(?<=\\S)  +(?=\\S)', t)])})
    T.append(t)
    L.append(ls)
    FO.append(fold(t))
    SH.append(sh)
    FSH.append(fold(u'\n'.join(sh)))

BIG = [u'MUST NOT', u'MUST', u'MAY NOT', u'MAY', u'SHOULD NOT', u'SHOULD', u'REQUIRED',
       u'must not', u'must', u'may not', u'may', u'should not', u'should',
       u'optional', u'not optional', u'never optional',
       u'zero checksum', u'zero-checksum', u'zero UDP checksum',
       u'all ones', u"all 1's", u'FFFF', u'ffff', u'65535', u'all zero',
       u'checksum', u'Checksum', u'pseudo-header',
       u'RFC 768', u'RFC-768', u'RFC 8200', u'RFC-8200', u'RFC 6935', u'RFC-6935',
       u'RFC 2460', u'RFC2460', u'RFC 6936', u'RFC6936', u'RFC 793', u'RFC-793',
       u'RFC 1122', u'RFC-1122', u'[Page ', u'Updates', u'Obsoletes', u'Category', u'STD']
for i in range(4):
    R[i]['words'] = dict((w, occ(T[i], w)) for w in BIG)
    R[i]['fold_words'] = dict((w, occ(FO[i], fold(w))) for w in BIG if u'  ' in w or u'\n' in w)

# ---- needle register: (owner, key, verbatim-in-one-line | folded sentence) ----
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

MIS = []
REG = []
for (o, k, nd) in NEEDLE:
    fl = fold(nd)
    lineface = len([x for x in L[o] if nd in x])
    lf_fold = len([x for x in L[o] if fl in fold(x)])
    cnt_o = occ(T[o], nd)
    cnt_f = occ(FO[o], fl)
    cnt_s = occ(FSH[o], fl)
    REG.append({'o': o, 'k': k, 'line': lineface, 'line_fold': lf_fold,
                'orig': cnt_o, 'fold': cnt_f, 'shell': cnt_s})
    if cnt_f == 0:
        stem = u' '.join(fl.split()[:6])
        cand = [n for n, x in enumerate(L[o], 1) if stem.split()[0] in x]
        MIS.append((o, k, fl, cand[:4]))

print(u'== base ==')
for i in range(4):
    r = R[i]
    print(u'%s BS=%d LN=%d FF=%d CR=%d NB=%d SH=%d NA=%d DS=%d DIG=%d' % (
        LBL[i], r['BS'], r['LN'], r['FF'], r['CR'], r['NB'], r['SH_N'],
        r['NONASCII'], r['DSPACE'], r['DIGITS']))
print(u'== obligations ==')
for i in range(4):
    w = R[i]['words']
    print(u'%s  MUST=%d MAY=%d SHOULD=%d MUSTNOT=%d MAYNOT=%d | must=%d may=%d should=%d mustnot=%d maynot=%d shouldnot=%d' % (
        LBL[i], w[u'MUST'], w[u'MAY'], w[u'SHOULD'], w[u'MUST NOT'], w[u'MAY NOT'],
        w[u'must'], w[u'may'], w[u'should'], w[u'must not'], w[u'may not'], w[u'should not']))
print(u'== headers (1..30) ==')
for i in (0, 2, 3):
    print(u'-- %s' % LBL[i])
    for n in range(1, 31):
        if n <= len(L[i]) and L[i][n - 1].strip() != u'':
            print(u'%4d|%s|' % (n, L[i][n - 1]))
print(u'== extra ranges ==')
for i, rng in ((3, (140, 160)), (3, (400, 412)), (0, (55, 84)), (1, (4566, 4584))):
    print(u'-- %s %d..%d' % (LBL[i], rng[0], rng[1]))
    for n in range(rng[0], rng[1] + 1):
        if 1 <= n <= len(L[i]):
            print(u'%5d|%s|' % (n, L[i][n - 1]))
print(u'== needles ==')
for e in REG:
    print(u'%-6s %-22s line=%d lfold=%d orig=%d fold=%d shell=%d' % (
        LBL[e['o']], e['k'], e['line'], e['line_fold'], e['orig'], e['fold'], e['shell']))
print(u'== misses ==')
for (o, k, fl, cand) in MIS:
    print(u'MISS %s %s :: %s' % (LBL[o], k, fl))
    for n in cand:
        print(u'      %5d|%s|' % (n, L[o][n - 1]))

# ---- cross-doc shared long lines (normalized, shell-stripped line face) ----
def pn(s):
    return re.sub(u'\\s+', u' ', s).strip().lower()

sets = []
for i in range(4):
    sets.append(set(pn(x) for x in SH[i] if len(pn(x)) >= 40))
pres = {}
for i, s in enumerate(sets):
    for a in s:
        pres.setdefault(a, []).append(i)
multi = dict((n, len([a for a, v in pres.items() if len(v) == n])) for n in (1, 2, 3, 4))
pairs = {}
for a, v in pres.items():
    if len(v) >= 2:
        for x in range(len(v)):
            for y in range(x + 1, len(v)):
                pairs[(v[x], v[y])] = pairs.get((v[x], v[y]), 0) + 1
print(u'== shared long lines ==')
print(u'by nsrc %s  pairs %s' % (json.dumps(multi), json.dumps(dict(
    ('%s-%s' % (LBL[a], LBL[b]), c) for (a, b), c in sorted(pairs.items())))))
for a, v in sorted(pres.items()):
    if len(v) >= 3:
        print(u'  TRI %s :: %s' % ('/'.join(LBL[x] for x in v), a[:90]))

# ---- 8200 own text vs 6935 quoted-2460 vs 6935 replacement ----
def para(i, lo, hi):
    return fold(u'\n'.join(L[i][lo - 1:hi]))

P82 = para(2, 1530, 1537)
P6Q = para(3, 466, 472)
P6R = para(3, 479, 485)
P6T = para(3, 487, 492)
CMP = {'82_own': P82, '6935_quote': P6Q, '6935_repl': P6R, '6935_tunnel': P6T}
for k, v in CMP.items():
    print(u'== para %s ==\n%s' % (k, v))
w82 = set(re.findall(u'[A-Za-z0-9\'"-]+', P82.lower()))
w6q = set(re.findall(u'[A-Za-z0-9\'"-]+', P6Q.lower()))
w6r = set(re.findall(u'[A-Za-z0-9\'"-]+', P6R.lower()))
print(u'82only %s | q69only %s | repl_only %s | 82xq %d | 82xrepl %d' % (
    sorted(w82 - w6q), sorted(w6q - w82), sorted(w6r - w82 - w6q),
    len(w82 & w6q), len(w82 & w6r)))
for f in (u'by default', u', and should log', u'and should log', u'MUST by default'):
    print(u'phrase %-16s : 8200=%d 6935quote=%d 6935repl=%d' % (
        f, occ(P82, f), occ(P6Q, f), occ(P6R, f)))

out = {'base': [{k: v for k, v in r.items() if k != 'words'} for r in R],
       'words': [r['words'] for r in R], 'needles': REG,
       'misses': [[LBL[o], k] for (o, k, f, c) in MIS],
       'shared_by_nsrc': multi, 'shared_pairs': dict(('%s-%s' % (LBL[a], LBL[b]), c) for (a, b), c in pairs.items()),
       'paras': CMP}
io.open('corpus/_b70meas.json', 'wb').write(json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8'))
print(u'DUMPED misses=%d' % len(MIS))
