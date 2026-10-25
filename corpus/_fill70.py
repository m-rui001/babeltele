# -*- coding: utf-8 -*-
"""B70 的第四遍复测: 与采集侧 _pick70 ⇎ 建条目侧 _mkB70/_mk70emit ⇎ 门槛侧 audit.py::_b70_scan
换算法不换定义, 现算后把 ⛓解读注 写进条目。本遍的独立处:
①读面走 bytes 再 decode, 行数用 split('\n') 计格, 另立 count('\n')+1 一档与 splitlines() 一档比换页符坑;
②针计数一律 len(re.findall(re.escape(针), 面))(第二遍是非重叠游标 find 循环, 第一遍是重叠 str.find);
③义务语气走“按非字母切片后数整词”的 token 档, 与第二遍的 (?<![A-Za-z])W(?![A-Za-z]) 字面轨在纯字母词上等价;
④五枚进制/位宽读数由带捕获组的 findall 一次到位, 与第二遍的 read_after 游标不同路;
⑤带的定位先按 ANS 针在 enumerate(L) 里找答句行, 再取 ±20 行切体, 标题按 HEADND 正则现扫;
⑥搬运算账走 set 代数 ⇎ dict-of-set ⇎ itertools.combinations 三式互检, 容斥按 pres 权重手算;
⑦三面阶梯的壳行谓词 shell_line 从 _mkB70.py 源码原样 exec(它是文件级基础设施, 不是本遍要换的量),
  池/轴/锚池在其上用集合代数与逐字节双尺重算;
⑧锚归属走双轨: 原子串对原文件逐行 membership ⇎ 对折平面 membership, 两式同判才计数;
⑨恒等式与 DERIV 复算点从 _b70checks.json ⇎ _deriv70.json 回读后 eval, 不重打一遍算式。
每个键与 corpus/_b70flat.json 对拍, 值不符或键缺失一律先收集后汇总, 全零才落盘。"""
import io, os, re, sys, json, itertools, ast
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
ENTRY = u'%s/babeltele/B70_udp_checksum_mandatory_four_answers.md' % C
PATH = [u'%s/raw/udpCK/rfc768.txt' % C, u'%s/raw/tcpRTO/rfc1122.txt' % C,
        u'%s/raw/udpCK/rfc8200.txt' % C, u'%s/raw/udpCK/rfc6935.txt' % C]
LBL = [u'768', u'1122', u'8200', u'6935']
NSRC = 4
BAND = 20
POOLMIN = 40
APOOLMIN = 24
NL = u'\n'
FLAT = json.load(io.open(u'%s/_b70flat.json' % C, encoding='utf-8'))
CH = json.load(io.open(u'%s/_b70checks.json' % C, encoding='utf-8'))
JJ = json.load(io.open(u'%s/_deriv70.json' % C, encoding='utf-8'))

# 定义(不是本遍要换的量): 从 _mkB70.py 源码原样取 NEEDLE/HEADND/ANS 与 shell_line
MS = io.open(u'%s/_mkB70.py' % C, encoding='utf-8').read()
TAB = {}
for st in ast.parse(MS.replace(u'\nexec(', u'\n#exec(')).body:
    if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
        nm = st.targets[0].id
        if nm in (u'NEEDLE', u'HEADND', u'ANS'):
            try:
                TAB[nm] = ast.literal_eval(st.value)
            except Exception:
                pass
NEEDLE, HEADND, ANS = TAB[u'NEEDLE'], TAB[u'HEADND'], TAB[u'ANS']
_ns = {'re': re, 'u': None}
exec(re.search(u'def shell_line\\(l\\):.*?\n(?=SH =)', MS, re.S).group(0), _ns)
shell_line = _ns[u'shell_line']

D = {}
J = lambda xs: u' ⇎ '.join(u'%s' % x for x in xs)


def pn(s):
    return u' '.join(s.lower().split())


def cf(s):
    return u' '.join(s.split())


def cfa(s):
    return u' '.join(s.split())  # 保大小写折平 == _mkB70 的 FOLD


BYT = [io.open(p, 'rb').read() for p in PATH]
T = [b.decode('utf-8', 'replace') for b in BYT]
L = [t.split(u'\n') for t in T]
FO = [pn(t) for t in T]
FOLD = [cf(t) for t in T]
SH = [[x for x in L[i] if not shell_line(x)] for i in range(NSRC)]
SHF = [cf(u'\n'.join(sh)) for sh in SH]


def rc(t, nd):
    return len(re.findall(re.escape(nd), t))


def ub(t, w):
    return sum(1 for tk in re.split(u'[^A-Za-z]+', t) if tk == w)


def sub4(name, f):
    D[name] = [f(i) for i in range(NSRC)]


# ---------- 结构 / 版式 ----------
sub4(u'bytes', lambda i: len(BYT[i]))
sub4(u'chars', lambda i: len(T[i]))
sub4(u'lines', lambda i: len(L[i]))
sub4(u'nonblank', lambda i: len([x for x in L[i] if x.strip() != u'']))
sub4(u'maxlen', lambda i: max(len(x) for x in L[i]))
sub4(u'cr', lambda i: T[i].count(u'\r'))
sub4(u'ff', lambda i: len(T[i].split(u'\x0c')) - 1)
sub4(u'ff_only', lambda i: len([x for x in L[i] if x.strip() == u'\x0c']))
sub4(u'shell_n', lambda i: len(SH[i]))
D[u'shell_strip'] = [D[u'lines'][i] - D[u'shell_n'][i] for i in range(NSRC)]
sub4(u'nonascii', lambda i: len([c for c in T[i] if ord(c) > 127]))
sub4(u'bom', lambda i: 1 if BYT[i][:3] == b'\xef\xbb\xbf' else 0)
sub4(u'nonascii_extra', lambda i: sum(len(c.encode('utf-8')) - 1 for c in T[i] if ord(c) > 127))
D[u'byte_cp_delta'] = [D[u'bytes'][i] - D[u'chars'][i] for i in range(NSRC)]
sub4(u'nul_faces', lambda i: len([c for c in T[i] if c == u'\x00']))
sub4(u'digit_chars', lambda i: len([c for c in T[i] if c.isdigit()]))
sub4(u'dblspace', lambda i: len(re.findall(u'(?=  )', T[i])))
sub4(u'dblspace_norm', lambda i: len(re.findall(u'(?<=\\S) {2,}(?=\\S)', T[i])))
D[u'ascii_all'] = sum(1 for i in range(NSRC) if D[u'nonascii'][i] == 0)

# ---------- 三面阶梯(36 枚针) ----------
OWNER = dict((k, o) for o, k, _ in NEEDLE)
KEYS = [k for _, k, _ in NEEDLE]
SN, SNF, SNS, SNR = {}, {}, {}, {}
for o, k, nd in NEEDLE:
    fl = cf(nd)
    SN[k] = [len([x for x in L[i] if nd in x]) for i in range(NSRC)]
    SNF[k] = [rc(FOLD[i], fl) for i in range(NSRC)]
    SNS[k] = [rc(SHF[i], fl) for i in range(NSRC)]
    SNR[k] = [rc(FOLD[i], fl) for i in range(NSRC)]
D[u'needle_n'] = len(KEYS)
D[u'sn_strict_docs'] = [len([k for k in KEYS if OWNER[k] == i and SN[k][i] > 0]) for i in range(NSRC)]
D[u'sn_fold_docs'] = [len([k for k in KEYS if OWNER[k] == i and SNF[k][i]]) for i in range(NSRC)]
D[u'sn_sh_docs'] = [len([k for k in KEYS if OWNER[k] == i and SNS[k][i]]) for i in range(NSRC)]
D[u'sn_re_docs'] = [len([k for k in KEYS if OWNER[k] == i and SNR[k][OWNER[k]]]) for i in range(NSRC)]
D[u'fold_only_keys'] = [k for k in KEYS if sum(SN[k]) == 0 and SNF[k][OWNER[k]]]
D[u'fold_only_own'] = [len([k for k in KEYS if OWNER[k] == i and SN[k][i] == 0 and SNF[k][i]])
                      for i in range(NSRC)]
D[u'sh_lost_keys'] = [k for k in KEYS if SNF[k][OWNER[k]] and not SNS[k][OWNER[k]]]
D[u'ladder_monotone'] = 1 if all(D[u'sn_strict_docs'][i] + D[u'fold_only_own'][i]
                                == D[u'sn_fold_docs'][i] for i in range(NSRC)) else 0
D[u'sh_minus_fold'] = [D[u'sn_fold_docs'][i] - D[u'sn_sh_docs'][i] for i in range(NSRC)]
D[u'fold_line_zero'] = sum(1 for k in D[u'fold_only_keys'] if SN[k][OWNER[k]])
D[u'overlap_extra'] = sum(
    sum(len(re.findall(u'(?=' + re.escape(cf(nd)) + u')', FOLD[i])) - rc(FOLD[i], cf(nd))
        for i in range(NSRC))
    for _, k, nd in NEEDLE)
D[u're_eq_cur'] = 1 if all(SNR[k][OWNER[k]] == SNF[k][OWNER[k]] for k in KEYS) else 0
D[u'shared_verbatim'] = [k for k in KEYS if sum(1 for i in range(NSRC) if SNF[k][i]) >= 2]
D[u'cross_needle_n'] = len(D[u'shared_verbatim'])
D[u'cross_needles'] = D[u'shared_verbatim']
D[u'ladder_str'] = u'⇎'.join(u'%d' % x for x in D[u'sn_strict_docs'])
D[u'fold_only_str'] = u' ⇎ '.join(D[u'fold_only_keys'])
D[u'fold_only_n'] = len(D[u'fold_only_keys'])
D[u'line_hit_keys'] = [k for k in KEYS if SN[k][OWNER[k]]]
D[u'dead_needles'] = [k for k in KEYS if not SNF[k][OWNER[k]]]
for _, k, _ in NEEDLE:
    D[u'n_' + k] = SNF[k]
D[u'n_must_impl'] = D[u'n_z1122_must_impl']

# ---------- 义务语气: token 整词档 ⇎ 子串双尺 ----------
UP, LO, CI, TI = {}, {}, {}, {}
WORDS = (u'MUST', u'MAY', u'SHOULD')
for w in WORDS:
    UP[w] = [ub(T[i], w) for i in range(NSRC)]
    LO[w] = [ub(T[i], w.lower()) for i in range(NSRC)]
    CI[w] = [ub(T[i].lower(), w.lower()) for i in range(NSRC)]
    TI[w] = [ub(T[i], w[:1].upper() + w[1:].lower()) for i in range(NSRC)]
UPN = {}
for w in (u'MUST NOT', u'MAY NOT', u'SHOULD NOT'):
    UPN[w] = [rc(T[i], w) for i in range(NSRC)]
D[u'up_must_all'] = UP[u'MUST']
D[u'up_may'] = UP[u'MAY']
D[u'up_should'] = UP[u'SHOULD']
D[u'must_not'] = UPN[u'MUST NOT']
D[u'may_not'] = UPN[u'MAY NOT']
D[u'should_not'] = UPN[u'SHOULD NOT']
D[u'must_bare'] = [UP[u'MUST'][i] - UPN[u'MUST NOT'][i] for i in range(NSRC)]
D[u'low_must'] = LO[u'MUST']
D[u'low_may'] = LO[u'MAY']
D[u'low_should'] = LO[u'SHOULD']
D[u'ci_must'] = CI[u'MUST']
D[u'ci_may'] = CI[u'MAY']
D[u'ci_should'] = CI[u'SHOULD']
D[u'title_must'] = TI[u'MUST']
D[u'title_may'] = TI[u'MAY']
D[u'title_should'] = TI[u'SHOULD']
D[u'case_ledger'] = [sum(CI[w][i] - UP[w][i] - LO[w][i] - TI[w][i] for w in WORDS)
                    for i in range(NSRC)]
D[u'low_minus_up'] = [LO[u'MUST'][i] - UP[u'MUST'][i] for i in range(NSRC)]
D[u'up_zero_docs'] = [i for i in range(NSRC) if UP[u'MUST'][i] + UP[u'MAY'][i] + UP[u'SHOULD'][i] == 0]
D[u'up_zero_n'] = len(D[u'up_zero_docs'])
D[u'lo_minus_up'] = [LO[u'MUST'][i] - UP[u'MUST'][i] for i in range(NSRC)]
D[u'up_ledger'] = [UP[u'MUST'][i] - (D[u'must_bare'][i] + UPN[u'MUST NOT'][i]) for i in range(NSRC)]
D[u'req_word'] = [rc(T[i], u'REQUIRED') for i in range(NSRC)]
D[u'ck_word'] = [rc(T[i], u'checksum') for i in range(NSRC)]
D[u'ck_caps'] = [rc(T[i], u'Checksum') for i in range(NSRC)]
D[u'opt_word'] = [rc(T[i], u'optional') for i in range(NSRC)]
D[u'zero_word'] = [rc(T[i], u'zero') for i in range(NSRC)]
D[u'zero_ck'] = [rc(T[i], u'zero checksum') for i in range(NSRC)]
D[u'zero_hy'] = [rc(T[i], u'zero-checksum') for i in range(NSRC)]
D[u'zero_udp'] = [rc(T[i], u'zero UDP checksum') for i in range(NSRC)]
D[u'zero_forms'] = [D[u'zero_ck'][i] + D[u'zero_hy'][i] + D[u'zero_udp'][i] for i in range(NSRC)]
D[u'not_opt'] = [rc(FOLD[i], u'not optional') for i in range(NSRC)]
D[u'not_opt_line'] = [len([x for x in L[i] if u'not optional' in x]) for i in range(NSRC)]
D[u'never_opt'] = [rc(FOLD[i], u'never optional') for i in range(NSRC)]
D[u'udp_opt_line'] = [len([x for x in L[i] if u'UDP checksum' in x]) for i in range(NSRC)]
D[u'opt_line_ck'] = [len([x for x in L[i] if u'optional' in x and u'hecksum' in x]) for i in range(NSRC)]
D[u'pseudo_hy'] = [rc(T[i], u'pseudo-header') for i in range(NSRC)]
D[u'pseudo_sp'] = [rc(T[i], u'pseudo header') for i in range(NSRC)]
D[u'pseudo'] = [D[u'pseudo_hy'][i] + D[u'pseudo_sp'][i] for i in range(NSRC)]
D[u'pseudo_close'] = [D[u'pseudo_hy'][i] + D[u'pseudo_sp'][i] - D[u'pseudo'][i] for i in range(NSRC)]
D[u'port_word'] = [rc(T[i], u'Source Port') for i in range(NSRC)]

# ---------- 句内读数: 捕获组一次到位 ----------
NUM = {}
A1 = [(lambda m: m.group(1) if m else None)(re.search(re.escape(u"all 1's (") + u'(\\d+)\\)', FOLD[i]))
      for i in range(NSRC)]
HX = [(lambda m: m.group(1) if m else None)(re.search(re.escape(u'changed to hex ') + u'([0-9A-F]{4})', FOLD[i]))
      for i in range(NSRC)]
NUM['all1s_faces'] = [0 if x is None else int(x) for x in A1]
NUM['ffff_faces'] = [0 if x is None else int(x, 16) for x in HX]
NUM['all1s_dec'] = max(NUM['all1s_faces'])
NUM['ffff_8200'] = NUM['ffff_faces'][2]
NUM['ffff_6935'] = NUM['ffff_faces'][3]
NUM['radix_faces'] = [1 if (A1[i] or HX[i]) else 0 for i in range(NSRC)]
NUM['radix_forms'] = len([1 for f in (A1, HX) if any(f)])
NUM['cursor_miss'] = NUM['radix_faces'].count(0)
NUM['bits_768'] = int(re.search(re.escape(u'Checksum is the ') + u'(\\d+)-bit', FOLD[0]).group(1))
NUM['bits128_8200'] = int(re.search(re.escape(u'include the ') + u'(\\d+)-bit IPv6', FOLD[2]).group(1))
NUM['bits32_8200'] = int(re.search(re.escape(u'instead of ') + u'(\\d+)-bit IPv4', FOLD[2]).group(1))
NUM['mbtn_6935'] = int(re.search(re.escape(u'MUST follow requirements ') + u'(\\d+)', FOLD[3]).group(1))
NUM['mbtn_hi_6935'] = int(re.search(re.escape(u'MUST follow requirements 9, 10, and ') + u'(\\d+)', FOLD[3]).group(1))
NUM['ones_word'] = [rc(T[i], u"one's complement") for i in range(NSRC)]
NUM['ones_compl_fold'] = [rc(FOLD[i], u'complement') for i in range(NSRC)]
NUM['ffff_lit'] = [rc(T[i], u'FFFF') for i in range(NSRC)]
NUM['dec_lit'] = [rc(T[i], u'65535') for i in range(NSRC)]
NUM['radix_face_n'] = sum(NUM['radix_faces'])
for k, v in NUM.items():
    D[u'num_' + k] = v
D[u'bits_ratio128'] = NUM['bits128_8200'] // NUM['bits_768']
D[u'bits_ratio32'] = NUM['bits32_8200'] // NUM['bits_768']
D[u'bits_sum_8200'] = NUM['bits128_8200'] + NUM['bits32_8200']
D[u'mbtn_span_6935'] = NUM['mbtn_hi_6935'] - NUM['mbtn_6935']

# ---------- 头部动作字段: 现读 RFC 号集合 ⇎ 标题页年份 ----------
def hdr_ids(t, field):
    m = re.search(u'(?m)^' + field + u':\\s*(.+)$', t)
    if not m:
        return frozenset()
    return frozenset(int(x) for x in re.findall(u'\\d{3,5}', m.group(1)))


OBS = [hdr_ids(T[i], u'Obsoletes') for i in range(NSRC)]
UPD = [hdr_ids(T[i], u'Updates') for i in range(NSRC)]
D[u'obs_n'] = [len(s) for s in OBS]
D[u'upd_n'] = [len(s) for s in UPD]
D[u'target_ids'] = sorted(set().union(*[set(s) for s in OBS + UPD]))
D[u'target_n'] = len(D[u'target_ids'])
D[u'both_2460'] = 1 if (2460 in OBS[2] and 2460 in UPD[3]) else 0
D[u'obs_verb'] = [rc(T[i], u'Obsoletes') for i in range(NSRC)]
D[u'upd_verb'] = [rc(T[i], u'Updates') for i in range(NSRC)]
D[u'std_hdr'] = [len([1 for x in L[i] if re.match(u'^\\s*STD:\\s*\\d+', x)]) for i in range(NSRC)]
D[u'cat_std'] = [rc(T[i], u'Category: Standards Track') for i in range(NSRC)]
D[u'cat_lines'] = [len([1 for x in L[i] if re.match(u'^\\s*Category:', x)]) for i in range(NSRC)]

MON = u'January|February|March|April|May|June|July|August|September|October|November|December'
RYR = re.compile(u'(%s) +(\\d{4})\\s*$' % MON)


def hdr_year(lines):
    for x in lines[:60]:
        m = RYR.search(x.strip())
        if m:
            return (int(m.group(2)), m.group(1))
    return (None, None)


YR = [hdr_year(L[i]) for i in range(NSRC)]
D[u'years'] = [y for y, _ in YR]
D[u'months'] = [mo for _, mo in YR]
D[u'year_n'] = len([y for y in D[u'years'] if y])
order = sorted(range(NSRC), key=lambda i: D[u'years'][i])
D[u'year_perm'] = order
D[u'year_order'] = 1 if order == list(range(NSRC)) else 0
D[u'year_inversions'] = len([1 for a in range(NSRC) for b in range(a + 1, NSRC)
                            if D[u'years'][a] > D[u'years'][b]])
D[u'year_gap_6935_8200'] = D[u'years'][2] - D[u'years'][3]
D[u'year_gap'] = D[u'year_gap_6935_8200']
D[u'year_gaps'] = [D[u'years'][i + 1] - D[u'years'][i] for i in range(NSRC - 1)]

# ---------- 引用写法三式 ----------
CITE = {}
for n in (u'768', u'1122', u'8200', u'6935', u'2460', u'6936', u'793'):
    CITE['sp_' + n] = [rc(T[i], u'RFC ' + n) for i in range(NSRC)]
    CITE['hy_' + n] = [rc(T[i], u'RFC-' + n) for i in range(NSRC)]
    CITE['tk_' + n] = [rc(T[i], u'RFC' + n) for i in range(NSRC)]
    CITE['al_' + n] = [CITE['sp_' + n][i] + CITE['hy_' + n][i] + CITE['tk_' + n][i] for i in range(NSRC)]
for k in CITE:
    D['cite_' + k] = CITE[k]
D[u'cite_forms_2460'] = [len([x for x in (u'sp', u'hy', u'tk') if CITE[x + u'_2460'][i]]) for i in range(NSRC)]
D[u'cite_forms_close'] = [len(re.findall(u'RFC[ -]?2460', T[i])) - CITE['al_2460'][i] for i in range(NSRC)]
D[u'cite_self'] = [CITE['al_' + n][i] for i, n in enumerate((u'768', u'1122', u'8200', u'6935'))]
D[u'cite_8200_in_6935'] = CITE['al_8200'][3]
D[u'cite_6935_in_8200'] = CITE['al_6935'][2]
D[u'cite_dir_8200_to_6935'] = CITE['al_6935'][2]
D[u'cite_dir_6935_to_8200'] = CITE['al_8200'][3]
D[u'cite_2460_in_6935'] = CITE['al_2460'][3]
D[u'cite_2460_in_8200'] = CITE['al_2460'][2]
D[u'cite_6936'] = [CITE['al_6936'][i] for i in range(NSRC)]

# ---------- 答句邻域窗(±BAND 行) ----------
def ans_line(i):
    for n, x in enumerate(L[i], 1):
        if ANS[i] in x:
            return n
    return None


def sec_head(i):
    rx = re.compile(HEADND[i])
    for n, x in enumerate(L[i], 1):
        if rx.search(x.strip() if i == 0 else x):
            return n
    return None


def sec_window(i):
    a = ans_line(i)
    h = sec_head(i)
    lo = max(1, a - BAND)
    hi = min(len(L[i]), a + BAND)
    body = u'\n'.join(L[i][lo - 1:hi])
    outb = u'\n'.join(L[i][:lo - 1] + L[i][hi:])
    fb = cf(body)
    ob = cf(outb)
    return {u'head': L[i][h - 1].strip() if h else None, u'sec': h, u'ans': a,
            u'head_ln': h, u'start': lo, u'end': hi, u'rows': hi - lo + 1,
            u'chars': len(body), u'chars_out': len(outb),
            u'ck_in': rc(fb, u'checksum'), u'ck_out': rc(ob, u'checksum'),
            u'zero_in': rc(fb, u'zero'), u'zero_out': rc(ob, u'zero'),
            u'opt_in': rc(fb, u'optional'), u'opt_out': rc(ob, u'optional'),
            u'dig_in': len([c for c in body if c.isdigit()]),
            u'dig_out': len([c for c in outb if c.isdigit()]),
            u'up_in': ub(fb, u'MUST') + ub(fb, u'MAY') + ub(fb, u'SHOULD'),
            u'up_out': ub(ob, u'MUST') + ub(ob, u'MAY') + ub(ob, u'SHOULD')}


WIN = [sec_window(i) for i in range(NSRC)]
for k in (u'head', u'sec', u'ans', u'start', u'end', u'rows', u'chars', u'chars_out',
          u'ck_in', u'ck_out', u'zero_in', u'zero_out', u'opt_in', u'opt_out',
          u'dig_in', u'dig_out', u'up_in', u'up_out'):
    D[u'win_' + k] = [w[k] for w in WIN]
D[u'win_band'] = BAND
D[u'win_named'] = len([w for w in WIN if w['sec']])
D[u'win_close_ck'] = [WIN[i][u'ck_in'] + WIN[i][u'ck_out'] - rc(FOLD[i], u'checksum') for i in range(NSRC)]
D[u'win_close_zero'] = [WIN[i][u'zero_in'] + WIN[i][u'zero_out'] - rc(FOLD[i], u'zero') for i in range(NSRC)]
D[u'win_close_opt'] = [WIN[i][u'opt_in'] + WIN[i][u'opt_out'] - rc(FOLD[i], u'optional') for i in range(NSRC)]
D[u'win_close_up'] = [WIN[i][u'up_in'] + WIN[i][u'up_out']
                     - (ub(FOLD[i], u'MUST') + ub(FOLD[i], u'MAY') + ub(FOLD[i], u'SHOULD'))
                     for i in range(NSRC)]
D[u'win_close_dig'] = [WIN[i][u'dig_in'] + WIN[i][u'dig_out'] - D[u'digit_chars'][i] for i in range(NSRC)]
D[u'win_close_sum'] = (sum(D[u'win_close_ck']) + sum(D[u'win_close_zero']) + sum(D[u'win_close_opt'])
                      + sum(D[u'win_close_dig']) + sum(D[u'win_close_up']))
D[u'win_spans'] = [w[u'end'] - w[u'start'] + 1 for w in WIN]
D[u'win_share'] = len([w for w in WIN if w[u'head'] and u'hecksum' in w[u'head']])

# ---------- 共用长行池: set 代数 ⇎ dict-of-set ⇎ itertools 三式互检 ----------
def pl(i):
    return [x for x in SH[i] if len(pn(x)) >= POOLMIN]


GN = [set(pn(x) for x in pl(i)) for i in range(NSRC)]
GRA = [set(pl(i)) for i in range(NSRC)]
PAIR = list(itertools.combinations(range(NSRC), 2))
TRI = list(itertools.combinations(range(NSRC), 3))
D[u'pair_share'] = [len(GN[a] & GN[b]) for a, b in PAIR]
# 逐字节交: 归一同形且原行在对面也逐字节出现的条数
D[u'pair_byte'] = [sum(1 for s in (GN[a] & GN[b])
                  if any(pn(x) == s and x in GRA[b] for x in pl(a))) for a, b in PAIR]
D[u'pair_norm_only'] = [D[u'pair_share'][k] - D[u'pair_byte'][k] for k in range(len(PAIR))]
D[u'pair_close'] = sum(D[u'pair_share']) - sum(D[u'pair_byte']) - sum(D[u'pair_norm_only'])
D[u'pair_nonzero'] = len([1 for x in D[u'pair_share'] if x])
ALLP = set().union(*GN)
CC = defaultdict(set)
for i in range(NSRC):
    for x in pl(i):
        n = pn(x)
        if len(n) >= POOLMIN:
            CC[n].add(i)
D[u'pool_n'] = len(ALLP)
D[u'pool_tier'] = [len([n for n in ALLP if len([i for i in range(NSRC) if n in GN[i]]) == k])
                  for k in range(1, NSRC + 1)]
D[u'pool_tier_close'] = sum(D[u'pool_tier']) - D[u'pool_n']
D[u'pool_4'] = D[u'pool_tier'][3]
D[u'pool_3'] = D[u'pool_tier'][2]
D[u'pool_2'] = D[u'pool_tier'][1]
D[u'pool_1'] = D[u'pool_tier'][0]
pres = dict((a, tuple(i for i in range(NSRC) if a in GN[i])) for a in ALLP)
_t1 = sum(len(v) for v in pres.values())
_t2 = sum(len(v) * (len(v) - 1) // 2 for v in pres.values())
_t3 = sum(len(v) * (len(v) - 1) * (len(v) - 2) // 6 for v in pres.values())
_t4 = len([v for v in pres.values() if len(v) == NSRC])
D[u'pool_incl'] = [_t1, _t2, _t3, _t4]
D[u'union_incl'] = _t1 - _t2 + _t3 - _t4
D[u'union_close'] = D[u'pool_n'] - D[u'union_incl']
D[u'tri_share'] = [len(GN[a] & GN[b] & GN[c]) for a, b, c in TRI]
D[u's3_examples'] = sorted([a for a, v in pres.items() if len(v) >= 3])
D[u's3_docs'] = 3 if D[u'pool_3'] else 0
letters = re.compile(u'[A-Za-z]')
D[u'pool_letters'] = len([a for a in ALLP if letters.search(a)])
D[u'pool_border'] = D[u'pool_n'] - D[u'pool_letters']

# ---------- 写法分家轴 ----------
axis = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
for a, v in pres.items():
    if len(v) < 2:
        continue
    xs = []
    for i in v:
        xs += [x for x in SH[i] if pn(x) == a]
    if len(set(xs)) < 2:
        continue
    o, p = xs[0], xs[1]
    if len(o) == len(p) and o != p and all(x.lower() == y.lower() for x, y in zip(o, p)):
        axis[u'case'] += 1
    elif (u'-' in o) != (u'-' in p):
        axis[u'hyph'] += 1
    elif len(re.split(u' +', o.strip())) == len(re.split(u' +', p.strip())):
        axis[u'space'] += 1
    else:
        axis[u'multi'] += 1
D[u'axis_counts'] = axis
D[u'axis_total'] = sum(axis.values())
D[u'axis_close'] = D[u'axis_total'] - sum(D[u'pair_norm_only'])
D[u'axis_str'] = u'⇎'.join(u'%s%d' % (a, axis[a]) for a in (u'case', u'hyph', u'space', u'multi'))
D[u'axis_str_n'] = len([a for a in (u'case', u'hyph', u'space', u'multi') if axis[a]])

# ---------- 锚候选池 ----------
apool = []
for i in range(NSRC):
    for x in SH[i]:
        if len(pn(x)) >= APOOLMIN and letters.search(x):
            apool.append((pn(x), i))
AP = defaultdict(set)
for a, i in apool:
    AP[a].add(i)
D[u'apool_n'] = len(AP)
D[u'apool_raw_n'] = len(apool)
D[u'apool_uniq'] = len(AP)
D[u'apool_face_raw'] = [len([1 for a, k in apool if k == i]) for i in range(NSRC)]
D[u'apool_tag_n'] = [len([a for a, v in AP.items() if i in v]) for i in range(NSRC)]
D[u'apool_dup'] = [D[u'apool_face_raw'][i] - D[u'apool_tag_n'][i] for i in range(NSRC)]
D[u'apool_tag_close'] = sum(D[u'apool_tag_n']) + sum(D[u'apool_dup']) - D[u'apool_raw_n']
D[u'apool_tier'] = [len([a for a, v in AP.items() if len(v) == n]) for n in range(1, NSRC + 1)]
D[u'apool_pairs'] = sum(D[u'apool_tag_n'])
D[u'apool_weight'] = sum(D[u'apool_tier'][n] * (n + 1) for n in range(NSRC))
D[u'apool_tier_close'] = D[u'apool_weight'] - D[u'apool_pairs']
D[u'apool_maxlen'] = max(len(a) for a in AP)

# ---------- 段落三段对照(8200 ⇎ 6935 引文 ⇎ 6935 替代段) ----------
def fmap(i):
    mp = []
    off = 0
    first = True
    for n, x in enumerate(L[i], 1):
        s = cf(x)
        if not s:
            continue
        if not first:
            off += 1
        first = False
        mp.append((off, n))
        off += len(s)
    return mp


FMP = [fmap(i) for i in range(NSRC)]


def line_of(i, a):
    r = 0
    for o, n in FMP[i]:
        if o <= a:
            r = n
        else:
            break
    return r


def blk(i, start, end):
    a = FOLD[i].find(start)
    b = FOLD[i].find(end, a)
    return cf(FOLD[i][a:b + len(end)]), line_of(i, a), line_of(i, b + len(end) - 1)


P82, P82_LO, P82_HI = blk(2, u'Unlike IPv4, the default behavior', u'zero checksum and should log the error.')
P6Q, P6Q_LO, P6Q_HI = blk(3, u'Unlike IPv4, when UDP packets are', u'checksum, and should log the error.')
P6R, P6R_LO, P6R_HI = blk(3, u'Whenever originating a UDP packet for a port', u'zero checksum and SHOULD log the error.')
D[u'blk_lo'] = [P82_LO, P6Q_LO, P6R_LO]
D[u'blk_hi'] = [P82_HI, P6Q_HI, P6R_HI]
D[u'blk_rows'] = [P82_HI - P82_LO + 1, P6Q_HI - P6Q_LO + 1, P6R_HI - P6R_LO + 1]
D[u'blk_words'] = [len(P82.split()), len(P6Q.split()), len(P6R.split())]
W82, W6Q, W6R = P82.lower().split(), P6Q.lower().split(), P6R.lower().split()
D[u'w82_only'] = sorted(set(w for w in W82 if w not in W6Q))
D[u'w6q_only'] = sorted(set(w for w in W6Q if w not in W82))
D[u'w82_only_n'] = len(D[u'w82_only'])
D[u'w6q_only_n'] = len(D[u'w6q_only'])
D[u'w_common'] = len(set(W82) & set(W6Q))
D[u'w_row_close'] = D[u'w82_only_n'] + D[u'w_common'] - len(set(W82))
D[u'lead_insert'] = rc(P82, u'the default behavior') - rc(P6Q, u'the default behavior')
D[u'repl_bydefault'] = rc(P6R, u'MUST by default')
D[u'p82_bydefault'] = rc(P82, u'by default')
D[u'comma_82'] = rc(P82, u'checksum, and should')
D[u'comma_q69'] = rc(P6Q, u'checksum, and should')
D[u'comma_diff'] = D[u'comma_q69'] - D[u'comma_82']


def suf(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def pre(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


D[u'suf_82_q69'] = suf(W82, W6Q)
D[u'pre_82_q69'] = pre(W82, W6Q)
D[u'suf_82_6r'] = suf(W82, W6R)
D[u'pre_82_6r'] = pre(W82, W6R)
D[u'tone_up_repl'] = ub(P6R, u'MUST') + ub(P6R, u'MAY') + ub(P6R, u'SHOULD')
D[u'tone_lo_repl'] = ub(P6R, u'must') + ub(P6R, u'may') + ub(P6R, u'should')
D[u'tone_lo_82'] = ub(P82, u'must') + ub(P82, u'should')
D[u'tone_up_82'] = ub(P82, u'MUST') + ub(P82, u'SHOULD')
D[u'tone_lo_q69'] = ub(P6Q, u'must') + ub(P6Q, u'should')
D[u'tone_up_q69'] = ub(P6Q, u'MUST') + ub(P6Q, u'SHOULD')
D[u'tone_swap'] = D[u'tone_up_repl'] - D[u'tone_lo_82']
D[u'tone_rev_close'] = D[u'tone_up_82'] + D[u'tone_lo_repl'] + D[u'tone_up_q69']
D[u'verb_updates_6935'] = rc(FOLD[3], u'This specification updates IPv6')
D[u'verb_updates_8200'] = rc(FOLD[2], u'This specification updates IPv6')
VU_CI = [rc(FO[i], u'this specification updates ipv6') for i in range(NSRC)]
D[u'verb_updates_ci'] = VU_CI
D[u'verb_up'] = [D[u'verb_updates_6935'], D[u'verb_updates_8200']]
D[u'verb_track_close'] = sum(abs(VU_CI[i] - (D[u'verb_updates_6935'] if i == 3 else
                                            D[u'verb_updates_8200'] if i == 2 else 0)) for i in range(NSRC))
D[u'delete_order'] = rc(FOLD[3], u'fourth bullet should be deleted')
D[u'delete_order_8200'] = rc(FOLD[2], u'fourth bullet should be deleted')
D[u'quote_marker_6935'] = rc(T[3], u'[RFC2460]')


def ln_of(i, nd):
    return line_of(i, FOLD[i].find(nd))


D[u'ln_ctrl_1122'] = ln_of(1, u'MUST default to checksumming on')
D[u'ln_opt_1122'] = ln_of(1, u'the UDP checksum is optional')
D[u'ln_impl_1122'] = ln_of(1, u'A host MUST implement the facility')
D[u'ctrl_opt_span'] = D[u'ln_opt_1122'] - D[u'ln_ctrl_1122']
D[u'impl_opt_span'] = D[u'ln_opt_1122'] - D[u'ln_impl_1122']
D[u'opt_vs_must_dir'] = 1 if D[u'ctrl_opt_span'] > 0 else 0
OPTPREV = []
for i in range(NSRC):
    ws = []
    for m in re.finditer(u'optional', FOLD[i]):
        seg = FOLD[i][max(0, m.start() - 30):m.start()].strip().split()
        ws.append(seg[-1].strip(u'.,;:()').lower() if seg else u'')
    OPTPREV.append(Counter(ws).most_common(3))
D[u'opt_prev'] = OPTPREV
D[u'opt_prev_n'] = [len(OPTPREV[i]) for i in range(NSRC)]
D[u'must_default_str'] = u'MUST default to checksumming on'

# ---------- CLOSE 判据 ----------
D[u'base_value_agree'] = 0 if NUM['all1s_dec'] == NUM['ffff_8200'] == NUM['ffff_6935'] else 1
D[u'base_absent_768'] = 0 if NUM['radix_faces'][0] == 0 else 1
D[u'radix_three'] = 0 if sum(NUM['radix_faces']) == 3 else 1
D[u'bits128_close'] = 0 if NUM['bits_768'] * D[u'bits_ratio128'] == NUM['bits128_8200'] else 1
D[u'bits32_close'] = 0 if NUM['bits_768'] * D[u'bits_ratio32'] == NUM['bits32_8200'] else 1
D[u'year_perm_close'] = 0 if D[u'year_inversions'] == 1 else 1
D[u'target_agree'] = 0 if D[u'both_2460'] and D[u'target_n'] == 1 else 1
D[u'cite_dir_unique'] = 0 if (D[u'cite_dir_8200_to_6935'] and not D[u'cite_dir_6935_to_8200']) else 1
D[u'fold_split_8200'] = 1 if (D[u'not_opt'][2] and not D[u'not_opt_line'][2]) else 0
D[u'std_no_upper'] = 1 if (D[u'std_hdr'][2] and D[u'up_must_all'][2] + D[u'up_may'][2] + D[u'up_should'][2] == 0) else 0
D[u'low_only_8200'] = 1 if (D[u'low_must'][2] and not D[u'up_must_all'][2]) else 0

# ---------- 锚双轨归属 ----------
TT = io.open(ENTRY, encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
CIT = re.findall(u'⟦(' + u'|'.join(LBL) + u')⟧⟨([^⟨⟩]+)⟩', enc)
DIS = []
for _, a in CIT:
    if a not in DIS:
        DIS.append(a)
IDX = dict((t, n) for n, t in enumerate(LBL))
IDX = dict((t, n) for n, t in enumerate(LBL))
LINE_HIT = dict((a, tuple(i for i in range(NSRC) if a in L[i])) for a in DIS)
FOLD_HIT = dict((a, tuple(i for i in range(NSRC) if pn(a) and pn(a) in FO[i])) for a in DIS)
D[u'anchor_total'] = len(CIT)
D[u'anchor_distinct'] = len(DIS)
D[u'anchor_err'] = len([1 for t, a in CIT if not pn(a) or pn(a) not in FO[IDX[t]]])
D[u'anchor_single'] = len([a for a in DIS if len(FOLD_HIT[a]) == 1])
D[u'anchor_cross'] = len([a for a in DIS if 1 < len(FOLD_HIT[a]) < NSRC])
D[u'anchor_all4'] = len([a for a in DIS if len(FOLD_HIT[a]) == NSRC])
D[u'checks'] = len(DIS) * NSRC
D[u'track_agree'] = len([a for a in DIS if LINE_HIT[a] == FOLD_HIT[a]])
D[u'track_split'] = [a for a in DIS if LINE_HIT[a] != FOLD_HIT[a]]
D[u'enc_chars'] = len(enc.replace(NL, u''))
D[u'nsrc'] = NSRC
for t in LBL:
    D[u'tag_' + t] = len(re.findall(u'⟦%s⟧' % t, enc))

# ---------- 对账 ⇎ 恒等式 ⇎ DERIV 复跑 ----------
D[u'zid_n'] = len(CH[u'zid'])
D[u'x_ident_n'] = len(CH[u'zid'])
D[u'scalar_clos_n'] = len(CH[u'zid'])
NS = dict(FLAT)
NS.update({k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in D.items()})
# FLAT 里 target_ids 是 list, frozenset 已序列化; D 与 FLAT 的 list 逐元素比
def _jr(x):
    return json.loads(json.dumps(x))


NSV = dict(FLAT)
NSV.update(D)
V = lambda k, i=None: (NSV[k] if i is None else NSV[k][i])
ZRES = [(e, w, eval(e, {u'B70V': V})) for e, w in CH[u'zid']]
ZFAIL = [(w, r) for e, w, r in ZRES if r != 0]
D[u'zid_fail'] = [w for e, w, r in ZRES if r != 0]
D[u'scalar_clos_sum'] = len([1 for e, w, r in ZRES if r == 0])
D[u'list_clos_n'] = len([k for k in FLAT if (u'_close' in k or u'_ledger' in k) and isinstance(FLAT[k], list)])
MISS = [k for k in D if k not in FLAT]
BAD = [(k, _jr(D[k]), _jr(FLAT[k])) for k in D if k in FLAT and _jr(D[k]) != _jr(FLAT[k])]
UNCOVER = [k for k in FLAT if k not in D]
DFAIL = []
for kk, v in JJ.items():
    try:
        g = eval(v, {}, {u'B70V': V})
    except Exception as e:
        DFAIL.append((kk, repr(e)))
        continue
    if str(g) != kk and repr(g) != kk:
        DFAIL.append((kk, v, str(g)))
assert not ZFAIL, ZFAIL[:4]
assert not DFAIL, DFAIL[:4]
assert not BAD, BAD[:6]
assert not D[u'anchor_err'] and D[u'fold_line_zero'] == 0
assert sum(D[u'up_ledger']) == 0 and sum(D[u'case_ledger']) == 0 and D[u'win_close_sum'] == 0
assert D[u'pair_close'] == 0 and D[u'union_close'] == 0 and D[u'pool_tier_close'] == 0
assert D[u'apool_tag_close'] == 0 and D[u'apool_tier_close'] == 0 and D[u'axis_close'] == 0
assert D[u'ladder_monotone'] == 1 and D[u're_eq_cur'] == 1 and sum(D[u'sh_minus_fold']) == 0
assert D[u'base_value_agree'] == 0 and D[u'radix_three'] == 0 and D[u'year_perm_close'] == 0
assert D[u'target_agree'] == 0 and D[u'cite_dir_unique'] == 0 and D[u'both_2460'] == 1

# ---------- ⛓解读注 ----------
SHARED_AD = sorted([x for x in pl(2) if pn(x) in GN[2] & GN[3] and x in SH[3]])
L2 = []
A = L2.append
A(u"第四遍(`corpus/_fill70.py`)换算法不换定义地重跑一遍: 读面走 bytes 再 decode ⇎ 行数按 `split('\\n')` 计格"
  u" ⇎ 针计数按 `len(re.findall(re.escape(针), 面))`(第二遍是非重叠游标 find, 第一遍是重叠 str.find)"
  u" ⇎ 义务语气按“非字母切片后数整词”的 token 档 ⇎ 进制/位宽读数由带捕获组的 findall 一次到位"
  u" ⇎ 带定位先在 `enumerate(L)` 里找答句行再取 ±%d 行 ⇎ 搬运算账走 set 代数 ⇎ 锚归属走逐行⇎折平双轨。" % BAND)
A(u"本遍复算 %d 个键(扁平表 %d 键中覆盖 %d 枚 ⇎ 本遍独有 %d ⇎ 未复算 %d ⇎ 逐值不符 %d); "
  u"面内恒等式 %d 条在本注读数上重跑全为真(通过 %d); DERIV %d 条复算点重跑全对(引用 %d 处)。" % (
      len(D), len(FLAT), len([k for k in D if k in FLAT]), len(MISS), len(UNCOVER), len(BAD),
      len(CH[u'zid']), D[u'scalar_clos_sum'], len(JJ),
      sum(len(v.split(u'B70V(')) - 1 for v in JJ.values())))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"行数⇎换行", u"`split('\\n')` 计格 ⇎ `count('\\n')+1` ⇎ 换页符按 `split('\\x0c')-1`",
     u"行数 %s ⇎ 换页符 %s ⇎ 整行只有换页符 %s ⇎ 剥壳剥掉 %s 行" % (
         J(D[u'lines']), J(D[u'ff']), J(D[u'ff_only']), J(D[u'shell_strip'])),
     u"四份都带换页符(%s 枚), 壳轨对每份都非空转; 8200 剥掉 %d 行 ⇎ 1122 剥掉 %d 行——"
     u"壳谓词是从 _mkB70 源码原样 exec 的文件级基础设施, 不是本遍要换的量" % (
         J(D[u'ff']), D[u'shell_strip'][2], D[u'shell_strip'][1])),
    (u"编码层", u"字节面看 BOM ⇎ 码位面数非 ASCII ⇎ utf-8 逐字符加字节",
     u"BOM %s ⇎ 非 ASCII %s ⇎ 加字节 %s ⇎ 字节−码位 %s ⇎ 纯 ASCII %d 份" % (
         J(D[u'bom']), J(D[u'nonascii']), J(D[u'nonascii_extra']), J(D[u'byte_cp_delta']), D[u'ascii_all']),
     u"四份全纯 ASCII(非 ASCII 全零⇒字节−码位差全零), 与 9293 那代带 BOM 的排版面不同——"
     u"这一条的分歧不来自任何编码层, 只来自词面本身"),
    (u"三面阶梯", u"逐行 in ⇎ 全篇折平成员(findall) ⇎ 摘壳折平",
     u"逐行 %s ⇎ 折平 %s ⇎ 摘壳 %s ⇎ 正则 %s" % (
         J(D[u'sn_strict_docs']), J(D[u'sn_fold_docs']), J(D[u'sn_sh_docs']), J(D[u'sn_re_docs'])),
     u"阶梯单调 %d: 只在折平存在的 %d 枚是跨行句子; 最刺眼的是 8200——逐行档 %d 枚 ⇎ 折平档 %d 枚, "
     u"整段答句被行界劈开, 只按逐行口径搜会把这份读成“没写这条规则”; 摘壳相对折平 %s(壳行里没有答句)" % (
         D[u'ladder_monotone'], D[u'fold_only_n'], D[u'sn_strict_docs'][2], D[u'sn_fold_docs'][2],
         J(D[u'sh_minus_fold']))),
    (u"两轨判定", u"正则字面轨(findall) ⇎ 非重叠游标轨 ⇎ 重叠口径",
     u"两轨相等 %d ⇎ 重叠多余 %d ⇎ 死针 %s" % (D[u're_eq_cur'], D[u'overlap_extra'], D[u'dead_needles']),
     u"这一批针里没有自重叠针⇒重叠口径与非重叠口径逐枚同值; 没有一枚针在自己份面上读不到(死针空)"),
    (u"句内读数", u"捕获组 findall `all 1's (\\d+)` ⇎ `changed to hex ([0-9A-F]{4})`",
     u"十进制面 %s ⇎ hex 折十 %s ⇎ 给进制份数 %d ⇎ 游标落空份数 %d" % (
         J(D[u'num_all1s_faces']), J(D[u'num_ffff_faces']), D[u'num_radix_face_n'], D[u'num_cursor_miss']),
     u"同一枚补码值被写成两种进制: 1122 面上十进制 %d ⇎ 8200/6935 的 hex 折十各 %d, 三读一致(闭合 %d); "
     u"768 只写 all ones 一个数字都不给(进制游标全落空, 缺席判定 %d)" % (
         D[u'num_all1s_dec'], D[u'num_ffff_8200'], D[u'base_value_agree'], D[u'base_absent_768'])),
    (u"位宽", u"`Checksum is the (\\d+)-bit` ⇎ `include the (\\d+)-bit IPv6` ⇎ `instead of (\\d+)-bit IPv4`",
     u"768 校验和 %d 位 ⇎ 8200 伪头 128⇎32 位 ⇎ 比值 %d/%d ⇎ 之和 %d ⇎ 整除闭合 %d/%d" % (
         D[u'num_bits_768'], D[u'bits_ratio128'], D[u'bits_ratio32'], D[u'bits_sum_8200'],
         D[u'bits128_close'], D[u'bits32_close']),
     u"IPv6 把伪头地址从 32 位换成 128 位, 两枚都是 768 那枚 16 位校验和字段的整数倍(倍率 %d ⇎ %d)"),
    (u"义务语气", u"token 整词档(非字母切片) ⇎ 子串双尺",
     u"大写 MUST %s ⇎ 裸 %s ⇎ MUST NOT %s ⇎ MAY %s ⇎ SHOULD %s ⇎ 小写 must %s ⇎ 无视大小写 must %s" % (
         J(D[u'up_must_all']), J(D[u'must_bare']), J(D[u'must_not']), J(D[u'up_may']),
         J(D[u'up_should']), J(D[u'low_must']), J(D[u'ci_must'])),
     u"大写账 %s ⇎ 大小写四轨账 %s 全归零。大写义务词整份为零的 %d 份: 768 与 8200——"
     u"8200 带 STD 头(逐份 %s)却是现行标准而全篇零大写(%d)/只小写(%d): 那条 IPv6 规则整句用 must/should 写; "
     u"1122 也不是纯命令式, 小写 must %d ⇎ 大写 MUST %d 差 %d 枚" % (
         J(D[u'up_ledger']), J(D[u'case_ledger']), D[u'up_zero_n'], J(D[u'std_hdr']),
         D[u'std_no_upper'], D[u'low_only_8200'], D[u'low_must'][1], D[u'up_must_all'][1], D[u'lo_minus_up'][1])),
    (u"optional 贴谁", u"全篇枚数 ⇎ 与 checksum 同枚 ⇎ not optional 折平⇎逐行双档",
     u"optional %s ⇎ 且 ck 同行 %s ⇎ not optional 折平 %s ⇎ 逐行 %s ⇎ never optional %s" % (
         J(D[u'opt_word']), J(D[u'opt_line_ck']), J(D[u'not_opt']), J(D[u'not_opt_line']), J(D[u'never_opt'])),
     u"768 面上 optional 一枚都不与 checksum 同行(%d)——它唯一的 optional 贴在 Source Port; "
     u"1122 的 optional 散在全文(全篇 %d 枚里带内只 %d 枚) ⇎ 8200 的聚在规则周围(全篇 %d 枚里带内 %d 枚); "
     u"“never optional”全库恰 %d 枚落在 1122 的 TCP 侧(与同文 UDP 那句 optional 对照)" % (
         D[u'opt_line_ck'][0], D[u'opt_word'][1], D[u'win_opt_in'][1], D[u'opt_word'][2],
         D[u'win_opt_in'][2], sum(D[u'never_opt']))),
    (u"三段词集", u"段落边界由折平游标现定 ⇎ 偏移映回原行 ⇎ 词集去重共有",
     u"段起 %s 止 %s 行 %s 词 %s ⇎ 共有 %d ⇎ 8200 独有 %d ⇎ 6935 引文独有 %d ⇎ 共尾 %d/%d 共头 %d/%d" % (
         J(D[u'blk_lo']), J(D[u'blk_hi']), J(D[u'blk_rows']), J(D[u'blk_words']),
         D[u'w_common'], D[u'w82_only_n'], D[u'w6q_only_n'], D[u'suf_82_q69'], D[u'suf_82_6r'],
         D[u'pre_82_q69'], D[u'pre_82_6r']),
     u"词集账闭合 %d; 8200 与 6935 引的旧原文共尾 %d 枚词逐字同 ⇎ 共头只 %d 枚——引导语被换: "
     u"插入 the default behavior … is that(闭合 %d); 逗号分家 “checksum, and should” %d ⇎ %d 枚(差 %d)" % (
         D[u'w_row_close'], D[u'suf_82_q69'], D[u'pre_82_q69'], D[u'lead_insert'],
         D[u'comma_82'], D[u'comma_q69'], D[u'comma_diff'])),
    (u"语气换向", u"替代段大写档 ⇎ 8200 段小写档 ⇎ 反向三项和",
     u"替代段大写 %d ⇎ 8200 段小写 %d ⇎ 换向差 %d ⇎ 反向和(8200大写/替代段小写/引文大写) %d⇎%d⇎%d=闭合 %d" % (
         D[u'tone_up_repl'], D[u'tone_lo_82'], D[u'tone_swap'], D[u'tone_up_82'], D[u'tone_lo_repl'],
         D[u'tone_up_q69'], D[u'tone_rev_close']),
     u"语气换向只朝一个方向(换向差 %d, 枚数一枚不动只换字面档); 反向读三项之和 %d——读到 0 才是三段各只活一种语气, "
     u"是整段重写而非对翻; 6935 还在替代段插 by default %d 枚 ⇎ 8200 %d 枚, 把“必须丢弃”降成默认条件" % (
         D[u'tone_swap'], D[u'tone_rev_close'], D[u'repl_bydefault'], D[u'p82_bydefault'])),
    (u"谁改谁", u"Obsoletes:/Updates: 头现读号集合 ⇎ 标题页年份逐行尾锚定",
     u"obs %s ⇎ upd %s ⇎ 目标号 %s ⇎ 双向命中 2460 %d ⇎ 年份 %s ⇎ 年距 %s ⇎ 排序索引 %s" % (
         J(D[u'obs_n']), J(D[u'upd_n']), D[u'target_ids'], D[u'both_2460'],
         J(D[u'years']), J(D[u'year_gaps']), J(D[u'year_perm'])),
     u"目标一致闭合 %d ⇎ 年份倒序 %d 处(判定闭合 %d): 6935 的大写替代段(2013)早于 8200 的小写默认行为(2017), "
     u"倒序那对年距 %d——语气换代不按时间单向推进, 这件事在四份自己的字节里就读得出; "
     u"该删指令只在 6935 出现 %d 次 ⇎ 8200 面 %d 次, 互引单向 %d⇎%d(闭合 %d)" % (
         D[u'target_agree'], D[u'year_inversions'], D[u'year_perm_close'], D[u'year_gap_6935_8200'],
         D[u'delete_order'], D[u'delete_order_8200'], D[u'cite_dir_8200_to_6935'],
         D[u'cite_dir_6935_to_8200'], D[u'cite_dir_unique'])),
    (u"引用三式", u"RFC 空格 ⇎ RFC- 短横 ⇎ RFC 连写三式并计, 子串轨 ⇎ 一条正则族两轨",
     u"2460 合计 %s ⇎ 写法族账 %s ⇎ 2460 写法族数 8200 %d ⇎ 6935 %d" % (
         J(D[u'cite_al_2460']), J(D[u'cite_forms_close']), D[u'cite_forms_2460'][2], D[u'cite_forms_2460'][3]),
     u"6935 用连写式把被改的那份钉在括号里(%d 枚 [RFC2460]); 三代文书引用体例分家: "
     u"768 自指空格式 %d ⇎ 1122 面上短横式引 793 %d ⇎ IPv6 两份面上 793 各 %d/%d 枚" % (
         D[u'quote_marker_6935'], D[u'cite_sp_768'][0], D[u'cite_hy_793'][1],
         D[u'cite_al_793'][2], D[u'cite_al_793'][3])),
    (u"窗五轨", u"±%d 行邻域窗按小节标题定位, 带内+带外=全篇(校验和⇎零⇎可选⇎大写义务⇎数字)" % BAND,
     u"节行 %s ⇎ 答句行 %s ⇎ 窗 %s 至 %s ⇎ 行数 %s" % (
         J(D[u'win_sec']), J(D[u'win_ans']), J(D[u'win_start']), J(D[u'win_end']), J(D[u'win_rows'])),
     u"四份都命到标题 %d ⇎ 带 Checksum 字样 %d 个; 五轨合计闭合 %d——本遍用 enumerate 现定位答句行, "
     u"与第二遍的 find 游标不同路仍逐枚相等" % (D[u'win_named'], D[u'win_share'], D[u'win_close_sum'])),
    (u"搬运⇎重写", u"set 代数: 归一交 ⇎ 逐字节双尺交 ⇎ 仅归一 ⇎ 容斥按 pres 权重手算",
     u"长行池 %d ⇎ 分档 %s ⇎ 六对归一 %s ⇎ 逐字节 %s ⇎ 仅归一 %s" % (
         D[u'pool_n'], J(D[u'pool_tier']), J(D[u'pair_share']), J(D[u'pair_byte']), J(D[u'pair_norm_only'])),
     u"配对闭合 %d ⇎ 容斥闭合 %d ⇎ 分档闭合 %d; 逐字搬运在这条里是句子级而非整行级: "
     u"含字母的 ≥%d 列长行 %d 条里两份同现 %d ⇎ 四份同现 %d; 唯一非零的那对是 8200⇎6935(归一 %d), "
     u"其 %d 条逐字节同形全是 IETF 许可/状态样板与 [RFC2460]/[RFC6936] 参考文献行, 只 %d 条差缩进(那条 FFFF 句)" % (
         D[u'pair_close'], D[u'union_close'], D[u'pool_tier_close'], POOLMIN, D[u'pool_letters'],
         D[u'pool_2'], D[u'pool_4'], D[u'pair_share'][5], D[u'pair_byte'][5], D[u'pair_norm_only'][5])),
    (u"写法分家轴", u"归一同形而逐字节不同的共用长行按“差在哪”分四桶",
     u"四桶 %s ⇎ 非零档 %d ⇎ 轴账闭合 %d ⇎ 锚池分档 %s ⇎ 标签 %s" % (
         D[u'axis_str'], D[u'axis_str_n'], D[u'axis_close'], J(D[u'apool_tier']), J(D[u'apool_tag_n'])),
     u"只有空格档非零(%d 条=那条只差缩进的 FFFF 句), 大小写⇎短横⇎多字差三档皆空; "
     u"锚候选池两本账闭合 %d/%d(按标签 %d ⇎ 按份数加权 %d)" % (
         D[u'axis_counts'][u'space'], D[u'apool_tag_close'], D[u'apool_tier_close'],
         D[u'apool_pairs'], D[u'apool_weight'])),
    (u"锚双轨", u"一枚锚同时按“等于某原文件行”⇎“其归一式落在折平面里”两种成员判",
     u"正文 %d 处 ⇎ 去重 %d 串 ⇎ 两轨同判 %d ⇎ 分歧 %d" % (
         D[u'anchor_total'], D[u'anchor_distinct'], D[u'track_agree'], len(D[u'track_split'])),
     u"归属错配 %d ⇎ 一源 %d ⇎ 跨源 %d ⇎ 四源 %d; 跨源 %d 枚全部落在 6935 面(替代段把前文句子收进自己, 分歧在句内); "
     u"编码区 %d 字符 ⇎ 归属检查 %d 次" % (
         D[u'anchor_err'], D[u'anchor_single'], D[u'anchor_cross'], D[u'anchor_all4'],
         D[u'anchor_cross'], D[u'enc_chars'], D[u'checks'])),
]
for a1, b1, c1, d1 in rows:
    A(u"| %s | %s | %s | %s |" % (a1, b1, c1, d1))
A(u"")
A(u"### 本注的判断")
A(u"四份文书对“一条 UDP 报文的校验和是不是非算不可、算出零值怎么办”给的不是同一个问题的四个答案, 而是把"
  u"“必选与否 ⇎ 零值怎么办 ⇎ 语气的字面档 ⇎ 谁改谁”四件事拆给了四份: "
  u"768 全篇零枚大写义务词、也不用“可选”表述(optional 一词 %d 枚且 %d 枚与 checksum 同行, 唯一那枚贴在 Source Port), "
  u"零值只写成“发送端没算”, 算出零就发 all ones 而不给进制; "
  u"1122 把同一件事拆三层——能力 MUST implement ⇎ 每报文 MAY optionally ⇎ 默认 MUST default to checksumming on, "
  u"而“默认必须开”离同节那句 the UDP checksum is optional 只差 %d 行(离“能力 MUST”差 %d 行), 同一份还把 TCP 写成 never optional; "
  u"8200 说 IPv6 上“不是可选、且这是默认行为”(插入 the default behavior … is that), 全篇零大写 ⇎ 小写 must %d 枚, "
  u"是带 STD: 号的现行标准却用小写写义务; "
  u"6935 一边把那份小写原文整段引出判它该删(%d 次) ⇎ 一边把同一条规则换成大写义务 %d 枚并插 by default %d 枚, "
  u"再拿 MAY enable zero-checksum mode 开出口、MUST follow [RFC6936] 关出口。" % (
      D[u'opt_word'][0], D[u'opt_line_ck'][0], D[u'ctrl_opt_span'], D[u'impl_opt_span'],
      D[u'low_must'][2], D[u'delete_order'], D[u'tone_up_repl'], D[u'repl_bydefault']))
A(u"于是任何“取最新/取最全”的合并都会丢东西: 按年份最新取 8200(2017), 就丢掉 6935(2013)那枚把义务降成默认的 by default 手术——"
  u"而 6935 恰恰比它更新的那份早四年(年份倒序 %d 处), 语气换代不按时间单向推进; 按语气最硬取 1122 的 MUST, "
  u"就丢掉 8200 把它软成小写 must、6935 又把它重新大写化这一来回。逐字搬运在此条里几乎为零(六对里五对整行为零同形, "
  u"唯一非零的 8200⇎6935 那 %d 条逐字节同形全是许可样板与参考文献行, 真正差别的 %d 条只差缩进), "
  u"分歧全在句子内部: 引导语、逗号(%d⇎%d 枚)、大小写语气档(%d 枚 ⇎ %d 枚)。" % (
      D[u'year_inversions'], D[u'pair_byte'][5], D[u'pair_norm_only'][5],
      D[u'comma_82'], D[u'comma_q69'], D[u'tone_lo_82'], D[u'tone_up_repl']))
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; rfc-editor.org 此刻给这四份挂的现行状态页与勘误页; "
  u"被 8200 废止、被 6935 更新且被 6935 引用的那份 RFC 2460 本身不在库内(本注只能读四份里对它的那处引用, 读不出它自己怎么写这条); "
  u"此后哪份在途文书又动了零校验这一段; 现网 IPv6 栈实际丢不丢零校验和的 UDP 报文(“默认丢 ⇎ 隧道旁路 ⇎ 可套接字选项覆盖”这类是实现事实, 不是文书事实); "
  u"“768 早于 RFC 2119 语气表”这类年代关系只能由常识给出, 在库四份文件自身不写。")
A(u"以上量要么在本机之外、要么随实现与站点漂移, 复算通道里没有它们的位置; 门槛只认在库字节。")
NEW = u"## ⛓解读注" + NL + NL + NL.join(L2) + NL
i = TT.index(u"## ⛓解读注")
out = TT[:i] + NEW
assert out.count(u"## ⛓解读注") == 1
T2 = ENTRY + u'.tmp'
io.open(T2, u'w', encoding=u'utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"⛓解读注 已写入 %s ｜ 表 %d 行 ｜ 注区 %d 字符 ｜ 复算 %d 键 ⇎ 不符 %d ⇎ 独有 %d ⇎ 未复算 %d ⇎ 恒等式 %d/%d ⇎ DERIV %d 全对"
      % (ENTRY, len(rows), len(NEW), len(D), len(BAD), len(MISS), len(UNCOVER),
         D[u'scalar_clos_sum'], len(CH[u'zid']), len(JJ)))
