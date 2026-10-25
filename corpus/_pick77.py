# -*- coding: utf-8 -*-
# B77 选锚与现算: 同一论文三版本(Llama 3 Herd, v1⇎v2⇎v3)。采集侧: 折平词面计数, 全部落 _b77meas.json。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C']
FILES = {
    'A': 'corpus/raw/arxiv/llama3_a.txt',
    'B': 'corpus/raw/arxiv/llama3_b.txt',
    'C': 'corpus/raw/arxiv/llama3_c.txt',
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

# ---- 版本差轴: 元数据三落点 ----
three('date_v1', cnt(u'31 jul 2024'))
three('date_v2', cnt(u'15 aug 2024'))
three('date_v3', cnt(u'23 nov 2024'))
three('jardanhan', cnt(u'jardanhan'))
three('janardhan', cnt(u'janardhan'))
three('tbl4_old', cnt(u'16 16 4 131,072'))
three('tbl4_new', cnt(u'16 16 8 131,072'))
three('core_aaron', cnt(u'core contributors aaron'))
three('amos_teo', cnt(u'amos teo'))
three('v1mark', cnt(u'21783v1'))
three('v2mark', cnt(u'21783v2'))
three('v3mark', cnt(u'21783v3'))

# ---- 正文不变轴(逐词频三版全等) ----
three('llama3', cnt(u'llama 3 '))
three('b405', [t.count(u'405') for t in LOW])
three('safety', cnt(u'safety'))
three('transformer', cnt(u'transformer'))
three('benchmark', cnt(u'benchmark'))
three('tokens', cnt(u' tokens'))
three('herd', cnt(u'herd of models'))

# ---- 句集交集(正文不可变轴) ----
SENTS = [set(split_sents(t)) for t in TXT]
pairs = {}
for i in range(3):
    for j in range(i + 1, 3):
        pairs[(i, j)] = len(SENTS[i] & SENTS[j])
F['sh_ab'] = pairs[(0, 1)]
F['sh_ac'] = pairs[(0, 2)]
F['sh_bc'] = pairs[(1, 2)]
F['sent_uniq'] = [len(SENTS[i]) for i in range(3)]

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
    ('A', u'[cs.AI] 31 Jul 2024 The Llama 3 Herd of Models'),
    ('B', u'[cs.AI] 15 Aug 2024 The Llama 3 Herd of Models'),
    ('C', u'[cs.AI] 23 Nov 2024 The Llama 3 Herd of Models'),
    ('A', u'santosh jardanhan'),
    ('C', u'santosh janardhan'),
    ('A', u'The Llama 3 Herd of Models Llama Team, AI @ Meta'),
]
ATOMS = []
for tg, a in ATOM_CAND:
    na = pnorm(a)
    if len(na) >= 3 and na in FACE:
        ATOMS.append((tg, a))
F['atom_tags'] = [tg for tg, _ in ATOMS]
F['atom_n'] = len(ATOMS)

io.open('corpus/_b77meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms77.txt', 'w', encoding='utf-8') as f:
    for _, a in ATOMS:
        f.write(a + u'\n')

print('== B77 pick ==')
print('chars', F['chars'], 'sents', F['sents'], 'avg', F['avg_sent'])
print('dates', F['date_v1'], F['date_v2'], F['date_v3'])
print('jardanhan', F['jardanhan'], 'janardhan', F['janardhan'])
print('tbl4 old', F['tbl4_old'], 'new', F['tbl4_new'])
print('core_aaron', F['core_aaron'], 'amos_teo', F['amos_teo'], 'marks', F['v1mark'], F['v2mark'], F['v3mark'])
print('正文不变轴 llama3', F['llama3'], '405', F['b405'], 'safety', F['safety'], 'transformer', F['transformer'], 'herd', F['herd'])
print('句集交集 AB', F['sh_ab'], 'AC', F['sh_ac'], 'BC', F['sh_bc'], 'uniq', F['sent_uniq'])
print('atoms', F['atom_n'], F['atom_tags'])
