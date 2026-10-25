# -*- coding: utf-8 -*-
# B75 选锚与现算: 同一判决书(Loper Bright, 2024)的四个声音(Syllabus⟦D⟧/多数意见⟦A⟧/Gorsuch 协同⟦B⟧/Kagan 异议⟦C⟧)。
# 采集侧: 折平词面计数, 计数主路不用 re; 全部值现算落 _b75meas.json。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C', 'D']
FILES = {
    'A': 'corpus/raw/opinions/loper_a.txt',
    'B': 'corpus/raw/opinions/loper_b.txt',
    'C': 'corpus/raw/opinions/loper_c.txt',
    'D': 'corpus/raw/opinions/loper_d.txt',
}
TXT, LOW = [], []
for tg in TAGS:
    raw = io.open(FILES[tg], encoding='utf-8', errors='replace').read()
    body = raw.partition('\n\n')[2]
    TXT.append(u' '.join(body.split()))
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


def four(name, vals):
    assert len(vals) == 4, name
    F[name] = vals
    return vals


def cnt(kw):
    return [t.count(kw) for t in LOW]


# ---- 壳账 ----
four('chars', [len(t) for t in TXT])
four('lines', [r.count(u'\n') for r in (io.open(FILES[tg], encoding='utf-8').read().partition(u'\n\n')[2] for tg in TAGS)])
F['sents'] = [len(split_sents(t)) for t in TXT]
four('avg_sent', [F['chars'][i] // max(F['sents'][i], 1) for i in range(4)])

# ---- 跨声音引用(谁点谁) ----
four('the_dissent', cnt(u'the dissent'))
four('the_majority', cnt(u'the majority'))
four('the_court_low', cnt(u'the court'))
four('justice_gorsuch', cnt(u'justice gorsuch'))
four('justice_kagan', cnt(u'justice kagan'))
four('chevron', cnt(u'chevron'))
four('stare', cnt(u'stare decisis'))
four('defer', [t.count(u'defer') for t in LOW])
four('congress', cnt(u'congress'))
four('agency', cnt(u'agency'))
four('apa', [t.count(u'apa') for t in LOW])
four('uncertain', cnt(u'uncertaint'))
four('policy', cnt(u'policy'))
four('constitution', cnt(u'constitution'))
four('precedent', cnt(u'precedent'))
four('overruled', [t.count(u'overrul') for t in LOW])
four('forty', [t.count(u'forty') + t.count(u'40') for t in LOW])
four('best_reading', cnt(u'best reading'))
four('ambigu', cnt(u'ambigu'))

# ---- 句集交集(互抄轴) ----
SENTS = [set(split_sents(t)) for t in TXT]
pairs = {}
for i in range(4):
    for j in range(i + 1, 4):
        pairs[(i, j)] = len(SENTS[i] & SENTS[j])
F['sh_ab'] = pairs[(0, 1)]
F['sh_ac'] = pairs[(0, 2)]
F['sh_ad'] = pairs[(0, 3)]
F['sh_bc'] = pairs[(1, 2)]
F['sh_bd'] = pairs[(1, 3)]
F['sh_cd'] = pairs[(2, 3)]

# ---- 锚(逐字, 每锚带标签) ----
import re


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


FACE = u'\n'.join(pnorm(t) for t in TXT)
ATOM_CAND = [
    ('A', u'Chevron is overruled.'),
    ('C', u'For 40 years, Chevron U. S. A. Inc. v. Natural Resources Defense Council'),
    ('C', u'The majority rolls out its own version of supermajority rules'),
    ('B', u'the ordinary meaning of a given statutory term'),
    ('D', u'Courts must exercise their independent judgment in deciding whether an agency has acted within its statutory authority'),
]
ATOMS = []
for tg, a in ATOM_CAND:
    na = pnorm(a)
    if len(na) >= 3 and na in FACE:
        ATOMS.append((tg, a))
F['atom_tags'] = [tg for tg, _ in ATOMS]
F['atom_n'] = len(ATOMS)

io.open('corpus/_b75meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms75.txt', 'w', encoding='utf-8') as f:
    for _, a in ATOMS:
        f.write(a + u'\n')

print('== B75 pick ==')
print('chars', F['chars'], 'sents', F['sents'], 'avg', F['avg_sent'])
print('the_dissent', F['the_dissent'], 'the_majority', F['the_majority'], 'the_court', F['the_court_low'])
print('chevron', F['chevron'], 'stare', F['stare'], 'defer', F['defer'], 'overrul', F['overruled'])
print('congress', F['congress'], 'agency', F['agency'], 'apa', F['apa'], 'policy', F['policy'], 'constitution', F['constitution'])
print('precedent', F['precedent'], 'forty', F['forty'], 'best_reading', F['best_reading'], 'ambigu', F['ambigu'])
print('共享句 AB', F['sh_ab'], 'AC', F['sh_ac'], 'AD', F['sh_ad'], 'BC', F['sh_bc'], 'BD', F['sh_bd'], 'CD', F['sh_cd'])
print('atoms', F['atom_n'], F['atom_tags'])
