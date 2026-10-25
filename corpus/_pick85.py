# -*- coding: utf-8 -*-
# B85 选锚与现算: 单文本压缩(SQLite 3.54.0 发布说明, 截止后冷门专业信息)。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

raw = io.open('corpus/raw/changelog/sqlite_b.txt', encoding='utf-8', errors='replace').read()
body = raw.partition(u'\n\n')[2]
FLAT = u' '.join(body.split())
LOW = FLAT.lower()

F = {}
F['chars'] = [len(FLAT)]
F['words'] = [len(FLAT.split())]

# 类目计数(条目组的引导词)
for kw in [u'cli ', u'query planner', u'alter table', u'diskused', u'date/time', u'windows', u'authorizer',
           u'sqlite3_', u'add ', u'enhance', u'improve', u'fixes']:
    F['n_' + kw.strip().replace(u' ', u'_')] = [LOW.count(kw)]

# 版本/性能/哈希
for kw in [u'3.54.0', u'3.51.0', u'4% faster', u'7.5%', u'2026-10-09', u'sqlite_source_id', u'sha3-256',
           u'no_color', u'o_tmpfile', u'windows vista', u'srwl', u'rowid', u'_rowid_', u'oid']:
    F['n_' + kw.replace(u'%', u'pct').replace(u'.', u'_').replace(u' ', u'_')] = [LOW.count(kw)]

import re


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


FACE = pnorm(FLAT)
ATOM_CAND = [
    u'Use the new diskused() extension to implement the ".diskused" dot-command.',
    u'The ability to end an SQL command using the line that contains just "go" or "/"',
    u'The ALTER TABLE command raises an error on any attempt to add, drop, or rename columns with the special names',
    u'Added the %J and %j conversions used to render JSON string literals',
    u'Drop support for WindowsXP and earlier Windows versions',
    u'About 4% faster, as measured by counting CPU cycles in the speedtest1',
    u'Added SQLITE_LIMIT_SCHEMA and SQLITE_LIMIT_TRIGGER_STEPS',
    u'Added the "weekday -N" form of the weekday modifier',
]
ATOMS = []
for a in ATOM_CAND:
    na = pnorm(a)
    if len(na) >= 3 and na in FACE:
        ATOMS.append(a)
F['atom_n'] = len(ATOMS)
F['atom_lines'] = ATOMS

io.open('corpus/_b85meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms85.txt', 'w', encoding='utf-8') as f:
    for a in ATOMS:
        f.write(a + u'\n')

for k, v in F.items():
    if k != 'atom_lines':
        print(k, v)
print('anchors', len(ATOMS))
