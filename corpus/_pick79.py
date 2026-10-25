# -*- coding: utf-8 -*-
# B79 选锚与现算: SQLite 更新日志三版本段(补丁 3.54.1⟦A⟧ / 母版 3.54.0⟦B⟧ / 旧线补丁 3.53.4⟦C⟧)。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C']
FILES = {
    'A': 'corpus/raw/changelog/sqlite_a.txt',
    'B': 'corpus/raw/changelog/sqlite_b.txt',
    'C': 'corpus/raw/changelog/sqlite_c.txt',
}
TXT, LOW = [], []
for tg in TAGS:
    raw = io.open(FILES[tg], encoding='utf-8', errors='replace').read()
    TXT.append(u' '.join(raw.partition('\n\n')[2].split()))
    LOW.append(TXT[-1].lower())


def split_sents(t):
    out, cur = [], u''
    for ch in t:
        cur += ch
        if ch in u'.!?':
            if len(cur.strip()) > 40:
                out.append(cur.strip().lower())
            cur = u''
    if len(cur.strip()) > 40:
        out.append(cur.strip().lower())
    return out


F = {}


def three(name, vals):
    assert len(vals) == 3, name
    F[name] = vals
    return vals


def cnt(kw):
    return [t.count(kw) for t in LOW]


three('chars', [len(t) for t in TXT])
three('lines', [r.count(u'\n') for r in (io.open(FILES[tg], encoding='utf-8').read().partition(u'\n\n')[2] for tg in TAGS)])
F['sents'] = [len(split_sents(t)) for t in TXT]
three('avg_sent', [F['chars'][i] // max(F['sents'][i], 1) for i in range(3)])

# ---- 动词轴 ----
three('fix', cnt(u'fix'))
three('add', cnt(u'add'))
three('improve', cnt(u'improve'))
three('optimization', cnt(u'optimization'))
three('optimize', cnt(u'optimiz'))
three('bug', cnt(u'bug'))
three('enhance', cnt(u'enhanc'))
three('new_word', [t.count(u'new ') for t in LOW])

# ---- 自反引用(补丁指向母版) ----
three('ref_540', cnt(u'3.54.0'))
three('ref_541', cnt(u'3.54.1'))
three('ref_item', cnt(u'item '))
three('release_word', cnt(u'release'))
three('previous', cnt(u'previous'))
three('source_id', cnt(u'sqlite_source_id'))
three('hashes', cnt(u'sha3'))
three('ais', cnt(u'from ais'))
three('heap', cnt(u'heap-buffer'))
three('bit32', cnt(u'32-bit'))
three('reported_users', cnt(u'reported by users'))
three('lineage', cnt(u'3.53.3'))
three('users_word', cnt(u'users'))
three('broken1', cnt(u'is now be'))
three('broken2', cnt(u'the replaces'))
three('date_line', cnt(u'2026-10-16'))
three('date_b', cnt(u'2026-10-09'))

# ---- 句集交集 ----
SENTS = [set(split_sents(t)) for t in TXT]
for (i, j), nm in zip([(0, 1), (0, 2), (1, 2)], ['sh_ab', 'sh_ac', 'sh_bc']):
    F[nm] = len(SENTS[i] & SENTS[j])

# ---- 锚 ----
import re


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


FACE = u'\n'.join(pnorm(t) for t in TXT)
ATOM_CAND = [
    ('A', u'Fix a possible heap-buffer overflow on 32-bit builds.'),
    ('A', u'Fixes other problems in 3.54.0 reported by users.'),
    ('C', u'Fixes for problems in 3.53.0 (and 3.53.1, 3.53.2, and 3.53.3) mostly coming from AIs.'),
    ('B', u'See the check-in timeline for details.'),
]
ATOMS = []
for tg, a in ATOM_CAND:
    na = pnorm(a)
    if len(na) >= 3 and na in FACE:
        ATOMS.append((tg, a))
F['atom_tags'] = [tg for tg, _ in ATOMS]
F['atom_n'] = len(ATOMS)

io.open('corpus/_b79meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms79.txt', 'w', encoding='utf-8') as f:
    for _, a in ATOMS:
        f.write(a + u'\n')

print('== B79 pick ==')
print('chars', F['chars'], 'sents', F['sents'], 'avg', F['avg_sent'])
print('fix', F['fix'], 'add', F['add'], 'improve', F['improve'], 'optimiz', F['optimize'], 'bug', F['bug'], 'new', F['new_word'])
print('ref_540', F['ref_540'], 'ref_item', F['ref_item'], 'release', F['release_word'], 'previous', F['previous'])
print('source_id', F['source_id'], 'hashes', F['hashes'])
print('ais', F['ais'], 'heap', F['heap'], '32bit', F['bit32'], 'reported', F['reported_users'], 'lineage', F['lineage'])
print('句集交集 AB', F['sh_ab'], 'AC', F['sh_ac'], 'BC', F['sh_bc'])
print('atoms', F['atom_n'], F['atom_tags'])
