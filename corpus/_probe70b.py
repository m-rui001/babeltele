# -*- coding: utf-8 -*-
"""B70 建条前置复测: 年份行、位宽行、进制读数在四面上的分布、引用写法族、共用长行的写法差异。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
P = [u'corpus/raw/udpCK/rfc768.txt', u'corpus/raw/tcpRTO/rfc1122.txt',
     u'corpus/raw/udpCK/rfc8200.txt', u'corpus/raw/udpCK/rfc6935.txt']
T = [io.open(p, 'rb').read().decode('utf-8', 'replace') for p in P]
L = [t.split(NL) for t in T]
LBL = [u'768', u'1122', u'8200', u'6935']
FO = [u' '.join(t.split()) for t in T]


def ra(hay, tok, pat):
    i = hay.find(tok)
    if i < 0:
        return None
    m = re.compile(pat).search(hay, i + len(tok))
    return None if not m else m.group(1)


print(u'== 位宽行 768')
for n, x in enumerate(L[0], 1):
    if u'Checksum is the' in x or u'16-bit' in x:
        print(n, repr(x))
print(u'== 年份行(前 60 行)')
MON = u'January|February|March|April|May|June|July|August|September|October|November|December'
for i in range(4):
    hits = [(n, x) for n, x in enumerate(L[i][:60], 1) if re.search(u'(%s) +\\d{4}\\s*$' % MON, x)]
    print(LBL[i], hits[:4])
print(u'== 游标读数')
for i in range(4):
    print(LBL[i], u'all1s=', ra(FO[i], u"all 1's (", u'(\\d+)\\)'),
          u'hex=', ra(FO[i], u'changed to hex ', u'([0-9A-F]{4})'),
          u'bit128=', ra(FO[i], u'include the ', u'(\\d+)-bit IPv6'),
          u'bit32=', ra(FO[i], u'instead of ', u'(\\d+)-bit IPv4'),
          u'req9=', ra(FO[i], u'MUST follow requirements ', u'(\\d+)'),
          u'reqhi=', ra(FO[i], u'MUST follow requirements 9, 10, and ', u'(\\d+)'))
print(u'== 768 面上的 65535 / FFFF / all ones')
for i in range(4):
    print(LBL[i], u'65535=', FO[i].count(u'65535'), u'FFFF=', FO[i].count(u'FFFF'),
          u'ffff=', FO[i].count(u'ffff'), u"all 1's=", FO[i].count(u"all 1's"),
          u'hex=', FO[i].count(u'hex '))
print(u'== 引用写法')
for n in (u'768', u'1122', u'8200', u'6935', u'2460', u'6936'):
    row = []
    for i in range(4):
        sp = T[i].count(u'RFC ' + n)
        hy = T[i].count(u'RFC-' + n)
        tk = T[i].count(u'RFC' + n) - sp - hy
        rx = len(re.findall(u'RFC[ -]?' + n, T[i]))
        row.append((LBL[i], sp, hy, tk, sp + hy + tk, rx))
    print(n, row)
print(u'== not optional / never optional / by default 折平⇎逐行')
for i in range(4):
    print(LBL[i], u'notopt_fold=', FO[i].count(u'not optional'),
          u'notopt_line=', len([x for x in L[i] if u'not optional' in x]),
          u'never=', FO[i].count(u'never optional'),
          u'bydefault=', FO[i].lower().count(u'by default'),
          u'optional=', T[i].count(u'optional'))
print(u'== 义务词大小写(全篇)')
for i in range(4):
    def ub(s, w):
        return len(re.findall(u'(?<![A-Za-z])' + w + u'(?![A-Za-z])', s))
    print(LBL[i], [(w, ub(T[i], w), ub(T[i].lower(), w.lower())) for w in (u'MUST', u'MAY', u'SHOULD')])
print(u'== 摘壳后共用长行的写法差异(前 6 例)')


def sh(i):
    out = []
    for x in L[i]:
        s = x.strip()
        if s == u'' or u'\x0c' in s:
            continue
        if re.match(u'^\\s*(\\[Page \\d+\\]|\\[?Page \\d+\\]?|RFC\\s?\\d+\\s+\\S{2,}.*\\s\\d{4}\\s*|[A-Za-z0-9]+\\s+\\S{2,}.*\\s[A-Z][a-z]+ \\d{4}\\s*|Internet Engineering Task Force\\s+.*\\d{4}\\s*)\\s*$', x):
            continue
        out.append(x)
    return out


SH = [sh(i) for i in range(4)]
NS = [set(u' '.join(x.lower().split()) for x in s if len(u' '.join(x.lower().split())) >= 40) for s in SH]
c = 0
for i in range(4):
    for j in range(i + 1, 4):
        inter = NS[i] & NS[j]
        for a in sorted(inter):
            xs = [x for x in SH[i] if u' '.join(x.lower().split()) == a] + \
                 [x for x in SH[j] if u' '.join(x.lower().split()) == a]
            if len(set(xs)) > 1 and c < 8:
                c += 1
                print(u'%s⇎%s' % (LBL[i], LBL[j]), [repr(y) for y in xs])
print(u'字节同形对数 / 归一同形对数: ', end=u'\n')
for i in range(4):
    for j in range(i + 1, 4):
        inter = NS[i] & NS[j]
        bo = 0
        for a in inter:
            ai = set(x for x in SH[i] if u' '.join(x.lower().split()) == a)
            aj = set(x for x in SH[j] if u' '.join(x.lower().split()) == a)
            bo += len(ai & aj)
        print(u'%s-%s' % (LBL[i], LBL[j]), len(inter), bo)
