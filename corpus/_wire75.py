# -*- coding: utf-8 -*-
# 幂等接线 B75: SRC/ATOM/_b75_scan/DERIV(37 键)/B75V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B75']" in s:
    print('B75 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B75'] = ['corpus/raw/opinions/loper_a.txt', 'corpus/raw/opinions/loper_b.txt',
              'corpus/raw/opinions/loper_c.txt', 'corpus/raw/opinions/loper_d.txt']
ATOM.add('B75')


def _b75_scan():
    """B75 同一判决书四声音(Loper Bright)。审计器侧第二套: lower 游标句切与词面计数。"""
    P5 = SRC['B75']
    LOW, SENT = [], []
    for p in P5:
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

    def four(name, vals):
        F[name] = list(vals)

    def cnt(kw):
        return [t.count(kw) for t in LOW]

    four('chars', [len(t) for t in LOW])
    four('sents', [len(s) for s in SENT])
    four('avg_sent', [F['chars'][i] // max(F['sents'][i], 1) for i in range(4)])
    for (i, j), nm in zip([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
                          ['sh_ab', 'sh_ac', 'sh_ad', 'sh_bc', 'sh_bd', 'sh_cd']):
        F[nm] = len(set(SENT[i]) & set(SENT[j]))
    four('the_dissent', cnt(u'the dissent'))
    four('the_majority', cnt(u'the majority'))
    four('the_court_low', cnt(u'the court'))
    four('justice_gorsuch', cnt(u'justice gorsuch'))
    four('justice_kagan', cnt(u'justice kagan'))
    four('chevron', cnt(u'chevron'))
    four('stare', cnt(u'stare decisis'))
    four('defer', [t.count(u'defer') for t in LOW])
    four('congress', cnt(u'congress'))
    four('agency', cnt(u'agency'))
    four('apa', [t.count(u'apa') for t in LOW])
    four('uncertain', cnt(u'uncertaint'))
    four('policy', cnt(u'policy'))
    four('constitution', cnt(u'constitution'))
    four('precedent', cnt(u'precedent'))
    four('overruled', [t.count(u'overrul') for t in LOW])
    four('forty', [t.count(u'forty') + t.count(u'40') for t in LOW])
    four('best_reading', cnt(u'best reading'))
    four('ambigu', cnt(u'ambigu'))
    return F


_B75 = _b75_scan()
B75V = lambda k, i=None: (_B75[k] if i is None else _B75[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + '\n' + CUT)
REG = json.load(io.open('corpus/_b75flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B75'] = " + json.dumps(REG, ensure_ascii=False) + '\n\n' + CUT)
s = s.replace('               B73V=B73V)', '               B73V=B73V,' + '\n' + '               B75V=B75V)')
assert 'B75V=B75V' in s
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('wire75 完成: %d 键' % len(REG))
