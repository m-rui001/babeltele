# -*- coding: utf-8 -*-
import io, re, os, hashlib
ROOT = os.path.dirname(os.path.abspath(__file__))
SLUGS = ['math_subsets', 'med_gitalb', 'law_ewca_method', 'fin_credit_cmte',
         'ind_creep_rupture', 'str_quake_slab']

def regions(slug):
    T = io.open(os.path.join(ROOT, 'raw', 'cot', slug + '.md'), encoding='utf-8').read()
    pr = re.search(u'## \\[\\[PROMPT\\]\\]\\n(.*?)\\n\\n## \\[\\[REASONING\\]\\]\\n(.*?)\\n\\n## \\[\\[ANSWER\\]\\]\\n?(.*)$', T, re.S)
    return pr.group(1), pr.group(2).rstrip(u'\n'), pr.group(3).strip()

OUT = []
for s in SLUGS:
    pf, rf, af = regions(s)
    OUT.append(u'===== %s  reasoning %d chars, %d lines =====' % (s, len(rf), rf.count(u'\n') + 1))
    OUT.append(u'--- HEAD 2200 ---')
    OUT.append(rf[:2200])
    OUT.append(u'--- TAIL 2200 ---')
    OUT.append(rf[-2200:])
io.open(os.path.join(ROOT, '_d50.txt'), 'w', encoding='utf-8').write(u'\n'.join(OUT) + u'\n')
print('written', sum(len(x) for x in OUT))
