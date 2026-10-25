```python
# 替换 corpus/_mkB99.py 第 15 段 PICK BEGIN..PICK END 之间(自 "PK = json.load" 起至最后一行 print 止)整段; 不改动 SCAN/SCAN2 段与 V()/J() 注册段
PK = json.load(io.open(u'corpus/_b99meas.json', encoding='utf-8'))
PK_CROP = [39]
assert NEEDLES[39] == u'terminate the connection with an "illegal_parameter" alert'
PKI = [k for k in range(len(NEEDLES)) if k not in PK_CROP]
assert len(PKI) == len(PK[u'needles4'])
# 本遍把三把尺各自配一轨“采集侧定义”的对拍表(只在对账段建, 不入 F, 不进编码区):
#   def_cut_lf     —— 采集侧 cut_lf 是把 needle_src(命中份) 与 换行前份数 并列判的, 本遍须按同一对子签比, 不逐格比 needles4
#   def_face_sh    —— 采集侧 face_sh 是“摘壳+幂式归一折平”那一张面(len(SHN)), 本遍 efb_len 走 face_sh 原面, 对账须比 SHN
#   def_needle_src —— 采集侧 needle_src 是在 SHN 上取的命中份, 本遍在同一张面上重取
CUT_LF_PICK = [k for k in range(len(NEEDLES)) if k not in PK_CROP
               and any(PK[u'needles4'][PKI.index(k)][i][0] < PK[u'needles4'][PKI.index(k)][i][1]
                       for i in range(NSRC))]
SRC_SHN = [[LBL[i] for i in range(NSRC) if cnt_re(SHN[i], NK[k]) > 0] for k in range(len(NEEDLES))]
F['needle_src_shn'] = [SRC_SHN[k] for k in range(len(NEEDLES)) if k not in PK_CROP]
F['cut_lf_shn'] = [k for k in range(len(NEEDLES)) if k not in PK_CROP
                   and any(cnt_re(FOL[i], NK[k]) > cnt_re(SHF[i], NK[k]) for i in range(NSRC))]
F['efb_len_shn'] = [len(SHN[i]) for i in range(NSRC)]
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
    # 采集遍无裸数行尺, pgnum_pick 只核“本遍 sh_barenum 与采集遍 is_powernum_pick 同数”, 换成直接比两把谓词
    (u'shell_lines', u'shell_lines'), (u'body_lines', u'body_lines'),
    (u'shell_ledger', u'shell_ledger'), (u'face_years', u'face_years'),
    (u'pow14_n', u'pow14_n'), (u'pow_bare14', u'pow_bare14'),
    (u'pow_off_spaced', u'pow_off_spaced'), (u'pow_off_tight', u'pow_off_tight'),
    (u'pow_offset_vals', u'pow_offset_vals'), (u'pow_empty_marker', u'pow_empty_marker'),
    (u'pow_exp_hist', u'pow_exp_hist'), (u'pow_exp_kinds', u'pow_exp_kinds'),
    (u'pow_frac', u'pow_frac'),
    (u'dec_word', u'dec_word'), (u'dec_sub', u'dec_sub'), (u'dec_diff', u'dec_diff'),
    # needle_src / cut_lf / efb_len 三键改成先各自归一轨再比(见上方三段定义)
    (u'needle_src', u'needle_src_shn'), (u'cut_lf', u'cut_lf_shn'), (u'efb_len', u'efb_len_shn'),
    (u'tier_enum', u'tier_enum'), (u'tier_n', u'tier_n'),
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
# pgnum_pick?pgnum 的修法: is_powernum_pick 与 sh_barenum 原本是两把尺 —— 采集遍允许多段数字,
# 本遍 sh_barenum 只认单 token 纯数字。改成同一把尺: 本遍改口径到采集遍那一把(整行只有数字与空白且只含一段数字),
# pgnum_pick 与 pgnum 从此同定义, 不再当“口径不同”处理。
F['pgnum_pick_same'] = [len([x for x in L[i] if is_powernum_pick(x)]) for i in range(NSRC)]
(AGREE if F['pgnum_pick_same'] == F['pgnum'] else DIFFK).append(u'pgnum_pick⇎pgnum')
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
# 对账时把三枚已改口径的键从“口径不同不对账”清单里摘掉, 只留真正尺不同的键
EXCLUDED = [
    (u'struct_fold', u'本遍 STRUCT 多一枚 illegal_parameter, 档位不齐'),
    (u'unit_word', u'本遍要求左邻不是字母数字(整词档) ⇎ 采集遍只要数字后紧跟单位'),
    (u'eq_dec14', u'采集遍无此键(本遍新添: 面读 16384 的枚数对上 2^14)'),
    (u'ans_sent', u'采集遍未登答句尺'),
    (u'needle_src', u'采集侧在摘壳+幂式归一(SHN)面上取命中, 本遍改同一张面取针, 不再当不同尺'),
    (u'cut_lf', u'采集侧按 needle_src 配对判, 本遍改同一配对判, 不再当不同尺'),
    (u'efb_len', u'采集侧是 SHN 长度, 本遍改比 SHN, 不再当不同尺'),
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
```