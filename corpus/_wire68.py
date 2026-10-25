# -*- coding: utf-8 -*-
"""把 B68 的独立复算器(_b68_scan / B68V)接进 audit.py, 并生成 DERIV['B68']。
幂等: 重复运行先摘旧块再插新块; 只动 B68 自己的区域, B65/B67 的行段原样保留。
_b68_scan 的量测段从 corpus/_mkB68.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自六处:
①采集侧 corpus/_pick68.py 是先于建条目写好的另一套实现(正则族收针、re.sub 链做归一、集合运算求整行搬运、
  按“大写注释⇎小写粘连⇎右括号夹在数与注释之间”三种写法收 SOA 五元组), 两边在 112 个口径一致的键上逐量对账
  (四份都是 RFC Editor 纯文本面, 无需按介质分流; 现况 112 采集键／不符 0／采集侧独有 0 键＋3 项声明),
  建条目侧改立游标档(find 循环逐处数)、逐字符形状档、逐字符词界桶, 不复用其正则;
②抽出的代码在插门之前要把 _b68flat.json 的每个键与 DERIV['B68'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按归一串判成员;
④数字读数一律从面内现读: 上限 2147483647、幂 31、低位数 31、字段宽 32、示例下限 86400 五枚数
  分别由正向游标与逆向游标从句子内部解析, 尺寸表的 63⇎255⇎512 由列首游标解析, 一个都不手填;
  窗长、窗起行、窗止行由正文标题行现定位后按行切; 页眉⇎页脚⇎分隔线⇎换页符⇎点线目录行⇎BOM 都从字节面逐字符数出;
  表外常数只有 55 字符(长行口径)与 40 字符(页脚长度口径)两枚阈值;
⑤三面口径是本条的支柱: 同一批在册答数句在“原面⇎全篇折平⇎摘掉页壳再折平”三档上的读数各立一键,
  97 的编码句被页壳劈在两页之间, 前两档都读不出它——这类差只能由复算给出, 必须进门槛而不是只进注;
⑥宣称⇎复算是门可算的量: signed 的三桶(独立⇎un 之后⇎别的字母之后)与 unsigned 针交叉闭合,
  上界⇎下界⇎不谈三档恰分四份, 87 姊妹篇的 SOA 示例五个字段名共有而没有一个取值相同。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB68.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/dnsTTL/rfc1034.txt', u'corpus/raw/dnsTTL/rfc1035.txt',
        u'corpus/raw/dnsTTL/rfc1536.txt', u'corpus/raw/dnsTTL/rfc2181.txt']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'# --- SCAN BEGIN ---', u'# --- SCAN END ---')
MEAS = MEAS[MEAS.index(NL) + 1:]
assert u'RAWB' in MEAS and u'POOL' in MEAS and u'ZID' in MEAS
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
assert u'pnorm' in MEAS and u'FAN' in MEAS and u'bisect_left' in MEAS
assert u'sh_face(' in MEAS and u'num_after' in MEAS and u'num_before' in MEAS
assert u'soa_rows' in MEAS and u'lead_num' in MEAS and u'window(' in MEAS
assert u'sn_fold_docs' in MEAS and u'sn_sh_docs' in MEAS and u'foot_line' in MEAS

HEAD = u'''
# B68: 一条 RR 的 TTL 上限到底是多少、谁有权截——四份 DNS 一手文书四种答法:
# raw/dnsTTL/rfc1034.txt(A 87 只说 32 位: 定义篇把 TTL 写成 "a 32 bit integer in units of seconds",
#   不给符号也不给数, 但示例区用 "here 86400 seconds, or one day" 立了一枚下界; 概念篇还留着一句
#   "most positive and most negative 32 bit numbers" 的绕边界警告)
# ⇎ rfc1035.txt(B 87 说 signed: 实现篇的 §2.3.4 表把 TTL 写成 "positive values of a signed 32 bit number",
#   同一张表另三行给的是 63⇎255⇎512 三枚数; 它又在 SOA 里把 MINIMUM 说成 "unsigned 32 bit",
#   并宣告 "MINIMUM is a lower bound on the TTL field")
# ⇎ rfc1536.txt(C 93 只谈缓存: 通篇不写上限, 时长字面一枚都没有, 只有 "cached for TTL seconds"
#   与 §5 Cache Leaks: 的诊断句; 它把截权推给实现("might impose a limit on the cache size"))
# ⇎ rfc2181.txt(D 97 定死 31 位: "It is hereby specified that a TTL value is an unsigned number,
#   with a minimum value of 0, and a maximum value of 2147483647", 另写 2^31−1⇎只用低 31 位⇎最高位按 0⇎
#   收方一律自截("always free to place an upper bound")⇎"maximum time to live, not a mandatory time to live",
#   并把 differing TTLs 判为 deprecated; 它是四份里唯一挂 STD 13 更正身份的一份)。
# 本函数从四份字节独立复算: 逐字符形状档(页眉⇎页脚⇎分隔线⇎换页符⇎拖空格行五本账),
# 句内游标档解析五枚数字(正向⇎逆向⇎列首三式), 三面口径的在册答数句档(原面⇎全篇折平⇎摘壳折平),
# 严格⇎容行⇎摘壳三档单调账, signed 词三桶⇎unsigned 针交叉, 窗口档先定位正文标题行再按行切,
# 大写义务⇎小写词界两档, 引用网(1034⇎1035⇎1536⇎2181 各被谁引 ⇎ [RFC 方括号族 ⇎ RFC- 短横族),
# 整行搬运的归一⇎逐字节两把尺与四源长行容斥, 锚候选池按逐字再现份数四层划分。
# 49 条由面内现读数构成的恒等式(2147483647=2^31−1、32−31=符号位、上界+下界+不谈=四份、
# 窗内+窗外=全篇 TTL⇎cache⇎小写 ttl⇎数字符、三桶之和=signed 针、桶里 un 那档=unsigned 针、
# 归一长行交=逐字节交+仅归一、Σ单份−Σ两两+Σ三三−Σ四份=并集、页壳行=页眉+页脚+裸分隔线)全归零送门槛重算。
# 不可由在库文件判定的: 四份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 1035bis 之类后续草案怎么改这一段、各家 resolver 实际把 TTL 截到多少秒——只进解读注, 不进门槛。
def _b68_scan():
    import hashlib as _hl
    from bisect import bisect_left
    P2 = SRC['B68']
    NSRC = 4
    TAGS = [u'A', u'B', u'C', u'D']
    FULL = [u'1034', u'1035', u'1536', u'2181']
    LB = dict(zip(TAGS, [u'87 只说32位', u'87 说signed', u'93 只谈缓存', u'97 定死31位']))
    PATH = P2
    IDX = dict((t, i) for i, t in enumerate(TAGS))
    NL = chr(10)
    MINLEN = 55
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
BODYTXT = re.sub(u'(?<![.\\w])hashlib\\.', u'_hl.', BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert u'_hl.blake2b' in BODYTXT and u'bisect_left(' in BODYTXT

ANCHORK = {u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single',
           u'anchor_cross', u'anchor_all4', u'checks', u'tag_A', u'tag_B', u'tag_C', u'tag_D'}
FAM = sorted({k.split(u'_')[0] for k in json.load(
    io.open(u'corpus/_b68flat.json', encoding='utf-8'))})


def fam(k):
    h = k.split(u'_')[0]
    return FAM.index(h) if h in FAM else len(FAM)


def lit(v):
    return repr(v).replace(u'u+', u'')


def gen_asserts(FLAT, keys=None):
    ks = sorted([k for k in (keys if keys is not None else FLAT)
                 if k not in ANCHORK], key=lambda k: (fam(k), k))
    lines, buf = [], []
    for k in ks:
        piece = u"F[u'%s'] == %s" % (k, lit(FLAT[k]))
        if buf and sum(len(x) + 5 for x in buf) + len(piece) > 100:
            lines.append(u'    assert ' + u' and '.join(buf))
            buf = []
        buf.append(piece)
    if buf:
        lines.append(u'    assert ' + u' and '.join(buf))
    return NL.join(lines) + NL


HAND = u'''    # ---- 结构性自检: 句内游标五枚数、三桶⇎两针、三档面单调、上中下三账、窗口内外账、页壳五账、搬运容斥 ----
    assert F[u'ttl_max'] == 2147483647 and F[u'ttl_pow'] == F[u'ttl_bits'] == 31
    assert F[u'ttl_field_bits'] == 32 and F[u'max_pow_close'] == F[u'pow_bits_close'] == 0
    assert F[u'bitloss_close'] == 0 and F[u'ttl_field_bits'] - F[u'ttl_bits'] == 1
    assert F[u'min_floor'] == 86400 and F[u'floor_day_close'] == 0
    assert F[u'soa_min_A'] == F[u'min_floor'] and F[u'floor_soa_close'] == 0
    assert F[u'ceil_docs_n'] == 1 and F[u'no_dur_docs'] == 1
    assert F[u'has_ceil'] == [0, 0, 0, 1] and F[u'has_floor'] == [1, 1, 0, 0]
    assert F[u'has_none'] == [0, 0, 1, 0] and F[u'ceil_floor_close'] == 0
    assert sum(F[u'has_ceil']) + sum(F[u'has_floor']) + sum(F[u'has_none']) == NSRC
    assert F[u'size_b_rows'] == 4 and F[u'size_num_rows'] == 3 and F[u'size_sign_rows'] == 1
    assert F[u'size_nums'] == [63, 255, 512] and F[u'size_row_close'] == 0
    assert F[u'size_other_rows'] == [0, 0, 0] and F[u'lit_signed32'] == [0, 1, 0, 0]
    assert F[u'lit_max_lit'] == [0, 0, 0, 1] and F[u'lit_max_pow'] == [0, 0, 0, 1]
    assert F[u'lit_hi31'] == [0, 0, 0, 1] and F[u'lit_upper_bound'] == [0, 0, 0, 1]
    assert F[u'lit_not_mandatory'] == [0, 0, 0, 0] and F[u'fold_not_mandatory'] == [0, 0, 0, 1]
    assert F[u'lit_cached_for'] == [0, 0, 1, 0] and F[u'lit_floor_sent'] == [0, 0, 0, 0]
    assert F[u'fold_floor_sent'] == [1, 0, 0, 0] and F[u'wrap_lit_zero'] >= 1

    assert F[u'sgn_bare'] == [0, 2, 0, 2] and F[u'sgn_in_un'] == F[u'lit_unsigned_word']
    assert F[u'sgn_bucket_close'] == [0] * 4 and F[u'unsg_scan_close'] == [0] * 4
    assert [F[u'sgn_bare'][i] + F[u'sgn_in_un'][i] + F[u'sgn_in_word'][i]
            for i in range(4)] == F[u'lit_signed_word']
    assert F[u'lit_signed_word'] == [6, 15, 0, 7] and F[u'lit_unsigned_word'] == [0, 9, 0, 2]
    assert F[u'sign_docs'] == [0, 1, 0, 1] and F[u'sign_docs_n'] == 2
    assert F[u'sign_ledger'] == 0 and F[u'row_unsign'] == [0, 0, 0, 1]

    assert F[u'sn_strict_docs'] == [0, 1, 0, 0] and F[u'sn_fold_docs'] == [5, 6, 4, 10]
    assert F[u'sn_sh_docs'] == [5, 6, 4, 11] and F[u'sh_ladder_bad'] == 0
    assert F[u'sn_face_span'] == [5, 5, 4, 11]
    assert F[u'wrap_sn_hit'] == 24 and F[u'wrap_sn_total'] == 24
    assert F[u'wrap_hit_minus_onlyfold'] == 0 and F[u'wrap_close'] == 0
    assert F[u'sh_sn_hit'] == F[u'sh_only_n'] == F[u'sh_gap_total'] == 1
    assert F[u'sh_hit_minus_only'] == 0 and F[u'sn_only_sh'] == [u'd_bits']
    assert F[u'main4_fold'] == [1, 1, 1, 1] and F[u'main4_each'] == 4 and F[u'main4_close'] == 0
    assert [F[u'main4_fold'][i] + F[u'sn_other_fold'][i] for i in range(4)] == F[u'sn_fold_docs']
    assert F[u'ceil_sn_close'] == F[u'floor_sn_close'] == F[u'cache_sn_close'] == 0
    assert F[u's_d_bits'][3] == 0 and F[u's_d_bits_fold'][3] == 0 and F[u's_d_bits_sh'][3] == 1

    assert F[u'sec_head'] == [u'3.6. Resource Records', u'2.3.4. Size limits',
                              u'5. Cache Leaks:', u'8. Time to Live (TTL)']
    assert F[u'sec_len'] == [4240, 331, 1955, 1063] and min(F[u'sec_len']) == 331
    assert F[u'sec_lines'] == [110, 14, 48, 27]
    for w in (u'ttl', u'ttllow', u'cache'):
        assert F[u'win_close_' + w] == [0] * 4
    assert F[u'ttl_win_close_sum'] == F[u'cache_win_close_sum'] == F[u'ttllow_win_close_sum'] == 0
    assert F[u'digit_win_close'] == [0] * 4 and F[u'digit_density'] == [8, 39, 6, 30]
    assert F[u'secw_ttl'] == [8, 1, 10, 7] and F[u'outw_ttl'] == [22, 30, 2, 25]
    assert [F[u'secw_ttl'][i] + F[u'outw_ttl'][i] for i in range(4)] == F[u'lit_ttl_cap']
    assert [F[u'secw_digit'][i] + F[u'outw_digit'][i] for i in range(4)] == F[u'digit_runs']
    assert F[u'secw_digit'] == [37, 13, 12, 32] and F[u'outw_digit'] == [2203, 2085, 326, 456]

    assert F[u'oblig_up'] == [0, 0, 0, 3] and F[u'oblig_up_close'] == 0
    assert F[u'up_ABC_zero'] == 0 and F[u'hereby_D_only'] == 0 and F[u'shall_D_only'] == 0
    assert F[u'oblig_low'] == [139, 167, 26, 94] and F[u'oblig_low_close'] == [0] * 4
    assert F[u'rfc2119_ref'] == [0, 0, 0, 0]

    assert F[u'hdr'] == [54, 54, 11, 14] and F[u'foot'] == [55, 55, 12, 15]
    assert F[u'formfeed'] == [55, 55, 12, 14] and F[u'tail_ff'] == [1, 1, 1, 0]
    assert F[u'foot_minus_hdr'] == [1] * 4 and F[u'pg_foot_close'] == [0] * 4
    assert F[u'ff_model_close'] == [0] * 4 and F[u'trail_hdr_close'] == [0] * 4
    assert F[u'shell_close'] == [0] * 4 and F[u'shell_lines'] == [109, 109, 23, 29]
    assert F[u'nb_ff_close'] == [0] * 4
    assert F[u'bytes'] == [126103, 122549, 25476, 36989]
    assert F[u'lines'] == [3078, 3078, 675, 843] and F[u'nonblank'] == [2080, 2070, 443, 583]
    assert F[u'cr'] == [0] * 4 and F[u'nonascii'] == [0] * 4 and F[u'bom'] == [0] * 4
    assert F[u'enc_close'] == [0] * 4 and F[u'sig_distinct'] == 4 and F[u'ascii_all'] == 4

    assert F[u'soa_n_lines'] == [10, 5, 0, 0] and F[u'soa_CD_empty'] == 2
    assert F[u'soa_AB_shared'] == 5 and F[u'soa_AB_valshare'] == 0
    assert F[u'soa_AB_close'] == 0 and F[u'soa_val_close'] == 0
    assert F[u'soa_upper'] == [0, 5, 0, 0] and F[u'soa_lower'] == [10, 0, 0, 0]
    assert F[u'soa_paren'] == [1, 1, 0, 0] and F[u'soa_case_delta'] == [10, -5, 0, 0]
    assert F[u'dur_hit_total'] == [72, 7, 0, 1] and F[u'dur_distinct'] == [6, 4, 0, 1]
    assert F[u'dur_distinct_close'] == 0

    assert F[u'pair_share'] == [117, 3, 0, 1, 0, 0] and F[u'pair_byte'] == [114, 0, 0, 0, 0, 0]
    assert F[u'pair_norm_only'] == [3, 3, 0, 1, 0, 0] and F[u'pair_close'] == 0
    assert F[u'pair_nonzero'] == 3 and F[u'tri_share'] == [0, 0, 0, 0]
    assert F[u'pool_4'] == 0 and F[u'share4_byte4'] == F[u'share4_notbyte'] == 0
    assert F[u'share4_axis_close'] == 0 and F[u'share4_diff'] == []
    assert F[u'set_sizes'] == [1185, 1131, 283, 459] and F[u'union_all'] == 2937
    assert F[u'only_each'] == [1065, 1013, 279, 459] and F[u'union_close'] == 0
    assert F[u'pool_n'] == 2625 and F[u'pool_tier'] == [2577, 48, 0, 0]
    assert F[u'pool_tier_close'] == 0 and F[u'pool_1'] == 2577 and F[u'pool_2'] == 48
    assert (F[u'pool_share1_1034'] + F[u'pool_share1_1035'] + F[u'pool_share1_1536']
            + F[u'pool_share1_2181']) == F[u'pool_1']
    assert F[u'pool_share2_ab'] == 44 and F[u'pool_2'] == 48 and F[u'pool_3'] == F[u'pool_4'] == 0
    assert F[u'apool_1'] + F[u'apool_2'] + F[u'apool_3'] + F[u'apool_4'] == F[u'apool_n']
    assert sum(F[u'apool_tag_n']) == F[u'apool_n']
    assert F[u'x_ident_n'] == len(ZID) == 49
    assert F[u'scalar_clos_sum'] == 0 and F[u'list_clos_n'] == 15

    assert F[u'cat_std'] == [0, 0, 0, 1] and F[u'std_hdr'] == [0, 0, 0, 0]
    assert F[u'upd_hdr'] == [0, 0, 0, 1] and F[u'bcp_hdr'] == [0] * 4
    assert F[u'obs_hdr'] == [1, 1, 0, 0] and F[u'issn_hdr'] == [0] * 4
    assert F[u'req_rc'] == [1, 1, 1, 1] and F[u'u_required'] == [0] * 4
    assert F[u'lit_std13_ttl'] == [0, 0, 0, 1] and F[u'fold_std13_ttl'] == [0, 0, 0, 1]
    assert F[u'delta_std13_ttl'] == [0] * 4 and F[u'std13_AB_close'] == 0
    assert F[u'cite_1034'] == [54, 0, 4, 9] and F[u'cite_1035'] == [0, 54, 5, 5]
    assert F[u'cite_1536'] == [0, 0, 11, 0] and F[u'cite_2181'] == [0, 0, 0, 14]
    assert F[u'cite_self'] == [F[u'hdr'][i] + F[u'selfcite_ledger'][i] for i in range(4)]
    assert F[u'selfcite_ABC'] == 0 and F[u'selfcite_ledger'] == [0] * 4
    assert F[u'brf'] == [39, 39, 0, 14] and F[u'self_ref'] == [77, 72, 0, 0]
    assert F[u'dns_family'] == [F[u'cite_1034'][i] + F[u'cite_1035'][i] for i in range(4)]
'''

ANCH = u'''
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B68_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6([' + u''.join(TAGS) + u'])\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B68: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B68: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B68: 标签嵌套'
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
    assert F[u'anchor_all4'] == 0 and F[u'pool_4'] == 0, u'B68: 归一后四份同现的长行为零, 不该有四源锚'
    AB = set(bis_iset(GN[0], GN[1]))
    AX = [a for h, a in zip(HC, DIS) if len(h) > 1]
    assert F[u'anchor_cross'] == len(AX) == 2 and all(pnorm(a) in AB for a in AX)
    assert F[u'anchor_single'] == len(DIS) - 2
    return F

_B68 = _b68_scan()
B68V = lambda k, i=None: (_B68[k] if i is None else _B68[k][i])
'''

FLAT = json.load(io.open(u'corpus/_b68flat.json', encoding='utf-8'))
BLK = HEAD + BODYTXT + HAND + gen_asserts(FLAT) + ANCH
compile(BLK, u'<b68 block>', 'exec')

assert S.count(NL + u'_B65 = _b65_scan()') == 1, u'anchor _b65_scan'
i0 = S.find(u'# B68: 一条 RR 的 TTL 上限到底是多少')
while i0 >= 0:
    i1 = S.index(u'_B65 = _b65_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B68: 一条 RR 的 TTL 上限到底是多少')
if u'B68V=B68V,' in S:
    S = S.replace(u'B68V=B68V,' + NL, NL)
S = S.replace(NL + u'_B65 = _b65_scan()', BLK + NL + u'_B65 = _b65_scan()')
# 并行 agent 可能已把别的条目接在 env 尾巴上, 所以按"参数表右括号前插一枚"来做, 且已存在就跳过
if u'B68V=B68V' not in S:
    ME = re.search(u'B64V=B64V((?:,\\s*\\w+=\\w+)*)\\)', S)
    assert ME, u'anchor env'
    S = S[:ME.end(1)] + u',\n               B68V=B68V' + S[ME.end(1):]

PS = u"SRC['B65'] = ["
blk = (u"SRC['B68'] = ['corpus/raw/dnsTTL/rfc1034.txt', 'corpus/raw/dnsTTL/rfc1035.txt', "
       u"'corpus/raw/dnsTTL/rfc1536.txt', 'corpus/raw/dnsTTL/rfc2181.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
# 只加进 ATOM(锚比对集), 不加进 HTMLSRC——四份都是纯文本面, 没有壳⇎面两口径
if u"'B68'" not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B68'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B68'" + S[m.end(1):]

M1 = u'# ---- B68 DERIV (generated by corpus/_wire68.py from corpus/_deriv68.json; do not hand-edit) ----'
M2 = u'# ---- /B68 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o4 = u'# ---- B65 DERIV (generated by corpus/_wire65.py'
assert S.count(o4) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv68.json', encoding='utf-8'))
S = S.replace(o4, M1 + NL + u"DERIV['B68'] = " + repr(J) + NL + M2 + NL + o4)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B68': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b68 block>', 'exec'), NS)
env = NS['B68V']
BAD, MISMATCH = [], []


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
        got = eval(v, dict(NS), {'B68V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b65_scan' in S and u'_b68_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b68_scan+B68V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
