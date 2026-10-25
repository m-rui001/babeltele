# -*- coding: utf-8 -*-
"""采集遍(B95, 第一套实现·机制族A): “X.509 证书序列号到底能有多长、什么算违规”
交五份一手文书各答一遍——
2459(1998 PKIX 初版: 序列号只写 "an integer assigned by the CA" + 唯一性, 符号与长度一枚数都不给;
  它的 ASN.1 备忘里有 16 octets 字样却只管目录属性的字符串上限)
⇎ 3280(2002: 补上 "MUST be a positive integer" ⇎ "MUST force ... non-negative" ⇎ 20 octets 双句,
  Note 里作 negative, or zero(带逗号), 全篇还有 4 处 Conformant——本族自己都没写齐的拼法)
⇎ 5280(2008: 与 3280 同文而删尽 Conformant(0 处), Note 去逗号作 negative or zero;
  附录 B 给出尺的 DER 侧写法: sign bit MUST be zero, 必要时补一枚前导 00'H octet;
  目录属性上限 ub-serial-number ::= 64(64 的第三种尺: 字符数)与“16 octets, or twice the specified
  upper bound”备忘; §7.1 样例把 17/18/256 三枚序列号连 DER 内容长度一并印出)
⇎ CA/B TLS BR v2.0.2(2023 世代: 把尺子整个换成值域——serialNumber 行三处印
  "non-sequential number greater than zero (0) and less than 2¹⁵⁹ containing at least 64 bits of output
  from a CSPRNG", 变更表里另有 Ballot 156 的旧句(无 2¹⁵⁹ 只有 64 bits); 2¹⁵⁹ 的上标在 pdftotext 默认档里
  丢字, 换 UTF-8 档三张面(layout ⇎ raw ⇎ pypdf)才收齐)
⇎ Let's Encrypt《A Warm Welcome to ASN.1 and DER》(实现侧一手说明: 8 字节的 DER 序列号最多 63 位,
  64 位正数要 9 字节(首字节补 0), 并印出 2^63+1 的九字节编码 02 09 00 80 00 00 00 00 00 00 01;
  原文是 HTML, 上标在壳内作 2<sup>63</sup>, 剥壳档里散作 2 63)。
三把尺: 字节数(20 octets) ⇎ 十六进制/字符数(ub-serial-number 64 字符) ⇎ 比特熵(64 bits 下限 ⇎ 159 位上限);
边界组: 20 ⇎ 9 ⇎ 8 ⇎ 1 字节(最小编码那类); 谁有权拒: 5280 叫用户 MUST be able to handle ⇎ 叫 CA MUST NOT 发
⇎ Note 叫用户 SHOULD be prepared to gracefully handle negative or zero ⇎ BR 只束 CA。

机制族A(本遍): 游标 find 环数针、邻居字符手扫判词界、整行序列正则判壳、4 行滑窗在折平面定位行号、
(?<=[.!?]) 正则切句、一条选择支正则抽(值,DER长度)对、一条正则直读上限值、块定界用节标题针、
集合 & 求同文句、2 的幂闭式算 DER 长度。建条目侧(_mkB95.py 的 SCAN)换机制不换定义逐键对账, 结果写回本文件。
所有正文数字由本遍量出后落 JSON, 一枚都不手打。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'2459', u'3280', u'5280', u'br', u'le']
SRC = [u'corpus/raw/serialLen/rfc2459.txt', u'corpus/raw/serialLen/rfc3280.txt',
       u'corpus/raw/serialLen/rfc5280.txt', u'corpus/raw/serialLen/br_v202.layout.txt',
       u'corpus/raw/serialLen/le_asn1_der.html']
YR = [1998, 2002, 2008, 2023, 2021]
NSRC = 5
M = {}


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in SRC]
T = [b.decode('utf-8', 'replace') for b in B]
RAWL = [t.split(NL) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]


def pnorm(s):
    return u' '.join(s.lower().split())


def cnt_cur(hay, nd):
    """机制A·游标 find 环: 数不重叠出现。"""
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def ub(s, w, kind=u'alpha'):
    """机制A·整词尺: 邻居字符手扫(两侧都不是字母 alpha ⇎ 都不是数字 digit ⇎ 都不是字母数字 alnum)。"""
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


def foldmap(txt):
    """折平面 + (面偏移→原行) 区间表: 只数非空白字符, 段间一枚空格。"""
    lines = txt.split(NL)
    offs, pos, seg = [], 0, []
    for i, l in enumerate(lines):
        c = pnorm(l)
        if not c:
            continue
        offs.append((pos, pos + len(c), i))
        seg.append(c)
        pos += len(c) + 1
    face = u' '.join(seg)
    assert len(face) == (pos - 1 if pos else 0), (len(face), pos)
    return face, offs


def line_of_face(offs, s0):
    cand = [o[2] for o in offs if o[0] <= s0]
    return cand[-1] if cand else None


def find_line(i, nd, a0=0):
    """机制A·4 行滑窗: 折平 needle 在多行窗口里试, 返回 needle 起点所在原行(0-based), 找不到回 -1。"""
    q = pnorm(nd)
    head = q[:min(20, len(q))]
    for a in range(a0, len(L[i])):
        win = NL.join(L[i][a:a + 4])
        if head not in pnorm(win):
            continue
        face, offs = foldmap(win)
        s0 = face.find(q)
        if s0 >= 0:
            return a + line_of_face(offs, s0)
    return -1


# ---------- 0. 面量 ----------
M['bytes'] = [len(B[i]) for i in range(NSRC)]
M['chars'] = [len(T[i]) for i in range(NSRC)]
M['n_lf'] = [cnt_cur(T[i], NL) for i in range(NSRC)]
M['n_cr'] = [cnt_cur(T[i], u'\r') for i in range(NSRC)]
M['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
M['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
M['ff'] = [cnt_cur(T[i], u'\x0c') for i in range(NSRC)]
M['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
M['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
M['nonascii'] = [sorted(set(ord(c) for c in T[i] if ord(c) > 127)) for i in range(NSRC)]
M['bom'] = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
M['tab'] = [cnt_cur(T[i], u'\t') for i in range(NSRC)]
BDSET = u'\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029\r'
OTHB = [[cnt_cur(T[i], c) for c in BDSET if c != u'\r'] for i in range(NSRC)]
M['other_bounds'] = OTHB
M['other_names'] = [c for c in BDSET if c != u'\r']
TB = [1 if T[i][-1:] in (NL + BDSET) else 0 for i in range(NSRC)]
M['trail_bound'] = TB
OBS = [M['splitlines'][i] - M['splitnl'][i] for i in range(NSRC)]
PRE = [sum(OTHB[i]) - TB[i] for i in range(NSRC)]
print(u'0 行式对账 splitlines−splitnl =', OBS, u' 预测(界符和−尾界符) =', PRE)
assert OBS == PRE, u'行式对账不平'

# ---------- 1. 壳形: 页壳族 ⇎ 表壳族 ⇎ HTML壳 ----------
def foot(x):
    return re.search(u'\\[Page \\d+\\]', x) is not None


def hdr_rfc(x, i):
    return re.match(u'^RFC \\d{4} +\\S', x) is not None


def hdr_ieft(x):
    return re.match(u'^Internet Engineering Task Force\\s*$', x) is not None


def br_pg(x):
    return re.match(u'^\\s*pg\\. \\d+\\s*$', x) is not None


def ffline(x):
    return len(x) == 1 and ord(x[0]) == 12


M['foot_page'] = [len([x for x in L[i] if foot(x)]) for i in range(NSRC)]
M['hdr_rfc'] = [len([x for x in L[i] if hdr_rfc(x, i)]) for i in range(NSRC)]
M['ietf_alone'] = [len([x for x in L[i] if hdr_ieft(x)]) for i in range(NSRC)]
M['br_pgnum'] = [len([x for x in L[i] if br_pg(x)]) for i in range(NSRC)]
M['ff_led'] = [len([x for x in L[i] if ffline(x)]) for i in range(NSRC)]


def is_shell(x, i):
    if i <= 2:
        return foot(x) or hdr_rfc(x, i) or hdr_ieft(x) or ffline(x) or x.strip() == u''
    if i == 3:
        return br_pg(x) or ffline(x) or x.strip() == u''
    return False  # le 那份按整份壳面处理, 剥壳面单列


M['shell_lines'] = [len([x for x in L[i] if is_shell(x, i)]) for i in range(NSRC)]
print(u'1 壳账 [Page]=', M['foot_page'], u'RFC眉=', M['hdr_rfc'], u'pg.=', M['br_pgnum'],
      u'FF独占行=', M['ff_led'], u'壳行合计=', M['shell_lines'])
assert M['foot_page'][3] == 0 and M['foot_page'][4] == 0
assert M['br_pgnum'][3] > 0
# 老式页壳: 首页有页脚无眉行, 其后逐页成对
M['page_pair_gap'] = [M['foot_page'][i] - M['hdr_rfc'][i] for i in range(NSRC)]
for i in range(3):
    assert M['page_pair_gap'][i] == 1, i
assert 100 < M['br_pgnum'][3] < 129

# ---------- 2. LE HTML 壳面两档 ----------
HT = T[4]
M['le_tags'] = len(re.findall(u'<[a-zA-Z/!][^>]*>', HT))
M['le_entities'] = len(re.findall(u'&[a-zA-Z]+;|&#[0-9]+;', HT))
ST = io.open(u'corpus/raw/serialLen/le_asn1_der.txt', 'rb').read().decode('utf-8', 'replace')
M['le_html_chars'] = len(HT)
M['le_stripped_chars'] = len(ST)
M['le_drop'] = M['le_html_chars'] - M['le_stripped_chars']
print(u'2 LE壳: 标签', M['le_tags'], u'实体', M['le_entities'], u'壳面', M['le_html_chars'],
      u'剥壳面', M['le_stripped_chars'])
assert M['le_stripped_chars'] < M['le_html_chars']
assert M['le_tags'] > 100

# ---------- 3. BR 三张提取面(layout ⇎ raw ⇎ pypdf)的指数账 ----------
BRF = {}
for nm, p in [(u'layout', SRC[3]), (u'raw', u'corpus/raw/serialLen/br_v202.raw.txt'),
              (u'pypdf', u'corpus/raw/serialLen/br_v202.pypdf.txt')]:
    s = io.open(p, 'rb').read().decode('utf-8', 'replace')
    BRF[nm] = {
        'chars': len(s),
        'n159': cnt_cur(s, u'2\u00b9\u2075\u2079'),
        'n1': cnt_cur(s, u'2\u00b9'),
        'csprng': cnt_cur(s, u'CSPRNG'),
        'serial_cap': cnt_cur(pnorm(s), pnorm(u'greater than zero (0) and less than 2\u00b9\u2075\u2079')),
    }
M['br_faces'] = BRF
print(u'3 BR三面:', json.dumps(BRF))
assert BRF['layout']['n159'] == BRF['raw']['n159'] == BRF['pypdf']['n159'] > 0
assert BRF['layout']['n1'] == BRF['layout']['n159']  # 没有一枚 2¹ 不是 2¹⁵⁹ 的开头

# ---------- 4. 判词针三档(逐行 ⇎ 全篇折平 ⇎ 摘壳折平) ----------
NEEDLES = [
    u'The serial number is an integer assigned by the CA to each certificate',      # 2459 独有形
    u'The serial number MUST be a positive integer assigned by the CA',            # 3280/5280
    u'the issuer name and serial number identify a unique certificate',            # 三 RFC 同文
    u'CAs MUST force the serialNumber to be a non-negative integer',
    u'Certificate users MUST be able to handle serialNumber values up to 20 octets',
    u'Conforming CAs MUST NOT use serialNumber values longer than 20 octets',
    u'Conformant CAs MUST NOT use serialNumber values longer than 20 octets',       # 3280 拼法
    u'that are negative or zero',                                                   # 5280 无逗号
    u'that are negative, or zero',                                                  # 3280 带逗号
    u'Certificate users SHOULD be prepared to gracefully handle such certificates',
    u'the sign bit in the DER encoding of the INTEGER value MUST be zero',
    u'This can be done by adding a leading (leftmost) ',
    u'ub-serial-number INTEGER ::= 64',
    u'As a minimum, 16 octets',
    u'monotonically increasing sequence number',                                   # 2459 cRLNumber 的序数尺
    u'cRLNumber values longer than 20 octets',                                     # 3280/5280 换长度尺
    u'the construct "positiveint ::= INTEGER',                                      # 2459 唯一 positive 出处(ASN.1 注)
    u'MUST be a non-sequential number greater than zero (0) and less than 2\u00b9\u2075\u2079',  # BR 行
    u'containing at least 64 bits of output from a CSPRNG',
    u'byte-for-byte identical to the serialNumber',
    u'serial numbers encoded in DER as 8 bytes can be at most 63 bits long',        # LE
    u'Encoding a 64-bit positive serial number requires a 9-byte encoded value',    # LE
    u'02 09 00 80 00 00 00 00 00 00 01',                                            # LE 的九字节实例
    u'RFC 5280 requires that serial numbers be positive',                           # LE 引规范
]
FOL = [pnorm(T[i]) for i in range(NSRC)]
SHP = [pnorm(NL.join([x for x in L[i] if not is_shell(x, i)])) for i in range(NSRC)]
rows = []
for nd in NEEDLES:
    q = pnorm(nd)
    r = []
    for i in range(NSRC):
        cl = len([x for x in L[i] if q in pnorm(x)])
        cf = cnt_cur(FOL[i], q)
        cs = cnt_cur(SHP[i], q)
        r.append((cl, cf, cs))
    rows.append((nd, r))
    print(u'4 %-56s %s 源=%s' % (nd[:56], r, [LBL[i] for i in range(NSRC) if r[i][2] > 0]))
M['needles3'] = [list(z[1]) for z in rows]
M['needle_src'] = [[LBL[i] for i in range(NSRC) if z[1][i][2] > 0] for z in rows]
M['ob_wrap'] = [[rows[k][1][i][1] - rows[k][1][i][0] for i in range(NSRC)] for k in range(len(NEEDLES))]

# ---------- 5. 关键句行号(供锚) ----------
PINL = []
for k, (nd, r) in enumerate(rows):
    for i in range(NSRC):
        if r[i][2] > 0:
            a = find_line(i, nd)
            assert a >= 0, (nd, i)
            PINL.append([LBL[i], nd, a + 1, k])
M['pin_lines'] = PINL
print(u'5 锚定行 %d 条' % len(PINL))

# ---------- 6. 词族账: 同一数字的三把尺 ----------
FAMS = [u'octet', u'octets', u'byte', u'bytes', u'hex', u'hexadecimal',
        u'positive', u'non-negative', u'negitive', u'negative', u'zero',
        u'CSPRNG', u'entropy', u'random', u'sequential', u'non-sequential',
        u'unique', u'serialNumber', u'serial number', u'serialNumber values',
        u'20 octets', u'64 bits', u'63 bits', u'159', u'160', u'64',
        u'2\u00b9\u2075\u2079', u'positiveint', u'MUST be able to handle',
        u'Conformant', u'Conforming']
LOW = [pnorm(T[i]) for i in range(NSRC)]
M['fam_sub'] = [[cnt_cur(LOW[i], pnorm(w)) for w in FAMS] for i in range(NSRC)]
WBK = [u'digit' if re.match(u'^[0-9]', w) else u'alpha' for w in FAMS]
M['fam_ub'] = [[ub(LOW[i], pnorm(w), WBK[k]) for k, w in enumerate(FAMS)] for i in range(NSRC)]
M['fam_wrap'] = [M['fam_sub'][i][k] - M['fam_ub'][i][k] for i in range(NSRC) for k in range(len(FAMS))]
for k, w in enumerate(FAMS):
    print(u'6 %-22s 子串=%s 词界=%s' % (w, [M['fam_sub'][i][k] for i in range(NSRC)],
                                       [M['fam_ub'][i][k] for i in range(NSRC)]))
# “某文书撤了数”的最宽档: 2459 对 20 octets / positive / 64 全档为 0?
WIDEST = []
for w in [u'20 octets', u'positive', u'ub-serial-number', u'64 bits']:
    q = pnorm(w)
    WIDEST.append([cnt_cur(LOW[i], q) for i in range(NSRC)])
M['widest'] = WIDEST
print(u'6 最宽档(全篇折平子串):', json.dumps(WIDEST))
assert WIDEST[0][0] == 0, u'2459 里 20 octets 并非零命中——判词要改'

# ---------- 7. §4.1.2.2 三代正文块: 切句 ⇎ 集合 ----------
def block(i, a_nd, b_nd):
    a = find_line(i, a_nd)
    b = find_line(i, b_nd, a + 1)
    assert a >= 0 and b > a, (a_nd, b_nd, a, b)
    return NL.join([x for x in L[i][a:b] if not is_shell(x, i)])


BLK = [block(i, u'The serial number', u'4.1.2.3') if i <= 2 else None for i in range(NSRC)]
assert BLK[0] and BLK[2]


def sents(txt):
    return [pnorm(z) for z in re.split(u'(?<=[.!?]) +', pnorm(txt)) if z]


S = [sents(b) if b is not None else [] for b in BLK]
M['sec_sents'] = [len(s) for s in S]
set2459, set3280, set5280 = set(S[0]), set(S[1]), set(S[2])
M['sec_2459_in_3280'] = len([z for z in S[0] if z in set3280])
M['sec_3280_5280_same'] = len([z for z in S[1] if z in set5280])
M['sec_5280_new'] = len([z for z in S[2] if z not in set3280])
M['sec_3280_dropped'] = len([z for z in S[1] if z not in set5280])
print(u'7 句集: 句数', M['sec_sents'], u'2459句落入3280', M['sec_2459_in_3280'],
      u'3280∩5280', M['sec_3280_5280_same'], u'5280新句', M['sec_5280_new'],
      u'3280被删句', M['sec_3280_dropped'])
assert M['sec_2459_in_3280'] <= len(S[0])

# ---------- 8. DER 数值账: 样例(值,内容长)对 ----------
RXD = re.compile(u'^\\s*\\d+\\s+(\\d+):\\s+INTEGER (\\d+)\\s*$')
PAIRS = []
for i in range(NSRC):
    ps = []
    for x in L[i]:
        m = RXD.match(x)
        if m:
            ps.append((int(m.group(2)), int(m.group(1))))
    PAIRS.append(ps)
M['der_pairs'] = PAIRS
print(u'8 DER对:', PAIRS)


def der_len(v):
    """机制A·闭式: 位数→字节数, 高位成 1 补一枚 00。"""
    if v < 0:
        raise ValueError
    bl = v.bit_length()
    n = (bl + 7) // 8
    if bl and bl % 8 == 0:
        n += 1
    return max(n, 1)


BADP = [(LBL[i], v, l, der_len(v)) for i in range(NSRC) for (v, l) in PAIRS[i] if der_len(v) != l]
M['der_pair_fail'] = len(BADP)
print(u'8 闭式对账不符:', BADP)
assert not BADP, u'样例 DER 长度与闭式不符'
M['der_159'] = der_len(2 ** 159 - 1)
M['der_160'] = der_len(2 ** 160 - 1)
M['der_63'] = der_len(2 ** 63 - 1)
M['der_63p1'] = der_len(2 ** 63 + 1)
print(u'8 边界: 2^159-1→%d 字节 ⇎ 2^160-1→%d 字节 ⇎ 2^63-1→%d ⇎ 2^63+1→%d'
      % (M['der_159'], M['der_160'], M['der_63'], M['der_63p1']))
assert M['der_159'] == 20 and M['der_160'] == 21 and M['der_63'] == 8 and M['der_63p1'] == 9

# ---------- 9. LE 实例回收: 九字节面串 → 值 ----------
i0 = T[4].find(u'02 09 00 80 00 00 00 00 00 00 01')
assert i0 >= 0
seg = T[4][i0:i0 + 40].split(NL)[0]
hx = u''.join(seg.split(u' '))[:4 + 2 * 9]
M['le_hex'] = hx
val = int(hx[4:4 + 2 * 9], 16) if hx[:2] == u'02' else int(hx[4:], 16)
M['le_hex_val'] = str(val)
M['le_hex_len_octet'] = int(hx[2:4], 16)
print(u'9 LE九字节串: 值=%d == 2^63+1? %s ｜ 长度字节=%d' % (val, val == 2 ** 63 + 1, M['le_hex_len_octet']))
assert val == 2 ** 63 + 1 and M['le_hex_len_octet'] == 9
# 壳内写法档: 2<sup>63</sup> 在剥壳档散作 2 63
M['le_sup_shell'] = cnt_cur(T[4], u'<sup>63</sup>')
M['le_sup_stripped'] = cnt_cur(pnorm(ST), u'value 2 63')
M['le_sup_fold'] = cnt_cur(pnorm(ST), u'2 63 +1')
print(u'9 LE上标壳: 壳内 <sup>63</sup> %d 枚 ⇎ 剥壳档 „2 63 +1“ %d 枚' % (M['le_sup_shell'], M['le_sup_fold']))
assert M['le_sup_shell'] >= 1 and M['le_sup_fold'] >= 1

# ---------- 10. BR serialNumber 表行: 块定界(节标题针) ----------
CAP = u'MUST be a non-sequential number greater than zero (0) and less than 2\u00b9\u2075\u2079'
brrows = []
for k, x in enumerate(L[3]):
    if CAP in x or u'byte-for-byte identical to the serialNumber' in x:
        mm = u'?'
        for sm in re.finditer(u'^[ \\t\\x0c\\u2007\\u00a0]*7\\.1\\.2\\.\\d+ [^\\n]*', NL.join(L[3][:k + 1]), re.M):
            mm = sm.group(0).strip()[:36]
        brrows.append([k + 1, 1 if CAP in x else 0,
                       1 if u'byte-for-byte' in x else 0, mm])
M['br_rows'] = brrows
print(u'10 BR 行:', brrows)
M['br_cap_rows'] = len([r for r in brrows if r[1] == 1])
M['br_bfb_rows'] = len([r for r in brrows if r[2] == 1])
M['br_cap_secs'] = [r[3] for r in brrows if r[1] == 1]
M['br_bfb_secs'] = [r[3] for r in brrows if r[2] == 1]
assert M['br_cap_rows'] == 8 and M['br_bfb_rows'] == 3
assert len(set(M['br_cap_secs'])) == 8, u'八行各属不同节'
# byte-for-byte 三行: 两行在 Precertificate Profile(7.1.2.9), 一行在 CRL 条目表(7.1.2.11)
assert M['br_bfb_secs'].count(u'7.1.2.9 Precertificate Profile') == 2
assert M['br_bfb_secs'].count(u'7.1.2.11 Common Certificate Fields') == 1

# ---------- 11. 义务词账(词界尺, 折平面) ----------
OBW = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY', u'SHALL', u'SHALL']
M['ob_line'] = [[sum([ub(x, w) for x in L[i]]) for w in [u'MUST', u'MUST NOT', u'SHOULD', u'MAY', u'SHALL']]
                for i in range(NSRC)]
M['ob_fold'] = [[ub(LOW[i], w.lower()) for w in [u'MUST', u'MUST NOT', u'SHOULD', u'MAY', u'SHALL']]
                for i in range(NSRC)]
M['ob_wrap2'] = [M['ob_fold'][i][k] - M['ob_line'][i][k] for i in range(NSRC) for k in range(5)]
print(u'11 义务词 行/折:', M['ob_line'], M['ob_fold'])

json.dump(M, io.open(u'corpus/_b95meas.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
print(u'已落 corpus/_b95meas.json ｜ 键 %d' % len(M))
