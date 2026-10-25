# -*- coding: utf-8 -*-
import io, re, os
ROOT = os.path.dirname(os.path.abspath(__file__))
SLUGS = ['math_subsets', 'med_gitalb', 'law_ewca_method', 'fin_credit_cmte',
         'ind_creep_rupture', 'str_quake_slab']

def reg(slug):
    T = io.open(os.path.join(ROOT, 'raw', 'cot', slug + '.md'), encoding='utf-8').read()
    pr = re.search(u'## \\[\\[PROMPT\\]\\]\\n(.*?)\\n\\n## \\[\\[REASONING\\]\\]\\n(.*?)\\n\\n## \\[\\[ANSWER\\]\\]\\n?(.*)$', T, re.S)
    return pr.group(2).rstrip(u'\n')

PATS = [u'Wait', u'wait,', u'Hmm', u'Actually', u'No,', u'restart', u'Let me re', u'wrong', u'error',
        u'must', u'MUST', u'caveat', u'In conclusion', u'Conclusion', u'uncertain', u'I am not sure',
        u'CFR', u'§', u'Article', u'lex loci', u'API ', u'ASCE', u'assume', u'Assuming', u'study']
for s in SLUGS:
    R = reg(s)
    print(u'##### %s (%d)' % (s, len(R)))
    for p in PATS:
        idx = [m.start() for m in re.finditer(re.escape(p), R)]
        if not idx:
            print(u'  [%s] 0')
            continue
        print(u'  [%s] %d' % (p, len(idx)))
        for k in idx[:2]:
            print(u'      ...%s...' % R[max(0, k - 90):k + 130].replace(u'\n', u' | '))
