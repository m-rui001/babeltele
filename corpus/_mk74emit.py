# -*- coding: utf-8 -*-
"""建条目第二遍(B74)的后半: 由 _mkB74.py 在顶层 exec 进来, 与前半共享同一批现读量。
本半只做三件事: 把“投递失败到底多久再试一次、什么时候不再试”这一句在五份文书里的答句段落做成可算的
段落对照(段界只在各份最宽档面上按字面针定位, 偏移再映回原文件行号; html 的行号按“标签/注释不切开”的
最小组导出), 排编码区正文、发 DERIV/checks/atoms/条目文件。
正文里每一枚三位以上的数都由 V()/J()/EXPR() 注册过算式; 锚一律由位置导出, 不手打。
锚的归属用两把尺: txt 抛回原文件行(门槛对面就是原文), html 抛回剥标签后的组读数(门槛对面按扩展名剥壳)。"""

# --- SCAN2 BEGIN --- (并键段: 同一段也机械切进 audit.py::_b74_scan)
TAGS = LBL
IDX = dict((t, n) for n, t in enumerate(LBL))
# 门槛对面(audit.py::_atom_face): txt 原样, html 两档(fill 空串⇎空格)并送
FAN = [pnorm(T[i]) if not ISH[i] else pnorm(detag(T[i], u'')) + u' #' + pnorm(detag(T[i], u' '))
       for i in range(NSRC)]
ATOMFAIL = []
# 写正文时的试针开关: 设环境变量 B74PROBE=1 让落空的锚返回标记而不是立刻中断, 一轮把全部缺针看光
PROBE = (u'B74PROBE' in __import__('os').environ)


def tag_groups(t):
    """换行只在标签/注释之外才切开: 返回 [(起行号, 原文片段)]; 片段是剥标签时不可分的最小单元"""
    cuts, i, n = [0], 0, len(t)
    while i < n:
        if t.startswith(u'<!--', i):
            j = t.find(u'-->', i)
            i = n if j < 0 else j + 3
            continue
        if t[i] == u'<':
            j = t.find(u'>', i)
            i = n if j < 0 else j + 1
            continue
        if t[i] == NL:
            cuts.append(i + 1)
        i += 1
    cuts.append(n)
    out, ln = [], 1
    for a, b in zip(cuts, cuts[1:]):
        seg = t[a:b]
        if seg.strip() != u'':
            out.append((ln, seg))
        ln += seg.count(NL)
    return out


GRP = [tag_groups(T[i]) if ISH[i] else [] for i in range(NSRC)]
SHPN = [[(n, x) for n, x in enumerate(L[i], 1) if not is_shell_pick(x)] for i in range(NSRC)]
for i in range(3):
    assert [x for _, x in SHPN[i]] == SHP[i], i
# 组数 ⇎ 非空行数: 差多少行是被标签/注释跨行粘走的
F['grp_n'] = [len(GRP[i]) if ISH[i] else len(SHPN[i]) for i in range(NSRC)]
F['nonblank_pick'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['grp_glued'] = [len([1 for _, x in GRP[i] if NL in x.strip(NL)]) if ISH[i] else 0
                  for i in range(NSRC)]
F['grp_minus_nonblank'] = [F['grp_n'][i] - F['nonblank_pick'][i] for i in range(NSRC)]
# 锚平面: txt=原行逐行(抛回原文), html=组的粘面读数
ALN = [(SHPN[i] if not ISH[i] else
        [(ln, u' '.join(detag(seg, u'').split())) for ln, seg in GRP[i]]) for i in range(NSRC)]
# 窗平面: 与 WIDE 逐字同果的 (行号, 折平片段) 序列
PP = [([(n, u' '.join(x.split())) for n, x in SHPN[i]] if not ISH[i] else
       [(ln, u' '.join(detag(seg, u' ').split())) for ln, seg in GRP[i]]) for i in range(NSRC)]
# 剥空: 只剩标签/注释的行折平后是空串, 留在序列里会让折平多出双空格
PP = [[p for p in pp if p[1] != u''] for pp in PP]
for i in range(NSRC):
    assert u' '.join(x for _, x in PP[i]) == WIDE[i], i


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


def AN(i, *nd):
    for ln, x in ALN[i]:
        p = pnorm(x)
        if all(pnorm(w) in p for w in nd):
            assert p in FAN[i], (LBL[i], x[:60])
            return u'⟦%s⟧⟨%s⟩' % (LBL[i], x)
    ATOMFAIL.append((LBL[i], nd))
    if PROBE:
        return u'⟦%s⟧⟨MISS:%s⟩' % (LBL[i], nd[0][:28])
    raise AssertionError(u'锚导出失败 %s %s' % (LBL[i], nd))


def blk(i, start, end):
    a = WIDE[i].find(start)
    if a < 0:
        raise AssertionError(u'段起针落空 %s %s' % (LBL[i], start))
    b = WIDE[i].find(end, a)
    if b < 0:
        raise AssertionError(u'段止针落空 %s %s' % (LBL[i], end))
    e = b + len(end)
    return u' '.join(WIDE[i][a:e].split()), line_of(i, a), line_of(i, e - 1)


def ln_of(i, nd, frm=0):
    a = WIDE[i].find(nd, frm)
    if a < 0:
        raise AssertionError(u'窗针落空 %s %s' % (LBL[i], nd))
    return a, line_of(i, a)


def ln_end(i, nd, frm=0):
    """短语落在哪一行要看它结束在哪一行: 72 列硬换行会把 “MUST be configurable” 切成两行"""
    a = WIDE[i].find(nd, frm)
    if a < 0:
        raise AssertionError(u'窗针落空 %s %s' % (LBL[i], nd))
    return a, line_of(i, a + len(nd) - 1)


GRP_SH = [len([x for x in L[i] if x.strip() != u'' and is_shell_pick(x)]) for i in range(3)]
F['shell_nonblank_pick'] = GRP_SH + [0, 0]
F['grp_close'] = [F['nonblank_pick'][i] - F['grp_n'][i]
                  - (F['grp_glued'][i] if ISH[i] else F['shell_nonblank_pick'][i])
                  for i in range(NSRC)]


PINS = [(0, u'4yz Transient Negative Completion reply', u'encouraged to try again.'),
        (1, u'The sender MUST delay retrying a particular destination', u'MUST be configurable.'),
        (2, u'The sender MUST delay retrying', u'MUST be configurable.'),
        (3, u'retry_interval_max limits the maximum interval', u'which is its default value.'),
        (4, u'Consider a message as undeliverable', u'the maximal_queue_lifetime limit.'),
        (1, u'Any queueing strategy MUST include', u'in response to error messages.'),
        (2, u'Any queuing strategy MUST include timeouts', u'under any circumstances.'),
        (0, u'It is difficult to assign a meaning', u'must agree on the interpretation.'),
        (3, u'the cutoff time is four days.', u'recipient address that counts.'),
        (4, u'The minimal time between attempts to deliver a deferred message',
         u'destination status cache.'),
        (1, u'Retries continue until the message is transmitted', u'MUST be configurable.'),
        (2, u'Retries continue until the message is transmitted', u'MUST be configurable.')]
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
F['tone_must'] = [ub(p, u'MUST') for p in PTXT]
F['tone_may'] = [ub(p, u'MAY') for p in PTXT]
F['tone_should'] = [ub(p, u'SHOULD') for p in PTXT]
F['tone_must_not_blk'] = [ub(p, u'MUST NOT') for p in PTXT]
F['blk_must_cur'] = [cnt_cur(p, u'MUST') for p in PTXT]
F['blk_must_re'] = [len(re.findall(u'MUST', p)) for p in PTXT]
F['blk_tone_ruler_close'] = (sum(abs(F['tone_must'][n] - F['blk_must_cur'][n]) for n in range(len(PB)))
                             + sum(abs(F['tone_must'][n] - F['blk_must_re'][n]) for n in range(len(PB))))
F['tone_in_blk'] = [F['tone_must'][n] + F['tone_may'][n] + F['tone_should'][n] for n in range(len(PB))]
F['w_only_5321'] = len(set(PW[2]) - set(PW[1]))
F['w_common_12'] = len(set(PW[1]) & set(PW[2]))
F['w_only_1123'] = len(set(PW[1]) - set(PW[2]))
F['w_close_5321'] = F['w_only_5321'] + F['w_common_12'] - F['blk_vocab'][2]
F['w_close_1123'] = F['w_only_1123'] + F['w_common_12'] - F['blk_vocab'][1]
F['w_sym_diff'] = F['w_only_5321'] + F['w_only_1123']


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


F['suf_1123_5321'] = suffix_words(PW[1], PW[2])
F['pre_1123_5321'] = head_words(PW[1], PW[2])
F['suf_queu_1123_5321'] = suffix_words(PW[5], PW[6])
F['pre_queu_1123_5321'] = head_words(PW[5], PW[6])
F['suf_giveup_1123_5321'] = suffix_words(PW[10], PW[11])
F['pre_giveup_1123_5321'] = head_words(PW[10], PW[11])
F['blk_same_1123_5321'] = 1 if PW[1] == PW[2] else 0
F['giveup_sent_same'] = 1 if PTXT[10] == PTXT[11] else 0
F['giveup_chars'] = [len(PTXT[10]), len(PTXT[11])]
F['queu_same'] = 1 if PTXT[5] == PTXT[6] else 0
F['blk_identical_chars'] = 1 if PTXT[1] == PTXT[2] else 0
F['ln_delay_1123'] = ln_of(1, u'The sender MUST delay retrying')[1]
_p_g1 = ln_of(1, u'Retries continue until the message is transmitted', WIDE[1].find(u'The sender MUST delay retrying'))
F['ln_giveup_1123'] = _p_g1[1]
F['ln_conf_head_1123'] = ln_of(1, u'MUST be configurable', _p_g1[0])[1]
F['ln_conf_1123'] = ln_end(1, u'algorithm MUST be configurable.', _p_g1[0])[1]
F['ln_delay_5321'] = ln_of(2, u'The sender MUST delay retrying')[1]
_p_g2 = ln_of(2, u'Retries continue until the message is transmitted', WIDE[2].find(u'The sender MUST delay retrying'))
F['ln_giveup_5321'] = _p_g2[1]
F['ln_conf_head_5321'] = ln_of(2, u'MUST be configurable', _p_g2[0])[1]
F['ln_conf_5321'] = ln_end(2, u'algorithm MUST be configurable.', _p_g2[0])[1]
F['delay_giveup_gap_1123'] = F['ln_giveup_1123'] - F['ln_delay_1123']
F['delay_giveup_gap_5321'] = F['ln_giveup_5321'] - F['ln_delay_5321']
F['giveup_conf_gap_1123'] = F['ln_conf_1123'] - F['ln_giveup_1123']
F['giveup_conf_gap_5321'] = F['ln_conf_5321'] - F['ln_giveup_5321']
F['conf_delay_span_1123'] = F['ln_conf_1123'] - F['ln_delay_1123']
F['conf_delay_span_5321'] = F['ln_conf_5321'] - F['ln_delay_5321']
# 同一枚止针的两把尺: 首字所在行 ⇎ 末字所在行。72 列硬换行会把答案的收束短语切开
F['conf_straddle_1123'] = F['ln_conf_1123'] - F['ln_conf_head_1123']
F['conf_straddle_5321'] = F['ln_conf_5321'] - F['ln_conf_head_5321']
F['ln_hard_821'] = ln_of(0, u'It is difficult to assign a meaning')[1]
F['ln_4yz_821'] = ln_of(0, u'4yz Transient Negative')[1]
F['ln_5yz_821'] = ln_of(0, u'5yz Permanent Negative')[1]
F['ln_thumb_821'] = ln_of(0, u'A rule of thumb')[1]
F['hard_4yz_gap'] = F['ln_hard_821'] - F['ln_4yz_821']
F['yz_gap'] = F['ln_5yz_821'] - F['ln_4yz_821']
F['thumb_hard_gap'] = F['ln_thumb_821'] - F['ln_hard_821']
# 规则串在面上出现多次(示例表也印同一条), 行距要用 “default retry rule:” 提示之后的那一次
_p_rule = WIDE[3].find(u'default retry rule')
F['ln_rule_exim'] = ln_of(3, F['ex_def_rule'], _p_rule)[1]
F['ln_rim_exim'] = ln_of(3, u'retry_interval_max limits')[1]
F['ln_cut_exim'] = ln_of(3, u'the cutoff time is four days.')[1]
F['ln_30min_exim'] = ln_of(3, u'They happen every 30 minutes')[1]
F['rule_prompt_off'] = _p_rule
F['rule_prompt_line'] = line_of(3, _p_rule)
F['rule_prompt_gap'] = F['ln_rule_exim'] - F['rule_prompt_line']
F['rule_first_off'] = WIDE[3].find(F['ex_def_rule'])
F['rule_first_line'] = line_of(3, WIDE[3].find(F['ex_def_rule']))
F['rule_two_lines'] = F['ln_rule_exim'] - F['rule_first_line']
F['rule_rim_gap'] = F['ln_rule_exim'] - F['ln_rim_exim']
F['rim_cut_gap'] = F['ln_cut_exim'] - F['ln_rim_exim']
F['cut_30min_gap'] = F['ln_30min_exim'] - F['ln_cut_exim']
F['cut_30min_abs'] = abs(F['cut_30min_gap'])
_p_mql = ln_of(4, u'Consider a message as undeliverable')
F['ln_mql_pf'] = _p_mql[1]
F['ln_minbo_pf'] = ln_of(4, u'The minimal time between attempts')[1]
F['ln_zero_pf'] = ln_of(4, u'Specify 0 when mail delivery should be tried only once', _p_mql[0])[1]
F['ln_zero_first_pf'] = line_of(4, WIDE[4].find(u'tried only once'))
F['zero_repeats'] = len(re.findall(u'tried only once', WIDE[4]))
F['mql_minbo_gap'] = F['ln_minbo_pf'] - F['ln_mql_pf']
F['zero_mql_gap'] = F['ln_zero_pf'] - F['ln_mql_pf']
F['zero_mql_abs'] = abs(F['zero_mql_gap'])
F['delay_shift_5321'] = F['ln_delay_5321'] - F['ln_delay_1123']
F['giveup_shift_5321'] = F['ln_giveup_5321'] - F['ln_giveup_1123']
F['shift_delta'] = F['delay_shift_5321'] - F['giveup_shift_5321']
F['hi_shift_delay'] = F['blk_hi'][2] - F['blk_hi'][1]
F['hi_shift_giveup'] = F['blk_hi'][11] - F['blk_hi'][10]
F['blk_five_rows'] = sum(F['blk_rows'][:5])
F['blk_rows_tot'] = sum(F['blk_rows'])
F['blk_words_tot'] = sum(F['blk_words'])
ANSET = [set(x for _, x in ALN[i]) for i in range(NSRC)]


def line_holds(i, ln, nd):
    """行号尺复核: 拿行号回原文件取那一行, 看针是否真落在这一行内"""
    for n, x in ALN[i]:
        if n == ln:
            return 1 if pnorm(nd) in pnorm(x) else 0
    raise AssertionError(u'行号无对应原行 %s %d' % (LBL[i], ln))


WRAPND = u'configurable.'
RT = [(1, F['ln_delay_1123'], u'The sender MUST delay retrying'),
      (1, F['ln_giveup_1123'], u'Retries continue until the message'),
      (1, F['ln_conf_1123'], WRAPND),
      (1, F['blk_hi'][1], WRAPND),
      (2, F['ln_delay_5321'], u'The sender MUST delay retrying'),
      (2, F['ln_giveup_5321'], u'Retries continue until the message'),
      (2, F['ln_conf_5321'], WRAPND),
      (2, F['blk_hi'][2], WRAPND),
      (0, F['ln_hard_821'], u'It is difficult to assign a meaning'),
      (0, F['ln_4yz_821'], u'4yz Transient Negative'),
      (0, F['ln_5yz_821'], u'5yz Permanent Negative'),
      (0, F['ln_thumb_821'], u'A rule of thumb')]
F['pin_rt'] = [line_holds(i, ln, nd) for i, ln, nd in RT]
F['pin_rt_n'] = len(F['pin_rt'])
F['pin_rt_ok'] = sum(F['pin_rt'])
F['pin_rt_lbl'] = [LBL[i] for i, _, _ in RT]
F['pin_rt_src'] = [len([1 for i, _, _ in RT if i == n]) for n in range(NSRC)]
# 反向对照: 同一枚短针拿到跨行短语的“首字行”去验, 应当全部落空(行号尺确实分得出首末)
F['pin_wrongline'] = sum([line_holds(1, F['ln_conf_head_1123'], WRAPND),
                          line_holds(2, F['ln_conf_head_5321'], WRAPND)])
# 单位词 “seconds”: RFC 一侧几乎不用, Postfix 的 manpage 离了它不能说话
F['sec_word'] = [cnt_cur(WIDE[i], u'seconds') for i in range(NSRC)]
F['sec_word_rfc'] = sum(F['sec_word'][:3])
CLOSE2 = {}
CLOSE2[u'blk_tone_none_exim_pf'] = 1 if (F['tone_in_blk'][3] == 0 and F['tone_in_blk'][4] == 0) else 0
CLOSE2[u'blk_may_only_5321'] = 1 if (F['tone_may'][2] > 0 and F['tone_may'][1] == 0) else 0
CLOSE2[u'pin_rt_all'] = 1 if F['pin_rt_ok'] == F['pin_rt_n'] else 0
CLOSE2[u'pin_wrap_probe'] = 1 if F['pin_wrongline'] == 0 else 0
CLOSE2[u'sec_only_1123'] = 1 if (F['sec_word_rfc'] == 1 and F['sec_word'][0] == 0
                                 and F['sec_word'][2] == 0 and F['sec_word'][3] == 0) else 0
CLOSE2[u'sec_html_gt_rfc'] = 1 if F['sec_word'][4] > F['sec_word_rfc'] else 0
CLOSE2[u'w_ledger_close'] = 0 if (F['w_close_5321'] or F['w_close_1123']) else 1
CLOSE2[u'blk_5321_longer'] = 1 if F['blk_chars'][2] > F['blk_chars'][1] else 0
CLOSE2[u'exim_rule_after_rim'] = 1 if F['rule_rim_gap'] > 0 else 0
CLOSE2[u'exim_rule_after_prompt'] = 1 if F['rule_prompt_gap'] > 0 else 0
CLOSE2[u'exim_rule_reprinted'] = 1 if F['rule_two_lines'] > 0 else 0
CLOSE2[u'hard_before_thumb_821'] = 1 if F['thumb_hard_gap'] > 0 else 0
CLOSE2[u'zero_after_mql_pf'] = 1 if F['zero_mql_gap'] > 0 else 0
CLOSE2[u'grp_ledger_close'] = 0 if sum(abs(x) for x in F['grp_close']) else 1
CLOSE2[u'giveup_inside_delay'] = 1 if (F['blk_lo'][10] > F['blk_lo'][1] and F['blk_lo'][11] > F['blk_lo'][2]) else 0
CLOSE2[u'queu_before_delay'] = 1 if (F['blk_lo'][5] < F['blk_lo'][1] and F['blk_lo'][6] < F['blk_lo'][2]) else 0
CLOSE2[u'exim_rim_before_four'] = 1 if (F['blk_lo'][3] < F['blk_lo'][8] and F['rule_prompt_line'] < F['ln_cut_exim']) else 0
CLOSE2[u'pf_mql_before_minbo'] = 1 if (F['blk_lo'][4] < F['blk_lo'][9] and F['mql_minbo_gap'] > 0) else 0
CLOSE2[u'blk_shift_equal'] = 1 if F['delay_shift_5321'] == F['giveup_shift_5321'] else 0
F.update(CLOSE2)
# --- SCAN2 END ---

# ---------- ZV 追加: 段落层的恒等式 ----------
ZV.append((u"B74V('w_close_5321') + B74V('w_close_1123')",
           u'两份答段的词集容斥各自归零: 相对另一份独有 + 交集 = 本段词表'))
ZV.append((u"B74V('w_sym_diff') - B74V('w_only_1123') - B74V('w_only_5321')",
           u'对称差的第二种走法: 两侧独有相加'))
ZV.append((u"B74V('pin_rt_ok') - B74V('pin_rt_n')",
           u'行号尺复核: 段窗首末行⇎独立行针报出的行号, 逐枚回原文件那一行自验'))
ZV.append((u"B74V('pin_wrongline')",
           u'反向对照: 跨行短语的末字拿到它的首字行去验, 两份都该落空'))
ZV.append((u"B74V('conf_straddle_1123') + B74V('conf_straddle_5321') - 2",
           u'两份 RFC 都把答案的收束短语切成两行: 首字行⇎末字行各差一行'))
ZV.append((u"B74V('shift_delta') - 1",
           u'“下限段”比“给弃段”多后移一行: 5321 不是整段平移, 段幅本身也长了一行'))
ZV.append((u"B74V('blk_tone_ruler_close')",
           u'段语气三把尺同值: 手扫邻居字符 ⇎ 非重叠游标 ⇎ 正则'))
ZV.append((u"sum([B74V('grp_close', i) for i in range(5)])",
           u'组面⇎非空行⇎(跨行组|壳行) 三本账五份相加归零'))
ZV.append((u"B74V('cut_30min_gap') + B74V('cut_30min_abs')",
           u'Exim “四日段→30 分钟段”是负距离(30 分钟那条印在四日段之前), 带签名⇎绝对值'))
ZV.append((u"B74V('zero_mql_gap') - B74V('zero_mql_abs')",
           u'Postfix “0=只试一次”排在 undeliverable 段之后, 带签名⇎绝对值'))
ZV.append((u"B74V('queu_before_delay') + B74V('giveup_inside_delay') - 2",
           u'两份 RFC 里队列超时清单都排在重试下限之前, 给弃句都落在下限段之内'))
ZV.append((u"B74V('exim_rim_before_four') + B74V('pf_mql_before_minbo') - 2",
           u'Exim 封顶段在四日段之前 ⇎ Postfix undeliverable 段在 minimal_backoff 段之前'))
ZV.append((u"B74V('blk_tone_none_exim_pf') - 1",
           u'两份 MTA 的答段一枚义务词也没有'))
ZV.append((u"B74V('tone_in_blk', 0) + B74V('tone_in_blk', 7)",
           u'821 的两段答句同样零义务词(它全份大写 MUST 亦为零)'))
ZV.append((u"B74V('blk_may_only_5321') - 1",
           u'MAY 只在 5321 的答段里出现(“MAY be appropriate to make fewer”), 1123 同段零枚'))
ZV.append((u"B74V('exim_rule_after_prompt') - 1",
           u'默认规则串印在 “default retry rule:” 提示之后, 行距为正'))
ZV.append((u"B74V('grp_glued', 3)",
           u'Exim 一枚跨行组也没有: 它的换行全在标签之外, 组面恒等于非空行数'))
ZV.append((u"B74V('hi_shift_delay') - B74V('hi_shift_giveup')",
           u'两份答段的“止行距”相等(5321 的两段都比 1123 同段晚这么多行)'))
ZV.append((u"B74V('hi_shift_delay') - B74V('delay_shift_5321') - 1",
           u'止行距−起行距=1 行: 差的正是 5321 下限段长出的那一行'))

for v, w in ZV:
    if eval(v, {FN: BB74}) != 0:
        raise AssertionError(u'恒等式不为零: ' + w + u' |' + v + u'|')

PAIRLBL = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in IT.combinations(range(NSRC), 2)]
PLBL = [u'%s#%d' % (LBL[i], n + 1) for n, (i, s, e) in enumerate(PINS)]


def P10(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, PAIRLBL[i])) for i in range(10))


def PJ(name, note=u''):
    return u' ⇎ '.join(V(name, n, u'%s·%s' % (note or name, PLBL[n])) for n in range(len(PINS)))


def NKL(keys):
    return u' '.join(k[1:] if k[:1] in (u'a', u'n') else k for k in keys)


LINES = []
LINES.append(
    u'📜 五份先按版式分家: 三份 RFC 是 RFC Editor 纯文本面 ⇎ 两份 MTA 文档是 HTML 页。'
    + u' 字节 ' + J(u'bytes', u'字节') + u', 面内码位 ' + J(u'chars', u'码位') + u', 原行 '
    + J(u'lines', u'原行') + u' ⇎ 非空行 ' + J(u'nonblank', u'非空行') + u', 最长行 '
    + J(u'maxlen', u'最长行') + u' 列——前三份同为 ' + V(u'maxlen', 0, u'最长行·821') + u' 列硬换行, '
    + u'两份 MTA 各 ' + V(u'maxlen', 3, u'最长行·exim') + u'/' + V(u'maxlen', 4, u'最长行·postfix')
    + u' 列。 全库回车 ' + J(u'cr', u'CR') + u' 枚 ⇎ NUL ' + J(u'nul', u'NUL') + u' 枚 ⇎ BOM '
    + J(u'bom', u'BOM') + u' 枚; 非 ASCII 码位 ' + J(u'nonascii', u'非ASCII') + u' 枚, '
    + u'字节−码位差 ' + J(u'byte_cp_delta', u'字节减码位') + u'(UTF-8 多字节所致, 三份 RFC 恒零)。 '
    + u'换页符独占整行 ' + J(u'ff_exact', u'换页独占行') + u' 行 ⇎ 建条目侧另按 strip()==换页符 判, '
    + u'该档 ' + J(u'ff_only', u'换页strip档') + u' 行——strip 先吃掉换页符本身, 这一档在什么面上都是零(口径陷阱如实记)。 '
    + u'splitlines 行 ' + J(u'lines_split', u'splitlines') + u' ⇎ 换行计数 ' + J(u'lines_nl', u'换行档')
    + u', 差额由换页符补上(闭合 ' + V(u'lines_split_close', None, u'行数闭合') + u', 判定 '
    + V(u'split_tail_close', None, u'行数账零') + u')。 '
    + u'两份 HTML 的开标签 ' + J(u'tag_open', u'开标签') + u' ⇎ 闭标签 ' + J(u'tag_close', u'闭标签')
    + u', Postfix 一页 ' + V(u'tag_tot', 4, u'标签合计·postfix') + u' 枚里 <br> 独占 '
    + V(u'br_tag', 4, u'br 枚·postfix') + u' 枚; 实体 exim ' + V(u'ent_total', 3, u'实体·exim')
    + u' ⇎ postfix ' + V(u'ent_total', 4, u'实体·postfix') + u', 其中数字实体剥后仍留 '
    + V(u'ent_numeric_left', 4, u'数字实体残留·postfix') + u' 枚(只在此侧), '
    + u'双逃 &amp; 由 ' + V(u'ent_amp_raw', 4, u'amp 原枚·postfix') + u' 枚吃到剩 '
    + V(u'ent_double_left', 4, u'双逃残留·postfix') + u' 枚 ⇎ exim 剩 ' + V(u'ent_double_left', 3, u'双逃残留·exim')
    + u' 枚(单趟实体表吃干净)。 单位行在此 ' + AN(4, u'Time units: s (seconds)') + u', 那句下限在彼 '
    + AN(1, u'SHOULD be at least 30 minutes') + u'。')

LINES.append(
    u'🪜 五档口径逐份换尺(逐行 ⇎ 折平 ⇎ 摘壳 ⇎ 断面 ⇎ 粘面), 名下针读到的枚数: 逐行 '
    + J(u'sn_strict_docs', u'逐行档') + u' ⇎ 折平 ' + J(u'sn_fold_docs', u'折平档') + u' ⇎ 摘壳 '
    + J(u'sn_sh_docs', u'摘壳档') + u' ⇎ 断面 ' + J(u'sn_ds_docs', u'断面档') + u' ⇎ 粘面 '
    + J(u'sn_dj_docs', u'粘面档') + u'。 折行一次救回 ' + V(u'fold_minus_strict_n', None, u'折行独有针')
    + u' 枚, 按份 ' + J(u'fold_minus_strict_own', u'折行独有') + u'(txt 的 ' + V(u'needle_n', None, u'针总数')
    + u' 枚针里有 ' + V(u'fold_minus_strict_n', None, u'折行独有') + u' 枚跨行, 一枚不剩地全落在换行口径上); '
    + u'摘壳一枚不丢(' + J(u'sh_minus_fold', u'摘壳减折平') + u'), 因为答句不在页壳里。 '
    + u'剥标签新开 ' + V(u'ds_only_n', None, u'断面独有针') + u' 枚: ' + NKL(F[u'ds_only_keys'])
    + u', 按份 ' + J(u'ds_only_own', u'断面独有') + u'; 换成“标签替空串”的粘法又多 '
    + V(u'dj_only_n', None, u'粘面独有针') + u' 枚(' + NKL(F[u'dj_only_keys']) + u'), '
    + u'同时丢掉 ' + V(u'ds_no_dj_n', None, u'断面有粘面无') + u' 枚(' + NKL(F[u'ds_no_dj_keys']) + u')——'
    + u'锚候选面取的是“标签替空串”的粘法 ' + AN(3, u'<letter>,<cutoff time>') + u', 同一串在断面档读法为 '
    + V(u'n_aexim_bond_ds', 3, u'尖括号·断面档枚') + u' ⇎ 粘面档 ' + V(u'n_aexim_bond_dj', 4, u'尖括号·粘面档枚')
    + u' 枚, 算法字母同理 ' + V(u'n_aexim_F_ds', 3, u'字母F·断面档枚')
    + u' ⇎ ' + V(u'n_aexim_F_dj', 4, u'字母F·粘面档枚') + u' 枚 ⇎ ' + AN(3, u'F: retry at fixed intervals') + u'。 '
    + u'两档换尺的进出账在 Exim 一侧 ' + V(u'sn_dj_docs', 3, u'粘面·exim') + u'−' + V(u'sn_ds_docs', 3, u'断面·exim')
    + u'=' + V(u'sn_dj_minus_ds', 3, u'粘减断·exim') + u' 枚。 死集 ' + V(u'dead_needles_none', None, u'死针账零')
    + u'(落空清单 ' + NKL(F[u'dead_needles']) + u'), 反向对照 ' + V(u'neg_n', None, u'反向针数') + u' 枚'
    + u'(' + J(u'neg_own', u'反向按份') + u')最宽档合计命中 ' + V(u'neg_hit_widest', None, u'反向最宽命中')
    + u' 枚; 名下针 ' + J(u'needles_owned', u'名下针') + u' 枚。')

LINES.append(
    u'🔤 十二族措辞针(每族一条字面串)在最宽档的枚数 ⇎ 折平档: ' + J(u'tier_tot', u'措辞最宽档') + u' ⇎ '
    + J(u'tier_fold_tot', u'措辞折平档') + u', 族名 ' + u' '.join(F[u'tier_words']) + u'; '
    + u'命中的族数 ' + J(u'tier_hit_fams', u'命中族数') + u' ⇎ 零枚的族数 ' + J(u'tier_zero_fams', u'空族数')
    + u'。 唯一在折平⇎剥后之间掉枚数的是 Postfix: ' + V(u'tier_fold_tot', 4, u'折平·postfix') + u' ⇎ '
    + V(u'tier_tot', 4, u'剥后·postfix') + u', 差 ' + V(u'tier_wide_minus_fold', 4, u'折平减剥后·postfix')
    + u' 枚——默认值成对印在目录项的 title 属性里(“' + V(u'pf_default_in_tag', None, u'属性内默认值参数数')
    + u'”个参数各少一枚), 整页加法 ' + V(u'pf_nd_default_all', None, u'default全枚') + u' 枚 = 标签区间内 '
    + V(u'pf_nd_default_tag', None, u'default标签内') + u' + 剥后剩余 ' + V(u'pf_nd_default_dj', None, u'default剥后')
    + u'。 其余四份这一档纹丝不动(' + J(u'tier_wide_minus_fold', u'折平减剥后') + u')。 '
    + u'措辞本身也是答案的形状: 821 只会说“' + AN(0, u'encouraged to try again') + u'”, '
    + u'1123 给出下限与给弃窗 ' + AN(1, u'least 4-5 days') + u' ⇎ 5321 在同一段里补一句可少试 '
    + AN(2, u'MAY be appropriate') + u', Exim 不谈义务只谈上限 ' + AN(3, u'retry_interval_max limits')
    + u', Postfix 把放弃写成一条参数说明 ' + AN(4, u'Consider a message as undeliverable') + u'。')

LINES.append(
    u'¶ 答段对照(段界只在各份最宽档按字面针定位, 行号映回原文件; 共 %d 段): 起行 %s ⇎ 止行 %s ⇎ 行数 %s ⇎ 字符 %s ⇎ 词 %s。'
    % (len(PINS), PJ(u'blk_lo', u'段起行'), PJ(u'blk_hi', u'段止行'), PJ(u'blk_rows', u'段行数'),
       PJ(u'blk_chars', u'段字符'), PJ(u'blk_words', u'段词数'))
    + u' 五段主答句合计 ' + V(u'blk_five_chars', None, u'主段字符合计') + u' 字符⇎'
    + V(u'blk_five_words', None, u'主段词合计') + u' 词, 十二段合计 ' + V(u'blk_rows_tot', None, u'十二段行')
    + u' 行⇎' + V(u'blk_words_tot', None, u'十二段词') + u' 词。 '
    + u'1123 的下限段 ' + V(u'blk_chars', 1, u'字符·1123段') + u' 字符⇎' + V(u'blk_rows', 1, u'行·1123段')
    + u' 行, 5321 把同一段搬到协议标准里涨到 ' + V(u'blk_chars', 2, u'字符·5321段') + u' 字符⇎'
    + V(u'blk_rows', 2, u'行·5321段') + u' 行(判定 ' + V(u'blk_5321_longer', None, u'5321段更长') + u'), '
    + u'起首一句两份各为 ' + AN(1, u'The sender MUST delay retrying') + u' ⇎ '
    + AN(2, u'The sender MUST delay retrying') + u', 同头而异尾。 '
    + u'两份的行号位移: 下限段后移 ' + V(u'delay_shift_5321', None, u'下限段位移') + u' 行⇎给弃段后移 '
    + V(u'giveup_shift_5321', None, u'给弃段位移') + u' 行, 差 ' + V(u'shift_delta', None, u'位移差')
    + u' 行——不是整段平移, 段幅本身也长了(判定 ' + V(u'blk_shift_equal', None, u'位移等值') + u'); '
    + u'两段的止行距反而相等: ' + V(u'hi_shift_delay', None, u'止行距·下限段') + u' ⇎ '
    + V(u'hi_shift_giveup', None, u'止行距·给弃段') + u' 行, 止行距−起行距='
    + EXPR(F[u'hi_shift_delay'] - F[u'delay_shift_5321'],
            u"B74V('hi_shift_delay') - B74V('delay_shift_5321')", u'止行距减去行距') + u' 行。 '
    + u'段内行距: 1123 ' + V(u'delay_giveup_gap_1123', None, u'下限→给弃·1123') + u'/'
    + V(u'giveup_conf_gap_1123', None, u'给弃→可配·1123') + u' ⇎ 5321 '
    + V(u'delay_giveup_gap_5321', None, u'下限→给弃·5321') + u'/' + V(u'giveup_conf_gap_5321', None, u'给弃→可配·5321')
    + u' 行; 行号尺复核: 段窗首末行⇎独立行针共 ' + V(u'pin_rt_n', None, u'行针复核枚') + u' 枚'
    + u'(821/1123/5321 各 ' + V(u'pin_rt_src', 0, u'行针枚·821') + u'/' + V(u'pin_rt_src', 1, u'行针枚·1123')
    + u'/' + V(u'pin_rt_src', 2, u'行针枚·5321') + u' 枚), 拿行号回原文件取那一行逐枚自验, 命中 '
    + V(u'pin_rt_ok', None, u'行针自验枚') + u' 枚(判定 ' + V(u'pin_rt_all', None, u'行针复核判定') + u'); '
    + u'反向对照: 1123 的首字行正好停在 ' + AN(1, u'algorithm MUST') + u' 的 MUST 上, '
    + u'5321 的末字行独占一行 ' + AN(2, u'configurable.')
    + u'; 把 “configurable.” 拿到首字行去验, 两份全落空(命中 ' + V(u'pin_wrongline', None, u'错行验中枚')
    + u' 枚, 判定 ' + V(u'pin_wrap_probe', None, u'错行对照判定') + u')——72 列硬换行正切在答案的收束短语里, '
    + u'两刀落点还不同(1123 切在 MUST 之后⇎5321 切在 be 之后): 首字行⇎末字行差 '
    + V(u'conf_straddle_1123', None, u'跨行·1123') + u' ⇎ '
    + V(u'conf_straddle_5321', None, u'跨行·5321') + u' 行。 '
    + u'821 的定义⇎难点⇎经验法则三针 ' + AN(0, u'4yz Transient Negative') + u' / ' + AN(0, u'difficult to assign a')
    + u' / ' + AN(0, u'A rule of thumb') + u' 相距 ' + V(u'yz_gap', None, u'4yz→5yz行距') + u'⇎'
    + V(u'hard_4yz_gap', None, u'难点→4yz行距') + u'⇎' + V(u'thumb_hard_gap', None, u'难点→thumb行距')
    + u' 行(判定 ' + V(u'hard_before_thumb_821', None, u'难点先于法则') + u'), 其后另起一段 '
    + AN(0, u'5yz Permanent Negative') + u'。 两份都把这一节回指给自己: '
    + AN(1, u'Retry messages after soft failure') + u' ⇎ ' + AN(2, u'discussed in Section 4.5.4.1') + u'。')

LINES.append(
    u'⇄ 词集账(1123 段 ⇎ 5321 段): 1123 独有 ' + V(u'w_only_1123', None, u'1123段独词') + u' 词 ⇎ 5321 独有 '
    + V(u'w_only_5321', None, u'5321段独词') + u' 词 ⇎ 共有 ' + V(u'w_common_12', None, u'两段共词')
    + u' 词, 对称差 ' + V(u'w_sym_diff', None, u'词对称差') + u' 词; 各自容斥归零(判定 '
    + V(u'w_ledger_close', None, u'词集账零') + u')。 同段共头 ' + V(u'pre_1123_5321', None, u'段共头词')
    + u' 词⇎共尾 ' + V(u'suf_1123_5321', None, u'段共尾词') + u' 词 ⇎ 词序全同 '
    + V(u'blk_same_1123_5321', None, u'段词序全同') + u' ⇎ 字符全同 ' + V(u'blk_identical_chars', None, u'段字符全同')
    + u'——搬的是同一句话, 但两头都不齐: 开头 ' + V(u'pre_1123_5321', None, u'段共头词')
    + u' 词逐字同, 结尾 ' + V(u'suf_1123_5321', None, u'段共尾词') + u' 词同, 中间被改写。 '
    + u'给弃句一档更细: ' + V(u'giveup_chars', 0, u'给弃句·1123字符') + u' ⇎ '
    + V(u'giveup_chars', 1, u'给弃句·5321字符') + u' 字符, 共头 ' + V(u'pre_giveup_1123_5321', None, u'给弃共头')
    + u' 词⇎共尾 ' + V(u'suf_giveup_1123_5321', None, u'给弃共尾') + u' 词⇎同句 '
    + V(u'giveup_sent_same', None, u'给弃句全同') + u'; 队列清单那句只剩共头 '
    + V(u'pre_queu_1123_5321', None, u'队列共头') + u' 词⇎共尾 ' + V(u'suf_queu_1123_5321', None, u'队列共尾')
    + u' 词(' + V(u'queu_same', None, u'队列句全同') + u' 全同)——术语换代从这一句开始: '
    + AN(1, u'Any queueing strategy MUST include') + u' ⇎ ' + AN(2, u'Any queuing strategy MUST include') + u'。 '
    + u'两把尺下的搬字量: 行尺共用长行 1123·5321 ' + V(u'pair_1123_5321', None, u'共用行·1123·5321')
    + u' 条, 换成句尺 ' + V(u's_pair_1123_5321', None, u'共用句·1123·5321') + u' 条, 增益 '
    + V(u's_ruler_gain_1123_5321', None, u'句尺增益·1123·5321') + u' 条(72 列硬换行把同一句切成多行)。')

LINES.append(
    u'🎚 语气五轨(全篇, 大写五轨按“MUST NOT ⇎ MUST ⇎ SHOULD NOT ⇎ SHOULD ⇎ MAY”手扫邻居字符, 与正则尺逐轨同值): '
    + J(u'tone_MUST_NOT', u'MUST NOT') + u' ⇎ ' + J(u'tone_MUST', u'MUST') + u' ⇎ '
    + J(u'tone_SHOULD_NOT', u'SHOULD NOT') + u' ⇎ ' + J(u'tone_SHOULD', u'SHOULD') + u' ⇎ '
    + J(u'tone_MAY', u'MAY') + u'; 合计 ' + J(u'tone_tot', u'语气合计') + u' 枚, '
    + u'裸 MUST = 全 MUST − MUST NOT ' + J(u'must_bare', u'裸MUST') + u'(判定 ' + V(u'tone_ledger', None, u'语气账零') + u'), '
    + u'小写 must 另有 ' + J(u'tone_must_lc', u'小写must') + u' 枚。 '
    + u'零枚大写 MUST 的恰是 821 与 Exim 两份(判定 ' + V(u'tone_zero_must_pair', None, u'零MUST两份') + u'), '
    + u'而 821 的小写 must 有 ' + V(u'tone_must_lc', 0, u'小写must·821') + u' 枚——它不是不用语气, 是不用规范语气。 '
    + u'答段内部的语气与全篇成反比: 段内 MUST ' + PJ(u'tone_must', u'段MUST') + u' ⇎ 段内 MAY '
    + PJ(u'tone_may', u'段MAY') + u' ⇎ 段内 SHOULD ' + PJ(u'tone_should', u'段SHOULD') + u', '
    + u'两份 MTA 段内三轨全零(判定 ' + V(u'blk_tone_none_exim_pf', None, u'MTA段零语气') + u'), '
    + u'5321 段内的 MAY 是唯一的一枚(判定 ' + V(u'blk_may_only_5321', None, u'MAY只在5321段') + u')。 '
    + u'术语换代可量: sender-SMTP ' + J(u'sender_smtp', u'sender-SMTP') + u' ⇎ receiver-SMTP '
    + J(u'receiver_smtp', u'receiver-SMTP') + u' ⇎ SMTP client ' + J(u'smtp_client', u'SMTP client')
    + u' 枚; queue 一词 ' + J(u'queue_word', u'queue词') + u' ⇎ retry 族 ' + J(u'retry_word', u'retry词')
    + u' ⇎ timeout ' + J(u'word_timeout', u'timeout词') + u' 枚; 两段各自的开场定义句也换了主语 '
    + AN(1, u'The general model of a sender-SMTP') + u' ⇎ ' + AN(2, u'The general model for an SMTP client')
    + u'。 新名在“新名+旧名”里占的千分位 '

    + J(u'term_new_per_mille', u'新名千分') + u'。 queueing⇎queuing 两种拼法 '
    + J(u'spelling_queueing', u'queueing') + u' ⇎ ' + J(u'spelling_queuing', u'queuing') + u' 枚。')

LINES.append(
    u'⏱ 换算表(%d 档, 全为秒): ' % len(F[u'cv_sec']) + u' ⇎ '.join(str(x) for x in F[u'cv_sec'])
    + u' ⇎ ' + u' ⇎ '.join(F[u'cv_names']) + u'。 1123/5321 的下限 ' + V(u'cv_floor', None, u'下限秒')
    + u' 秒 = ' + V(u'cv_floor_minus_exim', None, u'下限减exim首档') + u' + Exim 首档 '
    + V(u'ex_def_first', 0, u'exim首档') + u' 秒 ⇎ ' + V(u'cv_floor_minus_pf', None, u'下限减postfix')
    + u' + Postfix 的 ' + V(u'pf_def_sec', 2, u'postfix minimal_backoff') + u' 秒; 换算成倍率 '
    + V(u'cv_ratio_exim_vs_floor', None, u'exim千分比') + u' ⇎ ' + V(u'cv_ratio_pf_vs_floor', None, u'pf千分比')
    + u'(即 15m 是下限的 1/2, 300s 是下限的 1/6)。 低于下限的档位 ' + V(u'cv_below_n', None, u'低于下限档')
    + u' 档 ⇎ 不低于 ' + V(u'cv_above_n', None, u'不低于下限档') + u' 档, 相加=表长 '
    + V(u'cv_close', None, u'换算表闭合') + u'; 低的那 ' + V(u'cv_below_n', None, u'低于下限档') + u' 档是 '
    + u' '.join(str(x) for x in F[u'cv_below']) + u'。 单位词 “seconds” 在三份 RFC 里合计只 '
    + V(u'sec_word_rfc', None, u'seconds词·RFC合计') + u' 枚, 且一枚也不在 5321(判定 '
    + V(u'sec_only_1123', None, u'seconds只在1123') + u'): ' + AN(1, u'no less than 5 seconds')
    + u'; 5321 不写这个单位词, 它在同一节里多立的是一条与时长无关的禁令 '
    + AN(2, u'MUST NOT be cached') + u'。 另一侧 Postfix 的这页 manpage 写了 '
    + V(u'sec_word', 4, u'seconds词·postfix') + u' 枚(判定 ' + V(u'sec_html_gt_rfc', None, u'seconds多于RFC')
    + u')。 给弃窗两端: 4 天=' + V(u'band_lo', None, u'区间下沿')
    + u' ⇎ 5 天=' + V(u'band_hi', None, u'区间上沿') + u' 秒, ' + V(u'day_sec', None, u'日的秒数')
    + u' 秒/日; 两份 MTA 的默认各踩住一端(命中 ' + V(u'band_edge_hits', None, u'区间端点命中') + u' 处, 判定 '
    + V(u'ex_cutoff_in_band', None, u'exim在区间内') + u'/' + V(u'pf_life_in_band', None, u'pf在区间内') + u')。 '
    + u'Exim 默认规则串 ' + AN(3, F[u'ex_def_rule']) + u' 现分成 ' + V(u'ex_def_sets', None, u'默认规则段数')
    + u' 段(字母 ' + u''.join(F[u'ex_def_letters']) + u', 文档另定义 ' + u''.join(F[u'ex_letters_def'])
    + u' 三种, 差 ' + V(u'ex_letters_def_only', None, u'定义未用字母数') + u' 枚即 '
    + u''.join(F[u'ex_letters_def_only']) + u'), 段跨度 ' + u' '.join(str(x) for x in F[u'ex_sched_sec'])
    + u' 秒, 档数 ' + V(u'ex_attempts_tot', None, u'exim总档数') + u' 档('
    + u'⇎'.join([str(F[u'ex_f1_attempts']), str(F[u'ex_def_args'][1]), str(F[u'ex_f3_attempts'])])
    + u'), 其中几何段 ' + V(u'ex_g_steps', None, u'G段档数') + u' 档倍数 '
    + u' '.join(str(x) for x in F[u'ex_def_mults']) + u' 共 ' + V(u'ex_g_total', None, u'G段总秒')
    + u' 秒; 封顶 ' + V(u'ex_rim_cap', None, u'exim封顶秒') + u' 秒⇎截止 ' + V(u'ex_def_span', None, u'exim末段跨度')
    + u' 秒⇎过期 ' + V(u'ex_expire_days', None, u'exim过期秒') + u' 秒, 而“从何时起算”另有一句 '
    + AN(3, u'cutoff time is measured') + u'。 Postfix 六参数默认 '
    + u' ⇎ '.join(F[u'pf_def_tok']) + u' = 秒 ' + u' '.join(str(x) for x in F[u'pf_def_sec'])
    + u'(队列寿命⇎回弹寿命同值判定 ' + V(u'pf_bql_eq_mql', None, u'bql等于mql') + u', '
    + V(u'pf_def_sec', 2, u'postfix minimal_backoff') + u'⇎' + V(u'pf_def_sec', 4, u'postfix queue_run_delay')
    + u' 同值判定 ' + V(u'pf_ge_minbo', None, u'maxbo大于minbo') + u'); 这条参数在 manpage 里的定义句是 '
    + AN(4, u'The minimal time between attempts') + u'。')

LINES.append(
    u'🌿 谱系与年代: 抬头年份 ' + J(u'years', u'抬头年') + u', 相邻年距 '
    + u' ⇎ '.join(str(x) for x in F[u'year_gaps']) + u' 年, 首末跨 ' + V(u'year_span', None, u'年跨度')
    + u' 年(判定 ' + V(u'year_monotone', None, u'年份单调') + u')。 动作头: 5321 一句 '
    + AN(2, u'Obsoletes: 2821') + u' ⇎ 一句 ' + AN(2, u'Updates: 1123') + u', 821 一行 '
    + AN(0, u'Replaces: RFC 788') + u' 废止清单 ' + V(u'obs_n', 2, u'Obsoletes数·5321') + u'⇎更新清单 '
    + V(u'upd_n', 2, u'Updates数·5321') + u'⇎替代清单 ' + V(u'repl_n', 0, u'Replaces数·821')
    + u' 行, 对象并集 ' + u' '.join(str(x) for x in F[u'target_ids']) + u' 共 ' + V(u'target_n', None, u'对象并集数')
    + u' 个(无重叠)。 引用三式并计(空格⇎连写⇎短横, 账逐份归零 ' + V(u'cite_forms_close', 0, u'引用闭合·821')
    + u'): 821 自引 ' + V(u'cite_self', 0, u'自引·821') + u' 枚全为空格式 ' + V(u'cite_sp_821', 0, u'空格式自引·821')
    + u', 1123 自引 ' + V(u'cite_self', 1, u'自引·1123') + u' 枚全为连写 ' + V(u'cite_tk_1123', 1, u'连写式·1123')
    + u' 枚, 5321 自引 ' + V(u'cite_self', 2, u'自引·5321') + u'; 关键不对称: 1123 面上 “RFC 821” 空格式 '
    + V(u'cite_821_in_1123', None, u'空格式821在1123') + u' 枚 ⇎ 短横式 “RFC-821” '
    + V(u'cite_821_hy_in_1123', None, u'短横式821在1123') + u' 枚(判定 ' + V(u'cite_hy_only_1123', None, u'短横独有')
    + u'), 三式相加 ' + V(u'cite_821_3f_in_1123', None, u'三式和·1123引821') + u' 枚; 5321 面上引 821 '
    + V(u'cite_821_in_5321', None, u'821在5321') + u' 枚、引 1123 ' + V(u'cite_1123_in_5321', None, u'1123在5321')
    + u' 枚、引 2821 共 ' + V(u'cite_2821_tot', None, u'2821合计') + u' 枚; '
    + u'两份 MTA 面上 RFC 字样 ' + V(u'cite_rfc_word', 3, u'RFC字样·exim') + u'/' + V(u'cite_rfc_word', 4, u'RFC字样·postfix')
    + u' 处, 自引 ' + V(u'cite_self', 3, u'自引·exim') + u' 枚——它们引用的是协议, 不是自己。')

LINES.append(
    u'🧵 两把尺量搬字: 行尺(共用长行池, 只在 txt 三张面之间) ' + V(u'pool_n', None, u'行池条数') + u' 条, '
    + u'按共用份数分档 ' + JL(u'pool_tier', u'行池分档') + u' ⇎ 容斥并集闭合 ' + V(u'union_close', None, u'行池容斥闭合')
    + u'; 两两共用 ' + P10(u'pair_share', u'共用行') + u' 条, 最大一对 ' + F[u'pair_max_lbl'] + u' '
    + V(u'pair_max', None, u'最大共用行') + u' 条, 其中逐字节同 ' + V(u'pair_max_byte', None, u'最大逐字节同')
    + u' 条⇎只归一同 ' + V(u'pair_max_norm_only', None, u'最大只归一同') + u' 条(全池只归一同 '
    + V(u'shared_norm_only', None, u'只归一同合计') + u' 条, 判定 ' + V(u'pair_close', None, u'共用行账零') + u')。 '
    + u'写法分家四桶 ' + F[u'axis_str'] + u', 合计 ' + V(u'axis_total', None, u'分家合计') + u' = 去重串数 '
    + V(u'norm_only_set', None, u'只归一集合数') + u'(闭合 ' + V(u'axis_close', None, u'分家闭合') + u')。 '
    + u'句尺(共用句池, 五份都算): ' + V(u's_pool_n', None, u'句池条数') + u' 句, 分档 '
    + JL(u's_pool_tier', u'句池分档') + u', 两两共用 ' + P10(u's_pair_share', u'共用句') + u' 句, 最大一对 '
    + F[u's_pair_max_lbl'] + u' ' + V(u's_pair_max', None, u'最大共用句') + u' 句, 对 821·5321⇎1123·5321 的增益 '
    + V(u's_ruler_gain_821_5321', None, u'句尺增益·821·5321') + u'⇎' + V(u's_ruler_gain_1123_5321', None, u'句尺增益·1123·5321')
    + u' 句(判定 ' + V(u'head_pair', None, u'821节尺两份') + u')。 两份 MTA 与三份 RFC 之间共用句 '
    + V(u's_pair_html', None, u'HTML零共用句') + u' 句 ⇎ 共用行 ' + V(u'pool_html_shared', None, u'HTML共用行')
    + u' 行, 各自内部也只 ' + V(u'pool_txt_shared', None, u'txt共用行') + u' 行——同一句话在 RFC 与 MTA 文档里从来没有同形过。 '
    + u'锚候选池(把每份的面按行切开归一) ' + V(u'apool_n', None, u'锚池条数') + u' 条 ⇎ 原行 '
    + V(u'apool_raw_n', None, u'锚池原行') + u' 行, 分档 ' + JL(u'apool_tier', u'锚池分档') + u', 加权闭合 '
    + V(u'apool_tier_close', None, u'锚池加权闭合') + u'。')

LINES.append(
    u'🧱 组面⇎壳账: 门槛对面按扩展名分派(txt 原样 ⇎ html 剥标签两档), 本遍因此为 html 另立“组面”——'
    + u'换行只在标签与注释之外才切开, 组数 ' + J(u'grp_n', u'组数') + u' ⇎ 非空行 ' + J(u'nonblank_pick', u'非空行·组面尺')
    + u', 差 ' + J(u'grp_minus_nonblank', u'组减非空行') + u' 行: txt 一侧差的是页壳行 '
    + J(u'shell_nonblank_pick', u'壳非空行') + u', html 一侧差的是被标签跨行粘走的 '
    + J(u'grp_glued', u'跨行组') + u' 组(Postfix ' + V(u'grp_glued', 4, u'跨行组·postfix') + u' 组⇎Exim '
    + V(u'grp_glued', 3, u'跨行组·exim') + u' 组)。 三本账逐份相加归零 ' + J(u'grp_close', u'组面闭合') + u'。 '
    + u'两遍壳谓词(采集⇎本遍照抄)横比先分解到行: 本遍 ' + J(u'shell_n', u'壳行·本遍') + u' ⇎ 采集 '
    + J(u'shell_pick', u'壳行·采集') + u', 本遍多判 ' + J(u'shell_mk_only', u'本遍多判') + u' 行⇎采集多判 '
    + J(u'shell_pick_only', u'采集多判') + u' 行——采集多的 ' + V(u'shell_pick_only', 0, u'采集多判·821')
    + u' 行全在抬头页壳里(正文行零差 ' + J(u'shell_pick_only_body', u'采集多判正文') + u'), '
    + u'账平判定 ' + V(u'shell_ledger_close', None, u'壳账零') + u'(五份相加), 谓词复现判定 '
    + V(u'shell_replicate_pick', None, u'壳谓词复现') + u'。 壳的构成: 页壳行 ' + J(u'shell_page', u'页壳行')
    + u' ⇎ 抬头行 ' + J(u'shell_hdr', u'抬头行') + u', 空白行 ' + J(u'blank', u'空白行') + u' 行——'
    + u'“HTML 没有页壳”这句不成立(判定 ' + V(u'html_shell_none', None, u'HTML无壳') + u'), 只是它的壳全是空行。 '
    + u'抬头版式三档句点尺 ' + J(u'hdr_dot2sp', u'抬头两点式') + u' ⇎ ' + J(u'hdr_dot1sp', u'抬头一点式')
    + u' ⇎ ' + J(u'hdr_nodot', u'抬头无点式') + u'; 断词尺: 连字符跨行 ' + J(u'hyphen_break', u'连字符断行')
    + u' 处 ⇎ non-delivery 连写 ' + J(u'ndn_unbroken', u'NDN连写') + u' ⇎ 断成 “non- delivery” '
    + J(u'ndn_broken', u'NDN断开') + u' 处。')

LINES.append(
    u'🧮 闭合账总口径: 标量恒等式 ' + V(u'scalar_clos_n', None, u'恒等式数') + u' 条, 通过 '
    + V(u'scalar_clos_sum', None, u'恒等式通过') + u' 条 ⇎ 清单式闭合 ' + V(u'list_clos_n', None, u'清单闭合')
    + u' 项 ⇎ 面内恒等式同数共键 ' + V(u'x_ident_n', None, u'共键恒等式') + u' 条; '
    + u'与采集遍逐键对账 ' + V(u'pick_agree', None, u'对账相符') + u' 键相符 ⇎ ' + V(u'pick_diff', None, u'对账不符')
    + u' 键不符(只对同定义标量; 针表不横比——采集数的是字面针 ' + V(u'needle_table_pick', None, u'采集针表')
    + u' 枚, 本遍数的是由面上导出的锚句 ' + V(u'needle_table_mk', None, u'本遍针表') + u' 枚)。 '
    + u'措辞十二族的两遍正则共有 ' + V(u'tier_cross_n', None, u'措辞共测') + u' 条, 逐条同值 '
    + JL(u'tier_cross_agree', u'措辞共测同值') + u'; 只在某一遍出现的模式串 ' + NKL(F[u'tier_pat_pick_only'])
    + u' ⇎ ' + NKL(F[u'tier_pat_mk_only']) + u' 条。 五份同为 ' + V(u'cr', 0, u'CR·821') + u' 枚回车全 LF、'
    + V(u'nul', 0, u'NUL·821') + u' 枚 NUL; txt⇎html ' + V(u'txt_n', None, u'txt份数') + u' ⇎ '
    + V(u'html_n', None, u'html份数') + u' 份(判定 ' + V(u'txt_no_tag', None, u'txt零标签') + u')。')

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
    got = [e for e in ELEMS.get(s, []) if eval(e, {FN: BB74}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, NOEXPR
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv74.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
F['contract_n'] = len(F) + 1
json.dump(F, io.open(u'corpus/_b74flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms74.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCHS, key=len, reverse=True)) + NL)

CH = dict(AMETA)
CH.update({u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCHS))),
           u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
           u'classes': dict((c, sorted([a for a in ANCHS if len(HITC[a]) == n]))
                            for c, n in ((u'single', 1), (u'cross', 2), (u'three', 3), (u'four', 4), (u'five', 5))),
           u'collisions': dict((k, v) for k, v in COLL.items()),
           u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
           u'deriv_points': sum(len(v) for v in SEENX.values()), u'notes': NOTES,
           u'needle_n': F[u'needle_n'], u'zid': [[v, w] for v, w in ZV], u'litk': LITK, u'sn': SN,
           u'blk': PTXT, u'pins': [[LBL[i], s, e] for i, s, e in PINS],
           u'closure_keys': sorted([k for k in F if u'close' in k or k in (u'tone_ledger', u'grp_close')]),
           u'flat': F})
json.dump(CH, io.open(u'corpus/_b74checks.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

ANS5 = [u'只分 4yz/5yz 两类、自认难定 transient、全份零大写 MUST 零 retry 零 queue',
        u'定下限“SHOULD be at least 30 minutes”、给弃窗“at least 4-5 days”、参数“MUST be configurable”',
        u'把同一段搬进协议标准、术语换成 SMTP client、补一句 MAY 可以少试几次',
        u'一个义务词也不给, 只给阶梯规则串 F,2h,15m; G,16h,1h,1.5; F,4d,6h 与 24h 封顶、四天截止',
        u'只列参数默认 5d/5d/300s/4000s/300s/60s, 外加“0=只试一次”这一档']
ENTRY = u'corpus/babeltele/B74_mail_retry_schedule_five_answers.md'
srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 码位／原行 %d／非空行 %d／最长行 %d 列／换页 %d 枚／答句 %s)' % (
        PATH[i].split('/')[-1], F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        F[u'maxlen'][i], F[u'ff'][i], ANS5[i]) for i in range(NSRC))
    + u' (三份 RFC 为 RFC Editor 纯文本面、两份 MTA 文档为 HTML 面; 全库零回车、零 NUL、零 BOM; '
      + u'抬头年 ' + u'⇎'.join(str(y) for y in F[u'years']) + u', 跨 ' + str(F[u'year_span']) + u' 年; '
      + u'换算表 ' + str(len(F[u'cv_sec'])) + u' 档、十二族措辞针、十二段答段全部由行内游标或位置导出, 一个都不手填。 '
        u'抓取时刻、RFC Editor 此刻的现行状态页与勘误页(2821 此刻的“被废止”标签是否有后续勘误不可由在库文件判定——在库字节只给得出抬头里的 Obsoletes/Updates/Replaces 清单)、'
        u'被废止文书自己的现行文本、现网 Exim/Postfix 部署实际按什么参数跑(文档默认值不等于装机值)、镜像页的生成时刻(在库只留 '
        + str(F[u'year_stamp_n']) + u' 处时间戳 ' + u'⇎'.join(F[u'year_stamp']) + u'), 都只在本机或站外成立, 不进门槛)\n')
link = (u"；联结不是“同一份数据的两种序列化”, 而是“投递失败的邮件到底多久再试一次、什么时候不再试”在一份协议定义、"
        u"两份主机要求与两份 MTA 手册里的五种答法: 821 只把失败分成 4yz/5yz 两类, 连重试词汇都没有(retry 三形 "
        + str(F[u'tier_tot'][0]) + u' 枚措辞针里 ' + str(F[u'tier_zero_fams'][0]) + u" 族零枚, 全份大写 MUST "
        + str(F[u'tone_MUST'][0]) + u' 枚而小写 must ' + str(F[u'tone_must_lc'][0]) + u" 枚), 还自认两个站点很难对 transient 取一致; "
        + u"⇎ 1123 第一次给出数字: 下限“至少 30 分钟”(" + str(F[u'tier_tot'][1]) + u" 枚措辞针)、给弃窗“4-5 天”、"
        u"参数“MUST be configurable”, 外加一条 DNS 指数退避与 5 秒下限; ⇎ 5321 把 1123 那段逐字搬进协议标准"
        u"(共头 " + str(F[u'pre_1123_5321']) + u" 词、共尾 " + str(F[u'suf_1123_5321']) + u" 词、中间 "
        + str(F[u'w_only_5321']) + u" 词是它新加的, 两段行号位移同为 " + str(F[u'delay_shift_5321']) + u" 行), "
        u"术语换成 SMTP client, 并补一句 MAY: 目的地地址少试几次也可以; ⇎ Exim 一个义务词也不给("
        + str(F[u'tone_tot'][3]) + u" 枚语气词), 给的是可解析的阶梯: " + str(F[u'ex_attempts_tot']) + u" 档、"
        u"封顶 " + str(F[u'ex_rim_cap']) + u" 秒、截止 " + str(F[u'ex_def_span']) + u" 秒; ⇎ Postfix 只列默认值: "
        + u'/'.join(F[u'pf_def_tok']) + u", 外加“设 0 就只试一次”这一档。五种答法里只有两种给出“放弃”的确切时刻, "
        u"而“放弃”一词的三种写法(cutoff/give-up/undeliverable)分布是 "
        + u'⇎'.join(str(F[u'word_cutoff'][i]) for i in range(NSRC)) + u" 枚。\n")
tags = (u'五种答法分给五份文书 821 零 retry 零 queue 零大写 MUST(小写 must %d 枚) ⇎ 1123 首次给数: 30 分钟下限⇎4-5 天给弃窗⇎参数 MUST be configurable '
        u'⇎ 5321 逐字搬家: 共头 %d 词⇎共尾 %d 词⇎新词 %d⇎两段等距后移 %d 行 ⇎ Exim 零语气词只给规则串 %d 档⇎封顶 %d⇎截止 %d ⇎ Postfix 只给默认 %s '
        u'五档阶梯(逐行⇎折平⇎摘壳⇎断面⇎粘面, 折行救 %d 枚 ⇎ 断面新读 %d 枚 ⇎ 粘面再换 %d 枚丢 %d 枚) 死集零 反向 %d 枚全冷 '
        u'MTA 答段零义务词 ⇎ RFC 答段 MUST/MAY/SHOULD 齐 语气五轨闭合⇎零 MUST 恰是 821⇎Exim 两份 '
        u'换算表 %d 档: 低于 30 分钟下限 %d 档⇎两份 MTA 默认各踩住 4-5 天窗一端 %d 处 ⇎ 300s×6=1800s⇎15m×2=下限 '
        u'引用三式并计(空格⇎连写⇎短横) ⇎ 1123 面上 RFC-821 短横 %d 枚⇎空格式 %d 枚(判定现读) 谱系 5321 Obsoletes 2821⇎Updates 1123⇎821 Replaces %d 号 '
        u'两把尺搬字: 行池 %d 条最大 %d(逐字节 %d) ⇎ 句池 %d 句最大 %d(增益 %d) ⇎ 两份 MTA 与三份 RFC 零共用句 '
        u'组面⇎非空行⇎壳行三本账逐份归零 ⇎ Postfix 唯一一枚跨行组 ⇎ “HTML 无页壳”不成立只因其壳全是空行 '
        u'两遍壳谓词分解到行(采集多判 %d 行全抬头⇎本遍多判 %d 行) 闭合账 标量 %d⇎清单 %d 项⇎共键 %d 条 ⇎ 对账 %d 键符 %d 不符⇎针表两遍 %d⇎%d 不横比\n' % (
            F[u'tone_must_lc'][0], F[u'pre_1123_5321'], F[u'suf_1123_5321'], F[u'w_only_5321'], F[u'delay_shift_5321'],
            F[u'ex_attempts_tot'], F[u'ex_rim_cap'], F[u'ex_def_span'], u'/'.join(F[u'pf_def_tok']),
            F[u'fold_minus_strict_n'], F[u'ds_only_n'], F[u'dj_only_n'], F[u'ds_no_dj_n'], F[u'neg_n'],
            len(F[u'cv_sec']), F[u'cv_below_n'], F[u'band_edge_hits'],
            F[u'cite_821_hy_in_1123'], F[u'cite_821_in_1123'], sum(F[u'repl_n'][0:1]),
            F[u'pool_n'], F[u'pair_max'], F[u'pair_max_byte'], F[u's_pool_n'], F[u's_pair_max'], F[u's_ruler_gain_1123_5321'],
            F[u'shell_pick_only'][0], sum(F[u'shell_mk_only']), F[u'scalar_clos_n'], F[u'list_clos_n'], F[u'x_ident_n'],
            F[u'pick_agree'], F[u'pick_diff'], F[u'needle_table_pick'], F[u'needle_table_mk']))
title = (u'# B74 投递失败的邮件到底多久再试一次、什么时候不再试，五份一手文书五种答法：'
         u'821 只把失败分成两类、连重试词汇都没有（小写 must %d 枚⇎大写 MUST 零枚） ⇎ '
         u'1123 第一次给出数字：下限至少 30 分钟⇎给弃窗 4-5 天⇎参数必须可配 ⇎ '
         u'5321 把那段逐字搬进协议标准（共头 %d 词⇎共尾 %d 词⇎新词 %d 枚）并把术语换成 SMTP client、补一句“可以少试几次”的 MAY ⇎ '
         u'Exim 一个义务词也不给，只给阶梯规则串与 %d 次重试、%d 秒封顶、%d 秒截止 ⇎ '
         u'Postfix 只列参数默认 %s，另立“设 0 就只试一次”这一档'
         u'（给弃时刻五份只有两份给全，两种 MTA 默认各踩住 4-5 天窗的一端）\n') % (
             F[u'tone_must_lc'][0], F[u'pre_1123_5321'], F[u'suf_1123_5321'], F[u'w_only_5321'],
             F[u'ex_attempts_tot'], F[u'ex_rim_cap'], F[u'ex_def_span'], u'/'.join(F[u'pf_def_tok']))
text = (title + srcline + link + tags +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n'
        + u'## ⟪BabelTele⟫\n' + body + u'\n\n'
        + u'## ⛓解读注\n\n（此段由 corpus/_fill74.py 从 corpus/_b74checks.json 与 corpus/_deriv74.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s ｜ 归属错配 %d ⇎ 非锚面线 %d' % (USED, DIST, TAGN, len(ERR), len(MISSLINE)))
print(u'一源 %d ⇎ 二至四源 %d ⇎ 五源 %d ｜ 针 %d ⇎ 折行独有 %d ⇎ 断面独有 %s ⇎ 粘面独有 %s ⇎ 断面丢 %s ⇎ 死集 %s' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all5'], F[u'needle_n'], F[u'fold_minus_strict_n'],
    NKL(F[u'ds_only_keys']), NKL(F[u'dj_only_keys']), NKL(F[u'ds_no_dj_keys']), F[u'dead_needles']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ⇎ 恒等式 %d ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), F[u'x_ident_n'], len(F)))
print(u'段 起 %s 止 %s 行 %s 字符 %s 词 %s ｜ 1123⇎5321 独 %d⇎%d 共 %d 头 %d 尾 %d 位移 %d/%d' % (
    F[u'blk_lo'], F[u'blk_hi'], F[u'blk_rows'], F[u'blk_chars'], F[u'blk_words'],
    F[u'w_only_1123'], F[u'w_only_5321'], F[u'w_common_12'], F[u'pre_1123_5321'], F[u'suf_1123_5321'],
    F[u'delay_shift_5321'], F[u'giveup_shift_5321']))
print(u'段语气 MUST %s MAY %s SHOULD %s ｜ 三尺闭合 %d ｜ MTA段零 %d' % (
    F[u'tone_must'], F[u'tone_may'], F[u'tone_should'], F[u'blk_tone_ruler_close'], F[u'blk_tone_none_exim_pf']))
print(u'行距 1123 %d/%d ⇎ 5321 %d/%d ｜ 821 %d/%d/%d ｜ exim %d/%d/%d/%d ｜ pf %d/%d(共 %d 次)' % (
    F[u'delay_giveup_gap_1123'], F[u'giveup_conf_gap_1123'], F[u'delay_giveup_gap_5321'],
    F[u'giveup_conf_gap_5321'], F[u'yz_gap'], F[u'hard_4yz_gap'], F[u'thumb_hard_gap'],
    F[u'rule_prompt_gap'], F[u'rule_rim_gap'], F[u'rim_cut_gap'], F[u'cut_30min_gap'],
    F[u'mql_minbo_gap'], F[u'zero_mql_gap'], F[u'zero_repeats']))
print(u'池 行尺 %d 最大 %s(%d, 字节 %d) 轴 %s ⇎ 句尺 %d 最大 %d 增益 %d/%d ⇎ HTML 零共用 %d/%d' % (
    F[u'pool_n'], F[u'pair_max_lbl'], F[u'pair_max'], F[u'pair_max_byte'], F[u'axis_str'],
    F[u's_pool_n'], F[u's_pair_max'], F[u's_ruler_gain_821_5321'], F[u's_ruler_gain_1123_5321'],
    F[u'pool_html_shared'], F[u's_pair_html']))
print(u'组 %s ⇎ 非空 %s ⇎ 跨行组 %s ⇎ 组账 %s' % (F[u'grp_n'], F[u'nonblank_pick'], F[u'grp_glued'], F[u'grp_close']))
print(u'行针复核 %d/%d ⇎ 错行 %d ⇎ 跨行 1123/5321 %d/%d ⇎ seconds %s 合计 %d' % (
    F[u'pin_rt_ok'], F[u'pin_rt_n'], F[u'pin_wrongline'],
    F[u'conf_straddle_1123'], F[u'conf_straddle_5321'], F[u'sec_word'], F[u'sec_word_rfc']))
print(u'判定 %s' % (CLOSE,))

