# -*- coding: utf-8 -*-
"""README 记账第五遍(B72): 判词段 ⇎ 门槛表行 ⇎ 语料表行 ⇎ 转化指标机械行 ⇎ 聚合行, 全部按本遍现跑的
audit 与 raw 字节现量, 一个数都不抄建条目侧快照。

本遍的第五套实现(与采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注四遍换轨, 定义一律照抄):
① 面量吃 raw 字节, 行数按换行符计数, splitlines 档另数一遍(换页符也是行界)并与建条目侧恒等式对拍;
② 折平走手写空白折叠扫描(逐字符判空白run)⇎ 前三遍分别是 ' '.join(split()) 与 re.sub('[ ]+') 两轨,
   折完与建条目侧面量逐字符相等才算同一定义;
③ 剥引文标记本遍用正则两次 re.sub(行首竖线+跟随空格、行尾竖线), 与第四遍的逐字符切片实现相对拍,
   并且不止抽样: 对四份面的每一行都断言两实现同值;
④ 针文本不再抄建条目侧的 TEXT, 而按 SENT 的(起,止)在本遍自己的剥引文折平面上切片重导出, 长度与
   建条目侧 nd_len 逐枚相等才算导出一致; 命中计数用非重叠游标 ⇎ 正则字面轨两条都跑并互相对拍;
⑤ 整词尺本遍用“按非字母切段后逐段等值”, 与建条目侧的正向否定环视、第四遍的手写邻字扫描三轨并立;
⑥ 长行池与锚候选池本遍用位掩码(int 的 popcount)分档, 与建条目侧的 defaultdict(tuple)、第四遍的
   defaultdict(set) 换轨; 配对与容斥从掩码重算;
⑦ 窗口带内/带外本遍用行索引直接切, 数字符用逐字符 isdigit 计数, 与第四遍的切片拼接换轨;
⑧ 偏移映回原行号本遍改为“造面时并行登记行号表”, 按偏移直接取(既不线性扫描也不 bisect);
⑨ 义务语气/六族措辞/引用三式全部现量, 与扁平契约逐枚对拍, 不符先收集后汇总;
⑩ 转化指标表的“唯一码点”不再抄 audit 的 ALL 行(那是全库并集, 而本表只列已记账条目): 本遍按
   audit 自己的编码区正则逐条现数, 逐条与 audit 现算值对拍后取列内并集, 未记账条目的差另算一条账。
"""
import io, itertools, json, re, sys, ast, glob, subprocess

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\r\n' if u'\r\n' in io.open(u'corpus/README.md', encoding=u'utf-8').read() else u'\n'
S = io.open(u'corpus/README.md', encoding=u'utf-8').read()
FP = json.load(io.open(u'corpus/_b72flat.json', encoding=u'utf-8'))
DER = json.load(io.open(u'corpus/_deriv72.json', encoding=u'utf-8'))
CH = json.load(io.open(u'corpus/_b72checks.json', encoding=u'utf-8'))
C = u'corpus'
NSRC = 4
LBL = [u'2616', u'7231', u'7538', u'9110']
YR = [u'99', u'14', u'15', u'22']
SRC = [C + u'/raw/httpRedir/rfc2616.txt', C + u'/raw/httpRedir/rfc7231.txt',
       C + u'/raw/httpRedir/rfc7538.txt', C + u'/raw/httpRedir/rfc9110.txt']
SHW = [u'`raw/httpRedir/rfc2616.txt`', u'`raw/httpRedir/rfc7231.txt`',
       u'`raw/httpRedir/rfc7538.txt`', u'`raw/httpRedir/rfc9110.txt`']
ANS = [u'把 302 写成“客户端不许改写方法、但实现都当 303 用”, 301 还要先确认',
       u'删掉确认门, 换成“出于历史原因 a user agent MAY change the request method”, 307 才 MUST NOT change',
       u'不动 302, 另立 308 说“does not allow changing the request method from POST to GET”',
       u'收下那句 MAY 并排成竖线引文块, 正文另给叙述式(converged)与编号清单第 4 步两轨']
ENT = glob.glob(u'corpus/babeltele/B72_*.md')[0]

AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                     text=True, encoding=u'utf-8').stdout
assert u'T3 码位): PASS' in AUD, AUD[-500:]
assert u'证明失败' not in AUD, AUD[-500:]


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


def occ(t, w):
    """非重叠游标(定义同建条目侧 cnt_cur)"""
    c, i, n = 0, 0, len(w)
    while True:
        j = t.find(w, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def ovl(t, w):
    c, i = 0, 0
    while True:
        j = t.find(w, i)
        if j < 0:
            return c
        c += 1
        i = j + 1


def tok(t, w):
    """整词尺③: 按非字母切段后逐段等值"""
    return len([x for x in re.split(u'[^A-Za-z]+', t) if x == w])


SPCH = set(u' \n\t\x0b\x0c\r\x1c\x1d\x1e\x1f\x85\u2028\u2029\u00a0\u1680\u2000\u2001\u2002\u2003'
           u'\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u202f\u205f\u3000')


def foldscan(t):
    """手写空白run折叠(第五轨): 逐字符扫, run 收成一枚空格, 首尾run丢弃"""
    o, i, n = [], 0, len(t)
    while i < n:
        if t[i] in SPCH:
            while i < n and t[i] in SPCH:
                i += 1
            continue
        j = i
        while j < n and t[j] not in SPCH:
            j += 1
        if o:
            o.append(u' ')
        o.append(t[i:j])
        i = j
    return u''.join(o)


def dqre(x):
    """剥引文标记(定义照抄建条目侧 dequote, 实现换成两次 re.sub)"""
    y = re.sub(u'^[ \\t\\x0b\\x0c\\r]*\\| ?', u'', x)
    return re.sub(u'\\|[ \\t\\x0b\\x0c\\r]*$', u'', y.rstrip())


def pnorm(s):
    return u' '.join(s.lower().split())


def L4(v):
    return u' ⇎ '.join(u'—' if x is None else fmt(x) for x in v)


# ---------- ① 逐份面量 ----------
BS = LN = NB = EF = FFC = CR = NA = ML = DELTA = EXTRA = BOM = SPLITL = TAIL = None
BS, LN, NB, EF, FFC, CR, NA, ML, DELTA, EXTRA, BOM, SPLITL, TAIL = [], [], [], [], [], [], [], [], [], [], [], [], []
DIGCH, DBL, NUL = [], [], []
T = []
L = []
for p in SRC:
    b = io.open(p, u'rb').read()
    BS.append(len(b))
    t = b.decode(u'utf-8', u'replace')
    T.append(t)
    L.append(t.split(u'\n'))
    LN.append(t.count(u'\n') + 1)
    SPLITL.append(len(t.splitlines()))
    TAIL.append(1 if t.endswith(u'\n') else 0)
    NB.append(len([x for x in L[-1] if x.strip() != u'']))
    EF.append(len([x for x in L[-1] if x == u'\x0c']))
    FFC.append(occ(t, u'\x0c'))
    CR.append(occ(t, u'\r'))
    NA.append(len([c for c in t if ord(c) > 127]))
    ML.append(max(len(x) for x in L[-1]))
    DELTA.append(len(b) - len(t))
    EXTRA.append(sum(len(c.encode(u'utf-8')) - 1 for c in t if ord(c) > 127))
    BOM.append(1 if b[:3] == b'\xef\xbb\xbf' else 0)
    DIGCH.append(len([c for c in t if c.isdigit()]))
    DBL.append(ovl(t, u'  '))
    NUL.append(occ(t, u'\x00'))
assert [BS, LN, NB, ML, CR, NA, BOM, DELTA, EXTRA, DIGCH] == \
       [gk(u'bytes'), gk(u'lines'), gk(u'nonblank'), gk(u'maxlen'), gk(u'cr'), gk(u'nonascii'),
        gk(u'bom'), gk(u'byte_cp_delta'), gk(u'nonascii_extra'), gk(u'digit_chars')]
assert gk(u'chars') == [len(t) for t in T]
assert gk(u'lines_nl') == LN and gk(u'ff') == gk(u'ff_exact') == FFC
assert gk(u'ff_only') == [len([x for x in L[i] if x.strip() == u'\x0c']) for i in range(NSRC)] == [0] * 4
assert gk(u'tail_nl') == TAIL and gk(u'nul_faces') == NUL and gk(u'dblspace') == DBL
assert SPLITL == gk(u'lines_split')
assert gk(u'lines_split_close') == sum(LN[i] - TAIL[i] + FFC[i] - SPLITL[i] for i in range(NSRC)) == 0
assert gk(u'ascii_all') == sum(1 for i in range(NSRC) if NA[i] == 0) == 3

# ---------- ②③ 四档面(折平与剥引文各换一轨, 与建条目侧面量逐字符对拍) ----------
MS = io.open(u'%s/_mkB72.py' % C, encoding=u'utf-8').read()
NS = {u're': re}
for fn in (u'shell_line', u'shell_pick_line', u'dequote'):
    exec(re.search(u'def ' + fn + u'\\([a-z]\\):.*?\\n(?=\\S)', MS, re.S).group(0), NS)
is_shell, is_pick, dq_mk = NS[u'shell_line'], NS[u'shell_pick_line'], NS[u'dequote']
TAB = {}
for src in (MS, io.open(u'%s/_mk72emit.py' % C, encoding=u'utf-8').read()):
    for st in ast.parse(src.replace(u'\nexec(', u'\n#exec(')).body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
            nm = st.targets[0].id
            if nm in (u'SENT', u'TIER', u'PINS', u'ANSND', u'HDR', u'WORDS') and nm not in TAB:
                try:
                    TAB[nm] = ast.literal_eval(st.value)
                except Exception:
                    pass
for nm in (u'SENT', u'TIER', u'PINS', u'ANSND', u'HDR', u'WORDS'):
    assert nm in TAB, nm
SENT, TIERTAB, PINS, ANSND, HDRR = TAB[u'SENT'], TAB[u'TIER'], TAB[u'PINS'], TAB[u'ANSND'], TAB[u'HDR']
WORDS = TAB[u'WORDS']

FOLD, SH, SHF, QUOT = [], [], [], []
for i in range(NSRC):
    assert all(dqre(x) == dq_mk(x) for x in L[i]), LBL[i]
    FOLD.append(foldscan(T[i]))
    assert FOLD[i] == u' '.join(T[i].split()), LBL[i]
    assert FOLD[i] == re.sub(u'\\s+', u' ', T[i]).strip(), LBL[i]
    SH.append([x for x in L[i] if not is_shell(x)])
    SHF.append(foldscan(u'\n'.join(SH[i])))
    assert SHF[i] == u' '.join(u'\n'.join(SH[i]).split()), LBL[i]
    assert SHF[i] == re.sub(u'\\s+', u' ', u'\n'.join(SH[i])).strip(), LBL[i]
    QUOT.append(u' '.join([s for s in [foldscan(dqre(x)) for x in L[i]] if s]))
    assert QUOT[i] == u' '.join(u'\n'.join([dq_mk(x) for x in L[i]]).split()), LBL[i]
    assert QUOT[i] == re.sub(u'\\s+', u' ', u'\n'.join([dq_mk(x) for x in L[i]])).strip(), LBL[i]
# 行号并行表: 造面时把剥引文面上的每个字符登记到它的原行(既不线性扫描也不 bisect)
QMAP = []
for i in range(NSRC):
    mp = []
    first = True
    for n, x in enumerate(L[i], 1):
        s = foldscan(dqre(x))
        if not s:
            continue
        if not first:
            mp.append(n)
        first = False
        mp.extend([n] * len(s))
    QMAP.append(mp)
    assert len(mp) == len(QUOT[i]), (i, len(mp), len(QUOT[i]))


def line_of(i, a):
    return QMAP[i][a]


assert gk(u'shell_n') == [len(L[i]) - len(SH[i]) for i in range(NSRC)]
assert gk(u'shell_strip') == [len(SH[i]) for i in range(NSRC)]
PICKN = [len([x for x in L[i] if is_pick(x)]) for i in range(NSRC)]
assert gk(u'shell_pick') == gk(u'shell_pick_measured') == PICKN
MO = [[x for x in L[i] if is_shell(x) and not is_pick(x)] for i in range(NSRC)]
PO = [[x for x in L[i] if is_pick(x) and not is_shell(x)] for i in range(NSRC)]
assert gk(u'shell_mk_only') == [len(x) for x in MO]
assert gk(u'shell_pick_only') == [len(x) for x in PO]
assert gk(u'shell_both') == [gk(u'shell_n')[i] - len(MO[i]) for i in range(NSRC)]
assert gk(u'shell_diff') == [gk(u'shell_n')[i] - PICKN[i] for i in range(NSRC)]
assert gk(u'shell_mk_only_hdr') == [len([x for x in MO[i] if re.match(
    u'^[ \t]*(Network Working Group|Request for Comments:|Obsoletes:|Updates:|Category:|ISSN:)', x)])
    for i in range(NSRC)]
assert gk(u'shell_pick_only_body') == [len([x for x in PO[i] if re.match(u'^[ \t]+RFC [0-9]{4} ', x)])
                                       for i in range(NSRC)]
BARF = [occ(FOLD[i], u'|') for i in range(NSRC)]
BARQ = [occ(QUOT[i], u'|') for i in range(NSRC)]
assert [BARF, BARQ, [BARF[i] - BARQ[i] for i in range(NSRC)]] == \
       [gk(u'bar_fold'), gk(u'bar_quot'), gk(u'bar_removed')]
assert gk(u'bar_removed_line') == [sum(x.count(u'|') - dq_mk(x).count(u'|') for x in L[i])
                                  for i in range(NSRC)]
assert gk(u'pipe_glyphs') == [occ(T[i], u'|') for i in range(NSRC)]
assert gk(u'pipe_lines') == [len([x for x in L[i] if x.lstrip().startswith(u'|')]) for i in range(NSRC)]
assert gk(u'quot_line_n') == [len([x for x in L[i] if u'|' in x]) for i in range(NSRC)]
assert gk(u'quot_face_delta') == [len(FOLD[i]) - len(QUOT[i]) for i in range(NSRC)]
assert gk(u'quot_dropped') == [gk(u'pipe_glyphs')[i] - gk(u'quot_face_delta')[i] for i in range(NSRC)]

# ---------- ④ 针: 由(起,止)在本遍剥引文面上重导出 ----------
NEG = [k for o, k, s0, e0 in SENT if s0.startswith(u'@')]
OWNER = dict((k, o) for o, k, _, _ in SENT)
GN = [k for o, k, _, _ in SENT]
TEXT = {}
for (o, k, s0, e0) in [(i, k, s, e) for i, k, s, e in SENT if not k.endswith(u'_pipe')]:
    if k in NEG:
        TEXT[k] = s0[1:]
        continue
    a = QUOT[o].find(s0)
    b = QUOT[o].find(e0, a)
    TEXT[k] = QUOT[o][a:b + len(e0)]
_a = FOLD[3].find(u'For historical reasons, a user agent MAY change')
_b = FOLD[3].find(u'subsequent request.', _a)
TEXT[u'a9110_302_hist_may_pipe'] = FOLD[3][_a:_b + len(u'subsequent request.')]
assert TEXT[u'a9110_302_hist_may_pipe'] != TEXT[u'a9110_302_hist_may']
assert [len(TEXT[k]) for k in GN] == gk(u'nd_len')
assert gk(u'nd_len_tot') == sum(len(TEXT[k]) for k in GN)
FACES = [L, FOLD, SHF, QUOT]


def hit(k, tier):
    o = OWNER[k]
    nd = TEXT[k]
    if tier == 0:
        return occ(u'\n'.join([x for x in L[o] if nd in x]), nd)
    return occ(FACES[tier][o], nd)


SN = dict((k, [hit(k, n) for n in range(4)]) for k in GN)
for k in GN:
    assert SN[k] == gk(u'n_' + k), k
assert gk(u'needle_n') == len(GN) == 25
assert gk(u'needles_owned') == [len([k for k in GN if OWNER[k] == i]) for i in range(NSRC)]
assert gk(u'sn_strict_docs') == [len([k for k in GN if OWNER[k] == i and SN[k][0]]) for i in range(NSRC)]
assert gk(u'sn_fold_docs') == [len([k for k in GN if OWNER[k] == i and SN[k][1]]) for i in range(NSRC)]
assert gk(u'sn_sh_docs') == [len([k for k in GN if OWNER[k] == i and SN[k][2]]) for i in range(NSRC)]
assert gk(u'sn_quot_docs') == [len([k for k in GN if OWNER[k] == i and SN[k][3]]) for i in range(NSRC)]
FON = [k for k in GN if not SN[k][0] and SN[k][1]]
assert sorted(FON) == sorted(gk(u'fold_only_keys'))
FOWN = [len([k for k in FON if OWNER[k] == i]) for i in range(NSRC)]
assert FOWN == gk(u'fold_only_own') and len(FON) == gk(u'fold_only_n')
QON = [k for k in GN if not SN[k][2] and SN[k][3]]
assert sorted(QON) == sorted(gk(u'quot_only_keys'))
assert [len([k for k in QON if OWNER[k] == i]) for i in range(NSRC)] == gk(u'quot_only_own')
assert [SN[k][2] and not SN[k][3] for k in GN].count(True) == gk(u'quot_lost_n')
assert gk(u'quot_minus_sh') == [gk(u'sn_quot_docs')[i] - gk(u'sn_sh_docs')[i] for i in range(NSRC)]
assert gk(u'sh_minus_fold') == [0] * 4
assert all(FOWN[i] + gk(u'sn_strict_docs')[i] == gk(u'sn_fold_docs')[i] for i in range(NSRC))
assert gk(u'sn_sh_docs') == gk(u'sn_fold_docs')
assert gk(u'ladder_monotone') == 1
DEAD = [k for k in GN if not SN[k][3] and k not in [u'a9110_302_hist_may_pipe']]
assert sorted(DEAD) == sorted(gk(u'dead_needles'))
assert sorted([k for k in GN if not SN[k][3]]) == sorted(gk(u'dead_widest'))
assert gk(u'dead_nonneg') == len([k for k in DEAD if k not in NEG]) == 0
assert sorted(NEG) == gk(u'neg_controls') and sum(SN[k][3] for k in NEG) == gk(u'neg_hit_widest') == 0
assert gk(u'ser_fold_hit') == SN[u'a9110_302_hist_may_pipe'][1] == 2
assert gk(u'ser_quot_hit') == SN[u'a9110_302_hist_may_pipe'][3] == 0
assert all(len(re.findall(re.escape(TEXT[k]), QUOT[OWNER[k]])) == SN[k][3]
           for k in GN) == (gk(u're_eq_cur') == 1)
assert gk(u'overlap_extra') == sum(ovl(QUOT[OWNER[k]], TEXT[k]) - SN[k][3] for k in GN) == 0
assert gk(u'cross_needle_n') == len([k for k in GN if sum(1 for i in range(NSRC) if SN[k][i]) >= 2])

# ---------- ⑤ 义务语气四轨 ----------
UP = dict((w, [tok(T[i], w) for i in range(NSRC)]) for w in WORDS)
LO = dict((w, [tok(T[i], w.lower()) for i in range(NSRC)]) for w in WORDS)
CI = dict((w, [tok(T[i].lower(), w.lower()) for i in range(NSRC)]) for w in WORDS)
TI = dict((w, [tok(T[i], w[:1].upper() + w[1:].lower()) for i in range(NSRC)]) for w in WORDS)
UPN = dict((w, [occ(T[i], w) for i in range(NSRC)]) for w in (u'MUST NOT', u'MAY NOT', u'SHOULD NOT'))
assert UP[u'MUST'] == gk(u'up_must_all') and UP[u'MAY'] == gk(u'up_may') and UP[u'SHOULD'] == gk(u'up_should')
assert UPN[u'MUST NOT'] == gk(u'must_not') and UPN[u'SHOULD NOT'] == gk(u'should_not')
assert UPN[u'MAY NOT'] == gk(u'may_not') == [0] * 4
assert [UP[u'MUST'][i] - UPN[u'MUST NOT'][i] for i in range(NSRC)] == gk(u'must_bare')
assert LO[u'MUST'] == gk(u'low_must') and CI[u'MUST'] == gk(u'ci_must')
assert gk(u'case_ledger') == [sum(CI[w][i] - UP[w][i] - LO[w][i] - TI[w][i] for w in WORDS)
                              for i in range(NSRC)] == [0] * 4
assert gk(u'up_ledger') == [0] * 4
assert [tok(T[i], u'method') for i in range(NSRC)] == gk(u'method_word')
assert [tok(T[i], u'redirect') for i in range(NSRC)] == gk(u'redirect_word')

# ---------- 六族措辞(折平面 ⇎ 剥引文面两档) ----------
TIERT = dict((k, [occ(FOLD[i], w) for i in range(NSRC)]) for k, w in TIERTAB.items())
TIERQ = dict((k, [occ(QUOT[i], w) for i in range(NSRC)]) for k, w in TIERTAB.items())
for k in TIERTAB:
    assert TIERT[k] == gk(u'tier_' + k) and TIERQ[k] == gk(u'tierq_' + k)
FT = [sum(TIERT[k][i] for k in TIERTAB) for i in range(NSRC)]
QT = [sum(TIERQ[k][i] for k in TIERTAB) for i in range(NSRC)]
assert FT == gk(u'tier_fold_tot') and QT == gk(u'tier_quot_tot')
assert [QT[i] - FT[i] for i in range(NSRC)] == gk(u'tier_gain')
assert gk(u'tier_sum_close') == sum(gk(u'tier_gain')) - sum(gk(u'quot_only_own')) == 0
assert [occ(QUOT[i], u'POST to GET') for i in range(NSRC)] == gk(u'post_to_get')
assert [occ(QUOT[i], u'For historical reasons') for i in range(NSRC)] == gk(u'hist_reasons')

# ---------- 30x 小节 ⇎ 号码 ⇎ 数字四档 ----------
HEADLN, CODES = [], []
for i in range(NSRC):
    intro = [n for n, x in enumerate(L[i], 1) if re.match(u'^1\\.[ ]+Introduction[ ]*$', x.rstrip())]
    lo = intro[0] if intro else 0
    hd = [(n, x.strip()) for n, x in enumerate(L[i], 1)
          if re.search(HDRR[i], x) and n > lo and len(x.strip()) < 70]
    HEADLN.append(hd)
    CODES.append(re.findall(u'(30[0-9])', u' '.join(h[1] for h in hd)))
assert [len(h) for h in HEADLN] == gk(u'sec_heads') == gk(u'code_n')
assert CODES == gk(u'codes')
assert sorted(set().union(*[set(c) for c in CODES])) == gk(u'code_union')
assert [sorted(set(c)) for c in CODES] == gk(u'code_distinct')
assert [h[-1][0] if h else 0 for h in HEADLN] == gk(u'head_eof')
assert [h[0][0] if h else 0 for h in HEADLN] == gk(u'head_first_ln')
assert [occ(T[i], u'308') for i in range(NSRC)] == gk(u's308_raw')
assert [occ(FOLD[i], u'308') for i in range(NSRC)] == gk(u's308_fold')
assert [occ(SHF[i], u'308') for i in range(NSRC)] == gk(u's308_sh')
assert [occ(QUOT[i], u'308') for i in range(NSRC)] == gk(u's308_quot')
S3SH = [sum(occ(x, u'308') for x in L[i] if is_shell(x)) for i in range(NSRC)]
assert S3SH == gk(u's308_shell')
assert gk(u's308_raw') == gk(u's308_fold') == gk(u's308_quot')
assert sum(gk(u's308_raw')) - sum(gk(u's308_sh')) == sum(S3SH)
for w, kk in ((u'302', u'num_sec_302'), (u'307', u'num_sec_307'), (u'308', u'num_sec_308'),
              (u'GET', u'num_get_word'), (u'POST', u'num_post_word')):
    assert [occ(QUOT[i], w) for i in range(NSRC)] == gk(kk)
assert [len(re.findall(u'(?<![0-9])30[0-9](?![0-9])', QUOT[i])) for i in range(NSRC)] == gk(u'num_status_digits')
assert [len(re.findall(u'RFC[ ]?[0-9]{4}', T[i])) for i in range(NSRC)] == gk(u'num_rfc_refs')

# ---------- 抬头动作字段 ⇎ 年份 ⇎ 引用三式 ----------
def hdr_ids(t, field):
    m = re.search(u'(?m)^' + field + u':[ ]*(.+)$', t)
    if not m:
        return frozenset()
    return frozenset(int(x) for x in re.findall(u'[0-9]{3,5}', m.group(1).split(u'  ')[0]))


OBS = [hdr_ids(T[i], u'Obsoletes') for i in range(NSRC)]
UPD = [hdr_ids(T[i], u'Updates') for i in range(NSRC)]
assert [sorted(s) for s in OBS] == gk(u'obs_ids') and [sorted(s) for s in UPD] == gk(u'upd_ids')
assert [len(s) for s in OBS] == gk(u'obs_n') and [len(s) for s in UPD] == gk(u'upd_n')
assert sorted(set().union(*[set(s) for s in OBS + UPD])) == gk(u'target_ids')
MON = u'January|February|March|April|May|June|July|August|September|October|November|December'
YY = []
for i in range(NSRC):
    got = (None, None)
    for x in L[i][:60]:
        m = re.search(u'(%s)[ ]+([0-9]{4})' % MON, x.strip())
        if m:
            got = (int(m.group(2)), m.group(1))
            break
    YY.append(got)
assert [y for y, _ in YY] == gk(u'years') and [m for _, m in YY] == gk(u'months')
assert gk(u'year_inversions') == len([1 for a in range(NSRC) for b in range(a + 1, NSRC)
                                      if YY[a][0] > YY[b][0]]) == 0
CITE = {}
for n in (u'1945', u'2068', u'2616', u'2817', u'7231', u'7232', u'7538', u'9110', u'7230', u'7235'):
    CITE[u'sp_' + n] = [occ(T[i], u'RFC ' + n) for i in range(NSRC)]
    CITE[u'hy_' + n] = [occ(T[i], u'RFC-' + n) for i in range(NSRC)]
    CITE[u'tk_' + n] = [occ(T[i], u'RFC' + n) for i in range(NSRC)]
    CITE[u'al_' + n] = [CITE[u'sp_' + n][i] + CITE[u'hy_' + n][i] + CITE[u'tk_' + n][i]
                        for i in range(NSRC)]
    CITE[u'br_' + n] = [occ(T[i], u'[RFC' + n + u']') for i in range(NSRC)]
for k in CITE:
    assert CITE[k] == gk(u'cite_' + k), k
assert gk(u'cite_self') == [CITE[u'al_' + LBL[i]][i] for i in range(NSRC)]
assert gk(u'cite_forms_close') == [len(re.findall(u'RFC[ -]?' + LBL[i], T[i]))
                                   - CITE[u'al_' + LBL[i]][i] for i in range(NSRC)] == [0] * 4

# ---------- ⑥ 长行池(位掩码) ----------
RAWS = []
POOL = []
for i in range(NSRC):
    d = {}
    for x in SH[i]:
        n = pnorm(x)
        if len(n) >= 40:
            d.setdefault(n, set()).add(x)
    POOL.append(set(d))
    RAWS.append(d)
MASK = {}
for i in range(NSRC):
    for a in POOL[i]:
        MASK[a] = MASK.get(a, 0) | (1 << i)
POP = lambda m: bin(m).count(u'1')
TIERK = [0] * 4
for a, m in MASK.items():
    TIERK[POP(m) - 1] += 1
assert TIERK == gk(u'pool_tier') and len(MASK) == gk(u'pool_n')
PAIRS = list(itertools.combinations(range(NSRC), 2))
SHARE = [len([a for a, m in MASK.items() if (m >> i) & 1 and (m >> j) & 1]) for i, j in PAIRS]
BYTE = [len([a for a, m in MASK.items() if (m >> i) & 1 and (m >> j) & 1
             and any(x in RAWS[j][a] for x in RAWS[i][a])]) for i, j in PAIRS]
NORMO = [SHARE[x] - BYTE[x] for x in range(6)]
assert [SHARE, BYTE, NORMO] == [gk(u'pair_share'), gk(u'pair_byte'), gk(u'pair_norm_only')]
assert sum(SHARE) == sum(BYTE) + sum(NORMO)
mx = max(SHARE)
assert mx == gk(u'pair_max') and SHARE.index(mx) == gk(u'pair_max_idx')
assert [BYTE[SHARE.index(mx)], NORMO[SHARE.index(mx)]] == [gk(u'pair_max_byte'), gk(u'pair_max_norm_only')]
INC = [sum(len(POOL[i]) for i in range(NSRC)),
       sum(POP(m) * (POP(m) - 1) // 2 for m in MASK.values()),
       sum(POP(m) * (POP(m) - 1) * (POP(m) - 2) // 6 for m in MASK.values()),
       len([m for m in MASK.values() if POP(m) == 4])]
assert INC == gk(u'pool_incl')
assert len(MASK) == INC[0] - INC[1] + INC[2] - INC[3] == gk(u'union_incl')
assert gk(u'union_close') == gk(u'pool_n') - gk(u'union_incl') == 0
assert sorted([a for a, m in MASK.items() if POP(m) >= 3]) == gk(u's3_examples')
AX = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
NOS = 0
for a, m in MASK.items():
    if POP(m) < 2:
        continue
    xs = set()
    for i in range(NSRC):
        if (m >> i) & 1:
            xs |= RAWS[i][a]
    if len(xs) < 2:
        continue
    NOS += 1
    o, p = sorted(xs)[0], sorted(xs)[1]
    if len(o) == len(p) and o != p and all(x.lower() == y.lower() for x, y in zip(o, p)):
        AX[u'case'] += 1
    elif (u'-' in o) != (u'-' in p):
        AX[u'hyph'] += 1
    elif len(re.split(u' +', o.strip())) == len(re.split(u' +', p.strip())):
        AX[u'space'] += 1
    else:
        AX[u'multi'] += 1
assert AX == gk(u'axis_counts') and sum(AX.values()) == NOS == gk(u'norm_only_set') == gk(u'axis_total')
assert gk(u'axis_str') == u'⇎'.join(u'%s%d' % (a, AX[a]) for a in (u'case', u'hyph', u'space', u'multi'))
APM = {}
RAWC = [0] * NSRC
for i in range(NSRC):
    for x in SH[i]:
        n = pnorm(x)
        if len(n) >= 24 and re.search(u'[A-Za-z]', x):
            APM[n] = APM.get(n, 0) | (1 << i)
            RAWC[i] += 1
ATAG = [len([a for a, m in APM.items() if (m >> i) & 1]) for i in range(NSRC)]
assert [len(APM), RAWC, ATAG] == [gk(u'apool_n'), gk(u'apool_face_raw'), gk(u'apool_tag_n')]
assert [RAWC[i] - ATAG[i] for i in range(NSRC)] == gk(u'apool_dup')
AT = [len([m for m in APM.values() if POP(m) == n]) for n in range(1, 5)]
assert AT == gk(u'apool_tier')
assert sum(AT[n] * (n + 1) for n in range(4)) == gk(u'apool_weight') == sum(ATAG) == gk(u'apool_pairs')
assert max(len(a) for a in APM) == gk(u'apool_maxlen')

# ---------- ⑦⑧ 答句邻域窗 ⇎ 答句段界 ----------
BAND = 20
W, BL, PW_, PT = [], [], [], []
for i in range(NSRC):
    an = next(n for n, x in enumerate(L[i], 1) if ANSND[i] in x)
    lo, hi = max(1, an - BAND), min(len(L[i]), an + BAND)
    body = u'\n'.join(L[i][lo - 1:hi])
    outb = u'\n'.join(L[i][:lo - 1] + L[i][hi:])
    fb, fo = foldscan(body), foldscan(outb)
    d = {u'ans': an, u'start': lo, u'end': hi, u'rows': hi - lo + 1, u'chars': len(body),
         u'chars_out': len(outb),
         u'dig_in': len([c for c in body if c.isdigit()]),
         u'dig_out': len([c for c in outb if c.isdigit()])}
    for tr in (u'redirect', u'GET', u'POST', u'MUST'):
        d[tr] = occ(fb, tr)
        d[tr + u'_out'] = occ(fo, tr) + ovl(fo, tr)
    W.append(d)
for k in (u'ans', u'start', u'end', u'rows', u'chars', u'chars_out', u'dig_in', u'dig_out'):
    assert [d[k] for d in W] == gk(u'win_' + k), k
for tr in (u'redirect', u'GET', u'POST', u'MUST'):
    assert [d[tr] for d in W] == gk(u'win_' + tr + u'_in')
    assert [d[tr + u'_out'] for d in W] == gk(u'win_' + tr + u'_out')
assert gk(u'win_band') == BAND
assert [d[u'end'] - d[u'start'] + 1 for d in W] == gk(u'win_spans')
assert [W[i][u'dig_in'] + W[i][u'dig_out'] - DIGCH[i] for i in range(NSRC)] == gk(u'win_close_dig')


def blk(i, start, end):
    a = QUOT[i].find(start)
    b = QUOT[i].find(end, a)
    e = b + len(end)
    return foldscan(QUOT[i][a:e]), line_of(i, a), line_of(i, e - 1)


PB = [blk(i, s, e) for i, s, e in PINS]
PT = [p[0] for p in PB]
assert [p[1] for p in PB] == gk(u'blk_lo') and [p[2] for p in PB] == gk(u'blk_hi')
assert [p[2] - p[1] + 1 for p in PB] == gk(u'blk_rows')
assert [len(p[0]) for p in PB] == gk(u'blk_chars')
assert [len(p[0].split()) for p in PB] == gk(u'blk_words')
PW_ = [p[0].lower().split() for p in PB]
ONLY = [len(set(PW_[0]))] + [len(set(PW_[i]) - set(PW_[i - 1])) for i in range(1, NSRC)]
assert ONLY == gk(u'blk_only')
assert len(set(PW_[0]) & set(PW_[1])) == gk(u'blk_common_1')
assert [len(set(x)) for x in PW_] == gk(u'blk_vocab')
assert gk(u'w_row_close') == ONLY[1] + gk(u'blk_common_1') - len(set(PW_[1])) == 0


def suf(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def pre(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


assert suf(PW_[1], PW_[3]) == gk(u'suf_7231_9110') == 19
assert pre(PW_[1], PW_[3]) == gk(u'pre_7231_9110') == 19
assert PW_[1] == PW_[3] and PT[1] == PT[3]
assert suf(PW_[0], PW_[1]) == gk(u'suf_2616_7231') and pre(PW_[0], PW_[1]) == gk(u'pre_2616_7231') == 0
assert [tok(p, u'MUST') for p in PT] == gk(u'tone_must')
assert [tok(p, u'MAY') for p in PT] == gk(u'tone_may')
assert [tok(p, u'SHOULD') for p in PT] == gk(u'tone_should')
assert gk(u'tone_ledger') == [0] * 4


def ln_of(i, nd):
    return line_of(i, QUOT[i].find(nd))


GAPS = {}
for kk, nd in ((u'ln_note_2616', (0, u'RFC 1945 and RFC 2068 specify')),
               (u'ln_treat_2616', (0, u'treat 302 as if it were a 303')),
               (u'ln_hist_7231', (1, u'For historical reasons, a user agent MAY change')),
               (u'ln_mustnot_7231', (1, u'MUST NOT change the request method')),
               (u'ln_ind_7538', (2, u'The 308 (Permanent Redirect) status code indicates')),
               (u'ln_restricted_7538', (2, u'the use of status code 308 is restricted')),
               (u'ln_hist_9110', (3, u'For historical reasons, a user agent MAY change')),
               (u'ln_step_9110', (3, u'Change the request method according'))):
    GAPS[kk] = ln_of(*nd)
    assert GAPS[kk] == gk(kk), kk
assert gk(u'note_treat_gap') == GAPS[u'ln_treat_2616'] - GAPS[u'ln_note_2616'] == 2
assert gk(u'hist_mustnot_gap') == GAPS[u'ln_mustnot_7231'] - GAPS[u'ln_hist_7231']
assert gk(u'ind_restricted_gap') == GAPS[u'ln_restricted_7538'] - GAPS[u'ln_ind_7538']
assert gk(u'hist_step_gap') == GAPS[u'ln_step_9110'] - GAPS[u'ln_hist_9110'] < 0
assert gk(u'step_hist_abs') == abs(GAPS[u'ln_step_9110'] - GAPS[u'ln_hist_9110'])
M0 = ln_of(3, u'SHOULD resend the original request message with the following')
M1 = ln_of(3, u'A client SHOULD detect and intervene')
STEPS = [int(m.group(1)) for n, x in enumerate(L[3], 1) if M0 < n < M1
         for m in [re.match(u'^   ([0-9])\\.  ', x)] if m]
assert STEPS == gk(u'mod_step_nums') and len(STEPS) == gk(u'mod_steps') == 5
assert GAPS[u'ln_step_9110'] > M0 and GAPS[u'ln_step_9110'] < M1
assert occ(QUOT[3], u'is now deprecated') == gk(u'dep_all')
assert occ(QUOT[3], u'The 305 (Use Proxy) status code was defined in a previous version') == gk(u'dep_305_sent')

# ---------- ⑨ 锚的归类(串取自条目编码区, 归类只看折叠面) ----------
ET = io.open(ENT, encoding=u'utf-8').read()
ENCREG = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', ET, re.S).group(1)
AROW = [x.strip() for x in AUD.split(u'| B72 | ')[1].split(u'\n')[0].split(u'|')[:-1]]
assert len(ENCREG.replace(u'\n', u'')) == gk(u'enc_chars') == num(AROW[1]), AROW[:3]
assert len(set(ENCREG.replace(u'\n', u''))) == num(AROW[4]), AROW[:5]
BODY = ENCREG
ASTR = sorted(set(re.findall(u'⟨([^⟨⟩]+)⟩', BODY)))
FAN = [pnorm(t) for t in T]
HIT = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ASTR)
ASIN = len([a for a in ASTR if len(HIT[a]) == 1])
ACRO = len([a for a in ASTR if 2 <= len(HIT[a]) < NSRC])
AALL = len([a for a in ASTR if len(HIT[a]) == NSRC])
assert (len(re.findall(u'⟨', BODY)), ASIN, ACRO, AALL, len(ASTR)) == \
       (gk(u'anchor_total'), gk(u'anchor_single'), gk(u'anchor_cross'), gk(u'anchor_all4'),
        gk(u'anchor_distinct'))
TAGN = dict((t, BODY.count(u'⟦' + t + u'⟧')) for t in LBL)
assert [TAGN[t] for t in LBL] == [gk(u'tag_' + t) for t in LBL]
assert gk(u'checks') == len(ASTR) * NSRC == CH[u'checks']
assert gk(u'anchor_err') == 0

# ---------- ⑩ 转化指标: 编码区逐条现数, 列内并集不抄 ALL 行 ----------
GROW = []
ALLR = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        c = [x.strip() for x in l.split(u'|')[1:-1]]
        GROW.append(c)
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
ROWS = dict((c[0], c) for c in GROW)
assert len(ROWS) == len(GROW) and ALLR and len(ALLR) == len(GROW[0])
# 本表已列条目: 用 README 转化指标表的行界取, 不靠竖线枚数猜
SL0 = S.split(NL)
hh = [i for i, l in enumerate(SL0) if l.startswith(u'| entry | 编码字符 |')]
assert len(hh) == 1, hh
tt0 = [i for i in range(hh[0], len(SL0)) if SL0[i].startswith(u'| **合计（')]
assert len(tt0) == 1, tt0
LISTED0 = [l.split(u'|')[1].strip() for l in SL0[hh[0] + 2:tt0[0]]]
assert all(x.startswith(u'B') for x in LISTED0) and len(LISTED0) == 70 and u'B72' not in LISTED0
LISTED = sorted(LISTED0 + [u'B72'], key=lambda k: int(k[1:]))
UNACC = sorted(set(ROWS) - set(LISTED), key=lambda k: int(k[1:]))
ENCS, UNI, EN, DG = [], set(), [], []
for t in LISTED:
    f = glob.glob(u'corpus/babeltele/%s_*.md' % t)
    assert len(f) == 1, t
    tt = io.open(f[0], encoding=u'utf-8').read()
    m = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', tt, re.S)
    enc = m.group(1).replace(u'\n', u'')
    assert len(enc) == num(ROWS[t][2]), (t, len(enc), ROWS[t][2])
    assert len(set(enc)) == num(ROWS[t][5]), t
    ENCS.append(set(enc))
    EN.append(len(enc))
    DG.append(num(ROWS[t][1]))
UNI = set().union(*ENCS)
enc_all, dig_all = sum(EN), sum(DG)
assert enc_all + sum(num(ROWS[t][2]) for t in UNACC) == num(ALLR[2])
assert dig_all + sum(num(ROWS[t][1]) for t in UNACC) == num(ALLR[1])
DIG72, E72 = num(ROWS[u'B72'][1]), num(ROWS[u'B72'][2])
assert (DIG72, E72) == (3899, gk(u'enc_chars'))
CLOSEK = len([k for k in FP if u'close' in k])
DKEYS = len(set(re.findall(u"B72V\\('([a-z0-9_]+)'", json.dumps(DER, ensure_ascii=False))) & set(FP))
assert 0 < DKEYS < len(FP) and len(DER) == 176
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])

# ---------- 门槛表 B72 行 ----------
ST, FO, SD, QU4 = gk(u'sn_strict_docs'), gk(u'sn_fold_docs'), gk(u'sn_sh_docs'), gk(u'sn_quot_docs')
HEADROW = (u'| B72 | ' + fmt(E72) + u'（新建, 302 之后到底能不能把 POST 改成 GET 交四份 HTTP 一手规范各答一遍 '
           + str(gk(u'anchor_total')) + u' 处标注／' + str(gk(u'anchor_distinct'))
           + u' 个不同串（登记全命中, 单源 ' + str(gk(u'anchor_single')) + u' ⇎ 穿二三源 ' + str(gk(u'anchor_cross'))
           + u' ⇎ 四源全现 ' + str(gk(u'anchor_all4')) + u'——穿源的 ' + str(gk(u'anchor_cross'))
           + u' 枚是“同一处含混被四份文书各自重述”的那批跨行整句; 编码区 ' + fmt(E72) + u' 字符, 归属检查 '
           + str(gk(u'checks')) + u' 次, 错配 ' + str(gk(u'anchor_err')) + u'）: 四色锚位 '
           + u' ⇎ '.join(x + u' ⟦' + y + u'⟧' for x, y in zip(LBL, u'ABCD'))
           + u'; 答句四种（不许改写但实现都当 303 用 ⇎ 历史原因 MAY change ⇎ 另立 308 避开 ⇎ 收下注并写进编号清单）: '
           + u' ⇎ '.join(ANS) + u'; 四档阶梯（原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 剥引文折平）按文档读到 '
           + u'⇎'.join(map(str, ST)) + u' ／ ' + u'⇎'.join(map(str, FO)) + u' ／ '
           + u'⇎'.join(map(str, SD)) + u' ／ ' + u'⇎'.join(map(str, QU4)) + u' 枚（针表 '
           + str(gk(u'needle_n')) + u' 枚, 归各份 ' + u'⇎'.join(map(str, gk(u'needles_owned')))
           + u' 枚, 折行救回 ' + str(gk(u'fold_only_n')) + u' 枚（按份 ' + u'⇎'.join(map(str, FOWN))
           + u'）, 剥引文再多 ' + u'⇎'.join(map(str, gk(u'quot_minus_sh'))) + u' 枚（新增 '
           + str(gk(u'quot_only_n')) + u' 枚只在 9110: ' + gk(u'quot_only_str') + u'）, 摘壳档比折平档一粒不少（差 '
           + L4(gk(u'sh_minus_fold')) + u'）, 阶梯单调 ' + str(gk(u'ladder_monotone'))
           + u'）; 最宽档落空 ' + str(gk(u'dead_n')) + u' 枚 = 反向对照 ' + str(gk(u'neg_ctrl_n')) + u' 枚（合计命中 '
           + str(gk(u'neg_hit_widest')) + u'）+ 序列化对照 ' + str(gk(u'ser_n')) + u' 枚, 内容死针 '
           + str(gk(u'dead_nonneg')) + u' 枚; 判定轨两条并立: 正则字面 ⇎ 非重叠游标逐枚相等（'
           + str(gk(u're_eq_cur')) + u'）⇎ 重叠口径多出 ' + str(gk(u'overlap_extra')) + u' 枚为零; '
           + u'措辞六族（剥引文面现数）: 确认门 ' + L4(TIERQ[u'confirm_gate']) + u' ⇎ not allowed to change '
           + L4(TIERQ[u'not_allowed']) + u' ⇎ MAY change the request method ' + L4(TIERQ[u'may_change'])
           + u' ⇎ MUST NOT change the request method ' + L4(TIERQ[u'must_not_change'])
           + u' ⇎ does not allow changing ' + L4(TIERQ[u'not_allow_changing']) + u' ⇎ erroneously '
           + L4(TIERQ[u'erroneously']) + u'——六族合计折平 ' + L4(FT) + u' ⇎ 剥引文 ' + L4(QT) + u'（增益 '
           + L4(gk(u'tier_gain')) + u' 全落 9110, 与剥引文档新增针同账, 闭合 ' + str(gk(u'tier_sum_close'))
           + u'）; 确认门只在 2616（判定 ' + str(gk(u'confirm_gate_only_2616')) + u'）⇎ MAY change 恰在 7231⇎9110'
           + u'（判定 ' + str(gk(u'may_change_pair')) + u'）⇎ does not allow changing 只在中间两份（判定 '
           + str(gk(u'not_allow_changing_pair')) + u'）⇎ erroneously 只在首尾两份（判定 '
           + str(gk(u'erroneously_outer_pair')) + u'）; 序列化对照一枚: 带竖线那句折平面 '
           + str(gk(u'ser_fold_hit')) + u' 枚 ⇎ 剥引文面 ' + str(gk(u'ser_quot_hit')) + u' 枚, 而剥竖线后的同一句在剥引文面 '
           + str(gk(u'n_a9110_302_hist_may')[3]) + u' 枚（判定 ' + str(gk(u'ser_pair')) + u'）; '
           + u'竖线两尺: 折平面 ' + L4(BARF) + u' ⇎ 剥后 ' + L4(BARQ) + u' ⇎ 被剥 ' + L4(gk(u'bar_removed'))
           + u'（逐行剥前后各数一次同为 ' + L4(gk(u'bar_removed_line')) + u'）⇎ 含竖线行 ' + L4(gk(u'quot_line_n'))
           + u'——只有 9110 用竖线做引文块; 锚池 ' + fmt(gk(u'pool_n')) + u' 条分档 '
           + u'⇎'.join(map(fmt, gk(u'pool_tier'))) + u'（闭合 ' + str(gk(u'pool_tier_close')) + u'）⇎ 容斥闭合 '
           + str(gk(u'union_close')) + u'; 六对归一同形 ' + L4(SHARE) + u' ⇎ 逐字节 ' + L4(BYTE) + u' ⇎ 仅归一 '
           + L4(NORMO) + u', 最大一对 ' + gk(u'pair_max_lbl') + u' ' + fmt(gk(u'pair_max')) + u' 行（逐字节 '
           + fmt(gk(u'pair_max_byte')) + u' ⇎ 仅归一 ' + str(gk(u'pair_max_norm_only'))
           + u'）⇒ 9110 整段复用 7231 行文而只重排 ' + str(gk(u'pair_max_norm_only')) + u' 行; 写法分家四桶 '
           + gk(u'axis_str') + u'（轴账闭合 ' + str(gk(u'axis_close')) + u'）; 锚候选池 ' + fmt(gk(u'apool_n'))
           + u' 条按标签 ' + L4(ATAG) + u' ⇎ 按份数 ' + u'⇎'.join(map(fmt, AT)) + u'（两本账闭合 '
           + str(gk(u'apool_tag_close')) + u' ⇎ ' + str(gk(u'apool_tier_close')) + u'）; 义务语气四轨: MUST 全计 '
           + L4(UP[u'MUST']) + u' ⇎ 裸 MUST ' + L4(gk(u'must_bare')) + u' ⇎ MUST NOT ' + L4(UPN[u'MUST NOT'])
           + u' ⇎ MAY ' + L4(UP[u'MAY']) + u' ⇎ SHOULD ' + L4(UP[u'SHOULD']) + u' ⇎ SHOULD NOT '
           + L4(UPN[u'SHOULD NOT']) + u' ⇎ MAY NOT ' + L4(UPN[u'MAY NOT']) + u'（大写账 ' + L4(gk(u'up_ledger'))
           + u'）⇎ 小写 must ' + L4(LO[u'MUST']) + u' ⇎ 不分大小写 ' + L4(CI[u'MUST']) + u'（大小写账 '
           + L4(gk(u'case_ledger')) + u'）——7538 只管一枚状态码, 大写 MUST 仅 ' + str(UP[u'MUST'][2])
           + u' 枚 ⇎ 2616 ' + str(UP[u'MUST'][0]) + u' 枚; method ' + L4(gk(u'method_word')) + u' ⇎ redirect '
           + L4(gk(u'redirect_word')) + u' 枚; 30x 小节数 ' + L4(gk(u'sec_heads')) + u'（判定 '
           + str(gk(u'code_n_desc')) + u'=0 即按现读成立）⇎ 号码清单 ' + u' ⇎ '.join(u'[' + u' '.join(c) + u']'
                                                                                       for c in gk(u'codes'))
           + u' ⇎ 并集 ' + str(len(gk(u'code_union'))) + u' 枚: 304 被 7231 挪走（判定 '
           + str(gk(u'304_absent_in_7231')) + u'）⇎ 308 只活在 7538⇎9110（判定 ' + str(gk(u'308_only_7538_9110'))
           + u'）; 数字 308 四档面 ' + L4(gk(u's308_raw')) + u' ⇎ ' + L4(gk(u's308_fold')) + u' ⇎ '
           + L4(gk(u's308_sh')) + u' ⇎ ' + L4(gk(u's308_quot')) + u', 摘壳少的 ' + str(sum(gk(u's308_raw')) - sum(gk(u's308_sh')))
           + u' 枚全在壳行（判定 ' + str(gk(u'shell_308_only_7538')) + u'——7538 把争议号码本身印成页眉）; '
           + u'游标另数 302 ' + L4(gk(u'num_sec_302')) + u' ⇎ 307 ' + L4(gk(u'num_sec_307')) + u' ⇎ 3xx 全族串 '
           + L4(gk(u'num_status_digits')) + u'; 答句段: 行界 ' + L4(gk(u'blk_lo')) + u'.. ' + L4(gk(u'blk_hi'))
           + u'（行数 ' + L4(gk(u'blk_rows')) + u'）⇎ 段字符 ' + L4(gk(u'blk_chars')) + u' ⇎ 段词 ' + L4(gk(u'blk_words'))
           + u'——7231 段与 9110 段逐词相等（共尾 ' + str(gk(u'suf_7231_9110')) + u' 词 ⇎ 共头 '
           + str(gk(u'pre_7231_9110')) + u' 词 ⇎ 词序判定 ' + str(gk(u'blk_same_7231_9110')) + u' ⇎ 字符判定 '
           + str(gk(u'blk_identical_chars')) + u'）⇎ 2616 段与 7231 段只共尾 ' + str(gk(u'suf_2616_7231'))
           + u' 词、共头 ' + str(gk(u'pre_2616_7231')) + u' 词; 段内词集账闭合 ' + str(gk(u'w_row_close'))
           + u' ⇎ 段内语气 ' + L4(gk(u'tone_up')) + u' 枚大写（MAY ' + L4(gk(u'tone_may')) + u'）; 9110 还把改写写成编号清单: '
           + u'顶层 ' + str(gk(u'mod_steps')) + u' 条 ' + u','.join(str(x) for x in gk(u'mod_step_nums'))
           + u'（顺序判定 ' + str(gk(u'mod_step_seq')) + u'）, 改写那条落在区间内（判定 '
           + str(gk(u'mod_step_has_rewrite')) + u'）⇎ 清单比历史原因句早 ' + str(gk(u'step_hist_abs'))
           + u' 行（判定 ' + str(gk(u'step_before_hist')) + u'）⇎ 7231 次序相反, 约束句晚 ' + str(gk(u'hist_mustnot_gap'))
           + u' 行（判定 ' + str(gk(u'hist_after_7231')) + u'）⇎ 7538 的另立句与限制句隔 ' + str(gk(u'ind_restricted_gap'))
           + u' 行; 谁废止谁现读: Obsoletes ' + u' ⇎ '.join(str(sorted(s)) for s in OBS) + u' ⇎ Updates '
           + u' ⇎ '.join(str(sorted(s)) for s in UPD) + u', 对象并集 ' + str(gk(u'target_n'))
           + u' 枚, 链 2068←2616←7231←9110 判定 ' + str(gk(u'obs_chain')) + u' ⇎ 7538 只废止自己的草案期号判定 '
           + str(gk(u'7538_obsoletes_own_draft')) + u'; 标题页年份 ' + L4(gk(u'years')) + u'（'
           + u'⇎'.join(gk(u'months')) + u', 倒序 ' + str(gk(u'year_inversions')) + u' 处 ⇎ 年距 '
           + u'⇎'.join(str(x) for x in gk(u'year_gaps')) + u'）; 引用三式逐份归零（闭合 ' + L4(gk(u'cite_forms_close'))
           + u'）: 自指 ' + L4(gk(u'cite_self')) + u' ⇎ 2616 被 ' + L4(gk(u'cite_al_2616')) + u' ⇎ 7231 被 '
           + L4(gk(u'cite_al_7231')) + u' ⇎ 括号式 [RFC7231] ' + L4(gk(u'cite_br_7231')) + u' 枚; 7231→9110 读 '
           + str(gk(u'cite_dir_7231_to_9110')) + u' 枚 ⇎ 反向 ' + str(gk(u'cite_dir_9110_to_7231'))
           + u' 枚; 两遍壳账不横比而按行分解: 本遍 ' + L4(gk(u'shell_n')) + u' ⇎ 采集 ' + L4(PICKN) + u' ⇎ 同判 '
           + L4(gk(u'shell_both')) + u' ⇎ 只有本遍判壳 ' + L4(gk(u'shell_mk_only')) + u' 行全是抬头字段行 ⇎ 只有采集判壳 '
           + L4(gk(u'shell_pick_only')) + u' 行全是缩进后的“RFC 四位数+空格”正文句（判定 '
           + str(gk(u'pick_overstrip_only_2616')) + u'）⇎ 差 ' + L4(gk(u'shell_diff'))
           + u'; 针表两遍不同名分（采集 ' + str(gk(u'needle_table_pick')) + u' ⇎ 建条目 ' + str(gk(u'needle_table_mk'))
           + u'）故不横比; 同数共键 ' + str(len(DER)) + u' 枚算式／' + str(gk(u'x_ident_n'))
           + u' 条面内恒等式（标量闭账 ' + str(gk(u'scalar_clos_n')) + u' 项通过 ' + str(gk(u'scalar_clos_sum'))
           + u' ⇎ 含 close 的键 ' + str(CLOSEK) + u' 枚其中逐份清单 ' + str(gk(u'list_clos_n')) + u' 枚）, 扁平契约 '
           + str(len(FP)) + u' 枚键; 五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对锚逐字复核, 采集侧同定义标量 '
           + str(gk(u'pick_agree')) + u'/' + str(gk(u'pick_agree')) + u' 枚相符（壳账与针表按行分解, 不参与横比）; '
           + u'工具侧 atomcheck 的 SRC 表未登记本条, 四份纯文本面的逐字性由门槛侧 ' + str(gk(u'checks'))
           + u' 次归属检查承担（逐字命中 ' + str(gk(u'anchor_total')) + u' 处 ⇎ 错配 ' + str(gk(u'anchor_err')) + u'） |')

# ---------- 语料表 B72 行 ----------
C72 = (u'| B72 | ' + u' ⇎ '.join(
    SHW[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／面内码位 ' + fmt(gk(u'chars')[i])
    + u'／行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i]) + u'（换页符 ' + str(FFC[i]) + u' 枚，独占整行 ' + str(EF[i])
    + u' 行）／最长行 ' + str(ML[i]) + u' 列／答句 ' + ANS[i] + u'／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i])
    + u'／BOM ' + str(BOM[i]) + u'）' for i in range(NSRC))
           + u' | 四份答同一个问题 ⇒ 2616 把确认门写在正文（“MUST NOT automatically redirect” '
             + str(TIERQ[u'confirm_gate'][0]) + u' 枚）、又在同节注里自认实现都当 303 用（“treat 302 as if it were a 303”距定义句 '
             + str(gk(u'note_treat_gap')) + u' 行），一个数字上限都不给 ⇎ 7231 删掉确认门（该句面上 '
             + str(TIERQ[u'confirm_gate'][1]) + u' 枚）换成历史原因 MAY（' + str(TIERQ[u'may_change'][1])
             + u' 枚）并把约束挪给 307（“MUST NOT change the request method”晚 ' + str(gk(u'hist_mustnot_gap'))
             + u' 行）⇎ 7538 不争 302、另立 308（全份只有 ' + str(gk(u'sec_heads')[2]) + u' 个 30x 小节 ⇎ 大写 MUST '
             + str(UP[u'MUST'][2]) + u' 枚），义务写成散文 ought to ⇎ 9110 收下 7231 那段注且逐词不动（共尾共头各 '
             + str(gk(u'suf_7231_9110')) + u' 词），差别只在序列化：它被楔进竖线引文块（'
             + str(gk(u'quot_only_n')) + u' 枚针只在剥引文档读到）, 另给叙述式 converged 与编号清单第 '
             + str(gk(u'mod_steps')) + u' 步两轨（清单比注早 ' + str(gk(u'step_hist_abs')) + u' 行）；'
             + u'四档阶梯在本条的空转全在逐行档（' + u'⇎'.join(map(str, ST)) + u' 枚），'
             + str(gk(u'fold_only_n')) + u' 枚整句被行界劈开靠折行救回，而摘壳档一粒不多（差 '
             + L4(gk(u'sh_minus_fold')) + u'），只有剥引文竖线再多 ' + str(gk(u'quot_minus_sh')[3])
             + u' 枚——这是本条多立第四档的理由 |' + NL)

# ---------- 判词段 ----------
PARA = (u'**B72 问的是收到 302 之后到底能不能把 POST 改成 GET，四份 HTTP 一手规范给出四种答法**：'
        + u' ⇎ '.join(SHW[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
                      + u'／非空行 ' + fmt(NB[i]) + u'／换页符 ' + str(FFC[i]) + u' 枚（独占整行 ' + str(EF[i])
                      + u' 行）／答句 ' + ANS[i] + u'／非 ASCII ' + str(NA[i]) + u'／BOM ' + str(BOM[i]) + u'）'
                      for i in range(NSRC))
        + u'——前三份逐字节纯 ASCII 且都带换页符，只有 9110 零枚换页符 ⇎ 一枚 BOM ⇎ ' + str(NA[3])
          + u' 枚非 ASCII（取变音符），字节−码位差 ' + L4(gk(u'byte_cp_delta')) + u' ⇎ 非 ASCII 加字节 '
          + L4(gk(u'nonascii_extra')) + u' 逐份相等，纯 ASCII 面 ' + str(gk(u'ascii_all')) + u' 份；换页符 '
          + L4(FFC) + u' 枚且全部独占整行（' + L4(EF) + u' 行），建条目侧另有一档按 strip()==FF 判——strip 先吃掉换页符本身，该档恒零（'
          + L4(gk(u'ff_only')) + u'，口径陷阱如实记）。四种答法不是措辞差异而是裁决差异：2616 把确认门写进正文（“MUST NOT '
          u'automatically redirect” ' + str(TIERQ[u'confirm_gate'][0]) + u' 枚）又自认“实现都当 303 用”（同节注，距定义句 '
          + str(gk(u'note_treat_gap')) + u' 行）⇎ 7231 面上该句 ' + str(TIERQ[u'confirm_gate'][1])
          + u' 枚——确认门整句消失，换成“For historical reasons, a user agent MAY change the request method”（'
          + str(TIERQ[u'may_change'][1]) + u' 枚），同时给 307 立“MUST NOT change the request method”（'
          + str(TIERQ[u'must_not_change'][1]) + u' 枚，晚 ' + str(gk(u'hist_mustnot_gap'))
          + u' 行）⇎ 7538 不改 302 而是另立 308，把话头转成否定式“it does not allow changing the request method from POST to GET”（'
          + str(TIERQ[u'not_allow_changing'][2]) + u' 枚），全份只有 ' + str(gk(u'sec_heads')[2]) + u' 个 30x 小节 ⇎ 大写 MUST '
          + str(UP[u'MUST'][2]) + u' 枚，义务多写成散文 ought to ⇎ 9110 收下 7231 的注（段逐词相等：共尾共头各 '
          + str(gk(u'suf_7231_9110')) + u' 词 ⇎ 字符全同判定 ' + str(gk(u'blk_identical_chars'))
          + u'），却又给叙述式“converged on changing the method to GET”与编号清单第 ' + str(gk(u'mod_steps'))
          + u' 步“Change the request method according to the redirecting status code”两轨（清单比注早 '
          + str(gk(u'step_hist_abs')) + u' 行，判定 ' + str(gk(u'step_before_hist')) + u'）。'
          u'四档阶梯（原面 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 剥引文折平）读到 ' + u'⇎'.join(map(str, ST)) + u' ／ '
          + u'⇎'.join(map(str, FO)) + u' ／ ' + u'⇎'.join(map(str, SD)) + u' ／ ' + u'⇎'.join(map(str, QU4))
          + u' 枚——' + str(gk(u'needle_n')) + u' 枚在册针里只有 ' + str(sum(ST)) + u' 枚能在单行读全，'
          + str(gk(u'fold_only_n')) + u' 枚靠折行救回，剥引文档净增 ' + str(gk(u'quot_only_n'))
          + u' 枚且全在 9110（它把注排成 `| *Note:* …` 引文块，竖线楔在句中）；摘壳档比折平档一粒不少（差 '
          + L4(gk(u'sh_minus_fold')) + u'）——本条必需的是第四档转义层而非剥页壳。谁抄谁可量：归一同形长行池最大一对 '
          + gk(u'pair_max_lbl') + u' ' + fmt(gk(u'pair_max')) + u' 行里 ' + fmt(gk(u'pair_max_byte'))
          + u' 行逐字节同形 ⇎ 只有 ' + str(gk(u'pair_max_norm_only')) + u' 行被重新 wrap（配对闭合 '
          + str(gk(u'pair_close')) + u' ⇎ 容斥闭合 ' + str(gk(u'union_close')) + u'）⇒ 9110 对 7231 是行级搬运；'
          u'写法分家四桶 ' + gk(u'axis_str') + u'——分家几乎全在空格与大小写上。血统可查：Obsoletes '
          + u' ⇎ '.join(str(sorted(s)) for s in OBS) + u' ⇎ 对象并集 ' + str(gk(u'target_n')) + u' 枚 ⇎ 链判定 '
          + str(gk(u'obs_chain')) + u'（9110 的清单里没有 2616，它隔着 7231 吃下 2616 的血统）；标题页年份 '
          + L4(gk(u'years')) + u'（倒序 ' + str(gk(u'year_inversions')) + u' 处）⇒ 这条里“取最新”不会被年份骗，'
          u'只会被“最新那份把它改成什么”骗。竖线是这一条的转义层而非噪声：折平面 ' + L4(BARF) + u' 枚 ⇎ 剥后 ' + L4(BARQ)
          + u' 枚 ⇎ 被剥 ' + L4(gk(u'bar_removed')) + u' 枚（与逐行尺 ' + L4(gk(u'bar_removed_line'))
          + u' 同值），含竖线行 9110 ' + str(gk(u'quot_line_n')[3]) + u' 行 ⇎ 其余三份 '
          + u'⇎'.join(str(gk(u'quot_line_n')[i]) for i in range(3)) + u' 行——前三份的竖线是 ABNF/表格边框。'
          u'号码名分也可数：30x 小节 ' + L4(gk(u'sec_heads')) + u' ⇎ 304 只在 2616⇎9110 的清单（7231 挪走，判定 '
          + str(gk(u'304_absent_in_7231')) + u'）⇎ 308 只在 7538⇎9110（判定 ' + str(gk(u'308_only_7538_9110'))
          + u'）；数字 308 在摘壳档少 ' + str(sum(gk(u's308_raw')) - sum(gk(u's308_sh')))
          + u' 枚且全在 7538 的页眉（判定 ' + str(gk(u'shell_308_only_7538'))
          + u'）——页眉把争议号码本身印成 running header。语气换代不按时钟走：MUST 全计 ' + L4(UP[u'MUST'])
          + u' ⇎ MAY ' + L4(UP[u'MAY']) + u' ⇎ SHOULD ' + L4(UP[u'SHOULD']) + u' ⇎ MAY NOT '
          + L4(UPN[u'MAY NOT']) + u'（四份都不用 MAY NOT）。答句邻域按 ±' + str(gk(u'win_band')) + u' 行带切，'
          u'四轨（redirect ⇎ GET ⇎ POST ⇎ MUST）带内外分账，数字符带内+带外=全篇闭合 ' + str(gk(u'win_close_sum'))
          + u'（窗 ' + L4(gk(u'win_spans')) + u' 行）。门槛侧 ' + str(len(DER)) + u' 枚算式／' + str(gk(u'x_ident_n'))
          + u' 条面内恒等式（标量 ' + str(gk(u'scalar_clos_n')) + u' 项通过 ' + str(gk(u'scalar_clos_sum'))
          + u'），扁平契约 ' + str(len(FP)) + u' 枚键由第四 ⇎ 第五套实现逐枚复测；其中 ' + str(DKEYS)
          + u' 枚进得了 DERIV 算式 ⇎ 余下 ' + str(len(FP) - DKEYS) + u' 枚是形状清单、字符串表与窗口切片；' + str(len(ASTR))
          + u' 枚不同锚串按折叠面重分类 单源 ' + str(ASIN) + u' ⇎ 穿源 ' + str(ACRO) + u' ⇎ 四源 ' + str(AALL)
          + u'，与门槛登记口径一致。')

# ---------- 落盘: 定点插入, 不整体重写 ----------
assert S.count(u'**B72 问的是') == 0
assert S.count(u'| B72 |') == 0


def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:60])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


def sub(old, new, s, cnt=1):
    assert s.count(old) == cnt, (u'锚点不唯一', old[:60], s.count(old))
    return s.replace(old, new)


S = after(S, u'**B71 问的是一张 TLS 会话恢复票据到底能活多久', PARA + NL + NL)
S = after(S, u'| B71 | 7 298（新建,', HEADROW + NL)
S = after(S, u'| B71 | `raw/tlsTicket/rfc4507.txt`', C72)

L = S.split(NL)
h = [i for i, l in enumerate(L) if l.startswith(u'| entry | 编码字符 |')]
assert len(h) == 1, h
tot = [i for i in range(h[0], len(L)) if L[i].startswith(u'| **合计（')]
assert len(tot) == 1, tot
T0 = tot[0]
present = [l.split(u'|')[1].strip() for l in L[h[0] + 2:T0]]
assert present == LISTED0, present[:3]
missing = [k for k in sorted(ROWS, key=lambda k: int(k[1:])) if k not in present]
assert missing[0] == u'B72' and set(missing) <= {u'B72', u'B73'}, missing
NEWROW = (u'| %s | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
          % (u'B72', fmt(E72), ROWS[u'B72'][3], ROWS[u'B72'][4], ROWS[u'B72'][5], ROWS[u'B72'][7]))
L[T0:T0] = [NEWROW]
UNIQ_LISTED = len(UNI)
OLD = L[T0 + 1]
cells = OLD.split(u'|')
assert cells[2].strip().startswith(u'**4'), cells[2]
cells[1] = u' **合计（' + str(len(LISTED)) + u' 条）** '
cells[2] = u' **' + fmt(enc_all) + u'** '
cells[3] = (u' **%.1f%%**（摘要段合计 ' % (100.0 * enc_all / dig_all) + fmt(dig_all)
            + u'，本遍补记的一枚为 ' + fmt(E72) + u' 编码／' + fmt(DIG72)
            + u' 摘要；两列合计与本表所列 ' + str(len(LISTED)) + u' 条一致，故不取 audit 的 ALL 行'
              + u'（它多含已接线而未在本表记账的 ' + (u'⇎'.join(UNACC) if UNACC else u'无') + u'：编码 '
              + fmt(num(ALLR[2]) - enc_all) + u' ⇎ 摘要 ' + fmt(num(ALLR[1]) - dig_all)
              + u'）；唯一码点那格由本遍按 audit 的编码区正则逐条现数取列内并集，逐条与 audit 现算值对拍） ')
cells[5] = u' **%s** ' % fmt(UNIQ_LISTED)
assert len(cells) == len(OLD.split(u'|')), (len(cells), len(OLD.split(u'|')))
L[T0 + 1] = u'|'.join(cells)
NOTE = [i for i, l in enumerate(L) if l.startswith(u'（B54 起的 ') and u'机械行' in l]
assert len(NOTE) == 1, NOTE
L[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与'
              u'字符/语义单元五格, 不重写各条的口径注; 本遍再直补 B72 一枚, 合计行只列本表已记账条目, '
              u'唯一码点由本遍逐条现数取并集, 不再抄 ALL 行。）'
              % len([x for x in present + [u'B72'] if int(x[1:]) >= 54]))
S = NL.join(L)

S = sub(u'共 **70 条**（`babeltele/B01..B65、B67..B71`, 本遍补上 B71 的四处记账行, 合计按 audit 当下输出重算）',
        u'共 **71 条**（`babeltele/B01..B65、B67..B72`, 本遍补上 B72 的四处记账行, 合计按本表所列条目现算, '
        u'唯一码点逐条现数）', S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（70 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（71 条）', S)
PV = [l for l in S.split(NL) if u'条语料／' in l and u'推导全部通过' in l]
assert len(PV) == 1, PV
i0 = PV[0].find(u'当前 **')
j = PV[0].find(u'）', PV[0].find(u'audit 自报', i0))
while PV[0][j + 1:j + 2] == u'）':
    j += 1
S = S[:S.find(PV[0]) + i0] + (u'当前 **71 条语料／' + str(PROOFS) + u' 条**推导全部通过（audit 自报“已机检的推导 '
                              + str(PROOFS) + u' 条”）') + S[S.find(PV[0]) + j + 1:]

assert S.count(u'python -X utf8 corpus/_fill71.py') == 1
S = after(S, u'python -X utf8 corpus/_fill71.py',
          u'python -X utf8 corpus/_mkB72.py                    # 建条目(前半, 与 _mk72emit.py 同场 exec): 扁平契约 '
          + str(len(FP)) + u' 枚键／恒等式 ' + str(gk(u'x_ident_n')) + u' 条 ⇎ DERIV ' + str(len(DER))
          + u' 枚算式, 非重叠游标 ⇎ 正则字面轨 ⇎ 集合代数三机制, 采集侧同定义标量 ' + str(gk(u'pick_agree'))
          + u'/' + str(gk(u'pick_agree')) + u' 枚相符(壳账与针表按行分解, 不横比)' + NL)
S = after(S, u'python -X utf8 corpus/_mkB72.py',
          u'python -X utf8 corpus/_mkdigest3.py B72 <entry> 2616 corpus/raw/httpRedir/rfc2616.txt 160 260 '
          u'7231 corpus/raw/httpRedir/rfc7231.txt 160 260 7538 corpus/raw/httpRedir/rfc7538.txt 160 260 '
          u'9110 corpus/raw/httpRedir/rfc9110.txt 160 260   # 四源分节摘要(' + fmt(DIG72) + u' 字符, '
          + str(gk(u'anchor_total')) + u'/' + str(gk(u'anchor_total')) + u' 锚全命中)' + NL)
S = after(S, u'python -X utf8 corpus/_mkdigest3.py B72',
          u'python -X utf8 corpus/_wire72.py                    # 幂等接线: SRC/ATOM/SCAN(审计器侧第三套实现)/DERIV/'
          u'B72V 进 audit.py, 落盘前复跑 ' + str(len(FP)) + u' 枚扁平键 ⇎ ' + str(len(DER)) + u' 枚算式' + NL)
S = after(S, u'python -X utf8 corpus/_wire72.py',
          u'python -X utf8 corpus/_fill72.py                    # 第四遍: 四档阶梯⇎手写剥引文⇎位集代数⇎词轨各重导一次, '
          + str(gk(u'x_ident_n')) + u' 条恒等式现算归零后写回 ⛓解读注（21 行复测表 ⇎ 复算 ' + str(len(FP))
          + u' 键对账 0 不符 ⇎ 独有 0 枚）' + NL)

io.open(u'corpus/README.md', u'w', encoding=u'utf-8', newline=NL).write(S)
json.dump(dict(entries=len(LISTED), enc=enc_all, dig=dig_all, proofs=PROOFS, b72_enc=E72, b72_dig=DIG72,
               bytes=BS, lines=LN, nonblank=NB, formfeed_only=EF, ff_occ=FFC, cr=CR, nonascii=NA, bom=BOM,
               maxlen=ML, strict=ST, fold=FO, sh=SD, quot=QU4, fold_only_n=gk(u'fold_only_n'),
               fold_only_own=FOWN, quot_only_n=gk(u'quot_only_n'), up=UP[u'MUST'], low=LO[u'MUST'],
               ci=CI[u'MUST'], bar_fold=BARF, bar_quot=BARQ, shell_pick=PICKN, s308_shell=S3SH,
               close_keys=CLOSEK, uniq_listed=UNIQ_LISTED, unaccounted=UNACC, keys=len(FP),
               ident=gk(u'x_ident_n'), pairs=SHARE, pairs_byte=BYTE, pool_tier=TIERK,
               anchors=len(ASTR), listed=LISTED),
          io.open(u'corpus/_b72readme.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（' + str(len(LISTED)) + u' 条）编码 ' + fmt(enc_all) + u' ⇎ 摘要 ' + fmt(dig_all)
      + u' ⇎ 保留 %.1f%%' % (100.0 * enc_all / dig_all) + u' ｜ 唯一码点(列内并集) ' + fmt(UNIQ_LISTED)
      + u' ｜ 未记账 ' + (u'⇎'.join(UNACC) if UNACC else u'无') + u' ｜ 推导 ' + str(PROOFS)
      + u' 条 ｜ B72 行 ' + fmt(E72) + u'／' + fmt(DIG72) + u' ｜ 锚 ' + str(gk(u'anchor_total'))
      + u' 处⇎错配 ' + str(gk(u'anchor_err')) + u' ｜ 四档阶梯 ' + u'⇎'.join(map(str, ST)) + u'／'
      + u'⇎'.join(map(str, FO)) + u'／' + u'⇎'.join(map(str, SD)) + u'／' + u'⇎'.join(map(str, QU4))
      + u' ｜ 剥引文档新增 ' + str(gk(u'quot_only_n')) + u' 枚 ｜ 逐份字节 ' + u'⇎'.join(map(fmt, BS)))
