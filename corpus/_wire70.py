# -*- coding: utf-8 -*-
"""把 B70 的独立复算器(_b70_scan / B70V)接进 audit.py, 并生成 DERIV['B70']。
幂等: 重复运行先摘旧块再插新块; 只动 B70 自己的区域, 并行 agent 的 B65/B67/B69 行段原样保留。
_b70_scan 的量测段从 corpus/_mkB70.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间 ⇎
corpus/_mk70emit.py 的 SCAN2 BEGIN ⇎ SCAN2 END 之间逐行机械抽出, 只在头部换成 audit 自己的
路径常量与模块别名; 真正的独立性来自六处:
①采集侧 corpus/_pick70.py 是先于建条目写好的另一套实现(str.count/逐行 in 收针), 建条目侧改立
  游标逐字符档、正则档、集合代数档与 itertools 配对档, 两边在口径一致的键上逐量对账;
②抽出的代码在插门之前要把 _b70flat.json 的每个键与 DERIV['B70'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按归一串判成员;
④数字读数一律从面内现读: 65535 的十进制⇎十六进制两条游标、16/128/32 三枚位宽、6935 里
  "requirements 9, 10, and 11" 的两枚下标、四个标题页年份与相邻年距都由句内游标解析, 一个不手填;
  段落起止行由折平偏移映回原行号;
⑤语气这一维是三轨的: 大写档 ⇎ 小写档 ⇎ 首字母大写档之和必须等于不分大小写档(1122 面上大写 May 是月份),
  同一枚 IPv6 规则在 8200 与 6935 里的差别要能逐词算出来(共尾 ⇎ 共头 ⇎ 独有词 ⇎ 逗号 ⇎ 义务词枚数),
  而 23 枚针只在折平面存在、8200 的答句整段被行界劈开——这类差只能由复算给出;
⑥谁改谁 ⇎ 谁引谁也是量出来的: Obsoletes: ⇎ Updates: 两头的对象并集一枚, 6935 面上"该删"指令一次,
  8200 面上零次; 互引方向单向; 长行池两两交=逐字节交+仅归一, 唯一那条只归一同形的正是 FFFF 句。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB70.py', encoding='utf-8').read()
EM = io.open(u'corpus/_mk70emit.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/udpCK/rfc768.txt', u'corpus/raw/tcpRTO/rfc1122.txt',
        u'corpus/raw/udpCK/rfc8200.txt', u'corpus/raw/udpCK/rfc6935.txt']


def cut(src, a, b):
    i = src.index(a)
    j = src.index(b, i)
    return src[i:j]


MEAS = cut(MK, u'# --- SCAN BEGIN ---', u'# --- SCAN END ---')
MEAS = MEAS[MEAS.index(NL) + 1:]
MEAS2 = cut(EM, u'# --- SCAN2 BEGIN ---', u'# --- SCAN2 END ---')
MEAS2 = MEAS2[MEAS2.index(NL) + 1:]
MEAS = MEAS.rstrip() + NL + NL + MEAS2.rstrip() + NL
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
for nm in (u'pnorm', u'cnt_cur', u'read_after', u'sec_window', u'HEADND', u'POOLC', u'NPOOL', u'ZID',
           u'CLOSE', u'FOLD', u'FO', u'SH', u'NEEDLE', u'GN', u'GR', u'CNT', u'SN', u'SNF', u'SNS',
           u'NUM', u'win_close_sum', u'up_ledger', u'utf8_extra', u'ub', u'hdr_year', u'hdr_ids',
           u'blk', u'fmap', u'line_of', u'tone_rev_close', u'n_', u'num_'):
    assert nm in MEAS, nm

HEAD = u'''
# B70: 一条 UDP 报文的校验和到底是不是非算不可——四份一手 UDP/IPv6 文书四种答法:
# raw/udpCK/rfc768.txt(A 768/1980: 零值只写成 "a checksum value means that the transmitter generated no
#   checksum"(没算), 全篇大写义务词零枚——它早于 RFC 2119 的语气表; optional 一词只贴在 Source Port;
#   算出零就发 all ones 而不给任何进制, 校验和字段位数 16 写在图注里)
# ⇎ raw/tcpRTO/rfc1122.txt(B 1122/1989: 同一件事拆成三层——能力上 "A host MUST implement the facility" ⇎
#   每报文 "An application MAY optionally be able to control whether UDP" ⇎ "MUST default to checksumming on",
#   同一节 28 行之后又写 the UDP checksum is optional, 接收侧留给应用, 承认 turning off 有争议,
#   同段还把 TCP 的校验和写成 never optional; 零值只给十进制 65535)
# ⇎ raw/udpCK/rfc8200.txt(C 8200/2017, STD: "the default behavior ... is not optional" 却全篇 0 枚大写义务词 ⇎
#   小写 must 52 枚, 零值改写成 hex FFFF, 伪头地址 128 位 ⇎ IPv4 32 位, 隧道零校验的口留给 6936)
# ⇎ raw/udpCK/rfc6935.txt(D 6935/2013: 把旧原文整段引出并判它 fourth bullet should be deleted, 再换成大写义务
#   4 枚、插入 by default、出口写成 MAY enable zero-checksum mode; 动作头 Updates: 与 8200 的 Obsoletes:
#   指向同一枚 2460, 而 6935 面上不引 8200——被更新的那份反而更新得晚四年)。
# 本函数从四份字节独立复算: 同一枚补码值的两条进制游标(十进制 ⇎ hex, 全落空一份), 位宽三枚与两枚比值,
# 三档口径阶梯的在册答句针(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 正则轨)与折行独有针, 义务语气三轨互咬
# (大写 ⇎ 小写 ⇎ 首字母大写 = 不分大小写), optional 一词的邻接轨(全篇 ⇎ 与 checksum 同行 ⇎ 前词档 ⇎ 行距),
# 8200 ⇎ 6935 同一条规则的逐词账(段界映回原行 ⇎ 共有词 ⇎ 独有词 ⇎ 共尾 ⇎ 共头 ⇎ 逗号 ⇎ 语气换向),
# 头部动作字段与标题页年份(行尾锚定, 排序索引 ⇎ 倒序数 ⇎ 年距), 引用三式(空格 ⇎ 短横 ⇎ 连写)与互引方向,
# 答句邻域窗(±20 行)内外五轨对账, 长行池两两交的逐字节 ⇎ 仅归一分裂 ⇎ 写法分家四桶, 编码层全零。
# 恒等式(进制读数三枚一致 ⇎ 位宽比整除 ⇎ 大写+小写+首字母=不分大小写 ⇎ 词集独有+共有=全集 ⇎
# 反向语气三项之和 ⇎ 目标号并集唯一 ⇎ 引用三式相加=正则族 ⇎ 带内+带外=全篇五轨 ⇎ Σ单份−Σ两两+Σ三三−Σ四份=并集 ⇎
# 归一交=逐字节交+仅归一 ⇎ 分档之和=池条数 ⇎ 锚按标签账=按份数账)全归零送门槛重算。
# 不可由在库文件判定的: 四份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# RFC 2460/4443 本身(不在库内)、此后哪份文档又动了这段、现网实现实际丢不丢零校验报文——只进解读注, 不进门槛。
def _b70_scan():
    import io, re, itertools, hashlib as _hl
    from collections import Counter, defaultdict
    P2 = SRC['B70']
    NSRC = 4
    LBL = [u'768', u'1122', u'8200', u'6935']
    TAGS = LBL
    YR = [u'80', u'89', u'17', u'13']
    PATH = P2
    NL = chr(10)
    F = {}
    DER = {}
    LITK = {}
    IDX = dict((t, n) for n, t in enumerate(LBL))

    def _dv(x):
        if isinstance(x, tuple):
            return [_dv(y) for y in x]
        if isinstance(x, list):
            return [_dv(y) for y in x]
        if isinstance(x, dict):
            return dict((k, _dv(v)) for k, v in x.items())
        return x
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
BODYTXT = re.sub(u'(?<![.\\w])hashlib\\.', u'_hl.', BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
BODYTXT = BODYTXT.replace(u'print(', u'_sil(')
EVSRC = u"eval(e.strip().replace(u'\\n', u''))"
assert BODYTXT.count(EVSRC) == 2, BODYTXT.count(EVSRC)
BODYTXT = BODYTXT.replace(EVSRC, u"eval(e.strip().replace(u'\\n', u''), "
                                u"dict(globals(), F=F, CLOSE=CLOSE, NSRC=NSRC, "
                                u"len=len, sum=sum, max=max, min=min, abs=abs, range=range, re=re))")

ANCHORK = {u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single',
           u'anchor_cross', u'anchor_all4', u'checks',
           u'tag_768', u'tag_1122', u'tag_8200', u'tag_6935', u'enc_chars', u'nsrc'}
FLAT = json.load(io.open(u'corpus/_b70flat.json', encoding='utf-8'))
FAM = sorted({k.split(u'_')[0] for k in FLAT})


def fam(k):
    h = k.split(u'_')[0]
    return FAM.index(h) if h in FAM else len(FAM)


def lit(v):
    return repr(v).replace(u'u+', u'')


def gen_asserts(keys=None):
    ks = sorted([k for k in (keys if keys is not None else FLAT)
                 if k not in ANCHORK], key=lambda k: (fam(k), k))
    lines, buf = [], []
    for k in ks:
        piece = u"_dv(F[u'%s']) == %s" % (k, lit(FLAT[k]))
        if buf and sum(len(x) + 5 for x in buf) + len(piece) > 100:
            lines.append(u'    assert ' + u' and '.join(buf))
            buf = []
        buf.append(piece)
    if buf:
        lines.append(u'    assert ' + u' and '.join(buf))
    return NL.join(lines) + NL


HAND = u'''    # ---- 结构性自检: 进制两游标、位宽比、三档阶梯、语气三轨、段落逐词账、窗内外五轨、搬运容斥 ----
    assert F[u'num_all1s_dec'] == F[u'num_ffff_8200'] == F[u'num_ffff_6935'] == 65535
    assert F[u'num_all1s_faces'] == [0, 65535, 0, 0] and F[u'num_ffff_faces'] == [0, 0, 65535, 65535]
    assert F[u'num_radix_faces'] == [0, 1, 1, 1] and F[u'num_cursor_miss'] == 1
    assert F[u'num_radix_face_n'] == 3 and F[u'num_radix_forms'] == 2
    assert F[u'num_dec_lit'] == [0, 2, 0, 0] and F[u'num_ffff_lit'] == [0, 0, 1, 2]
    assert F[u'num_bits_768'] == 16 and F[u'num_bits128_8200'] == 128 and F[u'num_bits32_8200'] == 32
    assert F[u'num_bits_768'] * F[u'bits_ratio128'] == 128 and F[u'num_bits_768'] * F[u'bits_ratio32'] == 32
    assert F[u'bits_sum_8200'] == 160 and F[u'bits128_close'] == F[u'bits32_close'] == 0
    assert F[u'num_mbtn_6935'] == 9 and F[u'num_mbtn_hi_6935'] == 11 and F[u'mbtn_span_6935'] == 2
    assert F[u'years'] == [1980, 1989, 2017, 2013] and F[u'year_perm'] == [0, 1, 3, 2]
    assert F[u'year_gaps'] == [9, 28, -4] and F[u'year_inversions'] == 1 and F[u'year_gap'] == 4
    assert F[u'year_order'] == 0 and F[u'year_perm_close'] == 0
    assert F[u'obs_n'] == [0, 0, 1, 0] and F[u'upd_n'] == [0, 0, 0, 1] and F[u'target_ids'] == [2460]
    assert F[u'target_n'] == 1 and F[u'both_2460'] == 1 and F[u'target_agree'] == 0
    assert F[u'verb_updates_6935'] == 1 and F[u'verb_updates_8200'] == 0
    assert F[u'verb_updates_ci'] == [0, 0, 0, 1] and F[u'verb_track_close'] == 0
    assert F[u'delete_order'] == 1 and F[u'delete_order_8200'] == 0 and F[u'quote_marker_6935'] == 5
    assert F[u'std_hdr'] == [0, 0, 1, 0] and F[u'cat_std'] == [0, 0, 1, 1]
    assert F[u'up_must_all'] == [0, 200, 0, 10] and F[u'must_bare'] == [0, 180, 0, 9]
    assert F[u'must_not'] == [0, 20, 0, 1] and F[u'up_may'] == [0, 41, 0, 2] and F[u'up_should'] == [0, 73, 0, 3]
    assert F[u'low_must'] == [1, 59, 52, 5] and F[u'low_may'] == [1, 121, 32, 28]
    assert F[u'low_should'] == [3, 54, 27, 13] and F[u'ci_must'] == [1, 259, 52, 15]
    assert F[u'ci_may'] == [1, 165, 34, 31] and F[u'ci_should'] == [3, 127, 27, 16]
    assert F[u'title_must'] == [0, 0, 0, 0] and F[u'title_may'] == [0, 3, 2, 1]
    assert F[u'up_ledger'] == [0, 0, 0, 0] and F[u'case_ledger'] == [0, 0, 0, 0]
    assert F[u'lo_minus_up'] == [1, -141, 52, -5] and F[u'up_zero_docs'] == [0, 2]
    assert F[u'up_zero_n'] == 2 and F[u'std_no_upper'] == 1 and F[u'low_only_8200'] == 1
    assert F[u'sn_strict_docs'] == [3, 7, 0, 3] and F[u'sn_fold_docs'] == [6, 12, 6, 12]
    assert F[u'sn_sh_docs'] == [6, 12, 6, 12] and F[u'sn_re_docs'] == [6, 12, 6, 12]
    assert F[u'ladder_monotone'] == 1 and F[u'sh_minus_fold'] == [0, 0, 0, 0] and F[u'sh_lost_keys'] == []
    assert F[u're_eq_cur'] == 1 and F[u'overlap_extra'] == 0 and F[u'fold_line_zero'] == 0
    assert F[u'needle_n'] == 36 and F[u'fold_only_n'] == 23 and F[u'fold_only_own'] == [3, 5, 6, 9]
    assert len(F[u'fold_only_keys']) == 23 and F[u'dead_needles'] == []
    assert F[u'cross_needles'] == [u'z8200_must_compute'] and F[u'cross_needle_n'] == 1
    assert len(F[u'line_hit_keys']) == 13
    assert F[u'ck_word'] == [5, 32, 10, 73] and F[u'ck_caps'] == [2, 9, 5, 21]
    assert F[u'opt_word'] == [1, 14, 9, 1] and F[u'opt_line_ck'] == [0, 2, 0, 1]
    assert F[u'not_opt'] == [0, 0, 1, 1] and F[u'not_opt_line'] == [0, 0, 0, 1]
    assert F[u'never_opt'] == [0, 1, 0, 0] and F[u'req_word'] == [0, 1, 0, 1]
    assert F[u'zero_ck'] == [0, 0, 1, 18] and F[u'zero_hy'] == [0, 0, 2, 3] and F[u'zero_udp'] == [0, 0, 0, 15]
    assert F[u'pseudo_hy'] == [0, 0, 9, 2] and F[u'pseudo_sp'] == [1, 0, 0, 0] and F[u'pseudo_close'] == [0, 0, 0, 0]
    assert F[u'port_word'] == [1, 0, 0, 0] and F[u'opt_prev_n'] == [1, 3, 3, 1]
    assert F[u'ln_impl_1122'] == 4584 and F[u'ln_ctrl_1122'] == 4587 and F[u'ln_opt_1122'] == 4615
    assert F[u'ctrl_opt_span'] == 28 and F[u'impl_opt_span'] == 31 and F[u'opt_vs_must_dir'] == 1
    assert F[u'blk_lo'] == [1530, 466, 479] and F[u'blk_hi'] == [1537, 472, 485]
    assert F[u'blk_rows'] == [8, 7, 7] and F[u'blk_words'] == [80, 75, 70]
    assert F[u'w_common'] == 52 and F[u'w82_only_n'] == F[u'w6q_only_n'] == 2 and F[u'w_row_close'] == 0
    assert F[u'suf_82_q69'] == 5 and F[u'pre_82_q69'] == 2
    assert F[u'suf_82_6r'] == 12 and F[u'pre_82_6r'] == 0
    assert F[u'comma_82'] == 0 and F[u'comma_q69'] == 1 and F[u'comma_diff'] == 1
    assert F[u'lead_insert'] == 1 and F[u'repl_bydefault'] == 1 and F[u'p82_bydefault'] == 0
    assert F[u'tone_up_repl'] == F[u'tone_lo_82'] == 4 and F[u'tone_swap'] == 0
    assert F[u'tone_up_82'] == F[u'tone_lo_repl'] == F[u'tone_up_q69'] == 0
    assert F[u'tone_lo_q69'] == 4 and F[u'tone_rev_close'] == 0
    assert F[u'cite_sp_2460'] == [0, 0, 14, 6] and F[u'cite_tk_2460'] == [0, 0, 5, 5]
    assert F[u'cite_hy_2460'] == [0, 0, 0, 0] and F[u'cite_al_2460'] == [0, 0, 19, 11]
    assert F[u'cite_forms_2460'] == [0, 0, 2, 2] and F[u'cite_forms_close'] == [0, 0, 0, 0]
    assert F[u'cite_8200_in_6935'] == 0 and F[u'cite_6935_in_8200'] == 1
    assert F[u'cite_sp_793'] == [0, 34, 0, 0] or F[u'cite_al_793'] == [0, 34, 0, 0]
    assert F[u'win_band'] == 20 and F[u'win_named'] == 4 and F[u'win_share'] == 3
    assert F[u'win_sec'] == [45, 139, 1465, 455] and F[u'win_ans'] == [92, 4587, 1533, 483]
    assert F[u'win_start'] == [72, 4567, 1513, 463] and F[u'win_end'] == [112, 4607, 1553, 503]
    assert F[u'win_rows'] == F[u'win_spans'] == [41, 41, 41, 41]
    assert all(F[u'win_end'][i] - F[u'win_start'][i] + 1 == 41 for i in range(4))
    assert all(F[u'win_start'][i] <= F[u'win_ans'][i] <= F[u'win_end'][i] for i in range(4))
    assert F[u'win_ck_in'] == [4, 6, 8, 9] and F[u'win_ck_out'] == [1, 26, 2, 64]
    assert F[u'win_up_in'] == [0, 5, 0, 8] and F[u'win_up_out'] == [0, 309, 0, 7]
    assert F[u'win_close_sum'] == 0 and F[u'win_close_ck'] == F[u'win_close_up'] == [0, 0, 0, 0]
    assert F[u'pool_n'] == 4740 and F[u'pool_letters'] == 4723 and F[u'pool_border'] == 17
    assert F[u'pool_tier'] == [4721, 19, 0, 0] and F[u'union_incl'] == F[u'pool_n']
    assert F[u'pool_incl'] == [4759, 19, 0, 0] and F[u'union_close'] == 0
    assert F[u'pair_share'] == [0, 0, 0, 0, 0, 19] and F[u'pair_byte'] == [0, 0, 0, 0, 0, 18]
    assert F[u'pair_norm_only'] == [0, 0, 0, 0, 0, 1] and F[u'pair_close'] == 0
    assert F[u'pair_nonzero'] == 1 and F[u'axis_counts'] == {u'case': 0, u'hyph': 0, u'space': 1, u'multi': 0}
    assert F[u'axis_total'] == 1 and F[u'axis_str_n'] == 1 and F[u'axis_close'] == 0
    assert F[u's3_examples'] == [] and F[u'pool_4'] == 0
    assert F[u'apool_raw_n'] == 5321 and sum(F[u'apool_face_raw']) == 5321
    assert F[u'apool_n'] == F[u'apool_uniq'] == 5238 and F[u'apool_pairs'] == F[u'apool_weight'] == 5259
    assert F[u'apool_raw_n'] - sum(F[u'apool_dup']) == F[u'apool_weight']
    assert F[u'apool_tag_n'] == [60, 3691, 1111, 397] and F[u'apool_tier'] == [5217, 21, 0, 0]
    assert F[u'apool_tag_close'] == F[u'apool_tier_close'] == 0 and F[u'apool_maxlen'] == 72
    assert F[u'bytes'] == F[u'chars'] == [5896, 289148, 93162, 29055]
    assert F[u'lines'] == [174, 6845, 2356, 676] and F[u'nonblank'] == [108, 4549, 1488, 466]
    assert F[u'maxlen'] == [72, 72, 72, 72] and F[u'ff'] == [3, 116, 42, 12] and F[u'ff_only'] == [0, 0, 0, 0]
    assert F[u'shell_n'] == [107, 4318, 1445, 450] and F[u'shell_strip'] == [67, 2527, 911, 226]
    assert F[u'cr'] == [0, 0, 0, 0] and F[u'nul_faces'] == [0, 0, 0, 0] and F[u'ascii_all'] == 4
    assert F[u'bom'] == [0, 0, 0, 0] and F[u'nonascii'] == [0, 0, 0, 0] and F[u'nonascii_extra'] == [0, 0, 0, 0]
    assert F[u'byte_cp_delta'] == [0, 0, 0, 0] and F[u'digit_chars'] == [107, 5372, 2187, 565]
    assert F[u'dblspace'] == [1416, 66670, 16379, 2572] and F[u'dblspace_norm'] == [190, 2014, 852, 218]
    assert all(F[u'dblspace_norm'][i] <= F[u'dblspace'][i] for i in range(4))
    assert F[u'zid_n'] == 45 and F[u'zid_fail'] == [] and F[u'x_ident_n'] == 45
    assert F[u'scalar_clos_n'] == 45 and F[u'scalar_clos_sum'] == 45 and F[u'list_clos_n'] == 9
'''

ANCH = u'''
    FAN = FO
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B70_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6(' + u'|'.join(TAGS) + u')\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B70: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B70: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B70: 标签嵌套'
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
    F[u'nsrc'] = NSRC
    F[u'enc_chars'] = len(enc.replace(NL, u''))
    for t in TAGS:
        F[u'tag_' + t] = len(re.findall(u'\\u27e6%s\\u27e7' % t, enc))
    assert F[u'enc_chars'] == 8097 and F[u'nsrc'] == 4
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all4'] == len(DIS)
    assert all(F[u'tag_' + t] > 0 for t in TAGS), u'有四源标签没锚'
    assert F[u'tag_768'] == 6 and F[u'tag_1122'] == 9 and F[u'tag_8200'] == 7 and F[u'tag_6935'] == 8
    assert F[u'anchor_total'] == 30 and F[u'anchor_distinct'] == 27 and F[u'anchor_err'] == 0
    assert F[u'checks'] == 108 and F[u'anchor_all4'] == 0 and F[u'pool_4'] == 0
    AX = [a for h, a in zip(HC, DIS) if len(h) > 1]
    assert F[u'anchor_cross'] == len(AX) == 8
    assert len([h for h in HC if h == (2, 3)]) == 7, u'B70: 跨面锚不是成对落在 8200⇎6935'
    assert len([h for h in HC if h == (0, 1, 3)]) == 1, u'B70: 三份同现的标题行锚枚数变了'
    assert all(len(h) == 1 or h in ((2, 3), (0, 1, 3)) for h in HC)
    assert F[u'anchor_single'] == len(DIS) - 8 == 19
    # 同一句在 8200 是小写、在 6935 是大写: 归一(小写)后才成对, 这正是本条的分水岭
    # 跨面锚全部落在 6935 面: 替代段把两份前文的句子收进自己, 分歧在句内而非句际
    assert all(3 in h for h in HC if len(h) > 1), u'B70: 有跨面锚不落进 6935 面'
    return F

_B70 = _b70_scan()
B70V = lambda k, i=None: (_B70[k] if i is None else _B70[k][i])
'''

ANCH_A, ANCH_B = ANCH.split(u'    return F')
BLK = (HEAD + u'    def _sil(*a):\n        pass\n' + BODYTXT + HAND + ANCH_A
       + gen_asserts() + u'    return F' + ANCH_B)
compile(BLK, u'<b70 block>', u'exec')

assert S.count(NL + u"_B69 = _b69_scan()") == 1, u'anchor _b69_scan'
i0 = S.find(u'# B70: 一条 UDP 报文的校验和')
while i0 >= 0:
    i1 = S.index(u'_B69 = _b69_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B70: 一条 UDP 报文的校验和')
if u'B70V=B70V,' in S:
    S = S.replace(u'B70V=B70V,' + NL, NL)
S = S.replace(NL + u"_B69 = _b69_scan()", BLK + NL + u"_B69 = _b69_scan()")
if u'B70V=B70V' not in S:
    ME = re.search(u'B69V=B69V((?:,\\s*\\w+=\\w+)*)\\)', S)
    assert ME, u'anchor env'
    S = S[:ME.end(1)] + u',\n               B70V=B70V' + S[ME.end(1):]

PS = u"SRC['B65'] = ["
blk = (u"SRC['B70'] = ['corpus/raw/udpCK/rfc768.txt', 'corpus/raw/tcpRTO/rfc1122.txt', "
       u"'corpus/raw/udpCK/rfc8200.txt', 'corpus/raw/udpCK/rfc6935.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
if u"'B70'" not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B70'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B70'" + S[m.end(1):]

M1 = u'# ---- B70 DERIV (generated by corpus/_wire70.py from corpus/_deriv70.json; do not hand-edit) ----'
M2 = u'# ---- /B70 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o4 = u'# ---- B65 DERIV (generated by corpus/_wire65.py'
assert S.count(o4) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv70.json', encoding='utf-8'))
S = S.replace(o4, M1 + NL + u"DERIV['B70'] = " + repr(J) + NL + M2 + NL + o4)

NS = {'SRC': {'B70': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
try:
    exec(compile(BLK, u'<b70 block>', u'exec'), NS)
except AssertionError:
    import traceback
    tb = sys.exc_info()[2]
    while tb.tb_next:
        tb = tb.tb_next
    ls = BLK.split(NL)
    print(u'块内断言失败于第 %d 行:\n%s' % (tb.tb_lineno, ls[tb.tb_lineno - 1]))
    raise
env = NS['B70V']
BAD, MISMATCH = [], []


def deep(x):
    return [deep(y) for y in x] if isinstance(x, list) else list(x) if isinstance(x, tuple) else x


for k, v in FLAT.items():
    if k in (u'nsrc', u'enc_chars'):
        continue
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
        got = eval(v, dict(NS), {'B70V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b69_scan' in S and u'_b70_scan' in S
compile(S, u'<audit.py wired>', u'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b70_scan+B70V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
