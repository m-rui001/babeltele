# -*- coding: utf-8 -*-
"""把 B57 的独立复算器(_b57_scan / B57V)接进 audit.py, 并生成 DERIV['B57']。
幂等: 重复运行先摘旧块再插新块。
_b57_scan 的量测段从 corpus/_mkB57.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自三处:
①采集侧 corpus/_pick57.py 是先于建条目写好的另一套实现(它用正则认页眉页标、用 {8,} 量词抽套件名、用 split 断行制表),
  两边在 TIE 表上逐量对账(条数见 _b57checks.json 的 meas_tie_keys), 建条目侧改用逐次 find 扫描与手工扩字符;
②抽出的代码在插门之前要把 _b57flat.json 的每个键与 DERIV['B57'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里“源标签紧接原子引文”的配对现推, 四源一律按原文件行的归一串判成员。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB57.py', encoding='utf-8').read()
NL = chr(10)
RAWS = ['corpus/raw/ietf/rfc5246.txt', 'corpus/raw/ietf/rfc7525.txt',
        'corpus/raw/ietf/rfc8446.txt', 'corpus/raw/ietf/rfc9325.txt']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'def pnorm(s):', u'# --- SCAN END ---')
assert u'F[u' in MEAS and u'POOL' in MEAS and u'suite_bridge_close' in MEAS and u'sp_case_variants' in MEAS

HEAD = u'''
# B57: 同一个签名哈希(SHA-1)在四份规范性文书里有四种身份——raw/ietf/rfc5246.txt(TLS 1.2 协议, 把它写成枚举值与默认 MAC)
# ⇎ rfc7525.txt(BCP 195 第一版, 连 "SHA-1" 这个拼写都不出现, 只在 MAC 下限里留 HMAC-SHA1)
# ⇎ rfc8446.txt(TLS 1.3 协议, 把它关进 "Legacy algorithms" 注释块, 对证书留豁免从句、对握手消息给绝对 MUST NOT)
# ⇎ rfc9325.txt(BCP 195 第二版, 与 MD5 并列写成不留从句的 MUST NOT)。
# 本函数从四份字节独立复算: 字节/换行/最长行/制表符/非 ASCII/BOM/sha16 种数, 页标与页眉之差,
# RFC 2119 强度词的排他口径闭合差, 项目符 'o'⇎'*' 的单用与混用, SHA-1 三种拼写的可见度矩阵与判决行同现,
# 门限那句的数值与强度同时迁移(192 SHOULD NOT ⇎ 224 MUST NOT), 套件名的跨代零交集与两条桥的闭合差,
# 12 个有序引用对的方向违例、在库 Obsoletes/Updates 命中, 两版建议的整行⇎再现⇎句子三口径搬运与体裁拆分,
# 1.3 的 SignatureScheme 遗留块与“必须支持”集的交, 关键串四源矩阵与锚候选池, 锚归属由条目正文现推。
# 不可由在库文件判定的: 四份字节的磁盘 mtime 与页眉自写日期谁新谁旧(只在本机成立)、抓到的是否该号当前版本、
# 新建议点名的 8 枚套件在库里没有的规范(AES-GCM 与 ECDHE 那一族, 本库只收这四份)里是否合法、IANA 注册表此刻的弃用标记。
def _b57_scan():
    import hashlib as _hl
    import os as _os
    P2 = SRC['B57']
    TAGS = [u'T', u'O', u'F', u'N']
    LB = dict(zip(TAGS, [u'1.2 协议', u'旧建议', u'1.3 协议', u'新建议']))
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
             (u'collections.', u'_cl.')):
    BODYTXT = re.sub(u'(?<![.\\w])' + re.escape(a), b, BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert u'_os.open(' not in BODYTXT, u'裸 open( 被误改写'

TAIL = u'''
    # ---- 结构性自检: 排他闭合、两口径搬运、桥与引用方向、形状档 ----
    assert F[u'kw_close'] == [0, 0, 0, 0] and F[u'kw_close2'] == [0, 0, 0, 0] and F[u'kw_close3'] == [0, 0, 0, 0]
    assert F[u'kw_mix'] == [0, 0, 0, 0] and F[u'kw_mix_docs'] == 0 and F[u'kwbullet_num'] == [0, 0, 0, 0]
    assert F[u'pool_close'] == 0 and F[u'pool_tiers'] == [F[u'pool_1'], F[u'pool_2'], F[u'pool_3'], F[u'pool_4']]
    assert F[u'carry_close'] == 0 and F[u'carry_sent_close'] == 0 and F[u'carry_split_close'] == 0
    assert F[u'carry_thr_192'] == 0 and F[u'carry_thr_224'] == 0 and F[u'carry_sent_rat'] == 0
    assert F[u'carry_sub_overlap'] == F[u'carry_o_in_n_text'] + F[u'carry_n_in_o_text']
    assert F[u'carry_caliber_gap'] == F[u'carry_shared_raw'] - F[u'carry_sent_shared']
    assert (F[u'carry_shared_ref'] + F[u'carry_shared_toc'] + F[u'carry_shared_prose']
            == F[u'carry_shared_raw'])
    assert F[u'suite_bridge_close'] == 0 and F[u'suite_O_bridge_close'] == 0
    assert F[u'suite_common_TF'] == 0 and F[u'suite_from_N_in_F'] == 0 and F[u'suite_from_O_in_F'] == 0
    assert F[u'suite_from_N_in_T'] + F[u'suite_from_N_in_F'] + F[u'suite_from_N_in_none'] == F[u'suite_N_total']
    assert F[u'suite_from_O_in_T'] + F[u'suite_from_O_in_F'] + F[u'suite_from_O_in_none'] == F[u'suite_O_total']
    assert F[u'cite_pairs_nonzero'] + F[u'cite_pairs_zero'] == F[u'cite_pairs_total']
    assert F[u'cite_backward_violations'] == 0 and F[u'cite_rfc_pairs_nonzero'] == F[u'cite_pairs_nonzero']
    assert F[u'cite_obsoleted_inrepo_all'] == sum(F[u'cite_obsoleted_inrepo'])
    assert F[u'sp_case_variants'] == [3, 0, 2, 1] and F[u'sp_md5sha1'] == [0, 0, 0, 0]
    assert F[u'sp_total_sha1_family'] == [F[u'sp_sha1_hy'][k] + F[u'sp_sha1_lower'][k]
                                         + F[u'sp_hmac_sha1'][k] + F[u'sp_sha1_net'][k] for k in range(4)]
    assert F[u'line_sha_mustnot'] == [0, 0, 1, 1] and F[u'line_sha_in_enum'] == [0, 0, 5, 0]
    assert F[u'bits_192'] == [0, 1, 0, 0] and F[u'bits_224'] == [0, 0, 0, 1]
    assert F[u'curves_below_224'] == [0, 0, 0, 1] and F[u'line_rationale_mustnot'] == [0, 7, 0, 8]
    assert F[u'id_enum_lines'] == [0, 0, 32, 0] and F[u'id_sha1_schemes'] == [0, 0, 4, 0]
    assert F[u'id_must_support_sha1'] == 0 and F[u'id_dsa_sha1'] == [0, 0, 0, 0]
    assert F[u'id_legacy_block'] == [0, 0, 4, 0] and F[u'id_rsa_pss_rsae_sha256'] == [0, 0, 4, 0]
    assert F[u'tabs'] == [0, 0, 0, 0] and F[u'trailws'] == [0, 0, 0, 0] and F[u'crlf'] == [0, 0, 0, 0]
    assert F[u'nonascii'] == [0, 0, 0, 14] and F[u'bytegap'] == [0, 0, 0, 15] and F[u'bom'] == [0, 0, 0, 1]
    assert F[u'utf8_strict'] == [1, 1, 1, 1] and F[u'eqb'] == 3 and F[u'ascii_eq'] == [1, 1, 1, 0]
    assert F[u'maxlen'] == [72, 72, 72, 72] and F[u'sha_distinct'] == 4
    assert F[u'pagemarks'] == [104, 27, 160, 0] and F[u'hdr'] == [103, 26, 159, 0]
    assert F[u'page_gap'] == [1, 1, 1, 0] and F[u'author_hdr'] == [1, 1, 1, 0]
    assert F[u'date_seg_ok'] == [1, 1, 1] and F[u'month_gap_prev'][1:] == [81, 39, 51]
    assert sum(F[u'month_gap_prev'][1:]) == F[u'month_span']
    assert F[u'date_docnum_mono'] == F[u'date_seg_n'] == 3

    # ---- 锚归属: 从条目正文的“源标签紧接原子引文”配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B57_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B57: 正文里没有带标签的锚'
    assert len(re.findall(u'⟨', enc)) == len(CITES), u'B57: 有锚没带源标签'
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

_B57 = _b57_scan()
B57V = lambda k, i=None: (_B57[k] if i is None else _B57[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b57 block>', 'exec')

o = NL + u'_B56 = _b56_scan()'
assert S.count(o) == 1, u'anchor _b56_scan'
B57ENV = u'B56V=B56V,' + NL + u'               B57V=B57V)'
i0 = S.find(u'# B57: 同一个签名哈希')          # 幂等: 按标记整段摘除, 不靠全文逐字相等(改注释也该认得出来)
while i0 >= 0:
    i1 = S.index(u'_B56 = _b56_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B57: 同一个签名哈希')
if B57ENV in S:
    S = S.replace(B57ENV, u'B56V=B56V)')
S = S.replace(o, BLK + o)
assert S.count(u'B56V=B56V)') == 1, u'anchor env'
S = S.replace(u'B56V=B56V)', B57ENV)

PS = u"SRC['B56'] = ["
blk = (u"SRC['B57'] = ['corpus/raw/ietf/rfc5246.txt', 'corpus/raw/ietf/rfc7525.txt', "
       u"'corpus/raw/ietf/rfc8446.txt', 'corpus/raw/ietf/rfc9325.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B55', 'B56'}", u"'B55', 'B56', 'B57'}"
if NEW not in S:
    assert S.count(OLD) == 1, u'anchor ATOM'
    S = S.replace(OLD, NEW)

M1 = u'# ---- B57 DERIV (generated by corpus/_wire57.py from corpus/_deriv57.json; do not hand-edit) ----'
M2 = u'# ---- /B57 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv57.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B57'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B57': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b57 block>', 'exec'), NS)
env = NS['B57V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b57flat.json', encoding='utf-8'))


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
        got = eval(v, dict(NS), {'B57V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b56_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b57_scan+B57V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values()),
         env('anchor_total'), env('anchor_distinct'), env('checks')))
