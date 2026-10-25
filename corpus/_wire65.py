# -*- coding: utf-8 -*-
"""把 B65 的独立复算器(_b65_scan / B65V)接进 audit.py, 并生成 DERIV['B65']。
幂等: 重复运行先摘旧块再插新块。
_b65_scan 的量测段从 corpus/_mkB65.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自五处:
①采集侧 corpus/_pick65.py 是先于建条目写好的另一套实现(它用正则族扫义务词与字面针、用集合运算求整行搬运交集、
  按“AT MOST|more than”正则读上限数字), 两边在 275 个口径一致的键上逐量对账(四份都是 RFC Editor 纯文本面,
  无需按介质分流; 现况 275 采集键／不符 0／采集侧独有 0 键＋1 项声明), 建条目侧改立游标档与逐字符形状档, 不复用其正则;
②抽出的代码在插门之前要把 _b65flat.json 的每个键与 DERIV['B65'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按归一串判成员;
④数字读数一律从面内现读: 上限 2 由两句各自的主线针内游标解析("AT MOST " ⇎ "more than " 之后连读数字),
  不是手填; 撤数那两份读作 0 枚给数并对四份做账(给数份数+撤数份数=4); 窗长、窗起行、窗止行由正文标题行现定位后按行切;
  页眉两档、页脚、换页符、点线目录行、BOM 与码位清单都从字节面逐字符数出; 表外常数只有 40 字符/55 字符这类口径阈值;
⑤宣称⇎复算是门可算的量: 97⇎99 同为一枚 2 却挂在极性相反的义务句式下(两式在自己面内互为零命中),
  14⇎22 的撤数句逐字同现而紧跟其后的论证段各写各的, 超时句拼写在四份里恰好各落一档(time-out ⇎ timeout),
  这类差只能由复算给出, 必须进门槛而不是只进注。DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB65.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/httpKA/rfc2068.txt', u'corpus/raw/httpKA/rfc2616.txt',
        u'corpus/raw/httpKA/rfc7230.txt', u'corpus/raw/httpKA/rfc9112.txt']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'# --- SCAN BEGIN ---', u'# --- SCAN END ---')
MEAS = MEAS[MEAS.index(NL) + 1:]
assert u'RAWB' in MEAS and u'POOL' in MEAS and u'ZID' in MEAS
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
assert u'pnorm' in MEAS and u'FAN' in MEAS and u'bisect_left' in MEAS
assert u'window(' in MEAS and u'sn_fold_docs' in MEAS and u'sn_strict_docs' in MEAS
assert u'rfcnum_at' in MEAS and u'ceil_close' in MEAS and u'hdr_sp_line' in MEAS

HEAD = u'''
# B65: 同一个客户端对同一台服务器最多该同时开几条连接——四份 RFC Editor 纯文本四种答法:
# raw/httpKA/rfc2068.txt(A 97 最多二: HTTP/1.1 第一版, 上限写成 "SHOULD maintain AT MOST 2",
#   同一节还留代理乘法式 "up to 2*N connections"; 超时句写作带连字符的 time-out)
# ⇎ rfc2616.txt(B 99 不得超: 收掉同一个 2 却把句式翻成 "SHOULD NOT maintain more than 2",
#   并在超时句里插进 "(or existence)"; 抬头 Obsoletes: 2068)
# ⇎ rfc7230.txt(C 14 撤上限: 明文撤数 "does not mandate a particular maximum",
#   在变更附录里宣告 "The limit of two connections per server has been removed",
#   代理乘法句整段删除, 拼写换成不带连字符的 timeout, 并把 §8.1.4 拆成 §6.4 Concurrency ⇎ §6.5 Failures and Timeouts)
# ⇎ rfc9112.txt(D 22 同句撤: 逐字收下 C 的撤数句而重写紧跟其后的论证段(大 payload ⇎ very large content),
#   把重试条件推给兄弟规范 "Section 9.2.2 of [HTTP]"(具名引用 79 处而三份皆 0), 挂 STD: 99 而不再写 Obsoletes;
#   四份里唯一没有页眉/页脚/换页符/点线目录的一份, 也是唯一带 UTF-8 BOM 与一枚 U+00FC 的一份)。
# 本函数从四份字节独立复算: 逐字符形状档(行⇎非空行⇎仅 ASCII 空白档⇎换页独占档四本账), 句内游标档解析上限数字,
# 窗口档先定位正文标题行再按行切(窗起/窗止/窗长/窗内⇎窗外义务词), 严格档⇎折平档两把针尺,
# 大写义务⇎小写词界两档, 引用网(2068⇎2616⇎7230⇎7231⇎9110⇎9112⇎2119⇎2145⇎7235 各被谁引),
# 整行搬运的归一⇎逐字节两把尺与四源长行容斥, 锚候选池按逐字再现份数四层划分。
# 52 条由面内现读数构成的恒等式(2=2、给数 2 份+撤数 2 份=4 份、窗内+窗外=全篇 MUST⇎SHOULD⇎MAY、
# 严格档 3 枚+折平差=容行档读数、页眉+页脚=页壳行、字节−码位差=BOM 3+变音符 1、两把搬运尺相加=整行交集)全归零送门槛重算。
# 不可由在库文件判定的: 四份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 各家浏览器对同一域名实际同时开几条连接、现网服务器把空闲超时配成多少秒——只进解读注, 不进门槛。
def _b65_scan():
    import hashlib as _hl
    from bisect import bisect_left
    P2 = SRC['B65']
    NSRC = 4
    TAGS = [u'A', u'B', u'C', u'D']
    LB = dict(zip(TAGS, [u'97 最多二', u'99 不得超', u'14 撤上限', u'22 同句撤']))
    PATH = P2
    IDX = dict((t, i) for i, t in enumerate(TAGS))
    NL = chr(10)
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
for a, b in ((u'hashlib.', u'_hl.'),):
    BODYTXT = re.sub(u'(?<![.\\w])' + re.escape(a), b, BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert u'_hl.blake2b' in BODYTXT and u'bisect_left(' in BODYTXT

ANCHORK = {u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single',
           u'anchor_cross', u'anchor_all4', u'checks', u'tag_A', u'tag_B', u'tag_C', u'tag_D'}
FAM = [u'bytes', u'chars', u'lines', u'nonblank', u'nb_gap', u'ff_only', u'maxlen', u'trail', u'cr',
       u'nonascii', u'bom', u'formfeed', u'sig', u'enc_', u'bc_', u'hdr', u'foot', u'pg', u'page',
       u'toc', u'shell', u'd_shell', u'ceil', u'pol_', u'a_ceil', u'b_ceil', u'ans_', u'sec',
       u'secw_', u'outw_', u'u_', u'lo_', u'oblig', u'rfc2119', u'cite', u'lit_', u's_', u'wrap',
       u'sn_', u'wrapgap_', u'gen_', u'grace', u'idem', u'hyb', u'v_', u'num_lines', u'pool',
       u'apool', u'x_ident', u'scalar', u'list_clos', u'y_', u'share', u'union', u'only', u'abcd',
       u'hol', u'cat_', u'obs', u'upd', u'std_', u'bcp', u'issn', u'req_rc', u'in_scope',
       u'ise', u'retry', u'rem_', u'srvto', u'srv_side', u'tline', u'side', u'abortedseq',
       u'seqidem', u'selfcite', u'proxy', u'keepa', u'win_close']


def fam(k):
    for i, f in enumerate(FAM):
        if k.startswith(f) or (f + u'_') in k:
            return i
    return len(FAM)


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


HAND = u'''    # ---- 结构性自检: 两式极性对、句内游标上限、窗口内外账、严格⇎折平两把尺、世代拼写、版式四账、搬运容斥 ----
    assert F[u'a_ceil'] == F[u'b_ceil'] == 2 and F[u'ceil_close'] == 0
    assert F[u'ceil_docs'] == [1, 1, 0, 0] and F[u'nomandate_docs'] == [0, 0, 1, 1]
    assert F[u'ceil_docs_n'] + F[u'nomandate_docs_n'] == F[u'ceil_nomandate_ledger'] + NSRC == 4
    assert F[u'pol_a'] == [1, 0, 0, 0] and F[u'pol_b'] == [0, 1, 0, 0]
    assert F[u'pol_own'] == [F[u'pol_a'][i] + F[u'pol_b'][i] for i in range(4)] == [1, 1, 0, 0]
    assert F[u'pol_cross_ab'] == F[u'pol_cross_ba'] == F[u'pol_cross_close'] == 0
    assert F[u'lit_two_both'] == [F[u'lit_atmost2'][i] + F[u'lit_more2'][i] for i in range(4)]
    assert F[u'ans_gap'] == [0] * 4 and F[u'ans_line_n'] == F[u'ans_lit_present'] == F[u'ans_fold_present']
    assert F[u'ans_line_close'] == 0
    assert all(F[u'sec_a'][i] <= F[u'ans_line_' + t.lower()][0] <= F[u'sec_b'][i]
               for i, t in enumerate(TAGS)), u'上限句不在自己窗内'

    assert F[u'sec_head'] == [u'8.1.4 Practical Considerations', u'8.1.4 Practical Considerations',
                              u'6.4.  Concurrency', u'9.4.  Concurrency']
    assert F[u'sec_len'] == [2568, 2724, 1054, 1351] and min(F[u'sec_len']) == 1054
    assert F[u'sec_keys'] == [1, 1, 2, 2] and F[u'sec_keys_ledger'] == 0
    assert F[u'sec_pair_close'] == [0] * 4
    assert F[u'secw_atmost'] == [1, 0, 0, 0] and F[u'secw_nomandate'] == [0, 0, 1, 1]
    assert F[u'secw_lit_pn'] == [1, 1, 0, 0] and F[u'lit_pn'] == F[u'secw_lit_pn']
    assert F[u'main6_fold'] == [2, 2, 3, 3] and F[u'sn_other_fold'] == [6, 6, 8, 8]
    assert [F[u'main6_fold'][i] + F[u'sn_other_fold'][i] for i in range(4)] == F[u'sn_fold_docs']
    for w in (u'must', u'should', u'may'):
        assert [F[u'secw_' + w][i] + F[u'outw_' + w][i] - F[u'u_' + w][i]
                for i in range(4)] == [0] * 4
        assert F[u'win_close_' + w] == [0] * 4
    assert F[u'must_win_close_sum'] == 0
    assert F[u'secw_ought'] == [0, 0, 1, 1] and F[u'outw_ought'] == [1, 13, 20, 10]

    assert F[u'oblig_up'] == [F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i] for i in range(4)]
    assert F[u'oblig_low'] == [F[u'lo_must'][i] + F[u'lo_should'][i] + F[u'lo_may'][i] for i in range(4)]
    assert F[u'oblig_up_close'] == F[u'oblig_low_close'] == 0
    assert F[u'oblig_up'][0] > F[u'oblig_up'][3] and F[u'oblig_low'][0] > F[u'oblig_low'][3]
    assert F[u'u_must_not'] == [78, 120, 43, 22] and F[u'u_should_not'] == [22, 42, 13, 6]
    assert F[u'u_required'] == [0, 5, 1, 1] and F[u'u_recommended'] == [0, 1, 2, 3]
    assert F[u'u_may_not'] == [1, 0, 0, 0]

    assert F[u'lit_timeout_h'] == [3, 4, 0, 0] and F[u'lit_timeout_p'] == [0, 0, 4, 4]
    assert F[u'gen_h'] == [1, 1, 0, 0] and F[u'gen_p'] == [0, 0, 1, 1]
    assert F[u'gen_split_close'] == [F[u'gen_h'][i] + F[u'gen_p'][i] - 1 for i in range(4)] == [0] * 4
    assert F[u'lit_plain_in_ab'] == [F[u'lit_timeout_p'][i] - F[u'lit_timeout_h'][i]
                                     for i in range(4)] == [-3, -4, 4, 4]
    assert F[u'lit_orx'] == [0, 1, 0, 0] and F[u'lit_leno'] == [1, 1, 1, 1]
    assert F[u's_tline_h'] == [1, 1, 0, 0] and F[u's_tline_p'] == [0, 0, 1, 1]
    assert F[u'tline_both_docs'] == [1] * 4 and F[u'tline_pair_close'] == [0] * 4
    assert F[u'lit_srvto_h'] == [1, 1, 0, 0] and F[u'lit_srvto_p'] == [0, 0, 1, 1]
    assert F[u'srvto_pair_close'] == [0] * 4

    assert F[u'lit_abortedreq'] == [1, 0, 0, 0] and F[u'lit_abortedseq'] == [0, 1, 0, 0]
    assert F[u'abortedseq_wrap'] == [F[u'lit_abortedseq_fold'][i] - F[u'lit_abortedseq'][i]
                                     for i in range(4)] == [0, 0, 1, 0]
    assert F[u'lit_methodid'] == [1, 0, 0, 0] and F[u'lit_seqidem'] == [0] * 4
    assert F[u'seqidem_wrap'] == F[u'lit_seqidem_fold'] == [0, 1, 0, 0]
    assert F[u'lit_idemhave'] == [0, 0, 2, 1] and F[u'idemhave_ab_close'] == 0
    assert F[u'lit_sec922'] == [0, 0, 0, 2] and F[u'sec922_close'] == 0
    assert F[u'lit_removed2'] == [0, 0, 1, 0] and F[u'rem_decl_close'] == 0
    assert F[u'lit_oughttolimit'] == [0, 0, 2, 2] and F[u'lit_shouldlimit'] == [1, 1, 0, 0]
    assert F[u'lit_sustain'] == [0, 0, 1, 1] and F[u'lit_atleastone'] == [1, 1, 0, 0]

    assert F[u'cd_verdict_same'] == 2 and F[u's_cd_same_fold'] == [0, 0, 1, 1]
    assert F[u'cd_prose_diff'] == 2 and F[u'hol_excl'] == 0
    assert F[u'cd_verdict_same_minus_hol'] == F[u'cd_verdict_same'] - F[u'hol_excl'] - 2 == 0
    assert F[u's_hol_c_fold'] == [0, 0, 1, 0] and F[u's_hol_d_fold'] == [0, 0, 0, 1]
    assert F[u's_hol_fold'] == [F[u's_hol_c_fold'][i] + F[u's_hol_d_fold'][i] for i in range(4)]
    assert F[u's_hol'] == F[u's_hol_fold'] and F[u'lit_payloadblk'] == [0, 0, 1, 0]
    assert F[u'lit_bigcontent'] == [0, 0, 0, 1] and F[u'srv_side_sum'] == [0, 0, 1, 1]
    assert F[u'srv_side_cd_close'] == 0 and F[u'proxy_cd_sum'] == 0
    assert F[u'lit_sidec'] == [0, 0, 1, 0] and F[u'lit_sided'] == [0, 0, 0, 1]
    assert F[u'sidec_wrap'] == [0, 0, 0, 1] and F[u'sided_wrap'] == [0, 0, 1, 0]

    assert F[u'wrap_sn_n'] == 23 and F[u'wrap_sn_hit'] == F[u'wrap_onlyfold_n'] == 17
    assert F[u'wrap_sn_total'] == sum(sum(F[k]) for k in F if k.startswith(u'wrapgap_')) == 26
    assert F[u'wrap_hit_minus_onlyfold'] == F[u'wrap_sn_hit'] - len(F[u'sn_only_fold']) == 0
    assert F[u'sn_strict_docs'] == [3] * 4 and F[u'sn_fold_docs'] == [8, 8, 11, 11]
    for i in range(NSRC):
        assert F[u'sn_strict_docs'][i] + sum(F[u'wrapgap_' + q][i] for q in F[u'sn_only_fold']) \\
            == F[u'sn_fold_docs'][i], i
    assert F[u'wrap_proxy_ab'] == sum(F[u'wrapgap_proxy']) == 2
    assert F[u'lit_graceful'] == [1] * 4 and F[u'grace_docs'] == [1] * 4
    assert F[u's_grace_it_fold'] == [1, 1, 0, 0] and F[u's_grace_that_fold'] == [0, 0, 1, 1]
    assert F[u'grace_pair_close'] == [F[u's_grace_it_fold'][i] + F[u's_grace_that_fold'][i] - 1
                                      for i in range(4)] == [0] * 4
    assert F[u'grace_all_close'] == 0 and F[u'grace_trac_close'] == [0] * 4
    assert F[u's_grace_trac'] == F[u's_grace_trac_fold'] == [1, 1, 0, 0]
    assert F[u'ch_c64'] == [0, 0, 1, 0] and F[u'ch_c64_fold'] == [0, 0, 2, 0]
    assert F[u'ch_d94'] == [0] * 4 and F[u'ch_d94_fold'] == [0, 0, 0, 2]
    assert F[u'ch_fold_eq'] == [0] * 4 and F[u'ch_fold_gain'] == [0, 0, 1, 0]
    assert F[u'hyb_eol'] == [79, 114, 10, 21] and F[u'hyb_cont'] == [39, 75, 8, 14]
    assert all(F[u'hyb_eol'][i] >= F[u'hyb_cont'][i] for i in range(4))

    assert F[u'hdr'] == [161, 175, 88, 0] and F[u'hdr_ns'] == [0] * 4 and F[u'hdr_sp'] == F[u'hdr']
    assert F[u'foot'] == F[u'pg'] == F[u'formfeed'] == F[u'trail'] == F[u'nb_gap'] == F[u'ff_only_lines']
    assert F[u'ff_foot_sum'] == F[u'pg_foot_sum'] == F[u'nb_ff_sum'] == F[u'pagelines_close'] == 0
    assert F[u'pagelines'] == [F[u'hdr'][i] + F[u'foot'][i] for i in range(4)]
    assert F[u'pages_est'] == [max(F[u'hdr'][i], F[u'foot'][i]) for i in range(4)]
    assert F[u'nonblank_asciib'] == [F[u'nonblank'][i] + F[u'nb_gap'][i] for i in range(4)]
    assert F[u'lines_ge40_nos'] == [F[u'lines_ge40'][i] - F[u'shell_delta'][i] for i in range(4)]
    assert F[u'toc_lines'] == [233, 251, 93, 0] and F[u'd_shell_zero'] == 0
    assert F[u'selfcite_ledger'] == [0, 0, 0, 3] and F[u'selfcite_close3'] == sum(F[u'selfcite_ledger'][:3])
    assert F[u'cite_self'] == [F[u'hdr'][i] + F[u'selfcite_ledger'][i] for i in range(4)]
    assert F[u'num_lines'] == [6, 6, 7, 7]
    assert F[u'num_lines'] == [len([1 for l in LST[i] if len(l.strip()) >= 55
                                   and any(x in l for x in NLITS)]) for i in range(NSRC)]

    assert F[u'bom'] == [0, 0, 0, 1] and F[u'nonascii'] == [0, 0, 0, 1]
    assert F[u'nonascii_cp'] == [[], [], [], [u'0xfc']] and F[u'nonascii_cp_close'] == 0
    assert F[u'bc_delta'] == [F[u'bytes'][i] - F[u'chars'][i] for i in range(4)] == [0, 0, 0, 4]
    assert F[u'enc_close'] == [F[u'bc_delta'][i] - 3 * F[u'bom'][i] - F[u'nonascii_utf8_extra'][i]
                               for i in range(4)] == [0] * 4
    assert F[u'bytes'] == [378114, 422279, 205947, 109913]
    assert F[u'lines'] == [9076, 9860, 4988, 2462] and F[u'maxlen'] == [75, 72, 72, 72]
    assert F[u'cr'] == [0] * 4 and F[u'sig_distinct'] == 4

    assert F[u'share_ab'] == F[u'y_ab_byte_shared'] + F[u'y_ab_norm_only'] == 2301
    assert F[u'share_cd'] == F[u'y_cd_byte_shared'] + F[u'y_cd_norm_only'] == 470
    assert F[u'share_cd_delta'] == F[u'share_cd'] - F[u'share_cd_nos'] == 0
    assert F[u'share_ab_nos'] == F[u'share_ab'] and F[u'union_all_nos'] == F[u'union_all'] - 1
    assert F[u'abcd_incl'] == F[u'union_all'] == 8968 and F[u'abcd_close'] == 0
    assert F[u'union_delta'] == F[u'union_all'] - F[u'union_abc'] == F[u'only_d'] == 710
    assert [F[u'share_ad'], F[u'share_bd'], F[u'share_ac'], F[u'share_bc']] == [22, 30, 45, 55]
    assert F[u'pool_1'] + F[u'pool_2'] + F[u'pool_3'] + F[u'pool_4'] == F[u'pool_n'] == 3572
    assert F[u'pool_tier'] == [F[u'pool_%d' % n] for n in (1, 2, 3, 4)] and F[u'pool_tier_close'] == 0
    assert F[u'apool_1'] + F[u'apool_2'] + F[u'apool_3'] + F[u'apool_4'] == F[u'apool_n'] == 16624
    assert sum(F[u'apool_tag_n']) == F[u'apool_n']
    assert (F[u'pool_share1_2068'] + F[u'pool_share1_2616'] + F[u'pool_share1_7230']
            + F[u'pool_share1_9112']) == F[u'pool_1'] == 2328
    assert F[u'pool_share2_ab'] == 989 and F[u'pool_share2_cd'] == 223 and F[u'pool_2'] == 1218
    assert len(F[u'pool_share4']) == F[u'pool_4'] == F[u'share4_byte4'] + F[u'share4_notbyte'] == 6
    assert F[u'share4_byte4'] == 2 and F[u'share4_axis_close'] == 0
    assert [a for a, _ in F[u'share4_diff']] == [u'case', u'hyph', u'space', u'space']
    assert (F[u'share4_axis_case'] == 1 and F[u'share4_axis_hyph'] == 1
            and F[u'share4_axis_space'] == 2 and F[u'share4_axis_multi'] == 0)
    assert F[u'only_a'] == F[u'only_a_nos'] == 1676
    assert F[u'x_ident_n'] == len(ZID) == 53
    assert F[u'scalar_clos_n'] == 17 and F[u'scalar_clos_sum'] == 0 and F[u'list_clos_n'] == 15

    assert F[u'cat_std'] == F[u'req_rc'] == [1] * 4
    assert F[u'obs_hdr'] == [0, 1, 1, 1] and F[u'upd_hdr'] == [0, 0, 1, 0]
    assert F[u'std_hdr'] == [0, 0, 0, 1] and F[u'bcp_hdr'] == [0] * 4
    assert F[u'issn_hdr'] == [0, 0, 1, 1] and F[u'obsoleted_by'] == [1, 1, 0, 1]
    assert F[u'in_scope'] == F[u'ise'] == F[u'lit_asares'] == [0, 0, 1, 1]
    assert F[u'lit_ingeneral'] == [0] * 4
    assert F[u'cite_http_brk'] == [0, 0, 0, 79] and F[u'cite_rfc_brk'] == [0, 1, 154, 35]
    assert F[u'cite_2068'] == [161, 16, 6, 4] and F[u'cite_2616'] == [0, 175, 8, 0]
    assert F[u'cite_7230'] == [0, 0, 88, 9] and F[u'cite_7231'] == [0, 0, 38, 0]
    assert F[u'cite_9110'] == [0, 0, 0, 2] and F[u'cite_9112'] == [0, 0, 0, 3]
    assert F[u'rfc2119_ref'] == [0, 3, 3, 6] and F[u'cite_2119'] == [0, 3, 3, 4]
    assert F[u'v_proxy'] == [95, 126, 69, 24] and min(F[u'v_proxy']) == F[u'v_proxy'][3]
    assert F[u'v_retransmit'] == [2, 2, 1, 0] and F[u'lit_retrydef'] == [0, 0, 0, 1]
    assert F[u'retrydef_close'] == F[u'retry_form_close'] == 0
    assert F[u'v_idem'] == [2, 11, 7, 2] and F[u'lit_seqretry'] == F[u'lit_retransseq'] == [0, 0, 1, 0]
    assert F[u'idem_cd_n'] == F[u'lit_idemhave'][2] + F[u'lit_idemhave'][3] == 3
    assert F[u'v_timeoutw'] == [0, 0, 4, 4] == F[u'lit_timeout_p']
    assert F[u'v_browser'] == [2, 3, 8, 2] and F[u'v_congest'] == [5, 5, 1, 2]
    assert F[u'lit_congnet'] == [0, 0, 1, 1] and F[u'lit_avoidcong'] == [1, 0, 0, 0]
    assert F[u'v_client'] == [278, 310, 146, 108] and F[u'v_server'] == [534, 569, 208, 119]
    assert F[u'lit_keepa_upper'] == [20, 8, 5, 4] and F[u'lit_keepa_lower'] == [0, 0, 5, 4]
    assert F[u'keepa_ab_lower_zero'] == 0 and F[u'lit_closeopt'] == [3, 3, 18, 16]
    assert F[u'lit_msghttp'] == [4, 5, 11, 12] and F[u'lit_apchttp'] == [0, 4, 6, 6]
'''

ANCH = u'''
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B65_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6([' + u''.join(TAGS) + u'])\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B65: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B65: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B65: 标签嵌套'
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
    assert F[u'anchor_all4'] == 1, u'B65: 归一后四份同现的锚应当恰有一枚(超时值那句, 原面按 time-out⇎timeout 分家)'
    P4 = set(F[u'pool_share4'])
    A4 = [a for h, a in zip(HC, DIS) if len(h) == NSRC]
    assert [a for ax, a in F[u'share4_diff'] if ax == u'hyph'] == [pnorm(A4[0])]
    assert all(pnorm(a) in P4 for a in A4)
    return F

_B65 = _b65_scan()
B65V = lambda k, i=None: (_B65[k] if i is None else _B65[k][i])
'''

FLAT = json.load(io.open(u'corpus/_b65flat.json', encoding='utf-8'))
BLK = HEAD + BODYTXT + HAND + gen_asserts(FLAT) + ANCH
compile(BLK, u'<b65 block>', 'exec')

assert S.count(NL + u'_B64 = _b64_scan()') == 1, u'anchor _b64_scan'
B65ENV = u'B64V=B64V,' + NL + u'               B65V=B65V)'
i0 = S.find(u'# B65: 同一个客户端对同一台服务器最多该同时开几条连接')
while i0 >= 0:
    i1 = S.index(u'_B64 = _b64_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B65: 同一个客户端对同一台服务器最多该同时开几条连接')
if B65ENV in S:
    S = S.replace(B65ENV, u'B64V=B64V)')
S = S.replace(NL + u'_B64 = _b64_scan()', BLK + NL + u'_B64 = _b64_scan()')
# 并行 agent 可能已把 B67V 之类接在 env 尾巴上, 所以按"参数表右括号前插一枚"来做, 且已存在就跳过
if u'B65V=B65V' not in S:
    ME = re.search(u'B64V=B64V((?:,\\s*\\w+=\\w+)*)\\)', S)
    assert ME, u'anchor env'
    S = S[:ME.end(1)] + u',\n               B65V=B65V' + S[ME.end(1):]

PS = u"SRC['B64'] = ["
blk = (u"SRC['B65'] = ['corpus/raw/httpKA/rfc2068.txt', 'corpus/raw/httpKA/rfc2616.txt', "
       u"'corpus/raw/httpKA/rfc7230.txt', 'corpus/raw/httpKA/rfc9112.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B63', 'B64'}", u"'B63', 'B64', 'B65'}"
# 只加进 ATOM(锚比对集), 不加进 HTMLSRC——四份都是纯文本面, 没有壳⇎面两口径
if NEW not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B65'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B65'" + S[m.end(1):]

M1 = u'# ---- B65 DERIV (generated by corpus/_wire65.py from corpus/_deriv65.json; do not hand-edit) ----'
M2 = u'# ---- /B65 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o4 = u'# ---- B64 DERIV (generated by corpus/_wire64.py'
assert S.count(o4) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv65.json', encoding='utf-8'))
S = S.replace(o4, M1 + NL + u"DERIV['B65'] = " + repr(J) + NL + M2 + NL + o4)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B65': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b65 block>', 'exec'), NS)
env = NS['B65V']
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
        got = eval(v, dict(NS), {'B65V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b64_scan' in S and u'_b65_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b65_scan+B65V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
