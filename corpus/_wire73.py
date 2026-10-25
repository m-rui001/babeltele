# -*- coding: utf-8 -*-
# 幂等接线 B73: SRC/ATOM/_b73_scan/DERIV(43 键)/B73V 进 audit.py。已在位则跳过。
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B73']" in s:
    print('B73 已接线, 跳过')
    raise SystemExit

BLOCK = u'''SRC['B73'] = ['corpus/raw/filings/aapl25_10k_1a.txt', 'corpus/raw/filings/aapl24_10k_1a.txt',
              'corpus/raw/filings/msft25_10k_1a.txt', 'corpus/raw/filings/goog25_10k_1a.txt']
ATOM.add('B73')


def _b73_scan():
    """B73 四份 10-K Item 1A。审计器侧第二套: 句切分与词面计数, 与采集侧互为旁证。"""
    P3 = SRC['B73']
    LOW, SENT = [], []
    for p in P3:
        body = io.open(p, encoding='utf-8', errors='replace').read().partition(u'\n\n')[2]
        body = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), body)
        for a, b in (('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"')):
            body = body.replace(a, b)
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
    four('sh_ab_pct', [round(100.0 * F['sh_ab'] / F['sents'][0], 1)] * 4)
    four('could_harm', cnt(u'could harm'))
    four('the_company', cnt(u'the company'))
    four('we_word', [t.count(u' we ') for t in LOW])
    four('if_we', [t.count(u'if we') for t in LOW])
    four('tariff', cnt(u'tariff'))
    four('ai', cnt(u'artificial intelligence'))
    four('appstore', cnt(u'app store'))
    four('stockprice', cnt(u'stock price'))
    four('china', cnt(u'china'))
    four('supply', cnt(u'supply chain'))
    four('cyber', cnt(u'cyberattack'))
    four('privacy', cnt(u'data privacy'))
    four('litigation', cnt(u'litigation'))
    four('competition', cnt(u'competition'))
    four('intprop', cnt(u'intellectual property'))
    four('regulat', cnt(u'regulat'))
    return F


_B73 = _b73_scan()
B73V = lambda k, i=None: (_B73[k] if i is None else _B73[k][i])
'''
CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + chr(10) + CUT)
REG = json.load(io.open('corpus/_b73flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B73'] = " + json.dumps(REG, ensure_ascii=False) + chr(10) + chr(10) + CUT)
s = s.replace('               B72V=B72V)', '               B72V=B72V,' + chr(10) + '               B73V=B73V)')
assert 'B73V=B73V' in s
io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)
print('wire73 完成: %d 键' % len(REG))
