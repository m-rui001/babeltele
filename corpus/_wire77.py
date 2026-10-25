# -*- coding: utf-8 -*-
# 幂等接线 B77: SRC/ATOM/_b77_scan/DERIV(16 键)/B77V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B77']" in s:
    print('B77 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B77'] = ['corpus/raw/arxiv/llama3_a.txt', 'corpus/raw/arxiv/llama3_b.txt', 'corpus/raw/arxiv/llama3_c.txt']
ATOM.add('B77')

def _b77_scan():
    P7 = SRC['B77']
    LOW, SENT = [], []
    for p in P7:
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
    three('sent_uniq', [len(set(s)) for s in SENT])
    three('date_v1', cnt(u'31 jul 2024'))
    three('date_v2', cnt(u'15 aug 2024'))
    three('date_v3', cnt(u'23 nov 2024'))
    three('jardanhan', cnt(u'jardanhan'))
    three('janardhan', cnt(u'janardhan'))
    three('tbl4_old', cnt(u'16 16 4 131,072'))
    three('tbl4_new', cnt(u'16 16 8 131,072'))
    three('core_aaron', cnt(u'core contributors aaron'))
    three('llama3', cnt(u'llama 3 '))
    three('b405', [t.count(u'405') for t in LOW])
    three('safety', cnt(u'safety'))
    three('transformer', cnt(u'transformer'))
    three('herd', cnt(u'herd of models'))
    return F


_B77 = _b77_scan()
B77V = lambda k, i=None: (_B77[k] if i is None else _B77[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + chr(10) + CUT)
REG = json.load(io.open('corpus/_b77flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B77'] = " + json.dumps(REG, ensure_ascii=False) + chr(10)*2 + CUT)
s = s.replace('               B74V=B74V)', '               B74V=B74V,' + chr(10) + '               B77V=B77V)')
assert 'B77V=B77V' in s
io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)
print('wire77 完成: %d 键' % len(REG))
