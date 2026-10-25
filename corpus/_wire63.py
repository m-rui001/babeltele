# -*- coding: utf-8 -*-
"""把 B63 的独立复算器(_b63_scan / B63V)接进 audit.py, 并生成 DERIV['B63']。
幂等: 重复运行先摘旧块再插新块。
_b63_scan 的量测段从 corpus/_mkB63.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自五处:
①采集侧 corpus/_pick63.py 是先于建条目写好的另一套实现(它用 re.findall 数义务词与引用、
  用集合运算求搬运交集、按 (\\d+)\\s*(second|ms) 类抽时长成对读数、以 set & 算四源共行),
  两边在 412 个口径一致的键上逐量对账(四份都是纯文本面, 无需按介质分流; 现况 240 采集键／不符 0,
  采集侧独有的 3 键是它自己的页眉⇎页脚⇎换页声明档, 建条目侧改立 foot/formfeed 口径, 不共用键名);
②抽出的代码在插门之前要把 _b63flat.json 的每个键与 DERIV['B63'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按归一串判成员;
④和式的可判性与第一遍不同: 建条目侧把 RTO <- SRTT + max (G, K*RTTVAR) 与 PTO = smoothed_rtt +
  max(4*rttvar, kGranularity) + max_ack_delay 当结构解析(深度 0 的 ' + ' 分列、括号按逗号拆两参数、
  max_ack_delay 靠 is_maxnode 排除), 而非数正则命中; 数字读数一律从面内现读(答数、地板、上限、
  K 的定义行、方差除数、粒度值), 手填常数为零;
⑤宣称⇎复算是门可算的量: 用 D 自己面内的三枚常数(333/4/1)复算 PTO 得 999⇎997, 与它写出的 1000
  相减得两枚非零差(1⇎3 毫秒), 库里零字面——这条差只能由复算给出, 因此必须进门槛而不是只进注。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB63.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/tcpRTO/rfc1122.txt', u'corpus/raw/tcpRTO/rfc2988.txt',
        u'corpus/raw/tcpRTO/rfc6298.txt', u'corpus/raw/tcpiw/rfc9002.txt']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'# --- SCAN BEGIN ---', u'# --- SCAN END ---')
MEAS = MEAS[MEAS.index(NL) + 1:]
assert u'F[u' in MEAS and u'POOL' in MEAS and u'ZID' in MEAS and u'abcd_close' in MEAS
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
assert u'FAN' in MEAS and u'ATOMSEL' in MEAS and u'pnorm' in MEAS
assert u'dur_scan' in MEAS and u'is_maxnode' in MEAS and u'parse_sum_lines' in MEAS
assert u'y_ans_ms' in MEAS and u'align_n' in MEAS and u'dur_after' in MEAS

HEAD = u'''
# B63: 还没有 RTT 样本时第一个重传超时设多久——四份 RFC Editor 纯文本四种答法:
# raw/tcpRTO/rfc1122.txt(A 89 三秒: 整本主机需求书, 只给新建连接的初始化清单 "(b)  RTO = 3 seconds.",
#   算法本体让读者去执行 Karn 与 Jacobson; 倒推句 "variance ... initialized to the value that will
#   result in this RTO" 只属它; RTO 上限 2*MSL = 240 秒被排版拆在两行)
# ⇎ rfc2988.txt(B 00 三秒: 同一答数写成 set RTO <- 3 seconds (per RFC 1122 [Bra89]), 与 A 零共用行,
#   却原样接过上取整地板 1 秒(比它自己的答数低 2000 毫秒)与 60 秒上限)
# ⇎ rfc6298.txt(C 11 一秒: Obsoletes 2988 + Updates 1122, 答数降到 1 秒而 "3 seconds" 字面从 1 处涨到 9 处
#   ——窗内 1 ⇎ 窗外 8, 那枚 3000 毫秒被搬进 (5.7) 的 SYN 回退 MUST; 地板恰等于它自己的初值;
#   同一条 (2.4) 条款与被废止者在 4 行里 3 行逐字节全等、1 行只差一个逗号)
# ⇎ rfc9002.txt(D 21 三百三: QUIC 给的是初始 RTT 333 毫秒而非超时, PTO 由本份三枚常数复算,
#   实数 999 ⇎ 取整 997 都对不上它宣称的 1 秒(差 1 ⇎ 3 毫秒, 库内零字面), max() 两参数换了序、
#   末尾多一项 max_ack_delay, K 从符号写成字面 4, 变量名整套换代 SRTT/RTTVAR→smoothed_rtt/rttvar;
#   唯一不分页、带 BOM、含 8 枚非 ASCII 码点的一份)。
# 本函数从四份字节独立复算: 和式结构解析(深度 0 分列⇎max 拆参数⇎尾项排除), 面内现读的答数/地板/上限/系数/除数,
# 规范窗⇎窗外的搬家账(secw⇎outw 相加闭合), 时长归一毫秒并给每枚 token 打跨行⇎割小数两枚标志,
# 宣称⇎两种复算三键并立, 原面逐字面⇎空白折平两档之差, 归一⇎逐字节两把搬运尺, 页眉两式⇎页脚⇎换页⇎行尾空格四本账,
# 义务词全大写⇎小写两档与窗内窗外、引用网(1122⇎2988⇎6298⇎9002 各被谁引)、锚候选池按逐字再现份数四层划分与锚归属由正文现推、
# 四源长行容斥。30 条由面内现读数构成的恒等式(3000=9×333+3、999=3×333、3000=3000、240000=240000、1=1、
# 240000=4×60000)全归零送门槛重算。
# 不可由在库文件判定的: 四份的抓取时刻与磁盘 mtime 谁新谁旧、rfc-editor.org 此刻的现行状态页、
# 勘误页是否已挂新版、各家实现里 TCP_RTO_MIN 的实际取值——只进解读注, 不进门槛。
def _b63_scan():
    import hashlib as _hl
    import os as _os
    P2 = SRC['B63']
    NSRC = 4
    TAGS = [u'A', u'B', u'C', u'D']
    LB = dict(zip(TAGS, [u'89 三秒', u'00 三秒', u'11 一秒', u'21 三百三']))
    PATH = P2
    IDX = dict((t, i) for i, t in enumerate(TAGS))
    RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
    ROOT = u''
    C = u'corpus'
    NL = chr(10)
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
for a, b in ((u'os.path.getsize(', u'_os.path.getsize('), (u'hashlib.', u'_hl.')):
    BODYTXT = re.sub(u'(?<![.\\w])' + re.escape(a), b, BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert u'_os.open(' not in BODYTXT, u'裸 open( 被误改写'
assert u'_hl.blake2b' in BODYTXT and u'_os.path.getsize' in BODYTXT

TAIL = u'''
    # ---- 结构性自检: 四答、和式形状、窗⇎窗外搬家、时长归一、宣称⇎复算、版式四账、搬运容斥 ----
    assert F[u'bytes'] == [289148, 15280, 22454, 89071] and F[u'sig_distinct'] == 4
    assert len(set(F[u'sig'])) == 4 and F[u'chars'] == [289148, 15280, 22454, 89053]
    assert F[u'bytes'][3] - F[u'chars'][3] == 18
    assert F[u'bom'] == [0, 0, 0, 1] and F[u'nonascii'] == [0, 0, 0, 8]
    assert F[u'nonascii_raw'] == [0, 0, 0, 9]
    assert F[u'chars_split'] == F[u'chars'] and F[u'chars_no_nl'] == [282304, 14829, 21835, 86983]
    assert F[u'lines'] == [6845, 452, 620, 2071] and F[u'lines_nl'] == F[u'lines']
    assert F[u'nonblank'] == [4549, 264, 387, 1635] and F[u'maxlen'] == [72, 73, 72, 72]
    assert F[u'rec_close'] == [0] * 4 and F[u'cr'] == [0] * 4
    assert F[u'hdr'] == [115, 7, 10, 0] and F[u'hdr_ns'] == [115, 0, 0, 0]
    assert F[u'hdr_sp'] == [0, 7, 10, 0]
    assert [F[u'hdr_ns'][i] + F[u'hdr_sp'][i] - F[u'hdr'][i] for i in range(4)] == [0] * 4
    assert F[u'hdr_ledger'] == [0, 0, 0, 0] and F[u'hdr_ledger_sum'] == 0
    assert F[u'foot'] == [116, 8, 11, 0] and F[u'foot_brk'] == F[u'foot']
    assert F[u'foot_ietf'] == [116, 0, 0, 0] and F[u'formfeed'] == [116, 8, 11, 0]
    assert [F[u'foot_ietf'][i] - F[u'formfeed'][i] for i in range(4)] == [0, -8, -11, 0]
    assert F[u'ietf_vs_ff'] == [0, -8, -11, 0] and F[u'ietf_vs_ff'][0] == 0
    assert F[u'ff_foot_sum'] == 0 and F[u'trail'] == F[u'foot'] and F[u'trail_foot_sum'] == 0
    assert F[u'braden_foot'] == [7, 1, 2, 0] and F[u'editor_hdr'] == [2, 1, 0, 0]
    assert F[u'pagelines'] == [231, 15, 21, 0] and F[u'pages_est'] == [116, 8, 11, 0]
    assert F[u'pagelines'][3] == F[u'pages_est'][3] == F[u'foot'][3] == 0
    assert F[u'lines_ge40'] == [2531, 167, 235, 901] and F[u'shell_delta'] == [0, 1, 1, 0]
    assert F[u'lines_ge40_nos'] == [F[u'lines_ge40'][i] - F[u'shell_delta'][i] for i in range(4)]

    assert F[u'y_ans_ms'] == [3000, 3000, 1000, 333] and F[u'y_ans_distinct'] == 3
    assert F[u'y_ans_max'] == 3000 and F[u'y_ans_min'] == 333
    assert F[u'y_ans_ratio'] == 9 and F[u'y_ans_rem'] == 3
    assert F[u'y_ans_ratio'] * F[u'y_ans_min'] + F[u'y_ans_rem'] == F[u'y_ans_max']
    assert F[u'y_ans_unit'] == [u'seconds', u'seconds', u'second', u'milliseconds']
    assert F[u'y_ans_unit_sing'] == [1 if u == u'second' else 0 for u in F[u'y_ans_unit']] == [0, 0, 1, 0]
    assert F[u'y_ans_wrap'] == [0] * 4 and F[u'y_ans_num'] == [u'3', u'3', u'1', u'333']
    assert F[u'y_claim_ms'] == [3000, 3000, 1000, 1000] and F[u'y_claim_distinct'] == 2
    assert F[u'y_claim_vs_ans'] == F[u'y_claim_distinct'] - F[u'y_ans_distinct'] == -1
    assert F[u'y_ans_ms'][2] == F[u'y_claim_ms'][3] == 1000
    assert F[u'lit_3seconds'] == [1, 1, 9, 0] and F[u'lit_onesecclaim'] == [0, 0, 0, 1]
    assert F[u'y_secw_threesec'] == [1, 1, 1, 0] and F[u'y_outw_threesec'] == [0, 0, 8, 0]
    assert [F[u'y_secw_threesec'][i] + F[u'y_outw_threesec'][i] - F[u'lit_3seconds'][i]
            for i in range(4)] == [0] * 4
    assert F[u'secw_3seconds'] == F[u'y_secw_threesec'] and F[u'outw_3seconds'] == F[u'y_outw_threesec']
    assert F[u'y_c_revert_ms'] == 3000 and F[u'y_c_revert_wrap'] == 0
    assert F[u'y_c_revert_eq_a'] == F[u'y_c_revert_ms'] - F[u'y_ans_ms'][0] == 0
    assert F[u'y_c_revert_eq_b'] == F[u'y_c_revert_ms'] - F[u'y_ans_ms'][1] == 0
    assert F[u'y_c_may_still'] == 1 and F[u'y_b_may_still'] == 0
    assert F[u'y_c_may_still_fold'] == F[u'y_c_may_still']
    assert F[u'y_c_lower_note'] == 1 and F[u'lit_revert'] == [0, 0, 1, 0]
    assert F[u'secw_333full'] == [0, 0, 0, 1] and F[u'outw_333full'] == [0] * 4
    assert F[u'secw_333ms'] == [0] * 4 and F[u'outw_333ms'] == [0, 0, 0, 1]
    assert F[u'lit_333full'] == [0, 0, 0, 1] and F[u'lit_333ms'] == [0, 0, 0, 1]
    assert F[u'unit_both_333'] == [0, 0, 0, 1]
    for k in (u'3seconds', u'1second', u'333full', u'333ms', u'kgran', u'rounded', u'rtoarrow'):
        assert [F[u'secw_' + k][i] + F[u'outw_' + k][i] - F[u'lit_' + k][i] for i in range(4)] == [0] * 4, k

    assert F[u'y_sum_n'] == [0, 3, 3, 1] and F[u'y_sum_nterms'] == [0, 2, 2, 3]
    assert F[u'y_sum_shape'] == [u'\\u65e0\\u548c\\u5f0f', u'RTO<-G+K*RTTVAR', u'RTO<-G+K*RTTVAR',
                                 u'PTO=4*rttvar+kGranularity']
    assert F[u'y_sum_lhs'] == [u'', u'RTO', u'RTO', u'PTO'] and F[u'y_sum_op'] == [u'', u'<-', u'<-', u'=']
    assert F[u'y_sum_base'] == [u'', u'SRTT', u'SRTT', u'smoothed_rtt']
    assert F[u'y_sum_coef'] == [u'', u'K', u'K', u'4'] and F[u'y_coef_islit'] == [0, 0, 0, 1]
    assert F[u'y_coef_num'] == [0, 0, 0, 4]
    assert F[u'y_sum_mfirst'] == [u'', u'G', u'G', u'4*rttvar']
    assert F[u'y_sum_msecond'] == [u'', u'K*RTTVAR', u'K*RTTVAR', u'kGranularity']
    assert F[u'y_sum_var_first'] == [0, 0, 0, 1] and F[u'y_sum_mvar'] == [u'', u'RTTVAR', u'RTTVAR', u'rttvar']
    assert F[u'y_sum_tail'] == [u'', u'', u'', u'max_ack_delay'] and F[u'y_sum_tail_n'] == [0, 0, 0, 1]
    assert F[u'y_k_close'] == F[u'y_d_k'] - F[u'y_c_kdef'] == 4 - 4 == 0
    assert F[u'y_b_kdef'] == F[u'y_c_kdef'] == F[u'y_d_k'] == 4
    assert F[u'y_klit_sp'] == F[u'y_klit_ns'] == [0, 0, 0, 4] and F[u'y_klit_close'] == [0] * 4
    assert F[u'lit_4k_rttvar'] == F[u'lit_4xrttvar'] == [0, 0, 0, 4]
    assert F[u'assign_forms'] == [1, 5, 5, 0] and F[u'lit_rtoarrow'] == [0, 5, 5, 0]
    assert [F[u'lit_rtovalue'][i] + F[u'lit_rtoarrow'][i] - F[u'assign_forms'][i]
            for i in range(4)] == [0] * 4
    assert F[u'lit_pto_eq'] == [0, 0, 0, 1] and F[u'y_sum_n'][0] == 0
    assert F[u'y_a_rule_in_bc'] == [0, 0, 0] and F[u'y_a_sent_in_bc'] == [1, 0, 0, 0]
    assert F[u'y_a_varfrom'] == 1 and F[u'y_bc_varfrom'] == [1, 0, 0, 0]
    assert sum(F[u'y_bc_varfrom']) == F[u'y_a_varfrom'] == 1

    assert F[u'y_floor_ms'] == [0, 1000, 1000, 0] and F[u'y_floor_wrap'] == [0] * 4
    assert F[u'y_b_floor_gap'] == F[u'y_ans_ms'][1] - F[u'y_floor_ms'][1] == 2000
    assert F[u'y_bc_floor_close'] == F[u'y_floor_ms'][1] - F[u'y_floor_ms'][2] == 0
    assert F[u'y_c_floor_eq_init'] == F[u'y_floor_ms'][2] - F[u'y_ans_ms'][2] == 0
    assert F[u'y_floor_lines'] == [0, 1, 1, 0] and F[u'lit_rounded'] == [0, 1, 1, 0]
    assert F[u'secw_rounded'] == [0, 1, 1, 0] and F[u'outw_rounded'] == [0] * 4
    assert F[u'floor_pair'] == [1, 1] and F[u'floor_same_bytes'] == [1]
    assert F[u'floor_same_norm'] == [1] and F[u'floor_diff_bytes'] == [0]
    assert F[u'floor_close'] == (F[u'floor_same_bytes'][0] + F[u'floor_diff_bytes'][0]
                                 - F[u'floor_pair'][0]) == 0
    assert F[u'align_n'] == 4 and F[u'align_same_bytes'] == 3 and F[u'align_punct_only'] == 1
    assert F[u'align_norm_diff'] == 0
    assert F[u'align_close'] == (F[u'align_same_bytes'] + F[u'align_punct_only']
                                 + F[u'align_norm_diff'] - F[u'align_n']) == 0
    assert F[u'align_comma'] == 1 and F[u'align_char_delta'] == 1
    assert F[u'lit_commab'] == [0, 1, 0, 0] and F[u'lit_commac'] == [0, 0, 1, 0]
    assert F[u'y_clause_pair_n'] == 4 and F[u'floor_forms_gap'] == [0, 1, 1, 0]

    assert F[u'y_d_kinit'] == 333 and F[u'y_d_kinit_lit'] == 1 and F[u'y_d_gran'] == 1
    assert F[u'y_d_gran_unit'] == u'ms' and F[u'y_d_k'] == 4
    assert F[u'y_d_pto_exact'] == 999 and F[u'y_d_pto_int'] == 997 and F[u'y_d_claim_ms'] == 1000
    assert F[u'y_d_var_int'] == 166 and F[u'y_d_var_frac'] == 1
    assert F[u'y_ans_ms'][3] == 2 * F[u'y_d_var_int'] + F[u'y_d_var_frac'] == 333
    assert F[u'y_d_pto_exact'] == F[u'y_d_three'] * F[u'y_ans_ms'][3] == 3 * 333
    assert F[u'y_d_three'] == 3 and F[u'y_d_three_close'] == 0
    assert F[u'y_d_gap_exact'] == F[u'y_d_claim_ms'] - F[u'y_d_pto_exact'] == 1
    assert F[u'y_d_gap_int'] == F[u'y_d_claim_ms'] - F[u'y_d_pto_int'] == 3
    assert F[u'y_d_pto_spread'] == F[u'y_d_gap_int'] - F[u'y_d_gap_exact'] == 2
    assert F[u'y_d_gran_binds'] == 0 and F[u'y_d_floor'] == 1 and F[u'y_d_mad0'] == 1
    assert F[u'y_half_b'] == F[u'y_half_c'] == F[u'y_half_d'] == 2
    assert F[u'y_b_c_half_close'] == F[u'y_half_close'] == 0 and F[u'lit_half'] == [0, 0, 0, 2]
    assert F[u's_half'] == [0, 0, 0, 2] and F[u'lit_smoothinit'] == [0, 0, 0, 2]
    assert F[u'lit_kgran'] == [0, 0, 0, 11] and F[u'outw_kgran'] == [0, 0, 0, 11]
    assert F[u'secw_kgran'] == [0] * 4 and F[u'lit_kinirtt'] == [0, 0, 0, 7]
    assert F[u'y_gransym'] == [0, 2, 1, 0] and F[u'v_gran'] == [1, 4, 3, 3]
    assert F[u'v_clock'] == [0, 2, 2, 0] and F[u'lit_1ms'] == [0, 0, 0, 1]

    assert F[u'durms_a'] == [3000, 5000, 60000, 100000, 120000, 240000]
    assert F[u'durms_b'] == [1000, 3000, 5000, 60000] and F[u'durms_c'] == [1000, 3000, 60000]
    assert F[u'durms_d'] == [1, 333, 1000]
    assert F[u'durms_n'] == [len(F[u'durms_' + t.lower()]) for t in TAGS] == [6, 4, 3, 3]
    assert F[u'durlit'] == [F[u'durlit_' + t.lower()] for t in TAGS] == [11, 8, 24, 5]
    assert F[u'dur_ms_lo'] == 1 and F[u'dur_ms_hi'] == 240000 and F[u'y_dur_ratio'] == 240000
    assert F[u'y_dur_rem'] == F[u'dur_ms_hi'] % F[u'dur_ms_lo'] == 0
    assert F[u'durlo_gran_close'] == F[u'dur_ms_lo'] - F[u'y_d_gran'] == 0
    assert F[u'durhi_cap_close'] == F[u'dur_ms_hi'] - F[u'y_a_cap_ms'] == 0
    assert F[u'y_dur_frac'] == [3, 3, 0, 0] and F[u'y_dur_frac_only'] == [1, 1, 0, 0]
    assert [list(x) for x in F[u'y_dur_frac_vals']] == [[0, 5000], [5000], [], []]
    assert F[u'y_dur_wrap'] == [4, 2, 3, 0]
    assert [list(x) for x in F[u'y_dur_wrap_ms']] == [[0, 60000, 120000, 240000], [3000, 60000],
                                                     [1000, 3000, 60000], []]
    assert F[u'y_dur_zero'] == [2, 0, 0, 0] and F[u'y_dur_zero_wrap'] == [1, 0, 0, 0]
    assert F[u'y_dur_zero_frac'] == [1, 0, 0, 0] and F[u'lit_rtovalue'] == [1, 0, 0, 0]
    assert F[u'y_rtt0'] == [1, 0, 0, 0]
    assert F[u'y_dur_win_n'] == [len(x) for x in F[u'y_dur_win']] == [2, 4, 3, 2]
    assert F[u'y_dur_out_n'] == [len(x) for x in F[u'y_dur_out']] == [4, 0, 2, 2]
    assert F[u'dur_ms_lo'] == min(min(x) for x in [F[u'durms_' + t.lower()] for t in TAGS])
    assert F[u'dur_ms_hi'] == max(max(x) for x in [F[u'durms_' + t.lower()] for t in TAGS])
    ALLV = [v for part in (F[u'y_dur_win'] + F[u'y_dur_out']) for v in part]
    assert F[u'dur_ms_lo'] == min(ALLV) and F[u'dur_ms_hi'] == max(ALLV)
    assert sorted(set(ALLV)) == sorted(set(sum([F[u'durms_' + t.lower()] for t in TAGS], [])))
    assert F[u'y_dur_win'][0] == [3000, 240000] and F[u'y_dur_out'][0] == [5000, 60000, 100000, 120000]
    assert F[u'y_dur_win'][1] == F[u'durms_b'] and F[u'y_dur_out'][1] == []
    assert F[u'y_unit_n'] == [len(x) for x in F[u'y_unit_used']] == [1, 2, 2, 4]
    assert F[u'y_unit_used'][3] == [u'millisecond', u'milliseconds', u'ms', u'second']
    assert F[u'unit_mill_word'] == [2, 0, 0, 2] and F[u'unit_ms'] == [161, 3, 4, 34]
    assert F[u'unit_seconds'] == [25, 15, 30, 3]
    assert F[u'y_a_cap_ms'] == 240000 and F[u'y_a_cap_wrap'] == 1 and F[u'y_a_cap_win'] == 1
    assert F[u'y_a_mult'] == 2 and F[u'y_a_msl_word'] == 8
    assert F[u'y_bc_cap_ms'] == [0, 60000, 60000, 0] and F[u'y_bc_cap_wrap'] == [0, 1, 1, 0]
    assert F[u'y_bc_cap_win'] == [0, 1, 1, 0] and F[u'lit_200ms'] == [0] * 4
    assert F[u'y_cap_ratio'] == 4 and F[u'y_cap_rem'] == 0
    assert F[u'y_cap_ratio_close'] == (F[u'y_a_cap_ms'] - F[u'y_cap_ratio'] * F[u'y_cap_ref_ms']
                                       - F[u'y_cap_rem']) == 0
    assert F[u'y_cap_ref_ms'] == F[u'y_bc_cap_ms'][1] == 60000

    assert F[u'sec_a'] == [5576, 71, 102, 693] and F[u'sec_b'] == [5645, 145, 181, 744]
    assert [list(x) for x in F[u'sec_w']] == [[F[u'sec_a'][i], F[u'sec_b'][i]] for i in range(4)]
    assert F[u'sec_len'] == [3047, 2814, 2797, 2712] and F[u'sec_hit'] == [1, 1, 1, 1]
    assert max(F[u'sec_len']) - min(F[u'sec_len']) == 335
    assert F[u'sec_sub'] == [2, 0, 0, 0] and F[u'sec_num'] == [u'4..2..3..1', u'2', u'2', u'6..2..2']
    assert F[u'sec_head'][1] == u'2   The Basic Algorithm' and F[u'sec_head'][2] == u'2.  The Basic Algorithm'
    assert F[u'y_outw_appendix'] == [1, 0, 2, 8] and F[u'y_secw_appendix'] == [0, 0, 1, 1]

    assert F[u'wrap_pin_n'] == 14 and F[u'wrap_pin_hit'] == 1 and F[u'wrap_gap_total'] == 1
    assert F[u'wrap_gap_backoff5'] == [0, 1, 0, 0]
    for k in (u'cite6298', u'claim1s', u'floor', u'granrec', u'half', u'init1', u'init3', u'ms333',
              u'pto_eq', u'revert', u'rounded', u'tcpinit', u'v3'):
        assert F[u'wrap_gap_' + k] == [0] * 4, k
    assert F[u's_backoff5'] == [0, 0, 1, 0] and F[u's_backoff5_fold'] == [0, 1, 1, 0]
    assert F[u'lit_backoff'] == [0, 2, 2, 0] and F[u'v_backoff_word'] == [0, 1, 3, 0]
    assert F[u's_cite6298'] == [0, 0, 0, 1] == F[u's_cite6298_fold']
    assert F[u's_claim1s'] == [0, 0, 0, 1] and F[u's_ms333'] == [0, 0, 0, 1]
    assert F[u's_init3'] == [0, 1, 0, 0] and F[u's_init1'] == [0, 0, 1, 0] and F[u's_v3'] == [1, 0, 0, 0]

    assert F[u'u_must'] == [200, 15, 16, 35] and F[u'u_should'] == [73, 8, 7, 27]
    assert F[u'u_may'] == [41, 3, 4, 21] and F[u'u_must_not'] == [20, 3, 3, 9]
    assert F[u'oblig_up'] == [F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i]
                              for i in range(4)] == [314, 26, 27, 83]
    assert F[u'l_must'] == [59, 1, 1, 2] and F[u'l_should'] == [54, 3, 5, 4] and F[u'l_may'] == [121, 9, 6, 14]
    assert F[u'oblig_low'] == [F[u'l_must'][i] + F[u'l_should'][i] + F[u'l_may'][i] for i in range(4)]
    assert F[u'y_secw_must'] == [2, 4, 4, 5] and F[u'y_secw_should'] == [3, 4, 3, 2]
    assert F[u'y_secw_may'] == [0, 1, 2, 2] and F[u'y_secw_must_not'] == [0, 0, 0, 1]
    assert F[u'y_oblig_win'] == [F[u'y_secw_must'][i] + F[u'y_secw_should'][i] + F[u'y_secw_may'][i]
                                 for i in range(4)] == [5, 9, 9, 9]
    assert [F[u'y_outw_may'][i] + F[u'y_secw_may'][i] - F[u'u_may'][i] for i in range(4)] == [0] * 4
    assert F[u'y_outw_must'] == [198, 11, 12, 30] and F[u'y_outw_should'] == [70, 4, 4, 25]
    assert F[u'rfc2119_ref'] == [0, 1, 1, 6] and F[u'key_words_boiler'] == [0, 2, 2, 2]

    assert F[u'lit_srtt'] == [0, 15, 15, 0] and F[u'lit_rttvar_u'] == [0, 14, 14, 0]
    assert F[u'lit_rttvar_l'] == [0, 0, 0, 27] and F[u'lit_smoothed'] == [0, 0, 0, 38]
    assert F[u'lit_pto'] == [0, 0, 0, 79] and F[u'v_pto'] == [0, 0, 0, 79]
    assert F[u'y_name_family'] == [F[u'lit_srtt'][i] + F[u'lit_rttvar_u'][i] for i in range(4)] == [0, 29, 29, 0]
    assert F[u'y_name_family_l'] == [F[u'lit_rttvar_l'][i] + F[u'lit_smoothed'][i] for i in range(4)] == [0, 0, 0, 65]
    assert F[u'y_case_gap_rttvar'] == [F[u'lit_rttvar_u'][i] - F[u'lit_rttvar_l'][i] for i in range(4)]
    assert F[u'lit_rto'] == [10, 36, 58, 15] == F[u'v_rto']
    assert F[u'lit_inirto'] == F[u'v_initrto_low'] == [0, 0, 13, 0]
    assert F[u'v_initrto_cap'] == [0, 0, 1, 0] and F[u'y_secw_inirto'] == [0, 0, 1, 0]
    assert F[u'y_outw_inirto'] == [0, 0, 12, 0]
    assert [F[u'y_secw_inirto'][i] + F[u'y_outw_inirto'][i] - F[u'lit_inirto'][i] for i in range(4)] == [0] * 4
    assert F[u'lit_smoothinit'] == [0, 0, 0, 2] and F[u'lit_tcpinitrto'] == [0, 0, 0, 1]
    assert F[u'v_variance'] == [5, 1, 1, 0] and F[u'lit_setrto'] == [0, 2, 2, 0]
    assert F[u'v_rtt'] == [7, 50, 56, 113] and F[u'v_timer'] == [9, 18, 15, 58]
    assert F[u'v_congest'] == [0, 0, 0, 31] and F[u'v_persist'] == [0, 0, 0, 30]
    assert F[u'v_probe'] == [12, 0, 0, 9] and F[u'v_slowstart'] == [2, 0, 0, 15]

    assert F[u'cat_std'] == [0, 1, 1, 1] and F[u'cat_exp'] == F[u'cat_info'] == F[u'cat_hist'] == [0] * 4
    assert F[u'std_lvl'] == [0, 9, 13, 2]
    assert F[u'obs_hdr'] == [0, 0, 1, 0] and F[u'upd_hdr'] == [0, 0, 1, 0]
    assert F[u'obsoleted_by'] == [0] * 4 and F[u'errata'] == [0, 0, 1, 1] and F[u'issn_hdr'] == [0, 0, 1, 1]
    assert F[u'req_rc'] == [1] * 4 and F[u'rfc_hdr'] == [0] * 4
    assert F[u'cite_2988'] == [0, 7, 4, 0] and F[u'cite_6298'] == [0, 0, 10, 8]
    assert F[u'cite_793'] == [0, 1, 1, 0] and F[u'cite_1123'] == F[u'cite_9002'] == [0] * 4
    assert F[u'cite_1122_sp'] == [0, 5, 4, 0] and F[u'cite_1122_ns'] == [115, 0, 0, 0]
    assert F[u'cite_1122'] == [F[u'cite_1122_sp'][i] + F[u'cite_1122_ns'][i] for i in range(4)] == [115, 5, 4, 0]
    assert F[u'cite_ns_1122'] == F[u'cite_1122']
    assert F[u'y_cite_ledger_1122'] == [0] * 4
    assert F[u'a_self_lit'] == 116 and F[u'a_shell_1122_sp'] == 1 and F[u'a_1122_resid'] == 116 - 115 - 1 == 0
    assert F[u'num_lines'] == [8, 27, 54, 81] and F[u'lit_jaco'] == [13, 3, 4, 0]

    assert F[u'share_ab'] == F[u'share_ac'] == F[u'share_ad'] == 0
    assert F[u'share_bc'] == 95 and F[u'share_bd'] == 1 and F[u'share_cd'] == 13
    assert F[u'share_bc_plus'] == 1 and F[u'ABC_inter'] == 0 and F[u'BC_inter'] == 95
    assert F[u'y_bc_byte_shared'] == 84 and F[u'y_bc_norm_only'] == F[u'share_bc'] - F[u'y_bc_byte_shared'] == 11
    assert F[u'only_b'] == 72 and F[u'only_c'] == 128 and F[u'only_d'] == 888
    assert F[u'y_only_bcd'] == F[u'only_b'] + F[u'only_c'] + F[u'only_d'] == 1088
    assert F[u'union_abc'] == 2838 and F[u'union_abcd'] == 3726 and F[u'union_delta'] == 888
    assert F[u'union_abcd'] == F[u'union_abc'] + F[u'only_d'] == 3726
    assert F[u'abcd_incl'] == F[u'union_abcd']
    assert F[u'abcd_close'] == F[u'abcd_incl'] - F[u'union_abcd'] == 0
    assert F[u'shell_delta'] == [0, 1, 1, 0]
    assert F[u'union_abc_nos'] == 2836 and F[u'union_abcd_nos'] == 3724
    assert F[u'pool_n'] == 6248 and F[u'pool_tiers'] == [5758, 399, 35, 56]
    assert F[u'pool_1'] + F[u'pool_2'] + F[u'pool_3'] + F[u'pool_4'] == F[u'pool_n']
    assert F[u'pool_close'] == 0 and sum(F[u'pool_tiers']) == F[u'pool_n']
    assert F[u'pool_tag_n'] == [4189, 235, 343, 1481] and sum(F[u'pool_tag_n']) == F[u'pool_n']
    assert F[u'pool_maxlen'] == 73
    assert F[u'scalar_clos_n'] == 15 and F[u'list_clos_n'] == 4
    assert F[u'scalar_clos_sum'] == 0 and F[u'x_ident_n'] == 30

    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B63_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6([' + u''.join(TAGS) + u'])\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B63: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B63: 有锚没带源标签'
    ERR = [x for x in CITES if not pnorm(x[1]) or pnorm(x[1]) not in FAN[IDX[x[0]]]]
    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [tuple(i for i in range(NSRC) if pnorm(a) and pnorm(a) in FAN[i]) for a in DIS]
    F[u'anchor_total'] = len(CITES)
    F[u'anchor_distinct'] = len(DIS)
    F[u'anchor_err'] = len(ERR)
    F[u'anchor_single'] = len([h for h in HC if len(h) == 1])
    F[u'anchor_cross'] = len([h for h in HC if 1 < len(h) < NSRC])
    F[u'anchor_all4'] = len([h for h in HC if len(h) == NSRC])
    F[u'checks'] = len(DIS) * NSRC
    for t in TAGS:
        F[u'tag_' + t] = len(re.findall(u'\\u27e6%s\\u27e7' % t, enc))
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all4'] == len(DIS)
    assert all(F[u'tag_' + t] > 0 for t in TAGS), u'有四源标签没锚'
    assert F[u'anchor_all4'] == 0, u'B63: 没有一条锚在四份里逐字再现'
    return F

_B63 = _b63_scan()
B63V = lambda k, i=None: (_B63[k] if i is None else _B63[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b63 block>', 'exec')

assert S.count(NL + u'_B62 = _b62_scan()') == 1, u'anchor _b62_scan'
B63ENV = u'B62V=B62V,' + NL + u'               B63V=B63V)'
i0 = S.find(u'# B63: 还没有 RTT 样本时第一个重传超时设多久')
while i0 >= 0:
    i1 = S.index(u'_B62 = _b62_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B63: 还没有 RTT 样本时第一个重传超时设多久')
if B63ENV in S:
    S = S.replace(B63ENV, u'B62V=B62V)')
S = S.replace(NL + u'_B62 = _b62_scan()', BLK + NL + u'_B62 = _b62_scan()')
assert S.count(u'B62V=B62V)') == 1, u'anchor env'
S = S.replace(u'B62V=B62V)', B63ENV)

PS = u"SRC['B61'] = ["
blk = (u"SRC['B63'] = ['corpus/raw/tcpRTO/rfc1122.txt', 'corpus/raw/tcpRTO/rfc2988.txt', "
       u"'corpus/raw/tcpRTO/rfc6298.txt', 'corpus/raw/tcpiw/rfc9002.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B61', 'B62'}", u"'B61', 'B62', 'B63'}"
# 只加进 ATOM(锚比对集), 不加进 HTMLSRC——四份都是纯文本面, 没有壳⇎面两口径
if NEW not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B63'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B63'" + S[m.end(1):]

M1 = u'# ---- B63 DERIV (generated by corpus/_wire63.py from corpus/_deriv63.json; do not hand-edit) ----'
M2 = u'# ---- /B63 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B60'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv63.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B63'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B63': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b63 block>', 'exec'), NS)
env = NS['B63V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b63flat.json', encoding='utf-8'))


def deep(x):
    return [deep(y) for y in x] if isinstance(x, list) else list(x) if isinstance(x, tuple) else x


for k, v in FLAT.items():
    if k == u'sig_sha256_16':
        continue  # 采集侧声明的另一种签名档, 建条目侧不量
    try:
        got = env(k)
    except Exception as e:
        BAD.append((k, repr(e)))
        continue
    if deep(got) != deep(v):
        MISMATCH.append((k, v, got))
assert not BAD, BAD[:6]
assert not MISMATCH, MISMATCH[:6]
for kk, v in J.items():
    try:
        got = eval(v, dict(NS), {'B63V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b62_scan' in S and u'_b63_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b63_scan+B63V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values()),
         env('anchor_total'), env('anchor_distinct'), env('checks')))
