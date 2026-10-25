# -*- coding: utf-8 -*-
"""README 记账(B86): 判词段 ⇎ 门槛表行 ⇎ 语料表行 ⇎ 转化指标机械行 ⇎ 合计行 ⇎ 命令块 ⇎ 条数陈述。

本遍是真跑 `corpus/audit.py` 后按当下输出记账, 能现量的数一律用本遍自己的量尺现量, 再与扁平契约逐键对拍;
凡只有快照可取的读数, 文中一律标“契约值”。本遍换机制而不换定义之处:
① 版式走字节平面: 字节由 `os.stat` ⇎ 逐字节读入两把尺, 码位在 `decode('utf-8','replace')` 后 `len()`,
   行界只认 `\\n`(行尾 CR 逐行摘掉), 换页/回车/制表/BOM 由逐字节计数, 非 ASCII 由逐码位 `ord()>127` 现数;
② 壳尺走整行序列正则(`^\\s*\\[Page \\d+\\]` ⇎ `^RFC1122 +\\S` ⇎ `September 1981` …), 建条目与第五遍是
   `strip()` 后逐 token 形状判——同一谓词的第三套实现, 七路各自命中数之和减去重复命中才等于壳行(真容斥);
③ 判词针四档: 折平尺用 `' '.join(s.lower().split())`, 行档逐行现折再 `in`, 出现枚数走 `re.findall(re.escape(针))`
   (第五遍是 `str.count` ⇎ 采集侧是游标 find 环), 去编号档由 token 扫描器手工摘括号(第五遍也是 token 尺但逐形状分档);
④ 义务词整词尺: 逐命中读左右邻并查 `isalpha()`(第五遍先建三张布尔表再查表);
⑤ 锚不用正则配对: 按 `⟦` 分段手吃 `⟨…⟩`, 只吃 `## ⟪BabelTele⟫` 与 `## ⛓解读注` 之间那一节,
   归属逐枚在本遍自折的面上现验, 五源同现 ⇎ 穿二三源 ⇎ 独占三档由本遍现判;
⑥ DERIV 237 式在本遍就地重算: 先从 `corpus/audit.py` 内嵌的 `DERIV['B86']` 字面量反向 literal_eval 回字典与
   `_deriv86.json` 对拍(两把读取器), 再验每枚 `B86V` 引用的键确在契约里, 最后逐式对常量;
⑦ 唯一码点不抄 audit 的 ALL 行: 逐条现数并与 audit 的编码列对拍, 再取本表所列条目的并集;
⑧ 本库现有 90 份条目文件 ⇎ audit 90 行, 而转化指标表在库只 84 行——本遍补 B86 一枚后为 85 行,
   另 5 条(B87–B91)已接线未进本表, 其记账不归本遍; 合计行因此按本表所列 85 行现算, 并在行文里点名与
   audit ALL 行的差额来自那 5 条, 而不是把两把尺混成一格。
"""
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
NL = u'\n'
NSRC = 5
LBL = [u'793', u'1122', u'9293', u'6298', u'lin']
SRC = [C + u'/raw/tcpRetr/rfc793.txt', C + u'/raw/tcpRetr/rfc1122.txt',
       C + u'/raw/tcpRetr/rfc9293.txt', C + u'/raw/tcpRetr/rfc6298.txt',
       C + u'/raw/tcpRetr/ip-sysctl.txt']
SHW = [u'`' + p[len(C) + 1:] + u'`' for p in SRC]
YR = [1981, 1989, 2022, 2011, 0]
ANS = [u'翻倍重传到超时即止: 只给“不超五分钟”的默认上限', u'立 R1 ⇎ R2 两阈值',
       u'照登 1122 并给义务词编号, 又许 R2 为无穷', u'不谈次数: 只钉 RTO 下限 60 秒',
       u'交给内核参数与等式']
ENTRY = glob.glob(u'corpus/babeltele/B86_*.md')[0]
FP = json.load(io.open(u'corpus/_b86flat.json', encoding=u'utf-8'))
DER = json.load(io.open(u'corpus/_deriv86.json', encoding=u'utf-8'))
CH = json.load(io.open(u'corpus/_b86checks.json', encoding=u'utf-8'))
MK = io.open(u'corpus/_mkB86.py', encoding=u'utf-8').read()


def g(k):
    assert k in FP, k
    return FP[k]


def fmt(n):
    s = u'%d' % n if isinstance(n, int) else u'%g' % n
    if u'.' in s:
        a, b = s.split(u'.', 1)
        return fmt(int(a)) + u'.' + b
    if not s.isdigit() or len(s) <= 3:
        return s
    gr = [s[x:x + 3] for x in range(len(s) - 3, -1, -3)][::-1]
    if len(s) % 3:
        gr = [s[:len(s) % 3]] + gr
    return u' '.join(gr)


def num(x):
    return int(u''.join(c for c in x if c.isdigit()))


def J(xs):
    return u' ⇎ '.join(u'%s' % x for x in xs)


def pnorm(s):
    return u' '.join(s.lower().split())


# ---------- ⓪ 真跑 audit(输出缓存只在 audit ⇎ 建条 ⇎ 发射 ⇎ 接线 ⇎ 条目比它新时才作废) ----------
CACHE = u'corpus/_readme86_audit.txt'
DEPS = [u'corpus/audit.py', u'corpus/_mkB86.py', u'corpus/_mk86emit.py', u'corpus/_wire86.py',
        u'corpus/_fill86.py', ENTRY]
_fresh = os.path.exists(CACHE) and os.path.getmtime(CACHE) >= max([os.path.getmtime(p) for p in DEPS])
if _fresh:
    AUD = io.open(CACHE, encoding=u'utf-8').read()
else:
    AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                         text=True, encoding=u'utf-8').stdout
    io.open(CACHE, u'w', encoding=u'utf-8', newline=NL).write(AUD)
VERD = [l for l in AUD.split(NL) if l.startswith(u'保真门槛(T1 字面 + T2 推导 + T3 码位):')]
assert len(VERD) == 1, VERD
GATE_PASS = VERD[0].endswith(u'PASS')
FAILED = [l.split(u':')[0].strip() for l in AUD.split(NL) if re.match(u'^  B\\d+: ', l)]
assert u'B86' not in FAILED, FAILED
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])
GROW, ALLR = [], None
for l in AUD.split(NL):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        GROW.append([x.strip() for x in l.split(u'|')[1:-1]])
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR and len(GROW) == 90, len(GROW)
ROWS = dict((c[0], c) for c in GROW)
FILES = glob.glob(u'corpus/babeltele/B*_*.md')
assert len(ROWS) == len(FILES), (len(ROWS), len(FILES))
R86 = ROWS[u'B86']
assert num(R86[2]) == g(u'enc_chars'), (R86[2], g(u'enc_chars'))

# ---------- ① 版式: 字节平面 ----------
B = [io.open(p, 'rb').read() for p in SRC]
T = [x.decode('utf-8', 'replace') for x in B]
STAT = [os.stat(p).st_size for p in SRC]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in t.split(NL)] for t in T]
BY = [len(x) for x in B]
CP = [len(x) for x in T]
LN = [len(x) for x in L]
NB = [len([y for y in L[i] if y.strip() != u'']) for i in range(NSRC)]
MX = [max([len(y) for y in L[i]]) for i in range(NSRC)]
FF = [x.count(u'\x0c') for x in T]
CR = [x.count(u'\r') for x in T]
TB = [x.count(u'\t') for x in T]
BOM = [x.count(u'\ufeff') for x in T]
NA = [len([c for c in x if ord(c) > 127]) for x in T]
NA_LN = [len([y for y in L[i] if any(ord(c) > 127 for c in y)]) for i in range(NSRC)]
UTX = [BY[i] - CP[i] for i in range(NSRC)]
BL = [LN[i] - NB[i] for i in range(NSRC)]
FF_ALONE = [len([y for y in L[i] if y == u'\x0c']) for i in range(NSRC)]
FF_LEAD = [len([y for y in L[i] if y[:1] == u'\x0c']) for i in range(NSRC)]
FF_NL = [T[i].count(u'\x0c' + NL) for i in range(NSRC)]
BOM_HEAD = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
LF = [T[i].count(NL) for i in range(NSRC)]
TNL = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
RL = [LN[i] - TNL[i] for i in range(NSRC)]
assert LF == g(u'n_lf') and RL == g(u'readlines')
assert [RL[i] + TNL[i] - LN[i] for i in range(NSRC)] == g(u'lf_vs_readlines') == [0] * NSRC
for kk, mine in [(u'bytes', BY), (u'cp', CP), (u'splitnl', LN), (u'nonblank', NB),
                 (u'blank', BL), (u'maxlen', MX), (u'ff', FF), (u'n_cr', CR), (u'tab', TB)]:
    assert mine == g(kk), (kk, mine, g(kk))
assert BY == STAT == g(u'bytes_stat')
NADIST = [len(set([ord(c) for c in x if ord(c) > 127])) for x in T]
assert NA == g(u'na_total') and NA_LN == g(u'na_lines'), (NA, NA_LN)
assert NADIST == [len(v) for v in g(u'na_codepoints')], (NADIST, g(u'na_codepoints'))
assert UTX == g(u'utf8_extra') and [BY[i] - CP[i] - UTX[i] for i in range(NSRC)] == g(u'byte_cp_ledger')
# 换页三尺(枚数 ⇎ 独占整行 ⇎ 行首 ⇎ 紧邻换行)在本遍各数一遍, 再与契约的四把尺同栏对拍
assert FF == FF_ALONE == FF_LEAD == FF_NL == g(u'ff_led') == g(u'ff_alone') == g(u'ff_before_nl')
assert BOM == BOM_HEAD == g(u'bom'), (BOM, BOM_HEAD)
# 行账恒等式按本遍读数归零: 非空 + 空 = 总行, 且 splitlines = 换行枚数 − 尾换行 + 换页枚数
assert [NB[i] + BL[i] - LN[i] for i in range(NSRC)] == g(u'line_split_ledger') == [0] * NSRC
SPL = [len(T[i].splitlines()) for i in range(NSRC)]
assert SPL == g(u'splitlines')
assert [SPL[i] - FF[i] - (LN[i] - TNL[i]) for i in range(NSRC)] == g(u'splitlines_ledger')

# ---------- ② 壳账: 整行序列正则(第三套实现) ----------
RULES = [
    (u'空行', lambda x: x.strip() == u''),
    (u'独占行换页', lambda x: x == u'\x0c'),
    (u'页脚', lambda x: re.match(u'^\\s*.*\\[Page +\\d+\\]\\s*$', x) is not None),
    (u'793 眉', lambda x: re.match(u'^\\s*(September 1981|Transmission Control Protocol)\\s*$', x) is not None),
    (u'1122 眉', lambda x: re.match(u'^RFC1122 +\\S', x) is not None),
    (u'IETF 独立行', lambda x: re.match(u'^Internet Engineering Task Force\\s*$', x) is not None),
    (u'新式眉', lambda x: ((re.match(u'^\\s*(Internet Engineering Task Force|Internet-Draft)', x) is not None)
                           or (re.search(u'RFC ?\\d{4}[^A-Za-z0-9]+.*((19|20)\\d\\d)\\s*$', x) is not None))),
]
HITS = [[[1 if f(y) else 0 for y in L[i]] for _, f in RULES] for i in range(NSRC)]
SHL = [sum(1 for y in L[i] if any(f(y) for _, f in RULES)) for i in range(NSRC)]
SUM7 = [sum(sum(col) for col in HITS[i]) for i in range(NSRC)]
OVL7 = [SUM7[i] - SHL[i] for i in range(NSRC)]
assert SHL == g(u'shell_lines') == g(u'shell_shape') == g(u'shell_pick'), SHL
assert OVL7 == g(u'shape_ovl'), (OVL7, g(u'shape_ovl'))
assert SUM7 == g(u'shape_sum'), (SUM7, g(u'shape_sum'))
assert [SHL[i] - (SUM7[i] - OVL7[i]) for i in range(NSRC)] == g(u'shell_ledger') == [0] * NSRC
BODY = [LN[i] - SHL[i] for i in range(NSRC)]
assert BODY == g(u'body_lines') and [BODY[i] + SHL[i] - LN[i] for i in range(NSRC)] == g(u'body_shell_ledger')
# 七路各自的命中数与建条目侧的 token 尺逐路同值(第三套实现只换谓词写法, 不改判据)
RULEKEY = [u'blank', u'ff_alone', u'foot', u'hdr793', u'hdr1122', u'ietf_alone', u'hdrnew']
RHITS = [[sum(col) for col in HITS[i]] for i in range(NSRC)]
for r in range(len(RULES)):
    mine = [RHITS[i][r] for i in range(NSRC)]
    assert mine == g(RULEKEY[r]), (RULES[r][0], RULEKEY[r], mine, g(RULEKEY[r]))
assert [g(u'blank')[i] + g(u'hdr793')[i] + g(u'hdr1122')[i] + g(u'hdrnew')[i] + g(u'foot')[i]
       + g(u'ietf_alone')[i] + g(u'ff_alone')[i] for i in range(NSRC)] == SUM7
# ---------- ②b 抬头年: 本遍在面上现扫, 不复用任何快照 ----------
MONS = (u'January|February|March|April|May|June|July|August|September|October|November|December')
HDRYR = []
for i in range(NSRC):
    m = re.search(u'(?:' + MONS + u') +((?:19|20)\\d\\d)', T[i][:6000])
    HDRYR.append(int(m.group(1)) if m else 0)
assert HDRYR == YR, (HDRYR, YR)
print(u'① 版式 OK: 字节 %s ⇎ 行 %s ⇎ 非空 %s ⇎ 壳 %s(七路和 %s − 重复 %s)⇎ 换页 %s' %
      (J(BY), J(LN), J(NB), J(SHL), J(SUM7), J(OVL7), J(FF)))
print(u'②b 抬头年 OK: %s(第五份为内核文档, 面上无抬头年)' % J(HDRYR))


# ---------- ③ 判词针四档: 针集由 ast 从建条目脚本现取, 枚数走切分尺 ----------
OB7 = [u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'SHLD', u'ED']
OB5 = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']
OBL5 = [w.lower() for w in OB5]
OB_CHARS = set(u'MSASE')

def fc6(s):
    """折平保形的第三套实现: 逐字符扫, 空白串聚成一枚空格, 首尾空白抹掉(建条目侧 re.split ⇎ 第五遍 split())。"""
    out, i, n = [], 0, len(s)
    while i < n:
        if s[i].isspace():
            while i < n and s[i].isspace():
                i += 1
            out.append(u' ')
        else:
            out.append(s[i])
            i += 1
    return u''.join(out).strip()


def pl6(s):
    return fc6(s).lower()


def oc6(hay, nd):
    """出现枚数: 按针切分后段数减一(建条目侧 findall ⇎ 第五遍 str.count ⇎ 采集侧游标环)。"""
    return len(hay.split(nd)) - 1


ND = None
for _nd in ast.walk(ast.parse(MK)):
    if isinstance(_nd, ast.Assign) and [getattr(t, u'id', u'') for t in _nd.targets] == [u'NEEDLES']:
        ND = ast.literal_eval(_nd.value)
assert ND and len(ND) == g(u'needle_n') == 28, (ND and len(ND), g(u'needle_n'))
NK6 = [pl6(z) for z in ND]
assert [pl6(z) == pnorm(z) for z in ND] == [True] * len(ND)
SHELL6 = [[any(f(y) for _, f in RULES) for y in L[i]] for i in range(NSRC)]
NSH = [NL.join([L[i][j] for j in range(len(L[i])) if not SHELL6[i][j]]) for i in range(NSRC)]
FOL6 = [pl6(T[i]) for i in range(NSRC)]
SHP6 = [pl6(NSH[i]) for i in range(NSRC)]
FOLDX6 = [fc6(T[i]) for i in range(NSRC)]
SHPX6 = [fc6(NSH[i]) for i in range(NSRC)]
assert [FOL6[i] == pnorm(T[i]) for i in range(NSRC)] == [True] * NSRC


def detag6(s, tally=None, kinds=None):
    """去编号的第三套实现: 逐位置试括号形(不区分大小写)与裸形(只认大写), 命中即跳过(建条目侧两条正则相继 sub)。
    tally 若给则按被摘掉的词形计数; kinds 若给则按括号形/裸形分档记枚数与吃掉字符, 供“摘掉的编号 ⇎ 义务词掉档 ⇎ 面差”三处对账。"""
    out, i, n = [], 0, len(s)
    while i < n:
        sp = None
        if s[i] == u'(':
            for w in OB7:
                seg = s[i + 1:i + 1 + len(w)]
                if seg.upper() != w or s[i + 1 + len(w):i + 2 + len(w)] != u'-':
                    continue
                k = i + 2 + len(w)
                d = k
                while d < n and s[d].isdigit():
                    d += 1
                if d > k and s[d:d + 1] == u')' and out and out[-1] == u' ':
                    out.pop()
                    sp = d + 1
                    if tally is not None:
                        tally[w] = tally.get(w, 0) + 1
                    if kinds is not None:
                        kinds[u'paren_n'] += 1
                        kinds[u'paren_c'] += sp - (i - 1)
                    break
        if sp is None and s[i:i + 1] in OB_CHARS:
            for w in OB7:
                if s[i:i + len(w)] != w or s[i + len(w):i + len(w) + 1] != u'-':
                    continue
                k = i + len(w) + 1
                d = k
                while d < n and s[d].isdigit():
                    d += 1
                if d == k:
                    continue
                a = i - 1
                if a >= 0 and (s[a].isalnum() or s[a] == u'_'):
                    continue
                if d < n and (s[d].isalnum() or s[d] == u'_'):
                    continue
                sp = d
                if tally is not None:
                    tally[w] = tally.get(w, 0) + 1
                if kinds is not None:
                    kinds[u'bare_n'] += 1
                    kinds[u'bare_c'] += d - i
                break
        if sp is not None:
            i = sp
            continue
        out.append(s[i])
        i += 1
    return u''.join(out)


def _kinds():
    return {u'paren_n': 0, u'bare_n': 0, u'paren_c': 0, u'bare_c': 0}


SHTAG6 = [detag6(SHP6[i]) for i in range(NSRC)]
TALLY = [{} for _ in range(NSRC)]
KX = [_kinds() for _ in range(NSRC)]
SHTAGX6 = [detag6(SHPX6[i], TALLY[i], KX[i]) for i in range(NSRC)]
KL = [_kinds() for _ in range(NSRC)]
KT = [_kinds() for _ in range(NSRC)]
for i in range(NSRC):      # 同一把尺在折平保形面 ⇎ 全面上再各走一遍, 只为分档计枚
    detag6(SHP6[i], None, KL[i])
    detag6(T[i], None, KT[i])
R_LINE = [[len([1 for y in L[i] if NK6[k] in pl6(y)]) for i in range(NSRC)] for k in range(len(NK6))]
R_FOLD = [[oc6(FOL6[i], NK6[k]) for i in range(NSRC)] for k in range(len(NK6))]
R_SH = [[oc6(SHP6[i], NK6[k]) for i in range(NSRC)] for k in range(len(NK6))]
R_TAG = [[oc6(SHTAG6[i], NK6[k]) for i in range(NSRC)] for k in range(len(NK6))]
for _nm, mine, key in [(u'行', R_LINE, u'role_line'), (u'折', R_FOLD, u'role_fold'),
                       (u'摘壳', R_SH, u'role_sh'), (u'去编号', R_TAG, u'role_tag')]:
    assert mine == g(key), (_nm, [(k, mine[k], g(key)[k]) for k in range(len(NK6)) if mine[k] != g(key)[k]][:3])
LN4 = [sum(R_LINE[k][i] for k in range(len(NK6))) for i in range(NSRC)]
FN4 = [sum(R_FOLD[k][i] for k in range(len(NK6))) for i in range(NSRC)]
SN4 = [sum(R_SH[k][i] for k in range(len(NK6))) for i in range(NSRC)]
TN4 = [sum(R_TAG[k][i] for k in range(len(NK6))) for i in range(NSRC)]
assert [LN4, FN4, SN4, TN4] == [g(u'role_line_n'), g(u'role_fold_n'), g(u'role_sh_n'), g(u'role_tag_n')]
GAIN6 = [[FN4[i] - LN4[i], SN4[i] - FN4[i], TN4[i] - SN4[i]] for i in range(NSRC)]
assert GAIN6 == g(u'role_gain'), (GAIN6, g(u'role_gain'))
WRAP6 = [k for k in range(len(NK6)) if R_SH[k] != [0] * NSRC
         and any(R_LINE[k][i] < R_SH[k][i] for i in range(NSRC))]
SHELLC6 = [k for k in range(len(NK6)) if k not in WRAP6
           and any(R_FOLD[k][i] > R_SH[k][i] for i in range(NSRC))]
TAGC6 = [k for k in range(len(NK6)) if any(R_TAG[k][i] != R_SH[k][i] for i in range(NSRC))]
assert [WRAP6, SHELLC6, TAGC6] == [g(u'wrap_cut'), g(u'shell_cut'), g(u'tag_cut')]
WG6 = [sum(R_FOLD[k][i] - R_LINE[k][i] for k in range(len(NK6))) for i in range(NSRC)]
assert WG6 == g(u'wrap_gain') and sum(WG6) == g(u'wrap_gain_tot') == sum(g(u'wrap_gain_cells'))
TG6 = sum(R_TAG[k][i] - R_SH[k][i] for k in range(len(NK6)) for i in range(NSRC))
assert TG6 == g(u'tag_gain_tot') and len(NK6) * NSRC == g(u'role_probes')
MOVE6 = [[k, LBL[i], R_SH[k][i], R_TAG[k][i]] for k in range(len(NK6)) for i in range(NSRC)
         if R_SH[k][i] != R_TAG[k][i]]
assert MOVE6 == g(u'tag_move'), (MOVE6, g(u'tag_move'))
print(u'③ 判词针 OK: %d 枚×五份=%d 格 四档合计 %s ⇎ %s ⇎ %s ⇎ %s ⇎ 切开 换行%d/壳%d/编号%d ⇎ 涨量 %s=%d' %
      (len(NK6), g(u'role_probes'), J(LN4), J(FN4), J(SN4), J(TN4), len(WRAP6), len(SHELLC6), len(TAGC6),
       J(WG6), sum(WG6)))


# ---------- ④ 义务词四档 ⇎ 编号族: 整词尺换成字母段扫描 ----------
def aruns(s):
    """极大字母段(带下标): 整词判据由“左右邻是否字母”换成“落在哪一段里”。"""
    out, i, n = [], 0, len(s)
    while i < n:
        if s[i].isalpha():
            j = i
            while j < n and s[j].isalpha():
                j += 1
            out.append((s[i:j], i, j))
            i = j
        else:
            i += 1
    return out


def ob6(s, w):
    r = aruns(s)
    wt = w.split(u' ')
    if len(wt) == 1:
        return len([1 for x in r if x[0] == w])
    return len([1 for k in range(len(r) - len(wt) + 1)
                if tuple([r[k + t][0] for t in range(len(wt))]) == tuple(wt)
                and all(s[r[k + t][2]:r[k + t + 1][1]] == u' ' for t in range(len(wt) - 1))])


OB_MINE = {}
for _nm, key, faces in [(u'行', u'ob_line', None), (u'折', u'ob_fold', FOLDX6),
                        (u'摘壳', u'ob_sh', SHPX6), (u'去编号', u'ob_tag', SHTAGX6)]:
    mine = [[sum([ob6(y, w) for y in L[i]]) for w in OB5] for i in range(NSRC)] if faces is None else \
           [[ob6(faces[i], w) for w in OB5] for i in range(NSRC)]
    assert mine == g(key), (_nm, [(i, mine[i], g(key)[i]) for i in range(NSRC) if mine[i] != g(key)[i]])
    OB_MINE[_nm] = mine
OBLOW = [[ob6(FOLDX6[i], w) for w in OBL5] for i in range(NSRC)]
assert OBLOW == g(u'ob_lower'), [(i, OBLOW[i], g(u'ob_lower')[i]) for i in range(NSRC)
                                 if OBLOW[i] != g(u'ob_lower')[i]]
OBU_SH = [sum(v) for v in OB_MINE[u'摘壳']]
assert OBU_SH == g(u'ob_upper_tot')
assert [sum(v) for v in OBLOW] == g(u'ob_lower_tot')
assert [sum(v) for v in OB_MINE[u'折']] == g(u'ob_fold_tot')
assert [sum(v) for v in OB_MINE[u'去编号']] == g(u'ob_tag_tot')
assert [sum(v) for v in OB_MINE[u'行']] == g(u'ob_line_tot')
assert [OB_MINE[u'折'][i][k] - OB_MINE[u'行'][i][k] for i in range(NSRC) for k in range(5)] == g(u'ob_wrap')
assert g(u'ob_ruler_diff') == 0 and g(u'ob_nest_ledger') == [0] * NSRC


def tagdash6(s):
    c, i, n = 0, 0, len(s)
    while i < n:
        hit = None
        for w in OB7:
            if s[i:i + len(w)] != w or s[i + len(w):i + len(w) + 1] != u'-':
                continue
            k = i + len(w) + 1
            d = k
            while d < n and s[d].isdigit():
                d += 1
            if d == k:
                continue
            a = i - 1
            if a >= 0 and (s[a].isalnum() or s[a] == u'_'):
                continue
            if d < n and (s[d].isalnum() or s[d] == u'_'):
                continue
            hit = d
            break
        i = (hit if hit is not None else i + 1)
        c += 1 if hit is not None else 0
    return c


TD6 = [tagdash6(T[i]) for i in range(NSRC)]
assert TD6 == g(u'tag_dash'), (TD6, g(u'tag_dash'))
assert [len(SHP6[i]) - len(SHTAG6[i]) for i in range(NSRC)] == g(u'tag_chars'), \
    [len(SHP6[i]) - len(SHTAG6[i]) for i in range(NSRC)]
assert [tagdash6(FOLDX6[i]) for i in range(NSRC)] == g(u'tag_dash_fold')
# 本遍这把尺认七种词形(含带 NOT 的两词形), 建条目侧的 tag_dash 只认五种: 两把尺之差恰是两词形那批
TW6 = [len(re.findall(u'\\b(?:MUST NOT|SHOULD NOT)-[0-9]+\\b', T[i])) for i in range(NSRC)]
assert [KT[i][u'paren_n'] + KT[i][u'bare_n'] for i in range(NSRC)] == \
    [TD6[i] + TW6[i] for i in range(NSRC)], ([KT[i] for i in range(NSRC)], TD6, TW6)
assert [sum(g(u'tag_kind')[i]) for i in range(NSRC)] == TD6
# 折平保形面比折平小写面多摘掉的字符, 恰是只在大写面上才等得到裸形的那批(小写面一枚裸形也不摘)
assert [KL[i][u'bare_n'] for i in range(NSRC)] == [0] * NSRC
assert [len(SHPX6[i]) - len(SHTAGX6[i]) - (len(SHP6[i]) - len(SHTAG6[i])) for i in range(NSRC)] == \
    [KX[i][u'bare_c'] for i in range(NSRC)], ([KX[i] for i in range(NSRC)])
assert [KX[i][u'paren_c'] + KX[i][u'bare_c'] for i in range(NSRC)] == \
    [len(SHPX6[i]) - len(SHTAGX6[i]) for i in range(NSRC)]
# 摘掉的编号逐词形对上义务词的掉档: 一词形摘掉一次, 它自己及其前缀词形各掉一档
for i in range(NSRC):
    for k in range(5):
        w = OB5[k]
        drop = OB_MINE[u'摘壳'][i][k] - OB_MINE[u'去编号'][i][k]
        gone = sum(TALLY[i].get(v, 0) for v in ([w] + [x for x in OB7 if x.startswith(w + u' ')]))
        assert drop == gone, (LBL[i], w, drop, gone, TALLY[i])
    _t5 = sum([TALLY[i].get(w, 0) for w in OB5])
    assert sum([OB_MINE[u'摘壳'][i][k] - OB_MINE[u'去编号'][i][k] for k in range(5)]) == \
        _t5 + TALLY[i].get(u'MUST NOT', 0) + TALLY[i].get(u'SHOULD NOT', 0), (LBL[i], TALLY[i])
print(u'④ 义务词 OK: 大写合计 %s ⇎ 小写 %s ⇎ 编号(五形尺) %s ⇎ 两词形另 %s 枚 ⇎ 编号吃掉字符 %s ⇎ 摘掉编号逐份 %s' %
      (J(OBU_SH), J([sum(v) for v in OBLOW]), J(TD6), J(TW6), J(g(u'tag_chars')),
       J([sum(TALLY[i].values()) for i in range(NSRC)])))


# ---------- ⑤ 锚: ⟦ 分段手吃 ⟨…⟩, 归属在本遍自折的面上现验 ----------
EMD = io.open(ENTRY, encoding=u'utf-8').read()
PA = EMD.index(u'## ⟪BabelTele⟫')
PB = EMD.index(u'## ⛓解读注')
assert PA < PB
ENC = EMD[EMD.index(NL, PA) + 1:PB].rstrip(NL)
ENC6 = len([c for c in ENC if c != NL])
assert ENC6 == g(u'enc_chars') == CH[u'enc_chars'] == num(R86[2]), (ENC6, R86[2])
TAGS = [u'793', u'1122', u'9293', u'6298', u'lin']
TIDX = dict((t, n) for n, t in enumerate(TAGS))
CIT6 = []
for _seg in ENC.split(u'⟦')[1:]:
    _e = _seg.index(u'⟧')
    _tag, _rest = _seg[:_e], _seg[_e + 1:]
    assert _tag in TIDX, _tag
    _k = 0
    while True:
        _j = _rest.find(u'⟨', _k)
        if _j < 0:
            break
        _m = _rest.find(u'⟩', _j)
        assert _m > _j and u'⟨' not in _rest[_j + 1:_m], _rest[_j:_j + 40]
        CIT6.append((_tag, _rest[_j + 1:_m]))
        _k = _m + 1
USED6 = len([c for c in ENC if c == u'⟨'])
assert len(CIT6) == USED6 == g(u'anchor_total'), (len(CIT6), USED6)
STR6 = sorted(set([x[1] for x in CIT6]))
assert len(STR6) == g(u'anchor_distinct')
ATOMS = io.open(u'corpus/_atoms86.txt', encoding=u'utf-8').read().split(NL)
ATOMS = ATOMS[:-1] if ATOMS and ATOMS[-1] == u'' else ATOMS
assert set(ATOMS) == set(STR6) and len(ATOMS) == len(STR6), (len(ATOMS), len(STR6))
ERR6 = [x for x in CIT6 if pl6(x[1]) not in FOL6[TIDX[x[0]]]]
ATOMSET = set(ATOMS)
ROWSN6 = [set([pl6(y) for y in L[i]]) for i in range(NSRC)]
MISS6 = [x for x in CIT6 if x[1] not in ATOMSET and pl6(x[1]) not in ROWSN6[TIDX[x[0]]]]
assert len(ERR6) == g(u'anchor_err') and not ERR6, ERR6[:3]
assert not MISS6, MISS6[:3]
LITLINE = [x for x in CIT6 if x[1] not in set(L[TIDX[x[0]]])]
HITC6 = dict((a, tuple(i for i in range(NSRC) if pl6(a) in FOL6[i])) for a in STR6)
S1 = len([a for a in STR6 if len(HITC6[a]) == 1])
S2 = len([a for a in STR6 if 1 < len(HITC6[a]) < NSRC])
S5 = len([a for a in STR6 if len(HITC6[a]) == NSRC])
assert [S1, S2, S5] == [g(u'anchor_single'), g(u'anchor_cross'), g(u'anchor_all5')]
assert S1 + S2 + S5 == len(STR6) and len(STR6) * NSRC == CH[u'checks']
TAGN6 = dict((t, len([1 for x in CIT6 if x[0] == t])) for t in TAGS)
assert [TAGN6[t] for t in TAGS] == [CH[u'tag_' + t] for t in TAGS], (TAGN6, CH)
LIN6D = len([c for a in STR6 for c in a if (u'a' <= c <= u'z') or (u'A' <= c <= u'Z')])
LIT6 = LOUT6 = 0
_k = 0
while _k < len(ENC):
    _j = ENC.find(u'⟨', _k)
    _span = ENC[_k:] if _j < 0 else ENC[_k:_j]
    LOUT6 += len([c for c in _span if (u'a' <= c <= u'z') or (u'A' <= c <= u'Z')])
    if _j < 0:
        break
    _m = ENC.find(u'⟩', _j)
    LIT6 += len([c for c in ENC[_j + 1:_m] if (u'a' <= c <= u'z') or (u'A' <= c <= u'Z')])
    _k = _m + 1
# 发射侧那把尺数的是“去重后的锚串”里的字母, 逐处出现的字母另存一格, 两格不混作同一档
assert [LIN6D, LOUT6] == [CH[u'letters_in'], CH[u'letters_out']], (LIN6D, LOUT6, CH[u'letters_in'])
assert LIT6 >= LIN6D
print(u'⑤ 锚 OK: %d 处 ⇎ 去重 %d 串 ⇎ 归属落空 %d ⇎ 分档 独占%d/跨界%d/全份%d ⇎ 复核 %d 格 ⇎ 编码区 %d 字符 ⇎ 锚内字母 去重%d⇎逐处%d ⇎ 锚外字母 %d ⇎ 与整行原文逐字相同的锚 %d 枚(余 %d 枚要经折面才对齐, 建条目侧另有跨行档 %d 枚)' %
      (USED6, len(STR6), len(ERR6), S1, S2, S5, len(STR6) * NSRC, ENC6, LIN6D, LIT6, LOUT6,
       USED6 - len(LITLINE), len(LITLINE), len([r for r in CH[u'anchor_lines'] if r[3] > 1])))


# ---------- ⑥ DERIV: 键名即所推字面, 引用先验键在契约, 再逐式对值(换文本代入, 不建查表通道) ----------
VRE = re.compile(u"B86V\\('([^']+)'(?:,\\s*(-?\\d+))?\\)")
DCITE6, DFL6 = 0, []


def _sub(m):
    global DCITE6
    DCITE6 += 1
    k = m.group(1)
    assert k in FP, k
    v = FP[k]
    if m.group(2) is None:
        return repr(v)
    return repr(v[int(m.group(2))] if isinstance(v, list) else v)


# audit.py 里那段 DERIV['B86'] 由 _wire86.py 用 repr(json) 原样嵌入: 本遍从门内反向 literal_eval 出来与 json 对拍
ASRC = io.open(u'corpus/audit.py', encoding=u'utf-8').read()
DBEG = ASRC.index(u"DERIV['B86'] = ")
DEND = ASRC.index(NL, DBEG)
DER_MD = ast.literal_eval(ASRC[DBEG + len(u"DERIV['B86'] = "):DEND])
assert isinstance(DER_MD, dict) and DER_MD == DER, (len(DER_MD), len(DER))
SITE_MD = ASRC[DBEG:DEND].count(u"B86V(")

def _jsface(x):
    return str(json.loads(json.dumps(x, ensure_ascii=False)))


def _keyface(s):
    try:
        return _jsface(ast.literal_eval(s))
    except Exception:
        return None


JFACE = []
for _kk in sorted(DER, key=lambda x: (len(x), x)):
    _src = VRE.sub(_sub, DER[_kk])
    assert u'B86V' not in _src, _src[:80]
    try:
        _got = eval(_src, {u'max': max, u'min': min, u'sum': sum, u'abs': abs, u'len': len,
                           u'round': round, u'sorted': sorted, u'float': float, u'int': int})
    except Exception as _e:
        DFL6.append((_kk, repr(_e)[:70]))
        continue
    if _kk == u'0':
        if _got != 0:
            DFL6.append((_kk, _src[:80], str(_got)))
    elif str(_got) == _kk or repr(_got) == _kk:
        pass
    elif isinstance(_got, (list, tuple)) and _jsface(_got) == _keyface(_kk):
        # 本遍的取值面是 _b86flat.json, 元组已被序列化成列表; 值同而面不同, 单列一档而不放行
        JFACE.append(_kk)
    else:
        DFL6.append((_kk, _src[:80], str(_got)))
assert not DFL6, DFL6[:4]
assert all(u'(' in k for k in JFACE), JFACE[:3]
assert DCITE6 == SITE_MD == len(u' '.join([DER[x] for x in DER]).split(u'B86V(')) - 1, (DCITE6, SITE_MD)
KEYS_REF = sorted(set([m.group(1) for _kk in DER for m in VRE.finditer(DER[_kk])]))
assert len(DER) == CH[u'deriv_keys'] and set(DER) == set(DER_MD)
assert len(KEYS_REF) <= len(FP) and set(KEYS_REF) <= set(FP)
print(u'⑥ DERIV OK: %d 式 ⇎ audit.py 内嵌段与 json 同字典 ⇎ 引用处 %d(门内数 ⇎ 本遍代入数 ⇎ json 数) ⇎ 被引键 %d 枚全在 %d 键平面上 ⇎ 只经 JSON 序列化档(元组→列表)才对齐的 %d 式; '
      u'契约 deriv_points=%d 是建条遍的“登记式去重”档, 与本遍的“引用处”档不同尺, 不并格(它与平面键数 %d 同数纯属巧合: 一尺数表达式去重, 一尺数键面宽窄)' %
      (len(DER), DCITE6, len(KEYS_REF), len(FP), len(JFACE), CH[u'deriv_points'], len(FP)))


# ---------- ⑦ 指标表逐行: 区域由字面 find 手切(门内是 re.S 非贪婪正则), 码点逐字符入集 ----------
RD = io.open(u'corpus/README.md', encoding=u'utf-8').read()
RL = RD.split(NL)
_I = [i for i, l in enumerate(RL) if l.startswith(u'## 转化指标')]
assert len(_I) == 1, _I
assert RL[_I[0] + 1].startswith(u'| entry') and set(RL[_I[0] + 2].replace(u'|', u'').strip()) == set(u'-')
MTAB = []
for _l in RL[_I[0] + 3:]:
    if not _l.startswith(u'|'):
        break
    MTAB.append([x.strip() for x in _l.split(u'|')[1:-1]])
MB = [c for c in MTAB if re.match(u'^B\\d+$', c[0])]
MTO = [c for c in MTAB if c[0].startswith(u'**合计')]
assert len(MB) == 84 and len(MTO) == 1 and len(MTAB) == 85, (len(MB), len(MTO), len(MTAB))
MID = [c[0] for c in MB]
FID = dict((os.path.basename(p)[:3], p) for p in FILES)
assert len(FID) == 90 and u'B86' in FID and set([x for x in MID if x in FID]) <= set(FID)


def _regions6(t):
    a = t.index(u'[[原始语料|ORIGINAL]]' + NL) + len(u'[[原始语料|ORIGINAL]]') + 1
    b = t.index(NL + NL + u'## ⟪BabelTele', a)
    e = t.index(u'⟪BabelTele⟫' + NL) + len(u'⟪BabelTele⟫') + 1
    f = t.index(NL + NL + u'## ', e)
    return t[a:b], t[e:f]


M6 = {}
for _id in MID + [u'B86']:
    _t = io.open(FID[_id], encoding=u'utf-8').read()
    _og, _ec = _regions6(_t)
    _st = set()
    for _ch in _ec:
        if _ch != NL:
            _st.add(_ch)
    M6[_id] = (len(_ec) - _ec.count(NL), len(_og), _st)
    _n, _ol, _st2 = M6[_id]
    assert num(ROWS[_id][2]) == _n and num(ROWS[_id][5]) == len(_st2), (_id, ROWS[_id][2], _n)
    assert u'%.1f%%' % (_n * 100.0 / _ol) == ROWS[_id][3], (_id, ROWS[_id][3])
STALE = [(_id, c[1], M6[_id][0], c[4], len(M6[_id][2])) for _id, c in zip(MID, MB)
         if num(c[1]) != M6[_id][0] or num(c[4]) != len(M6[_id][2])]
assert not STALE, STALE[:3]
UN84, UN85 = set(), set()
for _id in MID:
    UN84 |= M6[_id][2]
    UN85 |= M6[_id][2]
UN85 |= M6[u'B86'][2]
SUM_N84 = sum([M6[x][0] for x in MID])
SUM_O84 = sum([M6[x][1] for x in MID])
assert num(MTO[0][1]) == SUM_N84, (MTO[0][1], SUM_N84)
print(u'⑦ 指标表 OK: 本遍所列 %d 行 ⇎ audit %d 行, 逐行编码/唯一码点/保留率三格与 audit 相符, README 旧行无失配 ⇎ '
      u'编码合计 %d ⇎ 摘要合计 %d ⇎ 保留率 %.1f%% ⇎ 并集码点 84 条=%d(README 现记 %d) ⇎ 85 条=%d' %
      (len(MID) + 1, len(GROW), SUM_N84, SUM_O84, SUM_N84 * 100.0 / SUM_O84, len(UN84), num(MTO[0][4]), len(UN85)))


# ---------- ⑧ README 记账: 十处改动逐处先验锚位, 落盘后回读比对 ----------
RDL = RL  # ⑦ 末行 RL 已换过一次手(① 里它是 readlines 尺), 这里重新起一名以免两尺混用
RLN = [LN[i] - TNL[i] for i in range(NSRC)]
assert RLN == g(u'readlines'), (RLN, g(u'readlines'))
assert len(RDL) == 777 and RDL[-1] == u'' and RD == NL.join(RDL), len(RDL)
OVER72 = [len([y for y in L[i] if len(y) > 72]) for i in range(NSRC)]
assert [1 if MX[i] > 72 else 0 for i in range(NSRC)] == [1 if c > 0 else 0 for c in OVER72], (MX, OVER72)
RLD = [SPL[i] - LN[i] for i in range(NSRC)]
assert RLD == [FF[i] - TNL[i] for i in range(NSRC)] == g(u'rows_ledger'), (RLD, FF, TNL)
assert [LN[i] - RLN[i] for i in range(NSRC)] == TNL == [1] * NSRC, (LN, RLN, TNL)
OVLEX = [OVL7[i] - FF[i] for i in range(NSRC)]
assert OVLEX == [0, g(u'hdrnew')[1], 0, 0, 0], OVLEX
MROW = [sum(1 for k in range(len(L[i])) if any(HITS[i][r][k] for r in (3, 4, 5, 6))
           and not HITS[i][0][k] and not HITS[i][2][k]) for i in range(NSRC)]
assert MROW == [g(u'hdr793')[0], g(u'hdr1122')[1], g(u'hdrnew')[2], g(u'hdrnew')[3], g(u'hdrnew')[4]], MROW
assert [BL[i] + g(u'foot')[i] + MROW[i] for i in range(NSRC)] == SHL, (BL, g(u'foot'), MROW, SHL)
# 剥壳“重复”逐对拆开: 只统计同时命中两路的行, 三对之和须等于七路之和减剥壳行
PAIR7 = {}
for _a in range(len(RULES)):
    for _b in range(_a + 1, len(RULES)):
        _c = [sum(1 for k in range(len(L[i])) if HITS[i][_a][k] and HITS[i][_b][k]) for i in range(NSRC)]
        if sum(_c) > 0:
            PAIR7[(RULEKEY[_a], RULEKEY[_b])] = _c
assert [sum(max(0, sum(HITS[i][r][k] for r in range(len(RULES))) - 1) for k in range(len(L[i])))
        for i in range(NSRC)] == OVL7, OVL7
assert len(PAIR7) == 3 and sum(sum(v) for v in PAIR7.values()) == sum(OVL7), (sorted(PAIR7), OVL7)
assert not [1 for i in range(NSRC) for k in range(len(L[i]))
            if sum(HITS[i][r][k] for r in range(len(RULES))) >= 3]
assert PAIR7[(u'blank', u'ff_alone')] == FF, PAIR7
FOOTHN = PAIR7[(u'foot', u'hdrnew')][1]
HHOV = PAIR7[(u'hdr1122', u'hdrnew')][1]
assert [FOOTHN, HHOV] == [116, 115] and FOOTHN + HHOV == g(u'hdrnew')[1], (FOOTHN, HHOV)
NNED = [len(v) for v in g(u'numtimes')]
NEG_O = g(u'neg_probes') - g(u'neg_n')
assert NEG_O == g(u'neg_n') * (NSRC - 1) == 44 and g(u'neg_others') == 0, (NEG_O, g(u'neg_others'))
assert g(u'neg_self') == g(u'neg_n') and not g(u'neg_cold')
assert g(u'neg_self_tot') == sum([sum(z) for z in g(u'neg_mat')]) == 21
assert len(g(u'neg_multi')) == len([z for z in g(u'neg_mat') if max(z) > 1]) == 3
assert sum([len(v) for v in g(u'spell_excl')]) == g(u'excl_n')
assert len(g(u'spell')[0]) == 34 and all(x > 0 for x in g(u'spell_vari')), g(u'spell_vari')
SUB5 = sum(g(u'spell_tot'))
WORD5 = sum(g(u'spell_word_tot'))
SPDIFF = [g(u'spell_tot')[i] - g(u'spell_word_tot')[i] for i in range(NSRC)]
assert all(d >= 0 for d in SPDIFF) and g(u'spell_cold') == [u'time-out'], SPDIFF
TCP3 = sum(g(u'spell_tot')[:3])
assert g(u'lin_rel_keys') + len(g(u'lin_rel_pick_names')) - g(u'lin_rel_both') == g(u'kn2_union')
assert len(g(u'lin_rel_pick_names')) - g(u'lin_rel_both') == len(g(u'lin_rel_dropped'))
assert g(u'sr_whole') + g(u'sr_cut') == g(u'sr_n') and g(u'neg_probes') == g(u'neg_n') * NSRC
assert len(g(u'pb_rows')) == 13 and sum(g(u'pb_rows')) == g(u'pb_rows_tot')
assert [FN4[i] - LN4[i] for i in range(NSRC)] == g(u'wrap_gain') == WG6
assert [SN4[i] - FN4[i] for i in range(NSRC)] == [0] * NSRC and not SHELLC6
ANSN = g(u'ans_needle')
for _i in range(NSRC):
    assert pl6(ANSN[_i]) in FOL6[_i], (LBL[_i], ANSN[_i][:40])
FIVE_MIN = pl6(u'five minutes')
assert [i for i in range(NSRC) if FIVE_MIN in FOL6[i]] == [0, 2], [LBL[i] for i in range(NSRC) if FIVE_MIN in FOL6[i]]
NINE246 = g(u'eq_9246_face')
assert str(NINE246) == u'924.6' and g(u'eq_9246_hit') == 0 and g(u'eq2_hit') == 0
assert all(float(x) == int(x) for x in g(u'eq_9246_cand')), g(u'eq_9246_cand')
assert len(g(u'eq_9246_cand')) == 5 and len(set(g(u'eq_9246_cand'))) == 4, g(u'eq_9246_cand')
assert round(min(g(u'eq_9246_gap')), 1) == round(min(g(u'eq2_dev')), 1) == 31842.4
assert [x[2] - x[4] for x in g(u'eq_rows')] == g(u'eq_ruler_ledger') == [0, 0]
GAIN_OK = [GAIN6[i][1] for i in range(NSRC)] == [0] * NSRC and not SHELLC6
assert GAIN_OK and len(TAGC6) == 1 and MOVE6[0][0] == g(u'tag_gain_needles')[0]
BOOLN = g(u'bool_all_n') + g(u'bool2_all')
ZIDN = g(u'zid_scan_n') + g(u'zid_scan2_n')
assert ZIDN == len(CH[u'zid']) and g(u'bool_red') == [] and g(u'bool2_red') == []
assert g(u'bool_green') == g(u'bool_all_n') and g(u'bool2_green') == g(u'bool2_all')
assert g(u'pick_agree') > 0 and g(u'contract_n') == len(FP) == 577
assert g(u'scan_key_n') + 1 == g(u'scan2_src_n')
assert CR == [0] * NSRC, CR
assert [len(x) for x in g(u'spell_excl')] == [0, 0, 0, 0, 13] == [0] * 4 + [g(u'excl_n')]
assert g(u'ovl_splitter_list') == 1 and [g(u'ovl_s1'), g(u'ovl_s2')] == [g(u'ovl_s1_char'), g(u'ovl_s2_char')]
assert g(u'tag_nextline_ledger') == [0] * NSRC
assert g(u'tag_nospace')[2] == TD6[2] + g(u'tag_num_nextline')[2]
assert g(u'sr_n') == 2 * len(g(u'pb_rows'))
PURE6 = g(u'blk_op_n') - g(u'blk_equal_runs') - g(u'blk_replace')
assert PURE6 == 5 and g(u'blk_op_n') == 31
GLUE6 = sorted(set(g(u'glued_all')[4]))
assert len(GLUE6) == g(u'glued_vari')[4] == 7 and len(g(u'glued_all')[4]) == g(u'glued_n')[4] == 9
assert [g(u'eq_rto_face')[t] for t in (0, 2, 1)] == [1.0, 3.0, 60.0], g(u'eq_rto_face')
EQLAB6 = [u'末次×下限 %g 秒' % g(u'eq_rto_face')[0], u'杀死×下限 %g 秒' % g(u'eq_rto_face')[0],
          u'末次×初始 %g 秒' % g(u'eq_rto_face')[2], u'末次×上限 %g 秒' % g(u'eq_rto_face')[1],
          u'等比和×下限 %g 秒' % g(u'eq_rto_face')[0]]
EQCAND6 = u' ⇎ '.join([u'%s（%s）' % (fmt(int(x)), EQLAB6[t])
                       for t, x in enumerate(g(u'eq_9246_cand'))])
assert len(EQCAND6.split(u' ⇎ ')) == 5
MULTI6 = [(k, max(z), u'＋'.join(LBL[i] for i in range(NSRC) if z[i] > 1))
          for k, z in zip(g(u'neg_multi'), [z for z in g(u'neg_mat') if max(z) > 1])]
assert [x[1] for x in MULTI6] == [4, 3, 6] and sum([x[1] for x in MULTI6]) == 13
RETRY6 = u'、'.join([u'%s=%s' % (k, v) for k, v in zip(
    [u'tcp_retries1', u'tcp_retries2', u'tcp_syn_retries', u'tcp_synack_retries'],
    g(u'kn2_default_str'))])
assert g(u'kn2_default_str') == [u'3', u'15', u'6', u'5'], g(u'kn2_default_str')
ENC85 = SUM_N84 + M6[u'B86'][0]
DIG85 = SUM_O84 + M6[u'B86'][1]
POS = [(u'本目录是该协议下的实际转化集', 8), (u'**B82 问的是', 82), (u'| B82 | 15 773（新建', 201),
       (u'| B82 | `raw/tcpRTO/rfc1122.txt`（1989', 310), (u'## 保真门槛：', 325), (u'| B85 | 2 111 | 341.0%', 444),
       (u'| **合计（84 条）**', 445), (u'（B54 起的 31 行是按', 447), (u'python -X utf8 corpus/_fill82.py', 762)]
for _a, _p in POS:
    _h = [i for i, l in enumerate(RDL) if l.startswith(_a)]
    assert len(_h) == 1 and _h[0] == _p, (_a, _h)
_h = [i for i, l in enumerate(RDL) if u'当前 **84 条语料' in l]
assert len(_h) == 1 and _h[0] == 330, _h


def pnet(t):
    return (t.count(u'（') - t.count(u'）'), t.count(u'(') - t.count(u')'))


def JF(xs):
    return u' ⇎ '.join(fmt(x) for x in xs)


def runs85(ns):
    n = sorted([int(x[1:]) for x in ns])
    out, a, b = [], n[0], n[0]
    for x in n[1:]:
        if x == b + 1:
            b = x
        else:
            out.append((a, b))
            a = b = x
    out.append((a, b))
    return u'、'.join(u'B%02d..B%02d' % (a, b) if b > a else u'B%02d' % a for a, b in out)


LISTED85 = MID + [u'B86']
assert len(LISTED85) == 85 and len(set(LISTED85)) == 85
UN5 = sorted([c[0] for c in GROW if c[0] not in set(LISTED85)], key=lambda k: int(k[1:]))
assert len(UN5) == len(GROW) - len(LISTED85) == len(FILES) - len(LISTED85), UN5
UN5S = u'／'.join(UN5)
DELTA_ENC = sum([num(ROWS[t][2]) for t in UN5])
DELTA_DIG = sum([num(ROWS[t][1]) for t in UN5])
DELTA_UNI = num(ALLR[5]) - len(UN85)
assert num(ALLR[2]) - ENC85 == DELTA_ENC and num(ALLR[1]) - DIG85 == DELTA_DIG, \
    (ALLR[2], ENC85, DELTA_ENC, ALLR[1], DIG85, DELTA_DIG)
assert DELTA_UNI > 0
FAILD = {}
for _l in AUD.split(NL):
    _m = re.match(u'^  (B\\d+): 编码侧=\\[(.*?)\\] 原文侧=\\[(.*?)\\] 码位=(\\[.*?\\])', _l)
    if _m:
        FAILD[_m.group(1)] = (len(re.findall(u"'([^']*)'", _m.group(2))),
                              len(re.findall(u"'([^']*)'", _m.group(3))), _m.group(4) == u'[]')
assert sorted(FAILD) == sorted(FAILED) and all(v[2] for v in FAILD.values()), (FAILD, FAILED)
assert u'B86' not in FAILD
FENC = u'⇎'.join(u'%d' % FAILD[t][0] for t in sorted(FAILD))
FDIG = u'⇎'.join(u'%d' % FAILD[t][1] for t in sorted(FAILD))
GFALL = u'／'.join(sorted(FAILD))
OVERALL = len(GROW) - len(FAILD)

ANSBR = [u'只写“不超五分钟”的默认上限, 一次数也不给', u'立 R1 ⇎ R2 两阈值, 到 R2 必须关连接',
         u'照登 1122 两句并给义务词编号, 又许 R2 为无穷', u'不谈次数, 只钉 RTO 下限 60 秒',
         u'交给内核参数与倍增等式']


def hdr(i):
    return u'%d ⟦%s⟧' % (HDRYR[i], LBL[i]) if HDRYR[i] else u'内核文档 ⟦lin⟧'


def brief(i):
    return (u'%s（%s：%s 字节／行数 %s／非空行 %s／最长行 %d 列（超 72 列 %d 行）／换页符 %d 枚／剥壳行 %s 行／'
            u'回车 %d／制表符 %d 枚／非 ASCII %d／答句 %s）'
            % (SHW[i], hdr(i), fmt(BY[i]), fmt(LN[i]), fmt(NB[i]), MX[i], OVER72[i], FF[i], fmt(SHL[i]),
               CR[i], TB[i], NA[i], ANSBR[i]))


def fullcell(i):
    return (u'%s（%s：%s 字节／面内码位 %s／行数 %s（`splitlines()` %s 行 ⇎ `readlines()` %s 行）／非空行 %s／'
            u'最长行 %d 列（超 72 列 %d 行）／换页符 %d 枚（独占整行 %d 行, 行内混排 %d 枚, 起手于换页符 %d 行, '
            u'剥壳行 %s 行＝空行 %s ＋页码行 %d ＋只被眉尺认出的行 %d, 七路之和 %s 比剥壳行多 %d）／回车 %d／制表符 %d 枚／'
            u'非 ASCII %d（BOM %d ⇎ 非 BOM %d, 码位清单 %s; 续字节口径 %d 枚）／答句 %s）'
            % (SHW[i], hdr(i), fmt(BY[i]), fmt(CP[i]), fmt(LN[i]), fmt(SPL[i]), fmt(RLN[i]), fmt(NB[i]),
               MX[i], OVER72[i], FF[i], FF_ALONE[i], FF[i] - FF_ALONE[i], FF_LEAD[i], fmt(SHL[i]), fmt(BL[i]),
               g(u'foot')[i], MROW[i], fmt(SUM7[i]), OVL7[i], CR[i], TB[i], NA[i], BOM[i], NA[i] - BOM[i],
               (u'、'.join(u'U+%04X' % c for c in g(u'na_codepoints')[i]) if NA[i] else u'无'),
               g(u'utf8_extra')[i], ANSBR[i]))


RATE85 = u'%.1f%%' % (ENC85 * 100.0 / DIG85)
OB5S = JF(OBU_SH)
OB5L = JF([sum(v) for v in OBLOW])
TDS = JF(TD6)
YRS = u' ⇎ '.join([u'%d' % y for y in HDRYR[:4]] + [u'内核文档无抬头年'])
NINE246GAP = min(g(u'eq_9246_gap'))
Q = lambda i: u'⟦%s⟧⟨%s⟩' % (LBL[i], ANSN[i])

# 跨行义务词: 大写档 §④ 已量(ob_wrap 即 折−行), 小写档与忽略大小写档在本遍另起一把尺——
# 机制换成“整篇折平面 + 接缝位置表”, 数落在接缝上的命中, 与采集侧的邻 token 现拼读法同义不同形
UPD = [[OB_MINE[u'折'][i][k] - OB_MINE[u'行'][i][k] for k in range(len(OB5))] for i in range(NSRC)]
assert [x for row in UPD for x in row] == g(u'ob_wrap') and all(x >= 0 for row in UPD for x in row)
UPSHAPES = [OB5[k] for k in range(len(OB5)) if any(UPD[i][k] for i in range(NSRC))]
LINED = [[sum([ob6(fc6(y), w) for y in L[i]]) for w in OBL5] for i in range(NSRC)]
LOWD = [[OBLOW[i][k] - LINED[i][k] for k in range(len(OBL5))] for i in range(NSRC)]
assert all(x >= 0 for row in LOWD for x in row), LOWD
LOWSHAPES = [OBL5[k] for k in range(len(OBL5)) if any(LOWD[i][k] for i in range(NSRC))]
LOWSUM = sum([x for row in LOWD for x in row])


def seamface6(rows):
    acc, seams, pos = [], [], 0
    for y in rows:
        yy = u' '.join(y.split())
        if not yy:
            continue
        if acc:
            seams.append(pos)
        pos += len(yy) + 1
        acc.append(yy)
    return u' '.join(acc), seams


def straddle6(face, seams, words, flags):
    out = []
    for w in words:
        for m in re.finditer(u'(?<!\\w)' + re.escape(w) + u'(?!\\w)', face, flags):
            if any(m.start() < sp < m.end() for sp in seams):
                out.append((w, m.start()))
    return out


FOLUP, SEAM6 = [None] * NSRC, [None] * NSRC
for i in range(NSRC):
    FOLUP[i], SEAM6[i] = seamface6(L[i])
    assert len([y for y in L[i] if u' '.join(y.split())]) == len(SEAM6[i]) + 1, (LBL[i], len(SEAM6[i]))
LOWLINE = [sum(r) for r in LINED]
assert LOWLINE == [202, 243, 212, 12, 55] and sum(LOWLINE) + LOWSUM == sum([sum(r) for r in OBLOW])
LOWDOC6 = u'、'.join([u'%s 落在 %s' % (OBL5[k], u'＋'.join(LBL[i] for i in range(NSRC) if LOWD[i][k]))
                      for k in range(len(OBL5)) if any(LOWD[i][k] for i in range(NSRC))])
assert LOWDOC6 == u'must not 落在 793、should not 落在 793＋9293', LOWDOC6
ST_UP = [len(straddle6(FOLUP[i], SEAM6[i], OB5, 0)) for i in range(NSRC)]
ST_LOWCI = [len(straddle6(FOLUP[i], SEAM6[i], OBL5, re.IGNORECASE)) for i in range(NSRC)]
ST_LOWCS = [sum(v) for v in LOWD]
assert ST_UP == g(u'st_up') == [sum(UPD[i]) for i in range(NSRC)], (ST_UP, g(u'st_up'))
assert ST_LOWCI == g(u'st_low'), (ST_LOWCI, g(u'st_low'))
assert ST_LOWCI == [ST_UP[i] + ST_LOWCS[i] for i in range(NSRC)], (ST_LOWCI, ST_UP, ST_LOWCS)
print(u'⑧乙 跨行义务词: 严格大写 %d 对 %s ⇎ 忽略大小写 %d 对 ⇎ 只认小写 %d 对 %s（逐份 %s ⇎ %s）' %
      (sum(ST_UP), u'、'.join(UPSHAPES), sum(ST_LOWCI), sum(ST_LOWCS), u'、'.join(LOWSHAPES),
       J(ST_UP), J(ST_LOWCI)))

# ---------- (甲) 判词段 ----------
P86 = (u'**B86 问的是重传几次、多久之后该放弃，五份一手文书给出五种答法**：' + u' ⇎ '.join([brief(i) for i in range(NSRC)]) +
       u'——四份是 RFC Editor 纯文本面且 72 列硬换行（超 72 列 %s 行）而内核那份最长 %d 列 ⇎ 回车逐份 %s 枚（五份皆零）⇎ '
       u'换页符只住在 RFC 侧三份（%s 枚, 且全部独占整行, 一枚也不夹在行中间）⇎ 制表符 %s 枚 ⇎ '
       u'非 ASCII %s 枚全在 9293（码位 %s 两种: 前者两枚＋BOM 一枚, 换成 UTF-8 续字节口径是 %d 枚＝该份字节 %s 减码位 %s）; 抬头年 %s, 前四份跨 %d 年。'
       % (JF(OVER72), MX[4], JF(CR), JF(FF), JF(TB), JF(NA), u'、'.join(u'U+%04X' % c for c in g(u'na_codepoints')[2]),
          g(u'utf8_extra')[2], fmt(BY[2]), fmt(CP[2]),
          YRS, HDRYR[2] - HDRYR[0]) +
       u'三把行尺各给一数: `split("\\n")` %s ⇎ `splitlines()` %s ⇎ `readlines()` %s 行——splitlines 比 `split("\\n")` 多 %s 行, '
       u'恰等于换页符枚数减尾换行, readlines 又比 `split("\\n")` 少 %s 行, 少的正是各份那一枚收尾换行。'
       % (JF(LN), JF(SPL), JF(RLN), JF(RLD), J(TNL)) +
       u'五种答法: 793 通篇时长式只 %d 枚 ⇎ 带单位数值 %d 项, 上限写成“five minutes”而对次数一字不提, '
       u'判词 %s（%d 词跨 %d 行）⇎ 1122 把放弃拆成两阈值 %s（%d 词跨 %d 行, 到 R2 必须关连接）⇎ '
       u'9293 照登同一 procedure、给义务词缀上 %d 枚编号, 又添一句 %s 把取舍交回应用（%d 词跨 %d 行）⇎ '
       u'6298 只管计时 %s（%d 词跨 %d 行, 只把 RTO 的下限钉在 60 秒）⇎ '
       u'ip-sysctl 交回内核参数与倍增等式 %s（%d 词跨 %d 行, %d 个去重键, tcp_retries1=3 ⇎ tcp_retries2=15）。'
       % (g(u'dur_by_doc')[0], g(u'numval_n')[0], Q(0), g(u'ans_words')[0], g(u'ans2_span')[0],
          Q(1), g(u'ans_words')[1], g(u'ans2_span')[1], TD6[2], Q(2),
          g(u'ans_words')[2], g(u'ans2_span')[2], Q(3), g(u'ans_words')[3], g(u'ans2_span')[3],
          Q(4), g(u'ans_words')[4], g(u'ans2_span')[4], g(u'kn2_uniq')) +
       u'“多久”在第五份变成可复算的等式: 倍增表 syn 默认 %d 次⇒末次累计 %d 秒 ⇎ 杀死连接 %d 秒, '
       u'synack %d 次⇒%d/%d, 逐行尺与闭式尺逐行差 0 且与面上印出的 %d/%d ⇎ %d/%d 逐格对上; '
       u'打满 100 秒的最小次数末次 %d ⇎ 杀死 %d, 而文书自说 at least %d——文说比末次多 %d、比杀死多 %d; '
       u'面上印着“%s 秒”%d 枚, 五式候选各复算一次（%s, 去重成 4 个不同值）一枚也不中, 最小偏离 %s 秒——'
       u'本条因此把“印着一个数”与“算得出这个数”分在两档: %s 只在字面档露面, %s 反而是纯推导。'
       % (g(u'eq_rows')[0][1], g(u'eq_rows')[0][2], g(u'eq_rows')[0][3], g(u'eq_rows')[1][1],
          g(u'eq_rows')[1][2], g(u'eq_rows')[1][3], g(u'eq_rows')[0][5], g(u'eq_rows')[0][6],
          g(u'eq_rows')[1][5], g(u'eq_rows')[1][6], g(u'eq_min_n_last'), g(u'eq_min_n_kill'), g(u'eq_doc_says'),
          g(u'eq_off_by')[0], g(u'eq_off_by')[1], fmt(NINE246), g(u'eq_9246_printed'),
          EQCAND6, fmt(NINE246GAP),
          fmt(NINE246), fmt(NINE246GAP)) +
       u'换代三条同时可见: 义务词写成编号的只有 9293（连字尺 %s）⇎ 答句写明次数的组数逐份 %s ⇎ '
       u'判词在四档面上的读数（%d 枚针×五份=%d 格: 行 %s ⇎ 折 %s ⇎ 摘壳 %s ⇎ 去编号 %s 枚）——折平涨 %d 次（逐份 %s）, '
       u'摘壳一粒不增（换页符行 ⇎ 页脚行 ⇎ 只被眉尺认出的行一枚也不压在判词上：被壳切开的针 %d 枚）, '
       u'去编号多读 %d 枚: %s 把义务词写成 (MUST-n) 式编号, 恰好掐断 %s 那一枚针; '
       u'被线切开的判词 %d 枚全由 72 列换行所致, 编号再切 %d 枚, 跨行枚数合计 %d ⇎ 最长跨 %d 行; '
       u'义务词跨行三档: 严格大写 %d 对（%s）⇎ 忽略大小写 %d 对 ⇎ 只认小写 %d 对（%s, 即 %s）, 逐份相加闭合: 严格大写 %s ＋ 只认小写 %s ＝ 忽略大小写 %s; '
       u'编号族只在 9293——连字尺 %d 枚 ⇎ token 尺 %d ⇎ '
       u'括号内 %d ＋裸形 %d 比连字尺少 %d 枚 ⇎ 粘连写法 %d 枚＝连字尺 %d ＋行首编号 %d ⇎ 最大号 %d ⇎ 摘掉它们吃掉 %s 字符。'
       % (TDS, JF(NNED), CH[u'needle_n'], len(NK6) * NSRC,
          JF(LN4), JF(FN4), JF(SN4), JF(TN4), sum(WG6), JF(WG6), len(SHELLC6),
          TG6, u'⟦%s⟧' % MOVE6[0][1], u'⟨%s⟩' % NK6[MOVE6[0][0]], len(WRAP6), len(TAGC6),
          g(u'sc_span_tot'), g(u'sc_max_span'),
          sum(ST_UP), u'、'.join(UPSHAPES), sum(ST_LOWCI), LOWSUM, u'、'.join(LOWSHAPES), LOWDOC6,
          J(ST_UP), J(ST_LOWCS), J(ST_LOWCI),
          TD6[2], g(u'tag_token')[2], g(u'tag_in_paren')[2], g(u'tag_bare')[2], -g(u'tag_form_ledger')[2],
          g(u'tag_nospace')[2], TD6[2], g(u'tag_num_nextline')[2], g(u'tag_max_no')[2], fmt(g(u'tag_chars')[2])))
P86 += (u'语形族 %d 式: 子串尺 %d 枚 ⇎ 整词尺 %d 枚（逐份多读 %s）⇎ 全冷一式“%s” ⇎ 独有 %d 枚全落在内核那份面上（前四份各 %d 枚）; '
        u'反向 %d 枚针各在五份面上探一遍共 %d 次: 主家面 %d 枚针现 %d 次（其中 %d 枚不止一次: %s）⇎ 另四份面共 %d 次探针命中 %d ⇎ '
        u'%d/%d 式是“排除面零 ⇎ 主家恰一次”的干净反向; '
        u'段窗 %d 扇共 %d 行 ⇎ 窗端点 %d 处（每扇首尾各一处）里 %d 处在本行读通 ⇎ %d 处要推到下行; '
        u'1122 ⇎ 9293 同段对照 行 %s ⇎ 句 %s ⇎ 逐字同 %d ⇎ 去编号同 %d ⇎ 归拼同 %d ⇎ 新句 %d。'
        u'闭合账: 布尔门 %d+%d=%d 道全绿 ⇎ 恒等式 %d+%d=%d 条归零（V 形回读 %d 条同数）⇎ 采集对账 %d/%d 键符 ⇎ '
        u'锚 %d 处去重 %d（独占 %d ⇎ 跨界 %d ⇎ 全份 %d, 归属复核 %d 次错配 %d）⇎ 编码区 %s 字符 ⇎ '
        u'DERIV %d 式在本遍就地重算（引用 %d 处 ⇎ 被引键 %d 枚全在 %d 枚键面上）⇎ 扁平 577 键五套实现零失配。'
        % (len(g(u'spell')[0]), SUB5, WORD5, JF(SPDIFF), g(u'spell_cold')[0], g(u'excl_n'), 0,
           g(u'neg_n'), g(u'neg_probes'), g(u'neg_self'), g(u'neg_self_tot'), len(MULTI6),
           u'、'.join([u'%s 在 %s 现 %d 次' % (k, d, n) for k, n, d in MULTI6]),
           NEG_O, g(u'neg_others'), g(u'neg_clean'), g(u'neg_n'),
           len(g(u'pb_rows')), g(u'pb_rows_tot'), g(u'sr_n'), g(u'sr_whole'), g(u'sr_cut'),
           JF(g(u'ov2_rows')), JF(g(u'ov2_sents')), g(u'ov2_same_raw'), g(u'ov2_same_tag'),
           g(u'ov2_same_canon'), g(u'ov2_new'),
           g(u'bool_all_n'), g(u'bool2_all'), BOOLN, g(u'zid_scan_n'), g(u'zid_scan2_n'), ZIDN, len(CH[u'zid']),
           g(u'pick_agree'), g(u'pick_agree'), len(CIT6), len(STR6), S1, S2, S5, CH[u'checks'], g(u'anchor_err'),
           fmt(ENC6), len(DER), DCITE6, len(KEYS_REF), len(FP)))
assert pnet(P86) == (0, 0), pnet(P86)
assert u'|' not in P86 and P86.count(u'`') % 2 == 0
print(u'⑧甲 判词段: %d 字符' % len(P86))

# ---------- (丙) 门槛表行: 锚账 ⇎ 面尺 ⇎ 五源同现形状, 全由本遍现数 ----------
FACE6 = [sum([oc6(FOL6[i], pl6(a)) for a in STR6]) for i in range(NSRC)]
TAGCNT6 = [TAGN6[t] for t in TAGS]
assert sum(TAGCNT6) == len(CIT6) == g(u'anchor_total'), (TAGCNT6, len(CIT6))
assert all(FACE6[i] >= TAGCNT6[i] for i in range(NSRC)), (FACE6, TAGCNT6)
FACED6 = [FACE6[i] - TAGCNT6[i] for i in range(NSRC)]
ALLS6 = [a for a in STR6 if len(HITC6[a]) == NSRC]
SPACED6 = [a for a in ALLS6 if u' ' in a]
PLAIN6 = [a for a in ALLS6 if u' ' not in a]
assert [len(PLAIN6), len(SPACED6), len(ALLS6)] == [5, 2, S5], (len(PLAIN6), len(SPACED6), S5)
MAXALL6 = max([len(a) for a in PLAIN6])
assert MAXALL6 == max([len(a) for a in ALLS6]), (MAXALL6, PLAIN6, SPACED6)
ANCHTAG = u' ⇎ '.join(u'%s ⟦%s⟧' % (LBL[i], LBL[i]) for i in range(NSRC))


def _tone(w):
    return sum(g(w))


assert _tone(u'pb_tone_must') == 11 and _tone(u'pb_tone_should') == 6
assert g(u'lin_keys_uniq') + len(g(u'kn2_dups')) == g(u'lin_keys_total') == 234
assert sum(g(u'lin_shape_n')) == len(g(u'kn2_shape')) == 16 and g(u'lin_rel_union') == 22
assert len(g(u'lin_numvals')) == g(u'numval_n')[4] == 10, (g(u'lin_numvals'), g(u'numval_n'))
assert len(g(u'lin_hexvals')) == 1 and len(g(u'glued_all')[4]) == g(u'glued_n')[4]
assert g(u'lin_shape_n') == g(u'kn2_shape_n') == [9, 3, 1, 1, 2]
assert sum(g(u'pb_rows')) == g(u'pb_rows_tot') and g(u'sr_whole') + g(u'sr_cut') == g(u'sr_n')
assert g(u'ovl_rows') == g(u'ov2_rows') and g(u'ovl_new') == g(u'ov2_new')
assert g(u'pb_five_rows') == sum([g(u'pb_rows')[t] for t in range(NSRC)]) == 110
assert g(u'pb_doc')[:NSRC] != list(range(NSRC)), g(u'pb_doc')
ANSROWS = sum([g(u'pb_rows')[t] for t in g(u'pb_ans_win')])
assert g(u'pb_ans_close') == 0 and g(u'pb_ans_n') == [1, 1, 2, 1, 1]
assert len(set(g(u'pb_ans_win'))) == NSRC and ANSROWS == 121 < g(u'pb_rows_tot')
assert 0 < g(u'pb_one_line') <= len(g(u'pb_rows'))
assert g(u'blk_words')[0] == g(u'blk_equal_words') + g(u'blk_drop_words') \
    and g(u'blk_words')[1] == g(u'blk_equal_words') + g(u'blk_insert_words')
assert g(u'blk_op_n') >= g(u'blk_equal_runs') + g(u'blk_replace')
assert g(u'ovl_splitter_diff') == 0 and g(u'blk_form_ledger') == [0, 0, 0]

# ---------- (丁) 门槛表行正文 ----------
G86 = (u'| B86 | %s（新建, 重传几次、多久之后该放弃 交 TCP 三份规范（1981 ⇎ 1989 ⇎ 2022）⇎ 一份 RTT 度量规范 ⇎ '
       u'一份内核参数文档共五份一手文书各答一遍 %d 处标注／%d 个不同串（登记全命中, 单源 %d ⇎ 穿二至四源 %d ⇎ 五源全现 %d——'
       u'全现的 %d 枚里 %d 枚是无空格单词形（最长 %d 字符: “%s”）⇎ %d 枚带空格短语形（“%s” ⇎ “%s”）, '
       u'编码区 %s 字符, 归属检查 %d 次, 错配 %d）: 五色锚位 %s（%s 处, '
       u'本遍按 ⟦ 分段手吃 ⟨…⟩ 现数并与建条目侧逐键对拍; 摘要遍按面另扫一遍, 同一批引用在五份面上露面 %s 次, '
       u'比归属尺多出的 %s 次是他源之锚恰好也活在这份面上——面尺 ≥ 引用尺逐份恒成立, 两把尺不共用键）; '
       u'四档口径（原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳去编号折平）在 %d 枚判词针×五份 %d 格上读到 %s ⇎ %s ⇎ %s ⇎ %s 次命中, '
       u'增益逐份 %s=%d ⇎ 摘壳 %d ⇎ 去编号 %d——折平救回的全部是 72 列硬换行（被线切开 %d 枚）, '
       u'摘壳一粒不增（被壳切开 %d 枚）, 去编号多读 %d 枚: %s 的 (MUST-n) 掐断 %s; '
       % (fmt(ENC6), len(CIT6), len(STR6), S1, S2, S5, len(ALLS6), len(PLAIN6), MAXALL6,
          max(PLAIN6, key=len), len(SPACED6), SPACED6[0], SPACED6[1], fmt(ENC6), CH[u'checks'], g(u'anchor_err'),
          ANCHTAG, JF(TAGCNT6), JF(FACE6), JF(FACED6),
          len(NK6), len(NK6) * NSRC, JF(LN4), JF(FN4), JF(SN4), JF(TN4), JF(WG6), sum(WG6),
          sum([GAIN6[i][1] for i in range(NSRC)]), TG6,
          len(WRAP6), len(SHELLC6), TG6, u'⟦%s⟧' % MOVE6[0][1], u'⟨%s⟩' % NK6[MOVE6[0][0]]))
G86 += (u'编号族只在 9293——连字尺 %d ⇎ token 尺 %d ⇎ 括号内 %d ＋裸形 %d 差 %d 枚 ⇎ 粘连面 %d 枚＝连字尺 %d ＋行首编号 %d ⇎ 最大号 %d ⇎ '
        u'摘掉吃 %s 字符 ⇎ 编号落在下行首 %d 枚; 义务词五式在摘壳折面 %s ⇎ 小写折面 %s（逐行小写 %s, 差 %d 枚即跨行那几对）⇎ '
        u'跨行三档 严格大写 %d ⇎ 忽略大小写 %d ⇎ 只认小写 %d '
        u'（逐份相加闭合: 严格大写 %s ＋ 只认小写 %s ＝ 忽略大小写 %s, 大写词形 %s ⇎ 小写词形 %s 即 %s）; 语形族 %d 式: 子串 %s 枚 ⇎ 整词 %s 枚（逐份多读 %s）⇎ 全冷一式“%s” ⇎ 独有 %d 枚全落内核那份面（前四份各 %d）; '
        u'反向 %d 枚针各在五份面探一遍共 %d 次: 主家面 %d 枚针现 %d 次（%d 枚不止一次: %s）⇎ 另四份面共 %d 次探针命中 %d ⇎ '
        u'“排除面零＋主家恰一次”的干净反向 %d/%d 式; '
        u'段窗 %d 扇共 %d 行 ⇎ 每份的首个主答句窗（扇号自 1 起: 第 %s 扇）合 %d 行, 9293 另有第二扇 ⇎ 头五扇 %d 行是另一把尺 ⇎ 单行成窗 %d 扇 ⇎ '
        u'十三扇内语气词 MUST %d ⇎ SHOULD %d ⇎ 编号 %d ⇎ MAY %d ⇎ 词 %s 枚 ⇎ 字符 %s 枚 ⇎ '
        u'窗端点自验 %d 处（每扇首尾各一处）= 本行读通 %d ＋推到下行 %d; '
        % (TD6[2], g(u'tag_token')[2], g(u'tag_in_paren')[2], g(u'tag_bare')[2], -g(u'tag_form_ledger')[2],
           g(u'tag_nospace')[2], TD6[2], g(u'tag_num_nextline')[2], g(u'tag_max_no')[2],
           fmt(g(u'tag_chars')[2]), g(u'tag_num_nextline')[2],
           OB5S, OB5L, J(LOWLINE), LOWSUM,
           sum(ST_UP), sum(ST_LOWCI), LOWSUM, J(ST_UP), J(ST_LOWCS), J(ST_LOWCI),
           u'、'.join(UPSHAPES), u'、'.join(LOWSHAPES), LOWDOC6,
           len(g(u'spell')[0]), fmt(SUB5), fmt(WORD5), JF(SPDIFF), g(u'spell_cold')[0], g(u'excl_n'), 0,
           g(u'neg_n'), g(u'neg_probes'), g(u'neg_self'), g(u'neg_self_tot'), len(MULTI6),
           u'、'.join([u'%s 在 %s 现 %d 次' % (k, d, n) for k, n, d in MULTI6]),
           NEG_O, g(u'neg_others'), g(u'neg_clean'), g(u'neg_n'),
           len(g(u'pb_rows')), g(u'pb_rows_tot'), u'、'.join([str(t + 1) for t in g(u'pb_ans_win')]),
           ANSROWS, g(u'pb_five_rows'), g(u'pb_one_line'),
           _tone(u'pb_tone_must'), _tone(u'pb_tone_should'),
           _tone(u'pb_tone_tag'), _tone(u'pb_tone_may'), fmt(g(u'pb_words_tot')), fmt(g(u'pb_chars_tot')),
           g(u'sr_n'), g(u'sr_whole'), g(u'sr_cut')))
G86 += (u'1122 ⇎ 9293 同段对照: 行 %s ⇎ 句 %s ⇎ 页壳行 %s ⇎ 全篇章节抬头行 %s 枚 ⇎ 逐字同 %d ⇎ 去编号同 %d ⇎ 归拼同 %d ⇎ 新句 %d ⇎ '
        u'词级对齐共 %d 段（等长 %d ⇎ 相替 %d ⇎ 纯插或纯删 %d）⇎ 共有词 %d ⇎ 1122 独有 %d ⇎ 9293 独有 %d——两份词账 %d＝%d＋%d ⇎ %d＝%d＋%d 各自闭合 ⇎ '
        u'最长共有段 %d 词 ⇎ 段字符 %s ⇎ 段词数 %s ⇎ 9293 段内编号 %d 枚吃 %d 字符 ⇎ 两把切分尺（按行拼句 ⇎ 按字符切句）在两份上各得 %d ⇎ %d 句, 之差 %d 枚; '
        u'内核键表: 键行 %d ⇎ 去重 %d ⇎ 重名 %d 个 ⇎ Default 行 %d ⇎ 带单位数值 %d 项 ⇎ 十六进制 %d 枚 ⇎ '
        u'数字粘连单位 %d 处（去重成 %d 个不同写法: %s）⇎ 值带句点 %d 处 ⇎ 相关键并集 %d 枚 ⇎ 取得到默认值写法的 %d 键分五档 %s ⇎ 四个重传键默认值 %s; '
        u'“多久”那份可复算: 倍增表 syn %d⇒末次 %d ⇎ 杀死 %d 秒 ⇎ synack %d⇒%d/%d, 逐行尺与闭式尺逐行差 %s 且与面上印出 %d/%d ⇎ %d/%d 对上 ⇎ '
        u'打满 100 秒最小 末次 %d/杀死 %d 而文说 at least %d（文说比末次多 %d、比杀死多 %d）⇎ 面上印“%s 秒”%d 枚, 五式复算（%s, 去重 4 值）命中 %d 枚, 最小偏离 %s 秒; '
        % (JF(g(u'ovl_rows')), JF([g(u'ovl_s1'), g(u'ovl_s2')]), JF(g(u'ovl_shell')), JF(g(u'ov_hdr_rows')),
           g(u'ovl_same_raw'), g(u'ovl_same_tag'), g(u'ovl_same_canon'), g(u'ovl_new'),
           g(u'blk_op_n'), g(u'blk_equal_runs'), g(u'blk_replace'), PURE6, g(u'blk_equal_words'),
           g(u'blk_drop_words'), g(u'blk_insert_words'),
           g(u'blk_words')[0], g(u'blk_equal_words'), g(u'blk_drop_words'),
           g(u'blk_words')[1], g(u'blk_equal_words'), g(u'blk_insert_words'),
           g(u'blk_longest'), JF(g(u'blk_chars')), JF(g(u'blk_words')),
           g(u'blk_tag_n'), g(u'blk_tag_chars'),
           g(u'ovl_s1') + g(u'ovl_s2'), g(u'ovl_s1_char') + g(u'ovl_s2_char'), g(u'ovl_splitter_diff'),
           g(u'lin_keys_total'), g(u'lin_keys_uniq'), len(g(u'kn2_dups')), g(u'lin_default_lines'),
           len(g(u'lin_numvals')), len(g(u'lin_hexvals')), g(u'glued_n')[4], g(u'glued_vari')[4],
           u'、'.join(GLUE6), g(u'lin_val_punct'), g(u'lin_rel_union'),
           len(g(u'kn2_shape')), J(g(u'lin_shape_n')), RETRY6,
           g(u'eq_rows')[0][1], g(u'eq_rows')[0][2], g(u'eq_rows')[0][3], g(u'eq_rows')[1][1],
           g(u'eq_rows')[1][2], g(u'eq_rows')[1][3], J(g(u'eq_ruler_ledger')),
           g(u'eq_rows')[0][5], g(u'eq_rows')[0][6], g(u'eq_rows')[1][5], g(u'eq_rows')[1][6],
           g(u'eq_min_n_last'), g(u'eq_min_n_kill'), g(u'eq_doc_says'),
           g(u'eq_off_by')[0], g(u'eq_off_by')[1],
           fmt(NINE246), g(u'eq_9246_printed'),
           EQCAND6, g(u'eq_9246_hit'), fmt(NINE246GAP)))
G86 += (u'版式与行尺: 字节 %s ⇎ 码位 %s ⇎ 三把行尺 `split("\\n")` %s ⇎ `splitlines()` %s ⇎ `readlines()` %s——'
        u'第二把比第一把多 %s 行（=换页 %s 枚−尾换行 %s）, 第三把每份少 1 行（尾换行）⇎ 超 72 列 %s 行 ⇎ 制表 %s 枚 ⇎ 回车逐份 %s 枚 ⇎ '
        u'非 ASCII %s（BOM %s ⇎ 剥壳后存活 %s）⇎ 剥壳 %s 行＝七路命中之和 %s−共认 %s（换页独占行同时是空行 逐份 %s ⇎ '
        u'1122 页码行同时命中新式眉尺 %d 行 ⇎ 1122 眉尺同时命中新式眉尺 %d 行, 无一行被三路以上共认）⇎ '
        u'空行 %s ＋页码 %s ＋只被眉尺认出的行 %s 三档相加逐份等于剥壳行; '
        u'闭合账: 布尔门 %d+%d=%d 道全绿 ⇎ V 形恒等式 %d+%d=%d 条归零 ⇎ 采集对账 %d/%d 键符 ⇎ 分歧 %d 枚 ⇎ '
        u'DERIV %d 式在本遍就地重算（引用 %d 处 ⇎ 被引 %d 枚全在 %d 枚扁平键面内）⇎ 编码区 %s 字符里锚内字母按串 %d ⇎ 按处 %d ⇎ 锚外 %s ⇎ '
        u'与整行原文逐字相同的锚 %d 枚（余 %d 枚要经折面才对齐）。） |'
        % (JF(BY), JF(CP), JF(LN), JF(SPL), JF(RLN), JF(RLD), JF(FF), JF(TNL), JF(OVER72), JF(TB), JF(CR),
           JF(NA), JF(BOM), JF(g(u'bom_after_fold')), JF(SHL), JF(SUM7), JF(OVL7), JF(FF),
           FOOTHN, HHOV, JF(BL), JF(g(u'foot')), JF(MROW),
           g(u'bool_all_n'), g(u'bool2_all'), BOOLN, g(u'zid_scan_n'), g(u'zid_scan2_n'), ZIDN,
           g(u'pick_agree'), g(u'pick_agree') + g(u'pick_diff'), g(u'pick_diff'),
           len(DER), DCITE6, len(KEYS_REF), len(FP), fmt(ENC6), LIN6D, LIT6, fmt(LOUT6),
           len(CIT6) - len(LITLINE), len(LITLINE)))
assert len(G86.split(u'|')) == 4, len(G86.split(u'|'))
assert pnet(G86) == (0, 0), pnet(G86)
assert G86.startswith(u'| B86 | ') and G86.endswith(u' |')
print(u'⑧丙 门槛表行: %d 字符' % len(G86))

# ---------- (戊) 语料表行: 五份版式账逐份全列 ＋ 判据只取本遍现量 ----------
FMC = [oc6(FOL6[i], FIVE_MIN) for i in range(NSRC)]
assert FMC == [1, 0, 1, 0, 0], FMC
LOWDOC = [sum(r) for r in OBLOW]
assert LOWDOC == [204, 243, 213, 12, 55]
assert [LOWDOC[i] - LOWLINE[i] for i in range(NSRC)] == ST_LOWCS, (LOWDOC, LOWLINE, ST_LOWCS)
JUDGE86 = (u'五份答同一个问题 ⇒ 答的是五种东西: 793 通篇大写义务词 %d 枚, 上限只写成“five minutes”'
           u'（该语在折平面上逐份露面 %s 次）, 答句里写明重传次数的组数 %d ⇎ '
           u'1122 把放弃拆成 R1 ⇎ R2 两阈值并写成义务（大写 %d ⇎ 小写 %d, 组数 %d）⇎ '
           u'9293 照登 1122 那两句而把义务词缀成编号 %d 枚（摘掉吃 %s 字符）, 与 1122 同段逐字同 %d 句 ⇎ '
           u'去编号同 %d 句 ⇎ 归拼同 %d 句 ⇎ 新句 %d 句, 另许 R2 取 infinity ⇎ '
           u'6298 一个次数也不给（组数 %d）, 只把 RTO 下限钉在 at least 60 秒（大写 %d ⇎ 小写 %d）⇎ '
           u'lin 交回内核参数表: 键行 %d ⇎ 去重 %d ⇎ Default 行 %d, 四个重传键默认 %s, '
           u'又把“多久”写成倍增等式——面上印“%s 秒”%d 枚而五式复算命中 %d 枚（最小偏离 %s 秒）; '
           u'四档阶梯在本条的空转全在摘壳档（折平比逐行多读 %d 次 ⇎ 摘壳再多 %d 枚 ⇎ 去编号再多 %d 枚）, '
           u'被行界劈开的判词 %d 枚 ⇎ 被编号劈开的 %d 枚'
           % (OBU_SH[0], JF(FMC), NNED[0], OBU_SH[1], LOWDOC[1], NNED[1], TD6[2], fmt(g(u'tag_chars')[2]),
              g(u'ovl_same_raw'), g(u'ovl_same_tag'), g(u'ovl_same_canon'), g(u'ovl_new'),
              NNED[3], OBU_SH[3], LOWDOC[3],
              g(u'lin_keys_total'), g(u'lin_keys_uniq'), g(u'lin_default_lines'), RETRY6,
              fmt(NINE246), g(u'eq_9246_printed'), g(u'eq_9246_hit'), fmt(NINE246GAP),
              sum(WG6), sum([SN4[i] - FN4[i] for i in range(NSRC)]),
              sum([TN4[i] - SN4[i] for i in range(NSRC)]), len(WRAP6), len(TAGC6)))
assert u'|' not in JUDGE86 and pnet(JUDGE86) == (0, 0), pnet(JUDGE86)
CORPUS86 = u'| B86 | %s | %s |' % (u' ⇎ '.join([fullcell(i) for i in range(NSRC)]), JUDGE86)
assert len(CORPUS86.split(u'|')) == 5 and CORPUS86.startswith(u'| B86 | ')
assert pnet(CORPUS86) == (0, 0), pnet(CORPUS86)
print(u'⑧戊 语料表行: %d 字符' % len(CORPUS86))

# ---------- (己) 指标表行 ⇎ 合计行 ⇎ 机械行注 ----------
ENC86R = num(R86[2])
assert ENC86R == ENC6 == M6[u'B86'][0] == g(u'enc_chars'), (ENC86R, ENC6, M6[u'B86'][0])
assert R86[3] == u'%.1f%%' % (ENC6 * 100.0 / M6[u'B86'][1])
assert num(R86[5]) == len(M6[u'B86'][2])
MROW86 = (u'| B86 | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
          % (fmt(ENC6), R86[3], R86[4], fmt(num(R86[5])), R86[7]))
assert MROW86.count(u'|') == 7 and pnet(MROW86) == (0, 0)
MECH = [c for c in MB if u'本行为 audit 直出' in c[3]]
assert len(MECH) == 31 and u'B86' not in [c[0] for c in MB], len(MECH)
NEW9 = [u'B73', u'B75', u'B76', u'B77', u'B78', u'B79', u'B83', u'B84', u'B85']
assert all(x in MID for x in NEW9) and len(NEW9) == 9
TOTAL86 = (u'| **合计（%d 条）** | **%s** | **%s**（摘要段合计 %s, 这两格已含本遍直补的 B86 一枚 %s 编码／%s 摘要——'
           u'剔掉它正是上一遍 84 行的 %s 编码／%s 摘要; '
           u'audit 当下出 %d 行而本表只列 %d 行，未列入的 %s 共 %d 枚仍带着 %s 编码／%s 摘要只在 audit 里出行，'
           u'故上一遍那句“本表 84 行与 audit 的 84 行一一对齐”“合计四格逐格相符于 ALL 行”自本遍起失效——'
           u'本表合计按所列 %d 行现数，与 ALL 行相差的 %s 编码 ⇎ %s 摘要 ⇎ %d 枚唯一码点正是那 %d 枚的量；'
           u'唯一码点那格仍由本遍按 audit 的编码区正则逐条现数取并集（拼接后去重，非各条之和），'
           u'%d 条并集 %d 枚比上一遍的 %d 枚多 %d） | — | **%s** | — |'
           % (len(LISTED85), fmt(ENC85), RATE85, fmt(DIG85), fmt(ENC6), fmt(M6[u'B86'][1]),
              fmt(SUM_N84), fmt(SUM_O84),
              len(GROW), len(LISTED85), UN5S, len(UN5), fmt(DELTA_ENC), fmt(DELTA_DIG),
              len(LISTED85), fmt(DELTA_ENC), fmt(DELTA_DIG), DELTA_UNI, len(UN5),
              len(LISTED85), len(UN85), num(MTO[0][4]), len(UN85) - num(MTO[0][4]), fmt(len(UN85))))
assert TOTAL86.count(u'|') == 7 and pnet(TOTAL86) == (0, 0), pnet(TOTAL86)
assert u'84 行' in RDL[447] and u'31 行' in RDL[447]
NOTE86 = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与字符/语义单元五格, '
          u'不重写各条的口径注; 上一遍再直补 %s 共 %d 枚, 当时本表 84 行确与 audit 的 84 行一一对齐; '
          u'本遍再直补新建的 B86 一枚（五源对照条, 口径注在门槛表行与语料表行里, 这里只直出五格）, '
          u'至此本表列到 %d 行而 audit 已有 %d 行——未列入的 %s 共 %d 枚只在 audit 出行, '
          u'故“一一对齐”与“合计四格逐格相符于 ALL 行”两句自本遍起失效, 直补标记仍剩 %d 行带“本行为 audit 直出”字样。）'
          % (len(MECH) + 1, u'⇎'.join(NEW9), len(NEW9), len(LISTED85), len(GROW), UN5S, len(UN5), len(MECH) + 1))
assert pnet(NOTE86) == (0, 0) and u'|' not in NOTE86
print(u'⑧己 指标表行 %d 字符 ⇎ 合计行 %d 字符 ⇎ 机械行注 %d 字符' % (len(MROW86), len(TOTAL86), len(NOTE86)))

# ---------- (庚) 门槛标题 ⇎ 陈述 ⇎ 条数陈述 ⇎ 命令链 ----------
assert RDL[325].startswith(u'## 保真门槛：') and u'**PASS**' in RDL[325] and u'（84 条）' in RDL[325]
GATE86 = (u'## 保真门槛：`python corpus/audit.py` → **FAIL**（%d 条: 红灯只有一类——%s 三枚的 T1 数字锚未回源'
          u'（编码侧 %s ⇎ 原文侧 %s）, 本遍新建的 B86 不在红列）' % (len(GROW), GFALL, FENC, FDIG))
assert RDL[330].startswith(u'   结果按锚点小数位四舍五入相等。当前 **84 条语料／3884 条**')
SENT86 = (u'   结果按锚点小数位四舍五入相等。当前 **%d 条语料／%d 条**推导: 除 %s 三枚的 T1 数字锚未回源'
          u'（编码侧 %s ⇎ 原文侧 %s, 三枚的码位清单皆空, 故无一条靠推导补上）之外全部通过'
          u'（audit 自报“已机检的推导 %d 条”, 行集与条目文件数相符 %d ⇎ %d）; 本遍新建的 B86 不在红列, '
          u'其 %d 式推导在本遍就地重算零失配, 如'
          % (len(GROW), PROOFS, GFALL, FENC, FDIG, PROOFS, len(GROW), len(FILES), len(DER)))
assert RDL[8].startswith(u'本目录是该协议下的实际转化集，共 **84 条**（')
_T9 = RDL[8].split(u'），分两代。')
assert len(_T9) == 2 and u'本遍把已接线而未进转化指标表的' in _T9[0]
assert runs85(LISTED85) == u'B01..B65、B67..B86', runs85(LISTED85)
HEAD86 = (u'本目录是该协议下的实际转化集，共 **%d 条**（`babeltele/%s`, 本遍新建 B86 一枚（TCP 重传次数与放弃时机, '
          u'五份一手文书）并把它的转化指标行直补进表, 合计行随之按本表所列 %d 条现算 ⇎ 唯一码点逐条现数取并集 %d 枚; '
          u'上一遍那句“与 audit 的 84 行一一对齐”自本遍起失效——audit 现有 %d 行, 未进本表的 %s 共 %d 枚仍只在 audit 里出行'
          % (len(LISTED85), runs85(LISTED85), len(LISTED85), len(UN85), len(GROW), UN5S, len(UN5))
          + u'），分两代。' + _T9[1])
assert pnet(HEAD86) == pnet(RDL[8]), (pnet(HEAD86), pnet(RDL[8]))
CMDS = [
    u'python -X utf8 corpus/_pick86.py                    # 选源预检: 同一问题的五份一手文书（rfc793 ⇎ rfc1122 ⇎ rfc9293 ⇎ rfc6298 ⇎ ip-sysctl）逐份先量版式与义务词形状, 定下四档面与反向对照面',
    u'python -X utf8 corpus/_mkB86.py                     # 建条目(前半, 与 _mk86emit.py 同场 exec): 扁平契约 %d 枚键 ⇎ DERIV %d 枚算式 ⇎ V 形 %d 条; 四档面(原行⇎折平⇎摘壳⇎去编号)⇎%d 枚判词针 ⇎ 义务词五式 ⇎ 编号族 ⇎ 带单位数值 ⇎ 段窗 ⇎ 反向针 ⇎ 内核键表'
    % (g(u'contract_n'), len(DER), ZIDN, CH[u'needle_n']),
    u'python -X utf8 corpus/_mkdigest3.py B86 <entry> 793 corpus/raw/tcpRetr/rfc793.txt 300 200 1122 corpus/raw/tcpRetr/rfc1122.txt 300 200 9293 corpus/raw/tcpRetr/rfc9293.txt 300 200 6298 corpus/raw/tcpRetr/rfc6298.txt 300 200 lin corpus/raw/tcpRetr/ip-sysctl.txt 300 200   # 五源分节摘要(每份开一窗 300/200), 本遍用同一组窗口在副本上重建, 与在库文件在 ⛓解读注之前的正文逐字符相同',
    u'python -X utf8 corpus/_wire86.py                    # 接线: SRC/ATOM/SCAN(审计器侧两套实现)/DERIV/B86V 进 audit.py, 落盘前复跑 %d 枚扁平键 ⇎ %d 枚算式 ⇎ %d 次归属检查' % (g(u'contract_n'), len(DER), CH[u'checks']),
    u'python -X utf8 corpus/_fill86.py                    # 第五遍(注区): 行界手索引 ⇎ `bisect` 行号尺 ⇎ token 跨度尺 ⇎ ast 摘门右式各重导一次, %d 道布尔门 ⇎ %d 条 V 形现算归零后写回 ⛓解读注（与采集遍对账不符 0/%d ⇎ 分歧 0 枚）' % (BOOLN, ZIDN, g(u'pick_agree')),
    u'python -X utf8 corpus/_readme86.py                  # 第六遍(记账): 本版式另起尺复量（七路剥壳逐对拆开 ⇎ 三把行尺 ⇎ 接缝表数跨行义务词 ⇎ 11×5 反向探面对拍）后把 B86 写进本文件十处; 判词段 %d 字符 ⇎ 门槛表行 %d 字符 ⇎ 语料表行 %d 字符'
    % (len(P86), len(G86), len(CORPUS86)),
]
for _c in CMDS:
    assert u'|' not in _c and pnet(_c) == (0, 0) and _c.startswith(u'python ')
print(u'⑧庚 门槛标题 %d ⇎ 陈述 %d ⇎ 条数陈述 %d ⇎ 命令链 %d 行' % (len(GATE86), len(SENT86), len(HEAD86), len(CMDS)))

# ---------- (辛) 落盘: 十处改动按索引降序施加, 写完回读逐行比对 ----------
OPS = [(763, 763, CMDS), (447, 448, [NOTE86]), (445, 446, [MROW86, TOTAL86]),
       (330, 331, [SENT86]), (325, 326, [GATE86]), (311, 311, [CORPUS86]),
       (202, 202, [G86]), (83, 83, [P86]), (8, 9, [HEAD86])]
assert [o[0] for o in OPS] == sorted([o[0] for o in OPS], reverse=True)
assert sum(len(o[2]) - (o[1] - o[0]) for o in OPS) == 10
NEWL = list(RDL)
for _a, _b, _ls in OPS:
    NEWL[_a:_b] = _ls
assert len(NEWL) == len(RDL) + 10 == 787, (len(RDL), len(NEWL))
RD2 = NL.join(NEWL)
OUT = u'corpus/README.md.tmp86'
io.open(OUT, u'w', encoding=u'utf-8', newline=NL).write(RD2)
os.replace(OUT, u'corpus/README.md')
BACK = io.open(u'corpus/README.md', encoding=u'utf-8').read()
BL2 = BACK.split(NL)
assert BACK == RD2 and len(BL2) == 787, (len(BL2), len(RD2))
REPL = dict([(o[0], o[2]) for o in OPS if o[1] > o[0]])
assert sorted(REPL) == [8, 325, 330, 445, 447], sorted(REPL)
KEPT, GONE = [], []
for _i, _l in enumerate(RDL):
    (GONE if _i in REPL else KEPT).append(_l)
for _l in KEPT:
    assert BL2.count(_l) >= 1, _l[:40]
for _l in GONE:
    assert _l not in BL2, _l[:40]
ADDED = []
for _a, _b, _ls in OPS:
    ADDED += _ls
assert len(ADDED) == len(set(ADDED)) == 15, len(ADDED)
for _l in ADDED:
    assert BL2.count(_l) == 1, _l[:40]


def _one(_pre):
    _k = [i for i, l in enumerate(BL2) if l.startswith(_pre)]
    assert len(_k) == 1, (_pre, _k)
    return _k[0]


assert BL2[_one(u'**B82 问的是') + 1] == P86
assert BL2[_one(u'| B82 | 15 773（新建') + 1] == G86
assert BL2[_one(u'| B82 | `raw/tcpRTO/rfc1122.txt`') + 1] == CORPUS86
assert BL2[_one(u'## 保真门槛：')] == GATE86 and BL2[_one(u'   结果按锚点小数位四舍五入相等。')] == SENT86
_i = _one(u'| B85 | 2 111 |')
assert BL2[_i + 1] == MROW86 and BL2[_i + 2] == TOTAL86
assert BL2[_i + 3] == u'' and BL2[_i + 4] == NOTE86
assert TOTAL86.startswith(u'| **合计（85 条）**') and MROW86.startswith(u'| B86 | 13 086 |')
_j = _one(u'python -X utf8 corpus/_pick86.py')
assert BL2[_j:_j + 6] == CMDS and BL2[_j - 1].startswith(u'python -X utf8 corpus/_fill82.py')
assert BL2[_j + 6].startswith(u'python -X utf8 corpus/atomcheck.py B67')
assert sum([1 for _l in BL2 if _l.startswith(u'| B') and u'本行为 audit 直出' in _l]) == len(MECH) + 1
assert len([_l for _l in BL2 if _l.startswith(u'| B') and _l.count(u'|') == 7]) == len(LISTED85)
assert BL2[8] == HEAD86 and BL2[9] == RDL[9] and BL2[7] == RDL[7]
assert RD2.count(u'84 条') == RD.count(u'84 条') - sum([_l.count(u'84 条') for _l in GONE])
assert len([l for l in BL2 if l.startswith(u'| B86 |')]) == 3
assert u'**PASS**' not in GATE86 and u'**FAIL**' in GATE86
json.dump({u'enc85': ENC85, u'dig85': DIG85, u'rate': RATE85, u'union85': len(UN85),
           u'union84': len(UN84), u'audit_rows': len(GROW), u'unlisted': UN5,
           u'delta_enc': DELTA_ENC, u'delta_dig': DELTA_DIG, u'delta_uni': DELTA_UNI,
           u'proofs': PROOFS, u'fail': GFALL, u'fail_enc': FAILD,
           u'lines_before': len(RDL), u'lines_after': len(BL2),
           u'p86': len(P86), u'g86': len(G86), u'corpus86': len(CORPUS86), u'cmds': len(CMDS)},
          io.open(u'corpus/_b86readme.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)
print(u'⑧辛 落盘 OK: %d 行→%d 行 ⇎ 判词段 %d ⇎ 门槛行 %d ⇎ 语料行 %d ⇎ 指标行 %d ⇎ 合计 %s ⇎ 并集 %d ⇎ 门槛标题 FAIL ⇎ 命令链 %d 行'
      % (len(RDL), len(BL2), len(P86), len(G86), len(CORPUS86), len(MROW86), RATE85, len(UN85), len(CMDS)))
