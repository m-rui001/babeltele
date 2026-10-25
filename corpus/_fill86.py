# -*- coding: utf-8 -*-
"""B86 的第五遍复测: 采集侧(_pick86.py)⇎ 建条目侧(_mkB86.py 的 SCAN ⇎ _mk86emit.py 的 SCAN2)
换算法不换定义地把 577 枚扁平键全部重跑一遍, 现算后把 ⛓解读注 写进条目。本遍是第四套实现, 换机制处:
①行界: `re.compile('\\n').split` ⇎ 建条侧 `str.split(NL)`; `splitlines` 档不叫 C 函数, 本遍逐字符认行界符集
  (`\\n \\r \\x0b \\x0c \\x1c-\\x1e \\x85 \\u2028 \\u2029`, `\\r\\n` 记一枚)自己重建; `readlines` 档走
  `re.split('(?<=\\n)')` 去空段; 换行/回车枚数走逐字符比较(建条侧取 `finditer` 位置表); 字节数走逐字节迭代,
  文件尺寸走 `os.stat().st_size`(建条侧是 `os.path.getsize`); 码位数走 `len()`(建条侧是逐字符累加);
②UTF-8 差额: 本遍用 `字节数 − 码位数` 直接作差(建条侧逐字符 `encode` 求和), 两把尺同值才入账;
③折平: `re.finditer('\\S+')` 取词跨度再 `join`(建条侧 `re.split('\\s')` 过滤空段 ⇎ `str.split()`);
④字面针三档: `str.count`(非重叠) ⇎ `re.finditer(re.escape)` 取位置(非重叠) ⇎ `finditer('(?=针)')`(重叠),
  建条侧是 `findall(re.escape)`, 采集侧是游标 find 环;
⑤整词尺: 先把全串翻成“ASCII 字母/数字/字母数字”三张布尔表(只认 52+10 枚字符, 不认 Unicode 字母),
  命中由前瞻 finditer 定位再查表读左右邻(建条侧 `ub_tab` 是游标 find + `isalpha()` 表 ⇎ `ub_re` 是断言正则);
⑥壳谓词第四档: 剥首尾空白后按“字面相等 ⇎ 前缀 ⇎ 后缀切片 ⇎ 末两 token”判, 一枚序列正则也不跑,
  逐行与采集侧(整行序列正则)⇎ 建条侧(token 形状)两把尺三方对拍;
⑦行号尺第四档: 折平面由“每行一段”的段表 (起, 止, 原行号) 现导, 偏移→行号走段表线性取满足 a≤off 的最后一段
  (建条侧是累积长度表 + bisect ⇎ 发射侧是逐字符行表); 区间→行集合走段表与区间的相交测试;
⑧句界第四档: `(?=[.!?](?: |$))` 的纯前瞻 finditer 出候选, 空格尾巴交给 `[^ ]` 的 search 现跳
  (建条侧逐字符扫 ⇎ 发射侧 `[.!?] +` 的 finditer);
⑨切开针第四档: 不枚举“这一行含不含针”, 也不逐枚量跨度对拍, 而是把每枚针的命中区间直接与段表求交,
  相交行数 >1 才算跨行, 同行重枚按“首行下标”去重(与建条侧的三档读数逐格对拍);
⑩数值抽取第四档: 一条 `\\d+(?:[.,]\\d+)?` 正则取数字段 + “起始左邻是字母数字或点号则整枚作废”的前置筛,
  单位词就地读(建条侧手工扫数字串 ⇎ 发射侧扫到第一枚数字 ⇎ 采集侧一条选择支正则);
⑪内核默认值第四档: 四句式全走 `str.partition` 链(建条侧是游标 find + 就地扫字符 ⇎ 发射侧四条正则级联);
⑫倍增第四轨: `itertools.accumulate` 逐次翻倍列成清单再取末项(建条侧 while 累加 ⇎ 发射侧 2**k 求和);
⑬池代数与锚账: 归属向量走 `Counter` 直方图 ⇎ 共现走“文档下标组合逐枚数”; 锚由条目正文的手写配对扫描现推,
  行号由本遍的段表复现, 候选针由两遍源码的字符串字面量递归收集再过词前/后缀退让档。
每个键与 corpus/_b86flat.json 逐值对拍, 值不符或键缺失一律先收集后汇总; 覆盖不足也要如实报数。"""
import io, os, re, sys, json, ast, glob, difflib, itertools as IT
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
C = u'corpus'
LBL = [u'793', u'1122', u'9293', u'6298', u'lin']
NSRC = 5
TAGS = LBL
IDX = dict((t, n) for n, t in enumerate(LBL))
FAM = [u'old', u'old', u'new', u'new', u'tbl']
OLD = [i for i in range(NSRC) if FAM[i] == u'old']
NEW = [i for i in range(NSRC) if FAM[i] == u'new']
TBL = [i for i in range(NSRC) if FAM[i] == u'tbl']
PATH = [u'%s/raw/tcpRetr/rfc793.txt' % C, u'%s/raw/tcpRetr/rfc1122.txt' % C,
        u'%s/raw/tcpRetr/rfc9293.txt' % C, u'%s/raw/tcpRetr/rfc6298.txt' % C,
        u'%s/raw/tcpRetr/ip-sysctl.txt' % C]
EP = glob.glob(u'%s/babeltele/B86_*.md' % C)
assert len(EP) == 1, EP
ENTRY = EP[0]

FLAT = json.load(io.open(u'%s/_b86flat.json' % C, encoding='utf-8'))
CH = json.load(io.open(u'%s/_b86checks.json' % C, encoding='utf-8'))
DER = json.load(io.open(u'%s/_deriv86.json' % C, encoding='utf-8'))
MEA = json.load(io.open(u'%s/_b86meas.json' % C, encoding='utf-8'))
MS = io.open(u'%s/_mkB86.py' % C, encoding='utf-8').read()
ES = io.open(u'%s/_mk86emit.py' % C, encoding='utf-8').read()

# ---------- 定义从两遍源码的 AST 里摘, 不重新声明 ----------
TABS = (u'OB', u'OBL', u'HEADS', u'HEADSL', u'TAGKIND', u'GRP', u'UNIT', u'UNITS', u'GLUE',
        u'DUR', u'NEEDLES', u'ANSK', u'NEG', u'RP', u'KW', u'KW_SHORT', u'PAIRS', u'PINS', u'PKSUB',
        u'TAIL', u'WS', u'SUB2', u'DVR2', u'OVW')
TAB = {}
for _src in (MS, ES):
    for st in ast.parse(_src).body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
            nm = st.targets[0].id
            if nm in TABS and nm not in TAB:
                try:
                    TAB[nm] = ast.literal_eval(st.value)
                except Exception:
                    try:
                        TAB[nm] = eval(compile(ast.Expression(st.value), '<tab>', 'eval'),
                                       dict(TAB), {u're': re})
                    except Exception:
                        pass
for nm in TABS:
    assert nm in TAB, nm
OB, OBL, HEADS, HEADSL, TAGKIND = TAB[u'OB'], TAB[u'OBL'], TAB[u'HEADS'], TAB[u'HEADSL'], TAB[u'TAGKIND']
UNIT, UNITS, GLUE, DUR = TAB[u'UNIT'], TAB[u'UNITS'], TAB[u'GLUE'], TAB[u'DUR']
GRP, NEEDLES, ANSK = TAB[u'GRP'], TAB[u'NEEDLES'], TAB[u'ANSK']
NEG, RP, KW, KW_SHORT = TAB[u'NEG'], TAB[u'RP'], TAB[u'KW'], TAB[u'KW_SHORT']
PAIRS, PINS, PKSUB, TAIL, WS = TAB[u'PAIRS'], TAB[u'PINS'], TAB[u'PKSUB'], TAB[u'TAIL'], TAB[u'WS']
SUB2, DVR2 = TAB[u'SUB2'], TAB[u'DVR2']

RXS = {}
for _src in (MS, ES):
    for st in ast.parse(_src).body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
            nm = st.targets[0].id
            if nm in (u'TAGR', u'TAGBR', u'TAGRE', u'TAGSHAPE', u'KEYRE', u'RXN', u'SECHDR',
                      u'KEY2', u'TAGSHAPE2', u'TWO_TAG') and nm not in RXS:
                try:
                    RXS[nm] = eval(compile(ast.Expression(st.value), '<rx>', 'eval'),
                                   dict(RXS), {u're': re})
                except Exception:
                    pass
for nm in (u'TAGR', u'TAGBR', u'TAGRE', u'TAGSHAPE', u'KEYRE', u'RXN', u'SECHDR', u'KEY2',
           u'TAGSHAPE2', u'TWO_TAG'):
    assert nm in RXS, nm

# ---------- 前两遍的尺: exec 进来只用于对拍与“键名点的那把尺” ----------
PXR = [u'pnorm', u'fold', u'is_shell_pick', u'_yearish', u'sh_blank', u'sh_ff', u'sh_foot',
       u'sh_hdr793', u'sh_hdr1122', u'sh_ietf', u'sh_hdrnew', u'shell_shape', u'tag_runs',
       u'ub_re', u'tag_strip', u'sent_cuts', u'sent_at', u'_bnd_word', u'_occ', u'tag_token_scan',
       u'kw_union', u'num_pairs', u'np2', u'canon', u'_tabs', u'ub_tab']
_ns = {u're': re, u'NL': NL, u'TAGR': RXS[u'TAGR'], u'TAGBR': RXS[u'TAGBR'],
       u'TAGSHAPE': RXS[u'TAGSHAPE'], u'HEADS': HEADS, u'UNIT': UNIT, u'UNITS': UNITS,
       u'TAIL': TAIL, u'WS': WS}
for _fn in PXR:
    _m = None
    for _src in (MS, ES):
        _m = re.search(u'def ' + _fn + u'\\(.*?\\):.*?\\n(?=\\S)', _src, re.S)
        if _m:
            break
    assert _m, _fn
    exec(_m.group(0), _ns)
for _fn in PXR:
    assert _fn in _ns, _fn
mk_pnorm, mk_fold = _ns[u'pnorm'], _ns[u'fold']
mk_pick_shell = _ns[u'is_shell_pick']
mk_shape = _ns[u'shell_shape']
mk_ub_re = _ns[u'ub_re']
mk_tag_strip = _ns[u'tag_strip']
mk_tag_runs = _ns[u'tag_runs']
mk_sent_cuts, mk_sent_at = _ns[u'sent_cuts'], _ns[u'sent_at']
mk_bnd = _ns[u'_bnd_word']
mk_occ = _ns[u'_occ']
mk_tag_scan = _ns[u'tag_token_scan']
mk_union = _ns[u'kw_union']
mk_np, mk_np2 = _ns[u'num_pairs'], _ns[u'np2']
mk_canon = _ns[u'canon']
mk_ub_tab, mk_tabs = _ns[u'ub_tab'], _ns[u'_tabs']
PRED = {u'sh_blank': _ns[u'sh_blank'], u'sh_ff': _ns[u'sh_ff'], u'sh_foot': _ns[u'sh_foot'],
        u'sh_hdr793': _ns[u'sh_hdr793'], u'sh_hdr1122': _ns[u'sh_hdr1122'], u'sh_ietf': _ns[u'sh_ietf'],
        u'sh_hdrnew': _ns[u'sh_hdrnew']}
MK_SHPREDS = [PRED[u'sh_blank'], PRED[u'sh_ff'], PRED[u'sh_foot'], PRED[u'sh_hdr793'],
              PRED[u'sh_hdr1122'], PRED[u'sh_ietf'], PRED[u'sh_hdrnew']]
MK_PAGESH = [PRED[u'sh_foot'], PRED[u'sh_hdr793'], PRED[u'sh_hdr1122'], PRED[u'sh_ietf'],
             PRED[u'sh_hdrnew']]

# ---------- 本遍自己的尺 ----------
def bytes_of(p):
    return io.open(p, 'rb').read()


BB3 = [bytes_of(p) for p in PATH]
TT3 = [b.decode('utf-8', 'replace') for b in BB3]
_RXNL = re.compile(u'\\n')
_RXRL = re.compile(u'(?<=\\n)')


def ln3(t):
    return _RXNL.split(t)


RAWL3 = [ln3(t) for t in TT3]
L3 = [[y[:-1] if (len(y) > 0 and y[-1] == u'\r') else y for y in RAWL3[i]] for i in range(NSRC)]
WSPAN = re.compile(u'\\S+')


def toks3(s):
    return [(m.start(), m.end()) for m in WSPAN.finditer(s)]


def fold3(s):
    return u' '.join([s[a:b] for a, b in toks3(s)])


def p3(s):
    return fold3(s.lower())


def c3(s, nd):
    return s.count(nd)


def oc3(s, nd):
    return [m.start() for m in re.finditer(re.escape(nd), s)]


def ovl3(s, nd):
    return [m.start() for m in re.finditer(u'(?=' + re.escape(nd) + u')', s)]


LET = frozenset(u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
DIG = frozenset(u'0123456789')
LOWSET = frozenset(u'abcdefghijklmnopqrstuvwxyz')


def m_alpha(s):
    return [c in LET for c in s]


def m_digit(s):
    return [c in DIG for c in s]


def m_alnum(s):
    return [(c in LET or c in DIG) for c in s]


MASK = {u'alpha': m_alpha, u'digit': m_digit, u'alnum': m_alnum}


def ub3(s, w, kind=u'alpha'):
    """整词尺: 前瞻定位 + ASCII 布尔表读邻(建条侧的表认 isalpha, 本遍的表只认 52 枚字母)。"""
    M = MASK[kind](s)
    n, m = len(w), len(s)
    return len([i for i in ovl3(s, w)
                if not (i > 0 and M[i - 1]) and not (i + n < m and M[i + n])])


_RXBRK = re.compile(u'[\\n\\x0b\\x0c\\r\\x1c-\\x1e\\x85\\u2028\\u2029]')


def splitlines3(t):
    """行式第三档: 逐枚行界符切, `\\r\\n` 只算一枚(与 str.splitlines 同定义, 不经 C 函数)。"""
    out, k = [], 0
    for m in _RXBRK.finditer(t):
        a, b = m.start(), m.end()
        if m.group(0) == u'\r' and b < len(t) and t[b] == u'\n':
            b += 1
        out.append(t[k:a])
        k = b
    if k < len(t):
        out.append(t[k:])
    return out


def brk_n3(t):
    return len(splitlines3(t))


def rl_lines(t):
    return [x for x in _RXRL.split(t) if x != u'']


def line_starts(t):
    return [m.start() for m in re.finditer(u'^', t, re.M)]


_LSTART = [line_starts(t) for t in TT3]


def raw_row(i, off):
    """原文件行号: 由 (?m)^ 的行首表线性取“不晚于 off 的最后一枚”。"""
    ls = _LSTART[i]
    k = 0
    while k < len(ls) and ls[k] <= off:
        k += 1
    return k - 1


def face_build(rows, low):
    """(原行号, 文本) → 折平面 ⇎ 段表[(起, 止, 原行号)]: 逐行折平后拼单空格, 空行不占段。"""
    seg, parts = [], []
    pos = 0
    for r, x in rows:
        f = p3(x) if low else fold3(x)
        if f == u'':
            continue
        if parts:
            parts.append(u' ')
            pos += 1
        seg.append((pos, pos + len(f), r))
        parts.append(f)
        pos += len(f)
    return u''.join(parts), seg


def seg_row(seg, off):
    k = -1
    for a, b, r in seg:
        if a <= off:
            k = r
        else:
            break
    return k


def seg_rows(seg, a, b):
    return sorted(set([r for sa, sb, r in seg if sa < b and sb > a]))


def seg_span(seg, a, b):
    rs = seg_rows(seg, a, b)
    return (rs[-1] - rs[0] + 1) if rs else 0


# ---------- 壳谓词第四档: 字面相等 ⇎ 前缀 ⇎ 后缀切片 ⇎ 末两 token ----------
def norm3(x):
    """本遍的“一行几个词”尺: 无参 split 再 join, 不做列表相等。"""
    return u' '.join(x.split())


def _dig3(s):
    return s != u'' and all(c in DIG for c in s)


def s3_blank(x):
    return x.strip() == u''


def s3_ff(x):
    return x == u'\x0c'


def s3_foot(x):
    t = x.split()
    if len(t) < 2:
        return False
    last = t[-1]
    return t[-2][:5] == u'[Page' and len(t[-2]) == 5 and last[-1:] == u']' and _dig3(last[:-1])


def s3_hdr793(x):
    return norm3(x) in (u'September 1981', u'Transmission Control Protocol')


def s3_hdr1122(x):
    t = x.split()
    return len(t) > 1 and t[0][:7] == u'RFC1122' and len(t[0]) == 7


def s3_ietf(x):
    return norm3(x) == u'Internet Engineering Task Force'


def _s3_year(tok):
    return len(tok) == 4 and _dig3(tok) and tok[:2] in (u'19', u'20')


def s3_hdrnew(x):
    t = x.split()
    if not t:
        return False
    if t[0][:14] == u'Internet-Draft' or u' '.join(t[:4]) == u'Internet Engineering Task Force':
        return True
    if not _s3_year(t[-1]):
        return False
    head = [y for y in t[:len(t) - 1] if y[:3] == u'RFC']
    for h in head:
        if len(h) == 7 and _dig3(h[3:]):
            return True
    for k in range(len(t) - 1):
        if t[k] == u'RFC' and len(t[k + 1]) == 4 and _dig3(t[k + 1]):
            return True
    return False


def shell3(x):
    return (s3_blank(x) or s3_ff(x) or s3_foot(x) or s3_hdr793(x) or s3_hdr1122(x)
            or s3_ietf(x) or s3_hdrnew(x))


S3PREDS = [s3_blank, s3_ff, s3_foot, s3_hdr793, s3_hdr1122, s3_ietf, s3_hdrnew]
S3PAGE = [s3_foot, s3_hdr793, s3_hdr1122, s3_ietf, s3_hdrnew]


def digit_runs3(x):
    M = m_digit(x)
    return len([1 for k in range(len(M)) if M[k] and (k == 0 or not M[k - 1])])


def is_pgnum3(x):
    s = x.strip()
    if s == u'':
        return False
    return digit_runs3(x) == 1 and all(c in DIG or c.isspace() for c in x)


def keylin3(x):
    """内核键行第四档: 建条侧是 ^[a-z_][a-z_0-9]* - (INTEGER|BOOLEAN|STRING|DWORD)\\s*$ 一把序列正则,
       本遍不跑正则——按“ - ”分成名字与类型两段, 逐段过 ASCII 类表, 尾空白逐字符退。"""
    k = x.find(u' - ')
    if k <= 0:
        return False
    n = x[:k]
    if n[0] not in LOWSET and n[0] != u'_':
        return False
    for c in n[1:]:
        if c not in LOWSET and c not in DIG and c != u'_':
            return False
    tp = x[k + 3:]
    e = len(tp)
    while e > 0 and tp[e - 1].isspace():
        e -= 1
    return tp[:e] in (u'INTEGER', u'BOOLEAN', u'STRING', u'DWORD')


def default_line3(x):
    k = 0
    while k < len(x) and x[k].isspace():
        k += 1
    return x[k:k + 8] == u'Default:'


# ---------- 编号族第四档: 逐枚词头 find 环 ⇎ 类表读界 ⇎ 两段区间摘除 ----------
UPSET = frozenset(u'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
TKHEADS = [u'MUST', u'SHOULD', u'MAY', u'SHLD', u'ED']
SHEADS = [u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'SHLD', u'ED']


def _word_at(s, k):
    return 0 <= k < len(s) and (s[k] in LET or s[k] in DIG or s[k] == u'_')


def tag_occ(s):
    """编号出现位置表: 逐枚词头 find 环(步长 1, 允许叠合), 数字段就地取最长。
       返回 (词头下标, 数字结束下标, 词头) —— 结束下标可以等于词头尾巴, 那一档就是“数字没跟上来”。"""
    out = []
    for kind in TKHEADS:
        h = kind + u'-'
        i = 0
        while True:
            j = s.find(h, i)
            if j < 0:
                break
            i = j + 1
            e = j + len(h)
            while e < len(s) and s[e] in DIG:
                e += 1
            out.append((j, e, kind))
    return sorted(out)


def _dg(j, e, kind):
    """这一枚编号是否真带数字(数字段非空)。"""
    return e > j + len(kind) + 1


def dash_ok(s, j, e, kind):
    """词界尺: 左不贴字界、右不贴字界、数字至少一枚(= 建条侧 \\b(KIND)-\\d+\\b)。"""
    return _dg(j, e, kind) and not _word_at(s, j - 1) and not _word_at(s, e)


def _cut_apply(s, cuts):
    out, k = [], 0
    for a, b in cuts:
        out.append(s[k:a])
        k = b
    out.append(s[k:])
    return u''.join(out)


def strip_paren4(s):
    """摘 “␠(KIND-数字)” 整对: 大小写不敏感(建条侧 TAGR 带 re.I), 逐位试七枚词头, 长头先试。"""
    cuts, i, n = [], 0, len(s)
    while i < n:
        e = 0
        if i >= 2 and s[i - 1] == u'(' and s[i - 2] == u' ':
            for h in SHEADS:
                if s[i:i + len(h)].lower() == h.lower() and s[i + len(h):i + len(h) + 1] == u'-':
                    k = i + len(h) + 1
                    while k < n and s[k] in DIG:
                        k += 1
                    if k > i + len(h) + 1 and s[k:k + 1] == u')':
                        e = k + 1
                        break
        if e > 0:
            cuts.append((i - 2, e))
            i = e
        else:
            i += 1
    return cuts


def strip_dash4(s):
    """摘裸形 KIND-数字: 大小写敏感(建条侧 TAGBR 不带 re.I), 词界由类表读, 长头先试。"""
    cuts, i, n = [], 0, len(s)
    while i < n:
        e = 0
        if not _word_at(s, i - 1):
            for h in SHEADS:
                if s[i:i + len(h)] == h and s[i + len(h):i + len(h) + 1] == u'-':
                    k = i + len(h) + 1
                    while k < n and s[k] in DIG:
                        k += 1
                    if k > i + len(h) + 1 and not _word_at(s, k):
                        e = k
                        break
        if e > 0:
            cuts.append((i, e))
            i = e
        else:
            i += 1
    return cuts


def tag_strip4(s):
    """去编号第四档: 先摘括号整对、再在摘完的那串上摘裸形(建条侧是同次序的两次 sub), 区间拼接、不跑 sub。"""
    a = _cut_apply(s, strip_paren4(s))
    return _cut_apply(a, strip_dash4(a))


# ---------- 四档面: 本遍的段表通道 ⇎ 建条侧的尺 ----------
FOL3 = [p3(TT3[i]) for i in range(NSRC)]
FOLDX3 = [fold3(TT3[i]) for i in range(NSRC)]
KEEP3 = [[(k, L3[i][k]) for k in range(len(L3[i])) if not shell3(L3[i][k])] for i in range(NSRC)]
ALLR3 = [[(k, L3[i][k]) for k in range(len(L3[i]))] for i in range(NSRC)]
SHP3, SEGSH3 = zip(*[face_build(KEEP3[i], 1) for i in range(NSRC)])
SHPX3, SEGSHX3 = zip(*[face_build(KEEP3[i], 0) for i in range(NSRC)])
WHOLE3, SEGALL3 = zip(*[face_build(ALLR3[i], 1) for i in range(NSRC)])
WHOLEX3, SEGALLX3 = zip(*[face_build(ALLR3[i], 0) for i in range(NSRC)])
SHP3, SEGSH3, SHPX3, SEGSHX3 = list(SHP3), list(SEGSH3), list(SHPX3), list(SEGSHX3)
WHOLE3, SEGALL3, WHOLEX3, SEGALLX3 = list(WHOLE3), list(SEGALL3), list(WHOLEX3), list(SEGALLX3)
SHTAG3 = [tag_strip4(SHP3[i]) for i in range(NSRC)]
SHTAGX3 = [tag_strip4(SHPX3[i]) for i in range(NSRC)]
LOWT3 = [t.lower() for t in TT3]
FOLDX_LOW3 = [x.lower() for x in FOLDX3]

# 建条侧的四档面(exec 进来的那把尺现构), 只用于“同串”判定与逐字符对照
mSHPREDS = [PRED[u'sh_blank'], PRED[u'sh_ff'], PRED[u'sh_foot'], PRED[u'sh_hdr793'],
            PRED[u'sh_hdr1122'], PRED[u'sh_ietf'], PRED[u'sh_hdrnew']]
mFOL = [mk_pnorm(TT3[i]) for i in range(NSRC)]
mFOLDX = [mk_fold(TT3[i]) for i in range(NSRC)]
mSHP = [mk_pnorm(NL.join([x for x in L3[i] if not mk_shape(x)])) for i in range(NSRC)]
mSHPX = [mk_fold(NL.join([x for x in L3[i] if not mk_shape(x)])) for i in range(NSRC)]
mSHTAG = [mk_tag_strip(mSHP[i]) for i in range(NSRC)]
FACEFAIL = []
for i in range(NSRC):
    if FOL3[i] != mFOL[i]:
        FACEFAIL.append([LBL[i], u'全篇折小写'])
    if FOLDX3[i] != mFOLDX[i]:
        FACEFAIL.append([LBL[i], u'全篇保形'])
    if SHP3[i] != mSHP[i]:
        FACEFAIL.append([LBL[i], u'摘壳折小写'])
    if SHPX3[i] != mSHPX[i]:
        FACEFAIL.append([LBL[i], u'摘壳保形'])
    if tag_strip4(SHP3[i]) != mk_tag_strip(mSHP[i]):
        FACEFAIL.append([LBL[i], u'摘壳去编号'])
    if tag_strip4(SHPX3[i]) != mk_tag_strip(mSHPX[i]):
        FACEFAIL.append([LBL[i], u'摘壳去编号保形'])
assert not FACEFAIL, FACEFAIL[:3]
SHELLROWFAIL = []
for i in range(NSRC):
    for k in range(len(L3[i])):
        _r = (shell3(L3[i][k]), mk_pick_shell(L3[i][k]), mk_shape(L3[i][k]))
        if not (_r[0] == _r[1] == _r[2]):
            SHELLROWFAIL.append([LBL[i], k] + list(_r))
assert not SHELLROWFAIL, SHELLROWFAIL[:3]
# 本遍的 digit 表只认 ASCII 十枚, 建条侧的 isdigit() 认 Unicode 十进制; 全库没有一枚 exotic 数字, 两把尺才同定义
EXODIG = [(i, k) for i in range(NSRC) for k in range(len(TT3[i]))
          if TT3[i][k].isdigit() and TT3[i][k] not in DIG]
assert not EXODIG, EXODIG[:3]
# 页码/键行/Default 三把 naive 尺也逐行与建条侧的序列正则对拍
ROWFAIL = []
for i in range(NSRC):
    for x in L3[i]:
        _p = (is_pgnum3(x), x.strip() != u'' and mk_tag_runs(x) == 1
              and not [c for c in x if not (c.isdigit() or c.isspace())])
        _k = (keylin3(x), re.match(u'^[a-z_][a-z_0-9]* - (INTEGER|BOOLEAN|STRING|DWORD)\\s*$', x) is not None)
        _d = (default_line3(x), re.match(u'^\\s*Default:', x) is not None)
        if _p[0] != _p[1] or _k[0] != _k[1] or _d[0] != _d[1]:
            ROWFAIL.append([LBL[i], x[:40], _p, _k, _d])
assert not ROWFAIL, ROWFAIL[:3]

G = {}
BAD = []
OVR = set()
OVRV = []


def dv(x):
    if isinstance(x, dict):
        return dict((str(k), dv(v)) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return [dv(y) for y in x]
    return x


def put(k, v):
    if k in FLAT:
        a, b = dv(FLAT[k]), dv(v)
        if a != b:
            (OVRV if k in OVR else BAD).append((k, a, b))
    G[k] = v
    return v


# ---------- 0. 面量 ⇎ 行式 ⇎ 换页账 ----------
put(u'bytes', [sum(1 for _ in BB3[i]) for i in range(NSRC)])
put(u'bytes_stat', [os.stat(p).st_size for p in PATH])
put(u'cp', [len(TT3[i]) for i in range(NSRC)])
put(u'n_lf', [len([1 for c in TT3[i] if c == NL]) for i in range(NSRC)])
put(u'n_cr', [len([1 for c in TT3[i] if c == u'\r']) for i in range(NSRC)])
put(u'splitnl', [len(RAWL3[i]) for i in range(NSRC)])
put(u'splitlines', [brk_n3(TT3[i]) for i in range(NSRC)])
put(u'readlines', [len(rl_lines(TT3[i])) for i in range(NSRC)])
put(u'ff', [c3(TT3[i], u'\x0c') for i in range(NSRC)])
put(u'ff_led', [len([x for x in L3[i] if x[:1] == u'\x0c']) for i in range(NSRC)])
put(u'ff_alone', [len([x for x in L3[i] if x == u'\x0c']) for i in range(NSRC)])
put(u'ff_before_nl', [len(ovl3(TT3[i], u'\x0c' + NL)) for i in range(NSRC)])
put(u'ff_at_eof', [1 if TT3[i][-1:] == u'\x0c' else 0 for i in range(NSRC)])
put(u'trailing_nl', [1 if TT3[i][-1:] == NL else 0 for i in range(NSRC)])
put(u'blank', [len([x for x in L3[i] if x.strip() == u'']) for i in range(NSRC)])
put(u'nonblank', [len([x for x in L3[i] if x.strip() != u'']) for i in range(NSRC)])
put(u'maxlen', [max([len(x) for x in L3[i]]) for i in range(NSRC)])
put(u'maxlen_scan', [max([len(m.group(0)) for m in re.finditer(u'[^\\n\\r]+', TT3[i])])
                     for i in range(NSRC)])
put(u'tab', [c3(TT3[i], u'\t') for i in range(NSRC)])
put(u'bom', [1 if TT3[i][:1] == u'\ufeff' else 0 for i in range(NSRC)])
put(u'bom_after_fold', [1 if u'\ufeff' in p3(TT3[i][1:]) else 0 for i in range(NSRC)])
NA3 = [[k for k in range(len(TT3[i])) if ord(TT3[i][k]) > 127] for i in range(NSRC)]
put(u'na_total', [len(NA3[i]) for i in range(NSRC)])
put(u'na_codepoints', [sorted(set([ord(TT3[i][k]) for k in NA3[i]])) for i in range(NSRC)])
put(u'utf8_extra', [len(BB3[i]) - len(TT3[i]) for i in range(NSRC)])
put(u'na_lines', [len(set([raw_row(i, k) for k in NA3[i]])) for i in range(NSRC)])
put(u'na_shell_lines', [len(set([raw_row(i, k) for k in NA3[i]
                                 if shell3(L3[i][raw_row(i, k)])])) for i in range(NSRC)])
put(u'na_body_lines', [G[u'na_lines'][i] - G[u'na_shell_lines'][i] for i in range(NSRC)])
put(u'rows_ledger', [G[u'splitlines'][i] - G[u'splitnl'][i] for i in range(NSRC)])
put(u'rows_pred', [G[u'ff_before_nl'][i] - G[u'trailing_nl'][i] for i in range(NSRC)])
put(u'rows_ledger_diff', [G[u'rows_ledger'][i] - G[u'rows_pred'][i] for i in range(NSRC)])
put(u'byte_cp_ledger', [G[u'bytes'][i] - G[u'cp'][i] - G[u'utf8_extra'][i] for i in range(NSRC)])
put(u'line_split_ledger', [G[u'nonblank'][i] + G[u'blank'][i] - G[u'splitnl'][i] for i in range(NSRC)])
put(u'bytes_vs_stat', 0 if G[u'bytes'] == G[u'bytes_stat'] else 1)
put(u'lf_vs_readlines', [G[u'readlines'][i] + G[u'trailing_nl'][i] - G[u'splitnl'][i]
                         for i in range(NSRC)])
put(u'splitlines_ledger', [G[u'splitlines'][i] - G[u'n_lf'][i] - G[u'ff'][i] for i in range(NSRC)])

# ---------- 1. 壳账: 三把尺 ⇎ 七形容斥 ----------
put(u'foot', [len([x for x in L3[i] if s3_foot(x)]) for i in range(NSRC)])
put(u'hdr793', [len([x for x in L3[i] if s3_hdr793(x)]) for i in range(NSRC)])
put(u'hdr1122', [len([x for x in L3[i] if s3_hdr1122(x)]) for i in range(NSRC)])
put(u'ietf_alone', [len([x for x in L3[i] if s3_ietf(x)]) for i in range(NSRC)])
put(u'hdrnew', [len([x for x in L3[i] if s3_hdrnew(x)]) for i in range(NSRC)])
put(u'pgnum', [len([x for x in L3[i] if is_pgnum3(x)]) for i in range(NSRC)])
put(u'keylin', [len([x for x in L3[i] if keylin3(x)]) for i in range(NSRC)])
put(u'default_lines', [len([x for x in L3[i] if default_line3(x)]) for i in range(NSRC)])
put(u'shell_pick', [len([1 for x in L3[i] if mk_pick_shell(x)]) for i in range(NSRC)])
put(u'shell_shape', [len([1 for x in L3[i] if mk_shape(x)]) for i in range(NSRC)])
put(u'shell_pred_diff', [len([1 for x in L3[i] if mk_pick_shell(x) != mk_shape(x)]) for i in range(NSRC)])
put(u'shell_lines', [len([1 for x in L3[i] if shell3(x)]) for i in range(NSRC)])
put(u'body_lines', [len([1 for x in L3[i] if not shell3(x)]) for i in range(NSRC)])
put(u'shape_hits', [sum([len([1 for x in L3[i] if f(x)]) for f in S3PREDS]) for i in range(NSRC)])
put(u'shape_ovl', [sum([max(0, len([1 for f in S3PREDS if f(x)]) - 1) for x in L3[i]])
                   for i in range(NSRC)])
put(u'shape_sum', G[u'shape_hits'])
put(u'shell_ledger', [G[u'shell_lines'][i] - (G[u'shape_sum'][i] - G[u'shape_ovl'][i])
                      for i in range(NSRC)])
put(u'body_shell_ledger', [G[u'body_lines'][i] + G[u'shell_lines'][i] - G[u'splitnl'][i]
                           for i in range(NSRC)])
put(u'pgnum_in_shell', [len([x for x in L3[i] if is_pgnum3(x) and shell3(x)]) for i in range(NSRC)])
put(u'pgnum_naked', [G[u'pgnum'][i] - G[u'pgnum_in_shell'][i] for i in range(NSRC)])

# ---------- 2. 义务词四档 ⇎ 并集尺 ⇎ 编号族 ----------
def ub4(s, w, uni):
    """整词尺第四档: 前瞻 finditer 定位 + 布尔表读邻; uni=1 用 Python 的 isalpha 表, 0 用 ASCII 五十余枚。"""
    M = [c.isalpha() for c in s] if uni else m_alpha(s)
    n, m = len(w), len(s)
    return len([i for i in ovl3(s, w)
                if not (i > 0 and M[i - 1]) and not (i + n < m and M[i + n])])


# 本遍只认 ASCII 字母, 建条侧的表认 isalpha: 九十二号那一枚非 ASCII 字母若贴在义务词边上就会露馅
UBDIFF = []
for i in range(NSRC):
    for k in range(len(OB)):
        for _face, _tier in ((FOLDX3[i], u'折平'), (SHPX3[i], u'摘壳'), (SHTAGX3[i], u'去编号')):
            if ub4(_face, OB[k], 0) != ub4(_face, OB[k], 1):
                UBDIFF.append([LBL[i], OB[k], _tier])
    for x in L3[i]:
        for k in range(len(OB)):
            if ub4(x, OB[k], 0) != ub4(x, OB[k], 1):
                UBDIFF.append([LBL[i], OB[k], u'逐行'])
assert not UBDIFF, UBDIFF[:3]


def kw4(s, heads):
    """并集尺: 三枚词头各扫一遍, 短语里的 MUST 只归一处(界含下划线, 与建条侧 _bnd_word 同定义)。"""
    M = m_alnum(s)
    m = len(s)
    tot = 0
    for h in heads:
        for j in ovl3(s, h):
            a, b = j - 1, j + len(h)
            if not (a >= 0 and (M[a] or s[a] == u'_')) and not (b < m and (M[b] or s[b] == u'_')):
                tot += 1
    return tot


put(u'foldx_ledger', [len(FOLDX3[i]) - len(FOL3[i]) for i in range(NSRC)])
put(u'shpx_ledger', [len(SHPX3[i]) - len(SHP3[i]) for i in range(NSRC)])
put(u'ob_line', [[sum([ub4(x, w, 0) for x in L3[i]]) for w in OB] for i in range(NSRC)])
put(u'ob_fold', [[ub4(FOLDX3[i], w, 0) for w in OB] for i in range(NSRC)])
put(u'ob_sh', [[ub4(SHPX3[i], w, 0) for w in OB] for i in range(NSRC)])
put(u'ob_tag', [[ub4(SHTAGX3[i], w, 0) for w in OB] for i in range(NSRC)])
put(u'ob_ruler_diff', len([1 for i in range(NSRC) for k in range(len(OB))
                           if G[u'ob_sh'][i][k] != mk_ub_re(SHPX3[i], OB[k])]))
put(u'ob_wrap', [G[u'ob_fold'][i][k] - G[u'ob_line'][i][k] for i in range(NSRC)
                 for k in range(len(OB))])
put(u'ob_line_tot', [sum(G[u'ob_line'][i]) for i in range(NSRC)])
put(u'ob_fold_tot', [sum(G[u'ob_fold'][i]) for i in range(NSRC)])
put(u'ob_tag_tot', [sum(G[u'ob_tag'][i]) for i in range(NSRC)])
put(u'ob_lower', [[ub4(FOLDX3[i], w, 0) for w in OBL] for i in range(NSRC)])
put(u'ob_upper_tot', [sum(G[u'ob_sh'][i]) for i in range(NSRC)])
put(u'ob_lower_tot', [sum(G[u'ob_lower'][i]) for i in range(NSRC)])
put(u'kw_allcaps', [kw4(TT3[i], HEADS) for i in range(NSRC)])
put(u'kw_ci', [kw4(LOWT3[i], HEADSL) for i in range(NSRC)])
put(u'kw_lowercase', [G[u'kw_ci'][i] - G[u'kw_allcaps'][i] for i in range(NSRC)])
put(u'kw_union_fold', [kw4(FOLDX3[i], HEADS) for i in range(NSRC)])
put(u'kw_union_fold_low', [kw4(FOLDX_LOW3[i], HEADSL) for i in range(NSRC)])
put(u'ob_nest_ledger', [G[u'ob_fold_tot'][i] - G[u'kw_union_fold'][i] - G[u'ob_fold'][i][1]
                        - G[u'ob_fold'][i][3] for i in range(NSRC)])
put(u'shpx_eq_pnorm', 1 if [p3(x) for x in SHPX3] == SHP3 else 0)


DASH_SP = [tag_occ(TT3[i]) for i in range(NSRC)]


def paren_spaced(s):
    """括号里“词头 + 空格 + 数字 + 右括号”的枚数: 逐枚词头找 '(KIND ' 字面串, 数字就地扫。"""
    c = 0
    for kind in TKHEADS:
        h = u'(%s ' % kind
        i = 0
        while True:
            j = s.find(h, i)
            if j < 0:
                break
            i = j + 1
            e = j + len(h)
            while e < len(s) and s[e] in DIG:
                e += 1
            if e > j + len(h) and e < len(s) and s[e] == u')':
                c += 1
    return c


put(u'tag_paren', [paren_spaced(TT3[i]) for i in range(NSRC)])
put(u'tag_dash', [len([1 for j, e, kd in DASH_SP[i] if dash_ok(TT3[i], j, e, kd)])
                  for i in range(NSRC)])
put(u'tag_kind', [[len([1 for j, e, kd in DASH_SP[i] if kd == w and dash_ok(TT3[i], j, e, kd)])
                   for w in TKHEADS] for i in range(NSRC)])
put(u'tag_max_no', [max([int(TT3[i][j + len(kd) + 1:e]) for j, e, kd in DASH_SP[i]
                         if dash_ok(TT3[i], j, e, kd)] or [0]) for i in range(NSRC)])
put(u'tag_in_paren', [len([1 for j, e, kd in DASH_SP[i] if _dg(j, e, kd)
                           and TT3[i][j - 1:j] == u'(' and TT3[i][e:e + 1] == u')'])
                      for i in range(NSRC)])
put(u'tag_bare', [len([1 for j, e, kd in DASH_SP[i] if _dg(j, e, kd) and TT3[i][j - 1:j] != u'('
                      and (e < len(TT3[i]) and (TT3[i][e].isspace() or TT3[i][e] in u').,;'))])
                  for i in range(NSRC)])


def tag_token4(s):
    """第三把编号尺的第四档: 空白切 token, 剥圈点后按“词头 + '-' + 全数字”判形(不跑 TAGSHAPE)。"""
    n, par, bare = 0, 0, 0
    for w in s.split():
        k = w.strip(u'().,;:')
        c = k.find(u'-')
        if c <= 0 or k[:c] not in TKHEADS or not _dig3(k[c + 1:]):
            continue
        n += 1
        if w[:1] == u'(' and w[-1:] == u')':
            par += 1
        else:
            bare += 1
    return n, par, bare


TT4 = [tag_token4(TT3[i]) for i in range(NSRC)]
put(u'tag_token', [x[0] for x in TT4])
put(u'tag_token_paren', [x[1] for x in TT4])
put(u'tag_token_plain', [x[2] for x in TT4])
put(u'tag_form_ledger', [G[u'tag_in_paren'][i] + G[u'tag_bare'][i] - G[u'tag_dash'][i]
                         for i in range(NSRC)])
put(u'tag_token_ledger', [G[u'tag_token'][i] - G[u'tag_dash'][i] for i in range(NSRC)])


def tag_shape_split(s):
    """编号形状的第四档扫描: 词界一过, 就把“数字没跟上来(推到下一行)”“括号整对被拉开”“方括号套住”三类各数一遍。"""
    apart = nxt = br = 0
    ctx = []
    for j, e, kd in tag_occ(s):
        hl = j + len(kd) + 1
        if _word_at(s, j - 1) or _word_at(s, e):
            continue
        if e == hl:
            m = e
            while m < len(s) and s[m] in u' \t\n':
                m += 1
            if m > e and m < len(s) and s[m] in DIG:
                nxt += 1
            continue
        if s[j - 1:j] == u'(' and s[e:e + 1] != u')':
            apart += 1
            ctx.append(repr(s[j - 2:e + 4]))
        if s[j - 2:j - 1] == u'[':
            br += 1
    return apart, nxt, br, ctx


def tag_cut_scan(s):
    """“切开”那一档不要求数字跟上来: 左贴 '(' 而右不等 ')' 的编号形态全数, 含数字被推到下一行的那些。"""
    return len([1 for j, e, kd in tag_occ(s)
                if not _word_at(s, j - 1) and not _word_at(s, e)
                and s[j - 1:j] == u'(' and s[e:e + 1] != u')'])


TS4 = [tag_shape_split(TT3[i]) for i in range(NSRC)]
put(u'tag_split_manual', [tag_cut_scan(TT3[i]) for i in range(NSRC)])
put(u'tag_kind_ledger', [sum(G[u'tag_kind'][i]) - G[u'tag_dash'][i] for i in range(NSRC)])
put(u'tag_paren_apart', [x[0] for x in TS4])
put(u'tag_num_nextline', [x[1] for x in TS4])
put(u'tag_bracket', [x[2] for x in TS4])
put(u'tag_apart_ctx', [[LBL[i], c] for i, x in enumerate(TS4) for c in x[3]])
put(u'tag_split_ledger', [G[u'tag_dash'][i] - (G[u'tag_in_paren'][i] + G[u'tag_bare'][i])
                          - G[u'tag_paren_apart'][i] for i in range(NSRC)])
put(u'tag_bracket_ledger', [G[u'tag_dash'][i] - G[u'tag_token'][i] - G[u'tag_bracket'][i]
                            for i in range(NSRC)])
put(u'tag_dash_fold', [len([1 for j, e, kd in tag_occ(FOLDX3[i]) if dash_ok(FOLDX3[i], j, e, kd)])
                       for i in range(NSRC)])
put(u'tag_fold_gain', [G[u'tag_dash_fold'][i] - G[u'tag_dash'][i] for i in range(NSRC)])


def tag_nospace4(s):
    """粘连尺: 先把空白逐枚摘净, 再按“左不贴大写与数字(下划线与小写放过) + 词头 + '-' + 数字”数。"""
    c = 0
    for j, e, kd in tag_occ(s):
        if not _dg(j, e, kd):
            continue
        if j > 0 and (s[j - 1] in UPSET or s[j - 1] in DIG):
            continue
        c += 1
    return c


NOSPC3 = [u''.join([c for c in TT3[i] if not c.isspace()]) for i in range(NSRC)]
put(u'tag_nospace', [tag_nospace4(NOSPC3[i]) for i in range(NSRC)])
put(u'tag_nextline_ledger', [G[u'tag_nospace'][i] - G[u'tag_dash'][i] - G[u'tag_num_nextline'][i]
                             for i in range(NSRC)])
put(u'labeled_decl', [c3(FOL3[i], u'individually labeled') for i in range(NSRC)])


put(u'tag_chars', [len(SHP3[i]) - len(SHTAG3[i]) for i in range(NSRC)])

# ---------- 3. 判词针四档(28 枚 × 五份) ----------
NK4 = [p3(z) for z in NEEDLES]
ROWSF3 = [[p3(x) for x in L3[i]] for i in range(NSRC)]
put(u'needle_n', len(NEEDLES))
put(u'role_line', [[len([1 for y in ROWSF3[i] if oc3(y, NK4[k])]) for i in range(NSRC)]
                   for k in range(len(NK4))])
put(u'role_fold', [[c3(FOL3[i], nd) for i in range(NSRC)] for nd in NK4])
put(u'role_sh', [[c3(SHP3[i], nd) for i in range(NSRC)] for nd in NK4])
put(u'role_tag', [[c3(SHTAG3[i], nd) for i in range(NSRC)] for nd in NK4])
put(u'role_line_n', [sum(G[u'role_line'][k][i] for k in range(len(NK4))) for i in range(NSRC)])
put(u'role_fold_n', [sum(G[u'role_fold'][k][i] for k in range(len(NK4))) for i in range(NSRC)])
put(u'role_sh_n', [sum(G[u'role_sh'][k][i] for k in range(len(NK4))) for i in range(NSRC)])
put(u'role_tag_n', [sum(G[u'role_tag'][k][i] for k in range(len(NK4))) for i in range(NSRC)])
put(u'role_gain', [[G[u'role_fold_n'][i] - G[u'role_line_n'][i], G[u'role_sh_n'][i] - G[u'role_fold_n'][i],
                    G[u'role_tag_n'][i] - G[u'role_sh_n'][i]] for i in range(NSRC)])
put(u'role_src', [[LBL[i] for i in range(NSRC) if G[u'role_sh'][k][i] > 0] for k in range(len(NK4))])
put(u'role_probes', G[u'needle_n'] * NSRC)
put(u'wrap_cut', [k for k in range(len(NK4)) if G[u'role_sh'][k] != [0] * NSRC
                  and any(G[u'role_line'][k][i] < G[u'role_sh'][k][i] for i in range(NSRC))])
put(u'wrap_cut_n', len(G[u'wrap_cut']))
put(u'shell_cut', [k for k in range(len(NK4)) if k not in G[u'wrap_cut']
                   and any(G[u'role_fold'][k][i] > G[u'role_sh'][k][i] for i in range(NSRC))])
put(u'tag_cut', [k for k in range(len(NK4))
                 if any(G[u'role_tag'][k][i] != G[u'role_sh'][k][i] for i in range(NSRC))])
put(u'wrap_gain_cells', [G[u'role_fold'][k][i] - G[u'role_line'][k][i]
                         for k in range(len(NK4)) for i in range(NSRC)])
put(u'tag_drop_cells', [max(0, G[u'role_sh'][k][i] - G[u'role_tag'][k][i])
                        for k in range(len(NK4)) for i in range(NSRC)])
put(u'tag_gain_cells', [max(0, G[u'role_tag'][k][i] - G[u'role_sh'][k][i])
                        for k in range(len(NK4)) for i in range(NSRC)])
put(u'tag_move', [[k, LBL[i], G[u'role_sh'][k][i], G[u'role_tag'][k][i]]
                  for k in range(len(NK4)) for i in range(NSRC)
                  if G[u'role_sh'][k][i] != G[u'role_tag'][k][i]])
put(u'tag_gain_needles', [k for k in range(len(NK4))
                          if any(G[u'role_tag'][k][i] > G[u'role_sh'][k][i] for i in range(NSRC))])
put(u'tag_drop_needles', [k for k in range(len(NK4))
                          if any(G[u'role_tag'][k][i] < G[u'role_sh'][k][i] for i in range(NSRC))])
put(u'tag_drop', [G[u'role_sh_n'][i] - G[u'role_tag_n'][i] for i in range(NSRC)])
put(u'tag_gain', [G[u'role_tag_n'][i] - G[u'role_sh_n'][i] for i in range(NSRC)])
put(u'wrap_gain', [sum(G[u'role_fold'][k][i] - G[u'role_line'][k][i] for k in range(len(NK4)))
                   for i in range(NSRC)])
put(u'wrap_gain_tot', sum(G[u'wrap_gain']))
put(u'tag_gain_tot', sum(G[u'role_tag_n'][i] - G[u'role_sh_n'][i] for i in range(NSRC)))

# ---------- 4. 五份答句(本遍的句界尺 ⇎ 段表行号尺) ----------
_RXSP = re.compile(u'(?=[.!?](?: |$))')
_RXNOSP = re.compile(u'[^ ]')


def _tail_skip(face, k, n):
    """从 k 起跳过一整串空格: 用 `[^ ]` 的 search 现读落点(建条侧是 while 逐枚比 face[j]==' ')。"""
    v = _RXNOSP.search(face, k, n)
    return n if v is None else v.start()


def sent4(face):
    """句界第四档: 纯前瞻 finditer 出候选, 尾巴上的空格靠 `[^ ]` search 一跳到位(建条侧逐字符扫 ⇎ 采集侧一条 re.split)。"""
    n, cuts, start = len(face), [], 0
    for m in _RXSP.finditer(face):
        k = m.start()
        j = _tail_skip(face, k + 1, n)
        cuts.append((start, k + 1))
        start = j
    if start < n:
        cuts.append((start, n))
    return [(a, b) for a, b in cuts if face[a:b].strip() != u'']


def sent_at4(spans, at):
    """落在哪一句: 数“起头不晚于 at 的句段”得到下标(建条侧是顺序扫到第一格包含 at 的)。"""
    k = len([1 for a, b in spans if a <= at]) - 1
    if 0 <= k < len(spans) and spans[k][0] <= at < spans[k][1]:
        return spans[k]
    return spans[0][0], spans[-1][1]


SPX4 = [sent4(x) for x in SHPX3]
SENT_LO4 = [[p3(SHPX3[i][a:b].strip()) for a, b in SPX4[i]] for i in range(NSRC)]
for i in range(NSRC):
    assert sent4(mSHPX[i]) == mk_sent_cuts(mSHPX[i]), u'句界两把尺不等: ' + LBL[i]
    assert SENT_LO4[i] == [mSHP[i][a:b] for a, b in mk_sent_cuts(mSHP[i])], u'两档面句列表不等'
    assert SENT_LO4[i] == [SHP3[i][a:b] for a, b in sent4(SHP3[i])], u'保形折小写两档句列表不等'
ANSQ = [p3(z) for z in ANSK]
put(u'ans_needle', ANSK)
S0 = [SHP3[i].find(ANSQ[i]) for i in range(NSRC)]
assert min(S0) >= 0, u'答句针在本遍摘壳面上读不到'
SB = [sent_at4(SPX4[i], S0[i]) for i in range(NSRC)]
SENT4 = [SHPX3[i][a:b] for i, (a, b) in enumerate(SB)]
put(u'ans_line', [seg_row(SEGSH3[i], S0[i]) for i in range(NSRC)])
put(u'ans_sent', SENT4)
put(u'ans_words', [len(x.split()) for x in SENT4])
put(u'ans_chars', [len(x) for x in SENT4])
put(u'ans_sent_line', [seg_row(SEGSH3[i], SB[i][0]) for i in range(NSRC)])
put(u'ans_sent_end', [seg_row(SEGSH3[i], SB[i][1] - 1) for i in range(NSRC)])
put(u'ans_sent_span', [G[u'ans_sent_end'][i] - G[u'ans_sent_line'][i] + 1 for i in range(NSRC)])
put(u'ans_needle_line', [len([1 for y in ROWSF3[i] if oc3(y, ANSQ[i])]) for i in range(NSRC)])
put(u'ans_shell_rows', [len([k for k in range(G[u'ans_sent_line'][i], G[u'ans_sent_end'][i] + 1)
                             if shell3(L3[i][k])]) for i in range(NSRC)])
put(u'ans_page_rows', [len([k for k in range(G[u'ans_sent_line'][i], G[u'ans_sent_end'][i] + 1)
                            if any(f(L3[i][k]) for f in S3PAGE)]) for i in range(NSRC)])
put(u'ans_ob', [[ub4(SENT4[i], w, 0) for w in OB] for i in range(NSRC)])
put(u'ans_tag_n', [len([1 for j, e, kd in tag_occ(SENT4[i]) if dash_ok(SENT4[i], j, e, kd)])
                   for i in range(NSRC)])
put(u'na_in_ans', [len([1 for c in SENT4[i] if ord(c) > 127]) for i in range(NSRC)])

# ---------- 5. 段落对照: 四行滑窗定位 ⇎ 两把句尺 ⇎ difflib 两种账 ----------
def cut_re4(face):
    """句界第五档(对“采集侧那条 re.split”的档): 标点后必须真有空格才切, 不吃串尾, 切出的片段不做过滤。"""
    n, cuts, start, k = len(face), [], 0, 0
    while k + 1 < n:
        if face[k] in u'.!?' and face[k + 1] == u' ':
            j = _tail_skip(face, k + 1, n)
            cuts.append((start, k + 1))
            start = k = j
            continue
        k += 1
    if start < n:
        cuts.append((start, n))
    return cuts


def sents4(lines):
    face = p3(NL.join(lines))
    return [p3(face[a:b]) for a, b in cut_re4(face) if face[a:b] != u'']


def sents4_char(face):
    """句子表第二把尺: 前瞻句界 + 逐段 strip 再折平(建条侧的 sent_cuts 是同一定义的游标扫)。"""
    return [p3(face[a:b].strip()) for a, b in sent4(face)]


CANON4 = [(u'implementers', u'implementors'), (u'acknowledgment', u'acknowledgement'),
          (u'endpoint', u'site')]


def canon4(z):
    """归拼第四档: 一次左到右扫, 每步在替身表里取“就地最长匹配”写字面替身(建条侧是三次 str.replace 串链)。"""
    out, k, n = [], 0, len(z)
    while k < n:
        hit = None
        for a, b in CANON4:
            if z.startswith(a, k) and (hit is None or len(a) > len(hit[0])):
                hit = (a, b)
        if hit is None:
            out.append(z[k])
            k += 1
        else:
            out.append(hit[1])
            k += len(hit[0])
    return u''.join(out)


def lfind4(i, nd, frm=0):
    """段端点第四档: 四行滑窗先过 16 字前缀针, 窗口面由段表现导, 偏移→原行号走 seg_row(建条侧是累积长度 + bisect)。"""
    q, rows = p3(nd)[:16], len(L3[i])
    for k in range(frm, rows):
        if q not in p3(NL.join(L3[i][k:k + 4])):
            continue
        face, seg = face_build([(k + m, L3[i][k + m]) for m in range(min(4, rows - k))], True)
        s0 = face.find(p3(nd))
        if s0 >= 0:
            return seg_row(seg, s0)
    return -1


def cut_at4(lines, stop):
    """段尾闸第四档: 先一次数出全部命中行再取首枚下标切片(建条侧是 enumerate 里遇中就 return)。"""
    q = p3(stop)
    hits = [k for k in range(len(lines)) if q in p3(lines[k])]
    return lines[:hits[0]] if hits else lines[:]


def tag_paren5(s):
    """去编号第三档: 只摘“空格+左括号+五位单词头-数字+右括号”的整对, 大小写不论, 两词头(MUST NOT)不认。"""
    n, cuts, k = len(s), [], 0
    while k + 1 < n:
        if s[k] == u' ' and s[k + 1] == u'(':
            end = -1
            for h in TKHEADS:
                j = k + 2 + len(h)
                if s[k + 2:k + 2 + len(h)].upper() != h or s[j:j + 1] != u'-':
                    continue
                d = j + 1
                while d < n and s[d] in DIG:
                    d += 1
                if d > j + 1 and s[d:d + 1] == u')':
                    end = d + 1
                    break
            if end > 0:
                cuts.append((k, end))
                k = end
                continue
        k += 1
    return _cut_apply(s, cuts)


_RXBARE = re.compile(u'\\b(?:MUST|SHOULD|MAY|SHLD|ED)-[0-9]+\\b')


def _word_ch(c):
    return c in LET or c in DIG or c == u'_'


def bare_tag_n4(s):
    """裸编号尺第四档: 逐位试五枚大写词头, 命中后要求左邻非词字符 ⇎ 紧跟 '-' ⇎ 一串数字 ⇎ 数字尾非词字符。"""
    n, k, c = len(s), 0, 0
    while k < n:
        end = -1
        for h in TKHEADS:
            j = k + len(h)
            if s[k:j] != h or (k > 0 and _word_ch(s[k - 1])) or s[j:j + 1] != u'-':
                continue
            d = j + 1
            while d < n and s[d] in DIG:
                d += 1
            if d > j + 1 and not (d < n and _word_ch(s[d])):
                end = d
                break
        if end < 0:
            k += 1
        else:
            c += 1
            k = end
    return c


S1 = [lfind4(1, u'The following procedure MUST be used to handle excessive')]
E1 = [lfind4(1, u'give up on the open attempt) sooner, of course')]
S2 = [lfind4(2, u'The following procedure MUST be used to handle excessive')]
E2 = [lfind4(2, u'give up on the open attempt) sooner, of course')]
assert min(S1 + E1 + S2 + E2) >= 0, u'段落端点未找到'
BL1 = cut_at4(L3[1][S1[0]:E1[0] + 1], u'4.2.3.6')
BL2 = cut_at4(L3[2][S2[0]:E2[0] + 1], u'3.8.4.')
FB1, FB2 = p3(NL.join(BL1)), p3(NL.join(BL2))
for i, nd in ((1, u'The following procedure MUST be used to handle excessive'),
              (1, u'give up on the open attempt) sooner, of course'),
              (2, u'The following procedure MUST be used to handle excessive'),
              (2, u'give up on the open attempt) sooner, of course')):
    assert lfind4(i, nd) == lfind4(i, nd, lfind4(i, nd)), u'端点从自身行起再找应同值: ' + nd
assert [x for x in BL1 if p3(u'4.2.3.6') in p3(x)] == [] and [x for x in BL2 if p3(u'3.8.4.') in p3(x)] == []
put(u'ovl_rows', [len(BL1), len(BL2)])
put(u'ovl_shell', [len([1 for x in BL1 if shell3(x)]), len([1 for x in BL2 if shell3(x)])])
s1, s2 = sents4(BL1), sents4(BL2)
s1c, s2c2 = sents4_char(FB1), sents4_char(FB2)
s2c = [tag_paren5(z).strip() for z in s2]
for f in (FB1, FB2):
    assert sent4(f) == mk_sent_cuts(f), u'段面上两把句尺不等'
for z in s2:
    assert tag_paren5(z) == RXS[u'TAGRE'].sub(u'', z), u'去编号两把尺不等: ' + z
for z in s1 + s2:
    assert canon4(z) == mk_canon(z), u'归拼两把尺不等: ' + z
put(u'ovl_s1', len(s1))
put(u'ovl_s2', len(s2))
put(u'ovl_s1_char', len(s1c))
put(u'ovl_s2_char', len(s2c2))
put(u'ovl_splitter_diff', abs(len(s1) - len(s1c)) + abs(len(s2) - len(s2c2)))
put(u'ovl_splitter_list', 1 if (s1 == s1c and s2 == s2c2) else 0)
put(u'ovl_same_raw', len([z for z in s2 if z in s1]))
put(u'ovl_same_tag', len([z for z in s2c if z in s1]))
put(u'ovl_same_canon', len([z for z in s2c if canon4(z) in [canon4(y) for y in s1]]))
put(u'ovl_new', G[u'ovl_s2'] - G[u'ovl_same_tag'])
WA = [p3(FB1[a:b]) for a, b in toks3(FB1)]
WB = [p3(FB2[a:b]) for a, b in toks3(FB2)]
put(u'blk_words', [len(WA), len(WB)])
sm = difflib.SequenceMatcher(None, WA, WB, autojunk=False)
BLKS = sm.get_matching_blocks()
OPS = sm.get_opcodes()
BQ = sum([z.size for z in BLKS if z.size])
OQ = sum([z[2] - z[1] for z in OPS if z[0] == u'equal'])
assert BQ == OQ, u'相同词两把尺不等'
assert len([z for z in BLKS if z.size]) == len([z for z in OPS if z[0] == u'equal'])
assert max([z.size for z in BLKS]) == max([z[2] - z[1] for z in OPS if z[0] == u'equal'])
put(u'blk_equal_runs', len([z for z in BLKS if z.size]))
put(u'blk_equal_words', BQ)
put(u'blk_longest', max([z.size for z in BLKS]))
put(u'blk_replace', len([op for op in OPS if op[0] == u'replace']))
put(u'blk_op_equal', OQ)
put(u'blk_op_delete', sum([z[2] - z[1] for z in OPS if z[0] == u'delete']))
put(u'blk_op_insert', sum([z[4] - z[3] for z in OPS if z[0] == u'insert']))
put(u'blk_op_rep_a', sum([z[2] - z[1] for z in OPS if z[0] == u'replace']))
put(u'blk_op_rep_b', sum([z[4] - z[3] for z in OPS if z[0] == u'replace']))
put(u'blk_op_n', len(OPS))
AJ = sum([z[2] - z[1] for z in difflib.SequenceMatcher(None, WA, WB, autojunk=True).get_opcodes()
          if z[0] == u'equal'])
assert AJ == sum([z.size for z in difflib.SequenceMatcher(None, WA, WB, autojunk=True).get_matching_blocks()])
put(u'blk_autojunk_diff', AJ - G[u'blk_equal_words'])
put(u'blk_drop_words', G[u'blk_words'][0] - G[u'blk_equal_words'])
put(u'blk_insert_words', G[u'blk_words'][1] - G[u'blk_equal_words'])
put(u'blk_form_ledger', [BQ - G[u'blk_op_equal'],
                         G[u'blk_words'][0] - (G[u'blk_op_equal'] + G[u'blk_op_delete'] + G[u'blk_op_rep_a']),
                         G[u'blk_words'][1] - (G[u'blk_op_equal'] + G[u'blk_op_insert'] + G[u'blk_op_rep_b'])])
put(u'blk_chars', [len(FB1), len(FB2)])
assert tag_strip4(FB2) == mk_tag_strip(FB2), u'去编号面两把尺不等'
put(u'blk_tag_chars', len(FB2) - len(tag_strip4(FB2)))
B2 = NL.join(BL2)
assert bare_tag_n4(B2) == len(_RXBARE.findall(B2)), u'裸编号两把尺不等'
put(u'blk_tag_n', bare_tag_n4(B2))
put(u'blk_is_substring', 1 if FB2 in FB1 else 0)
EV = u'send the segment at the front of the retransmission queue again'
NEV = p3(EV)
for i in range(NSRC):
    assert c3(FOL3[i], NEV) == len(oc3(FOL3[i], NEV)), u'事件句计数两把尺不等: ' + LBL[i]
put(u'ev_same', [1 if c3(FOL3[i], NEV) else 0 for i in range(NSRC)])
put(u'ev_n', [c3(FOL3[i], NEV) for i in range(NSRC)])
put(u'oxford_old', [c3(FOL3[0], u'closed state and return'), c3(FOL3[2], u'closed state and return')])
put(u'oxford_new', [c3(FOL3[0], u'closed state, and return'), c3(FOL3[2], u'closed state, and return')])
print(u'5 段落 %d⇎%d 行 ⇎ 句 %d⇎%d ⇎ 逐字同 %d ⇎ 去编号同 %d ⇎ 归拼同 %d ⇎ 相同词 %d/%d 段' % (
      G[u'ovl_rows'][0], G[u'ovl_rows'][1], G[u'ovl_s1'], G[u'ovl_s2'], G[u'ovl_same_raw'],
      G[u'ovl_same_tag'], G[u'ovl_same_canon'], G[u'blk_equal_words'], G[u'blk_equal_runs']))

# ---------- 6. 内核键值表: 键行两档 ⇎ 四句式 partition 链 ⇎ 发射侧四式正则 ----------
KTYPES = {True: (u'INTEGER', u'BOOLEAN', u'STRING', u'DWORD'),
          False: (u'integer', u'boolean', u'string', u'dword')}
STOP1 = u' .,;)'
NAMERX = (u'retrans', u'retries', u'retry', u'rto', u'timeout')
BODYW = (u'retransmission', u'retransmit', u'timeout', u'attempts')
SHAPES = [u'Default:', u'default value is', u'default value of', u'借参考句', u'无']


def key_name4(x, up):
    """键行第四档(上排类型)⇎ 第五档(小写类型, 走折平面): 只认第一枚 “ - ” 分界, 名字逐字符过 ASCII 小写表,
       类型逐字符退掉尾空白后与四元组比字面; 建条侧是一把序列正则 ⇎ 发射侧是另一把小写正则。"""
    k = x.find(u' - ')
    if k <= 0:
        return None
    n = x[:k]
    if n[0] not in LOWSET and n[0] != u'_':
        return None
    for c in n[1:]:
        if c not in LOWSET and c not in DIG and c != u'_':
            return None
    tp = x[k + 3:]
    e = len(tp)
    while e > 0 and tp[e - 1].isspace():
        e -= 1
    return n if tp[:e] in KTYPES[up] else None


def _parts4(s, kw):
    """kw 每枚出现之后的尾串, 按 partition 链一段段取(建条侧是对同一串反复 find 取位置)。"""
    outs, rest = [], s
    while True:
        a, f, b = rest.partition(kw)
        if not f:
            return outs
        outs.append(b)
        rest = b


def _tok4(s, skip, stop):
    """先跳 skip 类, 再读到 stop 类为止: 整段是切片, 不做逐字符累加。"""
    i, n = 0, len(s)
    while i < n and s[i] in skip:
        i += 1
    j = i
    while j < n and s[j] not in stop:
        j += 1
    return s[i:j]


def defval4(s):
    """四句式级联第四档: 四式全走 str.partition 链(建条侧是游标 find + 就地扫字符 ⇎ 发射侧是四条正则级联)。"""
    sl = s.lower()
    for tail in _parts4(sl, u'default:'):
        v = _tok4(tail, WS, STOP1)
        if v != u'':
            return (v, u'Default:')
    for kw in (u'default value is', u'default value of'):
        for tail in _parts4(sl, kw + u' '):
            v = _tok4(tail, WS, WS)
            if v != u'':
                return (v, kw)
    for tail in _parts4(sl, u'at least '):
        M = m_digit(tail)
        d = 0
        while d < len(M) and M[d]:
            d += 1
        if d == 0:
            continue
        t = tail.find(TAIL, d)
        if t < 0:
            continue
        if [_c for _c in set(tail[d:t]) if not _c.isalpha() and _c != u' ']:
            continue
        return (tail[:d], u'借参考句')
    return (None, u'无')


def defval4_rows(lines):
    """同一级联的逐行档: 先逐行读, 读到就带档名返回(硬换行把句式切成两半时这一档读不到)。"""
    for x in lines:
        v, sh = defval4(x)
        if v is not None:
            return (v, sh)
    return (None, u'无')


def dv2_4(s):
    """四式正则档: 四条都跑一遍再取第一枚命中(发射侧是 for+if 边跑边停)。"""
    sl = p3(s)
    got = [(rx.search(sl), sh) for rx, sh in DVR2]
    hit = [(m, sh) for m, sh in got if m is not None]
    return (hit[0][0].group(1), hit[0][1]) if hit else (None, u'无')


KEYS4, BODY4, cur4 = [], {}, None
for x in L3[4]:
    assert (key_name4(x, True) is not None) == keylin3(x), x
    nm = key_name4(x, True)
    if nm is not None:
        cur4 = nm
        KEYS4.append(nm)
        BODY4[nm] = []
    elif cur4 is not None:
        BODY4[cur4].append(x)
HD4 = [(r, key_name4(p3(L3[4][r]), False)) for r in range(len(L3[4]))]
HD4 = [(r, n) for r, n in HD4 if n is not None]
NWIN4, LAST4 = {}, {}
for t in range(len(HD4)):
    r, n = HD4[t]
    NWIN4[n] = NWIN4.get(n, 0) + 1
    LAST4[n] = (r + 1, HD4[t + 1][0] if t + 1 < len(HD4) else len(L3[4]))
BLK4 = dict((n, p3(NL.join([L3[4][x] for x in range(LAST4[n][0], LAST4[n][1])]))) for n in LAST4)
NB4 = dict((n, LAST4[n][1] - LAST4[n][0]) for n in LAST4)
CNT4 = Counter(KEYS4)
DUP4 = sorted([k for k in CNT4 if CNT4[k] > 1])
assert len(HD4) == len(KEYS4), u'两档键行数不等'
assert sorted(CNT4) == sorted(LAST4), u'两档键名集不等'
assert dict((k, CNT4[k]) for k in CNT4 if CNT4[k] > 1) == dict((k, NWIN4[k]) for k in NWIN4
                                                               if NWIN4[k] > 1), u'两档重名账不等'
REL4 = [k for k in KEYS4 if any(w in k for w in NAMERX)]
REL24 = [k for k in REL4 if any([w in p3(u' '.join(BODY4[k])) for w in BODYW])]
RELP4 = sorted(set([k for k in KEYS4 if any(s in k for s in PKSUB)]))
RELX4 = sorted(set(REL24))
UNIV4 = sorted(set(RELP4) | set(RELX4))
RLN4 = sorted([k for k in LAST4 if any(w in k for w in NAMERX) and any([w in BLK4[k] for w in BODYW])])
RLP4 = sorted([k for k in LAST4 if any(s in k for s in SUB2)])
UN4 = sorted(set(RLP4) | set(RLN4))
BOTH4 = len(set(RLP4) & set(RLN4))
assert RLN4 == RELX4, u'双判相关键两档名单不等'
assert RLP4 == RELP4, u'单判相关键两档名单不等'
assert UN4 == UNIV4, u'两把名尺并集不等'
put(u'lin_keys_total', len(KEYS4))
put(u'lin_keys_uniq', len(set(KEYS4)))
put(u'lin_key_dup_names', DUP4)
put(u'lin_key_dup_ledger', len(KEYS4) - len(set(KEYS4)) - len(DUP4))
put(u'lin_rel_pick_names', RELP4)
put(u'lin_rel_keys', len(RELX4))
put(u'lin_rel_names', RELX4)
put(u'lin_rel_names_cmp', sorted(REL24))
put(u'lin_rel_dropped', sorted(set(REL4) - set(REL24)))
put(u'lin_body_lines', sum([len(BODY4[k]) for k in RELX4]))
put(u'lin_default_lines', G[u'default_lines'][4])
DVP4 = dict((k, defval4(u' '.join(u' '.join(BODY4[k]).split()))) for k in UNIV4)
DVL4 = dict((k, defval4_rows(BODY4[k])) for k in UNIV4)
DVS4 = dict((k, defval4(NL.join(BODY4[k]))) for k in UNIV4)
DV4 = dict((k, DVP4[k]) for k in RELX4)
DV24 = dict((k, dv2_4(BLK4[k])) for k in UN4)
DVL24 = dict((k, defval4_rows([L3[4][x] for x in range(LAST4[k][0], LAST4[k][1])])) for k in UN4)
for k in UN4:
    assert DVP4[k] == DV24[k], u'四式级联两档不同结果: ' + k
    assert DVL4[k] == DVL24[k], u'四式逐行两档不同结果: ' + k
put(u'lin_rel_union', len(UNIV4))
put(u'lin_rel_both', len(set(RELP4) & set(RELX4)))
put(u'lin_defaults_pick', dict((k, DVP4[k][0]) for k in RELP4))
put(u'lin_shape_pick', dict((k, DVP4[k][1]) for k in RELP4))
put(u'lin_defaults_line', dict((k, DVL4[k][0]) for k in UNIV4))
put(u'lin_defaults_raw', dict((k, DVP4[k][0]) for k in RELX4))
put(u'lin_defaults', dict((k, (DV4[k][0] or u'').rstrip(u'.,;')) for k in RELX4))
put(u'lin_val_punct', len([k for k in UNIV4 if DVP4[k][0] is not None
                           and DVP4[k][0] != DVP4[k][0].rstrip(u'.,;')]))
put(u'lin_wrap_gain', sorted([k for k in UNIV4 if DVP4[k][0] and not DVL4[k][0]]))
put(u'lin_split_gain', sorted([k for k in UNIV4 if DVP4[k][0] and not DVS4[k][0]]))
put(u'lin_shape', dict((k, DV4[k][1]) for k in RELX4))
put(u'lin_shape_n', [len([k for k in RELX4 if DV4[k][1] == s]) for s in SHAPES])
put(u'lin_dv_none', len([k for k in RELX4 if DV4[k][0] is None]))
put(u'lin_numvals', sorted(set([v for v in G[u'lin_defaults'].values()
                                if v != u'' and all([c in DIG for c in v])])))
put(u'lin_hexvals', [v for v in G[u'lin_defaults_pick'].values() if v is not None and u'x' in v])
put(u'lin_default_str', tuple([G[u'lin_defaults'].get(u'tcp_retries1'), G[u'lin_defaults'].get(u'tcp_retries2'),
                               G[u'lin_defaults'].get(u'tcp_syn_retries'),
                               G[u'lin_defaults'].get(u'tcp_synack_retries')]))
put(u'kn2_keys', len(HD4))
put(u'kn2_uniq', len(NWIN4))
put(u'kn2_dups', sorted([k for k in NWIN4 if NWIN4[k] > 1]))
put(u'kn2_rel', RLN4)
put(u'kn2_pick', RLP4)
put(u'kn2_keys_close', len(HD4) - G[u'lin_keys_total'])
put(u'kn2_dup_close', len(set(G[u'kn2_dups']) ^ set(G[u'lin_key_dup_names'])))
put(u'kn2_rel_close', len(set(RLN4) ^ set(G[u'lin_rel_names'])))
put(u'kn2_pick_close', len(set(RLP4) ^ set(G[u'lin_rel_pick_names'])))
put(u'kn2_body_rows', sum([NB4[k] for k in RLN4]))
put(u'kn2_body_close', sum([NB4[k] for k in RLN4]) - G[u'lin_body_lines'])
put(u'kn2_union', len(UN4))
put(u'kn2_union_close', len(UN4) - G[u'lin_rel_union'])
put(u'kn2_ie_close', len(UN4) - (len(RLP4) + len(RLN4) - BOTH4))
put(u'kn2_hdr_rows', len(HD4))
put(u'kn2_last_hdr', HD4[-1][0])
put(u'kn2_dv', dict((k, (DV24[k][0] or u'').rstrip(u'.,;')) for k in RLN4))
put(u'kn2_shape', dict((k, DV24[k][1]) for k in RLN4))
put(u'kn2_shape_n', [len([k for k in RLN4 if DV24[k][1] == s]) for s in SHAPES])
put(u'kn2_dv_diff', sorted([k for k in RLN4 if G[u'kn2_dv'][k] != G[u'lin_defaults'][k]
                            or G[u'kn2_shape'][k] != G[u'lin_shape'][k]]))
put(u'kn2_shape_close', [a - b for a, b in zip(G[u'kn2_shape_n'], G[u'lin_shape_n'])])
put(u'kn2_default_str', tuple([G[u'kn2_dv'].get(u'tcp_retries1'), G[u'kn2_dv'].get(u'tcp_retries2'),
                               G[u'kn2_dv'].get(u'tcp_syn_retries'),
                               G[u'kn2_dv'].get(u'tcp_synack_retries')]))
put(u'kn2_wrap_gain', sorted([k for k in UN4 if DV24[k][0] and not DVL24[k][0]]))
put(u'kn2_wrap_close', len(set(G[u'kn2_wrap_gain']) ^ set(G[u'lin_wrap_gain'])))
put(u'kn2_none', len([k for k in RLN4 if G[u'kn2_dv'][k] == u'']))
put(u'kn2_numvals', sorted(set([v for v in G[u'kn2_dv'].values() if v != u'' and all([c in DIG for c in v])])))
put(u'kn2_hex', sorted(set([(DV24[k][0] or u'') for k in RLP4 if u'x' in (DV24[k][0] or u'')])))
put(u'lin_def_diff', [[k, G[u'lin_defaults_pick'][k], MEA[u'lin_defaults'].get(k),
                       G[u'lin_shape_pick'][k], MEA[u'lin_default_shape'].get(k)]
                      for k in sorted(G[u'lin_defaults_pick'])
                      if G[u'lin_defaults_pick'][k] != MEA[u'lin_defaults'].get(k)
                      or G[u'lin_shape_pick'][k] != MEA[u'lin_default_shape'].get(k)])
print(u'6 内核: 键行 %d⇎%d(两档) ⇎ 去重 %d ⇎ 双判 %d ⇎ 单判 %d ⇎ 并集 %d ⇎ 句式档 %s ⇎ 无值 %d' % (
      G[u'lin_keys_total'], G[u'kn2_keys'], G[u'lin_keys_uniq'], len(RLN4), len(RLP4), len(UN4),
      G[u'lin_shape_n'], G[u'lin_dv_none']))

# ---------- 7. 倍增等式: accumulate 末项 ⇎ 幂清单求和, 读数两档(partition ⇎ 游标扫) ----------
def sum_last4(N, rto=1):
    """倍增第四轨: 逐次翻倍列成清单, 累计和取 accumulate 的末项(建条侧 while 累加 ⇎ 发射侧 2**k 求和)。"""
    terms = [rto * 2 ** k for k in range(N)]
    return list(IT.accumulate(terms))[-1] if terms else 0


def sum_kill4(N, rto=1):
    return sum_last4(N + 1, rto)


def geo_sum4(N, rto=1):
    """闭式那一把: rto·(2^N − 1)。与上一轨逐行同数才入账。"""
    return rto * (2 ** N - 1)


def dbl_b4(N, rto=1):
    """倍增第五轨(发射侧形状): 幂清单求和, 不走 accumulate。"""
    return sum([rto * 2 ** k for k in range(N)])


def num_at4(s, kw, unit, opt_sp):
    """读数第四档: partition 取 kw 的每枚出现, 只有紧跟(至多一枚空格)数字串、数字串后又紧跟 unit 才算命中。"""
    for tail in _parts4(s, kw):
        i = 1 if (opt_sp and tail[:1] == u' ') else 0
        j = i
        while j < len(tail) and tail[j] in DIG:
            j += 1
        if j == i:
            continue
        if unit == u'':
            return tail[i:j]
        if tail[j:j + 1 + len(unit)] == u' ' + unit or tail[j:j + len(unit)] == unit:
            return tail[i:j]
    return None


def num_run4(s, kw):
    """读数第五档: 定位短语后向后扫到第一枚数字, 吃掉整串数字(小数点仅当后面还是数字), 连单位都不看。"""
    p = s.find(kw)
    assert p >= 0, kw
    k = p
    while k < len(s) and s[k] not in DIG:
        k += 1
    m = k
    while m < len(s) and (s[m] in DIG or (s[m] == u'.' and m + 1 < len(s) and s[m + 1] in DIG)):
        m += 1
    return (s[k:m] if m > k else None), m


def num_after_b4(s, kw):
    return num_run4(s, kw)[0]


def sec_tokens4(s):
    """面上印出的 “Nseconds” 连写: 逐枚极大数字串后紧跟 unit 才算(建条侧是一条 [0-9]+seconds 正则)。"""
    out, k, n = [], 0, len(s)
    while k < n:
        if s[k] in DIG:
            j = k
            while j < n and s[j] in DIG:
                j += 1
            if s[j:j + 7] == u'seconds':
                out.append(s[k:j] + u'seconds')
            k = j
            continue
        k += 1
    return out


def dec_secs4(s):
    """小数秒读数第四档: 极大数字串 + '.' + 数字串, 后面至少一枚空格再接 seconds, 取第一枚。"""
    k, n = 0, len(s)
    while k < n:
        if s[k] not in DIG:
            k += 1
            continue
        j = k
        while j < n and s[j] in DIG:
            j += 1
        if j >= n or s[j] != u'.':
            k = j
            continue
        d = j + 1
        while d < n and s[d] in DIG:
            d += 1
        if d == j + 1:
            k = d
            continue
        g = d
        while g < n and s[g] == u' ':
            g += 1
        if g > d and s[g:g + 7] == u'seconds':
            return s[k:d], g
        k = d
    return None, 0


for i in range(NSRC):
    assert FOL3[i] == WHOLE3[i], u'全篇折平面两构不等: ' + LBL[i]
EQK = [(u'syn', u'tcp_syn_retries'), (u'synack', u'tcp_synack_retries')]
EQ4 = []
EQB = []
for nm, k in EQK:
    tb = p3(u' '.join(BODY4[k]))
    bb = BLK4[k]
    N = int(num_at4(tb, u'default value is ', u'', False))
    pa = int(num_at4(tb, u'corresponds to ', u'second', True))
    pb = int(num_at4(tb, u'happen after ', u'second', True))
    rto = int(num_at4(tb, u'initial rto of ', u'second', True))
    assert [N, pa, pb, rto] == [int(num_after_b4(x, w)) for x, w in
                                ((bb, u'default value is'), (bb, u'corresponds to'),
                                 (bb, u'happen after'), (bb, u'initial rto of'))], k
    EQ4.append([nm, N, sum_last4(N, rto), sum_kill4(N, rto), geo_sum4(N, rto), pa, pb, rto])
    EQB.append([nm, N, dbl_b4(N, rto), dbl_b4(N + 1, rto), pa, pb, rto])
assert [x[2] == x[4] and x[3] == geo_sum4(x[1] + 1, x[7]) for x in EQ4] == [True, True]
put(u'eq_rows', EQ4)
put(u'eq_ok_syn', 1 if EQ4[0][2] == EQ4[0][5] and EQ4[0][3] == EQ4[0][6] else 0)
put(u'eq_ok_synack', 1 if EQ4[1][2] == EQ4[1][5] and EQ4[1][3] == EQ4[1][6] else 0)
put(u'eq_ruler_ledger', [x[2] - x[4] for x in EQ4])
put(u'eq_two_rulers_diff', sum([x[2] - x[4] for x in EQ4]))
put(u'eq_printed', [c3(FOL3[4], u'%dseconds' % x) for x in [31, 63, 127]])
put(u'eq_printed_all', sorted(set(sec_tokens4(FOL3[4]))))
put(u'eq_min_n_last', min([n for n in range(1, 20) if sum_last4(n) >= 100]))
put(u'eq_min_n_kill', min([n for n in range(1, 20) if sum_kill4(n) >= 100]))
DOC8 = num_at4(FOL3[4], u'a value of at least ', u'', False)
assert DOC8 is not None, u'内核那一份没印出“至少几”'
put(u'eq_doc_says', int(DOC8))
put(u'eq_off_by', [G[u'eq_doc_says'] - G[u'eq_min_n_last'], G[u'eq_doc_says'] - G[u'eq_min_n_kill']])
put(u'eq_n15_last', sum_last4(15))
put(u'eq_n15_kill', sum_kill4(15))
put(u'eq9246_by_src', [c3(FOL3[i], u'924.6') for i in range(NSRC)])
put(u'eq_9246_printed', G[u'eq9246_by_src'][4])
V9246, _E9246 = dec_secs4(FOL3[4])
assert V9246 is not None, u'924.6 那一句读不到小数秒'
put(u'eq_9246_face', float(V9246))
RTO4 = dict((k, G[u'lin_defaults'].get(k)) for k in [u'rto_min', u'rto_max', u'rto_initial'])
put(u'eq_rto_face', [int(RTO4[u'rto_min']) / 1000.0, int(RTO4[u'rto_max']) / 1000.0,
                     int(RTO4[u'rto_initial']) / 1000.0])
put(u'eq_rto_min_ms', int(RTO4[u'rto_min']))
put(u'eq_9246_cand', [sum_last4(15, G[u'eq_rto_face'][0]), sum_kill4(15, G[u'eq_rto_face'][0]),
                      sum_last4(15, G[u'eq_rto_face'][2]), sum_last4(15, G[u'eq_rto_face'][1]),
                      geo_sum4(15, G[u'eq_rto_face'][0])])
put(u'eq_9246_hit', len([x for x in G[u'eq_9246_cand'] if abs(x - G[u'eq_9246_face']) < 0.05]))
put(u'eq_9246_gap', [round(x - G[u'eq_9246_face'], 1) for x in G[u'eq_9246_cand']])
put(u'eq2_rows', EQB)
put(u'eq2_close', [[EQB[t][1] - EQ4[t][1], EQB[t][2] - EQ4[t][2], EQB[t][3] - EQ4[t][3],
                    EQB[t][4] - EQ4[t][5], EQB[t][5] - EQ4[t][6], EQB[t][6] - EQ4[t][7]]
                   for t in range(2)])
put(u'eq2_ruler_gap', [[EQB[t][2] - EQ4[t][2], EQB[t][2] - EQ4[t][4], EQB[t][3] - EQ4[t][3]]
                       for t in range(2)])
put(u'eq2_printed', [c3(WHOLE3[4], u'%dseconds' % x) for x in [31, 63, 127]])
put(u'eq2_printed_close', [G[u'eq2_printed'][t] - G[u'eq_printed'][t] for t in range(3)])
put(u'eq2_min_last', min([n for n in range(1, 20) if dbl_b4(n) >= 100]))
put(u'eq2_min_kill', min([n for n in range(1, 20) if dbl_b4(n + 1) >= 100]))
put(u'eq2_doc_says', int(num_run4(WHOLE3[4], u'a value of at least')[0]))
put(u'eq2_off_by', [G[u'eq2_doc_says'] - G[u'eq2_min_last'], G[u'eq2_doc_says'] - G[u'eq2_min_kill']])
put(u'eq2_n15_last', dbl_b4(15))
put(u'eq2_n15_kill', dbl_b4(16))
V9B, E9B = num_run4(WHOLE3[4], u'hypothetical timeout')
assert V9B == V9246, u'924.6 两把读数尺不等'
put(u'eq2_9246_face', float(V9B))
put(u'eq2_9246_unit', 1 if WHOLE3[4][E9B:E9B + 8].lstrip().startswith(u'seconds') else 0)
put(u'eq2_face_close', abs(G[u'eq2_9246_face'] - G[u'eq_9246_face']))
RB = dict((k, G[u'kn2_dv'].get(k)) for k in [u'rto_min', u'rto_max', u'rto_initial'])
put(u'eq2_rto_face', [int(RB[u'rto_min']) / 1000.0, int(RB[u'rto_max']) / 1000.0,
                      int(RB[u'rto_initial']) / 1000.0])
put(u'eq2_rto_close', [abs(G[u'eq2_rto_face'][t] - G[u'eq_rto_face'][t]) for t in range(3)])
put(u'eq2_cand', [dbl_b4(15, G[u'eq2_rto_face'][0]), dbl_b4(16, G[u'eq2_rto_face'][0]),
                  dbl_b4(15, G[u'eq2_rto_face'][2]), dbl_b4(15, G[u'eq2_rto_face'][1]),
                  G[u'eq2_rto_face'][0] * ((1 << 15) - 1)])
put(u'eq2_cand_close', [abs(x - y) for x, y in zip(G[u'eq2_cand'], G[u'eq_9246_cand'])])
put(u'eq2_hit', len([x for x in G[u'eq2_cand'] if abs(x - G[u'eq2_9246_face']) < 0.05]))
put(u'eq2_hit_close', G[u'eq2_hit'] - G[u'eq_9246_hit'])
put(u'eq2_dev', [round(abs(x - G[u'eq2_9246_face']), 1) for x in G[u'eq2_cand']])
put(u'eq2_dev_close', sum([abs(x - y) for x, y in zip(G[u'eq2_dev'], G[u'eq_9246_gap'])]))
put(u'eq2_9246_n', c3(WHOLE3[4], u'924.6'))
print(u'7 等式 %s/%s ⇎ 幂清单 %s ⇎ 最小N %d/%d ⇎ 文书印 %d ⇎ 差 %s ⇎ 候选 %s ⇎ 命中 %d/%d' % (
      G[u'eq_rows'][0][1:4], G[u'eq_rows'][1][1:4], G[u'eq2_rows'][0][2:4], G[u'eq_min_n_last'],
      G[u'eq_min_n_kill'], G[u'eq_doc_says'], G[u'eq_off_by'], G[u'eq_9246_cand'],
      G[u'eq_9246_hit'], G[u'eq2_hit']))
# ---------- 8. 语形族 ⇎ 数值项 ⇎ 粘连 ⇎ 时长 ----------
_RXNUM = re.compile(u'\\d+(?:[.,]\\d+)?')


def num_pairs4(text, units):
    """数值项第四档: 一条 `\\d+(?:[.,]\\d+)?` 取数字字段, 起始左邻是字母数字或点号则整枚作废,
       单位按长度降序就地读并数中间空格(建条侧手工扫数字串 ⇎ 采集侧一条选择支正则)。"""
    out = []
    for m in _RXNUM.finditer(text):
        i, j = m.start(), m.end()
        if i > 0 and (text[i - 1].isalnum() or text[i - 1] == u'.'):
            continue
        k, gap = j, 0
        while k < len(text) and text[k] == u' ':
            k += 1
            gap += 1
        for u_ in sorted(units, key=len, reverse=True):
            e = k + len(u_)
            if text.startswith(u_, k) and (e >= len(text) or not text[e].isalpha()):
                if gap <= 1:
                    out.append((text[i:j], u_, gap))
                break
    return out


def np24(lst):
    return sorted(set([(a, b) for a, b, _ in lst]))


NPR = {}
for _tier, _face, _units in ((u'raw', TT3, UNITS), (u'narrow', FOLDX3, UNIT), (u'wide', FOLDX3, UNITS),
                             (u'glue', TT3, GLUE)):
    for i in range(NSRC):
        mine = num_pairs4(_face[i], _units)
        assert mine == mk_np(_face[i], _units), u'数值两把尺不等: %s %s' % (_tier, LBL[i])
        NPR[(_tier, i)] = mine
F04 = [np24(NPR[(u'raw', i)]) for i in range(NSRC)]
FU4 = [np24(NPR[(u'narrow', i)]) for i in range(NSRC)]
FW4 = [np24(NPR[(u'wide', i)]) for i in range(NSRC)]
put(u'numunit', [list(map(list, FU4[i])) for i in range(NSRC)])
put(u'numunit_wide', [list(map(list, FW4[i])) for i in range(NSRC)])
put(u'numunit_raw', [list(map(list, F04[i])) for i in range(NSRC)])
put(u'numval_n', [len(FU4[i]) for i in range(NSRC)])
put(u'numval_wide_n', [len(FW4[i]) for i in range(NSRC)])
put(u'numval_extra', [sorted(set(FW4[i]) - set(FU4[i])) for i in range(NSRC)])
put(u'numunit_wrap', [sorted(set(FW4[i]) - set(F04[i])) for i in range(NSRC)])
put(u'glued_rows', [NPR[(u'glue', i)] for i in range(NSRC)])
put(u'glued_all', [[a + b for a, b, gp in NPR[(u'glue', i)] if gp == 0] for i in range(NSRC)])
put(u'glued_n', [len(G[u'glued_all'][i]) for i in range(NSRC)])
put(u'glued_vari', [len(set(G[u'glued_all'][i])) for i in range(NSRC)])
put(u'spaced_n', [len([1 for a, b, gp in NPR[(u'glue', i)] if gp == 1]) for i in range(NSRC)])
put(u'numtimes', [[list(z) for z in sorted(set(RXS[u'RXN'].findall(FOL3[i])))] for i in range(NSRC)])
put(u'dur', [[c3(FOL3[i], d) for d in DUR] for i in range(NSRC)])
put(u'dur_by_form', [sum([G[u'dur'][i][k] for i in range(NSRC)]) for k in range(len(DUR))])
put(u'dur_by_doc', [sum(G[u'dur'][i]) for i in range(NSRC)])
A_RAW = [sorted([tuple(z) for z in x]) for x in G[u'numunit_raw']]
B_RAW = [sorted([tuple(z) for z in x]) for x in MEA[u'numunit']]
put(u'numunit_ruler_diff', 1 if A_RAW == B_RAW else 0)
put(u'numunit_track_diff', [[sorted(set(x) - set(y)), sorted(set(y) - set(x))] for x, y in zip(A_RAW, B_RAW)])
TAB_MK = [mk_tabs(FOL3[i]) for i in range(NSRC)]
put(u'spell', [[c3(FOL3[i], p3(p)) for p in GRP] for i in range(NSRC)])
put(u'spell_word', [[ub4(FOL3[i], p3(p), 1) for p in GRP] for i in range(NSRC)])
for i in range(NSRC):
    for k in range(len(GRP)):
        assert G[u'spell_word'][i][k] == mk_ub_tab(FOL3[i], p3(GRP[k]), TAB_MK[i]), u'整词两把尺不等'
        assert G[u'spell'][i][k] == len(oc3(FOL3[i], p3(GRP[k]))), u'子串两把尺不等'
put(u'spell_diff', [G[u'spell'][i][k] - G[u'spell_word'][i][k]
                    for i in range(NSRC) for k in range(len(GRP))])
put(u'spell_tot', [sum(G[u'spell'][i]) for i in range(NSRC)])
put(u'spell_word_tot', [sum(G[u'spell_word'][i]) for i in range(NSRC)])
put(u'spell_vari', [len([1 for k in range(len(GRP)) if G[u'spell'][i][k] > 0]) for i in range(NSRC)])
put(u'spell_excl', [[p for k, p in enumerate(GRP)
                     if G[u'spell'][i][k] > 0 and all(G[u'spell'][j][k] == 0
                                                     for j in range(NSRC) if j != i)]
                    for i in range(NSRC)])
put(u'excl_n', sum([len(x) for x in G[u'spell_excl']]))
put(u'spell_cold', [p for k, p in enumerate(GRP) if all(G[u'spell'][i][k] == 0 for i in range(NSRC))])
put(u'tcp_will', [c3(FOL3[i], u'the tcp will') for i in range(NSRC)])
put(u'tcp_endpoint_will', [c3(FOL3[i], u'the tcp endpoint will') for i in range(NSRC)])
for i in range(NSRC):
    assert ub4(FOL3[i], u'the tcp will', 1) == len(oc3(FOL3[i], u'the tcp will'))
print(u'8 语形 %s 式种 %s 全冷 %s ⇎ 数值项 %s/%s ⇎ 粘连 %s 带空格 %s ⇎ 时长 %s' % (
      G[u'spell_tot'], G[u'spell_vari'], G[u'spell_cold'], G[u'numval_n'], G[u'numval_wide_n'],
      G[u'glued_n'], G[u'spaced_n'], G[u'dur_by_doc']))

# ---------- 9. 独占针 ⇎ 共现针 ⇎ 模板段(摘壳面两种构法) ----------
SHJP3 = [p3(NL.join([x for x in L3[i] if not shell3(x)])) for i in range(NSRC)]
for i in range(NSRC):
    assert SHJP3[i] == SHP3[i], u'摘壳面两种构法不同串: ' + LBL[i]


def mat4(pool, face, cnt):
    """针×份矩阵: 每枚针在五份摘壳面上各数一遍, 记下他份合计 ⇎ 本份枚数 ⇎ 命中他的份名; cnt 是本遍的哪把计数尺。"""
    out = []
    for own, p in pool:
        q = p3(p)
        row = [cnt(face[j], q) for j in range(NSRC)]
        me = IDX[own]
        out.append((own, p, row, sum([row[j] for j in range(NSRC) if j != me]), row[me],
                    [LBL[j] for j in range(NSRC) if j != me and row[j] > 0]))
    return out


def _cnt_a(s, q):
    return c3(s, q)


def _cnt_b(s, q):
    return len(oc3(s, q))


NEGEX4 = mat4(NEG, SHJP3, _cnt_a)
RPEX4 = mat4(RP, SHJP3, _cnt_a)
NG24 = mat4(NEG, SHP3, _cnt_b)
RP24 = mat4(RP, SHP3, _cnt_b)
for t in range(len(NEGEX4)):
    for j in range(NSRC):
        assert NEGEX4[t][2][j] == NG24[t][2][j], u'独占针两把尺不等: ' + NEG[t][1][:24]
for t in range(len(RPEX4)):
    for j in range(NSRC):
        assert RPEX4[t][2][j] == RP24[t][2][j], u'共现针两把尺不等: ' + RP[t][1][:24]
put(u'neg_n', len(NEG))
put(u'neg_probes', len(NEG) * NSRC)
put(u'neg_mat', [z[2] for z in NEGEX4])
put(u'neg_others', sum([z[3] for z in NEGEX4]))
put(u'neg_self', len([z for z in NEGEX4 if z[4] > 0]))
put(u'neg_self_tot', sum([z[4] for z in NEGEX4]))
put(u'neg_cold', [z[1] for z in NEGEX4 if z[4] == 0])
put(u'neg_multi', [z[1] for z in NEGEX4 if z[4] > 1])
put(u'neg_clean', len([z for z in NEGEX4 if z[3] == 0 and z[4] == 1]))
put(u'rp_n', len(RP))
put(u'rp_mat', [z[2] for z in RPEX4])
put(u'rp_others', sum([z[3] for z in RPEX4]))
put(u'rp_self_tot', sum([z[4] for z in RPEX4]))
put(u'rp_other_src', sorted(set([d for z in RPEX4 for d in z[5]])))
put(u'rp_reprint_9293', G[u'rp_mat'][0][IDX[u'9293']])
put(u'rp_all_carry', [z[3] > 0 for z in RPEX4])
put(u'ng2_mat', [z[2] for z in NG24])
put(u'ng2_close', sum([abs(NG24[t][2][j] - NEGEX4[t][2][j])
                       for t in range(len(NG24)) for j in range(NSRC)]))
put(u'ng2_others', sum([z[3] for z in NG24]))
put(u'ng2_self', sum([z[4] for z in NG24]))
put(u'ng2_multi', [z[1] for z in NG24 if z[4] > 1])
put(u'ng2_multi_cnt', [z[4] for z in NG24 if z[4] > 1])
put(u'ng2_multi_close', len(G[u'ng2_multi']) - len(G[u'neg_multi']))
put(u'rp2_mat', [z[2] for z in RP24])
put(u'rp2_close', sum([abs(RP24[t][2][j] - RPEX4[t][2][j])
                       for t in range(len(RP24)) for j in range(NSRC)]))
put(u'rp2_others', sum([z[3] for z in RP24]))
put(u'rp2_other_src', sorted(set([d for z in RP24 for d in z[5]])))
put(u'rp2_reprint', G[u'rp2_mat'][0][IDX[u'9293']])
KWSH4 = [SHP3[i].find(p3(KW)) for i in range(NSRC)]
KWF4 = [FOL3[i].find(p3(KW)) for i in range(NSRC)]
KWSHJ4 = [SHJP3[i].find(p3(KW)) for i in range(NSRC)]
KWFJ4 = [WHOLE3[i].find(p3(KW)) for i in range(NSRC)]
put(u'kw_head', KWF4)
put(u'kw_head_sh', KWSH4)
put(u'kw_present', [1 if x >= 0 else 0 for x in KWF4])
put(u'kw_docs', len([1 for x in KWSH4 if x >= 0]))
KWPAIR = [(a, b) for a in range(NSRC) for b in range(a + 1, NSRC) if KWSH4[a] >= 0 and KWSH4[b] >= 0]
put(u'kw_pair_n', len(KWPAIR))
put(u'kw_same', [1 if SHP3[a][KWSH4[a]:KWSH4[a] + 200] == SHP3[b][KWSH4[b]:KWSH4[b] + 200] else 0
                 for a, b in KWPAIR])
put(u'kw_same_raw', [1 if FOL3[a][KWF4[a]:KWF4[a] + 200] == FOL3[b][KWF4[b]:KWF4[b] + 200] else 0
                     for a, b in KWPAIR])
put(u'kw2_head', KWFJ4)
put(u'kw2_head_sh', KWSHJ4)
put(u'kw2_close', sum([abs(KWFJ4[i] - KWF4[i]) + abs(KWSHJ4[i] - KWSH4[i]) for i in range(NSRC)]))
put(u'kw2_docs', len([x for x in KWSHJ4 if x >= 0]))
KWP24 = [(a, b) for a in range(NSRC) for b in range(a + 1, NSRC) if KWSHJ4[a] >= 0 and KWSHJ4[b] >= 0]
put(u'kw2_pair_n', len(KWP24))
put(u'kw2_same', [1 if SHJP3[a][KWSHJ4[a]:KWSHJ4[a] + 200] == SHJP3[b][KWSHJ4[b]:KWSHJ4[b] + 200] else 0
                  for a, b in KWP24])
put(u'kw2_same_close', sum([abs(x - y) for x, y in zip(G[u'kw2_same'], G[u'kw_same'])]))
print(u'9 独占针 %d 枚他份命中 %d ⇎ 共现 %d 枚他份 %d ⇎ 模板段偏移 %s ⇎ 配对 %d 同段 %s' % (
      len(NEG), G[u'neg_others'], len(RP), G[u'rp_others'], G[u'kw_head'],
      G[u'kw_pair_n'], G[u'kw_same']))


# ---------- 10. 第五张面 ⇎ 切开针账 ⇎ 逐 token 去编号 ⇎ 跨行语气词 ----------
def face_ws4(rows, low):
    """折平第六档: 只交词表, 逐行 split 再拼单空格(采集侧逐词抄写带字符表, 发射侧按行拼)。"""
    ws = []
    for _r, x in rows:
        ws.extend((x.lower() if low else x).split())
    return u' '.join(ws)


PPFA = [face_ws4(ALLR3[i], 1) for i in range(NSRC)]
PPFB = [face_ws4(KEEP3[i], 1) for i in range(NSRC)]
PPFC = [face_ws4(KEEP3[i], 0) for i in range(NSRC)]
PPFD = [face_ws4(ALLR3[i], 0) for i in range(NSRC)]
PPROWS = [TT3[i].count(NL) + 1 for i in range(NSRC)]
PPKEPT = []
for i in range(NSRC):
    _c, _k = 0, 0
    while _k < len(L3[i]):
        if not shell3(L3[i][_k]):
            _c += 1
        _k += 1
    PPKEPT.append(_c)
put(u'pp_face_all', 1 if PPFA == [FOL3[i] for i in range(NSRC)] else 0)
put(u'pp_face_shell', 1 if PPFB == [SHP3[i] for i in range(NSRC)] else 0)
put(u'pp_face_shell_case', 1 if PPFC == [SHPX3[i] for i in range(NSRC)] else 0)
put(u'pp_face_all_case', 1 if PPFD == [FOLDX3[i] for i in range(NSRC)] else 0)
put(u'pp_face_len', [len(PPFB[i]) - len(SHP3[i]) for i in range(NSRC)])
put(u'pp_rows_kept', PPKEPT)
put(u'pp_rows_all', PPROWS)
put(u'pp_rows_close', [PPKEPT[i] + G[u'shell_lines'][i] - PPROWS[i] for i in range(NSRC)])
put(u'pp_chars_shell', [len(PPFB[i]) for i in range(NSRC)])
assert PPKEPT == [len(KEEP3[i]) for i in range(NSRC)]
assert PPROWS == [len(L3[i]) for i in range(NSRC)]


def spans5(face):
    """句窗第五档: 标点后带真空格的切点(发射侧那条正则切, 采集侧逐字符扫), 空白片段照样剔掉。"""
    return [(a, b) for a, b in cut_re4(face) if face[a:b].strip() != u'']


put(u'pp_sent_close', len([i for i in range(NSRC)
                           if spans5(SHP3[i]) != mk_sent_cuts(SHP3[i])]))
put(u'pp_sent_n', [len(spans5(SHP3[i])) for i in range(NSRC)])

SC4 = []
for k in range(len(NK4)):
    for i in range(NSRC):
        nn = len(NK4[k])
        hs = ovl3(SHP3[i], NK4[k])
        sp = [h for h in hs if len(seg_rows(SEGSH3[i], h, h + nn)) > 1]
        ins = [h for h in hs if h not in sp]
        rows_in = [seg_row(SEGSH3[i], h) for h in ins]
        mx = max([len(seg_rows(SEGSH3[i], h, h + nn)) for h in sp] or [0])
        SC4.append([k, i, len(hs), len(sp), len(ins) - len(set(rows_in)), mx])
put(u'sc_occ', [[z[2] for z in SC4 if z[1] == i] for i in range(NSRC)])
put(u'sc_span', [[z[3] for z in SC4 if z[1] == i] for i in range(NSRC)])
put(u'sc_dup', [[z[4] for z in SC4 if z[1] == i] for i in range(NSRC)])
put(u'sc_max_span', max([z[5] for z in SC4]))
put(u'sc_occ_close', sum([abs(SC4[t][2] - G[u'role_sh'][SC4[t][0]][SC4[t][1]])
                          for t in range(len(SC4))]))
put(u'sc_line_close', sum([abs(SC4[t][2] - SC4[t][3] - SC4[t][4] - G[u'role_line'][SC4[t][0]][SC4[t][1]])
                           for t in range(len(SC4))]))
put(u'sc_span_tot', sum([z[3] for z in SC4]))
put(u'sc_needle_n', len(set([z[0] for z in SC4 if z[3] > 0])))
put(u'sc_doc_span', [sum([z[3] for z in SC4 if z[1] == i]) for i in range(NSRC)])
put(u'sc_cut_close', 1 if sorted(set([z[0] for z in SC4 if z[3] > 0])) == sorted(G[u'wrap_cut']) else 0)
put(u'sc_gain_close', G[u'sc_span_tot'] - G[u'wrap_gain_tot'])
put(u'sc_doc_gain_close', [G[u'sc_doc_span'][i] - G[u'wrap_gain'][i] for i in range(NSRC)])


def _res4(tok, inner):
    """整枚被括号合住的编号连括号一起丢; 半开的只挖编号串留下圈点(量测侧那条正则吃 “ (x-n)” 整串)。"""
    if tok[:1] == u'(' and tok[-1:] == u')' and tok[1:-1] == inner:
        return u''
    return tok.replace(inner, u'')


def tag_eat4(toks):
    """去编号第五档: 先把每 token 的圈点核预抄一遍, 再游标两词式优先、单词式其次、不像原样抄。"""
    core = [t.strip(u'().,;:') for t in toks]
    out, k, n = [], 0, len(toks)
    while k < n:
        pair = (core[k] + u' ' + core[k + 1]).lower() if k + 1 < n else u''
        if pair and RXS[u'TWO_TAG'].match(pair):
            if toks[k][:1] == u'(' and toks[k + 1][-1:] == u')':
                k += 2
                continue
            out.append(_res4(toks[k], core[k]))
            out.append(_res4(toks[k + 1], core[k + 1]))
            k += 2
            continue
        if RXS[u'TAGSHAPE2'].match(core[k]):
            out.append(_res4(toks[k], core[k]))
            k += 1
            continue
        out.append(toks[k])
        k += 1
    return [t for t in out if t != u'']


TDF3, SEGTDF3 = [], []
for i in range(NSRC):
    _f, _s = face_build([(r, u' '.join(tag_eat4(x.lower().split()))) for r, x in KEEP3[i]], 0)
    TDF3.append(_f)
    SEGTDF3.append(_s)
put(u'td_face_same', [1 if TDF3[i] == SHTAG3[i] else 0 for i in range(NSRC)])
put(u'td_face_gap', [len(TDF3[i]) - len(SHTAG3[i]) for i in range(NSRC)])
put(u'td_chars', [len(SHP3[i]) - len(TDF3[i]) for i in range(NSRC)])

TC4 = []
for k in range(len(NK4)):
    for i in range(NSRC):
        nn = len(NK4[k])
        hs = ovl3(TDF3[i], NK4[k])
        sp = [h for h in hs if len(seg_rows(SEGTDF3[i], h, h + nn)) > 1]
        TC4.append([k, i, len(hs), len(sp)])
put(u'tc_occ', [[z[2] for z in TC4 if z[1] == i] for i in range(NSRC)])
put(u'tc_occ_close', sum([abs(TC4[t][2] - G[u'role_tag'][TC4[t][0]][TC4[t][1]])
                          for t in range(len(TC4))]))
put(u'tc_gain_needles', sorted(set([TC4[t][0] for t in range(len(TC4))
                                    if TC4[t][2] > G[u'role_sh'][TC4[t][0]][TC4[t][1]]])))
put(u'tc_gain_close', len(G[u'tc_gain_needles']) - len(G[u'tag_gain_needles']))
put(u'tc_span_after', sum([z[3] for z in TC4]))
put(u'tc_span_before', G[u'sc_span_tot'])


def straddle4(rows, words, low):
    """跨行语气词第四档: 游标只留上一行的末 token, 现拼现比(采集侧那把在折平面上查表读邻)."""
    out, prev = [], None
    for r, x in rows:
        t = x.split()
        if not t:
            continue
        head = t[0].strip(u'().,;:')
        if prev is not None:
            cand = (prev[1] + u' ' + head).lower() if low else prev[1] + u' ' + head
            for k in range(len(words)):
                if cand == words[k]:
                    out.append([prev[0], r, words[k]])
        prev = (r, t[-1].strip(u'().,;:'))
    return out


STUP4 = [straddle4(ALLR3[i], OB, 0) for i in range(NSRC)]
STLO4 = [straddle4(ALLR3[i], OBL, 1) for i in range(NSRC)]
put(u'st_up', [len(x) for x in STUP4])
put(u'st_low', [len(x) for x in STLO4])
put(u'st_up_close', sum(G[u'st_up']) - sum(G[u'ob_wrap']))
put(u'st_by_doc', [sum([G[u'ob_wrap'][i * 5 + k] for k in range(5)]) - G[u'st_up'][i]
                   for i in range(NSRC)])
put(u'st_tot', sum(G[u'st_up']) + sum(G[u'st_low']))
put(u'st_words', sorted(set([z[2].lower() for x in STUP4 + STLO4 for z in x])))
put(u'st_docs', len([i for i in range(NSRC) if STUP4[i] or STLO4[i]]))
put(u'st_in_shell', sum([len([z for z in STUP4[i] + STLO4[i]
                              if shell3(L3[i][z[0]]) or shell3(L3[i][z[1]])]) for i in range(NSRC)]))
print(u'10 第五张面 同 %s ⇎ 切开针 %d 枚跨行 %d ⇎ 逐 token 去编号同 %s 差 %s ⇎ 跨行大写 %d 小写 %d 种 %s' % (
      G[u'pp_face_all'], len(SC4), G[u'sc_span_tot'], G[u'td_face_same'], G[u'td_face_gap'],
      sum(G[u'st_up']), sum(G[u'st_low']), u'|'.join(G[u'st_words'])))
# ---------- 11. 答句第二档(正则句尺) ⇎ 段窗 ⇎ 端点回原行自验 ----------
def next_at5(spans, at):
    """落在哪一句(另一把): 数“尾巴已经过去的句段”, 第一格尾界晚于 at 的即是。"""
    k = len([1 for a, b in spans if b <= at])
    if k < len(spans) and spans[k][0] <= at:
        return spans[k]
    if k >= len(spans):
        return spans[-1]
    return spans[0]


SP5 = [spans5(SHP3[i]) for i in range(NSRC)]
HS5 = [oc3(SHP3[i], ANSQ[i]) for i in range(NSRC)]
for i in range(NSRC):
    assert len(HS5[i]) == 1, u'答句针在摘壳面上不是唯一命中: ' + LBL[i]
S0B = [x[0] for x in HS5]
for i in range(NSRC):
    assert S0B[i] == S0[i], u'两档答句针不同偏移'
SB5 = [next_at5(SP5[i], S0B[i]) for i in range(NSRC)]
TXT5 = [SHPX3[i][SB5[i][0]:SB5[i][1]] for i in range(NSRC)]
RK5 = [seg_rows(SEGSH3[i], SB5[i][0], SB5[i][1]) for i in range(NSRC)]
RW5 = [list(range(rk[0], rk[-1] + 1)) for rk in RK5]
put(u'ans2_off', S0B)
put(u'ans2_needle_line', [seg_row(SEGSH3[i], S0B[i]) for i in range(NSRC)])
put(u'ans2_sent_line', [seg_row(SEGSH3[i], SB5[i][0]) for i in range(NSRC)])
put(u'ans2_sent_end', [seg_row(SEGSH3[i], SB5[i][1] - 1) for i in range(NSRC)])
put(u'ans2_span', [G[u'ans2_sent_end'][i] - G[u'ans2_sent_line'][i] + 1 for i in range(NSRC)])
put(u'ans2_chars', [len(x) for x in TXT5])
put(u'ans2_words', [len(x.split()) for x in TXT5])
put(u'ans2_rows_whole', [len(rw) for rw in RW5])
put(u'ans2_rows_kept', [len(rk) for rk in RK5])
put(u'ans2_shell_rows', [len(rw) - len(rk) for rw, rk in zip(RW5, RK5)])
put(u'ans2_blank_span', [len([x for x in rw if L3[i][x].strip() == u'' and shell3(L3[i][x])])
                         for i, rw in enumerate(RW5)])
put(u'ans2_page_span', [len([x for x in rw if any(f(L3[i][x]) for f in S3PAGE)])
                        for i, rw in enumerate(RW5)])
put(u'ans_line_close', [G[u'ans2_sent_line'][i] - G[u'ans_sent_line'][i] for i in range(NSRC)])
put(u'ans_end_close', [G[u'ans2_sent_end'][i] - G[u'ans_sent_end'][i] for i in range(NSRC)])
put(u'ans_span_close', [G[u'ans2_span'][i] - G[u'ans_sent_span'][i] for i in range(NSRC)])
put(u'ans_words_close', [G[u'ans2_words'][i] - G[u'ans_words'][i] for i in range(NSRC)])
put(u'ans_sent_same', [1 if TXT5[i] == G[u'ans_sent'][i] else 0 for i in range(NSRC)])
put(u'ans_shell_close', [G[u'ans_shell_rows'][i] - G[u'ans2_shell_rows'][i] for i in range(NSRC)])
put(u'ans_page_close', [G[u'ans_page_rows'][i] - G[u'ans2_page_span'][i] for i in range(NSRC)])


def blk4(i, a, b):
    """行区间 → 保形折平的窗文本(本遍的段表行号尺, 采集侧那把现折行再拼)。"""
    return face_build([(r, x) for r, x in KEEP3[i] if a <= r <= b], 0)[0]


PB4 = []
for t, (i, s, e) in enumerate(PINS):
    qs, qe = p3(s), p3(e)
    ps = SHP3[i].find(qs)
    pe = SHP3[i].find(qe)
    assert ps >= 0 and pe >= 0 and pe >= ps, (LBL[i], s[:32])
    ra = seg_row(SEGSH3[i], ps)
    rb = seg_row(SEGSH3[i], pe + len(qe) - 1)
    PB4.append([i, ps, pe, ra, rb, blk4(i, ra, rb)])
put(u'pb_doc', [z[0] for z in PB4])
put(u'pb_rows', [z[4] - z[3] + 1 for z in PB4])
put(u'pb_words', [len(z[5].split()) for z in PB4])
put(u'pb_chars', [len(z[5]) for z in PB4])
put(u'pb_vocab', [len(set([p3(w) for w in z[5].split()])) for z in PB4])
put(u'pb_rows_tot', sum(G[u'pb_rows']))
put(u'pb_words_tot', sum(G[u'pb_words']))
put(u'pb_chars_tot', sum(G[u'pb_chars']))
put(u'pb_five_rows', sum([G[u'pb_rows'][t] for t in range(5)]))
put(u'pb_one_line', len([z for z in PB4 if z[4] == z[3]]))


def tone5(txt, w):
    """窗内语气词第二档: 逐 token 用 findall 拆字母段; 单词档看整段相等, 短语档看前段尾 ⇎ 后段头。"""
    runs = [re.findall(u'[A-Za-z]+', t) for t in txt.split(u' ')]
    if u' ' in w:
        a, b = w.split(u' ')
        return len([1 for x, y in zip(runs, runs[1:]) if x and y and x[-1] == a and y[0] == b])
    return sum([len([r for r in rr if r == w]) for rr in runs])


def tag_shape4(t):
    """编号判形: 两头逐字符退圈点(采集侧是 strip), 再交给那条形状正则。"""
    a, b = 0, len(t)
    while a < b and t[a] in u'().,;:':
        a += 1
    while b > a and t[b - 1] in u'().,;:':
        b -= 1
    return RXS[u'TAGSHAPE2'].match(t[a:b]) is not None


put(u'pb_tone_must', [tone5(z[5], u'MUST') for z in PB4])
put(u'pb_tone_mustnot', [tone5(z[5], u'MUST NOT') for z in PB4])
put(u'pb_tone_should', [tone5(z[5], u'SHOULD') for z in PB4])
put(u'pb_tone_may', [tone5(z[5], u'MAY') for z in PB4])
put(u'pb_tone_tag', [len([1 for t in z[5].split(u' ') if tag_shape4(t)]) for z in PB4])
put(u'pb_tone_close', sum([abs(G[k][t] - ub4(PB4[t][5], OB[j], 1))
                           for k, j in [(u'pb_tone_must', 0), (u'pb_tone_should', 2),
                                        (u'pb_tone_may', 4)] for t in range(len(PB4))]))
put(u'pb_phrase_close', sum([abs(G[u'pb_tone_mustnot'][t] - ub4(PB4[t][5], u'MUST NOT', 1))
                             for t in range(len(PB4))]))
put(u'pb_tag_block_close', [G[u'pb_tone_tag'][2] - G[u'tag_dash'][1],
                            G[u'pb_tone_tag'][3] - G[u'blk_tag_n']])
ANSW4 = [[t for t in range(len(PB4))
          if PB4[t][0] == i and PB4[t][3] <= G[u'ans2_needle_line'][i] <= PB4[t][4]]
         for i in range(NSRC)]
put(u'pb_ans_win', [z[0] if z else -1 for z in ANSW4])
put(u'pb_ans_n', [len(z) for z in ANSW4])
put(u'pb_ans_close', len([z for z in G[u'pb_ans_win'] if z < 0]))


def fmap4(x):
    """一行折平 ⇎ 逐字符原行下标: 由 token 区间表展开, 空格格的落点是下一枚 token 的头。"""
    sp = toks3(x)
    f, ix = [], []
    for k, (a, b) in enumerate(sp):
        if k:
            f.append(u' ')
            ix.append(sp[k][0])
        f.append(x[a:b])
        ix.extend(range(a, b))
    return u''.join(f).lower(), ix


FROW3 = [[(r, x) + fmap4(x) for r, x in enumerate(L3[i])] for i in range(NSRC)]
for i in range(NSRC):
    for r, x, f, ix in FROW3[i]:
        assert f == p3(x), u'逐行折平与本遍面尺不等: %s %d' % (LBL[i], r)


def anch4(i, phrase, whole=0):
    """端点回原文件自验: 逐行现折现找, 命中扩到字界(含 -_), 左右再验不贴字母数字, 折回该行的字面切片。"""
    q = p3(phrase)
    for r, x, f, ix in FROW3[i]:
        if not whole and shell3(x):
            continue
        p = f.find(q)
        if p < 0:
            continue
        a, b = p, p + len(q)
        while a > 0 and (f[a - 1].isalnum() or f[a - 1] in u'-_'):
            a -= 1
        while b < len(f) and (f[b].isalnum() or f[b] in u'-_'):
            b += 1
        if (a > 0 and f[a - 1].isalnum()) or (b < len(f) and f[b].isalnum()):
            continue
        an = x[ix[a]:ix[b - 1] + 1]
        if p3(an) != q and q not in p3(an):
            continue
        return an, r
    return None, -1


SEGRT4 = []
for t, (i, s, e) in enumerate(PINS):
    _a1, r1 = anch4(i, s)
    _a2, r2 = anch4(i, e)
    SEGRT4.append([i, s[:30], r1, 1 if _a1 is not None else 0])
    SEGRT4.append([i, e[:30], r2, 1 if _a2 is not None else 0])
put(u'sr_n', len(SEGRT4))
put(u'sr_whole', sum([z[3] for z in SEGRT4]))
put(u'sr_cut', G[u'sr_n'] - G[u'sr_whole'])
put(u'sr_rows_close', sum([abs(SEGRT4[t][2] - (PB4[t // 2][3] if t % 2 == 0 else PB4[t // 2][4]))
                           for t in range(len(SEGRT4)) if SEGRT4[t][3] == 1]))
put(u'sr_cut_rows', len([z for z in SEGRT4 if z[3] == 0]))
print(u'11 答句第二档 同 %s 差 %s ⇎ 段窗 %d 扇 %d 行 %d 词 ⇎ 端点 %d 枚整行读通 %d 切开 %d' % (
      sum(G[u'ans_sent_same']), G[u'ans_shell_close'], len(PB4), G[u'pb_rows_tot'],
      G[u'pb_words_tot'], G[u'sr_n'], G[u'sr_whole'], G[u'sr_cut']))
# ---------- 12. 段落对照第二档: 字面针重开两扇窗 ⇎ 节题现读 ⇎ 新句定位 ----------
OVW = TAB[u'OVW']
OSRC = OVW[1][0]
OVF4, OVR4, OVC4 = [], [], []
OVS4 = []
for i, pin, stopstr in OVW:
    ps = SHP3[i].find(p3(pin[1]))
    pe = SHP3[i].find(p3(pin[2]))
    assert ps >= 0 and pe >= ps, u'段窗针读不到: ' + LBL[i]
    ra = seg_row(SEGSH3[i], ps)
    rb = seg_row(SEGSH3[i], pe)
    stop = p3(stopstr)
    rows = [(r, x) for r, x in ALLR3[i] if ra <= r <= rb]
    cutr = -1
    for q in range(len(rows)):
        if stop in p3(rows[q][1]):
            cutr = rows[q][0]
            rows = rows[:q]
            break
    face = face_build(rows, 1)[0]
    OVF4.append(face)
    OVR4.append([len(rows), rows[0][0], rows[-1][0],
                 len([1 for _r, x in rows if shell3(x)]), cutr])
    OVC4.append(face_build(rows, 0)[0])
    OVS4.append([face[a:b].strip() for a, b in spans5(face)])
S1E, S2E = OVS4[0], OVS4[1]
S2T = [tag_paren5(z).strip() for z in S2E]
OVB4 = [[OVF4[t], OVR4[t][0], OVR4[t][1], OVR4[t][2], OVC4[t], OVR4[t][3], OVR4[t][4]]
        for t in range(2)]
put(u'ov2_rows', [z[0] for z in OVR4])
put(u'ov2_sents', [len(S1E), len(S2E)])
put(u'ov2_same_raw', len([z for z in S2E if z in set(S1E)]))
put(u'ov2_same_tag', len([z for z in S2T if z in set(S1E)]))
put(u'ov2_same_canon', len([z for z in S2T
                            if canon4(z) in set([canon4(y) for y in S1E])]))
put(u'ov2_new', len(S2E) - G[u'ov2_same_tag'])
put(u'ov2_rows_close', [G[u'ov2_rows'][t] - G[u'ovl_rows'][t] for t in range(2)])
put(u'ov2_shell', [z[3] for z in OVR4])
put(u'ov2_shell_close', [G[u'ov2_shell'][t] - G[u'ovl_shell'][t] for t in range(2)])
put(u'ov2_sents_close', [G[u'ov2_sents'][t] - (G[u'ovl_s1'] if t == 0 else G[u'ovl_s2'])
                         for t in range(2)])
put(u'ov2_same_close', [G[u'ov2_same_raw'] - G[u'ovl_same_raw'],
                        G[u'ov2_same_tag'] - G[u'ovl_same_tag'],
                        G[u'ov2_same_canon'] - G[u'ovl_same_canon']])
put(u'ov2_new_close', G[u'ov2_new'] - G[u'ovl_new'])
put(u'ov2_chars', [len(x) for x in OVF4])
put(u'ov2_sub', 1 if S2E and all([z in OVF4[0] for z in S2E]) else 0)

OVHDR4 = []
for i, _pin, _s in OVW:
    hd = []
    for r, x in ALLR3[i]:
        m = RXS[u'SECHDR'].match(x)
        if m is not None:
            hd.append((r, m.group(u'no'), u' '.join(m.group(u'ti').split())))
    OVHDR4.append(hd)
OVOVN4 = [([h for h in OVHDR4[t] if h[0] < OVR4[t][1]] or [(0, u'', u'')])[-1] for t in range(2)]
OVNX4 = [[h for h in OVHDR4[t] if h[0] > OVR4[t][1]] for t in range(2)]
put(u'ov_sec', [h[1] for h in OVOVN4])
put(u'ov_sec_title', [h[2] for h in OVOVN4])
put(u'ov_next_sec', [OVNX4[t][0][1] if OVNX4[t] else u'' for t in range(2)])
put(u'ov_next_row', [OVNX4[t][0][0] if OVNX4[t] else -1 for t in range(2)])
put(u'ov_title_same', 1 if G[u'ov_sec_title'][0] == G[u'ov_sec_title'][1] else 0)
put(u'ov_sec_shift', 1 if G[u'ov_sec'][0] != G[u'ov_sec'][1] else 0)
put(u'ov_hdr_rows', [len(h) for h in OVHDR4])
put(u'ov_stop_str', [w[2] for w in OVW])
put(u'ov_cut_n', len([z for z in OVR4 if z[4] >= 0]))

NEWK4 = [k for k in range(len(S2E)) if S2T[k] not in set(S1E)]
OSP4 = []
for z in [S2E[k] for k in NEWK4]:
    hs = ovl3(SHP3[OSRC], z[:44])
    q = hs[0] if hs else -1
    OSP4.append([seg_row(SEGSH3[OSRC], q) if q >= 0 else -1,
                 len(seg_rows(SEGSH3[OSRC], q, q + len(z))) if q >= 0 else 0,
                 len(hs),
                 len([1 for t in SHPX3[OSRC][q:q + len(z)].split(u' ') if tag_shape4(t)])
                 if q >= 0 else 0, len(z)])
put(u'os_n', len(OSP4))
put(u'os_first_row', [z[0] for z in OSP4])
put(u'os_rows', [z[1] for z in OSP4])
put(u'os_located', len([z for z in OSP4 if z[0] >= 0]))
put(u'os_ambig', len([z for z in OSP4 if z[2] > 1]))
put(u'os_tag_in_window', sum([z[3] for z in OSP4]))
put(u'os_len', [z[4] for z in OSP4])
print(u'12 段窗第二档 行 %s 句 %s ⇎ 节号 %s(“%s”) ⇎ 截断串 %s 触发 %d ⇎ 新句 %d 枚定位 %d 多解 %d 窗内编号 %d' % (
      G[u'ov2_rows'], G[u'ov2_sents'], G[u'ov_sec'], G[u'ov_sec_title'][0], G[u'ov_stop_str'],
      G[u'ov_cut_n'], G[u'os_n'], G[u'os_located'], G[u'os_ambig'], G[u'os_tag_in_window']))
# ---------- 13. 与采集遍逐键对账: 配对清单从建条遍源码的 PAIRS 字面量里摘 ----------
AGREE, DIFFK = [], []
for _mk, _pk in PAIRS:
    if _mk not in G or _pk not in MEA:
        DIFFK.append(_mk + u'?' + _pk)
        continue
    (AGREE if G[_mk] == MEA[_pk] else DIFFK).append(_mk)
for _mk, _pk in [(u'spell', u'spell'), (u'ob_line', u'ob_line'), (u'ob_fold', u'ob_fold')]:
    (AGREE if G[_mk] == MEA[_pk] else DIFFK).append(_mk)
THREE = [[[G[u'role_line'][k][i], G[u'role_fold'][k][i], G[u'role_sh'][k][i]] for i in range(NSRC)]
         for k in range(len(NK4))]
N3D = []
for k in range(min(len(THREE), len(MEA[u'needles3']))):
    for i in range(NSRC):
        for t in range(3):
            if THREE[k][i][t] != MEA[u'needles3'][k][i][t]:
                N3D.append([k, NEEDLES[k][:22], LBL[i], t, THREE[k][i][t], MEA[u'needles3'][k][i][t]])
put(u'n3_diff', N3D)
(AGREE if THREE == MEA[u'needles3'] else DIFFK).append(u'needles3')
for _mk, _pk in [(u'na_codepoints', u'nonascii'), (u'numunit_raw', u'numunit'),
                 (u'ovl_s1', u'ovl_s1'), (u'ovl_s2', u'ovl_s2'),
                 (u'ovl_same_tag', u'ovl_same'), (u'ovl_same_canon', u'ovl_same2')]:
    _a, _b = G[_mk], MEA[_pk]
    if _mk in (u'ovl_s1', u'ovl_s2', u'ovl_same_tag', u'ovl_same_canon'):
        _a, _b = [_a], [_b]
    if _mk == u'numunit_raw':
        _a = [sorted([tuple(z) for z in x]) for x in G[u'numunit_raw']]
        _b = [sorted([tuple(z) for z in x]) for x in MEA[u'numunit']]
    (AGREE if _a == _b else DIFFK).append(_mk)
for _mk in (u'kw_allcaps', u'kw_lowercase'):
    (AGREE if G[_mk] == MEA[_mk] else DIFFK).append(u'pk_' + _mk)
put(u'pick_agree', len(AGREE))
put(u'pick_diff', len(DIFFK))
put(u'pick_diffk', sorted(DIFFK))
assert not N3D, N3D[:4]
assert not DIFFK, DIFFK[:6]

# ---------- 14. 编码区锚账: 手写配对扫描 ⇎ 双轨归属(锚串一律从条目正文现采) ----------
MD = io.open(ENTRY, encoding=u'utf-8').read()
_i0 = MD.index(u'## ⟪BabelTele⟫')
_i1 = MD.index(u'## ⛓解读注')
ENC = MD[MD.index(NL, _i0) + 1:_i1].rstrip(NL)


def my_cites(s):
    """手写扫锚壳: 逐对 find 走 “⟦标签⟧⟨引文⟩”, “⟧”与“⟨”之间必须紧邻(发射侧是一条正则)。"""
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
RP2 = re.findall(u'⟦(' + u'|'.join(TAGS) + u')⟧⟨([^⟨⟩]+)⟩', ENC)
assert CITES == [(x, y) for x, y in RP2], (len(CITES), len(RP2))
USED = len([c for c in ENC if c == u'⟨'])
ANCHS = []
for _t, _a in CITES:
    if _a not in ANCHS:
        ANCHS.append(_a)
DIST = len(ANCHS)
TAGN = dict((t, len([x for x in CITES if x[0] == t])) for t in TAGS)
FAN3G = [p3(TT3[i]) for i in range(NSRC)]
ROWSRAW3 = [NL.join(p3(x) for x in L3[i]) for i in range(NSRC)]
ANSET4 = [set() for _ in range(NSRC)]
for _a in ANCHS:
    for i in range(NSRC):
        for _w in (0, 1):
            _an, _r = anch4(i, _a, _w)
            if _an is not None:
                ANSET4[i].add(_an)
ERR = [x for x in CITES if p3(x[1]) not in FAN3G[IDX[x[0]]]]
MISSLINE = [x for x in CITES
            if x[1] not in ANSET4[IDX[x[0]]] and p3(x[1]) not in ROWSRAW3[IDX[x[0]]]]
assert not ERR, ERR[:3]
assert not MISSLINE, MISSLINE[:3]
HITC = dict((a, tuple(i for i in range(NSRC) if p3(a) in FAN3G[i])) for a in ANCHS)
put(u'anchor_total', USED)
put(u'anchor_distinct', DIST)
put(u'anchor_err', len(ERR))
put(u'anchor_single', len([a for a in ANCHS if len(HITC[a]) == 1]))
put(u'anchor_cross', len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC]))
put(u'anchor_all5', len([a for a in ANCHS if len(HITC[a]) == NSRC]))
put(u'checks', DIST * NSRC)
put(u'enc_chars', len([c for c in ENC if c != NL]))
put(u'nsrc', len(TT3))
for t in TAGS:
    put(u'tag_' + t, TAGN[t])
assert G[u'anchor_single'] + G[u'anchor_cross'] + G[u'anchor_all5'] == DIST
assert G[u'anchor_total'] == sum(TAGN.values()) == len(CITES)
print(u'13 采集对账 %d 键符 ⇎ 14 锚 %d 处/去重 %d 串(独占 %d 跨界 %d 全份 %d)⇎ 复核 %d ⇎ 编码区 %d 字符 ⇎ 逐标签 %s' % (
      G[u'pick_agree'], G[u'anchor_total'], DIST, G[u'anchor_single'], G[u'anchor_cross'],
      G[u'anchor_all5'], G[u'checks'], G[u'enc_chars'], [TAGN[t] for t in TAGS]))
# ---------- 15. 布尔门 ⇎ 恒等式 ⇎ 键数账: 判词与名单一律从两遍源码的 AST 现摘 ----------
MSA, EMA = ast.parse(MS), ast.parse(ES)


def _gate_src(T, src, fnc):
    out = []
    for st in T.body:
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) \
                and isinstance(st.value.func, ast.Attribute) and st.value.func.attr == u'append' \
                and isinstance(st.value.func.value, ast.Name) and st.value.func.value.id == fnc \
                and len(st.value.args) == 1 and isinstance(st.value.args[0], ast.Tuple) \
                and len(st.value.args[0].elts) == 2 \
                and isinstance(st.value.args[0].elts[0], ast.Constant) \
                and isinstance(st.value.args[0].elts[0].value, type(u'')):
            out.append((st.value.args[0].elts[0].value,
                        u'(' + ast.get_source_segment(src, st.value.args[0].elts[1]) + u')'))
    return out


def _zsrc(T, src, fnc):
    out = []
    for st in T.body:
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) \
                and isinstance(st.value.func, ast.Name) and st.value.func.id == fnc \
                and len(st.value.args) == 2 \
                and all(isinstance(a, ast.Constant) and isinstance(a.value, type(u''))
                        for a in st.value.args):
            out.append((st.value.args[0].value, st.value.args[1].value))
    return out


def _tg(T, lineno_lo=None, lineno_hi=None):
    """F 的下标目标: 常量键名直取, 元组目标摊平, setdefault/update 的首枚字面量也算。"""
    out = []
    for nd in ast.walk(T):
        if isinstance(nd, ast.Assign) and nd.lineno is not None \
                and (lineno_lo is None or nd.lineno >= lineno_lo) \
                and (lineno_hi is None or nd.lineno < lineno_hi):
            for t in nd.targets:
                el = list(t.elts) if isinstance(t, (ast.Tuple, ast.List)) else [t]
                for e in el:
                    if isinstance(e, ast.Subscript) and isinstance(e.value, ast.Name) \
                            and e.value.id == u'F' and isinstance(e.slice, ast.Constant) \
                            and isinstance(e.slice.value, type(u'')):
                        out.append(e.slice.value)
        elif isinstance(nd, ast.Call) and isinstance(nd.func, ast.Attribute) \
                and nd.func.attr in (u'setdefault', u'update') \
                and isinstance(nd.func.value, ast.Name) and nd.func.value.id == u'F' \
                and nd.args and isinstance(nd.args[0], ast.Constant) \
                and isinstance(nd.args[0].value, type(u'')):
            out.append(nd.args[0].value)
    return out


def _minter(T, fnc):
    for st in T.body:
        if isinstance(st, ast.For) and isinstance(st.iter, ast.Call) \
                and isinstance(st.iter.func, ast.Name) and st.iter.func.id == u'enumerate' \
                and len(st.iter.args) == 1 and isinstance(st.iter.args[0], ast.Name) \
                and st.iter.args[0].id == fnc:
            return st.lineno
    raise AssertionError(fnc)


GATE_SRC = _gate_src(MSA, MS, u'G')
GATE2_SRC = _gate_src(EMA, ES, u'EG2')
Z_SRC = _zsrc(MSA, MS, u'Z')
ZX_SRC = _zsrc(EMA, ES, u'ZEXP')
assert len(GATE_SRC) == 55 and len(GATE2_SRC) == 23, (len(GATE_SRC), len(GATE2_SRC))
assert len(Z_SRC) == 38 and len(ZX_SRC) == 93, (len(Z_SRC), len(ZX_SRC))
LO1 = _minter(MSA, u'G')
LO2 = _minter(EMA, u'EG2')
LOA = [nd.lineno for nd in ast.walk(EMA)
       if isinstance(nd, ast.Assign) and isinstance(nd.targets[0], ast.Name)
       and nd.targets[0].id == u'ADDED'][0]
B2 = ES[:ES.index(u'# --- SCAN2 BEGIN ---')].count(NL) + 1
L2E = ES[:ES.index(u'# --- SCAN2 END ---')].count(NL) + 1
assert B2 < LO2 < LOA < L2E < EMA.body[-1].lineno


def _mint(pairs, pfx, pre, fb):
    """键名由门名退让而来: 只留 a-z0-9 取前 12 字符, 空串回落序号(建条遍带 g 头), 撞名加 x。"""
    out, seen = [], set()
    for gi, (nm, _) in enumerate(pairs):
        sl = re.sub(u'[^a-z0-9]', u'', nm)[:12]
        k = pfx + (sl if sl != u'' else fb % gi)
        while k in pre or k in seen:
            k += u'x'
        seen.add(k)
        out.append(k)
    return out


MK_STATIC = set(_tg(MSA))
GC = _mint(GATE_SRC, u'gc_', set(_tg(MSA, 0, LO1)), u'g%02d')
GC2 = _mint(GATE2_SRC, u'gc2_', MK_STATIC | set(GC) | set(_tg(EMA, B2, LO2)), u'%02d')
FLGC = sorted([k for k in FLAT if k.startswith(u'gc_')])
FLGC2 = sorted([k for k in FLAT if k.startswith(u'gc2_')])
assert sorted(GC) == FLGC, (GC[:4], FLGC[:4])
assert sorted(GC2) == FLGC2, (GC2[:4], FLGC2[:4])

BB86 = lambda name, i=None: (G[name] if i is None else G[name][i])
ENV = {u'F': G, u'B86V': BB86, u'NSRC': NSRC, u'pnorm': p3, u'SHP': SHP3, u'EFB': SHP3,
       u'T': TT3, u'ANSK': ANSK, u'occ_at': ovl3, u'EQ2': EQB, u'OVBLK': OVB4,
       u'OVOVN': OVOVN4, u'OVNEXT2': OVNX4, u'S1': S1, u'E1': E1, u'S2': S2, u'E2': E2,
       u'sum': sum, u'len': len, u'all': all, u'any': any, u'max': max, u'min': min,
       u'abs': abs, u'range': range, u're': re, u'sorted': sorted, u'tuple': tuple,
       u'set': set, u'str': str, u'int': int, u'float': float, u'list': list, u'dict': dict,
       u'round': round, u'zip': zip, u'map': map, u'bytes': bytes}
GFALL, G2FALL = [], []
GV = []
for _gi, (_nm, _e) in enumerate(GATE_SRC):
    try:
        _v = 1 if eval(_e, ENV, ENV) else 0
    except Exception as _x:
        GFALL.append([GC[_gi], _nm[:26], repr(_x)[:92]])
        continue
    GV.append([GC[_gi], _nm, _v])
put(u'gate_keys', GV)
put(u'bool_all_n', len(GATE_SRC))
put(u'bool_green', len([z for z in GV if z[2]]))
put(u'bool_red', [z[1] for z in GV if not z[2]])
G2V = []
for _gi, (_nm, _e) in enumerate(GATE2_SRC):
    try:
        _v = 1 if eval(_e, ENV, ENV) else 0
    except Exception as _x:
        G2FALL.append([GC2[_gi], _nm[:26], repr(_x)[:92]])
        continue
    G2V.append([GC2[_gi], _nm, _v])
put(u'gate2_keys', G2V)
put(u'bool2_all', len(GATE2_SRC))
put(u'bool2_green', len([z for z in G2V if z[2]]))
put(u'bool2_red', [z[1] for z in G2V if not z[2]])
put(u'bool2_red_count', len(G[u'bool2_red']))
put(u'bool_clos2_n', G[u'bool2_green'] - G[u'bool2_all'])
put(u'zid_scan_n', len(Z_SRC))
put(u'zid_scan2_n', len(ZX_SRC))
for _z in GV + G2V:
    put(_z[0], _z[2])
assert not GFALL, GFALL[:4]
assert not G2FALL, G2FALL[:4]
assert not G[u'bool_red'] and not G[u'bool2_red']

# ---------- 键数账: 两遍各自登记了几枚, 由 AST 目标行号数出来 ----------
S1FULL = MK_STATIC | set(GC)
ADDED = sorted((set(_tg(EMA, B2, LOA)) | set(GC2)) - S1FULL)
SELF5 = sorted(set(_tg(EMA, LOA, L2E)) - set(ADDED))
PAT = [nd.args[0].value for nd in ast.walk(EMA)
       if isinstance(nd, ast.Call) and isinstance(nd.func, ast.Attribute) and nd.func.attr == u'match'
       and len(nd.args) == 2 and isinstance(nd.args[0], ast.Constant)
       and isinstance(nd.args[0].value, type(u'')) and nd.args[0].value.startswith(u'^(pp_')][0]
EMITKEYS = sorted([k for k in (S1FULL | set(ADDED)) if re.match(PAT, k)])
put(u'scan_key_n', len(S1FULL) - 1)
put(u'scan2_src_n', len(S1FULL))
put(u'scan2_key_n', len(ADDED))
put(u'scan2_self_n', len(SELF5))
put(u'scan2_unprefixed', sorted(set(ADDED) - set(EMITKEYS)))
put(u'scan2_prefixed_old', sorted(set(EMITKEYS) - set(ADDED)))

# ---------- 恒等式: 建条遍 38 条走 F 形源码, 发射遍 93 条走 V 形查表, 复核清单再走一遍查表 ----------
ZF = [(w, repr(eval(e, ENV, ENV))[:60]) for e, w in Z_SRC if eval(e, ENV, ENV) != 0]
assert not ZF, ZF[:3]
ZXF = [w for e, w in ZX_SRC if eval(e, ENV, ENV) != 0]
assert not ZXF, ZXF[:3]
ZVF = [w for e, w in CH[u'zid'] if eval(e, ENV, ENV) != 0]
assert not ZVF, ZVF[:3]
assert len(CH[u'zid']) == G[u'zid_scan_n'] + G[u'zid_scan2_n'] == 131

# ---------- DERIV 复算点: 只走 B86V 查表通道 ----------
DFL, DCITE = [], 0
for _kk in sorted(DER, key=lambda x: (len(x), x)):
    _v = DER[_kk]
    DCITE += _v.count(u"B86V(")
    try:
        _got = eval(_v, ENV, ENV)
    except Exception as _e:
        DFL.append((_kk, repr(_e)[:80]))
        continue
    if _kk == u'0':
        # “0” 键是全部零项之和: 里面既有整数档也有浮点档的零(如 eq2_face_close), 所以按数值判零, 其余键按字面判
        if _got != 0:
            DFL.append((_kk, _v[:90], str(_got)))
        continue
    if str(_got) != _kk and repr(_got) != _kk:
        DFL.append((_kk, _v[:90], str(_got)))
assert not DFL, DFL[:4]

put(u'contract_n', len(G) + 1)
MISS = [k for k in G if k not in FLAT]
UNCOVER = [k for k in FLAT if k not in G]
assert not MISS, MISS[:6]
assert not UNCOVER, UNCOVER[:6]
assert G[u'contract_n'] == len(FLAT) == 577
print(u'15 布尔门 %d+%d 全绿 ⇎ 恒等式 %d+%d=%d 条归零 ⇎ 键数账 建条 %d/快照 %d+发射 %d(自计数 %d, 前缀多捞 %s)⇎ DERIV %d 键/%d 处引用 ⇎ 扁平 %d 键全覆盖' % (
      G[u'bool_green'], G[u'bool2_green'], G[u'zid_scan_n'], G[u'zid_scan2_n'], len(CH[u'zid']),
      G[u'scan_key_n'], G[u'scan2_src_n'], G[u'scan2_key_n'], G[u'scan2_self_n'],
      G[u'scan2_prefixed_old'], len(DER), DCITE, len(FLAT)))
# ---------- 16. ⛓解读注: 数字一律取本遍读数, 锚一律由本遍的面导 ----------
J = lambda xs: u' ⇎ '.join(u'%s' % x for x in xs)


def QT(tag, s):
    assert p3(s) in FAN3G[IDX[tag]], u'本遍锚平面读不到: ' + s[:50]
    return u'⟦%s⟧⟨%s⟩' % (tag, s)


def QRAW(tag, s):
    assert s in RAWF4[IDX[tag]], u'原行里读不到: ' + s[:50]
    return u'⟦%s⟧⟨%s⟩' % (tag, s)


def cell(c):
    assert u'|' not in c, c[:70]
    assert c.count(u'`') % 2 == 0, c[:70]
    return c


RAWF4 = [NL.join(L3[i]) for i in range(NSRC)]
PC4 = {}
CR4 = {}


def pieces4(k, i):
    """切开针的两半: 命中区间与摘壳段表逐段相交, 每行那一截经逐字符表映回原行字面。"""
    if (k, i) in PC4:
        return PC4[(k, i)]
    hs = [h for h in ovl3(SHP3[i], NK4[k]) if len(seg_rows(SEGSH3[i], h, h + len(NK4[k]))) > 1]
    if not hs:
        PC4[(k, i)] = None
        return None
    CR4[(k, i)] = len(hs)
    a, b = hs[0], hs[0] + len(NK4[k])
    rs = seg_rows(SEGSH3[i], a, b)
    out, rr = [], []
    for s, e, r in SEGSH3[i]:
        if e <= a or s >= b:
            continue
        ix = FROW3[i][r][3]
        lo, hi = max(a, s) - s, min(b, e) - s
        out.append(L3[i][r][ix[lo]:ix[hi - 1] + 1])
        rr.append(r)
    assert p3(u' '.join(out)) == NK4[k], u'两半拼不回针: ' + NEEDLES[k][:40]
    assert len(rr) == len(rs) and all(L3[i][rr[j]].find(out[j]) >= 0 for j in range(len(out))), NEEDLES[k][:40]
    PC4[(k, i)] = (out, rr)
    return PC4[(k, i)]


STR4 = [(k, i) for k in range(len(NK4)) for i in range(NSRC) if pieces4(k, i)]
assert set(STR4) == set([(z[0], z[1]) for z in SC4 if z[3] > 0])
assert sum([CR4[z] for z in STR4]) == G[u'sc_span_tot']
assert len(set([k for k, _i in STR4])) == G[u'sc_needle_n'] == G[u'wrap_cut_n']
MXD = sum([abs(G[u'maxlen'][i] - G[u'maxlen_scan'][i]) for i in range(NSRC)])
LI4 = sum([1 for a in ANCHS for c in a if u'a' <= c <= u'z' or u'A' <= c <= u'Z'])
LO4, _dep = 0, 0
for c in ENC:
    if c == u'⟨':
        _dep += 1
    elif c == u'⟩':
        _dep -= 1
    elif _dep == 0 and (u'a' <= c <= u'z' or u'A' <= c <= u'Z'):
        LO4 += 1
assert _dep == 0 and LI4 == CH[u'letters_in'] and LO4 == CH[u'letters_out']
assert sum([G[u'shape_sum'][i] - G[u'shape_ovl'][i] - G[u'shell_lines'][i]
            for i in range(NSRC)]) == 0

K7 = [k for k in range(len(NEEDLES)) if NEEDLES[k].startswith(u'An application MUST be able')][0]
A7, B7 = p3(u'An application MUST'), p3(u'be able to set the value for R2')
_S9 = SHP3[IDX[u'9293']]
_P1, _P2 = _S9.find(A7), _S9.find(B7)
assert _P1 >= 0 and _P2 > _P1 + len(A7), (_P1, _P2)
EATEN = _S9[_P1 + len(A7):_P2]
assert EATEN.strip().startswith(u'(') and EATEN.strip().endswith(u')') and u'must-' in EATEN, EATEN
REGION = _S9[_P1:_P2 + len(B7)]
assert REGION.count(EATEN) == 1
assert p3(u' '.join(REGION.split(EATEN, 1))) == NK4[K7], REGION[:80]
TAG_EAT = len(REGION) - len(NK4[K7])
assert TAG_EAT == len(EATEN) - 1, (TAG_EAT, EATEN)
RAW7 = [x for _r, x in ALLR3[IDX[u'9293']] if x.find(u'An application MUST') >= 0][0]

L2 = []
A = L2.append
A(u"第五遍(`corpus/_fill86.py`)把采集 ⇎ 建条目 ⇎ 发射三遍的量换算法不换定义地重跑一遍, 本遍是第四套实现, "
  u"独立处十三项: ①行界四通道并跑——`re.compile('\\n').split` ⇎ 本遍逐字符认九枚行界符(`\\n \\r \\x0b \\x0c \\x1c-\\x1e \\x85 \\u2028 \\u2029`, "
  u"`\\r\\n` 只记一枚)自建的 splitlines 档 ⇎ `(?<=\\n)` 切再丢空段的 readlines 档 ⇎ 逐字符数 `\\n` 的换行枚; 字节逐字节迭代 ⇎ `os.stat` 元数据 ⇎ "
  u"建条侧 `os.path.getsize`; 码位走 `len()` ⇎ 建条侧逐字符累加; UTF-8 差额直接作“字节−码位”(建条侧逐字符 `encode` 求和)。 "
  u"②折平走 `finditer('\\S+')` 取词跨度再 `join`(建条侧 `re.split('\\s')` 过滤空段)。 ③字面针三轨: `str.count`(非重叠) ⇎ `finditer(re.escape)` 取位置 ⇎ "
  u"`finditer('(?=针)')`(重叠), 采集侧是游标 find 环。 ④整词尺先把全串翻成“字母/数字/字母数字”三张布尔表(只认 52+10 枚字符, 不认 Unicode 字母), "
  u"命中由前瞻定位再查表读左右邻。 ⑤壳谓词第四档: `strip()` 后按字面相等 ⇎ 前缀 ⇎ 后缀切片 ⇎ 末两 token 判, 一枚序列正则也不跑。 "
  u"⑥行号尺第四档: 折平面由“每行一段”的段表(起, 止, 原行号)现导, 偏移→行号线性取满足 `起≤偏移` 的最后一段, 区间→行集合走相交测试。 "
  u"⑦句界第四档: `(?=[.!?](?: |$))` 的纯前瞻出候选, 空格尾巴由 `[^ ]` 的 search 现跳。 ⑧切开针第四档: 不判“这一行含不含针”, 而是把命中区间与段表求交, "
  u"相交行数 >1 才算跨行, 同行重枚按首行下标去重。 ⑨数值第四档: 一条 `\\d+(?:[.,]\\d+)?` 取数字段 + “左邻是字母数字或点号则整枚作废”的前置筛, 单位就地读。 "
  u"⑩内核默认值四句式全走 `str.partition` 链(建条侧游标 find, 发射侧四条正则级联)。 ⑪倍增第四轨: `itertools.accumulate` 逐次翻倍列清单再取末项。 "
  u"⑫去编号走 token 判别——逐 token 判形状丢弃再拼回(建条侧是一条抹除正则)。 ⑬锚账与键数账不抄上游名单: 锚由条目正文的手写配对扫描现推, "
  u"布尔门 ⇎ 恒等式 ⇎ DERIV 的右式一律从两遍源码 `ast` 摘出后在本遍读数上 eval, 键名清单由 AST 目标节点重建(元组与列表目标一并摊平)。 "
  u"五份在这一套算法下各 %s 行(`split(\"\\n\")` 尺)⇎ 字节合计 %s ⇎ 码位合计 %s。" % (
      J(G[u'splitnl']), format(sum(G[u'bytes']), u','), format(sum(G[u'cp']), u',')))
A(u"本遍复算 %d 键: 扁平表 %d 键全覆盖 ⇎ 本遍独有 %d ⇎ 未复算 %d ⇎ 逐值不符 %d ⇎ 需要申报的建条未量键 %d(申报清单 %s 空, 本遍没有任何一格靠改口径来对齐)。 "
  u"布尔门 %d+%d 道(建条目侧 ⇎ 发射侧, 右式从两遍源码逐道摘出在本遍读数上 eval)全绿, "
  u"红 %d+%d 道, 闭合差额 %d; 恒等式 %d+%d=%d 条全平, 其中 `checks` 回读的 V 形 %d 条也在本遍读数上重新归零; DERIV %d 键 ⇎ %d 处 `B86V` 引用逐键复算(键名即所推的字面, "
  u"零项之和走数值判零)。 键数账: 建条遍快照前 %d 枚 ⇎ 发射遍接手时 %d 枚 ⇎ 本遍重导的“发射新增”%d 枚 ⇎ 其后再写的自计数键 %d 枚 ⇎ 前缀尺多捞 %s。 "
  u"与采集遍逐键横比 %d/%d 键符 ⇎ %d 不符 ⇎ 判词针 %d 枚×五份 = %d 格四档读数, 与建条侧逐格差 %d。 编码区 %d 非换行字符里 %d 枚 `⟦…⟧⟨…⟩` 锚全部由本遍手写配对扫描取出, "
  u"并与正则档逐枚同序 ⇎ 去重 %d 串 ⇎ 面内读不到 %d 枚 ⇎ 原行读不到 %d 枚 ⇎ 归属分档 独占 %d ⇎ 跨界 %d ⇎ 全份 %d ⇎ 复核 %d 格 ⇎ "
  u"锚内外拉丁字母 %d ⇎ %d 枚由逐字符分类与尖括号游标现数(发射侧用一条正则)。" % (
      len(G), len(FLAT), len(MISS), len(UNCOVER), len(BAD), len(OVR), OVRV,
      G[u'bool_all_n'], G[u'bool2_all'],
      len(G[u'bool_red']), len(G[u'bool2_red']), G[u'bool_clos2_n'],
      G[u'zid_scan_n'], G[u'zid_scan2_n'], len(CH[u'zid']), len(CH[u'zid']), len(DER), DCITE,
      G[u'scan_key_n'], G[u'scan2_src_n'], G[u'scan2_key_n'], G[u'scan2_self_n'], G[u'scan2_prefixed_old'],
      G[u'pick_agree'], G[u'pick_agree'], G[u'pick_diff'], G[u'needle_n'], G[u'role_probes'], len(G[u'n3_diff']),
      G[u'enc_chars'], G[u'anchor_total'], DIST, G[u'anchor_err'], len(MISSLINE), G[u'anchor_single'],
      G[u'anchor_cross'], G[u'anchor_all5'], G[u'checks'], LI4, LO4))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"版式⇎四把行尺⇎换页账",
     u"行界四通道并跑: `re.compile('\\n').split` ⇎ 本遍逐字符认九枚行界符自建的 splitlines 档 ⇎ `(?<=\\n)` 切再丢空段的 readlines 档 ⇎ 逐字符数 `\\n`; "
     u"字节逐字节迭代 ⇎ `os.stat` ⇎ 建条侧 `os.path.getsize`; 码位走 `len()`; UTF-8 差额直接作“字节−码位”(建条侧逐字符 `encode` 求和)",
     u"最长行 %s ⇎ 正则跨尺 %s ⇎ 字节 %s ⇎ stat %s ⇎ 码位 %s ⇎ 切行 %s ⇎ splitlines %s ⇎ readlines %s ⇎ 换行枚 %s ⇎ 非空行 %s ⇎ 制表符 %s" % (
         J(G[u'maxlen']), J(G[u'maxlen_scan']), J(G[u'bytes']), J(G[u'bytes_stat']), J(G[u'cp']),
         J(G[u'splitnl']), J(G[u'splitlines']), J(G[u'readlines']), J(G[u'n_lf']),
         J(G[u'nonblank']), J(G[u'tab'])),
     u"两把最长行尺的分歧合计 %d 列 ⇎ 字节两把尺同值(不同 %d 份) ⇎ 差额账 %s 全平(只 9293 两数不等, 多出的 %d 字节就是 BOM 与非 ASCII 的 UTF-8 尾巴) ⇎ "
     u"splitlines−切行 = %s = 换页后随换行 %s − 收尾换行 %s(两遍谓词逐格差 %s) ⇎ readlines+尾换行−切行 %s ⇎ 非空+空行−切行 %s ⇎ "
     u"splitlines−换行枚−换页枚 %s; 换页 %s 枚里独占整行 %s ⇎ 紧接换行 %s ⇎ 行首带页 %s(对换页总数的账 %s)⇎ 落在文件尾 %s; 回车 %s 枚——五份全 LF 面。" % (
         MXD, G[u'bytes_vs_stat'], J(G[u'byte_cp_ledger']), G[u'utf8_extra'][2],
         J(G[u'rows_ledger']), J(G[u'ff_before_nl']), J(G[u'trailing_nl']), J(G[u'rows_ledger_diff']),
         J(G[u'lf_vs_readlines']), J(G[u'line_split_ledger']), J(G[u'splitlines_ledger']),
         J(G[u'ff']), J(G[u'ff_alone']), J(G[u'ff_before_nl']), J(G[u'ff_led']),
         J([G[u'ff_led'][i] - G[u'ff'][i] for i in range(NSRC)]), J(G[u'ff_at_eof']), J(G[u'n_cr']))),
    (u"页壳七路⇎第四档壳尺⇎剥壳正文",
     u"壳谓词第四档: `strip()` 后按字面相等 ⇎ 前缀 ⇎ 后缀切片 ⇎ 末两 token 判(采集侧跑整行序列正则 ⇎ 建条侧比逐 token 形状), 七路并起来判; "
     u"页码另起一把 naive 尺, 逐字符判“数字或空白”并按升沿数段; 四张面之间只比大小写与码位长度, 不比空白",
     u"壳行(本遍 ⇎ 采集 ⇎ 建条)%s ⇎ %s ⇎ %s ⇎ 七路命中总数 %s ⇎ 重复命中 %s ⇎ 剥壳正文 %s ⇎ 空行 %s ⇎ 页脚 %s ⇎ 793 式眉 %s ⇎ 1122 式眉 %s ⇎ "
     u"新式眉 %s ⇎ IETF 独立行 %s ⇎ naive 页码 %s(全裸 %s ⇎ 合壳形 %s) ⇎ 键行 %s ⇎ 印 Default 的行 %s" % (
         J(G[u'shell_lines']), J(G[u'shell_pick']), J(G[u'shell_shape']), J(G[u'shape_hits']),
         J(G[u'shape_ovl']), J(G[u'body_lines']), J(G[u'blank']), J(G[u'foot']), J(G[u'hdr793']),
         J(G[u'hdr1122']), J(G[u'hdrnew']), J(G[u'ietf_alone']), J(G[u'pgnum']), J(G[u'pgnum_naked']),
         J(G[u'pgnum_in_shell']), J(G[u'keylin']), J(G[u'default_lines'])),
     u"三把尺逐行同集: 分歧 %s 行 ⇎ 命中总数−重复 = 壳行(账 %s) ⇎ 壳+正文 = 切行(账 %s) ⇎ 摘壳保形折小写即摘壳折平面(判定 %d) ⇎ 全篇折小写比折平 %s ⇎ "
     u"摘壳折小写比摘壳折平 %s; 非 ASCII %s 枚 ⇎ 所在行 %s ⇎ 其中壳行 %s ⇎ 码位清单 %s ⇎ UTF-8 多 %s 字节 ⇎ BOM %s 枚在折平时被当空白吃掉(折平后剩 %s); "
     u"naive 页码尺报 %d 枚(逐份 %s), 其中合壳形 %d 枚 ⇎ 裸数字 %d 枚——那一族全在 9293 的表列里, 一枚也不合壳形。" % (
         J(G[u'shell_pred_diff']), J(G[u'shell_ledger']), J(G[u'pp_rows_close']), G[u'shpx_eq_pnorm'],
         J(G[u'foldx_ledger']), J(G[u'shpx_ledger']), J(G[u'na_total']), J(G[u'na_lines']),
         J(G[u'na_shell_lines']), J(G[u'na_codepoints']), J(G[u'utf8_extra']), J(G[u'bom']),
         J(G[u'bom_after_fold']), sum(G[u'pgnum']), J(G[u'pgnum']), sum(G[u'pgnum_in_shell']),
         sum(G[u'pgnum_naked']))),
    (u"答句五份⇎句界第四档⇎行号两轨",
     u"句界由 `[.!?]` 前瞻后接空白或行尾的候选现取, 空格尾巴交 `[^ ]` 的 search 现跳(建条侧逐字符扫 ⇎ 发射侧 `[.!?]+` finditer); "
     u"首末行经本遍段表映回原行, 再与建条侧的累积长度表+bisect ⇎ 发射侧的逐字符行表三轨对拍; 答句不再抄建条侧登记的句子表",
     u"词 %s ⇎ 字符 %s ⇎ 整句跨 %s 行 ⇎ 摘壳后 %s 行 ⇎ 首行 %s ⇎ 末行 %s ⇎ 面内偏移 %s ⇎ 锚针整串在一行读得通 %s 份 ⇎ 答句里的编号 %s 枚 ⇎ "
     u"大写义务词 %s ⇎ 非 ASCII %s 枚" % (
         J(G[u'ans_words']), J(G[u'ans_chars']), J(G[u'ans_sent_span']), J(G[u'ans2_rows_kept']),
         J(G[u'ans_sent_line']), J(G[u'ans_sent_end']), J(G[u'ans2_off']), J(G[u'ans_needle_line']),
         J(G[u'ans_tag_n']), J(G[u'ans_ob']), J(G[u'na_in_ans'])),
     u"本遍的两套答句通道逐格差(段表档对句子档): 首行 %s ⇎ 末行 %s ⇎ 跨度 %s ⇎ 词 %s ⇎ 页壳行 %s, 句串逐字符相同 %d/5; "
     u"跨度窗内的空壳行 %s ⇎ 页码形行 %s ⇎ 与建条侧页码账的差 %s——面内偏移那一档是本遍自导, 前三遍只登记行号。" % (
         J(G[u'ans_line_close']), J(G[u'ans_end_close']), J(G[u'ans_span_close']), J(G[u'ans_words_close']),
         J(G[u'ans_shell_close']), sum(G[u'ans_sent_same']),
         J(G[u'ans2_blank_span']), J(G[u'ans2_page_span']), J(G[u'ans_page_close']))),
    (u"判词针四档⇎三轨字面尺⇎跨行第四档",
     u"每枚针在四张面串上各数一遍: 子串轨走 `str.count`, 另起 `finditer(re.escape)` 取位置与 `finditer('(?=针)')` 重叠两轨校非重叠; "
     u"跨行不判“这一行含不含针”, 而是把命中区间与摘壳段表求交, 相交行数 >1 才算, 同行重枚按首行下标去重",
     u"逐行 %s ⇎ 全篇折平 %s ⇎ 摘壳折平 %s ⇎ 摘壳去编号 %s 枚 ⇎ 逐档增益(换行 ⇎ 页壳 ⇎ 编号)%s ⇎ 探针 %d 格 ⇎ 被换行切开 %d 枚 ⇎ "
     u"被页壳切开 %d 枚 ⇎ 被编号切开 %d 枚(针号 %s) ⇎ 摘壳面总命中 %d ⇎ 跨行命中 %d ⇎ 同行重枚 %d ⇎ 最长跨 %d 行" % (
         J(G[u'role_line_n']), J(G[u'role_fold_n']), J(G[u'role_sh_n']), J(G[u'role_tag_n']),
         J(G[u'role_gain']), G[u'role_probes'], G[u'wrap_cut_n'], len(G[u'shell_cut']),
         len(G[u'tag_cut']), J(G[u'tag_cut']),
         sum([sum(z) for z in G[u'sc_occ']]), G[u'sc_span_tot'],
         sum([sum(z) for z in G[u'sc_dup']]), G[u'sc_max_span']),
     u"总命中−同行重枚对行内尺读数(差 %d) ⇎ 跨行合计对换行增益(差 %d ⇎ 逐份 %s) ⇎ 切开针种名两遍同判 %d ⇎ 逐枚命中对建条侧读数(差 %d); "
     u"与采集遍的三档表逐格比 %d 枚×五份×三档, 不符 %d 格; 去编号档逐份净改读数 %s(正号=多读), 挪动清单 %s。" % (
         G[u'sc_line_close'], G[u'sc_gain_close'], J(G[u'sc_doc_gain_close']), G[u'sc_cut_close'],
         G[u'sc_occ_close'], G[u'needle_n'] * NSRC * 3, len(G[u'n3_diff']),
         J(G[u'tag_gain']), J(G[u'tag_move']))),
    (u"义务词编号族(只在 9293)⇎token 形状档",
     u"编号族按 token 现判形状: 词头+连字符+数字 ⇎ 左贴 '(' ⇎ 右贴 ')' ⇎ 裸形, 四档各自数; 粘连尺先把空白逐枚摘净再数, 切开尺不要求数字跟得上来; "
     u"抹除档逐 token 判形状丢弃再拼回(建条侧是一条抹除正则)",
     u"连字符式 %s ⇎ 括号内 %s ⇎ 裸形 %s ⇎ token 尺 %s ⇎ 粘连无空白 %s ⇎ 最大号 %s ⇎ 抹掉编号吃掉的字符 %s ⇎ 按词种(MUST ⇎ MUST NOT ⇎ SHOULD ⇎ "
     u"SHOULD NOT ⇎ MAY)%s ⇎ 被换行切开的编号 %s ⇎ 数字推到下一行 %s ⇎ 括号整对拉开 %s ⇎ 方括号 %s ⇎ 声明句“individually labeled”%s" % (
         J(G[u'tag_dash']), J(G[u'tag_in_paren']), J(G[u'tag_bare']), J(G[u'tag_token']),
         J(G[u'tag_nospace']), J(G[u'tag_max_no']), J(G[u'tag_chars']), J(G[u'tag_kind']),
         J(G[u'tag_split_manual']), J(G[u'tag_num_nextline']), J(G[u'tag_paren_apart']),
         J(G[u'tag_bracket']), J(G[u'labeled_decl'])),
     u"四条账逐枚归零: 连字−(括号内+裸形+整对拉开)= %s ⇎ 连字−token−方括号 = %s ⇎ 粘连−连字−推下一行 = %s ⇎ 词种之和−连字 = %s; "
     u"折平前后连字式差 %s(一枚也不靠换行才读得到); 整对拉开那枚的上下文 %s; 本遍逐 token 面与建条面串 %s 份逐字符同, 9293 两把尺吃字之差 %s "
     u"(本遍抹 %s ⇎ 建条抹 %s), 去编号前后跨行枚数 %d/%d。" % (
         J(G[u'tag_split_ledger']), J(G[u'tag_bracket_ledger']), J(G[u'tag_nextline_ledger']),
         J(G[u'tag_kind_ledger']), J(G[u'tag_fold_gain']), J(G[u'tag_apart_ctx']),
         J(G[u'td_face_same']), J(G[u'td_face_gap']), G[u'td_chars'][2], G[u'tag_chars'][2],
         G[u'tc_span_before'], G[u'tc_span_after'])),
    (u"大写义务词五式⇎整词布尔表",
     u"五式各走整词尺: 先把全串翻成字母/数字/字母数字三张布尔表, 命中由前瞻定位再查表读左右邻(建条侧一条断言正则 ⇎ 采集侧 `isalpha` 表); "
     u"跨行短语不靠两档相减, 而是逐对相邻非空行现拼首尾 token 再判",
     u"大写五式 %s ⇎ 合计 %s ⇎ 小写散文式 %s ⇎ 合计 %s ⇎ 并集尺(整词)对大写尺 %s ⇎ 只小写 %s ⇎ 行内尺与折平尺的分歧 %d 格共涨 %d 格 ⇎ "
     u"去编号后 %s ⇎ 跨行大写对 %s ⇎ 跨行小写对 %s ⇎ 落在页壳里的 %d 对" % (
         J(G[u'ob_fold']), J(G[u'ob_fold_tot']), J(G[u'ob_lower']), J(G[u'ob_lower_tot']),
         J(G[u'kw_allcaps']), J(G[u'kw_lowercase']), len(G[u'ob_wrap']), sum(G[u'ob_wrap']),
         J(G[u'ob_tag']), J(G[u'st_up']), J(G[u'st_low']), G[u'st_in_shell']),
     u"并集账逐份平(%s) ⇎ 套叠账 %s ⇎ 行内对折平的分歧 %d 格只在 1122 与 9293 的 MUST NOT/SHOULD NOT 上; 现拼档与两档相减档逐份差 %s ⇎ 合计差 %d ⇎ "
     u"跨行式样 %s ⇎ 涉及 %d 份; 去编号让 9293 的 MAY 由 %d 枚变 %d 枚 ⇎ MUST 由 %d 变 %d——编号尾巴把粘连的词头解放出来, 这一档只改 9293。" % (
         J(G[u'ob_nest_ledger']), J([G[u'ob_fold_tot'][i] - G[u'kw_allcaps'][i] - G[u'kw_lowercase'][i]
                                     for i in range(NSRC)]), G[u'ob_ruler_diff'],
         J(G[u'st_by_doc']), G[u'st_up_close'], J(G[u'st_words']), G[u'st_docs'],
         G[u'ob_fold'][2][4], G[u'ob_tag'][2][4], G[u'ob_fold'][2][0], G[u'ob_tag'][2][0])),
    (u"带单位数值⇎宽严两轨⇎粘连写法",
     u"数值第四档: 一条 `\\d+(?:[.,]\\d+)?` 取数字段, 起始左邻是字母数字或点号则整枚作废, 单位词就地读(建条侧手工扫数字串 ⇎ 发射侧扫到第一枚数字); "
     u"严轨要求单位在词界上 ⇎ 宽轨放过单字母; 时长十式各按字面针数一遍",
     u"严 %s ⇎ 宽 %s ⇎ 两轨差 %d ⇎ 只在折平后才读得到(数字与单位被换行分到两行)%s 组 ⇎ 粘连写法 %s 枚 ⇎ 去重 %s 式 ⇎ 样本 %s ⇎ "
     u"带空格写法 %s 处 ⇎ 次数式 %s ⇎ 时长逐份 %s ⇎ 逐式 %s" % (
         J(G[u'numval_n']), J(G[u'numval_wide_n']), G[u'numunit_ruler_diff'], J(G[u'numunit_wrap']),
         J(G[u'glued_n']), J(G[u'glued_vari']), J(G[u'glued_all']), J(G[u'spaced_n']),
         J(G[u'numtimes']), J(G[u'dur_by_doc']), J(G[u'dur_by_form'])),
     u"宽轨多出的只有 9293 那枚 %s(单字母 s), 两轨之差 %d 枚; 逐份宽−严 %s; 严轨清单两把尺(就地读 ⇎ 词界筛)互差 %s; "
     u"时长两把聚合尺同值(%d 枚 ⇎ 账 %d) ⇎ 十式逐式之和 %d = 逐份之和 %d; 粘连九枚全在内核那份, 面外一份也不写这种形。" % (
         J(G[u'numval_extra']), G[u'numunit_ruler_diff'],
         J([G[u'numval_wide_n'][i] - G[u'numval_n'][i] for i in range(NSRC)]),
         J(G[u'numunit_track_diff']), sum(G[u'dur_by_doc']),
         sum(G[u'dur_by_doc']) - sum(G[u'dur_by_form']), sum(G[u'dur_by_form']), sum(G[u'dur_by_doc']))),
    (u"语形族 34 式⇎两把词尺",
     u"三十四式在两份词尺上各数一遍: 子串尺走 `str.count` ⇎ 整词尺走布尔表查档; 独有式与冷式由读数矩阵现导, 不抄建条侧的清单",
     u"总量 %s ⇎ 出现的式种数 %s ⇎ 一枚也不出的式 %s ⇎ 整词尺合计 %s ⇎ 子串尺比整词尺多读 %d 枚(整词尺全库 %d 枚) ⇎ 独有式清单 %s ⇎ 合计 %d 枚 ⇎ "
     u"“the TCP will” %s ⇎ “the TCP endpoint will” %s" % (
         J(G[u'spell_tot']), J(G[u'spell_vari']), J(G[u'spell_cold']), J(G[u'spell_word_tot']),
         sum(G[u'spell_tot']) - sum(G[u'spell_word_tot']), sum(G[u'spell_word_tot']),
         J(G[u'spell_excl']), G[u'excl_n'], J(G[u'tcp_will']), J(G[u'tcp_endpoint_will'])),
     u"两把尺的差逐份 %s ⇎ 账 %d 归零(同一族上两把尺不能混用); 独有 %d 式全落在内核那份 ⇎ 冷式只 “time-out” 一种——三份 TCP 文书都写 “time out” 或 "
     u"“timeout”; 采集侧的语形表与本遍逐格同(不符 %d 格)。" % (
         J([G[u'spell_tot'][i] - G[u'spell_word_tot'][i] for i in range(NSRC)]),
         sum(G[u'spell_diff']) - (sum(G[u'spell_tot']) - sum(G[u'spell_word_tot'])),
         G[u'excl_n'], len(G[u'pick_diffk']))),
    (u"1122 §4.2.3.5 → 9293 §3.8.3 重写⇎三通道差分",
     u"“重写”分三档判: 逐字同 ⇎ 剥编号后同 ⇎ 再把 implementers→implementors/acknowledgment→acknowledgement 归拼后同; 词面差分走三条通道——建条侧直接取 "
     u"`get_opcodes()` 默认档 ⇎ 本遍由 `get_matching_blocks()` 自己重造动作序列 ⇎ 再跑一遍 `autojunk=False` 档比标签序列; 节号由块首行上方最近的编号标题现读",
     u"块高 %s 行(含页壳 %s) ⇎ 字符 %s ⇎ 词 %s ⇎ 句 %s ⇎ 三档同句 %d ⇎ %d ⇎ %d ⇎ 新句 %d 句 ⇎ 相同 %d 词分 %d 段(最长 %d 词) ⇎ 删 %d ⇎ 插 %d ⇎ "
     u"替换 %d 处 ⇎ 段内编号 %d 枚吃 %d 字符 ⇎ 节号 %s ⇎ 题面两份逐字同(标志 %d)⇎ 块后第一节 %s" % (
         J(G[u'ov2_rows']), J(G[u'ov2_shell']), J(G[u'ov2_chars']), J(G[u'blk_words']), J(G[u'ov2_sents']),
         G[u'ov2_same_raw'], G[u'ov2_same_tag'], G[u'ov2_same_canon'], G[u'ov2_new'],
         G[u'blk_equal_words'], G[u'blk_equal_runs'], G[u'blk_longest'], G[u'blk_drop_words'],
         G[u'blk_insert_words'], G[u'blk_replace'], G[u'blk_tag_n'], G[u'blk_tag_chars'],
         J(G[u'ov_sec']), G[u'ov_title_same'], J(G[u'ov_next_sec'])),
     u"三档单调判定 %d/%d(剥编号救回 %d 句 ⇎ 归拼不再救回) ⇎ 三条通道给同一组数: 词账 %s ⇎ 动作数 %d ⇎ 替换两端 %d/%d ⇎ autojunk 无差 %d; "
     u"针重开窗与段表重开窗逐格差 行 %s ⇎ 壳 %s ⇎ 句 %s ⇎ 三档同句 %s ⇎ 新句 %s; 整块作子串读不通 %d ⇎ 窗越界截断 %d 扇 ⇎ 窗内带编号 %d 处。" % (
         1 if G[u'ov2_same_raw'] <= G[u'ov2_same_tag'] <= G[u'ov2_same_canon'] else 0, 2,
         G[u'ov2_same_tag'] - G[u'ov2_same_raw'], J(G[u'blk_form_ledger']), G[u'blk_op_n'],
         G[u'blk_op_rep_a'], G[u'blk_op_rep_b'], G[u'blk_autojunk_diff'], J(G[u'ov2_rows_close']),
         J(G[u'ov2_shell_close']), J(G[u'ov2_sents_close']), J(G[u'ov2_same_close']), G[u'ov2_new_close'],
         G[u'blk_is_substring'], G[u'ov_cut_n'], G[u'os_tag_in_window'])),
    (u"重印对照⇎反向针冷账",
     u"共现针在(份,式)矩阵上逐格数, 归属向量走 `Counter` 直方图 ⇎ 两两三四的共用走“文档下标组合逐枚数”; 反向针不问“含不含”而枚举命中并量跨行, "
     u"多解档由命中次数现判; 采集侧的矩阵从 `_b86meas.json` 回读后与本遍逐格比",
     u"793 事件表那一句在面上 %s 枚 ⇎ 共现 %d 式 ⇎ 他份命中 %d 枚 ⇎ 落点 %s ⇎ 9293 复印 %d 枚; 反向针 %d 枚 ⇎ 探针 %d 次 ⇎ 本份读得到 %d/%d ⇎ "
     u"他份命中 %d 枚 ⇎ 全冷 %d 枚 ⇎ 本份合计 %d 次 ⇎ 多解 %s" % (
         J(G[u'ev_n']), G[u'rp_n'], G[u'rp_others'], J(G[u'rp_other_src']), G[u'rp_reprint_9293'],
         G[u'neg_n'], G[u'neg_probes'], G[u'neg_self'], G[u'neg_n'], G[u'neg_others'],
         len(G[u'neg_cold']), G[u'neg_self_tot'], J(G[u'neg_multi'])),
     u"共现矩阵逐格差 %d ⇎ 落点名单两遍同 %d 份 ⇎ 反向矩阵逐格差 %d ⇎ 本份合计差 %d ⇎ 多解名单同判(差 %d)⇎ 逐式本份枚数 %s; "
     u"干净格(他份零 ⇎ 本份恰好一枚)%d/%d 枚。" % (
         G[u'rp2_close'], len(set(G[u'rp2_other_src']) & set(G[u'rp_other_src'])), G[u'ng2_close'],
         G[u'ng2_self'] - G[u'neg_self_tot'], G[u'ng2_multi_close'], J(G[u'ng2_multi_cnt']),
         G[u'neg_clean'], G[u'neg_n'])),
    (u"内核键表⇎名/正文双判",
     u"键行由 '=' 的 `str.partition` 链现切, 默认值四句式(Default: ⇎ default value is ⇎ default value of ⇎ 借参考句)也全走 partition 链; "
     u"相关性双判(名字含 retries/timeout ⇎ 正文谈重传)与只按名档各数一遍, 级联档再逐键核",
     u"键行 %d ⇎ 去重名 %d ⇎ 重名 %d 个 %s ⇎ 末枚键行在第 %d 行 ⇎ 双判 %d 枚 ⇎ 只按名 %d 枚 ⇎ 并集 %d ⇎ 交集 %d ⇎ 落选 %s ⇎ "
     u"键正文行合计 %d ⇎ 默认句式四档 %s ⇎ 读不到值 %d 枚 ⇎ 十六进制 %s ⇎ 数值面 %s" % (
         G[u'kn2_keys'], G[u'kn2_uniq'], len(G[u'kn2_dups']), J(G[u'kn2_dups']), G[u'kn2_last_hdr'],
         len(G[u'kn2_rel']), len(G[u'kn2_pick']), G[u'kn2_union'], G[u'lin_rel_both'],
         J(G[u'lin_rel_dropped']), G[u'kn2_body_rows'], J(G[u'kn2_shape_n']), G[u'kn2_none'],
         J(G[u'kn2_hex']), J(G[u'kn2_numvals'])),
     u"容斥账 %d ⇎ 两把名尺与建条侧名单差 %d/%d ⇎ 键行数差 %d ⇎ 正文行数差 %d ⇎ 四式级联逐键与句式档同值(不同者 %s ⇎ 句式档差 %s) ⇎ "
     u"直接答这题的四键默认值 %s ⇎ 逐行读不到而整块才读到的 %s(两遍同名单 %d) ⇎ 带句点尾 %d 处。" % (
         G[u'kn2_ie_close'], G[u'kn2_rel_close'], G[u'kn2_pick_close'], G[u'kn2_keys_close'],
         G[u'kn2_body_close'], J(G[u'kn2_dv_diff']), J(G[u'kn2_shape_close']), J(G[u'kn2_default_str']),
         J(G[u'kn2_wrap_gain']), G[u'kn2_wrap_close'], G[u'lin_val_punct'])),
    (u"倍增等式第四轨",
     u"“N 次重传, 初始 RTO = TCP_RTO_MIN” 走第四条轨: `itertools.accumulate` 逐次翻倍列成清单再取末项(建条侧 while 累加 ⇎ 发射侧 `2**k` 求和), "
     u"末次与杀死两个口径各算一遍; 三枚 RTO 参数由字符扫描器现取而非正则分组",
     u"syn_retries %d ⇒ 末次 %d ⇎ 杀死 %d 秒 ⇎ synack_retries %d ⇒ %d ⇎ %d 秒 ⇎ 面上印出的秒数 %s ⇎ 最小 N 末次口径 %d ⇎ 杀死口径 %d ⇎ "
     u"文书自己写 %d ⇎ 差 %s ⇎ 三枚 RTO %s ⇎ 粘连秒数印出 %s 枚" % (
         G[u'eq2_rows'][0][1], G[u'eq2_rows'][0][2], G[u'eq2_rows'][0][3], G[u'eq2_rows'][1][1],
         G[u'eq2_rows'][1][2], G[u'eq2_rows'][1][3], J(G[u'eq_printed_all']), G[u'eq2_min_last'],
         G[u'eq2_min_kill'], G[u'eq2_doc_says'], J(G[u'eq2_off_by']), J(G[u'eq2_rto_face']),
         J(G[u'eq2_printed'])),
     u"三轨求和同值(幂清单 ⇎ 逐次累加 ⇎ 闭式)差 %s ⇎ 两行六档对建条侧逐格差 %s(绝对值合计 %d)⇎ 两把尺 %s ⇎ 印出的粘连秒数与建条侧差 %s ⇎ "
     u"闭式轨的最小 N 末次 %d ⇎ 杀死 %d(与逐次轨同判 %d); 文书自己给的 %d 比逐次轨的 %d 多 %d 枚, 因为它把“杀死”与“末次”混在同一句里。" % (
         J(G[u'eq_ruler_ledger']),
         J([x for z in G[u'eq2_close'] for x in z]),
         sum([sum([abs(x) for x in z]) for z in G[u'eq2_close']]),
         J([x for z in G[u'eq2_ruler_gap'] for x in z]), J(G[u'eq2_printed_close']),
         G[u'eq_min_n_last'], G[u'eq_min_n_kill'],
         1 if (G[u'eq_min_n_last'], G[u'eq_min_n_kill']) == (G[u'eq2_min_last'], G[u'eq2_min_kill']) else 0,
         G[u'eq2_doc_says'], G[u'eq2_min_last'], G[u'eq2_off_by'][0])),
    (u"“924.6 秒”不可复算",
     u"这一枚登记成“文书印出的数”: 五枚候选算式(2^N−1 ⇎ 2^(N+1)−1 ⇎ N·rto ⇎ 线性段 ⇎ N=15 闭式)全部复算一遍再与面读数比, 单位由数后八码位现验",
     u"面上 %d 枚 ⇎ 逐份 %s ⇎ 面读数 %s ⇎ 候选 %s ⇎ 与候选的偏离 %s ⇎ 命中 %d ⇎ 紧跟 seconds 的 %d 枚" % (
         G[u'eq_9246_printed'], J(G[u'eq9246_by_src']), G[u'eq_9246_face'], J(G[u'eq_9246_cand']),
         J(G[u'eq_9246_gap']), G[u'eq_9246_hit'], G[u'eq2_9246_unit']),
     u"五格差全平(%s ⇎ 判定 %s)⇎ 偏离最小的一枚也差 %s 秒 ⇒ 这一枚不进任何门槛等式, 只登记; 锚 %s ⇎ %s。" % (
         J(G[u'eq2_cand_close']), G[u'eq2_hit_close'], min(G[u'eq_9246_gap']),
         QT(u'lin', u'The default value of 15 yields a hypothetical timeout of 924.6'),
         QT(u'lin', u'924.6'))),
    (u"段窗⇎端点自验",
     u"13 扇窗的窗界一律由字面针在摘壳折平面上现取偏移、经本遍段表映回原行, 窗文本再由行区间切片重折; 端点回原文件自验走第四档——逐行现折现找再按字符表映回字面",
     u"行 %s 合计 %d ⇎ 五份主答句窗 %d 行 ⇎ 词合计 %d ⇎ 字符合计 %d ⇎ 不同词 %s ⇎ 单行成窗 %d 扇 ⇎ 端点 %d 枚 ⇎ 整串在一行读通 %d ⇎ "
     u"被换行推到下一行 %d ⇎ 语气词 MUST %s ⇎ SHOULD %s ⇎ MAY %s ⇎ 编号 %s" % (
         J(G[u'pb_rows']), G[u'pb_rows_tot'], G[u'pb_five_rows'], G[u'pb_words_tot'], G[u'pb_chars_tot'],
         J(G[u'pb_vocab']), G[u'pb_one_line'], G[u'sr_n'], G[u'sr_whole'], G[u'sr_cut'],
         J(G[u'pb_tone_must']), J(G[u'pb_tone_should']), J(G[u'pb_tone_may']), J(G[u'pb_tone_tag'])),
     u"所报行号对得上 %d ⇎ 五份答句落窗 %s ⇎ 可选窗 %s ⇎ 落空 %d 份 ⇎ 窗内语气词与整串正则同数(差 %d)⇎ 9293 主答句窗与 1122 讨论窗的编号枚数对整份登记值差 %s; "
     u"MUST NOT 全窗零 ⇎ 唯一一枚 MAY 在 6298 的窗里。" % (
         G[u'sr_rows_close'], J(G[u'pb_ans_win']), J(G[u'pb_ans_n']), G[u'pb_ans_close'],
         G[u'pb_tone_close'], J(G[u'pb_tag_block_close']))),
    (u"“RFC 1122 recommends”双份⇎哨兵口径",
     u"同一式在两处印出: 标志尺逐份判在面 ⇎ 偏移尺取折平面与摘壳面两个档; 配对走二百码位窗逐字比; 读到 0 与“口径不存在”分开记——缺档给 -1 而不是 0",
     u"份数 %d/%d ⇎ 逐份标志 %s ⇎ 折平面偏移 %s ⇎ 摘壳面偏移 %s ⇎ 配对 %d 对 ⇎ 二百码位窗逐字相同 %s 对 ⇎ 答句页壳行 %s ⇎ 页码行 %s" % (
         G[u'kw_docs'], G[u'kw_present'].count(1), J(G[u'kw_present']), J(G[u'kw_head']), J(G[u'kw_head_sh']),
         G[u'kw_pair_n'], J(G[u'kw_same']), J(G[u'ans_shell_rows']), J(G[u'ans_page_rows'])),
     u"两档偏移差 %d ⇎ 与建条侧的偏移合计差 %d ⇎ 配对同段两遍差 %d; 答句所在行的壳行数是真量(%s ⇎ 两套通道逐格差 %s), "
     u"而 1122 面上根本没有关键词模板段, 段首偏移因此记 %d 而不是 0。" % (
         sum([abs(G[u'kw_head'][i] - G[u'kw_head_sh'][i]) for i in range(NSRC)]), G[u'kw2_close'],
         G[u'kw2_same_close'], J(G[u'ans_shell_rows']), J(G[u'ans_shell_close']), G[u'kw_head'][1])),
    (u"闭合账⇎锚账⇎键数账",
     u"门的右式 ⇎ 恒等式表达式 ⇎ DERIV 的算式都从两遍源码 `ast` 摘出后在本遍读数上 eval; 锚由条目正文的手写配对扫描现推, "
     u"归属走双轨(摘壳面 ⇎ 原行面)同判才计数; 键名清单由 AST 目标节点重建, 元组与列表目标一并摊平",
     u"布尔门 %d/%d ⇎ %d/%d ⇎ 恒等式 %d+%d=%d ⇎ V 形回读 %d 条 ⇎ DERIV %d 键/%d 处引用 ⇎ 采集对账 %d/%d ⇎ 锚 %d 处/去重 %d/独占 %d/跨界 %d/全份 %d ⇎ "
     u"编码区 %d 字符 ⇎ 键 %d" % (
         G[u'bool_green'], G[u'bool_all_n'], G[u'bool2_green'], G[u'bool2_all'],
         G[u'zid_scan_n'], G[u'zid_scan2_n'], len(CH[u'zid']), len(CH[u'zid']), len(DER), DCITE,
         G[u'pick_agree'], G[u'pick_agree'], G[u'anchor_total'], DIST, G[u'anchor_single'],
         G[u'anchor_cross'], G[u'anchor_all5'], G[u'enc_chars'], G[u'contract_n']),
     u"锚误读 %d 枚 ⇎ 原行读不到 %d 枚 ⇎ 未被本遍窗口认领 %d 枚 ⇎ 逐标签引用 %s ⇎ 复核 %d 格 ⇎ 键数账 建条 %d ⇎ 发射接手 %d ⇎ 新增 %d ⇎ 自计数 %d ⇎ "
     u"前缀多捞 %s ⇎ 未复算 %d ⇎ 独有 %d ⇎ 判词针 %d 枚 ⇎ 反向针 %d 枚 ⇎ 端点自验 %d 枚。" % (
         G[u'anchor_err'], len(MISSLINE), len(MISS), J([G[u'tag_' + t] for t in TAGS]), G[u'checks'],
         G[u'scan_key_n'], G[u'scan2_src_n'], G[u'scan2_key_n'], G[u'scan2_self_n'],
         J(G[u'scan2_prefixed_old']), len(UNCOVER), G[u'anchor_distinct'], G[u'needle_n'], G[u'neg_n'],
         G[u'sr_n'])),
]
assert len(rows) == 16, len(rows)
for _r in rows:
    _c = [cell(x) for x in _r]
    A(u'| %s | %s | %s | %s |' % tuple(_c))
A(u"")
CUTK = {}
for _k, _i in STR4:
    CUTK.setdefault(_k, []).append(_i)
MULTI4 = sorted([k for k, v in CUTK.items() if len(v) > 1])
DIFF4 = [(k, CUTK[k][0], CUTK[k][1]) for k in MULTI4
         if pieces4(k, CUTK[k][0])[0][0].strip() != pieces4(k, CUTK[k][1])[0][0].strip()]
assert all(len(CUTK[_k]) >= 2 for _k, _a, _b in DIFF4) and len(DIFF4) >= 1
assert sum([len(CUTK[_k]) for _k, _a, _b in DIFF4]) == 2 * len(DIFF4), u'切开词点不同的针有成三处的'
A(u"五份答话在本遍仍是五次不同的动作, 而答句不再抄建条侧登记的句子表: 句界由 `[.!?]` 前瞻后接空白或行尾的候选现取, "
  u"空格尾巴交 `[^ ]` 的 search 现跳, 首末行经本遍段表映回原行——词 %s ⇎ 字符 %s ⇎ 整句跨 %s 行 ⇎ 摘壳后 %s 行 ⇎ 首行 %s ⇎ 末行 %s。 "
  u"793 答的是时长不是次数: %s 就挂在 RETRANSMISSION TIMEOUT 那条规则里, 而那条规则在它面上被硬换行切成 %s ⇢ %s, 一次也不数; "
  u"1122 把放弃拆成两阈值 %s %s, 又给下界 %s ⇢ %s; 9293 照登同一条并另许 %s; 6298 只钉计时下限 %s %s; "
  u"ip-sysctl 交回参数表 %s, 答句写作 %s %s。 五句里整串在一行内读得通的只有 9293 那一份(%s 份), 其余四句都被 72 列硬换行切开; "
  u"答句里印出的编号 %s 枚 ⇎ 大写义务词 %s ⇎ 非 ASCII %s 枚——6298 那句带一枚 MAY, 余下四份的答话一个语气词也不大写。" % (
      J(G[u'ans_words']), J(G[u'ans_chars']), J(G[u'ans_sent_span']), J(G[u'ans2_rows_kept']),
      J(G[u'ans_sent_line']), J(G[u'ans_sent_end']),
      QT(u'793', u'The present global default is five'),
      QT(u'793', u'send the segment at the front of the'), QT(u'793', u'retransmission queue again'),
      QT(u'1122', u'a threshold R2 greater than R1, close the'), QT(u'1122', u'Connection'),
      QT(u'1122', u'The value of R2 SHOULD'), QT(u'1122', u'correspond to at least 100 seconds'),
      QT(u'9293', u'set R2 to \"infinity\"'),
      QT(u'6298', u'A maximum value MAY be placed on RTO provided it is at least 60'),
      QT(u'6298', u'seconds'), QT(u'lin', u'tcp_retries2 - INTEGER'), QT(u'lin', u'would'),
      QT(u'lin', u'retransmit N times before killing the connection'),
      J(G[u'ans_needle_line']), J(G[u'ans_tag_n']), J(G[u'ans_ob']), J(G[u'na_in_ans'])))
EX4 = []
for _k, _a, _b in DIFF4[:2]:
    _seg = []
    for _i in (_a, _b):
        _o = pieces4(_k, _i)[0]
        _seg.append(u'%s: %s' % (TAGS[_i], u' ⇢ '.join([QRAW(TAGS[_i], _o[0].strip())] +
                                                       [u'⟨%s⟩' % z.strip() for z in _o[1:]])))
    EX4.append(u' ‖ '.join(_seg))
assert len(EX4) == min(2, len(DIFF4)) and all(u'⟨' in z for z in EX4), EX4
A(u"被硬换行切开的判词 %d 种 ⇎ %d 处跨行命中 ⇎ 最长跨 %d 行(逐份增益 %s, 跨行合计对换行增益账 %d)。 "
  u"本遍不问“这一行含不含针”, 而是把每一次命中区间与摘壳段表求交, 再把落在每一行的那一截经逐字符表映回原行字面: "
  u"各半折一次拼得回原针 ⇎ 每一半都在原行里逐字读得到, %d 处全过。 同一枚针在两处被切在不同词后的有 %d 种(两两成对, 共 %d 处), 例如 "
  u"%s——切点由排版宽度决定, 不由句法决定, 所以给跨行判词挂锚只能落到行, 不能落到短语。" % (
      G[u'sc_needle_n'], G[u'sc_span_tot'], G[u'sc_max_span'], J(G[u'wrap_gain']), G[u'sc_gain_close'],
      len(STR4), len(DIFF4), sum([len(CUTK[_k]) for _k, _a, _b in DIFF4]), J(EX4)))
A(u"唯一一枚被编号切开的针(第 %d 枚)只在 9293: 摘壳折平面上它读作 `%s`, 接合处横着 `%s`(%d 码位)——本遍现读的上下文, 不是手填。 "
  u"把两半之间的这一段抹掉再折一次, 面串就读回原针(区域比针长的 %d 码位 = 编号串 %d + 它左边那一格空白, 折平留下括号两侧各一格而针只带一格接合空白)。 "
  u"原行逐字 %s。 这一族在本遍被按 token 现判成四形: 连字符式 %d 枚 = 括号内 %d + 裸形 %d + 整对拉开 %d(差 %d 归零), "
  u"被换行切开的 %d 枚 = 数字推到下一行 %d + 括号整对拉开 %d, 那一枚的上下文 %s; 按词种分 %s, 之和 %d = 连字 %d(账 %d)。 "
  u"抹掉编号只改 9293 一家的读法: 涨针清单 %s ⇎ 挪动 %s, 而 9293 的 MAY 由 %s 里第 5 式 %d 枚变 %d 枚——编号尾巴把粘连的词头解放出来。" % (
      K7, NK4[K7], EATEN.strip(), len(EATEN.strip()), TAG_EAT, len(EATEN.strip()),
      QRAW(u'9293', RAW7.strip()), G[u'tag_dash'][2], G[u'tag_in_paren'][2], G[u'tag_bare'][2],
      G[u'tag_paren_apart'][2], G[u'tag_split_ledger'][2], G[u'tag_split_manual'][2],
      G[u'tag_num_nextline'][2], G[u'tag_paren_apart'][2], J(G[u'tag_apart_ctx']),
      J(G[u'tag_kind'][2]), sum(G[u'tag_kind'][2]), G[u'tag_dash'][2],
      sum(G[u'tag_kind'][2]) - G[u'tag_dash'][2], J(G[u'tag_gain_needles']), J(G[u'tag_move']),
      J(G[u'ob_fold'][2]), G[u'ob_fold'][2][4], G[u'ob_tag'][2][4]))
CUT3RD = set(G[u'wrap_cut']) | set(G[u'shell_cut']) | set(G[u'tag_cut'])
assert len(CUT3RD) == G[u'wrap_cut_n'] + len(G[u'shell_cut']) + len(G[u'tag_cut']), u'三档切开针不互斥'
A(u"三处口径要在注里挑明, 因为它们是本遍与前三遍唯一可能读出差的地方, 而差别来自实现不是来自数据。 "
  u"其一: -1 与 0 分家。 “RFC 1122 recommends” 的段首偏移在四份面上根本不存在(793 ⇎ 1122 ⇎ 6298 ⇎ lin 无此段), 本遍记 %s 而不是 0——"
  u"缺档写成 0 会把“口径不成立”伪装成“零命中”; 反面是答句跨度里的页码形行 %s, 那五枚 0 是真量出来的 0(空壳 %s ⇎ 页码 %s ⇎ 与建条侧账 %s)。 "
  u"其二: 负号照登记。 去编号面上本遍的 9293 与建条面的长度差 %d 码位(负=本遍抹得多)(%s), 因为两把尺吃字不同(本遍逐 token 抹 %d ⇎ 建条整族抹 %d), "
  u"差值取负而不是取绝对值——取绝对值就把“抹得多”与“抹得少”混成一档。 其三: 恒等式换成真容斥。 七路形状命中之和 %s 减重复命中 %s 才是壳行 %s"
  u"(五份合计账 0), 而不是“自己等于自己”; 页壳切开 %d 枚 ⇎ 编号切开 %d 枚 ⇎ 换行切开 %d 枚三档互不相交, 并起来才是 %d 枚一行读不通的针。" % (
      J(G[u'kw_head']), J(G[u'ans_page_rows']), J(G[u'ans2_blank_span']), J(G[u'ans2_page_span']),
      J(G[u'ans_page_close']), G[u'td_face_gap'][2], J(G[u'td_face_gap']), G[u'td_chars'][2],
      G[u'tag_chars'][2], J(G[u'shape_sum']), J(G[u'shape_ovl']), J(G[u'shell_lines']),
      len(G[u'shell_cut']), len(G[u'tag_cut']), G[u'wrap_cut_n'], len(CUT3RD)))
A(u"内核那份给的不是一枚数而是一条等式, 本遍用第四条轨(`itertools.accumulate` 逐次翻倍取末项)复算: syn_retries=%d ⇒ 末次 %s 秒 ⇎ 杀死 %s 秒, "
  u"synack_retries=%d ⇒ %s ⇎ %s, 与面上自己印出的 %s 逐格同值(两行六档对建条侧差 %s ⇎ 绝对值合计 %d ⇎ 幂清单⇎累加⇎闭式三轨差 %s); "
  u"“多久到 100 秒”在两个口径下是 %d 与 %d, 而文书自己写 %s ⇎ 差 %s——差在它把“末次”与“杀死”混在同一句里, 不在算法。 "
  u"唯独 “924.6 秒” 不在任何一轨上: 五枚候选 %s 对它的偏离 %s ⇎ 命中 %d ⇎ 最小差 %s 秒, 单位那一档由数后八码位现验(%d 枚紧跟 seconds), "
  u"所以这一枚只能登记成“文书印出的数”(%s ⇎ %s), 不进任何门槛等式——它的算法不在这份文档里。" % (
      G[u'eq2_rows'][0][1], G[u'eq2_rows'][0][2], G[u'eq2_rows'][0][3], G[u'eq2_rows'][1][1],
      G[u'eq2_rows'][1][2], G[u'eq2_rows'][1][3], J(G[u'eq_printed_all']),
      J([x for z in G[u'eq2_close'] for x in z]),
      sum([sum([abs(x) for x in z]) for z in G[u'eq2_close']]), J(G[u'eq_ruler_ledger']),
      G[u'eq2_min_last'], G[u'eq2_min_kill'], QT(u'lin', u'a value of at least 8'), J(G[u'eq2_off_by']),
      J(G[u'eq_9246_cand']), J(G[u'eq_9246_gap']), G[u'eq_9246_hit'], min(G[u'eq_9246_gap']),
      G[u'eq2_9246_unit'], QT(u'lin', u'The default value of 15 yields a hypothetical timeout of 924.6'),
      QT(u'lin', u'924.6')))
A(u"9293 把 1122 的那一节重写了一遍, 而“重写”在这里是三条单调档位判出来的: 逐字同 %d 句 ⇎ 剥编号后同 %d 句 ⇎ 再把 implementers→implementors/"
  u"acknowledgment→acknowledgement 归拼后同 %d 句——第三档一枚也不救回, 所以两家的差异不是拼写规范化能抹平的; 词面差分三条通道给同一组数 "
  u"(删 %d ⇎ 插 %d ⇎ 替换 %d 段 ⇎ 三档词账 %s 全平 ⇎ autojunk 无差 %d), 新句 %d 句逐枚定位回 9293 面(%d/%d 枚定位到 ⇎ 前缀多解 %d 枚)。 "
  u"节号倒是对不上: 同一道题在两份文书里挂在 %s 下, 题面 %d 个词逐字同(标志 %d)——换代改的是编号与措辞, 不是结论。 "
  u"另一处换代是术语: “the TCP will” 只在 793(%s 枚)⇎ “the TCP endpoint will” 只在 9293(%s 枚), 9293 把 endpoint 立成术语后又给义务词缀上编号 "
  u"(%s 那一句就是声明), 于是同一句 MUST 在两份文书里的可读性走的是两条通道。" % (
      G[u'ov2_same_raw'], G[u'ov2_same_tag'], G[u'ov2_same_canon'], G[u'blk_drop_words'],
      G[u'blk_insert_words'], G[u'blk_replace'], J(G[u'blk_form_ledger']), G[u'blk_autojunk_diff'],
      G[u'ov2_new'], G[u'os_located'], G[u'os_n'], G[u'os_ambig'], J(G[u'ov_sec']),
      len(G[u'ov_sec_title'][0].split()), G[u'ov_title_same'],
      J(G[u'tcp_will']), J(G[u'tcp_endpoint_will']), QT(u'9293', u'individually labeled')))
A(u"")
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"")
A(u"五份文件在 RFC Editor 此刻的现行状态页与勘误页——1122 的 R1 ⇎ R2 两句与 9293 的 %s ⇎ %s 有没有被 errata 改过措辞, "
  u"在库只有已发布的那一份正文, 判不了; 现网内核此刻的装机值(%s 这条登记的是默认式样, 不是运行值)判不了; ip-sysctl 在各内核版本间这段措辞的改动判不了, "
  u"因此“924.6 秒”与“at least 8”是否曾在同一版里自洽也无从对证。 6298 那句只给 RTO 上限的下限(%s), 它既不给次数也不给放弃时刻, "
  u"而内核那份的 rto_max 与它是两回事: 面内没有任何一条边把“最大 RTO”与“放弃”连起来。 最后, 判词针被换行切开的 %d 处只说明排版, "
  u"不说明句法——同一枚针在 1122 与 9293 被切在不同词后(%d 种), 谁抄谁、改了几处都由不得这一档。" % (
      QT(u'9293', u'The value of R2 SHOULD'), QT(u'1122', u'set R2 to'),
      QT(u'lin', u'tcp_retries2 - INTEGER'), QT(u'6298', u'at least 60'),
      G[u'sc_span_tot'], len(DIFF4)))
A(u"")

NEW = u"## ⛓解读注" + NL + NL + NL.join(L2) + NL
_i2 = MD.index(u"## ⛓解读注")
out = MD[:_i2] + NEW
assert out.count(u"## ⛓解读注") == 1, out.count(u"## ⛓解读注")
assert out.startswith(MD[:_i2]), u'前段被动过'
T2 = ENTRY + u'.tmp'
io.open(T2, 'w', encoding='utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"16 解读注 %d 行 ⇎ %d 码位 ⇎ 表 %d 行 ⇎ 锚 %d 枚 ⇎ 切开例 %d ⇎ 复算 %d 键不符 %d" % (
    len(L2), len(NEW), len(rows), len(ANCHS), len(DIFF4), len(G), len(BAD)))





