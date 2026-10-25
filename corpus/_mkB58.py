# -*- coding: utf-8 -*-
"""B58 建条目(第二遍现算, 四源): T = raw/cvss/cvss_v30_spec.html ⇎ O = cvss_v31_spec.html
⇎ F = cvss_v40_spec.html ⇎ N = cvss_examples.html (FIRST 官方四份一手文书, 工程技术学科)。
主轴: 同一条向量该打几分。v3.0 与 v3.1 把同一套闭式算术各写一遍(基础分系数 8 项逐一相等、44 条权重三元组全等),
只在环境分子式上改指数并把 0.9731 乘进去, 且 v3.1 自己写下 "which differs from CVSS v3.0";
v4.0 一个算式都不给, 换成 MacroVector 查表 + EQ1..EQ6 布尔约束; 算例文档把同一 CVE 的两代分数并排印出来。
配套轴: 全 2592 条合法基础向量上两代逐条同分; 三种“向上进到 0.1”的实现与精确小数(Fraction)判据三方对账;
非单调违例 114 ⇎ 6 的三档账(改指数只消掉未封顶那一支); 文档自陈的浮点陷阱在基础分全空间不可达。
第二遍的独立性: 系数从“含关键词的整行按 token 位置读”(pick 用方程段正则捕获), 权重按“<tr> 切块 + 组头命中定段 + 首字母带例外定缩写”
(pick 用逐行游标与全名映射), 单调性按“同一维 N<L<H 链 + 组合缓存”判(pick 逐对现算), 取整另写两种 ceil 变体,
搬运率(整行共用集)与算例配对是本遍新增的第二套切法; 每个共有量在末尾与 _pick58.py 逐量对账(不符只报不停机)。
门槛内 _b58_scan 是第三遍, 锚归属由条目正文现推。抓取时刻与磁盘 mtime、这批 HTML 是否各版当前发布、
v4.0 印出的分数在库内能否复算(v4.0 规范不给算式) 不可由在库文件判定, 进注不进门槛。"""
import io, os, re, sys, json, math, hashlib
from fractions import Fraction as Fr
from collections import Counter
from itertools import product

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = u'%s/babeltele/B58_one_vector_three_arithmetics.md' % C
M = json.load(io.open(u'corpus/_b58meas.json', encoding='utf-8'))
PATH = [u'corpus/raw/cvss/cvss_v30_spec.html', u'corpus/raw/cvss/cvss_v31_spec.html',
        u'corpus/raw/cvss/cvss_v40_spec.html', u'corpus/raw/cvss/cvss_examples.html']
TAGS = [u'T', u'O', u'F', u'N']
LB = dict(zip(TAGS, [u'v3.0 规范', u'v3.1 规范', u'v4.0 规范', u'算例文档']))
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATH]
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN --- (corpus/_wire58.py 把这一段机械切进 audit.py::_b58_scan)
ENT = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'),
       (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'),
       (u'&#215;', u'x'), (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"),
       (u'&mdash;', u'-'), (u'&ndash;', u'-'), (u'&deg;', u'deg'), (u'&infin;', u'inf')]
UNI = [(u' ', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
       (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->')]


def strip(s, br=u' '):
    """转码层: 注释 -> <br> -> 标签 -> 实体 -> unicode 折 ASCII -> 并空白(颠倒会吃掉含 &lt; 的整行)."""
    s = re.sub(u'(?s)<!--.*?-->', u'', s)
    s = re.sub(u'(?is)<br[^>]*>', br, s)
    s = re.sub(u'(?s)<[^>]+>', u'', s)
    for a, b in ENT + UNI:
        s = s.replace(a, b)
    return re.sub(u'[ \t]+', u' ', s).strip()


BODY = [strip(TXT[i]) for i in range(4)]
LST = [[strip(l, br=u' | ') for l in TXT[i].split(NL)] for i in range(4)]
F = {}
NN4 = 4


def four(name, f):
    F[name] = [f(k) for k in range(NN4)]


# ---------- 形状档 ----------
four(u'bytes', lambda i: os.path.getsize(PATH[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'lines', lambda i: TXT[i].count(NL))
four(u'nonblank', lambda i: len([l for l in TXT[i].split(NL) if l.strip()]))
four(u'tabs', lambda i: TXT[i].count(u'\t'))
four(u'nonascii', lambda i: len([c for c in TXT[i] if ord(c) > 127]))
four(u'bom', lambda i: 1 if TXT[i][:1] == u'﻿' else 0)
four(u'maxlen', lambda i: max(len(l) for l in TXT[i].split(NL)))
four(u'meanlen', lambda i: int(round(1.0 * sum(len(l) for l in TXT[i].split(NL) if l.strip()) /
                                       max(1, len([l for l in TXT[i].split(NL) if l.strip()])))))
four(u'sha16', lambda i: hashlib.sha256(io.open(PATH[i], 'rb').read()).hexdigest()[:16])
four(u'final_nl', lambda i: 1 if TXT[i].endswith(NL) else 0)
four(u'table_tags', lambda i: len(re.findall(u'(?is)<table', TXT[i])))
four(u'tr_rows', lambda i: len(re.findall(u'(?is)<tr', TXT[i])))
F[u'tr_rows_ratio'] = F[u'tr_rows'][3] // F[u'tr_rows'][0]
F[u'tr_rows_rest'] = F[u'tr_rows'][3] % F[u'tr_rows'][0]
F[u'tr_rows_div_close'] = F[u'tr_rows'][0] * F[u'tr_rows_ratio'] + F[u'tr_rows_rest'] - F[u'tr_rows'][3]
four(u'br_tags', lambda i: len(re.findall(u'(?is)<br', TXT[i])))
four(u'sup_tags', lambda i: len(re.findall(u'(?is)<sup', TXT[i])))
four(u'h_all', lambda i: len(re.findall(u'(?is)<h[1-6][ >]', TXT[i])))
four(u'ent_all', lambda i: len(re.findall(u'&[a-zA-Z#0-9]+;', TXT[i])))
four(u'ent_lt', lambda i: TXT[i].count(u'&lt;'))
four(u'minusuni', lambda i: TXT[i].count(u'−'))
four(u'nbsp', lambda i: TXT[i].count(u'&nbsp;') + TXT[i].count(u' '))
LONG = [max(TXT[i].split(NL), key=len) for i in range(4)]
F[u'maxline_len'] = [len(x) for x in LONG]
F[u'maxline_shared'] = 1 if len(set(LONG)) == 1 else 0
F[u'sha_distinct'] = len(set(F[u'sha16']))

# ---------- 词面指纹 ----------
def cnt(i, s):
    return BODY[i].count(s)


for nm, w in ((u'ar_ru', u'Roundup'), (u'ar_ru_up', u'Round up'), (u'ar_k642', u'6.42'),
              (u'ar_k752', u'7.52'), (u'ar_k822', u'8.22'), (u'ar_k108', u'1.08'),
              (u'ar_k9731', u'0.9731'), (u'ar_k0915', u'0.915'), (u'ar_pseudo', u'pseudocode'),
              (u'ar_appA', u'Appendix A'), (u'ar_floattrap', u'0.30000000000000004'),
              (u'bl_mv', u'MacroVector'), (u'bl_lookup', u'lookup table'),
              (u'bl_interp', u'interpolation'), (u'bl_cons', u'Constraints'),
              (u'sp_negligible', u'Negligible'), (u'sp_prov_urg', u'Provider Urgency'),
              (u'sp_exploitability', u'Exploitability'), (u'sp_isc', u'ISCBase'),
              (u'sp_iss', u'ISS'), (u'sp_miss', u'MISS'), (u'sp_diff30', u'differs from CVSS v3.0'),
              (u'sp_safety', u'Safety')):
    four(nm, lambda i, w=w: TXT[i].count(w))
for nm, w in ((u'ar_ru', u'Roundup'), (u'ar_ru_up', u'Round up'), (u'bl_mv', u'MacroVector'),
              (u'bl_lookup', u'lookup table'), (u'bl_interp', u'interpolation'),
              (u'bl_cons', u'constraints'), (u'sp_negligible', u'Negligible')):
    four(nm + u'_body', lambda i, w=w: BODY[i].count(w))
four(u'arith_any', lambda i: 1 if (cnt(i, u'Roundup') + cnt(i, u'Round up') + cnt(i, u'8.22')) else 0)
four(u'name_variants', lambda i: [TXT[i].count(u'Privilege Required'), TXT[i].count(u'Privileges Required'),
                                   TXT[i].count(u'Adjacent Network'), TXT[i].count(u'Adjacent')])
F[u'v30_sg'] = F[u'name_variants'][0][0]
F[u'v30_pl'] = F[u'name_variants'][0][1]
F[u'v31_sg'] = F[u'name_variants'][1][0]
F[u'v31_pl'] = F[u'name_variants'][1][1]
F[u'v30_adjnet'] = F[u'name_variants'][0][2]
F[u'v31_adjnet'] = F[u'name_variants'][1][2]

# ---------- 系数: 在含关键词的整行里按 token 位置读 ----------
NUMTOK = re.compile(u'\\d+\\.\\d+|\\d+')
toks = lambda line: NUMTOK.findall(line)


def eqline(i, *needles):
    got = [l for l in LST[i] if all(x in l for x in needles)]
    assert got, (i, needles)
    return got


def ismod(l):
    """这一行说的是环境分(MODIFIED)那一族: 3.0 用 M. 前缀与 ISCModified, 3.1 用 MISS/ModifiedXxx."""
    return (u'MISS' in l) or (u'Modified' in l) or (u'M.' in l)


def coef(i):
    """系数全部取自带该度量的方程行本身: 位置即语义, 一个数都不手填.
    分段不靠标签(3.1 把 'Scope Unchanged' 写在隔壁单元格里), 靠“这行是不是环境分子式”."""
    out = {}
    un = [l for l in eqline(i, u'6.42') if not ismod(l)][0]
    out[u'unch'] = float(toks(un)[0])
    ch = [l for l in eqline(i, u'7.52') if not ismod(l)][0]
    t = toks(ch)
    out[u'c752'], out[u'p029'], out[u'c325'], out[u'p02'] = [float(x) for x in t[:4]]
    mm = re.search(u'0\\.02\\D{1,2}(\\d+)', ch)
    out[u'exp'] = float(mm.group(1))
    out[u'expl'] = float(toks([l for l in eqline(i, u'8.22') if not ismod(l)][0])[0])
    f108 = [l for l in eqline(i, u'1.08') if u'Minimum' in l and u'Exploitability' in l
            and not ismod(l)]
    out[u'f108'] = float(toks(f108[0])[0])
    mv = [l for l in eqline(i, u'6.42') if ismod(l)]
    out[u'munch'] = float(toks(mv[0])[0]) if mv else None
    mc = [l for l in eqline(i, u'7.52') if ismod(l)]
    if mc:
        tm = toks(mc[0])
        out[u'm752'], out[u'mp029'], out[u'm325'] = [float(x) for x in tm[:3]]
        # v3.0 那行是 [..- 0.02]15 共 5 个记号; v3.1 多一个乘子记号 ⇒ 6 个
        out[u'mfactor'] = float(tm[3]) if len(tm) == 6 else 1.0
        out[u'mp02'] = float(tm[4]) if len(tm) == 6 else float(tm[3])
        out[u'mexp'] = float(tm[-1])
        F.setdefault(u'mod_toks', [0, 0])
        F[u'mod_toks'][i] = len(tm)
    cp = [l for l in eqline(i, u'0.915') if u'Minimum' in l]
    out[u'cap'] = float([x for x in toks(cp[0]) if u'.' in x][-1])
    return out


C30, C31 = coef(0), coef(1)
BASEKEYS = [u'unch', u'c752', u'p029', u'c325', u'p02', u'exp', u'expl', u'f108']
ENVKEYS = [u'munch', u'm752', u'mp029', u'm325', u'mp02', u'mfactor', u'mexp', u'cap']
F[u'coef_base_n'] = len(BASEKEYS)
F[u'coef_base_keynames'] = sorted(BASEKEYS)
F[u'coef_env_keys'] = len(ENVKEYS)
F[u'coef_base_n_equal'] = len([k for k in BASEKEYS if abs(C30[k] - C31[k]) < 1e-12])
F[u'coef_env_diff'] = sorted([[k, C30[k], C31[k]] for k in ENVKEYS if abs(C30[k] - C31[k]) > 1e-12])
F[u'coef_env_diff_n'] = len(F[u'coef_env_diff'])
SEQKEYS = sorted(set(BASEKEYS) | set([k for k in ENVKEYS if k in C30 and k in C31]))
F[u'coef_seq_v30'] = [C30[k] for k in SEQKEYS]
F[u'coef_seq_v31'] = [C31[k] for k in SEQKEYS]
F[u'coef_seq_n'] = len(SEQKEYS)
F[u'coef_v30'] = dict((k, C30[k]) for k in SEQKEYS)
F[u'coef_v31'] = dict((k, C31[k]) for k in SEQKEYS)
F[u'exp30'], F[u'exp31'] = int(C30[u'exp']), int(C31[u'exp'])
F[u'mexp30'], F[u'mexp31'] = int(C30[u'mexp']), int(C31[u'mexp'])
F[u'mf30'], F[u'mf31'] = C30[u'mfactor'], C31[u'mfactor']
F[u'cap30'], F[u'cap31'] = C30[u'cap'], C31[u'cap']

# ---------- 权重: <tr> 切块, 组头命中定段, 首字母带例外定缩写 ----------
ABN = {u'not defined': u'X', u'proof of concept': u'P', u'official fix': u'O',
       u'temporary fix': u'T', u'unavailable': u'U', u'unknown': u'U', u'unproven': u'U'}
GROUPS = [(u'attack vector', u'AV'), (u'attack complexity', u'AC'), (u'privilege', u'PR'),
          (u'user interaction', u'UI'), (u'c,i,a impact', u'CIA'),
          (u'confidentiality / integrity', u'CIA'), (u'requirement', u'REQ')]


def ab(v):
    key = v.lower()
    if key in ABN:
        return ABN[key]
    if key == u'adjacent network':
        return u'A'
    return key[:1].upper()


def cells_of(block):
    return [strip(x, br=u'|') for x in re.findall(u'(?is)<t[dh][^>]*>(.*?)</t[dh]>', block)]


def numtables(i):
    out = []
    for ch in re.split(u'(?is)(?=<table)', TXT[i]):
        if not re.match(u'(?is)<table', ch):
            continue
        rows = [cells_of(b) for b in re.split(u'(?is)<tr[^>]*>', ch)[1:] if u'</tr>' in b]
        if any(len(r) == 3 and u'numerical value' in (r[2] or u'').lower() for r in rows):
            out.append(rows)
    return out


def wtab(i):
    out, rows, heads, alt, first_ok, names = {}, 0, 0, 0, 0, []
    for trows in numtables(i):
        cur = None
        for cells in trows:
            if len(cells) != 3:
                continue
            g = cells[0]
            if g:
                names.append(g)
                hit = [a for key, a in GROUPS if key in g.lower()]
                cur = hit[0] if hit else None
                if hit:
                    heads += 1
            if cur is None or not cells[1]:
                continue
            rows += 1
            vs = [x.strip() for x in cells[1].split(u'|') if x.strip()]
            ns = [x.strip() for x in cells[2].split(u'|') if x.strip()]
            if len(vs) != len(ns):
                continue
            for v, n in zip(vs, ns):
                mm = re.match(u'([0-9.]+)(?:.*?\\(\\s*(?:or\\s+)?([0-9.]+)\\s+if)?', n)
                if not mm:
                    continue
                a = float(mm.group(1))
                b2 = float(mm.group(2)) if mm.group(2) else None
                if b2 is not None:
                    alt += 1
                k = ab(v)
                if k == u'N' and v.lower() not in (u'none', u'network'):
                    continue
                if k == v[:1].upper():
                    first_ok += 1
                if cur == u'CIA':
                    for p in (u'C', u'I', u'A'):
                        out[(p, k, u'U')] = a
                        out[(p, k, u'X')] = a
                elif cur == u'REQ':
                    out[(u'REQ', k, u'U')] = a
                else:
                    out[(cur, k, u'U')] = a
                    out[(cur, k, u'X')] = b2 if (cur == u'PR' and b2 is not None) else a
    return out, rows, heads, alt, names, first_ok


W30, R30, H30, A30, NM30, FO30 = wtab(0)
W31, R31, H31, A31, NM31, FO31 = wtab(1)
F[u'w_tab_n'] = [len(numtables(i)) for i in range(4)]


def consol(i):
    """那张“Metric | Metric Value | Numerical Value”总表: 逐行数列数与数值个数."""
    for trows in numtables(i):
        if not trows or len(trows[0]) != 3 or trows[0][0] != u'Metric':
            continue
        body = [c for c in trows[1:] if len(c) == 3]
        lab = [c for c in body if c[0]]
        vc = [len([x for x in c[1].split(u'|') if x.strip()]) for c in body]
        nc = [len([x for x in c[2].split(u'|') if x.strip()]) for c in body]
        return dict(rows=len(trows), val_rows=len(body), metric_rows=len(lab),
                    cont_rows=len(body) - len(lab), vals=sum(vc), nums=sum(nc),
                    maxpack=max(vc) if vc else 0, vc=vc)
    return dict(rows=0, val_rows=0, metric_rows=0, cont_rows=0, vals=0, nums=0, maxpack=0, vc=[])


CS = [consol(i) for i in range(4)]
for _k in (u'rows', u'val_rows', u'metric_rows', u'cont_rows', u'vals', u'nums', u'maxpack'):
    four(u'wt_' + _k, lambda i, _k=_k: CS[i][_k])
F[u'wt_pack_close'] = [CS[i][u'vals'] - CS[i][u'nums'] for i in range(4)]
F[u'wt_row_close'] = [CS[i][u'metric_rows'] + CS[i][u'cont_rows'] - CS[i][u'val_rows'] for i in range(4)]
F[u'wt_pack_seq_v30'] = CS[0][u'vc']
F[u'wt_pack_seq_v31'] = CS[1][u'vc']
F[u'w_groupheads_v30'], F[u'w_groupheads_v31'] = H30, H31
F[u'w_altrows_v30'], F[u'w_altrows_v31'] = A30, A31
F[u'w_triples_v30'], F[u'w_triples_v31'] = len(W30), len(W31)
F[u'w_common'] = len(set(W30) & set(W31))
F[u'w_equal'] = len([k for k in set(W30) & set(W31) if abs(W30[k] - W31[k]) < 1e-12])
F[u'w_unequal_n'] = len([k for k in set(W30) & set(W31) if abs(W30[k] - W31[k]) > 1e-12])
F[u'w_only30_n'] = len(set(W30) - set(W31))
F[u'w_only31_n'] = len(set(W31) - set(W30))
F[u'w_close30'] = len(W30) - F[u'w_common'] - F[u'w_only30_n']
F[u'w_close31'] = len(W31) - F[u'w_common'] - F[u'w_only31_n']
F[u'pr_alt'] = [W30[(u'PR', u'L', u'U')], W30[(u'PR', u'L', u'X')],
                W30[(u'PR', u'H', u'U')], W30[(u'PR', u'H', u'X')]]
F[u'pr_alt31'] = [W31[(u'PR', u'L', u'U')], W31[(u'PR', u'L', u'X')],
                  W31[(u'PR', u'H', u'U')], W31[(u'PR', u'H', u'X')]]
F[u'pr_alt_same'] = len([1 for a, b in zip(F[u'pr_alt'], F[u'pr_alt31']) if abs(a - b) < 1e-12])
F[u'w_firstletter_ok'] = [FO30, FO31]
F[u'w_names_v30'], F[u'w_names_v31'] = len(NM30), len(NM31)

# ---------- 分数实现(三种取整 + 精确小数判据) ----------
def ru_pseudo(x):
    ii = int(round(x * 100000.0))
    return ii / 100000.0 if ii % 10000 == 0 else (ii // 10000 + 1) / 10.0


def ru_guard(x):
    return math.ceil(round(x, 10) * 10.0) / 10.0


def ru_ceil(x):
    return math.ceil(x * 10.0) / 10.0


def parse_vec(s):
    d = {}
    for part in s.split(u'/')[1:]:
        if u':' in part:
            k, v = part.split(u':', 1)
            d[k] = v
    return d


AB2 = {u'N': u'N', u'A': u'A', u'L': u'L', u'P': u'P', u'M': u'M', u'H': u'H', u'R': u'R',
       u'X': u'X', u'U': u'U', u'C': u'C'}


def parts(vstr, W, Cc):
    d = parse_vec(vstr)
    sc = d.get(u'S')
    if sc not in (u'U', u'C'):
        return None
    scope = u'X' if sc == u'C' else u'U'
    def wv(g):
        return W.get((g, AB2.get(d.get(g), d.get(g)), scope if g == u'PR' else u'U'))
    cia = [wv(u'C'), wv(u'I'), wv(u'A')]
    exv = [wv(u'AV'), wv(u'AC'), wv(u'PR'), wv(u'UI')]
    if None in cia or None in exv:
        return None
    return sc, cia, exv, scope


def base_raw(vstr, W, Cc):
    q = parts(vstr, W, Cc)
    if q is None:
        return (u'bad', None)
    sc, cia, exv, _scope = q
    iss, ex, p = 1.0, Cc[u'expl'], 1.0
    for x in cia:
        p *= (1 - x)
    iss = 1 - p
    if sc == u'U':
        imp = Cc[u'unch'] * iss
    else:
        imp = Cc[u'c752'] * (iss - Cc[u'p029']) - Cc[u'c325'] * (iss - Cc[u'p02']) ** Cc[u'exp']
    for x in exv:
        ex *= x
    if imp <= 0:
        return (u'zero', 0.0)
    return (u'ok', imp + ex if sc == u'U' else Cc[u'f108'] * (imp + ex))


def base_score(vstr, W, Cc, ru=ru_pseudo):
    st, raw = base_raw(vstr, W, Cc)
    if st == u'bad':
        return None
    return 0.0 if st == u'zero' else ru(min(raw, 10.0))


def exact_raw(vstr, W, Cc):
    q = parts(vstr, W, Cc)
    if q is None:
        return None
    sc, cia, exv, scope = q
    d = parse_vec(vstr)
    def g(m):
        return Fr(str(W[(m, AB2.get(d[m], d[m]), scope if m == u'PR' else u'U')]))
    iss = 1 - (1 - g(u'C')) * (1 - g(u'I')) * (1 - g(u'A'))
    if sc == u'U':
        imp = Fr(str(Cc[u'unch'])) * iss
    else:
        imp = (Fr(str(Cc[u'c752'])) * (iss - Fr(str(Cc[u'p029'])))
               - Fr(str(Cc[u'c325'])) * (iss - Fr(str(Cc[u'p02']))) ** int(Cc[u'exp']))
    ex = Fr(str(Cc[u'expl'])) * g(u'AV') * g(u'AC') * g(u'PR') * g(u'UI')
    tot = imp + ex if sc == u'U' else Fr(str(Cc[u'f108'])) * (imp + ex)
    return None if imp <= 0 else min(tot, Fr(10))


def ru_exact(t):
    return float(Fr(-((-int(t.numerator * 10)) // int(t.denominator)), 10))


VALS = dict((g, sorted(set([v for (gg, v, _s) in W31 if gg == g]) - set([u'X', u'U'])))
            for g in (u'AV', u'AC', u'PR', u'UI', u'C', u'I', u'A'))
FULL = [u'CVSS:3.1/AV:%s/AC:%s/PR:%s/UI:%s/S:%s/C:%s/I:%s/A:%s' % x
        for x in product(VALS[u'AV'], VALS[u'AC'], VALS[u'PR'], VALS[u'UI'], (u'U', u'C'),
                         VALS[u'C'], VALS[u'I'], VALS[u'A'])]
F[u'full_vectors'] = len(FULL)
F[u'full_grid'] = [len(VALS[u'AV']), len(VALS[u'AC']), len(VALS[u'PR']), len(VALS[u'UI']), 2,
                   len(VALS[u'C']), len(VALS[u'I']), len(VALS[u'A'])]
F[u'full_grid_prod'] = 1
for x in F[u'full_grid']:
    F[u'full_grid_prod'] *= x
RR = [base_raw(v, W31, C31) for v in FULL]
F[u'full_ok'] = len([r for r in RR if r[0] == u'ok'])
F[u'full_zero'] = len([r for r in RR if r[0] == u'zero'])
F[u'full_capped'] = len([r for r in RR if r[0] == u'ok' and r[1] > 10.0])
F[u'full_close'] = F[u'full_ok'] + F[u'full_zero'] - F[u'full_vectors']
F[u'full_eq3031'] = len([v for v in FULL if base_score(v, W30, C30) == base_score(v, W31, C31)])
F[u'full_ne3031'] = len([v for v in FULL if base_score(v, W30, C30) != base_score(v, W31, C31)])
F[u'full_none30'] = len([v for v in FULL if base_score(v, W30, C30) is None])
okv = [v for v, r in zip(FULL, RR) if r[0] == u'ok']
TT = dict((v, exact_raw(v, W31, C31)) for v in okv)
F[u'full_pseudo_eq_exact'] = len([v for v in okv
                                  if abs(ru_exact(TT[v]) - base_score(v, W31, C31)) < 1e-12])
F[u'full_guard_eq_exact'] = len([v for v in okv
                                 if abs(ru_exact(TT[v]) - base_score(v, W31, C31, ru_guard)) < 1e-12])
F[u'full_ceil_eq_exact'] = len([v for v in okv
                                if abs(ru_exact(TT[v]) - base_score(v, W31, C31, ru_ceil)) < 1e-12])
F[u'full_exact_on_tenth'] = len([v for v in okv if (TT[v] * 10).denominator == 1])
F[u'full_raw_on_tenth'] = len([r[1] for r in RR
                               if r[0] == u'ok' and r[1] <= 10.0
                               and min((r[1] * 10.0) % 1.0, 1 - (r[1] * 10.0) % 1.0) < 1e-9])
F[u'full_pseudo_ne_guard'] = len([v for v in okv
                                  if base_score(v, W31, C31) != base_score(v, W31, C31, ru_guard)])
F[u'full_pseudo_ne_ceil'] = len([v for v in okv
                                 if base_score(v, W31, C31) != base_score(v, W31, C31, ru_ceil)])

# ---------- 非单调: 同一维 N<L<H 链, 组合结果先缓存 ----------
CIA, REQ = [u'N', u'L', u'H'], [u'L', u'M', u'H']
CH_ = [(c, i, a, cr, ir, ar) for c in CIA for i in CIA for a in CIA
       for cr in REQ for ir in REQ for ar in REQ]
F[u'mono_combos'] = len(CH_)
F[u'mono_cia'], F[u'mono_req'] = len(CIA) ** 3, len(REQ) ** 3
F[u'mono_grid_close'] = F[u'mono_cia'] * F[u'mono_req'] - F[u'mono_combos']


def mfun(cb, Cc, W):
    miss = min(1.0 - (1 - W[(u'C', cb[0], u'U')] * W[(u'REQ', cb[3], u'U')]) *
               (1 - W[(u'I', cb[1], u'U')] * W[(u'REQ', cb[4], u'U')]) *
               (1 - W[(u'A', cb[2], u'U')] * W[(u'REQ', cb[5], u'U')]), Cc[u'cap'])
    return (Cc[u'm752'] * (miss - Cc[u'mp029'])
            - Cc[u'm325'] * (miss * Cc[u'mfactor'] - Cc[u'mp02']) ** Cc[u'mexp'], miss)


def mono(Cc, W):
    bad, unc, pairs, worst = set(), set(), 0, (0.0, None)
    cache = dict((cb, mfun(cb, Cc, W)) for cb in CH_)
    rank = {u'N': 0, u'L': 1, u'H': 2}
    for cb in CH_:
        for dim in range(3):
            if rank[cb[dim]] == 2:
                continue
            nb = list(cb)
            nb[dim] = CIA[rank[cb[dim]] + 1]
            nb = tuple(nb)
            f0, m0 = cache[cb]
            f1, m1 = cache[nb]
            pairs += 1
            if f1 < f0 - 1e-12:
                bad.add((cb, dim))
                if m0 < Cc[u'cap'] - 1e-12 and m1 < Cc[u'cap'] - 1e-12:
                    unc.add((cb, dim))
                if f0 - f1 > worst[0]:
                    worst = (f0 - f1, (cb, nb))
    return bad, pairs, worst, unc


b30, p30, x30, u30 = mono(C30, W31)
b31, p31, x31, u31 = mono(C31, W31)
F[u'mono_bad_v30formula'], F[u'mono_bad_v31formula'] = len(b30), len(b31)
F[u'mono_pairs'] = p30
F[u'mono_pairs_close'] = p30 - p31
F[u'mono_both'], F[u'mono_only30'], F[u'mono_only31'] = len(b30 & b31), len(b30 - b31), len(b31 - b30)
F[u'mono_close30'] = len(b30) - len(b30 & b31) - len(b30 - b31)
F[u'mono_close31'] = len(b31) - len(b30 & b31) - len(b31 - b30)
F[u'mono_uncapped30'], F[u'mono_uncapped31'] = len(u30), len(u31)
F[u'mono_capped30'], F[u'mono_capped31'] = len(b30) - len(u30), len(b31) - len(u31)
F[u'mono_cap_close30'] = len(b30) - len(u30) - F[u'mono_capped30']
F[u'mono_worst30_amp'], F[u'mono_worst31_amp'] = round(x30[0], 6), round(x31[0], 9)
F[u'mono_worst31_amp_e5'] = round(x31[0] * 1e5, 4)
F[u'mono_worst_v30_ex'] = [round(x30[0], 6), list(x30[1][0]), list(x30[1][1])]
F[u'mono_worst_v31_ex'] = [round(x31[0], 9), list(x31[1][0]), list(x31[1][1])]
F[u'mono_cap'] = [C30[u'cap'], C31[u'cap']]
F[u'mono_req_min'], F[u'mono_req_max'] = W31[(u'REQ', u'L', u'U')], W31[(u'REQ', u'H', u'U')]

# ---------- 算例文档: 分数对、口径与档位 ----------
VEC = re.compile(u'CVSS:[34]\\.\\d(?:/[A-Z]{1,4}:[^/\\s"<>|&]+)+')
four(u'vec_occ', lambda i: len(VEC.findall(BODY[i])))
four(u'vec_distinct', lambda i: len(set(VEC.findall(BODY[i]))))
four(u'vec_occ_31', lambda i: len([x for x in VEC.findall(BODY[i]) if x.startswith(u'CVSS:3.1')]))
four(u'vec_occ_40', lambda i: len([x for x in VEC.findall(BODY[i]) if x.startswith(u'CVSS:4.0')]))
four(u'vec_pr_doublecolon', lambda i: len(re.findall(u'PR::', BODY[i])))

HDR = re.compile(u'^v([34]\\.\\d)(.*)$')
PAIRS, SKIP, TBLCOLS = [], {}, []
NUM = re.compile(u'^([0-9]\\.\\d)')
for ch in re.split(u'(?is)(?=<table)', TXT[3]):
    if not re.match(u'(?is)<table', ch):
        continue
    rows = [cells_of(b) for b in re.split(u'(?is)<tr[^>]*>', ch)[1:] if u'</tr>' in b]
    cols, hdr, hi = {}, None, -1
    for ri, cells in enumerate(rows):
        m = [(ci, HDR.match(c)) for ci, c in enumerate(cells)]
        hit = dict((ci, (mm.group(1), mm.group(2).strip())) for ci, mm in m if mm)
        gv = set([v for (v, _s) in hit.values()])
        if u'3.1' in gv and u'4.0' in gv:
            cols, hdr, hi = hit, cells, ri
            break
    if hdr is None:
        continue
    TBLCOLS.append(len(cols))
    j1 = [ci for ci, (v, _s) in sorted(cols.items()) if v == u'3.1']
    j2 = [ci for ci, (v, _s) in sorted(cols.items()) if v == u'4.0']
    if len(j1) != 1 or len(j2) != 1:
        KEY = u'multi' if (len(j1) > 1 or len(j2) > 1) else u'none'
        SKIP[KEY] = SKIP.get(KEY, 0) + 1
        continue
    k1, k2 = j1[0], j2[0]
    # 向量常印在另一行(分数行与向量行分开), 所以按列收一次: 该列里第一个出现的向量
    vcol = {}
    for ri, cells in enumerate(rows):
        if ri == hi:
            continue
        for ci, c in enumerate(cells):
            if ci in (k1, k2) and ci not in vcol:
                mm = VEC.search(c)
                if mm:
                    vcol[ci] = mm.group(0)
    for ri, cells in enumerate(rows):
        if ri == hi or k1 >= len(cells) or k2 >= len(cells):
            continue
        c1, c2 = cells[k1], cells[k2]
        if not (NUM.match(c1) and NUM.match(c2)):
            continue
        w1 = VEC.search(c1)
        w2 = VEC.search(c2)
        lab = cells[0].strip() if (0 not in cols and cells) else u''
        PAIRS.append({u's31': float(NUM.match(c1).group(1)),
                      u's40': float(NUM.match(c2).group(1)),
                      u'v31': (w1.group(0) if w1 else vcol.get(k1, u'')),
                      u'v40': (w2.group(0) if w2 else vcol.get(k2, u'')),
                      u'k31': cols.get(k1, (u'', u''))[1] or lab,
                      u'k40': cols.get(k2, (u'', u''))[1] or lab,
                      u'fromlab': 1 if (lab and not cols.get(k1, (u'', u''))[1]) else 0,
                      u'samecell': 1 if (w1 or w2) else 0, u'ncol': len(cols)})
F[u'pair_tbl_n_all'] = len(TBLCOLS)
F[u'sp_n'] = len(PAIRS)
F[u'skip_n'] = sum(SKIP.values())
F[u'pair_skip_n'] = len(SKIP)
F[u'pair_k31_blank'] = len([p for p in PAIRS if p[u'k31'] == u''])
F[u'pair_k31_base'] = len([p for p in PAIRS if p[u'k31'] == u'Base'])
F[u'pair_k40_base'] = len([p for p in PAIRS if p[u'k40'] == u'Base'])
F[u'pair_k40_blank'] = len([p for p in PAIRS if p[u'k40'] == u''])
F[u'pair_k40_composite'] = len([p for p in PAIRS if u'+' in p[u'k40']])
F[u'pair_k31blank_k40composite'] = len([p for p in PAIRS if p[u'k31'] == u'' and u'+' in p[u'k40']])
F[u'pair_col_kinds'] = len(set(TBLCOLS))
F[u'pair_col_max'] = max(TBLCOLS) if TBLCOLS else 0
F[u'pair_samecell'] = len([p for p in PAIRS if p[u'samecell']])
F[u'pair_fromlab'] = len([p for p in PAIRS if p[u'fromlab']])
F[u'pair_v31_vec'] = len([p for p in PAIRS if p[u'v31'].startswith(u'CVSS:3.1')])
F[u'pair_v40_vec'] = len([p for p in PAIRS if p[u'v40'].startswith(u'CVSS:4.0')])
F[u'pair_both_vec'] = len([p for p in PAIRS if p[u'v31'] and p[u'v40']])
F[u'pair_k31_other'] = len([p for p in PAIRS if p[u'k31'] not in (u'', u'Base')])
F[u'pair_close'] = F[u'sp_n'] - (F[u'pair_k31_blank'] + F[u'pair_k31_base']
                                 + F[u'pair_k31_other'])
STRICT = [p for p in PAIRS if p[u'k40'] == u'Base' and p[u'k31'] in (u'', u'Base')]
LOOSE = [p for p in PAIRS if p[u'k40'] in (u'', u'Base') and p[u'k31'] in (u'', u'Base')]
F[u'pair_scope_base_strict'] = len(STRICT)
F[u'pair_scope_base_loose'] = len(LOOSE)
F[u'pair_scope_base_gap'] = len(LOOSE) - len(STRICT)
DL = [p[u's40'] - p[u's31'] for p in PAIRS]
DB = [p[u's40'] - p[u's31'] for p in STRICT]
DBL = [p[u's40'] - p[u's31'] for p in LOOSE]
F[u'delta_pos'], F[u'delta_neg'], F[u'delta_zero'] = (len([d for d in DL if d > 1e-9]),
                                                      len([d for d in DL if d < -1e-9]),
                                                      len([d for d in DL if abs(d) <= 1e-9]))
F[u'delta_sum'] = round(sum(DL), 6)
F[u'delta_close'] = F[u'delta_pos'] + F[u'delta_neg'] + F[u'delta_zero'] - F[u'sp_n']
F[u'delta_base_n'], F[u'delta_base_sum'] = len(DB), round(sum(DB), 6)
F[u'delta_base_up'] = len([d for d in DB if d > 1e-9])
F[u'delta_base_down'] = len([d for d in DB if d < -1e-9])
F[u'delta_base_same'] = len([d for d in DB if abs(d) <= 1e-9])
F[u'delta_base_strict_tie'] = (F[u'delta_base_n'] == F[u'pair_scope_base_strict'])
F[u'delta_baseboth_n'], F[u'delta_baseboth_sum'] = len(DBL), round(sum(DBL), 6)
F[u'delta_baseboth_up'] = len([d for d in DBL if d > 1e-9])
F[u'delta_baseboth_down'] = len([d for d in DBL if d < -1e-9])
F[u'delta_baseboth_same'] = len([d for d in DBL if abs(d) <= 1e-9])
F[u'delta_ledger'] = F[u'delta_base_up'] + F[u'delta_base_down'] + F[u'delta_base_same'] \
    - F[u'delta_base_n']
F[u'delta_abs_max'] = max([abs(d) for d in DB]) if DB else 0.0
F[u'delta_abs_max_loose'] = max([abs(d) for d in DBL]) if DBL else 0.0
F[u'delta_mix_gap'] = round(F[u'delta_sum'] - F[u'delta_base_sum'], 6)
F[u'comp_other'] = F[u'sp_n'] - F[u'pair_scope_base_loose']
F[u'comp_other_strict'] = F[u'sp_n'] - F[u'pair_scope_base_strict']

BANDS = [(0.0, 0.0, u'None'), (0.1, 3.9, u'Low'), (4.0, 6.9, u'Medium'),
         (7.0, 8.9, u'High'), (9.0, 10.0, u'Critical')]
VOCAB = (u'None', u'Low', u'Medium', u'High', u'Critical', u'Negligible')


def bandf(x):
    for lo, hi, nm in BANDS:
        if lo <= x <= hi:
            return nm
    return u''


F[u'band_diff'] = len([p for p in PAIRS if bandf(p[u's31']) and bandf(p[u's40'])
                       and bandf(p[u's31']) != bandf(p[u's40'])])
F[u'band_same'] = len([p for p in PAIRS if bandf(p[u's31']) and bandf(p[u's31']) == bandf(p[u's40'])])
F[u'band_unmapped'] = F[u'sp_n'] - F[u'band_diff'] - F[u'band_same']
F[u'band_close'] = F[u'band_diff'] + F[u'band_same'] + F[u'band_unmapped'] - F[u'sp_n']
F[u'band_moves'] = [list(x) for x in sorted(set((bandf(p[u's31']), bandf(p[u's40'])) for p in PAIRS
                              if bandf(p[u's31']) and bandf(p[u's40'])
                              and bandf(p[u's31']) != bandf(p[u's40'])))]
four(u'band_label_lines', lambda i: len([x for x in VOCAB
                                         if x in [l.strip() for l in LST[i]]]))
four(u'band_vocab_inbody', lambda i: sorted(set(x for x in VOCAB if x in BODY[i])))


def bandtab(i):
    """档位表通道: 首格是档位名的行; 次格若是裸数或 a-b / a to b 则记下区间."""
    out, vocab = [], set()
    for row in re.findall(u'(?is)<tr[^>]*>(.*?)</tr>', TXT[i]):
        cs = cells_of(row)
        if not cs or cs[0] not in VOCAB:
            continue
        vocab.add(cs[0])
        m = re.match(u'^\\s*([0-9.]+)(?:\\s*(?:-|to)\\s*([0-9.]+))?\\s*$',
                     cs[1] if len(cs) > 1 else u'')
        if m:
            out.append((cs[0], float(m.group(1)),
                        float(m.group(2)) if m.group(2) else float(m.group(1))))
    return out, sorted(vocab)


BT = [bandtab(i) for i in range(NN4)]
four(u'band_rows', lambda i: len(BT[i][0]))
four(u'band_labels', lambda i: [x[0] for x in BT[i][0]])
four(u'band_bounds', lambda i: [[x[1], x[2]] for x in BT[i][0]])
four(u'band_vocab', lambda i: BT[i][1])
F[u'band_moves_n'] = len(F[u'band_moves'])

# ---------- 复现: 两代公式跑算例印出的 CVSS:3.1 分数 ----------
CAND = [p for p in PAIRS if p[u'v31'].startswith(u'CVSS:3.1') and p[u'k31'] in (u'', u'Base')]
F[u'repro_cand'] = len(CAND)
PRINT = {}
for p in CAND:
    PRINT.setdefault(p[u'v31'], set()).add(p[u's31'])
F[u'repro_vec_distinct'] = len(PRINT)
F[u'repro_repeat'] = F[u'repro_cand'] - F[u'repro_vec_distinct']
res = [(v, base_score(v, W31, C31), base_score(v, W30, C30),
        base_score(v, W31, C31, ru_guard), base_score(v, W31, C31, ru_ceil))
       for v in sorted(PRINT)]
hit = lambda v, g: g is not None and any(abs(g - p) < 1e-9 for p in PRINT[v])
F[u'repro_pts'] = len(res)
F[u'repro_ok'] = len([x for x in res if hit(x[0], x[1])])
F[u'repro_bad'] = len([x for x in res if x[1] is not None and not hit(x[0], x[1])])
F[u'repro_none'] = len([x for x in res if x[1] is None])
F[u'repro_close'] = F[u'repro_ok'] + F[u'repro_bad'] + F[u'repro_none'] - F[u'repro_pts']
F[u'repro_ok30'] = len([x for x in res if hit(x[0], x[2])])
F[u'repro30_eq_31'] = len([x for x in res if x[1] is not None and abs(x[1] - x[2]) < 1e-9])
F[u'repro_guard_eq'] = len([x for x in res if x[1] is not None and abs(x[1] - x[3]) < 1e-9])
F[u'repro_ceil_eq'] = len([x for x in res if x[1] is not None and abs(x[1] - x[4]) < 1e-9])

# ---------- v4.0: 不给算式, 给查表 ----------
four(u'eq_heads', lambda i: len(re.findall(u'EQ(\\d)', BODY[i])))
four(u'eq3_6', lambda i: BODY[i].count(u'EQ3+EQ6') + BODY[i].count(u'EQ3 and EQ6'))
EQR = []
for rows in numtables(2):
    for r in rows[1:]:
        if len(r) >= 2 and (r[0] or u''):
            EQR.append((r[0], r[1] if len(r) > 1 else u''))
for ch in re.split(u'(?is)(?=<table)', TXT[2]):
    if not re.match(u'(?is)<table', ch):
        continue
    rows = [cells_of(b) for b in re.split(u'(?is)<tr[^>]*>', ch)[1:] if u'</tr>' in b]
    if not rows or not rows[0] or not re.match(u'(?i)^levels', rows[0][0] or u''):
        continue
    for r in rows[1:]:
        if len(r) >= 2:
            EQR.append((r[0], r[1] if len(r) > 1 else u''))
F[u'eq_row_n'] = len(EQR)
F[u'eq_level_kinds'] = len(set(x[0] for x in EQR))
F[u'eq_and'] = len([1 for x in EQR if u' and ' in x[1]])
F[u'eq_or'] = len([1 for x in EQR if u' or ' in x[1]])
F[u'eq_not'] = len([1 for x in EQR if u'not ' in x[1]])

# ---------- 跨文书整行共用 ----------
def pnorm(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


FAN = [pnorm(BODY[i]) for i in range(4)]
L2 = [set(pnorm(l) for l in LST[i] if len(l) >= 20 and pnorm(l)) for i in range(4)]
four(u'lines_ge20', lambda i: len(L2[i]))
F[u'share_TO'] = len(L2[0] & L2[1])
F[u'share_TF'] = len(L2[0] & L2[2])
F[u'share_OF'] = len(L2[1] & L2[2])
F[u'share_TN'] = len(L2[0] & L2[3])
F[u'share_ON'] = len(L2[1] & L2[3])
F[u'share_FN'] = len(L2[2] & L2[3])
F[u'share_all4'] = len(L2[0] & L2[1] & L2[2] & L2[3])
F[u'only_T'] = len(L2[0] - L2[1])
F[u'only_O'] = len(L2[1] - L2[0])
F[u'union_TO'] = len(L2[0] | L2[1])
F[u'share_close_TO'] = F[u'share_TO'] + F[u'only_T'] + F[u'only_O'] - F[u'union_TO']

# ---------- 锚池 ----------
SPECIAL = (u'CVSS:3.0/', u'CVSS:3.1/', u'CVSS:4.0/', u'Roundup', u'Round up', u'MacroVector',
           u'6.42', u'7.52', u'1.08', u'0.9731', u'0.30000000000000004', u'0.915',
           u'Negligible', u'Provider Urgency', u'EQ3', u'lookup table', u'interpolation',
           u'Base + Threat', u'Adjacent Network', u'Privilege Required', u'which differs',
           u'ISCBase', u'MISS', u'Exploitability', u'Appendix A', u'pseudocode', u'8.22 x',
           u'0.68 if Scope', u'v4 Score')
POOL = set()
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) >= 20 or any(x in l for x in SPECIAL):
            POOL.add((t, l))
POOL = sorted([(t, x) for (t, x) in POOL if pnorm(x)])
CROSS = dict(((t, x), sum(1 for k in range(4) if pnorm(x) in FAN[k])) for (t, x) in POOL)
POOLC = [(t, CROSS[(t, x)], x) for (t, x) in POOL]
F[u'pool_n'] = len(POOLC)
four(u'pool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
F[u'pool_1'] = len([p for p in POOLC if p[1] == 1])
F[u'pool_2'] = len([p for p in POOLC if p[1] == 2])
F[u'pool_3'] = len([p for p in POOLC if p[1] == 3])
F[u'pool_4'] = len([p for p in POOLC if p[1] == 4])
F[u'pool_tiers'] = [F[u'pool_1'], F[u'pool_2'], F[u'pool_3'], F[u'pool_4']]
F[u'pool_close'] = F[u'pool_1'] + F[u'pool_2'] + F[u'pool_3'] + F[u'pool_4'] - F[u'pool_n']


def ATOMSEL(kind, tag, *needles):
    ok = (lambda n: n == 1) if kind == u'own' else (lambda n: n == int(kind[1:]))
    got = [p for p in POOLC if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
    if not got:
        got = [p for p in POOLC if p[0] == tag and all(x in p[2] for x in needles)]
    assert got, (kind, tag, needles)
    return max(got, key=lambda x: (len(x[2]), x[2]))


USEDATOM = []


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    USEDATOM.append(x[2])
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


CLOSK = sorted([k for k in F if (u'_close' in k or k.endswith(u'_ledger'))
                and isinstance(F[k], (int, float)) and not isinstance(F[k], bool)])
F[u'scalar_clos_n'] = len(CLOSK)
F[u'scalar_clos_sum'] = sum(F[k] for k in CLOSK)
F[u'scalar_clos_list'] = CLOSK
F[u'list_clos_n'] = len([k for k in F if (u'_close' in k or k.endswith(u'_ledger'))
                         and isinstance(F[k], list)])

# --- SCAN END ---

# ---------- DERIV 登记与正文模板 ----------
K, ZERO, COLL, SEENX = {}, [], {}, {}
G, LINES, MISSING = {}, [], []
FN = u'B58V'


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
        if len(exprs) < 2:
            continue
        nums = [eval(e, {u'B58V': BB58}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            # 名单类字面量不能相减: 改判"全等"(集合大小 1) 而不是极差 0
            out[k] = u"%s*(1-(len(set([tuple(y) for y in [%s]]))-1))" % (k, u','.join(exprs))
    return out


def V(name, i=None, note=u''):
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


def CLOS(key, note):
    """闭合账: 打印的数即该键的值(应当为 0), 算式也用同一键, 门槛复算必须得 0."""
    return V(key, None, note)


TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


def JOIN(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LB[t])) for i, t in enumerate(TAGS))


BB58 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B58V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
BARE = re.compile(r'^[0-9+\-*/().,\s]*$')
HELP = re.compile(u"^(V|JOIN|CLOS|TOK|AT)\\(")
_Q = u'"\''


def _split_top(s):
    out, buf, d, q = [], u'', 0, None
    for ch in s:
        if q:
            buf += ch
            if ch == q:
                q = None
            continue
        if ch in _Q:
            q = ch
            buf += ch
            continue
        if ch in u'([{':
            d += 1
        elif ch in u')]})':
            d -= 1
        if ch == u',' and d == 0:
            out.append(buf)
            buf = u''
            continue
        buf += ch
    out.append(buf)
    return [x.strip() for x in out]


def _unlit(x):
    t = x[1:] if x[:1] == u'u' else x
    assert t[0] in _Q and t[-1] == t[0], x
    return t[1:-1]


def _inline(t):
    while True:
        i = t.find(u'{EXPR(')
        if i < 0:
            break
        j = t.index(u'(', i)
        d, k = 0, j
        q = None
        while True:
            c = t[k]
            if q:
                if c == q:
                    q = None
                k += 1
                continue
            if c in _Q:
                q = c
                k += 1
                continue
            if c == u'(':
                d += 1
            elif c == u')':
                d -= 1
                if d == 0:
                    break
            k += 1
        if t[k + 1] != u'}':
            raise AssertionError((u'EXPRSCAN', repr(t[i:k + 4]), repr(t[j + 1:k])))
        args = _split_top(t[j + 1:k])
        assert len(args) == 3, args
        val = eval(args[0], {u'F': F, u'B58V': BB58, u'len': len, u'max': max, u'round': round,
                             u'repr': repr})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]

    def rep(m):
        c = m.group(1).strip()
        if HELP.match(c):
            return eval(c, {u'V': V, u'JOIN': JOIN, u'CLOS': CLOS, u'TOK': TOK, u'AT': AT})
        if u'B58V(' not in c:
            return m.group(0)
        assert BARE.match(BCALL.sub(u'0', c)), c
        val = eval(c, {u'B58V': BB58})
        reg(str(val), c.strip(), c.strip())
        return str(val)
    return re.sub(r'\{([^{}]*)\}', rep, t)


class _Ctx(dict):
    def __missing__(self, k):
        MISSING.append(k)
        return u'§' + k


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + _inline(tmpl)).format_map(_Ctx(dict(G, **kw))))


# ---------- 正文 ----------
LINE(u'🧭', u"四源字节 {JOIN('bytes')}: v3.0 规范 ⇎ v3.1 规范 ⇎ v4.0 规范 ⇎ 算例文档, 后一份是前三份的产物而最大。"
     u"原文件行 {JOIN('lines')} ⇎ 非空行 {JOIN('nonblank')} ⇎ 表 {JOIN('table_tags')} 枚 ⇎ 表行 {JOIN('tr_rows')} 条: "
     u"算例文档一行只印一个分数或向量, 表行数 {EXPR(F['tr_rows'][3] // F['tr_rows'][0], u\"B58V('tr_rows',3)//B58V('tr_rows',0)\", '行数整除商')} 倍于 v3.0 加余 {V('tr_rows_rest')}(商×除数+余数校住 {CLOS('tr_rows_div_close', '行数整除闭合')}, 比 {EXPR(round(1.0*F['tr_rows'][3]/F['tr_rows'][0],2), u\"round(B58V('tr_rows',3)/B58V('tr_rows',0)*100)/100\", '行数比两位')} 倍)。"
     u"最长行 {JOIN('maxlen')}——四份同为 {V('maxlen',0)} 列, 而且逐字节是同一条样板行(共享 {V('maxline_shared')} 枚): 同一份站点的页脚把四页钉成同一种容器。"
     u"平均行长 {JOIN('meanlen')}: 版本越新行越短。去标签正文字符 {JOIN('chars')}。"
     u"制表符 {JOIN('tabs')} ⇎ 非 ASCII {JOIN('nonascii')} ⇎ BOM {JOIN('bom')} ⇎ 尾部换行 {JOIN('final_nl')}: "
     u"四份都不以换行收尾, 于是非空行数比换行数多 {EXPR(F['nonblank'][1]-F['lines'][1], u\"B58V('nonblank',1)-B58V('lines',1)\", 'v3.1 行数差')} 枚(v3.0 那页两者同为 {V('lines',0)}, 因它首行即文档)。"
     u"转码层: <br> {JOIN('br_tags')} 枚 ⇎ <sup> {JOIN('sup_tags')} 枚 ⇎ &lt; 实体 {JOIN('ent_lt')} 枚 ⇎ NBSP {JOIN('nbsp')} 枚 ⇎ 实体总数 {JOIN('ent_all')}; "
     u"<sup> 一剥掉, 指数就并进正文同一行: {AT('own', 'T', u'3.25 x [ISCBase')}, 朴素切法会把 15 读成公式里的第三个数。"
     u"顺序若先解实体再剥标签, 含 &lt; 的那一行会被当成开标签吃掉后半行——本遍与采集遍同用“先剥后解”。"
     u"四份 sha16 是 {V('sha_distinct')} 个不同的串(串只进注, 门槛报种数)。", **{})

LINE(u'📏', u"系数一个都不手填: 全部从含该度量的方程行里按 token 位置读出。基础分那 {V('coef_base_n')} 项两代逐一相等——同 {V('coef_base_n_equal')}／{V('coef_base_n')} 项, 差异 {V('coef_base_n')}-{V('coef_base_n_equal')} 项, 即 "
     u"6.42 ⇎ 7.52 ⇎ 0.029 ⇎ 3.25 ⇎ 0.02 ⇎ 指数 {V('exp30')} ⇎ 8.22 ⇎ 1.08 在 v3.1 里全部原样再现。"
     u"环境分那 {V('coef_env_keys')} 项里 {V('coef_env_diff_n')} 项不同: 指数 {V('mexp30')}→{V('mexp31')}, 乘子 {V('mf30')}→{V('mf31')}。"
     u"v3.1 自己写下: {AT('own', 'O', u'differs from CVSS v3.0')}; 而 '0.9731' 在 v3.0 出现 {V('ar_k9731',0)} 次、在 v3.1 出现 {V('ar_k9731',1)} 次。"
     u"符号名也换过: 'ISCBase' {JOIN('sp_isc')} ⇎ 'ISS' {JOIN('sp_iss')} ⇎ 'MISS' {JOIN('sp_miss')}。"
     u"权重表: 带 'Numerical Value' 表头的总表 {JOIN('w_tab_n')} 张, 表内行 {JOIN('wt_rows')} ⇎ 取值行 {JOIN('wt_val_rows')}(带度量名 {JOIN('wt_metric_rows')} 行 ⇎ 续行 {JOIN('wt_cont_rows')} 行), "
     u"数值 {JOIN('wt_nums')} 个 ⇎ 一格最多并排 {JOIN('wt_maxpack')} 个(v3.0 一格塞四值, v3.1 一格一值而数值一个不少): "
     u"组头 {V('w_groupheads_v30')} ⇎ {V('w_groupheads_v31')} 个, 带“另一档”括注的行 {V('w_altrows_v30')} ⇎ {V('w_altrows_v31')} 行, "
     u"展开成 (度量,取值,口径) 三元组 {V('w_triples_v30')} ⇎ {V('w_triples_v31')}, 共有 {V('w_common')}, 其中数值相等 {V('w_equal')} 条 ⇎ 不等 {V('w_unequal_n')} 条, "
     u"各自独有 {V('w_only30_n')}⇎{V('w_only31_n')}(三档各校住 {CLOS('w_close30', 'v3.0 三元组闭合')} ⇎ {CLOS('w_close31', 'v3.1 三元组闭合')})。"
     u"唯一随口径变动的度量是 PR: Low {V('pr_alt',0)}⇎{V('pr_alt',1)}, High {V('pr_alt',2)}⇎{V('pr_alt',3)}(不变⇎改变), 两代这四个数相同 {V('pr_alt_same')}／4: "
     u"{AT('own', 'T', u'0.68 if Scope')}。"
     u"同一份 v3.0 文档里度量名自己不一致: 单数 {V('v30_sg')} 处 ⇎ 复数 {V('v30_pl')} 处; v3.1 只剩复数 {V('v31_pl')} ⇎ 单数 {V('v31_sg')}; "
     u"取值名 'Adjacent Network' {V('v30_adjnet')} ⇎ {V('v31_adjnet')} 处(数值都是 0.62, 只是不再拖尾)。")

LINE(u'📐', u"取整这一档在三份文书里是三种东西: 'Roundup'(连写) {JOIN('ar_ru')} ⇎ 'Round up'(带空格) {JOIN('ar_ru_up')}——"
     u"v3.0 只用带空格的老写法({V('ar_ru_up',0)} 处) ⇎ v3.1 只用连写的函数名({V('ar_ru',1)} 处) ⇎ v4.0 与算例文档两个写法都 {V('ar_ru',2)} 处。"
     u"定义句 {AT('own', 'O', u'specified to 1 decimal place')}; 反例 {AT('own', 'O', u'0.30000000000000004')}; "
     u"处置 {AT('own', 'O', u'Appendix A - Floating Point Rounding')} 与整数伪码 {AT('own', 'O', u'function Roundup (input)')}; "
     u"'pseudocode' 字样 {JOIN('ar_pseudo')}。"
     u"本库把三种实现各写一遍, 以 Fraction 精确小数为判据: 全部 {V('full_ok')} 条可算向量上伪码 {V('full_pseudo_eq_exact')} 条一致、"
     u"先修 round 再 ceil {V('full_guard_eq_exact')} 条一致、直接 ceil {V('full_ceil_eq_exact')} 条一致(三者都是满分), "
     u"两两分裂 {V('full_pseudo_ne_guard')} ⇎ {V('full_pseudo_ne_ceil')} 条。"
     u"更硬的一条: 浮点 raw 落在 0.1 边界 ±1e-9 内的有 {V('full_raw_on_tenth')} 条, 精确小数恰为 0.1 整倍的只有 {V('full_exact_on_tenth')} 条——就是被 Minimum 折成 10 的那批。"
     u"⇒ 文档自陈的浮点陷阱在“基础分全空间”里不可复现: 它举的那例是 {AT('own', 'O', u'0.1 + 0.2')} 那种加法本身, 而不是这条公式的任何输出; "
     u"“v3.1 为什么要写伪码”由文档自陈支撑, 不由在库分数复现——这一档只进注。", **{})

LINE(u'🪢', u"主轴一: 同一条向量该打几分, 两代算术给出同一个答案, 而且是全空间而非抽样。"
     u"合法基础向量 {V('full_vectors')} 条 = 网格 {V('full_grid',0)}×{V('full_grid',1)}×{V('full_grid',2)}×{V('full_grid',3)}×{V('full_grid',4)}×{V('full_grid',5)}×{V('full_grid',6)}×{V('full_grid',7)} = {V('full_grid_prod')}; "
     u"其中影响子分 ≤0 直接判 0 的 {V('full_zero')} 条, 可算 {V('full_ok')} 条(两档校住 {CLOS('full_close', '可加零=全空间')}), 未封顶前超 10 而被 Minimum 折回的 {V('full_capped')} 条。"
     u"把 v3.0 系数与 v3.1 系数各跑一遍: 同分 {V('full_eq3031')} 条 ⇎ 变分 {V('full_ne3031')} 条 ⇎ 因权重读不出而算不出的 {V('full_none30')} 条——"
     u"两代在每一条合法向量上逐一相等(全空间量词, 不是抽样)。"
     u"抽样侧另有铁证: 算例文档印出向量并去重得 {V('repro_vec_distinct')} 条 CVSS:3.1 向量, 本库用 v3.1 公式复算命中 {V('repro_ok')} 条 ⇎ 不符 {V('repro_bad')} 条 ⇎ 读不出 {V('repro_none')} 条"
     u"(三档校住 {CLOS('repro_close', '复算三档闭合')}); 同一批向量换 v3.0 公式命中 {V('repro_ok30')} 条 ⇎ 与 v3.1 同分 {V('repro30_eq_31')} 条 ⇎ 换朴素取整 {V('repro_guard_eq')}／{V('repro_ceil_eq')} 条仍全中。"
     u"候选 {V('repro_cand')} 处出现 ⇎ 去向量 {V('repro_vec_distinct')} 条, 同一条向量被重复印 {V('repro_repeat')} 次。"
     u"写法也分家: 'Roundup' 字样 {JOIN('ar_ru')} 枚 ⇎ 'Round up' {JOIN('ar_ru_up')} 枚——v3.0 只用后一种(v3.1 只用前一种), 而按去空白去标点的归一口径再比, 同一条式子在这一档落到两版: {AT('m2', 'O', u'Roundup (Minimum')}(v3.0 一侧写作 {AT('own', 'T', u'Round up (Minimum')})。", **{})

LINE(u'🧱', u"主轴二: 两代只在环境分上分家, 而分家的后果是可数的。"
     u"C×I×A 三档 {V('mono_cia')} 种 × CR/IR/AR 三档 {V('mono_req')} 种 = {V('mono_combos')} 个组合(乘积校住 {CLOS('mono_grid_close', '组合数乘积闭合')}), 逐维升一档共 {V('mono_pairs')} 次比较(两式同 {V('mono_pairs_close')} 差)。"
     u"v3.0 式违例 {V('mono_bad_v30formula')} 处 ⇎ v3.1 式违例 {V('mono_bad_v31formula')} 处; 两式同违 {V('mono_both')} ⇎ 只 v3.0 违 {V('mono_only30')} ⇎ 只 v3.1 违 {V('mono_only31')}"
     u"(三档校住 v3.0 的总数 {CLOS('mono_close30', '违例三档闭合')} ⇎ 校住 v3.1 的 {CLOS('mono_close31', '违例对v31闭合')})。"
     u"未封顶处违例 {V('mono_uncapped30')} ⇎ {V('mono_uncapped31')}, 贴帽处 {V('mono_capped30')} ⇎ {V('mono_capped31')}(封顶与否校住 {CLOS('mono_cap_close30', 'v3.0 违例分档闭合')}): "
     u"把指数 15→13 并乘 0.9731, 消掉的正是未封顶那一支的 {V('mono_only30')} 处, 剩下的 {V('mono_bad_v31formula')} 处全部贴在 cap {V('cap30')} 上。"
     u"幅度差着量级: v3.0 最坏一档降 {V('mono_worst30_amp')}, v3.1 最坏一档只降 {V('mono_worst31_amp_e5')}×10^-5——后者已到浮点噪声级。"
     u"REQ 三档权重取自文档: 最低 {V('mono_req_min')} ⇎ 最高 {V('mono_req_max')}。"
     u"所以“v3.1 修了单调性”要按账读: 消 {V('mono_only30')} 处, 余 {V('mono_bad_v31formula')} 处, 新增 {V('mono_only31')} 处。"
     u"v3.0 的式子 {AT('own', 'T', u'Modified Scope Changed')}, v3.1 的式子 {AT('own', 'O', u'MISS x 0.9731')}。", **{})

LINE(u'🗣', u"主轴三: v4.0 把算术整个撤掉。算式迹象(Roundup 或 Round up 或 8.22) {JOIN('arith_any')}——v4.0 一侧为 0; "
     u"8.22 {JOIN('ar_k822')} ⇎ 6.42 {JOIN('ar_k642')} ⇎ 1.08 {JOIN('ar_k108')} ⇎ 0.915 {JOIN('ar_k0915')}: 四个数在 v4.0 与算例文档里都一个不写。"
     u"换成查表: 'MacroVector' {JOIN('bl_mv')} 处 ⇎ 'lookup table' {JOIN('bl_lookup')} 处 ⇎ 'interpolation' {JOIN('bl_interp')} 处 ⇎ 'constraints' {JOIN('bl_cons')} 处; "
     u"约束表行 {V('eq_row_n')} 条, 档位标签 {V('eq_level_kinds')} 种, 布尔连接 and {V('eq_and')} 行 ⇎ or {V('eq_or')} ⇎ not {V('eq_not')}, "
     u"自陈不独立的约束对 {JOIN('eq3_6')} 处: {AT('own', 'F', u'EQ3 and EQ6 are not independent')}; "
     u"表头式 {AT('own', 'F', u'EQ3')}, 机制句 {AT('own', 'F', u'defined by interpolation')}。"
     u"新增两套非数值档: 'Negligible' {JOIN('sp_negligible')} ⇎ 'Provider Urgency' {JOIN('sp_prov_urg')} ⇎ 'Safety' {JOIN('sp_safety')}, "
     u"其中 {AT('J2', 'N', u'Safety is a Supplemental metric')} 把 Safety 定为可选补充度量。"
     u"于是“v4.0 的分数能否在库内复算”没有肯定答案: 库里既无系数也无取整函数, 该文档 {V('vec_occ',3)} 处向量(去重 {V('vec_distinct',3)} 种)只能与它印出的数字对表——这一档写在门槛外。", **{})

LINE(u'🧵', u"主轴四: 算例文档把两代分数并排印出来, 而“并排”不等于“同物”。"
     u"含分数对的表 {V('pair_tbl_n_all')} 张 ⇎ 配成对 {V('sp_n')} 对 ⇎ 跳过 {V('skip_n')} 行(一侧多值或缺值, 类别 {V('pair_skip_n')} 种); "
     u"表式列数 {V('pair_col_kinds')} 种(两列 ⇎ 三列并存), 分数与向量同格 {V('pair_samecell')} 处。"
     u"列头自写口径: v3.1 侧空 {V('pair_k31_blank')} ⇎ 'Base' {V('pair_k31_base')}; v4.0 侧 'Base' {V('pair_k40_base')} ⇎ 空 {V('pair_k40_blank')} ⇎ "
     u"复合口径(含 '+') {V('pair_k40_composite')} 处, 其中 {V('pair_k31blank_k40composite')} 处是“v3.1 侧无口径 ⇎ v4.0 侧是 Base+Threat 那一类”——并排时差值不是同一量之差。"
     u"只取两侧表头都印 'Base' 的 {V('pair_scope_base_strict')} 对(放宽到 v4.0 侧空表头则 {V('pair_scope_base_loose')} 对, 口径宽窄差 {V('pair_scope_base_gap')} 对): 升 {V('delta_base_up')} ⇎ 降 {V('delta_base_down')} ⇎ 平 {V('delta_base_same')}(三档校住 {CLOS('delta_ledger', '升降平三档闭合')}), "
     u"差值和 {V('delta_base_sum')}, 单对最大 {V('delta_abs_max')}; 混入非 Base 的 {V('comp_other_strict')} 对后全 {V('sp_n')} 对的正⇎负⇎零是 {V('delta_pos')}⇎{V('delta_neg')}⇎{V('delta_zero')}(校住 {CLOS('delta_close', '全对三档闭合')}), "
     u"和从 {V('delta_base_sum')} 变到 {V('delta_sum')}——口径混行的影响是 {V('delta_mix_gap')}。"
     u"跨严重度档 {V('band_diff')} 对 ⇎ 同档 {V('band_same')} ⇎ 无档 {V('band_unmapped')}(三档校住 {CLOS('band_close', '跨档三档闭合')}), 迁移方向 {V('band_moves_n')} 种。"
     u"档位数字三份规范完全相同(标签行 {JOIN('band_label_lines')}, 词表 {JOIN('band_vocab')})——变的不是档位, 是档位下面那个数怎么来。", **{})

LINE(u'🧬', u"同一批事实的两种序列化(载体层): 权重表在 v3.0 一格塞四个取值({AT('own', 'T', u'Network | Adjacent')}), "
     u"在 v3.1 一格一取值、续行首格留空——表内行 {V('wt_rows',0)} ⇎ {V('wt_rows',1)}, 数值同为 {V('wt_nums',0)} 个 ⇎ 一格最多 {V('wt_maxpack',0)} 个值, 而展开后的三元组 {V('w_triples_v30')} ⇎ {V('w_triples_v31')} 完全对齐(共有 {V('w_common')} 全等)。"
     u"取值的缩写不能由首字母推: 本遍按首字母判对 {V('w_firstletter_ok',0)} ⇎ {V('w_firstletter_ok',1)} 处, 其余靠全名例外表——'Not Defined' 读成 X, "
     u"'Proof of Concept' 与 'Physical' 抢 P, 'Unproven'／'Unavailable'／'Unknown' 抢 U。"
     u"组头行(带度量的那一格) v3.0 {V('w_names_v30')} ⇎ v3.1 {V('w_names_v31')} 行。"
     u"跨文书整行共用(≥20 字符且归一后非空): v3.0 一侧 {V('lines_ge20',0)} 行 ⇎ v3.1 一侧 {V('lines_ge20',1)} 行, 共用 {V('share_TO')} 行, "
     u"独有 {V('only_T')} ⇎ {V('only_O')}, 三档相加校住并集 {V('union_TO')}(差 {CLOS('share_close_TO', '两版整行并集闭合')}); "
     u"v3.0⇎v4.0 共用 {V('share_TF')} ⇎ v3.1⇎v4.0 共用 {V('share_OF')} ⇎ v3.1⇎算例 {V('share_ON')} ⇎ 四份全在 {V('share_all4')} 行——"
     u"换代保留的是档位表与站点样板, 换掉的是方程本身。")

LINE(u'🧪', u"这条的可核事实分三档。第一档全部由四份在库字节现推({AT('own', 'T', u'Round up (Minimum')} ⇎ {AT('own', 'O', u'function Roundup (input)')} ⇎ "
     u"{AT('own', 'F', u'defined by interpolation')} ⇎ {AT('own', 'N', u'v4 Score')}) ⇒ B58V 可复算: 基础分系数同 {V('coef_base_n_equal')}／{V('coef_base_n')} "
     u"⇎ 环境分异 {V('coef_env_diff_n')}, 权重三元组 {V('w_triples_v30')}⇎{V('w_triples_v31')} 全等 {V('w_equal')}, "
     u"全空间同分 {V('full_eq3031')}／{V('full_vectors')}, 抽样复现 {V('repro_ok')}／{V('repro_vec_distinct')}, "
     u"取整三实现各自对精确小数 {V('full_pseudo_eq_exact')}⇎{V('full_guard_eq_exact')}⇎{V('full_ceil_eq_exact')}, "
     u"违例 {V('mono_bad_v30formula')}⇎{V('mono_bad_v31formula')} 与未封顶 {V('mono_uncapped30')}⇎{V('mono_uncapped31')}, "
     u"分数对 {V('sp_n')} 对里同口径 {V('pair_scope_base_strict')}, 跨档 {V('band_diff')}, v4.0 算式迹象 {V('arith_any',2)}, "
     u"整行共用 {V('share_TO')}, 锚池四档闭合 {CLOS('pool_close', '锚池闭合')}; "
     u"本条登记的标量闭合账 {V('scalar_clos_n')} 处相加 = {EXPR(F['scalar_clos_sum'], u\"B58V('w_close30')+B58V('w_close31')+B58V('full_close')+B58V('repro_close')+B58V('mono_close30')+B58V('mono_close31')+B58V('mono_grid_close')+B58V('mono_pairs_close')+B58V('mono_cap_close30')+B58V('delta_ledger')+B58V('delta_close')+B58V('band_close')+B58V('pair_close')+B58V('tr_rows_div_close')+B58V('share_close_TO')+B58V('pool_close')\", '闭合账逐项相加校 0')}。"
     u"第二档只在本机成立: 四份字节的磁盘 mtime 与抓取时刻、这批 HTML 是否各版本的当前发布——进注不进门槛。"
     u"第三档不可由在库文件判定: v4.0 印出的分数能否由其规范复算(规范只给查表与 EQ 约束, 不给算式), 0.9731 与指数 13 的推导过程"
     u"(v3.1 只声明与 v3.0 不同并指向库里没有的 User Guide: {AT('J2', 'O', u'See the User Guide')}), 以及评估该以哪代作基线的政策选择。"
     u"锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 ◘anchor_total◙ 处／◘anchor_distinct◙ 条去重串, 归属由正文现推, "
     u"每条对四源逐一判成员共 ◘checks◙ 次检查, 归一属一源 ◘anchor_single◙ ⇎ 两或三源 ◘anchor_cross◙ ⇎ 四源 ◘anchor_all4◙, 错配 ◘anchor_err◙ 处。")

LINE(u'∴', u"骨架 ⇒ ① 四源字节 {JOIN('bytes')}, 最长行同为 {V('maxlen',0)} 列且逐字节同一条(共享 {V('maxline_shared')}); "
     u"② 系数: 基础分 {V('coef_base_n_equal')}／{V('coef_base_n')} 项全同, 环境分 {V('coef_env_diff_n')} 项改(指数 {V('mexp30')}→{V('mexp31')}, 乘子 {V('mf30')}→{V('mf31')}, 文档自陈); "
     u"③ 权重: 表内行 {V('wt_rows',0)}⇎{V('wt_rows',1)} 而数值同 {V('wt_nums',0)} 个, 三元组 {V('w_triples_v30')}⇎{V('w_triples_v31')} 全等, PR 双口径 {V('pr_alt',0)}⇎{V('pr_alt',1)} 与 {V('pr_alt',2)}⇎{V('pr_alt',3)}; "
     u"④ 全空间 {V('full_vectors')} 条向量两代同分 {V('full_eq3031')} 条 ⇎ 抽样 {V('repro_ok')}／{V('repro_vec_distinct')} 条命中印出值; "
     u"⑤ 取整三实现与精确小数三方一致, 边界样本 {V('full_raw_on_tenth')} 条 ⇎ 恰为 0.1 整倍 {V('full_exact_on_tenth')} 条; "
     u"⑥ 违例 {V('mono_bad_v30formula')}⇎{V('mono_bad_v31formula')}(消 {V('mono_only30')}, 新增 {V('mono_only31')}, 余 {V('mono_capped31')} 处贴帽), 幅度 {V('mono_worst30_amp')}→{V('mono_worst31_amp_e5')}×10^-5; "
     u"⑦ v4.0 算式迹象 {V('arith_any',2)} 改查表: 约束行 {V('eq_row_n')}, MacroVector {V('bl_mv',2)} 处, 插值 {V('bl_interp',2)} 处; "
     u"⑧ 算例 {V('sp_n')} 对里同口径 {V('pair_scope_base_strict')} 对, 差值和 {V('delta_base_sum')} ⇎ 混口径 {V('delta_sum')}, 跨档 {V('band_diff')} 对, 复合口径 {V('pair_k40_composite')} 对。"
     u"判词: “这条向量几分”在三份规范里没有同一种答法——问 v3.0, 是一条闭式算术加一句 round up; 问 v3.1, 基础分逐字同答(全 {V('full_vectors')} 条), "
     u"环境分换指数并乘 0.9731, 还补一份附录教你躲浮点; 问 v4.0, 它不给算式, 只给 MacroVector 查表与 EQ 约束, 库内连“几分”都无法复算; "
     u"问算例文档, 它给的是两代分数并排 {V('sp_n')} 对, 其中 {V('pair_k40_composite')} 对根本不同口径。")

LINE(u'ℒ', u"方法 ⇒ 遇到“同一问题被多版规范各自改算”的原料, 先问算式能不能在库里跑起来: 本条把两份规范的系数从方程行的 token 位置读出来(拒绝手填), "
     u"把权重表展开成 (度量,取值,口径) 三元组再比集合(共有 {V('w_common')} ⇎ 独有 {V('w_only30_n')}／{V('w_only31_n')}), "
     u"然后把“基础分没动”做成全空间量词——{V('full_vectors')} 条合法向量逐条比, 而不是抽 {V('repro_vec_distinct')} 条样; "
     u"改动则做成反事实账: 只换指数与乘子重算非单调违例({V('mono_bad_v30formula')}→{V('mono_bad_v31formula')}, 未封顶那一支 {V('mono_uncapped30')}→{V('mono_uncapped31')}), "
     u"让“修了什么”落到组合数上而不是形容词上。取整同时实现三种写法并以分数为判据, 得 {V('full_pseudo_eq_exact')}⇎{V('full_guard_eq_exact')}⇎{V('full_ceil_eq_exact')} 三方一致、"
     u"边界样本 {V('full_raw_on_tenth')} 条——这既证伪了我原本要写的“朴素实现会跳档”, 也把文档自陈的浮点陷阱限定回它自己举的那例(0.1+0.2)。"
     u"并排分数一律先读列头口径再相减, 并把同口径 {V('delta_base_sum')} ⇎ 混口径 {V('delta_sum')} 两本账都登记, 差异本身就是结论。")

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 四源各 {JOIN('chars')} 字符, 窗口只能取锚点触到的行; "
     u"而本条的结论几乎全是跨文档与跨算式的量: 全空间 {V('full_vectors')} 条向量两代同分, 违例三档账 {V('mono_both')}+{V('mono_only30')}+{V('mono_only31')}={V('mono_bad_v30formula')}, "
     u"取整三实现与 {V('full_ok')} 条精确小数判据, {V('sp_n')} 对分数里同口径 {V('pair_scope_base_strict')} 对与两本差值账, 整行共用 {V('share_TO')} 行与并集闭合。"
     u"尤其“v4.0 不给算式”这一条, 任何单源窗口都看不见——它要由 v3.1 一侧的 8.22 出现 {V('ar_k822',1)} 次与 v4.0 一侧的 {V('ar_k822',2)} 次同时成立才读得出来。"
     u"读它请按“这个分数是哪代公式、哪一个口径列头、在第几行被印出来”来读, 而不是按“少抄了多少原文”。", **{})

assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
HITC = dict((a, tuple(i for i in range(4) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCH if 1 < len(HITC[a]) < 4]),
       u'all4': len([a for a in ANCH if len(HITC[a]) == 4])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'],
         u'anchor_all4': CLS[u'all4'], u'checks': DIST * 4}
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all4'] == DIST
for n, v in sorted(AMETA.items()):
    reg(str(v), u"%s('%s')" % (FN, n), TOKV.get(n, n))
for n in AMETA:
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
assert u'◘' not in body, u'锚统计量占位符未回填'
for n, v in AMETA.items():
    F[n] = v
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv58.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b58flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms58.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[TOFN]⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == n]))
                       for c, n in ((u'single', 1), (u'two', 2), (u'three', 3), (u'four', 4))),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
      u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': 4, u'flat': F,
      u'closure_keys': [k for k in F if k.endswith(u'close')],
      u'mono_worst_ex': {u'v30': F[u'mono_worst_v30_ex'], u'v31': F[u'mono_worst_v31_ex']}}
json.dump(CH, io.open(u'corpus/_b58checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／原文件行 %d／非空行 %d／表 %d 枚／\'Roundup\' %d 次／\'8.22\' %d 次)' % (
        PATH[i], F[u'bytes'][i], F[u'lines'][i], F[u'nonblank'][i], F[u'table_tags'][i],
        F[u'ar_ru'][i], F[u'ar_k822'][i]) for i in range(4)) +
    u' (四份都是 first.org 的 CVSS 规范页 HTML 序列化; 系数与权重一律从方程行与表内现读, 一个都不手填; '
    u'抓取时刻与磁盘 mtime、这批 HTML 是否各版本当前发布只在本机或站外成立, 不进门槛)\n')
联结 = (u'；联结不是“同一份数据的两种序列化”, 而是同一个漏洞向量在三套评分机制加一份算例集里的四种答法: '
        u"v3.0 与 v3.1 的基础分系数 %d／%d 项逐一相等、权重三元组 %d⇎%d 条全等, 只在环境分把指数 %d 改成 %d 并乘 %s"
        u"(v3.1 自己写明 'differs from CVSS v3.0'); v4.0 一个算式都不给('8.22' %d 次, 'Roundup' %d 次), 换成 MacroVector %d 处与约束表 %d 行; "
        u"算例文档把两代分数并排印 %d 对, 其中 %d 对两列口径不同; 非单调违例 %d⇎%d 处: 改动消掉 %d 处、新增 %d 处\n") % (
    F[u'coef_base_n_equal'], F[u'coef_base_n'], F[u'w_triples_v30'], F[u'w_triples_v31'],
    F[u'mexp30'], F[u'mexp31'], F[u'mf31'], F[u'ar_k822'][2], F[u'ar_ru'][2], F[u'bl_mv'][2],
    F[u'eq_row_n'], F[u'sp_n'], F[u'pair_k40_composite'], F[u'mono_bad_v30formula'],
    F[u'mono_bad_v31formula'], F[u'mono_only30'], F[u'mono_only31'])
title = (u'# B58 同一条向量的四种答法：两代算术在全 %d 条向量上逐条同分 ⇎ 环境分自陈改指数与乘子 ⇎ 新版一个算式都不给 ⇎ 算例并排 %d 对分数（%d 对不同口径）\n' % (
    F[u'full_vectors'], F[u'sp_n'], F[u'pair_k40_composite']))
text = (title + srcline + 联结 +
        u'tags: 全空间量词复算 系数按 token 位置读 权重三元组集合相等 两种表序列化 取整三实现⇎分数判据 '
        u'浮点陷阱不可达 非单调违例三档账 未封顶⇎贴帽 自陈版本差异 复合口径混差 跨档迁移 整行共用⇎并集闭合 '
        u'锚归属由正文现推 闭合账 %d 项\n' % F[u'scalar_clos_n'] +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill58.py 从 corpus/_b58checks.json 与 corpus/_b58meas.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两或三源 %d ⇎ 四源 %d ⇎ 错配 %d ｜ 池内取用 %d／池 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], len(ERR), CH[u'pool_used'], F[u'pool_n']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(F)))
print(u'两代同分 %d／%d ｜ 抽样 %d／%d ｜ 违例 %d⇎%d ｜ 共用行 %d⇎%d⇎%d ｜ 三元组 %d⇎%d' % (
    F[u'full_eq3031'], F[u'full_vectors'], F[u'repro_ok'], F[u'repro_vec_distinct'],
    F[u'mono_bad_v30formula'], F[u'mono_bad_v31formula'], F[u'share_TO'], F[u'share_OF'],
    F[u'share_ON'], F[u'w_triples_v30'], F[u'w_triples_v31']))
BAD = [bk for bk in sorted(F) if bk in M and F[bk] != M[bk]]
for bk in BAD:
    print(u'  与采集侧不符: %s 建条目=%s 采集=%s' % (bk, F[bk], M[bk]))
print(u'对账: 共有键 %d 个, 其中不符 %d 个' % (len([b for b in F if b in M]), len(BAD)))
