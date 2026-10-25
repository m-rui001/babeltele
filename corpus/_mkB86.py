# -*- coding: utf-8 -*-
"""建条目第二遍(B86): “同一条连接重传几次、多久之后该放弃”, 五份一手文书各答一遍
793(1981 TCP 规范: 事件表把 RETRANSMISSION TIMEOUT 写成无条件循环——再发一次、重置定时器、返回, 全文一枚阈值也没有;
它只在 OPEN 调用里给一句 “The present global default is five minutes”) ⇎ 1122(1989 主机需求: 立 R1/R2 双阈值并声明
两把尺任选, R2 SHOULD ≥100 秒 ⇎ SYN 的 R2 MUST ≥3 分钟, 还把设 R2 的权利交给应用) ⇎ 9293(2022 STD 1: 逐句重印 1122
那一段并挂 (MUST-20)…(SHLD-11) 编号, 独家把 R2 写成 "infinity", 同时原样保留 793 的无限循环并把 “the TCP will”
改成 “the TCP endpoint will”) ⇎ 6298(2011 RTO 计算: 只封顶单次超时 “at least 60 seconds”, 通篇不谈总放弃)
⇎ Linux ip-sysctl.txt(实现文档: 把 R1/R2 落成 tcp_retries1=3 ⇎ tcp_retries2=15, 给 (N, N+1) 错位口径、
倍增等式 6→63→127 ⇎ 5→31→63、924.6 秒的 hypothetical timeout, 和一整组 SCTP 纯次数阈值)。

本遍与采集侧(_pick86.py)换机制而不换定义, 九处:
①字面针: 采集侧游标 find 环 ⇎ 本遍 re.findall(re.escape) 整体扫描, 另立重叠档 finditer('(?=针)');
②整词尺: 采集侧邻居字符手扫 ⇎ 本遍先把全串翻成三张布尔表(字母/数字/字母数字)再查表读左右邻, 第三轨用断言正则——三把尺逐枚同数才入账;
③壳谓词: 采集侧对整行跑序列正则 ⇎ 本遍 strip 后按 token 形状判(末两 token ⇎ 首 token ⇎ 年形切片), 逐行必须同集;
④行号尺: 采集侧用 4 行滑窗在折平面上试 ⇎ 本遍建累积长度表交给 bisect 由面偏移直映原行;
⑤句界: 采集侧 (?<=[.!?]) + 正则切句 ⇎ 本遍逐字符扫“句末标点+空白+小写或左括号”;
⑥数值抽取: 采集侧一条 RXU 选择支 ⇎ 本遍手工扫数字串再就地读单位词, 严尺(四个单位词) ⇎ 宽尺(容裸 s)分档;
⑦默认值: 采集侧靠 'Default:' 正则取键值 ⇎ 本遍按四句式级联现读并记下每一键走的哪一式;
⑧等式: 采集侧 sum(2**k for k in range(N)) ⇎ 本遍逐次倍增值累加, 两把尺同数才入账;
⑨池代数: 采集侧集合 & ⇎ 本遍 Counter 直方图 ⇎ 组合逐枚数共现, 两条通道同数才算复核。
四档口径: 原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳去编号折平(第三⇎第四档之差只由 9293 的编号族贡献)。
所有正文数字由 V()/J()/EXPR() 注册后插值, 一枚都不手打; 锚一律由面上位置导出。键名等于所量之物。"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'793', u'1122', u'9293', u'6298', u'lin']
NSRC = 5
PATH = [u'corpus/raw/tcpRetr/rfc793.txt', u'corpus/raw/tcpRetr/rfc1122.txt',
        u'corpus/raw/tcpRetr/rfc9293.txt', u'corpus/raw/tcpRetr/rfc6298.txt',
        u'corpus/raw/tcpRetr/ip-sysctl.txt']
FAM = [u'old', u'old', u'new', u'new', u'tbl']
IDS = [u'793', u'1122', u'9293', u'6298', u'ip-sysctl']
OLD = [i for i in range(NSRC) if FAM[i] == u'old']
NEW = [i for i in range(NSRC) if FAM[i] == u'new']
TBL = [i for i in range(NSRC) if FAM[i] == u'tbl']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire86.py 把这一段 ⇎ _mk86emit.py 的 SCAN2 段机械切进 audit.py::_b86_scan)


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
RAWL = [t.split(NL) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]


def pnorm(s):
    return u' '.join(s.lower().split())


def fold(s):
    return u' '.join([c for c in re.split(u'\\s', s) if c != u''])


def cnt_cur(hay, nd):
    """采集侧那一把(游标 find 环), 本遍只用于对拍。"""
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def cnt_re(hay, nd):
    """本遍的字面针轨: 转义后整体正则扫描(采集侧是游标环)。"""
    return len(re.findall(re.escape(nd), hay))


def cnt_ovl(hay, nd):
    """重叠档: 同一处允许被后面那次命中起点复用。"""
    return len(re.findall(u'(?=%s)' % re.escape(nd), hay))


def _tabs(s):
    return ([c.isalpha() for c in s], [c.isdigit() for c in s], [c.isalnum() for c in s])


def ub_tab(s, w, fl, kind=u'alpha'):
    """本遍的整词尺: 命中后查布尔表读左右邻(采集侧是逐字符手扫)。"""
    al, dg, an = fl
    t = al if kind == u'alpha' else dg if kind == u'digit' else an
    c, i, n, m = 0, 0, len(w), len(s)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if not (a >= 0 and t[a]) and not (b < m and t[b]):
            c += 1
        i = j + 1


def ub_cur(s, w, kind=u'alpha'):
    """采集侧那一把(邻居字符手扫), 本遍只用于对拍。"""
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if kind == u'alpha':
            ok = not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha())
        elif kind == u'digit':
            ok = not (a >= 0 and s[a].isdigit()) and not (b < len(s) and s[b].isdigit())
        else:
            ok = not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())
        if ok:
            c += 1
        i = j + 1


def ub_re(s, w, kind=u'alpha'):
    """第三轨: 负向断言正则。"""
    a = u'(?<![A-Za-z])' if kind == u'alpha' else u'(?<![0-9])' if kind == u'digit' else u'(?<![0-9A-Za-z])'
    b = u'(?![A-Za-z])' if kind == u'alpha' else u'(?![0-9])' if kind == u'digit' else u'(?![0-9A-Za-z])'
    return len(re.findall(a + re.escape(w) + b, s))


def is_shell_pick(x):
    """采集侧壳谓词的逐字照抄(整行序列正则), 供两遍壳集对拍用。"""
    if re.search(u'\\[Page \\d+\\]', x):
        return True
    if re.match(u'^\\s*(September 1981|Transmission Control Protocol)\\s*$', x):
        return True
    if re.match(u'^RFC1122 +\\S', x):
        return True
    if re.match(u'^Internet Engineering Task Force\\s*$', x):
        return True
    if re.search(u'RFC ?\\d{4}[^A-Za-z0-9]+.*((19|20)\\d\\d)\\s*$', x):
        return True
    if re.match(u'^\\s*(Internet Engineering Task Force|Internet-Draft)', x):
        return True
    if x == u'\x0c':
        return True
    return x.strip() == u''


def _yearish(w):
    return len(w) == 4 and w.isdigit() and (w[:2] == u'19' or w[:2] == u'20')


def sh_blank(x):
    return x.strip() == u''


def sh_ff(x):
    return x == u'\x0c'


def sh_foot(x):
    t = x.strip().split()
    return len(t) >= 2 and t[-2] == u'[Page' and t[-1].endswith(u']') and t[-1][:-1].isdigit()


def sh_hdr793(x):
    return x.strip().split() in ([u'September', u'1981'], [u'Transmission', u'Control', u'Protocol'])


def sh_hdr1122(x):
    t = x.strip().split()
    return len(t) > 1 and t[0] == u'RFC1122'


def sh_ietf(x):
    return x.strip().split() == [u'Internet', u'Engineering', u'Task', u'Force']


def sh_hdrnew(x):
    """新式页壳的 token 尺: 行末是年形 token ⇎ 行里有一枚 RFC+四位数(或裸 RFC 后跟四位数), 或行首是那两个抬头。"""
    t = x.strip().split()
    if not t:
        return False
    if t[0].startswith(u'Internet-Draft') or t[:4] == [u'Internet', u'Engineering', u'Task', u'Force']:
        return True
    if not _yearish(t[-1]):
        return False
    for k in range(len(t) - 1):
        h = t[k]
        if h.startswith(u'RFC') and len(h) == 7 and h[3:].isdigit():
            return True
        if h == u'RFC' and len(t[k + 1]) == 4 and t[k + 1].isdigit():
            return True
    return False


def shell_shape(x):
    """本遍的壳谓词: strip 后按 token 形状判, 一枚序列正则也不跑。"""
    return (sh_blank(x) or sh_ff(x) or sh_foot(x) or sh_hdr793(x) or sh_hdr1122(x)
            or sh_ietf(x) or sh_hdrnew(x))


def tag_runs(x):
    return len(re.findall(u'\\d+', x))


TAGR = re.compile(u' \\((MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHLD|ED)-[0-9]+\\)', re.I)
TAGBR = re.compile(u'\\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHLD|ED)-[0-9]+\\b')


def tag_strip(s):
    return TAGBR.sub(u'', TAGR.sub(u'', s))


def sent_cuts(face):
    """本遍的句界尺: 逐字符扫“句末标点 + 至少一枚空格”, 返回每句的 [起, 止) 表。
       采集侧是一条 re.split('(?<=[.!?]) +')——同一定义, 两把尺必须逐句同列表才入账。"""
    n, out, start, k = len(face), [], 0, 0
    while k < n:
        if face[k] in u'.!?' and (k + 1 >= n or face[k + 1] == u' '):
            j = k + 1
            while j < n and face[j] == u' ':
                j += 1
            out.append((start, k + 1))
            start = j
            k = j
            continue
        k += 1
    if start < n:
        out.append((start, n))
    return [(a, b) for a, b in out if face[a:b].strip() != u'']


def sent_at(spans, at):
    for a, b in spans:
        if a <= at < b:
            return a, b
    return spans[0][0], spans[-1][1]


# ---------- 0. 面量 ⇎ 行式 ⇎ 换页账 ----------
F['bytes'] = [len(B[i]) for i in range(NSRC)]
F['bytes_stat'] = [os.path.getsize(p) for p in PATH]
F['cp'] = [sum(1 for _ in T[i]) for i in range(NSRC)]          # 逐字符计数, 不用 len()
F['n_lf'] = [len([m.start() for m in re.finditer(u'\\n', T[i])]) for i in range(NSRC)]
F['n_cr'] = [len([m.start() for m in re.finditer(u'\\r', T[i])]) for i in range(NSRC)]
F['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
F['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
F['readlines'] = [sum(1 for _ in io.StringIO(T[i])) for i in range(NSRC)]
F['ff'] = [cnt_re(T[i], u'\x0c') for i in range(NSRC)]
F['ff_led'] = [len([x for x in L[i] if len(x) and ord(x[0]) == 12]) for i in range(NSRC)]
F['ff_alone'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
F['ff_before_nl'] = [cnt_ovl(T[i], u'\x0c' + NL) for i in range(NSRC)]
F['ff_at_eof'] = [1 if T[i][-1:] == u'\x0c' else 0 for i in range(NSRC)]
F['trailing_nl'] = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
F['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
F['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
F['maxlen_scan'] = []
for i in range(NSRC):
    _m, _c = 0, 0
    for ch in T[i]:                      # 逐字符走面, 遇换行归零、遇回车跳过(不经任何 split)
        if ch == NL:
            _m = _c if _c > _m else _m
            _c = 0
        elif ch != u'\r':
            _c += 1
    _m = _c if _c > _m else _m
    F['maxlen_scan'].append(_m)
F['tab'] = [cnt_re(T[i], u'\t') for i in range(NSRC)]
F['bom'] = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
F['bom_after_fold'] = [1 if u'\ufeff' in pnorm(T[i][1:]) else 0 for i in range(NSRC)]
NAOFF = [[m.start() for m in re.finditer(u'[^\\x00-\\x7f]', T[i])] for i in range(NSRC)]
RAWCUM = []
for i in range(NSRC):
    _a, _t = [], 0
    for _x in T[i].split(NL):
        _t += len(_x) + 1
        _a.append(_t)
    RAWCUM.append(_a)
import bisect as _bs


def cum_line_raw(i, off):
    return _bs.bisect_right(RAWCUM[i], off)


F['na_total'] = [len(NAOFF[i]) for i in range(NSRC)]
F['na_codepoints'] = [sorted(set(ord(T[i][k]) for k in NAOFF[i])) for i in range(NSRC)]
F['utf8_extra'] = [sum([len(T[i][k].encode('utf-8')) - 1 for k in NAOFF[i]]) for i in range(NSRC)]
F['na_lines'] = [len(set([cum_line_raw(i, k) for k in NAOFF[i]])) for i in range(NSRC)]
F['na_shell_lines'] = [len(set([cum_line_raw(i, k) for k in NAOFF[i]
                                if shell_shape(L[i][cum_line_raw(i, k)])])) for i in range(NSRC)]
F['na_body_lines'] = [F['na_lines'][i] - F['na_shell_lines'][i] for i in range(NSRC)]
F['rows_ledger'] = [F['splitlines'][i] - F['splitnl'][i] for i in range(NSRC)]
F['rows_pred'] = [F['ff_before_nl'][i] - F['trailing_nl'][i] for i in range(NSRC)]
F['rows_ledger_diff'] = [F['rows_ledger'][i] - F['rows_pred'][i] for i in range(NSRC)]
F['byte_cp_ledger'] = [F['bytes'][i] - F['cp'][i] - F['utf8_extra'][i] for i in range(NSRC)]
F['line_split_ledger'] = [F['nonblank'][i] + F['blank'][i] - F['splitnl'][i] for i in range(NSRC)]
F['bytes_vs_stat'] = 0 if F['bytes'] == F['bytes_stat'] else 1
F['lf_vs_readlines'] = [F['readlines'][i] + F['trailing_nl'][i] - F['splitnl'][i] for i in range(NSRC)]
F['splitlines_ledger'] = [F['splitlines'][i] - F['n_lf'][i] - F['ff'][i] for i in range(NSRC)]
print(u'0 面量:', json.dumps(dict((k, F[k]) for k in
      ['bytes', 'cp', 'n_lf', 'n_cr', 'splitnl', 'splitlines', 'readlines', 'ff', 'ff_led', 'ff_alone',
       'blank', 'nonblank', 'maxlen', 'tab', 'bom', 'rows_ledger', 'rows_pred'])))
print(u'  非ASCII:', F['na_total'], F['na_codepoints'], u' utf8 多出的字节:', F['utf8_extra'])

# ---------- 1. 壳账: 三个序列化家族 ----------
FOOT = [len([x for x in L[i] if sh_foot(x)]) for i in range(NSRC)]
HDR793 = [len([x for x in L[i] if sh_hdr793(x)]) for i in range(NSRC)]
HDR1122 = [len([x for x in L[i] if sh_hdr1122(x)]) for i in range(NSRC)]
IETF = [len([x for x in L[i] if sh_ietf(x)]) for i in range(NSRC)]
HDRNEW = [len([x for x in L[i] if sh_hdrnew(x)]) for i in range(NSRC)]
F['foot'] = FOOT
F['hdr793'] = HDR793
F['hdr1122'] = HDR1122
F['ietf_alone'] = IETF
F['hdrnew'] = HDRNEW
F['pgnum'] = [len([x for x in L[i] if x.strip() != u'' and tag_runs(x) == 1
                  and not [c for c in x if not (c.isdigit() or c.isspace())]]) for i in range(NSRC)]
F['keylin'] = [len([x for x in L[i] if re.match(u'^[a-z_][a-z_0-9]* - (INTEGER|BOOLEAN|STRING|DWORD)\\s*$', x)])
               for i in range(NSRC)]
F['default_lines'] = [len([x for x in L[i] if re.match(u'^\\s*Default:', x)]) for i in range(NSRC)]
F['shell_pick'] = [len([1 for x in L[i] if is_shell_pick(x)]) for i in range(NSRC)]
F['shell_shape'] = [len([1 for x in L[i] if shell_shape(x)]) for i in range(NSRC)]
F['shell_pred_diff'] = [len([1 for x in L[i] if is_shell_pick(x) != shell_shape(x)]) for i in range(NSRC)]
F['shell_lines'] = F['shell_shape']
F['body_lines'] = [len([1 for x in L[i] if not shell_shape(x)]) for i in range(NSRC)]
SHPREDS = [sh_blank, sh_ff, sh_foot, sh_hdr793, sh_hdr1122, sh_ietf, sh_hdrnew]
F['shape_hits'] = [sum([len([1 for x in L[i] if f(x)]) for f in SHPREDS]) for i in range(NSRC)]
F['shape_ovl'] = [sum([max(0, len([1 for f in SHPREDS if f(x)]) - 1) for x in L[i]]) for i in range(NSRC)]
F['shape_sum'] = F['shape_hits']
F['shell_ledger'] = [F['shell_lines'][i] - (F['shape_sum'][i] - F['shape_ovl'][i]) for i in range(NSRC)]
F['body_shell_ledger'] = [F['body_lines'][i] + F['shell_lines'][i] - F['splitnl'][i] for i in range(NSRC)]
F['pgnum_in_shell'] = [len([x for x in L[i] if x.strip() != u'' and tag_runs(x) == 1
                            and not [c for c in x if not (c.isdigit() or c.isspace())] and shell_shape(x)])
                       for i in range(NSRC)]
F['pgnum_naked'] = [F['pgnum'][i] - F['pgnum_in_shell'][i] for i in range(NSRC)]
print(u'1 壳: 页脚', FOOT, u' 793眉', HDR793, u' 1122眉', HDR1122, u' 新式眉', HDRNEW,
      u' IETF独立', IETF, u' 独立页码', F['pgnum'], u' 键行', F['keylin'], u' Default行', F['default_lines'])
print(u'  壳行(照抄尺/形状尺)', F['shell_pick'], F['shell_shape'], u' 逐行分歧', F['shell_pred_diff'],
      u' 剥壳正文行', F['body_lines'], u' 形状重数', F['shape_ovl'])

# ---------- 2. 义务词四档 ⇎ 编号族 ⇎ 大小写两代 ----------
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']
OBL = [u'must', u'must not', u'should', u'should not', u'may']
FOL = [pnorm(T[i]) for i in range(NSRC)]
SHP = [pnorm(NL.join([x for x in L[i] if not shell_shape(x)])) for i in range(NSRC)]
SHTAG = [tag_strip(SHP[i]) for i in range(NSRC)]
# 义务词比的是大小写, 折平必须换一把不转小写的尺(pnorm 会把 MUST 折成 must, 四档全读成 0)
FOLDX = [fold(T[i]) for i in range(NSRC)]
SHPX = [fold(NL.join([x for x in L[i] if not shell_shape(x)])) for i in range(NSRC)]
SHTAGX = [tag_strip(SHPX[i]) for i in range(NSRC)]
_tabs_all = [_tabs(FOL[i]) for i in range(NSRC)]
_tabs_x = [_tabs(FOLDX[i]) for i in range(NSRC)]
_tabs_sx = [_tabs(SHPX[i]) for i in range(NSRC)]
_tabs_tx = [_tabs(SHTAGX[i]) for i in range(NSRC)]
F['foldx_ledger'] = [len(FOLDX[i]) - len(FOL[i]) for i in range(NSRC)]
F['shpx_ledger'] = [len(SHPX[i]) - len(SHP[i]) for i in range(NSRC)]
F['ob_line'] = [[sum([ub_tab(x, w, _tabs(x), u'alpha') for x in L[i]]) for w in OB] for i in range(NSRC)]
F['ob_fold'] = [[ub_tab(FOLDX[i], w, _tabs_x[i], u'alpha') for w in OB] for i in range(NSRC)]
F['ob_sh'] = [[ub_tab(SHPX[i], w, _tabs_sx[i], u'alpha') for w in OB] for i in range(NSRC)]
F['ob_tag'] = [[ub_tab(SHTAGX[i], w, _tabs_tx[i], u'alpha') for w in OB] for i in range(NSRC)]
F['ob_ruler_diff'] = len([1 for i in range(NSRC) for k in range(len(OB))
                          if F['ob_sh'][i][k] != ub_re(SHPX[i], OB[k])])
F['ob_wrap'] = [F['ob_fold'][i][k] - F['ob_line'][i][k] for i in range(NSRC) for k in range(len(OB))]
F['ob_line_tot'] = [sum(F['ob_line'][i]) for i in range(NSRC)]
F['ob_fold_tot'] = [sum(F['ob_fold'][i]) for i in range(NSRC)]
F['ob_tag_tot'] = [sum(F['ob_tag'][i]) for i in range(NSRC)]
F['ob_lower'] = [[ub_tab(FOLDX[i], OBL[k], _tabs_x[i], u'alpha') for k in range(len(OB))]
                 for i in range(NSRC)]
F['ob_upper_tot'] = [sum(F['ob_sh'][i]) for i in range(NSRC)]
F['ob_lower_tot'] = [sum(F['ob_lower'][i]) for i in range(NSRC)]


def _bnd_word(s, a, b):
    """词界形状(与采集侧 \\b 同义, 但这里是逐字符查表而非正则): 两侧都不是字母数字下划线。"""
    return not (a >= 0 and (s[a].isalnum() or s[a] == u'_')) \
        and not (b < len(s) and (s[b].isalnum() or s[b] == u'_'))


def kw_union(s, heads):
    """并集尺: 三枚词头各扫一遍游标环, 短语里的 MUST 只归一处(采集侧是一条选择支正则)。"""
    return sum([sum([1 for j in _occ(s, h) if _bnd_word(s, j - 1, j + len(h))]) for h in heads])


def _occ(s, w):
    out, i = [], 0
    while True:
        j = s.find(w, i)
        if j < 0:
            return out
        out.append(j)
        i = j + 1


HEADS = [u'MUST', u'SHOULD', u'MAY']
HEADSL = [u'must', u'should', u'may']
LOWT = [t.lower() for t in T]
FOLDX_LOW = [x.lower() for x in FOLDX]
F['kw_allcaps'] = [kw_union(T[i], HEADS) for i in range(NSRC)]
F['kw_ci'] = [kw_union(LOWT[i], HEADSL) for i in range(NSRC)]
F['kw_lowercase'] = [F['kw_ci'][i] - F['kw_allcaps'][i] for i in range(NSRC)]
F['kw_union_fold'] = [kw_union(FOLDX[i], HEADS) for i in range(NSRC)]
F['kw_union_fold_low'] = [kw_union(FOLDX_LOW[i], HEADSL) for i in range(NSRC)]
F['ob_nest_ledger'] = [F['ob_fold_tot'][i] - F['kw_union_fold'][i] - F['ob_fold'][i][1] - F['ob_fold'][i][3]
                       for i in range(NSRC)]
F['tag_paren'] = [len(re.findall(u'\\((MUST|SHOULD|MAY|SHLD|ED) \\d+\\)', T[i])) for i in range(NSRC)]
F['tag_dash'] = [len(re.findall(u'\\b(MUST|SHOULD|MAY|SHLD|ED)-\\d+\\b', T[i])) for i in range(NSRC)]
TAGKIND = [u'MUST', u'SHOULD', u'MAY', u'SHLD', u'ED']
F['tag_kind'] = [[len(re.findall(u'\\b%s-[0-9]+\\b' % w, T[i])) for w in TAGKIND] for i in range(NSRC)]
F['tag_max_no'] = [max([int(x) for x in re.findall(u'\\b(?:MUST|SHOULD|MAY|SHLD|ED)-([0-9]+)\\b', T[i])] or [0])
                   for i in range(NSRC)]
F['tag_chars'] = [len(SHP[i]) - len(SHTAG[i]) for i in range(NSRC)]
F['tag_in_paren'] = [len(re.findall(u'\\((MUST|SHOULD|MAY|SHLD|ED)-[0-9]+\\)', T[i])) for i in range(NSRC)]
F['tag_bare'] = [len(re.findall(u'(?<!\\()(MUST|SHOULD|MAY|SHLD|ED)-[0-9]+(?=[\\s).,;])', T[i]))
                 for i in range(NSRC)]
TAGSHAPE = re.compile(u'^(MUST|SHOULD|MAY|SHLD|ED)-[0-9]+$')


def tag_token_scan(s):
    """第三把编号尺: 按空白切成 token 再剥圈点判形(整篇正则尺之外的那些读不到)。"""
    n, par, bare = 0, 0, 0
    for w in s.split():
        k = w.strip(u'().,;:')
        if TAGSHAPE.match(k):
            n += 1
            if w.startswith(u'(') and w.endswith(u')'):
                par += 1
            else:
                bare += 1
    return n, par, bare


TT = [tag_token_scan(T[i]) for i in range(NSRC)]
F['tag_token'] = [x[0] for x in TT]
F['tag_token_paren'] = [x[1] for x in TT]
F['tag_token_plain'] = [x[2] for x in TT]
F['tag_form_ledger'] = [F['tag_in_paren'][i] + F['tag_bare'][i] - F['tag_dash'][i] for i in range(NSRC)]
F['tag_token_ledger'] = [F['tag_token'][i] - F['tag_dash'][i] for i in range(NSRC)]
# 逐枚分类: 左邻是 '(' 却没在同处等到 ')' 的编号 = 被硬换行切开的那一枚
F['tag_split_manual'] = []
for i in range(NSRC):
    c = 0
    for h in [u'MUST-', u'SHOULD-', u'MAY-', u'SHLD-', u'ED-']:
        for j in _occ(T[i], h):
            k = j + len(h)
            while k < len(T[i]) and T[i][k].isdigit():
                k += 1
            if not _bnd_word(T[i], j - 1, k):
                continue
            if T[i][j - 1:j] == u'(' and T[i][k:k + 1] != u')':
                c += 1
    F['tag_split_manual'].append(c)
F['tag_kind_ledger'] = [sum(F['tag_kind'][i]) - F['tag_dash'][i] for i in range(NSRC)]
# 两枚“形状”各自另数一遍: 括号被破折号拉开的那一枚 ⇎ 数字被硬换行推到下一行的那几枚
F['tag_paren_apart'] = []
F['tag_num_nextline'] = []
F['tag_bracket'] = []
F['tag_apart_ctx'] = []
for i in range(NSRC):
    ap, nx, br = 0, 0, 0
    for h in [u'MUST-', u'SHOULD-', u'MAY-', u'SHLD-', u'ED-']:
        for j in _occ(T[i], h):
            k = j + len(h)
            while k < len(T[i]) and T[i][k].isdigit():
                k += 1
            if not _bnd_word(T[i], j - 1, k):
                continue
            if k == j + len(h):
                m = k
                while m < len(T[i]) and T[i][m] in u' \t\n':
                    m += 1
                if m > k and T[i][m].isdigit():
                    nx += 1
                continue
            if T[i][j - 1:j] == u'(' and T[i][k:k + 1] != u')':
                ap += 1
                F['tag_apart_ctx'].append([LBL[i], repr(T[i][j - 2:k + 4])])
            if T[i][j - 2:j - 1] == u'[':
                br += 1
    F['tag_paren_apart'].append(ap)
    F['tag_num_nextline'].append(nx)
    F['tag_bracket'].append(br)
F['tag_split_ledger'] = [F['tag_dash'][i] - (F['tag_in_paren'][i] + F['tag_bare'][i])
                         - F['tag_paren_apart'][i] for i in range(NSRC)]
F['tag_bracket_ledger'] = [F['tag_dash'][i] - F['tag_token'][i] - F['tag_bracket'][i]
                           for i in range(NSRC)]
F['tag_dash_fold'] = [len(re.findall(u'\\b(?:MUST|SHOULD|MAY|SHLD|ED)-[0-9]+\\b', FOLDX[i]))
                      for i in range(NSRC)]
F['tag_fold_gain'] = [F['tag_dash_fold'][i] - F['tag_dash'][i] for i in range(NSRC)]
# 词头与数字之间隔着一段空白(硬换行)的那些: 折平只是把空白压成一枚空格, 所以折平面仍读不到
NOSPC = [re.sub(u'\\s', u'', T[i]) for i in range(NSRC)]
F['tag_nospace'] = [len(re.findall(u'(?<![A-Z0-9])(?:MUST|SHOULD|MAY|SHLD|ED)-[0-9]+', NOSPC[i]))
                    for i in range(NSRC)]
F['tag_nextline_ledger'] = [F['tag_nospace'][i] - F['tag_dash'][i] - F['tag_num_nextline'][i]
                            for i in range(NSRC)]
F['labeled_decl'] = [cnt_re(FOL[i], u'individually labeled') for i in range(NSRC)]
print(u'2 义务词 行/折/壳/壳去编号:', F['ob_line'], F['ob_fold'], F['ob_sh'], F['ob_tag'])
print(u'  大写合计', F['ob_upper_tot'], u' 小写合计', F['ob_lower_tot'], u' 并集大写', F['kw_allcaps'],
      u' 并集小写', F['kw_lowercase'], u' 嵌套账', F['ob_nest_ledger'])
print(u'  编号', F['tag_dash'], u' 括号/裸形', F['tag_in_paren'], F['tag_bare'], u' 两形状账',
      F['tag_form_ledger'], u' token尺', F['tag_token'], u' token账', F['tag_token_ledger'],
      u' 换行切开', F['tag_split_manual'], u' 括号拉开', F['tag_paren_apart'],
      u' 数字推到下一行', F['tag_num_nextline'], u' 折平编号', F['tag_dash_fold'],
      u' 无空白编号', F['tag_nospace'],
      u' 套括', F['tag_bracket'], u' 两形状新账', F['tag_split_ledger'], u' 套括账', F['tag_bracket_ledger'],
      u' 按词种', F['tag_kind'], u' 最大号', F['tag_max_no'],
      u' 编号吃掉字符', F['tag_chars'])

# ---------- 3. 说法与拼写族(子串尺 ⇎ 整词尺) ----------
GRP = [u'retransmission', u'retransmissions', u'retransmit', u'retransmitted', u'retransmits',
       u'time units', u'count of retransmissions', u'threshold', u'excessive retransmissions',
       u'at least', u'before killing', u'time out', u'timeout', u'time-out', u'give up',
       u'abort', u'five minutes', u'3 minutes', u'100 seconds', u'60 seconds', u'924.6',
       u'tcp_retries1', u'tcp_retries2', u'tcp_syn_retries', u'tcp_synack_retries',
       u'tcp_orphan_retries', u'association_max_retrans', u'path_max_retrans', u'pf_retrans',
       u'max_init_retransmits', u'TCP_RTO_MIN', u'N times', u'(N+1)th', u'Default']
F['spell'] = [[cnt_re(FOL[i], pnorm(p)) for p in GRP] for i in range(NSRC)]
F['spell_word'] = [[ub_tab(FOL[i], pnorm(p), _tabs_all[i]) for p in GRP] for i in range(NSRC)]
F['spell_diff'] = [F['spell'][i][k] - F['spell_word'][i][k] for i in range(NSRC) for k in range(len(GRP))]
F['spell_tot'] = [sum(F['spell'][i]) for i in range(NSRC)]
F['spell_word_tot'] = [sum(F['spell_word'][i]) for i in range(NSRC)]
F['spell_vari'] = [len([1 for k in range(len(GRP)) if F['spell'][i][k] > 0]) for i in range(NSRC)]
F['spell_excl'] = [[p for k, p in enumerate(GRP)
                    if F['spell'][i][k] > 0 and all(F['spell'][j][k] == 0 for j in range(NSRC) if j != i)]
                   for i in range(NSRC)]
F['excl_n'] = sum([len(x) for x in F['spell_excl']])
F['spell_cold'] = [p for k, p in enumerate(GRP) if all(F['spell'][i][k] == 0 for i in range(NSRC))]
F['tcp_will'] = [cnt_re(FOL[i], u'the tcp will') for i in range(NSRC)]
F['tcp_endpoint_will'] = [cnt_re(FOL[i], u'the tcp endpoint will') for i in range(NSRC)]
print(u'3 语形族总量', F['spell_tot'], u' 式种数', F['spell_vari'], u' 全冷式', F['spell_cold'])
print(u'  子串−整词 差合计', sum(F['spell_diff']), u' the TCP will', F['tcp_will'],
      u' the TCP endpoint will', F['tcp_endpoint_will'])
for k, p in enumerate(GRP):
    print(u'   %-26s %s' % (p, [F['spell'][i][k] for i in range(NSRC)]))

# ---------- 4. 次数尺 ⇎ 时间尺 ⇎ 数字与单位的粘连 ----------
UNIT = [u'milliseconds', u'microseconds', u'seconds', u'ms']


def num_pairs(text, units):
    """本遍轨: 手工扫数字串, 就地读紧随其后的单位词, 并记下中间空格数(采集侧是一条选择支正则)。"""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if not c.isdigit() or (i > 0 and (text[i - 1].isalnum() or text[i - 1] == u'.')):
            i += 1
            continue
        j, sep = i, 0
        while j < n and (text[j].isdigit()
                         or (sep == 0 and text[j] in u'.,' and j + 1 < n and text[j + 1].isdigit())):
            if text[j] in u'.,':
                sep = 1
            j += 1
        k, gap = j, 0
        while k < n and text[k] == u' ':
            k += 1
            gap += 1
        for u_ in sorted(units, key=len, reverse=True):
            if text.startswith(u_, k) and (k + len(u_) >= n or not text[k + len(u_)].isalpha()):
                if gap <= 1:
                    out.append((text[i:j], u_, gap))
                break
        i = j
    return out


def np2(lst):
    return sorted(set([(a, b) for a, b, _ in lst]))


UNIT = [u'milliseconds', u'microseconds', u'seconds', u'ms']
UNITS = UNIT + [u's']
GLUE = UNIT + [u'second', u'hours', u'hour', u'minutes', u'minute', u'msec', u'usec', u'sec']
F0 = [np2(num_pairs(T[i], UNITS)) for i in range(NSRC)]
FU = [np2(num_pairs(FOLDX[i], UNIT)) for i in range(NSRC)]
FW = [np2(num_pairs(FOLDX[i], UNITS)) for i in range(NSRC)]
F['numunit'] = [[list(z) for z in FU[i]] for i in range(NSRC)]
F['numunit_wide'] = [[list(z) for z in FW[i]] for i in range(NSRC)]
F['numunit_raw'] = [[list(z) for z in F0[i]] for i in range(NSRC)]
F['numval_n'] = [len(FU[i]) for i in range(NSRC)]
F['numval_wide_n'] = [len(FW[i]) for i in range(NSRC)]
F['numval_extra'] = [sorted(set(FW[i]) - set(FU[i])) for i in range(NSRC)]
F['numunit_wrap'] = [sorted(set(FW[i]) - set(F0[i])) for i in range(NSRC)]
# 数字与单位之间零空格(内核文档那一代的手打痕迹): 尺在原面逐行上, 不经折平(折平会把硬换行也粘起来)
F['glued_rows'] = [num_pairs(T[i], GLUE) for i in range(NSRC)]
F['glued_all'] = [[a + b for a, b, gp in F['glued_rows'][i] if gp == 0] for i in range(NSRC)]
F['glued_n'] = [len(F['glued_all'][i]) for i in range(NSRC)]
F['glued_vari'] = [len(set(F['glued_all'][i])) for i in range(NSRC)]
F['spaced_n'] = [len([1 for a, b, gp in F['glued_rows'][i] if gp == 1]) for i in range(NSRC)]
RXN = re.compile(u'(?<![A-Za-z0-9])(\\d+|N)(?:[ ]?(?:retransmissions|times|tries))\\b')
F['numtimes'] = [[list(z) for z in sorted(set(RXN.findall(FOL[i])))] for i in range(NSRC)]
DUR = [u'five minutes', u'3 minutes', u'100 seconds', u'60 seconds', u'924.6 seconds', u'1second',
       u'63seconds', u'127seconds', u'31seconds', u'two hours']
F['dur'] = [[cnt_re(FOL[i], d) for d in DUR] for i in range(NSRC)]
print(u'4 数值项 严', F['numval_n'], u' 宽', F['numval_wide_n'], u' 宽多出', F['numval_extra'],
      u' 粘连枚', F['glued_n'], u' 去重', F['glued_vari'], u' 带空格', F['spaced_n'])
print(u'  粘连样本', F['glued_all'], u' 只折面读得到', F['numunit_wrap'])
print(u'  次数式', F['numtimes'])

# ---------- 5. 判词针四档 ----------
NEEDLES = [
    u'send the segment at the front of the retransmission queue again',
    u'reinitialize the retransmission timer, and return',
    u'There are two thresholds R1 and R2 measuring the amount of retransmission',
    u'R1 and R2 might be measured in time units or as a count of retransmissions',
    u'pass negative advice',
    u'to trigger dead-gateway diagnosis',
    u'close the connection',
    u'An application MUST be able to set the value for R2',
    u'set R2 to "infinity"',
    u'The value of R1 SHOULD correspond to at least 3 retransmissions, at the current RTO',
    u'The value of R2 SHOULD correspond to at least 100 seconds',
    u'SYN retransmissions MUST be handled in the general way',
    u'R2 for a SYN segment MUST be set large enough',
    u'for at least 3 minutes',
    u'give up on the open attempt',
    u'A maximum value MAY be placed on RTO provided it is at least 60 seconds',
    u'The present global default is five minutes',
    u'would retransmit N times before killing the connection at the (N+1)th RTO',
    u'The default value of 15 yields a hypothetical timeout of 924.6 seconds',
    u'RFC 1122 recommends at least 100 seconds for the timeout, which corresponds to a value of at least 8',
    u'RFC 1122 recommends at least 3 retransmissions, which is the default',
    u'corresponds to 63seconds till the last retransmission',
    u'happen after 127seconds',
    u'corresponds to 31seconds till the last retransmission',
    u'happen after 63seconds',
    u'with the current initial RTO of 1second',
    u'If this value is exceeded, the association is terminated',
    u'The maximum number of retransmissions that will be attempted on a given path',
]
F['needle_n'] = len(NEEDLES)
NK = [pnorm(z) for z in NEEDLES]
ROWSN = [[(k, pnorm(x)) for k, x in enumerate(L[i])] for i in range(NSRC)]
F['role_line'] = [[len([1 for _, y in ROWSN[i] if NK[k] in y]) for i in range(NSRC)]
                  for k in range(len(NK))]
F['role_fold'] = [[cnt_re(FOL[i], NK[k]) for i in range(NSRC)] for k in range(len(NK))]
F['role_sh'] = [[cnt_re(SHP[i], NK[k]) for i in range(NSRC)] for k in range(len(NK))]
F['role_tag'] = [[cnt_re(SHTAG[i], NK[k]) for i in range(NSRC)] for k in range(len(NK))]
F['role_line_n'] = [sum(F['role_line'][k][i] for k in range(len(NK))) for i in range(NSRC)]
F['role_fold_n'] = [sum(F['role_fold'][k][i] for k in range(len(NK))) for i in range(NSRC)]
F['role_sh_n'] = [sum(F['role_sh'][k][i] for k in range(len(NK))) for i in range(NSRC)]
F['role_tag_n'] = [sum(F['role_tag'][k][i] for k in range(len(NK))) for i in range(NSRC)]
F['role_gain'] = [[F['role_fold_n'][i] - F['role_line_n'][i], F['role_sh_n'][i] - F['role_fold_n'][i],
                   F['role_tag_n'][i] - F['role_sh_n'][i]] for i in range(NSRC)]
F['role_src'] = [[LBL[i] for i in range(NSRC) if F['role_sh'][k][i] > 0] for k in range(len(NK))]
F['role_probes'] = F['needle_n'] * NSRC
F['wrap_cut'] = [k for k in range(len(NK)) if F['role_sh'][k] != [0] * NSRC
                 and any(F['role_line'][k][i] < F['role_sh'][k][i] for i in range(NSRC))]
F['wrap_cut_n'] = len(F['wrap_cut'])
F['shell_cut'] = [k for k in range(len(NK)) if k not in F['wrap_cut']
                  and any(F['role_fold'][k][i] > F['role_sh'][k][i] for i in range(NSRC))]
F['tag_cut'] = [k for k in range(len(NK)) if any(F['role_tag'][k][i] != F['role_sh'][k][i] for i in range(NSRC))]
F['wrap_gain_cells'] = [F['role_fold'][k][i] - F['role_line'][k][i]
                        for k in range(len(NK)) for i in range(NSRC)]
F['tag_drop_cells'] = [max(0, F['role_sh'][k][i] - F['role_tag'][k][i])
                       for k in range(len(NK)) for i in range(NSRC)]
F['tag_gain_cells'] = [max(0, F['role_tag'][k][i] - F['role_sh'][k][i])
                       for k in range(len(NK)) for i in range(NSRC)]
F['tag_move'] = [[k, LBL[i], F['role_sh'][k][i], F['role_tag'][k][i]]
                 for k in range(len(NK)) for i in range(NSRC)
                 if F['role_sh'][k][i] != F['role_tag'][k][i]]
F['tag_gain_needles'] = [k for k in range(len(NK))
                         if any(F['role_tag'][k][i] > F['role_sh'][k][i] for i in range(NSRC))]
F['tag_drop_needles'] = [k for k in range(len(NK))
                         if any(F['role_tag'][k][i] < F['role_sh'][k][i] for i in range(NSRC))]
F['tag_drop'] = [F['role_sh_n'][i] - F['role_tag_n'][i] for i in range(NSRC)]
F['tag_gain'] = [F['role_tag_n'][i] - F['role_sh_n'][i] for i in range(NSRC)]
F['wrap_gain'] = [sum(F['role_fold'][k][i] - F['role_line'][k][i] for k in range(len(NK)))
                  for i in range(NSRC)]
F['wrap_gain_tot'] = sum(F['wrap_gain'])
F['tag_gain_tot'] = sum(F['role_tag_n'][i] - F['role_sh_n'][i] for i in range(NSRC))
print(u'5 判词针四档合计', F['role_line_n'], F['role_fold_n'], F['role_sh_n'], F['role_tag_n'],
      u' 逐档增益', F['role_gain'])
print(u'  换行切开 %d 枚 %s ⇎ 壳切 %d ⇎ 编号切 %d' % (
      F['wrap_cut_n'], [NEEDLES[k][:34] for k in F['wrap_cut']], len(F['shell_cut']), len(F['tag_cut'])))
print(u'  去编号挪动 %s ⇎ 涨格 %s ⇎ 跌格 %s' % (
      json.dumps(F['tag_move'], ensure_ascii=False), sum(F['tag_gain_cells']), sum(F['tag_drop_cells'])))

# ---------- 6. 五份答句(逐字符句界) ----------
ANSK = [u'send the segment at the front of the retransmission queue again',
        u'a threshold R2 greater than R1, close the connection',
        u'set R2 to "infinity"',
        u'A maximum value MAY be placed on RTO provided it is at least 60 seconds',
        u'would retransmit N times before killing the connection']
CUM = []
for i in range(NSRC):
    acc, a = [], 0
    for x in L[i]:
        a += len(x) + 1
        acc.append(a)
    CUM.append(acc)


def cum_line(i, off):
    """本遍行号尺: 累积长度表 + bisect(采集侧是 4 行滑窗)。"""
    import bisect
    return bisect.bisect_right(CUM[i], off)


def face_of(i):
    """摘壳折平面 + (面偏移 → 原行) 表, 由累积长度现导。"""
    seg, offs, pos = [], [], 0
    for k, x in enumerate(L[i]):
        if shell_shape(x):
            continue
        c = pnorm(x)
        if not c:
            continue
        offs.append((pos, pos + len(c), k))
        seg.append(c)
        pos += len(c) + 1
    return u' '.join(seg), offs


FACE, OFFS = zip(*[face_of(i) for i in range(NSRC)])
FACE = list(FACE)
OFFS = list(OFFS)


def off_line(i, s0):
    lo, hi = 0, len(OFFS[i]) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if OFFS[i][mid][0] <= s0:
            lo = mid
        else:
            hi = mid - 1
    return OFFS[i][lo][2] if OFFS[i] else -1


F['ans_needle'] = ANSK
F['ans_line'] = []
F['ans_sent'] = []
F['ans_words'] = []
F['ans_chars'] = []
F['ans_sent_span'] = []
F['ans_needle_line'] = []
F['ans_sent_line'] = []
F['ans_sent_end'] = []
F['ans_ob'] = []
F['ans_tag_n'] = []
F['ans_shell_rows'] = []
F['ans_page_rows'] = []
F['na_in_ans'] = []
F['shpx_eq_pnorm'] = 1 if [pnorm(x) for x in SHPX] == SHP else 0
PAGESH = [sh_foot, sh_hdr793, sh_hdr1122, sh_ietf, sh_hdrnew]
for i in range(NSRC):
    q = pnorm(ANSK[i])
    s0 = FACE[i].find(q)
    assert s0 >= 0, (LBL[i], ANSK[i])
    a, b = sent_at(sent_cuts(SHPX[i]), s0)
    sent = SHPX[i][a:b]
    ln = off_line(i, s0)
    la, lb = off_line(i, a), off_line(i, b - 1)
    F['ans_line'].append(ln)
    F['ans_sent'].append(sent)
    F['ans_words'].append(len(sent.split()))
    F['ans_chars'].append(len(sent))
    F['ans_sent_line'].append(la)
    F['ans_sent_end'].append(lb)
    F['ans_sent_span'].append(lb - la + 1)
    F['ans_needle_line'].append(len([1 for x in L[i] if q in pnorm(x)]))
    F['ans_shell_rows'].append(len([k for k in range(la, lb + 1) if shell_shape(L[i][k])]))
    F['ans_page_rows'].append(len([k for k in range(la, lb + 1)
                                   if any(f(L[i][k]) for f in PAGESH)]))
    F['ans_ob'].append([ub_tab(sent, w, _tabs(sent), u'alpha') for w in OB])
    F['ans_tag_n'].append(len(re.findall(u'\\b(?:MUST|SHOULD|MAY|SHLD|ED)-\\d+\\b', sent)))
    F['na_in_ans'].append(len([c for c in sent if ord(c) > 127]))
print(u'6 答句:', json.dumps([[LBL[i], F['ans_words'][i], F['ans_chars'][i], F['ans_sent_span'][i],
                               F['ans_sent_line'][i], F['ans_tag_n'][i]] for i in range(NSRC)], ensure_ascii=False))
print(u'  行内读得到', F['ans_needle_line'], u' 跨页壳行', F['ans_shell_rows'],
      u' 其中页码页眉', F['ans_page_rows'], u' 保形面同小写面', F['shpx_eq_pnorm'])
for i in range(NSRC):
    print(u'   %s %r' % (LBL[i], F['ans_sent'][i][:110]))

# ---------- 7. 1122 ⇎ 9293 段落逐句对照 ⇎ 793 ⇎ 9293 事件表重印 ----------
TAGRE = re.compile(u' \\((?:MUST|SHOULD|MAY|SHLD|ED)-\\d+\\)', re.I)


def sents(lines):
    return [pnorm(z) for z in re.split(u'(?<=[.!?]) +', pnorm(NL.join(lines))) if z]


def sents_char(face):
    """本遍轨: 逐字符扫“句末标点+空格”切段(采集侧是一条 re.split)。"""
    return [pnorm(face[a:b].strip()) for a, b in sent_cuts(face)]


def canon(z):
    return (z.replace(u'implementers', u'implementors').replace(u'acknowledgment', u'acknowledgement')
            .replace(u'endpoint', u'site'))


def lfind(i, nd, frm=0):
    q = pnorm(nd)[:16]
    for k in range(frm, len(L[i])):
        if q in pnorm(NL.join(L[i][k:k + 4])):
            face, offs = face_of_win(i, k)
            s0 = face.find(pnorm(nd))
            if s0 >= 0:
                return k + (offs[bisect_idx(offs, s0)][2] if offs else 0)
    return -1


def bisect_idx(offs, s0):
    lo, hi = 0, len(offs) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if offs[mid][0] <= s0:
            lo = mid
        else:
            hi = mid - 1
    return lo


def face_of_win(i, k):
    seg, offs, pos = [], [], 0
    for m in range(k, min(k + 4, len(L[i]))):
        c = pnorm(L[i][m])
        if not c:
            continue
        offs.append((pos, pos + len(c), m - k))
        seg.append(c)
        pos += len(c) + 1
    return u' '.join(seg), offs


S1 = [lfind(1, u'The following procedure MUST be used to handle excessive')]
E1 = [lfind(1, u'give up on the open attempt) sooner, of course')]
S2 = [lfind(2, u'The following procedure MUST be used to handle excessive')]
E2 = [lfind(2, u'give up on the open attempt) sooner, of course')]
assert min(S1 + E1 + S2 + E2) >= 0, u'段落端点未找到'
BL1 = L[1][S1[0]:E1[0] + 1]
BL2 = L[2][S2[0]:E2[0] + 1]


def cut_at(lines, stop):
    for k, x in enumerate(lines):
        if pnorm(stop) in pnorm(x):
            return lines[:k]
    return lines


BL1 = cut_at(BL1, u'4.2.3.6')
BL2 = cut_at(BL2, u'3.8.4.')
F['ovl_rows'] = [len(BL1), len(BL2)]
F['ovl_shell'] = [len([x for x in BL1 if shell_shape(x)]), len([x for x in BL2 if shell_shape(x)])]
s1, s2 = sents(BL1), sents(BL2)
s1c, s2c2 = sents_char(pnorm(NL.join(BL1))), sents_char(pnorm(NL.join(BL2)))
s2c = [TAGRE.sub(u'', z).strip() for z in s2]
F['ovl_s1'], F['ovl_s2'] = len(s1), len(s2)
F['ovl_s1_char'], F['ovl_s2_char'] = len(s1c), len(s2c2)
F['ovl_splitter_diff'] = abs(F['ovl_s1'] - F['ovl_s1_char']) + abs(F['ovl_s2'] - F['ovl_s2_char'])
F['ovl_splitter_list'] = 1 if (s1 == s1c and s2 == s2c2) else 0
F['ovl_same_raw'] = len([z for z in s2 if z in s1])
F['ovl_same_tag'] = len([z for z in s2c if z in s1])
F['ovl_same_canon'] = len([z for z in s2c if canon(z) in [canon(y) for y in s1]])
F['ovl_new'] = F['ovl_s2'] - F['ovl_same_tag']
import difflib
WA = [pnorm(w) for w in NL.join(BL1).split()]
WB = [pnorm(w) for w in NL.join(BL2).split()]
F['blk_words'] = [len(WA), len(WB)]
sm = difflib.SequenceMatcher(None, WA, WB, autojunk=False)
BLKS = sm.get_matching_blocks()
OPS = sm.get_opcodes()
F['blk_equal_runs'] = len([z for z in BLKS if z.size])
F['blk_equal_words'] = sum([z.size for z in BLKS])
F['blk_longest'] = max([z.size for z in BLKS])
F['blk_replace'] = len([op for op in OPS if op[0] == u'replace'])
F['blk_op_equal'] = sum([z[2] - z[1] for z in OPS if z[0] == u'equal'])
F['blk_op_delete'] = sum([z[2] - z[1] for z in OPS if z[0] == u'delete'])
F['blk_op_insert'] = sum([z[4] - z[3] for z in OPS if z[0] == u'insert'])
F['blk_op_rep_a'] = sum([z[2] - z[1] for z in OPS if z[0] == u'replace'])
F['blk_op_rep_b'] = sum([z[4] - z[3] for z in OPS if z[0] == u'replace'])
F['blk_op_n'] = len(OPS)
OSH = difflib.SequenceMatcher(None, WA, WB, autojunk=True)
F['blk_autojunk_diff'] = sum([z.size for z in OSH.get_matching_blocks()]) - F['blk_equal_words']
F['blk_drop_words'] = F['blk_words'][0] - F['blk_equal_words']
F['blk_insert_words'] = F['blk_words'][1] - F['blk_equal_words']
F['blk_form_ledger'] = [F['blk_equal_words'] - F['blk_op_equal'],
                        F['blk_words'][0] - (F['blk_op_equal'] + F['blk_op_delete'] + F['blk_op_rep_a']),
                        F['blk_words'][1] - (F['blk_op_equal'] + F['blk_op_insert'] + F['blk_op_rep_b'])]
F['blk_chars'] = [len(pnorm(NL.join(BL1))), len(pnorm(NL.join(BL2)))]
F['blk_tag_chars'] = F['blk_chars'][1] - len(tag_strip(pnorm(NL.join(BL2))))
F['blk_tag_n'] = len(re.findall(u'\\b(?:MUST|SHOULD|MAY|SHLD|ED)-[0-9]+\\b', NL.join(BL2)))
F['blk_is_substring'] = 1 if pnorm(NL.join(BL2)) in pnorm(NL.join(BL1)) else 0
# 793 的事件表条目 ⇎ 9293 重印: 同一段落在两份面上的形状差
EV = u'send the segment at the front of the retransmission queue again'
F['ev_same'] = [1 if pnorm(EV) in FOL[i] else 0 for i in range(NSRC)]
F['ev_n'] = [cnt_re(FOL[i], pnorm(EV)) for i in range(NSRC)]
OX1 = [cnt_re(FOL[0], u'closed state and return'), cnt_re(FOL[2], u'closed state and return')]
OX2 = [cnt_re(FOL[0], u'closed state, and return'), cnt_re(FOL[2], u'closed state, and return')]
F['oxford_old'] = OX1
F['oxford_new'] = OX2
print(u'7 段落 %d⇎%d 行 ⇎ 句 %d⇎%d ⇎ 逐字同 %d ⇎ 去编号同 %d ⇎ 归拼同 %d ⇎ 新句 %d' % (
      F['ovl_rows'][0], F['ovl_rows'][1], F['ovl_s1'], F['ovl_s2'], F['ovl_same_raw'],
      F['ovl_same_tag'], F['ovl_same_canon'], F['ovl_new']))
print(u'  词对齐 相同 %d 词/%d 段 最长 %d ⇎ 删 %d ⇎ 插 %d ⇎ 替换 %d ⇎ 块内编号 %d 枚吃 %d 字符' % (
      F['blk_equal_words'], F['blk_equal_runs'], F['blk_longest'], F['blk_drop_words'], F['blk_insert_words'],
      F['blk_replace'], F['blk_tag_n'], F['blk_tag_chars']))
print(u'  793/9293 事件表同句 %s ⇎ 逗号改动 793 %s/%s 9293 %s/%s' % (F['ev_n'], OX1, OX2, '', ''))

# ---------- 8. 内核键值表: 四句式级联 ----------
KEYRE = re.compile(u'^([a-z_][a-z_0-9]*) - (INTEGER|BOOLEAN|STRING|DWORD)\\s*$')
KEYS = []
BODY = {}
cur = None
for x in L[4]:
    m = KEYRE.match(x)
    if m:
        cur = m.group(1)
        KEYS.append(cur)
        BODY[cur] = []
    elif cur is not None:
        BODY[cur].append(x)
REL = [k for k in KEYS if re.search(u'retrans|retries|retry|rto|timeout', k)]
REL2 = [k for k in REL if any(pnorm(w) in pnorm(u' '.join(BODY[k]))
                              for w in [u'retransmission', u'retransmit', u'timeout', u'attempts'])]
PKSUB = [u'retr', u'retry', u'timeout', u'_rto', u'rto_']
RELP = sorted(set([k for k in KEYS if any(s in k for s in PKSUB)]))
RELX = sorted(set(REL2))
UNIV = sorted(set(RELP) | set(REL2))
TAIL = u'retransmissions, which is the default'
F['lin_keys_total'] = len(KEYS)
F['lin_keys_uniq'] = len(set(KEYS))
F['lin_key_dup_names'] = sorted(set([k for k in KEYS if KEYS.count(k) > 1]))
F['lin_key_dup_ledger'] = F['lin_keys_total'] - F['lin_keys_uniq'] - len(F['lin_key_dup_names'])
F['lin_rel_pick_names'] = RELP
F['lin_rel_keys'] = len(RELX)
F['lin_rel_names'] = RELX
F['lin_rel_dropped'] = sorted(set(REL) - set(REL2))
F['lin_body_lines'] = sum([len(BODY[k]) for k in RELX])
F['lin_default_lines'] = F['default_lines'][4]
WS = u' \t\x0b\x0c'


def _tok_at(s, at, stop):
    while at < len(s) and s[at] in WS:
        at += 1
    j = at
    while j < len(s) and s[j] not in stop:
        j += 1
    return (s[at:j] if j > at else None)


def _after_kw(s, kw, stop):
    for j in _occ(s, kw):
        v = _tok_at(s, j + len(kw), stop)
        if v:
            return v
    return None


def _borrow(s):
    """第四式: “at least N … retransmissions, which is the default” 里借来的那个 N。"""
    for j in _occ(s, u'at least '):
        k, d = j + 9, j + 9
        while d < len(s) and s[d].isdigit():
            d += 1
        if d == k:
            continue
        t = s.find(TAIL, d)
        if t < 0:
            continue
        if all(s[x].isalpha() or s[x] == u' ' for x in range(d, t)):
            return s[k:d]
    return None


def defval(s):
    """四句式级联: Default: ⇎ default value is ⇎ default value of ⇎ 借参考句; 命中即停。"""
    sl = s.lower()
    v = _after_kw(sl, u'default:', u' .,;)')
    if v:
        return (v, u'Default:')
    for kw, sh in [(u'default value is', u'default value is'), (u'default value of', u'default value of')]:
        v = _after_kw(sl, kw + u' ', WS)
        if v:
            return (v, sh)
    v = _borrow(sl)
    if v:
        return (v, u'借参考句')
    return (None, u'无')


def defval_lines(lines):
    """同一级联, 但一次只给一行(硬换行把句式切成两半时这一档就读不到)。"""
    for x in lines:
        v, sh = defval(x)
        if v:
            return (v, sh)
    return (None, u'无')


DVP = dict((k, defval(u' '.join(u' '.join(BODY[k]).split()))) for k in UNIV)
DVL = dict((k, defval_lines(BODY[k])) for k in UNIV)
DVS = dict((k, defval(NL.join(BODY[k]))) for k in UNIV)
DV = dict((k, DVP[k]) for k in RELX)
F['lin_rel_union'] = len(UNIV)
F['lin_rel_both'] = len(sorted(set(RELP) & set(RELX)))
F['lin_defaults_pick'] = dict((k, DVP[k][0]) for k in RELP)
F['lin_shape_pick'] = dict((k, DVP[k][1]) for k in RELP)
F['lin_defaults_line'] = dict((k, DVL[k][0]) for k in UNIV)
F['lin_defaults_raw'] = dict((k, DVP[k][0]) for k in RELX)
F['lin_defaults'] = dict((k, (DV[k][0] or u'').rstrip(u'.,;')) for k in RELX)
F['lin_val_punct'] = len([k for k in UNIV if DVP[k][0] is not None
                          and DVP[k][0] != DVP[k][0].rstrip(u'.,;')])
F['lin_wrap_gain'] = sorted([k for k in UNIV if DVP[k][0] and not DVL[k][0]])
F['lin_split_gain'] = sorted([k for k in UNIV if DVP[k][0] and not DVS[k][0]])
F['lin_shape'] = dict((k, DV[k][1]) for k in RELX)
F['lin_shape_n'] = [len([k for k in RELX if DV[k][1] == s])
                    for s in [u'Default:', u'default value is', u'default value of', u'借参考句', u'无']]
F['lin_dv_none'] = len([k for k in RELX if DV[k][0] is None])
F['lin_numvals'] = sorted(set([v for v in F['lin_defaults'].values() if v is not None and re.match(u'^[0-9]+$', v)]))
F['lin_hexvals'] = [v for v in F['lin_defaults_pick'].values() if v is not None and u'x' in v]
F['lin_default_str'] = F['lin_defaults'].get(u'tcp_retries1'), F['lin_defaults'].get(u'tcp_retries2'), \
    F['lin_defaults'].get(u'tcp_syn_retries'), F['lin_defaults'].get(u'tcp_synack_retries')
print(u'8 内核: 键行 %d ⇎ 去重 %d ⇎ 重名 %s ⇎ 名尺 %d ⇎ 相关(本遍) %d ⇎ 落选 %s ⇎ 正文行 %d' % (
      F['lin_keys_total'], F['lin_keys_uniq'], F['lin_key_dup_names'], len(RELP), F['lin_rel_keys'],
      F['lin_rel_dropped'], F['lin_body_lines']))
print(u'  句式档 %s ⇎ 无值 %d ⇎ 数值 %s ⇎ 十六进制 %s ⇎ 带尾点 %d' % (
      F['lin_shape_n'], F['lin_dv_none'], F['lin_numvals'], F['lin_hexvals'], F['lin_val_punct']))
print(u'  默认值:', json.dumps(F['lin_defaults'], ensure_ascii=False))
print(u'  逐行读不到 ⇎ 整块读得到 %s ⇎ 换行原样拼接才丢 %s ⇎ 逐行尺 %s' % (
      F['lin_wrap_gain'], F['lin_split_gain'], json.dumps(F['lin_defaults_line'], ensure_ascii=False)))

# ---------- 9. 倍增等式(两把尺) ⇎ 924.6 不可面导 ----------


def sum_last(N, rto=1):
    """到“最后一次重传”为止的累计秒数: rto+2rto+4rto+… 共 N 项, 逐次倍增值累加(本遍轨)。"""
    v, acc, k = rto, 0, 0
    while k < N:
        acc += v
        v *= 2
        k += 1
    return acc


def sum_kill(N, rto=1):
    """文档自己说 “killing the connection at the (N+1)th RTO” ⇒ 末次之和再加一项。"""
    return sum_last(N + 1, rto)


def geo_sum(N, rto=1):
    """采集侧那一把: 闭式 rto·(2^N − 1)。两把尺逐行同数才入账。"""
    return rto * (2 ** N - 1)


EQ = []


def eq_face(k):
    """从那一键自己的正文块现读四个量: 默认 N ⇎ 印出的“末次”秒数 ⇎ 印出的“最终”秒数 ⇎ 印出的初始 RTO。"""
    tb = pnorm(u' '.join(BODY[k]))
    m = re.search(u'default value is ([0-9]+)', tb)
    a = re.search(u'corresponds to ([0-9]+) ?seconds', tb)
    b = re.search(u'happen after ([0-9]+) ?seconds', tb)
    r = re.search(u'initial rto of ([0-9]+) ?second', tb)
    assert m and a and b and r, k
    return [int(m.group(1)), int(a.group(1)), int(b.group(1)), int(r.group(1))]


for nm, k in [(u'syn', u'tcp_syn_retries'), (u'synack', u'tcp_synack_retries')]:
    N, pa, pb, rto = eq_face(k)
    EQ.append([nm, N, sum_last(N, rto), sum_kill(N, rto), geo_sum(N, rto), pa, pb, rto])
F['eq_rows'] = EQ
F['eq_ok_syn'] = 1 if EQ[0][2] == EQ[0][5] and EQ[0][3] == EQ[0][6] else 0
F['eq_ok_synack'] = 1 if EQ[1][2] == EQ[1][5] and EQ[1][3] == EQ[1][6] else 0
F['eq_ruler_ledger'] = [x[2] - x[4] for x in EQ]
F['eq_two_rulers_diff'] = sum(F['eq_ruler_ledger'])
F['eq_printed'] = [cnt_re(FOL[4], u'%dseconds' % x) for x in [31, 63, 127]]
F['eq_printed_all'] = sorted(set([m.group(0) for m in re.finditer(u'[0-9]+seconds', FOL[4])]))
F['eq_min_n_last'] = min([n for n in range(1, 20) if sum_last(n) >= 100])
F['eq_min_n_kill'] = min([n for n in range(1, 20) if sum_kill(n) >= 100])
DOC8 = re.search(u'a value of at least ([0-9]+)', FOL[4])
assert DOC8, u'内核那一份没印出“至少几”'
F['eq_doc_says'] = int(DOC8.group(1))
F['eq_off_by'] = [F['eq_doc_says'] - F['eq_min_n_last'], F['eq_doc_says'] - F['eq_min_n_kill']]
F['eq_n15_last'] = sum_last(15)
F['eq_n15_kill'] = sum_kill(15)
F['eq9246_by_src'] = [cnt_re(FOL[i], u'924.6') for i in range(NSRC)]
F['eq_9246_printed'] = F['eq9246_by_src'][4]
P9246 = re.search(u'([0-9]+\\.[0-9]+) +seconds', FOL[4])
assert P9246, u'924.6 那一句读不到小数秒'
F['eq_9246_face'] = float(P9246.group(1))
RTO = dict((k, F['lin_defaults'].get(k)) for k in [u'rto_min', u'rto_max', u'rto_initial'])
F['eq_rto_face'] = [int(RTO[u'rto_min']) / 1000.0, int(RTO[u'rto_max']) / 1000.0,
                    int(RTO[u'rto_initial']) / 1000.0]
F['eq_rto_min_ms'] = int(RTO[u'rto_min'])
F['eq_9246_cand'] = [sum_last(15, F['eq_rto_face'][0]), sum_kill(15, F['eq_rto_face'][0]),
                     sum_last(15, F['eq_rto_face'][2]), sum_last(15, F['eq_rto_face'][1]),
                     geo_sum(15, F['eq_rto_face'][0])]
F['eq_9246_hit'] = len([x for x in F['eq_9246_cand'] if abs(x - F['eq_9246_face']) < 0.05])
F['eq_9246_gap'] = [round(x - F['eq_9246_face'], 1) for x in F['eq_9246_cand']]
print(u'9 等式:', EQ, u' 面上印出', F['eq_printed'], u' 达到100秒的最小N 末次/杀死 %d/%d ⇎ 文书印 %d ⇎ 差 %s' % (
      F['eq_min_n_last'], F['eq_min_n_kill'], F['eq_doc_says'], F['eq_off_by']))
print(u'  N=15 倍增和 %d/%d ⇎ 面印 924.6 %s 枚 %s ⇎ 候选 %s ⇎ 命中 %d ⇎ 差 %s' % (
      F['eq_n15_last'], F['eq_n15_kill'], F['eq9246_by_src'], F['eq_9246_face'],
      F['eq_9246_cand'], F['eq_9246_hit'], F['eq_9246_gap']))

# ---------- 10. 反向对照针 ⇎ 共现针 ⇎ 关键词模板段 ----------
# 独占针: 只应该在自己那一份的摘壳面上读到。共现针单列一档: 它们本就注定在他份读得到
# (9293 把 793 的那句循环原样复印, 模板段则是 9293/6298 共用的套话)。
NEG = [(u'1122', u'An application MUST be able to set the value for R2'),
       (u'9293', u'set R2 to "infinity"'),
       (u'9293', u'the tcp endpoint will'),
       (u'6298', u'A maximum value MAY be placed on RTO provided it is at least 60 seconds'),
       (u'lin', u'before killing the connection'),
       (u'lin', u'tcp_retries2'),
       (u'lin', u'TCP_RTO_MIN'),
       (u'lin', u'924.6'),
       (u'lin', u'(N+1)th'),
       (u'lin', u'association_max_retrans'),
       (u'793', u'the tcp will')]
KW_SHORT = u'The key words'
RP = [(u'793', u'reinitialize the retransmission timer, and return'),
      (u'9293', KW_SHORT),
      (u'6298', KW_SHORT)]
IDX = dict((t, n) for n, t in enumerate(LBL))


def neg_rows(pool):
    out = []
    for own, p in pool:
        row = [cnt_re(SHP[j], pnorm(p)) for j in range(NSRC)]
        out.append((own, p, row, sum(row[j] for j in range(NSRC) if j != IDX[own]),
                    row[IDX[own]], [LBL[j] for j in range(NSRC) if j != IDX[own] and row[j] > 0]))
    return out


NEGEX = neg_rows(NEG)
RPEX = neg_rows(RP)
F['neg_n'] = len(NEG)
F['neg_probes'] = len(NEG) * NSRC
F['neg_mat'] = [z[2] for z in NEGEX]
F['neg_others'] = sum([z[3] for z in NEGEX])
F['neg_self'] = len([z for z in NEGEX if z[4] > 0])
F['neg_self_tot'] = sum([z[4] for z in NEGEX])
F['neg_cold'] = [z[1] for z in NEGEX if z[4] == 0]
F['neg_multi'] = [z[1] for z in NEGEX if z[4] > 1]
F['neg_clean'] = len([z for z in NEGEX if z[3] == 0 and z[4] == 1])
F['rp_n'] = len(RP)
F['rp_mat'] = [z[2] for z in RPEX]
F['rp_others'] = sum([z[3] for z in RPEX])
F['rp_self_tot'] = sum([z[4] for z in RPEX])
F['rp_other_src'] = sorted(set([d for z in RPEX for d in z[5]]))
F['rp_reprint_9293'] = F['rp_mat'][0][IDX[u'9293']]
F['rp_all_carry'] = [z[3] > 0 for z in RPEX]
KW = u'The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT"'
F['kw_head'] = [FOL[i].find(pnorm(KW)) for i in range(NSRC)]
KWS = [SHP[i].find(pnorm(KW)) for i in range(NSRC)]
F['kw_head_sh'] = KWS
F['kw_present'] = [1 if F['kw_head'][i] >= 0 else 0 for i in range(NSRC)]
F['kw_docs'] = len([1 for x in KWS if x >= 0])
KWPAIR = [(a, b) for a in range(NSRC) for b in range(a + 1, NSRC)
          if KWS[a] >= 0 and KWS[b] >= 0]
F['kw_pair_n'] = len(KWPAIR)
F['kw_same'] = [1 if SHP[a][KWS[a]:KWS[a] + 200] == SHP[b][KWS[b]:KWS[b] + 200] else 0 for a, b in KWPAIR]
F['kw_same_raw'] = [1 if FOL[a][F['kw_head'][a]:F['kw_head'][a] + 200]
                    == FOL[b][F['kw_head'][b]:F['kw_head'][b] + 200] else 0 for a, b in KWPAIR]
print(u'10 反向针 %d 式 ⇎ 探针 %d ⇎ 被排除份上命中 %d ⇎ 自己份读得到 %d/%d ⇎ 全冷 %s' % (
      F['neg_n'], F['neg_probes'], F['neg_others'], F['neg_self'], F['neg_n'], F['neg_cold']))
print(u'   模板段: 在面 %s ⇎ 偏移 %s ⇎ 配对 %d' % (F['kw_present'], F['kw_head'], F['kw_pair_n']))
print(u'   共现针 %d 枚 ⇎ 他份命中 %s ⇎ 落点 %s ⇎ 9293 复印 793 那句 %d 枚 ⇎ 矩阵 %s' % (
      F['rp_n'], F['rp_others'], F['rp_other_src'], F['rp_reprint_9293'], F['rp_mat']))

# --- PICK BEGIN --- (与采集遍逐键对账: 同一把定义, 第二套实现)
PK = json.load(io.open(u'corpus/_b86meas.json', encoding='utf-8'))
PAIRS = [(u'bytes', u'bytes'), (u'n_lf', u'n_lf'), (u'n_cr', u'n_cr'), (u'splitlines', u'splitlines'),
         (u'splitnl', u'splitnl'), (u'ff', u'ff'), (u'ff_led', u'ff_led'), (u'blank', u'blank'),
         (u'maxlen', u'maxlen'), (u'tab', u'tab'), (u'bom', u'bom'), (u'foot', u'foot_page'),
         (u'hdr793', u'hdr_793'), (u'hdr1122', u'hdr_rfc1122'), (u'hdrnew', u'hdr_new'),
         (u'ietf_alone', u'ietf_alone'), (u'ff_before_nl', u'ff_before_nl'),
         (u'ff_at_eof', u'ff_at_eof'), (u'trailing_nl', u'trailing_nl'),
         (u'pgnum', u'pgnum'), (u'keylin', u'default_keys'), (u'default_lines', u'default_lines'),
         (u'shell_lines', u'shell_lines'), (u'tag_paren', u'tag_paren'), (u'tag_dash', u'tag_dash'),
         (u'numtimes', u'numtimes'), (u'lin_keys_uniq', u'lin_keys_total'),
         (u'lin_defaults_pick', u'lin_defaults'), (u'lin_shape_pick', u'lin_default_shape'),
         (u'lin_rel_pick_names', u'lin_rel_keys'),
         (u'role_src', u'needle_src'), (u'ob_wrap', u'ob_wrap')]
AGREE, DIFFK = [], []
for mk_k, pk_k in PAIRS:
    if mk_k not in F or pk_k not in PK:
        DIFFK.append(mk_k + u'?' + pk_k)
        continue
    (AGREE if F[mk_k] == PK[pk_k] else DIFFK).append(mk_k)
for mk_k, pk_k in [(u'spell', u'spell'), (u'ob_line', u'ob_line'), (u'ob_fold', u'ob_fold')]:
    (AGREE if F[mk_k] == PK[pk_k] else DIFFK).append(mk_k)
three = [[[F['role_line'][k][i], F['role_fold'][k][i], F['role_sh'][k][i]] for i in range(NSRC)]
         for k in range(len(NK))]
N3D = []
for k in range(min(len(three), len(PK[u'needles3']))):
    for i in range(NSRC):
        for t in range(3):
            if three[k][i][t] != PK[u'needles3'][k][i][t]:
                N3D.append([k, NEEDLES[k][:22], LBL[i], t, three[k][i][t], PK[u'needles3'][k][i][t]])
F['n3_diff'] = N3D
(AGREE if three == PK[u'needles3'] else DIFFK).append(u'needles3')
F['lin_rel_names_cmp'] = sorted(REL2)
for mk_k, pk_k in [(u'na_codepoints', u'nonascii'), (u'numunit_raw', u'numunit'),
                   (u'ovl_s1', u'ovl_s1'), (u'ovl_s2', u'ovl_s2'),
                   (u'ovl_same_tag', u'ovl_same'), (u'ovl_same_canon', u'ovl_same2')]:
    a, b = F[mk_k], PK[pk_k]
    if mk_k in (u'ovl_s1', u'ovl_s2', u'ovl_same_tag', u'ovl_same_canon'):
        a, b = [a], [b]
    if mk_k == u'numunit_raw':
        a = [sorted([tuple(z) for z in x]) for x in F['numunit_raw']]
        b = [sorted([tuple(z) for z in x]) for x in PK['numunit']]
        F['numunit_ruler_diff'] = 1 if a == b else 0
        F['numunit_track_diff'] = [[sorted(set(x) - set(y)), sorted(set(y) - set(x))]
                                   for x, y in zip(a, b)]
    (AGREE if a == b else DIFFK).append(mk_k)
for mk_k, pk_k in [(u'kw_allcaps', u'kw_allcaps'), (u'kw_lowercase', u'kw_lowercase')]:
    (AGREE if F[mk_k] == PK[pk_k] else DIFFK).append(u'pk_' + mk_k)
F['pick_agree'] = len(AGREE)
F['pick_diff'] = len(DIFFK)
F['pick_diffk'] = sorted(DIFFK)
F['lin_def_diff'] = [[k, F['lin_defaults_pick'][k], PK[u'lin_defaults'].get(k),
                      F['lin_shape_pick'][k], PK[u'lin_default_shape'].get(k)]
                     for k in sorted(F['lin_defaults_pick'])
                     if F['lin_defaults_pick'][k] != PK[u'lin_defaults'].get(k)
                     or F['lin_shape_pick'][k] != PK[u'lin_default_shape'].get(k)]
print(u'PICK 对账: %d 键符 ⇎ %d 键不符 %s' % (F['pick_agree'], F['pick_diff'], sorted(DIFFK)))
if N3D:
    print(u'   needles3 逐格不符(针, 份, 档 0行/1折/2壳, 本遍, 采集):', N3D)
print(u'   numunit 两轨差:', F.get('numunit_track_diff'))
print(u'   内核默认值逐键差:', json.dumps(F['lin_def_diff'], ensure_ascii=False))
# --- PICK END ---

# ---------- 布尔门(每道都能失败) ----------
CLOSE = []


def K(name, expr, note):
    CLOSE.append((name, expr, note))


def _cb(name, val, expr, note):
    F[name] = 1 if val else 0
    return (name, expr, note)


CLOSE2 = {}
G = []
G.append((u'五份全 LF 面', all([F['n_cr'][i] == 0 for i in range(NSRC)])))
G.append((u'最长行两把尺同值', F['maxlen'] == F['maxlen_scan']))
G.append((u'行式对账逐份平', F['rows_ledger'] == F['rows_pred']))
G.append((u'字节两把尺同值', F['bytes'] == F['bytes_stat']))
G.append((u'换行三把尺同值', F['splitnl'] == [F['n_lf'][i] + 1 for i in range(NSRC)]
                            and F['lf_vs_readlines'] == [0] * NSRC))
G.append((u'壳谓词两把尺逐行同集', F['shell_pred_diff'] == [0] * NSRC))
G.append((u'壳账容斥闭合', F['shell_ledger'] == [0] * NSRC))
G.append((u'剥壳正文行+壳行=总行', F['body_shell_ledger'] == [0] * NSRC))
G.append((u'独立页码行一枚也不合壳形', F['pgnum_in_shell'] == [0] * NSRC and sum(F['pgnum']) > 0))
G.append((u'义务词第三轨与表尺同数', F['ob_ruler_diff'] == 0))
G.append((u'编号族只在 9293', [F['tag_dash'][i] > 0 for i in range(NSRC)] == [False, False, True, False, False]))
G.append((u'编号两形状之差=括号被拉开的那一枚', F['tag_split_ledger'] == [0] * NSRC))
G.append((u'编号 token 尺缺口=方括号套住的那些', F['tag_bracket_ledger'] == [0] * NSRC))
G.append((u'被推下去的编号只在 9293', [F['tag_num_nextline'][i] > 0 for i in range(NSRC)]
                                  == [False, False, True, False, False]))
G.append((u'拉开与套括都只在 9293', [F['tag_paren_apart'][i] + F['tag_bracket'][i] > 0 for i in range(NSRC)]
                                == [False, False, True, False, False]))
G.append((u'编号词种相加=总数', F['tag_kind_ledger'] == [0] * NSRC))
G.append((u'793 大写义务词一枚也没有', F['ob_upper_tot'][0] == 0))
G.append((u'小写并集盖得住大写并集(原面两把尺)', all([F['kw_ci'][i] >= F['kw_allcaps'][i]
                                                     for i in range(NSRC)])))
G.append((u'义务词短语账与并集账嵌套闭合', F['ob_nest_ledger'] == [0] * NSRC))
G.append((u'答句五份都读得到', all([F['ans_words'][i] > 0 for i in range(NSRC)])))
G.append((u'答句在摘壳面内', all([pnorm(F['ans_sent'][i]) in SHP[i] for i in range(NSRC)])))
G.append((u'答句行内尺只在 9293 读得到', F['ans_needle_line'] == [0, 0, 1, 0, 0]))
G.append((u'答句跨度只压着一枚壳行且它不是页码页眉', sum(F['ans_shell_rows']) == 1
                                            and sum(F['ans_page_rows']) == 0))
G.append((u'答句全是 ASCII', sum(F['na_in_ans']) == 0))
G.append((u'倍增两把尺同值', F['eq_two_rulers_diff'] == 0))
G.append((u'syn 等式命中印数', F['eq_ok_syn'] == 1))
G.append((u'synack 等式命中印数', F['eq_ok_synack'] == 1))
G.append((u'924.6 只在一份印出', F['eq9246_by_src'] == [0, 0, 0, 0, 1]))
G.append((u'面上三个 RTO 参数复现不出 924.6', F['eq_9246_hit'] == 0))
G.append((u'独占针在他份零命中', F['neg_others'] == 0))
G.append((u'独占针本份全读得到', F['neg_self'] == F['neg_n']))
G.append((u'没有全冷的独占针', F['neg_cold'] == []))
G.append((u'共现针张张在他份读得到', all(F['rp_all_carry'])))
G.append((u'共现落点只有 9293 与 6298', F['rp_other_src'] == [u'6298', u'9293']))
G.append((u'9293 恰复印 793 那句一枚', F['rp_reprint_9293'] == 1))
G.append((u'模板段只在两份', sum(F['kw_present']) == 2))
G.append((u'段落端点找到了', min(S1 + E1 + S2 + E2) >= 0))
G.append((u'切句两把尺逐句同列表', F['ovl_splitter_list'] == 1))
G.append((u'新句数=句数−同句数', F['ovl_new'] == F['ovl_s2'] - F['ovl_same_tag']))
G.append((u'同句数单调三档', F['ovl_same_raw'] <= F['ovl_same_tag'] <= F['ovl_same_canon']))
G.append((u'词对齐 autojunk 无差', F['blk_autojunk_diff'] == 0))
G.append((u'词账三条通道闭合', F['blk_form_ledger'] == [0, 0, 0]))
G.append((u'9293 段不是 1122 段的子串', F['blk_is_substring'] == 0))
G.append((u'内核键=键行', F['lin_keys_total'] == F['keylin'][4]))
G.append((u'键行减去重=重名枚数', F['lin_keys_total'] - F['lin_keys_uniq'] == len(F['lin_key_dup_names'])))
G.append((u'内核两把名尺并集容斥闭合', F['lin_rel_union']
                                        == len(F['lin_rel_pick_names']) + F['lin_rel_keys'] - F['lin_rel_both']))
G.append((u'句式档相加=相关键', sum(F['lin_shape_n']) == F['lin_rel_keys']))
G.append((u'Default 行只在内核文档', all([F['default_lines'][i] == 0 for i in range(NSRC - 1)])
                                and F['default_lines'][4] > 0))
G.append((u'粘连式只在内核文档', F['glued_n'][4] >= 1 and sum(F['glued_n'][:4]) == 0))
G.append((u'原面数值项两轨同集', F['numunit_ruler_diff'] == 1))
G.append((u'换行切开针都读得到', all([F['role_sh'][k] != [0] * NSRC for k in F['wrap_cut']])))
G.append((u'去编号新添了读数而一处也没减', sum(F['tag_gain_cells']) > 0 and sum(F['tag_drop_cells']) == 0))
G.append((u'去编号的挪动只在 9293', sorted(set([z[1] for z in F['tag_move']])) == [u'9293']))
G.append((u'涨格减跌格=9293 那份的净值', F['tag_gain'][2] == sum(F['tag_gain_cells']) - sum(F['tag_drop_cells'])))
G.append((u'对账无不符键', F['pick_diff'] == 0))
GK = []
for gi, (nm, val) in enumerate(G):
    sl = re.sub(u'[^a-z0-9]', u'', nm)[:12]
    key = u'gc_' + (sl if sl != u'' else u'g%02d' % gi)
    while key in F:
        key += u'x'
    F[key] = 1 if val else 0
    GK.append([key, nm, 1 if val else 0])
F['gate_keys'] = GK
F['bool_all_n'] = len(G)
F['bool_green'] = len([1 for nm, v in G if v])
F['bool_red'] = [nm for nm, v in G if not v]
print(u'布尔门 %d 道, 绿 %d ⇎ 红 %s' % (F['bool_all_n'], F['bool_green'], F['bool_red']))
assert F['bool_green'] == F['bool_all_n'], F['bool_red']

# ---------- 恒等式(ZID: 全归零才算平) ----------
ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"sum(F['rows_ledger_diff'])", u'行式对账: splitlines−split(\\n) = 换页后随换行−尾换行, 逐份相减')
Z(u"sum(F['byte_cp_ledger'])", u'字节 − 码位 = UTF-8 多出的字节, 逐份相减')
Z(u"sum(F['line_split_ledger'])", u'总行 = 非空行 + 空行, 逐份相减')
Z(u"sum(F['lf_vs_readlines'])", u'行尺三轨: split(\\n)  ⇎ readlines ⇎ 换行数+1 逐份相同')
Z(u"sum([abs(x) for x in F['shell_ledger']])", u'壳账容斥: 壳行 = 七形之和 − 重数(逐枚重扫)')
Z(u"sum([abs(x) for x in F['body_shell_ledger']])", u'剥壳正文行(另数一遍) + 壳行 = 总行')
Z(u"sum(F['pgnum']) - sum(F['pgnum_in_shell']) - sum(F['pgnum_naked'])",
  u'独立成行的纯数字行 = 被壳形收走的那些 + 留在正文里的那些')
Z(u"sum(F['ob_wrap']) - (sum(F['ob_fold_tot']) - sum(F['ob_line_tot']))",
  u'跨行涨量: 逐格相加 = 两档总量之差(行的和 ⇎ 列的和)')
Z(u"sum(F['ob_upper_tot']) - sum([sum(F['ob_sh'][i]) for i in range(5)])",
  u'大写义务词: 按份登记的合计 = 现从第四档逐词相加')
Z(u"sum(F['tag_split_ledger'])", u'编号两形状(括号形另扫 + 裸形另扫) + 括号被拉开的那些 = 横杠式总数')
Z(u"sum(F['tag_bracket_ledger'])", u'编号 token 尺 + 被方括号套住的那些 = 横杠式总数')
Z(u"sum(F['tag_split_manual']) - sum(F['tag_paren_apart']) - sum(F['tag_num_nextline'])",
  u'左括号开了却没即时合上的编号 = 拉开的那一枚 + 数字被推到下一行的那几枚')
Z(u"sum(F['tag_nextline_ledger'])", u'无空白尺读到的编号 = 横杠式 + 数字被推到下一行的那些')
Z(u"sum(F['tag_fold_gain'])", u'折平后的横杠式编号 − 原面横杠式编号 = 零(折平留了一格空格)')
Z(u"sum(F['tag_kind_ledger'])", u'编号按五种词头分档相加 = 横杠式总数')
Z(u"sum(F['wrap_gain_cells']) - F['wrap_gain_tot']", u'换行涨量: 逐针相加 = 逐份相加')
Z(u"sum(F['tag_gain_cells']) - sum(F['tag_drop_cells']) - F['tag_gain_tot']",
  u'去编号挪动: 涨格 − 跌格 = 逐份净值')
Z(u"len(F['tag_move']) - len(F['tag_cut'])",
  u'去编号挪动: 逐(针×份)格数 = 挪动的针数(每枚针至多在一份里挪)')
Z(u"sum(F['spell_diff']) - (sum(F['spell_tot']) - sum(F['spell_word_tot']))",
  u'子串尺比整词尺多读的枚数 = 两尺总量之差')
Z(u"sum([len(x) for x in F['spell_excl']]) - F['excl_n']", u'独有式清单 = 独有式枚数')
Z(u"F['ovl_s2'] - F['ovl_same_tag'] - F['ovl_new']", u'新句 = 句数 − 去编号同句数')
Z(u"sum(F['blk_form_ledger'])", u'词账三通道(匹配块 ⇎ 操作码 ⇎ 全长)在两种口径下相消')
Z(u"F['blk_autojunk_diff']", u'默认 autojunk 的匹配字数 = 关掉后的字数')
Z(u"F['lin_keys_total'] - F['keylin'][4]", u'内核键数 = 键行匹配枚数(两套正则)')
Z(u"sum(F['lin_shape_n']) - F['lin_rel_keys']", u'五种句式档相加 = 相关键数')
Z(u"F['default_lines'][4] - F['lin_default_lines']", u'Default 行总数 = 内核那一份的读数')
Z(u"F['eq_two_rulers_diff']", u'倍增两把尺(逐项累加 ⇎ 闭式)逐行相加同值')
Z(u"F['neg_probes'] - F['neg_n'] * 5", u'独占针探针 = 式数 × 份数')
Z(u"sum([sum(x) for x in F['neg_mat']]) - F['neg_others'] - F['neg_self_tot']",
  u'独占针矩阵: 全体相加 = 他份命中 + 本份命中')
Z(u"F['neg_self_tot'] - sum([max(x) for x in F['neg_mat']])",
  u'独占针: 他份零命中时, 每行的最大值就是本份读数')
Z(u"F['neg_clean'] + len(F['neg_multi']) - F['neg_n']",
  u'独占针逐枚: 本份恰一枚 ⇎ 本份多枚, 两档相加 = 式数')
Z(u"sum([sum(x) for x in F['rp_mat']]) - F['rp_self_tot'] - F['rp_others']",
  u'共现针矩阵: 全体相加 = 他份命中 + 本份命中')
Z(u"sum(F['kw_ci']) - sum(F['kw_allcaps']) - sum(F['kw_lowercase'])",
  u'关键词三把尺: 大小写不分总量 = 全大写 + 其余')
Z(u"sum(F['kw_same']) - sum(F['kw_same_raw'])", u'模板段是否同文: 摘壳面 ⇎ 全篇折平面两把尺同判')
Z(u"sum(F['kw_present']) - F['kw_docs']", u'模板段存在与否(标志尺 ⇎ 偏移尺)')
Z(u"F['kw_pair_n'] - (F['kw_docs'] * (F['kw_docs'] - 1)) // 2", u'模板段配对数 = 存在份数的两两组合')
Z(u"F['pick_diff']", u'与采集遍逐键对账的不符数为零')
Z(u"F['bool_green'] - F['bool_all_n']", u'布尔门全绿')
for e, w in ZID:
    v = eval(e, {u'F': F, u'range': range, u'sum': sum, u'len': len, u'max': max, u'abs': abs})
    if v != 0:
        print(u'ZID 不平: %s ⇒ %s' % (w, v))
        raise SystemExit(1)
print(u'恒等式 %d 条全平' % len(ZID))
F['zid_scan_n'] = len(ZID)
F['scan_key_n'] = len(F)
# --- SCAN END --- (以上由 _wire86.py 机械切进 audit.py::_b86_scan)

BB86 = lambda name, i=None: (F[name] if i is None else F[name][i])


def _ev(e):
    return eval(e, {u'B86V': BB86, u'NSRC': NSRC, u'range': range, u'F': F, u'len': len, u'sum': sum})


FN = u'B86V'
_to_v = re.compile(r"(?:F)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B86V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(5)').replace(u'NSRC', u'5')


K_, ZERO, COLL, SEENX = {}, [], {}, {}


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K_:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K_.setdefault(s, (expr, note))
    return


def V(name, i=None, note=u''):
    if name not in F:
        raise AssertionError(u'无此键 ' + name)
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def J(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LBL[i])) for i in range(NSRC))


def JL(name, note=u''):
    return V(name, None, note) if isinstance(F[name], (list, dict)) else J(name, note)


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


ZV = []
for e, w in ZID:
    v = to_v(e.replace(u'\n', u''))
    if eval(v, {FN: BB86, u'range': range, u'sum': sum, u'len': len, u'max': max, u'abs': abs}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))
    reg(str(_ev(e)), v, w)


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB86}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([str(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


for k, v in dump_deriv().items():
    DER[k] = v

print(u'第二遍量测完成: 扁平键 %d ⇎ 恒等式 %d 全平 ⇎ 布尔门 %d 全绿 ⇎ 针 %d(反向 %d) ⇎ 对账 %d 符 %d 不符'
      % (len(F), len(ZID), F['bool_all_n'], F['needle_n'], F['neg_n'], F['pick_agree'], F['pick_diff']))
io.open(u'corpus/_b86flat.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True))

exec(io.open(u'corpus/_mk86emit.py', encoding='utf-8').read())
