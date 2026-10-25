# -*- coding: utf-8 -*-
r"""README 记账: 60 条 → 61 条。合计、唯一码点、推导条数全部取自 audit 的当下输出, 不手填。
本文件是第五套实现, 换算法不换定义: 采集侧 corpus/_pick61.py 用正则族与集合运算符, 建条目侧 corpus/_mkB61.py 用游标
find 循环 + 逐字符判邻后缀 + 排序两指针归并, 门槛侧 audit.py::_b61_scan 是从建条目侧 SCAN 段机械抽出的那一份,
第四遍 corpus/_fill61.py 用切片比对与小集合建表查大集——本遍量源一个 re 都不用(只用 find、切片与字符比较;
import re 只为改 README 的既有句子与从 audit 的输出里刮行, 不参与任何一次测量):
谓词的空白段整段收下后只问“是否恰一枚空格”来分严松两档, 整词计数走手工切出的字母 token 序列, 集合交并走 bisect
于排序后的归一行表(既非集合运算符, 也非两指针), 数 token 的后邻符号用一台 9 字符窗口状态机, 五份字节签名换 sha512
前 8 字节(建条目侧与门槛侧都是 sha256 前 16 位)。
匹配语义照 re 的“最左非重叠”: 逐位试, 试中就把游标跳到命中末尾(所以 (\d+) 取的是极大数字串, 与采集侧一致)。
锚统计直接扫条目 ⟪BabelTele⟫ 段的 ⟦⟧⟨⟩ 游标, 每条串再到本遍现拼的“整篇归一 haystack”里 find 一次
(建条目侧按池位置推, 第四遍按行建表查)。每个数与 corpus/_b61meas.json(采集侧 95 键)、corpus/_b61flat.json(316 键)
双向对表, 注侧元数据与 corpus/_b61checks.json 对表; 本遍全部现量另存 corpus/_b61audit.json, 供日后条目改文时回比。
任一标量对不上就当场停机。本遍不复算 pool_* 六键与 rfc_refs 清单(那是建条目侧按自身行长与去重规则建的锚池,
口径与 num-lines 族不同), 其余按名字逐条对表。"""
import bisect, hashlib, io, json, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
FM = u'corpus/README.md'
NL = chr(10)
TAG = u'B61'
ENTRY = u'corpus/babeltele/B61_ipv6_mtu_five_answers.md'
PATHS = [u'corpus/raw/ipv6/rfc1883.txt', u'corpus/raw/ipv6/rfc2460.txt', u'corpus/raw/ipv6/rfc8200.txt',
         u'corpus/raw/ipv6/rfc2675.txt', u'corpus/raw/ipv6/rfc8201.txt']
TAGS = [u'A', u'B', u'C', u'D', u'E']
LB = [u'95 初版', u'98 标准', u'17 现行', u'超大包档', u'PMTUD 档']
IDX = dict((t, i) for i, t in enumerate(TAGS))
NS = 5
DIG = u'0123456789'
WS = u' \t\n\r\x0b\x0c'
DLM = WS + u',.;:)-'
WLIT = {u'576': u'576', u'1280': u'1280', u'528': u'528', u'1232': u'1232',
        u'c65535': u'65,535', u'c4294967295': u'4,294,967,295', u'jumbo': u'jumbo', u'Jumbo': u'Jumbo'}
KINDS = (u'hy_octet', u'sp_octet', u'wrap_octet', u'comma', u'dot', u'paren', u'other')
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')
RD = lambda q: io.open(q, encoding='utf-8', errors='replace').read()


def sub(old, new, s):
    assert s.count(old) == 1, (u'锚不唯一', s.count(old), old[:60])
    return s.replace(old, new)


def rnd(x):
    return round(x, 4) if isinstance(x, float) else x


def isw(c):
    return (u'a' <= c <= u'z') or (u'A' <= c <= u'Z') or (u'0' <= c <= u'9') or c == u'_'


def pnorm(s):
    o = []
    for c in s.lower():
        if (u'a' <= c <= u'z') or (u'0' <= c <= u'9'):
            o.append(c)
    return u''.join(o)


def occ(s, ndl, frm=0, to=None):
    """非重叠字面计数: 命中后游标跳到末尾(与 str.count 同档, 但走 find 循环)。
    切片必须把 frm 也算上——只给 frm 不给 to 时容易漏切, 那样“尾窗”会退化成整篇。"""
    t = s[frm:] if to is None else s[frm:to]
    c = k = 0
    while True:
        j = t.find(ndl, k)
        if j < 0:
            return c
        c += 1
        k = j + len(ndl)


def wocc(s, word, ci=False):
    """整词档: 左右字符现判是否词字符(采集侧写的是 \\b…\\b)。"""
    low = s.lower() if ci else s
    ndl = word.lower() if ci else word
    c = k = 0
    while True:
        j = low.find(ndl, k)
        if j < 0:
            return c
        e = j + len(ndl)
        if (j == 0 or not isw(s[j - 1])) and (e >= len(s) or not isw(s[e])):
            c += 1
        k = e if e > j else j + 1
    return c


def scan(s, fn, ci=False):
    """照 re.finditer 的最左非重叠语义逐位试 fn(i)→命中末尾下标。"""
    out, i, n = [], 0, len(s)
    while i < n:
        e = fn(i)
        if e is not None and e > i:
            out.append((i, e))
            i = e
        else:
            i += 1
    return out


def wsr(s, j):
    """收下整段空白, 返回 (其后下标, 空白段本身)。"""
    k = j
    while k < len(s) and s[k] in WS:
        k += 1
    return k, s[j:k]


def drun(s, j):
    k = j
    while k < len(s) and s[k] in DIG:
        k += 1
    return k, s[j:k]


def tok_pos(s, lit):
    """`(?<![\\d,])lit(?!\\d)` 的手工档: 返回 token 起始下标表。"""
    out, k = [], 0
    while True:
        j = s.find(lit, k)
        if j < 0:
            return out
        e = j + len(lit)
        if (j == 0 or s[j - 1] not in DIG + u',') and (e >= len(s) or s[e] not in DIG):
            out.append(j)
        k = j + 1


def unit_at(s, off):
    """s[off:] 是 octet / octets 且其后是分隔符或窗口末(9 字符窗的口径)。"""
    if s[off:off + 5] != u'octet':
        return False
    e = off + 6 if s[off + 5:off + 6] == u's' else off + 5
    return e >= len(s) or s[e] in DLM


def kind_after(t, b):
    """b 是 token 末位下标; 在其后 9 字符窗口上按状态机分档(先连字符, 再单空格, 再折行)。"""
    r = t[b:b + 9]
    if r[:6] == u'-octet':
        return u'hy_octet'
    if r[:1] == u' ' and unit_at(r, 1):
        return u'sp_octet'
    q, g = wsr(r, 0)
    if g and unit_at(r, q):
        return u'wrap_octet'
    h = r[:1]
    if h == u',':
        return u'comma'
    if h == u'.':
        return u'dot'
    if h == u')':
        return u'paren'
    return u'other'


def head_line(l):
    """编号标题行: 行首至多三空格 + 数字组(.数字)* + 可选点 + 空格或制表 + 非空白, 且行末是字母。
    返回采集侧正则捕获组本身(纯编号, 不含尾点与空白), 这样“不同编号数”一档才对得上。"""
    sp = 0
    while sp < len(l) and l[sp] == u' ':
        sp += 1
    if sp > 3 or sp >= len(l) or l[sp] not in DIG:
        return None
    i = sp
    while i < len(l) and l[i] in DIG:
        i += 1
    while i + 1 < len(l) and l[i] == u'.' and l[i + 1] in DIG:
        i += 2
        while i < len(l) and l[i] in DIG:
            i += 1
    num = l[sp:i]
    if i < len(l) and l[i] == u'.':
        i += 1
    j = i
    while j < len(l) and l[j] in u' \t':
        j += 1
    if j == i or j >= len(l) or l[j] in WS:
        return None
    if not ((u'a' <= l[-1] <= u'z') or (u'A' <= l[-1] <= u'Z')):
        return None
    return num


def clo_line_of(t):
    """变更记录附录定位: 整行扫、两支同收、取最后一处命中的行首(目录页也印同一枚标题)。"""
    last = -1
    p = 0
    for l in t.split(NL):
        k = 0
        while k < len(l) and l[k] == u' ' and k < 5:
            k += 1
        if k <= 4:
            hit = l.startswith(u'This memo has the following changes from', k)
            if not hit and l[k:k + 9] == u'Appendix ':
                if l[k + 9:k + 10].isupper() and l[k + 10:k + 11] == u'.':
                    j = k + 11
                    ns = 0
                    while j < len(l) and l[j] == u' ' and ns < 2:
                        j += 1
                        ns += 1
                    hit = ns >= 1 and l[j:j + 7] == u'Changes'
            if hit:
                last = p
        p += len(l) + 1
    return last


def sec_span(t):
    """§5 窗: 首个以“5. ”起的标题行到首个“6. ”行(按字符下标切, 与采集侧 re.search 同档)。"""
    a = b = -1
    p = 0
    for l in t.split(NL):
        for d, cur in ((u'5', a), (u'6', b)):
            if cur < 0 and l[:1] == d and l[1:2] == u'.':
                j, g = wsr(l, 2)
                if g and j < len(l) and l[j] not in WS:
                    if d == u'5':
                        a = p
                    else:
                        b = p
        p += len(l) + 1
    return (a, b) if a >= 0 and b > a else (-1, -1)


# ---------- 1) 门槛现取 ----------
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
OUT = p.stdout
assert u'保真门槛' in OUT and u'PASS' in OUT, OUT[-600:]
row = {}
for l in OUT.split(NL):
    if not l.startswith(u'| '):
        continue
    parts = [x.strip() for x in l.strip(u'|').split(u'|')]
    k = parts[0]
    if (k[:1] == u'B' and k[1:].isdigit()) or k == u'ALL':
        row[k] = parts[1:]
NENT = len([k for k in row if k != u'ALL'])
assert NENT == 61, NENT
b61, A = row[u'B61'], row[u'ALL']
dig_all, enc_all = int(A[0].replace(u' ', u'')), int(A[1].replace(u' ', u''))
uniq_all = int(re.sub(u'[^0-9]', u'', A[4]))
assert (sum(int(v[0].replace(u' ', u'')) for k, v in row.items() if k != u'ALL'),
        sum(int(v[1]) for k, v in row.items() if k != u'ALL')) == (dig_all, enc_all)
assert b61[7:10] == [u'0', u'0', u'0'], b61  # T1⇎T2⇎T3 三档全零; 第 10 列是 1–2 位待核计数(B61 有 0 项)
soft_all = proofs = None
HINT = {}
for l in OUT.split(NL):
    if l.startswith(u'提示') and u'共' in l:
        soft_all = int(l.split(u'共')[1].split(u' 个')[0])
    if l.startswith(u'已机检的推导'):
        proofs = int(l.split(u'(')[1].split(u' 条)')[0])
    m2 = re.match(u'^   (B\\d\\d) (\\[.*\\])$', l)
    if m2:
        HINT[m2.group(1)] = eval(m2.group(2), {'__builtins__': {}}, {})
assert sum(len(v) for v in HINT.values()) == soft_all, (HINT, soft_all)
H61 = HINT.get(u'B61') or []
assert sorted(H61) == [u'48', u'55', u'95', u'98'], H61
dig61, enc61 = int(b61[0]), int(b61[1])
ret_tot = A[2].replace(u'*', u'')

CH = json.load(io.open(u'corpus/_b61checks.json', encoding='utf-8'))
FLAT = json.load(io.open(u'corpus/_b61flat.json', encoding='utf-8'))
MEAS = json.load(io.open(u'corpus/_b61meas.json', encoding='utf-8'))
assert enc61 == CH[u'enc_chars'] == 7641, (enc61, CH[u'enc_chars'])
Q5 = {}


def q(name, val):
    """本遍现量登记: 凡契约里同名的键必须逐值相等, 采集侧 meas 里同名的键亦然。"""
    Q5[name] = val
    if name in FLAT:
        assert rnd(val) == rnd(FLAT[name]), (name, val, FLAT[name])
    if name in MEAS:
        assert rnd(val) == rnd(MEAS[name]), (name, val, MEAS[name])
    return val


def m(name):
    return Q5[name]


def five(f):
    return [f(k) for k in range(NS)]


RB = [io.open(x, u'rb').read() for x in PATHS]
T = [r.decode(u'utf-8', u'replace') for r in RB]
assert all(r.count(b'\r') == 0 for r in RB), u'本遍按纯 LF 面写, 有 CR 就得改口径'
LOW = [t.lower() for t in T]
LST = [t.split(NL) for t in T]
FAN = [pnorm(t) for t in T]

# ---- 形状 ----
q(u'bytes', five(lambda i: len(RB[i])))
q(u'chars', five(lambda i: len(T[i])))
q(u'lines', five(lambda i: len(LST[i])))
q(u'nonblank', five(lambda i: len([l for l in LST[i] if l.strip()])))
q(u'maxlen', five(lambda i: max(len(l) for l in LST[i])))
q(u'trail', five(lambda i: len([l for l in LST[i] if l != l.rstrip()])))
q(u'cr', five(lambda i: occ(T[i], u'\r')))
q(u'nonascii', five(lambda i: len([c for c in T[i] if ord(c) > 127])))
q(u'pipe', five(lambda i: occ(T[i], u'|')))
q(u'dashes', five(lambda i: occ(T[i], u'-')))
# 签名换算法: 建条目侧与门槛侧是 sha256 前 16 位(FLAT 的 sig 键), 本遍取 sha512 前 8 位, 故另起键名、不与 sig 对表;
# 只比“五份字节签名互不相同”这一枚标量(sig_distinct), 它两遍同值才进契约。
q(u'sig512_8', [hashlib.sha512(RB[i]).hexdigest()[:8] for i in range(NS)])
q(u'sig_distinct', len(set(m(u'sig512_8'))))

# ---- 字面 ⇎ token ⇎ 差值 ----
for lit in (u'576', u'1280', u'528', u'1232', u'65535', u'4294967295', u'9000', u'1500', u'2048',
            u'1480', u'1492', u'1452'):
    q(u'lit_' + lit, five(lambda i, lit=lit: occ(T[i], lit)))
for k in (u'c65535', u'c4294967295'):
    q(u'lit_' + k, five(lambda i, k=k: occ(T[i], WLIT[k])))
for lit in (u'576-octet', u'1280-octet'):
    q(u'lit_' + lit, five(lambda i, lit=lit: occ(T[i], lit)))
for k in (u'576', u'1280', u'528', u'1232', u'65535', u'1500', u'1480', u'2112',
          u'c65535', u'c4294967295'):
    ndl = WLIT.get(k, k)
    q(u'tok_' + k, five(lambda i, ndl=ndl: len(tok_pos(T[i], ndl))))
    if u'lit_' + k in Q5:
        q(u'subgap_' + k, [m(u'lit_' + k)[i] - m(u'tok_' + k)[i] for i in range(NS)])

# ---- 后邻符号分区 ----
for k in (u'576', u'1280', u'528', u'1232', u'c65535'):
    ndl = WLIT.get(k, k)
    mat = [[(j, j + len(ndl)) for j in tok_pos(T[i], ndl)] for i in range(NS)]
    cnt = [{c: 0 for c in KINDS} for i in range(NS)]
    for i in range(NS):
        for a, b in mat[i]:
            cnt[i][kind_after(T[i], b)] += 1
    for c in KINDS:
        q(u'sk_%s_%s' % (k, c), [cnt[i][c] for i in range(NS)])
    q(u'sk_%s_total' % k, five(lambda i: len(mat[i])))
    q(u'sk_%s_close' % k, [sum(cnt[i].values()) - len(mat[i]) for i in range(NS)])

# ---- 折行通道双档 ----
def seq_count(s, blocks, flex, ci=False):
    """最左非重叠地数“字面块 + 段间空白”的序列; 返回 (处数, 数字串表)。"""
    out, hits, i, n = [], [], 0, len(s)
    low = s.lower() if ci else s
    while i < n:
        k = i
        ok = True
        digs = []
        for bi, blk in enumerate(blocks):
            if bi:
                if flex:
                    k2, g = wsr(low, k)
                    if not g:
                        ok = False
                        break
                    k = k2
                else:
                    if low[k:k + 1] != u' ':
                        ok = False
                        break
                    k += 1
            if blk == u'D':
                k2, g = drun(low, k)
                if not g:
                    ok = False
                    break
                digs.append(g)
                k = k2
            else:
                w = blk.lower() if ci else blk
                if low[k:k + len(w)] != w:
                    ok = False
                    break
                k += len(w)
        if ok:
            hits.append(digs)
            out.append(k)
            i = k
        else:
            i += 1
    return len(out), hits


def seq_count_s(s, line):
    """恰一枚空格档: 整串按单空格切开再逐块衔接(数字块用 'D' 占位)。"""
    return seq_count(s, line.split(u' '), False)[0]


FLOORW = [u'have an MTU of', u'D']
# 上限句两档必须用同一对键相减(与建条目侧同一条纪律)
wf = [seq_count(T[i], FLOORW, True) for i in range(NS)]
q(u'w_floor_sent', [x[0] for x in wf])
q(u'floor_vals', [[d[0] for d in x[1]] for x in wf])
for i in range(NS):
    q(u'floor_vals_' + TAGS[i], Q5[u'floor_vals'][i])
sf = [seq_count_s(T[i], u'have an MTU of D octets') for i in range(NS)]
q(u's_floor_sent', sf)
q(u'wrap_gap_floor_sent', [m(u'w_floor_sent')[i] - sf[i] for i in range(NS)])
def pf_pairs(s):
    """`N octets (M minus` 档: 极大数字串 + 单空格 + 'octets (' + 数字 + 单空格 + 'minus'(与采集侧同一条正则)。
    两处定长面宽度: ' octets (' 是 9 枚字符、' minus' 是 6 枚——切片宽度必须跟着字面串本身, 差一枚就恒不匹配。"""
    out, i, n = [], 0, len(s)
    while i < n:
        if s[i] in DIG:
            j, a = drun(s, i)
            if s[j:j + 9] == u' octets (':
                k2, b = drun(s, j + 9)
                if b and s[k2:k2 + 6] == u' minus':
                    out.append([a, b])
                    i = k2 + 6
                    continue
        i += 1
    return out


pf = [pf_pairs(T[i]) for i in range(NS)]
# 门槛主账的“净载荷算式”两档用的是字面针 octets (576 minus ——建条目侧与门槛侧同一条针, 故 98 标准那句 1232/1280 不算命中;
# 本遍把针拆成 “octets + 整段空白 + (576 minus” 逐段接, 与那一条字面 count 同定义、不同走法。
PFL = u'octets (576 minus'


def pf_flex(s):
    c, k = 0, 0
    while True:
        j = s.find(u'octets', k)
        if j < 0:
            return c
        p2, g = wsr(s, j + 6)
        if g and s[p2:p2 + 10] == u'(576 minus':
            c += 1
        k = j + 6


q(u'w_payload_floor', [pf_flex(T[i]) for i in range(NS)])
q(u's_payload_floor', [occ(T[i], PFL) for i in range(NS)])
q(u'wrap_gap_payload_floor', [m(u'w_payload_floor')[i] - m(u's_payload_floor')[i] for i in range(NS)])
q(u'pfloor_pair', pf)
for i in range(NS):
    q(u'pfloor_pair_' + TAGS[i], Q5[u'pfloor_pair'][i])
    q(u'pfloor_pair_' + TAGS[i] + u'_n', len(Q5[u'pfloor_pair'][i]))
q(u'w_min_mtu', [seq_count(T[i], [u'minimum IPv6 MTU from', u'D', u'to', u'D'], True)[0] for i in range(NS)])
q(u's_min_mtu', [seq_count_s(T[i], u'minimum IPv6 MTU from D to D') for i in range(NS)])
q(u'wrap_gap_min_mtu', [m(u'w_min_mtu')[i] - m(u's_min_mtu')[i] for i in range(NS)])
q(u'w_jumbo_opt', [seq_count(T[i], [u'Jumbo', u'Payload', u'option'], True)[0] for i in range(NS)])
q(u's_jumbo_opt', [occ(T[i], u'Jumbo Payload option') for i in range(NS)])
q(u'wrap_gap_jumbo_opt', [m(u'w_jumbo_opt')[i] - m(u's_jumbo_opt')[i] for i in range(NS)])
q(u'wrap_gap_jumbo', m(u'wrap_gap_jumbo_opt'))
q(u'w_routers', [seq_count(T[i], [u'not by', u'routers'], True)[0] for i in range(NS)])
q(u's_routers', [occ(T[i], u'not by routers') for i in range(NS)])
q(u'wrap_gap_routers', [m(u'w_routers')[i] - m(u's_routers')[i] for i in range(NS)])
q(u'w_frag_src', [seq_count(T[i], [u'performed only by source', u'nodes'], True)[0] for i in range(NS)])
q(u's_frag_src', [occ(T[i], u'performed only by source nodes') for i in range(NS)])
q(u'wrap_gap_frag_src', [m(u'w_frag_src')[i] - m(u's_frag_src')[i] for i in range(NS)])
q(u'wrap_gap_frag', m(u'wrap_gap_frag_src'))
q(u'w_1280_oct', [seq_count(T[i], [u'1280', u'octets'], True)[0] for i in range(NS)])
q(u's_1280_oct', [occ(T[i], u'1280 octets') for i in range(NS)])
q(u'wrap_gap_1280_oct', [m(u'w_1280_oct')[i] - m(u's_1280_oct')[i] for i in range(NS)])
q(u'wrap_gap_1280', m(u'wrap_gap_1280_oct'))
q(u'w_576_oct', [seq_count(T[i], [u'576', u'octets'], True)[0] for i in range(NS)])
q(u's_576_oct', [occ(T[i], u'576 octets') for i in range(NS)])
q(u'wrap_gap_576_oct', [m(u'w_576_oct')[i] - m(u's_576_oct')[i] for i in range(NS)])
q(u'minmtu_sent', [seq_count(LOW[i], [u'every link in the', u'internet have an mtu of'], True)[0]
                   for i in range(NS)])  # 针一律小写: 本遍把面折成小写再逐段接(采集侧靠 (?i) 同档)
q(u'at_least', [seq_count(LOW[i], [u'at least', u'D'], False)[0] for i in range(NS)])
q(u'src_only', [occ(T[i], u'performed only by source nodes') for i in range(NS)])
q(u'not_routers', [occ(T[i], u'not by routers') for i in range(NS)])

# ---- jumbo / 分片 / MTU 语汇 ----
q(u'jumbo_ci', [occ(LOW[i], u'jumbo') for i in range(NS)])
q(u'jumbo_caps', [occ(T[i], u'Jumbo') for i in range(NS)])
q(u'jumbo_word', [wocc(T[i], u'jumbo', True) for i in range(NS)])
q(u'jumbo_payload', [occ(LOW[i], u'jumbo payload') for i in range(NS)])
q(u'jumbo_option_def', [occ(T[i], u'Jumbo Payload option') for i in range(NS)])
q(u'remove_note', [occ(T[i], u'Removed all references to jumbograms') for i in range(NS)])
q(u'frag_ci', [occ(LOW[i], u'fragment') for i in range(NS)])
q(u'frag_word', [wocc(T[i], u'fragment', True) for i in range(NS)])
q(u'frag_head', [occ(LOW[i], u'fragment header') for i in range(NS)])  # 门槛这条是单空格档(采侧 (?i)fragment header)
q(u'frag_head_flex', [seq_count(LOW[i], [u'fragment', u'header'], True)[0] for i in range(NS)])
q(u'frag_head_wrap', [m(u'frag_head_flex')[i] - m(u'frag_head')[i] for i in range(NS)])
q(u'frag_head_caps', [seq_count(T[i], [u'Fragment', u'header'], False)[0] for i in range(NS)])
q(u'frag_noun', [occ(LOW[i], u'fragmentation') for i in range(NS)])
q(u'frag_and_reas', [seq_count(LOW[i], [u'fragmentation and reassembly'], True)[0] for i in range(NS)])
q(u'mtu_any', [occ(LOW[i], u'mtu') for i in range(NS)])
q(u'MTU_caps', [occ(T[i], u'MTU') for i in range(NS)])
q(u'link_mtu', [occ(LOW[i], u'link mtu') for i in range(NS)])
q(u'path_mtu', [occ(LOW[i], u'path mtu') for i in range(NS)])
q(u'pmtu', [occ(T[i], u'PMTU') for i in range(NS)])
q(u'ptb', [occ(LOW[i], u'packet too big') for i in range(NS)])

# ---- 义务词体例 ----
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED', u'RECOMMENDED', u'OPTIONAL'):
    q(u'u_' + w.replace(u' ', u'_').lower(), [occ(T[i], w) for i in range(NS)])
for w in (u'must', u'should', u'may', u'required', u'recommended', u'optional', u'allowed', u'needed'):
    q(u'l_' + w, [wocc(T[i], w) for i in range(NS)])
for w in (u'Must', u'Should', u'May'):
    q(u'c_' + w.lower(), [wocc(T[i], w) for i in range(NS)])
q(u'l_must_ci', [wocc(T[i], u'must', True) for i in range(NS)])
q(u'oblig_up', [m(u'u_must')[i] + m(u'u_should')[i] + m(u'u_may')[i] + m(u'u_required')[i]
                + m(u'u_recommended')[i] + m(u'u_must_not')[i] + m(u'u_should_not')[i] for i in range(NS)])
q(u'oblig_low', [m(u'l_must')[i] + m(u'l_should')[i] + m(u'l_may')[i] for i in range(NS)])
q(u'rfc2119_ref', [occ(T[i], u'2119') for i in range(NS)])
q(u'rfc8174_ref', [occ(T[i], u'8174') for i in range(NS)])
q(u'key_words_boiler', [occ(T[i], u'key words') + occ(T[i], u'Key words') for i in range(NS)])
q(u'lowercase_selfdoc', [seq_count(LOW[i], [u'only uses lower case'], True)[0] for i in range(NS)])
q(u'no_cite_2119', [occ(LOW[i], u"doesn't cite rfc 2119") + occ(LOW[i], u'does not cite the rfc 2119 definitions')
                    for i in range(NS)])

# ---- 文档身份 ----
def hdr(t, pre):
    """抬头字段行: 采集侧写的是 `^Obsoletes: \\d+`(列 0, 不容缩进)。"""
    c = 0
    for l in t.split(NL):
        if l[:len(pre)].lower() == pre and l[len(pre):len(pre) + 1] in DIG:
            c += 1
    return c


q(u'obsoletes_hdr', [hdr(t, u'obsoletes: ') for t in T])
q(u'updates_hdr', [hdr(t, u'updates: ') for t in T])
q(u'category_std', [occ(T[i], u'Category: Standards Track') for i in range(NS)])
q(u'category_exp', [occ(T[i], u'Experimental') for i in range(NS)])
q(u'stds_stmt', [occ(T[i], u'Standards Track') for i in range(NS)])
q(u'obsoleted_by', [occ(LOW[i], u'obsoleted by') for i in range(NS)])
q(u'errata', [occ(LOW[i], u'errata') for i in range(NS)])


def loghead(t):
    """变更记录条目行: 行首恰 1–4 枚空格 + 两位数字 + “) ”(五枚以上不算, 与采集侧 `^ {1,4}` 同档)。"""
    c = 0
    for l in t.split(NL):
        k = 0
        while k < len(l) and l[k] == u' ':
            k += 1
        if 1 <= k <= 4 and len(l) > k + 3 and l[k] in DIG and l[k + 1] in DIG and l[k + 2:k + 4] == u') ':
            c += 1
    return c


q(u'change_log_head', [loghead(t) for t in T])


def rfcrefs(t):
    out, i = set(), 0
    while True:
        j = t.find(u'RFC', i)
        if j < 0:
            return out
        k = j + 3
        if t[k:k + 1] in WS:
            k += 1
        g = t[k:k + 4]
        if len(g) == 4 and all(c in DIG for c in g):
            out.add(g)
        i = j + 3


q(u'rfc_ref_n', five(lambda i: len(rfcrefs(T[i]))))
q(u'section_cite', five(lambda i: len([1 for j in range(len(T[i]))
                                       if T[i][j:j + 7].lower() == u'section' and (j == 0 or not isw(T[i][j - 1]))
                                       and T[i][j + 7:j + 8] == u' ' and T[i][j + 8:j + 9] in DIG])))
q(u'sec_head', five(lambda i: len([h for h in (head_line(l) for l in LST[i]) if h])))
q(u'sec_head_d', five(lambda i: len(set(h for h in (head_line(l) for l in LST[i]) if h))))

# ---- 两窗: 变更记录附录 ⇎ 正文 ----
CS = [clo_line_of(t) for t in T]
q(u'clo_found', [1 if c >= 0 else 0 for c in CS])
q(u'clo_line', five(lambda i: 0 if CS[i] < 0 else 1 + occ(T[i], NL, 0, CS[i])))
for k in sorted(WLIT):
    body, tail = [], []
    for i in range(NS):
        if CS[i] < 0:
            body.append(occ(T[i], WLIT[k]))
            tail.append(0)
        else:
            body.append(occ(T[i], WLIT[k], 0, CS[i]))
            tail.append(occ(T[i], WLIT[k], CS[i]))
    q(u'body_' + k, body)
    q(u'tail_' + k, tail)
    q(u'close_' + k, [body[i] + tail[i] - occ(T[i], WLIT[k]) for i in range(NS)])
q(u'comma_only', m(u'tok_c65535'))
SP = [sec_span(t) for t in T]
for k in (u'576', u'1280', u'528', u'1232', u'c65535'):
    q(u'sec5_' + k, five(lambda i, k=k: occ(T[i], WLIT[k], SP[i][0], SP[i][1]) if SP[i][0] >= 0 else 0))
    for i in range(NS):
        q(u'sec5_%s_%s' % (k, TAGS[i]), Q5[u'sec5_' + k][i])
# 门边的 §5 窗是 NL.join(行 a..行 b−1): 本遍按字符下标切出的那段多带末行换行一枚, 故减一才同长。
q(u'sec5_len', five(lambda i: (SP[i][1] - SP[i][0] - 1) if SP[i][0] >= 0 else 0))

# ---- 整行搬运: 归一表 + bisect ----
LN = [sorted(set(pnorm(l) for l in LST[i] if len(l.strip()) >= 40 and pnorm(l))) for i in range(NS)]
has = lambda a, x: a[bisect.bisect_left(a, x):][:1] == [x]
q(u'lines_ge40', five(lambda i: len(LN[i])))
for a in range(NS):
    for b in range(a + 1, NS):
        small, big = (LN[a], LN[b]) if len(LN[a]) <= len(LN[b]) else (LN[b], LN[a])
        q(u'share_%s%s' % (TAGS[a], TAGS[b]), len([x for x in small if has(big, x)]))
q(u'AB_C_inter', len([x for x in LN[0] if has(LN[1], x) and has(LN[2], x)]))
merged = sorted(LN[0] + LN[1] + LN[2])
uniq = [x for i, x in enumerate(merged) if i == 0 or merged[i - 1] != x]
q(u'union_ABC', len(uniq))
q(u'only_A', len([x for x in LN[0] if not has(LN[1], x) and not has(LN[2], x)]))
q(u'only_B', len([x for x in LN[1] if not has(LN[0], x) and not has(LN[2], x)]))
q(u'only_C', len([x for x in LN[2] if not has(LN[0], x) and not has(LN[1], x)]))
q(u'abc_close', m(u'only_A') + m(u'only_B') + m(u'only_C') + m(u'share_AB') + m(u'share_AC')
  + m(u'share_BC') - 2 * m(u'AB_C_inter') - m(u'union_ABC'))

# ---- 含关键数字的长行 ----
NEED = [u'576', u'1280', u'528', u'1232', u'65,535', u'4,294,967,295', u'jumbo', u'Jumbo']
q(u'num-lines', five(lambda i: len([l for l in LST[i] if len(l.strip()) >= 55
                                    and any(x in l for x in NEED)])))
for i in range(NS):
    q(u'num-lines ' + TAGS[i], Q5[u'num-lines'][i])
    q(u'num-lines_' + TAGS[i], Q5[u'num-lines'][i])

# ---- 锚: 扫条目 ⟪BabelTele⟫ 段 ----
MD = RD(ENTRY)
head = MD.find(u'## ⟪BabelTele⟫')
tail = MD.find(u'## ⛓解读注')
assert 0 <= head < tail, (head, tail)
BODY = MD[head + len(u'## ⟪BabelTele⟫'):tail].strip(NL)
cur, anchors, tc = None, [], dict((t, 0) for t in TAGS)
k = 0
while k < len(BODY):
    if BODY[k] == u'⟦':
        e = BODY.find(u'⟧', k)
        t = BODY[k + 1:e]
        if t in tc:
            tc[t] += 1
            cur = t
        k = e + 1
        continue
    if BODY[k] == u'⟨' and cur is not None and BODY[k - 1] == u'⟧':
        e = BODY.find(u'⟩', k)
        anchors.append((cur, BODY[k + 1:e]))
        k = e + 1
        continue
    k += 1
DIST = sorted(set(x for _t, x in anchors), key=len, reverse=True)
HITN = dict((a, len([i for i in range(NS) if pnorm(a) and FAN[i].find(pnorm(a)) >= 0])) for a in DIST)
q(u'anchor_total', len(anchors))
q(u'anchor_distinct', len(DIST))
q(u'anchor_err', len([x for x in anchors if x[0] and FAN[IDX[x[0]]].find(pnorm(x[1])) < 0]))
q(u'anchor_single', len([a for a in DIST if HITN[a] == 1]))
q(u'anchor_cross', len([a for a in DIST if 1 < HITN[a] < NS]))
q(u'anchor_all5', len([a for a in DIST if HITN[a] == NS]))
q(u'checks', m(u'anchor_distinct') * NS)
assert sum(tc.values()) == m(u'anchor_total'), tc
assert tc == CH[u'tag_counts'], (tc, CH[u'tag_counts'])
assert m(u'anchor_single') + m(u'anchor_cross') + m(u'anchor_all5') == m(u'anchor_distinct')
for t in TAGS:
    q(u'tag_' + t, tc[t])
for a in (u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single', u'anchor_cross',
          u'anchor_all5', u'checks'):
    assert Q5[a] == CH[u'ameta'][a], (a, Q5[a], CH[u'ameta'][a])
q(u'letters_in', sum(len([c for c in a if (u'a' <= c <= u'z') or (u'A' <= c <= u'Z')]) for a in DIST))
OUT5, k = [], 0
while k < len(BODY):
    if BODY[k] == u'⟨':
        e = BODY.find(u'⟩', k)
        if e > 0:
            k = e + 1
            continue
    OUT5.append(BODY[k])
    k += 1
q(u'letters_out', len([c for c in u''.join(OUT5) if (u'a' <= c <= u'z') or (u'A' <= c <= u'Z')]))
q(u'enc_self', len(BODY.replace(NL, u'')))
assert m(u'letters_in') == CH[u'letters_in'] and m(u'letters_out') == CH[u'letters_out'], \
    (m(u'letters_in'), CH[u'letters_in'], m(u'letters_out'), CH[u'letters_out'])
assert m(u'enc_self') == enc61 == CH[u'enc_chars'], (m(u'enc_self'), enc61)
ATT = [x for x in RD(u'corpus/_atoms61.txt').split(NL) if x]
assert sorted(ATT) == sorted(DIST), u'原子清单与 _atoms61.txt 不同'

DJO = json.load(io.open(u'corpus/_deriv61.json', encoding='utf-8'))
OCC = sum(v.count(u'B61V') for v in DJO.values())
assert CH[u'deriv_keys'] == len(DJO) == 94, (CH, len(DJO))
# 两处口径不同: OCC 数 DERIV 算式串里 B61V 的字面出现次数(复合式把同一枚算式抄进 max([..]) 与 min([..]) 各一次),
# deriv_points 是建条目侧按“值→算式”登记的条数。
assert OCC > 0 and CH[u'deriv_points'] == 290, (OCC, CH[u'deriv_points'])
NMEAS = len([k for k in MEAS if k[:1] != u'_'])
assert len([k for k in MEAS if k[:1] != u'_']) == 95, NMEAS
TIED = [k for k in MEAS if k[:1] != u'_' and k in Q5]
assert len(TIED) == NMEAS, sorted(set(MEAS) - set(Q5) - set([u'_plain_idx']))
for kk in TIED:
    assert rnd(MEAS[kk]) == rnd(Q5[kk]), (kk, MEAS[kk], Q5[kk])

AUDSN = dict(Q5)
AUDSN[u'_paths'] = PATHS
json.dump(AUDSN, io.open(u'corpus/_b61audit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# ---------- 3) 逐处替换 ----------
K = dict(FLAT)
K.update(Q5)
jt = lambda xs: u', '.join(str(x) for x in xs)
jn = lambda nm: (u' ⇎ '.join(str(x) for x in Q5[nm]) if isinstance(Q5[nm], list) else str(Q5[nm]))
for nm in (u'bytes', u'chars', u'lines', u'nonblank', u'maxlen', u'trail', u'cr', u'nonascii',
           u'w_floor_sent', u's_floor_sent',
           u'wrap_gap_floor_sent', u'floor_vals', u'minmtu_sent', u'clo_found', u'clo_line', u'body_576',
           u'tail_576', u'body_1280', u'tail_1280', u'body_Jumbo', u'tail_Jumbo', u'close_576',
           u'lit_c65535', u'lit_65535', u'lit_c4294967295', u'jumbo_option_def', u'w_jumbo_opt', u'wrap_gap_jumbo',
           u'jumbo_ci', u'jumbo_caps', u'remove_note', u's_jumbo_opt', u's_routers', u'w_routers', u'src_only', u'pmtu',
           u'u_must', u'u_should', u'u_may', u'l_must', u'l_should', u'l_may', u'rfc2119_ref', u'lowercase_selfdoc',
           u'no_cite_2119', u'obsoletes_hdr', u'category_std', u'category_exp', u'errata', u'lines_ge40',
           u'share_AB', u'share_BC', u'share_AC', u'share_CD', u'share_CE', u'num-lines', u'sec5_1280', u'at_least',
           u'sec5_len', u'rfc_ref_n', u'section_cite', u'pfloor_pair', u'tok_1500'):
    if nm in Q5:
        K[u'j_' + nm] = jn(nm)
K.update({
    u'j_floor_vals': u' ⇎ '.join(u'[%s]' % u','.join(x) for x in m(u'floor_vals')),
    u'j_pfloor_pair': u' ⇎ '.join(u'[%s]' % u','.join(u'/'.join(y) for y in x) for x in m(u'pfloor_pair')),
    u'j_sk576': u'%d+%d+%d+%d+%d+%d+%d' % tuple(Q5[u'sk_576_' + c][0] for c in KINDS),
    u'jnl': u' ⇎ '.join(str(x) for x in m(u'num-lines')),
    u'tA': tc[u'A'], u'tB': tc[u'B'], u'tC': tc[u'C'], u'tD': tc[u'D'], u'tE': tc[u'E'],
    u'coll': len(CH[u'collisions']), u'zeros': CH[u'zero_terms'],
    u'deriv_keys': CH[u'deriv_keys'], u'deriv_points': OCC, u'dedup_points': CH[u'deriv_points'],
    u'enc': enc61, u'dig': dig61, u'proofs': proofs, u'nent': NENT, u'nmeas': len(Q5),
    u'flatn': len(FLAT), u'hints': u'／'.join(u'`%s`' % x for x in H61), u'nhint': len(H61),
    u'bytesA': fmt(m(u'bytes')[0]), u'bytesB': fmt(m(u'bytes')[1]), u'bytesC': fmt(m(u'bytes')[2]),
    u'bytesD': fmt(m(u'bytes')[3]), u'bytesE': fmt(m(u'bytes')[4]),
    u'nbA': fmt(m(u'nonblank')[0]), u'nbB': fmt(m(u'nonblank')[1]), u'nbC': fmt(m(u'nonblank')[2]),
    u'nbD': fmt(m(u'nonblank')[3]), u'nbE': fmt(m(u'nonblank')[4]),
    u'linesA': m(u'lines')[0], u'linesB': m(u'lines')[1], u'linesC': m(u'lines')[2],
    u'linesD': m(u'lines')[3], u'linesE': m(u'lines')[4]})

NEWPAR = (
    u'**B61 问的是一条链路至少要装多少字节、一个 IPv6 包最大能多大, 五份一手规范给出五种答法**：`raw/ipv6/rfc1883.txt`'
    u'（95 初版 ⟦A⟧：{bytesA} 字节／非空行 {nbA}／行数 {linesA}） ⇎ `rfc2460.txt`（98 标准 ⟦B⟧：{bytesB}／{nbB}） ⇎ '
    u'`rfc8200.txt`（17 现行 ⟦C⟧：{bytesC}／{nbC}） ⇎ `rfc2675.txt`（超大包档 ⟦D⟧：{bytesD}／{nbD}） ⇎ '
    u'`rfc8201.txt`（PMTUD 档 ⟦E⟧：{bytesE}／{nbE}）——五份全是 RFC Editor 的纯文本面, 回车 {j_cr} ⇎ 非 ASCII 字符 {j_nonascii} ⇎ '
    u'最长行 {j_maxlen} 列, 所以本条没有剥壳层, 差异全在“同一条链路要求被写成什么样”。'
    u'门槛主账是下限句谓词 have an MTU of + 数字 + octets：空白容忍档 {j_w_floor_sent} 句 ⇎ 单空格档 {j_s_floor_sent} 句, '
    u'差额 {j_wrap_gap_floor_sent} 处全是被排版折行的那几处（同一通道对 not by⇎routers 与 Jumbo⇎Payload⇎option 也成立: '
    u'{j_w_routers} ⇎ {j_s_routers}、{j_w_jumbo_opt} ⇎ {j_s_jumbo_opt}）; 现读的数 {j_floor_vals}——'
    u'同一枚句式在 95 初版要到 576、在两代后续文书都要到 1280, 而超大包档与 PMTUD 档通篇不写这条下限（整句谓词 every link in the internet have an MTU of '
    u'{j_minmtu_sent} ⇎ at least + 数字 {j_at_least}）。'
    u'“这条要求还在不在”取决于窗口: 附录定位行两支同收（“Appendix 字母.  Changes…” ⇎ “This memo has the following changes from…”）、'
    u'取最后一处命中（目录页也印同一枚标题）, 行号 {j_clo_line}、命中 {j_clo_found}; '
    u'576 正文 {j_body_576} ⇎ 变更记录 {j_tail_576}（相加校住字面处数, 闭合 {j_close_576}）, 1280 {j_body_1280} ⇎ {j_tail_1280}, '
    u'Jumbo 大写 {j_body_Jumbo} ⇎ {j_tail_Jumbo}——98 标准正文里 576 是 0 处, 它只剩变更记录那一句“把最小 MTU 从 576 改成 1280”。'
    u'净载荷算式 95 初版 {j_pfloor_pair} ⇎ 1232=1280−48 ⇎ 17 现行把这句整段删了。'
    u'包顶只有带千分位一种写法: 65,535 {j_lit_c65535} 处 ⇎ 无逗号 65535 {j_lit_65535}（全 0）⇎ 4,294,967,295 只在超大包档 {j_lit_c4294967295} 处; '
    u'数 token 的后邻符号七档相加校住 token 数: 576 在 95 初版 {j_sk576}（合计 {sk_576_total[0]}, 差 {sk_576_close[0]}）, '
    u'1280 在 98 标准 {sk_1280_total[1]} 处、单空格 {sk_1280_sp_octet[1]} ⇎ 折行 {sk_1280_wrap_octet[1]}。'
    u'超大包选项的一生: 定义逐字面 {j_jumbo_option_def}（折平档 {j_w_jumbo_opt}, 差 {j_wrap_gap_jumbo}）⇎ jumbo 全族 {j_jumbo_ci} ⇎ 大写 {j_jumbo_caps}, '
    u'98 标准用变更记录 {remove_note[1]} 处“Removed all references to jumbograms…”自我移除, 17 现行正文⇎变更记录各 {body_Jumbo[2]}⇎{tail_Jumbo[2]} 处, '
    u'实验档 rfc2675 接走 {jumbo_caps[3]} 处。'
    u'分片主语三份逐字同现（{j_src_only}）⇎ 整条后半截在原面直搜查无（{j_s_routers}）而折平后 {j_w_routers} 处——'
    u'“谁切碎包”这个答案在五份里其实只有三类: 三份照搬 ⇎ 超大包档不管 ⇎ PMTUD 档改写成 PMTU 语汇（PMTU {pmtu[4]} 处 ⇎ Packet Too Big {ptb[4]} 处 ⇎ MTU 全族 {mtu_any[4]} 处）。'
    u'义务词体例是这套编号文书的反常例: 全大写 MUST⇎SHOULD⇎MAY 五份 {j_u_must} ⇎ {j_u_should} ⇎ {j_u_may} 处, '
    u'小写 must {j_l_must} ⇎ should {j_l_should} ⇎ may {j_l_may}; PMTUD 档自陈“只用小写、不引 2119 定义”'
    u'（{j_lowercase_selfdoc} ⇎ {j_no_cite_2119} 句, 而它引用 2119 {rfc2119_ref[4]} 次）。'
    u'文档身份: 抬头 Obsoletes 行 {j_obsoletes_hdr} ⇎ “Category: Standards Track” {j_category_std} ⇎ 字样 Experimental {j_category_exp}'
    u'（超大包档的抬头也印 Standards Track, 库内并无可判“实验”二字的字节）⇎ 勘误字样 {j_errata} 处 ⇎ § 引用 {j_section_cite} 处 ⇎ 不同 RFC 号 {j_rfc_ref_n} 枚。'
    u'搬运账: 整行归一（只留 a-z0-9、strip 后 ≥40 字符）集合 {j_lines_ge40}, 两两交 AB {share_AB} ⇎ BC {share_BC} ⇎ AC {share_AC} ⇎ CD {share_CD} ⇎ CE {share_CE}, '
    u'三份同现 {AB_C_inter} ⇎ 并集 {union_ABC} ⇎ 只在 95 初版 {only_A} ⇎ 只在 17 现行 {only_C}, 容斥闭合 {abc_close}——'
    u'现行版与超大包档 0 行整行相同, 而它正是那条 1280 要求的隔壁文书。'
    u'含关键数字的长行（≥55 字符）{jnl} 条; 登记锚 {anchor_total} 处／{anchor_distinct} 个不同串'
    u'（每标签 A {tA} ⇎ B {tB} ⇎ C {tC} ⇎ D {tD} ⇎ E {tE}; 单源 {anchor_single} ⇎ 穿二至四源 {anchor_cross} ⇎ 五源全现 {anchor_all5}, '
    u'归属检查 {checks} 次, 错配 {anchor_err}）。'
    u'“五份的抓取时刻与磁盘 mtime 谁新谁旧”“rfc-editor.org 此刻的现行状态页”“RFC 2675 在官网的类目”“勘误表是否已挂新版”'
    u'“现实链路的 MTU 分布（1500 只是以太网的举例）”不可由在库文件判定，判词按第三档写、门槛不背书。\n')

# 预检: 每段模板落地前先把其中的占位符点齐——逐个跑 KeyError 太费轮次。
def pre(t, tagx):
    miss = sorted(set(x for x in re.findall(u'\\{([A-Za-z0-9_]+)(?:\\[[0-9]+\\])?\\}', t) if x not in K))
    assert not miss, (u'模板 %s 取不到值' % tagx, miss)


S = io.open(FM, encoding='utf-8').read()
pre(NEWPAR, u'NEWPAR')
S = sub(u'共 **60 条**（`babeltele/B01..B60`）', u'共 **{nent} 条**（`babeltele/B01..B61`）'.format(**K), S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（60 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（{nent} 条）'.format(**K), S)
old_pr = re.search(u'当前 \\*\\*60 条语料／\\d+ 条\\*\\*推导全部通过（audit 自报“已机检的推导 \\d+ 条”）', S)
assert old_pr
S = S.replace(old_pr.group(0), (u'当前 **{nent} 条语料／{proofs} 条**推导全部通过（audit 自报“已机检的推导 {proofs} 条”）'
                                .format(**K)))
PAR_ANCHOR = u'**B60 问的是一张公签 TLS 证书能活多久, 五份一手文书给出五种答法**'
S = sub(PAR_ANCHOR, NEWPAR.format(**K) + PAR_ANCHOR, S)

ROW61 = (u'| B61 | {enc}（新建, 同一条链路下限与包顶交五份一手规范各答一遍 {anchor_total} 处标注／{anchor_distinct} 个不同串（登记全命中, '
         u'每标签 A {tA} ⇎ B {tB} ⇎ C {tC} ⇎ D {tD} ⇎ E {tE}, 归属检查 {checks} 次）: 五色锚位 95 初版 ⟦A⟧ ⇎ 98 标准 ⟦B⟧ ⇎ 17 现行 ⟦C⟧ ⇎ 超大包档 ⟦D⟧ ⇎ PMTUD 档 ⟦E⟧; '
         u'头条句式“have an MTU of + 数字 + octets”: 空白容忍 {j_w_floor_sent} ⇎ 单空格 {j_s_floor_sent}（折行 {j_wrap_gap_floor_sent}）, '
         u'现读 {j_floor_vals}; 正文⇎变更记录两窗把“还要不要 576”分开——576 {j_body_576}⇎{j_tail_576} ⇎ 1280 {j_body_1280}⇎{j_tail_1280} ⇎ Jumbo {j_body_Jumbo}⇎{j_tail_Jumbo}（闭合 {j_close_576}）, '
         u'附录定位行两支同收取末次命中, 行号 {j_clo_line}; 净载荷算式 {j_pfloor_pair}（−48 = 40 头部 + 8 分片头）; '
         u'包顶只有千分位写法: 65,535 {j_lit_c65535} ⇎ 无逗号 {j_lit_65535} ⇎ 4,294,967,295 {j_lit_c4294967295}, 后邻符号七档闭合（576 在 95 初版 {j_sk576}）; '
         u'超大包选项 定义 {j_jumbo_option_def}（折平 {j_w_jumbo_opt}）⇎ 自我移除 {remove_note[1]} 句 ⇎ 17 现行 {body_Jumbo[2]} ⇎ 实验档 {jumbo_caps[3]}; '
         u'分片主语三份逐字同现 {j_src_only} 而原面直搜后半截 {j_s_routers}; 义务词 全大写 {j_u_must} ⇎ 小写 must {j_l_must} ⇎ PMTUD 自陈不引 2119（{j_no_cite_2119}）; '
         u'身份 抬头 Obsoletes {j_obsoletes_hdr} ⇎ Standards Track {j_category_std} ⇎ Experimental 字样 {j_category_exp} ⇎ 勘误 {j_errata}; '
         u'搬运 整行集 {j_lines_ge40}、交 AB⇎BC⇎AC⇎CD⇎CE {share_AB}⇎{share_BC}⇎{share_AC}⇎{share_CD}⇎{share_CE} ⇎ 同现 {AB_C_inter} ⇎ 并集 {union_ABC}（容斥闭合 {abc_close}）; '
         u'长行候选 {jnl}; 同数共键复合式 {coll} 组、零项 {zeros} 枚折成一条算式; '
         u'门槛侧 {deriv_keys} 枚推导键／{deriv_points} 处 B61V 引用点（建条目侧按“值→算式”去重记 {dedup_points}）, '
         u'五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对 {anchor_distinct} 条锚逐字全命中, 工具侧 atomcheck 另核 ok={anchor_distinct} bad=0） |\n')
pre(ROW61, u'ROW61')
anchor_row = (u'工具侧 atomcheck 另核 ok=15 bad=0） |' + NL)
S = sub(anchor_row, anchor_row + ROW61.format(**K), S)

lin_old = re.search(u'第二代（B11–B60）锚内字母 \\*\\*([0-9 ]+)\\*\\*、锚外 \\*\\*([0-9 ]+)\\*\\*；'
                    u'全库合计 \\*\\*([0-9 ]+)／([0-9 ]+)\\*\\*（B60 一枚条目贡献 ([0-9 ]+)／([0-9 ]+), 由建条目侧现数）', S)
assert lin_old, u'字母合计行锚不住'
_g = [int(x.replace(u' ', u'')) for x in lin_old.groups()]
li, lo = m(u'letters_in'), m(u'letters_out')
S = S.replace(lin_old.group(0), (u'第二代（B11–B61）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
                                u'（B61 一枚条目贡献 %s／%s, 由本遍现数并校住建条目侧快照）'
                                % (fmt(_g[0] + li), fmt(_g[1] + lo), fmt(_g[2] + li), fmt(_g[3] + lo),
                                   fmt(li), fmt(lo))))

RAW61 = (u'| B61 | `raw/ipv6/rfc1883.txt`（95 初版 ⟦A⟧：{bytesA} 字节／行数 {linesA}／非空行 {nbA}／下限句现读 576／576 正文 {body_576[0]} ⇎ 变更记录 {tail_576[0]} 处） ⇎ '
         u'`rfc2460.txt`（98 标准 ⟦B⟧：{bytesB}／{linesB}／{nbB}／下限句 1280／变更记录标题行 {clo_line[1]} 行, 自我移除 jumbograms {remove_note[1]} 句） ⇎ '
         u'`rfc8200.txt`（17 现行 ⟦C⟧：{bytesC}／{linesC}／{nbC}／下限句 1280 而净载荷那句已删 {pfloor_pair_C_n} 对／勘误字样 {errata[2]} 处） ⇎ '
         u'`rfc2675.txt`（超大包档 ⟦D⟧：{bytesD}／{linesD}／{nbD}／Jumbo 大写 {jumbo_caps[3]} 处／4,294,967,295 {lit_c4294967295[3]} 处） ⇎ '
         u'`rfc8201.txt`（PMTUD 档 ⟦E⟧：{bytesE}／{linesE}／{nbE}／PMTU {pmtu[4]} 处而任何下限数字 0 处／自陈只用小写 {lowercase_selfdoc[4]} 句） | '
         u'五份答同一个问题 ⇒ 95 初版写 576 ⇎ 98 标准改成 1280 并把 jumbograms 整族搬走 ⇎ 17 现行留 1280 而删掉净载荷算式 ⇎ '
         u'超大包档把 65,535 之上重开为 4,294,967,295 ⇎ PMTUD 档通篇不写任何链路下限、只教怎么发现; '
         u'95 初版与 98 标准整行共用 {share_AB} 条, 17 现行与超大包档 {share_CD} 条|' + NL)
pre(RAW61, u'RAW61')
anchor2 = (u'三代基准整行共用 484 条而 CA 说明与任何一份都 0 条|' + NL)
S = sub(anchor2, anchor2 + RAW61.format(**K), S)  # 与 ROW61 同一条纪律: 落地前必须 format, 否则 README 印出花括号

row_tot = (u'| **合计（{nent} 条）** | **{enct}** | **{rett}**（摘要段合计 {digt}） | — | **{unqt}** | — |\n').format(
    nent=NENT, enct=fmt(enc_all).replace(u',', u' '), rett=ret_tot,
    digt=fmt(dig_all).replace(u',', u' '), unqt=fmt(uniq_all).replace(u',', u' '))
old_tot = re.search(u'[|] [*]{2}合计（60 条）[*]{2}[^\n]*\n', S)
assert old_tot
S = S.replace(old_tot.group(0), row_tot)

old_soft = re.search(u'残余提示（不计 FAIL）：\\d+ 个 1–2 位结构计数', S)
assert old_soft
S = S.replace(old_soft.group(0), u'残余提示（不计 FAIL）：%d 个 1–2 位结构计数' % soft_all)
TAILPOS = u'））未逐位核验，'
assert S.count(TAILPOS) == 1
S = S.replace(TAILPOS, (u'；新建的 B61 待核 %d 项（%s）——`48` 是净载荷括号算式两端的差（576−528 ⇎ 1280−1232, 拿本条现读的两对读数相减即得, '
                        u'源文自己在括号里另写 40 头部 + 8 分片头）, `55` 是本条自定的“含关键数字长行”字符阈值（输入参数而非源内计数）, '
                        u'`95`⇎`98` 是两枚版本年标签（只活在条目自述与判词里）——四枚都不是量在五份源上的事实断言, 故不消解'
                        + TAILPOS) % (len(H61), u'／'.join(u'`%s`' % x for x in H61)), 1)

WL, WR = 200, 200
CMD = (u'python -X utf8 corpus/_mkB61.py                  # 建条目: 扁平契约 %d 枚键／DERIV %d 枚算式, 占位符未替换 0 个, 采侧对账 %d 键 0 不符\n'
       u'python -X utf8 corpus/_mkdigest3.py B61 <entry> A corpus/raw/ipv6/rfc1883.txt %d %d '
       u'B corpus/raw/ipv6/rfc2460.txt %d %d C corpus/raw/ipv6/rfc8200.txt %d %d '
       u'D corpus/raw/ipv6/rfc2675.txt %d %d E corpus/raw/ipv6/rfc8201.txt %d %d   # 五源分节摘要(%s 字符, 窗口按 %d⇎%d 取句边界)\n'
       u'python -X utf8 corpus/_wire61.py                    # 把 SCAN 段机械切进 audit.py::_b61_scan 并插 DERIV[\'B61\']\n'
       u'python -X utf8 corpus/_fill61.py                    # 第四遍: 现取注数并把 ⛓解读注 写回条目(10 行复测表全 assert)\n'
       u'python -X utf8 corpus/atomcheck.py B61 corpus/_atoms61.txt   # 工具侧独立逐字校验: ok=%d bad=0\n'
       % (len(FLAT), CH[u'deriv_keys'], NMEAS, WL, WR, WL, WR, WL, WR, WL, WR, WL, WR,
          fmt(dig61).replace(u',', u' '), WL, WR, m(u'anchor_distinct')))
anchor3 = u'python -X utf8 corpus/atomcheck.py B60 corpus/_atoms60.txt   # 工具侧独立逐字校验: ok=15 bad=0' + NL
assert S.count(anchor3) == 1
S = sub(anchor3, anchor3 + CMD, S)
S = sub(u'python -X utf8 corpus/_readme53.py               # 记账: 本文件第五遍再量一次四份源',
        u'python -X utf8 corpus/_readme61.py               # 记账: 本文件第五遍再量一次五份源(量源一个 re 都不用, 只用 find/切片/字符比较; '
        u'%d 枚键与扁平契约⇎采集侧快照逐键对表)\n'
        u'python -X utf8 corpus/_readme53.py               # 记账: 本文件第五遍再量一次四份源' % len(Q5), S)

io.open(FM, 'w', encoding='utf-8', newline=NL).write(S)
print(u'README 已记账: %d 条 ｜ 编码合计 %s ⇎ 摘要合计 %s ⇎ 合计保留率 %s ｜ 唯一码点 %d ｜ 推导 %d 条 ｜ 提示 %d（清单 %s） ｜ '
      u'B61 %s 字符／%d 锚(%d 串, A %d⇎B %d⇎C %d⇎D %d⇎E %d, 单源 %d⇎穿二至四 %d⇎五源 %d, 检查 %d, 错配 %d) ｜ '
      u'第五遍现量 %d 个键全等契约 ｜ 下限句 %s ⇎ 单空格 %s ⇎ 折行 %s ⇎ 现读 %s ｜ 两窗 576 %s⇎%s ⇎ Jumbo %s⇎%s ｜ '
      u'包顶 65,535 %s ⇎ 无逗号 %s ⇎ 4,294,967,295 %s ｜ 千分位 token %s 处而超大包档 other %s 档 ｜ '
      u'义务词 全大写 %s ⇎ 小写 must %s ｜ 整行共用 %s⇎%s⇎%s ⇎ CD %d ⇎ 同现 %d ⇎ 并集 %d ⇎ 容斥闭合 %d ｜ 长行候选 %s ｜ sha512 %d 种'
      % (NENT, fmt(enc_all), fmt(dig_all), ret_tot, uniq_all, proofs, soft_all,
         u' '.join(sorted(HINT)), fmt(enc61), m(u'anchor_total'), m(u'anchor_distinct'),
         tc[u'A'], tc[u'B'], tc[u'C'], tc[u'D'], tc[u'E'], m(u'anchor_single'), m(u'anchor_cross'),
         m(u'anchor_all5'), m(u'checks'), m(u'anchor_err'), len(Q5),
         u'⇎'.join(str(x) for x in m(u'w_floor_sent')), u'⇎'.join(str(x) for x in m(u's_floor_sent')),
         u'⇎'.join(str(x) for x in m(u'wrap_gap_floor_sent')),
         u'⇎'.join(u'[%s]' % u','.join(x) for x in m(u'floor_vals')),
         u'⇎'.join(str(x) for x in m(u'body_576')), u'⇎'.join(str(x) for x in m(u'tail_576')),
         u'⇎'.join(str(x) for x in m(u'body_Jumbo')), u'⇎'.join(str(x) for x in m(u'tail_Jumbo')),
         u'⇎'.join(str(x) for x in m(u'lit_c65535')), u'⇎'.join(str(x) for x in m(u'lit_65535')),
         u'⇎'.join(str(x) for x in m(u'lit_c4294967295')),
         u'⇎'.join(str(x) for x in m(u'tok_c65535')), m(u'sk_c65535_other')[3],
         u'⇎'.join(str(x) for x in m(u'u_must')), u'⇎'.join(str(x) for x in m(u'l_must')),
         m(u'share_AB'), m(u'share_BC'), m(u'share_AC'), m(u'share_CD'), m(u'AB_C_inter'),
         m(u'union_ABC'), m(u'abc_close'), u'⇎'.join(str(x) for x in m(u'num-lines')),
         m(u'sig_distinct')))
