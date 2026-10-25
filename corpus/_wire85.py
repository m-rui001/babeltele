# -*- coding: utf-8 -*-
# 幂等接线 B85: SRC/ATOM/_b85_scan/DERIV(6 键)/B85V 进 audit.py。已在位则跳过。
import io, json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['B85']" in s:
    print('B85 已接线, 跳过')
    raise SystemExit

BLOCK = u'''
SRC['B85'] = ['corpus/raw/changelog/sqlite_b.txt']
ATOM.add('B85')

def _b85_scan():
    body = io.open(SRC['B85'][0], encoding='utf-8', errors='replace').read().partition(u'\n\n')[2]
    flat = u' '.join(body.split())
    low = flat.lower()
    F = {}
    F['chars'] = [len(flat)]
    F['words'] = [len(flat.split())]
    for kw in [u'cli ', u'query planner', u'alter table', u'diskused', u'date/time', u'windows', u'authorizer', u'sqlite3_', u'add ', u'enhance', u'improve', u'fixes']:
        F['n_' + kw.strip().replace(u' ', u'_')] = [low.count(kw)]
    for kw in [u'3.54.0', u'3.51.0', u'4% faster', u'7.5%', u'2026-10-09', u'sqlite_source_id', u'sha3-256', u'no_color', u'o_tmpfile', u'windows vista', u'srwl', u'rowid', u'_rowid_', u'oid']:
        F['n_' + kw.replace(u'%', u'pct').replace(u'.', u'_').replace(u' ', u'_')] = [low.count(kw)]
    return F


_B85 = _b85_scan()
B85V = lambda k, i=None: (_B85[k][0] if i is None else _B85[k][i])
'''

CUT = 'rows, fails, proofs, soft_all = [], [], [], []'
assert s.count(CUT) == 1
s = s.replace(CUT, BLOCK + chr(10) + CUT)
REG = json.load(io.open('corpus/_b85flat.json', encoding='utf-8'))
s = s.replace(CUT, u"DERIV['B85'] = " + json.dumps(REG, ensure_ascii=False) + chr(10)*2 + CUT)
s = s.replace('               B84V=B84V)', '               B84V=B84V,' + chr(10) + '               B85V=B85V)')
assert 'B85V=B85V' in s
io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)
print('wire85 完成: %d 键' % len(REG))
