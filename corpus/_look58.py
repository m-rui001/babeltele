# -*- coding: utf-8 -*-
"""看四份文书里方程段/权重表/档位表/算例块的去标签原文, 供 _pick58.py 定正则用。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
RAW = u'corpus/raw/cvss/'
P = [RAW + u'cvss_v30_spec.html', RAW + u'cvss_v31_spec.html',
     RAW + u'cvss_v40_spec.html', RAW + u'cvss_examples.html']


ENT = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'),
       (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-')]
UNI = [(u'\u00a0', u' '), (u'\u2212', u'-'), (u'\u2013', u'-'), (u'\u2014', u'-'),
       (u'\u00d7', u'x')]


def strip(s, br=u' '):
    s = re.sub(u'(?s)<!--.*?-->', u'', s)
    s = re.sub(u'(?is)<br[^>]*>', br, s)
    s = re.sub(u'(?s)<[^>]+>', u'', s)          # 先剥标签
    for a, b in ENT + UNI:
        s = s.replace(a, b)                     # 后解实体, 否则 &lt; 会被当成标签开括号
    return re.sub(u'[ \t]+', u' ', s).strip()


def uni_only(s):
    for a, b in UNI:
        s = s.replace(a, b)
    return s


def rows(html):
    return [[strip(x) for x in re.findall(u'(?is)<t[dh][^>]*>(.*?)</t[dh]>', tr)]
            for tr in re.findall(u'(?is)<tr[^>]*>(.*?)</tr>', html)]


T = [io.open(p, encoding='utf-8', errors='replace').read() for p in P]
which = sys.argv[1] if len(sys.argv) > 1 else u'eq'


def num(j, d):
    try:
        return int(sys.argv[j])
    except Exception:
        return d


lo = num(2, 0)
hi = num(3, 10 ** 9)

if which == u'seg':
    i = num(2, 0)
    head = sys.argv[3] if len(sys.argv) > 3 else u'Environmental'
    n = num(4, 2600)
    k = T[i].find(head)
    print(u'=== %s at %d ===' % (P[i], k))
    for ln in strip(T[i][k:k + n], br=u' | ').split('\n'):
        print(u'|' + ln[:240])
elif which == u'eq':
    for i, head in ((0, u'CVSS v3.0 Equations'), (1, u'CVSS v3.1 equations')):
        k = T[i].find(head)
        print(u'=== %s at %d ===' % (P[i], k))
        body = strip(T[i][k:k + 7000], br=u' | ')
        for ln in body.split('\n'):
            print(u'|' + ln[:240])
elif which == u'wt':
    for i in (int(sys.argv[2]) if len(sys.argv) > 2 else 0,):
        print(u'=== weights %s ===' % P[i])
        for raw_tr in re.findall(u'(?is)<tr[^>]*>(.*?)</tr>', T[i]):
            rawc = re.findall(u'(?is)<t[dh][^>]*>(.*?)</t[dh]>', raw_tr)
            cells = [strip(x) for x in rawc]
            if len(cells) == 3:
                print(u'[%s] |[|] %s |[|] %s' % (
                    cells[0][:56],
                    strip(rawc[1], br=u' |[|] ')[:78],
                    strip(rawc[2], br=u' |[|] ')[:104]))
elif which == u'band':
    for i in range(4):
        print(u'=== %s ===' % P[i])
        for cells in rows(T[i]):
            if cells and cells[0] in (u'None', u'Low', u'Medium', u'High', u'Critical',
                                      u'Negligible', u'Severity'):
                print(u'  %s' % u' | '.join(cells)[:150])
elif which == u'v40':
    k = T[2].find(u'EQ1')
    print(strip(T[2][max(0, k - 2500):k + 6000], br=u' | ')[:9000])
elif which == u'ex':
    blocks = list(re.finditer(u'(?is)<h[34] id="(CVE-\\d{4}-\\d+)".*?(?=<h[34] id="CVE|$)', T[3]))
    print(u'blocks %d' % len(blocks))
    for m in blocks[lo:hi]:
        print(u'=== %s ===' % m.group(1))
        for cells in rows(m.group(0)):
            print(u'  %d: %s' % (len(cells), u' ## '.join(cells)[:200]))
