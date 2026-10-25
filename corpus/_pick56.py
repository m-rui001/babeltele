# -*- coding: utf-8 -*-
"""B56 第一遍(独立采集, 先于建条目写成): 只从三份在库字节现量。
I = corpus/raw/tz/iso3166.tab(249 行两位码⇎名, 排序与命名理由写在它自己的注释里),
Z = corpus/raw/tz/zone1970.tab(把同一批码当国家列), R = corpus/raw/langsubtag.txt(region 型子标签 305 枚)。
本遍的主产物不是“三份文件各有多少行”, 而是同一批码在三处各自的值域与词汇:
  码集包含方向(Z ⇎ I ⇎ R 的双向差集与三向交)、名字串在三份表里的相等⇎不等、不等里“只换写法”⇎“换了词”的分档,
  以及 I 的注释自写的三条命名理由能不能在它自己的数据里逐条验到。
落 corpus/_b56meas.json: {meas, pool, sel, tags, paths, labels}; pool 是逐字锚候选 (标签, 命中源数, 原文或片段)。
建条目侧 corpus/_mkB56.py 只从这里取锚, 并在 TIE 表里与本遍逐量对账。
"""
import collections, hashlib, io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NL = chr(10)
TAGS = [u'I', u'Z', u'R']
PATHS = [u'corpus/raw/tz/iso3166.tab', u'corpus/raw/tz/zone1970.tab', u'corpus/raw/langsubtag.txt']
LB = [u'ISO 3166 码表', u'时区表', u'子标签注册表']
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATHS]
M = {}


def two(name, f):
    M[name] = [f(i) for i in range(3)]


two(u'bytes', lambda i: os.path.getsize(PATHS[i]))
two(u'chars', lambda i: len(TXT[i]))
two(u'lines', lambda i: TXT[i].count(NL))
two(u'segments', lambda i: len(TXT[i].split(NL)))
two(u'nonblank', lambda i: len([l for l in TXT[i].split(NL) if l.strip()]))
two(u'blank', lambda i: M[u'segments'][i] - M[u'nonblank'][i])
two(u'lt', lambda i: TXT[i].count(u'<'))
two(u'gt', lambda i: TXT[i].count(u'>'))
two(u'nonascii', lambda i: len([c for c in TXT[i] if ord(c) > 127]))
two(u'tabs', lambda i: TXT[i].count(u'\t'))
two(u'hash', lambda i: len([l for l in TXT[i].split(NL) if l.startswith(u'#')]))
two(u'sha16', lambda i: hashlib.sha256(open(PATHS[i], 'rb').read()).hexdigest()[:16])
M[u'ascii_eq'] = [1 if M[u'nonascii'][i] == 0 else 0 for i in range(3)]

IV, ZV, RV = TXT[0], TXT[1], TXT[2]
IL, ZL_, RL = IV.split(NL), ZV.split(NL), RV.split(NL)

# ---------- I 侧: 码表本身 ----------
IDAT = [l.split(u'\t') for l in IL if l.strip() and not l.startswith(u'#')]
M[u'i_rows'] = len(IDAT)
M[u'i_cols'] = sorted(set(len(x) for x in IDAT))
NAME = [x[1] for x in IDAT]
CODE = [x[0] for x in IDAT]
M[u'i_code_n'] = len(CODE)
M[u'i_code_dist'] = len(set(CODE))
M[u'i_code_dup'] = len(CODE) - len(set(CODE))
M[u'i_name_dist'] = len(set(NAME))
M[u'i_name_dup'] = len(NAME) - len(set(NAME))
M[u'i_name_dupv'] = sorted(set(n for n in NAME if NAME.count(n) > 1))
M[u'i_sorted_desc'] = sum(1 for i in range(1, len(CODE)) if CODE[i] < CODE[i - 1])
M[u'i_hdr_cmt'] = len([l for l in IL if l.startswith(u'#') and u'\t' in l])
M[u'i_tab_expect'] = M[u'i_rows'] * (M[u'i_cols'][0] - 1) + M[u'i_hdr_cmt']
M[u'i_tab_diff'] = M[u'i_tab_expect'] - TXT[0].count(u'\t')
M[u'i_len2'] = sum(1 for c in CODE if len(c) == 2)
M[u'i_amp'] = sum(1 for n in NAME if u'&' in n)
M[u'i_paren'] = sum(1 for n in NAME if u'(' in n)
M[u'i_dot'] = sum(1 for n in NAME if u'.' in n)
M[u'i_comma'] = sum(1 for n in NAME if u',' in n)
M[u'i_nonascii_names'] = len([n for n in NAME if any(ord(ch) > 127 for ch in n)])
M[u'i_apos_curly'] = len([n for n in NAME if u'\u2019' in n])
M[u'i_maxlen'] = max(len(n) for n in NAME)
M[u'i_maxlen_v'] = [n for n in NAME if len(n) == M[u'i_maxlen']]
M[u'i_minlen'] = min(len(n) for n in NAME)
M[u'i_name_chars'] = sum(len(n) for n in NAME)
M[u'i_cmt_lines'] = M[u'hash'][0]
M[u'i_cmt_chars'] = sum(len(l) for l in IL if l.startswith(u'#'))
M[u'i_dates'] = sorted(set(re.findall(r'\d{4}-\d{2}-\d{2}', IV)))
try:
    open(PATHS[0], 'rb').read().decode('utf-8')
    M[u'i_utf8_strict'] = 1
except UnicodeDecodeError:
    M[u'i_utf8_strict'] = 0
M[u'i_bytegap'] = M[u'bytes'][0] - M[u'chars'][0]

# 注释自写的三条命名理由, 逐条交给数据判
CLAIM_PAIR = [(u'AS', u'Samoa (American)'), (u'WS', u'Samoa (western)')]
SN = sorted(NAME)
M[u'i_claim_samoa'] = sum(1 for c, n in CLAIM_PAIR if c in CODE and NAME[CODE.index(c)] == n)
M[u'i_samoa_adj'] = (abs(SN.index(u'Samoa (western)') - SN.index(u'Samoa (American)')) - 1
                     if all(n in SN for n in (u'Samoa (western)', u'Samoa (American)')) else -1)
OLDNAMES = {u'CZ': u'Czech Republic', u'TR': u'Turkey', u'NL': u'Netherlands'}
M[u'i_claim_oldnames'] = sum(1 for c, n in OLDNAMES.items() if c in CODE and NAME[CODE.index(c)] == n)
M[u'i_claim_absent'] = sum(1 for w in (u'Czechia', u'Türkiye', u'Turkiye') if w not in NAME)
# 名字排序把同名干并置: 有多少相邻对共享括号前的词干
STEM = [n.split(u' (')[0] for n in SN]
M[u'i_stem_adj'] = sum(1 for i in range(1, len(SN)) if STEM[i] == STEM[i - 1])
M[u'i_stem_kinds'] = len(set(STEM))
M[u'i_stem_multi'] = len([s for s in set(STEM) if STEM.count(s) > 1])
MULTI = [s for s in set(STEM) if STEM.count(s) > 1]


def idxs(s):
    return [i for i, x in enumerate(SN) if x.split(u' (')[0] == s]


M[u'i_stem_contig'] = len([s for s in MULTI if idxs(s)[-1] - idxs(s)[0] + 1 == len(idxs(s))])
# 注释点名的六个“ISO 上另有写法”的串: 本表用着的 ⇎ 本表避掉的
USEDBY = [u'Samoa (American)', u'Samoa (western)', u'Czech Republic', u'Turkey', u'Netherlands']
AVOIDED = [u'American Samoa', u'Samoa', u'Czechia', u'Türkiye', u'Netherlands (the)',
           u'Netherlands (Kingdom of the)']
M[u'i_claim_used'] = len([w for w in USEDBY if w in NAME])
M[u'i_claim_avoided'] = len([w for w in AVOIDED if w not in NAME])
M[u'i_claim_open'] = (M[u'i_claim_used'] + M[u'i_claim_avoided'] - (len(USEDBY) + len(AVOIDED)))
M[u'i_avoided_present'] = len([w for w in AVOIDED if w in NAME])
M[u'i_dot_names'] = [n for n in NAME if u'.' in n]
M[u'i_url'] = IV.count(u'https://')
M[u'i_tab_in_cmt'] = len([l for l in IL if l.startswith(u'#') and u'\t' in l])
M[u'i_tab_data'] = sum(l.count(u'\t') for l in IL if l.strip() and not l.startswith(u'#'))
M[u'i_hdr_split'] = 1 if (u'#country-' + NL + u'#code' in IV and u'country-code' not in IV) else 0
DPOS = sorted([(IV.find(d), d) for d in M[u'i_dates']])
M[u'i_date_pos'] = [p for (p, d) in DPOS]
BYPOS = [d for (p, d) in DPOS]
M[u'i_dates_byline'] = BYPOS
M[u'i_date_unsorted'] = sum(1 for i in range(1, len(BYPOS)) if BYPOS[i] < BYPOS[i - 1])
M[u'i_leap_ok'] = len([d for d in M[u'i_dates'] if d.endswith(u'-02-29')])

# ---------- Z 侧: 把码当国家列的表(与 B55 同一份字节, 本遍独立重取) ----------
ZD = [l.split(u'\t') for l in ZL_ if l.strip() and not l.startswith(u'#')]
M[u'z_rows'] = len(ZD)
M[u'z_cols'] = sorted(set(len(x) for x in ZD))
M[u'z_col3'] = sum(1 for x in ZD if len(x) == 3)
M[u'z_col4'] = sum(1 for x in ZD if len(x) > 3)
CC = [c for x in ZD for c in x[0].split(u',')]
M[u'z_cc_occ'] = len(CC)
M[u'z_cc_dist'] = len(set(CC))
M[u'z_multi_rows'] = len([x for x in ZD if u',' in x[0]])
M[u'z_maxm'] = max(len(x[0].split(u',')) for x in ZD)
CNTZ = collections.Counter(CC)
M[u'z_shared_rows'] = len([x for x in ZD if any(CNTZ[c] > 1 for c in x[0].split(u','))])
M[u'z_at'] = len([l for l in ZL_ if l.startswith(u'#@')])
ZF = [l for l in ZL_ if l.startswith(u'#') and u'\t' in l]
M[u'z_hdr_tab'] = ZF[0].count(u'\t') if ZF else 0
M[u'z_tab_expect'] = M[u'z_col3'] * 2 + M[u'z_col4'] * 3 + M[u'z_hdr_tab'] + M[u'z_at']
M[u'z_tab_diff'] = M[u'z_tab_expect'] - TXT[1].count(u'\t')
ZFIRST = [x[0].split(u',')[0] for x in ZD]
M[u'z_first_desc'] = sum(1 for i in range(1, len(ZFIRST)) if ZFIRST[i] < ZFIRST[i - 1])
TAILBAD = [x for x in ZD if x[0].split(u',')[1:] != sorted(x[0].split(u',')[1:])]
M[u'z_tail_un'] = len(TAILBAD)
WHOLEBAD = [x for x in ZD if x[0].split(u',') != sorted(x[0].split(u','))]
M[u'z_whole_un'] = len(WHOLEBAD)
M[u'z_lat4'] = len([x for x in ZD if len(re.split(u'[+-]', x[1])[1]) == 4])
M[u'z_lat6'] = len([x for x in ZD if len(re.split(u'[+-]', x[1])[1]) == 6])
M[u'z_coord_sum'] = M[u'z_lat4'] + M[u'z_lat6'] - M[u'z_rows']

# ---------- R 侧: 只取 region 型 ----------
SEGS, cur = [], []
for l in RL:
    if l.strip() == u'%%':
        SEGS.append(cur); cur = []
    else:
        cur.append(l)
SEGS.append(cur)
M[u'r_segs'] = len([s for s in SEGS if any(x.strip() for x in s)])
M[u'r_sep'] = len([l for l in RL if l.strip() == u'%%'])


def segdict(s):
    d = {}
    for l in s:
        m = re.match(u'([A-Za-z][A-Za-z-]*):[ ]?(.*)$', l)
        if m:
            d[m.group(1)] = m.group(2)
    return d


FD = [segdict(s) for s in SEGS]
REG = dict((d[u'Subtag'], d.get(u'Description', u'')) for d in FD if d.get(u'Type') == u'region')
M[u'r_region_n'] = len(REG)
M[u'r_alpha'] = len([c for c in REG if len(c) == 2])
M[u'r_digit'] = len([c for c in REG if c.isdigit()])
M[u'r_range'] = len([c for c in REG if u'..' in c])
M[u'r_other'] = M[u'r_region_n'] - M[u'r_alpha'] - M[u'r_digit'] - M[u'r_range']
M[u'r_desc_amp'] = len([v for v in REG.values() if u'&' in v])
M[u'r_desc_paren'] = len([v for v in REG.values() if u'(' in v])
M[u'r_desc_nonascii'] = len([v for v in REG.values() if any(ord(ch) > 127 for ch in v)])
M[u'r_desc_dist'] = len(set(REG.values()))
M[u'r_desc_reuse'] = M[u'r_region_n'] - M[u'r_desc_dist']

# ---------- 三向码集账 ----------
IS, ZS, RS = set(CODE), set(CC), set(REG)
M[u'inter3'] = len(IS & ZS & RS)
M[u'z_in_i'] = len(ZS & IS)
M[u'z_only_i'] = sorted(ZS - IS)
M[u'i_only_z'] = sorted(IS - ZS)
M[u'i_only_z_n'] = len(IS - ZS)
M[u'z_only_i_n'] = len(ZS - IS)
M[u'i_in_r'] = len(IS & RS)
M[u'i_only_r'] = len(IS - RS)
M[u'r_only_i'] = len(RS - IS)
M[u'r_only_i_alpha'] = len([c for c in RS - IS if len(c) == 2])
M[u'r_only_i_digit'] = len([c for c in RS - IS if c.isdigit()])
M[u'r_only_i_range'] = len([c for c in RS - IS if u'..' in c])
M[u'r_only_i_sum'] = (M[u'r_only_i_alpha'] + M[u'r_only_i_digit'] + M[u'r_only_i_range']
                      - M[u'r_only_i'])
M[u'z_only_r_n'] = len(ZS - RS)
M[u'r_alpha_in_i'] = len([c for c in (IS & RS) if len(c) == 2])
M[u'r_alpha_close'] = M[u'r_alpha_in_i'] + M[u'r_only_i_alpha'] - M[u'r_alpha']
M[u'rz_alpha'] = len([c for c in RS - ZS if len(c) == 2])
M[u'rz_alpha_close'] = (M[u'r_only_i_alpha'] + M[u'i_only_z_n']) - M[u'rz_alpha']
# 桥: 本条量的 R−I 两位 ⇎ I−Z, 与 B55 契约里“region 两位不在 Z 国家列”应是同一枚数;
# 前提(Z⊆I, I 的两位全在 R)由 bridge_precond 量出, 不靠假设。
B55 = json.load(io.open(u'corpus/_b55flat.json', encoding='utf-8'))
M[u'bridge_precond'] = M[u'z_only_i_n'] + (M[u'i_code_n'] - M[u'i_in_r'])
M[u'alpha_gap_bridge'] = (M[u'r_only_i_alpha'] + M[u'i_only_z_n']) - B55[u'reg_alpha_only']

# ---------- 名字词汇账(同一枚码在两份表里的名串) ----------
SH = sorted(IS & RS)
M[u'name_cmp'] = len(SH)
EQ = [c for c in SH if NAME[CODE.index(c)] == REG[c]]
DIF = [c for c in SH if NAME[CODE.index(c)] != REG[c]]
M[u'name_eq'] = len(EQ)
M[u'name_dif'] = len(DIF)


def n2(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower().replace(u'&', u'and').replace(u'\u2019', u"'"))


LEX = [c for c in DIF if n2(NAME[CODE.index(c)]) == n2(REG[c])]
SEM = [c for c in DIF if n2(NAME[CODE.index(c)]) != n2(REG[c])]
M[u'name_lex'] = len(LEX)
M[u'name_sem'] = len(SEM)
M[u'name_lex_plus_sem'] = M[u'name_lex'] + M[u'name_sem'] - M[u'name_dif']
M[u'name_amp_all_lex'] = len([c for c in DIF if u'&' in NAME[CODE.index(c)]]) - \
    len([c for c in LEX if u'&' in NAME[CODE.index(c)]])
M[u'name_apos'] = len([c for c in LEX if u'\u2019' in NAME[CODE.index(c)]])
M[u'name_longer_r'] = len([c for c in DIF if len(REG[c]) > len(NAME[CODE.index(c)])])
M[u'name_longer_i'] = len([c for c in DIF if len(NAME[CODE.index(c)]) > len(REG[c])])
M[u'name_samelen'] = M[u'name_dif'] - M[u'name_longer_r'] - M[u'name_longer_i']
M[u'name_dif_chars'] = sum(len(REG[c]) - len(NAME[CODE.index(c)]) for c in DIF)
M[u'name_str_pool'] = len(set(NAME) & set(REG.values()))
M[u'i_dif_first'] = DIF[0]
M[u'i_dif_first_pair'] = [NAME[CODE.index(DIF[0])], REG[DIF[0]]]
M[u'sem_examples'] = [(c, NAME[CODE.index(c)], REG[c]) for c in SEM[:3]]
M[u'lex_examples'] = [(c, NAME[CODE.index(c)], REG[c]) for c in LEX[:3]]
# Z 也用到这批码, 但它没有名字列: 名字层在 Z 里以什么形态活着
ZD2 = [l.split(u'\t') for l in ZL_ if l.strip() and not l.startswith(u'#')]
TAILC, COMP, CMT = set(), set(), set()
for x in ZD2:
    p = x[2].split(u'/') if len(x) > 2 else []
    COMP.update(p)
    if p:
        TAILC.add(p[-1])
    for c in x[3:]:
        CMT.add(c)
HN = sorted(set(NAME) & set(n for n in set(NAME) if n in ZV))
M[u'z_name_hits'] = len(HN)
M[u'z_name_dist'] = len(set(NAME))
M[u'z_tail_comp'] = len([n for n in HN if n in TAILC])
M[u'z_mid_comp'] = len([n for n in HN if n in COMP and n not in TAILC])
M[u'z_cmt_only'] = len([n for n in HN if n not in COMP])
M[u'z_tier_close'] = M[u'z_tail_comp'] + M[u'z_mid_comp'] + M[u'z_cmt_only'] - M[u'z_name_hits']
M[u'z_name_cols'] = sorted(set(len(x) for x in ZD2))
US = [n for n in set(NAME) if u' ' in n]
M[u'z_space_names'] = len(US)
M[u'z_us_plain'] = len([n for n in US if n in ZV])
M[u'z_us_only'] = len([n for n in US if n not in ZV and n.replace(u' ', u'_') in ZV])
M[u'z_code_cmt'] = len([l for l in ZL_ if l.startswith(u'#@')])
# 同一个名字挂在两表的另一枚码上
OTHER = [(c, n, [k for k in REG if REG[k] == n]) for c, n in zip(CODE, NAME)
         if n in set(REG.values()) and n != REG.get(c)]
M[u'i_cross_code_names'] = len(OTHER)
M[u'i_cross_code_pairs'] = [(c, n, v) for (c, n, v) in OTHER]
M[u'i_amp_and_r'] = len([c for c in CODE if u'&' in NAME[CODE.index(c)]
                         and u' and ' in REG.get(c, u'')])
M[u'i_amp_close'] = M[u'i_amp_and_r'] - M[u'i_amp']
M[u'r_only_deprecated'] = len([c for c in RS - IS if any(
    d.get(u'Subtag') == c and u'Deprecated' in d for d in FD)])
M[u'r_shared_deprecated'] = len([c for c in IS & RS if any(
    d.get(u'Subtag') == c and u'Deprecated' in d for d in FD)])

# ---------- 关键串在三源的同现 ----------
KEYS = [u'ISO 3166', u'alpha-2', u'country', u'tab', u'Antigua', u'Czech', u'Turkey', u'Samoa',
        u'Netherlands', u'Virgin Islands', u'region', u'Description', u'Andorra', u'United Kingdom',
        u'public domain', u'Bonaire', u'Malvinas', u'Barbuda', u'Micronesia', u'Congo', u'timezone',
        u'Eggert', u'Olson', u'UTF-8', u'alpha']
KH = []
for k in KEYS:
    h = [i for i in range(3) if k in TXT[i]]
    KH.append((k, h))
M[u'key_n'] = len(KEYS)
M[u'key_3'] = len([x for x in KH if len(x[1]) == 3])
M[u'key_2'] = len([x for x in KH if len(x[1]) == 2])
M[u'key_1'] = len([x for x in KH if len(x[1]) == 1])
M[u'key_0'] = len([x for x in KH if not x[1]])
M[u'key_3names'] = [x[0] for x in KH if len(x[1]) == 3]
M[u'key_0names'] = [x[0] for x in KH if not x[1]]
M[u'key_sum'] = M[u'key_3'] + M[u'key_2'] + M[u'key_1'] + M[u'key_0'] - M[u'key_n']

# ---------- 注释的“同一句话”在三种口径下的同现 ----------
IC = [l.strip() for l in IL if l.startswith(u'#')]
ZC = [l.strip() for l in ZL_ if l.startswith(u'#')]
SI, SZ = set(x for x in IC if len(x) >= 4), set(x for x in ZC if len(x) >= 4)
M[u'cmt_line_shared'] = len(SI & SZ)
M[u'cmt_line_shared_v'] = sorted(SI & SZ)
M[u'cmt_lines'] = [len(IC), len(ZC), len([l for l in RL if l.startswith(u'#')])]
M[u'cmt_chars'] = [sum(len(x) for x in IC), sum(len(x) for x in ZC)]


def blob(ls):
    return re.sub(u'\\s+', u' ', u' '.join(x.lstrip(u'#').strip() for x in ls))


def sents(b):
    return [s.strip() for s in re.split(u'(?<=[.:]) (?=[A-Z(#])', b) if len(s.strip()) >= 8]


SBI, SBZ = sents(blob(IC)), sents(blob(ZC))
SH = sorted(set(SBI) & set(SBZ))
M[u'cmt_sent_n'] = [len(SBI), len(SBZ)]
M[u'cmt_sent_shared'] = len(SH)
M[u'cmt_sent_shared_v'] = SH
M[u'cmt_contig_both'] = len([s for s in SH if s in IV and s in ZV])
M[u'cmt_contig_i'] = len([s for s in SH if s in IV])
M[u'cmt_contig_z'] = len([s for s in SH if s in ZV])
M[u'cmt_contig_none'] = len([s for s in SH if s not in IV and s not in ZV])
CURLY = (u'\u2018', u'\u2019', u'\u201c', u'\u201d')
M[u'curly'] = [sum(t.count(x) for x in CURLY) for t in (IV, ZV, RV)]
M[u'cmt_sorted_word'] = [IV.count(u'sorted'), ZV.count(u'sorted'), RV.count(u'sorted')]

# ---------- 锚候选池 ----------
POOL = []
for l in IL:
    s = l.strip()
    if not s or s.startswith(u'#'):
        continue
    frag = s.split(u'\t')[1] if u'\t' in s else s
    if len(frag) >= 4:
        POOL.append((u'I', frag))
for l in IL:
    s = l.strip()
    if s.startswith(u'#') and len(s) >= 9:
        POOL.append((u'I', s))
for l in ZL_:
    s = l.strip()
    if s.startswith(u'#') and len(s) >= 9 and u'\t' not in s:
        POOL.append((u'Z', s))
for l in ZL_:
    if l.strip() and not l.startswith(u'#'):
        for f in l.split(u'\t'):
            if len(f.strip()) >= 8:
                POOL.append((u'Z', f.strip()))
for d in FD:
    if d.get(u'Type') != u'region':
        continue
    for k in (u'Subtag', u'Type', u'Added', u'Deprecated', u'Preferred-Value', u'Scope'):
        v = d.get(k, u'')
        if v and len(k) + len(v) + 2 >= 12:
            POOL.append((u'R', u'%s: %s' % (k, v)))
for d in FD:
    if d.get(u'Type') == u'region' and len(d.get(u'Description', u'')) >= 4:
        POOL.append((u'R', u'Description: ' + d[u'Description']))
    if d.get(u'Type') == u'region' and u'Comments' in d and len(d[u'Comments']) >= 14:
        POOL.append((u'R', u'Comments: ' + d[u'Comments']))
seen, UNIQ = set(), []
for t, x in POOL:
    if (t, x) in seen:
        continue
    seen.add((t, x))
    UNIQ.append((t, x))
CROSS = []
for t, x in UNIQ:
    hits = [i for i in range(3) if x in TXT[i]]
    CROSS.append((t, len(hits), x))
M[u'pool_n'] = len(CROSS)
M[u'pool_1'] = len([x for x in CROSS if x[1] == 1])
M[u'pool_2'] = len([x for x in CROSS if x[1] == 2])
M[u'pool_3'] = len([x for x in CROSS if x[1] == 3])
M[u'pool_0'] = len([x for x in CROSS if x[1] == 0])
M[u'pool_by_tag'] = dict((t, len([x for x in CROSS if x[0] == t])) for t in TAGS)
SEL3 = [x for x in CROSS if x[1] >= 2][:6]
M[u'sel3_n'] = len([x for x in CROSS if x[1] >= 2])

json.dump({u'meas': M, u'pool': [[a, b, c] for (a, b, c) in CROSS],
           u'sel': [c for (_, _, c) in SEL3], u'tags': TAGS, u'paths': PATHS, u'labels': LB},
          io.open(u'corpus/_b56meas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print(u'I %d 字节／%d 行／数据 %d 行／列 %s／注释 %d 行 %d 字符／制表符 %d(结构推得 %d, 差 %d)' % (
    M[u'bytes'][0], M[u'lines'][0], M[u'i_rows'], M[u'i_cols'], M[u'i_cmt_lines'], M[u'i_cmt_chars'],
    M[u'tabs'][0], M[u'i_tab_expect'], M[u'i_tab_diff']))
print(u'I 码 %d 枚(重复 %d) ⇎ 名 %d 种(重复 %d %s) ｜ 排序逆序 %d ｜ amp %d ⇎ 括号 %d ⇎ 缩写点 %d ⇎ 逗号 %d' % (
    M[u'i_code_dist'], M[u'i_code_dup'], M[u'i_name_dist'], M[u'i_name_dup'], M[u'i_name_dupv'],
    M[u'i_sorted_desc'], M[u'i_amp'], M[u'i_paren'], M[u'i_dot'], M[u'i_comma']))
print(u'I 注释的三条命名理由对数据: Samoa 两条 %d／%d 全在 ⇎ 名排序相隔 %d ⇎ 同干并置的相邻对 %d(种 %d, 多名的干 %d)' % (
    M[u'i_claim_samoa'], 2, M[u'i_samoa_adj'], M[u'i_stem_adj'], M[u'i_stem_kinds'], M[u'i_stem_multi']))
print(u'                 旧名三条 %d／3 命中 ⇎ 新名(Czechia/Türkiye/Turkiye)缺席 %d／3 ｜ 非 ASCII 名 %d 串 ⇎ 弯引号 %d ⇎ 严格 UTF-8 %d ⇎ 字节-字符 %d' % (
    M[u'i_claim_oldnames'], M[u'i_claim_absent'], M[u'i_nonascii_names'], M[u'i_apos_curly'],
    M[u'i_utf8_strict'], M[u'i_bytegap']))
print(u'Z %d 字节／数据 %d 行／制表符 %d(结构推 %d 差 %d) ｜ 国家码 %d 枚／出现 %d 次／多选行 %d(最多 %d 国)' % (
    M[u'bytes'][1], M[u'z_rows'], M[u'tabs'][1], M[u'z_tab_expect'], M[u'z_tab_diff'],
    M[u'z_cc_dist'], M[u'z_cc_occ'], M[u'z_multi_rows'], M[u'z_maxm']))
print(u'R %d 字节／%d 段 ⇎ region 型 %d 枚: 两位 %d ⇎ 数字 %d ⇎ 区间 %d ⇎ 其他 %d ｜ Description %d 种(复用 %d)' % (
    M[u'bytes'][2], M[u'r_segs'], M[u'r_region_n'], M[u'r_alpha'], M[u'r_digit'], M[u'r_range'],
    M[u'r_other'], M[u'r_desc_dist'], M[u'r_desc_reuse']))
print(u'码集三向: 三源共有 %d ｜ Z⇎I: Z 有 I 无 %d %s ⇎ I 有 Z 无 %d %s' % (
    M[u'inter3'], M[u'z_only_i_n'], M[u'z_only_i'], M[u'i_only_z_n'], M[u'i_only_z']))
print(u'        I⇎R: I 有 R 无 %d ⇎ R 有 I 无 %d(两位 %d ⇎ 数字 %d ⇎ 区间 %d, 相加校住 差 %d)' % (
    M[u'i_only_r'], M[u'r_only_i'], M[u'r_only_i_alpha'], M[u'r_only_i_digit'], M[u'r_only_i_range'],
    M[u'r_only_i_sum']))
print(u'        与 B55 那笔账接得上: 本条 R−I 两位 %d ＋ I−Z %d = %d ⇎ B55 契约的 R−Z 两位 %d(差 %d, 前提 Z⊆I ⇎ I 两位全在 R 计 %d 破绽)' % (
    M[u'r_only_i_alpha'], M[u'i_only_z_n'], M[u'r_only_i_alpha'] + M[u'i_only_z_n'],
    B55[u'reg_alpha_only'], M[u'alpha_gap_bridge'], M[u'bridge_precond']))
print(u'名字词汇(同码同名位比 %d 枚): 全等 %d ⇎ 不等 %d = 只换写法 %d ＋ 换词 %d(相加校住差 %d)' % (
    M[u'name_cmp'], M[u'name_eq'], M[u'name_dif'], M[u'name_lex'], M[u'name_sem'], M[u'name_lex_plus_sem']))
print(u'   不等里: 长名在 R %d ⇎ 在 I %d ⇎ 等长 %d ｜ 字符数净差 %d ｜ amp 类 %d(“只换写法”一档里多出 %d) ⇎ 弯引号 %d' % (
    M[u'name_longer_r'], M[u'name_longer_i'], M[u'name_samelen'], M[u'name_dif_chars'],
    M[u'name_amp_all_lex'] + len([c for c in LEX if '&' in NAME[CODE.index(c)]]), M[u'name_amp_all_lex'],
    M[u'name_apos']))
print(u'   首例 %s: %s ⇎ %s ｜ 字面名串在两表值集里共有 %d 种' % (
    M[u'i_dif_first'], M[u'i_dif_first_pair'][0], M[u'i_dif_first_pair'][1], M[u'name_str_pool']))
print(u'名字层在 Z: Z 的列数只有 %s(无名字列) ⇎ 但 %d／%d 枚 I 名在 Z 逐字出现: 路径末段 %d ⇎ 中间段 %d ⇎ 只在末列自由文本 %d(三档闭合 %d)' % (
    M[u'z_name_cols'], M[u'z_name_hits'], M[u'z_name_dist'], M[u'z_tail_comp'], M[u'z_mid_comp'],
    M[u'z_cmt_only'], M[u'z_tier_close']))
print(u'          带空格的名 %d 枚: 原样活着的 %d ⇎ 必须换成下划线才活着的 %d' % (
    M[u'z_space_names'], M[u'z_us_plain'], M[u'z_us_only']))
print(u'跨码同名 %d 例 %s ｜ I 的 & 名 %d 枚在 R 全是 “ and ”(%d, 闭合 %d)' % (
    M[u'i_cross_code_names'], M[u'i_cross_code_pairs'], M[u'i_amp'], M[u'i_amp_and_r'], M[u'i_amp_close']))
print(u'I 注释点名的六个“ISO 另有写法”串: 本表在用的 5 命中 %d ⇎ 本表避掉的 6 缺席 %d(两头校住 %d, 反而在场的 %d)' % (
    M[u'i_claim_used'], M[u'i_claim_avoided'], M[u'i_claim_open'], M[u'i_avoided_present']))
print(u'I 的注释自身: 注释 %d 行 %d 字符 ⇎ 列名注释藏在两条里(拆行 %d, 连写的 country-code 出现 %d 次) ⇎ 注释行里唯一带制表符的 %d 行' % (
    M[u'i_cmt_lines'], M[u'i_cmt_chars'], M[u'i_hdr_split'], IV.count(u'country-code'), M[u'i_tab_in_cmt']))
print(u'  注释里的 %d 个日期按行序 %s ⇎ 按值序 %s(行序逆 %d 处) ⇎ 闰日 %d 枚 ｜ URL %d 枚 ｜ 同干多名 %d 组, 名排序里连成块的 %d 组' % (
    len(M[u'i_dates']), BYPOS, M[u'i_dates'], M[u'i_date_unsorted'], M[u'i_leap_ok'], M[u'i_url'],
    M[u'i_stem_multi'], M[u'i_stem_contig']))
print(u'R 侧弃用账: R−I 那 %d 枚里带 Deprecated 的 %d 枚 ⇎ I 共有的 %d 枚里带弃用的 %d 枚' % (
    M[u'r_only_i'], M[u'r_only_deprecated'], M[u'inter3'], M[u'r_shared_deprecated']))
print(u'关键串 %d 枚: 三源同现 %d ⇎ 两源 %d ⇎ 单源 %d ⇎ 不中 %d(相加校住 %d) ｜ 三源名单 %s' % (
    M[u'key_n'], M[u'key_3'], M[u'key_2'], M[u'key_1'], M[u'key_0'], M[u'key_sum'], M[u'key_3names']))
print(u'注释的同一句话三种口径: I %d 行 ⇎ Z %d 行 ⇎ R %d 行 ｜ 整行逐字共用 %d 行(%s)' % (
    M[u'cmt_lines'][0], M[u'cmt_lines'][1], M[u'cmt_lines'][2], M[u'cmt_line_shared'],
    M[u'cmt_line_shared_v']))
print(u'  接行归一后共用句 %d 句(I %d ⇎ Z %d 句): 其中整句在两源都连续的 %d 句 ⇎ 只在 I 连续 %d ⇎ 只在 Z %d ⇎ 两边都被折行 %d' % (
    M[u'cmt_sent_shared'], M[u'cmt_sent_n'][0], M[u'cmt_sent_n'][1], M[u'cmt_contig_both'],
    M[u'cmt_contig_i'], M[u'cmt_contig_z'], M[u'cmt_contig_none']))
for s in M[u'cmt_sent_shared_v']:
    print(u'    · %s ｜ 连续在 I %d ⇎ Z %d' % (s[:74], s in IV, s in ZV))
print(u'  弯引号四类 I %d ⇎ Z %d ⇎ R %d ｜ “sorted”一词 I %d ⇎ Z %d ⇎ R %d' % (
    M[u'curly'][0], M[u'curly'][1], M[u'curly'][2],
    M[u'cmt_sorted_word'][0], M[u'cmt_sorted_word'][1], M[u'cmt_sorted_word'][2]))
print(u'锚候选池 %d 条(按标签 %s) ｜ 穿一源 %d ⇎ 两源 %d ⇎ 三源 %d ⇎ 不中 %d ｜ 穿≥2 源 %d 条 ｜ 落 corpus/_b56meas.json' % (
    M[u'pool_n'], M[u'pool_by_tag'], M[u'pool_1'], M[u'pool_2'], M[u'pool_3'], M[u'pool_0'], M[u'sel3_n']))
