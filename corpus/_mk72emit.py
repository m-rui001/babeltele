# -*- coding: utf-8 -*-
"""建条目第二遍(B72)的后半: 由 _mkB72.py 在顶层 exec 进来, 与前半共享同一批现读量。
本半只做三件事: 把“302 之后能不能改写方法”这一句在四份文书里的答句段落做成可算的段落对照
(段界只在最宽的剥引文平面上按字面针定位, 偏移再映回原文件行号)、排编码区正文、发 DERIV/checks/atoms/条目文件。
正文里每一枚三位以上的数都由 V()/J()/EXPR() 注册过算式; 锚一律由位置从原行导出, 不手打。"""

# --- SCAN2 BEGIN --- (并键段: 同一段也机械切进 audit.py::_b72_scan)
TAGS = LBL
IDX = dict((t, n) for n, t in enumerate(LBL))
FAN = [pnorm(t) for t in T]
ATOMFAIL = []


def AN(i, *nd):
    for l in L[i]:
        if all(x in l for x in nd):
            return u'⟦%s⟧⟨%s⟩' % (LBL[i], l)
    ATOMFAIL.append((LBL[i], nd))
    raise AssertionError(u'锚导出失败 %s %s' % (LBL[i], nd))


def fmap(i):
    """剥引文折平面上的偏移 ⇎ 原行号双向尺: 段界按剥引文后的面量, 行号仍指回原文件"""
    mp = []
    off = 0
    first = True
    for n, x in enumerate(L[i], 1):
        s = u' '.join(dequote(x).split())
        if not s:
            continue
        if not first:
            off += 1
        first = False
        mp.append((off, n))
        off += len(s)
    return mp


FMP = [fmap(i) for i in range(NSRC)]
for i in range(NSRC):
    assert u' '.join([u' '.join(dequote(x).split()) for x in L[i]
                      if u' '.join(dequote(x).split())]) == QUOT[i], i


def line_of(i, a):
    r = 0
    for o, n in FMP[i]:
        if o <= a:
            r = n
        else:
            break
    return r


def blk(i, start, end):
    """答句段 = 剥引文折平面上从 start 起到 end(含) 的那一段; 起止只按字面针定位, 行号由偏移现映"""
    a = QUOT[i].find(start)
    if a < 0:
        raise AssertionError(u'段起针落空 %s %s' % (LBL[i], start))
    b = QUOT[i].find(end, a)
    if b < 0:
        raise AssertionError(u'段止针落空 %s %s' % (LBL[i], end))
    e = b + len(end)
    return u' '.join(QUOT[i][a:e].split()), line_of(i, a), line_of(i, e - 1)


def ln_of(i, nd):
    a = QUOT[i].find(nd)
    if a < 0:
        raise AssertionError(u'行针落空 %s %s' % (LBL[i], nd))
    return line_of(i, a)


PINS = [(0, u'RFC 1945 and RFC 2068 specify', u'redirected request.'),
        (1, u'For historical reasons, a user agent MAY change', u'subsequent request.'),
        (2, u'The 308 (Permanent Redirect) status code indicates', u'POST to GET.'),
        (3, u'For historical reasons, a user agent MAY change', u'subsequent request.')]
PB = [blk(i, s, e) for i, s, e in PINS]
PTXT = [p[0] for p in PB]
F['blk_lo'] = [p[1] for p in PB]
F['blk_hi'] = [p[2] for p in PB]
F['blk_rows'] = [p[2] - p[1] + 1 for p in PB]
F['blk_chars'] = [len(p[0]) for p in PB]
F['blk_words'] = [len(p[0].split()) for p in PB]
PW = [p[0].lower().split() for p in PB]
F['blk_only'] = [((len(set(PW[i]) - set(PW[i - 1])) if i else len(set(PW[i])))) for i in range(NSRC)]
F['blk_common_1'] = len(set(PW[0]) & set(PW[1]))
F['blk_vocab'] = [len(set(x)) for x in PW]
F['w_row_close'] = F['blk_only'][1] + F['blk_common_1'] - len(set(PW[1]))


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


F['suf_7231_9110'] = suffix_words(PW[1], PW[3])
F['pre_7231_9110'] = head_words(PW[1], PW[3])
F['suf_2616_7231'] = suffix_words(PW[0], PW[1])
F['pre_2616_7231'] = head_words(PW[0], PW[1])
F['blk_same_7231_9110'] = 1 if PW[1] == PW[3] else 0
F['blk_identical_chars'] = 1 if PTXT[1] == PTXT[3] else 0
F['tone_must'] = [ub(p, u'MUST') for p in PTXT]
F['tone_may'] = [ub(p, u'MAY') for p in PTXT]
F['tone_must_not_blk'] = [ub(p, u'MUST NOT') for p in PTXT]
F['tone_should'] = [ub(p, u'SHOULD') for p in PTXT]
F['tone_up'] = [F['tone_must'][i] + F['tone_may'][i] + F['tone_should'][i] for i in range(NSRC)]
F['tone_bare_must'] = [F['tone_must'][i] - ub(p, u'MUST NOT') for i, p in enumerate(PTXT)]
F['tone_ledger'] = [F['tone_must'][i] - (F['tone_bare_must'][i] + ub(p, u'MUST NOT'))
                    for i, p in enumerate(PTXT)]
F['ln_note_2616'] = ln_of(0, u'RFC 1945 and RFC 2068 specify')
F['ln_treat_2616'] = ln_of(0, u'treat 302 as if it were a 303')
F['note_treat_gap'] = F['ln_treat_2616'] - F['ln_note_2616']
F['ln_hist_7231'] = ln_of(1, u'For historical reasons, a user agent MAY change')
F['ln_mustnot_7231'] = ln_of(1, u'MUST NOT change the request method')
F['hist_mustnot_gap'] = F['ln_mustnot_7231'] - F['ln_hist_7231']
F['ln_ind_7538'] = ln_of(2, u'The 308 (Permanent Redirect) status code indicates')
F['ln_restricted_7538'] = ln_of(2, u'the use of status code 308 is restricted')
F['ind_restricted_gap'] = F['ln_restricted_7538'] - F['ln_ind_7538']
F['ln_hist_9110'] = ln_of(3, u'For historical reasons, a user agent MAY change')
F['ln_step_9110'] = ln_of(3, u'Change the request method according')
F['hist_step_gap'] = F['ln_step_9110'] - F['ln_hist_9110']
F['step_hist_abs'] = abs(F['hist_step_gap'])
TOPNUM = re.compile(u'^   (\\d)\\.  ')
_m0 = ln_of(3, u'SHOULD resend the original request message with the following')
_m1 = ln_of(3, u'A client SHOULD detect and intervene')
F['mod_step_nums'] = [int(m.group(1)) for n, x in enumerate(L[3], 1)
                      if _m0 < n < _m1 for m in [TOPNUM.match(x)] if m]
F['mod_steps'] = len(F['mod_step_nums'])
CLOSE2 = {}
CLOSE2[u'mod_step_seq'] = 1 if F['mod_step_nums'] == [1, 2, 3, 4, 5] else 0
CLOSE2[u'mod_step_has_rewrite'] = 1 if (F['ln_step_9110'] > _m0 and F['ln_step_9110'] < _m1) else 0
F['dep_305_sent'] = cnt_cur(QUOT[3], u'The 305 (Use Proxy) status code was defined in a previous version')
F['dep_all'] = cnt_cur(QUOT[3], u'is now deprecated')
CLOSE2[u'dep_305_one'] = 1 if (F['dep_305_sent'] == 1 and F['dep_all'] == 2) else 0
CLOSE2[u'step_before_hist'] = 1 if F['hist_step_gap'] < 0 else 0
CLOSE2[u'hist_after_7231'] = 1 if F['hist_mustnot_gap'] > 0 else 0
CFOUR = [u'tierq_confirm_gate', u'tierq_may_change', u'tierq_not_allow_changing', u'tierq_erroneously']
F['claim_four_n'] = [sum(1 for k in CFOUR if F[k][i]) for i in range(NSRC)]
CLOSE2[u'claim_four_none_all'] = 1 if (max(F['claim_four_n']) < len(CFOUR) and sum(F['claim_four_n']) >= 2) else 0
F.update(CLOSE2)
F['dead_widest'] = [k for k in GN if not SN[k][3]]
F['dead_n'] = len(F['dead_widest'])
F['ser_n'] = len(SER)
F['neg_ctrl_n'] = len(F['neg_controls'])
F['cross_needles'] = [k for k in GN if sum(1 for i in range(NSRC) if SN[k][i]) >= 2]
F['cross_needle_n'] = len(F['cross_needles'])
F['fold_only_str'] = u' ⇎ '.join(F['fold_only_keys'])
F['quot_only_n'] = len(F['quot_only_keys'])
F['quot_only_str'] = u' ⇎ '.join(F['quot_only_keys'])
F['line_hit_keys'] = [k for k in GN if SN[k][0]]
# --- SCAN2 END ---

ZV.append((u"B72V('mod_steps') - 5",
           u'9110 把改写动作写成一份五条的编号清单(顶层 1..5)'))
ZV.append((u"B72V('mod_step_seq') - 1", u'清单编号严格 1,2,3,4,5 无跳号'))
ZV.append((u"B72V('mod_step_has_rewrite') - 1",
           u'“Change the request method according to the redirecting status code” 就落在这份清单之内'))
ZV.append((u"B72V('dep_305_one') - 1",
           u'9110 面上“is now deprecated”两枚里恰一枚属于 305 小节(另一枚说的是别的对象)'))
ZV.append((u"B72V('claim_four_none_all') - 1",
           u'四种说法(确认门⇎可改⇎不允许改⇎误改写)没有一份同时给全'))
ZV.append((u"sum(B72V('claim_four_n')) - ("
           + u' + '.join(u"sum([1 if B72V('%s', i) else 0 for i in range(4)])" % k for k in CFOUR)
           + u")", u'四族按份归并 ⇎ 按族归并: 同一批出现数两种走法相等'))
ZV.append((u"B72V('dead_n') - B72V('neg_ctrl_n') - B72V('ser_n')",
           u'最宽档落空的针=反向对照+序列化对照两类, 内容针一枚不落'))
ZV.append((u"B72V('blk_only', 1) + B72V('blk_common_1') - B72V('blk_vocab', 1)",
           u'7231 段的词集账: 相对 2616 段独有 + 两份交集 = 7231 段词表(容斥)'))
ZV.append((u"B72V('step_before_hist') - 1",
           u'9110 里改写清单排在历史原因注之前(与 7231 的注在前、约束句在后相反)'))
ZV.append((u"B72V('hist_step_gap') + B72V('step_hist_abs')",
           u'9110 的两处行距符号账: 带签名 ⇎ 绝对值'))
ZV.append((u"B72V('hist_after_7231') - 1",
           u'7231 里“MUST NOT change”排在“历史原因”句之后'))

PAIRLBL = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in itertools.combinations(range(NSRC), 2)]


def P6(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, PAIRLBL[i])) for i in range(6))


def J4(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, u'段')) for i in range(NSRC))


LINES = []
LINES.append(
    u'🧭 四源字节 ' + J(u'bytes', u'字节') + u' ⇎ 面内码位 ' + J(u'chars', u'码位') + u' ⇎ 原文件行 '
    + J(u'lines', u'行数') + u' ⇎ 非空行 ' + J(u'nonblank', u'非空行') + u' ⇎ 最长行 ' + J(u'maxlen', u'最长行')
    + u' 列: 2616 把 302 写成“客户端不许改写方法、但实现都当 303 用”(' + AN(0, u'treat 302 as if it were a 303')
    + u') ⇎ 7231 换成“出于历史原因 MAY change”(' + AN(1, u'For historical reasons')
    + u') ⇎ 7538 干脆另立 308 以避开这处含混(' + AN(2, u'The 308 (Permanent Redirect) status code')
    + u') ⇎ 9110 收下历史原因句、把改写动作写进编号清单(' + AN(3, u'Change the request method')
    + u')。 版式: 换页符 ' + J(u'ff', u'换页符') + u' 枚 ⇎ 剥壳后剩 ' + J(u'shell_strip', u'留行')
    + u' 行, 9110 面上零枚换页符(判定 ' + V(u'no_ff_only_9110', None, u'9110零换页') + u') ⇎ 剥引文竖线另有 '
    + J(u'pipe_lines', u'竖线行') + u' 行含竖线、' + J(u'pipe_glyphs', u'竖线符') + u' 枚竖线符; CR '
    + J(u'cr', u'CR') + u' 全零, BOM ' + J(u'bom', u'BOM') + u' ⇎ 非 ASCII 码位 ' + J(u'nonascii', u'非ASCII')
    + u' —— 字节−码位差 ' + J(u'byte_cp_delta', u'字节码位差') + u' 与每枚非 ASCII 的 utf-8 加字节 '
    + J(u'nonascii_extra', u'加字节') + u' 逐份相等, 纯 ASCII 面 ' + V(u'ascii_all', None, u'纯ASCII份数')
    + u' 份(9110 带一枚 BOM 与取变音符)。 两遍壳谓词不同账: 本遍 ' + J(u'shell_n', u'壳行·本遍') + u' ⇎ 采集 '
    + J(u'shell_pick', u'壳行·采集') + u', 两遍同判 ' + J(u'shell_both', u'同判壳行') + u' 行, 只有本遍判壳的 '
    + J(u'shell_mk_only', u'本遍多判') + u' 行全是抬头字段行(抬头归因 ' + J(u'shell_mk_only_hdr', u'多判归抬头')
    + u'), 只有采集判壳的 ' + J(u'shell_pick_only', u'采集多判') + u' 行全是缩进后以“RFC 四位数+空格”开头的正文句('
    + J(u'shell_pick_only_body', u'多判归正文') + u' 行同判), 差 ' + J(u'shell_diff', u'壳账差')
    + u' 行——采集那枚谓词在 2616 身上多吃掉 ' + V(u'shell_pick_only', 0, u'采集多判·2616')
    + u' 行正文, 判定 ' + V(u'pick_overstrip_only_2616', None, u'采集过剥唯一') + u'。')

LINES.append(
    u'📐 答句针 ' + V(u'needle_n', None, u'针总数') + u' 枚(归各份 ' + J(u'needles_owned', u'名下针')
    + u' 枚)走四档阶梯: 原面逐行 ' + J(u'sn_strict_docs', u'逐行档') + u' ⇎ 全篇折平 ' + J(u'sn_fold_docs', u'折平档')
    + u' ⇎ 摘壳折平 ' + J(u'sn_sh_docs', u'摘壳档') + u' ⇎ 剥引文折平 ' + J(u'sn_quot_docs', u'剥引文档')
    + u' 枚。 逐行档塌得最狠: 全库 ' + V(u'needle_n', None, u'针总数') + u' 枚里只有 ' + J(u'sn_strict_docs', u'逐行命中')
    + u' 枚能在单行里读全, 靠折行救回的 ' + V(u'fold_only_n', None, u'折行独有') + u' 枚(按份 '
    + J(u'fold_only_own', u'折行独有·份') + u'), 7538 名下 ' + V(u'needles_owned', 2, u'名下针·7538')
    + u' 枚在逐行档一枚不中(' + AN(2, u'is restricted') + u' 那句整段跨行)。 剥引文档比摘壳档再多 '
    + J(u'quot_minus_sh', u'剥引文减摘壳') + u' 枚, 新增只发生在 9110(判定 ' + V(u'quot_only_9110', None, u'剥引文唯一')
    + u'): ' + V(u'quot_only_n') + u' 枚(' + F[u'quot_only_str'] + u')——9110 把这句注成 `| *Note:* …` 引文块, 竖线楔在句中, '
    + u'不剥引文竖线就读不到整句。 摘壳档比折平档一粒不少(差 ' + J(u'sh_minus_fold', u'摘壳减折平') + u'), 阶梯单调账 '
    + V(u'ladder_monotone', None, u'阶梯单调') + u'。 最宽档落空的针 ' + V(u'dead_n', None, u'死针枚数') + u' 枚 = 反向对照 '
    + V(u'neg_ctrl_n', None, u'反向针数') + u' 枚 + 序列化对照 ' + V(u'ser_n', None, u'序列化对照数') + u' 枚('
    + u' ⇎ '.join(F[u'dead_widest']) + u'), 非反向的内容死针 ' + V(u'dead_nonneg', None, u'死集非反向') + u' 枚 ⇒ 内容针在最宽档全读得到; '
    + u'反向针在最宽档合计命中 ' + V(u'neg_hit_widest', None, u'反向命中') + u'。 判定轨也换过: 正则字面轨 ⇎ 非重叠游标轨逐枚相等(闭合 '
    + V(u're_eq_cur', None, u'两轨相等') + u'), 重叠口径多出的 ' + V(u'overlap_extra', None, u'重叠多余') + u' 枚为零。')

LINES.append(
    u'🔍 “改写方法”这件事在四份文书里有六种说法, 全部在剥引文面上现数: 确认门 “MUST NOT automatically redirect” '
    + J(u'tierq_confirm_gate', u'确认门') + u' 枚(判定 ' + V(u'confirm_gate_only_2616', None, u'确认门唯一')
    + u', 只在 2616 存活: ' + AN(0, u'MUST NOT automatically redirect') + u') ⇎ “not allowed to change the method” '
    + J(u'tierq_not_allowed', u'不许改') + u' 枚(2616 ' + AN(0, u'RFC 1945 and RFC 2068') + u') ⇎ “MAY change the request method” '
    + J(u'tierq_may_change', u'可改') + u' 枚(7231 ⇎ 9110 两份, 判定 ' + V(u'may_change_pair', None, u'可改成对')
    + u', 而它在折平面上读作 ' + J(u'tier_may_change', u'可改·折平') + u' —— 9110 的 ' + V(u'tier_may_change', 3, u'可改折平·9110')
    + u' 枚全靠剥竖线才现形) ⇎ “MUST NOT change the request method” ' + J(u'tierq_must_not_change', u'不得改')
    + u' 枚(7231 ' + AN(1, u'MUST NOT change the request method') + u' 与 9110 逐字同句) ⇎ “does not allow changing the request method” '
    + J(u'tierq_not_allow_changing', u'不允许改') + u' 枚(只在中间两份, 判定 ' + V(u'not_allow_changing_pair', None, u'不允许成对')
    + u', 7538 ' + AN(2, u'does not allow changing') + u') ⇎ “erroneously”(误改写) ' + J(u'tierq_erroneously', u'误改写')
    + u' 枚(首尾两份, 判定 ' + V(u'erroneously_outer_pair', None, u'误改写首尾') + u', 2616 那枚就在 301 小节: '
    + AN(0, u'some existing HTTP/1.0 user agents') + u')。 六族合计折平 '
    + J(u'tier_fold_tot', u'六族折平') + u' ⇎ 剥引文 ' + J(u'tier_quot_tot', u'六族剥引文') + u', 增益 '
    + J(u'tier_gain', u'六族增益') + u' 全落在 9110, 与剥引文档新增针数同账(闭合 ' + V(u'tier_sum_close', None, u'六族闭合')
    + u'); 9110 的引文块行原面自带竖线, 例如 ' + AN(3, u'were later added to unambiguously indicate')
    + u' 一行(它不是六族针, 只作块形证据)。 “POST to GET” ' + J(u'post_to_get', u'POSTtoGET') + u' 枚(2616 里通往 GET 的正门是 303 的取回句 '
    + AN(0, u'SHOULD be retrieved using') + u') ⇎ “For historical reasons” ' + J(u'hist_reasons', u'历史原因')
    + u' 枚——9110 一句里出现 ' + V(u'hist_reasons', 3, u'历史原因·9110') + u' 次而 2616 零次('
    + V(u'n_a2616_no_historical', 0, u'历史原因针·2616') + u' 枚, 反向对照)。')

LINES.append(
    u'🧾 四段答句本身可比: 段行界 ' + J(u'blk_lo', u'段起行') + u'.. ' + J(u'blk_hi', u'段止行') + u'(行数 '
    + J(u'blk_rows', u'段行数') + u') ⇎ 段字符 ' + J(u'blk_chars', u'段字符') + u' ⇎ 段词 ' + J(u'blk_words', u'段词')
    + u'。 7231 段与 9110 段逐词相等(共尾 ' + V(u'suf_7231_9110', None, u'7231·9110共尾') + u' 词 ⇎ 共头 '
    + V(u'pre_7231_9110', None, u'7231·9110共头') + u' 词 ⇎ 词序全同判定 ' + V(u'blk_same_7231_9110', None, u'段全同')
    + u' ⇎ 字符全同判定 ' + V(u'blk_identical_chars', None, u'段字符同') + u')——9110 把 7231 的注整段搬走、一个词都没动, 差别只在序列化: 它被楔进引文块('
    + AN(3, u'For historical reasons') + u')。 2616 段与 7231 段共尾只有 ' + V(u'suf_2616_7231', None, u'2616·7231共尾')
    + u' 词 ⇎ 共头 ' + V(u'pre_2616_7231', None, u'2616·7231共头') + u' 词: 同一处含混换了一套说法('
    + AN(0, u'RFC 1945 and RFC 2068') + u' ⇎ ' + AN(1, u'For historical reasons') + u')。 词集账: 7231 段相对 2616 段独有 '
    + V(u'blk_only', 1, u'段独有词·7231') + u' 词, 与两份交集 ' + V(u'blk_common_1', None, u'段交集词')
    + u' 相加=7231 段词表 ' + V(u'blk_vocab', 1, u'段词表·7231') + u'(闭合 ' + V(u'w_row_close', None, u'段词闭合')
    + u')。 语气按段现数: MUST ' + J(u'tone_must', u'段MUST') + u' ⇎ 裸 MUST ' + J(u'tone_bare_must', u'段裸MUST')
    + u' ⇎ MUST NOT ' + J(u'tone_must_not_blk', u'段MUSTNOT') + u' ⇎ MAY ' + J(u'tone_may', u'段MAY') + u' ⇎ SHOULD '
    + J(u'tone_should', u'段SHOULD') + u', 大写账 ' + J(u'tone_ledger', u'段语气账') + u' 逐份归零。 '
    + u'9110 不只留注, 还把改写动作写成编号清单: 顶层条目 ' + V(u'mod_steps', None, u'清单条目数') + u' 条('
    + u','.join(str(x) for x in F[u'mod_step_nums']) + u'), 判定 ' + V(u'mod_step_seq', None, u'清单连号')
    + u', 而 “Change the request method according” 那条正落在清单区间内(判定 '
    + V(u'mod_step_has_rewrite', None, u'改写条目在清单内') + u', 与历史原因句隔 ' + V(u'step_hist_abs', None, u'注⇎清单行距')
    + u' 行)。')

LINES.append(
    u'📊 30x 家族在四份里的名分是可数的: 正文小节数 ' + J(u'code_n', u'小节数') + u'(判定 '
    + V(u'code_n_desc', None, u'小节数序') + u'), 号码清单 '
    + u' ⇎ '.join(u'[' + u' '.join(c) + u']' for c in F[u'codes']) + u' 并集 ' + u' '.join(F[u'code_union'])
    + u' 枚。 304 在 2616 与 9110 的清单里, 7231 把它整族挪去并发规范(判定 ' + V(u'304_absent_in_7231', None, u'304缺席')
    + u'), 7538 只有一份小节(' + AN(2, u'The 308 (Permanent Redirect) status code') + u'), 308 只活在 7538⇎9110 的清单里(判定 '
    + V(u'308_only_7538_9110', None, u'308两份') + u')。 数字 308 在四档面上的枚数 ' + J(u's308_raw', u'308原面') + u' ⇎ '
    + J(u's308_fold', u'308折平') + u' ⇎ ' + J(u's308_sh', u'308摘壳') + u' ⇎ ' + J(u's308_quot', u'308剥引文')
    + u': 折行与剥引文都不动它, 唯独摘壳少 ' + V(u's308_shell', 2, u'壳内308·7538') + u' 枚——全在 7538 的页眉里('
    + AN(2, u'The 308 (Permanent Redirect) status code') + u' 那份的 running header 把争议号码本身印成页眉), 判定 '
    + V(u'shell_308_only_7538', None, u'壳内308唯一') + u'。 游标读数另数一遍: 面上 302 ' + J(u'num_sec_302', u'302枚')
    + u' ⇎ 307 ' + J(u'num_sec_307', u'307枚') + u' ⇎ 308 ' + J(u'num_sec_308', u'308枚') + u' ⇎ 3xx 全族数字串 '
    + J(u'num_status_digits', u'3xx串') + u' 枚。 305 的名分在 9110 里是判废弃: 面上 “is now deprecated” '
    + V(u'dep_all', None, u'废弃判词枚数') + u' 枚 ⇎ 其中 305 小节那条 ' + V(u'dep_305_sent', None, u'305判词枚数')
    + u' 枚(判定 ' + V(u'dep_305_one', None, u'305判词唯一') + u')。')

LINES.append(
    u'🔗 谁废止谁全部行内现读: Obsoletes '
    + u' ⇎ '.join(u'[' + u' '.join(str(y) for y in v) + u']' for v in F[u'obs_ids']) + u' ⇎ Updates '
    + u' ⇎ '.join(u'[' + u' '.join(str(y) for y in v) + u']' for v in F[u'upd_ids'])
    + u', 动作头对象并集 ' + V(u'target_n', None, u'对象并集') + u' 枚('
    + u' '.join(str(y) for y in F[u'target_ids']) + u'), 链 2068←2616←7231←9110 判定 '
    + V(u'obs_chain', None, u'废止链') + u'(9110 的清单里没有 2616, 它隔着 7231 吃下 2616 的血统)。 7538 的 Obsoletes 只列自己的草案期号 7238(判定 '
    + V(u'7538_obsoletes_own_draft', None, u'自号废止') + u', ' + AN(2, u'The 308 (Permanent Redirect) status code')
    + u' 抬头)。 标题页年份 ' + J(u'years', u'年份') + u'(' + u'⇎'.join(F[u'months']) + u'), 倒序 '
    + V(u'year_inversions', None, u'年份倒序')
    + u' 处, 年距 ' + u'⇎'.join(str(x) for x in F[u'year_gaps']) + u'。 引用写法三式并计: 2616 被 ' + J(u'cite_al_2616', u'引2616')
    + u' 次 ⇎ 7231 ' + J(u'cite_al_7231', u'引7231') + u' ⇎ 7538 ' + J(u'cite_al_7538', u'引7538') + u' ⇎ 9110 '
    + J(u'cite_al_9110', u'引9110') + u', 括号式 [RFCNNNN] ' + J(u'cite_br_7231', u'括号7231') + u' 枚, 三式账 '
    + J(u'cite_forms_close', u'写法账') + u' 逐份归零; 7231→9110 方向读 ' + V(u'cite_dir_7231_to_9110', None, u'7231到9110')
    + u' 枚 ⇎ 反向 ' + V(u'cite_dir_9110_to_7231', None, u'9110到7231') + u' 枚(9110 废止它, 当然读得到; 反之 7231 面上零枚 7538: '
    + V(u'cite_7538_in_7231', None, u'7231引7538') + u' 枚)。 自指 ' + J(u'cite_self', u'自指') + u' 枚。')

LINES.append(
    u'⚖ 义务语气四轨: MUST 全计 ' + J(u'up_must_all', u'MUST全计') + u' ⇎ 裸 MUST ' + J(u'must_bare', u'裸MUST')
    + u' ⇎ MUST NOT ' + J(u'must_not', u'MUSTNOT') + u'(大写账 ' + J(u'up_ledger', u'大写账') + u' 逐份归零, 判定 '
    + V(u'up_ledger_zero', None, u'大写账零') + u') ⇎ MAY ' + J(u'up_may', u'MAY') + u' ⇎ SHOULD ' + J(u'up_should', u'SHOULD')
    + u' ⇎ SHOULD NOT ' + J(u'should_not', u'SHOULDNOT') + u' ⇎ MAY NOT ' + J(u'may_not', u'MAYNOT') + u' 枚(四份都不用 MAY NOT)。 '
    + u'小写 must ' + J(u'low_must', u'小写must') + u' ⇎ 不分大小写 ' + J(u'ci_must', u'大小写must') + u', 大小写账 '
    + J(u'case_ledger', u'大小写账') + u' 逐份归零(判定 ' + V(u'case_ledger_zero', None, u'大小写账零') + u')。 '
    + u'份量差得悬殊但不是重点: 7538 一份只有 ' + V(u'up_must_all', 2, u'MUST·7538') + u' 枚大写 MUST(' + AN(2, u'A 308 response is cacheable')
    + u' 那份只管一枚状态码), 2616 ' + V(u'up_must_all', 0, u'MUST·2616')
    + u' 枚; 同一份里 7538 也把义务写成散文 ought to 而非关键词(' + AN(2, u'Clients with link editing capabilities')
    + u')。 method 一词 ' + J(u'method_word', u'method词')
    + u' ⇎ redirect ' + J(u'redirect_word', u'redirect词') + u' 枚。')

LINES.append(
    u'🪟 答句邻域按 ±' + V(u'win_band', None, u'窗带') + u' 行切: 答句行 ' + J(u'win_ans', u'答句行') + u', 窗 '
    + J(u'win_start', u'窗起') + u'.. ' + J(u'win_end', u'窗止') + u'(' + J(u'win_rows', u'窗行数') + u' 行, 窗字符 '
    + J(u'win_chars', u'窗字符') + u')。 带内四轨: redirect ' + J(u'win_redirect_in', u'窗内redirect') + u' ⇎ GET '
    + J(u'win_GET_in', u'窗内GET') + u' ⇎ POST ' + J(u'win_POST_in', u'窗内POST') + u' ⇎ MUST ' + J(u'win_MUST_in', u'窗内MUST')
    + u' 枚; 带外 ' + J(u'win_redirect_out', u'窗外redirect') + u' ⇎ ' + J(u'win_GET_out', u'窗外GET') + u' ⇎ '
    + J(u'win_POST_out', u'窗外POST') + u' ⇎ ' + J(u'win_MUST_out', u'窗外MUST') + u' 枚。 数字符带内 ' + J(u'win_dig_in', u'窗内数字')
    + u' ⇎ 带外 ' + J(u'win_dig_out', u'窗外数字') + u' ⇎ 全篇 ' + J(u'digit_chars', u'数字符') + u', 四轨闭合 '
    + V(u'win_close_sum', None, u'窗闭合') + u'(逐份 ' + J(u'win_close_dig', u'窗闭合·份') + u')。 9110 的窗内读到 MUST '
    + V(u'win_MUST_in', 3, u'窗内MUST·9110') + u' 枚而 7538 ' + V(u'win_MUST_in', 2, u'窗内MUST·7538')
    + u' 枚——9110 的窗中心是那条 “converged” 注(' + AN(3, u'converged on changing the method')
    + u'), 它下一句给出自动重定向的默认 ' + AN(3, u'MAY automatically redirect its request')
    + u', 同一份里“历史原因”注与改写清单隔 ' + V(u'step_hist_abs', None, u'注⇎清单行距') + u' 行, 而且清单在前(判定 '
    + V(u'step_before_hist', None, u'清单在前') + u') ⇎ 7231 次序相反, 约束句落在历史原因句之后 '
    + V(u'hist_mustnot_gap', None, u'历史⇎不得行距') + u' 行(判定 ' + V(u'hist_after_7231', None, u'不得在后') + u')。')

LINES.append(
    u'📦 共用长行池(归一同形、长度 ≥40、非壳) ' + V(u'pool_n', None, u'池条数') + u' 条, 按几份同现分档 '
    + u' ⇎ '.join(V(u'pool_tier', i, u'池分档·%d 份同现' % (i + 1)) for i in range(NSRC)) + u'(闭合 ' + V(u'pool_tier_close', None, u'池分档闭合') + u'): 两份 '
    + V(u'pool_2', None, u'两现长行') + u' ⇎ 三份 ' + V(u'pool_3', None, u'三现长行') + u' ⇎ 四份 ' + V(u'pool_4', None, u'四现长行')
    + u' 条。 六对(' + u' ⇎ '.join(F[u'pair_lbl']) + u')归一同形 ' + P6(u'pair_share', u'同形对') + u' ⇎ 逐字节同形 '
    + P6(u'pair_byte', u'字节对') + u' ⇎ 只归一同形 ' + P6(u'pair_norm_only', u'仅归一对') + u', 最大一对 '
    + V(u'pair_max_lbl', None, u'最大对名') + u' 达 ' + V(u'pair_max', None, u'最大对枚数') + u' 行(逐字节 '
    + V(u'pair_max_byte', None, u'最大对字节') + u' ⇎ 仅归一 ' + V(u'pair_max_norm_only', None, u'最大对仅归一')
    + u')——7231 与 9110 这对是规范血统的物证: 9110 整段复用 7231 行文, 行被重新 wrap 的只有 '
    + V(u'pair_max_norm_only', None, u'最大对仅归一') + u' 行。 代数闭合 ' + V(u'pair_close', None, u'配对闭合')
    + u' ⇎ 容斥闭合 ' + V(u'union_close', None, u'容斥闭合') + u' ⇎ 分档闭合 ' + V(u'pool_tier_close', None, u'池分档闭合')
    + u'; 归一同形而逐字节不同的串 ' + V(u'norm_only_set', None, u'仅归一串数') + u' 条按“差在哪”分四桶 ' + F[u'axis_str']
    + u'(非零档 ' + V(u'axis_str_n', None, u'轴档非零数') + u' 个, 轴账闭合 ' + V(u'axis_close', None, u'轴账闭合')
    + u')。 锚候选池按标签 ' + J(u'apool_tag_n', u'锚池标签') + u' ⇎ 按份数 '
    + u' ⇎ '.join(V(u'apool_tier', i, u'锚池分档·%d 份同现' % (i + 1)) for i in range(NSRC))
    + u', 两本账闭合 ' + V(u'apool_tag_close', None, u'锚池标签闭合') + u' ⇎ ' + V(u'apool_tier_close', None, u'锚池分档闭合') + u'。')

LINES.append(
    u'🔢 序列化对照针: 9110 那句 “For historical reasons, a user agent MAY change the | request method …” 在折平面上带竖线读到 '
    + V(u'ser_fold_hit', None, u'带竖线枚数') + u' 枚 ⇎ 剥引文面上 ' + V(u'ser_quot_hit', None, u'带竖线剥后')
    + u' 枚(判定 ' + V(u'ser_pair', None, u'序列化对照') + u'), 而剥掉竖线后的同一句在剥引文面读到 '
    + V(u'n_a9110_302_hist_may', 3, u'剥竖线枚数·9110') + u' 枚——枚数不变, 搬的不是内容('
    + AN(3, u'For historical reasons') + u')。 竖线账两尺: 折平面 ' + J(u'bar_fold', u'竖线折平') + u' ⇎ 剥后 '
    + J(u'bar_quot', u'竖线剥后') + u', 被剥 ' + J(u'bar_removed', u'竖线剥掉') + u' 枚, 与逐行剥前后各数一次的行尺 '
    + J(u'bar_removed_line', u'竖线行尺') + u' 逐份同值; 剥引文丢的针只有这一枚序列化对照('
    + V(u'quot_lost_n', None, u'剥丢针数') + u' 枚, 内容针丢 ' + V(u'quot_lost_nonserv', None, u'剥丢内容针') + u' 枚)。 '
    + u'9110 面上含竖线行 ' + V(u'pipe_lines', 3, u'竖线行·9110') + u' 行 ⇎ 其余三份 '
    + u'⇎'.join(str(F[u'pipe_lines'][i]) for i in range(3)) + u' 行——前三份的竖线是 ABNF/表格边框, 只有 9110 用它做引文块。 '
    + u'换页符与剥壳在这一条里只管页码: 整行只有换页符的 ' + J(u'ff_exact', u'换页独占行') + u' 行 ⇎ 建条目侧另有一档按 x.strip()==FF 判, '
    + u'strip 先吃掉换页符本身, 该档恒零 ' + J(u'ff_only', u'换页strip档') + u'(口径陷阱如实记); 行数恒等式 '
    + J(u'lines_split', u'splitlines行') + u' ⇎ 换行计数档 ' + J(u'lines_nl', u'换行档') + u'(闭合 ' + V(u'lines_split_close', None, u'行数闭合')
    + u', 判定 ' + V(u'lines_split_zero', None, u'行数账零') + u')。')

LINES.append(
    u'🧮 闭合账总口径: 标量恒等式 ' + V(u'scalar_clos_n', None, u'恒等式数') + u' 条, 通过 ' + V(u'scalar_clos_sum', None, u'恒等式通过')
    + u' 条 ⇎ 清单式闭合 ' + V(u'list_clos_n', None, u'清单闭合') + u' 项 ⇎ 面内恒等式同数共键 ' + V(u'x_ident_n', None, u'共键恒等式')
    + u' 条; 与采集遍逐键对账 ' + V(u'pick_agree', None, u'对账相符')
    + u' 键相符 ⇎ ' + V(u'pick_diff', None, u'对账不符') + u' 键不符(只对同定义标量; 壳账不横比、改按行分解), '
    + u'两遍的壳账差异已在上面按行分解(不是当作数据差异处理)。 '
    + u'反向对照 ' + V(u'neg_ctrl_n', None, u'反向针数') + u' 枚 ⇎ 名下针 ' + J(u'needles_owned', u'名下针') + u' 枚。 '
    + u'四份都是 RFC Editor 纯文本面且全 LF(回车 ' + J(u'cr', u'CR') + u'), NUL ' + J(u'nul_faces', u'NUL') + u' 枚; '
    + u'2616 的双空格 ' + V(u'dblspace', 0, u'双空格·2616') + u' 处是页眉页脚对齐留下的排版层, 与内容无关('
    + V(u'dblspace', 3, u'双空格·9110') + u' 处对 9110)。')

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
MISSLINE = [x for x in CITES if x[1] not in L[IDX[x[0]]]]
assert not ERR, ERR[:3]
assert not MISSLINE, MISSLINE[:3]
HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCHS)
CLS = {u'single': len([a for a in ANCHS if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC]),
       u'all4': len([a for a in ANCHS if len(HITC[a]) == NSRC])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'], u'anchor_all4': CLS[u'all4'],
         u'checks': DIST * NSRC, u'enc_chars': len(body.replace(NL, u'')), u'nsrc': NSRC}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all4'] == DIST
assert not ATOMFAIL, ATOMFAIL
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
    got = [e for e in ELEMS.get(s, []) if eval(e, {FN: BB72}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, NOEXPR
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv72.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
F['contract_n'] = len(F) + 1
json.dump(F, io.open(u'corpus/_b72flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms72.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCHS, key=len, reverse=True)) + NL)

CH = dict(AMETA)
CH.update({u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCHS))),
           u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
           u'classes': dict((c, sorted([a for a in ANCHS if len(HITC[a]) == n]))
                            for c, n in ((u'single', 1), (u'cross', 2), (u'three', 3), (u'four', 4))),
           u'collisions': dict((k, v) for k, v in COLL.items()),
           u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
           u'deriv_points': sum(len(v) for v in SEENX.values()), u'notes': NOTES,
           u'needle_n': F[u'needle_n'], u'zid': [[v, w] for v, w in ZV], u'litk': LITK, u'sn': SN,
           u'closure_keys': sorted([k for k in F if u'close' in k or k in (u'up_ledger', u'case_ledger')]),
           u'flat': F})
json.dump(CH, io.open(u'corpus/_b72checks.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

ENTRY = u'corpus/babeltele/B72_redirect_method_rewrite_four_answers.md'
srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 码位／原行 %d／非空行 %d／最长行 %d 列／答句 %s／页壳换页 %d 枚／竖线行 %d 行)' % (
        PATH[i].split('/')[-1], F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        F[u'maxlen'][i],
        [u'客户端不许改写方法、但实现都当 303 用、301 要确认',
         u'出于历史原因 MAY 改写、307 MUST NOT 改写、306 一族不许',
         u'另立 308 不许改写、308 的使用限于服务器有把握的场合',
         u'收下历史原因句、改写动作写成五条清单、305 已废弃'][i],
        F[u'ff'][i], F[u'pipe_lines'][i]) for i in range(NSRC))
    + u' (四份同为 RFC Editor 纯文本面, 全 LF; 三份纯 ASCII ⇎ 9110 带 BOM ' + str(F[u'bom'][3]) + u' 枚与 '
      + str(F[u'nonascii'][3]) + u' 枚非 ASCII; 30x 小节 ' + u'⇎'.join(str(x) for x in F[u'code_n'])
      + u' 个 ⇎ 号码并集 ' + u' '.join(F[u'code_union']) + u', 标题页年份 ' + u'⇎'.join(str(y) for y in F[u'years'])
      + u', 动作头对象 ' + u' '.join(str(y) for y in F[u'target_ids']) + u' 全部由行内游标或位置导出, 一个都不手填。 '
        u'抓取时刻、RFC Editor 此刻的现行状态页与勘误页(2616/7231 此刻的“现行/历史”标签与是否有后续勘误不可由在库文件判定——在库字节只给得出抬头里的 Obsoletes/Updates 清单)、'
        u'被废止文书自己的现行文本、现网客户端与浏览器实际怎么改写方法, 都只在本机或站外成立, 不进门槛)\n')
link = (u"；联结不是“同一份数据的两种序列化”, 而是“302 之后到底能不能把 POST 改成 GET”在四份 HTTP 一手规范里的四种答法: "
        u"2616 说客户端“不许改写”, 同时承认实现都把 302 当 303 用, 301 则要求确认(确认门句式面上 %d 枚 ⇎ 后三份 %d 枚); " % (
            F['tier_confirm_gate'][0], sum(F['tier_confirm_gate'][1:]))
        + u" ⇎ 7231 把它软成 “For historical reasons … MAY change”(%d 枚), 给 307 立下 “MUST NOT change”(%d 枚), 又在 306 注里数 “does not allow changing”(%d 枚); " % (
            F['tier_may_change'][1], F['tier_must_not_change'][1], F['tier_not_allow_changing'][1])
        + u" ⇎ 7538 不去争论 302, 直接另立 308: “indicates … does not allow changing”(%d 枚)、把 308 的使用限制在“服务器有足够把握客户端懂这个新码”的场合(%d 枚), 全份只有 %d 枚大写 MUST; " % (
            F['tier_not_allow_changing'][2], F['n_a7538_restricted'][2], F['up_must_all'][2])
        + u" ⇎ 9110 把 7231 那句逐字收下(%d 枚 ⇎ 剥引文前后 %d/%d), 改写动作落在一份 %d 条的编号清单里(“Change the request method according to the redirecting status code”, 1 枚), 把 305 判为已废弃(%d 枚废弃判词里 %d 枚属于 305 小节)。" % (
            F['tier_may_change'][3], F['tier_may_change'][3], F['tierq_may_change'][3],
            F['mod_steps'], F['dep_all'], F['dep_305_sent'])
        + u"行级逐字搬运集中在 7231⇎9110 那一对: 字母长行池 %d 条里两份同现 %d 条、最大一对(%s) %d 行 ⇎ 其中逐字节 %d 行; 写法分家四桶 %s。" % (
            F['pool_n'], F['pool_2'], F['pair_max_lbl'], F['pair_max'], F['pair_max_byte'], F['axis_str']))
title = (u'# B72 302 之后到底能不能把 POST 改成 GET，四份 HTTP 一手文书四种答法：'
         u'客户端不许改写但实现都当 303 用、301 要确认 ⇎ 出于历史原因 MAY 改写、307 一律 MUST NOT 改写 ⇎ '
         u'不去争论 302、另立 308 并把其使用限于有把握的场合 ⇎ 原样收下历史原因句、把改写动作写成五条编号清单、顺手把 305 判废弃'
         u'（不许⇎可改⇎另立⇎流程化 四件事没有一份同时给全）\n')
tags = (u'四种答法分给四份文书 确认门句式只在 2616(3⇎0⇎0⇎0, 判定现读) “MAY change”成对在 7231⇎9110 ⇎ “does not allow changing”成对在 7231⇎7538 '
        u'“erroneously”只活首尾两份(2616 数 ⇎ 9110 捡回) 同一句在 7231⇎9110 逐词相等(共尾⇎共头⇎词序全同判定) 段落词集账闭合 '
        u'四档阶梯(逐行⇎折平⇎摘壳⇎剥引文, 折行救 %d 枚 ⇎ 剥引文再救 %d 枚) 9110 的 `| *Note:*` 引文块把竖线楔进句中(带竖线 %d 枚⇎剥后 0 枚⇎枚数不变) '
        u'最宽档落空 5 枚=反向 4+序列化对照 1(内容针全读得到) 两遍壳谓词分解到行(本遍多判 %d 行全抬头⇎采集多判 %d 行全正文) 页眉印着 308 的只有 7538(摘壳少 %d 枚) '
        u'30x 小节清单 8⇎7⇎1⇎9(304 在 7231 缺席 ⇎ 308 只在后两份) 数字四档面枚数对账(折行⇎摘壳⇎剥引文) 废止链 2068←2616←7231←9110 ⇎ 7538 废止自己的草案期号 7238 '
        u'引用三式并计(空格⇎短横⇎连写, 账逐份归零) ⇎ 方向单向(7231 面上零枚 7538) 义务语气四轨(全计⇎裸⇎NOT⇎小写⇎不分大小写, 两账归零) ⇎ 7538 只有 2 枚大写 MUST '
        u'答句邻域窗四轨(redirect⇎GET⇎POST⇎MUST, 带内+带外=全篇) 共用长行池 %d 条分档 ⇎ 最大一对 %d 行(逐字节 %d) 写法分家四桶 %s '
        u'9110 零换页符使摘壳档空转 ⇎ 竖线两尺同值(glyph 尺⇎行尺) 闭合账 标量 %d⇎清单 %d 项⇎恒等式 %d 条 ⇎ 与采集遍对账 %d 键符 %d 不符\n' % (
            F['fold_only_n'], F['quot_only_n'], F['ser_fold_hit'], F['shell_mk_only'][0], F['shell_pick_only'][0],
            F['s308_shell'][2], F['pool_n'], F['pair_max'], F['pair_max_byte'], F['axis_str'],
            F['scalar_clos_n'], F['list_clos_n'], F['x_ident_n'], F['pick_agree'], F['pick_diff']))
text = (title + srcline + link + tags +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n'
        + u'## ⟪BabelTele⟫\n' + body + u'\n\n'
        + u'## ⛓解读注\n\n（此段由 corpus/_fill72.py 从 corpus/_b72checks.json 与 corpus/_deriv72.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s ｜ 归属错配 %d ⇎ 非原行 %d' % (USED, DIST, TAGN, len(ERR), len(MISSLINE)))
print(u'一源 %d ⇎ 二至三源 %d ⇎ 四源 %d ｜ 针 %d ⇎ 折行独有 %d(%s) ⇎ 剥引文独有 %d(%s) ⇎ 四档 %s⇎%s⇎%s⇎%s ⇎ 死针 %s' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], F[u'needle_n'], F[u'fold_only_n'], F[u'fold_only_own'],
    F[u'quot_only_n'], F[u'quot_only_keys'], F[u'sn_strict_docs'], F[u'sn_fold_docs'], F[u'sn_sh_docs'],
    F[u'sn_quot_docs'], F[u'dead_needles']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ⇎ 恒等式 %d ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), F[u'x_ident_n'], len(F)))
print(u'段落 起 %s 止 %s 行 %s 词 %s 字符 %s 独有 %s 交集 %s 词表 %s 闭合 %d 共尾 %d/%d 共头 %d/%d 同 %d/%d' % (
    F[u'blk_lo'], F[u'blk_hi'], F[u'blk_rows'], F[u'blk_words'], F[u'blk_chars'], F[u'blk_only'],
    F[u'blk_common_1'], F[u'blk_vocab'], F[u'w_row_close'], F[u'suf_7231_9110'], F[u'suf_2616_7231'],
    F[u'pre_7231_9110'], F[u'pre_2616_7231'], F[u'blk_same_7231_9110'], F[u'blk_identical_chars']))
print(u'段语气 %s/%s/%s 裸 %s 账 %s ｜ 行距 注⇎当303 %d 历史⇎不得 %d 定义⇎限制 %d 历史⇎步骤 %d' % (
    F[u'tone_must'], F[u'tone_may'], F[u'tone_should'], F[u'tone_bare_must'], F[u'tone_ledger'],
    F[u'note_treat_gap'], F[u'hist_mustnot_gap'], F[u'ind_restricted_gap'], F[u'hist_step_gap']))
print(u'措辞 %s ⇎ %s ｜ 30x %s %s ｜ 年 %s 废止 %s 更新 %s' % (
    F[u'tier_fold_tot'], F[u'tier_quot_tot'], F[u'code_n'], F[u'code_union'], F[u'years'],
    F[u'obs_ids'], F[u'upd_ids']))
print(u'池 n=%d tier=%s share=%s 字节=%s 仅归一=%s 最大 %s(%d) 闭合=%d/%d/%d 轴=%s ⇎ 锚池 %d tier=%s' % (
    F[u'pool_n'], F[u'pool_tier'], F[u'pair_share'], F[u'pair_byte'], F[u'pair_norm_only'],
    F[u'pair_max_lbl'], F[u'pair_max'], F[u'pair_close'], F[u'union_close'], F[u'pool_tier_close'],
    F[u'axis_counts'], F[u'apool_n'], F[u'apool_tier']))
print(u'判定 %s' % (CLOSE,))
