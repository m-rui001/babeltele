# -*- coding: utf-8 -*-
"""建条目第二遍(B95): “X.509 证书序列号到底能有多长、什么算违规”, 五份一手文书各答一遍
2459(1998 PKIX 初版: 序列号只写 "an integer assigned by the CA" + 唯一性, 符号与长度一枚数都不给;
  全篇 '20 octets' 最宽档 0 命中, 'positive' 只剩 ASN.1 备忘里的 positiveint)
⇎ 3280(2002: 补上 MUST be a positive integer ⇎ CAs MUST force ... non-negative ⇎ 20 octets 双句,
  Note 作 negative, or zero(带逗号), 且全篇还留着 6 处 Conformant——5280 把它删尽了)
⇎ 5280(2008: 与 3280 同文而删尽 Conformant(最宽档 0), Note 去逗号; 附录 B: sign bit MUST be zero,
  必要时补一枚前导 00'H octet; 目录属性上限 ub-serial-number INTEGER ::= 64(64 的第三种尺: 字符数);
  §7.1 样例把 17/18/256 三枚序列号连 DER 内容长度一并印出——三代里只有它印这个格式)
⇎ CA/B TLS BR v2.0.2(2023 世代: 尺子整个换成值域——八行 serialNumber 表行(八枚不同的 7.1.2.x 节)印
  "non-sequential number greater than zero (0) and less than 2¹⁵⁹ containing at least 64 bits of output
  from a CSPRNG", '64 bits' 共 9 枚: 多出的那枚是变更表里 Ballot 156 的旧句(只束熵不束上界);
  2¹⁵⁹ 的上标要 UTF-8 档才收齐——layout ⇎ raw ⇎ pypdf 三面各 9 枚)
⇎ Let's Encrypt《A Warm Welcome to ASN.1 and DER》(实现侧: 8 字节的 DER 序列号最多 63 位,
  64 位正数要 9 字节(首字节补 0), 并印出 2^63+1 的九字节编码 02 09 00 80 00 00 00 00 00 00 01;
  原文 HTML, 上标在壳内作 2<sup>63</sup>, 剥壳档散作 2 63)。

本遍与采集侧(_pick95.py)换机制而不换定义, 十一处:
①字面针: 采集侧游标 find 环 ⇎ 本遍 re.findall(re.escape) 整体扫描, 另立重叠档 finditer('(?=针)');
②整词尺: 采集侧邻居字符手扫 ⇎ 本遍先把整串翻成三张布尔表(字母/数字/字母数字)再查表读左右邻, 第三轨负向断言正则——三轨逐枚同数才入账;
③壳谓词: 采集侧对整行跑序列正则 ⇎ 本遍先 strip 再逐字符游标定形(找 '[Page '+数字+']' ⇎ 'RFC '+恰四数字+空格串+非空白 ⇎ 'pg.'+数字+界), 逐行必须同集;
④行号尺: 采集侧 4 行滑窗在折平面试 ⇎ 本遍建全篇折平面 + 累积长度表交给 bisect 由面偏移直映原行;
⑤句界: 采集侧一条 re.split('(?<=[.!?]) +') ⇎ 本遍逐字符扫“句末标点+空格”;
⑥DER 样例抽取: 采集侧一条选择支正则 ⇎ 本遍按空白切 token 判形([序, '17:', 'INTEGER', '1'] 四件套);
⑦节归属: 采集侧对每行上方前缀跑 finditer ⇎ 本遍先一次枚出全部 7.1.2.x 标题建清单, 再按行号 bisect 归属;
⑧同文句池: 采集侧集合 & ⇎ 本遍 Counter 直方图逐句取 min 相加;
⑨DER 长度: 采集侧 bit_length 闭式 ⇎ 本遍逐次右移数比特再算字节;
⑩LE 十六进制串: 采集侧 split+join 定长切片 ⇎ 本遍逐字符收 hex 两枚一组共十一组;
⑪上限值: 采集侧靠整枚针 'ub-serial-number INTEGER ::= 64' 命中 ⇎ 本遍两条正则级联剥前缀再就地读数字。
四档口径: 原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 重叠档; 所有正文数字由 V()/J()/EXPR() 注册后插值, 一枚都不手打;
锚一律由面上位置导出。键名等于所量之物。对账结果写回 corpus/_b95meas.json。"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'2459', u'3280', u'5280', u'br', u'le']
NSRC = 5
YR = [1998, 2002, 2008, 2023, 2021]
PATH = [u'corpus/raw/serialLen/rfc2459.txt', u'corpus/raw/serialLen/rfc3280.txt',
        u'corpus/raw/serialLen/rfc5280.txt', u'corpus/raw/serialLen/br_v202.layout.txt',
        u'corpus/raw/serialLen/le_asn1_der.html']
BRFACES = [u'corpus/raw/serialLen/br_v202.layout.txt', u'corpus/raw/serialLen/br_v202.raw.txt',
           u'corpus/raw/serialLen/br_v202.pypdf.txt']
STRIPPED = u'corpus/raw/serialLen/le_asn1_der.txt'
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire95.py 把这一段 ⇎ 前面的模块级前奏一并机械切进 _b95_scan)


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
RAWL = [t.split(NL) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]


def pnorm(s):
    return u' '.join(s.lower().split())


def cnt_re(hay, nd):
    """本遍的字面针轨: 转义后整体正则扫描(采集侧是游标环)。"""
    return len(re.findall(re.escape(nd), hay))


def cnt_ovl(hay, nd):
    """重叠档: 同一处允许被后面那次命中起点复用。"""
    return len(re.findall(u'(?=%s)' % re.escape(nd), hay))


def cnt_cur(hay, nd):
    """采集侧那一把(游标 find 环), 本遍只用于对拍。"""
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


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


def is_shell_pick(x, i):
    """采集侧壳谓词的逐字照抄(整行序列正则), 供两遍壳集逐行对拍。"""
    if i <= 2:
        return (re.search(u'\\[Page \\d+\\]', x) is not None
                or re.match(u'^RFC \\d{4} +\\S', x) is not None
                or re.match(u'^Internet Engineering Task Force\\s*$', x) is not None
                or (len(x) == 1 and ord(x[0]) == 12) or x.strip() == u'')
    if i == 3:
        return (re.match(u'^\\s*pg\\. \\d+\\s*$', x) is not None
                or (len(x) == 1 and ord(x[0]) == 12) or x.strip() == u'')
    return False


def sh_blank(x):
    return x.strip() == u''


def sh_ff(x):
    return x == u'\x0c'


def sh_foot(x):
    """逐字符找 '[Page ' + 数字 + ']'(采集侧是一条 search 正则)。"""
    k, n = 0, len(x)
    while True:
        k = x.find(u'[Page ', k)
        if k < 0:
            return False
        j, d0 = k + 6, k + 6
        while j < n and x[j].isdigit():
            j += 1
        if j > d0 and j < n and x[j] == u']':
            return True
        k += 1


def sh_hdr_rfc(x):
    """逐字符判 'RFC ' + 恰四数字 + 空格串 + 非空白(采集侧是 ^RFC \\d{4} +\\S)。"""
    if x[:4] != u'RFC ':
        return False
    j, d0 = 4, 4
    while j < len(x) and x[j].isdigit():
        j += 1
    if j - d0 != 4:
        return False
    sp = j
    while j < len(x) and x[j] == u' ':
        j += 1
    return j > sp and j < len(x) and not x[j].isspace()


def sh_ietf(x):
    pre = u'Internet Engineering Task Force'
    return x[:len(pre)] == pre and x[len(pre):].strip() == u''


def sh_pg(x):
    k = 0
    while k < len(x) and x[k].isspace():
        k += 1
    if x[k:k + 4] != u'pg. ':
        return False
    j, d0 = k + 4, k + 4
    while j < len(x) and x[j].isdigit():
        j += 1
    return j > d0 and x[j:].strip() == u''


SHPRED = [sh_blank, sh_ff, sh_foot, sh_hdr_rfc, sh_ietf, sh_pg]


def selpred(i):
    """本遍每份生效的壳谓词子集(与采集侧 is_shell 的分支同定义)。"""
    if i == 4:
        return []
    if i == 3:
        return [SHPRED[0], SHPRED[1], SHPRED[5]]
    return SHPRED[0:5]


def shell_shape(x, i):
    """本遍的壳谓词: 逐字符游标定形(空行 ⇎ 独占换页符 ⇎ '[Page'+数字+']' ⇎ 'RFC '+四数字 ⇎ IETF 整行 ⇎ 'pg.'+数字), 一枚序列正则也不跑。
       前三份(RFC 世代)只认 页脚/RFC眉/IETF/换页独占/空行; 第四份(BR)只认 pg.+数字/换页独占/空行; 第五份不剥。"""
    return any(f(x) for f in selpred(i))


def sent_cuts(face):
    """本遍的句界尺: 逐字符扫“句末标点 + 至少一枚空格”, 返回每句 [起, 止) 表(采集侧是一条 re.split)。"""
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


def sents_re(txt):
    """采集侧那一把: (?<=[.!?]) + 正则切句, 本遍只用于对拍。"""
    return [pnorm(z) for z in re.split(u'(?<=[.!?]) +', pnorm(txt)) if z]


def sents_char(txt):
    face = pnorm(txt)
    return [face[a:b] for a, b in sent_cuts(face)]


# 全篇折平面(含壳行): 面偏移→原行 由累积长度表 + bisect 现映(采集侧是 4 行滑窗)
CUM = []
FACC = []
OFFS = []
for i in range(NSRC):
    acc, a = [], 0
    for x in L[i]:
        a += len(x) + 1
        acc.append(a)
    CUM.append(acc)
    seg, offs, pos = [], [], 0
    for k, x in enumerate(L[i]):
        c = pnorm(x)
        if not c:
            continue
        offs.append((pos, pos + len(c), k))
        seg.append(c)
        pos += len(c) + 1
    FACC.append(u' '.join(seg))
    OFFS.append(offs)
import bisect as _bs


def off_line(i, s0):
    o = OFFS[i]
    if not o or s0 < o[0][0]:
        return -1
    lo, hi = 0, len(o) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if o[mid][0] <= s0:
            lo = mid
        else:
            hi = mid - 1
    return o[lo][2]


def find_line_b(i, nd, minrow=0):
    q = pnorm(nd)
    o = OFFS[i]
    if minrow > 0:
        if not o:
            return -1
        lo = _bs.bisect_left([z[2] for z in o], minrow)
        smin = o[lo][0] if lo < len(o) else len(FACC[i]) + 1
    else:
        smin = 0
    s0 = FACC[i].find(q, smin)
    return -1 if s0 < 0 else off_line(i, s0)


def cum_line_raw(i, off):
    """原面偏移→行下标: 按 '\\n' 累积长度表 bisect(不经 split)。"""
    return _bs.bisect_right(CUM[i], off)


# ---------- 0. 面量 ⇎ 行式对账 ----------
F['bytes'] = [len(B[i]) for i in range(NSRC)]
F['bytes_stat'] = [os.path.getsize(p) for p in PATH]
F['cp'] = [sum(1 for _ in T[i]) for i in range(NSRC)]
F['chars'] = list(F['cp'])
F['n_lf'] = [len([m.start() for m in re.finditer(u'\\n', T[i])]) for i in range(NSRC)]
F['n_cr'] = [len([m.start() for m in re.finditer(u'\\r', T[i])]) for i in range(NSRC)]
F['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
F['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
F['readlines'] = [sum(1 for _ in io.StringIO(T[i])) for i in range(NSRC)]
BDSET = u'\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029\r'
F['other_names'] = [c for c in BDSET if c != u'\r']
_ob = []
for i in range(NSRC):
    cnt = dict((c, 0) for c in F['other_names'])
    for ch in T[i]:                      # 逐字符走面数界符(采集侧是对每种界符跑游标环)
        if ch in cnt:
            cnt[ch] += 1
    _ob.append([cnt[c] for c in F['other_names']])
F['other_bounds'] = _ob
F['ff'] = [sum(1 for ch in T[i] if ch == u'\x0c') for i in range(NSRC)]
F['trail_bound'] = [1 if T[i][-1:] in (NL + BDSET) else 0 for i in range(NSRC)]
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
F['tab'] = [sum(1 for ch in T[i] if ch == u'\t') for i in range(NSRC)]
F['bom'] = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
NAOFF = [[m.start() for m in re.finditer(u'[^\\x00-\\x7f]', T[i])] for i in range(NSRC)]
F['na_total'] = [len(NAOFF[i]) for i in range(NSRC)]
F['na_codepoints'] = [sorted(set(ord(T[i][k]) for k in NAOFF[i])) for i in range(NSRC)]
F['rows_ledger'] = [F['splitlines'][i] - F['splitnl'][i] for i in range(NSRC)]
F['rows_pred'] = [sum(_ob[i]) - F['trail_bound'][i] for i in range(NSRC)]
F['rows_ledger_diff'] = [F['rows_ledger'][i] - F['rows_pred'][i] for i in range(NSRC)]
F['byte_cp_ledger'] = [F['bytes'][i] - F['cp'][i] for i in range(NSRC)]
# 字节−码位差的另一条独立算路: 逐枚非 ASCII 字符按 UTF-8 编码多出字节数之和
F['utf8_extra'] = [sum(len(ch.encode('utf-8')) - 1 for ch in T[i] if ord(ch) > 127)
                   for i in range(NSRC)]
F['line_split_ledger'] = [F['nonblank'][i] + F['blank'][i] - F['splitnl'][i] for i in range(NSRC)]
F['bytes_vs_stat'] = 0 if F['bytes'] == F['bytes_stat'] else 1
print(u'0 面量: bytes', F['bytes'], u' cp', F['cp'], u' 行式账', F['rows_ledger'], F['rows_pred'])
assert F['rows_ledger'] == F['rows_pred'], u'行式对账不平'

# ---------- 1. 壳账: 序列正则尺 ⇎ token 形状尺 ----------
F['foot_page'] = [len([x for x in L[i] if sh_foot(x)]) for i in range(NSRC)]
F['hdr_rfc'] = [len([x for x in L[i] if sh_hdr_rfc(x)]) for i in range(NSRC)]
F['ietf_alone'] = [len([x for x in L[i] if sh_ietf(x)]) for i in range(NSRC)]
F['br_pgnum'] = [len([x for x in L[i] if sh_pg(x)]) for i in range(NSRC)]
F['ff_led'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
F['shell_pick'] = [len([1 for x in L[i] if is_shell_pick(x, i)]) for i in range(NSRC)]
F['shell_shape'] = [len([1 for x in L[i] if shell_shape(x, i)]) for i in range(NSRC)]
F['shell_pred_diff'] = [len([1 for k, x in enumerate(L[i]) if is_shell_pick(x, i) != shell_shape(x, i)])
                        for i in range(NSRC)]
F['shell_lines'] = F['shell_shape']
F['body_lines'] = [F['splitnl'][i] - F['shell_lines'][i] for i in range(NSRC)]
F['shape_hits'] = [sum([len([1 for x in L[i] if f(x)]) for f in selpred(i)]) for i in range(NSRC)]
F['shape_ovl'] = [sum([max(0, len([1 for f in selpred(i) if f(x)]) - 1) for x in L[i]])
                  for i in range(NSRC)]
F['shell_ledger'] = [F['shell_lines'][i] - (F['shape_hits'][i] - F['shape_ovl'][i]) for i in range(NSRC)]
F['page_pair_gap'] = [F['foot_page'][i] - F['hdr_rfc'][i] for i in range(NSRC)]
print(u'1 壳: [Page]', F['foot_page'], u'RFC眉', F['hdr_rfc'], u'pg.', F['br_pgnum'],
      u'两尺壳行', F['shell_pick'], F['shell_shape'], u'逐行分歧', F['shell_pred_diff'])
assert F['shell_pred_diff'] == [0] * NSRC, u'两把壳尺逐行不同集'

# ---------- 2. LE HTML 壳: 标签与实体由两条各自独立的逐字符游走 ----------
HT = T[4]
def _ascL(c):
    return (u'a' <= c <= u'z') or (u'A' <= c <= u'Z')
_tags, _k = 0, 0
_n = len(HT)
while _k < _n:
    if HT[_k] == u'<' and _k + 1 < _n and (_ascL(HT[_k + 1]) or HT[_k + 1] in u'/!'):
        j = HT.find(u'>', _k)
        if j >= 0:
            _tags += 1
            _k = j + 1
            continue
    _k += 1
_ent, _k = 0, 0
while _k < _n:
    if HT[_k] == u'&':
        j = HT.find(u';', _k)
        if 0 <= j < _n:
            m = HT[_k + 1:j]
            if (m and all(_ascL(c) for c in m)) or \
               (len(m) > 1 and m[0] == u'#' and m[1:].isdigit()):
                _ent += 1
                _k = j + 1
                continue
    _k += 1
F['le_tags'] = _tags
F['le_entities'] = _ent
ST = io.open(STRIPPED, 'rb').read().decode('utf-8', 'replace')
F['le_html_chars'] = sum(1 for _ in HT)
F['le_stripped_chars'] = sum(1 for _ in ST)
F['le_drop'] = F['le_html_chars'] - F['le_stripped_chars']
print(u'2 LE壳: 标签', F['le_tags'], u'实体', F['le_entities'], u'壳面', F['le_html_chars'], u'剥壳面',
      F['le_stripped_chars'], u'吃掉', F['le_drop'])

# ---------- 3. BR 三张提取面的指数账 ----------
BRF = {}
BRF_B = {u'layout': [], u'raw': [], u'pypdf': []}
for nm, p in [(u'layout', BRFACES[0]), (u'raw', BRFACES[1]), (u'pypdf', BRFACES[2])]:
    s = io.open(p, 'rb').read().decode('utf-8', 'replace')
    BRF[nm] = {
        'chars': len(s),
        'n159': cnt_re(s, u'2\u00b9\u2075\u2079'),
        'n1': cnt_re(s, u'2\u00b9'),
        'csprng': cnt_re(s, u'CSPRNG'),
        'serial_cap': cnt_re(pnorm(s), pnorm(u'greater than zero (0) and less than 2\u00b9\u2075\u2079')),
    }
    BRF_B[nm] = [BRF[nm]['chars'], BRF[nm]['n159'], BRF[nm]['n1'], BRF[nm]['csprng'], BRF[nm]['serial_cap']]
F['br_faces'] = BRF
_f = [u'layout', u'raw', u'pypdf']
F['brf_chars'] = [BRF[x]['chars'] for x in _f]
F['brf_n159'] = [BRF[x]['n159'] for x in _f]
F['brf_csprng'] = [BRF[x]['csprng'] for x in _f]
F['brf_cap'] = [BRF[x]['serial_cap'] for x in _f]
print(u'3 BR三面:', json.dumps(BRF))
assert BRF['layout']['n159'] == BRF['raw']['n159'] == BRF['pypdf']['n159'] > 0

# ---------- 4. 判词针四档(逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 重叠档) ----------
NEEDLES = [
    u'The serial number is an integer assigned by the CA to each certificate',
    u'The serial number MUST be a positive integer assigned by the CA',
    u'the issuer name and serial number identify a unique certificate',
    u'CAs MUST force the serialNumber to be a non-negative integer',
    u'Certificate users MUST be able to handle serialNumber values up to 20 octets',
    u'Conforming CAs MUST NOT use serialNumber values longer than 20 octets',
    u'Conformant CAs MUST NOT use serialNumber values longer than 20 octets',
    u'that are negative or zero',
    u'that are negative, or zero',
    u'Certificate users SHOULD be prepared to gracefully handle such certificates',
    u'the sign bit in the DER encoding of the INTEGER value MUST be zero',
    u'This can be done by adding a leading (leftmost) ',
    u'ub-serial-number INTEGER ::= 64',
    u'As a minimum, 16 octets',
    u'monotonically increasing sequence number',
    u'cRLNumber values longer than 20 octets',
    u'the construct "positiveint ::= INTEGER',
    u'MUST be a non-sequential number greater than zero (0) and less than 2\u00b9\u2075\u2079',
    u'containing at least 64 bits of output from a CSPRNG',
    u'byte-for-byte identical to the serialNumber',
    u'serial numbers encoded in DER as 8 bytes can be at most 63 bits long',
    u'Encoding a 64-bit positive serial number requires a 9-byte encoded value',
    u'02 09 00 80 00 00 00 00 00 00 01',
    u'RFC 5280 requires that serial numbers be positive',
]
NK = [pnorm(z) for z in NEEDLES]
LOW = [pnorm(T[i]) for i in range(NSRC)]
SHP = [pnorm(NL.join([x for x in L[i] if not shell_shape(x, i)])) for i in range(NSRC)]
F['needle_n'] = len(NEEDLES)
F['role_line'] = [[sum(1 for x in L[i] if NK[k] in pnorm(x)) for i in range(NSRC)] for k in range(len(NK))]
F['role_fold'] = [[cnt_re(LOW[i], NK[k]) for i in range(NSRC)] for k in range(len(NK))]
F['role_sh'] = [[cnt_re(SHP[i], NK[k]) for i in range(NSRC)] for k in range(len(NK))]
F['role_ovl'] = [[cnt_ovl(SHP[i], NK[k]) for i in range(NSRC)] for k in range(len(NK))]
F['needles3'] = [[[F['role_line'][k][i], F['role_fold'][k][i], F['role_sh'][k][i]]
                  for i in range(NSRC)] for k in range(len(NK))]
F['needle_src'] = [[LBL[i] for i in range(NSRC) if F['role_sh'][k][i] > 0] for k in range(len(NK))]
F['ob_wrap'] = [[F['role_fold'][k][i] - F['role_line'][k][i] for i in range(NSRC)] for k in range(len(NK))]
F['ovl_eq_fold'] = sum([abs(F['role_ovl'][k][i] - F['role_sh'][k][i])
                        for k in range(len(NK)) for i in range(NSRC)])
print(u'4 针四档: 行', [sum(F['role_line'][k][i] for k in range(len(NK))) for i in range(NSRC)],
      u'折', [sum(F['role_fold'][k][i] for k in range(len(NK))) for i in range(NSRC)],
      u'壳', [sum(F['role_sh'][k][i] for k in range(len(NK))) for i in range(NSRC)])

# ---------- 5. 关键句行号(供锚): 累积长度表 + bisect ----------
PINL = []
for k in range(len(NK)):
    for i in range(NSRC):
        if F['role_sh'][k][i] > 0:
            a = find_line_b(i, NEEDLES[k])
            assert a >= 0, (NEEDLES[k], i)
            PINL.append([LBL[i], NEEDLES[k], a + 1, k])
F['pin_lines'] = PINL
print(u'5 锚定行 %d 条' % len(PINL))

# ---------- 6. 词族账: 三把尺(子串 ⇎ 布尔表词界 ⇎ 断言正则词界) ----------
FAMS = [u'octet', u'octets', u'byte', u'bytes', u'hex', u'hexadecimal',
        u'positive', u'non-negative', u'negitive', u'negative', u'zero',
        u'CSPRNG', u'entropy', u'random', u'sequential', u'non-sequential',
        u'unique', u'serialNumber', u'serial number', u'serialNumber values',
        u'20 octets', u'64 bits', u'63 bits', u'159', u'160', u'64',
        u'2\u00b9\u2075\u2079', u'positiveint', u'MUST be able to handle',
        u'Conformant', u'Conforming']
WBK = [u'digit' if re.match(u'^[0-9]', w) else u'alpha' for w in FAMS]
_tabs_low = [_tabs(LOW[i]) for i in range(NSRC)]
F['fam_sub'] = [[cnt_re(LOW[i], pnorm(w)) for w in FAMS] for i in range(NSRC)]
F['fam_ub'] = [[ub_tab(LOW[i], pnorm(w), _tabs_low[i], WBK[k]) for k, w in enumerate(FAMS)]
               for i in range(NSRC)]
F['fam_ub_re'] = [[ub_re(LOW[i], pnorm(w), WBK[k]) for k, w in enumerate(FAMS)] for i in range(NSRC)]
F['fam_ub_cur'] = [[ub_cur(LOW[i], pnorm(w), WBK[k]) for k, w in enumerate(FAMS)] for i in range(NSRC)]
F['fam_ruler_diff'] = sum([1 for i in range(NSRC) for k in range(len(FAMS))
                           if not (F['fam_ub'][i][k] == F['fam_ub_re'][i][k] == F['fam_ub_cur'][i][k])])
F['fam_wrap'] = [F['fam_sub'][i][k] - F['fam_ub'][i][k] for i in range(NSRC) for k in range(len(FAMS))]
WIDEST = []
for w in [u'20 octets', u'positive', u'ub-serial-number', u'64 bits']:
    q = pnorm(w)
    WIDEST.append([cnt_re(LOW[i], q) for i in range(NSRC)])
F['widest'] = WIDEST
print(u'6 词族: 三轨分歧', F['fam_ruler_diff'], u' 最宽档', json.dumps(WIDEST))
assert WIDEST[0][0] == 0, u'2459 里 20 octets 并非零命中——判词要改'

# ---------- 7. §4.1.2.2 三代正文块: 逐字符句界 ⇎ Counter 直方图 ----------


def block_b(i, a_nd, b_nd):
    a = find_line_b(i, a_nd)
    b = find_line_b(i, b_nd, a + 1)
    assert a >= 0 and b > a, (a_nd, b_nd, a, b)
    return NL.join([x for x in L[i][a:b] if not shell_shape(x, i)])


from collections import Counter

BLK = [block_b(i, u'The serial number', u'4.1.2.3') if i <= 2 else None for i in range(NSRC)]
S = [sents_char(b) if b is not None else [] for b in BLK]
S_R = [sents_re(b) if b is not None else [] for b in BLK]
F['sec_sents'] = [len(s) for s in S]
F['sec_ruler_same'] = 1 if S == S_R else 0
C2459, C3280, C5280 = Counter(S[0]), Counter(S[1]), Counter(S[2])
F['sec_2459_in_3280'] = sum(min(C2459[z], C3280[z]) for z in C2459)
F['sec_3280_5280_same'] = sum(min(C3280[z], C5280[z]) for z in C3280)
F['sec_5280_new'] = len([z for z in S[2] if z not in C3280])
F['sec_3280_dropped'] = len([z for z in S[1] if z not in C5280])
print(u'7 句集:', F['sec_sents'], u'两把句界尺同列', F['sec_ruler_same'],
      u'2459∩3280', F['sec_2459_in_3280'], u'3280∩5280', F['sec_3280_5280_same'],
      u'5280新句', F['sec_5280_new'], u'3280被删句', F['sec_3280_dropped'])

# ---------- 8. DER 样例(值,内容长)对: token 判形 ⇎ 正则选择支 ⇎ 逐次右移 ----------
RXD = re.compile(u'^\\s*\\d+\\s+(\\d+):\\s+INTEGER (\\d+)\\s*$')


def der_pairs_token(lines):
    out = []
    for x in lines:
        t = x.split()
        if len(t) != 4 or not t[0].isdigit():
            continue
        if not (t[1].endswith(u':') and t[1][:-1].isdigit()):
            continue
        if t[2] != u'INTEGER' or not t[3].isdigit():
            continue
        out.append((int(t[3]), int(t[1][:-1])))
    return out


PAIRS = [der_pairs_token(L[i]) for i in range(NSRC)]
PAIRS_R = [[(int(m.group(2)), int(m.group(1))) for m in (RXD.match(x) for x in L[i]) if m]
           for i in range(NSRC)]
F['der_pairs'] = PAIRS
F['der_pairs_ruler_same'] = 1 if PAIRS == PAIRS_R else 0


def der_len(v):
    """采集侧那一把: bit_length 闭式, 高位成 1 补一枚 00。"""
    if v < 0:
        raise ValueError
    bl = v.bit_length()
    n = (bl + 7) // 8
    if bl and bl % 8 == 0:
        n += 1
    return max(n, 1)


def der_len_shift(v):
    """本遍那一把: 逐次右移数比特, 再算字节并照 sign bit 规矩补 00。"""
    bl, w = 0, v
    while w > 0:
        bl += 1
        w >>= 1
    n = bl // 8 + (1 if bl % 8 else 0)
    n += 1 if (bl and bl % 8 == 0) else 0
    return max(n, 1)


BADP = [(LBL[i], v, l, der_len_shift(v)) for i in range(NSRC) for (v, l) in PAIRS[i]
        if der_len_shift(v) != l]
F['der_pair_fail'] = len(BADP)
BADP2 = sum(1 for i in range(NSRC) for (v, _l) in PAIRS[i] if der_len(v) != der_len_shift(v))
F['der_ruler_diff'] = BADP2
F['der_159'] = der_len_shift(2 ** 159 - 1)
F['der_160'] = der_len_shift(2 ** 160 - 1)
F['der_63'] = der_len_shift(2 ** 63 - 1)
F['der_63p1'] = der_len_shift(2 ** 63 + 1)
F['der_pair_n'] = [len(x) for x in PAIRS]
print(u'8 DER: 两轨同表', F['der_pairs_ruler_same'], u'闭式⇎右移分歧', F['der_ruler_diff'],
      u' 样例对', F['der_pair_n'], u' 边界', F['der_159'], F['der_160'], F['der_63'], F['der_63p1'])
assert F['der_pairs_ruler_same'] == 1 and not BADP

# ---------- 9. LE 九字节实例: 逐字符收 hex 对 ⇎ split+join 切片 ----------
i0 = T[4].find(u'02 09 00 80 00 00 00 00 00 00 01')
assert i0 >= 0
_hx, _k, _pairs = [], i0, 0
while _k < len(T[4]) and _pairs < 11:
    if T[4][_k] == u' ' and _hx and len(_hx[-1]) == 2:
        _hx.append(u'')
    if T[4][_k] in u'0123456789abcdefABCDEF':
        if not _hx:
            _hx.append(u'')
        _hx[-1] += T[4][_k]
        if len(_hx[-1]) == 2:
            _pairs += 1
    if T[4][_k] == NL and _hx and len(_hx[-1]) < 2:
        break
    _k += 1
F['le_hex'] = u''.join(_hx)
F['le_hex_len_octet'] = int(F['le_hex'][2:4], 16)
F['le_hex_val'] = str(int(F['le_hex'][4:4 + 2 * 9], 16))
F['le_hex_is2'] = 1 if F['le_hex'][:2] == u'02' else 0
F['le_sup_shell'] = cnt_re(HT, u'<sup>63</sup>')
F['le_sup_stripped'] = cnt_re(pnorm(ST), u'value 2 63')
F['le_sup_fold'] = cnt_re(pnorm(ST), u'2 63 +1')
print(u'9 LE十六进制:', F['le_hex'], F['le_hex_val'], u' 长度字节', F['le_hex_len_octet'])
assert len(F['le_hex']) == 22 and F['le_hex'].isdigit()

# ---------- 10. BR serialNumber 行: 标题清单一次建好, 行号 bisect 归属 ----------
def sub_in(hay, nd):
    """逐字符滑窗判含(采集侧是 in 运算符): 定义同, 机制换。"""
    n, m = len(nd), len(hay)
    if n == 0 or n > m:
        return False
    k = 0
    while k + n <= m:
        t = 0
        while t < n and hay[k + t] == nd[t]:
            t += 1
        if t == n:
            return True
        k += 1
    return False


HDRS = []
for k, x in enumerate(L[3]):
    t = x.strip()
    if not t:
        continue
    w0 = t.split(u' ', 1)[0]
    if w0.startswith(u'7.1.2.') and w0[6:].isdigit() and len(t) > len(w0) and t[len(w0)] == u' ':
        HDRS.append((k, t[:36]))


def sec_of(row):
    lo, hi = 0, len(HDRS) - 1
    ans = u'?'
    while lo <= hi:
        mid = (lo + hi) // 2
        if HDRS[mid][0] <= row:
            ans = HDRS[mid][1]
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


CAP = u'MUST be a non-sequential number greater than zero (0) and less than 2\u00b9\u2075\u2079'
FULLBFB = u'byte-for-byte identical to the serialNumber'
SHORTBFB = u'byte-for-byte'
brrows = []
for k, x in enumerate(L[3]):
    isc = sub_in(x, CAP)
    if isc or sub_in(x, FULLBFB):
        brrows.append([k + 1, 1 if isc else 0, 1 if sub_in(x, SHORTBFB) else 0, sec_of(k)])
F['br_rows'] = brrows
F['br_cap_rows'] = len([r for r in brrows if r[1] == 1])
F['br_bfb_rows'] = len([r for r in brrows if r[2] == 1])
F['br_cap_secs'] = [r[3] for r in brrows if r[1] == 1]
F['br_bfb_secs'] = [r[3] for r in brrows if r[2] == 1]
F['br_hdr_n'] = len(HDRS)
print(u'10 BR 行: cap', F['br_cap_rows'], u'bfb', F['br_bfb_rows'], u'标题清单', F['br_hdr_n'])
assert F['br_cap_rows'] == 8 and len(set(F['br_cap_secs'])) == 8

# ---------- 11. 义务词账(行内尺 ⇎ 折平尺) ----------
OBW = [u'MUST', u'MUST NOT', u'SHOULD', u'MAY', u'SHALL']
_tabs_line = [[_tabs(x) for x in L[i]] for i in range(NSRC)]
F['ob_line'] = [[sum([ub_tab(x, w, _tabs_line[i][k], u'alpha')
                      for k, x in enumerate(L[i])]) for w in OBW] for i in range(NSRC)]
F['ob_fold'] = [[ub_tab(LOW[i], w.lower(), _tabs_low[i], u'alpha') for w in OBW] for i in range(NSRC)]
F['ob_wrap2'] = [F['ob_fold'][i][k] - F['ob_line'][i][k] for i in range(NSRC) for k in range(5)]
print(u'11 义务词 行/折:', F['ob_line'], F['ob_fold'])

# ---------- 12. ub-serial-number 上限值: 两条正则级联剥前缀 ⇎ 采集侧整枚针 ----------
_pre1 = re.compile(u'^.*ub-serial-number INTEGER[ ]*::=[ ]*', re.S)
_pre2 = re.compile(u'[^0-9].*$')
UBV = []
for i in range(NSRC):
    v = None
    for x in L[i]:
        if u'ub-serial-number' in x:
            t = _pre2.sub(u'', _pre1.sub(u'', x.strip()))
            if t.isdigit():
                v = int(t)
    UBV.append(v)
F['ub_serial_vals'] = UBV
F['ub_serial_n'] = [len([x for x in L[i] if u'ub-serial-number' in x]) for i in range(NSRC)]
print(u'12 ub-serial-number:', UBV, u' 行种', F['ub_serial_n'])
assert UBV[1] == 64 and UBV[2] == 64 and UBV[0] is None

# --- PICK BEGIN --- (与采集遍逐键对账: 同一把定义, 第二套实现)
PK = json.load(io.open(u'corpus/_b95meas.json', encoding='utf-8'))
PAIRK = [
    (u'bytes', u'bytes'), (u'chars', u'chars'), (u'n_lf', u'n_lf'), (u'n_cr', u'n_cr'),
    (u'splitlines', u'splitlines'), (u'splitnl', u'splitnl'), (u'ff', u'ff'),
    (u'blank', u'blank'), (u'maxlen', u'maxlen'), (u'tab', u'tab'), (u'bom', u'bom'),
    (u'other_bounds', u'other_bounds'), (u'trail_bound', u'trail_bound'),
    (u'na_codepoints', u'nonascii'),
    (u'foot_page', u'foot_page'), (u'hdr_rfc', u'hdr_rfc'), (u'ietf_alone', u'ietf_alone'),
    (u'br_pgnum', u'br_pgnum'), (u'ff_led', u'ff_led'), (u'shell_lines', u'shell_lines'),
    (u'page_pair_gap', u'page_pair_gap'),
    (u'le_tags', u'le_tags'), (u'le_entities', u'le_entities'),
    (u'le_html_chars', u'le_html_chars'), (u'le_stripped_chars', u'le_stripped_chars'),
    (u'le_drop', u'le_drop'),
    (u'br_faces', u'br_faces'),
    (u'needle_src', u'needle_src'), (u'ob_wrap', u'ob_wrap'),
    (u'pin_lines', u'pin_lines'),
    (u'fam_sub', u'fam_sub'), (u'fam_ub', u'fam_ub'), (u'fam_wrap', u'fam_wrap'),
    (u'widest', u'widest'),
    (u'sec_sents', u'sec_sents'), (u'sec_2459_in_3280', u'sec_2459_in_3280'),
    (u'sec_3280_5280_same', u'sec_3280_5280_same'), (u'sec_5280_new', u'sec_5280_new'),
    (u'sec_3280_dropped', u'sec_3280_dropped'),
    (u'der_pairs', u'der_pairs'), (u'der_pair_fail', u'der_pair_fail'),
    (u'der_159', u'der_159'), (u'der_160', u'der_160'), (u'der_63', u'der_63'),
    (u'der_63p1', u'der_63p1'),
    (u'le_hex', u'le_hex'), (u'le_hex_val', u'le_hex_val'), (u'le_hex_len_octet', u'le_hex_len_octet'),
    (u'le_sup_shell', u'le_sup_shell'), (u'le_sup_stripped', u'le_sup_stripped'),
    (u'le_sup_fold', u'le_sup_fold'),
    (u'br_rows', u'br_rows'), (u'br_cap_rows', u'br_cap_rows'), (u'br_bfb_rows', u'br_bfb_rows'),
    (u'br_cap_secs', u'br_cap_secs'), (u'br_bfb_secs', u'br_bfb_secs'),
    (u'ob_line', u'ob_line'), (u'ob_fold', u'ob_fold'), (u'ob_wrap2', u'ob_wrap2'),
]
AGREE, DIFFK = [], []
for mk_k, pk_k in PAIRK:
    if mk_k not in F or pk_k not in PK:
        DIFFK.append(mk_k + u'?' + pk_k)
        continue
    a, b = F[mk_k], PK[pk_k]
    if mk_k in (u'der_pairs', u'br_rows'):
        a = [list(map(list, x)) if mk_k == u'der_pairs' else x for x in a]
        if mk_k == u'der_pairs':
            a = [[list(z) for z in x] for x in a]
    (AGREE if a == b else DIFFK).append(mk_k)
N3D = []
for k in range(min(len(F['needles3']), len(PK[u'needles3']))):
    for i in range(NSRC):
        for t in range(3):
            if F['needles3'][k][i][t] != PK[u'needles3'][k][i][t]:
                N3D.append([k, NEEDLES[k][:22], LBL[i], t, F['needles3'][k][i][t],
                            PK[u'needles3'][k][i][t]])
F['n3_diff'] = N3D
(AGREE if F['needles3'] == PK[u'needles3'] else DIFFK).append(u'needles3')
F['pick_agree'] = len(AGREE)
F['pick_diff'] = len(DIFFK)
F['pick_diffk'] = sorted(DIFFK)
F['pick_pairs'] = len(PAIRK) + 1
print(u'PICK 对账: %d 键符 ⇎ %d 键不符 %s ｜ needles3 逐格不符 %d' % (
      F['pick_agree'], F['pick_diff'], sorted(DIFFK), len(N3D)))
if N3D:
    print(u'   needles3 不符(针, 份, 档, 本遍, 采集):', N3D[:6])
# --- PICK END ---

# ---------- 布尔门(每道都能失败) ----------
G = []
G.append((u'字节两把尺同值', F['bytes'] == F['bytes_stat']))
G.append((u'最长行两把尺同值', F['maxlen'] == F['maxlen_scan']))
G.append((u'行式对账逐份平', F['rows_ledger_diff'] == [0] * NSRC))
G.append((u'换行两把尺同值', F['splitnl'] == [F['n_lf'][i] + 1 for i in range(NSRC)]
                            and F['line_split_ledger'] == [0] * NSRC))
G.append((u'BR 是全份 CRLF 面而四份纯 LF', F['n_cr'][3] == F['n_lf'][3]
                                          and sum(F['n_cr'][j] for j in [0, 1, 2, 4]) == 0))
G.append((u'壳谓词两把尺逐行同集', F['shell_pred_diff'] == [0] * NSRC))
G.append((u'壳账容斥闭合', F['shell_ledger'] == [0] * NSRC))
G.append((u'剥壳正文+壳行=总行', F['body_lines'] == [F['splitnl'][i] - F['shell_lines'][i]
                                                    for i in range(NSRC)]))
G.append((u'页壳世代: 三份 RFC 页码页脚成对差一, BR 走 pg.',
          F['page_pair_gap'][:3] == [1, 1, 1] and F['foot_page'][3] == 0 and F['br_pgnum'][3] > 100))
G.append((u'重叠档与不重叠档逐格同数', F['ovl_eq_fold'] == 0))
G.append((u'词族三轨逐枚同数', F['fam_ruler_diff'] == 0))
G.append((u'2459 撤了长度尺: 20 octets 最宽档 0 命中',
          F['widest'][0] == [0, 8, 8, 0, 0]))
G.append((u'Conformant 只在 3280 活着', F['fam_sub'][1][FAMS.index(u'Conformant')] == 6
                                        and F['fam_sub'][2][FAMS.index(u'Conformant')] == 0))
G.append((u'positive 词界尺: 2459 只剩 positiveint',
          [F['fam_ub'][i][FAMS.index(u'positive')] for i in range(NSRC)] == [0, 1, 1, 0, 4]
          and [F['fam_ub'][i][FAMS.index(u'positiveint')] for i in range(NSRC)] == [2, 2, 0, 0, 0]))
G.append((u'六十四比特的尺只在 BR: 64 bits 逐份 [0,0,0,10,0]',
          F['fam_sub'][3][FAMS.index(u'64 bits')] == 10 and sum(F['fam_sub'][i][FAMS.index(u'64 bits')]
                                                                for i in [0, 1, 2, 4]) == 0))
G.append((u'2¹⁵⁹ 三面九枚 ⇎ 值域句八枚: csprng 比 cap 多的恰是旧句',
          F['brf_n159'] == [9, 9, 9] and F['brf_cap'] == [8, 8, 8]
          and F['brf_csprng'] == [11, 11, 11] and F['br_cap_rows'] == 8))
G.append((u'两把句界尺逐句同列表', F['sec_ruler_same'] == 1))
G.append((u'三代句数 2⇎8⇎8 且新句+删句闭合',
          F['sec_sents'][:3] == [2, 8, 8]
          and F['sec_3280_5280_same'] + F['sec_3280_dropped'] == F['sec_sents'][1]
          and F['sec_3280_5280_same'] + F['sec_5280_new'] == F['sec_sents'][2]))
G.append((u'DER 样例只在 5280 印出且两轨同表',
          F['der_pairs_ruler_same'] == 1 and [x > 0 for x in F['der_pair_n']] == [False, False, True, False, False]))
G.append((u'样例与闭式⇎右移两把尺全对', F['der_pair_fail'] == 0 and F['der_ruler_diff'] == 0))
G.append((u'DER 边界: 2^159-1→20 ⇎ 2^160-1→21 ⇎ 2^63-1→8 ⇎ 2^63+1→9',
          [F['der_159'], F['der_160'], F['der_63'], F['der_63p1']] == [20, 21, 8, 9]))
G.append((u'LE 实例回收: 02 09 起头 ⇎ 长度字节 9 ⇎ 值恰 2^63+1',
          F['le_hex_is2'] == 1 and F['le_hex_len_octet'] == 9
          and int(F['le_hex_val']) == 2 ** 63 + 1))
G.append((u'BR 八行值域句各属不同节 ⇎ byte-for-byte 三行 = 两行 precert + 一行 CRL',
          F['br_cap_rows'] == 8 and len(set(F['br_cap_secs'])) == 8
          and F['br_bfb_secs'].count(u'7.1.2.9 Precertificate Profile') == 2
          and F['br_bfb_secs'].count(u'7.1.2.11 Common Certificate Fields') == 1))
G.append((u'ub-serial-number 的 64 只在 3280/5280 印出',
          F['ub_serial_vals'] == [None, 64, 64, None, None]))
G.append((u'LE 壳比剥壳面长且吃掉的是壳', F['le_drop'] == F['le_html_chars'] - F['le_stripped_chars']
                                         and F['le_tags'] > 100 and F['le_entities'] > 100))
G.append((u'制表符只在内核侧那一份的 HTML 里', F['tab'][4] > 0 and sum(F['tab'][:4]) == 0))
G.append((u'与采集遍逐键对账无不符', F['pick_diff'] == 0 and F['n3_diff'] == []))
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


Z(u"sum(F['rows_ledger_diff'])", u'行式对账: splitlines−split(\\n) = 界符合计−尾界符, 逐份相减')
Z(u"sum(F['byte_cp_ledger']) - sum(F['utf8_extra'])", u'字节 − 码位 = 非 ASCII 字符按 UTF-8 多出的字节(逐枚现编码相加)')
Z(u"sum(F['line_split_ledger'])", u'总行 = 非空行 + 空行, 逐份相减')
Z(u"sum(F['shell_ledger'])", u'壳账容斥: 壳行 = 六形之和 − 重数(逐枚重扫)')
Z(u"F['le_html_chars'] - F['le_stripped_chars'] - F['le_drop']", u'LE 壳面 − 剥壳面 = 吃掉的字符')
Z(u"F['pick_pairs'] - F['pick_agree'] - F['pick_diff']", u'对账: 键对相加 = 符+不符')
Z(u"len(F['pin_lines']) - sum(len([t for t in F['role_sh'][k] if t != 0]) for k in range(F['needle_n']))",
  u'锚行条目数 = 摘壳档非零针格数(两路各自数出)')
Z(u"sum(F['fam_wrap']) - (sum([sum(F['fam_sub'][i]) for i in range(5)]) - sum([sum(F['fam_ub'][i]) for i in range(5)]))",
  u'子串尺比词界尺多读的枚数 = 两尺总量之差')
Z(u"sum(F['ob_wrap2']) - (sum([sum(F['ob_fold'][i]) for i in range(5)]) - sum([sum(F['ob_line'][i]) for i in range(5)]))",
  u'跨行涨量: 逐格相加 = 两档总量之差')
Z(u"F['sec_3280_5280_same'] + F['sec_5280_new'] - F['sec_sents'][2]", u'5280 的句 = 与 3280 同句 + 新句')
Z(u"F['sec_3280_5280_same'] + F['sec_3280_dropped'] - F['sec_sents'][1]", u'3280 的句 = 与 5280 同句 + 被删句')
Z(u"F['br_cap_rows'] + F['br_bfb_rows'] - len(F['br_rows'])", u'BR 行账: 值域句 + byte-for-byte = 收进行')
Z(u"F['der_pair_n'][2] - sum([len(x) for x in F['der_pairs']])", u'DER 样例对总数全在 5280 一档')
Z(u"F['der_159'] * 8 - 1 - 159", u'尺的互译: 20 字节的上界整数值恰是 2^159−1(20×8−1 位)')
Z(u"F['der_63p1'] - F['der_63'] - 1", u'64 位正数比 63 位正数多一枚前导 00')
Z(u"F['der_159'] * 8 - F['der_63'] * 8 - 96", u'跨文书同尺换算: BR 上界 159 位 ⇎ LE 的 63 位, 位差 96 = (20−8)字节×8')
Z(u"F['der_160'] - F['der_159'] - 1", u'越界一枚: 2^160−1 比 2^159−1 多一枚内容字节')
Z(u"len(F['le_hex']) - 4 - 2 * F['le_hex_len_octet']", u'十六进制串长 = tag 2 字符 + 长度字节 2 字符 + 内容每字节 2 字符')
Z(u"F['brf_n159'][0] - F['brf_cap'][0] - 1", u'BR 面上 2¹⁵⁹ 九枚 − 值域句八枚 = 旧句那枚(9−8−1)')
Z(u"F['bool_green'] - F['bool_all_n']", u'布尔门全绿')
for e, w in ZID:
    v = eval(e, {u'F': F, u'range': range, u'sum': sum, u'len': len, u'max': max, u'abs': abs})
    if v != 0:
        print(u'ZID 不平: %s ⇒ %s' % (w, v))
        raise SystemExit(1)
print(u'恒等式 %d 条全平' % len(ZID))
F['zid_scan_n'] = len(ZID)
F['scan_key_n'] = len(F)
# --- SCAN END --- (以上由 _wire95.py 机械切进 _b95_scan; 以下为建条目侧登记与发射)

BB95 = lambda name, i=None: (F[name] if i is None else F[name][i])


def _ev(e):
    return eval(e, {u'B95V': BB95, u'NSRC': NSRC, u'range': range, u'F': F, u'len': len, u'sum': sum})


FN = u'B95V'
_to_v = re.compile(r"(?:F)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B95V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
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
    if eval(v, {FN: BB95, u'range': range, u'sum': sum, u'len': len, u'max': max, u'abs': abs}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))
    reg(str(_ev(e)), v, w)


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB95}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([str(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


for k, v in dump_deriv().items():
    DER[k] = v

# 把对账结果写回采集遍的读数档(口径一致的键集, 逐键对账在此落盘)
PK[u'pick_agree'] = F['pick_agree']
PK[u'pick_diff'] = F['pick_diff']
PK[u'pick_diffk'] = F['pick_diffk']
PK[u'pick_pairs'] = F['pick_pairs']
PK[u'n3_diff'] = F['n3_diff']
PK[u'pick_from'] = u'corpus/_mkB95.py'
json.dump(PK, io.open(u'corpus/_b95meas.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)

print(u'第二遍量测完成: 扁平键 %d ⇎ 恒等式 %d 全平 ⇎ 布尔门 %d 全绿 ⇎ 针 %d ⇎ 对账 %d 符 %d 不符 ⇎ 已写回 _b95meas.json'
      % (len(F), len(ZID), F['bool_all_n'], F['needle_n'], F['pick_agree'], F['pick_diff']))
io.open(u'corpus/_b95flat.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True))

exec(io.open(u'corpus/_mk95emit.py', encoding='utf-8').read())
