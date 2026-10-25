# -*- coding: utf-8 -*-
"""把 B56 的独立复算器(_b56_scan / B56V)接进 audit.py, 并生成 DERIV['B56']。
幂等: 重复运行先摘旧块再插新块。
_b56_scan 的量测段从 corpus/_mkB56.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自三处:
①采集侧 corpus/_pick56.py 是先于建条目写好的另一套实现(它按 split 制表符解析码表、按逐行状态机切注册表),
  两边在 TIE 表上逐量对账(条数见 _b56checks.json 的 meas_tie_keys);
②抽出的代码在插门之前要把 _b56flat.json 的每个键与 DERIV['B56'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里“源标签紧接原子引文”的配对现推, 三源一律按原文件行归一后判成员。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB56.py', encoding='utf-8').read()
NL = chr(10)
RAWS = ['corpus/raw/tz/iso3166.tab', 'corpus/raw/tz/zone1970.tab', 'corpus/raw/langsubtag.txt']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'def pnorm(s):', u'# --- SCAN END ---')
assert u'F[u' in MEAS and u'POOL' in MEAS and u'cmt_contig' in MEAS and u'rz_alpha' in MEAS

HEAD = u'''
# B56: 同一批 ISO 3166 两位码在三张表里各有身份——raw/tz/iso3166.tab(码表, 名写成第二列, 命名理由写在自己的注释里)
# ⇎ raw/tz/zone1970.tab(时区表, 第一列借同一批码, 却没有名字列) ⇎ raw/langsubtag.txt(BCP 47 注册表的 region 型切片, 码集比码表大)。
# 本函数从三份字节独立复算: 字节/换行/非空/'<'/'>'/制表符/'#'行/非 ASCII/弯引号/sha16 种数,
# 码表的严格两列正则命中与制表符枚数由列结构反推, 注释自写四律与三条命名理由的点名串两头判, 名排序与同干连块,
# 名字层的三向 join(按码逐码比名 ⇎ 按名串取交 ⇎ 按标识符碎片存活), 只换写法⇎换了词的分档,
# 集含方向的三向差集全闭合与跨条目桥数, 弃用分向账, 注释共用句的整行⇎接行⇎逐字连续三口径,
# 关键串三源矩阵与锚候选池, 锚归属由条目正文现推。
# 不可由在库文件判定的: 三份字节的磁盘 mtime 与注释里那几个日期谁新谁旧(只在本机成立)、
# ISO 官方此刻在用的名串(文件只给两份表各自的写法)、注册表把旧名留在已弃码上的流程理由。
def _b56_scan():
    import hashlib as _hl
    import os as _os
    P2 = SRC['B56']
    TAGS = [u'I', u'Z', u'R']
    LB = dict(zip(TAGS, [u'码表', u'时区表', u'子标签注册表']))
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
    # ---- 结构性自检: 每处闭合、两口径差、命名理由两头判 ----
    assert F[u'i_rows_unmatched'] == 0 and F[u'i_multi_tab'] == 0 and F[u'i_tab_diff'] == 0
    assert F[u'i_claim_open'] == 0 and F[u'i_stem_close'] == 0 and F[u'i_samoa_gap'] == 0
    assert F[u'i_code_dup'] == 0 and F[u'i_name_dup'] == 0 and F[u'i_sorted_desc'] == 0
    assert F[u'z_tier_close'] == 0 and F[u'z_us_close'] == 0
    assert F[u'r_len_close'] == 0 and F[u'r_only_i_close'] == 0 and F[u'r_alpha_close'] == 0
    assert F[u'bridge'] == 0 and F[u'z_in_i_close'] == 0 and F[u'i_in_r_close'] == 0
    assert F[u'dep_close'] == 0 and F[u'shared_dep'] == 0 and F[u'z_only_i'] == 0 and F[u'i_only_r'] == 0
    assert F[u'name_lex_close'] == 0 and F[u'name_cmp_close'] == 0 and F[u'name_len_close'] == 0
    assert F[u'name_pool_close'] == 0 and F[u'name_amp_close'] == 0 and F[u'r_sep_gap'] == 0
    assert F[u'cmt_contig_close'] == 0 and F[u'key_close'] == 0 and F[u'key_pair_close'] == 0
    assert F[u'pool_close'] == 0 and F[u'curly_close'] == 0
    assert F[u'ascii_eq'] == [0, 0, 0] and F[u'i_utf8_strict'] == 1 and F[u'i_leap'] == 1
    assert F[u'sha_distinct'] == 3 and F[u'eqc'] == 0
    assert F[u'i_hdr_split'] == 1 and F[u'i_hdr_cc'] == 0 and F[u'cmt_line_shared'] == 1
    assert F[u'cmt_sent_shared'] == 4 and F[u'cmt_contig_both'] == 1
    assert F[u'name_lex'] == 10 and F[u'name_cross'] == 2
    assert F[u'name_amp_all'] == 11 and F[u'name_lex_amp'] == 8
    assert F[u'bytegap'] == [55, 56, 742]
    assert F[u'z_cc_dist'] + F[u'i_only_z'] == F[u'i_code_n']
    assert F[u'i_code_n'] + F[u'r_only_i'] == F[u'r_region_n']

    # ---- 锚归属: 从条目正文的“源标签紧接原子引文”配对现推, 三源都按原文件行判成员 ----
    ep = glob.glob(u'corpus/babeltele/B56_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B56: 正文里没有带标签的锚'
    assert len(re.findall(u'⟨', enc)) == len(CITES), u'B56: 有锚没带源标签'
    ERR = [x for x in CITES if not pnorm(x[1]) or pnorm(x[1]) not in FAN[IDX[x[0]]]]
    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [tuple(i for i in range(3) if pnorm(a) in FAN[i]) for a in DIS]
    F[u'anchor_total'] = len(CITES)
    F[u'anchor_distinct'] = len(DIS)
    F[u'anchor_err'] = len(ERR)
    F[u'anchor_single'] = len([h for h in HC if len(h) == 1])
    F[u'anchor_two'] = len([h for h in HC if len(h) == 2])
    F[u'anchor_three'] = len([h for h in HC if len(h) == 3])
    F[u'checks'] = len(DIS) * 3
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_two'] + F[u'anchor_three'] == len(DIS)
    return F

_B56 = _b56_scan()
B56V = lambda k, i=None: (_B56[k] if i is None else _B56[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b56 block>', 'exec')

o = NL + u'_B56 = _b56_scan()'
o4 = NL + u'_B55 = _b55_scan()'
assert S.count(o4) == 1, u'anchor _b55_scan'
B56ENV = u'B55V=B55V,' + NL + u'               B56V=B56V)'
if BLK in S:
    S = S.replace(BLK, u'')
if B56ENV in S:
    S = S.replace(B56ENV, u'B55V=B55V)')
S = S.replace(o4, BLK + o4)
assert S.count(u'B55V=B55V)') == 1, u'anchor env'
S = S.replace(u'B55V=B55V)', B56ENV)

PS = u"SRC['B55'] = ["
blk = u"SRC['B56'] = ['corpus/raw/tz/iso3166.tab', 'corpus/raw/tz/zone1970.tab', 'corpus/raw/langsubtag.txt']\n"
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B54', 'B55'}", u"'B54', 'B55', 'B56'}"
if NEW not in S:
    assert S.count(OLD) == 1, u'anchor ATOM'
    S = S.replace(OLD, NEW)

M1 = u'# ---- B56 DERIV (generated by corpus/_wire56.py from corpus/_deriv56.json; do not hand-edit) ----'
M2 = u'# ---- /B56 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv56.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B56'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B56': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b56 block>', 'exec'), NS)
env = NS['B56V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b56flat.json', encoding='utf-8'))


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
        got = eval(v, dict(NS), {'B56V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b55_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b56_scan+B56V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values())))
