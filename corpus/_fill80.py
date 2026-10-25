# -*- coding: utf-8 -*-
"""B80 的第五遍复测: 采集侧(_pick80.py)⇎ 建条目侧(_mkB80.py + _mk80emit.py)⇎ 门槛侧(audit.py::_b80_scan)
换算法不换定义, 现算后把 ⛓解读注 写进条目。本遍的独立处:
①行界: 手写索引循环按 `\\n` 切(第二遍是 `str.split`, 采集侧是 `re.split`), 换行枚数走 `str.count`;
②折平/归一: `re.sub('\\s+',' ')` 档(第二遍是 `' '.join(s.split())`), 与 `fold` ⇎ `pnorm` 逐份对拍;
③针计数三档: `str.count`(非重叠) ⇎ `findall(re.escape)` ⇎ `findall('(?=针)')`(重叠), 逐行档走手写循环;
④邻居尺: `finditer` 定位后取左右邻字符判 alpha/digit/alnum(第二遍是游标 find + `_nb` 手扫, 采集侧是断言正则),
  另起一条断言正则档与它逐枚对拍, 两轨之差就是本遍的语气尺闭合;
⑤壳谓词: `strip()` 后按空格切 token 的第三档(第二遍是折平切档, 采集侧是三条整序正则), 逐行对拍后拆账到行;
⑥节号尺: 一条 `^(\\d+(\\.\\d+)*)(\\.?)` 正则代第二遍的逐字符吃档, 逐行对拍; 句界尺换成
  `\\.(?=[ \\t\\n]*(?:[A-Z(]|$))` 一条 finditer 代第二遍的手扫;
⑦行号尺: 偏移→行号走 `bisect_right`(第二遍是线性扫到尾), 段界定位把 `str.find` 换成编译一次转义针的 `search(hay, frm)`;
⑧段池代数: 归属向量走 `Counter` 直方图 ⇎ 容斥走“对文档下标的组合逐枚求交”(第二遍是 C(len(v),k) 逐元算式),
  两两共用走“按键域扫一遍”(第二遍是集合 &), 写法归一 `dehyph` 换成 `re.sub('-[ \\t]*','')`;
⑨状态码行 ⇎ ABNF 行 ⇎ 抬头三式 ⇎ 标题形状三档: 各起一条本遍的正则/切片档, 与第二遍的谓词在全库逐行对拍, 不等即停;
⑩针表 `SENT` ⇎ 十二族 `PINS` ⇎ 九族施事针 ⇎ 二十枚码表 ⇎ 语气五式的**定义**从源码 `ast`/`exec` 复用——要换的是量, 不是定义;
⑪锚归属双轨: 原子串对锚平面(非壳原行)逐行 membership ⇎ 对整篇归一串 substring, 两式同判才计数; 42 处锚的
  行号 ⇎ 候选行数与 `_b80checks.json` 的 `anchor_lines` 逐枚回读对上;
⑫恒等式与 DERIV: 139 条标量式从 `_mkB80.py` 源码 `ast` 摘 `Z(...)`、28+若干布尔门摘 `CLOSE[..] = ⇎ CLOSE2[..] =`
  的右式, 再在本遍读数上 eval(不抄第二遍的结论); 163 条 V 形 ⇎ 198 键 DERIV 复算点从 `_b80checks.json` ⇎
  `_deriv80.json` 回读 eval; 采集侧 167 键对账在本遍重跑。
每个键与 corpus/_b80flat.json 逐值对拍, 值不符或键缺失一律先收集后汇总; 覆盖不足也要如实报数。"""
import io, os, re, sys, json, ast, bisect, itertools as IT
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
ENTRY = u'%s/babeltele/B80_http_automatic_retry_five_answers.md' % C
PATH = [u'%s/raw/httpretry/rfc2616.txt' % C, u'%s/raw/httpretry/rfc7231.txt' % C,
        u'%s/raw/httpretry/rfc6585.txt' % C, u'%s/raw/httpretry/rfc8470.txt' % C,
        u'%s/raw/httpretry/rfc9110.txt' % C]
LBL = [u'2616', u'7231', u'6585', u'8470', u'9110']
NSRC = 5
NL = u'\n'
TAGS = LBL
IDX = dict((t, n) for n, t in enumerate(LBL))

FLAT = json.load(io.open(u'%s/_b80flat.json' % C, encoding='utf-8'))
CH = json.load(io.open(u'%s/_b80checks.json' % C, encoding='utf-8'))
DER = json.load(io.open(u'%s/_deriv80.json' % C, encoding='utf-8'))
MEA = json.load(io.open(u'%s/_b80meas.json' % C, encoding='utf-8'))

MS = io.open(u'%s/_mkB80.py' % C, encoding='utf-8').read()
EM = io.open(u'%s/_mk80emit.py' % C, encoding='utf-8').read()

# ---- 定义(不是本遍要换的量): 字面表用 ast 摘, 谓词函数用 exec 取来对拍 ----
TABS = (u'SENT', u'TONE', u'AUTOFAM', u'REWORD', u'SUBJ', u'ACT', u'NUM', u'METH', u'NEG',
        u'CODES', u'PAREN', u'PINS', u'ANS_HEAD', u'ANS_PH', u'MON', u'RANK')
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
for nm in TABS:
    assert TAB.get(nm) is not None, nm
SENT = TAB[u'SENT']
TONE = TAB[u'TONE']
AUTOFAM = TAB[u'AUTOFAM']
REWORD = TAB[u'REWORD']
SUBJ = TAB[u'SUBJ']
ACT = TAB[u'ACT']
NUM = TAB[u'NUM']
METH = TAB[u'METH']
NEG = TAB[u'NEG']
CODES = TAB[u'CODES']
PAREN = TAB[u'PAREN']
PINS = TAB[u'PINS']
ANS_HEAD = TAB[u'ANS_HEAD']
ANS_PH = TAB[u'ANS_PH']
MON = TAB[u'MON']
RANK = TAB[u'RANK']

# ---- 第二遍的谓词: 只用来对拍, 本遍的读数一律走自己的尺 ----
PK = [u'pnorm', u'fold', u'_nb', u'ub', u'cnt_cur', u'cnt_ovl', u'cnt_re', u'is_shell_pick',
      u'is_page_shell_pick', u'shell_line', u'sect_no', u'sent_ends', u'sent_count',
      u'code_row_picklike', u'is_abnf_row', u'hdr_form', u'dehyph', u'bucket', u'sents',
      u'tag_rulers']
_ns = {u're': re, u'NL': NL, u'RANK': RANK, u'u': u''}
for fn in PK:
    m = re.search(u'def ' + fn + u'\\(.*?\\):.*?\\n(?=\\S)', MS, re.S)
    assert m, fn
    exec(m.group(0), _ns)
for fn in PK:
    assert fn in _ns, fn
mk_pnorm = _ns[u'pnorm']
mk_fold = _ns[u'fold']
mk_ub = _ns[u'ub']
mk_cnt_cur = _ns[u'cnt_cur']
mk_cnt_ovl = _ns[u'cnt_ovl']
mk_cnt_re = _ns[u'cnt_re']
mk_is_pick = _ns[u'is_shell_pick']
mk_is_pg = _ns[u'is_page_shell_pick']
mk_shell = _ns[u'shell_line']
mk_sect_no = _ns[u'sect_no']
mk_sent_ends = _ns[u'sent_ends']
mk_sent_count = _ns[u'sent_count']
mk_code_row = _ns[u'code_row_picklike']
mk_abnf = _ns[u'is_abnf_row']
mk_hdr_form = _ns[u'hdr_form']
mk_dehyph = _ns[u'dehyph']
mk_bucket = _ns[u'bucket']
mk_sents = _ns[u'sents']
mk_tag_rulers = _ns[u'tag_rulers']


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
    """折平: re.sub 档(第二遍是 ' '.join(split()))"""
    return re.sub(u'\\s+', u' ', s).strip()


def p5(s):
    return re.sub(u'\\s+', u' ', s.lower()).strip()


def w5(s):
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


def c5(hay, nd):
    """非重叠计数: str.count(第二遍是 findall(re.escape), 采集侧是游标 find)"""
    return hay.count(nd)


def r5(hay, nd):
    return len(re.findall(re.escape(nd), hay))


def o5(hay, nd):
    return len(re.findall(u'(?=' + re.escape(nd) + u')', hay))


assert c5(u'aXbX', u'X') == r5(u'aXbX', u'X') == mk_cnt_cur(u'aXbX', u'X') == 2
assert o5(u'aaa', u'aa') == mk_cnt_ovl(u'aaa', u'aa') == 2
assert f5(u'  A \t\nb ') == mk_fold(u'  A \t\nb ') and p5(u' A b\n') == mk_pnorm(u' A b\n')
assert w5(u'a b  c\n') == 3 == len(u'a b  c\n'.split())


def locate(hay, nd, frm=0):
    """定位针: 编译一次转义正则后 search(第二遍是 str.find)"""
    m = re.compile(re.escape(nd)).search(hay, frm)
    return -1 if m is None else m.start()


def nb5(s, i, n, kind):
    """邻居档: finditer 之外由本遍自己看左右邻字符(与第二遍同定义, 但由 finditer 驱动)"""
    a, b = i - 1, i + n
    if kind == u'alpha':
        return not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha())
    if kind == u'digit':
        return not (a >= 0 and s[a].isdigit()) and not (b < len(s) and s[b].isdigit())
    return not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())


def ub5(s, w, kind=u'alpha'):
    """边界尺: 重叠定位(lookahead 轨)后由 nb5 验左右邻(第二遍是游标 find + `_nb` 手扫)"""
    return len([m for m in re.finditer(u'(?=' + re.escape(w) + u')', s)
                if nb5(s, m.start(), len(w), kind)])


CLS5 = {u'alpha': u'A-Za-z', u'digit': u'0-9', u'alnum': u'A-Za-z0-9'}


def ub5re(s, w, kind=u'alpha'):
    """第二把尺: 断言正则档(只用于对拍, 不参与读数)"""
    return len(re.findall(u'(?<![' + CLS5[kind] + u'])' + re.escape(w) + u'(?![' + CLS5[kind] + u'])', s))


assert ub5(u'MUST NOT', u'MUST') == ub5re(u'MUST NOT', u'MUST') == 1
assert ub5(u'aMUSTx 9MUST 9', u'MUST') == 1 == ub5re(u'aMUSTx 9MUST 9', u'MUST')
assert ub5(u'aaaa', u'aa') == ub5(u'aaaa', u'aa', u'alnum') == 0
assert ub5(u'429', u'42', u'digit') == ub5re(u'429', u'42', u'digit') == 0


def bd5(nd):
    return u'digit' if nd.isdigit() else u'alpha'


def shell5(x):
    """壳谓词第三档: strip 后按空白切 token, 逐段比首尾(第二遍是折平再切, 采集侧是整序正则)"""
    tk = x.strip().split()
    if not tk:
        return True
    if tk[0] == u'[Page' and len(tk) == 3 and tk[1].isdigit() and tk[2] == u']':
        return True
    if tk[0] == u'RFC' and len(tk) >= 4 and tk[1].isdigit():
        y = tk[-1]
        if len(y) == 4 and y[:2] in (u'19', u'20') and y[2:].isdigit():
            return True
    return False


RE_SECT = re.compile(u'^(\\d+(?:\\.\\d+)*)(\\.?)')


def sect5(s):
    """节号尺: 一条正则代第二遍的逐字符吃档; 返回(元组, 尾点) ⇎ (None, None)"""
    m = RE_SECT.match(s)
    if m is None:
        return None, None
    e = m.end()
    if e >= len(s) or s[e] not in u' \t':
        return None, None
    return tuple(int(z) for z in m.group(1).split(u'.')), m.group(2) == u'.'


RE_SENT = re.compile(u'\\.(?=[ \\t\\n]*(?:[A-Z(]|$))')


def sends5(s):
    """句尾尺: 一条 finditer 代第二遍的手扫, 返回每个句尾下标"""
    return [m.start() for m in RE_SENT.finditer(s)]


def sentend5(s):
    """段内“下一处句尾”: 与第二遍 sent_ends 同定义(只吃 ' \\t\\n' 后看大写/括号/串尾)"""
    for j in sends5(s):
        return j
    return None


def dh5(s):
    """写法归一: re.sub 档(第二遍是逐字符吃)"""
    return re.sub(u'-[ \\t]*', u'', s).lower()


assert all(dh5(x) == mk_dehyph(x) for x in (u'non-\nidempotent', u'a- b', u'x', u'-', u'ab-'))


def spans5(t):
    """`<…>` 形: 手写扫描, 换行不吃(代 <[^>\\n]+>)"""
    out, i, n = [], 0, len(t)
    while i < n:
        a = t.find(u'<', i)
        if a < 0:
            return out
        b = a + 1
        while b < n and t[b] != u'>' and t[b] != NL:
            b += 1
        if b < n and t[b] == u'>':
            out.append(t[a:b + 1])
            i = b + 1
        else:
            i = a + 1


def class5(sh):
    """四把标签尺: 开名形 ⇎ 闭名形 ⇎ <http 形 ⇎ 其余(伪法)"""
    op = cl = ur = 0
    for x in sh:
        if x[1:2] == u'/':
            cl += 1
        elif re.match(u'<[A-Za-z][A-Za-z0-9]*[ >/]', x + u'>') and re.match(
                u'<[A-Za-z][A-Za-z0-9]*(?:[ >/])', x):
            op += 1
        if x.startswith(u'<http'):
            ur += 1
    return len(sh), op, cl, ur


RE_ABNF = re.compile(u'^Retry-After[ \\t]+=')


def abnf5(x):
    s = f5(x)
    return s.startswith(u'Retry-After') and s[len(u'Retry-After'):].lstrip().startswith(u'=')


def hdrform5(x):
    """编号标题三式: 本遍用正则取出编号串后按下标切片数空格"""
    s = x.lstrip(u' \t')
    m = RE_SECT.match(s)
    if m is None:
        return None
    tp, dot = sect5(s)
    if tp is None or len(tp) < 2:
        return None
    j = m.end(1) + (1 if dot else 0)
    sp = 0
    while j + sp < len(s) and s[j + sp] == u' ':
        sp += 1
    if sp == 0 or j + sp >= len(s) or s[j + sp].isspace():
        return None
    if (dot, sp) == (True, 2):
        return u'dot2sp'
    if (dot, sp) == (True, 1):
        return u'dot1sp'
    if (dot, sp) == (False, 1):
        return u'nodot'
    return None


RE_CODE = re.compile(u'^(\\d+(?:\\.\\d+)*)(\\.?)')


def code5(x, c):
    """状态码定义行: 一条正则取编号, 再手工吃空白, 看码后一字符(第二遍是 sect_no + 两段下标)"""
    s = x.lstrip(u' \t')
    m = RE_CODE.match(s)
    if m is None:
        return False
    j = m.end(1) + (1 if m.group(2) else 0)
    if s[j:j + 1] not in (u' ', u'\t'):
        return False
    rest = s[j:].lstrip(u' \t')
    if not rest.startswith(c):
        return False
    nx = rest[len(c):len(c) + 1]
    return not (nx and (nx.isdigit() or nx == u'.'))


def sents5(face):
    """句池切档: 手写扫描按 “标点后至少一枚空白 ⇾ 大写/数字/星/尖括号” 切(代零宽 re.split)"""
    out, a, i, n = [], 0, 0, len(face)
    while i < n:
        if face[i] in u'.!?':
            k = i + 1
            if k < n and face[k].isspace():
                while k < n and face[k].isspace():
                    k += 1
                if k < n and (u'A' <= face[k] <= u'Z' or face[k].isdigit() or face[k] in u'*<('):
                    out.append(face[a:i + 1])
                    a = k
                    i = k
                    continue
        i += 1
    out.append(face[a:])
    return [u' '.join(x.lower().split()) for x in out]


def ent5(t):
    """实体尺: 手写吃 &…; (最多 9 字符), 代 &[A-Za-z#0-9]{1,8};"""
    n, i, m = 0, 0, len(t)
    while True:
        a = t.find(u'&', i)
        if a < 0:
            return n
        b = a + 1
        while b < m and b - a <= 9 and (t[b].isalnum() or t[b] == u'#'):
            b += 1
        if b < m and t[b] == u';' and 1 <= b - a - 1 <= 8:
            n += 1
            i = b + 1
        else:
            i = a + 1


assert ent5(u'&a; &#12; &x &abcdefghi; &ABCDEFGHI;') == len(
    re.findall(u'&[A-Za-z#0-9]{1,8};', u'&a; &#12; &x &abcdefghi; &ABCDEFGHI;'))

G = {}
J = lambda xs: u' ⇎ '.join(u'%s' % x for x in xs)


def num(x):
    return u'%d' % x if isinstance(x, int) and not isinstance(x, bool) else u'%s' % (x,)


# ---------- 面 ----------
B = [io.open(p, 'rb').read() for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
L = [ln5(t) for t in T]
FOLD = [f5(t) for t in T]
LOWFOLD = [x.lower() for x in FOLD]
LOW = [[y.lower() for y in L[i]] for i in range(NSRC)]

# 谓词逐行对拍: 本遍每把尺都要在全库上等于第二遍的定义
for i in range(NSRC):
    assert f5(T[i]) == mk_fold(T[i]) and p5(T[i]) == mk_pnorm(T[i])
    assert all(f5(x) == mk_fold(x) for x in L[i])
    assert [x for x in L[i] if shell5(x)] == [x for x in L[i] if mk_shell(x)], i
    assert [x for x in L[i] if abnf5(x)] == [x for x in L[i] if mk_abnf(x)], i
    assert [hdrform5(x) for x in L[i]] == [mk_hdr_form(x) for x in L[i]], i
    assert [f5(x) and sect5(f5(x)) for x in L[i]] == [f5(x) and mk_sect_no(f5(x)) for x in L[i]], i
    assert spans5(T[i]) == re.findall(u'<[^>\\n]+>', T[i]), i
    assert class5(spans5(T[i])) == tuple(mk_tag_rulers(T[i])), i
    assert ent5(T[i]) == len(re.findall(u'&[A-Za-z#0-9]{1,8};', T[i]))
    assert sentend5(FOLD[i]) == mk_sent_ends(FOLD[i])
    for nd in (TONE + [u'automatic', u'idempotent'] + NEG):
        kd = bd5(nd)
        assert sum(ub5(y, nd.lower() if nd == nd.lower() else nd, kd) for y in L[i]) == sum(
            mk_ub(y, nd.lower() if nd == nd.lower() else nd, kd) for y in L[i]), (i, nd)
SHP = [[x for x in L[i] if not mk_is_pick(x)] for i in range(NSRC)]
SHL = [[x for x in L[i] if not shell5(x)] for i in range(NSRC)]
SH = [f5(NL.join(SHP[i])) for i in range(NSRC)]
assert all(SH[i] == u' '.join(NL.join(SHP[i]).split()) for i in range(NSRC))
for i in range(NSRC):
    assert [x for x in L[i] if mk_is_pick(x)] == [x for x in L[i] if shell5(x)] or True
MO = [[x for x in L[i] if shell5(x) and not mk_is_pick(x)] for i in range(NSRC)]
PO = [[x for x in L[i] if mk_is_pick(x) and not shell5(x)] for i in range(NSRC)]

# ---------- 面量 ----------
G['label'] = LBL
G['src'] = PATH
G['bytes'] = [len(b) for b in B]
G['chars'] = [len(t) for t in T]
G['lines'] = [len(x) for x in L]
G['newlines'] = [t.count(NL) for t in T]
G['lines_nl'] = [G['newlines'][i] + 1 for i in range(NSRC)]
G['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
G['blank'] = [len([x for x in L[i] if f5(x) == u'']) for i in range(NSRC)]
G['maxlen'] = [max(len(x) for x in L[i]) for i in range(NSRC)]
G['over72'] = [len([x for x in L[i] if len(x) > 72]) for i in range(NSRC)]
G['ff'] = [t.count(u'\x0c') for t in T]
G['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
G['ff_only'] = [len([x for x in L[i] if f5(x) == u'' and x != u'']) for i in range(NSRC)]
G['ff_inline'] = [len([x for x in L[i] if u'\x0c' in x and x != u'\x0c']) for i in range(NSRC)]
G['cr'] = [t.count(u'\r') for t in T]
G['nul'] = [t.count(u'\x00') for t in T]
G['nonascii'] = [len([c for c in t if ord(c) > 127]) for t in T]
G['bom'] = [1 if b[:3] == b'\xef\xbb\xbf' else 0 for b in B]
G['byte_cp_delta'] = [G['bytes'][i] - G['chars'][i] for i in range(NSRC)]
G['nonascii_extra'] = [sum(len(c.encode('utf-8')) - 1 for c in T[i] if ord(c) > 127)
                       for i in range(NSRC)]
G['tail_nl'] = [1 if t.endswith(NL) else 0 for t in T]
G['lines_split'] = [len(t.splitlines()) for t in T]
G['lines_split_close'] = sum(G['lines_nl'][i] - G['tail_nl'][i] + G['ff'][i] - G['ff_inline'][i]
                             - G['lines_split'][i] for i in range(NSRC))
G['digit_chars'] = [sum(1 for c in t if c.isdigit()) for t in T]
TAG4 = [class5(spans5(t)) for t in T]
G['txt_n'] = len([1 for p in PATH if p.lower().endswith(u'.txt')])
G['html_n'] = NSRC - G['txt_n']
G['tag_shape'] = [x[0] for x in TAG4]
G['tag_open'] = [x[1] for x in TAG4]
G['tag_close'] = [x[2] for x in TAG4]
G['tag_url'] = [x[3] for x in TAG4]
G['tag_pseudo'] = [G['tag_shape'][i] - G['tag_open'][i] - G['tag_close'][i] - G['tag_url'][i]
                   for i in range(NSRC)]
G['ent_total'] = [ent5(t) for t in T]
G['comment'] = [t.count(u'<!--') for t in T]
G['shell_lines'] = [len(L[i]) - len(SHP[i]) for i in range(NSRC)]
G['fold_chars'] = [len(x) for x in FOLD]
G['sh_chars'] = [len(x) for x in SH]
G['sh_char_gap'] = [G['sh_chars'][i] - G['fold_chars'][i] for i in range(NSRC)]
G['pg_lines'] = [len([x for x in L[i] if u'[Page ' in x and x.rstrip().endswith(u']')])
                 for i in range(NSRC)]
G['hdr_lines_indent'] = [len([x for x in L[i] if f5(x).startswith(u'RFC ')]) for i in range(NSRC)]


def hdr_tight5(x):
    """顶格抬头: 本遍切片判(第二遍是 ^RFC \\d+\\b)"""
    if not x.startswith(u'RFC '):
        return False
    j = 4
    while j < len(x) and x[j].isdigit():
        j += 1
    return j > 4 and (j >= len(x) or not x[j].isalnum())


assert len([x for x in L[1] if hdr_tight5(x)]) == len(
    [x for x in L[1] if re.match(r'^RFC \d+\b', x)])
G['hdr_lines_tight'] = [len([x for x in L[i] if hdr_tight5(x)]) for i in range(NSRC)]
G['pageless'] = [1 if (G['ff'][i] == 0 and G['pg_lines'][i] == 0) else 0 for i in range(NSRC)]
G['ff_minus_pg'] = [G['ff'][i] - G['pg_lines'][i] for i in range(NSRC)]
G['shell_pick'] = G['shell_lines']
G['shell_mk'] = [len(L[i]) - len(SHL[i]) for i in range(NSRC)]
G['shell_mk_only'] = [len(x) for x in MO]
G['shell_pick_only'] = [len(x) for x in PO]
G['shell_both'] = [G['shell_mk'][i] - G['shell_mk_only'][i] for i in range(NSRC)]
G['shell_ledger_close'] = sum(abs(G['shell_pick'][i] + G['shell_mk_only'][i]
                                  - G['shell_pick_only'][i] - G['shell_mk'][i]) for i in range(NSRC))
G['shell_pick_hdr'] = [len([x for x in PO[i] if f5(x).startswith(u'RFC')]) for i in range(NSRC)]
G['shell_mk_hdr'] = [len([x for x in MO[i] if f5(x).startswith(u'RFC')]) for i in range(NSRC)]


# ---------- 抬头谱系(本遍按“冒号字段 + 一条数字逗号串正则”取) ----------
RE_FIELD = {}


def head_field5(i, key):
    for x in L[i][:22]:
        s = x.strip()
        if not s.startswith(key + u':'):
            continue
        m = re.match(u'^' + re.escape(key) + u':([0-9, ]*)', s)
        if m is None:
            continue
        return [y.strip() for y in m.group(1).split(u',')]
    return []


G['obs_ids'] = [head_field5(i, u'Obsoletes') for i in range(NSRC)]
G['upd_ids'] = [head_field5(i, u'Updates') for i in range(NSRC)]
G['obs_line'] = [next((x.strip() for x in L[i][:22] if x.strip().startswith(u'Obsoletes:')), None)
                 for i in range(NSRC)]
G['upd_line'] = [next((x.strip() for x in L[i][:22] if x.strip().startswith(u'Updates:')), None)
                 for i in range(NSRC)]
G['std_line'] = [next((x.strip() for x in L[i][:22] if f5(x).startswith(u'STD:')), None)
                 for i in range(NSRC)]
G['issn_hdr'] = [1 if any(x.strip().startswith(u'ISSN:') for x in L[i][:22]) else 0
                 for i in range(NSRC)]
MONRE = re.compile(u'(' + u'|'.join(MON) + u') ([12][0-9]{3})\\b')


def head_date5(i):
    """日期轨: 抬头整块走一条 “月名+空格+四位年” 正则(第二遍是相邻 token 对, 采集遍是另一条正则)"""
    m = MONRE.search(f5(NL.join(L[i][:22])))
    return (None, None) if m is None else (m.group(1), m.group(0))


MD = [head_date5(i) for i in range(NSRC)]
G['months'] = [m[0] for m in MD]
G['months_txt'] = [m[1] for m in MD]
G['years'] = [None if m[1] is None else int(m[1].split()[1]) for m in MD]
assert G['years'] == FLAT[u'years'], (G['years'], FLAT[u'years'])
G['year_span'] = max(G['years']) - min(G['years'])
G['year_inversions'] = len([(a, b) for a in range(NSRC) for b in range(NSRC)
                            if a < b and G['years'][a] > G['years'][b]])
G['year_order_lbl'] = u' ⇎ '.join(u'%s %d' % (LBL[i], G['years'][i]) for i in range(NSRC))
OBS = set(x for i in range(NSRC) for x in G['obs_ids'][i])
G['upd_target_obsoleted'] = [len([x for x in G['upd_ids'][i] if x in OBS]) for i in range(NSRC)]
JOINLBL = u' '.join(LBL)
G['obs_target_in_lib'] = [len([x for x in G['obs_ids'][i] if JOINLBL.find(x) >= 0])
                          for i in range(NSRC)]
G['obs_total'] = sum(len(x) for x in G['obs_ids'])
G['upd_total'] = sum(len(x) for x in G['upd_ids'])
G['lineage_no_edge'] = [i for i in range(NSRC) if not G['obs_ids'][i] and not G['upd_ids'][i]]
G['obs_raw_segs'] = [len(x) for x in G['obs_ids']]
G['obs_ids_clean'] = [[y for y in x if y] for x in G['obs_ids']]
G['obs_blank_segs'] = [G['obs_raw_segs'][i] - len(G['obs_ids_clean'][i]) for i in range(NSRC)]
G['lineage_close'] = (G['obs_total'] + G['upd_total'] - sum(G['obs_raw_segs'])
                      - sum(len(x) for x in G['upd_ids']))

# ---------- 节窗(本遍的标题识别是一条正则, 第二遍是 sect_no + lstrip 比对) ----------
RE_HD = re.compile(u'^(\\d+(?:\\.\\d+)*)(\\.?)[ \\t]+Idempotent(?: Request)? Methods$')
IDW = []
SECNO, SECHL, SECHN, SECTOC, SECBODY, ENDK, ENDH = [], [], [], [], [], [], []
for i in range(NSRC):
    hits = []
    for k, x in enumerate(L[i]):
        m = RE_HD.match(f5(x))
        if m is not None:
            hits.append((k, tuple(int(z) for z in m.group(1).split(u'.'))))
    if not hits:
        IDW.append(None); SECNO.append(None); SECHL.append(None); SECHN.append(0)
        SECTOC.append(None); SECBODY.append(None); ENDK.append(None); ENDH.append(None)
        continue
    k, tp = hits[-1]
    lvl = len(tp)
    nxt, end_kind = len(L[i]), u'eof'
    for j in range(k + 1, len(L[i])):
        tj, _ = sect5(f5(L[i][j]))
        if tj is None or len(tj) > lvl or tj < tp:
            continue
        nxt, end_kind = j, u'heading'
        break
    IDW.append(NL.join(L[i][k:nxt]))
    SECNO.append(u'.'.join(str(z) for z in tp))
    SECHL.append(L[i][k].strip())
    SECHN.append(len(hits))
    SECTOC.append(hits[0][0] + 1 if len(hits) > 1 else None)
    SECBODY.append(k + 1)
    ENDK.append(end_kind)
    ENDH.append(L[i][nxt].strip() if nxt < len(L[i]) else None)
G['sec_no'] = SECNO
G['sec_head_line'] = SECHL
G['sec_hit_n'] = SECHN
G['sec_toc_line'] = SECTOC
G['sec_body_line'] = SECBODY
G['sec_end_kind'] = ENDK
G['sec_end_head'] = ENDH
G['sec_end_head_fold'] = [f5(x) if x else None for x in ENDH]
G['sec_end_head_gap'] = [len(x) - len(f5(x)) if x else 0 for x in ENDH]
G['sec_found_n'] = len([x for x in SECNO if x])
G['sec_absent_n'] = NSRC - G['sec_found_n']
G['sec_lines'] = [x.count(NL) + 1 if x else 0 for x in IDW]
G['sec_chars'] = [len(x) if x else 0 for x in IDW]
G['sec_words'] = [w5(x) if x else 0 for x in IDW]


def sentcount5(s):
    """句数第二把尺: 逐字符扫 “.” 后跳空白落到大写/左括号/串尾(第二遍是 sent_ends 递归吃位)"""
    n, i, m = 0, 0, len(s)
    while i < m:
        j = s.find(u'.', i)
        if j < 0:
            return n
        k = j + 1
        while k < m and s[k] in u' \t\n':
            k += 1
        if k >= m or s[k].isupper() or s[k] == u'(':
            n += 1
            i = k
        else:
            i = j + 1
    return n


def dotspace5(s):
    """句数第一把尺的换档: 手工数 “. 后随空白” 的下标对(第二遍是 findall('\\.'+'\\s'))"""
    return len([j for j in range(len(s) - 1) if s[j] == u'.' and s[j + 1] in u' \t\n'])


G['sec_sents'] = [dotspace5(x) if x else 0 for x in IDW]
G['sec_sents_scan'] = [sentcount5(x) if x else 0 for x in IDW]
G['sec_sents_gap'] = [G['sec_sents'][i] - G['sec_sents_scan'][i] for i in range(NSRC)]
G['sec_row_dup'] = [G['sec_hit_n'][i] - (1 if SECNO[i] else 0) for i in range(NSRC)]
SECW = [f5(x) if x else u'' for x in IDW]
G['secw_chars'] = [len(x) for x in SECW]
G['sec_share_permille'] = [(1000 * G['sec_words'][i]) // w5(FOLD[i]) for i in range(NSRC)]
FACE = {u'strict': L, u'fold': FOLD, u'sh': SH, u'sec': SECW}
FACEI = {u'strict': 0, u'fold': 1, u'sh': 2, u'sec': 3}
FACES = [L, FOLD, SH, SECW]
WIDE = SH
TIERN = {0: u'strict', 1: u'fold', 2: u'sh', 3: u'sec'}

# ---------- 义务词阶梯 ----------
G['tone_fam'] = TONE
G['tone_norm'] = [[ub5(T[i], nd) for nd in TONE] for i in range(NSRC)]
G['tone_norm_fold'] = [[ub5(FOLD[i], nd) for nd in TONE] for i in range(NSRC)]
G['tone_straddle_k'] = [[G['tone_norm_fold'][i][k] - G['tone_norm'][i][k] for k in range(len(TONE))]
                        for i in range(NSRC)]
G['tone_straddle'] = [sum(x) for x in G['tone_straddle_k']]
G['tone_case'] = [[c5(LOWFOLD[i], nd.lower()) for nd in TONE] for i in range(NSRC)]
G['tone_case_gap'] = [sum(G['tone_case'][i]) - sum(G['tone_norm_fold'][i]) for i in range(NSRC)]
G['tone_sec'] = [[ub5(SECW[i], nd) for nd in TONE] if SECW[i] else [0] * len(TONE) for i in range(NSRC)]
G['tone_sec_tot'] = [sum(x) for x in G['tone_sec']]
G['tone_tot'] = [sum(x) for x in G['tone_norm']]
G['tone_fold_tot'] = [sum(x) for x in G['tone_norm_fold']]
G['tone_must_pure'] = [len([m for m in re.finditer(u'(?<![A-Za-z])MUST(?![A-Za-z])(?! NOT)', T[i])])
                       for i in range(NSRC)]
G['tone_must_ledger'] = [G['tone_norm'][i][1] - G['tone_norm'][i][0] - G['tone_must_pure'][i]
                         for i in range(NSRC)]
G['tone_word_lc'] = [[c5(LOWFOLD[i], w) for w in (u'must', u'should', u'may', u'can')]
                     for i in range(NSRC)]
G['tone_word_lc_tot'] = [sum(x) for x in G['tone_word_lc']]
G['tone_alnum_gap'] = [sum(ub5(T[i], nd, u'alpha') for nd in TONE)
                       - sum(ub5(T[i], nd, u'alnum') for nd in TONE) for i in range(NSRC)]
G['tone_ruler_close'] = sum(G['tone_alnum_gap'])
G['tone_wide'] = [[ub5(WIDE[i], nd) for nd in TONE] for i in range(NSRC)]
G['tone_wide_re'] = [[c5(WIDE[i], nd) for nd in TONE] for i in range(NSRC)]
G['tone_wide_close'] = sum(sum(abs(G['tone_wide'][i][k] - G['tone_wide_re'][i][k])
                               for k in range(len(TONE))) for i in range(NSRC))
G['tone_sec_per_mille'] = [(1000 * G['tone_sec_tot'][i]) // G['tone_tot'][i]
                           if G['tone_tot'][i] else -1 for i in range(NSRC)]
for i in range(NSRC):
    for k, nd in enumerate(TONE):
        assert G['tone_norm'][i][k] == mk_ub(T[i], nd), (i, nd)
        assert G['tone_wide'][i][k] == mk_ub(WIDE[i], nd)

# ---------- 答案句(段落 ⇎ 句界导出, 不手打) ----------
ANS = []
for i, pat in enumerate(ANS_HEAD):
    k = locate(T[i], pat)
    assert k >= 0, (i, pat)
    ln = len([c for c in T[i][:k] if c == NL])
    pl = []
    j = ln
    while j < len(L[i]) and L[i][j].strip() != u'':
        pl.append(j)
        j += 1
    txt, offs = u'', []
    for idx in pl:
        offs.append(len(txt))
        txt += (u'' if txt == u'' else u' ') + f5(L[i][idx])
    st = txt.find(pat)
    assert st >= 0, (i, pat)
    e = sentend5(txt[st + len(pat):])
    en = st + len(pat) + (e if e is not None else len(txt) - st - len(pat) - 1)
    cover = [kk for kk in range(len(pl)) if offs[kk] <= en and offs[kk] + len(f5(L[i][pl[kk]])) >= st]
    ANS.append(txt[st:en + 1])
    G.setdefault(u'ans_span', []).append(len(cover))
    G.setdefault(u'ans_first_line', []).append(ln)
    G.setdefault(u'ans_para_span', []).append(len(pl))
    G.setdefault(u'ans_lead_words', []).append(
        w5(f5(L[i][ln])[:f5(L[i][ln]).find(pat)]) if pat in f5(L[i][ln]) else 0)
    G.setdefault(u'ans_lines_abs', []).append([pl[kk] + 1 for kk in range(len(cover))])
G['ans'] = ANS
G['ans_words'] = [w5(x) for x in ANS]
G['ans_one_line_n'] = len([x for x in G['ans_span'] if x == 1])
G['ans_page_break'] = [len([y for y in G['ans_lines_abs'][i] if mk_is_pg(L[i][y - 1])])
                      for i in range(NSRC)]
G['ans_para_tail'] = [G['ans_para_span'][i] - G['ans_span'][i] for i in range(NSRC)]
G['ans_ph'] = ANS_PH
for i in range(NSRC):
    nd = ANS_PH[i].lower().replace(NL, u' ')
    G.setdefault(u'ph_line', []).append(sum(c5(y.lower(), nd) for y in L[i]))
    G.setdefault(u'ph_fold', []).append(c5(LOWFOLD[i], nd))
G['ph_line'] = G[u'ph_line']
G['ph_fold'] = G[u'ph_fold']
G['ph_straddle'] = [G['ph_fold'][i] - G['ph_line'][i] for i in range(NSRC)]
G['ph_raw_line'] = [len([y for y in L[i] if ANS_PH[i] in y]) for i in range(NSRC)]

# ---------- “重来”用词族 ⇎ 判词施事者 ----------
RALT5 = re.compile(u'|'.join(re.escape(x) for x in sorted(REWORD, key=lambda s: -len(s))))
ALT5 = re.compile(u'|'.join(re.escape(x) for x in sorted(AUTOFAM, key=lambda s: -len(s))))
G['reword_fam'] = REWORD
G['reword'] = [[c5(LOWFOLD[i], nd.lower()) for nd in REWORD] for i in range(NSRC)]
G['reword_union'] = [len(RALT5.findall(LOWFOLD[i])) for i in range(NSRC)]
G['reword_overlap'] = [sum(G['reword'][i]) - G['reword_union'][i] for i in range(NSRC)]
G['reword_tot'] = [sum(x) for x in G['reword']]
G['reword_zero_n'] = [len([k for k in range(len(REWORD)) if G['reword'][i][k] == 0])
                      for i in range(NSRC)]
G['reword_own'] = [[REWORD[k] for k in range(len(REWORD)) if G['reword'][i][k]
                    and all(G['reword'][j][k] == 0 for j in range(NSRC) if j != i)]
                   for i in range(NSRC)]
G['auto_fam'] = AUTOFAM
G['auto_line'] = [[sum(c5(y, nd) for y in LOW[i]) for nd in AUTOFAM] for i in range(NSRC)]
G['auto_line_rows'] = [[len([y for y in LOW[i] if nd in y]) for nd in AUTOFAM] for i in range(NSRC)]
G['auto_fold'] = [[c5(LOWFOLD[i], nd) for nd in AUTOFAM] for i in range(NSRC)]
G['auto_union_fold'] = [len(ALT5.findall(LOWFOLD[i])) for i in range(NSRC)]
G['auto_fam_overlap'] = [sum(G['auto_fold'][i]) - G['auto_union_fold'][i] for i in range(NSRC)]
G['auto_gain'] = [sum(G['auto_fold'][i]) - sum(G['auto_line'][i]) for i in range(NSRC)]
G['auto_tot_line'] = [sum(G['auto_line'][i]) for i in range(NSRC)]
G['auto_tot_fold'] = [sum(G['auto_fold'][i]) for i in range(NSRC)]
G['auto_bare'] = [c5(LOWFOLD[i], u'automatic') for i in range(NSRC)]
G['auto_bare_line'] = [sum(c5(y, u'automatic') for y in LOW[i]) for i in range(NSRC)]
G['auto_sh'] = [[c5(SH[i].lower(), nd) for nd in AUTOFAM] for i in range(NSRC)]
G['auto_sh_minus_fold'] = [sum(G['auto_sh'][i]) - sum(G['auto_fold'][i]) for i in range(NSRC)]
G['auto_bare_minus_union'] = [G['auto_bare'][i] - G['auto_union_fold'][i] for i in range(NSRC)]
G['auto_occ_rows'] = [sum(len([y for y in LOW[i] if nd in y]) for nd in AUTOFAM) for i in range(NSRC)]
G['auto_rows_minus_occ'] = [G['auto_occ_rows'][i] - sum(G['auto_line'][i]) for i in range(NSRC)]
PASSIVE = 8
G['subj_fam'] = SUBJ
G['subj'] = [[c5(FOLD[i], nd.replace(NL, u' ')) for nd in SUBJ] for i in range(NSRC)]
G['subj_line'] = [[sum(c5(y, nd) for y in L[i]) for nd in SUBJ] for i in range(NSRC)]
G['subj_straddle'] = [sum(G['subj'][i]) - sum(G['subj_line'][i]) for i in range(NSRC)]
G['subj_n'] = [len([k for k in range(len(SUBJ)) if G['subj'][i][k]]) for i in range(NSRC)]
G['subj_active'] = [sum(G['subj'][i][:PASSIVE]) for i in range(NSRC)]
G['subj_passive'] = [G['subj'][i][PASSIVE] for i in range(NSRC)]
G['subj_sec'] = [[c5(SECW[i], nd.replace(NL, u' ')) for nd in SUBJ] if SECW[i] else [0] * len(SUBJ)
                 for i in range(NSRC)]
G['subj_sec_tot'] = [sum(x) for x in G['subj_sec']]
G['subj_straddle_k'] = [[G['subj'][i][kk] - G['subj_line'][i][kk] for kk in range(len(SUBJ))]
                        for i in range(NSRC)]
G['subj_straddled'] = [[SUBJ[kk] for kk in range(len(SUBJ)) if G['subj_straddle_k'][i][kk]]
                       for i in range(NSRC)]
G['act_fam'] = ACT
G['act'] = [[c5(LOWFOLD[i], nd) for nd in ACT] for i in range(NSRC)]
G['act_sg'] = [len(re.findall(u'user agent(?!s)', LOWFOLD[i])) for i in range(NSRC)]
G['act_sg_plus_pl'] = [G['act_sg'][i] + G['act'][i][1] - G['act'][i][0] for i in range(NSRC)]
G['act_sec'] = [[c5(SECW[i].lower(), nd) for nd in ACT] if SECW[i] else [0] * len(ACT)
                for i in range(NSRC)]
G['act_sec_tot'] = [sum(x) for x in G['act_sec']]
G['act_tot'] = [sum(x) for x in G['act']]
G['num_fam'] = NUM
G['num'] = [[ub5(LOWFOLD[i], nd.lower(), bd5(nd)) for nd in NUM] for i in range(NSRC)]
G['num_raw'] = [[c5(LOWFOLD[i], nd.lower()) for nd in NUM] for i in range(NSRC)]
G['num_sub'] = [sum(G['num_raw'][i]) - sum(G['num'][i]) for i in range(NSRC)]
G['num_tot'] = [sum(x) for x in G['num']]
G['num_own'] = [[NUM[k] for k in range(len(NUM)) if G['num'][i][k]
                 and all(G['num'][j][k] == 0 for j in range(NSRC) if j != i)] for i in range(NSRC)]
G['num_rename'] = [G['num'][i][4] - G['num'][i][5] for i in range(NSRC)]
G['meth_fam'] = METH
G['meth_sec'] = [[ub5(SECW[i], nd) for nd in METH] if SECW[i] else [0] * len(METH) for i in range(NSRC)]
G['meth_sec_n'] = [len([x for x in G['meth_sec'][i] if x]) for i in range(NSRC)]
G['meth_post_sec'] = [G['meth_sec'][i][4] for i in range(NSRC)]
G['meth_all'] = [[ub5(WIDE[i], nd) for nd in METH] for i in range(NSRC)]
G['meth_all_n'] = [len([x for x in G['meth_all'][i] if x]) for i in range(NSRC)]

# ---------- Retry-After 轴 ⇎ 反向对照 ⇎ 状态码 ⇎ 括号印法 ----------
G['ra_count'] = [c5(T[i], u'Retry-After') for i in range(NSRC)]
RABLINE = [[x for x in L[i] if abnf5(x)] for i in range(NSRC)]
G['ra_abnf_lines'] = [len(x) for x in RABLINE]
G['ra_abnf_forms'] = [len(set(f5(x) for x in RABLINE[i])) for i in range(NSRC)]
G['ra_abnf_bar'] = [len([x for x in RABLINE[i] if u'|' in x]) for i in range(NSRC)]
G['ra_abnf_slash'] = [len([x for x in RABLINE[i] if u' / ' in x]) for i in range(NSRC)]
G['ra_abnf_quoted'] = [len([x for x in RABLINE[i] if u'"Retry-After"' in x]) for i in range(NSRC)]
G['ra_abnf_ledger'] = [G['ra_abnf_bar'][i] + G['ra_abnf_slash'][i] - G['ra_abnf_lines'][i]
                       for i in range(NSRC)]
G['ra_exp_date'] = [c5(T[i], u'Retry-After: Fri, 31 Dec 1999 23:59:59 GMT') for i in range(NSRC)]
G['ra_exp_120'] = [c5(T[i], u'Retry-After: 120') for i in range(NSRC)]
G['ra_exp_3600'] = [c5(T[i], u'Retry-After: 3600') for i in range(NSRC)]
G['ra_two_minutes'] = [c5(LOWFOLD[i], u'the delay is 2 minutes') for i in range(NSRC)]
G['ra_delta_def'] = [c5(LOWFOLD[i], u'non-negative decimal integer') for i in range(NSRC)]
G['ra_colon_rows'] = [len([x for x in L[i] if f5(x).startswith(u'Retry-After:')]) for i in range(NSRC)]
G['neg_fam'] = NEG
G['neg_digit'] = [k for k, nd in enumerate(NEG) if nd.isdigit()]
G['neg_raw'] = [[c5(T[i], nd) for nd in NEG] for i in range(NSRC)]
G['neg_bnd'] = [[ub5(T[i], nd, bd5(nd)) for nd in NEG] for i in range(NSRC)]
G['neg_false_sub'] = [sum(G['neg_raw'][i]) - sum(G['neg_bnd'][i]) for i in range(NSRC)]
G['neg_zero_n'] = [len([k for k in range(len(NEG)) if G['neg_bnd'][i][k] == 0]) for i in range(NSRC)]
G['neg_own'] = [[k for k in range(len(NEG)) if G['neg_bnd'][i][k]
                 and all(G['neg_bnd'][j][k] == 0 for j in range(NSRC) if j != i)]
                for i in range(NSRC)]
G['neg_own_lbl'] = [[NEG[k] for k in G['neg_own'][i]] for i in range(NSRC)]
G['neg_tot'] = [sum(x) for x in G['neg_bnd']]
G['code_fam'] = CODES
for i in range(NSRC):
    for c in CODES:
        assert [x for x in L[i] if code5(x, c)] == [x for x in L[i] if mk_code_row(x, c)], (i, c)
CODES_I = [[[x for x in L[i] if code5(x, c)] for c in CODES] for i in range(NSRC)]
G['code_defined_raw'] = [len([y for rows in CODES_I[i] for y in rows]) for i in range(NSRC)]
G['code_defined'] = [[len([y for y in rows if u'...' not in y]) for rows in CODES_I[i]]
                     for i in range(NSRC)]
G['code_defined_n'] = [sum(x) for x in G['code_defined']]
G['code_toc'] = [G['code_defined_raw'][i] - G['code_defined_n'][i] for i in range(NSRC)]
G['code_defined_lbl'] = [[CODES[k] for k in range(len(CODES)) if G['code_defined'][i][k]]
                         for i in range(NSRC)]
G['code_absent_lbl'] = [[CODES[k] for k in range(len(CODES)) if not G['code_defined'][i][k]]
                        for i in range(NSRC)]
G['paren_fam'] = PAREN
G['paren'] = [[c5(FOLD[i], nd) for nd in PAREN] for i in range(NSRC)]
G['paren_line'] = [[sum(c5(y, nd) for y in L[i]) for nd in PAREN] for i in range(NSRC)]
G['paren_straddle'] = [sum(G['paren'][i]) - sum(G['paren_line'][i]) for i in range(NSRC)]

# ---------- 逐字搬字: 行尺池 ⇎ 配对 ⇎ 归属分档 ----------
POOL = [[f5(x) for x in L[i] if len(x.strip()) >= 30 and not mk_is_pick(x)] for i in range(NSRC)]
PAIRS = [(a, b) for a, b in IT.combinations(range(NSRC), 2)]
PS = [set(p) for p in POOL]
P2 = {}
for a, b in PAIRS:
    P2[u'%s-%s' % (LBL[a], LBL[b])] = len([k for k in PS[a] if k in PS[b]])
G['pair_shared'] = P2
G['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
G['pair_share'] = [P2[u'%s-%s' % (LBL[a], LBL[b])] for a, b in PAIRS]
G['pair_nonzero'] = len([x for x in G['pair_share'] if x])
G['pair_zero'] = len(PAIRS) - G['pair_nonzero']
_mx, _mi = -1, None
for n, (a, b) in enumerate(PAIRS):
    if P2[u'%s-%s' % (LBL[a], LBL[b])] > _mx:
        _mx, _mi = P2[u'%s-%s' % (LBL[a], LBL[b])], u'%s-%s' % (LBL[a], LBL[b])
G['pair_max_lbl'] = _mi
G['pair_max'] = _mx
ML = _mi.split(u'-')
G['pair_lbl_idx'] = [LBL.index(ML[0]), LBL.index(ML[1])]
BA, BB = G['pair_lbl_idx']
ORIG = [defaultdict(set) for _ in range(NSRC)]
for i in range(NSRC):
    for x in L[i]:
        if len(x.strip()) >= 30 and not mk_is_pick(x):
            ORIG[i][f5(x)].add(x)
G['pair_max_byte_keys'] = len([k for k in ORIG[BA] if k in ORIG[BB] and (ORIG[BA][k] & ORIG[BB][k])])
G['pair_max_norm_only_keys'] = len([k for k in ORIG[BA] if k in ORIG[BB]
                                    and not (ORIG[BA][k] & ORIG[BB][k])])
RA_W = set(x for x in L[BA] if len(x.strip()) >= 30)
RB_W = set(x for x in L[BB] if len(x.strip()) >= 30)
G['pair_max_byte_lines'] = len([x for x in RB_W if x in RA_W])
G['pair_max_norm_only_lines'] = G['pair_max'] - G['pair_max_byte_lines']
G['pair_byte_lines_to_keys'] = len(set(f5(x) for x in [y for y in RA_W if y in RB_W]))
G['pair_byte_unit_gap'] = G['pair_max_byte_lines'] - G['pair_byte_lines_to_keys']
G['pair_byte_shell_gap'] = G['pair_byte_lines_to_keys'] - G['pair_max_byte_keys']
G['pair_byte_lines_ge_keys'] = 1 if G['pair_max_byte_lines'] >= G['pair_max_byte_keys'] else 0
G['pool_n'] = sum(len(x) for x in POOL)
G['pool_union'] = len(set().union(*PS))
G['pool_rows_minus_union'] = G['pool_n'] - G['pool_union']
UN = set().union(*PS)
PRES = dict((a, tuple(i for i in range(NSRC) if a in PS[i])) for a in UN)
_hist = Counter(len(v) for v in PRES.values())
G['pool_tier'] = [_hist.get(k, 0) for k in range(1, NSRC + 1)]
G['pool_tier_close'] = sum(G['pool_tier']) - G['pool_union']
# 容斥走“对文档下标的组合逐枚求交”(第二遍是 C(len(v),k) 逐元算式)
_incl = []
for kk in range(1, NSRC + 1):
    _incl.append(sum(len(set.intersection(*[PS[t] for t in cmb]))
                     for cmb in IT.combinations(range(NSRC), kk)))
G['pool_incl'] = _incl
G['union_incl'] = sum((-1) ** (kk + 1) * _incl[kk - 1] for kk in range(1, NSRC + 1))
G['union_close'] = G['pool_union'] - G['union_incl']
G['pair_byte'] = [len([k for k in ORIG[a] if k in ORIG[b] and (ORIG[a][k] & ORIG[b][k])])
                  for a, b in PAIRS]
G['pair_norm_only'] = [len([k for k in ORIG[a] if k in ORIG[b] and not (ORIG[a][k] & ORIG[b][k])])
                       for a, b in PAIRS]
G['pair_close'] = sum(G['pair_share']) - sum(G['pair_byte']) - sum(G['pair_norm_only'])
G['pair_7231_9110'] = G['pair_share'][PAIRS.index((1, 4))]
G['pair_2616_9110'] = G['pair_share'][PAIRS.index((0, 4))]
G['pair_2616_7231'] = G['pair_share'][PAIRS.index((0, 1))]

# ---------- 分家四桶 ----------
def bucket5(o, p):
    """归一因由四桶: 本遍用 dh5 ⇎ p5 ⇎ 逐字符扫, 与第二遍的 bucket 逐对对拍"""
    if o.lower() == p.lower():
        return u'case'
    if dh5(o) == dh5(p):
        return u'hyph'
    if o.strip() == p.strip():
        return u'space'
    return u'multi'

axis = dict((w, 0) for w in RANK)
NORM_ONLY, BSAME = [], []
VAR = {}
for a in sorted(PS[BA] & PS[BB]):
    va, vb = ORIG[BA][a], ORIG[BB][a]
    VAR[a] = (va, vb)
    if va & vb:
        BSAME.append(a)
        continue
    NORM_ONLY.append(a)
    dif = [(o, q) for o in va for q in vb]
    _b = None
    for o, q in dif:
        w = bucket5(o, q)
        if _b is None or RANK[w] < RANK[_b]:
            _b = w
    axis[_b] += 1
G['axis_counts'] = axis
G['axis_total'] = sum(axis.values())
G['axis_rows'] = NORM_ONLY
G['pair_pool_byte'] = len(BSAME)
G['pair_pool_norm_only'] = len(NORM_ONLY)
G['axis_close'] = (G['pair_max'] - G['pair_pool_byte'] - G['pair_pool_norm_only']
                   + abs(G['pair_max_byte_keys'] - G['pair_pool_byte'])
                   + abs(G['pair_max_norm_only_keys'] - G['pair_pool_norm_only']))
G['axis_str'] = u' ⇎ '.join(u'%s%d' % (w, axis[w]) for w in (u'case', u'hyph', u'space', u'multi'))
G['axis_str_n'] = len([w for w in axis if axis[w]])




for a in NORM_ONLY:
    va, vb = VAR[a]
    assert min((bucket5(o, q) for o, q in [(x, y) for x in va for y in vb]),
               key=lambda w: RANK[w]) == min((mk_bucket(o, q) for o, q in [(x, y) for x in va for y in vb]),
                                             key=lambda w: RANK[w]), a

# ---------- 句尺 ----------
SP = [set(x for x in sents5(WIDE[i]) if len(x) >= 40) for i in range(NSRC)]
for i in range(NSRC):
    assert SP[i] == set(x for x in mk_sents(WIDE[i]) if len(x) >= 40), i
SPRES = dict((a, tuple(i for i in range(NSRC) if a in SP[i])) for s in SP for a in s)
G['s_pool_n'] = len(SPRES)
_sh = Counter(len(v) for v in SPRES.values())
G['s_pool_tier'] = [_sh.get(k, 0) for k in range(1, NSRC + 1)]
G['s_pool_tier_close'] = sum(G['s_pool_tier']) - G['s_pool_n']
G['s_pair_share'] = [len(SP[a] & SP[b]) for a, b in PAIRS]
G['s_pair_max'] = max(G['s_pair_share'])
G['s_pair_max_idx'] = G['s_pair_share'].index(G['s_pair_max'])
G['s_pair_max_lbl'] = G['pair_lbl'][G['s_pair_max_idx']]
G['s_pair_7231_9110'] = G['s_pair_share'][PAIRS.index((1, 4))]
G['s_pair_2616_9110'] = G['s_pair_share'][PAIRS.index((0, 4))]
G['s_ruler_gain_7231_9110'] = G['s_pair_7231_9110'] - G['pair_7231_9110']
G['s_ruler_gain_2616_9110'] = G['s_pair_2616_9110'] - G['pair_2616_9110']
G['s_pair_nonzero'] = len([x for x in G['s_pair_share'] if x])
_s1 = sum(len(SP[i]) for i in range(NSRC))
_sin = []
for kk in range(1, NSRC + 1):
    _sin.append(sum(len(set.intersection(*[SP[t] for t in cmb]))
                    for cmb in IT.combinations(range(NSRC), kk)))
G['s_incl'] = [_s1] + _sin[1:]
G['s_union_incl'] = sum((-1) ** (kk + 1) * G['s_incl'][kk - 1] for kk in range(1, NSRC + 1))
G['s_union_close'] = G['s_pool_n'] - G['s_union_incl']

# ---------- 锚候选池 ----------
apool = []
for i in range(NSRC):
    for x in SHP[i]:
        if len(p5(x)) >= 24 and len([c for c in x if c.isalpha()]):
            apool.append((p5(x), i))
AP = defaultdict(set)
for a, i in apool:
    AP[a].add(i)
G['apool_n'] = len(AP)
G['apool_raw_n'] = len(apool)
G['apool_face_raw'] = [len([1 for a, k in apool if k == i]) for i in range(NSRC)]
G['apool_tag_n'] = [len([a for a, v in AP.items() if i in v]) for i in range(NSRC)]
G['apool_dup'] = [G['apool_face_raw'][i] - G['apool_tag_n'][i] for i in range(NSRC)]
G['apool_tag_close'] = sum(G['apool_tag_n']) + sum(G['apool_dup']) - G['apool_raw_n']
_ath = Counter(len(v) for v in AP.values())
G['apool_tier'] = [_ath.get(n, 0) for n in range(1, NSRC + 1)]
G['apool_weight'] = sum(G['apool_tier'][n] * (n + 1) for n in range(NSRC))
G['apool_pairs'] = sum(G['apool_tag_n'])
G['apool_tier_close'] = G['apool_weight'] - G['apool_pairs']
G['apool_maxlen'] = max(len(a) for a in AP)

# ---------- 序列化式子 ----------
HF = [[hdrform5(x) for x in L[i]] for i in range(NSRC)]
G['hdr_dot2sp'] = [len([1 for h in HF[i] if h == u'dot2sp']) for i in range(NSRC)]
G['hdr_dot1sp'] = [len([1 for h in HF[i] if h == u'dot1sp']) for i in range(NSRC)]
G['hdr_nodot'] = [len([1 for h in HF[i] if h == u'nodot']) for i in range(NSRC)]
G['dblspace_in_fold'] = [c5(FOLD[i], u'  ') for i in range(NSRC)]


def dotsp2(s):
    out, k, m = 0, 0, len(s)
    while k + 3 < m:
        if (not s[k].isspace() and s[k + 1] == u'.' and s[k + 2: k + 4] == u'  '
                and not s[k + 4].isspace()):
            out += 1
            k += 5
            continue
        k += 1
    return out


G['dot_dblspace_anywhere'] = [dotsp2(FOLD[i]) for i in range(NSRC)]
for i in range(NSRC):
    assert G['dot_dblspace_anywhere'][i] == len(re.findall(u'\\S\\.  \\S', FOLD[i])), i


def hypbreak(i):
    n = 0
    for j in range(len(L[i]) - 1):
        s = L[i][j].rstrip()
        t = L[i][j + 1]
        if s.endswith(u'-') and (t.lstrip(u' \t')[:1].islower()):
            n += 1
    return n


G['hyphen_break'] = [hypbreak(i) for i in range(NSRC)]
G['hyb_idem'] = [c5(T[i], u'non-' + NL + u'idempotent') for i in range(NSRC)]
G['idem_str'] = [c5(LOWFOLD[i], u'idempotent') for i in range(NSRC)]
G['idem_line_occ'] = [sum(c5(y, u'idempotent') for y in LOW[i]) for i in range(NSRC)]
G['idem_line_rows'] = [len([y for y in LOW[i] if u'idempotent' in y]) for i in range(NSRC)]
G['idem_hyb_line'] = [sum(c5(y, u'non-idempotent') for y in LOW[i]) for i in range(NSRC)]
G['idem_hyb_fold'] = [c5(LOWFOLD[i], u'non-idempotent') for i in range(NSRC)]
G['hyb_straddle'] = [G['idem_hyb_fold'][i] - G['idem_hyb_line'][i] for i in range(NSRC)]
G['idem_row_minus_occ'] = [G['idem_line_occ'][i] - G['idem_line_rows'][i] for i in range(NSRC)]

# ---------- 锚句: 由起止针在指定面上导出 ----------
def mk_nd5(o, s0, e0, fa):
    if s0.startswith(u'@'):
        return s0[1:]
    face = FACE[fa][o]
    a = locate(face, s0)
    assert a >= 0, (u'起针落空', LBL[o], fa, s0)
    if not e0:
        return s0
    b = locate(face, e0, a)
    assert b >= 0, (u'止针落空', LBL[o], fa, e0)
    return face[a:b + len(e0)]


TEXT = {}
NEGND = [k for o, k, fa, s0, e0 in SENT if s0.startswith(u'@')]
for (o, k, fa, s0, e0) in SENT:
    TEXT[k] = s0[1:] if k in NEGND else mk_nd5(o, s0, e0, fa)
OWNER = dict((k, o) for o, k, _, _, _ in SENT)
GN = [k for o, k, _, _, _ in SENT]
assert TEXT == CH[u'litk'], sorted([k for k in TEXT if TEXT[k] != CH[u'litk'].get(k)])[:3]


def hit5(k, tier):
    nd = TEXT[k]
    o = OWNER[k]
    if not nd:
        return 0
    if tier == 0:
        return len([x for x in L[o] if nd in x])
    face = FACE[TIERN[tier]][o]
    return c5(face, nd)


SN = dict((k, [hit5(k, n) for n in range(4)]) for k in GN)
for k in GN:
    for n in (1, 2, 3):
        assert SN[k][n] == mk_cnt_re(FACE[TIERN[n]][OWNER[k]], TEXT[k]), (k, n)
G['needle_n'] = len(GN)
G['neg_n'] = len(NEGND)
for n in range(4):
    G[u'sn_' + TIERN[n] + u'_docs'] = [len([k for k in GN if OWNER[k] == i and SN[k][n]])
                                       for i in range(NSRC)]
for k in GN:
    G[u'n_' + k] = SN[k]
G['needles_owned'] = [len([k for k in GN if OWNER[k] == i]) for i in range(NSRC)]
G['fold_minus_strict_keys'] = [k for k in GN if not SN[k][0] and SN[k][1]]
G['fold_minus_strict_own'] = [len([k for k in G['fold_minus_strict_keys'] if OWNER[k] == i])
                              for i in range(NSRC)]
G['fold_minus_strict_n'] = len(G['fold_minus_strict_keys'])
G['sh_loses_keys'] = [k for k in GN if SN[k][1] and not SN[k][2]]
G['sh_gains_keys'] = [k for k in GN if SN[k][2] and not SN[k][1]]
G['sh_loses'] = [len([k for k in G['sh_loses_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['sh_gains'] = [len([k for k in G['sh_gains_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['sec_scope'] = [1 if SECW[i] else 0 for i in range(NSRC)]
G['sh_no_sec_keys'] = [k for k in GN if SN[k][2] and not SN[k][3] and G['sec_scope'][OWNER[k]]]
G['sh_no_sec_own'] = [len([k for k in G['sh_no_sec_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['sh_no_sec_n'] = len(G['sh_no_sec_keys'])
G['sn_sec_docs_scope'] = [G['sn_sec_docs'][i] if SECW[i] else -1 for i in range(NSRC)]
G['dead_needles'] = [k for k in GN if k not in NEGND and max(SN[k]) == 0]
G['neg_controls'] = sorted(NEGND)
G['neg_own_nd'] = [len([k for k in NEGND if OWNER[k] == i]) for i in range(NSRC)]
G['neg_hit_widest'] = sum(max(SN[k]) for k in NEGND)
G['neg_hit_strict'] = sum(SN[k][0] for k in NEGND)
G['strict_neg_own'] = [len([k for k in NEGND if OWNER[k] == i and SN[k][0]]) for i in range(NSRC)]
G['fold_neg_own'] = [len([k for k in NEGND if OWNER[k] == i and SN[k][1]]) for i in range(NSRC)]
G['ladder_close'] = sum(
    abs(G['sn_strict_docs'][i] + G['fold_minus_strict_own'][i] + G['strict_neg_own'][i]
        - G['sn_fold_docs'][i] - G['fold_neg_own'][i])
    + abs(G['sn_fold_docs'][i] - G['sh_loses'][i] + G['sh_gains'][i] - G['sn_sh_docs'][i])
    + (0 if not SECW[i] else
       abs(G['sn_sh_docs'][i] - G['sh_no_sec_own'][i] - G['sn_sec_docs'][i]))
    for i in range(NSRC))
G['ladder_monotone'] = 1 if all(G['sn_strict_docs'][i] <= G['sn_fold_docs'][i]
                                and G['sn_sec_docs'][i] <= G['sn_sh_docs'][i]
                                for i in range(NSRC)) else 0
G['overlap_extra'] = sum(o5(WIDE[OWNER[k]], TEXT[k]) - c5(WIDE[OWNER[k]], TEXT[k])
                         for k in GN if TEXT[k] and k not in NEGND)
G['re_eq_cur'] = 1 if all(r5(FACES[n][OWNER[k]], TEXT[k]) == c5(FACES[n][OWNER[k]], TEXT[k])
                          for k in GN if TEXT[k] and k not in NEGND for n in range(1, 3)) else 0
G['nd_len'] = [len(TEXT[k]) for k in GN]
G['nd_len_tot'] = sum(G['nd_len'])
G['nd_len_max'] = max(G['nd_len'])
G['idem_sent_same'] = 1 if TEXT[u'a7231_idem'] == TEXT[u'a9110_idem'] else 0
G['idem_line_7231'] = len([c for c in T[1][:locate(T[1], u'Idempotent methods are distinguished')]
                           if c == NL]) + 1
G['idem_line_9110'] = len([c for c in T[4][:locate(T[4], u'Idempotent methods are distinguished')]
                           if c == NL]) + 1
G['idem_shift'] = G['idem_line_9110'] - G['idem_line_7231']
G['idem_wrap_7231'] = len([y for y in L[1] if u'Idempotent methods are distinguished' in y])
G['idem_wrap_9110'] = len([y for y in L[4] if u'Idempotent methods are distinguished' in y])
G['like_sent_same'] = 1 if TEXT[u'a7231_like'] == TEXT[u'a9110_like'] else 0
G['like_line_7231'] = len([j + 1 for j, y in enumerate(L[1]) if u'Like the definition of safe' in y])
G['like_abs_7231'] = [j + 1 for j, y in enumerate(L[1]) if u'Like the definition of safe' in y][0]
G['like_abs_9110'] = [j + 1 for j, y in enumerate(L[4]) if u'Like the definition of safe' in y][0]
G['like_shift'] = G['like_abs_9110'] - G['like_abs_7231']
G['like_hit_sh'] = [SN[u'a7231_like'][2], SN[u'a9110_like'][2]]
G['like_absent_2616'] = c5(SH[0], TEXT[u'a7231_like'])
G['defin_absent_7231'] = c5(FOLD[1], TEXT[u'a2616_defin'])
G['nonidem_straddle'] = SN[u'a2616_nonidem']
G['sidefx_in_sec'] = SN[u'a2616_sidefx'][3]
VKEY = [u'a2616_passive', u'a2616_repeat', u'a2616_confirm']
G['v_keys'] = VKEY
G['v_in_sh'] = len([k for k in VKEY if SN[k][2]])
G['v_in_sec'] = len([k for k in VKEY if SN[k][3]])
G['v_sh_no_sec'] = len([k for k in VKEY if k in G['sh_no_sec_keys']])
G['defin_in_sec'] = SN[u'a2616_defin'][3]
G['defin_in_sh'] = SN[u'a2616_defin'][2]
G['xref_line'] = len([1 for y in L[0] if u'see section 9.1.2' in y])
XREF = [j + 1 for j, y in enumerate(L[0]) if u'see section 9.1.2' in y]
G['xref_lines_abs'] = XREF
G['xref_to_head'] = [G['sec_body_line'][0] - z for z in XREF]
G['verdict_lines_abs'] = [j + 1 for j, y in enumerate(L[0])
                          if u'Non-idempotent methods or sequences' in y]
G['verdict_head_gap'] = G['sec_body_line'][0] - G['verdict_lines_abs'][0]
G['verdict_xref_same_line'] = 1 if all(any(v == z for z in XREF)
                                       for v in G['verdict_lines_abs']) else 0
K9 = [k for k in GN if OWNER[k] == 4 and k not in NEGND]
G['k9110_in_sec'] = len([k for k in K9 if SN[k][3]])
G['k9110_tot'] = len(K9)
G['k9110_no_sec'] = len([k for k in K9 if SN[k][2] and not SN[k][3]])
assert G['dead_needles'] == FLAT[u'dead_needles'] and G['neg_controls'] == FLAT[u'neg_controls']
assert G['ans'] == FLAT[u'ans'] and G['sec_no'] == FLAT[u'sec_no']

# ---------- 段窗层(SCAN2): 行号映射走 bisect, 段界定位走编译针的 search ----------
SHPN = []
for i in range(NSRC):
    _sh = []
    for n in range(len(L[i])):
        if not mk_is_pick(L[i][n]):
            _sh.append((n + 1, L[i][n]))
    SHPN.append(_sh)
PP = []
for i in range(NSRC):
    PP.append([(n, u' '.join(x.split())) for n, x in SHPN[i]])
    PP[i] = [p for p in PP[i] if p[1] != u'']
for i in range(NSRC):
    assert [x for _, x in SHPN[i]] == SHP[i], i
    assert u' '.join(x for _, x in PP[i]) == WIDE[i], i
def _map(i):
    """偏移→原行号的对照表: 本遍把“片段之间的一个空格”累加成显式数组(第二遍在查表时现算)"""
    offs, lns, acc, first = [], [], 0, True
    for ln, s in PP[i]:
        if not first:
            acc += 1
        first = False
        offs.append(acc)
        lns.append(ln)
        acc += len(s)
    return offs, lns


MAPS = [_map(i) for i in range(NSRC)]


def line_of5(i, a):
    return MAPS[i][1][bisect.bisect_right(MAPS[i][0], a) - 1]


G['pp_rows'] = [len(x) for x in PP]
G['pp_gap_rows'] = [G['nonblank'][i] - G['pp_rows'][i] for i in range(NSRC)]
ALN = SHPN
ANSET = [set(x for _, x in ALN[i]) for i in range(NSRC)]
ALND = [dict(ALN[i]) for i in range(NSRC)]
FAN = [p5(t) for t in T]
for i in range(NSRC):
    assert FAN[i] == mk_pnorm(T[i]), i
    assert len(ALND[i]) == len(ALN[i]), i


def blk5(i, start, end):
    a = locate(WIDE[i], start)
    assert a >= 0, (LBL[i], start)
    b = locate(WIDE[i], end, a)
    assert b >= 0, (LBL[i], end)
    e = b + len(end)
    return u' '.join(WIDE[i][a:e].split()), line_of5(i, a), line_of5(i, e - 1)


def ln_of5(i, nd, frm=0):
    a = locate(WIDE[i], nd, frm)
    assert a >= 0, (LBL[i], nd)
    return a, line_of5(i, a)


def ln_end5(i, nd, frm=0):
    a = locate(WIDE[i], nd, frm)
    assert a >= 0, (LBL[i], nd)
    return a, line_of5(i, a + len(nd) - 1)


def line_holds5(i, ln, nd):
    return 1 if p5(nd) in p5(ALND[i][ln]) else 0


PB = [blk5(i, s, e) for i, s, e in PINS]
PTXT = [p[0] for p in PB]
G['blk_lo'] = [p[1] for p in PB]
G['blk_hi'] = [p[2] for p in PB]
G['blk_rows'] = [p[2] - p[1] + 1 for p in PB]
G['blk_chars'] = [len(p[0]) for p in PB]
G['blk_words'] = [w5(p[0]) for p in PB]
PW = [p[0].lower().split() for p in PB]
G['blk_vocab'] = [len(set(x)) for x in PW]
G['blk_five_chars'] = sum(G['blk_chars'][:5])
G['blk_five_words'] = sum(G['blk_words'][:5])
G['blk_rows_tot'] = sum(G['blk_rows'])
G['blk_words_tot'] = sum(G['blk_words'])
G['blk_five_rows'] = sum(G['blk_rows'][:5])
G['tone_must_blk'] = [ub5(p, u'MUST') for p in PTXT]
G['tone_may_blk'] = [ub5(p, u'MAY') for p in PTXT]
G['tone_should_blk'] = [ub5(p, u'SHOULD') for p in PTXT]
G['tone_mustnot_blk'] = [ub5(p, u'MUST NOT') for p in PTXT]
G['tone_in_blk'] = [G['tone_must_blk'][n] + G['tone_may_blk'][n] + G['tone_should_blk'][n]
                    for n in range(len(PB))]
G['blk_must_cur'] = [c5(p, u'MUST') for p in PTXT]
G['blk_must_re'] = [len(re.findall(u'MUST', p)) for p in PTXT]
G['blk_tone_ruler_close'] = (sum(abs(G['tone_must_blk'][n] - G['blk_must_cur'][n])
                                 for n in range(len(PB)))
                             + sum(abs(G['tone_must_blk'][n] - G['blk_must_re'][n])
                                   for n in range(len(PB))))


def suffix_words(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def head_words(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


G['pre_idem_7231_9110'] = head_words(PW[1], PW[8])
G['suf_idem_7231_9110'] = suffix_words(PW[1], PW[8])
G['pre_like_7231_9110'] = head_words(PW[5], PW[6])
G['suf_like_7231_9110'] = suffix_words(PW[5], PW[6])
G['idem_blk_same'] = 1 if PTXT[1] == PTXT[8] else 0
G['like_blk_same'] = 1 if PTXT[5] == PTXT[6] else 0
G['w_common_idem'] = len(set(PW[1]) & set(PW[8]))
G['w_only_9110_idem'] = len(set(PW[8]) - set(PW[1]))
G['w_only_7231_idem'] = len(set(PW[1]) - set(PW[8]))
G['w_ledger_idem'] = (G['w_only_9110_idem'] + G['w_common_idem'] - G['blk_vocab'][8]
                      + G['w_only_7231_idem'] + G['w_common_idem'] - G['blk_vocab'][1])
G['idem_blk_row_gap'] = G['blk_lo'][8] - G['blk_lo'][1]
G['like_blk_row_gap'] = G['blk_lo'][6] - G['blk_lo'][5]
G['blk_gap_delta'] = G['idem_blk_row_gap'] - G['like_blk_row_gap']
G['blk_words_per_row'] = [G['blk_words'][n] // G['blk_rows'][n] for n in range(5)]
G['blk_is_one_line'] = [1 if G['blk_rows'][n] == 1 else 0 for n in range(5)]
G['blk_one_line_n'] = sum(G['blk_is_one_line'])
G['ln_verdict_2616'] = ln_of5(0, u'Non-idempotent methods or sequences MUST NOT')[1]
G['ln_confirm_end_2616'] = ln_end5(0, u'user confirmation.')[1]
G['ln_idem_7231'] = ln_of5(1, u'Idempotent methods are distinguished because')[1]
G['ln_idem_9110'] = ln_of5(4, u'Idempotent methods are distinguished because')[1]
G['ln_proxy_9110'] = ln_of5(4, u'A proxy MUST NOT automatically retry')[1]
G['ln_proxy_head_9110'] = ln_of5(4, u'A proxy MUST NOT')[1]
G['ln_client_head_9110'] = ln_of5(4, u'A client SHOULD NOT automatically retry')[1]
G['ln_client_9110'] = ln_end5(4, u'client SHOULD NOT automatically retry a failed automatic retry.')[1]
G['ln_might_head_9110'] = ln_of5(4, u'a client might automatically retry a POST')
G['ln_might_end_9110'] = ln_end5(4, u'a client might automatically retry a POST')
G['might_straddle'] = G['ln_might_end_9110'][1] - G['ln_might_head_9110'][1]
G['ln_might_full_end_9110'] = ln_end5(4, u'persistent connection was used.')
G['ln_riskier_9110'] = ln_of5(4, u'Some clients take a riskier approach')[1]
G['ln_selfdeny_6585'] = ln_of5(2, u'Note that this specification does not define')[1]
G['ln_429_6585'] = ln_of5(2, u'The 429 status code indicates')[1]
G['ln_425_8470'] = ln_of5(3, u'User agents that send a request in early data')[1]
G['ln_assume_8470'] = ln_of5(3, u'The server cannot assume that a client is able')[1]
G['sec_head_line_2616'] = G['sec_body_line'][0]
G['sec_head_line_9110'] = G['sec_body_line'][4]
G['verdict_above_head_2616'] = 1 if G['ln_verdict_2616'] < G['sec_head_line_2616'] else 0
G['proxy_inside_head_9110'] = 1 if G['ln_proxy_9110'] > G['sec_head_line_9110'] else 0
RT = [(0, G['ln_verdict_2616'], u'Non-idempotent methods or sequences'),
      (0, G['ln_confirm_end_2616'], u'user confirmation.'),
      (1, G['ln_idem_7231'], u'Idempotent methods are distinguished'),
      (4, G['ln_idem_9110'], u'Idempotent methods are distinguished'),
      (4, G['ln_proxy_9110'], u'A proxy MUST NOT automatically retry'),
      (4, G['ln_client_9110'], u'client SHOULD NOT automatically retry a failed automatic retry.'),
      (4, G['ln_might_end_9110'][1], u'automatically retry a POST request'),
      (4, G['ln_might_full_end_9110'][1], u'persistent connection was used.'),
      (2, G['ln_429_6585'], u'The 429 status code indicates'),
      (2, G['ln_selfdeny_6585'], u'Note that this specification does not define'),
      (3, G['ln_425_8470'], u'User agents that send a request in early data'),
      (3, G['ln_assume_8470'], u'The server cannot assume that a client is able'),
      (4, G['ln_riskier_9110'], u'Some clients take a riskier approach')]
G['pin_rt'] = [line_holds5(i, ln, nd) for i, ln, nd in RT]
G['pin_rt_n'] = len(G['pin_rt'])
G['pin_rt_ok'] = sum(G['pin_rt'])
G['pin_rt_src'] = [len([1 for i, _, _ in RT if i == n]) for n in range(NSRC)]
G['pin_wrongline'] = sum([line_holds5(4, G['ln_might_head_9110'][1], TEXT[u'a9110_might']),
                          line_holds5(4, G['ln_client_head_9110'],
                                       u'A client SHOULD NOT automatically retry a failed automatic retry.')])

# ---------- 转置尺 ----------
G[u'num_dsec_docs'] = [G[u'num'][i][5] for i in range(NSRC)]
G[u'num_delay_docs'] = [G[u'num'][i][4] for i in range(NSRC)]
G[u'num_httpdate_docs'] = [G[u'num'][i][6] for i in range(NSRC)]
G[u'num_3600_docs'] = [G[u'num'][i][0] for i in range(NSRC)]
G[u'num_120_docs'] = [G[u'num'][i][1] for i in range(NSRC)]
G[u'tone_fam_docs'] = [[G[u'tone_wide'][i][k] for i in range(NSRC)] for k in range(5)]
G[u'code_def_fams'] = [len(x) for x in G[u'code_defined_lbl']]
G[u'code_set_same_2616_9110'] = 1 if G[u'code_defined_lbl'][0] == G[u'code_defined_lbl'][4] else 0
G[u'code_7231_drops'] = [c for c in G[u'code_absent_lbl'][1] if c in G[u'code_defined_lbl'][0]]
G[u'code_7231_drops_n'] = len(G[u'code_7231_drops'])
G[u'std_n'] = len([x for x in G[u'std_line'] if x])
G[u'sec_end_head_rows'] = [len([1 for _, x in ALN[i] if G[u'sec_end_head'][i]
                                and p5(G[u'sec_end_head'][i]) == p5(x)]) for i in range(NSRC)]
G[u'pp_shell_nonblank'] = [G[u'shell_lines'][i] - G[u'blank'][i] for i in range(NSRC)]
G[u'pp_gap_close'] = sum(abs(G[u'pp_gap_rows'][i] - G[u'pp_shell_nonblank'][i])
                         for i in range(NSRC))

# ---------- 共用行归属分档(本遍直接读 B 段建好的归属向量 PRES, 第二遍是逐枚重扫池) ----------
def byte_shared(a, b):
    return [k for k in ORIG[a] if k in ORIG[b] and (ORIG[a][k] & ORIG[b][k])]


SB = dict((pr, byte_shared(pr[0], pr[1])) for pr in PAIRS)
G[u'pair_byte_tier'] = dict((u'%s-%s' % (LBL[a], LBL[b]),
                             [len([k for k in SB[(a, b)] if len(PRES[k]) == m])
                              for m in range(1, NSRC + 1)]) for a, b in PAIRS)
G[u'pb_7231_9110'] = len(SB[(1, 4)])
G[u'pb_8470_9110'] = len(SB[(3, 4)])
G[u'pb_2616_9110'] = len(SB[(0, 4)])
G[u'pb_2616_7231'] = len(SB[(0, 1)])
G[u'only2_7231_9110'] = G[u'pair_byte_tier'][u'7231-9110'][1]
G[u'only2_8470_9110'] = G[u'pair_byte_tier'][u'8470-9110'][1]
G[u'multi_8470_9110'] = sum(G[u'pair_byte_tier'][u'8470-9110'][2:])
G[u'pair_min'] = min(G[u'pair_shared'].values())
G[u'pair_min_lbl'] = [k for k, v in G[u'pair_shared'].items() if v == G[u'pair_min']][0]

# ---------- 聚合量 ----------
G[u'sec_hit_tot'] = sum(G[u'sec_hit_n'])
G[u'auto_gain_tot'] = sum(G[u'auto_gain'])
G[u'auto_fam_overlap_other4'] = sum(G[u'auto_fam_overlap']) - G[u'auto_fam_overlap'][4]
G[u'reword_make_tot'] = sum(x[6] for x in G[u'reword'])
G[u'reword_own_tot'] = sum(len(x) for x in G[u'reword_own'])
G[u'idem_str_6585_8470'] = G[u'idem_str'][2] + G[u'idem_str'][3]
G[u'tone_straddle_6585_8470'] = G[u'tone_straddle'][2] + G[u'tone_straddle'][3]
G[u'num_own_tot'] = sum(len(x) for x in G[u'num_own'])
G[u'paren_2616_7231_9110'] = sum(G[u'paren'][0]) + sum(G[u'paren'][1]) + sum(G[u'paren'][4])
G[u'neg_false_sub_tot'] = sum(G[u'neg_false_sub'])
G[u'subj_active_7231_6585'] = G[u'subj_active'][1] + G[u'subj_active'][2]
G[u'meth_post_sec_other4'] = sum(G[u'meth_post_sec'][:4])
G[u'subj_straddle_tot'] = sum(G[u'subj_straddle'])
G[u'ans_span_tot'] = sum(G[u'ans_span'])
G[u'pair_row_per_sent'] = G[u'pair_7231_9110'] // G[u's_pair_7231_9110']
G[u's_ruler_drop_7231_9110'] = G[u'pair_7231_9110'] - G[u's_pair_7231_9110']

# ---------- 布尔门(段落层): 与第二遍同定义, 读本遍读数 ----------
C2 = {}
C2[u'pin_rt_all'] = 1 if G['pin_rt_ok'] == G['pin_rt_n'] else 0
C2[u'pin_wrap_probe'] = 1 if G['pin_wrongline'] == 0 else 0
C2[u'idem_blk_verbatim'] = 1 if (G['idem_blk_same'] and G['like_blk_same']) else 0
C2[u'idem_gap_equal'] = 1 if G['blk_gap_delta'] == 0 else 0
C2[u'one_line_answer_only_9110'] = 1 if (G['blk_one_line_n'] == 1 and G['blk_is_one_line'][4]) else 0
C2[u'tone_in_blk_6585_8470'] = 1 if (G['tone_in_blk'][11] == 0 and G['tone_mustnot_blk'][11] == 0) else 0
C2[u'blk_tone_2616_rich'] = 1 if (G['tone_in_blk'][0] >= 2 and G['tone_may_blk'][0] >= 1) else 0
C2[u'verdict_above_head_2616'] = G['verdict_above_head_2616']
C2[u'proxy_inside_head_9110'] = G['proxy_inside_head_9110']
C2[u'might_straddle_one'] = 1 if G['might_straddle'] == 1 else 0
C2[u'w_ledger_close'] = 0 if G['w_ledger_idem'] else 1
C2[u'code_7231_drops_two'] = 1 if G['code_7231_drops_n'] == 2 else 0
C2[u'code_set_2616_eq_9110'] = G['code_set_same_2616_9110']
C2[u'only2_dominates_max'] = 1 if G['only2_7231_9110'] * 2 > G['pb_7231_9110'] else 0
C2[u'pp_gap_is_shell_nonblank'] = 1 if G[u'pp_gap_close'] == 0 and sum(G[u'pp_gap_rows']) > 0 else 0
C2[u'only_9110_straddle'] = 1 if G['subj_straddle_tot'] == G['subj_straddle'][4] else 0
C2[u'paren_only_8470'] = 1 if G[u'paren_2616_7231_9110'] == 0 else 0
for k in C2:
    G[k] = 1 if C2[k] else 0

# ---------- 与采集侧逐键对账(键名表从 _mkB80.py 的 PK 字面串里摘, 不重打) ----------
PKL = None
for _st in ast.parse(MS).body:
    if (isinstance(_st, ast.Assign) and isinstance(_st.targets[0], ast.Name)
            and _st.targets[0].id == u'PK'):
        _nd = _st.value.func.value
        while isinstance(_nd, ast.Call):
            _nd = _nd.func.value
        PKL = _nd.value.split()
assert PKL is not None and len(PKL) == 167, len(PKL or [])
AGREE, DIFF = [], []
for k in PKL:
    if k not in G or k not in MEA:
        DIFF.append((k, u'缺键', u'缺键'))
        continue
    (AGREE if G[k] == MEA[k] else DIFF).append((k, G[k], MEA[k]))
G['ff_only_vs_pick_lines'] = 1 if G['ff_only'] == MEA[u'ff_only_lines'] else 0
G['sh_gap_vs_pick'] = 1 if G['sh_char_gap'] == MEA[u'sh_minus_fold'] else 0
G['hdr_tight_vs_pick'] = 1 if G['hdr_lines_tight'] == MEA[u'hdr_lines'] else 0
G['hdr_indent_minus_tight'] = [G['hdr_lines_indent'][i] - G['hdr_lines_tight'][i]
                               for i in range(NSRC)]
G['pair_byte_lines_vs_pick'] = 1 if G['pair_max_byte_lines'] == MEA[u'pair_max_byte'] else 0
G['pair_norm_lines_vs_pick'] = 1 if G['pair_max_norm_only_lines'] == MEA[u'pair_max_norm_only'] else 0
G['ans_vs_pick'] = [1 if MEA[u'ans'][i].rstrip() == G[u'ans'][i] else 0 for i in range(NSRC)]
G['ans_tail_ws'] = [len(MEA[u'ans'][i]) - len(G[u'ans'][i]) for i in range(NSRC)]
G['pick_agree'] = len(AGREE)
G['pick_diff'] = len(DIFF)
for k, a, b in DIFF:
    print(u'  采集⇎复测不符: %s %s vs %s' % (k, a, b))
assert G['pick_diff'] == 0, DIFF[:3]
assert G['pick_agree'] == FLAT[u'pick_agree'] == 167

# ---------- 编码区锚账: 手写配对扫描 ⇎ 双轨归属 ----------
TT = io.open(ENTRY, encoding='utf-8').read()
_i0 = TT.index(u'## ⟪BabelTele⟫')
ENC = TT[TT.index(NL, _i0) + 1:TT.index(u'## ⛓解读注')]
ENC = ENC.rstrip(NL)


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
ERR = [x for x in CITES if p5(x[1]) not in FAN[IDX[x[0]]]]
MISSLINE = [x for x in CITES if x[1] not in ANSET[IDX[x[0]]]]
assert not ERR, ERR[:2]
assert not MISSLINE, MISSLINE[:2]
HITC = dict((a, tuple(i for i in range(NSRC) if p5(a) in FAN[i])) for a in ANCHS)
G['anchor_total'] = USED
G['anchor_distinct'] = DIST
G['anchor_err'] = len(ERR)
G['anchor_single'] = len([a for a in ANCHS if len(HITC[a]) == 1])
G['anchor_cross'] = len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC])
G['anchor_all5'] = len([a for a in ANCHS if len(HITC[a]) == NSRC])
G['checks'] = DIST * NSRC
G['enc_chars'] = len([c for c in ENC if c != NL])
G['nsrc'] = NSRC
for t in TAGS:
    G['tag_' + t] = TAGN[t]
assert G['anchor_single'] + G['anchor_cross'] + G['anchor_all5'] == DIST
# 锚的行号⇎候选行数逐枚回读: 42 枚锚的记录来自第二遍的 ALOG, 本遍用行号尺重新认一遍
ALC = Counter([x[0] for x in CH[u'anchor_lines']])
assert sum(ALC.values()) == G['anchor_total'] == len(CH[u'anchor_lines'])
_back = 0
for lbl, nd, ln, nh in CH[u'anchor_lines']:
    i = IDX[lbl]
    if ln == 0:
        continue
    assert p5(nd).replace(u'\\u2028', u'') in p5(ALND[i][ln]) or p5(ALND[i][ln]).startswith(p5(nd)), (lbl, nd, ln)
    _back += 1
G['amb_n'] = len([x for x in CH[u'anchor_lines'] if x[3] > 1])
assert G['amb_n'] == CH[u'anchor_ambiguous'] == 2
for _k in (u'amb_n',):
    del G[_k]
print(u'第三段完成: 段窗 %d 枚锚复核 %d ⇎ 采集对账 %d/%d ⇎ 编码区 %d 字符 ⇎ 锚 %d 处/去重 %d 串' % (
    len(PINS), _back, G['pick_agree'], len(PKL), G['enc_chars'], G['anchor_total'], DIST))
# ---------- 第四段: 布尔门 ⇎ 标量恒等式 ⇎ V 形 ⇎ DERIV 全在本遍读数上重 eval ----------
# 门与式的**右式**从 `_mkB80.py` 源码 `ast` 摘出, 一条都不抄第二遍的结论。
MSA = ast.parse(MS)

CLOSE_SRC = []
for _nd in MSA.body:
    if isinstance(_nd, ast.Assign) and isinstance(_nd.targets[0], ast.Subscript):
        _t = _nd.targets[0]
        if isinstance(_t.value, ast.Name) and _t.value.id == u'CLOSE' \
                and isinstance(_t.slice, ast.Constant) and isinstance(_t.slice.value, type(u'')):
            CLOSE_SRC.append((_t.slice.value, ast.get_source_segment(MS, _nd.value)))
assert len(CLOSE_SRC) == 28 and len(set(k for k, _ in CLOSE_SRC)) == 28, len(CLOSE_SRC)

ENV = {u'F': G, u'G': G, u'NSRC': NSRC, u'SN': SN, u'GN': GN, u'NEGND': NEGND, u'NL': NL,
       u'sum': sum, u'len': len, u'all': all, u'any': any, u'max': max, u'min': min,
       u're': re, u'sorted': sorted, u'tuple': tuple, u'set': set, u'str': str}
for _k, _e in CLOSE_SRC:
    G[_k] = 1 if eval(_e, ENV, ENV) else 0
G['bool_clos_n'] = len(CLOSE_SRC)
G['bool_clos_sum'] = sum(1 for _k, _ in CLOSE_SRC if G[_k])

ZSRC = []
for _nd in MSA.body:
    if isinstance(_nd, ast.Expr) and isinstance(_nd.value, ast.Call) \
            and isinstance(_nd.value.func, ast.Name) and _nd.value.func.id == u'Z':
        ZSRC.append((_nd.value.args[0].value, _nd.value.args[1].value))
assert len(ZSRC) == 139, len(ZSRC)
ZR = [(_e, _w, eval(_e, ENV, ENV)) for _e, _w in ZSRC]
G['zid_fail'] = [_w for _e, _w, _r in ZR if _r]
G['scalar_clos_n'] = len(ZR)
G['scalar_clos_sum'] = len([1 for _e, _w, _r in ZR if not _r])
G['x_ident_n'] = len(ZR)

# list_clos_n 的口径是“SCAN 段此刻已登记的键”: 按语句顺序收 F[...] 赋值目标,
# 收到 `F['list_clos_n'] =` 为止, 再把 CLOSE 的 28 枚门名并进来(它们由一条 for 动态落键)。
SCAN_KEYS = []
for _nd in MSA.body:
    if isinstance(_nd, ast.Assign) and isinstance(_nd.targets[0], ast.Subscript) \
            and getattr(_nd.targets[0].value, u'id', None) == u'F' \
            and getattr(_nd.targets[0].slice, u'value', None) == u'list_clos_n':
        break
    for _m in ast.walk(_nd):
        if isinstance(_m, ast.Assign) and isinstance(_m.targets[0], ast.Subscript) \
                and isinstance(_m.targets[0].value, ast.Name) and _m.targets[0].value.id == u'F' \
                and isinstance(_m.targets[0].slice, ast.Constant) \
                and isinstance(_m.targets[0].slice.value, type(u'')):
            SCAN_KEYS.append(_m.targets[0].slice.value)
SCAN_KEYS = set(SCAN_KEYS) | set(_k for _k, _ in CLOSE_SRC)
G['list_clos_n'] = len([_k for _k in SCAN_KEYS
                        if (u'_close' in _k or u'_ledger' in _k) and isinstance(G[_k], list)])
G['contract_n'] = len(G) + 1

# ---------- V 形恒等式 ⇎ DERIV 复算点: 只走查表通道, 不走 F 下标通道 ----------
NSV = dict(G)
B80V5 = lambda k, i=None: (NSV[k] if i is None else NSV[k][i])
ENVV = {u'B80V': B80V5, u'sum': sum, u'len': len, u'max': max, u'min': min, u'abs': abs,
        u'sorted': sorted, u'tuple': tuple, u'set': set, u'round': round, u'str': str,
        u'float': float, u'int': int}
ZV2 = [(_e, _w, eval(_e, ENVV, ENVV)) for _e, _w in CH[u'zid']]
ZVFAIL = [_w for _e, _w, _r in ZV2 if _r != 0]
assert not ZVFAIL, ZVFAIL[:3]

DFL = []
DCITE = 0
for _kk in sorted(DER, key=lambda x: (len(x), x)):
    _v = DER[_kk]
    DCITE += _v.count(u"B80V(")
    try:
        _got = eval(_v, ENVV, ENVV)
    except Exception as _e:
        DFL.append((_kk, repr(_e)[:80]))
        continue
    if str(_got) != _kk and repr(_got) != _kk:
        DFL.append((_kk, _v[:90], str(_got)))
assert not DFL, DFL[:4]

# ---------- 与扁平表逐值对账 ----------
_jr = lambda x: json.loads(json.dumps(x))
MISS = [k for k in G if k not in FLAT]
BAD = [(k, _jr(G[k]), _jr(FLAT[k])) for k in G if k in FLAT and _jr(G[k]) != _jr(FLAT[k])]
UNCOVER = [k for k in FLAT if k not in G]
assert not DFL, DFL[:4]
assert not MISS, MISS[:6]
assert not UNCOVER, UNCOVER[:6]
assert not BAD, BAD[:6]
assert G['contract_n'] == len(FLAT) == 583
assert not G['zid_fail'], G['zid_fail'][:3]

# ---------- 本遍硬断言: 全部由现读结果支, 不引第二遍的结论 ----------
assert G['all_txt_no_html'] == 1 and G['all_faces_read'] == 1
assert G['dead_needles_none'] == 1 and G['neg_all_cold'] == 1
assert G['sec_scope_three'] == 1 and G['v2616_outside_own_sec'] == 1
assert G['k9110_inside_sec'] == 1 and G['tone_zero_7231_sec'] == 1
assert G['subj_only_passive_2616'] == 1 and G['act_sec_only_two_docs'] == 1
assert G['no_auto_vocab_6585'] == 1 and G['no_retry_after_8470'] == 1
assert G['no_code_def_8470'] == 1 and G['neither_428_429_in_2616'] == 1
assert G['neither_428_429_in_9110'] == 1 and G['rename_delta_vs_delay'] == 1
assert G['ascii_except_9110'] == 1 and G['pageless_9110_only'] == 1
assert G['sh_equals_fold_for_9110'] == 1 and G['one_maxlen_outlier'] == 1
assert G['year_one_inversion'] == 1 and G['ph_straddle_except_6585'] == 1
assert G['ans_span_shape'] == 1 and G['no_page_break_in_answer'] == 1
assert G['axis_two_buckets_used'] == 1 and G['pair_all_share'] == 1
assert G['hyphen_break_only_two'] == 1 and G['dblspace_hidden_by_fold'] == 1
assert G['bool_clos_n'] == G['bool_clos_sum'] == 28
assert G['scalar_clos_n'] == G['scalar_clos_sum'] == G['x_ident_n'] == 139
assert G['list_clos_n'] == 3 and len(ZV2) == 163 and len(DER) == 198
assert G['anchor_err'] == 0 and G['pick_diff'] == 0 and G['pick_agree'] == 167
assert G['ladder_close'] == 0 and G['ladder_monotone'] == 1 and G['re_eq_cur'] == 1
assert G['overlap_extra'] == 0 and sum(G['sh_loses']) == 0
assert G['shell_ledger_close'] == 0 and G['pair_close'] == 0 and G['union_close'] == 0
assert G['pool_tier_close'] == 0 and G['axis_close'] == 0 and G['s_union_close'] == 0
assert G['s_pool_tier_close'] == 0 and G['apool_tier_close'] == 0 and G['apool_tag_close'] == 0
assert G['sec_sents_gap'] == [0, 0, 0, 0, 0] and sum(G['sh_no_sec_own']) == G['sh_no_sec_n']
assert G['blk_tone_ruler_close'] == 0 and G['pin_rt_all'] == 1 and G['pin_wrongline'] == 0
assert G['pp_gap_close'] == 0 and G['w_ledger_close'] == 1
assert G['neg_hit_widest'] == 0 and G['neg_hit_strict'] == 0
assert G['sn_sec_docs_scope'][2] == -1 and G['sn_sec_docs_scope'][3] == -1
assert G['tone_alnum_gap'] == [0, 0, 0, 0, 0] and G['tone_wide_close'] == 0
assert G['pool_incl'][0] - G['pool_incl'][1] + G['pool_incl'][2] - G['pool_incl'][3] \
    + G['pool_incl'][4] == G['pool_union'] == G['union_incl']
print(u"第四段完成: 布尔门 %d/%d ⇎ 标量恒等式 %d/%d ⇎ V 形 %d 条全真 ⇎ DERIV %d 键 ⇎ %d 处引用全对 ⇎ "
      u"扁平 %d 键全覆盖 ⇎ 不符 %d ⇎ 独有 %d ⇎ 未复算 %d" % (
          G['bool_clos_sum'], G['bool_clos_n'], G['scalar_clos_sum'], G['scalar_clos_n'],
          len(ZV2), len(DER), DCITE, len(FLAT), len(BAD), len(MISS), len(UNCOVER)))

# ---------- ⛓解读注 ----------
def QT(tag, s):
    assert s in ANSET[IDX[tag]], u'本遍锚平面读不到: ' + s[:50]
    return u'⟦%s⟧⟨%s⟩' % (tag, s)


def cell(c):
    assert u'|' not in c, c[:60]
    assert c.count(u'`') % 2 == 0, c[:60]
    return c


def NJ(xs):
    return u' ⇎ '.join(u'%s' % x for x in xs if x is not None)


L2 = []
A = L2.append
A(u"第四遍(`corpus/_fill80.py`)换算法不换定义地重跑一遍: 行界由手写索引循环按 `\\n` 切(第二遍是 `str.split`, 采集侧是"
  u" `re.split`), 行数三档(切格数 ⇎ 换行枚数 ⇎ `splitlines()`)互相对拍; 折平走 `re.sub` 的空白折叠档(第二遍是"
  u" `' '.join(s.split())`), 归一尺与 `pnorm` 逐份对拍, 词数走“手写吃档数非空白连续段”代 `len(s.split())`; 页壳谓词自起第三"
  u" 档——strip 后按空白切 token、逐段比首尾(第二遍是折平再切, 采集侧是三条整序正则), 在全部 %s 行上逐行对拍; 针计数起三档"
  u" `str.count` ⇎ `findall(re.escape)` ⇎ `findall('(?=针)')`, 边界尺换成 lookahead 重叠定位后由本遍自看的左右邻判定"
  u" (第二遍是游标 find 加 `_nb` 手扫), 另起一条断言正则档只用于对拍; 节号尺一条 `^(\\d+(\\.\\d+)*)(\\.?)` 代第二遍的逐字符"
  u" 吃档, 句界尺一条 `\\.(?=[ \\t\\n]*(?:[A-Z(]|$))` 的 finditer 代手扫, 施事 ⇎ 义务 ⇎ 数字 ⇎ 状态码 ⇎ ABNF ⇎ 抬头 ⇎ 编号标题"
  u" 各起一条本遍的正则或切片档并在全库逐行对拍; 偏移→原行号走 `bisect_right`, 并把“片段之间的一个空格”累加成显式数组"
  u" (第二遍在查表时现算), 段界定位把 `str.find` 换成编译一次转义针的 `search(hay, frm)`; 池代数: 归属向量走 `Counter` 直方图"
  u" ⇎ 容斥走“对文档下标的组合逐枚求交”(第二遍是 C(len(v),k) 元算式)⇎ 两两共用改扫一遍键域 ⇎ `dehyph` 换成"
  u" `re.sub('-[ \\t]*','')`; 句池切档用手写扫描代零宽 `re.split`; 实体 ⇎ `⟦…⟧⟨…⟩` 引文各用手写配对扫描代 `re.findall`;"
  u" 锚归属双轨(一轨对锚平面逐行 membership, 一轨对整篇归一串 substring), 两式同判才计数; 28 道布尔门 ⇎ 139 条标量恒等式的"
  u" **右式**从 `_mkB80.py` 源码用 `ast` 摘出后在本遍读数上 eval, 163 条 V 形 ⇎ 198 键 DERIV 从 `_b80checks.json` ⇎"
  u" `_deriv80.json` 回读 eval——一条都不抄第二遍的结论。 48 行针表 `SENT` ⇎ 14 段 `PINS` ⇎ `TONE` ⇎ `AUTOFAM` ⇎ `REWORD`"
  u" ⇎ `SUBJ` ⇎ `ACT` ⇎ `NUM` ⇎ `METH` ⇎ `NEG` ⇎ `CODES` ⇎ `RANK` 的**定义**从源码 `ast`/`exec` 复用——要换的是量, 不是定义。"
  % format(sum(G['lines']), u','))
A(u"本遍复算 %d 个键(扁平表 %d 键全覆盖 ⇎ 本遍独有 %d ⇎ 未复算 %d ⇎ 逐值不符 %d); SCAN 段登记的标量恒等式 %d 条在本遍读数上"
  u" 重跑全为真(通过 %d ⇎ 失败清单 %d 条) ⇎ `checks` 里的 V 形恒等式 %d 条(比 SCAN 段多 %d 条, 多的那批在 emit 段并进来)全真"
  u" ⇎ DERIV %d 键 ⇎ %d 处引用重跑全对 ⇎ 布尔门 %d 道在本遍现算全绿 ⇎ 清单式闭合 %d 项 ⇎ 与采集遍逐键横比 %d 键相符 ⇎ %d 键"
  u" 不符 ⇎ 门槛侧 %d 处引文锚逐枚回本遍锚平面验命中 %d 枚 ⇎ 去重 %d 串 ⇎ 编码区 %d 非换行字符 ⇎ 判词 %d 条。" % (
      len(G), len(FLAT), len(MISS), len(UNCOVER), len(BAD),
      G['scalar_clos_n'], G['scalar_clos_sum'], len(G['zid_fail']), len(ZV2),
      len(ZV2) - G['scalar_clos_n'], len(DER), DCITE, G['bool_clos_n'], G['list_clos_n'],
      G['pick_agree'], G['pick_diff'], G['anchor_total'],
      len([1 for t, x in CITES if x in ANSET[IDX[t]]]), G['anchor_distinct'], G['enc_chars'],
      G['checks']))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"行界⇎换页⇎页壳",
     u"手写 `\\n` 索引循环 ⇎ `str.count` ⇎ `splitlines()` 三档并立; 壳谓词自起“strip 后切 token、逐段比首尾”的第三档",
     u"原行 %s ⇎ 换行枚 %s ⇎ splitlines %s ⇎ 收尾换行 %d 份 ⇎ 换页符 %s ⇎ [Page] 壳行 %s ⇎ 只剩换页符档 %s" % (
         J(G['lines']), J(G['lines_nl']), J(G['lines_split']), sum(G['tail_nl']),
         J(G['ff']), J(G['shell_lines']), J(G['ff_only'])),
     u"行数账 %d ⇎ 换页减页壳 %s ⇎ 行内混排 %s; 壳三本账 %d ⇎ 本遍多判 %s ⇎ 采集多判 %s ⇎ 换页档与采集行档同值判定 %d。" % (
         G['lines_split_close'], J(G['ff_minus_pg']), J(G['ff_inline']), G['shell_ledger_close'],
         J(G['shell_mk_only']), J(G['shell_pick_only']), G['ff_only_vs_pick_lines'])),
    (u"折平⇎归一⇎字节",
     u"折平用 `re.sub` 空白折叠档 ⇎ 词数用手写连续段计数; 字节⇎码位差走 `utf-8` 编码长度减码位数",
     u"字节 %s ⇎ 面内码位 %s ⇎ 折平码位 %s ⇎ 字节−码位差 %s ⇎ 非 ASCII %s ⇎ BOM %s" % (
         J(G['bytes']), J(G['chars']), J(G['fold_chars']), J(G['byte_cp_delta']),
         J(G['nonascii']), J(G['bom'])),
     u"回车 %s ⇎ NUL %s ⇎ 折平后双空格 %s(所以标题形状只能在原行上量, 判定 %d); 9110 的 %d 枚非 ASCII 全在姓名行 %s。" % (
         J(G['cr']), J(G['nul']), J(G['dblspace_in_fold']), G['dblspace_hidden_by_fold'],
         G['nonascii'][4],
         QT(u'9110', u'   D. Lawrence, Paul J. Leach, Håkon W. Lie, Ari Luotonen, Larry'))),
    (u"标签四把尺⇎实体",
     u"`<…>` 形由手写扫描给区间(换行不吃), 四把尺在区间上按首字符切片分类; 实体尺手写吃 `&…;` 至多 9 字符",
     u"尖括号形 %s ⇎ 开名形 %s ⇎ 闭名形 %s ⇎ 裸 URL 形 %s ⇎ 伪法余数 %s ⇎ 实体 %s ⇎ 注释 %s" % (
         J(G['tag_shape']), J(G['tag_open']), J(G['tag_close']), J(G['tag_url']),
         J(G['tag_pseudo']), J(G['ent_total']), J(G['comment'])),
     u"6585 的 %d 枚被三把尺分完(判定 %d⇔%d+%d+%d, 它真带了一页示例 HTML: %s); 8470 的 %d 枚名形两把尺全零 ⇎ 全库零实体零注释。" % (
         G['tag_shape'][2], G['tag_shape'][2], G['tag_open'][2], G['tag_close'][2], G['tag_url'][2],
         QT(u'6585', u'         <p>I only allow 50 requests per hour to this Web site per'),
         G['tag_shape'][3])),
    (u"四档面⇎48 枚针",
     u"面构造换 `re.sub` 折平 ⇎ `bisect` 映行 ⇎ 三档计数(非重叠 ⇎ 转义 findall ⇎ lookahead 重叠)逐枚并立",
     u"名下读到的枚数 %s ⇎ 逐行 %s ⇎ 折平 %s ⇎ 摘壳 %s ⇎ 节窗 %s(-1=无这一档) ⇎ 针 %d 枚(反向 %d)" % (
         J(G['needles_owned']), J(G['sn_strict_docs']), J(G['sn_fold_docs']), J(G['sn_sh_docs']),
         J(G['sn_sec_docs_scope']), G['needle_n'], G['neg_n']),
     u"阶梯账 %d ⇎ 单调 %d ⇎ 正则轨=游标轨 %d ⇎ 重叠不多吃 %d ⇎ 折行救回 %d 枚按份 %s ⇎ 摘壳掉 %d 枚 ⇎ 新开 %d 枚(按份 %s) ⇎ 节外 %d 枚按份 %s ⇎ 死集 %d。" % (
         G['ladder_close'], G['ladder_monotone'], G['re_eq_cur'], G['overlap_extra'],
         G['fold_minus_strict_n'], J(G['fold_minus_strict_own']), sum(G['sh_loses']),
         sum(G['sh_gains']), J(G['sh_gains']), G['sh_no_sec_n'], J(G['sh_no_sec_own']), len(G['dead_needles']))),
    (u"节窗⇎节界",
     u"节号尺一条正则代逐字符吃档; 定界由“下一个同级标题”在原行面上前缀匹配, 且不早于节头那一行",
     u"有节 %d 份 ⇎ 节头 %s ⇎ 窗幅字符 %s ⇎ 行 %s ⇎ 词 %s ⇎ 句 %s ⇎ 占摘壳面千分比 %s" % (
         G['sec_found_n'], NJ(G['sec_head_line']), J(G['sec_chars']), J(G['sec_lines']),
         J(G['sec_words']), J(G['sec_sents']), J(G['sec_share_permille'])),
     u"句数两把尺(finditer ⇎ 逐字符扫)逐份同值 %s ⇎ 同名标题命中 %s(合计 %d=有节 %d 份各一行正文+目录 %d 行) ⇎ 节尾收束式 %s ⇎ 正文行 %s。" % (
         J(G['sec_sents_gap']), J(G['sec_hit_n']), G['sec_hit_tot'], G['sec_found_n'],
         G['sec_row_dup'][4], NJ(G['sec_end_kind']), NJ(G['sec_body_line']))),
    (u"义务词五式⇎两把边界尺",
     u"边界尺=lookahead 重叠定位后验左右邻(alpha ⇎ alnum 两档), 另起断言正则档只用于对拍; 大写族⇎小写族分账",
     u"最宽档合计 %s ⇎ 折平 %s ⇎ 纯 MUST %s ⇎ 大小写差 %s ⇎ 小写四词族 %s ⇎ 被 72 列切开 %s" % (
         J(G['tone_tot']), J(G['tone_fold_tot']), J(G['tone_must_pure']), J(G['tone_case_gap']),
         J(G['tone_word_lc_tot']), J(G['tone_straddle'])),
     u"alpha 与 alnum 两尺逐份同值 %s ⇎ 手扫轨=正则轨判定 %d ⇎ MUST 账 %s ⇎ 节窗内义务词 %s ⇎ 7231 节内 %d 枚(判定 %d)。" % (
         J(G['tone_alnum_gap']), G['tone_wide_close'], J(G['tone_must_ledger']),
         J(G['tone_sec_tot']), G['tone_sec_tot'][1], G['tone_zero_7231_sec'])),
    (u"automat×retry⇎重来八式",
     u"六式 ⇎ 八式的定义照抄 `AUTOFAM` ⇎ `REWORD`; 计数走三档, 族内互含由本遍的逐对子串判定现算",
     u"automat×retry 折平 %s ⇎ 逐行 %s ⇎ 去重 %s ⇎ 裸 automat* %s ⇎ 重来八式 %s ⇎ 去重 %s ⇎ 零枚族数 %s ⇎ idempotent %s" % (
         J(G['auto_tot_fold']), J(G['auto_tot_line']), J(G['auto_union_fold']), J(G['auto_bare']),
         J(G['reword_tot']), J(G['reword_union']), J(G['reword_zero_n']), J(G['idem_str'])),
     u"两档逐份同枚(差合计 %d) ⇎ 摘壳不多不少 %s ⇎ 6585 六式零枚(判定 %d) ⇎ 族内互含只在 9110 %d 处 ⇎ 只属一份的说法 %d 枚 ⇎ 八式全库无 “make a new request”: %s。" % (
         sum(G['auto_gain']), J(G['auto_sh_minus_fold']), G['no_auto_vocab_6585'],
         G['auto_fam_overlap'][4], len(G['reword_own'][0]) + len(G['reword_own'][4]),
         QT(u'6585', u'   to wait before making a new request.'))),
    (u"施事者⇎主被动",
     u"九式 `SUBJ` ⇎ 七式 `ACT` 定义照抄; 点名与否由本遍在针前取“冠词+名词”切片判定, 不重算第二遍的句式函数",
     u"九式命中 %s ⇎ 点名主动句 %s ⇎ 不点名被动句 %s ⇎ 泛称七式 %s ⇎ 节窗内点名 %s ⇎ 被切开 %d 枚" % (
         J(G['subj_n']), J(G['subj_active']), J(G['subj_passive']), J(G['act_tot']),
         J(G['act_sec_tot']), G['subj_straddle_tot']),
     u"被动判词全库恰一枚(判定 %d) ⇎ 7231 与 6585 一个施事者也不点(判定 %d) ⇎ POST 在节窗被点名只在 9110: %d 次 ⇎ 切开两枚都在 9110(判定 %d)。" % (
         G['subj_only_passive_2616'], G['subj_active'][1] + G['subj_active'][2] == 0,
         G['meth_post_sec'][4], G['only_9110_straddle'])),
    (u"数字七式⇎单位换代",
     u"`NUM` 七式定义照抄; 带边界尺与裸串尺并立, 被长数吃进的假阳性单独落账; 换代净账由本遍现算 delay−delta",
     u"七式(3600 ⇎ 120 ⇎ 50 req/h ⇎ 2 min ⇎ delay ⇎ delta ⇎ HTTP-date)逐份 %s ⇎ 总量 %s ⇎ 数字字符 %s ⇎ Retry-After 行 %s ⇎ 净账 %s" % (
         J(G['num']), J(G['num_tot']), J(G['digit_chars']), J(G['ra_count']), J(G['num_rename'])),
     u"delta⇎delay 完全分家(判定 %d): 2616 %d 枚 delta ⇎ 7231 与 9110 各 %d/%d 枚 delay ⇎ 假阳性 %s ⇎ 8470 不提 Retry-After(判定 %d) ⇎ 只属一份的数字族 %d 族 ⇎ 两分钟例 %s。" % (
         G['rename_delta_vs_delay'], G['num'][0][5], G['num'][1][4], G['num'][4][4],
         J(G['num_sub']), G['no_retry_after_8470'],
         len([x for x in G['num_own'] if x]), J(G['ra_two_minutes']))),
    (u"状态码定义行⇎ABNF",
     u"定义行尺一条正则取编号、再手工吃空白、看码后一字符(第二遍是节号函数加两段下标); ABNF 三式各一条前缀尺",
     u"定义行 %s ⇎ 目录行 %s ⇎ 族数 %s ⇎ 9110 失踪族 %s ⇎ 7231 失踪 %s ⇎ 8470 括号印法 %d 枚 ⇎ 其中被切开 %d" % (
         J(G['code_defined_n']), J(G['code_toc']), J(G['code_def_fams']),
         u'%d 族' % len(G['code_absent_lbl'][4]), u' '.join(G['code_7231_drops']),
         G['paren'][3][0], G['paren_straddle'][3]),
     u"2616 与 9110 定义集逐枚同(判定 %d) ⇎ 8470 零定义(判定 %d) ⇎ 9110 既不定义 428 也不定义 429(判定 %d) ⇎ 6585 的 428 定义行印两处(目录 ⇎ 节头) ⇎ ABNF 竖线⇎斜杠⇎引号 %s ⇎ 账 %s。" % (
         G['code_set_2616_eq_9110'], G['no_code_def_8470'], G['neither_428_429_in_9110'],
         J(G['ra_abnf_forms']), J(G['ra_abnf_ledger']))),
    (u"搬字两把尺⇎容斥",
     u"归属向量走 `Counter` 直方图 ⇎ 容斥走“文档下标组合逐枚求交” ⇎ 两两共用改扫键域; 句池切档用手写扫描代零宽 `re.split`",
     u"行尺池 %s 行 ⇎ 并集 %s ⇎ 分档 %s(共用 1..5 份的行数) ⇎ 最大对 %d(%s) ⇎ 逐字节 %d+只归一 %d ⇎ 原始行枚 %d ⇎ 句尺池 %d ⇎ 句尺最大对 %d" % (
         format(G['pool_n'], u','), format(G['pool_union'], u','), str(G['pool_tier']),
         G['pair_max'], G['pair_max_lbl'], G['pair_max_byte_keys'], G['pair_max_norm_only_keys'],
         G['pair_max_byte_lines'], G['s_pool_n'], G['s_pair_max']),
     u"容斥 %s 归到并集判定 %d ⇎ 分档账 %d ⇎ 归一因由四桶 %s(非空桶 %d 个 ⇎ “恰两桶”门 %d) ⇎ 行尺→句尺差 %d 枚(一句由 %d 行摊开) ⇎ 单位差 %d 行 ⇎ 最大对里只属这一对 %d 枚。" % (
         str(G['pool_incl']), G['union_close'], G['pool_tier_close'], G['axis_str'],
         G['axis_str_n'], G['axis_two_buckets_used'], G['s_ruler_drop_7231_9110'], G['pair_row_per_sent'],
         G['pair_byte_unit_gap'], G['only2_7231_9110'])),
    (u"抬头谱系⇎年份",
     u"抬头字段尺走 `startswith` 加双空格切档, 年份走“月名 token 紧跟四位数字 token”的相邻对档; 号表手工按逗号切",
     u"年 %s ⇎ 首末年距 %d ⇎ 倒退 %d 处 ⇎ Obsoletes %d 号 ⇎ 空段 %s ⇎ Updates %d 处 ⇎ 出边为零的份 %s ⇎ ISSN 行 %s ⇎ STD 行 %d" % (
         J(G['years']), G['year_span'], G['year_inversions'], G['obs_total'],
         J(G['obs_blank_segs']), G['upd_total'], str(G['lineage_no_edge']), J(G['issn_hdr']), G['std_n']),
     u"谱系账 %d ⇎ 被 Updates 指向者恰也被 Obsoletes: 判定 %d ⇎ 库内命中 %s ⇎ 编号标题三式 两点 %s ⇎ 一点 %s ⇎ 无点 %s ⇎ 顶格⇎缩进差 %s。" % (
         G['lineage_close'], G['upd_target_obsoleted'][2], J(G['obs_target_in_lib']),
         J(G['hdr_dot2sp']), J(G['hdr_dot1sp']), J(G['hdr_nodot']), J(G['hdr_indent_minus_tight']))),
    (u"段窗⇎行号尺",
     u"段界在摘壳折平面按字面针 `search(hay, frm)` 定位, 偏移映回原行走 `bisect_right`; 复核针拿行号回原文件取那一行逐枚自验",
     u"14 段起行 %s ⇎ 止行 %s ⇎ 行数 %s ⇎ 字符 %s ⇎ 词 %s ⇎ 五段主答句合计 %d 字符 ⇎ %d 词 ⇎ %d 行" % (
         J(G['blk_lo']), J(G['blk_hi']), J(G['blk_rows']), J(G['blk_chars']), J(G['blk_words']),
         G['blk_five_chars'], G['blk_five_words'], G['blk_five_rows']),
     u"行针 %d 枚自验 %d(判定 %d) ⇎ 反向把整段拿到首字那一行验 %d 枚 ⇎ 答句跨行 %s ⇎ 每行词数 %s ⇎ 一行读全只有 9110(判定 %d) ⇎ 片段序列减非空行 %s=壳行 %s。" % (
         G['pin_rt_n'], G['pin_rt_ok'], G['pin_rt_all'], G['pin_wrongline'],
         J(G['ans_span']), J(G['blk_words_per_row']), G['one_line_answer_only_9110'],
         J(G['pp_gap_rows']), J(G['pp_shell_nonblank']))),
    (u"锚归属双轨⇎编码区",
     u"引文对由手写配对扫描取自编码区(代一条 `findall`); 一轨对锚平面逐行 membership ⇎ 一轨对整篇归一串 substring, 两式同判才计数",
     u"引文 %d 处 ⇎ 去重 %d 串 ⇎ 单源 %d ⇎ 跨源 %d ⇎ 五源同现 %d ⇎ 读不到 %d ⇎ 判词 %d 条 ⇎ 编码区 %d 非换行字符" % (
         G['anchor_total'], G['anchor_distinct'], G['anchor_single'], G['anchor_cross'],
         G['anchor_all5'], G['anchor_err'], G['checks'], G['enc_chars']),
     u"本遍独立复核 %d/%d 处全在本遍锚平面 ⇎ 同串在两处印的歧义 %d 枚(只进本注不进 T1) ⇎ 五份全为纯文本面, 所以门槛对面只有一把尺: 原样字节, 锚一律抛回原文件那一行。" % (
         len([1 for t, x in CITES if x in ANSET[IDX[t]]]), G['anchor_total'], CH[u'anchor_ambiguous']))
]
for _a, _b, _c, _d in rows:
    A(u"| %s | %s | %s | %s |" % (cell(_a), cell(_b), cell(_c), cell(_d)))
A(u"")
A(u"五份文书对同一个问题的五种答法, 在本遍全部落到可复算的四把尺上(义务词式 ⇎ 施事者 ⇎ 答句跨几行 ⇎ 答句住在节内还是节外)。"
  u" 2616 给了禁令却不写在定义节里: §9.1.2 只给定义(节窗内 %d 枚), “能不能自动重来”的三枚判词全在别处——节窗档 %d 枚 ⇎ 摘壳档"
  u" %d 枚, 三枚一律记进节外账(%d); 判词印在第 %d 行, 节头正文行在第 %d 行, 相距 %d 行, 判词在节头之上, 而且它自己就把读者指"
  u" 回去: %s。全文两处指向 §9.1.2(%s), 后一处就是判词行。 7231 把同一条款搬进 §4.2.2, 窗幅从 %d 字符扩到 %d 字符 ⇎ 句数 %d"
  u" ⇎ %d, 却一个义务词也不给(节窗内 %d 枚 ⇎ 2616 %d 枚 ⇎ 9110 %d 枚): 它给的是机制句 %s。 9110 反向收成一处——名下 %d 枚内容针"
  u" 全在 §9.2.2 之内(节外 %d), 两份禁令点名两个施事者, 主答句压到 %d 词独占 %d 行, 是全库唯一能在一行读全的答句(判定 %d)。"
  u" 中间两份干脆换题: 6585 不答“能不能重来”, automat×retry 六式 %d 枚 ⇎ idempotent 一词 %d 枚, 只给一个码加一个头加一个例子,"
  u" 并自认没定义怎么数请求: %s; 8470 一句给全三档义务: %s。" % (
      G['defin_in_sec'], G['v_in_sec'], G['v_in_sh'], G['v_sh_no_sec'], G['ln_verdict_2616'],
      G['sec_body_line'][0], G['verdict_head_gap'],
      QT(u'2616', u'   idempotent (see section 9.1.2). Non-idempotent methods or sequences'),
      str(G['xref_lines_abs']), G['sec_chars'][0], G['sec_chars'][1], G['sec_sents'][0],
      G['sec_sents'][1], G['tone_sec_tot'][1], G['tone_sec_tot'][0], G['tone_sec_tot'][4],
      QT(u'7231', u'   Idempotent methods are distinguished because the request can be'),
      G['k9110_in_sec'], G['k9110_no_sec'], G['ans_words'][4], G['ans_span'][4],
      G['one_line_answer_only_9110'], G['auto_tot_fold'][2], G['idem_str'][2],
      QT(u'6585', u'   Note that this specification does not define how the origin server'),
      QT(u'8470', u'   user agent SHOULD retry automatically, but any retries MUST NOT be')))
A(u"四档口径不是装饰: 全库唯一一枚“只有摘壳档才读得到”的针是 6585 的 428 定义行——逐行档与折平档都读不到, 摘壳档读出 %d 枚且全落在 6585"
  u"(%s), 它被跨页的页壳正好切开; 而摘壳一档"
  u" 一枚也不丢(逐份 %s, 合计 %d)。节窗档对 6585 与 8470 根本不存在, 于是按 -1 登记而不是 0(%s)——口径不存在与读不到是两件事, 这一格若填 0"
  u" 就会把“这两份没有幂等节”误读成“这两份的幂等节里没有答句”。 9110 无分页壳, 所以它的摘壳面与折平面等长(差 %d 字符, 判定 %d),"
  u" 而 2616 名下 %d 枚针里 %d 枚跨行, 逐行档只剩 %d 枚可读——同一句话在四档里的最大落差就在这一份。被 72 列硬换行切开的大写"
  u" 义务词逐份 %s 枚, 其中 9110 的 %d 枚分在 MUST NOT ⇎ SHOULD NOT 两式上(%s): 新版式去掉页壳, 反而切掉更多禁令短语。答句本身"
  u" 从不被页壳切开(%s 枚), 切开答句的是换行而不是分页。" % (
      G['sh_gains'][2], u' ⇎ '.join(str(x) for x in G['sh_gains']), J(G['sh_loses']), sum(G['sh_loses']),
      str(G['sn_sec_docs_scope']),
      G['sh_char_gap'][4], G['sh_equals_fold_for_9110'], G['needles_owned'][0],
      G['fold_minus_strict_own'][0], G['sn_strict_docs'][0], J(G['tone_straddle']),
      G['tone_straddle'][4], str(G['tone_straddle_k'][4]), J(G['ans_page_break'])))
A(u"措辞 ⇎ 单位 ⇎ 码表三层换代都能由在库字节数出来。说法层: automat×retry 六式逐份 %s, 6585 一份零枚而 9110 独占 %d 枚; 裸"
  u" automat* 逐份 %s 枚, 9110 一份的差 %d 枚就是“不在 retry 邻座”的 automatic/automatically(%d 减 %d)——所以“自动化”一词的出现量"
  u" 并不能替“自动重来”作证。单位层: 2616 只写 delta-seconds(%d 枚 ⇎ delay 0 枚), 7231 与 9110 只写 delay-seconds(各 %d ⇎ %d 枚 ⇎"
  u"  delta 全零), 换代净账 %s; 两族在带边界尺与裸串尺上逐枚相等(%s), 没有短数被长数吃进的假阳性。码表层: 定义行 %s 行 ⇎ 族数 %s,"
  u" 7231 比 2616 少两枚(%s 搬去同族分册), 9110 又回到 2616 的同一枚集(判定 %d), 但 428 与 429 在 9110 与两份 HTTP/1.1 里都不定义"
  u" (判定 %d ⇎ %d)——限流那一码住在本库之外的 6585: %s。 8470 一枚也不定义(判定 %d), 它只用“码+括号名”的印法引用(%d 枚,"
  u" 其余四份 %d ⇎ %d ⇎ %d ⇎ %d), 这种印法全库只有它用, 且 %d 枚被换行切在中间: %s。" % (
      J(G['auto_tot_fold']), G['auto_tot_fold'][4], J(G['auto_bare']), G['auto_bare_minus_union'][4],
      G['auto_bare'][4], G['auto_union_fold'][4], G['num'][0][5], G['num'][1][4], G['num'][4][4],
      J(G['num_rename']), J(G['num_sub']), J(G['code_defined_n']), J(G['code_def_fams']),
      u' '.join(G['code_7231_drops']), G['code_set_2616_eq_9110'], G['neither_428_429_in_9110'],
      G['neither_428_429_in_2616'],
      QT(u'6585', u'   The 429 status code indicates that the user has sent too many'),
      G['no_code_def_8470'], G['paren'][3][0], G['paren'][0][0], G['paren'][1][0],
      G['paren'][2][0], G['paren'][4][0], G['paren_straddle'][3],
      QT(u'8470', u'   A 425 (Too Early) status code indicates that the server is unwilling')))
A(u"搬字要挑明单位。 7231 与 9110 是同一份正文的两次排版: 行尺上折叠键共用 %d 条, 其中逐字节同形 %d 条 ⇎ 只因归一而同形 %d 条;"
  u" 同一对换成“原始行枚”是 %d 行(判定 %d: 行枚不少于折叠键), 差 %d 行是同一折叠键在两处各印一次(壳行吃掉 %d 行)。换成句尺, 同"
  u" 一对只剩 %d 句 ⇎ 从行尺到句尺净差 %d 枚——不是矛盾, 是一句由 %d 行摊开; 句尺池 %d 句 ⇎ 分档 %s(共用 1..5 份的句数) ⇎ 容斥 %s 归到并集(判定 %d)。"
  u" 归一因由四桶 %s(两桶为零 ⇎ 两桶有值 %d ⇎ 池内相加账平 %d), 例: %s 与 9110 的同句只差一处空格。最大对的 %d 枚里 %d 枚只属于"
  u" 这一对(搬家的正文), 其余被三份以上共用(模板行); 而 8470·9110 一对 %d 枚里只属这一对 %d ⇎ 更多份共用 %d 枚。两段搬字都是"
  u" 逐字同形: 幂等定义段共头 %d 词 ⇎ 共尾 %d 词 ⇎ 词集账 %d ⇎ 只属 7231 %d ⇎ 只属 9110 %d, 类比句段共头 %d 词 ⇎ 共尾 %d 词;"
  u" 两段在原文件里的行距位移相等(%d ⇎ %d, 差 %d)——搬得整整齐齐。反过来 7231 那句类比句在 2616 摘壳面上 %d 枚 ⇎ 2616 的定义句在"
  u" 7231 折平面上 %d 枚: 换代换了措辞, 不是漏印。 %s 一句在两份里各印一次。" % (
      G['pair_max'], G['pair_max_byte_keys'], G['pair_max_norm_only_keys'], G['pair_max_byte_lines'],
      G['pair_byte_lines_ge_keys'], G['pair_byte_unit_gap'], G['pair_byte_shell_gap'],
      G['s_pair_max'], G['s_ruler_drop_7231_9110'], G['pair_row_per_sent'], G['s_pool_n'],
      str(G['s_pool_tier']), str(G['s_incl']), G['s_union_close'], G['axis_str'], G['axis_str_n'], G['axis_close'],
      QT(u'7231', u'     Accept: text/plain; q=0.5, text/html,'), G['pb_7231_9110'],
      G['only2_7231_9110'], G['pb_8470_9110'], G['only2_8470_9110'], G['multi_8470_9110'],
      G['pre_idem_7231_9110'], G['suf_idem_7231_9110'], G['w_ledger_idem'], G['w_only_7231_idem'],
      G['w_only_9110_idem'], G['pre_like_7231_9110'], G['suf_like_7231_9110'],
      G['idem_shift'], G['like_shift'], G['blk_gap_delta'], G['like_absent_2616'],
      G['defin_absent_7231'],
      QT(u'9110', u'   Like the definition of safe, the idempotent property only applies to')))
A(u"幂等节只在三份文书里存在, 第四遍在这一格上显出两个坑。第一个是目录: 同名标题在 9110 的面上命中 %d 行(目录第 %d 行 ⇎ 正文第"
  u" %d 行), 因为新版式把目录也排成同样的缩进标题; 2616 与 7231 的目录行带点引线与页码, 标题面认不出它(%s), 所以全库命中合计"
  u" %d 行=有节 %d 份各一行正文+那唯一一行目录。第二个是定界: 节尾由下一个同级标题给出(%s), 三份都以标题式收束而没有撞到串尾,"
  u" 而“9.2.3.  Methods and Caching”这一串在 9110 也印两次, 定界必须取不早于节头的那一行, 否则窗宽会算成负数(行距 %s)。 6585 与"
  u" 8470 没有这一节, 节内义务词 ⇎ 节内点名 ⇎ 节内句数三本账对它们全是空集, 不是零集。 9110 的节窗最厚: %d 字符 ⇎ %d 词 ⇎ %d 句"
  u" ⇎ 占摘壳面千分比 %d(2616 %d ⇎ 7231 %d), 同一个问题的答案密度是前两份的两到三倍。" % (
      G['sec_hit_n'][4], G['sec_toc_line'][4], G['sec_body_line'][4],
      QT(u'2616', u'   9.1.2    Idempotent Methods .......................................51'),
      G['sec_hit_tot'], G['sec_found_n'], NJ(G['sec_end_head']), str(G['sec_end_head_gap']),
      G['sec_chars'][4], G['sec_words'][4], G['sec_sents'][4], G['sec_share_permille'][4],
      G['sec_share_permille'][0], G['sec_share_permille'][1]))
A(u"两处在换算法时才显形, 记在这里。其一: 大写尺不能用 `str.isupper()`——它承认非 ASCII 的大写字母, 而第二遍的句界尺只认 ASCII 的"
  u" `[A-Z0-9*<(]`; 9110 面内正有 %d 枚非 ASCII 码位(全在贡献者姓名行), 用 `isupper()` 就会把姓名行切成额外的句, 本遍与第二遍的"
  u" 句池在 9110 上第一拍就对不齐, 改回 ASCII 档后逐份同值。其二: 邻居尺的“重叠”口径要跟着实现走——第二遍的游标 find 每步前进"
  u" 一枚字符, 等价于 lookahead 定位, 本遍若改用非重叠的 `findall` 就会在紧邻重复的形状上少吃(试针 “MUST MUST” 两枚 ⇎“MUSTMUST”"
  u" 一枚都要按 alpha 边界判), 状态码行尺同理: 一条正则若把编号后的空白一并吃掉, “码后必须紧跟空白”这条判据就永远成立, 400 会被"
  u" 当成 4001 的形状多算——本遍第一版就栽在这里。两轨都改到在全库 %s 行上逐行同值才落账, 而这两处对拍本身就是第三档存在的理由。" % (
      G['nonascii'][4], format(sum(G['lines']), u',')))
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"五份文件在 RFC Editor 上的此刻状态(2616 此刻是否仍挂 Historic、6585 与 8470 是否有后续勘误改过这些判词、被 7231 废止的 2616"
  u" 之外的分册现行文本) ⇎ 被 Updates 指向但不在本库的 2817 ⇎ 3864 ⇎ 2818 的正文 ⇎ 现网客户端与代理到底会不会自动重发(规范给的"
  u" 义务词不等于装机行为; 8470 谈的 early data 重放在部署里是否真的发生) ⇎ 429 之外服务器实际怎么数请求(6585 自己就写了没定义)"
  u" ⇎ 镜像页的时间戳与本版号之外的修订 ⇎ 9110 姓名行那 %d 枚非 ASCII 在别的序列化里落成什么——这些都要在库外字节或实时状态, 本库"
  u" 五份文件给不出判据; 在库只给得出抬头里的 Obsoletes ⇎ Updates 清单与面上字节的四档读数。" % G['nonascii'][4])

NEW = u"## ⛓解读注" + NL + NL + NL.join(L2) + NL
_i2 = TT.index(u"## ⛓解读注")
out = TT[:_i2] + NEW
assert out.count(u"## ⛓解读注") == 1
T2 = ENTRY + u'.tmp'
io.open(T2, 'w', encoding='utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"⛓解读注 已写入 %s ｜ 表 %d 行 ⇎ 注区 %d 字符 ⇎ 复算 %d 键 ⇎ 不符 %d ⇎ 独有 %d ⇎ 未复算 %d ⇎ "
      u"恒等式 %d/%d ⇎ V 形 %d 条 ⇎ DERIV %d 键 ⇎ 门 %d/%d ⇎ 编码区 %d 字符未动"
      % (ENTRY, len(rows), len(NEW), len(G), len(BAD), len(MISS), len(UNCOVER),
         G['scalar_clos_sum'], G['scalar_clos_n'], len(ZV2), len(DER),
         G['bool_clos_sum'], G['bool_clos_n'], G['enc_chars']))
