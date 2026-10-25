# -*- coding: utf-8 -*-
"""把 B59 的独立复算器(_b59_scan / B59V)接进 audit.py, 并生成 DERIV['B59']。
幂等: 重复运行先摘旧块再插新块。
_b59_scan 的量测段从 corpus/_mkB59.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自三处:
①采集侧 corpus/_pick59.py 是先于建条目写好的另一套实现(它用 '<' 游标分段器剥壳、str.find 游标计数、
  字母边界正则数强度词、Counter 词元汇总数 password、从右数列格取 ASVS 末格、按行首 token 段数定章节号),
  两边在 TIE 表上逐量对账(共有键与不符数见建条目末尾打印);
②抽出的代码在插门之前要把 _b59flat.json 的每个键与 DERIV['B59'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按去标签正文的归一串判成员。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB59.py', encoding='utf-8').read()
NL = chr(10)
RAWS = ['corpus/raw/pwd/nist_63b_rev3.html', 'corpus/raw/pwd/asvs_40_v2.md',
        'corpus/raw/pwd/nist_63b_rev4.html', 'corpus/raw/pwd/owasp_auth_cs.html']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'ENT = [', u'# --- SCAN END ---')
assert u'F[u' in MEAS and u'POOL' in MEAS and u'asvs_ref_inT' in MEAS and u'bl_word_close' in MEAS
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and not re.search(u'(?<![A-Za-z_0-9])M\\[', MEAS)

HEAD = u'''
# B59: 同一个口令该多长——四份一手规范四种答法: raw/pwd/nist_63b_rev3.html(T 8 字符且写作 memorized secret)
# ⇎ asvs_40_v2.md(O 12 字符并要求上限 128, 每条要求末格钉一个 NIST 条款号)
# ⇎ nist_63b_rev4.html(F 单因子 15 字符、多因子那半句把 8 写成英文单词 eight, 且唯一引入 blocklist)
# ⇎ owasp_auth_cs.html(N 把 8 与 15 一并归给 "NIST SP800-63B" 而不说是哪一版).
# 本函数从四份字节独立复算: 去标签层(注释→<br>→标签→实体→unicode)后的形状档与两口径字数差,
# "数|词 + characters" 语境的取值集合与记法账(数字⇎英文词), ASVS 末格条款号集合与两版规范标题号集的命中账,
# 矩阵三列勾数⇎图例行勾号⇎文件内勾号字符的闭合, 强度词大写/小写/首字母三档与忽略大小写的闭合(MUST 大写全 0),
# memorized secret⇎password 的术语换代账与单复数闭合, blacklist 词族的紧写/带空格两形,
# 熵位集增删(丢 20 增 40), 跨文书整行共用⇎子串再现⇎句子档三口径与体裁拆分, 锚候选池四层与锚归属由正文现推。
# 不可由在库文件判定的: 四份文件的抓取时刻与磁盘 mtime 谁新谁旧、草案此刻是否已定稿、
# 备忘单那句 "(NIST SP800-63B)" 究竟指 2017 定稿还是 2025 草案、旧规范页的废止横幅何时挂上——只进解读注, 不进门槛。
def _b59_scan():
    import hashlib as _hl
    import os as _os
    from collections import Counter
    P2 = SRC['B59']
    TAGS = [u'T', u'O', u'F', u'N']
    LB = dict(zip(TAGS, [u'旧规范', u'验证标准', u'新草案', u'备忘单']))
    PATH = P2
    IDX = dict((t, i) for i, t in enumerate(TAGS))
    RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
    TXT = [RD(p) for p in PATH]
    ROOT = u''
    C = u'corpus'
    NL = chr(10)
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
for a, b in ((u'os.path.getsize(', u'_os.path.getsize('), (u'hashlib.', u'_hl.')):
    BODYTXT = re.sub(u'(?<![.\\w])' + re.escape(a), b, BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert u'_os.open(' not in BODYTXT, u'裸 open( 被误改写'
assert u'_hl.sha256' in BODYTXT and u'_os.path.getsize' in BODYTXT

TAIL = u'''
    # ---- 结构性自检: 门槛四答、记法账、条款号命中、术语与强度词闭合、搬运三口径 ----
    assert F[u'bytes'] == [215987, 30539, 353757, 135420] and F[u'sig_distinct'] == 4
    assert F[u'lt_tags'] == [4221, 0, 7474, 2761] and F[u'table_tags'] == [16, 0, 5, 1]
    assert F[u'lines'] == [2470, 211, 4032, 6073] and F[u'rlines'] == [2469, 211, 3991, 6073]
    assert F[u'nonblank'] == [1787, 149, 2570, 2380] and F[u'rnonblank'] == [1053, 149, 1521, 534]
    assert F[u'js_gap'] == [F[u'chars_untagged'][i] - F[u'chars'][i] for i in range(4)]
    assert F[u'js_gap'][1] == 0 and F[u'script_tags'] == [9, 0, 9, 6] and F[u'style_tags'] == [0, 0, 0, 1]
    assert F[u'pipe_cells'] == [4, 655, 5, 0] and F[u'bold_marks'] == [0, 57, 0, 0]
    assert F[u'pipe_vs_row'] == F[u'pipe_cells'][1] - (F[u'tr_rows'][0] + F[u'tr_rows'][2])
    assert F[u'tabs'] == [0, 0, 0, 0] and F[u'bom'] == [0, 0, 0, 0]
    assert F[u'ctx_set'] == [[6, 8, 64], [6, 12, 64, 128], [4, 6, 8, 15, 64], [8, 15, 64]]
    assert F[u'ctx_occ'] == [10, 4, 6, 4] and F[u'ctx_distinct'] == [3, 4, 5, 3]
    assert F[u'ctx_word_form'] == [0, 0, 3, 0] and F[u'ctx_digit_form'] == [10, 4, 3, 4]
    assert F[u'ctx_form_close'] == [0, 0, 0, 0]
    assert F[u'th_digit8'] == [4, 1, 0, 1] and F[u'th_word_eight'] == [0, 0, 1, 0]
    assert F[u'ctx_eight_docs'] == 1 and F[u'ctx_d8_docs'] == 3
    assert F[u'th_digit15'] == [0, 0, 1, 1] and F[u'ctx_815_docs'] == 2 and F[u'ctx_12_only'] == 1
    assert F[u'th_digit128'] == [0, 1, 0, 0] and F[u'ctx_128_only'] == 1
    assert F[u'asvs_req_rows'] == 57 and F[u'asvs_ref_occ'] == 48 and F[u'asvs_ref_distinct'] == 16
    assert F[u'asvs_rows_noref'] == 9 and F[u'asvs_ref_occ'] + F[u'asvs_rows_noref'] == F[u'asvs_req_rows']
    assert F[u'asvs_ref_inT'] == 16 and F[u'asvs_ref_inF'] == 0
    assert F[u'asvs_ref_inT_text'] == 16 and F[u'asvs_ref_inF_text'] == 0
    assert F[u'asvs_ref_missT'] == [] and len(F[u'asvs_ref_missF']) == 16
    assert F[u'asvs_ref_close'] == 0
    assert F[u'asvs_tick_cols'] == [27, 48, 53] and F[u'asvs_tick_total'] == 128
    assert F[u'asvs_tick_legend'] == 1 and F[u'asvs_tick_glyph'] == 129
    assert F[u'asvs_tick_close'] == 0 and F[u'asvs_cwe_distinct'] == 22
    assert F[u'sec_T_n'] == 73 and F[u'sec_F_n'] == 12 and F[u'sec_shared'] == 0
    assert F[u'sec_T_inF_text'] == 4 and F[u'sec_head_n'] == [80, 0, 13, 0]
    assert F[u'id_211_docs'] == 2 and F[u'asvs_5112'] == [7, 25, 0, 0]
    assert F[u'tm_memorized'] == [113, 3, 4, 0] and F[u'tm_bridge'] == [0, 1, 0, 0]
    assert F[u'tm_pw_sing'] == [40, 45, 134, 105] and F[u'tm_pw_any'] == [80, 77, 247, 134]
    assert F[u'tm_close'] == [0, 0, 0, 0]
    assert F[u'kw_must_u'] == [0, 0, 0, 0] and F[u'must_upper_all4'] == 0
    assert F[u'kw_must_l'] == [6, 2, 16, 6] and F[u'kw_shall_u'] == [283, 3, 337, 0]
    assert F[u'kw_close_sum'] == 0 and F[u'kw_gap'] == [114, 17, 165, 46]
    assert F[u'kw_shallnot_u'] == [29, 0, 25, 0] and F[u'kw_shouldnot_u'] == [8, 0, 8, 0]
    assert F[u'comp_shouldnot'] == [1, 0, 0, 0] and F[u'comp_shallnot'] == [0, 0, 1, 0]
    assert F[u'chg_shallnot'] == [0, 0, 1, 0]
    assert F[u'mc_blocklist'] == [0, 0, 17, 2] and F[u'bl_blacklist'] == [6, 0, 2, 0]
    assert F[u'bl_spaced'] == [2, 0, 0, 0] and F[u'bl_word_any'] == [8, 0, 19, 2]
    assert F[u'bl_word_close'] == [0, 0, 0, 0] and F[u'bl_black_close'] == [0, 0, 0, 0]
    assert F[u'bit_set'] == [[u'112', u'20', u'32', u'64'], [u'112', u'20', u'32', u'64'],
                             [u'112', u'32', u'40', u'64'], []]
    assert F[u'bit_lost'] == [u'20'] and F[u'bit_new'] == [u'40'] and F[u'bit_close'] == [0, 0, 0, 0]
    assert F[u'share_TF'] == 63 and F[u'share_ON'] == 0 and F[u'share_all4'] == 0
    assert F[u'only_T'] == 742 and F[u'only_F'] == 1096 and F[u'union_TF'] == 1901
    assert F[u'share_TF'] + F[u'only_T'] + F[u'only_F'] == F[u'union_TF']
    assert F[u'share_close_TF'] == 0 and F[u'share_close_ON'] == 0
    assert F[u'carry_sub_TF'] == 80 and F[u'carry_sub_FT'] == 142
    assert F[u'carry_caliber_gap'] == F[u'carry_sub_overlap'] - F[u'share_TF'] == 159
    assert F[u'carry_ref'] == 0 and F[u'carry_toc'] == 0 and F[u'carry_prose'] == 63
    assert F[u'carry_split_close'] == 0
    assert F[u'sent_shared_TF'] == 95 and F[u'sent_share_th'] == 1 and F[u'sent_close_TF'] == 0
    assert F[u'pool_n'] == 2463 and F[u'pool_tiers'] == [2218, 221, 20, 4] and F[u'pool_close'] == 0
    assert F[u'pool_tag_n'] == [816, 122, 1169, 356] and F[u'pool_maxlen'] == 1352
    assert sum(F[u'pool_tag_n']) == F[u'pool_n']
    assert F[u'scalar_clos_n'] == 8 and F[u'scalar_clos_sum'] == 0 and F[u'list_clos_n'] == 6
    assert F[u'sec_cite_sec'] == [0, 0, 153, 0] and F[u'sec_cite_word'] == [117, 2, 47, 4]
    assert F[u'sec_cite_any'] == [117, 2, 200, 4] and F[u'sec_cite_close'] == [0, 0, 0, 0]
    assert F[u'id_211_occ'] == [0, 4, 1, 0] and F[u'id_211_docs'] == 2
    assert F[u'chars'] == [173270, 30220, 258623, 53212] and F[u'chars_untagged'] == [174211, 30220, 261152, 55036]
    assert F[u'scalar_clos_list'] == sorted([u'asvs_ref_close', u'asvs_tick_close', u'carry_split_close',
                                             u'kw_close_sum', u'pool_close', u'sent_close_TF',
                                             u'share_close_ON', u'share_close_TF'])
    assert len(set(F[u'sha16'])) == 4

    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B59_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B59: 正文里没有带标签的锚'
    assert len(re.findall(u'⟨', enc)) == len(CITES), u'B59: 有锚没带源标签'
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
    for t in TAGS:
        F[u'tag_' + t] = len(re.findall(u'⟦%s⟧' % t, enc))
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all4'] == len(DIS)
    return F

_B59 = _b59_scan()
B59V = lambda k, i=None: (_B59[k] if i is None else _B59[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b59 block>', 'exec')

o = NL + u'_B58 = _b58_scan()'
assert S.count(o) == 1, u'anchor _b58_scan'
B59ENV = u'B58V=B58V,' + NL + u'               B59V=B59V)'
i0 = S.find(u'# B59: 同一个口令该多长')
while i0 >= 0:
    i1 = S.index(u'_B58 = _b58_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B59: 同一个口令该多长')
if B59ENV in S:
    S = S.replace(B59ENV, u'B58V=B58V)')
S = S.replace(o, BLK + o)
assert S.count(u'B58V=B58V)') == 1, u'anchor env'
S = S.replace(u'B58V=B58V)', B59ENV)

PS = u"SRC['B58'] = ["
blk = (u"SRC['B59'] = ['corpus/raw/pwd/nist_63b_rev3.html', 'corpus/raw/pwd/asvs_40_v2.md', "
       u"'corpus/raw/pwd/nist_63b_rev4.html', 'corpus/raw/pwd/owasp_auth_cs.html']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B57', 'B58'}", u"'B57', 'B58', 'B59'}"
if NEW not in S:
    assert S.count(OLD) == 1, u'anchor ATOM'
    S = S.replace(OLD, NEW)

M1 = u'# ---- B59 DERIV (generated by corpus/_wire59.py from corpus/_deriv59.json; do not hand-edit) ----'
M2 = u'# ---- /B59 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv59.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B59'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B59': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b59 block>', 'exec'), NS)
env = NS['B59V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b59flat.json', encoding='utf-8'))


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
        got = eval(v, dict(NS), {'B59V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b58_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b59_scan+B59V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values()),
         env('anchor_total'), env('anchor_distinct'), env('checks')))
