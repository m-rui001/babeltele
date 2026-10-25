# -*- coding: utf-8 -*-
# 幂等接线 B78: SRC/ATOM/_b78_scan/DERIV(25 键)/B78V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B78']" in s:
    print('B78 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B78'] = ['corpus/raw/faa/ad_a.txt', 'corpus/raw/faa/ad_b.txt']
ATOM.add('B78')

def _b78_scan():
    P8 = SRC['B78']
    LOW, SENT = [], []
    for p in P8:
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

    def two(name, vals):
        F[name] = list(vals)

    def cnt(kw):
        return [t.count(kw) for t in LOW]

    two('chars', [len(t) for t in LOW])
    two('sents', [len(s) for s in SENT])
    two('avg_sent', [F['chars'][i] // max(F['sents'][i], 1) for i in range(2)])
    F['sh_ab'] = len(set(SENT[0]) & set(SENT[1]))
    two('sent_uniq', [len(set(SENT[i])) for i in range(2)])
    two('easa', cnt(u'easa'))
    two('unsafe', cnt(u'unsafe condition'))
    two('prompted', cnt(u'prompted by'))
    two('mcai', cnt(u'mcai'))
    two('modification', [t.count(u'modif') for t in LOW])
    two('inspect', [t.count(u'inspect') for t in LOW])
    two('comments', cnt(u'comment'))
    two('docket', cnt(u'docket'))
    two('cost', cnt(u'cost'))
    two('fires', cnt(u'fire'))
    two('2022_0185', cnt(u'2022-0185'))
    two('fr5817', cnt(u'88 fr 5817'))
    two('other_ad', cnt(u'2023-01702'))
    return F


_B78 = _b78_scan()
B78V = lambda k, i=None: (_B78[k] if i is None else _B78[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + chr(10) + CUT)
REG = json.load(io.open('corpus/_b78flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B78'] = " + json.dumps(REG, ensure_ascii=False) + chr(10)*2 + CUT)
s = s.replace('               B77V=B77V)', '               B77V=B77V,' + chr(10) + '               B78V=B78V)')
assert 'B78V=B78V' in s
io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)
print('wire78 完成: %d 键' % len(REG))
