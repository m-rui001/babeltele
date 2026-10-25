# -*- coding: utf-8 -*-
"""B81 的第五遍复测: 采集侧(_pick81.py)⇎ 建条目侧(_mkB81.py + _mk81emit.py)⇎ 门槛侧(audit.py::_b81_scan)
换算法不换定义, 现算后把 ⛓解读注 写进条目。本遍的独立处:
①行界: 手写索引循环按 `\\n` 切(第二遍是 `str.split`), 换行枚数走 `str.count`, 码位数走逐字符累加(第二遍是 `len`);
  字节数走 `os.stat` 的文件系统元数据(第二遍是读进来的缓冲区长度)——两条通道同一数才算复核;
②折平/拆字: `re.sub('\\s+',' ')` 加 `str.translate(拆字表)` 两档(第二遍是 `re.split('\\s')` 过滤空段 ⇎ 逐字符查表重建),
  与第二遍的 `fold` ⇎ `delig` 在整份面与逐行面上双重对拍; 归一尺 `p5` 与 `pnorm` 逐份对拍;
③针计数三档: `str.count`(非重叠) ⇎ `finditer('(?=针)')`(重叠) ⇎ 第二遍的 `findall(re.escape)`; 逐行档把行循环
  换成累加器(第二遍是 `sum(cnt_re(...) for y in L[i])`);
④整词尺: `finditer` 前瞻定位后取左右邻字符判 alpha/digit/alnum(第二遍是游标 find 加 `_nb` 手扫, 采集侧是断言正则),
  另起一条断言正则档与它逐枚对拍, 两轨之差就是本遍的语气尺闭合;
⑤壳谓词第三档: `strip()` 后按空白切 token(无参 `split()`, 第二遍是 `fold` 再按一枚空格切), 逐段比首尾;
  页码尺换成 `re.fullmatch` 加 `len(re.findall('\\d+',x))` 的段数档(第二遍是逐字符判形状);
⑥数值抽取: 一条“负向后视断言 ⇎ 数字段 ⇎ 至多一枚空格 ⇎ 单位选支(按长度降序) ⇎ 负向前瞻字母”的正则,
  与第二遍的手工扫数字串两轨逐份对拍(严单位 ⇎ 宽到裸 s 两把尺各比一次);
⑦标题分档: 一条 `^( *)([0-9.]+)( )` 正则取缩进与点段再数段数(第二遍是逐字符吃档), 论文面节题用采集侧那条
  `^\\s*([IVX]+)\\.\\s+[A-Z]` 正则——本遍既不抄第二遍的字符扫, 也不抄采集侧的三条整序正则, 而是两把都跑再对拍;
⑧句界: `\\.(?=[ \\t\\n]+[A-Z(“"])` 一条 finditer 代第二遍的逐字符扫(尾退档同一: 最后一枚句点, 再退到串尾);
⑨行号尺: 偏移→行号走 `bisect_right`(第二遍是线性扫到尾), 逐字符对照表由 `re.finditer('\\S+')` 加
  `str.translate` 的展开长度同时构造(第二遍是手工跳空白);
⑩段池代数: 归属向量走 `Counter` 直方图 ⇎ 容斥与两两/三三/四四共用走“对文档下标的组合逐枚数共现”(第二遍是集合 `&`);
⑪词窗尺: `zip(*[tokens[i:] for i in range(n)])` 的转置档代第二遍的 `tokens[k:k+n]==p` 切片逐枚全等;
⑫定义复用而量不复用: `SPELL ⇎ TERM ⇎ UNIT ⇎ NUM ⇎ ROLE(27) ⇎ NEG(19) ⇎ PAR ⇎ CFG ⇎ TONE ⇎ VOICE ⇎ CIT ⇎ WIN ⇎
PINS(14) ⇎ SAMEK(115) ⇎ LIGMAP` 从两遍源码 `ast` 摘, 谓词函数 `exec` 进来只用于对拍; 28+16 道布尔门的右式 ⇎
34+30 条恒等式的表达式也从源码 `ast` 摘, 64 条 V 形 ⇎ 215 键 DERIV 从 `_b81checks.json` ⇎ `_deriv81.json` 回读
eval——一条都不抄第二遍的结论; 锚的归属由条目正文的“源标签紧接原子引文”手写配对扫描现推, 双轨(整篇归一串 ⇎
逐行归一串)同判才计数。
每个键与 corpus/_b81flat.json 逐值对拍, 值不符或键缺失一律先收集后汇总; 覆盖不足也要如实报数。"""
import io, os, re, sys, json, ast, bisect, itertools as IT
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
ENTRY = u'%s/babeltele/B81_aqm_queuing_delay_target_five_answers.md' % C
PATH = [u'%s/raw/qdelay/rfc7567.txt' % C, u'%s/raw/qdelay/piehdp.txt' % C,
        u'%s/raw/qdelay/rfc8033.txt' % C, u'%s/raw/qdelay/cake.txt' % C,
        u'%s/raw/qdelay/rfc8289.txt' % C]
LBL = [u'7567', u'madp', u'8033', u'cake', u'8289']
NSRC = 5
NL = u'\n'
TAGS = LBL
FAM = [u'rfc', u'paper', u'rfc', u'paper', u'rfc']
IDS = [u'7567', u'', u'8033', u'', u'8289']
YR = [2015, 2016, 2017, 2018, 2018]
RFCI = [0, 2, 4]
PAPI = [1, 3]
IDX = dict((t, n) for n, t in enumerate(LBL))

FLAT = json.load(io.open(u'%s/_b81flat.json' % C, encoding='utf-8'))
CH = json.load(io.open(u'%s/_b81checks.json' % C, encoding='utf-8'))
DER = json.load(io.open(u'%s/_deriv81.json' % C, encoding='utf-8'))
MEA = json.load(io.open(u'%s/_b81meas.json' % C, encoding='utf-8'))

MS = io.open(u'%s/_mkB81.py' % C, encoding='utf-8').read()
EM = io.open(u'%s/_mk81emit.py' % C, encoding='utf-8').read()

# ---------- 定义(不是本遍要换的量): 字面表用 ast 摘, 谓词函数用 exec 取来对拍 ----------
TABS = (u'SPELL', u'TERM', u'UNIT', u'UNITW', u'UNITW_S', u'NUM', u'ROLE', u'NEG', u'PAR', u'CFG',
        u'TONE', u'VOICE', u'CIT', u'WIN', u'PINS', u'LIGMAP', u'PAIRO', u'GREEKO', u'DASHQO',
        u'SAMEK', u'HEADRX', u'SUB43')
TAB = {}
for src in (MS, EM):
    for st in ast.parse(src).body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
            nm = st.targets[0].id
            if nm in TABS and nm not in TAB:
                try:
                    TAB[nm] = ast.literal_eval(st.value)
                except Exception:
                    pass
for nm in [x for x in TABS if x != u'SUB43']:
    assert TAB.get(nm) is not None, nm
SPELL, TERM, UNIT, UNITW, UNITW_S = TAB[u'SPELL'], TAB[u'TERM'], TAB[u'UNIT'], TAB[u'UNITW'], TAB[u'UNITW_S']
NUM, ROLE, NEG, PAR, CFG = TAB[u'NUM'], TAB[u'ROLE'], TAB[u'NEG'], TAB[u'PAR'], TAB[u'CFG']
TONE, VOICE, CIT, WIN = TAB[u'TONE'], TAB[u'VOICE'], TAB[u'CIT'], TAB[u'WIN']
PINS, LIGMAP, PAIRO = TAB[u'PINS'], TAB[u'LIGMAP'], TAB[u'PAIRO']
GREEKO, DASHQO, SAMEK, HEADRX = TAB[u'GREEKO'], TAB[u'DASHQO'], TAB[u'SAMEK'], TAB[u'HEADRX']
ROLEN = [x[2] for x in ROLE]

# ---------- 第二遍的谓词: 只用来对拍, 本遍的读数一律走自己的尺 ----------
PKF = [u'pnorm', u'fold', u'cnt_cur', u'cnt_re', u'cnt_ovl', u'_nb', u'ub', u'shell_by_shape',
       u'is_shell_pick', u'digit_runs', u'digit_line', u'delig', u'win_cnt', u'num_pairs',
       u'head_shape', u'dotrun', u'roman_shape', u'sent_end', u'pool_of']
_ns = {u're': re, u'NL': NL, u'LIGMAP': LIGMAP, u'LMAPC': LIGMAP, u'u': u'', u'ord': ord}
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
mk_cnt_re, mk_cnt_ovl, mk_cnt_cur = _ns[u'cnt_re'], _ns[u'cnt_ovl'], _ns[u'cnt_cur']
mk_ub, mk_shell, mk_is_pick = _ns[u'ub'], _ns[u'shell_by_shape'], _ns[u'is_shell_pick']
mk_druns, mk_dline, mk_delig = _ns[u'digit_runs'], _ns[u'digit_line'], _ns[u'delig']
mk_win, mk_pairs = _ns[u'win_cnt'], _ns[u'num_pairs']
mk_hshape, mk_dotrun, mk_roman = _ns[u'head_shape'], _ns[u'dotrun'], _ns[u'roman_shape']
mk_sent_end, mk_pool = _ns[u'sent_end'], _ns[u'pool_of']


# ---------- 本遍自己的尺 ----------
def ln5(t):
    """行界: 手写索引循环(第二遍是 str.split)"""
    out, i = [], 0
    while True:
        j = t.find(NL, i)
        if j < 0:
            out.append(t[i:])
            return out
        out.append(t[i:j])
        i = j + 1


def f5(s):
    """折平: re.sub 档(第二遍是 re.split('\\s') 过滤空段)"""
    return re.sub(u'\\s+', u' ', s).strip()


def p5(s):
    return re.sub(u'\\s+', u' ', s.lower()).strip()


TR5 = str.maketrans(LIGMAP)


def dg5(s):
    """拆字: str.translate 档(第二遍是逐字符查表重建)"""
    return s.translate(TR5)


def c5(s, nd):
    """非重叠计数: str.count(第二遍是 findall(re.escape), 采集侧是游标 find)"""
    return s.count(nd)


def o5(s, nd):
    """重叠计数: finditer 前瞻(第二遍是 j+1 游标环)"""
    return len([1 for m in re.finditer(u'(?=' + re.escape(nd) + u')', s)])


def ub5(s, w, kind=u'alpha'):
    """整词尺: 前瞻定位后看左右邻(第二遍是游标 find 加 _nb 手扫)"""
    n = len(w)
    c = 0
    for m in re.finditer(u'(?=' + re.escape(w) + u')', s):
        i, a, b = m.start(), m.start() - 1, m.start() + n
        if kind == u'alpha':
            ok = not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha())
        elif kind == u'digit':
            ok = not (a >= 0 and s[a].isdigit()) and not (b < len(s) and s[b].isdigit())
        else:
            ok = not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())
        if ok:
            c += 1
    return c


def sh5(x, fam):
    """壳谓词第三档: 无参 split() 后比首尾 token(第二遍是 fold 再按一枚空格切)"""
    tk = x.split()
    if not tk:
        return True
    if fam == u'rfc':
        if len(tk) >= 2 and tk[-2] == u'[Page' and len(tk[-1]) >= 2 and tk[-1][-1] == u']' \
                and tk[-1][:-1].isdigit():
            return True
        if len(tk) >= 4 and tk[0] == u'RFC' and len(tk[1]) == 4 and tk[1].isdigit() \
                and len(tk[-1]) == 4 and tk[-1][:2] in (u'19', u'20') and tk[-1][2:].isdigit():
            return True
        return False
    if ord(x[0]) == 12:
        rest = x[1:]
        return bool(re.fullmatch(u'[\\s\\d]+', rest)) and bool(re.search(u'\\d', rest))
    return False


def druns5(x):
    """数字段数: findall 档(第二遍是逐字符翻转 prev 计数)"""
    return len(re.findall(u'\\d+', x))


def dline5(x):
    return 1 if (re.fullmatch(u'[\\s\\d]*', x) and druns5(x) == 1) else 0


def win5(tokens, nd):
    """词窗尺: 转置滑窗(第二遍是 tokens[k:k+n]==p 切片逐枚比)"""
    p = tuple(nd.split(u' '))
    n = len(p)
    if n > len(tokens):
        return 0
    return sum(1 for row in zip(*[tokens[i:] for i in range(n)]) if row == p)


UNITS_SORT = {u'a': sorted(UNITW, key=len, reverse=True), u'b': sorted(UNITW_S, key=len, reverse=True)}
NPRE = {}
for _t, us in UNITS_SORT.items():
    NPRE[_t] = re.compile(u'(?<![A-Za-z0-9.])(\\d+(?:[.,]\\d+)?)(?: )?(' +
                          u'|'.join(re.escape(u) for u in us) + u')(?![A-Za-z])')


def pairs5(face, tag):
    """数值抽取: 一条正则的选择支档(第二遍是手工扫数字串再就地读最长单位)"""
    return [(m.group(1), m.group(2)) for m in NPRE[tag].finditer(face)]


def dotrun5(x):
    """最长连续点串: 切分档(第二遍是逐字符比较计数)"""
    runs = [len(y) for y in re.split(u'[^.]+', x) if y.strip(u'.') == u'']
    return max(runs) if runs else 0


def has_leader5(x):
    """目录引道符: “三枚连点”直接成员判定(第二遍是 dotrun 与 3 比大小)"""
    return 1 if u'...' in x else 0


def leader_sp5(x):
    """空格点尺: 点 ⇎ 空白交替段的段数(第二遍是 (?:\\.\\s*){3,} 一条正则)"""
    cnt = 0
    for ch in x:
        if ch == u'.':
            cnt += 1
        elif not ch.isspace():
            if cnt >= 3:
                return 1
            cnt = 0
    return 1 if cnt >= 3 else 0


def hshape5(x):
    """标题形状: 缩进由 lstrip(' ') 的字数导出, 点串由一条正则取, 段数由 split 后过滤空段
    (第二遍是逐字符吃档)"""
    rest = x.lstrip(u' ')
    ind = 1 if len(rest) != len(x) else 0
    m = re.match(u'[0-9.]+', rest)
    if not m:
        return ind, 0, u'', 0, 0
    d = m.group(0)
    e = m.end()
    if e >= len(rest) or rest[e] != u' ':
        return ind, 0, u'', 0, 0
    segs = [s for s in d.split(u'.') if s != u'']
    if not all(s.isdigit() for s in segs):
        return ind, 0, u'', 0, 0
    return ind, len(segs), u'.'.join(segs), 1, (1 if d.endswith(u'.') else 0)


def rom5(x):
    """论文面节题: 采集侧那条整序正则(第二遍是逐字符扫 I/V/X)"""
    m = re.match(u'\\s*([IVX]+)\\.\\s+[A-Z]', x)
    if not m:
        return u'', 0
    return m.group(1), len(m.group(1))


RXR = re.compile(u'\\.\\s*\\.\\s*\\.')
G2RX = {}

BRK5 = re.compile(u'\\[\\d+\\]')


def brk5(s):
    """方括号编号引用: 逐字符扫“[ + 一串数字 + ]”(采集侧与本遍均另有正则档, 这里用它代第二遍的 findall)"""
    n, i, m = 0, 0, len(s)
    while i < m:
        if s[i] != u'[':
            i += 1
            continue
        j = i + 1
        while j < m and s[j].isdigit():
            j += 1
        if j > i + 1 and j < m and s[j] == u']':
            n += 1
            i = j + 1
        else:
            i += 1
    return n


def rfcline5(s, num):
    """引用尺: 找编号串的每枚出现, 再看它前四字符是不是“RFC ”(代第二遍的 split('RFC ') 后逐段 startswith)"""
    n, i = 0, 0
    while True:
        j = s.find(num, i)
        if j < 0:
            return n
        k = j + len(num)
        if j >= 4 and s[j - 4:j] == u'RFC ' and (k >= len(s) or s[k] in (u' ', u',')):
            n += 1
        i = j + 1


SE5 = re.compile(u'\\.(?=\\s+[A-Z(“"])')


def wc5(s):
    """词数: 手写吃档数非空白连续段(第二遍是 len(s.split()))"""
    n, i, m = 0, 0, len(s)
    while i < m:
        while i < m and s[i].isspace():
            i += 1
        if i < m:
            n += 1
            while i < m and not s[i].isspace():
                i += 1
    return n


def sent_end5(s, frm):
    """句界: 一条 finditer 前瞻正则(第二遍是逐字符扫“点+空白+大写或左括号/左引号”)"""
    m = SE5.search(s, frm)
    if m:
        return m.start()
    d = s.rfind(u'.', frm)
    return d if d >= frm else len(s) - 1


def row_fd5(raw):
    """折平加拆字, 同时给每个结果字符记下它来自原行的下标: finditer 词档加 translate 展开长度"""
    s, idx = [], []
    for m in re.finditer(u'\\S+', raw):
        if s:
            s.append(u' ')
            idx.append(m.start())
        w = raw[m.start():m.end()]
        e = w.translate(TR5)
        s.append(e)
        for j, ch in enumerate(w):
            idx.extend([m.start() + j] * len(ch.translate(TR5)))
    return u''.join(s), idx


def tone_re5(s, nd):
    return len(re.findall(u'(?<![A-Za-z])' + re.escape(nd) + u'(?![A-Za-z])', s))


G = {}
_xc = []


def put(k, v):
    G[k] = v


# ---------- 文件字节 ⇎ 码位 ⇎ 行界 ----------
B5 = [io.open(p, 'rb').read() for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B5]
RAWL = [ln5(t) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]
for i in range(NSRC):
    assert ln5(T[i]) == RAWL[i] and mk_fold(NL) == u''

G[u'label'] = LBL
G[u'src'] = PATH
G[u'fam'] = FAM
G[u'ids'] = IDS
G[u'years'] = YR
G[u'bytes'] = [os.stat(p).st_size for p in PATH]
G[u'chars'] = [sum(1 for _c in T[i]) for i in range(NSRC)]
G[u'lines'] = [len(RAWL[i]) for i in range(NSRC)]
G[u'newlines'] = [T[i].count(NL) for i in range(NSRC)]
_nb5 = lambda x: any(not ch.isspace() for ch in x)
G[u'nonblank'] = [len([x for x in L[i] if _nb5(x)]) for i in range(NSRC)]
G[u'blank'] = [G[u'lines'][i] - G[u'nonblank'][i] for i in range(NSRC)]


def maxlen5(rows):
    m = 0
    for x in rows:
        if len(x) > m:
            m = len(x)
    return m


G[u'maxlen'] = [maxlen5(L[i]) for i in range(NSRC)]
G[u'over72'] = [len([x for x in L[i] if len(x) > 72]) for i in range(NSRC)]
G[u'ff'] = [T[i].count(u'\x0c') for i in range(NSRC)]
G[u'ff_exact'] = [len([x for x in L[i] if len(x) == 1 and ord(x) == 12]) for i in range(NSRC)]
G[u'ff_inline'] = [G[u'ff'][i] - G[u'ff_exact'][i] for i in range(NSRC)]
G[u'ff_lead'] = [len([x for x in L[i] if len(x) and ord(x[0]) == 12]) for i in range(NSRC)]
G[u'cr'] = [sum(1 for ch in T[i] if ord(ch) == 13) for i in range(NSRC)]
G[u'cr_rows'] = [len([x for x in RAWL[i] if len(x) and ord(x[-1]) == 13]) for i in range(NSRC)]
G[u'nul'] = [sum(1 for ch in T[i] if ord(ch) == 0) for i in range(NSRC)]
G[u'nonascii'] = [sum(1 for ch in T[i] if ord(ch) > 127) for i in range(NSRC)]
G[u'bom'] = [1 if B5[i][0:3] == b'\xef\xbb\xbf' else 0 for i in range(NSRC)]
G[u'tail_nl'] = [1 if T[i] and T[i][-1] == NL else 0 for i in range(NSRC)]
G[u'byte_cp_delta'] = [G[u'bytes'][i] - G[u'chars'][i] for i in range(NSRC)]
# UTF-8 加长量按码位区间算(第二遍是逐字符 len(c.encode('utf-8'))−1)
UTF8 = [(0x80, 0x800, 1), (0x800, 0x10000, 2), (0x10000, 0x110000, 3)]


def extra5(o):
    for lo, hi, n in UTF8:
        if lo <= o < hi:
            return n
    return 0


G[u'utf8_extra'] = [sum(extra5(ord(ch)) for ch in T[i] if ord(ch) > 127) for i in range(NSRC)]
G[u'byte_cp_ledger'] = [G[u'byte_cp_delta'][i] - G[u'utf8_extra'][i] for i in range(NSRC)]
G[u'crlf_rows'] = [1 if G[u'cr'][i] == G[u'newlines'][i] else 0 for i in range(NSRC)]
G[u'wrap_rows'] = G[u'over72']
G[u'wrap_family'] = [0 if FAM[i] == u'rfc' else 1 for i in range(NSRC)]
for i in range(NSRC):
    assert G[u'bytes'][i] == len(B5[i]), i
    assert G[u'lines'][i] == G[u'newlines'][i] + 1, i
    assert G[u'cr'][i] == G[u'cr_rows'][i], i
    assert [y[:-1] if (y and ord(y[-1]) == 13) else y for y in RAWL[i]] == L[i], i
    assert [y.rstrip(u'\r') if y.endswith(u'\r') else y for y in RAWL[i]] == L[i], i

# ---------- 非 ASCII 四成分: Counter 直方图代逐字符过滤 ----------
NA5 = [[ord(ch) for ch in T[i] if ord(ch) > 127] for i in range(NSRC)]
NAC = [Counter(x) for x in NA5]
G[u'lig_pair'] = [[NAC[i].get(o, 0) for o in PAIRO] for i in range(NSRC)]
G[u'lig_total'] = [sum(x) for x in G[u'lig_pair']]
G[u'na_greek'] = [sum(NAC[i].get(o, 0) for o in GREEKO) for i in range(NSRC)]
G[u'na_dashq'] = [sum(NAC[i].get(o, 0) for o in DASHQO) for i in range(NSRC)]
G[u'na_total'] = [len(x) for x in NA5]
G[u'na_other'] = [sum(v for o, v in NAC[i].items() if o not in PAIRO + GREEKO + DASHQO)
                  for i in range(NSRC)]
G[u'na_ledger'] = [G[u'lig_total'][i] + G[u'na_greek'][i] + G[u'na_dashq'][i] + G[u'na_other'][i]
                   - G[u'na_total'][i] for i in range(NSRC)]

# ---------- 七张面 ⇎ 与第二遍逐份对拍 ----------
FOLD5 = [f5(T[i]) for i in range(NSRC)]
LOWFOLD5 = [x.lower() for x in FOLD5]
SHP5 = [[x for x in L[i] if not sh5(x, FAM[i])] for i in range(NSRC)]
for i in range(NSRC):
    assert FOLD5[i] == mk_fold(T[i]) and p5(T[i]) == mk_pnorm(T[i]), i
    assert dg5(FOLD5[i]) == mk_delig(FOLD5[i]), i
    assert [f5(x) for x in L[i]] == [mk_fold(x) for x in L[i]], i
    assert [dg5(f5(x)) for x in L[i]] == [mk_delig(mk_fold(x)) for x in L[i]], i
    assert [dg5(f5(x)) for x in L[i] if not sh5(x, FAM[i])] == [mk_delig(mk_fold(x)) for x in L[i]
                                                                if not mk_is_pick(x, FAM[i])], i
SH5 = [f5(NL.join(SHP5[i])) for i in range(NSRC)]
LOW_SH5 = [x.lower() for x in SH5]
SHLIG5 = [dg5(x) for x in SH5]
LOW_SHLIG5 = [x.lower() for x in SHLIG5]
LIG5 = [dg5(x) for x in FOLD5]
LOWLIG5 = [x.lower() for x in LIG5]
TOK5 = [x.split(u' ') for x in LOW_SHLIG5]
for i in range(NSRC):
    assert len(TOK5[i]) == len(LOW_SHLIG5[i].split(u' '))
G[u'shell_pred_diff'] = sum([len([k for k in range(len(L[i]))
                                 if mk_is_pick(L[i][k], FAM[i]) != sh5(L[i][k], FAM[i])])
                             for i in range(NSRC)])
G[u'shell_pg_token0'] = [len([x for x in L[i] if f5(x).split(u' ')[0:1] == [u'[Page'] and sh5(x, FAM[i])])
                         for i in range(NSRC)]
G[u'shell_fold_eats_ff'] = [len([x for x in L[i] if len(x) and ord(x[0]) == 12 and f5(x) != x])
                            for i in range(NSRC)]

# ---------- 面量字符账 ----------
G[u'shlig_chars'] = [len(x) for x in SHLIG5]
G[u'sh_chars'] = [len(x) for x in SH5]
G[u'fold_chars'] = [len(x) for x in FOLD5]
G[u'lig_char_add'] = [G[u'shlig_chars'][i] - G[u'sh_chars'][i] for i in range(NSRC)]
G[u'lig_add_close'] = [G[u'lig_char_add'][i] - G[u'lig_total'][i] for i in range(NSRC)]

# ---------- 页壳账 ----------
G[u'pg_lines'] = [len([x for x in L[i] if u'[Page' in x]) for i in range(NSRC)]
G[u'hdr_lines_tight'] = [len([x for x in L[i] if sh5(x, u'rfc') and _nb5(x)]) - G[u'pg_lines'][i]
                         for i in range(NSRC)]
G[u'pgnum_naive'] = [len([x for x in L[i] if dline5(x)]) for i in range(NSRC)]
G[u'pgnum_ffled'] = [len([x for x in L[i] if dline5(x) and len(x) and ord(x[0]) == 12])
                     for i in range(NSRC)]
G[u'pgnum_overstrip'] = [G[u'pgnum_naive'][i] - G[u'pgnum_ffled'][i] for i in range(NSRC)]
G[u'pgnum_multirun'] = [len([x for x in L[i] if druns5(x) >= 2 and re.fullmatch(u'[\\s\\d]*', x)])
                        for i in range(NSRC)]
G[u'pgnum_anyshape'] = [G[u'pgnum_naive'][i] + G[u'pgnum_multirun'][i] for i in range(NSRC)]
G[u'pgnum_ruler_gap'] = [G[u'pgnum_anyshape'][i] - G[u'pgnum_naive'][i] for i in range(NSRC)]
G[u'shell_lines'] = [len([x for x in L[i] if sh5(x, FAM[i])]) for i in range(NSRC)]
G[u'shell_ledger'] = [G[u'shell_lines'][i] - G[u'blank'][i]
                      - (G[u'pg_lines'][i] + G[u'hdr_lines_tight'][i] if FAM[i] == u'rfc'
                         else G[u'pgnum_ffled'][i]) for i in range(NSRC)]
G[u'shell_nonblank'] = [len([x for x in L[i] if sh5(x, FAM[i]) and _nb5(x)]) for i in range(NSRC)]
G[u'shell_blank_only'] = [1 if G[u'shell_nonblank'][i] == 0 else 0 for i in range(NSRC)]
G[u'sh_minus_fold'] = [G[u'sh_chars'][i] - G[u'fold_chars'][i] for i in range(NSRC)]
G[u'shell_text_chars'] = [-G[u'sh_minus_fold'][i] for i in range(NSRC)]
for i in range(NSRC):
    assert [1 for x in L[i] if mk_dline(x)] == [1 for x in L[i] if dline5(x)], i
    assert [x for x in L[i] if mk_shell(x, FAM[i])] == [x for x in L[i] if sh5(x, FAM[i])], i
    assert mk_druns(NL.join(L[i])) == sum(druns5(x) for x in L[i])

# ---------- 拼写 ⇎ 术语: 子串轨换 str.count, 词窗轨换转置滑窗 ----------
G[u'spell_fam'] = SPELL
G[u'term_fam'] = TERM
G[u'spell'] = [[c5(LOW_SHLIG5[i], nd) for nd in SPELL] for i in range(NSRC)]
G[u'term'] = [[c5(LOW_SHLIG5[i], nd) for nd in TERM] for i in range(NSRC)]
G[u'spell_word'] = [[win5(TOK5[i], nd) for nd in SPELL] for i in range(NSRC)]
G[u'term_word'] = [[win5(TOK5[i], nd) for nd in TERM] for i in range(NSRC)]
G[u'spell_ruler_gap'] = [sum(G[u'spell'][i][k] - G[u'spell_word'][i][k] for k in range(len(SPELL)))
                         for i in range(NSRC)]
G[u'term_ruler_gap'] = [sum(G[u'term'][i][k] - G[u'term_word'][i][k] for k in range(len(TERM)))
                        for i in range(NSRC)]
G[u'spell_side'] = [u'queuing' if G[u'spell'][i][0] > G[u'spell'][i][1] else
                    (u'queueing' if G[u'spell'][i][1] > G[u'spell'][i][0] else u'两拼都有')
                    for i in range(NSRC)]
G[u'spell_minor'] = [min(G[u'spell'][i][0], G[u'spell'][i][1]) for i in range(NSRC)]
G[u'spell_major'] = [max(G[u'spell'][i][0], G[u'spell'][i][1]) for i in range(NSRC)]
G[u'spell_one_n'] = len([x for x in G[u'spell_minor'] if x == 0])
G[u'spell_sum_close'] = [G[u'spell_major'][i] + G[u'spell_minor'][i]
                         - (G[u'spell'][i][0] + G[u'spell'][i][1]) for i in range(NSRC)]
G[u'spell_phrase_sum'] = [sum(G[u'spell'][i][2:]) for i in range(NSRC)]
G[u'spell_phrase_two'] = [G[u'spell'][i][3] + G[u'spell'][i][4] for i in range(NSRC)]
G[u'term_side'] = [u'latency' if G[u'term'][i][1] > G[u'term'][i][0] else u'delay' for i in range(NSRC)]
G[u'term_minor'] = [min(G[u'term'][i][0], G[u'term'][i][1]) for i in range(NSRC)]
G[u'term_major'] = [max(G[u'term'][i][0], G[u'term'][i][1]) for i in range(NSRC)]
G[u'term_skew'] = [round(float(G[u'term_major'][i]) / G[u'term_minor'][i], 1) for i in range(NSRC)]
G[u'term_own'] = [[TERM[k] for k in range(len(TERM)) if G[u'term'][i][k]
                   and all(G[u'term'][j][k] == 0 for j in range(NSRC) if j != i)] for i in range(NSRC)]
for i in range(NSRC):
    assert G[u'spell'][i] == [mk_cnt_re(LOW_SHLIG5[i], nd) for nd in SPELL], i
    assert G[u'term'][i] == [mk_cnt_re(LOW_SHLIG5[i], nd) for nd in TERM], i
    assert G[u'spell_word'][i] == [mk_win(TOK5[i], nd) for nd in SPELL], i
    assert G[u'term_word'][i] == [mk_win(TOK5[i], nd) for nd in TERM], i
    assert [c5(SH5[i], nd) for nd in SPELL] == [mk_cnt_re(SH5[i], nd) for nd in SPELL], i
    assert o5(LOW_SHLIG5[i], u'ms') == mk_cnt_ovl(LOW_SHLIG5[i], u'ms')
    assert c5(LOW_SHLIG5[i], u'ms') == mk_cnt_cur(LOW_SHLIG5[i], u'ms')

# ---------- 字距拉开三把尺 ----------
G[u'rtt_tight'] = [c5(LOW_SHLIG5[i], u'rtt') for i in range(NSRC)]
G[u'rtt_kern'] = [c5(SHLIG5[i], u'RT T') for i in range(NSRC)]
G[u'rtt_loose'] = [c5(LOW_SHLIG5[i], u'rt t') for i in range(NSRC)]
G[u'rtt_loose_false'] = [G[u'rtt_loose'][i] - G[u'rtt_kern'][i] for i in range(NSRC)]
FW = []
for i in range(NSRC):
    got = []
    for m in re.finditer(u'(?=rt t)', LOW_SHLIG5[i]):
        a = m.start()
        got.append(f5(LOW_SHLIG5[i][max(0, a - 6):a + 8]).split(u' ')[0])
    FW.append(sorted(set(got))[:4])
G[u'rtt_false_words'] = FW

# ---------- 单位制 ⇎ 数值集 ----------
G[u'unit_fam'] = UNIT
G[u'unit'] = [[c5(LOW_SHLIG5[i], nd) for nd in UNIT] for i in range(NSRC)]
G[u'unit_word'] = [[ub5(LOW_SHLIG5[i], nd) for nd in UNIT] for i in range(NSRC)]
G[u'unit_sub_over'] = [G[u'unit'][i][0] - G[u'unit_word'][i][0] for i in range(NSRC)]
G[u'numvals'] = [sorted(set(pairs5(LOW_SHLIG5[i], u'a'))) for i in range(NSRC)]
G[u'numval_n'] = [len(x) for x in G[u'numvals']]
G[u'numval_s_pairs'] = [sorted(set(pairs5(LOW_SHLIG5[i], u'b'))) for i in range(NSRC)]
G[u'numval_s_extra'] = [[x for x in G[u'numval_s_pairs'][i] if x not in G[u'numvals'][i]]
                        for i in range(NSRC)]
G[u'numval_s_lost'] = [[x for x in G[u'numvals'][i] if x not in G[u'numval_s_pairs'][i]]
                       for i in range(NSRC)]
for i in range(NSRC):
    assert G[u'numvals'][i] == sorted(set(mk_pairs(LOW_SHLIG5[i], UNITW))), i
    assert G[u'numval_s_pairs'][i] == sorted(set(mk_pairs(LOW_SHLIG5[i], UNITW_S))), i
    assert G[u'unit_word'][i] == [mk_ub(LOW_SHLIG5[i], nd) for nd in UNIT], i
    assert G[u'unit'][i] == [mk_cnt_re(LOW_SHLIG5[i], nd) for nd in UNIT], i
    assert G[u'rtt_false_words'][i] == FLAT[u'rtt_false_words'][i], i

# ---------- 数字族 ----------
G[u'num_fam'] = NUM
G[u'num'] = [[c5(LOW_SHLIG5[i], nd) for nd in NUM] for i in range(NSRC)]
G[u'num_raw'] = [[c5(LOWFOLD5[i], nd) for nd in NUM] for i in range(NSRC)]
G[u'num_word'] = [[win5(TOK5[i], nd) for nd in NUM] for i in range(NSRC)]
G[u'num_lig_gap'] = [sum(G[u'num'][i]) - sum(G[u'num_raw'][i]) for i in range(NSRC)]
G[u'num_sub_vs_word'] = [sum(G[u'num'][i][k] - G[u'num_word'][i][k]) for k in range(0)
                         for i in range(NSRC)]
G[u'num_tot'] = [sum(x) for x in G[u'num']]
G[u'num_own'] = [[NUM[k] for k in range(len(NUM)) if G[u'num'][i][k]
                  and all(G[u'num'][j][k] == 0 for j in range(NSRC) if j != i)] for i in range(NSRC)]
G[u'num_zero_n'] = [len([k for k in range(len(NUM)) if G[u'num'][i][k] == 0]) for i in range(NSRC)]
for i in range(NSRC):
    assert G[u'num'][i] == [mk_cnt_re(LOW_SHLIG5[i], nd) for nd in NUM], i
    assert G[u'num_word'][i] == [mk_win(TOK5[i], nd) for nd in NUM], i
    assert G[u'num_raw'][i] == [mk_cnt_re(LOWFOLD5[i], nd) for nd in NUM], i
assert G[u'num'][0] == [0] * len(NUM) and G[u'num_tot'] == [0, 76, 17, 9, 23]
assert G[u'num_lig_gap'] == [0] * NSRC
assert G[u'num_sub_vs_word'] == []

# ---------- 角色四档: 原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳+拆字 ----------
G[u'role_src'] = [x[0] for x in ROLE]
G[u'role_kind'] = [x[1] for x in ROLE]
G[u'role_fam'] = ROLEN
G[u'role_line'] = [[sum(c5(y.lower(), nd) for y in L[i]) for nd in ROLEN] for i in range(NSRC)]
G[u'role_fold'] = [[c5(LOWFOLD5[i], nd) for nd in ROLEN] for i in range(NSRC)]
G[u'role_sh'] = [[c5(LOW_SH5[i], nd) for nd in ROLEN] for i in range(NSRC)]
G[u'role_lig'] = [[c5(LOW_SHLIG5[i], nd) for nd in ROLEN] for i in range(NSRC)]
G[u'role_ovl_close'] = sum(sum(o5(LOW_SHLIG5[i], ROLEN[k]) - c5(LOW_SHLIG5[i], ROLEN[k])
                               for k in range(len(ROLEN))) for i in range(NSRC))
G[u'role_wrap'] = [[k for k in range(len(ROLEN)) if G[u'role_src'][k] == LBL[i]
                    and G[u'role_line'][i][k] == 0 and G[u'role_fold'][i][k] >= 1] for i in range(NSRC)]
G[u'role_dup'] = [[k for k in range(len(ROLEN)) if G[u'role_src'][k] == LBL[i]
                   and G[u'role_line'][i][k] >= 1 and G[u'role_fold'][i][k] > G[u'role_line'][i][k]]
                  for i in range(NSRC)]
G[u'role_wrap_n'] = [len(x) for x in G[u'role_wrap']]
G[u'role_dup_n'] = [len(x) for x in G[u'role_dup']]
G[u'role_straddle'] = [sum(G[u'role_fold'][i]) - sum(G[u'role_line'][i]) for i in range(NSRC)]
G[u'role_straddle_ledger'] = [G[u'role_straddle'][i] - G[u'role_wrap_n'][i] - G[u'role_dup_n'][i]
                              for i in range(NSRC)]
G[u'role_shell_gain'] = [sum(G[u'role_sh'][i]) - sum(G[u'role_fold'][i]) for i in range(NSRC)]
G[u'role_lig_gain'] = [sum(G[u'role_lig'][i]) - sum(G[u'role_sh'][i]) for i in range(NSRC)]
G[u'role_shell_needles'] = sorted([k for i in range(NSRC) for k in range(len(ROLEN))
                                   if G[u'role_src'][k] == LBL[i]
                                   and G[u'role_fold'][i][k] == 0 and G[u'role_sh'][i][k] == 1])
G[u'role_line_miss'] = [k for k in range(len(ROLEN))
                        if G[u'role_line'][LBL.index(G[u'role_src'][k])][k] == 0]
G[u'role_line_miss_n'] = len(G[u'role_line_miss'])
G[u'role_line_read_n'] = len(ROLEN) - G[u'role_line_miss_n']
G[u'role_own'] = [[k for k in range(len(ROLEN)) if G[u'role_lig'][i][k]
                   and all(G[u'role_lig'][j][k] == 0 for j in range(NSRC) if j != i)]
                  for i in range(NSRC)]
G[u'role_multi'] = [(G[u'role_src'][k], G[u'role_kind'][k],
                     G[u'role_lig'][LBL.index(G[u'role_src'][k])][k])
                    for k in range(len(ROLEN))
                    if G[u'role_lig'][LBL.index(G[u'role_src'][k])][k] > 1]
WRAPK5 = sorted([k for x in G[u'role_wrap'] for k in x])
SHELLK5 = sorted(G[u'role_shell_needles'])
G[u'role_miss_ledger'] = sorted(WRAPK5 + SHELLK5) == G[u'role_line_miss']
G[u'role_wrap_shell_overlap'] = len(set(WRAPK5) & set(SHELLK5))
G[u'ms100_roles'] = [(G[u'role_src'][k], G[u'role_kind'][k]) for k in range(len(ROLEN))
                     if u'100 ms' in ROLEN[k]]
G[u'ms100_count'] = [G[u'num'][i][NUM.index(u'100 ms')] for i in range(NSRC)]
G[u'needle_n'] = len(ROLEN) + len(NUM) + len(NEG)
G[u'face_n'] = 4
for i in range(NSRC):
    assert G[u'role_line'][i] == [sum(mk_cnt_re(y.lower(), nd) for y in L[i]) for nd in ROLEN], i
    assert G[u'role_fold'][i] == [mk_cnt_re(LOWFOLD5[i], nd) for nd in ROLEN], i
    assert G[u'role_sh'][i] == [mk_cnt_re(LOW_SH5[i], nd) for nd in ROLEN], i
    assert G[u'role_lig'][i] == [mk_cnt_re(LOW_SHLIG5[i], nd) for nd in ROLEN], i
assert G[u'role_straddle_ledger'] == [0] * NSRC and G[u'role_ovl_close'] == 0
assert G[u'role_wrap_n'] == [0, 0, 1, 0, 5] and G[u'role_dup_n'] == [1, 0, 0, 0, 0]
assert G[u'role_shell_gain'] == [0, 0, 1, 0, 1] and G[u'role_lig_gain'] == [0] * NSRC
assert G[u'role_miss_ledger'] and G[u'role_wrap_shell_overlap'] == 0
assert G[u'role_line_miss'] == [11, 18, 19, 20, 21, 24, 25, 26] and G[u'role_line_read_n'] == 19
for k in range(len(ROLEN)):
    i = LBL.index(G[u'role_src'][k])
    assert G[u'role_lig'][i][k] >= 1, (k, ROLEN[k])
    assert sum(G[u'role_lig'][j][k] for j in range(NSRC)) == G[u'role_lig'][i][k], (k, ROLEN[k])
assert len(G[u'ms100_roles']) == 6 and G[u'ms100_count'] == [0, 22, 0, 0, 9]

# ---------- 反面针: 每根针带一份“必须读零”的清单, 含大写针走逐字符等值面 ----------
G[u'neg_fam'] = [x[0] for x in NEG]
G[u'neg_zero_on'] = [x[1] for x in NEG]
G[u'neg_kind'] = [x[2] for x in NEG]
G[u'neg_n'] = len(NEG)


def nface5(i, nd):
    return SHLIG5[i] if nd != nd.lower() else LOW_SHLIG5[i]


G[u'neg_word'] = [[ub5(nface5(i, nd), nd) for i in range(NSRC)] for nd in G[u'neg_fam']]
G[u'neg_sub'] = [[c5(nface5(i, nd), nd) for i in range(NSRC)] for nd in G[u'neg_fam']]
G[u'neg_zero_idx'] = [[LBL.index(l) for l in x[1]] for x in NEG]
G[u'neg_probes'] = sum(len(x[1]) for x in NEG)
G[u'neg_zero_hits'] = sum(G[u'neg_word'][k][i] for k in range(G[u'neg_n'])
                          for i in G[u'neg_zero_idx'][k])
G[u'neg_owner_present'] = len([k for k in range(G[u'neg_n'])
                               if max(G[u'neg_word'][k]) > 0 and len(G[u'neg_zero_on'][k]) < NSRC])
G[u'neg_sub_false'] = sum(G[u'neg_sub'][k][i] - G[u'neg_word'][k][i] for k in range(G[u'neg_n'])
                          for i in G[u'neg_zero_idx'][k])
G[u'neg_sub_false_rows'] = [(G[u'neg_fam'][k], LBL[i], G[u'neg_sub'][k][i], G[u'neg_word'][k][i])
                            for k in range(G[u'neg_n']) for i in G[u'neg_zero_idx'][k]
                            if G[u'neg_sub'][k][i] != G[u'neg_word'][k][i]]
for k in range(G[u'neg_n']):
    nd = G[u'neg_fam'][k]
    for i in range(NSRC):
        assert G[u'neg_word'][k][i] == mk_ub(nface5(i, nd), nd), (k, i)
        assert G[u'neg_sub'][k][i] == mk_cnt_re(nface5(i, nd), nd), (k, i)
assert G[u'neg_zero_hits'] == 0, [(G[u'neg_fam'][k], LBL[i], G[u'neg_word'][k][i])
                                  for k in range(G[u'neg_n']) for i in G[u'neg_zero_idx'][k]]

# ---------- 参数名 ⇎ 免配置族 ----------
G[u'par_fam'] = PAR
G[u'par'] = [[c5(SHLIG5[i], nd) for nd in PAR] for i in range(NSRC)]
G[u'par_upper_n'] = [len([k for k in range(4) if G[u'par'][i][k]]) for i in range(NSRC)]
G[u'par_greek_n'] = [len([k for k in range(4, 8) if G[u'par'][i][k]]) for i in range(NSRC)]
G[u'par_impl_n'] = [len([k for k in range(8, 11) if G[u'par'][i][k]]) for i in range(NSRC)]
G[u'par_impl'] = [[(PAR[k], G[u'par'][i][k]) for k in range(8, 11) if G[u'par'][i][k]]
                  for i in range(NSRC)]
G[u'cfg_fam'] = CFG
G[u'cfg'] = [[c5(LOW_SHLIG5[i], nd) for nd in CFG] for i in range(NSRC)]
G[u'cfg_claim'] = [sum(G[u'cfg'][i][:6]) for i in range(NSRC)]
G[u'cfg_own'] = [[CFG[k] for k in range(len(CFG)) if G[u'cfg'][i][k]
                  and all(G[u'cfg'][j][k] == 0 for j in range(NSRC) if j != i)] for i in range(NSRC)]
G[u'cfg_lig_gain'] = [c5(LOWLIG5[i], u'configuration') - c5(LOWFOLD5[i], u'configuration')
                      for i in range(NSRC)]
G[u'cfg_lig_needle'] = [c5(LOWLIG5[i], u'configuration') for i in range(NSRC)]
G[u'cfg_lig_words'] = [len(set([nd for nd in CFG
                                 if c5(LOWLIG5[i], nd) > c5(LOWFOLD5[i], nd)])) for i in range(NSRC)]
for i in range(NSRC):
    assert G[u'par'][i] == [mk_cnt_re(SHLIG5[i], nd) for nd in PAR], i
    assert G[u'cfg'][i] == [mk_cnt_re(LOW_SHLIG5[i], nd) for nd in CFG], i
    assert G[u'cfg_lig_needle'][i] == mk_cnt_re(LOWLIG5[i], u'configuration'), i
assert (G[u'par_upper_n'] == [0, 0, 2, 0, 2] and G[u'par_greek_n'] == [0, 4, 0, 0, 0]
        and G[u'par_impl_n'] == [0, 1, 0, 0, 0] and G[u'par_impl'][1] == [(u'pdrop', 4)])
assert [len(x) for x in G[u'cfg_own']] == [2, 0, 2, 0, 1] and G[u'cfg_claim'] == [8, 1, 2, 0, 1]
assert G[u'cfg_lig_gain'] == [0, 0, 0, 7, 0]
assert G[u'cfg_lig_needle'] == [3, 0, 0, 7, 4] and G[u'cfg_lig_words'] == [0, 0, 0, 1, 0]
assert G[u'cfg_lig_gain'][0] == G[u'cfg_lig_gain'][4] == 0

# ---------- 义务词阶梯: 邻居手扫轨 ⇎ 断言正则轨 ----------
G[u'tone_fam'] = TONE
G[u'tone_raw'] = [[ub5(T[i], nd) for nd in TONE] for i in range(NSRC)]
G[u'tone_sh'] = [[ub5(SHLIG5[i], nd) for nd in TONE] for i in range(NSRC)]
G[u'tone_re_track'] = [[len(re.findall(u'(?<![A-Za-z])' + re.escape(nd) + u'(?![A-Za-z])', SHLIG5[i]))
                       for nd in TONE] for i in range(NSRC)]
G[u'tone_ruler_close'] = sum(abs(G[u'tone_sh'][i][k] - G[u'tone_re_track'][i][k])
                             for i in range(NSRC) for k in range(5))
G[u'tone_straddle_k'] = [[G[u'tone_sh'][i][k] - G[u'tone_raw'][i][k] for k in range(5)]
                         for i in range(NSRC)]
G[u'tone_straddle'] = [sum(x) for x in G[u'tone_straddle_k']]
G[u'tone_lc'] = [[c5(LOW_SHLIG5[i], w) for w in (u'must', u'should', u'may', u'can')]
                 for i in range(NSRC)]
G[u'tone_must_pure'] = [ub5(SHLIG5[i], u'MUST') - ub5(SHLIG5[i], u'MUST NOT') for i in range(NSRC)]
G[u'tone_must_ledger'] = [G[u'tone_sh'][i][1] - G[u'tone_sh'][i][0] - G[u'tone_must_pure'][i]
                          for i in range(NSRC)]
for i in range(NSRC):
    assert G[u'tone_raw'][i] == [mk_ub(T[i], nd) for nd in TONE], i
    assert G[u'tone_sh'][i] == [mk_ub(SHLIG5[i], nd) for nd in TONE], i
    assert G[u'tone_lc'][i] == [mk_cnt_re(LOW_SHLIG5[i], w)
                                for w in (u'must', u'should', u'may', u'can')], i
assert G[u'tone_ruler_close'] == 0 and G[u'tone_must_ledger'] == [0] * NSRC
assert G[u'tone_straddle'] == [0, 0, 0, 0, 1]

# ---------- 标题分档: 本遍用 hshape5 的正则选择支, 第二遍用逐字符吃档 ----------
TONED5 = lambda x: 1 if any(ub5(x, nd) for nd in TONE) else 0
HS5 = [[hshape5(x) for x in L[i]] for i in range(NSRC)]
G[u'head_tone_toc'] = [len([x for x, h in zip(L[i], HS5[i])
                            if h[3] and h[0] and h[1] >= 2 and TONED5(x)]) for i in range(NSRC)]
G[u'head_tone_list'] = [len([x for x, h in zip(L[i], HS5[i])
                             if h[3] and h[0] and h[1] == 1 and h[4] and TONED5(x)]) for i in range(NSRC)]
G[u'head_tone_sec'] = [len([x for x, h in zip(L[i], HS5[i])
                            if h[3] and not h[0] and h[1] >= 2 and TONED5(x)]) for i in range(NSRC)]
G[u'head_tone_shape'] = [len([x for x in L[i] if re.match(HEADRX, x) and TONED5(x)]) for i in range(NSRC)]
G[u'head_tone_stray'] = [G[u'head_tone_shape'][i] - G[u'head_tone_toc'][i] - G[u'head_tone_list'][i]
                         - G[u'head_tone_sec'][i] for i in range(NSRC)]
G[u'head_toc_leader_strict'] = [len([x for x, h in zip(L[i], HS5[i])
                                     if h[3] and h[0] and h[1] >= 2 and TONED5(x) and has_leader5(x)])
                                for i in range(NSRC)]
G[u'head_toc_leader_spaced'] = [len([x for x, h in zip(L[i], HS5[i])
                                     if h[3] and h[0] and h[1] >= 2 and TONED5(x) and leader_sp5(x)])
                                for i in range(NSRC)]
G[u'head_tone_stray_lines'] = [[f5(x) for x, h in zip(L[i], HS5[i])
                                if re.match(HEADRX, x) and TONED5(x)
                                and not (h[3] and (h[1] >= 2 or (h[0] and h[1] == 1)))]
                               for i in range(NSRC)]
G[u'head_tier_pick'] = [[len([x for x in L[i] if re.match(u'^ +\\d+\\.\\d', x) and TONED5(x)]),
                         len([x for x in L[i] if re.match(u'^ +\\d+\\.\\s+\\S', x) and TONED5(x)]),
                         len([x for x in L[i] if re.match(u'^\\d+\\.\\d', x) and TONED5(x)])]
                        for i in range(NSRC)]
G[u'head_tier_close'] = [sum([abs(G[u'head_tier_pick'][i][t] - x)
                              for t, x in enumerate([G[u'head_tone_toc'][i], G[u'head_tone_list'][i],
                                                     G[u'head_tone_sec'][i]])]) for i in range(NSRC)]
for i in range(NSRC):
    assert HS5[i] == [mk_hshape(x) for x in L[i]], i
    assert G[u'head_tone_stray_lines'][i] == [mk_fold(x) for x, h in zip(L[i], HS5[i])
                                              if re.match(HEADRX, x) and TONED5(x)
                                              and not (h[3] and (h[1] >= 2 or (h[0] and h[1] == 1)))], i
assert (G[u'head_tone_toc'] == [4, 0, 0, 0, 0] and G[u'head_tone_list'] == [6, 0, 0, 0, 0]
        and G[u'head_tone_sec'] == [4, 0, 0, 0, 0] and G[u'head_tone_shape'] == [15, 0, 0, 0, 0])
assert G[u'head_tier_close'] == [0] * NSRC and G[u'head_tone_stray'] == [1, 0, 0, 0, 0]
assert (G[u'head_toc_leader_strict'] == [0] * NSRC
        and G[u'head_toc_leader_spaced'] == [1, 0, 0, 0, 0])

# ---------- 语态 ⇎ 引用 ----------
G[u'voice_fam'] = VOICE
G[u'voice'] = [[c5(LOW_SHLIG5[i], nd) for nd in VOICE] for i in range(NSRC)]
G[u'voice_we'] = [G[u'voice'][i][0] for i in range(NSRC)]
G[u'voice_impersonal'] = [G[u'voice'][i][1] + G[u'voice'][i][2] for i in range(NSRC)]
G[u'voice_weverb'] = [sum(G[u'voice'][i][3:7]) for i in range(NSRC)]
G[u'cit_fam'] = CIT
G[u'cit'] = [[c5(SHLIG5[i], nd) for nd in CIT] for i in range(NSRC)]
G[u'cit_brk'] = [brk5(SHLIG5[i]) for i in range(NSRC)]
G[u'cit_rfc'] = [len(re.findall(u'RFC \\d{4}', SHLIG5[i])) for i in range(NSRC)]
G[u'cite_matrix'] = [[(0 if i == j or not IDS[j] else rfcline5(SHLIG5[i], IDS[j]))
                     for j in range(NSRC)] for i in range(NSRC)]
for i in range(NSRC):
    assert G[u'voice'][i] == [mk_cnt_re(LOW_SHLIG5[i], nd) for nd in VOICE], i
    assert G[u'cit'][i] == [mk_cnt_re(SHLIG5[i], nd) for nd in CIT], i
    assert G[u'cit_brk'][i] == len(re.findall(u'\\[\\d+\\]', SHLIG5[i])), i
    for j in range(NSRC):
        assert G[u'cite_matrix'][i][j] == (0 if i == j or not IDS[j] else
                                          len([1 for y in SHLIG5[i].split(u'RFC ')
                                               if y.startswith(IDS[j] + u' ')
                                               or y.startswith(IDS[j] + u',')])), (i, j)
assert (G[u'voice_weverb'] == [0, 8, 0, 2, 0]
        and G[u'voice_impersonal'] == [36, 0, 17, 0, 21])
assert max(G[u'voice_we'][i] for i in RFCI) > min(G[u'voice_we'][i] for i in PAPI)
assert (G[u'cite_matrix'][4] == [0] * NSRC and G[u'cite_matrix'][3] == [0] * NSRC
        and G[u'cite_matrix'][1][0] == 1 and G[u'cite_matrix'][2][0] == 2)
assert ([G[u'cit_brk'][i] for i in RFCI] == [0, 0, 0]
        and [G[u'cit_rfc'][i] for i in PAPI] == [1, 4])

# ---------- 节窗: 节号由 hshape5 的点段 ⇎ rom5 的罗马串导出, 比大小靠整数元组 ----------
G[u'sec_no'] = []
G[u'sec_title'] = []
G[u'sec_lines'] = []
G[u'sec_chars'] = []
G[u'sec_tone'] = []
G[u'sec_numval'] = []
G[u'sec_par'] = []
G[u'sec_role'] = []
TOCL5, BODYL5, HITN5, W5, WS5 = [], [], [], [], []
for i in range(NSRC):
    hit = [x for x, y in enumerate(L[i]) if WIN[i] in y]
    assert hit, (i, WIN[i])
    HITN5.append(len(hit))
    TOCL5.append(hit[0] + 1 if len(hit) > 1 else None)
    k = hit[-1]
    BODYL5.append(k + 1)
    if FAM[i] == u'rfc':
        heads = [(x, HS5[i][x]) for x in range(len(L[i])) if HS5[i][x][3] and dotrun5(L[i][x]) < 3]
    else:
        heads = [(x, (0, 1, rom5(L[i][x])[0], 1, 0)) for x in range(len(L[i]))
                 if rom5(L[i][x])[1] > 0 and dotrun5(L[i][x]) < 3]
    assert heads, i
    bg = [h for h in heads if h[0] <= k][-1]
    if FAM[i] == u'rfc':
        cur = tuple([int(z) for z in bg[1][2].split(u'.')])
        lvl = len(cur)
    else:
        cur, lvl = (0,), 1
    nxt = len(L[i])
    for x, h in heads:
        if x <= bg[0]:
            continue
        if FAM[i] == u'rfc':
            if h[1] == 0:
                continue
            tup = tuple([int(z) for z in h[2].split(u'.')])
            if len(tup) <= lvl and tup >= cur:
                nxt = x
                break
        else:
            nxt = x
            break
    w = f5(NL.join(x for x in L[i][bg[0]:nxt] if not sh5(x, FAM[i])))
    W5.append(w)
    WS5.append((bg[0], nxt))
    G[u'sec_no'].append(bg[1][2])
    G[u'sec_title'].append(f5(L[i][bg[0]]))
    G[u'sec_lines'].append(nxt - bg[0])
    G[u'sec_chars'].append(len(w))
    G[u'sec_tone'].append([ub5(w, nd) for nd in TONE])
    G[u'sec_numval'].append(sorted(set(pairs5(w.lower(), u'a'))))
    G[u'sec_par'].append([c5(w, nd) for nd in PAR])
    G[u'sec_role'].append([kk for kk in range(len(ROLEN)) if G[u'role_src'][kk] == LBL[i]
                           and ROLEN[kk] in w.lower()])
G[u'sec_hit_n'] = HITN5
G[u'sec_toc_line'] = TOCL5
G[u'sec_body_line'] = BODYL5
G[u'sec_tone_tot'] = [sum(x) for x in G[u'sec_tone']]
G[u'sec_span_pct'] = [round(100.0 * G[u'sec_chars'][i] / G[u'sh_chars'][i], 1) for i in range(NSRC)]
G[u'sec_no_pick'] = []
for i in range(NSRC):
    rx = re.compile(u'^\\s*(\\d+(?:\\.\\d+)*)\\.?\\s+\\S') if FAM[i] == u'rfc' \
        else re.compile(u'^\\s*([IVX]+)\\.\\s+[A-Z]')
    hh = [(x, rx.match(L[i][x])) for x in range(len(L[i]))
          if rx.match(L[i][x]) and RXR.search(L[i][x]) is None]
    G[u'sec_no_pick'].append([h for h in hh if h[0] <= G[u'sec_body_line'][i] - 1][-1][1].group(1))
SUB435 = [x + 1 for x, y in enumerate(L[4]) if re.match(u'^4\\.3\\.\\s', y)]
G[u'sec_sub_line'] = SUB435[0]
G[u'sec_sub_title'] = f5(L[4][SUB435[0] - 1])
for i in range(NSRC):
    assert G[u'sec_numval'][i] == sorted(set(mk_pairs(W5[i].lower(), UNITW))), i
    assert G[u'sec_par'][i] == [mk_cnt_re(W5[i], nd) for nd in PAR], i
    assert G[u'sec_tone'][i] == [mk_ub(W5[i], nd) for nd in TONE], i
    assert W5[i] == mk_fold(NL.join(x for x in L[i][WS5[i][0]:WS5[i][1]]
                                     if not mk_is_pick(x, FAM[i]))), i
    assert [dotrun5(x) for x in L[i]] == [mk_dotrun(x) for x in L[i]], i
    assert [rom5(x) for x in L[i]] == [mk_roman(x) for x in L[i]], i
assert G[u'sec_no_pick'] == G[u'sec_no'], (G[u'sec_no'], G[u'sec_no_pick'])
assert len(SUB435) == 1 and G[u'sec_sub_line'] > G[u'sec_body_line'][4]
assert G[u'sec_no'] == [u'4.3', u'I', u'8', u'IV', u'4'], G[u'sec_no']
assert (G[u'sec_lines'] == [69, 8, 32, 113, 91]
        and G[u'sec_chars'] == [2743, 3642, 1108, 7355, 4469])
assert G[u'sec_tone_tot'] == [9, 0, 0, 0, 4]
assert (G[u'sec_hit_n'][0] == 2 and G[u'sec_toc_line'][0] == 136
        and G[u'sec_body_line'][0] == 1071)
assert [x is None for x in G[u'sec_toc_line']] == [False, True, True, True, True]
assert [G[u'sec_body_line'][i] > G[u'sec_lines'][i] for i in range(NSRC)] == [True] * NSRC

# ---------- 答案句: 段界靠 _nb5 的空白档外扩, 句界靠一条前瞻正则 ----------
ANS5, SPAN5, BLOCKN5, ANSHELL5, ANSROW5 = [], [], [], [], []
TXT5 = []
for i, pat in enumerate(WIN):
    hit = [x for x, y in enumerate(L[i]) if pat in y]
    ln = hit[-1]
    lo = ln
    while lo - 1 >= 0 and _nb5(L[i][lo - 1]):
        lo -= 1
    hi = ln
    while hi + 1 < len(L[i]) and _nb5(L[i][hi + 1]):
        hi += 1
    blk = L[i][lo:hi + 1]
    ANSHELL5.append(len([x for x in blk if sh5(x, FAM[i]) and _nb5(x)]))
    rows = [f5(x) for x in blk if _nb5(x) and not sh5(x, FAM[i])]
    txt = u' '.join(rows)
    offs = [len(u' '.join(rows[:kk])) for kk in range(len(rows))]
    TXT5.append((txt, offs, rows))
    st = txt.lower().find(pat.lower())
    assert st >= 0, (LBL[i], pat)
    e = sent_end5(txt, st + len(pat))
    assert e >= st, (LBL[i], txt[st:st + 40])
    ANS5.append(txt[st:e + 1])
    SPAN5.append(len([kk for kk in range(len(rows))
                      if offs[kk] <= e and offs[kk] + len(rows[kk]) >= st]))
    BLOCKN5.append(len(rows))
    ANSROW5.append(ln + 1)
G[u'ans'] = ANS5
G[u'ans_words'] = [wc5(x) for x in ANS5]
G[u'ans_span'] = SPAN5
G[u'ans_block_lines'] = BLOCKN5
G[u'ans_shell_rows'] = ANSHELL5
G[u'ans_anchor_line'] = ANSROW5
G[u'ans_one_line_n'] = len([x for x in SPAN5 if x == 1])
G[u'ans_span_tot'] = sum(SPAN5)
G[u'ans_punct'] = [1 if x.endswith(u'.') else 0 for x in ANS5]
G[u'ans_punct_n'] = sum(G[u'ans_punct'])
for i, pat in enumerate(WIN):
    hit = [x for x, y in enumerate(L[i]) if pat in y]
    ln = hit[-1]
    lo = ln
    while lo - 1 >= 0 and L[i][lo - 1].strip() != u'':
        lo -= 1
    hi = ln
    while hi + 1 < len(L[i]) and L[i][hi + 1].strip() != u'':
        hi += 1
    rowsm = [mk_fold(x) for x in L[i][lo:hi + 1]
             if x.strip() != u'' and not mk_is_pick(x, FAM[i])]
    txtm, offs = u'', []
    for y in rowsm:
        offs.append(len(txtm))
        txtm += (u'' if txtm == u'' else u' ') + y
    stm = txtm.lower().find(pat.lower())
    em = mk_sent_end(txtm, stm + len(pat))
    assert ANS5[i] == txtm[stm:em + 1], i
    assert TXT5[i][0] == txtm, i
    assert TXT5[i][1] == offs, i
    assert G[u'ans_span'][i] == len([kk for kk in range(len(rowsm))
                                     if offs[kk] <= em and offs[kk] + len(rowsm[kk]) >= stm]), i
assert (G[u'ans_span'] == [1, 1, 3, 1, 2] and G[u'ans_block_lines'] == [1, 7, 6, 5, 14])
assert (G[u'ans_shell_rows'] == [0] * NSRC and G[u'ans_words'] == [8, 24, 22, 4, 10])
assert G[u'ans_one_line_n'] == 3 and G[u'ans_span_tot'] == 8
assert G[u'ans_punct'] == [0, 1, 1, 1, 1] and G[u'ans_punct_n'] == 4
assert G[u'ans'][0].endswith(u'Tuning') and G[u'ans'][2].endswith(u'respectively.')
assert G[u'ans_anchor_line'] == [1071, 15, 948, 184, 702]

# ---------- 段落层 ⇎ 行号尺: 折平加拆字带逐字符对照表, 行号靠 bisect 而非线性扫 ----------
TAGS5 = LBL
IDX5 = dict((t, n) for n, t in enumerate(LBL))
FAN5 = [p5(t) for t in T]
ROWS5 = [[(n, x) for n, x in enumerate(L[i], 1) if not sh5(x, FAM[i])] for i in range(NSRC)]
FD5 = []
for i in range(NSRC):
    arr = []
    for n, x in ROWS5[i]:
        f, ix = row_fd5(x)
        assert len(f) == len(ix) and len(f.lower()) == len(f), (LBL[i], n)
        arr.append((n, x, f, ix))
    FD5.append(arr)
    assert [a[1] for a in FD5[i]] == SHP5[i], i
    assert u' '.join(a[2] for a in FD5[i]) == SHLIG5[i], i
    assert [a[2] for a in FD5[i]] == [dg5(f5(a[1])) for a in FD5[i]], i
PP5 = [[(a[0], a[2]) for a in FD5[i]] for i in range(NSRC)]
ALN5 = FD5
ANSET5 = [set(a[1] for a in FD5[i]) for i in range(NSRC)]
ROWSRAW5 = [u'\x01'.join(p5(a[1]) for a in FD5[i]) for i in range(NSRC)]
G[u'pp_rows'] = [len(PP5[i]) for i in range(NSRC)]
G[u'pp_gap_rows'] = [G[u'nonblank'][i] - G[u'pp_rows'][i] for i in range(NSRC)]
G[u'pp_shell_nonblank'] = [G[u'shell_lines'][i] - G[u'blank'][i] for i in range(NSRC)]
G[u'pp_gap_close'] = sum(abs(G[u'pp_gap_rows'][i] - G[u'pp_shell_nonblank'][i]) for i in range(NSRC))
for i in range(NSRC):
    assert u' '.join(x for _, x in PP5[i]) == SHLIG5[i], i


def fmap5(i):
    ls = [len(s) for _, s in PP5[i]]
    return [(sum(ls[:k]) + k, PP5[i][k][0]) for k in range(len(ls))]


FMP5 = [fmap5(i) for i in range(NSRC)]
STS5 = [[o for o, _ in FMP5[i]] for i in range(NSRC)]


def line_of5(i, a):
    k = bisect.bisect_right(STS5[i], a) - 1
    return FMP5[i][k][1] if k >= 0 else 0


def loc5(i, a):
    k = bisect.bisect_right(STS5[i], a) - 1
    return FMP5[i][k][1], a - STS5[i][k]


def wl5(raw, k):
    if k <= 0 or raw[k - 1].isspace():
        return k
    return re.search(u'\\S+$', raw[:k]).start()


def wr5(raw, k):
    return k + len(re.match(u'\\S*', raw[k:]).group(0))


def grow5(raw, a, b, lim):
    lo, hi = wl5(raw, a), wr5(raw, b)
    while True:
        cand = []
        j = lo - 1
        while j >= 0 and raw[j].isspace():
            j -= 1
        if j >= 0:
            left = wl5(raw, j + 1)
            cand.append((lo - left, u'l', left))
        k = hi
        while k < len(raw) and raw[k].isspace():
            k += 1
        if k < len(raw):
            right = wr5(raw, k)
            cand.append((right - hi, u'r', right))
        if not cand:
            break
        d, side, pos = min(cand)
        if hi - lo + d > lim:
            break
        if side == u'l':
            lo = pos
        else:
            hi = pos
    return raw[lo:hi], lo, hi


def an5(i, nd, exact, lo, lim=92):
    """锚由面上位置导出: 命中的区间映回原行再按整词切窗——本遍的窗口尺与第二遍同定义不同写法"""
    key = p5(nd)
    hits = []
    for n, x, f, ix in ALN5[i]:
        if n < lo:
            continue
        p = f.lower()
        if exact:
            if p5(p) != key:
                continue
            a, b = 0, len(f)
        else:
            k = p.find(key)
            if k < 0:
                continue
            a, b = k, k + len(nd)
        seg, s, e = grow5(x, ix[a], ix[min(b, len(ix)) - 1] + 1, lim)
        assert seg in x, (LBL[i], n)
        assert key in p5(dg5(seg)), (LBL[i], n, nd)
        assert p5(seg) in FAN5[i], (LBL[i], seg[:60])
        hits.append((n, seg, x))
    return hits


def off_last5(i, nd):
    a = LOW_SHLIG5[i].rfind(p5(nd))
    assert a >= 0, (LBL[i], nd)
    return a


def blk5(i, start, end, frm=0):
    a = LOW_SHLIG5[i].find(p5(start), frm)
    assert a >= 0, (LBL[i], start, u'起')
    b = LOW_SHLIG5[i].find(p5(end), a)
    assert b >= 0, (LBL[i], end, u'止')
    e = b + len(p5(end))
    return f5(SHLIG5[i][a:e]), line_of5(i, a), line_of5(i, e - 1)


def line_holds5(i, ln, nd):
    for n, x, f, ix in ALN5[i]:
        if n == ln:
            return 1 if p5(nd) in p5(f) else 0
    raise AssertionError(u'行号无对应原行 %s %d' % (LBL[i], ln))


def split_pieces5(i, nd, last=False):
    f = LOW_SHLIG5[i]
    key = p5(nd)
    a = f.rfind(key) if last else f.find(key)
    assert a >= 0, (LBL[i], nd)
    e = a + len(key) - 1
    h, t = line_of5(i, a), line_of5(i, e)
    rh, fh, ixh = [y for y in ALN5[i] if y[0] == h][0][1:]
    rt, ft, ixt = [y for y in ALN5[i] if y[0] == t][0][1:]
    _, ao = loc5(i, a)
    _, te = loc5(i, e)
    head = rh[ixh[ao]:ixh[len(fh) - 1] + 1]
    tail = rt[ixt[0]:ixt[te] + 1]
    assert head in rh and tail in rt, (LBL[i], nd)
    return h, t, head, tail


# ---------- 段窗 ⇎ 关键词模板段 ⇎ 答句行号 ----------
PB5 = [blk5(i, s, e) for i, s, e in PINS]
PTXT5 = [p[0] for p in PB5]
G[u'blk_lo'] = [p[1] for p in PB5]
G[u'blk_hi'] = [p[2] for p in PB5]
G[u'blk_rows'] = [p[2] - p[1] + 1 for p in PB5]
G[u'blk_chars'] = [len(p[0]) for p in PB5]
G[u'blk_words'] = [wc5(p[0]) for p in PB5]
PW5 = [re.split(u'\\s+', p.strip().lower()) for p in PTXT5]
G[u'blk_vocab'] = [len(set(x)) for x in PW5]
G[u'blk_five_chars'] = sum(G[u'blk_chars'][:5])
G[u'blk_five_rows'] = sum(G[u'blk_rows'][:5])
G[u'blk_five_words'] = sum(G[u'blk_words'][:5])
G[u'blk_rows_tot'] = sum(G[u'blk_rows'])
G[u'blk_words_tot'] = sum(G[u'blk_words'])
G[u'tone_must_blk'] = [ub5(p, u'MUST') for p in PTXT5]
G[u'tone_may_blk'] = [ub5(p, u'MAY') for p in PTXT5]
G[u'tone_should_blk'] = [ub5(p, u'SHOULD') for p in PTXT5]
G[u'tone_mustnot_blk'] = [ub5(p, u'MUST NOT') for p in PTXT5]
G[u'tone_in_blk'] = [G[u'tone_must_blk'][n] + G[u'tone_may_blk'][n] + G[u'tone_should_blk'][n]
                     for n in range(len(PB5))]
G[u'blk_must_cur'] = [c5(p, u'MUST') for p in PTXT5]
G[u'blk_must_re'] = [len(re.findall(u'MUST', p)) for p in PTXT5]
G[u'blk_tone_ruler_close'] = (sum(abs(G[u'tone_must_blk'][n] - G[u'blk_must_cur'][n])
                                  for n in range(len(PB5)))
                              + sum(abs(G[u'tone_must_blk'][n] - G[u'blk_must_re'][n])
                                    for n in range(len(PB5))))
G[u'blk_lc'] = [c5(p.lower(), u'can ') + c5(p.lower(), u'should ') + c5(p.lower(), u'will ')
               for p in PTXT5]


def headw5(a, b):
    return len(list(IT.takewhile(lambda t: t[0] == t[1], zip(a, b))))


def sufw5(a, b):
    return len(list(IT.takewhile(lambda t: t[0] == t[1], zip(reversed(a), reversed(b)))))


G[u'pre_kw_7567_8033'] = headw5(PW5[9], PW5[10])
G[u'pre_kw_7567_8289'] = headw5(PW5[9], PW5[11])
G[u'pre_kw_8033_8289'] = headw5(PW5[10], PW5[11])
G[u'suf_kw_7567_8033'] = sufw5(PW5[9], PW5[10])
G[u'suf_kw_7567_8289'] = sufw5(PW5[9], PW5[11])
G[u'suf_kw_8033_8289'] = sufw5(PW5[10], PW5[11])
G[u'kw_same_7567_8033'] = 1 if PTXT5[9] == PTXT5[10] else 0
G[u'kw_all_same'] = 1 if (PTXT5[9] == PTXT5[10] == PTXT5[11]) else 0
G[u'kw_min_head'] = min(G[u'pre_kw_7567_8033'], G[u'pre_kw_7567_8289'], G[u'pre_kw_8033_8289'])
G[u'kw_max_head'] = max(G[u'pre_kw_7567_8033'], G[u'pre_kw_7567_8289'], G[u'pre_kw_8033_8289'])
G[u'suf_kw_tot'] = G[u'suf_kw_7567_8033'] + G[u'suf_kw_7567_8289'] + G[u'suf_kw_8033_8289']
G[u'kw_vocab_max'] = max(G[u'blk_vocab'][9], G[u'blk_vocab'][10], G[u'blk_vocab'][11])
G[u'kw_notrec'] = [ub5(PTXT5[n], u'NOT RECOMMENDED') for n in (9, 10, 11)]
G[u'kw_notrec_tot'] = sum(G[u'kw_notrec'])
KWPOS5 = [LOW_SHLIG5[i].find(p5(u'The key words')) for i in range(NSRC)]
G[u'kw_at'] = [x if x >= 0 else -1 for x in KWPOS5]
G[u'kw_docs'] = len([x for x in G[u'kw_at'] if x >= 0])
G[u'kw_minus_row'] = [line_of5(i, x) if x >= 0 else -1 for i, x in enumerate(G[u'kw_at'])]
ASDESC5 = p5(u'as described in')
G[u'as_desc_rows'] = [n for n, x, f, ix in ALN5[0] if ASDESC5 in f.lower()]
G[u'as_desc_n'] = len(G[u'as_desc_rows'])
G[u'blk_words_per_row'] = [G[u'blk_words'][n] // G[u'blk_rows'][n] for n in range(5)]
G[u'blk_is_one_line'] = [1 if G[u'blk_rows'][n] == 1 else 0 for n in range(5)]
G[u'blk_one_line_n'] = sum(G[u'blk_is_one_line'])
G[u'ans_head'] = [off_last5(i, WIN[i]) for i in range(NSRC)]
G[u'ans_head_line'] = [line_of5(i, a) for i, a in enumerate(G[u'ans_head'])]
G[u'ans_tail_line'] = [line_of5(i, a + len(p5(WIN[i])) - 1) for i, a in enumerate(G[u'ans_head'])]
G[u'ans_needle_span'] = [G[u'ans_tail_line'][i] - G[u'ans_head_line'][i] + 1 for i in range(NSRC)]
G[u'ans_sent_at'] = [LOW_SHLIG5[i].rfind(p5(G[u'ans'][i])) for i in range(NSRC)]
G[u'ans_sent_line'] = [line_of5(i, G[u'ans_sent_at'][i]) for i in range(NSRC)]
G[u'ans_sent_end'] = [line_of5(i, G[u'ans_sent_at'][i] + len(p5(G[u'ans'][i])) - 1)
                      for i in range(NSRC)]
G[u'ans_sent_span'] = [G[u'ans_sent_end'][i] - G[u'ans_sent_line'][i] + 1 for i in range(NSRC)]
G[u'ans_span_ind'] = [len([1 for n, x, f, ix in FD5[i]
                           if G[u'ans_head_line'][i] <= n <= G[u'ans_tail_line'][i]])
                      for i in range(NSRC)]
G[u'ans_line_close'] = sum(abs(G[u'ans_sent_line'][i] - G[u'ans_anchor_line'][i]) for i in range(NSRC))
G[u'ans_span_close'] = sum(abs(G[u'ans_sent_span'][i] - G[u'ans_span'][i]) for i in range(NSRC))
G[u'ans_needle_gap'] = [G[u'ans_span'][i] - G[u'ans_needle_span'][i] for i in range(NSRC)]
G[u'ans_row_ledger'] = [G[u'ans_sent_end'][i] - G[u'ans_sent_line'][i] + 1
                        - len([1 for n, x, f, ix in FD5[i]
                               if G[u'ans_sent_line'][i] <= n <= G[u'ans_sent_end'][i]])
                        for i in range(NSRC)]

# ---------- 切开判词: 两半各回自己那一行 ----------
SPLITREC5 = []
WRAPK25 = sorted([x for y in G[u'role_wrap'] for x in y])
SHELLK25 = sorted(G[u'role_shell_needles'])
assert WRAPK25 == WRAPK5 and SHELLK25 == sorted(SHELLK5) and not (set(WRAPK25) & set(SHELLK25))
for k in WRAPK25 + SHELLK25:
    i = LBL.index(G[u'role_src'][k])
    h, t, head, tail = split_pieces5(i, ROLEN[k])
    SPLITREC5.append((k, i, h, t, len(head), len(tail)))
G[u'split_k'] = [x[0] for x in SPLITREC5]
G[u'split_lbl'] = [LBL[x[1]] for x in SPLITREC5]
G[u'split_head'] = [x[2] for x in SPLITREC5]
G[u'split_tail'] = [x[3] for x in SPLITREC5]
G[u'split_span'] = [x[3] - x[2] + 1 for x in SPLITREC5]
G[u'split_span_tot'] = sum(G[u'split_span'])
G[u'split_head_chars'] = [x[4] for x in SPLITREC5]
G[u'split_tail_chars'] = [x[5] for x in SPLITREC5]
G[u'split_n'] = len(SPLITREC5)
G[u'split_rows_tot'] = sum(G[u'split_head_chars']) + sum(G[u'split_tail_chars'])
G[u'split_full_on_head'] = sum(line_holds5(x[1], x[2], ROLEN[x[0]]) for x in SPLITREC5)
G[u'split_half_ok'] = sum([line_holds5(x[1], x[2], p5(dg5(split_pieces5(x[1], ROLEN[x[0]])[2])))
                           for x in SPLITREC5])
G[u'split_shell_between'] = []
for x in SPLITREC5:
    if x[0] in SHELLK25:
        i = x[1]
        G[u'split_shell_between'].append(
            len([y for y in L[i][x[2]:x[3] - 1] if sh5(y, FAM[i]) and _nb5(y)]))
G[u'split_wrap_n'] = len(WRAPK5)
G[u'split_shell_n'] = len(SHELLK25)
G[u'split_ledger'] = G[u'split_n'] - len(G[u'role_line_miss'])
G[u'split_span_vs_miss'] = G[u'split_span_tot'] - G[u'split_n'] - sum(
    [len([1 for n2 in [y[0] for y in FD5[LBL.index(G[u'role_src'][k])]]
          if split_pieces5(LBL.index(G[u'role_src'][k]), ROLEN[k])[0] <= n2
          <= split_pieces5(LBL.index(G[u'role_src'][k]), ROLEN[k])[1]]) for k in G[u'split_k']])


def needle_at5(i, ln, nd, side):
    key = p5(nd)
    w = key.split(u' ')
    for m in range(len(ALN5[i])):
        if ALN5[i][m][0] != ln:
            continue
        p = p5(ALN5[i][m][2])
        if key in p:
            return 2
        prev = p5(ALN5[i][m - 1][2]) if m else u''
        nxt = p5(ALN5[i][m + 1][2]) if m + 1 < len(ALN5[i]) else u''
        for j in range(1, len(w)):
            if side == u'head' and p.endswith(u' '.join(w[:j])) and nxt.startswith(u' '.join(w[j:])):
                return 1
            if side == u'tail' and p.startswith(u' '.join(w[j:])) and prev.endswith(u' '.join(w[:j])):
                return 1
        return 0
    raise AssertionError(u'行号无对应原行 %s %d' % (LBL[i], ln))


SEGRT5 = []
for n, (i, s, e) in enumerate(PINS):
    SEGRT5.append((i, PB5[n][1], p5(s), u'head'))
    SEGRT5.append((i, PB5[n][2], p5(e), u'tail'))
G[u'seg_rt'] = [needle_at5(i, ln, nd, sd) for i, ln, nd, sd in SEGRT5]
G[u'seg_rt_n'] = len(G[u'seg_rt'])
G[u'seg_rt_ok'] = len([x for x in G[u'seg_rt'] if x])
G[u'seg_rt_whole'] = len([x for x in G[u'seg_rt'] if x == 2])
G[u'seg_rt_cut'] = len([x for x in G[u'seg_rt'] if x == 1])
G[u'seg_rt_head'] = len([1 for (i, ln, nd, sd), v in zip(SEGRT5, G[u'seg_rt']) if sd == u'head' and v])
G[u'seg_rt_tail'] = G[u'seg_rt_ok'] - G[u'seg_rt_head']
G[u'blk_head_row'] = [PB5[n][1] for n in range(5)]
G[u'blk_tail_row'] = [PB5[n][2] for n in range(5)]
G[u'blk_head_gap'] = [G[u'blk_head_row'][n] - G[u'ans_anchor_line'][n] for n in range(5)]

# ---------- 模板长行池: 归属向量走 Counter 直方图, 共用数走“按键域扫一遍” ----------
def pool5(i, lim):
    return set([f5(x) for n, x in ROWS5[i] if len(f5(x)) >= lim])


PAIRS5 = list(IT.combinations(range(NSRC), 2))
TRIPS5 = list(IT.combinations(range(NSRC), 3))
QUADS5 = list(IT.combinations(range(NSRC), 4))
POOL5 = [pool5(i, 40) for i in range(NSRC)]
POOL25_5 = [pool5(i, 25) for i in range(NSRC)]


def mask5(pools):
    M = {}
    for i, s in enumerate(pools):
        for k in s:
            M.setdefault(k, []).append(i)
    return M


MASK5, MASK25_5 = mask5(POOL5), mask5(POOL25_5)
UNION5, UNION25_5 = sorted(MASK5), sorted(MASK25_5)
G[u'pool_n'] = [len(x) for x in POOL5]
G[u'pool_sum'] = sum(G[u'pool_n'])
G[u'pool_union'] = len(MASK5)
G[u'pool_raw_rows'] = [len([x for n, x in ROWS5[i] if len(f5(x)) >= 40]) for i in range(NSRC)]
G[u'pool_dup'] = sum(G[u'pool_raw_rows']) - G[u'pool_sum']
G[u'pool_n25'] = [len(x) for x in POOL25_5]
G[u'pool_union25'] = len(MASK25_5)
G[u'pool_widen'] = G[u'pool_union25'] - G[u'pool_union']
HIST5 = Counter([len(v) for v in MASK5.values()])
G[u'pool_tier'] = [HIST5.get(m, 0) for m in range(1, NSRC + 1)]
G[u'pool_pair'] = dict((u'%s-%s' % (LBL[a], LBL[b]), len([k for k in UNION5 if a in MASK5[k] and b in MASK5[k]]))
                       for a, b in PAIRS5)
G[u'pool_trip'] = dict((u'%s-%s-%s' % (LBL[a], LBL[b], LBL[c]),
                        len([k for k in UNION5 if a in MASK5[k] and b in MASK5[k] and c in MASK5[k]]))
                       for a, b, c in TRIPS5)
G[u'pool_quad'] = dict((u'%s-%s-%s-%s' % (LBL[a], LBL[b], LBL[c], LBL[d]),
                        len([k for k in UNION5 if all(z in MASK5[k] for z in (a, b, c, d))]))
                       for a, b, c, d in QUADS5)
G[u'pool_pair_tot'] = sum(G[u'pool_pair'].values())
G[u'pool_trip_tot'] = sum(G[u'pool_trip'].values())
G[u'pool_quad_tot'] = sum(G[u'pool_quad'].values())
G[u'pool_ie_close'] = G[u'pool_sum'] - G[u'pool_pair_tot'] + G[u'pool_trip_tot'] - G[u'pool_quad_tot'] \
    - G[u'pool_union']
RFCSET5 = set(LBL[i] for i in RFCI)
PAPSET5 = set(LBL[i] for i in PAPI)
RFCPAIR = sorted([k for k in G[u'pool_pair'] if all(z in RFCSET5 for z in k.split(u'-'))])
PAPAIR = sorted([k for k in G[u'pool_pair'] if any(z in PAPSET5 for z in k.split(u'-'))])
G[u'pool_pair_by'] = [G[u'pool_pair'][u'%s-%s' % (LBL[a], LBL[b])] for a, b in PAIRS5]
G[u'pool_pair_rfc_keys'] = RFCPAIR
G[u'pool_pair_rfc'] = sum(G[u'pool_pair'][k] for k in RFCPAIR)
G[u'pool_pair_paper'] = sum(G[u'pool_pair'][k] for k in PAPAIR)
G[u'pool_pair_paper_n'] = len([k for k in PAPAIR if G[u'pool_pair'][k] == 0])
G[u'pool_max_pair'] = max(G[u'pool_pair'].values())
G[u'pool_min_pair_rfc'] = min(G[u'pool_pair'][k] for k in RFCPAIR)
G[u'pool_tier_close'] = sum(G[u'pool_tier']) - G[u'pool_union']
G[u'pool_sum_close'] = sum(G[u'pool_tier'][m] * (m + 1) for m in range(NSRC)) - G[u'pool_sum']
SHARED5 = set()
for k in RFCPAIR:
    a, b = [LBL.index(z) for z in k.split(u'-')]
    SHARED5 |= (POOL5[a] & POOL5[b])
G[u'pool_shared_rfc'] = len(SHARED5)
G[u'pool_shared_toned'] = len([x for x in SHARED5 if TONED5(x)])
G[u'pool_shared_rfcline'] = len([x for x in SHARED5 if c5(x, u'RFC') > 0])
G[u'pool_shared_status'] = len([x for x in SHARED5 if c5(x.lower(), u'status of this document') > 0])
G[u'pool_paper_in_toned'] = sum(len([x for x in POOL5[i] if TONED5(x)]) for i in PAPI)
G[u'pool_rfc_in_toned'] = sum(len([x for x in POOL5[i] if TONED5(x)]) for i in RFCI)

# ---------- 转置尺: 族量按“这一式在五份里各读几枚”横过来逐份读 ----------
G[u'unit_docs'] = [[G[u'unit'][i][k] for i in range(NSRC)] for k in range(len(UNIT))]
G[u'unit_word_docs'] = [[G[u'unit_word'][i][k] for i in range(NSRC)] for k in range(len(UNIT))]
G[u'spell_docs'] = [[G[u'spell'][i][k] for i in range(NSRC)] for k in range(len(SPELL))]
G[u'term_docs'] = [[G[u'term'][i][k] for i in range(NSRC)] for k in range(len(TERM))]
G[u'tone_docs'] = [[G[u'tone_sh'][i][k] for i in range(NSRC)] for k in range(5)]
G[u'num_docs'] = [[G[u'num'][i][k] for i in range(NSRC)] for k in range(len(NUM))]
G[u'num_cold'] = [NUM[k] for k in range(len(NUM)) if sum(G[u'num_docs'][k]) == 0]
G[u'num_cold_n'] = len(G[u'num_cold'])
G[u'num_hot_n'] = len(NUM) - G[u'num_cold_n']
G[u'num_own_tot'] = sum(len(x) for x in G[u'num_own'])
G[u'cfg_own_tot'] = sum(len(x) for x in G[u'cfg_own'])
G[u'term_own_tot'] = sum(len(x) for x in G[u'term_own'])
G[u'spell_tot'] = [sum(x) for x in G[u'spell_docs']]
G[u'term_tot'] = [sum(x) for x in G[u'term_docs']]
G[u'unit_tot'] = [sum(x) for x in G[u'unit_docs']]
G[u'role_by_face'] = [[sum(G[u'role_line'][i]) if k == 0 else sum(G[u'role_fold'][i]) if k == 1
                       else sum(G[u'role_sh'][i]) if k == 2 else sum(G[u'role_lig'][i])
                       for i in range(NSRC)] for k in range(4)]
G[u'face_tot'] = [sum(G[u'role_by_face'][k]) for k in range(4)]
G[u'face_gain'] = [G[u'face_tot'][k] - G[u'face_tot'][k - 1] for k in range(1, 4)]
G[u'face_mono'] = sum([1 for k in range(1, 4) if G[u'face_tot'][k] >= G[u'face_tot'][k - 1]])
G[u'gain_fold'] = [G[u'role_fold'][i][k] - G[u'role_line'][i][k]
                   for i in range(NSRC) for k in range(len(ROLEN))]
G[u'gain_sh'] = [G[u'role_sh'][i][k] - G[u'role_fold'][i][k]
                 for i in range(NSRC) for k in range(len(ROLEN))]
G[u'gain_lig'] = [G[u'role_lig'][i][k] - G[u'role_sh'][i][k]
                  for i in range(NSRC) for k in range(len(ROLEN))]
G[u'gain_fold_tot'] = sum(G[u'gain_fold'])
G[u'gain_sh_tot'] = sum(G[u'gain_sh'])
G[u'gain_lig_tot'] = sum(G[u'gain_lig'])
G[u'gain_fold_key'] = len([x for x in G[u'gain_fold'] if x > 0])
G[u'gain_sh_key'] = len([x for x in G[u'gain_sh'] if x > 0])
G[u'gain_fold_dup'] = sum([G[u'role_fold'][i][k] - G[u'role_line'][i][k] for i in range(NSRC)
                           for k in range(len(ROLEN)) if G[u'role_line'][i][k] > 0])
G[u'gain_sh_dup'] = sum([G[u'role_sh'][i][k] - G[u'role_fold'][i][k] for i in range(NSRC)
                         for k in range(len(ROLEN)) if G[u'role_fold'][i][k] > 0])
G[u'ans_words_tot'] = sum(G[u'ans_words'])
G[u'sec_lines_tot'] = sum(G[u'sec_lines'])
G[u'sec_chars_tot'] = sum(G[u'sec_chars'])
G[u'sec_tone_tot_all'] = sum(G[u'sec_tone_tot'])


def tone_straddle_pair5(i, nd):
    w = nd.split(u' ')
    return [(FD5[i][m][0], FD5[i][m + 1][0]) for m in range(len(FD5[i]) - 1)
            if FD5[i][m][2].endswith(w[0]) and FD5[i][m + 1][2].startswith(u' '.join(w[1:]))]


TSK5 = [k for k in range(5) if G[u'tone_straddle_k'][4][k]]
G[u'tone_straddle_nd'] = [TONE[k] for k in TSK5]
TSP5 = []
for kk in TSK5:
    TSP5.extend(tone_straddle_pair5(4, TONE[kk]))
G[u'tone_straddle_lines'] = [list(x) for x in TSP5]
G[u'tone_straddle_n'] = len(TSP5)
G[u'tone_straddle_adj'] = len([x for x in TSP5 if x[1] - x[0] == 1])
G[u'tone_straddle_shell'] = G[u'tone_straddle_n'] - G[u'tone_straddle_adj']
G[u'tone_straddle_ledger'] = G[u'tone_straddle'][4] - G[u'tone_straddle_n']
assert G[u'tone_straddle_n'] >= 1 and G[u'tone_straddle_ledger'] == 0

# ---------- 第五段: 与采集遍逐键对账(键名表由 ast 从 _mkB81.py 摘, 一条不重打) ----------
NUMK = []
for _nd in ast.parse(MS).body:
    if isinstance(_nd, ast.Assign) and getattr(_nd.targets[0], u'id', u'') == u'NUMK':
        NUMK = [x.value for x in _nd.value.elts]
assert len(SAMEK) == 112 and len(NUMK) == 3, (len(SAMEK), len(NUMK))

# 第二遍按“逐元素 + 元组⇎列表两种序列化”对拍, 本遍换成整值过一遍 JSON 通道再比
_jr = lambda x: json.loads(json.dumps(x))
AGREE, DIFFK = [], []
for kk in SAMEK + NUMK:
    if kk not in G or kk not in MEA:
        DIFFK.append((kk, u'缺键'))
        continue
    if _jr(G[kk]) == _jr(MEA[kk]):
        AGREE.append(kk)
    else:
        DIFFK.append((kk, u'值不符'))
G[u'ans_vs_pick'] = [1 if G[u'ans'][i] == MEA[u'ans'][i] else 0 for i in range(NSRC)]
G[u'ans_tail_ws'] = [len(MEA[u'ans'][i]) - len(G[u'ans'][i]) for i in range(NSRC)]
G[u'pick_agree'] = len(AGREE)
G[u'pick_diff'] = len(DIFFK)
G[u'pick_diff_keys'] = [x[0] for x in DIFFK]
G[u'pick_same_n'] = len(SAMEK) + len(NUMK)
assert not DIFFK, DIFFK[:4]
assert G[u'pick_agree'] == G[u'pick_same_n'] == 115
assert G[u'ans_vs_pick'] == [1] * NSRC and G[u'ans_tail_ws'] == [0] * NSRC

# ---------- 编码区锚账: 手写配对扫描 ⇎ 双轨归属 ----------
TT = io.open(ENTRY, encoding='utf-8').read()
_i0 = TT.index(u'## ⟪BabelTele⟫')
ENC = TT[TT.index(NL, _i0) + 1:TT.index(u'## ⛓解读注')].rstrip(NL)


def my_cites(s):
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
for _, a in CITES:
    if a not in ANCHS:
        ANCHS.append(a)
DIST = len(ANCHS)
TAGN = dict((t, len([x for x in CITES if x[0] == t])) for t in TAGS)
ERR = [x for x in CITES if p5(x[1]) not in FAN5[IDX[x[0]]]]
MISSLINE = [x for x in CITES
            if x[1] not in ANSET5[IDX[x[0]]] and p5(x[1]) not in ROWSRAW5[IDX[x[0]]]]
assert not ERR, ERR[:2]
assert not MISSLINE, MISSLINE[:2]
HITC = dict((a, tuple(i for i in range(NSRC) if p5(a) in FAN5[i])) for a in ANCHS)
G[u'anchor_total'] = USED
G[u'anchor_distinct'] = DIST
G[u'anchor_err'] = len(ERR)
G[u'anchor_single'] = len([a for a in ANCHS if len(HITC[a]) == 1])
G[u'anchor_cross'] = len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC])
G[u'anchor_all5'] = len([a for a in ANCHS if len(HITC[a]) == NSRC])
G[u'checks'] = DIST * NSRC
G[u'enc_chars'] = len([c for c in ENC if c != NL])
G[u'nsrc'] = NSRC
for t in TAGS:
    G[u'tag_' + t] = TAGN[t]
assert G[u'anchor_single'] + G[u'anchor_cross'] + G[u'anchor_all5'] == DIST
assert G[u'anchor_all5'] <= 1

# 锚的行号⇎候选数逐枚回读: 记录来自第二遍的 ALOG, 本遍用自己的行号尺认一遍
# 跨行锚在日志里是“针串[首]/[末]”两枚, 整串在任何单行都读不通, 故用两半尺验:
# 针串本身不记在日志里(只记前 34 字符), 本遍从字面表 ⇎ 段界表里按前缀找回整串, 再要求两半行号与日志同值
FULLS = [x[1] for x in CH[u'split']] + list(ROLEN) + list(TONE) + [c for _, c in CITES]
ALC = Counter([x[0] for x in CH[u'anchor_lines']])
assert sum(ALC.values()) == G[u'anchor_total'] == len(CH[u'anchor_lines'])
MARK = {}
for lbl, nd, ln, nh in CH[u'anchor_lines']:
    if nd.endswith(u'[首]'):
        MARK.setdefault((lbl, nd[:-3]), [0, 0])[0] = ln
    elif nd.endswith(u'[末]'):
        MARK.setdefault((lbl, nd[:-3]), [0, 0])[1] = ln
_back = 0
for (lbl, key), (lh, lt) in sorted(MARK.items()):
    assert lh and lt, (lbl, key)
    i = IDX[lbl]
    got = None
    for mode in (False, True):
        for f in FULLS:
            if not p5(f).startswith(p5(key)):
                continue
            try:
                h, t, head, tail = split_pieces5(i, f, mode)
            except Exception:
                continue
            if (h, t) == (lh, lt):
                got = (f, mode, head, tail)
                break
        if got:
            break
    assert got, (lbl, key, lh, lt)
    f, mode, head, tail = got
    rh = [y for y in FD5[i] if y[0] == lh][0][1]
    rt = [y for y in FD5[i] if y[0] == lt][0][1]
    assert head in rh and p5(tail) in p5(rt), (lbl, key)
    _back += 2
for lbl, nd, ln, nh in CH[u'anchor_lines']:
    if nd.endswith(u'[首]') or nd.endswith(u'[末]'):
        continue
    hits = an5(IDX[lbl], nd, False, 0)
    assert ln in [x[0] for x in hits], (lbl, nd, ln)
    _back += 1
assert _back == G[u'anchor_total'] == len(CH[u'anchor_lines'])
assert CH[u'anchor_ambiguous'] == len([x for x in CH[u'anchor_lines'] if x[3] > 1])

# ---------- 布尔门: 28 + 16 道的右式一律由源码 ast 摘出, 在本遍读数上重 eval ----------
MSA = ast.parse(MS)
CLOSE_SRC = []
for _nd in MSA.body:
    if isinstance(_nd, ast.Assign) and isinstance(_nd.targets[0], ast.Subscript):
        _t = _nd.targets[0]
        if isinstance(_t.value, ast.Name) and _t.value.id == u'CLOSE' \
                and isinstance(_t.slice, ast.Constant) and isinstance(_t.slice.value, type(u'')):
            CLOSE_SRC.append((_t.slice.value, ast.get_source_segment(MS, _nd.value)))
assert len(CLOSE_SRC) == 28 and len(set(k for k, _ in CLOSE_SRC)) == 28, len(CLOSE_SRC)

ENV = {u'F': G, u'G': G, u'NSRC': NSRC, u'NUM': NUM, u'RFCI': RFCI, u'PAPI': PAPI,
       u'sum': sum, u'len': len, u'all': all, u'any': any, u'max': max, u'min': min,
       u'range': range, u're': re, u'sorted': sorted, u'tuple': tuple, u'set': set,
       u'str': str, u'abs': abs, u'float': float, u'int': int, u'list': list}
CLOSEV = {}
for _k, _e in CLOSE_SRC:
    CLOSEV[_k] = 1 if eval(_e, ENV, ENV) else 0
G[u'bool_clos_n'] = len(CLOSE_SRC)
G[u'bool_clos_sum'] = sum(CLOSEV.values())
assert G[u'bool_clos_sum'] == G[u'bool_clos_n'], [k for k, v in CLOSEV.items() if not v]

EMA = ast.parse(EM)
CLOSE2_SRC = []
for _nd in EMA.body:
    if isinstance(_nd, ast.Assign) and isinstance(_nd.targets[0], ast.Subscript):
        _t = _nd.targets[0]
        if isinstance(_t.value, ast.Name) and _t.value.id == u'CLOSE2' \
                and isinstance(_t.slice, ast.Constant) and isinstance(_t.slice.value, type(u'')):
            CLOSE2_SRC.append((_t.slice.value, ast.get_source_segment(EM, _nd.value)))
assert len(CLOSE2_SRC) == 16, len(CLOSE2_SRC)
ENV[u'RFCPAIR'] = RFCPAIR
ENV[u'PAPAIR'] = PAPAIR
ENV[u'TONED'] = TONED5
for _k, _e in CLOSE2_SRC:
    G[_k] = 1 if eval(_e, ENV, ENV) else 0
G[u'bool_clos2_n'] = len(CLOSE2_SRC)
G[u'bool_clos2_sum'] = sum(G[_k] for _k, _ in CLOSE2_SRC)
G[u'bool_all_n'] = G[u'bool_clos_n'] + G[u'bool_clos2_n']
G[u'bool_all_sum'] = G[u'bool_clos_sum'] + G[u'bool_clos2_sum']
assert G[u'bool_clos2_sum'] == 16, [_k for _k, _ in CLOSE2_SRC if not G[_k]]

# ---------- 恒等式: 建条侧 34 条标量式 ⇎ 摘壳侧 30 条 V 形式, 右式同样从源码摘 ----------
ZSRC = []
for _nd in MSA.body:
    if isinstance(_nd, ast.Expr) and isinstance(_nd.value, ast.Call) \
            and isinstance(_nd.value.func, ast.Name) and _nd.value.func.id == u'Z':
        ZSRC.append((_nd.value.args[0].value, _nd.value.args[1].value))
assert len(ZSRC) == 34, len(ZSRC)
ZFAIL = [w for e, w in ZSRC if eval(e, ENV, ENV) != 0]
G[u'zid_scan_n'] = len(ZSRC)
assert not ZFAIL, ZFAIL[:3]

ZEXP_SRC = []
for _nd in EMA.body:
    if isinstance(_nd, ast.Expr) and isinstance(_nd.value, ast.Call) \
            and isinstance(_nd.value.func, ast.Name) and _nd.value.func.id == u'ZEXP':
        ZEXP_SRC.append((_nd.value.args[0].value, _nd.value.args[1].value))
assert len(ZEXP_SRC) == 30, len(ZEXP_SRC)
G[u'zid_scan2_n'] = len(ZEXP_SRC)

# ---------- V 形恒等式 ⇎ DERIV 复算点: 只走查表通道 ----------
NSV = dict(G)
B81V5 = lambda k, i=None: (NSV[k] if i is None else NSV[k][i])
ENVV = {u'B81V': B81V5, u'sum': sum, u'len': len, u'max': max, u'min': min, u'abs': abs,
         u'sorted': sorted, u'tuple': tuple, u'set': set, u'round': round, u'str': str,
         u'float': float, u'int': int, u'range': range, u'all': all, u'any': any}
ZVFAIL = [w for e, w in CH[u'zid'] if eval(e, ENVV, ENVV) != 0]
assert not ZVFAIL, ZVFAIL[:3]
assert len(CH[u'zid']) == G[u'zid_scan_n'] + G[u'zid_scan2_n'] == 64
ZF2 = [w for e, w in ZEXP_SRC if eval(e, ENVV, ENVV) != 0]
assert not ZF2, ZF2[:3]

DFL = []
DCITE = 0
for _kk in sorted(DER, key=lambda x: (len(x), x)):
    _v = DER[_kk]
    DCITE += _v.count(u"B81V(")
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
BAD = [(k, _jr(G[k]), _jr(FLAT[k])) for k in G if k in FLAT and _jr(G[k]) != _jr(FLAT[k])]
UNCOVER = [k for k in FLAT if k not in G and k != u'contract_n']
assert not MISS, MISS[:6]
assert not UNCOVER, UNCOVER[:6]
assert not BAD, BAD[:6]
G[u'contract_n'] = len(G) + 1
assert G[u'contract_n'] == len(FLAT) == 411
print(u"第五段完成: 采集对账 %d/%d ⇎ 编码区 %d 字符 ⇎ 锚 %d 处/去重 %d 串/复核 %d ⇎ "
      u"布尔门 %d+%d 全绿 ⇎ 标量式 %d ⇎ V 形 %d 条归零 ⇎ DERIV %d 键/%d 处引用 ⇎ 扁平 %d 键全覆盖" % (
          G[u'pick_agree'], G[u'pick_same_n'], G[u'enc_chars'], G[u'anchor_total'], DIST, _back,
          G[u'bool_clos_sum'], G[u'bool_clos2_sum'], G[u'zid_scan_n'], len(CH[u'zid']),
          len(DER), DCITE, len(FLAT)))

# ---------- ⛓解读注 ----------
J = lambda xs: u' ⇎ '.join(u'%s' % x for x in xs)


def QT(tag, s):
    assert p5(s) in FAN5[IDX[tag]], u'本遍锚平面读不到: ' + s[:50]
    return u'⟦%s⟧⟨%s⟩' % (tag, s)


def cell(c):
    assert u'|' not in c, c[:70]
    assert c.count(u'`') % 2 == 0, c[:70]
    return c


def NJ(xs):
    return u' ⇎ '.join(u'%s' % x for x in xs if x is not None)


# 切开判词的两半由本遍的 split_pieces5 现取(整串在首行读不通, 两半各回自己那一行读得通)
SPLIT5 = []
for _n, (_lb, _k) in enumerate(zip(G[u'split_lbl'], G[u'split_k'])):
    _h, _t, _hd, _tl = split_pieces5(IDX[_lb], ROLEN[_k])
    assert (_h, _t) == (G[u'split_head'][_n], G[u'split_tail'][_n])
    assert len(_hd) == G[u'split_head_chars'][_n] and len(_tl) == G[u'split_tail_chars'][_n]
    SPLIT5.append((_lb, _h, _t, _hd, _tl))

L2 = []
A = L2.append
A5 = [a for a in ANCHS if len(HITC[a]) == NSRC]
A2 = [a for a in ANCHS if 1 < len(HITC[a]) < NSRC]
assert len(A5) == G[u'anchor_all5'] and len(A2) == G[u'anchor_cross']
MI = G[u'neg_fam'].index(u'ms')
A5S = A5[0] if A5 else u'无'
A2LONG = max(A2, key=len)
A2SHORT = min(A2, key=len)
A(u"第五遍(`corpus/_fill81.py`)换算法不换定义地把前四遍的量重跑一遍, 本遍的独立处有十二项: ①行界由手写索引循环按 `\\n` 切"
  u"(第二遍是 `str.split`), 换行枚数走 `str.count`, 码位数逐字符累加(第二遍是 `len`), 字节数走 `os.stat` 的文件系统元数据"
  u"(第二遍是读进来的缓冲区长度)——两条通道给出同一个数才算复核; ②折平走 `re.sub('\\s+',' ')` 加 `str.translate(拆字表)` 两档"
  u"(第二遍是 `re.split` 过滤空段 ⇎ 逐字符查表重建), 归一尺 `p5` 与第二遍的 `pnorm` 逐份对拍; ③针计数起三档 `str.count`(非重叠) ⇎"
  u" `finditer('(?=针)')`(重叠) ⇎ 第二遍的 `findall(re.escape)`, 逐行档把行循环换成累加器; ④整词尺用前瞻定位后取左右邻字符判"
  u" alpha/digit/alnum(第二遍是游标 find 加手扫), 另起一条断言正则档与它逐枚对拍; ⑤壳谓词第三档——`strip()` 后无参 `split()` 切"
  u" token 逐段比首尾(第二遍是折平再按一枚空格切), 页码尺换成 `re.fullmatch` 加数字段计数; ⑥数值抽取用一条“负向后视 ⇎ 数字段 ⇎"
  u" 至多一枚空格 ⇎ 单位选支按长度降序 ⇎ 负向前瞻字母”的正则, 与第二遍的手工扫数字串两轨逐份对拍; ⑦标题分档走一条"
  u" `^( *)([0-9.]+)( )` 正则取缩进与点段再数段数(第二遍是逐字符吃档), 论文面节题借采集侧的 `^\\s*([IVX]+)\\.\\s+[A-Z]`——"
  u" 两把都跑再对拍; ⑧句界走 `\\.(?=[ \\t\\n]+[A-Z(“\"])` 一条 finditer 代逐字符扫; ⑨偏移→行号走 `bisect_right`(第二遍是线性"
  u" 扫到尾), 逐字符对照表由 `re.finditer('\\S+')` 加 `translate` 的展开长度同时构造; ⑩段池归属向量走 `Counter` 直方图 ⇎ 容斥与"
  u" 两两三三四四共用走“对文档下标的组合逐枚数共现”(第二遍是集合 `&`); ⑪词窗尺走 `zip(*[tokens[i:] for i in range(n)])` 的转置档"
  u" 代切片逐枚全等; ⑫定义复用而量不复用——`SPELL ⇎ TERM ⇎ UNIT ⇎ NUM ⇎ ROLE ⇎ NEG ⇎ PAR ⇎ CFG ⇎ TONE ⇎ VOICE ⇎ CIT ⇎ WIN ⇎ PINS ⇎"
  u" SAMEK ⇎ LIGMAP` 从两遍源码 `ast` 摘, 谓词函数 `exec` 进来只用于对拍; 28+16 道布尔门的右式 ⇎ 34+30 条恒等式的表达式也从源码"
  u" `ast` 摘, %d 条 V 形 ⇎ %d 键 DERIV 从 `_b81checks.json` ⇎ `_deriv81.json` 回读 eval。 全部五份面共 %s 行 ⇎ %s 字符 ⇎ 套版长行池"
  u" %d 枚在这一套算法下重跑。" % (len(CH[u'zid']), len(DER), format(sum(G['lines']), u','),
                                   format(sum(G['chars']), u','), G[u'pool_union']))
A(u"本遍复算 %d 个键(扁平表 %d 键全覆盖 ⇎ 本遍独有 %d ⇎ 未复算 %d ⇎ 逐值不符 %d); 布尔门 %d 道(建条目侧 %d ⇎ 段落侧 %d)在本遍现算"
  u" 读数上全绿; 恒等式 %d+%d=%d 条归零(标量轨在第二遍源码上 eval ⇎ V 形轨查 `%s` 表), `checks` 里登记的 V 形 %d 条全真; DERIV %d 键"
  u" ⇎ %d 处引用重跑全对; 与采集遍逐键横比 %d/%d 键相符 ⇎ %d 键不符 ⇎ 五句答话两轨(本遍逐字符句界 ⇎ 采集侧前瞻正则)逐份同串 %s ⇎"
  u" 尾随空白 %s 字符; 编码区 %d 非换行字符里 %d 处 `⟦…⟧⟨…⟩` 引文锚全部由本遍手写配对扫描取出并与断言正则档逐枚同序, 去重 %d 串"
  u" ⇎ 面内读不到 %d 枚 ⇎ 行号回读复核 %d 枚(其中 %d 枚走切开两半尺) ⇎ 判定 %d 项门槛全绿。" % (
      len(G) - 1, len(FLAT), len(MISS), len(UNCOVER), len(BAD),
      G[u'bool_all_sum'], G[u'bool_clos_sum'], G[u'bool_clos2_sum'],
      G[u'zid_scan_n'], G[u'zid_scan2_n'], G[u'zid_scan_n'] + G[u'zid_scan2_n'], u'B81V',
      len(CH[u'zid']), len(DER), DCITE,
      G[u'pick_agree'], G[u'pick_same_n'], G[u'pick_diff'], J(G[u'ans_vs_pick']), J(G[u'ans_tail_ws']),
      G[u'enc_chars'], G[u'anchor_total'], G[u'anchor_distinct'], G[u'anchor_err'], _back, G[u'split_n'],
      G[u'contract_n']))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"版式⇎行界⇎字节",
     u"字节走 `os.stat`(第二遍读缓冲区) ⇎ 码位逐字符累加 ⇎ 行界手写 `\\n` 索引循环 ⇎ 换行枚 `str.count`",
     u"字节 %s ⇎ 面内码位 %s ⇎ 原行 %s ⇎ 换行枚 %s ⇎ 收尾换行 %s ⇎ 非空行 %s ⇎ 最长行 %s ⇎ 超 72 列 %s" % (
         J(G['bytes']), J(G['chars']), J(G['lines']), J(G['newlines']), J(G['tail_nl']),
         J(G['nonblank']), J(G['maxlen']), J(G['over72'])),
     u"回车 %s ⇎ 论文面“行枚=回车枚+1”判定 %s ⇎ 硬换行溢出按族 %s ⇎ 字节−码位差 %s 与 utf-8 多字节 %s 两份账逐份同值 %s ⇎"
     u" BOM %s ⇎ NUL %s——三份规范面逐枚纯 ASCII ⇎ 两份论文一行为一段(madp %d 列 ⇎ cake %d 列)。" % (
         J(G['cr']), J(G['crlf_rows']), J(G['wrap_family']), J(G['byte_cp_delta']), J(G['utf8_extra']),
         J(G['byte_cp_ledger']), J(G['bom']), J(G['nul']), G['maxlen'][1], G['maxlen'][3])),
    (u"页壳⇎页码三把尺",
     u"壳谓词第三档: `strip()` 后无参 `split()` 切 token 逐段比首尾(第二遍折平再按一枚空格切, 采集侧三条整序正则); 页码尺走"
     u" `re.fullmatch` 加数字段计数",
     u"壳行 %s ⇎ 空壳 %s ⇎ 非空壳 %s ⇎ 剥壳正文行 %s ⇎ 页码行 %s ⇎ 眉行 %s ⇎ 换页符 %s ⇎ 独占一行 %s ⇎ 行内混排 %s" % (
         J(G['shell_lines']), J(G['blank']), J(G['shell_nonblank']), J(G['pp_rows']), J(G['pg_lines']),
         J(G['hdr_lines_tight']), J(G['ff']), J(G['ff_exact']), J(G['ff_inline'])),
     u"两遍逐行同集分歧 %d 行 ⇎ 壳三本账 %s ⇎ 折平吃掉换页 %s ⇎ 只由换页组成的行 %s ⇎ 缺口=非空壳判定 %d(账 %d); naive 页码尺"
     u" %s 枚里真页码 %s 枚 ⇎ 多吃 %s 枚表格行 ⇎ 放宽到数字成两段的再多吃 %s 枚(两尺差 %s ⇎ 全形状档 %s)。" % (
         G['shell_pred_diff'], J(G['shell_ledger']), J(G['shell_fold_eats_ff']), J(G['shell_blank_only']),
         G['pp_gap_is_shell_nonblank'], G['pp_gap_close'], J(G['pgnum_naive']), J(G['pgnum_ffled']),
         J(G['pgnum_overstrip']), J(G['pgnum_multirun']), J(G['pgnum_ruler_gap']),
         J(G['pgnum_anyshape']))),
    (u"非ASCII⇎连字⇎四档面字符账",
     u"拆字走 `str.translate`(第二遍逐字符查表重建), 连字对按 `LIGMAP` 逐型数 ⇎ 四档面各由不同构造路径独立拼出",
     u"非 ASCII %s ⇎ 希腊 %s ⇎ 弯引与破折 %s ⇎ 其余 %s ⇎ fi/ﬂ %s ⇎ 连字合计 %s ⇎ 全篇折平 %s ⇎ 摘壳 %s ⇎ 摘壳加拆字 %s" % (
         J(G['na_total']), J(G['na_greek']), J(G['na_dashq']), J(G['na_other']), J(G['lig_pair']),
         J(G['lig_total']), J(G['fold_chars']), J(G['sh_chars']), J(G['shlig_chars'])),
     u"四桶账 %s ⇎ 拆字加回字符 %s 与连字枚数逐份同值 %s ⇎ 摘壳少读 %s ⇎ 壳内文本 %s(三档字符账 %d) ⇎ 三份规范面 %s 枚——非 ASCII 一枚也不"
     u"在规范面上, 拆字只在两份论文面改形。" % (
         J(G['na_ledger']), J(G['lig_char_add']), J(G['lig_add_close']), J(G['sh_minus_fold']),
         J(G['shell_text_chars']),
         sum(abs(G['fold_chars'][i] - G['sh_chars'][i] - G['shell_text_chars'][i]) for i in range(NSRC)),
         J([G['na_total'][i] for i in RFCI]))),
    (u"判词针族 27 枚⇎四档口径",
     u"四档面各自独立构造(逐行累加 ⇎ `re.sub` 折平 ⇎ 剥壳 ⇎ 剥壳加 translate), 计数三档并立; 增益按“枚”记账而非按“针”",
     u"四档命中 %s 次 ⇎ 增益 %s ⇎ 单调判定 %d ⇎ 逐行读通 %d 枚 ⇎ 读不通 %d 枚 ⇎ 硬换行切开 %s ⇎ 目录重印 %s ⇎ 壳切 %s ⇎ 拆字新增 %s" % (
         J(G['face_tot']), J(G['face_gain']), G['face_mono'], G['role_line_read_n'], G['role_line_miss_n'],
         J(G['role_wrap_n']), J(G['role_dup_n']), J(G['role_shell_gain']), J(G['role_lig_gain'])),
     u"折平档净增 %d 枚 = 切开 %d 枚 + 目录重印新添 %d 枚(涉及针 %d 枚) ⇎ 摘壳档净增 %d(壳切 %d ⇎ 涉及针 %d) ⇎ 拆字档 %d ⇎ 三档重叠账 %d"
     u" ⇎ 按枚比按针多 %d 枚 ⇎ 壳切的两枚针 %s ⇎ 只属一家的针 %s ⇎ 多枚针 %s。" % (
         G['gain_fold_tot'], G['split_wrap_n'], G['gain_fold_dup'], G['gain_fold_key'],
         G['gain_sh_tot'], G['split_shell_n'], G['gain_sh_key'],
         G['gain_lig_tot'], G['role_ovl_close'], G['gain_fold_tot'] + G['gain_sh_tot'] - G['split_n'],
         J(G['role_shell_needles']),
         J([len(x) for x in G['role_own']]), J([len(x) for x in G['role_multi']]))),
    (u"切开八枚⇎两半⇎行号往返",
     u"两半由偏移经 `bisect_right` 映回原行再按逐字符对照表切(第二遍线性扫+手工跳空白); 行号往返拿面自验",
     u"切开 %d 枚(针号 %s) ⇎ 首行 %s ⇎ 末行 %s ⇎ 两半字数 %s ⇎ %s ⇎ 跨行幅度 %s(合计 %d 行) ⇎ 两半字符合计 %d" % (
         G['split_n'], J(G['split_k']), J(G['split_head']), J(G['split_tail']),
         J(G['split_head_chars']), J(G['split_tail_chars']), J(G['split_span']),
         G['split_span_tot'], G['split_rows_tot']),
     u"两半各回本行可读判定 %d/8 ⇎ 整串完全落在首行的枚数 %d(反向对照门 %d = “0 枚 ⇎ 两半全通”这条判据成立) ⇎ 壳切两枚之间确夹非空壳行 %s ⇎ 幅度账 %d(闭合 %d) ⇎ 切开 %d 枚"
     u" 硬换行+%d 枚壳切 ⇎ 跨行幅度与枚数之差登记 %d; 段窗 %d 枚针回读命中 %d(首侧 %d ⇎ 末侧 %d ⇎ 整针落一行 %d ⇎ 被推到邻行 %d)。" % (
         G['split_half_ok'], G['split_full_on_head'], G['split_reverse_cold'], J(G['split_shell_between']),
         G['split_ledger'], G['split_ledger_close'], G['split_wrap_n'], G['split_shell_n'],
         G['split_span_vs_miss'], G['seg_rt_n'], G['seg_rt_ok'], G['seg_rt_head'], G['seg_rt_tail'],
         G['seg_rt_whole'], G['seg_rt_cut'])),
    (u"拼写⇎术语⇎RTT 三把尺",
     u"整词尺走前瞻+邻字符判定, 子串尺走 `str.count`, 词窗尺走转置档 ⇎ 三轨在同一张拆字面上跑",
     u"queuing/queueing 两拼 %s ⇎ 多数拼 %s ⇎ 少数拼 %s ⇎ 只读到一向 %d 份 ⇎ 短语式 %s ⇎ 两式并存 %s ⇎ 尺间差 %s" % (
         J(G['spell']), J(G['spell_major']), J(G['spell_minor']), G['spell_one_n'],
         J(G['spell_phrase_sum']), J(G['spell_phrase_two']), J(G['spell_ruler_gap'])),
     u"delay⇎latency 偏斜 %s(少数侧最小 %d 枚, 无一为零) ⇎ 独有术语 %s ⇎ sojourn 只在 8289(%d 枚 ⇎ 其余 %d) ⇎ 尺间差 %s ⇎ RTT 紧 %s"
     u" ⇎ 字距拉开 %s ⇎ 裸子串 %s(假命中 %s: %s)。" % (
         J(G['term_skew']), min(G['term_minor']), J(G['term_own']), G['term'][4][7],
         sum(G['term'][i][7] for i in range(4)), J(G['term_ruler_gap']), J(G['rtt_tight']),
         J(G['rtt_kern']), J(G['rtt_loose']), J(G['rtt_loose_false']),
         u' '.join(u'%s=%s' % (LBL[i], u','.join(G['rtt_false_words'][i]) or u'无')
                   for i in range(NSRC)))),
    (u"单位⇎数值⇎100 ms 六角色",
     u"数值抽取一条正则(负向后视 ⇎ 数字段 ⇎ 至多一枚空格 ⇎ 单位选支按长度降序 ⇎ 负向前瞻字母)代第二遍手工扫, 严宽两把尺各对拍一次",
     u"单位六式 %s ⇎ 整词尺 %s ⇎ 子串尺多读 %s ⇎ 数值十七式总量 %s ⇎ 去重后 %s 项 ⇎ 各家独有 %s(共 %d 式) ⇎ 全冷式 %s" % (
         J(G['unit']), J(G['unit_word']), J(G['unit_sub_over']), J(G['num_tot']), J(G['numval_n']),
         J(G['num_own']), G['num_own_tot'], J(G['num_cold'])),
     u"7567 %d 项带单位时长(十七式全零 %s) ⇎ 8033 缩写 ms 整词 %d 枚而全称 %d/%d/%d/%d 枚 ⇎ 宽尺多 %s 项 ⇎ 丢 %s 项 ⇎ 拆字前后数值账"
     u" %s ⇎ “100 ms”值 %s 枚 ⇎ 角色 %d 个: %s。" % (
         G['numval_n'][0], J(G['num'][0]), G['unit_word'][2][0], G['num'][2][10], G['num'][2][11],
         G['num'][2][12], G['num'][2][13], J([len(x) for x in G['numval_s_extra']]),
         J([len(x) for x in G['numval_s_lost']]),
         J(G['num_lig_gap']), J(G['ms100_count']), len(G['ms100_roles']),
         u' ⇎ '.join(u'%s“%s”' % (a, b) for a, b in G['ms100_roles']))),
    (u"反面针 19 枚⇎64 次探针",
     u"应冷处由本遍现算: 逐式在三档面上的命中各数一遍, 子串轨与整词轨差值单独落账",
     u"反面针 %d 枚 ⇎ 探针 %d 次 ⇎ 应冷处读到 %d 枚 ⇎ 有主针 %d/%d 枚 ⇎ 子串轨比整词轨多读 %d 枚" % (
         G['neg_n'], G['neg_probes'], G['neg_zero_hits'], G['neg_owner_present'], G['neg_n'],
         G['neg_sub_false']),
     u"多读 %d 枚集中在两式两份(%s)——全是词尾 `-ms` 的复数形被子串轨读进来: 7567 那 %d 枚住在 algorithms ⇎ mechanisms ⇎ systems ⇎ terms 一类词的"
     u"末尾, 8033 的 %d 枚住在 systems ⇎ modems ⇎ aims ⇎ streams 的末尾, 而整词尺在这两面上都读 0 ⇎ 应零清单 %s ⇎ “15 ms”这一式在 8033 定值却通篇只写全称, 缩写形五"
     u"份一枚也读不到: %s。" % (
         G['neg_sub_false'],
         u' ⇎ '.join(u'%s@%s=%d⇎%d' % (a, b, c, d) for a, b, c, d in G['neg_sub_false_rows']),
         G['neg_sub'][MI][0], G['neg_sub'][MI][2],
         J([len(x) for x in G['neg_zero_idx']]),
         QT(u'8033', u'defaulted to 15 milliseconds and 150 milliseconds for non-data-center'))),
    (u"参数名⇎免配置⇎拆字增益",
     u"族定义照抄 `PAR` ⇎ `CFG`(10 式), 计数换三档; 拆字增益单独按词记账",
     u"大写参数名 %s 式 ⇎ 希腊 %s 式 ⇎ 代码式 %s 式(%s) ⇎ 免配置族十式命中总量 %s ⇎ 各家独有 %s(共 %d 式)" % (
         J(G['par_upper_n']), J(G['par_greek_n']), J(G['par_impl_n']),
         u' '.join(u'%s=%d' % (a, b) for x in G['par_impl'] for a, b in x) or u'无',
         J(G['cfg_claim']), J(G['cfg_own']), G['cfg_own_tot']),
     u"cake 宣称族 %d 枚(一处也不写) ⇎ configuration 的拆字增益 %s 枚 ⇎ 拆字读数 %s ⇎ 受益词数 %s ⇎ 8289 附录里 %s ⇎ 小写 ms2time 按"
     u" `PAR` 尺(大小写敏感)在 8289 读 %d 枚 ⇎ 同一串在拆字小写面上按整词反面尺读 %s 枚——两把尺都要报, 判词用的是前者。" % (
         G['cfg_claim'][3], J(G['cfg_lig_gain']), J(G['cfg_lig_needle']), J(G['cfg_lig_words']),
         QT(u'8289', u'time_t TARGET = MS2TIME(5);     // 5 ms TARGET queue delay'),
         G['par'][4][10], J(G['neg_word'][17]))),
    (u"义务词阶梯⇎标题分档⇎目录引道符",
     u"大写族⇎小写族分家, 边界尺 alpha/alnum 两档并立; 标题形状尺一条正则代逐字符吃档",
     u"五式原面 %s ⇎ 摘壳 %s ⇎ 纯 MUST %s ⇎ 小写四词族 %s ⇎ 标题形总数 %s ⇎ 目录 %s ⇎ 列表 %s ⇎ 正文节 %s ⇎ 目录点引线 常规尺 %s ⇎"
     u" 空格点尺 %s" % (
         J(G['tone_raw']), J(G['tone_sh']), J(G['tone_must_pure']), J(G['tone_lc']),
         J(G['head_tone_shape']), J(G['head_tone_toc']), J(G['head_tone_list']), J(G['head_tone_sec']),
         J(G['head_toc_leader_strict']), J(G['head_toc_leader_spaced'])),
     u"两份论文面五式全零(madp %s ⇎ cake %s) ⇎ 纯 MUST 合计 %d 枚全在三份规范面(逐面 %s) ⇎ MUST 账 %s ⇎ 尺间差 %d ⇎ SHOULD NOT 被 72 列切开逐面"
     u" %s 枚(全在 8289, 针 %s ⇎ 行 %s ⇎ 相邻 %d 对 ⇎ 隔壳 %d 对 ⇎ 账 %d) ⇎ 标题逐档账 %s ⇎ 采集侧档位读数 %s。" % (
         J(G['tone_raw'][1]), J(G['tone_raw'][3]), sum(G['tone_must_pure']), J(G['tone_must_pure']),
         J(G['tone_must_ledger']), G['tone_ruler_close'],
         J(G['tone_straddle']), J(G['tone_straddle_nd']), J(G['tone_straddle_lines']),
         G['tone_straddle_adj'], G['tone_straddle_shell'], G['tone_straddle_ledger'],
         J(G['head_tier_close']), J(G['head_tier_pick']))),
    (u"语态⇎引用矩阵",
     u"`VOICE`(9 式) ⇎ `CIT`(12 式)定义照抄, 计数换前瞻档; 谁引谁由“RFC+编号”紧接的面上位置现扫",
     u"第一人称动词式 %s ⇎ 非人称式 %s ⇎ we 计数 %s ⇎ 方括号编号 %s ⇎ “RFC 编号”式 %s" % (
         J(G['voice_weverb']), J(G['voice_impersonal']), J(G['voice_we']), J(G['cit_brk']), J(G['cit_rfc'])),
     u"规范面的 we 一枚也不比论文少(%d ⇎ 两份论文 %d/%d) ⇎ 谁引谁 %s ⇎ 最新两份对外引用合计 %d 枚 ⇎ 8289 不引 7567 也不引 8033 ⇎ 论文面"
     u"编号引用只在论文面(%s 枚 ⇎ 规范面 %d 枚)。" % (
         G['voice_we'][4], G['voice_we'][1], G['voice_we'][3],
         u' '.join(u'%s→%s' % (LBL[i], u','.join(str(x) for x in G['cite_matrix'][i])) for i in range(NSRC)),
         sum(G['cite_matrix'][i][j] for i in (3, 4) for j in range(NSRC)),
         J(G['cit_brk']), sum(G['cit_brk'][i] for i in RFCI))),
    (u"节窗⇎目录陷阱",
     u"节号尺 `^( *)([0-9.]+)( )` ⇎ 论文面节题 `^\\s*([IVX]+)\\.\\s+[A-Z]` 两把并跑; 定界取不早于节头的下一个同级标题",
     u"节号 %s ⇎ 窗幅行 %s ⇎ 字符 %s ⇎ 占摘壳面 %s ⇎ 节内义务词 %s(合计 %d) ⇎ 同名标题命中 %s ⇎ 目录行 %s ⇎ 正文行 %s" % (
         J(G['sec_no']), J(G['sec_lines']), J(G['sec_chars']),
         u' ⇎ '.join(u'%s%%' % x for x in G['sec_span_pct']),
         J(G['sec_tone_tot']), G['sec_tone_tot_all'], J(G['sec_hit_n']), NJ(G['sec_toc_line']),
         J(G['sec_body_line'])),
     u"节号两轨同值(采集侧 %s) ⇎ 8289 的答案句在 §4 总述 %d 行 ⇎ 专讲 TARGET 的 “%s” 在 %d 行 ⇎ 相隔 %d 行 ⇎ 节内针 %s ⇎ 节内参数名"
     u" %s ⇎ 节内数值 %s。" % (
         J(G['sec_no_pick']), G['sec_body_line'][4], G['sec_sub_title'], G['sec_sub_line'],
         G['sec_sub_line'] - G['sec_body_line'][4], J(G['sec_role']), J(G['sec_par']), J(G['sec_numval']))),
    (u"答句⇎段窗⇎行号尺",
     u"答句由逐字符句界导出(采集侧用前瞻正则), 再由段窗尺拿整句重导一遍对拍; 行号经 `bisect_right` 回映射",
     u"答句词数 %s(共 %d) ⇎ 整句跨行 %s(共 %d) ⇎ 锚针本身跨行 %s ⇎ 句比针多 %s 行 ⇎ 自然段行数 %s ⇎ 段内壳行 %s ⇎ 一行读全 %d 份" % (
         J(G['ans_words']), G['ans_words_tot'], J(G['ans_span']), G['ans_span_tot'],
         J(G['ans_needle_span']), J(G['ans_needle_gap']), J(G['ans_block_lines']),
         J(G['ans_shell_rows']), G['ans_one_line_n']),
     u"行号两轨差合计 %d ⇎ 跨行差 %d ⇎ 空壳账 %s ⇎ 句界尺重导同值判定 %d ⇎ 采集侧同串 %s ⇎ 尾随空白 %s; 十四段行 %s ⇎ 字符 %s ⇎ 词 %s"
     u" ⇎ 词表 %s ⇎ 首行 %s ⇎ 末行 %s ⇎ 段窗相对答句 %s ⇎ 五段主答 %d 行 %d 词 %d 字符。" % (
         G['ans_line_close'], G['ans_span_close'], J(G['ans_row_ledger']), G['ans_ruler_rematch'],
         J(G['ans_vs_pick']), J(G['ans_tail_ws']), J(G['blk_rows']), J(G['blk_chars']),
         J(G['blk_words']), J(G['blk_vocab']), J(G['blk_head_row']), J(G['blk_tail_row']),
         J(G['blk_head_gap']), G['blk_five_rows'], G['blk_five_words'], G['blk_five_chars'])),
    (u"模板段⇎套版长行池",
     u"池=剥壳后逐行折平(不拆字 ⇎ 不改大小写)长度 ≥40 的行去重; 归属向量 `Counter` ⇎ 共用走文档下标组合逐枚数共现",
     u"各份 %s ⇎ 并集 %d ⇎ 原行 %s(同文重印 %d) ⇎ 分档(共用 1..5 份)%s ⇎ 两两 %s ⇎ 三三 %d ⇎ 四份以上 %d ⇎ 阈值放宽 25 字符并集 %d(多"
     u" %d)" % (
         J(G['pool_n']), G['pool_union'], J(G['pool_raw_rows']), G['pool_dup'], J(G['pool_tier']),
         u' '.join(u'%s=%d' % (k, v) for k, v in G['pool_pair'].items()), G['pool_trip_tot'],
         G['pool_quad_tot'], G['pool_union25'], G['pool_widen']),
     u"容斥账 %d(各份之和 %d − 两两 %d + 三三 %d = 并集 %d) ⇎ 分档账 %d ⇎ 加和账 %d ⇎ 三份 RFC 之间 %d 枚 ⇎ 凡牵进论文的每一对 %d 枚"
     u"(%d 对全冷, 判定 %d) ⇎ 共用 %d 枚里带义务词 %d ⇎ 带“RFC”字样 %d ⇎ 讲本文档现状 %d; 关键词模板段 %d 份各印一次而互不相同(共头"
     u" %d/%d/%d 词 ⇎ 共尾 %d/%d/%d ⇎ NOT RECOMMENDED 只在 8289 %s 枚) ⇎ 论文面口径不存在登记 %s ⇎ 行号 %s。" % (
         G['pool_ie_close'], G['pool_sum'], G['pool_pair_tot'], G['pool_trip_tot'], G['pool_union'],
         G['pool_tier_close'], G['pool_sum_close'], G['pool_pair_rfc'], G['pool_pair_paper'],
         G['pool_pair_paper_n'], G['paper_pool_cold'], G['pool_shared_rfc'], G['pool_shared_toned'],
         G['pool_shared_rfcline'], G['pool_shared_status'], G['kw_docs'], G['pre_kw_7567_8033'],
         G['pre_kw_7567_8289'], G['pre_kw_8033_8289'], G['suf_kw_7567_8033'], G['suf_kw_7567_8289'],
         G['suf_kw_8033_8289'], J(G['kw_notrec']), J(G['kw_at']), J(G['kw_minus_row']))),
    (u"闭合账⇎锚⇎对账",
     u"门的右式 ⇎ 恒等式表达式从两遍源码 `ast` 摘出后在本遍读数上 eval; 锚由条目正文的手写配对扫描现推, 双轨同判才计数",
     u"布尔门 %d/%d ⇎ 恒等式 %d+%d=%d ⇎ V 形 %d 条 ⇎ DERIV %d 键/%d 处引用 ⇎ 采集对账 %d/%d ⇎ 锚 %d 处/去重 %d/单面 %d/跨面 %d/五面同"
     u" %d ⇎ 编码区 %d 字符 ⇎ 键 %d" % (
         G['bool_all_sum'], G['bool_all_n'], G['zid_scan_n'], G['zid_scan2_n'],
         G['zid_scan_n'] + G['zid_scan2_n'], len(CH['zid']), len(DER), DCITE,
         G['pick_agree'], G['pick_same_n'], G['anchor_total'], G['anchor_distinct'],
         G['anchor_single'], G['anchor_cross'], G['anchor_all5'], G['enc_chars'], G['contract_n']),
     u"锚误读 %d 枚 ⇎ 行号回读 %d/%d ⇎ 不符键 %d ⇎ 未复算 %d ⇎ 独有 %d ⇎ 判词 %d 条 ⇎ 内容针 %d 枚 ⇎ 反向针 %d 枚; 五面同串的锚 %d 枚 ⇎ 跨两三面的"
     u" %d 枚(%s ⇎ 长形那枚 %s)——同串不等于同句: 五面同串的 “%s” 只有两字母, 它在 7567 与 8033 的整词读数都是 0(子串轨却读 %s/%s),"
     u" 靠子串轨才落进五面; 真共用的整句模板只有长形那枚。 余下 %d 枚只在自己那份面上读得到。" % (
         G['anchor_err'], _back, G['anchor_total'], len(BAD), len(UNCOVER), len(MISS),
         G['checks'], G['needle_n'], G['neg_n'], len(A5), len(A2),
         u' '.join(u'%s(%s)' % (a[:44], u','.join(LBL[d] for d in HITC[a])) for a in A2 if a == A2SHORT),
         u' '.join(u'%s(%s)' % (a[:44], u','.join(LBL[d] for d in HITC[a])) for a in A2 if a == A2LONG),
         A5S, G['neg_sub'][MI][0], G['neg_sub'][MI][2], G['anchor_single']))]
assert len(rows) == 15, len(rows)
for _r in rows:
    _c = [cell(x) for x in _r]
    A(u'| %s | %s | %s | %s |' % tuple(_c))
A(u"")


def QRAW(tag, s):
    assert any(s in a[1] for a in FD5[IDX[tag]]), u'原行里读不到: ' + s[:50]
    return u'⟦%s⟧⟨%s⟩' % (tag, s)


NCOIN = len([k for k in DER if u'split_head_chars' in DER[k] or u'split_tail_chars' in DER[k]])
A(u"五种答话在本遍的面上仍是五次不同的动作, 而这是换了一整套算法之后仍然落回同一处的结果。 7567 通篇 %d 项带单位时长 ⇎ 数值十七式读数"
  u" %s——它把主张写成规范性标题: %s(§4.3 正文 %d 行, 同一串在目录 %d 行被硬换行推到下一行才成式: %s), 全库只有它这一份的标题形计数"
  u"非零(%s 枚 ⇎ 两份论文 %d ⇎ %d)。 madp 的 “20 ms” %d 枚 ⇎ “100 ms” %d 枚, 立数方式只有两种: 转述别家的默认——%s(句中带 [7], 把 20 ms 归给"
  u" PIE); 或写进自己的仿真参数——%s。 “100 ms” 在本遍登记的两个角色都是引述(PIE 的突发容忍 ⇎ CoDel 的 RTT 假设), 它自己不给数。"
  u" 8033 给双档默认并把毫秒写全: %s——缩写 ms 整词 %d 枚 ⇎ 全称四形 %d/%d/%d/%d 枚。 cake 不作宣称只报实测: %s(宣称族命中 %d 枚"
  u" ⇎ 义务词五式 %s), 第一人称就写在实测句里: %s。 8289 先给定义式再导出: %s ⇎ 参数名 TARGET/INTERVAL %d/%d 枚为全库唯一(%d 式) ⇎"
  u" sojourn %d 枚只活在它家(其余四份合计 %d)。 五份抬头年跨 %s, 而“谁引谁”矩阵里最新两份对外引用合计 %d 枚。" % (
      G[u'numval_n'][0], J(G[u'num'][0]),
      QT(u'7567', u'4.3.  AQM Algorithm Deployment SHOULD NOT Require Operational Tuning'),
      G[u'sec_body_line'][0], G[u'sec_toc_line'][0],
      QT(u'7567', u'AQM Algorithm Deployment SHOULD NOT Require Operational'),
      J(G[u'head_tone_shape']), G[u'head_tone_shape'][1], G[u'head_tone_shape'][3],
      G[u'num'][1][3], G[u'ms100_count'][1],
      QT(u'madp', u'to be less sensitive to trafﬁc loads [7], its default target delay of 20 ms should be less'),
      QT(u'madp', u'\u03c4 = 20 ms and \u03bb = 30 ms'),
      QT(u'8033', u'defaulted to 15 milliseconds and 150 milliseconds for non-data-center'),
      G[u'unit_word'][2][0], G[u'num'][2][10], G[u'num'][2][11], G[u'num'][2][12], G[u'num'][2][13],
      QT(u'cake', u'10 Mbps link with 50 ms baseline latency. Our basic test is the Real-Time Response Under'),
      G[u'cfg_claim'][3], J(G[u'tone_raw'][3]),
      QT(u'cake', u'link. We use the Flent testing tool [23] to run the tests, and the data ﬁles are available'),
      QT(u'8289', u'ms [CHARB2007].  Using this RTT gives a minimum TARGET of 5 ms and'),
      G[u'par'][4][0], G[u'par'][4][1], G[u'par_upper_n'][4], G[u'term'][4][7],
      sum(G[u'term'][i][7] for i in range(4)), J(G[u'years']),
      sum(G[u'cite_matrix'][i][j] for i in (3, 4) for j in range(NSRC))))
A(u"被切开的那 %d 枚判词, 本遍不再抄第二遍登记的字面, 而是从偏移经 `bisect` 映回原行再按逐字符对照表切两半: 八枚的两半逐枚回自己那一行"
  u"都读得通(%d/8 枚), 而把整串拿到首行去读则 %d/8 枚读得通——线切过之后没有一枚还完整留在自己那一行。 其中 %d 枚是 72 列硬换行切的 ⇎ %d 枚是页壳切的——壳切那两枚的两行之间确实"
  u"夹着 %s 行非空壳行, 例: %s ⇎ 下一行 %s。 跨行幅度合计 %d 行 ⇎ 两半字符合计 %d 字符 ⇎ 幅度与枚数之差登记 %d。 语气词也被同一根线切开:"
  u" 摘壳面比原面多读 %s 枚, 一式全在 8289——上一行收尾 %s ⇎ 下一行起头 %s(行 %s), SHOULD NOT 因此只在折平后成式。" % (
      G[u'split_n'], G[u'split_half_ok'], G[u'split_full_on_head'], G[u'split_wrap_n'], G[u'split_shell_n'],
      J(G[u'split_shell_between']),
      QRAW(G[u'split_lbl'][6], SPLIT5[6][3]), QRAW(G[u'split_lbl'][6], SPLIT5[6][4]),
      G[u'split_span_tot'], G[u'split_rows_tot'], G[u'split_span_vs_miss'], J(G[u'tone_straddle']),
      QT(u'8289', u'necessary to increase INTERVAL by that extra delay.  TARGET SHOULD'),
      QT(u'8289', u'NOT be adjusted for such short-term bursts, but INTERVAL MAY need to'),
      J(G[u'tone_straddle_lines'])))
A(u"套版长行池 %d 枚在两遍不同的池代数下逐值相同(第二遍对键域取集合 `&` ⇎ 本遍对文档下标的组合逐枚数共现 ⇎ 归属向量走 `Counter` 直方图):"
  u" 分档 %s ⇎ 两两 %s ⇎ 三三 %d ⇎ 四份以上 %d, 容斥账 %d(各份之和 %d − 两两 %d + 三三 %d = 并集 %d)。 这个池把体裁判据直接摊开: 三份 RFC"
  u" 之间共用 %d 枚(最大对 %d ⇎ 最小对 %d) ⇎ 凡牵进任何一份论文的每一对 %d 枚(%d 对全冷)——论文面与规范面不共享一行套版。 共用那 %d 枚里"
  u"带义务词的只有 %d 枚 ⇎ 带“RFC”字样 %d 枚 ⇎ 讲本文档现状 %d 枚。 关键词模板段三份各印一次而互不相同: 两两共头 %d/%d/%d 词 ⇎ 共尾 %d/%d"
  u"/%d 词 ⇎ 8289 与谁都在 %d 词处断开(它多插一枚 NOT RECOMMENDED: %s 枚)。 论文面没有这一段, 口径不存在按 -1 登记(行号 %s)。 “as described"
  u" in” 在 7567 面上有 %d 枚候选(版权行 %d ⇎ 关键词段末枚 %d), 锚归属带上限才落对(判定 %d)。" % (
      G[u'pool_union'], J(G[u'pool_tier']),
      u' '.join(u'%s=%d' % (k, v) for k, v in G[u'pool_pair'].items()), G[u'pool_trip_tot'], G[u'pool_quad_tot'],
      G[u'pool_ie_close'], G[u'pool_sum'], G[u'pool_pair_tot'], G[u'pool_trip_tot'], G[u'pool_union'],
      G[u'pool_pair_rfc'], G[u'pool_max_pair'], G[u'pool_min_pair_rfc'], G[u'pool_pair_paper'],
      G[u'pool_pair_paper_n'], G[u'pool_shared_rfc'], G[u'pool_shared_toned'], G[u'pool_shared_rfcline'],
      G[u'pool_shared_status'], G[u'pre_kw_7567_8033'], G[u'pre_kw_7567_8289'], G[u'pre_kw_8033_8289'],
      G[u'suf_kw_7567_8033'], G[u'suf_kw_7567_8289'], G[u'suf_kw_8033_8289'], G[u'kw_min_head'],
      J(G[u'kw_notrec']), J(G[u'kw_minus_row']), G[u'as_desc_n'], G[u'as_desc_rows'][0],
      G[u'as_desc_rows'][1], G[u'as_desc_amb_resolved']))
A(u"三处口径要在这里挑明, 因为它们是本遍与第二遍唯一可能读出差的地方, 而差别来自实现不是来自数据。 其一: 由折平行拼整篇面时, 第 k 行的"
  u"起始列是“前 k 行长度之和加 k”(每两行之间有一枚分隔空格)——本遍第一版按“加 k−1”算, 两半字数于是各偏一枚, 最先显形的正是引用这两个键的"
  u" %d 枚巧合式; 改正后逐枚落回第二遍的原值(%s ⇎ %s)。 其二: 第二遍的 `%s` 把两半登记成按行界切开的长度, 本遍改由逐字符对照表取区间,"
  u" 两条通道给出同一组数(%s ⇎ %s ⇎ 两半回本行全读通 %d/8)。 其三: 段落层用的面是“折平加拆字”的(%s), 与纯折平面(%s)逐份差 %s 字符,"
  u" 非零只落在两份论文面上——拆字把每一枚连字号还原成两枚字母, 所以枚数与字符数在这里同值; 摘壳档的两面也各登记在案(%s ⇎ %s)。"
  u" 另两处如实登记: 数值族的“子串减整词”清单两遍都登记为空(%d 枚)——第二遍的循环上界按构造写死为 %d, 本遍照抄定义而没有“修好”它,"
  u" 真正的尺间差住在 `%s`=%s 与 `%s`=%s 两本账里; 锚的归属同理不能按条目推: 五面同串的只有 %d 枚, 而它是两字母短形 “%s”——它在 7567 与 8033 的"
  u"整词读数都是 0, 只在子串轨上读到 %d/%d 枚, 是短形嵌在长词尾(`algorithms ⇎ mechanisms` 那一类词的末两字母)的必然结果; 跨面两枚里 “%s” 同为单词形, 真正"
  u"整句共用的模板只有 “%s” 一枚。 所以锚只能按面逐枚数, 同串⇎同句是两件事。" % (
      NCOIN, J(G[u'split_head_chars']), J(G[u'split_tail_chars']), u'split_pieces',
      J(G[u'split_head_chars']), J(G[u'split_tail_chars']), G[u'split_half_ok'],
      u'row_fd5', u'FOLD5', J(G[u'lig_char_add']), J(G[u'sh_chars']), J(G[u'shlig_chars']),
      len(G[u'num_sub_vs_word']), 0, u'unit_sub_over', J(G[u'unit_sub_over']),
      u'term_ruler_gap', J(G[u'term_ruler_gap']), G[u'anchor_all5'], A5S,
      G['neg_sub'][MI][0], G['neg_sub'][MI][2], A2SHORT, A2LONG))
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"五份文件在 RFC Editor 与出版方站点此刻的状态(7567 是否仍挂 BCP ⇎ 8033 与 8289 有没有新 errata 改过这几句默认值 ⇎ madp 与 cake 这两篇"
  u"会议论文此刻是否被撤稿或改版) ⇎ 现网路由器与内核实现实际把 TARGET 取成多少(标准与论文给出的数字不等于装机行为) ⇎ PDF 原版式与此"
  u"纯文本面的排版差异(论文面 %d 枚连字与 %d ⇎ %d 枚非 ASCII 在 PDF 里落成什么) ⇎ 抓取时刻与磁盘 mtime 谁新谁旧 ⇎ 被“as described in”指向"
  u"却不在本库的 2119 正文——这些都要在库外字节或实时状态, 本库 %d 份文件给不出判据; 在库只给得出面上字节的四档读数 ⇎ %d 枚判词针的"
  u"位置账 ⇎ %d 枚反面针的冷账。" % (
      sum(G[u'lig_total']), G[u'na_total'][1], G[u'na_total'][3], G[u'nsrc'], G[u'needle_n'], G[u'neg_n']))

NEW = u"## ⛓解读注" + NL + NL + NL.join(L2) + NL
_i2 = TT.index(u"## ⛓解读注")
out = TT[:_i2] + NEW
assert out.count(u"## ⛓解读注") == 1
T2 = ENTRY + u'.tmp'
io.open(T2, 'w', encoding='utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"⛓解读注 已写入 %s ｜ 表 %d 行 ⇎ 注区 %d 字符 ⇎ 复算 %d 键 ⇎ 不符 %d ⇎ 独有 %d ⇎ 未复算 %d ⇎ "
      u"恒等式 %d+%d ⇎ V 形 %d 条 ⇎ DERIV %d 键 ⇎ 门 %d/%d ⇎ 编码区 %d 字符未动"
      % (ENTRY, len(rows), len(NEW), len(G) - 1, len(BAD), len(MISS), len(UNCOVER),
         G[u'zid_scan_n'], G[u'zid_scan2_n'], len(CH[u'zid']), len(DER),
         G[u'bool_all_sum'], G[u'bool_all_n'], G[u'enc_chars']))
