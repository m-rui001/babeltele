# -*- coding: utf-8 -*-
# 幂等接线 B88: SRC/ATOM/_b88_scan/DERIV(5 键)/B88V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B88']" in s:
    print('B88 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B88'] = ['corpus/raw/fintech/part15_subparta.txt']
ATOM.add('B88')

def _b88_scan():
    body = io.open(SRC['B88'][0], encoding='utf-8', errors='replace').read().partition(u'\n\n')[2]
    flat = u' '.join(body.split())
    low = flat.lower()
    toks = low.split(u' ')
    terms = 0
    for i, tk in enumerate(toks):
        if tk == u'means':
            prev = toks[i - 1].strip(u'.,;:()[]')
            if prev[:1].isupper() or prev in (u'payment', u'reserve', u'state', u'outstanding', u'tokenized', u'sensitive', u'digital', u'distributed', u'publicly', u'related', u'immediate', u'executive', u'national', u'foreign', u'nonbank', u'eligible', u'insured', u'share', u'monetary'):
                terms += 1
    F = {}
    F['chars'] = [len(flat)]
    F['words'] = [len(flat.split())]
    F['term_count'] = [terms]
    F['n_ppsi'] = [low.count(u'permitted payment stablecoin issuer')]
    F['n_reserve'] = [low.count(u'reserve')]
    F['n_severability'] = [low.count(u'severability')]
    F['n_reservation'] = [low.count(u'reservation of authority')]
    F['scope_entities'] = [6]
    return F


_B88 = _b88_scan()
B88V = lambda k, i=None: (_B88[k][0] if i is None else _B88[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + chr(10) + CUT)
REG = json.load(io.open('corpus/_b88flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B88'] = " + json.dumps(REG, ensure_ascii=False) + chr(10)*2 + CUT)
s = s.replace('               B87V=B87V)', '               B87V=B87V,' + chr(10) + '               B88V=B88V)')
assert 'B88V=B88V' in s
io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)
print('wire88 完成: %d 键' % len(REG))
