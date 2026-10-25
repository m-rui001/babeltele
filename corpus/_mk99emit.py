# -*- coding: utf-8 -*-
# B99 发射段(第三遍之后的写稿动作): 编码区每一枚数字都由量测字典 F 现插, 锚只从
# corpus/_atoms99.txt 按 (标签, 子串) 定位取原文; 取不到即失败, 不许自造引文。
REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B99V('%s')" % name if i is None else u"B99V('%s', %d)" % (name, i)
    REG.setdefault(u'%s' % v, expr)
    return v


ATOMS = []
for _ln in io.open(u'corpus/_atoms99.txt', encoding='utf-8'):
    if _ln.strip():
        _tg, _tx = _ln.rstrip(u'\n').split(u'\t', 1)
        ATOMS.append((_tg, _tx))
MISS = []


def AN(tg, sub):
    hit = [x for x in ATOMS if x[0] == tg and sub in x[1]]
    if not hit:
        MISS.append((tg, sub))
        return u'⟨?%s?⟩' % sub
    assert hit[0][0] == tg
    return u'⟨%s⟩' % hit[0][1]


E = []
E.append(u'🧭 一条 TLS 记录到底能装多少明文, 五份一手文书给出五副尺子, 且答句本身长短不一: '
         u'RFC 8446(TLS 1.3)答句 %d 词 %d 字符跨 %d 行 ⟦A⟧%s, 同篇另有两句把上限抬成 +1 octets ⇎ +256 bytes '
         u'⟦A⟧%s 与 ⟦A⟧%s ⇎ RFC 5246(TLS 1.2)答句只 %d 词 %d 字符跨 %d 行 ⟦B⟧%s, 同族另两句一律不带单位词 '
         u'⟦B⟧%s ⟦B⟧%s ⇎ RFC 8449(record_size_limit)答句 %d 词 %d 字符 ⟦C⟧%s, 同页另一句写旧上限 ⟦C⟧%s '
         u'⇎ RFC 6066(max_fragment_length)答句最长 %d 词 %d 字符跨 %d 行, 它不答上限而答档位 ⟦D⟧%s ⇎ '
         u'OpenSSL split_send_fragment.pod %d 词 %d 字符跨 %d 行, 唯一把上限写成十进制而不是幂式的一句 ⟦E⟧%s'
         u'——五份全文里 2^14 式子的枚数 %d⇎%d⇎%d⇎%d⇎%d, 答句里带幂式的枚数 %d⇎%d⇎%d⇎%d⇎%d, 答句里带三位以上十进制的枚数 '
         u'%d⇎%d⇎%d⇎%d⇎%d(只有实现侧那份把 16384 写进答句)。\n'
         % (V('ans_words', 0), V('ans_chars', 0), V('ans_sent_span', 0),
            AN(u'A', u'The length MUST NOT exceed 2^14 bytes'),
            AN(u'A', u'TLSInnerPlaintext MUST NOT exceed'),
            AN(u'A', u'MUST NOT exceed 2^14 + 256'),
            V('ans_words', 1), V('ans_chars', 1), V('ans_sent_span', 1),
            AN(u'B', u'MUST NOT exceed 2^14.'),
            AN(u'B', u'MUST NOT exceed 2^14 + 1024'),
            AN(u'B', u'MUST NOT exceed 2^14 + 2048'),
            V('ans_words', 2), V('ans_chars', 2),
            AN(u'C', u'TLS 1.3 uses a limit of 2^14+1 octets'),
            AN(u'C', u'that limit is 2^14 octets'),
            V('ans_words', 3), V('ans_chars', 3), V('ans_sent_span', 3),
            AN(u'D', u'2^9(1), 2^10(2), 2^11(3), 2^12(4)'),
            V('ans_words', 4), V('ans_chars', 4), V('ans_sent_span', 4),
            AN(u'E', u'SSL3_RT_MAX_PLAIN_LENGTH (16384)'),
            V('pow14_n', 0), V('pow14_n', 1), V('pow14_n', 2), V('pow14_n', 3), V('pow14_n', 4),
            V('ans_pow', 0), V('ans_pow', 1), V('ans_pow', 2), V('ans_pow', 3), V('ans_pow', 4),
            V('ans_dec_tot', 0), V('ans_dec_tot', 1), V('ans_dec_tot', 2), V('ans_dec_tot', 3),
            V('ans_dec_tot', 4)))

E.append(u'🪜 同一副上限在不同读面阶梯上数出来不一样: 逐行档 ⇎ 全篇折平档 ⇎ 摘壳折平档 ⇎ 摘壳+幂式归一档。'
         u'把逐行档拼到折平档, 针多读得 %d⇎%d⇎%d⇎%d⇎%d 枚(硬换行把 ⟦A⟧%s 这类式子的加号推到下一行), '
         u'幂式归一(只改写带空格的加数式)后摘壳面缩短 %d⇎%d⇎%d⇎%d⇎%d 字符, 恰为空格式枚数 '
         u'%d⇎%d⇎%d⇎%d⇎%d 的两倍(每处删掉加号两侧各一枚空格, 账平 %d⇎%d⇎%d⇎%d⇎%d)——所以只有前两份有得缩; '
         u'五份的行宽上限 %d⇎%d⇎%d⇎%d⇎%d 码位, 去重 %d 种(RFC 一律 72, 实现侧放宽到 94); '
         u'壳行取六种形状的并(空行 ⇎ 整行换页符 ⇎ RFC 眉 ⇎ 页脚 ⇎ IETF 行 ⇎ =pod 标记): 逐形相加 %d⇎%d⇎%d⇎%d⇎%d 次 '
         u'⇎ 同中两形的重叠 %d⇎%d⇎%d⇎%d⇎%d ⇎ 得壳行 %d⇎%d⇎%d⇎%d⇎%d ⇎ 正文行 %d⇎%d⇎%d⇎%d⇎%d, '
         u'容斥账 %d⇎%d⇎%d⇎%d⇎%d ⇎ 壳+正对行尺的合账 %d⇎%d⇎%d⇎%d⇎%d; 折平面 %d⇎%d⇎%d⇎%d⇎%d 字符 ⇎ '
         u'壳面 %d⇎%d⇎%d⇎%d⇎%d 字符。四档全读不到的冷针 %d 枚(编号 %s) ⇎ 判词针共 %d 枚 × 五份 = 探针 %d 次。\n'
         % (V('wrap_gain', 0), V('wrap_gain', 1), V('wrap_gain', 2), V('wrap_gain', 3), V('wrap_gain', 4),
            AN(u'A', u'the full encoded TLSInnerPlaintext MUST NOT exceed'),
            V('pow_spread', 0), V('pow_spread', 1), V('pow_spread', 2), V('pow_spread', 3), V('pow_spread', 4),
            V('pow_off_spaced', 0), V('pow_off_spaced', 1), V('pow_off_spaced', 2), V('pow_off_spaced', 3),
            V('pow_off_spaced', 4),
            V('pow_spread_ledger', 0), V('pow_spread_ledger', 1), V('pow_spread_ledger', 2),
            V('pow_spread_ledger', 3), V('pow_spread_ledger', 4),
            V('maxlen', 0), V('maxlen', 1), V('maxlen', 2), V('maxlen', 3), V('maxlen', 4),
            V('maxlen_kinds'),
            V('shape_hits', 0), V('shape_hits', 1), V('shape_hits', 2), V('shape_hits', 3),
            V('shape_hits', 4),
            V('shape_ovl', 0), V('shape_ovl', 1), V('shape_ovl', 2), V('shape_ovl', 3), V('shape_ovl', 4),
            V('shell_lines', 0), V('shell_lines', 1), V('shell_lines', 2), V('shell_lines', 3),
            V('shell_lines', 4),
            V('body_lines', 0), V('body_lines', 1), V('body_lines', 2), V('body_lines', 3), V('body_lines', 4),
            V('shell_ledger', 0), V('shell_ledger', 1), V('shell_ledger', 2), V('shell_ledger', 3),
            V('shell_ledger', 4),
            V('body_shell_ledger', 0), V('body_shell_ledger', 1), V('body_shell_ledger', 2),
            V('body_shell_ledger', 3), V('body_shell_ledger', 4),
            V('face_all', 0), V('face_all', 1), V('face_all', 2), V('face_all', 3), V('face_all', 4),
            V('face_sh', 0), V('face_sh', 1), V('face_sh', 2), V('face_sh', 3), V('face_sh', 4),
            V('cold_n'), u'/'.join([u'%d' % V('cold_needles', k) for k in range(V('cold_n'))]),
            V('needle_n'), V('needle_probes')))

E.append(u'⚖ 单位词就是口径: 同一句 "The length MUST NOT exceed 2^14" 在 8446 带 bytes ⟦A⟧%s, 在 5246 什么都不带 '
         u'⟦B⟧%s; 数字—单位对 %d⇎%d⇎%d⇎%d⇎%d 枚。加数写法两种序列化: 带空格 "2^14 + k" %d⇎%d⇎%d⇎%d⇎%d 枚 ⇎ '
         u'紧写 "2^14+k" %d⇎%d⇎%d⇎%d⇎%d 枚, 5246 一份里两种并存(同一族常量的两种序列化: 结构体定义带空格, '
         u'record_overflow 告警段不带空格 ⟦B⟧%s); 裸幂(不带加数)%d⇎%d⇎%d⇎%d⇎%d 枚。'
         u'8449 把 %d 拆成 %d+%d, 与它自己写的允许膨胀 %d 对账差 %d ⟦C⟧%s; '
         u'三份规范面加数集合起来共 %d 个档: %d⇎%d⇎%d⇎%d; 把每档按两种拼写各算一遍——幂式 2^14+k 得 '
         u'%d⇎%d⇎%d⇎%d⇎%d ⇎ 十进制 16384+k 得 %d⇎%d⇎%d⇎%d⇎%d, 合账 %d 只证明拼写没写歪, 不证明面上有数; '
         u'面上真读到的是: 摘壳折平面上十进制 16384 在 8449 ⇎ 实现侧两份共 %d 枚 ⇎ 幂式 2^14 五份共 '
         u'%d⇎%d⇎%d⇎%d⇎%d 枚。\n'
         % (AN(u'A', u'MUST NOT exceed 2^14 bytes'), AN(u'B', u'MUST NOT exceed 2^14.'),
            V('unit_num_n', 0), V('unit_num_n', 1), V('unit_num_n', 2), V('unit_num_n', 3), V('unit_num_n', 4),
            V('pow_off_spaced', 0), V('pow_off_spaced', 1), V('pow_off_spaced', 2), V('pow_off_spaced', 3),
            V('pow_off_spaced', 4),
            V('pow_off_tight', 0), V('pow_off_tight', 1), V('pow_off_tight', 2), V('pow_off_tight', 3),
            V('pow_off_tight', 4),
            AN(u'B', u'more than 2^14+2048 bytes'),
            V('pow_bare14', 0), V('pow_bare14', 1), V('pow_bare14', 2), V('pow_bare14', 3), V('pow_bare14', 4),
            V('eq_256_split', 2), V('eq_256_split', 0), V('eq_256_split', 1), V('eq_256_split', 3),
            V('eq_256_split', 4),
            AN(u'C', u'the allowance for expansion to 256 octets'),
            V('off14_n'), V('off14_set', 0), V('off14_set', 1), V('off14_set', 2), V('off14_set', 3),
            V('eq_pow_v', 0), V('eq_pow_v', 1), V('eq_pow_v', 2), V('eq_pow_v', 3), V('eq_pow_v', 4),
            V('eq_pow_d', 0), V('eq_pow_d', 1), V('eq_pow_d', 2), V('eq_pow_d', 3), V('eq_pow_d', 4),
            V('eq_pow_ledger'), V('eq_dec14', 0),
            V('pow14_n', 0), V('pow14_n', 1), V('pow14_n', 2), V('pow14_n', 3), V('pow14_n', 4)))

E.append(u'📐 档位题只 RFC 6066 与实现侧答: 6066 的指数 %d⇎%d⇎%d⇎%d 配码位 %d⇎%d⇎%d⇎%d, 指数减码位恒等于 %d '
         u'(四档一把尺)⟦D⟧%s ⇎ 面上写全等号的只有 %d 枚而写裸幂的 %d 枚 ⟦D⟧%s; '
         u'实现侧四档给十进制 %d⇎%d⇎%d⇎%d, 其中 %d 档不写单位 ⇎ 写单位的那档现读 %d 枚, 词面在此 ⟦E⟧%s, '
         u'取值区间下界 %d 上界 %d 差 %d, 管道数上界 %d ⟦E⟧%s, 读缓冲至少 %d(= 上限 + 加密膨胀 %d) '
         u'⟦E⟧%s。6066 的 %d 字节展开式 %d 项相加(%d headers ⇎ %d application ⇎ %d padding ⇎ %d mac), '
         u'超出的膨胀 %d 与实现侧的 %d 差 %d ⟦D⟧%s。规范侧下限 %d ⇎ 8449 建议的最小值 %d, 差 %d ⇎ 商 %d '
         u'⟦C⟧%s。\n'
         % (V('tier_exp_list', 0), V('tier_exp_list', 1), V('tier_exp_list', 2), V('tier_exp_list', 3),
            V('tier_cp_list', 0), V('tier_cp_list', 1), V('tier_cp_list', 2), V('tier_cp_list', 3),
            V('tier_gap'),
            AN(u'D', u'the negotiated length is 2^9=512'),
            V('tier_pow_face', 0), V('tier_pow_face', 1),
            AN(u'D', u'2^9, 2^10, 2^11, and 2^12'),
            V('pod_tier_dec_list', 0), V('pod_tier_dec_list', 1), V('pod_tier_dec_list', 2),
            V('pod_tier_dec_list', 3),
            V('pod_tier_nounit_n'), V('pod_tier_unit_rows'),
            AN(u'E', u'Sets Maximum Fragment Length to 512 bytes'),
            V('eq_pod_range', 0), V('eq_pod_range', 1), V('eq_pod_range', 2), V('eq_pod_range', 3),
            AN(u'E', u'must be in the range 1 - SSL_MAX_PIPELINES'),
            V('read_16704_n'), V('eq_16704'),
            AN(u'E', u'SSL3_RT_MAX_PLAIN_LENGTH + SSL3_RT_MAX_ENCRYPTED_OVERHEAD'),
            V('eq_805'), V('eq_805_parts_n'), V('h805_hdr'), V('h805_app'), V('h805_pad'), V('h805_mac'),
            V('eq_805_over'), V('eq_16704'), V('eq_overhead_cmp', 2),
            AN(u'D', u'larger than 805 bytes MUST discard the message'),
            V('eq_floor', 0), V('eq_floor', 1), V('eq_floor', 2), V('eq_floor', 3),
            AN(u'C', u'a value smaller than 64')))

E.append(u'🧱 行尺本身也要对账: 把换页符当行界的 splitlines 档 %d⇎%d⇎%d⇎%d⇎%d 行 ⇎ split(换行) 档 '
         u'%d⇎%d⇎%d⇎%d⇎%d 行 ⇎ 逐字符数换行 %d⇎%d⇎%d⇎%d⇎%d 行, 前两轨之差 %d⇎%d⇎%d⇎%d⇎%d 恰等于换页符 '
         u'%d⇎%d⇎%d⇎%d⇎%d 枚减去「文件以换行收尾」的那一枚 %d⇎%d⇎%d⇎%d⇎%d(实现侧一份没有换页符, 所以差是负的), '
         u'逐格账平 %d⇎%d⇎%d⇎%d⇎%d。同一份上另有两把壳尺打架: 采集遍的编号档 %d⇎%d⇎%d⇎%d⇎%d 行 ⇎ 本遍形状档 '
         u'%d⇎%d⇎%d⇎%d⇎%d 行, 逐行分歧 %d⇎%d⇎%d⇎%d⇎%d 行。六形各自的枚数: RFC 眉 %d⇎%d⇎%d⇎%d⇎%d 行 ⇎ '
         u'页脚 %d⇎%d⇎%d⇎%d⇎%d 行 ⇎ 整行换页符 %d⇎%d⇎%d⇎%d⇎%d 行 ⇎ 实现侧的 =pod 标记 %d⇎%d⇎%d⇎%d⇎%d 行 ⇎ '
         u'裸页码行 %d⇎%d⇎%d⇎%d⇎%d ⇎ =item 行 %d⇎%d⇎%d⇎%d⇎%d。\n'
         % (V('splitlines', 0), V('splitlines', 1), V('splitlines', 2), V('splitlines', 3), V('splitlines', 4),
            V('splitnl', 0), V('splitnl', 1), V('splitnl', 2), V('splitnl', 3), V('splitnl', 4),
            V('n_lf', 0), V('n_lf', 1), V('n_lf', 2), V('n_lf', 3), V('n_lf', 4),
            V('rows_ledger', 0), V('rows_ledger', 1), V('rows_ledger', 2), V('rows_ledger', 3),
            V('rows_ledger', 4),
            V('ff', 0), V('ff', 1), V('ff', 2), V('ff', 3), V('ff', 4),
            V('trailing_nl', 0), V('trailing_nl', 1), V('trailing_nl', 2), V('trailing_nl', 3),
            V('trailing_nl', 4),
            V('rows_ledger_diff', 0), V('rows_ledger_diff', 1), V('rows_ledger_diff', 2),
            V('rows_ledger_diff', 3), V('rows_ledger_diff', 4),
            V('shell_pick', 0), V('shell_pick', 1), V('shell_pick', 2), V('shell_pick', 3),
            V('shell_pick', 4),
            V('shell_shape', 0), V('shell_shape', 1), V('shell_shape', 2), V('shell_shape', 3),
            V('shell_shape', 4),
            V('shell_pred_diff', 0), V('shell_pred_diff', 1), V('shell_pred_diff', 2),
            V('shell_pred_diff', 3), V('shell_pred_diff', 4),
            V('hdr_rfc', 0), V('hdr_rfc', 1), V('hdr_rfc', 2), V('hdr_rfc', 3), V('hdr_rfc', 4),
            V('foot_page', 0), V('foot_page', 1), V('foot_page', 2), V('foot_page', 3), V('foot_page', 4),
            V('ff_alone', 0), V('ff_alone', 1), V('ff_alone', 2), V('ff_alone', 3), V('ff_alone', 4),
            V('podmark', 0), V('podmark', 1), V('podmark', 2), V('podmark', 3), V('podmark', 4),
            V('pgnum', 0), V('pgnum', 1), V('pgnum', 2), V('pgnum', 3), V('pgnum', 4),
            V('pod_item', 0), V('pod_item', 1), V('pod_item', 2), V('pod_item', 3), V('pod_item', 4)))

E.append(u'🔁 反向对照: 只在一份面上读得到的独占判词针 %d 枚 ⇎ 其中在本家读到的 %d 枚 ⇎ 竟在别家也读到的 %d 枚 '
         u'(探针 %d 次), 换行归一才救回的独占针 %d 枚; 两份以上共享的针 %d 枚, 共享格 %d 格 ⟦A⟧%s 一句在 '
         u'8446⇎5246 两面同现 ⟦B⟧%s。告警名三种写法: 裸写 record_overflow %d⇎%d⇎%d⇎%d⇎%d 枚 ⇎ 带引号 '
         u'%d⇎%d⇎%d⇎%d⇎%d ⟦A⟧%s ⇎ 而 illegal_parameter 告警 %d⇎%d⇎%d⇎%d⇎%d——1.3 把超限与非法参数分两个告警, '
         u'1.2 只提前者。判词五档(折平/逐行/正则轨/游标轨)在同一份上的计数差合计 %d⇎%d⇎%d⇎%d⇎%d, '
         u'小写档 must not/must/should not/should/may 合计 %d⇎%d⇎%d⇎%d⇎%d ⇎ 大写档 must not/must/should not/should/may 合计 '
         u'%d⇎%d⇎%d⇎%d⇎%d ⇎ 逐行档 %d⇎%d⇎%d⇎%d⇎%d, 两把词尺的差即被换行劈开的判词。\n'
         % (V('own_n'), V('own_self'), V('own_others'), V('own_probes'), V('own_powrescued_n'),
            V('shared_n'), V('shared_cells'),
            AN(u'A', u'records carrying data in chunks of 2^14 bytes or less'),
            AN(u'B', u'records carrying data in chunks of 2^14 bytes or less'),
            V('alert_bare', 0), V('alert_bare', 1), V('alert_bare', 2), V('alert_bare', 3), V('alert_bare', 4),
            V('alert_quoted', 0), V('alert_quoted', 1), V('alert_quoted', 2), V('alert_quoted', 3),
            V('alert_quoted', 4),
            AN(u'A', u'record_overflow'),
            V('alert_illegal', 0), V('alert_illegal', 1), V('alert_illegal', 2), V('alert_illegal', 3),
            V('alert_illegal', 4),
            V('ob_ruler_diff', 0), V('ob_ruler_diff', 1), V('ob_ruler_diff', 2), V('ob_ruler_diff', 3),
            V('ob_ruler_diff', 4),
            V('ob_lower_tot', 0), V('ob_lower_tot', 1), V('ob_lower_tot', 2), V('ob_lower_tot', 3),
            V('ob_lower_tot', 4),
            V('ob_fold_tot', 0), V('ob_fold_tot', 1), V('ob_fold_tot', 2), V('ob_fold_tot', 3),
            V('ob_fold_tot', 4),
            V('ob_line_tot', 0), V('ob_line_tot', 1), V('ob_line_tot', 2), V('ob_line_tot', 3),
            V('ob_line_tot', 4)))

E.append(u'🧾 结构面与谱系: 定界进去的节 %d 对(编号×篇名), 节内字符合 %d ⇎ 节内行合 %d ⇎ 节内句合 %d, '
         u'其中含幂式的句 %d 句; 年份取自眉行末格(实现侧无眉行, 退回版权行的起止年) 共 %d 枚 ⇎ 去重 %d 种, '
         u'逐份种数 %d⇎%d⇎%d⇎%d⇎%d: %s ⇎ %s ⇎ %s ⇎ %s ⇎ %s。'
         u'锚定位 %d 处, 其中跨行 %d 处, 最长跨 %d 行; 与采集遍 _pick99 的键对账 %d 项 = 键名配对 %d 条 '
         u'+ 复合对账 %d 项(逐针四档表 ⇎ 三档逐针表 ⇎ 裁后 cut_lf ⇎ 游标 pins), 同 %d ⇎ 异 %d ⇎ '
         u'口径另立 %d 对, 差异键 %s。ℒ 方法 ⇒ 这副上限题的隐性知识分四键: ①答案键 %d⇎%d⇎%d⇎%d⇎%d 是同一 '
         u"2^14 的五种序列化(幂式 ⇎ 幂式+1 ⇎ 幂式+加数 ⇎ 十进制 ⇎ 只写档位不写上限); "
         u'②尺键 加数尺 %d 个档 ⇎ 膨胀尺拆成 %d+%d ⇎ 档位尺指数减码位恒 %d, 三尺互不换算; '
         u'③档键 同一句在逐行/折平/摘壳/摘壳+归一四档上的可读性各不同(冷针 %d 枚 ⇎ 折平涨 %d 枚); '
         u'④层键 数值落在规范面(告警段 ⇎ 结构体定义 ⇎ NOTE)还是实现面(默认值 ⇎ 取值区间 ⇎ 读缓冲), '
         u'每键都是可机检的 count, 零项照占键位。\n'
         % (V('sec_n'), V('sec_cp_tot'), V('sec_rows_tot'), V('sents_tot'), V('sents_pow_tot'),
            V('year_tot'), V('year_n'),
            V('hdr_year_set', 0), V('hdr_year_set', 1), V('hdr_year_set', 2), V('hdr_year_set', 3),
            V('hdr_year_set', 4),
            u' '.join([u'%d' % V('year_list', k) for k in range(len(F['year_list']))
                       if F['year_src'][k] == 0]),
            u' '.join([u'%d' % V('year_list', k) for k in range(len(F['year_list']))
                       if F['year_src'][k] == 1]),
            u' '.join([u'%d' % V('year_list', k) for k in range(len(F['year_list']))
                       if F['year_src'][k] == 2]),
            u' '.join([u'%d' % V('year_list', k) for k in range(len(F['year_list']))
                       if F['year_src'][k] == 3]),
            u' '.join([u'%d' % V('year_list', k) for k in range(len(F['year_list']))
                       if F['year_src'][k] == 4]),
            V('pin_n'), V('pin_cross'), V('pin_max_span'),
            V('pick_pairs_sum'), V('pick_pairs_n'), V('pick_comp_n'),
            V('pick_agree'), V('pick_diff'), V('pick_excl_n'),
            json.dumps(F['pick_diffk'], ensure_ascii=False),
            V('ans_words', 0), V('ans_words', 1), V('ans_words', 2), V('ans_words', 3), V('ans_words', 4),
            V('off14_n'), V('eq_256_split', 0), V('eq_256_split', 1), V('tier_gap'),
            V('cold_n'), V('wrap_tot')))

enc = u''.join(E)
assert not MISS, u'锚词汇表里没有这些针: %s' % MISS[:6]
n_tags = len(re.findall(u'⟦([A-E])⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'编码区标签 %d ≠ 编码区锚 %d' % (n_tags, n_atoms)
assert u'V(' not in enc, u'编码区里出现字面 V( —— 插值没跑'
SRALL = u'!'.join(T)
missing = []
for mm in re.finditer(u'\\d[\\d.]*', enc):
    tk = mm.group(0).rstrip(u'.')
    if tk in REG or tk in SRALL:
        continue
    missing.append(tk)
assert not missing, u'无着落 token: %s' % sorted(set(missing))[:12]

atoms_by_tag = {}
for _tg, _tx in ATOMS:
    atoms_by_tag.setdefault(_tg, []).append(_tx)
orig_lines = []
for i, tg in enumerate([u'A', u'B', u'C', u'D', u'E']):
    orig_lines.append(u'### ⟦%s⟧ ⟸ %s' % (tg, PATH[i]))
    orig_lines.append(u'')
    for a in atoms_by_tag.get(tg, []):
        orig_lines.append(a)
        orig_lines.append(u'')
orig = u'\n'.join(orig_lines).rstrip()

title = (u'# B99 一条 TLS 记录最多装多少明文: 8446⇎5246⇎8449⇎6066⇎OpenSSL 五份一手文书各答一遍 '
         u'2^14⇎2^14(+1/+256/+1024/+2048)⇎档位四制⇎16384 十进制, 单位词与换行决定哪一档读得到\n')
srcline = (u'src: %s(%d B 折平 %d 字符) ⇎ %s(%d B) ⇎ %s(%d B) ⇎ %s(%d B) ⇎ %s(%d B) '
           u'(五份均为 TLS/实现侧一手文本: RFC 8446 TLS 1.3 ⇎ RFC 5246 TLS 1.2 ⇎ RFC 8449 record_size_limit ⇎ '
           u'RFC 6066 max_fragment_length ⇎ OpenSSL split_send_fragment.pod; 数字一律从面内现读, 一个都不手填; '
           u'"记录能装多大"在 1.2→1.3 之间换了口径(明文上限不动 ⇎ 内层加 1 ⇎ 密文膨胀从 1024/2048 改算成 256), '
           u'与 B57 的签名算法裁决不成同题对照; 上游改版后的现值只在本机或站外成立, 不进门槛)\n'
           % (PATH[0], V('bytes', 0), V('face_all', 0), PATH[1], V('bytes', 1), PATH[2], V('bytes', 2),
              PATH[3], V('bytes', 3), PATH[4], V('bytes', 4)))
tagsline = (u'tags: 答案键(2^14 的五种序列化) 尺键(加数尺⇎膨胀尺⇎档位尺) 档键(四档读面阶梯+行尺三轨) '
            u'单位键(bytes/octets/裸数/带码位) 层键(规范面⇎实现面) 反向对照键(独占⇎共享) '
            u'锚归属由正文现推 闭合账 标量档 清单档\n')
md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')
out = u'corpus/babeltele/B99_tls_record_max_plaintext.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open(u'corpus/_b99contract.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(u'B99 建条目: %s' % out)
print(u'编码区 %d 字符, 锚 %d 枚(标签 %d 枚), 扁平契约 %d 枚键 ⇎ 五源字节 %d'
      % (len(enc.replace(u'\n', u'')), n_atoms, n_tags, len(REG), sum(F['bytes'])))
