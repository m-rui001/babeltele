# -*- coding: utf-8 -*-
# 幂等接线 B76: SRC/ATOM/_b76_scan/DERIV(19 键)/B76V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B76']" in s:
    print('B76 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B76'] = ['corpus/raw/fomc/fomc25sep_a.txt', 'corpus/raw/fomc/fomc25sep_b.txt',
              'corpus/raw/fomc/fomc25sep_c.txt']
ATOM.add('B76')


def _b76_scan():
    """B76 同一次 FOMC 会议三体裁。审计器侧第二套: lower 游标句切与词面计数。"""
    P6 = SRC['B76']
    LOW, SENT = [], []
    for p in P6:
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
    three('powell', cnt(u'powell'))
    three('participants', cnt(u'participant'))
    three('median', cnt(u'median'))
    three('voted', cnt(u'vot'))
    three('miran', cnt(u'miran'))
    three('uncertain', cnt(u'uncertaint'))
    three('balance_risks', cnt(u'balance of risks'))
    three('projection', cnt(u'projection'))
    three('october', cnt(u'october'))
    return F


_B76 = _b76_scan()
B76V = lambda k, i=None: (_B76[k] if i is None else _B76[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + '\n' + CUT)
REG = json.load(io.open('corpus/_b76flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B76'] = " + json.dumps(REG, ensure_ascii=False) + '\n\n' + CUT)
s = s.replace('               B75V=B75V)', '               B75V=B75V,' + '\n' + '               B76V=B76V)')
assert 'B76V=B76V' in s
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('wire76 完成: %d 键' % len(REG))
