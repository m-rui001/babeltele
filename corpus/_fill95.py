# -*- coding: utf-8 -*-
# B95 解读注遍(第三套机制, 独立于 _pick95.py ⇎ _mkB95.py):
#   面一律按 rb 读出再 decode('utf-8','replace')——文本模式会把 BR 那面的 CRLF 折掉 6385 枚回车,
#   行尺一律手工 split('\n')(不用 splitlines, 也不用 readlines), 词尺走逐字符扫空白;
#   字面针走 str.count(整串子串档), 大小写另开一档(先把整面 lower+折空白), 整词档走负向断言正则的
#   第四轨(建条遍是三轨: 布尔表 ⇎ 游标 ⇎ 断言; 采集遍是游标手扫);
#   定义窗定界用"整行等值"比对题面行(既不是采集遍的行号滑窗, 也不是建条遍的面偏移 bisect);
#   句界用逐字符扫"句末标点+空格"的独立一份实现; 壳谓词用行首/含子串的第三种定形;
#   HTML 剥壳用 '<' 游标状态机, 同时产粘面(标签替空串)与断面(标签替空格)两张;
#   DER 内容长用十六进制字符路(数 hex 位数折半, 首 nibble ≥8 补一枚前导 00)——前两遍是 bit_length
#   闭式与逐次右移; §7.1 样例对按"冒号左侧末token=内容长"这一条独立切法回收。
# 前两遍的中间量一枚都不复用; 注里每个数都由本遍现读现算, 与编码区登记的数各自独立成账。
# 默认只打印现量清单(Probe), 加 WRITE=1 才把 "## ⛓解读注" 段写回条目(不动编码区与原文区)。
import io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ENTRY = u'corpus/babeltele/B95_certificate_serial_number_length_three_rulers.md'
RAWS = [u'corpus/raw/serialLen/rfc2459.txt', u'corpus/raw/serialLen/rfc3280.txt',
        u'corpus/raw/serialLen/rfc5280.txt', u'corpus/raw/serialLen/br_v202.layout.txt',
        u'corpus/raw/serialLen/le_asn1_der.html']
BRF = [u'corpus/raw/serialLen/br_v202.layout.txt', u'corpus/raw/serialLen/br_v202.raw.txt',
       u'corpus/raw/serialLen/br_v202.pypdf.txt']
LBL = [u'2459', u'3280', u'5280', u'br', u'le']
N = 5
WIN_H = [u'4.1.2.2  Serial number', u'4.1.2.2  Serial number', u'4.1.2.2.  Serial Number']
WIN_E = [u'4.1.2.3  Signature', u'4.1.2.3  Signature', u'4.1.2.3.  Signature']
FAMS = [u'octet', u'octets', u'byte', u'bytes', u'hex', u'hexadecimal',
        u'positive', u'non-negative', u'negitive', u'negative', u'zero', u'CSPRNG',
        u'entropy', u'random', u'sequential', u'non-sequential', u'unique', u'serialNumber',
        u'serial number', u'serialNumber values', u'20 octets', u'64 bits', u'63 bits',
        u'159', u'160', u'64', u'2\u00b9\u2075\u2079', u'positiveint',
        u'MUST be able to handle', u'Conformant', u'Conforming']
FI = {w: k for k, w in enumerate(FAMS)}
REG = json.load(io.open(u'corpus/_b95contract.json', encoding=u'utf-8'))
FLAT = json.load(io.open(u'corpus/_b95flat.json', encoding=u'utf-8'))

# ---------- 面: 逐字节读出 ----------
RB = [io.open(p, 'rb').read() for p in RAWS]
T = [z.decode('utf-8', 'replace') for z in RB]
LOW = []  # 大小写档面: lower + 空白折一枚空格(逐字符扫, 不用 ' '.join(split()))


def foldlow(s):
    out, prev = [], False
    for c in s:
        if c.isspace():
            if out and not prev:
                out.append(u' ')
            prev = True
        else:
            out.append(c.lower())
            prev = False
    if out and out[-1] == u' ':
        out.pop()
    return u''.join(out)


LOW = [foldlow(z) for z in T]
L = [z.split(NL) for z in T]

n_byte = [len(z) for z in RB]
n_ch = [len(z) for z in T]
n_extra = [n_byte[i] - n_ch[i] for i in range(N)]


def cnt_char(s, c):
    k = 0
    for x in s:
        if x == c:
            k += 1
    return k


n_lf = [cnt_char(z, u'\n') for z in T]
n_cr = [cnt_char(z, u'\r') for z in T]
n_line = [len(z) for z in L]
n_word = []
for z in T:
    c, prev = 0, True
    for ch in z:
        ws = ch.isspace()
        if not ws and prev:
            c += 1
        prev = ws
    n_word.append(c)
n_cp = [len(set(z)) for z in T]
na_tot, na_set = [], []
for z in T:
    s = set()
    c = 0
    for ch in z:
        if ord(ch) > 127:
            c += 1
            s.add(ch)
    na_tot.append(c)
    na_set.append(len(s))


def sub_ci(w):
    return [LOW[i].count(foldlow(w)) for i in range(N)]


def word_ci(w, kind=None):
    q = foldlow(w)
    if kind is None:
        kind = u'digit' if re.match(u'^[0-9]', q) else u'alpha'
    a = u'(?<![0-9])' if kind == u'digit' else u'(?<![A-Za-z])'
    b = u'(?![0-9])' if kind == u'digit' else u'(?![A-Za-z])'
    return [len(re.findall(a + re.escape(q) + b, LOW[i])) for i in range(N)]


# 大小写敏感档(直接在原面上 str.count)


def sub_cs(w):
    return [T[i].count(w) for i in range(N)]


def is_shell_line(x, i):
    """第三把壳尺: 只看行首三形与独占换页符(采集遍是整行序列正则, 建条遍是逐字符游标定形)。"""
    s = x.strip()
    if s == u'':
        return True
    if i <= 2:
        return (s == u'\x0c' or s.startswith(u'[Page ') or s.startswith(u'RFC ')
                or s.startswith(u'Internet Engineering Task Force')
                or u'[Page ' in s)
    if i == 3:
        return s == u'\x0c' or re.match(r'^pg\.\s*\d+', s) is not None
    return False


# ---------- 定义窗: 整行等值定界(含题面行 ⇎ 从正文首行起) ⇎ 纯 find 定界 ----------
WIN, WIN_FULL, WIN_ROW, NAIVE = [], [], [], []
for i in range(3):
    h1 = [k for k, l in enumerate(L[i]) if l == WIN_H[i]]
    h2 = [k for k, l in enumerate(L[i]) if l == WIN_E[i]]
    assert len(h1) == 1 and len(h2) == 1 and h2[0] > h1[0], (i, h1, h2)
    WIN_ROW.append((h1[0] + 1, h2[0] + 1))
    WIN_FULL.append((NL.join(L[i][h1[0]:h2[0]]), NL.join(L[i][h1[0] + 1:h2[0]])))
    WIN.append((NL.join([x for x in L[i][h1[0]:h2[0]] if not is_shell_line(x, i)]),
                NL.join([x for x in L[i][h1[0] + 1:h2[0]] if not is_shell_line(x, i)])))
    a = T[i].find(u'4.1.2.2')
    b = T[i].find(u'4.1.2.3', a + 1)
    NAIVE.append((a, b, b - a, T[i][a:T[i].find(NL, a)].strip()[:56]))
for i in (3, 4):
    WIN.append((None, None))
    WIN_FULL.append((None, None))
    NAIVE.append(None)


def sents(txt):
    """独立句界: 逐字符扫 '句末标点 + 空格', 返回句子表。"""
    f = foldlow(txt)
    out, start, k, n = [], 0, 0, len(f)
    while k < n:
        if f[k] in u'.!?' and (k + 1 >= n or f[k + 1] == u' '):
            j = k + 1
            while j < n and f[j] == u' ':
                j += 1
            seg = f[start:j].strip()
            if seg:
                out.append(seg)
            start = j
            k = j
            continue
        k += 1
    if start < n:
        seg = f[start:].strip()
        if seg:
            out.append(seg)
    return out


SEC = [sents(WIN_FULL[i][0]) for i in range(3)]            # 含题面行, 不剥壳
SEC_F = [sents(WIN_FULL[i][1]) for i in range(3)]          # 从正文首行起, 不剥壳
SEC_U = [sents(WIN[i][0]) for i in range(3)]               # 含题面行, 剥壳
SEC_B = [sents(WIN[i][1]) for i in range(3)]               # 从正文首行起, 剥壳(与注册 sec_sents 同格)
for k in (SEC, SEC_F, SEC_U):
    for i in (3, 4):
        k.append([])


def inter(a, b):
    """多重集交: 手工双重循环(前两遍是集合 & ⇎ Counter 直方图)。"""
    n, bb = 0, list(b)
    for x in a:
        if x in bb:
            n += 1
            bb.remove(x)
    return n


# ---------- DER: 十六进制字符路 ⇎ §7.1 样例对的冒号左路 ----------


def der_hex_bare(v):
    """不加前导零的那一把(只为把“奇数位 hex 会误判”这一处岔口量出来)。"""
    h = u'%X' % v
    return len(h) // 2 + (1 if int(h[0], 16) >= 8 else 0)


def der_hex(v):
    h = u'%X' % v
    if len(h) % 2:
        h = u'0' + h          # 十六进制位数不足偶数先补前导零, 再谈符号位那枚
    return len(h) // 2 + (1 if int(h[0], 16) >= 8 else 0)


BOUND = [(2 ** 159 - 1, u'2^159-1'), (2 ** 160 - 1, u'2^160-1'),
         (2 ** 63 - 1, u'2^63-1'), (2 ** 63 + 1, u'2^63+1')]
PAIRS = []
for i in range(N):
    got = []
    for x in L[i]:
        if u':' not in x:
            continue
        left, right = x.split(u':', 1)
        tk = left.split()
        if len(tk) != 2 or not tk[0].isdigit() or not tk[1].isdigit():
            continue
        m = re.match(u'^\\s*INTEGER\\s+([0-9]+)\\s*$', right)
        if m:
            got.append((int(m.group(1)), int(tk[1])))
    PAIRS.append(got)
PAIR_BAD = [(LBL[i], v, l, der_hex(v)) for i in range(N) for (v, l) in PAIRS[i] if der_hex(v) != l]
PAIR_BAD_BARE = [(LBL[i], v, l, der_hex_bare(v)) for i in range(N)
                 for (v, l) in PAIRS[i] if der_hex_bare(v) != l]
BOUND_BARE = [der_hex_bare(v) for v, _ in BOUND]

# ---------- LE: HTML 壳状态机(粘面 ⇎ 断面) ⇎ 十六进制串 ----------


def detag(s, fill):
    out, k, n = [], 0, len(s)
    while k < n:
        c = s[k]
        if c == u'<' and k + 1 < n and (s[k + 1].isascii() and s[k + 1].isalpha()
                                        or s[k + 1] in u'/!'):
            j = s.find(u'>', k)
            if j >= 0:
                out.append(fill)
                k = j + 1
                continue
        out.append(c)
        k += 1
    return u''.join(out)


HSTICKY = detag(T[4], u'')
HSPACED = detag(T[4], u' ')
n_tags = len(re.findall(r'<(?=[a-zA-Z/!])[^>]*>', T[4]))
n_ent = len(re.findall(u'&[a-zA-Z#0-9]+;', T[4]))
# 十六进制串档: 整面正则找 '两枚 hex + 空格' 连成的长串(建条遍是 split+join 定长切片, 采集遍是逐字符收组)
HEXRUNS = re.findall(u'(?<![0-9a-fA-F])(?:[0-9a-fA-F]{2} ){7,}[0-9a-fA-F]{2}(?![0-9a-fA-F])', T[4])
HEXSER = [z for z in HEXRUNS if z.startswith(u'02 ')]
HEX = HEXSER[0].split(u' ') if HEXSER else []
HEX_BYTES = [int(z, 16) for z in HEX]
HEX_VAL = 0
for b in HEX_BYTES[2:]:
    HEX_VAL = HEX_VAL * 256 + b
SUP_SHELL = T[4].count(u'<sup>63</sup>')
SUP_SPACED = foldlow(HSPACED).count(u'value 2 63')
SUP_SPACED2 = foldlow(HSPACED).count(u'2 63 +1')
SUP_STICKY = foldlow(HSTICKY).count(u'value 263')
SUP_STICKY2 = foldlow(HSTICKY).count(u'263+1')

# ---------- BR 三张提取面 ----------
BRF_T = [io.open(p, 'rb').read().decode('utf-8', 'replace') for p in BRF]
BRF_LOW = [foldlow(z) for z in BRF_T]
BRF_CH = [len(z) for z in BRF_T]
BRF_159 = [BRF_LOW[k].count(foldlow(u'2\u00b9\u2075\u2079')) for k in range(3)]
BRF_CSP = [BRF_LOW[k].count(u'csprng') for k in range(3)]
BRF_CAP = [BRF_LOW[k].count(u'non-sequential number greater than zero') for k in range(3)]

# ---------- 编码区锚: 只按索引走查 '⟦⟧⟨⟩'(不用 AN(), 不用正则) ----------
md = io.open(ENTRY, encoding=u'utf-8').read()
assert md.count(u'## ⛓解读注') == 1
enc = re.search(u'## ⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
orig = re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\\n\\n## ', md, re.S).group(1)
PAIRS_AN, k = [], 0
while True:
    a = enc.find(u'⟦', k)
    if a < 0:
        break
    b = enc.find(u'⟧', a)
    c = enc.find(u'⟨', b)
    d = enc.find(u'⟩', c)
    PAIRS_AN.append((enc[a + 1:b], enc[c + 1:d]))
    k = d + 1
UNIQ = sorted(set(PAIRS_AN))
TAGP = [u'A', u'B', u'C', u'D', u'E']
IDX = {t: i for i, t in enumerate(TAGP)}


FACE_RAW = T[:4] + [HSPACED]        # 四面原样 + 第五面换成本遍游标断面
FACE_STK = T[:4] + [HSTICKY]
FACE_SHL = T[:4] + [T[4]]


def an_hit(tg, atom):
    """五档: 本家面逐字符 ⇎ 粘面 ⇎ 未剥的壳面 ⇎ 只折空白(留大小写) ⇎ 折平+小写(与门里 prose_norm 同族)。"""
    i = IDX[tg]
    f = foldlow(atom)
    ver = FACE_RAW[i].count(atom)
    ws = u' '.join(FACE_RAW[i].split()).count(u' '.join(atom.split()))
    return (ver, FACE_STK[i].count(atom), FACE_SHL[i].count(atom), ws,
            foldlow(FACE_RAW[i]).count(f),
            sum([1 for j in range(N) if j != i and foldlow(FACE_RAW[j]).count(f) > 0]))


# ---------- 现量清单 ----------
def row(v):
    return u'⇎'.join([u'%d' % x if isinstance(x, int) else u'%s' % x for x in v])


OUT = []
P = OUT.append
P(u'字节 %s ⇎ 码位 %s ⇎ 多出的字节 %s' % (row(n_byte), row(n_ch), row(n_extra)))
P(u'手工切行 %s ⇎ 换行 %s ⇎ 回车 %s ⇎ 词 %s ⇎ 唯一码位 %s' %
  (row(n_line), row(n_lf), row(n_cr), row(n_word), row(n_cp)))
P(u'非ASCII %s ⇎ 去重 %s' % (row(na_tot), row(na_set)))
P(u'注册: bytes %s chars %s splitnl %s n_lf %s n_cr %s cp %s na %s maxlen %s' %
  (row(FLAT['bytes']), row(FLAT['chars']), row(FLAT['splitnl']), row(FLAT['n_lf']),
   row(FLAT['n_cr']), row(FLAT['cp']), row(FLAT['na_total']), row(FLAT['maxlen'])))
RAWL = [z.split(NL) for z in T]
P(u'义务词 MUST: 本遍逐行(留行尾回车) %s ⇎ 去回车 %s ⇎ 本遍折平子串 %s ⇎ 本遍折平整词 %s ⇎ 注册 ob_line %s ob_fold %s' %
  (row([sum([l.count(u'MUST') for l in RAWL[i]]) for i in range(N)]),
   row([sum([l.rstrip(u'\r').count(u'MUST') for l in RAWL[i]]) for i in range(N)]),
   row([LOW[i].count(u'must') for i in range(N)]), row(word_ci(u'must')),
   row([FLAT['ob_line'][i][0] for i in range(N)]), row([FLAT['ob_fold'][i][0] for i in range(N)])))
P(u'义务词 MAY: 逐行敏感 %s ⇎ 折平子串 %s ⇎ 整词 %s ⇎ 注册 ob_line %s ob_fold %s' %
  (row([sum([l.rstrip(u'\r').count(u'MAY') for l in RAWL[i]]) for i in range(N)]),
   row([LOW[i].count(u'may') for i in range(N)]), row(word_ci(u'may')),
   row([FLAT['ob_line'][i][3] for i in range(N)]), row([FLAT['ob_fold'][i][3] for i in range(N)])))
P(u'最长行(手工扫, 留行尾回车) %s ⇎ 去回车 %s ⇎ 注册 %s' %
  (row([max([len(x) for x in RAWL[i]]) for i in range(N)]),
   row([max([len(x.rstrip(u'\r')) for x in RAWL[i]]) for i in range(N)]), row(FLAT['maxlen'])))
for w in [u'20 octets', u'serialNumber', u'serial number', u'octet', u'positive',
          u'non-negative', u'CSPRNG', u'64 bits', u'2\u00b9\u2075\u2079', u'Conformant',
          u'Conforming', u'the sign bit', u'positiveint']:
    P(u'针 %-34s 敏感子串 %s ⇎ 不敏感子串 %s ⇎ 整词 %s ⇎ 注册 fam_sub %s fam_ub %s' %
      (w, row(sub_cs(w)), row(sub_ci(w)), row(word_ci(w)),
       row([FLAT['fam_sub'][i][FI[w]] for i in range(N)] if w in FI else u'-'),
       row([FLAT['fam_ub'][i][FI[w]] for i in range(N)] if w in FI else u'-')))
P(u'serialNumber 嵌在驼峰里的枚数 %s' %
  row([LOW[i].count(u'certificateserialnumber') for i in range(N)]))
P(u'窗: 题行(1基) %s' % str(WIN_ROW))
P(u'  含题面行 原 %s 折平 %s ⇎ 剥壳后 %s 折平 %s' %
  (row([len(WIN_FULL[i][0]) for i in range(3)]), row([len(foldlow(WIN_FULL[i][0])) for i in range(3)]),
   row([len(WIN[i][0]) for i in range(3)]), row([len(foldlow(WIN[i][0])) for i in range(3)])))
P(u'  从正文首行起 原 %s 折平 %s ⇎ 剥壳后 %s 折平 %s ⇎ 注册 chars %s' %
  (row([len(WIN_FULL[i][1]) for i in range(3)]), row([len(foldlow(WIN_FULL[i][1])) for i in range(3)]),
   row([len(WIN[i][1]) for i in range(3)]), row([len(foldlow(WIN[i][1])) for i in range(3)]),
   u'-'))
P(u'  窗内义务词 MUST %s ⇎ SHOULD %s ⇎ 剥壳后窗内 %s' %
  (row([WIN_FULL[i][1].count(u'MUST') for i in range(3)] + [0, 0]),
   row([WIN_FULL[i][1].count(u'SHOULD') for i in range(3)] + [0, 0]),
   row([WIN[i][1].count(u'MUST') for i in range(3)] + [0, 0])))
for i in range(3):
    P(u'  %s 句数: 含题面不剥壳 %d ⇎ 正文起不剥壳 %d ⇎ 含题面剥壳 %d ⇎ 正文起剥壳 %d ⇎ 注册 %d' %
      (LBL[i], len(SEC[i]), len(SEC_F[i]), len(SEC_U[i]), len(SEC_B[i]), FLAT['sec_sents'][i]))
    P(u'    不剥壳比剥壳多出的句: %s' % [z[:56] for z in SEC[i] if z not in SEC_U[i]])
    P(u'    纯 find: 起 %d 止 %d 窗长 %d 首行 %r' % NAIVE[i])
P(u'句集(正文起·剥壳): 2459∩3280 %d(注册 %d) ⇎ 3280∩5280 %d(注册 %d) ⇎ 5280新 %d(注册 %d) ⇎ 3280删 %d(注册 %d)' %
  (inter(SEC_B[0], SEC_B[1]), FLAT['sec_2459_in_3280'],
   inter(SEC_B[1], SEC_B[2]), FLAT['sec_3280_5280_same'],
   len([z for z in SEC_B[2] if z not in SEC_B[1]]), FLAT['sec_5280_new'],
   len([z for z in SEC_B[1] if z not in SEC_B[2]]), FLAT['sec_3280_dropped']))
P(u'DER hex 路 边界 %s ⇎ 未补前导零那把 %s ⇎ 注册 %s %s %s %s' %
  (row([der_hex(v) for v, _ in BOUND]), row(BOUND_BARE), FLAT['der_159'], FLAT['der_160'],
   FLAT['der_63'], FLAT['der_63p1']))
P(u'样例对 %s(注册 %s) 逐枚核对错 %d 枚 ⇎ 未补零那把错 %d 枚 %s(注册 der_pair_fail %d)' %
  (row([len(x) for x in PAIRS]), row(FLAT['der_pair_n']), len(PAIR_BAD), len(PAIR_BAD_BARE),
   PAIR_BAD_BARE[:4], FLAT['der_pair_fail']))
P(u'5280 样例对 %s' % PAIRS[2])
P(u'注册 der_pairs[2] %s' % FLAT['der_pairs'][2])
P(u'BR 三面 字符 %s ⇎ 2^159 %s ⇎ CSPRNG %s ⇎ 值域句 %s ⇎ 注册 %s %s %s %s' %
  (row(BRF_CH), row(BRF_159), row(BRF_CSP), row(BRF_CAP), row(FLAT['brf_chars']),
   row(FLAT['brf_n159']), row(FLAT['brf_csprng']), row(FLAT['brf_cap'])))
P(u'LE 标签 %d(注册 %d) 实体 %d(注册 %d) 粘面 %d 断面 %d(断面行数 %d) 注册剥壳面 %d' %
  (n_tags, FLAT['le_tags'], n_ent, FLAT['le_entities'], len(HSTICKY), len(HSPACED),
   len(HSPACED.split(NL)), FLAT['le_stripped_chars']))
P(u'LE sup 壳内 %d ⇎ 断面 %d/%d ⇎ 粘面 %d/%d ⇎ 注册 shell %d stripped %d fold %d' %
  (SUP_SHELL, SUP_SPACED, SUP_SPACED2, SUP_STICKY, SUP_STICKY2,
   FLAT['le_sup_shell'], FLAT['le_sup_stripped'], FLAT['le_sup_fold']))
P(u'LE hex 串 %r 长 %d ⇎ tag %d len %d ⇎ 值 %d ⇎ 注册 %s %d %s ⇎ 面上长串 %d 条' %
  (u' '.join(HEX), len(u''.join(HEX)), HEX_BYTES[0] if HEX_BYTES else 0,
   HEX_BYTES[1] if len(HEX_BYTES) > 1 else 0, HEX_VAL, FLAT['le_hex'],
   FLAT['le_hex_len_octet'], FLAT['le_hex_val'], len(HEXRUNS)))
P(u'锚: 引用 %d 处 ⇎ 去重 %d 串 ⇎ 编码区字符 %d ⇎ 原文区 %d(含换行 %d)' %
  (len(PAIRS_AN), len(UNIQ), len(enc.replace(NL, u'')), len(orig.replace(NL, u'')), len(orig)))
AN_T = [an_hit(tg, at) for tg, at in PAIRS_AN]
for (tg, at), v in zip(PAIRS_AN, AN_T):
    P(u'  ⟦%s⟧ %-52s 本家逐字符 %d 粘面 %d 壳面 %d 只折空白 %d 折平小写 %d 别家 %d'
      % (tg, at[:52], v[0], v[1], v[2], v[3], v[4], v[5]))
P(u'锚档合计: 逐字符 %d/%d ⇎ 只折空白 %d/%d ⇎ 折平小写 %d/%d ⇎ 只因大小写 %s ⇎ 别家同现 %d 处' %
  (len([1 for v in AN_T if v[0] > 0]), len(AN_T), len([1 for v in AN_T if v[3] > 0]), len(AN_T),
   len([1 for v in AN_T if v[4] > 0]), len(AN_T),
   [a[:44] for (_t, a), v in zip(PAIRS_AN, AN_T) if v[3] == 0 and v[4] > 0],
   len([1 for v in AN_T if v[5] > 0])))
P(u'注册 对账 %d/%d/%d 布尔门 %d/%d 键 %d 契约 %d(复合 %d)' %
  (FLAT['pick_pairs'], FLAT['pick_agree'], FLAT['pick_diff'], FLAT['bool_green'],
   FLAT['bool_all_n'], len(FLAT), len(REG),
   len([v for v in REG.values() if not v.startswith(u"B95V('")])))
print(u'\n'.join(OUT))

# ---------- 注 ----------
SRC_CH = sum(n_ch)
SRC_BY = sum(n_byte)
ENC_CH = len(enc.replace(NL, u''))
ORG_CH = len(orig.replace(NL, u''))
ORG_NL = len(orig)
A_VER = len([1 for v in AN_T if v[0] > 0])
A_WS = len([1 for v in AN_T if v[3] > 0])
A_FOLD = len([1 for v in AN_T if v[4] > 0])
A_CASE = [a for (_t, a), v in zip(PAIRS_AN, AN_T) if v[3] == 0 and v[4] > 0]
A_CROSS = len([1 for v in AN_T if v[5] > 0])
SH_N = len([1 for tg, _a in PAIRS_AN if tg == u'E'])
E_SHL = len([1 for (tg, _a), v in zip(PAIRS_AN, AN_T) if tg == u'E' and v[2] > 0])
E_SPB = len([1 for (tg, _a), v in zip(PAIRS_AN, AN_T) if tg == u'E' and v[0] > 0])
MAXLINE_KEEP = [max([len(x) for x in RAWL[i]]) for i in range(N)]
MAXLINE_CR = [max([len(x.rstrip(u'\r')) for x in RAWL[i]]) for i in range(N)]
CAMEL = [LOW[i].count(u'certificateserialnumber') for i in range(N)]
TXTMODE = [len(io.open(p, encoding='utf-8').read()) for p in RAWS]
DISK = io.open(u'corpus/raw/serialLen/le_asn1_der.txt', 'rb').read().decode('utf-8', 'replace')
DISK_LN = len(DISK.split(NL))
LOWDIFF = sub_ci(u'Conformant')[1] - sub_cs(u'Conformant')[1]
WRAP = [sum([sub_ci(w)[i] - word_ci(w)[i] for w in FAMS]) for i in range(N)]
WRAP_REG = [sum(FLAT['fam_wrap'][i * len(FAMS):(i + 1) * len(FAMS)]) for i in range(N)]
widest0 = sub_ci(u'20 octets')[0]
positive0 = word_ci(u'positive')[0]
sub_wrap_tot = sum(WRAP)
pcta = lambda a, b: u'%.2f%%' % (100.0 * a / b)
ODDFIX = sorted(set([v for i in range(N) for (v, _l) in PAIRS[i]
                     if der_hex_bare(v) != der_hex(v)]))
TOT_PAIRS = sum([len(x) for x in PAIRS])
SEC_HANS = [z for z in SEC[1] if z not in SEC_U[1]]
SEC_HAN_DELTA = len(SEC[1]) - len(SEC_U[1])

FMT = (u'## ⛓解读注\n\n'
        u'本遍是第三套机制, 与前两遍只换机制不换定义: 面一律按 rb 读出再 `decode(\'utf-8\',\'replace\')`'
        u'(文本模式会把 BR 那面 %d 枚回车静悄悄归一掉: 同一份文件文本模式落 %d 字符, 逐字节档读到 %d 字符), '
        u'行一律手工 `split(\'\\n\')`(不 splitlines, 不 readlines), 词与句一律逐字符扫, 字面针一律 `str.count`, '
        u'窗定界一律整行等值, HTML 剥壳一律 `\'<\'` 游标状态机, DER 内容长一律十六进制字符路。'
        u'前两遍的中间量一枚都不复用。\n\n'
        u'### 压缩账(五份一律 %s, 本遍现读)\n'
        u'| 量 | 2459 ⇎ 3280 ⇎ 5280 ⇎ br ⇎ le |\n|---|---|\n'
        u'| 字节面 ⇎ 码位面 | %s ⇎ %s |\n'
        u'| UTF-8 多出的字节(=码位差) | %s |\n'
        u'| 手工切行 ⇎ 逐字符数换行 ⇎ 数回车 | %s ⇎ %s ⇎ %s |\n'
        u'| 逐字符扫词 | %s |\n'
        u'| 唯一码位 ⇎ 非 ASCII 枚 ⇎ 非 ASCII 去重 | %s ⇎ %s ⇎ %s |\n'
        u'| 子串档 `20 octets`(敏感 ⇎ 不敏感 ⇎ 整词三档同值) | %s ⇎ %s ⇎ %s |\n'
        u'| `serialNumber` 敏感子串 ⇎ 不敏感子串 ⇎ 整词 | %s ⇎ %s ⇎ %s |\n'
        u'| `2¹⁵⁹` 枚数 | %s |\n'
        u'| §4.1.2.2 窗字符(正文首行起, 原面 ⇎ 剥壳面) | %s ⇎ %s |\n\n'
        u'编码区 %d 字符(不含换行) ⇎ 五份源面合 %s 字符(字节合 %s, 差 %d 恰为后两份各 %d ⇎ %d 枚非 ASCII 的 '
        u'UTF-8 余量) = %s ⇎ 在档摘录 %s 字符(去换行)⇎%s(含换行): 编码⇎摘录两把尺 %s⇎%s。\n\n'
        u'### 四处只有换尺子才看得见的岔口(本注现读出)\n'
        u'① 行尺: 手工 `split(\'\\n\')` 在 br 那面把 %d 枚回车留在行尾, 于是"最长行"这格本遍读 %d, 而建条遍先把'
        u'行尾回车剥掉再量得 %d——其余四面两档同值(%s ⇎ %s)。同一枚"行"在三份 RFC 面上没有回车, 差别只发生在'
        u'那份全 CRLF 面上。\n'
        u'② 定界档: 只对整个面用纯 `find(\'4.1.2.2\')` 起、`find(\'4.1.2.3\')` 止, 三份 RFC 全落在目录行'
        u'(面偏移 %d ⇎ %d ⇎ %d), 窗长只有 %d ⇎ %d ⇎ %d 字符, 里面一枚答值都读不到; 换成本遍的整行等值定界, '
        u'窗起于第 %s–%s ⇎ %s–%s ⇎ %s–%s 行(1 基, 含头不含尾), 原窗 %d ⇎ %d ⇎ %d 字符。建条遍之所以没踩这个坑, 是因为它的题面针取'
        u'的是正文首句 \'The serial number\' 而不是节号——目录行里没有 \'the\'。\n'
        u'③ 窗内句数的两处档差(与注册 [2,8,8] 相对): 5280 的节号写作 \'4.1.2.2.  Serial Number\', 末尾那枚句号'
        u'加空格在折平面上自造一处断点, 于是含题面行的窗给 %d 句, 从正文首行起给 %d 句; 3280 含题面不剥壳给 %d 句, '
        u'同窗剥壳后给 %d 句——枚数差只有 %d, 集合差却有 %d 句(%s): 页眉行折进断面之后 \'et. al.\' 里的两枚句点各造'
        u'一处断点, 另一句是整行页眉被当成一句。本遍剥壳+正文起档逐格回 [2,8,8], 句集容斥也逐格回 2459∩3280 %d ⇎ '
        u'3280∩5280 同句 %d ⇎ 5280 新句 %d ⇎ 3280 被删 %d(前两遍用集合 & ⇎ Counter 直方图, 本遍用多重集手工'
        u'双重循环)。\n'
        u'④ 大小写档与词界档: `serialNumber` 敏感子串 %s ⇎ 不敏感 %s ⇎ 不敏感面上加整词边界 %s, 差的那 %s 枚'
        u'几乎全长在 ASN.1 结构名 `CertificateSerialNumber` 里(逐份 %s 枚)——所以编码区给 %d 那一格记的是'
        u'不敏感子串档, 不是"驼峰那个拼法写了 %d 次"。`octet` 在 2459 子串 %d ⇎ 整词 %d, 差的 %d 枚全在 `octets` '
        u'内; `positive` 整词 %s ⇎ 子串 %s, 2459 那两枚子串都长在 `positiveInt`(它 %d 枚)里, 这正是"它一次都没'
        u'把序列号说成正整数"的根据; `Conformant` 敏感 %d ⇎ 不敏感 %d(3280 面内另有 %d 枚小写)。义务词两档同摆: '
        u'MUST 逐行 %s ⇎ 折平 %s, MAY 逐行 %s ⇎ 折平 %s——折平档把句中助动词 may 全吃进来。\n\n'
        u'### DER 这把尺的第三条路(本遍)\n'
        u'边界四枚现算 %d ⇎ %d ⇎ %d ⇎ %d 与登记同值(依次是 2^159−1 ⇎ 2^160−1 ⇎ 2^63−1 ⇎ 2^63+1 所需的 DER '
        u'内容字节数)。但这把尺一上手就错了 %d 枚: 样例里补零前后结果不同的值(%s)——十六进制位数是奇数时不先补前导零, '
        u'那半枚字节在整除时被丢掉, 内容长就少算一枚; 补零后与面上印出的长度逐枚核对, 全五份共收 %d 对(错 %d 枚), '
        u'这些对全部落在 §7.1 那串样例里, 回收的样例对表与前两遍同一条 %s。§7.1 的抽取路数是"冒号左侧末 token 即内容长"(建条遍是 token 判形, '
        u'采集遍是正则选择支)。实现侧那面本遍收出 %d 条 hex 长串(串长 %d 字节组起收), 以 02 起头的那条是唯一取用'
        u'的一条: `%s` ⇎ tag %d ⇎ 内容长 %d ⇎ 值 %d = 2^63+1, 紧凑串长 %d 字符。\n\n'
        u'### 序列化换了, 针就不在原地(BR 三面 ⇎ 实现侧壳内)\n'
        u'同一份 CA/B TLS BR 的三张提取面(layout ⇎ raw ⇎ pypdf)字符 %s ⇎ 2¹⁵⁹ %s ⇎ CSPRNG %s ⇎ 值域句 %s——'
        u'三面同数, 上标那形没被任何一张面拆散。实现侧那一份是带标签网页: 同一个 2^63 在壳内作 %d 枚 '
        u'<sup>63</sup>, 在剥出的断面上散作 \'value 2 63\' %d 枚 ⇎ \'2 63 +1\' %d 枚, 在粘面(标签替空串)上'
        u'作 \'value 263\' %d 枚 ⇎ \'263+1\' %d 枚——枚数没变, 字面针却要跟着档换形。本遍自己游标剥壳得 '
        u'断面 %d 字符/%d 行 ⇎ 粘面 %d 字符, 与盘上那份预剥文件 %d 字符/%d 行不是同一把尺, 所以 ⟦E⟧ 的 %d 枚锚'
        u'一律在本遍断面上比, 不复用预剥文件。\n\n'
        u'### 锚核验(%d 处 ⟦标签⟧⟨原文⟩ ⇎ 去重 %d 串, 逐枚按标签回本家文件)\n'
        u'本家面逐字符 verbatim 命中 %d 处; 另有 %d 处要把空白折成一枚空格才命中(锚身被硬换行劈开); '
        u'把面与锚同时小写后再比则 %d/%d 全命中——多出来的那 %d 处只与大小写有关, 是 ⟦A⟧⟨%s⟩ 一枚: '
        u'面上作 `The construct "positiveInt ::= INTEGER`, 词表按小写收进来, 门里的比对面(prose_norm 归一'
        u'大小写与引号)认它, 逐字符档不认。⟦E⟧ 那 %d 处锚在未剥的壳面上命中 %d 处、在本遍断面上命中 %d 处: '
        u'挡住它们的不是标签而是硬换行。去重后 %d 串里有 %d 串在别家面上也读得到(按引用算是跨家同现 %d 处), '
        u'其中最干净的是 `Conformant`/`Conforming` 那一对与逗号那一对, 各自只在一面成句。\n\n'
        u'### 读法\n'
        u'编码区九段各管一副账: 🧭 五份面尺三轨行账 ⇎ 码位与字节两把尺只在后两份分开(差 %d ⇎ %d), 逐枚非 ASCII '
        u'多出的字节两路相减归零; 📏 答值四代四把尺互不译(2459 一枚长度都不给: `20 octets` 最宽档 %d 枚, '
        u'`positive` 整词档 %d 枚), 3280 给 20 字节, BR 给 <2¹⁵⁹ 值域与 ≥64 位熵, 实现侧给 DER 内容长; '
        u'⚖ 单位词三轨(子串 ⇎ 布尔表词界 ⇎ 断言正则)逐枚同数, 子串尺比词界尺多读的那 %d 枚是复数词尾与驼峰内嵌; '
        u'🪜 义务词两档 ⇎ 那句弱义务折平档 %s ⇎ 逐行档合计 %d; 🔁 判词针 %d 枚×五份的四档可读性 ⇎ 独占账 '
        u'%d 枚只一面读到; 🧮 同宗三代正文块句数 [2,8,8] 与句集容斥; 🧱 BR 表行按节归属(八行值域句各属一节 ⇎ '
        u'三行 byte-for-byte 分属两节)与 ub-serial-number 的 64(第三种尺: 字符数); 🧬 DER 样例对与边界四枚; '
        u'🧾 壳账与对账 %d 项 ⇎ 逐键符 %d ⇎ 不符 %d ⇎ 布尔门 %d/%d。核心结论一条: 这道题的四代答案不在同一把尺上——字节数 ⇎ '
        u'比特位 ⇎ 值域 ⇎ 编码内容长, 只有把 20 字节去掉符号位换成 159 位, 才能看出 3280/5280 与 BR 那两句'
        u'其实同格, 而 8 字节只能到 63 位这件事只有实现面写了出来。\n\n'
        u'### 本条不能由在库文件判定的(只登记, 不进门槛)\n'
        u'现网证书里实际用到的序列号长度分布 ⇎ CA 实现是否真按 BR 的 ≥64 位熵发号(本条只认规范面自身) ⇎ '
        u'RFC 勘误表与改版后的现值 ⇎ BR 版本号 v2.0.2 之后是否仍写 2¹⁵⁹。上游一旦改版, 编码区里由面上现读的'
        u'数就只在本机这份快照成立。\n\n'
        u'### 编码与门的账\n'
        u'T1 逐锚回源: 本注逐字符档 %d/%d ⇎ 折空白档 %d/%d ⇎ 折平小写档 %d/%d(门按 prose_norm 档判, 与本遍'
        u'折平小写档同族) ⇎ T2 DERIV 复算: %d 枚键由 corpus/_b95contract.json 逐枚现算(其中 %d 枚是复合式或'
        u'聚合式而非直取值), 门内现量 %d 键与建条遍逐键同值 ⇎ T3 码位账: 五份源面唯一码位 %s(并集另计)。'
        u'对账 %d 项 ⇎ 符 %d ⇎ 不符 %d ⇎ 布尔门 %d/%d 全绿。\n'
        )
ARGS = (n_cr[3], TXTMODE[3], n_ch[3], u'rb 逐字节读出',
           row(n_byte), row(n_ch), row(n_extra),
           row(n_line), row(n_lf), row(n_cr), row(n_word),
           row(n_cp), row(na_tot), row(na_set),
           row(sub_cs(u'20 octets')), row(sub_ci(u'20 octets')), row(word_ci(u'20 octets')),
           row(sub_cs(u'serialNumber')), row(sub_ci(u'serialNumber')), row(word_ci(u'serialNumber')),
           row(sub_ci(u'2\u00b9\u2075\u2079')),
           row([len(WIN_FULL[i][1]) for i in range(3)] + [u'—', u'—']),
           row([len(WIN[i][1]) for i in range(3)] + [u'—', u'—']),
           ENC_CH, u'%d' % SRC_CH, u'%d' % SRC_BY, SRC_BY - SRC_CH, n_extra[3], n_extra[4],
           pcta(ENC_CH, SRC_CH), u'%d' % ORG_CH, u'%d' % ORG_NL, pcta(ENC_CH, ORG_CH), pcta(ENC_CH, ORG_NL),
           n_cr[3], MAXLINE_KEEP[3], MAXLINE_CR[3], row(MAXLINE_KEEP[:3] + [MAXLINE_KEEP[4]]),
           row(MAXLINE_CR[:3] + [MAXLINE_CR[4]]),
           NAIVE[0][0], NAIVE[1][0], NAIVE[2][0], NAIVE[0][2], NAIVE[1][2], NAIVE[2][2],
           WIN_ROW[0][0], WIN_ROW[0][1], WIN_ROW[1][0], WIN_ROW[1][1], WIN_ROW[2][0], WIN_ROW[2][1],
           len(WIN_FULL[0][0]), len(WIN_FULL[1][0]), len(WIN_FULL[2][0]),
           len(SEC[2]), len(SEC_F[2]), len(SEC[1]), len(SEC_U[1]),
           SEC_HAN_DELTA, len(SEC_HANS), [z[:20] for z in SEC_HANS],
           inter(SEC_B[0], SEC_B[1]), inter(SEC_B[1], SEC_B[2]),
           len([z for z in SEC_B[2] if z not in SEC_B[1]]), len([z for z in SEC_B[1] if z not in SEC_B[2]]),
           row(sub_cs(u'serialNumber')), row(sub_ci(u'serialNumber')), row(word_ci(u'serialNumber')),
           row([sub_ci(u'serialNumber')[i] - sub_cs(u'serialNumber')[i] for i in range(N)]), row(CAMEL),
           sub_ci(u'serialNumber')[0], sub_cs(u'serialNumber')[0],
           sub_ci(u'octet')[0], word_ci(u'octet')[0], sub_ci(u'octet')[0] - word_ci(u'octet')[0],
           row(word_ci(u'positive')), row(sub_ci(u'positive')), sub_ci(u'positiveint')[0],
           sub_cs(u'Conformant')[1], sub_ci(u'Conformant')[1], LOWDIFF,
           row([sum([l.rstrip(u'\r').count(u'MUST') for l in RAWL[i]]) for i in range(N)]),
           row([LOW[i].count(u'must') for i in range(N)]),
           row([sum([l.rstrip(u'\r').count(u'MAY') for l in RAWL[i]]) for i in range(N)]),
           row([LOW[i].count(u'may') for i in range(N)]),
           der_hex(2 ** 159 - 1), der_hex(2 ** 160 - 1), der_hex(2 ** 63 - 1), der_hex(2 ** 63 + 1),
           len(PAIR_BAD_BARE), ODDFIX, TOT_PAIRS, len(PAIR_BAD), PAIRS[2],
           len(HEXRUNS), 8, u' '.join(HEX), HEX_BYTES[0], HEX_BYTES[1], HEX_VAL, len(u''.join(HEX)),
           row(BRF_CH), row(BRF_159), row(BRF_CSP), row(BRF_CAP),
           SUP_SHELL, SUP_SPACED, SUP_SPACED2, SUP_STICKY, SUP_STICKY2,
           len(HSPACED), len(HSPACED.split(NL)), len(HSTICKY), FLAT['le_stripped_chars'], DISK_LN, SH_N,
           len(PAIRS_AN), len(UNIQ), A_VER, A_WS - A_VER, A_FOLD, len(AN_T), len(A_CASE), A_CASE[0],
           SH_N, E_SHL, E_SPB, len(UNIQ),
           len(set([a for (_t, a), v in zip(PAIRS_AN, AN_T) if v[5] > 0])), A_CROSS,
           n_extra[3], n_extra[4], widest0, positive0, sub_wrap_tot,
           row(FLAT['role_fold'][9]), sum(FLAT['role_line'][9]), FLAT['needle_n'],
           len([1 for k in range(FLAT['needle_n']) if len(FLAT['needle_src'][k]) == 1]),
           FLAT['pick_pairs'], FLAT['pick_agree'], FLAT['pick_diff'],
           FLAT['bool_green'], FLAT['bool_all_n'],
           A_VER, len(AN_T), A_WS, len(AN_T), A_FOLD, len(AN_T),
           len(REG), len([v for v in REG.values() if not v.startswith(u"B95V('")]), len(FLAT),
           row(n_cp), FLAT['pick_pairs'], FLAT['pick_agree'], FLAT['pick_diff'],
           FLAT['bool_green'], FLAT['bool_all_n'])

SPECS = [m for m in re.finditer(u'%[-+ #0]*[0-9.]*[a-zA-Z]', FMT)]
print(u'槽 %d ⇎ 参 %d' % (len(SPECS), len(ARGS)))
if os.environ.get(u'ALIGN') == u'1':
    for i, m in enumerate(SPECS):
        print(u'%3d %-3s %-16r | %s' % (i, m.group(), ARGS[i],
                                        FMT[max(0, m.start() - 30):m.start()]
                                        .replace(u'\n', u'\\n')[-30:]))
    for i in range(len(SPECS), len(ARGS)):
        print(u'多余参 %d %r' % (i, ARGS[i]))
assert len(SPECS) == len(ARGS), u'槽参与数不符'
NOTE = FMT % ARGS

head, _ = md.split(u'## ⛓解读注', 1)
new = head + NOTE
assert new.count(u'## ⟪BabelTele⟫') == 1 and new.count(u'## ⛓解读注') == 1
assert new.count(u'## [[原始语料|ORIGINAL]]') == 1
assert u'(待第四遍复测后写回)' not in new
assert new.count(u'⟦') == new.count(u'⟧') and new.count(u'⟨') == new.count(u'⟩')
if os.environ.get('WRITE') == u'1':
    io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(new)
    print(u'B95 解读注已写回: 注 %d 字符 ⇎ 编码区 %d 字符(%s of 源) ⇎ 锚 %d 处/去重 %d(逐字符 %d ⇎ 折空白 %d '
          u'⇎ 折平 %d) ⇎ 待核见门' % (len(NOTE), ENC_CH, pcta(ENC_CH, SRC_CH), len(PAIRS_AN), len(UNIQ),
                                        A_VER, A_WS, A_FOLD))
else:
    print(u'--- 注草稿(未写回) ---\n' + NOTE)
