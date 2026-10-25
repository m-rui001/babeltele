# -*- coding: utf-8 -*-
# B70 probe: dump verbatim line ranges + base counts for the four UDP-checksum documents.
from __future__ import print_function
import io, json, re

P = {
    0: u'corpus/raw/udpCK/rfc768.txt',
    1: u'corpus/raw/tcpRTO/rfc1122.txt',
    2: u'corpus/raw/udpCK/rfc8200.txt',
    3: u'corpus/raw/udpCK/rfc6935.txt',
}
RANGES = {
    0: [(44, 52), (86, 100)],
    1: [(4580, 4625), (4700, 4716), (5045, 5062)],
    2: [(1460, 1478), (1528, 1548)],
    3: [(455, 500)],
}
WORDS = [u'MUST NOT', u'MUST', u'MAY NOT', u'MAY', u'SHOULD NOT', u'SHOULD', u'REQUIRED',
         u'must not', u'must', u'may not', u'may', u'should not', u'should',
         u'optional', u'not optional', u'never optional', u'zero checksum', u'zero-checksum',
         u'all ones', u'FFFF', u'ffff', u'65535', u'all zero', u'checksum',
         u'RFC 768', u'RFC-768', u'RFC 8200', u'RFC-8200', u'RFC 6935', u'RFC-6935',
         u'RFC 793', u'RFC-793', u'RFC 1122', u'RFC-1122']

D = {}
for i, p in sorted(P.items()):
    b = io.open(p, 'rb').read()
    t = b.decode('latin-1')
    ls = t.split(u'\n')
    rec = {
        'path': p, 'BS': len(b), 'LN': t.count(u'\n') + 1,
        'FF': t.count(u'\x0c'), 'CR': t.count(u'\r'),
        'NONBLANK': len([x for x in ls if x.strip() != u'']),
        'NONASCII': len([c for c in t if ord(c) > 127]),
        'words': dict((w, t.count(w)) for w in WORDS),
    }
    D[i] = rec
    print(u'=== %s bytes %d lines %d FF %d CR %d nonblank %d nonascii %d' % (
        p, rec['BS'], rec['LN'], rec['FF'], rec['CR'], rec['NONBLANK'], rec['NONASCII']))
    for lo, hi in RANGES[i]:
        print(u'--- range %d..%d' % (lo, hi))
        for n in range(lo, hi + 1):
            if 1 <= n <= len(ls):
                print(u'%5d|%s|' % (n, ls[n - 1]))
    hits = []
    for n, l in enumerate(ls, 1):
        if u'checksum' in l and (u'optional' in l or u'zero' in l or u'MUST' in l or u'must' in l):
            hits.append(n)
    D[i]['chk_lines'] = hits
    print(u'--- checksum+optional/zero/MUST lines: %d' % len(hits))
    for n in hits:
        print(u'%5d|%s|' % (n, ls[n - 1]))

io.open('corpus/_b70probe.json', 'wb').write(json.dumps(D, ensure_ascii=False, indent=1).encode('utf-8'))
print(u'DONE')
