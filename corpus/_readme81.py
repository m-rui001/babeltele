# -*- coding: utf-8 -*-
"""README 记账(B81): 门槛表行 ⇎ 语料表行 ⇎ 判词段 ⇐ 转化指标机械行 ⇐ 合计行 ⇐ 命令块 ⇐ 三处条数陈述,
全部按本遍现跑的 audit 与 raw 字节现量, 一个数不抄建条目侧或解读注侧的快照。

本遍是第七套实现(采集 ⇎ 建条目 ⇎ 审计器 SCAN ⇎ 审计器 SCAN2 ⇎ 解读注 之外), 六处换机制不换定义:
① 面量走字节平面(`bytes.count(b'\\n')` ⇎ `b'\\x0c'` ⇎ `b'\\r'` ⇎ BOM 看前三字节), 再 `decode` 取码位,
   与建条目侧(文本平面 `re.split`)并立; 行数三档关系在本条要加第四项: 两份论文面**以一枚裸换页符收尾**
   (`splitlines()` 不在文末空段上多切一刀), 故 切格档 = `split('\\n')` 档 − 末行换行 + 换页符 − 尾换页符;
② 针的枚数走 `str.count`(非重叠), 建条目侧是 `re.findall(re.escape(nd))`, 采集侧是游标 find 环;
③ 整词尺走带 lookaround 的正则(`(?<![A-Za-z])w(?![A-Za-z])`), 建条目侧是邻居字符手扫 `_nb/ub`;
④ 词窗尺走 n-gram 直方图(`Counter` 建全部 n 元组再查表), 建条目侧是滑窗逐枚全等比对;
⑤ 数值对走一条正则选择支(单位alternation 长者在前 ⇎ 前后断言), 建条目侧是手工扫数字串就地读单位词;
⑥ 壳谓词与页码尺不再重跑第三套判据, 改走**账**: 剥壳正文行 = 原行 − 壳行 = 非空行 − 非空壳行 ⇎
   壳行 = 空行 + 抬头行(RFC 面按页码行+眉行, 论文面按换页符起手的页码行), 四条独立量出的数互相归零;
⑦ 锚不用正则配对: 按 `⟦` 分段取首个 `⟨…⟩`, 逐枚切片回编码区原文, 再按标签回它自己那一源做归一核验;
   二十七枚判词针另走“只住在登记那一源、别处零枚”的排他核验;
⑧ 行文里点名的每一枚英文片段都要在它那一源的归一面上命中才允许落盘;
⑨ 唯一码点不抄 audit 的 ALL 行: 逐条现数并与 audit 的编码列对拍后取本表所列条目的并集;
   条数三处陈述全部由本遍现读的文件系统行集与 audit 自报数现算, 不做硬编码加减。
"""
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
LBL = [u'7567', u'madp', u'8033', u'cake', u'8289']
FAM = [u'rfc', u'paper', u'rfc', u'paper', u'rfc']
RFCI = [0, 2, 4]
PAPI = [1, 3]
YR = [u'2015', u'2016', u'2017', u'2018', u'2018']
SRC = [C + u'/raw/qdelay/rfc7567.txt', C + u'/raw/qdelay/piehdp.txt', C + u'/raw/qdelay/rfc8033.txt',
       C + u'/raw/qdelay/cake.txt', C + u'/raw/qdelay/rfc8289.txt']
SHW = [u'`' + p[len(C) + 1:] + u'`' for p in SRC]
KIND = [u'15 年 BCP：只下规范性语句，一枚带单位时长也不给',
        u'16 年论文：不自己数字，把别家默认引述一遍',
        u'17 年实验规范：给双档默认并把毫秒写全',
        u'18 年论文：不作宣称，只报实测',
        u'18 年标准轨道：先给定义式再导出']
ANS5 = [u'标题式判词', u'引述别家默认', u'双档默认全称', u'实测基线', u'定义式导出']
ENTRY = glob.glob(u'corpus/babeltele/B81_*.md')[0]
FP = json.load(io.open(u'corpus/_b81flat.json', encoding=u'utf-8'))
DER = json.load(io.open(u'corpus/_deriv81.json', encoding=u'utf-8'))
CH = json.load(io.open(u'corpus/_b81checks.json', encoding=u'utf-8'))

AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                     text=True, encoding=u'utf-8').stdout
VERD = [l for l in AUD.split(u'\n') if l.startswith(u'保真门槛(T1 字面 + T2 推导 + T3 码位):')]
assert len(VERD) == 1, VERD
FAILED = [l.split(u':')[0].strip() for l in AUD.split(u'\n') if re.match(u'^  B\\d+: ', l)]
assert u'B81' not in FAILED, FAILED
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


# ---------- ① 字节平面面量 ⇎ 行数四档 ----------
BS, CH_, LN, NLC, SPL, TAIL, NB, BLK, ML, O72, FFC, EFO, FIL, NFL, CR, CRW, NA, DELTA, XTRA = ([] for _ in range(19))
FFEND, BOM, NUL = [], [], []
TS, LS, L = [], [], []
for p in SRC:
    b = io.open(p, u'rb').read()
    t = b.decode(u'utf-8')
    TS.append(t)
    ls = re.split(u'\n', t)
    LS.append(ls)
    # 剥行尾回车走 endswith(建条目侧用 ord(y[-1])==13)
    L.append([y[:-1] if y.endswith(u'\r') else y for y in ls])
    BS.append(len(b))
    CH_.append(len(t))
    LN.append(len(ls))
    NLC.append(b.count(b'\n'))
    SPL.append(len(t.splitlines()))
    TAIL.append(1 if t.endswith(u'\n') else 0)
    FFEND.append(1 if t.endswith(u'\x0c') else 0)
    NB.append(len([x for x in L[-1] if x.strip()]))
    BLK.append(len(L[-1]) - NB[-1])
    ML.append(max(len(x) for x in L[-1]))
    O72.append(len([x for x in L[-1] if len(x) > 72]))
    FFC.append(b.count(b'\x0c'))
    EFO.append(len([x for x in L[-1] if x == u'\x0c']))
    FIL.append(FFC[-1] - EFO[-1])
    NFL.append(len([x for x in L[-1] if x.startswith(u'\x0c')]))
    CR.append(b.count(b'\r'))
    CRW.append(len([x for x in ls if x.endswith(u'\r')]))
    NA.append(len([c for c in t if ord(c) > 127]))
    XTRA.append(sum(len(c.encode(u'utf-8')) - 1 for c in t if ord(c) > 127))
    DELTA.append(len(b) - len(t))
    NUL.append(b.count(b'\x00'))
    BOM.append(1 if b[:3] == b'\xef\xbb\xbf' else 0)
for k, v in ((u'bytes', BS), (u'chars', CH_), (u'lines', LN), (u'newlines', NLC), (u'nonblank', NB),
             (u'blank', BLK), (u'maxlen', ML), (u'over72', O72), (u'wrap_rows', O72), (u'ff', FFC),
             (u'ff_exact', EFO), (u'ff_inline', FIL), (u'ff_lead', NFL), (u'cr', CR),
             (u'cr_rows', CRW), (u'nonascii', NA), (u'utf8_extra', XTRA), (u'byte_cp_delta', DELTA),
             (u'nul', NUL), (u'bom', BOM), (u'tail_nl', TAIL)):
    assert v == gk(k), (k, v, gk(k))
for i in range(NSRC):
    assert LN[i] == NLC[i] + 1, i
    assert CR[i] == CRW[i], i
    assert DELTA[i] == XTRA[i], i
    assert SPL[i] == LN[i] - TAIL[i] + FFC[i] - FFEND[i], (i, SPL[i], LN[i], TAIL[i], FFC[i], FFEND[i])
assert sum(NUL) == 0 and sum(BOM) == 0
assert CR == [0, 675, 0, 333, 0] and sum(CR) == 1008
assert FFEND == [0, 1, 0, 1, 0] and gk(u'crlf_rows') == [0, 1, 0, 1, 0]
assert ML == [72, 1109, 72, 1175, 72] and O72 == [0, 53, 0, 98, 0]
assert [O72[i] for i in PAPI] == [53, 98] and [O72[i] for i in RFCI] == [0, 0, 0]
assert NA == [0, 222, 0, 282, 0] and sum(NA[:1] + NA[2:3] + NA[4:]) == 0

# ---------- ② 四档面: 折平 ⇎ 摘壳 ⇎ 拆字, 全部由本遍自己的构造导出 ----------
def foldr(s):
    """折平: 无参 split 再 join(建条目侧是 re.split(r'\\s') 后滤空再 join)"""
    return u' '.join(s.split())


LIGM = {0xFB01: u'fi', 0xFB02: u'fl', 0x2019: u"'", 0x2018: u"'", 0x201C: u'"', 0x201D: u'"',
        0x2014: u'-', 0x2013: u'-', 0x2212: u'-'}
PAIRO = (0xFB01, 0xFB02)
GREEKO = (0x3C4, 0x3BB, 0x3B1, 0x3B2)
DASHQO = (0x2019, 0x201C, 0x201D, 0x2018, 0x2014, 0x2013, 0x2212)
TAB = dict((o, LIGM[o]) for o in LIGM)
assert set(TAB) == set(PAIRO + DASHQO) and len(TAB) == 9


def is_shell(x, fam):
    """第三档壳尺: 无参 split 切 token 后逐段比首尾(建条目侧在折平面上按一枚空格切, 采集侧跑整序正则)"""
    tk = x.split()
    if not tk:
        return True
    if fam == u'rfc':
        if len(tk) >= 2 and tk[-2] == u'[Page' and len(tk[-1]) >= 2 and tk[-1].endswith(u']') \
                and tk[-1][:-1].isdigit():
            return True
        if len(tk) >= 4 and tk[0] == u'RFC' and len(tk[1]) == 4 and tk[1].isdigit() \
                and len(tk[-1]) == 4 and tk[-1][:2] in (u'19', u'20') and tk[-1][2:].isdigit():
            return True
        return False
    return bool(x[:1] == u'\x0c' and x[1:].strip().isdigit())


SHELL = [[is_shell(x, FAM[i]) for x in L[i]] for i in range(NSRC)]
SL = [len([1 for k, h in enumerate(SHELL[i]) if h]) for i in range(NSRC)]
SLNB = [len([x for x, h in zip(L[i], SHELL[i]) if h and x.strip() != u'']) for i in range(NSRC)]
PGR = [len([x for x in L[i] if u'[Page' in x]) for i in range(NSRC)]
HDR = [SLNB[i] - PGR[i] if FAM[i] == u'rfc' else 0 for i in range(NSRC)]
PPR = [LN[i] - SL[i] for i in range(NSRC)]
PGN = [len([x for x in L[i] if re.fullmatch(u'[\\s\\d]+', x) and len(re.findall(u'\\d+', x)) == 1])
       for i in range(NSRC)]
PGF = [len([x for x in L[i] if x[:1] == u'\x0c' and re.fullmatch(u'[\\s\\d]+', x)
           and len(re.findall(u'\\d+', x)) == 1]) for i in range(NSRC)]
PGM = [len([x for x in L[i] if re.fullmatch(u'[\\s\\d]+', x) and len(re.findall(u'\\d+', x)) >= 2])
       for i in range(NSRC)]
for k, v in ((u'shell_lines', SL), (u'shell_nonblank', SLNB), (u'pp_rows', PPR), (u'pg_lines', PGR),
             (u'hdr_lines_tight', HDR), (u'pgnum_naive', PGN), (u'pgnum_ffled', PGF),
             (u'pgnum_multirun', PGM)):
    assert v == gk(k), (k, v, gk(k))
# 壳账三条独立归零: 剥壳正文行两把尺 ⇎ 壳行=空行+抬头行 ⇎ 论文面页码尺多剥的正是表格数字行
assert [PPR[i] - (NB[i] - SLNB[i]) for i in range(NSRC)] == [0] * NSRC
assert [SL[i] - BLK[i] - (PGR[i] + HDR[i] if FAM[i] == u'rfc' else PGF[i]) for i in range(NSRC)] == [0] * NSRC
assert [PGN[i] - PGF[i] - gk(u'pgnum_overstrip')[i] for i in range(NSRC)] == [0] * NSRC
assert [PGN[i] + PGM[i] - gk(u'pgnum_anyshape')[i] for i in range(NSRC)] == [0] * NSRC

FOLD, LOWFOLD, SH, LOWSH, SHLIG, LOWSHLIG = ([] for _ in range(6))
for i in range(NSRC):
    FOLD.append(foldr(TS[i]))
    LOWFOLD.append(FOLD[i].lower())
    SH.append(foldr(u'\n'.join([x for x, h in zip(L[i], SHELL[i]) if not h])))
    LOWSH.append(SH[i].lower())
    # 拆字: str.translate(建条目侧逐字符查表重建, 采集侧 str.replace 串链)
    SHLIG.append(SH[i].translate(TAB))
    LOWSHLIG.append(SHLIG[i].lower())
assert [len(SH[i]) for i in range(NSRC)] == gk(u'sh_chars')
assert [len(SHLIG[i]) for i in range(NSRC)] == gk(u'shlig_chars')
assert [len(FOLD[i]) for i in range(NSRC)] == gk(u'fold_chars')
assert [len(SHLIG[i]) - len(SH[i]) for i in range(NSRC)] == gk(u'lig_char_add')
LIGC = [[len([c for c in t if ord(c) == o]) for o in PAIRO] for t in TS]
assert LIGC == gk(u'lig_pair') and [sum(x) for x in LIGC] == gk(u'lig_total')
assert [len(SHLIG[i]) - len(SH[i]) - LIGC[i][0] - LIGC[i][1] for i in range(NSRC)] == [0] * NSRC
NAC = [[ord(c) for c in t if ord(c) > 127] for t in TS]
assert [len([o for o in NAC[i] if o in GREEKO]) for i in range(NSRC)] == gk(u'na_greek')
assert [len([o for o in NAC[i] if o in DASHQO]) for i in range(NSRC)] == gk(u'na_dashq')
assert [len([o for o in NAC[i] if o not in PAIRO + GREEKO + DASHQO]) for i in range(NSRC)] == gk(u'na_other')
assert [LIGC[i][0] + LIGC[i][1] + gk(u'na_greek')[i] + gk(u'na_dashq')[i] + gk(u'na_other')[i]
        - NA[i] for i in range(NSRC)] == [0] * NSRC

# ---------- ③④ 针的枚数: str.count ⇎ lookaround 整词尺 ⇎ n-gram 词窗尺 ----------
ROLEN = gk(u'role_fam')
RSRC = gk(u'role_src')
NUMF, UNITF, TERMF, SPELLF, TONEF = gk(u'num_fam'), gk(u'unit_fam'), gk(u'term_fam'), gk(u'spell_fam'), gk(u'tone_fam')


def sc(hay, nd):
    return hay.count(nd)


def wcnt(s, w):
    return len(re.findall(u'(?<![A-Za-z])' + re.escape(w) + u'(?![A-Za-z])', s))


def ngram(tokens, nd):
    p = tuple(nd.split(u' '))
    n = len(p)
    return Counter(tuple(tokens[k:k + n]) for k in range(len(tokens) - n + 1))[p]


TOKR = [LOWSHLIG[i].split(u' ') for i in range(NSRC)]
RL = [[sum(sc(y.lower(), nd) for y in L[i]) for nd in ROLEN] for i in range(NSRC)]
RF = [[sc(LOWFOLD[i], nd) for nd in ROLEN] for i in range(NSRC)]
RS = [[sc(LOWSH[i], nd) for nd in ROLEN] for i in range(NSRC)]
RG = [[sc(LOWSHLIG[i], nd) for nd in ROLEN] for i in range(NSRC)]
for k, v in ((u'role_line', RL), (u'role_fold', RF), (u'role_sh', RS), (u'role_lig', RG)):
    assert v == gk(k), (k, v[:1], gk(k)[:1])
FACET = [[sum(RL[i]) if k == 0 else sum(RF[i]) if k == 1 else sum(RS[i]) if k == 2 else sum(RG[i])
          for i in range(NSRC)] for k in range(4)]
assert FACET == gk(u'role_by_face')
FACE = [sum(x) for x in FACET]
assert FACE == gk(u'face_tot')
assert [FACE[k] - FACE[k - 1] for k in range(1, 4)] == gk(u'face_gain')
assert sum(RF[i][k] - RL[i][k] for i in range(NSRC) for k in range(len(ROLEN))) == gk(u'gain_fold_tot')
assert sum(RS[i][k] - RF[i][k] for i in range(NSRC) for k in range(len(ROLEN))) == gk(u'gain_sh_tot')
assert sum(RG[i][k] - RS[i][k] for i in range(NSRC) for k in range(len(ROLEN))) == gk(u'gain_lig_tot')
# 排他核验: 二十七枚判词针只住在它登记的那一源, 别处零枚
for k in range(len(ROLEN)):
    i = LBL.index(RSRC[k])
    assert RG[i][k] >= 1, (k, ROLEN[k])
    assert sum(RG[j][k] for j in range(NSRC) if j != i) == 0, (k, ROLEN[k])
UNIT_ = [[sc(LOWSHLIG[i], nd) for nd in UNITF] for i in range(NSRC)]
UNITW_ = [[wcnt(LOWSHLIG[i], nd) for nd in UNITF] for i in range(NSRC)]
assert UNIT_ == gk(u'unit') and UNITW_ == gk(u'unit_word')
assert [UNIT_[i][0] - UNITW_[i][0] for i in range(NSRC)] == gk(u'unit_sub_over')
NUM_ = [[sc(LOWSHLIG[i], nd) for nd in NUMF] for i in range(NSRC)]
assert NUM_ == gk(u'num') and [sum(x) for x in NUM_] == gk(u'num_tot')
TERM_ = [[sc(LOWSHLIG[i], nd) for nd in TERMF] for i in range(NSRC)]
SPELL_ = [[sc(LOWSHLIG[i], nd) for nd in SPELLF] for i in range(NSRC)]
assert TERM_ == gk(u'term') and SPELL_ == gk(u'spell')
assert [[ngram(TOKR[i], nd) for nd in TERMF] for i in range(NSRC)] == gk(u'term_word')
assert [[ngram(TOKR[i], nd) for nd in SPELLF] for i in range(NSRC)] == gk(u'spell_word')
assert [sum(TERM_[i][k] - gk(u'term_word')[i][k] for k in range(len(TERMF))) for i in range(NSRC)] == gk(u'term_ruler_gap')
TONE_ = [[wcnt(SHLIG[i], nd) for nd in TONEF] for i in range(NSRC)]
assert TONE_ == gk(u'tone_sh')
# 原面逐行档(把逐行枚数加总)与摘壳档只差 8289 那一枚被 72 列线切开的 SHOULD NOT
TONE0 = [[sum(wcnt(y, nd) for y in L[i]) for nd in TONEF] for i in range(NSRC)]
assert TONE0 == gk(u'tone_raw')
assert sum(TONE_[i][k] - TONE0[i][k] for i in range(NSRC) for k in range(5)) == gk(u'tone_straddle_n')

# ---------- ⑤ 数值对: 一条正则选择支(单位长者在前 + 前后断言) ----------
UW_S = (u'milliseconds', u'microseconds', u'ms', u'second', u's')
UW_T = (u'milliseconds', u'microseconds', u'seconds', u'ms')
RX_T = re.compile(u'(?<![A-Za-z0-9.])(\\d+(?:[.,]\\d+)?)[ ]?(' + u'|'.join(UW_T) + u')(?![A-Za-z])')
RX_S = re.compile(u'(?<![A-Za-z0-9.])(\\d+(?:[.,]\\d+)?)[ ]?(' + u'|'.join(UW_S) + u')(?![A-Za-z])')
PAIRS_T = [sorted(set(RX_T.findall(LOWSHLIG[i]))) for i in range(NSRC)]
PAIRS_S = [sorted(set(RX_S.findall(LOWSHLIG[i]))) for i in range(NSRC)]
NV = [[tuple(y) for y in gk(u'numvals')[i]] for i in range(NSRC)]
NX = [[tuple(y) for y in gk(u'numval_s_pairs')[i]] for i in range(NSRC)]
assert PAIRS_T == NV and PAIRS_S == NX
assert [len(x) for x in PAIRS_T] == gk(u'numval_n')
# 严尺收 “5 seconds”, 宽尺的 second 支被尾随 s 挡住、s 支被 e 挡住 ⇒ 宽档反而丢这一枚
assert [[x for x in NX[i] if x not in NV[i]] for i in range(NSRC)] == \
       [[tuple(y) for y in gk(u'numval_s_extra')[i]] for i in range(NSRC)]
assert [[x for x in NV[i] if x not in NX[i]] for i in range(NSRC)] == \
       [[tuple(y) for y in gk(u'numval_s_lost')[i]] for i in range(NSRC)]

# ---------- ⑥⑦ 锚: 按 ⟦ 分段手吃 ⟨…⟩, 回编码区 ⇎ 回自己那一源 ----------
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
    assert FLATENC.find(seg[a:z]) >= 0
assert len(cites) == gk(u'anchor_total'), (len(cites), gk(u'anchor_total'))
DIS = set([x[1] for x in cites])
assert len(DIS) == gk(u'anchor_distinct')
PER = dict((t, len([x for x in cites if x[0] == t])) for t in LBL)
assert PER == dict((t, gk(u'tag_' + t)) for t in LBL)
P5 = [pn(TS[i]) for i in range(NSRC)]
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
assert all(len(FACEHIT[q]) >= len(REFHIT[q]) for q in DIS)
assert CLS1 + CLSN + CLS5 == gk(u'anchor_distinct')
CROSS_UNREF = len([q for q in DIS if 1 < len(FACEHIT[q]) and len(REFHIT[q]) == 1])
assert REF1 - CLS1 == CROSS_UNREF
assert REF1 + REFN == gk(u'anchor_distinct') and REFN <= CLSN
# 同一串被多个标签共引的只有模板句那枚: 它挂在三份规范名下, 也只在三份规范面上读到
MULTI = sorted([q for q in DIS if len(REFHIT[q]) > 1])
assert len(MULTI) == REFN
assert [REFHIT[q] for q in MULTI] == [set(LBL[i] for i in RFCI)]
assert [FACEHIT[q] for q in MULTI] == [list(RFCI)]
assert gk(u'checks') == gk(u'anchor_distinct') * NSRC and gk(u'anchor_err') == 0
# 五面同串的那一枚到底是什么(本遍现数, 不抄解读注的手打记忆)
ALL5 = sorted([q for q in DIS if len(FACEHIT[q]) == NSRC])
assert len(ALL5) == CLS5 == gk(u'anchor_all5')
if CLS5:
    assert len(ALL5[0]) == 2 and ALL5[0] == u'ms'
    assert [gk(u'unit_word')[i][0] for i in (0, 2)] == [0, 0] and [gk(u'unit')[i][0] for i in (0, 2)] != [0, 0]

# ---------- ⑧ 行文点名的英文片段一律回自己那一源的归一面核验 ----------
FRAG = {u'7567': [u'AQM Algorithm Deployment SHOULD NOT Require Operational Tuning',
                  u'the key words', u'as described in'],
        u'madp': [u'its default target delay of 20 ms', u'burst allowance of 100 ms',
                  u'the assumption that the Round Trip Time (RTT) is 100 ms'],
        u'8033': [u'defaulted to 15 milliseconds and 150 milliseconds for non-data-center',
                  u'15 microseconds and 150 microseconds for data-center switches',
                  u'self-configuring'],
        u'cake': [u'50 ms baseline latency', u'10 Mbps link', u'We use the Flent'],
        u'8289': [u'Using this RTT gives a minimum TARGET of 5 ms', u'not recommended',
                  u'sojourn', u'5-10%', u'parameter-free']}
FHITS = dict((f, [i for i in range(NSRC) if pn(f) in P5[i]])
             for frs in FRAG.values() for f in frs)
for lab, frs in FRAG.items():
    for f in frs:
        assert LBL.index(lab) in FHITS[f], (lab, f)
# 行文说“只活在一家”的那几枚, 由面上现数确认只命中一面
CLAIM_OWN = {u'sojourn': u'8289', u'parameter-free': u'8289', u'self-configuring': u'8033',
             u'We use the Flent': u'cake', u'the assumption that the Round Trip Time (RTT) is 100 ms': u'madp',
             u'AQM Algorithm Deployment SHOULD NOT Require Operational Tuning': u'7567'}
for f, lab in CLAIM_OWN.items():
    assert FHITS[f] == [LBL.index(lab)], (f, lab, FHITS[f])
# 独家的数值式换到最宽的档重测: 不折平、不剥壳、不拆字, 只在原文件小写面上数, 别处仍须为零
LOWTS = [t.lower() for t in TS]
OWNFRAG = [(LBL[i], x) for i in range(NSRC) for x in gk(u'num_own')[i]]
for lab, f in OWNFRAG:
    assert sc(LOWSHLIG[LBL.index(lab)], f.lower()) >= 1, (lab, f)
    assert [i for i in range(NSRC) if f.lower() in LOWTS[i]] == [LBL.index(lab)], (lab, f)

# ---------- 转化指标: 逐条现数, 列内并集 ----------
GROW, ALLR = [], None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        GROW.append([x.strip() for x in l.split(u'|')[1:-1]])
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR
ROWS = dict((c[0], c) for c in GROW)
SL81 = ROWS[u'B81']
E81, D81 = num(SL81[2]), num(SL81[1])
assert E81 == gk(u'enc_chars'), (E81, gk(u'enc_chars'))
# 摘要段用命令块里那组 300/200 窗口在副本上重建, 与在库文件逐字节相同才允许把该命令写进 README
DGH = u'corpus/_tmp81dgh.md'
io.open(DGH, u'w', encoding=u'utf-8', newline=NL).write(TT)
_dg = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/_mkdigest3.py', u'B81', DGH]
                     + sum([[LBL[i], SRC[i], u'300', u'200'] for i in range(NSRC)], []),
                     capture_output=True, text=True, encoding=u'utf-8').stdout
assert io.open(DGH, encoding=u'utf-8').read() == TT, u'副本重建与在库文件不同形'
assert (u'digest_total=%d' % D81 in _dg
        and u'atoms=%d union_hit=%d' % (gk(u'anchor_total'), gk(u'anchor_total')) in _dg), _dg
os.remove(DGH)
LINES_S = S.split(NL)
hh = [i for i, l in enumerate(LINES_S) if l.startswith(u'| entry | 编码字符 |')]
assert len(hh) == 1
tt0 = [i for i in range(hh[0], len(LINES_S)) if LINES_S[i].startswith(u'| **合计（')]
assert len(tt0) == 1
LISTED0 = [l.split(u'|')[1].strip() for l in LINES_S[hh[0] + 2:tt0[0]]]
assert all(x.startswith(u'B') for x in LISTED0)
assert u'B81' not in LISTED0 and S.count(u'| B81 |') == 0 and S.count(u'**B81 问的是') == 0
LISTED = sorted(LISTED0 + [u'B81'], key=lambda k: int(k[1:]))
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
assert SL81[3] == u'%.1f%%' % (100.0 * E81 / D81), (SL81[3], E81, D81)
assert SL81[4] == u'%.3f%%' % (100.0 * E81 / sum(BS)), SL81[4]
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])
VFORM = len(CH[u'zid'])
DKEYS = len(set(re.findall(u"B81V\\('([a-z0-9_]+)'", json.dumps(DER, ensure_ascii=False))) & set(FP))
CLOSEK = len([k for k in FP if u'close' in k])

# 闭合账(本遍自算一遍再与契约对拍): 五份面各自的阶梯 ⇎ 池容斥 ⇎ 拆字长度
assert gk(u'face_mono') == sum([1 for k in range(1, 4) if FACE[k] >= FACE[k - 1]])
assert gk(u'pool_ie_close') == 0 and gk(u'pool_sum_close') == 0 and gk(u'pool_tier_close') == 0
assert sum(gk(u'pool_tier')) == gk(u'pool_union')
assert gk(u'shell_ledger') == [0] * NSRC and gk(u'shell_pred_diff') == 0
assert gk(u'byte_cp_ledger') == [0] * NSRC and gk(u'na_ledger') == [0] * NSRC
assert gk(u'lig_add_close') == [0] * NSRC and gk(u'num_lig_gap') == [0] * NSRC
assert gk(u'bool_all_sum') == gk(u'bool_all_n') and gk(u'bool_clos_sum') == gk(u'bool_clos_n')
assert gk(u'bool_clos2_sum') == gk(u'bool_clos2_n')
assert gk(u'pick_diff') == 0 and gk(u'pick_agree') == gk(u'pick_same_n')
assert gk(u'nsrc') == NSRC and gk(u'contract_n') == len(FP)
# 切开判词两把尺: 折行 ⇎ 页壳, 二者相加等于切开针总数
assert gk(u'split_wrap_n') + gk(u'split_shell_n') == gk(u'split_n')
assert gk(u'split_half_ok') == gk(u'split_n') and gk(u'split_full_on_head') == 0
assert [gk(u'tone_raw')[i][k] - gk(u'tone_sh')[i][k] for i in range(NSRC) for k in range(5)].count(0) == 24
assert gk(u'tone_straddle') == [0, 0, 0, 0, 1] and gk(u'only_8289_tone_straddle') == 1
# 套版长行池: 三份规范之间 ⇎ 凡牵进论文的每一对
assert gk(u'pool_pair_rfc') + gk(u'pool_pair_paper') == gk(u'pool_pair_tot')
assert gk(u'pool_pair_paper') == 0 and gk(u'pool_pair_paper_n') == 7
assert len(gk(u'num_own')[0]) == 0 and gk(u'num_cold') == [u'15 ms']
assert gk(u'cfg_claim')[3] == 0 and gk(u'pool_paper_in_toned') == 0

# ---------- 门槛表 B81 行 ----------
HEADROW = (u'| B81 | ' + fmt(E81) + u'（新建, 一个 AQM 该把排队延迟压到多少、依据什么 交三份 RFC Editor 纯文本面 ⇎ '
           u'两份 pdftotext 论文面各答一遍 ' + str(gk(u'anchor_total')) + u' 处标注／' + str(gk(u'anchor_distinct'))
           + u' 个不同串（登记全命中, 单源 ' + str(gk(u'anchor_single')) + u' ⇎ 穿二至四源 ' + str(gk(u'anchor_cross'))
           + u' ⇎ 五源全现 ' + str(gk(u'anchor_all5')) + u'——同串那枚是两字母短形 “' + ALL5[0] + u'”: '
             u'子串轨五面 ' + V4([gk(u'unit')[i][0] for i in range(NSRC)]) + u' 枚都有它 ⇎ 整词轨只在 '
             + LBL[0] + u' ⇎ ' + LBL[2] + u' 两面上读到 ' + str(gk(u'unit_word')[0][0]) + u' ⇎ '
             + str(gk(u'unit_word')[2][0]) + u' 枚（' + LBL[4] + u' 整词 ' + str(gk(u'unit_word')[4][0])
             + u' 枚）; 编码区 ' + fmt(E81) + u' 字符, 归属检查 ' + str(gk(u'checks')) + u' 次, 错配 '
           + str(gk(u'anchor_err')) + u'）: 五色锚位 ' + u' ⇎ '.join(x + u' ⟦' + x + u'⟧' for x in LBL)
           + u'（' + u' ⇎ '.join(str(PER[t]) for t in LBL) + u' 处）; 四档口径（原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳加拆字折平）'
             u'在 ' + str(len(ROLEN)) + u' 枚判词针上读到 ' + V4(FACE) + u' 次命中, 增益 ' + V4(gk(u'face_gain'))
           + u' 枚 ⇎ 单调 ' + str(gk(u'face_mono')) + u'/3 档——折平救回 ' + str(gk(u'gain_fold_tot')) + u' 枚（逐份 '
           + V4(gk(u'role_straddle')) + u'）, 摘壳新读 ' + str(gk(u'gain_sh_tot')) + u' 枚而一粒不丢（丢 '
           + str(gk(u'gain_sh_dup')) + u' 枚, 新读的是 ' + u' ⇎ '.join(ROLEN[k] for k in gk(u'role_shell_needles'))
           + u' 两枚被跨页页壳切开）, 拆字档比摘壳档多 ' + str(gk(u'gain_lig_tot')) + u' 枚: '
           + str(gk(u'lig_total')[1]) + u' ⇎ ' + str(gk(u'lig_total')[3]) + u' 枚连字全在论文面上, 而判词针一枚也不住论文面；'
             u'被线切开的判词 ' + str(gk(u'split_n')) + u' 枚（换行 ' + str(gk(u'split_wrap_n')) + u' ⇎ 页壳 '
           + str(gk(u'split_shell_n')) + u'）两半各归一行都读得通（' + str(gk(u'split_half_ok')) + u'/' + str(gk(u'split_n'))
           + u'）, 整串拿到首行 ' + str(gk(u'split_full_on_head')) + u' 枚读不通; 语气五轨（MUST NOT ⇎ MUST ⇎ SHOULD NOT ⇎ SHOULD ⇎ MAY）'
             u'摘壳档逐份 ' + V4([sum(x) for x in gk(u'tone_sh')]) + u' ⇎ 原面逐行 ' + V4([sum(x) for x in gk(u'tone_raw')])
           + u'（差 ' + str(gk(u'tone_straddle_n')) + u' 枚, 只在 8289 的 SHOULD NOT 跨 820/821 行）⇎ 论文两面五式全零; '
             u'数值十七式逐份 ' + V4(gk(u'num_tot')) + u' 枚（7567 十七式全冷 ⇎ 全库只冷一式 ' + str(gk(u'num_cold_n'))
           + u' 枚 “' + gk(u'num_cold')[0] + u'” ⇎ 独家式 ' + str(gk(u'num_own_tot')) + u' 枚）⇎ 六式单位子串轨 '
           + str(gk(u'unit_tot')[0]) + u' ⇎ ' + str(gk(u'unit_tot')[1]) + u' ⇎ ' + str(gk(u'unit_tot')[2]) + u' ⇎ '
           + str(gk(u'unit_tot')[3]) + u' ⇎ ' + str(gk(u'unit_tot')[4]) + u' ⇎ ' + str(gk(u'unit_tot')[5])
           + u' 枚而整词轨差 ' + V4(gk(u'unit_sub_over')) + u' 枚（“' + LBL[0] + u'”面上 ' + str(gk(u'unit_sub_over')[0])
           + u' 枚 ms 全是长词尾部）；八式术语 delay ⇎ latency 偏斜比 ' + V4(gk(u'term_skew')) + u' ⇎ 一家独术语 '
           + str(gk(u'term_own_tot')) + u' 式（sojourn ' + str(gk(u'term')[4][7]) + u' 枚只活在 8289, 别四份 '
           + str(sum(gk(u'term')[i][7] for i in range(4))) + u' 枚）⇎ 五式拼写主拼 ' + u' ⇎ '.join(gk(u'spell_side'))
           + u'（只持一拼的 ' + str(gk(u'spell_one_n')) + u' 份）；免配置宣称族 ' + V4(gk(u'cfg_claim'))
           + u' ⇎ 一家独式 ' + str(gk(u'cfg_own_tot')) + u' 式, 论文 cake 通篇 ' + str(gk(u'cfg_claim')[3]) + u' 枚宣称; '
             u'参数名族 TARGET ⇎ INTERVAL ' + str(gk(u'par')[4][0]) + u' ⇎ ' + str(gk(u'par')[4][1]) + u' 枚只在 8289, '
             u'希腊字母式 ' + str(sum(gk(u'par_greek_n'))) + u' 枚只在 madp; 套版长行池 ' + str(gk(u'pool_union'))
           + u' 枚分档 ' + V4(gk(u'pool_tier')) + u', 两两共用 RFC 之间 ' + str(gk(u'pool_pair_rfc')) + u' ⇎ 凡牵进论文的每一对 '
           + str(gk(u'pool_pair_paper')) + u'（' + str(gk(u'pool_pair_paper_n')) + u' 对全冷）⇎ 三三 '
           + str(gk(u'pool_trip_tot')) + u' ⇎ 容斥 ' + str(gk(u'pool_ie_close')) + u'; 关键词模板段三份各印一次而互不相同: '
             u'共头 ' + str(gk(u'pre_kw_7567_8033')) + u'/' + str(gk(u'pre_kw_7567_8289')) + u'/' + str(gk(u'pre_kw_8033_8289'))
           + u' 词 ⇎ 共尾 ' + str(gk(u'suf_kw_7567_8033')) + u'/' + str(gk(u'suf_kw_7567_8289')) + u'/' + str(gk(u'suf_kw_8033_8289'))
           + u' ⇎ NOT RECOMMENDED 只在 8289（' + str(gk(u'kw_notrec_tot')) + u' 枚）⇎ 论文面无此段, 行号按 -1 登记 '
           + V4(gk(u'kw_minus_row')) + u'; 节窗档 ' + u' ⇎ '.join(gk(u'sec_no')) + u' 节 ' + V4(gk(u'sec_lines'))
           + u' 行 ⇎ 占比 ' + V4(gk(u'sec_span_pct')) + u'% ⇎ 节内义务词 ' + V4(gk(u'sec_tone_tot')) + u' 枚; '
             u'反向对照 ' + str(gk(u'neg_n')) + u' 枚针 ' + str(gk(u'neg_probes')) + u' 次探针全冷（最宽档 '
           + str(gk(u'neg_zero_hits')) + u' 命中 ⇎ 子串轨假阳 ' + str(gk(u'neg_sub_false')) + u' 枚）; 版式两岔: 三份规范面 72 列硬换行'
             u'（超 72 列 ' + V4([0, 0, 0]) + u' 行）⇎ 两份论文面最长行 ' + str(ML[1]) + u' ⇎ ' + str(ML[3]) + u' 列（超长行 '
           + str(O72[1]) + u' ⇎ ' + str(O72[3]) + u' 行）⇎ 非 ASCII ' + str(NA[1]) + u' ⇎ ' + str(NA[3]) + u' 枚全在论文面, '
             u'规范面 ' + str(sum([NA[i] for i in RFCI])) + u' 枚, 回车 ' + str(sum(CR)) + u' 枚也全在论文面（CRLF 收尾行 '
           + V4(gk(u'cr_rows')) + u'）; 闭合账 布尔门 ' + str(gk(u'bool_all_sum')) + u'/' + str(gk(u'bool_all_n'))
           + u' ⇎ V 形恒等式 ' + str(VFORM) + u' 条 ⇎ 对账 ' + str(gk(u'pick_agree')) + u' 键符 ' + str(gk(u'pick_diff'))
           + u' 不符 ⇎ 锚 ' + str(gk(u'anchor_total')) + u' 处去重 ' + str(gk(u'anchor_distinct')) + u'。门槛侧 '
           + str(len(DER)) + u' 枚 DERIV 算式 ⇎ 扁平契约 ' + str(len(FP)) + u' 枚键由采集 ⇎ 建条目 ⇎ 审计两轨 ⇎ 解读注 ⇎ 本遍'
             u'六套实现逐枚复测, 其中 ' + str(DKEYS) + u' 枚进得了 DERIV 算式 ⇎ ' + str(CLOSEK) + u' 枚是闭合账位。） |')
assert HEADROW.count(u'|') == 3 and HEADROW.count(u'`') % 2 == 0

# ---------- 语料表 B81 行 ----------
C81 = (u'| B81 | ' + u' ⇎ '.join(
    SHW[i] + u'（' + YR[i] + u' ⟦' + LBL[i] + u'⟧：' + fmt(BS[i]) + u' 字节／面内码位 ' + fmt(CH_[i])
    + u'／行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i]) + u'／最长行 ' + str(ML[i]) + u' 列（超 72 列 ' + str(O72[i])
    + u' 行）／换页符 ' + str(FFC[i]) + u' 枚（独占整行 ' + str(EFO[i]) + u' 行, 行内混排 ' + str(FIL[i])
    + u' 枚, 起手于换页符 ' + str(NFL[i]) + u' 行, 剥壳行 ' + fmt(SL[i]) + u' 行＝空行 ' + fmt(BLK[i])
    + u' ＋页码行 ' + str(PGR[i]) + u' ＋眉行 ' + str(HDR[i]) + (u' ＋论文面页码行 ' + str(PGF[i])
                       if FAM[i] == u'paper' else u'') + u'）／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i])
    + u'（连字 ' + str(LIGC[i][0] + LIGC[i][1]) + u' ⇎ 希腊 ' + str(gk(u'na_greek')[i]) + u' ⇎ 引号破折 ' + str(gk(u'na_dashq')[i]) + u' ⇎ 其余 '
    + str(gk(u'na_other')[i]) + u'）／BOM ' + str(BOM[i]) + u'／答句 ' + ANS5[i] + u'）'
    for i in range(NSRC))
    + u' | 五份答同一个问题 ⇒ 答的是五种东西: 7567 把答句写成规范性标题（§4.3 正文 ' + str(gk(u'sec_body_line')[0])
      + u' 行 ⇎ 目录 ' + str(gk(u'sec_toc_line')[0]) + u' 行各印一次, 标题形计数全库只它非零 ' + str(gk(u'head_tone_shape')[0])
      + u' 枚, 十七式数值 ' + str(gk(u'num_tot')[0]) + u' 枚） ⇎ madp 自己不立数, 只引述别家默认（20 ms '
      + str(gk(u'num')[1][3]) + u' ⇎ 100 ms ' + str(gk(u'ms100_count')[1]) + u' 枚, 六式角色针里两枚归它） ⇎ 8033 把毫秒写全: '
      + u'全称四式 ' + str(gk(u'num')[2][10]) + u'/' + str(gk(u'num')[2][11]) + u'/' + str(gk(u'num')[2][12]) + u'/'
      + str(gk(u'num')[2][13]) + u' 枚 ⇎ 缩写 ms 整词 ' + str(gk(u'unit_word')[2][0]) + u' 枚 ⇎ 免配置写成陈述句（宣称 '
      + str(gk(u'cfg_claim')[2]) + u' 枚） ⇎ cake 只报实测（宣称 ' + str(gk(u'cfg_claim')[3]) + u' ⇎ 义务词五式 '
      + str(sum(gk(u'tone_sh')[3])) + u' 枚, 第一人称动词 ' + str(gk(u'voice_weverb')[3]) + u' 枚） ⇎ 8289 先给定义式再由 '
      + str(gk(u'ms100_count')[4]) + u' 枚 100 ms 天花板导出 TARGET 5 ms ⇎ INTERVAL 100 ms（参数名 '
      + str(gk(u'par')[4][0] + gk(u'par')[4][1]) + u' 枚 ⇎ sojourn ' + str(gk(u'term')[4][7]) + u' 枚为一家术语）; '
      + u'谁引谁: 引用族 ' + V4(gk(u'cit_rfc')) + u' 枚, 而五面互引矩阵里只有 madp→7567 '
      + str(gk(u'cite_matrix')[1][0]) + u' 枚 ⇎ 8033→7567 ' + str(gk(u'cite_matrix')[2][0]) + u' 枚, 最新两份对外引用 '
      + str(gk(u'cite_matrix')[3][0] + gk(u'cite_matrix')[4][0]) + u' 枚; 版式吃掉判词: 切开 ' + str(gk(u'split_n'))
      + u' 枚（' + str(gk(u'split_wrap_n')) + u' 枚由 72 列换行 ⇎ ' + str(gk(u'split_shell_n')) + u' 枚由跨页页壳, 夹 '
      + str(gk(u'split_shell_between')[0]) + u' ⇎ ' + str(gk(u'split_shell_between')[1]) + u' 行非空壳）⇎ 幅度合计 '
      + str(gk(u'split_span_tot')) + u' 行 ⇎ 两半 ' + str(gk(u'split_rows_tot')) + u' 字符; 唯一用“码+括号名”印法的条目不是本条——'
      u'本条的五种印法是“时长+单位”“全称”“比例”“实测值”“定义式” |')
assert C81.count(u'|') == 4 and C81.count(u'`') % 2 == 0

# ---------- 判词段 ----------
PARA = (u'**B81 问的是一个 AQM 该把排队延迟压到多少、依据什么，五份一手文书给出五种答法**：'
        + u' ⇎ '.join(SHW[i] + u'（' + YR[i] + u' ⟦' + LBL[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
                      + u'／非空行 ' + fmt(NB[i]) + u'／最长行 ' + str(ML[i]) + u' 列／换页符 ' + str(FFC[i])
                      + u' 枚／剥壳行 ' + fmt(SL[i]) + u' 行／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i])
                      + u'／答句 ' + ANS5[i] + u'）' for i in range(NSRC))
        + u'——三份规范面同为 72 列硬换行面且换页符独占整行（' + V4([FFC[i] for i in RFCI]) + u' 枚 ⇎ 行内混排 '
        + V4([FIL[i] for i in RFCI]) + u' 枚）, 两份论文面是 pdftotext 面：超长行 ' + str(O72[1]) + u' ⇎ ' + str(O72[3])
        + u' 行 ⇎ CRLF ' + str(CR[1]) + u' ⇎ ' + str(CR[3]) + u' 行 ⇎ 非 ASCII ' + str(NA[1]) + u' ⇎ ' + str(NA[3])
        + u' 枚（连字 ' + str(LIGC[1][0] + LIGC[1][1]) + u' ⇎ ' + str(LIGC[3][0] + LIGC[3][1]) + u' 枚, 拆字给摘壳面各加 '
        + str(gk(u'lig_char_add')[1]) + u' ⇎ ' + str(gk(u'lig_char_add')[3]) + u' 字符, 与连字枚数同值 ⇎ 规范面 '
        + V4([gk(u'lig_char_add')[i] for i in RFCI]) + u'）⇎ 两份论文面都以一枚裸换页符收尾, 于是换行档 ⇎ 切格档 ⇎ '
        + u'`splitlines()` 档三把尺的关系在这里要多减一枚尾换页符（' + V4(SPL) + u' ⇎ ' + V4(LN) + u' ⇎ ' + V4(TAIL)
        + u' ⇎ ' + V4(FFEND) + u'）; 抬头年 ' + u' ⇎ '.join(str(y) for y in gk(u'years')) + u', 跨 '
        + str(max(gk(u'years')) - min(gk(u'years'))) + u' 年。'
        + u'“该压到多少”这句话的五种印法: 7567 通篇 ' + str(gk(u'num_tot')[0]) + u' 枚带单位时长（十七式数值读数逐式 '
        + str(gk(u'num_zero_n')[0]) + u' 式为零）, 它把主张写成规范性标题 ⟦7567⟧⟨' + gk(u'ans')[0] + u'⟩——§4.3 正文 '
        + str(gk(u'sec_body_line')[0]) + u' 行 ⇎ 目录 ' + str(gk(u'sec_toc_line')[0]) + u' 行各印一次, 目录那行还带着点线引导符（'
        + str(gk(u'head_toc_leader_spaced')[0]) + u' 枚）; 全库标题形计数只它非零（' + V4(gk(u'head_tone_shape'))
        + u' 枚）⇎ madp 立数方式只有引述: ⟦madp⟧⟨' + gk(u'ans')[1] + u'⟩（' + str(gk(u'num')[1][3]) + u' 枚 20 ms 全库仅此一份,'
        + u' “100 ms” ' + str(gk(u'ms100_count')[1]) + u' 枚的两个角色都是引述——PIE 的突发容忍 ⇎ CoDel 的 RTT 假设）⇎ '
        + u'8033 给双档默认并把毫秒写全: ⟦8033⟧⟨' + gk(u'ans')[2] + u'⟩（全称四式 ' + str(sum(gk(u'num')[2][10:14]))
        + u' 枚 ⇎ 缩写 ms 整词 ' + str(gk(u'unit_word')[2][0]) + u' 枚, 但子串轨读到 ' + str(gk(u'unit')[2][0])
        + u' 枚——差 ' + str(gk(u'unit_sub_over')[2]) + u' 枚全住在 requirements／milliseconds 这类长词里）⇎ cake 不作宣称只报实测: '
        + u'⟦cake⟧⟨' + gk(u'ans')[3] + u'⟩（宣称族命中 ' + str(gk(u'cfg_claim')[3]) + u' 枚 ⇎ 义务词五式 '
        + str(sum(gk(u'tone_sh')[3])) + u' 枚 ⇎ 数值九枚全是实测值, 独家式 ' + u' '.join(gk(u'num_own')[3]) + u'）⇎ '
        + u'8289 先给定义式再导出: TARGET = RTT 的 ' + str(gk(u'num')[4][15]) + u' 枚“5-10%” ⇎ 由 100 ms 天花板导出 '
        + u'⟦8289⟧⟨' + gk(u'ans')[4] + u'⟩（参数名 TARGET/INTERVAL ' + str(gk(u'par')[4][0]) + u' ⇎ '
        + str(gk(u'par')[4][1]) + u' 枚为全库唯一 ⇎ sojourn ' + str(gk(u'term')[4][7]) + u' 枚只活在它家, 别四份合计 '
        + str(sum(gk(u'term')[i][7] for i in range(4))) + u' 枚）。'
        + u'术语 ⇎ 单位 ⇎ 语态三线同时分家: delay ⇎ latency 偏斜比 ' + V4(gk(u'term_skew')) + u'（'
        + u' ⇎ '.join(gk(u'term_side')) + u'）⇎ 五式拼写主拼 ' + u' ⇎ '.join(gk(u'spell_side')) + u' ⇎ 只单一拼 '
        + str(gk(u'spell_one_n')) + u' 份; 第一人称动词只在两份论文面出现（' + V4(gk(u'voice_weverb')) + u' 枚）⇎ '
        u'无人称句式 ' + V4(gk(u'voice_impersonal')) + u' 枚; 免配置三处安放: 标题 ⇎ 陈述句 ⇎ 结论句 ⇎ cake 一处不写（宣称 '
        + V4(gk(u'cfg_claim')) + u'）; 套版长行池 ' + str(gk(u'pool_union')) + u' 枚里三份 RFC 之间共用 '
        + str(gk(u'pool_pair_rfc')) + u' 枚（最大对 ' + str(gk(u'pool_max_pair')) + u' ⇎ 最小对 '
        + str(gk(u'pool_min_pair_rfc')) + u'）⇎ 凡牵进论文的每一对 ' + str(gk(u'pool_pair_paper')) + u' 枚（'
        + str(gk(u'pool_pair_paper_n')) + u' 对全冷）——论文面与规范面不共享一行套版; 共用行里带义务词的 '
        + str(gk(u'pool_shared_toned')) + u' 枚 ⇎ 带 “RFC” 字样 ' + str(gk(u'pool_shared_rfcline')) + u' 枚。'
        + u'版式与口径: ' + str(len(ROLEN)) + u' 枚判词针只有 ' + str(FACE[0]) + u' 次命中能在单行读全, 折平救 '
        + str(gk(u'gain_fold_tot')) + u' 枚 ⇎ 摘壳再救 ' + str(gk(u'gain_sh_tot')) + u' 枚 ⇎ 拆字 '
        + str(gk(u'gain_lig_tot')) + u' 枚; 被切开 ' + str(gk(u'split_n')) + u' 枚里 ' + str(gk(u'split_wrap_n'))
        + u' 枚是 72 列换行 ⇎ ' + str(gk(u'split_shell_n')) + u' 枚是页壳; SHOULD NOT 被同一根线切开 '
        + str(gk(u'tone_straddle')[4]) + u' 枚（行 ' + str(gk(u'tone_straddle_lines')[0][0]) + u' ⇎ '
        + str(gk(u'tone_straddle_lines')[0][1]) + u'）, 只在 8289。反向 ' + str(gk(u'neg_n')) + u' 枚针 '
        + str(gk(u'neg_probes')) + u' 次探针在归一面上全冷（' + str(gk(u'neg_zero_hits')) + u' 命中）, 唯子串轨假阳 '
        + str(gk(u'neg_sub_false')) + u' 枚——“' + gk(u'neg_sub_false_rows')[0][0] + u'”在 ⟦' + gk(u'neg_sub_false_rows')[0][1]
        + u'⟧ 读到 ' + str(gk(u'neg_sub_false_rows')[0][2]) + u' 枚而整词 ' + str(gk(u'neg_sub_false_rows')[0][3]) + u' 枚。'
        + u'闭合账: 布尔门 ' + str(gk(u'bool_all_sum')) + u'/' + str(gk(u'bool_all_n')) + u' ⇎ V 形恒等式 ' + str(VFORM)
        + u' 条 ⇎ 对账 ' + str(gk(u'pick_agree')) + u' 键 ' + str(gk(u'pick_diff')) + u' 不符 ⇎ 锚 ' + str(gk(u'anchor_total'))
        + u' 处 ⇎ 归属 ' + str(gk(u'checks')) + u' 次 ⇎ 错配 ' + str(gk(u'anchor_err')) + u'——五种答话在本遍换了一整套计数机制之后'
        + u'仍落回同一处。')
for _s in (PARA,):
    assert _s.count(u'|') == 0 and _s.count(u'`') % 2 == 0
# 判词段里点名的五段答句都要在它那一源的原面上读得到(不是抄来的字面)
assert PARA.count(u'⟦') == 2 * NSRC + 1 and PARA.count(u'⟨') == NSRC
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


S2 = after(S, u'**B80 问的是失败的 HTTP 请求到底能不能由程序自己重发', PARA + NL + NL)
S2 = after_row(S2, u'B80', u'（新建,', HEADROW + NL)
S2 = after_row(S2, u'B80', u'`raw/httpretry/rfc2616.txt`', C81 + NL)

L2 = S2.split(NL)
h2 = [i for i, l in enumerate(L2) if l.startswith(u'| entry | 编码字符 |')]
assert len(h2) == 1
t2 = [i for i in range(h2[0], len(L2)) if L2[i].startswith(u'| **合计（')]
assert len(t2) == 1
T0 = t2[0]
present = [l.split(u'|')[1].strip() for l in L2[h2[0] + 2:T0]]
assert present == LISTED0, present[:3]
L2[T0:T0] = [(u'| B81 | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
              % (fmt(E81), SL81[3], SL81[4], SL81[5], SL81[7]))]
HC = len(L2[h2[0]].split(u'|'))
cells = L2[T0 + 1].split(u'|')
assert len(cells) == HC, (len(cells), HC)
UN = sorted(set(c[0] for c in UNACC), key=lambda k: int(k[1:]))
cells[1] = u' **合计（' + str(len(LISTED)) + u' 条）** '
cells[2] = u' **' + fmt(enc_all) + u'** '
cells[3] = (u' **%.1f%%**（摘要段合计 ' % (100.0 * enc_all / dig_all) + fmt(dig_all)
            + u'，本遍补记的一枚为 ' + fmt(E81) + u' 编码／' + fmt(D81)
            + u' 摘要；两列合计与本表所列 ' + str(len(LISTED)) + u' 条一致，故不取 audit 的 ALL 行'
              + u'（它多含已接线而未在本表记账的 ' + u'⇎'.join(UN) + u'：编码 '
              + fmt(num(ALLR[2]) - enc_all) + u' ⇎ 摘要 ' + fmt(num(ALLR[1]) - dig_all)
              + u'，这 %d 条各自已在门槛表⇎语料表两行记账；唯一码点那格由本遍按 audit 的编码区正则逐条现数取列内并集，'
                u'逐条与 audit 现算值对拍） ' % len(UN))
cells[5] = u' **%s** ' % fmt(len(UNI))
assert len(cells) == len(L2[T0 + 1].split(u'|')), (len(cells), len(L2[T0 + 1].split(u'|')))
L2[T0 + 1] = u'|'.join(cells)
NOTE = [i for i, l in enumerate(L2) if l.startswith(u'（B54 起的 ') and u'机械行' in l]
assert len(NOTE) == 1, NOTE
L2[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与字符/语义单元五格, '
               u'不重写各条的口径注; 本遍再直补 B81 一枚, 合计行只列本表已记账条目, 唯一码点由本遍逐条现数取并集, '
               u'不再抄 ALL 行。）'
               % len([x for x in present + [u'B81'] if int(x[1:]) >= 54]))
S2 = NL.join(L2)

FIDS = sorted(set(int(re.match(r'B(\d+)_', os.path.basename(x)).group(1))
                  for x in glob.glob(u'corpus/babeltele/B*.md') if re.match(r'B\d+_', os.path.basename(x))))
assert [u'B%02d' % x for x in FIDS] == [c[0] for c in GROW], (len(FIDS), len(GROW))


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


FAILD = dict((u'B' + m.group(1), len([x for x in m.group(2).split(u',') if x.strip()]))
             for m in re.finditer(u'^  B(\\d+): 编码侧=\\[(.*?)\\]', AUD, re.M))
assert (not GATE_PASS) == bool(FAILD) and u'B81' not in FAILD, (GATE_PASS, FAILD)

S2 = subn(u'共 \\*\\*\\d+ 条\\*\\*（`babeltele/[^`]*`, 本遍补上 B\\d+ 的四处记账行[^）]*）',
          lambda m: (u'共 **%d 条**（`babeltele/%s`, 本遍补上 B81 的四处记账行, 合计按本表所列 %d 条现算, '
                     u'唯一码点逐条现数；已接线而未进本表合计行的 %s 均已记了门槛表⇎语料表两行, '
                     u'本遍不再重记其记账数（上一遍该行按 B80 现量写就, 未含本遍一枚））'
                     % (len(FIDS), runs(FIDS), len(LISTED), u'／'.join(UN))), S2)
S2 = subn(u'## 保真门槛：`python corpus/audit.py` → \\*\\*PASS\\*\\*（\\d+ 条）',
          lambda m: (u'## 保真门槛：`python corpus/audit.py` → **PASS**（%d 条）' % len(FIDS)
                     if GATE_PASS else
                     u'## 保真门槛：`python corpus/audit.py` → 本遍复跑总判 **FAIL**：失配只落在未记账的 %s'
                     u'（audit 报其 %d 枚编码侧数字锚在原文侧读不到）；本遍记账的 B81 错配 %d 枚, 本表所列 %d 条不受影响'
                     % (u'／'.join(sorted(FAILD)), sum(FAILD.values()), gk(u'anchor_err'), len(LISTED))), S2)
S2 = subn(u'当前 \\*\\*\\d+ 条语料／\\d+ 条\\*\\*推导全部通过（audit 自报“已机检的推导 \\d+ 条”，行集与文件数相符 \\d+ ⇎ \\d+）',
          lambda m: (u'当前 **%d 条语料／%d 条**推导%s（audit 自报“已机检的推导 %d 条”，行集与文件数相符 %d ⇎ %d）'
                     % (len(FIDS), PROOFS,
                        u'全部通过' if GATE_PASS else u'除 %s 外全部通过' % u'／'.join(sorted(FAILD)),
                        PROOFS, len(GROW), len(FIDS))), S2)

assert S2.count(u'python -X utf8 corpus/_fill80.py') == 1
L81 = [(u'python -X utf8 corpus/_mkB81.py',
        u'                     # 建条目(前半, 与 _mk81emit.py 同场 exec): 扁平契约 ' + str(len(FP))
        + u' 枚键⇎ DERIV ' + str(len(DER)) + u' 枚算式 ⇎ V 形 ' + str(VFORM) + u' 条; 四档面(原行⇎折平⇎摘壳⇎拆字)⇎'
        + str(len(ROLEN)) + u' 枚判词针 ⇎ ' + str(len(NUMF)) + u' 式数值 ⇎ 单位⇎术语⇎拼写⇎语气⇎宣称⇎参数⇎引用八族, '
        u'采集侧同定义标量 ' + str(gk(u'pick_agree')) + u'/' + str(gk(u'pick_agree')) + u' 枚相符'),
       (u'python -X utf8 corpus/_mkdigest3.py B81 <entry> '
        + u' '.join(u'%s %s 300 200' % (LBL[i], SRC[i]) for i in range(NSRC)),
        u'   # 五源分节摘要(' + fmt(D81) + u' 字符, ' + str(gk(u'anchor_total'))
        + u' 枚锚全命中, 五份各开一窗 300/200；本遍用同一组窗口重建后与在库文件逐字节相同)'),
       (u'python -X utf8 corpus/_wire81.py',
        u'                    # 接线: SRC/ATOM/SCAN(审计器侧两套实现)/DERIV/B81V 进 audit.py, 落盘前复跑 '
        + str(len(FP)) + u' 枚扁平键 ⇎ ' + str(len(DER)) + u' 枚算式 ⇎ ' + str(gk(u'checks')) + u' 次归属检查'),
       (u'python -X utf8 corpus/_fill81.py',
        u'                    # 第五遍(注区): 行界手索引 ⇎ `bisect` 行号尺 ⇎ n-gram 直方图 ⇎ ast 摘门右式各重导一次, '
        + str(gk(u'bool_clos_n')) + u'+' + str(gk(u'bool_clos2_n')) + u' 道布尔门 ⇎ ' + str(VFORM)
        + u' 条 V 形现算归零后写回 ⛓解读注（15 行复测表 ⇎ 复算 ' + str(len(FP)) + u' 键对账 '
        + str(gk(u'pick_diff')) + u' 不符 ⇎ 独有 ' + str(len(gk(u'pick_diff_keys'))) + u' 枚）')]
CUR = u'python -X utf8 corpus/_fill80.py'
for head, tail in L81:
    S2 = after(S2, CUR, head + tail + NL)
    CUR = head

T3 = u'corpus/README.md.tmp81'
io.open(T3, u'w', encoding=u'utf-8', newline=NL).write(S2)
os.replace(T3, u'corpus/README.md')
json.dump(dict(listed=LISTED, listed_n=len(LISTED), enc=enc_all, dig=dig_all, uniq=len(UNI),
               proofs=PROOFS, b81_enc=E81, b81_dig=D81, unaccounted=UN, audit_rows=len(GROW),
               entries_files=len(FIDS), gate_pass=GATE_PASS, gate_failed=FAILD,
               bytes=BS, chars=CH_, lines=LN, newlines=NLC, splitlines=SPL, tail_nl=TAIL, ff_end=FFEND,
               nonblank=NB, blank=BLK, maxlen=ML, over72=O72, ff=FFC, ff_only=EFO, ff_inline=FIL,
               ff_lead=NFL, shell_lines=SL, shell_nonblank=SLNB, pp_rows=PPR, pg_lines=PGR, hdr_lines=HDR,
               pgnum_naive=PGN, pgnum_ffled=PGF, pgnum_multirun=PGM, cr=CR, nonascii=NA, bom=BOM,
               lig_pair=LIGC, face_tot=FACE, gain_fold=gk(u'gain_fold_tot'), gain_sh=gk(u'gain_sh_tot'),
               gain_lig=gk(u'gain_lig_tot'), unit_sub_over=gk(u'unit_sub_over'), num_tot=gk(u'num_tot'),
               term_skew=gk(u'term_skew'), pool_pair_rfc=gk(u'pool_pair_rfc'), keys=len(FP), deriv=len(DER),
               vform=VFORM, close_keys=CLOSEK, dkeys=DKEYS, bool_gates=gk(u'bool_all_n'),
               anchors=gk(u'anchor_total'), anchor_face=(CLS1, CLSN, CLS5), anchor_ref=REF1,
               anchor_cross_unref=CROSS_UNREF, checks=gk(u'checks'), all5_needle=ALL5),
          io.open(u'corpus/_b81readme.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（%d 条）编码 %s ⇎ 摘要 %s ⇎ 保留 %.1f%% ｜ 唯一码点(列内并集) %s ｜ 未记账 %s ｜ '
      u'audit 行 %d ⇎ 文件 %d ｜ 推导 %d 条 ｜ 本遍总判 %s%s ｜ B81 行 %s 编码／%s 摘要 ｜ 锚 %d 处⇎归属检查 %d 次⇎错配 %d ｜ '
      u'四档命中 %s ⇎ 切开 %d 枚 ⇎ 反向 %d 枚×%d 探针'
      % (len(LISTED), fmt(enc_all), fmt(dig_all), 100.0 * enc_all / dig_all, fmt(len(UNI)),
         u'⇎'.join(UN), len(GROW), len(FIDS), PROOFS, u'PASS' if GATE_PASS else u'FAIL',
         u'' if GATE_PASS else u'（只落在 %s）' % u'⇎'.join(sorted(FAILD)),
         fmt(E81), fmt(D81), gk(u'anchor_total'), gk(u'checks'), gk(u'anchor_err'),
         V4(FACE), gk(u'split_n'), gk(u'neg_n'), gk(u'neg_probes')))
