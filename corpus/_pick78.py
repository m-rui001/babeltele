# -*- coding: utf-8 -*-
# B78 选锚与现算: 同一缺陷(LPSOV 线束/UERF)的两次 FAA 适航指令(初始 AD ⟦A⟧ ⇎ 整改 AD ⟦B⟧)。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B']
FILES = {
    'A': 'corpus/raw/faa/ad_a.txt',
    'B': 'corpus/raw/faa/ad_b.txt',
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


def two(name, vals):
    assert len(vals) == 2, name
    F[name] = vals
    return vals


def cnt(kw):
    return [t.count(kw) for t in LOW]


two('chars', [len(t) for t in TXT])
two('lines', [r.count(u'\n') for r in (io.open(FILES[tg], encoding='utf-8').read().partition(u'\n\n')[2] for tg in TAGS)])
F['sents'] = [len(split_sents(t)) for t in TXT]
two('avg_sent', [F['chars'][i] // max(F['sents'][i], 1) for i in range(2)])

# ---- 互指与谱系 ----
two('easa', cnt(u'easa'))
two('unsafe', cnt(u'unsafe condition'))
two('lpsov', cnt(u'lpsov'))
two('uerf', cnt(u'uerf'))
two('prompted', cnt(u'prompted by'))
two('other_ad', [t.count(u'2023-01702') - (1 if i == 0 else 0) for i, t in enumerate(LOW)])  # B 引 A
two('self_ad', [t.count(u'2023-22080') - (1 if i == 1 else 0) for i, t in enumerate(LOW)])
two('mcai', cnt(u'mcai'))
two('modification', cnt(u'modif'))
two('inspect', cnt(u'inspect'))
two('cost', cnt(u'cost'))
two('comments', cnt(u'comment'))
two('supersedes', cnt(u'supersede'))
two('amends', cnt(u'amends'))
two('paperwork', cnt(u'paperwork'))
two('interim', cnt(u'interim'))
two('fires', cnt(u'fire'))
two('fuel', cnt(u'fuel'))
two('2022_0185', cnt(u'2022-0185'))
two('r2', cnt(u'required for installation'))
two('docket', cnt(u'docket'))

# ---- 句集交集 ----
SENTS = [set(split_sents(t)) for t in TXT]
F['sh_ab'] = len(SENTS[0] & SENTS[1])
F['sent_uniq'] = [len(SENTS[i]) for i in range(2)]

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
    ('A', u'This AD was prompted by a safety review of the airplane fuel system, which identified that the electrical harness routing of the engine low pressure shut off valve (LPSOV) is not adequately protected against uncontained engine rotor failure (UERF).'),
    ('B', u'This AD requires modification of the LPSOV electrical harness routing on either the left-hand engine or the right-hand engine'),
    ('B', u'loss of engine fuel isolation capability in case of UERF, possibly resulting in an uncontrolled fire'),
    ('A', u'unsafe condition may exist on airplanes with two different types of engines installed'),
    ('B', u'This AD applies to the Airbus SAS airplanes specified in paragraphs (c)(1) through (3) of this AD'),
]
ATOMS = []
for tg, a in ATOM_CAND:
    na = pnorm(a)
    if len(na) >= 3 and na in FACE:
        ATOMS.append((tg, a))
F['atom_tags'] = [tg for tg, _ in ATOMS]
F['atom_n'] = len(ATOMS)

io.open('corpus/_b78meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms78.txt', 'w', encoding='utf-8') as f:
    for _, a in ATOMS:
        f.write(a + u'\n')

print('== B78 pick ==')
print('chars', F['chars'], 'sents', F['sents'], 'avg', F['avg_sent'])
print('easa', F['easa'], 'unsafe', F['unsafe'], 'lpsov', F['lpsov'], 'uerf', F['uerf'], 'prompted', F['prompted'])
print('other_ad', F['other_ad'], 'self_ad', F['self_ad'], 'mcai', F['mcai'], '2022-0185', F['2022_0185'])
print('modification', F['modification'], 'inspect', F['inspect'], 'cost', F['cost'], 'comments', F['comments'])
print('supersedes', F['supersedes'], 'amends', F['amends'], 'interim', F['interim'], 'fires', F['fires'], 'docket', F['docket'])
print('共享句', F['sh_ab'], 'uniq', F['sent_uniq'])
print('atoms', F['atom_n'], F['atom_tags'])
