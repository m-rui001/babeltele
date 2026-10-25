# -*- coding: utf-8 -*-
# B73 选锚与现算: 四份 10-K Item 1A 风险因素(AAPL FY25⟦A⟧⇎AAPL FY24⟦B⟧两年搬运轴 ⇎ MSFT⟦C⟧/GOOG⟦D⟧ FY25 行业共享轴)。
# 采集侧: 字符游标与句切分(计数主路不用 re); 全部值现算落 _b73meas.json。
import io, json, re, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C', 'D']
FILES = {
    'A': 'corpus/raw/filings/aapl25_10k_1a.txt',
    'B': 'corpus/raw/filings/aapl24_10k_1a.txt',
    'C': 'corpus/raw/filings/msft25_10k_1a.txt',
    'D': 'corpus/raw/filings/goog25_10k_1a.txt',
}

TXT, LOW = [], []
for tg in TAGS:
    raw = io.open(FILES[tg], encoding='utf-8', errors='replace').read()
    body = raw.partition('\n\n')[2]
    body = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), body)
    body = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), body)
    body = body.replace(u'&amp;', u'&').replace(u'&lt;', u'<').replace(u'&gt;', u'>').replace(u'&quot;', u'"')
    TXT.append(u' '.join(body.split()))
    LOW.append(TXT[-1].lower())


def split_sents(t):
    out, cur = [], u''
    for ch in t:
        cur += ch
        if ch in u'.!?':
            out.append(cur.strip())
            cur = u''
    if cur.strip():
        out.append(cur.strip())
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
four('lines', [r.count(u'\n') for r in (io.open(FILES[tg], encoding='utf-8', errors='replace').read().partition(u'\n\n')[2] for tg in TAGS)])
F['sents'] = [len([s for s in split_sents(t) if len(s) > 40]) for t in TXT]
four('avg_sent', [F['chars'][i] // max(F['sents'][i], 1) for i in range(4)])

# ---- 句级搬运(自我指纹) ----
SENTS = [set(s.strip().lower() for s in split_sents(t) if len(s) > 40) for t in TXT]
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
F['sh_ab_pct'] = round(100.0 * F['sh_ab'] / F['sents'][0], 1)

# ---- 体裁指纹 ----
four('could_harm', cnt(u'could harm'))
four('may_adversely', cnt(u'may adversely affect'))
four('if_we', [t.count(u'if we') for t in LOW])
four('the_company', cnt(u'the company'))
four('we_word', [t.count(u' we ') for t in LOW])

# ---- 主题轴 ----
four('tariff', cnt(u'tariff'))
four('ai', cnt(u'artificial intelligence'))
four('appstore', cnt(u'app store'))
four('stockprice', cnt(u'stock price'))
four('supply', cnt(u'supply chain'))
four('cyber', cnt(u'cyberattack'))
four('privacy', cnt(u'data privacy'))
four('litigation', cnt(u'litigation'))
four('competition', cnt(u'competition'))
four('intprop', cnt(u'intellectual property'))
four('china', cnt(u'china'))
four('regulat', cnt(u'regulat'))

# ---- 锚(逐字, 每锚带标签) ----
def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


import re
FACE = u'\n'.join(pnorm(t) for t in TXT)
ATOM_CAND = [
    ('A', u'Restrictions on international trade, such as tariffs and other controls on imports or exports of goods, technology or data, can materially adversely affect the Company’s business and supply chain.'),
    ('B', u'exposed to information technology system failures or network disruptions caused by natural disasters, accidents, power disruptions, telecommunications failures, acts of terrorism or war, computer viruses, physical or electronic break-ins, ransomware'),
    ('C', u'A catastrophic event that results in the destruction or disruption of any of our critical business or systems, or the infrastructure or systems they rely on, such as power grids, could harm our ability to conduct normal business operations or adversely affect our results of operations.'),
    ('D', u'Reduced spending by advertisers, a loss of partners, or new and existing technologies that block ads online and/or affect our ability to personalize ads could harm our business.'),
    ('D', u'Our operations and financial results are subject to various risks and uncertainties, including but not limited to those described below, which could harm our business, reputation, financial condition, and operating results'),
]
ATOMS = []
for tg, a in ATOM_CAND:
    na = pnorm(a)
    assert len(na) >= 3 and na in FACE, u'锚未命中 %s: %s' % (tg, a[:60])
    ATOMS.append((tg, a))
F['atom_tags'] = [tg for tg, _ in ATOMS]
F['atom_n'] = len(ATOMS)

io.open('corpus/_b73meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms73.txt', 'w', encoding='utf-8') as f:
    for _, a in ATOMS:
        f.write(a + u'\n')

print('== B73 pick ==')
print('chars', F['chars'], 'lines', F['lines'], 'sents', F['sents'], 'avg', F['avg_sent'])
print('共享句 AB', F['sh_ab'], 'AC', F['sh_ac'], 'AD', F['sh_ad'], 'BC', F['sh_bc'], 'BD', F['sh_bd'], 'CD', F['sh_cd'], 'AB%', F['sh_ab_pct'])
print('could_harm', F['could_harm'], 'may_adv', F['may_adversely'], 'if_we', F['if_we'], 'the_company', F['the_company'], 'we', F['we_word'])
print('tariff', F['tariff'], 'ai', F['ai'], 'appstore', F['appstore'], 'stock', F['stockprice'], 'china', F['china'])
print('atoms', F['atom_n'], F['atom_tags'])
