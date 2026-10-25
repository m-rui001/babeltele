# -*- coding: utf-8 -*-
"""把 B54 的独立复算器(_b54_scan / B54V)接进 audit.py, 并生成 DERIV['B54']。
幂等: 重复运行先摘旧块再插新块。
_b54_scan 的量测段从 corpus/_mkB54.py 的现算段( SCAN BEGIN ⇎ SCAN END 两根标记之间)逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自三处:
①采集侧 corpus/_pick54.py 是先于建条目写好的另一套实现, 两边在 47 个量上对过账(见 _mkB54 的 TIE 块);
②抽出的代码在插门之前要把 _b54flat.json 的每个键与 DERIV['B54'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里“源标签紧接原子引文”的配对现推, 两源一律按原文件行归一后判成员。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB54.py', encoding='utf-8').read()
NL = chr(10)
RAWS = ['corpus/raw/codata_table.html', 'corpus/raw/codata_all.html']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'def pnorm(s):', u'TIE = [')
assert u'F[u' in MEAS and u'align_eq' in MEAS and u'demo_name' in MEAS

HEAD = u'''
# B54: 同一秒抓下的两份 .html——raw/codata_table.html(自称 Complete Listing, 355 行常数, 0 枚 '<')
# ⇎ raw/codata_all.html(名叫 all, 内容是一页 ill-formed request 错误, 155 枚 '<')。
# 本函数从两份字节独立复算: 行列段/空行/'<'/'>'/非 ASCII/sha16, 定宽列位与断列两法互证, 表头与数据列位差,
# 排序四键阶梯与逆序对, '(exact)' 与 '...' 的分层, 小数位对齐, 分组与指数记法, 单位列两遍计数,
# 错误页的标签/注释/属性/一次性短语计数, 那枚 base64 挑战串的时刻, 穿两源关键串矩阵与锚归属。
# 不可由在库文件判定的: 错误页由哪一次请求造成、哪个入口才是这份清单的正身、磁盘 mtime 是否等于抓取时刻(只在本机成立)。
def _b54_scan():
    import hashlib as _hl
    import os as _os
    import collections as _cl
    import base64 as _b64
    import datetime as _dt
    P2 = SRC['B54']
    TAGS = [u'T', u'E']
    LB = dict(zip(TAGS, [u'完整清单', u'错误页外壳']))
    PATH = P2
    IDX = dict((t, i) for i, t in enumerate(TAGS))
    RD = lambda p: io.open(p, encoding='latin-1').read()
    TXT = [RD(p) for p in PATH]
    ROOT = u''
    C = u'corpus'
    NL = chr(10)
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
for a, b in ((u'os.path.join(ROOT, C, ', u'_os.path.join(C, '), (u'os.path.getsize(', u'_os.path.getsize('),
             (u'hashlib.', u'_hl.'), (u'collections.', u'_cl.'), (u'base64.', u'_b64.'),
             (u'datetime.', u'_dt.')):
    BODYTXT = re.sub(u'(?<![.\\w])' + re.escape(a), b, BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT), u'仍有裸 open('
assert u'_os.open(' not in BODYTXT, u'裸 open( 被误改写'

TAIL = u'''
    # ---- 结构性自检: 两法互证、分档相加、记数法互补 ----
    assert F[u'impl_diff'] == 0 and F[u'unit_diff'] == 0
    assert F[u'exact_rows'] + F[u'meas_rows'] + F[u'no_unc'] == F[u'rows']
    assert F[u'ell_out_exact'] == 0 and F[u'ell_rows'] == F[u'ell_in_exact']
    assert F[u'align_rows'] == F[u'meas_rows'] and F[u'align_eq'] + F[u'align_ne'] == F[u'align_rows']
    assert F[u'exp_minus'] + F[u'exp_unsigned'] + F[u'exp_plus'] == F[u'exp_any']
    assert F[u'hitboth'] + F[u'hitsingle'] + F[u'hitnone'] == F[u'hitkinds']
    assert len(set(F[u'sha16'])) == 2 and F[u'ascii_eq'] == 2
    assert F[u'grp_frac_not3'] == F[u'grp_frac_n'] - F[u'grp_frac_3']
    assert F[u'cross_rows'] == 0 and F[u'url_shared'] == 0

    # ---- 锚归属: 从条目正文的“源标签紧接原子引文”配对现推, 两源都按原文件行判成员 ----
    ep = glob.glob(u'corpus/babeltele/B54_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B54: 正文里没有带标签的锚'
    assert len(re.findall(u'⟨', enc)) == len(CITES), u'B54: 有锚没带源标签'
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

_B54 = _b54_scan()
B54V = lambda k, i=None: (_B54[k] if i is None else _B54[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b54 block>', 'exec')

o = NL + u'_B52 = _b52_scan()'
assert S.count(o) == 1, u'anchor _b52_scan'
B54ENV = u'B53V=B53V,' + NL + u'               B54V=B54V)'
if BLK in S:
    S = S.replace(BLK, u'')
if B54ENV in S:
    S = S.replace(B54ENV, u'B53V=B53V)')
S = S.replace(o, BLK + o)
assert S.count(u'B53V=B53V)') == 1, u'anchor env'
S = S.replace(u'B53V=B53V)', B54ENV)

PS = u"SRC['B53'] = ["
blk = u"SRC['B54'] = ['corpus/raw/codata_table.html', 'corpus/raw/codata_all.html']\n"
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B52', 'B53'}", u"'B52', 'B53', 'B54'}"
if NEW not in S:
    assert S.count(OLD) == 1, u'anchor ATOM'
    S = S.replace(OLD, NEW)

M1 = u'# ---- B54 DERIV (generated by corpus/_wire54.py from corpus/_deriv54.json; do not hand-edit) ----'
M2 = u'# ---- /B54 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv54.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B54'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B54': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b54 block>', 'exec'), NS)
env = NS['B54V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b54flat.json', encoding='utf-8'))
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
        got = eval(v, dict(NS), {'B54V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b52_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b54_scan+B54V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values())))
