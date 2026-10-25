# -*- coding: utf-8 -*-
"""把 B64 的独立复算器(_b64_scan / B64V)接进 audit.py, 并生成 DERIV['B64']。
幂等: 重复运行先摘旧块再插新块。
_b64_scan 的量测段从 corpus/_mkB64.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自五处:
①采集侧 corpus/_pick64.py 是先于建条目写好的另一套实现(它用 re.match 逐行切表、用 (\\d+)\\s*secs?
  成对读 OLD:/NEW: 的旧值新值、以集合运算求搬运交集、按正则族数义务词与引用), 两边在 242 个口径
  一致的键上逐量对账(四份都是 RFC Editor 纯文本面, 无需按介质分流; 现况 265 采集键／不符 0,
  采集侧独有的 23+3 键是它自己的 sha256 档、答数行号档与逐份引用⇎块数档, 建条目侧改立 blake2b、
  规范窗⇎窗外与逐字符形状口径, 不共用键名);
②抽出的代码在插门之前要把 _b64flat.json 的每个键与 DERIV['B64'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按归一串判成员;
④数字读数一律从面内现读: 四枚答数由各自主线的“数字+单位”游标档解出(97 散文／03 表行／13 的 NEW: 行／
  18 的竖线格), 97 的退避序列由首值现读后翻倍仿真至封顶(4→8→16→32→64 秒), 夹逼上下界从 13⇎18 的
  “60 <= "value" <= 86400”式两侧现读, 手填常数为零; 表行切分先按 '|' 分格再按字符类, 于是 03 的 24 行⇎
  18 的 28 行、四枚同名换值(REL/DEC_MAX_RC 由 5→4 是 18 自改, 13 通篇没提)都是可判口径;
⑤宣称⇎复算是门可算的量: 13 声称只动两枚参数, 18 落地的同名对照里有四枚变了值, 提案比值 30 ⇎ 表间比值 30
  闭合, 而 97 的 64 秒既是答数又是翻倍序列的末项(末项÷首项=16=2^4)。这类差只能由复算给出, 必须进门槛而不是只进注。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB64.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/dhcp/rfc2131.txt', u'corpus/raw/dhcp/rfc3315.txt',
        u'corpus/raw/dhcp/rfc7083.txt', u'corpus/raw/dhcp/rfc8415.txt']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'# --- SCAN BEGIN ---', u'# --- SCAN END ---')
MEAS = MEAS[MEAS.index(NL) + 1:]
assert u'F[u' in MEAS and u'POOL' in MEAS and u'ZID' in MEAS and u'abcd_close' in MEAS
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
assert u'FAN' in MEAS and u'ATOMSEL' in MEAS and u'pnorm' in MEAS
assert u'dur_near' in MEAS and u'dur_tagged' in MEAS and u'shape' in MEAS
assert u'y_ans_ms' in MEAS and u'a_seq_ms' in MEAS and u'dur_after' in MEAS

HEAD = u'''
# B64: 报文没人应答时重传退避封顶多久——四份 RFC Editor 纯文本四种答法:
# raw/dhcp/rfc2131.txt(A 97 六十四: DHCPv4 协议正文, 答数埋在散文里 "up to a maximum of 64 seconds",
#   同段先给首枚延时 4 秒再要求每次翻倍, 64 因而只能由翻倍仿真(4→8→16→32→64)复算出来;
#   T2 缺省式 "0.875 * duration_of_lease" 被排版劈在两行, 原面读不到该字面)
# ⇎ rfc3315.txt(B 03 一百二: DHCPv6 的 §5.5 参数表给 SOL_MAX_RT 120 secs, 客户端无从改变;
#   全文“120 secs”只两枚, 恰是 SOL ⇎ INF 两行)
# ⇎ rfc7083.txt(C 13 倍三十: 只谈这一枚参数, 把 03 的同一行用 OLD:/NEW: 重印一遍改成 3600 secs(比值 30),
#   另开出可下发的选项、值域 60..86400; 9 枚 OLD:/NEW: 标签里两对带秒数、两对只是散文块界)
# ⇎ rfc8415.txt(D 18 可下发: 收下 C 的选项与越界丢弃句, 缺省接成 3600 secs(竖线表格),
#   同时把 C 从未提过的 REL/DEC_MAX_RC 从 5 改成 4; 独有两句: 值要留住 ⇎ 只在触发它的接口生效)。
# 本函数从四份字节独立复算: 逐字符形状档(行⇎非空行⇎仅 ASCII 空白档⇎换页独占档四本账), 游标档读“数字+单位”,
# 表格先按 '|' 分格再按字符类(块数⇎行数⇎同名对照⇎未提案改动), OLD:/NEW: 标签配对档, 夹逼句逐行三档对照,
# 翻倍序列仿真⇎答数末项闭合, 时长归一毫秒并标跨行旗, 规范窗⇎窗外的搬家账, 原面逐字面⇎空白折平两档之差,
# 归一⇎逐字节两把搬运尺与四源长行容斥, 引用网(2131⇎3315⇎7083⇎8415 各被谁引), 锚候选池按逐字再现份数四层划分。
# 27 条由面内现读数构成的恒等式(3600000=56×64000+16000、3600000=30×120000、64000=4000×16、
# 86400=1440×60、同+异=21、页眉两档=页眉总数)全归零送门槛重算。
# 不可由在库文件判定的: 四份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 各家客户端把 SOL_MAX_RT 实际记多久、现网 DHCP 服务器下发的真实值域——只进解读注, 不进门槛。
def _b64_scan():
    import hashlib as _hl
    import os as _os
    P2 = SRC['B64']
    NSRC = 4
    TAGS = [u'A', u'B', u'C', u'D']
    LB = dict(zip(TAGS, [u'97 六十四', u'03 一百二', u'13 倍三十', u'18 可下发']))
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
assert u'_hl.blake2b' in BODYTXT

ANCHORK = {u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single',
           u'anchor_cross', u'anchor_all4', u'checks', u'tag_A', u'tag_B', u'tag_C', u'tag_D'}
FAM = [u'bytes', u'chars', u'lines', u'nonblank', u'nb_gap', u'ff_only', u'maxlen', u'trail', u'cr',
       u'nonascii', u'bom', u'formfeed', u'rec_close', u'sig', u'hdr', u'foot', u'pg', u'page',
       u'lines_ge40', u'shell', u'y_ans', u'y_a_', u'a_', u'y_cd', u'y_bc', u'y_db', u'tbl', u'bd_',
       u'pv_', u'on_', u'clamp', u'al_', u'y_clamp', u'y_ignore', u'y_must_ignore', u'lit_',
       u'durms', u'durlit', u'dur_', u'y_dur', u'y_unit', u'unit_', u's_', u'wrap', u'n_', u'u_',
       u'l_', u'oblig', u'rfc2119', u'cite', u'y_cite', u'cat_', u'obs', u'upd', u'obsoleted',
       u'issn', u'req_rc', u'sec', u'outw', u'num_lines', u'share', u'union', u'only', u'abcd',
       u'y_bd', u'pool', u'x_ident', u'scalar', u'list_clos']


def fam(k):
    for i, f in enumerate(FAM):
        if k.startswith(f) or (f + u'_') in k:
            return i
    return len(FAM)


def lit(v):
    return repr(v).replace(u'u+', u'')


def gen_asserts(FLAT):
    ks = sorted([k for k in FLAT if k not in ANCHORK], key=lambda k: (fam(k), k))
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


HAND = u'''    # ---- 结构性自检: 四答的载体、表行账、提案⇎落地、翻倍仿真、窗⇎窗外搬家、版式四账、搬运容斥 ----
    assert F[u'y_ans_ms'] == [64000, 120000, 3600000, 3600000]
    assert F[u'y_ans_s'] == [x // 1000 for x in F[u'y_ans_ms']] == [64, 120, 3600, 3600]
    assert F[u'y_ans_distinct'] == 3 and F[u'y_ans_wrap'] == [0] * 4
    assert F[u'y_ans_ratio'] * F[u'y_ans_min'] + F[u'y_ans_rem'] == F[u'y_ans_max'] == 3600000
    assert F[u'cap_ratio_d_b'] == F[u'y_ans_ms'][3] // F[u'y_ans_ms'][1] == 30
    assert F[u'a_cap_ratio_d_b'] == F[u'y_ans_ms'][3] // F[u'y_ans_ms'][0] == 56 == F[u'y_ans_ratio']
    assert F[u'a_seq_ms'] == [x * 1000 for x in F[u'a_seq']] == [4000, 8000, 16000, 32000, 64000]
    assert F[u'a_seq'][0] * 2 ** F[u'a_doublings'] == F[u'a_seq'][-1] == F[u'y_ans_s'][0]
    assert F[u'a_seq_n'] == F[u'a_doublings'] + 1 == 5 and F[u'a_ratio'] == 2 ** F[u'a_doublings'] == 16
    assert F[u'y_a_first'] == F[u'a_seq_ms'][0] and F[u'y_a_next'] == F[u'a_seq_ms'][1] == 8000
    assert F[u'y_a_first'] * F[u'a_ratio'] == F[u'y_ans_ms'][0]
    assert F[u'y_bc_ans_gap'] == F[u'y_ans_ms'][1] - F[u'y_ans_ms'][0] == 56000
    assert F[u'y_db_ans_gap'] == F[u'y_ans_ms'][3] - F[u'y_ans_ms'][1] == 3480000
    assert F[u'y_db_ans_gap'] // F[u'y_ans_ms'][1] == 29 and F[u'y_ans_ms'][3] == 30 * F[u'y_ans_ms'][1]

    assert F[u'tbl_n'] == [0, 1, 0, 1] and F[u'tbl_rows'] == [[], [24], [], [28]]
    assert F[u'tbl_row_delta'] == F[u'tbl_rows_0'][3] - F[u'tbl_rows_0'][1] == 4
    assert F[u'tbl_start'] == [[], [851], [], [1471]]
    assert F[u'bd_n'] == len(F[u'bd_diff']) + F[u'bd_same'] == 4 + 17 == 21
    assert F[u'bd_unproposed_n'] == 2 and F[u'bd_diff'][2:] == [[u'REL_MAX_RC', 5, 4], [u'DEC_MAX_RC', 5, 4]]
    assert len([x for x in F[u'bd_diff'] if x[2] // x[1] == 30]) == 2
    assert F[u'bd_ratio'].count(30) == 2 and F[u'bd_ratio'].count(1) == F[u'bd_same'] == 17
    assert F[u'pv_sol_max_rt'] == [[], [120], [], [3600]] and F[u'pv_inf_max_rt'] == [[], [120], [], [3600]]
    assert F[u'lit_s120'] == [0, 2, 2, 0] and F[u'secw_s120'] == F[u'lit_s120']
    assert F[u'outw_s120'] == [0] * 4 and F[u'lit_s3600'] == [0, 0, 2, 2] == F[u'secw_s3600']

    assert F[u'on_n_c'] == 9 and F[u'on_n_a'] == F[u'on_n_b'] == F[u'on_n_d'] == 0
    assert F[u'on_pair_c'][:2] == [[u'SOL_MAX_RT', 120, 3600, 3], [u'INF_MAX_RT', 120, 3600, 3]]
    assert [p[0] for p in F[u'on_pair_c']] == [u'SOL_MAX_RT', u'INF_MAX_RT', u'MUST', u'MUST']
    assert F[u'on_span'] == sum(p[3] for p in F[u'on_pair_c']) == 22
    assert F[u'on_changed_n'] == len(F[u'on_changed']) == 2 and F[u'on_ratio'] == [30, 30]
    assert F[u'on_ratio_cap_close'] == F[u'cap_ratio_d_b'] - F[u'on_ratio'][0] == 0
    assert F[u'lit_oldlbl'] == [0, 0, 4, 0] and F[u'lit_newlbl'] == [0, 0, 5, 0]

    assert F[u'clamp_lo'] == [0, 0, 60, 60] and F[u'clamp_hi'] == [0, 0, 86400, 86400]
    assert F[u'clamp_span'] == F[u'clamp_hi'][2] // F[u'clamp_lo'][2] == 1440
    assert [F[u'secw_v86400'][i] + F[u'outw_v86400'][i] - F[u'lit_v86400'][i]
            for i in range(4)] == [0] * 4
    assert F[u'y_clamp_lit'][2] == F[u'y_clamp_lit'][3] == 2 and F[u'al_n'] == 2
    assert F[u'al_same_bytes'] + F[u'al_punct_only'] + F[u'al_norm_diff'] == F[u'al_n'] == 2
    assert F[u'y_ignore_srt'] == [0, 0, 0, 1] == F[u'y_ignore_inf']
    assert F[u'y_must_ignore_n'][3] == 11 and F[u'y_must_ignore_n'][3] - F[u'lit_ignore'][3] == 0
    assert F[u'lit_retain'] == [0, 0, 0, 1] and F[u'lit_iface'] == [0, 0, 0, 2]
    assert F[u'lit_retain'][2] == F[u'lit_iface'][2] == 0

    assert F[u'dur_ms_lo'] == 1000 and F[u'dur_ms_hi'] == 86400000
    assert F[u'dur_ms_hi'] // F[u'dur_ms_lo'] == 86400 and F[u'dur_rem'] == [0]
    assert F[u'durms_n_a'] + F[u'durms_n_b'] + F[u'durms_n_c'] + F[u'durms_n_d'] == 23
    assert F[u'y_dur_win_n'] == [len(x) for x in F[u'y_dur_win']] == [3, 7, 2, 9]
    assert F[u'y_dur_out_n'] == [len(x) for x in F[u'y_dur_out']] == [1, 1, 1, 3]
    assert F[u'y_dur_wrap'] == [1, 0, 0, 0] and F[u'y_dur_wrap_ms'][0] == [4000]
    assert F[u'y_unit_n'] == [len(x) for x in F[u'y_unit_used']] == [1, 3, 2, 3]

    assert F[u'wrap_sn_n'] == 11 and F[u'wrap_pin_n'] == 6
    assert F[u'wrap_sn_total'] == F[u'wrapgap_max64sp'][0] + F[u'wrapgap_retainfull'][3] + 0 == 2
    assert F[u'wrap_sn_hit'] == 2
    assert F[u's_max64sp'] == [0, 0, 0, 0] and F[u's_max64full'] == [1, 0, 0, 0]
    assert F[u's_max64sp_fold'][0] == F[u's_max64full'][0] == 1
    assert F[u's_retainfull'] == [0, 0, 0, 0] and F[u's_retainfull_fold'][3] == F[u'lit_retain'][3] == 1
    assert F[u'wrap_total'] == F[u'wrap_userval'][0] == F[u'wrap_pin_hit'] == 1
    assert F[u'lit_durdef875'] == [0] * 4 and F[u'lit_durdef875_fold'] == [1, 0, 0, 0]
    assert F[u'lit_durdef875_gap_sum'] == sum(F[u'lit_durdef875_gap']) == 1

    assert F[u'u_must'] == [118, 136, 15, 220] and F[u'oblig_up'] == [F[u'u_must'][i] + F[u'u_should'][i]
                                                                     + F[u'u_may'][i] for i in range(4)]
    assert F[u'oblig_low'] == [F[u'l_must'][i] + F[u'l_should'][i] + F[u'l_may'][i] for i in range(4)]
    assert F[u'y_oblig_win'] == [F[u'y_secw_must'][i] + F[u'y_secw_should'][i] + F[u'y_secw_may'][i]
                                 for i in range(4)] == [28, 0, 0, 0]
    assert [F[u'y_secw_must'][i] + F[u'y_outw_must'][i] - F[u'u_must'][i] for i in range(4)] == [0] * 4
    assert F[u'sec_hit'] == [1] * 4 and F[u'sec_len'] == [8944, 1583, 970, 5162]
    assert F[u'sec_w'] == [[F[u'sec_a'][i], F[u'sec_b'][i]] for i in range(4)]
    assert F[u'sec_len'][0] > F[u'sec_len'][3] > F[u'sec_len'][1] > F[u'sec_len'][2]
    assert F[u'sec_len_a'] == F[u'sec_len'][0] and F[u'sec_len_d'] == F[u'sec_len'][3]
    assert F[u'outw_solmaxrt'] == [0, 1, 46, 44] and F[u'secw_solmaxrt'] == [0, 1, 4, 1]
    assert [F[u'secw_solmaxrt'][i] + F[u'outw_solmaxrt'][i] - F[u'lit_solmaxrt'][i] for i in range(4)] == [0] * 4
    assert F[u'hdr'] == [44, 100, 6, 153] and F[u'hdr_ns'] == [0] * 4 and F[u'hdr_sp'] == F[u'hdr']
    assert F[u'hdr_ledger_sum'] == sum(F[u'hdr_ledger']) == 0
    assert F[u'foot'] == F[u'pg'] == F[u'formfeed'] == F[u'trail'] == F[u'nb_gap'] == F[u'ff_only_lines']
    assert F[u'ff_foot_sum'] == F[u'pg_foot_sum'] == F[u'nb_ff_sum'] == 0
    assert F[u'nonblank_asciib'] == [F[u'nonblank'][i] + F[u'nb_gap'][i] for i in range(4)]
    assert F[u'lines_ge40_nos'] == [F[u'lines_ge40'][i] - F[u'shell_delta'][i] for i in range(4)]
    assert F[u'pagelines'] == [F[u'hdr'][i] + F[u'foot'][i] for i in range(4)]
    assert F[u'pages_est'] == [max(F[u'hdr'][i], F[u'foot'][i]) for i in range(4)]
    assert F[u'y_self_lit'] == [45, 101, 8, 155] and F[u'num_lines'] == [21, 36, 42, 116]
    assert F[u'num_lines_b'] == F[u'num_lines'][1] and F[u'num_lines'] == [len([1 for l in LST[i]
                                                                               if len(l.strip()) >= 55
                                                                               and any(x in l for x in NLITS)])
                                                                           for i in range(NSRC)]

    assert F[u'share_bd'] == 627 and F[u'y_bd_byte_shared'] == 526
    assert F[u'y_bd_norm_only'] == F[u'share_bd'] - F[u'y_bd_byte_shared'] == 101
    assert F[u'share_cd'] == F[u'y_cd_byte_shared'] == 27 and F[u'y_cd_norm_only'] == 0
    assert F[u'abcd_incl'] == F[u'union_abcd'] == 5621 and F[u'abcd_close'] == 0
    assert F[u'union_abcd'] == F[u'union_abc'] + F[u'union_delta'] == 3206 + 2415
    assert F[u'union_delta'] == F[u'union_abcd'] - F[u'union_abc'] == 2415
    assert F[u'union_abcd_nos'] - F[u'union_abc_nos'] == F[u'union_delta'] == 2415
    assert F[u'only_c'] == 84 and F[u'only_c_nos'] == F[u'only_c']
    assert F[u'pool_1'] + F[u'pool_2'] + F[u'pool_3'] + F[u'pool_4'] == F[u'pool_n'] == 9861
    assert F[u'pool_close'] == 0 and sum(F[u'pool_tag_n']) == F[u'pool_n']
    assert F[u'x_ident_n'] == len(ZID) == 27
    EV = lambda e: eval(e, {u'B64V': lambda k, i=None: (F[k] if i is None else F[k][i])})
    assert [EV(e) for e, _ in ZID] == [0] * F[u'x_ident_n']
    assert F[u'scalar_clos_sum'] == 0 and F[u'list_clos_n'] == 3
'''

TAIL = HAND + gen_asserts(json.load(io.open(u'corpus/_b64flat.json', encoding='utf-8'))) + u'''
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B64_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6([' + u''.join(TAGS) + u'])\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B64: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B64: 有锚没带源标签'
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
    assert F[u'anchor_all4'] == 0, u'B64: 没有一条锚在四份里逐字再现'
    return F

_B64 = _b64_scan()
B64V = lambda k, i=None: (_B64[k] if i is None else _B64[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b64 block>', 'exec')

assert S.count(NL + u'_B63 = _b63_scan()') == 1, u'anchor _b63_scan'
B64ENV = u'B63V=B63V,' + NL + u'               B64V=B64V)'
i0 = S.find(u'# B64: 报文没人应答时重传退避封顶多久')
while i0 >= 0:
    i1 = S.index(u'_B63 = _b63_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B64: 报文没人应答时重传退避封顶多久')
if B64ENV in S:
    S = S.replace(B64ENV, u'B63V=B63V)')
S = S.replace(NL + u'_B63 = _b63_scan()', BLK + NL + u'_B63 = _b63_scan()')
assert S.count(u'B63V=B63V)') == 1, u'anchor env'
S = S.replace(u'B63V=B63V)', B64ENV)

PS = u"SRC['B63'] = ["
blk = (u"SRC['B64'] = ['corpus/raw/dhcp/rfc2131.txt', 'corpus/raw/dhcp/rfc3315.txt', "
       u"'corpus/raw/dhcp/rfc7083.txt', 'corpus/raw/dhcp/rfc8415.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B62', 'B63'}", u"'B62', 'B63', 'B64'}"
# 只加进 ATOM(锚比对集), 不加进 HTMLSRC——四份都是纯文本面, 没有壳⇎面两口径
if NEW not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B64'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B64'" + S[m.end(1):]

M1 = u'# ---- B64 DERIV (generated by corpus/_wire64.py from corpus/_deriv64.json; do not hand-edit) ----'
M2 = u'# ---- /B64 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B63'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv64.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B64'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B64': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b64 block>', 'exec'), NS)
env = NS['B64V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b64flat.json', encoding='utf-8'))


def deep(x):
    return [deep(y) for y in x] if isinstance(x, list) else list(x) if isinstance(x, tuple) else x


for k, v in FLAT.items():
    if k == u'sig_sha256_16':
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
        got = eval(v, dict(NS), {'B64V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b63_scan' in S and u'_b64_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b64_scan+B64V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
