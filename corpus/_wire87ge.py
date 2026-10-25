# -*- coding: utf-8 -*-
# 幂等接线 B87: SRC/ATOM/_b87_scan/DERIV(11 键)/B87V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B87']" in s:
    print('B87 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B87'] = ['corpus/raw/faa/ad_2026ge.txt']
ATOM.add('B87')

def _b87_scan():
    body = io.open(SRC['B87'][0], encoding='utf-8', errors='replace').read().partition(u'\n\n')[2]
    flat = u' '.join(body.split())
    low = flat.lower()
    F = {}
    F['chars'] = [len(flat)]
    F['words'] = [len(flat.split())]
    for kw in [u'this ad', u'unsafe condition', u'prompted by', u'cf34', u'group 1', u'group 2', u'v6.50', u'v6.60', u'v5.60', u'v5.70', u'eec fadec', u'variable geometry', u'corrosion', u'engine degraded', u'amends', u'docket', u'cost', u'horizon air', u'12 months', u'replace', u'reporting requirement', u'executive order']:
        F['n_' + kw.replace(u' ', u'_')] = [low.count(kw)]
    return F


_B87 = _b87_scan()
B87V = lambda k, i=None: (_B87[k][0] if i is None else _B87[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + chr(10) + CUT)
REG = json.load(io.open('corpus/_b87flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B87'] = " + json.dumps(REG, ensure_ascii=False) + chr(10)*2 + CUT)
s = s.replace('               B85V=B85V)', '               B85V=B85V,' + chr(10) + '               B87V=B87V)')
assert 'B87V=B87V' in s
io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)
print('wire87 完成: %d 键' % len(REG))
