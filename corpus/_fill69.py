# -*- coding: utf-8 -*-
"""B69 的第四遍复测: 与采集侧 _pick69 ⇎ 建条目侧 _mkB69/_mk69emit ⇎ 门槛侧 audit.py::_b69_scan
换算法不换定义, 现算后把 ⛓解读注 写进条目。本遍的独立处:
①读面走 bytes 再 decode, 行数用 count('\\n')+1, 另立 splitlines() 一档把换页符吃进换行的坑量出来;
②针计数一律 len(re.findall(re.escape(针), 面)) (第二遍是游标 find 循环, 第一遍是 str.count);
③归一走“空白类整体替换+lower+split”, 三面(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平)各用自己的筛行式;
④五枚读数(MSL 分钟数 ⇎ 术语表任意值 ⇎ Timeout 后的 2 ⇎ 绕回小时整数部分 ⇎ 时钟步长微秒)
  由带捕获组的正则一次到位, 与第二遍的正向/逆向游标不同路;
⑤带的定位先按 needle 在原文件行里定位答句行, 再取 ±40 行切片, 标题按归属口径自答句行向上取最近一枚, 另存一档自带首行向下扫(两式在 793 上改口);
⑥搬运算账走 set 代数 ⇎ dict-of-set ⇎ itertools.combinations 三式互检;
⑦义务语气走正则词界 \\bMUST(?! NOT)\\b, 与第二遍的子串档对账;
⑧锚归属走双轨: 原子串对原文件逐行 membership ⇎ 对折平面 membership, 两式同判才计数;
⑨恒等式与 DERIV 复算点从 _b69checks.json ⇎ _deriv69.json 回读后 eval, 不重打一遍算式。
每个键与 corpus/_b69flat.json 对拍, 值不符或键缺失一律先收集后汇总, 全零才落盘。"""
import io, os, re, sys, json, itertools
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
ENTRY = u'%s/babeltele/B69_tcp_timewait_linger_four_answers.md' % C
PATH = [u'%s/raw/tcpTW/rfc793.txt' % C, u'%s/raw/tcpRTO/rfc1122.txt' % C,
        u'%s/raw/tcpTW/rfc6528.txt' % C, u'%s/raw/tcpTW/rfc9293.txt' % C]
LBL = [u'793', u'1122', u'6528', u'9293']
NSRC = 4
MINLEN = 24
BAND = 40
NL = u'\n'
EXTRA = {u'splitlines_extra', u'track_agree', u'track_split', u'rfc_ref_pref_1122',
         u'rfc_ref_pref_6528', u'rfc_ref_pref_9293', u'isn_bits_loose',
         u'win_head_ln_fwd', u'win_head_fwd', u'win_track_differ'}
J = lambda xs: u' ⇎ '.join(u'%s' % x for x in xs)
D = {}
FLAT = json.load(io.open(u'%s/_b69flat.json' % C, encoding='utf-8'))
CH = json.load(io.open(u'%s/_b69checks.json' % C, encoding='utf-8'))
JJ = json.load(io.open(u'%s/_deriv69.json' % C, encoding='utf-8'))
MS = u'\n'.join(io.open(p, encoding='utf-8', errors='replace').read() for p in [u'%s/_mkB69.py' % C])
import ast
TAB = {}
for st in ast.parse(MS).body:
    if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
        nm = st.targets[0].id
        if nm in (u'NEEDLE', u'FOLD', u'HEADND', u'PATH', u'MINLEN', u'BAND'):
            TAB[nm] = ast.literal_eval(st.value)
NEEDLE, FOLD, HEADND = TAB[u'NEEDLE'], TAB[u'FOLD'], TAB[u'HEADND']

BYT = [io.open(p, 'rb').read() for p in PATH]
T = [b.decode('utf-8', 'replace') for b in BYT]
L = [t.split(u'\n') for t in T]


def pn(s):
    return u' '.join(re.sub(u'[\\s\\u00a0\\u2007\\u202f]+', u' ', s).strip().lower().split())


def cf(s):
    """只折空白不降大小写: 读数轨要在原大小写面上抓 MSL/TIME-WAIT 前的数字"""
    return u' '.join(re.sub(u'[\\s\\u00a0\\u2007\\u202f]+', u' ', s).split())


FO = [pn(t) for t in T]
SHRE = [re.compile(u'^\\s*\\x0c*\\s*$'), re.compile(u'\\[Page'), re.compile(u'^RFC \\d+\\s'),
        re.compile(u'^\\s*\\d+\\s+\\S.*20\\d\\d\\s*$'), re.compile(u'^\\s*(RFC|INTERNET-DRAFT|Network Working Group)')]


def shface(t):
    keep = []
    for l in t.split(u'\n'):
        if any(r.search(l) for r in SHRE):
            continue
        keep.append(l)
    return pn(u'\n'.join(keep))


SH = [shface(t) for t in T]


def sub4(name, f):
    D[name] = [f(i) for i in range(NSRC)]


def cnt(t, nd):
    return len(re.findall(re.escape(nd), t))


# ---------- 面与版式 ----------
sub4(u'bytes', lambda i: len(BYT[i]))
sub4(u'chars', lambda i: len(T[i]))
sub4(u'lines', lambda i: T[i].count(u'\n') + 1)
sub4(u'nonblank', lambda i: len([l for l in L[i] if l.strip()]))
sub4(u'maxlen', lambda i: max(len(x) for x in L[i]))
sub4(u'cr', lambda i: T[i].count(u'\r'))
sub4(u'ff', lambda i: T[i].count(u'\x0c'))
sub4(u'ff_only', lambda i: len([l for l in L[i] if l == u'\x0c']))
sub4(u'bom', lambda i: 1 if BYT[i][:3] == b'\xef\xbb\xbf' else 0)
sub4(u'nonascii', lambda i: len([c for c in T[i] if ord(c) > 127]))
sub4(u'nonascii_extra', lambda i: sum(len(c.encode('utf-8')) - 1 for c in T[i] if ord(c) > 127))
sub4(u'byte_cp_delta', lambda i: len(BYT[i]) - len(T[i]))
D[u'splitlines_extra'] = [len(T[i].splitlines()) - (T[i].count(u'\n') + 1) for i in range(NSRC)]
D[u'nonascii_set'] = sorted(set(hex(ord(c)) for c in T[3] if ord(c) > 127))

# ---------- 词轨 ----------
for nm, nd in ((u'msl', u'MSL'), (u'tw', u'TIME-WAIT'), (u'twospace', u'TIME-WAIT state'),
               (u'quiet', u'quiet'), (u'linger', u'linger'), (u'minutes_word', u'minute'),
               (u'tw_plain', u'TIME WAIT'), (u'quiet_time_word', u'quiet time'),
               (u'isn', u'ISN'), (u'iss', u'ISS'), (u'ka', u'keep-alive'), (u'timestamp', u'Timestamp'), (u'kabare', u'keepalive'),
               (u'reboot', u'reboot'), (u'time_wait_domin', u'TIME-WAIT'),
               (u'rfc_ref_1122', u'1122'), (u'rfc_ref_6528', u'6528'),
               (u'rfc_ref_9293', u'9293')):
    if nm == u'time_wait_domin':
        sub4(nm, lambda i, nd=nd: cnt(T[i], nd) - len(re.findall(
            re.escape(u'TIME-WAIT state'), T[i])))
        D[nm] = [cnt(T[i], nd) - len(re.findall(re.escape(u'TIME-WAIT state'), T[i]))
                 for i in range(NSRC)]
        continue
    sub4(nm, lambda i, nd=nd: cnt(T[i], nd))
D[u'msl_minute_word'] = D[u'minutes_word']
D[u'twospace'] = [cnt(T[i], u'TIME-WAIT state') for i in range(NSRC)]

# ---------- 2MSL 四式 ⇎ 同面并存 ----------
FORMS = {u'f2msl': u'2MSL', u'f2x': u'2xMSL', u'f2star': u'2*MSL', u'f2xsp': u'2 x MSL'}
for nm, nd in FORMS.items():
    D[nm] = [cnt(T[i], nd) for i in range(NSRC)]
D[u'form_all'] = [sum(D[nm][i] for nm in FORMS) for i in range(NSRC)]
D[u'form_distinct'] = [len([nm for nm in FORMS if D[nm][i]]) for i in range(NSRC)]
D[u'form_docs'] = [len([1 for i in range(NSRC) if D[nm][i]]) for nm in
                       (u'f2msl', u'f2x', u'f2star', u'f2xsp')]

# ---------- 引用写法两族 ----------
D[u'r793d'] = [cnt(T[i], u'RFC-793') for i in range(NSRC)]
D[u'r793s'] = [cnt(T[i], u'RFC 793') for i in range(NSRC)]
D[u'r1122d'] = [cnt(T[i], u'RFC-1122') for i in range(NSRC)]
D[u'r1122s'] = [cnt(T[i], u'RFC 1122') for i in range(NSRC)]

# ---------- 义务语气: 正则词界档 ----------
D[u'up_must_all'] = [len(re.findall(u'\\bMUST\\b', T[i])) for i in range(NSRC)]
D[u'must_not'] = [len(re.findall(u'\\bMUST NOT\\b', T[i])) for i in range(NSRC)]
D[u'must_bare'] = [D[u'up_must_all'][i] - D[u'must_not'][i] for i in range(NSRC)]
D[u'up_must'] = D[u'must_bare']
D[u'up_should'] = [len(re.findall(u'\\bSHOULD\\b', T[i])) for i in range(NSRC)]
D[u'up_may'] = [len(re.findall(u'\\bMAY\\b', T[i])) for i in range(NSRC)]
D[u'up_ledger'] = [D[u'up_must_all'][i] - D[u'must_bare'][i] - D[u'must_not'][i] for i in range(NSRC)]
D[u'sec_must_not'] = D[u'must_not']
D[u'quiet_rewritten'] = 0 if pn(u'keep quiet for a maximum segment lifetime') in FO[3] else 1
D[u'msl2_same_bytes'] = 1 if (u'For this specification the MSL is taken to be 2 minutes.' in T[0]
                              and u'For this specification the MSL is taken to be 2 minutes.' in T[3]) else 0
D[u'msl_taken'] = [cnt(T[i], u'MSL is taken to be') for i in range(NSRC)]
D[u'c2m'] = [cnt(T[i], u'2 minutes') for i in range(NSRC)]
D[u'msl_undefined_c'] = 1 if cnt(T[2], u'2 minutes') == 0 else 0
D[u'h455'] = [cnt(T[i], u'4.55 hours') for i in range(NSRC)]
D[u'wrap_hours'] = D[u'h455']
D[u'four_us'] = [cnt(T[i], u'4 microseconds') for i in range(NSRC)]
D[u'obsoletes'] = [len(re.findall(u'^Obsoletes:', T[i], re.M)) for i in range(NSRC)]
D[u'updates'] = [len(re.findall(u'^Updates:', T[i], re.M)) for i in range(NSRC)]
D[u'std'] = [len(re.findall(u'^STD:', T[i], re.M)) for i in range(NSRC)]
D[u'issn'] = [len(re.findall(u'^ISSN:', T[i], re.M)) for i in range(NSRC)]
D[u'cat_std'] = [1 if u'Category: Standards Track' in T[i] else 0 for i in range(NSRC)]
D[u'cat_info'] = [1 if u'Category: Informational' in T[i] else 0 for i in range(NSRC)]

# ---------- 句内读数: 捕获组一次到位 ----------
RX = {u'minutes_a': (0, u'MSL is taken to be (\\d+) minutes'),
      u'minutes_d': (3, u'MSL is taken to be (\\d+) minutes'),
      u'minutes_arb': (0, u'Arbitrarily defined to be (\\d+) minutes'),
      u'twoms_a': (0, u'Timeout=(\\d+)MSL'),
      u'usec_a': (0, u'incremented roughly every (\\d+) microsecond'),
      u'usec_d': (3, u'once every roughly (\\d+) microsecond')}
for nm, (i, pat) in RX.items():
    m = re.search(pat, cf(T[i]))
    D[u'num_' + nm] = int(m.group(1)) if m else None
mh = re.search(u'approximately every (\\d+)\\.(\\d+) hours', cf(T[0]))
D[u'num_hours_a'] = int(mh.group(1)) if mh else None
mh2 = re.search(u'approximately every (\\d+)\\.(\\d+) hours', cf(T[3]))
D[u'cycle_h'] = [None] * NSRC
for i in range(NSRC):
    m = re.search(u'every (\\d+\\.\\d+) hours', cf(T[i]))
    D[u'cycle_h'][i] = float(m.group(1)) if m else None
D[u'cycle_docs'] = len([x for x in D[u'cycle_h'] if x])
D[u'usec'] = [D[u'num_usec_a'], None, None, D[u'num_usec_d']]
D[u'msl_minutes'] = [D[u'num_minutes_a'], None, None, D[u'num_minutes_d']]
D[u'nul_faces'] = [1 if x is None else 0 for x in D[u'msl_minutes']]
D[u'nul_sh'] = [1 if x is None else 0 for x in D[u'usec']]
D[u'msl_digit'] = [sorted(set(int(x) for x in re.findall(u'(\\d+)[ x*]*MSL', cf(T[i]))))
                   for i in range(NSRC)]
D[u'msl_digit_n'] = [len(set(x)) for x in D[u'msl_digit']]
def isn_bits(t):
    """按建条目侧的有序三选一口径逐枚游标扫描: 命中即跳过整枚针, 未命中只跨过 '32'"""
    n = 0
    k = 0
    while True:
        p = t.find(u'32', k)
        if p < 0:
            return n
        for nd in (u'32 bit ISN', u'32-bit counter', u'32 bit'):
            if t.startswith(nd, p):
                n += 1
                k = p + len(nd)
                break
        else:
            k = p + 2


D[u'isn_bits'] = [isn_bits(t) for t in T]
D[u'isn_bits_loose'] = [len(re.findall(u'32[ -]bit', T[i])) for i in range(NSRC)]
for _n in (u'1122', u'6528', u'9293'):
    D[u'rfc_ref_pref_' + _n] = [len(re.findall(u'RFC\\s*' + _n, T[i])) for i in range(NSRC)]
D[u'minutes_agree'] = 0 if D[u'num_minutes_a'] == D[u'num_minutes_d'] else 1
D[u'arb_eq_spec'] = 0 if D[u'num_minutes_arb'] == D[u'num_minutes_a'] else 1
D[u'usec_agree'] = 0 if D[u'num_usec_a'] == D[u'num_usec_d'] else 1
D[u'twoms_is_2'] = 0 if D[u'num_twoms_a'] == 2 else 1
D[u'wrap_hours_n'] = D[u'num_hours_a']
D[u'dur_hit_total'] = [len(re.findall(u'(\\d+(?:\\.\\d+)?)[ ]*(seconds|minutes|hours|microseconds)', FO[i]))
                       for i in range(NSRC)]
D[u'dur_distinct'] = [len(set((float(a), b) for a, b in
                         re.findall(u'(\\d+(?:\\.\\d+)?)[ ]*(seconds|minutes|hours|microseconds)', FO[i])))
                      for i in range(NSRC)]

# ---------- 三面阶梯(在册 28 枚针) ----------
ALLN = [(i, k, nd, u'line') for i, k, nd in NEEDLE] + [(i, k, nd, u'fold') for i, k, nd in FOLD]
OWNER, LITK4, SNL, SNF, SNS = {}, {}, {}, {}, {}
for i, k, nd, kind in ALLN:
    OWNER[k] = i
    LITK4[k] = nd
    SNL[k] = [len([l for l in L[x] if nd in l]) for x in range(NSRC)]
    n4 = pn(nd)
    SNF[k] = [1 if n4 in FO[x] else 0 for x in range(NSRC)]
    SNS[k] = [1 if n4 in SH[x] else 0 for x in range(NSRC)]
KEYS = [k for _, k, _, _ in ALLN]
D[u'needle_n'] = len(KEYS)
D[u'sn_strict_docs'] = [len([k for k in KEYS if OWNER[k] == i and SNL[k][i] > 0]) for i in range(NSRC)]
D[u'sn_fold_docs'] = [len([k for k in KEYS if OWNER[k] == i and SNF[k][i] > 0]) for i in range(NSRC)]
D[u'sn_sh_docs'] = [len([k for k in KEYS if OWNER[k] == i and SNS[k][i] > 0]) for i in range(NSRC)]
D[u'fold_only_keys'] = [k for k in KEYS if sum(SNL[k]) == 0 and sum(SNF[k]) > 0]
D[u'fold_only_n'] = len(D[u'fold_only_keys'])
D[u'fold_only_own'] = [len([k for k in D[u'fold_only_keys'] if OWNER[k] == i]) for i in range(NSRC)]
D[u'ladder_monotone'] = 1 if all(D[u'sn_strict_docs'][i] + D[u'fold_only_own'][i]
                                 == D[u'sn_fold_docs'][i] for i in range(NSRC)) else 0
D[u'fold_line_zero'] = sum(SNL[k][i] for _, k, _, kind in ALLN if kind == u'fold'
                           for i in range(NSRC) if i != OWNER[k])
D[u'sh_minus_fold'] = [D[u'sn_sh_docs'][i] - D[u'sn_fold_docs'][i] for i in range(NSRC)]
D[u'sh_lost_keys'] = [k for k in KEYS if SNF[k][OWNER[k]] and not SNS[k][OWNER[k]]]
D[u'sh_lost_n'] = len(D[u'sh_lost_keys'])
D[u'sh_only_keys'] = [k for k in KEYS if SNS[k][OWNER[k]] and not SNF[k][OWNER[k]]]
D[u'msl2_two_docs'] = [SNL[u'a_msl2'][0], SNL[u'd_msl2'][3]]

# ---------- 答句邻域带 ----------
HDO = re.compile(u'^\\s*(\\d+(?:\\.\\d+)*\\.?)\\s+([A-Z].*)$')


def head_from(ls, st):
    for x in range(st, -1, -1):
        m = HDO.match(ls[x])
        if m and u'....' not in ls[x]:
            return m.group(1).rstrip(u'.'), m.group(2).strip(), x + 1
    return u'', u'', 0


W = {}
for i in range(NSRC):
    ln = T[i].count(u'\n', 0, T[i].find(HEADND[i]))
    a = max(0, ln - BAND)
    b = min(len(L[i]) - 1, ln + BAND)
    sec, title, hl = head_from(L[i], ln)
    win = u'\n'.join(L[i][a:b + 1])
    W[i] = {u'start': a + 1, u'end': b + 1, u'center': ln + 1, u'rows': b - a + 1,
            u'chars': len(win), u'sec': sec, u'head': title, u'hl': hl,
            u'msl_in': cnt(win, u'MSL'), u'tw_in': cnt(win, u'TIME-WAIT'),
            u'dig_in': len([1 for c in win if c.isdigit()])}
for nm, key in ((u'win_start', u'start'), (u'win_end', u'end'), (u'win_center', u'center'),
                (u'win_rows', u'rows'), (u'win_chars', u'chars'), (u'win_sec', u'sec'),
                (u'win_head', u'head'), (u'win_head_ln', u'hl'), (u'win_msl_in', u'msl_in'),
                (u'win_tw_in', u'tw_in'), (u'win_dig_in', u'dig_in')):
    D[nm] = [W[i][key] for i in range(NSRC)]
D[u'win_band'] = BAND
D[u'win_title'] = D[u'win_head']
D[u'win_named'] = len([1 for i in range(NSRC) if W[i][u'sec']])
D[u'win_share'] = len([1 for i in range(NSRC) if u'CONNECTION' in W[i][u'head'].upper()])
D[u'win_msl_out'] = [D[u'msl'][i] - D[u'win_msl_in'][i] for i in range(NSRC)]
D[u'win_tw_out'] = [D[u'tw'][i] - D[u'win_tw_in'][i] for i in range(NSRC)]
D[u'win_dig_out'] = [len([1 for c in T[i] if c.isdigit()]) - D[u'win_dig_in'][i] for i in range(NSRC)]
D[u'win_close_msl'] = [D[u'win_msl_in'][i] + D[u'win_msl_out'][i] - D[u'msl'][i] for i in range(NSRC)]
D[u'win_close_tw'] = [D[u'win_tw_in'][i] + D[u'win_tw_out'][i] - D[u'tw'][i] for i in range(NSRC)]
D[u'win_close_dig'] = [D[u'win_dig_in'][i] + D[u'win_dig_out'][i]
                       - len([1 for c in T[i] if c.isdigit()]) for i in range(NSRC)]
D[u'win_close_sum'] = sum(D[u'win_close_msl']) + sum(D[u'win_close_tw']) + sum(D[u'win_close_dig'])
D[u'win_level'] = [W[i][u'head'].split()[0].count(u'.') for i in range(NSRC)]


def head_fwd(ls, st):
    for x in range(st, len(ls)):
        m = HDO.match(ls[x])
        if m and u'....' not in ls[x]:
            return m.group(1).rstrip(u'.'), m.group(2).strip(), x + 1
    return u'', u'', 0


FWD = [head_fwd(L[i], max(0, W[i][u'center'] - 1 - BAND)) for i in range(NSRC)]
D[u'win_head_ln_fwd'] = [f[2] for f in FWD]
D[u'win_head_fwd'] = [f[1] for f in FWD]
D[u'win_track_differ'] = len([i for i in range(NSRC) if FWD[i][2] != W[i][u'hl']])

# ---------- 池与集合代数 ----------
GN, GR = [], []
for i in range(NSRC):
    GN.append(set(pn(l) for l in L[i] if len(l.strip()) >= MINLEN and len(pn(l)) >= MINLEN))
    GR.append(set(l for l in L[i] if len(l.strip()) >= MINLEN))
PAIR = list(itertools.combinations(range(NSRC), 2))
TRI = list(itertools.combinations(range(NSRC), 3))
D[u'set_sizes'] = [len(s) for s in GN]
D[u'pair_share'] = [len(GN[a] & GN[b]) for a, b in PAIR]
D[u'pair_byte'] = [len(GR[a] & GR[b]) for a, b in PAIR]
D[u'pair_norm_only'] = [D[u'pair_share'][k] - D[u'pair_byte'][k] for k in range(len(PAIR))]
D[u'pair_close'] = sum(D[u'pair_share']) - sum(D[u'pair_byte']) - sum(D[u'pair_norm_only'])
D[u'pair_nonzero'] = len([1 for x in D[u'pair_share'] if x])
D[u'tri_share'] = [len(GN[a] & GN[b] & GN[c]) for a, b, c in TRI]
D[u'union_all'] = len(set().union(*GN))
D[u'only_each'] = [len(GN[i] - set().union(*[GN[j] for j in range(NSRC) if j != i])) for i in range(NSRC)]
D[u'union_close'] = (sum(D[u'set_sizes']) - sum(D[u'pair_share']) + sum(D[u'tri_share'])
                     - D[u'union_all'])
CNT = defaultdict(set)
for i in range(NSRC):
    for l in L[i]:
        n = pn(l)
        if len(l.strip()) >= MINLEN and len(n) >= MINLEN:
            CNT[n].add(i)
D[u'pool_n'] = len(CNT)
D[u'pool_tier'] = [len([1 for n in CNT if len(CNT[n]) == k]) for k in range(1, NSRC + 1)]
D[u'pool_tier_close'] = sum(D[u'pool_tier']) - D[u'pool_n']
for a in range(NSRC):
    D[u'pool_share1_' + LBL[a]] = len([n for n in CNT if CNT[n] == {a}])
D[u'pool_4'] = D[u'pool_tier'][NSRC - 1]
D[u'pool_3'] = D[u'pool_tier'][NSRC - 2]
S3 = [n for n in CNT if len(CNT[n]) == 3]
D[u's3_examples'] = sorted(S3)[:3]
D[u's3_docs'] = len(CNT[S3[0]]) if S3 else 0
AB = [n for n in CNT if CNT[n] == {0, 3}]
AB3 = [n for n in CNT if {0, 3} <= CNT[n] and len(CNT[n]) > 2]
D[u'pair_ad_share'] = len(AB) + len(AB3)
D[u'pair_ad_excl'] = len(AB)
D[u'pair_ad_in3'] = len(AB3)
D[u'pair_ad_byte'] = len(GR[0] & GR[3])
D[u'pair_ad_norm_only'] = D[u'pair_ad_share'] - D[u'pair_ad_byte']
D[u'pair_ad_close'] = D[u'pair_ad_share'] - D[u'pair_ad_byte'] - D[u'pair_ad_norm_only']
D[u'pair_ad_split'] = D[u'pair_ad_share'] - D[u'pair_ad_excl'] - D[u'pair_ad_in3']
D[u'pair_ad_pair_close'] = D[u'pair_ad_share'] - D[u'pair_share'][2]
S4 = [n for n in CNT if len(CNT[n]) == NSRC]
D[u's4_examples'] = sorted(S4)[:3]

# ---------- 锚候选池 ----------
SPEC = (u'2MSL', u'2xMSL', u'2*MSL', u'MSL', u'TIME-WAIT', u'quiet', u'4.55', u'2 minutes',
        u'MUST', u'SHOULD', u'MAY', u'Obsoletes', u'Updates', u'STD', u'ISSN', u'keep-alive',
        u'ISS', u'ISN', u'Timestamp', u'reboot', u'last seen')
POOL = []
for i in range(NSRC):
    for l in set(L[i]):
        if len(l) < 20 and not any(x in l for x in SPEC):
            continue
        if not pn(l):
            continue
        POOL.append((LBL[i], l))
TIERN = Counter()
TAGN = Counter()
for tag, l in POOL:
    n = pn(l)
    k = len([1 for i in range(NSRC) if n in FO[i]])
    TIERN[k] += 1
    TAGN[tag] += 1
D[u'apool_n'] = len(POOL)
D[u'apool_tag_n'] = [TAGN[LBL[i]] for i in range(NSRC)]
for k in range(1, NSRC + 1):
    D[u'apool_%d' % k] = TIERN[k]
D[u'apool_tag_close'] = sum(D[u'apool_tag_n']) - D[u'apool_n']
D[u'apool_tier_close'] = sum(D[u'apool_%d' % k] for k in range(1, NSRC + 1)) - D[u'apool_n']

# ---------- 锚双轨归属 ----------
TT = io.open(ENTRY, encoding='utf-8').read()
ATOMS = [x for x in io.open(u'%s/_atoms69.txt' % C, encoding='utf-8').read().split(u'\n') if x]
enc = re.search(u'\u27eaBabelTele\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
CIT = re.findall(u'\u27e6(' + u'|'.join(LBL) + u')\u27e7\u27e8([^\u27e8\u27e9]+)\u27e9', enc)
LINE_HIT = {}
FOLD_HIT = {}
DIS = []
for _, a in CIT:
    if a not in DIS:
        DIS.append(a)
for a in DIS:
    LINE_HIT[a] = tuple(i for i in range(NSRC) if a in L[i])
    FOLD_HIT[a] = tuple(i for i in range(NSRC) if pn(a) and pn(a) in FO[i])
D[u'anchor_total'] = len(CIT)
D[u'anchor_distinct'] = len(DIS)
D[u'anchor_err'] = len([a for a in DIS if not FOLD_HIT[a]])
D[u'anchor_single'] = len([a for a in DIS if len(FOLD_HIT[a]) == 1])
D[u'anchor_cross'] = len([a for a in DIS if 1 < len(FOLD_HIT[a]) < NSRC])
D[u'anchor_all4'] = len([a for a in DIS if len(FOLD_HIT[a]) == NSRC])
D[u'checks'] = len(DIS) * NSRC
D[u'track_agree'] = len([a for a in DIS if LINE_HIT[a] == FOLD_HIT[a]])
D[u'track_split'] = [a for a in DIS if LINE_HIT[a] != FOLD_HIT[a]]
D[u'enc_chars'] = len(enc.replace(NL, u''))
D[u'nsrc'] = NSRC
for t in LBL:
    D[u'tag_' + t] = len(re.findall(u'\u27e6%s\u27e7' % t, enc))

# ---------- 在册 28 枚针的逐行计数(与第二遍的 FOLDLINE 同义异路) ----------
for k in KEYS:
    D[u'n_' + k] = SNL[k]
D[u'shared_verbatim'] = [k for k in KEYS if sum(SNL[k]) >= 2]

# ---------- 共用长行的写法轴(一遍扫全行建 norm→原行表, 不做逐条 rfind) ----------
ROWMAP = [defaultdict(list) for _ in range(NSRC)]
for i in range(NSRC):
    for l in L[i]:
        if len(l.strip()) >= MINLEN:
            ROWMAP[i][pn(l)].append(l)


def axes(rows):
    forms = []
    for rr in rows:
        for r in rr:
            if r not in forms:
                forms.append(r)
    if len(forms) < 2:
        return []
    if len(set(f.lower() for f in forms)) == 1:
        return [u'case']
    if len(set(f.lower().replace(u'-', u'') for f in forms)) == 1:
        return [u'hyph']
    if len(set(re.sub(u'\\s', u'', f.lower()) for f in forms)) == 1:
        return [u'space']
    return [u'multi']


SHARED = [(n, [ROWMAP[i].get(n, []) for i in range(NSRC)]) for n in S4 + S3]
D[u'shared_any_byte'] = len([1 for n, rows in SHARED
                             if set.intersection(*[set(r) for r in rows if r])])
D[u'shared_norm_only'] = len(SHARED) - D[u'shared_any_byte']
D[u'shared_total'] = len(SHARED)
AXC = dict((a, len([1 for n, rows in SHARED if axes(rows) == [a]]))
           for a in (u'case', u'hyph', u'space', u'multi'))
D[u'axis_counts'] = AXC
D[u'axis_close'] = sum(AXC.values()) - D[u'shared_norm_only']
D[u'axis_str'] = u'⇎'.join(u'%s%d' % (a, AXC[a]) for a in (u'case', u'hyph', u'space', u'multi'))
D[u'axis_str_n'] = len([a for a in AXC if AXC[a]])
S3R = [ROWMAP[i].get(D[u's3_examples'][0], []) for i in range(NSRC)]
D[u's3_raw'] = S3R
D[u's3_raw_first'] = S3R[0][0]
D[u's3_docs'] = len([1 for x in S3R if x])
D[u's3_norm_close'] = len(pn(D[u's3_raw_first'])) - len(D[u's3_examples'][0])

# ---------- 时长档(先建档再派生并集/份数, 与第二遍的逐份 sorted-set 反序) ----------
D[u'dur_pairs'] = [sorted(set((float(a), b) for a, b in
                       re.findall(u'(\\d+(?:\\.\\d+)?)[ ]*(seconds|minutes|hours|microseconds)', FO[i])))
                   for i in range(NSRC)]
D[u'dur_union'] = len(set().union(*[set(x) for x in D[u'dur_pairs']]))
D[u'dur_docs'] = [len([1 for i in range(NSRC) if p in D[u'dur_pairs'][i]])
                  for p in sorted(set().union(*[set(x) for x in D[u'dur_pairs']]))]

# ---------- 对账 ⇎ 恒等式 ⇎ DERIV 复跑 ----------
D[u'zid_n'] = len(CH[u'zid'])
D[u'x_ident_n'] = len(CH[u'zid'])
D[u'scalar_clos_n'] = len(CH[u'zid'])
NS = dict(FLAT)
NS.update(D)
V = lambda k, i=None: (NS[k] if i is None else NS[k][i])
ZRES = [(e, w, eval(e, {u'B69V': V})) for e, w in CH[u'zid']]
ZFAIL = [(w, r) for e, w, r in ZRES if r != 0]
D[u'zid_fail'] = [w for e, w, r in ZRES if r != 0]
D[u'scalar_clos_sum'] = len([1 for e, w, r in ZRES if r == 0])
NS.update(D)
MISS = [k for k in D if k not in FLAT]
_jr = lambda x: json.loads(json.dumps(x))
BAD = [(k, D[k], FLAT[k]) for k in D if k in FLAT and _jr(D[k]) != FLAT[k]]
UNCOVER = [k for k in FLAT if k not in D]
DFAIL = []
for kk, v in JJ.items():
    try:
        g = eval(v, {}, {u'B69V': V})
    except Exception as e:
        DFAIL.append((kk, repr(e)))
        continue
    if str(g) != kk and repr(g) != kk:
        DFAIL.append((kk, v, str(g)))
assert not ZFAIL, ZFAIL[:4]
assert not DFAIL, DFAIL[:4]
assert not BAD, BAD[:6]
assert set(MISS) <= EXTRA, MISS[:6]
assert not D[u'anchor_err'] and D[u'fold_line_zero'] == 0
assert sum(D[u'up_ledger']) == 0 and D[u'win_close_sum'] == 0 and D[u'pair_close'] == 0
assert D[u'union_close'] == 0 and D[u'pool_tier_close'] == 0
assert D[u'apool_tag_close'] == 0 and D[u'apool_tier_close'] == 0
assert D[u'ladder_monotone'] == 1 and D[u'sh_lost_n'] == 0

L2 = []
A = L2.append
A(u"第四遍(`corpus/_fill69.py`)换算法不换定义地重跑一遍: 读面走 bytes 再 decode ⇎ 行数按 `count('\\n')+1`"
  u" ⇎ 针计数按 `len(re.findall(re.escape(针), 面))` ⇎ 归一走空白类整体替换 ⇎ 五枚读数由带捕获组的正则一次到位"
  u" ⇎ 带的定位先找答句行再取 ±%d 行切片 ⇎ 搬运算账走 set 代数 ⇎ 义务语气走词界正则。" % BAND)
A(u"本遍共复算 %d 个键(扁平表 %d 键中覆盖 %d 枚, 缺 %d ⇎ 多 %d ⇎ 不符 %d); 面内恒等式 %d 条按本注读数重跑全部为真; "
  u"DERIV %d 条复算点在本注的读数上重跑全对(引用 %d 处)。" % (
      len(D), len(FLAT), len([k for k in D if k in FLAT]), len(UNCOVER), len(MISS), len(BAD),
      len(CH[u'zid']), len(JJ), sum(len(v.split(u'B69V(')) - 1 for v in JJ.values())))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"行数⇎换行", u"`split('\\n')` 计格 ⇎ `count('\\n')+1` 计枚 ⇎ `splitlines()` 第三式",
     u"%s ⇎ splitlines 多出 %s" % (J(D[u'lines']), J(D[u'splitlines_extra'])),
     u"三式在 LF 面一致 ⇎ 差值恰为换页符 %s 枚——splitlines 认 \\x0c 为换行, 谁用它数行数就会把版式读成内容" % J(D[u'ff'])),
    (u"编码层", u"字节面看 BOM ⇎ 码位面数非 ASCII ⇎ utf-8 逐字符加字节",
     u"BOM %s ⇎ 非 ASCII %s ⇎ 加字节 %s ⇎ 字节−码位 %s" % (
         J(D[u'bom']), J(D[u'nonascii']), J(D[u'nonascii_extra']), J(D[u'byte_cp_delta'])),
     u"只有 9293 不干净: 一枚 BOM(+2) ⇎ 两枚 U+00FC(+1 each) ⇒ 3 枚码位带来 4 枚加字节——"
     u"“非 ASCII 数=字节差”这条默认等式在这里差 1, 所以本条把加字节另立一列"),
    (u"三面阶梯", u"逐行 in ⇎ 全篇折平成员 ⇎ 自己筛掉页壳行再折平",
     u"原面 %s ⇎ 折平 %s ⇎ 摘壳 %s" % (J(D[u'sn_strict_docs']), J(D[u'sn_fold_docs']), J(D[u'sn_sh_docs'])),
     u"只增不减(%d), 新增的三枚是 %s; 摘壳档相对折平 %s——9293 零换页符, 剥壳对它是空操作, "
     u"这恰好是 B68 的反面(那边第三档才是唯一读到关键句的一档)" % (
         D[u'ladder_monotone'], u'、'.join(D[u'fold_only_keys']), J(D[u'sh_minus_fold']))),
    (u"句内读数", u"捕获组正则 `(\\d+) minutes` ⇎ `(\\d+)MSL` ⇎ `(\\d+)\\.(\\d+) hours`",
     u"分钟 %s⇎%s ⇎ 术语表 %s ⇎ Timeout %s ⇎ 微秒 %s⇎%s ⇎ 小时整数部分 %s" % (
         D[u'num_minutes_a'], D[u'num_minutes_d'], D[u'num_minutes_arb'], D[u'num_twoms_a'],
         D[u'num_usec_a'], D[u'num_usec_d'], D[u'num_hours_a']),
     u"四本闭合全归零(分钟 %d ⇎ 术语表 %d ⇎ 微秒 %d ⇎ Timeout %d)。绕回小时本注按 `every (\\d+\\.\\d+) hours` 读到 %s"
     u"——它把 “4.55” 当整枚小数收, 而不是像 793 那句 “less than 4.55” 那样只当字面" % (
         D[u'minutes_agree'], D[u'arb_eq_spec'], D[u'usec_agree'], D[u'twoms_is_2'], J(D[u'cycle_h']))),
    (u"分钟数的缺席档", u"“2 minutes” 字样枚数 ⇎ “taken to be” 句式枚数 两式并计",
     u"2 minutes %s ⇎ taken-to-be %s ⇎ 分钟数缺席面 %s" % (J(D[u'c2m']), J(D[u'msl_taken']), J(D[u'nul_faces'])),
     u"1122 面上有 1 处 “2 minutes”, 但那枚数不是 MSL 的定义值(它给的是 2xMSL 的式); 6528 面上 %d 处分钟字样"
     u"且 taken-to-be 句式 %d 枚 ⇒ 本条的“谁没给时长”不是搜不到字面, 而是搜到了也不构成答案" % (
         D[u'c2m'][1], D[u'msl_taken'][2])),
    (u"2MSL 四式", u"四个独立子串针 + 同面并存计数",
     u"连字 %s ⇎ 乘号 %s ⇎ 星号 %s ⇎ 带空格 %s ⇎ 合计 %s ⇎ 并存 %s" % (
         J(D[u'f2msl']), J(D[u'f2x']), J(D[u'f2star']), J(D[u'f2xsp']), J(D[u'form_all']),
         J(D[u'form_distinct'])),
     u"1122 ⇎ 9293 各自同面并存两式(%d ⇎ %d), 6528 只用星号式, 793 只在状态图里用连字式; "
     u"单式搜索会把另外三份读成“没有这条规则”" % (D[u'form_distinct'][1], D[u'form_distinct'][3])),
    (u"义务语气", u"本注走词界正则 `\\bMUST\\b` ⇎ `\\bMUST NOT\\b`, 与建条目侧的子串档对账",
     u"大写 MUST %s ⇎ 裸 %s ⇎ MUST NOT %s ⇎ MAY %s ⇎ SHOULD %s" % (
         J(D[u'up_must_all']), J(D[u'must_bare']), J(D[u'must_not']), J(D[u'up_may']), J(D[u'up_should'])),
     u"逐份账 %s(正则档与子串档必须互相咬合才归零)。793 面上大写义务词 0 枚——它比 RFC 2119 的语气表早十年, "
     u"同一条规则在 793 是许可句(“may violate”), 到 1122 变 MUST, 到 9293 仍是 MUST 但义务主体换成 endpoint" % J(D[u'up_ledger'])),
    (u"改写判定", u"把 793 的 keep-quiet 整句归一后在 9293 折平面上查成员",
     u"读到原句=%d(0=读到, 即失败态)" % (1 - D[u'quiet_rewritten']),
     u"9293 收下 793 的“MSL=2 分钟”却把 “the TCP must keep quiet for a maximum segment lifetime” 换成 endpoint 说法——"
     u"逐字搬运与语气改写在同一份文档里同时发生, 所以“9293 只是排版重写”这个读法站不住"),
    (u"搬运⇎重写", u"长行集合代数(MINLEN=%d): 逐字节交 ⇎ 归一交 ⇎ 仅归一 ⇎ 只此两份 ⇎ 三份同压" % MINLEN,
     u"归一 %s ⇎ 逐字节 %s ⇎ 仅归一 %s ⇎ 非零对 %d" % (
         J(D[u'pair_share']), J(D[u'pair_byte']), J(D[u'pair_norm_only']), D[u'pair_nonzero']),
     u"793⇎9293 归一 %d(逐字节 %d ⇎ 只此两份 %d ⇎ 三份同压 %d) ⇎ 6528⇎9293 逐字节 %d ⇎ 1122⇎9293 逐字节 %d"
     u"——同一份 9293 对三家做了三种不同的事: 逐字搬   搬了重写   几乎不搬" % (
         D[u'pair_ad_share'], D[u'pair_ad_byte'], D[u'pair_ad_excl'], D[u'pair_ad_in3'],
         D[u'pair_byte'][5], D[u'pair_byte'][4])),
    (u"池代数", u"dict-of-set 计数 ⇎ 集合差算“只在本份”",
     u"池 %s ⇎ 分档 %s ⇎ 只在本份 %s ⇎ 并集 %s" % (
         D[u'pool_n'], J(D[u'pool_tier']), J(D[u'only_each']), D[u'union_all']),
     u"容斥闭合 %d ⇎ 分档闭合 %d; 四份同现 %d 枚⇒“只差一根写法轴”的对照档空转, 三源同现那枚是状态机记号行 %s" % (
         D[u'union_close'], D[u'pool_tier_close'], D[u'pool_4'], u' ⇎ '.join(D[u's3_examples']))),
    (u"带内外三轨", u"±%d 行邻域带, 先定位答句行再切片, 标题按归属口径自答句行向上扫" % BAND,
     u"带起 %s ⇎ 带止 %s ⇎ 答句行 %s ⇎ 带长 %s" % (
         J(D[u'win_start']), J(D[u'win_end']), J(D[u'win_center']), J(D[u'win_chars'])),
     u"三轨闭合合计 %d; 带内 MSL %s ⇎ 带外 %s——9293 把同一句埋在比 793 早得多的位置(第 %d 行 ⇎ 第 %d 行), "
     u"而 6528 的带外 MSL 余量为 %d 枚: 它全篇只在那一句里用 MSL; 标题若改从带首行向下扫, 四份里只有 793 改口——"
     u"归属口径给第 %d 行(§Sequence Numbers), 向下扫给第 %d 行(§Establishing a connection), "
     u"因为带是等长的行窗而不是节界" % (
         D[u'win_close_sum'], J(D[u'win_msl_in']), J(D[u'win_msl_out']), D[u'win_center'][3],
         D[u'win_center'][0], D[u'win_msl_out'][2], D[u'win_head_ln'][0], D[u'win_head_ln_fwd'][0])),
    (u"锚双轨", u"一枚锚同时按“等于某原文件行”⇎“其归一式落在折平面里”两种成员判",
     u"正文 %d 处 ⇎ 去重 %d 串 ⇎ 两轨同判 %d ⇎ 分歧 %d" % (
         D[u'anchor_total'], D[u'anchor_distinct'], D[u'track_agree'], len(D[u'track_split'])),
     u"归属错配 %d ⇎ 一源 %d ⇎ 跨源 %d ⇎ 四源 %d; 跨源那批全部落在 9293 面上(逐字收下的句子只存在于被抄的那一侧)" % (
         D[u'anchor_err'], D[u'anchor_single'], D[u'anchor_cross'], D[u'anchor_all4'])),
    (u"引用写法族", u"短横族 ⇎ 空格式分开数, 不把 “RFC-793” 折成 “RFC 793”",
     u"RFC-793 %s ⇎ RFC 793 %s ⇎ RFC 1122 %s" % (
         J(D[u'r793d']), J(D[u'r793s']), J(D[u'r1122s'])),
     u"1122 引 793 全走短横式(%d 枚), 9293 引 793 全走空格式(%d 枚)——规范化一次就会把两代文书的引用网读成一团; "
     u"数“被引了几次”时数字串轨与 RFC 前缀轨不等: 6528 在自己面上 %d ⇎ %d 枚 ⇎ 在 9293 面上 %d ⇎ %d 枚"
     u"(DOI 里的 RFC6528 ⇎ URL 里的 rfc6528 不带空格), 所以本注把两轨分开记" % (
         D[u'r793d'][1], D[u'r793s'][3], D[u'rfc_ref_6528'][2], D[u'rfc_ref_pref_6528'][2],
         D[u'rfc_ref_6528'][3], D[u'rfc_ref_pref_6528'][3])),
    (u"针的口径", u"建条目侧用有序三选一(“32 bit ISN” ⇎ “32-bit counter” ⇎ “32 bit”), 本注用逐枚游标扫描复现它, 另记字符类 `32[ -]bit` 一档",
     u"三选一口径 %s ⇎ 字符类口径 %s" % (J(D[u'isn_bits']), J(D[u'isn_bits_loose'])),
     u"两式在 793 上同值(%d ⇎ %d), 在另外三份上字符类多读 %d ⇎ %d ⇎ %d 枚——有序选一会把 “32-bit” 里非 counter "
     u"的那些枚整个放过; 本注另用逐枚游标扫描(命中即跳过整枚针)复现了有序选一, 两式读数与建条目侧逐份全等" % (
         D[u'isn_bits'][0], D[u'isn_bits_loose'][0],
         D[u'isn_bits_loose'][1] - D[u'isn_bits'][1], D[u'isn_bits_loose'][2] - D[u'isn_bits'][2],
         D[u'isn_bits_loose'][3] - D[u'isn_bits'][3])),
    (u"名分账", u"头部字段按 `^Obsoletes:` ⇎ `^Updates:` ⇎ `^STD:` ⇎ `^ISSN:` 逐行正则",
     u"Obsoletes %s ⇎ Updates %s ⇎ STD %s ⇎ ISSN %s ⇎ Standards Track %s" % (
         J(D[u'obsoletes']), J(D[u'updates']), J(D[u'std']), J(D[u'issn']), J(D[u'cat_std'])),
     u"6528 自己挂着 Obsoletes/Updates 头(它废止旧文并被 9293 再废止), 9293 一页点名含 6528 的清单; "
     u"STD: 头只有 9293 有, 但 “Category: Standards Track” 两枚都有(%s)——名分字段与类别行不能互相代读" % J(D[u'cat_std'])),
]
for a1, b1, c1, d1 in rows:
    A(u"| %s | %s | %s | %s |" % (a1, b1, c1, d1))
A(u"")
A(u"### 本注的判断")
A(u"四份文书对“主动关掉一条连接之后”给的不是同一个问题的四个答案, 而是四个问题的各一个答案: "
  u"793 回答“等多久”(2 枚 MSL, 且 MSL=2 分钟是任意取的工程常数)并顺手承认可以不回答“要不要等”(明文许可违背 quiet time); "
  u"1122 回答“必须等”(MUST linger)却把“能不能跳过”写进同一句的两个条件里; "
  u"6528 拒绝回答“等多久”, 把问题换成“从上一段报文最后被见到起过了几枚 MSL”; "
  u"9293 回答“谁承担这个义务”(TCP endpoint 而非 TCP), 同时把前三份一起废止。"
  u"所以任何“取最大值/取最新”式的合并都会丢东西: 按时间最新取 9293, 就丢掉 6528 的起算点改法; "
  u"按字面最全取 793, 就丢掉 1122 那两条件出口——而 9293 恰恰同时收下 793 的分钟句与 1122 的条件句, "
  u"却在 keep-quiet 那句上做了主语手术。逐字节交(29 枚 ⇎ 1122 方向 0 枚 ⇎ 6528 方向 15 枚)与归一交(351 ⇎ 16 ⇎ 16) "
  u"分成两套账, 正是这场“收内容 ⇎ 改语气”双轨操作的量证。")
A(u"另有两处容易被读成矛盾而其实不是: 其一, 793 全篇大写 MUST 零枚, 不是它没有义务语句, 而是它用小写 must 与许可句写义务, "
  u"所以“按 RFC 2119 关键词搜 793 得零命中”是搜索口径的产物而非规范的产物; 其二, 6528 面上 “2 minutes” 零枚而 “MSL” 只 %d 枚, "
  u"不是它不谈时长, 而是它把时长写成乘法式 `2*MSL` 并把 MSL 的值推给被引文书——时长字面的缺席与判据的存在可以同时为真。" % D[u'msl'][2])
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; rfc-editor.org 此刻给这四份挂的现行状态页与勘误页"
  u"(6528 现在被标成 Historic 还是 Experimental, 在库字节里读不出来); 此后哪份在途草案又动了 TIME-WAIT 这一段; "
  u"现网内核实际把 TIME-WAIT 设成多久(“2MSL ⇎ 5 秒 ⇎ 可 sysctl 覆盖”这类都是实现事实, 不是文书事实); "
  u"RFC 2119 关键词表相对 793 的年代差只能由常识给出, 在库四份文件自身不写“793 早于 2119”; "
  u"9293 的 BOM 是抓取链条上哪一环加上去的, 还是 RFC Editor 的原版面自带。")
A(u"以上量要么在本机之外、要么随实现与站点漂移, 复算通道里没有它们的位置; 门槛只认在库字节。")
NEW = u"## ⛓解读注" + NL + NL + NL.join(L2) + NL
i = TT.index(u"## ⛓解读注")
out = TT[:i] + NEW
assert out.count(u"## ⛓解读注") == 1
T2 = ENTRY + u'.tmp'
io.open(T2, u'w', encoding=u'utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"⛓解读注 已写入 %s ｜ 表 %d 行 ｜ 注区 %d 字符 ｜ 复算 %d 键 ⇎ 不符 0 ⇎ 独有 %d ⇎ 未覆盖 %d ⇎ 恒等式 %d ⇎ DERIV %d 全对"
      % (ENTRY, len(rows), len(NEW), len(D), len(MISS), len(UNCOVER), len(CH[u'zid']), len(JJ)))
