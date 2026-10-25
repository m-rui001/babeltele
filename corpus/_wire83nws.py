# -*- coding: utf-8 -*-
# 幂等接线 B83: SRC/ATOM/_b83_scan/DERIV(13 键)/B83V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B83']" in s:
    print('B83 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B83'] = ['corpus/raw/nws/afd_a.txt', 'corpus/raw/nws/afd_b.txt', 'corpus/raw/nws/afd_c.txt']
ATOM.add('B83')

def _b83_scan():
    PB = SRC['B83']
    LOW, SENT = [], []
    for p in PB:
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
    three('key_messages', cnt(u'key messages'))
    three('amp', cnt(u'&&'))
    three('aviation', cnt(u'aviation'))
    three('nws', cnt(u'national weather service'))
    three('afd_hdr', cnt(u'area forecast discussion'))
    three('fire', cnt(u'fire'))
    three('confidence', cnt(u'confidence'))
    three('uncertain', cnt(u'uncertaint'))
    three('short_term', cnt(u'short term'))
    three('advisory', cnt(u'advisory'))
    three('front', cnt(u'front'))
    three('ensemble', cnt(u'ensemble'))
    three('model', cnt(u'model'))
    three('marine', cnt(u'marine'))
    three('gulf', cnt(u'gulf'))
    three('coast', cnt(u'coast'))
    three('possible', cnt(u'possible'))
    three('likely', cnt(u'likely'))
    three('rain', cnt(u'rain'))
    three('snow', cnt(u'snow'))
    three('ridge', cnt(u'ridge'))
    return F


_B83 = _b83_scan()
B83V = lambda k, i=None: (_B83[k] if i is None else _B83[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + chr(10) + CUT)
REG = json.load(io.open('corpus/_b83flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B83'] = " + json.dumps(REG, ensure_ascii=False) + chr(10)*2 + CUT)
s = s.replace('               B82V=B82V)', '               B82V=B82V,' + chr(10) + '               B83V=B83V)')
assert 'B83V=B83V' in s
io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)
print('wire83 完成: %d 键' % len(REG))
