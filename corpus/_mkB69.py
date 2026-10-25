# -*- coding: utf-8 -*-
"""建条目第二遍(B69): 主动关闭一条 TCP 连接之后到底要等多久才能重用同一对端口/同一批序列号,
交四份一手文书各答一遍: 793(81) 任意定 MSL=2 分钟且许可违背 quiet time ⇎ 1122(89) 定死 MUST linger 2xMSL 但给两条件出口
⇎ 6528(12) 干脆不靠等待、改按“最后见到报文起算 2*MSL”并换掉 ISS 生成法 ⇎ 9293(22) 逐字收下 793 那句 2 分钟、
把主语改成 endpoint、数式写成 2MSL 而非 2xMSL, 并把前两份连同 6528 一起 Obsoletes。

本遍刻意与采集侧换实现: 采集侧用 str.count/逐行 in 判定, 本遍用游标逐字符、正则、集合代数与 itertools;
键名一律等于所量之物。所有正文数字都经 V()/D()/LIT() 注册后插值, 没有一枚是手打的。"""
import io, itertools, json, re, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
TAGS = [u'A', u'B', u'C', u'D']
LBL = [u'793', u'1122', u'6528', u'9293']
YR = [u'81', u'89', u'12', u'22']
NSRC = 4
PATH = [u'corpus/raw/tcpTW/rfc793.txt', u'corpus/raw/tcpRTO/rfc1122.txt',
        u'corpus/raw/tcpTW/rfc6528.txt', u'corpus/raw/tcpTW/rfc9293.txt']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire69.py 把这一段 ⇎ _mk69emit.py 的 SCAN2 段机械切进 audit.py::_b69_scan)


def rd(p):
    s = io.open(p, encoding='utf-8', errors='replace').read()
    return s


T = [rd(p) for p in PATH]
L = [t.split(u'\n') for t in T]


def pnorm(s):
    return u' '.join(s.lower().split())


FO = [pnorm(t) for t in T]
# 摘壳面: 去掉页眉行/分页符/[Page n] 页脚行后再折平(9293 无分页符, 它的壳只有首部块)
def hdr_line(l):
    return bool(re.match(u'^\\s*RFC\\d+\\s+\\S.*\\s([A-Z][a-z]+)\\s+\\d{4}\\s*$', l)) or \
        bool(re.match(u'^[A-Z]+\\d+\\s+.{5,}.*\\s\\d{4}\\s*$', l)) or \
        bool(re.match(u'^RFC\\s+\\d+\\s+\\S', l))


def foot_line(l):
    return bool(re.match(u'^\\s*\\[?Page \\d+\\]?\\s*$', l)) or bool(re.match(u'^\\s*\\[Page \\d+\\]\\s*$', l))


def shell_strip(t):
    out = []
    for l in t.split(u'\n'):
        if u'\x0c' in l or hdr_line(l) or foot_line(l):
            continue
        out.append(l)
    return u'\n'.join(out)


SH = [pnorm(shell_strip(t)) for t in T]


def cnt_cur(t, nd):
    """游标逐字符数出现处(不用 str.count)"""
    n, i = 0, 0
    while True:
        j = t.find(nd, i)
        if j < 0:
            return n
        n += 1
        i = j + 1


def line_of(t, nd, k=0):
    """返回第 k 枚含 nd 的原文件行(逐字符扫描, 不切行)"""
    i, seen = 0, 0
    while True:
        j = t.find(nd, i)
        if j < 0:
            return None
        if seen == k:
            a = t.rfind(u'\n', 0, j) + 1
            b = t.find(u'\n', j)
            return t[a:b if b >= 0 else len(t)]
        seen += 1
        i = j + 1


# ---------- 字面针(与采集侧同一批文本, 判定换成游标+折平双档) ----------
NEEDLE = [
    (0, u'a_quiet', u'the TCP must keep quiet for a maximum segment lifetime'),
    (0, u'a_msl2', u'For this specification the MSL is taken to be 2 minutes.'),
    (0, u'a_eng', u'is an engineering choice, and may be changed if experience indicates'),
    (0, u'a_violate', u'TCP implementors may violate the "quiet time" restriction, but only'),
    (0, u'a_arb2', u'Arbitrarily defined to be 2 minutes.'),
    (0, u'a_isn455', u'Thus, the ISN cycles approximately every 4.55 hours.'),
    (0, u'a_lt455', u'the MSL is less than 4.55'),
    (0, u'a_fig', u'Timeout=2MSL'),
    (1, u'b_linger', u'TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime).'),
    (1, u'b_mayaccept', u'However, it MAY accept a new SYN from the remote TCP to'),
    (1, u'b_cond1', u'assigns its initial sequence number for the new'),
    (1, u'b_cond2', u'returns to TIME-WAIT state if the SYN turns out to be'),
    (1, u'b_busy', u'local socket) pair that defines the connection is busy'),
    (1, u'b_shorten', u'port pair is tied up, some TCPs allow a new SYN to be'),
    (1, u'b_ka', u'Implementors MAY include "keep-alives" in their TCP'),
    (2, u'c_star', u'previous connection before 2*MSL have passed since a segment'),
    (2, u'c_lastseen', u'corresponding to the old incarnation was last seen (where "MSL" is'),
    (2, u'c_twref', u'the TIME-WAIT state and TCP\'s "quiet time" concept (see Appendix B of'),
    (2, u'c_quiettwo', u'kept or a quiet time observed for two maximum segment lifetimes'),
    (3, u'd_linger', u'When a connection is closed actively, it MUST linger in the TIME-WAIT'),
    (3, u'd_msl2', u'For this specification the MSL is taken to be 2 minutes.'),
    (3, u'd_endpoint', u'the TCP endpoint must keep quiet for an MSL'),
    (3, u'd_clockmust', u'A TCP implementation MUST use the above type of "clock" for clock-'),
    (3, u'd_paws', u'it is recommended to implement the'),
    (3, u'd_obsoletes', u'Obsoletes: 793, 879, 2873, 6093, 6429, 6528,'),
]
FOLD = [
    (0, u'a_eng_whole', u'This is an engineering choice, and may be changed if experience indicates it is desirable to do so.'),
    (1, u'b_two_both', u'it MUST linger in TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime). However, it MAY accept a new SYN'),
    (3, u'd_quiet_whole', u'the TCP endpoint must keep quiet for an MSL before assigning any sequence numbers upon starting up or recovering from a situation where memory of sequence numbers in use was lost.'),
]
ALLN = [(i, k, nd, u'line') for i, k, nd in NEEDLE] + [(i, k, nd, u'fold') for i, k, nd in FOLD]
SN = {}
SNF = {}
SNS = {}
SNS = {}
FOLDLINE = {}
KIND = {}
OWNER = {}
for i, k, nd, kind in ALLN:
    KIND[k] = kind
    OWNER[k] = i
    LITK[k] = nd
    FOLDLINE[k] = [len([1 for l in L[x] if nd in l]) for x in range(NSRC)]
    nf = pnorm(nd)
    SNF[k] = [1 if nf in FO[x] else 0 for x in range(NSRC)]
    SNS[k] = [1 if nf in SH[x] else 0 for x in range(NSRC)]
SN = FOLDLINE
KEYS = [k for _, k, _, _ in ALLN]
F['needle_n'] = len(KEYS)
F['sn_strict_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SN[k][i] > 0) for i in range(NSRC)]
F['sn_fold_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SNF[k][i]) for i in range(NSRC)]
F['sn_sh_docs'] = [sum(1 for k in KEYS if OWNER[k] == i and SNS[k][i]) for i in range(NSRC)]
F['fold_only_keys'] = [k for k in KEYS if sum(SN[k]) == 0 and sum(SNF[k]) > 0]
F['fold_only_own'] = [sum(1 for k in KEYS if OWNER[k] == i and SN[k][i] == 0 and SNF[k][i])
                      for i in range(NSRC)]
F['sh_only_keys'] = [k for k in KEYS if SNS[k][OWNER[k]] and not SNF[k][OWNER[k]]]
F['sh_lost_keys'] = [k for k in KEYS if SNF[k][OWNER[k]] and not SNS[k][OWNER[k]]]
F['ladder_monotone'] = 1 if all(F['sn_strict_docs'][i] + F['fold_only_own'][i] == F['sn_fold_docs'][i]
                                for i in range(NSRC)) else 0
F['sh_minus_fold'] = [F['sn_fold_docs'][i] - F['sn_sh_docs'][i] for i in range(NSRC)]
F['fold_line_zero'] = sum(1 for _, k, _, kind in ALLN if kind == u'fold'
                          for i in range(NSRC) if i != OWNER[k] and SN[k][i] > 0)
F['shared_verbatim'] = [k for k in KEYS if sum(1 for i in range(NSRC) if SN[k][i]) >= 2]
F['msl2_two_docs'] = [SN[u'a_msl2'][0], SN[u'd_msl2'][3]]
F['msl2_same_bytes'] = 1 if SN[u'a_msl2'][0] and SN[u'a_msl2'][3] else 0
F['quiet_rewritten'] = 0 if SN[u'a_quiet'][3] else 1

# ---------- 结构面量(游标/正则, 与采集侧的 str.count 分流) ----------
F['bytes'] = [len(t.encode('utf-8')) for t in T]
F['chars'] = [len(t) for t in T]
F['lines'] = [len(t.split(u'\n')) for t in T]
F['nonblank'] = [len([x for x in l if x.strip() != u'']) for l in L]
F['ff'] = [cnt_cur(t, u'\x0c') for t in T]
F['ff_only'] = [len([x for x in l if x == u'\x0c']) for l in L]
F['cr'] = [cnt_cur(t, u'\r') for t in T]
F['nonascii'] = [len([c for c in t if ord(c) > 127]) for t in T]
F['bom'] = [1 if t.startswith(u'﻿') else 0 for t in T]
F['byte_cp_delta'] = [F['bytes'][i] - len([1 for c in T[i]]) for i in range(NSRC)]
TOK = {u'msl': u'MSL', u'tw': u'TIME-WAIT', u'f2msl': u'2MSL', u'f2x': u'2xMSL',
       u'f2star': u'2*MSL', u'f2xsp': u'2 x MSL', u'quiet': u'quiet', u'linger': u'linger',
       u'twospace': u'TIME-WAIT state', u'iss': u'ISS', u'isn': u'ISN', u'timestamp': u'Timestamp',
       u'ka': u'keep-alive', u'kabare': u'keepalive', u'obsoletes': u'Obsoletes:',
       u'updates': u'Updates:', u'std': u'STD:', u'issn': u'ISSN',
       u'cat_std': u'Category: Standards Track', u'cat_info': u'Category: Informational',
       u'r793d': u'RFC-793', u'r793s': u'RFC 793', u'r1122s': u'RFC 1122', u'r1122d': u'RFC-1122',
       u'c2m': u'2 minutes', u'four_us': u'4 microseconds', u'h455': u'4.55 hours',
       u'reboot': u'reboot', u'must_not': u'MUST NOT'}
for k, nd in TOK.items():
    F[k] = [cnt_cur(t, nd) for t in T]
F['form_all'] = [F[u'f2msl'][i] + F[u'f2x'][i] + F[u'f2star'][i] + F[u'f2xsp'][i]
                 for i in range(NSRC)]
F['form_distinct'] = [len([1 for k in (u'f2msl', u'f2x', u'f2star', u'f2xsp') if F[k][i]])
                      for i in range(NSRC)]
F['form_docs'] = [len([1 for i in range(NSRC) if F[k][i]]) for k in
                  (u'f2msl', u'f2x', u'f2star', u'f2xsp')]
F['must_bare'] = [len(re.findall(u'\\bMUST(?! NOT)\\b', t)) for t in T]
F['up_must'] = F['must_bare']
F['up_must_all'] = [cnt_cur(t, u'MUST') for t in T]
F['up_should'] = [cnt_cur(t, u'SHOULD') for t in T]
F['up_may'] = [cnt_cur(t, u'MAY') for t in T]
F['up_ledger'] = [F['up_must_all'][i] - F['must_bare'][i] - F[u'must_not'][i] for i in range(NSRC)]
F['sec_must_not'] = F[u'must_not']
F['nonascii_extra'] = [sum(len(c.encode('utf-8')) - 1 for c in t if ord(c) > 127) for t in T]
F['nonascii_set'] = sorted(set(hex(ord(c)) for c in T[3] if ord(c) > 127))

# ---------- 句内游标读数: 数一个都不手填 ----------
NUM = {}


def read_after(i, pre, key):
    m = re.search(re.escape(pre) + u'(\\d+)', T[i])
    NUM[key] = int(m.group(1)) if m else None
    LITK[key] = pre + u'<NUM>'
    return NUM[key]


def read_before(i, suf, key):
    m = re.search(u'(\\d+)' + re.escape(suf), T[i])
    NUM[key] = int(m.group(1)) if m else None
    LITK[key] = u'<NUM>' + suf
    return NUM[key]


NUM[u'minutes_a'] = read_after(0, u'MSL is taken to be ', u'minutes_a')
NUM[u'minutes_d'] = read_after(3, u'MSL is taken to be ', u'minutes_d')
NUM[u'hours_a'] = read_after(0, u'the ISN cycles approximately every ', u'hours_a')
NUM[u'usec_a'] = read_after(0, u'incremented roughly every ', u'usec_a')
NUM[u'usec_d'] = read_after(3, u'once every roughly ', u'usec_d')
NUM[u'minutes_arb'] = read_after(0, u'Arbitrarily defined to be ', u'minutes_arb')
NUM[u'twoms_a'] = read_after(0, u'Timeout=', u'twoms_a')
F['isn_bits'] = [len(re.findall(u'32 bit ISN|32-bit counter|32 bit', t)) for t in T]
F['wrap_hours'] = [cnt_cur(t, u'4.55 hours') for t in T]
CLOSE = {}
CLOSE[u'minutes_agree'] = 0 if NUM[u'minutes_a'] == NUM[u'minutes_d'] else 1
CLOSE[u'arb_eq_spec'] = 0 if NUM[u'minutes_arb'] == NUM[u'minutes_a'] else 1
CLOSE[u'usec_agree'] = 0 if NUM[u'usec_a'] == NUM[u'usec_d'] else 1
CLOSE[u'twoms_is_2'] = 0 if NUM[u'twoms_a'] == 2 else 1
F['msl_minutes'] = [NUM[u'minutes_a'], None, None, NUM[u'minutes_d']]
F['wrap_hours_n'] = NUM[u'hours_a']
F['usec'] = [NUM[u'usec_a'], None, None, NUM[u'usec_d']]
F['nul_faces'] = [1 if F['msl_minutes'][i] is None else 0 for i in range(NSRC)]
F['nul_sh'] = [1 if F['usec'][i] is None else 0 for i in range(NSRC)]

# ---------- 池/集合代数(与采集侧的 dict-of-set 换 itertools.combinations) ----------
MINLEN = 24
GN, GR = [], []
for i in range(NSRC):
    GN.append(set(pnorm(l) for l in L[i] if len(l.strip()) >= MINLEN and len(pnorm(l)) >= MINLEN))
    GR.append(set(l for l in L[i] if len(l.strip()) >= MINLEN))
PAIR = list(itertools.combinations(range(NSRC), 2))
F['set_sizes'] = [len(s) for s in GN]
F['pair_share'] = [len(GN[a] & GN[b]) for a, b in PAIR]
F['pair_byte'] = [len(GR[a] & GR[b]) for a, b in PAIR]
F['pair_norm_only'] = [F['pair_share'][k] - F['pair_byte'][k] for k in range(len(PAIR))]
F['pair_close'] = sum(F['pair_share']) - sum(F['pair_byte']) - sum(F['pair_norm_only'])
F['pair_nonzero'] = len([1 for x in F['pair_share'] if x])
F['tri_share'] = [len(GN[a] & GN[b] & GN[c]) for a, b, c in itertools.combinations(range(NSRC), 3)]
F['union_all'] = len(set().union(*GN))
F['only_each'] = [len([x for x in GN[i] if not any(x in GN[j] for j in range(NSRC) if j != i)])
                  for i in range(NSRC)]
CNT = defaultdict(set)
for i in range(NSRC):
    for l in L[i]:
        if len(l.strip()) >= MINLEN:
            n = pnorm(l)
            if len(n) >= MINLEN:
                CNT[n].add(i)
F['pool_n'] = len(CNT)
F['pool_tier'] = [len([1 for n in CNT if len(CNT[n]) == k]) for k in range(1, NSRC + 1)]
F['pool_tier_close'] = sum(F['pool_tier']) - F['pool_n']
for a in range(NSRC):
    F['pool_share1_' + LBL[a]] = len([n for n in CNT if CNT[n] == {a}])
F['pool_4'] = F['pool_tier'][NSRC - 1]
F['pool_3'] = F['pool_tier'][NSRC - 2]
F['union_close'] = (sum(F['set_sizes']) - sum(F['pair_share']) + sum(F['tri_share'])
                    - F['pool_4'] - F['union_all'])
S4 = [n for n in CNT if len(CNT[n]) == NSRC]
S3 = [n for n in CNT if len(CNT[n]) == 3]
F['s3_examples'] = sorted(S3)[:3]
F['s4_examples'] = sorted(S4)[:3]
AB = [n for n in CNT if CNT[n] == {0, 3}]
AB3 = [n for n in CNT if {0, 3} <= CNT[n] and len(CNT[n]) > 2]
F['pair_ad_share'] = len(AB) + len(AB3)
F['pair_ad_excl'] = len(AB)
F['pair_ad_in3'] = len(AB3)
F['pair_ad_byte'] = len(GR[0] & GR[3])
F['pair_ad_norm_only'] = F['pair_ad_share'] - F['pair_ad_byte']
F['pair_ad_close'] = F['pair_ad_share'] - F['pair_byte'][2] - F['pair_ad_norm_only']
F['pair_ad_split'] = F['pair_ad_share'] - F['pair_ad_excl'] - F['pair_ad_in3']
F['pair_ad_pair_close'] = F['pair_ad_share'] - F['pair_share'][2]


def raw_rows(i, norm):
    return [l for l in L[i] if pnorm(l) == norm]


def axes(rows):
    forms = []
    for r in rows:
        for l in r:
            if l not in forms:
                forms.append(l)
    if len(forms) < 2:
        return []
    if len(set(f.lower() for f in forms)) == 1:
        return [u'case']
    if len(set(f.lower().replace(u'-', u'') for f in forms)) == 1:
        return [u'hyph']
    if len(set(u''.join(f.lower().split()) for f in forms)) == 1:
        return [u'space']
    return [u'multi']


SHARED = [(n, [raw_rows(i, n) for i in range(NSRC)]) for n in S4 + S3]
F['shared_any_byte'] = len([1 for n, rows in SHARED if set.intersection(*[set(r) for r in rows if r])])
F['shared_norm_only'] = len(SHARED) - F['shared_any_byte']
F['axis_counts'] = {a: len([1 for n, rows in SHARED if axes(rows) == [a]])
                    for a in (u'case', u'hyph', u'space', u'multi')}
F['axis_close'] = sum(F['axis_counts'].values()) - F['shared_norm_only']
F['shared_total'] = len(SHARED)

# ---------- 候选锚池与归属 ----------
SPECIAL = (u'2MSL', u'2xMSL', u'2*MSL', u'MSL', u'TIME-WAIT', u'quiet', u'4.55', u'2 minutes',
           u'MUST', u'SHOULD', u'MAY', u'Obsoletes', u'Updates', u'STD', u'ISSN', u'keep-alive',
           u'ISS', u'ISN', u'Timestamp', u'reboot', u'last seen')
POOL = []
seenp = set()
for i in range(NSRC):
    for l in L[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if not pnorm(l):
            continue
        if (i, l) in seenp:
            continue
        seenp.add((i, l))
        POOL.append((LBL[i], l))
CROSS = {}
for tag, l in POOL:
    n = pnorm(l)
    CROSS[(tag, l)] = len([1 for i in range(NSRC) if n in FO[i]])
POOLC = [(t, CROSS[(t, l)], l) for t, l in POOL]
F['apool_n'] = len(POOLC)
F['apool_tag_n'] = [len([p for p in POOLC if p[0] == LBL[i]]) for i in range(NSRC)]
for n in range(1, NSRC + 1):
    F['apool_%d' % n] = len([p for p in POOLC if p[1] == n])
F['apool_tier_close'] = sum(F['apool_%d' % k] for k in range(1, NSRC + 1)) - F['apool_n']
F['apool_tag_close'] = sum(F['apool_tag_n']) - F['apool_n']

ATOMFAIL = []


def AT(i, needles, fold=False):
    """锚由位置导出: 取本标签面上第一枚同时含全部 needles 的原文件行"""
    for l in L[i]:
        if all(x in l for x in needles):
            return u'⟦%s⟧⟨%s⟩' % (LBL[i], l)
    if fold:
        nd = u' '.join(needles)
        if nd in FO[i]:
            ATOMFAIL.append((LBL[i], needles, u'fold'))
            return u'⟦%s⟧⟨%s⟩' % (LBL[i], nd)
    ATOMFAIL.append((LBL[i], needles, u'miss'))
    return u'⟦%s⟧⟨MISSING⟩' % LBL[i]


ANCH = []


def A_(i, *nd):
    x = AT(i, list(nd), fold=(len(nd) == 1 and len(nd[0]) > 70))
    ANCH.append(x)
    return x


# ---------- 恒等式(必须能失败) ----------
ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"F['pair_close']", u'两两“归一同形”减“逐字节同形”再减“只归一同形”应回到零(池代数闭合)')
Z(u"F['union_close']", u'容斥: 单份集之和−两两交之和+三三交之和−四交=并集')
Z(u"F['pool_tier_close']", u'分档各枚数之和=池条数')
Z(u"F['axis_close']", u'共用长行的写法轴分档之和=“归一同形而逐字节不同”的条数')
Z(u"F['shared_any_byte'] + F['shared_norm_only'] - F['shared_total']", u'共用长行=逐字节同形+仅归一同形')
Z(u"F['apool_tier_close']", u'锚候选池按“几份面上出现”分档之和=池条数')
Z(u"F['apool_tag_close']", u'锚候选池按标签分布之和=池条数')
Z(u"CLOSE['minutes_agree']", u'793 ⇎ 9293 句内游标读出的 MSL 分钟数相等')
Z(u"CLOSE['arb_eq_spec']", u'793 术语表“Arbitrarily defined”的分钟数=正文那句的分钟数')
Z(u"CLOSE['usec_agree']", u'两份读出的时钟步长微秒数相等')
Z(u"CLOSE['twoms_is_2']", u'793 状态图 Timeout=2MSL 里游标读出的 2 就是 2')
Z(u"max([abs(F['byte_cp_delta'][i] - F['nonascii_extra'][i]) for i in range(NSRC)])",
  u'字节数−码位数 = 每枚非 ASCII 码位的 utf-8 加字节数之和(9293: BOM 加 2, 两枚 u-umlaut 各加 1)')
Z(u"F['byte_cp_delta'][0] + F['byte_cp_delta'][1] + F['byte_cp_delta'][2]", u'三份纯 ASCII 面的字节−码位差全为零')
Z(u"F['bom'][0] + F['bom'][1] + F['bom'][2] + F['bom'][3] - 1", u'四份里恰有一枚 BOM(9293)')
Z(u"F['nonascii'][3] - F['bom'][3] * 3", u'非 ASCII 码点数=BOM 份数×3')
Z(u"len(F['nul_faces'] and [x for x in F['nul_faces'] if x]) - 2", u'MSL 分钟数只有两份面上给得出(缺席两份)')
Z(u"sum(F['form_all']) - (sum(F['f2msl']) + sum(F['f2x']) + sum(F['f2star']) + sum(F['f2xsp']))",
  u'2MSL 四式合计=各式逐份之和(合计口径闭合)')
Z(u"max([0] + [F['form_all'][i] - F['msl'][i] for i in range(NSRC)])",
  u'每份面上的 2MSL 四式枚数之和不超过该面 MSL 枚数(超了即两轨口径破)')
Z(u"max([0] + [-F['up_ledger'][i] for i in range(NSRC)])",
  u'大写义务词账: 每面 MUST 总数 = 裸 MUST + MUST NOT(正则轨与子串轨对齐)')
Z(u"len([1 for i in range(NSRC) if F['tw'][i]]) - NSRC", u'四份都写到 TIME-WAIT 连字式')
Z(u"len([1 for i in range(NSRC) if F['twospace'][i]]) - NSRC", u'四份都写到 “TIME-WAIT state” 整语')
Z(u"F['ff'][3]", u'9293 是 RFC Editor 的新排版面, 换页符枚数为零(与前三份的页式外壳断裂)')
Z(u"len([1 for i in range(NSRC) if F['ff'][i]]) - 3", u'带换页符的恰是前三份')
Z(u"len([i for i in range(NSRC) if F['std'][i] and not F['cat_std'][i]])",
  u'有 STD: 头的份必然也标 Category: Standards Track(反之不成立: 老排版面只标类别不标 STD)')
Z(u"F['fold_line_zero']", u'三枚折行针按逐行口径必须全为零(它们只在折平面存在)')
Z(u"1 - F['quiet_rewritten']", u'793 的 keep-quiet 整句在 9293 面上按原句读不到(主语被改写; 读到原句即为失败)')
Z(u"1 - F['msl2_same_bytes']", u'两份面上的“MSL=2 分钟”那句逐字同形(1=同形)——不同形即为失败态')
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

print(u'第二遍量测完成: 扁平键 %d ｜ 恒等式 %d ｜ 失败 %d ｜ 针 %d ｜ 池 %d ｜ 锚池 %d ｜ 读数 %s'
      % (len(F), len(ZID), len(ZF), len(SN), F['pool_n'], F['apool_n'], NUM))

# ---------- 附加口径: 游标邻接数／时长档／答题节窗 ----------
def dur_pairs(t):
    out = []
    for m in re.finditer(u'(\\d+(?:\\.\\d+)?)\\s*(seconds|minutes|hours|microseconds)', t):
        out.append((float(m.group(1)), m.group(2)))
    return out


F[u'dur_pairs'] = [sorted(set(dur_pairs(t))) for t in T]
F[u'dur_distinct'] = [len(s) for s in F[u'dur_pairs']]
F[u'dur_hit_total'] = [len(dur_pairs(t)) for t in T]
F[u'dur_docs'] = [len([1 for i in range(NSRC) if F[u'dur_pairs'][i]])] * 0 + [
    len([1 for i in range(NSRC) if any(x == p for x in F[u'dur_pairs'][i])])
    for p in sorted(set().union(*[set(x) for x in F[u'dur_pairs']]))]
F[u'dur_union'] = len(set().union(*[set(x) for x in F[u'dur_pairs']]))
F[u'msl_digit'] = [sorted(set(int(m.group(1)) for m in re.finditer(u'(\\d+)\\s*[x*]?\\s*MSL', t))) for t in T]
F[u'msl_digit_n'] = [len(x) for x in F[u'msl_digit']]
F[u'msl_taken'] = [1 if u'MSL is taken to be' in t else 0 for t in T]
F[u'minutes_word'] = [cnt_cur(t, u'minute') for t in T]


BAND = 40
HDO = re.compile(r'^\s*(\d+(?:\.\d+)*\.?)\s+([A-Z].*)$')


def head_above(ls, ln):
    """答句所属的编号节标题(拒绝目录页的引导点), 取最近的一枚"""
    for st in range(ln, -1, -1):
        m = HDO.match(ls[st])
        if m and u'....' not in ls[st]:
            return m.group(1).rstrip(u'.'), m.group(2).strip(), st + 1
    return u'', u'', 0


def sec_window(i, nd):
    """答句邻域带: 以答句行为心, 两侧各取 BAND 行——不依赖节标题解析, 带内外分账仍可闭合"""
    t = T[i]
    ls = L[i]
    p = t.find(nd)
    if p < 0:
        return None
    ln = t.count(u'\n', 0, p)
    sec, title, hln = head_above(ls, ln)
    a = max(0, ln - BAND)
    b = min(len(ls) - 1, ln + BAND)
    win = u'\n'.join(ls[a:b + 1])
    return {u'head': title, u'sec': sec, u'center': ln + 1, u'head_ln': hln,
            u'start': a + 1, u'end': b + 1, u'chars': len(win), u'rows': b - a + 1,
            u'msl_in': cnt_cur(win, u'MSL'), u'msl_out': cnt_cur(t, u'MSL') - cnt_cur(win, u'MSL'),
            u'tw_in': cnt_cur(win, u'TIME-WAIT'), u'tw_out': cnt_cur(t, u'TIME-WAIT') - cnt_cur(win, u'TIME-WAIT'),
            u'dig_in': len([1 for c in win if c.isdigit()]),
            u'dig_out': len([1 for c in t if c.isdigit()]) - len([1 for c in win if c.isdigit()])}


HEADND = {0: u'For this specification the MSL is taken to be 2 minutes.',
          1: u'TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime).',
          2: u'corresponding to the old incarnation was last seen',
          3: u'For this specification the MSL is taken to be 2 minutes.'}
WIN = [sec_window(i, HEADND[i]) for i in range(NSRC)]
for k in (u'head', u'sec', u'center', u'head_ln', u'start', u'end', u'chars', u'rows',
          u'msl_in', u'msl_out', u'tw_in', u'tw_out', u'dig_in', u'dig_out'):
    F[u'win_' + k] = [w[k] for w in WIN]
F[u'win_band'] = BAND
F[u'win_named'] = len([w for w in WIN if w[u'sec']])
F[u'win_close_msl'] = [w[u'msl_in'] + w[u'msl_out'] - F[u'msl'][i] for i, w in enumerate(WIN)]
F[u'win_close_tw'] = [w[u'tw_in'] + w[u'tw_out'] - F[u'tw'][i] for i, w in enumerate(WIN)]
F[u'win_close_dig'] = [w[u'dig_in'] + w[u'dig_out'] - len([1 for c in T[i] if c.isdigit()])
                       for i, w in enumerate(WIN)]
F[u'win_close_sum'] = sum(F[u'win_close_msl']) + sum(F[u'win_close_tw']) + sum(F[u'win_close_dig'])
F[u'win_share'] = len([w for w in WIN if u'CONNECTION' in w[u'head'].upper()])
for k in CLOSE:
    F[k] = CLOSE[k]
# --- SCAN END ---
# ---------- ZID 的 B69V 形(与 python 形逐条对拍后送 DERIV) ----------
BB69 = lambda name, i=None: (F[name] if i is None else F[name][i])
FN = u'B69V'
_to_v = re.compile(r"(?:F|CLOSE)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B69V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(4)').replace(u'NSRC', u'4')


for k in CLOSE:
    F[k] = CLOSE[k]
ZV = []
for e, w in ZID:
    v = to_v(e.replace(u'\n', u''))
    if eval(v, {FN: BB69}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))

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
        nums = [eval(e, {FN: BB69}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([tuple(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out

exec(io.open(u'corpus/_mk69emit.py', encoding='utf-8').read())
