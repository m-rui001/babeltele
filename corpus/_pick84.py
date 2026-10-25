# -*- coding: utf-8 -*-
# B84 选锚与现算: 单文本压缩(美国宪法全文)。测量结构计数, 全部落 _b84meas.json。
import io, json, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FILES = {'A': 'corpus/raw/constitution/us_constitution_full.txt'}
raw = io.open(FILES['A'], encoding='utf-8', errors='replace').read()
body = raw.partition(u'\n\n')[2]
FLAT = u' '.join(body.split())
LOW = FLAT.lower()

F = {}
F['chars'] = [len(FLAT)]
F['words'] = [len(FLAT.split())]

# 结构计数(词边界: 以空格切 token 数 roman 头)
toks = LOW.split(u' ')


def roman_hdr_count(word):
    # 形如 'amendment'/'article' 后紧跟纯罗马数字 token
    n = 0
    romans = set(u'i v x l c d m')
    for i, tk in enumerate(toks):
        if tk == word and i + 1 < len(toks):
            nxt = toks[i + 1].strip(u'.,;:()[]')
            if nxt and all(ch in u'ivxlcdm' for ch in nxt):
                n += 1
    return n


F['amend_hdr'] = [roman_hdr_count(u'amendment')]
F['article_hdr'] = [roman_hdr_count(u'article')]

# 序言词数: 'we the people' 起到 'article' 首现
i0 = LOW.find(u'we the people')
i1 = LOW.find(u'article', i0)
F['preamble_words'] = [len(LOW[i0:i1].split())]

for kw in [u'congress', u'president', u'senate', u'section', u'repeal', u'court', u'state']:
    F[kw if kw != u'section' else u'section_word'] = [LOW.count(kw)]

# 补充: 两院/年龄/年数等数值词面(供编码引用, 需逐字在源)
for kw in [u'two thirds', u'thirty', u'seven years', u'twenty five', u'fourteen years', u'ten days',
           u'nine states', u'fourteen', u'thirds']:
    F['kw_' + kw.replace(u' ', u'_')] = [LOW.count(kw)]

# 锚(逐字)
import re


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


FACE = pnorm(FLAT)
ATOM_CAND = [
    'We the People of the United States, in Order to form a more perfect Union',
    'All legislative Powers herein granted shall be vested in a Congress',
    'The executive Power shall be vested in a President',
    'Congress shall make no law respecting an establishment of religion',
    'the right of the people to keep and bear Arms, shall not be infringed',
    'No Soldier shall, in time of peace be quartered',
    'excessive bail shall not be required, nor excessive fines imposed',
    'nor be deprived of life, liberty, or property, without due process of law',
    'The enumeration in the Constitution, of certain rights, shall not be construed',
    'The powers not delegated to the United States',
    'neither slavery nor involuntary servitude',
    'No person shall be elected to the office of the President more than twice',
    'unreasonable searches and seizures',
    'a well regulated militia',
    'speedy and public trial',
    'compelled in any criminal case to be a witness against himself',
]
ATOMS = []
for a in ATOM_CAND:
    na = pnorm(a)
    if len(na) >= 3 and na in FACE:
        ATOMS.append(a)
F['atom_n'] = len(ATOMS)
F['atom_lines'] = ATOMS

io.open('corpus/_b84meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
with io.open('corpus/_atoms84.txt', 'w', encoding='utf-8') as f:
    for a in ATOMS:
        f.write(a + u'\n')

for k, v in F.items():
    if k != 'atom_lines':
        print(k, v)
print('anchors', len(ATOMS))
