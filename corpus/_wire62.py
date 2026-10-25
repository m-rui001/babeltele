# -*- coding: utf-8 -*-
"""把 B62 的独立复算器(_b62_scan / B62V)接进 audit.py, 并生成 DERIV['B62']。
幂等: 重复运行先摘旧块再插新块。
_b62_scan 的量测段从 corpus/_mkB62.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自五处:
①采集侧 corpus/_pick62.py 是先于建条目写好的另一套实现(它用 re.findall 与前后瞻数方程族、
  用集合运算求搬运交集、按 (\\d+) 类抽阈值成对读数、以 set & 算三源共行),
  两边在 264 个口径一致的键上逐量对账(五份都是纯文本面, 无需按介质分流; 现况 264／不符 0,
  采集侧独有的 37 键是它自己的正则族与前后瞻档, 建条目侧改立 n_/s_ 口径, 不共用键名);
②抽出的代码在插门之前要把 _b62flat.json 的每个键与 DERIV['B62'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 五源一律按归一串判成员;
④方程族的可判性与第一遍不同: 建条目侧把 min (C*VAR, max (K*VAR, B)) 当结构解析(游标 find 循环 +
  逐字符判邻, 两个系数与常数帽分开解出), 而非数正则命中; 数字读数一律从面内现读(IW 行的倍数、
  If 行的阈值、"ten"/"twice" 这类英文数词), 手填常数为零;
⑤档位表的方向(倍数沿档升、阈值沿档降)与表两端各自算回同一枚常数帽, 都是门可复算的量, 不是注释里的解释。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB62.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/tcpiw/rfc2581.txt', u'corpus/raw/tcpiw/rfc3390.txt', u'corpus/raw/tcpiw/rfc5681.txt',
        u'corpus/raw/tcpiw/rfc6928.txt', u'corpus/raw/tcpiw/rfc9002.txt']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'# --- SCAN BEGIN ---', u'# --- SCAN END ---')
MEAS = MEAS[MEAS.index(NL) + 1:]
assert u'F[u' in MEAS and u'POOL' in MEAS and u'EQS' in MEAS and u'abc_close' in MEAS
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
assert u'FAN' in MEAS and u'ATOMSEL' in MEAS and u'pnorm' in MEAS
assert u'x_c_iw_mult' in MEAS and u'num_after' in MEAS and u'word_before' in MEAS

HEAD = u'''
# B62: 新建连接在第一个 RTT 里允许立刻发出多少字节——五份 RFC Editor 纯文本五种答法:
# raw/tcpiw/rfc2581.txt(A 99 两段: 现行上限 2 段, 把 IW = min (4*SMSS, max (2*SMSS, 4380 bytes)) 引作"非标准的实验性扩展",
#   方程之后第 4 行落刀 "We do NOT allow this change as part of the standard"; 4380 字面 2 处)
# ⇎ rfc3390.txt(B 02 方程: 同一枚方程(同带标号 (1))升为标准上限, 变量名 SMSS→MSS, 只差 1 个字母,
#   并自己给出 1460×3=4380 的桥; 阈值档 [1095],[1095,2190],[2190])
# ⇎ rfc5681.txt(C 09 三段表: 保留 1095⇎2190 两枚阈值, 中间档换成随 SMSS 增长的 IW = 3*SMSS, 整篇 4380 字面 0 处,
#   唯一的 min ( 与初窗无关; 表内倍数沿档 2→3→4 而阈值 2190→1095, 方向相反)
# ⇎ rfc6928.txt(D 13 十倍, Experimental: min (10*MSS, max (2*MSS, 14600)) 且自称 patterned after RFC 3390;
#   14600 只以裸写出现 2 处)
# ⇎ rfc9002.txt(E 21 QUIC: 换掉计量单位, 通篇 MSS 字样 0 处, 改说 ten times the maximum datagram size,
#   以 the larger of ... 14,720 封顶, 并用 8 字节 UDP ⇎ 20 字节 TCP 头差搭桥; 唯一非分页、带 BOM 的一份)。
# 本函数从五份字节独立复算: 方程结构解析(外层系数⇎内层系数⇎常数帽, 逐字符游标), 面内现读的阈值/倍数/段数/英文数词,
# 规范句整行最后一处命中 ⇎ 回溯编号标题 ⇎ 前推到异号下一标题的两窗划分与窗内窗外相加闭合,
# 字面出现处⇎独立数 token⇎子串档相减, 原面逐字面⇎整篇空白折平两档之差, 页眉抬词频⇎集合去重两口径分别立键,
# 义务词全大写⇎小写两档、引用网(2581⇎3390⇎5681⇎6928⇎9002 各被谁引)、锚候选池按逐字再现份数五层划分与锚归属由正文现推、
# 三源⇎四源⇎五源共行容斥。19 条面内读数恒等式(4380=1460×3、14600=1460×10、14720=14600+10×(20−8)、
# 6570−2190=4380、09 表两端各算回 4380、每档段数上限=同档倍数)全归零送门槛重算。
# 不可由在库文件判定的: 五份的抓取时刻与磁盘 mtime 谁新谁旧、rfc-editor.org 此刻的现行状态页、
# 勘误表是否已挂新版、库外流传的 RFC 5681 表序与这份面内表序谁对——只进解读注, 不进门槛。
def _b62_scan():
    import hashlib as _hl
    import os as _os
    P2 = SRC['B62']
    NSRC = 5
    TAGS = [u'A', u'B', u'C', u'D', u'E']
    LB = dict(zip(TAGS, [u'99 两段', u'02 方程', u'09 三段表', u'13 十倍', u'21 QUIC']))
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
    # ---- 结构性自检: 五答、两窗划分、方程解析、表与阈值方向、折行双档、义务词两档、搬运容斥 ----
    assert F[u'bytes'] == [31351, 36177, 44339, 56523, 89071] and F[u'sig_distinct'] == 5
    assert len(set(F[u'sig'])) == 5 and F[u'chars'] == [31351, 36177, 44339, 56523, 89053]
    assert F[u'x_bom_bytes'] == F[u'bytes'][4] - F[u'chars'][4] == 18
    assert F[u'bom'] == [0, 0, 0, 0, 1] and F[u'nonascii'] == [0, 0, 0, 0, 8]
    assert F[u'chars_split'] == F[u'chars'] and F[u'chars_no_nl'] == [30564, 35334, 43328, 55176, 86983]
    assert F[u'lines'] == [788, 844, 1012, 1348, 2071] and F[u'lines_nl'] == F[u'lines']
    assert F[u'nonblank'] == [508, 575, 707, 901, 1635] and F[u'maxlen'] == [72] * 5
    assert F[u'rec_close'] == [0] * 5 and F[u'cr'] == [0] * 5
    assert F[u'hdr'] == [13, 14, 17, 23, 0] and F[u'foot'] == [14, 15, 18, 24, 0]
    assert F[u'foot_brk'] == F[u'foot'] and F[u'foot_old'] == [0] * 5
    assert F[u'trail'] == F[u'foot'] and F[u'trail_is_foot'] == [0] * 5
    assert F[u'pagelines'] == [27, 29, 35, 47, 0] and F[u'pagelines'][4] == 0
    assert F[u'lines_ge40'] == [366, 429, 512, 626, 901] and F[u'shell_delta'] == [0, 1, 1, 1, 0]
    assert F[u'lines_ge40_nos'] == [F[u'lines_ge40'][i] - F[u'shell_delta'][i] for i in range(5)]

    assert F[u'x_eq_n'] == [1, 1, 0, 1, 0] and F[u'x_eq_coef'] == [4, 4, 0, 10, 0]
    assert F[u'x_eq_inner'] == [2, 2, 0, 2, 0] and F[u'x_eq_cap'] == [4380, 4380, 0, 14600, 0]
    assert F[u'x_eq_var'] == [u'SMSS', u'MSS', u'', u'MSS', u''] and F[u'x_eq_varlen'] == [4, 3, 0, 3, 0]
    assert F[u'x_ab_var_diff'] == F[u'x_eq_varlen'][0] - F[u'x_eq_varlen'][1] == 1
    assert F[u'x_coef_ratio'] == [200, 200, 0, 500, 0]
    assert F[u'x_eq_close'] == [F[u'lit_minp'][i] - F[u'x_eq_n'][i] for i in range(5)] == [0, 0, 1, 0, 0]
    assert F[u'lit_minp'] == [1, 1, 1, 1, 0] and F[u'lit_maxp'] == [2, 1, 1, 1, 0]
    assert F[u'lit_p1'] == [3, 7, 0, 4, 0] and F[u'n_min4'] == [1, 1, 0, 0, 0] and F[u'n_min10'] == [0, 0, 0, 1, 0]

    assert F[u'sec_a'] == [141, 45, 206, 183, 910] and F[u'sec_b'] == [185, 121, 418, 251, 938]
    assert [list(x) for x in F[u'sec_w']] == [[F[u'sec_a'][i], F[u'sec_b'][i]] for i in range(5)]
    assert F[u'sec_len'] == [1865, 3219, 9448, 3283, 1468] and F[u'sec_hit'] == [1, 1, 1, 1, 2]
    assert F[u'sec_num'] == [u'3..1', u'1', u'3..1', u'2', u'7..2']
    for k in (u'4380', u'2190', u'1095', u'14600', u'c14720', u'minp', u'maxp'):
        assert F[u'lit_' + k] == [F[u'secw_' + k][i] + F[u'outw_' + k][i] for i in range(5)], k
    assert F[u'secw_4380'] == [1, 3, 0, 0, 0] and F[u'outw_4380'] == [1, 1, 0, 0, 0]
    assert F[u'secw_1095'] == F[u'lit_1095'] and F[u'outw_1095'] == [0] * 5
    assert F[u'secw_2190'] == F[u'lit_2190'] and F[u'outw_2190'] == [0] * 5
    assert F[u'secw_14600'] == [0, 0, 0, 1, 0] and F[u'secw_c14720'] == [0, 0, 0, 0, 1]

    assert F[u'x_b_if'] == [[1095], [1095, 2190], [2190]] and F[u'x_c_if'] == [[2190], [1095, 2190], [1095]]
    assert F[u'x_b_if_n'] == F[u'x_c_if_n'] == F[u'x_b_tiers_n'] == F[u'x_c_tiers_n'] == 3
    assert F[u'x_c_iw_mult'] == [2, 3, 4] and F[u'x_c_seg_cap'] == [2, 3, 4]
    assert F[u'x_c_seg_gap'] == 0 and F[u'x_c_mult_delta'] == 2 and F[u'x_c_bound_delta'] == -1095
    assert F[u'x_c_dir_opp'] == 1 and (F[u'x_c_mult_delta'] > 0) != (F[u'x_c_bound_delta'] > 0)
    assert F[u'x_c_hi_mult'] == F[u'x_c_iw_mult'][0] == 2 and F[u'x_c_mid_mult'] == 3
    assert F[u'x_b_hi_bound'] == F[u'x_c_hi_bound'] == 2190 and F[u'x_thresh_close'] == 0
    assert F[u'x_b_lo_bound'] == F[u'x_c_lo_bound'] == 1095 and F[u'x_lo_close'] == 0
    assert F[u'x_c_mid_ub'] == 2190 and F[u'x_c_mid_ub_close'] == 0
    assert F[u'x_c_top_at_hi'] == F[u'x_c_lo_at_lo'] == 4380 and F[u'x_c_span_close'] == 0
    assert F[u'x_c_cap_close'] == F[u'x_c_top_at_hi'] - F[u'x_eq_cap'][1] == 0
    assert F[u'x_b_at_hi'] == 4380 and F[u'x_c_upper_at2190'] == 6570 and F[u'x_widen'] == 2190
    assert F[u'x_at1460_b'] == F[u'x_at1460_c'] == 4380 and F[u'x_at1460_close'] == 0
    assert F[u'x_b_strict'] == 1 and F[u'x_c_le'] == 2 and F[u'x_c_upper_lt'] == 1
    assert F[u'lit_4380'] == [2, 4, 0, 0, 0] and F[u'lit_2smss'] == [4, 0, 2, 0, 0]
    assert F[u'tier_const_cap'] == [0, 1, 0, 0, 0] and F[u'tier_grow_cap'] == [0, 0, 1, 0, 0]
    assert F[u'tier_lesscap'] == [1, 0, 0, 0, 0] and F[u'tier_norm_same'] == 0
    assert F[u'tier_ifparen'] == [0, 1, 0, 0, 0] and F[u'tier_ifsmsq'] == F[u'tier_ifsmss'] == [0, 0, 1, 0, 0]

    assert F[u'x_b_mssnum'] == 1460 and F[u'x_b_pkgnum'] == 1500 and F[u'x_b_three'] == 3 and F[u'x_b_close'] == 0
    assert F[u'x_d_ten'] == 10 and F[u'x_d_close'] == 0 and F[u'x_eq_cap'][3] == 14600
    assert F[u'x_e_capnum'] == 14720 and F[u'x_e_bridge'] == 120 and F[u'x_e_ovh'] == 12
    assert F[u'x_e_seg'] == F[u'x_e_ten'] == 10 and F[u'x_e_close'] == 0
    assert F[u'x_e_ovhnum'] == 8 and F[u'x_e_ovhtcp'] == 20 and F[u'x_e_twice'] == 2
    assert F[u'x_e_tenword'] == u'ten' and F[u'x_e_twiceword'] == u'twice'
    assert F[u'x_e_break'] == 7360 and F[u'x_e_break_close'] == 0 and F[u'x_e_binds'] == 1
    assert F[u'x_e_floornum'] == 1200 and F[u'x_e_iw'] == 12000 and F[u'x_e_twice_at_floor'] == 2400
    assert F[u'x_a_gap'] == 4 and F[u'x_a_order'] == 1 and F[u'n_dont_allow'] == [1, 0, 0, 0, 0]
    assert F[u'n_skel'] == [0, 1, 0, 1, 0] and F[u'x_skel_cite'] == [u'', u'2581', u'', u'3390', u'']
    assert F[u'x_b_after'] == 23 and F[u'x_d_after'] == 2 and F[u'x_after_spread'] == 21

    assert F[u'lit_14600'] == [0, 0, 0, 2, 0] and F[u'lit_c14600'] == [0] * 5
    assert F[u'bare_only_14600'] == [F[u'lit_14600'][i] - F[u'lit_c14600'][i] for i in range(5)] == [0, 0, 0, 2, 0]
    assert F[u'lit_c14720'] == [0, 0, 0, 0, 1] and F[u'lit_14720'] == [0] * 5
    assert F[u'comma_only_14720'] == [0, 0, 0, 0, 1]
    assert F[u'subgap_14600'] == [0] * 5 and F[u'subgap_14720'] == [0] * 5
    assert F[u'lit_1460'] == [0, 2, 0, 2, 0] and F[u'tok_1460'] == [0, 2, 0, 0, 0] and F[u'subgap_1460'][3] == 2
    assert F[u'numband_n_a'] == 27 and F[u'numband_n_b'] == 38 and F[u'numband_n_c'] == 42
    assert F[u'numband_n_d'] == 37 and F[u'numband_n_e'] == 39
    assert F[u'nb_lo'] == F[u'x_c_lo_bound'] == 1095 and F[u'nb_hi'] == F[u'x_e_capnum'] == 14720
    assert F[u'lit_4k'] == [0, 6, 0, 0, 0] and F[u'lit_333'] == [0, 0, 0, 0, 2] and F[u'lit_1200'] == [0, 0, 0, 0, 2]
    assert F[u'num_lines'] == [24, 9, 32, 50, 1]

    assert F[u'wrap_pin_n'] == 15 and F[u'wrap_pin_hit'] == 1 and F[u'wrap_gap_total'] == 2
    assert F[u's_seg10'] == [0, 0, 0, 12, 0] and F[u's_seg10_fold'] == [0, 0, 0, 14, 0]
    assert F[u'wrap_gap_seg10'] == [0, 0, 0, 2, 0]
    for k in (u'min4', u'min10', u'cap4380', u'cap14600', u's4smss', u's4mss', u'dont_allow', u'large_of',
              u'udp8', u'tcp20', u'ten_times', u'iw_of', u'two_smss', u'skel'):
        assert F[u'wrap_gap_' + k] == [0] * 5, k
    assert F[u's_two_smss'] == F[u'lit_2smss'] and F[u's_min4'] == F[u'n_min4']
    assert F[u'w_iw_word'] == [4, 111, 7, 111, 1] and F[u'iw_word_nos'] == [4, 97, 7, 88, 1]
    assert F[u'hdr_title'] == [0, 14, 0, 23, 0] and F[u'iw_word_gap'] == F[u'hdr_title']

    assert F[u'u_must'] == [21, 3, 34, 5, 35] and F[u'u_should'] == [16, 4, 23, 7, 27]
    assert F[u'u_may'] == [4, 3, 6, 3, 21] and F[u'u_must_not'] == [9, 1, 16, 2, 9]
    assert F[u'oblig_up'] == [41, 10, 63, 15, 83] and F[u'x_oblig_spread'] == F[u'oblig_up'][4] - F[u'oblig_up'][1] == 73
    assert F[u'l_must'] == [2, 2, 2, 3, 2] and F[u'l_should'] == [7, 5, 7, 5, 4] and F[u'l_may'] == [12, 5, 16, 22, 14]
    assert F[u'oblig_low'] == [21, 12, 25, 30, 20]
    assert F[u'u_required'] == [1] * 5 and F[u'u_should_not'] == [1, 1, 1, 1, 7]
    assert F[u'key_words_boiler'] == [2] * 5 and F[u'rfc2119_ref'] == [1, 4, 3, 4, 6]
    assert F[u'w_mustnot_seg'] == [1, 0, 3, 0, 0]

    assert F[u'v_mss'] == [26, 15, 41, 7, 0] and F[u'v_smss'] == [16, 0, 30, 0, 0]
    assert F[u'v_mds'] == [0, 0, 0, 0, 4] and F[u'v_datagram'] == [0, 0, 0, 0, 22]
    assert F[u'v_iw'] == [8, 0, 10, 58, 0] and F[u'v_cwnd'] == [39, 4, 62, 2, 0]
    assert F[u'v_icw'] == [1, 1, 3, 3, 2] and F[u'v_seg_word'] == [68, 117, 81, 39, 4]
    assert F[u'v_slow_start'] == [13, 3, 16, 3, 15] and F[u'v_slowstart_flat'] == [0] * 5
    assert F[u'v_slowstart_hy'] == [1, 0, 1, 0, 0] and F[u'x_seg_small'] == [2, 0, 3, 2, 0]

    assert F[u'cite_2581'] == [13, 5, 15, 0, 0] and F[u'cite_3390'] == [0, 14, 6, 17, 0]
    assert F[u'cite_5681'] == [0, 0, 17, 7, 11] and F[u'cite_6928'] == [0, 0, 0, 23, 4]
    assert F[u'cite_9002'] == [0] * 5 and F[u'cite_6298'] == [0, 0, 0, 7, 8]
    assert F[u'cite_1122'] == [1, 4, 7, 0, 0] and F[u'cite_2001'] == [3, 0, 10, 0, 0]
    assert F[u'cite_2414'] == [1, 4, 3, 3, 0] and F[u'cite_2988'] == [0, 6, 3, 0, 0]
    assert F[u'cat_std'] == [1, 1, 1, 0, 1] and F[u'cat_exp'] == [0, 0, 0, 1, 0]
    assert F[u'cat_info'] == F[u'cat_hist'] == [0] * 5
    assert F[u'obs_hdr'] == [1, 1, 1, 0, 0] and F[u'upd_hdr'] == [0, 1, 0, 0, 0]
    assert F[u'obsoleted_by'] == [0] * 5 and F[u'errata'] == [0, 0, 0, 1, 1] and F[u'issn_hdr'] == [0, 0, 0, 1, 1]

    assert F[u'share_ab'] == 29 and F[u'share_ac'] == 190 and F[u'share_ad'] == 3 and F[u'share_ae'] == 1
    assert F[u'share_bc'] == 14 and F[u'share_bd'] == 29 and F[u'share_be'] == 2
    assert F[u'share_cd'] == 11 and F[u'share_ce'] == 5 and F[u'share_de'] == 14
    assert F[u'share_bc_plus'] == 4 and F[u'ABC_inter'] == 9 and F[u'only_c'] == 311
    assert F[u'only_d'] == 590 and F[u'only_e'] == 886 and F[u'union_abc'] == 1083 and F[u'abc_incl'] == 1083
    assert F[u'abc_incl'] == (F[u'lines_ge40'][0] + F[u'lines_ge40'][1] + F[u'lines_ge40'][2]
                              - F[u'share_ab'] - F[u'share_ac'] - F[u'share_bc']
                              + F[u'ABC_inter']) == F[u'union_abc'] == 1083
    assert F[u'abc_close'] == F[u'abc_incl'] - F[u'union_abc'] == 0
    assert F[u'abc_close_nos'] == 0 and F[u'union_abc_nos'] == 1081
    assert F[u'union_abcd'] == 1673 and F[u'union_abcde'] == 2559 and F[u'union_delta'] == 886
    assert F[u'pool_n'] == 3941 and F[u'pool_tiers'] == [3010, 760, 127, 21, 23]
    assert F[u'pool_close'] == 0 and sum(F[u'pool_tiers']) == F[u'pool_n']
    assert F[u'pool_tag_n'] == [460, 530, 653, 818, 1480] and sum(F[u'pool_tag_n']) == F[u'pool_n']
    assert F[u'pool_maxlen'] == 72 and F[u'scalar_clos_n'] == 13 and F[u'list_clos_n'] == 2
    assert F[u'scalar_clos_sum'] == 0 and F[u'x_ident_n'] == 19

    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 五源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B62_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B62: 正文里没有带标签的锚'
    assert len(re.findall(u'⟨', enc)) == len(CITES), u'B62: 有锚没带源标签'
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
    F[u'anchor_all5'] = len([h for h in HC if len(h) == NSRC])
    F[u'checks'] = len(DIS) * NSRC
    for t in TAGS:
        F[u'tag_' + t] = len(re.findall(u'⟦%s⟧' % t, enc))
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all5'] == len(DIS)
    assert all(F[u'tag_' + t] > 0 for t in TAGS), u'有五源标签没锚'
    return F

_B62 = _b62_scan()
B62V = lambda k, i=None: (_B62[k] if i is None else _B62[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b62 block>', 'exec')

assert S.count(NL + u'_B61 = _b61_scan()') == 1, u'anchor _b61_scan'
B62ENV = u'B61V=B61V,' + NL + u'               B62V=B62V)'
i0 = S.find(u'# B62: 新建连接在第一个 RTT 里允许立刻发出多少字节')
while i0 >= 0:
    i1 = S.index(u'_B61 = _b61_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B62: 新建连接在第一个 RTT 里允许立刻发出多少字节')
if B62ENV in S:
    S = S.replace(B62ENV, u'B61V=B61V)')
S = S.replace(NL + u'_B61 = _b61_scan()', BLK + NL + u'_B61 = _b61_scan()')
assert S.count(u'B61V=B61V)') == 1, u'anchor env'
S = S.replace(u'B61V=B61V)', B62ENV)

PS = u"SRC['B61'] = ["
blk = (u"SRC['B62'] = ['corpus/raw/tcpiw/rfc2581.txt', 'corpus/raw/tcpiw/rfc3390.txt', "
       u"'corpus/raw/tcpiw/rfc5681.txt', 'corpus/raw/tcpiw/rfc6928.txt', 'corpus/raw/tcpiw/rfc9002.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B60', 'B61'}", u"'B60', 'B61', 'B62'}"
# 只加进 ATOM(锚比对集), 不加进 HTMLSRC——五份都是纯文本面, 没有壳⇎面两口径
if NEW not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B62'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B62'" + S[m.end(1):]

M1 = u'# ---- B62 DERIV (generated by corpus/_wire62.py from corpus/_deriv62.json; do not hand-edit) ----'
M2 = u'# ---- /B62 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B60'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv62.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B62'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B62': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b62 block>', 'exec'), NS)
env = NS['B62V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b62flat.json', encoding='utf-8'))


def deep(x):
    return [deep(y) for y in x] if isinstance(x, list) else list(x) if isinstance(x, tuple) else x


for k, v in FLAT.items():
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
        got = eval(v, dict(NS), {'B62V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b61_scan' in S and u'_b62_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b62_scan+B62V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values()),
         env('anchor_total'), env('anchor_distinct'), env('checks')))
