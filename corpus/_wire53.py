# -*- coding: utf-8 -*-
"""把 B53 的独立复算器(_b53_scan / B53V)接进 audit.py, 并留出 DERIV['B53'] 的生成块位。
幂等: 重复运行先摘旧块再插新块。
_b53_scan 的量测段从 corpus/_mkB53.py 的现算段机械抽出(逐行原样搬入 audit, 只在头部换成 audit 自己的路径常量),
真正的独立性来自两处: ①采集侧 corpus/_pick53.py 是先于建条目写好的另一套实现, 两边在 15 个量上对过账(见 _mkB53 的 TIE 块);
②抽出后的代码在插门之前要把 _b53flat.json 的每一个键与 DERIV['B53'] 的每一条表达式重跑一遍, 值不符就当场停机。
锚的归属由条目正文的“源标签紧接原子引文”配对现推: 落地页按原文件的行判成员, 其余三层按去标签正文判(与建条目侧同一处口径)。"""
import io, os, re, sys, json

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB53.py', encoding='utf-8').read()
NL = chr(10)


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


Q = chr(34)
MEAS = cut(u'def pnorm(s):', u'TIE = [')
GL = cut(u"# 那一行里", u"G[u'aTtl']")
assert u'F[u' in MEAS and u'gl_opl' in GL

HEAD = u'''
# B53: 同一份 FIPS 202 的四种序列化——官方 txt ⇎ 本机 pdftotext -layout ⇎ 本机 pdftotext raw ⇎ 官方 CSRC 落地页 html。
# 四份文件的行/列/字节口径、码点存活表、骨架四口径配对、折叠空白后的公共片段、html 两种正文、穿层矩阵与锚归属,
# 全部由本函数从四份 raw 与条目正文独立复算; 采集侧 corpus/_pick53.py 另写一遍并与本函数在 15 个量上对账,
# 建条目侧 corpus/_mkB53.py 的现算段被逐行搬进这里, 插门前先把 _b53flat.json 的每个键重跑一遍。
# “哪一种序列化才算这份标准的正文”“⊕ 在 PDF 里本来是什么”不在本函数的能力范围内: 库里没有渲染物, 只有 {pp} 页 {ps} 个流的字节统计。
def _b53_scan():
    import hashlib as _hl
    import os as _os
    import subprocess as _sp
    P4 = SRC['B53']
    TAGS = [u'T', u'L', u'P', u'H']
    LB = dict(zip(TAGS, [u'官方纯文本', u'本机按版式', u'本机无版式', u'官方落地页']))
    PATH = P4
    IDX = dict((t, i) for i, t in enumerate(TAGS))
    RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
    TXT = [RD(p) for p in PATH]
    ROOT = u''
    C = u'corpus'
    NL = chr(10)
    SHA = lambda t: _hl.sha256(t.encode('utf-8')).hexdigest()
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in (MEAS + GL).split(NL))
# 抽出段里用到的绝对路径写法在 audit 里按相对路径成立
BODYTXT = BODYTXT.replace(u'os.path.join(ROOT, C, ', u'_os.path.join(C, ').replace(u'os.path.getsize(', u'_os.path.getsize(')
BODYTXT = BODYTXT.replace(u'hashlib.', u'_hl.')

TAIL = u'''
    # ---- 可复现性: 本机两份现生两遍, 产物须字节相同; 官方两份只数“下载来的有几份” ----
    PDFC = u'corpus/raw/fips202.pdf'
    RG = []
    for i, fl in ((1, [u'-layout']), (2, [])):
        outs = []
        for _ in range(2):
            tmp = u'corpus/raw/_b53re%d.txt' % i
            _sp.run([u'pdftotext'] + fl + [PDFC, tmp], check=True)
            outs.append(SHA(RD(tmp)))
        os.remove(tmp)
        RG.append(outs[0] == outs[1] == SHA(TXT[i]))
    assert all(RG), RG
    F[u'regen_both'] = 1 if all(RG) else 0

    # ---- 单调性与口径自检 ----
    assert F[u'pair_tl_raw'] <= F[u'pair_tl_strip'] <= F[u'pair_tl_skel'] <= F[u'pairtotal']
    assert F[u'pair_th_raw'] <= F[u'pair_th_strip'] <= F[u'pair_th_skel'] <= F[u'pairtotal']
    assert F[u'gap_tl'] == F[u'pair_tl_skel'] - F[u'pair_tl_strip']
    assert F[u'setdiff_ab'] == [F[u'wsetb'][i] - F[u'wseta'][i] for i in range(4)]
    assert F[u'stepwrap'] == F[u'stepsoft'][0] - F[u'step'][0]
    assert F[u'hkw_lost'] == F[u'hkw_raw'] - F[u'hkw_body']
    assert F[u'html_uswds_body'] == 0 and F[u'html_uswds_raw'] > 0
    assert F[u'fffd'][1] == F[u'nonascii'][1] and F[u'fffd'][2] == F[u'nonascii'][2]
    assert F[u'gen_n'] + F[u'dl_n'] == F[u'nsrc']

    # ---- 锚归属: 从条目正文的“源标签紧接原子引文”配对现推, 不读旁注文件 ----
    ep = glob.glob(u'corpus/babeltele/B53_*.md')
    assert len(ep) == 1, ep
    T = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', T, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B53: 正文里没有带标签的锚'

    def hitset(a):
        n = pnorm(a)
        return tuple(i for i in range(4) if n and n in FA[i])

    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [hitset(a) for a in DIS]
    F[u'anchor_total'] = len(CITES)
    F[u'anchor_distinct'] = len(DIS)
    F[u'anchor_err'] = len([h for h in HC if not h])
    F[u'anchor_single'] = len([h for h in HC if len(h) == 1])
    F[u'anchor_cross'] = len([h for h in HC if 1 < len(h) < 4])
    F[u'anchor_all4'] = len([h for h in HC if len(h) == 4])
    F[u'checks'] = len(DIS) * 4
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all4'] + F[u'anchor_err'] == len(DIS)
    return F

_B53 = _b53_scan()
B53V = lambda k, i=None: (_B53[k] if i is None else _B53[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b53 block>', 'exec')

o = u'\n_B52 = _b52_scan()'
o2 = u'B52V=B52V)'
o2b = u'B52V=B52V,\n               B53V=B53V)'
if BLK in S:
    S = S.replace(BLK, u'')
if o2b in S:
    S = S.replace(o2b, o2)
assert S.count(o) == 1, u'anchor _b52_scan'
S = S.replace(o, BLK + o)
assert S.count(o2) == 1, u'anchor env'
S = S.replace(o2, o2b)

PS = u"SRC['B52'] = ["
blk = (u"SRC['B53'] = ['corpus/raw/fips202.txt', 'corpus/raw/fips202_pdflayout.txt',\n"
       u"            'corpus/raw/fips202_plain.txt', 'corpus/raw/fips202.html']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD = u"'B51', 'B52'}"
NEW = u"'B51', 'B52', 'B53'}"
if NEW not in S:
    assert S.count(OLD) == 1, u'anchor ATOM'
    S = S.replace(OLD, NEW)

M1 = u'# ---- B53 DERIV (generated by corpus/_mkB53.py; do not hand-edit) ----'
M2 = u'# ---- /B53 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv53.json', encoding='utf-8'))
body = M1 + NL + u"DERIV['B53'] = " + repr(J) + NL + M2 + NL
S = S.replace(o3, body + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B53': ['corpus/raw/fips202.txt', 'corpus/raw/fips202_pdflayout.txt',
                      'corpus/raw/fips202_plain.txt', 'corpus/raw/fips202.html']},
      're': re, 'io': io, 'os': os, 'glob': __import__('glob')}
exec(compile(BLK, u'<b53 block>', 'exec'), NS)
env = NS['B53V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b53flat.json', encoding='utf-8'))
for k, v in FLAT.items():
    try:
        got = env(k)
    except Exception as e:
        BAD.append((k, repr(e)))
        continue
    if got != v:
        MISMATCH.append((k, v, got))
assert not BAD, BAD
assert not MISMATCH, MISMATCH[:6]
for kk, v in J.items():
    try:
        got = eval(v, dict(NS), {'B53V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert len(S) > 100000 and u'_b52_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: scan+env+DERIV(%d keys, 扁平键 %d 个逐一对账, 预演全对)' % (len(J), len(FLAT)))
