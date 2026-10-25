# -*- coding: utf-8 -*-
"""把 B58 的独立复算器(_b58_scan / B58V)接进 audit.py, 并生成 DERIV['B58']。
幂等: 重复运行先摘旧块再插新块。
_b58_scan 的量测段从 corpus/_mkB58.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自三处:
①采集侧 corpus/_pick58.py 是先于建条目写好的另一套实现(它按方程段正则捕获系数、按逐行游标定权重段、逐对现算单调性),
  两边在 TIE 表上逐量对账(共有键与不符数见建条目末尾打印), 建条目侧改用"含关键词整行按 token 位置读系数"
  与"<tr> 切块 + 组头命中定段 + 首字母带例外定缩写"和"同一维 N<L<H 链 + 组合缓存";
②抽出的代码在插门之前要把 _b58flat.json 的每个键与 DERIV['B58'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按去标签正文的归一串判成员。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB58.py', encoding='utf-8').read()
NL = chr(10)
RAWS = ['corpus/raw/cvss/cvss_v30_spec.html', 'corpus/raw/cvss/cvss_v31_spec.html',
        'corpus/raw/cvss/cvss_v40_spec.html', 'corpus/raw/cvss/cvss_examples.html']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'ENT = [', u'# --- SCAN END ---')
assert u'F[u' in MEAS and u'POOL' in MEAS and u'full_eq3031' in MEAS and u'wt_pack_close' in MEAS
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'M[' not in MEAS

HEAD = u'''
# B58: 同一条漏洞向量该打几分——四份 FIRST 一手文书给出四种答法: raw/cvss/cvss_v30_spec.html(T 基础分闭式 + 环境分指数 15)
# ⇎ cvss_v31_spec.html(O 基础分逐字同式、环境分改指数 13 并乘 0.9731, 且自陈 "which differs from CVSS v3.0")
# ⇎ cvss_v40_spec.html(F 一个算式都不给, 换成 MacroVector 查表与 EQ1..EQ6 布尔约束)
# ⇎ cvss_examples.html(N 把两代分数并排印成表, 列头自写口径).
# 本函数从四份字节独立复算: 去标签层(注释→<br>→标签→实体→unicode)后的形状档与词面指纹,
# 基础分 8 项系数与 8 项环境系数的按行读取及两代差集, 权重表的两种序列化(一格五值⇎一格一值带续行)与三元组集合相等,
# 全 2592 条合法基础向量上两代逐条同分, 三种"进到 0.1"实现与 Fraction 精确判据的三方对账,
# 非单调违例的 114⇎6 三档账(消掉的 108 处全在未封顶那支), 算例文档的配对/跳过/口径直方与差值两本账,
# 跨严重度档迁移方向, 跨文书整行共用集与并集闭合, 锚候选池四层与锚归属由条目正文现推。
# 不可由在库文件判定的: 四份 HTML 的抓取时刻与磁盘 mtime 谁新谁旧、这批页面此刻是否各版当前发布(站点根路径现在指向 v4.0)、
# v4.0 印出的分数在库内是否可复算(v4.0 规范不给算式, 只给 MacroVector 与约束)——只进解读注, 不进门槛。
def _b58_scan():
    import hashlib as _hl
    import os as _os
    import math as _math
    from fractions import Fraction as Fr
    from itertools import product
    P2 = SRC['B58']
    TAGS = [u'T', u'O', u'F', u'N']
    LB = dict(zip(TAGS, [u'v3.0 规范', u'v3.1 规范', u'v4.0 规范', u'算例文档']))
    PATH = P2
    IDX = dict((t, i) for i, t in enumerate(TAGS))
    RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
    TXT = [RD(p) for p in PATH]
    ROOT = u''
    C = u'corpus'
    NL = chr(10)
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
for a, b in ((u'os.path.getsize(', u'_os.path.getsize('), (u'hashlib.', u'_hl.'),
             (u'math.', u'_math.')):
    BODYTXT = re.sub(u'(?<![.\\w])' + re.escape(a), b, BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert u'_os.open(' not in BODYTXT, u'裸 open( 被误改写'
assert u'_math.ceil' in BODYTXT and u'_hl.sha256' in BODYTXT and u'_os.path.getsize' in BODYTXT

TAIL = u'''
    # ---- 结构性自检: 全空间量词、系数差集、权重表两种序列化、单调性三档、算例口径账 ----
    assert F[u'full_vectors'] == F[u'full_grid_prod'] == 2592
    assert F[u'full_eq3031'] + F[u'full_ne3031'] == F[u'full_vectors'] and F[u'full_eq3031'] == 2592
    assert F[u'full_close'] == 0 and F[u'full_none30'] == 0
    assert F[u'full_ok'] == F[u'full_pseudo_eq_exact'] == F[u'full_guard_eq_exact'] == F[u'full_ceil_eq_exact']
    assert F[u'full_pseudo_ne_ceil'] == F[u'full_pseudo_ne_guard'] == 0
    assert F[u'full_raw_on_tenth'] == 0 and F[u'full_exact_on_tenth'] == 7
    assert F[u'full_zero'] + F[u'full_ok'] == F[u'full_vectors'] and F[u'full_capped'] == 7
    assert F[u'coef_base_n'] == F[u'coef_base_n_equal'] == 8
    assert F[u'coef_seq_n'] == F[u'coef_base_n'] + F[u'coef_env_keys'] == 16
    assert len(F[u'coef_v30']) == len(F[u'coef_v31']) == F[u'coef_seq_n']
    assert sorted([k for k in F[u'coef_v30'] if abs(F[u'coef_v30'][k] - F[u'coef_v31'][k]) > 1e-12]) \\
        == [u'mexp', u'mfactor']
    assert F[u'coef_env_diff_n'] == 2 and F[u'mexp30'] == 15 and F[u'mexp31'] == 13
    assert F[u'mf30'] == 1.0 and abs(F[u'mf31'] - 0.9731) < 1e-12
    assert F[u'cap30'] == F[u'cap31'] == 0.915 and F[u'exp30'] == F[u'exp31'] == 15
    assert F[u'coef_base_keynames'] == sorted(F[u'coef_base_keynames'])
    assert F[u'w_triples_v30'] == F[u'w_triples_v31'] == F[u'w_common'] == 44
    assert F[u'w_unequal_n'] == F[u'w_only30_n'] == F[u'w_only31_n'] == 0
    assert F[u'w_close30'] == F[u'w_close31'] == 0
    assert F[u'w_tab_n'] == [1, 1, 0, 0] and F[u'wt_rows'] == [10, 33, 0, 0]
    assert F[u'wt_nums'] == F[u'wt_vals'] == [32, 32, 0, 0]
    assert F[u'wt_val_rows'] == [9, 32, 0, 0] and F[u'wt_metric_rows'] == [9, 9, 0, 0]
    assert F[u'wt_cont_rows'] == [0, 23, 0, 0] and F[u'wt_maxpack'] == [5, 1, 0, 0]
    assert F[u'wt_val_rows'][1] - F[u'wt_metric_rows'][1] == F[u'wt_cont_rows'][1]
    assert F[u'wt_pack_close'] == [0, 0, 0, 0] and F[u'wt_row_close'] == [0, 0, 0, 0]
    assert F[u'mono_pairs'] == 1458 and F[u'mono_combos'] == 729 and F[u'mono_grid_close'] == 0
    assert F[u'mono_only30'] + F[u'mono_both'] == F[u'mono_bad_v30formula'] == 114
    assert F[u'mono_both'] == F[u'mono_bad_v31formula'] == 6 and F[u'mono_only31'] == 0
    assert F[u'mono_capped30'] + F[u'mono_uncapped30'] == F[u'mono_bad_v30formula']
    assert F[u'mono_capped31'] == F[u'mono_bad_v31formula'] and F[u'mono_uncapped31'] == 0
    assert F[u'mono_close30'] == F[u'mono_close31'] == F[u'mono_cap_close30'] == 0
    assert F[u'sp_n'] == 38 and F[u'pair_close'] == 0 and F[u'repro_close'] == 0
    assert F[u'repro_ok'] == F[u'repro_vec_distinct'] == 29
    assert F[u'repro_bad'] == F[u'repro_none'] == 0
    assert F[u'delta_pos'] + F[u'delta_neg'] + F[u'delta_zero'] == F[u'sp_n'] + F[u'delta_close']
    assert F[u'delta_base_n'] == F[u'pair_scope_base_strict'] == 28
    assert F[u'delta_base_up'] + F[u'delta_base_down'] + F[u'delta_base_same'] == F[u'delta_base_n']
    assert F[u'delta_base_strict_tie'] and F[u'delta_ledger'] == 0
    assert F[u'pair_scope_base_loose'] == F[u'pair_scope_base_strict'] + F[u'pair_scope_base_gap']
    assert F[u'comp_other_strict'] == F[u'sp_n'] - F[u'pair_scope_base_strict']
    assert abs(F[u'delta_mix_gap'] - (F[u'delta_sum'] - F[u'delta_base_sum'])) < 1e-9
    assert F[u'band_diff'] + F[u'band_same'] + F[u'band_unmapped'] == F[u'sp_n'] + F[u'band_close']
    assert F[u'band_rows'] == [5, 5, 5, 0] and F[u'band_bounds'][0] == F[u'band_bounds'][1] \\
        == F[u'band_bounds'][2] and F[u'band_bounds'][3] == []
    assert F[u'band_vocab'][3] == [] and F[u'band_vocab'][0] == F[u'band_vocab'][1]
    assert u'Negligible' in F[u'band_vocab'][2] and u'Negligible' not in F[u'band_vocab'][0]
    assert F[u'arith_any'] == [1, 1, 0, 0] and F[u'eq_row_n'] == 22
    assert F[u'bl_mv'] == [0, 0, 39, 0] and F[u'bl_mv_body'] == [0, 0, 37, 0]
    assert F[u'ar_ru'] == [0, 14, 0, 0] and F[u'ar_ru_up'] == [10, 0, 0, 0]
    assert F[u'ar_k822'][2] == F[u'ar_k822'][3] == 0 and F[u'ar_k9731'][1] == 1
    assert F[u'share_TO'] + F[u'only_T'] + F[u'only_O'] == F[u'union_TO'] + F[u'share_close_TO']
    assert F[u'pool_1'] + F[u'pool_2'] + F[u'pool_3'] + F[u'pool_4'] == F[u'pool_n'] + F[u'pool_close']
    assert F[u'tr_rows_div_close'] == 0 and F[u'mono_pairs_close'] == 0
    assert F[u'scalar_clos_n'] == 16 and F[u'scalar_clos_sum'] == 0 and F[u'list_clos_n'] == 2
    assert F[u'scalar_clos_list'] == sorted([u'band_close', u'delta_close', u'delta_ledger',
                                             u'full_close', u'mono_cap_close30', u'mono_close30',
                                             u'mono_close31', u'mono_grid_close', u'mono_pairs_close',
                                             u'pair_close', u'pool_close', u'repro_close',
                                             u'share_close_TO', u'tr_rows_div_close',
                                             u'w_close30', u'w_close31'])
    assert len(set(F[u'sha16'])) == 4 and F[u'tabs'] == [0, 0, 0, 0] and F[u'bom'] == [0, 0, 0, 0]
    assert F[u'bytes'] == [77769, 89323, 118046, 229650]

    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B58_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B58: 正文里没有带标签的锚'
    assert len(re.findall(u'⟨', enc)) == len(CITES), u'B58: 有锚没带源标签'
    ERR = [x for x in CITES if not pnorm(x[1]) or pnorm(x[1]) not in FAN[IDX[x[0]]]]
    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [tuple(i for i in range(4) if pnorm(a) and pnorm(a) in FAN[i]) for a in DIS]
    F[u'anchor_total'] = len(CITES)
    F[u'anchor_distinct'] = len(DIS)
    F[u'anchor_err'] = len(ERR)
    F[u'anchor_single'] = len([h for h in HC if len(h) == 1])
    F[u'anchor_cross'] = len([h for h in HC if 1 < len(h) < 4])
    F[u'anchor_all4'] = len([h for h in HC if len(h) == 4])
    F[u'checks'] = len(DIS) * 4
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all4'] == len(DIS)
    return F

_B58 = _b58_scan()
B58V = lambda k, i=None: (_B58[k] if i is None else _B58[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b58 block>', 'exec')

o = NL + u'_B57 = _b57_scan()'
assert S.count(o) == 1, u'anchor _b57_scan'
B58ENV = u'B57V=B57V,' + NL + u'               B58V=B58V)'
i0 = S.find(u'# B58: 同一条漏洞向量')
while i0 >= 0:
    i1 = S.index(u'_B57 = _b57_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B58: 同一条漏洞向量')
if B58ENV in S:
    S = S.replace(B58ENV, u'B57V=B57V)')
S = S.replace(o, BLK + o)
assert S.count(u'B57V=B57V)') == 1, u'anchor env'
S = S.replace(u'B57V=B57V)', B58ENV)

PS = u"SRC['B57'] = ["
blk = (u"SRC['B58'] = ['corpus/raw/cvss/cvss_v30_spec.html', 'corpus/raw/cvss/cvss_v31_spec.html', "
       u"'corpus/raw/cvss/cvss_v40_spec.html', 'corpus/raw/cvss/cvss_examples.html']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B56', 'B57'}", u"'B56', 'B57', 'B58'}"
if NEW not in S:
    assert S.count(OLD) == 1, u'anchor ATOM'
    S = S.replace(OLD, NEW)

M1 = u'# ---- B58 DERIV (generated by corpus/_wire58.py from corpus/_deriv58.json; do not hand-edit) ----'
M2 = u'# ---- /B58 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv58.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B58'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B58': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b58 block>', 'exec'), NS)
env = NS['B58V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b58flat.json', encoding='utf-8'))


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
        got = eval(v, dict(NS), {'B58V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b57_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b58_scan+B58V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values()),
         env('anchor_total'), env('anchor_distinct'), env('checks')))
