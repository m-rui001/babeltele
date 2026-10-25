# -*- coding: utf-8 -*-
"""B63 ⛓解读注(第四遍): 本注每个数都是现测并 assert 的, 不手填。
四套实现: 采集侧 corpus/_pick63.py(re.findall 与前后瞻数时长、集合运算求搬运、sha256 签名档)
⇎ 建条目侧 corpus/_mkB63.py(游标档 find 循环 + 逐字符判邻、逐字符切“数字+空白+单位”、深度计数的和式拆分、
  排序两指针求交, 扁平契约 corpus/_b63flat.json)
⇎ 门槛侧 corpus/audit.py::_b63_scan()(由 corpus/_wire63.py 从 SCAN 段机械抽出, 插门前把全部扁平键与
全部 DERIV 算式在抽出体上逐条预演) ⇎ 本注第四遍。
本注的读法与前三遍都不同:
①时长族不逐字符走位: 一条正则 (\\d[\\d,]*)(空白类)(单位族)(?![A-Za-z]) 收非重叠 token, 单位族按长名先试的次序与建条目侧同,
  归一乘数表也同, 于是“跨行”⇎“小数割裂”两枚标志只是把 group(2) 里查换行、把 start 前两根字符查句点——
  答数行、宣称行、上限行、地板上取整行、(5.7) 回退行都从同一个搜索器派生, 一个常数也不手填;
②和式行不用缓冲区逐字符: 先按行首 (RTO|PTO) 与 <-/= 正则配对, 再对右侧统计 “ + ” 左侧的括号净深切列,
  max 档按首枚逗号拆两参数、乘积档按首个 * 拆系数与变量, 形状串由本注自己拼回与 y_sum_shape 对拍;
③面内常数走正反两向正则: 'where K = ' ⇎ 'RTTVAR <- R/' ⇎ 'rttvar = kInitialRtt / ' 取后随数字(建条目侧是 num_after 游标),
  '(\\d+)\\*rttvar' ⇎ '(\\d+)\\*MSL, i\\.e\\., 240' 取前随数字(建条目侧是 num_before 反向走位);
  PTO 的 999⇎997 两档由 333⇎4⇎1 三枚现读数复算, 与宣称的 1 秒差 1⇎3 毫秒;
④规范窗不逐行回溯: 全篇编号标题一次收成 (行号, 编号, 首 token) 表(建条目侧是就地逐字符 headnum),
  规范句最后一处命中二分出所在节, 收口沿用“strip 后同题 ⇎ 首 token 前缀同族”两条否判(93 那一份的题号 '2' 会前缀吃掉 2.1 各节),
  窗长按逐行长度相加再减一根换行, 窗偏移按 cumsum 重排;
⑤字面族与窗内外: 字面档用 len(t.split(针))-1(建条目侧是 find 循环), 窗档改用 re.finditer 取全部起点位置再按窗区间二分——
  窗外不是“总数减窗内”, 而是位置集合的补;
⑥折行档不折全篇: 每行 strip 后各自 split 成 token 再 join 成一面(建条目侧整篇 split/join), 在同一面上 split 计数, 减逐行各自 split 的和;
  14 枚针逐枚核 原面档 ⇎ 折面档 ⇎ 差;
⑦义务词两档: 全大写族 split 计数(与建条目侧同定义不同实现, 故 MUST 一档含 "MUST NOT" 内的), 小写族 [A-Za-z0-9_]+ 词流整词相等;
⑧壳账三式: 页眉 ^RFC(\\d{4})(?!\\d) 与 ^RFC \\d{4}(?!\\d) 带题文两档各自立键再与并档对账,
  页脚按 \\[Page \\d+\\]$ ⇎ Page \\d+$ 两档、机构名页脚另按行首字串判; 换页符按逐字符计数、行尾空格按行与 rstrip 比较;
⑨B⇎C 条款对照: (2.4) 起四行按“最后一处 Whenever RTO is computed 行 + 偏移”配对, 逐字节相等 ⇎ 归一相等 ⇎ 长度差 ⇎ 逗号差四档;
⑩搬运账归一用 re.sub 去非 a-z0-9, 交按“小表建字典、大表逐条查字典”再与集合运算符 & 对拍, 并集按单个计数字典 add,
  only_* 按建条目侧的分组定义(B 比 A、C 其余三份, D 比前三份)用集合差算, 含壳⇎去壳两面各算一遍,
  字节档 ⇎ 归一档的差另立键; 锚候选池按“这条锚在几份文书逐字再现”分四档, 成员判据仍用整篇归一串;
⑪恒等式与闭合账由本注独立重算, 标量闭合清单从扁平表按键名规则(_close/_resid/_ledger)重新导出与 scalar_clos_list 对拍;
⑫锚归属由条目正文配对现推, 成员判据双轨: 流式拼面(逐行归一相接, 每批只留末尾 len(锚)−1 字符续接, 不现造整篇面)定档,
  再用逐行两档(单行含锚 ⇎ 相邻两行拼接含锚)对拍, 两式必须同判; 另求“这枚锚最少压在几行上”(1..5 行滑窗, 裁窗后判)得行跨度分布;
  四份签名按 blake2b 前 16 位在本注重算一遍。
不可由在库文件判定的只写在本注: 四份的抓取时刻与磁盘 mtime 谁新谁旧、rfc-editor.org 此刻的现行状态页与
Obsoletes/Updates 关系图、勘误表是否已挂新版、各 OS 里 TCP_RTO_MIN 的实际取值、现实链路 RTT 分布——都不进判词与门槛。
"""
import io, os, re, sys, json, bisect, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B63_tcp_initial_rto_four_answers.md')
FLAT = json.load(io.open(C + u'/_b63flat.json', encoding=u'utf-8'))
MEAS = json.load(io.open(C + u'/_b63meas.json', encoding=u'utf-8'))
CH = json.load(io.open(C + u'/_b63checks.json', encoding=u'utf-8'))
DER = json.load(io.open(C + u'/_deriv63.json', encoding=u'utf-8'))
PATH = [u'corpus/raw/tcpRTO/rfc1122.txt', u'corpus/raw/tcpRTO/rfc2988.txt', u'corpus/raw/tcpRTO/rfc6298.txt',
        u'corpus/raw/tcpiw/rfc9002.txt']
TAGS = [u'A', u'B', u'C', u'D']
LBL = dict(zip(TAGS, [u'89 三秒', u'00 三秒', u'11 一秒', u'21 三百三']))
RD = lambda p: io.open(p, encoding=u'utf-8-sig').read()
SRC = [RD(p) for p in PATH]
LST = [t.split(NL) for t in SRC]
RB = [open(p, 'rb').read() for p in PATH]
NSRC = 4
J = lambda xs: u'⇎'.join(str(x) for x in xs)
sc = lambda t, needle: len(t.split(needle)) - 1
WF = re.compile(u'[A-Za-z0-9_]+')
D = u'0123456789'


def nrm(l):
    return re.sub(u'[^a-z0-9]', u'', l.lower())


def occ4(t, needle, frm=0, to=None):
    return [m.start() for m in re.finditer(re.escape(needle), t[frm:to if to is not None else len(t)])]


# ---- ①时长族: 一条正则收 token, 归一到毫秒 ----
MUL = {u'milliseconds': 1, u'millisecond': 1, u'ms': 1, u'seconds': 1000, u'second': 1000,
       u'sec': 1000, u'useconds': 0, u'usecond': 0}
DURRE = re.compile(u'(\\d[\\d,]*)((?:[ \\t\\n\\x0b\\x0c\\r])*)(' + u'|'.join(MUL) + u')(?![A-Za-z])')


def durs(t):
    out = []
    for m in DURRE.finditer(t):
        n, gap, u = m.group(1), m.group(2), m.group(3)
        s = m.start(1)
        frac = 1 if s >= 2 and t[s - 1] == u'.' and t[s - 2] in D else 0
        out.append((int(n.replace(u',', u'')) * MUL[u], s, n, u, 1 if NL in gap else 0, frac))
    return out


DU = [durs(t) for t in SRC]
DM, DL, DW, DF = [], [], [], []
for i in range(NSRC):
    dm = sorted(set(x[0] for x in DU[i] if x[0] > 0))
    DM.append(dm)
    assert dm == FLAT[u'durms_' + TAGS[i].lower()], (i, dm, FLAT[u'durms_' + TAGS[i].lower()])
    assert len(dm) == FLAT[u'durms_n_' + TAGS[i].lower()] and len(DU[i]) == FLAT[u'durlit_' + TAGS[i].lower()]
    DW.append(len([x for x in DU[i] if x[4]]))
    DF.append(len([x for x in DU[i] if x[5]]))
assert [len(DM[i]) for i in range(NSRC)] == FLAT[u'durms_n'] and [len(DU[i]) for i in range(NSRC)] == FLAT[u'durlit']
LO, HI = min(min(x) for x in DM), max(max(x) for x in DM)
assert (LO, HI) == (FLAT[u'dur_ms_lo'], FLAT[u'dur_ms_hi'])
assert HI // LO == FLAT[u'y_dur_ratio'] and HI % LO == FLAT[u'y_dur_rem'] == 0
assert DW == FLAT[u'y_dur_wrap'] and DF == FLAT[u'y_dur_frac']
FV = [sorted(set(x[0] for x in DU[i] if x[5])) for i in range(NSRC)]
WV = [sorted(set(x[0] for x in DU[i] if x[4])) for i in range(NSRC)]
assert FV == [list(x) for x in FLAT[u'y_dur_frac_vals']], FV
assert WV == [list(x) for x in FLAT[u'y_dur_wrap_ms']], WV
assert [len([v for v in DM[i] if v in FV[i]]) for i in range(NSRC)] == FLAT[u'y_dur_frac_only']
assert [len([x for x in DU[i] if x[0] == 0]) for i in range(NSRC)] == FLAT[u'y_dur_zero']
assert [len([x for x in DU[i] if x[0] == 0 and x[4]]) for i in range(NSRC)] == FLAT[u'y_dur_zero_wrap']
assert [len([x for x in DU[i] if x[0] == 0 and x[5]]) for i in range(NSRC)] == FLAT[u'y_dur_zero_frac']
UU = [sorted(set(x[3] for x in DU[i])) for i in range(NSRC)]
assert UU == [list(x) for x in FLAT[u'y_unit_used']] and [len(x) for x in UU] == FLAT[u'y_unit_n']
assert [sc(SRC[i], u'second') for i in range(NSRC)] == FLAT[u'unit_seconds']
assert [sc(SRC[i], u'ms') for i in range(NSRC)] == FLAT[u'unit_ms']
assert [sc(SRC[i], u'millisecond') for i in range(NSRC)] == FLAT[u'unit_mill_word']


def da(t, needle, rng=240):
    """针之后第一枚时长 token(与建条目侧的 dur_after 同定义: 复用同一个搜索器, 故数与单位跨行也算一枚)。"""
    p = t.find(needle)
    if p < 0:
        return (0, u'', u'', 0)
    m = DURRE.search(t, p + len(needle), p + len(needle) + rng)
    if not m:
        return (0, u'', u'', 0)
    n, gap, u = m.group(1), m.group(2), m.group(3)
    return (int(n.replace(u',', u'')) * MUL[u], n, u, 1 if NL in gap else 0)


ANSN = {u'A': u'(b)  RTO = ', u'B': u'set RTO <- ', u'C': u'set RTO <- ', u'D': u'SHOULD be set to '}
ANS = [da(SRC[i], ANSN[TAGS[i]]) for i in range(NSRC)]
ANS_MS = [x[0] for x in ANS]
assert ANS_MS == FLAT[u'y_ans_ms'], (ANS_MS, FLAT[u'y_ans_ms'])
assert [x[1] for x in ANS] == FLAT[u'y_ans_num'] and [x[2] for x in ANS] == FLAT[u'y_ans_unit']
assert [x[3] for x in ANS] == FLAT[u'y_ans_wrap'] == [0] * NSRC
assert [1 if x[2] == u'second' else 0 for x in ANS] == FLAT[u'y_ans_unit_sing']
MAXA, MINA = max(ANS_MS), min(ANS_MS)
RATIO, REM = MAXA // MINA, MAXA % MINA
assert len(set(ANS_MS)) == FLAT[u'y_ans_distinct'] == 3 and (MAXA, MINA) == (3000, 333)
assert (RATIO, REM) == (FLAT[u'y_ans_ratio'], FLAT[u'y_ans_rem'])
CLM = [da(SRC[i], u'starting with a PTO of ')[0] for i in range(NSRC)]
CLAIM_MS = [c if c else ANS_MS[i] for i, c in enumerate(CLM)]
assert CLAIM_MS == FLAT[u'y_claim_ms'] and len(set(CLAIM_MS)) == FLAT[u'y_claim_distinct'] == 2
assert len(set(CLAIM_MS)) - len(set(ANS_MS)) == FLAT[u'y_claim_vs_ans'] == -1
assert [sc(SRC[i], u'RTT = 0 seconds') for i in range(NSRC)] == FLAT[u'y_rtt0']

# ---- ②和式结构: 正则配左部, 括号净深切 ' + ' 分列 ----
def split0(rhs):
    """深度 0 的 ' + ' 分列: 左段止于空格、右段起于加号后的空格(建条目侧用缓冲区逐字符回吐)。"""
    out, s0, d, k = [], 0, 0, 0
    while k < len(rhs):
        if rhs[k] == u'(':
            d += 1
        elif rhs[k] == u')':
            d -= 1
        elif rhs[k:k + 3] == u' + ' and d == 0:
            out.append(rhs[s0:k].strip())
            s0 = k + 2
            k += 2
        k += 1
    out.append(rhs[s0:].strip())
    return [x for x in out if x]


def ismax4(tm):
    q = tm.find(u'(')
    return tm.startswith(u'max') and q >= 0 and u',' in tm[q + 1:tm.rfind(u')')]


SUMS = []
for i in range(NSRC):
    got = []
    for l in LST[i]:
        s = l.strip()
        m = re.match(u'^(RTO|PTO)\\s*(<-|=)\\s*(.+)$', s)
        if not m:
            continue
        terms = split0(m.group(3))
        mi = next((z for z, tm in enumerate(terms) if ismax4(tm)), -1)
        base = tail = u''
        mf = ms = coef = mvar = u''
        for z, tm in enumerate(terms):
            if ismax4(tm):
                inner = tm[tm.find(u'(') + 1:tm.rfind(u')')]
                a1, a2 = inner.split(u',', 1)
                mf, ms = a1.strip(), a2.strip()
                for tm2 in (a1.strip(), a2.strip()):
                    if u'*' in tm2:
                        coef, mvar = tm2.split(u'*', 1)
            elif mi < 0 or z < mi:
                base = (base + u'+' + tm) if base else tm
            else:
                tail = (tail + u'+' + tm) if tail else tm
        got.append((m.group(1), m.group(2), len(terms), mf, ms, coef, mvar, base, tail))
    SUMS.append(got)
SN_ = [len(g) for g in SUMS]
assert SN_ == FLAT[u'y_sum_n'], (SN_, FLAT[u'y_sum_n'])
for z, key in ((1, u'y_sum_op'), (2, u'y_sum_nterms'), (3, u'y_sum_mfirst'), (4, u'y_sum_msecond'),
               (5, u'y_sum_coef'), (6, u'y_sum_mvar'), (7, u'y_sum_base'), (8, u'y_sum_tail')):
    got = [g[0][z] if g else u'' for g in SUMS]
    if z == 2:
        got = [g[0][z] if g else 0 for g in SUMS]
    assert got == FLAT[key], (key, got, FLAT[key])
assert [g[0][0] if g else u'' for g in SUMS] == FLAT[u'y_sum_lhs']
SHAPE = [u'%s%s%s+%s' % (g[0][0], g[0][1], g[0][3], g[0][4]) if g else u'无和式' for g in SUMS]
assert SHAPE == FLAT[u'y_sum_shape'], SHAPE
assert [1 if g and g[0][8] else 0 for g in SUMS] == FLAT[u'y_sum_tail_n']
assert [1 if g and u'*' in g[0][3] else 0 for g in SUMS] == FLAT[u'y_sum_var_first']
assert [1 if g and g[0][5] and g[0][5].isdigit() else 0 for g in SUMS] == FLAT[u'y_coef_islit']
assert [int(g[0][5]) if g and g[0][5].isdigit() else 0 for g in SUMS] == FLAT[u'y_coef_num']

# ---- ③面内常数(正反两向正则) ⇎ PTO 复算 ----
def na4(t, needle):
    m = re.search(re.escape(needle) + u'\\s*(\\d[\\d,]*)', t)
    return int(m.group(1).replace(u',', u'')) if m else 0


def nb4(t, needle):
    m = re.search(u'(\\d+)' + re.escape(needle), t)
    return int(m.group(1)) if m else 0


K_BC = [na4(SRC[i], u'where K = ') for i in range(NSRC)]
K_D = nb4(SRC[3], u'*rttvar')
MULT_A = nb4(SRC[0], u'*MSL, i.e., 240')
HALF = [na4(SRC[1], u'RTTVAR <- R/'), na4(SRC[2], u'RTTVAR <- R/'), na4(SRC[3], u'rttvar = kInitialRtt / ')]
GRAN = da(SRC[3], u'Section 6.1.2 recommends a value of ')
KINIT = na4(SRC[3], u'Section 6.2.2 is ')
CAP_A = da(SRC[0], u'upper bound should be ')
CAP_BC = [da(SRC[i], u'provided it is at least ') for i in range(NSRC)]
FLOOR = [da(SRC[i], u'rounded up to ') for i in range(NSRC)]
REVERT = da(SRC[2], u're-initialized to ')
assert K_BC == FLAT[u'y_bc_kdef'] and K_BC[1] == FLAT[u'y_b_kdef'] == K_BC[2] == FLAT[u'y_c_kdef']
assert K_D == FLAT[u'y_d_k'] == 4 and MULT_A == FLAT[u'y_a_mult'] == 2
assert HALF == [FLAT[u'y_half_b'], FLAT[u'y_half_c'], FLAT[u'y_half_d']] == [2, 2, 2]
assert GRAN[0] == FLAT[u'y_d_gran'] and GRAN[2] == FLAT[u'y_d_gran_unit'] and GRAN[3] == 0
assert KINIT == FLAT[u'y_d_kinit'] == 333
assert CAP_A == tuple(FLAT[u'y_a_cap']) and [x[0] for x in CAP_BC] == FLAT[u'y_bc_cap_ms']
assert [x[3] for x in CAP_BC] == [0, 1, 1, 0] == FLAT[u'y_bc_cap_wrap'] and CAP_A[3] == FLAT[u'y_a_cap_wrap'] == 1
assert [x[0] for x in FLOOR] == FLAT[u'y_floor_ms'] and [x[3] for x in FLOOR] == FLAT[u'y_floor_wrap']
assert REVERT[0] == FLAT[u'y_c_revert_ms'] == 3000 and REVERT[3] == FLAT[u'y_c_revert_wrap'] == 0
REF = CAP_BC[1][0]
CR, CREM = CAP_A[0] // REF, CAP_A[0] % REF
assert (CR, CREM) == (FLAT[u'y_cap_ratio'], FLAT[u'y_cap_rem']) == (4, 0)
PTO_EX = ANS_MS[3] + (K_D * ANS_MS[3]) // 2
PTO_IN = ANS_MS[3] + K_D * (ANS_MS[3] // 2)
VAR_I, VAR_F = ANS_MS[3] // 2, ANS_MS[3] % 2
THREE = K_D // 2 + 1
assert PTO_EX == FLAT[u'y_d_pto_exact'] == 999 and PTO_IN == FLAT[u'y_d_pto_int'] == 997
assert CLM[3] == FLAT[u'y_d_claim_ms'] == 1000
assert CLM[3] - PTO_EX == FLAT[u'y_d_gap_exact'] == 1 and CLM[3] - PTO_IN == FLAT[u'y_d_gap_int'] == 3
assert PTO_EX - PTO_IN == FLAT[u'y_d_pto_spread'] == 2 == FLAT[u'y_d_gap_int'] - FLAT[u'y_d_gap_exact']
assert THREE == FLAT[u'y_d_three'] and PTO_EX - THREE * ANS_MS[3] == FLAT[u'y_d_three_close'] == 0
assert (VAR_I, VAR_F) == (FLAT[u'y_d_var_int'], FLAT[u'y_d_var_frac']) == (166, 1)
GRANSYM = [sc(SRC[i], u'G seconds') for i in range(NSRC)]
assert GRANSYM == FLAT[u'y_gransym']
ROUNDG = [sc(SRC[i], u'MUST be rounded to G seconds') for i in range(NSRC)]
assert ROUNDG == FLAT[u'y_roundg']
assert [sc(SRC[i], u'will result in this RTO') for i in range(NSRC)] == FLAT[u'y_bc_varfrom']
assert [sc(SRC[i], u'The smoothed variance is to be') for i in range(NSRC)] == FLAT[u'y_a_sent_in_bc']
assert sc(SRC[2], u'MAY still use') == FLAT[u'y_c_may_still'] and sc(SRC[1], u'MAY still use') == FLAT[u'y_b_may_still'] == 0
assert sc(SRC[2], u'Rationale for Lowering the Initial RTO') == FLAT[u'y_c_lower_note'] == 1
assert sc(SRC[3], u'max_ack_delay in the PTO period computation is set to 0') == FLAT[u'y_d_mad0'] == 1
assert sc(SRC[3], u'PTO period MUST be at least kGranularity') == FLAT[u'y_d_floor'] == 1
assert sc(SRC[3], u'is 333 ms') == FLAT[u'y_d_kinit_lit'] == 1

# ---- ④规范窗: 标题表 + bisect ----
RULE = {u'A': u'(b)  RTO = 3 seconds', u'B': u'set RTO <- 3 seconds (per RFC 1122',
        u'C': u'set RTO <- 1 second', u'D': u'SHOULD be set to 333 milliseconds'}
HD = re.compile(u'^[ \\t\\n\\x0b\\x0c\\r]*(\\d+(?:\\.\\d+)*)(\\.?)[ \\t\\x0b\\x0c\\r]+\\S')
CUM = []
for i in range(NSRC):
    o, s = [], 0
    for l in LST[i]:
        o.append(s)
        s += len(l) + 1
    CUM.append(o)
WIN, WLEN, WNUM = [], [], []
for i in range(NSRC):
    ls = LST[i]
    hits = [n for n, l in enumerate(ls) if RULE[TAGS[i]] in l]
    r = hits[-1]
    assert len(hits) == FLAT[u'sec_hit'][i], (i, hits)
    heads = [(n, HD.match(l).group(1), l.strip()) for n, l in enumerate(ls)
             if HD.match(l) and len(l.strip()) > 3]
    keys = [h[0] for h in heads]
    p = bisect.bisect_right(keys, r) - 1
    a, na, sa = heads[p]
    WNUM.append(na)
    pre = sa.split(u' ')[0]
    b = len(ls)
    for n, _, s in heads:
        if n > r and s != sa and not s.startswith(pre):
            b = n
            break
    WIN.append((a, b))
    WLEN.append(sum(len(x) + 1 for x in ls[a:b]) - 1)
assert WIN == [tuple(x) for x in FLAT[u'sec_w']]
assert [w[0] for w in WIN] == FLAT[u'sec_a'] and [w[1] for w in WIN] == FLAT[u'sec_b']
assert WLEN == FLAT[u'sec_len']
assert [x.replace(u'..', u'.') for x in FLAT[u'sec_num']] == WNUM, (WNUM, FLAT[u'sec_num'])
assert [LST[i][WIN[i][0]].strip()[:64] for i in range(NSRC)] == FLAT[u'sec_head']
assert [list(x) for x in [(CUM[i][WIN[i][0]], CUM[i][WIN[i][1]] - 1) for i in range(NSRC)]] == [list(x) for x in
        [FLAT[u'sec_off_' + t.lower()] for t in TAGS]]
SUB = re.compile(u'^[ \\t]*\\(?([a-z])\\)[ \\t]+\\S')
assert [len([l for l in LST[i][WIN[i][0]:WIN[i][1]] if SUB.match(l)]) for i in range(NSRC)] == FLAT[u'sec_sub']
WOFF = [(CUM[i][WIN[i][0]], CUM[i][WIN[i][1]] - 1) for i in range(NSRC)]

# ---- ⑤字面族 ⇎ 窗内外(位置集合的补, 不是总数减窗内) ----
LITK = {u'3seconds': u'3 seconds', u'1second': u'1 second', u'333ms': u'333 ms', u'1ms': u'1 ms',
        u'200ms': u'200 ms', u'rtoarrow': u'RTO <- ', u'rtovalue': u'RTO = ', u'setrto': u'set RTO',
        u'inirto': u'initial RTO', u'rounded': u'rounded up', u'kgran': u'kGranularity',
        u'kinirtt': u'kInitialRtt', u'smoothed': u'smoothed_rtt', u'rttvar_l': u'rttvar',
        u'rttvar_u': u'RTTVAR', u'srtt': u'SRTT', u'pto': u'PTO', u'rto': u'RTO', u'4xrttvar': u'4*rttvar',
        u'4k_rttvar': u'4 * rttvar', u'backoff': u'backing off',
        u'commab': u'less than 1 second then the', u'commac': u'less than 1 second, then the',
        u'revert': u'MUST be re-initialized to 3 seconds', u'onesecclaim': u'a PTO of 1 second',
        u'tcpinitrto': u"TCP's initial", u'jaco': u'Jacobson', u'333full': u'333 milliseconds',
        u'half': u'rttvar = kInitialRtt / 2', u'pto_eq': u'PTO = smoothed_rtt',
        u'smoothinit': u'smoothed_rtt = kInitialRtt'}
LIT4 = {}
for k in sorted(LITK):
    LIT4[k] = [sc(SRC[i], LITK[k]) for i in range(NSRC)]
    assert LIT4[k] == FLAT[u'lit_' + k], (k, LIT4[k], FLAT[u'lit_' + k])
assert [LIT4[u'rtoarrow'][i] + LIT4[u'rtovalue'][i] for i in range(NSRC)] == FLAT[u'assign_forms']
assert [LIT4[u'rtoarrow'][i] - LIT4[u'rtovalue'][i] for i in range(NSRC)] == FLAT[u'assign_gap']
assert [LIT4[u'commab'][i] + LIT4[u'commac'][i] for i in range(NSRC)] == FLAT[u'floor_forms_gap']
assert [1 if LIT4[u'333ms'][i] and LIT4[u'333full'][i] else 0 for i in range(NSRC)] == FLAT[u'unit_both_333']
assert [LIT4[u'4k_rttvar'][i] - LIT4[u'4xrttvar'][i] for i in range(NSRC)] == FLAT[u'y_klit_close'] == [0] * 4
assert LIT4[u'4k_rttvar'] == FLAT[u'y_klit_sp'] and LIT4[u'4xrttvar'] == FLAT[u'y_klit_ns']
SECW4, OUTW4 = {}, {}
for k in (u'3seconds', u'1second', u'333ms', u'333full', u'rtoarrow', u'rounded', u'kgran'):
    pin, pout = [], []
    for i in range(NSRC):
        ps = [x + WOFF[i][0] for x in occ4(SRC[i], LITK[k], WOFF[i][0], WOFF[i][1])]
        allp = [x + 0 for x in occ4(SRC[i], LITK[k])]
        pin.append(len(ps))
        pout.append(len([x for x in allp if not (WOFF[i][0] <= x < WOFF[i][1])]))
        assert pin[i] == FLAT[u'secw_' + k][i] and pout[i] == FLAT[u'outw_' + k][i], (k, i, pin, pout)
        assert pin[i] + pout[i] == LIT4[k][i]
WK2 = [(u'may', u'MAY'), (u'must', u'MUST'), (u'should', u'SHOULD'), (u'inirto', u'initial RTO'),
       (u'threesec', u'3 seconds'), (u'appendix', u'Appendix')]
SECW_O, OUTW_O = {}, {}
for k, s in WK2:
    a = [len([x + WOFF[i][0] for x in occ4(SRC[i], s, WOFF[i][0], WOFF[i][1])]) for i in range(NSRC)]
    b = [len([x for x in occ4(SRC[i], s) if not (WOFF[i][0] <= x < WOFF[i][1])]) for i in range(NSRC)]
    assert a == FLAT[u'y_secw_' + k] and b == FLAT[u'y_outw_' + k], (k, a, b)
    SECW_O[k], OUTW_O[k] = a, b
assert [SECW_O[u'may'][i] + SECW_O[u'must'][i] + SECW_O[u'should'][i] for i in range(NSRC)] == FLAT[u'y_oblig_win']
SECW_MN = [len([x + WOFF[i][0] for x in occ4(SRC[i], u'MUST NOT', WOFF[i][0], WOFF[i][1])]) for i in range(NSRC)]
assert SECW_MN == FLAT[u'y_secw_must_not']
assert [sc(SRC[i], u'MSL') for i in range(NSRC)][0] == FLAT[u'y_a_msl_word'] == 8

# ---- ⑥折行: 逐行 token 接面 ⇎ 逐行各自 split ----
SN = [(u'init3', u'set RTO <- 3 seconds (per RFC 1122'), (u'init1', u'set RTO <- 1 second'),
      (u'floor', u'Whenever RTO is computed, if it is less than 1 second'),
      (u'rounded', u'RTO SHOULD be rounded up to 1 second'),
      (u'revert', u'MUST be re-initialized to 3 seconds'), (u'v3', u'(b)  RTO = 3 seconds'),
      (u'ms333', u'SHOULD be set to 333 milliseconds'), (u'claim1s', u'a PTO of 1 second'),
      (u'pto_eq', u'PTO = smoothed_rtt + max(4*rttvar, kGranularity) + max_ack_delay'),
      (u'half', u'rttvar = kInitialRtt / 2'), (u'tcpinit', u"as recommended for TCP's initial"),
      (u'cite6298', u'see Section 2 of [RFC6298]'), (u'granrec', u'recommends a value of 1 ms'),
      (u'backoff5', u'the "backing off" on repeated')]
assert len(SN) == FLAT[u'wrap_pin_n']
ALONE, FOLD3, GAP3 = {}, {}, {}
JOIN = [u' '.join(u' '.join(l.split()) for l in LST[i] if l.strip()) for i in range(NSRC)]
for k, s in SN:
    ALONE[k] = [sum(len(l.split(s)) - 1 for l in LST[i]) for i in range(NSRC)]
    FOLD3[k] = [sc(JOIN[i], u' '.join(s.split())) for i in range(NSRC)]
    GAP3[k] = [FOLD3[k][i] - ALONE[k][i] for i in range(NSRC)]
    assert ALONE[k] == FLAT[u's_' + k], (k, ALONE[k], FLAT[u's_' + k])
    assert FOLD3[k] == FLAT[u's_' + k + u'_fold'], (k, FOLD3[k])
    assert GAP3[k] == FLAT[u'wrap_gap_' + k], (k, GAP3[k], FLAT[u'wrap_gap_' + k])
WRAP_TOTAL = sum(sum(x) for x in GAP3.values())
WRAP_HIT = len([k for k, s in SN if max(GAP3[k]) > 0])
WRAP_BY = [sum(GAP3[k][i] for k, s in SN) for i in range(NSRC)]
assert WRAP_TOTAL == FLAT[u'wrap_gap_total'] == 1 and WRAP_HIT == FLAT[u'wrap_pin_hit'] == 1
assert sum(WRAP_BY) == WRAP_TOTAL and WRAP_BY[1] == GAP3[u'backoff5'][1] == 1

# ---- ⑦义务词两档 ----
UPW = (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED')
U4 = dict((w, [sc(SRC[i], w) for i in range(NSRC)]) for w in UPW)
for w in UPW:
    assert U4[w] == FLAT[u'u_' + w.replace(u' ', u'_').lower()], (w, U4[w])
UOB = [U4[u'MUST'][i] + U4[u'SHOULD'][i] + U4[u'MAY'][i] for i in range(NSRC)]
assert UOB == FLAT[u'oblig_up']
LOWC = [[sum(1 for x in WF.findall(SRC[i]) if x == w) for w in (u'must', u'should', u'may')]
        for i in range(NSRC)]
assert [LOWC[i][0] for i in range(NSRC)] == FLAT[u'l_must']
assert [LOWC[i][1] for i in range(NSRC)] == FLAT[u'l_should']
assert [LOWC[i][2] for i in range(NSRC)] == FLAT[u'l_may']
LOB = [sum(x) for x in LOWC]
assert LOB == FLAT[u'oblig_low']

# ---- ⑧语汇 ⇎ 引用 ⇎ 身份 ----
WK = [(u'rto', u'RTO'), (u'pto', u'PTO'), (u'retrans', u'retransmi'), (u'rtt', u'RTT'),
      (u'rtt_low', u'rtt'), (u'clock', u'clock granularity'), (u'gran', u'granularity'),
      (u'initrto_cap', u'Initial RTO'), (u'initrto_low', u'initial RTO'), (u'timer', u'timer'),
      (u'persist', u'persistent'), (u'probe', u'probe'), (u'slowstart', u'slow start'),
      (u'congest', u'congestion control'), (u'variance', u'variance'), (u'backoff_word', u'back off')]
V4 = {}
for k, s in WK:
    V4[k] = [sc(SRC[i], s) for i in range(NSRC)]
    assert V4[k] == FLAT[u'v_' + k], (k, V4[k], FLAT[u'v_' + k])
assert [LIT4[u'rttvar_u'][i] - LIT4[u'rttvar_l'][i] for i in range(NSRC)] == FLAT[u'y_case_gap_rttvar']
assert [LIT4[u'srtt'][i] + LIT4[u'rttvar_u'][i] for i in range(NSRC)] == FLAT[u'y_name_family']
assert [LIT4[u'smoothed'][i] + LIT4[u'rttvar_l'][i] for i in range(NSRC)] == FLAT[u'y_name_family_l']
CITE = {}
for n in (u'1122', u'1123', u'2988', u'6298', u'9002', u'793'):
    rx = re.compile(u'RFC ?' + n + u'(?!\\d)')
    CITE[n] = [len(rx.findall(SRC[i])) for i in range(NSRC)]
    assert CITE[n] == FLAT[u'cite_' + n], (n, CITE[n], FLAT[u'cite_' + n])
SP = [sc(SRC[i], u'RFC 1122') for i in range(NSRC)]
NS_ = [sc(SRC[i], u'RFC1122') for i in range(NSRC)]
assert SP == FLAT[u'cite_1122_sp'] and NS_ == FLAT[u'cite_1122_ns']
assert [SP[i] + NS_[i] for i in range(NSRC)] == FLAT[u'cite_ns_1122']
assert [CITE[u'1122'][i] - SP[i] - NS_[i] for i in range(NSRC)] == FLAT[u'y_cite_ledger_1122'] == [0] * 4
HK = [(u'cat_std', u'Category: Standards Track'), (u'cat_exp', u'Category: Experimental'),
      (u'cat_info', u'Category: Informational'), (u'cat_hist', u'Category: Historic'),
      (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'), (u'issn_hdr', u'ISSN:'),
      (u'rfc_hdr', u'RFC Internet Engineering Task Force'), (u'braden_foot', u'Braden'),
      (u'editor_hdr', u'Editor'), (u'req_rc', u'Request for Comments:')]
for k, s in HK:
    assert [sc(SRC[i], s) for i in range(NSRC)] == FLAT[k], (k, FLAT[k])
assert [sc(SRC[i].lower(), u'obsoleted by') for i in range(NSRC)] == FLAT[u'obsoleted_by']
assert [sc(SRC[i].lower(), u'errata') for i in range(NSRC)] == FLAT[u'errata']
assert [sc(SRC[i], u'Standards Track') for i in range(NSRC)] == FLAT[u'std_lvl']
assert [sc(SRC[i], u'2119') for i in range(NSRC)] == FLAT[u'rfc2119_ref']
assert [sc(SRC[i], u'key words') + sc(SRC[i], u'Key words') for i in range(NSRC)] == FLAT[u'key_words_boiler']

# ---- ⑨壳账三式 + 编码层 ----
HD_SP = re.compile(u'^RFC \\d{4}(?!\\d) +(\\S.*)$')
HD_NS = re.compile(u'^RFC(\\d{4})(?!\\d)(?: |$)')
FO_BR = re.compile(u'\\[Page (\\d+)\\]$')
FO_OLD = re.compile(u'(?:[ \\t]|^)Page (\\d+)$')


def is_sp(l):
    m = HD_SP.match(l)
    return bool(m) and m.group(1).strip() != u''


def is_ns(l):
    return bool(HD_NS.match(l))


H_SP = [len([l for l in LST[i] if is_sp(l)]) for i in range(NSRC)]
H_NS = [len([l for l in LST[i] if is_ns(l) and not is_sp(l)]) for i in range(NSRC)]
H_ALL = [len([l for l in LST[i] if is_sp(l) or is_ns(l)]) for i in range(NSRC)]
assert H_SP == FLAT[u'hdr_sp'] and H_NS == FLAT[u'hdr_ns'] and H_ALL == FLAT[u'hdr']
assert [H_SP[i] + H_NS[i] - H_ALL[i] for i in range(NSRC)] == FLAT[u'hdr_ledger'] == [0] * 4
assert sum(FLAT[u'hdr_ledger']) == FLAT[u'hdr_ledger_sum'] == 0


def is_br(l):
    s = l.strip()
    m = FO_BR.search(s)
    return bool(m) and s.endswith(u']')


F_BR = [len([l for l in LST[i] if is_br(l)]) for i in range(NSRC)]
F_OLD = [len([l for l in LST[i] if FO_OLD.search(l.strip()) and not is_br(l)]) for i in range(NSRC)]
F_ALL = [F_BR[i] + F_OLD[i] for i in range(NSRC)]
F_IE = [len([l for l in LST[i] if is_br(l) and l.strip().startswith(u'Internet Engineering Task Force')])
        for i in range(NSRC)]
assert F_ALL == FLAT[u'foot'] and F_BR == FLAT[u'foot_brk'] and F_OLD == FLAT[u'foot_old'] == [0] * 4
assert F_IE == FLAT[u'foot_ietf']
FF = [len([1 for ch in SRC[i] if ch == u'\x0c']) for i in range(NSRC)]
assert FF == FLAT[u'formfeed'] == F_ALL
assert sum(FF[i] - F_ALL[i] for i in range(NSRC)) == FLAT[u'ff_foot_sum'] == 0
assert [F_IE[i] - FF[i] for i in range(NSRC)] == FLAT[u'ietf_vs_ff'] and sum(FLAT[u'ietf_vs_ff']) == FLAT[u'ietf_vs_ff_sum'] == -19
TR = [len([l for l in LST[i] if l != l.rstrip()]) for i in range(NSRC)]
assert TR == FLAT[u'trail'] and sum(TR[i] - F_ALL[i] for i in range(NSRC)) == FLAT[u'trail_foot_sum'] == 0
assert [H_ALL[i] + F_ALL[i] for i in range(NSRC)] == FLAT[u'pagelines']
assert [FF[i] if FF[i] else max(H_ALL[i], F_ALL[i]) for i in range(NSRC)] == FLAT[u'pages_est']
SELF = sc(SRC[0], u'1122')
RCS = sc(SRC[0], u'Request for Comments: 1122')
assert SELF == FLAT[u'a_self_lit'] == 116 and RCS == FLAT[u'a_shell_1122_sp'] == 1
assert SELF - H_NS[0] - RCS == FLAT[u'a_1122_resid'] == 0
BYT = [len(x) for x in RB]
CHR = [len(t) for t in SRC]
assert BYT == FLAT[u'bytes'] and CHR == FLAT[u'chars'] == [len(x) for x in SRC]
assert [len(t.replace(NL, u'')) for t in SRC] == FLAT[u'chars_no_nl']
assert [t.count(NL) + 1 for t in SRC] == FLAT[u'lines'] == [len(x) for x in LST]
assert [len([l for l in LST[i] if l.strip()]) for i in range(NSRC)] == FLAT[u'nonblank']
assert [max(len(l) for l in LST[i]) for i in range(NSRC)] == FLAT[u'maxlen']
assert [len([ch for ch in SRC[i] if ord(ch) > 127]) for i in range(NSRC)] == FLAT[u'nonascii']
assert [len([ch for ch in RB[i].decode(u'utf-8', u'replace') if ord(ch) > 127]) for i in range(NSRC)] == FLAT[u'nonascii_raw']
assert [1 if RB[i][:3] == b'\xef\xbb\xbf' else 0 for i in range(NSRC)] == FLAT[u'bom']
assert [BYT[i] - CHR[i] for i in range(NSRC)] == [0, 0, 0, 18]
assert [t.count(u'\r') for t in SRC] == FLAT[u'cr'] == [0] * 4
SIG = [hashlib.blake2b(RB[i], digest_size=8).hexdigest() for i in range(NSRC)]
assert SIG == FLAT[u'sig'] and len(set(SIG)) == FLAT[u'sig_distinct'] == 4
NLITS = (u'RTO', u'PTO', u'3 seconds', u'1 second', u'333', u'kGranularity', u'kInitialRtt')
assert [len([l for l in LST[i] if len(l.strip()) >= 55 and any(x in l for x in NLITS)])
        for i in range(NSRC)] == FLAT[u'num_lines']

# ---- ⑩B ⇎ C 条款逐行对照 ----
FL4 = [(i, n, l) for i in range(NSRC) for n, l in enumerate(LST[i]) if u'rounded up' in l]
FB = [l for i, n, l in FL4 if i == 1]
FC = [l for i, n, l in FL4 if i == 2]
assert [len(x) for x in (FB, FC)] == FLAT[u'y_floor_lines'][1:3] and FLAT[u'y_floor_lines'] == [0, 1, 1, 0]
assert [len(FB), len(FC)] == FLAT[u'floor_pair']
assert len([1 for a, b in zip(FB, FC) if a == b]) == FLAT[u'floor_same_bytes'][0] == 1
assert len([1 for a, b in zip(FB, FC) if a != b]) == FLAT[u'floor_diff_bytes'][0] == 0
assert len([1 for a, b in zip(FB, FC) if nrm(a) == nrm(b)]) == FLAT[u'floor_same_norm'][0] == 1
AI = []
for i in (1, 2):
    hits = [n for n, l in enumerate(LST[i]) if u'Whenever RTO is computed' in l]
    AI.append(hits[-1])
PAIR4 = [(LST[1][AI[0] + k], LST[2][AI[1] + k]) for k in range(4)]
assert len(PAIR4) == FLAT[u'align_n'] == FLAT[u'y_clause_pair_n'] == 4
SB = len([1 for a, b in PAIR4 if a == b])
PO = len([1 for a, b in PAIR4 if a != b and nrm(a) == nrm(b)])
ND = len([1 for a, b in PAIR4 if nrm(a) != nrm(b)])
assert (SB, PO, ND) == (FLAT[u'align_same_bytes'], FLAT[u'align_punct_only'], FLAT[u'align_norm_diff']) == (3, 1, 0)
assert SB + PO + ND - 4 == FLAT[u'align_close'] == 0
assert sum(len(b) - len(a) for a, b in PAIR4) == FLAT[u'align_char_delta'] == 1
assert len([1 for a, b in PAIR4 if b.count(u',') - a.count(u',') == 1]) == FLAT[u'align_comma'] == 1

# ---- ⑪搬运账: re.sub 归一 + 集合运算符, 含壳 ⇎ 去壳两面 ----
GE, GEN, GERAW = [], [], []
for store, shell in ((GE, True), (GEN, False)):
    for i in range(NSRC):
        s = {}
        for l in LST[i]:
            if not shell and (is_sp(l) or is_ns(l) or is_br(l) or FO_OLD.search(l.strip())):
                continue
            n = nrm(l)
            if len(l.strip()) >= 40 and len(n) >= 40:
                s[n] = 1
        store.append(s)
RAWSET = []
for i in range(NSRC):
    s = {}
    for l in LST[i]:
        if len(l.strip()) >= 40 and len(nrm(l)) >= 40:
            s[l] = 1
    RAWSET.append(s)
assert [len(x) for x in GE] == FLAT[u'lines_ge40'] and [len(x) for x in GEN] == FLAT[u'lines_ge40_nos']
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
BCI = PAIR[(1, 2)]
TRI = sum(1 for k in GE[0] if k in GE[1] and k in GE[2])
assert BCI == FLAT[u'BC_inter'] == 95 and TRI == FLAT[u'ABC_inter'] == 0
# only_* 按建条目侧分组: B 只比 A、C 三份, D 比前三份
GRP = {1: (0, 2), 2: (0, 1, 3), 3: (0, 1, 2)}
ONLY = {}
for i, g in GRP.items():
    ONLY[i] = len(KS(GE[i]) - set().union(*[KS(GE[j]) for j in g]))
    assert ONLY[i] == FLAT[u'only_' + TAGS[i].lower()], (i, ONLY[i], FLAT[u'only_' + TAGS[i].lower()])
    assert len(KS(GEN[i]) - set().union(*[KS(GEN[j]) for j in g])) == FLAT[u'only_' + TAGS[i].lower() + u'_nos']
BCPD = sum(1 for k in GE[1] if k in GE[2] and k in GE[3])
BCAD = sum(1 for k in GE[1] if k in GE[2] and k in GE[0] and k not in GE[3])
assert BCPD + BCAD - 0 == FLAT[u'share_bc_plus'] == 1
U3, U4S = union4(GE[0], GE[1], GE[2]), union4(*GE)
assert U3 == FLAT[u'union_abc'] and U4S == FLAT[u'union_abcd'] and U4S - U3 == FLAT[u'union_delta'] == ONLY[3]
assert len(KS(GEN[0]) | KS(GEN[1]) | KS(GEN[2]) | KS(GEN[3])) == FLAT[u'union_abcd_nos']
assert len(KS(GEN[0]) | KS(GEN[1]) | KS(GEN[2])) == FLAT[u'union_abc_nos']
T_ABC = sum(1 for k in GE[0] if k in GE[1] and k in GE[3])
T_ABD, T_ACD = T_ABC, sum(1 for k in GE[0] if k in GE[2] and k in GE[3])
T_BCD = BCPD
INCL = (sum(len(x) for x in GE) - sum(PAIR.values()) + T_ABC + T_ABD + T_ACD + T_BCD
        - sum(1 for k in GE[0] if k in GE[1] and k in GE[2] and k in GE[3]))
assert INCL == FLAT[u'abcd_incl'] == U4S and INCL - U4S == FLAT[u'abcd_close'] == 0
BS = inter4(RAWSET[1], RAWSET[2])
assert BS == FLAT[u'y_bc_byte_shared'] == 84 and PAIR[(1, 2)] - BS == FLAT[u'y_bc_norm_only'] == 11
assert sum(ONLY[i] for i in GRP) == FLAT[u'y_only_bcd'] == 1088
RULE_LINE = LST[0][max([n for n, l in enumerate(LST[0]) if RULE[u'A'] in l])]
assert RULE_LINE == FLAT[u'y_a_rule_line']
assert [len([1 for l in LST[i] if nrm(RULE_LINE) in nrm(l)]) for i in (1, 2, 3)] == FLAT[u'y_a_rule_in_bc'] == [0, 0, 0]
FANS = [nrm(t) for t in SRC]
SPECIAL = (u'RTO', u'PTO', u'3 seconds', u'1 second', u'333', u'SRTT', u'RTTVAR', u'kGranularity',
           u'kInitialRtt', u'Jacobson', u'Karn', u'backing off', u'initial RTO', u'rounded up',
           u'milliseconds', u'smoothed_rtt')
POOLC = {}
for i in range(NSRC):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        n = nrm(l)
        if n:
            POOLC[(TAGS[i], l)] = sum(1 for k in range(NSRC) if n in FANS[k])
TIERS = [len([v for v in POOLC.values() if v == n]) for n in range(1, NSRC + 1)]
assert len(POOLC) == FLAT[u'pool_n'] == 6248 and TIERS == FLAT[u'pool_tiers'] == [5758, 399, 35, 56]
assert sum(TIERS) - len(POOLC) == FLAT[u'pool_close'] == 0
assert [len([k for k in POOLC if k[0] == t]) for t in TAGS] == FLAT[u'pool_tag_n']
assert max(len(k[1]) for k in POOLC) == FLAT[u'pool_maxlen'] == 73

# ---- ⑫恒等式(本注独立算) ⇎ 闭合账重导 ----
IDENTS = [MAXA == RATIO * MINA + REM, PTO_EX == THREE * ANS_MS[3],
          FLAT[u'y_d_claim_ms'] == PTO_EX + FLAT[u'y_d_gap_exact'],
          FLAT[u'y_d_claim_ms'] == PTO_IN + FLAT[u'y_d_gap_int'],
          PTO_EX - PTO_IN == FLAT[u'y_d_gap_int'] - FLAT[u'y_d_gap_exact'],
          ANS_MS[3] == 2 * VAR_I + VAR_F, K_D == K_BC[2] == K_BC[1],
          HALF[0] == HALF[1] == HALF[2], FLOOR[1][0] == FLOOR[2][0] == ANS_MS[2],
          ANS_MS[1] - FLOOR[1][0] == FLAT[u'y_b_floor_gap'] == 2000,
          REVERT[0] == ANS_MS[0] == ANS_MS[1], CAP_A[0] == CR * REF + CREM,
          LO == GRAN[0] and HI == CAP_A[0], SELF == H_NS[0] + RCS,
          BCAD == TRI, INCL == U4S, U4S == U3 + ONLY[3], H_SP[0] + H_NS[0] == H_ALL[0],
          FF == F_ALL == TR, SB + PO + ND == 4, len(set(SIG)) == NSRC, sum(TIERS) == len(POOLC),
          [sorted(set(DU[i][k][0] for k in range(len(DU[i])) if WOFF[i][0] <= DU[i][k][1] < WOFF[i][1]
                     and DU[i][k][0] > 0)) for i in range(NSRC)] == [list(x) for x in FLAT[u'y_dur_win']],
          all(max(x) == max(list(FLAT[u'y_dur_win'][i]) + list(FLAT[u'y_dur_out'][i])) for i, x in enumerate(DM)),
          all(FOLD3[k][i] >= ALONE[k][i] for k, s in SN for i in range(NSRC)),
          all(U4[u'MUST'][i] >= SECW_O[u'must'][i] for i in range(NSRC)),
          GRANSYM[0] == GRANSYM[3] == 0, len(SN) == FLAT[u'wrap_pin_n'],
          sum(WRAP_BY) == WRAP_TOTAL, max(len(x) for x in GE) == len(GE[0]),
          UOB[0] > UOB[3] and LOB[0] > LOB[3], len(CITE) == 6]
assert all(IDENTS), [n for n, x in enumerate(IDENTS) if not x]
CK = sorted([k for k in FLAT if (u'_close' in k or u'_resid' in k or u'_ledger' in k)
             and isinstance(FLAT[k], (int, float)) and not isinstance(FLAT[k], bool)])
assert CK == FLAT[u'scalar_clos_list'] and len(CK) == FLAT[u'scalar_clos_n'] == 15
assert sum(FLAT[k] for k in CK) == FLAT[u'scalar_clos_sum'] == 0
assert len([k for k in FLAT if (u'_close' in k or u'_ledger' in k) and isinstance(FLAT[k], list)]) == FLAT[u'list_clos_n']
assert FLAT[u'x_ident_n'] == 30 and len(DER) == CH[u'deriv_keys']

# ---- ⑬锚归属: 流式拼面定档 ⇎ 逐行两档对拍, 再求最小行跨度 ----
TT = io.open(ENTRY, encoding=u'utf-8').read()
enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
DIS4 = []
for _, a in CITES:
    if a not in DIS4:
        DIS4.append(a)
LINEF = []
for i in range(NSRC):
    one = [nrm(l) for l in LST[i]]
    two = [one[k] + one[k + 1] for k in range(len(one) - 1)]
    LINEF.append((one, two))


def hits(i, atom):
    """逐行流式拼归一面: 每批只留末尾 len(锚)-1 字符续接, 命中数与整篇归一口径相同, 但不现造整篇面。"""
    n = nrm(atom)
    if not n:
        return 0
    buf, c, keep = u'', 0, len(n) - 1
    for l in LST[i]:
        buf += nrm(l)
        p = buf.find(n)
        while p >= 0:
            c += 1
            p = buf.find(n, p + len(n))
        buf = buf[-keep:] if keep else u''
    return c


def where(atom):
    return tuple(i for i in range(NSRC) if hits(i, atom) > 0)


def where_line(atom):
    n = nrm(atom)
    return tuple(i for i in range(NSRC) if n and (n in LINEF[i][0] or any(n in p for p in LINEF[i][1])))


def span(atom, i):
    """这枚锚最少压在源 i 的几行上(1..5); 落在空行上也占一格。"""
    n = nrm(atom)
    if not n:
        return 0
    P = LINEF[i][0]
    for k in range(1, 6):
        s = u''.join(P[:k])
        if n in s:
            return k
        for j in range(k, len(P)):
            s = (s + P[j])[len(P[j - k]):]
            if n in s:
                return k
    return 0


HC4 = [where(a) for a in DIS4]
HCL = [where_line(a) for a in DIS4]
SPX = [(a, [span(a, i) for i in m]) for a, m in zip(DIS4, HC4) if m]
THR = len([x for x in SPX if max(x[1]) >= 3])
DIFF = len([x for x in SPX if len(set(x[1])) > 1])
MAXSP = max([max(x[1]) for x in SPX])
ERR4 = [x for x in CITES if not nrm(x[1]) or len(where(x[1])) == 0]
SIN = len([h for h in HC4 if len(h) == 1])
CRS = len([h for h in HC4 if 1 < len(h) < NSRC])
ALL4 = len([h for h in HC4 if len(h) == NSRC])
assert not ERR4, ERR4[:3]
assert HCL == HC4, [x for x, y in zip(DIS4, [m != q for m, q in zip(HC4, HCL)]) if y][:2]
assert THR == 0 and MAXSP == 2 and DIFF == len([x for x in SPX if max(x[1]) >= 2]) == 2
assert SIN == FLAT[u'anchor_single'] and CRS == FLAT[u'anchor_cross'] and ALL4 == FLAT[u'anchor_all4'] == 0
assert len(CITES) == FLAT[u'anchor_total'] and len(DIS4) == FLAT[u'anchor_distinct']
assert [len(re.findall(u'⟦%s⟧' % t, enc)) for t in TAGS] == [FLAT[u'tag_' + t] for t in TAGS]
assert len(re.findall(u'⟨', enc)) == len(CITES) == sum(FLAT[u'tag_' + t] for t in TAGS)

# ---- ⑭采集侧对账(本注只做逐键比, 不改定义) ----
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

# ---- 判词用的三枚反向对照: 改一个比较符就会塌的量 ----
assert FLAT[u'lit_3seconds'][3] == 0 and FLAT[u'lit_1second'][0] == 0
assert FLAT[u'secw_3seconds'][:3] == [1, 1, 1] and FLAT[u'outw_3seconds'][2] == 8
assert FLAT[u'y_sum_var_first'] == [0, 0, 0, 1] and FLAT[u'y_sum_tail_n'] == [0, 0, 0, 1]
assert FLAT[u'y_klit_close'] == [0, 0, 0, 0] and FLAT[u'lit_4xrttvar'][:3] == [0, 0, 0]

L = []
A = L.append
A(u'### 第四遍复测(本注现算, 与前三遍不同路)')
A(u'')
A(u'| 量 | 本注的写法 | 结果 | 与建条目侧 |')
A(u'|---|---|---|---|')
A(u'| 答数行 | 在各自的答题针(“%s”⇎“%s”⇎“%s”⇎“%s”)之后搜第一枚 数字+空白+单位词 token 并归一到毫秒 | '
  u'数字串 %s ⇎ 单位词 %s ⇎ 毫秒 %s ⇎ 跨行 %s | 与 y_ans_ms ⇎ y_ans_num ⇎ y_ans_unit ⇎ y_ans_wrap 逐档一致(四枚答数无一跨行); '
  u'最大⇎最小 %d⇎%d=%d 倍余 %d, 三个不同答数 |'
  % (ANSN[u'A'].strip(), ANSN[u'B'].strip(), ANSN[u'C'].strip(), ANSN[u'D'].strip(),
     J([x[1] for x in ANS]), u' ⇎ '.join(u'⟨%s⟩' % x[2] for x in ANS), J(ANS_MS), J([x[3] for x in ANS]),
     MAXA, MINA, RATIO, REM))
A(u'| 和式结构 | 行首 (RTO⇎PTO) 与 <-/= 正则配对, 右侧按“+ 左侧括号净深为 0”切列, max 档按首枚逗号拆两参数、乘积档按首个 * 拆系数 | '
  u'解出行数 %s ⇎ 形状 %s ⇎ 项数 %s ⇎ 首格 %s ⇎ 次格 %s ⇎ 基底 %s ⇎ 尾项 %s | 与 y_sum_n ⇎ y_sum_shape ⇎ y_sum_nterms ⇎ '
  u'y_sum_mfirst ⇎ y_sum_msecond ⇎ y_sum_base ⇎ y_sum_tail 一致; 乘积项占首格的位数 %s(只有 21 为 1), 赋值符两式 %s ⇎ 差 %s |'
  % (J(SN_), u' ⇎ '.join(u'⟨%s⟩' % x for x in SHAPE), J([g[0][2] if g else 0 for g in SUMS]),
     u' ⇎ '.join(u'⟨%s⟩' % (x or u'—') for x in [g[0][3] if g else u'' for g in SUMS]),
     u' ⇎ '.join(u'⟨%s⟩' % (x or u'—') for x in [g[0][4] if g else u'' for g in SUMS]),
     u' ⇎ '.join(u'⟨%s⟩' % (x or u'—') for x in [g[0][7] if g else u'' for g in SUMS]),
     u' ⇎ '.join(u'⟨%s⟩' % (x or u'无') for x in [g[0][8] if g else u'' for g in SUMS]),
     J(FLAT[u'y_sum_var_first']), J(FLAT[u'assign_forms']), J(FLAT[u'assign_gap'])))
A(u'| 面内常数 | 正向正则取针后数字(K ⇎ R/ ⇎ / ⇎ 6.2.2 is), 反向正则取针前数字(*rttvar ⇎ *MSL, i.e., 240), 上限/地板/回退三行各用同一个时长搜索器 | '
  u'K %s ⇎ 半值分母 %s ⇎ 粒度 %s%s ⇎ kInitialRtt %d ⇎ A 的倍数 %d ⇎ 上限 %d ⇎ B/C 的地板 %s ⇎ C 的回退 %d | '
  u'与 y_bc_kdef ⇎ y_d_k ⇎ y_half_* ⇎ y_d_gran ⇎ y_d_kinit ⇎ y_a_mult ⇎ y_a_cap_ms ⇎ y_floor_ms ⇎ y_c_revert_ms 一致, '
  u'废止者与被废止者的 K 现读彼此闭合 %d |'
  % (J(K_BC), J(HALF), GRAN[0], GRAN[2], KINIT, MULT_A, CAP_A[0], J([x[0] for x in FLOOR]), REVERT[0],
     FLAT[u'y_b_kdef_close']))
A(u'| 宣称⇎复算 | 由本注现读的 333⇎4⇎1 三枚常数复算 PTO 两档(先乘后除 ⇎ 方差先取整), 再与面内“starting with a PTO of”之后的宣称对差 | '
  u'实数档 %d ⇎ 取整档 %d ⇎ 宣称 %d ⇎ 差 %d⇎%d 毫秒 ⇎ 两取法之差 %d | 与 y_d_pto_exact ⇎ y_d_pto_int ⇎ y_d_claim_ms ⇎ '
  u'y_d_gap_* ⇎ y_d_pto_spread 一致; 333 为奇数(半值 %d 余 %d), 库里没有一行写着 999 或 997 |'
  % (PTO_EX, PTO_IN, CLM[3], FLAT[u'y_d_gap_exact'], FLAT[u'y_d_gap_int'], PTO_EX - PTO_IN, VAR_I, VAR_F))
A(u'| 规范窗 | 全篇编号标题一次收表(正则), 规范句最后一处命中二分定位, 收口按“同题 ⇎ 首 token 前缀”两条否判; 窗长逐行相加再减一 | '
  u'窗 %s ⇎ 窗长 %s ⇎ 编号 %s ⇎ 窗内子条目 %s | 与 sec_w ⇎ sec_a ⇎ sec_b ⇎ sec_len ⇎ sec_num ⇎ sec_sub ⇎ sec_hit ⇎ sec_off_* 一致'
  u'(建条目侧是就地逐字符回溯, 本注是表+二分; 编号串按建条目侧的点号档回写) |'
  % (J([u'%d–%d' % w for w in WIN]), J(WLEN), J(WNUM), J(FLAT[u'sec_sub'])))
A(u'| 时长族 | 一条正则收非重叠 token(单位族长名先试, 后不接字母), 归一乘数表同; 跨行标志查 group(2), 割裂标志查 start 前两根字符 | '
  u'枚数 %s ⇎ 去重值 %s ⇎ 值域 %d–%d ⇎ 小数割裂 %s(仅 %s) ⇎ 零值 %s ⇎ 单位族 %s | '
  u'与 durlit ⇎ durms_* ⇎ dur_ms_lo/hi ⇎ y_dur_frac(_vals/_only) ⇎ y_dur_zero ⇎ y_unit_used 逐键一致; 上限 %d=窗内 %d 的 %d 倍余 %d |'
  % (J(FLAT[u'durlit']), u' ⇎ '.join(u'[%s]' % (u','.join(str(y) for y in x)) for x in DM), LO, HI,
     J(DF), u' ⇎ '.join(u'[%s]' % (u','.join(str(y) for y in x)) for x in FV), J(FLAT[u'y_dur_zero']),
     u' ⇎ '.join(u'[%s]' % (u' '.join(x)) for x in UU), HI, REF, CR, CREM))
A(u'| 窗内外分档 | 对每枚针取全部起点位置(re.finditer), 再按窗区间切两半——窗外是位置集合的补, 不是总数减窗内 | '
  u'“3 seconds” 窗内 %s ⇎ 窗外 %s; “1 second” 窗内 %s ⇎ 窗外 %s; kGranularity 窗内 %s ⇎ 窗外 %s | '
  u'与 secw_/outw_ ⇎ y_secw_/y_outw_ 逐键一致, 两份相加恒等于全篇字面 %s ⇎ %s ⇎ %s |'
  % (J(FLAT[u'secw_3seconds']), J(FLAT[u'outw_3seconds']), J(FLAT[u'secw_1second']), J(FLAT[u'outw_1second']),
     J(FLAT[u'secw_kgran']), J(FLAT[u'outw_kgran']),
     J(FLAT[u'lit_3seconds']), J(FLAT[u'lit_1second']), J(FLAT[u'lit_kgran'])))
A(u'| 字面⇎折行 | 字面档 split 计数; 折行不折全篇: 逐行 token 化后接成一面再 split, 减逐行各自 split 的和 | '
  u'%d 枚字面针全数对上; %d 枚折行针里 %d 枚被排版折断, 合计 %d 处——唯一的断口在 B 的三秒句尾 “though the ⇎ \"backing off\" on repeated”'
  u'(同一句在 C 压在一行里: 原面 %s ⇎ 折面 %s) | '
  u'与 lit_* ⇎ s_* ⇎ s_*_fold ⇎ wrap_gap_* ⇎ wrap_gap_total ⇎ wrap_pin_hit 一致; 答数针 \"RTO = \" 只在 89 出现 %s 处 |'
  % (len(LIT4), len(SN), WRAP_HIT, WRAP_TOTAL, J(ALONE[u'backoff5']), J(FOLD3[u'backoff5']), J(LIT4[u'rtovalue'])))
A(u'| 义务词两档 ⇎ 窗内 | 全大写族 split 计数(故 MUST 一档含 "MUST NOT" 内的), 小写族 [A-Za-z0-9_]+ 词流整词相等; 窗内改按位置切 | '
  u'MUST %s ⇎ SHOULD %s ⇎ MAY %s ⇎ MUST NOT %s ⇎ 三词合计 %s; must %s ⇎ should %s ⇎ may %s ⇎ 合计 %s ⇎ 窗内合计 %s | '
  u'与 u_/l_/oblig_up ⇎ oblig_low ⇎ y_oblig_win 一致 |'
  % (J(U4[u'MUST']), J(U4[u'SHOULD']), J(U4[u'MAY']), J(U4[u'MUST NOT']), J(UOB),
     J(FLAT[u'l_must']), J(FLAT[u'l_should']), J(FLAT[u'l_may']), J(LOB), J(FLAT[u'y_oblig_win'])))
A(u'| 壳账三式 | 页眉 ^RFC \\d{4} 带题文 ⇎ ^RFC\\d{4} 不带空格两档各立键再与并档对账; 页脚 \\[Page n\\]$ ⇎ 旧式 Page n$ 两档, 机构名页脚按行首字串; '
  u'换页符逐字符计、行尾空格按行与 rstrip 比较 | '
  u'页眉 %s(带空格 %s ⇎ 无空格 %s, 账 %s) ⇎ 页脚 %s(方括号 %s ⇎ 旧式 %s ⇎ 左侧机构名 %s) ⇎ 换页 %s ⇎ 行尾空格 %s ⇎ 版面行 %s ⇎ 估计页 %s | '
  u'与 hdr/hdr_sp/hdr_ns ⇎ hdr_ledger_sum ⇎ foot/foot_brk/foot_old/foot_ietf ⇎ formfeed ⇎ trail ⇎ pagelines ⇎ pages_est 一致; '
  u'89 的“1122”字面 %d 处 = 页眉 %d + 抬头 %d(残差 %d) |'
  % (J(H_ALL), J(H_SP), J(H_NS), FLAT[u'hdr_ledger_sum'], J(F_ALL), J(F_BR), J(F_OLD), J(F_IE), J(FF), J(TR),
     J(FLAT[u'pagelines']), J(FLAT[u'pages_est']), SELF, H_NS[0], RCS, FLAT[u'a_1122_resid']))
A(u'| 语汇⇎引用⇎身份 | 字面 split 计数; 引用号逐枚编号各配一条 RFC ?n(?!\\d) 收 findall 长度(793 只有三位, 一位正则收不全四位数族); 黏合两式另立键对账 | '
  u'RTO %s ⇎ PTO %s ⇎ RTT %s ⇎ rtt %s ⇎ granularity %s; 1122 %s ⇎ 2988 %s ⇎ 6298 %s(带空格 %s ⇎ 黏写 %s, 账 %s) | '
  u'与 v_* ⇎ cite_* ⇎ cite_1122_sp ⇎ cite_1122_ns ⇎ y_cite_ledger_1122 ⇎ cat_/obs_/upd_/issn_ 一致; 大写 RTTVAR ⇎ 小写 rttvar 之差 %s |'
  % (J(V4[u'rto']), J(V4[u'pto']), J(V4[u'rtt']), J(V4[u'rtt_low']), J(V4[u'gran']),
     J(CITE[u'1122']), J(CITE[u'2988']), J(CITE[u'6298']), J(SP), J(NS_), J(FLAT[u'y_cite_ledger_1122']),
     J(FLAT[u'y_case_gap_rttvar'])))
A(u'| B⇎C 条款对照 | (2.4) 行号由“最后一处 Whenever RTO is computed”现推, 四行配对后逐字节 ⇎ 归一 ⇎ 长度差 ⇎ 逗号差四档; 地板行另按 '
  u'“rounded up”行的行集比对 | 配对 %d 行 ⇎ 逐字节同 %d ⇎ 只差标点 %d ⇎ 归一也不同 %d ⇎ 字符增减 %+d ⇎ 多一枚逗号 %d 行 ⇎ 闭合 %d | '
  u'与 align_* ⇎ floor_* ⇎ y_floor_lines 一致(废止链上的改动在字面是一枚逗号) |'
  % (len(PAIR4), SB, PO, ND, FLAT[u'align_char_delta'], FLAT[u'align_comma'], FLAT[u'align_close']))
A(u'| 整行搬运 | 归一 re.sub 去非 a-z0-9; 交按“小表建字典、大表逐条查字典”再与集合运算符 & 对拍, 并集按单个计数字典 add; '
  u'only_* 按建条目侧分组(B 比 A、C, D 比前三份); 字节档另按原行串求交 | '
  u'B⇎C %d ⇎ B⇎D %d ⇎ C⇎D %d ⇎ A⇎B⇎C %d ⇎ B∩C∩D 加 B∩C∩A %d ⇎ 并集(三份 %d／四份 %d) ⇎ 容斥−并集 %d; '
  u'只在本份 B %d ⇎ C %d ⇎ D %d ⇎ 合计 %d; 字节档同现 %d ⇎ 只在归一档相同 %d | '
  u'与 share_/BC_inter ⇎ ABC_inter ⇎ share_bc_plus ⇎ union_/only_/abcd_incl ⇎ abcd_close ⇎ y_only_bcd ⇎ y_bc_* 一致; '
  u'去壳两面各算一遍(壳差 %s) |'
  % (PAIR[(1, 2)], PAIR[(1, 3)], PAIR[(2, 3)], TRI, FLAT[u'share_bc_plus'], U3, U4S, INCL - U4S,
     ONLY[1], ONLY[2], ONLY[3], FLAT[u'y_only_bcd'], BS, FLAT[u'y_bc_norm_only'],
     J(FLAT[u'shell_delta'])))
A(u'| 锚池⇎序列化 | 池按“整篇归一串含这条锚的份数”分四档(成员判据仍用整篇归一, 与下面锚归属的行档不同口径); 序列化按 len(rb) ⇎ 解码长度 ⇎ 去换行 ⇎ BOM 前三字节 ⇎ 非 ASCII 码点 | '
  u'池 %d 条分档 %s(逐份 %s, 闭合 %d, 最长 %d 列) ⇎ 签名 %d 种 ⇎ 字节 %s ⇎ 字符 %s ⇎ 差 %s ⇎ BOM %s ⇎ 非 ASCII %s(硬解 %s) | '
  u'与 pool_* ⇎ sig ⇎ bytes/chars/chars_no_nl/bom/nonascii(_raw) 一致; 89 体量 %d 倍于 00 而答题只占 %d 字符 |'
  % (len(POOLC), J(TIERS), J(FLAT[u'pool_tag_n']), FLAT[u'pool_close'], FLAT[u'pool_maxlen'], len(set(SIG)),
     J(BYT), J(CHR), J([BYT[i] - CHR[i] for i in range(NSRC)]), J(FLAT[u'bom']), J(FLAT[u'nonascii']),
     J(FLAT[u'nonascii_raw']), BYT[0] // BYT[1], WLEN[0]))
A(u'| 恒等式 | 本注用上面的独立读数重算 %d 组关系(3000=%d×%d+%d ⇎ %d=%d×333 ⇎ 1000−%d=%d ⇎ 1000−%d=%d ⇎ 333=2×%d+%d ⇎ '
  u'上限 %d=%d×%d+%d ⇎ 值域两端=面内粒度与面内上限 ⇎ 页眉两式=并档 ⇎ 换页=页脚=行尾空格) | 全部为真; '
  u'门槛侧登记恒等式 %d 条 ⇎ 标量闭合 %d 项(合计 %d)⇎ 清单闭合 %d 项 | 与 x_ident_n ⇎ scalar_clos_n ⇎ scalar_clos_sum ⇎ list_clos_n 一致 |'
  % (len(IDENTS), RATIO, MINA, REM, PTO_EX, THREE, PTO_EX, FLAT[u'y_d_gap_exact'], PTO_IN, FLAT[u'y_d_gap_int'],
     VAR_I, VAR_F, CAP_A[0], CR, REF, CREM, FLAT[u'x_ident_n'], FLAT[u'scalar_clos_n'], FLAT[u'scalar_clos_sum'],
     FLAT[u'list_clos_n']))
A(u'| 锚归属 | 由条目正文 ⟦标签⟧⟨引文⟩ 配对现推, 成员判据两式并行: ①逐行流式拼归一面(每批只留末尾 len(锚)−1 字符续接, 不现造整篇面) ②单行表 ⇎ 相邻两行拼接表按子串判; 两式必须给出同一归属 | '
  u'%d 处／去重 %d 串／一源 %d ⇎ 两至三源 %d ⇎ 四源 %d ⇎ 错配 %d; 行跨度 压一行 %d ⇎ 压两行 %d ⇎ 三行以上 %d(最大 %d), '
  u'同一枚锚在不同源里跨度不同的 %d 串 | 与建条目侧、门槛侧同; 压两行的两串都是同一句在 B 占一行、到 C 占两行, '
  u'而折行档那枚带 “the” 前缀的针正相反——在 B 断两行、在 C 压一行: 归属由内容定, 行数由排版定 |'
  % (len(CITES), len(DIS4), SIN, CRS, ALL4, len(ERR4),
     len([x for x in SPX if max(x[1]) == 1]), len([x for x in SPX if max(x[1]) == 2]), THR, MAXSP, DIFF))
A(u'| 两侧对账 | 采集侧 %d 键在四份面上逐键比(本注不参与其算法) | 共有 %d ／ 不符 %d | 89⇎00⇎11 是同族分页壳, 21 不分页带 BOM——两式页眉因此分开立键 |'
  % (len(MEAS), len([k for k in MEAS if k in FLAT]), len(BAD4)))
A(u'')
A(u'### 读法')
A(u'')
A(u'一、四个答数都写在能一行读完的地方, 分歧却在倍差上: 最大 %d 是最小 %d 的 %d 倍余 %d, 全列 %s 毫秒。'
  u'89 把答案放在初始化清单里——同列还写着 ⟦A⟧⟨%s⟩, 算法本体只说“须实现 Karn 与 Jacobson”, 全篇解出和式 %d 行; '
  u'00 与 11 各复写同一条和式 %d⇎%d 遍, 21 只写 %d 遍。'
  u'问“设多久”, 89 答一个数; 问“这数怎么算”, 它不给式子——同一份文档对同一格给的是两种可判性。'
  % (MAXA, MINA, RATIO, REM, J(ANS_MS),
     [l.strip() for l in LST[0] if u'(a)  RTT = 0' in l][0], SN_[0], SN_[1], SN_[2], SN_[3]))
A(u'二、3 秒在 11 里没有消失, 只是搬了位置: 答题句换成 %d 毫秒(%s), 而 “3 seconds” 的字面反而从 89⇎00 的 %d⇎%d 处涨到 %d 处——'
  u'其中窗内 %d 处、窗外 %d 处, 搬家落在 (5.7) 的 SYN 回退 MUST 里 ⟦C⟧⟨%s⟩(现读 %d 毫秒, 与 89⇎00 的答数各自闭合 %d⇎%d)。'
  u'它另留两句退路: “前一版用 3 秒, 实现 MAY 仍用” %d 处(00 里 %d 处)与附录 A “Rationale for Lowering the Initial RTO” %d 处。'
  % (ANS_MS[2], u' ⇎ '.join(u'⟨%s⟩' % x for x in [ANS[2][1] + u' ' + ANS[2][2]]),
          LIT4[u'3seconds'][0], LIT4[u'3seconds'][1], LIT4[u'3seconds'][2],
          FLAT[u'secw_3seconds'][2], FLAT[u'outw_3seconds'][2],
          [l.strip() for l in LST[2] if LITK[u'revert'] in l][0][:44].rsplit(u' ', 1)[0], REVERT[0],
          FLAT[u'y_c_revert_eq_a'], FLAT[u'y_c_revert_eq_b'],
          FLAT[u'y_c_may_still'], FLAT[u'y_b_may_still'], FLAT[u'y_c_lower_note']))
A(u'三、21 把“答多久”改成“答初始 RTT”: 面内现读 ⟨%s⟩ %s, 由它自己的 %d⇎%d⇎%d 三枚常数复算 PTO=%d(实数档)⇎%d(方差先取整档), '
  u'而文书宣称 ⟦D⟧⟨%s⟩——宣称与算法差 %d⇎%d 毫秒, 21 面内把 999 或 997 与 PTO 写在同一行的 %d 行(“1 second” 字面 %d 处全是散文那处宣称与 11 的规则)。'
  u'奇数是成因: 333=2×%d+%d, 方差半值必然丢 1 毫秒; 取大档两参数还换了序(乘积占首格 %d), 尾项 max_ack_delay 只在 21 有(份数 %d), '
  u'而它在 Initial/Handshake 空间又被置零 ⟦D⟧⟨%s⟩。'
  % (ANS[3][1], ANS[3][2], ANS_MS[3], K_D, GRAN[0], PTO_EX, PTO_IN,
          [l.strip() for l in LST[3] if LITK[u'onesecclaim'] in l][0][:52].rsplit(u' ', 1)[0],
          FLAT[u'y_d_gap_exact'], FLAT[u'y_d_gap_int'],
          len([1 for l in LST[3] if u'PTO' in l and (u'999' in l or u'997' in l)]), LIT4[u'1second'][3], VAR_I, VAR_F,
          FLAT[u'y_sum_var_first'][3], FLAT[u'y_sum_tail_n'][3],
          [l.strip() for l in LST[3] if u'max_ack_delay in the PTO' in l][0][:48].rsplit(u' ', 1)[0]))
A(u'四、废止链上的改动可以小到一枚逗号: 00 与 11 的 (2.4)–(2.7) 四行配对, 逐字节相同 %d 行、只差标点 %d 行(多一枚逗号 %d 行、净增 %d 字符), '
  u'同一条地板上取整两份各现读 %d 毫秒(闭合 %d), 而 00 的地板比自己给新建连接的答数低 %d 毫秒; '
  u'11 的地板恰等于自己的答数(闭合 %d)——数字没动, 动的是它管住谁。K 的定义值两份都是 %d, 与 21 写死的 %d 闭合 %d: 换代只把符号落成字面。'
  % (SB, PO, FLAT[u'align_comma'], FLAT[u'align_char_delta'], FLOOR[1][0], FLAT[u'y_bc_floor_close'],
          FLAT[u'y_b_floor_gap'], FLAT[u'y_c_floor_eq_init'], K_BC[1], K_D, FLAT[u'y_k_close']))
A(u'五、壳在这里比内容更能骗人: 89 每页重印“RFC1122”式无空格页眉 %d 行 ⇎ 带空格式 %d 行, 而 00/11 只有后者(%d⇎%d 行)——'
  u'页眉两式必须分开立键, 否则“这份文档被引了几次自己的号”会答成 %d(“1122” 字面), 而其中 %d 行是每页重印的自家无空格页眉, 后两份真引它的合计只有 %d 处; '
  u'00/11 的页脚⇎换页符⇎行尾空格三本账逐份相等(%d⇎%d⇎%d 与 %d⇎%d⇎%d), 唯独机构名页脚减换页符 %s(合计 %d)——只有 89 每页重印机构名。'
  u'词频的另一条隐形通道在排版: 本注按拼行面数出的跨行 %d 处全落在 00 的 the "backing off" on repeated(原面 %d 处 ⇎ 折面 %d 处), '
  u'其余 %d 枚针皆 0; 21 三者全 0(不分页、带 BOM %d 份、非 ASCII %d 枚)。'
  % (H_NS[0], H_SP[0], H_SP[1], H_SP[2], SELF, H_NS[0], sum(CITE[u'1122'][1:]),
     F_ALL[1], FF[1], TR[1], F_ALL[2], FF[2], TR[2], J(FLAT[u'ietf_vs_ff']), FLAT[u'ietf_vs_ff_sum'],
     WRAP_TOTAL, ALONE[u'backoff5'][1], FOLD3[u'backoff5'][1], len(SN) - WRAP_HIT,
     FLAT[u'bom'][3], FLAT[u'nonascii'][3]))
A(u'')
A(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
A(u'')
A(u'① 四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; ② rfc-editor.org 此刻给这四份挂的类目与状态页——库内抬头只印 '
  u'Category: Standards Track %d⇎%d⇎%d⇎%d 行 ⇎ Obsoletes: %d ⇎ Updates: %d(都在 11 自己身上), 面内 “obsoleted by” 字样 %d 处, '
  u'勘误表提及 %d⇎%d⇎%d⇎%d 处只是文书自我引用; ③ 勘误是否已把 00 的 (2.1) 改成别的数; '
  u'④ 各实现里 TCP_RTO_MIN/TCP_INIT_RTT 的实际取值(21 引的 kInitialRtt=%d 与 11 引的 1 秒在部署侧各被改成的数)——属站外核验; '
  u'⑤ 现实链路 RTT 分布, 以及 21 说“333 毫秒使握手与 Initial 空间够用”这一权衡在真实网络里是否成立——文书只给结论不给测量。'
  u'这些都不进判词与门槛。'
  % (tuple(FLAT[u'cat_std']) + (FLAT[u'obs_hdr'][2], FLAT[u'upd_hdr'][2], sum(FLAT[u'obsoleted_by']))
     + tuple(FLAT[u'errata']) + (KINIT,)))
A(u'')
A(u'### 编码与门的账')
A(u'')
A(u'编码区 {0} 字符(不含换行); 锚 {1} 处 ⇎ 去重 {2} 串 ⇎ 归属检查 {3} 次 ⇎ 错配 {4}; '
  u'一源 {5} ⇎ 两至三源 {6} ⇎ 四源 {7}; 标签 A⇎B⇎C⇎D 各 {8}⇎{9}⇎{10}⇎{11} 处。'
  .format(CH[u'enc_chars'], FLAT[u'anchor_total'], FLAT[u'anchor_distinct'], FLAT[u'checks'], FLAT[u'anchor_err'],
          FLAT[u'anchor_single'], FLAT[u'anchor_cross'], FLAT[u'anchor_all4'],
          FLAT[u'tag_A'], FLAT[u'tag_B'], FLAT[u'tag_C'], FLAT[u'tag_D']))
A(u'DERIV {0} 键 ⇎ 复算点 {1} 处 ⇎ 同数共键 {2} 组 ⇎ 0 折 {3} 项; 扁平键 {4} 个; '
  u'闭合账 标量 {5} 项(合计 0)⇎ 清单 {6} 项 ⇎ 面内恒等式 {7} 条; 锚候选池 {8} 条按逐字再现份数分 4 档({9}), 分档闭合 {10}, 池中实际用作锚 {11} 条。'
  .format(CH[u'deriv_keys'], CH[u'deriv_points'], len(CH[u'collisions']), CH[u'zero_terms'],
          len(FLAT), FLAT[u'scalar_clos_n'], FLAT[u'list_clos_n'], FLAT[u'x_ident_n'],
          FLAT[u'pool_n'], u'⇎'.join(str(x) for x in FLAT[u'pool_tiers']), FLAT[u'pool_close'], CH[u'pool_used']))
A(u'门槛三遍: T1 字面逐锚回原文 ⇎ T2 DERIV 每条算式重跑 ⇎ T3 码位与字母账; '
  u'本注另加第四遍复测, 上表 17 行全部 assert, 不符即停机。')
NOTE = NL.join(L)
assert not re.findall(u'%[sdifg]|%\\(', NOTE), re.findall(u'%[sdifg]|%\\(', NOTE)[:5]
head = TT[:TT.index(u'## ⛓解读注') + len(u'## ⛓解读注')]
io.open(ENTRY, 'w', encoding=u'utf-8', newline=NL).write(head + NL + NL + NOTE + NL)
print(u'⛓解读注已写 %d 字符 ｜ 第四遍 assert 全过 ｜ 采集对账 %d 键 0 不符 ｜ 恒等式 %d 组 ｜ 字面针 %d 枚'
      % (len(NOTE), len(MEAS), len(IDENTS), len(LIT4)))
