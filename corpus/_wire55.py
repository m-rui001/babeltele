# -*- coding: utf-8 -*-
"""把 B55 的独立复算器(_b55_scan / B55V)接进 audit.py, 并生成 DERIV['B55']。
幂等: 重复运行先摘旧块再插新块。
_b55_scan 的量测段从 corpus/_mkB55.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自三处:
①采集侧 corpus/_pick55.py 是先于建条目写好的另一套实现, 两边在 TIE 表上逐量对账(条数见 _b55checks.json 的 meas_tie_keys);
②抽出的代码在插门之前要把 _b55flat.json 的每个键与 DERIV['B55'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里“源标签紧接原子引文”的配对现推, 两源一律按原文件行归一后判成员。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB55.py', encoding='utf-8').read()
NL = chr(10)
RAWS = ['corpus/raw/langsubtag.txt', 'corpus/raw/tz/zone1970.tab']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'def pnorm(s):', u'# --- SCAN END ---')
assert u'F[u' in MEAS and u'pref_out' in MEAS and u'z4_agree' in MEAS and u'POOL2' in MEAS

HEAD = u'''
# B55: 一张表 ⇎ 一张借它的码当列值的表——raw/langsubtag.txt(BCP 47 子标签注册表, 段分隔是一行两个 '%')
# ⇎ raw/tz/zone1970.tab(时区表, 国家列用的正是注册表 region 型子标签)。
# 本函数从两份字节独立复算: 字节/换行/段/'<'/制表符/'#'行/非 ASCII/sha16, 段结构与字段面(逐行 ⇎ 折叠两种口径),
# 四个交叉引用字段的值域在整码判 ⇎ 拆片判两种口径下的越界数, 子标签长度签名与类型内分布, Description 复用,
# Added/Deprecated 日期账, region 池(两位码 ⇎ UN 数字码 ⇎ 区间)与 Z 国家列的双向差集, Z 注释自写三条规则的核对,
# 制表符枚数由列结构反推, 穿两源关键串矩阵与锚归属。
# 不可由在库文件判定的: 注册表与磁盘 mtime 谁新谁旧(只在本机成立)、这套值域约束在 RFC 正文里如何表述、
# 区间码是“保留段”还是“私用段”的名义归属(文件只给码与 Description)。
def _b55_scan():
    import hashlib as _hl
    import os as _os
    import collections as _cl
    P2 = SRC['B55']
    TAGS = [u'R', u'Z']
    LB = dict(zip(TAGS, [u'子标签注册表', u'时区表']))
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
    # ---- 结构性自检: 封闭性相加、两口径差全归因、注释规则零反例 ----
    assert F[u'sep_gap'] == 0 and F[u'closed'] == 0 and F[u'reg_sum'] == 0
    assert F[u'viol_minus_comp'] == 0 and F[u'sl_sum'] == 0 and F[u'z_col_sum'] == 0
    assert F[u'z_coord_sum'] == 0 and F[u'z_tab_diff'] == 0 and F[u'z_badfmt'] == 0
    assert F[u'z_zone_dup'] == 0 and F[u'scope_sum'] == 0 and F[u'reg_only_sum'] == 0
    assert F[u'z4_pos'] == 0 and F[u'z4_neg'] == 0 and F[u'x_verbatim'] == 0
    assert F[u'other_extra'] == 0 and F[u'viol_piece'] == 0
    assert F[u'field_lines'] == F[u'colon'][0] and F[u'colon'][1] == 0
    assert F[u'z4_agree'] == F[u'z_rows'] and F[u'z_shared_rows'] == F[u'z_col4']
    assert F[u'x_normonly'] == F[u'pool_cross'] and F[u'z_only'] == 0
    assert len(set(F[u'sha16'])) == 2 and F[u'eqc'] == 0
    assert F[u'reg_shared'] + F[u'z_only'] == F[u'z_countries']
    assert F[u'reg_alpha_only'] + F[u'reg_digit_only'] + F[u'reg_range_only'] == F[u'reg_only']

    # ---- 锚归属: 从条目正文的“源标签紧接原子引文”配对现推, 两源都按原文件行判成员 ----
    ep = glob.glob(u'corpus/babeltele/B55_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B55: 正文里没有带标签的锚'
    assert len(re.findall(u'⟨', enc)) == len(CITES), u'B55: 有锚没带源标签'
    ERR = [x for x in CITES if not pnorm(x[1]) or pnorm(x[1]) not in FAN[IDX[x[0]]]]
    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [tuple(i for i in range(2) if pnorm(a) in FAN[i]) for a in DIS]
    F[u'anchor_total'] = len(CITES)
    F[u'anchor_distinct'] = len(DIS)
    F[u'anchor_err'] = len(ERR)
    F[u'anchor_single'] = len([h for h in HC if len(h) == 1])
    F[u'anchor_both'] = len([h for h in HC if len(h) == 2])
    F[u'checks'] = len(DIS) * 2
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_both'] + F[u'anchor_err'] == len(DIS)
    return F

_B55 = _b55_scan()
B55V = lambda k, i=None: (_B55[k] if i is None else _B55[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b55 block>', 'exec')

o = NL + u'_B55 = _b55_scan()'
o4 = NL + u'_B54 = _b54_scan()'
assert S.count(o4) == 1, u'anchor _b54_scan'
B55ENV = u'B54V=B54V,' + NL + u'               B55V=B55V)'
if BLK in S:
    S = S.replace(BLK, u'')
if B55ENV in S:
    S = S.replace(B55ENV, u'B54V=B54V)')
S = S.replace(o4, BLK + o4)
assert S.count(u'B54V=B54V)') == 1, u'anchor env'
S = S.replace(u'B54V=B54V)', B55ENV)

PS = u"SRC['B54'] = ["
blk = u"SRC['B55'] = ['corpus/raw/langsubtag.txt', 'corpus/raw/tz/zone1970.tab']\n"
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B52', 'B53', 'B54'}", u"'B52', 'B53', 'B54', 'B55'}"
if NEW not in S:
    assert S.count(OLD) == 1, u'anchor ATOM'
    S = S.replace(OLD, NEW)

M1 = u'# ---- B55 DERIV (generated by corpus/_wire55.py from corpus/_deriv55.json; do not hand-edit) ----'
M2 = u'# ---- /B55 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv55.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B55'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B55': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b55 block>', 'exec'), NS)
env = NS['B55V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b55flat.json', encoding='utf-8'))
for k, v in FLAT.items():
    try:
        got = env(k)
    except Exception as e:
        BAD.append((k, repr(e)))
        continue
    if got != v:
        MISMATCH.append((k, v, got))
assert not BAD, BAD[:6]
assert not MISMATCH, MISMATCH[:6]
for kk, v in J.items():
    try:
        got = eval(v, dict(NS), {'B55V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b54_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b55_scan+B55V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values())))
