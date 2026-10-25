
# ---------- 段窗层(SCAN2): 行号映射走 bisect, 段界定位走编译针的 search ----------
SHPN = []
for i in range(NSRC):
    _sh = []
    for n in range(len(L[i])):
        if not mk_is_pick(L[i][n]):
            _sh.append((n + 1, L[i][n]))
    SHPN.append(_sh)
PP = []
for i in range(NSRC):
    PP.append([(n, u' '.join(x.split())) for n, x in SHPN[i]])
    PP[i] = [p for p in PP[i] if p[1] != u'']
for i in range(NSRC):
    assert [x for _, x in SHPN[i]] == SHP[i], i
    assert u' '.join(x for _, x in PP[i]) == WIDE[i], i
def _map(i):
    """偏移→原行号的对照表: 本遍把“片段之间的一个空格”累加成显式数组(第二遍在查表时现算)"""
    offs, lns, acc, first = [], [], 0, True
    for ln, s in PP[i]:
        if not first:
            acc += 1
        first = False
        offs.append(acc)
        lns.append(ln)
        acc += len(s)
    return offs, lns


MAPS = [_map(i) for i in range(NSRC)]


def line_of5(i, a):
    return MAPS[i][1][bisect.bisect_right(MAPS[i][0], a) - 1]


G['pp_rows'] = [len(x) for x in PP]
G['pp_gap_rows'] = [G['nonblank'][i] - G['pp_rows'][i] for i in range(NSRC)]
ALN = SHPN
ANSET = [set(x for _, x in ALN[i]) for i in range(NSRC)]
ALND = [dict(ALN[i]) for i in range(NSRC)]
FAN = [p5(t) for t in T]
for i in range(NSRC):
    assert FAN[i] == mk_pnorm(T[i]), i
    assert len(ALND[i]) == len(ALN[i]), i


def blk5(i, start, end):
    a = locate(WIDE[i], start)
    assert a >= 0, (LBL[i], start)
    b = locate(WIDE[i], end, a)
    assert b >= 0, (LBL[i], end)
    e = b + len(end)
    return u' '.join(WIDE[i][a:e].split()), line_of5(i, a), line_of5(i, e - 1)


def ln_of5(i, nd, frm=0):
    a = locate(WIDE[i], nd, frm)
    assert a >= 0, (LBL[i], nd)
    return a, line_of5(i, a)


def ln_end5(i, nd, frm=0):
    a = locate(WIDE[i], nd, frm)
    assert a >= 0, (LBL[i], nd)
    return a, line_of5(i, a + len(nd) - 1)


def line_holds5(i, ln, nd):
    return 1 if p5(nd) in p5(ALND[i][ln]) else 0


PB = [blk5(i, s, e) for i, s, e in PINS]
PTXT = [p[0] for p in PB]
G['blk_lo'] = [p[1] for p in PB]
G['blk_hi'] = [p[2] for p in PB]
G['blk_rows'] = [p[2] - p[1] + 1 for p in PB]
G['blk_chars'] = [len(p[0]) for p in PB]
G['blk_words'] = [w5(p[0]) for p in PB]
PW = [p[0].lower().split() for p in PB]
G['blk_vocab'] = [len(set(x)) for x in PW]
G['blk_five_chars'] = sum(G['blk_chars'][:5])
G['blk_five_words'] = sum(G['blk_words'][:5])
G['blk_rows_tot'] = sum(G['blk_rows'])
G['blk_words_tot'] = sum(G['blk_words'])
G['blk_five_rows'] = sum(G['blk_rows'][:5])
G['tone_must_blk'] = [ub5(p, u'MUST') for p in PTXT]
G['tone_may_blk'] = [ub5(p, u'MAY') for p in PTXT]
G['tone_should_blk'] = [ub5(p, u'SHOULD') for p in PTXT]
G['tone_mustnot_blk'] = [ub5(p, u'MUST NOT') for p in PTXT]
G['tone_in_blk'] = [G['tone_must_blk'][n] + G['tone_may_blk'][n] + G['tone_should_blk'][n]
                    for n in range(len(PB))]
G['blk_must_cur'] = [c5(p, u'MUST') for p in PTXT]
G['blk_must_re'] = [len(re.findall(u'MUST', p)) for p in PTXT]
G['blk_tone_ruler_close'] = (sum(abs(G['tone_must_blk'][n] - G['blk_must_cur'][n])
                                 for n in range(len(PB)))
                             + sum(abs(G['tone_must_blk'][n] - G['blk_must_re'][n])
                                   for n in range(len(PB))))


def suffix_words(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def head_words(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


G['pre_idem_7231_9110'] = head_words(PW[1], PW[8])
G['suf_idem_7231_9110'] = suffix_words(PW[1], PW[8])
G['pre_like_7231_9110'] = head_words(PW[5], PW[6])
G['suf_like_7231_9110'] = suffix_words(PW[5], PW[6])
G['idem_blk_same'] = 1 if PTXT[1] == PTXT[8] else 0
G['like_blk_same'] = 1 if PTXT[5] == PTXT[6] else 0
G['w_common_idem'] = len(set(PW[1]) & set(PW[8]))
G['w_only_9110_idem'] = len(set(PW[8]) - set(PW[1]))
G['w_only_7231_idem'] = len(set(PW[1]) - set(PW[8]))
G['w_ledger_idem'] = (G['w_only_9110_idem'] + G['w_common_idem'] - G['blk_vocab'][8]
                      + G['w_only_7231_idem'] + G['w_common_idem'] - G['blk_vocab'][1])
G['idem_blk_row_gap'] = G['blk_lo'][8] - G['blk_lo'][1]
G['like_blk_row_gap'] = G['blk_lo'][6] - G['blk_lo'][5]
G['blk_gap_delta'] = G['idem_blk_row_gap'] - G['like_blk_row_gap']
G['blk_words_per_row'] = [G['blk_words'][n] // G['blk_rows'][n] for n in range(5)]
G['blk_is_one_line'] = [1 if G['blk_rows'][n] == 1 else 0 for n in range(5)]
G['blk_one_line_n'] = sum(G['blk_is_one_line'])
G['ln_verdict_2616'] = ln_of5(0, u'Non-idempotent methods or sequences MUST NOT')[1]
G['ln_confirm_end_2616'] = ln_end5(0, u'user confirmation.')[1]
G['ln_idem_7231'] = ln_of5(1, u'Idempotent methods are distinguished because')[1]
G['ln_idem_9110'] = ln_of5(4, u'Idempotent methods are distinguished because')[1]
G['ln_proxy_9110'] = ln_of5(4, u'A proxy MUST NOT automatically retry')[1]
G['ln_proxy_head_9110'] = ln_of5(4, u'A proxy MUST NOT')[1]
G['ln_client_head_9110'] = ln_of5(4, u'A client SHOULD NOT automatically retry')[1]
G['ln_client_9110'] = ln_end5(4, u'client SHOULD NOT automatically retry a failed automatic retry.')[1]
G['ln_might_head_9110'] = ln_of5(4, u'a client might automatically retry a POST')
G['ln_might_end_9110'] = ln_end5(4, u'a client might automatically retry a POST')
G['might_straddle'] = G['ln_might_end_9110'][1] - G['ln_might_head_9110'][1]
G['ln_might_full_end_9110'] = ln_end5(4, u'persistent connection was used.')
G['ln_riskier_9110'] = ln_of5(4, u'Some clients take a riskier approach')[1]
G['ln_selfdeny_6585'] = ln_of5(2, u'Note that this specification does not define')[1]
G['ln_429_6585'] = ln_of5(2, u'The 429 status code indicates')[1]
G['ln_425_8470'] = ln_of5(3, u'User agents that send a request in early data')[1]
G['ln_assume_8470'] = ln_of5(3, u'The server cannot assume that a client is able')[1]
G['sec_head_line_2616'] = G['sec_body_line'][0]
G['sec_head_line_9110'] = G['sec_body_line'][4]
G['verdict_above_head_2616'] = 1 if G['ln_verdict_2616'] < G['sec_head_line_2616'] else 0
G['proxy_inside_head_9110'] = 1 if G['ln_proxy_9110'] > G['sec_head_line_9110'] else 0
RT = [(0, G['ln_verdict_2616'], u'Non-idempotent methods or sequences'),
      (0, G['ln_confirm_end_2616'], u'user confirmation.'),
      (1, G['ln_idem_7231'], u'Idempotent methods are distinguished'),
      (4, G['ln_idem_9110'], u'Idempotent methods are distinguished'),
      (4, G['ln_proxy_9110'], u'A proxy MUST NOT automatically retry'),
      (4, G['ln_client_9110'], u'client SHOULD NOT automatically retry a failed automatic retry.'),
      (4, G['ln_might_end_9110'][1], u'automatically retry a POST request'),
      (4, G['ln_might_full_end_9110'][1], u'persistent connection was used.'),
      (2, G['ln_429_6585'], u'The 429 status code indicates'),
      (2, G['ln_selfdeny_6585'], u'Note that this specification does not define'),
      (3, G['ln_425_8470'], u'User agents that send a request in early data'),
      (3, G['ln_assume_8470'], u'The server cannot assume that a client is able'),
      (4, G['ln_riskier_9110'], u'Some clients take a riskier approach')]
G['pin_rt'] = [line_holds5(i, ln, nd) for i, ln, nd in RT]
G['pin_rt_n'] = len(G['pin_rt'])
G['pin_rt_ok'] = sum(G['pin_rt'])
G['pin_rt_src'] = [len([1 for i, _, _ in RT if i == n]) for n in range(NSRC)]
G['pin_wrongline'] = sum([line_holds5(4, G['ln_might_head_9110'][1], TEXT[u'a9110_might']),
                          line_holds5(4, G['ln_client_head_9110'],
                                       u'A client SHOULD NOT automatically retry a failed automatic retry.')])

# ---------- 转置尺 ----------
G[u'num_dsec_docs'] = [G[u'num'][i][5] for i in range(NSRC)]
G[u'num_delay_docs'] = [G[u'num'][i][4] for i in range(NSRC)]
G[u'num_httpdate_docs'] = [G[u'num'][i][6] for i in range(NSRC)]
G[u'num_3600_docs'] = [G[u'num'][i][0] for i in range(NSRC)]
G[u'num_120_docs'] = [G[u'num'][i][1] for i in range(NSRC)]
G[u'tone_fam_docs'] = [[G[u'tone_wide'][i][k] for i in range(NSRC)] for k in range(5)]
G[u'code_def_fams'] = [len(x) for x in G[u'code_defined_lbl']]
G[u'code_set_same_2616_9110'] = 1 if G[u'code_defined_lbl'][0] == G[u'code_defined_lbl'][4] else 0
G[u'code_7231_drops'] = [c for c in G[u'code_absent_lbl'][1] if c in G[u'code_defined_lbl'][0]]
G[u'code_7231_drops_n'] = len(G[u'code_7231_drops'])
G[u'std_n'] = len([x for x in G[u'std_line'] if x])
G[u'sec_end_head_rows'] = [len([1 for _, x in ALN[i] if G[u'sec_end_head'][i]
                                and p5(G[u'sec_end_head'][i]) == p5(x)]) for i in range(NSRC)]
G[u'pp_shell_nonblank'] = [G[u'shell_lines'][i] - G[u'blank'][i] for i in range(NSRC)]
G[u'pp_gap_close'] = sum(abs(G[u'pp_gap_rows'][i] - G[u'pp_shell_nonblank'][i])
                         for i in range(NSRC))

# ---------- 共用行归属分档(本遍直接读 B 段建好的归属向量 PRES, 第二遍是逐枚重扫池) ----------
def byte_shared(a, b):
    return [k for k in ORIG[a] if k in ORIG[b] and (ORIG[a][k] & ORIG[b][k])]


SB = dict((pr, byte_shared(pr[0], pr[1])) for pr in PAIRS)
G[u'pair_byte_tier'] = dict((u'%s-%s' % (LBL[a], LBL[b]),
                             [len([k for k in SB[(a, b)] if len(PRES[k]) == m])
                              for m in range(1, NSRC + 1)]) for a, b in PAIRS)
G[u'pb_7231_9110'] = len(SB[(1, 4)])
G[u'pb_8470_9110'] = len(SB[(3, 4)])
G[u'pb_2616_9110'] = len(SB[(0, 4)])
G[u'pb_2616_7231'] = len(SB[(0, 1)])
G[u'only2_7231_9110'] = G[u'pair_byte_tier'][u'7231-9110'][1]
G[u'only2_8470_9110'] = G[u'pair_byte_tier'][u'8470-9110'][1]
G[u'multi_8470_9110'] = sum(G[u'pair_byte_tier'][u'8470-9110'][2:])
G[u'pair_min'] = min(G[u'pair_shared'].values())
G[u'pair_min_lbl'] = [k for k, v in G[u'pair_shared'].items() if v == G[u'pair_min']][0]

# ---------- 聚合量 ----------
G[u'sec_hit_tot'] = sum(G[u'sec_hit_n'])
G[u'auto_gain_tot'] = sum(G[u'auto_gain'])
G[u'auto_fam_overlap_other4'] = sum(G[u'auto_fam_overlap']) - G[u'auto_fam_overlap'][4]
G[u'reword_make_tot'] = sum(x[6] for x in G[u'reword'])
G[u'reword_own_tot'] = sum(len(x) for x in G[u'reword_own'])
G[u'idem_str_6585_8470'] = G[u'idem_str'][2] + G[u'idem_str'][3]
G[u'tone_straddle_6585_8470'] = G[u'tone_straddle'][2] + G[u'tone_straddle'][3]
G[u'num_own_tot'] = sum(len(x) for x in G[u'num_own'])
G[u'paren_2616_7231_9110'] = sum(G[u'paren'][0]) + sum(G[u'paren'][1]) + sum(G[u'paren'][4])
G[u'neg_false_sub_tot'] = sum(G[u'neg_false_sub'])
G[u'subj_active_7231_6585'] = G[u'subj_active'][1] + G[u'subj_active'][2]
G[u'meth_post_sec_other4'] = sum(G[u'meth_post_sec'][:4])
G[u'subj_straddle_tot'] = sum(G[u'subj_straddle'])
G[u'ans_span_tot'] = sum(G[u'ans_span'])
G[u'pair_row_per_sent'] = G[u'pair_7231_9110'] // G[u's_pair_7231_9110']
G[u's_ruler_drop_7231_9110'] = G[u'pair_7231_9110'] - G[u's_pair_7231_9110']

# ---------- 布尔门(段落层): 与第二遍同定义, 读本遍读数 ----------
C2 = {}
C2[u'pin_rt_all'] = 1 if G['pin_rt_ok'] == G['pin_rt_n'] else 0
C2[u'pin_wrap_probe'] = 1 if G['pin_wrongline'] == 0 else 0
C2[u'idem_blk_verbatim'] = 1 if (G['idem_blk_same'] and G['like_blk_same']) else 0
C2[u'idem_gap_equal'] = 1 if G['blk_gap_delta'] == 0 else 0
C2[u'one_line_answer_only_9110'] = 1 if (G['blk_one_line_n'] == 1 and G['blk_is_one_line'][4]) else 0
C2[u'tone_in_blk_6585_8470'] = 1 if (G['tone_in_blk'][11] == 0 and G['tone_mustnot_blk'][11] == 0) else 0
C2[u'blk_tone_2616_rich'] = 1 if (G['tone_in_blk'][0] >= 2 and G['tone_may_blk'][0] >= 1) else 0
C2[u'verdict_above_head_2616'] = G['verdict_above_head_2616']
C2[u'proxy_inside_head_9110'] = G['proxy_inside_head_9110']
C2[u'might_straddle_one'] = 1 if G['might_straddle'] == 1 else 0
C2[u'w_ledger_close'] = 0 if G['w_ledger_idem'] else 1
C2[u'code_7231_drops_two'] = 1 if G['code_7231_drops_n'] == 2 else 0
C2[u'code_set_2616_eq_9110'] = G['code_set_same_2616_9110']
C2[u'only2_dominates_max'] = 1 if G['only2_7231_9110'] * 2 > G['pb_7231_9110'] else 0
C2[u'pp_gap_is_shell_nonblank'] = 1 if G[u'pp_gap_close'] == 0 and sum(G[u'pp_gap_rows']) > 0 else 0
C2[u'only_9110_straddle'] = 1 if G['subj_straddle_tot'] == G['subj_straddle'][4] else 0
C2[u'paren_only_8470'] = 1 if G[u'paren_2616_7231_9110'] == 0 else 0
for k in C2:
    G[k] = 1 if C2[k] else 0

# ---------- 与采集侧逐键对账(键名表从 _mkB80.py 的 PK 字面串里摘, 不重打) ----------
PKL = None
for _st in ast.parse(MS).body:
    if (isinstance(_st, ast.Assign) and isinstance(_st.targets[0], ast.Name)
            and _st.targets[0].id == u'PK'):
        _nd = _st.value.func.value
        while isinstance(_nd, ast.Call):
            _nd = _nd.func.value
        PKL = _nd.value.split()
assert PKL is not None and len(PKL) == 167, len(PKL or [])
AGREE, DIFF = [], []
for k in PKL:
    if k not in G or k not in MEA:
        DIFF.append((k, u'缺键', u'缺键'))
        continue
    (AGREE if G[k] == MEA[k] else DIFF).append((k, G[k], MEA[k]))
G['ff_only_vs_pick_lines'] = 1 if G['ff_only'] == MEA[u'ff_only_lines'] else 0
G['sh_gap_vs_pick'] = 1 if G['sh_char_gap'] == MEA[u'sh_minus_fold'] else 0
G['hdr_tight_vs_pick'] = 1 if G['hdr_lines_tight'] == MEA[u'hdr_lines'] else 0
G['hdr_indent_minus_tight'] = [G['hdr_lines_indent'][i] - G['hdr_lines_tight'][i]
                               for i in range(NSRC)]
G['pair_byte_lines_vs_pick'] = 1 if G['pair_max_byte_lines'] == MEA[u'pair_max_byte'] else 0
G['pair_norm_lines_vs_pick'] = 1 if G['pair_max_norm_only_lines'] == MEA[u'pair_max_norm_only'] else 0
G['ans_vs_pick'] = [1 if MEA[u'ans'][i].rstrip() == G[u'ans'][i] else 0 for i in range(NSRC)]
G['ans_tail_ws'] = [len(MEA[u'ans'][i]) - len(G[u'ans'][i]) for i in range(NSRC)]
G['pick_agree'] = len(AGREE)
G['pick_diff'] = len(DIFF)
for k, a, b in DIFF:
    print(u'  采集⇎复测不符: %s %s vs %s' % (k, a, b))
assert G['pick_diff'] == 0, DIFF[:3]
assert G['pick_agree'] == FLAT[u'pick_agree'] == 167

# ---------- 编码区锚账: 手写配对扫描 ⇎ 双轨归属 ----------
TT = io.open(ENTRY, encoding='utf-8').read()
_i0 = TT.index(u'## ⟪BabelTele⟫')
ENC = TT[TT.index(NL, _i0) + 1:TT.index(u'## ⛓解读注')]
ENC = ENC.rstrip(NL)


def my_cites(s):
    out, i = [], 0
    while True:
        a = s.find(u'⟦', i)
        if a < 0:
            return out
        b = s.find(u'⟧', a)
        c = s.find(u'⟨', b) if b >= 0 else -1
        d = s.find(u'⟩', c) if c >= 0 else -1
        if b < 0 or d < 0 or c != b + 1:
            raise AssertionError(u'锚壳不成对 @%d' % a)
        out.append((s[a + 1:b], s[c + 1:d]))
        i = d + 1


CITES = my_cites(ENC)
RE_PAIR = re.findall(u'⟦(' + u'|'.join(TAGS) + u')⟧⟨([^⟨⟩]+)⟩', ENC)
assert CITES == [(x, y) for x, y in RE_PAIR], (len(CITES), len(RE_PAIR))
USED = len([c for c in ENC if c == u'⟨'])
ANCHS = []
for _, a in CITES:
    if a not in ANCHS:
        ANCHS.append(a)
DIST = len(ANCHS)
TAGN = dict((t, len([x for x in CITES if x[0] == t])) for t in TAGS)
ERR = [x for x in CITES if p5(x[1]) not in FAN[IDX[x[0]]]]
MISSLINE = [x for x in CITES if x[1] not in ANSET[IDX[x[0]]]]
assert not ERR, ERR[:2]
assert not MISSLINE, MISSLINE[:2]
HITC = dict((a, tuple(i for i in range(NSRC) if p5(a) in FAN[i])) for a in ANCHS)
G['anchor_total'] = USED
G['anchor_distinct'] = DIST
G['anchor_err'] = len(ERR)
G['anchor_single'] = len([a for a in ANCHS if len(HITC[a]) == 1])
G['anchor_cross'] = len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC])
G['anchor_all5'] = len([a for a in ANCHS if len(HITC[a]) == NSRC])
G['checks'] = DIST * NSRC
G['enc_chars'] = len([c for c in ENC if c != NL])
G['nsrc'] = NSRC
for t in TAGS:
    G['tag_' + t] = TAGN[t]
assert G['anchor_single'] + G['anchor_cross'] + G['anchor_all5'] == DIST
# 锚的行号⇎候选行数逐枚回读: 42 枚锚的记录来自第二遍的 ALOG, 本遍用行号尺重新认一遍
ALC = Counter([x[0] for x in CH[u'anchor_lines']])
assert sum(ALC.values()) == G['anchor_total'] == len(CH[u'anchor_lines'])
_back = 0
for lbl, nd, ln, nh in CH[u'anchor_lines']:
    i = IDX[lbl]
    if ln == 0:
        continue
    assert p5(nd).replace(u'\\u2028', u'') in p5(ALND[i][ln]) or p5(ALND[i][ln]).startswith(p5(nd)), (lbl, nd, ln)
    _back += 1
G['amb_n'] = len([x for x in CH[u'anchor_lines'] if x[3] > 1])
assert G['amb_n'] == CH[u'anchor_ambiguous'] == 2
for _k in (u'amb_n',):
    del G[_k]
print(u'第三段完成: 段窗 %d 枚锚复核 %d ⇎ 采集对账 %d/%d ⇎ 编码区 %d 字符 ⇎ 锚 %d 处/去重 %d 串' % (
    len(PINS), _back, G['pick_agree'], len(PKL), G['enc_chars'], G['anchor_total'], DIST))
