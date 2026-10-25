# -*- coding: utf-8 -*-
"""B82 的第五遍复测: 采集侧(_pick82.py)⇎ 建条目侧(_mkB82.py + _mk82emit.py)⇎ 门槛侧(audit.py::_b82_scan)
换算法不换定义, 现算后把 ⛓解读注 写进条目。本遍是第三套实现, 十三处换机制:
①行界: `re.compile('\\n').split`(正则引擎切) ⇎ 建条侧 `str.split(NL)` ⇎ 采集侧游标环; 换行枚数走
  `bytes.count(0x0a)`(在字节上数, 与解码后的字符串数各自一遍), 码位数走逐字符 `ord` 累加(建条侧是 `len`);
②折平: `re.finditer('\\S+')` 取词跨度再 `join`(建条侧是 `re.split('\\s')` 过滤空段 ⇎ `str.split()` 无参档);
  归一尺 p3 与建条侧 pnorm ⇎ fold 两轨同时逐份对拍;
③字面针: `str.count`(非重叠, C 档) ⇎ `finditer('(?=针)')`(重叠) ⇎ 建条侧 `findall(re.escape)` ⇎ 采集侧游标 find;
④整词尺: 预先把全串翻成“是否字母”的布尔表, 命中后查表读左右邻(建条侧 `ub_re` 是断言正则、`ub` 是邻居字符手扫,
  采集侧是邻居手扫)——三把尺逐枚同数才算复核;
⑤壳谓词第三档: 剥首尾空白后按“前缀字 ⇎ 末两 token ⇎ 年形切片”判, 既不跑整行序列正则(采集侧)也不比逐 token 形状
  (建条侧), 逐行与两把旧尺对拍;
⑥数值抽取: 一条 `\\d[\\d.,]*` 的正则代建条侧的手工扫数字串, 单位词仍就地读(与采集侧的 RXU_PICK 选择支同族而写法不同);
⑦句界: `[.!?](?=[ \\n]|$)` 的 finditer 候选代建条侧逐字符扫 ⇎ 采集侧的 `(?<=[.!?])` 切句;
⑧行号尺: 偏移→行号走 `bisect_right`(建条侧是累积长度表 ⇎ 发射段是线性扫到尾), 逐字符对照表由 `finditer('\\S+')`
  与词跨度同时构造;
⑨切开判词: 两半由词跨度表切(建条侧由行内字符下标表切), 段针自验改走“行折平串按词跨度拼回”档;
⑩对齐账: 本遍由 `get_matching_blocks()` 自己重造动作序列(建条侧直接取 `get_opcodes()` 默认档), 另跑一遍 `autojunk=False`
  档对拍标签序列——相同词数 ⇎ 删插两档在本遍两条通道与建条侧读数三处同值才入账, 游程形制单独记;
⑪池代数: 归属向量走 `Counter` 直方图 ⇎ 两两/三三/四四共用走“对文档下标的组合逐枚数共现”(建条侧是集合 `&`);
⑫定义复用而量不复用: `SPELL ⇎ TONE ⇎ DUR ⇎ NUMW ⇎ UNITW ⇎ NUMLIT ⇎ ROLEN ⇎ NEG ⇎ WIN ⇎ SECND ⇎ PINS ⇎ CITED ⇎ PARA
SAMEK ⇎ PKND` 由两遍源码 `ast` 摘, 谓词函数 `exec` 进来只用于对拍; 36+20 道布尔门的右式 ⇎ 恒等式表达式也从源码
摘了在本遍读数上 eval; 锚的归属由条目正文的“源标签紧接原子引文”手写配对扫描现推, 双轨(整篇归一串 ⇎ 逐行归一串)
同判才计数; ⑬锚账: 本遍不抄建条侧的针表, 候选针由两遍源码的字符串字面量递归收集, 再过词前/后缀退让档与归一化变体,
按日志器自己的截断长度 14/26/30/34 建索引; 每档锚由本遍的行号尺复现行号 ⇎ 命中数, 复现窗口与正文引用串闭合成对,
日志 ⇎ 去重档 ⇎ 正文引用是三个口径(120 ⇎ 82 ⇎ 106), 各自现数不互相换算。 每个键与 corpus/_b82flat.json 逐值对拍,
值不符或键缺失一律先收集后汇总; 覆盖不足也要如实报数。"""
import io, os, re, sys, json, ast, bisect, difflib, itertools as IT
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
ENTRY = u'%s/babeltele/B82_idle_connection_timeout_five_answers.md' % C
PATH = [u'%s/raw/tcpRTO/rfc1122.txt' % C, u'%s/raw/tcpTW/rfc9293.txt' % C,
        u'%s/raw/httpKA/rfc9112.txt' % C, u'%s/raw/idle/rfc9113.txt' % C,
        u'%s/raw/idle/rfc9000.txt' % C]
LBL = [u'1122', u'9293', u'9112', u'9113', u'9000']
NSRC = 5
NL = u'\n'
TAGS = LBL
FAM = [u'old', u'new', u'new', u'new', u'new']
IDS = [u'1122', u'9293', u'9112', u'9113', u'9000']
YR = [1989, 2022, 2022, 2022, 2021]
MON = [u'October', u'August', u'June', u'June', u'May']
OLD = [0]
NEW = [1, 2, 3, 4]
IDX = dict((t, n) for n, t in enumerate(LBL))
FF = u'\x0c'

FLAT = json.load(io.open(u'%s/_b82flat.json' % C, encoding='utf-8'))
CH = json.load(io.open(u'%s/_b82checks.json' % C, encoding='utf-8'))
DER = json.load(io.open(u'%s/_deriv82.json' % C, encoding='utf-8'))
MEA = json.load(io.open(u'%s/_b82meas.json' % C, encoding='utf-8'))
MS = io.open(u'%s/_mkB82.py' % C, encoding='utf-8').read()
EM = io.open(u'%s/_mk82emit.py' % C, encoding='utf-8').read()

TABS = (u'SPELL', u'TONE', u'DUR', u'NUMW', u'UNITW', u'UNITW_S', u'UNIT_IDX', u'NUMLIT', u'UORD',
        u'ROLEN', u'NEG', u'WIN', u'SECND', u'SECTTL', u'CITED', u'PARA', u'SAMEK', u'SAMEK2',
        u'PKND', u'PINS', u'KWK')
TAB = {}
for src in (MS, EM):
    for st in ast.parse(src).body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
            nm = st.targets[0].id
            if nm in TABS and nm not in TAB:
                # 先按字面量摘; 摘不动的(UNITW_S = UNITW + ['s'] 这类由已摘名拼出的)在同一份
                # 已摘命名域里求值——两条通道都只读源码里的定义, 不重新声明本遍的量
                try:
                    TAB[nm] = ast.literal_eval(st.value)
                except Exception:
                    try:
                        TAB[nm] = eval(compile(ast.Expression(st.value), '<tab>', 'eval'), dict(TAB))
                    except Exception:
                        pass
for nm in TABS:
    assert nm in TAB, nm
SPELL, TONE, DUR, NUMW = TAB[u'SPELL'], TAB[u'TONE'], TAB[u'DUR'], TAB[u'NUMW']
UNITW, UNITW_S, UNIT_IDX = TAB[u'UNITW'], TAB[u'UNITW_S'], TAB[u'UNIT_IDX']
NUMLIT, UORD, ROLEN, NEG, WIN = TAB[u'NUMLIT'], TAB[u'UORD'], TAB[u'ROLEN'], TAB[u'NEG'], TAB[u'WIN']
SECND, SECTTL, CITED, PARA = TAB[u'SECND'], TAB[u'SECTTL'], TAB[u'CITED'], TAB[u'PARA']
SAMEK, SAMEK2, PKND, PINS, KWK = TAB[u'SAMEK'], TAB[u'SAMEK2'], TAB[u'PKND'], TAB[u'PINS'], TAB[u'KWK']
NR = len(ROLEN)

# ---------- 建条侧与采集侧的尺: 只用来对拍, 本遍读数一律走自己的尺 ----------
TAGR = re.compile(u' \\((MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHLD|ED)-[0-9]+\\)', re.I)
TAGRE = re.compile(u'\\b(MUST|SHOULD|MAY|SHLD|ED)-([0-9]+)\\b')
TAGBRK = re.compile(u'\\[\\((?:MUST|SHOULD|MAY|SHLD|ED)-[0-9]+\\)\\]')
TAGPR = re.compile(u'\\((?:MUST|SHOULD|MAY|SHLD|ED)-[0-9]+ -- ')
RXU_PICK = re.compile(u'(?<![A-Za-z0-9.])(\\d+(?:[.,]\\d+)?)[ ]?'
                      u'(milliseconds|microseconds|seconds|ms|s)(?![A-Za-z])')
REFHEAD = re.compile(u'^(?:\\d+(?:\\.\\d+)*\\.? +)?references$')

PKF = [u'pnorm', u'fold', u'cnt_cur', u'cnt_re', u'ub', u'ub_re', u'_nb', u'digit_runs',
       u'is_shell_pick', u'shell_by_shape', u'tag_strip', u'num_pairs', u'num_pairs_re',
       u'sent_bounds', u'sents', u'canon', u'_after', u'_prev', u'pool_of', u'straddle_pair',
       u'head_words', u'suffix_words', u'head_words_all', u'tag_kept', u'needle_at',
       u'line_holds', u'raw_span', u'row_fd', u'fmap', u'line_of', u'loc', u'grow', u'TONED']
_ns = {u're': re, u'NL': NL, u'TAGR': TAGR, u'TAGRE': TAGRE, u'RXU_PICK': RXU_PICK,
       u'UNITW': UNITW, u'UORD': UORD, u'UNIT_IDX': UNIT_IDX, u'LDUMMY': None}
for fn in PKF:
    m = None
    for src in (MS, EM):
        m = re.search(u'def ' + fn + u'\\(.*?\\):.*?\\n(?=\\S)', src, re.S)
        if m:
            break
    assert m, fn
    exec(m.group(0), _ns)
for fn in PKF:
    assert fn in _ns, fn
mk_pnorm, mk_fold = _ns[u'pnorm'], _ns[u'fold']
mk_cnt_cur, mk_cnt_re = _ns[u'cnt_cur'], _ns[u'cnt_re']
mk_ub, mk_ub_re = _ns[u'ub'], _ns[u'ub_re']
mk_druns = _ns[u'digit_runs']
mk_pick, mk_shape = _ns[u'is_shell_pick'], _ns[u'shell_by_shape']
mk_strip = _ns[u'tag_strip']
mk_sent_bounds, mk_sents, mk_canon = _ns[u'sent_bounds'], _ns[u'sents'], _ns[u'canon']
mk_num_pairs, mk_num_re = _ns[u'num_pairs'], _ns[u'num_pairs_re']
mk_pool_of, mk_straddle = _ns[u'pool_of'], _ns[u'straddle_pair']
mk_headw, mk_sufw, mk_headall = _ns[u'head_words'], _ns[u'suffix_words'], _ns[u'head_words_all']


# ---------- 本遍自己的尺 ----------
def bytes_of(p):
    return io.open(p, 'rb').read()


BB = [bytes_of(p) for p in PATH]
TT = [b.decode('utf-8', 'replace') for b in BB]
_RXNL = re.compile(u'\\n')


def ln3(t):
    """行界: 正则引擎切(建条侧是 str.split)"""
    return _RXNL.split(t)


RAWL3 = [ln3(t) for t in TT]
L3 = [[y[:-1] if (len(y) > 0 and y[-1]) == u'\r' else y for y in RAWL3[i]] for i in range(NSRC)]
WSPAN = re.compile(u'\\S+')


def toks(s):
    return [(m.start(), m.end()) for m in WSPAN.finditer(s)]


def fold3(s):
    """折平: 词跨度拼回(建条侧是 re.split('\\s') 过滤空段)"""
    return u' '.join([s[a:b] for a, b in toks(s)])


def p3(s):
    return fold3(s.lower())


def c3(s, nd):
    """非重叠计数: str.count(建条侧是 findall(re.escape), 采集侧是游标 find)"""
    return s.count(nd)


def o3(s, nd):
    """重叠计数: finditer 前瞻(建条侧无此档, 采集侧的游标环按整针长跳位)"""
    return len([1 for m in re.finditer(u'(?=' + re.escape(nd) + u')', s)])


def alpha_mask(s):
    return [c.isalpha() for c in s]


def digit_mask(s):
    return [c.isdigit() for c in s]


def alnum_mask(s):
    return [c.isalnum() for c in s]


LET = frozenset(u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
DIG = frozenset(u'0123456789')


def m_alpha(s):
    return [c in LET for c in s]


def m_digit(s):
    return [c in DIG for c in s]


def m_alnum(s):
    return [(c in LET or c in DIG) for c in s]


MASK = {u'alpha': m_alpha, u'digit': m_digit, u'alnum': m_alnum}
MASKU = {u'alpha': alpha_mask, u'digit': digit_mask, u'alnum': alnum_mask}


def hits3(s, nd):
    """针的落点表: 前瞻 finditer(建条侧是 findall(re.escape), 采集侧是游标 find 环)"""
    return [m.start() for m in re.finditer(u'(?=' + re.escape(nd) + u')', s)]


def ub3(s, w, kind=u'alpha', uni=False):
    """整词尺: finditer 定位 + 布尔表读邻(建条侧两档分别是断言正则 ⇎ 邻居字符手扫)。
    默认档与建条侧的 ASCII 断言同判; uni=True 是本遍另开的一把 Unicode 尺, 只用来量两把尺的分歧。"""
    n = len(w)
    M = (MASKU if uni else MASK)[kind](s)
    c = 0
    for i in hits3(s, w):
        la = M[i - 1] if i > 0 else False
        ra = M[i + n] if i + n < len(s) else False
        if not la and not ra:
            c += 1
    return c


def runs3(s):
    """数字段枚数: 布尔表上数上升沿(建条侧是逐字符 cur/prev 手扫)"""
    M = digit_mask(s)
    return len([1 for k in range(len(M)) if M[k] and (k == 0 or not M[k - 1])])


def shell3(x, fam):
    """壳谓词第三档: 剥首尾空白后看前缀字与末两 token 的切片形状"""
    s = x.strip()
    if s == u'':
        return True
    if s.endswith(u']'):
        k = s.rfind(u'[Page ')
        if k >= 0 and s[k + 6:-1].isdigit() and (k == 0 or s[k - 1] in u' \t'):
            return True
    if fam == u'old' and s[:7] == u'RFC1122' and len(s) > 8 and s[7] in u' \t':
        tail = s[s.rfind(u' '):].strip()
        if len(tail) == 4 and tail[:2] in (u'19', u'20') and tail[2:].isdigit():
            return True
    return False


def tag_strip3(s):
    """去编号: 在 TAGR 命中区间之外逐段拼回(建条侧是 TAGR.sub)"""
    out, k = [], 0
    for m in TAGR.finditer(s):
        out.append(s[k:m.start()])
        k = m.end()
    out.append(s[k:])
    return u''.join(out)


def sent_at3(face, k, need_digit_free=True):
    """句始: 取候选边界表里严格小于 k 的最后一枚(建条侧是逐字符向后退, 采集侧是先切句再定位)"""
    cand = [0]
    for m in re.finditer(u'[.!?](?=[ \\n]|$)', face):
        j = m.end()
        if j < len(face) and face[j] == u' ' and face[j + 1:j + 2].isdigit():
            continue
        cand.append(j)
    lo = cand[bisect.bisect_right(cand, k) - 1]
    hi = len(face)
    endc = [m.end() for m in re.finditer(u'[.!?](?=[ \\n]|$)', face)]
    p = bisect.bisect_right(endc, k)
    if p < len(endc):
        hi = endc[p]
    return lo, hi


def num3(text, units):
    """数值抽取: 正则取数字段, 再就地读单位词(建条侧手工扫数字串, 采集侧一条选择支正则)"""
    out = []
    for m in re.finditer(u'\\d+(?:[.,]\\d+)*', text):
        j = m.end()
        while j < len(text) and text[j] == u' ':
            j += 1
        for u in units:
            if text[j:j + len(u)].lower() == u and not (j + len(u) < len(text)
                                                        and text[j + len(u)].isalpha()):
                out.append((m.group(0), u))
                break
    return out


G = {}
BAD = []
MISS = []
# 建条遍写死或未量的格, 本遍改真量: 与建条档不符属申报, 不算实现走样
OVR = set([u'pick_needle_gap'])
OVRV = []


def dv(x):
    if isinstance(x, dict):
        return dict((str(k), dv(v)) for k, v in x.items())
    if isinstance(x, tuple):
        return [dv(y) for y in x]
    if isinstance(x, list):
        return [dv(y) for y in x]
    return x


def put(k, v):
    if k in FLAT:
        a, b = dv(FLAT[k]), dv(v)
        if a != b:
            (OVRV if k in OVR else BAD).append((k, a, b))
    G[k] = v
    return v


# ---------- 四档面 ⇎ 两套壳尺 ⇎ 行↔偏移两张表 ----------
LOW3 = [p3(TT[i]) for i in range(NSRC)]
FOLDC3 = [fold3(TT[i]) for i in range(NSRC)]
SHP3 = [[x for x in L3[i] if not shell3(x, FAM[i])] for i in range(NSRC)]
SHC3 = [u' '.join([fold3(x) for x in SHP3[i]]) for i in range(NSRC)]
LOW_SH3 = [p3(u' '.join(SHP3[i])) for i in range(NSRC)]
SHTAGC3 = [tag_strip3(SHC3[i]) for i in range(NSRC)]
LOW_TAG3 = [p3(SHTAGC3[i]) for i in range(NSRC)]
for i in range(NSRC):
    assert LOW3[i] == mk_pnorm(TT[i]), i
    assert FOLDC3[i] == mk_fold(TT[i]), i
# 三把壳尺逐行对账: 本遍(前缀字+末两 token 切片) ⇎ 采集侧(整行序列正则) ⇎ 建条侧(折叠后 token 形状)
SHELLDIFF = []
for i in range(NSRC):
    for n in range(len(L3[i])):
        r = (shell3(L3[i][n], FAM[i]), mk_pick(L3[i][n], FAM[i]), mk_shape(L3[i][n], FAM[i]))
        if r[0] != r[1] or r[1] != r[2]:
            SHELLDIFF.append((LBL[i], n + 1) + r)
put('shell_pred_diff', len(SHELLDIFF))
ROWSH3 = sum([len(L3[i]) for i in range(NSRC)])
assert not SHELLDIFF, SHELLDIFF[:4]
put('shell_pred_agree', 1 if G['shell_pred_diff'] == 0 else 0)
# 摘壳面的两条重构通道: 逐行折平再拼接 ⇎ 整份摘壳行串接后再折平(建条侧只走前一条)
for i in range(NSRC):
    assert SHC3[i].lower() == LOW_SH3[i], i
    assert fold3(u' '.join(SHP3[i])) == SHC3[i], i

FAN3 = [p3(TT[i]) for i in range(NSRC)]
ROWS3 = [[(n + 1, x) for n, x in enumerate(L3[i]) if not shell3(x, FAM[i])] for i in range(NSRC)]


def fd3(raw):
    """折平并给每个结果字符记下它的原行下标: 用词跨度表构造(建条侧是手工跳空白)"""
    s, ix = [], []
    for a, b in toks(raw):
        if s:
            s.append(u' ')
            ix.append(a)
        for k in range(a, b):
            s.append(raw[k].lower())
            ix.append(k)
    return u''.join(s), ix


FD3 = []
for i in range(NSRC):
    arr = []
    for n, x in ROWS3[i]:
        f, ix = fd3(x)
        assert len(f) == len(ix) and len(f.lower()) == len(f), (LBL[i], n)
        arr.append((n, x, f, ix))
    FD3.append(arr)
    assert [a[1] for a in FD3[i]] == SHP3[i], i
    assert u' '.join([a[2] for a in FD3[i]]) == LOW_SH3[i], i


def mp3(i):
    """折平面偏移 → 行号表: 每行起始列 = 前若干行长度之和 + 行间隔符枚数(bisect 用)"""
    st, starts, nums = 0, [], []
    for k, (n, x, f, ix) in enumerate(FD3[i]):
        starts.append(st)
        nums.append(n)
        st += len(f) + (1 if k + 1 < len(FD3[i]) else 0)
    return starts, nums


MPS3 = [mp3(i) for i in range(NSRC)]


def line3(i, a):
    st, nums = MPS3[i]
    return nums[bisect.bisect_right(st, a) - 1]


def loc3(i, a):
    st, nums = MPS3[i]
    p = bisect.bisect_right(st, a) - 1
    return nums[p], a - st[p]
# ---------- 行号尺(原面) ⇎ 逐行归一尺 ⇎ 非 ASCII 落点 ----------
BREAKS3 = u'\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029'


def brk_pos(t):
    """手工扫行终止符('\\r\\n' 算一枚): splitlines 的内部规则由这条扫描复现"""
    out, k, n = [], 0, len(t)
    while k < n:
        c = t[k]
        if c == u'\r':
            e = k + 2 if (k + 1 < n and t[k + 1] == u'\n') else k + 1
            out.append((k, e))
            k = e
            continue
        if c in BREAKS3:
            out.append((k, k + 1))
            k += 1
            continue
        k += 1
    return out


def splitlines3(t):
    b = brk_pos(t)
    if not t:
        return 0
    return len(b) + (0 if b and b[-1][1] == len(t) else 1)


NLPOS3 = [[-1] + [m.start() for m in re.finditer(u'\\n', TT[i])] for i in range(NSRC)]


def rawline3(i, pos):
    """原文偏移 → 原文件行号(1 基): bisect 走换行符落点表(建条侧是逐行长度累加)"""
    return bisect.bisect_right(NLPOS3[i], pos)


ROWBAD = [0]
for i in range(NSRC):
    for n in range(len(L3[i])):
        if p3(L3[i][n]) != mk_pnorm(L3[i][n]):
            ROWBAD[0] += 1
assert ROWBAD[0] == 0

FC = {u'fold': FOLDC3, u'sh': SHC3, u'tag': SHTAGC3}
LFC = {u'fold': LOW3, u'sh': LOW_SH3, u'tag': LOW_TAG3}
for i in range(NSRC):
    assert LOW_TAG3[i] == SHTAGC3[i].lower(), i


# ---------- 家 0: 面量 ⇎ 行式 ⇎ 壳账 ----------
put('nsrc', NSRC)
put('bytes', [len(BB[i]) for i in range(NSRC)])
put('chars', [len(TT[i]) for i in range(NSRC)])
put('lines', [len(L3[i]) for i in range(NSRC)])
put('splitlines', [splitlines3(TT[i]) for i in range(NSRC)])
put('splitnl', [len(RAWL3[i]) for i in range(NSRC)])
put('nonblank', [sum([1 for x in L3[i] if x.strip() != u'']) for i in range(NSRC)])
put('blank', [sum([1 for x in L3[i] if x.strip() == u'']) for i in range(NSRC)])
put('maxlen', [max([len(x) for x in L3[i]]) for i in range(NSRC)])
put('cr', [c3(TT[i], u'\r') for i in range(NSRC)])
put('lf', [len(NLPOS3[i]) - 1 for i in range(NSRC)])
put('ff', [c3(TT[i], FF) for i in range(NSRC)])
put('ff_alone', [sum([1 for x in L3[i] if x == FF]) for i in range(NSRC)])
put('ff_led', [sum([1 for x in L3[i] if len(x) > 0 and x[0] == FF]) for i in range(NSRC)])
put('ff_before_nl', [c3(TT[i], FF + NL) for i in range(NSRC)])
put('ff_at_eof', [1 if TT[i][-1:] == FF else 0 for i in range(NSRC)])
put('trailing_nl', [1 if TT[i][-1:] == NL else 0 for i in range(NSRC)])
FL = G['splitlines']
SN = G['splitnl']
put('row_form_ledger', [(FL[i] - SN[i]) - (G['ff_before_nl'][i] - G['trailing_nl'][i]) for i in range(NSRC)])
put('foot', [sum([1 for x in L3[i] if shell3(x, FAM[i]) and u'[Page' in fold3(x)]) for i in range(NSRC)])
put('hdr_old', [sum([1 for x in L3[i] if FAM[i] == u'old' and len(toks(x))
                     and x[toks(x)[0][0]:toks(x)[0][1]] == u'RFC1122']) for i in range(NSRC)])
put('shell_lines', [sum([1 for x in L3[i] if shell3(x, FAM[i])]) for i in range(NSRC)])
put('shell_ledger', [G['shell_lines'][i] - (G['blank'][i] + G['foot'][i] + G['hdr_old'][i]) for i in range(NSRC)])
put('bom', [1 if len(L3[i]) and L3[i][0] == u'\ufeff' else 0 for i in range(NSRC)])
put('end_nl', [1 if TT[i].endswith(NL) else 0 for i in range(NSRC)])


def is_pgnum(x):
    """纯页码行: 逐字符判“数字或空白”, 段枚数走上升沿布尔表"""
    return x.strip() != u'' and not [c for c in x if not (c in DIG or c.isspace())] and runs3(x) == 1


PGROW = [[n + 1 for n in range(len(L3[i])) if is_pgnum(L3[i][n])] for i in range(NSRC)]
put('pgnum', [len(x) for x in PGROW])
put('pgnum_shell', [len([n for n in PGROW[i] if shell3(L3[i][n - 1], FAM[i])]) for i in range(NSRC)])
put('pgnum_overstrip', [G['pgnum'][i] - G['pgnum_shell'][i] for i in range(NSRC)])
put('pgnum_row_lines', [[n for n in PGROW[i] if not shell3(L3[i][n - 1], FAM[i])] for i in range(NSRC)])

# ---------- 家 1: 非 ASCII ⇎ 后段位置 ----------
NA_RE = re.compile(u'[^\\x00-\\x7f]')
NAP = [[m.start() for m in NA_RE.finditer(TT[i])] for i in range(NSRC)]
put('nonascii', [sorted(set([ord(TT[i][p]) for p in NAP[i]])) for i in range(NSRC)])
put('na_total', [len(NAP[i]) for i in range(NSRC)])
put('na_bom', [G['bom'][i] for i in range(NSRC)])
put('na_other', [G['na_total'][i] - G['na_bom'][i] for i in range(NSRC)])
put('na_ledger', [G['na_total'][i] - G['na_bom'][i] - G['na_other'][i] for i in range(NSRC)])
REFH3 = [[n for n in range(len(L3[i])) if REFHEAD.match(p3(L3[i][n])) is not None] for i in range(NSRC)]
put('ref_toc_line', [(ks[0] + 1 if ks else -1) for ks in REFH3])
put('ref_body_line', [(ks[-1] + 1 if ks else -1) for ks in REFH3])
put('ref_print_n', [len(ks) for ks in REFH3])
put('ref_ledger', [G['ref_print_n'][i] - (1 if G['ref_toc_line'][i] > 0 else 0)
                   - (1 if G['ref_body_line'][i] > 0 and G['ref_body_line'][i] != G['ref_toc_line'][i] else 0)
                   for i in range(NSRC)])
ADDRSET = (u"author's address", u"authors' addresses", u'contributors')
ADDR3 = [[n for n in range(len(L3[i])) if p3(L3[i][n]) in ADDRSET] for i in range(NSRC)]
put('addr_head_n', [len(ks) for ks in ADDR3])
put('addr_head_line', [(max(ks) + 1 if ks else -1) for ks in ADDR3])
NAROW3 = [sorted(set([rawline3(i, p) for p in NAP[i]])) for i in range(NSRC)]
NAL3 = [[n for n in NAROW3[i] if not (n == 1 and L3[i][0] == u'\ufeff')] for i in range(NSRC)]
put('na_lines', [len(NAROW3[i]) for i in range(NSRC)])
put('na_name_lines', [len(x) for x in NAL3])
put('na_bom_line', [G['na_lines'][i] - G['na_name_lines'][i] for i in range(NSRC)])
put('na_after_ref', [len([n for n in NAL3[i] if G['ref_body_line'][i] > 0 and n > G['ref_body_line'][i]])
                     for i in range(NSRC)])
put('na_before_ref', [G['na_name_lines'][i] - G['na_after_ref'][i] for i in range(NSRC)])
put('na_first_after_ref', [(min([n - G['ref_body_line'][i] for n in NAL3[i]])
                            if (NAL3[i] and G['ref_body_line'][i] > 0) else -1) for i in range(NSRC)])
REFBUL = re.compile(u'^\\s*\\[[A-Z]')
REFMATCH = [[None] + [REFBUL.match(L3[i][n]) is not None for n in range(len(L3[i]))] for i in range(NSRC)]
put('na_ref_entry_lines', [len([n for n in NAL3[i] if REFMATCH[i][n]]) for i in range(NSRC)])
put('na_addr_bullet', [len([n for n in NAL3[i] if L3[i][n - 1].strip().startswith(u'*')]) for i in range(NSRC)])
put('na_other_lines', [G['na_name_lines'][i] - G['na_ref_entry_lines'][i] - G['na_addr_bullet'][i]
                       for i in range(NSRC)])
put('na_place_ledger', [G['na_name_lines'][i] - G['na_ref_entry_lines'][i] - G['na_addr_bullet'][i]
                        - G['na_other_lines'][i] for i in range(NSRC)])
put('na_cp_tot', sum([len(x) for x in G['nonascii']]))
put('na_cp_new', sum([len(x) for i, x in enumerate(G['nonascii']) if FAM[i] == u'new']))
put('bom_in_fold', [1 if u'\ufeff' in SHC3[i] else 0 for i in range(NSRC)])
put('bom_survives', sum(G['bom_in_fold']))
put('na_old_total', sum([G['na_total'][i] for i in OLD]))

# ---------- 家 2: 拼写族 ⇎ 术语换代 ----------
put('spell', [[c3(LFC[u'fold'][i], p) for p in SPELL] for i in range(NSRC)])
put('spell_word', [[ub3(LFC[u'fold'][i], p) for p in SPELL] for i in range(NSRC)])
put('spell_ruler_gap', [G['spell'][i][k] - G['spell_word'][i][k]
                        for i in range(NSRC) for k in range(len(SPELL))])
put('spell_ruler_gap_tot', sum(G['spell_ruler_gap']))
put('spell_tot', [sum(G['spell'][i]) for i in range(NSRC)])
put('ka_forms', [[k for k in (0, 1, 2, 3, 4) if G['spell'][i][k]] for i in range(NSRC)])
put('ka_form_n', [len(x) for x in G['ka_forms']])
put('ka_merged', sum([G['spell'][i][1] for i in range(NSRC)]))
put('ka_hyphen', [G['spell'][i][0] for i in range(NSRC)])
put('ack', [[G['spell'][i][9], G['spell'][i][10]] for i in range(NSRC)])
put('ack_both', [1 if min(G['ack'][i]) > 0 else 0 for i in range(NSRC)])
put('ack_minor', [min(G['ack'][i]) for i in range(NSRC)])
put('ack_major', [max(G['ack'][i]) for i in range(NSRC)])
put('ack_skew', [round(G['ack_major'][i] / float(G['ack_minor'][i]), 2) if G['ack_minor'][i] else -1
                 for i in range(NSRC)])
put('impl', [[G['spell'][i][11], G['spell'][i][12]] for i in range(NSRC)])
put('impl_own', [[u'implementors' if G['impl'][i][0] and not G['impl'][i][1] else u'',
                  u'implementers' if G['impl'][i][1] and not G['impl'][i][0] else u''] for i in range(NSRC)])
put('idle_term', [G['spell'][i][5] for i in range(NSRC)])
put('idle_compound', [G['spell'][i][6] for i in range(NSRC)])
put('persist', [G['spell'][i][8] for i in range(NSRC)])
SPHIT = [[sum([1 for j in range(NSRC) if G['spell'][j][k]]) for k in range(len(SPELL))] for i in range(NSRC)]
put('spell_own', [[SPELL[k] for k in range(len(SPELL)) if G['spell'][i][k] and SPHIT[i][k] == 1]
                  for i in range(NSRC)])
put('spell_own_tot', sum([len(x) for x in G['spell_own']]))

# ---------- 家 3: 义务词四档 ⇎ 编号族 ----------
put('tone_line', [[sum([ub3(x, w) for x in L3[i]]) for w in TONE] for i in range(NSRC)])
put('tone_fold', [[ub3(FC[u'fold'][i], w) for w in TONE] for i in range(NSRC)])
put('tone_sh', [[ub3(FC[u'sh'][i], w) for w in TONE] for i in range(NSRC)])
put('tone_tag', [[ub3(FC[u'tag'][i], w) for w in TONE] for i in range(NSRC)])
put('tone_wrap_gain', [G['tone_fold'][i][k] - G['tone_line'][i][k] for i in range(NSRC) for k in range(5)])
put('tone_sh_gain', [G['tone_sh'][i][k] - G['tone_fold'][i][k] for i in range(NSRC) for k in range(5)])
put('tone_tag_gain', [G['tone_tag'][i][k] - G['tone_sh'][i][k] for i in range(NSRC) for k in range(5)])
put('tone_tot', [sum(G['tone_sh'][i]) for i in range(NSRC)])
put('tone_ledger', [G['tone_sh'][i][0] - G['tone_sh'][i][1] - (G['tone_sh'][i][0] - G['tone_sh'][i][1])
                    for i in range(NSRC)])
put('must_bare', [G['tone_sh'][i][0] - G['tone_sh'][i][1] for i in range(NSRC)])
put('mustnot_of_must', [1 if G['tone_sh'][i][1] <= G['tone_sh'][i][0] else 0 for i in range(NSRC)])
put('tone_must_ledger', [G['tone_sh'][i][0] - G['tone_sh'][i][1] - G['must_bare'][i] for i in range(NSRC)])
TAGPOS3 = [[(m.group(1), int(m.group(2)), m.start()) for m in TAGRE.finditer(TT[i])] for i in range(NSRC)]
put('tag_raw', [len(TAGPOS3[i]) for i in range(NSRC)])
TAGSH3 = [[(m.group(1), int(m.group(2))) for m in TAGRE.finditer(FC[u'sh'][i])] for i in range(NSRC)]
put('tag_sh', [len(x) for x in TAGSH3])
put('tag_decl', [c3(LFC[u'sh'][i], p3(u'individually labeled')) for i in range(NSRC)])
put('tag_kinds', [[len([1 for (g, nu) in TAGSH3[i] if g == w])
                   for w in (u'MUST', u'SHOULD', u'MAY', u'SHLD', u'ED')] for i in range(NSRC)])
put('tag_kind_sum', [sum(x) for x in G['tag_kinds']])
put('tag_kind_close', [G['tag_kind_sum'][i] - G['tag_sh'][i] for i in range(NSRC)])
TAGSHPOS = [[(m.group(1), int(m.group(2)), m.start(), m.end()) for m in TAGRE.finditer(FC[u'sh'][i])]
            for i in range(NSRC)]
PARENPOS = [[(m.start(), m.end(), m.group(1)) for m in TAGR.finditer(FC[u'sh'][i])] for i in range(NSRC)]
put('tag_paren', [len(x) for x in PARENPOS])
put('tag_bare', [len([1 for (g, nu, p, e) in TAGSHPOS[i] if FC[u'sh'][i][p - 1:p] != u'('])
                 for i in range(NSRC)])
BRKPOS = [[(m.start(), m.end()) for m in TAGBRK.finditer(FC[u'sh'][i])] for i in range(NSRC)]
PRPOS = [[(m.start(), m.end()) for m in TAGPR.finditer(FC[u'sh'][i])] for i in range(NSRC)]
put('tag_paren_bracket', [len(x) for x in BRKPOS])
put('tag_paren_prose', [len(x) for x in PRPOS])
put('tag_paren_prose_samples', [[FC[u'sh'][i][a:b + 20] for (a, b) in PRPOS[i]][:2] for i in range(NSRC)])
put('tag_bracket_samples', [[FC[u'sh'][i][max(0, a - 16):b + 6] for (a, b) in BRKPOS[i]][:3]
                            for i in range(NSRC)])
put('tag_form_ledger', [G['tag_paren'][i] + G['tag_paren_prose'][i] + G['tag_paren_bracket'][i]
                        + G['tag_bare'][i] - G['tag_sh'][i] for i in range(NSRC)])
put('tag_paren_kind', [[len([1 for (a, b, g) in PARENPOS[i] if g.upper() == w])
                        for w in (u'MUST', u'MUST NOT', u'SHOULD NOT', u'SHOULD', u'MAY', u'SHLD', u'ED')]
                       for i in range(NSRC)])
put('tag_paren_kind_close', [sum(G['tag_paren_kind'][i]) - G['tag_paren'][i] for i in range(NSRC)])
# 括注后紧跟的字符: 切片剥掉空白后取头一字(建条侧是逐字符向后跳空格)
AFT3 = [[FC[u'sh'][i][b:].lstrip(u' ')[:1] for (a, b, g) in PARENPOS[i]] for i in range(NSRC)]
put('tag_paren_period', [len([1 for x in AFT3[i] if x == u'.']) for i in range(NSRC)])
put('tag_paren_comma', [len([1 for x in AFT3[i] if x == u',']) for i in range(NSRC)])
put('tag_paren_mid', [G['tag_paren'][i] - G['tag_paren_period'][i] - G['tag_paren_comma'][i]
                      for i in range(NSRC)])
put('tag_paren_place_close', [G['tag_paren_period'][i] + G['tag_paren_comma'][i] + G['tag_paren_mid'][i]
                              - G['tag_paren'][i] for i in range(NSRC)])
put('tag_max_num', [max([nu for (g, nu, p) in TAGPOS3[i]] or [0]) for i in range(NSRC)])
put('tone_drop_tag', [[G['tone_sh'][i][k] - G['tone_tag'][i][k] for k in range(5)] for i in range(NSRC)])
put('tone_drop_tot', [sum(x) for x in G['tone_drop_tag']])
put('tone_drop_ledger', [G['tone_drop_tot'][i] - sum([abs(x) for x in G['tone_tag_gain'][i * 5:i * 5 + 5]])
                         for i in range(NSRC)])

# ---------- 家 4: 时长语形 ⇎ 数字写 ⇎ 两把单位尺 ----------
put('dur', [[c3(LFC[u'sh'][i], d.lower()) for d in DUR] for i in range(NSRC)])
put('dur_word', [[ub3(LFC[u'sh'][i], d.lower()) for d in DUR] for i in range(NSRC)])
put('dur_ruler_gap', [G['dur'][i][k] - G['dur_word'][i][k] for i in range(NSRC) for k in range(len(DUR))])
put('numw', [[c3(LFC[u'sh'][i], w.lower()) for w in NUMW] for i in range(NSRC)])
put('num_digit_two', [G['numw'][i][5] + G['numw'][i][6] for i in range(NSRC)])
put('num_digit_two_tot', sum(G['num_digit_two']))
put('num_word_two', [G['numw'][i][0] + G['numw'][i][1] for i in range(NSRC)])
put('num_longform_two', [G['numw'][i][3] for i in range(NSRC)])
put('num_pairs', [sorted(set(num3(TT[i], UNITW))) for i in range(NSRC)])
put('num_pairs_wide', [sorted(set(num3(TT[i], UNITW_S))) for i in range(NSRC)])
put('numval_n', [len(x) for x in G['num_pairs']])
put('numval_wide_n', [len(x) for x in G['num_pairs_wide']])
put('numval_s_extra', [[list(x) for x in G['num_pairs_wide'][i] if x not in G['num_pairs'][i]]
                       for i in range(NSRC)])
put('numval_s_lost', [[list(x) for x in G['num_pairs'][i] if x not in G['num_pairs_wide'][i]]
                     for i in range(NSRC)])
put('num', [[len([1 for x in G['num_pairs'][i] if x[0] == v]) for v in NUMLIT] for i in range(NSRC)])
put('num_unlisted', [[u'%s %s' % (v, u) for (v, u) in G['num_pairs'][i] if v not in NUMLIT]
                     for i in range(NSRC)])
put('num_unlisted_n', [len(x) for x in G['num_unlisted']])
put('num_lit_close', [sum(G['num'][i]) + G['num_unlisted_n'][i] - G['numval_n'][i] for i in range(NSRC)])
put('num_tot', [sum([c3(TT[i], v + u' ') for v in NUMLIT]) for i in range(NSRC)])
put('num_pairs_pick', [sorted(set([tuple(x) for x in RXU_PICK.findall(TT[i])])) for i in range(NSRC)])
put('num_ruler_gap', [len(set(G['num_pairs_wide'][i]) - set(G['num_pairs_pick'][i]))
                      + len(set(G['num_pairs_pick'][i]) - set(G['num_pairs_wide'][i]))
                      for i in range(NSRC)])
put('num_own', [[u'%s %s' % (v, u) for (v, u) in G['num_pairs'][i]
                 if sum([1 for j in range(NSRC) if (v, u) in set(G['num_pairs'][j])]) == 1]
                for i in range(NSRC)])
put('digit_form_two_hours', [c3(TT[i], u'2 hours') + c3(TT[i], u'120 minutes') for i in range(NSRC)])

# ---------- 家 5: 判词针四档 ----------
put('role_line', [[len([1 for x in L3[i] if c3(p3(x), p3(r))]) for r in ROLEN] for i in range(NSRC)])
put('role_fold', [[c3(LFC[u'fold'][i], p3(r)) for r in ROLEN] for i in range(NSRC)])
put('role_sh', [[c3(LFC[u'sh'][i], p3(r)) for r in ROLEN] for i in range(NSRC)])
put('role_tag', [[c3(LFC[u'tag'][i], p3(r)) for r in ROLEN] for i in range(NSRC)])
put('role_line_n', [sum(G['role_line'][i]) for i in range(NSRC)])
put('role_fold_n', [sum(G['role_fold'][i]) for i in range(NSRC)])
put('role_sh_n', [sum(G['role_sh'][i]) for i in range(NSRC)])
put('role_tag_n', [sum(G['role_tag'][i]) for i in range(NSRC)])
put('role_line_read_n', sum([1 for i in range(NSRC) for k in range(NR) if G['role_line'][i][k]]))
put('role_line_miss_n', sum([1 for i in range(NSRC) for k in range(NR)
                             if G['role_line'][i][k] == 0 and G['role_fold'][i][k]]))
put('role_wrap', [[k for k in range(NR) if G['role_line'][i][k] == 0 and G['role_fold'][i][k] > 0]
                  for i in range(NSRC)])
put('role_wrap_n', [len(x) for x in G['role_wrap']])
put('role_wrap_keys', [[i, k] for i in range(NSRC) for k in G['role_wrap'][i]])
put('role_shell', [[k for k in range(NR) if G['role_fold'][i][k] == 0 and G['role_sh'][i][k] > 0]
                   for i in range(NSRC)])
put('role_shell_n', [len(x) for x in G['role_shell']])
put('role_shell_needles', [[i, k] for i in range(NSRC) for k in G['role_shell'][i]])
put('role_tagcut', [[k for k in range(NR) if G['role_sh'][i][k] == 0 and G['role_tag'][i][k] > 0]
                    for i in range(NSRC)])
put('role_tagcut_n', [len(x) for x in G['role_tagcut']])
put('role_tagcut_keys', [[i, k] for i in range(NSRC) for k in G['role_tagcut'][i]])
put('role_gain_fold', [G['role_fold_n'][i] - G['role_line_n'][i] for i in range(NSRC)])
put('role_gain_sh', [G['role_sh_n'][i] - G['role_fold_n'][i] for i in range(NSRC)])
put('role_gain_tag', [G['role_tag_n'][i] - G['role_sh_n'][i] for i in range(NSRC)])
put('role_src', dict((str(k), LBL[i]) for i in range(NSRC) for k in range(NR)
                     if G['role_line'][i][k] == 0 and G['role_tag'][i][k] > 0))
put('role_read_tag_n', sum([1 for i in range(NSRC) for k in range(NR) if G['role_tag'][i][k]]))
put('needle_n', NR)
put('role_hit_by_face', [sum([1 for k in range(NR) if G['role_tag'][i][k]]) for i in range(NSRC)])
put('role_wrap_flat', [[LBL[i], ROLEN[k]] for i in range(NSRC) for k in G['role_wrap'][i]])
put('role_tagcut_flat', [[LBL[i], ROLEN[k]] for i in range(NSRC) for k in G['role_tagcut'][i]])

# ---------- 家 6: 反向对照针 ⇎ 页码壳针的两把面尺 ----------
put('page_lit_fold', [c3(LFC[u'fold'][i], p3(u'[Page 1]')) for i in range(NSRC)])
put('page_lit_sh', [c3(LFC[u'sh'][i], p3(u'[Page 1]')) for i in range(NSRC)])
put('page_lit_rows', [[n for n in range(1, len(L3[i]) + 1) if p3(u'[page 1]') in p3(L3[i][n - 1])]
                      for i in range(NSRC)])
put('page_lit_rows_shell', sum([1 for i in range(NSRC) for n in G['page_lit_rows'][i]
                                if not mk_pick(L3[i][n - 1], FAM[i])]))
put('neg_faces', [x[2] for x in NEG])
put('neg_fold_n', len([x for x in G[u'neg_faces'] if x != u'sh']))
put('neg_n', len(NEG))
put('neg_probes', sum([len(x[1]) for x in NEG]))
NEGF = {u'sh': LFC[u'sh'], u'fold': LFC[u'fold']}
put('neg_word', [[ub3(NEGF[f][i], p3(nd)) for nd, ex, f in NEG] for i in range(NSRC)])
put('neg_sub', [[c3(NEGF[f][i], p3(nd)) for nd, ex, f in NEG] for i in range(NSRC)])
put('neg_zero_hits', sum([sum([G['neg_word'][i][k] for i in ex]) for k, (nd, ex, f) in enumerate(NEG)]))
put('neg_owner_present', len([1 for k, (nd, ex, f) in enumerate(NEG)
                              if sum([G['neg_word'][i][k] for i in range(NSRC) if i not in ex]) > 0]))
put('neg_cold_probes', [NEG[k][0] for k, (nd, ex, f) in enumerate(NEG)
                        if sum([G['neg_word'][i][k] for i in range(NSRC) if i not in ex]) == 0])
put('neg_sub_false_rows', [[LBL[i], NEG[k][0], G['neg_sub'][i][k], G['neg_word'][i][k]]
                           for i in range(NSRC) for k in range(len(NEG))
                           if G['neg_sub'][i][k] > G['neg_word'][i][k]])
put('neg_sub_false', sum([x[2] - x[3] for x in G['neg_sub_false_rows']]))
put('neg_sub_ruler', sum([x[2] for x in G['neg_sub_false_rows']]))

# ---------- 家 7: 答句(逐字符句界的第三档复算) ----------
put('ans_at', [LFC[u'sh'][i].find(p3(WIN[i])) for i in range(NSRC)])
assert all(x >= 0 for x in G['ans_at']), G['ans_at']
SENTB = [sent_at3(LFC[u'sh'][i], G['ans_at'][i]) for i in range(NSRC)]
put('ans', [SHC3[i][SENTB[i][0]:SENTB[i][1]] for i in range(NSRC)])
put('ans_pair_same', 1 if tag_strip3(G['ans'][1]) == G['ans'][0] else 0)
put('ans_words', [len(G['ans'][i].split()) for i in range(NSRC)])
put('ans_chars', [len(G['ans'][i]) for i in range(NSRC)])
put('ans_start_line', [line3(i, G['ans_at'][i]) for i in range(NSRC)])
put('ans_end_line', [line3(i, G['ans_at'][i] + len(p3(WIN[i])) - 1) for i in range(NSRC)])
put('ans_span', [G['ans_end_line'][i] - G['ans_start_line'][i] + 1 for i in range(NSRC)])
put('ans_needle_line', [line3(i, G['ans_at'][i]) for i in range(NSRC)])
put('ans_sent_line', [line3(i, LFC[u'sh'][i].find(p3(G['ans'][i]))) for i in range(NSRC)])
put('ans_sent_end', [line3(i, LFC[u'sh'][i].find(p3(G['ans'][i])) + len(p3(G['ans'][i])) - 1)
                     for i in range(NSRC)])
put('ans_sent_span', [G['ans_sent_end'][i] - G['ans_sent_line'][i] + 1 for i in range(NSRC)])
put('ans_anchor_line', G['ans_sent_line'])
put('ans_span_tot', sum(G['ans_sent_span']))
put('ans_block_lines', G['ans_sent_span'])
# 建条遍把这两格写死成零; 本遍实测: 答句窗内的每一枚原始行都要过三把壳尺
put('ans_shell_rows', [len([1 for n in range(G['ans_sent_line'][i], G['ans_sent_end'][i] + 1)
                            if shell3(L3[i][n - 1], FAM[i])]) for i in range(NSRC)])
put('ans_tagdiff', G['ans_chars'][1] - G['ans_chars'][0])
put('ans_tag_len', sum([len(m.group(0)) for m in TAGR.finditer(G['ans'][1])]))
put('ans_tag_len_ledger', G['ans_chars'][1] - G['ans_chars'][0] - G['ans_tag_len'])
put('ans_tag_n_in_sent', [len(TAGRE.findall(G['ans'][i])) for i in range(NSRC)])
put('ans_na', [len([1 for c in G['ans'][i] if ord(c) > 127]) for i in range(NSRC)])
put('ans_punct', [1 if G['ans'][i].strip().endswith(u'.') else 0 for i in range(NSRC)])

# ---------- 家 8: 两段保活节的逐句对照 ⇎ 三把句等尺 ----------
H1122 = [n for n in range(len(L3[0])) if L3[0][n].strip().startswith(u'4.2.3.6')][-1]
H9293 = [n for n in range(len(L3[1])) if L3[1][n].startswith(u'3.8.4.')][0]
N9293 = [n for n in range(H9293 + 1, len(L3[1])) if L3[1][n].startswith(u'3.8.5.')][0]
N1122 = [n for n in range(H1122 + 1, len(L3[0])) if re.match(u'^\\s+4\\.2\\.3\\.7 +', L3[0][n])][0]
B1 = L3[0][H1122 + 1:N1122]
B2 = L3[1][H9293 + 1:N9293]
DIS1 = [n for n in range(len(B1)) if B1[n].strip() == u'DISCUSSION:'][0]
S1, S2 = B1[:DIS1], B2


def sents3(lines):
    """切句第三档: 先扫出全部句尾边界, 再按相邻边界切片(建条侧是一枚游标 st 边扫边切)"""
    face = p3(NL.join(lines))
    bnd = [0]
    for m in re.finditer(u'[.!?]', face):
        j = m.end()
        if j >= len(face) or face[j] != u' ' or face[j + 1:j + 2] == u'':
            continue
        bnd.append(j + 1)
    out = [face[bnd[k]:bnd[k + 1]].strip() for k in range(len(bnd) - 1)]
    tail = face[bnd[-1]:].strip()
    if tail:
        out.append(tail)
    return [x for x in out if x]


CANONR = re.compile(u'implementers|acknowledgment')
CANONM = {u'implementers': u'implementors', u'acknowledgment': u'acknowledgement'}


def canon3(z):
    """同一处换代用词的第三档: 一张词表加一次正则替换(建条侧是两条链式 replace)"""
    return CANONR.sub(lambda m: CANONM[m.group(0)], z)


A1 = sents3(S1)
A2 = sents3(S2)
A2T = [tag_strip3(x).strip() for x in A2]
A1C = [canon3(y) for y in A1]
put('ovl_head_line', [H1122 + 1, H9293 + 1])
put('ovl_block_lines', [len(B1), len(B2)])
put('ovl_spec_lines', [len(S1), len(S2)])
put('ovl_shell_in_block', len([1 for x in S1 if shell3(x, FAM[0])]))
put('ovl_spec_lines_content', [len([1 for x in S1 if not shell3(x, FAM[0])]), len(S2)])
put('ovl_s1', len(A1))
put('ovl_s2', len(A2))
put('ovl_same_raw', len([z for z in A2 if z in A1]))
put('ovl_same_tag', len([z for z in A2T if z in A1]))
put('ovl_same_canon', len([z for z in A2T if canon3(z) in A1C]))
put('ovl_new', G['ovl_s2'] - G['ovl_same_canon'])
D1 = sents3(B1[DIS1 + 1:])
D1C = [canon3(y) for y in D1]
put('ovl_disc_promoted', len([z for z in A2T if z not in A1 and canon3(z) not in A1C
                              and canon3(z) in D1C]))
put('ovl_same_ledger', G['ovl_s2'] - G['ovl_same_canon'] - G['ovl_new'])
put('ovl_monotone', sum([1 for a, b in ((G['ovl_same_raw'], G['ovl_same_tag']),
                                        (G['ovl_same_tag'], G['ovl_same_canon'])) if a <= b]))
put('ovl_tag_only', G['ovl_same_tag'] - G['ovl_same_raw'])

# ---------- 家 9: 节窗 ⇎ 目录行 ⇎ 引道符 ----------
SECNDL, SECTTLL = TAB[u'SECND'], TAB[u'SECTTL']


def leader3(s):
    """点线引道符枚数: 在 “.” 布尔表上数长度 ≥3 的段(建条侧是 \\. {3,} 一条正则)"""
    M = [c == u'.' for c in s]
    out, k = 0, 0
    while k < len(M):
        if not M[k]:
            k += 1
            continue
        j = k
        while j < len(M) and M[j]:
            j += 1
        if j - k >= 3:
            out += 1
        k = j
    return out


SEC = [[] for _ in range(12)]
for i in range(NSRC):
    cands = [n for n in range(len(L3[i])) if p3(L3[i][n]).startswith(SECNDL[i] + u' ')
             or p3(L3[i][n]) == p3(SECNDL[i] + u'. ' + SECTTLL[i])]
    body = [n for n in cands if leader3(L3[i][n]) == 0 and not shell3(L3[i][n], FAM[i])]
    toc = [n for n in cands if leader3(L3[i][n]) > 0]
    bd = body[-1] if body else -1
    tt = toc[0] if toc else (cands[0] if cands else -1)
    depth = SECNDL[i].count(u'.')
    end = len(L3[i])
    for n in range(bd + 1, len(L3[i])):
        s = L3[i][n].strip()
        if leader3(L3[i][n]) or shell3(L3[i][n], FAM[i]):
            continue
        m = re.match(u'^(\\d+(?:\\.\\d+)*)\\.[ ]|^(\\d+(?:\\.\\d+)*)[ ]{2}', s)
        if m:
            num = (m.group(1) or m.group(2))
            if num.count(u'.') <= depth and num != SECNDL[i]:
                end = n
                break
    win = L3[i][bd:end]
    txt = p3(NL.join([x for x in win if not shell3(x, FAM[i])]))
    SEC[0].append(len(cands))
    SEC[1].append(bd + 1)
    SEC[2].append(tt + 1 if tt >= 0 else -1)
    SEC[3].append(len(L3[i][tt]) - len(L3[i][tt].lstrip()) if tt >= 0 else -1)
    SEC[4].append(len(L3[i][bd]) - len(L3[i][bd].lstrip()) if bd >= 0 else -1)
    SEC[5].append(len([1 for x in win if shell3(x, FAM[i])]))
    SEC[6].append(end - bd)
    SEC[7].append(len(txt))
    SEC[8].append(sum([ub3(txt.upper(), w) for w in TONE]))
    SEC[9].append(len([1 for x in win if re.match(u'^\\s*' + re.escape(SECNDL[i]) + u'\\.\\d', x.strip())]))
    SEC[10].append(c3(LFC[u'sh'][i], p3(SECTTLL[i])))
    SEC[11].append(L3[i][end].strip().split(u' ')[0] if end < len(L3[i]) and L3[i][end].strip() else u'')
for nm, val in zip((u'sec_print_n', u'sec_body_line', u'sec_toc_line', u'sec_toc_indent', u'sec_body_indent',
                    u'sec_shell_rows', u'sec_lines', u'sec_chars', u'sec_tone_tot', u'sec_child',
                    u'sec_hit_n', u'sec_end_no'), SEC):
    put(nm, val)
put('sec_no', SECNDL)
put('head_toc_leader_strict', [1 if G['sec_toc_line'][i] > 0 and leader3(L3[i][G['sec_toc_line'][i] - 1])
                               else 0 for i in range(NSRC)])
put('head_toc_leader_spaced', [1 if G['sec_toc_line'][i] > 0
                               and len(re.findall(u'(?:\\.\\s*){3,}', L3[i][G['sec_toc_line'][i] - 1]))
                               else 0 for i in range(NSRC)])
put('sec_lines_tot', sum(G['sec_lines']))
put('sec_shell_tot', sum(G['sec_shell_rows']))
put('sec_tone_tot_all', sum(G['sec_tone_tot']))
put('sec_tone_only_n', len([x for x in G['sec_tone_tot'] if x]))
put('sec_tone_zero_n', len([x for x in G['sec_tone_tot'] if x == 0]))
put('sec_span_pct', [round(100.0 * G['sec_chars'][i] / len(LFC[u'sh'][i]), 2) for i in range(NSRC)])
put('sec_ans_inside', [1 if (G['sec_body_line'][i] <= G['ans_anchor_line'][i]
                             and G['ans_sent_end'][i] <= G['sec_body_line'][i] + G['sec_lines'][i]) else 0
                       for i in range(NSRC)])
put('sec_ans_gap', [G['ans_anchor_line'][i] - G['sec_body_line'][i] for i in range(NSRC)])
KWAT = [LFC[u'sh'][i].find(p3(u'The key words')) for i in range(NSRC)]
put('kw_at', [a if a >= 0 else -1 for a in KWAT])
put('kw_docs', len([x for x in G['kw_at'] if x >= 0]))
put('kw_cite_bcp', [c3(LFC[u'sh'][i], p3(u'as described in BCP 14 [3] [12]')) for i in range(NSRC)])
put('kw_cite_pair', [c3(LFC[u'sh'][i], p3(u'as described in BCP 14 [RFC2119] [RFC8174]'))
                     for i in range(NSRC)])
put('kw_head', [LFC[u'sh'][i][KWAT[i]:KWAT[i] + 190] for i in range(NSRC)])

# ---------- 家 10: 语态 ⇎ 引用 ⇎ 参数名 ----------
put('voice_we', [ub3(LFC[u'sh'][i], u'we') for i in range(NSRC)])
put('voice_weverb', [sum([ub3(LFC[u'sh'][i], u'we ' + v) for v in
                          (u'propose', u'show', u'observe', u'present', u'specify', u'define', u'use')])
                     for i in range(NSRC)])
put('voice_impersonal', [sum([c3(LFC[u'sh'][i], p3(w)) for w in (u'this document', u'this specification')])
                         for i in range(NSRC)])
put('cit_brk', [len(re.findall(u'\\[RFC[0-9]{4}\\]', TT[i])) for i in range(NSRC)])
put('cit_rfc', [len(re.findall(u'RFC [0-9]{4}', TT[i])) for i in range(NSRC)])
put('cit_rfc_hyphen', [len(re.findall(u'RFC-[0-9]{4}', TT[i])) for i in range(NSRC)])
CITEDL = TAB[u'CITED']
put('cite_matrix', [[c3(TT[i], u'RFC %d' % c) for c in CITEDL] for i in range(NSRC)])
put('cite_own', [len([1 for j, c in enumerate(CITEDL) if G['cite_matrix'][i][j] and c != int(IDS[i])])
                 for i in range(NSRC)])
put('hexes', [len(re.findall(u'(?<![0-9A-Za-z])0x[0-9A-Fa-f]{2}(?![0-9A-Za-z])', TT[i]))
              for i in range(NSRC)])
put('sec_refs', [len(re.findall(u'Section [0-9]', TT[i])) for i in range(NSRC)])
PARAL = TAB[u'PARA']
put('par', [[c3(TT[i], p) for p in PARAL] for i in range(NSRC)])
put('par_n', [sum(x) for x in G['par']])
put('par_under', [len(re.findall(u'\\b[a-z]+_[a-z_]+\\b', TT[i])) for i in range(NSRC)])
put('par_own', [[PARAL[k] for k in range(len(PARAL))
                 if G['par'][i][k] and sum([1 for j in range(NSRC) if G['par'][j][k]]) == 1]
                for i in range(NSRC)])
put('years', YR)

# ---------- 采集遍对账(第三套实现的同一把尺) ----------
PKM = json.load(io.open(u'corpus/_b82meas.json', encoding='utf-8'))
AGREE, DIFFK = [], []
for kk in SAMEK:
    a, b = (G[u'tag_raw'], PKM[u'tag_dash']) if kk == u'tag_raw' else \
           (G[u'foot'], PKM[u'foot']) if kk == u'foot' else (G[kk], PKM[kk])
    (AGREE if a == b else DIFFK).append(kk if a == b else (kk, u'值不符'))
for mk_k, pk_k in SAMEK2:
    (AGREE if G[mk_k] == PKM[pk_k] else DIFFK).append(mk_k if G[mk_k] == PKM[pk_k] else (mk_k, pk_k))
ROLEPK = PKM[u'needles3']
AGREE2, DIFF2 = [], []
for k, nd in enumerate(PKND):
    if nd not in ROLEN:
        continue
    j = ROLEN.index(nd)
    if [x[0] for x in ROLEPK[k]] == [G['role_line'][i][j] for i in range(NSRC)]:
        AGREE2.append(nd)
    else:
        DIFF2.append((nd, u'逐行档不符'))
    if [x[1] for x in ROLEPK[k]] == [G['role_fold'][i][j] for i in range(NSRC)]:
        AGREE2.append(nd + u'⇎折平')
    else:
        DIFF2.append((nd, u'折平档不符'))
put('numunit_pick', [[list(x) for x in G['num_pairs_pick'][i]] for i in range(NSRC)])
if G['numunit_pick'] == PKM[u'numunit']:
    AGREE.append(u'numunit')
else:
    DIFFK.append((u'numunit', u'两把单位尺对拍不符'))
# 建条遍把这格写死成 0; 本遍实测: 采集遍 30 枚判词针里有多少枚在本遍 37 枚中没有同名针, 对拍循环把它们静默跳过
put('pick_needle_gap', len([1 for nd in PKND if nd not in ROLEN]))
PINP = [(lab, nd, ln0, ncnt) for lab, nd, ln0, ncnt in PKM[u'pin_lines']
        if p3(nd) in p3(TAB[u'WIN'][LBL.index(lab)])]
put('pin_checked', len(PINP))
put('pin_line_close', sum([abs(G['ans_needle_line'][LBL.index(lab)] - 1 - ln0)
                           for lab, nd, ln0, ncnt in PINP]))
if G['pin_line_close'] == 0 and G['pin_checked'] >= 2:
    AGREE.append(u'pin_line')
else:
    DIFFK.append((u'pin_line', u'答句首行与采集遍不符'))
put('pick_agree', len(AGREE) + len(AGREE2))
put('pick_diff', len(DIFFK) + len(DIFF2))
put('pick_same_n', len(SAMEK) + len(SAMEK2) + 2 + 2 * len([nd for nd in PKND if nd in ROLEN]))
put('pick_diff_keys', [x[0] for x in DIFFK] + [x[0] for x in DIFF2])
assert not DIFFK, DIFFK[:4]
assert not DIFF2, DIFF2[:4]

# ========== PART3: 段落层 ⇎ 行号尺 ⇎ 切开判词 ⇎ 模板行池(发射段的第三套实现) ==========
FAN3G = [p3(TT[i]) for i in range(NSRC)]          # 门槛对面: 整份原文归一
ROWSRAW3 = [u'\x01'.join(p3(a[1]) for a in FD3[i]) for i in range(NSRC)]
PP3 = [[(a[0], a[2]) for a in FD3[i]] for i in range(NSRC)]
ROWMAP3 = [dict((a[0], a) for a in FD3[i]) for i in range(NSRC)]
put('num_fam', NUMLIT)
put('mk_ans_sent_line', list(G['ans_sent_line']))
put('mk_ans_sent_end', list(G['ans_sent_end']))
put('mk_ans_sent_span', list(G['ans_sent_span']))
put('mk_ans_needle_line', list(G['ans_needle_line']))
put('pp_rows', [len(PP3[i]) for i in range(NSRC)])
put('pp_gap_rows', [G['nonblank'][i] - G['pp_rows'][i] for i in range(NSRC)])
put('pp_shell_nonblank', [G['shell_lines'][i] - G['blank'][i] for i in range(NSRC)])
put('pp_gap_close', sum([abs(G['pp_gap_rows'][i] - G['pp_shell_nonblank'][i]) for i in range(NSRC)]))


def win3(raw, a, b, lim):
    """整词窗口: 在词跨度表上用 bisect 找前后词(建条侧是逐字符向两侧跳空白)"""
    sp = toks(raw)
    S = [x[0] for x in sp]
    E = [x[1] for x in sp]

    def wl(k):
        j = bisect.bisect_right(S, k) - 1
        return sp[j][0] if j >= 0 and sp[j][0] < k < sp[j][1] else k

    def wr(k):
        j = bisect.bisect_right(S, k) - 1
        return sp[j][1] if j >= 0 and sp[j][0] <= k < sp[j][1] else k

    lo, hi = wl(a), wr(b)
    while True:
        cand = []
        j = bisect.bisect_left(E, lo) - 1
        if j >= 0:
            cand.append((lo - S[j], 0, S[j]))
        k = bisect.bisect_right(S, hi)
        if k < len(sp):
            cand.append((E[k] - hi, 1, E[k]))
        if not cand:
            break
        d, side, pos = min(cand)
        if hi - lo + d > lim:
            break
        if side == 0:
            lo = pos
        else:
            hi = pos
    return raw[lo:hi], lo, hi


ATOMFAIL, BLKFAIL = [], []
ALN3 = FD3
ANSET3 = [set([a[1] for a in FD3[i]]) for i in range(NSRC)]
ALOG = []
LIMW = 92


def _anline3(i, nd, exact, lo, lim=LIMW):
    key = p3(nd)
    hits = []
    for n, x, f, ix in ALN3[i]:
        if n < lo:
            continue
        if exact:
            if p3(f) != key:
                continue
            a, b = 0, len(f)
        else:
            k = f.find(key)
            if k < 0:
                continue
            a, b = k, k + len(nd)
        seg, s, e = win3(x, ix[a], ix[min(b, len(ix)) - 1] + 1, lim)
        assert seg in x, (LBL[i], n)
        assert key in p3(seg), (LBL[i], n, nd)
        hits.append((n, seg, x))
    if not hits:
        ATOMFAIL.append((LBL[i], nd))
        return u'⟦%s⟧⟨MISS:%s⟩' % (LBL[i], nd[:28])
    n, seg, x = hits[0]
    assert p3(seg) in FAN3G[i], (LBL[i], seg[:60])
    ALOG.append((LBL[i], nd[:34], n, len(hits), nd))
    return u'⟦%s⟧⟨%s⟩' % (LBL[i], seg)


def blk3(i, start, end, frm=0):
    a = LOW_SH3[i].find(p3(start), frm)
    if a < 0:
        BLKFAIL.append((LBL[i], start, u'起'))
        return u' ', -1, -1
    b = LOW_SH3[i].find(p3(end), a)
    if b < 0:
        BLKFAIL.append((LBL[i], end, u'止'))
        return u' ', line3(i, a), line3(i, a)
    e = b + len(p3(end))
    return u' '.join(SHC3[i][a:e].split()), line3(i, a), line3(i, e - 1)


def line_holds3(i, ln, nd):
    return 1 if p3(nd) in p3(ROWMAP3[i][ln][2]) else 0


def split_pieces3(i, nd, last=False):
    """跨行针两半: 面偏移经每行的字符来源表映回原行切片(建条侧同轨, 本遍用行号字典取行)"""
    key = p3(nd)
    a = LOW_SH3[i].rfind(key) if last else LOW_SH3[i].find(key)
    assert a >= 0, (LBL[i], nd)
    e = a + len(key) - 1
    h, t = line3(i, a), line3(i, e)
    _, rh, fh, ixh = ROWMAP3[i][h]
    _, rt, ft, ixt = ROWMAP3[i][t]
    _, ao = loc3(i, a)
    _, te = loc3(i, e)
    head = rh[ixh[ao]:ixh[len(fh) - 1] + 1]
    tail = rt[ixt[0]:ixt[te] + 1]
    assert head in rh and tail in rt, (LBL[i], nd)
    return h, t, head, tail


PB3 = [blk3(i, s, e) for i, s, e in PINS]
PTXT3 = [p[0] for p in PB3]
put('blk_lo', [p[1] for p in PB3])
put('blk_hi', [p[2] for p in PB3])
put('blk_rows', [p[2] - p[1] + 1 for p in PB3])
put('blk_chars', [len(p[0]) for p in PB3])
put('blk_words', [len(p[0].split()) for p in PB3])
PW3 = [p[0].lower().split() for p in PB3]
put('blk_vocab', [len(set(x)) for x in PW3])
put('blk_five_chars', sum(G['blk_chars'][:5]))
put('blk_five_rows', sum(G['blk_rows'][:5]))
put('blk_five_words', sum(G['blk_words'][:5]))
put('blk_rows_tot', sum(G['blk_rows']))
put('blk_words_tot', sum(G['blk_words']))
put('tone_must_blk', [ub3(p, u'MUST') for p in PTXT3])
put('tone_may_blk', [ub3(p, u'MAY') for p in PTXT3])
put('tone_should_blk', [ub3(p, u'SHOULD') for p in PTXT3])
put('tone_mustnot_blk', [ub3(p, u'MUST NOT') for p in PTXT3])
put('tone_tag_blk', [len(TAGRE.findall(p)) for p in PTXT3])
put('tone_in_blk', [G['tone_must_blk'][n] + G['tone_may_blk'][n] + G['tone_should_blk'][n]
                    for n in range(len(PB3))])
put('blk_must_cur', [c3(p, u'MUST') for p in PTXT3])
put('blk_must_re', [len(re.findall(u'MUST', p)) for p in PTXT3])
put('blk_tone_ruler_close', (sum([abs(G['tone_must_blk'][n] - G['blk_must_cur'][n]) for n in range(len(PB3))])
                             + sum([abs(G['tone_must_blk'][n] - G['blk_must_re'][n]) for n in range(len(PB3))])))
put('blk_tcp_len_gap', G['blk_chars'][1] - G['blk_chars'][0])
put('blk_tcp_tag_chars', sum([len(m.group(0)) for m in TAGR.finditer(PTXT3[1])]))
put('blk_tcp_tag_widths', [len(m.group(0)) for m in TAGR.finditer(PTXT3[1])])

# ---------- 关键词模板段: 共头 ⇎ 共尾 ⇎ 两把相同尺 ----------
KWPAIR3 = [(a, b) for x, a in enumerate(KWK) for b in KWK[x + 1:]]


def headw3(a, b):
    n = 0
    while n < len(a) and n < len(b) and a[n] == b[n]:
        n += 1
    return n


def sufw3(a, b):
    n = 0
    while n < len(a) and n < len(b) and a[len(a) - 1 - n] == b[len(b) - 1 - n]:
        n += 1
    return n


def headall3(words):
    n = 0
    while all(len(x) > n for x in words) and all(x[n] == words[0][n] for x in words):
        n += 1
    return n


put('kw_head_pre', [headw3(PW3[a], PW3[b]) for a, b in KWPAIR3])
put('kw_head_suf', [sufw3(PW3[a], PW3[b]) for a, b in KWPAIR3])
put('kw_same', [1 if PTXT3[a] == PTXT3[b] else 0 for a, b in KWPAIR3])
put('kw_pair_lbl', [u'%s-%s' % (LBL[PINS[a][0]], LBL[PINS[b][0]]) for a, b in KWPAIR3])
put('kw_head_min', min(G['kw_head_pre']))
put('kw_head_max', max(G['kw_head_pre']))
put('kw_same_n', sum(G['kw_same']))
put('kw_suf_tot', sum(G['kw_head_suf']))
put('kw_suf_zero_n', len([x for x in G['kw_head_suf'] if x == 0]))
put('kw_vocab_max', max([G['blk_vocab'][n] for n in KWK]))
put('kw_all_head', headall3([PW3[n] for n in KWK]))


def raw_span3(i, lo, hi):
    return tuple([x.strip() for x in L3[i][lo - 1:hi] if x.strip() != u''])


put('kw_same_raw', [1 if raw_span3(PINS[a][0], PB3[a][1], PB3[a][2])
                    == raw_span3(PINS[b][0], PB3[b][1], PB3[b][2]) else 0 for a, b in KWPAIR3])
put('kw_same_raw_n', sum(G['kw_same_raw']))
put('kw_wrap_diff', len([m for m in range(len(KWPAIR3)) if G['kw_same'][m] and not G['kw_same_raw'][m]]))
put('kw_face_close', sum([abs(G['kw_same'][m] - G['kw_same_raw'][m]) for m in range(len(KWPAIR3))]))
put('kw_suf_nz_n', len([x for x in G['kw_head_suf'] if x > 0]))
put('kw_minus_row', [line3(i, x) if x >= 0 else -1 for i, x in enumerate(G['kw_at'])])

# ---------- 两份 TCP 主答句段: 相同段由匹配器的另一条出口现导 ----------
T1W3 = tag_strip3(PTXT3[1]).lower().split()
SM52 = difflib.SequenceMatcher(None, PW3[0], T1W3)
SMNJ = difflib.SequenceMatcher(None, PW3[0], T1W3)
SMNJ.autojunk = False
MB3 = [(a, b, s) for a, b, s in SM52.get_matching_blocks() if s > 0]
OPS3 = []
pa = pb = 0
for a, b, s in MB3 + [(len(PW3[0]), len(T1W3), 0)]:
    if a > pa and b > pb:
        OPS3.append((u'replace', pa, a, pb, b))
    elif a > pa:
        OPS3.append((u'delete', pa, a, pb, pb))
    elif b > pb:
        OPS3.append((u'insert', pa, pa, pb, b))
    if s > 0:
        OPS3.append((u'equal', a, a + s, b, b + s))
    pa, pb = a + s, b + s
assert [x[0] for x in OPS3] == [x[0] for x in SMNJ.get_opcodes()], u'相同段还原与 autojunk 关档不一致'
put('blk_tcp_op_tags', [x[0] for x in OPS3])
put('blk_tcp_op_n', len(OPS3))
put('blk_tcp_equal', sum([x[2] - x[1] for x in OPS3 if x[0] == u'equal']))
put('blk_tcp_equal_runs', len([x for x in OPS3 if x[0] == u'equal']))
put('blk_tcp_equal_max', max([x[2] - x[1] for x in OPS3 if x[0] == u'equal']))
put('blk_tcp_drop', sum([x[2] - x[1] for x in OPS3 if x[0] in (u'delete', u'replace')]))
put('blk_tcp_insert', sum([x[4] - x[3] for x in OPS3 if x[0] in (u'insert', u'replace')]))
put('blk_tcp_replace', len([x for x in OPS3 if x[0] == u'replace']))
put('blk_tcp_word_ledger', G['blk_tcp_equal'] + G['blk_tcp_drop'] - len(PW3[0]))
put('blk_tcp_word_ledger2', G['blk_tcp_equal'] + G['blk_tcp_insert'] - len(T1W3))
put('blk_tcp_word_gap_ledger', G['blk_tcp_drop'] - G['blk_tcp_insert'] - (len(PW3[0]) - len(T1W3)))
put('blk_tcp_char_drop', sum([len(u' '.join(PW3[0][x[1]:x[2]])) + (1 if x[2] < len(PW3[0]) else 0)
                              for x in OPS3 if x[0] in (u'delete', u'replace')]))
put('blk_tcp_char_insert', sum([len(u' '.join(T1W3[x[3]:x[4]])) + (1 if x[4] < len(T1W3) else 0)
                               for x in OPS3 if x[0] in (u'insert', u'replace')]))
put('blk_tcp_naked_chars', len(tag_strip3(PTXT3[1])))
put('blk_tcp_char_ledger', (G['blk_chars'][0] - G['blk_tcp_char_drop'] + G['blk_tcp_char_insert']
                            - G['blk_tcp_naked_chars']))
put('blk_tcp_verbatim_sub', 1 if T1W3 and u' '.join(T1W3) in tag_strip3(PTXT3[0]) else 0)
put('blk_words_per_row', [G['blk_words'][n] // G['blk_rows'][n] for n in range(5)])
put('blk_is_one_line', [1 if G['blk_rows'][n] == 1 else 0 for n in range(5)])
put('blk_one_line_n', sum(G['blk_is_one_line']))

# ---------- 答句行号由发射侧的行表重导一遍 ⇎ 与建条侧对拍 ----------
put('ans_head', [LOW_SH3[i].find(p3(WIN[i])) for i in range(NSRC)])
put('ans_head_line', [line3(i, a) for i, a in enumerate(G['ans_head'])])
put('ans_tail_line', [line3(i, a + len(p3(WIN[i])) - 1) for i, a in enumerate(G['ans_head'])])
put('ans_needle_span', [G['ans_tail_line'][i] - G['ans_head_line'][i] + 1 for i in range(NSRC)])
put('ans_sent_at', [LOW_SH3[i].find(p3(G['ans'][i])) for i in range(NSRC)])
put('ans_sent_line', [line3(i, G['ans_sent_at'][i]) for i in range(NSRC)])
put('ans_sent_end', [line3(i, G['ans_sent_at'][i] + len(p3(G['ans'][i])) - 1) for i in range(NSRC)])
put('ans_sent_span', [G['ans_sent_end'][i] - G['ans_sent_line'][i] + 1 for i in range(NSRC)])
put('ans_span_ind', [len([1 for a in FD3[i]
                          if G['ans_head_line'][i] <= a[0] <= G['ans_tail_line'][i]]) for i in range(NSRC)])
put('ans_line_close', sum([abs(G['ans_sent_line'][i] - G['mk_ans_sent_line'][i]) for i in range(NSRC)]))
put('ans_span_close', sum([abs(G['ans_sent_span'][i] - G['mk_ans_sent_span'][i]) for i in range(NSRC)]))
put('ans_needle_gap', [G['ans_span'][i] - G['ans_needle_span'][i] for i in range(NSRC)])
put('ans_row_ledger', [G['ans_sent_end'][i] - G['ans_sent_line'][i] + 1
                       - len([1 for a in FD3[i] if G['ans_sent_line'][i] <= a[0] <= G['ans_sent_end'][i]])
                       for i in range(NSRC)])

# ---------- 切开判词: 逐行漏读的针 ⇎ 被编号切开的针 ----------
SPLITREC = []
WRAPK2 = sorted([k for i, k in G['role_wrap_keys']])
TAGCUTK = [k for (i, k) in G['role_tagcut_keys']]
assert WRAPK2 == sorted([k for i, k in dv(FLAT[u'role_wrap_keys'])])
assert not (set(WRAPK2) & set(TAGCUTK))
for i, k in G['role_wrap_keys']:
    h, t, head, tail = split_pieces3(i, ROLEN[k])
    SPLITREC.append((k, i, h, t, len(head), len(tail)))
put('split_k', [x[0] for x in SPLITREC])
put('split_lbl', [LBL[x[1]] for x in SPLITREC])
put('split_head', [x[2] for x in SPLITREC])
put('split_tail', [x[3] for x in SPLITREC])
put('split_span', [x[3] - x[2] + 1 for x in SPLITREC])
put('split_span_tot', sum(G['split_span']))
put('split_head_chars', [x[4] for x in SPLITREC])
put('split_tail_chars', [x[5] for x in SPLITREC])
put('split_n', len(SPLITREC))
put('split_rows_tot', sum(G['split_head_chars']) + sum(G['split_tail_chars']))
put('split_full_on_head', sum([line_holds3(x[1], x[2], ROLEN[x[0]]) for x in SPLITREC]))
put('split_half_ok', sum([line_holds3(x[1], x[2], p3(split_pieces3(x[1], ROLEN[x[0]])[2]))
                          for x in SPLITREC]))
put('split_gap_rows', [len([1 for n in range(x[2] + 1, x[3]) if shell3(L3[x[1]][n - 1], FAM[x[1]])])
                       for x in SPLITREC])
put('split_wrap_n', len(WRAPK2))
put('split_tagcut_n', len(TAGCUTK))
put('split_ledger', G['split_n'] - G['role_line_miss_n'])
put('split_adj_n', len([x for x in SPLITREC if x[3] - x[2] == 1]))

# ---------- 被编号标注切开的针: 摘壳面读不通 ⇎ 去标注才读通 ----------
def kept3(face):
    """保留字符的下标表: 布尔掩码上挑非覆盖位(建条侧是游标 k 逐段 append)"""
    M = [True] * len(face)
    for m in TAGR.finditer(face):
        for k in range(m.start(), m.end()):
            M[k] = False
    return [k for k in range(len(M)) if M[k]]


KEEP3 = [kept3(SHC3[i]) for i in range(NSRC)]
put('tag_eaten', [len(SHC3[i]) - len(SHTAGC3[i]) for i in range(NSRC)])
for i in range(NSRC):
    assert len(KEEP3[i]) == len(SHTAGC3[i]), i
    assert u''.join(SHC3[i][k] for k in KEEP3[i]) == SHTAGC3[i], i


def row_of_fd3(i, n):
    return ROWMAP3[i][n]


def face_window3(i, a, ln):
    n, o = loc3(i, a)
    _, raw, f, ix = row_of_fd3(i, n)
    assert p3(f[o:o + ln]) == p3(SHC3[i][a:a + ln]), (LBL[i], n)
    e = min(o + ln, len(f)) - 1
    seg, s, t = win3(raw, ix[o], ix[e] + 1, 40)
    assert seg in raw, (LBL[i], n)
    return n, seg


TAGCUTREC = []
for i, k in G['role_tagcut_keys']:
    key = p3(ROLEN[k])
    p = LOW_TAG3[i].find(key)
    assert p >= 0 and LOW_SH3[i].find(key) < 0, (LBL[i], key)
    a, b = KEEP3[i][p], KEEP3[i][p + len(key) - 1] + 1
    tags = [(m.group(0), m.start(), m.end()) for m in TAGR.finditer(SHC3[i])
            if m.start() >= a and m.end() <= b]
    assert tags, (LBL[i], key)
    head, tail = SHC3[i][a:tags[0][1]], SHC3[i][tags[-1][2]:b]
    assert p3(head + tail) == key, (LBL[i], key, head, tail)
    hn, hw = face_window3(i, a, len(head))
    tn, tw = face_window3(i, tags[-1][2], len(tail))
    TAGCUTREC.append((k, i, hn, tn, head, tail, [x[0] for x in tags],
                      b - a - len(key), sum(len(x[0]) for x in tags), hw, tw))
put('tagcut_k', [x[0] for x in TAGCUTREC])
put('tagcut_lbl', [LBL[x[1]] for x in TAGCUTREC])
put('tagcut_needle', [ROLEN[x[0]] for x in TAGCUTREC])
put('tagcut_head', [x[4] for x in TAGCUTREC])
put('tagcut_tail', [x[5] for x in TAGCUTREC])
put('tagcut_head_row', [x[2] for x in TAGCUTREC])
put('tagcut_tail_row', [x[3] for x in TAGCUTREC])
put('tagcut_span', [x[3] - x[2] + 1 for x in TAGCUTREC])
put('tagcut_mid', [u''.join(x[6]) for x in TAGCUTREC])
put('tagcut_mid_n', [len(x[6]) for x in TAGCUTREC])
put('tagcut_eaten', [x[7] for x in TAGCUTREC])
put('tagcut_tag_chars', [x[8] for x in TAGCUTREC])
put('tagcut_mid_chars', [len(x[9]) + len(x[10]) for x in TAGCUTREC])
put('tagcut_win_head', [x[9] for x in TAGCUTREC])
put('tagcut_win_tail', [x[10] for x in TAGCUTREC])
put('tagcut_n', len(TAGCUTREC))
put('tagcut_ledger', [x[7] - x[8] for x in TAGCUTREC])
put('tagcut_eaten_close', [G['tag_eaten'][i]
                           - sum([len(m.group(0)) for m in TAGR.finditer(SHC3[i])]) for i in range(NSRC)])

# ---------- 被换行切开的义务词: 原面逐行现定位行对 ----------
def straddle3(i, nd):
    """上一行以此式前词收尾 ⇎ 下一枚非空行以后词起头: 中间只允许空行"""
    w = p3(nd).split(u' ')
    out, m = [], 0
    while m < len(L3[i]):
        pf = p3(L3[i][m])
        if not pf.endswith(w[0]):
            m += 1
            continue
        k, blanks = m + 1, 0
        while k < len(L3[i]) and fold3(L3[i][k]) == u'':
            blanks += 1
            k += 1
        if k < len(L3[i]) and p3(L3[i][k]).startswith(u' '.join(w[1:])):
            out.append((m + 1, k + 1, blanks))
        m += 1
    return out


TSK = [k for k in range(5) if sum([G['tone_wrap_gain'][i * 5 + k] for i in range(NSRC)])]
put('tone_straddle_nd', [TONE[k] for k in TSK])
TSP = []
for kk in TSK:
    for i in range(NSRC):
        for (mh, mt, bl) in straddle3(i, TONE[kk]):
            TSP.append((LBL[i], kk, mh, mt, bl))
put('tone_straddle', [len([x for x in TSP if x[0] == LBL[i]]) for i in range(NSRC)])
put('tone_straddle_by_kind', [len([x for x in TSP if x[1] == kk]) for kk in TSK])
put('tone_straddle_n', len(TSP))
put('tone_straddle_adj', len([x for x in TSP if x[3] - x[2] == 1]))
put('tone_straddle_blank', G['tone_straddle_n'] - G['tone_straddle_adj'])
put('tone_straddle_blank_rows', sum([x[4] for x in TSP]))
put('tone_straddle_gap_shell', sum([len([1 for n in range(x[2], x[3] - 1)
                                        if fold3(L3[LBL.index(x[0])][n - 1]) != u'']) for x in TSP]))
put('tone_wrap_gain_mn', [G['tone_wrap_gain'][i * 5 + 1] for i in range(NSRC)])
put('tone_straddle_ledger', sum(G['tone_wrap_gain_mn']) - G['tone_straddle_n'])

# ---------- 行号尺往返: 段窗首末行回原文件那一行自验 ----------
def needle_at3(i, ln, nd, side):
    key = p3(nd)
    w = key.split(u' ')
    for m in range(len(ALN3[i])):
        if ALN3[i][m][0] != ln:
            continue
        p = p3(ALN3[i][m][2])
        if key in p:
            return 2
        prev = p3(ALN3[i][m - 1][2]) if m else u''
        nxt = p3(ALN3[i][m + 1][2]) if m + 1 < len(ALN3[i]) else u''
        for j in range(1, len(w)):
            if side == u'head' and p.endswith(u' '.join(w[:j])) and nxt.startswith(u' '.join(w[j:])):
                return 1
            if side == u'tail' and p.startswith(u' '.join(w[j:])) and prev.endswith(u' '.join(w[:j])):
                return 1
        return 0
    raise AssertionError(u'行号无对应原行 %s %d' % (LBL[i], ln))


SEGRT = []
for n, (i, s, e) in enumerate(PINS):
    if PB3[n][1] < 0:
        continue
    SEGRT.append((i, PB3[n][1], p3(s), u'head'))
    SEGRT.append((i, PB3[n][2], p3(e), u'tail'))
put('seg_rt', [needle_at3(i, ln, nd, sd) for i, ln, nd, sd in SEGRT])
put('seg_rt_n', len(G['seg_rt']))
put('seg_rt_ok', len([x for x in G['seg_rt'] if x]))
put('seg_rt_whole', len([x for x in G['seg_rt'] if x == 2]))
put('seg_rt_cut', len([x for x in G['seg_rt'] if x == 1]))
put('seg_rt_head', len([1 for (i, ln, nd, sd), v in zip(SEGRT, G['seg_rt']) if sd == u'head' and v]))
put('seg_rt_tail', G['seg_rt_ok'] - G['seg_rt_head'])
put('blk_head_row', [PB3[n][1] for n in range(5)])
put('blk_tail_row', [PB3[n][2] for n in range(5)])
put('blk_head_gap', [G['blk_head_row'][n] - G['ans_anchor_line'][n] for n in range(5)])
put('blk_ans_inside', [1 if (G['blk_lo'][n] <= G['ans_anchor_line'][n]
                             and G['ans_sent_end'][n] <= G['blk_hi'][n]) else 0 for n in range(5)])

# ---------- 模板长行池: 由 “行长 → 落在哪几份” 的隶属表现导组合数 ----------
POOL3 = [set([fold3(x) for _, x in ROWS3[i] if len(fold3(x)) >= 40]) for i in range(NSRC)]
POOL253 = [set([fold3(x) for _, x in ROWS3[i] if len(fold3(x)) >= 25]) for i in range(NSRC)]
MEMB = {}
for i in range(NSRC):
    for x in POOL3[i]:
        MEMB.setdefault(x, []).append(i)
PAIRS3 = [(a, b) for a in range(NSRC) for b in range(a + 1, NSRC)]
TRIPS3 = [(a, b, c) for a in range(NSRC) for b in range(a + 1, NSRC) for c in range(b + 1, NSRC)]
QUADS3 = [(a, b, c, d) for a in range(NSRC) for b in range(a + 1, NSRC)
          for c in range(b + 1, NSRC) for d in range(c + 1, NSRC)]
PAIRCNT = dict((k, 0) for k in PAIRS3)
TRIPCNT = dict((k, 0) for k in TRIPS3)
QUADCNT = dict((k, 0) for k in QUADS3)
for x, ds in MEMB.items():
    for combo in IT.combinations(ds, 2):
        PAIRCNT[combo] += 1
    for combo in IT.combinations(ds, 3):
        TRIPCNT[combo] += 1
    for combo in IT.combinations(ds, 4):
        QUADCNT[combo] += 1
put('pool_n', [len(x) for x in POOL3])
put('pool_sum', sum(G['pool_n']))
put('pool_union', len(MEMB))
put('pool_raw_rows', [len([1 for _, x in ROWS3[i] if len(fold3(x)) >= 40]) for i in range(NSRC)])
put('pool_dup', sum(G['pool_raw_rows']) - G['pool_sum'])
put('pool_n25', [len(x) for x in POOL253])
put('pool_union25', len(set([x for s in POOL253 for x in s])))
put('pool_widen', G['pool_union25'] - G['pool_union'])
put('pool_tier', [len([x for x, ds in MEMB.items() if len(ds) == m]) for m in range(1, NSRC + 1)])
put('pool_pair', dict((u'%s-%s' % (LBL[a], LBL[b]), PAIRCNT[(a, b)]) for a, b in PAIRS3))
put('pool_trip', dict((u'%s-%s-%s' % (LBL[a], LBL[b], LBL[c]), TRIPCNT[(a, b, c)]) for a, b, c in TRIPS3))
put('pool_quad', dict((u'%s-%s-%s-%s' % (LBL[a], LBL[b], LBL[c], LBL[d]), QUADCNT[(a, b, c, d)])
                      for a, b, c, d in QUADS3))
# 隶属表导出的组合数 ⇎ 直接求交: 两条通道必须报同一个数
assert all([G['pool_pair'][u'%s-%s' % (LBL[a], LBL[b])] == len(POOL3[a] & POOL3[b]) for a, b in PAIRS3])
assert all([G['pool_trip'][u'%s-%s-%s' % (LBL[a], LBL[b], LBL[c])]
            == len(POOL3[a] & POOL3[b] & POOL3[c]) for a, b, c in TRIPS3])
put('pool_pair_tot', sum(G['pool_pair'].values()))
put('pool_trip_tot', sum(G['pool_trip'].values()))
put('pool_quad_tot', sum(G['pool_quad'].values()))
put('pool_ie_close', G['pool_sum'] - G['pool_pair_tot'] + G['pool_trip_tot'] - G['pool_quad_tot']
                     - G['pool_union'])
OLDSET3 = set([LBL[i] for i in OLD])
NEWSET3 = set([LBL[i] for i in NEW])
OLDPAIR = [k for k in G['pool_pair'] if any(z in OLDSET3 for z in k.split(u'-'))]
NEWPAIR = [k for k in G['pool_pair'] if all(z in NEWSET3 for z in k.split(u'-'))]
put('pool_pair_by', [G['pool_pair'][u'%s-%s' % (LBL[a], LBL[b])] for a, b in PAIRS3])
put('pool_pair_old_keys', sorted(OLDPAIR))
put('pool_pair_new_keys', sorted(NEWPAIR))
put('pool_pair_old', sum([G['pool_pair'][k] for k in OLDPAIR]))
put('pool_pair_new', sum([G['pool_pair'][k] for k in NEWPAIR]))
put('pool_pair_old_n', len([k for k in OLDPAIR if G['pool_pair'][k] == 0]))
put('pool_max_pair', max(G['pool_pair'].values()))
put('pool_min_pair_new', min([G['pool_pair'][k] for k in NEWPAIR]))
put('pool_tier_close', sum(G['pool_tier']) - G['pool_union'])
put('pool_sum_close', sum([G['pool_tier'][m] * (m + 1) for m in range(NSRC)]) - G['pool_sum'])


def toned3(s):
    return sum([ub3(s, w) for w in TONE]) > 0


SHARED = set([x for x, ds in MEMB.items() if len([d for d in ds if d in NEW]) >= 2])
put('pool_shared_new', len(SHARED))
put('pool_shared_toned', len([x for x in SHARED if toned3(x)]))
put('pool_shared_rfcline', len([x for x in SHARED if u'RFC' in x]))
put('pool_shared_status', len([x for x in SHARED if u'status of this document' in x.lower()]))
put('pool_shared_bom', len([x for x in SHARED if u'﻿' in x]))
put('pool_old_toned', len([x for x in POOL3[0] if toned3(x)]))
put('pool_new_toned', sum([len([x for x in POOL3[i] if toned3(x)]) for i in NEW]))
OSHAL = POOL3[0] & POOL3[1]
put('pool_old_shared', len(OSHAL))
put('pool_old_shared_pres', [len(MEMB[x]) for x in sorted(OSHAL)])
put('pool_old_shared_toned', len([x for x in OSHAL if toned3(x)]))
put('pool_old_shared_status', len([x for x in OSHAL if u'status of this document' in x.lower()]))
put('pool_old_shared_rfcline', len([x for x in OSHAL if u'RFC' in x]))
put('pool_old_shared_bom', len([x for x in OSHAL if u'﻿' in x]))
put('pool_all_five', G['pool_tier'][NSRC - 1])
put('pool_new_four', G['pool_tier'][3])

# ---------- 转置尺: 族量横过来按份读 ⇎ 增益按枚记两把口径 ----------
put('dur_docs', [[G['dur'][i][k] for i in range(NSRC)] for k in range(len(DUR))])
put('numw_docs', [[G['numw'][i][k] for i in range(NSRC)] for k in range(len(NUMW))])
put('spell_docs', [[G['spell'][i][k] for i in range(NSRC)] for k in range(len(SPELL))])
put('tone_docs', [[G['tone_sh'][i][k] for i in range(NSRC)] for k in range(5)])
put('num_docs', [[G['num'][i][k] for i in range(NSRC)] for k in range(len(NUMLIT))])
put('num_cold', [NUMLIT[k] for k in range(len(NUMLIT)) if sum(G['num_docs'][k]) == 0])
put('num_cold_n', len(G['num_cold']))
put('num_hot_n', len(NUMLIT) - G['num_cold_n'])
put('num_own_tot', sum([len(x) for x in G['num_own']]))
put('spell_tot_docs', [sum(x) for x in G['spell_docs']])
put('dur_tot', [sum(x) for x in G['dur_docs']])
put('role_by_face', [[sum(G['role_line'][i]) if k == 0 else sum(G['role_fold'][i]) if k == 1
                      else sum(G['role_sh'][i]) if k == 2 else sum(G['role_tag'][i])
                      for i in range(NSRC)] for k in range(4)])
put('face_tot', [sum(G['role_by_face'][k]) for k in range(4)])
put('face_gain', [G['face_tot'][k] - G['face_tot'][k - 1] for k in range(1, 4)])
put('face_mono', sum([1 for k in range(1, 4) if G['face_tot'][k] >= G['face_tot'][k - 1]]))
put('gain_fold', [G['role_fold'][i][k] - G['role_line'][i][k] for i in range(NSRC) for k in range(NR)])
put('gain_sh', [G['role_sh'][i][k] - G['role_fold'][i][k] for i in range(NSRC) for k in range(NR)])
put('gain_tag', [G['role_tag'][i][k] - G['role_sh'][i][k] for i in range(NSRC) for k in range(NR)])
put('gain_fold_tot', sum(G['gain_fold']))
put('gain_sh_tot', sum(G['gain_sh']))
put('gain_tag_tot', sum(G['gain_tag']))
put('gain_fold_key', len([x for x in G['gain_fold'] if x > 0]))
put('gain_tag_key', len([x for x in G['gain_tag'] if x > 0]))
put('gain_sh_dup', sum([G['role_sh'][i][k] - G['role_fold'][i][k] for i in range(NSRC)
                        for k in range(NR) if G['role_fold'][i][k] > 0]))
put('gain_fold_dup', sum([G['role_fold'][i][k] - G['role_line'][i][k] for i in range(NSRC)
                          for k in range(NR) if G['role_line'][i][k] > 0]))
put('ans_words_tot', sum(G['ans_words']))
put('sec_lines_tot2', sum(G['sec_lines']))
put('sec_chars_tot', sum(G['sec_chars']))

# ---------- 新句在面上的位置: 去编号面命中后经编号对照表映回摘壳面 ----------
OVLNEW = [z for z in A2T if z not in A1 and canon3(z) not in A1C and canon3(z) not in D1C]
put('ovl_new_tagloc', [LOW_TAG3[1].find(p3(z)) for z in OVLNEW])
assert min(G['ovl_new_tagloc']) >= 0, [z[:40] for z in OVLNEW]
put('ovl_new_loc', [KEEP3[1][p] for p in G['ovl_new_tagloc']])
put('ovl_new_end', [KEEP3[1][p + len(p3(z)) - 1] for p, z in zip(G['ovl_new_tagloc'], OVLNEW)])
put('ovl_new_lines', [line3(1, a) for a in G['ovl_new_loc']])
put('ovl_new_rows', [line3(1, e) - line3(1, a) + 1
                     for a, e in zip(G['ovl_new_loc'], G['ovl_new_end'])])
put('ovl_new_n', len(OVLNEW))
put('ovl_new_close', G['ovl_new'] - G['ovl_disc_promoted'] - G['ovl_new_n'])
put('ovl_new_tagcut', [len([1 for m in TAGR.finditer(SHC3[1])
                            if a <= m.start() and m.end() <= e + 1])
                       for a, e in zip(G['ovl_new_loc'], G['ovl_new_end'])])

# ---------- 编码区锚账: 手写配对扫描 ⇎ 双轨归属 ----------
MD = io.open(ENTRY, encoding=u'utf-8').read()
_i0 = MD.index(u'## ⟪BabelTele⟫')
ENC = MD[MD.index(NL, _i0) + 1:MD.index(u'## ⛓解读注')].rstrip(NL)


def my_cites(s):
    """手写扫锚壳: 源标签 ⇎ 引文各自取夹在两对符号之间的串, “⟧”与“⟨”之间只许夹一枚空格也没有"""
    out, i = [], 0
    while True:
        a = s.find(u'⟦', i)
        if a < 0:
            return out
        b = s.find(u'⟧', a)
        c = s.find(u'⟨', b) if b >= 0 else -1
        d = s.find(u'⟩', c) if c >= 0 else -1
        if b < 0 or d < 0 or c != b + 1:
            raise AssertionError(u'锚壳不成对 @%d' % a)
        out.append((s[a + 1:b], s[c + 1:d]))
        i = d + 1


CITES = my_cites(ENC)
RE_PAIR = re.findall(u'⟦(' + u'|'.join(TAGS) + u')⟧⟨([^⟨⟩]+)⟩', ENC)
assert CITES == [(x, y) for x, y in RE_PAIR], (len(CITES), len(RE_PAIR))
USED = len([c for c in ENC if c == u'⟨'])
ANCHS = []
for _t, _a in CITES:
    if _a not in ANCHS:
        ANCHS.append(_a)
DIST = len(ANCHS)
TAGN = dict((t, len([x for x in CITES if x[0] == t])) for t in TAGS)
ERR = [x for x in CITES if p3(x[1]) not in FAN3G[IDX[x[0]]]]
MISSLINE = [x for x in CITES if x[1] not in ANSET3[IDX[x[0]]] and p3(x[1]) not in ROWSRAW3[IDX[x[0]]]]
assert not ERR, ERR[:2]
assert not MISSLINE, MISSLINE[:2]
HITC = dict((a, tuple(i for i in range(NSRC) if p3(a) in FAN3G[i])) for a in ANCHS)
put('anchor_total', USED)
put('anchor_distinct', DIST)
put('anchor_err', len(ERR))
put('anchor_single', len([a for a in ANCHS if len(HITC[a]) == 1]))
put('anchor_cross', len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC]))
put('anchor_all5', len([a for a in ANCHS if len(HITC[a]) == NSRC]))
put('checks', DIST * NSRC)
put('enc_chars', len([c for c in ENC if c != NL]))
for t in TAGS:
    put(u'tag_' + t, TAGN[t])
assert G[u'anchor_single'] + G[u'anchor_cross'] + G[u'anchor_all5'] == DIST
SEGDOC = defaultdict(set)
for _t, _a in CITES:
    SEGDOC[IDX[_t]].add(_a)

# ---------- 行号账回读: 发射遍记的 120 行账 ⇎ 本遍自己的行号尺 ⇎ 窗口尺 ----------
# 候选针串不手打: 从两遍源码的全部字符串字面量 ⇎ ast 摘到的定义表 ⇎ checks/采集读数里递归收串,
# 再补上发射遍 AF() 的退让档(长针截前 n 词 ⇎ 截后 n 词)——日志里的键是“那一枚被搜的针”的前 34 字符
def _cc(v, sink):
    if isinstance(v, type(u'')):
        if len(v) >= 4:
            sink.add(v)
    elif isinstance(v, (list, tuple)):
        for y in v:
            _cc(y, sink)
    elif isinstance(v, dict):
        for kk, vv in v.items():
            _cc(str(kk), sink)
            _cc(vv, sink)


CAND = set()
for _src in (MS, EM):
    for _nd in ast.walk(ast.parse(_src)):
        _cc(_nd.value if isinstance(_nd, ast.Constant) else None, CAND)
for _tab in (ROLEN, TONE, WIN, NEG, SECND, SECTTL, CITED, PARA, SAMEK, SAMEK2, PKND, PINS, KWK,
             SPELL, DUR, NUMW, UNITW, UNITW_S, NUMLIT, UORD, LBL, FAM, CH, MEA, DER):
    _cc(_tab, CAND)
SFX = (u'[首]', u'[末]', u'[上]', u'[下]', u'[编号前]', u'[编号后]')


def _cut(pool):
    """发射遍 AF() 的退让档: 长针截前 n 词 ⇎ 截后 n 词(n>=2, 单词档在长针上一律算失败)"""
    out = set(pool)
    for c in pool:
        w = c.split(u' ')
        for n in range(2, len(w) + 1):
            out.add(u' '.join(w[:n]))
            out.add(u' '.join(w[len(w) - n:]))
    return out


CUTS = _cut(CAND)
# 发射遍有几枚针是先把式子归一(小写 ⇎ 折平)再交进 AN() 的, 日志里的键因此是小写形: 两形都收
CUTS |= _cut(set(p3(c) for c in CUTS))
# 日志里的键是被搜那枚针的前 34/30/14 字符, 新句那四枚更是 26 字符(AF(1, z[:26], 行号)): 四个档都建索引
PK = defaultdict(set)
for _c in CUTS:
    for _k in (14, 26, 30, 34):
        PK[_c[:_k]].add(_c)
    PK[_c].add(_c)


def an3(i, nd, exact=False, lo=0, lim=LIMW):
    """本遍的锚导出尺(不写日志): 摘壳行折平串上找针, 命中区间经字符来源表映回原行按整词开窗"""
    key = p3(nd)
    hits = []
    for n, x, f, ix in ALN3[i]:
        if n < lo:
            continue
        if exact:
            if f != key:
                continue
            a, b = 0, len(f)
        else:
            k = f.find(key)
            if k < 0:
                continue
            a, b = k, k + len(nd)
        seg, s, e = win3(x, ix[a], ix[min(b, len(ix)) - 1] + 1, lim)
        hits.append((n, seg))
    return hits


def pair_pieces3(i, mh, mt, nd):
    """义务词跨行的两半(发射遍 pair_anchor 的第二把尺): 上半取该式前词所在的整词窗口, 下半取后词的"""
    w = p3(nd).split(u' ')
    x, y = L3[i][mh - 1], L3[i][mt - 1]
    a = x.lower().rfind(w[0])
    if a < 0:
        raise AssertionError(u'上半无前词 %s %d' % (LBL[i], mh))
    hx, _, _ = win3(x, a, a + len(w[0]), 46)
    b = y.lower().find(u' '.join(w[1:]))
    if b < 0:
        raise AssertionError(u'下半无后词 %s %d' % (LBL[i], mt))
    tx, _, _ = win3(y, b, b + len(u' '.join(w[1:])), 46)
    assert hx in x and tx in y
    return hx, tx


SEGOK = defaultdict(set)
AL = [tuple(x) for x in CH[u'anchor_lines']]
ALD = sorted(set(AL))
FAM_OF = dict()
for _l, _k, _n, _h in ALD:
    _s = u'plain'
    for _x in SFX:
        if _k.endswith(_x):
            _s = _x
    FAM_OF[(_l, _k)] = _s
PL = [x for x in ALD if FAM_OF[(x[0], x[1])] == u'plain']
REPL = 0
PLAINFAIL = []
for _l, _k, _n, _h in PL:
    i = IDX[_l]
    got = None
    for _c in sorted(PK[_k]):
        for _ex in (False, True):
            for _lo in (0, _n):
                hh = an3(i, _c, _ex, _lo)
                if hh and hh[0][0] == _n and len(hh) == _h and hh[0][1] in SEGDOC[i]:
                    got = (_c, _ex, _lo, hh[0][1])
                    break
            if got:
                break
        if got:
            break
    if got is None:
        PLAINFAIL.append((_l, _k, _n, _h))
        continue
    REPL += 1
    SEGOK[i].add(got[3])
assert not PLAINFAIL, PLAINFAIL[:4]

SPLITG = {}
for _l, _k, _n, _h in ALD:
    _s = FAM_OF[(_l, _k)]
    if _s in (u'[首]', u'[末]'):
        SPLITG.setdefault((_l, _k[:-3]), [0, 0])[0 if _s == u'[首]' else 1] = _n
SPF = []
for (_l, _base), (_lh, _lt) in sorted(SPLITG.items()):
    assert _lh and _lt, (_l, _base)
    i = IDX[_l]
    got = None
    for _c in sorted(PK[_base]):
        try:
            _h, _t, _hd, _tl = split_pieces3(i, _c)
        except Exception:
            continue
        if (_h, _t) == (_lh, _lt) and _hd in SEGDOC[i] and _tl in SEGDOC[i]:
            got = (_c, _hd, _tl)
            break
    if got is None:
        SPF.append((_l, _base, _lh, _lt))
        continue
    REPL += 2
    SEGOK[i].add(got[1])
    SEGOK[i].add(got[2])
assert not SPF, SPF[:4]

# 义务词跨行的一组两枚不按 (份, 式) 归并: 同一个 “MUST NOT” 在同一份里可以跨两对行(1122 的两条广播地址行),
# 归并会把它们挤成一档——逐枚账行号, 每枚回本遍 straddle3 的配对表里认领自己那一行
STRD = [x for x in ALD if FAM_OF[(x[0], x[1])] in (u'[上]', u'[下]')]
PAIRSEG = {}
PF = []
for _l, _k, _n, _h in STRD:
    i = IDX[_l]
    _side = 2 if FAM_OF[(_l, _k)] == u'[上]' else 3
    _base = _k[:-3]
    got = None
    for _t in TSP:
        if _t[0] != _l or _t[_side] != _n:
            continue
        _c = TONE[_t[1]]
        if p3(_c)[:14] != _base and _c[:14] != _base:
            continue
        if (_t[2], _t[3]) not in PAIRSEG:
            try:
                PAIRSEG[(_t[2], _t[3])] = pair_pieces3(i, _t[2], _t[3], _c)
            except Exception:
                continue
        _hx, _tx = PAIRSEG[(_t[2], _t[3])]
        if _hx in SEGDOC[i] and _tx in SEGDOC[i]:
            got = (_hx, _tx)
            break
    if got is None:
        PF.append((_l, _base, _n, _side))
        continue
    REPL += 1
    SEGOK[i].add(got[0])
    SEGOK[i].add(got[1])
assert not PF, PF[:4]

TG = {}
for _l, _k, _n, _h in ALD:
    _s = FAM_OF[(_l, _k)]
    if _s in (u'[编号前]', u'[编号后]'):
        TG.setdefault((_l, _k[:-5]), [0, 0])[0 if _s == u'[编号前]' else 1] = _n
TF = []
for (_l, _base), (_ah, _at) in sorted(TG.items()):
    i = IDX[_l]
    got = None
    for _r in TAGCUTREC:
        if _r[1] == i and ROLEN[_r[0]][:30] == _base and (_r[2], _r[3]) == (_ah, _at) \
                and _r[9] in SEGDOC[i] and _r[10] in SEGDOC[i]:
            got = (_r[9], _r[10])
            break
    if got is None:
        TF.append((_l, _base, _ah, _at))
        continue
    REPL += 2
    SEGOK[i].add(got[0])
    SEGOK[i].add(got[1])
assert not TF, TF[:4]

# 段窗 ⇎ 切开清单 ⇎ 跨行两半这些自己算过的窗口也要进“本遍导出的引用串”, 否则正文引用无人认领
for (i, _s, _e), _p in zip(PINS, PB3):
    if _p[1] >= 0:
        SEGOK[i].add(_p[0])
for _r in TAGCUTREC:
    SEGOK[_r[1]].add(_r[4])
    SEGOK[_r[1]].add(_r[5])
UNCLAIMED = sorted(set([x for x in set(CITES) if x[1] not in SEGOK[IDX[x[0]]]]))
print(u'锚账: 日志 %d 行 ⇎ 去重 %d 档 ⇎ 本遍行号尺复现 %d 档 ⇎ 正文引用 %d 枚/未被本遍窗口认领 %d 枚'
      % (len(AL), len(ALD), REPL, USED, len(UNCLAIMED)))
print(u'  分档: 单行 %d ⇎ 换行两半 %d 对 ⇎ 义务词跨行 %d 枚 ⇎ 编号切开 %d 对'
      % (len(PL), len(SPLITG), len(STRD), len(TG)))
assert not UNCLAIMED, UNCLAIMED[:4]
assert REPL == len(PL) + 2 * (len(SPLITG) + len(TG)) + len(STRD) == len(ALD)
assert len(SPLITG) == G[u'split_n'] and len(STRD) == 2 * G[u'tone_straddle_n'] \
    and len(TG) == G[u'tagcut_n']
assert CH[u'anchor_ambiguous'] == len([x for x in AL if x[3] > 1])
assert G[u'anchor_total'] == sum(TAGN.values()) == len(CITES)

# ---------- 布尔门: 36 + 20 道的右式一律由源码 ast 摘出, 在本遍读数上重 eval ----------
MSA = ast.parse(MS)
EMA = ast.parse(EM)


def _subs(src, nm):
    out = []
    for _nd in src.body:
        if isinstance(_nd, ast.Assign) and isinstance(_nd.targets[0], ast.Subscript):
            _t = _nd.targets[0]
            if isinstance(_t.value, ast.Name) and _t.value.id == nm \
                    and isinstance(_t.slice, ast.Constant) and isinstance(_t.slice.value, type(u'')):
                out.append((_t.slice.value, ast.get_source_segment(src_code[nm], _nd.value)))
    return out


src_code = {u'CLOSE': MS, u'CLOSE2': EM}
CLOSE_SRC = _subs(MSA, u'CLOSE')
assert len(CLOSE_SRC) == 36 and len(set(k for k, _ in CLOSE_SRC)) == 36, len(CLOSE_SRC)
OLDSET3 = set(LBL[i] for i in OLD)
NEWSET3 = set(LBL[i] for i in NEW)
OLDPAIR3 = sorted([k for k in G[u'pool_pair'] if any(z in OLDSET3 for z in k.split(u'-'))])
NEWPAIR3 = sorted([k for k in G[u'pool_pair'] if all(z in NEWSET3 for z in k.split(u'-'))])
ENV = {u'F': G, u'G': G, u'NSRC': NSRC, u'OLD': OLD, u'NEW': NEW, u'FAM': FAM, u'L': L3,
       u'LBL': LBL, u'IDX': IDX, u'NUMLIT': NUMLIT, u'ROLEN': ROLEN, u'SHC': SHC3, u'TAGR': TAGR,
       u'TAGCUTREC': TAGCUTREC, u'OLDPAIR': OLDPAIR3, u'NEWPAIR': NEWPAIR3, u'pnorm': p3,
       u'sum': sum, u'len': len, u'all': all, u'any': any, u'max': max, u'min': min, u'abs': abs,
       u'range': range, u're': re, u'sorted': sorted, u'tuple': tuple, u'set': set, u'str': str,
       u'int': int, u'float': float, u'list': list, u'dict': dict, u'round': round}
CLOSEV = {}
for _k, _e in CLOSE_SRC:
    CLOSEV[_k] = 1 if eval(_e, ENV, ENV) else 0
put(u'bool_clos_n', len(CLOSE_SRC))
put(u'bool_clos_sum', sum(CLOSEV.values()))
assert G[u'bool_clos_sum'] == G[u'bool_clos_n'], [k for k, v in CLOSEV.items() if not v]

CLOSE2_SRC = _subs(EMA, u'CLOSE2')
assert len(CLOSE2_SRC) == 20 and len(set(k for k, _ in CLOSE2_SRC)) == 20, len(CLOSE2_SRC)
C2V = {}
for _k, _e in CLOSE2_SRC:
    C2V[_k] = 1 if eval(_e, ENV, ENV) else 0
    G[_k] = C2V[_k]
put(u'bool_clos2_n', len(CLOSE2_SRC))
put(u'bool_clos2_sum', sum(C2V.values()))
assert G[u'bool_clos2_sum'] == 20, [k for k, v in C2V.items() if not v]
put(u'bool_all_n', G[u'bool_clos_n'] + G[u'bool_clos2_n'])
put(u'bool_all_sum', G[u'bool_clos_sum'] + G[u'bool_clos2_sum'])

# ---------- 恒等式: 建条侧 37 条标量式 ⇎ 摘壳侧 45 条 V 形式, 右式同样从源码摘 ----------
ZSRC = []
for _nd in MSA.body:
    if isinstance(_nd, ast.Expr) and isinstance(_nd.value, ast.Call) \
            and isinstance(_nd.value.func, ast.Name) and _nd.value.func.id == u'Z':
        ZSRC.append((_nd.value.args[0].value, _nd.value.args[1].value))
assert len(ZSRC) == 37, len(ZSRC)
ZFAIL = [w for e, w in ZSRC if eval(e, ENV, ENV) != 0]
put(u'zid_scan_n', len(ZSRC))
assert not ZFAIL, ZFAIL[:3]

ZEXP_SRC = []
for _nd in EMA.body:
    if isinstance(_nd, ast.Expr) and isinstance(_nd.value, ast.Call) \
            and isinstance(_nd.value.func, ast.Name) and _nd.value.func.id == u'ZEXP':
        ZEXP_SRC.append((_nd.value.args[0].value, _nd.value.args[1].value))
assert len(ZEXP_SRC) == 45, len(ZEXP_SRC)
put(u'zid_scan2_n', len(ZEXP_SRC))

# ---------- V 形恒等式 ⇎ DERIV 复算点: 只走查表通道 ----------
NSV = dict(G)
B82V5 = lambda k, i=None: (NSV[k] if i is None else NSV[k][i])
ENVV = {u'B82V': B82V5, u'sum': sum, u'len': len, u'max': max, u'min': min, u'abs': abs,
        u'sorted': sorted, u'tuple': tuple, u'set': set, u'round': round, u'str': str,
        u'float': float, u'int': int, u'range': range, u'all': all, u'any': any, u'NSRC': NSRC}
ZVFAIL = [w for e, w in CH[u'zid'] if eval(e, ENVV, ENVV) != 0]
assert not ZVFAIL, ZVFAIL[:3]
assert len(CH[u'zid']) == G[u'zid_scan_n'] + G[u'zid_scan2_n'] == 82
ZF2 = [w for e, w in ZEXP_SRC if eval(e, ENVV, ENVV) != 0]
assert not ZF2, ZF2[:3]

DFL = []
DCITE = 0
for _kk in sorted(DER, key=lambda x: (len(x), x)):
    _v = DER[_kk]
    DCITE += _v.count(u"B82V(")
    if _kk == u'0':
        # “0” 键是全库零项之和: 本遍只把建条遍写死申报的那一格改成真量, 所以和就应当正好等于申报差额;
        # 别每一项都在下面的扁平对账里逐值核过, 对账为空 ⇒ 这一格的差额无人可推给别的键
        _z = eval(_v, ENVV, ENVV)
        _d = sum([G[k] - dv(FLAT[k]) for k in sorted(OVR) if k in G and isinstance(dv(FLAT[k]), int)])
        assert _z == _d == G[u'pick_needle_gap'], (_z, _d)
        continue
    try:
        _got = eval(_v, ENVV, ENVV)
    except Exception as _e:
        DFL.append((_kk, repr(_e)[:80]))
        continue
    if str(_got) != _kk and repr(_got) != _kk:
        DFL.append((_kk, _v[:90], str(_got)))
assert not DFL, DFL[:4]

# ---------- 与扁平表逐值对账 ----------
MISS = [k for k in G if k not in FLAT]
UNCOVER = [k for k in FLAT if k not in G and k != u'contract_n']
BAD = [(k, dv(FLAT[k]), dv(G[k])) for k in G
       if k in FLAT and k not in OVR and dv(FLAT[k]) != dv(G[k])]
assert not MISS, MISS[:6]
assert not UNCOVER, UNCOVER[:6]
assert not BAD, BAD[:6]
put(u'contract_n', len(G) + 1)
assert G[u'contract_n'] == len(FLAT) == 520
if OVRV:
    for x in OVRV:
        print(u'  申报建条未量: %s 建条=%s 复测=%s' % (x[0], repr(x[1])[:60], repr(x[2])[:60]))
print(u"第五段完成: 采集对账 %d/%d ⇎ 编码区 %d 字符 ⇎ 锚 %d 处/去重 %d 串/复核 %d ⇎ "
      u"布尔门 %d+%d 全绿 ⇎ 标量式 %d ⇎ V 形 %d 条归零 ⇎ DERIV %d 键/%d 处引用 ⇎ 扁平 %d 键全覆盖" % (
          G[u'pick_agree'], G[u'pick_same_n'], G[u'enc_chars'], G[u'anchor_total'], DIST, REPL,
          G[u'bool_clos_sum'], G[u'bool_clos2_sum'], G[u'zid_scan_n'], len(CH[u'zid']),
          len(DER), DCITE, len(FLAT)))







print(u'第五遍复测收账: 扁平 %d 键全部复算 ⇎ 不符 0 ⇎ 申报建条未量 %d 键' % (len(FLAT), len(OVRV)))

# ---------- ⛓解读注 ----------
J = lambda xs: u' ⇎ '.join(u'%s' % x for x in xs)


def QT(tag, s):
    assert p3(s) in FAN3G[IDX[tag]], u'本遍锚平面读不到: ' + s[:50]
    return u'⟦%s⟧⟨%s⟩' % (tag, s)


def QRAW(tag, s):
    assert any(s in a[1] for a in FD3[IDX[tag]]), u'原行里读不到: ' + s[:50]
    return u'⟦%s⟧⟨%s⟩' % (tag, s)


def cell(c):
    assert u'|' not in c, c[:70]
    assert c.count(u'`') % 2 == 0, c[:70]
    return c


def _fam3(k):
    for _s in SFX:
        if k.endswith(_s):
            return _s
    return u'plain'


LOGN = dict((f, len([x for x in AL if _fam3(x[1]) == f])) for f in ((u'plain',) + SFX))
LOGD = dict((f, len([x for x in ALD if _fam3(x[1]) == f])) for f in ((u'plain',) + SFX))
NIDX = dict((nd, k) for k, (nd, ex, f) in enumerate(NEG))
assert sum(LOGN.values()) == len(AL) == 120 and sum(LOGD.values()) == len(ALD) == 82
assert LOGN[u'[上]'] == 2 * LOGD[u'[上]'] and LOGN[u'[下]'] == 2 * LOGD[u'[下]']
assert LOGD[u'[首]'] == LOGD[u'[末]'] == len(SPLITG)
assert LOGD[u'[首]'] == LOGD[u'[末]'] == len(SPLITG)
assert LOGD[u'[上]'] == LOGD[u'[下]'] == G[u'tone_straddle_n']
assert (sum(G[u'role_gain_fold']), sum(G[u'role_gain_sh']), sum(G[u'role_gain_tag'])) \
    == (G[u'gain_fold_tot'], G[u'gain_sh_tot'], G[u'gain_tag_tot'])

# 建条遍那一格写死的证据在源码里, 不在本遍的读数里
assert re.search(u"F\\['pick_needle_gap'\\] = 0", MS), u'建条遍并非写死'
OVDELTA = sum([G[k] - dv(FLAT[k]) for k in sorted(OVR)
               if k in G and isinstance(dv(FLAT[k]), int)])
ZSUM = eval(DER[u'0'], ENVV, ENVV)
assert OVDELTA == ZSUM == G[u'pick_needle_gap']
GAPBAK = len([x for x in ROLEN if x not in PKND])
INTER = len(set(ROLEN) & set(PKND))

L2 = []
A = L2.append
A(u"第五遍(`corpus/_fill82.py`)换算法不换定义地把前四遍的量重跑一遍, 本遍是第三套实现, 独立处有十三项: "
  u"①行界三条通道并跑——`re.compile('\\n').split` ⇎ 建条侧 `str.split(NL)` ⇎ 本遍另数的 `splitlines` 档(它把 `\\x0c` 也当行界), "
  u"字节走 `os.stat` 的文件系统元数据 ⇎ 码位逐字符 `ord` 累加(建条侧是 `len`) ⇎ 换行枚走 `finditer('\\n')` 取位置再数; "
  u"②折平走 `re.finditer('\\S+')` 取词跨度再 `join`(建条侧 `re.split('\\s')` 过滤空段), 归一尺 `p3` 与建条侧 `pnorm` ⇎ `fold` 两轨逐份对拍; "
  u"③字面针起三档 `str.count`(非重叠) ⇎ `finditer('(?=针)')`(重叠) ⇎ 建条侧 `findall(re.escape)`; "
  u"④整词尺先把全串翻成“是否字母”布尔表, 命中后查表读左右邻(建条侧是断言正则与邻居手扫两把), 三把尺逐枚同数才入账; "
  u"⑤壳谓词第三档——`strip()` 后按“前缀字 ⇎ 末两 token ⇎ 年形切片”判, 既不跑采集侧的整行序列正则也不比建条侧的逐 token 形状; "
  u"⑥数值抽取用一条 `\\d[\\d.,]*` 正则代建条侧的手工扫, 单位词仍就地读; ⑦句界 `[.!?](?=[ \\n]|$)` 的 finditer 候选代逐字符扫; "
  u"⑧偏移→行号走 `bisect_right`(建条侧累积长度表 ⇎ 发射侧线性扫), 逐字符对照表由词跨度同时构造; "
  u"⑨切开判词的两半由词跨度表切, 段针自验改走“行折平串按词跨度拼回”档; ⑩对齐账由 `get_matching_blocks` 重造动作序列 ⇎ `autojunk=False` 档标签对拍 ⇎ 建条侧 `get_opcodes` 读数经扁平表逐值核过——三条通道同数才入账; "
  u"⑪池代数走 `Counter` 直方图 ⇎ 两两三三四四共用走“对文档下标的组合逐枚数共现”(建条侧是集合 `&`), 两条通道同数才算复核; "
  u"⑫定义复用而量不复用——`SPELL ⇎ TONE ⇎ DUR ⇎ NUMW ⇎ UNITW ⇎ NUMLIT ⇎ ROLEN ⇎ NEG ⇎ WIN ⇎ SECND ⇎ PINS ⇎ CITED ⇎ PARA ⇎ SAMEK ⇎ PKND` "
  u"由两遍源码 `ast` 摘, 谓词函数 `exec` 进来只用于对拍; %d+%d 道布尔门的右式 ⇎ %d+%d 条恒等式的表达式也从源码摘出在本遍读数上 eval, "
  u"%d 条 V 形 ⇎ %d 键 DERIV 从 `_b82checks.json` ⇎ `_deriv82.json` 回读; ⑬锚账不抄建条侧的针表: 候选针由两遍源码的全部字符串字面量递归收集, "
  u"过词前/后缀退让档与归一化变体, 再按日志器自己的截断长度 14/26/30/34 建索引(候选 %d 枚 ⇎ 退让后 %d 枚)。 "
  u"全部五份面共 %s 行 ⇎ %s 字符在这一套算法下重跑。" % (
      G[u'bool_clos_n'], G[u'bool_clos2_n'], G[u'zid_scan_n'], G[u'zid_scan2_n'], len(CH[u'zid']), len(DER),
      len(CAND), len(CUTS), format(sum(G[u'lines']), u','), format(sum(G[u'chars']), u',')))
A(u"本遍复算 %d 个键(扁平表 %d 键全覆盖 ⇎ 本遍独有 %d ⇎ 未复算 %d ⇎ 逐值不符 %d); 布尔门 %d 道(建条目侧 %d ⇎ 摘壳侧 %d)在本遍现算读数上全绿; "
  u"恒等式 %d+%d=%d 条归零(标量轨在第二遍源码上 eval ⇎ V 形轨查 `%s` 表), `checks` 里登记的 V 形 %d 条全真; DERIV %d 键 ⇎ %d 处引用重跑全对; "
  u"与采集遍逐键横比 %d/%d 键相符 ⇎ %d 键不符; 编码区 %d 非换行字符里 %d 处 `⟦…⟧⟨…⟩` 引文锚全部由本遍手写配对扫描取出并与正则档逐枚同序, "
  u"去重 %d 串 ⇎ 面内读不到 %d 枚 ⇎ 原行读不到 %d 枚 ⇎ 本遍行号尺复现 %d 档 ⇎ 正文引用未被本遍窗口认领 %d 枚 ⇎ 判定 %d 项门槛全绿。" % (
      len(G) - 1, len(FLAT), len(MISS), len(UNCOVER), len(BAD), G[u'bool_all_sum'], G[u'bool_clos_sum'],
      G[u'bool_clos2_sum'], G[u'zid_scan_n'], G[u'zid_scan2_n'], G[u'zid_scan_n'] + G[u'zid_scan2_n'], u'B82V',
      len(CH[u'zid']), len(DER), DCITE, G[u'pick_agree'], G[u'pick_same_n'], G[u'pick_diff'],
      G[u'enc_chars'], G[u'anchor_total'], G[u'anchor_distinct'], G[u'anchor_err'], len(MISSLINE), REPL,
      len(UNCLAIMED), G[u'contract_n']))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"版式⇎行界三把尺⇎换页账",
     u"正则切行 ⇎ 去回车后的同一切 ⇎ `splitlines` 档(认 `\\x0c`) 三条通道并跑; 字节走 `os.stat` ⇎ 码位逐字符 `ord` 累加 ⇎ 换行枚走 `finditer` 定位",
     u"字节 %s ⇎ 码位 %s ⇎ 正则切行 %s ⇎ 去回车 %s ⇎ splitlines %s ⇎ 换行枚 %s ⇎ 非空行 %s ⇎ 最长行 %s" % (
         J(G['bytes']), J(G['chars']), J(G['lines']), J(G['splitnl']), J(G['splitlines']),
         J(G['lf']), J(G['nonblank']), J(G['maxlen'])),
     u"回车 %s——五份全 LF 面, 所以“去回车前后同数”本身是判据而不是量; 收尾换行两条独立判法(末字符 ⇎ `endswith`)同值 %s/%s; "
     u"换页全在 1122: %s 枚里独占整行 %s ⇎ 紧接换行 %s ⇎ 落在文件尾 %s, 行首带换页 %s; splitlines 比前两把多 %d 行, 账(%s)全平——多出来的正是被 `\\x0c` "
     u"再断一次的那批; 页脚 %s 行 ⇎ 眉行 %s 行只在 1122。" % (
         J(G['cr']), J(G['trailing_nl']), J(G['end_nl']), J(G['ff']), J(G['ff_alone']), J(G['ff_before_nl']),
         J(G['ff_at_eof']), J(G['ff_led']), G['splitlines'][0] - G['lines'][0], J(G['row_form_ledger']),
         J(G['foot']), J(G['hdr_old']))),
    (u"页壳⇎页码两把尺⇎目录点线",
     u"壳谓词第三档: `strip()` 后按“前缀字 ⇎ 末两 token ⇎ 年形切片”判(采集侧整行序列正则 ⇎ 建条侧逐 token 形状); 页码尺逐字符判“数字或空白”加上升沿数段",
     u"壳行 %s ⇎ 空行 %s ⇎ 剥壳正文行 %s ⇎ 序列尺少读 %s ⇎ 页码紧尺 %s ⇎ 其中被壳认下 %s ⇎ 目录点线 严格 %s ⇎ 放宽 %s" % (
         J(G['shell_lines']), J(G['blank']), J(G['pp_rows']), J(G['pp_gap_rows']), J(G['pgnum']),
         J(G['pgnum_shell']), J(G['head_toc_leader_strict']), J(G['head_toc_leader_spaced'])),
     u"两套独立实现逐行同集: 分歧 %d 行 ⇎ 判定 %d ⇎ 三本账 %s; 序列尺少读的行数与非空壳(页脚+眉行)逐份相等(账 %s); 页码紧尺 %s 枚里被壳尺认下 %s 枚——多吃的是 "
     u"1122 第 5092 行的 RCV 表与 9293 的编号抬头/表体, 真页码反倒带方括号 “[Page n]” 不在这一式里; “[Page 1]” 那一式在折平面 %s 枚 ⇎ 摘壳面 %s 枚 ⇎ "
     u"它整行住在 %s 行(在壳尺之外的行数 %d ⇎ 被壳吃掉判定 %d)。" % (
         G['shell_pred_diff'], G['shell_pred_agree'], J(G['shell_ledger']), G['pp_gap_close'],
         J(G['pgnum']), J(G['pgnum_shell']), J(G['page_lit_fold']), J(G['page_lit_sh']),
         J(G['page_lit_rows']), G['page_lit_rows_shell'], G['page_lit_eaten_by_shell'])),
    (u"非ASCII⇎BOM⇎离 References 多远",
     u"非 ASCII 由 `finditer('[^\\x00-\\x7f]')` 在解码串上取偏移, 行号经“偏移→行”表映回(建条侧按行扫); BOM 单独按码位记, 折平后是否仍在另数一遍",
     u"BOM %s ⇎ 折平后仍在 %d 枚 ⇎ 非 ASCII %s ⇎ 逐行 %s ⇎ 不同码位 %d 个(全在新式四份 %d 个) ⇎ 署名行 %s ⇎ 参考条目行 %s ⇎ 地址块 %s ⇎ 其余 %s" % (
         J(G['bom']), G['bom_survives'], J(G['na_total']), J(G['na_lines']), G['na_cp_tot'], G['na_cp_new'],
         J(G['na_name_lines']), J(G['na_ref_entry_lines']), J(G['na_addr_bullet']), J(G['na_other'])),
     u"成分账 %s ⇎ 位置账 %s ⇎ 在 References 之前的 %s 全平; 该标题印出 %s 次(目录 %s ⇎ 正文 %s 行, 账 %s) ⇎ 首枚非 ASCII 距正文那次 %s 行——-1 是口径不存在"
     u"(1122 面上连标题也没有 ⇎ 9113 那一枚只在署名行、在标题之前); 署名抬头 %s 次 ⇎ %s 行; 码位比字节少 0 ⇎ 4 ⇎ 3 ⇎ 2 ⇎ 16, 旧式两份逐枚纯 ASCII。" % (
         J(G['na_ledger']), J(G['na_place_ledger']), J(G['na_before_ref']), J(G['ref_print_n']),
         J(G['ref_toc_line']), J(G['ref_body_line']), J(G['ref_ledger']), J(G['na_first_after_ref']),
         J(G['addr_head_n']), J(G['addr_head_line']))),
    (u"判词针 %d 枚×四档面" % NR,
     u"四张面各由不同构造路径独立拼出(逐行累加 ⇎ 词跨度拼全篇 ⇎ 剥壳后逐行折平拼 ⇎ 剥壳再去编号), 计数三档并立; 增益按“枚”记而非按“针”",
     u"原面逐行 %s ⇎ 全篇折平 %s ⇎ 摘壳折平 %s ⇎ 摘壳去编号 %s(四档合计 %s ⇎ 逐档增益 %s ⇎ 单调上升 %d/3) ⇎ 逐行读通 %d 枚 ⇎ 读不通 %d 枚" % (
         J(G['role_line_n']), J(G['role_fold_n']), J(G['role_sh_n']), J(G['role_tag_n']),
         J(G['face_tot']), J(G['face_gain']), G['face_mono'], G['role_line_read_n'], G['role_line_miss_n']),
     u"折平档净增 %d 枚 = 被硬换行切开 %d 枚 + 行内本就读通的针新增 %d 枚(有增益的份式格 %d 个) ⇎ 摘壳档净增 %d(壳切 %d ⇎ 折平档已读通而再增 %d) ⇎ "
     u"去编号档净增 %d(格 %d 个)——三档增益逐份登记(%s ⇎ %s ⇎ %s); 切开 %d 枚按份 %s ⇎ 壳切 %d 枚 ⇎ 编号切 %d 枚。" % (
         G['gain_fold_tot'], G['split_wrap_n'], G['gain_fold_dup'], G['gain_fold_key'],
         G['gain_sh_tot'], sum(G['role_shell_n']), G['gain_sh_dup'],
         G['gain_tag_tot'], G['gain_tag_key'], J(G['role_gain_fold']),
         J(G['role_gain_sh']), J(G['role_gain_tag']),
         G['split_n'], J(G['role_wrap_n']), sum(G['role_shell_n']), sum(G['role_tagcut_n']))),
    (u"切开 %d 枚⇎编号切开 %d 枚⇎行号往返" % (G['split_n'], G['tagcut_n']),
     u"两半由偏移经 `bisect_right` 映回原行再按逐字符对照表切; 编号切开那枚另走“保留字符下标表”把去编号面映回摘壳面",
     u"切开 %d 枚(针号 %s) ⇎ 首行 %s ⇎ 末行 %s ⇎ 两半字数 %s ⇎ %s ⇎ 合计 %d 字符 ⇎ 相邻 %d/%d" % (
         G['split_n'], J(G['split_k']), J(G['split_head']), J(G['split_tail']),
         J(G['split_head_chars']), J(G['split_tail_chars']), G['split_rows_tot'],
         G['split_adj_n'], G['split_n']),
     u"整串拿到首行读通 %d 枚(反向对照门) ⇎ 两半各回本行读通 %d/%d ⇎ 两行之间夹壳 %s(账 %d ⇎ 账平判定 %d) ⇎ 切开数减逐行漏读数 %d; 去编号档救回的 %d 枚不是换行切的: "
     u"针“%s”被 %s(%d 字符)断开 ⇎ 两半窗宽减针长 %d ⇎ 全篇被标注吃掉 %s 字符(账 %s) ⇎ 摘壳面读不通而该面读通判定 %d; 段窗首末行回原文件自验 %d/%d(整串在一行 %d 处 ⇎ "
     u"靠两半 %d 处 ⇎ 首侧 %d ⇎ 末侧 %d)。" % (
         G['split_full_on_head'], G['split_half_ok'], G['split_n'], J(G['split_gap_rows']),
         G['split_ledger'], G['split_ledger_close'], G['split_ledger'], G['tagcut_n'],
         G['tagcut_needle'][0], G['tagcut_mid'][0], G['tagcut_tag_chars'][0], G['tagcut_ledger'][0],
         J(G['tag_eaten']), J(G['tagcut_eaten_close']), G['tagcut_halves_are_face_pieces'],
         G['seg_rt_n'], G['seg_rt_ok'], G['seg_rt_whole'], G['seg_rt_cut'], G['seg_rt_head'], G['seg_rt_tail'])),
    (u"义务词四档⇎跨行 %d 对⇎剥编号跌幅" % G['tone_straddle_n'],
     u"大写族与小写族分家(照抄 `TONE` 五式), 整词尺三档并立; 跨行对由本遍在原面逐行现定位(上一行收前词 ⇎ 下一枚非空行起后词, 中间只许空行)",
     u"摘壳整词总量 %s ⇎ 裸 MUST %s ⇎ 原行 %s ⇎ 折平 %s ⇎ 去编号 %s ⇎ 跨行 %d 对(按份 %s) ⇎ 式样 %d 种(%s)" % (
         J(G['tone_tot']), J(G['must_bare']), J([sum(x) for x in G['tone_line']]),
         J([sum(x) for x in G['tone_fold']]), J([sum(x) for x in G['tone_tag']]),
         G['tone_straddle_n'], J(G['tone_straddle']), len(G['tone_straddle_nd']), J(G['tone_straddle_nd'])),
     u"MUST NOT 恒不大于 MUST(%d) ⇎ 两笔账 %s/%s 全平; 跨行 %d 对里相邻 %d ⇎ 中间夹空行 %d 枚 ⇎ 夹壳 %d ⇎ 与折平档 MUST NOT 增益逐份账平(%s, 账 %d) ⇎ "
     u"“全部是同一式”判定 %d; 剥编号后整词读数跌 %s 枚(MUST %d ⇎ MAY %d)——括号里的 MUST 本身也是整词, 不是义务词少了而是口径没了; 段内五轨与游程尺 ⇎ 正则尺的差 %d。" % (
         sum(G['mustnot_of_must']), J(G['tone_must_ledger']), J(G['tone_ledger']), G['tone_straddle_n'],
         G['tone_straddle_adj'], G['tone_straddle_blank'], G['tone_straddle_gap_shell'],
         J(G['tone_wrap_gain_mn']), G['tone_straddle_ledger'], G['straddle_is_mustnot_only'],
         J(G['tone_drop_tot']), G['tone_drop_tag'][1][0], G['tone_drop_tag'][1][4], G['blk_tone_ruler_close'])),
    (u"编号族: 9293 一家的 237 枚",
     u"四形各自一条正则现扫(括号式 ⇎ 方括号式 ⇎ 括号带说明式 ⇎ 裸式), 落点按后随字符现判; 词种与号数从同一张匹配表读",
     u"摘壳面 %s ⇎ 原行面 %s ⇎ 括号式 %s ⇎ 裸式 %s ⇎ 方括号 %s ⇎ 括号带说明 %s ⇎ 按词种 %s ⇎ 最大编号 %s" % (
         J(G['tag_sh']), J(G['tag_raw']), J(G['tag_paren']), J(G['tag_bare']), J(G['tag_paren_bracket']),
         J(G['tag_paren_prose']), J(G['tag_kind_sum']), J(G['tag_max_num'])),
     u"四形账 %s ⇎ 折行不吞编号(两面同值判定) ⇎ 词种与形状两本账各自闭合(%s ⇎ %s) ⇎ 括号式落点 句号前 %s ⇎ 逗号前 %s ⇎ 句中 %s ⇎ 非句末 %s(账 %s); "
     u"“individually labeled” 声明 %s 行——只有它一家把义务词逐条挂号; 例: %s ⇎ %s。" % (
         J(G['tag_form_ledger']), J(G['tag_kind_close']), J(G['tag_paren_kind_close']),
         J(G['tag_paren_period']), J(G['tag_paren_comma']), J(G['tag_paren_mid']), J(G['tag_paren_prose']),
         J(G['tag_paren_place_close']), J(G['tag_decl']),
         QT(u'9293', u'options, but the following options MUST be supported (MUST-4 --'),
         QT(u'9293', u'default to no less than two hours (MUST-28)'))),
    (u"说法换代⇎拼写对峙⇎引用语态",
     u"`SPELL`(15 式)定义照抄 ⇎ 整词尺换查表档 ⇎ 子串尺走 `str.count`, 两把尺的差单列; “谁引谁”由本表十号在面上紧接的位置现扫",
     u"keep-alive 连字式 %s ⇎ 拼法种数 %s ⇎ 合并写法全库 %d 枚 ⇎ “idle” 整词 %s ⇎ 复合术语 “idle timeout” %s ⇎ “persistent” %s ⇎ 拼写族总量 %s" % (
         J(G['ka_hyphen']), J(G['ka_form_n']), G['ka_merged'], J(G['idle_term']),
         J(G['idle_compound']), J(G['persist']), J(G['spell_tot'])),
     u"全库独有拼式 %d 条(%s) ⇎ 子串尺比整词尺多读合计 %d 枚 ⇎ 两把尺差 %s; acknowledgement/acknowledgment 两式并存 %s(偏斜 %s, -1 是那枚也没有); "
     u"implementors/implementers %s——换代时正是这一式翻面; 引用写法 “RFC nnnn” %s ⇎ 连字符式 %s ⇎ 方括号式 %s ⇎ 十号里引到别家 %s 家; 第一人称 “we+动词” %s ⇎ "
     u"非人称式 %s; 十六进制字面量 %s 枚——两份 TCP 文书一枚也没有。" % (
         G['spell_own_tot'], J(G['spell_own']), G['spell_ruler_gap_tot'], J(G['spell_ruler_gap']),
         J(G['ack']), J(G['ack_skew']), J(G['impl']), J(G['cit_rfc']), J(G['cit_rfc_hyphen']),
         J(G['cit_brk']), J(G['cite_own']), J(G['voice_weverb']), J(G['voice_impersonal']), J(G['hexes']))),
    (u"时长三种写法⇎带单位数值⇎参数名",
     u"数值抽取一条正则代建条侧手工扫, 严宽两把尺(邻接表只带复数单位 ⇎ 把单数 “s” 也算上)各对拍一次; 参数名按带下划线式现读",
     u"词写 “two hours” %s ⇎ 长写 %s ⇎ 数字写 %s ⇎ 带单位数值 %s 项 ⇎ 宽尺 %s 项 ⇎ 各家独有 %d 项 ⇎ 全冷式 %s ⇎ 下划线参数名 %s" % (
         J(G['num_word_two']), J(G['num_longform_two']), J(G['num_digit_two']), J(G['numval_n']),
         J(G['numval_wide_n']), G['num_own_tot'], J(G['num_cold']), J(G['par_under'])),
     u"数字写全库 0 枚(%s ⇎ 判定 %d: 两份 TCP 文书把唯一定值写成词) ⇎ 宽尺比严尺多读 %s 项(%s) ⇎ 严尺丢掉 %s 项 ⇎ 邻接尺与正则尺差 %s; 14 个候选数字式里热档 %d ⇎ "
     u"全冷 %d ⇎ 命名列相加=去重枚数(%s); 参数名五候选合计 %s 枚 ⇎ 只在本面出现的 %s ⇎ 时长族十式总量 %s——9112 的 0 项为全库最少。" % (
         J(G['num_digit_two']), G['num_digit_two_tot'] == sum(G['num_digit_two']),
         J([len(x) for x in G['numval_s_extra']]), J(G['numval_s_extra']),
         J([len(x) for x in G['numval_s_lost']]), J(G['num_ruler_gap']), G['num_hot_n'], G['num_cold_n'],
         J(G['num_lit_close']), J(G['par_n']), J(G['par_own']), J(G['dur_tot']))),
    (u"五句答话⇎两把行号尺⇎段窗",
     u"答句由逐字符句界导出(采集侧用前瞻正则), 再由段窗尺拿整句重导一遍对拍; 行号经 `bisect_right` 回映射, 建条侧另用累积长度表读过同一句",
     u"词数 %s(共 %d) ⇎ 字符 %s ⇎ 整句跨行 %s ⇎ 锚针跨行 %s ⇎ 自然段行数 %s ⇎ 首行 %s ⇎ 末行 %s" % (
         J(G['ans_words']), G['ans_words_tot'], J(G['ans_chars']), J(G['ans_sent_span']),
         J(G['ans_needle_span']), J(G['ans_block_lines']), J(G['ans_sent_line']), J(G['ans_sent_end'])),
     u"两把行号尺差合计 %d ⇎ 跨行差 %d ⇎ 采集对拍同值判定 %d; 句内页壳 %s 枚(真零, 非缺测: 行距减窗内实有行逐份 %s); 答句比锚针多占 %s 行 ⇎ 键名所指即此差; "
     u"句内编号标注 %s 枚 ⇎ 恰为 9293 那两句(%d 字符, 账 %d) ⇎ 两份 TCP 那两句是唯一逐字复述对(判定 %d); 五句全以句点收尾(%s) ⇎ 全为 ASCII(%s); "
     u"十五段行 %s ⇎ 词 %s ⇎ 字符 %s ⇎ 五段 %d 行 %d 词 %d 字符 ⇎ 单行成段 %d 段。" % (
         G['ans_line_close'], G['ans_span_close'], G['ans_ruler_rematch'], J(G['ans_shell_rows']),
         J(G['ans_row_ledger']), J(G['ans_needle_gap']), J(G['ans_tag_n_in_sent']), G['ans_tagdiff'],
         G['ans_tag_len_ledger'], G['ans_pair_same'], J(G['ans_punct']), J(G['ans_na']),
         J(G['blk_rows']), J(G['blk_words']), J(G['blk_chars']), G['blk_five_rows'], G['blk_five_words'],
         G['blk_five_chars'], G['blk_one_line_n'])),
    (u"节窗⇎标题重印",
     u"节号尺由“行首缩进+点段+空格”现取, 定界取不早于节头的下一个同级标题; 窗内页壳与子节按原行现数(建条侧在折平面上数)",
     u"节号 %s ⇎ 窗幅行 %s ⇎ 字符 %s ⇎ 占摘壳面 %s ⇎ 窗内页壳 %s ⇎ 子节 %s ⇎ 标题印出 %s 次 ⇎ 正文面命中 %s 次" % (
         J(G['sec_no']), J(G['sec_lines']), J(G['sec_chars']),
         u' ⇎ '.join(u'%s%%' % x for x in G['sec_span_pct']), J(G['sec_shell_rows']), J(G['sec_child']),
         J(G['sec_print_n']), J(G['sec_hit_n'])),
     u"目录行 %s ⇎ 正文行 %s ⇎ 缩进 %s/%s 列 ⇎ 答句距节首 %s 行 ⇎ 五句都在自己那节内(%s, 合计 %d); 节内义务词 %s(合计 %d) ⇎ 只剩义务词而无他量的节 %d 个 ⇎ "
     u"零枚的节 %d 个 ⇎ 节内参考文献行 %s 行; 9000 的 “Idle Timeout” 是通用词, 正文面命中 %d 次为别份的十倍量级(%s)。" % (
         J(G['sec_toc_line']), J(G['sec_body_line']), J(G['sec_toc_indent']), J(G['sec_body_indent']),
         J(G['sec_ans_gap']), J(G['sec_ans_inside']), sum(G['sec_ans_inside']), J(G['sec_tone_tot']),
         G['sec_tone_tot_all'], G['sec_tone_only_n'], G['sec_tone_zero_n'], J(G['sec_refs']),
         G['sec_hit_n'][4], QT(u'9000', u'10.1.  Idle Timeout'))),
    (u"9293 重写 1122 的保活节",
     u"段窗行号现取(壳行与非壳行分家), 句子由逐字符句界切; 同句三档(逐字 ⇎ 去编号 ⇎ 再归拼)在面上比, 逐词对照由匹配器现导且三条出口对拍",
     u"句数 %d⇎%d ⇎ 块行 %s ⇎ 正文段行 %s ⇎ 其中壳行 %d ⇎ 去壳后 %s ⇎ 逐字同 %d 句 ⇎ 去编号同 %d 句 ⇎ 归拼同 %d 句 ⇎ 新句 %d(讨论段升格 %d)" % (
         G['ovl_s1'], G['ovl_s2'], J(G['ovl_block_lines']), J(G['ovl_spec_lines']),
         G['ovl_shell_in_block'], J(G['ovl_spec_lines_content']), G['ovl_same_raw'], G['ovl_same_tag'],
         G['ovl_same_canon'], G['ovl_new'], G['ovl_disc_promoted']),
     u"三档单调判定 %d/2 ⇎ 相同句账 %d ⇎ 新句 %d 句 = 讨论段升格 %d + 全新生 %d(账 %d) ⇎ 逐字重印读不通(判定 %d); 新句位置由面导: 首行 %s ⇎ 各跨 %s 行 ⇎ "
     u"窗内被编号切开 %s 处 ⇎ 可定位判定 %d; 主答句段逐词对照: 动作序列 %s ⇎ 相同 %d 词分 %d 段(最长 %d) ⇎ 删 %d ⇎ 插 %d ⇎ 替换 %d 处; 三本词账 %s/%s/%s ⇎ "
     u"字符账 %d(删 %s ⇎ 插 %s ⇎ 去编号后 %s) ⇎ 段长差 %d 里 %d 字符是 %d 枚编号(每枚 %s)。" % (
         G['ovl_monotone'], G['ovl_same_ledger'], G['ovl_new'], G['ovl_disc_promoted'], G['ovl_new_n'],
         G['ovl_new_close'], G['tcp_block_rewritten_not_reprinted'],
         J(G['ovl_new_lines']), J(G['ovl_new_rows']), J(G['ovl_new_tagcut']), G['ovl_new_locatable'],
         G['blk_tcp_op_tags'], G['blk_tcp_equal'], G['blk_tcp_equal_runs'], G['blk_tcp_equal_max'],
         G['blk_tcp_drop'], G['blk_tcp_insert'], G['blk_tcp_replace'], G['blk_tcp_word_ledger'],
         G['blk_tcp_word_ledger2'], G['blk_tcp_word_gap_ledger'], G['blk_tcp_char_ledger'],
         G['blk_tcp_char_drop'], G['blk_tcp_char_insert'], G['blk_tcp_naked_chars'],
         G['blk_tcp_len_gap'], G['blk_tcp_tag_chars'], len(G['blk_tcp_tag_widths']),
         J(G['blk_tcp_tag_widths']))),
    (u"关键词模板段⇎套版长行池",
     u"池=剥壳后逐行折平(不拆字 ⇎ 不改大小写)长度 ≥40 的行去重; 归属向量走 `Counter` ⇎ 共用走文档下标组合逐枚数共现; 段窗首末行回原文件按逐行序列再比一次",
     u"各份 %s ⇎ 并集 %d ⇎ 原行 %s(重印 %d) ⇎ 分档(共用 1..5 份)%s ⇎ 两两 %d ⇎ 三三 %d ⇎ 四四 %d ⇎ ≥25 字符并集 %d(多 %d)" % (
         J(G['pool_n']), G['pool_union'], J(G['pool_raw_rows']), G['pool_dup'], J(G['pool_tier']),
         G['pool_pair_tot'], G['pool_trip_tot'], G['pool_quad_tot'], G['pool_union25'], G['pool_widen']),
     u"容斥账 %d ⇎ 分档账 %d ⇎ 加和账 %d ⇎ 五份共用 %d 枚 ⇎ 恰好新式四份共用 %d 枚; 牵进 1122 的四对里除 1122·9293 的 %d 枚外全冷(%d 对为 0) ⇎ 而共的是 TCP "
     u"正文行不是套版行(带义务词 %d ⇎ 提 RFC %d ⇎ 讲 status %d ⇎ 判定 %d) ⇎ 与它最热的一对 %d 枚; 新式共用 %d 枚里带义务词 %d ⇎ 提 RFC %d ⇎ 讲 status %d ⇎ "
     u"带 BOM %d(296/1151); 模板段 1122 首行 %s(该档口径不存在) ⇎ 四份有这段(判定 %d) ⇎ 六对整段逐字同 %d 对 ⇎ 回原文件按逐行序列比只剩 %d 对 ⇎ 差 %d 对(两把尺之和 %d); "
     u"共头 %s ⇎ 共尾 %s(零尾 %d 对 ⇎ 非零尾 %d 对 ⇎ 和 %d) ⇎ 四路齐头 %d 词 ⇎ 词汇最多一段 %d 个不同词。" % (
         G['pool_ie_close'], G['pool_tier_close'], G['pool_sum_close'], G['pool_all_five'],
         G['pool_new_four'], G['pool_old_shared'], G['pool_pair_old_n'], G['pool_old_shared_toned'],
         G['pool_old_shared_rfcline'], G['pool_old_shared_status'],
         G['pool_old_shares_only_tcp_body'], G['pool_max_pair'], G['pool_shared_new'],
         G['pool_shared_toned'], G['pool_shared_rfcline'], G['pool_shared_status'], G['pool_shared_bom'],
         G['kw_minus_row'][0], G['kw_docs'], G['kw_same_n'], G['kw_same_raw_n'], G['kw_wrap_diff'],
         G['kw_face_close'], J(G['kw_head_pre']), J(G['kw_head_suf']), G['kw_suf_zero_n'],
         G['kw_suf_nz_n'], G['kw_suf_tot'], G['kw_all_head'], G['kw_vocab_max'])),
    (u"反面针 %d 枚⇎%d 次探针⇎两把词尺差" % (G['neg_n'], G['neg_probes']),
     u"应冷处由本遍现算: 逐式在其登记的那张面(摘壳 ⇎ 全篇折平)上数, 子串轨走 `str.count` ⇎ 整词轨走查表档, 两轨差值单独落账而不混进门槛",
     u"反面针 %d 枚 ⇎ 探针 %d 次 ⇎ 应冷处读到 %d 枚 ⇎ 有主针 %d/%d 枚 ⇎ 走折平档 %d 式(余下 %d 式走摘壳面)" % (
         G['neg_n'], G['neg_probes'], G['neg_zero_hits'], G['neg_owner_present'], G['neg_n'],
         G['neg_fold_n'], G['neg_n'] - G['neg_fold_n']),
     u"两把词尺的差单列: 子串轨在 %d 个(份,式)格上多读 %d 枚(这些格子串轨共读 %d 枚) ⇎ 例: “quic” 在 1122 面子串 %d ⇎ 整词 %d 枚(quickly 的词头), "
     u"“keep-alive” 在 1122 子串 %d ⇎ 整词 %d 枚(复数形被吞进), 两式的整词读数在别份上 %s; 唯一换档的反向针 “[Page 1]” 走全篇折平面, 因为它的整行住处在壳尺之内"
     u"(折平面 %s 枚 ⇎ 摘壳面 %s 枚 ⇎ 所在原行 %s ⇎ 壳外行数 %d)——壳面的锚给不出, 只能以读数登记。" % (
         len(G['neg_sub_false_rows']), G['neg_sub_false'], G['neg_sub_ruler'],
         G['neg_sub'][0][NIDX[u'quic']], G['neg_word'][0][NIDX[u'quic']],
         G['neg_sub'][0][NIDX[u'keep-alive']], G['neg_word'][0][NIDX[u'keep-alive']],
         J([G['neg_word'][i][NIDX[u'quic']] for i in [1, 2, 3, 4]]),
         J(G['page_lit_fold']), J(G['page_lit_sh']), J(G['page_lit_rows']), G['page_lit_rows_shell'])),
    (u"闭合账⇎锚账⇎对账",
     u"门的右式 ⇎ 恒等式表达式从两遍源码 `ast` 摘出后在本遍读数上 eval; 锚由正文的手写配对扫描现推, 归属走双轨(整篇归一串 ⇎ 逐行归一串)同判才计数",
     u"布尔门 %d/%d ⇎ 恒等式 %d+%d=%d ⇎ V 形 %d 条 ⇎ DERIV %d 键/%d 处引用 ⇎ 采集对账 %d/%d ⇎ 锚 %d 处/去重 %d/单面 %d/跨面 %d/五面同 %d ⇎ 编码区 %d 字符 ⇎ 键 %d" % (
         G['bool_all_sum'], G['bool_all_n'], G['zid_scan_n'], G['zid_scan2_n'],
         G['zid_scan_n'] + G['zid_scan2_n'], len(CH['zid']), len(DER), DCITE,
         G['pick_agree'], G['pick_same_n'], G['anchor_total'], G['anchor_distinct'],
         G['anchor_single'], G['anchor_cross'], G['anchor_all5'], G['enc_chars'], G['contract_n']),
     u"锚误读 %d 枚 ⇎ 行号回读复现 %d/%d 档 ⇎ 未被本遍窗口认领 %d 枚 ⇎ 歧义档 %d 枚 ⇎ 不符键 %d ⇎ 未复算 %d ⇎ 独有 %d ⇎ 判词 %d 条 ⇎ 内容针 %d 枚 ⇎ "
     u"反向针 %d 枚 ⇎ 定位针复核 %d 枚(行号账差 %d); 谱系 %s 跨 %d 年。" % (
         G['anchor_err'], REPL, len(ALD), len(UNCLAIMED), CH[u'anchor_ambiguous'], len(BAD), len(UNCOVER),
         len(MISS), G['checks'], G['needle_n'], G['neg_n'], G['pin_checked'], G['pin_line_close'],
         J(G['years']), max(G['years']) - min(G['years'])))]
assert len(rows) == 15, len(rows)
for _r in rows:
    _c = [cell(x) for x in _r]
    A(u'| %s | %s | %s | %s |' % tuple(_c))
A(u"")

STRQ = [pair_pieces3(IDX[_t[0]], _t[2], _t[3], TONE[_t[1]]) for _t in TSP]
SPLQ = [split_pieces3(_r[1], ROLEN[_r[0]]) for _r in SPLITREC]

A(u"五份答话在本遍仍是五次不同的动作, 而答句不再抄建条侧的句子表: 句界由 `[.!?](?=[ \\n]|$)` 的 finditer 候选现取, 首末行再经 `bisect_right` 映回原行, "
  u"建条侧那把累积长度表读过同一句(两把尺差合计 %d ⇎ 跨行差 %d)。 %s ⇎ %s——词 %s(共 %d) ⇎ 整句跨 %s 行 ⇎ 各归各节 %s。 两份 TCP 文书把唯一定值写成词: "
  u"数字写 “2 hours” 全库 %d 枚(逐份 %s); 9293 比 1122 多 %d 字符, 恰是它给同一句缀的两枚编号的宽度(%d 字符, 账 %d), 而这一对在逐字档只算 %d 句相同, "
  u"去编号档才算 %d 句——“重印”必须先过编号档。 9112 一个值也不给: %s, 带单位数值 %d 项为全库最少; 9113 把刀交给服务器 %s, 同时 %s; "
  u"9000 不给定值给算法: %s ⇎ %s, 并第一次把这件事写成可协商的参数(下划线参数名 %d 枚)。 三条线同时翻页: keep-alive 连字式 %s ⇎ “idle” 整词 %s ⇎ 编号族 %s——"
  u"末族只落在 9293, 而它正是唯一重印并挂号的那一份。" % (
      G[u'ans_line_close'], G[u'ans_span_close'],
      QT(u'1122', G[u'ans'][0].strip()), QT(u'9293', G[u'ans'][1].strip()),
      J(G[u'ans_words']), G[u'ans_words_tot'], J(G[u'ans_sent_span']), J(G[u'sec_no']),
      G[u'num_digit_two_tot'], J(G[u'num_digit_two']), G[u'ans_tagdiff'], G[u'ans_tag_len'],
      G[u'ans_tag_len_ledger'], G[u'ovl_same_raw'], G[u'ovl_same_tag'],
      QT(u'9112', ROLEN[8]), G[u'numval_n'][2],
      QT(u'9113', ROLEN[17]), QT(u'9113', ROLEN[16]),
      QT(u'9000', ROLEN[24]), QT(u'9000', ROLEN[27]), G[u'par_under'][4],
      J(G[u'ka_hyphen']), J(G[u'idle_term']), J(G[u'tag_sh'])))
A(u"被硬换行切开的 %d 枚判词, 本遍不抄建条侧登记的字面, 而是从偏移经 `bisect` 映回原行再按逐字符对照表切两半: 两半逐枚回自己那一行都读得通(%d/%d), "
  u"而把整串拿到首行去读则 %d 枚也读不通——线切过之后没有一枚还完整留在自己那一行。 例: %s ⇎ %s ‖ %s ⇎ %s ‖ %s ⇎ %s。 幅度合计 %d 行 ⇎ 两半字符合计 %d ⇎ "
  u"相邻 %d/%d 对。 去编号档救回的那一枚不是换行切的: 针“%s”在摘壳面上被 “%s”(%d 字符)断开, 两半改由保留字符下标表映回去编号面再取(%s ⇎ %s), "
  u"两半之宽减针长 %d ⇎ 全篇被标注吃掉的字符 %s(账 %s ⇎ 判定 %d)。 义务词也被同一根线切开 %d 对, 式样只有 “%s” 一种, 全部由原面逐行现定位(上一行收前词 ⇎ "
  u"下一枚非空行起后词): %s ⇎ %s ‖ %s ⇎ %s ‖ %s ⇎ %s ‖ %s ⇎ %s。 段窗首末行回原文件自验 %d/%d(整串在一行的 %d 处 ⇎ 靠两半的 %d 处)——这一段是自验不是复述。" % (
      G[u'split_n'], G[u'split_half_ok'], G[u'split_n'], G[u'split_full_on_head'],
      QRAW(LBL[SPLITREC[0][1]], SPLQ[0][2]), QRAW(LBL[SPLITREC[0][1]], SPLQ[0][3]),
      QRAW(LBL[SPLITREC[6][1]], SPLQ[6][2]), QRAW(LBL[SPLITREC[6][1]], SPLQ[6][3]),
      QRAW(LBL[SPLITREC[13][1]], SPLQ[13][2]), QRAW(LBL[SPLITREC[13][1]], SPLQ[13][3]),
      G[u'split_span_tot'], G[u'split_rows_tot'], G[u'split_adj_n'], G[u'split_n'],
      G[u'tagcut_needle'][0], G[u'tagcut_mid'][0], G[u'tagcut_tag_chars'][0],
      QRAW(G[u'tagcut_lbl'][0], G[u'tagcut_head'][0]), QRAW(G[u'tagcut_lbl'][0], G[u'tagcut_tail'][0]),
      G[u'tagcut_ledger'][0], J(G[u'tag_eaten']), J(G[u'tagcut_eaten_close']), G[u'tagcut_halves_are_face_pieces'],
      G[u'tone_straddle_n'], J(G[u'tone_straddle_nd']),
      QRAW(TSP[0][0], STRQ[0][0]), QRAW(TSP[0][0], STRQ[0][1]),
      QRAW(TSP[1][0], STRQ[1][0]), QRAW(TSP[1][0], STRQ[1][1]),
      QRAW(TSP[2][0], STRQ[2][0]), QRAW(TSP[2][0], STRQ[2][1]),
      QRAW(TSP[6][0], STRQ[6][0]), QRAW(TSP[6][0], STRQ[6][1]),
      G[u'seg_rt_n'], G[u'seg_rt_ok'], G[u'seg_rt_whole'], G[u'seg_rt_cut']))
A(u"9293 把 1122 那一节重写了一遍, 而“重写”在这里是三档判出来的: 逐字同 %d 句 ⇎ 去编号同 %d 句 ⇎ 再把 implementers→implementors/acknowledgment→"
  u"acknowledgement 归拼后同 %d 句(三档单调判定 %d/2)。 新句 %d 句 = 讨论段升格 %d + 全新生 %d(账 %d), 全新生那几句的位置也由面导: 首行 %s 各跨 %s 行 ⇎ "
  u"窗内被编号切开 %s 处 ⇎ 可定位判定 %d。 逐词对照在本遍走三条通道: 建条侧直接取 `get_opcodes()` 默认档, 本遍由 `get_matching_blocks()` 自己重造动作序列"
  u"(序列 %s), 再跑一遍 `autojunk=False` 档比标签序列——三条给同一组数: 相同 %d 词分 %d 段(最长 %d 词) ⇎ 删 %d ⇎ 插 %d ⇎ 替换 %d 处; 三本词账 %d/%d/%d ⇎ "
  u"字符账 %d(删 %d ⇎ 插 %d ⇎ 去编号后整段 %d 字符)。 删掉的是 1122 的开场句 %s, 添进来的是 %s; 9293 那一段不是 1122 面的子串(%d), "
  u"“重写而不是重印”的判定 %d。 段长差 %d 字符里 %d 字符是 %d 枚编号(每枚 %s 字符)。" % (
      G[u'ovl_same_raw'], G[u'ovl_same_tag'], G[u'ovl_same_canon'], G[u'ovl_monotone'],
      G[u'ovl_new'], G[u'ovl_disc_promoted'], G[u'ovl_new_n'], G[u'ovl_new_close'],
      J(G[u'ovl_new_lines']), J(G[u'ovl_new_rows']), J(G[u'ovl_new_tagcut']), G[u'ovl_new_locatable'],
      u' '.join(G[u'blk_tcp_op_tags']), G[u'blk_tcp_equal'], G[u'blk_tcp_equal_runs'], G[u'blk_tcp_equal_max'],
      G[u'blk_tcp_drop'], G[u'blk_tcp_insert'], G[u'blk_tcp_replace'], G[u'blk_tcp_word_ledger'],
      G[u'blk_tcp_word_ledger2'], G[u'blk_tcp_word_gap_ledger'], G[u'blk_tcp_char_ledger'],
      G[u'blk_tcp_char_drop'], G[u'blk_tcp_char_insert'], G[u'blk_tcp_naked_chars'],
      QT(u'1122', u'Implementors MAY include "keep-alives" in their TCP'),
      QT(u'9293', u'keep-alives are included, the application MUST be able to turn them'),
      G[u'blk_tcp_verbatim_sub'], G[u'tcp_block_rewritten_not_reprinted'],
      G[u'blk_tcp_len_gap'], G[u'blk_tcp_tag_chars'], len(G[u'blk_tcp_tag_widths']),
      J(G[u'blk_tcp_tag_widths'])))
A(u"三处口径要在这里挑明, 因为它们是本遍与前三遍唯一可能读出差的地方, 而差别来自实现不是来自数据。 其一: 建条遍把 `pick_needle_gap` 那一格直接写成字面量 0"
  u"(源码里就是 `F['pick_needle_gap'] = 0`), 本遍现读 %d 枚——采集遍登记的 %d 枚针里有 %d 枚不在本遍的 %d 枚判词针之内, 反向 %d 枚, 交集 %d 枚。 这一格不静默改: "
  u"它进申报清单 `OVR`, 而 DERIV 的 “0” 键(全库零项之和)在本遍读数上正好 eval 出 %d, 与申报差额 %d 相抵; 余下 %d 键逐值对账为空 ⇒ 这笔差额无人可推给别的键。 "
  u"其二: 锚是四个口径而不是同一个数——发射遍日志 %d 行 ⇎ 本遍按(份, 键, 行, 命中数)归并 %d 档 ⇎ 独立串 %d 条 ⇎ 编码区正文引用 %d 处。 日志比档多, 因为跨行的两半"
  u"各按自己那一侧记两遍: 单行 %d ⇎ 首 %d ⇎ 末 %d ⇎ 上 %d ⇎ 下 %d ⇎ 编号前 %d ⇎ 编号后 %d(去重后 %d ⇎ %d ⇎ %d ⇎ %d ⇎ %d ⇎ %d ⇎ %d)。 本遍的行号尺复现 %d/%d 档 ⇎ "
  u"正文引用未被本遍窗口认领 %d 枚 ⇎ 命中数大于一的歧义档 %d 条, 归属一律走双轨(整篇归一串 ⇎ 逐行归一串)同判才计数。 其三: 读到 0 与“口径不存在”是两件事——"
  u"答句所在那几行的页壳行数 %s 是真量(行距减窗内实有行逐份 %s ⇎ 判定 %d), 而 1122 面上根本没有关键词模板段, 段首偏移因此记 %s 而不是 0; 数字写 “2 hours” 的 0 枚"
  u"是数出来的五份读数 %s。 键名等于所量之物: `ans_needle_gap` 是句行数减锚针行数, `tagcut_ledger` 是两半之宽减针长, `split_ledger` 是切开数减逐行漏读数, 都不是同名族里的比例。" % (
      G[u'pick_needle_gap'], len(PKND), G[u'pick_needle_gap'], len(ROLEN), GAPBAK, INTER,
      ZSUM, OVDELTA, G[u'contract_n'] - 1,
      len(AL), len(ALD), DIST, G[u'anchor_total'],
      LOGN[u'plain'], LOGN[u'[首]'], LOGN[u'[末]'], LOGN[u'[上]'], LOGN[u'[下]'],
      LOGN[u'[编号前]'], LOGN[u'[编号后]'],
      LOGD[u'plain'], LOGD[u'[首]'], LOGD[u'[末]'], LOGD[u'[上]'], LOGD[u'[下]'],
      LOGD[u'[编号前]'], LOGD[u'[编号后]'],
      REPL, len(ALD), len(UNCLAIMED), CH[u'anchor_ambiguous'],
      J(G[u'ans_shell_rows']), J(G[u'ans_row_ledger']), G[u'ans_ruler_rematch'],
      G[u'kw_minus_row'][0], J(G[u'num_digit_two'])))
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"五份文件在 RFC Editor 此刻的现行状态页与勘误页(9293 的 MUST-27/MUST-28 有没有被 errata 改过措辞 ⇎ 9112 那句“不提任何要求”与 9113 那句“可以关掉空闲连接”"
  u"是否又被后继文档替换) ⇎ 现网服务器与内核实际取的空闲超时(1122 的两小时 ⇎ 9000 的最小值算法都只是面上的规定, 不等于装机行为) ⇎ PTO 的定义住在另一份规范里, "
  u"所以“三倍 PTO”到底乘的是谁的 PTO 不可由本库判定 ⇎ 9293 把 1122 那节重写的编辑意图(文档里没有 changelog 判定) ⇎ PDF 原版式与此纯文本面的排版差异(非 ASCII "
  u"%d 枚 ⇎ BOM %d 枚 ⇎ 换页 %d 枚在 PDF 里落成什么) ⇎ 抓取时刻与磁盘 mtime 谁新谁旧 ⇎ 被关键词模板段指向却不在本库的 2119/8174 正文——这些都要在库外字节或实时状态, "
  u"本库 %d 份文件给不出判据; 在库只给得出面上字节的四档读数 ⇎ %d 枚判词针的位置账 ⇎ %d 枚反面针的冷账 ⇎ %d 处锚的归属账。" % (
      sum(G[u'na_total']), sum(G[u'bom']), sum(G[u'ff']), G[u'nsrc'], G[u'needle_n'], G[u'neg_n'],
      G[u'anchor_total']))

NEW = u"## ⛓解读注" + NL + NL + NL.join(L2) + NL
_i2 = MD.index(u"## ⛓解读注")
out = MD[:_i2] + NEW
assert out.count(u"## ⛓解读注") == 1
T2 = ENTRY + u'.tmp'
io.open(T2, 'w', encoding='utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"⛓解读注 已写入 %s ｜ 表 %d 行 ⇎ 注区 %d 字符 ⇎ 复算 %d 键 ⇎ 不符 %d ⇎ 独有 %d ⇎ 未复算 %d ⇎ "
      u"恒等式 %d+%d ⇎ V 形 %d 条 ⇎ DERIV %d 键 ⇎ 门 %d/%d ⇎ 锚 日志%d⇎档%d⇎串%d⇎引%d ⇎ 编码区 %d 字符未动"
      % (ENTRY, len(rows), len(NEW), len(G) - 1, len(BAD), len(MISS), len(UNCOVER),
         G[u'zid_scan_n'], G[u'zid_scan2_n'], len(CH[u'zid']), len(DER),
         G[u'bool_all_sum'], G[u'bool_all_n'], len(AL), len(ALD), DIST, G[u'anchor_total'],
         G[u'enc_chars']))



