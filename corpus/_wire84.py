# -*- coding: utf-8 -*-
# 幂等接线 B84: SRC/ATOM/_b84_scan/DERIV(14 键)/B84V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B84']" in s:
    print('B84 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B84'] = ['corpus/raw/constitution/us_constitution_full.txt']
ATOM.add('B84')

def _b84_scan():
    body = io.open(SRC['B84'][0], encoding='utf-8', errors='replace').read().partition(u'\n\n')[2]
    flat = u' '.join(body.split())
    low = flat.lower()
    toks = low.split(u' ')
    def roman_hdr_count(word):
        n = 0
        for i, tk in enumerate(toks):
            if tk == word and i + 1 < len(toks):
                nxt = toks[i + 1].strip(u'.,;:()[]')
                if nxt and all(ch in u'ivxlcdm' for ch in nxt):
                    n += 1
        return n
    i0 = low.find(u'we the people')
    i1 = low.find(u'article', i0)
    F = {}
    F['chars'] = [len(flat)]
    F['words'] = [len(flat.split())]
    F['amend_hdr'] = [roman_hdr_count(u'amendment')]
    F['article_hdr'] = [roman_hdr_count(u'article')]
    F['preamble_words'] = [len(low[i0:i1].split())]
    for kw in [u'congress', u'president', u'senate', u'section', u'repeal', u'court', u'state']:
        F[kw if kw != u'section' else u'section_word'] = [low.count(kw)]
    for kw in [u'two thirds', u'thirty', u'seven years', u'twenty five', u'fourteen years', u'ten days', u'nine states', u'fourteen', u'thirds']:
        F['kw_' + kw.replace(u' ', u'_')] = [low.count(kw)]
    return F


_B84 = _b84_scan()
B84V = lambda k, i=None: (_B84[k][0] if i is None else _B84[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + chr(10) + CUT)
REG = json.load(io.open('corpus/_b84flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B84'] = " + json.dumps(REG, ensure_ascii=False) + chr(10)*2 + CUT)
s = s.replace('               B83V=B83V)', '               B83V=B83V,' + chr(10) + '               B84V=B84V)')
assert 'B84V=B84V' in s
io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)
print('wire84 完成: %d 键' % len(REG))
