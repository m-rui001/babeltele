# -*- coding: utf-8 -*-
# 幂等接线 B79: SRC/ATOM/_b79_scan/DERIV(10 键)/B79V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B79']" in s:
    print('B79 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B79'] = ['corpus/raw/changelog/sqlite_a.txt', 'corpus/raw/changelog/sqlite_b.txt', 'corpus/raw/changelog/sqlite_c.txt']
ATOM.add('B79')

def _b79_scan():
    P9 = SRC['B79']
    LOW, SENT = [], []
    for p in P9:
        body = io.open(p, encoding='utf-8', errors='replace').read().partition(u'\n\n')[2]
        t = u' '.join(body.split()).lower()
        LOW.append(t)
        cur, sents = u'', []
        for ch in t:
            cur += ch
            if ch in u'.!?':
                if len(cur.strip()) > 40:
                    sents.append(cur.strip())
                cur = u''
        if len(cur.strip()) > 40:
            sents.append(cur.strip())
        SENT.append(sents)
    F = {}

    def three(name, vals):
        F[name] = list(vals)

    def cnt(kw):
        return [t.count(kw) for t in LOW]

    three('chars', [len(t) for t in LOW])
    three('sents', [len(s) for s in SENT])
    three('avg_sent', [F['chars'][i] // max(F['sents'][i], 1) for i in range(3)])
    for (i, j), nm in zip([(0, 1), (0, 2), (1, 2)], ['sh_ab', 'sh_ac', 'sh_bc']):
        F[nm] = len(set(SENT[i]) & set(SENT[j]))
    three('fix', cnt(u'fix'))
    three('add', cnt(u'add'))
    three('improve', cnt(u'improve'))
    three('optimize', [t.count(u'optimiz') for t in LOW])
    three('ref_540', cnt(u'3.54.0'))
    three('ais', cnt(u'from ais'))
    three('heap', cnt(u'heap-buffer'))
    three('bit32', cnt(u'32-bit'))
    three('reported_users', cnt(u'reported by users'))
    three('lineage', cnt(u'3.53.3'))
    three('source_id', cnt(u'sqlite_source_id'))
    three('hashes', cnt(u'sha3'))
    three('broken1', cnt(u'is now be'))
    three('broken2', cnt(u'the replaces'))
    return F


_B79 = _b79_scan()
B79V = lambda k, i=None: (_B79[k] if i is None else _B79[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + chr(10) + CUT)
REG = json.load(io.open('corpus/_b79flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B79'] = " + json.dumps(REG, ensure_ascii=False) + chr(10)*2 + CUT)
s = s.replace('               B78V=B78V)', '               B78V=B78V,' + chr(10) + '               B79V=B79V)')
assert 'B79V=B79V' in s
io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)
print('wire79 完成: %d 键' % len(REG))
