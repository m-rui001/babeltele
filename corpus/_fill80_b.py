
# ---------- 节窗(本遍的标题识别是一条正则, 第二遍是 sect_no + lstrip 比对) ----------
RE_HD = re.compile(u'^(\\d+(?:\\.\\d+)*)(\\.?)[ \\t]+Idempotent(?: Request)? Methods$')
IDW = []
SECNO, SECHL, SECHN, SECTOC, SECBODY, ENDK, ENDH = [], [], [], [], [], [], []
for i in range(NSRC):
    hits = []
    for k, x in enumerate(L[i]):
        m = RE_HD.match(f5(x))
        if m is not None:
            hits.append((k, tuple(int(z) for z in m.group(1).split(u'.'))))
    if not hits:
        IDW.append(None); SECNO.append(None); SECHL.append(None); SECHN.append(0)
        SECTOC.append(None); SECBODY.append(None); ENDK.append(None); ENDH.append(None)
        continue
    k, tp = hits[-1]
    lvl = len(tp)
    nxt, end_kind = len(L[i]), u'eof'
    for j in range(k + 1, len(L[i])):
        tj, _ = sect5(f5(L[i][j]))
        if tj is None or len(tj) > lvl or tj < tp:
            continue
        nxt, end_kind = j, u'heading'
        break
    IDW.append(NL.join(L[i][k:nxt]))
    SECNO.append(u'.'.join(str(z) for z in tp))
    SECHL.append(L[i][k].strip())
    SECHN.append(len(hits))
    SECTOC.append(hits[0][0] + 1 if len(hits) > 1 else None)
    SECBODY.append(k + 1)
    ENDK.append(end_kind)
    ENDH.append(L[i][nxt].strip() if nxt < len(L[i]) else None)
G['sec_no'] = SECNO
G['sec_head_line'] = SECHL
G['sec_hit_n'] = SECHN
G['sec_toc_line'] = SECTOC
G['sec_body_line'] = SECBODY
G['sec_end_kind'] = ENDK
G['sec_end_head'] = ENDH
G['sec_end_head_fold'] = [f5(x) if x else None for x in ENDH]
G['sec_end_head_gap'] = [len(x) - len(f5(x)) if x else 0 for x in ENDH]
G['sec_found_n'] = len([x for x in SECNO if x])
G['sec_absent_n'] = NSRC - G['sec_found_n']
G['sec_lines'] = [x.count(NL) + 1 if x else 0 for x in IDW]
G['sec_chars'] = [len(x) if x else 0 for x in IDW]
G['sec_words'] = [w5(x) if x else 0 for x in IDW]


def sentcount5(s):
    """句数第二把尺: 逐字符扫 “.” 后跳空白落到大写/左括号/串尾(第二遍是 sent_ends 递归吃位)"""
    n, i, m = 0, 0, len(s)
    while i < m:
        j = s.find(u'.', i)
        if j < 0:
            return n
        k = j + 1
        while k < m and s[k] in u' \t\n':
            k += 1
        if k >= m or s[k].isupper() or s[k] == u'(':
            n += 1
            i = k
        else:
            i = j + 1
    return n


def dotspace5(s):
    """句数第一把尺的换档: 手工数 “. 后随空白” 的下标对(第二遍是 findall('\\.'+'\\s'))"""
    return len([j for j in range(len(s) - 1) if s[j] == u'.' and s[j + 1] in u' \t\n'])


G['sec_sents'] = [dotspace5(x) if x else 0 for x in IDW]
G['sec_sents_scan'] = [sentcount5(x) if x else 0 for x in IDW]
G['sec_sents_gap'] = [G['sec_sents'][i] - G['sec_sents_scan'][i] for i in range(NSRC)]
G['sec_row_dup'] = [G['sec_hit_n'][i] - (1 if SECNO[i] else 0) for i in range(NSRC)]
SECW = [f5(x) if x else u'' for x in IDW]
G['secw_chars'] = [len(x) for x in SECW]
G['sec_share_permille'] = [(1000 * G['sec_words'][i]) // w5(FOLD[i]) for i in range(NSRC)]
FACE = {u'strict': L, u'fold': FOLD, u'sh': SH, u'sec': SECW}
FACEI = {u'strict': 0, u'fold': 1, u'sh': 2, u'sec': 3}
FACES = [L, FOLD, SH, SECW]
WIDE = SH
TIERN = {0: u'strict', 1: u'fold', 2: u'sh', 3: u'sec'}

# ---------- 义务词阶梯 ----------
G['tone_fam'] = TONE
G['tone_norm'] = [[ub5(T[i], nd) for nd in TONE] for i in range(NSRC)]
G['tone_norm_fold'] = [[ub5(FOLD[i], nd) for nd in TONE] for i in range(NSRC)]
G['tone_straddle_k'] = [[G['tone_norm_fold'][i][k] - G['tone_norm'][i][k] for k in range(len(TONE))]
                        for i in range(NSRC)]
G['tone_straddle'] = [sum(x) for x in G['tone_straddle_k']]
G['tone_case'] = [[c5(LOWFOLD[i], nd.lower()) for nd in TONE] for i in range(NSRC)]
G['tone_case_gap'] = [sum(G['tone_case'][i]) - sum(G['tone_norm_fold'][i]) for i in range(NSRC)]
G['tone_sec'] = [[ub5(SECW[i], nd) for nd in TONE] if SECW[i] else [0] * len(TONE) for i in range(NSRC)]
G['tone_sec_tot'] = [sum(x) for x in G['tone_sec']]
G['tone_tot'] = [sum(x) for x in G['tone_norm']]
G['tone_fold_tot'] = [sum(x) for x in G['tone_norm_fold']]
G['tone_must_pure'] = [len([m for m in re.finditer(u'(?<![A-Za-z])MUST(?![A-Za-z])(?! NOT)', T[i])])
                       for i in range(NSRC)]
G['tone_must_ledger'] = [G['tone_norm'][i][1] - G['tone_norm'][i][0] - G['tone_must_pure'][i]
                         for i in range(NSRC)]
G['tone_word_lc'] = [[c5(LOWFOLD[i], w) for w in (u'must', u'should', u'may', u'can')]
                     for i in range(NSRC)]
G['tone_word_lc_tot'] = [sum(x) for x in G['tone_word_lc']]
G['tone_alnum_gap'] = [sum(ub5(T[i], nd, u'alpha') for nd in TONE)
                       - sum(ub5(T[i], nd, u'alnum') for nd in TONE) for i in range(NSRC)]
G['tone_ruler_close'] = sum(G['tone_alnum_gap'])
G['tone_wide'] = [[ub5(WIDE[i], nd) for nd in TONE] for i in range(NSRC)]
G['tone_wide_re'] = [[c5(WIDE[i], nd) for nd in TONE] for i in range(NSRC)]
G['tone_wide_close'] = sum(sum(abs(G['tone_wide'][i][k] - G['tone_wide_re'][i][k])
                               for k in range(len(TONE))) for i in range(NSRC))
G['tone_sec_per_mille'] = [(1000 * G['tone_sec_tot'][i]) // G['tone_tot'][i]
                           if G['tone_tot'][i] else -1 for i in range(NSRC)]
for i in range(NSRC):
    for k, nd in enumerate(TONE):
        assert G['tone_norm'][i][k] == mk_ub(T[i], nd), (i, nd)
        assert G['tone_wide'][i][k] == mk_ub(WIDE[i], nd)

# ---------- 答案句(段落 ⇎ 句界导出, 不手打) ----------
ANS = []
for i, pat in enumerate(ANS_HEAD):
    k = locate(T[i], pat)
    assert k >= 0, (i, pat)
    ln = len([c for c in T[i][:k] if c == NL])
    pl = []
    j = ln
    while j < len(L[i]) and L[i][j].strip() != u'':
        pl.append(j)
        j += 1
    txt, offs = u'', []
    for idx in pl:
        offs.append(len(txt))
        txt += (u'' if txt == u'' else u' ') + f5(L[i][idx])
    st = txt.find(pat)
    assert st >= 0, (i, pat)
    e = sentend5(txt[st + len(pat):])
    en = st + len(pat) + (e if e is not None else len(txt) - st - len(pat) - 1)
    cover = [kk for kk in range(len(pl)) if offs[kk] <= en and offs[kk] + len(f5(L[i][pl[kk]])) >= st]
    ANS.append(txt[st:en + 1])
    G.setdefault(u'ans_span', []).append(len(cover))
    G.setdefault(u'ans_first_line', []).append(ln)
    G.setdefault(u'ans_para_span', []).append(len(pl))
    G.setdefault(u'ans_lead_words', []).append(
        w5(f5(L[i][ln])[:f5(L[i][ln]).find(pat)]) if pat in f5(L[i][ln]) else 0)
    G.setdefault(u'ans_lines_abs', []).append([pl[kk] + 1 for kk in range(len(cover))])
G['ans'] = ANS
G['ans_words'] = [w5(x) for x in ANS]
G['ans_one_line_n'] = len([x for x in G['ans_span'] if x == 1])
G['ans_page_break'] = [len([y for y in G['ans_lines_abs'][i] if mk_is_pg(L[i][y - 1])])
                      for i in range(NSRC)]
G['ans_para_tail'] = [G['ans_para_span'][i] - G['ans_span'][i] for i in range(NSRC)]
G['ans_ph'] = ANS_PH
for i in range(NSRC):
    nd = ANS_PH[i].lower().replace(NL, u' ')
    G.setdefault(u'ph_line', []).append(sum(c5(y.lower(), nd) for y in L[i]))
    G.setdefault(u'ph_fold', []).append(c5(LOWFOLD[i], nd))
G['ph_line'] = G[u'ph_line']
G['ph_fold'] = G[u'ph_fold']
G['ph_straddle'] = [G['ph_fold'][i] - G['ph_line'][i] for i in range(NSRC)]
G['ph_raw_line'] = [len([y for y in L[i] if ANS_PH[i] in y]) for i in range(NSRC)]

# ---------- “重来”用词族 ⇎ 判词施事者 ----------
RALT5 = re.compile(u'|'.join(re.escape(x) for x in sorted(REWORD, key=lambda s: -len(s))))
ALT5 = re.compile(u'|'.join(re.escape(x) for x in sorted(AUTOFAM, key=lambda s: -len(s))))
G['reword_fam'] = REWORD
G['reword'] = [[c5(LOWFOLD[i], nd.lower()) for nd in REWORD] for i in range(NSRC)]
G['reword_union'] = [len(RALT5.findall(LOWFOLD[i])) for i in range(NSRC)]
G['reword_overlap'] = [sum(G['reword'][i]) - G['reword_union'][i] for i in range(NSRC)]
G['reword_tot'] = [sum(x) for x in G['reword']]
G['reword_zero_n'] = [len([k for k in range(len(REWORD)) if G['reword'][i][k] == 0])
                      for i in range(NSRC)]
G['reword_own'] = [[REWORD[k] for k in range(len(REWORD)) if G['reword'][i][k]
                    and all(G['reword'][j][k] == 0 for j in range(NSRC) if j != i)]
                   for i in range(NSRC)]
G['auto_fam'] = AUTOFAM
G['auto_line'] = [[sum(c5(y, nd) for y in LOW[i]) for nd in AUTOFAM] for i in range(NSRC)]
G['auto_line_rows'] = [[len([y for y in LOW[i] if nd in y]) for nd in AUTOFAM] for i in range(NSRC)]
G['auto_fold'] = [[c5(LOWFOLD[i], nd) for nd in AUTOFAM] for i in range(NSRC)]
G['auto_union_fold'] = [len(ALT5.findall(LOWFOLD[i])) for i in range(NSRC)]
G['auto_fam_overlap'] = [sum(G['auto_fold'][i]) - G['auto_union_fold'][i] for i in range(NSRC)]
G['auto_gain'] = [sum(G['auto_fold'][i]) - sum(G['auto_line'][i]) for i in range(NSRC)]
G['auto_tot_line'] = [sum(G['auto_line'][i]) for i in range(NSRC)]
G['auto_tot_fold'] = [sum(G['auto_fold'][i]) for i in range(NSRC)]
G['auto_bare'] = [c5(LOWFOLD[i], u'automatic') for i in range(NSRC)]
G['auto_bare_line'] = [sum(c5(y, u'automatic') for y in LOW[i]) for i in range(NSRC)]
G['auto_sh'] = [[c5(SH[i].lower(), nd) for nd in AUTOFAM] for i in range(NSRC)]
G['auto_sh_minus_fold'] = [sum(G['auto_sh'][i]) - sum(G['auto_fold'][i]) for i in range(NSRC)]
G['auto_bare_minus_union'] = [G['auto_bare'][i] - G['auto_union_fold'][i] for i in range(NSRC)]
G['auto_occ_rows'] = [sum(len([y for y in LOW[i] if nd in y]) for nd in AUTOFAM) for i in range(NSRC)]
G['auto_rows_minus_occ'] = [G['auto_occ_rows'][i] - sum(G['auto_line'][i]) for i in range(NSRC)]
PASSIVE = 8
G['subj_fam'] = SUBJ
G['subj'] = [[c5(FOLD[i], nd.replace(NL, u' ')) for nd in SUBJ] for i in range(NSRC)]
G['subj_line'] = [[sum(c5(y, nd) for y in L[i]) for nd in SUBJ] for i in range(NSRC)]
G['subj_straddle'] = [sum(G['subj'][i]) - sum(G['subj_line'][i]) for i in range(NSRC)]
G['subj_n'] = [len([k for k in range(len(SUBJ)) if G['subj'][i][k]]) for i in range(NSRC)]
G['subj_active'] = [sum(G['subj'][i][:PASSIVE]) for i in range(NSRC)]
G['subj_passive'] = [G['subj'][i][PASSIVE] for i in range(NSRC)]
G['subj_sec'] = [[c5(SECW[i], nd.replace(NL, u' ')) for nd in SUBJ] if SECW[i] else [0] * len(SUBJ)
                 for i in range(NSRC)]
G['subj_sec_tot'] = [sum(x) for x in G['subj_sec']]
G['subj_straddle_k'] = [[G['subj'][i][kk] - G['subj_line'][i][kk] for kk in range(len(SUBJ))]
                        for i in range(NSRC)]
G['subj_straddled'] = [[SUBJ[kk] for kk in range(len(SUBJ)) if G['subj_straddle_k'][i][kk]]
                       for i in range(NSRC)]
G['act_fam'] = ACT
G['act'] = [[c5(LOWFOLD[i], nd) for nd in ACT] for i in range(NSRC)]
G['act_sg'] = [len(re.findall(u'user agent(?!s)', LOWFOLD[i])) for i in range(NSRC)]
G['act_sg_plus_pl'] = [G['act_sg'][i] + G['act'][i][1] - G['act'][i][0] for i in range(NSRC)]
G['act_sec'] = [[c5(SECW[i].lower(), nd) for nd in ACT] if SECW[i] else [0] * len(ACT)
                for i in range(NSRC)]
G['act_sec_tot'] = [sum(x) for x in G['act_sec']]
G['act_tot'] = [sum(x) for x in G['act']]
G['num_fam'] = NUM
G['num'] = [[ub5(LOWFOLD[i], nd.lower(), bd5(nd)) for nd in NUM] for i in range(NSRC)]
G['num_raw'] = [[c5(LOWFOLD[i], nd.lower()) for nd in NUM] for i in range(NSRC)]
G['num_sub'] = [sum(G['num_raw'][i]) - sum(G['num'][i]) for i in range(NSRC)]
G['num_tot'] = [sum(x) for x in G['num']]
G['num_own'] = [[NUM[k] for k in range(len(NUM)) if G['num'][i][k]
                 and all(G['num'][j][k] == 0 for j in range(NSRC) if j != i)] for i in range(NSRC)]
G['num_rename'] = [G['num'][i][4] - G['num'][i][5] for i in range(NSRC)]
G['meth_fam'] = METH
G['meth_sec'] = [[ub5(SECW[i], nd) for nd in METH] if SECW[i] else [0] * len(METH) for i in range(NSRC)]
G['meth_sec_n'] = [len([x for x in G['meth_sec'][i] if x]) for i in range(NSRC)]
G['meth_post_sec'] = [G['meth_sec'][i][4] for i in range(NSRC)]
G['meth_all'] = [[ub5(WIDE[i], nd) for nd in METH] for i in range(NSRC)]
G['meth_all_n'] = [len([x for x in G['meth_all'][i] if x]) for i in range(NSRC)]

# ---------- Retry-After 轴 ⇎ 反向对照 ⇎ 状态码 ⇎ 括号印法 ----------
G['ra_count'] = [c5(T[i], u'Retry-After') for i in range(NSRC)]
RABLINE = [[x for x in L[i] if abnf5(x)] for i in range(NSRC)]
G['ra_abnf_lines'] = [len(x) for x in RABLINE]
G['ra_abnf_forms'] = [len(set(f5(x) for x in RABLINE[i])) for i in range(NSRC)]
G['ra_abnf_bar'] = [len([x for x in RABLINE[i] if u'|' in x]) for i in range(NSRC)]
G['ra_abnf_slash'] = [len([x for x in RABLINE[i] if u' / ' in x]) for i in range(NSRC)]
G['ra_abnf_quoted'] = [len([x for x in RABLINE[i] if u'"Retry-After"' in x]) for i in range(NSRC)]
G['ra_abnf_ledger'] = [G['ra_abnf_bar'][i] + G['ra_abnf_slash'][i] - G['ra_abnf_lines'][i]
                       for i in range(NSRC)]
G['ra_exp_date'] = [c5(T[i], u'Retry-After: Fri, 31 Dec 1999 23:59:59 GMT') for i in range(NSRC)]
G['ra_exp_120'] = [c5(T[i], u'Retry-After: 120') for i in range(NSRC)]
G['ra_exp_3600'] = [c5(T[i], u'Retry-After: 3600') for i in range(NSRC)]
G['ra_two_minutes'] = [c5(LOWFOLD[i], u'the delay is 2 minutes') for i in range(NSRC)]
G['ra_delta_def'] = [c5(LOWFOLD[i], u'non-negative decimal integer') for i in range(NSRC)]
G['ra_colon_rows'] = [len([x for x in L[i] if f5(x).startswith(u'Retry-After:')]) for i in range(NSRC)]
G['neg_fam'] = NEG
G['neg_digit'] = [k for k, nd in enumerate(NEG) if nd.isdigit()]
G['neg_raw'] = [[c5(T[i], nd) for nd in NEG] for i in range(NSRC)]
G['neg_bnd'] = [[ub5(T[i], nd, bd5(nd)) for nd in NEG] for i in range(NSRC)]
G['neg_false_sub'] = [sum(G['neg_raw'][i]) - sum(G['neg_bnd'][i]) for i in range(NSRC)]
G['neg_zero_n'] = [len([k for k in range(len(NEG)) if G['neg_bnd'][i][k] == 0]) for i in range(NSRC)]
G['neg_own'] = [[k for k in range(len(NEG)) if G['neg_bnd'][i][k]
                 and all(G['neg_bnd'][j][k] == 0 for j in range(NSRC) if j != i)]
                for i in range(NSRC)]
G['neg_own_lbl'] = [[NEG[k] for k in G['neg_own'][i]] for i in range(NSRC)]
G['neg_tot'] = [sum(x) for x in G['neg_bnd']]
G['code_fam'] = CODES
for i in range(NSRC):
    for c in CODES:
        assert [x for x in L[i] if code5(x, c)] == [x for x in L[i] if mk_code_row(x, c)], (i, c)
CODES_I = [[[x for x in L[i] if code5(x, c)] for c in CODES] for i in range(NSRC)]
G['code_defined_raw'] = [len([y for rows in CODES_I[i] for y in rows]) for i in range(NSRC)]
G['code_defined'] = [[len([y for y in rows if u'...' not in y]) for rows in CODES_I[i]]
                     for i in range(NSRC)]
G['code_defined_n'] = [sum(x) for x in G['code_defined']]
G['code_toc'] = [G['code_defined_raw'][i] - G['code_defined_n'][i] for i in range(NSRC)]
G['code_defined_lbl'] = [[CODES[k] for k in range(len(CODES)) if G['code_defined'][i][k]]
                         for i in range(NSRC)]
G['code_absent_lbl'] = [[CODES[k] for k in range(len(CODES)) if not G['code_defined'][i][k]]
                        for i in range(NSRC)]
G['paren_fam'] = PAREN
G['paren'] = [[c5(FOLD[i], nd) for nd in PAREN] for i in range(NSRC)]
G['paren_line'] = [[sum(c5(y, nd) for y in L[i]) for nd in PAREN] for i in range(NSRC)]
G['paren_straddle'] = [sum(G['paren'][i]) - sum(G['paren_line'][i]) for i in range(NSRC)]

# ---------- 逐字搬字: 行尺池 ⇎ 配对 ⇎ 归属分档 ----------
POOL = [[f5(x) for x in L[i] if len(x.strip()) >= 30 and not mk_is_pick(x)] for i in range(NSRC)]
PAIRS = [(a, b) for a, b in IT.combinations(range(NSRC), 2)]
PS = [set(p) for p in POOL]
P2 = {}
for a, b in PAIRS:
    P2[u'%s-%s' % (LBL[a], LBL[b])] = len([k for k in PS[a] if k in PS[b]])
G['pair_shared'] = P2
G['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
G['pair_share'] = [P2[u'%s-%s' % (LBL[a], LBL[b])] for a, b in PAIRS]
G['pair_nonzero'] = len([x for x in G['pair_share'] if x])
G['pair_zero'] = len(PAIRS) - G['pair_nonzero']
_mx, _mi = -1, None
for n, (a, b) in enumerate(PAIRS):
    if P2[u'%s-%s' % (LBL[a], LBL[b])] > _mx:
        _mx, _mi = P2[u'%s-%s' % (LBL[a], LBL[b])], u'%s-%s' % (LBL[a], LBL[b])
G['pair_max_lbl'] = _mi
G['pair_max'] = _mx
ML = _mi.split(u'-')
G['pair_lbl_idx'] = [LBL.index(ML[0]), LBL.index(ML[1])]
BA, BB = G['pair_lbl_idx']
ORIG = [defaultdict(set) for _ in range(NSRC)]
for i in range(NSRC):
    for x in L[i]:
        if len(x.strip()) >= 30 and not mk_is_pick(x):
            ORIG[i][f5(x)].add(x)
G['pair_max_byte_keys'] = len([k for k in ORIG[BA] if k in ORIG[BB] and (ORIG[BA][k] & ORIG[BB][k])])
G['pair_max_norm_only_keys'] = len([k for k in ORIG[BA] if k in ORIG[BB]
                                    and not (ORIG[BA][k] & ORIG[BB][k])])
RA_W = set(x for x in L[BA] if len(x.strip()) >= 30)
RB_W = set(x for x in L[BB] if len(x.strip()) >= 30)
G['pair_max_byte_lines'] = len([x for x in RB_W if x in RA_W])
G['pair_max_norm_only_lines'] = G['pair_max'] - G['pair_max_byte_lines']
G['pair_byte_lines_to_keys'] = len(set(f5(x) for x in [y for y in RA_W if y in RB_W]))
G['pair_byte_unit_gap'] = G['pair_max_byte_lines'] - G['pair_byte_lines_to_keys']
G['pair_byte_shell_gap'] = G['pair_byte_lines_to_keys'] - G['pair_max_byte_keys']
G['pair_byte_lines_ge_keys'] = 1 if G['pair_max_byte_lines'] >= G['pair_max_byte_keys'] else 0
G['pool_n'] = sum(len(x) for x in POOL)
G['pool_union'] = len(set().union(*PS))
G['pool_rows_minus_union'] = G['pool_n'] - G['pool_union']
UN = set().union(*PS)
PRES = dict((a, tuple(i for i in range(NSRC) if a in PS[i])) for a in UN)
_hist = Counter(len(v) for v in PRES.values())
G['pool_tier'] = [_hist.get(k, 0) for k in range(1, NSRC + 1)]
G['pool_tier_close'] = sum(G['pool_tier']) - G['pool_union']
# 容斥走“对文档下标的组合逐枚求交”(第二遍是 C(len(v),k) 逐元算式)
_incl = []
for kk in range(1, NSRC + 1):
    _incl.append(sum(len(set.intersection(*[PS[t] for t in cmb]))
                     for cmb in IT.combinations(range(NSRC), kk)))
G['pool_incl'] = _incl
G['union_incl'] = sum((-1) ** (kk + 1) * _incl[kk - 1] for kk in range(1, NSRC + 1))
G['union_close'] = G['pool_union'] - G['union_incl']
G['pair_byte'] = [len([k for k in ORIG[a] if k in ORIG[b] and (ORIG[a][k] & ORIG[b][k])])
                  for a, b in PAIRS]
G['pair_norm_only'] = [len([k for k in ORIG[a] if k in ORIG[b] and not (ORIG[a][k] & ORIG[b][k])])
                       for a, b in PAIRS]
G['pair_close'] = sum(G['pair_share']) - sum(G['pair_byte']) - sum(G['pair_norm_only'])
G['pair_7231_9110'] = G['pair_share'][PAIRS.index((1, 4))]
G['pair_2616_9110'] = G['pair_share'][PAIRS.index((0, 4))]
G['pair_2616_7231'] = G['pair_share'][PAIRS.index((0, 1))]

# ---------- 分家四桶 ----------
def bucket5(o, p):
    """归一因由四桶: 本遍用 dh5 ⇎ p5 ⇎ 逐字符扫, 与第二遍的 bucket 逐对对拍"""
    if o.lower() == p.lower():
        return u'case'
    if dh5(o) == dh5(p):
        return u'hyph'
    if o.strip() == p.strip():
        return u'space'
    return u'multi'

axis = dict((w, 0) for w in RANK)
NORM_ONLY, BSAME = [], []
VAR = {}
for a in sorted(PS[BA] & PS[BB]):
    va, vb = ORIG[BA][a], ORIG[BB][a]
    VAR[a] = (va, vb)
    if va & vb:
        BSAME.append(a)
        continue
    NORM_ONLY.append(a)
    dif = [(o, q) for o in va for q in vb]
    _b = None
    for o, q in dif:
        w = bucket5(o, q)
        if _b is None or RANK[w] < RANK[_b]:
            _b = w
    axis[_b] += 1
G['axis_counts'] = axis
G['axis_total'] = sum(axis.values())
G['axis_rows'] = NORM_ONLY
G['pair_pool_byte'] = len(BSAME)
G['pair_pool_norm_only'] = len(NORM_ONLY)
G['axis_close'] = (G['pair_max'] - G['pair_pool_byte'] - G['pair_pool_norm_only']
                   + abs(G['pair_max_byte_keys'] - G['pair_pool_byte'])
                   + abs(G['pair_max_norm_only_keys'] - G['pair_pool_norm_only']))
G['axis_str'] = u' ⇎ '.join(u'%s%d' % (w, axis[w]) for w in (u'case', u'hyph', u'space', u'multi'))
G['axis_str_n'] = len([w for w in axis if axis[w]])




for a in NORM_ONLY:
    va, vb = VAR[a]
    assert min((bucket5(o, q) for o, q in [(x, y) for x in va for y in vb]),
               key=lambda w: RANK[w]) == min((mk_bucket(o, q) for o, q in [(x, y) for x in va for y in vb]),
                                             key=lambda w: RANK[w]), a

# ---------- 句尺 ----------
SP = [set(x for x in sents5(WIDE[i]) if len(x) >= 40) for i in range(NSRC)]
for i in range(NSRC):
    assert SP[i] == set(x for x in mk_sents(WIDE[i]) if len(x) >= 40), i
SPRES = dict((a, tuple(i for i in range(NSRC) if a in SP[i])) for s in SP for a in s)
G['s_pool_n'] = len(SPRES)
_sh = Counter(len(v) for v in SPRES.values())
G['s_pool_tier'] = [_sh.get(k, 0) for k in range(1, NSRC + 1)]
G['s_pool_tier_close'] = sum(G['s_pool_tier']) - G['s_pool_n']
G['s_pair_share'] = [len(SP[a] & SP[b]) for a, b in PAIRS]
G['s_pair_max'] = max(G['s_pair_share'])
G['s_pair_max_idx'] = G['s_pair_share'].index(G['s_pair_max'])
G['s_pair_max_lbl'] = G['pair_lbl'][G['s_pair_max_idx']]
G['s_pair_7231_9110'] = G['s_pair_share'][PAIRS.index((1, 4))]
G['s_pair_2616_9110'] = G['s_pair_share'][PAIRS.index((0, 4))]
G['s_ruler_gain_7231_9110'] = G['s_pair_7231_9110'] - G['pair_7231_9110']
G['s_ruler_gain_2616_9110'] = G['s_pair_2616_9110'] - G['pair_2616_9110']
G['s_pair_nonzero'] = len([x for x in G['s_pair_share'] if x])
_s1 = sum(len(SP[i]) for i in range(NSRC))
_sin = []
for kk in range(1, NSRC + 1):
    _sin.append(sum(len(set.intersection(*[SP[t] for t in cmb]))
                    for cmb in IT.combinations(range(NSRC), kk)))
G['s_incl'] = [_s1] + _sin[1:]
G['s_union_incl'] = sum((-1) ** (kk + 1) * G['s_incl'][kk - 1] for kk in range(1, NSRC + 1))
G['s_union_close'] = G['s_pool_n'] - G['s_union_incl']

# ---------- 锚候选池 ----------
apool = []
for i in range(NSRC):
    for x in SHP[i]:
        if len(p5(x)) >= 24 and len([c for c in x if c.isalpha()]):
            apool.append((p5(x), i))
AP = defaultdict(set)
for a, i in apool:
    AP[a].add(i)
G['apool_n'] = len(AP)
G['apool_raw_n'] = len(apool)
G['apool_face_raw'] = [len([1 for a, k in apool if k == i]) for i in range(NSRC)]
G['apool_tag_n'] = [len([a for a, v in AP.items() if i in v]) for i in range(NSRC)]
G['apool_dup'] = [G['apool_face_raw'][i] - G['apool_tag_n'][i] for i in range(NSRC)]
G['apool_tag_close'] = sum(G['apool_tag_n']) + sum(G['apool_dup']) - G['apool_raw_n']
_ath = Counter(len(v) for v in AP.values())
G['apool_tier'] = [_ath.get(n, 0) for n in range(1, NSRC + 1)]
G['apool_weight'] = sum(G['apool_tier'][n] * (n + 1) for n in range(NSRC))
G['apool_pairs'] = sum(G['apool_tag_n'])
G['apool_tier_close'] = G['apool_weight'] - G['apool_pairs']
G['apool_maxlen'] = max(len(a) for a in AP)

# ---------- 序列化式子 ----------
HF = [[hdrform5(x) for x in L[i]] for i in range(NSRC)]
G['hdr_dot2sp'] = [len([1 for h in HF[i] if h == u'dot2sp']) for i in range(NSRC)]
G['hdr_dot1sp'] = [len([1 for h in HF[i] if h == u'dot1sp']) for i in range(NSRC)]
G['hdr_nodot'] = [len([1 for h in HF[i] if h == u'nodot']) for i in range(NSRC)]
G['dblspace_in_fold'] = [c5(FOLD[i], u'  ') for i in range(NSRC)]


def dotsp2(s):
    out, k, m = 0, 0, len(s)
    while k + 3 < m:
        if (not s[k].isspace() and s[k + 1] == u'.' and s[k + 2: k + 4] == u'  '
                and not s[k + 4].isspace()):
            out += 1
            k += 5
            continue
        k += 1
    return out


G['dot_dblspace_anywhere'] = [dotsp2(FOLD[i]) for i in range(NSRC)]
for i in range(NSRC):
    assert G['dot_dblspace_anywhere'][i] == len(re.findall(u'\\S\\.  \\S', FOLD[i])), i


def hypbreak(i):
    n = 0
    for j in range(len(L[i]) - 1):
        s = L[i][j].rstrip()
        t = L[i][j + 1]
        if s.endswith(u'-') and (t.lstrip(u' \t')[:1].islower()):
            n += 1
    return n


G['hyphen_break'] = [hypbreak(i) for i in range(NSRC)]
G['hyb_idem'] = [c5(T[i], u'non-' + NL + u'idempotent') for i in range(NSRC)]
G['idem_str'] = [c5(LOWFOLD[i], u'idempotent') for i in range(NSRC)]
G['idem_line_occ'] = [sum(c5(y, u'idempotent') for y in LOW[i]) for i in range(NSRC)]
G['idem_line_rows'] = [len([y for y in LOW[i] if u'idempotent' in y]) for i in range(NSRC)]
G['idem_hyb_line'] = [sum(c5(y, u'non-idempotent') for y in LOW[i]) for i in range(NSRC)]
G['idem_hyb_fold'] = [c5(LOWFOLD[i], u'non-idempotent') for i in range(NSRC)]
G['hyb_straddle'] = [G['idem_hyb_fold'][i] - G['idem_hyb_line'][i] for i in range(NSRC)]
G['idem_row_minus_occ'] = [G['idem_line_occ'][i] - G['idem_line_rows'][i] for i in range(NSRC)]

# ---------- 锚句: 由起止针在指定面上导出 ----------
def mk_nd5(o, s0, e0, fa):
    if s0.startswith(u'@'):
        return s0[1:]
    face = FACE[fa][o]
    a = locate(face, s0)
    assert a >= 0, (u'起针落空', LBL[o], fa, s0)
    if not e0:
        return s0
    b = locate(face, e0, a)
    assert b >= 0, (u'止针落空', LBL[o], fa, e0)
    return face[a:b + len(e0)]


TEXT = {}
NEGND = [k for o, k, fa, s0, e0 in SENT if s0.startswith(u'@')]
for (o, k, fa, s0, e0) in SENT:
    TEXT[k] = s0[1:] if k in NEGND else mk_nd5(o, s0, e0, fa)
OWNER = dict((k, o) for o, k, _, _, _ in SENT)
GN = [k for o, k, _, _, _ in SENT]
assert TEXT == CH[u'litk'], sorted([k for k in TEXT if TEXT[k] != CH[u'litk'].get(k)])[:3]


def hit5(k, tier):
    nd = TEXT[k]
    o = OWNER[k]
    if not nd:
        return 0
    if tier == 0:
        return len([x for x in L[o] if nd in x])
    face = FACE[TIERN[tier]][o]
    return c5(face, nd)


SN = dict((k, [hit5(k, n) for n in range(4)]) for k in GN)
for k in GN:
    for n in (1, 2, 3):
        assert SN[k][n] == mk_cnt_re(FACE[TIERN[n]][OWNER[k]], TEXT[k]), (k, n)
G['needle_n'] = len(GN)
G['neg_n'] = len(NEGND)
for n in range(4):
    G[u'sn_' + TIERN[n] + u'_docs'] = [len([k for k in GN if OWNER[k] == i and SN[k][n]])
                                       for i in range(NSRC)]
for k in GN:
    G[u'n_' + k] = SN[k]
G['needles_owned'] = [len([k for k in GN if OWNER[k] == i]) for i in range(NSRC)]
G['fold_minus_strict_keys'] = [k for k in GN if not SN[k][0] and SN[k][1]]
G['fold_minus_strict_own'] = [len([k for k in G['fold_minus_strict_keys'] if OWNER[k] == i])
                              for i in range(NSRC)]
G['fold_minus_strict_n'] = len(G['fold_minus_strict_keys'])
G['sh_loses_keys'] = [k for k in GN if SN[k][1] and not SN[k][2]]
G['sh_gains_keys'] = [k for k in GN if SN[k][2] and not SN[k][1]]
G['sh_loses'] = [len([k for k in G['sh_loses_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['sh_gains'] = [len([k for k in G['sh_gains_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['sec_scope'] = [1 if SECW[i] else 0 for i in range(NSRC)]
G['sh_no_sec_keys'] = [k for k in GN if SN[k][2] and not SN[k][3] and G['sec_scope'][OWNER[k]]]
G['sh_no_sec_own'] = [len([k for k in G['sh_no_sec_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['sh_no_sec_n'] = len(G['sh_no_sec_keys'])
G['sn_sec_docs_scope'] = [G['sn_sec_docs'][i] if SECW[i] else -1 for i in range(NSRC)]
G['dead_needles'] = [k for k in GN if k not in NEGND and max(SN[k]) == 0]
G['neg_controls'] = sorted(NEGND)
G['neg_own_nd'] = [len([k for k in NEGND if OWNER[k] == i]) for i in range(NSRC)]
G['neg_hit_widest'] = sum(max(SN[k]) for k in NEGND)
G['neg_hit_strict'] = sum(SN[k][0] for k in NEGND)
G['strict_neg_own'] = [len([k for k in NEGND if OWNER[k] == i and SN[k][0]]) for i in range(NSRC)]
G['fold_neg_own'] = [len([k for k in NEGND if OWNER[k] == i and SN[k][1]]) for i in range(NSRC)]
G['ladder_close'] = sum(
    abs(G['sn_strict_docs'][i] + G['fold_minus_strict_own'][i] + G['strict_neg_own'][i]
        - G['sn_fold_docs'][i] - G['fold_neg_own'][i])
    + abs(G['sn_fold_docs'][i] - G['sh_loses'][i] + G['sh_gains'][i] - G['sn_sh_docs'][i])
    + (0 if not SECW[i] else
       abs(G['sn_sh_docs'][i] - G['sh_no_sec_own'][i] - G['sn_sec_docs'][i]))
    for i in range(NSRC))
G['ladder_monotone'] = 1 if all(G['sn_strict_docs'][i] <= G['sn_fold_docs'][i]
                                and G['sn_sec_docs'][i] <= G['sn_sh_docs'][i]
                                for i in range(NSRC)) else 0
G['overlap_extra'] = sum(o5(WIDE[OWNER[k]], TEXT[k]) - c5(WIDE[OWNER[k]], TEXT[k])
                         for k in GN if TEXT[k] and k not in NEGND)
G['re_eq_cur'] = 1 if all(r5(FACES[n][OWNER[k]], TEXT[k]) == c5(FACES[n][OWNER[k]], TEXT[k])
                          for k in GN if TEXT[k] and k not in NEGND for n in range(1, 3)) else 0
G['nd_len'] = [len(TEXT[k]) for k in GN]
G['nd_len_tot'] = sum(G['nd_len'])
G['nd_len_max'] = max(G['nd_len'])
G['idem_sent_same'] = 1 if TEXT[u'a7231_idem'] == TEXT[u'a9110_idem'] else 0
G['idem_line_7231'] = len([c for c in T[1][:locate(T[1], u'Idempotent methods are distinguished')]
                           if c == NL]) + 1
G['idem_line_9110'] = len([c for c in T[4][:locate(T[4], u'Idempotent methods are distinguished')]
                           if c == NL]) + 1
G['idem_shift'] = G['idem_line_9110'] - G['idem_line_7231']
G['idem_wrap_7231'] = len([y for y in L[1] if u'Idempotent methods are distinguished' in y])
G['idem_wrap_9110'] = len([y for y in L[4] if u'Idempotent methods are distinguished' in y])
G['like_sent_same'] = 1 if TEXT[u'a7231_like'] == TEXT[u'a9110_like'] else 0
G['like_line_7231'] = len([j + 1 for j, y in enumerate(L[1]) if u'Like the definition of safe' in y])
G['like_abs_7231'] = [j + 1 for j, y in enumerate(L[1]) if u'Like the definition of safe' in y][0]
G['like_abs_9110'] = [j + 1 for j, y in enumerate(L[4]) if u'Like the definition of safe' in y][0]
G['like_shift'] = G['like_abs_9110'] - G['like_abs_7231']
G['like_hit_sh'] = [SN[u'a7231_like'][2], SN[u'a9110_like'][2]]
G['like_absent_2616'] = c5(SH[0], TEXT[u'a7231_like'])
G['defin_absent_7231'] = c5(FOLD[1], TEXT[u'a2616_defin'])
G['nonidem_straddle'] = SN[u'a2616_nonidem']
G['sidefx_in_sec'] = SN[u'a2616_sidefx'][3]
VKEY = [u'a2616_passive', u'a2616_repeat', u'a2616_confirm']
G['v_keys'] = VKEY
G['v_in_sh'] = len([k for k in VKEY if SN[k][2]])
G['v_in_sec'] = len([k for k in VKEY if SN[k][3]])
G['v_sh_no_sec'] = len([k for k in VKEY if k in G['sh_no_sec_keys']])
G['defin_in_sec'] = SN[u'a2616_defin'][3]
G['defin_in_sh'] = SN[u'a2616_defin'][2]
G['xref_line'] = len([1 for y in L[0] if u'see section 9.1.2' in y])
XREF = [j + 1 for j, y in enumerate(L[0]) if u'see section 9.1.2' in y]
G['xref_lines_abs'] = XREF
G['xref_to_head'] = [G['sec_body_line'][0] - z for z in XREF]
G['verdict_lines_abs'] = [j + 1 for j, y in enumerate(L[0])
                          if u'Non-idempotent methods or sequences' in y]
G['verdict_head_gap'] = G['sec_body_line'][0] - G['verdict_lines_abs'][0]
G['verdict_xref_same_line'] = 1 if all(any(v == z for z in XREF)
                                       for v in G['verdict_lines_abs']) else 0
K9 = [k for k in GN if OWNER[k] == 4 and k not in NEGND]
G['k9110_in_sec'] = len([k for k in K9 if SN[k][3]])
G['k9110_tot'] = len(K9)
G['k9110_no_sec'] = len([k for k in K9 if SN[k][2] and not SN[k][3]])
assert G['dead_needles'] == FLAT[u'dead_needles'] and G['neg_controls'] == FLAT[u'neg_controls']
assert G['ans'] == FLAT[u'ans'] and G['sec_no'] == FLAT[u'sec_no']
