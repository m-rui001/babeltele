# -*- coding: utf-8 -*-
"""B54 采集(第一遍现算): 同一批抓取的两份 .html——
T = raw/codata_table.html(40 801 B, 自称 Complete Listing, 0 个 '<')
E = raw/codata_all.html(5 371 B, 名叫 all 实为“ill-formed request”错误页, 155 个 '<')
本脚本独立实现两套字段抽取(两空格以上断列 → 反推列位 → 定宽列), 四种排序键, 两遍单位统计; 两边不符即证明失败。
建条目侧 corpus/_mkB54.py 与审计侧 audit.py::_b54_scan() 各再写一遍同一套算法。
可判性分档: “哪个 URL 才是这份清单”“错误页由哪次请求造成”由本库文件判不出来, 只进解读注;
本机可复核但不进门槛的那一档: 磁盘 mtime 与内容里 base64 时间戳同秒(拷贝文件即失效)。
落 corpus/_b54meas.json / _b54meas.txt。"""
import io, os, re, sys, json, hashlib, base64, collections, datetime

sys.stdout.reconfigure(encoding='utf-8')
ROOT = u'corpus/raw'
NL = u'\n'
PATH = {u'T': os.path.join(ROOT, u'codata_table.html'),
        u'E': os.path.join(ROOT, u'codata_all.html')}
ORDER = [u'T', u'E']


def rd(p):
    return io.open(p, encoding='latin-1').read()


X = dict((k, rd(PATH[k])) for k in ORDER)
BYTES = dict((k, os.path.getsize(PATH[k])) for k in ORDER)
SHA = dict((k, hashlib.sha256(open(PATH[k], 'rb').read()).hexdigest()) for k in ORDER)
M = {}


def pn(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


def nonblank(s):
    return [l.rstrip(u'\r') for l in s.split(NL) if l.strip()]


# ---------- 1. 量纲 ----------
NB = dict((k, nonblank(X[k])) for k in ORDER)
M[u'bytes'] = [BYTES[k] for k in ORDER]
M[u'chars'] = [len(X[k]) for k in ORDER]
M[u'lines'] = [X[k].count(NL) for k in ORDER]
M[u'segments'] = [len(X[k].split(NL)) for k in ORDER]
M[u'nonblank'] = [len(NB[k]) for k in ORDER]
M[u'blank'] = [M[u'segments'][i] - M[u'nonblank'][i] for i in range(2)]
M[u'lt'] = [X[k].count(u'<') for k in ORDER]
M[u'gt'] = [X[k].count(u'>') for k in ORDER]
M[u'nonascii'] = [len([c for c in X[k] if ord(c) > 127]) for k in ORDER]
M[u'sha16'] = [SHA[k][:16] for k in ORDER]
M[u'sha_diff'] = len(set(SHA.values())) == 2
M[u'bytes_ratio'] = round(M[u'bytes'][0] / float(M[u'bytes'][1]), 2)
M[u'ext_html'] = [os.path.basename(PATH[k]).endswith(u'.html') for k in ORDER]
M[u'head15'] = [X[k].lstrip()[:15].lower() for k in ORDER]
M[u'doctype'] = [X[k].lower().count(u'<!doctype') for k in ORDER]
assert sum(M[u'nonascii']) == 0, M[u'nonascii']

# ---------- 2. 声明与使用 ----------
M[u'e_charset_decl'] = len(re.findall(u'(?i)charset=', X[u'E']))
M[u'e_declared'] = re.findall(u'(?i)charset=([A-Za-z0-9_-]+)', X[u'E'])
M[u'e_meta'] = len(re.findall(u'(?i)<meta[^a-z]', X[u'E']))
M[u'e_gen'] = re.findall(u'(?i)name="generator" content="([^"]+)"', X[u'E'])
M[u't_decl'] = len(re.findall(u'(?i)charset=', X[u'T']))
M[u't_titleish'] = [X[u'T'].split(NL)[1].strip(), X[u'T'].split(NL)[2].strip()]

# ---------- 3. 定宽表结构: 先断列, 再反推列位, 两法对照 ----------
ls = X[u'T'].split(NL)
DASH = [i for i, l in enumerate(ls) if re.match(u'^-{20,}$', l.strip())]
M[u'dash_lines'] = len(DASH)
M[u'dash_len'] = [len(ls[i]) for i in DASH]
hd = DASH[0] - 1
M[u'hdr_len'] = len(ls[hd])
HDR = [ls[hd].index(n) for n in (u'Quantity', u'Value', u'Uncertainty', u'Unit')]
M[u'hdr_off'] = HDR
M[u'hdr_words'] = re.findall(u'[A-Za-z]+', ls[hd])


def by_gap(l):
    f = re.split(u' {2,}', l.strip())
    while len(f) < 4:
        f.append(u'')
    return f[:4]


def starts(l):
    pos, out = 0, []
    for x in by_gap(l):
        if not x:
            out.append(-1)
            continue
        p = l.find(x, pos)
        out.append(p)
        pos = p + len(x)
    return out


ROWS = [l for l in ls[DASH[0] + 1:] if l.strip()]
GAP = [by_gap(l) for l in ROWS]
ST = [starts(l) for l in ROWS]
M[u'rows'] = len(ROWS)
M[u'row_pairs'] = M[u'rows'] - 1
M[u'rowlen_max'] = max(len(l) for l in ROWS)
M[u'rowlen_min'] = min(len(l) for l in ROWS)
M[u'rowlen_gt_hdr'] = len([l for l in ROWS if len(l) > M[u'hdr_len']])
M[u'rowlen_eq_dash'] = len([l for l in ROWS if len(l) == M[u'dash_len'][0]])
COLSTART = [collections.Counter(s[i] for s in ST).most_common() for i in range(4)]
M[u'col_start_mode'] = [c[0][0] for c in COLSTART]
M[u'col_start_kinds'] = [len(c) for c in COLSTART]
M[u'col_start_top'] = [[list(x) for x in c[:3]] for c in COLSTART]
CQ, CV, CU, CT = M[u'col_start_mode']


def by_col(l):
    return [l[CQ:CV].rstrip(), l[CV:CU].rstrip(), l[CU:CT].rstrip(), l[CT:].rstrip()]


COL = [by_col(l) for l in ROWS]
M[u'impl_name_diff'] = len([i for i in range(M[u'rows']) if COL[i][0] != GAP[i][0]])
M[u'impl_val_diff'] = len([i for i in range(M[u'rows']) if COL[i][1] != GAP[i][1]])
M[u'impl_unc_diff'] = len([i for i in range(M[u'rows']) if COL[i][2] != GAP[i][2]])
M[u'impl_unit_diff'] = len([i for i in range(M[u'rows']) if COL[i][3] != GAP[i][3]])
M[u'impl_diff_rows'] = [GAP[i][0] for i in range(M[u'rows'])
                        if COL[i] != GAP[i]][:4]
NAMES, V, U, UN = [g[0] for g in GAP], [g[1] for g in GAP], [g[2] for g in GAP], [g[3] for g in GAP]
assert all(g[0] and g[1] for g in GAP) and len(COL) == len(GAP) == M[u'rows']

# ---------- 4. 排序口径阶梯(四种键, 逐级测) ----------
M[u'name_len_max'] = max(len(n) for n in NAMES)
M[u'name_len_min'] = min(len(n) for n in NAMES)
M[u'name_len_ge61'] = len([n for n in NAMES if len(n) >= CV])
M[u'name_upper'] = len([n for n in NAMES if n[:1].isupper()])
M[u'name_hyphen'] = len([n for n in NAMES if u'-' in n])
M[u'name_dot'] = len([n for n in NAMES if u'.' in n])


def desc(seq, key):
    k = [key(x) for x in seq]
    return [len([1 for a, b in zip(k, k[1:]) if a > b]),
            len([1 for a, b in zip(k, k[1:]) if a == b])]


M[u'sort_calibers'] = 4
M[u'sort_name_byte'] = desc(NAMES, lambda s: s)
M[u'sort_name_fold'] = desc(NAMES, lambda s: s.lower())
M[u'sort_name_skel'] = desc(NAMES, pn)
M[u'sort_row_skel'] = desc(ROWS, pn)
M[u'sort_head'] = [NAMES[0], NAMES[-1]]
FI = [i for i in range(1, M[u'rows']) if NAMES[i] < NAMES[i - 1]]
M[u'sort_first_inversion'] = FI[0] if FI else -1
M[u'sort_inversion_pairs_byte'] = len(FI)
M[u'sort_inversion_causes'] = sorted(collections.Counter(
    (NAMES[i - 1][:17], NAMES[i][:17]) for i in FI).keys())[:4]
M[u'sort_name_byte_and_fold_gap'] = M[u'sort_name_byte'][0] - M[u'sort_name_fold'][0]
M[u'sort_name_fold_and_skel_gap'] = M[u'sort_name_fold'][0] - M[u'sort_name_skel'][0]

# ---------- 5. (exact) 与 '...' 的分层 ----------
M[u'exact_rows'] = len([u for u in U if u == u'(exact)'])
M[u'meas_rows'] = len([u for u in U if u and u != u'(exact)'])
M[u'no_unc'] = len([u for u in U if not u])
M[u'ell_rows'] = len([v for v in V if u'...' in v])
M[u'ell_dots'] = sum(v.count(u'...') for v in V)
M[u'ell_in_exact'] = len([i for i in range(M[u'rows']) if u'...' in V[i] and U[i] == u'(exact)'])
M[u'ell_not_exact'] = len([i for i in range(M[u'rows']) if u'...' in V[i] and U[i] != u'(exact)'])
M[u'exact_no_ell'] = len([i for i in range(M[u'rows']) if U[i] == u'(exact)' and u'...' not in V[i]])
M[u'exact_no_ell_names'] = [NAMES[i] for i in range(M[u'rows'])
                            if U[i] == u'(exact)' and u'...' not in V[i]][:6]
assert M[u'exact_rows'] + M[u'meas_rows'] + M[u'no_unc'] == M[u'rows'], (M[u'exact_rows'], M[u'meas_rows'], M[u'no_unc'])
assert M[u'ell_in_exact'] + M[u'ell_not_exact'] == M[u'ell_rows']
assert M[u'exact_rows'] == M[u'ell_in_exact'] + M[u'exact_no_ell']

# ---------- 6. 小数位对齐不变量(词面零提及, 只能复算) ----------
def dec_places(s):
    t = re.split(u'[eE]', s.replace(u'...', u''))[0]
    return len(t.split(u'.')[1]) if u'.' in t else 0


ALIGN = [(NAMES[i], dec_places(V[i]), dec_places(U[i]))
         for i in range(M[u'rows']) if U[i] and U[i] != u'(exact)']
M[u'align_rows'] = len(ALIGN)
M[u'align_eq'] = len([a for a in ALIGN if a[1] == a[2]])
M[u'align_ne'] = len([a for a in ALIGN if a[1] != a[2]])
M[u'align_ne_names'] = [a[0] for a in ALIGN if a[1] != a[2]][:8]
M[u'align_ne_diff'] = sorted(set(a[1] - a[2] for a in ALIGN if a[1] != a[2]))
M[u'align_exact_rows'] = len([i for i in range(M[u'rows']) if U[i] == u'(exact)'])
assert M[u'align_rows'] == M[u'meas_rows'], (M[u'align_rows'], M[u'meas_rows'])

# ---------- 7. 数字分组与指数记法 ----------
def groups(s):
    s = s.replace(u'...', u'')
    s = re.split(u'[eE]', s)[0]
    ip, _, fp = s.partition(u'.')
    return ip.split(u' '), (fp.split(u' ') if fp else [])


ALLG = []
for s in V + U:
    if not s or s == u'(exact)':
        continue
    gi, gf = groups(s)
    ALLG.append((len(gi), len(gf)))
M[u'grp_int_kinds'] = sorted(collections.Counter(x[0] for x in ALLG).items())
M[u'grp_frac_kinds'] = sorted(collections.Counter(x[1] for x in ALLG).items())
FR = [g for s in V + U if s and s != u'(exact)' for g in groups(s)[1]]
M[u'grp_frac_sizes'] = sorted(collections.Counter(len(x) for x in FR if x).items())
M[u'grp_frac_last3'] = len([x for x in FR if len(x) == 3])
M[u'grp_frac_n'] = len([x for x in FR if x])
M[u'grp_sep'] = sum(len(s.split(u' ')) - 1 for s in V + U if s and s != u'(exact)' and re.search(u'\\d \\d', s))
M[u'grp_any'] = len([s for s in V + U if s and re.search(u'\\d \\d', s)])
M[u'grp_val_sep'] = sum(len(v.split(u' ')) - 1 for v in V if re.search(u'\\d \\d', v))
M[u'exp_re_plus'] = len([s for s in V if re.search(u'e\\+\\d', s)])
M[u'exp_re_minus'] = len([s for s in V if re.search(u'e-\\d', s)])
M[u'exp_re_unsigned'] = len([s for s in V if re.search(u'(?<![-+\\w])e\\d', s)])
M[u'exp_re_any'] = len([s for s in V if re.search(u'e[-+]?\\d', s)])
RE = re.compile(u'e[-+]?\\d+')
M[u'exp_vu_both'] = len([i for i in range(M[u'rows']) if RE.search(V[i]) and RE.search(U[i])])
M[u'exp_vu_same'] = len([i for i in range(M[u'rows']) if RE.search(V[i]) and RE.search(U[i])
                         and RE.search(V[i]).group(0) == RE.search(U[i]).group(0)])
M[u'exp_vu_diff'] = M[u'exp_vu_both'] - M[u'exp_vu_same']
M[u'exp_v_only'] = len([i for i in range(M[u'rows']) if RE.search(V[i]) and not RE.search(U[i])])
assert M[u'exp_re_minus'] + M[u'exp_re_unsigned'] == M[u'exp_re_any'], (M[u'exp_re_minus'], M[u'exp_re_unsigned'], M[u'exp_re_any'])

# ---------- 8. 单位列(两遍统计) ----------
M[u'unit_blank'] = len([u for u in UN if not u])
M[u'unit_filled'] = M[u'rows'] - M[u'unit_blank']
CNT = collections.Counter(u for u in UN if u)
M[u'unit_distinct'] = len(CNT)
M[u'unit_top'] = CNT.most_common(6)
M[u'unit_top_n'] = [n for _, n in CNT.most_common(6)]
M[u'unit_top_name'] = [k for k, _ in CNT.most_common(6)]
M[u'unit_once'] = len([k for k, n in CNT.items() if n == 1])
M[u'unit_hat'] = len([u for u in UN if u'^' in u])
M[u'unit_multi'] = len([u for u in UN if u' ' in u])
CNT2 = collections.Counter(u for u in [c[3] for c in COL] if u)
M[u'unit_col_distinct'] = len(CNT2)
M[u'unit_two_impl_agree'] = (CNT == CNT2)
M[u'unit_blank_exact'] = len([i for i in range(M[u'rows']) if not UN[i] and U[i] == u'(exact)'])

# ---------- 9. E 侧: 壳有多厚 ----------
E = X[u'E']
TAGS = re.findall(u'<[a-zA-Z][^>]*>', E)
TAGLESS = re.sub(u'<[^>]+>', u' ', E)
COMMENTS = re.findall(u'<!--(.*?)-->', E, re.S)
TN = collections.Counter(t[1:].split()[0].split(u'>')[0].lower() for t in TAGS)
CLOSE = len(re.findall(u'</[a-zA-Z]', E))
M[u'e_tags'] = len(TAGS)
M[u'e_close'] = CLOSE
M[u'e_tagk'] = sorted(TN)
M[u'e_tag_names'] = len(TN)
M[u'e_tag_top'] = TN.most_common(8)
M[u'e_tag_top_n'] = [n for _, n in TN.most_common(8)]
M[u'e_tag_top_name'] = [k for k, _ in TN.most_common(8)]
M[u'e_comment_n'] = len(COMMENTS)
M[u'e_comment_chars'] = sum(len(c) for c in COMMENTS)
M[u'e_comment_href'] = len([c for c in COMMENTS if u'HREF' in c.upper()])
M[u'e_prose_chars'] = len(TAGLESS.strip())
M[u'e_prose_nb'] = len(nonblank(TAGLESS))
M[u'e_body_words'] = len(re.findall(u'[A-Za-z]{2,}', TAGLESS))
M[u'e_err_words'] = len(re.findall(u'[A-Za-z]{2,}', u'ill-formed request'))
M[u'e_script'] = len(re.findall(u'(?i)<script[^a-z]', E))
M[u'e_img'] = len(re.findall(u'(?i)<img[^a-z]', E))
M[u'e_hr'] = len(re.findall(u'(?i)<hr[^a-z]', E))
M[u'e_href_all'] = len(re.findall(u'(?i)href=', E))
LINK = u'/cuu/Constants/index.html'
M[u'e_link_raw'] = E.count(LINK)
M[u'e_link_tagless'] = TAGLESS.count(LINK)
M[u'e_link_in_comment'] = len([c for c in COMMENTS if LINK in c])
M[u'e_err_phrase'] = E.count(u'you have supplied an ill-formed request')
M[u'e_sorry'] = E.count(u'Sorry')
M[u'e_try_new'] = E.count(u'Try a new search')
M[u'e_new_search'] = E.count(u'New search')
M[u'e_gtag'] = sorted(set(re.findall(u'G-[A-Z0-9]{6,}', E)))
M[u'e_gtag_n'] = len(re.findall(u'G-[A-Z0-9]{6,}', E))
M[u'e_cf_b64'] = re.findall(u"t:'([A-Za-z0-9=+/]+)'", E)
M[u'e_cf_r'] = re.findall(u"r:'([0-9a-f]+)'", E)
M[u'e_amp'] = E.count(u'&amp;')

# ---------- 10. 同批抓取: 内容里的时间戳 ⇎ 磁盘 mtime(本机可复核, 不进门槛) ----------
TOK = M[u'e_cf_b64'][0]
EPOCH = int(base64.b64decode(TOK))
M[u'tok'] = TOK
M[u'tok_epoch'] = EPOCH
M[u'tok_utc'] = datetime.datetime.fromtimestamp(EPOCH, datetime.timezone.utc).strftime(u'%Y-%m-%dT%H:%M:%SZ')
MT = dict((k, os.path.getmtime(PATH[k])) for k in ORDER)
M[u'mtime_epoch'] = [MT[k] for k in ORDER]
M[u'mtime_same_sec'] = [int(MT[k]) == EPOCH for k in ORDER]
M[u'mtime_delta'] = round(abs(MT[u'E'] - MT[u'T']), 3)
M[u'mtime_utc'] = [datetime.datetime.fromtimestamp(MT[k], datetime.timezone.utc).strftime(u'%Y-%m-%dT%H:%M:%SZ') for k in ORDER]
M[u't_year'] = re.findall(u'\\d{4} CODATA adjustment', X[u'T'])
M[u'e_title'] = re.findall(u'(?i)<title>([^<]*)</title>', E)
M[u't_urls'] = sorted(set(re.findall(u'https?://\\S+', X[u'T'])))
M[u'e_urls'] = sorted(set(re.findall(u'https?://[^"\'<> ]+', E)))
M[u'url_shared'] = sorted(set(M[u't_urls']) & set(M[u'e_urls']))
M[u'e_paths'] = sorted(set(re.findall(u'"(/[a-z]{2,3}/)[^"]*"', E, re.I)))

# ---------- 11. 候选锚池: 逐源截取 + 命中源数 ----------
POOL, SEEN = [], set()
SK = dict((k, pn(X[k])) for k in ORDER)
ROWSET = set(l.strip() for l in ROWS)
DOT = 0
for k in ORDER:
    for l in X[k].split(NL):
        s = l.strip()
        if len(s) < 22:
            continue
        if re.search(u'\\.{6,}', s):
            DOT += 1  # 分隔线: 长度够但不是话, 只计数不作锚
            continue
        n = pn(s)
        if len(n) < 14 or n in SEEN:
            continue
        SEEN.add(n)
        h = tuple(t for t in ORDER if n in SK[t])
        if not h:
            continue
        POOL.append([k, list(h), s])
M[u'pool_dot'] = DOT
M[u'pool_n'] = len(POOL)
M[u'pool_by_src'] = [len([p for p in POOL if p[0] == k]) for k in ORDER]
M[u'pool_hitn'] = [len([p for p in POOL if len(p[1]) == n]) for n in (1, 2)]
assert sum(M[u'pool_hitn']) == M[u'pool_n']
M[u'pool_disclose'] = u'锚命中判定: 两源都用原文件行(本条没有去标签这一层: T 的 \'<\' 计数为 %d)' % M[u'lt'][0]
SEL = {}
for k in ORDER:
    own = [p for p in POOL if p[0] == k and len(p[1]) == 1]
    own.sort(key=lambda p: (-len(pn(p[2])), pn(p[2])))
    dat = [p for p in own if p[2] in ROWSET]
    dat.sort(key=lambda p: (-len(pn(p[2])), pn(p[2])))
    oth = [p for p in own if p[2] not in ROWSET]
    oth.sort(key=lambda p: (-len(pn(p[2])), pn(p[2])))
    c2 = [p for p in POOL if p[0] == k and len(p[1]) == 2]
    c2.sort(key=lambda p: (-len(pn(p[2])), pn(p[2])))
    SEL[k] = {u'own': own[:12], u'own_n': len(own), u'datarow': dat[:14], u'datarow_n': len(dat),
              u'other': oth[:10], u'other_n': len(oth), u'c2': c2[:6], u'c2_n': len(c2)}
M[u'sel_own_n'] = [SEL[k][u'own_n'] for k in ORDER]
M[u'sel_datarow_n'] = [SEL[k][u'datarow_n'] for k in ORDER]
M[u'sel_other_n'] = [SEL[k][u'other_n'] for k in ORDER]
M[u'sel_c2_n'] = [SEL[k][u'c2_n'] for k in ORDER]
assert all(SEL[k][u'own'] for k in ORDER), {k: SEL[k][u'own_n'] for k in ORDER}

json.dump({u'meas': M, u'pool': POOL, u'sel': SEL, u'tags': ORDER,
           u'paths': [PATH[k] for k in ORDER],
           u'labels': {u'T': u'完整清单', u'E': u'错误页外壳'}},
          io.open(u'corpus/_b54meas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

OUT = [u'# B54 采集: CODATA 完整清单(.html 皮 0 个 \'<\') ⇎ 同批抓取的 ill-formed request 错误页, 第一遍现算']
for k in sorted(M):
    OUT.append(u'%-24s %s' % (k, M[k]))
io.open(u'corpus/_b54meas.txt', 'w', encoding='utf-8', newline=NL).write(NL.join(OUT) + NL)
print(NL.join(OUT))
print(u'池 %d 条 ｜ 分层 %s ｜ 自有 %s' % (M[u'pool_n'], M[u'pool_hitn'], M[u'sel_own_n']))
