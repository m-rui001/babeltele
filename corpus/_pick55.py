# -*- coding: utf-8 -*-
"""B55 第一遍(独立采集, 先于建条目写成): 只从 corpus/raw/langsubtag.txt 与 corpus/raw/tz/zone1970.tab 现量。
R = langsubtag.txt(BCP 47 / IANA 语言子标签注册表, 记录分隔符是 %%), Z = zone1970.tab(tz 的时区表, 国家列借的就是 R 的 region 码)。
本条要量的不是“两张表各有多少行”, 而是 R 自己没写明的值域约束在两种口径下的表现:
四个交叉引用字段(Suppress-Script/Macrolanguage/Preferred-Value/Prefix)各有规定值域, 判越界有两种口径——
整码判(把字段值当一个码) ⇎ 拆片判(按 '-' 切开逐片判); 两种口径的越界数在四个字段上分别是多少, 是本遍的主产物。
另取: 记录结构与字段面、子标签长度分布、Description 复用、Added/Deprecated 日期账、region 池里的数字码(UN M.49)⇎两位码,
以及 Z 的国家列与 R 的 region 集的双向差集。
落 corpus/_b55meas.json: {meas, pool, sel, tags, paths, labels}; pool 是逐字锚候选 (标签, 命中源数, 原文行),
建条目侧 corpus/_mkB55.py 只从这里取锚, 并在 TIE 表里与本遍逐量对账。
"""
import collections, glob, io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NL = chr(10)
TAGS = [u'R', u'Z']
PATHS = [u'corpus/raw/langsubtag.txt', u'corpus/raw/tz/zone1970.tab']
LB = [u'子标签注册表', u'时区表']
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATHS]
IDX = dict((t, i) for i, t in enumerate(TAGS))
M = {}


def two(name, f):
    M[name] = [f(i) for i in range(2)]


# ---------- 1) 两文件的基本形状 ----------
two(u'bytes', lambda i: os.path.getsize(PATHS[i]))
two(u'chars', lambda i: len(TXT[i]))
two(u'lines', lambda i: TXT[i].count(NL))
two(u'segments', lambda i: len(TXT[i].split(NL)))
two(u'nonblank', lambda i: len([l for l in TXT[i].split(NL) if l.strip()]))
two(u'blank', lambda i, _=None: M[u'segments'][i] - M[u'nonblank'][i])
two(u'lt', lambda i: TXT[i].count(u'<'))
two(u'gt', lambda i: TXT[i].count(u'>'))
two(u'nonascii', lambda i: len([c for c in TXT[i] if ord(c) > 127]))
two(u'tabs', lambda i: TXT[i].count(u'\t'))
two(u'colons', lambda i: len(re.findall(u'^[A-Z][A-Za-z-]*:', TXT[i], re.M)))
two(u'ascii_eq', lambda i: 1 if len([c for c in TXT[i] if ord(c) > 127]) == 0 else 0)

R, Z = TXT[0], TXT[1]

# ---------- 2) 记录结构 ----------
RL = R.split(NL)
RECS, cur = [], {}
for line in RL:
    s = line.strip()
    if s == u'%%':
        if cur:
            RECS.append(cur)
        cur = {}
        continue
    if not s:
        continue
    if line[:1] in u' \t' and cur:
        k = list(cur.keys())[-1]
        cur[k] = cur[k] + u' ' + s
        continue
    m = re.match(u'^([A-Z][A-Za-z-]*):\\s*(.*)$', line)
    if m:
        cur[m.group(1)] = m.group(2).strip()
if cur:
    RECS.append(cur)
M[u'records'] = len(RECS)
M[u'sep_occ'] = len(re.findall(u'^%%$', R, re.M))
M[u'types'] = dict(collections.Counter(r.get(u'Type', u'<none>') for r in RECS))
M[u'keys'] = dict(collections.Counter(k for r in RECS for k in r))
M[u'key_kinds'] = len(M[u'keys'])
M[u'subrec'] = len([r for r in RECS if u'Subtag' in r])
M[u'nosub'] = M[u'records'] - M[u'subrec']
M[u'hdr_outside'] = 1 if RECS and list(RECS[0].keys()) == [u'File-Date'] else 0
FILE_DATE = M[u'file_date'] = re.search(u'^File-Date:\\s*(\\S+)', R, re.M).group(1)
M[u'file_date_eq_first'] = 1 if list(RECS[0].keys()) == [u'File-Date'] else 0

SUB = [r for r in RECS if u'Subtag' in r]
BY = dict((t, [r for r in SUB if r.get(u'Type') == t]) for t in
          (u'language', u'extlang', u'script', u'region', u'variant'))
SET = dict((t, set(r[u'Subtag'] for r in BY[t])) for t in BY)
ALL_SUB = set(r[u'Subtag'] for r in SUB)
PV_ALL = [r for r in RECS if u'Preferred-Value' in r]
PREF = set(r[u'Preferred-Value'] for r in PV_ALL)
M[u'pvrec'] = len(PV_ALL)

# ---------- 3) 两种口径的闭世界账(本条主轴) ----------
DOM = [(u'Suppress-Script', SET[u'script']), (u'Macrolanguage', SET[u'language']),
       (u'Preferred-Value', ALL_SUB), (u'Prefix', ALL_SUB | PREF)]
XREF = {}
# 字段值取逐行口径: 同一段里同一字段可以出现多行(前缀单段最多 11 行), 折叠口径会少收
VALS = {}
for _b in R.split(NL + u'%%' + NL):
    for line in _b.split(NL):
        m = re.match(u'^([A-Z][A-Za-z-]*):[ \\t]*(.*)$', line)
        if m:
            VALS.setdefault(m.group(1), []).append(m.group(2).strip())
M[u'field_line_kinds'] = len(VALS)
M[u'field_line_n'] = dict((k, len(v)) for k, v in VALS.items())
M[u'field_lines'] = sum(len(v) for v in VALS.values())
M[u'field_folded'] = sum(M[u'keys'].values())
M[u'field_extra'] = M[u'field_lines'] - M[u'field_folded']
BLKS = R.split(NL + u'%%' + NL)
M[u'prefix_multi_recs'] = len([b for b in BLKS if len(re.findall(u'^Prefix:', b, re.M)) > 1])
M[u'prefix_max_per_rec'] = max(len(re.findall(u'^Prefix:', b, re.M)) for b in BLKS)
M[u'pref_distinct'] = len(PREF)
assert M[u'field_lines'] == M[u'colons'][0]
assert M[u'field_extra'] == (M[u'field_line_n'][u'Description'] - M[u'keys'][u'Description']) +     (M[u'field_line_n'][u'Prefix'] - M[u'keys'][u'Prefix']) + (M[u'field_line_n'][u'Comments'] - M[u'keys'][u'Comments'])
for k, dom in DOM:
    vals = VALS.get(k, [])
    whole = set(vals)
    pieces = set(p for v in whole for p in v.split(u'-'))
    XREF[k] = {
        u'field_n': len([r for r in RECS if k in r]),
        u'occ': len(vals), u'distinct': len(whole),
        u'compound': len([v for v in whole if u'-' in v]),
        u'viol_whole': sorted(v for v in whole if v not in dom),
        u'viol_piece': sorted(p for p in pieces if p not in dom),
        u'domain_n': len(dom),
    }
M[u'xref'] = XREF
M[u'viol_whole_total'] = sum(len(v[u'viol_whole']) for v in XREF.values())
M[u'viol_piece_total'] = sum(len(v[u'viol_piece']) for v in XREF.values())
M[u'compound_total'] = sum(v[u'compound'] for v in XREF.values())
M[u'fields_clean'] = len([k for k, v in XREF.items() if not v[u'viol_whole']])

# ---------- 4) 子标签长度与 Description ----------
M[u'sub_len'] = dict(collections.Counter(len(r[u'Subtag']) for r in SUB))
M[u'sub_len_kinds'] = len(M[u'sub_len'])
M[u'type_by_len'] = dict((t, dict(collections.Counter(len(r[u'Subtag']) for r in BY[t]))) for t in BY)
DESC = collections.Counter(r[u'Description'] for r in SUB if u'Description' in r)
M[u'desc_total'] = sum(DESC.values())
M[u'desc_distinct'] = len(DESC)
M[u'desc_multi'] = len([d for d, n in DESC.items() if n > 1])
M[u'desc_max_n'] = max(DESC.values())
M[u'desc_max'] = sorted([d for d, n in DESC.items() if n == M[u'desc_max_n']])
M[u'desc_once'] = len([d for d, n in DESC.items() if n == 1])
M[u'desc_reuse'] = M[u'desc_total'] - M[u'desc_distinct']

# ---------- 5) 日期账 ----------
ADDS = [r[u'Added'] for r in RECS if u'Added' in r]
DEPS = [(r.get(u'Subtag') or r.get(u'Preferred-Value') or r.get(u'Tag'), r[u'Deprecated'], r.get(u'Added'))
        for r in RECS if u'Deprecated' in r]
M[u'added_n'] = len(ADDS)
M[u'added_min'], M[u'added_max'] = min(ADDS), max(ADDS)
M[u'added_distinct'] = len(set(ADDS))
M[u'dep_n'] = len(DEPS)
M[u'dep_distinct_dates'] = len(set(d[1] for d in DEPS))
M[u'dep_before_add'] = [d for d in DEPS if d[2] and d[1] < d[2]]
M[u'dep_before_add_n'] = len(M[u'dep_before_add'])
M[u'added_after_file'] = len([a for a in ADDS if a > FILE_DATE])
dep_codes = set(d[0] for d in DEPS)
M[u'pref_dep'] = sorted(p for p in PREF if p in dep_codes)
M[u'pref_dep_n'] = len(M[u'pref_dep'])
M[u'dep_typed'] = dict(collections.Counter(r.get(u'Type') for r in RECS if u'Deprecated' in r))
M[u'comments_n'] = len(re.findall(u'^Comments:', R, re.M))
M[u'comment_field_n'] = len([r for r in RECS if u'Comments' in r])
M[u'comments_chars'] = sum(len(r[u'Comments']) for r in RECS if u'Comments' in r)
M[u'tag_field_n'] = len([r for r in RECS if u'Tag' in r])
M[u'scope_kinds'] = dict(collections.Counter(r[u'Scope'] for r in RECS if u'Scope' in r))

# ---------- 6) region 池 ⇎ 时区表的国家列 ----------
REG = SET[u'region']
M[u'region_n'] = len(REG)
M[u'reg_alpha'] = len([r for r in REG if re.match(u'^[A-Z]{2}$', r)])
M[u'reg_digit'] = len([r for r in REG if re.match(u'^[0-9]{3}$', r)])
M[u'reg_other'] = sorted(r for r in REG if not re.match(u'^[A-Z]{2}$', r) and not re.match(u'^[0-9]{3}$', r))
M[u'reg_ZZ'] = 1 if u'ZZ' in REG else 0
M[u'reg_x'] = len([r for r in REG if r[0] == u'X' or r[0] == u'Q'])
zl = [l.rstrip(u'\r') for l in Z.split(NL) if l.strip() and not l.startswith(u'#')]
M[u'z_rows'] = len(zl)
M[u'z_cols'] = sorted(set(len(l.split(u'\t')) for l in zl))
M[u'z_col_kinds'] = len(M[u'z_cols'])
CO = set()
BADFMT = []
for l in zl:
    p = l.split(u'\t')
    for c in p[0].split(u','):
        if c:
            CO.add(c)
    if not re.match(u'^[A-Z]{2}(,[A-Z]{2})*$', p[0]):
        BADFMT.append(p[0])
M[u'z_countries'] = len(CO)
M[u'z_multi_rows'] = len([l for l in zl if u',' in l.split(u'\t')[0]])
M[u'z_max_multi'] = max(len(l.split(u'\t')[0].split(u',')) for l in zl)
M[u'z_bad_fmt'] = BADFMT
M[u'z_only'] = sorted(CO - REG)
M[u'reg_only'] = len(REG - CO)
M[u'reg_shared'] = len(REG & CO)
M[u'z_zone_first'] = zl[0].split(u'\t')[2]
M[u'z_zone_prefixes'] = dict(collections.Counter(z.split(u'/')[0] for z in
                                                 [l.split(u'\t')[2] for l in zl]))
M[u'z_zone_n'] = len([l.split(u'\t')[2] for l in zl])
M[u'z_zone_distinct'] = len(set(l.split(u'\t')[2] for l in zl))
M[u'z_coords_re_ok'] = len([l for l in zl if re.match(u'^[+-]\\d{4,6}[+-]\\d{4,6}$', l.split(u'\t')[1])])
M[u'z_comment_rows'] = len([l for l in zl if len(l.split(u'\t')) > 3 and l.split(u'\t')[3].strip()])

# ---------- 7b) 第二口径的账: 同一记录的 Description 可以有多行 ----------
DL = re.findall(u'^Description:[ \\t]*(.*)$', R, re.M)
M[u'desc_lines'] = len(DL)
M[u'desc_distinct_line'] = len(set(DL))
M[u'desc_reuse_line'] = len(DL) - len(set(DL))
CL = collections.Counter(DL)
M[u'desc_multi_kinds'] = len([d for d, n in CL.items() if n > 1])
M[u'desc_once_line'] = len([d for d, n in CL.items() if n == 1])
M[u'desc_max_line_n'] = max(CL.values())
M[u'desc_max_line'] = sorted([d for d, n in CL.items() if n == M[u'desc_max_line_n']])
PER = [len(re.findall(u'^Description:', b, re.M)) for b in R.split(NL + u'%%' + NL)]
M[u'desc_multi_recs'] = len([n for n in PER if n > 1])
M[u'desc_max_per_rec'] = max(PER)
FD = [r[u'Description'] for r in RECS if u'Description' in r]
M[u'desc_fold_n'] = len(FD)
M[u'desc_fold_distinct'] = len(set(FD))
M[u'desc_fold_reuse'] = M[u'desc_fold_n'] - M[u'desc_fold_distinct']
M[u'sub_distinct'] = len(set(r[u'Subtag'] for r in SUB))
M[u'sub_repeat'] = len(SUB) - M[u'sub_distinct']
M[u'sub_dup_max'] = max(collections.Counter(r[u'Subtag'] for r in SUB).values())
M[u'pref_out'] = sorted(PREF - ALL_SUB)
M[u'pref_out_n'] = len(M[u'pref_out'])
M[u'dots'] = sorted(s for s in ALL_SUB if u'..' in s)
M[u'dots_n'] = len(M[u'dots'])

# ---------- 7c) 时区表的列账: 坐标位数 ⇎ 列数 ⇎ 前缀 ⇎ 多国行 ----------
def _dg(c):
    return [len(x) - 1 for x in re.findall(u'[+-]\\d+', c)]


LA = [_dg(l.split(u'\t')[1]) for l in zl]
M[u'z_lat_4'] = len([x for x in LA if x[0] == 4])
M[u'z_lat_6'] = len([x for x in LA if x[0] == 6])
M[u'z_lon_5'] = len([x for x in LA if x[1] == 5])
M[u'z_lon_7'] = len([x for x in LA if x[1] == 7])
M[u'z_col3'] = len([l for l in zl if len(l.split(u'\t')) == 3])
M[u'z_col4'] = len([l for l in zl if len(l.split(u'\t')) == 4])
M[u'z_max_multi'] = max(len(l.split(u'\t')[0].split(u',')) for l in zl)
M[u'z_max_multi_row'] = max(zl, key=lambda l: len(l.split(u'\t')[0].split(u','))).split(u'\t')[2]
PRE = collections.Counter(l.split(u'\t')[2].split(u'/')[0] for l in zl)
M[u'z_pre_kinds'] = len(PRE)
M[u'z_pre_max'] = max(PRE.values())
M[u'z_pre_max_name'] = sorted([p for p, n in PRE.items() if n == M[u'z_pre_max']])
M[u'z_pre_min'] = min(PRE.values())
M[u'z_pre_min_name'] = sorted([p for p, n in PRE.items() if n == M[u'z_pre_min']])
M[u'z_hash'] = len(re.findall(u'^#', Z, re.M))
M[u'z_desc_word'] = len(re.findall(u'description', Z, re.I))
M[u'z_zone_last'] = zl[-1].split(u'\t')[2]
M[u'reg_alpha_only'] = len([r for r in (REG - CO) if re.match(u'^[A-Z]{2}$', r)])
M[u'reg_digit_only'] = len([r for r in (REG - CO) if re.match(u'^[0-9]{3}$', r)])
M[u'reg_range_only'] = len([r for r in (REG - CO) if u'..' in r])
assert M[u'subrec'] + M[u'tag_field_n'] + M[u'hdr_outside'] == M[u'records']
assert M[u'types'][u'grandfathered'] + M[u'types'][u'redundant'] == M[u'tag_field_n']
assert M[u'reg_alpha'] + M[u'reg_digit'] + len(M[u'reg_other']) == M[u'region_n']
assert M[u'z_lat_4'] + M[u'z_lat_6'] == M[u'z_rows'] == M[u'z_col3'] + M[u'z_col4']
assert M[u'reg_alpha_only'] + M[u'reg_digit_only'] + M[u'reg_range_only'] <= M[u'reg_only']
assert M[u'desc_lines'] - M[u'desc_multi_recs'] > 0 and M[u'desc_reuse_line'] + M[u'desc_distinct_line'] == M[u'desc_lines']

# ---------- 8) 关键串穿两源 ----------
CROSS = [u'region', u'script', u'language', u'Deprecated', u'Preferred-Value', u'Suppress-Script',
         u'Macrolanguage', u'File-Date', u'%%', u'AD', u'GB', u'Type:', u'Subtag:', u'Cyrl', u'Europe']
pn = lambda s: re.sub(u'[^a-z0-9]', u'', s.lower())
FLAT = [pn(t) for t in TXT]
HS = [tuple(i for i in range(2) if pn(t) in FLAT[i]) for t in CROSS]
M[u'hitkinds'] = len(CROSS)
M[u'hitboth'] = len([h for h in HS if len(h) == 2])
M[u'hitsingle'] = len([h for h in HS if len(h) == 1])
M[u'hitnone'] = len([h for h in HS if not h])
M[u'hitR'] = len([h for h in HS if h == (0,)])
M[u'hitZ'] = len([h for h in HS if h == (1,)])
M[u'both_names'] = u' ／ '.join([t for t, h in zip(CROSS, HS) if len(h) == 2])

# ---------- 9) 逐字锚候选池 ----------
POOL = []
seen = set()
for tag, txt in zip(TAGS, TXT):
    for l in txt.split(NL):
        s = l.strip()
        if len(s) < 12 or u'\t' in s:
            continue
        k = pn(s)
        if not k or k in seen:
            continue
        seen.add(k)
        POOL.append((tag, len([i for i in range(2) if k in FLAT[i]]), s))
M[u'pool_n'] = len(POOL)
M[u'pool_cross'] = len([p for p in POOL if p[1] > 1])
c1 = [l.split(u'\t')[0].split(u',') for l in zl]
M[u'z_cc_sum'] = sum(len(cs) for cs in c1)
M[u'z_whole_unsorted'] = len([cs for cs in c1 if cs != sorted(cs)])
M[u'z_tail_unsorted'] = len([cs for cs in c1 if len(cs) > 1 and cs[1:] != sorted(cs[1:])])
M[u'z_first_desc'] = len([1 for a, b in zip([c[0] for c in c1], [c[0] for c in c1][1:]) if b < a])
MC = collections.Counter()
for cs in c1:
    for c in cs:
        MC[c] += 1
SHARED = set(c for c, n in MC.items() if n > 1)
M[u'z_rows_shared'] = len([cs for cs in c1 if any(c in SHARED for c in cs)])
M[u'z_col4_match'] = len([1 for cs, l in zip(c1, zl)
                          if (len(l.split(u'\t')) == 4) == any(c in SHARED for c in cs)])
M[u'z_at'] = len([l for l in Z.split(NL) if l.startswith(u'#@')])
M[u'z_tabbed'] = len([l for l in Z.split(NL) if l.startswith(u'#') and u'\t' in l])
M[u'z_tab_expect'] = 2 * M[u'z_col3'] + 3 * M[u'z_col4'] + 3 + M[u'z_at']
assert M[u'z_tab_expect'] == M[u'tabs'][1]
assert M[u'z_col4_match'] == M[u'z_rows'] and M[u'z_first_desc'] == 0
assert M[u'z_hash'] + M[u'z_rows'] == M[u'nonblank'][1]

# ---------- 8b) 锚池补足: 数据行的制表片段(整行含控制符, 不能进锚) ----------
for l in [zl[0], zl[-1], max(zl, key=lambda x: len(x.split(u'\t')[0].split(u',')))] + \
         [x for x in Z.split(NL) if x.startswith(u'#@')]:
    for f in l.split(u'\t'):
        k = pn(f.strip())
        if len(f) >= 8 and k and k not in seen:
            seen.add(k)
            POOL.append((u'Z', len([i for i in range(2) if k in FLAT[i]]), f.strip()))
M[u'z_field_pool'] = len([p for p in POOL if p[0] == u'Z' and not p[2].startswith(u'#')])
M[u'pool_n'] = len(POOL)
M[u'pool_cross'] = len([p for p in POOL if p[1] > 1])

io.open(u'corpus/_b55meas.json', u'w', encoding='utf-8', newline=NL).write(json.dumps(
    {u'meas': M, u'pool': POOL, u'tags': TAGS, u'paths': PATHS, u'labels': LB,
     u'sel': [p[2] for p in POOL if p[1] > 1][:20]}, ensure_ascii=False, indent=0))
print(u'R %d 字节／%d 行 ⇎ Z %d 字节／%d 行 ｜ 非 ASCII %s ⇎ 制表符 %s' % (
    M[u'bytes'][0], M[u'lines'][0], M[u'bytes'][1], M[u'lines'][1], M[u'nonascii'], M[u'tabs']))
print(u'记录 %d 段(%% 分隔 %d 次) ｜ 有 Subtag 的 %d ⇎ 无 Subtag 的 %d ｜ 字段面 %d 种 ｜ Type %s' % (
    M[u'records'], M[u'sep_occ'], M[u'subrec'], M[u'nosub'], M[u'key_kinds'], M[u'types']))
print(u'闭世界两种口径:')
for k, v in sorted(XREF.items()):
    print(u'   %s: 字段 %d 条／引用 %d 处／%d 个码／复合型 %d 个 → 整码判越界 %d %s ⇎ 拆片判越界 %d %s' % (
        k, v[u'field_n'], v[u'occ'], v[u'distinct'], v[u'compound'],
        len(v[u'viol_whole']), v[u'viol_whole'], len(v[u'viol_piece']), v[u'viol_piece']))
print(u'   合计 整码判 %d ⇎ 拆片判 %d ｜ 四字段里零越界的 %d 个 ｜ 越界数减复合数 %d' % (
    M[u'viol_whole_total'], M[u'viol_piece_total'], M[u'fields_clean'],
    M[u'viol_whole_total'] - M[u'compound_total']))
print(u'字段账: 逐行 %d 处 ⇎ 折叠 %d 格 ｜ 差 %d 全在 Description/Prefix/Comments ｜ 单段最多 Prefix %d 行(于 %d 段)' % (
    M[u'field_lines'], M[u'field_folded'], M[u'field_extra'],
    M[u'prefix_max_per_rec'], M[u'prefix_multi_recs']))
print(u'日期: File-Date %s ⇎ Added %d 处／%d 个不同日／最早 %s 最晚 %s ｜ Deprecated %d 条 ｜ 早于 Added %d 条 ｜ 晚于 File-Date %d 条' % (
    FILE_DATE, M[u'added_n'], M[u'added_distinct'], M[u'added_min'], M[u'added_max'],
    M[u'dep_n'], M[u'dep_before_add_n'], M[u'added_after_file']))
print(u'   Preferred-Value 指向已弃码 %d 处: %s' % (M[u'pref_dep_n'], M[u'pref_dep'][:8]))
print(u'Description: 用 %d 次／%d 条不同 ⇎ 复用 %d ｜ 同名多码 %d 组 ｜ 最高 %d 名 %s' % (
    M[u'desc_total'], M[u'desc_distinct'], M[u'desc_reuse'], M[u'desc_multi'],
    M[u'desc_max_n'], M[u'desc_max']))
print(u'region %d 枚: 两位码 %d ⇎ 三位数字码 %d ⇎ 其他 %s ｜ ZZ %d ｜ X/Q 保留段 %d' % (
    M[u'region_n'], M[u'reg_alpha'], M[u'reg_digit'], M[u'reg_other'], M[u'reg_ZZ'], M[u'reg_x']))
print(u'Z: 数据 %d 行／列数种类 %s ｜ 国家码 %d 枚(多选行 %d, 最多 %d 国一行) ｜ 时区名 %d ⇎ %d 种' % (
    M[u'z_rows'], M[u'z_cols'], M[u'z_countries'], M[u'z_multi_rows'], M[u'z_max_multi'],
    M[u'z_zone_n'], M[u'z_zone_distinct']))
print(u'   join: Z 有而 R 无 %d %s ⇎ R 有而 Z 无 %d ｜ 交集 %d ｜ Z 国家列格式异常 %s' % (
    len(M[u'z_only']), M[u'z_only'], M[u'reg_only'], M[u'reg_shared'], M[u'z_bad_fmt']))
print(u'关键串 %d 枚: 两源同现 %d ⇎ 单源 %d(R 独占 %d／Z 独占 %d) ⇎ 不中 %d ｜ 同现名单: %s' % (
    M[u'hitkinds'], M[u'hitboth'], M[u'hitsingle'], M[u'hitR'], M[u'hitZ'], M[u'hitnone'], M[u'both_names']))
print(u'锚候选池 %d 条(穿两源 %d) ｜ Z 的片段锚 %d 条 ｜ 落 corpus/_b55meas.json' % (
    M[u'pool_n'], M[u'pool_cross'], M[u'z_field_pool']))
print(u'Z 自写的三条规则对数据的账: 首码逆序 %d ｜ 整列不 alphabetical %d 行 ⇎ 去掉首国后 %d 行 ｜ 国家格 %d 枚' % (
    M[u'z_first_desc'], M[u'z_whole_unsorted'], M[u'z_tail_unsorted'], M[u'z_cc_sum']))
print(u'Z 第 4 列 ⇎“该国跨多时区”: 两个方向都相符的行 %d／%d ｜ 实验性 #@ 行 %d ｜ 制表符按列结构推得 %d' % (
    M[u'z_col4_match'], M[u'z_rows'], M[u'z_at'], M[u'z_tab_expect']))
print(u'第二口径的账: Description 行 %d(在 %d 段里, %d 段带第二条以上, 单段最多 %d 行) ／ %d 个不同串 ⇎ 复用 %d ｜ 最高 %d 名 %s' % (
    M[u'desc_lines'], M[u'keys'][u'Description'], M[u'desc_multi_recs'],
    M[u'desc_max_per_rec'], M[u'desc_distinct_line'], M[u'desc_reuse_line'],
    M[u'desc_max_line_n'], M[u'desc_max_line']))
print(u'Subtag 记录 %d 段 ⇎ 不同码 %d(重复 %d, 单码最多 %d 段) ｜ Pref-Value 有而 Subtag 无 %d %s ｜ 区间码 %d 个 %s' % (
    M[u'subrec'], M[u'sub_distinct'], M[u'sub_repeat'], M[u'sub_dup_max'], M[u'pref_out_n'], M[u'pref_out'],
    M[u'dots_n'], M[u'dots']))
print(u'Z 坐标: 分钟级 %d 行 ⇎ 秒级 %d 行(纬度 4⇎6 位, 经度 5⇎7 位) ｜ 3 列 %d ⇎ 4 列 %d ｜ 注释 %d 行' % (
    M[u'z_lat_4'], M[u'z_lat_6'], M[u'z_col3'], M[u'z_col4'], M[u'z_hash']))
print(u'Z 前缀 %d 种: 最多 %d(%s) ⇎ 最少 %d(%s) ｜ 一国一行的最多 %d 国(%s) ｜ 末行 %s' % (
    M[u'z_pre_kinds'], M[u'z_pre_max'], M[u'z_pre_max_name'], M[u'z_pre_min'], M[u'z_pre_min_name'],
    M[u'z_max_multi'], M[u'z_max_multi_row'], M[u'z_zone_last']))
print(u'R 有而 Z 无的 %d 枚拆开: 两位码 %d ⇎ 三位数字码 %d ⇎ 区间 %d ｜ “description”一词在 Z 出现 %d 次' % (
    M[u'reg_only'], M[u'reg_alpha_only'], M[u'reg_digit_only'], M[u'reg_range_only'], M[u'z_desc_word']))
