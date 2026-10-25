# -*- coding: utf-8 -*-
"""B54 建条目(第二遍现算): 同一批抓取的两份 .html——
T = raw/codata_table.html(自称 Complete Listing, 355 行常数, 0 个 '<')
⇎ E = raw/codata_all.html(名叫 all, 内容是一页“ill-formed request”错误, 155 个 '<')。
锚只按特征子串从 _pick54.py 的候选池取(不手抄原文); 每个数字在这里独立现算并登记成 audit.py 里 B54V 的复算式,
零值折进 '0' 键; 同一套算式采集侧(_pick54)与审计侧(_b54_scan)各再写一遍, 三边不符即证明失败。
本条把“同一个字面数由多条事实写出”做成复合式: 同数的每条算式都要进 DERIV, 不再只留第一条。
不可核的一句话(“哪个 URL 才是这份清单”“错误页由哪次请求造成”)写进判词并给成因;
磁盘 mtime 与那枚时间戳同秒只在本机成立, 进注不进门槛。"""
import io, os, re, sys, json, hashlib, base64, collections, datetime

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = u'corpus'
NL = u'\n'
ENTRY = u'%s/babeltele/B54_complete_listing_and_ill_formed_request.md' % C
J = json.load(io.open(os.path.join(ROOT, C, u'_b54meas.json'), encoding='utf-8'))
MM, POOL = J[u'meas'], J[u'pool']
TAGS, PATH = J[u'tags'], J[u'paths']
LB = dict(zip(TAGS, [u'完整清单', u'错误页外壳']))
RD = lambda p: io.open(os.path.join(ROOT, p), encoding='latin-1').read()
TXT = [RD(p) for p in PATH]
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN --- (corpus/_wire54.py 把这一段机械切进 audit.py::_b54_scan)


def pnorm(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


def nbR(s):
    return [l.rstrip(u'\r') for l in s.split(NL) if l.strip()]


F = {}


def two(name, f):
    F[name] = [f(k) for k in TAGS]


two(u'bytes', lambda k: os.path.getsize(PATH[IDX[k]]))
two(u'chars', lambda k: len(TXT[IDX[k]]))
two(u'lines', lambda k: TXT[IDX[k]].count(NL))
two(u'segments', lambda k: len(TXT[IDX[k]].split(NL)))
two(u'nonblank', lambda k: len(nbR(TXT[IDX[k]])))
two(u'blank', lambda k: F[u'segments'][IDX[k]] - F[u'nonblank'][IDX[k]])
two(u'lt', lambda k: TXT[IDX[k]].count(u'<'))
two(u'gt', lambda k: TXT[IDX[k]].count(u'>'))
two(u'nonascii', lambda k: len([c for c in TXT[IDX[k]] if ord(c) > 127]))
two(u'doctype', lambda k: TXT[IDX[k]].lower().count(u'<!doctype'))
two(u'sha16', lambda k: hashlib.sha256(io.open(PATH[IDX[k]], 'rb').read()).hexdigest()[:16])
F[u'sha_distinct'] = len(set(F[u'sha16']))
F[u'ascii_eq'] = len([i for i in range(2) if F[u'chars'][i] == F[u'bytes'][i]])
F[u'bytes_ratio'] = int(round(100.0 * F[u'bytes'][0] / F[u'bytes'][1]))

X = TXT[0]
ls = X.split(NL)
DASH = [i for i, l in enumerate(ls) if re.match(u'^-{20,}$', l.strip())]
F[u'dash_len'] = len(ls[DASH[0]])
HD = DASH[0] - 1
F[u'hdr_len'] = len(ls[HD])
F[u'hdr_off'] = [ls[HD].index(n) for n in (u'Quantity', u'Value', u'Uncertainty', u'Unit')]
ROWS = [l for l in ls[DASH[0] + 1:] if l.strip()]
F[u'rows'] = len(ROWS)
F[u'row_pairs'] = len(ROWS) - 1
F[u'rowlen_max'] = max(len(l) for l in ROWS)
F[u'rowlen_min'] = min(len(l) for l in ROWS)
F[u'rowlen_gt_hdr'] = len([l for l in ROWS if len(l) > F[u'hdr_len']])
F[u'rowlen_eq_dash'] = len([l for l in ROWS if len(l) == F[u'dash_len']])
F[u'datarow_chars'] = sum(len(l) for l in ROWS)
F[u'datarow_share'] = int(round(100.0 * F[u'datarow_chars'] / F[u'chars'][0]))


def gap4(l):
    f = re.split(u' {2,}', l.strip())
    while len(f) < 4:
        f.append(u'')
    return f[:4]


GAP = [gap4(l) for l in ROWS]
POS = []
for l in ROWS:
    p, out = 0, []
    for x in gap4(l):
        if not x:
            out.append(-1)
            continue
        q = l.find(x, p)
        out.append(q)
        p = q + len(x)
    POS.append(out)
CS = [collections.Counter(q[i] for q in POS).most_common() for i in range(4)]
F[u'col_start'] = [c[0][0] for c in CS]
F[u'col_n'] = [c[0][1] for c in CS]
F[u'col_kinds'] = [len(c) for c in CS]
CQ, CV, CU, CT = F[u'col_start']


def col4(l):
    return [l[CQ:CV].rstrip(), l[CV:CU].rstrip(), l[CU:CT].rstrip(), l[CT:].rstrip()]


COL = [col4(l) for l in ROWS]
F[u'impl_cell'] = F[u'rows'] * 4
F[u'impl_diff'] = sum(1 for i in range(F[u'rows']) for f in range(4) if COL[i][f] != GAP[i][f])
F[u'hdr_vs_col'] = [F[u'hdr_off'][i] - (F[u'col_start'][i] if i < 3 else F[u'col_start'][3]) for i in range(4)]
F[u'hdr_vs_col_all'] = len([d for d in F[u'hdr_vs_col'] if d])
NM, VL, UC, UT = [g[0] for g in GAP], [g[1] for g in GAP], [g[2] for g in GAP], [g[3] for g in GAP]

F[u'name_len_max'] = max(len(n) for n in NM)
F[u'name_len_min'] = min(len(n) for n in NM)
F[u'name_upper'] = len([n for n in NM if n[:1].isupper()])
F[u'name_hyphen'] = len([n for n in NM if u'-' in n])
F[u'name_dot'] = len([n for n in NM if u'.' in n])


def desc(seq, key):
    k = [key(x) for x in seq]
    return len([1 for a, b in zip(k, k[1:]) if a > b]), len([1 for a, b in zip(k, k[1:]) if a == b])


ST4 = [desc(NM, lambda s: s), desc(NM, lambda s: s.lower()), desc(NM, pnorm), desc(ROWS, pnorm)]
F[u'sort_byte'], F[u'sort_fold'], F[u'sort_skel'], F[u'sort_rowskel'] = [x[0] for x in ST4]
F[u'sort_tie_skel'] = ST4[2][1]
F[u'case_cuts'] = F[u'sort_byte'] - F[u'sort_fold']
F[u'punct_cuts'] = F[u'sort_fold'] - F[u'sort_skel']
FI = [i for i in range(1, F[u'rows']) if NM[i] < NM[i - 1]]
F[u'first_inv'] = FI[0] if FI else -1
F[u'inv_pairs'] = len(FI)

F[u'exact_rows'] = len([u for u in UC if u == u'(exact)'])
F[u'meas_rows'] = len([u for u in UC if u and u != u'(exact)'])
F[u'no_unc'] = len([u for u in UC if not u])
F[u'ell_rows'] = len([v for v in VL if u'...' in v])
F[u'ell_dots'] = sum(v.count(u'...') for v in VL)
F[u'ell_in_exact'] = len([i for i in range(F[u'rows']) if u'...' in VL[i] and UC[i] == u'(exact)'])
F[u'ell_out_exact'] = F[u'ell_rows'] - F[u'ell_in_exact']
F[u'exact_no_ell'] = F[u'exact_rows'] - F[u'ell_in_exact']


def dp(s):
    t = re.split(u'[eE]', s.replace(u'...', u''))[0]
    return len(t.split(u'.')[1]) if u'.' in t else 0


AL = [(VL[i], UC[i]) for i in range(F[u'rows']) if UC[i] and UC[i] != u'(exact)']
F[u'align_rows'] = len(AL)
F[u'align_eq'] = len([a for a in AL if dp(a[0]) == dp(a[1])])
F[u'align_ne'] = len([a for a in AL if dp(a[0]) != dp(a[1])])
ALI = [i for i in range(F[u'rows']) if UC[i] and UC[i] != u'(exact)'
       and u'...' not in VL[i] and dp(VL[i]) == dp(UC[i])]
DM = max(ALI, key=lambda i: (dp(VL[i]), NM[i]))
F[u'demo_dec'] = dp(VL[DM])
F[u'demo_name'] = NM[DM]
F[u'demo_rows'] = len(ALI)
EXPAT = re.compile(u'[eE][-+]?[0-9]')
EVI = [i for i in range(F[u'rows']) if EXPAT.search(VL[i]) and EXPAT.search(UC[i])]
FMX = max(EVI, key=lambda i: (len(NM[i]), NM[i]))
F[u'expboth_name'] = NM[FMX]


def grps(s):
    s = re.split(u'[eE]', s.replace(u'...', u''))[0]
    ip, _, fp = s.partition(u'.')
    return ip.split(u' '), (fp.split(u' ') if fp else [])


FR = [g for s in VL + UC if s and s != u'(exact)' for g in grps(s)[1] if g]
F[u'grp_frac_n'] = len(FR)
F[u'grp_frac_3'] = len([g for g in FR if len(g) == 3])
F[u'grp_frac_not3'] = F[u'grp_frac_n'] - F[u'grp_frac_3']
F[u'grp_frac_min'] = min(len(g) for g in FR)
F[u'grp_frac_max'] = max(len(g) for g in FR)
INTP = [g for s in VL + UC if s and s != u'(exact)' for g in grps(s)[0] if g]
F[u'grp_int_n'] = len(INTP)
F[u'grp_int_1'] = len([g for g in INTP if len(g) == 1])
F[u'grp_int_gt1'] = F[u'grp_int_n'] - F[u'grp_int_1']
F[u'grp_sep'] = sum(len(re.findall(u'(?<=\\d) (?=\\d)', s)) for s in VL + UC if s and s != u'(exact)')
RX = re.compile(u'e[-+]?\\d+')
F[u'exp_minus'] = len([v for v in VL if re.search(u'e-\\d', v)])
F[u'exp_plus'] = len([v for v in VL if re.search(u'e\\+\\d', v)])
F[u'exp_unsigned'] = len([v for v in VL if re.search(u'(?<![-+\\w])e\\d', v)])
F[u'exp_any'] = len([v for v in VL if RX.search(v)])
F[u'exp_vu_both'] = len([i for i in range(F[u'rows']) if RX.search(VL[i]) and RX.search(UC[i])])
F[u'exp_vu_same'] = len([i for i in range(F[u'rows']) if RX.search(VL[i]) and RX.search(UC[i])
                         and RX.search(VL[i]).group(0) == RX.search(UC[i]).group(0)])
F[u'exp_vu_diff'] = F[u'exp_vu_both'] - F[u'exp_vu_same']
F[u'exp_v_only'] = len([i for i in range(F[u'rows']) if RX.search(VL[i]) and not RX.search(UC[i])])

C1 = collections.Counter(u for u in UT if u)
C2 = collections.Counter(u for u in [c[3] for c in COL] if u)
F[u'unit_blank'] = len([u for u in UT if not u])
F[u'unit_filled'] = F[u'rows'] - F[u'unit_blank']
F[u'unit_distinct'] = len(C1)
F[u'unit_distinct_col'] = len(C2)
F[u'unit_diff'] = abs(len(C1) - len(C2))
F[u'unit_once'] = len([k for k, n in C1.items() if n == 1])
F[u'unit_hat'] = len([u for u in UT if u'^' in u])
F[u'unit_multi'] = len([u for u in UT if u' ' in u])
F[u'unit_top3'] = [n for _, n in C1.most_common(3)]
F[u'unit_top_sum'] = sum(F[u'unit_top3'])
F[u'unit_blank_exact'] = len([i for i in range(F[u'rows']) if not UT[i] and UC[i] == u'(exact)'])
F[u'unit_top_s'] = u' ⇎ '.join(u'%s(%d)' % (k, n) for k, n in C1.most_common(3))

E = TXT[1]
TE = re.findall(u'<[a-zA-Z][^>]*>', E)
TN = collections.Counter(t[1:].split()[0].split(u'>')[0].lower() for t in TE)
TAGLESS = re.sub(u'<[^>]+>', u' ', E)
NOSC = re.sub(u'<script.*?</script>', u' ', E, flags=re.S | re.I)
NOSC = re.sub(u'<[^>]+>', u' ', NOSC)
COM = re.findall(u'<!--(.*?)-->', E, re.S)
F[u'e_tags'] = len(TE)
F[u'e_close'] = len(re.findall(u'</[a-zA-Z]', E))
F[u'e_tag_kinds'] = len(TN)
F[u'e_tag_top4'] = [n for _, n in TN.most_common(4)]
F[u'e_tag_top4_sum'] = sum(F[u'e_tag_top4'])
F[u'e_tag_top4_s'] = u' ⇎ '.join(u'%s(%d)' % (k, n) for k, n in TN.most_common(4))
F[u'e_comment_n'] = len(COM)
F[u'e_comment_chars'] = sum(len(c) for c in COM)
F[u'e_comment_href'] = len([c for c in COM if u'HREF' in c.upper()])
F[u'e_annotyics'] = E.count(u'Analtyics')
F[u'e_analytics'] = E.count(u'Analytics')
F[u'e_prose'] = len(TAGLESS.strip())
F[u'e_prose_nb'] = len(nbR(TAGLESS))
F[u'e_noscript'] = len(NOSC.strip())
F[u'e_noscript_nb'] = len(nbR(NOSC))
F[u'e_script_lost'] = F[u'e_prose'] - F[u'e_noscript']
F[u'e_script_n'] = len(re.findall(u'(?i)<script[^a-z]', E))
F[u'e_img'] = len(re.findall(u'(?i)<img[^a-z]', E))
F[u'e_hr'] = len(re.findall(u'(?i)<hr[^a-z]', E))
F[u'e_meta'] = len(re.findall(u'(?i)<meta[^a-z]', E))
F[u'e_href_all'] = len(re.findall(u'(?i)href=', E))
F[u'e_amp'] = E.count(u'&amp;')
F[u'e_charset'] = len(re.findall(u'(?i)charset=', E))
F[u't_charset'] = len(re.findall(u'(?i)charset=', X))
F[u'e_gen'] = len(re.findall(u'(?i)name="generator"', E))
LINK = u'/cuu/Constants/index.html'
F[u'e_link_raw'] = E.count(LINK)
F[u'e_link_tagless'] = TAGLESS.count(LINK)
F[u'e_link_comment'] = len([c for c in COM if LINK in c])
F[u'e_cmt_marks'] = F[u'e_comment_href'] + F[u'e_link_comment']
F[u'e_err'] = E.count(u'you have supplied an ill-formed request')
F[u'e_sorry'] = E.count(u'Sorry')
F[u'e_try'] = E.count(u'Try a new search')
F[u'e_newsearch'] = E.count(u'New search')
F[u'e_once_marks'] = F[u'e_err'] + F[u'e_sorry'] + F[u'e_try'] + F[u'e_newsearch'] + F[u'e_annotyics']
F[u'e_gtag_occ'] = len(re.findall(u'G-[A-Z0-9]{6,}', E))
F[u'e_year'] = len(re.findall(u'2022', E))
F[u't_year'] = len(re.findall(u'2022', X))
F[u'e_tag_s'] = u' ⇎ '.join(u'%s %d' % (k, n) for k, n in TN.most_common(4))

TOKSTR = re.findall(u"t:'([A-Za-z0-9=+/]+)'", E)[0]
F[u'tok_str'] = TOKSTR
F[u'tok_len'] = len(TOKSTR)
F[u'tok_epoch'] = int(base64.b64decode(TOKSTR))
F[u'tok_utc'] = datetime.datetime.fromtimestamp(F[u'tok_epoch'], datetime.timezone.utc).strftime(u'%Y-%m-%d %H:%M:%S')
F[u'r_field'] = re.findall(u"r:'([0-9a-f]+)'", E)[0]
F[u'r_hexlen'] = len(F[u'r_field'])
F[u't_urls'] = sorted(set(re.findall(u'https?://\\S+', X)))
F[u'e_urls'] = sorted(set(re.findall(u'https?://[^"\'<> ]+', E)))
F[u'url_shared'] = len(set(F[u't_urls']) & set(F[u'e_urls']))
F[u't_url_n'] = len(F[u't_urls'])
F[u'e_url_n'] = len(F[u'e_urls'])

CROSS = [u'CODATA', u'constants', u'Fundamental Physical Constants', u'uncertainty', u'physics.nist.gov',
         u'googletagmanager', u'iso-8859-1', u'(exact)', u'alpha particle', u'value', u'unit', u'ill-formed']
FAN = [pnorm(TXT[i]) for i in range(2)]
HS = [tuple(i for i in range(2) if pnorm(t) in FAN[i]) for t in CROSS]
F[u'hitkinds'] = len(CROSS)
F[u'hitboth'] = len([h for h in HS if len(h) == 2])
F[u'hitsingle'] = len([h for h in HS if len(h) == 1])
F[u'hitnone'] = len([h for h in HS if not h])
F[u'hitkT'] = len([h for h in HS if h == (0,)])
F[u'hitkE'] = len([h for h in HS if h == (1,)])
assert F[u'hitboth'] + F[u'hitsingle'] + F[u'hitnone'] == F[u'hitkinds']
F[u'both_names'] = u' ／ '.join([t for t, h in zip(CROSS, HS) if len(h) == 2])

POOL2 = [l.strip() for l in ROWS if len(l.strip()) >= 22]
F[u'row_anchor_pool'] = len(POOL2)
F[u'cross_rows'] = len([l for l in POOL2 if pnorm(l) in FAN[1]])

# --- SCAN END ---

TIE = [(u'bytes', u'bytes', None), (u'chars', u'chars', None), (u'lines', u'lines', None),
       (u'segments', u'segments', None), (u'nonblank', u'nonblank', None), (u'blank', u'blank', None),
       (u'lt', u'lt', None), (u'gt', u'gt', None), (u'nonascii', u'nonascii', None),
       (u'doctype', u'doctype', None), (u'rows', u'rows', None), (u'row_pairs', u'row_pairs', None),
       (u'rowlen_max', u'rowlen_max', None), (u'rowlen_min', u'rowlen_min', None),
       (u'rowlen_gt_hdr', u'rowlen_gt_hdr', None), (u'hdr_len', u'hdr_len', None),
       (u'dash_len', u'dash_len', 0), (u'exact_rows', u'exact_rows', None), (u'meas_rows', u'meas_rows', None),
       (u'no_unc', u'no_unc', None), (u'ell_rows', u'ell_rows', None), (u'exact_no_ell', u'exact_no_ell', None),
       (u'align_rows', u'align_rows', None), (u'align_eq', u'align_eq', None), (u'align_ne', u'align_ne', None),
       (u'unit_blank', u'unit_blank', None), (u'unit_distinct', u'unit_distinct', None),
       (u'unit_once', u'unit_once', None), (u'unit_hat', u'unit_hat', None), (u'unit_multi', u'unit_multi', None),
       (u'exp_minus', u'exp_re_minus', None), (u'exp_plus', u'exp_re_plus', None),
       (u'exp_unsigned', u'exp_re_unsigned', None), (u'exp_any', u'exp_re_any', None),
       (u'sort_byte', u'sort_name_byte', 0), (u'sort_fold', u'sort_name_fold', 0),
       (u'sort_skel', u'sort_name_skel', 0), (u'e_tags', u'e_tags', None), (u'e_close', u'e_close', None),
       (u'e_tag_kinds', u'e_tag_names', None), (u'e_comment_n', u'e_comment_n', None),
       (u'e_comment_chars', u'e_comment_chars', None), (u'e_prose', u'e_prose_chars', None),
       (u'e_script_n', u'e_script', None), (u'e_href_all', u'e_href_all', None),
       (u'e_link_raw', u'e_link_raw', None), (u'e_link_tagless', u'e_link_tagless', None),
       (u'tok_epoch', u'tok_epoch', None)]
BADK = [(bk, F[bk], MM[mk] if ix is None else MM[mk][ix]) for bk, mk, ix in TIE
        if F[bk] != (MM[mk] if ix is None else MM[mk][ix])]
assert not BADK, BADK[:6]
assert len(MM[u'url_shared']) == F[u'url_shared'] == len(set(F[u't_urls']) & set(F[u'e_urls']))
assert F[u'impl_diff'] == 0 and F[u'unit_diff'] == 0
assert F[u'exact_rows'] + F[u'meas_rows'] + F[u'no_unc'] == F[u'rows']
assert F[u'exp_minus'] + F[u'exp_unsigned'] + F[u'exp_plus'] == F[u'exp_any']
assert F[u'align_rows'] == F[u'meas_rows'] and F[u'align_eq'] + F[u'align_ne'] == F[u'align_rows']
assert len(set(F[u'sha16'])) == 2

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
    reg(s, u"B54V('%s'%s)" % (name, u'' if i is None else u', %d' % i), note or name)
    return s


def EXPR(s, expr, note):
    reg(s, expr, note)
    return s


def SVAL(name, note=u''):
    """不含数字的字符串值: 原样进正文, 算式登记成对该串本身的复算。"""
    s = F[name]
    reg(s, u"B54V('%s')" % name, note or name)
    return s


TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


def ATOMSEL(kind, tag, *needles):
    ok = (lambda n: n == 1) if kind == u'own' else (lambda n: n == int(kind[1:]))
    got = [p for p in POOL if p[0] == tag and ok(len(p[1])) and all(x in p[2] for x in needles)]
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


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + tmpl).format(**kw))


# ---------- 锚 ----------
G[u'aList'] = AT(u'own', u'T', u'Complete Listing')
G[u'aYear'] = AT(u'own', u'T', u'2022 CODATA adjustment')
G[u'aFrom'] = AT(u'own', u'T', u'physics.nist.gov')
G[u'aHdr'] = AT(u'own', u'T', u'Quantity', u'Uncertainty')
G[u'aFirst'] = AT(u'own', u'T', ROWS[0].strip()[:18])
G[u'aSecond'] = AT(u'own', u'T', ROWS[1].strip()[:14])
G[u'aLast'] = AT(u'own', u'T', ROWS[-1].strip()[:18])
G[u'aKlitz'] = AT(u'own', u'T', u'von Klitzing constant', u'...')
G[u'Avog'] = AT(u'own', u'T', u'Avogadro constant')
G[u'aEv'] = AT(u'own', u'T', u'electron volt')
G[u'aMagmom'] = AT(u'own', u'T', u'triton to proton mag. mom. ratio')
G[u'aWien'] = AT(u'own', u'T', u'Wien frequency displacement law constant')
G[u'aAlphaMass'] = AT(u'own', u'T', u'alpha particle mass energy equivalent')
G[u'aPerm'] = AT(u'own', u'T', u'vacuum mag. permeability')
G[u'aWeak'] = AT(u'own', u'T', u'weak mixing angle')
G[u'aErg'] = AT(u'own', u'E', u'ill-formed request')
G[u'aSorry'] = AT(u'own', u'E', u'Sorry')
G[u'aTry'] = AT(u'own', u'E', u'Try a new search')
G[u'aTitle'] = AT(u'own', u'E', u'CODATA Values of the Fundamental Constants')
G[u'aMeta'] = AT(u'own', u'E', u'charset=')
G[u'aGen'] = AT(u'own', u'E', u'generator')
G[u'aAnaltyics'] = AT(u'own', u'E', u'Analtyics')
G[u'aCf'] = AT(u'own', u'E', u"t:'")
G[u'aNav'] = AT(u'own', u'E', u'BGCOLOR="#C9EDD6"')
G[u'aDap'] = AT(u'own', u'E', u'dap.digitalgov.gov')

# ---------- 数字登记 ----------
G[u'by'] = JOIN(u'bytes', u'字节')
G[u'ch'] = JOIN(u'chars', u'字符')
G[u'ly'] = JOIN(u'lines', u'换行')
G[u'sg'] = JOIN(u'segments', u'段')
G[u'nb'] = JOIN(u'nonblank', u'非空行')
G[u'bk'] = JOIN(u'blank', u'空行')
G[u'ltw'] = JOIN(u'lt', u"'<' 枚")
G[u'gtn'] = JOIN(u'gt', u"'>' 枚")
G[u'na'] = JOIN(u'nonascii', u'非 ASCII 枚')
G[u'dcw'] = JOIN(u'doctype', u'DOCTYPE')
G[u'byT'] = V(u'bytes', IDX[u'T'], u'字节·清单')
G[u'byE'] = V(u'bytes', IDX[u'E'], u'字节·错误页')
G[u'ltE'] = V(u'lt', IDX[u'E'], u"'<' 枚·错误页")
G[u'gtnE'] = V(u'gt', IDX[u'E'], u"'>' 枚·错误页")
G[u'naE'] = V(u'nonascii', IDX[u'E'], u'非 ASCII 枚·错误页')
G[u'eqc'] = V(u'ascii_eq', None, u'字符数=字节数成立的份数')
G[u'br7'] = V(u'bytes_ratio', None, u'字节比(百分数)')
G[u'shaS'] = u'%s ⇎ %s' % (F[u'sha16'][0], F[u'sha16'][1])
G[u'shaK'] = V(u'sha_distinct', None, u'sha16 种数')
G[u'rows'] = V(u'rows')
G[u'pairs'] = V(u'row_pairs')
G[u'rmax'], G[u'rmin'] = V(u'rowlen_max'), V(u'rowlen_min')
G[u'rgh'], G[u'rgd'] = V(u'rowlen_gt_hdr'), V(u'rowlen_eq_dash')
G[u'dash'], G[u'hdrl'] = V(u'dash_len'), V(u'hdr_len')
G[u'dcc'], G[u'dcs'] = V(u'datarow_chars'), V(u'datarow_share')
G[u'c0'] = V(u'col_start', 0, u'名列起点')
G[u'c1'] = V(u'col_start', 1, u'值列起点')
G[u'c2'] = V(u'col_start', 2, u'不确定度列起点')
G[u'c3'] = V(u'col_start', 3, u'单位列起点')
G[u'c1n'] = V(u'col_n', 1, u'值列起点主位置行数')
G[u'c3n'] = V(u'col_n', 3, u'单位列起点主位置行数')
G[u'cell'], G[u'ipd'] = V(u'impl_cell'), V(u'impl_diff')
for i in range(4):
    G[u'hv%d' % i] = V(u'hdr_vs_col', i, u'表头与数据列位差·第%d列' % (i + 1))
G[u'hva'] = V(u'hdr_vs_col_all')
G[u'nmax'], G[u'nmin'] = V(u'name_len_max'), V(u'name_len_min')
G[u'nup'], G[u'nhy'], G[u'ndot'] = V(u'name_upper'), V(u'name_hyphen'), V(u'name_dot')
G[u'sb'] = V(u'sort_byte', None, u'键一·字节')
G[u'sf'] = V(u'sort_fold', None, u'键二·并大小写')
G[u'ss'] = V(u'sort_skel', None, u'键三·只留字母数字')
G[u'sr'] = V(u'sort_rowskel', None, u'键四·整行只留字母数字')
G[u'st'], G[u'cc'], G[u'pc'] = V(u'sort_tie_skel'), V(u'case_cuts'), V(u'punct_cuts')
G[u'fi'], G[u'fip'] = V(u'first_inv'), V(u'inv_pairs')
G[u'ex'], G[u'me'], G[u'nou'] = V(u'exact_rows'), V(u'meas_rows'), V(u'no_unc')
G[u'el'], G[u'eld'] = V(u'ell_rows'), V(u'ell_dots')
G[u'ele'], G[u'elo'], G[u'ene'] = V(u'ell_in_exact'), V(u'ell_out_exact'), V(u'exact_no_ell')
G[u'ar'], G[u'ae'], G[u'an'] = V(u'align_rows'), V(u'align_eq'), V(u'align_ne')
G[u'aDemo'] = AT(u'own', u'T', F[u'demo_name'])
G[u'dgt'] = V(u'demo_dec', None, u'示范行的小数位数')
G[u'adn'] = V(u'demo_rows')
G[u'aMagmom'] = AT(u'own', u'T', F[u'expboth_name'])
G[u'gn'], G[u'g3'], G[u'gnot'] = V(u'grp_frac_n'), V(u'grp_frac_3'), V(u'grp_frac_not3')
G[u'gmin'], G[u'gmax'] = V(u'grp_frac_min'), V(u'grp_frac_max')
G[u'gin'], G[u'gin1'], G[u'ging'] = V(u'grp_int_n'), V(u'grp_int_1'), V(u'grp_int_gt1')
G[u'gsep'] = V(u'grp_sep')
G[u'em'], G[u'ep'], G[u'eu'], G[u'ea'] = V(u'exp_minus'), V(u'exp_plus'), V(u'exp_unsigned'), V(u'exp_any')
G[u'eb'], G[u'ed'], G[u'eo'] = V(u'exp_vu_both'), V(u'exp_vu_diff'), V(u'exp_v_only')
G[u'ub'], G[u'uf'] = V(u'unit_blank'), V(u'unit_filled')
G[u'ud'], G[u'ud2'], G[u'ugd'] = V(u'unit_distinct'), V(u'unit_distinct_col'), V(u'unit_diff')
G[u'u1'], G[u'uh'], G[u'um'] = V(u'unit_once'), V(u'unit_hat'), V(u'unit_multi')
for i in range(3):
    G[u'ut%d' % i] = V(u'unit_top3', i, u'第%d名单位行数' % (i + 1))
G[u'uts'] = V(u'unit_top_sum')
G[u'utopk'] = SVAL(u'unit_top_s', u'最多三种单位')
G[u'ube'] = V(u'unit_blank_exact')
G[u'et'], G[u'ec'] = V(u'e_tags'), V(u'e_close')
G[u'ekt'] = V(u'e_tag_kinds')
for i in range(4):
    G[u'etf%d' % i] = V(u'e_tag_top4', i, u'第%d名标签枚数' % (i + 1))
G[u'etfsum'] = V(u'e_tag_top4_sum')
G[u'etopk'] = SVAL(u'e_tag_s', u'四种标签名与枚数')
G[u'ecn'], G[u'ecc'] = V(u'e_comment_n'), V(u'e_comment_chars')
G[u'ecm'] = V(u'e_cmt_marks')
G[u'eal'], G[u'ean'] = V(u'e_annotyics'), V(u'e_analytics')
G[u'eps'], G[u'epn'] = V(u'e_prose'), V(u'e_prose_nb')
G[u'ens'], G[u'enn'] = V(u'e_noscript'), V(u'e_noscript_nb')
G[u'els'] = V(u'e_script_lost')
G[u'esr'] = V(u'e_script_n')
G[u'eim'], G[u'ehr'], G[u'emt'] = V(u'e_img'), V(u'e_hr'), V(u'e_meta')
G[u'ehf'] = V(u'e_href_all')
G[u'eamp'] = V(u'e_amp')
G[u'ecs'] = V(u'e_charset')
G[u'tcs'] = V(u't_charset')
G[u'ecg'] = V(u'e_gen')
G[u'elr'], G[u'elt'], G[u'elc'] = V(u'e_link_raw'), V(u'e_link_tagless'), V(u'e_link_comment')
G[u'epp'] = V(u'e_once_marks')
G[u'egt'] = V(u'e_gtag_occ')
G[u'ey'], G[u'ty'] = V(u'e_year'), V(u't_year')
G[u'tkl'] = V(u'tok_len')
G[u'te'] = V(u'tok_epoch')
G[u'thms'] = SVAL(u'tok_utc', u'抓取时刻 UTC')
reg(str(F[u'tok_utc'][:4]), u"str(B54V('tok_utc'))[:4]", u'挑战串时刻·年')
G[u'rh'] = V(u'r_hexlen')
G[u'us'], G[u'tun'], G[u'eun'] = V(u'url_shared'), V(u't_url_n'), V(u'e_url_n')
G[u'hk'], G[u'hb'], G[u'hs'], G[u'hn'] = V(u'hitkinds'), V(u'hitboth'), V(u'hitsingle'), V(u'hitnone')
G[u'hT'], G[u'hE'] = V(u'hitkT'), V(u'hitkE')
G[u'pap'] = V(u'row_anchor_pool')
G[u'crx'] = V(u'cross_rows')
G[u'bothw'] = SVAL(u'both_names', u'两源同现关键串')
G[u'nsgl'] = TOK(u'anchor_single', u'单源锚')
G[u'ndist'] = TOK(u'anchor_distinct', u'去重锚串数')
G[u'nat'] = TOK(u'anchor_total', u'正文锚处数')
G[u'ache'] = TOK(u'anchor_both', u'两源同现锚')
G[u'aerr'] = TOK(u'anchor_err', u'错配数')
G[u'checked'] = TOK(u'checks', u'成员检查次数')

TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


G[u'nsgl'] = TOK(u'anchor_single', u'单源锚')
G[u'ndist'] = TOK(u'anchor_distinct', u'去重锚串数')
G[u'nat'] = TOK(u'anchor_total', u'正文锚处数')
G[u'ache'] = TOK(u'anchor_both', u'两源同现锚')
G[u'aerr'] = TOK(u'anchor_err', u'错配数')
G[u'checked'] = TOK(u'checks', u'成员检查次数')

# ---------- 判词 ----------
LINE(u'🧭', u"体例 {aList} ‖ {aYear} ‖ {aErg} ⇒ 在库的是同一秒落盘的两份 .html: 清单那一份 {byT} 字节里 '<' 出现 0 次"
        u"(整份就是一张定宽表, 连 DOCTYPE 都不写), 错误页这一份 {byE} 字节里 '<' {ltE} 枚、DOCTYPE {dcw} 枚、'>' {gtnE} 枚而可读的话只剩一句“请求不合格式”。"
        u"两份都是纯 ASCII({na}), 所以字符数与字节数在 {eqc} 份里各自相等; sha16 各取前 16 位后 {shaK} 种全不同(整串见 ⛓解读注, 它是旁证不是门槛)。"
        u"两源的 URL 交集 {us} 个(清单里 {tun} 个, 错误页里 {eun} 个), 所以“同一批抓取”不是这两份文件的字面关系, 而是从错误页内容里那枚挑战串读出来的, 见 ⏳。", **G)

LINE(u'📏', u"同一批抓取的两份产物在量纲上反号 {ly} 个换行 ⇎ {sg} 段 ⇎ {nb} 非空行 ⇎ {bk} 空行 ⇒ "
        u"清单那份额外有一条 {dash} 字符的分隔线和 {hdrl} 字符的表头行, 数据 {rows} 行、行长只落在 {rmin}～{rmax} 之间: "
        u"比表头还长的有 {rgh} 行, 与分隔线等长的 {rgd} 行; 数据行合计 {dcc} 字符, 占整份文件 {dcs}%。"
        u"错误页去掉标签还剩 {eps} 字符({epn} 行), 其中脚本源码就占 {els} 字符——真正给人读的话只剩 {enn} 行; 反过来清单是它字节的 {br7}%。"
        u"清单那一头行数的两端: 首行 {aFirst}, 末行 {aLast}——相邻行对因此是 {pairs} 双, 下一段拿它做排序检查。", **G)

LINE(u'🔤', u"数字记法在这张表里自有一套写法 {aKlitz} ‖ {aAlphaMass} ‖ {aWien} ‖ {aEv} ⇒ "
        u"数字内部的分隔空格 {gsep} 处; 小数部分的组共 {gn} 组, 三位一组只占 {g3} 组, 其余 {gnot} 组, "
        u"组大小从 {gmin} 位到 {gmax} 位都有——三位是中间组的规矩, 最后一组装可疑位, 2 位与 4 位都合法; 整数部分 {gin} 组里 {gin1} 组只有一位({ging} 组不止)。"
        u"指数写法: 负指数 {em} 行(值列) ⇎ 正而不带符号 {eu} 行(值列) ⇎ 带 '+' 的 {ep} 行(值列)(三者相加校住总数 {ea}); "
        u"值与不确定度同时带指数的 {eb} 行里写法不同者 {ed} 行——同带指数时两边符号一致(例如 {aMagmom}), 只有值带指数的另算 {eo} 行。"
        u"“末组不必三位”与“正指数不写 '+'”这两条在文件里零词面, 只能复算。", **G)

LINE(u'🧱', u"字段边界有两条独立判法: 断列(两个以上空格切开) ⇎ 定宽列(按现数出的列位切) ⇒ "
        u"列位是数出来的: 四列起点依次 {c0} ⇎ {c1} ⇎ {c2} ⇎ {c3}, 其中值列主位置覆盖 {c1n} 行、单位列主位置覆盖 {c3n} 行(单位列的另一种“起点”是那一格根本不存在); "
        u"拿这套列位回头复现断列结果: {cell} 次逐格比对里不一致 {ipd} 处。"
        u"表头四个词的位置与数据列位分别是 {hv0} ⇎ {hv1} ⇎ {hv2} ⇎ {hv3} 的差, 非零者 {hva} 处——表头并不是照着数据列对齐的, 锚 {aHdr} 那一行就是证据。", **G)

LINE(u'🧲', u"“这张表按字母排”有四种判法, 数出四个数 ⇒ 字节键逆序 {sb} 对, 并大小写后 {sf} 对, "
        u"只留字母数字后 {ss} 对(相等 {st} 对), 整行同键 {sr} 对; 逐级降下 {cc} ⇎ {pc} 对。"
        u"字节键下共 {fip} 对逆序(在 {pairs} 对相邻行里), 第一处就在第 {fi} 对: {aFirst} 之后紧跟 {aSecond}——'-' 的码位比空格大, 所以 'particle-el' 排在 'particle m' 之前。"
        u"而表的末行 {aLast} 自己就不守这个序('W to Z' 落在 'Wien…' 之后)。名单里 {nup} 行首字母大写, {nhy} 行带连字符, {ndot} 行带缩写点(名长 {nmin}～{nmax} 字), 而表里没有一处写着它按哪一键排。", **G)

LINE(u'🖼', u"错误页的壳可以拆开数 {aTitle} ‖ {aMeta} ‖ {aGen} ‖ {aAnaltyics} ⇒ 整份 {et} 枚开标签 ⇎ {ec} 枚闭标签 ⇎ {ekt} 种, "
        u"最多的四种是 {etopk}(合计 {etfsum} 枚); 注释 {ecn} 段共 {ecc} 字符, 其中带 HREF 证据的两类各算一次合计 {ecm} 处, "
        u"'Analtyics' 这种拼错只在注释里 {eal} 处而正确的 'Analytics' {ean} 处。"
        u"声明与使用对不上: 声明 charset 有 {ecs} 处而整份 0 枚非 ASCII({naE}), 清单那份连 charset 都不写({tcs} 处)。"
        u"链接活在属性里: /cuu/Constants/index.html 在整份 {elr} 处, 去标签后 {elt} 处, 注释里 {elc} 处——{aTry} 那一行的去处随标签一起被删; "
        u"一次性短语(ill-formed 那句、Sorry、Try a new search、New search、Analtyics)合计 {epp} 处。"
        u"壳里的部件各数一遍: meta {emt} 枚、img {eim} 枚、hr {ehr} 枚、script {esr} 段(noscript 回落文本 {ens} 字符)、href {ehf} 处, "
        u"实体引用只有 {eamp} 枚; 三代分析代码同页——{aGen} 署 GoLive CyberStudio({ecg} 处), gtag 串 {egt} 次, {aDap} 是联邦那一份; "
        u"{aNav} 那一格落在三段注释之外, 而 {aSorry} 之后那一段才是这页给人读的全部内容。", **G)

LINE(u'📐', u"不确定度那一栏把 {rows} 行分三层 {ex} ⇎ {me} ⇎ {nou}(三者相加校住行数) ⇒ "
        u"'(exact)' {ex} 行, 其余 {me} 行给数字不确定度, 该栏空着的 {nou} 行。"
        u"值里带 '...' 的 {el} 行(点号共 {eld} 处)全部落在 '(exact)' 里: 截断者 {ele}, 不在其内者 {elo}; "
        u"于是 '(exact)' 又分两式——被截断的 {ele} 行与给全的 {ene} 行({Avog}、{aEv} 都在给全那一式)。"
        u"这一分档不是排版小事: 它决定小数位对齐那条不变量能核到哪一层, 见 🧵。", **G)

LINE(u'🧵', u"表里没写出来的排版不变量 ⇒ 把值与不确定度各按小数点数位: 可判的 {ar} 行里位位相等 {ae} 行, 不等 {an} 行——"
        u"这条“两边小数位数相同”在文件里零词面, 只能复算(位位可判的 {adn} 行里位数最多的一行是 {aDemo}: 两边各 {dgt} 位小数); 它对 '...' 那 {el} 行根本不适用(值已被截断)。"
        u"单位栏的另两个数: 空 {ub} 行 ⇎ 有值 {uf} 行, 种数 {ud}(断列法与定宽法各数一遍是 {ud} ⇎ {ud2}, 相差 {ugd}), "
        u"只出现一次者 {u1} 种, 带 '^' 幂写法 {uh} 行, 含空格的组合单位 {um} 行; 最多的三种 {utopk} 各占 {ut0} ⇎ {ut1} ⇎ {ut2} 行(三名合计 {uts} 行)。"
        u"空单位与 '(exact)' 的交集 {ube} 行——“无量纲”与“定义值”在这张表里是两件事(锚 {aWeak} 是前者, {aPerm} 是后者)。", **G)

LINE(u'⏳', u"时间只有内容侧那一条能永久复算 {aCf} ⇒ 错误页里那枚挑战串 t:'…' 长 {tkl} 字符, base64 解出整数 {te}, "
        u"换成 UTC 就是 {thms}; 同段的 r:'…' 是 {rh} 位十六进制。"
        u"这份时刻与磁盘 mtime 同秒这件事只在本机成立(拷贝一次文件就失效), 所以它写在注里而不进门槛。"
        u"表自己写的年份是 '2022' {ty} 处({aYear}), 而错误页里 '2022' {ey} 处——两份文件在文字层几乎不重合, 见 🗂。"
        u"出处也只有清单那一头写着: {aFrom} 把来源印成一行, 错误页反过来只把去处指回 /cuu/Constants/index.html({elr} 处)——"
        u"两份文件互不引用, 同一批抓取的关系只留在那枚 base64 串里。", **G)

LINE(u'🗂', u"关键串穿两源 {hk} 枚(归一键: 只留字母数字并小写) ⇒ 两源同现 {hb} 枚 ⇎ 只现一源 {hs} 枚(清单独占 {hT}, 错误页独占 {hE}) ⇎ 一枚不中 {hn} 枚; "
        u"同现的是 {bothw}。"
        u"而整行级的候选池里两源重合 {crx} 条(池中清单行 {pap} 行, 拿错误页全文去配命中 {crx} 行): "
        u"短语级 {hb} 枚与行级 {crx} 条不矛盾——前者问“这几个字母两边都出现过吗”, 后者问“这一整行两边都是它吗”。"
        u"两种口径都写在这里, 不留给读者猜; 本条正文的锚因此全是单源锚(两源同现 {ache} 条)。", **G)

LINE(u'🧪', u"这条的可核事实分三档 {aKlitz} ‖ {aWien} ‖ {aCf} ⇒ 第一档 B54V 可复算: 两源的字节/行/段/空行/'<'/'>'/非 ASCII, "
        u"定宽列位与两法互证({cell} 格 {ipd} 处不一致), 表头与数据列位差 {hva} 处, 排序四键阶梯 {sb}⇎{sf}⇎{ss}⇎{sr}, "
        u"'(exact)' 与 '...' 的分层, 小数位对齐 {ae}⇎{an}, 分组与指数的记数法, 单位列两遍统计(种数差 {ugd}), 错误页的标签/注释/属性计数, 以及那枚 base64 时间戳。"
        u"第二档只在本机成立: 磁盘 mtime 与那枚时间戳同秒——它进注不进门槛, 因为门槛要能在任何一份拷贝上重跑。"
        u"第三档不可核, 由成因决定: 错误页是哪一次请求造成的、'physics.nist.gov/constants' 与 /cuu/ 两个入口谁才是这份清单的正身、"
        u"'2022 CODATA adjustment' 之后官方又改过什么——库里只有这两份字节, 没有请求日志也没有当前线上状态。"
        u"锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 {nat} 处／{ndist} 条去重串, 归属由正文现推, "
        u"每条对两源逐一判成员共 {checked} 次检查, 单源 {nsgl} ⇎ 两源同现 {ache}, 错配 {aerr} 处。", **G)

LINE(u'∴', u"骨架 ⇒ ① 同批两份 .html 字节 {by}, 换行 {ly}, 非空行 {nb}, '<' {ltw}, 非 ASCII {na}(纯 ASCII 故字符=字节 {eqc} 份); "
           u"② 清单是定宽表: 数据 {rows} 行占字符 {dcs}%, 列位 {c0}⇎{c1}⇎{c2}⇎{c3}, 两法 {cell} 格比对不一致 {ipd} 处, 表头与列位非零差 {hva} 处; "
           u"③ 排序四键逆序 {sb}⇎{sf}⇎{ss}⇎{sr}, 大小写切掉 {cc} 对, 标点再切掉 {pc} 对, 第一处在第 {fi} 对; "
           u"④ 不确定度分三层 {ex}⇎{me}⇎{nou}, '...' 的 {el} 行全在 '(exact)' 内, 故 '(exact)' 又分截断 {ele} ⇎ 给全 {ene}; "
           u"⑤ 隐不变量: 值与不确定度小数位相等 {ae} 行 ⇎ 不等 {an} 行(适用面 {ar} 行); "
           u"⑥ 记法: 小数末组非三位 {gnot} 组(最大 {gmax} 位), 指数负 {em} ⇎ 正而不写 '+' {eu} ⇎ 写 '+' {ep}; "
           u"⑦ 错误页: 开标签 {et}／闭 {ec}／种 {ekt}, 注释 {ecn} 段 {ecc} 字符, 链接 {elr} 处 → 去标签 {elt} 处, 去标签后 {eps} 字符里脚本 {els} 字符; "
           u"⑧ 穿两源 {hk} 枚关键串同现 {hb} 枚, 整行锚池重合 {crx} 条, 内容侧时间戳 {te}。"
           u"判词: 一个文件是什么由它的字节自己说——同后缀的两份, 字节 {by}, 一份 0 枚 '<' 一份 {ltE} 枚; "
           u"命名相反(table 才是数据, all 是一页错误); 而两边几乎不相交({us} 个共同 URL、整行重合 {crx} 条)却是同一秒抓下的。", **G)

LINE(u'ℒ', u"方法 ⇒ 遇到“同名的两份文件”先别问哪份对, 先各自建口径再问重合: "
        u"本条把字段边界写成两条独立判法(断列 ⇎ 定宽列), {cell} 格 {ipd} 处不一致才算坐实定宽; "
        u"把“按字母排”写成四键阶梯并逐级报降幅({cc} ⇎ {pc}), 因为只报“排没排”会把连字符与大小写两种成因糊成一谈; "
        u"把隐不变量单独立一栏(小数位对齐 {ae}⇎{an})并写明它的适用面 {ar} 行——不适用的一档正好是全部 '(exact)' 行, 其中截断式 {el} 行; "
        u"把重合写成两级(短语 {hb} 枚 ⇎ 整行 {crx} 条), 免得一个 0 看上去推翻另一个数; "
        u"最后把时间分两档: base64 解出的 {te} 住在字节里, 永久可复算, 磁盘 mtime 与它同秒只在本机成立, 所以只进注。"
        u"错误页也不当垃圾: 标签 {et}／{ec}／{ekt}、注释里拼错 {eal} 处、链接 {elr}⇎{elt} 的落差都是可数的事实。", **G)

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 两源各 {ch} 字符, 窗口只能取锚点触到的行; "
        u"而本条的结论全是跨行量: {rows} 行的四键排序阶梯、{cell} 格的两法互证、{ar} 行的小数位对齐、{ud} 种单位的两遍计数。"
        u"尤其带 '...' 的 {el} 行与给全的 {ene} 行 '(exact)' 分档, 任何单窗口都装不下这张表的层级。"
        u"读它请按“这个数是对哪一列、用哪种边界口径数出来的”来读, 而不是按“少抄了多少原文”。", **G)

body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([TE])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
HITC = dict((a, tuple(i for i in range(2) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]), u'both': len([a for a in ANCH if len(HITC[a]) == 2])}
AMETA = {u'anchor_total': len(CITES), u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_both': CLS[u'both'], u'checks': DIST * 2}
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'both'] == DIST
for k, v in sorted(AMETA.items()):
    reg(str(v), u"B54V('%s')" % k, TOKV.get(k, k))
for n in (u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single', u'anchor_both', u'checks'):
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
assert u'◘' not in body, u'锚统计量占位符未回填'
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(os.path.join(ROOT, C, u'_deriv54.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(os.path.join(ROOT, C, u'_b54flat.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(os.path.join(ROOT, C, u'_atoms54.txt'), 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[TE]⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == (1 if c == u'single' else 2)]))
                       for c in (u'single', u'both')),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV), u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': 2, u'flat': F,
      u'meas_tie_keys': [b for b, _, _ in TIE]}
json.dump(CH, io.open(os.path.join(ROOT, C, u'_b54checks.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

srcline = (u'src: ' + u' ⇎ '.join(u'%s (%d 字节／非空行 %d／\'<\' %d 枚)' % (PATH[i], F[u'bytes'][i], F[u'nonblank'][i], F[u'lt'][i])
                                 for i in range(2)) +
           u' (两份由同一秒的抓取落盘; 内容侧的抓取时刻住在错误页那枚挑战串里, 可永久复算; 磁盘 mtime 与它同秒只在本机成立, 不进门槛)\n')
联结 = (u'；联结不是“同一份数据的两种序列化”, 而是同一秒抓下的两份 .html: 清单那份 %d 字节里 \'<\' %d 枚(整份是一张定宽表), '
        u'错误页那份 %d 字节里 \'<\' %d 枚而可读正文只剩一句“请求不合格式”; 两源共同 URL %d 个, 整行级候选池重合 %d 条, '
        u'而短语级关键串 %d 枚里两源同现 %d 枚; 清单自己有三层可数的事: 排序四键逆序 %d⇎%d⇎%d, (exact) %d 行 ⇎ 带截断点 %d 行 ⇎ 小数位相等 %d 行\n') % (
    F[u'bytes'][0], F[u'lt'][0], F[u'bytes'][1], F[u'lt'][1], F[u'url_shared'], F[u'cross_rows'],
    F[u'hitkinds'], F[u'hitboth'], F[u'sort_byte'], F[u'sort_fold'], F[u'sort_skel'],
    F[u'exact_rows'], F[u'ell_rows'], F[u'align_eq'])
text = (u'# B54 两份 .html 形状相反：一份是 %d 行常数的定宽表，一份的可读正文只剩错误页那句抱怨\n' % F[u'rows'])
text += (srcline + 联结 +
         u'tags: 定宽列两法互证 表头与数据错位 排序四键阶梯 (exact)与截断分档 小数位对齐隐不变量 三位分组末组例外 '
         u'正指数不写加号 标签与注释计数 链接只活在属性里 声明字符集而未用 base64 抓取时刻 整行池零重合须分口径 锚归属由正文现推\n' +
         u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
         u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
         u'## ⛓解读注\n\n（此段由 corpus/_fill54.py 从 corpus/_b54checks.json 与 corpus/_b54meas.json 现算写入）\n')
io.open(os.path.join(ROOT, ENTRY), 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d 串 ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'DERIV %d 键 ⇎ 复算点 %d ｜ 同数共键 %d 组(复合式) ｜ 0 键折 %d 项' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO)))
for k, v in sorted(COLL.items(), key=lambda x: -len(x[1]))[:10]:
    print(u'  同数 %s ← %s' % (k, v))
print(u'残留未替换占位符 %d' % len(re.findall(u'\\{[a-zA-Z_0-9]+\\}', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))))
print(u'锚内拉丁 %d ｜ 锚外拉丁 %d ｜ 标签 %d 枚 ｜ 池内取用 %d ｜ 扁平键 %d 个' % (
    CH[u'letters_in'], CH[u'letters_out'], CH[u'tagn'], CH[u'pool_used'], len(F)))
