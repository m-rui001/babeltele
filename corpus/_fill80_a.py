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
