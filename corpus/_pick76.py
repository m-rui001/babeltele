# -*- coding: utf-8 -*-
# B76 选锚与现算: 同一次 FOMC 会议(2025-09)的三份体裁(声明⟦A⟧/纪要⟦B⟧/经济预测摘要⟦C⟧)。
# 采集侧: 折平词面计数, 计数主路不用 re; 全部值现算落 _b76meas.json。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C']
FILES = {
    'A': 'corpus/raw/fomc/fomc25sep_a.txt',
    'B': 'corpus/raw/fomc/fomc25sep_b.txt',
    'C': 'corpus/raw/fomc/fomc25sep_c.txt',
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


# ---- 壳账 ----
three('chars', [len(t) for t in TXT])
three('lines', [r.count(u'\n') for r in (io.open(FILES[tg], encoding='utf-8').read().partition(u'\n\n')[2] for tg in TAGS)])
F['sents'] = [len(split_sents(t)) for t in TXT]
three('avg_sent', [F['chars'][i] // max(F['sents'][i], 1) for i in range(3)])

# ---- 体裁轴 ----
three('powell', cnt(u'powell'))
three('participants', cnt(u'participant'))
three('staff', cnt(u'staff'))
three('respondents', cnt(u'respondent'))
three('voted', cnt(u'vot'))
three('against', [t.count(u'against') for t in LOW])
three('miran', cnt(u'miran'))
three('uncertain', cnt(u'uncertaint'))
three('risk', [t.count(u'risk') for t in LOW])
three('balance_risks', cnt(u'balance of risks'))
three('inflation', cnt(u'inflation'))
three('labor', cnt(u'labor'))
three('employment', cnt(u'employment'))
three('tariff', cnt(u'tariff'))
three('october', cnt(u'october'))
three('december', cnt(u'december'))
three('yearend', [t.count(u'year-end') + t.count(u'year end') for t in LOW])
three('median', cnt(u'median'))
three('longer_run', [t.count(u'longer run') for t in LOW])
three('quarter_point', [t.count(u'quarter percentage point') + t.count(u'basis point') for t in LOW])
three('gradually', cnt(u'gradual'))
three('downside', cnt(u'downside'))
three('deviation', cnt(u'deviation'))
three('survey', cnt(u'survey'))
three('projection', cnt(u'projection'))
three('minutes_word', cnt(u'participants'))

# ---- 句集交集(互抄轴) ----
SENTS = [set(split_sents(t)) for t in TXT]
pairs = {}
for i in range(3):
    for j in range(i + 1, 3):
        pairs[(i, j)] = len(SENTS[i] & SENTS[j])
F['sh_ab'] = pairs[(0, 1)]
F['sh_ac'] = pairs[(0, 2)]
F['sh_bc'] = pairs[(1, 2)]

# ---- 锚(逐字) ----
import re


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


FACE = u'\n'.join(pnorm(t) for t in TXT)
ATOM_CAND = [
    ('A', u'lower the target range for the federal funds rate by 1/4 percentage point to 4 to 4-1/4 percent'),
    ('A', u'the balance of risks'),
    ('B', u'voted against'),
    ('C', u'median federal funds rate'),
    ('C', u'longer run'),
]
ATOMS = []
for tg, a in ATOM_CAND:
    na = pnorm(a)
    if len(na) >= 3 and na in FACE:
        ATOMS.append((tg, a))
F['atom_tags'] = [tg for tg, _ in ATOMS]
F['atom_n'] = len(ATOMS)

io.open('corpus/_b76meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms76.txt', 'w', encoding='utf-8') as f:
    for _, a in ATOMS:
        f.write(a + u'\n')

print('== B76 pick ==')
print('chars', F['chars'], 'sents', F['sents'], 'avg', F['avg_sent'])
print('powell', F['powell'], 'participants', F['participants'], 'staff', F['staff'], 'respondents', F['respondents'])
print('voted', F['voted'], 'against', F['against'], 'miran', F['miran'])
print('uncertain', F['uncertain'], 'risk', F['risk'], 'balance_risks', F['balance_risks'], 'downside', F['downside'])
print('inflation', F['inflation'], 'labor', F['labor'], 'tariff', F['tariff'])
print('october', F['october'], 'december', F['december'], 'median', F['median'], 'projection', F['projection'])
print('共享句 AB', F['sh_ab'], 'AC', F['sh_ac'], 'BC', F['sh_bc'])
print('atoms', F['atom_n'], F['atom_tags'])
