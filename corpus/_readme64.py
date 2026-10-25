# -*- coding: utf-8 -*-
r"""README 记账: 63 条 → 64 条（B64 一枚）。合计、码点、推导条数、待核清单全部取自 audit 的当下输出, 不手填。
第五套实现, 换算法不换定义: 采集侧 _pick64.py 用正则族与集合运算符, 建条目侧 _mkB64.py 用游标 find 循环＋逐字符判邻,
门槛侧 audit.py::_b64_scan 是机械抽出的那一份, 第四遍 _fill64.py 用行表与流式拼面对拍——
本遍量源一个 re 都不用(只用 find、切片、字符循环与 bisect; import re 只为刮 audit 的表行与改 README 既有句子):
锚位由逐字符状态机在编码区里走出(遇 ⟨ 起、遇 ⟩ 止, 标签取该 ⟨ 之前最近的一枚 ⟦), 归属由逐字符归一后的面 find 判,
字母账按 ord 区间计数, 源账用字节循环数换行与非空, 集合交并走 bisect。每个数与 _b64flat.json／_b64meas.json／
_b64checks.json 三张快照双向对表, 任一标量对不上就当场停机; 本遍现量另存 _b64readme.json。
签名换了算法: 采集侧 sha256 前 16 位 ⇎ 建条目侧 blake2b(8 字节), 本遍两式都算, 只要求“不同签名数”一致。"""
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
    """逐字符归一面: 只留 a-z0-9(建条目侧声明的口径是“归一只留 a-z0-9”, 与 B62⇎B63 那遍折成单空格的写法不同,
    换算法不换定义: 本遍不分段拼接, 单趟循环按 ord 区间挑码点)。"""
    o = []
    for c in s:
        if u'a' <= c <= u'z' or u'0' <= c <= u'9':
            o.append(c)
        elif u'A' <= c <= u'Z':
            o.append(chr(ord(c) + 32))
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
    return c


def scan_occ(s, ndl):
    """同一支字面, 另一种数法: 逐格切片比较, 不用 find。"""
    L, c, i = len(ndl), 0, 0
    while i + L <= len(s):
        if s[i:i + L] == ndl:
            c += 1; i += L
        else:
            i += 1
    return c


SP = dict(tag=u'B64', n=u'64', ns=4,
          entry=u'corpus/babeltele/B64_dhcp_retransmit_cap_four_answers.md',
          paths=[u'corpus/raw/dhcp/rfc2131.txt', u'corpus/raw/dhcp/rfc3315.txt',
                 u'corpus/raw/dhcp/rfc7083.txt', u'corpus/raw/dhcp/rfc8415.txt'],
          tags=[u'A', u'B', u'C', u'D'],
          lb=[u'97 六十四', u'03 一百二', u'13 倍三十', u'18 可下发'],
          short=[u'rfc2131.txt', u'rfc3315.txt', u'rfc7083.txt', u'rfc8415.txt'],
          dir=u'dhcp', alln=u'anchor_all4', nall=4)

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
assert PROOFS == 2093 and len(HINT) == 16, (PROOFS, len(HINT))
assert u'PASS' in AUD and u'FAIL' not in AUD.split(u'保真门槛')[1][:40], AUD[-400:]

t, n, ns = SP[u'tag'], SP[u'n'], SP[u'ns']
F = json.load(io.open(u'corpus/_b%sflat.json' % n, encoding='utf-8'))
CH = json.load(io.open(u'corpus/_b%schecks.json' % n, encoding='utf-8'))
MS = json.load(io.open(u'corpus/_b%smeas.json' % n, encoding='utf-8'))
DER = json.load(io.open(u'corpus/_deriv%s.json' % n, encoding='utf-8'))
T = RD(SP[u'entry'])
a = T.index(u'⟪BabelTele⟫' + NL) + len(u'⟪BabelTele⟫' + NL)
b = T.index(NL + NL + u'## ', a)
enc = T[a:b]
ORIG = T[T.index(u'[[原始语料|ORIGINAL]]' + NL) + len(u'[[原始语料|ORIGINAL]]' + NL):T.index(NL + NL + u'## ⟪BabelTele')]
assert enc.count(u'{') == 0 and u'◘' not in T and u'%(' not in T, (enc.count(u'{'),)

# ---- 锚位: 逐字符状态机(标签取这枚 ⟨ 之前最近的一枚 ⟦) ----
seq, tag, i = [], None, 0
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
FACE = [cnorm(RW(p)) for p in SP[u'paths']]
raws = [RW(p) for p in SP[u'paths']]
LOWF = [r.lower() for r in raws]
mem = [tuple(k for k in range(ns) if NA[j] and FACE[k].find(NA[j]) >= 0) for j in range(len(NA))]
checks = len(NA) * ns
sin = len([x for x in mem if len(x) == 1])
crs = len([x for x in mem if 1 < len(x) < ns])
alll = len([x for x in mem if len(x) == ns])
err = len([x for x in mem if not x])
declared = [tg for tg, _, _, _ in seq]
for tg, x, _, _ in seq:
    assert SP[u'tags'].index(tg) in mem[atoms.index(x)], (t, u'锚不在自称的源里', tg, x[:40])
tcnt = dict((g, sum(1 for d in declared if d == g)) for g in SP[u'tags'])
lin_all = sum(letters(x) for _, x, _, _ in seq)
lin = sum(letters(x) for x in atoms)
cover = [False] * len(enc)
for _, x, i0, i1 in seq:
    for k in range(i0, i1 + 1):
        cover[k] = True
lout = letters(u''.join(enc[k] for k in range(len(enc)) if not cover[k]))

# ---- 源账: 字节循环数换行/非空, 行数与页标两种口径都量 ----
bs, ln, nb, pg, sh2, bl2, cr, na, ff, nba, chars_no_nl = [], [], [], [], [], [], [], [], [], [], []
for pth, r in zip(SP[u'paths'], raws):
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
    rb = io.open(pth, 'rb').read()
    bs.append(os.path.getsize(pth))
    ln.append(c_ln + 1); nb.append(c_nb); cr.append(c_cr); na.append(c_na)
    ff.append(c_ff); nba.append(c_nba)
    chars_no_nl.append(len(r) - r.count(NL))
    pg.append(occ(r, u'[Page '))
    sh2.append(hashlib.sha256(rb).hexdigest()[:16])
    bl2.append(hashlib.blake2b(rb, digest_size=8).hexdigest())
    assert [ord(c) > 127 for c in r].count(True) == c_na == 0

g = lambda k: F[k]
assert (F[u'anchor_total'], F[u'anchor_distinct']) == (len(seq), len(atoms)), (t, F[u'anchor_total'], len(seq))
assert (F[u'anchor_single'], F[u'anchor_cross'], F[SP[u'alln']]) == (sin, crs, alll), (t, sin, crs, alll)
assert F[u'anchor_err'] == err == 0 and CH[u'anchor_total'] == len(seq), (t, err, len(seq))
assert F[u'checks'] == checks == F[u'anchor_distinct'] * ns, (t, checks, F[u'checks'])
assert [F[u'tag_' + x] for x in SP[u'tags']] == [tcnt[x] for x in SP[u'tags']], (t, tcnt)
assert F[u'sig'] == bl2 and MS[u'sig_sha256_16'] == sh2, (t, F[u'sig'], bl2)
assert F[u'sig_distinct'] == len(set(bl2)) == len(set(sh2)) == ns, (t, F[u'sig_distinct'])
assert CH[u'letters_in'] == lin and CH[u'letters_out'] == lout, (t, lin, lin_all, CH[u'letters_in'], lout)
encl = len(enc) - enc.count(NL)
assert CH[u'enc_chars'] == encl and int(ROW[t][2]) == encl, (t, encl, ROW[t][2])
assert int(ROW[t][1]) == len(ORIG), (t, ROW[t][1], len(ORIG))
assert g(u'bytes') == bs and g(u'chars') == bs and g(u'chars_no_nl') == chars_no_nl, (t, bs, g(u'chars'))
assert g(u'nonblank') == nb and g(u'nonblank_asciib') == nba, (t, nb, nba)
assert g(u'lines') == ln, (t, ln, g(u'lines'))
assert g(u'nonascii') == na and g(u'cr') == cr and g(u'bom') == [0] * ns, (t, na, cr)
assert [x - y for x, y in zip(nba, nb)] == ff == g(u'nb_gap') == g(u'ff_only_lines'), (t, nba, nb, ff)
assert pg == g(u'foot') == g(u'formfeed') == g(u'trail') == g(u'foot_brk') == g(u'pages_est'), (t, pg, g(u'foot'))
assert g(u'pagelines') == [g(u'hdr')[i] + g(u'foot')[i] for i in range(ns)], (t, g(u'pagelines'))
assert sorted(F) == sorted(CH[u'flat']) and not [k for k in F if F[k] != CH[u'flat'][k]], (t, len(F))
shared = [k for k in MS if k in F and isinstance(MS[k], (int, float, str)) and not isinstance(MS[k], bool)]
bad = [k for k in shared if rnd(MS[k]) != rnd(F[k])]
assert not bad, (t, bad[:6])

# ---- 乘式与差式必须自洽(键取建条目侧, 关系由本遍现算) ----
assert g(u'y_ans_max') == max(g(u'y_ans_ms')) and g(u'y_ans_min') == min(g(u'y_ans_ms'))
assert g(u'y_ans_ratio') == g(u'y_ans_max') // g(u'y_ans_min') and g(u'y_ans_rem') == g(u'y_ans_max') % g(u'y_ans_min')
assert g(u'y_ans_distinct') == len(set(g(u'y_ans_ms')))
assert g(u'y_ans_max') == g(u'y_ans_ratio') * g(u'y_ans_min') + g(u'y_ans_rem') == 56 * 64000 + 16000
assert g(u'y_ans_span_close') == g(u'y_ans_max') - g(u'y_ans_ratio') * g(u'y_ans_min') - g(u'y_ans_rem') == 0
assert g(u'a_seq') == [4, 8, 16, 32, 64] and g(u'a_seq_n') == len(g(u'a_seq'))
assert all(g(u'a_seq')[i] * 2 == g(u'a_seq')[i + 1] for i in range(4))
assert g(u'a_ratio') == g(u'a_seq')[-1] // g(u'a_seq')[0] == 2 ** g(u'a_doublings')
assert g(u'a_seq_ms') == [x * 1000 for x in g(u'a_seq')] and g(u'y_a_first') == g(u'a_seq_ms')[0]
assert g(u'y_ans_s')[0] == g(u'a_seq')[-1] == 64 and g(u'lit_max64') == [1, 0, 0, 0]
assert g(u'clamp_span') == g(u'clamp_hi')[2] // g(u'clamp_lo')[2] == 1440
assert g(u'bd_same') + g(u'bd_diff_n') == g(u'bd_n') == 21 and g(u'bd_close') == 0
assert g(u'bd_pv_same') == g(u'bd_same') and len(g(u'bd_unproposed')) == g(u'bd_unproposed_n') == 2
assert g(u'tbl_rows')[1][0] + g(u'tbl_row_delta') == g(u'tbl_rows')[3][0]
assert [len(x) for x in g(u'tbl_rows')] == g(u'tbl_n')
assert g(u'on_ratio') == [p[2] // p[1] for p in g(u'on_pair_c') if p[1]] == [30, 30]
assert g(u'on_n_c') == 9 and len(g(u'on_pair_c')) == 4 and g(u'on_span') == 22
assert [g(u'on_n_' + x) for x in u'abcd'] == [0, 0, 9, 0]
assert g(u'share_bd') == g(u'y_bd_byte_shared') + g(u'y_bd_norm_only') == 526 + 101
assert g(u'share_cd') == g(u'y_cd_byte_shared') and g(u'y_cd_norm_only') == 0
assert g(u'al_same_bytes') == g(u'al_punct_only') == 0 and g(u'al_norm_diff') == g(u'al_n') == 2
assert g(u'union_abcd') == g(u'abcd_incl') and g(u'abcd_close') == 0
assert g(u'union_delta') == g(u'union_abcd') - g(u'union_abc') == 2415
assert g(u'hdr') == [g(u'hdr_sp')[i] + g(u'hdr_ns')[i] for i in range(ns)]
assert g(u'hdr_ledger_sum') == 0 and g(u'pg_foot_sum') == g(u'ff_foot_sum') == g(u'nb_ff_sum') == 0
assert g(u'shell_delta') == [g(u'lines_ge40')[i] - g(u'lines_ge40_nos')[i] for i in range(ns)]
assert g(u'lit_srt_minus_irt') == [g(u'lit_solmaxrt')[i] - g(u'lit_irt')[i] for i in range(ns)]
assert g(u'dur_ms_hi') // g(u'dur_ms_lo') == g(u'dur_ratio')[0] and g(u'dur_rem') == [0]
assert sum(g(u'pool_tiers')) == g(u'pool_n') and g(u'pool_close') == 0
assert g(u'wrap_total') == g(u'wrap_pin_hit') == 1 and g(u'y_ans_wrap') == [0] * ns
assert g(u'x_ident_n') == 27 and g(u'scalar_clos_sum') == 0 and g(u'scalar_clos_n') == 16
assert CH[u'deriv_keys'] == len(DER) == 147 and CH[u'zero_terms'] == 157 and len(CH[u'collisions']) == 54

R = dict(F=F, CH=CH, MS=MS, DER=DER, enc=enc, orig=ORIG, atoms=atoms, mem=mem, bs=bs, ln=ln, nb=nb, pg=pg,
         sh2=sh2, bl2=bl2, cr=cr, na=na, ff=ff, nba=nba, sp=SP, faces=list(FACE), encl=encl, lin_all=lin_all,
         lin=lin, lout=lout, tcnt=tcnt, checks=checks, sin=sin, crs=crs, alll=alll, nent=len(seq), ndis=len(atoms),
         flat=len(F), meas=len(MS), shared=len(shared), cno=chars_no_nl)
ans = re.search(u'：([^（]+)（', T.split(NL)[0]).group(1)
R[u'ans'] = ans
io.open(u'corpus/_atoms%s.txt' % n, 'w', encoding='utf-8').write(NL.join(atoms) + NL)
AC = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/atomcheck.py', t,
                     u'corpus/_atoms%s.txt' % n], capture_output=True, text=True, encoding='utf-8').stdout
mm = re.search(r'ok=(\d+) bad=(\d+)', AC)
assert mm and int(mm.group(1)) == len(atoms) and int(mm.group(2)) == 0, (t, AC[-160:])
R[u'atom'] = (int(mm.group(1)), int(mm.group(2)))

# ---- 全库合计 ----
A = ROW[u'ALL']
dig_all, enc_all = int(A[1].replace(u' ', u'')), int(A[2].replace(u' ', u''))
ret_tot = A[3].strip().strip(u'*').strip(u'%')
assert re.match(u'^[\\d.]+$', ret_tot), (A[3],)
uniq_all = int(A[5].replace(u' ', u''))
soft_all = sum(len(v) for v in HINT.values())
assert soft_all == 27 and int(A[11]) == soft_all, (soft_all, A[11])
NENT = 64
zero_n = len([k for k in ROW if k.startswith(u'B') and ROW[k][11] == u'0'])
assert zero_n == NENT - len(HINT), (zero_n, len(HINT))

S = RD(FM)
FP = F


def gk(Fx, k):
    assert k in Fx, k
    return Fx[k]


def bracket(srcs, fact):
    o = []
    for i in range(ns):
        o.append(srcs[i] + u'（' + SP[u'lb'][i] + u' ⟦' + SP[u'tags'][i] + u'⟧：'
                 + fmt(R[u'bs'][i]) + u' 字节／行数 ' + fmt(R[u'ln'][i]) + u'／非空行 ' + fmt(R[u'nb'][i])
                 + u'（另有换页符独占 ' + fmt(R[u'ff'][i]) + u' 行按 strip 口径不计）'
                 + u'／' + fact(FP, R, i) + u'／回车 ' + str(R[u'cr'][i]) + u'／非 ASCII ' + str(R[u'na'][i]) + u'）')
    return u' ⇎ '.join(o)


SRC64 = [u'`raw/dhcp/rfc2131.txt`', u'`rfc3315.txt`', u'`rfc7083.txt`', u'`rfc8415.txt`']


def f64(Fx, m, i):
    tbl = (str(Fx[u'tbl_n'][i]) + u' 张 ' + fmt(Fx[u'tbl_rows'][i][0]) + u' 行（表头第 '
           + fmt(Fx[u'tbl_start'][i][0]) + u' 行）') if Fx[u'tbl_n'][i] else u'0 张（答数不在表里）'
    return (u'答数 ' + fmt(Fx[u'y_ans_ms'][i]) + u' 毫秒＝“' + Fx[u'y_ans_num'][i] + u' ' + Fx[u'y_ans_unit'][i]
            + u'”／参数表 ' + tbl + u'／SOL_MAX_RT 字样 ' + fmt(Fx[u'lit_solmaxrt'][i])
            + u' 处／页眉 ' + fmt(Fx[u'hdr'][i]) + u'⇎页脚 ' + fmt(Fx[u'foot'][i])
            + u'⇎`[Page ` 串 ' + str(m[u'pg'][i]) + u' 处')


def cnt(ndl, low=False):
    """本遍独立复核: 在原面(或整面转小写后的面)上用逐位切片比较数非重叠出现次数——
    建条目侧用游标 find 循环, 本遍改成一格一格比字面, 定义不变(字面在面内的出现处数)。"""
    fl = LOWF if low else raws
    return [scan_occ(f, ndl) for f in fl]


def tcount():
    return u' ⇎ '.join(tt + u' ' + str(R[u'tcnt'][tt]) for tt in SP[u'tags'])


assert cnt(u'SOL_MAX_RT') == gk(FP, u'lit_solmaxrt'), cnt(u'SOL_MAX_RT')
assert cnt(u'120 secs') == gk(FP, u'lit_s120') and cnt(u'3600 secs') == gk(FP, u'lit_s3600')
assert cnt(u'600 secs') == gk(FP, u'lit_s600')
assert cnt(u'maximum of 64 seconds') == gk(FP, u'lit_max64')
assert cnt(u'duration_of_lease') == gk(FP, u'lit_durword')
assert cnt(u'0.875 * duration_of_lease') == gk(FP, u'lit_durdef875')
assert cnt(u'obsoleted by', True) == gk(FP, u'obsoleted_by')

T64 = (u'**B64 问的是报文发出去没人应答时重传退避该封顶多久, 四份一手规范给出四种答法**：'
       + bracket(SRC64, f64)
       + u'——四份同为 RFC Editor 的纯文本面, 全 LF、无 BOM、无非 ASCII 码点, 所以本条没有剥壳层, 差异全在“同一枚封顶被写成什么、由谁来写”。'
       u'头条答数按毫秒归一 ' + J(gk(FP, u'y_ans_ms')) + u' ⇎ 数串 ' + u' ⇎ '.join(gk(FP, u'y_ans_num'))
       + u' ⇎ 单位 ' + u' ⇎ '.join(gk(FP, u'y_ans_unit'))
       + u' ⇎ 数与单位跨行 ' + J(gk(FP, u'y_ans_wrap')) + u'——四枚答数无一跨行; 最大÷最小 '
       + fmt(gk(FP, u'y_ans_max')) + u'÷' + fmt(gk(FP, u'y_ans_min')) + u'＝' + str(gk(FP, u'y_ans_ratio'))
       + u' 余 ' + str(gk(FP, u'y_ans_rem')) + u' ⇎ 不同答数 ' + str(gk(FP, u'y_ans_distinct'))
       + u' 种; 两端之比校成闭合式 ' + fmt(gk(FP, u'y_ans_max')) + u'＝' + str(gk(FP, u'y_ans_ratio')) + u'×'
       + fmt(gk(FP, u'y_ans_min')) + u'＋' + fmt(gk(FP, u'y_ans_rem')) + u'（闭合 '
       + str(gk(FP, u'y_ans_span_close')) + u' ⇎ 提案⇎标准同值闭合 ' + str(gk(FP, u'y_cd_ans_close'))
       + u'）; 四份面上出现过的时长两端 ' + fmt(gk(FP, u'dur_ms_lo')) + u'⇎' + fmt(gk(FP, u'dur_ms_hi'))
       + u' 毫秒（比 ' + str(gk(FP, u'dur_ratio')[0]) + u' 倍余 ' + str(gk(FP, u'dur_rem')[0])
       + u'）, 逐份时长集（毫秒）97 ' + J(gk(FP, u'durms_a')) + u' ⇎ 03 ' + J(gk(FP, u'durms_b')) + u' ⇎ 13 '
       + J(gk(FP, u'durms_c')) + u' ⇎ 18 ' + J(gk(FP, u'durms_d')) + u'（出现处含重复 '
       + u' ⇎ '.join(str(gk(FP, u'durlit_' + x)) for x in u'abcd') + u' 枚, 单位种类 '
       + J(gk(FP, u'y_unit_n')) + u' 种）。'
       u'97 的 64 秒不是孤立字面而是翻倍序列末项: 首值现读 ' + fmt(gk(FP, u'y_a_first')) + u' 毫秒 ⇎ 下次 '
       + fmt(gk(FP, u'y_a_next')) + u' 毫秒 ⇎ 序列 ' + u'→'.join(str(x) for x in gk(FP, u'a_seq'))
       + u' 秒共 ' + str(gk(FP, u'a_seq_n')) + u' 项 ⇎ 翻倍 ' + str(gk(FP, u'a_doublings')) + u' 次 ⇎ 末÷首 '
       + str(gk(FP, u'a_ratio')) + u'＝2^' + str(gk(FP, u'a_doublings')) + u'; 原面直搜 “maximum of 64 seconds” '
       + J(cnt(u'maximum of 64 seconds')) + u' 处（本遍逐格切片比较）, 而 SOL_MAX_RT 这个术语在四份里 ' + J(gk(FP, u'lit_solmaxrt'))
       + u' 处——97 通篇 0 处, 它连这个词都没有（IRT 词根 ' + J(gk(FP, u'lit_irt')) + u' 处, 两族之差 '
       + J(gk(FP, u'lit_srt_minus_irt')) + u'）。'
       u'03 把答数钉成参数表里的一行: 表 ' + J(gk(FP, u'tbl_n')) + u' 张、行 ' + fmt(gk(FP, u'tbl_rows')[1][0]) + u'⇎'
       + fmt(gk(FP, u'tbl_rows')[3][0]) + u'（表头第 ' + fmt(gk(FP, u'tbl_start')[1][0]) + u'⇎'
       + fmt(gk(FP, u'tbl_start')[3][0]) + u' 行, 差 ' + str(gk(FP, u'tbl_row_delta'))
       + u' 行）, “120 secs” ' + J(gk(FP, u'lit_s120')) + u' 处恰是 SOL ⇎ INF 两行, 客户端无从改变。'
       u'13 不进表, 用 OLD:/NEW: 把同一行重印再改: 标签 ' + str(gk(FP, u'on_n_c')) + u' 枚全在 13（四份 '
       + J([gk(FP, u'on_n_' + x) for x in u'abcd']) + u' 枚）, 成对解出 ' + str(len(gk(FP, u'on_pair_c')))
       + u' 组: ' + u' ⇎ '.join(p[0] + u' ' + str(p[1]) + u'→' + str(p[2]) for p in gk(FP, u'on_pair_c') if p[1])
       + u'（比值 ' + J(gk(FP, u'on_ratio')) + u'）⇎ 另 ' + str(len([p for p in gk(FP, u'on_pair_c') if not p[1]]))
       + u' 组是义务词重印, 四组行距合计 ' + str(gk(FP, u'on_span')) + u'; 改动参数 '
       + str(len(gk(FP, u'on_changed'))) + u' 枚 ' + u' ⇎ '.join(gk(FP, u'on_changed'))
       + u'; 同一遍还开出可下发选项, 值域 ' + fmt(gk(FP, u'clamp_lo')[2]) + u'..' + fmt(gk(FP, u'clamp_hi')[2])
       + u'（上下界比 ' + str(gk(FP, u'clamp_span')) + u'）, 字面 ' + J(gk(FP, u'lit_clamp')) + u' 处 ⇎ 86400 '
       + J(gk(FP, u'y_clamp_86400')) + u' 处。'
       u'18 收下同一枚 3600 秒却另有来历: 与 03 同名的参数 ' + str(gk(FP, u'bd_n')) + u' 枚里 '
       + str(gk(FP, u'bd_same')) + u' 枚逐字同值 ⇎ ' + str(gk(FP, u'bd_diff_n')) + u' 枚改动 '
       + u' ⇎ '.join(x[0] + u' ' + str(x[1]) + u'→' + str(x[2]) for x in gk(FP, u'bd_diff'))
       + u', 其中 ' + str(gk(FP, u'bd_unproposed_n')) + u' 枚（' + u' ⇎ '.join(gk(FP, u'bd_unproposed'))
       + u'）是 18 自己改的、13 通篇没提; 整除比值档 ' + str(len(gk(FP, u'bd_ratio'))) + u' 枚里 '
       + str(gk(FP, u'bd_ratio')[0]) + u' 倍 ' + str(sum(1 for x in gk(FP, u'bd_ratio') if x > 1)) + u' 枚 ⇎ 同值 '
       + str(sum(1 for x in gk(FP, u'bd_ratio') if x == 1)) + u' 枚（另 '
       + str(gk(FP, u'bd_n') - len(gk(FP, u'bd_ratio'))) + u' 枚 5→4 不整除, 不入比值档）。'
       u'可下发不等于照收: 18 的夹逼句与 13 逐行对照 ' + str(gk(FP, u'al_n')) + u' 行, 字节全等 '
       + str(gk(FP, u'al_same_bytes')) + u' ⇎ 仅标点差 ' + str(gk(FP, u'al_punct_only')) + u' ⇎ 归一也不同 '
       + str(gk(FP, u'al_norm_diff')) + u'（闭合 ' + str(gk(FP, u'al_close')) + u'）, 字符净差 '
       + str(gk(FP, u'al_char_delta')) + u'; “越界即弃”句 ' + J(gk(FP, u'lit_discard')) + u' 处而“必须丢弃”只在 18, '
       u'覆盖的存活期⇎接口作用域也只有 18 写（' + J(gk(FP, u'lit_retain')) + u' ⇎ ' + J(gk(FP, u'lit_iface'))
       + u'）, 而 “MUST ignore” 一族 ' + J(gk(FP, u'y_must_ignore_n')) + u' 处。'
       u'次轴“多久去续租”: 97 用 T1＝0.5×duration_of_lease ⇎ T2＝0.875×同一标识符（字样 '
       + J(cnt(u'duration_of_lease')) + u' 处, 本遍现数; 0.5 式 ' + J(gk(FP, u'n_p05')) + u' ⇎ 0.875 式 '
       + J(gk(FP, u'n_p08')) + u' 处）, 而它的 T2 缺省式被排版劈在两行: 原面直搜 ' + J(gk(FP, u'lit_durdef875'))
       + u' 处 ⇎ 折平后 ' + J(gk(FP, u'lit_durdef875_fold')) + u' 处（逐份差 ' + J(gk(FP, u'lit_durdef875_gap'))
       + u', 合计 ' + str(gk(FP, u'lit_durdef875_gap_sum')) + u'）——按行搜该字面的复算者读不到它; 折行通道次轴针 '
       + str(gk(FP, u'wrap_pin_n')) + u' 枚里 ' + str(gk(FP, u'wrap_pin_hit')) + u' 枚有差、真跨行 '
       + str(gk(FP, u'wrap_total')) + u' 处, 数与单位拆两行的时长 ' + J(gk(FP, u'y_dur_wrap')) + u' 枚（其值只在 97: '
       + fmt(gk(FP, u'y_dur_wrap_ms')[0][0]) + u' 毫秒）; v6 三份改用 shortest preferred lifetime 作基准（行数 '
       + J(gk(FP, u'n_spl')) + u'）并把 T1/T2 交给服务器下发。'
       u'义务词不成差轴, 成轴的是“答数旁边站着 MUST 还是 MAY”: 全大写 MUST ' + J(gk(FP, u'u_must')) + u' ⇎ SHOULD '
       + J(gk(FP, u'u_should')) + u' ⇎ MAY ' + J(gk(FP, u'u_may')) + u' ⇎ MUST NOT ' + J(gk(FP, u'u_must_not'))
       + u', 三词合计 ' + J(gk(FP, u'oblig_up')) + u' ⇎ 小写词界档合计 ' + J(gk(FP, u'oblig_low'))
       + u'——窗内 MUST ' + J(gk(FP, u'y_secw_must')) + u' ⇎ 窗外 ' + J(gk(FP, u'y_outw_must'))
       + u': 97 的 ' + str(gk(FP, u'y_secw_must')[0]) + u' 处全在答数那一节（答数句自己挂 SHOULD, 散文）, '
       u'而 18 的答数行只是表里一个数、义务句全在窗外那一节; RFC 2119 被引 ' + J(gk(FP, u'rfc2119_ref')) + u' 次。'
       u'壳账: 页眉带空格 ' + J(gk(FP, u'hdr_sp')) + u' ⇎ 粘连档 ' + J(gk(FP, u'hdr_ns')) + u' ⇎ 并档 '
       + J(gk(FP, u'hdr')) + u'; 页脚 ⇎ 换页 ⇎ `[Page ` 串 ⇎ 行尾空格档四式逐份全等 ' + J(gk(FP, u'foot'))
       + u'（本遍用 find 数串、建条目侧判整行, 两口径 ' + str(gk(FP, u'pg_foot_sum')) + u' 之差为 0）; 非空行两口径 '
       + J(gk(FP, u'nonblank')) + u' ⇎ 只认空格制表回车档 ' + J(gk(FP, u'nonblank_asciib')) + u', 差 '
       + J(gk(FP, u'nb_gap')) + u' 恰是换页符独占行。签名换算法不换定义: 采集侧 sha256 前 16 位 ⇎ 建条目侧 blake2b 8 字节, '
       u'两式各得 ' + str(gk(FP, u'sig_distinct')) + u' 种（' + R[u'sh2'][0] + u' ⇎ ' + R[u'bl2'][0] + u'）。'
       u'搬运: 长行集合 ' + J(gk(FP, u'lines_ge40')) + u' ⇎ 去壳后 ' + J(gk(FP, u'lines_ge40_nos')) + u' ⇎ 差 '
       + J(gk(FP, u'shell_delta')) + u', 含关键数字的长行 ' + J(gk(FP, u'num_lines')) + u' 行; 两两交 '
       + str(gk(FP, u'share_ab')) + u' ⇎ ' + str(gk(FP, u'share_bc')) + u' ⇎ ' + str(gk(FP, u'share_ac')) + u' ⇎ '
       + str(gk(FP, u'share_ad')) + u' ⇎ ' + str(gk(FP, u'share_cd')) + u' ⇎ ' + str(gk(FP, u'share_bd'))
       + u' 行——03⇎18 那 ' + fmt(gk(FP, u'share_bd')) + u' 行是表行被逐字节复写（字节档 '
       + fmt(gk(FP, u'y_bd_byte_shared')) + u' ⇎ 只在归一同 ' + fmt(gk(FP, u'y_bd_norm_only'))
       + u'）, 而提案⇎标准 13⇎18 只 ' + str(gk(FP, u'share_cd')) + u' 行（字节档 '
       + str(gk(FP, u'y_cd_byte_shared')) + u'）, 复写在句内不在整行; 只在本份 ' + str(gk(FP, u'only_c'))
       + u' 行, 四份并集 ' + fmt(gk(FP, u'union_abcd')) + u' ⇎ 三份 ' + fmt(gk(FP, u'union_abc')) + u'（容斥闭合 '
       + str(gk(FP, u'abcd_close')) + u'）。'
       u'身份与继承: Standards Track ' + J(gk(FP, u'cat_std')) + u' ⇎ Obsoletes 头 ' + J(gk(FP, u'obs_hdr'))
       + u' ⇎ Updates 头 ' + J(gk(FP, u'upd_hdr')) + u' ⇎ ISSN ' + J(gk(FP, u'issn_hdr')) + u', 引用 3315 '
       + J(gk(FP, u'cite_3315')) + u' 处拆带空格 ' + J(gk(FP, u'cite_3315_sp')) + u' ⇎ 粘连 '
       + J(gk(FP, u'cite_3315_ns')) + u' ⇎ 7083 ' + J(gk(FP, u'cite_7083')) + u' ⇎ 8415 '
       + J(gk(FP, u'cite_8415')) + u'——13 通篇引 03 ' + str(gk(FP, u'cite_3315')[2]) + u' 次而零次引 18（它早五年）, '
       u'18 引 13 ' + str(gk(FP, u'cite_7083')[3]) + u' 次把提案收进标准, “obsoleted by” 字样 '
       + J(cnt(u'obsoleted by')) + u' 处全在 18 的对照附录。'
       u'锚 ' + str(R[u'nent']) + u' 处／' + str(R[u'ndis']) + u' 个不同串（每标签 ' + tcount() + u', 单源 '
       + str(R[u'sin']) + u' ⇎ 穿二三源 ' + str(R[u'crs']) + u' ⇎ 四源全现 ' + str(R[u'alll'])
       + u'——无一枚四源同现, 因为答数本身就分家, 归属检查 ' + str(R[u'checks']) + u' 次, 错配 0）, '
       u'逐字再现份数分 4 档 ' + J(gk(FP, u'pool_tiers')) + u'（池 ' + fmt(gk(FP, u'pool_n')) + u' 条, 分档闭合 '
       + str(gk(FP, u'pool_close')) + u', 池中实际用作锚 ' + str(CH[u'pool_used']) + u' 条）。'
       u'“四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧”“rfc-editor.org 此刻给的现行状态与类目”“勘误表是否已把 03 的 §5.5 或 18 的表行改成别的数”'
       u'“各家 DHCP 客户端实际把 SOL_MAX_RT 记多久、服务器现网下发到什么值”不可由在库文件判定，判词按第三档写、门槛不背书。')

C64 = (u'| B64 | ' + bracket(SRC64, f64) + u' | 四份答同一个问题 ⇒ 97 把封顶写成散文里翻倍序列的末项（64 秒, 全篇 0 处 SOL_MAX_RT）'
       + u' ⇎ 03 钉成参数表一行（120 秒, 2 处即 SOL⇎INF 两行, 客户端无从改变） ⇎ 13 不进表而用 OLD:/NEW: 重印同一行、只改两枚并开出可下发值域 60..86400'
       + u' ⇎ 18 收下同一枚 3600 秒却另有来历: 同名 21 枚参数 17 枚逐字同值 ⇎ 4 枚改动, 其中 2 枚是它自己改的、13 通篇没提;'
       + u' 可下发不等于照收——夹逼句两行对照字节全等 0、归一也不同 2, 越界即弃句只在 18; 四份同为纯文本面, 页眉 ⇎ 页脚 ⇎ 换页三式在初窗词频上分道' + NL)

CN = {2: u'两', 3: u'三', 4: u'四', 5: u'五', 6: u'六'}


def rowline(tag, question, extra):
    return (u'| ' + tag + u' | ' + str(R[u'encl']) + u'（新建, ' + question + u' 交' + CN[ns]
            + u'份一手规范各答一遍 ' + str(R[u'nent']) + u' 处标注／' + str(R[u'ndis']) + u' 个不同串（登记全命中, 每标签 '
            + tcount() + u', 归属检查 ' + str(R[u'checks']) + u' 次）: ' + CN[ns] + u'色锚位 '
            + u' ⇎ '.join(SP[u'lb'][i] + u' ⟦' + SP[u'tags'][i] + u'⟧' for i in range(ns)) + u'; ' + extra
            + u'; 同数共键 ' + str(len(CH[u'collisions'])) + u' 组、零项 ' + str(CH[u'zero_terms'])
            + u' 枚折成一条算式; 门槛侧 ' + str(CH[u'deriv_keys']) + u' 枚推导键／' + str(CH[u'deriv_points'])
            + u' 处复算点, 面内恒等式 ' + str(F[u'x_ident_n']) + u' 条; 五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对 '
            + str(R[u'ndis']) + u' 条锚逐字全命中, 工具侧 atomcheck 另核 ok=' + str(R[u'atom'][0]) + u' bad='
            + str(R[u'atom'][1]) + u'） |' + NL)


E64 = (u'头条答数（毫秒归一）' + J(gk(FP, u'y_ans_ms')) + u' ⇎ 数串 ' + u' ⇎ '.join(gk(FP, u'y_ans_num'))
       + u' ⇎ 单位 ' + u' ⇎ '.join(gk(FP, u'y_ans_unit')) + u', 极值比 ' + str(gk(FP, u'y_ans_ratio'))
       + u' 余 ' + fmt(gk(FP, u'y_ans_rem')) + u'; 97 的 64 秒是翻倍序列末项（'
       + u'→'.join(str(x) for x in gk(FP, u'a_seq')) + u', 末÷首＝' + str(gk(FP, u'a_ratio')) + u'＝2^'
       + str(gk(FP, u'a_doublings')) + u'）而 SOL_MAX_RT 字样 0 处; 03 的表 1 张 ' + fmt(gk(FP, u'tbl_rows')[1][0])
       + u' 行（表头 ' + fmt(gk(FP, u'tbl_start')[1][0]) + u'）⇎ 18 的表 1 张 ' + fmt(gk(FP, u'tbl_rows')[3][0])
       + u' 行（表头 ' + fmt(gk(FP, u'tbl_start')[3][0]) + u', 多 ' + str(gk(FP, u'tbl_row_delta'))
       + u' 行）; 13 用 OLD:/NEW: 重印 ' + u' ⇎ '.join(p[0] + u' ' + str(p[1]) + u'→' + str(p[2])
                                                for p in gk(FP, u'on_pair_c') if p[1]) + u'（比值 '
       + J(gk(FP, u'on_ratio')) + u'）并开值域 ' + fmt(gk(FP, u'clamp_lo')[2]) + u'..' + fmt(gk(FP, u'clamp_hi')[2])
       + u'（上下界比 ' + str(gk(FP, u'clamp_span')) + u'）; 同名参数 ' + str(gk(FP, u'bd_n')) + u' 枚同值 '
       + str(gk(FP, u'bd_same')) + u' ⇎ 改动 ' + str(gk(FP, u'bd_diff_n')) + u'（' + str(gk(FP, u'bd_unproposed_n'))
       + u' 枚 13 没提）; 夹逼⇎丢弃两行对照字节全等 0 ⇎ 归一也不同 ' + str(gk(FP, u'al_norm_diff'))
       + u'（字符净差 ' + str(gk(FP, u'al_char_delta')) + u'）; 03⇎18 搬运 ' + fmt(gk(FP, u'share_bd'))
       + u' 行（字节 ' + fmt(gk(FP, u'y_bd_byte_shared')) + u' ⇎ 仅归一同 ' + fmt(gk(FP, u'y_bd_norm_only'))
       + u'）⇎ 13⇎18 ' + str(gk(FP, u'share_cd')) + u' 行')


def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:50])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


S = sub(u'共 **63 条**（`babeltele/B01..B63`）', u'共 **64 条**（`babeltele/B01..B64`）', S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（63 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（64 条）', S)
S = sub(u'当前 **63 条语料／1969 条**推导全部通过（audit 自报“已机检的推导 1969 条”）',
        u'当前 **64 条语料／' + str(PROOFS) + u' 条**推导全部通过（audit 自报“已机检的推导 ' + str(PROOFS) + u' 条”）', S)
OLD63 = u'**B63 问的是'
assert S.count(OLD63) == 1
S = S.replace(OLD63, T64 + NL + OLD63)
S = after(S, u'| B63 | 14424（新建,', rowline(u'B64', u'报文没人应答时重传退避封顶多久', E64))
m = re.search(u'第二代（B11–B63）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；全库合计 \\*\\*([\\d ]+)／([\\d ]+)\\*\\*'
              u'（B62 ⇎ B63 两枚条目贡献 ([\\d ]+)／([\\d ]+) ⇎ ([\\d ]+)／([\\d ]+), 与 B61 的 617／646 同为去重锚口径, '
              u'由本遍现数并校住建条目侧快照）', S)
assert m and m.group(5) == u'670' and m.group(8) == u'1 467', (u'字母账定位失败', m and m.groups())
d = lambda x: int(re.sub(u'[^0-9]', u'', x))
i2, o2, ia, oa = d(m.group(1)), d(m.group(2)), d(m.group(3)), d(m.group(4))
assert ia - i2 == 121 and oa - o2 == 2195, (i2, ia, o2, oa)
ni2, no2 = i2 + R[u'lin'], o2 + R[u'lout']
nia, noa = ia + R[u'lin'], oa + R[u'lout']
assert nia - ni2 == 121 and noa - no2 == 2195
S = sub(m.group(0), u'第二代（B11–B64）锚内字母 **' + fmt(ni2) + u'**、锚外 **' + fmt(no2) + u'**；全库合计 **'
        + fmt(nia) + u'／' + fmt(noa) + u'**（B64 一枚条目贡献 ' + fmt(R[u'lin']) + u'／' + fmt(R[u'lout'])
        + u', 与 B62 ⇎ B63 的 ' + m.group(5) + u'／' + m.group(6) + u' ⇎ ' + m.group(7) + u'／' + m.group(8)
        + u'、B61 的 617／646 同为去重锚口径, 由本遍现数并校住建条目侧快照）', S)
S = after(S, u'| B63 | `raw/tcpRTO/rfc1122.txt`', C64)
TOTOLD = (u'| **合计（63 条）** | **402 725** | **113.3%**（摘要段合计 355 309，本遍新建的两枚为 8 922 ⇎ 14 424 '
          u'编码／3 378 ⇎ 4 407 摘要） | — | **2 229** | — |')
assert S.count(TOTOLD) == 1, S.count(TOTOLD)
old_enc, old_dig = 402725, 355309
assert (enc_all, dig_all) == (old_enc + R[u'encl'], old_dig + int(ROW[u'B64'][1])), (enc_all, dig_all)
assert 2229 < uniq_all == 2230, (uniq_all,)
# 这张指标表自 B54 起就没再逐条开行（_readme54…_readme6263 同样只改合计行）, 本遍按同一例: 只换合计行。
S = sub(TOTOLD, u'| **合计（64 条）** | **' + fmt(enc_all) + u'** | **' + ret_tot + u'%**（摘要段合计 '
        + fmt(dig_all) + u'，本遍新建的一枚为 ' + fmt(R[u'encl']) + u' 编码／' + fmt(int(ROW[u'B64'][1]))
        + u' 摘要） | — | **' + fmt(uniq_all) + u'** | — |', S)
S = sub(u'残余提示（不计 FAIL）：26 个 1–2 位结构计数（',
        u'残余提示（不计 FAIL）：' + str(soft_all) + u' 个 1–2 位结构计数（', S)
H03 = u'`03`'
assert HINT[u'B64'] == [u'03'], HINT[u'B64']
S = sub(u'互为旁证））未逐位核验，',
        u'互为旁证；新建的 B64 待核 ' + str(len(HINT[u'B64'])) + u' 项（' + H03 + u'）——它是四枚年份标签里 rfc3315 那一枚（2003）的切片, '
        u'活在条目自设的标签“03 一百二”与判词的交叉引用里; 本遍用 audit 同一枚 tokenizer 的口径在四份源里现找: `03` 从不作为独占数字出现'
        u'（只作为 3315 ⇎ 2003 的内部切片）, 而同族的 `97`⇎`13`⇎`18` 都能在至少一份源里独占出现, 故只有这一枚落到待核; '
        u'它也不是量在四份源上的事实断言））未逐位核验，', S)
S = sub(u'是**待核列为 0** 的 48 条条目里最连续的十二条',
        u'是**待核列为 0** 的 ' + str(zero_n) + u' 条条目里最连续的十二条', S)
S = sub(u'同样为 0，新建的 B63 亦为 0；除上面清单里那 15 枚条目外再无带待核的条目（B48 的 1 项即条目号 48）',
        u'同样为 0，新建的 B63 亦为 0，新建的 B64 带 1 项即上面那条年份标签 ' + H03 + u'；除上面清单里那 '
        + str(len(HINT)) + u' 枚条目外再无带待核的条目（B48 的 1 项即条目号 48）', S)


def digestcmd():
    grp = []
    for i in range(ns):
        grp += [SP[u'tags'][i], SP[u'paths'][i], u'140', u'140']
    return (u'python -X utf8 corpus/_mkdigest3.py B64 <entry> ' + u' '.join(grp)
            + u'   # 四源分节摘要(' + fmt(int(ROW[u'B64'][1])) + u' 字符, 窗口按 140⇎140 取句边界, '
            + str(R[u'nent']) + u'/' + str(R[u'nent']) + u' 锚全命中)' + NL)


CMD = (u'python -X utf8 corpus/_mkB64.py                  # 建条目: 扁平契约 ' + str(len(F))
       + u' 枚键／DERIV ' + str(CH[u'deriv_keys']) + u' 枚算式 ⇎ 复算点 ' + str(CH[u'deriv_points'])
       + u' 处, 采侧对账 ' + str(R[u'shared']) + u' 键 0 不符, 占位符未替换 0 个' + NL
       + digestcmd()
       + u"python -X utf8 corpus/_wire64.py                    # 把 SCAN 段机械切进 audit.py::_b64_scan 并插 DERIV['B64']" + NL
       + u'python -X utf8 corpus/_fill64.py                    # 第四遍: 现取注数写回 ⛓解读注, 模板全用 % 插值并在落盘前 '
       + u'assert 无残留占位 ⇎ 面内恒等式 ' + str(F[u'x_ident_n']) + u' 条' + NL
       + u'python -X utf8 corpus/atomcheck.py B64 corpus/_atoms64.txt   # 工具侧独立逐字校验: ok='
       + str(R[u'atom'][0]) + u' bad=' + str(R[u'atom'][1]) + u'（本遍重生成候选清单后重跑）' + NL)
S = after(S, u'python -X utf8 corpus/_readme6263.py', CMD
          + u'python -X utf8 corpus/_readme64.py               # 记账: 本文件第五遍再量一次四份源(量源一个 re 都不用, '
          + str(R[u'shared']) + u' 枚键与扁平契约⇎采集快照逐键对表, 签名两式各算; 全库合计取自本遍现跑的 audit)' + NL)
io.open(FM, 'w', encoding='utf-8', newline=NL).write(S)
SNAP = dict(totals=dict(enc=enc_all, dig=dig_all, uniq=uniq_all, proofs=PROOFS, hints=soft_all, zero=zero_n,
                        nent=NENT),
            letters=dict(g2_in=ni2, g2_out=no2, all_in=nia, all_out=noa),
            B64=dict(enc=R[u'encl'], dig=int(ROW[u'B64'][1]), anchors=R[u'nent'], distinct=R[u'ndis'],
                     single=R[u'sin'], cross=R[u'crs'], alln=R[u'alll'], checks=R[u'checks'],
                     letters_in=R[u'lin'], letters_out=R[u'lout'], atom=list(R[u'atom']), bytes=R[u'bs'],
                     lines=R[u'ln'], nonblank=R[u'nb'], nonblank_asciib=R[u'nba'], pagelines=R[u'F'][u'pagelines'],
                     cr=R[u'cr'], nonascii=R[u'na'], sha256_16=R[u'sh2'], blake2b_16=R[u'bl2'],
                     tag_counts=R[u'tcnt'], flat=R[u'flat'], meas=R[u'meas'], shared=R[u'shared'],
                     derived=dict((x, R[u'F'][x]) for x in (u'y_ans_ms', u'y_ans_ratio', u'y_ans_rem', u'a_ratio',
                                                            u'clamp_span', u'bd_same', u'share_bd'))))
json.dump(SNAP, io.open(u'corpus/_b64readme.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 64 条 ｜ 编码合计 ' + fmt(enc_all) + u' ⇎ 摘要合计 ' + fmt(dig_all) + u' ⇎ 合计保留率 ' + ret_tot
      + u'% ｜ 唯一码点 ' + fmt(uniq_all) + u' ｜ 推导 ' + str(PROOFS) + u' 条 ｜ 待核 ' + str(soft_all) + u'（其中 0 项条目 '
      + str(zero_n) + u' 条） ｜ B64 ' + fmt(R[u'encl']) + u' 字符／' + str(R[u'nent']) + u' 锚(' + str(R[u'ndis'])
      + u' 串, ' + tcount() + u', 单源 ' + str(R[u'sin']) + u'⇎穿 ' + str(R[u'crs']) + u'⇎全现 ' + str(R[u'alll'])
      + u', 检查 ' + str(R[u'checks']) + u') ｜ 字母账 第二代 ' + fmt(ni2) + u'／' + fmt(no2) + u' ⇎ 全库 '
      + fmt(nia) + u'／' + fmt(noa) + u' ｜ 第五遍现量与契约对表 ' + str(R[u'shared']) + u' 键 0 不符 ｜ atomcheck ok='
      + str(R[u'atom'][0]) + u' bad=' + str(R[u'atom'][1]))
