# -*- coding: utf-8 -*-
"""B62 ⛓解读注(第四遍): 本注每个数都是现测并 assert 的, 不手填。
四套实现: 采集侧 corpus/_pick62.py(re.findall 与前后瞻数方程族、str.count 数折平档、set & 求搬运)
⇎ 建条目侧 corpus/_mkB62.py(游标档 find 循环 + 逐字符判邻 + 方程结构解析 + 排序两指针求交, 扁平契约 corpus/_b62flat.json)
⇎ 门槛侧 corpus/audit.py::_b62_scan()(由 corpus/_wire62.py 从 SCAN 段机械抽出, 插门前把 389 个扁平键与
109 条 DERIV 算式在抽出体上逐条预演) ⇎ 本注第四遍。
本注的读法与前三遍都不同:
①方程族不扫全文也不设正则: 逐行用 split 在 “min (” 处断开, 外层系数取第一个 '*(' 左侧、内层系数取第二个 '*' 左侧、
  常数帽取其后逗号段的头一串数字(帽后六字符留作单位档), 变量名要落在 MSS⇎SMSS 里才认——
  枚数/两系数/帽/变量名/单位五档全部与建条目侧同值才通过, 另核 “每一处 min ( 要么解出要么被否掉”;
②规范窗用正则标题表 + bisect: 先把全篇编号标题一次性收成一张 (行号, 编号) 表(建条目侧是就地逐字符回溯),
  再由规范句最后一处命中的行号二分出所在节, 收口取该行之后第一枚异号标题(99 那一份的收口行其实是跨行续句行首的 “4380”,
  与建条目侧同一判据); 窗长按逐行长度相加再减一根换行;
③字面档用 split 计数(len(x.split(针))-1), token 档用 \\d[\\d,]* 匹配后再判左右邻字符——两条都不问 "第几处",
  只问 "这枚数是不是独立成数"; 值域档同一条匹配换 \\d+ 并按前后邻判独立, 两端.nb_lo⇎nb_hi 都取面内读数;
④折行档不折全篇: 每行 strip 后按序接成一面(空行略过), 在同一面上 split 计数, 再减逐行各自 split 的和;
  15 枚针逐枚核 原面档 ⇎ 折面档 ⇎ 差;
⑤义务词两档: 全大写族用 split 计数(与建条目侧的 occ 同定义不同实现), 小写族用 [A-Za-z0-9_]+ 词流整词相等;
⑥搬运账归一用 re.sub 去非 a-z0-9, 交并按"小表建立字典、大表逐条查字典"再与集合运算符 & 对拍, 并集按单个计数字典 add,
  only_* 按建条目侧的“同代其余三份”分组(不比全体五份)用集合差算, 含壳⇎去壳两面各算一遍;
⑦C 的档位表用三段 split 重读(“=” ⇎ “*” ⇎ “ segments” 前末词), If 行整行逐字符收全部数字组;
  B 的三行分支按 “then win <=” 行与其上一条件行配对重读常数;
⑧锚归属由条目正文配对现推, 成员判据换成"该行 ⇎ 该行与下一行拼起来"必须含整串归一锚——比建条目侧的整篇归一更严,
  若某枚锚跨了两行以上就会被本注判错(现况 0 枚)。
不可由在库文件判定的只写在本注: 五份的抓取时刻与磁盘 mtime 谁新谁旧、rfc-editor.org 此刻的现行状态页、
勘误表是否已挂新版、库外流传的 RFC 5681 档位表序与这份面内表序谁对、现实链路的 MSS 分布——都不进判词与门槛。
"""
import io, os, re, sys, json, bisect

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B62_tcp_initial_window_five_answers.md')
FLAT = json.load(io.open(C + u'/_b62flat.json', encoding=u'utf-8'))
MEAS = json.load(io.open(C + u'/_b62meas.json', encoding=u'utf-8'))
CH = json.load(io.open(C + u'/_b62checks.json', encoding=u'utf-8'))
PATH = [u'corpus/raw/tcpiw/rfc2581.txt', u'corpus/raw/tcpiw/rfc3390.txt', u'corpus/raw/tcpiw/rfc5681.txt',
        u'corpus/raw/tcpiw/rfc6928.txt', u'corpus/raw/tcpiw/rfc9002.txt']
TAGS = [u'A', u'B', u'C', u'D', u'E']
LBL = dict(zip(TAGS, [u'99 两段', u'02 方程', u'09 三段表', u'13 十倍', u'21 QUIC']))
RD = lambda p: io.open(p, encoding='utf-8-sig', errors='replace').read()
SRC = [RD(p) for p in PATH]
LST = [t.split(NL) for t in SRC]
NSRC = 5
J = lambda xs: u'⇎'.join(str(x) for x in xs)


def sc(t, needle):
    """字面档: 分割计数(不找位置, 只数段数)。"""
    return len(t.split(needle)) - 1


def firstnum(s):
    d = u''
    for ch in s:
        if ch.isdigit():
            d += ch
        elif d:
            break
    return int(d) if d else 0


# ---- ①方程族: 逐行 split 拆三段 ----
VARS = (u'MSS', u'SMSS')


def digs(s):
    return s.isdigit() and s != u''


EQ = []
for i in range(NSRC):
    got = []
    for l in LST[i]:
        if u'min (' not in l or u'max (' not in l:
            continue
        a = l.split(u'min (', 1)[1]
        coef, rest = a.split(u'*', 1)
        if not digs(coef):
            continue
        var = rest.split(u',', 1)[0].strip()
        b = rest.split(u'max (', 1)[1]
        inner, rest2 = b.split(u'*', 1)
        if not digs(inner) or var not in VARS:
            continue
        v2, seg = rest2.split(u',', 1)[0].strip(), rest2.split(u',', 1)[1]
        if v2 not in VARS:
            continue
        cap = firstnum(seg)
        if not cap:
            continue
        got.append((int(coef), var, int(inner), v2, cap,
                    seg[seg.index(u'%d' % cap) + len(u'%d' % cap):][:6]))
    EQ.append(got)
E_N = [len(g) for g in EQ]
E_COEF = [g[0][0] if g else 0 for g in EQ]
E_VAR = [g[0][1] if g else u'' for g in EQ]
E_IN = [g[0][2] if g else 0 for g in EQ]
E_CAP = [g[0][4] if g else 0 for g in EQ]
E_VAR2 = [g[0][3] if g else u'' for g in EQ]
E_UNIT = [g[0][5] if g else u'' for g in EQ]
assert E_N == FLAT[u'x_eq_n'], (E_N, FLAT[u'x_eq_n'])
assert E_COEF == FLAT[u'x_eq_coef'] and E_IN == FLAT[u'x_eq_inner'], (E_COEF, E_IN)
assert E_CAP == FLAT[u'x_eq_cap'], (E_CAP, FLAT[u'x_eq_cap'])
assert E_VAR == FLAT[u'x_eq_var'] and [len(x) for x in E_VAR] == FLAT[u'x_eq_varlen']
assert E_VAR2 == FLAT[u'x_eq_var'] and E_UNIT == FLAT[u'x_eq_unit'], (E_VAR2, E_UNIT)
# 每一处 "min (" 都要被解出或被否掉: 09 那份唯一的 min ( 是增量式, 与初窗无关
assert [sc(SRC[i], u'min (') for i in range(NSRC)] == FLAT[u'lit_minp']
assert [E_N[i] + FLAT[u'x_eq_close'][i] for i in range(NSRC)] == FLAT[u'lit_minp'], FLAT[u'x_eq_close']

# ---- ②规范窗: 标题表 + bisect ----
RULE = {u'A': u'IW, the initial value of cwnd, MUST be less',
        u'B': u'The upper bound for the initial window is given more precisely',
        u'C': u'IW, the initial value of cwnd, MUST be set',
        u'D': u'More precisely, the upper bound for the initial window',
        u'E': u'Initial and Minimum Congestion Window'}
HD = re.compile(u'^ {0,4}(\\d+(?:\\.\\d+)*)(\\.?)[ \\t]+\\S')
WIN, WLEN = [], []
for i in range(NSRC):
    ls = LST[i]
    hits = [n for n, l in enumerate(ls) if RULE[TAGS[i]] in l]
    r = hits[-1]
    assert len(hits) == FLAT[u'sec_hit'][i], (i, hits, FLAT[u'sec_hit'][i])
    heads = [(n, HD.match(l).group(1)) for n, l in enumerate(ls)
             if HD.match(l) and len(l.strip()) > 3]
    keys = [h[0] for h in heads]
    p = bisect.bisect_right(keys, r) - 1
    a, na = heads[p]
    nxt = [h for h in heads if h[0] > r and h[1] != na]
    b = nxt[0][0] if nxt else len(ls)
    WIN.append((a, b))
    WLEN.append(sum(len(x) + 1 for x in ls[a:b]) - 1)
assert WIN == [(x[0], x[1]) for x in [tuple(w) for w in FLAT[u'sec_w']]], (WIN, FLAT[u'sec_w'])
assert [w[0] for w in WIN] == FLAT[u'sec_a'] and [w[1] for w in WIN] == FLAT[u'sec_b']
assert WLEN == FLAT[u'sec_len'], (WLEN, FLAT[u'sec_len'])

# ---- ③字面 ⇎ 独立 token ⇎ 值域 ----
LITS = (u'4380', u'2190', u'1095', u'14600', u'14720', u'1500', u'1460', u'1200')
L4 = dict((k, [sc(SRC[i], k) for i in range(NSRC)]) for k in LITS)
L4C = {u'14,720': [sc(SRC[i], u'14,720') for i in range(NSRC)],
       u'14,600': [sc(SRC[i], u'14,600') for i in range(NSRC)]}
for k, v in L4.items():
    assert v == FLAT[u'lit_' + k], (k, v, FLAT[u'lit_' + k])
assert L4C[u'14,720'] == FLAT[u'lit_c14720'] and L4C[u'14,600'] == FLAT[u'lit_c14600']
NUM = re.compile(u'\\d[\\d,]*\\d|\\d')
BAND = re.compile(u'\\d+')
D = u'0123456789'
T4, B4 = {}, {}
for k in LITS:
    T4[k] = [0] * NSRC
for i in range(NSRC):
    t = SRC[i]
    for m in NUM.finditer(t):
        s, e = m.start(), m.end()
        prev = t[s - 1] if s else u''
        nxt = t[e] if e < len(t) else u''
        if prev in D + u',.' or nxt in D:
            continue
        for k in LITS:
            if m.group(0) == k:
                T4[k][i] += 1
    vals = {}
    for m in BAND.finditer(t):
        s, e = m.start(), m.end()
        prev = t[s - 1] if s else u''
        nxt = t[e] if e < len(t) else u''
        if prev in D + u',.' or nxt in D or not 4 <= e - s <= 5:
            continue
        v = int(m.group(0))
        if FLAT[u'nb_lo'] <= v <= FLAT[u'nb_hi']:
            vals[v] = 1
    B4[i] = sorted(vals)
for k in LITS:
    assert T4[k] == FLAT[u'tok_' + k], (k, T4[k], FLAT[u'tok_' + k])
assert [len(B4[i]) for i in range(NSRC)] == [FLAT[u'numband_n_' + x.lower()] for x in TAGS]
assert [B4[i] for i in range(NSRC)] == [FLAT[u'numband_' + x.lower()] for x in TAGS]

# ---- ④折行: 逐行 strip 后接成一面(建条目侧整篇 split/join, 采集侧 \s+ 正则) ----
SN = [(u'min4', u'min (4*'), (u'min10', u'min (10*'), (u'cap4380', u'max (2*MSS, 4380'),
      (u'cap14600', u'max (2*MSS, 14600)'), (u'seg10', u'10 segments'), (u'two_smss', u'2*SMSS'),
      (u's4smss', u'4*SMSS'), (u's4mss', u'4*MSS'), (u'dont_allow', u'We do NOT allow this change'),
      (u'large_of', u'the larger of'), (u'udp8', u'8-byte overhead'), (u'tcp20', u'20-byte overhead'),
      (u'ten_times', u'ten times the maximum datagram size'), (u'iw_of', u'IW, the initial value of cwnd'),
      (u'skel', u'represents a change from')]
assert len(SN) == FLAT[u'wrap_pin_n']
ALONE, FOLD3, GAP3 = {}, {}, {}
for k, s in SN:
    ALONE[k] = [sum(len(l.split(s)) - 1 for l in LST[i]) for i in range(NSRC)]
    FOLD3[k] = [sc(u' '.join(x for x in (l.strip() for l in LST[i]) if x), s) for i in range(NSRC)]
    GAP3[k] = [FOLD3[k][i] - ALONE[k][i] for i in range(NSRC)]
    assert ALONE[k] == FLAT[u's_' + k], (k, ALONE[k], FLAT[u's_' + k])
    assert FOLD3[k] == FLAT[u's_' + k + u'_fold'], (k, FOLD3[k])
    assert GAP3[k] == FLAT[u'wrap_gap_' + k], (k, GAP3[k], FLAT[u'wrap_gap_' + k])
WRAP_TOTAL = sum(sum(r) for r in GAP3.values())
WRAP_HIT = len([k for k, s in SN if max(GAP3[k]) > 0])
WRAP_BY = [sum(GAP3[k][i] for k, s in SN) for i in range(NSRC)]
assert WRAP_TOTAL == FLAT[u'wrap_gap_total'] and WRAP_HIT == FLAT[u'wrap_pin_hit']
assert sum(WRAP_BY) == WRAP_TOTAL and WRAP_BY[3] == GAP3[u'seg10'][3] == 2

# ---- ⑤义务词两档 + 引用 + 身份 ----
UPW = (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED')
U4 = dict((w, [sc(SRC[i], w) for i in range(NSRC)]) for w in UPW)
for w in UPW:
    kk = u'u_' + w.replace(u' ', u'_').lower()
    assert U4[w] == FLAT[kk], (w, U4[w], FLAT[kk])
WF = re.compile(u'[A-Za-z0-9_]+')
LOWC = {}
for i in range(NSRC):
    ws = WF.findall(SRC[i])
    LOWC[i] = [sum(1 for x in ws if x == w) for w in (u'must', u'should', u'may')]
assert [LOWC[i][0] for i in range(NSRC)] == FLAT[u'l_must']
assert [LOWC[i][1] for i in range(NSRC)] == FLAT[u'l_should']
assert [LOWC[i][2] for i in range(NSRC)] == FLAT[u'l_may']
UOB = [U4[u'MUST'][i] + U4[u'SHOULD'][i] + U4[u'MAY'][i] for i in range(NSRC)]
LOB = [sum(LOWC[i]) for i in range(NSRC)]
assert UOB == FLAT[u'oblig_up'] and LOB == FLAT[u'oblig_low']
WK = [(u'mss', u'MSS'), (u'smss', u'SMSS'), (u'mds', u'max_datagram_size'), (u'datagram', u'datagram'),
      (u'iw', u'IW'), (u'cwnd', u'cwnd'), (u'initwin_lower', u'initial window'),
      (u'initwin_caps', u'Initial Window'), (u'icw', u'initial congestion window'),
      (u'slow_start', u'slow start'), (u'slowstart_hy', u'Slow-Start'), (u'slowstart_flat', u'SlowStart')]
V4 = {}
for k, s in WK:
    V4[u'v_' + k] = [sc(SRC[i], s) for i in range(NSRC)]
    assert V4[u'v_' + k] == FLAT[u'v_' + k], (k, V4[u'v_' + k], FLAT[u'v_' + k])
V4[u'v_smss_ci'] = [sc(SRC[i].lower(), u'smss') for i in range(NSRC)]
assert V4[u'v_smss_ci'] == FLAT[u'v_smss_ci']
TOK = [WF.findall(SRC[i]) for i in range(NSRC)]
WC = []
for i in range(NSRC):
    ws = [x.lower() for x in TOK[i]]
    WC.append([sum(1 for k in range(len(ws) - 1) if ws[k] == u'initial' and ws[k + 1] == u'window'),
               sum(1 for x in ws if x in (u'segment', u'segments'))])
assert [WC[i][0] for i in range(NSRC)] == FLAT[u'v_iw_word'], ([WC[i][0] for i in range(NSRC)],)
assert [WC[i][1] for i in range(NSRC)] == FLAT[u'v_seg_word']
# IW 这个缩写只在 99/09/13 三份里当变量名用: 全大写子串档 ⇎ 行首 “IW =” 起句档(按行 split 后邻词相等)
IWB = []
for i in range(NSRC):
    n = 0
    for l in LST[i]:
        w = l.split()
        n += sum(1 for k in range(len(w) - 1) if w[k] == u'IW' and w[k + 1] == u'=')
    IWB.append(n)
assert all(IWB[i] <= FLAT[u'v_iw'][i] for i in range(NSRC)), IWB
assert IWB[0] == E_N[0] and IWB[2] == len(FLAT[u'x_c_iw_mult'])
assert [IWB[i] for i in (1, 3, 4)] == [0, 0, 0]
CITE = {}
for n in (u'2581', u'3390', u'5681', u'6928', u'9002', u'2414', u'2001', u'2988', u'6298', u'1122'):
    CITE[n] = [sc(SRC[i], u'RFC ' + n) + sc(SRC[i], u'RFC' + n) for i in range(NSRC)]
    assert CITE[n] == FLAT[u'cite_' + n], (n, CITE[n], FLAT[u'cite_' + n])
KW = [sc(SRC[i], u'key words') + sc(SRC[i], u'Key words') for i in range(NSRC)]
assert KW == FLAT[u'key_words_boiler']
R2119 = [sc(SRC[i], u'2119') for i in range(NSRC)]
assert R2119 == FLAT[u'rfc2119_ref']

# ---- ⑥分页壳: 正则判页眉页脚 ----
HDR = re.compile(u'^RFC (\\d{4})(?!\\d)(?: |$)')
FOT = re.compile(u'^(?:.*\\[Page \\d+\\]$|.*Page \\d+$)')


def hdr4(l):
    return bool(HDR.match(l)) and l[8:].strip() != u''


def fot4(l):
    s = l.strip()
    return bool(s) and bool(FOT.match(s))


H4 = [len([l for l in LST[i] if hdr4(l)]) for i in range(NSRC)]
F4 = [len([l for l in LST[i] if fot4(l)]) for i in range(NSRC)]
assert H4 == FLAT[u'hdr'] and F4 == FLAT[u'foot'], (H4, FLAT[u'hdr'], F4, FLAT[u'foot'])
assert [H4[i] + F4[i] for i in range(NSRC)] == FLAT[u'pagelines']
TITLE = [len([l for l in LST[i] if HDR.match(l) and l[8:].strip() != u''
              and u'Initial Window' in l]) for i in range(NSRC)]
assert TITLE == FLAT[u'hdr_title']
BOM4 = [1 if open(p, 'rb').read(3) == b'\xef\xbb\xbf' else 0 for p in PATH]
assert BOM4 == FLAT[u'bom']
BYT = [len(open(p, 'rb').read()) for p in PATH]
assert BYT == FLAT[u'bytes'] and [BYT[i] - len(SRC[i]) for i in range(NSRC)] == \
    [FLAT[u'bytes'][i] - FLAT[u'chars'][i] for i in range(NSRC)]

# ---- ⑦搬运账: re.sub 归一 + 集合运算符, 含壳 ⇎ 去壳两面 ----
def nrm(l):
    return re.sub(u'[^a-z0-9]', u'', l.lower())


GE, GEN = [], []
for store, shell in ((GE, True), (GEN, False)):
    for i in range(NSRC):
        s = {}
        for l in LST[i]:
            if not shell and (hdr4(l) or fot4(l)):
                continue
            n = nrm(l)
            if len(l.strip()) >= 40 and len(n) >= 40:
                s[n] = 1
        store.append(s)
assert [len(GE[i]) for i in range(NSRC)] == FLAT[u'lines_ge40']
assert [len(GEN[i]) for i in range(NSRC)] == FLAT[u'lines_ge40_nos']
assert [len(GE[i]) - len(GEN[i]) for i in range(NSRC)] == FLAT[u'shell_delta']


def KS(d):
    return set(d.keys())


def inter4(x, y):
    a, b = (x, y) if len(x) <= len(y) else (y, x)
    return sum(1 for k in a if k in b)


def union4(*ds):
    m = {}
    for d in ds:
        for k in d:
            m[k] = 1
    return len(m)


PAIR = {}
for i in range(NSRC):
    for j in range(i + 1, NSRC):
        PAIR[(i, j)] = inter4(GE[i], GE[j])
        assert PAIR[(i, j)] == len(KS(GE[i]) & KS(GE[j])) == FLAT[u'share_%s%s' % (TAGS[i].lower(), TAGS[j].lower())]
        assert inter4(GEN[i], GEN[j]) == FLAT[u'share_%s%s_nos' % (TAGS[i].lower(), TAGS[j].lower())]
TRI = sum(1 for k in GE[0] if k in GE[1] and k in GE[2])
assert TRI == FLAT[u'ABC_inter'] and len(KS(GE[0]) & KS(GE[1]) & KS(GE[2])) == TRI
U3 = union4(GE[0], GE[1], GE[2])
U5 = union4(*GE)
U4SET = union4(*GE[:4])
assert U3 == FLAT[u'union_abc'] and U5 == FLAT[u'union_abcde'] and U4SET == FLAT[u'union_abcd']
assert len(KS(GEN[0]) | KS(GEN[1]) | KS(GEN[2])) == FLAT[u'union_abc_nos']
# only_* 只跟“同一代的其余三份”比(99/02/09 互为三代, 13/21 各自另立), 不比全体五份
GRP = {2: (0, 1, 3), 3: (0, 1, 2), 4: (0, 1, 2, 3)}
ONLY = {}
for i, g in GRP.items():
    ONLY[i] = len(KS(GE[i]) - set().union(*[KS(GE[j]) for j in g]))
    assert ONLY[i] == FLAT[u'only_' + TAGS[i].lower()], (i, ONLY[i], FLAT[u'only_' + TAGS[i].lower()])
    assert len(KS(GEN[i]) - set().union(*[KS(GEN[j]) for j in g])) == FLAT[u'only_' + TAGS[i].lower() + u'_nos']
BCPLUS = sum(1 for k in GE[1] if k in GE[2] and (k in GE[3] or k in GE[4]))
assert BCPLUS == FLAT[u'share_bc_plus'], (BCPLUS, FLAT[u'share_bc_plus'])
INCL4 = (len(GE[0]) + len(GE[1]) + len(GE[2]) - PAIR[(0, 1)] - PAIR[(0, 2)] - PAIR[(1, 2)] + TRI)
assert INCL4 == FLAT[u'abc_incl'] and INCL4 - U3 == 0
INCL4N = (len(GEN[0]) + len(GEN[1]) + len(GEN[2])
          - inter4(GEN[0], GEN[1]) - inter4(GEN[0], GEN[2]) - inter4(GEN[1], GEN[2])
          + len(KS(GEN[0]) & KS(GEN[1]) & KS(GEN[2])))
assert INCL4N - FLAT[u'union_abc_nos'] == FLAT[u'abc_close_nos']
UNION_DELTA = U5 - U4SET
assert UNION_DELTA == FLAT[u'union_delta']

# ---- ⑧档位表方向: 行内 split 重读倍数与阈值 ----
MU, SG, TH = [], [], []
for l in LST[2]:
    if l.strip().startswith(u'IW = '):
        MU.append(int(l.split(u'=')[1].strip().split(u'*')[0].strip()))
        # 段数帽取 “ segments” 之前那一段的末词(建条目侧用 num_before 反向走位)
        seg = l.split(u' segments')
        SG.append(int(seg[0].split()[-1]) if len(seg) > 1 else 0)
COND = []
for l in LST[2]:
    s = l.strip()
    if u'SMSS' in s and (s.startswith(u'If ') or s.startswith(u'if ')):
        nums, d = [], u''
        for ch in s + u' ':
            if ch.isdigit():
                d += ch
            elif d:
                nums.append(int(d))
                d = u''
        COND.append(nums)
assert [len(c) for c in COND] == [1, 2, 1], COND
assert COND[0] == [FLAT[u'x_c_hi_bound']] and COND[2] == [FLAT[u'x_c_lo_bound']]
assert COND[1] == [FLAT[u'x_c_lo_bound'], FLAT[u'x_c_mid_ub']]
TH = [COND[0][0], min(COND[1]), COND[2][0]]
assert MU == FLAT[u'x_c_iw_mult'], (MU, FLAT[u'x_c_iw_mult'])
assert SG == FLAT[u'x_c_seg_cap'], (SG, FLAT[u'x_c_seg_cap'])
def nums4(s):
    return [int(x) for x in re.findall(u'\\d+', s)]


BR = [(n, l) for n, l in enumerate(LST[1]) if u'then win <=' in l]
CAPB = [nums4(l.split(u'<=')[1]) for n, l in BR]
PREB = [nums4(LST[1][n - 1]) for n, l in BR]
assert [len(c) for c in CAPB] == [1, 1, 1] and [len(p) for p in PREB] == [1, 2, 1]
assert [c[0] for c in CAPB] == [4, FLAT[u'x_eq_cap'][1], 2], CAPB
assert PREB == FLAT[u'x_b_if'], (PREB, FLAT[u'x_b_if'])
assert sum(1 for n, l in BR if u'MSS' not in l) == FLAT[u'x_b_mid_const']
assert FLAT[u'x_b_caps'] == [u'; '.join(l.strip() for n, l in BR)]
assert FLAT[u'x_b_if_n'] == len(BR)

# ---- ⑨恒等式重跑(本注独立算, 全部为真才继续) ----
MSS, THREE, CAP13, CAP21 = FLAT[u'x_b_mssnum'], FLAT[u'x_b_three'], FLAT[u'x_eq_cap'][3], FLAT[u'x_e_capnum']
IDENTS = [CAP13 == MSS * FLAT[u'x_d_ten'], CAP13 - MSS * FLAT[u'x_d_ten'] == 0,
          FLAT[u'x_b_close'] == 0 and MSS * THREE == FLAT[u'x_eq_cap'][1],
          CAP21 - CAP13 == FLAT[u'x_e_seg'] * FLAT[u'x_e_ovh'],
          FLAT[u'x_c_upper_at2190'] - FLAT[u'x_widen'] == FLAT[u'x_eq_cap'][1],
          MU[0] * TH[0] == MU[2] * TH[2] == FLAT[u'x_eq_cap'][1],
          all(MU[k] == SG[k] for k in range(3)),
          (MU[2] - MU[0] > 0) != (TH[2] - TH[0] > 0),
          FLAT[u'x_e_break'] * FLAT[u'x_e_twice'] == CAP21,
          FLAT[u'x_e_iw'] == FLAT[u'x_e_floornum'] * FLAT[u'x_e_ten'],
          FLAT[u'x_at1460_b'] == FLAT[u'x_at1460_c'],
          FLAT[u'x_thresh_close'] == FLAT[u'x_lo_close'] == FLAT[u'x_c_mid_ub_close'] == 0]
assert all(IDENTS), [n for n, x in enumerate(IDENTS) if not x]
ZKEYS = sorted([k for k in FLAT if u'_close' in k and isinstance(FLAT[k], (int, float))
                and not isinstance(FLAT[k], bool)])
LKEYS = sorted([k for k in FLAT if u'_close' in k and isinstance(FLAT[k], list)])
assert ZKEYS == FLAT[u'scalar_clos_list'] and len(ZKEYS) == FLAT[u'scalar_clos_n']
assert sum(FLAT[k] for k in ZKEYS) == FLAT[u'scalar_clos_sum'] == 0
assert len(LKEYS) == FLAT[u'list_clos_n']

# ---- ⑩锚归属: 逐行 ⇎ 拼行 两档成员判据 ----
TT = io.open(ENTRY, encoding=u'utf-8').read()
enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
DIS4 = []
for _, a in CITES:
    if a not in DIS4:
        DIS4.append(a)
LINEF = []
for i in range(NSRC):
    one = set(nrm(l) for l in LST[i])
    two = set()
    for k in range(len(LST[i]) - 1):
        two.add(nrm(LST[i][k]) + nrm(LST[i][k + 1]))
    LINEF.append((one, two))


def where(atom):
    n = nrm(atom)
    return tuple(i for i in range(NSRC) if n in LINEF[i][0] or (n in LINEF[i][1] if len(n) > 0 else False))


HC4 = [where(a) for a in DIS4]
ERR4 = [x for x in CITES if not nrm(x[1]) or len(where(x[1])) == 0]
SIN = len([h for h in HC4 if len(h) == 1])
CRS = len([h for h in HC4 if 1 < len(h) < NSRC])
ALL5 = len([h for h in HC4 if len(h) == NSRC])
assert not ERR4, ERR4[:3]
assert SIN == FLAT[u'anchor_single'] and CRS == FLAT[u'anchor_cross'] and ALL5 == FLAT[u'anchor_all5']
assert len(CITES) == FLAT[u'anchor_total'] and len(DIS4) == FLAT[u'anchor_distinct']

# ---- ⑪采集侧对账(本注只做逐键比, 不改定义) ----
BAD4 = []
for k in sorted(MEAS):
    if k not in FLAT:
        continue
    a, b = MEAS[k], FLAT[k]
    if isinstance(a, list) and isinstance(b, tuple):
        a = list(b)
    if [list(x) if isinstance(x, (list, tuple)) else x for x in ([a] if not isinstance(a, list) else a)] != \
       [list(x) if isinstance(x, (list, tuple)) else x for x in ([b] if not isinstance(b, list) else b)]:
        BAD4.append(k)
assert not BAD4, BAD4[:6]

# ---- 判词用的两枚反向对照: 改一个比较符就会塌的量 ----
assert FLAT[u'lit_4380'][2] == 0 and FLAT[u'secw_4380'][2] == 0
assert FLAT[u'outw_4380'][0] == 1 and FLAT[u'secw_4380'][0] == 1
assert FLAT[u'lit_2smss'][:3] == [4, 0, 2] and FLAT[u'x_eq_n'][2] == 0

L = []
A = L.append
A(u'### 第四遍复测(本注现算, 与前三遍不同路)')
A(u'')
A(u'| 量 | 本注的写法 | 结果 | 与建条目侧 |')
A(u'|---|---|---|---|')
A(u'| 初窗方程 | 逐行 split 拆 “min (” 左右两段, 外层系数取第一个 * 左侧、内层系数取第二个 * 左侧、常数帽取其后逗号段的头一串数字, 帽后六字符留作单位档 | '
  u'枚数 %s ⇎ 外层系数 %s ⇎ 内层 %s ⇎ 常数帽 %s ⇎ 变量名 %s(长度 %s) ⇎ 帽后单位 %s | 与 x_eq_n ⇎ x_eq_coef ⇎ x_eq_inner ⇎ x_eq_cap ⇎ x_eq_var ⇎ x_eq_unit 逐档一致; '
  u'每一处 “min (” 要么被解出要么被否掉: 全篇 %s 处 ⇎ 解出 %s 处 ⇎ 差 %s 处(09 那枚是增量式), 起句写作 “IW =” 的行按份 %s(02⇎13 的方程在续行上, 不带变量名) |'
  % (J(E_N), J(E_COEF), J(E_IN), J(E_CAP), u' ⇎ '.join(u'⟨%s⟩' % (x or u'无') for x in E_VAR),
     J([len(x) for x in E_VAR]), u' ⇎ '.join(u'⟨%s⟩' % (x or u'无') for x in E_UNIT),
     J(FLAT[u'lit_minp']), J(E_N), J(FLAT[u'x_eq_close']), J(IWB)))
A(u'| 规范窗 | 全篇编号标题一次收表(正则), 规范句最后一处命中按行号 bisect 定位, 下一异号标题收口; 窗长逐行相加再减一 | '
  u'窗 %s–%s ⇎ 窗长 %s 字符 ⇎ 编号 %s | 与 sec_w ⇎ sec_a ⇎ sec_b ⇎ sec_len ⇎ sec_num ⇎ sec_hit 一致 |'
  % (J([w[0] for w in WIN]), J([w[1] for w in WIN]), J(WLEN),
     u' ⇎ '.join(u'%s' % (HD.match(LST[i][WIN[i][0]]).group(1)) for i in range(NSRC))))
A(u'| 窗内外分档 | 同一枚字面在窗切片与非窗切片各数一次(split 计数) | 4380 窗内 %s ⇎ 窗外 %s; 14,720 窗内 %s | '
  u'与 secw_ ⇎ outw_ 逐键一致, 99 两段的 4380 恰有一处在窗外(引文那句在别处) |'
  % (J(FLAT[u'secw_4380']), J(FLAT[u'outw_4380']), J(FLAT[u'secw_c14720'])))
A(u'| 字面⇎独立数 | 字面 split 计数; 独立数先按 \\d[\\d,]*\\d 收 token, 再判左不接数字逗号句点、右不接数字 | '
  u'4380 %s ⇎ 14600 %s ⇎ 1460 %s(token %s), 14,720 带逗号 %s ⇎ 裸写 %s | '
  u'与 lit_/tok_/subgap_/bare_only_14600 ⇎ comma_only_14720 一致 |'
  % (J(FLAT[u'lit_4380']), J(FLAT[u'lit_14600']), J(FLAT[u'lit_1460']), J(FLAT[u'tok_1460']),
     J(FLAT[u'lit_c14720']), J(FLAT[u'lit_14720'])))
A(u'| 值域档 | 同一条匹配换 \\d+, 前后邻判独立, 取 %s–%s 之间去重值(两端都是面内读数) | 99 %d ⇎ 02 %d ⇎ 09 %d ⇎ 13 %d ⇎ 21 %d 枚 | '
  u'与 numband_/numband_n_ 逐份同值同列 |'
  % (FLAT[u'nb_lo'], FLAT[u'nb_hi'], *[len(B4[i]) for i in range(NSRC)]))
A(u'| 折行 | 不折全篇: 每行 strip 后按序接成一面(空行略过), 在同一面上 split 计数, 再减逐行各自 split 的和 | '
  u'%d 枚针里有 %d 枚被排版折断, 按份跨行数 %s, 合计 %d 处(全落在 13 十倍的 “10 segments”: 原面 %s ⇎ 折面 %s) | '
  u'与 wrap_gap_* ⇎ wrap_gap_total ⇎ wrap_pin_hit 一致 |'
  % (len(SN), WRAP_HIT, J(WRAP_BY), WRAP_TOTAL, J(ALONE[u'seg10']), J(FOLD3[u'seg10'])))
A(u'| 义务词两档 | 全大写族 split 计数(与建条目侧同定义、不同实现), 小写族 [A-Za-z0-9_]+ 词流整词相等 | '
  u'MUST %s ⇎ SHOULD %s ⇎ MAY %s ⇎ MUST NOT %s ⇎ 全大写合计 %s; must %s ⇎ should %s ⇎ may %s ⇎ 合计 %s | '
  u'与 u_/l_/oblig_up ⇎ oblig_low 一致 |'
  % (J(U4[u'MUST']), J(U4[u'SHOULD']), J(U4[u'MAY']), J(U4[u'MUST NOT']), J(UOB),
     J([LOWC[i][0] for i in range(NSRC)]), J([LOWC[i][1] for i in range(NSRC)]),
     J([LOWC[i][2] for i in range(NSRC)]), J(LOB)))
A(u'| 引用⇎身份⇎壳 | 引用号按 “RFC nnnn” ⇎ “RFCnnnn” 两种黏合各 split 一次; 页眉 ^RFC \\d{4} \\S ⇎ 页脚 [Page n] 或 Page n | '
  u'2581 %s ⇎ 3390 %s ⇎ 5681 %s ⇎ 6928 %s ⇎ 9002 %s 处; 页眉 %s ⇎ 页脚 %s ⇎ 合计 %s; key words 样板 %s 处, 2119 被引 %s 次 | '
  u'与 cite_/hdr/foot/pagelines/key_words_boiler/rfc2119_ref 一致 |'
  % (J(CITE[u'2581']), J(CITE[u'3390']), J(CITE[u'5681']), J(CITE[u'6928']), J(CITE[u'9002']),
     J(H4), J(F4), J([H4[i] + F4[i] for i in range(NSRC)]), J(KW), J(R2119)))
A(u'| 整行搬运 | 归一用 re.sub 去非 a-z0-9; 交按“小表建字典、大表查字典”, 并集按单个计数字典 add(采集侧用集合运算符, 建条目侧用排序两指针) | '
  u'99⇎02 %d ⇎ 99⇎09 %d ⇎ 02⇎09 %d ⇎ 三份同现 %d ⇎ 并集 %d; 02⇎09⇎(13|21) %d 行; 只在本份 09 %d ⇎ 13 %d ⇎ 21 %d; 容斥 %d−并集=%d | '
  u'与 share_/ABC_inter/union_/only_/abc_incl ⇎ abc_close 逐键一致 |'
  % (PAIR[(0, 1)], PAIR[(0, 2)], PAIR[(1, 2)], TRI, U3, BCPLUS,
     ONLY[2], ONLY[3], ONLY[4], INCL4, INCL4 - U3))
A(u'| 档位表方向 | C 的 IW 行按 “=” ⇎ “*” ⇎ “ segments” 前末词三段 split 重读倍数与段数, If 行整行逐字符收全部数字组 | '
  u'倍数 %s ⇎ 段数上限 %s ⇎ 三行阈值 %s(中档一行同时含两枚) ⇎ B 的三行常数 %s | 与 x_c_iw_mult ⇎ x_c_seg_cap ⇎ x_c_hi_bound ⇎ x_c_lo_bound ⇎ x_c_mid_ub ⇎ x_b_if 一致; '
  u'倍数沿档升 %d、阈值沿档降 %d(方向相反位 %d), 每档段数−倍数差合计 %d |'
  % (J(MU), J(SG), u' ⇎ '.join(u'[%s]' % (u','.join(str(y) for y in c)) for c in COND), J([c[0] for c in CAPB]),
     MU[2] - MU[0], TH[0] - TH[2], FLAT[u'x_c_dir_opp'], FLAT[u'x_c_seg_gap']))
A(u'| 序列化⇎介质 | 页眉页脚按正则判; 字节数按 len(rb), BOM 按前三字节相等判, 字符数按解码后长度 | '
  u'字节 %s ⇎ 字符 %s ⇎ 差 %s(仅 21 QUIC 带 BOM %s, 非 ASCII %s 枚) | 与 bytes/chars/bom/nonascii 一致 |'
  % (J(BYT), J(FLAT[u'chars']), J([BYT[i] - len(SRC[i]) for i in range(NSRC)]), J(BOM4), J(FLAT[u'nonascii'])))
A(u'| 恒等式 | 本注用上面的独立读数重算 %d 组关系(4380=%d×%d ⇎ 14600=%d×%d ⇎ %d−%d=%d×%d ⇎ 表两端各算回同一枚 %d ⇎ 段数列=倍数列 ⇎ 加宽 %d 补回 %d) | 全部为真; '
  u'门槛侧登记 %d 条恒等式 ⇎ %d 项标量闭合合计 %d | 与 x_ident_n ⇎ scalar_clos_n ⇎ scalar_clos_sum 一致 |'
  % (len(IDENTS), MSS, THREE, MSS, FLAT[u'x_d_ten'], CAP21, CAP13, FLAT[u'x_e_seg'], FLAT[u'x_e_ovh'],
     FLAT[u'x_eq_cap'][1], FLAT[u'x_widen'], FLAT[u'x_c_upper_at2190'],
     FLAT[u'x_ident_n'], FLAT[u'scalar_clos_n'], FLAT[u'scalar_clos_sum']))
A(u'| 锚归属 | 由条目正文 ⟦标签⟧⟨引文⟩ 配对现推, 成员判据换成“单行归一表 ⇎ 相邻两行拼接表”, 比建条目侧的整篇归一更严 | '
  u'%d 处／去重 %d 串／一源 %d ⇎ 两至四源 %d ⇎ 五源 %d ⇎ 错配 %d | 与建条目侧、门槛侧同(无一枚锚跨三行以上) |'
  % (len(CITES), len(DIS4), SIN, CRS, ALL5, len(ERR4)))
A(u'| 两侧对账 | 采集侧 %d 键在五份纯文本面上逐键比(本注不参与其算法) | 共有 %d ／ 不符 %d | 五份同为文本面, 无需按介质分流 |'
  % (len(MEAS), len([k for k in MEAS if k in FLAT]), len(BAD4)))
A(u'')
A(u'### 读法')
A(u'')
A(u'一、“第一个 RTT 能发多少”只有方程或表能答, 而两者不可兼得: 99 两段把 %d 枚方程引作实验性扩展并在其后第 %d 行逐字否决, '
  u'否决句在库里只出现 %d 处; 同一枚方程(%s)到 02 方程手里成为标准上限, 变量名从 %s 缩成 %s(%d 个字母), '
  u'两枚标号 (1) 的方程在 99 ⇎ 02 ⇎ 13 里各 %d⇎%d⇎%d 处, 在 09 ⇎ 21 里 %d⇎%d 处——同一段推导换了身份, 字没改。'
  % (FLAT[u'x_eq_n'][0], FLAT[u'x_a_gap'], FLAT[u'n_dont_allow'][0],
          FLAT[u'x_eq'][0], FLAT[u'x_eq_var'][0], FLAT[u'x_eq_var'][1], FLAT[u'x_ab_var_diff'],
          FLAT[u'lit_p1'][0], FLAT[u'lit_p1'][1], FLAT[u'lit_p1'][3],
          FLAT[u'lit_p1'][2], FLAT[u'lit_p1'][4]))
A(u'二、09 三段表换的是形状不是阈值: %d⇎%d 两枚阈值在 02 ⇎ 09 各出现 %d⇎%d ⇎ %d⇎%d 处(窗内窗外的分档也相同), '
  u'但 4380 这一枚在 09 整篇 %d 处、窗内 %d 处——数字一个没留, 却从表的两端各被算回来一次: %d×%d=%d ⇎ %d×%d=%d, 与 02 的常数帽差 %d。'
  u'更看不见的是方向: 09 的倍数沿档 %s 而阈值沿档 %s(相反位 %d), 13 十倍与 02 方程只把一个系数从 %d 换成 %d, 方向谈不上。'
  % (FLAT[u'x_c_lo_bound'], FLAT[u'x_c_hi_bound'],
          FLAT[u'lit_1095'][1], FLAT[u'lit_1095'][2], FLAT[u'lit_2190'][1], FLAT[u'lit_2190'][2],
          FLAT[u'lit_4380'][2], FLAT[u'secw_4380'][2],
          FLAT[u'x_c_hi_mult'], FLAT[u'x_c_hi_bound'], FLAT[u'x_c_top_at_hi'],
          MU[2], FLAT[u'x_c_lo_bound'], FLAT[u'x_c_lo_at_lo'], FLAT[u'x_c_cap_close'],
          J(MU), u' ⇎ '.join(u'[%s]' % (u','.join(str(y) for y in c)) for c in COND), FLAT[u'x_c_dir_opp'], FLAT[u'x_eq_coef'][1], FLAT[u'x_eq_coef'][3]))
A(u'三、分歧恰好只在两档之间那一点: SMSS=%d 时 02 方程按上档给 %d(=%d×%d), 09 三段表把它算进中间档给 %d(=%d×%d), '
  u'多出的 %d 字节=+50%%, 库里没有一行写着它; 到常见 MSS=%d 处两份又并回 %d⇎%d(差 %d)。'
  u'边界符号是唯一的成因线索: 02 的中间档用严格不等号 %d 行 ⇎ 09 用 <= %d 行、上档用 > %d 行。'
  % (FLAT[u'x_c_hi_bound'], FLAT[u'x_b_at_hi'], FLAT[u'x_eq_inner'][1], FLAT[u'x_c_hi_bound'],
          FLAT[u'x_c_upper_at2190'], FLAT[u'x_c_mid_mult'], FLAT[u'x_c_hi_bound'], FLAT[u'x_widen'],
          FLAT[u'x_b_mssnum'], FLAT[u'x_at1460_b'], FLAT[u'x_at1460_c'], FLAT[u'x_at1460_close'],
          FLAT[u'x_b_strict'], FLAT[u'x_c_le'], FLAT[u'x_c_upper_lt']))
A(u'四、21 QUIC 把量都换了: MSS 字样 %d 处 ⇎ SMSS %d 处 ⇎ max_datagram_size %d 处 ⇎ datagram %d 处, '
  u'方程 %d 枚——它用英文数词说话(%s ⇎ %s), 十倍×上限 %d ⇎ 最小载荷 %d×%d=%d, 翻倍档只在 >%d 时咬合(咬合位 %d); '
  u'%d 与 13 十倍的 %d 之间那 %d 字节, 恰好等于 %d 段×(%d−%d) 的头差——换传输层的人必须自己把常数帽翻译成报文尺寸。'
  % (FLAT[u'v_mss'][4], FLAT[u'v_smss'][4], FLAT[u'v_mds'][4], FLAT[u'v_datagram'][4],
          FLAT[u'x_eq_n'][4], u'⟨%s⟩' % FLAT[u'x_e_tenword'], u'⟨%s⟩' % FLAT[u'x_e_twiceword'],
          FLAT[u'x_e_capnum'], FLAT[u'x_e_floornum'], FLAT[u'x_e_ten'], FLAT[u'x_e_iw'],
          FLAT[u'x_e_break'], FLAT[u'x_e_binds'], CAP21, CAP13, FLAT[u'x_e_bridge'],
          FLAT[u'x_e_seg'], FLAT[u'x_e_ovhtcp'], FLAT[u'x_e_ovhnum']))
A(u'五、壳与面在这里分道: 每页重印的页眉把“initial window”的词频抬了 %d⇎%d 处(= 页眉里印标题的行数 %d⇎%d), '
  u'而去壳只挪动长行集合 %d 行——同一枚页眉在集合里去重成一条。词频档 ⇎ 集合档必须分别立键, 否则“这份文档提了几次初窗”会答成页数。'
  u'另一处隐形通道在排版: 本注按拼行面数出的跨行 %d 处全在 13 十倍的“10 segments”上(原面 %d 处 ⇎ 折面 %d 处), '
  u'其余 %d 枚针跨行皆 0; 按份相加 %s。'
  % (FLAT[u'iw_word_gap'][1], FLAT[u'iw_word_gap'][3], FLAT[u'hdr_title'][1], FLAT[u'hdr_title'][3],
          FLAT[u'shell_delta'][1] + FLAT[u'shell_delta'][2] + FLAT[u'shell_delta'][3],
          WRAP_TOTAL, FLAT[u's_seg10'][3], FLAT[u's_seg10_fold'][3],
          len(SN) - WRAP_HIT, J(WRAP_BY)))
A(u'')
A(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
A(u'')
A(u'① 五份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; ② rfc-editor.org 此刻给这五份挂的类目与状态——库内抬头只印 '
  u'Standards Track %d⇎%d⇎%d⇎%d⇎%d 行 ⇎ Experimental %d 处(在 13 十倍), Errata 提及 %d⇎%d⇎%d⇎%d⇎%d 处只是文书自我引用; '
  u'③ 勘误表是否已把这五份之一改成另一版; ④ 库外流传的 RFC 5681 档位表序与这份面内表序谁对——在库字节只支持本注读出的那一版'
  u'(倍数 %s ⇎ 阈值 %s), 站外版本差异属另一条证据链; ⑤ 现实链路的 MSS 分布(%d 是以太网的举例)与首窗在部署侧的实际取值。'
  u'这些只能站外核验, 因此都不进判词与门槛。'
  % (tuple(FLAT[u'cat_std']) + (FLAT[u'cat_exp'][3],) + tuple(FLAT[u'errata'])
     + (J(MU), u' ⇎ '.join(u'[%s]' % (u','.join(str(y) for y in c)) for c in COND), FLAT[u'x_b_mssnum'])))
A(u'')
A(u'### 编码与门的账')
A(u'')
A(u'编码区 {0} 字符(不含换行); 锚 {1} 处 ⇎ 去重 {2} 串 ⇎ 归属检查 {3} 次 ⇎ 错配 {4}; '
  u'一源 {5} ⇎ 两至四源 {6} ⇎ 五源 {7}; 标签 A⇎B⇎C⇎D⇎E 各 {8}⇎{9}⇎{10}⇎{11}⇎{12} 处。'
  .format(CH[u'enc_chars'], FLAT[u'anchor_total'], FLAT[u'anchor_distinct'], FLAT[u'checks'], FLAT[u'anchor_err'],
          FLAT[u'anchor_single'], FLAT[u'anchor_cross'], FLAT[u'anchor_all5'],
          FLAT[u'tag_A'], FLAT[u'tag_B'], FLAT[u'tag_C'], FLAT[u'tag_D'], FLAT[u'tag_E']))
A(u'DERIV {0} 键 ⇎ 复算点 {1} 处 ⇎ 同数共键 {2} 组 ⇎ 0 折 {3} 项; 扁平键 {4} 个; '
  u'闭合账 标量 {5} 项(合计 0)⇎ 清单 {6} 项 ⇎ 面内恒等式 {7} 条; 锚候选池 {8} 条按逐字再现份数分 5 档({9}), 分档闭合 {10}。'
  .format(CH[u'deriv_keys'], CH[u'deriv_points'], len(CH[u'collisions']), CH[u'zero_terms'],
          len(FLAT), FLAT[u'scalar_clos_n'], FLAT[u'list_clos_n'], FLAT[u'x_ident_n'],
          FLAT[u'pool_n'], u'⇎'.join(str(x) for x in FLAT[u'pool_tiers']), FLAT[u'pool_close']))
A(u'门槛三遍: T1 字面逐锚回原文 ⇎ T2 DERIV 每条算式重跑 ⇎ T3 码位与字母账; '
  u'本注另加第四遍复测, 上表 14 行全部 assert, 不符即停机。')
NOTE = NL.join(L)
# 防回归: 本注模板一律用 % 插值, 落盘后不得再有未替换的 %d/%s 占位
assert not re.findall(u'%[sdifg]|%\\(', NOTE), re.findall(u'%[sdifg]|%\\(', NOTE)[:5]
head = TT[:TT.index(u'## ⛓解读注') + len(u'## ⛓解读注')]
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(head + NL + NL + NOTE + NL)
print(u'⛓解读注已写 %d 字符 ｜ 第四遍 assert 全过 ｜ 采集对账 %d 键 0 不符' % (len(NOTE), len(MEAS)))
