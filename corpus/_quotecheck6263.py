# -*- coding: utf-8 -*-
"""README 新增行里的英文引号逐字回原文核验(去标签口径)。"""
import io
import re

NL = chr(10)
P = [u'corpus/raw/tcpiw/rfc2581.txt', u'corpus/raw/tcpiw/rfc3390.txt', u'corpus/raw/tcpiw/rfc5681.txt',
     u'corpus/raw/tcpiw/rfc6928.txt', u'corpus/raw/tcpiw/rfc9002.txt']
Q = [u'corpus/raw/tcpRTO/rfc1122.txt', u'corpus/raw/tcpRTO/rfc2988.txt', u'corpus/raw/tcpRTO/rfc6298.txt',
     u'corpus/raw/tcpiw/rfc9002.txt']


def cnorm(s):
    o = []
    for c in s.lower():
        if (u'a' <= c <= u'z') or (u'0' <= c <= u'9'):
            o.append(c)
        elif c in u' \t\n\r\x0b\x0c':
            o.append(u' ')
    return re.sub(u' +', u' ', u''.join(o))


SRC = {u'62': [cnorm(io.open(p, encoding=u'utf-8-sig').read()) for p in P],
       u'63': [cnorm(io.open(p, encoding=u'utf-8-sig').read()) for p in Q]}
L = io.open(u'corpus/README.md', encoding=u'utf-8').read().split(NL)
lines = [i + 1 for i, x in enumerate(L)
         if x.startswith(u'**B62 ') or x.startswith(u'**B63 ') or x.startswith(u'| B62 ') or x.startswith(u'| B63 ')]
tot = 0
bad = []
for ln in lines:
    for q in re.findall(u'“([^”]{4,})”', L[ln - 1]):
        qq = cnorm(q).strip()
        if not re.search(u'[a-z]{3}', qq):
            continue
        tot += 1
        if not any(qq in s for n in (u'62', u'63') for s in SRC[n]):
            bad.append((ln, q))
print(u'扫行 %s ｜ 引号 %d 枚 ｜ 逐字未命中 %d' % (lines, tot, len(bad)))
for b in bad:
    print(b)
