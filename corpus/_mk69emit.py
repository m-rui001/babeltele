# -*- coding: utf-8 -*-
"""建条目第二遍(B69)的后半: 由 _mkB69.py 在顶层 exec 进来, 与前半共享同一批现读量。
本半只做三件事: 把针表并入扁平键(好让门槛侧只认一个字典)、排编码区正文、发 DERIV/checks/atoms/条目文件。
正文里每一枚三位以上的数都由 V()/J() 注册过算式, 没有一枚手打。"""

# --- SCAN2 BEGIN --- (并键段: 同一段也机械切进 audit.py::_b69_scan)
# ---------- 并键: 针命中 ⇎ 游标读数进 F ----------
for k, v in SN.items():
    F[u'n_' + k] = v
for k, v in NUM.items():
    F[u'num_' + k] = v
F[u'maxlen'] = [max(len(x) for x in L[i]) for i in range(NSRC)]
CYCLE = []
for t in T:
    m = re.search(u'(\\d+(?:\\.\\d+)?)\\s+hours', t)
    CYCLE.append(float(m.group(1)) if m else None)
F[u'cycle_h'] = CYCLE
F[u'cycle_docs'] = len([x for x in CYCLE if x])
F[u'win_title'] = [w[u'head'] for w in WIN]
F[u'win_level'] = [len(re.findall(u'[.]', w[u'head'].split(None, 1)[0])) for w in WIN]
F[u'quiet_time_word'] = [cnt_cur(t, u'quiet time') for t in T]
F[u'tw_plain'] = [cnt_cur(t, u'TIME WAIT') for t in T]
F[u'time_wait_domin'] = [F[u'tw'][i] - F[u'twospace'][i] for i in range(NSRC)]
F[u'msl_undefined_c'] = 1 if (F[u'msl_taken'][2] == 0 and F[u'c2m'][2] == 0) else 0
F[u'axis_str'] = u'⇎'.join(u'%s%d' % (a, F[u'axis_counts'][a]) for a in (u'case', u'hyph', u'space', u'multi'))
F[u'axis_str_n'] = len([a for a in (u'case', u'hyph', u'space', u'multi') if F[u'axis_counts'][a]])
F[u'sh_lost_n'] = len(F[u'sh_lost_keys'])
F[u'fold_only_n'] = len(F[u'fold_only_keys'])
F[u'rfc_ref_6528'] = [cnt_cur(t, u'6528') for t in T]
F[u'rfc_ref_1122'] = [cnt_cur(t, u'1122') for t in T]
F[u'rfc_ref_9293'] = [cnt_cur(t, u'9293') for t in T]
F[u'msl_minute_word'] = [cnt_cur(t, u'minute') for t in T]

F[u's3_raw'] = [[l for l in L[i] if pnorm(l) == F[u's3_examples'][0]] for i in range(NSRC)]
F[u's3_raw_first'] = F[u's3_raw'][0][0]
F[u's3_docs'] = len([1 for i in range(NSRC) if F[u's3_raw'][i]])
F[u's3_norm_close'] = len(pnorm(F[u's3_raw_first'])) - len(F[u's3_examples'][0])

# --- SCAN2 END ---
IDX = dict((t, n) for n, t in enumerate(LBL))
TAGS = LBL
FAN = FO
ATOMFAIL = []


def AN(i, *nd):
    for l in L[i]:
        if all(x in l for x in nd):
            return u'⟦%s⟧⟨%s⟩' % (LBL[i], l)
    ATOMFAIL.append((LBL[i], nd))
    raise AssertionError(u'锚导出失败 %s %s' % (LBL[i], nd))


LINES = []
LINES.append(
    u'🧭 四源字节 ' + J(u'bytes', u'字节') + u' ⇎ 面内码位 ' + J(u'chars', u'码位') + u' ⇎ 原文件行 '
    + J(u'lines', u'行数') + u' ⇎ 非空行 ' + J(u'nonblank', u'非空行') + u' ⇎ 最长行 ' + J(u'maxlen', u'最长行')
    + u' 列: 793 把 MSL 定成 ' + V(u'num_minutes_a', None, u'MSL分钟·793') + u' 分钟还明文许可违背 quiet time ⇎ '
    + u'1122 定死 MUST linger 两枚 MSL 却自带出口 ⇎ 6528 不等时间、改从“最后见到报文”那刻起算 ⇎ '
    + u'9293 逐字收下 793 那句、把主语换成 endpoint 并把前三份一起 Obsoletes。'
    + u' 版式换代一枚: 换页符 ' + J(u'ff', u'换页符') + u' 枚 ⇎ 整行只有换页符的 ' + J(u'ff_only', u'换页独占行')
    + u' 行——前三份按页断开(页眉页脚行留在正文流里), 9293 的换页符是 ' + V(u'ff', 3, u'换页符·9293')
    + u' 枚的新排版面, 所以本条的摘壳档对它无物可剥。'
    + u' 编码层只有一份不干净: BOM ' + J(u'bom', u'BOM') + u' ⇎ 非 ASCII 码位 ' + J(u'nonascii', u'非ASCII')
    + u' ⇎ 每枚非 ASCII 带来的加字节 ' + J(u'nonascii_extra', u'加字节') + u' ⇎ 字节−码位差 '
    + J(u'byte_cp_delta', u'字节码位差') + u'; CR ' + J(u'cr', u'CR') + u' 全零, 四份都是 LF 面。'
    + u' 词轨先分家: MSL ' + J(u'msl', u'MSL枚') + u' ⇎ TIME-WAIT 连字式 ' + J(u'tw', u'TW枚') + u' ⇎ “TIME-WAIT state” 整语 '
    + J(u'twospace', u'TWstate') + u' ⇎ quiet 词干 ' + J(u'quiet', u'quiet') + u' ⇎ “quiet time” 整语 '
    + J(u'quiet_time_word', u'quiettime') + u' ⇎ linger ' + J(u'linger', u'linger') + u': 6528 把 MSL 压到 '
    + V(u'msl', 2, u'MSL·6528') + u' 枚而 TIME-WAIT 还有 ' + V(u'tw', 2, u'TW·6528')
    + u' 枚——它谈状态与起算点, 不再复述时长。')

LINES.append(
    u'📐 时长数全部句内游标现读, 一枚都不手填。793 的 “MSL is taken to be ” 之后读出 ' + V(u'num_minutes_a', None, u'正读分钟·793')
    + u' 分钟 ' + AN(0, LITK[u'a_msl2']) + u' ⇎ 9293 的同一枚游标在同一句之后读出 ' + V(u'num_minutes_d', None, u'正读分钟·9293')
    + u' 分钟 ' + AN(3, LITK[u'd_msl2']) + u'——两份读数对账闭合 ' + V(u'minutes_agree', None, u'分钟数对账')
    + u'; 793 的术语表另有 ' + AN(0, LITK[u'a_arb2']) + u', “Arbitrarily defined to be ” 之后读出 '
    + V(u'num_minutes_arb', None, u'术语表分钟') + u' 分钟, 与正文那句一致(闭合 ' + V(u'arb_eq_spec', None, u'术语表=正文')
    + u')。状态图里那枚超时器 ' + AN(0, LITK[u'a_fig']) + u' 的 “Timeout=” 之后读出 ' + V(u'num_twoms_a', None, u'图内Timeout')
    + u'(闭合 ' + V(u'twoms_is_2', None, u'图式=2') + u'), 同一枚式样在 9293 的图里再现 ' + V(u'n_a_fig', 3, u'图式·9293')
    + u' 次。绕回周期由逆向游标自 “approximately every ” 之后取到带小数的全数 ' + V(u'cycle_h', 0, u'绕回小时·793')
    + u' ' + AN(0, LITK[u'a_isn455']) + u', 793 用它反推“只要 MSL 短过绕回周期就安全” ' + AN(0, LITK[u'a_lt455'])
    + u' ⇎ 9293 把同一句重写一遍 ' + V(u'cycle_h', 3, u'绕回小时·9293') + u'(同现份数 ' + V(u'cycle_docs', None, u'绕回周期份数')
    + u')。时钟步长: 793 的 “incremented roughly every ” 之后读出 ' + V(u'num_usec_a', None, u'微秒·793')
    + u' ⇎ 9293 的 “once every roughly ” 之后读出 ' + V(u'num_usec_d', None, u'微秒·9293') + u'(闭合 '
    + V(u'usec_agree', None, u'时钟步长对账') + u')。谁没给分钟数: “taken to be” 那条定 MSL 的句式在 '
    + J(u'msl_taken', u'taken-to-be句') + u' 份面上出现 ⇎ “2 minutes” 字样 ' + J(u'c2m', u'2minutes') + u' 处 ⇎ '
    + u'分钟数缺席份数 ' + J(u'nul_faces', u'分钟数缺席') + u'——6528 全篇不写 MSL 等于几分钟(它把时长推给 “last seen” '
    + V(u'f2star', 2, u'2*MSL·6528') + u' 枚式) ' + AN(2, LITK[u'c_lastseen']) + u' ⇎ 1122 面上有 '
    + V(u'c2m', 1, u'2minutes·1122') + u' 处 “2 minutes”, 但那枚数不在 MSL 定义句里(6528 无分钟定义句的闭合 '
    + V(u'msl_undefined_c', None, u'6528无分钟定义') + u')。时长字面账: 逐份“数字+单位”命中 ' + J(u'dur_hit_total', u'时长命中')
    + u' 处 ⇎ 不同取值 ' + J(u'dur_distinct', u'时长取值') + u' 枚。')

LINES.append(
    u'⚖ 头条不是“哪个数更大”, 而是“要不要等、等多久、从哪一刻起算、能不能跳过”: '
    + u'793 先定数再自毁 ' + AN(0, LITK[u'a_violate']) + u'——它明文允许实现者违背自己刚立的 quiet time 限制, '
    + u'并把 MSL 说成任意取的 ' + V(u'num_minutes_a', None, u'MSL分钟·793b') + u' 分钟, 同段还留一句“可由经验改动” '
    + AN(0, LITK[u'a_eng']) + u'(整句要折平才读得到, 见 ⚙ 行) ⇎ 1122 换成命令式并把出口写进同一句 '
    + AN(1, LITK[u'b_linger']) + u' ⇎ ' + AN(1, LITK[u'b_mayaccept']) + u', 两个条件分别在 ' + AN(1, LITK[u'b_cond1'])
    + u' ⇎ ' + AN(1, LITK[u'b_cond2']) + u' 两行里(重开连接时另发初始号 ⇎ 若那枚 SYN 出自对方已关的死连接就退回 TIME-WAIT), '
    + u'它还嫌端口占用太久而允许缩短 ' + AN(1, LITK[u'b_shorten']) + u' ⇎ 6528 干脆取消“等”: 窗口锚在上一段报文最后被见到的时刻 '
    + AN(2, LITK[u'c_lastseen']) + u', 判据 ' + AN(2, LITK[u'c_star']) + u', 并显式挂回旧文的概念与附录 '
    + AN(2, LITK[u'c_twref']) + u'; 它同时换了序列号生成法(慢时钟加伪随机) ' + AN(2, LITK[u'c_quiettwo'])
    + u' ⇎ 9293 同时收下两家: 逐字保留 793 那句 ' + V(u'num_minutes_d', None, u'MSL分钟·9293b') + u' 分钟(两份该句逐字同形, '
    + u'闭合 ' + V(u'msl2_same_bytes', None, u'2分钟句同形') + u'), 又收下 1122 的 linger 与两条件 '
    + AN(3, LITK[u'd_linger']) + u' ⇎ ' + AN(3, LITK[u'b_cond1']) + u'(该条件句在 9293 面上再现 ' + V(u'n_b_cond1', 3, u'条件句·9293')
    + u' 次); 但 793 那句 “the TCP must keep quiet for a maximum segment lifetime” 在 9293 面上按原句读不到(改写判定 '
    + V(u'quiet_rewritten', None, u'quiet句改写') + u'), 主语换成端点 ' + AN(3, LITK[u'd_endpoint'])
    + u'。四份对同一件事给的是四种句式: 许可句 ⇎ 命令句带出口 ⇎ 判据式 ⇎ 命令句+废止声明。')

LINES.append(
    u'🔁 谁抄谁可以逐字量出来: 归一长行的两两交集 ' + J(u'pair_share', u'归一同行') + u' ⇎ 逐字节同形 '
    + J(u'pair_byte', u'逐字节同行') + u' ⇎ 仅归一同形 ' + J(u'pair_norm_only', u'仅归一') + u'(配对闭合 '
    + V(u'pair_close', None, u'配对代数闭合') + u' ⇎ 非零对 ' + V(u'pair_nonzero', None, u'非零对') + u'): '
    + u'最大一对是 793⇎9293 的 ' + V(u'pair_ad_byte', None, u'AD逐字节') + u' 行(归一 ' + V(u'pair_ad_share', None, u'AD归一')
    + u' ⇎ 仅归一 ' + V(u'pair_ad_norm_only', None, u'AD仅归一') + u' ⇎ 只此两份 '
    + V(u'pair_ad_excl', None, u'AD只此两份') + u' ⇎ 还压在第三份 ' + V(u'pair_ad_in3', None, u'AD三份同压')
    + u' ⇎ 拆账闭合 ' + V(u'pair_ad_split', None, u'AD拆账闭合') + u' ⇎ 与配对档闭合 '
    + V(u'pair_ad_pair_close', None, u'AD配对档闭合') + u' ⇎ 闭合 ' + V(u'pair_ad_close', None, u'AD配对闭合')
    + u'), 第二对是 6528⇎9293 的逐字节 ' + V(u'pair_byte', 5, u'CD逐字节') + u' 行(归一 ' + V(u'pair_share', 5, u'CD归一')
    + u' ⇎ 仅归一 ' + V(u'pair_norm_only', 5, u'CD仅归一') + u'); 1122⇎9293 归一 ' + V(u'pair_share', 4, u'BD归一')
    + u' 行却逐字节 ' + V(u'pair_byte', 4, u'BD逐字节') + u' 行'
    + u'——9293 近乎逐字收下 6528 的算法句, 对 1122 只搬走内容、把句子重写。跨两份逐字共现的在册针: ' + u' ⇎ '.join(F[u'shared_verbatim'])
    + u'(旧面在册 ' + V(u'msl2_two_docs', 0, u'MSL句·793') + u' 枚 ⇎ 9293 面上 '
    + V(u'msl2_two_docs', 1, u'MSL句·9293') + u' 枚), 其中定 MSL 那句 ⇎ Timeout=2MSL 图式 ⇎ 1122 的两条件句全部同时活在旧面与 9293 面上。'
    + u' 名分账: Obsoletes 头 ' + J(u'obsoletes', u'Obsoletes头') + u' ⇎ Updates 头 ' + J(u'updates', u'Updates头')
    + u' ⇎ STD 头 ' + J(u'std', u'STD头') + u' ⇎ ISSN 头 ' + J(u'issn', u'ISSN头') + u' ⇎ Standards Track '
    + J(u'cat_std', u'标准类') + u': 9293 ' + AN(3, LITK[u'd_obsoletes']) + u' 一次点名 ' + V(u'obsoletes', 3, u'点名·9293')
    + u' 枚 RFC(含 6528 与 6093)——它把“要不要等”的三份答案全部废止, 却又逐字收下第一份那句 '
    + V(u'num_minutes_d', None, u'MSL分钟·9293c') + u' 分钟。引用写法必须三式并计: “RFC-793” 短横式 '
    + J(u'r793d', u'短横引793') + u' ⇎ “RFC 793” 空格式 ' + J(u'r793s', u'空格引793') + u' ⇎ “RFC-1122” '
    + J(u'r1122d', u'短横引1122') + u' ⇎ “RFC 1122” ' + J(u'r1122s', u'空格引1122') + u'——只认空格式就会把“1122 引 793”读成 '
    + V(u'r793d', 1, u'短横引793·1122') + u' 次为零; 只认短横式则 9293 引 793 的 ' + V(u'r793s', 3, u'空格引793·9293')
    + u' 次全读漏。6528 那份被引 ' + V(u'rfc_ref_6528', 3, u'6528被引') + u' 次只出现在 9293 的废止清单里(旧两份零枚: 闭合另见 ⛓)。')

LINES.append(
    u'🧪 答句邻域带(以答句行为心、两侧各取 ' + V(u'win_band', None, u'带宽') + u' 行; 带内首行 '
    + J(u'win_start', u'带起') + u' ⇎ 末行 ' + J(u'win_end', u'带止') + u' ⇎ 答句行 ' + J(u'win_center', u'答句行')
    + u' ⇎ 带长 ' + J(u'win_chars', u'带长字符') + u' ⇎ 带内行 ' + J(u'win_rows', u'带行数') + u'): '
    + u'四份的答句各自所属的编号节(向上找最近一枚不含目录引导点的标题) '
    + u' ⇎ '.join(V(u'win_title', i, u'节名·' + LBL[i]) for i in range(NSRC)) + u', '
    + u'四份里定位到编号节的 ' + V(u'win_named', None, u'定位到节') + u' 份 ⇎ 与状态图/连接状态同名的 '
    + V(u'win_share', None, u'节名含CONNECTION') + u' 份。带内外分账: MSL 带内 ' + J(u'win_msl_in', u'MSL带内')
    + u' ⇎ 带外 ' + J(u'win_msl_out', u'MSL带外') + u'(逐份闭合 ' + J(u'win_close_msl', u'MSL带闭合')
    + u') ⇎ TIME-WAIT 带内 ' + J(u'win_tw_in', u'TW带内') + u' ⇎ 带外 ' + J(u'win_tw_out', u'TW带外') + u'(闭合 '
    + J(u'win_close_tw', u'TW带闭合') + u') ⇎ 数字符带内 ' + J(u'win_dig_in', u'数字带内') + u' ⇎ 带外 '
    + J(u'win_dig_out', u'数字带外') + u'(闭合 ' + J(u'win_close_dig', u'数字带闭合') + u', 三轨合计 '
    + V(u'win_close_sum', None, u'带账三轨合计') + u')。带口径下的密度对照: 6528 的答句行在第 '
    + V(u'win_center', 2, u'答句行·6528') + u' 行、带内 MSL ' + V(u'win_msl_in', 2, u'MSL带内·6528')
    + u' 枚 ⇎ 793 的答句行在第 ' + V(u'win_center', 0, u'答句行·793') + u' 行、带内 MSL '
    + V(u'win_msl_in', 0, u'MSL带内·793') + u' 枚 ⇎ 9293 同一句却落在第 ' + V(u'win_center', 3, u'答句行·9293')
    + u' 行——四份都把答案埋在正文中段, 带外余量 ' + V(u'win_msl_out', 3, u'MSL带外·9293')
    + u' 枚 MSL 说明 9293 通篇仍在别处反复引用这个时长。')

LINES.append(
    u'⚙ 三面阶梯在本条只走到两阶, 而这两阶必需: 在册 ' + V(u'needle_n', None, u'在册针') + u' 枚答句针按原面(逐行)读到 '
    + J(u'sn_strict_docs', u'原面') + u' 枚 ⇎ 全篇折平读到 ' + J(u'sn_fold_docs', u'折平') + u' ⇎ 摘壳折平读到 '
    + J(u'sn_sh_docs', u'摘壳') + u'(只增不减 ' + V(u'ladder_monotone', None, u'阶梯不倒挂') + u', 摘壳−折平 '
    + J(u'sh_minus_fold', u'摘壳减折平') + u' ⇎ 被壳挡住的针 ' + V(u'sh_lost_n', None, u'被壳挡住')
    + u' 枚): 9293 零换页符, 剥壳对它是空操作, 所以本条第三档没有新增句。真正的通道是折行: '
    + V(u'fold_only_n', None, u'折行独有针') + u' 枚针只在折平面存在 ' + AN(0, LITK[u'a_eng']) + u' ⇎ '
    + AN(1, LITK[u'b_linger']) + u' ⇎ ' + AN(3, LITK[u'd_endpoint']) + u'——它们所属的整句(“is an engineering choice, and may be changed if experience indicates it is desirable to do so.” ⇎ '
    + u'“it MUST linger in TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime). However, it MAY accept a new SYN” ⇎ '
    + u'“the TCP endpoint must keep quiet for an MSL before assigning any sequence numbers upon starting up or recovering from a situation where memory of sequence numbers in use was lost.”)'
    + u' 全被行界劈开, 逐行口径一律零命中(闭合 ' + V(u'fold_line_zero', None, u'折行针逐行零命中') + u'), 按份新增 '
    + J(u'fold_only_own', u'折行独有') + u' 枚(清单 ' + u' ⇎ '.join(F[u'fold_only_keys']) + u')。'
    + u'最锋利的一处: 1122 把“MUST 等两枚 MSL”与“MAY 立刻接受新 SYN”写进同一句而中间隔着行界——只按行搜 “MUST linger” 就读不到它自带的出口; '
    + u'793 的“这是工程选择”被劈在 “is an engineering choice, and” 与后半句之间, 而那半句正是它允许违背 quiet time 的免责根据。')

LINES.append(
    u'📏 义务语气换代是第二根轴: 大写 MUST 全形 ' + J(u'up_must_all', u'MUST全形') + u' ⇎ 裸 MUST(不含 MUST NOT) '
    + J(u'must_bare', u'裸MUST') + u' ⇎ MUST NOT ' + J(u'must_not', u'MUSTNOT') + u' ⇎ SHOULD '
    + J(u'up_should', u'SHOULD') + u' ⇎ MAY ' + J(u'up_may', u'MAY') + u'(逐份账闭合 ' + J(u'up_ledger', u'义务词账')
    + u'): 793 面上大写义务词 ' + V(u'up_must_all', 0, u'MUST·793') + u' 枚——整篇用小写 must/should 与 “may violate” 这类许可句, '
    + u'那套大写词表比它晚十年; 1122 ⇎ 9293 把命令式抬到 ' + V(u'up_must_all', 1, u'MUST·1122') + u' ⇎ '
    + V(u'up_must_all', 3, u'MUST·9293') + u' 枚, 而 6528 只有 ' + V(u'up_must_all', 2, u'MUST·6528')
    + u' 枚——它是实验性提案而不是要求。同一条 linger 规则的语气换代可读: 793 用许可(“may violate”) ⇎ 1122 用 MUST linger + MAY accept ⇎ '
    + u'9293 用同一枚 MUST 但把 quiet 的义务主体改成 endpoint。词面密度: “TIME-WAIT state” 整语 ' + J(u'twospace', u'TWstate')
    + u' ⇎ 连字式减整语余量 ' + J(u'time_wait_domin', u'TW余量') + u' ⇎ 无连字符写法 ' + J(u'tw_plain', u'TIMEWAIT无横线')
    + u' ⇎ keep-alive ' + J(u'ka', u'keep-alive') + u' ⇎ Timestamp ' + J(u'timestamp', u'Timestamp') + u' ⇎ ISS '
    + J(u'iss', u'ISS') + u' ⇎ ISN ' + J(u'isn', u'ISN') + u' ⇎ “32 bit/32-bit” ' + J(u'isn_bits', u'32位') + u' ⇎ reboot '
    + J(u'reboot', u'reboot') + u': 6528 一份里 ISN 字样 ' + V(u'isn', 2, u'ISN·6528') + u' 枚 ⇎ MSL 只有 '
    + V(u'msl', 2, u'MSL·6528') + u' 枚——它把论证重心从“等多久”挪到“怎么发号”。9293 的 reboot ' + V(u'reboot', 3, u'reboot·9293')
    + u' 处是四份里唯一把这当作时钟丢失场景来讲的一份。')

LINES.append(
    u'🧩 写法轴与池代数: 归一长行池 ' + V(u'pool_n', None, u'池条数') + u' 条按“压在几份里”分档 ' + J(u'pool_tier', u'池分档')
    + u'(分档闭合 ' + V(u'pool_tier_close', None, u'池分档闭合') + u' ⇎ 容斥并集闭合 ' + V(u'union_close', None, u'容斥闭合')
    + u' ⇎ 并集 ' + V(u'union_all', None, u'并集') + u' ⇎ 只在本份 ' + J(u'only_each', u'只在本份') + u'), 三份同现 '
    + V(u'pool_3', None, u'三源同现') + u' 条 ⇎ 四份同现 ' + V(u'pool_4', None, u'四源同现')
    + u' 条——四份同现零枚, 所以“逐字节同形 ⇎ 只差一根写法轴”那两档在本条空转(轴账闭合 '
    + V(u'axis_close', None, u'轴账闭合') + u', 分档 ' + V(u'axis_str_n', None, u'轴档非零数') + u' 枚非零: '
    + F[u'axis_str'] + u'); 唯一那条三源同现的长行是状态机记号 ' + AN(0, F[u's3_raw_first']) + u'(归一长度对账 '
    + V(u's3_norm_close', None, u'归一长度对账') + u', 实际压在 ' + V(u's3_docs', None, u'该记号份数')
    + u' 份面上), 它在三三交 '
    + J(u'tri_share', u'三三交') + u' 里占 793⇎1122⇎9293 那一枚(' + V(u'tri_share', 1, u'三三交ABD')
    + u')——三份共抄同一张状态转换记号行而各写散文。锚候选池 ' + V(u'apool_n', None, u'锚池') + u' 条按标签 '
    + J(u'apool_tag_n', u'锚池标签') + u' ⇎ 按出现份数 ' + u' ⇎ '.join(V(u'apool_%d' % k, None, u'锚池%d份' % k)
                                                                       for k in (1, 2, 3, 4)) + u'(标签闭合 '
    + V(u'apool_tag_close', None, u'锚池标签闭合') + u' ⇎ 份数闭合 ' + V(u'apool_tier_close', None, u'锚池分档闭合') + u')。'
    + u'2MSL 四式并计: 连字式 ' + J(u'f2msl', u'2MSL') + u' ⇎ 乘号式 ' + J(u'f2x', u'2xMSL') + u' ⇎ 星号式 '
    + J(u'f2star', u'2*MSL') + u' ⇎ 带空格 ' + J(u'f2xsp', u'2 x MSL') + u' ⇎ 合计 ' + J(u'form_all', u'四式合计')
    + u' ⇎ 同面并存式数 ' + J(u'form_distinct', u'并存式数') + u' ⇎ 各式出现的份数 ' + J(u'form_docs', u'式·份数')
    + u'——1122 与 9293 各自同时写两种式样(并存 ' + V(u'form_distinct', 1, u'并存·1122') + u' ⇎ '
    + V(u'form_distinct', 3, u'并存·9293') + u' 式), 6528 只用星号式, 793 只在图里用连字式; 只按一种式样搜就会把另外三份读成“没有这条规则”。')

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
    got = [e for e in ELEMS.get(s, []) if eval(e, {FN: BB69}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, NOEXPR
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv69.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b69flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms69.txt', 'w', encoding='utf-8', newline=NL).write(
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
           u'closure_keys': sorted([k for k in F if u'close' in k or k == u'up_ledger']), u'flat': F})
json.dump(CH, io.open(u'corpus/_b69checks.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

ENTRY = u'corpus/babeltele/B69_tcp_timewait_linger_four_answers.md'
srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 码位／原行 %d／非空行 %d／最长行 %d 列／答句 %s／页壳换页 %d 枚)' % (
        PATH[i].split('/')[-1], F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        F[u'maxlen'][i], [u'定 MSL 为 %d 分钟且许可违背 quiet time' % NUM[u'minutes_a'],
                          u'MUST linger 2xMSL 但两条件下 MAY 立刻接受新 SYN',
                          u'不问等待、从 last seen 起算 2*MSL',
                          u'收下 %d 分钟句、主语改 endpoint 并 Obsoletes 前三份' % NUM[u'minutes_d']][i],
        F[u'ff'][i]) for i in range(NSRC))
           + u' (四份 RFC Editor 纯文本面, 全 LF; 9293 带一枚 BOM 与两枚取变音符, 摘掉 BOM 后正文纯 ASCII; '
             u'MSL 分钟数、绕回小时、时钟微秒与图内 Timeout 全由句内游标现读, 一个都不手填。抓取时刻、RFC Editor 此刻的现行状态页与勘误页、'
             u'此后哪份文档又动了这段、现网内核实际把 TIME-WAIT 设成多久, 都只在本机或站外成立, 不进门槛)\n')
link = (u"；联结不是“同一份数据的两种序列化”, 而是“主动关掉一条连接之后到底要等多久、能不能跳过这段等待”在四份一手 TCP 文书里的四种答法: "
        u"793 把 MSL 任意定成 {0} 分钟(术语表另处再写一遍 {1} 分钟, 闭合 {2}), 同段承认“这是工程选择”并把违背 quiet time 写成明文许可"
        u"(在册 {3} 枚答句针里它面上 {4} 枚走逐行档、其余要折平), 全篇大写 MUST {5} 枚; ⇎ "
        u"1122 换成 MUST linger 两枚 MSL——式样写 2xMSL {6} 枚, 又把出口写进同一句(MAY accept a new SYN, 两条件各 {7}⇎{8} 枚), "
        u"还嫌端口 tied up 而允许缩短 {9} 枚; ⇎ "
        u"6528 取消“等”这个动作: 判据改成“自上一段报文最后被见到起是否已过 2*MSL”({10} 枚星号式), 全篇不写 MSL 等于几分钟"
        u"(“2 minutes” {11} 处 ⇎ “taken to be” 句式 {12} 枚), 并把 ISS 生成换成慢时钟加伪随机(ISN 字样 {13} 枚 ⇎ MSL 只 {14} 枚); ⇎ "
        u"9293 同时收下三家: 793 那句 {15} 分钟在它面上逐字再现(两份同形闭合 {16}), 1122 的 linger 与两条件各再现 {17}⇎{18} 次, "
        u"而 793 的 keep-quiet 整句被改写(判定 {19}), 主语换成 TCP endpoint; 它一页 Obsoletes 掉 {20} 枚 RFC(含 6528)。"
        u"逐字搬运可量: 归一长行六对里非零 {21} 对, 最大一对 793⇎9293 归一 {22} 行(逐字节 {23} ⇎ 仅归一 {24}), 1122⇎9293 {25} 行, "
        u"6528⇎9293 归一 {26} 行而逐字节 {27} 行——算法收下、句子重写; 四份同现的长行 {28} 条, 写法分家两档因此空转(轴账闭合 {29}).\n").format(
    NUM[u'minutes_a'], NUM[u'minutes_arb'], F[u'arb_eq_spec'], F[u'needle_n'], F[u'sn_strict_docs'][0],
    F[u'up_must_all'][0], F[u'f2x'][1], F[u'n_b_cond1'][1], F[u'n_b_cond2'][1], F[u'n_b_shorten'][1], F[u'f2star'][2], F[u'c2m'][2], F[u'msl_taken'][2],
    F[u'isn'][2], F[u'msl'][2], NUM[u'minutes_d'], F[u'msl2_same_bytes'], F[u'n_b_cond1'][3], F[u'n_b_cond2'][3],
    F[u'quiet_rewritten'], F[u'n_d_obsoletes'][3], F[u'pair_nonzero'], F[u'pair_share'][2], F[u'pair_byte'][2],
    F[u'pair_norm_only'][2], F[u'pair_share'][4], F[u'pair_share'][5], F[u'pair_byte'][5], F[u'pool_4'], F[u'axis_close'])
title = (u'# B69 主动关闭一条连接之后到底要等多久、这段等待能不能跳过，四份 TCP 一手文书四种答法：'
         u'任意定 MSL 且明文许可违背 ⇎ MUST linger 两枚 MSL 却自带 MAY 出口 ⇎ 不问等待而从“最后见到报文”起算 ⇎ '
         u'收下 2 分钟句、把义务主语换成 endpoint 并一次性 Obsoletes 前三份（时长⇎起算点⇎可否跳过⇎语气主体四件事没有一份给全）\n')
tags = (u'tags: 时长⇎起算点⇎可否跳过⇎语气主体 四件事分给四份文书 句内游标解析(正读 ⇎ 逆读到带小数的小时) '
        u'taken-to-be 句式两份同形⇎1122 的 2 minutes 不在定义句里 MSL 分钟数缺席档(6528 不给分钟 ⇎ 只给 2*MSL 式) '
        u'Timeout=2MSL 图式跨两份逐字同 绕回小时 4.55 与“MSL 必须短过它”的单向推理 时钟步长微秒两份一致 '
        u'MUST linger ⇎ MAY accept 同句自带出口(两句劈在行界两侧, 折行档必需) 两条件句被 9293 逐字收下 '
        u'6528 取消等待改按 last seen ⇎ quiet time 整句被 9293 改写主语 keep-quiet 义务主体 TCP→TCP endpoint '
        u'三面阶梯只走到两阶(9293 零换页符⇒摘壳档空转) 2MSL 四式并计(连字⇎2x⇎2*⇎带空格) 同面并存两式(1122⇎9293) '
        u'引用三式并计(RFC-793 短横式独占 1122 ⇎ RFC 793 空格式独占 6528/9293) 逐字搬运可量(AD 最大对 ⇎ CD 归一有而字节零) '
        '四份同现长行零枚⇒写法分家档空转 状态机记号行三源同现 大写义务词换代(793 零枚⇎1122/9293 百枚级⇎6528 个位) '
        'keep-alive 只在 1122/9293 ⇎ Timestamp 只在 1122/9293 ⇎ ISN 密度最高在 6528 BOM 一枚⇎两枚变音符⇎字节码位差=加字节和 '
        '窗口三轨闭合(MSL⇎TIME-WAIT⇎数字符) 闭合账 标量 %d⇎清单 %d 项⇎恒等式 %d 条\n' % (
            F[u'scalar_clos_n'], len([k for k in F if u'close' in k]), F[u'x_ident_n']))
text = (title + srcline + link + tags +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n'
        + u'## ⟪BabelTele⟫\n' + body + u'\n\n'
        + u'## ⛓解读注\n\n（此段由 corpus/_fill69.py 从 corpus/_b69checks.json 与 corpus/_deriv69.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s ｜ 归属错配 %d ⇎ 非原行 %d' % (USED, DIST, TAGN, len(ERR), len(MISSLINE)))
print(u'一源 %d ⇎ 二至三源 %d ⇎ 四源 %d ｜ 针 %d ⇎ 折行独有 %s ⇎ 阶梯 %s⇎%s⇎%s' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], F[u'needle_n'], F[u'fold_only_keys'],
    F[u'sn_strict_docs'], F[u'sn_fold_docs'], F[u'sn_sh_docs']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ⇎ 恒等式 %d ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), F[u'x_ident_n'], len(F)))
print(u'游标读数 %s ⇎ 绕回小时 %s ⇎ 分钟句份数 %s ⇎ 时长命中 %s' % (
    NUM, F[u'cycle_h'], F[u'msl_taken'], F[u'dur_hit_total']))
print(u'搬运 归一 %s ⇎ 字节 %s ⇎ 仅归一 %s ⇎ 非零对 %d ｜ 池 %s tier %s 闭合 %d ⇎ 四源同现 %d' % (
    F[u'pair_share'], F[u'pair_byte'], F[u'pair_norm_only'], F[u'pair_nonzero'], F[u'pool_n'], F[u'pool_tier'],
    F[u'pool_tier_close'], F[u'pool_4']))
print(u'窗 标题 %s ⇎ 起 %s 止 %s 长 %s ⇎ 闭合三轨 %d' % (
    F[u'win_title'], F[u'win_start'], F[u'win_end'], F[u'win_chars'], F[u'win_close_sum']))
print(u'义务 大写MUST %s ⇎ 裸 %s ⇎ MUSTNOT %s ⇎ MAY %s ⇎ 账 %s' % (
    F[u'up_must_all'], F[u'must_bare'], F[u'must_not'], F[u'up_may'], F[u'up_ledger']))
print(u'写法四式 2MSL %s ⇎ 2x %s ⇎ 2* %s ⇎ 合计 %s ⇎ 并存 %s' % (
    F[u'f2msl'], F[u'f2x'], F[u'f2star'], F[u'form_all'], F[u'form_distinct']))
