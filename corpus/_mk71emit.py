# -*- coding: utf-8 -*-
"""建条目第二遍(B71)的后半: 由 _mkB71.py 在顶层 exec 进来, 与前半共享同一批现读量。
本半只做三件事: 把 4507 ⇎ 5077 ⇎ 8446 的同一段 hint 规则做成可算的段落对照(段界只按字面针
在折平面上定位, 折平偏移再映回原行号)、排编码区正文、发 DERIV/checks/atoms/条目文件。
正文里每一枚三位以上的数都由 V()/J()/EXPR() 注册过算式。"""

# --- SCAN2 BEGIN --- (并键段: 同一段也机械切进 audit.py::_b71_scan)
def fmap(i):
    """摘壳折平面上的偏移 ⇎ 原行号双向尺: 段界按剥壳后的面量, 行号仍指回原文件"""
    mp = []
    off = 0
    first = True
    for n, x in enumerate(L[i], 1):
        if shell_line(x):
            continue
        s = u' '.join(x.split())
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
    assert u' '.join(u' '.join(x.split()) for x in SH[i] if u' '.join(x.split())) == SHF[i], i


def line_of(i, a):
    r = 0
    for o, n in FMP[i]:
        if o <= a:
            r = n
        else:
            break
    return r


def blk(i, start, end):
    """段落 = 折平面上从 start 起到 end(含) 的那一段; 起止都只按字面针定位, 行号由偏移现映"""
    a = SHF[i].find(start)
    if a < 0:
        raise AssertionError(u'段起针落空 %s' % start)
    b = SHF[i].find(end, a)
    if b < 0:
        raise AssertionError(u'段止针落空 %s' % end)
    e = b + len(end)
    return u' '.join(SHF[i][a:e].split()), line_of(i, a), line_of(i, e - 1)


def ln_of(i, nd):
    a = SHF[i].find(nd)
    if a < 0:
        raise AssertionError(u'行针落空 %s' % nd)
    return line_of(i, a)


P45, P45_LO, P45_HI = blk(0, u'A value of zero is reserved', u'ticket_lifetime_hint.')
P50, P50_LO, P50_HI = blk(1, u'A value of zero is reserved', u'ticket_lifetime_hint.')
P84, P84_LO, P84_HI = blk(2, u'A server MAY treat a ticket', u'ticket_lifetime.')
F['blk_lo'] = [P45_LO, P50_LO, P84_LO]
F['blk_hi'] = [P45_HI, P50_HI, P84_HI]
F['blk_rows'] = [P45_HI - P45_LO + 1, P50_HI - P50_LO + 1, P84_HI - P84_LO + 1]
F['blk_words'] = [len(P45.split()), len(P50.split()), len(P84.split())]
W45 = P45.lower().split()
W50 = P50.lower().split()
W84 = P84.lower().split()
F['w45_only'] = sorted(set(w for w in W45 if w not in W50))
F['w50_only'] = sorted(set(w for w in W50 if w not in W45))
F['w45_only_n'] = len(F['w45_only'])
F['w50_only_n'] = len(F['w50_only'])
F['w_common'] = len(set(W45) & set(W50))
F['w_row_close'] = F['w45_only_n'] + F['w_common'] - len(set(W45))
F['hint_in_45'] = cnt_cur(P45, u'hint')
F['hint_in_50'] = cnt_cur(P50, u'hint')
F['hint_in_84'] = cnt_cur(P84, u'hint')


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


F['suf_45_50'] = suffix_words(W45, W50)
F['pre_45_50'] = head_words(W45, W50)
F['suf_50_84'] = suffix_words(W50, W84)
F['pre_50_84'] = head_words(W50, W84)
F['orlonger_45'] = cnt_cur(P45, u'or longer')
F['orlonger_50'] = cnt_cur(P50, u'or longer')
F['orlonger_84'] = cnt_cur(P84, u'or longer')
F['tone_up_45'] = ub(P45, u'MUST') + ub(P45, u'MAY') + ub(P45, u'SHOULD')
F['tone_up_50'] = ub(P50, u'MUST') + ub(P50, u'MAY') + ub(P50, u'SHOULD')
F['tone_up_84'] = ub(P84, u'MUST') + ub(P84, u'MAY') + ub(P84, u'SHOULD')
F['tone_cap_84'] = ub(P84, u'MUST NOT')
F['ln_zero_4507'] = ln_of(0, u'A value of zero is reserved')
F['ln_unspec_4507'] = ln_of(0, u'is unspecified.')
F['zero_split_gap'] = F['ln_unspec_4507'] - F['ln_zero_4507']
F['ln_relative_5077'] = ln_of(1, u'relative to when the ticket is received')
F['ln_hintdef_5077'] = ln_of(1, u'ticket_lifetime_hint field contains a hint')
F['relative_span'] = F['ln_relative_5077'] - F['ln_hintdef_5077']
F['ln_cap_8446'] = ln_of(2, u'604800 seconds')
F['ln_zeroind_8446'] = ln_of(2, u'should be discarded immediately')
F['cap_zeroind_span'] = F['ln_cap_8446'] - F['ln_zeroind_8446']
F['dead_needles'] = [k for k in KEYS if not SNF[k][OWNER[k]]]
F['cross_needles'] = [k for k in KEYS if sum(1 for i in range(NSRC) if SNF[k][i]) >= 2]
F['fold_only_n'] = len(F['fold_only_keys'])
F['fold_only_str'] = u' ⇎ '.join(F['fold_only_keys'])
F['line_hit_keys'] = [k for k in KEYS if SN[k][OWNER[k]]]
F['hint_in_blk'] = [F['hint_in_45'], F['hint_in_50'], F['hint_in_84']]
F['orlonger_blk'] = [F['orlonger_45'], F['orlonger_50'], F['orlonger_84']]
# --- SCAN2 END ---

BLKLBL = [u'4507段', u'5077段', u'8446段']


def J3(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, BLKLBL[i])) for i in range(3))


PAIRLBL = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in itertools.combinations(range(NSRC), 2)]
GAPLBL = [u'%s到%s' % (LBL[i], LBL[i + 1]) for i in range(NSRC - 1)]


def P6(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, PAIRLBL[i])) for i in range(6))


LINES = []
LINES.append(
    u'🧭 四源字节 ' + J(u'bytes', u'字节') + u' ⇎ 面内码位 ' + J(u'chars', u'码位') + u' ⇎ 原文件行 '
    + J(u'lines', u'行数') + u' ⇎ 非空行 ' + J(u'nonblank', u'非空行') + u' ⇎ 最长行 ' + J(u'maxlen', u'最长行')
    + u' 列: 4507 给 hint 不封顶(' + AN(0, u'value of zero is reserved') + u') ⇎ 5077 逐字收下同一句并补计时起点 '
    + AN(1, u'relative to when the ticket is received') + u' ⇎ 8446 把字段改名、写出硬上限 '
    + AN(2, u'604800 seconds (7 days)') + u' ⇎ 9001 全篇不自建时长, 只转述 ' + AN(3, u'sets a limit of seven days')
    + u'。 版式: 换页符 ' + J(u'ff', u'换页符') + u' 枚 ⇎ 摘壳剥掉 ' + J(u'shell_strip', u'剥壳行')
    + u' 行 ⇎ 整行只有换页符的 ' + J(u'ff_exact', u'换页独占行') + u' 行(建条目侧另有一档按 x.strip()==FF 判, strip 先吃掉换页符本身, 该档恒零 '
    + J(u'ff_only', u'换页独占行strip档') + u', 口径陷阱如实记); CR ' + J(u'cr', u'CR') + u' 全零, 四份都是 LF 面, BOM '
    + J(u'bom', u'BOM') + u' ⇎ 非 ASCII 码位 ' + J(u'nonascii', u'非ASCII') + u' —— 字节−码位差 '
    + J(u'byte_cp_delta', u'字节码位差') + u' 与每枚非 ASCII 的加字节 ' + J(u'nonascii_extra', u'加字节')
    + u' 逐份相等, 纯 ASCII 面 ' + V(u'ascii_all', None, u'纯ASCII份数') + u' 份(9001 带一枚 BOM 与取变音符)。')

LINES.append(
    u'📐 时长在这一条里是三枚可现读的数: 8446 面上从 “value greater than ” 之后游标读出秒 '
    + V(u'num_cap_faces', 2, u'上限秒·8446') + AN(2, u'604800 seconds (7 days)') + u', 同句括注日数 '
    + V(u'num_cap_days', 2, u'括注日数') + u' ⇎ 4507 面上从 “longer than the ” 读出时 ' + V(u'num_d24', None, u'24时数')
    + u' 小时 ' + AN(0, u'24-hour lifetime') + u' —— 换算现乘得 ' + V(u'num_day_seconds', None, u'日秒数')
    + u' 秒, 上限对它的整除倍率 ' + V(u'num_cap_ratio', None, u'上限倍率') + u' ⇎ 余数 ' + V(u'num_cap_remainder', None, u'上限余数')
    + u'(闭合 ' + V(u'cap_ratio_close', None, u'倍率闭合') + u'), 上下界判定 ' + V(u'day_lt_cap', None, u'日小于上限')
    + u'。 给得出这枚上限的份数 ' + V(u'num_cap_present_docs', None, u'给上限份数') + u'(闭合 '
    + V(u'cap_unique', None, u'上限唯一') + u'): 4507⇎5077 面上折平口径读那句 “MUST NOT use any value greater than” 得 '
    + J(u'must_cap_face', u'上限句折平') + u' 枚, 9001 连 “A value of zero” 都一枚没有(判定 ' + V(u'no_self_lifetime', None, u'9001无自建')
    + u')。 字面轨另数一遍: “604800” ' + J(u'num_cap_lit', u'上限字面') + u' 枚——与 8446 那句大写 MUST NOT 同数(闭合 '
    + V(u'num_cap_lit', 2, u'字面·8446') + u'−' + V(u'n_z8446_cap', 2, u'上限句·8446') + u' 归零)。 混淆用的幂 '
    + V(u'num_mod_pow', None, u'模幂') + u' 只活在 8446 ' + AN(2, u'modulo 2^32') + u'。 字段名换了代, 计数要用词界正则: '
    u'ticket_lifetime_hint ' + J(u'fld_hint', u'hint字段') + u' ⇎ ticket_lifetime ' + J(u'fld_plain', u'plain字段')
    + u' 枚, 声明行 uint32 …_hint; ' + J(u'uint32_hint', u'hint声明') + u' ⇎ uint32 ticket_lifetime; '
    + J(u'uint32_plain', u'plain声明') + u' —— hint 式在后两份面上归零(判定 ' + V(u'field_renamed', None, u'字段改名')
    + u'), 全篇 hint 一词 ' + J(u'hint_word', u'hint词') + u' 枚。')

LINES.append(
    u'🔍 在册 ' + V(u'needle_n', None, u'针总数') + u' 枚答句针走三面阶梯: 原面逐行档各中 ' + J(u'sn_strict_docs', u'逐行档')
    + u' 枚 ⇎ 全篇折平档 ' + J(u'sn_fold_docs', u'折平档') + u' ⇎ 摘壳折平档 ' + J(u'sn_sh_docs', u'摘壳档')
    + u' 枚; 只在折平面存在的 ' + V(u'fold_only_n', None, u'折行独有枚数') + u' 枚(按份 ' + J(u'fold_only_own', u'折行独有·份')
    + u' 枚), 逐行档全落空的恰是 5077: 它名下 ' + V(u'needles_owned', 1, u'5077针数') + u' 枚针在逐行档只命中 '
    + V(u'sn_strict_docs', 1, u'逐行·5077') + u' 枚 ⇎ 折平档 ' + V(u'sn_fold_docs', 1, u'折平·5077') + u' 枚。'
    + u' 最刺眼的是 4507: 它的零值句被页壳劈开——“value of zero is reserved”落在第 ' + V(u'ln_zero_4507', None, u'零句行')
    + u' 行, 半句 “is unspecified.” 在第 ' + V(u'ln_unspec_4507', None, u'未定行') + u' 行, 相隔 '
    + V(u'zero_split_gap', None, u'零句跨页距') + u' 行, 中间隔着页眉页脚 ' + AN(0, u'value of zero is reserved')
    + u' 之后的壳——只按逐行口径搜就会把这份读成“没写完这句”。 阶梯单调账闭合 ' + V(u'ladder_monotone', None, u'阶梯单调')
    + u', 摘壳档比折平档少 ' + J(u'sh_minus_fold', u'摘壳减折平') + u' 枚(壳行里没有答句), 折行针按逐行口径必须全零= '
    + V(u'fold_line_zero', None, u'折行逐行零') + u'。 9001 零换页符 ' + V(u'ff', 3, u'换页·9001')
    + u' 枚 ⇒ 第三档对它是空操作(与 B69 那份零换页符的文书同型), 阶梯在本条只靠折行一条通道。 判定轨也换过: 正则字面轨 ⇎ 非重叠游标轨逐枚相等(闭合 '
    + V(u're_eq_cur', None, u'两轨相等') + u'), 重叠口径多出的 ' + V(u'overlap_extra', None, u'重叠多余') + u' 枚为零。'
    + u' 跨面同现的针 ' + V(u'cross_needle_n', None, u'跨面针枚数') + u' 枚(句子被复制, 整行没被复制)。')

LINES.append(
    u'🗣 零值是什么意思, 是这一条最锋利的一处翻转: 4507 ⇎ 5077 都写 “A value of zero is reserved to indicate that the '
    u'lifetime of the ticket is unspecified.”(针轨逐份 ' + J(u'n_z4507_zero_reserved', u'零=未定·4507针') + u' ⇎ '
    + J(u'n_z5077_zero_reserved', u'零=未定·5077针') + u' 枚; 搬运是双向的, 但双向都只在剥壳之后成立: 摘壳折平面上 5077 的整句'
    u'(连句号)在 4507 面读到 ' + V(u'zero_carry_sh', 1, u'整句·5077在4507摘壳面') + u' 枚 ⇎ 同一枚针在含页壳的全篇折平面上只剩 '
    + V(u'zero_carry_fold', 1, u'整句·5077在4507全篇面') + u' 枚——那句在 4507 里被页壳劈开, 不剥壳就读不到整句; '
    u'反过来 4507 的短针(不带后半句)在自己面 ' + V(u'n_z4507_zero_reserved', 0, u'短针·4507本面') + u' 枚 ⇎ 5077 面 '
    + V(u'n_z4507_zero_reserved', 1, u'短针·4507在5077') + u' 枚, 折平⇎摘壳两档同数('
    + V(u'zero_carry_sh', 0, u'短针·4507在5077摘壳面') + u'/' + V(u'zero_carry_fold', 0, u'短针·4507在5077全篇面')
    + u'), 零=未定一致闭合 ' + V(u'zero_res_agree', None, u'零未定一致')
    + u') ⇎ 8446 把同一个值翻成 “The value of zero indicates that the ticket should be discarded immediately” '
    + AN(2, u'should be discarded immediately') + u'(该句式全库唯一判定 ' + V(u'zero_ind_unique', None, u'立即丢弃唯一')
    + u' 之外的翻转判定 ' + V(u'zero_flip', None, u'零值翻转') + u'), 两式在 8446 的同一句里前后相隔 '
    + V(u'cap_zeroind_span', None, u'上限⇎零值行距') + u' 行 ⇎ 9001 面上 “A value of zero” '
    + V(u'n_z9001_zero', 3, u'零句式·9001') + u' 枚——它既不封顶也不定义零。 语气换代同步发生: 大写 MUST '
    + J(u'up_must_all', u'大写MUST') + u' ⇎ 裸 MUST ' + J(u'must_bare', u'裸MUST') + u' ⇎ MUST NOT '
    + J(u'must_not', u'MUSTNOT') + u' ⇎ MAY ' + J(u'up_may', u'大写MAY') + u' ⇎ SHOULD ' + J(u'up_should', u'大写SHOULD')
    + u'; 大写账闭合 ' + J(u'up_ledger', u'大写账') + u' ⇎ 大小写账闭合 ' + J(u'case_ledger', u'大小写账')
    + u'; 小写轨 must ' + J(u'low_must', u'小写must') + u' ⇎ 全小写针 “client should delete” '
    + J(u'should_delete', u'丢弃句全小写针') + u' 枚四份都落空——这两份把义务词写成大写 SHOULD, 全小写针在此是口径陷阱, 如实记 0; '
    u'同一句按原大小写做针则 ' + J(u'n_z4507_should_delete', u'丢弃句原样针') + u' 枚, 逐字搬运只发生在 4507⇎5077 之间。 '
    u'“不得复用”直到 8446 才出现: SHOULD NOT '
    + J(u'should_not', u'SHOULDNOT') + u' 枚, 判定 ' + V(u'reuse_absent', None, u'复用缺席') + u'。')

LINES.append(
    u'🎯 同一件事的四种答法可以逐词量出来。三段现定界在起 ' + J3(u'blk_lo', u'段起行') + u' ⇎ 止 '
    + J3(u'blk_hi', u'段止行') + u' 行(占 ' + J3(u'blk_rows', u'段行数') + u' 行), 折平后词数 ' + J3(u'blk_words', u'段词数')
    + u' ⇎ 去重共有词 ' + V(u'w_common', None, u'共有词') + u' 枚, 只在 4507 段的 ' + V(u'w45_only_n', None, u'4507独有枚数')
    + u' 枚 ⇎ 只在 5077 段的 ' + V(u'w50_only_n', None, u'5077独有枚数') + u' 枚, 词集账闭合 '
    + V(u'w_row_close', None, u'词集闭合') + u'; 共尾 ' + V(u'suf_45_50', None, u'共尾·45对50') + u' ⇎ 共头 '
    + V(u'pre_45_50', None, u'共头·45对50') + u' 枚——两个数都等于这两段各自的词数(' + V(u'blk_words', 0, u'段词·4507')
    + u'/' + V(u'blk_words', 1, u'段词·5077')
    + u'), 也就是这一段整段照搬、一个词都没动(行数 ' + V(u'blk_rows', 0, u'段行·4507') + u' ⇎ '
    + V(u'blk_rows', 1, u'段行·5077')
    + u' 只是重新 wrap 的差别)。 5077 补的计时起点不在这段里, 它在字段说明那句(只活在 5077 面, 判定 '
    + V(u'rel_inserted', None, u'起点插入') + u'; 4507 面上反向针零命中 '
    + V(u'n_z4507_no_relative', 0, u'反向针·4507') + u' 枚), 离 hint 定义句 '
    + V(u'relative_span', None, u'定义⇎起点行距') + u' 行。 5077 对 8446 那对: 共尾 ' + V(u'suf_50_84', None, u'共尾·50对84')
    + u' ⇎ 共头 ' + V(u'pre_50_84', None, u'共头·50对84') + u' 枚——尾巴接不上, 因为句尾的字段名换了, hint 一词在三段里 '
    + J3(u'hint_in_blk', u'段内hint') + u' 枚。 “or longer” 那半个出口在三段里各 ' + J3(u'orlonger_blk', u'段内or longer')
    + u' 枚 ⇎ 全篇 “shorter or longer” ' + J(u'orlonger', u'or longer折平') + u' 枚, 而 8446 面上只剩 '
    + AN(2, u'MAY treat a ticket as valid for a shorter period') + u'(句式 ' + J(u'shorter_only', u'只剩shorter')
    + u' 枚, 砍除判定 ' + V(u'drop_or_longer', None, u'砍掉or longer') + u', 其变体在 4507 面零命中 '
    + V(u'n_z8446_shorter_only', 0, u'8446式·4507') + u' 枚); 起算点也被换掉: “from the time of ticket issuance” '
    + J(u'from_issuance', u'issuance折平') + u' 枚(判定 ' + V(u'from_issuance_only', None, u'issuance唯一') + u')。')

LINES.append(
    u'📄 能不能复用是第四个问题: 8446 ' + AN(2, u'SHOULD NOT reuse a ticket for multiple connections')
    + u' ⇎ 9001 ' + AN(3, u'Clients SHOULD NOT reuse tickets as') + u' —— 两式各一枚且互不逐字同现 '
    + J(u'n_z9001_reuse', u'9001复用句') + u' ⇎ ' + J(u'n_z8446_reuse', u'8446复用句')
    + u'(缺席判定 ' + V(u'reuse_absent', None, u'复用缺席') + u'), 而 4507 ⇎ 5077 面上一个 reuse 字都没有: '
    + J(u'reuse_word', u'reuse词') + u' 枚。 9001 的回答方式是转述: “' + AN(3, u'sets a limit of seven days')
    + u'” 把主语交给 [TLS13], 该方括号引用记号逐份 ' + J(u'num_tls13_refs', u'TLS13记号') + u' 枚 ⇎ 它自己的 lifetime 一词仍现 '
    + J(u'lifetime_word', u'lifetime词') + u' 枚(转述判定 ' + V(u'delegates', None, u'转述判定')
    + u')。 度量单位也分家: week ' + J(u'week_word', u'week词') + u' 枚只在 8446(“restricted to a week” '
    + AN(2, u'restricted to a week') + u', 判定 ' + V(u'week_only_8446', None, u'week唯一') + u') ⇎ 24-hour '
    + J(u'd24_hour', u'24小时') + u' 枚恰在前两份(闭合 ' + V(u'24hour_pair', None, u'24小时成对')
    + u'), 后两份连“一天”这个参照都不提; unspecified ' + J(u'unspec_word', u'unspecified') + u' ⇎ 立即 immediately '
    + J(u'imm_word', u'immediately') + u' ⇎ discard ' + J(u'discard_low', u'discard小写') + u' 枚。')

LINES.append(
    u'🔧 谁废谁可以现读: 5077 的 Obsoletes: 头读到 ' + V(u'obs_n', 1, u'废止枚数·5077') + u' 枚对象 '
    + u' ⇎ '.join(EXPR(x, u"B71V('obs_set_5077', %d)" % n, u'5077废止对象') for n, x in enumerate(F['obs_set_5077']))
    + AN(1, u'Obsoletes: 4507') + u' ⇎ 8446 的头读到 ' + V(u'obs_n', 2, u'废止枚数·8446') + u' 枚 '
    + u' ⇎ '.join(EXPR(x, u"B71V('obs_set_8446', %d)" % n, u'8446废止对象') for n, x in enumerate(F['obs_set_8446']))
    + AN(2, u'Obsoletes: 5077, 5246, 6961') + u', 另 Updates: ' + V(u'upd_n', 2, u'更新枚数·8446') + u' 枚 '
    + u' ⇎ '.join(EXPR(x, u"B71V('upd_set_8446', %d)" % n, u'8446更新对象') for n, x in enumerate(F['upd_set_8446']))
    + u'; 4507 ⇎ 9001 两种头各 ' + V(u'obs_n', 0, u'废止·4507') + u'/' + V(u'obs_n', 3, u'废止·9001')
    + u' 枚。 链条闭合判定 ' + V(u'chain_closed', None, u'链条闭合') + u': 5077 被 8446 直接废止、而 4507 只死在 5077 头上'
    u'(它不在 8446 的任何动作头里)。 全库动作对象并集 ' + V(u'target_n', None, u'目标号枚数') + u' 枚: '
    + u' ⇎ '.join(EXPR(x, u"B71V('target_ids', %d)" % n, u'目标号') for n, x in enumerate(F['target_ids']))
    + u' ⇎ 动词字面 Obsoletes ' + J(u'obs_verb', u'废止动词') + u' ⇎ Updates ' + J(u'upd_verb', u'更新动词')
    + u'(后者含小节标题“Updates Affecting TLS 1.2”, 行锚定的头行只有 ' + J(u'upd_line', u'更新头行')
    + u' 行)。 名分同样现读: Category 行逐份 ' + J(u'cat_hdr', u'类别行') + u' ⇎ Standards Track '
    + J(u'cat_std', u'类别ST') + u' 枚(闭合 ' + V(u'cat_close', None, u'类别闭合') + u'), STD: 头 '
    + J(u'std_hdr', u'STD头') + u', ISSN ' + J(u'issn', u'ISSN') + u'。 标题页年份逐行尾锚定现读 ' + J(u'years', u'年份')
    + u'(月 ' + J(u'months', u'月份') + u'), 相邻差 ' + u' ⇎ '.join(V(u'year_gaps', i, u'年距·' + GAPLBL[i]) for i in range(3))
    + u' 年, 倒序 ' + V(u'year_inversions', None, u'年份倒序数') + u' 处、置换 '
    + u' ⇎ '.join(V(u'year_perm', i, u'年份序索引%d' % i) for i in range(4)) + u'(闭合 ' + V(u'year_order', None, u'年份递增')
    + u')——本条的四份是按时间单向推进的, 与 B70 那“恰有一处倒序”的语气换代恰成对照。')

LINES.append(
    u'📏 答句邻域窗(±' + V(u'win_band', None, u'窗带宽') + u' 行)按小节标题定位: 标题行 ' + J(u'win_sec', u'节行')
    + u' ⇎ 答句行 ' + J(u'win_ans', u'答句行') + u' ⇎ 窗 ' + J(u'win_start', u'窗起') + u' 至 ' + J(u'win_end', u'窗止')
    + u'(行数 ' + J(u'win_rows', u'窗行数') + u'), 节行与答句行都命到 ' + V(u'win_named', None, u'命名节数') + u'/'
    + V(u'win_ans_named', None, u'命名答句数') + u' 份(注: 前两式在目录里也有同名行, 节行读到的是目录档, 窗只按答句行切, 不据此判正文小节)。'
    + u' 窗内⇎窗外五轨对账: lifetime 带内 ' + J(u'win_lt_in', u'窗内lifetime') + u' ⇎ 带外 ' + J(u'win_lt_out', u'窗外lifetime')
    + u', zero ' + J(u'win_zero_in', u'窗内zero') + u' ⇎ ' + J(u'win_zero_out', u'窗外zero') + u', 604800 '
    + J(u'win_cap_in', u'窗内上限') + u' ⇎ ' + J(u'win_cap_out', u'窗外上限') + u', reuse ' + J(u'win_reuse_in', u'窗内reuse')
    + u' ⇎ ' + J(u'win_reuse_out', u'窗外reuse') + u', 数字符 ' + J(u'win_dig_in', u'窗内数字') + u' ⇎ '
    + J(u'win_dig_out', u'窗外数字') + u'; 五轨合计闭合 ' + V(u'win_close_sum', None, u'窗账闭合') + u'(逐轨 '
    + J(u'win_close_lt', u'lifetime闭合') + u' ⇎ ' + J(u'win_close_zero', u'zero闭合') + u' ⇎ '
    + J(u'win_close_cap', u'上限闭合') + u' ⇎ ' + J(u'win_close_reuse', u'reuse闭合') + u' ⇎ '
    + J(u'win_close_dig', u'数字闭合') + u')。 密度对照: 8446 面上 604800 全库 ' + V(u'num_cap_lit', 2, u'字面·8446')
    + u' 枚里带内 ' + V(u'win_cap_in', 2, u'窗内上限·8446') + u' 枚 ⇎ 9001 面上 reuse 全库 ' + V(u'reuse_word', 3, u'reuse·9001')
    + u' 枚里带内只有 ' + V(u'win_reuse_in', 3, u'窗内reuse·9001') + u' 枚——前者把上限锁在字段定义处, 后者的复用警告散在 0-RTT 前后。')

LINES.append(
    u'🔗 引用写法三式并计(RFC 空格 ⇎ RFC- 短横 ⇎ RFC 连写), 逐份: 4507 ' + J(u'cite_al_4507', u'4507合计')
    + u' ⇎ 5077 ' + J(u'cite_al_5077', u'5077合计') + u' ⇎ 8446 ' + J(u'cite_al_8446', u'8446合计')
    + u' ⇎ 2246 ' + J(u'cite_al_2246', u'2246合计') + u' ⇎ 4346 ' + J(u'cite_al_4346', u'4346合计') + u'。 '
    + u'子串轨三式相加 ⇎ 一条正则族读出的枚数, 逐份差 ' + J(u'cite_forms_close', u'写法族账') + u'; 2246 的写法族数 '
    + J(u'cite_forms_2246', u'2246写法族') + u' 族——4507 面上它只以方括号连写式出现 ' + AN(0, u'[RFC2246]')
    + u'。 互引方向: 5077 面上引 4507 ' + V(u'cite_4507_in_5077', None, u'5077引4507') + u' 枚 ⇎ 8446 面上引 5077 '
    + V(u'cite_5077_in_8446', None, u'8446引5077') + u' 枚 ⇎ 而 8446 面上读不到 9001 '
    + V(u'cite_dir_8446_to_9001', None, u'8446引9001') + u' 枚(单向判定 ' + V(u'cite_dir', None, u'互引单向')
    + u'——引用只流向后出的一方; 9001 引 8446 走的是 [TLS13] 这个别名而非 RFC 号)。 各份自指 '
    + J(u'cite_self', u'自指') + u' 枚。')

LINES.append(
    u'🧮 逐字搬运在这一条里是“句子级”而非“整行级”: 摘壳原面的 ≥40 列长行池 ' + V(u'pool_n', None, u'长行池')
    + u' 条里含字母的只有 ' + V(u'pool_letters', None, u'字母行长行') + u' 条(其余 ' + V(u'pool_border', None, u'边框行长行')
    + u' 条是 ASCII 图与表格边框), 两份同现 ' + V(u'pool_2', None, u'两现长行') + u' ⇎ 三份同现 '
    + V(u'pool_3', None, u'三现长行') + u' ⇎ 四份同现 ' + V(u'pool_4', None, u'四现长行')
    + u' 条(归一同形而逐字节不同的串共 ' + V(u'norm_only_set', None, u'仅归一串数') + u' 条, 按“差在哪”分四桶: '
    + F[u'axis_str'] + u', 非零档 '
    + V(u'axis_str_n', None, u'轴档非零数') + u' 个, 轴账闭合 ' + V(u'axis_close', None, u'轴账闭合') + u')。 '
    + u'六对(' + u' ⇎ '.join(F[u'pair_lbl']) + u')归一同形 ' + P6(u'pair_share', u'同形对')
    + u' ⇎ 逐字节同形 ' + P6(u'pair_byte', u'字节对') + u' ⇎ 只归一同形 ' + P6(u'pair_norm_only', u'仅归一对')
    + u', 最大一对 ' + V(u'pair_max_lbl', None, u'最大对名') + u' 达 ' + V(u'pair_max', None, u'最大对枚数')
    + u' 行(其中逐字节 ' + V(u'pair_max_byte', None, u'最大对字节') + u' ⇎ 仅归一 ' + V(u'pair_max_norm_only', None, u'最大对仅归一')
    + u')——这就是 4507 与 5077 那对: 段落逐句收下而行被重新 wrap。 代数闭合 ' + V(u'pair_close', None, u'配对闭合')
    + u' ⇎ 容斥闭合 ' + V(u'union_close', None, u'容斥闭合') + u' ⇎ 分档闭合 ' + V(u'pool_tier_close', None, u'池分档闭合')
    + u'。 锚候选池按标签 ' + J(u'apool_tag_n', u'锚池标签') + u' ⇎ 按份数 ' + J(u'apool_tier', u'锚池分档')
    + u', 两本账闭合 ' + V(u'apool_tag_close', None, u'锚池标签闭合') + u' ⇎ ' + V(u'apool_tier_close', None, u'锚池分档闭合')
    + u'。 闭合账总口径: 标量 ' + V(u'scalar_clos_n', None, u'标量恒等式数') + u' ⇎ 清单 '
    + V(u'list_clos_n', None, u'清单闭合数') + u' 项 ⇎ 恒等式 ' + V(u'x_ident_n', None, u'恒等式条数')
    + u' 条, 通过 ' + V(u'scalar_clos_sum', None, u'恒等式通过数') + u' 条。')

for v, w in ZV:
    reg(u'0', v, w)

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
    got = [e for e in ELEMS.get(s, []) if eval(e, {FN: BB71}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, NOEXPR
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv71.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b71flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms71.txt', 'w', encoding='utf-8', newline=NL).write(
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
json.dump(CH, io.open(u'corpus/_b71checks.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

ENTRY = u'corpus/babeltele/B71_tls_ticket_lifetime_four_answers.md'
srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 码位／原行 %d／非空行 %d／最长行 %d 列／答句 %s／页壳换页 %d 枚)' % (
        PATH[i].split('/')[-1], F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        F[u'maxlen'][i],
        [u'零值=寿命未定、hint 只给提示、不设上限、不提议子',
         u'同一句逐字收下、补“相对收到时刻”、仍无上限',
         u'字段改名、零值=立即丢弃、604800 秒 MUST NOT 硬上限、C.4 不得复用',
         u'零枚 604800、只转述“[TLS13] sets a limit of seven days”、另立不得复用'][i],
        F[u'ff'][i]) for i in range(NSRC))
    + u' (四份同为 RFC Editor 纯文本面, 全 LF; 三份纯 ASCII ⇎ 9001 带 BOM ' + str(F['bom'][3]) + u' 枚与 '
      + str(F['nonascii'][3]) + u' 枚非 ASCII; 上限 ' + str(NUM['cap_faces'][2]) + u' 秒 ⇎ 括注日数 '
      + str(NUM['cap_days'][2]) + u' ⇎ 前两份的 24 小时参照, 标题页年份 '
      + u'⇎'.join(str(y) for y in F['years']) + u', 动作头对象 ' + u' ⇎ '.join(str(y) for y in F['target_ids'])
      + u' 全部句内或行内游标现读, 一个都不手填。 抓取时刻、RFC Editor 此刻的现行状态页与勘误页(4507/5077 后来被改判为名分上的 Experimental 一事不可由在库文件判定——在库字节只给得出 Category: Standards Track)、'
        u'被废止者本身的现行文本、现网栈实际缓存多久, 都只在本机或站外成立, 不进门槛)\n')
link = (u"；联结不是“同一份数据的两种序列化”, 而是“一张 TLS 会话恢复票据能活多久、零值是什么意思、一张票能不能复用”在四份一手文书里的四种答法: "
        u"4507 把时长写成 hint(“%s”, 零值=%s ⇎ 全篇 MUST NOT %d 枚、无上限), 丢弃义务用小写 should 与 %s 句式, 只引用 24 小时参照(%s);" % (
            u'ticket_lifetime_hint 提示存多久', u'寿命未定', F['must_not'][0], u'本地策略', u'[RFC2246]')
        + u" ⇎ 5077 逐字收下同一枚零值句(%d 枚)并把计时起点补进同一句(%s, 判定 %d), 仍不封顶;" % (
            F['n_z5077_zero_reserved'][1], u'relative to when the ticket is received', F['rel_inserted'])
        + u" ⇎ 8446 改名去掉 hint(%s %d 枚 ⇎ %s %d 枚)、零值翻成立即丢弃(翻转判定 %d)、写出 %d 秒(= %d 日整)的 MUST NOT 硬上限、"
            u"把“shorter or longer”砍成“shorter”(判定 %d)、起算点换成 issuance(判定 %d), 并在 C.4 首次写下不得复用;" % (
                u'ticket_lifetime_hint', F['fld_hint'][2], u'ticket_lifetime', F['fld_plain'][2],
                F['zero_flip'], NUM['cap_faces'][2], NUM['cap_ratio'], F['drop_or_longer'], F['from_issuance_only'])
        + u" ⇎ 9001 全篇 %d 枚 604800 ⇎ %d 枚 MUST NOT 上限句, 只转述 “[TLS13] sets a limit of seven days”(判定 %d), 另给 Clients SHOULD NOT reuse tickets。"
            u"行级逐字搬运集中在 4507⇎5077 那一对: 字母长行池 %d 条里两份同现 %d 条、最大一对(%s) %d 行 ⇎ 其中逐字节 %d 行; 写法分家四桶 %s。" % (
                NUM['cap_lit'][3], F['must_cap_face'][3], F['delegates'],
                F['pool_letters'], F['pool_2'], F['pair_max_lbl'], F['pair_max'],
                F['pair_max_byte'], F['axis_str']))
title = (u'# B71 一张 TLS 会话恢复票据到底能活多久，四份一手文书四种答法：'
         u'hint 只给提示、零值=寿命未定、不封顶 ⇎ 同一句逐字收下、补“相对收到时刻”、仍无上限 ⇎ '
         u'字段改名去掉 hint、零值=立即丢弃、604800 秒的 MUST NOT 硬上限、shorter or longer 被砍成 shorter ⇎ '
         u'全篇零枚时长规则、只转述“[TLS13] sets a limit of seven days”并另立“不得复用票据”'
         u'（能活多久⇎零值何意⇎从何时起算⇎可否复用 四件事没有一份给全）\n')
tags = (u'tags: 四件事分给四份文书 零值语义翻转(寿命未定 ⇎ 立即丢弃 ⇎ 不定义) 同一枚整句在 4507⇎5077 逐字同现 ⇎ 8446 的句式谁都没抄 '
        u'计时起点三式(无起点 ⇎ 相对收到时刻 ⇎ 从签发时刻) “shorter or longer”被砍成“shorter”(砍除判定现读) '
        u'字段改名用词界正则数(ticket_lifetime_hint ⇎ ticket_lifetime, 声明行逐份) 硬上限 604800 只在一份面(游标⇎字面⇎句轨三档同数, 倍率 7 日整余零) '
        u'24-hour 参照恰成对(4507 ⇎ 5077, 后两份零枚) ⇎ week 只在 8446 三面阶梯(4507 的零值句被页壳劈开, 逐行档 ⇎ 折平档现读) ⇎ 9001 零换页符使第三档空转(与 B69 那份零换页符的文书同型) '
        u'正则字面轨 ⇎ 非重叠游标轨 ⇎ 重叠口径三轨对账 转述式回答([TLS13] 作主语, 全篇不自建时长) 复用禁令只在后两份(8446 与 9001 两式互不逐字同现) '
        u'Obsoletes 链逐号可查(5077←8446; 4507 只死在 5077 头上) Category: Standards Track 四份同名分(后来改判 Experimental 不可由在库文件判定) '
        u'标题页年份严格递增零倒序(与 B70 恰有一处倒序对照) 引用三式并计(空格 ⇎ 短横 ⇎ 连写) ⇎ 9001 用 [TLS13] 别名不用 RFC 号 '
        u'互引单向(8446 面上读不到 9001) 答句邻域窗五轨(lifetime ⇎ zero ⇎ 604800 ⇎ reuse ⇎ 数字符, 带内+带外=全篇) '
        u'节标题在目录重复 ⇒ 窗只按答句行切(口径如实记) 行级逐字搬运只在一对上(最大一对 %d 行 ⇎ 逐字节 %d 行) 写法分家四桶 %s '
        u'锚候选池标签⇎份数两本账 闭合账 标量 %d⇎清单 %d 项⇎恒等式 %d 条\n' % (
            F['pair_max'], F['pair_max_byte'], F['axis_str'],
            F['scalar_clos_n'], len([k for k in F if u'close' in k]), F['x_ident_n']))
text = (title + srcline + link + tags +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n'
        + u'## ⟪BabelTele⟫\n' + body + u'\n\n'
        + u'## ⛓解读注\n\n（此段由 corpus/_fill71.py 从 corpus/_b71checks.json 与 corpus/_deriv71.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s ｜ 归属错配 %d ⇎ 非原行 %d' % (USED, DIST, TAGN, len(ERR), len(MISSLINE)))
print(u'一源 %d ⇎ 二至三源 %d ⇎ 四源 %d ｜ 针 %d ⇎ 折行独有 %d(%s) ⇎ 阶梯 %s⇎%s⇎%s ⇎ 死针 %s' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], F[u'needle_n'], F[u'fold_only_n'],
    F[u'fold_only_own'], F[u'sn_strict_docs'], F[u'sn_fold_docs'], F[u'sn_sh_docs'], F[u'dead_needles']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ⇎ 恒等式 %d ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), F[u'x_ident_n'], len(F)))
print(u'段落 起 %s 止 %s 行 %s 词 %s 共尾 %d/%d 共头 %d/%d 独有(%d/%d %s|%s) hint %d/%d/%d orlonger %d/%d/%d 语气 %d/%d/%d' % (
    F[u'blk_lo'], F[u'blk_hi'], F[u'blk_rows'], F[u'blk_words'], F[u'suf_45_50'], F[u'suf_50_84'],
    F[u'pre_45_50'], F[u'pre_50_84'], F[u'w45_only_n'], F[u'w50_only_n'],
    F[u'w45_only'], F[u'w50_only'], F[u'hint_in_45'], F[u'hint_in_50'], F[u'hint_in_84'],
    F[u'orlonger_45'], F[u'orlonger_50'], F[u'orlonger_84'],
    F[u'tone_up_45'], F[u'tone_up_50'], F[u'tone_up_84']))
print(u'行距 零句跨页 %d (行 %d..%d) 起点 %d 上限⇎零值 %d' % (
    F['zero_split_gap'], F['ln_zero_4507'], F['ln_unspec_4507'], F['relative_span'], F['cap_zeroind_span']))
print(u'数读 %s' % (NUM,))
print(u'窗 节行 %s 答行 %s 窗 %s..%s 行数 %s lt %s/%s zero %s/%s cap %s/%s reuse %s/%s 闭合 %s' % (
    F[u'win_sec'], F[u'win_ans'], F[u'win_start'], F[u'win_end'], F[u'win_rows'],
    F[u'win_lt_in'], F[u'win_lt_out'], F[u'win_zero_in'], F[u'win_zero_out'],
    F[u'win_cap_in'], F[u'win_cap_out'], F[u'win_reuse_in'], F[u'win_reuse_out'], F[u'win_close_sum']))
print(u'池 n=%d 字母=%d 边框=%d tier=%s share=%s 字节=%s 仅归一=%s 最大 %s(%d) 闭合=%d/%d/%d 轴=%s ⇎ 锚池 %d tier=%s' % (
    F[u'pool_n'], F[u'pool_letters'], F[u'pool_border'], F[u'pool_tier'], F[u'pair_share'], F[u'pair_byte'],
    F[u'pair_norm_only'], F[u'pair_max_lbl'], F[u'pair_max'], F[u'pair_close'], F[u'union_close'],
    F[u'pool_tier_close'], F[u'axis_counts'], F[u'apool_n'], F[u'apool_tier']))
print(u'判定 %s' % (CLOSE,))
