# -*- coding: utf-8 -*-
# B83 选锚与现算: SQLite 更新日志三版本段(补丁 3.54.1⟦A⟧ / 母版 3.54.0⟦B⟧ / 旧线补丁 3.53.4⟦C⟧)。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C']
FILES = {
    'A': 'corpus/raw/nws/afd_a.txt',
    'B': 'corpus/raw/nws/afd_b.txt',
    'C': 'corpus/raw/nws/afd_c.txt',
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

# ---- 模板轴(全国统一) ----
three('key_messages', cnt(u'key messages'))
three('amp', cnt(u'&&'))
three('aviation', cnt(u'aviation'))
three('nws', cnt(u'national weather service'))
three('afd_hdr', cnt(u'area forecast discussion'))
three('fire', cnt(u'fire'))

# ---- 办公室文化轴 ----
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

# ---- 句集交集 ----
SENTS = [set(split_sents(t)) for t in TXT]
for (i, j), nm in zip([(0, 1), (0, 2), (1, 2)], ['sh_ab', 'sh_ac', 'sh_bc']):
    F[nm] = len(SENTS[i] & SENTS[j])
F['sent_uniq'] = [len(SENTS[i]) for i in range(3)]

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
    ('A', u'Area Forecast Discussion National Weather Service Houston/Galveston TX'),
    ('A', u'Elevated fire weather conditions are possible over the next couple of days.'),
    ('C', u'This is ushering drier air in to the region with moderate to high confidence for ongoing IFR/MVFR conditions'),
    ('C', u'Area Forecast Discussion National Weather Service Spokane WA'),
    ('A', u'Warm and dry conditions expected through early next week.'),
]
ATOMS = []
for tg, a in ATOM_CAND:
    na = pnorm(a)
    if len(na) >= 3 and na in FACE:
        ATOMS.append((tg, a))
F['atom_tags'] = [tg for tg, _ in ATOMS]
F['atom_n'] = len(ATOMS)

io.open('corpus/_b83meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms83.txt', 'w', encoding='utf-8') as f:
    for _, a in ATOMS:
        f.write(a + u'\n')

