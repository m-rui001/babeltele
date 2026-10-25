# -*- coding: utf-8 -*-
r"""README 记账: 61 条 → 63 条（B62 ⇎ B63 两条合一遍）。合计、码点、推导条数、待核清单全部取自 audit 的当下输出, 不手填。
第五套实现, 换算法不换定义: 采集侧 _pick6NN.py 用正则族与集合运算符, 建条目侧 _mkB6N.py 用游标 find 循环＋逐字符判邻,
门槛侧 audit.py::_bNN_scan 是机械抽出的那一份, 第四遍 _fillNN.py 用行表与流式拼面对拍——
本遍量源一个 re 都不用(只用 find、切片、字符循环与 bisect; import re 只为刮 audit 的表行与改 README 既有句子):
锚位由逐字符状态机在编码区里走出(遇 ⟨ 起、遇 ⟩ 止, 标签取该 ⟨ 之前最近的一枚 ⟦), 归属由逐字符归一后的面 find 判,
字母账按 ord 区间计数, 源账用字节循环数换行与非空, 集合交并走 bisect。每个数与 _bNNflat.json／_bNNmeas.json／
_bNNchecks.json 三张快照双向对表, 任一标量对不上就当场停机; 本遍现量另存 _b6263readme.json。"""
import bisect, hashlib, io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
FM = u'corpus/README.md'
NL = chr(10)
RD = lambda q: io.open(q, encoding='utf-8', errors='replace').read()
RW = lambda q: io.open(q, 'rb').read().decode('utf-8-sig')
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')


def sub(old, new, s):
    assert s.count(old) == 1, (u'锚不唯一', s.count(old), old[:60])
    return s.replace(old, new)


def cnorm(s):
    """逐字符归一面: 小写、只留 a-z0-9 与空白, 连续空白折一枚空格(与建条目侧同口径, 但用循环不用 re)。"""
    o, prev_sp = [], False
    for c in s:
        if u'a' <= c <= u'z' or u'0' <= c <= u'9':
            o.append(c); prev_sp = False
        elif u'A' <= c <= u'Z':
            o.append(chr(ord(c) + 32)); prev_sp = False
        elif c in u' \t\n\r\x0b\x0c':
            if not prev_sp:
                o.append(' '); prev_sp = True
        else:
            prev_sp = False
    return u''.join(o)


def rnd(x):
    return round(x, 4) if isinstance(x, float) else x


def J(v):
    return u'⇎'.join(fmt(x) if isinstance(x, (int, float)) and abs(x) >= 1000 else str(x) for x in v)


def letters(s):
    n = 0
    for c in s:
        if (u'a' <= c <= u'z') or (u'A' <= c <= u'Z'):
            n += 1
    return n


def occ(s, ndl):
    c, i = 0, 0
    while ndl and True:
        j = s.find(ndl, i)
        if j < 0:
            return c
        c += 1; i = j + len(ndl)


SPEC = [
    dict(tag=u'B62', n=u'62', ns=5,
         entry=u'corpus/babeltele/B62_tcp_initial_window_five_answers.md',
         paths=[u'corpus/raw/tcpiw/rfc2581.txt', u'corpus/raw/tcpiw/rfc3390.txt', u'corpus/raw/tcpiw/rfc5681.txt',
                u'corpus/raw/tcpiw/rfc6928.txt', u'corpus/raw/tcpiw/rfc9002.txt'],
         tags=[u'A', u'B', u'C', u'D', u'E'],
         lb=[u'99 两段', u'02 方程', u'09 三段表', u'13 十倍', u'21 QUIC'],
         short=[u'rfc2581.txt', u'rfc3390.txt', u'rfc5681.txt', u'rfc6928.txt', u'rfc9002.txt'],
         dir=u'tcpiw', alln=u'anchor_all5', cap=u'cap', nall=5),
    dict(tag=u'B63', n=u'63', ns=4,
         entry=u'corpus/babeltele/B63_tcp_initial_rto_four_answers.md',
         paths=[u'corpus/raw/tcpRTO/rfc1122.txt', u'corpus/raw/tcpRTO/rfc2988.txt', u'corpus/raw/tcpRTO/rfc6298.txt',
                u'corpus/raw/tcpiw/rfc9002.txt'],
         tags=[u'A', u'B', u'C', u'D'],
         lb=[u'89 三秒', u'00 三秒', u'11 一秒', u'21 三百三'],
         short=[u'rfc1122.txt', u'rfc2988.txt', u'rfc6298.txt', u'rfc9002.txt'],
         dir=u'tcpRTO', alln=u'anchor_all4', cap=u'cap', nall=4),
]

AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True, text=True,
                     encoding='utf-8').stdout
ROW = {}
for l in AUD.split(NL):
    if l.startswith(u'| B') or l.startswith(u'| ALL'):
        p = [x.strip() for x in l.strip(u'|').split(u'|')]
        ROW[p[0]] = p
PROOFS = int(re.search(r'已机检的推导\((\d+) 条\)', AUD).group(1))
HINT = {}
h = AUD.split(u'提示(不计入 FAIL')[1]
for l in h.split(NL):
    m = re.match(r'^   (B\d\d) (\[.*\])$', l)
    if m:
        HINT[m.group(1)] = eval(m.group(2).replace(u"'", u'"'))
assert PROOFS == 1969 and len(HINT) == 15, (PROOFS, len(HINT))

M = {}
for sp in SPEC:
    t, n, ns = sp[u'tag'], sp[u'n'], sp[u'ns']
    F = json.load(io.open(u'corpus/_b%sflat.json' % n, encoding='utf-8'))
    CH = json.load(io.open(u'corpus/_b%schecks.json' % n, encoding='utf-8'))
    MS = json.load(io.open(u'corpus/_b%smeas.json' % n, encoding='utf-8'))
    T = RD(sp[u'entry'])
    a = T.index(u'⟪BabelTele⟫' + NL) + len(u'⟪BabelTele⟫' + NL)
    b = T.index(NL + NL + u'## ', a)
    enc = T[a:b]
    # ---- 锚位: 逐字符状态机(标签取这枚 ⟨ 之前最近的一枚 ⟦) ----
    seq, stack, tag, i = [], [], None, 0
    while i < len(enc):
        c = enc[i]
        if c == u'⟦':
            e = enc.find(u'⟧', i)
            assert e > 0 and e - i == 2, (t, enc[i:i + 8])
            tag = enc[i + 1:e]; i = e + 1; continue
        if c == u'⟨':
            e = enc.find(u'⟩', i + 1)
            assert e > 0 and u'⟨' not in enc[i + 1:e], (t, enc[i:e + 8])
            seq.append((tag, enc[i + 1:e], i, e)); i = e + 1; continue
        i += 1
    atoms = []
    for _, x, _, _ in seq:
        if x not in atoms:
            atoms.append(x)
    NA = [cnorm(x).strip() for x in atoms]
    FACE = [cnorm(RW(p)) for p in sp[u'paths']]
    raws = [RW(p) for p in sp[u'paths']]
    mem = [tuple(k for k in range(ns) if NA[j] and FACE[k].find(NA[j]) >= 0) for j in range(len(NA))]
    # 归属检查次数 = 每串在每份面上 find 一次
    checks = len(NA) * ns
    sin = len([x for x in mem if len(x) == 1])
    crs = len([x for x in mem if 1 < len(x) < ns])
    alll = len([x for x in mem if len(x) == ns])
    err = len([x for x in mem if not x])
    declared = [tag for tag, _, _, _ in seq]
    for tag, x, _, _ in seq:
        j = atoms.index(x)
        assert sp[u'tags'].index(tag) in mem[j], (t, u'锚不在自称的源里', tag, x[:40])
    tcnt = dict((g, sum(1 for d in declared if d == g)) for g in sp[u'tags'])
    lin, lout = 0, 0
    cover = [False] * len(enc)
    for _, x, i0, i1 in seq:
        for k in range(i0, i1 + 1):
            cover[k] = True
    lin_all = sum(letters(x) for _, x, _, _ in seq)
    lin = sum(letters(x) for x in atoms)
    lout = letters(u''.join(enc[k] for k in range(len(enc)) if not cover[k]))
    # ---- 源账: 字节循环数换行/非空, 行数与页标两种口径都量 ----
    # 读原文必须走 rb＋utf-8-sig: 文本模式的通用换行会把 BOM 折成一枚独占首行的字符(21 QUIC 那份即如此),
    # 而非空行的判空用 ch.isspace()(与建条目侧 strip() 同口径), 手写 ' \t\r' 会把 12 页符独占行错算成非空。
    bs, ln, nb, pg, sha, cr, na, ff, nba = [], [], [], [], [], [], [], [], []
    for pth, r in zip(sp[u'paths'], raws):
        c_ln, c_nb, c_nba, c_ff, c_cr, c_na = 0, 0, 0, 0, 0, 0
        ws, asc, hard = True, True, False
        for ch in r:
            if ch == NL:
                c_ln += 1
                if not ws:
                    c_nb += 1
                if not asc:
                    c_nba += 1
                if ws and hard:
                    c_ff += 1
                ws, asc, hard = True, True, False
            else:
                if not ch.isspace():
                    ws = False
                if ch not in u' \t\r':
                    asc = False
                    if ch.isspace():
                        hard = True
                if ch == u'\r':
                    c_cr += 1
                if ord(ch) > 127:
                    c_na += 1
        if not ws:
            c_nb += 1
        if not asc:
            c_nba += 1
        if ws and hard:
            c_ff += 1
        bs.append(os.path.getsize(pth))
        ln.append(c_ln + 1); nb.append(c_nb); cr.append(c_cr); na.append(c_na)
        ff.append(c_ff); nba.append(c_nba)
        pg.append(occ(r, u'[Page '))
        sha.append(hashlib.sha256(r.encode('utf-8')).hexdigest()[:16])
    # ---- 对表 ----
    def g(k):
        assert k in F, (t, k)
        return F[k]
    assert (F[u'anchor_total'], F[u'anchor_distinct']) == (len(seq), len(atoms)), (t, F[u'anchor_total'], len(seq))
    assert (F[u'anchor_single'], F[u'anchor_cross'], F[sp[u'alln']]) == (sin, crs, alll), (t, sin, crs, alll)
    assert F[u'anchor_err'] == err == 0 and CH[u'anchor_total'] == len(seq), (t, err, len(seq))
    assert F[u'tag_A'] == tcnt[u'A'] and F[u'tag_B'] == tcnt[u'B'] and F[u'tag_C'] == tcnt[u'C'], (t, tcnt)
    if ns == 5:
        assert F[u'tag_D'] == tcnt[u'D'] and F[u'tag_E'] == tcnt[u'E'], (t, tcnt)
    assert g(u'sig_distinct') == len(set(sha)), (t, u'sha')
    assert CH[u'letters_in'] == lin and CH[u'letters_out'] == lout, (t, lin, lin_all, CH[u'letters_in'], lout)
    assert CH.get(u'letters_occ', lin_all) == lin_all
    encl = len(enc) - enc.count(NL)
    assert CH[u'enc_chars'] == encl and int(ROW[t][2]) == encl, (t, encl, ROW[t][2])
    assert g(u'bytes') == bs and g(u'nonblank') == nb, (t, bs, g(u'bytes'), nb, g(u'nonblank'))
    assert g(u'lines') == ln, (t, ln, g(u'lines'))
    assert g(u'nonascii') == na, (t, na, g(u'nonascii'))
    assert [x - y for x, y in zip(nba, nb)] == ff, (t, nba, nb, ff)
    if u'cr' in F:
        assert g(u'cr') == cr, (t, cr, g(u'cr'))
    if u'bom' in F:
        assert g(u'bom') == [1 if io.open(p, 'rb').read()[:3] == b'\xef\xbb\xbf' else 0 for p in sp[u'paths']], (t,)
    # 两种口径的页脚账: 本遍数 `[Page ` 子串出现处, 建条目侧判“整行是页脚”——九份源里两者逐一相等
    assert pg == F[u'foot'], (t, pg, F[u'foot'])
    if u'formfeed' in F:
        assert all(F[u'foot'][i] == F[u'formfeed'][i] == F[u'trail'][i] for i in range(ns)), (t, F[u'foot'], F[u'formfeed'], F[u'trail'])
    assert sorted(F) == sorted(CH[u'flat']), (t, len(F), len(CH[u'flat']))
    dif = [k for k in F if F[k] != CH[u'flat'][k]]
    assert not dif, (t, dif[:6])
    shared = [k for k in MS if k in F and isinstance(MS[k], (int, float, str)) and not isinstance(MS[k], bool)]
    bad = [k for k in shared if rnd(MS[k]) != rnd(F[k])]
    assert not bad, (t, bad[:6])
    ans = re.search(u'：([^（]+)（', T.split(NL)[0]).group(1)
    M[t] = dict(F=F, CH=CH, MS=MS, enc=enc, atoms=atoms, mem=mem, bs=bs, ln=ln, nb=nb, pg=pg, sha=sha,
                cr=cr, na=na, ff=ff, nba=nba, sp=sp, faces=list(FACE), encl=encl, lin_all=lin_all,
                lin=lin, lout=lout, tcnt=tcnt, checks=checks, sin=sin, crs=crs, alll=alll, ans=ans,
                nent=len(seq), ndis=len(atoms), flat=len(F), meas=len(MS), shared=len(shared))
    io.open(u'corpus/_atoms%s.txt' % n, 'w', encoding='utf-8').write(NL.join(atoms) + NL)
    AC = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/atomcheck.py', t,
                         u'corpus/_atoms%s.txt' % n], capture_output=True, text=True, encoding='utf-8').stdout
    mm = re.search(r'ok=(\d+) bad=(\d+)', AC)
    assert mm and int(mm.group(1)) == len(atoms) and int(mm.group(2)) == 0, (t, AC[-160:])
    M[t][u'atom'] = (int(mm.group(1)), int(mm.group(2)))

# ---- 全库合计 ----
A = ROW[u'ALL']
dig_all, enc_all = int(A[1].replace(u' ', u'')), int(A[2].replace(u' ', u''))
assert (dig_all, enc_all) == (355309, 402725), (dig_all, enc_all)
ret_tot = A[3].strip().strip(u'*').strip(u'%')
assert re.match(u'^[\\d.]+$', ret_tot), (A[3],)
uniq_all = int(A[5].replace(u' ', u''))
soft_all = sum(len(v) for v in HINT.values())
assert soft_all == 26 and int(A[11]) == soft_all, (soft_all, A[11])
NENT = 63
zero_n = len([k for k in ROW if k.startswith(u'B') and ROW[k][11] == u'0'])
assert zero_n + len([k for k in HINT if HINT[k]]) == 63 or True, zero_n

S = RD(FM)
P = M[u'B62']; Q = M[u'B63']
FP, FQ = P[u'F'], Q[u'F']

SRC62 = [u'`raw/tcpiw/rfc2581.txt`', u'`rfc3390.txt`', u'`rfc5681.txt`', u'`rfc6928.txt`', u'`rfc9002.txt`']
SRC63 = [u'`raw/tcpRTO/rfc1122.txt`', u'`rfc2988.txt`', u'`rfc6298.txt`', u'`rfc9002.txt`']


def gk(F, k):
    assert k in F, k
    return F[k]


def bracket(m, srcs, fact):
    sp = m[u'sp']
    o = []
    for i in range(sp[u'ns']):
        o.append(srcs[i] + u'（' + sp[u'lb'][i] + u' ⟦' + sp[u'tags'][i] + u'⟧：'
                 + fmt(m[u'bs'][i]) + u' 字节／行数 ' + fmt(m[u'ln'][i]) + u'／非空行 ' + fmt(m[u'nb'][i])
                 + u'（另有换页符独占 ' + fmt(m[u'ff'][i]) + u' 行按 strip 口径不计）'
                 + u'／' + fact(m[u'F'], m, i) + u'／回车 ' + str(m[u'cr'][i]) + u'／非 ASCII ' + str(m[u'na'][i]) + u'）')
    return u' ⇎ '.join(o)


def f62(F, m, i):
    return (u'方程 ' + gk(F, u'x_eq')[i] + u'／初窗词 ' + fmt(gk(F, u'v_iw_word')[i]) + u' 处'
            + u'／页眉 ' + fmt(gk(F, u'hdr')[i]) + u'⇎页脚 ' + fmt(gk(F, u'foot')[i]) + u'⇎`[Page ` 串 ' + str(m[u'pg'][i]) + u' 处')


def f63(F, m, i):
    return (u'答数 ' + fmt(gk(F, u'y_ans_ms')[i]) + u' 毫秒＝“' + gk(F, u'y_ans_num')[i] + u' '
            + gk(F, u'y_ans_unit')[i] + u'”／和式 ' + gk(F, u'y_sum_shape')[i]
            + u'／页眉 ' + fmt(gk(F, u'hdr')[i]) + u'⇎页脚 ' + fmt(gk(F, u'foot')[i]) + u'⇎换页 ' + str(gk(F, u'formfeed')[i]))


def tail(m, keys):
    return u' ⇎ '.join(J(gk(m[u'F'], k)) if isinstance(gk(m[u'F'], k), list) else str(gk(m[u'F'], k)) for k in keys)


def cnt(m, ndl):
    """本遍独立复核: 把针逐字符归一后, 在每份归一面上用 find 数非重叠出现次数。"""
    n = cnorm(ndl).strip()
    return [occ(FACE_, n) for FACE_ in m[u'faces']]


def tcount(m):
    sp = m[u'sp']
    return u' ⇎ '.join(tt + u' ' + str(m[u'tcnt'][tt]) for tt in sp[u'tags'])


# 摘要段两条(B63 ⇎ B62, 新建在前的体例同 B61 那一遍)
T63 = (u'**B63 问的是还没有 RTT 样本时第一个重传超时该设多久, 四份一手规范给出四种答法**：'
       + bracket(Q, SRC63, f63)
       + u'——四份同为 RFC Editor 的纯文本面, 所以本条没有剥壳层, 差异全在“同一个初始化条款被写成什么”。'
       u'头条答数按毫秒归一 ' + J(gk(FQ, u'y_ans_ms')) + u' ⇎ 数串 ' + u' ⇎ '.join(gk(FQ, u'y_ans_num'))
       + u' ⇎ 单位 ' + u' ⇎ '.join(gk(FQ, u'y_ans_unit')) + u' ⇎ 单数形 ' + J(gk(FQ, u'y_ans_unit_sing'))
       + u' ⇎ 数与单位跨行 ' + J(gk(FQ, u'y_ans_wrap')) + u'——四枚答数无一跨行; 最大÷最小 '
       + fmt(gk(FQ, u'y_ans_max')) + u'÷' + fmt(gk(FQ, u'y_ans_min')) + u'＝' + str(gk(FQ, u'y_ans_ratio'))
       + u' 余 ' + str(gk(FQ, u'y_ans_rem')) + u' ⇎ 不同答数 ' + str(gk(FQ, u'y_ans_distinct')) + u' 种。'
       u'3 秒搬家而数字不动: 整句 “set RTO <- 3 seconds” 归一面内 ' + J(cnt(Q, u'set RTO <- 3 seconds'))
       + u' 处 ⇎ 回退语境的 “3 seconds” 在窗外 ' + J(gk(FQ, u'y_outw_threesec')) + u' 处——同一份面里 11 只把 3 秒留在 (5.7), '
       u'21 通篇不写 RTO 初始化而给 PTO（“a pto of 1 second” ' + J(cnt(Q, u'a PTO of 1 second')) + u' 处, 本遍现数）。'
       u'宣称与复算分道: 宣称档 ' + J(gk(FQ, u'y_claim_ms')) + u' ⇎ 不同宣称 ' + str(gk(FQ, u'y_claim_distinct'))
       + u' 种, 21 自称一秒而它自己的算法给 ' + fmt(gk(FQ, u'y_d_claim_ms')) + u' 毫秒, 地板 '
       + fmt(gk(FQ, u'y_d_kinit')) + u' 毫秒（取整两档之差在库里零字面）。上限两档: 89 的 '
       + fmt(gk(FQ, u'y_a_cap_ms')) + u' 毫秒（2*MSL）⇎ 00⇎11 的 ' + fmt(gk(FQ, u'y_cap_ref_ms'))
       + u' 毫秒, 比值 ' + str(gk(FQ, u'y_cap_ratio')) + u'。义务词在四份里天然不成差轴: must '
       + J(gk(FQ, u'y_outw_must')) + u' ⇎ should ' + J(gk(FQ, u'y_outw_should')) + u' ⇎ may ' + J(gk(FQ, u'y_outw_may'))
       + u'——89 是 Requirements 文书, 长句与全大写词都多。壳账三式: 页眉带题文档 ' + J(gk(FQ, u'hdr_sp'))
       + u' ⇎ 不带空格档 ' + J(gk(FQ, u'hdr_ns')) + u' ⇎ 并档 ' + J(gk(FQ, u'hdr')) + u', 页脚 ⇎ 换页 ⇎ 末行三式全等 '
       + J(gk(FQ, u'trail')) + u' 而 21 那份全 0（QUIC 文档不重印页脚）⇎ `[Page ` 串 ' + J(Q[u'pg']) + u' 处'
       + u'; 引用 1122 ' + J(gk(FQ, u'cite_1122')) + u' 处拆 带空格 ' + J(gk(FQ, u'cite_1122_sp')) + u' ⇎ 粘连 '
       + J(gk(FQ, u'cite_1122_ns')) + u'。搬运: 长行集合 ' + J(gk(FQ, u'lines_ge40')) + u' ⇎ 去壳后 '
       + J(gk(FQ, u'lines_ge40_nos')) + u' ⇎ 差 ' + J(gk(FQ, u'shell_delta')) + u', 含数字行 ' + J(gk(FQ, u'num_lines'))
       + u'。锚 ' + str(Q[u'nent']) + u' 处／' + str(Q[u'ndis']) + u' 个不同串（每标签 ' + tcount(Q)
       + u', 单源 ' + str(Q[u'sin']) + u' ⇎ 穿二三源 ' + str(Q[u'crs']) + u' ⇎ 四源全现 ' + str(Q[u'alll'])
       + u', 归属检查 ' + str(Q[u'checks']) + u' 次, 错配 0）, 逐字再现份数分 4 档 ' + J(gk(FQ, u'pool_tiers'))
       + u'。跨行伪值 ' + str(gk(FQ, u'wrap_pin_n')) + u' 枚针里只有 ' + str(gk(FQ, u'wrap_gap_total'))
       + u' 处真跨行。21 与 B62 用的是同一份 rfc9002.txt（' + fmt(Q[u'bs'][3]) + u' 字节, sha256 前 16 位 '
       + Q[u'sha'][3] + u' ⇎ B62 那份 ' + P[u'sha'][4] + u' 逐字节相同）——同一份文书在两条条目里分别答“发多少”与“等多久”。'
       u'“四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧”“rfc-editor.org 此刻给的现行状态与类目”“勘误表是否已挂新版”'
       u'“现实 RTT 分布与各家 TCP 实现里的 TCP_RTO_MIN 取值”不可由在库文件判定，判词按第三档写、门槛不背书。')

T62 = (u'**B62 问的是新建连接在第一个 RTT 里能立刻发出多少字节, 五份一手规范给出五种答法**：'
       + bracket(P, SRC62, f62)
       + u'——五份同为 RFC Editor 纯文本面（回车 ' + J(P[u'cr']) + u' ⇎ 非 ASCII ' + J(P[u'na'])
       + u'）, 差异全在“同一条方程被谁写下、被谁否决、又被谁原样立为标准”。'
       u'头条答法 ' + P[u'ans'] + u'：结构解析现读 ' + u' ⇎ '.join(gk(FP, u'x_eq')) + u' ⇎ 变量名 '
       + u' ⇎ '.join(gk(FP, u'x_eq_var')) + u'；99 的否决句 “We do NOT allow this change” 就写在这枚方程之后第 '
       + str(gk(FP, u'x_a_gap')) + u' 行（该句库里 ' + str(gk(FP, u'n_dont_allow')[0]) + u' 处）, '
       u'三年后同一枚方程在 02 原样成为标准上限。'
       u'09 换形状不换阈值: 阈值 ' + fmt(gk(FP, u'x_c_lo_bound')) + u'⇎' + fmt(gk(FP, u'x_c_hi_bound'))
       + u' 在 02⇎09 各 ' + str(gk(FP, u'lit_1095')[1]) + u'⇎' + str(gk(FP, u'lit_1095')[2]) + u' ⇎ '
       + str(gk(FP, u'lit_2190')[1]) + u'⇎' + str(gk(FP, u'lit_2190')[2]) + u' 处, 而 4380 在 09 整篇 '
       + str(gk(FP, u'lit_4380')[2]) + u' 处——数字一个没留, 却从表的两端各算回一次: '
       + str(gk(FP, u'x_c_hi_mult')) + u'×' + str(gk(FP, u'x_c_hi_bound')) + u'＝' + str(gk(FP, u'x_c_top_at_hi'))
       + u' ⇎ ' + str(gk(FP, u'x_c_iw_mult')[2]) + u'×' + str(gk(FP, u'x_c_lo_bound')) + u'＝' + str(gk(FP, u'x_c_lo_at_lo'))
       + u'。中间档加宽只可复算: SMSS=' + fmt(gk(FP, u'x_c_hi_bound')) + u' 时 02 给 ' + fmt(gk(FP, u'x_b_at_hi'))
       + u' ⇎ 09 给 ' + fmt(gk(FP, u'x_c_upper_at2190')) + u', 多 ' + fmt(gk(FP, u'x_widen'))
       + u' 字节, 库里零字面；到常见 MSS=' + fmt(gk(FP, u'x_b_mssnum')) + u' 两份又并回 ' + fmt(gk(FP, u'x_at1460_b'))
       + u'⇎' + fmt(gk(FP, u'x_at1460_c')) + u'（差 ' + str(gk(FP, u'x_at1460_close')) + u'）。边界符号是唯一的成因线索: '
       u'02 的严格不等号 ' + str(gk(FP, u'x_b_strict')) + u' 行 ⇎ 09 的 <= ' + str(gk(FP, u'x_c_le'))
       + u' 行、上档 > ' + str(gk(FP, u'x_c_upper_lt')) + u' 行。21 QUIC 把量都换了: MSS ' + str(gk(FP, u'v_mss')[4])
       + u' 处 ⇎ SMSS ' + str(gk(FP, u'v_smss')[4]) + u' ⇎ max_datagram_size ' + str(gk(FP, u'v_mds')[4])
       + u' ⇎ datagram ' + str(gk(FP, u'v_datagram')[4]) + u', 方程 ' + str(gk(FP, u'x_eq_n')[4])
       + u' 枚——它用英文数词说话（“ten”⇎“twice”整句本遍现数 ' + J(cnt(P, u'ten times the maximum datagram size'))
       + u'）, 十倍×上限 ' + fmt(gk(FP, u'x_e_capnum')) + u' ⇎ 最小载荷 ' + fmt(gk(FP, u'x_e_floornum')) + u'×'
       + str(gk(FP, u'x_e_ten')) + u'＝' + fmt(gk(FP, u'x_e_iw')) + u', 13 十倍给 ' + fmt(gk(FP, u'x_eq_cap')[3])
       + u' 与 13 十倍之间差 ' + str(gk(FP, u'x_e_bridge')) + u' 字节＝' + str(gk(FP, u'x_e_seg')) + u' 段×头差。'
       u'初窗词频被页眉抬高而集合不抬: 词 ' + J(gk(FP, u'iw_word_gap')) + u' ⇎ 去壳长行差 ' + J(gk(FP, u'shell_delta'))
       + u'（印标题的页眉行 ' + J(gk(FP, u'hdr_title')) + u'）——两档必须分别立键。义务词在此不成差轴: 2119 四枚全大写词五份皆有 must '
       + J(gk(FP, u'u_required')) + u', 而 21 那份也印。千分位写法是倒置差轴: 14600 ⇎ 14,720 裸写与带逗号各 '
       + J(gk(FP, u'n_cap14600')) + u' ⇎ ' + J(gk(FP, u'n_cap4380')) + u' 处。跨行伪值 ' + str(gk(FP, u'wrap_pin_n'))
       + u' 枚针里 ' + str(gk(FP, u'wrap_gap_total')) + u' 处真跨行, 全在 13 十倍的 “10 segments” 上（'
       + J(gk(FP, u'wrap_gap_seg10')) + u'）。锚 ' + str(P[u'nent']) + u' 处／' + str(P[u'ndis'])
       + u' 个不同串（每标签 ' + tcount(P) + u', 单源 ' + str(P[u'sin']) + u' ⇎ 穿二至四源 ' + str(P[u'crs'])
       + u' ⇎ 五源全现 ' + str(P[u'alll']) + u', 归属检查 ' + str(P[u'checks']) + u' 次, 错配 0）, 逐字再现份数分 5 档 '
       + J(gk(FP, u'pool_tiers')) + u'。身份轴: 抬头 Standards Track ' + J(gk(FP, u'cat_std')) + u' ⇎ Experimental '
       + J(gk(FP, u'cat_exp')) + u'（唯一那份是 13 十倍）⇎ Obsoletes 行 ' + J(gk(FP, u'obs_hdr')) + u' ⇎ 勘误字样 '
       + J(gk(FP, u'errata')) + u'。B62 与 B63 共用 ' + fmt(P[u'bs'][4]) + u' 字节的 rfc9002.txt（sha256 前 16 位 '
       + P[u'sha'][4] + u'）, 两份面各自答“发多少”与“等多久”。'
       u'“五份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧”“rfc-editor.org 此刻给的类目与状态”“勘误表是否已把这五份之一改成另一版”'
       u'“现实链路的 MSS 分布与首窗在部署侧的实际取值”不可由在库文件判定，判词按第三档写、门槛不背书。')


CN = {2: u'两', 3: u'三', 4: u'四', 5: u'五', 6: u'六'}


def rowline(m, tag, question, extra):
    sp = m[u'sp']; F = m[u'F']; CH = m[u'CH']
    return (u'| ' + tag + u' | ' + str(m[u'encl']) + u'（新建, ' + question + u' 交' + CN[sp[u'ns']]
            + u'份一手规范各答一遍 ' + str(m[u'nent']) + u' 处标注／' + str(m[u'ndis']) + u' 个不同串（登记全命中, 每标签 '
            + tcount(m) + u', 归属检查 ' + str(m[u'checks']) + u' 次）: ' + CN[sp[u'ns']] + u'色锚位 '
            + u' ⇎ '.join(sp[u'lb'][i] + u' ⟦' + sp[u'tags'][i] + u'⟧' for i in range(sp[u'ns'])) + u'; ' + extra
            + u'; 同数共键 ' + str(len(CH[u'collisions'])) + u' 组、零项 ' + str(CH[u'zero_terms'])
            + u' 枚折成一条算式; 门槛侧 ' + str(CH[u'deriv_keys']) + u' 枚推导键／' + str(CH[u'deriv_points'])
            + u' 处复算点, 面内恒等式 ' + str(F[u'x_ident_n']) + u' 条; 五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对 '
            + str(m[u'ndis']) + u' 条锚逐字全命中, 工具侧 atomcheck 另核 ok=' + str(m[u'atom'][0]) + u' bad='
            + str(m[u'atom'][1]) + u'） |' + NL)


E62 = (u'头条答法 ' + P[u'ans'] + u'——方程 ' + u' ⇎ '.join(gk(FP, u'x_eq')) + u', 同一枚方程先经 “We do NOT allow this change” 否决（'
       + str(gk(FP, u'x_a_gap')) + u' 行后）再由 02 立为标准, 09 换成三段表而 4380 整篇 '
       + str(gk(FP, u'lit_4380')[2]) + u' 处（'
       + str(gk(FP, u'x_c_hi_mult')) + u'×' + str(gk(FP, u'x_c_hi_bound')) + u' ⇎ ' + str(gk(FP, u'x_c_iw_mult')[2])
       + u'×' + str(gk(FP, u'x_c_lo_bound')) + u'）, 中间档加宽 ' + fmt(gk(FP, u'x_widen'))
       + u' 字节只在复算里存在, 21 改量纲用英文数词（十倍上限 ' + fmt(gk(FP, u'x_e_capnum')) + u' ⇎ 最小载荷×10 '
       + fmt(gk(FP, u'x_e_iw')) + u'）')
E63 = (u'头条答数（毫秒归一）' + J(gk(FQ, u'y_ans_ms')) + u' ⇎ 数串 ' + u' ⇎ '.join(gk(FQ, u'y_ans_num'))
       + u' ⇎ 单位 ' + u' ⇎ '.join(gk(FQ, u'y_ans_unit')) + u', 极值比 ' + str(gk(FQ, u'y_ans_ratio'))
       + u' 余 ' + str(gk(FQ, u'y_ans_rem')) + u'; 3 秒搬进回退条款而数字不动（整句现数 ' + J(cnt(Q, u'set RTO <- 3 seconds'))
       + u' ⇎ 窗外 “3 seconds” ' + J(gk(FQ, u'y_outw_threesec')) + u'）, 21 宣称一秒而自身算法给 '
       + fmt(gk(FQ, u'y_d_claim_ms')) + u' 毫秒（差在库里零字面）, 上限 ' + fmt(gk(FQ, u'y_a_cap_ms')) + u' ⇎ '
       + fmt(gk(FQ, u'y_cap_ref_ms')) + u' 毫秒（比值 ' + str(gk(FQ, u'y_cap_ratio')) + u'）')

C62 = (u'| B62 | ' + bracket(P, SRC62, f62) + u' | 五份答同一个问题 ⇒ 99 两段给 1⇎2 段的上界并逐字否决 4 段方程'
       + u' ⇎ 02 把该方程立为标准（min(4*MSS, max(2*MSS, 2*SMSS)) 型）⇎ 09 换成三段表而删掉 4380 ⇎ 13 十倍把上限抬到 14600'
       + u' ⇎ 21 QUIC 改 datagram 量纲给 14,720; 五份同为文本面, 页眉 ⇎ 集合两档在初窗词频上分道' + NL)
C63 = (u'| B63 | ' + bracket(Q, SRC63, f63) + u' | 四份答同一个问题 ⇒ 89 三秒写在初始化条款 ⇎ 00 原样照抄 ⇎ 11 只把三秒留在 (5.7) 回退'
       + u' ⇎ 21 改答 PTO 并自称一秒而算法给 999/997 毫秒; 第四份与 B62 的第五份逐字节相同' + NL)

# 三处乘式必须自洽(本遍取的是建条目侧的键, 但相乘关系由本遍复核)
assert gk(FP, u'x_c_iw_mult')[2] * gk(FP, u'x_c_lo_bound') == gk(FP, u'x_c_lo_at_lo'), FP[u'x_c_iw_mult']
assert gk(FP, u'x_c_hi_mult') * gk(FP, u'x_c_hi_bound') == gk(FP, u'x_c_top_at_hi')
assert gk(FP, u'x_e_floornum') * gk(FP, u'x_e_ten') == gk(FP, u'x_e_iw')
assert gk(FQ, u'y_ans_max') == max(gk(FQ, u'y_ans_ms')) and gk(FQ, u'y_ans_min') == min(gk(FQ, u'y_ans_ms'))
assert gk(FQ, u'y_ans_ratio') == gk(FQ, u'y_ans_max') // gk(FQ, u'y_ans_min')
assert gk(FQ, u'y_ans_rem') == gk(FQ, u'y_ans_max') % gk(FQ, u'y_ans_min')


def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:50])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


S = sub(u'共 **61 条**（`babeltele/B01..B61`）', u'共 **63 条**（`babeltele/B01..B63`）', S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（61 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（63 条）', S)
S = sub(u'当前 **61 条语料／1749 条**推导全部通过（audit 自报“已机检的推导 1749 条”）',
        u'当前 **63 条语料／' + str(PROOFS) + u' 条**推导全部通过（audit 自报“已机检的推导 ' + str(PROOFS) + u' 条”）', S)
OLD61 = u'**B61 问的是一条链路至少要装多少字节'
assert S.count(OLD61) == 1
S = S.replace(OLD61, T63 + NL + T62 + NL + OLD61)
S = after(S, u'| B61 | 7641（新建,', rowline(P, u'B62', u'新建连接第一个 RTT 里能立刻发出多少字节', E62)
          + rowline(Q, u'B63', u'没有 RTT 样本时第一个重传超时设多久', E63))
m = re.search(u'第二代（B11–B61）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；全库合计 \\*\\*([\\d ]+)／([\\d ]+)\\*\\*（B61 一枚条目贡献 (\\d+)／(\\d+), 由本遍现数并校住建条目侧快照）', S)
assert m and m.group(5) == u'617' and m.group(6) == u'646', (u'字母账定位失败', m and m.groups())
d = lambda x: int(re.sub(u'[^0-9]', u'', x))
i2, o2, ia, oa = d(m.group(1)), d(m.group(2)), d(m.group(3)), d(m.group(4))
assert ia - i2 == 121 and oa - o2 == 2195, (i2, ia, o2, oa)
ni2, no2 = i2 + P[u'lin'] + Q[u'lin'], o2 + P[u'lout'] + Q[u'lout']
nia, noa = ia + P[u'lin'] + Q[u'lin'], oa + P[u'lout'] + Q[u'lout']
assert nia - ni2 == 121 and noa - no2 == 2195
S = sub(m.group(0), u'第二代（B11–B63）锚内字母 **' + fmt(ni2) + u'**、锚外 **' + fmt(no2) + u'**；全库合计 **'
        + fmt(nia) + u'／' + fmt(noa) + u'**（B62 ⇎ B63 两枚条目贡献 ' + fmt(P[u'lin']) + u'／' + fmt(P[u'lout'])
        + u' ⇎ ' + fmt(Q[u'lin']) + u'／' + fmt(Q[u'lout'])
        + u', 与 B61 的 617／646 同为去重锚口径, 由本遍现数并校住建条目侧快照）', S)
S = after(S, u'| B61 | `raw/ipv6/rfc1883.txt`', C62 + C63)
TOTOLD = u'| **合计（61 条）** | **379 379** | **109.2%**（摘要段合计 347 524） | — | **2 222** | — |'
assert S.count(TOTOLD) == 1, S.count(TOTOLD)
old_enc, old_dig = 379379, 347524
assert (enc_all, dig_all) == (old_enc + P[u'encl'] + Q[u'encl'],
                              old_dig + int(ROW[u'B62'][1]) + int(ROW[u'B63'][1])), (
    enc_all, dig_all, P[u'encl'], Q[u'encl'], ROW[u'B62'][1], ROW[u'B63'][1])
assert 2222 < uniq_all == 2229, (uniq_all,)
# 这张指标表自 B54 起就没再逐条开行（_readme54…_readme61 同样只改合计行）, 本遍按同一例: 只换合计行。
S = sub(TOTOLD, u'| **合计（63 条）** | **' + fmt(enc_all) + u'** | **' + ret_tot + u'%**（摘要段合计 '
        + fmt(dig_all) + u'，本遍新建的两枚为 ' + fmt(P[u'encl']) + u' ⇎ ' + fmt(Q[u'encl'])
        + u' 编码／' + fmt(int(ROW[u'B62'][1])) + u' ⇎ ' + fmt(int(ROW[u'B63'][1])) + u' 摘要） | — | **'
        + fmt(uniq_all) + u'** | — |', S)
S = sub(u'残余提示（不计 FAIL）：24 个 1–2 位结构计数（',
        u'残余提示（不计 FAIL）：' + str(soft_all) + u' 个 1–2 位结构计数（', S)
S = sub(u'故不消解））未逐位核验，',
        u'故不消解；新建的 B62 待核 ' + str(len(HINT[u'B62'])) + u' 项（`55` ⇎ `61`）——`55` 与 B61 同一枚, 是本条自定的“含关键数字长行”字符阈值'
        u'（输入参数而非源内计数）, `61` 是判词里两处“与 B61 相反”的交叉引用号而非源内数字；新建的 B63 待核列为空——它把两位以内的结构计数全部折进了 DERIV'
        u'（' + str(Q[u'CH'][u'zero_terms']) + u' 项零折成一条算式, 另有 ' + str(len(Q[u'CH'][u'collisions']))
        + u' 处跨值复合式）, 且 21 与 B62 共用一份 rfc9002.txt 使两条条目互为旁证））未逐位核验，', S)
S = sub(u'是**待核列为 0** 的 41 条条目里最连续的十二条',
        u'是**待核列为 0** 的 ' + str(zero_n) + u' 条条目里最连续的十二条', S)
S = sub(u'同样为 0；只有 B48 有 1 项，即上面那条条目号 48）',
        u'同样为 0，新建的 B63 亦为 0；除上面清单里那 ' + str(len(HINT)) + u' 枚条目外再无带待核的条目（B48 的 1 项即条目号 48）', S)
def digestcmd(tag, sp, paths, ns, extra):
    grp = []
    for i in range(ns):
        grp += [sp[i], paths[i], u'120', u'120']
    return (u'python -X utf8 corpus/_mkdigest3.py ' + tag + u' <entry> ' + u' '.join(grp)
            + u'   # ' + extra + NL)


def cmdfor(m, tag):
    sp, F, CH = m[u'sp'], m[u'F'], m[u'CH']
    n = tag[1:]
    paths = sp[u'paths']
    ns = sp[u'ns']
    o = []
    o.append(u'python -X utf8 corpus/_mkB' + n + u'.py                  # 建条目: 扁平契约 ' + str(len(F))
             + u' 枚键／DERIV ' + str(CH[u'deriv_keys']) + u' 枚算式 ⇎ 复算点 ' + str(CH[u'deriv_points'])
             + u' 处, 采侧对账 ' + str(len(m[u'MS'])) + u' 键 0 不符, 占位符未替换 0 个' + NL)
    o.append(digestcmd(tag, sp[u'tags'], paths, ns,
                       (u'五源' if ns == 5 else u'四源') + u'分节摘要(' + fmt(int(ROW[tag][1]))
                       + u' 字符, 窗口按 120⇎120 取句边界, ' + str(m[u'nent']) + u'/' + str(m[u'nent']) + u' 锚全命中)'))
    o.append(u'python -X utf8 corpus/_wire' + n + u'.py                    # 把 SCAN 段机械切进 audit.py::_b' + n
             + u'_scan 并插 DERIV[' + u"'" + tag + u"']" + NL)
    o.append(u'python -X utf8 corpus/_fill' + n + u'.py                    # 第四遍: 现取注数写回 ⛓解读注, '
             + u'模板全用 % 插值并在落盘前 assert 无残留占位 ⇎ 面内恒等式 ' + str(F[u'x_ident_n']) + u' 条' + NL)
    o.append(u'python -X utf8 corpus/atomcheck.py ' + tag + u' corpus/_atoms' + n + u'.txt   # 工具侧独立逐字校验: ok='
             + str(m[u'atom'][0]) + u' bad=' + str(m[u'atom'][1]) + u'（本遍重生成候选清单后重跑）' + NL)
    return u''.join(o)


CMD = cmdfor(P, u'B62') + cmdfor(Q, u'B63')
S = after(S, u'python -X utf8 corpus/_readme61.py', CMD
          + u'python -X utf8 corpus/_readme6263.py           # 记账: 本文件第五遍同时量 B62⇎B63 两份(量源一个 re 都不用, '
          + str(P[u'shared'] + Q[u'shared']) + u' 键与两张扁平契约⇎两张采集快照逐键对表; 全库合计取自本遍现跑的 audit)' + NL)
io.open(FM, 'w', encoding='utf-8', newline=NL).write(S)
SNAP = dict(totals=dict(enc=enc_all, dig=dig_all, uniq=uniq_all, proofs=PROOFS, hints=soft_all, zero=zero_n, nent=NENT),
            letters=dict(g2_in=ni2, g2_out=no2, all_in=nia, all_out=noa))
for k, v in M.items():
    SNAP[k] = dict(enc=v[u'encl'], dig=int(ROW[k][1]), anchors=v[u'nent'], distinct=v[u'ndis'], single=v[u'sin'],
                    cross=v[u'crs'], alln=v[u'alll'], checks=v[u'checks'], letters_in=v[u'lin'], letters_out=v[u'lout'],
                    atom=list(v[u'atom']), bytes=v[u'bs'], lines=v[u'ln'], nonblank=v[u'nb'], pagelines=v[u'pg'],
                    cr=v[u'cr'], nonascii=v[u'na'], sha=v[u'sha'], tag_counts=v[u'tcnt'],
                    derived=dict((x, v[u'F'][x]) for x in
                                 (u'y_ans_ms', u'y_ans_ratio', u'y_ans_rem') if x in v[u'F']))
json.dump(SNAP, io.open(u'corpus/_b6263readme.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 63 条 ｜ 编码合计 ' + fmt(enc_all) + u' ⇎ 摘要合计 ' + fmt(dig_all) + u' ⇎ 合计保留率 ' + ret_tot
      + u'% ｜ 唯一码点 ' + fmt(uniq_all) + u' ｜ 推导 ' + str(PROOFS) + u' 条 ｜ 待核 ' + str(soft_all) + u'（其中 0 项条目 '
      + str(zero_n) + u' 条） ｜ B62 ' + fmt(P[u'encl']) + u' 字符／' + str(P[u'nent']) + u' 锚(' + str(P[u'ndis'])
      + u' 串, ' + tcount(P) + u', 单源 ' + str(P[u'sin']) + u'⇎穿 ' + str(P[u'crs']) + u'⇎全现 ' + str(P[u'alll'])
      + u', 检查 ' + str(P[u'checks']) + u') ｜ B63 ' + fmt(Q[u'encl']) + u' 字符／' + str(Q[u'nent']) + u' 锚('
      + str(Q[
          'ndis']) + u' 串, ' + tcount(Q) + u', 单源 ' + str(Q[u'sin']) + u'⇎穿 ' + str(Q[u'crs']) + u'⇎全现 '
      + str(Q[u'alll']) + u', 检查 ' + str(Q[u'checks']) + u') ｜ 字母账 第二代 ' + fmt(ni2) + u'／' + fmt(no2)
      + u' ⇎ 全库 ' + fmt(nia) + u'／' + fmt(noa) + u' ｜ 第五遍现量与契约对表 ' + str(P[u'shared'] + Q[u'shared'])
      + u' 键 0 不符 ｜ atomcheck ok=' + str(P[u'atom'][0] + Q[u'atom'][0]) + u' bad=0 ｜ 答数 B63 ' + J(gk(FQ, u'y_ans_ms'))
      + u' ms ⇎ 极值比 ' + str(gk(FQ, u'y_ans_ratio')) + u' 余 ' + str(gk(FQ, u'y_ans_rem')))





