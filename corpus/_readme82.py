# -*- coding: utf-8 -*-
"""README 记账(B82): 判词段 ⇎ 门槛表行 ⇎ 语料表行 ⇎ 转化指标机械行 ⇎ 合计行 ⇎ 命令块 ⇎ 三处条数陈述,
凡本遍能现量的数一律按本遍现跑的 audit ⇎ 现读的 raw 字节 ⇎ 本遍自己的量尺现数, 与建条目侧的快照逐键对拍;
下面另点名八族只有快照可取的读数, 文中出现时一律标“契约值”。

本遍换机制而不换定义之处:
① 面量走字节平面(`bytes.count(b'\\n')` ⇎ `b'\\x0c'` ⇎ `b'\\r'` ⇎ BOM 看前三字节), 行式五档由本遍现读;
② 壳尺走整行序列正则(`^RFC1122 +\\S` ⇎ `\\[Page \\d+\\]` ⇎ 空行), 建条目侧是折叠后逐 token 比形状, 两把尺的剥壳行数须同值;
③ 判词针: 第一档按“某行的归一面含此针”数行处, 第二至四档用游标 find 环数出现枚(建条目侧是转义正则 findall);
④ 义务词整词尺用邻居字符手扫(建条目侧是 `(?<![A-Za-z])` 断言正则);
⑤ 跨行义务词行对: 本遍按每行 token 列的末词 ⇎ 首词判定, 建条目侧在折叠串上比 endswith/startswith;
⑥ 切开两半: 本遍另建一张 token→原行字符跨度尺, 末半再按“数出第 N 个非空格字符”逐字符扫定针尾(建条目侧用逐行索引表 `ALN` 的折平→原行映射);
⑦ 锚不用正则配对: 按 `⟦` 分段手吃 `⟨…⟩`, 止于 `## ⛓解读注`, 再逐枚回全文归一面做归属;
   行号歧义有两把尺——本遍按“处”数（同一串挂几个标签算几次）, 建条目侧按它逐针导出时数的（`anchor_ambiguous`）, 两值同栏印出而不共用键;
   反向对照的过读要分两档: 排除份被子串尺点着的 6 次(15 枚)是“换尺即失效”, 主家侧两尺之差 162 枚另计, 相加才是 SUBFALSE;
⑧ 模板长行池的折叠用无参 `split()`(建条目侧用 `re.split(r'\\s')` 滤空再 join);
⑨ 摘要在副本上按 README 里那一组 300/200 窗重建, 与在库文件在 `## ⛓解读注` 之前逐字符相同才允许把该命令写进 README;
   重建自报的逐份锚数(面尺)由本遍按面重扫对拍, 与引用尺(每个锚只归一家)差额单列而不混作同一档;
⑩ 唯一码点不抄 audit 的 ALL 行: 逐条现数并与 audit 的编码列对拍后取本表所列条目的并集;
   条数三处陈述全部由本遍现读的文件系统行集与 audit 自报数现算, 不做硬编码加减;
⑪ 判词针与采集侧两串清单(30 ⇎ 20 枚)对拍: 两串的下标各是它自己清单的位置, 与本遍 37 枚针集不同轴,
   只能按串对齐(清单由 ast 从采集侧脚本现取), 落在本遍针集外的 8 ⇎ 5 枚如实印出而不算不符;
⑫ DERIV 276 式在本遍就地重算: 先验每枚 B82V 引用的键确在契约里, 再逐式对键;
   JSON 往返把采集侧 tuple 打成 list 的那一枚按括号形还原, 单独计数而不混入“直接相等”。
⑬ 改写既有的条数陈述时, 替换文本的括号净数须与被吞的原文一致: 在库那句现多一枚闭括号——上一遍的定位式只吞到第一枚
   闭括号, 替换文本却写两枚, 于是每跑一遍就多留一枚; 本遍把定位式扩到连吞三枚闭括号再只写两枚, 并对改后的整行断言 ( ⇎ ) 等数;
   族级读数的族名不手抄枚数, 由 FAMC 逐条配一枚契约键列出, 印出的“共N族”取 len(FAMC)。
族级读数(节窗 ⇎ 9293 相对 1122 的对齐账含段内标注枚数 ⇎ 关键词模板段的逐对共头共尾 ⇎ “RFC nnnn”式引用 ⇎
带单位数值的宽严两尺 ⇎ 建条目侧按针数出的行号歧义档 ⇎ 抬头年 ⇎ BOM 剥壳后存活枚数)取采集侧契约——七族在扁平契约,
行号歧义档那族在 checks 档, 门槛侧由 DERIV 现算;
采集⇎建条目两轨的对账本遍不复用采集侧的数: 25 枚标量 ⇎ 74 档针目全部由本遍现量后换尺再对一次。
抬头年在本遍另存一份逐份转写并与契约对拍, 十六进制参数 ⇎ 自家节号引 ⇎ 引用三式各五份由本遍在面上现量后与契约对拍;
   引用三式的谓词照抄采集侧: 方括号式那把尺的 pattern 里含 “RFC” 字样本身（`\\[RFCdddd\\]`）, 若按形状简写成
   `\\[[0-9]{4}\\]` 则五份面上一枚也读不到（0⇎0⇎0⇎0⇎0）——“数对但话错”里最静的一种;
   “十个号里各家引到别家”那列 ⇎ 它背后的引用矩阵本遍不复扫, 只取契约值并在行文里点明这一句。
本遍只把契约与 audit 的行值 ⇎ 本遍现量的面逐枚对拍, 不复算这些族的内部构造。"""
import ast
import glob
import io
import json
import os
import re
import subprocess
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
NSRC = 5
LBL = [u'1122', u'9293', u'9112', u'9113', u'9000']
FAM = [u'old', u'new', u'new', u'new', u'new']
OLDI = [0]
NEWI = [1, 2, 3, 4]
YR = [1989, 2022, 2022, 2022, 2021]
MON = [u'October', u'August', u'June', u'June', u'May']
SRC = [C + u'/raw/tcpRTO/rfc1122.txt', C + u'/raw/tcpTW/rfc9293.txt', C + u'/raw/httpKA/rfc9112.txt',
       C + u'/raw/idle/rfc9113.txt', C + u'/raw/idle/rfc9000.txt']
SHW = [u'`' + p[len(C) + 1:] + u'`' for p in SRC]
ANS5 = [u'词写两小时且默认关', u'同句照登并给义务词编号', u'一个值也不给(不提任何要求)',
        u'不说多久只说服务器可以关', u'给算法不给定值(两端最小 ⇎ ≥3×PTO)']
ENTRY = glob.glob(u'corpus/babeltele/B82_*.md')[0]
FP = json.load(io.open(u'corpus/_b82flat.json', encoding=u'utf-8'))
DER = json.load(io.open(u'corpus/_deriv82.json', encoding=u'utf-8'))
CH = json.load(io.open(u'corpus/_b82checks.json', encoding=u'utf-8'))
AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                     text=True, encoding=u'utf-8').stdout
VERD = [l for l in AUD.split(u'\n') if l.startswith(u'保真门槛(T1 字面 + T2 推导 + T3 码位):')]
assert len(VERD) == 1, VERD
FAILED = [l.split(u':')[0].strip() for l in AUD.split(u'\n') if re.match(u'^  B\\d+: ', l)]
assert u'B82' not in FAILED, FAILED
GATE_PASS = VERD[0].endswith(u'PASS')
S = io.open(u'corpus/README.md', encoding=u'utf-8').read()
NL = u'\r\n' if u'\r\n' in S else u'\n'


def gk(k):
    assert k in FP, k
    return FP[k]


def fmt(n):
    s = u'%d' % n if isinstance(n, int) else u'%g' % n
    if u'.' in s:
        a, b = s.split(u'.', 1)
        return fmt(int(a)) + u'.' + b
    if not s.isdigit() or len(s) <= 3:
        return s
    g = [s[x:x + 3] for x in range(len(s) - 3, -1, -3)][::-1]
    if len(s) % 3:
        g = [s[:len(s) % 3]] + g
    return u' '.join(g)


def num(x):
    return int(u''.join(c for c in x if c.isdigit()))


def V4(v):
    return u'⇎'.join(u'—' if x is None else str(x) for x in v)


def pn(s):
    return u' '.join(s.lower().split())


def fold0(s):
    """本遍折叠尺: 无参 split 再 join(建条目侧是 re.split(r'\\s') 滤空再 join)"""
    return u' '.join(s.split())


def occ(hay, nd):
    """本遍字面针轨: 游标 find 环数非重叠出现枚(建条目侧是转义正则 findall)"""
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def ub0(s, w):
    """本遍整词尺: 邻居字符手扫(建条目侧是 (?<![A-Za-z])/(?!…) 断言正则)"""
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha()):
            c += 1
        i = j + 1


# ---------- ① 字节平面 ⇎ 行式五档 ----------
BS, CH_, LN, LF, SPL, SPLNL, NB, BLK, ML, O72, FFC, EFA, FFL, FFBN, FFE, TNL = ([] for _ in range(16))
CR, NA, NAS, NAT, BOM, DELTA = [], [], [], [], [], []
TS, L, NONSHELL = [], [], []
for p in SRC:
    b = io.open(p, u'rb').read()
    t = b.decode(u'utf-8', u'replace')
    TS.append(t)
    ls = t.split(u'\n')
    L.append([y[:-1] if y.endswith(u'\r') else y for y in ls])
    BS.append(len(b))
    CH_.append(len(t))
    DELTA.append(len(b) - len(t))
    LN.append(len(ls))
    LF.append(b.count(b'\n'))
    SPL.append(len(t.splitlines()))
    SPLNL.append(len(t.split(u'\n')))
    TNL.append(1 if t.endswith(u'\n') else 0)
    FFE.append(1 if t.endswith(u'\x0c') else 0)
    NB.append(len([x for x in L[-1] if x.strip() != u'']))
    BLK.append(len(L[-1]) - NB[-1])
    ML.append(max(len(x) for x in L[-1]))
    O72.append(len([x for x in L[-1] if len(x) > 72]))
    FFC.append(b.count(b'\x0c'))
    EFA.append(len([x for x in L[-1] if x == u'\x0c']))
    FFL.append(len([x for x in L[-1] if x[:1] == u'\x0c']))
    FFBN.append(b.count(b'\x0c\n'))
    CR.append(b.count(b'\r'))
    NA.append(sorted(set(ord(c) for c in t if ord(c) > 127)))
    NAS.append(sum(len(c.encode(u'utf-8')) - 1 for c in t if ord(c) > 127))
    NAT.append(len([c for c in t if ord(c) > 127]))
    BOM.append(1 if L[-1][0][:1] == u'\ufeff' else 0)
for k, v in ((u'bytes', BS), (u'chars', CH_), (u'lines', LN), (u'lf', LF), (u'splitlines', SPL),
             (u'splitnl', SPLNL), (u'nonblank', NB), (u'blank', BLK), (u'maxlen', ML), (u'ff', FFC),
             (u'ff_alone', EFA), (u'ff_led', FFL), (u'ff_before_nl', FFBN), (u'ff_at_eof', FFE),
             (u'trailing_nl', TNL), (u'cr', CR), (u'nonascii', NA), (u'na_total', NAT), (u'bom', BOM),
             (u'end_nl', TNL)):
    assert v == gk(k), (k, v, gk(k))
for i in range(NSRC):
    assert LN[i] == LF[i] + 1 and SPLNL[i] == LN[i], i
    assert CR[i] == 0, i
    assert SPL[i] == LN[i] - TNL[i] + FFBN[i] - FFE[i], (i, SPL[i], LN[i], TNL[i], FFBN[i], FFE[i])
    assert gk(u'row_form_ledger')[i] == 0, i
    assert DELTA[i] == NAS[i], (i, DELTA[i], NAS[i])
    assert (0xFEFF in NA[i]) == bool(BOM[i]), i
    assert NAT[i] >= len(NA[i]) and (not NA[i] or max(NA[i]) <= 0xFFFF), i
assert sum(BOM) == 4 and gk(u'bom_survives') == 4
assert sum(CR) == 0 and O72 == [0] * NSRC and ML == [72] * NSRC
assert sum(NAT) == 18 and sum(NAT[i] for i in OLDI) == 0
assert sum(FFC) == 116 and FFC[0] == 116 and sum(FFC[1:]) == 0

# ---------- ② 壳账: 本遍走整行序列正则 ----------
def shell_seq(x, fam):
    if re.search(u'\\[Page \\d+\\]', x) is not None:
        return True
    if fam == u'old' and re.match(u'^RFC1122 +\\S', x) is not None:
        return True
    return x.strip() == u''


SH = [[shell_seq(x, FAM[i]) for x in L[i]] for i in range(NSRC)]
SL = [len([1 for h in SH[i] if h]) for i in range(NSRC)]
FOOT = [len([x for x, h in zip(L[i], SH[i]) if h and u'[Page' in fold0(x)]) for i in range(NSRC)]
HDR = [len([x for x in L[i] if FAM[i] == u'old' and fold0(x).split(u' ')[0] == u'RFC1122'])
       for i in range(NSRC)]
for k, v in ((u'shell_lines', SL), (u'foot', FOOT), (u'hdr_old', HDR)):
    assert v == gk(k), (k, v, gk(k))
assert gk(u'shell_ledger') == [0] * NSRC
assert [SL[i] - (BLK[i] + FOOT[i] + HDR[i]) for i in range(NSRC)] == [0] * NSRC
PPR = [LN[i] - SL[i] for i in range(NSRC)]
PPNB = [len([x for x, h in zip(L[i], SH[i]) if h and x.strip() != u'']) for i in range(NSRC)]
assert PPR == gk(u'pp_rows') and PPNB == gk(u'pp_shell_nonblank')
assert [PPNB[i] - FOOT[i] - HDR[i] for i in range(NSRC)] == [0] * NSRC
assert gk(u'pp_gap_close') == 0 and gk(u'pp_gap_is_shell_nonblank') == 1
assert [PPR[i] + PPNB[i] - NB[i] for i in range(NSRC)] == [0] * NSRC
NONSHELL = [[x for x, h in zip(L[i], SH[i]) if not h] for i in range(NSRC)]


def digit_runs(x):
    return len(re.findall(u'\\d+', x))


PGN = [len([x for x in L[i] if re.fullmatch(u'[\\s\\d]+', x) and digit_runs(x) == 1 and x.strip() != u''])
       for i in range(NSRC)]
PGS = [len([x for x in L[i] if re.fullmatch(u'[\\s\\d]+', x) and digit_runs(x) == 1 and x.strip() != u''
            and shell_seq(x, FAM[i])]) for i in range(NSRC)]
assert PGN == gk(u'pgnum') and PGS == gk(u'pgnum_shell')
assert [PGN[i] - PGS[i] for i in range(NSRC)] == gk(u'pgnum_overstrip')

# ---------- ③ 四档面 ⇎ 37 枚判词针 ----------
LOW = [pn(t) for t in TS]
SHC = [fold0(NL.join(NONSHELL[i])) for i in range(NSRC)]
LOW_SH = [pn(u' '.join(fold0(x) for x in NONSHELL[i])) for i in range(NSRC)]
assert LOW_SH == [pn(x) for x in SHC]
TAGPAT = re.compile(u' \\((?:MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHLD|ED)-[0-9]+\\)', re.I)
TAGFACE = [TAGPAT.sub(u'', SHC[i]) for i in range(NSRC)]
LOW_TAG = [pn(x) for x in TAGFACE]
assert LOW_TAG == [re.sub(TAGPAT, u'', LOW_SH[i]) for i in range(NSRC)]

MS = io.open(u'corpus/_mkB82.py', encoding=u'utf-8').read()
ROLEN = TONE = PKND = None
for nd in ast.parse(MS).body:
    if isinstance(nd, ast.Assign) and getattr(nd.targets[0], u'id', u'') in (u'ROLEN', u'TONE', u'PKND'):
        v = ast.literal_eval(nd.value)
        if nd.targets[0].id == u'ROLEN':
            ROLEN = v
        elif nd.targets[0].id == u'TONE':
            TONE = v
        else:
            PKND = v
assert ROLEN and TONE and PKND, (ROLEN, TONE, PKND)
assert len(ROLEN) == gk(u'needle_n') == len(CH[u'needles']) and CH[u'needles'] == list(ROLEN)
assert TONE == [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']

R_LINE = [[len([x for x in L[i] if pn(r) in pn(x)]) for r in ROLEN] for i in range(NSRC)]
R_FOLD = [[occ(LOW[i], pn(r)) for r in ROLEN] for i in range(NSRC)]
R_SH = [[occ(LOW_SH[i], pn(r)) for r in ROLEN] for i in range(NSRC)]
R_TAG = [[occ(LOW_TAG[i], pn(r)) for r in ROLEN] for i in range(NSRC)]
for k, v in ((u'role_line', R_LINE), (u'role_fold', R_FOLD), (u'role_sh', R_SH), (u'role_tag', R_TAG)):
    assert v == gk(k), (k, [sum(x) for x in v], [sum(x) for x in gk(k)])
RN = [[sum(x) for x in M] for M in (R_LINE, R_FOLD, R_SH, R_TAG)]
for kk, v in zip((u'role_line_n', u'role_fold_n', u'role_sh_n', u'role_tag_n'), RN):
    assert v == gk(kk), (kk, v, gk(kk))
FACE = [sum(x) for x in RN]
assert FACE == gk(u'face_tot') == [42, 60, 60, 61]
GF = [RN[1][i] - RN[0][i] for i in range(NSRC)]
GS = [RN[2][i] - RN[1][i] for i in range(NSRC)]
GT = [RN[3][i] - RN[2][i] for i in range(NSRC)]
assert GF == gk(u'role_gain_fold') and GS == gk(u'role_gain_sh') and GT == gk(u'role_gain_tag')
assert gk(u'face_gain') == [sum(GF), sum(GS), sum(GT)] == [18, 0, 1]
assert sum(GF) == gk(u'gain_fold_tot') and sum(GS) == gk(u'gain_sh_tot') and sum(GT) == gk(u'gain_tag_tot')
GFD = sum([R_FOLD[i][k] - R_LINE[i][k] for i in range(NSRC) for k in range(len(ROLEN)) if R_LINE[i][k] > 0])
SHD = sum([R_SH[i][k] - R_FOLD[i][k] for i in range(NSRC) for k in range(len(ROLEN)) if R_FOLD[i][k] > 0])
assert GFD == gk(u'gain_fold_dup') and SHD == gk(u'gain_sh_dup') == 0
assert sum(GF) == gk(u'split_wrap_n') + GFD
TAGCUTK = [(i, k) for i in range(NSRC) for k in range(len(ROLEN)) if R_SH[i][k] == 0 and R_TAG[i][k] > 0]
assert TAGCUTK == [tuple(x) for x in gk(u'role_tagcut_keys')] and len(TAGCUTK) == gk(u'split_tagcut_n') == sum(GT)
assert [[k for k in range(len(ROLEN)) if R_SH[i][k] == 0 and R_TAG[i][k] > 0] for i in range(NSRC)] == gk(u'role_tagcut')
assert [SL[i] == BLK[i] for i in NEWI] == [True] * 4 and FOOT[0] == FFC[0] and sum(FOOT[1:]) == 0
FM = len([k for k in range(1, 4) if FACE[k] >= FACE[k - 1]])
assert FM == gk(u'face_mono') == 3
WRAPK = [[k for k in range(len(ROLEN)) if R_LINE[i][k] == 0 and R_FOLD[i][k] > 0] for i in range(NSRC)]
SHELLK = [[k for k in range(len(ROLEN)) if R_FOLD[i][k] == 0 and R_SH[i][k] > 0] for i in range(NSRC)]
assert WRAPK == gk(u'role_wrap') and SHELLK == gk(u'role_shell')
assert [len(x) for x in WRAPK] == gk(u'role_wrap_n') and sum(len(x) for x in SHELLK) == 0
assert sum(len(x) for x in WRAPK) == gk(u'role_line_miss_n') == gk(u'split_n')
assert gk(u'split_ledger') == gk(u'split_n') - gk(u'role_line_miss_n') == 0

# ---------- ④ 义务词 ⇎ 术语 ⇎ 编号: 同定义换尺 ----------
TSH = [[ub0(SHC[i], w) for w in TONE] for i in range(NSRC)]
TLINE = [[sum(ub0(x, w) for x in L[i]) for w in TONE] for i in range(NSRC)]
FOLDC = [fold0(t2) for t2 in TS]
TFOLD = [[ub0(FOLDC[i], w) for w in TONE] for i in range(NSRC)]
TTAG = [[ub0(TAGFACE[i], w) for w in TONE] for i in range(NSRC)]
for k, v in ((u'tone_sh', TSH), (u'tone_line', TLINE), (u'tone_fold', TFOLD), (u'tone_tag', TTAG)):
    assert v == gk(k), (k, v, gk(k))
assert [sum(x) for x in TSH] == gk(u'tone_tot')
TAGRE = re.compile(u'\\b(MUST|SHOULD|MAY|SHLD|ED)-([0-9]+)\\b')
TRAW = [len(TAGRE.findall(t)) for t in TS]
TSHC = [len(TAGRE.findall(x)) for x in SHC]
assert TRAW == gk(u'tag_raw') and TSHC == gk(u'tag_sh') == gk(u'tag_kind_sum') == [0, 237, 0, 0, 0]
assert gk(u'tag_kind_close') == [0] * NSRC and sum(TSHC[i] for i in range(NSRC) if i != 1) == 0
assert [TSH[i][0] - TSH[i][1] for i in range(NSRC)] == gk(u'must_bare')
DROP = [[TSH[i][k] - TTAG[i][k] for k in range(5)] for i in range(NSRC)]
assert DROP == gk(u'tone_drop_tag')
assert [sum(x) for x in DROP] == gk(u'tone_drop_tot') == [0, 79, 0, 0, 0]
assert [DROP[1][0], DROP[1][4]] == [61, 18]
assert [sum(abs(y) for y in DROP[i]) for i in range(NSRC)] == gk(u'tone_drop_tot')
assert gk(u'tone_drop_ledger') == [0] * NSRC
TONE7 = [u'MUST', u'MUST NOT', u'SHOULD NOT', u'SHOULD', u'MAY', u'SHLD', u'ED']
TAGP2 = re.compile(u' \\((MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHLD|ED)-[0-9]+\\)', re.I)
PKIND = [[len([1 for m in TAGP2.finditer(SHC[i]) if m.group(1).upper() == w]) for w in TONE7]
         for i in range(NSRC)]
assert PKIND == [list(x) for x in gk(u'tag_paren_kind')]
assert [sum(x) for x in PKIND] == gk(u'tag_paren')
assert DROP[1][0] == PKIND[1][0] and DROP[1][4] == PKIND[1][4]
assert PKIND[1][5] + PKIND[1][6] == gk(u'tag_paren')[1] - gk(u'tone_drop_tot')[1]
assert PKIND[1][1] + PKIND[1][2] + PKIND[1][3] + PKIND[1][6] == 0
KAPAT = [u'keep-alive', u'keepalive', u'keep alive', u'keeps alive', u'keep-alives',
         u'idle', u'idle timeout', u'inactive', u'persistent', u'acknowledgement',
         u'acknowledgment', u'implementors', u'implementers', u'two hours', u'time out']
SPL_ME = [[occ(LOW[i], p) for p in KAPAT] for i in range(NSRC)]
SPL_W = [[ub0(LOW[i], p) for p in KAPAT] for i in range(NSRC)]
assert SPL_ME == gk(u'spell') and SPL_W == gk(u'spell_word')
GAP = [[SPL_ME[i][k] - SPL_W[i][k] for k in range(len(KAPAT))] for i in range(NSRC)]
assert [x for r in GAP for x in r] == gk(u'spell_ruler_gap')
assert sum([sum(r) for r in GAP]) == gk(u'spell_ruler_gap_tot')
assert [sum(x) for x in SPL_ME] == gk(u'spell_tot')
assert sum([sum(r) for r in GAP]) == sum(gk(u'spell_tot')) - sum([sum(x) for x in SPL_W])
assert [x[0] for x in SPL_ME] == gk(u'ka_hyphen')
assert [x[5] for x in SPL_ME] == gk(u'idle_term') and [x[6] for x in SPL_ME] == gk(u'idle_compound')
assert [x[8] for x in SPL_ME] == gk(u'persist')
assert sum(x[1] for x in SPL_ME) == gk(u'ka_merged') == 0
assert [[k for k in range(5) if SPL_ME[i][k]] for i in range(NSRC)] == gk(u'ka_forms')
assert [len(x) for x in gk(u'ka_forms')] == gk(u'ka_form_n')
assert [[x[9], x[10]] for x in SPL_ME] == gk(u'ack')
assert [1 if min(x) > 0 else 0 for x in gk(u'ack')] == gk(u'ack_both')
assert [[x[11], x[12]] for x in SPL_ME] == gk(u'impl')
assert [[u'implementors' if x[0] and not x[1] else u'',
         u'implementers' if x[1] and not x[0] else u''] for x in gk(u'impl')] == gk(u'impl_own')
OWN = [[KAPAT[k] for k in range(len(KAPAT))
        if SPL_ME[i][k] and sum(1 for j in range(NSRC) if SPL_ME[j][k]) == 1] for i in range(NSRC)]
assert OWN == gk(u'spell_own') == [[u'implementors'], [], [u'inactive'], [], [u'idle timeout']]
NUMW = [u'two hours', u'one hour', u'ten minutes', u'some long amount of time', u'three times',
        u'120 minutes', u'2 hours', u'120 seconds']
NUMW_ME = [[occ(LOW_SH[i], w.lower()) for w in NUMW] for i in range(NSRC)]
assert NUMW_ME == gk(u'numw')
assert [x[0] + x[1] for x in NUMW_ME] == gk(u'num_word_two')
assert [x[5] + x[6] for x in NUMW_ME] == gk(u'num_digit_two') == gk(u'digit_form_two_hours') == [0] * NSRC
THREE = NUMW_ME[4][4]
assert THREE == gk(u'numw')[4][4] == 11 and [NUMW_ME[i][4] for i in OLDI] == [0]
assert gk(u'years') == YR and max(YR) - min(YR) == 33
assert min(gk(u'numval_n')) == gk(u'numval_n')[2] and len(gk(u'num_cold')) == 1
NREQ = [r for r in ROLEN if u'no requirements' in r]
assert len(NREQ) == 1
NREQK = ROLEN.index(NREQ[0])
assert [i for i in range(NSRC) if R_SH[i][NREQK] > 0] == [2]
NDEFAULT = [r for r in ROLEN if r.startswith(u'they MUST default')]
assert len(NDEFAULT) == 1
NDEFK = ROLEN.index(NDEFAULT[0])
assert [i for i in range(NSRC) if R_LINE[i][NDEFK] > 0] == [0]
assert [i for i in range(NSRC) if R_SH[i][NDEFK] > 0] == [0, 1]
KA0 = [x[0] for x in SPL_ME]
IDLE0 = [x[5] for x in SPL_ME]
IDLEC = [x[6] for x in SPL_ME]
NW2 = [x[0] + x[1] for x in NUMW_ME]
ND2 = [x[5] + x[6] for x in NUMW_ME]
assert KA0 == gk(u'ka_hyphen') and IDLE0 == gk(u'idle_term') and IDLEC == gk(u'idle_compound')
assert NW2 == gk(u'num_word_two') and ND2 == gk(u'num_digit_two')

# ---------- ⑤ 跨行义务词行对: 本遍按 token 列的末词/首词判 ----------
def straddle_mine(i, w):
    tk = [fold0(x).lower().split(u' ') for x in L[i]]
    parts = pn(w).split(u' ')
    out = []
    for m in range(len(tk)):
        if not tk[m] or tk[m][-1] != parts[0]:
            continue
        k, bl = m + 1, 0
        while k < len(tk) and not tk[k]:
            bl += 1
            k += 1
        if k < len(tk) and tk[k][:len(parts) - 1] == parts[1:]:
            out.append((m + 1, k + 1, bl))
    return out


TSK = [k for k in range(5) if sum([TSH[i][k] - TLINE[i][k] for i in range(NSRC)])]
assert TSK == [1], TSK
SP_ROWS = [(LBL[i], k, mh, mt, bl) for k in TSK for i in range(NSRC)
           for (mh, mt, bl) in straddle_mine(i, TONE[k])]
SP_N = len(SP_ROWS)
SP_PER = [len([x for x in SP_ROWS if x[0] == t]) for t in LBL]
SP_ND = [TONE[k] for k in TSK]
SP_ADJ = len([x for x in SP_ROWS if x[3] - x[2] == 1])
SP_BLANK = SP_N - SP_ADJ
SP_BLROWS = sum(x[4] for x in SP_ROWS)
SP_GSHELL = sum(len([1 for n in range(x[2], x[3] - 1)
                     if fold0(L[LBL.index(x[0])][n - 1]) != u'']) for x in SP_ROWS)
# 跨行账: 每一式在摘壳面比逐行面多读到的枚数, 应当正好等于本遍现找的行对数
MNG = [TSH[i][TSK[0]] - TLINE[i][TSK[0]] for i in range(NSRC)]
assert SP_N == gk(u'tone_straddle_n') == 7
assert SP_PER == MNG == gk(u'tone_straddle') == gk(u'tone_wrap_gain_mn')
assert sum(MNG) - SP_N == gk(u'tone_straddle_ledger') == 0
assert SP_ND == gk(u'tone_straddle_nd') == [u'MUST NOT']
assert len([x for x in SP_ROWS if x[1] == TSK[0]]) == gk(u'tone_straddle_by_kind')[0]
assert SP_ADJ == gk(u'tone_straddle_adj') == SP_N
assert SP_BLANK == gk(u'tone_straddle_blank') == SP_BLROWS == gk(u'tone_straddle_blank_rows') == 0
assert SP_GSHELL == gk(u'tone_straddle_gap_shell') == 0
assert [(x[0], x[2], x[3]) for x in SP_ROWS] == [(y[0], y[2], y[3]) for y in CH[u'straddle']]

# ---------- ⑥ 切开两半: 本遍建 token→原行字符跨度尺 ----------
def spans(i):
    """(面内 token 序号, 原行号(1 基), 该行内 token 的原始起迄, 该行 token 数)"""
    out, li = [], 0
    for n, x in enumerate(L[i]):
        if SH[i][n]:
            continue
        ms = list(re.finditer(u'\\S+', x))
        for j, m in enumerate(ms):
            out.append((li + j, n + 1, m.start(), m.end(), len(ms), j))
        li += len(ms)
    return out, li


TOK = [spans(i) for i in range(NSRC)]


def cut_to_raw(row, frm, folded_len):
    """从 frm 起数出 folded_len 个非空格字符, 截到该字符之后(建条目侧用逐行折平→原行索引表反查)"""
    k, n = frm, 0
    while n < folded_len:
        if not row[k].isspace():
            n += 1
        k += 1
    return row[frm:k]


def half_pieces(i, nd):
    key = pn(nd)
    face = LOW_SH[i]
    a = face.find(key)
    assert a >= 0, (LBL[i], nd)
    e = a + len(key) - 1
    arr, _n = TOK[i]
    # 面内 token 序号 ⇎ 该 token 折叠起点 → 按面的空格分词累计宽度反查(面就是 token 以单空格串成)
    tk = face.split(u' ')
    acc = 0
    hs = te = hso = teo = None
    for x, w in enumerate(tk):
        if acc <= a < acc + len(w):
            hs, hso = x, acc
        if acc <= e < acc + len(w):
            te, teo = x, acc
        acc += len(w) + 1
    assert hs is not None and te is not None, (LBL[i], nd)
    info = dict((t[0], t) for t in arr)
    hl, tl = info[hs][1], info[te][1]
    hrow = L[i][hl - 1]
    trow = L[i][tl - 1]
    lasttok = [m for m in re.finditer(u'\\S+', hrow)][-1]
    firsttok = re.match(u'\\s*(\\S+)', trow)
    head = hrow[info[hs][2]:lasttok.end()]
    pre = len([c for c in trow[:info[te][2]] if not c.isspace()])
    nl = pre + (e - teo) + 1
    tail = cut_to_raw(trow, firsttok.start(1), nl)
    assert head in hrow and tail in trow, (LBL[i], nd)
    assert len([c for c in tail if not c.isspace()]) == nl, (LBL[i], nd)
    assert tail.lower().endswith(tk[te][:e - teo + 1]), (LBL[i], nd)
    return hl, tl, head, tail


WRAPREC = [(i, k) for i in range(NSRC) for k in WRAPK[i]]
assert len(WRAPREC) == 15 == gk(u'split_n')
PIECES = [half_pieces(i, ROLEN[k]) for (i, k) in WRAPREC]
assert [x[0] for x in PIECES] == gk(u'split_head'), ([x[0] for x in PIECES], gk(u'split_head'))
assert [x[1] for x in PIECES] == gk(u'split_tail')
assert [len(x[2]) for x in PIECES] == gk(u'split_head_chars')
assert [len(x[3]) for x in PIECES] == gk(u'split_tail_chars')
ROWTOT = sum(len(x[2]) + len(x[3]) for x in PIECES)
SPANTOT = sum(x[1] - x[0] + 1 for x in PIECES)
assert ROWTOT == gk(u'split_rows_tot') == 555
assert SPANTOT == gk(u'split_span_tot') == 30
SHELLCUT = sum(len(x) for x in SHELLK)
assert [x[1] - x[0] + 1 for x in PIECES] == gk(u'split_span') == [2] * 15 == [2 + y for y in gk(u'split_gap_rows')]
assert SHELLCUT == 0 and gk(u'split_wrap_n') == len(WRAPREC) == gk(u'split_n')
assert gk(u'split_tagcut_n') == len(TAGCUTK) == gk(u'tagcut_n') == 1
SPLITN = len(WRAPREC) + SHELLCUT
FULL_HEAD = sum(1 for (i, k), (hl, tl, hd, tl2) in zip(WRAPREC, PIECES)
                if pn(ROLEN[k]) in pn(L[i][hl - 1]))
assert FULL_HEAD == gk(u'split_full_on_head') == 0
HALF_OK = sum(1 for (i, k), (hl, tl, hd, tlp) in zip(WRAPREC, PIECES)
              if pn(hd) in pn(L[i][hl - 1]) and pn(tlp) in pn(L[i][tl - 1]))
assert HALF_OK == gk(u'split_half_ok') == 15

# ---------- ⑦ 反向对照: 排除份全冷 ⇎ 两把词尺的差 ----------
NEG = [tuple(x) for x in CH[u'neg']]
assert len(NEG) == gk(u'neg_n') == 15
NFAC = {u'sh': LOW_SH, u'fold': LOW}
assert sorted(set([x[2] for x in NEG])) == [u'fold', u'sh']
NW = [[ub0(NFAC[nd_f[2]][i], pn(nd_f[0])) for nd_f in NEG] for i in range(NSRC)]
NS = [[occ(NFAC[nd_f[2]][i], pn(nd_f[0])) for nd_f in NEG] for i in range(NSRC)]
assert NW == gk(u'neg_word') and NS == gk(u'neg_sub')
NB0 = sum(len(x[1]) for x in NEG)
ZERO = sum([NW[i][k] for k, (nd, ex, f) in enumerate(NEG) for i in ex])
OWNP = len([1 for k, (nd, ex, f) in enumerate(NEG)
            if sum([NW[i][k] for i in range(NSRC) if i not in ex]) > 0])
COLD = [NEG[k][0] for k, (nd, ex, f) in enumerate(NEG)
        if sum([NW[i][k] for i in range(NSRC) if i not in ex]) == 0]
ROWSF = [[LBL[i], NEG[k][0], NS[i][k], NW[i][k]] for i in range(NSRC) for k in range(len(NEG))
         if NS[i][k] > NW[i][k]]
SUBRULER = sum([x[2] for x in ROWSF])
SUBFALSE = sum([x[2] - x[3] for x in ROWSF])
NEGK = dict((nd, ex) for (nd, ex, f) in NEG)
assert len(NEGK) == len(NEG)
COLDHIT = [x for x in ROWSF if LBL.index(x[0]) in NEGK[x[1]]]
OWNHIT = [x for x in ROWSF if LBL.index(x[0]) not in NEGK[x[1]]]
CSUB = sum([x[2] for x in COLDHIT])
OSUB = sum([x[2] - x[3] for x in OWNHIT])
assert len(COLDHIT) == 6 and len(OWNHIT) == 7 and CSUB == 15 and OSUB == 162
assert CSUB + OSUB == SUBFALSE and all(x[3] == 0 for x in COLDHIT)
assert NB0 == gk(u'neg_probes') == 43 and ZERO == gk(u'neg_zero_hits') == 0
assert OWNP == gk(u'neg_owner_present') == len(NEG) and COLD == gk(u'neg_cold_probes') == []
assert ROWSF == gk(u'neg_sub_false_rows') and len(ROWSF) == 13
assert SUBRULER == gk(u'neg_sub_ruler') == 597 and SUBFALSE == gk(u'neg_sub_false') == 177
assert SUBFALSE < SUBRULER and SUBRULER - SUBFALSE == sum([x[3] for x in ROWSF])
assert gk(u'neg_fold_n') == len([x for x in NEG if x[2] != u'sh']) == 1
assert gk(u'neg_faces') == [x[2] for x in NEG]

# ---------- ⑧ 锚: 按 ⟦ 分段手吃 ⟨…⟩, 止于解读注 ----------
TT = io.open(ENTRY, encoding=u'utf-8').read()
_m = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', TT, re.S)
ENC = _m.group(1)
FLATENC = ENC.replace(u'\n', u'')
assert len(FLATENC) == gk(u'enc_chars')
cites, parts = [], TT[TT.index(u'⟪BabelTele⟫'):TT.index(u'## ⛓解读注')].split(u'⟦')
for seg in parts[1:]:
    if u'⟧' not in seg:
        continue
    y = seg.index(u'⟧')
    lab = seg[:y]
    if lab not in LBL or seg[y + 1:y + 2] != u'⟨':
        continue
    a = y + 2
    z = seg.index(u'⟩', a)
    cites.append((lab, seg[a:z]))
    assert FLATENC.find(seg[a:z]) >= 0, seg[a:z][:40]
assert len(cites) == gk(u'anchor_total'), (len(cites), gk(u'anchor_total'))
DIS = set([x[1] for x in cites])
assert len(DIS) == gk(u'anchor_distinct')
PER = dict((t, len([x for x in cites if x[0] == t])) for t in LBL)
assert PER == dict((t, gk(u'tag_' + t)) for t in LBL)
P5 = [pn(t) for t in TS]
IN5 = [len([q for l, q in cites if l == LBL[i] and pn(q) in P5[i]]) for i in range(NSRC)]
assert IN5 == [PER[t] for t in LBL], (IN5, [PER[t] for t in LBL])
FACEHIT = dict((q, [i for i in range(NSRC) if pn(q) in P5[i]]) for q in DIS)
REFHIT = dict((q, set(l for l, q2 in cites if q2 == q)) for q in DIS)
CLS1 = len([q for q in DIS if len(FACEHIT[q]) == 1])
CLSN = len([q for q in DIS if 1 < len(FACEHIT[q]) < NSRC])
CLS5 = len([q for q in DIS if len(FACEHIT[q]) == NSRC])
assert (CLS1, CLSN, CLS5) == (gk(u'anchor_single'), gk(u'anchor_cross'), gk(u'anchor_all5'))
REF1 = len([q for q in DIS if len(REFHIT[q]) == 1])
REFN = len([q for q in DIS if 1 < len(REFHIT[q]) < NSRC])
CROSS_UNREF = len([q for q in DIS if len(FACEHIT[q]) > 1 and len(REFHIT[q]) == 1])
assert REF1 + REFN == len(DIS) and REF1 - CLS1 == CROSS_UNREF
assert REFN + CROSS_UNREF == CLSN + CLS5, (REFN, CROSS_UNREF, CLSN, CLS5)
MULTI = sorted([q for q in DIS if len(REFHIT[q]) > 1])
assert len(MULTI) == REFN
MULTIMAX = max([len(REFHIT[q]) for q in MULTI])
assert all(sorted(REFHIT[q]) == sorted(LBL[i] for i in FACEHIT[q]) for q in MULTI)
assert MULTIMAX == min([len(REFHIT[q]) for q in MULTI]) == NSRC - 1
AMB_LINE = len([1 for lab, q in cites if len([x for x in L[LBL.index(lab)] if pn(q) in pn(x)]) > 1])
ALL5 = sorted([q for q in DIS if len(FACEHIT[q]) == NSRC])
WORD5 = [q for q in ALL5 if u' ' not in q]
W5MAX = max([len(q) for q in ALL5])
assert len(WORD5) == len(ALL5) == CLS5 and WORD5 == ALL5 and W5MAX == 8
CHECKS = len(DIS) * NSRC
ERRN = sum(PER[t] - IN5[i] for i, t in enumerate(LBL))
assert CHECKS == gk(u'checks') == 385 and ERRN == gk(u'anchor_err') == 0

# ---------- ⑨ 行文点名的英文片段一律回那一源的归一面核验 ----------
FRAG = {u'1122': [u'they MUST default to off', u'no less than two hours', u'SEG.SEQ = SND.NXT-1'],
        u'9293': [u'is said to be "idle"', u'configurable (MUST-27) and MUST default', u'(MUST-27)'],
        u'9112': [u'no requirements on the length (or existence) of this timeout',
                  u'Servers will usually have some timeout value'],
        u'9113': [u'permitted to terminate idle connections', u'SHOULD first send a GOAWAY'],
        u'9000': [u'the minimum of the two advertised values', u'at least three times the current Probe Timeout',
                  u'max_idle_timeout']}
# 只有摘掉义务词编号才读通的片段: 原面必须没有, 去编号面必须有, 且它确是第四档救回的那枚针
FRAG_TAG = {u'9293': [u'configurable and MUST default']}
FHITS = dict((f, [i for i in range(NSRC) if pn(f) in P5[i]]) for frs in FRAG.values() for f in frs)
for lab, frs in FRAG.items():
    for f in frs:
        assert LBL.index(lab) in FHITS[f], (lab, f, FHITS[f])
FHTAG = []
for lab, frs in FRAG_TAG.items():
    i = LBL.index(lab)
    for f in frs:
        assert pn(f) not in P5[i] and pn(f) in LOW_TAG[i], (lab, f)
        k = ROLEN.index(f)
        assert (i, k) in TAGCUTK, (lab, f, k)
        FHTAG.append((lab, f, R_SH[i][k], R_TAG[i][k]))
assert FHTAG == [(u'9293', u'configurable and MUST default', 0, 1)]
CLAIM_OWN = {u'at least three times the current Probe Timeout': u'9000', u'max_idle_timeout': u'9000',
             u'no requirements on the length (or existence) of this timeout': u'9112',
             u'permitted to terminate idle connections': u'9113', u'is said to be "idle"': u'9293'}
for f, lab in CLAIM_OWN.items():
    assert FHITS[f] == [LBL.index(lab)], (f, lab, FHITS[f])
ANS0 = list(gk(u'ans'))
assert [len(x) for x in ANS0] == gk(u'ans_chars')
assert all(pn(x) in P5[i] and pn(x) in LOW_SH[i] for i, x in enumerate(ANS0))
ANSTAG = [len(TAGRE.findall(x)) for x in ANS0]
assert ANSTAG == gk(u'ans_tag_n_in_sent')
ANSLEN = len(ANS0[1]) - len(ANS0[0])
assert ANSLEN == gk(u'ans_tag_len') == gk(u'ans_tagdiff')
ANS = [x.strip() for x in ANS0]
assert [len(x) for x in ANS] == [len(x) - 1 for x in ANS0]

# ---------- ⑩ 套版长行池: 无参 split 折叠 ----------
def pool_of(i, lim):
    return set(fold0(x) for x in NONSHELL[i] if len(fold0(x)) >= lim)


POOL = [pool_of(i, 40) for i in range(NSRC)]
POOL25 = [pool_of(i, 25) for i in range(NSRC)]
assert [len(x) for x in POOL] == gk(u'pool_n') and [len(x) for x in POOL25] == gk(u'pool_n25')
UNION = set().union(*POOL)
assert len(UNION) == gk(u'pool_union') == 14625
assert len(set().union(*POOL25)) == gk(u'pool_union25') and gk(u'pool_widen') == 2120
PRES = dict((k, len([1 for x in POOL if k in x])) for k in UNION)
TIER = [len([k for k in UNION if PRES[k] == m]) for m in range(1, NSRC + 1)]
assert TIER == gk(u'pool_tier') and sum(TIER) == len(UNION)
PAIRS = [(a, b) for a in range(NSRC) for b in range(a + 1, NSRC)]
TRIPS = [(a, b, c) for a in range(NSRC) for b in range(a + 1, NSRC) for c in range(b + 1, NSRC)]
QUADS = [(a, b, c, d) for a in range(NSRC) for b in range(a + 1, NSRC)
         for c in range(b + 1, NSRC) for d in range(c + 1, NSRC)]
PP2 = dict((u'%s-%s' % (LBL[a], LBL[b]), len(POOL[a] & POOL[b])) for a, b in PAIRS)
assert PP2 == dict(gk(u'pool_pair'))
assert sum(PP2.values()) == gk(u'pool_pair_tot') == 204
PSUM = sum(len(x) for x in POOL)
P2 = sum(len(POOL[a] & POOL[b]) for a, b in PAIRS)
P3 = sum(len(POOL[a] & POOL[b] & POOL[c]) for a, b, c in TRIPS)
P4 = sum(len(POOL[a] & POOL[b] & POOL[c] & POOL[d]) for a, b, c, d in QUADS)
ALLP = len(set.intersection(*POOL))
assert (P2, P3, P4) == (gk(u'pool_pair_tot'), gk(u'pool_trip_tot'), gk(u'pool_quad_tot')) == (204, 81, 18)
assert ALLP == len([k for k in UNION if PRES[k] == NSRC]) == gk(u'pool_all_five') == 0
RAWR = [len([x for x in NONSHELL[i] if len(fold0(x)) >= 40]) for i in range(NSRC)]
assert RAWR == gk(u'pool_raw_rows') and PSUM == gk(u'pool_sum')
assert sum(RAWR) - PSUM == gk(u'pool_dup')
assert sum(TIER[m] * (m + 1) for m in range(NSRC)) - PSUM == gk(u'pool_sum_close') == 0
IE = PSUM - P2 + P3 - P4 + ALLP - len(UNION)
assert IE == 0 == gk(u'pool_ie_close')
assert ALLP == 0 and TIER[3] == gk(u'pool_new_four') == 18 and max(PP2.values()) == gk(u'pool_max_pair')
assert PP2[u'1122-9293'] == gk(u'pool_old_shared') == 8
assert [PP2[u'1122-%s' % t] for t in LBL[1:]] == [8, 0, 0, 0]
assert gk(u'old_pool_three_cold') == 1

# ---------- 门槛侧: 门数 ⇎ 恒等式数 ⇎ 算式数由本遍 ast 现数 ----------
EM = io.open(u'corpus/_mk82emit.py', encoding=u'utf-8').read()
G1 = len(re.findall(u"^CLOSE\\[u'", MS, re.M)) + len(re.findall(u"^CLOSE\\[u'", EM, re.M))
G2 = len(re.findall(u"^CLOSE2\\[u'", MS, re.M)) + len(re.findall(u"^CLOSE2\\[u'", EM, re.M))
assert (G1, G2) == (gk(u'bool_clos_n'), gk(u'bool_clos2_n')) == (36, 20)
assert gk(u'bool_all_n') == G1 + G2 == gk(u'bool_all_sum')
assert gk(u'bool_clos_sum') == G1 and gk(u'bool_clos2_sum') == G2
VFORM = len(CH[u'zid'])
assert gk(u'zid_scan_n') + gk(u'zid_scan2_n') == VFORM == 82
JD = json.dumps(DER, ensure_ascii=False)
assert len(DER) == CH[u'deriv_keys'] and DER
assert all(u'B82V(' in v for v in DER.values())
DEK = sorted(set(re.findall(u"B82V\\('([^']+)'", JD)))
assert all(k in FP for k in DEK), [k for k in DEK if k not in FP][:6]
V82 = lambda k, i=None: (FP[k] if i is None else FP[k][i])


def detup(v):
    """JSON 往返把采集侧的 tuple 打印成 list: 全为字符串的层还原成括号形, 其余不动"""
    if isinstance(v, list):
        o = [detup(y) for y in v]
        return tuple(o) if o and all(isinstance(y, str) for y in o) else o
    return v


DERBAD, DERJSON = [], 0
for kf, ex in DER.items():
    v = eval(ex, {u'B82V': V82}, {})
    if str(v) == kf:
        continue
    if str(detup(v)) == kf:
        DERJSON += 1
        continue
    DERBAD.append((kf, ex))
assert not DERBAD, DERBAD[:3]
assert JD.count(u'B82V(') == sum(v.count(u'B82V(') for v in DER.values())
DERV = JD.count(u'B82V(')
NOTE_ROWS = len([l for l in TT[TT.index(u'## ⛓解读注'):].split(u'\n')
                 if l.startswith(u'| ') and l.count(u'|') == 5]) - 1
assert NOTE_ROWS == 15
assert gk(u'contract_n') == len(FP) == 520
assert gk(u'pick_diff') == 0 and gk(u'pick_agree') == gk(u'pick_same_n') == 63
assert len(gk(u'pick_diff_keys')) == 0
# 本遍再与采集侧(_b82meas.json)对账一次: 同定义换尺, 键名由本遍现取
HEX = [len(re.findall(u'(?<![0-9A-Za-z])0x[0-9A-Fa-f]{2}(?![0-9A-Za-z])', t)) for t in TS]
SECREF = [len(re.findall(u'Section [0-9]', t)) for t in TS]
assert HEX == gk(u'hexes') and SECREF == gk(u'sec_refs')
# 引用写法的三把尺: 谓词一律照抄采集侧的形状, 方括号式那枚的谓词含 “RFC” 字样本身
CIT4 = [len(re.findall(u'RFC [0-9]{4}', t)) for t in TS]
CITH = [len(re.findall(u'RFC-[0-9]{4}', t)) for t in TS]
CITB = [len(re.findall(u'\\[RFC[0-9]{4}\\]', t)) for t in TS]
assert CIT4 == gk(u'cit_rfc') and CITH == gk(u'cit_rfc_hyphen') and CITB == gk(u'cit_brk')
assert CITH[0] == 24 and CITH[1:] == [0, 0, 0, 0] and CITB[0] == CITB[1] == 0
COWN = gk(u'cite_own')
assert len(gk(u'cite_matrix')[0]) == 10 and COWN[0] == 0 and sum(COWN) == 18
PK = json.load(io.open(u'corpus/_b82meas.json', encoding=u'utf-8'))
MY = {u'bytes': BS, u'blank': BLK, u'maxlen': ML, u'ff': FFC, u'nonascii': NA, u'spell': SPL_ME,
      u'pgnum': PGN, u'hexes': HEX, u'sec_refs': SECREF, u'shell_lines': SL, u'foot': FOOT,
      u'bom': BOM, u'tag_raw': TRAW, u'tone_line': TLINE, u'tone_fold': TFOLD, u'lf': LF, u'cr': CR,
      u'splitlines': SPL, u'splitnl': SPLNL, u'ff_alone': EFA, u'ff_led': FFL,
      u'ff_before_nl': FFBN, u'ff_at_eof': FFE, u'trailing_nl': TNL, u'hdr_old': HDR}
PKK = {u'tag_raw': u'tag_dash', u'tone_line': u'ob_line', u'tone_fold': u'ob_fold',
       u'lf': u'n_lf', u'cr': u'n_cr'}
PAGREE = [k for k in sorted(MY) if k not in PKK and MY[k] == PK[k]]
PAGREE += [k for k in sorted(PKK) if MY[k] == PK[PKK[k]]]
assert len(PAGREE) == len(MY), sorted(set(MY) - set(PAGREE))
# 判词针两档对拍: 采集侧两串清单的下标是它自己清单的位置, 与本遍 ROLEN 不同轴, 只能按串对齐
PS = io.open(u'corpus/_pick82.py', encoding=u'utf-8').read()
N2 = None
for nd in ast.parse(PS).body:
    if isinstance(nd, ast.Assign) and getattr(nd.targets[0], u'id', u'') == u'NEEDLES2':
        N2 = ast.literal_eval(nd.value)
assert N2 is not None
assert (len(PKND), len(N2)) == (len(PK[u'needles3']), len(PK[u'needles3b'])) == (30, 20)


def pk_col(needles, rows, col, mat):
    """按串对齐后逐枚比某一档: 返回(相符枚名, 不符枚名, 本遍针集没有的枚名)"""
    ok, bad, off = [], [], []
    for k, nd in enumerate(needles):
        if nd not in ROLEN:
            off.append(nd)
            continue
        j = ROLEN.index(nd)
        (ok if [x[col] for x in rows[k]] == [mat[i][j] for i in range(NSRC)] else bad).append(nd)
    return ok, bad, off


P3L, P3LB, OFFA = pk_col(PKND, PK[u'needles3'], 0, R_LINE)
P3F, P3FB, _ = pk_col(PKND, PK[u'needles3'], 1, R_FOLD)
PBL, PBLB, OFFB = pk_col(N2, PK[u'needles3b'], 0, R_LINE)
PBF, PBF2, _ = pk_col(N2, PK[u'needles3b'], 1, R_FOLD)
assert P3LB == P3FB == PBLB == PBF2 == []
PKCHK = len(P3L) + len(P3F) + len(PBL) + len(PBF)
assert PKCHK == 2 * (len(PKND) - len(OFFA)) + 2 * (len(N2) - len(OFFB))
print(u'判词针按串对拍: 30 枚清单本遍针集外 %d 枚 ⇎ 20 枚清单外 %d 枚, 相符档目 %d'
      % (len(OFFA), len(OFFB), PKCHK))
print(u'  缺席(30): ' + u' ⇎ '.join(OFFA))
print(u'  缺席(20): ' + u' ⇎ '.join(OFFB))

# ---------- 摘要重建: README 里那一行命令必须在副本上复现在库文件 ----------
GROW, ALLR = [], None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        GROW.append([x.strip() for x in l.split(u'|')[1:-1]])
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR
ROWS = dict((c[0], c) for c in GROW)
SL82 = ROWS[u'B82']
E82, D82 = num(SL82[2]), num(SL82[1])
assert E82 == gk(u'enc_chars') == 15773
assert SL82[3] == u'%.1f%%' % (100.0 * E82 / D82), (SL82[3], E82, D82)
assert SL82[4] == u'%.3f%%' % (100.0 * E82 / sum(BS)), SL82[4]
assert len(set(FLATENC)) == num(SL82[5]) == 538
DGH = u'corpus/_tmp82dgh.md'
io.open(DGH, u'w', encoding=u'utf-8', newline=NL).write(TT)
_dg = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/_mkdigest3.py', u'B82', DGH]
                     + sum([[LBL[i], SRC[i], u'300', u'200'] for i in range(NSRC)], []),
                     capture_output=True, text=True, encoding=u'utf-8')
assert _dg.returncode == 0, _dg.stderr[-400:]
_dg = _dg.stdout
NEW_TT = io.open(DGH, encoding=u'utf-8').read()
assert NEW_TT[:NEW_TT.index(u'## ⛓解读注')] == TT[:TT.index(u'## ⛓解读注')], u'副本重建与在库文件不同形'
assert u'digest_total=%d' % D82 in _dg, _dg
assert u'atoms=%d union_hit=%d' % (gk(u'anchor_total'), gk(u'anchor_total')) in _dg, _dg
DGANCH = [(m.group(1), int(m.group(2))) for m in
          re.finditer(u'^([^:]+): anchors=(\\d+)/\\d+ blocks=', _dg, re.M)]
DGF = [len([q for l, q in cites if pn(q) in P5[i]]) for i in range(NSRC)]
assert [x[0] for x in DGANCH] == LBL
assert [x[1] for x in DGANCH] == DGF, (DGANCH, DGF)
XW = [len([q for l, q in cites if l != LBL[i] and pn(q) in P5[i]]) for i in range(NSRC)]
assert [DGF[i] - PER[t] for i, t in enumerate(LBL)] == XW
assert DGF == [43, 51, 25, 27, 39] and sum(DGF) == 185 and sum(PER.values()) == gk(u'anchor_total')
assert all(DGF[i] > PER[t] for i, t in enumerate(LBL))
assert _dg.count(u'/%d blocks=' % gk(u'anchor_total')) == NSRC and u'MISS(no raw hit)' not in _dg, _dg
os.remove(DGH)

# ---------- 转化指标: 逐条现数, 列内并集 ----------
LINES_S = S.split(NL)
hh = [i for i, l in enumerate(LINES_S) if l.startswith(u'| entry | 编码字符 |')]
assert len(hh) == 1
tt0 = [i for i in range(hh[0], len(LINES_S)) if LINES_S[i].startswith(u'| **合计（')]
assert len(tt0) == 1
LISTED0 = [l.split(u'|')[1].strip() for l in LINES_S[hh[0] + 2:tt0[0]]]
assert all(x.startswith(u'B') for x in LISTED0)
assert u'B82' not in LISTED0 and S.count(u'| B82 |') == 0 and S.count(u'**B82 问的是') == 0
LISTED = sorted(LISTED0 + [u'B82'], key=lambda k: int(k[1:]))
UNACC = [c for c in GROW if c[0] not in LISTED]
ENCS, EN, DG = [], [], []
for t in LISTED:
    f = glob.glob(u'corpus/babeltele/%s_*.md' % t)
    assert len(f) == 1, t
    tt = io.open(f[0], encoding=u'utf-8').read()
    mm = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', tt, re.S)
    e = mm.group(1).replace(u'\n', u'')
    assert len(e) == num(ROWS[t][2]), (t, len(e), ROWS[t][2])
    assert len(set(e)) == num(ROWS[t][5]), t
    ENCS.append(set(e))
    EN.append(len(e))
    DG.append(num(ROWS[t][1]))
UNI = set().union(*ENCS)
enc_all, dig_all = sum(EN), sum(DG)
assert enc_all + sum(num(c[2]) for c in UNACC) == num(ALLR[2])
assert dig_all + sum(num(c[1]) for c in UNACC) == num(ALLR[1])
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])

FIDS = sorted(set(int(re.match(r'B(\d+)_', os.path.basename(x)).group(1))
                  for x in glob.glob(u'corpus/babeltele/B*.md') if re.match(r'B\d+_', os.path.basename(x))))
assert [u'B%02d' % x for x in FIDS] == [c[0] for c in GROW], (len(FIDS), len(GROW))
FAILD = dict((u'B' + m.group(1), len([x for x in m.group(2).split(u',') if x.strip()]))
             for m in re.finditer(u'^  B(\\d+): 编码侧=\\[(.*?)\\]', AUD, re.M))
assert (not GATE_PASS) == bool(FAILD) and u'B82' not in FAILD, (GATE_PASS, FAILD)

# ---------- 编号切开针: 本遍按面重导一遍 ⇎ 再与建条目侧的窗口对拍 ----------
TG = CH[u'tagcut'][0]
assert TG[0] == LBL[TAGCUTK[0][0]] == u'9293' and TG[1] == ROLEN[TAGCUTK[0][1]]
assert TG[2] == TG[3] == gk(u'tagcut_head_row')[0] == gk(u'tagcut_tail_row')[0]
assert len(TG[4][0]) == gk(u'tagcut_tag_chars')[0] == gk(u'tagcut_eaten')[0] == 10
assert len(TG[5]) + len(TG[6]) == gk(u'tagcut_mid_chars')[0] == 70
assert pn(TG[1]) not in LOW_SH[1] and pn(TG[1]) in LOW_TAG[1]
assert pn(TG[5]) in LOW_SH[1] and pn(TG[6]) in LOW_SH[1]
TGN = len(TG[5]), len(TG[6])

# ---------- 判词段 ⇎ 门槛表行 ⇎ 语料表行 ----------
FAMC = [(u'节窗', FP, u'sec_lines'), (u'关键词模板段', FP, u'kw_head_min'),
        (u'9293 相对 1122 的对齐账（含段内标注枚数）', FP, u'ovl_s1'), (u'带单位数值的宽严两尺', FP, u'num_ruler_gap'),
        (u'“RFC nnnn”式引用处数', FP, u'cit_rfc'), (u'建条目侧按针数出的行号歧义档', CH, u'anchor_ambiguous'),
        (u'抬头年（本遍另存逐份转写并与契约对拍）', FP, u'years'), (u'BOM 剥壳后存活枚数', FP, u'bom_survives')]
assert all(k in d for _, d, k in FAMC), [k for _, d, k in FAMC if k not in d]
HEADROW = (u'| B82 | ' + fmt(E82) + u'（新建, 一条空闲连接到底多久该关掉、由谁说了算 交 TCP 两份 ⇎ HTTP 两份 ⇎ QUIC 一份'
           u'共五份 RFC Editor 纯文本面各答一遍 ' + str(len(cites)) + u' 处标注／' + str(len(DIS))
           + u' 个不同串（登记全命中, 单源 ' + str(CLS1) + u' ⇎ 穿二至四源 ' + str(CLSN)
           + u' ⇎ 五源全现 ' + str(CLS5) + u'——五源同现的 ' + str(len(ALL5)) + u' 枚全是单词形（无空格, 最长 '
           + str(W5MAX) + u' 字符: ' + u' ⇎ '.join(u'“%s”' % q for q in ALL5) + u'）, 被多个标签共引的 ' + str(len(MULTI))
           + u' 枚一律穿 ' + str(MULTIMAX) + u' 源; 编码区 ' + fmt(E82) + u' 字符, 归属检查 ' + str(CHECKS) + u' 次, 错配 '
           + str(ERRN) + u'，另 ' + str(AMB_LINE) + u' 处所引的串在本源不止一行露面（行号只取首现那一行，建条目侧的歧义档 '
           + str(CH[u'anchor_ambiguous']) + u' 枚是它按针导出时数的））: 五色锚位 ' + u' ⇎ '.join(x + u' ⟦' + x + u'⟧' for x in LBL)
           + u'（' + u' ⇎ '.join(str(PER[t]) for t in LBL) + u' 处, 本遍按 ⟦ 分段手吃 ⟨…⟩ 现数并与建条目侧逐键对拍;'
             u' 摘要遍按面另扫一遍, 同一批引用在五份面上露面 ' + u' ⇎ '.join(str(x) for x in DGF)
             + u' 次, 比归属尺多出的 ' + u' ⇎ '.join(str(x) for x in XW)
             + u' 次是他源之锚恰好也活在这份面上——面尺 ≥ 引用尺恒成立, 两把尺不共用键）;'
             u' 四档口径（原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳去编号折平）在 ' + str(len(ROLEN)) + u' 枚判词针上读到 '
           + V4(FACE) + u' 次命中, 增益 ' + V4([sum(GF), sum(GS), sum(GT)]) + u' 枚 ⇎ 单调 '
           + str(FM) + u'/3 档——折平救回 ' + str(sum(GF)) + u' 枚（逐份 ' + V4(GF) + u'）, '
           + u'摘壳档一粒不增不减（新读 ' + str(sum(GS)) + u' ⇎ 丢 ' + str(SHD) + u'：五份的页码行只剩 1122 还印 '
             u'[Page N], 新式四份的剥壳增量全落在空行上）, 去编号档多 ' + str(sum(GT)) + u' 枚：“'
           + CH[u'tagcut'][0][1] + u'” 被 9293 的 ' + CH[u'tagcut'][0][4][0] + u' 掐成两截（标注本体 '
           + str(len(TG[4][0])) + u' 字符, 两截在摘壳面上的窗口各 ' + str(TGN[0]) + u' ⇎ ' + str(TGN[1])
           + u' 字符）; 被线切开的判词 ' + str(SPLITN) + u' 枚（换行 ' + str(len(WRAPREC)) + u' ⇎ 页壳 '
           + str(SHELLCUT) + u'）两半各归一行都读得通（'
           + str(HALF_OK) + u'/' + str(len(WRAPREC)) + u'）, 整串拿到首行 ' + str(FULL_HEAD) + u' 枚读不通, '
             u'两半合计 ' + str(ROWTOT) + u' 字符 ⇎ 幅度 ' + str(SPANTOT) + u' 行; '
             u'义务词跨行 ' + str(SP_N) + u' 对（逐份 ' + V4(SP_PER)
           + u'）式样只有一种（' + SP_ND[0] + u'）⇎ 两行之间夹空行 ' + str(SP_BLANK)
           + u' ⇎ 夹壳行 ' + str(SP_GSHELL) + u' 枚; 术语换代 keep-alive '
           + V4(KA0) + u' ⇎ idle ' + V4(IDLE0) + u' ⇎ “idle timeout” 复合式 '
           + V4(IDLEC) + u' 枚只在 9000 ⇎ 编号族摘壳面 ' + V4(TSHC)
           + u' 枚只在 9293（其中带前空格的'
             u'“ (WORD-n)”括号形 %d 枚——术语尺在这批括号形里读到 %d 枚 MUST ⇎ %d 枚 MAY '
             u'共 %d 枚, 余 %d 枚是 SHLD 不属五式, 故去编号档只比摘壳档少读这 %d 枚而非括号形的全部 %d 枚）; '
             % (sum(PKIND[1]), PKIND[1][0], PKIND[1][4], sum(DROP[1]),
                PKIND[1][5] + PKIND[1][6], sum(DROP[1]), sum(PKIND[1]))
             + u'带单位数值逐份 ' + V4(gk(u'numval_n')) + u' 项（9112 全库最少 ' + str(gk(u'numval_n')[2])
           + u' 项）⇎ 宽尺比严尺多读 ' + V4(gk(u'num_ruler_gap')) + u' 枚 ⇎ 独家式 ' + str(gk(u'num_own_tot'))
           + u' 枚 ⇎ 全库只冷一式 “' + gk(u'num_cold')[0] + u'”; 节窗档 ' + u' ⇎ '.join(gk(u'sec_no')) + u' 节 '
           + V4(gk(u'sec_lines')) + u' 行 ⇎ 占比 ' + V4(gk(u'sec_span_pct')) + u'% ⇎ 节内义务词 '
           + V4(gk(u'sec_tone_tot')) + u' 枚; 套版长行池 ' + fmt(len(UNION)) + u' 枚分档 ' + V4(TIER)
           + u', 两两 ' + str(P2) + u' ⇎ 三三 ' + str(P3) + u' ⇎ 四四 '
           + str(P4) + u' ⇎ 五份共用 ' + str(ALLP) + u' ⇎ 容斥 '
           + str(IE) + u'——牵进 1122 的每一对除与 9293 共的 ' + str(PP2[u'1122-9293'])
           + u' 枚 TCP 正文行外全为零; 关键词模板段四份印（1122 无此段, 行号按 -1 登记 ' + V4(gk(u'kw_minus_row'))
           + u'）⇎ 共头 ' + str(gk(u'kw_head_min')) + u'..' + str(gk(u'kw_head_max')) + u' 词 ⇎ 整段相同 '
           + str(gk(u'kw_same_n')) + u' 对 ⇎ 逐行序列也相同 ' + str(gk(u'kw_same_raw_n')) + u' 对 ⇎ 只因换行不同 '
           + str(gk(u'kw_wrap_diff')) + u' 对; 9293 相对 1122 那一节: 句 ' + str(gk(u'ovl_s1')) + u' ⇎ '
           + str(gk(u'ovl_s2')) + u' ⇎ 逐字同 ' + str(gk(u'ovl_same_raw')) + u' ⇎ 去编号同 ' + str(gk(u'ovl_same_tag'))
           + u' ⇎ 归拼同 ' + str(gk(u'ovl_same_canon')) + u' ⇎ 新句 ' + str(gk(u'ovl_new')) + u'（其中 '
           + str(gk(u'ovl_disc_promoted')) + u' 句由散句升格）⇎ 相同词段 ' + str(gk(u'blk_tcp_equal'))
           + u' 词/3 段/最长 ' + str(gk(u'blk_tcp_equal_max')) + u' 词 ⇎ 删 ' + str(gk(u'blk_tcp_drop'))
           + u' ⇎ 插 ' + str(gk(u'blk_tcp_insert')) + u' ⇎ 替换 ' + str(gk(u'blk_tcp_replace'))
           + u' ⇎ 段长差 ' + str(gk(u'blk_tcp_len_gap')) + u' 里 ' + str(gk(u'blk_tcp_tag_chars'))
           + u' 字符是 ' + str(gk(u'tagcut_mid_n')[0]) + u' 枚编号标注; 反向对照 ' + str(len(NEG)) + u' 枚针的 '
           + str(NB0) + u' 次“排除份”探针在整词尺上全冷（' + str(ZERO) + u' 命中）⇎ 换子串尺则其中 '
           + str(len(COLDHIT)) + u' 次点着（多读 ' + str(CSUB) + u' 枚）⇎ 主家侧两尺之差另计 '
           + str(OSUB) + u' 枚（该格子串尺共读 ' + str(SUBRULER) + u' 枚）——门槛认的是整词尺, 子串尺会把反向对照判活; 版式五份同岔:'
             u' 72 列硬换行面（超 72 列 ' + V4(O72) + u' 行）⇎ 回车 ' + str(sum(CR)) + u' 枚 ⇎ 换页符 '
           + str(FFC[0]) + u' 枚只在 1122（独占整行 ' + str(EFA[0]) + u' 行）⇎ 非 ASCII ' + str(sum(NAT))
           + u' 枚全在新式四份（' + V4(NAT) + u'）⇎ BOM ' + str(sum(BOM)) + u' 枚; 闭合账 布尔门 '
           + str(G1 + G2) + u'/' + str(G1 + G2) + u' ⇎ V 形恒等式 ' + str(VFORM) + u' 条 ⇎ 对账 '
           + str(gk(u'pick_agree')) + u' 键符 ' + str(gk(u'pick_diff')) + u' 不符（本遍换尺再对一遍: '
           + str(len(MY)) + u' 枚标量 ⇎ ' + str(PKCHK) + u' 档针目全数相符, 采集侧两串清单各有 '
           + str(len(OFFA)) + u' ⇎ ' + str(len(OFFB)) + u' 枚不在本遍 ' + str(len(ROLEN))
           + u' 枚针集内, 如实记缺席而不记不符） ⇎ 锚 ' + str(len(cites))
           + u' 处去重 ' + str(len(DIS)) + u'。门槛侧 ' + str(len(DER)) + u' 枚 DERIV 算式 ⇎ 扁平契约 '
           + str(len(FP)) + u' 枚键由采集 ⇎ 建条目 ⇎ 审计三轨 ⇎ 解读注 ⇎ 本遍五套实现逐枚复测, '
           + str(len(DER)) + u' 式在本遍就地重算全数对键（算式共引 ' + str(DERV) + u' 次 ⇎ '
             + str(len(DEK)) + u' 枚不同常量, 全部在 ' + str(len(FP)) + u' 枚键内; 其中 '
             + str(DERJSON) + u' 枚是 JSON 把采集侧 tuple 打成 list 的形差, 还原括号形才对上）; '
             u'本遍现量的是行式五档 ⇎ '
             u'剥壳账 ⇎ ' + str(len(ROLEN)) + u' 枚针的四档 ⇎ 义务词与术语 ⇎ 跨行 ' + str(SP_N)
           + u' 对 ⇎ 切开 ' + str(len(WRAPREC)) + u' 枚两半 ⇎ 反向 ' + str(len(NEG)) + u' 枚 ⇎ 锚 '
           + str(len(cites)) + u' 处（归属 ' + str(CHECKS) + u' 次 ⇎ 错配 ' + str(ERRN) + u'）⇎ 长行池 ' + fmt(len(UNION)) + u' 枚; '
           + u' ⇎ '.join(x[0] for x in FAMC) + (u'共%d族取契约值（本遍在面上现量后与契约逐列对拍的: 十六进制参数 ⇎ 自家节号引'
             u' ⇎ 引用三式各五份——其中“RFC nnnn”式那一式同时是上面族账里的一族; 抬头年另存一份逐份转写同此对拍）。） |') % len(FAMC))
assert HEADROW.count(u'|') == 3 and HEADROW.count(u'`') % 2 == 0

C82 = (u'| B82 | ' + u' ⇎ '.join(
    SHW[i] + u'（' + str(YR[i]) + u' ⟦' + LBL[i] + u'⟧：' + fmt(BS[i]) + u' 字节／面内码位 ' + fmt(CH_[i])
    + u'／行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i]) + u'／最长行 ' + str(ML[i]) + u' 列（超 72 列 ' + str(O72[i])
    + u' 行）／换页符 ' + str(FFC[i]) + u' 枚（独占整行 ' + str(EFA[i]) + u' 行, 行内混排 ' + str(FFC[i] - EFA[i])
    + u' 枚, 起手于换页符 ' + str(FFL[i]) + u' 行, 剥壳行 ' + fmt(SL[i]) + u' 行＝空行 ' + fmt(BLK[i])
    + u' ＋页码行 ' + str(FOOT[i]) + u' ＋眉行 ' + str(HDR[i]) + u'）／回车 ' + str(CR[i]) + u'／非 ASCII '
    + str(NAT[i]) + u'（BOM ' + str(BOM[i]) + u' ⇎ 其余 ' + str(NAT[i] - BOM[i]) + u'）／答句 ' + ANS5[i] + u'）'
    for i in range(NSRC))
    + u' | 五份答同一个问题 ⇒ 答的是五种东西: 1122 把定值写成词——“two hours” ' + str(NW2[0])
      + u' 枚 ⇎ 带数字的两小时 ' + str(ND2[0]) + u' 枚, 且 keep-alives 一上来就 MAY 而默认关（“'
      + u'they MUST default to off' + u'” 原面逐行 ' + str(R_LINE[0][NDEFK]) + u' 行 ⇎ 其余四份 '
      + str(sum(R_LINE[i][NDEFK] for i in range(1, NSRC))) + u' 行） ⇎ 9293 把同一句照登并给义务词编号（摘壳面 ' + str(TSHC[1]) + u' 枚 (MUST-n) 形 ⇎ 答句内 '
      + str(ANSTAG[1]) + u' 枚 ⇎ 答句因此比 1122 多 ' + str(ANSLEN) + u' 字符）'
      + u' ⇎ 9112 一个值也不给: 带单位数值 ' + str(gk(u'numval_n')[2]) + u' 项为五份最少, 把“长度乃至是否存在”写成 '
      + u'“' + NREQ[0] + u'” 式陈述句' + u' ⇎ 9113 不说多久只把刀交给服务器（“' + u'permitted to terminate idle connections'
      + u'” ⇎ idle ' + str(IDLE0[3]) + u' 枚）⇎ 9000 给算法不给定值: “' + u'the minimum of the two advertised values'
      + u'” ⇎ “at least three times the current Probe Timeout” ' + str(THREE) + u' 枚 ⇎ 0 才是禁用; '
      + u'谁引谁: 引用三式的配法各不相同——“RFC nnnn” ' + V4(CIT4) + u' 处 ⇎ 连字符式 “RFC-dddd” ' + V4(CITH)
      + u' 处（只在 1122）⇎ 方括号式 “[RFCdddd]” ' + V4(CITB) + u' 处（两份 TCP 各 0） ⇎ 十个号里各家引到别家 '
      + V4(COWN) + u' 家（1122 一家也不引; 此列与引用矩阵由采集侧现扫, 本遍只取契约值） ⇎ 各份自家节号引 ' + V4(SECREF)
      + u' 处 ⇎ 十六进制参数 ' + V4(HEX) + u' 枚（两份 TCP 一种进制也不给）; 版式吃掉判词: 切开 '
      + str(SPLITN) + u' 枚全由 72 列换行所致（换行 ' + str(len(WRAPREC)) + u' ⇎ 页壳 ' + str(SHELLCUT) + u' 枚）⇎ 幅度合计 '
      + str(SPANTOT) + u' 行 ⇎ 两半 ' + str(ROWTOT) + u' 字符; 唯一把义务词写成编号的只有 9293,'
      u' 唯一“给算法不给定值”的只有 9000 |')
assert C82.count(u'|') == 4 and C82.count(u'`') % 2 == 0

PARA = (u'**B82 问的是一条空闲连接到底多久该关掉、由谁说了算，五份一手文书给出五种答法**：'
        + u' ⇎ '.join(SHW[i] + u'（' + str(YR[i]) + u' ⟦' + LBL[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
                      + u'／非空行 ' + fmt(NB[i]) + u'／最长行 ' + str(ML[i]) + u' 列／换页符 ' + str(FFC[i])
                      + u' 枚／剥壳行 ' + fmt(SL[i]) + u' 行／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NAT[i])
                      + u'／答句 ' + ANS5[i] + u'）' for i in range(NSRC))
        + u'——五份同为 RFC Editor 纯文本面且全是 72 列硬换行（超 72 列 ' + V4(O72) + u' 行）⇎ 回车 '
        + str(sum(CR)) + u' 枚 ⇎ 换页符只住在 1122（' + str(FFC[0]) + u' 枚, 独占整行 ' + str(EFA[0])
        + u' 行）⇎ 非 ASCII ' + str(sum(NAT)) + u' 枚全在新式四份（' + V4(NAT) + u' ⇎ 其中 BOM ' + str(sum(BOM))
        + u' 枚, 剥壳后仍 survives ' + str(gk(u'bom_survives')) + u' 枚）; 抬头年 ' + u' ⇎ '.join(str(y) for y in YR)
        + u', 跨 ' + str(max(YR) - min(YR)) + u' 年。'
        + u'“多久”这句话的五种印法: 1122 用词不用数——⟦1122⟧⟨' + ANS[0] + u'⟩（“two hours” '
        + str(NW2[0]) + u' 枚 ⇎ 数字形 ' + str(ND2[0]) + u' 枚 ⇎ 全份带单位数值 '
        + str(gk(u'numval_n')[0]) + u' 项, 一项也不用于保活） ⇎ 9293 同一句加两枚编号——⟦9293⟧⟨' + ANS[1]
        + u'⟩（答句内 ' + str(ANSTAG[1]) + u' 枚 ⇎ 多 ' + str(ANSLEN) + u' 字符 ⇎ 全份 '
        + str(TSHC[1]) + u' 枚编号） ⇎ 9112 一句定值也不给——⟦9112⟧⟨' + ANS[2] + u'⟩（带单位数值 '
        + str(gk(u'numval_n')[2]) + u' 项为五份最少） ⇎ 9113 不说多久只说可以关——⟦9113⟧⟨' + ANS[3]
        + u'⟩ ⇎ 9000 给算法——⟦9000⟧⟨' + ANS[4] + u'⟩（“three times” ' + str(THREE)
        + u' 枚 ⇎ “idle timeout” 复合术语 ' + str(IDLEC[4]) + u' 枚为一家所有）。'
        + u'三线同时换代: 术语 keep-alive ' + V4(KA0) + u' ⇎ idle '
        + V4(IDLE0) + u' ⇎ 编号 ' + V4(TSHC) + u'（' + str(TSHC[1]) + u' 枚只在 9293）; 套版长行池 '
        + fmt(len(UNION)) + u' 枚里牵进 1122 的每一对除与 9293 共的 ' + str(PP2[u'1122-9293']) + u' 枚外全冷, '
        + u'而新式四份共用的有 ' + str(TIER[3]) + u' 枚 ⇎ 五份共用 ' + str(ALLP) + u' 枚; '
        + u'关键词模板段四份各印一次而互不相同: 共头 ' + str(gk(u'kw_head_min')) + u'..' + str(gk(u'kw_head_max'))
        + u' 词 ⇎ 整段相同 ' + str(gk(u'kw_same_n')) + u' 对 ⇎ 逐行序列也相同只 ' + str(gk(u'kw_same_raw_n')) + u' 对。'
        + u'版式与口径: ' + str(len(ROLEN)) + u' 枚判词针只有 ' + str(FACE[0]) + u' 次命中能在单行读全, 折平救 '
        + str(sum(GF)) + u' 枚 ⇎ 摘壳 ' + str(sum(GS)) + u' 枚 ⇎ 去编号 ' + str(sum(GT)) + u' 枚; 被切开 '
        + str(SPLITN) + u' 枚里换行 ' + str(len(WRAPREC)) + u' ⇎ 页壳 ' + str(SHELLCUT)
        + u' 枚, 另有 ' + str(len(TAGCUTK)) + u' 枚被 9293 的 ' + CH[u'tagcut'][0][4][0] + u' 掐断; 义务词跨行 '
        + str(SP_N) + u' 对全为 ' + SP_ND[0] + u'（逐份 ' + V4(SP_PER)
        + u'）; 反向 ' + str(len(NEG)) + u' 枚针的 ' + str(NB0) + u' 次排除份探针在整词尺上全冷（'
        + str(ZERO) + u' 命中）⇎ 换子串尺却点着其中 ' + str(len(COLDHIT)) + u' 次（多读 ' + str(CSUB)
        + u' 枚）——“' + COLDHIT[0][1] + u'”在 ⟦' + COLDHIT[0][0] + u'⟧ 读到 '
        + str(COLDHIT[0][2]) + u' 枚而整词 0 枚; 主家侧两尺之差 ' + str(OSUB) + u' 枚另计。'
        + u'闭合账: 布尔门 ' + str(G1 + G2) + u'/' + str(G1 + G2) + u' ⇎ V 形恒等式 ' + str(VFORM)
        + u' 条 ⇎ 对账 ' + str(gk(u'pick_agree')) + u' 键 ' + str(gk(u'pick_diff')) + u' 不符 ⇎ 锚 '
        + str(len(cites)) + u' 处 ⇎ 归属 ' + str(CHECKS) + u' 次 ⇎ 错配 ' + str(ERRN)
        + u'——五种答话在本遍换了一整套量尺之后仍落回同一处。')
for _s in (PARA,):
    assert _s.count(u'|') == 0 and _s.count(u'`') % 2 == 0
assert PARA.count(u'⟦') == PARA.count(u'⟧') == 2 * NSRC + 1
assert PARA.count(u'⟨') == PARA.count(u'⟩') == NSRC
assert sorted(set(re.findall(u'⟦([^⟦⟧]*)⟧', PARA))) == sorted(LBL)
for i in range(NSRC):
    assert pn(gk(u'ans')[i]) in P5[i], (LBL[i], gk(u'ans')[i][:40])
assert sum(PER.values()) == gk(u'anchor_total') and all(PER[t2] >= 1 for t2 in LBL)

# ---------- 落盘: 定点插入, 不整体重写 ----------
def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:60])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


def after_row(s, eid, needle, text):
    hits = [l for l in s.split(NL) if l.startswith(u'| ' + eid + u' | ') and needle in l]
    assert len(hits) == 1, (eid, needle, len(hits))
    return after(s, hits[0], text)


def subn(pat, mk, s, n=1):
    ms = list(re.finditer(pat, s))
    assert len(ms) == n, (pat, len(ms))
    m = ms[0]
    return s[:m.start()] + mk(m) + s[m.end():]


S2 = after(S, u'**B81 问的是一个 AQM 该把排队延迟压到多少、依据什么', PARA + NL + NL)
S2 = after_row(S2, u'B81', u'（新建,', HEADROW + NL)
S2 = after_row(S2, u'B81', u'`raw/qdelay/rfc7567.txt`', C82 + NL)

L2 = S2.split(NL)
h2 = [i for i, l in enumerate(L2) if l.startswith(u'| entry | 编码字符 |')]
assert len(h2) == 1
t2 = [i for i in range(h2[0], len(L2)) if L2[i].startswith(u'| **合计（')]
assert len(t2) == 1
T0 = t2[0]
present = [l.split(u'|')[1].strip() for l in L2[h2[0] + 2:T0]]
assert present == LISTED0, present[:3]
L2[T0:T0] = [(u'| B82 | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
              % (fmt(E82), SL82[3], SL82[4], SL82[5], SL82[7]))]
assert [l.split(u'|')[1].strip() for l in L2[h2[0] + 2:T0 + 1]] == LISTED0 + [u'B82'], L2[T0][:40]
NUM0 = [int(x[1:]) for x in LISTED0]
INV = [(a, b) for a, b in zip(NUM0, NUM0[1:]) if b < a]
assert INV == [(26, 23)], INV          # 本表行序不严格按编号: 在库那处 B26 先于 B23 是前一遍直补留下的
assert set(LISTED0 + [u'B82']) == set(LISTED) and len(LISTED0) + 1 == len(LISTED)
assert L2[T0].startswith(u'| B82 | ') and L2[T0 + 1].startswith(u'| **合计（')
HC = len(L2[h2[0]].split(u'|'))
cells = L2[T0 + 1].split(u'|')
assert len(cells) == HC, (len(cells), HC)
UN = sorted(set(c[0] for c in UNACC), key=lambda k: int(k[1:]))
for t in UN:
    rr = [l for l in L2 if l.startswith(u'| ' + t + u' | ')]
    assert len(rr) >= 2 and any(u'`raw/' in l for l in rr) and any(u'`raw/' not in l for l in rr), (t, len(rr))
cells[1] = u' **合计（' + str(len(LISTED)) + u' 条）** '
cells[2] = u' **' + fmt(enc_all) + u'** '
cells[3] = (u' **%.1f%%**（摘要段合计 ' % (100.0 * enc_all / dig_all) + fmt(dig_all)
            + u'，本遍补记的一枚为 ' + fmt(E82) + u' 编码／' + fmt(D82)
            + u' 摘要；两列合计与本表所列 ' + str(len(LISTED)) + u' 条一致，故不取 audit 的 ALL 行'
              + u'（它多含已接线而未在本表记账的 ' + u'⇎'.join(UN) + u'：编码 '
              + fmt(num(ALLR[2]) - enc_all) + u' ⇎ 摘要 ' + fmt(num(ALLR[1]) - dig_all)
              + u'，这 %d 条各自已在门槛表⇎语料表两行记账；唯一码点那格由本遍按 audit 的编码区正则逐条现数取列内并集，'
                u'逐条与 audit 现算值对拍） ' % len(UN))
cells[5] = u' **%s** ' % fmt(len(UNI))
assert len(L2[T0].split(u'|')) == HC == len(cells), (len(L2[T0].split(u'|')), HC)
L2[T0 + 1] = u'|'.join(cells)
NOTE = [i for i, l in enumerate(L2) if l.startswith(u'（B54 起的 ') and u'机械行' in l]
assert len(NOTE) == 1, NOTE
L2[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与字符/语义单元五格, '
               u'不重写各条的口径注; 本遍再直补 B82 一枚, 合计行只列本表已记账条目, 唯一码点由本遍逐条现数取并集, '
               u'不再抄 ALL 行。）'
               % len([x for x in present + [u'B82'] if int(x[1:]) >= 54]))
S2 = NL.join(L2)


def runs(ns):
    out, a, b = [], ns[0], ns[0]
    for x in ns[1:]:
        if x == b + 1:
            b = x
        else:
            out.append((a, b))
            a = b = x
    out.append((a, b))
    return u'、'.join(u'B%02d..B%02d' % (a, b) if b > a else u'B%02d' % a for a, b in out)


S2 = subn(u'共 \\*\\*\\d+ 条\\*\\*（`babeltele/[^`]*`, 本遍补上 B\\d+ 的四处记账行[^）]*）））',
          lambda m: (u'共 **%d 条**（`babeltele/%s`, 本遍补上 B82 的四处记账行, 合计按本表所列 %d 条现算, '
                     u'唯一码点逐条现数；已接线而未进本表合计行的 %s 均已记了门槛表⇎语料表两行, '
                     u'本遍不再重记其记账数（上一遍该行按 B81 现量写就, 未含本遍一枚））'
                     % (len(FIDS), runs(FIDS), len(LISTED), u'／'.join(UN))), S2)
assert S2.count(u'，分两代。') == 1
_d0 = [l for l in S2.split(NL) if u'四处记账行' in l]
assert len(_d0) == 1 and _d0[0].count(u'（') == _d0[0].count(u'）'), _d0[0][-90:]
S2 = subn(u'## 保真门槛：`python corpus/audit.py` → \\*\\*PASS\\*\\*（\\d+ 条）',
          lambda m: (u'## 保真门槛：`python corpus/audit.py` → **PASS**（%d 条）' % len(FIDS)
                     if GATE_PASS else
                     u'## 保真门槛：`python corpus/audit.py` → 本遍复跑总判 **FAIL**：失配只落在未记账的 %s'
                     u'（audit 报其 %d 枚编码侧数字锚在原文侧读不到）；本遍记账的 B82 错配 %d 枚, 本表所列 %d 条不受影响'
                     % (u'／'.join(sorted(FAILD)), sum(FAILD.values()), ERRN, len(LISTED))), S2)
S2 = subn(u'当前 \\*\\*\\d+ 条语料／\\d+ 条\\*\\*推导全部通过（audit 自报“已机检的推导 \\d+ 条”，行集与文件数相符 \\d+ ⇎ \\d+）',
          lambda m: (u'当前 **%d 条语料／%d 条**推导%s（audit 自报“已机检的推导 %d 条”，行集与文件数相符 %d ⇎ %d）'
                     % (len(FIDS), PROOFS,
                        u'全部通过' if GATE_PASS else u'除 %s 外全部通过' % u'／'.join(sorted(FAILD)),
                        PROOFS, len(GROW), len(FIDS))), S2)

assert S2.count(u'python -X utf8 corpus/_fill81.py') == 1
L82 = [(u'python -X utf8 corpus/_mkB82.py',
        u'                     # 建条目(前半, 与 _mk82emit.py 同场 exec): 扁平契约 ' + str(len(FP))
        + u' 枚键⇎ DERIV ' + str(len(DER)) + u' 枚算式 ⇎ V 形 ' + str(VFORM) + u' 条; 四档面(原行⇎折平⇎摘壳⇎去编号)⇎'
        + str(len(ROLEN)) + u' 枚判词针 ⇎ ' + str(len(KAPAT)) + u' 式拼写⇎义务词五式⇎编号族⇎带单位数值宽严两尺⇎'
        u'节窗⇎套版长行池⇎引用⇎跨行行对九族, 采集侧同定义标量 ' + str(gk(u'pick_agree')) + u'/'
        + str(gk(u'pick_agree')) + u' 枚相符; 记账遍再以 ' + str(len(MY)) + u' 标量 ⇎ '
        + str(PKCHK) + u' 档针目换尺复对采集侧 _b82meas.json, 全数相符'),
       (u'python -X utf8 corpus/_mkdigest3.py B82 <entry> '
        + u' '.join(u'%s %s 300 200' % (LBL[i], SRC[i]) for i in range(NSRC)),
        u'   # 五源分节摘要(' + fmt(D82) + u' 字符, ' + str(len(cites))
        + u' 枚锚全命中, 五份各开一窗 300/200；本遍用同一组窗口在副本上重建, 与在库文件在 ⛓解读注之前的正文逐字符相同'),
       (u'python -X utf8 corpus/_wire82.py',
        u'                    # 接线: SRC/ATOM/SCAN(审计器侧两套实现)/DERIV/B82V 进 audit.py, 落盘前复跑 '
        + str(len(FP)) + u' 枚扁平键 ⇎ ' + str(len(DER)) + u' 枚算式 ⇎ ' + str(CHECKS) + u' 次归属检查'),
       (u'python -X utf8 corpus/_fill82.py',
        u'                    # 第五遍(注区): 行界手索引 ⇎ `bisect` 行号尺 ⇎ token 跨度尺 ⇎ ast 摘门右式各重导一次, '
        + str(G1) + u'+' + str(G2) + u' 道布尔门 ⇎ ' + str(VFORM)
        + u' 条 V 形现算归零后写回 ⛓解读注（' + str(NOTE_ROWS) + u' 行复测表 ⇎ 扁平 ' + str(len(FP))
        + u' 键全部复算 ⇎ 与采集遍对账不符 ' + str(gk(u'pick_diff')) + u'/' + str(gk(u'pick_agree'))
        + u' ⇎ 独有 ' + str(len(gk(u'pick_diff_keys'))) + u' 枚）')]
CUR = u'python -X utf8 corpus/_fill81.py'
for head, tail in L82:
    S2 = after(S2, CUR, head + tail + NL)
    CUR = head

T3 = u'corpus/README.md.tmp82'
io.open(T3, u'w', encoding=u'utf-8', newline=NL).write(S2)
os.replace(T3, u'corpus/README.md')
json.dump(dict(listed=LISTED, listed_n=len(LISTED), enc=enc_all, dig=dig_all, uniq=len(UNI),
               proofs=PROOFS, b82_enc=E82, b82_dig=D82, unaccounted=UN, audit_rows=len(GROW),
               entries_files=len(FIDS), gate_pass=GATE_PASS, gate_failed=FAILD,
               bytes=BS, chars=CH_, lines=LN, splitlines=SPL, splitnl=SPLNL, tail_nl=TNL, ff=FFC,
               ff_alone=EFA, ff_led=FFL, cr=CR, nonascii=NAT, bom=BOM, shell_lines=SL,
               shell_nonblank=PPNB, foot=FOOT, hdr=HDR, pp_rows=PPR, pgnum=PGN, pgnum_shell=PGS,
               face_tot=FACE, face_mono=FM, gain_sh_dup=SHD, role_gain_fold=GF, role_gain_sh=GS, role_gain_tag=GT,
               gain_fold=sum(GF), gain_sh=sum(GS), gain_tag=sum(GT),
               tone_sh=TSH, tone_tot=[sum(x) for x in TSH], tag_sh=TSHC, tag_paren_kind=PKIND, tag_raw=TRAW,
               ka_hyphen=KA0, idle_term=IDLE0, idle_compound=IDLEC, spell_tot=[sum(x) for x in SPL_ME],
               straddle_rows=SP_ROWS, split_head=[x[0] for x in PIECES], split_tail=[x[1] for x in PIECES],
               split_head_chars=[len(x[2]) for x in PIECES], split_tail_chars=[len(x[3]) for x in PIECES],
               split_rows_tot=ROWTOT, split_span_tot=SPANTOT,
               split_full_on_head=FULL_HEAD, split_half_ok=HALF_OK, neg_probes=NB0,
               neg_sub_ruler=SUBRULER, neg_cold_rows=len(COLDHIT), neg_cold_sub=CSUB, neg_owner_gap=OSUB, pool_n=[len(x) for x in POOL], pool_union=len(UNION),
               pool_pair=PP2, pool_pair_tot=P2, pool_trip_tot=P3,
               pool_quad_tot=P4, pool_tier=TIER, pool_ie_close=IE,
               keys=len(FP), deriv=len(DER), vform=VFORM, gates=(G1, G2), anchors=len(cites),
               anchor_face=(CLS1, CLSN, CLS5), anchor_ref=REF1, anchor_cross_unref=CROSS_UNREF,
               anchor_all5=ALL5, anchor_multi_max=MULTIMAX, checks=CHECKS, anchor_err=ERRN, anchor_amb=AMB_LINE,
               note_rows=NOTE_ROWS, pk_agree=len(PAGREE), pk_needles=PKCHK,
               hexes=HEX, sec_refs=SECREF, cit_space=CIT4, cit_hyphen=CITH, cit_bracket=CITB, cit_own=COWN, listed_before=LISTED0,
               needle_n=len(ROLEN), entry_bytes=len(S2.encode(u'utf-8'))),
          io.open(u'corpus/_b82readme.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（%d 条）编码 %s ⇎ 摘要 %s ⇎ 保留 %.1f%% ｜ 唯一码点(列内并集) %s ｜ 未记账 %s ｜ '
      u'audit 行 %d ⇎ 文件 %d ｜ 推导 %d 条 ｜ 本遍总判 %s%s ｜ B82 行 %s 编码／%s 摘要 ｜ 锚 %d 处⇎归属 %d 次⇎错配 %d ｜ '
      u'四档命中 %s ⇎ 切开 %d 枚(两半 %d 字符⇎幅度 %d 行⇎两半读通 %d⇎首行读不通 %d) ⇎ 跨行 %d 对 ⇎ 反向 %d 枚×%d 排除份探针(整词 %d 命中⇎子串点着 %d 次/%d 枚⇎主家差 %d 枚) ｜ '
      u'剥壳行 %s ⇎ 编号 %s 枚 ⇎ 池 %s 枚⇎两两 %d⇎三三 %d⇎四四 %d⇎容斥 %d ｜ 门 %d+%d ⇎ V 形 %d ⇎ DERIV %d ⇎ 契约 %d'
      % (len(LISTED), fmt(enc_all), fmt(dig_all), 100.0 * enc_all / dig_all, fmt(len(UNI)),
         u'⇎'.join(UN), len(GROW), len(FIDS), PROOFS, u'PASS' if GATE_PASS else u'FAIL',
         u'' if GATE_PASS else u'（只落在 %s）' % u'⇎'.join(sorted(FAILD)),
         fmt(E82), fmt(D82), len(cites), CHECKS, ERRN,
         V4(FACE), SPLITN, ROWTOT, SPANTOT, HALF_OK, FULL_HEAD,
         SP_N, len(NEG), NB0, ZERO, len(COLDHIT), CSUB, OSUB,
         V4(SL), V4(TSHC), fmt(len(UNION)), P2, P3,
         P4, IE, G1, G2, VFORM, len(DER), len(FP))
      + u' ｜ 注表 %d 行 ⇎ 采集侧换尺复对 %d 键 ⇎ %d 档针目 ｜ tagcut 掐断标注 %d 字符⇎窗口 %s'
      % (NOTE_ROWS, len(PAGREE), PKCHK, len(TG[4][0]), u' ⇎ '.join(str(x) for x in TGN)))
