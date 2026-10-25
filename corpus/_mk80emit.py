# -*- coding: utf-8 -*-
"""B80 建条目第二遍的发射段: 由 _mkB80.py 在顶层 exec 进来, 与前半共享同一批现读量。
段一 SCAN2 是段落层、行号尺与转置尺(同一段也由 corpus/_wire80.py 机械切进 audit.py::_b80_scan);
段二是编码区正文, 每一枚三位以上的数都由 V()/J()/EXPR() 注册过算式, 锚一律由面上位置导出;
段三自 replay 恒等式、复核锚归属、落盘 flat/deriv/atoms/checks 与条目文件。"""

# --- SCAN2 BEGIN --- (并键段: 同一段也机械切进 audit.py::_b80_scan)
TAGS = LBL
IDX = dict((t, n) for n, t in enumerate(LBL))
# 门槛对面(audit.py::_atom_face): 纯文本条目不剥壳, 整份原文归一后就是比对面
FAN = [pnorm(t) for t in T]
ATOMFAIL = []
# 写正文时的试针开关: 设环境变量 B80PROBE=1 让落空的锚返回标记而不是立刻中断, 一轮把全部缺针看光
PROBE = (u'B80PROBE' in __import__('os').environ)

SHPN = [[(n, x) for n, x in enumerate(L[i], 1) if not is_shell_pick(x)] for i in range(NSRC)]
for i in range(NSRC):
    assert [x for _, x in SHPN[i]] == SHP[i], i
# 窗平面: 与 WIDE 逐字同果的 (行号, 折平片段) 序列——WIDE 正是这些片段以单空格粘起来的
PP = [[(n, u' '.join(x.split())) for n, x in SHPN[i]] for i in range(NSRC)]
PP = [[p for p in pp if p[1] != u''] for pp in PP]
for i in range(NSRC):
    assert u' '.join(x for _, x in PP[i]) == WIDE[i], i
F['pp_rows'] = [len(PP[i]) for i in range(NSRC)]
F['pp_gap_rows'] = [F['nonblank'][i] - F['pp_rows'][i] for i in range(NSRC)]


def fmap(i):
    mp, off, first = [], 0, True
    for ln, s in PP[i]:
        if not first:
            off += 1
        first = False
        mp.append((off, ln))
        off += len(s)
    return mp


FMP = [fmap(i) for i in range(NSRC)]


def line_of(i, a):
    r = 0
    for o, n in FMP[i]:
        if o <= a:
            r = n
        else:
            break
    return r


ALN = [SHPN[i] for i in range(NSRC)]
ANSET = [set(x for _, x in ALN[i]) for i in range(NSRC)]


ALOG = []


def _anline(i, nd, exact, lo=0):
    """锚由面上位置导出: 匹配行按原行号登记, 首处即答案行; 命中多行时逐行数一并记账, 供正文核对“锚到底落在哪一行”"""
    hits = []
    for ln, x in ALN[i]:
        if ln < lo:
            continue
        p = pnorm(x)
        ok = (p == pnorm(nd[0])) if exact else all(pnorm(w) in p for w in nd)
        if ok:
            hits.append((ln, x, p))
    if not hits:
        ATOMFAIL.append((LBL[i], nd))
        if PROBE:
            ALOG.append((LBL[i], nd[0][:34], 0, 0))
            return u'⟦%s⟧⟨MISS:%s⟩' % (LBL[i], nd[0][:28])
        raise AssertionError(u'锚导出失败 %s %s' % (LBL[i], nd))
    ln, x, p = hits[0]
    assert p in FAN[i], (LBL[i], x[:60])
    ALOG.append((LBL[i], nd[0][:34], ln, len(hits)))
    return u'⟦%s⟧⟨%s⟩' % (LBL[i], x)


def AN(i, *nd):
    return _anline(i, nd, False)


def ANX(i, nd):
    """整行只由这一串组成的行(编号标题行 ⇎ 它的目录行), 拿到目录里的 “…… 51” 就走不通"""
    return _anline(i, (nd,), True)


def ANL(i, lo, *nd):
    """同一串在目录与正文各印一次时只取不早于 lo 的那一枚: 节尾定界用的是正文标题行, 不是目录行"""
    return _anline(i, nd, False, lo)


BLKFAIL = []


def blk(i, start, end):
    a = WIDE[i].find(start)
    if a < 0:
        BLKFAIL.append((LBL[i], start, u'起'))
        if not PROBE:
            raise AssertionError(u'段起针落空 %s %s' % (LBL[i], start))
        return u' ', 0, 0
    b = WIDE[i].find(end, a)
    if b < 0:
        BLKFAIL.append((LBL[i], end, u'止'))
        if not PROBE:
            raise AssertionError(u'段止针落空 %s %s' % (LBL[i], end))
        return u' ', line_of(i, a), line_of(i, a)
    e = b + len(end)
    return u' '.join(WIDE[i][a:e].split()), line_of(i, a), line_of(i, e - 1)


def ln_of(i, nd, frm=0):
    a = WIDE[i].find(nd, frm)
    if a < 0:
        raise AssertionError(u'窗针落空 %s %s' % (LBL[i], nd))
    return a, line_of(i, a)


def ln_end(i, nd, frm=0):
    """短语落在哪一行要看它结束在哪一行: 72 列硬换行会把 “non-idempotent requests” 切成两行"""
    a = WIDE[i].find(nd, frm)
    if a < 0:
        raise AssertionError(u'窗针落空 %s %s' % (LBL[i], nd))
    return a, line_of(i, a + len(nd) - 1)


def line_holds(i, ln, nd):
    """行号尺复核: 拿行号回原文件取那一行, 看针是否真落在这一行内"""
    for n, x in ALN[i]:
        if n == ln:
            return 1 if pnorm(nd) in pnorm(x) else 0
    raise AssertionError(u'行号无对应原行 %s %d' % (LBL[i], ln))


# 段界全部由字面针导出: 前 5 段是五份的主答句, 后 9 段是搬字对、定义段、自否认段
PINS = [(0, u'Non-idempotent methods or sequences', u'the request(s).'),
        (1, u'Idempotent methods are distinguished because', u"server's response."),
        (2, u'The 429 status code indicates', u'rate limiting").'),
        (3, u'User agents that send a request in early data are expected', u'response status code.'),
        (4, u'A proxy MUST NOT automatically retry non-idempotent requests.', u'non-idempotent requests.'),
        (1, u'Like the definition of safe', u'each idempotent request.'),
        (4, u'Like the definition of safe', u'each idempotent request.'),
        (0, u'Methods can also have the property of', u'share this property.'),
        (4, u'Idempotent methods are distinguished because', u"server's response."),
        (4, u'Some clients take a riskier approach', u'automatic retry is possible.'),
        (3, u'The server cannot assume that a client is able to retry',
         u'one of these conditions is met.'),
        (2, u'Note that this specification does not define', u'stateful cookie.'),
        (0, u'The automatic retry SHOULD NOT be repeated', u'of requests fails.'),
        (4, u'a user agent can repeat a POST request automatically', u'safe for that resource.')]
PB = [blk(i, s, e) for i, s, e in PINS]
PTXT = [p[0] for p in PB]
F['blk_lo'] = [p[1] for p in PB]
F['blk_hi'] = [p[2] for p in PB]
F['blk_rows'] = [p[2] - p[1] + 1 for p in PB]
F['blk_chars'] = [len(p[0]) for p in PB]
F['blk_words'] = [len(p[0].split()) for p in PB]
PW = [p[0].lower().split() for p in PB]
F['blk_vocab'] = [len(set(x)) for x in PW]
F['blk_five_chars'] = sum(F['blk_chars'][:5])
F['blk_five_words'] = sum(F['blk_words'][:5])
F['blk_rows_tot'] = sum(F['blk_rows'])
F['blk_words_tot'] = sum(F['blk_words'])
F['blk_five_rows'] = sum(F['blk_rows'][:5])
F['tone_must_blk'] = [ub(p, u'MUST') for p in PTXT]
F['tone_may_blk'] = [ub(p, u'MAY') for p in PTXT]
F['tone_should_blk'] = [ub(p, u'SHOULD') for p in PTXT]
F['tone_mustnot_blk'] = [ub(p, u'MUST NOT') for p in PTXT]
F['tone_in_blk'] = [F['tone_must_blk'][n] + F['tone_may_blk'][n] + F['tone_should_blk'][n]
                    for n in range(len(PB))]
F['blk_must_cur'] = [cnt_cur(p, u'MUST') for p in PTXT]
F['blk_must_re'] = [len(re.findall(u'MUST', p)) for p in PTXT]
F['blk_tone_ruler_close'] = (sum(abs(F['tone_must_blk'][n] - F['blk_must_cur'][n]) for n in range(len(PB)))
                             + sum(abs(F['tone_must_blk'][n] - F['blk_must_re'][n]) for n in range(len(PB))))


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


# 7231 ⇎ 9110 的三对搬字段: 逐字同形则头尾共用词=整段词数
F['pre_idem_7231_9110'] = head_words(PW[1], PW[8])
F['suf_idem_7231_9110'] = suffix_words(PW[1], PW[8])
F['pre_like_7231_9110'] = head_words(PW[5], PW[6])
F['suf_like_7231_9110'] = suffix_words(PW[5], PW[6])
F['idem_blk_same'] = 1 if PTXT[1] == PTXT[8] else 0
F['like_blk_same'] = 1 if PTXT[5] == PTXT[6] else 0
F['w_common_idem'] = len(set(PW[1]) & set(PW[8]))
F['w_only_9110_idem'] = len(set(PW[8]) - set(PW[1]))
F['w_only_7231_idem'] = len(set(PW[1]) - set(PW[8]))
F['w_ledger_idem'] = (F['w_only_9110_idem'] + F['w_common_idem'] - F['blk_vocab'][8]
                      + F['w_only_7231_idem'] + F['w_common_idem'] - F['blk_vocab'][1])
F['idem_blk_row_gap'] = F['blk_lo'][8] - F['blk_lo'][1]
F['like_blk_row_gap'] = F['blk_lo'][6] - F['blk_lo'][5]
F['blk_gap_delta'] = F['idem_blk_row_gap'] - F['like_blk_row_gap']
# 主答句五段的“说多少词 ⇎ 占多少行”: 9110 一句 8 词独占一行, 2616 三句摊到多行
F['blk_words_per_row'] = [F['blk_words'][n] // F['blk_rows'][n] for n in range(5)]
F['blk_is_one_line'] = [1 if F['blk_rows'][n] == 1 else 0 for n in range(5)]
F['blk_one_line_n'] = sum(F['blk_is_one_line'])
# 行号尺: 段首行 ⇎ 独立行针, 再拿被 72 列切开短语的首末行做反向对照
F['ln_verdict_2616'] = ln_of(0, u'Non-idempotent methods or sequences MUST NOT')[1]
F['ln_confirm_end_2616'] = ln_end(0, u'user confirmation.')[1]
F['ln_idem_7231'] = ln_of(1, u'Idempotent methods are distinguished because')[1]
F['ln_idem_9110'] = ln_of(4, u'Idempotent methods are distinguished because')[1]
F['ln_proxy_9110'] = ln_of(4, u'A proxy MUST NOT automatically retry')[1]
F['ln_proxy_head_9110'] = ln_of(4, u'A proxy MUST NOT')[1]
F['ln_client_head_9110'] = ln_of(4, u'A client SHOULD NOT automatically retry')[1]
F['ln_client_9110'] = ln_end(4, u'client SHOULD NOT automatically retry a failed automatic retry.')[1]
F['ln_might_head_9110'] = ln_of(4, u'a client might automatically retry a POST')
F['ln_might_end_9110'] = ln_end(4, u'a client might automatically retry a POST')
F['might_straddle'] = F['ln_might_end_9110'][1] - F['ln_might_head_9110'][1]
F['ln_might_full_end_9110'] = ln_end(4, u'persistent connection was used.')
F['ln_riskier_9110'] = ln_of(4, u'Some clients take a riskier approach')[1]
F['ln_selfdeny_6585'] = ln_of(2, u'Note that this specification does not define')[1]
F['ln_429_6585'] = ln_of(2, u'The 429 status code indicates')[1]
F['ln_425_8470'] = ln_of(3, u'User agents that send a request in early data')[1]
F['ln_assume_8470'] = ln_of(3, u'The server cannot assume that a client is able')[1]
F['sec_head_line_2616'] = F['sec_body_line'][0]
F['sec_head_line_9110'] = F['sec_body_line'][4]
F['verdict_above_head_2616'] = 1 if F['ln_verdict_2616'] < F['sec_head_line_2616'] else 0
F['proxy_inside_head_9110'] = 1 if F['ln_proxy_9110'] > F['sec_head_line_9110'] else 0
RT = [(0, F['ln_verdict_2616'], u'Non-idempotent methods or sequences'),
      (0, F['ln_confirm_end_2616'], u'user confirmation.'),
      (1, F['ln_idem_7231'], u'Idempotent methods are distinguished'),
      (4, F['ln_idem_9110'], u'Idempotent methods are distinguished'),
      (4, F['ln_proxy_9110'], u'A proxy MUST NOT automatically retry'),
      (4, F['ln_client_9110'], u'client SHOULD NOT automatically retry a failed automatic retry.'),
      (4, F['ln_might_end_9110'][1], u'automatically retry a POST request'),
      (4, F['ln_might_full_end_9110'][1], u'persistent connection was used.'),
      (2, F['ln_429_6585'], u'The 429 status code indicates'),
      (2, F['ln_selfdeny_6585'], u'Note that this specification does not define'),
      (3, F['ln_425_8470'], u'User agents that send a request in early data'),
      (3, F['ln_assume_8470'], u'The server cannot assume that a client is able'),
      (4, F['ln_riskier_9110'], u'Some clients take a riskier approach')]
F['pin_rt'] = [line_holds(i, ln, nd) for i, ln, nd in RT]
F['pin_rt_n'] = len(F['pin_rt'])
F['pin_rt_ok'] = sum(F['pin_rt'])
F['pin_rt_src'] = [len([1 for i, _, _ in RT if i == n]) for n in range(NSRC)]
# 反向对照: 把被切开的短语整串拿到“首字那一行”去验, 行号尺应当认不出(它确实分得清首末)
F['pin_wrongline'] = sum([line_holds(4, F['ln_might_head_9110'][1], TEXT[u'a9110_might']),
                          line_holds(4, F['ln_client_head_9110'],
                                     u'A client SHOULD NOT automatically retry a failed automatic retry.')])
CLOSE2 = {}
CLOSE2[u'pin_rt_all'] = 1 if F['pin_rt_ok'] == F['pin_rt_n'] else 0
CLOSE2[u'pin_wrap_probe'] = 1 if F['pin_wrongline'] == 0 else 0
CLOSE2[u'idem_blk_verbatim'] = 1 if (F['idem_blk_same'] and F['like_blk_same']) else 0
CLOSE2[u'idem_gap_equal'] = 1 if F['blk_gap_delta'] == 0 else 0
CLOSE2[u'one_line_answer_only_9110'] = 1 if (F['blk_one_line_n'] == 1 and F['blk_is_one_line'][4]) else 0
CLOSE2[u'tone_in_blk_6585_8470'] = 1 if (F['tone_in_blk'][11] == 0 and F['tone_mustnot_blk'][11] == 0) else 0
CLOSE2[u'blk_tone_2616_rich'] = 1 if (F['tone_in_blk'][0] >= 2 and F['tone_may_blk'][0] >= 1) else 0
CLOSE2[u'verdict_above_head_2616'] = F['verdict_above_head_2616']
CLOSE2[u'proxy_inside_head_9110'] = F['proxy_inside_head_9110']
CLOSE2[u'might_straddle_one'] = 1 if F['might_straddle'] == 1 else 0
CLOSE2[u'w_ledger_close'] = 0 if F['w_ledger_idem'] else 1
F.update(CLOSE2)

# ---------- 转置尺: 矩阵量按族横过来逐份读, 免得正文里印整行矩阵 ----------
F[u'num_dsec_docs'] = [F[u'num'][i][5] for i in range(NSRC)]
F[u'num_delay_docs'] = [F[u'num'][i][4] for i in range(NSRC)]
F[u'num_httpdate_docs'] = [F[u'num'][i][6] for i in range(NSRC)]
F[u'num_3600_docs'] = [F[u'num'][i][0] for i in range(NSRC)]
F[u'num_120_docs'] = [F[u'num'][i][1] for i in range(NSRC)]
F[u'tone_fam_docs'] = [[F[u'tone_wide'][i][k] for i in range(NSRC)] for k in range(5)]
F[u'code_def_fams'] = [len(x) for x in F[u'code_defined_lbl']]
F[u'code_set_same_2616_9110'] = 1 if F[u'code_defined_lbl'][0] == F[u'code_defined_lbl'][4] else 0
F[u'code_7231_drops'] = [c for c in F[u'code_absent_lbl'][1] if c in F[u'code_defined_lbl'][0]]
F[u'code_7231_drops_n'] = len(F[u'code_7231_drops'])
F[u'std_n'] = len([x for x in F[u'std_line'] if x])
# 节尾那行标题在面上印几行(新版式的目录与正文同形, 旧版式的目录带点引线故不同形)
F[u'sec_end_head_rows'] = [len([1 for _, x in ALN[i]
                                if F[u'sec_end_head'][i] and pnorm(F[u'sec_end_head'][i]) == pnorm(x)])
                           for i in range(NSRC)]
# 摘壳折平的片段序列 ⇎ 非空行: 差的不是零, 差的正是被摘掉的“非空壳行”(页眉那一类)
F[u'pp_shell_nonblank'] = [F[u'shell_lines'][i] - F[u'blank'][i] for i in range(NSRC)]
F[u'pp_gap_close'] = sum(abs(F[u'pp_gap_rows'][i] - F[u'pp_shell_nonblank'][i]) for i in range(NSRC))
CLOSE2[u'pp_gap_is_shell_nonblank'] = 1 if F[u'pp_gap_close'] == 0 and sum(F[u'pp_gap_rows']) > 0 else 0
ZV.append((u"B80V('pp_gap_close')",
           u'片段序列比非空行少的行数 = 非空壳行枚数: 摘壳丢下的每一行都记在页壳上, 逐份相消'))
ZV.append((u"sum(B80V('pp_rows')) + sum(B80V('shell_lines')) - sum(B80V('lines'))",
           u'片段序列行数加壳行数等于原行数(空行全归壳, 无一行两头都不算)'))
# ---------- 共用行的“归属分档”: 一对共用的行里, 有几枚只属于这一对 ⇎ 有几枚是更多份共用的模板行 ----------
def byte_shared(a, b):
    return [k for k in ORIG[a] if k in ORIG[b] and (ORIG[a][k] & ORIG[b][k])]


def pres_n(k):
    return len([1 for i in range(NSRC) if k in set(POOL[i])])


SB = dict((pr, byte_shared(pr[0], pr[1])) for pr in PAIRS)
F[u'pair_byte_tier'] = dict((u'%s-%s' % (LBL[a], LBL[b]),
                             [len([k for k in SB[(a, b)] if pres_n(k) == m]) for m in range(1, NSRC + 1)])
                            for a, b in PAIRS)
F[u'pb_7231_9110'] = len(SB[(1, 4)])
F[u'pb_8470_9110'] = len(SB[(3, 4)])
F[u'pb_2616_9110'] = len(SB[(0, 4)])
F[u'pb_2616_7231'] = len(SB[(0, 1)])
F[u'only2_7231_9110'] = F[u'pair_byte_tier'][u'7231-9110'][1]
F[u'only2_8470_9110'] = F[u'pair_byte_tier'][u'8470-9110'][1]
F[u'multi_8470_9110'] = sum(F[u'pair_byte_tier'][u'8470-9110'][2:])
F[u'pair_min'] = min(F[u'pair_shared'].values())
F[u'pair_min_lbl'] = [k for k, v in F[u'pair_shared'].items() if v == F[u'pair_min']][0]
CLOSE2[u'code_7231_drops_two'] = 1 if F[u'code_7231_drops_n'] == 2 else 0
CLOSE2[u'code_set_2616_eq_9110'] = F[u'code_set_same_2616_9110']
CLOSE2[u'only2_dominates_max'] = 1 if F[u'only2_7231_9110'] * 2 > F[u'pb_7231_9110'] else 0
F.update(CLOSE2)
ZV.append((u"B80V('pb_7231_9110') + B80V('pair_norm_only')[6] - B80V('pair_max')",
           u'字节同形加“只归一同形”=这一对的共用枚数(最大对)'))
ZV.append((u"B80V('only2_7231_9110') + sum(B80V('pair_byte_tier')['7231-9110'][2:]) - B80V('pb_7231_9110')",
           u'共用行按“另有几份也印了它”分档: 只属这一对的⇎三份以上共用的, 相加=字节同形枚数'))
ZV.append((u"B80V('only2_8470_9110') + B80V('multi_8470_9110') - B80V('pb_8470_9110')",
           u'同一分档在 8470·9110 一对上也账平'))
ZV.append((u"B80V('code_def_fams')[0] - B80V('code_def_fams')[4]",
           u'2616 与 9110 定义的状态码族数同值(现行文档把 1999 那份的核心码整套重定义了一遍)'))
ZV.append((u"B80V('code_7231_drops_n') - 2",
           u'7231 相比 2616 少定义两枚码(401 与 416 搬去别的分册)'))
ZV.append((u"B80V('std_n') - 1", u'全库只有 9110 印着 STD 行'))
ZV.append((u"B80V('sec_end_head_rows')[4] - B80V('sec_row_dup')[4] - 1",
           u'节尾标题在 9110 面上印两行(目录⇎正文)——与它的目录命中同源: 都是新版式目录与正文同形'))
ZV.append((u"sum(B80V('sec_end_head_rows')[:2]) - 2",
           u'2616 与 7231 的节尾标题各只印一行: 它们的目录行带点引线, 与标题不同形'))

# ---------- 正文里要印的聚合量: 先把“合计”做成有名字的键, 再让正文一根针读一枚量 ----------
F[u'sec_hit_tot'] = sum(F[u'sec_hit_n'])
F[u'auto_gain_tot'] = sum(F[u'auto_gain'])
F[u'auto_fam_overlap_other4'] = sum(F[u'auto_fam_overlap']) - F[u'auto_fam_overlap'][4]
F[u'reword_make_tot'] = sum(x[6] for x in F[u'reword'])
F[u'reword_own_tot'] = sum(len(x) for x in F[u'reword_own'])
F[u'idem_str_6585_8470'] = F[u'idem_str'][2] + F[u'idem_str'][3]
F[u'tone_straddle_6585_8470'] = F[u'tone_straddle'][2] + F[u'tone_straddle'][3]
F[u'num_own_tot'] = sum(len(x) for x in F[u'num_own'])
F[u'paren_2616_7231_9110'] = sum(F[u'paren'][0]) + sum(F[u'paren'][1]) + sum(F[u'paren'][4])
F[u'neg_false_sub_tot'] = sum(F[u'neg_false_sub'])
F[u'subj_active_7231_6585'] = F[u'subj_active'][1] + F[u'subj_active'][2]
F[u'meth_post_sec_other4'] = sum(F[u'meth_post_sec'][:4])
F[u'subj_straddle_tot'] = sum(F[u'subj_straddle'])
F[u'ans_span_tot'] = sum(F[u'ans_span'])
F[u'pair_row_per_sent'] = F[u'pair_7231_9110'] // F[u's_pair_7231_9110']
F[u's_ruler_drop_7231_9110'] = F[u'pair_7231_9110'] - F[u's_pair_7231_9110']
CLOSE2[u'only_9110_straddle'] = 1 if F[u'subj_straddle_tot'] == F[u'subj_straddle'][4] else 0
CLOSE2[u'paren_only_8470'] = 1 if F[u'paren_2616_7231_9110'] == 0 else 0
F.update(CLOSE2)
ZV.append((u"B80V('sec_hit_tot') - (B80V('sec_found_n') + 1)",
           u'同名标题命中合计=有节的份数+恰一行目录'))
ZV.append((u"B80V('blk_five_rows') - B80V('ans_span_tot')",
           u'五段主答句行幅合计 ⇎ 答句跨行账合计: 两条独立导出同值'))

# --- SCAN2 END ---

# ---------- ZV 追加: 段落层的恒等式 ----------
ZV.append((u"B80V('pin_rt_ok') - B80V('pin_rt_n')",
           u'行号尺复核: 段窗首末行⇎独立行针报出的行号, 逐枚回原文件那一行自验'))
ZV.append((u"B80V('pin_wrongline')",
           u'反向对照: 被 72 列切开的短语整串拿到首字那一行去验, 行号尺应当认不出'))
ZV.append((u"B80V('might_straddle') - 1",
           u'9110 的 “a client might automatically retry …” 被换行切在中间: 首字行⇎末字行差一行'))
ZV.append((u"B80V('idem_blk_same') + B80V('like_blk_same') - 2",
           u'7231 ⇎ 9110 的两段搬字逐字同形: 整段折平后一个词都不差'))
ZV.append((u"B80V('blk_gap_delta')",
           u'两段搬字的行距位移相等(整节按同一距离平移)'))
ZW = u"B80V('w_ledger_idem')"
ZV.append((ZW, u'词集容斥: 只 9110 有 + 只 7231 有 + 两份共用, 逐段回各自词表枚数'))
ZV.append((u"B80V('w_common_idem') + B80V('w_only_9110_idem') - B80V('blk_vocab', 8)",
           u'共用词加独有词等于本段词表: 9110 一侧'))
ZV.append((u"B80V('w_common_idem') + B80V('w_only_7231_idem') - B80V('blk_vocab', 1)",
           u'共用词加独有词等于本段词表: 7231 一侧'))
ZV.append((u"B80V('blk_tone_ruler_close')",
           u'段内义务词三轨(邻居手扫 ⇎ 游标 find ⇎ 正则)逐段相等'))
ZV.append((u"sum(B80V('tone_mustnot_blk')[n] for n in (1, 8))",
           u'两份的幂等定义段一枚 MUST NOT 也不给(禁令在别处)'),)
ZV.append((u"B80V('blk_one_line_n') - 1",
           u'五份主答句里恰一句能在一行内读全(9110)'))
ZV.append((u"B80V('blk_five_rows') - sum(B80V('ans_span')[:5])",
           u'五段主答句的行幅合计 ⇎ 答句跨行账: 两条独立导出同值'))

PAIRLBL = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in IT.combinations(range(NSRC), 2)]
PLBL = [u'%s#%d' % (LBL[i], n + 1) for n, (i, s, e) in enumerate(PINS)]


def PJ(name, note=u''):
    return u' ⇎ '.join(V(name, n, u'%s·%s' % (note or name, PLBL[n])) for n in range(len(PINS)))


def NKL(keys):
    return u' '.join(k[1:] if k[:1] in (u'a', u'n') else k for k in keys)


LINES = []
if PROBE:
    # 探针模式下把三根读数针改成软的: 一轮把正文里全部缺针/错单位读数看光, 而不是撞第一个就停
    BADREAD = []
    _V0, _J0, _JL0 = V, J, JL

    def V(name, i=None, note=u''):
        try:
            return _V0(name, i, note)
        except Exception as e:
            BADREAD.append((u'V', name, i, repr(e)[:70]))
            return u'?'

    def J(name, note=u''):
        try:
            return _J0(name, note)
        except Exception as e:
            BADREAD.append((u'J', name, None, repr(e)[:70]))
            return u'?'

    def JL(name, note=u''):
        try:
            return _JL0(name, note)
        except Exception as e:
            BADREAD.append((u'JL', name, None, repr(e)[:70]))
            return u'?'

LINES.append(
    u'📜 五份先按版式分家: 全是 RFC Editor 的纯文本面(纯文本 ' + V(u'txt_n', None, u'txt份数')
    + u' 份 ⇎ 网页 ' + V(u'html_n', None, u'html份数') + u' 份)。 字节 ' + J(u'bytes', u'字节')
    + u', 面内码位 ' + J(u'chars', u'码位') + u', 原行 ' + J(u'lines', u'原行') + u' ⇎ 非空行 '
    + J(u'nonblank', u'非空行') + u', 最长行 ' + J(u'maxlen', u'最长行') + u' 列——四份同为 '
    + V(u'maxlen', 0, u'最长行·2616') + u' 列硬换行, 只有 7231 溢出到 ' + V(u'maxlen', 1, u'最长行·7231')
    + u' 列(超 ' + V(u'maxlen', 0, u'基线') + u' 列的行 ' + V(u'over72', 1, u'超72行·7231') + u' 行, 判定 '
    + V(u'one_maxlen_outlier', None, u'唯一超长者') + u')。 全库回车 ' + J(u'cr', u'CR') + u' 枚 ⇎ NUL '
    + J(u'nul', u'NUL') + u' 枚; BOM ' + J(u'bom', u'BOM') + u' 枚(只 9110 一份带), 非 ASCII 码位 '
    + J(u'nonascii', u'非ASCII') + u' 枚、字节−码位差 ' + J(u'byte_cp_delta', u'字节减码位')
    + u' 字节, 两处同源于 UTF-8 多字节(判定 ' + V(u'ascii_except_9110', None, u'ASCII其余四份')
    + u'): 30 枚全在贡献者姓名里——' + AN(4, u'Håkon W. Lie') + u'。 换页符 ' + J(u'ff', u'换页')
    + u' 枚 ⇎ [Page] 壳行 ' + J(u'pg_lines', u'页壳行') + u' 行 ⇎ “strip 后只剩换页符”档 '
    + J(u'ff_only', u'换页strip档') + u' 行, 三把尺逐份同枚(判定 ' + V(u'ff_only_vs_pick_lines', None, u'换页档对账')
    + u'); 行内混排的换页 ' + J(u'ff_inline', u'换页行内') + u' 枚 ⇎ 换页减页壳 ' + J(u'ff_minus_pg', u'换页减页壳')
    + u'——一一对应。 9110 是唯一无分页壳的一份(判定 ' + V(u'pageless_9110_only', None, u'无壳只在9110')
    + u'), 于是它的摘壳面与折平面等长(差 ' + V(u'sh_char_gap', 4, u'壳差·9110') + u' 字符, 判定 '
    + V(u'sh_equals_fold_for_9110', None, u'9110摘壳等折平') + u')。 splitlines 行 ' + J(u'lines_split', u'splitlines')
    + u' ⇎ 换行计数 ' + J(u'lines_nl', u'换行档') + u', 差额由换页符与行尾补上(判定 '
    + V(u'lines_split_close', None, u'行数闭合') + u'); 收尾换行 ' + J(u'tail_nl', u'尾换行') + u' 枚。 '
    + u'标签四把尺都只在这一份纯文本里量: 尖括号形 ' + J(u'tag_shape', u'尖括号形') + u' ⇎ 开标签名形 '
    + J(u'tag_open', u'开标签名形') + u' ⇎ 闭标签名形 ' + J(u'tag_close', u'闭标签名形') + u' ⇎ 裸 URL 形 '
    + J(u'tag_url', u'URL形') + u', 余下 ' + J(u'tag_pseudo', u'尖括号伪法') + u' 枚是规范的伪法('
    + AN(0, u'<any CHAR except CTLs or separators>') + u' 这一类)。 6585 的 '
    + V(u'tag_shape', 2, u'尖括号形·6585') + u' 枚被三把尺分完(判定 ' + V(u'tag_shape', 2, u'6585形数')
    + u'⇔' + V(u'tag_close', 2, u'闭名·6585') + u'+' + V(u'tag_open', 2, u'开名·6585') + u'+'
    + V(u'tag_url', 2, u'URL·6585') + u'), 因为它真带了一页示例 HTML: ' + AN(2, u'<p>I only allow 50 requests per hour')
    + u'; 8470 的 ' + V(u'tag_pseudo', 3, u'伪法·8470') + u' 枚一枚没有, 它的 <> 全是裸引用。 全库实体 '
    + J(u'ent_total', u'实体') + u' ⇎ 注释 ' + J(u'comment', u'注释') + u' 枚。 抬头“RFC 数字”顶格行 '
    + J(u'hdr_lines_tight', u'顶格抬头') + u' ⇎ 折平后以 RFC 开头的行 ' + J(u'hdr_lines_indent', u'折平RFC行')
    + u', 差 ' + J(u'hdr_indent_minus_tight', u'折平减顶格') + u' 行——差得最多的是 9110('
    + V(u'hdr_indent_minus_tight', 4, u'折平减顶格·9110') + u' 行), 它一份也没有顶格抬头, 差的全是参考清单里缩进的“RFC 数字⇎DOI”行: '
    + AN(4, u'RFC 793, DOI') + u'。 编号标题三档: 两点式 ' + J(u'hdr_dot2sp', u'标题两点式')
    + u' ⇎ 一点式 ' + J(u'hdr_dot1sp', u'标题一点式') + u' ⇎ 无点式 ' + J(u'hdr_nodot', u'标题无点式')
    + u'——2616 一份就不写尾点(判定 ' + V(u'hdr_nodot', 0, u'无点·2616') + u'>' + V(u'hdr_dot2sp', 0, u'两点·2616') + u')。')

LINES.append(
    u'🪜 四档口径逐份换尺(逐行 ⇎ 折平 ⇎ 摘壳 ⇎ 节窗), 名下针读到的枚数: 逐行 ' + J(u'sn_strict_docs', u'逐行档')
    + u' ⇎ 折平 ' + J(u'sn_fold_docs', u'折平档') + u' ⇎ 摘壳 ' + J(u'sn_sh_docs', u'摘壳档') + u' ⇎ 节窗 '
    + JL(u'sn_sec_docs_scope', u'节窗档') + u'(6585 与 8470 没有幂等节, 这一档按 -1 登记: 口径不存在, 不是零; '
    u'判定 ' + V(u'sec_scope_three', None, u'三档口径存在') + u')。 折行一次救回 '
    + V(u'fold_minus_strict_n', None, u'折行独有针') + u' 枚, 按份 ' + J(u'fold_minus_strict_own', u'折行独有')
    + u'——2616 名下 ' + V(u'needles_owned', 0, u'名下针·2616') + u' 枚里 ' + V(u'fold_minus_strict_own', 0, u'折行独有·2616')
    + u' 枚跨行, 逐行档只剩 ' + V(u'sn_strict_docs', 0, u'逐行·2616') + u' 枚可读。 摘壳一枚不丢('
    + J(u'sh_loses', u'摘壳减折平') + u') ⇎ 新开 ' + V(u'sh_gains', 2, u'摘壳独有·6585') + u' 枚('
    + NKL(F[u'sh_gains_keys']) + u'): 428 的定义句正好被 ' + AN(2, u'The 428 status code indicates')
    + u' 跨到下一页的页壳切开, 只有摘壳档读得到。 节外 ' + V(u'sh_no_sec_n', None, u'节外针') + u' 枚('
    + NKL(F[u'sh_no_sec_keys']) + u'), 按份 ' + J(u'sh_no_sec_own', u'节外按份')
    + u'——全是两份 HTTP/1.1 系的规范里住在幂等节之外的那几枚。 死集 ' + V(u'dead_needles_none', None, u'死针账零')
    + u'(清单 ' + NKL(F[u'dead_needles']) + u'); 反向对照 ' + V(u'neg_n', None, u'反向针数') + u' 枚('
    + J(u'neg_own_nd', u'反向按份') + u')最宽档命中 ' + V(u'neg_hit_widest', None, u'反向最宽命中')
    + u' ⇎ 最窄档 ' + V(u'neg_hit_strict', None, u'反向最窄命中') + u' 枚。 阶梯进出账判定 '
    + V(u'ladder_close', None, u'阶梯闭合') + u'、单调性 ' + V(u'ladder_monotone', None, u'阶梯单调')
    + u'、正则轨与游标轨同值 ' + V(u're_eq_cur', None, u'两轨同值') + u'、重叠口径不多吃 '
    + V(u'overlap_extra', None, u'重叠多出') + u'。 名下针共 ' + J(u'needles_owned', u'名下针') + u' 枚 ⇎ 锚句总长 '
    + V(u'nd_len_tot', None, u'锚句总长') + u' 字符, 最长一枚 ' + V(u'nd_len_max', None, u'锚句最长') + u' 字符。')

LINES.append(
    u'🗂 幂等节只有三份文书有(有节 ' + V(u'sec_found_n', None, u'有节份数') + u' ⇎ 无节 '
    + V(u'sec_absent_n', None, u'无节份数') + u'): 2616 是 ' + ANX(0, u'9.1.2 Idempotent Methods')
    + u', 7231 把它搬进 ' + ANX(1, u'4.2.2.  Idempotent Methods') + u', 9110 再搬进第 '
    + V(u'sec_body_line', 4, u'节头行·9110') + u' 行的 ' + AN(4, u'A request method is considered')
    + u'——后两者的编号尾节同为 2.2, 前缀从 4 换到 9。 '
    + u'节窗幅: 字符 ' + J(u'sec_chars', u'节窗字符') + u' ⇎ 行 ' + J(u'sec_lines', u'节窗行') + u' ⇎ 词 '
    + J(u'sec_words', u'节窗词') + u' ⇎ 句 ' + J(u'sec_sents', u'节窗句') + u'; 句数换第二把尺(逐字符扫句尾 ⇎ 前瞻正则)'
    + u'逐份同值 ' + J(u'sec_sents_gap', u'句数两轨差') + u'。 节窗字数占各自摘壳面的千分比 '
    + J(u'sec_share_permille', u'节窗千分比') + u'。 同名标题在面上命中 ' + J(u'sec_hit_n', u'标题命中')
    + u' 行——只有 9110 命中两行: 目录行 ' + V(u'sec_toc_line', 4, u'目录行·9110') + u' ⇎ 正文行 '
    + V(u'sec_body_line', 4, u'节头行·9110') + u', 新版式把目录也写成同样的缩进标题(判定 ' + V(u'sec_row_dup', 4, u'目录正文差·9110')
    + u'); 2616 与 7231 的目录行带点引线与页码, 标题面认不出它: ' + AN(0, u'9.1.2 Idempotent Methods ...')
    + u'——于是全库命中合计 ' + V(u'sec_hit_tot', None, u'命中合计') + u' 枚 = 有节的 ' + V(u'sec_found_n', None, u'有节份数2')
    + u' 份各一行正文 + 那唯一一行目录(判定 ' + V(u'sec_row_dup', 4, u'目录多出') + u'⇔' + V(u'sec_hit_tot', None, u'合计')
    + u'-' + V(u'sec_found_n', None, u'份数') + u')。 '
    + u'节尾由下一个同级标题定界: ' + ANX(0, u'9.2 OPTIONS') + u' ⇎ ' + ANX(1, u'4.2.3.  Cacheable Methods')
    + u' ⇎ ' + ANL(4, F[u'sec_body_line'][4], u'9.2.3.  Methods and Caching')
    + u'(同一串在 9110 的目录与正文各印一次, 定界取不早于节头的那一行), 三份都是标题式收束(无一到串尾)。 '
    + u'同一行标题在面上印几行也是版式差: 逐份 ' + J(u'sec_end_head_rows', u'节尾标题印行') + u' 行——'
    + V(u'sec_end_head_rows', 4, u'节尾印行·9110') + u' 行来自 9110 的目录与正文同形(判定 '
    + V(u'sec_end_head_rows', 4, u'印两行') + u'-' + V(u'sec_row_dup', 4, u'目录命中') + u'-1=' + EXPR(F[u'sec_end_head_rows'][4] - F[u'sec_row_dup'][4] - 1,
           u"B80V('sec_end_head_rows', 4) - B80V('sec_row_dup', 4) - 1", u'节尾印行归零')
    + u'), 旧版式的两份各只印一行。 '
    + u'7231 的节窗里一个义务词也没有(节内 ' + V(u'tone_sec_tot', 1, u'节内义务词·7231') + u' 枚, 判定 '
    + V(u'tone_zero_7231_sec', None, u'7231节内零义务词') + u'), 它给的是纯机制句; 2616 节内 '
    + V(u'tone_sec_tot', 0, u'节内义务词·2616') + u' 枚 ⇎ 9110 ' + V(u'tone_sec_tot', 4, u'节内义务词·9110') + u' 枚。')

LINES.append(
    u'⚖ 2616 把判词写在定义之外: §9.1.2 只给“ Methods can also have the property of…”这句定义(它在节窗内, '
    + V(u'defin_in_sec', None, u'定义在节内') + u' 枚 ⇎ ' + V(u'defin_in_sh', None, u'定义在摘壳') + u'), '
    + u'而“能不能自动重来”的三枚判词全在别处——逐行 ' + V(u'v_in_sec', None, u'判词在节内') + u' 枚 ⇎ 摘壳 '
    + V(u'v_in_sh', None, u'判词在摘壳') + u' 枚, 三枚都记进节外账(' + V(u'v_sh_no_sec', None, u'判词记节外')
    + u')。 判词印在第 ' + V(u'ln_verdict_2616', None, u'判词行·2616') + u' 行: '
    + AN(0, u'idempotent (see section 9.1.2). Non-idempotent methods or sequences') + u'——它自己就把读者指回 §9.1.2; '
    + u'该节标题在第 ' + V(u'sec_head_line_2616', None, u'节头行·2616') + u' 行, 相距 '
    + V(u'verdict_head_gap', None, u'判词到节头') + u' 行, 判词在节头之上(判定 '
    + V(u'verdict_above_head_2616', None, u'判词先于节头') + u')。 全文指向 §9.1.2 的交叉引用共 '
    + V(u'xref_line', None, u'交叉引用处') + u' 处, 前一处已在讲流水线: '
    + AN(0, u'non-idempotent sequences of methods (see section 9.1.2)') + u', 后一处就是判词行(两处行号 '
    + JL(u'xref_lines_abs', u'引用行号') + u' ⇎ 判词行 ' + JL(u'verdict_lines_abs', u'判词行号') + u')。 '
    + u'节内还有那句副作用禁令(在节窗内 ' + V(u'sidefx_in_sec', None, u'副作用句在节内') + u' 枚): '
    + AN(0, u'TRACE SHOULD NOT have side effects') + u'。 对照 9110: 它名下 ' + V(u'k9110_tot', None, u'9110名下针')
    + u' 枚全部住在 §9.2.2 之内(节内 ' + V(u'k9110_in_sec', None, u'9110节内') + u' ⇎ 节外 '
    + V(u'k9110_no_sec', None, u'9110节外') + u', 判定 ' + V(u'k9110_inside_sec', None, u'9110全在节内')
    + u')——同一个问题, 2616 的答案散在连接管理章里 ⇎ 9110 把答案收进一节。')

LINES.append(
    u'🔤 “自动重来”的说法本身是族谱: automat*×retry 六式(' + u' '.join(F[u'auto_fam']) + u')折平档枚数 '
    + J(u'auto_tot_fold', u'自动重试族') + u' ⇎ 逐行档 ' + J(u'auto_tot_line', u'自动重试族逐行')
    + u'——两档逐份同枚(判定 ' + V(u'auto_gain_tot', None, u'折行增益合计') + u'), 摘壳也不多不少('
    + J(u'auto_sh_minus_fold', u'摘壳减折平·自动族') + u')。 6585 六式零枚, 连裸词 automat* 也是 '
    + V(u'auto_bare', 2, u'裸automat·6585') + u' 枚(判定 ' + V(u'no_auto_vocab_6585', None, u'6585零自动词')
    + u'), 它答的是另一套话: 一个码加一个头加一个例子——' + AN(2, u'Retry-After: 3600') + u', '
    + AN(2, u'I only allow 50 requests per hour') + u', 外加自认没定义怎么数: '
    + AN(2, u'Note that this specification does not define') + u'。 9110 一份独占 '
    + V(u'auto_tot_fold', 4, u'自动族·9110') + u' 枚 ⇎ 裸 automat* ' + V(u'auto_bare', 4, u'裸automat·9110')
    + u' 枚(差 ' + V(u'auto_bare_minus_union', 4, u'裸词减族·9110') + u' 枚是“不在 retry 邻座”的 automatic/automatically)。 '
    + u'族内互含只发生在 9110 一份(判定 ' + V(u'auto_fam_overlap_other4', None, u'族内互含归零')
    + u')。 再说“重来”的八个动词式(' + u' '.join(F[u'reword_fam']) + u'): 族内合计 ' + J(u'reword_tot', u'重来族')
    + u' ⇎ 去重后 ' + J(u'reword_union', u'重来去重') + u' 枚, 差 ' + J(u'reword_overlap', u'重来互含')
    + u' 枚来自同词根互包; 零枚的族数 ' + J(u'reword_zero_n', u'重来零枚族') + u'——8470 八式里 '
    + V(u'reword_zero_n', 3, u'零枚族·8470') + u' 式一次没用(判定 ' + V(u'reword_zero_n', 3, u'重来零枚·8470')
    + u'), 而全库没有一枚写 “make a new request”: 6585 写的是 ' + AN(2, u'to wait before making a new request')
    + u'(判定 ' + V(u'reword_make_tot', None, u'make零枚合计') + u'); 只属于一份的说法零枚(判定 '
    + V(u'reword_own_tot', None, u'独有一族') + u')。 idempotent 一词逐份 '
    + J(u'idem_str', u'idempotent枚') + u' 枚: 6585 与 8470 面上零枚(判定 ' + V(u'idem_str_6585_8470', None, u'两份零idempotent')
    + u')。')

LINES.append(
    u'‼ 义务词五式(' + u' '.join(F[u'tone_fam']) + u')在最宽档逐份 ' + J(u'tone_tot', u'义务词最宽档')
    + u' ⇎ 折平 ' + J(u'tone_fold_tot', u'义务词折平') + u'; 大小写差(全大写族 ⇎ 含小写) '
    + J(u'tone_case_gap', u'大小写差') + u', 小写族合计 ' + J(u'tone_word_lc_tot', u'小写族')
    + u'——8470 一份大写 ' + V(u'tone_tot', 3, u'义务词·8470') + u' ⇎ 小写 ' + V(u'tone_word_lc_tot', 3, u'小写族·8470')
    + u' 枚, 它是唯一把 “must/should” 也大量写小写的引用式文书。 字母边界尺与字母数字边界尺在大写族上逐份同值 '
    + J(u'tone_alnum_gap', u'两把词尺差') + u'(合计判定 ' + V(u'tone_ruler_close', None, u'义务词尺闭合') + u'); '
    + u'手扫轨与正则轨同值(合计差 ' + V(u'tone_wide_close', None, u'义务词两轨差') + u')。 被 72 列换行切开的大写义务词 '
    + J(u'tone_straddle', u'义务词切开') + u' 枚——2616 三枚 ⇎ 7231 一枚 ⇎ 9110 九枚, 6585 与 8470 零枚(判定 '
    + V(u'tone_straddle_6585_8470', None, u'两份零切开') + u')。 大写 MUST 账: 裸 MUST = MUST NOT + 纯 MUST, '
    + u'五份各自账平 ' + J(u'tone_must_ledger', u'MUST账') + u'(纯 MUST ' + J(u'tone_must_pure', u'纯MUST') + u')。 '
    + u'节窗内的义务词只属于两份: ' + J(u'tone_sec_tot', u'节内义务词') + u', 每千字 ' + J(u'tone_sec_per_mille', u'节内义务词千分比')
    + u' 枚 ⇎ 7231/6585/8470 的节窗里 ' + J(u'tone_sec_tot', u'节内义务词零') + u' 枚(判定 '
    + V(u'tone_zero_7231_sec', None, u'7231节内零') + u')。 五份的答句语气各不相同: 2616 用被动 '
    + AN(0, u'MUST NOT be automatically retried, although user agents MAY offer a') + u'; 7231 整段不点义务 '
    + AN(1, u'Idempotent methods are distinguished because') + u'; 6585 只把 MUST NOT 给缓存 '
    + AN(2, u'Responses with the 429 status code MUST NOT be stored by a cache.') + u'; 8470 一句里给全 SHOULD ⇎ MUST NOT ⇎ MAY '
    + AN(3, u'user agent SHOULD retry automatically, but any retries MUST NOT be') + u'; 9110 点名两份禁令 '
    + AN(4, u'A proxy MUST NOT automatically retry non-idempotent requests.') + u'。')

LINES.append(
    u'🔢 数字七式(' + u' '.join(F[u'num_fam']) + u')逐份: 秒数 "3600" ' + J(u'num_3600_docs', u'3600枚')
    + u' ⇎ "120" ' + J(u'num_120_docs', u'120枚') + u' ⇎ HTTP-date ' + J(u'num_httpdate_docs', u'HTTPdate枚')
    + u' ⇎ delta-seconds ' + J(u'num_dsec_docs', u'delta秒枚') + u' ⇎ delay-seconds ' + J(u'num_delay_docs', u'delay秒枚')
    + u'。 单位名换代完全分家: 2616 只写 delta-seconds(' + V(u'num_dsec_docs', 0, u'delta·2616') + u' 枚 ⇎ delay '
    + V(u'num_delay_docs', 0, u'delay·2616') + u' 枚), 7231 与 9110 只写 delay-seconds('
    + V(u'num_delay_docs', 1, u'delay·7231') + u'/' + V(u'num_delay_docs', 4, u'delay·9110') + u' 枚 ⇎ delta '
    + V(u'num_dsec_docs', 1, u'delta·7231') + u'/' + V(u'num_dsec_docs', 4, u'delta·9110')
    + u' 枚), 判定 ' + V(u'rename_delta_vs_delay', None, u'改名分家') + u'; 带边界尺与裸串尺在两族上逐枚相等 '
    + J(u'num_sub', u'数字子串差') + u'(无短数被长数的子串吃进的假阳性)。 数字族里恰两枚只属于一份: '
    + u'2616 的 delta-seconds ⇎ 6585 的 ' + AN(2, u'I only allow 50 requests per hour') + u'(判定 '
    + EXPR(F[u'num_own_tot'] - 2, u"B80V('num_own_tot') - 2", u'独有减恰两枚') + u')。 Retry-After 一行 '
    + J(u'ra_count', u'RetryAfter枚') + u' 枚, 8470 全文不提它(判定 ' + V(u'no_retry_after_8470', None, u'8470零RetryAfter')
    + u')。 规则式两代并立: 2616 用竖线式 ⇎ 7231/9110 用斜杠式, 竖线 ' + J(u'ra_abnf_bar', u'竖线式') + u' ⇎ 斜杠 '
    + J(u'ra_abnf_slash', u'斜杠式') + u' ⇎ 引号式 ' + J(u'ra_abnf_quoted', u'引号式') + u', 逐份三式加规则行总数 '
    + J(u'ra_abnf_lines', u'规则行数') + u' 账平(判定 ' + V(u'ra_abnf_ledger', None, u'规则式账平')
    + u'): ' + AN(0, u'Retry-After  = "Retry-After"') + u' ⇎ ' + AN(1, u'Retry-After = HTTP-date / delay-seconds')
    + u'; 定义式两侧 ' + J(u'ra_delta_def', u'单位定义行') + u' 行, 2616 的 ' + AN(0, u'delta-seconds  = 1*DIGIT')
    + u' ⇎ 7231 的 ' + AN(1, u'delay-seconds  = 1*DIGIT') + u'。 例子分家: HTTP-date 例 ' + J(u'ra_exp_date', u'日期例')
    + u' 枚 ⇎ “120 秒⇎两分钟”例 ' + J(u'ra_exp_120', u'120例') + u' ⇎ ' + J(u'ra_two_minutes', u'两分钟例')
    + u' ⇎ 只有 6585 印 ' + AN(2, u'Retry-After: 3600') + u'(' + V(u'ra_exp_3600', 2, u'3600例·6585')
    + u' 枚, 判定 ' + V(u'ra_exp_120', 2, u'120例·6585') + u'+' + V(u'ra_two_minutes', 2, u'两分钟例·6585')
    + u'=0)。 数字总量 ' + J(u'num_tot', u'数字族合计') + u' 枚 ⇎ 数字字符 ' + J(u'digit_chars', u'数字字符') + u' 枚。')

LINES.append(
    u'🧾 状态码定义行(“码 + 名”形状, 目录行另计)逐份 ' + J(u'code_defined_n', u'定义行') + u' 行 ⇎ 目录行 '
    + J(u'code_toc', u'目录行') + u' 行 ⇎ 族数 ' + J(u'code_def_fams', u'定义码族数') + u' 枚。 2616 定义 '
    + V(u'code_def_fams', 0, u'族数·2616') + u' 枚 ⇎ 7231 只剩 ' + V(u'code_def_fams', 1, u'族数·7231')
    + u' 枚——少了 401 与 416 两枚(判定 ' + V(u'code_7231_drops_n', None, u'7231少定义') + u' ⇎ '
    + u' '.join(F[u'code_7231_drops']) + u'), 它们搬去了同族分册; 9110 又回到 '
    + V(u'code_def_fams', 4, u'族数·9110') + u' 枚, 且定义集与 2616 逐枚同(判定 '
    + V(u'code_set_same_2616_9110', None, u'码集同2616') + u')。 6585 定义 '
    + V(u'code_def_fams', 2, u'族数·6585') + u' 枚新码(' + u' '.join(F[u'code_defined_lbl'][2]) + u'), 其中 428 定义行印了两处(目录 ⇎ 节标题): '
    + V(u'code_defined', 2, u'428定义行·6585') + u' 枚; 8470 一枚也不定义(判定 ' + V(u'no_code_def_8470', None, u'8470零定义')
    + u'), 它只用“码+括号名”的印法引用: ' + AN(3, u'A 425 (Too Early) status code indicates') + u'——这种印法只有它用(判定 '
    + V(u'paren_2616_7231_9110', None, u'其余三份括号印法')
    + u'), 且 ' + V(u'paren_straddle', 3, u'括号被切·8470') + u' 枚被换行切在中间(其余四份 '
    + V(u'paren_straddle', 0, u'括号被切·2616') + u'/' + V(u'paren_straddle', 1, u'括号被切·7231') + u'/'
    + V(u'paren_straddle', 2, u'括号被切·6585') + u'/' + V(u'paren_straddle', 4, u'括号被切·9110') + u' 枚)。 '
    + u'现行 9110 既不定义 428 也不定义 429(判定 ' + V(u'neither_428_429_in_9110', None, u'9110零428429')
    + u' ⇎ 2616/7231 同 ' + V(u'neither_428_429_in_2616', None, u'2616零428429') + u'): 限流那一码住在本族之外的 6585 里, '
    + AN(2, u'The 429 status code indicates') + u'。 反向对照九式(' + u' '.join(F[u'neg_fam']) + u')逐份冷热度: '
    + u'零枚族数 ' + J(u'neg_zero_n', u'冷族数') + u' ⇎ 边界尺合计 ' + J(u'neg_tot', u'反向合计')
    + u' 枚——2616 冷 ' + V(u'neg_zero_n', 0, u'冷族·2616') + u' 式但说 idempotent ' + V(u'neg_bnd', 0, u'反向·2616')
    + u' 行的最后一列 ' + V(u'neg_bnd', 0, u'idempotent·2616') + u' 枚; 裸串尺比边界尺多出的假阳性恰两枚(判定 '
    + EXPR(F[u'neg_false_sub_tot'] - 2, u"B80V('neg_false_sub_tot') - 2", u'假阳性多出') + u'): 2616 的 “425” ⇎ 9110 的 “428” 都来自别处(9110 那枚在 '
    + AN(4, u'RFC 4289, December 2005') + u' 这类引用号里)。')

LINES.append(
    u'🎭 谁来重来的名字也换代: 九式施事针(' + u' '.join(F[u'subj_fam']) + u')逐份命中 ' + J(u'subj_n', u'施事针')
    + u' 枚; 点名施事者的主动句 ' + J(u'subj_active', u'主动句') + u' ⇎ 不点名的被动句 ' + J(u'subj_passive', u'被动句')
    + u'——被动式判词全库恰一枚, 就是 2616 那句(判定 ' + V(u'subj_only_passive_2616', None, u'唯被动2616') + u'); '
    + u'7231 与 6585 的判词一个施事者也不点(判定 ' + V(u'subj_active_7231_6585', None, u'两份零主动')
    + u')。 泛称七式(… )逐份合计 ' + J(u'act_tot', u'施事泛称') + u' 枚, 其中 user agent 的单数⇎复数在零宽尺下相加不减 '
    + J(u'act_sg_plus_pl', u'单复数子串差') + u'; 节窗内的点名账: 2616 的 §9.1.2 ' + V(u'act_sec_tot', 0, u'节内施事·2616')
    + u' 枚(它只谈方法与序列, 不谈谁) ⇎ 7231 谈 client ' + V(u'act_sec', 1, u'节内client·7231') + u' 次 ⇎ 9110 谈 client '
    + V(u'act_sec', 4, u'节内client·9110') + u' ⇎ proxy ' + V(u'act_sec', 4, u'节内proxy·9110')
    + u' ⇎ user agent ' + V(u'act_sec', 4, u'节内ua·9110') + u' 次(判定 ' + V(u'act_sec_only_two_docs', None, u'节内点名两份')
    + u')。 POST 在节窗里被点名只发生在 9110: ' + V(u'meth_post_sec', 4, u'节内POST·9110') + u' 次 ⇎ 其余四份 '
    + V(u'meth_post_sec_other4', None, u'节内POST其余四份') + u' 次(判定 '
    + V(u'meth_post_sec_other4', None, u'四份零节内POST') + u'), 那句是 ' + AN(4, u'a user agent can repeat a POST request automatically') + u'。 九式施事针被换行切开的恰两枚, 都在 9110 名下(判定 '
    + EXPR(F[u'subj_straddle_tot'] - F[u'subj_straddle'][4], u"B80V('subj_straddle_tot') - B80V('subj_straddle', 4)", u'切开只在一份') + u'): ' + NKL(F[u'subj_straddled'][4]) + u'。')

LINES.append(
    u'📐 搬字用两把尺。 行尺: 长行池 ' + V(u'pool_n', None, u'行池') + u' 行 ⇎ 并集 ' + V(u'pool_union', None, u'行池并集')
    + u' 条(重复行 ' + V(u'pool_rows_minus_union', None, u'池行减并集') + u' 行), 按“几条文档印了它”分档 '
    + JL(u'pool_tier', u'行池分档') + u'(判定 ' + V(u'pool_tier_close', None, u'分档闭合') + u'); 两两共用 '
    + V(u'pair_nonzero', None, u'非零对数') + u' 对 ⇎ 零枚 ' + V(u'pair_zero', None, u'零枚对数')
    + u' 对, 最小 ' + V(u'pair_min', None, u'最小共用') + u' 枚(' + V(u'pair_min_lbl', None, u'最小对')
    + u'), 最大 ' + V(u'pair_max', None, u'最大共用') + u' 枚(' + V(u'pair_max_lbl', None, u'最大对')
    + u')=逐字节同形 ' + V(u'pair_max_byte_keys', None, u'字节同形') + u' + 只归一同形 ' + V(u'pair_max_norm_only_keys', None, u'只归一同形')
    + u'(判定 ' + V(u'pair_close', None, u'两两账平') + u')。 单位要挑明: 同一对换成“原始行枚”数是 '
    + V(u'pair_max_byte_lines', None, u'字节同形行枚') + u' 行 ⇎ 折叠键 ' + V(u'pair_max_byte_keys', None, u'字节同形')
    + u' 条, 差 ' + V(u'pair_byte_unit_gap', None, u'行减键差') + u' 行是同一折叠键在两处各印一次(壳行吃掉 '
    + V(u'pair_byte_shell_gap', None, u'键减壳差') + u' 行, 判定 ' + V(u'pair_byte_lines_ge_keys', None, u'行不少于键')
    + u'))。 分家三本账: 折叠后同形而字节不同者按“靠什么归一”拆 ' + V(u'axis_str', None, u'分家口径')
    + u', 共 ' + V(u'axis_total', None, u'分家行数') + u' 行 ⇎ 池内两桶相加账平(判定 ' + V(u'axis_close', None, u'分家账平')
    + u' ⇎ 用到的桶 ' + V(u'axis_str_n', None, u'分家桶数') + u' 个), 例: ' + AN(1, u'Accept: text/plain; q=0.5, text/html,')
    + u' 与 9110 的同句只差一处空格。 容斥复核: Σ单份−Σ两两+Σ三三−Σ四四+Σ五五 ' + V(u'pool_incl', None, u'容斥各阶')
    + u' ⇎ 并集 ' + V(u'union_incl', None, u'容斥结果') + u' 条(判定 ' + V(u'union_close', None, u'容斥闭合') + u')。 '
    + u'句尺(把硬换行折成句)另一把: 池 ' + V(u's_pool_n', None, u'句池') + u' 句 ⇎ 最大对 '
    + V(u's_pair_max', None, u'句尺最大') + u' 句(' + V(u's_pair_max_lbl', None, u'句尺最大对') + u'), 同一对从行尺到句尺 '
    + V(u's_ruler_drop_7231_9110', None, u'句尺少读') + u' 枚(与_gain_ 反号相加归零 '
    + EXPR(F[u's_ruler_gain_7231_9110'] + F[u's_ruler_drop_7231_9110'],
           u"B80V('s_ruler_gain_7231_9110') + B80V('s_ruler_drop_7231_9110')", u'两尺反号')
    + u')——单位不同不是矛盾: 一句由 '
    + V(u'pair_row_per_sent', None, u'行句比') + u' 行摊开。 '
    + u'共用行的归属分档也量: 最大对的 ' + V(u'pb_7231_9110', None, u'字节同形·7231对') + u' 枚里 '
    + V(u'only2_7231_9110', None, u'只属这一对') + u' 枚只属于这一对(搬家正文), 其余三份以上共用(模板行); 8470·9110 一对 '
    + V(u'pb_8470_9110', None, u'字节同形·8470对') + u' 枚里只属这一对 ' + V(u'only2_8470_9110', None, u'只属8470对')
    + u' ⇎ 更多份共用 ' + V(u'multi_8470_9110', None, u'多份共用8470对') + u' 枚(判定两对各自账平 '
    + V(u'pair_close', None, u'两两账平') + u')。 锚候选池第三把尺: ' + V(u'apool_n', None, u'锚池') + u' 条 ⇎ 原始 '
    + V(u'apool_raw_n', None, u'锚池原始') + u' 条, 按份 ' + JL(u'apool_tag_n', u'锚池按份') + u'(判定 '
    + V(u'apool_tag_close', None, u'锚池账平') + u')。')

LINES.append(
    u'🧬 抬头谱系全在库内字节里: 发布序 ' + V(u'year_order_lbl', None, u'年序') + u', 年距首末 '
    + V(u'year_span', None, u'年跨') + u' 年 ⇎ 按发布顺序排年只一处倒退(判定 ' + V(u'year_inversions', None, u'年序倒退')
    + u'): 7231(2014) 之后出的 6585 写 ' + AN(2, u'April 2012') + u'。 Obsoletes 共 ' + V(u'obs_total', None, u'废止总数')
    + u' 号, 各份段数 ' + JL(u'obs_raw_segs', u'废止段数') + u', 其中 9110 冒号后尾随一个空段('
    + V(u'obs_blank_segs', 4, u'空段·9110') + u'), 剔空后读出 ' + V(u'obs_total', None, u'废止号')
    + u' 号 ⇎ 各份清单 ' + u' '.join(u'%s:%s' % (LBL[i], u','.join(F[u'obs_ids_clean'][i]) or u'-') for i in range(NSRC))
    + u'(判定 ' + V(u'lineage_close', None, u'谱系账平') + u')。 被废止者恰好也在本库: 库内命中 '
    + EXPR(sum(F[u'obs_target_in_lib']), u"sum(B80V('obs_target_in_lib'))", u'废止目标在库内') + u' 处 ⇎ '
    + J(u'obs_target_in_lib', u'废止在库') + u'——7231 废止 ' + AN(1, u'Obsoletes: 2616') + u' ⇎ 9110 废止 '
    + AN(4, u'Obsoletes: 2818, 7230, 7231, 7232, 7233, 7235,') + u'(库里两份都在列)。 Updates 共 '
    + V(u'upd_total', None, u'更新总数') + u' 处, 而 6585 更新的那份 ' + AN(2, u'Updates: 2616')
    + u' 正是被人废止的那份(判定 ' + V(u'upd_target_obsoleted', 2, u'更新者被废止·6585') + u')。 出边为零的一份是 '
    + V(u'lineage_no_edge', None, u'无出边') + u'(8470 抬头既不 Obsoletes 也不 Updates)。 抬头其他两格: ISSN '
    + J(u'issn_hdr', u'ISSN行') + u' 行(2616 无), STD 行 ' + V(u'std_n', None, u'STD行数') + u' 行 ⇎ '
    + AN(4, u'STD: 97') + u'; 发布月 ' + u' '.join(F[u'months_txt']) + u'。')

LINES.append(
    u'¶ 答段对照(段界只在摘壳折平面按字面针定位, 行号映回原文件; 共 %d 段: 前五段是五份主答句, 后九段是搬字对⇎定义段⇎自否认段): '
    u'起行 %s ⇎ 止行 %s ⇎ 行数 %s ⇎ 字符 %s ⇎ 词 %s。' % (len(PINS), PJ(u'blk_lo', u'段起行'),
                                                          PJ(u'blk_hi', u'段止行'), PJ(u'blk_rows', u'段行数'),
                                                          PJ(u'blk_chars', u'段字符'), PJ(u'blk_words', u'段词数'))
    + u' 五段主答句合计 ' + V(u'blk_five_chars', None, u'主段字符') + u' 字符 ⇎ ' + V(u'blk_five_words', None, u'主段词数')
    + u' 词 ⇎ ' + V(u'blk_five_rows', None, u'主段行数') + u' 行(与答句跨行账 ' + J(u'ans_span', u'答句跨行')
    + u' 同值, 判定 ' + V(u'blk_five_rows', None, u'主段行账') + u'⇔' + V(u'ans_span_tot', None, u'答句跨行合计')
    + u'); 十四段合计 ' + V(u'blk_rows_tot', None, u'十二段行') + u' 行 ⇎ ' + V(u'blk_words_tot', None, u'十二段词') + u' 词。 '
    + u'最短的一段是 9110 的主答句: ' + V(u'blk_words', 4, u'词·9110段') + u' 词独占 '
    + V(u'blk_rows', 4, u'行·9110段') + u' 行, 全库唯一能在一行内读全的答句(判定 '
    + V(u'one_line_answer_only_9110', None, u'一行读全只在9110') + u' ⇎ 五份 ' + J(u'blk_is_one_line', u'一行读全')
    + u'); 每行词数 ' + J(u'blk_words_per_row', u'段内每行词') + u'。 7231 ⇎ 9110 的搬字两段落逐字同形(判定 '
    + V(u'idem_blk_verbatim', None, u'搬段逐字同') + u'): 幂等定义段共头 ' + V(u'pre_idem_7231_9110', None, u'共头·幂等段')
    + u' 词 ⇎ 共尾 ' + V(u'suf_idem_7231_9110', None, u'共尾·幂等段') + u' 词, 词集账 '
    + V(u'w_ledger_idem', None, u'词集账') + u' 归零(只 7231 ' + V(u'w_only_7231_idem', None, u'只7231')
    + u' ⇎ 只 9110 ' + V(u'w_only_9110_idem', None, u'只9110') + u' ⇎ 共用 ' + V(u'w_common_idem', None, u'共用词')
    + u'); 两段的行距位移相等(判定 ' + V(u'idem_gap_equal', None, u'位移等值') + u'): 幂等段 '
    + V(u'idem_blk_row_gap', None, u'幂等段位移') + u' 行 ⇎ 类比句段 ' + V(u'like_blk_row_gap', None, u'类比段位移')
    + u' 行 ⇎ 差 ' + V(u'blk_gap_delta', None, u'位移差') + u'。 ' + AN(4, u'Like the definition of safe')
    + u' 一句在两份里各印一次 ⇎ 2616 面上零枚(判定 ' + V(u'like_absent_2616', None, u'2616读不到')
    + u'), 反过来 2616 的定义句在 7231 面上 ' + V(u'defin_absent_7231', None, u'7231读不到')
    + u' 枚——换代换了措辞, 不是漏印。 72 列硬换行正切在答案的收束短语里: 五句判词短语逐行读不到的 '
    + J(u'ph_straddle', u'短语被切') + u' 枚 ⇎ 折平全部读得到(判定 ' + V(u'ph_straddle_except_6585', None, u'唯6585未切')
    + u'), 6585 那句 ' + AN(2, u'MAY include a Retry-After header indicating how long') + u' 逐行即读全。 '
    + u'9110 的 “might” 句被切在一行之内还是两行之间由行号尺定: 首字行 ' + V(u'ln_might_head_9110', 1, u'might首行')
    + u' ⇎ 末字行 ' + V(u'ln_might_end_9110', 1, u'might末行') + u', 跨 ' + V(u'might_straddle', None, u'might跨行')
    + u' 行(判定 ' + V(u'might_straddle_one', None, u'might跨一行') + u')。 行号尺复核: 段窗首末行 ⇎ 独立行针共 '
    + V(u'pin_rt_n', None, u'行针复核枚') + u' 枚(' + J(u'pin_rt_src', u'行针按份') + u'), 拿行号回原文件取那一行逐枚自验, '
    + u'命中 ' + V(u'pin_rt_ok', None, u'行针自验枚') + u' 枚(判定 ' + V(u'pin_rt_all', None, u'行针复核判定')
    + u'); 反向对照: 把整段拿回“首字那一行”去验, ' + V(u'pin_wrongline', None, u'错行验中枚') + u' 枚命中(判定 '
    + V(u'pin_wrap_probe', None, u'错行对照判定') + u')。 摘壳折平的片段序列比非空行少 '
    + J(u'pp_gap_rows', u'片段少读行') + u' 行, 少的恰好就是被摘掉的非空页壳行 '
    + J(u'pp_shell_nonblank', u'非空壳行') + u' 行(判定 ' + V(u'pp_gap_close', None, u'壳行相消') + u')。')

LINES.append(
    u'🧮 闭合账总口径: 标量恒等式 ' + V(u'scalar_clos_n', None, u'恒等式数') + u' 条, 全部归零 ⇎ 通过 '
    + V(u'scalar_clos_sum', None, u'恒等式通过') + u' 条 ⇎ 清单式闭合 ' + V(u'list_clos_n', None, u'清单闭合')
    + u' 项 ⇎ 布尔门 ' + V(u'bool_clos_n', None, u'布尔门数') + u' 道全绿(合计 ' + V(u'bool_clos_sum', None, u'布尔门通过')
    + u'); 恒等式在面内共键 ' + V(u'x_ident_n', None, u'共键恒等式') + u' 条。 与采集遍逐键对账 '
    + V(u'pick_agree', None, u'对账相符') + u' 键逐值符 ⇎ ' + V(u'pick_diff', None, u'对账不符')
    + u' 键不符(只对同定义标量); 换名四对各自算完再对拍: 换页 strip 档 ⇎ 采集行档 '
    + V(u'ff_only_vs_pick_lines', None, u'换页档对拍') + u', 摘壳差 ⇎ ' + V(u'sh_gap_vs_pick', None, u'摘壳差对拍')
    + u', 顶格抬头 ⇎ ' + V(u'hdr_tight_vs_pick', None, u'抬头对拍') + u', 字节同形原始行 ⇎ '
    + V(u'pair_byte_lines_vs_pick', None, u'字节行对拍') + u' ⇎ 只归一 ' + V(u'pair_norm_lines_vs_pick', None, u'归一行对拍')
    + u'。 答句两轨只差尾随空白(采集侧的句界正则把 “.” 后的空格留在句里): 逐份 ' + J(u'ans_vs_pick', u'答句等值')
    + u' ⇎ 尾随空白 ' + J(u'ans_tail_ws', u'答句尾空') + u' 字符。 本遍共 ' + V(u'needle_n', None, u'针总数')
    + u' 枚内容针 ⇎ ' + V(u'neg_n', None, u'反向针') + u' 枚反向针; 五份都是纯文本面, 所以门槛对面只有一把尺——'
    + u'原样字节(锚一律抛回原文件那一行), 这与建条侧的四档口径不冲突。')

BADZID = []
for v, w in ZV:
    got = eval(v, {FN: BB80})
    if got != 0:
        BADZID.append((v, w, got))
assert not BADZID, BADZID[:3]
for v, w in ZV:
    reg(u'0', v, w)

DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)

body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCHS = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCHS)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦(' + u'|'.join(TAGS) + u')⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
MISSLINE = [x for x in CITES if x[1] not in ANSET[IDX[x[0]]]]
assert not ATOMFAIL, ATOMFAIL[:3]
if not PROBE:
    assert not ERR, ERR[:3]
    assert not MISSLINE, MISSLINE[:3]
# 同一串针若在本份里有多行可读, 锚取最先那一行: 逐枚记下行号与候选行数, 供人工核对归属
AMB = [x for x in ALOG if x[3] > 1]
if PROBE:
    for x in sorted(set(BADREAD)):
        print(u'  读数针落空: %s %s[%s] %s' % x)
    for x in sorted(set(BLKFAIL)):
        print(u'  段针落空: %s %s @%s' % (x[0], x[2], x[1]))
    for x in sorted(set(ATOMFAIL)):
        print(u'  锚针落空: %s %s' % x)
    print(u'探针汇总: 读数 %d ⇎ 段针 %d ⇎ 锚针 %d ｜ 正文 %d 字符 ｜ 多行可读针 %d' % (
        len(BADREAD), len(BLKFAIL), len(ATOMFAIL), len(body), len(AMB)))
    for x in AMB:
        print(u'  针多解: %s 针=%s 首行=%d 候选=%d' % (x[0], x[1], x[2], x[3]))
    raise SystemExit(0)
HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCHS)
CLS = {u'single': len([a for a in ANCHS if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC]),
       u'all5': len([a for a in ANCHS if len(HITC[a]) == NSRC])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'], u'anchor_all5': CLS[u'all5'],
         u'checks': DIST * NSRC, u'enc_chars': len(body.replace(NL, u'')), u'nsrc': NSRC}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all5'] == DIST
F.update(AMETA)
for n, v in sorted(AMETA.items()):
    reg(str(v), u"%s('%s')" % (FN, n), n)


def _walk(v, path):
    if isinstance(v, list):
        for i, x in enumerate(v):
            for it in _walk(x, path + (i,)):
                yield it
    elif isinstance(v, int) and not isinstance(v, bool):
        yield v, path


def _expr(k, path):
    head = u"%s('%s'%s)" % (FN, k, (u', ' + repr(path[0])) if path else u'')
    return head + u''.join(u'[%d]' % i for i in path[1:])


ELEMS = {}
for kk, vv in F.items():
    for num, pp in _walk(vv, ()):
        if num >= 100:
            ELEMS.setdefault(str(num), []).append(_expr(kk, pp))
SRC_HARD = set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', u''.join(T)))
BODY_HARD = sorted(set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', body)
                       if len(m.group(0).rstrip(u'.')) >= 3), key=lambda x: (len(x), x))
NOEXPR = []
for s in BODY_HARD:
    if s in K_ or s in SRC_HARD:
        continue
    got = [e for e in ELEMS.get(s, []) if eval(e, {FN: BB80}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, [(x, body[max(0, body.index(x) - 80):body.index(x) + 30]) for x in NOEXPR[:3]]
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv80.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
F['contract_n'] = len(F) + 1
json.dump(F, io.open(u'corpus/_b80flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms80.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCHS, key=len, reverse=True)) + NL)

CH = dict(AMETA)
CH.update({u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCHS))),
           u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
           u'classes': dict((c, sorted([a for a in ANCHS if len(HITC[a]) == n]))
                            for c, n in ((u'single', 1), (u'cross', 2), (u'three', 3), (u'four', 4), (u'five', 5))),
           u'collisions': dict((k, v) for k, v in COLL.items()),
           u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
           u'deriv_points': sum(len(v) for v in SEENX.values()), u'notes': NOTES,
           u'anchor_ambiguous': len(AMB), u'anchor_lines': [list(x) for x in ALOG],
           u'needle_n': F[u'needle_n'], u'zid': [[v, w] for v, w in ZV], u'litk': LITK, u'sn': SN,
           u'blk': PTXT, u'pins': [[LBL[i], s, e] for i, s, e in PINS],
           u'closure_keys': sorted([k for k in F if u'close' in k or u'ledger' in k]),
           u'flat': F})
json.dump(CH, io.open(u'corpus/_b80checks.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

ANS5 = [u'判词是被动式“MUST NOT be automatically retried, although user agents MAY offer…”, 还住在连接管理章里, §9.1.2 只给定义',
        u'节内一个义务词也不给, 把幂等写成“为什么区别对待”的机制句, 禁令挪到别处',
        u'不答能不能重来, 只给一个码加一个头加一个例子, 并自认没定义怎么数请求',
        u'一句话给全: early data 的 SHOULD retry ⇎ 非幂等的 MUST NOT 重放 ⇎ MAY 换连接重来',
        u'点名两份禁令 proxy MUST NOT ⇎ client SHOULD NOT, 八词独占一行']
ENTRY = u'corpus/babeltele/B80_http_automatic_retry_five_answers.md'
srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 码位／原行 %d／非空行 %d／最长行 %d 列／换页 %d 枚／答句 %s)' % (
        PATH[i].split('/')[-1], F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        F[u'maxlen'][i], F[u'ff'][i], ANS5[i]) for i in range(NSRC))
    + u' (五份全是 RFC Editor 纯文本面; 换页 ' + str(sum(F[u'ff'])) + u' 枚 ⇎ 页壳行 '
    + str(F['shell_lines']) + u'; 九一一零无分页壳, 唯一带 BOM 与非 ASCII 的一份 '
    + str(sum(F[u'nonascii'])) + u' 枚); 抬头年 ' + u'⇎'.join(str(y) for y in F[u'years']) + u', 跨 '
    + str(F[u'year_span']) + u' 年, 谱系 ' + u'⇎'.join(F[u'year_order_lbl'])
    + u', 年序倒退 ' + str(F[u'year_inversions']) + u' 处(6585 发得晚却署 '
    + str(F[u'years'][2]) + u'); 节窗 ⇎ 十四段答段 ⇎ 行号尺的往返复核全部由面上位置导出, 一个都不手填。 '
      + u'抓取时刻、RFC Editor 此刻的现行状态页与勘误页(2616 此刻是否仍挂“Historic”标签、后续 errata 是否修过这句判词, 都不可由在库文件判定——在库字节只给得出抬头里的 Obsoletes/Updates 清单)、'
        u'被废止文书自己的现行文本、现网客户端与代理实际会不会自动重发(规范给的义务词不等于装机行为)、'
        u'镜像页的生成时刻与本版号之外的修订, 都只在本机或站外成立, 不进门槛)\n')
link = (u"；联结不是“同一份数据的两种序列化”, 而是“失败的请求到底能不能由程序自己重发”在五份 HTTP 文书里的五种答法: "
        u"2616 把判词写在幂等定义之外——§9.1.2 只给 “Methods can also have the property of…” 这句定义, "
        u"“Non-idempotent methods or sequences MUST NOT be automatically retried” 却印在第 "
        + str(F[u'ln_verdict_2616']) + u" 行, 距节头 " + str(F[u'verdict_head_gap']) + u" 行, 而且是全库唯一一句不点施事者的被动式; "
        u"⇎ 7231 把同一条款搬进 §4.2.2, 节内大写义务词 " + str(F[u'tone_sec_tot'][1]) + u" 枚, 只留机制句, 禁令挪去别处; "
        u"⇎ 6585 根本不答这个问题, 它给 429 一个码 ⇎ Retry-After 一个头 ⇎ " + str(F[u'ra_exp_3600'][2])
        + u" 枚例子, 外加一句自认 “this specification does not define” 该怎么数; "
        u"⇎ 8470 在一句里给全 SHOULD retry ⇎ MUST NOT 重放 ⇎ MAY 换连接, 是唯一把 must/should 也大量写小写的一份("
        + str(F[u'tone_tot'][3]) + u" 枚大写 ⇎ " + str(F[u'tone_word_lc_tot'][3]) + u" 枚小写); "
        u"⇎ 9110 把两份禁令点名写全(proxy ⇎ client), 收进 §9.2.2, " + str(F[u'k9110_tot'])
        + u" 枚名下针全在节内。措辞也换代: automat×retry 搭配 " + u'⇎'.join(str(x) for x in F[u'auto_tot_fold'])
        + u" 枚, 施事者从被动式换成 user agent/client/proxy(九式施事针命中 "
        + u'⇎'.join(str(x) for x in F[u'subj_n']) + u" 枚), 单位从 delta-seconds 换成 delay-seconds("
        + str(F[u'rename_delta_vs_delay']) + u"), 而“重发”一词的八个动词式里 8470 一次只用上 "
        + str(F[u'reword_zero_n'][3]) + u" 式之外的 " + str(8 - F[u'reword_zero_n'][3]) + u" 式。\n")
tags = (u'五答: 2616 判词在节外(节内 %d 枚 ⇎ 摘壳 %d 枚, 距节头 %d 行) ⇎ 7231 节内零义务词只给机制 ⇎ 6585 不答只给码⇎头⇎例子并自认未定义 ⇎ 8470 一句给全 SHOULD⇎MUST NOT⇎MAY ⇎ 9110 点名 proxy⇎client 两禁令(名下 %d 枚全在节内) '
        u'四档口径(逐行⇎折平⇎摘壳⇎节窗, 折行救 %d 枚 ⇎ 摘壳新开 %s 枚 ⇎ 节外 %d 枚) 死集零 反向 %d 枚全冷 '
        u'幂等节只有 %d 份有(9110 目录行也命中, 共 %d 枚) '
        u'措辞换代: automat×retry %s 枚 ⇎ 裸 automat %s 枚 ⇎ 重来八式 %s 枚 ⇎ 施事九式 %s 枚(被动恰 %d 枚) '
        u'义务词 %s 枚 ⇎ 小写 %s 枚 ⇎ 切开 %s 枚 ⇎ MUST 账平 '
        u'数字七式: delta⇎delay 改名分家 ⇎ Retry-After %s 枚 ⇎ 规则式竖线 %s ⇎ 斜杠 %s ⇎ 6585 独例 3600 '
        u'搬字两把尺: 行池 %d 条最大 %d(字节 %d ⇎ 只归一 %d ⇎ 原始行 %d) ⇎ 句池 %d 句最大 %d(增益 %d) ⇎ 只属一对 %d 枚 ⇎ 多份共用 %d 枚 '
        u'状态码定义族 %s ⇎ 7231 少两枚 ⇎ 括号印法只在 8470(%d 枚, %d 枚被换行切开) ⇎ 反向假阳性恰 %d 枚 '
        u'十四段答段: 五份主答句共 %d 行 ⇎ 唯 9110 一行读全 ⇎ 7231⇎9110 两段逐字同形共头 %d 词共尾 %d 词 ⇎ 行距同为 %d '
        u'谱系 %s 跨 %d 年 ⇎ 年序倒退 %d ⇎ Obsoletes %d 号 ⇎ Updates %d 处 '
        u'闭合账 标量 %d⇎清单 %d 项⇎共键 %d 条 ⇎ 对账 %d 键符 %d 不符 ⇎ 恒等式 %d 枚自 replay ⇎ 锚 %d 处去重 %d\n' % (
            F[u'v_in_sec'], F[u'v_in_sh'], F[u'verdict_head_gap'], F[u'k9110_tot'],
            F[u'fold_minus_strict_n'], F[u'sh_gains'], F[u'sh_no_sec_n'], F[u'neg_n'],
            F[u'sec_found_n'], F[u'sec_hit_tot'],
            u'⇎'.join(str(x) for x in F[u'auto_tot_fold']), u'⇎'.join(str(x) for x in F[u'auto_bare']),
            u'⇎'.join(str(x) for x in F[u'reword_tot']), u'⇎'.join(str(x) for x in F[u'subj_n']), F[u'subj_passive'][0],
            u'⇎'.join(str(x) for x in F[u'tone_tot']), u'⇎'.join(str(x) for x in F[u'tone_word_lc_tot']),
            u'⇎'.join(str(x) for x in F[u'tone_straddle']),
            u'⇎'.join(str(x) for x in F[u'ra_count']), u'⇎'.join(str(x) for x in F[u'ra_abnf_bar']),
            u'⇎'.join(str(x) for x in F[u'ra_abnf_slash']),
            F[u'pool_n'], F[u'pair_max'], F[u'pair_max_byte_keys'], F[u'pair_max_norm_only_keys'],
            F[u'pair_max_byte_lines'], F[u's_pool_n'], F[u's_pair_max'], F[u's_ruler_gain_7231_9110'],
            F[u'only2_7231_9110'], F[u'multi_8470_9110'],
            u'⇎'.join(str(x) for x in F[u'code_def_fams']), sum(F[u'paren'][3]), F[u'paren_straddle'][3],
            F[u'neg_false_sub_tot'], F[u'blk_five_rows'], F[u'pre_idem_7231_9110'], F[u'suf_idem_7231_9110'],
            F[u'idem_blk_row_gap'], u'⇎'.join(F[u'year_order_lbl']), F[u'year_span'], F[u'year_inversions'],
            F[u'obs_total'], F[u'upd_total'],
            F[u'scalar_clos_n'], F[u'list_clos_n'], F[u'x_ident_n'],
            F[u'pick_agree'], F[u'pick_diff'], len(ZV), USED, DIST))
title = (u'# B80 失败的 HTTP 请求到底能不能由程序自己重发，五份一手文书五种答法：'
         u'2616 给了禁令却不写在定义节里（判词距 §9.1.2 节头 %d 行，全库唯一被动式） ⇎ '
         u'7231 搬同条款进 §4.2.2 却一个义务词也不给（节内 %d 枚） ⇎ '
         u'6585 不答这个问题，只给 429 ⇎ Retry-After ⇎ 一个例子，还自认没定义怎么数 ⇎ '
         u'8470 一句给全 SHOULD retry ⇎ MUST NOT 重放 ⇎ MAY 换连接 ⇎ '
         u'9110 点名 proxy MUST NOT ⇎ client SHOULD NOT 两禁令，八词独占一行'
         u'（措辞三代换代：automat×retry %s 枚 ⇎ 施事者 %s 枚 ⇎ 单位 delta-seconds→delay-seconds）\n') % (
             F[u'verdict_head_gap'], F[u'tone_sec_tot'][1],
             u'⇎'.join(str(x) for x in F[u'auto_tot_fold']), u'⇎'.join(str(x) for x in F[u'subj_n']))
text = (title + srcline + link + tags +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n'
        + u'## ⟪BabelTele⟫\n' + body + u'\n\n'
        + u'## ⛓解读注\n\n（此段由 corpus/_fill80.py 从 corpus/_b80checks.json 与 corpus/_deriv80.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s ｜ 归属错配 %d ⇎ 非锚面线 %d ｜ 多行可读针 %d' % (
    USED, DIST, TAGN, len(ERR), len(MISSLINE), len(AMB)))
for x in AMB:
    print(u'  针多解: %s 针=%s 首行=%d 候选=%d' % (x[0], x[1], x[2], x[3]))
print(u'一源 %d ⇎ 二至四源 %d ⇎ 五源 %d ｜ 针 %d ⇎ 折行独有 %d ⇎ 摘壳独有 %s ⇎ 节外 %s ⇎ 死集 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all5'], F[u'needle_n'], F[u'fold_minus_strict_n'],
    NKL(F[u'sh_gains_keys']), NKL(F[u'sh_no_sec_keys']), len(F[u'dead_needles'])))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ⇎ 恒等式 %d ⇎ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), F[u'x_ident_n'], len(F)))
print(u'段 起 %s 止 %s 行 %s 字符 %s 词 %s ｜ 幂等段 共头 %d 共尾 %d 词集账 %d 位移 %d/%d' % (
    F[u'blk_lo'], F[u'blk_hi'], F[u'blk_rows'], F[u'blk_chars'], F[u'blk_words'],
    F[u'pre_idem_7231_9110'], F[u'suf_idem_7231_9110'], F[u'w_ledger_idem'],
    F[u'idem_blk_row_gap'], F[u'like_blk_row_gap']))
print(u'段语气 MUST %s MUST NOT %s MAY %s SHOULD %s ｜ 三轨闭合 %d ｜ 一行读全 %s' % (
    F[u'tone_must_blk'], F[u'tone_mustnot_blk'], F[u'tone_may_blk'], F[u'tone_should_blk'],
    F[u'blk_tone_ruler_close'], F[u'blk_is_one_line']))
print(u'行距 判词⇎节头 %d ⇎ 目录⇎正文 %s ｜ 节窗 %s 行 %s 字符' % (
    F[u'verdict_head_gap'], F[u'sec_row_dup'], F[u'sec_lines'], F[u'sec_chars']))
print(u'池 行尺 %d 最大 %s(%d, 字节 %d ⇎ 原始行 %d) 轴 %s ⇎ 句尺 %d 最大 %d 增益 %d' % (
    F[u'pool_n'], F[u'pair_max_lbl'], F[u'pair_max'], F[u'pair_max_byte_keys'],
    F[u'pair_max_byte_lines'], F[u'axis_str'], F[u's_pool_n'], F[u's_pair_max'], F[u's_ruler_gain_7231_9110']))
print(u'行针复核 %d/%d ⇎ 错行反向 %d ⇎ might 跨行 %d' % (
    F[u'pin_rt_ok'], F[u'pin_rt_n'], F[u'pin_wrongline'], F[u'might_straddle']))
print(u'判定 %s' % (CLOSE,))
