# -*- coding: utf-8 -*-
"""建条目第二遍(B70)的后半: 由 _mkB70.py 在顶层 exec 进来, 与前半共享同一批现读量。
本半只做三件事: 把 8200 ⇎ 6935 的同一条 IPv6 规则做成可算的段落对照(段落边界由折平游标现定,
折平偏移再映回原行号)、排编码区正文、发 DERIV/checks/atoms/条目文件。
正文里每一枚三位以上的数都由 V()/J()/EXPR() 注册过算式。"""

# --- SCAN2 BEGIN --- (并键段: 同一段也机械切进 audit.py::_b70_scan)
# ---------- 折平偏移 ⇎ 原行号的双向尺 ----------
def fmap(i):
    mp = []
    off = 0
    first = True
    for n, x in enumerate(L[i], 1):
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
    assert u' '.join(u' '.join(x.split()) for x in L[i] if u' '.join(x.split())) == FOLD[i], i


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
    a = FOLD[i].find(start)
    if a < 0:
        raise AssertionError(u'段起针落空 %s' % start)
    b = FOLD[i].find(end, a)
    if b < 0:
        raise AssertionError(u'段止针落空 %s' % end)
    e = b + len(end)
    return u' '.join(FOLD[i][a:e].split()), line_of(i, a), line_of(i, e - 1)


def ln_of(i, nd):
    a = FOLD[i].find(nd)
    if a < 0:
        raise AssertionError(u'行针落空 %s' % nd)
    return line_of(i, a)


P82, P82_LO, P82_HI = blk(2, u'Unlike IPv4, the default behavior', u'zero checksum and should log the error.')
P6Q, P6Q_LO, P6Q_HI = blk(3, u'Unlike IPv4, when UDP packets are', u'checksum, and should log the error.')
P6R, P6R_LO, P6R_HI = blk(3, u'Whenever originating a UDP packet for a port', u'zero checksum and SHOULD log the error.')
F['blk_lo'] = [P82_LO, P6Q_LO, P6R_LO]
F['blk_hi'] = [P82_HI, P6Q_HI, P6R_HI]
F['blk_rows'] = [P82_HI - P82_LO + 1, P6Q_HI - P6Q_LO + 1, P6R_HI - P6R_LO + 1]
F['blk_words'] = [len(P82.split()), len(P6Q.split()), len(P6R.split())]
W82 = P82.lower().split()
W6Q = P6Q.lower().split()
W6R = P6R.lower().split()
F['w82_only'] = sorted(set(w for w in W82 if w not in W6Q))
F['w6q_only'] = sorted(set(w for w in W6Q if w not in W82))
F['w82_only_n'] = len(F['w82_only'])
F['w6q_only_n'] = len(F['w6q_only'])
F['w_common'] = len(set(W82) & set(W6Q))
F['w_row_close'] = F['w82_only_n'] + F['w_common'] - len(set(W82))
F['lead_insert'] = cnt_cur(P82, u'the default behavior') - cnt_cur(P6Q, u'the default behavior')
F['repl_bydefault'] = cnt_cur(P6R, u'MUST by default')
F['p82_bydefault'] = cnt_cur(P82, u'by default')
F['comma_82'] = cnt_cur(P82, u'checksum, and should')
F['comma_q69'] = cnt_cur(P6Q, u'checksum, and should')
F['comma_diff'] = F['comma_q69'] - F['comma_82']


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


F['suf_82_q69'] = suffix_words(W82, W6Q)
F['pre_82_q69'] = head_words(W82, W6Q)
F['suf_82_6r'] = suffix_words(W82, W6R)
F['pre_82_6r'] = head_words(W82, W6R)
F['tone_up_repl'] = ub(P6R, u'MUST') + ub(P6R, u'MAY') + ub(P6R, u'SHOULD')
F['tone_lo_repl'] = ub(P6R, u'must') + ub(P6R, u'may') + ub(P6R, u'should')
F['tone_lo_82'] = ub(P82, u'must') + ub(P82, u'should')
F['tone_up_82'] = ub(P82, u'MUST') + ub(P82, u'SHOULD')
F['tone_lo_q69'] = ub(P6Q, u'must') + ub(P6Q, u'should')
F['tone_up_q69'] = ub(P6Q, u'MUST') + ub(P6Q, u'SHOULD')
F['tone_swap'] = F['tone_up_repl'] - F['tone_lo_82']
F['tone_rev_close'] = F['tone_up_82'] + F['tone_lo_repl'] + F['tone_up_q69']
F['verb_updates_6935'] = cnt_cur(FOLD[3], u'This specification updates IPv6')
F['verb_updates_8200'] = cnt_cur(FOLD[2], u'This specification updates IPv6')
VU_CI = [cnt_cur(FO[i], u'this specification updates ipv6') for i in range(NSRC)]
F['verb_updates_ci'] = VU_CI
F['verb_up'] = [F['verb_updates_6935'], F['verb_updates_8200']]
F['verb_track_close'] = sum(abs(VU_CI[i] - (F['verb_updates_6935'] if i == 3 else F['verb_updates_8200'] if i == 2 else 0))
                            for i in range(NSRC))
F['delete_order'] = cnt_cur(FOLD[3], u'fourth bullet should be deleted')
F['delete_order_8200'] = cnt_cur(FOLD[2], u'fourth bullet should be deleted')
F['quote_marker_6935'] = cnt_cur(T[3], u'[RFC2460]')
F['ln_ctrl_1122'] = ln_of(1, u'MUST default to checksumming on')
F['ln_opt_1122'] = ln_of(1, u'the UDP checksum is optional')
F['ln_impl_1122'] = ln_of(1, u'A host MUST implement the facility')
F['ctrl_opt_span'] = F['ln_opt_1122'] - F['ln_ctrl_1122']
F['impl_opt_span'] = F['ln_opt_1122'] - F['ln_impl_1122']
F['opt_vs_must_dir'] = 1 if F['ctrl_opt_span'] > 0 else 0
OPTPREV = []
for i in range(NSRC):
    ws = []
    for m in re.finditer(u'optional', FOLD[i]):
        seg = FOLD[i][max(0, m.start() - 30):m.start()].strip().split()
        ws.append(seg[-1].strip(u'.,;:()').lower() if seg else u'')
    OPTPREV.append(Counter(ws).most_common(3))
F['opt_prev'] = OPTPREV
F['opt_prev_n'] = [len(OPTPREV[i]) for i in range(NSRC)]
F['port_word'] = [cnt_cur(T[i], u'Source Port') for i in range(NSRC)]
F['must_default_str'] = u'MUST default to checksumming on'
F['n_must_impl'] = F['n_z1122_must_impl']
F['cross_needles'] = [k for k in KEYS if sum(1 for i in range(NSRC) if SNF[k][i]) >= 2]
F['ladder_str'] = u'⇎'.join(u'%d' % x for x in F['sn_strict_docs'])
F['fold_only_str'] = u' ⇎ '.join(F['fold_only_keys'])
F['fold_only_n'] = len(F['fold_only_keys'])
F['line_hit_keys'] = [k for k in KEYS if SN[k][OWNER[k]]]
F['dead_needles'] = [k for k in KEYS if not SNF[k][OWNER[k]]]
# --- SCAN2 END ---

# ---------- 三段对照用的逐段插值(段落只有三段, 不走四源轨) ----------
BLKLBL = [u'8200段', u'6935引文', u'6935替代段']


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
    + u' 列: 768 只把零值说成“没算”(' + AN(0, u'transmitter', u'no checksum') + u'), 全篇 '
    + V(u'up_must_all', 0, u'大写MUST·768') + u' 枚大写义务词 ⇎ 1122 要能力 ' + AN(1, u'MUST implement', u'generate and validate')
    + u' 而默认开 ' + AN(1, u'MUST default to checksumming on') + u' ⇎ 8200 把“不是可选”写成默认行为('
    + AN(2, u'default behavior', u'UDP packets are') + u') ⇎ 6935 判那份小写原文该删 '
    + AN(3, u'following text in [RFC2460]', u'fourth bullet') + u' 再换成大写。'
    + u' 版式: 换页符 ' + J(u'ff', u'换页符') + u' 枚 ⇎ 摘壳剥掉 ' + J(u'shell_strip', u'剥壳行')
    + u' 行 ⇎ 整行只有换页符的 ' + J(u'ff_only', u'换页独占行') + u' 行; CR ' + J(u'cr', u'CR')
    + u' 全零, 四份都是 LF 面, BOM ' + J(u'bom', u'BOM') + u' ⇎ 非 ASCII 码位 ' + J(u'nonascii', u'非ASCII')
    + u' —— 字节−码位差 ' + J(u'byte_cp_delta', u'字节码位差') + u' 与每枚非 ASCII 的加字节 '
    + J(u'nonascii_extra', u'加字节') + u' 同为全零, 纯 ASCII 面 ' + V(u'ascii_all', None, u'纯ASCII份数') + u' 份。')

LINES.append(
    u'📐 同一枚补码值在四份里被写成两种进制, 一枚都不手填。1122 面上从 “all 1’s (” 之后正读到十进制 '
    + V(u'num_all1s_dec', None, u'十进制·1122') + AN(1, u"all 1's", u'65535') + u' ⇎ 8200 面上从 “changed to hex ” 之后把十六进制字面折成十 '
    + V(u'num_ffff_8200', None, u'hex折十·8200') + AN(2, u'zero, it must be changed to hex FFFF')
    + u' ⇎ 6935 的替代段同一游标读出 ' + V(u'num_ffff_6935', None, u'hex折十·6935') + AN(3, u'MUST be changed to hex FFFF')
    + u' —— 三枚读数一致的闭合 ' + V(u'base_value_agree', None, u'进制同值闭合') + u'。字面轨另数一遍: “65535” '
    + J(u'num_dec_lit', u'十进制字面') + u' 枚 ⇎ “FFFF” ' + J(u'num_ffff_lit', u'十六进制字面') + u' 枚, 给得出进制的份数 '
    + V(u'num_radix_face_n', None, u'给进制份数') + u' ⇎ 两条游标全落空的份数 ' + V(u'num_cursor_miss', None, u'游标落空份数')
    + u': 768 只写 “all ones” 一个数字都不给 ' + AN(0, u'transmitted', u'all ones')
    + u'——它连“零等于几”都留给读者, 于是“可以不算”在这份里从来不是权利, 只是一种写在线上的值。'
    + u' 位宽同样现读: 768 的校验和字段是 ' + V(u'num_bits_768', None, u'位宽·768') + u' 位 '
    + AN(0, u'Checksum is the', u'16-bit') + u' ⇎ 8200 的伪头地址换成 ' + V(u'num_bits128_8200', None, u'128位·8200')
    + u' 位 ⇎ ' + V(u'num_bits32_8200', None, u'32位·8200') + u' 位 '
    + AN(2, u'addresses from the IP header', u'checksum computation') + u': 两枚比值 '
    + V(u'bits_ratio128', None, u'128倍率') + u' ⇎ ' + V(u'bits_ratio32', None, u'32倍率')
    + u'(整除余零闭合 ' + V(u'bits128_close', None, u'位宽比闭合一') + u' ⇎ ' + V(u'bits32_close', None, u'位宽比闭合二')
    + u'), 相加 ' + V(u'bits_sum_8200', None, u'两位宽之和') + u'。伪头这个词两式并计: 带连字符 ' + J(u'pseudo_hy', u'伪头连字')
    + u' ⇎ 带空格 ' + J(u'pseudo_sp', u'伪头空格') + u' ⇎ 合计 ' + J(u'pseudo', u'伪头合计')
    + u' 枚——768 那份用不带连字符的旧拼法, IPv6 两份用连字式(同一枚算法, 词形也换了代)。')

LINES.append(
    u'🔍 在册 ' + V(u'needle_n', None, u'针总数') + u' 枚答句针走三面阶梯: 原面逐行档各中 ' + J(u'sn_strict_docs', u'逐行档')
    + u' 枚 ⇎ 全篇折平档 ' + J(u'sn_fold_docs', u'折平档') + u' ⇎ 摘壳折平档 ' + J(u'sn_sh_docs', u'摘壳档')
    + u' 枚; 只在折平面存在的 ' + V(u'fold_only_n', None, u'折行独有枚数') + u' 枚: ' + F[u'fold_only_str'] + u'。'
    + u' 最刺眼的是 8200: 它的答句整段被行界劈开, 逐行档 ' + V(u'sn_strict_docs', 2, u'逐行·8200')
    + u' 枚 ⇎ 折平档 ' + V(u'sn_fold_docs', 2, u'折平·8200') + u' 枚 ' + AN(2, u'node must compute a UDP checksum')
    + u'——只按逐行口径搜就会把这份读成“没写这条规则”; 而它面上那半句 not optional 同样只活在折平面(折平 '
    + V(u'not_opt', 2, u'not optional·8200') + u' 枚 ⇎ 逐行 ' + V(u'not_opt_line', 2, u'not optional逐行·8200') + u' 枚)。'
    + u' 阶梯单调账闭合 ' + V(u'ladder_monotone', None, u'阶梯单调') + u', 摘壳档比折平档少 '
    + J(u'sh_minus_fold', u'摘壳减折平') + u' 枚(壳行里没有答句), 折行针按逐行口径必须全零= '
    + V(u'fold_line_zero', None, u'折行逐行零') + u'。判定轨也换过: 正则字面轨 ⇎ 非重叠游标轨逐枚相等(闭合 '
    + V(u're_eq_cur', None, u'两轨相等') + u'), 重叠口径多出的 ' + V(u'overlap_extra', None, u'重叠多余') + u' 枚为零。'
    + u' 跨面同现的针 ' + V(u'cross_needle_n', None, u'跨面针枚数') + u' 枚(句子被复制, 整行没被复制)。')

LINES.append(
    u'🗣 语气大小写是这一条的分水岭, 且三轨互咬。大写轨 MUST ' + J(u'up_must_all', u'大写MUST') + u' ⇎ 裸 MUST '
    + J(u'must_bare', u'裸MUST') + u' ⇎ MUST NOT ' + J(u'must_not', u'MUSTNOT') + u' ⇎ MAY ' + J(u'up_may', u'大写MAY')
    + u' ⇎ SHOULD ' + J(u'up_should', u'大写SHOULD') + u'; 小写轨 must ' + J(u'low_must', u'小写must') + u' ⇎ may '
    + J(u'low_may', u'小写may') + u' ⇎ should ' + J(u'low_should', u'小写should') + u'; 忽略大小写的总轨 must '
    + J(u'ci_must', u'不分大小写must') + u' ⇎ may ' + J(u'ci_may', u'不分大小写may') + u' ⇎ should '
    + J(u'ci_should', u'不分大小写should') + u'; 大写账闭合 ' + J(u'up_ledger', u'大写账') + u' ⇎ 大小写账闭合 '
    + J(u'case_ledger', u'大小写账') + u'; 首字母大写档 must ' + J(u'title_must', u'首字母must') + u' ⇎ may ' + J(u'title_may', u'首字母may') + u'(1122 面上大写 May 是月份不是语气词)' + u'。大写义务词整份为零的是 ' + V(u'up_zero_n', None, u'零大写份数')
    + u' 份: 768(比 1122 早 ' + V(u'year_gaps', 0, u'768到1122年距') + u' 年)与 8200——后者带 STD 头(逐份 '
    + J(u'std_hdr', u'STD头') + u')⇎类别行写 Proposed Standard(逐份 ' + J(u'cat_std', u'类别头')
    + u'), 是标着的现行标准, 全篇大写 ' + V(u'up_must_all', 2, u'大写MUST·8200')
    + u' 枚 ⇎ 小写 ' + V(u'low_must', 2, u'小写must·8200') + u' 枚, 判定 ' + V(u'std_no_upper', None, u'STD零大写判定')
    + u'/' + V(u'low_only_8200', None, u'只小写判定') + u': 那条“IPv6 上 UDP 校验和不是可选”整句就是用 must/should 写的 '
    + AN(2, u'receivers must discard UDP packets containing a') + AN(2, u'zero checksum and should log')
    + u' ⇎ 6935 把同一件事改写成大写 ' + AN(3, u'IPv6 node MUST compute') + u'。'
    + u' 1122 也不是纯命令式: 它的小写 must ' + V(u'low_must', 1, u'小写must·1122') + u' 枚 ⇎ 大写 MUST '
    + V(u'up_must_all', 1, u'大写MUST·1122') + u' 枚, 差 ' + V(u'lo_minus_up', 1, u'小写减大写·1122')
    + u' 枚, 而这一节还自成一段“这件事有争议” ' + AN(1, u'controversial') + u'。')

LINES.append(
    u'🎯 optional 这个词在四份里贴的是四种东西: 全篇 ' + J(u'opt_word', u'optional枚') + u' 枚, 且与 checksum 同行的 '
    + J(u'opt_line_ck', u'optional且ck同行') + u' 枚——768 面上 ' + V(u'opt_line_ck', 0, u'同枚·768')
    + u' 枚: 它唯一的 optional 贴在 Source Port 上 ' + AN(0, u'Source Port', u'optional') + u', 那枚 optional 前面那个词只读到 '
    + u' ⇎ '.join(u'%s:%d' % (w, c) for w, c in F[u'opt_prev'][0]) + u'; “可以不算”从不写成权利, 只写成零值 '
    + AN(0, u'not used', u'zero is inserted') + u'。1122 把这件事拆成三层: 能力上 MUST implement ⇎ 每报文 '
    + AN(1, u'MAY optionally be able to control') + u' ⇎ 默认 ' + AN(1, u'MUST default to checksumming on')
    + u', 而同一节的 IMPLEMENTATION 注里写 the UDP checksum is optional ' + AN(1, u'is optional; the value zero')
    + u'——它离“默认必须开”只差 ' + V(u'ctrl_opt_span', None, u'默认⇎可选行距') + u' 行, 离“能力 MUST”差 '
    + V(u'impl_opt_span', None, u'能力⇎可选行距') + u' 行(先后向判定 ' + V(u'opt_vs_must_dir', None, u' optional在后')
    + u'), 而它在 1122 面上的前词共有 ' + V(u'opt_prev_n', 1, u'前词档数·1122') + u' 档: '
    + u' ⇎ '.join(u'%s:%d' % (w, c) for w, c in F[u'opt_prev'][1]) + u'; 接收侧留给应用 '
    + AN(1, u'without checksums should be discarded') + u'。同一份文书给 UDP 与 TCP 的两说: '
    + AN(1, u'never optional', u'MUST generate') + u'(全库 never optional 逐份 ' + J(u'never_opt', u'never optional')
    + u' 枚, 除 1122 外三份各 0)。'
    + u' 8200 面上 optional ' + V(u'opt_word', 2, u'optional·8200') + u' 枚 ⇎ 6935 ' + V(u'opt_word', 3, u'optional·6935')
    + u' 枚; “not optional” 折平档 ' + J(u'not_opt', u'not optional折平') + u' 枚 ⇎ 逐行档 '
    + J(u'not_opt_line', u'not optional逐行') + u' 枚——IPv6 两份写的是 UDP not optional, 1122 写的是 UDP optional, 768 一个字都不说。')

LINES.append(
    u'📄 同一条 IPv6 规则在 8200 与 6935 里的差别可以逐词算出来: 三段现定界在起 ' + J3(u'blk_lo', u'段起行') + u' ⇎ 止 '
    + J3(u'blk_hi', u'段止行') + u' 行(占 ' + J3(u'blk_rows', u'段行数') + u' 行), 折平后词数 ' + J3(u'blk_words', u'段词数')
    + u' ⇎ 去重共有词 ' + V(u'w_common', None, u'共有词') + u' 枚, 只在 8200 段的 ' + V(u'w82_only_n', None, u'8200独有枚数')
    + u' 枚: ' + u' '.join(F[u'w82_only']) + u' ⇎ 只在 6935 引文里的 ' + V(u'w6q_only_n', None, u'6935引文独有')
    + u' 枚, 词集账闭合 ' + V(u'w_row_close', None, u'词集闭合') + u'。去大小写的共尾 ' + V(u'suf_82_q69', None, u'共尾词数')
    + u' 枚词 ⇎ 共头只到 ' + V(u'pre_82_q69', None, u'共头词数') + u' 枚——引导语被换了: 插入 the default behavior … is that(闭合 '
    + V(u'lead_insert', None, u'引导语插入') + u'), 而 6935 引的那份原文仍是旧的引导语 ' + AN(3, u'UDP checksum is not optional')
    + u'; 8200 与 6935 替代段的共尾 ' + V(u'suf_82_6r', None, u'共尾·8200对替代段') + u' ⇎ 共头 ' + V(u'pre_82_6r', None, u'共头·8200对替代段')
    + u'——尾巴接得上、头接不上, 被改写的是同一句。逗号也分家: ' + V(u'comma_82', None, u'逗号·8200') + u' ⇎ ' + V(u'comma_q69', None, u'逗号·6935引文')
    + u' 枚 “checksum, and should”, 差 ' + V(u'comma_diff', None, u'逗号差') + u'; 8200 面上那句不带逗号 '
    + AN(2, u'zero checksum and should log') + u'。语气换向只朝一个方向: 6935 替代段大写义务 ' + V(u'tone_up_repl', None, u'替代段大写')
    + u' 枚 ⇎ 8200 那段小写 ' + V(u'tone_lo_82', None, u'8200段小写') + u' 枚, 差 ' + V(u'tone_swap', None, u'语气换向差')
    + u'(枚数一枚不动, 只换字面档); 反向读三项 ' + V(u'tone_up_82', None, u'8200段大写') + u' ⇎ '
    + V(u'tone_lo_repl', None, u'替代段小写') + u' ⇎ ' + V(u'tone_up_q69', None, u'引文大写') + u'(那段小写 '
    + V(u'tone_lo_q69', None, u'引文小写') + u' 枚), 之和 ' + V(u'tone_rev_close', None, u'语气反向闭合')
    + u'——读到 0 才是三段各只活一种语气, 换向不是对翻而是整段重写。6935 还在替代段里插 by default ' + V(u'repl_bydefault', None, u'替代段bydefault')
    + u' 枚 ⇎ 8200 面上 ' + V(u'p82_bydefault', None, u'8200bydefault') + u' 枚 ' + AN(3, u'receivers MUST by default')
    + u', 把“必须丢弃”从无条件降成默认条件(出口由 ' + AN(3, u'MAY enable zero-checksum mode') + u' 那枚 MAY 开)。')

LINES.append(
    u'🔧 谁改谁是可以现读的: 8200 的 Obsoletes: 头读到 ' + V(u'obs_n', 2, u'废止枚数·8200') + u' 枚 RFC 号, 6935 的 Updates: 头读到 '
    + V(u'upd_n', 3, u'更新枚数·6935') + u' 枚, 两个动作的对象并集只有 ' + V(u'target_n', None, u'目标号枚数')
    + u' 枚(全库目标号 ' + V(u'target_ids', 0, u'目标号') + u'), 同一对象闭合 ' + V(u'target_agree', None, u'目标一致')
    + u' ⇎ 768、1122 两种头各 ' + V(u'obs_n', 0, u'废止·768') + u'/' + V(u'upd_n', 0, u'更新·768')
    + u' 枚(那份排版面根本没有动作字段) ' + AN(3, u'This specification updates IPv6', u'allow a zero') + u'。'
    + u' 标题页年份逐行尾锚定现读 ' + J(u'years', u'年份') + u'(月 ' + J(u'months', u'月份') + u'), 相邻差 '
    + u' ⇎ '.join(V(u'year_gaps', i, u'年距·' + GAPLBL[i]) for i in range(3))
    + u': 恰有一处倒序 ' + V(u'year_inversions', None, u'年份倒序数') + u', 排序索引(按份序 0⇱768, 1⇱1122, 2⇱8200, 3⇱6935) '
    + u' ⇎ '.join(V(u'year_perm', i, u'年份序索引%d' % i) for i in range(4)) + u', 倒序那一对的年距 '
    + V(u'year_gap_6935_8200', None, u'6935到8200年距')
    + u' ⇎ 倒序判定闭合 ' + V(u'year_perm_close', None, u'年份置换') + u'(读到 0 才是恰有一处倒序)——于是“大写替代段(2013)在前、小写默认行为(2017)在后”'
    + u'这件反直觉的事在四份自己的字节里就读得出, 不必查外部状态页: 语气换代不是按时间单向推进的。'
    + u' 6935 面上 ' + V(u'verb_updates_6935', None, u'updates句·6935') + u' 枚 “This specification updates IPv6” ⇎ 8200 面上 '
    + V(u'verb_updates_8200', None, u'updates句·8200') + u' 枚 ⇎ 不分大小写档 ' + J(u'verb_updates_ci', u'updates句CI')
    + u'(两轨差 ' + V(u'verb_track_close', None, u'updates两轨') + u'), 而“该删”指令只在 6935 出现 ' + V(u'delete_order', None, u'删除指令')
    + u' 次(8200 面上 ' + V(u'delete_order_8200', None, u'删除指令·8200') + u' 次), 引文方括号标记 '
    + V(u'quote_marker_6935', None, u'RFC2460方括号') + u' 枚。')

LINES.append(
    u'📏 答句邻域窗(±' + V(u'win_band', None, u'窗带宽') + u' 行)按小节标题定位: 标题行 ' + J(u'win_sec', u'节行')
    + u' ⇎ 答句行 ' + J(u'win_ans', u'答句行') + u' ⇎ 窗 ' + J(u'win_start', u'窗起') + u' 至 ' + J(u'win_end', u'窗止')
    + u'(行数 ' + J(u'win_rows', u'窗行数') + u'), 四份都命到标题 ' + V(u'win_named', None, u'命名节数')
    + u', 其中带 “Checksum” 字样的标题 ' + V(u'win_share', None, u'标题含校验和') + u' 个。窗内⇎窗外五轨对账: checksum 带内 '
    + J(u'win_ck_in', u'窗内ck') + u' ⇎ 带外 ' + J(u'win_ck_out', u'窗外ck') + u', zero '
    + J(u'win_zero_in', u'窗内zero') + u' ⇎ ' + J(u'win_zero_out', u'窗外zero') + u', optional '
    + J(u'win_opt_in', u'窗内opt') + u' ⇎ ' + J(u'win_opt_out', u'窗外opt') + u', 大写义务词 '
    + J(u'win_up_in', u'窗内大写义务') + u' ⇎ ' + J(u'win_up_out', u'窗外大写义务') + u', 数字符 '
    + J(u'win_dig_in', u'窗内数字') + u' ⇎ ' + J(u'win_dig_out', u'窗外数字') + u'; 五轨合计闭合 '
    + V(u'win_close_sum', None, u'窗账闭合') + u'(逐轨 ' + J(u'win_close_ck', u'ck闭合') + u' ⇎ '
    + J(u'win_close_zero', u'zero闭合') + u' ⇎ ' + J(u'win_close_opt', u'opt闭合') + u' ⇎ '
    + J(u'win_close_up', u'大写义务闭合') + u' ⇎ ' + J(u'win_close_dig', u'数字闭合') + u')。密度对照: 1122 全库 optional '
    + V(u'opt_word', 1, u'optional·1122') + u' 枚里带内只有 ' + V(u'win_opt_in', 1, u'窗内optional·1122')
    + u' 枚, 8200 全库 ' + V(u'opt_word', 2, u'optional·8200') + u' 枚里带内 ' + V(u'win_opt_in', 2, u'窗内optional·8200')
    + u' 枚——1122 的 optional 是散在全文的普通词, 8200 的聚在这条规则周围; 零值词同理 '
    + V(u'win_zero_in', 1, u'窗内zero·1122') + u'/' + V(u'zero_word', 1, u'全篇zero·1122') + u' ⇎ '
    + V(u'win_zero_in', 2, u'窗内zero·8200') + u'/' + V(u'zero_word', 2, u'全篇zero·8200') + u'。')

LINES.append(
    u'🔗 引用写法三式并计(RFC 空格 ⇎ RFC- 短横 ⇎ RFC 连写), 逐份: 2460 ' + J(u'cite_sp_2460', u'空格式2460') + u' ⇎ '
    + J(u'cite_hy_2460', u'短横式2460') + u' ⇎ ' + J(u'cite_tk_2460', u'连写式2460') + u'(合计 '
    + J(u'cite_al_2460', u'2460合计') + u'), 6936 ' + J(u'cite_al_6936', u'6936合计') + u' ⇎ 768 '
    + J(u'cite_al_768', u'768合计') + u' ⇎ 1122 ' + J(u'cite_al_1122', u'1122合计') + u' ⇎ 8200 '
    + J(u'cite_al_8200', u'8200合计') + u' ⇎ 6935 ' + J(u'cite_al_6935', u'6935合计')
    + u'。子串轨三式相加 ⇎ 一条正则族读出的枚数, 逐份差 ' + J(u'cite_forms_close', u'写法族账')
    + u'; 2460 的写法族数 8200 ' + V(u'cite_forms_2460', 2, u'写法族·8200') + u' ⇎ 6935 '
    + V(u'cite_forms_2460', 3, u'写法族·6935') + u' 族, 6935 用连写式 ' + V(u'cite_tk_2460', 3, u'连写2460·6935')
    + u' 枚把被改的那份钉在括号里 ' + AN(3, u'as specified in [RFC2460]') + u'。互引方向: 8200 面上引 6935 '
    + V(u'cite_dir_8200_to_6935', None, u'8200引6935') + u' 枚 ⇎ 6935 面上引 8200 ' + V(u'cite_dir_6935_to_8200', None, u'6935引8200')
    + u' 枚, 单向判定 ' + V(u'cite_dir_unique', None, u'单向闭合判定') + u'(后出的一方才可以引先出的那份)。'
    + u' 768 自指空格式 ' + V(u'cite_sp_768', 0, u'空格768·自指') + u' 枚(署名行 ' + AN(0, u'User Datagram Protocol')
    + u') ⇎ 1122 面上以短横式引它 ' + V(u'cite_hy_768', 1, u'短横768·1122') + u' 枚; 同一份 1122 面上 793 全走短横式 '
    + V(u'cite_hy_793', 1, u'短横793·1122') + u' 枚 ⇎ IPv6 两份面上 793 各 ' + V(u'cite_al_793', 2, u'793合计·8200')
    + u'/' + V(u'cite_al_793', 3, u'793合计·6935') + u' 枚——三代文书的引用体例与话题同时分家。')

LINES.append(
    u'🧮 逐字搬运在这一条里是“句子级”而非“整行级”: 摘壳原面的 ≥40 列长行池 ' + V(u'pool_n', None, u'长行池')
    + u' 条里含字母的只有 ' + V(u'pool_letters', None, u'字母行长行') + u' 条(其余 ' + V(u'pool_border', None, u'边框行长行')
    + u' 条是 ASCII 图与表格边框), 两份同现 ' + V(u'pool_2', None, u'两现长行') + u' ⇎ 三份同现 '
    + V(u'pool_3', None, u'三现长行') + u' ⇎ 四份同现 ' + V(u'pool_4', None, u'四现长行')
    + u' 条, 六对(768·1122 ⇎ 768·8200 ⇎ 768·6935 ⇎ 1122·8200 ⇎ 1122·6935 ⇎ 8200·6935)逐字节同形 '
    + P6(u'pair_byte', u'字节对') + u' ⇎ 只归一同形 ' + P6(u'pair_norm_only', u'仅归一对') + u', 代数闭合 '
    + V(u'pair_close', None, u'配对闭合') + u' ⇎ 容斥闭合 ' + V(u'union_close', None, u'容斥闭合') + u' ⇎ 分档闭合 '
    + V(u'pool_tier_close', None, u'池分档闭合') + u'。两档分家处只有一处: 只在归一后才同形的那一条就是那条 FFFF 句, 两份的差别只在缩进(共 '
    + V(u'apool_maxlen', None, u'锚池最长') + u' 列以内): 写法分家四桶(大小写 ⇎ 短横 ⇎ 空格 ⇎ 多字差) ' + F[u'axis_str']
    + u' ⇎ 非零档 ' + V(u'axis_str_n', None, u'轴档非零数') + u' 个, 轴账闭合 ' + V(u'axis_close', None, u'轴账闭合')
    + u'。锚候选池按标签 ' + J(u'apool_tag_n', u'锚池标签') + u' ⇎ 按份数 ' + J(u'apool_tier', u'锚池分档')
    + u', 两本账闭合 ' + V(u'apool_tag_close', None, u'锚池标签闭合') + u' ⇎ ' + V(u'apool_tier_close', None, u'锚池分档闭合')
    + u'。闭合账总口径: 标量 ' + V(u'scalar_clos_n', None, u'标量恒等式数') + u' ⇎ 清单 '
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
    got = [e for e in ELEMS.get(s, []) if eval(e, {FN: BB70}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, NOEXPR
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv70.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b70flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms70.txt', 'w', encoding='utf-8', newline=NL).write(
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
json.dump(CH, io.open(u'corpus/_b70checks.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

ENTRY = u'corpus/babeltele/B70_udp_checksum_mandatory_four_answers.md'
srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 码位／原行 %d／非空行 %d／最长行 %d 列／答句 %s／页壳换页 %d 枚)' % (
        PATH[i].split('/')[-1], F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        F[u'maxlen'][i],
        [u'零值即“没算”、全篇 %d 枚大写义务词、一种进制都不给' % F[u'up_must_all'][0],
         u'能力 MUST、MAY optionally 而 MUST default 开、下文又写 UDP checksum is optional',
         u'IPv6 默认行为 not optional(全篇 %d 枚大写、小写 must %d 枚)' % (F[u'up_must_all'][2], F[u'low_must'][2]),
         u'引那份小写原文判它该删、换成大写义务词 %d 枚并插 by default' % F[u'tone_up_repl']][i],
        F[u'ff'][i]) for i in range(NSRC))
    + u' (四份 RFC Editor 纯文本面, 全 LF, 全纯 ASCII: BOM 与非 ASCII 码位四份都是 %d 枚; '
      u'同一枚补码值的两种进制(十进制 %d ⇎ hex %d)、位宽 %d⇎%d⇎%d、标题页年份 %s、动作头对象 RFC %s 全部句内或行内游标现读, 一个都不手填。'
      u'抓取时刻、RFC Editor 此刻的现行状态页与勘误页、被引用也被告知该删的 RFC 2460 本身(不在库内)、现网实现实际丢不丢零校验报文, '
      u'都只在本机或站外成立, 不进门槛)\n' % (
        F[u'nonascii'][0], NUM['all1s_dec'], NUM['ffff_8200'],
        NUM['bits_768'], NUM['bits128_8200'], NUM['bits32_8200'],
        u'⇎'.join(str(y) for y in F['years']), u' ⇎ '.join(str(y) for y in F['target_ids'])))
link = (u"；联结不是“同一份数据的两种序列化”, 而是“一条 UDP 报文的校验和到底是不是非算不可、算出零值怎么办”在四份一手文书里的四种答法: "
        u"768 全篇没有一枚 RFC 2119 大写义务词(大写 MUST {up768} ⇎ 小写 must {lo768}), 也不用“可选”表述——optional 一词在它面上只 {opt768} 枚、"
        u"且与 checksum 同行 {optck768} 枚(唯一那枚贴在 Source Port 上), 零值的含义写成“发送端没算”, 算出零就发 all ones 而不给进制"
        u"(十进制游标 {dec768} ⇎ hex 游标 {hex768}); ⇎ 1122 拆成三层: 能力上 MUST implement({impl} 枚) ⇎ 每报文 MAY optionally ⇎"
        u" 默认 MUST default to checksumming on({ctrl} 枚), 而同一节 {span} 行之后写 the UDP checksum is optional({optd} 枚),"
        u" 接收侧留给应用({recv} 枚)并承认 turning off 有争议({controv} 枚), 同段还把 TCP 写成 never optional({never} 枚); ⇎"
        u" 8200 说 IPv6 上“不是可选、且这是默认行为”(引导语插入 the default behavior … is that, 与 6935 引的旧原文共尾 {suf} 枚词逐字同"
        u" ⇎ 共头只 {pre} 枚), 全篇大写义务词 {up82} 枚 ⇎ 小写 must {lo82} 枚(STD 现行标准而判定 {stdno}), 零值改写成 hex FFFF"
        u"(面上 FFFF 字面 {ffff82} 枚); ⇎ 6935 把旧原文整段引出判它该删(该指令 {dele} 次 ⇎ 8200 面 {dele82} 次), 再换成大写义务 {uprepl} 枚"
        u" ⇎ 替代段小写 {lorepl} 枚(反向闭合 {rev}), 插入 by default({bd} 枚 ⇎ 8200 {bd82} 枚), 出口写成 MAY enable zero-checksum mode;"
        u" 动作头一边 Obsoletes: 一边 Updates:, 对象现读同一枚 RFC {tgt}(数量 {obs}⇎{upd}, 并集 {tn} 枚)。"
        u"行级逐字搬运几乎为零: 含字母的 ≥40 列长行池 {pl} 条里两份同现 {p2} 条、四份同现 {p4} 条, 写法分家四桶 {axis};"
        u" 差别全在句子内部——引导语、逗号({cm82}⇎{cm69} 枚)、大小写语气({lo82p} 枚 ⇎ {up69p} 枚)。").format(
    up768=F[u'up_must_all'][0], lo768=F[u'low_must'][0], opt768=F[u'opt_word'][0], optck768=F[u'opt_line_ck'][0],
    dec768=NUM['all1s_faces'][0], hex768=NUM['ffff_faces'][0],
    impl=F[u'n_z1122_must_impl'][1], ctrl=F[u'n_z1122_may_ctrl'][1], span=F['ctrl_opt_span'],
    optd=F[u'n_z1122_udp_optional'][1], recv=F[u'n_z1122_recv_opt'][1], controv=F[u'n_z1122_controversial'][1],
    never=F[u'never_opt'][1], suf=F[u'suf_82_q69'], pre=F[u'pre_82_q69'],
    up82=F[u'up_must_all'][2], lo82=F[u'low_must'][2], stdno=F[u'std_no_upper'], ffff82=F[u'num_ffff_lit'][2],
    dele=F[u'delete_order'], dele82=F[u'delete_order_8200'], uprepl=F[u'tone_up_repl'], lorepl=F[u'tone_lo_repl'],
    rev=F[u'tone_rev_close'], bd=F[u'repl_bydefault'], bd82=F[u'p82_bydefault'],
    tgt=F[u'target_ids'][0], obs=F[u'obs_n'][2], upd=F[u'upd_n'][3], tn=F[u'target_n'],
    pl=F[u'pool_letters'], p2=F[u'pool_2'], p4=F[u'pool_4'], axis=F[u'axis_str'],
    cm82=F[u'comma_82'], cm69=F[u'comma_q69'], lo82p=F[u'tone_lo_82'], up69p=F[u'tone_up_repl'])
title = (u'# B70 一条 UDP 报文的校验和到底是不是非算不可，四份一手文书四种答法：'
         u'零值直说“没算”而全篇无大写义务词 ⇎ 能力 MUST、默认 MUST 开、下文却写 optional ⇎ '
         u'IPv6 用小写 must 把 not optional 写成默认行为 ⇎ 引那份小写原文判它该删、换成大写 MUST 并插入 by default'
         u'（必选与否⇎零值怎么办⇎语气大小写⇎谁改谁 四件事没有一份给全）\n')
tags = (u'tags: 必选⇎零值⇎语气⇎动作 四件事分给四份文书 同一枚补码值两种进制(十进制游标 ⇎ hex 游标, 现读同值闭合)'
        u' 768 两条进制游标都落空(只写 all ones 不给进制) optional 贴 Source Port⇎贴每报文权利⇎贴 IPv6 默认行为'
        u' MUST implement 能力 ⇎ MAY optionally 权利 ⇎ MUST default 默认(1122 一节三件事, 相隔行数现读) '
        u'the UDP checksum is optional ⇎ TCP checksum is never optional(同一份文书分 UDP/TCP 两说)'
        u' 三面阶梯(逐行档中三份 ⇎ 8200 一份不中, not optional 只活在折平面) 正则字面轨 ⇎ 非重叠游标轨 ⇎ 重叠口径三轨对账'
        u' 大写义务词整份为零的两份(1980 那份 ⇎ STD 现行 IPv6 那份) 语气三轨(大写档+小写档=不分大小写档)'
        u' 同一条 IPv6 规则共尾逐字同 ⇎ 共头被改写(the default behavior … is that 插入) 逗号差 “checksum, and should”'
        u' 语气换向双向闭合(8200 段只小写 ⇎ 6935 替代段只大写 ⇎ 6935 引文只小写) by default 插入把无条件降成默认条件'
        u' MAY enable zero-checksum mode 开出口 ⇎ MUST follow [RFC6936] 关出口 Obsoletes: ⇎ Updates: 同一枚对象(现读号集合)'
        u' 标题页年份现读恰有一处倒序(6935 的大写替代段早于 8200 的小写默认行为) 引用三式并计(空格 ⇎ 短横 ⇎ 连写)'
        u' 互引单向(8200 引 6935 ⇎ 6935 面上无 8200) 答句邻域窗五轨(带内+带外=全篇) optional 密度带内⇎带外分档'
        u' (1122 散在全文 ⇎ 8200 聚在规则周围) 行级逐字搬运几近于零(字母长行池 ⇎ 边框行占多数) 写法分家四桶(大小写 ⇎ 短横 ⇎ 空格 ⇎ 多字差)'
        u' 锚候选池标签⇎份数两本账 位宽 %d ⇎ %d ⇎ %d 现读整除 ⇎ 伪头词两式(连字符⇎空格) 闭合账 标量 %d⇎清单 %d 项⇎恒等式 %d 条\n' % (
            NUM['bits_768'], NUM['bits128_8200'], NUM['bits32_8200'],
            F[u'scalar_clos_n'], len([k for k in F if u'close' in k]), F[u'x_ident_n']))
text = (title + srcline + link + tags +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n'
        + u'## ⟪BabelTele⟫\n' + body + u'\n\n'
        + u'## ⛓解读注\n\n（此段由 corpus/_fill70.py 从 corpus/_b70checks.json 与 corpus/_deriv70.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s ｜ 归属错配 %d ⇎ 非原行 %d' % (USED, DIST, TAGN, len(ERR), len(MISSLINE)))
print(u'一源 %d ⇎ 二至三源 %d ⇎ 四源 %d ｜ 针 %d ⇎ 折行独有 %d(%s) ⇎ 阶梯 %s⇎%s⇎%s ⇎ 死针 %s' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], F[u'needle_n'], F[u'fold_only_n'],
    F[u'fold_only_own'], F[u'sn_strict_docs'], F[u'sn_fold_docs'], F[u'sn_sh_docs'], F[u'dead_needles']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ⇎ 恒等式 %d ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), F[u'x_ident_n'], len(F)))
print(u'段落 起 %s 止 %s 行 %s 词 %s 共尾 %d/%d 共头 %d/%d 独有(%d/%d) 逗号 %d⇎%d 语气 %d⇎%d 换向 %d 反向 %d⇎%d⇎%d 引文小写 %d 闭合 %d' % (
    F[u'blk_lo'], F[u'blk_hi'], F[u'blk_rows'], F[u'blk_words'], F[u'suf_82_q69'], F[u'suf_82_6r'],
    F[u'pre_82_q69'], F[u'pre_82_6r'], F[u'w82_only_n'], F[u'w6q_only_n'], F[u'comma_82'], F[u'comma_q69'],
    F[u'tone_up_repl'], F[u'tone_lo_82'], F[u'tone_swap'], F[u'tone_up_82'], F[u'tone_lo_repl'],
    F[u'tone_up_q69'], F[u'tone_lo_q69'], F[u'tone_rev_close']))
print(u'进制 读数 %s ⇎ 字面 dec=%s ffff=%s ⇎ 位宽 %s/%s/%s ⇎ 年 %s ⇎ 动作 obs=%s upd=%s target=%s' % (
    [NUM['all1s_dec'], NUM['ffff_8200'], NUM['ffff_6935']], NUM['dec_lit'], NUM['ffff_lit'],
    NUM['bits_768'], NUM['bits128_8200'], NUM['bits32_8200'], F[u'years'], F[u'obs_n'], F[u'upd_n'], F[u'target_ids']))
print(u'窗 节行 %s 答行 %s 窗 %s..%s 行数 %s ck %s/%s zero %s/%s opt %s/%s up %s/%s 闭合 %s' % (
    F[u'win_sec'], F[u'win_ans'], F[u'win_start'], F[u'win_end'], F[u'win_rows'],
    F[u'win_ck_in'], F[u'win_ck_out'], F[u'win_zero_in'], F[u'win_zero_out'],
    F[u'win_opt_in'], F[u'win_opt_out'], F[u'win_up_in'], F[u'win_up_out'], F[u'win_close_sum']))
print(u'池 n=%d 字母=%d 边框=%d tier=%s 字节对=%s 仅归一=%s 闭合=%d/%d/%d 轴=%s ⇎ 锚池 %s tier=%s' % (
    F[u'pool_n'], F[u'pool_letters'], F[u'pool_border'], F[u'pool_tier'], F[u'pair_byte'],
    F[u'pair_norm_only'], F[u'pair_close'], F[u'union_close'], F[u'pool_tier_close'], F[u'axis_counts'],
    F[u'apool_n'], F[u'apool_tier']))
print(u'引用 2460=%s 三式=%s/%s/%s 账=%s 互引 %d⇎%d 自指=%s ⇎ 1122 的 793=%s ⇎ IPv6 两份 %s' % (
    F[u'cite_al_2460'], F[u'cite_sp_2460'], F[u'cite_hy_2460'], F[u'cite_tk_2460'], F[u'cite_forms_close'],
    F[u'cite_dir_8200_to_6935'], F[u'cite_dir_6935_to_8200'], F[u'cite_self'],
    F[u'cite_al_793'], [F[u'cite_al_793'][2], F[u'cite_al_793'][3]]))
print(u'前词 %s ｜ optional %s 枚 ⇎ 同枚 ck %s ｜ 行距 ctrl=%d impl=%d' % (
    F[u'opt_prev'], F[u'opt_word'], F[u'opt_line_ck'], F[u'ctrl_opt_span'], F[u'impl_opt_span']))
