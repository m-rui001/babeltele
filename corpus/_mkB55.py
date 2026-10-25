# -*- coding: utf-8 -*-
"""B55 建条目(第二遍现算): corpus/raw/langsubtag.txt(BCP 47 子标签注册表, 段分隔是 %%) ⇎
corpus/raw/tz/zone1970.tab(时区表, 国家列借的正是注册表 region 型子标签)。
主轴是“注册表四个交叉引用字段自己没写明的值域约束”在两种口径下的表现: 整码判 ⇎ 拆片判;
第二轴是时区表用注释写下三条规则(第 4 列的充要条件 ⇎ 先按国家码排 ⇎ 其余按字母排), 再拿数据判它守不守。
锚只按特征子串从 _pick55.py 的候选池取(不手抄原文); 每个数字在这里独立现算并登记成 audit.py 里 B55V 的复算式,
零值折进 '0' 键; 同一字面的多条算式合成复合式, 全部相符才等于该字面。
采集侧(_pick55)与建条目侧在本文件 TIE 表上逐量对账, 不符即停机; 门槛内 _b55_scan 是第三遍。
磁盘 mtime 与文件里写的日期同不同秒只在本机成立, 进注不进门槛。"""
import io, os, re, sys, json, hashlib, collections

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = u'corpus'
NL = u'\n'
ENTRY = u'%s/babeltele/B55_subtag_registry_and_zone1970_tab.md' % C
J = json.load(io.open(os.path.join(ROOT, C, u'_b55meas.json'), encoding='utf-8'))
MM, POOL = J[u'meas'], J[u'pool']
TAGS, PATH = J[u'tags'], J[u'paths']
LB = dict(zip(TAGS, [u'子标签注册表', u'时区表']))
RD = lambda p: io.open(os.path.join(ROOT, p), encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATH]
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN ---


def pnorm(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


F = {}


def two(name, f):
    F[name] = [f(k) for k in TAGS]


two(u'bytes', lambda k: os.path.getsize(PATH[IDX[k]]))
two(u'chars', lambda k: len(TXT[IDX[k]]))
two(u'lines', lambda k: TXT[IDX[k]].count(NL))
two(u'segments', lambda k: len(TXT[IDX[k]].split(NL)))
two(u'nonblank', lambda k: len([l for l in TXT[IDX[k]].split(NL) if l.strip()]))
two(u'blank', lambda k: F[u'segments'][IDX[k]] - F[u'nonblank'][IDX[k]])
two(u'lt', lambda k: TXT[IDX[k]].count(u'<'))
two(u'gt', lambda k: TXT[IDX[k]].count(u'>'))
two(u'nonascii', lambda k: len([c for c in TXT[IDX[k]] if ord(c) > 127]))
two(u'tabs', lambda k: TXT[IDX[k]].count(u'\t'))
two(u'colon', lambda k: len(re.findall(u'^[A-Z][A-Za-z-]*:', TXT[IDX[k]], re.M)))
two(u'hash', lambda k: len(re.findall(u'^#', TXT[IDX[k]], re.M)))
two(u'ascii_eq', lambda k: 0 if [c for c in TXT[IDX[k]] if ord(c) > 127] else 1)
two(u'sha16', lambda k: hashlib.sha256(io.open(PATH[IDX[k]], 'rb').read()).hexdigest()[:16])
F[u'sha_distinct'] = len(set(F[u'sha16']))
F[u'eqc'] = sum(F[u'ascii_eq'])
F[u'ratio'] = int(round(1.0 * F[u'bytes'][0] / F[u'bytes'][1]))

R, Z = TXT[0], TXT[1]

# ---------- 注册表: 段、字段、类型 ----------
BLK = R.split(NL + u'%%' + NL)
F[u'records'] = len(BLK)
F[u'sep_occ'] = len([l for l in R.split(NL) if l.strip() == u'%%'])
F[u'sep_gap'] = F[u'records'] - 1 - F[u'sep_occ']


def parse(b):
    d = {}
    for line in b.split(NL):
        if not line.strip():
            continue
        m = re.match(u'^([A-Z][A-Za-z-]*):[ \t]*(.*)$', line) if line[:1] not in u' \t' else None
        if m:
            d.setdefault(m.group(1), []).append(m.group(2).strip())
        elif d:
            k = list(d)[-1]
            d[k][-1] = d[k][-1] + u' ' + line.strip()
    return d


RECS = [parse(b) for b in BLK]
F[u'hdr_outside'] = 1 if list(RECS[0]) == [u'File-Date'] else 0
FN = {}
for r in RECS:
    for k in r:
        FN[k] = FN.get(k, 0) + 1
F[u'key_n'] = FN
F[u'key_kinds'] = len(FN)
F[u'field_folded'] = sum(FN.values())
LN = {}
for b in BLK:
    for line in b.split(NL):
        m = re.match(u'^([A-Z][A-Za-z-]*):', line) if line[:1] not in u' \t' else None
        if m:
            LN[m.group(1)] = LN.get(m.group(1), 0) + 1
F[u'field_lines'] = sum(LN.values())
F[u'field_line_n'] = LN
F[u'field_extra'] = F[u'field_lines'] - F[u'field_folded']
F[u'field_kinds'] = len(LN)
F[u'pf_multi'] = len([b for b in BLK if len(re.findall(u'^Prefix:', b, re.M)) > 1])
F[u'pf_max'] = max(len(re.findall(u'^Prefix:', b, re.M)) for b in BLK)
F[u'dl_per_extra'] = F[u'field_line_n'][u'Description'] - FN[u'Description']
F[u'other_extra'] = F[u'field_extra'] - F[u'dl_per_extra'] - (F[u'field_line_n'][u'Prefix'] - FN[u'Prefix']) - \
    (F[u'field_line_n'][u'Comments'] - FN[u'Comments'])

TYPE = [u'language', u'extlang', u'script', u'region', u'variant', u'grandfathered', u'redundant']
TC = collections.Counter(r.get(u'Type', [u'<none>'])[0] for r in RECS)
F[u'type_n'] = dict((t, TC[t]) for t in TYPE)
F[u'type_none'] = TC[u'<none>']
F[u'type_kinds'] = len(TC)
SUB = [r for r in RECS if u'Subtag' in r]
F[u'subrec'] = len(SUB)
F[u'nosub'] = F[u'records'] - F[u'subrec']
F[u'tagrec'] = FN[u'Tag']
F[u'closed'] = F[u'subrec'] + F[u'tagrec'] + F[u'hdr_outside'] - F[u'records']
BY = dict((t, [r for r in SUB if r.get(u'Type', [u''])[0] == t]) for t in
          (u'language', u'extlang', u'script', u'region', u'variant'))
SET = dict((t, set(r[u'Subtag'][0] for r in BY[t])) for t in BY)
ALL_SUB = set(r[u'Subtag'][0] for r in SUB)
F[u'sub_distinct'] = len(ALL_SUB)
F[u'sub_repeat'] = F[u'subrec'] - F[u'sub_distinct']
F[u'sub_dupmax'] = max(collections.Counter(r[u'Subtag'][0] for r in SUB).values())
F[u'pref_distinct'] = len(set(r[u'Preferred-Value'][0] for r in RECS if u'Preferred-Value' in r))
F[u'dots'] = len([s for s in ALL_SUB if u'..' in s])

# ---------- 主轴: 四个交叉引用字段的两种口径 ----------
XK = [u'Suppress-Script', u'Macrolanguage', u'Preferred-Value', u'Prefix']
PREF = set(v for r in RECS for v in r.get(u'Preferred-Value', []))
XD = {u'Suppress-Script': SET[u'script'], u'Macrolanguage': SET[u'language'],
      u'Preferred-Value': ALL_SUB, u'Prefix': ALL_SUB | PREF}
XV = {k: ([], []) for k in XK}
F[u'x_field_n'], F[u'x_occ'], F[u'x_dist'], F[u'x_comp'] = [], [], [], []
F[u'x_vw'], F[u'x_vp'], F[u'x_dom'], F[u'x_eq'] = [], [], [], []
for k in XK:
    vals = LN.get(k) and [v for r in RECS for v in r.get(k, [])] or []
    whole = set(vals)
    pieces = set(p for v in whole for p in v.split(u'-'))
    dom = XD[k]
    vw = sorted(v for v in whole if v not in dom)
    vp = sorted(p for p in pieces if p not in dom)
    XV[k] = (vw, vp)
    F[u'x_field_n'].append(FN[k])
    F[u'x_occ'].append(len(vals))
    F[u'x_dist'].append(len(whole))
    F[u'x_comp'].append(len([v for v in whole if u'-' in v]))
    F[u'x_vw'].append(len(vw))
    F[u'x_vp'].append(len(vp))
    F[u'x_dom'].append(len(dom))
    F[u'x_eq'].append(len(vw) - len([v for v in whole if u'-' in v]))
F[u'viol_whole'] = sum(F[u'x_vw'])
F[u'viol_piece'] = sum(F[u'x_vp'])
F[u'compound'] = sum(F[u'x_comp'])
F[u'viol_minus_comp'] = F[u'viol_whole'] - F[u'compound']
F[u'x_occ_total'] = sum(F[u'x_occ'])
F[u'clean'] = len([i for i in range(4) if not F[u'x_vw'][i]])
F[u'clean_piece'] = len([i for i in range(4) if not F[u'x_vp'][i]])
F[u'pref_out'] = len(PREF - ALL_SUB)
F[u'dom_gap'] = F[u'x_dom'][1] - F[u'x_dom'][0]
F[u'pf_widen'] = F[u'x_dom'][3] - F[u'x_dom'][2]

# ---------- 长度签名 ----------
LC = collections.Counter(len(r[u'Subtag'][0]) for r in SUB)
F[u'sl_len'] = sorted(LC)
F[u'sl_n'] = [LC[i] for i in F[u'sl_len']]
F[u'sl_kinds'] = len(F[u'sl_len'])
F[u'sl_sum'] = sum(F[u'sl_n']) - F[u'subrec']


def tn(t):
    c = collections.Counter(len(r[u'Subtag'][0]) for r in BY[t])
    ks = sorted(c)
    return [c[i] for i in ks], ks


F[u'lang_n'], F[u'lang_k'] = tn(u'language')
F[u'reg_n'], F[u'reg_k'] = tn(u'region')
F[u'scr_n'], F[u'scr_k'] = tn(u'script')
F[u'var_n'], F[u'var_k'] = tn(u'variant')
F[u'ext_n'], F[u'ext_k'] = tn(u'extlang')

# ---------- Description 两口径 ----------
DL = re.findall(u'^Description:[ \t]*(.*)$', R, re.M)
F[u'desc_lines'] = len(DL)
F[u'desc_dist'] = len(set(DL))
F[u'desc_reuse'] = F[u'desc_lines'] - F[u'desc_dist']
DC = collections.Counter(DL)
F[u'desc_once'] = len([d for d, n in DC.items() if n == 1])
F[u'desc_multikind'] = len([d for d, n in DC.items() if n > 1])
F[u'desc_maxn'] = max(DC.values())
F[u'desc_maxv'] = sorted([d for d, n in DC.items() if n == F[u'desc_maxn']])
F[u'desc_multirec'] = len([b for b in BLK if len(re.findall(u'^Description:', b, re.M)) > 1])
F[u'desc_permax'] = max(len(re.findall(u'^Description:', b, re.M)) for b in BLK)
FDs = [r[u'Description'][-1] for r in RECS if u'Description' in r]
F[u'desc_fold'] = len(FDs)
F[u'desc_folddist'] = len(set(FDs))
F[u'desc_foldreuse'] = F[u'desc_fold'] - F[u'desc_folddist']
F[u'desc_distgap'] = F[u'desc_dist'] - F[u'desc_folddist']

# ---------- 日期账 ----------
AD = [r[u'Added'][0] for r in RECS if u'Added' in r]
DP = [(r.get(u'Subtag') or r.get(u'Preferred-Value') or r.get(u'Tag'))[0]
      for r in RECS if u'Deprecated' in r]
DPD = [(r.get(u'Subtag') or r.get(u'Preferred-Value') or r.get(u'Tag'))[0] for r in RECS if u'Deprecated' in r]
DPA = [(r[u'Deprecated'][0], r.get(u'Added', [None])[0]) for r in RECS if u'Deprecated' in r]
F[u'file_date'] = RECS[0][u'File-Date'][0]
F[u'added_n'] = len(AD)
F[u'added_dist'] = len(set(AD))
F[u'added_min'] = min(AD)
F[u'added_max'] = max(AD)
F[u'added_span'] = (int(F[u'added_max'][:4]) - int(F[u'added_min'][:4]))
F[u'dep_n'] = len(DPD)
F[u'dep_days'] = len(set(d[0] for d in DPA))
F[u'dep_before'] = len([d for d in DPA if d[1] and d[0] < d[1]])
F[u'added_after'] = len([a for a in AD if a > F[u'file_date']])
F[u'pref_dep'] = len([p for p in PREF if p in set(DPD)])
DK = [u'language', u'extlang', u'region', u'variant', u'grandfathered', u'redundant']
DC2 = collections.Counter(r.get(u'Type', [u'<none>'])[0] for r in RECS if u'Deprecated' in r)
F[u'dep_typed'] = [DC2[t] for t in DK]
F[u'dep_typed_kinds'] = len(DC2)
F[u'scope_n'] = [FN[u'Scope']]
SC = collections.Counter(r[u'Scope'][0] for r in RECS if u'Scope' in r)
F[u'scope_kinds'] = len(SC)
F[u'scope_coll'] = SC[u'collection']
F[u'scope_macro'] = SC[u'macrolanguage']
F[u'scope_special'] = SC[u'special']
F[u'scope_private'] = SC[u'private-use']
F[u'scope_sum'] = sum([F[u'scope_coll'], F[u'scope_macro'], F[u'scope_special'], F[u'scope_private']]) - FN[u'Scope']
F[u'cm_n'] = FN[u'Comments']
F[u'cm_lines'] = LN[u'Comments']
F[u'cm_chars'] = sum(len(r[u'Comments'][-1]) for r in RECS if u'Comments' in r)
F[u'cm_chars_line'] = sum(len(v) for r in RECS for v in r.get(u'Comments', []))
F[u'cm_caldiff'] = F[u'cm_chars_line'] - F[u'cm_chars']

# ---------- region 池 ⇎ 时区表国家列 ----------
REG = SET[u'region']
F[u'region_n'] = len(REG)
F[u'reg_alpha'] = len([r for r in REG if re.match(u'^[A-Z]{2}$', r)])
F[u'reg_digit'] = len([r for r in REG if re.match(u'^[0-9]{3}$', r)])
F[u'reg_other'] = len([r for r in REG if u'..' in r])
F[u'reg_sum'] = F[u'reg_alpha'] + F[u'reg_digit'] + F[u'reg_other'] - F[u'region_n']
F[u'reg_zz'] = 1 if u'ZZ' in REG else 0
F[u'reg_xq'] = len([r for r in REG if r[:1] in (u'X', u'Q')])
zl = [l.rstrip(u'\r') for l in Z.split(NL) if l.strip() and not l.startswith(u'#')]
F[u'z_rows'] = len(zl)
CO = set()
for l in zl:
    for c in l.split(u'\t')[0].split(u','):
        if c:
            CO.add(c)
CC = [l.split(u'\t')[0].split(u',') for l in zl]
F[u'z_countries'] = len(CO)
F[u'z_cc_sum'] = sum(len(c) for c in CC)
F[u'reg_shared'] = len(REG & CO)
F[u'z_only'] = len(CO - REG)
F[u'reg_only'] = len(REG - CO)
F[u'reg_alpha_only'] = len([r for r in (REG - CO) if re.match(u'^[A-Z]{2}$', r)])
F[u'reg_digit_only'] = len([r for r in (REG - CO) if re.match(u'^[0-9]{3}$', r)])
F[u'reg_range_only'] = len([r for r in (REG - CO) if u'..' in r])
F[u'reg_only_sum'] = F[u'reg_alpha_only'] + F[u'reg_digit_only'] + F[u'reg_range_only'] - F[u'reg_only']
F[u'z_multi_rows'] = len([c for c in CC if len(c) > 1])
F[u'z_maxm'] = max(len(c) for c in CC)
F[u'z_badfmt'] = len([l for l in zl if not re.match(u'^[A-Z]{2}(,[A-Z]{2})*$', l.split(u'\t')[0])])
F[u'z_col3'] = len([l for l in zl if len(l.split(u'\t')) == 3])
F[u'z_col4'] = len([l for l in zl if len(l.split(u'\t')) == 4])
F[u'z_col_sum'] = F[u'z_col3'] + F[u'z_col4'] - F[u'z_rows']


def dg(c):
    return [len(x) - 1 for x in re.findall(u'[+-]\\d+', c)]


LA = [dg(l.split(u'\t')[1]) for l in zl]
F[u'z_lat4'] = len([x for x in LA if x[0] == 4])
F[u'z_lat6'] = len([x for x in LA if x[0] == 6])
F[u'z_lon5'] = len([x for x in LA if x[1] == 5])
F[u'z_lon7'] = len([x for x in LA if x[1] == 7])
F[u'z_coord_sum'] = F[u'z_lat4'] + F[u'z_lat6'] - F[u'z_rows']
F[u'z_first_desc'] = len([1 for a, b in zip([c[0] for c in CC], [c[0] for c in CC][1:]) if b < a])
F[u'z_whole_un'] = len([c for c in CC if c != sorted(c)])
F[u'z_tail_un'] = len([c for c in CC if len(c) > 1 and c[1:] != sorted(c[1:])])
MC = collections.Counter(c for cs in CC for c in cs)
SH = set(c for c, n in MC.items() if n > 1)
F[u'z_shared_rows'] = len([cs for cs in CC if any(c in SH for c in cs)])
F[u'z4_pos'] = len([i for i in range(F[u'z_rows']) if len(zl[i].split(u'\t')) == 4
                    and not any(c in SH for c in CC[i])])
F[u'z4_neg'] = len([i for i in range(F[u'z_rows']) if len(zl[i].split(u'\t')) == 3
                    and any(c in SH for c in CC[i])])
F[u'z4_agree'] = F[u'z_rows'] - F[u'z4_pos'] - F[u'z4_neg']
F[u'z_at'] = len([l for l in Z.split(NL) if l.startswith(u'#@')])
F[u'z_tabbed'] = len([l for l in Z.split(NL) if l.startswith(u'#') and u'\t' in l])
F[u'z_cmt_only'] = F[u'hash'][1] - F[u'z_at']
F[u'z_tab_struct'] = 2 * F[u'z_col3'] + 3 * F[u'z_col4'] + 3 + F[u'z_at']
F[u'z_tab_diff'] = F[u'tabs'][1] - F[u'z_tab_struct']
ZC = [l.split(u'\t')[2] for l in zl]
F[u'z_zone_n'] = len(ZC)
F[u'z_zone_dist'] = len(set(ZC))
F[u'z_zone_dup'] = F[u'z_zone_n'] - F[u'z_zone_dist']
PRE = collections.Counter(z.split(u'/')[0] for z in ZC)
F[u'z_pre_kinds'] = len(PRE)
F[u'z_pre_max'] = max(PRE.values())
F[u'z_pre_min'] = min(PRE.values())
F[u'z_pre_maxv'] = sorted([p for p, n in PRE.items() if n == F[u'z_pre_max']])
F[u'z_pre_minv'] = sorted([p for p, n in PRE.items() if n == F[u'z_pre_min']])
F[u'z_slash'] = sum(z.count(u'/') for z in ZC)
F[u'z_first_zone'] = ZC[0]
F[u'z_last_zone'] = ZC[-1]

# ---------- 穿两源: 关键串 ⇎ 逐字锚候选池 ----------
CROSS = [u'region', u'script', u'language', u'Deprecated', u'Preferred-Value', u'Suppress-Script',
         u'Macrolanguage', u'File-Date', u'%%', u'AD', u'GB', u'Type:', u'Subtag:', u'Cyrl', u'Europe']
FAN = [pnorm(TXT[i]) for i in range(2)]
HS = [tuple(i for i in range(2) if pnorm(t) in FAN[i]) for t in CROSS]
F[u'hitkinds'] = len(CROSS)
F[u'hitboth'] = len([h for h in HS if len(h) == 2])
F[u'hitsingle'] = len([h for h in HS if len(h) == 1])
F[u'hitnone'] = len([h for h in HS if not h])
F[u'hitR'] = len([h for h in HS if h == (0,)])
F[u'hitZ'] = len([h for h in HS if h == (1,)])
F[u'bothw'] = u' ／ '.join([t for t, h in zip(CROSS, HS) if len(h) == 2])

POOL2, seen = [], set()
for tag, txt in zip(TAGS, TXT):
    for l in txt.split(NL):
        s = l.strip()
        k = pnorm(s)
        if len(s) < 12 or u'\t' in s or not k or k in seen:
            continue
        seen.add(k)
        POOL2.append((tag, len([i for i in range(2) if k in FAN[i]]), s))
for l in [zl[0], zl[-1], max(zl, key=lambda x: len(x.split(u'\t')[0].split(u',')))] + \
         [x for x in Z.split(NL) if x.startswith(u'#@')]:
    for f in l.split(u'\t'):
        s, k = f.strip(), pnorm(f.strip())
        if len(s) < 8 or not k or k in seen:
            continue
        seen.add(k)
        POOL2.append((u'Z', len([i for i in range(2) if k in FAN[i]]), s))
F[u'pool_n'] = len(POOL2)
F[u'poolR'] = len([p for p in POOL2 if p[0] == u'R'])
F[u'poolZ'] = len([p for p in POOL2 if p[0] == u'Z'])
F[u'pool_cross'] = len([p for p in POOL2 if p[1] > 1])
XC = [p for p in POOL2 if p[1] > 1]
F[u'x_verbatim'] = len([p for p in XC if p[2] in TXT[1 - IDX[p[0]]]])
F[u'x_normonly'] = F[u'pool_cross'] - F[u'x_verbatim']
F[u'x_names'] = u' ⇎ '.join([p[2] for p in XC])

# --- SCAN END ---

TIE = [(u'bytes', u'bytes', None), (u'chars', u'chars', None), (u'lines', u'lines', None),
       (u'segments', u'segments', None), (u'nonblank', u'nonblank', None), (u'blank', u'blank', None),
       (u'lt', u'lt', None), (u'gt', u'gt', None), (u'nonascii', u'nonascii', None),
       (u'tabs', u'tabs', None), (u'colon', u'colons', None), (u'records', u'records', None),
       (u'sep_occ', u'sep_occ', None), (u'hdr_outside', u'hdr_outside', None),
       (u'key_kinds', u'key_kinds', None), (u'subrec', u'subrec', None), (u'nosub', u'nosub', None),
       (u'tagrec', u'tag_field_n', None), (u'sub_distinct', u'sub_distinct', None),
       (u'sub_repeat', u'sub_repeat', None), (u'sub_dupmax', u'sub_dup_max', None),
       (u'pref_distinct', u'pref_distinct', None), (u'field_lines', u'field_lines', None),
       (u'field_folded', u'field_folded', None), (u'field_extra', u'field_extra', None),
       (u'pf_multi', u'prefix_multi_recs', None), (u'pf_max', u'prefix_max_per_rec', None),
       (u'viol_whole', u'viol_whole_total', None), (u'viol_piece', u'viol_piece_total', None),
       (u'compound', u'compound_total', None), (u'clean', u'fields_clean', None),
       (u'dots', u'dots_n', None), (u'sl_kinds', u'sub_len_kinds', None),
       (u'desc_lines', u'desc_lines', None), (u'desc_dist', u'desc_distinct_line', None),
       (u'desc_reuse', u'desc_reuse_line', None), (u'desc_multirec', u'desc_multi_recs', None),
       (u'desc_permax', u'desc_max_per_rec', None), (u'desc_fold', u'desc_fold_n', None),
       (u'desc_folddist', u'desc_fold_distinct', None), (u'desc_maxn', u'desc_max_line_n', None),
       (u'added_n', u'added_n', None), (u'added_dist', u'added_distinct', None),
       (u'added_min', u'added_min', None), (u'added_max', u'added_max', None),
       (u'dep_n', u'dep_n', None), (u'dep_days', u'dep_distinct_dates', None),
       (u'dep_before', u'dep_before_add_n', None), (u'added_after', u'added_after_file', None),
       (u'pref_dep', u'pref_dep_n', None), (u'cm_n', u'comment_field_n', None),
       (u'cm_chars', u'comments_chars', None), (u'scope_coll', u'scope_kinds', u'collection'),
       (u'region_n', u'region_n', None), (u'reg_alpha', u'reg_alpha', None),
       (u'reg_digit', u'reg_digit', None), (u'reg_zz', u'reg_ZZ', None), (u'reg_xq', u'reg_x', None),
       (u'z_rows', u'z_rows', None), (u'z_countries', u'z_countries', None),
       (u'reg_shared', u'reg_shared', None),
       (u'reg_only', u'reg_only', None), (u'reg_alpha_only', u'reg_alpha_only', None),
       (u'reg_digit_only', u'reg_digit_only', None), (u'z_multi_rows', u'z_multi_rows', None),
       (u'z_maxm', u'z_max_multi', None), (u'z_cc_sum', u'z_cc_sum', None),
       (u'z_lat4', u'z_lat_4', None), (u'z_lat6', u'z_lat_6', None),
       (u'z_col3', u'z_col3', None), (u'z_col4', u'z_col4', None),
       (u'z_at', u'z_at', None), (u'z_tabbed', u'z_tabbed', None),
       (u'z_shared_rows', u'z_rows_shared', None), (u'z4_agree', u'z_col4_match', None),
       (u'z_first_desc', u'z_first_desc', None), (u'z_whole_un', u'z_whole_unsorted', None),
       (u'z_tail_un', u'z_tail_unsorted', None), (u'z_pre_kinds', u'z_pre_kinds', None),
       (u'z_pre_max', u'z_pre_max', None), (u'z_pre_min', u'z_pre_min', None),
       (u'z_zone_n', u'z_zone_n', None), (u'z_zone_dist', u'z_zone_distinct', None),
       (u'z_first_zone', u'z_zone_first', None), (u'z_last_zone', u'z_zone_last', None),
       (u'file_date', u'file_date', None), (u'hitkinds', u'hitkinds', None),
       (u'hitboth', u'hitboth', None), (u'hitsingle', u'hitsingle', None),
       (u'hitR', u'hitR', None), (u'hitZ', u'hitZ', None), (u'bothw', u'both_names', None),
       (u'pool_n', u'pool_n', None), (u'pool_cross', u'pool_cross', None),
       (u'x_verbatim', None, None), (u'pref_out', u'pref_out_n', None),
       (u'dom_gap', None, None), (u'pf_widen', None, None)]
TIE = [t for t in TIE if t[1] is not None]


def mv(mk, ix):
    v = MM[mk]
    return v[ix] if isinstance(ix, (int, str)) and isinstance(v, (list, dict)) else v


BADK = [(bk, F[bk], mv(mk, ix)) for bk, mk, ix in TIE if F[bk] != mv(mk, ix)]
assert not BADK, BADK[:8]
assert F[u'sep_gap'] == 0 and F[u'closed'] == 0 and F[u'reg_sum'] == 0
assert F[u'viol_minus_comp'] == 0 and F[u'sl_sum'] == 0 and F[u'z_col_sum'] == 0
assert F[u'z_coord_sum'] == 0 and F[u'z_tab_diff'] == 0 and F[u'z_badfmt'] == 0
assert F[u'z_zone_dup'] == 0 and F[u'scope_sum'] == 0 and F[u'reg_only_sum'] == 0
assert F[u'z4_pos'] == 0 and F[u'z4_neg'] == 0 and F[u'x_verbatim'] == 0
assert F[u'pool_n'] == MM[u'pool_n'] and len(POOL2) == len(POOL), (F[u'pool_n'], len(POOL2))
assert F[u'hash'][1] == MM[u'z_hash'] and F[u'pref_distinct'] == MM[u'pref_distinct']
assert F[u'field_lines'] == F[u'colon'][0] and F[u'colon'][1] == 0
assert F[u'other_extra'] == 0
assert len(MM[u'z_only']) == F[u'z_only']
assert F[u'cm_lines'] == MM[u'comments_n'] and F[u'cm_caldiff'] > 0

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
    reg(s, u"B55V('%s'%s)" % (name, u'' if i is None else u', ' + repr(i)), note or name)
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
    got = [p for p in POOL if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
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
G[u'aHdr'] = AT(u'own', u'R', u'File-Date')
G[u'aType'] = AT(u'own', u'R', u'Type: language')
G[u'aRange'] = AT(u'own', u'R', u'qaa..qtz')
G[u'aScRange'] = AT(u'own', u'R', u'Qaaa..Qabx')
G[u'aRegQ'] = AT(u'own', u'R', u'QM..QZ')
G[u'aRegX'] = AT(u'own', u'R', u'XA..XZ')
G[u'aSup'] = AT(u'own', u'R', u'Suppress-Script: Latn')
G[u'aMacro'] = AT(u'own', u'R', u'Macrolanguage: zh')
G[u'aPref'] = AT(u'own', u'R', u'cmn-Hans')
G[u'aPfx'] = AT(u'own', u'R', u'Prefix: en-CA')
G[u'aPfxMulti'] = AT(u'own', u'R', u'oc-aranes')
G[u'aTag'] = AT(u'own', u'R', u'GB-oed')
G[u'aScope'] = AT(u'own', u'R', u'Scope: collection')
G[u'aCmtGB'] = AT(u'own', u'R', u'Channel Islands')
G[u'aCmt029'] = AT(u'own', u'R', u'Caribbean (029)')
G[u'aAdded'] = AT(u'own', u'R', u'Added: 2005-10-16')
G[u'aDep'] = AT(u'own', u'R', u'Deprecated: 1989-01-01')
G[u'aPrivate'] = AT(u'own', u'R', u'Private use')
G[u'aRed'] = AT(u'own', u'R', u'Type: redundant')
G[u'aSsi'] = AT(u'J2', u'R', u'Sô')
G[u'aTzHdr'] = AT(u'own', u'Z', u'tzdb')
G[u'aPublic'] = AT(u'own', u'Z', u'public domain')
G[u'aEggert'] = AT(u'own', u'Z', u'Eggert')
G[u'aIso3166'] = AT(u'own', u'Z', u'ISO 3166')
G[u'aIso6709'] = AT(u'own', u'Z', u'ISO 6709')
G[u'aCoordFmt'] = AT(u'own', u'Z', u'DDMMSS')
G[u'aIff'] = AT(u'own', u'Z', u'if and only if')
G[u'aSort'] = AT(u'own', u'Z', u'listed alphabetically')
G[u'aTerr'] = AT(u'own', u'Z', u'territorial claims', u'Mention RU')
G[u'aTabex'] = AT(u'own', u'Z', u'<tab>')
G[u'aFirst'] = AT(u'own', u'Z', u'Andorra')
G[u'aPR'] = AT(u'own', u'Z', u'Puerto_Rico')
G[u'aPRcc'] = AT(u'own', u'Z', u'PR,AG')
G[u'aAnt'] = AT(u'J2', u'Z', u'Antarctica/')
G[u'aAtl'] = AT(u'J2', u'Z', u'Atlantic/')
G[u'aCrd'] = AT(u'own', u'Z', u'+4230')

# ---------- 数字登记 ----------
G[u'by'] = JOIN(u'bytes', u'字节')
G[u'ln'] = JOIN(u'lines', u'换行')
G[u'nb'] = JOIN(u'nonblank', u'非空行')
G[u'ch'] = JOIN(u'chars', u'字符')
G[u'ltw'] = JOIN(u'lt', u"'<' 枚")
G[u'na'] = JOIN(u'nonascii', u'非 ASCII 枚')
G[u'tb'] = JOIN(u'tabs', u'制表符枚')
G[u'tbR'], G[u'tbZ'] = V(u'tabs', 0, u'制表符·注册表'), V(u'tabs', 1, u'制表符·时区表')
G[u'hsh'] = JOIN(u'hash', u"'#' 行")
G[u'byR'], G[u'byZ'] = V(u'bytes', 0, u'字节·注册表'), V(u'bytes', 1, u'字节·时区表')
G[u'eqc'] = V(u'eqc', None, u'字符数=字节数成立的份数')
G[u'ratio'] = V(u'ratio', None, u'字节比(倍)')
G[u'shaK'] = V(u'sha_distinct', None, u'sha16 种数')
G[u'rec'] = V(u'records')
G[u'sep'] = V(u'sep_occ')
G[u'sepap'] = V(u'sep_gap', None, u'段数减分隔符减一')
G[u'sub'] = V(u'subrec')
G[u'nosub'] = V(u'nosub')
G[u'tag'] = V(u'tagrec')
G[u'gf'] = V(u'type_n', u'grandfathered', u'grandfathered 段')
G[u'rd'] = V(u'type_n', u'redundant', u'redundant 段')
G[u'closed'] = V(u'closed', None, u'三类相加与段数之差')
G[u'fkeys'] = V(u'key_kinds', None, u'字段名种数')
G[u'flin'] = V(u'field_lines')
G[u'ffol'] = V(u'field_folded')
G[u'fext'] = V(u'field_extra')
G[u'pfmax'] = V(u'pf_max', None, u'单段 Prefix 最多行数')
G[u'pfmulti'] = V(u'pf_multi', None, u'带第二条以上 Prefix 的段数')
G[u'otd'] = V(u'other_extra', None, u'多行字段差里 Description/Prefix 之外的部分')
G[u'lg'] = u' ⇎ '.join(V(u'lang_n', i, u'language 长%d' % F[u'lang_k'][i]) for i in range(len(F[u'lang_n'])))
G[u'lgk'] = u' ⇎ '.join(str(x) for x in F[u'lang_k'])
G[u'regk'] = u' ⇎ '.join(str(x) for x in F[u'reg_k'])
G[u'sck'] = u' ⇎ '.join(str(x) for x in F[u'scr_k'])
G[u'vark'] = u' ⇎ '.join(str(x) for x in F[u'var_k'])
for i in range(len(F[u'reg_n'])):
    G[u'rg%d' % i] = V(u'reg_n', i, u'region 长%d 枚' % F[u'reg_k'][i])
for i in range(len(F[u'scr_n'])):
    G[u'sc%d' % i] = V(u'scr_n', i, u'script 长%d 枚' % F[u'scr_k'][i])
for i in range(len(F[u'var_n'])):
    G[u'va%d' % i] = V(u'var_n', i, u'variant 长%d 枚' % F[u'var_k'][i])
G[u'slk'] = V(u'sl_kinds', None, u'子标签长度种类')
for i in range(len(F[u'sl_len'])):
    G[u'sl%d' % F[u'sl_len'][i]] = V(u'sl_n', i, u'长 %d 字符的子标签枚数' % F[u'sl_len'][i])
G[u'slsum'] = V(u'sl_sum', None, u'长度分布相加与子标签段数之差')
G[u'sdist'] = V(u'sub_distinct')
G[u'srep'] = V(u'sub_repeat')
G[u'sdup'] = V(u'sub_dupmax', None, u'同一码最多共用段数')
G[u'dots'] = V(u'dots', None, u'写成区间的子标签枚数')
G[u'pvrec'] = V(u'x_field_n', 2, u'Preferred-Value 段数')
G[u'pfxrec'] = V(u'x_field_n', 3, u'Prefix 段数')
G[u'ssrec'] = V(u'x_field_n', 0, u'Suppress-Script 段数')
G[u'mlrec'] = V(u'x_field_n', 1, u'Macrolanguage 段数')
G[u'xocc'] = V(u'x_occ_total', None, u'四字段逐行值数')
G[u'ssocc'], G[u'mlocc'] = V(u'x_occ', 0, u'Script 引用处'), V(u'x_occ', 1, u'Macrolanguage 引用处')
G[u'pvocc'], G[u'pfxocc'] = V(u'x_occ', 2, u'Preferred-Value 引用处'), V(u'x_occ', 3, u'Prefix 引用处')
G[u'pfxlines'] = EXPR(str(F[u'field_line_n'][u'Prefix']), u"B55V('field_line_n')['Prefix']", u'Prefix 行数')
G[u'ssdist'], G[u'mldist'] = V(u'x_dist', 0, u'Script 不同值'), V(u'x_dist', 1, u'Macrolanguage 不同值')
G[u'pvdist'], G[u'pfxdist'] = V(u'x_dist', 2, u'Preferred-Value 不同值'), V(u'x_dist', 3, u'Prefix 不同值')
G[u'ss_dom'], G[u'ml_dom'] = V(u'x_dom', 0, u'script 码池'), V(u'x_dom', 1, u'language 码池')
G[u'pv_dom'], G[u'pf_dom'] = V(u'x_dom', 2, u'子标签码池'), V(u'x_dom', 3, u'子标签∪Preferred-Value')
G[u'domgap'] = V(u'dom_gap', None, u'language 码池减 script 码池')
G[u'pfx3'] = V(u'pref_out', None, u'只在 Preferred-Value 出现的码枚数')
G[u'pfxwiden'] = V(u'pf_widen', None, u'Prefix 值域比子标签池宽')
G[u'vw'], G[u'vp'] = V(u'viol_whole'), V(u'viol_piece')
G[u'pvw'], G[u'pfxw'] = V(u'x_vw', 2, u'Preferred-Value 整码越界'), V(u'x_vw', 3, u'Prefix 整码越界')
G[u'comp'] = V(u'compound', None, u'含连字符的值枚数')
G[u'vc'] = V(u'viol_minus_comp', None, u'越界数减复合数')
G[u'clean'] = V(u'clean', None, u'整码判零越界的字段数')
G[u'cleanp'] = V(u'clean_piece', None, u'拆片判零越界的字段数')
G[u'xcomp3'], G[u'xcomp14'] = V(u'x_comp', 2, u'Preferred-Value 复合值'), V(u'x_comp', 3, u'Prefix 复合值')
G[u'dl'], G[u'ddist'], G[u'dre'] = V(u'desc_lines'), V(u'desc_dist'), V(u'desc_reuse')
G[u'donce'], G[u'dmultikind'] = V(u'desc_once'), V(u'desc_multikind')
G[u'dmaxn'] = V(u'desc_maxn', None, u'同名共用码数上限')
G[u'dmultirec'], G[u'dpermax'] = V(u'desc_multirec'), V(u'desc_permax')
G[u'dfold'], G[u'dfd'], G[u'dfr'] = V(u'desc_fold'), V(u'desc_folddist'), V(u'desc_foldreuse')
G[u'ddgap'] = V(u'desc_distgap', None, u'逐行不同串减折叠不同串')
G[u'fdate'] = str(F[u'file_date'])
G[u'addn'], G[u'addd'] = V(u'added_n'), V(u'added_dist')
G[u'addmin'], G[u'addmax'] = str(F[u'added_min']), str(F[u'added_max'])
G[u'addspan'] = V(u'added_span', None, u'登用年份跨度')
G[u'depn'], G[u'depd'] = V(u'dep_n'), V(u'dep_days')
G[u'depbefore'] = V(u'dep_before', None, u'弃用日早于登用日的条数')
G[u'addafter'] = V(u'added_after', None, u'晚于 File-Date 的登用日')
G[u'pvdep'] = V(u'pref_dep', None, u'Preferred-Value 指向已弃码处数')
G[u'depsum'] = EXPR(str(sum(F[u'dep_typed'])), u"sum(B55V('dep_typed'))", u'弃用按类型相加')
for i, t in enumerate([u'language', u'extlang', u'region', u'variant', u'grandfathered', u'redundant']):
    G[u'dt%d' % i] = V(u'dep_typed', i, u'%s 型弃用' % t)
G[u'scopen'] = V(u'scope_n', 0, u'Scope 段数')
G[u'sckinds'] = V(u'scope_kinds', None, u'Scope 取值种数')
G[u'sccoll'], G[u'scmacro'] = V(u'scope_coll'), V(u'scope_macro')
G[u'scspec'], G[u'scpriv'] = V(u'scope_special'), V(u'scope_private')
G[u'scsum'] = V(u'scope_sum', None, u'Scope 四值相加与段数之差')
G[u'cmn'], G[u'cmc'] = V(u'cm_n'), V(u'cm_chars')
G[u'cmline'] = V(u'cm_lines', None, u'Comments 行数')
G[u'cmdiff'] = V(u'cm_caldiff', None, u'Comments 逐行与折叠的字符差')
G[u'tzlang'] = V(u'type_n', u'language', u'language 段数')
G[u'tzext'], G[u'tzscr'] = V(u'type_n', u'extlang'), V(u'type_n', u'script')
G[u'tzvar'] = V(u'type_n', u'variant', u'variant 段数')
G[u'tzreg'] = V(u'type_n', u'region', u'region 段数')
G[u'types'] = V(u'type_kinds', None, u'Type 取值种数')
G[u'region_n'] = V(u'region_n')
G[u'ra'], G[u'rdg'], G[u'ro'] = V(u'reg_alpha'), V(u'reg_digit'), V(u'reg_other')
G[u'regsum'] = V(u'reg_sum', None, u'region 三分相加与总数之差')
G[u'zz'] = V(u'reg_zz', None, u"'ZZ' 在不在 region 池")
G[u'xq'] = V(u'reg_xq', None, u'X 或 Q 开头的 region 枚数')
G[u'zcc'] = V(u'z_countries')
G[u'sh'] = V(u'reg_shared')
G[u'zonly'] = V(u'z_only', None, u'Z 有而 R 无')
G[u'ronly'] = V(u'reg_only', None, u'R 有而 Z 无')
G[u'rao'], G[u'rdo'], G[u'rro'] = V(u'reg_alpha_only'), V(u'reg_digit_only'), V(u'reg_range_only')
G[u'ros'] = V(u'reg_only_sum', None, u'三类相加与差集大小之差')
G[u'ccsum'] = V(u'z_cc_sum', None, u'国家格总出现次')
G[u'zmulti'], G[u'zmaxm'] = V(u'z_multi_rows'), V(u'z_maxm')
G[u'zrows'] = V(u'z_rows')
G[u'zcol3'], G[u'zcol4'] = V(u'z_col3'), V(u'z_col4')
G[u'zcolsum'] = V(u'z_col_sum', None, u'两种列数相加与行数之差')
G[u'zlat4'], G[u'zlat6'] = V(u'z_lat4'), V(u'z_lat6')
G[u'zlon5'], G[u'zlon7'] = V(u'z_lon5'), V(u'z_lon7')
G[u'zcrdsum'] = V(u'z_coord_sum', None, u'坐标两档相加与行数之差')
G[u'zfirst'] = V(u'z_first_desc', None, u'首码逆序处')
G[u'zwhoun'], G[u'ztailun'] = V(u'z_whole_un'), V(u'z_tail_un')
G[u'zshared'] = V(u'z_shared_rows', None, u'行内至少一枚码在他行也出现的行数')
G[u'zagree'] = V(u'z4_agree', None, u'第 4 列与充要条件相符的行')
G[u'z4pos'], G[u'z4neg'] = V(u'z4_pos'), V(u'z4_neg')
G[u'zat'] = V(u'z_at', None, u"'#@' 开头的行")
G[u'ztabbed'] = V(u'z_tabbed', None, u'带制表符的注释行')
G[u'zcmt'] = V(u'z_cmt_only', None, u'注释行里非 #@ 的部分')
G[u'ztabstruct'], G[u'ztabdiff'] = V(u'z_tab_struct'), V(u'z_tab_diff', None, u'制表符实数与结构推得之差')
G[u'zzn'], G[u'zzd'] = V(u'z_zone_n'), V(u'z_zone_dist')
G[u'zzdup'] = V(u'z_zone_dup', None, u'时区名总数减去重')
G[u'zprek'], G[u'zpmax'], G[u'zpmin'] = V(u'z_pre_kinds'), V(u'z_pre_max'), V(u'z_pre_min')
G[u'zslash'] = V(u'z_slash', None, u"时区名里 '/' 枚")
G[u'zbadfmt'] = V(u'z_badfmt', None, u'国家列格式不符的行')
G[u'hk'], G[u'hb'] = V(u'hitkinds'), V(u'hitboth')
G[u'hs'], G[u'hn'] = V(u'hitsingle'), V(u'hitnone')
G[u'hR'], G[u'hZ'] = V(u'hitR'), V(u'hitZ')
G[u'pn'] = V(u'pool_n', None, u'逐字锚候选池条数')
G[u'pr'], G[u'pz'] = V(u'poolR', None, u'池里注册表条数'), V(u'poolZ', None, u'池里时区表条数')
G[u'pc'] = V(u'pool_cross', None, u'归一后穿两源的池条数')
G[u'xv'] = V(u'x_verbatim', None, u'其中逐字也穿两源的条数')
G[u'xn'] = V(u'x_normonly', None, u'只靠归一键才同现的条数')
G[u'nat'] = TOK(u'anchor_total', u'锚在正文出现处数')
G[u'ndist'] = TOK(u'anchor_distinct', u'锚去重串数')
G[u'nerr'] = TOK(u'anchor_err', u'锚错配处数')
G[u'nsgl'] = TOK(u'anchor_single', u'只属一源的锚串数')
G[u'nboth'] = TOK(u'anchor_both', u'穿两源的锚串数')
G[u'checked'] = TOK(u'checks', u'锚成员检查次数')
G[u'tynone'] = V(u'type_none', None, u'空 Type 段数')
G[u'bothw'] = F[u'bothw']

LINE(u'🧭', u"两份文件靠同一批 ISO 3166 两位码相接: {aHdr} 是注册表的第一行, {aTzHdr} 是时区表注释的第一行。"
        u"R {byR} 字节／{lnR} 换行／'<' {ltR} 枚／制表符 {tbR} 枚 ⇎ Z {byZ} 字节／{lnZ} 换行／'<' {ltZ} 枚／制表符 {tbZ} 枚(字节比 {ratio} 倍, 差 {chd} 字符)。"
        u"注册表一个制表符也没有, 时区表那 {ltZ} 枚 '<' 全住在注释写的 '…<tab>…' 记法里({aTabex}), 数据行一枚不落。"
        u"两份都不是纯 ASCII(非 ASCII {na} 枚), 所以字符数=字节数在 {eqc} 份上成立; '#' 开头的行 R {hsR} ⇎ Z {hsZ}——R 没有注释语法, {rec} 段全算数据。"
        u"两份的 sha16 是 {shaK} 个不同的串(串本身只进解读注)。",
        lnR=V(u'lines', 0, u'换行·注册表'), lnZ=V(u'lines', 1, u'换行·时区表'),
        ltR=V(u'lt', 0, u"'<' 枚·注册表"), ltZ=V(u'lt', 1, u"'<' 枚·时区表"),
        tbR=V(u'tabs', 0, u'制表符·注册表'), tbZ=V(u'tabs', 1, u'制表符·时区表'),
        hsR=V(u'hash', 0, u"'#' 行·注册表"), hsZ=V(u'hash', 1, u"'#' 行·时区表"),
        chd=EXPR(str(F[u'chars'][0] - F[u'chars'][1]), u"B55V('chars',0)-B55V('chars',1)", u'字符差'))

LINE(u'📏', u"记录结构: 分隔行(整行只有两个 % 字符)出现 {sep} 次, 切出 {rec} 段——段数恰比分隔符多 1(差 {sepap} 段: 文件既不以分隔符开头也不以它结尾)。"
        u"{sub} 段带 Subtag ⇎ {nosub} 段不带; 后者 = {tag} 段用 Tag({gf} 段 grandfathered ⇎ {rd} 段 redundant)加 {aHdr} 那 1 段, 三档相加校住 {rec}(差 {closed})。"
        u"字段名 {fkeys} 种; 逐行数 '名:' 得 {flin} 处 ⇎ 每段同名只留一格的折叠口径 {ffol} 格, 差 {fext} 处, 其中 {otd} 处不在 Description ⇎ Prefix ⇎ Comments 三名之内(即除这三名以外没有字段在同段出现两次)。"
        u"同段多行不是罕见: Prefix 在 {pfmulti} 段里出现第二条以上, 单段最多 {pfmax} 行({aPfxMulti}), Description 单段最多 {dpermax} 行。"
        u"Type 有 {types} 种取值(含 {tynone} 种空值, 属 {aHdr} 那段): language {tzlang} ⇎ region {tzreg} ⇎ script {tzscr} ⇎ variant {tzvar} ⇎ extlang {tzext} ⇎ grandfathered {gf} ⇎ redundant {rd}({aRed})。", **G)

LINE(u'🔤', u"子标签的长度就是类型签名: {slk} 种长度——{sl2} 枚 2 字符 ⇎ {sl3} 枚 3 字符 ⇎ {sl4} 枚 4 ⇎ {sl5} 枚 5 ⇎ {sl6} 枚 6 ⇎ {sl7} 枚 7 ⇎ {sl8} 枚 8 ⇎ {sl10} 枚 10, 八档相加校住 {sub}(差 {slsum})。"
        u"切到类型内部: language 只有 {lgk} 三种长度({lg}), region {regk} 三种({rg0} ⇎ {rg1} ⇎ {rg2}), script {sck} 两种({sc0} ⇎ {sc1}), variant 占 {vark} 五种({va0} ⇎ {va1} ⇎ {va2} ⇎ {va3} ⇎ {va4})。"
        u"写成 '起..止' 的私用区间有 {dots} 枚, 每一枚都是它类型里的最长值: {aRange}(language 唯一 8 字符那枚) ⇎ {aScRange}(script 唯一 10 字符那枚) ⇎ {aRegQ} 与 {aRegX}(region 仅有的两枚 6 字符), 而 region 的 3 字符档正是数字码 {rdg} 枚({aCmt029} 那行注释直接引它们)。", **G)

LINE(u'🧱', u"闭世界两种口径——本条的主轴: 四个交叉引用字段各规定一个值域。{aSup} 的值只能取 script 码(池 {ss_dom} 枚), {aMacro} 只能取 language 码(池 {ml_dom} 枚), "
        u"{aPref} 只能取已登记子标签(池 {pv_dom} 枚), {aPfx} 取子标签或某个 Preferred-Value(池 {pf_dom} 枚)。"
        u"逐行取到 {xocc} 个字段值(其中 Prefix {pfxlines} 行 ⇎ 只按段折叠是 {pfxrec} 格), 于是有两种判法: "
        u"整码判(把整个值当一个码, 同一个值在几段里重复也只计一枚)越界 {vw} 枚 ⇎ 拆片判(按 '-' 切开逐片判)越界 {vp} 枚。"
        u"两数之差不是抽样差异: 越界的 {vw} 枚与含 '-' 的 {comp} 枚同数(差 {vc}), 也就是整码判报的每一例都是一个复合标签——"
        u"Prefix 独占 {pfxw} 枚(如 {aPfx}), Preferred-Value 占 {pvw} 枚(如 {aPref}), 而 {ssrec} 段 Script 引用 ⇎ {mlrec} 段 Macrolanguage 引用两口径都零越界(整码判零越界的 {clean} 个 ⇎ 拆片判零越界的 {cleanp} 个)。"
        u"所以“这张表有没有越界值”取决于先问哪一种: 问“它是码吗”答有 {vw} 个不是, 问“它的每一片都是码吗”答 {vp} 个不是。", **G)

LINE(u'🧲', u"值域大小并不对称: script 码池 {ss_dom} ⇎ language 码池 {ml_dom}(差 {domgap} 枚), 而子标签全集 {sdist} 枚 = 七类里带 Subtag 的 {sub} 段去掉同码重复({srep} 枚, 同一码最多被 {sdup} 段共用)。"
        u"Prefix 的值域要比子标签全集另加 {pfx3} 枚——那 {pfx3} 枚从未作为 Subtag 登记, 只作为 Preferred-Value 出现({aPref}), "
        u"于是 {pf_dom} = {pv_dom} + {pfx3}(宽出 {pfxwiden} 枚); 恰好 Preferred-Value 整码判的全部越界就是这 {pvw} 枚。"
        u"同一个事实的两面: 注册表把复合码收进 Preferred-Value 的值域, 却没收进 Subtag 的登记表。", **G)

LINE(u'🖼', u"region 池 ⇎ 时区表的国家列: region 型子标签 {region_n} 枚 = 两位码 {ra} ⇎ 三位数字码 {rdg} ⇎ 区间 {ro}(相加校住 {region_n}, 差 {regsum}), 其中 {xq} 枚以 X 或 Q 开头(私用与保留段: {aRegQ} ⇎ {aRegX}), 'ZZ' 在池里({zz} 枚)。"
        u"时区表国家列去重得 {zcc} 枚, 与 region 交 {sh} 枚 ⇎ 时区表有而注册表无 {zonly} 枚 ⇎ 注册表有而时区表无 {ronly} 枚; "
        u"那 {ronly} 枚拆开是两位码 {rao} ⇎ 三位码 {rdo} ⇎ 区间 {rro}(相加校住 {ronly}, 差 {ros})——数字码与区间本来就不可能是 ISO 3166 国家码, 于是“缺 {ronly} 枚”里只有 {rao} 枚是真缺口。"
        u"国家格总出现 {ccsum} 次(一格一枚), 多国家行 {zmulti} 行, 最多一行 {zmaxm} 国({aPRcc}); 国家列格式不符的 {zbadfmt} 行。", **G)

LINE(u'📐', u"时区表把规则写在注释里, 再交给数据判: {aIff} 说第 4 列“当且仅当”——按数据判“行内至少一枚码在他行也出现”的行 {zshared} ⇎ 真带第 4 列的行 {zcol4}, "
        u"多余 {z4pos} 行 ⇎ 缺失 {z4neg} 行, 相符 {zagree}/{zrows} 行(整条充要式在库内成立)。"
        u"{aSort} 那半句管的是多国行: 人口最多的那国放在首位, “其余”才按国家码字母排——首国按人口挑, 不归字母管, 于是判法有两种: "
        u"整列按字母判 {zwhoun} 行不守 ⇎ 只判首国之外的 {ztailun} 行不守; 注释承诺的是后一种, 所以前一种读法数出的 {zwhoun} 行是过度解读, 不是缺陷。"
        u"整表另有“先按国家码排”, 按首码判逆序 {zfirst} 处; 后一种读法上唯一的失守是 {zmaxm} 国那一行 {aPR}(首国之外 {zmaxm} 减 1 枚没排好)。"
        u"坐标两档: {aCoordFmt} 写了两种写法, 数据里分钟级 {zlat4} 行(纬度 4 位 ⇎ 经度 5 位) ⇎ 秒级 {zlat6} 行(纬度 6 位 ⇎ 经度 7 位), 两档相加校住 {zrows}(差 {zcrdsum})。"
        u"制表符也能推: 3 列 {zcol3} 行 ×2 加 4 列 {zcol4} 行 ×3 加那条列名注释行的 3 枚加 {zat} 行 '#@' 各 1 枚 = {ztabstruct} ⇎ 数出来 {tbZ}, 差 {ztabdiff}。", **G)

LINE(u'🧵', u"Description 也有两种口径: 逐行 {dl} 处／{ddist} 个不同串／复用 {dre} 次(只出现一次的 {donce} 条 ⇎ 出现两次以上的 {dmultikind} 条); "
        u"每段只留最后一条则 {dfold} 格／{dfd} 个不同／复用 {dfr} 次, 两口径的“不同串”差 {ddgap} 条。"
        u"同一记录可写多行说明: {dmultirec} 段带第二条以上, 单段最多 {dpermax} 行。"
        u"复用最高的一组是 {aPrivate}, 被 {dmaxn} 枚码共用; 名字本身在注册表与两源之外没有参照物, 所以只报数。"
        u"Subtag 侧同样有重复: {sub} 段 ⇎ {sdist} 个不同码(重复 {srep})——一个码两段的典型是 extlang 与 language 同名同形。"
        u"Scope 只 {sckinds} 种取值(collection {sccoll} ⇎ macrolanguage {scmacro} ⇎ special {scspec} ⇎ private-use {scpriv}, 相加校住 {scopen}, 差 {scsum}), "
        u"其中 macrolanguage 档与 {aMacro} 那 {mlrec} 段互相定义着对方。Comments 字段 {cmn} 段／{cmline} 行／折叠口径 {cmc} 字符(两口径差 {cmdiff} 字符, 因为有一段写了两行 Comments), 里面既有 {aCmtGB} 这种领土变更, 也有 {aCmt029} 这种直接引数字码的说明。", **G)

LINE(u'⏳', u"日期账: {aHdr} 声明 File-Date {fdate}; {aAdded} 这类 Added 行 {addn} 处／{addd} 个不同日, 最早 {addmin} ⇎ 最晚 {addmax}(年份跨 {addspan} 载), "
        u"晚于 File-Date 的 {addafter} 条。Deprecated {depn} 条／{depd} 个不同弃用日, 按类型是 {dt0} ⇎ {dt1} ⇎ {dt2} ⇎ {dt3} ⇎ {dt4} ⇎ {dt5}(相加 {depsum} 校住 {depn})。"
        u"其中 {depbefore} 条的弃用日早于本段自己的登用日({aDep} 对 {aAdded}), 另有 {pvdep} 处 Preferred-Value 指向已弃用的码——"
        u"判词此处只记数; 这 {depbefore} 条在表内的形状(各是什么类型、登用日是否同一天)由 ⛓注现查, 而两份日期为何错位仍不可由在库文件判定。", **G)

LINE(u'🗂', u"关键串穿两源 {hk} 枚(归一键: 只留字母数字并小写) ⇒ 两源同现 {hb} 枚 ⇎ 只现一源 {hs} 枚(注册表独占 {hR}, 时区表独占 {hZ}) ⇎ 一枚不中 {hn} 枚; 同现的是 {bothw}。"
        u"逐字锚候选池 {pn} 条(注册表 {pr} ⇎ 时区表 {pz}): 整行取 ≥12 字符且不含制表符, 按时区表的行全是制表分列, 另取其片段 ≥8 字符。"
        u"池里归一后穿两源的只有 {pc} 条——{aSsi} ⇎ {aAnt} ⇎ {aAtl}, 三条全是词形巧合: 归一键把 'Sô' 的 'ô' 与 'Antarctica/' 的尾斜杠都吃掉, "
        u"而按原样逐字判在两源另一源里一条都找不到({xv} 条, 于是 {xn} 条只活在归一口径里)。"
        u"这条口径差写进门槛: 短语级同现 {hb} 枚 ⇎ 逐字级同现 {xv} 枚 ⇎ 归一后池内同现 {pc} 条, 三个数各问各的。", **G)

LINE(u'🧪', u"这条的可核事实分三档, 第一档全部由两源字节现推({aHdr} ⇎ {aPublic} ⇎ {aXsamp}) ⇒ 第一档 B55V 可复算: 两源的字节/换行/段/'<'/制表符/'#'行/非 ASCII, "
        u"段数与分隔符差 {sepap}, 三档段数闭合 {closed}, 字段行的逐行⇎折叠差 {fext}(其余字段 {otd}), "
        u"四字段两口径矩阵(整码 {vw} ⇎ 拆片 {vp}, 复合差 {vc}), 值域宽度差 {pfxwiden}, 长度八档闭合 {slsum}, "
        u"region 三分闭合 {regsum} ⇎ 差集三分闭合 {ros}, 第 4 列充要条件相符 {zagree}/{zrows}, 制表符结构推得差 {ztabdiff}, 坐标两档闭合 {zcrdsum}, "
        u"以及锚的归属(下面报数)。"
        u"第二档只在本机成立: 两份字节的磁盘 mtime 与文件里写的日期谁新谁旧——它进注不进门槛, 因为门槛要能在任何一份拷贝上重跑。"
        u"第三档不可核, 由成因决定: {depbefore} 条弃用日早于登用日的来历, 'The most populous city' 那条首位选择规则要有人口数据才能判, "
        u"{aTerr} 背后的领土主张, 注册表由哪个机构按什么流程更新, 以及 {dots} 枚私用区间“归谁分配”——库里只有这两份字节。"
        u"锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 {nat} 处／{ndist} 条去重串, 归属由正文现推, "
        u"每条对两源逐一判成员共 {checked} 次检查, 单源 {nsgl} ⇎ 两源同现 {nboth}, 错配 {nerr} 处。",
        aXsamp=AT(u'own', u'R', u'X-SAMPA'), **G)

LINE(u'∴', u"骨架 ⇒ ① 两源字节 {by}, 换行 {ln}, 非空行 {nb}, '制表符' {tb}, 非 ASCII {na}, '#' 行 {hsh}; "
           u"② 注册表是段表: {rec} 段由 {sep} 行分隔符切出, {sub} 段带 Subtag ⇎ {nosub} 段不带, 字段名 {fkeys} 种, 逐行 {flin} ⇎ 折叠 {ffol}; "
           u"③ 主轴: 四字段 {xocc} 个值, 整码判越界 {vw} ⇎ 拆片判越界 {vp}, 越界数与复合数差 {vc}, 两口径都干净的 {clean} ⇎ {cleanp} 个; "
           u"④ 值域: {ss_dom} ⇎ {ml_dom} ⇎ {pv_dom} ⇎ {pf_dom}, 最宽一档比子标签池宽 {pfxwiden} 枚; "
           u"⑤ 长度签名 {slk} 档闭合 {slsum}, 私用区间 {dots} 枚各为其类型最长; "
           u"⑥ 跨文件 join: region {region_n} ⇎ 国家码 {zcc}, 交集 {sh}, 两向差 {zonly} ⇎ {ronly}(其中真缺口 {rao}); "
           u"⑦ 时区表自写规则对数据: 第 4 列充要 {z4pos}+{z4neg} 违例 ⇎ 首码逆序 {zfirst} ⇎ 整列 {zwhoun} ⇎ 去首国 {ztailun}, 坐标 {zlat4} ⇎ {zlat6}, 制表符差 {ztabdiff}; "
           u"⑧ 日期 {addn} 处／{addd} 日 ⇎ {depn} 条弃用, 反向 {depbefore}, 指向已弃 {pvdep}; 穿两源短语 {hb} 枚 ⇎ 逐字 {xv} 条。"
           u"判词: 一张表说“值必须是一个码”, 另一张表把同一批码用作国家列——两份文件对同一串字母的约束一个是硬值域一个是引用, "
           u"而 {vw} 枚“越界”全是因为判法把一个复合标签当一个标签; 换一根口径, 同一批字节给的是 {vp} 而不是 {vw}。", **G)

LINE(u'ℒ', u"方法 ⇒ 遇到“字段值必须是另一张表里的码”这种约束, 先问判法再问结论: "
        u"本条把四个字段各判两遍(整码 ⇎ 拆片), {vw} ⇎ {vp} 两数并写, 并把“越界的全是复合标签”写成差值键 {vc} 而不是靠断言假设; "
        u"把段的账写成三档相加({sub} ⇎ {tag} ⇎ {hdrn}), 把字段的账写成两口径相减({flin} ⇎ {ffol} = {fext}), 且证明余下 {otd} 处不属于其它字段; "
        u"把跨文件的 join 写成双向差({zonly} ⇎ {ronly})再把并集侧拆开({rao} ⇎ {rdo} ⇎ {rro}), 免得“缺 {ronly} 枚”被读成 {ronly} 个错误; "
        u"把注释里的规则拿数据判(第 4 列充要 {zagree}／{zrows}, 排序首码 {zfirst}, 其余 {zwhoun} ⇎ {ztailun}), "
        u"并且把两种排序口径都报——只报整列判的那 {zwhoun} 行会显得这张表更不守规矩; "
        u"最后把归一键能穿、逐字串不能穿的那 {pc} 条词形巧合单独计一笔({xv} 条逐字同现)。",
        hdrn=V(u'hdr_outside', None, u'只有 File-Date 的段数'), **G)

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 两源各 {ch0} ⇎ {ch1} 字符, 窗口只能取锚点触到的行; "
         u"而本条的结论全是跨行量: {xocc} 个字段值的两口径矩阵、{rec} 段的三档闭合、{slk} 档长度签名、"
         u"{zagree}／{zrows} 行的充要条件核对、{dl} 行 Description 的两口径复用。"
         u"尤其“整码判 {vw} ⇎ 拆片判 {vp}”这一对, 任何单窗口都装不下四字段各自的复合值清单。"
         u"读它请按“这个数是对哪个字段、用哪种判法数出来的”来读, 而不是按“少抄了多少原文”。",
         ch0=V(u'chars', 0, u'字符·注册表'), ch1=V(u'chars', 1, u'字符·时区表'), **G)

assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([RZ])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
HITC = dict((a, tuple(i for i in range(2) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]), u'both': len([a for a in ANCH if len(HITC[a]) == 2])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_both': CLS[u'both'], u'checks': DIST * 2}
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'both'] == DIST
for k, v in sorted(AMETA.items()):
    reg(str(v), u"B55V('%s')" % k, TOKV.get(k, k))
for n in (u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single', u'anchor_both', u'checks'):
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
assert u'◘' not in body, u'锚统计量占位符未回填'
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(os.path.join(ROOT, C, u'_deriv55.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(os.path.join(ROOT, C, u'_b55flat.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(os.path.join(ROOT, C, u'_atoms55.txt'), 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[RZ]⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == (1 if c == u'single' else 2)]))
                       for c in (u'single', u'both')),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV), u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': 2, u'flat': F,
      u'meas_tie_keys': [b for b, _, _ in TIE]}
json.dump(CH, io.open(os.path.join(ROOT, C, u'_b55checks.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

srcline = (u'src: ' + u' ⇎ '.join(u'%s (%d 字节／非空行 %d／\'<\' %d 枚／制表符 %d 枚)' % (PATH[i], F[u'bytes'][i], F[u'nonblank'][i],
               F[u'lt'][i], F[u'tabs'][i]) for i in range(2)) +
           u' (两份没有共同的版本日期: 注册表把 File-Date 写成 ' + F[u'file_date'] + u' 一行, 时区表把出处写成 '
           u'From Paul Eggert (2025-05-15) 一条注释; 磁盘 mtime 与这两个日期谁新谁旧只在本机成立, 不进门槛)\n')
联结 = (u'；联结不是“同一份数据的两种序列化”, 而是一张表 ⇎ 一张借它的码当列值的表: 注册表 %d 字节／%d 段, 每段以一行两个 %% 字符分隔, '
        u'四个交叉引用字段规定的值域在两种判法下给出 %d ⇎ %d 个越界值(越界的全是含连字符的复合标签, 共 %d 枚); '
        u'时区表 %d 字节／%d 数据行, 国家列的 %d 枚两位码全部落在注册表 region 型的 %d 枚里(反向缺 %d 枚, 其中 %d 枚本来就是数字码与区间), '
        u'而它注释自写的三条规则里, 第 4 列的充要条件核对到 %d／%d 行, 排序声明在整列口径下 %d 行不守 ⇎ 去掉每行首国的口径下 %d 行不守\n') % (
    F[u'bytes'][0], F[u'records'], F[u'viol_whole'], F[u'viol_piece'], F[u'compound'],
    F[u'bytes'][1], F[u'z_rows'], F[u'z_countries'], F[u'region_n'], F[u'reg_only'],
    F[u'reg_digit_only'] + F[u'reg_range_only'], F[u'z4_agree'], F[u'z_rows'], F[u'z_whole_un'], F[u'z_tail_un'])
text = (u'# B55 一张子标签注册表 ⇎ 一张把它的码当国家列的时区表：%d 枚越界值在两种判法下是 %d 个也是 %d 个\n' % (
    F[u'viol_whole'], F[u'viol_whole'], F[u'viol_piece']))
text += (srcline + 联结 +
         u'tags: 段表与分隔符 字段逐行⇎折叠两口径 交叉引用值域矩阵 整码判⇎拆片判 值域宽度不对称 子标签长度签名 私用区间码 '
         u'跨文件双向差集 region 数字码 ISO6709 坐标位数分档 第 4 列充要条件核对 排序声明两种口径核对 制表符可由列结构推得 '
         u'Description 多行与复用 日期账与反向时序 归一锚假同现须逐字复查 锚归属由正文现推\n' +
         u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
         u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
         u'## ⛓解读注\n\n（此段由 corpus/_fill55.py 从 corpus/_b55checks.json 与 corpus/_b55meas.json 现算写入）\n')
io.open(os.path.join(ROOT, ENTRY), 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d 串 ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'单源 %d ⇎ 两源同现 %d ⇎ 错配 %d ｜ 池内取用 %d' % (CLS[u'single'], CLS[u'both'], len(ERR), CH[u'pool_used']))
print(u'DERIV %d 键 ⇎ 复算点 %d ｜ 同数共键 %d 组(复合式) ｜ 0 键折 %d 项' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO)))
for k, v in sorted(COLL.items(), key=lambda x: -len(x[1]))[:8]:
    print(u'  同数 %s ← %s' % (k, u' ⇎ '.join(v)))
print(u'残留未替换占位符 %d ｜ 未点名花括号 %d' % (
    len(re.findall(u'◘', body)), len(re.findall(u'[{][a-zA-Z_0-9]+[}]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))))
print(u'锚内拉丁 %d ｜ 锚外拉丁 %d ｜ 标签 %d 枚 ｜ 扁平键 %d 个' % (
    CH[u'letters_in'], CH[u'letters_out'], CH[u'tagn'], len(F)))
