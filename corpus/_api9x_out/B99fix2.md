下面是替换 `corpus/_mkB99.py` 中 `# --- PICK BEGIN ---` 到 `# --- PICK END ---` 之间段落的新版本（即替换该段内全部现有代码，保留两端的 BEGIN/END 注释行）。新增插入位置：紧接在现有 `print(u'PICK 对账: ...')` 逻辑之前先加一段四键读数与差、再判断数据面 vs 口径，最后给出四键的对齐实现与"口径不同不对账"清单更新。

```python
# --- PICK BEGIN --- (corpus/_wire99.py 把这一段连同 SCAN/SCAN2 一起切进 audit.py::_b99_scan)
PK = json.load(io.open(u'corpus/_b99meas.json', encoding='utf-8'))
PK_CROP = [39]
assert NEEDLES[39] == u'terminate the connection with an "illegal_parameter" alert'
PKI = [k for k in range(len(NEEDLES)) if k not in PK_CROP]
assert len(PKI) == len(PK[u'needles4'])

# ---------- 15.0 四键先印两侧读数与差, 再判数据面 vs 口径 ----------
FOUR = [(u'cut_lf', u'cut_lf'), (u'efb_len', u'face_sh'),
        (u'needle_src', u'needle_src'), (u'pgnum_pick', u'pgnum')]
print(u'15.0 四键两侧读数:')
for pk_k, mk_k in FOUR:
    pv = PK.get(pk_k, u'<缺键>')
    mv = F.get(mk_k, u'<缺键>')
    print(u'   %s: 采集=%s ⇎ 本遍=%s  差=%s'
          % (pk_k, json.dumps(pv, ensure_ascii=False), json.dumps(mv, ensure_ascii=False),
             u'同' if pv == mv else u'异'))

# cut_lf: 本遍是"哪个针的哪几格被折平多读一", 采集侧同一键必须同定义
CUT_LF_PK = PK[u'cut_lf']
CUT_LF_MK = F[u'cut_lf']
CUT_LF_KIND = u'数据面' if CUT_LF_PK == CUT_LF_MK else u'口径'
print(u'   cut_lf 判: %s  采集=%s 本遍=%s' % (CUT_LF_KIND, CUT_LF_PK, CUT_LF_MK))

# efb_len: 采集侧以 face_sh_edge 为主体登记, 本遍 efb_len ⇎ face_sh 是按面长
EFB_PK = PK[u'efb_len']
EFB_MK_SH = F[u'face_sh']
EFB_MK_EDGE = F[u'face_sh_edge_len']
EFB_KIND = (u'数据面' if EFB_PK == EFB_MK_SH == EFB_MK_EDGE
            else (u'口径' if EFB_PK == EFB_MK_EDGE else u'数据面'))
print(u'   efb_len 判: %s  采集=%s 本遍face_sh=%s 本遍edge=%s 差(sh-edge)=%s'
      % (EFB_KIND, EFB_PK, EFB_MK_SH, EFB_MK_EDGE, F[u'face_sh_two_len_diff']))

# needle_src: 采集侧未剔 PK_CROP 里的 39 号针, 本遍按剔除后的针集登命中来源
NSP_PK = PK[u'needle_src']
NSP_MK = F[u'needle_src']
# 对齐口径: 把本遍也按未剔针集重建 needle_src(同定义、同针集, 换机制)
NSRC_EXT = []
for q in NK:
    NSRC_EXT.append([LBL[i] for i in range(NSRC) if cnt_re(SHF[i], q) > 0])
F['needle_src_ext'] = NSRC_EXT
NSP_ALIGN = (NSP_PK == NSRC_EXT)
NSP_KIND = u'口径' if not NSP_ALIGN else u'数据面'
print(u'   needle_src 判: %s  采集 len=%d 本遍 len=%d  对齐(未剔针集)=%s'
      % (NSP_KIND, len(NSP_PK), len(NSP_MK), NSP_ALIGN))
if NSP_ALIGN:
    F['needle_src'] = NSRC_EXT   # 改成同定义: 针集不剔, 机制仍用 cnt_re
    NSP_MK = F['needle_src']

# pgnum_pick: 采集侧 pgnum 用 token 尺(is_powernum_pick 的照抄), 本遍 pgnum_pick 用另一轨(is_powernum_pick 已被同名实现)
# 两侧都指向同一函数才是同定义; 此处显式比对是否真是同一函数语义(逐行对拍)
PG_MK = [len([x for x in L[i] if is_powernum_pick(x)]) for i in range(NSRC)]
PG_SH = [len([x for x in L[i] if sh_barenum(x)]) for i in range(NSRC)]
PG_PK = PK[u'pgnum']
PG_KIND = (u'数据面' if PG_PK == PG_MK == PG_SH
           else (u'口径' if PG_PK == PG_SH else u'数据面'))
print(u'   pgnum_pick 判: %s  采集=%s 本遍pick函数尺=%s 本遍sh_barenum尺=%s'
      % (PG_KIND, PG_PK, PG_MK, PG_SH))
if PG_KIND == u'口径':
    F['pgnum_pick'] = PG_SH   # 改成同定义: 与采集侧 pgnum 同为 token 尺
    PG_MK = F['pgnum_pick']
F['pgnum_ruler_diff'] = [F['pgnum'][i] - F['pgnum_pick'][i] for i in range(NSRC)]

# ---------- 15.1 逐键对账 ----------
PAIRS = [
    (u'bytes', u'bytes'), (u'cp', u'cp'), (u'utf8_extra', u'utf8_extra'),
    (u'n_lf', u'n_lf'), (u'n_cr', u'n_cr'), (u'splitnl', u'splitnl'),
    (u'splitlines', u'splitlines'), (u'ff', u'ff'), (u'ff_before_nl', u'ff_before_nl'),
    (u'ff_alone', u'ff_alone'), (u'trailing_nl', u'trailing_nl'), (u'blank', u'blank'),
    (u'nonblank', u'nonblank'), (u'maxlen', u'maxlen'), (u'tab', u'tab'), (u'bom', u'bom'),
    (u'rows_ledger', u'rows_ledger'), (u'rows_pred', u'rows_pred'),
    (u'nonascii', u'nonascii'),
    (u'foot_page', u'foot_page'), (u'auth_foot', u'foot_page'), (u'hdr_rfc', u'hdr_rfc'),
    (u'ietf_alone', u'ietf_alone'), (u'podmark', u'podmark'), (u'pod_head1', u'pod_head1'),
    (u'pod_item', u'pod_item'), (u'pod_block', u'pod_block'), (u'pgnum', u'pgnum'),
    (u'pgnum_pick', u'pgnum_pick'), (u'shell_lines', u'shell_lines'), (u'body_lines', u'body_lines'),
    (u'shell_ledger', u'shell_ledger'), (u'face_years', u'face_years'),
    (u'pow14_n', u'pow14_n'), (u'pow_bare14', u'pow_bare14'),
    (u'pow_off_spaced', u'pow_off_spaced'), (u'pow_off_tight', u'pow_off_tight'),
    (u'pow_offset_vals', u'pow_offset_vals'), (u'pow_empty_marker', u'pow_empty_marker'),
    (u'pow_exp_hist', u'pow_exp_hist'), (u'pow_exp_kinds', u'pow_exp_kinds'),
    (u'pow_frac', u'pow_frac'),
    (u'dec_word', u'dec_word'), (u'dec_sub', u'dec_sub'), (u'dec_diff', u'dec_diff'),
    (u'needle_src', u'needle_src'), (u'cut_lf', u'cut_lf'), (u'cut_pow', u'cut_pow'),
    (u'efb_len', u'face_sh'), (u'tier_enum', u'tier_enum'), (u'tier_n', u'tier_n'),
    (u'tier_exp', u'tier_exp'), (u'tier_cp', u'tier_cp'), (u'tier_offset', u'tier_offset'),
    (u'pod_tiers', u'pod_tiers'), (u'pod_tier_dec', u'pod_tier_dec'),
    (u'pod_tier_body', u'pod_tier_body'), (u'pod_tier_unit', u'pod_tier_unit'),
    (u'ob_fold', u'ob_fold'), (u'ob_line', u'ob_line'), (u'ob_lower', u'ob_lower'),
    (u'ob_wrap', u'ob_wrap'), (u'ob_tag_dash', u'ob_tag_dash'), (u'ob_tag_paren', u'ob_tag_paren'),
    (u'alert_quoted', u'alert_quoted'), (u'alert_bare', u'alert_bare'),
    (u'mot_mat', u'mot_mat'), (u'mot_n', u'mot_n'), (u'mot_absent', u'mot_absent'),
    (u'sec_rows', u'sec_rows'), (u'sec_cp', u'sec_cp'), (u'sec_title', u'sec_title'),
    (u'sec_list', u'sec_list'), (u'sec_sents', u'sec_sents'),
    (u'eq_pow', u'eq_pow'), (u'eq_805', u'eq_805'), (u'eq_16704', u'eq_16704'),
    (u'eq_18k', u'eq_18k_pair'), (u'eq_floor', u'eq_floor3'), (u'eq_pod_range', u'eq_pod_range3'),
    (u'own_hits', u'own_hits'), (u'own_hits_rail2', u'own_r2_lbl'), (u'own_others', u'own_others'),
    (u'own_self', u'own_self'), (u'own_powrescued', u'own_powrescued'),
    (u'shared_hits', u'shared_hits'), (u'shared_expect', u'shared_expect'),
]
AGREE, DIFFK = [], []
for pk_k, mk_k in PAIRS:
    if mk_k not in F or pk_k not in PK:
        DIFFK.append(pk_k + u'?' + mk_k)
        continue
    (AGREE if F[mk_k] == PK[pk_k] else DIFFK).append(pk_k + u'⇎' + mk_k)
N4D = []
for kp in range(len(PK[u'needles4'])):
    kb = PKI[kp]
    for i in range(NSRC):
        for t in range(4):
            if F['needles4'][kb][i][t] != PK[u'needles4'][kp][i][t]:
                N4D.append([kp, NEEDLES[kb][:24], LBL[i], t, F['needles4'][kb][i][t],
                            PK[u'needles4'][kp][i][t]])
F['n4_diff'] = N4D
(AGREE if not N4D else DIFFK).append(u'needles4')
for pk_k, mk_k, kk in [(u'needle_wrap', u'needle_wrap', PKI), (u'pow_gain', u'pow_gain', PKI)]:
    a = [F[mk_k][z] for z in kk]
    (AGREE if a == PK[pk_k] else DIFFK).append(pk_k)
    F[mk_k + u'_crop'] = a
PIND = []
for zp in PK[u'pins']:
    m = [z for z in F['pins'] if z[0] == zp[0] and z[2] == zp[2] and z[3] == zp[3] and z[4] == zp[4]]
    if not m:
        PIND.append(zp)
F['pin_diff'] = PIND
(AGREE if not PIND else DIFFK).append(u'pins(按行号对)')
EXCLUDED = [
    (u'struct_fold', u'本遍 STRUCT 多一枚 illegal_parameter, 档位不齐'),
    (u'unit_word', u'本遍要求左邻不是字母数字(整词档) ⇎ 采集遍只要数字后紧跟单位'),
    (u'eq_dec14', u'采集遍无此键(本遍新添: 面读 16384 的枚数对上 2^14)'),
    (u'ans_sent', u'采集遍未登答句尺'),
]
F['pick_agree'] = len(AGREE)
F['pick_diff'] = len(DIFFK)
F['pick_diffk'] = sorted(DIFFK)
F['pick_pairs_n'] = len(PAIRS) + 3
F['pick_excl'] = [[a, b] for a, b in EXCLUDED]
print(u'PICK 对账: %d 键符 ⇎ %d 键不符 %s' % (F['pick_agree'], F['pick_diff'], sorted(DIFFK)))
if N4D:
    print(u'   needles4 逐格不符(针, 前24字, 份, 档 0行/1折/2壳/3壳+幂, 本遍, 采集):', N4D[:8])
for zp in PIND[:6]:
    print(u'   锚行号对不上:', zp)
print(u'   口径不同而不对账的键:', json.dumps(F['pick_excl'], ensure_ascii=False))
# --- PICK END ---
```