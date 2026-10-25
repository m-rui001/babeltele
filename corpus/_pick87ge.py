# -*- coding: utf-8 -*-
# B87 选锚与现算: 单文本压缩(FAA GE CF34 适航指令(2026-10-22), 截止后冷门专业信息)。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

raw = io.open('corpus/raw/faa/ad_2026ge.txt', encoding='utf-8', errors='replace').read()
body = raw.partition(u'\n\n')[2]
FLAT = u' '.join(body.split())
LOW = FLAT.lower()

F = {}
F['chars'] = [len(FLAT)]
F['words'] = [len(FLAT.split())]

# AD 轴
for kw in [u'this ad', u'unsafe condition', u'prompted by', u'cf34', u'group 1', u'group 2', u'v6.50', u'v6.60', u'v5.60', u'v5.70',
           u'eec fadec', u'variable geometry', u'corrosion', u'engine degraded', u'amends', u'docket', u'cost', u'horizon air',
           u'12 months', u'replace', u'reporting requirement', u'executive order']:
    F['n_' + kw.replace(u' ', u'_')] = [LOW.count(kw)]

import re


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


FACE = pnorm(FLAT)
ATOM_CAND = [
    u'This AD requires removing certain electronic engine control (EEC) full authority digital electronic control (FADEC) software versions from service',
    u'corrosion of the variable geometry system actuator',
    u'Group 1 engines, within 12 months after the effective date of this AD, replace any EEC FADEC software version that is V6.50 or earlier',
    u'any software version that is V5.70 or later approved version',
    u'GE Model CF34-8E2, CF34-8E2A1, CF34- 8E5, CF34-8E5A1, CF34-8E5A2, CF34-8E5A2HA, CF34-8E6, and CF34-8E6A1 engines',
    u'to prevent EEC FADEC software from automatically locking the engin',
]

ATOMS = []
for a in ATOM_CAND:
    na = pnorm(a)
    if len(na) >= 3 and na in FACE:
        ATOMS.append(a)
F['atom_n'] = len(ATOMS)
F['atom_lines'] = ATOMS

io.open('corpus/_b87meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms87ge.txt', 'w', encoding='utf-8') as f:
    for a in ATOMS:
        f.write(a + u'\n')

for k, v in F.items():
    if k != 'atom_lines':
        print(k, v)
print('anchors', len(ATOMS))
