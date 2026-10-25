# -*- coding: utf-8 -*-
"""建条目第二遍(B71): “一张 TLS 会话恢复票据到底能活多久、零值是什么意思、一张票能不能复用”,
交四份一手文书各答一遍: 4507(06) hint 字段、零值=寿命未定、无上限 ⇎ 5077(08) 同句逐字收下
并补“相对收到时刻”, 仍无上限 ⇎ 8446(18) 字段改名去掉 hint、零值翻成“立即丢弃”、
写出 604800 秒的 MUST NOT 硬上限、并把“shorter or longer”只剩 shorter ⇎ 9001(21) 全篇不自建
时长规则, 只转述“[TLS13] sets a limit of seven days”, 另给 Clients SHOULD NOT reuse tickets。

本遍与采集侧换实现: 非重叠游标、正则字面轨、集合代数与 itertools 配对; 所有正文数字都由
V()/J()/EXPR() 注册后插值, 一枚都不手打; 键名等于所量之物。"""
import io, itertools, json, re, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'4507', u'5077', u'8446', u'9001']
TAGS = LBL
NSRC = 4
PATH = [u'corpus/raw/tlsTicket/rfc4507.txt', u'corpus/raw/tlsTicket/rfc5077.txt',
        u'corpus/raw/ietf/rfc8446.txt', u'corpus/raw/tlsTicket/rfc9001.txt']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire71.py 把这一段 ⇎ _mk71emit.py 的 SCAN2 段机械切进 audit.py::_b71_scan)


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
L = [t.split(u'\n') for t in T]


def pnorm(s):
    return u' '.join(s.lower().split())


def cnt_cur(hay, nd):
    """非重叠游标计数(采集侧是重叠口径, 两者差单独立键对账)"""
    c = 0
    i = 0
    n = len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def cnt_ovl(hay, nd):
    c = 0
    i = 0
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + 1


def read_after(hay, token, pat):
    """游标读数: token 之后第一个匹配 pat 的组, 读不到给 None"""
    i = hay.find(token)
    if i < 0:
        return None
    m = re.compile(pat).search(hay, i + len(token))
    return None if not m else m.group(1)


GR = read_after
FO = [pnorm(t) for t in T]
FOLD = [u' '.join(t.split()) for t in T]


def shell_line(l):
    if l.strip() == u'':
        return True
    if u'\x0c' in l:
        return True
    if re.match(u'^\\s*\\[?Page \\d+\\]?\\s*$', l):
        return True
    if re.match(u'^\\s*\\[?P\\[?a\\]?g?e?\\s?\\d*\\]?\\s*$', l):
        return True
    if re.match(u'^\\s*RFC-\\d+\\s.*\\s[A-Z][a-z]+ \\d{4}\\s*$', l):
        return True
    if re.match(u'^\\s*RFC \\d+\\s+\\S.*\\s([A-Z][a-z]+ \\d{4}|\\d{4})\\s*$', l):
        return True
    if re.match(u'^\\s*\\S.*\\s(Standards Track|Experimental|Informational|Historic)\\s+\\[?P?age? ?\\d*\\]?\\s*$', l):
        return True
    if re.match(u'^\\s*Network Working Group\\s+\\S.*$', l):
        return True
    if re.match(u'^\\s*(Request for Comments:|Obsoletes:|Updates:|Category:|ISSN:|Internet-Draft)', l):
        return True
    return False


SH = [[x for x in L[i] if not shell_line(x)] for i in range(NSRC)]
SHF = [u' '.join(u'\n'.join(sh).split()) for sh in SH]
FO_SH = [pnorm(u'\n'.join(sh)) for sh in SH]

# ---------- 字面针: 答句整句, 判定走三面档 + 正则字面轨 ----------
NEEDLE = [
    (0, u'z4507_zero_reserved', u'A value of zero is reserved to indicate that the lifetime of the ticket'),
    (0, u'z4507_unspec_end', u'is unspecified.'),
    (0, u'z4507_should_delete', u'A client SHOULD delete the ticket and associated state when the time expires'),
    (0, u'z4507_or_longer', u'A server MAY treat a ticket as valid for a shorter or longer period of time than what is stated in the ticket_lifetime_hint'),
    (0, u'z4507_no_relative', u'relative to when the ticket is received'),
    (0, u'z4507_24hour', u'The ticket lifetime may be longer than the 24-hour lifetime recommended in [RFC2246]'),
    (0, u'z4507_may_be_unspec', u'Since the lifetime of a ticket may be unspecified'),
    (0, u'z4507_hint_def', u'ticket_lifetime_hint field contains a hint from the server about how long the ticket should be stored'),
    (1, u'z5077_zero_reserved', u'A value of zero is reserved to indicate that the lifetime of the ticket is unspecified.'),
    (1, u'z5077_relative', u'in seconds as a 32-bit unsigned integer in network byte order relative to when the ticket is received'),
    (1, u'z5077_should_delete', u'A client SHOULD delete the ticket and associated state when the time expires'),
    (1, u'z5077_or_longer', u'A server MAY treat a ticket as valid for a shorter or longer period of time than what is stated in the ticket_lifetime_hint'),
    (1, u'z5077_24hour', u'The ticket lifetime may be longer than the 24-hour lifetime recommended in [RFC4346]'),
    (1, u'z5077_hint_def', u'ticket_lifetime_hint field contains a hint from the server about how long the ticket should be stored'),
    (2, u'z8446_cap', u'Servers MUST NOT use any value greater than 604800 seconds (7 days)'),
    (2, u'z8446_zero_discard', u'The value of zero indicates that the ticket should be discarded immediately'),
    (2, u'z8446_cache7', u'Clients MUST NOT cache tickets for longer than 7 days, regardless of the ticket_lifetime'),
    (2, u'z8446_shorter_only', u'A server MAY treat a ticket as valid for a shorter period of time than what is stated in the ticket_lifetime'),
    (2, u'z8446_lifetime_from', u'Indicates the lifetime in seconds as a 32-bit unsigned integer in network byte order from the time of ticket issuance'),
    (2, u'z8446_must_not_attempt', u'Clients MUST NOT attempt to use tickets which have ages greater than the "ticket_lifetime" value'),
    (2, u'z8446_week', u'Because ticket lifetimes are restricted to a week, 32 bits is enough to represent any plausible age, even in milliseconds'),
    (2, u'z8446_reuse', u'Clients SHOULD NOT reuse a ticket for multiple connections'),
    (2, u'z8446_mod232', u'modulo 2^32'),
    (3, u'z9001_seven_days', u'[TLS13] sets a limit of seven days on the time between the original connection and any attempt to use 0-RTT'),
    (3, u'z9001_reuse', u'Clients SHOULD NOT reuse tickets as that allows entities other than the server to correlate connections'),
    (3, u'z9001_cap_ref', u'sets a limit of seven days'),
    (3, u'z9001_zero', u'A value of zero'),
    (3, u'z9001_lifetime_word', u'lifetime'),
]
GN = [k for _, k, _ in NEEDLE]
OWNER = dict((k, o) for o, k, _ in NEEDLE)
TEXT = dict((k, nd) for _, k, nd in NEEDLE)
LITK.update(TEXT)
SN = {}
SNF = {}
SNS = {}
SNR = {}
CNT = {}
for o, k, nd in NEEDLE:
    SN[k] = [len([x for x in L[i] if nd in x]) for i in range(NSRC)]
    fl = u' '.join(nd.split())
    SNF[k] = [cnt_cur(FOLD[i], fl) for i in range(NSRC)]
    SNS[k] = [cnt_cur(SHF[i], fl) for i in range(NSRC)]
    SNR[k] = [len([1 for m in re.finditer(re.escape(fl), FOLD[i])]) for i in range(NSRC)]
    CNT[k] = [cnt_ovl(FOLD[i], fl) - SNR[k][i] for i in range(NSRC)]
KEYS = GN
F['needle_n'] = len(KEYS)
F['sn_strict_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SN[k][i] > 0) for i in range(NSRC)]
F['sn_fold_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SNF[k][i]) for i in range(NSRC)]
F['sn_sh_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SNS[k][i]) for i in range(NSRC)]
F['sn_re_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SNR[k][OWNER[k]]) for i in range(NSRC)]
F['fold_only_keys'] = [k for k in KEYS if sum(SN[k]) == 0 and SNF[k][OWNER[k]]]
F['fold_only_own'] = [len([k for k in KEYS if OWNER[k] == i and SN[k][i] == 0 and SNF[k][i]])
                      for i in range(NSRC)]
F['sh_lost_keys'] = [k for k in KEYS if SNF[k][OWNER[k]] and not SNS[k][OWNER[k]]]
F['ladder_monotone'] = 1 if all(F['sn_strict_docs'][i] + F['fold_only_own'][i] == F['sn_fold_docs'][i]
                                for i in range(NSRC)) else 0
F['sh_minus_fold'] = [F['sn_fold_docs'][i] - F['sn_sh_docs'][i] for i in range(NSRC)]
F['fold_line_zero'] = sum(1 for k in F['fold_only_keys'] if SN[k][OWNER[k]])
F['overlap_extra'] = sum(sum(CNT[k]) for k in KEYS)
F['re_eq_cur'] = 1 if all(SNR[k][OWNER[k]] == SNF[k][OWNER[k]] for k in KEYS) else 0
F['zero_carry_sh'] = [SNS[u'z4507_zero_reserved'][1], SNS[u'z5077_zero_reserved'][0]]
F['zero_carry_fold'] = [SNF[u'z4507_zero_reserved'][1], SNF[u'z5077_zero_reserved'][0]]
F['shared_verbatim'] = [k for k in KEYS if sum(1 for i in range(NSRC) if SNF[k][i]) >= 2]
F['cross_needle_n'] = len(F['shared_verbatim'])
F['needles_owned'] = [len([k for k in KEYS if OWNER[k] == i]) for i in range(NSRC)]
for o, k, nd in NEEDLE:
    F['n_' + k] = SNF[k]

# ---------- 结构面量 ----------
F['bytes'] = [len(b) for b in B]
F['chars'] = [len(t) for t in T]
F['lines'] = [len(t.split(u'\n')) for t in T]
F['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['maxlen'] = [max(len(x) for x in L[i]) for i in range(NSRC)]
F['ff'] = [cnt_cur(t, u'\x0c') for t in T]
F['ff_only'] = [len([x for x in L[i] if x.strip() == u'\x0c']) for i in range(NSRC)]
F['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
F['shell_n'] = [len(SH[i]) for i in range(NSRC)]
F['shell_strip'] = [F['lines'][i] - F['shell_n'][i] for i in range(NSRC)]
F['cr'] = [cnt_cur(t, u'\r') for t in T]
F['nonascii'] = [len([c for c in t if ord(c) > 127]) for t in T]
F['bom'] = [1 if b[:3] == b'\xef\xbb\xbf' else 0 for b in B]


def utf8_extra(s):
    return sum(len(c.encode('utf-8')) - 1 for c in s)


F['nonascii_extra'] = [utf8_extra(t) for t in T]
F['byte_cp_delta'] = [F['bytes'][i] - F['chars'][i] for i in range(NSRC)]
F['nul_faces'] = [len([1 for c in t if c == u'\x00']) for t in T]
F['digit_chars'] = [len([c for c in t if c.isdigit()]) for t in T]
F['dblspace'] = [cnt_ovl(t, u'  ') for t in T]
F['ascii_all'] = sum(1 for i in range(NSRC) if F['nonascii'][i] == 0)

# ---------- 头部动作字段 ----------
def hdr_ids(t, field):
    m = re.search(u'(?m)^' + field + u':\\s*(.+)$', t)
    if not m:
        return frozenset()
    return frozenset(int(x) for x in re.findall(u'\\d{3,5}', m.group(1)))


OBS = [hdr_ids(T[i], u'Obsoletes') for i in range(NSRC)]
UPD = [hdr_ids(T[i], u'Updates') for i in range(NSRC)]
F['obs_set_5077'] = sorted(OBS[1])
F['obs_set_8446'] = sorted(OBS[2])
F['upd_set_8446'] = sorted(UPD[2])
F['obs_n'] = [len(s) for s in OBS]
F['upd_n'] = [len(s) for s in UPD]
F['target_ids'] = sorted(set().union(*[set(s) for s in OBS + UPD]))
F['target_n'] = len(F['target_ids'])
F['obs_verb'] = [cnt_cur(T[i], u'Obsoletes') for i in range(NSRC)]
F['upd_verb'] = [cnt_cur(T[i], u'Updates') for i in range(NSRC)]
F['upd_line'] = [len([1 for x in L[i] if re.match(u'^\\s*Updates:', x)]) for i in range(NSRC)]
F['cat_std'] = [cnt_cur(T[i], u'Category: Standards Track') for i in range(NSRC)]
F['cat_hdr'] = [len([1 for x in L[i] if re.match(u'^\\s*Category:', x)]) for i in range(NSRC)]
F['issn'] = [cnt_cur(T[i], u'ISSN: 2070-1721') for i in range(NSRC)]
F['exp_n'] = [cnt_cur(T[i], u'Experimental') for i in range(NSRC)]
F['std_hdr'] = [len([1 for x in L[i] if re.match(u'^\\s*STD:\\s*\\d+', x)]) for i in range(NSRC)]

MON = u'January|February|March|April|May|June|July|August|September|October|November|December'
RYR = re.compile(u'(%s) +(\\d{4})\\s*$' % MON)


def hdr_year(lines):
    for x in lines[:60]:
        m = RYR.search(x.strip())
        if m:
            return (int(m.group(2)), m.group(1))
    return (None, None)


YR = [hdr_year(L[i]) for i in range(NSRC)]
F['years'] = [y for y, _ in YR]
F['months'] = [mo for _, mo in YR]
F['year_n'] = len([y for y in F['years'] if y])
order = sorted(range(NSRC), key=lambda i: F['years'][i])
F['year_perm'] = order
F['year_order'] = 1 if order == list(range(NSRC)) else 0
F['year_inversions'] = len([1 for a in range(NSRC) for b in range(a + 1, NSRC)
                            if F['years'][a] > F['years'][b]])
F['year_gaps'] = [F['years'][i + 1] - F['years'][i] for i in range(NSRC - 1)]

# ---------- 义务语气四轨 ----------
def ub(s, w):
    return len(re.findall(u'(?<![A-Za-z])' + w + u'(?![A-Za-z])', s))


UP = {}
LO = {}
CI = {}
TI = {}
WORDS = (u'MUST', u'MAY', u'SHOULD')
for w in WORDS:
    UP[w] = [ub(T[i], w) for i in range(NSRC)]
    LO[w] = [ub(T[i], w.lower()) for i in range(NSRC)]
    CI[w] = [ub(T[i].lower(), w.lower()) for i in range(NSRC)]
    TI[w] = [ub(T[i], w[:1].upper() + w[1:].lower()) for i in range(NSRC)]
UPN = {}
for w in (u'MUST NOT', u'MAY NOT', u'SHOULD NOT'):
    UPN[w] = [cnt_cur(T[i], w) for i in range(NSRC)]
F['up_must_all'] = UP[u'MUST']
F['up_may'] = UP[u'MAY']
F['up_should'] = UP[u'SHOULD']
F['must_not'] = UPN[u'MUST NOT']
F['should_not'] = UPN[u'SHOULD NOT']
F['may_not'] = UPN[u'MAY NOT']
F['must_bare'] = [UP[u'MUST'][i] - UPN[u'MUST NOT'][i] for i in range(NSRC)]
F['low_must'] = LO[u'MUST']
F['low_may'] = LO[u'MAY']
F['low_should'] = LO[u'SHOULD']
F['ci_must'] = CI[u'MUST']
F['ci_may'] = CI[u'MAY']
F['ci_should'] = CI[u'SHOULD']
F['title_must'] = TI[u'MUST']
F['title_may'] = TI[u'MAY']
F['title_should'] = TI[u'SHOULD']
F['case_ledger'] = [sum(CI[w][i] - UP[w][i] - LO[w][i] - TI[w][i] for w in WORDS)
                    for i in range(NSRC)]
F['up_ledger'] = [UP[u'MUST'][i] - (F['must_bare'][i] + UPN[u'MUST NOT'][i]) for i in range(NSRC)]
F['should_delete'] = [cnt_cur(FOLD[i], u'client should delete') for i in range(NSRC)]
F['must_cap_face'] = [cnt_cur(FOLD[i], u'must not use any value greater than') for i in range(NSRC)]

# ---------- 字段改名与答句词轨 ----------
FLD = {}
for base in (u'ticket_lifetime', u'ticket_lifetime_hint'):
    rx = re.compile(u'(?<![A-Za-z0-9_])' + base + u'(?![A-Za-z0-9_])')
    FLD[base] = [len(rx.findall(T[i])) for i in range(NSRC)]
F['fld_hint'] = FLD[u'ticket_lifetime_hint']
F['fld_plain'] = FLD[u'ticket_lifetime']
F['fld_sub'] = [cnt_cur(T[i], u'ticket_lifetime') for i in range(NSRC)]
F['fld_close'] = [F['fld_sub'][i] - (F['fld_hint'][i] + F['fld_plain'][i]) for i in range(NSRC)]
F['uint32_hint'] = [len([1 for x in L[i] if u'uint32 ticket_lifetime_hint;' in x]) for i in range(NSRC)]
F['uint32_plain'] = [len([1 for x in L[i] if u'uint32 ticket_lifetime;' in x]) for i in range(NSRC)]
F['hint_word'] = [cnt_cur(T[i], u'hint') for i in range(NSRC)]
F['zero_word'] = [cnt_cur(T[i], u'zero') for i in range(NSRC)]
F['unspec_word'] = [cnt_cur(T[i], u'unspecified') for i in range(NSRC)]
F['discard_low'] = [cnt_cur(T[i], u'discard') for i in range(NSRC)]
F['discard_cap'] = [cnt_cur(T[i], u'Discard') for i in range(NSRC)]
F['imm_word'] = [cnt_cur(T[i], u'immediately') for i in range(NSRC)]
F['seven_days'] = [cnt_cur(T[i], u'seven days') for i in range(NSRC)]
F['week_word'] = [cnt_cur(T[i], u'week') for i in range(NSRC)]
F['d24_hour'] = [cnt_cur(T[i], u'24-hour') for i in range(NSRC)]
F['reuse_word'] = [cnt_cur(T[i], u'reuse') for i in range(NSRC)]
F['orlonger'] = [cnt_cur(FOLD[i], u'shorter or longer') for i in range(NSRC)]
F['shorter_only'] = [cnt_cur(FOLD[i], u'valid for a shorter period') for i in range(NSRC)]
F['relative_in'] = [cnt_cur(FOLD[i], u'relative to when the ticket is received') for i in range(NSRC)]
F['from_issuance'] = [cnt_cur(FOLD[i], u'from the time of ticket issuance') for i in range(NSRC)]
F['lifetime_word'] = [cnt_cur(T[i], u'lifetime') for i in range(NSRC)]
F['session_ticket'] = [cnt_cur(T[i], u'NewSessionTicket') for i in range(NSRC)]
F['recv_time'] = [cnt_cur(FOLD[i], u'when the ticket is received') for i in range(NSRC)]

# ---------- 句内游标读数 ----------
NUM = {}
NUM['cap_faces'] = [0 if read_after(FOLD[i], u'value greater than ', u'(\\d+)') is None
                    else int(read_after(FOLD[i], u'value greater than ', u'(\\d+)')) for i in range(NSRC)]
NUM['cap_lit'] = [cnt_cur(T[i], u'604800') for i in range(NSRC)]
NUM['cap_days'] = [0 if read_after(FOLD[i], u'seconds (', u'(\\d+) days') is None
                   else int(read_after(FOLD[i], u'seconds (', u'(\\d+) days')) for i in range(NSRC)]
NUM['d24'] = int(read_after(FOLD[0], u'longer than the ', u'(\\d+)-hour'))
NUM['day_seconds'] = NUM['d24'] * 3600
NUM['cap_ratio'] = NUM['cap_faces'][2] // NUM['day_seconds']
NUM['cap_remainder'] = NUM['cap_faces'][2] % NUM['day_seconds']
NUM['cap_present_docs'] = sum(1 for x in NUM['cap_faces'] if x)
NUM['mod_pow'] = int(read_after(FOLD[2], u'modulo 2^', u'(\\d+)'))
NUM['ms_factor'] = 1000
NUM['sec_ms_close'] = NUM['mod_pow']
NUM['tls13_refs'] = [cnt_cur(T[i], u'[TLS13]') for i in range(NSRC)]
for k, v in NUM.items():
    F[u'num_' + k] = v

# ---------- 引用写法三式 ----------
CITE = {}
for n in (u'4507', u'5077', u'8446', u'9001', u'2246', u'4346', u'5246', u'6961', u'5705', u'6066'):
    CITE['sp_' + n] = [cnt_cur(T[i], u'RFC ' + n) for i in range(NSRC)]
    CITE['hy_' + n] = [cnt_cur(T[i], u'RFC-' + n) for i in range(NSRC)]
    CITE['tk_' + n] = [cnt_cur(T[i], u'RFC' + n) for i in range(NSRC)]
    CITE['al_' + n] = [CITE['sp_' + n][i] + CITE['hy_' + n][i] + CITE['tk_' + n][i] for i in range(NSRC)]
for k in CITE:
    F['cite_' + k] = CITE[k]
F['cite_forms_2246'] = [len([x for x in (u'sp', u'hy', u'tk') if CITE[x + u'_2246'][i]]) for i in range(NSRC)]
F['cite_forms_close'] = [len(re.findall(u'RFC[ -]?2246', T[i])) - CITE['al_2246'][i] for i in range(NSRC)]
F['cite_self'] = [CITE['al_' + n][i] for i, n in enumerate(LBL)]
F['cite_4507_in_5077'] = CITE['al_4507'][1]
F['cite_5077_in_8446'] = CITE['al_5077'][2]
F['cite_4507_in_8446'] = CITE['al_4507'][2]
F['cite_8446_in_9001'] = CITE['al_8446'][3]
F['cite_9001_in_8446'] = CITE['al_9001'][2]
F['cite_dir_5077_to_8446'] = CITE['al_5077'][2]
F['cite_dir_8446_to_9001'] = CITE['al_9001'][2]
F['cite_dir_9001_to_8446'] = CITE['al_8446'][3]
F['cite_8446_in_9001_sp'] = CITE['sp_8446'][3]

# ---------- 答句邻域窗(±BAND 行) ----------
BAND = 20
ANSND = {0: u'ticket_lifetime_hint field contains a hint', 1: u'relative to when the ticket is received',
         2: u'604800 seconds', 3: u'sets a limit of seven days'}
HEADND = {0: u'^3\\.3\\.', 1: u'^3\\.3\\.', 2: u'^4\\.6\\.1\\.', 3: u'^4\\.6\\.'}
ANS = ANSND


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
    fb = u' '.join(body.split())
    fo = u' '.join(outb.split())
    return {u'head': L[i][h - 1].strip() if h else None, u'sec': h, u'ans': a,
            u'head_ln': h, u'start': lo, u'end': hi, u'rows': hi - lo + 1,
            u'chars': len(body), u'chars_out': len(outb),
            u'lt_in': cnt_cur(fb, u'lifetime'), u'lt_out': cnt_cur(fo, u'lifetime'),
            u'zero_in': cnt_cur(fb, u'zero'), u'zero_out': cnt_cur(fo, u'zero'),
            u'cap_in': cnt_cur(fb, u'604800'), u'cap_out': cnt_cur(fo, u'604800'),
            u'reuse_in': cnt_cur(fb, u'reuse'), u'reuse_out': cnt_cur(fo, u'reuse'),
            u'dig_in': len([c for c in body if c.isdigit()]),
            u'dig_out': len([c for c in outb if c.isdigit()]),
            u'up_in': ub(fb, u'MUST') + ub(fb, u'MAY') + ub(fb, u'SHOULD'),
            u'up_out': ub(fo, u'MUST') + ub(fo, u'MAY') + ub(fo, u'SHOULD')}


WIN = [sec_window(i) for i in range(NSRC)]
for k in (u'head', u'sec', u'ans', u'start', u'end', u'rows', u'chars', u'chars_out',
          u'lt_in', u'lt_out', u'zero_in', u'zero_out', u'cap_in', u'cap_out',
          u'reuse_in', u'reuse_out', u'dig_in', u'dig_out', u'up_in', u'up_out'):
    F[u'win_' + k] = [w[k] for w in WIN]
F['win_band'] = BAND
F['win_named'] = len([w for w in WIN if w['sec']])
F['win_ans_named'] = len([w for w in WIN if w['ans']])
F['win_close_lt'] = [w['lt_in'] + w['lt_out'] - cnt_cur(FOLD[i], u'lifetime') for i, w in enumerate(WIN)]
F['win_close_zero'] = [w['zero_in'] + w['zero_out'] - cnt_cur(FOLD[i], u'zero') for i, w in enumerate(WIN)]
F['win_close_cap'] = [w['cap_in'] + w['cap_out'] - cnt_cur(FOLD[i], u'604800') for i, w in enumerate(WIN)]
F['win_close_reuse'] = [w['reuse_in'] + w['reuse_out'] - cnt_cur(FOLD[i], u'reuse') for i, w in enumerate(WIN)]
F['win_close_dig'] = [w['dig_in'] + w['dig_out'] - F['digit_chars'][i] for i, w in enumerate(WIN)]
F['win_close_sum'] = (sum(F['win_close_lt']) + sum(F['win_close_zero']) + sum(F['win_close_cap'])
                      + sum(F['win_close_reuse']) + sum(F['win_close_dig']))
F['win_spans'] = [w['end'] - w['start'] + 1 for w in WIN]

# ---------- 共用长行池与配对代数 ----------
def pool_lines(i):
    return [x for x in SH[i] if len(pnorm(x)) >= 40]


POOLC = [Counter(pnorm(x) for x in pool_lines(i)) for i in range(NSRC)]
NPOOL = [set(POOLC[i]) for i in range(NSRC)]
pool_all = set().union(*NPOOL)
tier = [0, 0, 0, 0]
pres = defaultdict(list)
for a in pool_all:
    ds = tuple(i for i in range(NSRC) if a in NPOOL[i])
    pres[a] = ds
    tier[len(ds) - 1] += 1
F['pool_n'] = len(pool_all)
F['pool_tier'] = tier
F['pool_tier_close'] = sum(tier) - len(pool_all)
F['pool_4'] = tier[3]
F['pool_3'] = tier[2]
F['pool_2'] = tier[1]
F['pool_1'] = tier[0]
PAIRS = [(a, b) for a, b in itertools.combinations(range(NSRC), 2)]
pair_share = []
pair_byte = []
pair_norm_only = []
for i, j in PAIRS:
    inter = NPOOL[i] & NPOOL[j]
    bo = sum(1 for s in inter if any(pnorm(x) == s and x in SH[j] for x in pool_lines(i)))
    pair_share.append(len(inter))
    pair_byte.append(bo)
    pair_norm_only.append(len(inter) - bo)
F['pair_share'] = pair_share
F['pair_byte'] = pair_byte
F['pair_norm_only'] = pair_norm_only
F['pair_nonzero'] = len([x for x in pair_share if x])
F['pair_close'] = sum(pair_share) - sum(pair_byte) - sum(pair_norm_only)
F['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
mx = max(pair_share)
F['pair_max'] = mx
F['pair_max_idx'] = pair_share.index(mx)
F['pair_max_byte'] = pair_byte[F['pair_max_idx']]
F['pair_max_norm_only'] = pair_norm_only[F['pair_max_idx']]
F['pair_max_lbl'] = F['pair_lbl'][F['pair_max_idx']]
F['s3_examples'] = sorted([a for a, v in pres.items() if len(v) >= 3])
F['tri_share'] = [len([a for a, v in pres.items() if len(v) >= 3 and i in v]) for i in range(NSRC)]
_t1 = sum(len(v) for v in pres.values())
_t2 = sum(len(v) * (len(v) - 1) // 2 for v in pres.values())
_t3 = sum(len(v) * (len(v) - 1) * (len(v) - 2) // 6 for v in pres.values())
_t4 = len([v for v in pres.values() if len(v) == NSRC])
F['pool_incl'] = [_t1, _t2, _t3, _t4]
F['union_incl'] = _t1 - _t2 + _t3 - _t4
F['union_close'] = F['pool_n'] - F['union_incl']
letters = re.compile(u'[A-Za-z]')
F['pool_letters'] = len([a for a in pool_all if letters.search(a)])
F['pool_border'] = F['pool_n'] - F['pool_letters']
F['shared_norm_only'] = sum(pair_norm_only)

# ---------- 写法分家轴 ----------
axis = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
for a, v in pres.items():
    if len(v) < 2:
        continue
    xs = set()
    for i in v:
        xs |= set(x for x in SH[i] if pnorm(x) == a)
    if len(xs) < 2:
        continue
    o, p = sorted(xs)[0], sorted(xs)[1]
    if len(o) == len(p) and o != p and all(x.lower() == y.lower() for x, y in zip(o, p)):
        axis[u'case'] += 1
    elif (u'-' in o) != (u'-' in p):
        axis[u'hyph'] += 1
    elif len(re.split(u' +', o.strip())) == len(re.split(u' +', p.strip())):
        axis[u'space'] += 1
    else:
        axis[u'multi'] += 1
F['axis_counts'] = axis
F['axis_total'] = sum(axis.values())
F['norm_only_set'] = len([a for a, v in pres.items() if len(v) >= 2
                          and len(set(x for i in v for x in SH[i] if pnorm(x) == a)) > 1])
F['axis_close'] = F['axis_total'] - F['norm_only_set']
F['axis_str'] = u'⇎'.join(u'%s%d' % (a, axis[a]) for a in (u'case', u'hyph', u'space', u'multi'))
F['axis_str_n'] = len([a for a in (u'case', u'hyph', u'space', u'multi') if axis[a]])

# ---------- 锚候选池 ----------
apool = []
for i in range(NSRC):
    for x in SH[i]:
        if len(pnorm(x)) >= 24 and letters.search(x):
            apool.append((pnorm(x), i))
AP = defaultdict(set)
for a, i in apool:
    AP[a].add(i)
F['apool_n'] = len(AP)
F['apool_raw_n'] = len(apool)
F['apool_face_raw'] = [len([1 for a, k in apool if k == i]) for i in range(NSRC)]
F['apool_tag_n'] = [len([a for a, v in AP.items() if i in v]) for i in range(NSRC)]
F['apool_dup'] = [F['apool_face_raw'][i] - F['apool_tag_n'][i] for i in range(NSRC)]
F['apool_tag_close'] = sum(F['apool_tag_n']) + sum(F['apool_dup']) - F['apool_raw_n']
F['apool_tier'] = [len([a for a, v in AP.items() if len(v) == n]) for n in range(1, NSRC + 1)]
F['apool_uniq'] = len(AP)
F['apool_pairs'] = sum(F['apool_tag_n'])
F['apool_weight'] = sum(F['apool_tier'][n] * (n + 1) for n in range(NSRC))
F['apool_tier_close'] = F['apool_weight'] - F['apool_pairs']
F['apool_maxlen'] = max(len(a) for a in AP)

# ---------- 闭合判定 ----------
CLOSE = {}
CLOSE[u'zero_flip'] = 1 if (F['n_z4507_zero_reserved'][0] and F['n_z5077_zero_reserved'][1]
                            and F['n_z8446_zero_discard'][2] and not F['n_z9001_zero'][3]) else 0
CLOSE[u'zero_res_agree'] = 0 if (F['n_z4507_zero_reserved'][0] and F['n_z5077_zero_reserved'][1]) else 1
CLOSE[u'zero_ind_unique'] = 0 if (F['n_z8446_zero_discard'][2] == 1
                                  and sum(F['n_z8446_zero_discard'][i] for i in (0, 1, 3)) == 0) else 1
CLOSE[u'cap_unique'] = 0 if NUM['cap_present_docs'] == 1 else 1
CLOSE[u'cap_ratio_close'] = 0 if (NUM['cap_ratio'] == NUM['cap_days'][2] == 7
                                  and NUM['cap_remainder'] == 0) else 1
CLOSE[u'day_lt_cap'] = 0 if NUM['day_seconds'] < NUM['cap_faces'][2] else 1
CLOSE[u'drop_or_longer'] = 1 if (F['orlonger'][0] == F['orlonger'][1] == 1
                                 and F['orlonger'][2] == 0 and F['shorter_only'][2] == 1) else 0
CLOSE[u'rel_inserted'] = 1 if (F['relative_in'][1] >= 1 and F['relative_in'][0] == 0
                               and F['recv_time'][1] >= 1 and F['recv_time'][0] == 0) else 0
CLOSE[u'from_issuance_only'] = 1 if (F['from_issuance'][2] == 1
                                     and sum(F['from_issuance'][i] for i in (0, 1, 3)) == 0) else 0
CLOSE[u'field_renamed'] = 1 if (sum(F['fld_hint'][2:]) == 0 and F['uint32_hint'][0] == 1
                                and F['uint32_hint'][1] == 1 and F['uint32_plain'][2] >= 1) else 0
CLOSE[u'reuse_absent'] = 1 if (F['n_z9001_reuse'][3] and F['n_z8446_reuse'][2]
                               and F['n_z9001_reuse'][0] + F['n_z9001_reuse'][1] == 0) else 0
CLOSE[u'delegates'] = 1 if (F['n_z9001_seven_days'][3] and F['seven_days'][3] >= 1
                            and F['lifetime_word'][3] >= 1) else 0
CLOSE[u'no_self_lifetime'] = 1 if (F['must_cap_face'][3] == 0 and NUM['cap_lit'][3] == 0
                                   and F['n_z9001_zero'][3] == 0) else 0
CLOSE[u'week_only_8446'] = 1 if (F['week_word'][2] and F['week_word'][0] + F['week_word'][1]
                                 + F['week_word'][3] == 0) else 0
CLOSE[u'24hour_pair'] = 0 if (F['d24_hour'][0] == F['d24_hour'][1] == 1
                              and F['d24_hour'][2] == F['d24_hour'][3] == 0) else 1
CLOSE[u'year_order'] = 0 if (F['year_inversions'] == 0 and F['year_order'] == 1) else 1
CLOSE[u'cat_close'] = 0 if sum(F['cat_std']) == sum(F['cat_hdr']) == NSRC else 1
CLOSE[u'obs_5077_unique'] = 0 if F['obs_n'][1] == 1 else 1
CLOSE[u'chain_closed'] = 1 if (5077 in OBS[2] and not (4507 in OBS[2] or 4507 in UPD[2])
                               and F['obs_n'][1] == 1) else 0
CLOSE[u'cite_dir'] = 1 if (F['cite_5077_in_8446'] and not F['cite_dir_8446_to_9001']
                           and F['cite_4507_in_5077']) else 0
CLOSE[u'up_zero_9001_cap'] = 0 if (F['must_cap_face'][3] == 0) else 1
for k in CLOSE:
    F[k] = CLOSE[k]
ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"F['pair_close']", u'两两“归一同形”减“逐字节同形”再减“只归一同形”应回到零(池代数闭合)')
Z(u"F['pool_tier_close']", u'共用长行按份数分档之和=池条数')
Z(u"F['axis_close']", u'写法分家轴四桶之和=“归一同形而逐字节不同”的条数')
Z(u"F['union_close']", u'按份数加权和=单份集合大小之和−两两交+…(容斥对账)')
Z(u"F['apool_tier_close']", u'锚候选池按“几份面上出现”加权分档之和=池条目数')
Z(u"F['apool_tag_close']", u'锚候选池按标签分布之和=池条目数')
Z(u"F['ladder_monotone'] - 1", u'三面阶梯单调: 逐行档 + 折行独有档 = 折平档')
Z(u"F['re_eq_cur'] - 1", u'正则字面轨与非重叠游标轨在同一批针上逐枚相等')
Z(u"F['overlap_extra']", u'重叠口径减非重叠口径在全库针上合计为零')
Z(u"F['fold_line_zero']", u'折行独有的针按逐行口径必须全为零')
Z(u"sum(F['sh_minus_fold'])", u'摘壳折平档一枚不丢(壳行里没有答句)')
Z(u"sum([abs(x) for x in F['up_ledger']])", u'大写 MUST 总数 = 裸 MUST + MUST NOT')
Z(u"sum([abs(x) for x in F['case_ledger']])", u'每份面: 大写档+小写档+首字母大写档=不分大小写档')
Z(u"F['win_close_sum']", u'答句邻域窗五轨(lifetime⇎zero⇎604800⇎reuse⇎数字符)带内+带外=全篇')
Z(u"len(F['s3_examples']) - (F['pool_3'] + F['pool_4'])", u'三份及以上同现的共用长行枚数=池分档第三+第四档')
Z(u"CLOSE['zero_flip'] - 1", u'零值语义翻转判定: 4507⇎5077=未定, 8446=立即丢弃, 9001 面上连这句都没有')
Z(u"CLOSE['zero_res_agree']", u'“零值=未定”那枚整句在 4507 与 5077 面上都读得到')
Z(u"CLOSE['zero_ind_unique']", u'“零=立即丢弃”句式全库只 8446 一枚')
Z(u"CLOSE['cap_unique']", u'604800 这枚读数全库只有一份给得出')
Z(u"CLOSE['cap_ratio_close']", u'604800 秒 = 7 日整(游标倍率与括注日数同枚、余零)')
Z(u"CLOSE['day_lt_cap']", u'24 小时的秒数严格小于硬上限')
Z(u"CLOSE['drop_or_longer'] - 1", u'“shorter or longer”在 8446 被砍成“shorter”: 前两份各一枚、8446 零枚而其变体一枚')
Z(u"CLOSE['rel_inserted'] - 1", u'relative to when the ticket is received 只活在 5077 面(4507 零枚)')
Z(u"CLOSE['from_issuance_only'] - 1", u'“from the time of ticket issuance”只 8446 一枚(起算点被换掉)')
Z(u"CLOSE['field_renamed'] - 1", u'ticket_lifetime_hint 在 8446⇎9001 面上零枚, uint32 声明行前两份各一枚 ⇎ 8446 现 plain 式')
Z(u"CLOSE['reuse_absent'] - 1", u'“不得复用票据”只在 8446⇎9001 两份面上, 4507/5077 零枚')
Z(u"CLOSE['delegates'] - 1", u'9001 不自建时长: 七日上限那句带 [TLS13] 主语, 而 lifetime 一词它仍用')
Z(u"CLOSE['no_self_lifetime'] - 1", u'9001 面上读不到 MUST NOT use any value greater than ⇎ 604800 ⇎ “A value of zero”')
Z(u"CLOSE['week_only_8446'] - 1", u'week 这个词只有 8446 用(“restricted to a week”), 其余三份零枚')
Z(u"CLOSE['24hour_pair']", u'24-hour 恰在 4507⇎5077 各一枚, 后两份零枚')
Z(u"CLOSE['year_order']", u'标题页年份 2006→2008→2018→2021 严格递增、零倒序(与 B70 恰有一处倒序对照)')
Z(u"CLOSE['cat_close']", u'四份的 Category: 行全是 Standards Track(在库字节只给得出这个名分)')
Z(u"CLOSE['obs_5077_unique']", u'5077 的 Obsoletes: 头恰一枚对象')
Z(u"CLOSE['chain_closed'] - 1", u'废止链: 5077←8446 逐号可查, 而 4507 只被 5077 废止、不出现在 8446 的头里')
Z(u"CLOSE['cite_dir'] - 1", u'互引单向: 5077 引 4507 ⇎ 8446 引 5077 ⇎ 8446 面上读不到 9001')
Z(u"sum(F['cr'])", u'四份 CR 全零(纯 LF 面)')
Z(u"sum(F['nul_faces'])", u'四份面上 NUL 全零')
Z(u"sum(F['bom']) - 1", u'BOM 恰一枚: 只有 9001 带')
Z(u"max([abs(F['byte_cp_delta'][i] - F['nonascii_extra'][i]) for i in range(NSRC)])",
  u'字节数−码位数 = 每枚非 ASCII 码位的 utf-8 加字节数(9001 的差恰由 BOM+取变音符补足)')
Z(u"F['ascii_all'] - (NSRC - 1)", u'四份里三份是纯 ASCII 面')
Z(u"F['ff'][3]", u'9001 零换页符 ⇒ 阶梯第三档对它是空操作')
Z(u"len([1 for i in range(NSRC) if F['ff'][i]]) - (NSRC - 1)", u'带换页符的恰是前三份')
Z(u"sum(F['cite_forms_close'])", u'2246 的子串三式相加=一条正则族读出的枚数(写法族账闭合)')
Z(u"F['win_named'] - F['win_ans_named']", u'四份都定位到答句行与节标题行')
Z(u"F['num_cap_lit'][2] - F['n_z8446_cap'][2]", u'8446 面上 604800 字面枚数=那句大写 MUST NOT 的游标枚数')
Z(u"F['fld_close'][0] - F['fld_close'][1]", u'字段名带下划线时用词界正则: plain 计数−hint 计数在前两份一致(改名只发生在后两份)')
Z(u"F['n_z4507_no_relative'][0]", u'4507 面上“relative to when the ticket is received”整句零命中(反向针)')
Z(u"F['n_z5077_zero_reserved'][0]", u'“零=未定”那枚连句号整句针在 4507 的全篇折平面上落空(页壳插在句中)')
Z(u"F['n_z8446_shorter_only'][0]", u'8446 的“只剩 shorter”句式在 4507 面上零命中')
Z(u"F['n_z9001_lifetime_word'][3] - F['lifetime_word'][3]", u'lifetime 的针轨与全篇词轨在 9001 面上同数')
Z(u"F['num_day_seconds'] - 24 * 3600", u'24 小时的秒数由游标读出的时数现乘')
Z(u"sum(F['needles_owned']) - F['needle_n']", u'按份名下的针数相加=在册针总数(登记账不漏不重)')
Z(u"F['axis_total'] - F['norm_only_set']", u'写法分家轴四桶之和=“归一同形而逐字节不同”的去重串数')
Z(u"F['must_cap_face'][0] + F['must_cap_face'][1]", u'4507⇎5077 面上都读不到那句 MUST NOT 上限(折平口径)')
Z(u"F['fld_close'][0] + F['fld_close'][1] + F['fld_close'][2] + F['fld_close'][3]",
  u'词界正则把 ticket_lifetime 的每种写法分干净: 子串计数=hint式+plain式(改名前后都不漏)')
Z(u"sum(F['zero_carry_sh']) - 2*len(F['zero_carry_sh']) + 2",
  u'摘壳折平面上那枚零值整句在对方两份面上各命中一次(逐字搬运, 只是行被页壳劈开)')
Z(u"F['zero_carry_fold'][1]",
  u'含页壳的全篇折平面上 4507 读不到 5077 那句整句(壳把句子劈开: 读到非零即为失败态)')
F['zid_n'] = len(ZID)
ZF = [w for e, w in ZID if eval(e.strip().replace(u'\n', u''))]
F['zid_fail'] = ZF


def _ev(e):
    return eval(e.strip().replace(u'\n', u''))


for e, w in ZID:
    if _ev(e):
        print(u'  失败: ' + w + u' <= ' + e.strip() + u' -> ' + repr(_ev(e)))
F['scalar_clos_n'] = len(ZID)
F['scalar_clos_sum'] = sum(1 for e, w in ZID if not _ev(e))
F['list_clos_n'] = len([k for k in F if (u'_close' in k or u'_ledger' in k) and isinstance(F[k], list)])
F['x_ident_n'] = len(ZID)
# --- SCAN END ---
# ---------- ZID 的 B71V 形(与 python 形逐条对拍后送 DERIV) ----------
BB71 = lambda name, i=None: (F[name] if i is None else F[name][i])
FN = u'B71V'
_to_v = re.compile(r"(?:F|CLOSE)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B71V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(4)').replace(u'NSRC', u'4')


ZV = []
for e, w in ZID:
    v = to_v(e.replace(u'\n', u''))
    if eval(v, {FN: BB71}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))

print(u'第二遍量测完成: 扁平键 %d ｜ 恒等式 %d ｜ 失败 %d ｜ 针 %d ｜ 池 %d ｜ 锚池 %d' %
      (len(F), len(ZID), len(ZF), len(SN), F['pool_n'], F['apool_n']))
print(u'结构 bytes=%s chars=%s lines=%s nonblank=%s maxlen=%s' % (F['bytes'], F['chars'], F['lines'], F['nonblank'], F['maxlen']))
print(u'版式 ff=%s ff_exact=%s ff_only=%s shell=%s strip=%s cr=%s nonascii=%s bom=%s extra=%s delta=%s digit=%s'
      % (F['ff'], F['ff_exact'], F['ff_only'], F['shell_n'], F['shell_strip'], F['cr'], F['nonascii'],
         F['bom'], F['nonascii_extra'], F['byte_cp_delta'], F['digit_chars']))
print(u'阶梯 strict=%s fold=%s shell=%s re=%s fold_only=%d(%s) sh_lost=%s overlap=%d re_eq=%d'
      % (F['sn_strict_docs'], F['sn_fold_docs'], F['sn_sh_docs'], F['sn_re_docs'],
         len(F['fold_only_keys']), F['fold_only_own'], F['sh_lost_keys'], F['overlap_extra'], F['re_eq_cur']))
print(u'义务 大写MUST=%s bare=%s MUSTNOT=%s SHOULDNOT=%s MAY=%s SHOULD=%s | 小写must=%s | 无视大小写must=%s | 账=%s 案例=%s'
      % (F['up_must_all'], F['must_bare'], F['must_not'], F['should_not'], F['up_may'], F['up_should'],
         F['low_must'], F['ci_must'], F['up_ledger'], F['case_ledger']))
print(u'词轨 fld_hint=%s fld_plain=%s close=%s uint32=%s/%s hint=%s zero=%s unspec=%s imm=%s seven=%s week=%s d24=%s reuse=%s orlonger=%s shorter_only=%s rel=%s issuance=%s recv=%s'
      % (F['fld_hint'], F['fld_plain'], F['fld_close'], F['uint32_hint'], F['uint32_plain'], F['hint_word'],
         F['zero_word'], F['unspec_word'], F['imm_word'], F['seven_days'], F['week_word'], F['d24_hour'],
         F['reuse_word'], F['orlonger'], F['shorter_only'], F['relative_in'], F['from_issuance'], F['recv_time']))
print(u'数读 %s' % (NUM,))
print(u'头部 obs=%s upd=%s target=%s cat=%s issn=%s exp=%s std=%s years=%s months=%s gaps=%s inv=%d' % (
    F['obs_n'], F['upd_n'], F['target_ids'], F['cat_std'], F['issn'], F['exp_n'], F['std_hdr'],
    F['years'], F['months'], F['year_gaps'], F['year_inversions']))
print(u'判定 %s' % (CLOSE,))
print(u'窗 head=%s sec=%s ans=%s rows=%s lt=%s/%s zero=%s/%s cap=%s/%s reuse=%s/%s up=%s 闭合=%s' % (
    F['win_head'], F['win_sec'], F['win_ans'], F['win_rows'], F['win_lt_in'], F['win_lt_out'],
    F['win_zero_in'], F['win_zero_out'], F['win_cap_in'], F['win_cap_out'],
    F['win_reuse_in'], F['win_reuse_out'], F['win_up_in'], F['win_close_sum']))
print(u'池 n=%d tier=%s letters=%d border=%d pair_share=%s 最大对=%s(%d) 字节对=%s 仅归一=%s 闭合=%d/%d/%d 轴=%s 锚池=%d'
      % (F['pool_n'], F['pool_tier'], F['pool_letters'], F['pool_border'], F['pair_share'],
         F['pair_max_lbl'], F['pair_max'], F['pair_byte'], F['pair_norm_only'],
         F['pair_close'], F['union_close'], F['pool_tier_close'], F['axis_counts'], F['apool_n']))
print(u'引用 4507=%s 5077=%s 8446=%s 2246=%s 4346=%s tls13=%s 自指=%s 形式账=%s' % (
    F['cite_al_4507'], F['cite_al_5077'], F['cite_al_8446'], F['cite_al_2246'], F['cite_al_4346'],
    F['num_tls13_refs'], F['cite_self'], F['cite_forms_close']))

# ---------- 锚(逐字原行, 由位置导出) ----------
IDX = {t: n for n, t in enumerate(LBL)}
FAN = FO
ATOMFAIL = []


def AN(i, *nd):
    for l in L[i]:
        if all(x in l for x in nd):
            return u'⟦%s⟧⟨%s⟩' % (LBL[i], l)
    ATOMFAIL.append((LBL[i], nd))
    raise AssertionError(u'锚导出失败 %s %s' % (LBL[i], nd))


# ---------- DERIV 登记 ----------
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


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB71}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([tuple(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out

exec(io.open(u'corpus/_mk71emit.py', encoding='utf-8').read())
