# -*- coding: utf-8 -*-
"""把 B71 的独立复算器(_b71_scan / B71V)接进 audit.py, 并生成 DERIV['B71']。
幂等: 重复运行先摘旧块再插新块; 只动 B71 自己的区域, 并行 agent 的 B65/B67/B69/B70 行段原样保留。
_b71_scan 的量测段从 corpus/_mkB71.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间 ⇎
corpus/_mk71emit.py 的 SCAN2 BEGIN ⇎ SCAN2 END 之间逐行机械抽出, 只在头部换成 audit 自己的
路径常量与模块别名; 真正的独立性来自六处:
①采集侧 corpus/_pick71.py 是先于建条目写好的另一套实现(str.count/逐行 in 收针), 建条目侧改立
  游标逐字符档、正则字面档、重叠口径档与集合代数档, 两边在口径一致的键上逐量对账;
②抽出的代码在插门之前要把 _b71flat.json 的每个键与 DERIV['B71'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按归一串判成员;
④数字读数一律从面内现读: 604800 只从 "value greater than " 之后由游标解析, 括注日数、24 小时那句里的
  时数、86400=24×3600、上限/日的商与余数、2^32 的指数都由字节读, 一个不手填; 段落起止行由折平偏移映回原行号;
⑤字段改名用的是词界正则(下划线两侧不接字母数字), 于是 ticket_lifetime ⇎ ticket_lifetime_hint 两种写法
  不漏不重; 语气是四轨的: 裸 MUST ⇎ MUST NOT ⇎ 小写 must 之和必须等于不分大小写 must 档;
⑥零值那半句在 4507 里被页壳劈成两截: 同一枚连句号的针在含壳折平面落空、在摘壳折平面命中, 这类差
  只能由三档阶梯给出; 上限只活在 8446、"or longer" 在 8446 被砍、计时起点只补在 5077, 都是段内逐词账。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB71.py', encoding='utf-8').read()
EM = io.open(u'corpus/_mk71emit.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/tlsTicket/rfc4507.txt', u'corpus/raw/tlsTicket/rfc5077.txt',
        u'corpus/raw/ietf/rfc8446.txt', u'corpus/raw/tlsTicket/rfc9001.txt']


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
for nm in (u'pnorm', u'cnt_cur', u'cnt_ovl', u'read_after', u'sec_window', u'HEADND', u'POOLC', u'NPOOL',
           u'ZID', u'CLOSE', u'FOLD', u'FO', u'SH', u'SHF', u'NEEDLE', u'GN', u'GR', u'CNT',
           u'SN', u'SNF', u'SNS', u'SNR', u'NUM', u'win_close_sum', u'up_ledger', u'utf8_extra',
           u'ub', u'hdr_year', u'hdr_ids', u'shell_line', u'FLD', u'blk', u'fmap', u'line_of',
           u'ln_of', u'hint_in_blk', u'orlonger_blk', u'n_', u'num_'):
    assert nm in MEAS, nm

HEAD = u'''
# B71: TLS 会话票据到底能活多久——四份一手 TLS 文书四种答法:
# raw/tlsTicket/rfc4507.txt(A 4507/2006: 只给 hint, 不封顶——"The ticket lifetime may be longer than the
#   24-hour lifetime recommended"; 零值写成 "A value of zero is reserved to indicate that the lifetime of
#   the ticket is unspecified."(未定), 而这半句在页面上被页眉页脚劈成两截; 字段名 ticket_lifetime_hint)
# ⇎ raw/tlsTicket/rfc5077.txt(B 5077/2008, Obsoletes: 4507: 同一句整段照搬、一个词都没动(段内 62 枚词共头
#   共尾都是 62), 只在字段说明处补计时起点 "relative to when the ticket is received"(离定义句 3 行))
# ⇎ raw/ietf/rfc8446.txt(C 8446/2018, Obsoletes: 5077/5246/6961 ⇎ Updates: 5705/6066: 字段改名 ticket_lifetime,
#   写出硬上限 "MUST NOT use any value greater than 604800 seconds (7 days)", 同一个零值翻成
#   "should be discarded immediately"(立即丢弃), 把上一代的出口 "shorter or longer" 砍成只剩 shorter,
#   起算点改成 "from the time of ticket issuance", 还第一次禁复用 SHOULD NOT reuse a ticket)
# ⇎ raw/tlsTicket/rfc9001.txt(D 9001/2021: 全篇不自建时长, 把裁决转述给 [TLS13]——"sets a limit of seven days",
#   该方括号别名叫 31 枚; 面上连 "A value of zero" 都一枚没有; 复用禁令另写一式, 与 8446 不逐字同现)。
# 本函数从四份字节独立复算: 上限的三条轨(游标 ⇎ 字面 ⇎ 整句针)与 24 小时⇎7 天的换算/整除/余数, 字段改名的
# 词界正则两档, 三档口径阶梯的在册答句针(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 正则轨 ⇎ 重叠口径), 义务语气四轨
# (裸 MUST ⇎ MUST NOT ⇎ 小写 must = 不分大小写 must), 4507⇎5077⇎8446 同一段的逐词账(段界映回原行 ⇎ 共有词 ⇎
# 独有词 ⇎ 共尾 ⇎ 共头 ⇎ 段内 hint ⇎ 段内 or longer ⇎ 段内大写义务), 动作头 Obsoletes ⇎ Updates 的对象并集
# 与链条, 标题页年份(行尾锚定 ⇎ 相邻差 ⇎ 置换索引 ⇎ 倒序数), 引用三式与互引方向, 答句邻域窗(±20 行)五轨对账,
# 长行池两两交的逐字节 ⇎ 仅归一分裂与写法分家四桶, 编码层(9001 一枚 BOM ⇎ 8 枚非 ASCII ⇎ 12 枚多余字节)。
# 恒等式(上限三轨同数 ⇎ 24×3600=86400 ⇎ 604800/86400=7 余 0 ⇎ 词界正则=hint式+plain式 ⇎ 阶梯单调
# ⇎ 大写+小写+MUST NOT=不分大小写 ⇎ 段词独有+共有=全集 ⇎ 带内+带外=全篇五轨 ⇎ Σ单份−Σ两两+Σ三三−Σ四份=并集 ⇎
# 归一交=逐字节交+仅归一 ⇎ 分档之和=池条数 ⇎ 锚按标签账=按份数账)全归零送门槛重算。
# 不可由在库文件判定的: 四份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 4507/5077 此后被改列为 Experimental、[TLS13] 之外被引用的那些文书本身(不在库内)、现网实现实际把票据缓存多久——
# 只进解读注, 不进门槛。
def _b71_scan():
    import io, re, itertools, hashlib as _hl
    from collections import Counter, defaultdict
    P2 = SRC['B71']
    NSRC = 4
    LBL = [u'4507', u'5077', u'8446', u'9001']
    TAGS = LBL
    YR = [u'06', u'08', u'18', u'21']
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
           u'tag_4507', u'tag_5077', u'tag_8446', u'tag_9001', u'enc_chars', u'nsrc'}
FLAT = json.load(io.open(u'corpus/_b71flat.json', encoding='utf-8'))
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


HAND = u'''    # ---- 结构性自检: 上限三轨、字段改名词界、三档阶梯、语气四轨、段落逐词账、窗内外五轨、搬运容斥 ----
    assert F[u'num_cap_faces'] == [0, 0, 604800, 0] and F[u'num_cap_lit'] == [0, 0, 1, 0]
    assert F[u'num_cap_days'] == [0, 0, 7, 0] and F[u'num_cap_present_docs'] == 1
    assert F[u'n_z8446_cap'] == [0, 0, 1, 0] and F[u'num_cap_lit'] == F[u'n_z8446_cap']
    assert F[u'num_cap_ratio'] == 7 and F[u'num_cap_remainder'] == 0 and F[u'cap_ratio_close'] == 0
    assert F[u'num_day_seconds'] == F[u'num_d24'] * 3600 == 86400 and F[u'day_lt_cap'] == 0
    assert F[u'num_mod_pow'] == 32 and F[u'num_ms_factor'] == 1000 and F[u'num_sec_ms_close'] == 32
    assert F[u'must_cap_face'] == [0, 0, 0, 0] and F[u'no_self_lifetime'] == 1
    assert F[u'fld_hint'] == [3, 3, 0, 0] and F[u'fld_plain'] == [0, 0, 7, 0]
    assert F[u'fld_sub'] == [F[u'fld_hint'][i] + F[u'fld_plain'][i] for i in range(4)]
    assert F[u'fld_sub'] == [3, 3, 7, 0] and F[u'fld_close'] == [0, 0, 0, 0]
    assert F[u'uint32_hint'] == [1, 1, 0, 0] and F[u'uint32_plain'] == [0, 0, 2, 0]
    assert F[u'field_renamed'] == 1 and F[u'hint_word'] == [5, 5, 0, 0]
    assert F[u'lifetime_word'] == [12, 13, 12, 2] == F[u'n_z9001_lifetime_word']
    assert F[u'week_word'] == [0, 0, 1, 0] and F[u'seven_days'] == [0, 0, 0, 1] and F[u'week_only_8446'] == 1
    assert F[u'd24_hour'] == [1, 1, 0, 0] and F[u'24hour_pair'] == 0
    assert F[u'sn_strict_docs'] == [1, 0, 2, 2] and F[u'sn_fold_docs'] == [7, 6, 9, 4]
    assert F[u'sn_sh_docs'] == F[u'sn_re_docs'] == [7, 6, 9, 4] and F[u'sh_lost_keys'] == []
    assert F[u'ladder_monotone'] == 1 and F[u'sh_minus_fold'] == [0, 0, 0, 0] and F[u'fold_line_zero'] == 0
    assert F[u're_eq_cur'] == 1 and F[u'overlap_extra'] == 0
    assert F[u'needle_n'] == 28 and sum(F[u'needles_owned']) == F[u'needle_n']
    assert F[u'needles_owned'] == [8, 6, 9, 5] and F[u'fold_only_n'] == 21
    assert F[u'fold_only_own'] == [6, 6, 7, 2] and len(F[u'line_hit_keys']) == 5
    assert F[u'dead_needles'] == [u'z4507_no_relative', u'z9001_zero'] and F[u'cross_needle_n'] == 11
    assert F[u'zero_carry_sh'] == [1, 1] and F[u'zero_carry_fold'] == [1, 0]
    assert F[u'zero_res_agree'] == 0 and F[u'zero_flip'] == 1 and F[u'zero_ind_unique'] == 0
    assert F[u'n_z5077_zero_reserved'] == [0, 1, 0, 0] and F[u'n_z4507_zero_reserved'] == [1, 1, 0, 0]
    assert F[u'zero_split_gap'] == F[u'ln_unspec_4507'] - F[u'ln_zero_4507'] == 10
    assert F[u'relative_span'] == F[u'ln_relative_5077'] - F[u'ln_hintdef_5077'] == 3
    assert F[u'cap_zeroind_span'] == F[u'ln_cap_8446'] - F[u'ln_zeroind_8446'] == -1
    assert F[u'relative_in'] == [0, 2, 0, 0] and F[u'rel_inserted'] == 1 and F[u'from_issuance_only'] == 1
    assert F[u'up_must_all'] == [18, 18, 330, 85] and F[u'must_bare'] == [9, 9, 256, 60]
    assert F[u'must_not'] == [9, 9, 74, 25] and F[u'up_may'] == [6, 6, 58, 24] and F[u'up_should'] == [5, 5, 76, 21]
    assert F[u'ci_must'] == [F[u'must_bare'][i] + F[u'must_not'][i] + F[u'low_must'][i] for i in range(4)]
    assert F[u'ci_must'] == [21, 21, 344, 87] and F[u'low_must'] == [3, 3, 14, 2]
    assert F[u'up_ledger'] == [0, 0, 0, 0] and F[u'case_ledger'] == [0, 0, 0, 0]
    assert F[u'title_must'] == [0, 0, 0, 0] and F[u'should_not'] == [1, 1, 15, 2] and F[u'reuse_absent'] == 1
    assert F[u'should_delete'] == [0, 0, 0, 0] and F[u'n_z4507_should_delete'] == [1, 1, 0, 0]
    assert F[u'blk_lo'] == [389, 438, 4124] and F[u'blk_hi'] == [403, 443, 4126]
    assert F[u'blk_rows'] == [15, 6, 3] and F[u'blk_words'] == [62, 62, 21]
    assert F[u'suf_45_50'] == F[u'pre_45_50'] == 62 and F[u'w45_only_n'] == F[u'w50_only_n'] == 0
    assert F[u'w_common'] == 43 and F[u'w_row_close'] == 0
    assert F[u'suf_50_84'] == 0 and F[u'pre_50_84'] == 1 and F[u'hint_in_blk'] == [1, 1, 0]
    assert F[u'orlonger_blk'] == [1, 1, 0] and F[u'orlonger'] == [1, 1, 0, 0]
    assert F[u'shorter_only'] == [0, 0, 1, 0] and F[u'drop_or_longer'] == 1
    assert F[u'tone_up_45'] == F[u'tone_up_50'] == 3 and F[u'tone_up_84'] == 1 and F[u'tone_cap_84'] == 0
    assert F[u'reuse_word'] == [0, 0, 4, 2] and F[u'discard_low'] == [2, 2, 5, 24]
    assert F[u'imm_word'] == [0, 0, 16, 9] and F[u'unspec_word'] == [2, 2, 2, 0] and F[u'zero_word'] == [4, 4, 41, 8]
    assert F[u'obs_n'] == [0, 1, 4, 0] and F[u'upd_n'] == [0, 0, 2, 0] and F[u'upd_line'] == [0, 0, 1, 0]
    assert F[u'obs_set_5077'] == [4507] and F[u'obs_set_8446'] == [2018, 5077, 5246, 6961]
    assert F[u'upd_set_8446'] == [5705, 6066]
    assert F[u'target_ids'] == sorted(F[u'target_ids']) == [2018, 4507, 5077, 5246, 5705, 6066, 6961]
    assert F[u'target_n'] == 7 and F[u'chain_closed'] == 1 and F[u'obs_5077_unique'] == 0
    assert F[u'years'] == [2006, 2008, 2018, 2021] and F[u'year_perm'] == [0, 1, 2, 3]
    assert F[u'year_gaps'] == [2, 10, 3] and F[u'year_inversions'] == 0 and F[u'year_order'] == 0
    assert F[u'months'] == [u'May', u'January', u'August', u'May'] and F[u'year_n'] == 4
    assert F[u'cat_hdr'] == [1, 1, 1, 1] == F[u'cat_std'] and F[u'cat_close'] == 0
    assert F[u'std_hdr'] == [0, 0, 0, 0] and F[u'issn'] == [0, 0, 1, 1]
    assert F[u'cite_al_4507'] == [16, 24, 0, 0] and F[u'cite_al_5077'] == [0, 19, 5, 0]
    assert F[u'cite_al_8446'] == [0, 0, 192, 2] and F[u'cite_al_9001'] == [0, 0, 0, 0]
    assert F[u'cite_self'] == [16, 19, 192, 0] and F[u'cite_forms_close'] == [0, 0, 0, 0]
    assert F[u'cite_4507_in_5077'] == 24 and F[u'cite_5077_in_8446'] == 5
    assert F[u'cite_9001_in_8446'] == 0 and F[u'cite_dir'] == 1 and F[u'num_tls13_refs'] == [0, 0, 0, 31]
    assert F[u'win_band'] == 20 and F[u'win_named'] == 4 == F[u'win_ans_named']
    assert F[u'win_sec'] == [360, 406, 4051, 767] and F[u'win_ans'] == [387, 438, 4121, 787]
    assert F[u'win_start'] == [367, 418, 4101, 767] and F[u'win_end'] == [407, 458, 4141, 807]
    assert F[u'win_rows'] == F[u'win_spans'] == [41, 41, 41, 41]
    assert all(F[u'win_end'][i] - F[u'win_start'][i] + 1 == 41 for i in range(4))
    assert all(F[u'win_start'][i] <= F[u'win_ans'][i] <= F[u'win_end'][i] for i in range(4))
    assert F[u'win_lt_in'] == [4, 4, 5, 0] and F[u'win_lt_out'] == [8, 9, 7, 2]
    assert F[u'lifetime_word'] == [F[u'win_lt_in'][i] + F[u'win_lt_out'][i] for i in range(4)]
    assert F[u'win_zero_in'] == [2, 2, 1, 0] and F[u'win_zero_out'] == [2, 2, 40, 8]
    assert F[u'zero_word'] == [F[u'win_zero_in'][i] + F[u'win_zero_out'][i] for i in range(4)]
    assert F[u'win_cap_in'] == [0, 0, 1, 0] and F[u'win_cap_out'] == [0, 0, 0, 0]
    assert F[u'win_reuse_in'] == [0, 0, 0, 0] and F[u'win_reuse_out'] == [0, 0, 4, 2]
    assert F[u'win_close_sum'] == 0 and F[u'win_close_lt'] == F[u'win_close_zero'] == [0, 0, 0, 0]
    assert F[u'win_close_cap'] == F[u'win_close_reuse'] == F[u'win_close_dig'] == [0, 0, 0, 0]
    assert F[u'pool_n'] == 5710 and F[u'pool_letters'] + F[u'pool_border'] == F[u'pool_n']
    assert F[u'pool_tier'] == [5408, 297, 3, 2] and sum(F[u'pool_tier']) == F[u'pool_n']
    assert F[u'pool_tier_close'] == 0 and F[u'union_incl'] == F[u'pool_n'] and F[u'union_close'] == 0
    assert F[u'pool_1'] + F[u'pool_3'] + F[u'pool_4'] == 5413 and F[u'pool_2'] == 297
    assert F[u'pair_share'] == [259, 7, 2, 8, 2, 40] and F[u'pair_byte'] == [235, 1, 1, 6, 2, 39]
    assert F[u'pair_norm_only'] == [24, 6, 1, 2, 0, 1] and F[u'pair_close'] == 0
    assert F[u'pair_share'] == [F[u'pair_byte'][i] + F[u'pair_norm_only'][i] for i in range(6)]
    assert F[u'pair_max_lbl'] == u'4507·5077' and F[u'pair_max'] == 259 and F[u'pair_max_norm_only'] == 24
    assert F[u'pair_nonzero'] == 6 and F[u'shared_norm_only'] == 34
    assert F[u'axis_total'] == F[u'norm_only_set'] == 30 and F[u'axis_close'] == 0
    assert F[u'axis_str_n'] == 2 and F[u'axis_counts'] == {u'case': 2, u'hyph': 0, u'space': 28, u'multi': 0}
    assert F[u'apool_raw_n'] == 7247 and sum(F[u'apool_face_raw']) == F[u'apool_raw_n']
    assert F[u'apool_n'] == F[u'apool_uniq'] == 6573 and F[u'apool_pairs'] == F[u'apool_weight'] == 6942
    assert F[u'apool_raw_n'] - sum(F[u'apool_dup']) == F[u'apool_weight']
    assert F[u'apool_tag_n'] == [422, 505, 4249, 1766] and sum(F[u'apool_tag_n']) == F[u'apool_weight']
    assert F[u'apool_tier'] == [6216, 347, 8, 2] and sum(F[u'apool_tier']) == F[u'apool_n']
    assert F[u'apool_tag_close'] == F[u'apool_tier_close'] == 0 and F[u'apool_maxlen'] == 69
    assert F[u'bytes'] == [35329, 41989, 337736, 126175] and F[u'chars'] == [35329, 41989, 337736, 126163]
    assert F[u'lines'] == [956, 1124, 8964, 2757] and F[u'nonblank'] == [608, 710, 5848, 2186]
    assert F[u'maxlen'] == [72, 72, 72, 72] and F[u'ff'] == [17, 20, 160, 0] == F[u'ff_exact']
    assert F[u'ff_only'] == [0, 0, 0, 0] and F[u'shell_n'] == [572, 667, 5524, 2183]
    assert F[u'shell_strip'] == [384, 457, 3440, 574] and F[u'cr'] == [0, 0, 0, 0]
    assert F[u'nul_faces'] == [0, 0, 0, 0] and F[u'ascii_all'] == 3
    assert F[u'bom'] == [0, 0, 0, 1] and F[u'nonascii'] == [0, 0, 0, 8] and F[u'nonascii_extra'] == [0, 0, 0, 12]
    assert F[u'byte_cp_delta'] == F[u'nonascii_extra'] and F[u'digit_chars'] == [648, 868, 9315, 5582]
    assert F[u'zid_n'] == 57 and F[u'zid_fail'] == [] and F[u'x_ident_n'] == 57
    assert F[u'scalar_clos_n'] == F[u'scalar_clos_sum'] == 57 and F[u'list_clos_n'] == 9
'''

ANCH = u'''
    FAN = FO
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B71_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6(' + u'|'.join(TAGS) + u')\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B71: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B71: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B71: 标签嵌套'
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
    assert F[u'enc_chars'] == 7298 and F[u'nsrc'] == 4
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all4'] == len(DIS)
    assert all(F[u'tag_' + t] > 0 for t in TAGS), u'有四源标签没锚'
    assert F[u'tag_4507'] == 4 and F[u'tag_5077'] == 2 and F[u'tag_8446'] == 8 and F[u'tag_9001'] == 3
    assert F[u'anchor_total'] == 17 and F[u'anchor_distinct'] == 14 and F[u'anchor_err'] == 0
    assert F[u'checks'] == 56 and F[u'anchor_all4'] == 0 and F[u'pool_4'] == 2
    AX = [a for h, a in zip(HC, DIS) if len(h) > 1]
    assert F[u'anchor_cross'] == len(AX) == 2
    assert all(h == (0, 1) for h in HC if len(h) > 1), u'B71: 跨面锚不落进 4507⇎5077 那对'
    assert F[u'anchor_single'] == len(DIS) - 2 == 12
    # 唯一的跨面锚对是"24 小时"那行与零值半句: 5077 换掉的只有引用号 ⇎ 页壳位置
    assert len([a for a, h in zip(DIS, HC) if h == (0, 1) and u'24-hour' in a]) == 1
    assert len([a for a, h in zip(DIS, HC) if h == (0, 1) and u'value of zero is reserved' in a]) == 1
    return F

_B71 = _b71_scan()
B71V = lambda k, i=None: (_B71[k] if i is None else _B71[k][i])
'''

ANCH_A, ANCH_B = ANCH.split(u'    return F')
BLK = (HEAD + u'    def _sil(*a):\n        pass\n' + BODYTXT + HAND + ANCH_A
       + gen_asserts() + u'    return F' + ANCH_B)
compile(BLK, u'<b71 block>', u'exec')

assert S.count(NL + u"_B70 = _b70_scan()") == 1, u'anchor _b70_scan'
i0 = S.find(u'# B71: TLS 会话票据到底能活多久')
while i0 >= 0:
    i1 = S.index(u'_B70 = _b70_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B71: TLS 会话票据到底能活多久')
if u'B71V=B71V,' in S:
    S = S.replace(u'B71V=B71V,' + NL, NL)
S = S.replace(NL + u"_B70 = _b70_scan()", BLK + NL + u"_B70 = _b70_scan()")
if u'B71V=B71V' not in S:
    ME = re.search(u'B70V=B70V((?:,\\s*\\w+=\\w+)*)\\)', S)
    assert ME, u'anchor env'
    S = S[:ME.end(1)] + u',\n               B71V=B71V' + S[ME.end(1):]

PS = u"SRC['B65'] = ["
blk = (u"SRC['B71'] = ['corpus/raw/tlsTicket/rfc4507.txt', 'corpus/raw/tlsTicket/rfc5077.txt', "
       u"'corpus/raw/ietf/rfc8446.txt', 'corpus/raw/tlsTicket/rfc9001.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
if u"'B71'" not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B71'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B71'" + S[m.end(1):]

M1 = u'# ---- B71 DERIV (generated by corpus/_wire71.py from corpus/_deriv71.json; do not hand-edit) ----'
M2 = u'# ---- /B71 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o4 = u'# ---- B70 DERIV (generated by corpus/_wire70.py'
assert S.count(o4) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv71.json', encoding='utf-8'))
S = S.replace(o4, M1 + NL + u"DERIV['B71'] = " + repr(J) + NL + M2 + NL + o4)

NS = {'SRC': {'B71': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
try:
    exec(compile(BLK, u'<b71 block>', u'exec'), NS)
except AssertionError:
    import traceback
    tb = sys.exc_info()[2]
    while tb.tb_next:
        tb = tb.tb_next
    ls = BLK.split(NL)
    print(u'块内断言失败于第 %d 行:\n%s' % (tb.tb_lineno, ls[tb.tb_lineno - 1]))
    raise
env = NS['B71V']
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
        got = eval(v, dict(NS), {'B71V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b70_scan' in S and u'_b71_scan' in S
compile(S, u'<audit.py wired>', u'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b71_scan+B71V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
