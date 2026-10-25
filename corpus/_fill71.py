# -*- coding: utf-8 -*-
"""B71 的第四遍复测: 与采集侧 _pick71 ⇎ 建条目侧 _mkB71/_mk71emit ⇎ 门槛侧 audit.py::_b71_scan
换算法不换定义, 现算后把 ⛓解读注 写进条目。本遍的独立处:
①读面走 bytes 再 decode, 行数同时按 split('\n') 计格 ⇎ count('\n')+1 计换行 ⇎ splitlines 计行三档对拍,
  换页符按 split('\x0c')-1(第二遍是游标 find 循环);
②针计数一律 len(re.findall(re.escape(针), 面))(第二遍是非重叠游标, 第一遍是 str.count),
  重叠口径另用 (?=针) 前瞻档算差;
③义务语气走“按非字母切片后数整词”的 token 档, 与第二遍的 (?<![A-Za-z])W(?![A-Za-z]) 字面轨在纯字母词上等价;
④字段改名走“按非词字符切片后数整 token”的档(_hint ⇎ _plain 两式各自成 token), 与第二遍的词界正则不同路,
  子串档另用 str.count, 三式相加才等于 ticket_lifetime 的全部出现;
⑤四枚读数(604800 ⇎ 括注日数 ⇎ 24-hour ⇎ 2^32)由带捕获组的 findall 一次到位, 与第二遍的 read_after 游标不同路;
⑥带的定位先在 enumerate(L) 里找答句行再取 ±20 行切体, 标题按 HEADND 现扫;
⑦段落的起止行由折平偏移经 bisect(bisect_right) 映回原行号(第二遍是线性游标扫描);
⑧搬运算账走 set 代数 ⇎ dict-of-set ⇎ itertools.combinations 三式互检, 容斥按 pres 权重手算;
⑨壳行谓词 shell_line 从 _mkB71.py 源码原样 exec(文件级基础设施, 不是本遍要换的量),
  池/轴/锚池在其上用集合代数与逐字节双尺重算;
⑩锚归属走双轨: 原子串对原文件逐行 membership ⇎ 对折平面 membership, 两式同判才计数;
恒等式与 DERIV 复算点从 _b71checks.json ⇎ _deriv71.json 回读后 eval, 不重打一遍算式。
每个键与 corpus/_b71flat.json 对拍, 值不符或键缺失一律先收集后汇总, 全零才落盘。"""
import io, os, re, sys, json, itertools, ast, bisect
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
ENTRY = u'%s/babeltele/B71_tls_ticket_lifetime_four_answers.md' % C
PATH = [u'%s/raw/tlsTicket/rfc4507.txt' % C, u'%s/raw/tlsTicket/rfc5077.txt' % C,
        u'%s/raw/ietf/rfc8446.txt' % C, u'%s/raw/tlsTicket/rfc9001.txt' % C]
LBL = [u'4507', u'5077', u'8446', u'9001']
NSRC = 4
BAND = 20
POOLMIN = 40
APOOLMIN = 24
NL = u'\n'
FLAT = json.load(io.open(u'%s/_b71flat.json' % C, encoding='utf-8'))
CH = json.load(io.open(u'%s/_b71checks.json' % C, encoding='utf-8'))
JJ = json.load(io.open(u'%s/_deriv71.json' % C, encoding='utf-8'))

# 定义(不是本遍要换的量): 从 _mkB71.py 源码原样取 NEEDLE/HEADND/ANSND 与 shell_line
MS = io.open(u'%s/_mkB71.py' % C, encoding='utf-8').read()
TAB = {}
for st in ast.parse(MS.replace(u'\nexec(', u'\n#exec(')).body:
    if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
        nm = st.targets[0].id
        if nm in (u'NEEDLE', u'HEADND', u'ANSND'):
            try:
                TAB[nm] = ast.literal_eval(st.value)
            except Exception:
                pass
NEEDLE = TAB[u'NEEDLE']
HEADND = TAB[u'HEADND']
ANSND = TAB[u'ANSND']
_ns = {'re': re}
exec(re.search(u'def shell_line\\(l\\):.*?\n(?=SH =)', MS, re.S).group(0), _ns)
shell_line = _ns[u'shell_line']

D = {}
J = lambda xs: u' ⇎ '.join(u'%s' % x for x in xs)


def pn(s):
    return u' '.join(s.lower().split())


def cf(s):
    return u' '.join(s.split())


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


def tk(t, w):
    return sum(1 for s in re.split(u'[^A-Za-z0-9_]+', t) if s == w)


def sub4(name, f):
    D[name] = [f(i) for i in range(NSRC)]


# ---------- 结构 / 版式 ----------
sub4(u'bytes', lambda i: len(BYT[i]))
sub4(u'chars', lambda i: len(T[i]))
sub4(u'lines', lambda i: len(L[i]))
D[u'lines_nl'] = [T[i].count(u'\n') + 1 for i in range(NSRC)]
D[u'lines_split'] = [len(T[i].splitlines()) for i in range(NSRC)]
D[u'tail_nl'] = [1 if T[i].endswith(u'\n') else 0 for i in range(NSRC)]
sub4(u'nonblank', lambda i: len([x for x in L[i] if x.strip() != u'']))
sub4(u'maxlen', lambda i: max(len(x) for x in L[i]))
sub4(u'cr', lambda i: T[i].count(u'\r'))
sub4(u'ff', lambda i: len(T[i].split(u'\x0c')) - 1)
sub4(u'ff_only', lambda i: len([x for x in L[i] if x.strip() == u'\x0c']))
sub4(u'ff_exact', lambda i: len([x for x in L[i] if x == u'\x0c']))
sub4(u'shell_n', lambda i: len(SH[i]))
D[u'shell_strip'] = [D[u'lines'][i] - D[u'shell_n'][i] for i in range(NSRC)]
sub4(u'nonascii', lambda i: len([c for c in T[i] if ord(c) > 127]))
sub4(u'bom', lambda i: 1 if BYT[i][:3] == b'\xef\xbb\xbf' else 0)
sub4(u'nonascii_extra', lambda i: sum(len(c.encode('utf-8')) - 1 for c in T[i] if ord(c) > 127))
D[u'byte_cp_delta'] = [D[u'bytes'][i] - D[u'chars'][i] for i in range(NSRC)]
sub4(u'nul_faces', lambda i: len([c for c in T[i] if c == u'\x00']))
sub4(u'digit_chars', lambda i: len([c for c in T[i] if c.isdigit()]))
sub4(u'dblspace', lambda i: len(re.findall(u'(?=  )', T[i])))
D[u'ascii_all'] = sum(1 for i in range(NSRC) if D[u'nonascii'][i] == 0)
D[u'lines_split_close'] = sum(D[u'lines_nl'][i] - D[u'tail_nl'][i] + D[u'ff'][i]
                              - D[u'lines_split'][i] for i in range(NSRC))
TXT = set()
for _r, _d, _f in os.walk(u'%s/raw' % C):
    for x in _f:
        if x.startswith(u'rfc') and x.endswith(u'.txt'):
            TXT.add(x)
D[u'in_repo_2246'] = 1 if u'rfc2246.txt' in TXT else 0
D[u'in_repo_4346'] = 1 if u'rfc4346.txt' in TXT else 0
D[u'in_repo_5246'] = 1 if u'rfc5246.txt' in TXT else 0
D[u'in_repo_n'] = len(TXT)

# ---------- 三面阶梯针 ----------
OWNER = dict((k, o) for o, k, _ in NEEDLE)
KEYS = [k for _, k, _ in NEEDLE]
SN, SNF, SNS, SNR, CNT = {}, {}, {}, {}, {}
for o, k, nd in NEEDLE:
    fl = cf(nd)
    SN[k] = [len([x for x in L[i] if nd in x]) for i in range(NSRC)]
    SNF[k] = [rc(FOLD[i], fl) for i in range(NSRC)]
    SNS[k] = [rc(SHF[i], fl) for i in range(NSRC)]
    SNR[k] = [rc(FOLD[i], fl) for i in range(NSRC)]
    CNT[k] = [len(re.findall(u'(?=' + re.escape(fl) + u')', FOLD[i])) - SNR[k][i]
              for i in range(NSRC)]
D[u'needle_n'] = len(KEYS)
D[u'needles_owned'] = [len([k for k in KEYS if OWNER[k] == i]) for i in range(NSRC)]
D[u'sn_strict_docs'] = [len([k for k in KEYS if OWNER[k] == i and SN[k][i] > 0]) for i in range(NSRC)]
D[u'sn_fold_docs'] = [len([k for k in KEYS if OWNER[k] == i and SNF[k][i]]) for i in range(NSRC)]
D[u'sn_sh_docs'] = [len([k for k in KEYS if OWNER[k] == i and SNS[k][i]]) for i in range(NSRC)]
D[u'sn_re_docs'] = [len([k for k in KEYS if OWNER[k] == i and SNR[k][OWNER[k]]]) for i in range(NSRC)]
D[u'fold_only_keys'] = [k for k in KEYS if sum(SN[k]) == 0 and SNF[k][OWNER[k]]]
D[u'fold_only_own'] = [len([k for k in KEYS if OWNER[k] == i and SN[k][i] == 0 and SNF[k][i]])
                       for i in range(NSRC)]
D[u'fold_only_n'] = len(D[u'fold_only_keys'])
D[u'fold_only_str'] = u' ⇎ '.join(D[u'fold_only_keys'])
D[u'sh_lost_keys'] = [k for k in KEYS if SNF[k][OWNER[k]] and not SNS[k][OWNER[k]]]
D[u'ladder_monotone'] = 1 if all(D[u'sn_strict_docs'][i] + D[u'fold_only_own'][i]
                                 == D[u'sn_fold_docs'][i] for i in range(NSRC)) else 0
D[u'sh_minus_fold'] = [D[u'sn_fold_docs'][i] - D[u'sn_sh_docs'][i] for i in range(NSRC)]
D[u'fold_line_zero'] = sum(1 for k in D[u'fold_only_keys'] if SN[k][OWNER[k]])
D[u'overlap_extra'] = sum(sum(CNT[k]) for k in KEYS)
D[u're_eq_cur'] = 1 if all(SNR[k][OWNER[k]] == SNF[k][OWNER[k]] for k in KEYS) else 0
D[u'line_hit_keys'] = [k for k in KEYS if SN[k][OWNER[k]]]
D[u'dead_needles'] = [k for k in KEYS if not SNF[k][OWNER[k]]]
D[u'shared_verbatim'] = [k for k in KEYS if sum(1 for i in range(NSRC) if SNF[k][i]) >= 2]
D[u'cross_needles'] = D[u'shared_verbatim']
D[u'cross_needle_n'] = len(D[u'shared_verbatim'])
D[u'zero_carry_sh'] = [SNS[u'z4507_zero_reserved'][1], SNS[u'z5077_zero_reserved'][0]]
D[u'zero_carry_fold'] = [SNF[u'z4507_zero_reserved'][1], SNF[u'z5077_zero_reserved'][0]]
for _, k, _ in NEEDLE:
    D[u'n_' + k] = SNF[k]

# ---------- 义务语气: token 整词档 ----------
UP, LO, CI, TI, UPN = {}, {}, {}, {}, {}
WORDS = (u'MUST', u'MAY', u'SHOULD')
for w in WORDS:
    UP[w] = [ub(T[i], w) for i in range(NSRC)]
    LO[w] = [ub(T[i], w.lower()) for i in range(NSRC)]
    CI[w] = [ub(T[i].lower(), w.lower()) for i in range(NSRC)]
    TI[w] = [ub(T[i], w[:1].upper() + w[1:].lower()) for i in range(NSRC)]
for w in (u'MUST NOT', u'MAY NOT', u'SHOULD NOT'):
    UPN[w] = [T[i].count(w) for i in range(NSRC)]
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
D[u'up_ledger'] = [UP[u'MUST'][i] - (D[u'must_bare'][i] + UPN[u'MUST NOT'][i]) for i in range(NSRC)]
D[u'should_delete'] = [rc(FOLD[i], u'client should delete') for i in range(NSRC)]
D[u'must_cap_face'] = [rc(FOLD[i], u'must not use any value greater than') for i in range(NSRC)]

# ---------- 字段改名: token 整档 ⇎ 词界正则 ⇎ 子串档 ----------
D[u'fld_hint'] = [tk(T[i], u'ticket_lifetime_hint') for i in range(NSRC)]
D[u'fld_plain'] = [tk(T[i], u'ticket_lifetime') for i in range(NSRC)]
D[u'fld_sub'] = [T[i].count(u'ticket_lifetime') for i in range(NSRC)]
D[u'fld_close'] = [D[u'fld_sub'][i] - (D[u'fld_hint'][i] + D[u'fld_plain'][i])
                   for i in range(NSRC)]
D[u'uint32_hint'] = [len([1 for x in L[i] if u'uint32 ticket_lifetime_hint;' in x]) for i in range(NSRC)]
D[u'uint32_plain'] = [len([1 for x in L[i] if u'uint32 ticket_lifetime;' in x]) for i in range(NSRC)]
for w, nm in ((u'hint', u'hint_word'), (u'zero', u'zero_word'), (u'unspecified', u'unspec_word'),
              (u'discard', u'discard_low'), (u'Discard', u'discard_cap'),
              (u'immediately', u'imm_word'), (u'seven days', u'seven_days'), (u'week', u'week_word'),
              (u'24-hour', u'd24_hour'), (u'reuse', u'reuse_word'), (u'lifetime', u'lifetime_word'),
              (u'NewSessionTicket', u'session_ticket')):
    D[nm] = [T[i].count(w) for i in range(NSRC)]
for w, nm in ((u'shorter or longer', u'orlonger'), (u'valid for a shorter period', u'shorter_only'),
              (u'relative to when the ticket is received', u'relative_in'),
              (u'from the time of ticket issuance', u'from_issuance'),
              (u'when the ticket is received', u'recv_time')):
    D[nm] = [rc(FOLD[i], w) for i in range(NSRC)]

# ---------- 句内读数: 捕获组一次到位 ----------
def grab(t, pre, pat, base=10):
    m = re.search(re.escape(pre) + pat, t)
    return None if not m else int(m.group(1), base)


NUM = {}
NUM['cap_faces'] = [0 if grab(FOLD[i], u'value greater than ', u'(\\d+)') is None
                    else grab(FOLD[i], u'value greater than ', u'(\\d+)') for i in range(NSRC)]
NUM['cap_days'] = [0 if grab(FOLD[i], u'seconds (', u'(\\d+)(?= days)') is None
                   else grab(FOLD[i], u'seconds (', u'(\\d+)(?= days)') for i in range(NSRC)]
NUM['cap_lit'] = [T[i].count(u'604800') for i in range(NSRC)]
NUM['d24'] = grab(FOLD[0], u'longer than the ', u'(\\d+)(?=-hour)')
NUM['day_seconds'] = NUM['d24'] * 3600
NUM['cap_ratio'] = NUM['cap_faces'][2] // NUM['day_seconds']
NUM['cap_remainder'] = NUM['cap_faces'][2] % NUM['day_seconds']
NUM['cap_present_docs'] = len([x for x in NUM['cap_faces'] if x])
NUM['mod_pow'] = grab(FOLD[2], u'modulo 2^', u'(\\d+)')
NUM['ms_factor'] = 1000
NUM['sec_ms_close'] = NUM['mod_pow']
NUM['tls13_refs'] = [T[i].count(u'[TLS13]') for i in range(NSRC)]
for k, v in NUM.items():
    D[u'num_' + k] = v

# ---------- 头部动作字段 ⇎ 标题页年份 ⇎ 类目 ----------
def hdr_ids(t, field):
    for x in t.split(u'\n'):
        s = x.strip()
        if s.lower().startswith(field.lower() + u':'):
            return frozenset(int(v) for v in re.findall(u'\\d{3,5}', s.split(u':', 1)[1]))
    return frozenset()


OBS = [hdr_ids(T[i], u'Obsoletes') for i in range(NSRC)]
UPD = [hdr_ids(T[i], u'Updates') for i in range(NSRC)]
D[u'obs_set_5077'] = sorted(OBS[1])
D[u'obs_set_8446'] = sorted(OBS[2])
D[u'upd_set_8446'] = sorted(UPD[2])
D[u'obs_n'] = [len(s) for s in OBS]
D[u'upd_n'] = [len(s) for s in UPD]
D[u'target_ids'] = sorted(set().union(*[set(s) for s in OBS + UPD]))
D[u'target_n'] = len(D[u'target_ids'])
D[u'obs_verb'] = [T[i].count(u'Obsoletes') for i in range(NSRC)]
D[u'upd_verb'] = [T[i].count(u'Updates') for i in range(NSRC)]
D[u'upd_line'] = [len([1 for x in L[i] if x.strip().startswith(u'Updates:')]) for i in range(NSRC)]
D[u'cat_std'] = [T[i].count(u'Category: Standards Track') for i in range(NSRC)]
D[u'cat_hdr'] = [len([1 for x in L[i] if x.strip().startswith(u'Category:')]) for i in range(NSRC)]
D[u'issn'] = [T[i].count(u'ISSN: 2070-1721') for i in range(NSRC)]
D[u'exp_n'] = [T[i].count(u'Experimental') for i in range(NSRC)]
D[u'std_hdr'] = [len([1 for x in L[i] if re.match(u'^\\s*STD:\\s*\\d+', x)]) for i in range(NSRC)]

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
D[u'year_gaps'] = [D[u'years'][i + 1] - D[u'years'][i] for i in range(NSRC - 1)]

# ---------- 引用写法三式 ----------
CITE = {}
for n in (u'4507', u'5077', u'8446', u'9001', u'2246', u'4346', u'5246', u'6961', u'5705', u'6066'):
    CITE['sp_' + n] = [T[i].count(u'RFC ' + n) for i in range(NSRC)]
    CITE['hy_' + n] = [T[i].count(u'RFC-' + n) for i in range(NSRC)]
    CITE['tk_' + n] = [T[i].count(u'RFC' + n) for i in range(NSRC)]
    CITE['al_' + n] = [CITE['sp_' + n][i] + CITE['hy_' + n][i] + CITE['tk_' + n][i]
                      for i in range(NSRC)]
for k in CITE:
    D['cite_' + k] = CITE[k]
D[u'cite_forms_2246'] = [len([x for x in (u'sp', u'hy', u'tk') if CITE[x + u'_2246'][i]])
                         for i in range(NSRC)]
D[u'cite_forms_close'] = [len(re.findall(u'RFC[ -]?2246', T[i])) - CITE['al_2246'][i]
                          for i in range(NSRC)]
D[u'cite_self'] = [CITE['al_' + n][i] for i, n in enumerate(LBL)]
D[u'cite_4507_in_5077'] = CITE['al_4507'][1]
D[u'cite_5077_in_8446'] = CITE['al_5077'][2]
D[u'cite_4507_in_8446'] = CITE['al_4507'][2]
D[u'cite_8446_in_9001'] = CITE['al_8446'][3]
D[u'cite_9001_in_8446'] = CITE['al_9001'][2]
D[u'cite_dir_5077_to_8446'] = CITE['al_5077'][2]
D[u'cite_dir_8446_to_9001'] = CITE['al_9001'][2]
D[u'cite_dir_9001_to_8446'] = CITE['al_8446'][3]
D[u'cite_8446_in_9001_sp'] = CITE['sp_8446'][3]

# ---------- 答句邻域窗 ----------
def ans_line(i):
    for n, x in enumerate(L[i], 1):
        if ANSND[i] in x:
            return n
    return None


def sec_head(i):
    rx = re.compile(HEADND[i])
    for n, x in enumerate(L[i], 1):
        if rx.search(x):
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
    fo = cf(outb)
    return {u'head': L[i][h - 1].strip() if h else None, u'sec': h, u'ans': a, u'head_ln': h,
            u'start': lo, u'end': hi, u'rows': hi - lo + 1,
            u'chars': len(body), u'chars_out': len(outb),
            u'lt_in': rc(fb, u'lifetime'), u'lt_out': rc(fo, u'lifetime'),
            u'zero_in': rc(fb, u'zero'), u'zero_out': rc(fo, u'zero'),
            u'cap_in': rc(fb, u'604800'), u'cap_out': rc(fo, u'604800'),
            u'reuse_in': rc(fb, u'reuse'), u'reuse_out': rc(fo, u'reuse'),
            u'dig_in': len([c for c in body if c.isdigit()]),
            u'dig_out': len([c for c in outb if c.isdigit()]),
            u'up_in': ub(fb, u'MUST') + ub(fb, u'MAY') + ub(fb, u'SHOULD'),
            u'up_out': ub(fo, u'MUST') + ub(fo, u'MAY') + ub(fo, u'SHOULD')}


WIN = [sec_window(i) for i in range(NSRC)]
for k in (u'head', u'sec', u'ans', u'start', u'end', u'rows', u'chars', u'chars_out', u'lt_in',
          u'lt_out', u'zero_in', u'zero_out', u'cap_in', u'cap_out', u'reuse_in', u'reuse_out',
          u'dig_in', u'dig_out', u'up_in', u'up_out'):
    D[u'win_' + k] = [w[k] for w in WIN]
D[u'win_band'] = BAND
D[u'win_named'] = len([w for w in WIN if w[u'sec']])
D[u'win_ans_named'] = len([w for w in WIN if w[u'ans']])
D[u'win_close_lt'] = [WIN[i][u'lt_in'] + WIN[i][u'lt_out'] - rc(FOLD[i], u'lifetime')
                      for i in range(NSRC)]
D[u'win_close_zero'] = [WIN[i][u'zero_in'] + WIN[i][u'zero_out'] - rc(FOLD[i], u'zero')
                        for i in range(NSRC)]
D[u'win_close_cap'] = [WIN[i][u'cap_in'] + WIN[i][u'cap_out'] - rc(FOLD[i], u'604800')
                       for i in range(NSRC)]
D[u'win_close_reuse'] = [WIN[i][u'reuse_in'] + WIN[i][u'reuse_out'] - rc(FOLD[i], u'reuse')
                         for i in range(NSRC)]
D[u'win_close_dig'] = [WIN[i][u'dig_in'] + WIN[i][u'dig_out'] - D[u'digit_chars'][i]
                       for i in range(NSRC)]
D[u'win_close_sum'] = (sum(D[u'win_close_lt']) + sum(D[u'win_close_zero'])
                       + sum(D[u'win_close_cap']) + sum(D[u'win_close_reuse'])
                       + sum(D[u'win_close_dig']))
D[u'win_spans'] = [w[u'end'] - w[u'start'] + 1 for w in WIN]

# ---------- 段落: 偏移→行号改走 bisect ----------
def fmap(i):
    offs = []
    nrs = []
    off = 0
    first = True
    for n, x in enumerate(L[i], 1):
        if shell_line(x):
            continue
        s = cf(x)
        if not s:
            continue
        if not first:
            off += 1
        first = False
        offs.append(off)
        nrs.append(n)
        off += len(s)
    return offs, nrs


FMP = [fmap(i) for i in range(NSRC)]


def line_of(i, a):
    offs, nrs = FMP[i]
    return nrs[bisect.bisect_right(offs, a) - 1]


def blk(i, start, end):
    a = SHF[i].find(start)
    b = SHF[i].find(end, a)
    e = b + len(end)
    return cf(SHF[i][a:e]), line_of(i, a), line_of(i, e - 1)


def ln_of(i, nd):
    return line_of(i, SHF[i].find(nd))


P45, P45_LO, P45_HI = blk(0, u'A value of zero is reserved', u'ticket_lifetime_hint.')
P50, P50_LO, P50_HI = blk(1, u'A value of zero is reserved', u'ticket_lifetime_hint.')
P84, P84_LO, P84_HI = blk(2, u'A server MAY treat a ticket', u'ticket_lifetime.')
D[u'blk_lo'] = [P45_LO, P50_LO, P84_LO]
D[u'blk_hi'] = [P45_HI, P50_HI, P84_HI]
D[u'blk_rows'] = [P45_HI - P45_LO + 1, P50_HI - P50_LO + 1, P84_HI - P84_LO + 1]
D[u'blk_words'] = [len(P45.split()), len(P50.split()), len(P84.split())]
W45 = P45.lower().split()
W50 = P50.lower().split()
W84 = P84.lower().split()
D[u'w45_only'] = sorted(set(w for w in W45 if w not in W50))
D[u'w50_only'] = sorted(set(w for w in W50 if w not in W45))
D[u'w45_only_n'] = len(D[u'w45_only'])
D[u'w50_only_n'] = len(D[u'w50_only'])
D[u'w_common'] = len(set(W45) & set(W50))
D[u'w_row_close'] = D[u'w45_only_n'] + D[u'w_common'] - len(set(W45))
D[u'hint_in_45'] = rc(P45, u'hint')
D[u'hint_in_50'] = rc(P50, u'hint')
D[u'hint_in_84'] = rc(P84, u'hint')
D[u'hint_in_blk'] = [D[u'hint_in_45'], D[u'hint_in_50'], D[u'hint_in_84']]
D[u'orlonger_45'] = rc(P45, u'or longer')
D[u'orlonger_50'] = rc(P50, u'or longer')
D[u'orlonger_84'] = rc(P84, u'or longer')
D[u'orlonger_blk'] = [D[u'orlonger_45'], D[u'orlonger_50'], D[u'orlonger_84']]
D[u'tone_up_45'] = ub(P45, u'MUST') + ub(P45, u'MAY') + ub(P45, u'SHOULD')
D[u'tone_up_50'] = ub(P50, u'MUST') + ub(P50, u'MAY') + ub(P50, u'SHOULD')
D[u'tone_up_84'] = ub(P84, u'MUST') + ub(P84, u'MAY') + ub(P84, u'SHOULD')
D[u'tone_cap_84'] = ub(P84, u'MUST NOT')


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


D[u'suf_45_50'] = suf(W45, W50)
D[u'pre_45_50'] = pre(W45, W50)
D[u'suf_50_84'] = suf(W50, W84)
D[u'pre_50_84'] = pre(W50, W84)
D[u'ln_zero_4507'] = ln_of(0, u'A value of zero is reserved')
D[u'ln_unspec_4507'] = ln_of(0, u'is unspecified.')
D[u'zero_split_gap'] = D[u'ln_unspec_4507'] - D[u'ln_zero_4507']
D[u'ln_relative_5077'] = ln_of(1, u'relative to when the ticket is received')
D[u'ln_hintdef_5077'] = ln_of(1, u'ticket_lifetime_hint field contains a hint')
D[u'relative_span'] = D[u'ln_relative_5077'] - D[u'ln_hintdef_5077']
D[u'ln_cap_8446'] = ln_of(2, u'604800 seconds')
D[u'ln_zeroind_8446'] = ln_of(2, u'should be discarded immediately')
D[u'cap_zeroind_span'] = D[u'ln_cap_8446'] - D[u'ln_zeroind_8446']

# ---------- 共用长行池 ⇎ 配对 ⇎ 轴 ⇎ 锚池 ----------
def pl(i):
    return [x for x in SH[i] if len(pn(x)) >= POOLMIN]


GN = [set(pn(x) for x in pl(i)) for i in range(NSRC)]
GRA = [set(pl(i)) for i in range(NSRC)]
PAIRS = list(itertools.combinations(range(NSRC), 2))
TRI = list(itertools.combinations(range(NSRC), 3))
D[u'pair_share'] = [len(GN[a] & GN[b]) for a, b in PAIRS]
D[u'pair_byte'] = [sum(1 for s in (GN[a] & GN[b])
                       if any(pn(x) == s and x in GRA[b] for x in pl(a))) for a, b in PAIRS]
D[u'pair_norm_only'] = [D[u'pair_share'][k] - D[u'pair_byte'][k] for k in range(len(PAIRS))]
D[u'pair_close'] = (sum(D[u'pair_share']) - sum(D[u'pair_byte'])
                    - sum(D[u'pair_norm_only']))
D[u'pair_nonzero'] = len([x for x in D[u'pair_share'] if x])
D[u'pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
mx = max(D[u'pair_share'])
D[u'pair_max'] = mx
D[u'pair_max_idx'] = D[u'pair_share'].index(mx)
D[u'pair_max_byte'] = D[u'pair_byte'][D[u'pair_max_idx']]
D[u'pair_max_norm_only'] = D[u'pair_norm_only'][D[u'pair_max_idx']]
D[u'pair_max_lbl'] = D[u'pair_lbl'][D[u'pair_max_idx']]
ALLP = set().union(*GN)
CC = defaultdict(set)
for i in range(NSRC):
    for x in pl(i):
        CC[pn(x)].add(i)
pres = dict((a, tuple(i for i in range(NSRC) if a in GN[i])) for a in ALLP)
D[u'pool_n'] = len(ALLP)
D[u'pool_tier'] = [len([a for a, v in pres.items() if len(v) == n]) for n in range(1, NSRC + 1)]
D[u'pool_tier_close'] = sum(D[u'pool_tier']) - D[u'pool_n']
D[u'pool_4'] = D[u'pool_tier'][3]
D[u'pool_3'] = D[u'pool_tier'][2]
D[u'pool_2'] = D[u'pool_tier'][1]
D[u'pool_1'] = D[u'pool_tier'][0]
_t1 = sum(len(v) for v in pres.values())
_t2 = sum(len(v) * (len(v) - 1) // 2 for v in pres.values())
_t3 = sum(len(v) * (len(v) - 1) * (len(v) - 2) // 6 for v in pres.values())
_t4 = len([v for v in pres.values() if len(v) == NSRC])
D[u'pool_incl'] = [_t1, _t2, _t3, _t4]
D[u'union_incl'] = _t1 - _t2 + _t3 - _t4
D[u'union_close'] = D[u'pool_n'] - D[u'union_incl']
D[u'tri_share'] = [len([a for a, v in pres.items() if len(v) >= 3 and i in v])
                   for i in range(NSRC)]
D[u's3_examples'] = sorted([a for a, v in pres.items() if len(v) >= 3])
letters = re.compile(u'[A-Za-z]')
D[u'pool_letters'] = len([a for a in ALLP if letters.search(a)])
D[u'pool_border'] = D[u'pool_n'] - D[u'pool_letters']
D[u'shared_norm_only'] = sum(D[u'pair_norm_only'])

axis = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
for a, v in pres.items():
    if len(v) < 2:
        continue
    xs = set()
    for i in v:
        xs |= set(x for x in SH[i] if pn(x) == a)
    if len(xs) < 2:
        continue
    o, p = sorted(xs)[0], sorted(xs)[1]
    if len(o) == len(p) and o != p and all(x.lower() == y.lower() for x, y in zip(o, p)):
        axis[u'case'] += 1
    elif (u'-' in o) != (u'-' in p):
        axis[u'hyph'] += 1
    elif len([y for y in o.strip().split(u' ') if y]) == len([y for y in p.strip().split(u' ') if y]):
        axis[u'space'] += 1
    else:
        axis[u'multi'] += 1
D[u'axis_counts'] = axis
D[u'axis_total'] = sum(axis.values())
D[u'norm_only_set'] = len([a for a, v in pres.items()
                           if len(v) >= 2 and len(set(x for i in v for x in SH[i] if pn(x) == a)) > 1])
D[u'axis_close'] = D[u'axis_total'] - D[u'norm_only_set']
D[u'axis_str'] = u'⇎'.join(u'%s%d' % (a, axis[a]) for a in (u'case', u'hyph', u'space', u'multi'))
D[u'axis_str_n'] = len([a for a in (u'case', u'hyph', u'space', u'multi') if axis[a]])

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

# ---------- 闭合判定 ----------
CLOSE = {}
CLOSE[u'zero_flip'] = 1 if (D[u'n_z4507_zero_reserved'][0] and D[u'n_z5077_zero_reserved'][1]
                            and D[u'n_z8446_zero_discard'][2] and not D[u'n_z9001_zero'][3]) else 0
CLOSE[u'zero_res_agree'] = 0 if (D[u'n_z4507_zero_reserved'][0]
                                 and D[u'n_z5077_zero_reserved'][1]) else 1
CLOSE[u'zero_ind_unique'] = 0 if (D[u'n_z8446_zero_discard'][2] == 1 and sum(
    D[u'n_z8446_zero_discard'][i] for i in (0, 1, 3)) == 0) else 1
CLOSE[u'cap_unique'] = 0 if NUM['cap_present_docs'] == 1 else 1
CLOSE[u'cap_ratio_close'] = 0 if (NUM['cap_ratio'] == NUM['cap_days'][2] == 7
                                  and NUM['cap_remainder'] == 0) else 1
CLOSE[u'day_lt_cap'] = 0 if NUM['day_seconds'] < NUM['cap_faces'][2] else 1
CLOSE[u'drop_or_longer'] = 1 if (D[u'orlonger'][0] == D[u'orlonger'][1] == 1
                                 and D[u'orlonger'][2] == 0 and D[u'shorter_only'][2] == 1) else 0
CLOSE[u'rel_inserted'] = 1 if (D[u'relative_in'][1] >= 1 and D[u'relative_in'][0] == 0
                               and D[u'recv_time'][1] >= 1 and D[u'recv_time'][0] == 0) else 0
CLOSE[u'from_issuance_only'] = 1 if (D[u'from_issuance'][2] == 1 and sum(
    D[u'from_issuance'][i] for i in (0, 1, 3)) == 0) else 0
CLOSE[u'field_renamed'] = 1 if (sum(D[u'fld_hint'][2:]) == 0 and D[u'uint32_hint'][0] == 1
                                and D[u'uint32_hint'][1] == 1 and D[u'uint32_plain'][2] >= 1) else 0
CLOSE[u'reuse_absent'] = 1 if (D[u'n_z9001_reuse'][3] and D[u'n_z8446_reuse'][2]
                               and D[u'n_z9001_reuse'][0] + D[u'n_z9001_reuse'][1] == 0) else 0
CLOSE[u'delegates'] = 1 if (D[u'n_z9001_seven_days'][3] and D[u'seven_days'][3] >= 1
                            and D[u'lifetime_word'][3] >= 1) else 0
CLOSE[u'no_self_lifetime'] = 1 if (D[u'must_cap_face'][3] == 0 and NUM['cap_lit'][3] == 0
                                   and D[u'n_z9001_zero'][3] == 0) else 0
CLOSE[u'week_only_8446'] = 1 if (D[u'week_word'][2] and D[u'week_word'][0] + D[u'week_word'][1]
                                 + D[u'week_word'][3] == 0) else 0
CLOSE[u'24hour_pair'] = 0 if (D[u'd24_hour'][0] == D[u'd24_hour'][1] == 1
                              and D[u'd24_hour'][2] == D[u'd24_hour'][3] == 0) else 1
CLOSE[u'year_order'] = 0 if (D[u'year_inversions'] == 0 and D[u'year_order'] == 1) else 1
CLOSE[u'cat_close'] = 0 if sum(D[u'cat_std']) == sum(D[u'cat_hdr']) == NSRC else 1
CLOSE[u'obs_5077_unique'] = 0 if D[u'obs_n'][1] == 1 else 1
CLOSE[u'chain_closed'] = 1 if (5077 in OBS[2] and not (4507 in OBS[2] or 4507 in UPD[2])
                               and D[u'obs_n'][1] == 1) else 0
CLOSE[u'cite_dir'] = 1 if (D[u'cite_5077_in_8446'] and not D[u'cite_dir_8446_to_9001']
                           and D[u'cite_4507_in_5077']) else 0
CLOSE[u'up_zero_9001_cap'] = 0 if (D[u'must_cap_face'][3] == 0) else 1
for k in CLOSE:
    D[k] = CLOSE[k]

# ---------- 锚双轨归属 ----------
TT = io.open(ENTRY, encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
CIT = re.findall(u'⟦(' + u'|'.join(LBL) + u')⟧⟨([^⟨⟩]+)⟩', enc)
DIS = []
for _, a in CIT:
    if a not in DIS:
        DIS.append(a)
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


def _jr(x):
    return json.loads(json.dumps(x))


NSV = dict(FLAT)
NSV.update(D)
V = lambda k, i=None: (NSV[k] if i is None else NSV[k][i])
ZRES = [(e, w, eval(e, {u'B71V': V})) for e, w in CH[u'zid']]
ZFAIL = [(w, r) for e, w, r in ZRES if r != 0]
D[u'zid_fail'] = [w for e, w, r in ZRES if r != 0]
D[u'scalar_clos_sum'] = len([1 for e, w, r in ZRES if r == 0])
D[u'list_clos_n'] = len([k for k in FLAT if (u'_close' in k or u'_ledger' in k)
                         and isinstance(FLAT[k], list)])
MISS = [k for k in D if k not in FLAT]
BAD = [(k, _jr(D[k]), _jr(FLAT[k])) for k in D if k in FLAT and _jr(D[k]) != _jr(FLAT[k])]
UNCOVER = [k for k in FLAT if k not in D]
DFAIL = []
for kk, v in JJ.items():
    try:
        g = eval(v, {}, {u'B71V': V})
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
assert sum(D[u'fld_close']) == 0
assert D[u'pair_close'] == 0 and D[u'union_close'] == 0 and D[u'pool_tier_close'] == 0
assert D[u'apool_tag_close'] == 0 and D[u'apool_tier_close'] == 0 and D[u'axis_close'] == 0
assert D[u'ladder_monotone'] == 1 and D[u're_eq_cur'] == 1 and sum(D[u'sh_minus_fold']) == 0
assert D[u'cap_unique'] == 0 and D[u'cap_ratio_close'] == 0 and D[u'day_lt_cap'] == 0
assert D[u'year_order'] == 0 and D[u'obs_5077_unique'] == 0 and D[u'cat_close'] == 0
assert D[u'zero_ind_unique'] == 0 and D[u'up_zero_9001_cap'] == 0 and D[u'24hour_pair'] == 0
assert D[u'w_row_close'] == 0 and D[u'zero_split_gap'] == 10
assert D[u'lines_split_close'] == 0 and sum(D[u'tail_nl']) == NSRC
assert sorted(D[u'dead_needles']) == [u'z4507_no_relative', u'z9001_zero']
assert D[u'zero_carry_sh'][1] - D[u'zero_carry_fold'][1] == D[u'zero_flip']

# ---------- ⛓解读注 ----------
L2 = []
A = L2.append
A(u"第四遍(`corpus/_fill71.py`)换算法不换定义地重跑一遍: 读面走 bytes 再 decode ⇎ 行数三档对拍"
  u"(`split('\\n')` 计格 ⇎ `count('\\n')+1` ⇎ `splitlines()`) ⇎ 换页符按 `split('\\x0c')-1` ⇎ 针计数按 "
  u"`len(re.findall(re.escape(针), 面))`(第二遍是非重叠游标 find, 第一遍是 `str.count`) ⇎ 义务语气按“非字母切片后数整词”"
  u" ⇎ 字段名按“非词字符切片后数整 token”(把 `ticket_lifetime_hint` 当一枚 token, 与第二遍的词界正则不同路) ⇎ "
  u"四枚读数由带捕获组的 findall 一次到位 ⇎ 带定位先在 `enumerate(L)` 里找答句行再取 ±%d 行 ⇎ "
  u"段落起止行由折平偏移经 `bisect_right` 映回(第二遍是线性游标扫描) ⇎ 搬运走 set 代数 ⇎ 锚归属走逐行⇎折平双轨。" % BAND)
A(u"本遍复算 %d 个键(扁平表 %d 键中覆盖 %d 枚 ⇎ 本遍独有 %d ⇎ 未复算 %d ⇎ 逐值不符 %d); "
  u"面内恒等式 %d 条在本注读数上重跑全为真(通过 %d); DERIV %d 条复算点重跑全对(引用 %d 处)。" % (
      len(D), len(FLAT), len([k for k in D if k in FLAT]), len(MISS), len(UNCOVER), len(BAD),
      len(CH[u'zid']), D[u'scalar_clos_sum'], len(JJ),
      sum(len(v.split(u'B71V(')) - 1 for v in JJ.values())))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"行数⇎换页", u"`split('\\n')` ⇎ `count('\\n')+1` ⇎ `splitlines()` 三档 ⇎ 换页符 `split('\\x0c')-1`",
     u"行数 %s ⇎ 换行档 %s ⇎ splitlines %s ⇎ 换页符 %s ⇎ 末行有换行符 %s 份 ⇎ 剥壳剥掉 %s 行" % (
         J(D[u'lines']), J(D[u'lines_nl']), J(D[u'lines_split']), J(D[u'ff']),
         sum(D[u'tail_nl']), J(D[u'shell_strip'])),
     u"三档的差全部由换页符与末行换行解释: splitlines 档 = 换行档 − 末行换行(%s 份有) + 换页符枚数, 四份闭合 %d——"
     u"`splitlines()` 把 %s 枚换页符也当行界, 而 9001 换页符 %d 枚⇒它只与另两档差末行那 1 格; "
     u"摘壳相对含壳折平的针读数四份 %s⇒剥掉的 %s 行壳里一枚针都没有(8446 一份就剥掉 %d 行)" % (
         sum(D[u'tail_nl']), D[u'lines_split_close'], J(D[u'ff']), D[u'ff'][3],
         J(D[u'sh_minus_fold']), J(D[u'shell_strip']), D[u'shell_strip'][2])),
    (u"编码层", u"字节面看 BOM ⇎ 码位面数非 ASCII ⇎ 逐字符按 utf-8 加字节",
     u"BOM %s ⇎ 非 ASCII %s ⇎ 加字节 %s ⇎ 字节−码位 %s ⇎ 纯 ASCII %d 份" % (
         J(D[u'bom']), J(D[u'nonascii']), J(D[u'nonascii_extra']),
         J(D[u'byte_cp_delta']), D[u'ascii_all']),
     u"三份纯 ASCII, 只有 9001 带 BOM ⇎ %d 枚非 ASCII 字符(排版引号与长横), 加字节 %d = 字节−码位差 %d "
     u"逐枚相等——这一条的实质分歧与编码层无关, 只有 9001 一份是 UTF-8 排版面" % (
         D[u'nonascii'][3], D[u'nonascii_extra'][3], D[u'byte_cp_delta'][3])),
    (u"三面阶梯", u"逐行 in ⇎ 全篇折平(findall) ⇎ 摘壳折平 ⇎ 正则字面轨",
     u"逐行 %s ⇎ 折平 %s ⇎ 摘壳 %s ⇎ 正则 %s ⇎ 只折平存在的 %d 枚" % (
         J(D[u'sn_strict_docs']), J(D[u'sn_fold_docs']), J(D[u'sn_sh_docs']),
         J(D[u'sn_re_docs']), D[u'fold_only_n']),
     u"阶梯单调 %d ⇎ 摘壳相对折平 %s ⇎ 死针 %s: 4507 的 %d 枚自家针逐行档只命中 %d 枚, 5077 的 %d 枚一枚都不在逐行档"
     u"(答句整段被行界劈开), 8446/9001 的逐行档各 %d/%d 枚——把行界抹平才把前两份读成“写了这条规则”; "
     u"阶梯读不到的两枚恰是该零命中的两枚反向针(4507 面上无 relative to when the ticket is received ⇎ "
     u"9001 面上无“A value of zero”句式), 死集等于判定集" % (
         D[u'ladder_monotone'], J(D[u'sh_minus_fold']), J(D[u'dead_needles']),
         D[u'sn_fold_docs'][0], D[u'sn_strict_docs'][0], D[u'sn_fold_docs'][1],
         D[u'sn_strict_docs'][2], D[u'sn_strict_docs'][3])),
    (u"两轨判定", u"正则字面轨(findall) ⇎ 非重叠游标轨 ⇎ 重叠前瞻档",
     u"两轨相等 %d ⇎ 重叠多余 %d ⇎ 跨面同现针 %d 枚" % (
         D[u're_eq_cur'], D[u'overlap_extra'], D[u'cross_needle_n']),
     u"这批针里没有自重叠针⇒重叠档与非重叠档逐枚同值; 跨面同现的 %d 枚就是 4507⇎5077 逐字搬运的那批句子" % (
         D[u'cross_needle_n'])),
    (u"零值那半句", u"同一枚连句号的针在两种面上各读一次 ⇎ 偏移映回原行号",
     u"5077 的整句在 4507 摘壳面 %d 枚 ⇎ 含壳全篇面 %d 枚 ⇎ 4507 的短针在 5077 摘壳面 %d 枚 ⇎ 含壳面 %d 枚 ⇎ "
     u"“A value of zero”在第 %d 行⇎“is unspecified.”在第 %d 行 ⇎ 相隔 %d 行" % (
         D[u'zero_carry_sh'][1], D[u'zero_carry_fold'][1], D[u'zero_carry_sh'][0],
         D[u'zero_carry_fold'][0], D[u'ln_zero_4507'], D[u'ln_unspec_4507'], D[u'zero_split_gap']),
     u"同一枚连句号整句针在 4507 剥壳后读到 %d 枚、不剥壳只剩 %d 枚(差 %d, 翻转判定 %d)⇒这句被一页壳正好劈开——"
     u"半句止于第 %d 行, 后半句从第 %d 行起; 反向那枚停在“the ticket”的短针两档都是 %d 枚⇒劈开只发生在整句上。"
     u"不剥壳就断言“4507 没写这句”会读成零枚, 只按逐行档读又会以为两份各写各的; 8446 把同一个零值翻成“立即丢弃”"
     u"(全库唯一, 判定 %d⇒成立), 9001 面上“值零”句式 %d 枚而它既不封顶也不定义零(判定 %d⇒成立)" % (
         D[u'zero_carry_sh'][1], D[u'zero_carry_fold'][1],
         D[u'zero_carry_sh'][1] - D[u'zero_carry_fold'][1], D[u'zero_flip'],
         D[u'ln_zero_4507'], D[u'ln_unspec_4507'], D[u'zero_carry_sh'][0],
         D[u'zero_ind_unique'], D[u'n_z9001_zero'][3], D[u'up_zero_9001_cap'])),
    (u"句内读数", u"捕获组 findall `value greater than (\\d+)` ⇎ `seconds ((\\d+) days)` ⇎ `longer than the (\\d+)-hour` ⇎ `modulo 2^(\\d+)`",
     u"上限秒数面 %s ⇎ 括注日数 %s ⇎ 上限只活在 %d 份 ⇎ 日=%d 秒 ⇎ 商 %d 余 %d ⇎ 2^%d" % (
         J(D[u'num_cap_faces']), J(D[u'num_cap_days']), D[u'num_cap_present_docs'],
         D[u'num_day_seconds'], D[u'num_cap_ratio'], D[u'num_cap_remainder'], D[u'num_mod_pow']),
     u"上限只活在 %d 份里: %d = 每日 %d 秒 × %d 日(余数 %d ⇒ 恰是整日数, 括注的 %d 日与商同值); "
     u"8446 面上十进制字面 %d 枚 ⇎ “week”字样 %d 枚 ⇎ 整句针 %d 枚, 三轨同指这一份; "
     u"24 小时那句只在 4507/5077(%s 枚)而 8446/9001 面上 0 枚——旧的“建议值”被硬上限替掉, "
     u"9001 只用文字转述 seven days(“seven days”字样 %d 枚 ⇎ [TLS13] 括号引用 %d 枚)" % (
         D[u'num_cap_present_docs'], D[u'num_cap_faces'][2], D[u'num_day_seconds'],
         D[u'num_cap_ratio'], D[u'num_cap_remainder'], D[u'num_cap_days'][2],
         D[u'num_cap_lit'][2], D[u'week_word'][2], D[u'n_z8446_cap'][2], J(D[u'd24_hour']),
         D[u'seven_days'][3], D[u'num_tls13_refs'][3]))
    ,
    (u"字段改名", u"整 token 档(非词字符切片) ⇎ 词界正则档 ⇎ 子串档",
     u"hint 式 %s ⇎ 裸式 %s ⇎ 子串总现 %s ⇎ 三式闭合 %s ⇎ hint 声明行 %s ⇎ 裸式声明行 %s" % (
         J(D[u'fld_hint']), J(D[u'fld_plain']), J(D[u'fld_sub']), J(D[u'fld_close']),
         J(D[u'uint32_hint']), J(D[u'uint32_plain'])),
     u"改名后 %d 份面上 hint 式归零(判定 %d), 裸式只在 8446(%d 枚); 子串档 %d = token 档 %d+%d——"
     u"用整 token 计数才不把 `ticket_lifetime_hint` 误当裸式, 用子串档才能证明两式不重不漏" % (
         len([i for i in (2, 3) if D[u'fld_hint'][i] == 0]), D[u'field_renamed'],
         D[u'fld_plain'][2], D[u'fld_sub'][2], D[u'fld_hint'][2], D[u'fld_plain'][2]))
    ,
    (u"义务语气", u"token 整词档 ⇎ 子串双尺(大写/MUST NOT/小写/无视大小写)",
     u"大写 MUST %s ⇎ 裸 %s ⇎ MUST NOT %s ⇎ SHOULD NOT %s ⇎ 小写 must %s ⇎ 无视大小写 must %s ⇎ 首字母 %s" % (
         J(D[u'up_must_all']), J(D[u'must_bare']), J(D[u'must_not']), J(D[u'should_not']),
         J(D[u'low_must']), J(D[u'ci_must']), J(D[u'title_must'])),
     u"大写账 %s ⇎ 四轨账 %s 全归零; 4507⇎5077 的大写 MUST 各 %d 枚、MUST NOT 各 %d 枚, 两行的账逐枚相等——"
     u"与逐字搬运那条对得上; 8446 猛增到 %d 枚且 MUST NOT %d 枚——“不得超上限”“不得缓存超七日”“不得复用”"
     u"三处否定义务是它新增的; 9001 面上大写义务 %d 枚, 但封顶那件事它一枚都不写(判定 %d⇒成立)" % (
         J(D[u'up_ledger']), J(D[u'case_ledger']), D[u'up_must_all'][0], D[u'must_not'][0],
         D[u'up_must_all'][2], D[u'must_not'][2], D[u'up_must_all'][3], D[u'up_zero_9001_cap']))
    ,
    (u"该删哪句", u"折平针“shorter or longer”⇎“valid for a shorter period”⇎段内“or longer”",
     u"or longer %s ⇎ 只剩 shorter %s ⇎ 段内 %s ⇎ 判定 %d" % (
         J(D[u'orlonger']), J(D[u'shorter_only']), J(D[u'orlonger_blk']), D[u'drop_or_longer']),
     u"4507 与 5077 都写“可以更短也可以更长”, 8446 只留“可以更短”(“or longer”在它的段内档⇎全篇档都 %d 枚 ⇎ %d 枚"
     u", 而前两份段内各 1 枚)——同一枚 MAY 句被砍掉一半自由度, 这个差在第二遍的游标档与本遍的 findall 档读到同一个数" % (
         D[u'orlonger_84'], D[u'orlonger'][2]))
    ,
    (u"计时起点", u"折平针“relative to when the ticket is received”⇎“from the time of ticket issuance”",
     u"relative %s ⇎ when received %s ⇎ issuance %s ⇎ 判定 %d/%d ⇎ 5077 段内距 %d 行" % (
         J(D[u'relative_in']), J(D[u'recv_time']), J(D[u'from_issuance']),
         D[u'rel_inserted'], D[u'from_issuance_only'], D[u'relative_span']),
     u"4507 面上“相对何时起算”一个字都没写(%d⇎%d 枚), 5077 补 relative to when the ticket is received"
     u"(%d 枚), 8446 又把起点改成 from the time of ticket issuance(%d 枚, 全库唯一)——"
     u"起点这句话在三份里换了两次写法, 三份的判定互不重合" % (
         D[u'relative_in'][0], D[u'recv_time'][0], D[u'relative_in'][1], D[u'from_issuance'][2]))
    ,
    (u"段内逐词账", u"段落边界由摘壳折平的针现定 ⇎ 偏移经 bisect 映回原行 ⇎ 词集去重共有",
     u"段起 %s 止 %s 行 %s 词 %s ⇎ 共有 %d ⇎ 只 4507 %d ⇎ 只 5077 %d ⇎ 共尾 %d ⇎ 共头 %d ⇎ hint 在段内 %s" % (
         J(D[u'blk_lo']), J(D[u'blk_hi']), J(D[u'blk_rows']), J(D[u'blk_words']),
         D[u'w_common'], D[u'w45_only_n'], D[u'w50_only_n'], D[u'suf_45_50'], D[u'pre_45_50'],
         J(D[u'hint_in_blk'])),
     u"4507 与 5077 的这段共尾 %d 枚词 ⇎ 共头 %d 枚词, 两个数都等于各自的词数(%s)⇒整段照搬, 一个词没动, "
     u"行数 %d⇎%d 只是重新 wrap; 词集账闭合 %d; 5077 补的计时起点不在这段里(段内 hint %d⇎%d 枚), "
     u"8446 的改名段共头只 %d 枚——它把这段重写了" % (
         D[u'suf_45_50'], D[u'pre_45_50'], J(D[u'blk_words']), D[u'blk_rows'][0],
         D[u'blk_rows'][1], D[u'w_row_close'],
         D[u'hint_in_45'], D[u'hint_in_50'], D[u'pre_50_84']))
    ,
    (u"谁废止谁", u"Obsoletes:/Updates: 头现读号集合(逐行 strip 后切冒号) ⇎ 标题页年份尾锚定",
     u"obs 枚数 %s ⇎ upd %s ⇎ 5077 废 %s ⇎ 8446 废 %s ⇎ 8446 更 %s ⇎ 目标并集 %s ⇎ 年份 %s ⇎ 月 %s" % (
         J(D[u'obs_n']), J(D[u'upd_n']), D[u'obs_set_5077'], D[u'obs_set_8446'],
         D[u'upd_set_8446'], D[u'target_ids'], J(D[u'years']), J(D[u'months'])),
     u"链路闭合 %d: 5077 面上唯一废止 4507, 8446 面上废止 5077 而不再碰 4507; 年份严格递增 %d(倒序 %d 处, "
     u"判定 %d) ⇎ 年距 %s——与 B70 那条“更新得比被更新者晚四年”的倒序不同, 这一条的文书顺序与时间顺序同向, "
     u"所以“取最新”在这条里不会被年份骗, 只会被 9001 的转述骗(它把规则整段归给 [TLS13], 面上括号引用 %d 枚)" % (
         D[u'chain_closed'], D[u'year_order'], D[u'year_inversions'], D[u'year_order'],
         J(D[u'year_gaps']), D[u'num_tls13_refs'][3]))
    ,
    (u"窗五轨", u"±%d 行邻域窗按小节标题定位, 带内+带外=全篇(lifetime⇎zero⇎604800⇎reuse⇎数字)" % BAND,
     u"节行 %s ⇎ 答句行 %s ⇎ 窗 %s 至 %s ⇎ 行数 %s ⇎ 闭合 %s" % (
         J(D[u'win_sec']), J(D[u'win_ans']), J(D[u'win_start']), J(D[u'win_end']),
         J(D[u'win_rows']), J([D[u'win_close_lt'], D[u'win_close_zero'], D[u'win_close_cap'],
                              D[u'win_close_reuse'], D[u'win_close_dig']])),
     u"四份都命到小节标题 %d 枚 ⇎ 窗跨度齐 %s 行 ⇎ 五轨合计闭合 %d; 复用禁令在带外(9001 面带内 %d 枚 ⇎ "
     u"带外 %d 枚), 上限在带内(8446 面带内 %d 枚 ⇎ 带外 %d 枚)——窗把“答句周围”和“文书别处的杂项”分开了" % (
         D[u'win_named'], J(D[u'win_spans']), D[u'win_close_sum'], D[u'win_reuse_in'][3],
         D[u'win_reuse_out'][3], D[u'win_cap_in'][2], D[u'win_cap_out'][2]))
    ,
    (u"搬运⇎重写", u"set 代数: 归一交 ⇎ 逐字节双尺交 ⇎ 仅归一 ⇎ 容斥按 pres 权重手算",
     u"长行池 %d ⇎ 分档 %s ⇎ 六对归一 %s ⇎ 逐字节 %s ⇎ 仅归一 %s" % (
         D[u'pool_n'], J(D[u'pool_tier']), J(D[u'pair_share']), J(D[u'pair_byte']), J(D[u'pair_norm_only'])),
     u"配对闭合 %d ⇎ 容斥闭合 %d ⇎ 分档闭合 %d; 与 B70(六对里只一对非零, 且全是许可样板)相反, "
     u"这一条的最大对是 %s(归一 %d 枚, 逐字节 %d 枚, 只差缩进 %d 枚)——4507 被 5077 整段照搬是真的行级搬运; "
     u"三份同现的 %d 枚 ⇎ 四份同现 %d 枚" % (
         D[u'pair_close'], D[u'union_close'], D[u'pool_tier_close'], D[u'pair_max_lbl'],
         D[u'pair_share'][D[u'pair_max_idx']], D[u'pair_max_byte'], D[u'pair_max_norm_only'],
         D[u'pool_3'], D[u'pool_4']))
    ,
    (u"写法分家轴", u"归一同形而逐字节不同的共用长行按“差在哪”分四桶",
     u"四桶 %s ⇎ 非零档 %d ⇎ 轴账闭合 %d ⇎ 锚池分档 %s ⇎ 标签 %s" % (
         D[u'axis_str'], D[u'axis_str_n'], D[u'axis_close'], J(D[u'apool_tier']),
         J(D[u'apool_tag_n'])),
     u"空格档 %d 枚(同一句在两份里只差行首缩进) ⇎ 大小写档 %d 枚, 短横⇎多字差两档 %s/%d 枚; "
     u"锚候选池两本账闭合 %d/%d(按标签 %d ⇎ 按份数加权 %d ⇎ 池条目 %d ⇎ 最长 %d 字符)" % (
         D[u'axis_counts'][u'space'], D[u'axis_counts'][u'case'],
         D[u'axis_counts'][u'hyph'], D[u'axis_counts'][u'multi'], D[u'apool_tag_close'],
         D[u'apool_tier_close'], D[u'apool_pairs'], D[u'apool_weight'], D[u'apool_n'],
         D[u'apool_maxlen']))
    ,
    (u"锚双轨", u"一枚锚同时按“等于某原文件行”⇎“其归一式落在折平面里”两种成员判",
     u"正文 %d 处 ⇎ 去重 %d 串 ⇎ 两轨同判 %d ⇎ 分歧 %d" % (
         D[u'anchor_total'], D[u'anchor_distinct'], D[u'track_agree'], len(D[u'track_split'])),
     u"归属错配 %d ⇎ 一源 %d ⇎ 跨源 %d ⇎ 四源 %d; 跨源 %d 枚全落在 4507⇎5077 这一对(逐字搬运把同一行留在两份里); "
     u"编码区 %d 字符 ⇎ 归属检查 %d 次 ⇎ 标签 4507/5077/8446/9001 = %d/%d/%d/%d" % (
         D[u'anchor_err'], D[u'anchor_single'], D[u'anchor_cross'], D[u'anchor_all4'],
         D[u'anchor_cross'], D[u'enc_chars'], D[u'checks'], D[u'tag_4507'], D[u'tag_5077'],
         D[u'tag_8446'], D[u'tag_9001']))
    ,
]
for a1, b1, c1, d1 in rows:
    A(u"| %s | %s | %s | %s |" % (a1, b1, c1, d1))
A(u"")
A(u"### 本注的判断")
A(u"四份文书答的不是同一个问题的四个答案, 而是把“票据能活多久 ⇎ 零值是什么意思 ⇎ 从哪一刻起算 ⇎ 一张票能不能复用”"
  u"四件事拆给了四份: 4507 给字段与一个 hint, 零值只写成“寿命未定”(面内 %d 枚), 并主动允许服务器把票当作"
  u"“更短或更长”有效(%d 枚)——它连一个上限数字都不给, 只引 2246 的 24 小时建议; 5077 把那段整句照搬"
  u"(共尾共头各 %d 枚词, 词集账闭合 %d)⇎ 唯一补上的是计时起点 relative to when the ticket is received(%d 枚), "
  u"仍不设上限; 8446 一次改五处: 字段改名去掉 hint(%d 份面上 hint 式归零)、零值翻成“立即丢弃”(全库唯一, 判定 %d⇒成立)、"
  u"写出 MUST NOT 超 %d 秒即 %d 日(每日 %d 秒⇒商 %d ⇎ 余 %d)、把“或更长”砍掉只剩更短(段内 %d 枚)、并把起点改写成 "
  u"from the time of ticket issuance(%d 枚, 唯一); 9001 一枚自己的时长规则都不写, 转述“[TLS13] sets a limit of "
  u"seven days”(%d 枚引用), 只另补一条复用禁令(4507/5077 面上 %d 枚 ⇎ 8446 的“不该复用多连接”%d 枚 ⇎ "
  u"9001 的“会让他人关联连接”%d 枚——三份措辞互不相同)。" % (
      D[u'n_z4507_zero_reserved'][0], D[u'orlonger'][0], D[u'suf_45_50'], D[u'w_row_close'],
      D[u'relative_in'][1], len([i for i in (2, 3) if D[u'fld_hint'][i] == 0]), D[u'zero_ind_unique'],
      D[u'num_cap_faces'][2], D[u'num_cap_days'][2], D[u'num_day_seconds'],
      D[u'num_cap_ratio'], D[u'num_cap_remainder'],
      D[u'orlonger_84'], D[u'from_issuance'][2], D[u'num_tls13_refs'][3], D[u'n_z8446_reuse'][0],
      D[u'n_z8446_reuse'][2], D[u'n_z9001_reuse'][3]))
A(u"于是任何“取最新/取最全”的合并都会丢东西: 按年份最新取 9001(2021), 就丢掉 8446 面上那枚把上限钉死为整日数的"
  u"算术(%d = %d × %d, 余 %d)与字段改名本身——9001 只说“[TLS13] 定了七天”, 自己既不给秒数也不定义零值(判定 %d); "
  u"按“最严”取 8446, 就丢掉 5077 补的那句计时起点(8446 把它换成“自签发起”, 两份的起点并不等价)与 4507/5077 的"
  u"“可更长”自由度; 按“最原始”取 4507, 就同时丢掉上限、丢弃语义与复用禁令。逐字搬运在这条里是真的行级搬运: "
  u"%s 那对共用 %d 枚长行, 其中 %d 枚逐字节同形 ⇎ %d 枚只差缩进, 轴账 %s 闭合 %d——但搬运只发生在 4507→5077 一步, "
  u"8446 起就是重写(与 5077 段的共头只 %d 枚词)。" % (
      D[u'num_cap_faces'][2], D[u'num_day_seconds'], D[u'num_cap_ratio'], D[u'num_cap_remainder'],
      D[u'no_self_lifetime'], D[u'pair_max_lbl'], D[u'pair_max'], D[u'pair_max_byte'],
      D[u'pair_max_norm_only'], D[u'axis_str'], D[u'axis_close'], D[u'pre_50_84']))
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; rfc-editor.org 此刻给这四份挂的现行状态页与勘误页"
  u"(含 4507/5077 此后被改判为 Experimental 一事——本注只能读面上自带的类目行 Standards Track %s ⇎ "
  u"Experimental %s 枚, 读不出站点的当前标注); 这条链条之外被引用的 RFC 2246/4346 不在库内"
  u"(库内 rfc*.txt 共 %d 份, 2246 %d ⇎ 4346 %d, 而四份面上对 2246 的引用共 %d 枚——那句“24 小时建议”的原句读不到); "
  u"5246 在库内(%d)但不属于这条的四份源; 9001 转述的 [TLS13] 就是库内的 8446, 但这条等式来自文档惯例而非在库字节自证; "
  u"此后哪份在途文书又动了票据寿命; 现网实现实际缓存多久、要不要复用一张票(“票据是一次用的 ⇎ 可重放的”是实现事实, "
  u"不是文书事实)。" % (
      J(D[u'cat_std']), J(D[u'exp_n']), D[u'in_repo_n'], D[u'in_repo_2246'], D[u'in_repo_4346'],
      sum(D[u'cite_al_2246']), D[u'in_repo_5246']))
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
