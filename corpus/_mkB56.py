# -*- coding: utf-8 -*-
"""B56 建条目(第二遍现算, 三源): I = corpus/raw/tz/iso3166.tab(249 行两位码⇎英文名, 命名理由写在它自己的注释里)
⇎ Z = corpus/raw/tz/zone1970.tab(312 行, 第一列借同一批码, 但它没有名字列) ⇎ R = corpus/raw/langsubtag.txt 的 region 型切片
(同一批码的超集: 两位 272 ⇎ 三位数字 31 ⇎ 区间 2)。
主轴两条: ①同一批码的“名字层”在三处各有存在形态——I 写成列、Z 只写成标识符片段或自由文本、R 写成 Description,
于是一份表里改一个连字符、换一个撇号、把一个词挪到别的码上, 都是可判的跨源事实;
②同一批码的“集含方向”——Z⊆I⊆R(两位档) 三向差集全闭合, 并与 B55 的 region⇎国家列那笔账接得上。
第二遍的独立性: 本文件用“逐行严格正则”解析 I(pick 用 split 制表符), 用 re.split 切 R 的段(pick 用逐行状态机),
注释共用句用“接行归一再断句”这套 pick 里没有的算法; 每个数在 TIE 表上与 _pick56.py 逐量对账, 不符即停机。
门槛内 _b56_scan 是第三遍, 锚归属由条目正文现推。磁盘 mtime、哪个入口抓到这些文件不可由在库文件判定, 进注不进门槛。"""
import io, os, re, sys, json, hashlib, collections

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = u'%s/babeltele/B56_three_tables_one_code_batch.md' % C
J = json.load(io.open(u'corpus/_b56meas.json', encoding='utf-8'))
MM, POOLP = J[u'meas'], J[u'pool']
TAGS, PATH = J[u'tags'], J[u'paths']
LB = dict(zip(TAGS, [u'码表', u'时区表', u'子标签注册表']))
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATH]
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN ---


def pnorm(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


F = {}


def two(name, f):
    F[name] = [f(k) for k in range(3)]


two(u'bytes', lambda i: os.path.getsize(PATH[i]))
two(u'chars', lambda i: len(TXT[i]))
two(u'lines', lambda i: TXT[i].count(NL))
two(u'segments', lambda i: len(TXT[i].split(NL)))
two(u'nonblank', lambda i: len(re.findall(u'^\\s*\\S', TXT[i], re.M)))
two(u'lt', lambda i: TXT[i].count(u'<'))
two(u'gt', lambda i: TXT[i].count(u'>'))
two(u'nonascii', lambda i: len([c for c in TXT[i] if ord(c) > 127]))
two(u'tabs', lambda i: TXT[i].count(u'\t'))
two(u'hash', lambda i: len(re.findall(u'^#', TXT[i], re.M)))
two(u'curly', lambda i: sum(TXT[i].count(x) for x in (u'\u2018', u'\u2019', u'\u201c', u'\u201d')))
two(u'sha16', lambda i: hashlib.sha256(io.open(PATH[i], 'rb').read()).hexdigest()[:16])
F[u'blank'] = [F[u'segments'][i] - F[u'nonblank'][i] for i in range(3)]
F[u'ascii_eq'] = [1 if F[u'nonascii'][i] == 0 else 0 for i in range(3)]
F[u'eqc'] = sum(F[u'ascii_eq'])
F[u'sha_distinct'] = len(set(F[u'sha16']))
F[u'bytegap'] = [F[u'bytes'][i] - F[u'chars'][i] for i in range(3)]
F[u'ratio'] = [int(round(1.0 * F[u'bytes'][i] / F[u'bytes'][0])) for i in range(3)]
F[u'curly_close'] = sum(F[u'curly']) - (F[u'curly'][1] + F[u'curly'][0] + F[u'curly'][2])

LS = [t.split(NL) for t in TXT]
DATA = [[l for l in LS[i] if l.strip() and not l.startswith(u'#')] for i in range(3)]
CMT = [[l for l in LS[i] if l.startswith(u'#')] for i in range(3)]

# ---------- I: 严格两列正则(pick 用 split, 这里换一个判法) ----------
IM = [re.match(u'^([A-Z]{2})\t([^\t]+)$', l) for l in LS[0]]
IROWS = [m for m in IM if m]
F[u'i_rows_strict'] = len(IROWS)
F[u'i_rows_data'] = len(DATA[0])
F[u'i_rows_unmatched'] = F[u'i_rows_data'] - F[u'i_rows_strict']
F[u'i_multi_tab'] = len([l for l in DATA[0] if l.count(u'\t') > 1])
CODE = [m.group(1) for m in IROWS]
NAME = [m.group(2) for m in IROWS]
F[u'i_cols'] = [2]
F[u'i_code_n'] = len(CODE)
F[u'i_code_dist'] = len(set(CODE))
F[u'i_code_dup'] = F[u'i_code_n'] - F[u'i_code_dist']
F[u'i_name_dist'] = len(set(NAME))
F[u'i_name_dup'] = len(NAME) - len(set(NAME))
F[u'i_sorted_desc'] = len([i for i in range(1, len(CODE)) if CODE[i] < CODE[i - 1]])
F[u'i_amp'] = len([n for n in NAME if u'&' in n])
F[u'i_paren'] = len([n for n in NAME if u'(' in n])
F[u'i_dot'] = len([n for n in NAME if u'.' in n])
F[u'i_comma'] = len([n for n in NAME if u',' in n])
F[u'i_apos'] = len([n for n in NAME if u'\u2019' in n])
F[u'i_nonascii_names'] = len([n for n in NAME if any(ord(ch) > 127 for ch in n)])
F[u'i_name_chars'] = sum(len(n) for n in NAME)
F[u'i_maxlen'] = max(len(n) for n in NAME)
F[u'i_minlen'] = min(len(n) for n in NAME)
F[u'i_maxlen_v'] = [n for n in NAME if len(n) == F[u'i_maxlen']]
F[u'i_cmt_lines'] = len(CMT[0])
F[u'i_cmt_chars'] = sum(len(l) for l in CMT[0])
F[u'i_cmt_tab_lines'] = len([l for l in CMT[0] if u'\t' in l])
F[u'i_tab_expect'] = F[u'i_rows_strict'] + F[u'i_cmt_tab_lines']
F[u'i_tab_diff'] = F[u'i_tab_expect'] - F[u'tabs'][0]
F[u'i_utf8_strict'] = 1
try:
    io.open(PATH[0], 'rb').read().decode(u'utf-8')
except UnicodeDecodeError:
    F[u'i_utf8_strict'] = 0
F[u'i_url'] = len(re.findall(u'https?://', TXT[0]))
F[u'i_dates'] = sorted(set(re.findall(r'\d{4}-\d{2}-\d{2}', TXT[0])))
F[u'i_dates_byline'] = [d for (_, d) in sorted((TXT[0].find(d), d) for d in F[u'i_dates'])]
F[u'i_date_unsorted'] = len([i for i in range(1, len(F[u'i_dates_byline']))
                             if F[u'i_dates_byline'][i] < F[u'i_dates_byline'][i - 1]])
F[u'i_leap'] = len([d for d in F[u'i_dates'] if d.endswith(u'-02-29')])
F[u'i_hdr_split'] = 1 if (u'#country-' + NL + u'#code' in TXT[0] and u'country-code' not in TXT[0]) else 0
F[u'i_hdr_cc'] = TXT[0].count(u'country-code')

# 注释自写的三条命名理由逐条交给数据判
SN = sorted(NAME)
USED = [u'Samoa (American)', u'Samoa (western)', u'Czech Republic', u'Turkey', u'Netherlands']
AVOID = [u'American Samoa', u'Samoa', u'Czechia', u'Türkiye', u'Netherlands (the)',
         u'Netherlands (Kingdom of the)']
F[u'i_claim_used'] = len([w for w in USED if w in NAME])
F[u'i_claim_avoided'] = len([w for w in AVOID if w not in NAME])
F[u'i_claim_avoided_in'] = len([w for w in AVOID if w in NAME])
F[u'i_claim_total'] = len(USED) + len(AVOID)
F[u'i_claim_open'] = (F[u'i_claim_used'] + F[u'i_claim_avoided']) - F[u'i_claim_total']
F[u'i_samoa_gap'] = abs(SN.index(u'Samoa (western)') - SN.index(u'Samoa (American)')) - 1
STEM = [n.split(u' (')[0] for n in SN]


def sidx(s):
    return [i for i, x in enumerate(SN) if x.split(u' (')[0] == s]


MULTI = [s for s in set(STEM) if STEM.count(s) > 1]
F[u'i_stem_kinds'] = len(set(STEM))
F[u'i_stem_multi'] = len(MULTI)
F[u'i_stem_adj'] = len([i for i in range(1, len(SN)) if STEM[i] == STEM[i - 1]])
F[u'i_stem_contig'] = len([s for s in MULTI if sidx(s)[-1] - sidx(s)[0] + 1 == len(sidx(s))])
F[u'i_stem_close'] = F[u'i_stem_contig'] - F[u'i_stem_multi']
F[u'i_multi_skins'] = len(MULTI) - len([s for s in MULTI if s in SN])

# ---------- Z: 同一批码, 没有名字列 ----------
ZD = [l.split(u'\t') for l in DATA[1]]
F[u'z_rows'] = len(ZD)
F[u'z_cols'] = sorted(set(len(x) for x in ZD))
F[u'z_col3'] = len([x for x in ZD if len(x) == 3])
F[u'z_col4'] = len([x for x in ZD if len(x) > 3])
CC = [c for x in ZD for c in x[0].split(u',')]
F[u'z_cc_occ'] = len(CC)
F[u'z_cc_dist'] = len(set(CC))
F[u'z_multi_rows'] = len([x for x in ZD if u',' in x[0]])
F[u'z_maxm'] = max(len(x[0].split(u',')) for x in ZD)
F[u'z_at'] = len([l for l in LS[1] if l.startswith(u'#@')])
IS, ZS = set(CODE), set(CC)
HN = sorted([n for n in set(NAME) if n in TXT[1]])
TAILC, COMP, CMT4 = set(), set(), set()
for x in ZD:
    if len(x) > 2:
        parts = x[2].split(u'/')
        COMP.update(parts)
        TAILC.add(parts[-1])
    for c in x[3:]:
        CMT4.add(c)
F[u'z_name_hits'] = len(HN)
F[u'z_tail_comp'] = len([n for n in HN if n in TAILC])
F[u'z_mid_comp'] = len([n for n in HN if n in COMP and n not in TAILC])
F[u'z_cmt_only'] = len([n for n in HN if n not in COMP])
F[u'z_tier_close'] = (F[u'z_tail_comp'] + F[u'z_mid_comp'] + F[u'z_cmt_only']) - F[u'z_name_hits']
SP = [n for n in set(NAME) if u' ' in n]
F[u'z_space_names'] = len(SP)
F[u'z_us_plain'] = len([n for n in SP if n in TXT[1]])
F[u'z_us_only'] = len([n for n in SP if n not in TXT[1] and n.replace(u' ', u'_') in TXT[1]])
F[u'z_us_close'] = (F[u'z_us_plain'] + F[u'z_us_only']) - len([n for n in SP if n in TXT[1]
                                                              or n.replace(u' ', u'_') in TXT[1]])

# ---------- R: region 型切片(re.split 切段, pick 用逐行状态机) ----------
RB = re.split(u'\n%%\n', TXT[2])
F[u'r_recs'] = len(RB)
F[u'r_sep'] = len([l for l in LS[2] if l.strip() == u'%%'])
F[u'r_sep_gap'] = F[u'r_recs'] - 1 - F[u'r_sep']


def rf(b):
    return dict(re.findall(u'^([A-Za-z][A-Za-z-]*):[ ]?(.*)$', b, re.M))


RECS = [rf(b) for b in RB]
F[u'r_region_n'] = len([d for d in RECS if d.get(u'Type') == u'region'])
REG = dict((d[u'Subtag'], d.get(u'Description', u'')) for d in RECS if d.get(u'Type') == u'region')
DEPD = set(d[u'Subtag'] for d in RECS if d.get(u'Type') == u'region' and u'Deprecated' in d)
PREFV = dict((d[u'Subtag'], d.get(u'Preferred-Value', u''))
             for d in RECS if d.get(u'Type') == u'region')
RS = set(REG)
F[u'r_alpha'] = len([c for c in RS if len(c) == 2])
F[u'r_digit'] = len([c for c in RS if len(c) == 3 and c.isdigit()])
F[u'r_range'] = len([c for c in RS if u'..' in c])
F[u'r_len_close'] = (F[u'r_alpha'] + F[u'r_digit'] + F[u'r_range']) - F[u'r_region_n']
F[u'r_desc_dist'] = len(set(REG.values()))
F[u'r_desc_reuse'] = F[u'r_region_n'] - F[u'r_desc_dist']
F[u'r_amp_desc'] = len([v for v in REG.values() if u'&' in v])

# ---------- 三向集含 ----------
F[u'inter3'] = len(IS & ZS & RS)
F[u'z_only_i'] = len(ZS - IS)
F[u'i_only_z'] = len(IS - ZS)
F[u'i_only_r'] = len(IS - RS)
F[u'r_only_i'] = len(RS - IS)
F[u'r_only_i_alpha'] = len([c for c in RS - IS if len(c) == 2])
F[u'r_only_i_digit'] = len([c for c in RS - IS if len(c) == 3 and c.isdigit()])
F[u'r_only_i_range'] = len([c for c in RS - IS if u'..' in c])
F[u'r_only_i_close'] = (F[u'r_only_i_alpha'] + F[u'r_only_i_digit'] + F[u'r_only_i_range']) - F[u'r_only_i']
F[u'r_alpha_in_i'] = len([c for c in IS & RS if len(c) == 2])
F[u'r_alpha_close'] = (F[u'r_alpha_in_i'] + F[u'r_only_i_alpha']) - F[u'r_alpha']
F[u'rz_alpha'] = len([c for c in RS - ZS if len(c) == 2])
F[u'bridge'] = (F[u'r_only_i_alpha'] + F[u'i_only_z']) - F[u'rz_alpha']
F[u'z_in_i_close'] = (F[u'inter3'] + F[u'z_only_i']) - F[u'z_cc_dist']
F[u'i_in_r'] = len(IS & RS)
F[u'r_segs_nonempty'] = len([b for b in RB if b.strip()])
F[u'i_in_r_close'] = (F[u'i_in_r'] + F[u'i_only_r']) - F[u'i_code_n']
F[u'r_only_dep'] = len([c for c in RS - IS if c in DEPD])
F[u'shared_dep'] = len([c for c in IS & RS if c in DEPD])
F[u'dep_total'] = len(DEPD)
F[u'dep_close'] = (F[u'r_only_dep'] + F[u'shared_dep']) - F[u'dep_total']
F[u'z_i_pairs'] = sorted(IS - ZS)
F[u'r_i_alpha_v'] = sorted([c for c in RS - IS if len(c) == 2])

# ---------- 名字词汇账: 同一枚码在两份表里 ----------
SH = sorted(IS & RS)
F[u'name_cmp'] = len(SH)
N = dict(zip(CODE, NAME))
EQ = [c for c in SH if N[c] == REG[c]]
DIF = [c for c in SH if N[c] != REG[c] and c in REG]


def n2(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower().replace(u'&', u'and').replace(u'\u2019', "'"))


LEX = [c for c in DIF if n2(N[c]) == n2(REG[c])]
SEM = [c for c in DIF if n2(N[c]) != n2(REG[c])]
F[u'name_eq'] = len(EQ)
F[u'name_dif'] = len(DIF)
F[u'name_lex'] = len(LEX)
F[u'name_sem'] = len(SEM)
F[u'name_lex_close'] = (F[u'name_lex'] + F[u'name_sem']) - F[u'name_dif']
F[u'name_cmp_close'] = (F[u'name_eq'] + F[u'name_dif']) - F[u'name_cmp']
F[u'name_longer_r'] = len([c for c in DIF if len(REG[c]) > len(N[c])])
F[u'name_longer_i'] = len([c for c in DIF if len(N[c]) > len(REG[c])])
F[u'name_samelen'] = len([c for c in DIF if len(N[c]) == len(REG[c])])
F[u'name_len_close'] = (F[u'name_longer_r'] + F[u'name_longer_i'] + F[u'name_samelen']) - F[u'name_dif']
F[u'name_dif_chars'] = sum(len(REG[c]) - len(N[c]) for c in DIF)
F[u'name_amp_both'] = len([c for c in CODE if u'&' in N[c] and u' and ' in REG.get(c, u'')])
F[u'name_amp_all'] = len([c for c in DIF if u'&' in N[c]])
F[u'name_amp_close'] = F[u'name_amp_both'] - F[u'i_amp']
F[u'name_lex_amp'] = len([c for c in LEX if u'&' in N[c]])
F[u'name_apos_lex'] = len([c for c in LEX if u'\u2019' in N[c]])
F[u'name_str_pool'] = len(set(NAME) & set(REG.values()))
XR = [(c, N[c], sorted([k for k in REG if REG[k] == N[c] and k != c]))
      for c in CODE if N[c] in set(REG.values()) and N[c] != REG.get(c)]
F[u'name_cross'] = len(XR)
F[u'name_cross_v'] = [[c, n, v] for (c, n, v) in XR]
F[u'name_pool_close'] = (F[u'name_eq'] + F[u'name_cross']) - F[u'name_str_pool']
F[u'name_first_diff'] = [DIF[0], N[DIF[0]], REG[DIF[0]]]
F[u'sem_ex'] = [(c, N[c], REG[c]) for c in SEM[:2]]
F[u'lex_ex'] = [(c, N[c], REG[c]) for c in LEX[:2]]

# ---------- 注释的“同一句话”: 整行 ⇎ 接行断句 ⇎ 逐字连续 ----------
SI = set(l.strip() for l in CMT[0] if len(l.strip()) >= 4)
SZ = set(l.strip() for l in CMT[1] if len(l.strip()) >= 4)
F[u'cmt_lines'] = [len(CMT[i]) for i in range(3)]
F[u'cmt_line_shared'] = len(SI & SZ)
F[u'cmt_line_shared_v'] = sorted(SI & SZ)


def blob(ls):
    return re.sub(u'\\s+', u' ', u' '.join(x.lstrip(u'#').strip() for x in ls))


def sents(b):
    return [s.strip() for s in re.split(u'(?<=[.:]) (?=[A-Z(#])', b) if len(s.strip()) >= 8]


SBI, SBZ = sents(blob(CMT[0])), sents(blob(CMT[1]))
CSH = sorted(set(SBI) & set(SBZ))
F[u'cmt_sent_n'] = [len(SBI), len(SBZ)]
F[u'cmt_sent_shared'] = len(CSH)
F[u'cmt_sent_shared_v'] = CSH
F[u'cmt_contig_both'] = len([s for s in CSH if s in TXT[0] and s in TXT[1]])
F[u'cmt_contig_i'] = len([s for s in CSH if s in TXT[0] and s not in TXT[1]])
F[u'cmt_contig_z'] = len([s for s in CSH if s in TXT[1] and s not in TXT[0]])
F[u'cmt_contig_none'] = len([s for s in CSH if s not in TXT[0] and s not in TXT[1]])
F[u'cmt_contig_close'] = (F[u'cmt_contig_both'] + F[u'cmt_contig_i'] + F[u'cmt_contig_z']
                          + F[u'cmt_contig_none']) - F[u'cmt_sent_shared']
F[u'cmt_sorted_word'] = [TXT[i].count(u'sorted') for i in range(3)]

# ---------- 关键串矩阵 ⇎ 锚候选池 ----------
CROSSK = [u'ISO 3166', u'alpha-2', u'country', u'tab', u'Antigua', u'Czech', u'Turkey', u'Samoa',
          u'Netherlands', u'Virgin Islands', u'region', u'Description', u'Andorra', u'United Kingdom',
          u'public domain', u'Bonaire', u'Malvinas', u'Barbuda', u'Micronesia', u'Congo', u'timezone',
          u'Eggert', u'Olson', u'UTF-8', u'alpha']
FAN = [pnorm(t) for t in TXT]
KH = [(k, tuple(i for i in range(3) if k in TXT[i])) for k in CROSSK]
F[u'key_n'] = len(CROSSK)
F[u'key_3'] = len([x for x in KH if len(x[1]) == 3])
F[u'key_2'] = len([x for x in KH if len(x[1]) == 2])
F[u'key_1'] = len([x for x in KH if len(x[1]) == 1])
F[u'key_0'] = len([x for x in KH if not x[1]])
F[u'key_close'] = (F[u'key_3'] + F[u'key_2'] + F[u'key_1'] + F[u'key_0']) - F[u'key_n']
F[u'key_3names'] = [x[0] for x in KH if len(x[1]) == 3]
F[u'key_IZ'] = len([x for x in KH if set(x[1]) == {0, 1}])
F[u'key_IR'] = len([x for x in KH if set(x[1]) == {0, 2}])
F[u'key_ZR'] = len([x for x in KH if set(x[1]) == {1, 2}])
F[u'key_pair_close'] = (F[u'key_IZ'] + F[u'key_IR'] + F[u'key_ZR']) - F[u'key_2']
# 锚候选池在本遍独立重建(pick 的池只用来取锚串, 池的条数在这里重算并与 pick 对账):
# 两份 tzdb 表取“数据行的非首格”与“够长的注释行”, 注册表取 region 型记录的六个字段行与 Description/Comments。
POOL = []


def addpool(t, x):
    if x and x not in [y for (u_, y) in POOL if u_ == t]:
        POOL.append((t, x))


for l in LS[0]:
    s = l.strip()
    if not s:
        continue
    if s.startswith(u'#'):
        addpool(u'I', s) if len(s) >= 9 else None
    elif u'	' in s:
        addpool(u'I', s.split(u'	')[1]) if len(s.split(u'	')[1]) >= 4 else None
    else:
        addpool(u'I', s) if len(s) >= 4 else None
for l in LS[1]:
    s = l.strip()
    if not s:
        continue
    if s.startswith(u'#'):
        if len(s) >= 9 and u'	' not in s:
            addpool(u'Z', s)
    else:
        for f in s.split(u'	'):
            if len(f) >= 8:
                addpool(u'Z', f)
for d in RECS:
    if d.get(u'Type') != u'region':
        continue
    for k in (u'Subtag', u'Type', u'Added', u'Deprecated', u'Preferred-Value', u'Scope'):
        v = d.get(k, u'')
        if v and len(k) + len(v) + 2 >= 12:
            addpool(u'R', u'%s: %s' % (k, v))
    if len(d.get(u'Description', u'')) >= 4:
        addpool(u'R', u'Description: ' + d[u'Description'])
    if len(d.get(u'Comments', u'')) >= 14:
        addpool(u'R', u'Comments: ' + d[u'Comments'])
POOL = [(t, len([1 for k in range(3) if x in TXT[k]]), x) for (t, x) in POOL]

F[u'pool_n'] = len(POOL)
F[u'poolI'] = len([p for p in POOL if p[0] == u'I'])
F[u'poolZ'] = len([p for p in POOL if p[0] == u'Z'])
F[u'poolR'] = len([p for p in POOL if p[0] == u'R'])
F[u'pool_1'] = len([p for p in POOL if p[1] == 1])
F[u'pool_2'] = len([p for p in POOL if p[1] == 2])
F[u'pool_3'] = len([p for p in POOL if p[1] == 3])
F[u'pool_close'] = (F[u'pool_1'] + F[u'pool_2'] + F[u'pool_3']) - F[u'pool_n']
F[u'pool_cross'] = F[u'pool_2'] + F[u'pool_3']

# --- SCAN END ---

TIE = [(u'bytes', u'bytes', None), (u'chars', u'chars', None), (u'lines', u'lines', None),
       (u'segments', u'segments', None), (u'lt', u'lt', None), (u'gt', u'gt', None),
       (u'nonascii', u'nonascii', None), (u'tabs', u'tabs', None), (u'hash', u'hash', None),
       (u'curly', u'curly', None),
       (u'nonblank', u'nonblank', None), (u'blank', u'blank', None),
       (u'i_rows_strict', u'i_rows', None), (u'i_code_n', u'i_code_n', None),
       (u'i_code_dist', u'i_code_dist', None), (u'i_code_dup', u'i_code_dup', None),
       (u'i_name_dist', u'i_name_dist', None), (u'i_name_dup', u'i_name_dup', None),
       (u'i_sorted_desc', u'i_sorted_desc', None), (u'i_amp', u'i_amp', None),
       (u'i_paren', u'i_paren', None), (u'i_dot', u'i_dot', None), (u'i_comma', u'i_comma', None),
       (u'i_nonascii_names', u'i_nonascii_names', None), (u'i_apos', u'i_apos_curly', None),
       (u'i_name_chars', u'i_name_chars', None), (u'i_maxlen', u'i_maxlen', None),
       (u'i_minlen', u'i_minlen', None), (u'i_cmt_lines', u'i_cmt_lines', None),
       (u'i_cmt_chars', u'i_cmt_chars', None), (u'i_cmt_tab_lines', u'i_tab_in_cmt', None),
       (u'i_tab_expect', u'i_tab_expect', None), (u'i_tab_diff', u'i_tab_diff', None),
       (u'i_url', u'i_url', None), (u'i_dates', u'i_dates', None),
       (u'i_dates_byline', u'i_dates_byline', None), (u'i_date_unsorted', u'i_date_unsorted', None),
       (u'i_leap', u'i_leap_ok', None), (u'i_hdr_split', u'i_hdr_split', None),
       (u'i_utf8_strict', u'i_utf8_strict', None), (u'i_claim_used', u'i_claim_used', None),
       (u'i_claim_avoided', u'i_claim_avoided', None), (u'i_claim_avoided_in', u'i_avoided_present', None),
       (u'i_samoa_gap', u'i_samoa_adj', None), (u'i_stem_kinds', u'i_stem_kinds', None),
       (u'i_stem_multi', u'i_stem_multi', None), (u'i_stem_adj', u'i_stem_adj', None),
       (u'i_stem_contig', u'i_stem_contig', None), (u'z_rows', u'z_rows', None),
       (u'z_cols', u'z_cols', None), (u'z_col3', u'z_col3', None), (u'z_col4', u'z_col4', None),
       (u'z_cc_occ', u'z_cc_occ', None), (u'z_cc_dist', u'z_cc_dist', None),
       (u'z_multi_rows', u'z_multi_rows', None), (u'z_maxm', u'z_maxm', None),
       (u'z_at', u'z_code_cmt', None), (u'z_name_hits', u'z_name_hits', None),
       (u'z_tail_comp', u'z_tail_comp', None), (u'z_mid_comp', u'z_mid_comp', None),
       (u'z_cmt_only', u'z_cmt_only', None), (u'z_space_names', u'z_space_names', None),
       (u'z_us_plain', u'z_us_plain', None), (u'z_us_only', u'z_us_only', None),
       (u'r_segs_nonempty', u'r_segs', None), (u'r_recs', u'r_segs', 0), (u'r_sep', u'r_sep', None), (u'r_region_n', u'r_region_n', None),
       (u'r_alpha', u'r_alpha', None), (u'r_digit', u'r_digit', None), (u'r_range', u'r_range', None),
       (u'r_desc_dist', u'r_desc_dist', None), (u'inter3', u'inter3', None),
       (u'z_only_i', u'z_only_i_n', None), (u'i_only_z', u'i_only_z_n', None),
       (u'i_only_r', u'i_only_r', None), (u'r_only_i', u'r_only_i', None),
       (u'r_only_i_alpha', u'r_only_i_alpha', None), (u'r_only_i_digit', u'r_only_i_digit', None),
       (u'r_only_i_range', u'r_only_i_range', None), (u'r_alpha_in_i', u'r_alpha_in_i', None),
       (u'rz_alpha', u'rz_alpha', None), (u'name_cmp', u'name_cmp', None),
       (u'name_eq', u'name_eq', None), (u'name_dif', u'name_dif', None),
       (u'name_lex', u'name_lex', None), (u'name_sem', u'name_sem', None),
       (u'name_longer_r', u'name_longer_r', None), (u'name_longer_i', u'name_longer_i', None),
       (u'name_samelen', u'name_samelen', None), (u'name_dif_chars', u'name_dif_chars', None),
       (u'name_str_pool', u'name_str_pool', None), (u'name_cross', u'i_cross_code_names', None),
       (u'cmt_lines', u'cmt_lines', None),
       (u'cmt_line_shared', u'cmt_line_shared', None), (u'cmt_sent_n', u'cmt_sent_n', None),
       (u'cmt_sent_shared', u'cmt_sent_shared', None), (u'cmt_contig_both', u'cmt_contig_both', None),
       (u'cmt_contig_none', u'cmt_contig_none', None), (u'cmt_sorted_word', u'cmt_sorted_word', None),
       (u'key_n', u'key_n', None), (u'key_3', u'key_3', None), (u'key_2', u'key_2', None),
       (u'key_1', u'key_1', None), (u'pool_n', u'pool_n', None), (u'pool_1', u'pool_1', None),
       (u'pool_2', u'pool_2', None), (u'pool_3', u'pool_3', None),
       (u'name_amp_all', u'name_amp_and_r', None), (u'i_in_r', u'i_in_r', None)]
TIE = [t for t in TIE if t[1] in MM]


def mv(mk, ix):
    v = MM[mk]
    if ix is None:
        return v
    return v[ix] if isinstance(v, list) else v


BADK = [(bk, F[bk], mv(mk, ix)) for bk, mk, ix in TIE if F[bk] != mv(mk, ix)]
assert not BADK, BADK[:8]
assert len(TIE) >= 95, len(TIE)
assert F[u'i_rows_unmatched'] == 0 and F[u'i_multi_tab'] == 0 and F[u'i_tab_diff'] == 0
assert F[u'i_claim_open'] == 0 and F[u'i_stem_close'] == 0 and F[u'i_samoa_gap'] == 0
assert F[u'i_code_dup'] == 0 and F[u'i_name_dup'] == 0 and F[u'i_sorted_desc'] == 0
assert F[u'z_tier_close'] == 0 and F[u'z_us_close'] == 0
assert F[u'r_len_close'] == 0 and F[u'r_only_i_close'] == 0 and F[u'r_alpha_close'] == 0
assert F[u'bridge'] == 0 and F[u'z_in_i_close'] == 0 and F[u'i_in_r_close'] == 0
assert F[u'dep_close'] == 0 and F[u'shared_dep'] == 0 and F[u'z_only_i'] == 0 and F[u'i_only_r'] == 0
assert F[u'name_lex_close'] == 0 and F[u'name_cmp_close'] == 0 and F[u'name_len_close'] == 0
assert F[u'name_pool_close'] == 0 and F[u'name_amp_close'] == 0 and F[u'r_sep_gap'] == 0
assert F[u'cmt_contig_close'] == 0 and F[u'key_close'] == 0 and F[u'key_pair_close'] == 0
assert F[u'pool_close'] == 0 and F[u'curly_close'] == 0
assert F[u'ascii_eq'] == [0, 0, 0] and F[u'i_utf8_strict'] == 1 and F[u'i_leap'] == 1
assert len(set(F[u'sha16'])) == 3 and F[u'eqc'] == 0
assert F[u'i_hdr_split'] == 1 and F[u'i_hdr_cc'] == 0 and F[u'cmt_line_shared'] == 1
assert F[u'cmt_sent_shared'] == 4 and F[u'cmt_contig_both'] == 1
assert F[u'name_lex'] == 10 and F[u'name_cross'] == 2
assert F[u'name_amp_all'] == 11 and F[u'name_lex_amp'] == 8 and F[u'curly'][0] == 25
assert F[u'sha_distinct'] == 3 and F[u'r_segs_nonempty'] > 0
assert F[u'z_cc_dist'] + F[u'i_only_z'] == F[u'i_code_n']
assert F[u'bytegap'][0] == MM[u'i_bytegap'] and F[u'bytegap'] == [55, 56, 742]

K, ZERO, COLL, SEENX = {}, [], {}, {}


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K.setdefault(s, (expr, note))


def dump_deriv():
    out = dict((k, v[0]) for k, v in K.items())
    for k, exprs in SEENX.items():
        if len(exprs) > 1:
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
    return out


def V(name, i=None, note=u''):
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"B56V('%s'%s)" % (name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def EXPR(s, expr, note):
    reg(s, expr, note)
    return s


TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


def ATOMSEL(kind, tag, *needles):
    ok = (lambda n: n == 1) if kind == u'own' else (lambda n: n == int(kind[1:]))
    got = [p for p in POOLP if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
    assert got, (kind, tag, needles)
    return max(got, key=lambda x: (len(x[2]), x[2]))


USEDATOM = []


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    USEDATOM.append(x[2])
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


def JOIN(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LB[t])) for i, t in enumerate(TAGS))


G = {}
LINES = []
MISSING = []


class _Ctx(dict):
    def __missing__(self, k):
        MISSING.append(k)
        return u'§' + k


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + tmpl).format_map(_Ctx(dict(G, **kw))))


# ---------- 锚 ----------
G[u'aPub'] = AT(u'own', u'I', u'public domain')
G[u'aClar'] = AT(u'own', u'I', u'clarified as of')
G[u'aHdr1'] = AT(u'own', u'I', u'alpha-2 country code, current as of')
G[u'aUrl'] = AT(u'own', u'I', u'iso.org/committee')
G[u'aUsual'] = AT(u'own', u'I', u'usual English name')
G[u'aSorted'] = AT(u'own', u'I', u'sorted by country code')
G[u'aTerr'] = AT(u'own', u'I', u'territorial claims')
G[u'aColHdr'] = AT(u'own', u'I', u'name of country, territory')
G[u'aCountry'] = AT(u'J2', u'I', u'country-')
G[u'aLeap'] = AT(u'own', u'I', u'2024-02-29')
G[u'aEggert'] = AT(u'own', u'I', u'Paul Eggert')
G[u'aSamoa'] = AT(u'own', u'I', u'Samoa (American)')
G[u'aCzech'] = AT(u'own', u'I', u'Czech Republic')
G[u'aCote'] = AT(u'own', u'I', u'd\u2019Ivoire')
G[u'aTurks'] = AT(u'own', u'I', u'Turks & Caicos')
G[u'aEastTimor'] = AT(u'J2', u'I', u'East Timor')
G[u'aMicron'] = AT(u'J2', u'I', u'Micronesia')
G[u'aBouvet'] = AT(u'J2', u'I', u'Bouvet Island')
G[u'aZHdr'] = AT(u'own', u'Z', u'tzdb timezone descriptions')
G[u'aZPub'] = AT(u'own', u'Z', u'public domain.')
G[u'aZCols'] = AT(u'own', u'Z', u'The countries that overlap')
G[u'aZIso'] = AT(u'own', u'Z', u'2-character country codes')
G[u'aZTZ'] = AT(u'own', u'Z', u'TZ environment variable')
G[u'aZPop'] = AT(u'own', u'Z', u'most-populous city')
G[u'aLines'] = AT(u'own', u'Z', u'Lines beginning with')
G[u'aLinesI'] = AT(u'own', u'I', u'a single tab')

G[u'aUTF'] = AT(u'own', u'I', u'All text uses UTF-8 encoding')
G[u'aBRAZ'] = AT(u'own', u'Z', u'Brazil (northeast')
G[u'aBA'] = AT(u'own', u'Z', u'Argentina/Buenos_Aires')
G[u'aAND'] = AT(u'own', u'Z', u'Europe/Andorra')
G[u'aTROLL'] = AT(u'own', u'Z', u'Antarctica/Troll')
G[u'aRType'] = AT(u'own', u'R', u'Type: region')
G[u'aRTP'] = AT(u'own', u'R', u'Description: East Timor')
G[u'aR057'] = AT(u'own', u'R', u'Description: Micronesia')
G[u'aDepTP'] = AT(u'own', u'R', u'Deprecated: 2002-05-20')
G[u'aPrefTL'] = AT(u'own', u'R', u'Preferred-Value: TL')
G[u'aAntR'] = AT(u'own', u'R', u'Description: Antigua and Barbuda')
G[u'aBurma'] = AT(u'own', u'R', u'Description: Burma')
G[u'aSoviet'] = AT(u'own', u'R', u'Union of Soviet Socialist Republics')
G[u'aPrivate'] = AT(u'own', u'R', u'Description: Private use')
G[u'aCIV'] = AT(u'own', u'R', u"Côte d'Ivoire")
G[u'aZQ'] = AT(u'own', u'R', u'Description: Eastern Europe')

# ---------- 数字登记 ----------
G[u'by'] = JOIN(u'bytes', u'字节')
G[u'ln'] = JOIN(u'lines', u'换行')
G[u'nb'] = JOIN(u'nonblank', u'非空行')
G[u'ltw'] = JOIN(u'lt', u"'<' 枚")
G[u'tb'] = JOIN(u'tabs', u'制表符枚')
G[u'hsh'] = JOIN(u'hash', u"'#' 行")
G[u'na'] = JOIN(u'nonascii', u'非 ASCII 枚')
G[u'cl'] = JOIN(u'curly', u'弯引号枚')
G[u'bg'] = JOIN(u'bytegap', u'字节减字符')
G[u'eqc'] = V(u'eqc', None, u'字符数=字节数成立的份数')
G[u'shaK'] = V(u'sha_distinct', None, u'sha16 种数')
G[u'ratioZ'] = V(u'ratio', 1, u'Z 字节是 I 的倍率')
G[u'ratioR'] = V(u'ratio', 2, u'R 字节是 I 的倍率')
G[u'byI'], G[u'byZ'], G[u'byR'] = V(u'bytes', 0, u'字节·码表'), V(u'bytes', 1, u'字节·时区表'), V(u'bytes', 2, u'字节·注册表')
G[u'tbI'], G[u'tbZ'], G[u'tbR'] = V(u'tabs', 0, u'制表符·码表'), V(u'tabs', 1, u'制表符·时区表'), V(u'tabs', 2, u'制表符·注册表')

G[u'ir'] = V(u'i_rows_strict', None, u'严格两列正则命中的行')
G[u'ird'] = V(u'i_rows_data', None, u'非注释行')
G[u'irx'] = V(u'i_rows_unmatched', None, u'两列正则不中的行数')
G[u'imt'] = V(u'i_multi_tab', None, u'两枚以上制表符的数据行')
G[u'icd'], G[u'icdup'] = V(u'i_code_dist', None, u'不同码'), V(u'i_code_dup', None, u'重数码')
G[u'ind'], G[u'indup'] = V(u'i_name_dist', None, u'不同名'), V(u'i_name_dup', None, u'重名')
G[u'isort'] = V(u'i_sorted_desc', None, u'按码排序的逆序处')
G[u'iam'] = V(u'i_amp', None, u'带 & 的名')
G[u'ipar'] = V(u'i_paren', None, u'带括号的名')
G[u'idot'] = V(u'i_dot', None, u'带缩写点的名')
G[u'icm'] = V(u'i_comma', None, u'带逗号的名')
G[u'inas'] = V(u'i_nonascii_names', None, u'含非 ASCII 的名')
G[u'iap'] = V(u'i_apos', None, u'含弯撇号的名')
G[u'ichars'] = V(u'i_name_chars', None, u'名串字符合计')
G[u'imaxlen'], G[u'iminlen'] = V(u'i_maxlen', None, u'最长名'), V(u'i_minlen', None, u'最短名')
G[u'imaxv'] = u' ⇎ '.join(F[u'i_maxlen_v'][:2])
G[u'icml'], G[u'icc'] = V(u'i_cmt_lines', None, u'注释行'), V(u'i_cmt_chars', None, u'注释字符')
G[u'icmt'] = V(u'i_cmt_tab_lines', None, u'注释里带制表符的行')
G[u'ite'], G[u'itd'] = V(u'i_tab_expect', None, u'制表符结构推得'), V(u'i_tab_diff', None, u'制表符实数与推得之差')
G[u'iurl'] = V(u'i_url', None, u'URL 枚')
G[u'idates'] = u' ⇎ '.join(F[u'i_dates_byline'])
G[u'idual'] = EXPR(str(len(F[u'i_dates'])), u"len(B56V('i_dates'))", u'注释里的不同日期')
G[u'idiu'] = V(u'i_date_unsorted', None, u'按行序的日期逆序处')
G[u'ileap'] = V(u'i_leap', None, u'闰日枚数')
G[u'ihs'] = V(u'i_hdr_split', None, u'列名注释被拆成两条')
G[u'ihcc'] = V(u'i_hdr_cc', None, u'连写的 country-code 出现次')
G[u'iutf'] = V(u'i_utf8_strict', None, u'严格 UTF-8 解码通过')
G[u'iu1'], G[u'iu2'] = V(u'i_claim_used', None, u'注释点名的在用串命中'), V(u'i_claim_avoided', None, u'注释点名的避用串缺席')
G[u'iut'], G[u'iope'] = V(u'i_claim_total', None, u'注释点名的串总数'), V(u'i_claim_open', None, u'两条账相加与总数之差')
G[u'iavi'] = V(u'i_claim_avoided_in', None, u'本该避掉却仍在场的串')
G[u'isg'] = V(u'i_samoa_gap', None, u'名排序里两枚 Samoa 之间隔的行')
G[u'isk'], G[u'ism'], G[u'isa'] = V(u'i_stem_kinds', None, u'括号前词干种数'), V(u'i_stem_multi', None, u'多名的干'), V(u'i_stem_adj', None, u'同干相邻对')
G[u'isc2'], G[u'isclose'] = V(u'i_stem_contig', None, u'名排序里连成块的同干组'), V(u'i_stem_close', None, u'连块组数减多名干数')

G[u'zrows'] = V(u'z_rows', None, u'时区表数据行')
G[u'zcols'] = u' ⇎ '.join(str(x) for x in F[u'z_cols'])
G[u'z3'], G[u'z4'] = V(u'z_col3', None, u'3 列行'), V(u'z_col4', None, u'4 列行')
G[u'zcc'], G[u'zcco'] = V(u'z_cc_dist', None, u'国家列不同码'), V(u'z_cc_occ', None, u'国家码出现次')
G[u'zmr'], G[u'zmx'] = V(u'z_multi_rows', None, u'多国行'), V(u'z_maxm', None, u'一行的最多国')
G[u'zat'] = V(u'z_at', None, u"'#@' 行")
G[u'znh'] = V(u'z_name_hits', None, u'I 的名在 Z 逐字出现')
G[u'zt1'], G[u'zt2'], G[u'zt3'] = V(u'z_tail_comp', None, u'名等于路径末段'), V(u'z_mid_comp', None, u'名等于中间段'), V(u'z_cmt_only', None, u'名不等于任何路径段')
G[u'ztz'] = V(u'z_tier_close', None, u'三档相加与命中数之差')
G[u'zsp'], G[u'zsp1'], G[u'zsp2'] = V(u'z_space_names', None, u'带空格的名'), V(u'z_us_plain', None, u'原样活着'), V(u'z_us_only', None, u'换成下划线才活着')
G[u'zspc'] = V(u'z_us_close', None, u'两档相加与带空格名命中之差')

G[u'rrec'], G[u'rsep'] = V(u'r_recs', None, u'注册表段数'), V(u'r_sep', None, u'分隔行')
G[u'rgap'] = V(u'r_sep_gap', None, u'段数减分隔符减一')
G[u'rgn'] = V(u'r_region_n', None, u'region 型段数')
G[u'ra'], G[u'rdg'], G[u'rro'] = V(u'r_alpha', None, u'两位 region'), V(u'r_digit', None, u'三位数字 region'), V(u'r_range', None, u'区间 region')
G[u'rlc'] = V(u'r_len_close', None, u'三分相加与 region 总数之差')
G[u'rdist'], G[u'rreuse'] = V(u'r_desc_dist', None, u'Description 不同串'), V(u'r_desc_reuse', None, u'复用次')
G[u'ramd'] = V(u'r_amp_desc', None, u'R 侧 Description 带 & 的')

G[u'in3'] = V(u'inter3', None, u'三源共有码')
G[u'zoi'], G[u'ioz'] = V(u'z_only_i', None, u'Z 有 I 无'), V(u'i_only_z', None, u'I 有 Z 无')
G[u'ior'] = V(u'i_only_r', None, u'I 有 R 无')
G[u'roi'] = V(u'r_only_i', None, u'R 有 I 无')
G[u'roia'], G[u'roid'], G[u'roir'] = V(u'r_only_i_alpha', None, u'R 独有两位'), V(u'r_only_i_digit', None, u'R 独有数字'), V(u'r_only_i_range', None, u'R 独有区间')
G[u'roic'] = V(u'r_only_i_close', None, u'三档相加与 R 独有之差')
G[u'raic'] = V(u'r_alpha_close', None, u'共有两位加独有两位与 region 两位之差')
G[u'rza'] = V(u'rz_alpha', None, u'region 两位不在 Z 国家列')
G[u'brg'] = V(u'bridge', None, u'桥数与本条两档相加之差')
G[u'zcl'], G[u'icl'] = V(u'z_in_i_close', None, u'共有加 Z 独有与 Z 码数之差'), V(u'i_in_r_close', None, u'共有加 I 独有与 I 码数之差')
G[u'depac'] = V(u'dep_close', None, u'两档相加与弃用总数之差')
G[u'rod'], G[u'shd'], G[u'depn'], G[u'depc'] = V(u'r_only_dep', None, u'R 独有里带弃用的'), V(u'shared_dep', None, u'共有码里带弃用的'), V(u'dep_total', None, u'region 弃用总数'), V(u'dep_close', None, u'两档相加与弃用总数之差')

G[u'ncmp'] = V(u'name_cmp', None, u'可比码')
G[u'neq'], G[u'ndf'] = V(u'name_eq', None, u'名全等'), V(u'name_dif', None, u'名不等')
G[u'ncl2'] = V(u'name_cmp_close', None, u'两档相加与可比码之差')
G[u'nlex'], G[u'nsem'] = V(u'name_lex', None, u'只换写法'), V(u'name_sem', None, u'换了词')
G[u'nclc'] = V(u'name_lex_close', None, u'两档相加与名不等之差')
G[u'nlr'], G[u'nli'], G[u'nls'] = V(u'name_longer_r', None, u'R 名更长'), V(u'name_longer_i', None, u'I 名更长'), V(u'name_samelen', None, u'等长')
G[u'nllc'] = V(u'name_len_close', None, u'三档相加与名不等之差')
G[u'ndc'] = V(u'name_dif_chars', None, u'名串字符净差')
G[u'nab'], G[u'nac'] = V(u'name_amp_both', None, u'I 用 & 而 R 用 and 的码'), V(u'name_amp_close', None, u'与 I 侧 & 名数之差')
G[u'nla'] = V(u'name_lex_amp', None, u'只换写法一档里带 & 的')
G[u'rai'] = V(u'r_alpha_in_i', None, u'与 I 共有的两位 region')
G[u'naa'] = V(u'name_amp_all', None, u'名不等一档里 I 侧带 & 的')
G[u'npl'], G[u'ncx'] = V(u'name_str_pool', None, u'名串在两表值集共有'), V(u'name_cross', None, u'同名挂在别枚码上')
G[u'npc'] = V(u'name_pool_close', None, u'全等加跨码与共有名串之差')
G[u'fdif'] = u' ⇎ '.join(F[u'name_first_diff'])
G[u'sem0'] = u' ⇎ '.join(F[u'sem_ex'][0][1:])
G[u'lex0'] = u' ⇎ '.join(F[u'lex_ex'][0][1:])
G[u'crossv'] = u' ⇎ '.join(u'%s@%s(%s)' % (n, c, u','.join(v)) for (c, n, v) in F[u'name_cross_v'])

G[u'cl1'], G[u'cl2'], G[u'cl3'] = (V(u'cmt_lines', 0, u'注释行·码表'), V(u'cmt_lines', 1, u'注释行·时区表'),
                                   V(u'cmt_lines', 2, u'注释行·注册表'))
G[u'clw'] = V(u'cmt_line_shared', None, u'整行逐字共用的注释行')
G[u'csn'] = EXPR(str(F[u'cmt_sent_n'][0]), u"B56V('cmt_sent_n', 0)", u'接行后 I 的句数')
G[u'csn2'] = EXPR(str(F[u'cmt_sent_n'][1]), u"B56V('cmt_sent_n', 1)", u'接行后 Z 的句数')
G[u'css'] = V(u'cmt_sent_shared', None, u'接行后共用句')
G[u'ccb'], G[u'cci'], G[u'ccz'], G[u'ccn'] = (V(u'cmt_contig_both', None, u'两源都连续的共用句'),
                                             V(u'cmt_contig_i', None, u'只在码表连续'),
                                             V(u'cmt_contig_z', None, u'只在时区表连续'),
                                             V(u'cmt_contig_none', None, u'两源都被折行的共用句'))
G[u'cccc'] = V(u'cmt_contig_close', None, u'四档相加与共用句之差')
G[u'csw'] = JOIN(u'cmt_sorted_word', u"'sorted' 一词")

G[u'kn'] = V(u'key_n', None, u'关键串枚数')
G[u'k3'], G[u'k2'], G[u'k1'], G[u'k0'] = (V(u'key_3', None, u'三源同现'), V(u'key_2', None, u'两源同现'),
                                          V(u'key_1', None, u'单源'), V(u'key_0', None, u'一枚不中'))
G[u'kc'] = V(u'key_close', None, u'四档相加与串数之差')
G[u'kiz'], G[u'kir'], G[u'kzr'] = V(u'key_IZ', None, u'I⇎Z 两源'), V(u'key_IR', None, u'I⇎R 两源'), V(u'key_ZR', None, u'Z⇎R 两源')
G[u'kpairs'] = V(u'key_pair_close', None, u'三种配对相加与两源同现之差')
G[u'k3n'] = u' ⇎ '.join(F[u'key_3names'])
G[u'pn'] = V(u'pool_n', None, u'锚候选池条数')
G[u'pi'], G[u'pz'], G[u'pr'] = V(u'poolI', None, u'池里码表条'), V(u'poolZ', None, u'池里时区表条'), V(u'poolR', None, u'池里注册表条')
G[u'p1'], G[u'p2'], G[u'p3'] = V(u'pool_1', None, u'只穿一源'), V(u'pool_2', None, u'穿两源'), V(u'pool_3', None, u'穿三源')
G[u'pcl'] = V(u'pool_close', None, u'三档相加与池条数之差')
G[u'pcross'] = V(u'pool_cross', None, u'穿两源以上')
G[u'nat'] = TOK(u'anchor_total', u'锚在正文出现处数')
G[u'ndist'] = TOK(u'anchor_distinct', u'锚去重串数')
G[u'nerr'] = TOK(u'anchor_err', u'锚错配处数')
G[u'ns1'] = TOK(u'anchor_single', u'只属一源的锚串数')
G[u'ns2'] = TOK(u'anchor_two', u'穿两源的锚串数')
G[u'ns3'] = TOK(u'anchor_three', u'穿三源的锚串数')
G[u'checked'] = TOK(u'checks', u'锚成员检查次数')
G[u'iopz'] = EXPR(str(F[u'z_cc_dist'] + F[u'i_only_z']), u"B56V('z_cc_dist')+B56V('i_only_z')", u'Z 码数加 I 独有码')

LINE(u'🧭', u"三源字节 {by}: 码表 {byI} ⇎ 时区表 {byZ}(约 {ratioZ} 倍) ⇎ 注册表 {byR}(约 {ratioR} 倍)。"
        u"换行 {ln}, 非空行 {nb}, '<' {ltw}, 制表符 {tb}, '#' 行 {hsh}, 非 ASCII {na}。"
        u"注册表是段表: {rrec} 段由 {rsep} 行分隔符切出(差 {rgap}), 它没有注释语法, 所以 '#' 行 {cl3} ⇎ 另两份 {cl1} ⇎ {cl2}。"
        u"三份都不是纯 ASCII: 非 ASCII {na}, 字节减字符 {bgI} ⇎ {bgZ} ⇎ {bgR}, 所以字符数=字节数在 {eqc} 份上成立; "
        u"弯引号四类 {cl}, 三者 sha16 是 {shaK} 个不同的串(串本身只进解读注)。",
        bgZ=V(u'bytegap', 1, u'字节减字符·时区表'), bgI=V(u'bytegap', 0, u'字节减字符·码表'),
        bgR=V(u'bytegap', 2, u'字节减字符·注册表'))

LINE(u'📏', u"码表把自己规定成“每行一枚制表符分两列”, 并交给数据判: 逐行套严格两列正则(两位大写码 + 恰一枚制表符 + 不含制表符的名)命中 {ir} 行, "
        u"非注释行共 {ird} 行, 不中的 {irx} 行, 带第二枚制表符的数据行 {imt} 行。"
        u"于是制表符也可推: 数据 {ir} 枚 + 注释里 {icmt} 枚(那条列名行) = {ite} ⇎ 数出来 {tbI}, 差 {itd}。"
        u"列名注释自身是断的: {aCountry} 与 {aColHdr} 是相邻两条注释, 连写的 'country-code' 在整份文件里出现 {ihcc} 次(拆行标志 {ihs})。"
        u"码 {icd} 枚无重复({icdup}) ⇎ 名 {ind} 种无重复({indup}); 注释说 {aSorted}, 按码判逆序 {isort} 处。"
        u"名串合计 {ichars} 字符, 最长 {imaxlen}({imaxv}) ⇎ 最短 {iminlen}; 带 & 的 {iam} ⇎ 带括号的 {ipar} ⇎ 带缩写点的 {idot} ⇎ 带逗号的 {icm}。", **G)

LINE(u'📐', u"注释写规则, 数据判规则——码表的四条格式律: 单制表符分列(上段 {itd}), "
        u"'#' 开头是注释(共 {icml} 行 {icc} 字符, 其中 {icmt} 行含制表符 ⇒ 注释行也可能长得像数据行), "
        u"{aUTF} 说全用 UTF-8(严格解码通过 {iutf}, 字节减字符 {bgI} 而含非 ASCII 的名 {inas} 串), "
        u"以及按码排序({isort} 处逆序)。"
        u"注释还自写三条命名理由, 点名了 {iut} 串: 它说该用的 {iu1} 串全在场, 该避掉的 {iu2} 串全不在场(两账相加校住 {iut}, 差 {iope}), "
        u"而“该避掉却反而在场”的有 {iavi} 串。判到名字层的具体三条: {aSamoa} 与它的姊妹在名排序里相隔 {isg} 行, "
        u"括号前同干多名的 {ism} 组在名排序里全部连成块({isc2}, 差 {isclose}), 词干共 {isk} 种 ⇎ 同干相邻对 {isa} 处。"
        u"注释里 {idual} 个日期按行序是 {idates}, 与值序逆 {idiu} 处(那条被压在后面的 {aLeap} 恰是闰日 {ileap} 枚), "
        u"出处署名 {aEggert} 而全表只 {iurl} 枚 URL。", bgI=V(u'bytegap', 0, u'字节减字符·码表'), **G)

LINE(u'🪢', u"同一批码的名字在三处是三种东西——本条主轴。取 I⇎R 共有的 {ncmp} 枚码逐码比名: 全等 {neq} ⇎ 不等 {ndf}"
        u"(两档相加校住 {ncmp}, 差 {ncl2})。不等的再分档: 把 & 写成 and、把弯撇号写成直撇号这类“只换写法”{nlex} 枚 ⇎ "
        u"换了词的 {nsem} 枚(相加校住 {ndf}, 差 {nclc})。首例 {fdif}; 换词的如 {sem0}, 只换写法的如 {lex0}。"
        u"I 侧 {iam} 枚带 '&' 的名, 在 R 里 {nab} 枚写作 ' and '(与 I 侧计数差 {nac}, 即一枚不漏); "
        u"“只换写法”一档里带 & 的 {nla} 枚。弯撇号只有 {iap} 枚: {aCote} ⇎ R 写作 {aCIV}。"
        u"名长一侧: R 更长的 {nlr} ⇎ I 更长的 {nli} ⇎ 等长 {nls}(三档校住 {ndf}, 差 {nllc}), 字符数净差 {ndc}。"
        u"I 还大量缩写: {aTurks} 这种带点或截短的写法在 R 没有对应。", **G)

LINE(u'🧱', u"码的集含方向是三向的, 而且每向都闭合: 三源共有 {in3} 枚; Z 有而 I 无 {zoi} 枚 ⇎ I 有而 Z 无 {ioz} 枚"
        u"(即 {iopz} 校住 I 码数, 差 {zcl}); I 有而 R 无 {ior} 枚 ⇎ R 有而 I 无 {roi} 枚(差 {icl})。"
        u"R 独有那 {roi} 枚拆开是两位 {roia} ⇎ 三位数字 {roid} ⇎ 区间 {roir}(相加校住 {roi}, 差 {roic}), "
        u"region 的两位共 {ra} 枚, 拆成与 I 共有的 {rai} 枚 ⇎ I 里没有的 {roia} 枚(相加校住 {ra}, 差 {raic})。"
        u"于是时区表国家列之外的两位 region 那 {rza} 枚恰好等于本条的 {roia} 加 {ioz}(桥差 {brg}): 一份表比另一份少的码, 拆成“注册表根本没登记”与“注册表登记了但时区表没用”两笔。"
        u"弃用账也分向: R 的 region 里带弃用的 {depn} 枚, 其中 {rod} 枚在 I 独有条目里 ⇎ 与 I 共有的 {in3} 枚里带弃用的 {shd} 枚(相加校住 {depn}, 差 {depac})。",
        **G)

LINE(u'🗣', u"名字层在时区表里没有一个安身列, 却并未消失: Z 的列数只有 {zcols}(3 列 {z3} 行 ⇎ 4 列 {z4} 行), 第三列是 '大洲/城市' 式标识符, 第四列是自由文本。"
        u"I 的 {ind} 枚名逐字拿去 Z 里找, 命中 {znh} 枚: 等于某个标识符末段的 {zt1} ⇎ 等于中间段的 {zt2} ⇎ 不等于任何路径段的 {zt3}(三档相加校住 {znh}, 差 {ztz})。"
        u"末段的如 {aAND} 里的 Andorra, 中间段的如 {aBA} 把 Argentina 放在两级路径之间, 第四格自由文本的如 {aBRAZ} 把国名与括号内的州码并置在一格。"
        u"带空格的名 {zsp} 枚里, 原样带空格活着的只 {zsp1} 枚, 必须把空格写成下划线才活着的 {zsp2} 枚(Z 用 'Lord_Howe' 这种形式), 两档校住 {zspc}。"
        u"国家码本身在 Z 出现 {zcco} 次于 {zcc} 枚不同码, 多国行 {zmr} 行, 最多一行 {zmx} 国; Z 另有 {zat} 行 '#@' 前缀的注释(位置行), 它把码表的名字列整个换成坐标。", **G)

LINE(u'🧵', u"两份表的注释其实在说同样的话, 但按整行逐字判只共用 {clw} 行——而且那一行恰恰是 {aCountry} 这个拆行残片, 不是任何一条规则。"
        u"把注释块接行(换行折成空格)再断句: 码表 {csn} 句 ⇎ 时区表 {csn2} 句, 共用句 {css} 条(码表一侧 {aLinesI} ⇎ 时区表一侧 {aLines})。"
        u"这 {css} 条再按“在原文件里是否连续”判: 两源都连续的 {ccb} 条 ⇎ 只在码表连续的 {cci} 条 ⇎ 只在时区表连续的 {ccz} 条 ⇎ 两份文件都在句中折行的 {ccn} 条"
        u"(四档相加校住 {css}, 差 {cccc})。也就是说“这两份注释是否写了同一条规则”取决于先问整行、接行、还是逐字连续: "
        u"同一句声明在两份原文件里各自折在不同的行上, 所以 {aLinesI}(码表)与 {aLines}(时区表)这两个锚串互不逐字相等, 只有接行后才成为一条可比的声明。"
        u"'sorted' 一词 {csw} 次: 两份表都声明排序, 注册表一个 'sorted' 也不写; 弯引号枚数 {cl}。", **G)

LINE(u'🗂', u"跨源可判性还有一层是字面串。{kn} 枚关键串按逐字命中判: 三源同现 {k3} 枚({k3n}) ⇎ 两源 {k2} 枚 ⇎ 单源 {k1} 枚 ⇎ 一枚不中 {k0} 枚(四档校住 {kn}, 差 {kc}); "
        u"两源那一档再分配对: 码表⇎时区表 {kiz} ⇎ 码表⇎注册表 {kir} ⇎ 时区表⇎注册表 {kzr}(相加校住 {k2}, 差 {kpairs})。"
        u"锚候选池 {pn} 条(码表 {pi} ⇎ 时区表 {pz} ⇎ 注册表 {pr}): 只穿一源 {p1} ⇎ 穿两源 {p2} ⇎ 穿三源 {p3}(校住 {pn}, 差 {pcl}), 穿两源以上共 {pcross} 条。"
        u"注册表侧的锚只取 region 型的字段行, 所以 {aRType} ⇎ {aDepTP} ⇎ {aPrefTL} 这类“同一记录的第二行”也在池里。", **G)

LINE(u'🧬', u"同一个名字串可以挂在两批不同的码上: 名串集与 Description 值集的交有 {npl} 条, 其中按码对齐的全等只 {neq} 条, 余下 {ncx} 条是跨码同名(校住 {npl}, 差 {npc}): {crossv}。"
        u"两例的成因不同: I 把 {aEastTimor} 写在现役码 TL 上, 而 R 把这个串留给已弃用的 {aRTP} 码 TP, 并在同一段写 {aPrefTL} —— 名字跟着旧码, 码跟着新码; "
        u"另一例 I 把 {aMicron} 写在 FM 上, 而 R 把同一串分给数字区 057({aR057}), FM 自己的 Description 反而长出一截。"
        u"所以“按名 join 两份表”会多算 {ncx} 条, 而“按码 join”会漏掉 R 独有的 {roi} 枚——两种 join 的差额在这里都是可数的。"
        u"R 侧的 Description {rdist} 种 ⇎ {rgn} 枚复用 {rreuse} 次({aPrivate} 是共用最多的那组), 且 R 的 Description 里 '&' 只 {ramd} 枚: 连字符与 and 的分工写在两份表各自的取词习惯里。", **G)

LINE(u'🧪', u"这条的可核事实分三档, 第一档全部由三份在库字节现推({aPub} ⇎ {aZHdr} ⇎ {aRType}) ⇒ B56V 可复算: 三源字节/换行/非空/'<'/制表符/'#'行/非 ASCII/sha 种数, "
        u"码表的两列正则命中 {ir} ⇎ 不中 {irx} ⇎ 多符行 {imt}, 制表符结构推得差 {itd}, 注释四律与命名三理由({iu1}＋{iu2} 校住 {iut}, 差 {iope}), "
        u"同干连块差 {isclose} ⇎ Samoa 间隔 {isg} ⇎ 日期行序逆 {idiu}, 三向集含四处闭合({zoi} ⇎ {ioz} ⇎ {ior} ⇎ {roi})与桥差 {brg}, "
        u"弃用分向差 {depac}, 名字词汇四档闭合({ncl2} ⇎ {nclc} ⇎ {nllc} ⇎ {npc}), '&' 对 ' and ' 差 {nac}, "
        u"名字在 Z 的三档 {zt1}＋{zt2}＋{zt3} 差 {ztz} ⇎ 空格档差 {zspc}, 注释共用句四档差 {cccc}, 关键串与锚池两矩阵差 {kc} ⇎ {pcl}。"
        u"第二档只在本机成立: 三份字节的磁盘 mtime 与注释里那 {idual} 个日期谁新谁旧、{aEggert} 署的那次改动是否就是当前这份——进注不进门槛。"
        u"第三档不可由在库文件判定: ISO 官方此刻在用的名串(本条只见两份表各自的写法, 没第三份参照), "
        u"注册表把 'East Timor' 留在 TP 而把 TL 另立的流程理由, {aTerr} 那句免责声明背后的具体争议, 以及时区表第一列该不该用数字区码。"
        u"锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 {nat} 处／{ndist} 条去重串, 归属由正文现推, "
        u"每条对三源逐一判成员共 {checked} 次检查, 单源 {ns1} ⇎ 两源 {ns2} ⇎ 三源 {ns3}, 错配 {nerr} 处。", **G)

LINE(u'∴', u"骨架 ⇒ ① 三源字节 {by}, '#' 行 {hsh}, 制表符 {tb}, 非 ASCII {na}; "
           u"② 码表形状: 严格两列 {ir}／{ird} ⇎ 多符行 {imt} ⇎ 制表符推得差 {itd} ⇎ 列名注释拆行 {ihcc}; "
           u"③ 注释四律与命名三理由: 在场 {iu1} ⇎ 缺席 {iu2} ⇎ 合计校住 {iut}(差 {iope}), 同干连块 {isc2}／{ism}, 名排序逆序 {isort}; "
           u"④ 集含三向: 共有 {in3}, 四向差 {zoi} ⇎ {ioz} ⇎ {ior} ⇎ {roi}, 三分 {roia}＋{roid}＋{roir}(差 {roic}), 桥 {roia}＋{ioz}={rza}(差 {brg}); "
           u"⑤ 名字词汇: {neq} 全等 ⇎ {ndf} 不等 = {nlex} 只换写法 ＋ {nsem} 换词, '&'→'and' {nab}／{iam}, 跨码同名 {ncx}; "
           u"⑥ 名在 Z: 无名列({zcols}) 却命中 {znh} = {zt1}＋{zt2}＋{zt3}, 空格档 {zsp1}＋{zsp2}／{zsp}; "
           u"⑦ 注释同现三口径: 整行 {clw} ⇎ 接行 {css} ⇎ 连续 {ccb}/{cci}/{ccz}/{ccn}; 关键串 {k3}⇎{k2}⇎{k1}⇎{k0}; 锚池 {pn} 条穿三源 {p3} 条。"
           u"判词: 同一批两字母码在三处是三种对象——一处的名是列值, 一处的名是标识符的碎片, 一处的名属于另一套更大的码集; "
           u"所以“这两个名字是否一致”没有唯一答案: 按码 join 得 {neq} 条一致, 按名 join 多算 {ncx} 条, 问 Z 得 {znh} 条碎片级存活, 问注释得 {css} 条要接行才成句的规则。", **G)

LINE(u'ℒ', u"方法 ⇒ 遇到“同一批码在多份表里各说各话”的原料, 先把 join 键定下来再数: "
        u"本条把三种 join 并写(按码 {ncmp} 枚 ⇎ 按名串 {npl} 条 ⇎ 按碎片存活 {znh} 条), 并把它们的差额各登记成键({npc} ⇎ {ztz}), "
        u"这样“多算 {ncx} 条”就是算出来的而不是断言的; "
        u"把集含方向写成四向差加三分闭合({zoi} ⇎ {ioz} ⇎ {ior} ⇎ {roi}, 差 {roic}), 再把跨条目的桥写成 {roia}＋{ioz}−{rza} = {brg} 而不是抄上一个条目的结论; "
        u"把注释里的声明分成四种口径判(整行 {clw} ⇎ 接行断句 {css} ⇎ 逐字连续 {ccb} ⇎ 被折行 {ccn}), "
        u"并特意把唯一整行共用那条 {aCountry} 报出来——它是个拆行残片, 说明“整行相同”这个口径会把格式噪声当成语义重合; "
        u"最后把“该用的⇎该避的”两组字面串各判一遍再相加校住 {iut}, 免得只报命中那半句。", **G)

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 三源各 {chI} ⇎ {chZ} ⇎ {chR} 字符, 窗口只能取锚点触到的行; "
         u"而本条的结论全是跨行跨源量: {ncmp} 枚码的名字逐码比对、四向集含与桥、{css} 条要接行才现形的共用句、"
         u"{znh} 枚名字在标识符碎片里的三档存活。尤其“同一个名挂在别枚码上”那 {ncx} 例, 任何单源窗口都只看得见自己那半。"
         u"读它请按“这个数是对哪两份表、用哪种 join 数出来的”来读, 而不是按“少抄了多少原文”。",
     chI=V(u'chars', 0, u'字符·码表'), chZ=V(u'chars', 1, u'字符·时区表'),
     chR=V(u'chars', 2, u'字符·注册表'), **G)

assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([IZR])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
HITC = dict((a, tuple(i for i in range(3) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]),
       u'two': len([a for a in ANCH if len(HITC[a]) == 2]),
       u'three': len([a for a in ANCH if len(HITC[a]) == 3])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_two': CLS[u'two'], u'anchor_three': CLS[u'three'],
         u'checks': DIST * 3}
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'two'] + CLS[u'three'] == DIST
for k, v in sorted(AMETA.items()):
    reg(str(v), u"B56V('%s')" % k, TOKV.get(k, k))
for n in AMETA:
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
assert u'◘' not in body, u'锚统计量占位符未回填'
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv56.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b56flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms56.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[IZR]⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == n]))
                       for c, n in ((u'single', 1), (u'two', 2), (u'three', 3))),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV), u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': 3, u'flat': F,
      u'tie_keys': len(TIE), u'meas_tie_keys': [b for b, _, _ in TIE]}
json.dump(CH, io.open(u'corpus/_b56checks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

srcline = (u'src: ' + u' ⇎ '.join(u'%s (%d 字节／非空行 %d／\'<\' %d 枚／制表符 %d 枚／\'#\' 行 %d)' % (
    PATH[i], F[u'bytes'][i], F[u'nonblank'][i], F[u'lt'][i], F[u'tabs'][i], F[u'hash'][i]) for i in range(3)) +
           u' (三份没有共同的版本标记: 码表把出处写成 ' + F[u'i_dates_byline'][-1] + u' 一条注释, 时区表另写一个日期, '
           u'注册表用 File-Date 行; 谁新谁旧只在本机成立, 不进门槛)\n')
联结 = (u'；联结不是“同一份数据的两种序列化”, 而是同一批两位码在三份表里各有身份: 码表 %d 行两位码⇎名(注释自写四律与三条命名理由, '
        u'该用的 %d 串在场 ⇎ 该避的 %d 串缺席), 时区表 %d 行没有名字列却逐字装着码表来的名 %d 个(末段 %d ⇎ 中间段 %d ⇎ 非路径段 %d), '
        u'注册表的 region 型 %d 枚是码表的超集(两位 %d ＋ 三位数字 %d ＋ 区间 %d, 独有 %d 枚里 %d 枚已弃用); '
        u'按码比名 %d 枚里全等 %d ⇎ 不等 %d(只换写法 %d ＋ 换词 %d), 按名串 join 会多算 %d 条同名异码, '
        u'两份 tzdb 表的注释按整行只共用 %d 条(还是那个拆行残片), 接行断句才共 %d 条\n') % (
    F[u'i_rows_strict'], F[u'i_claim_used'], F[u'i_claim_avoided'], F[u'z_rows'], F[u'z_name_hits'],
    F[u'z_tail_comp'], F[u'z_mid_comp'], F[u'z_cmt_only'], F[u'r_region_n'], F[u'r_alpha'], F[u'r_digit'],
    F[u'r_range'], F[u'r_only_i'], F[u'r_only_dep'], F[u'name_cmp'], F[u'name_eq'], F[u'name_dif'],
    F[u'name_lex'], F[u'name_sem'], F[u'name_cross'], F[u'cmt_line_shared'], F[u'cmt_sent_shared'])
text = (u'# B56 三张表管着同一批两位码：一张把名写成列 ⇎ 一张没有名字列却装着 %d 个名 ⇎ 一张把 %d 枚扩成 %d 枚\n' % (
    F[u'z_name_hits'], F[u'i_code_n'], F[u'r_region_n']))
text += (srcline + 联结 +
         u'tags: 严格两列正则⇎制表符结构反推 注释四律对数据 命名理由点名可查 同干连块 日期行序非单调 闰日 '
         u'三向集含全闭合 跨条目桥数 弃用分向 按码⇎按名⇎按碎片三种join 只换写法⇎换了词 &对and 弯撇号⇎直撇号 '
         u'同名异码两例 名字在标识符里的三档存活 空格⇎下划线 注释整行⇎接行⇎逐字连续三口径 拆行残片刻坏整行口径 '
         u'关键串三源矩阵 锚归属由正文现推\n' +
         u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
         u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
         u'## ⛓解读注\n\n（此段由 corpus/_fill56.py 从 corpus/_b56checks.json 与 corpus/_b56meas.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d 串 ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'单源 %d ⇎ 两源 %d ⇎ 三源 %d ⇎ 错配 %d ｜ 池内取用 %d' % (
    CLS[u'single'], CLS[u'two'], CLS[u'three'], len(ERR), CH[u'pool_used']))
print(u'DERIV %d 键 ⇎ 复算点 %d ｜ 同数共键 %d 组(复合式) ｜ 0 键折 %d 项 ｜ TIE %d 量' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(TIE)))
for k, v in sorted(COLL.items(), key=lambda x: -len(x[1]))[:8]:
    print(u'  同数 %s ← %s' % (k, u' ⇎ '.join(v)))
print(u'残留未替换占位符 %d ｜ 未点名花括号 %d' % (
    len(re.findall(u'◘', body)), len(re.findall(u'[{][a-zA-Z_0-9]+[}]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))))
print(u'锚内拉丁 %d ｜ 锚外拉丁 %d ｜ 标签 %d 枚 ｜ 扁平键 %d 个' % (
    CH[u'letters_in'], CH[u'letters_out'], CH[u'tagn'], len(F)))
