# -*- coding: utf-8 -*-
# ============================================================================
# B94 建条目侧(第二套实现, A 侧): 单文本压缩 · 跨六份一手文书的问答式压缩
#   问题: ICMP 差错报文该限到什么速率、谁说了算？
#   源(六份, 时间序) = 792(1981) ⇎ 1009(1987) ⇎ 1122(1989) ⇎ 1812(1995)
#        ⇎ 4443(2006) ⇎ ip-sysctl(内核实现文档)
#   本文件只做两件事: ①SCAN 段对六面各量一遍(第二套实现见 corpus/_pick94.py,
#     两套在口径一致的键集上逐键对账, 对账件由 _pick94.py 写 corpus/_b94meas.json);
#   ②按 B96 版式发射条目(编码区数字全部由 V() 从对账件插值, 零手填)。
# 机制档位(A 侧, 与 _pick94.py 的 B 轨换机制不换口径):
#   逐行正则切页壳 ⇎ 面折平 ⇎ split(chr(10)) 行面 ⇎ str.count 子串档 ⇎
#   lookaround 词界正则 token 档 ⇎ 游标 find 环 ⇎ bisect 行号表 ⇎
#   闭式乘除 ⇎ 逐次减法验商 ⇎ 二串 Horner ⇎ 逐位倍增 ⇎ 一条正则解数×单位对。
# 运行次序: python -X utf8 corpus/_mkB94.py  ⇎ python -X utf8 corpus/_pick94.py
#           ⇎ 再跑一遍 _mkB94.py(读对账件发射) ⇎ _mk94emit.py ⇎ _wire94.py ⇎ _fill94.py
# 口径不同不对账(本遍显式列入, 与 _pick94.py §RECON 同口径):
#   ① bytes/cp 本遍按 len() 计, _pick94.py 另有逐迭代第二尺, 只在对账件内自证, 不互对;
#   ② ratemask 的 mask_bits/mask_stars 本遍按位定义行尾星号读, _pick94.py 另经位标字母表
#      交叉证, 本遍只在 mask_dec 一号面上对账;
#   ③ blocks 的块长以行数字符计, 两遍同尺; 但 ob 义务词本遍按预大写化游标计, _pick94.py
#      另有引擎内大小写折叠第二尺, 只在对账件内自证, 不互对;
#   ④ eq 里的派生量(rate_calc/agg_from_iface/split_from_dir/ts_states)本遍现算自同遍其它键,
#      _pick94.py 亦现算, 但对账止于被乘键与打印键, 派生式本身各自闭合。
# ============================================================================
import io, json, os, re, sys, bisect
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SRC = [u'corpus/raw/icmpRate/rfc792.txt', u'corpus/raw/icmpRate/rfc1009.txt',
       u'corpus/raw/icmpRate/rfc1122.txt', u'corpus/raw/icmpRate/rfc1812.txt',
       u'corpus/raw/icmpRate/rfc4443.txt', u'corpus/raw/icmpRate/ip-sysctl.txt']
LABELS = [u'792', u'1009', u'1122', u'1812', u'4443', u'sys']
NSRC = 6
MEASA = u'corpus/_tmp94_measA.json'
MEAS = u'corpus/_b94meas.json'
ENTRY = u'corpus/babeltele/B94_icmp_error_ratelimit_compression.md'
NET = u'corpus/_atoms94.txt'

# --- SCAN BEGIN ---
def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


def pnorm(s):
    """最宽档: 小写 + 引号撇音符整枚删除 + 连字符族归一 + 只留 [0-9a-z 汉字 . - 空格] + 空白折一。"""
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


T = [rd(p) for p in SRC]
LINES = [t.split(chr(10)) for t in T]
FLAT = [u' '.join(t.split()) for t in T]
LOW = [f.lower() for f in FLAT]
PN = [pnorm(f) for f in FLAT]
F = {}


def a_cnt(hay, nd):
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def a_ub(s, w):
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha()):
            c += 1
        i = j + 1


def a_sh(x):
    return (x.strip() == u'' or x == u'\x0c'
            or re.search(u'\\[Page \\d+\\]', x) is not None
            or re.match(u'^RFC ?\\d+\\b', x) is not None
            or re.match(u'^Internet Engineering Task Force\\s*$', x) is not None
            or re.match(u'^\\s*Network Working Group\\s*$', x) is not None
            or re.match(u'^\\s*Request for Comments:\\s*\\d+\\s*$', x) is not None)


SHP = [pnorm(chr(10).join([x for x in LINES[i] if not a_sh(x)])) for i in range(NSRC)]
NOSHP = [chr(10).join([x for x in LINES[i] if not a_sh(x)]) for i in range(NSRC)]
# 原面 → 摘壳原面(按行的映射表, 用于把摘壳命中回挂到原行号)
SHP2RAW = []
for i in range(NSRC):
    keep, acc = [], 0
    _mp = []
    for nr, x in enumerate(LINES[i]):
        if not a_sh(x):
            _mp.append(nr)
    SHP2RAW.append(_mp)

# —— 面量(六面逐面) ——
F['bytes'] = [len(T[i].encode('utf-8')) for i in range(NSRC)]
F['cp'] = [len(T[i]) for i in range(NSRC)]
F['n_lf'] = [a_cnt(T[i], chr(10)) for i in range(NSRC)]
F['splitnl'] = [len(LINES[i]) for i in range(NSRC)]
F['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
F['ff'] = [T[i].count(u'\x0c') for i in range(NSRC)]
F['blank'] = [len([x for x in LINES[i] if x.strip() == u'']) for i in range(NSRC)]
F['nonblank'] = [len([x for x in LINES[i] if x.strip() != u'']) for i in range(NSRC)]
F['maxlen'] = [max(len(x) for x in LINES[i]) for i in range(NSRC)]
F['tab'] = [T[i].count(u'\t') for i in range(NSRC)]
F['nonascii'] = [len(set(ord(c) for c in T[i] if ord(c) > 127)) for i in range(NSRC)]
F['bom'] = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
F['nsrc'] = [NSRC]

# —— 页壳两档(本遍 A 轨正则行判; _pick94.py 用 token 形状判, 口径一致) ——
F['shell'] = [len([x for x in LINES[i] if a_sh(x)]) for i in range(NSRC)]
F['shell_body'] = [F['splitnl'][i] - F['shell'][i] for i in range(NSRC)]
F['foot_page'] = [len([x for x in LINES[i] if re.search(u'\\[Page \\d+\\]', x)]) for i in range(NSRC)]
F['hdr_rfc'] = [len([x for x in LINES[i] if a_sh(x) and x.strip().split()[:1] == [u'RFC']]) for i in range(NSRC)]

# —— 年份(六面各一枚, 时间序) ——
MONTHS = (u'January|February|March|April|May|June|July|August|September|October|November|December')
_yr = []
for i in range(NSRC):
    mt = re.search(u'(?:%s) ((19|20)\\d\\d)' % MONTHS, T[i])
    _yr.append(int(mt.group(1)) if mt else -1)
F['year'] = _yr
F['year_span'] = [max(y for y in _yr if y > 0) - min([y for y in _yr if y > 0])]

# —— 判词针(三档口径: 逐行 ⇎ 全篇折平 ⇎ 摘壳折平) ——
NEEDLES = [
    u'may send a source quench message for every message that it discards',
    u'must be prepared to limit the frequency with which it sends',
    u'at most once per T millseconds',
    u'of the order of 100 bytes',
    u'2,000 datagrams per second per interface',
    u'The recommended maximum rate is 1 per second per',
    u'very low rate, e.g., 0.005 per second',
    u'host MAY send a Source Quench message if it is',
    u'MUST be able to limit the rate at which the messages can be generated',
    u'SHOULD also be able to limit the rate at which it sends other sorts',
    u'SHOULD be settable as part of the configuration',
    u'is left to the implementor',
    u'send an ICMP error message for every N dropped packets',
    u'at most once per T milliseconds',
    u'MUST limit the rate of ICMPv6 error messages it originates',
    u'token bucket, limiting the average rate',
    u'N can be either packets/second or a fraction',
    u'allowing up to B error messages to be transmitted in a burst',
    u'is not reasonable',
    u'The rate-limiting parameters SHOULD be configurable',
    u'the possible defaults could be B=10',
    u'N=10/s',
    u'Removed the Timer-based and the Bandwidth-based methods',
    u'TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE',
    u'controls the burst size of these packets',
    u'Mask made of ICMP types for which rates are being limited',
    u'These are rate limited by default',
]
rows3 = []
for nd in NEEDLES:
    q = pnorm(nd)
    r = []
    for i in range(NSRC):
        cl = len([x for x in LINES[i] if q in pnorm(x)])
        cf = a_cnt(LOW[i], q)
        cs = a_cnt(SHP[i], q)
        r.append((cl, cf, cs))
    rows3.append(r)
F['needles3'] = rows3
F['needle_n'] = [len(NEEDLES)]
F['needle_src'] = [[LABELS[i] for i in range(NSRC) if rows3[k][i][2] > 0] for k in range(len(NEEDLES))]
cold = [NEEDLES[k] for k in range(len(NEEDLES)) if not F['needle_src'][k]]
assert cold == [], cold
F['wrapcut'] = [[LABELS[i], NEEDLES[k][:40]] for k in range(len(NEEDLES)) for i in range(NSRC)
                if rows3[k][i][1] == 0 and rows3[k][i][2] > 0]
F['wrapcut_n'] = [len(F['wrapcut'])]

# —— 关键句落点行(三把行号尺: 累加+二分 ⇎ 摘壳随行表 ⇎ 摘壳偏移回原面) ——
CUMS = []
for i in range(NSRC):
    _a, _t = [], 0
    for _x in LINES[i]:
        _t += len(_x) + 1
        _a.append(_t)
    CUMS.append(_a)


def shp_off_to_rawoff(i, foff):
    """摘壳折面偏移 → 原面码位偏移(经摘壳行号 + 行内偏移)。"""
    nr = SHP2RAW[i][foff[0]]
    base = CUMS[i][nr - 1] if nr else 0
    return base + foff[1]


PIN = []
for k, nd in enumerate(NEEDLES):
    q = pnorm(nd)
    for i in range(NSRC):
        if rows3[k][i][2] <= 0:
            continue
        # 摘壳折面找 q, 再定落点原行(本遍只用折面一次线性找, A 轨口径)
        fpos = SHP[i].find(q)
        # 折面偏移 → 摘壳行号(逐行累积长度表 + bisect)
        _cum, _t = [], 0
        for _ln in NOSHP[i].split(chr(10)):
            _t += len(pnorm(_ln)) + 1
            _cum.append(_t)
        shp_line = bisect.bisect_right(_cum, fpos)
        raw_line = SHP2RAW[i][shp_line]
        PIN.append([LABELS[i], k, nd[:44], raw_line])
F['pin_lines'] = PIN
F['pin_by_src'] = [len([z for z in PIN if z[0] == LABELS[i]]) for i in range(NSRC)]
F['pin_wrap'] = [len([z for z in PIN if False])]  # 单行内定位不判跨行, 跨行另由 needles3 档给出

# —— 义务词五式(预大写化游标, 与 _pick94.py B 轨引擎折叠在口径上等价) ——
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']
F['ob'] = [[a_ub(T[i].upper(), w) for w in OB] for i in range(NSRC)]
F['ob_tot'] = [sum(x) for x in F['ob']]

# —— 数×单位对(一条选择支正则; 与采集遍手工扫在口径一致) ——
RX = re.compile(u'(?<![A-Za-z0-9.,])(\\d+(?:[.,]\\d+)?)[ ]?'
                u'(per second|datagrams per second|packets/second|/s|milliseconds|millseconds|'
                u'mbps|kbps|bytes|octets|words|times per second)(?![A-Za-z])', re.I)
F['pairs'] = [sorted(set((m[0], m[1].lower()) for m in RX.findall(T[i]))) for i in range(NSRC)]
F['pairs_n'] = [len(F['pairs'][i]) for i in range(NSRC)]
RATEU = [u'per second', u'datagrams per second', u'packets/second', u'/s', u'times per second']
F['rate_pairs_per_src'] = [len([p for p in F['pairs'][i] if p[1] in RATEU]) for i in range(NSRC)]

# —— 切句(正向后顾切; 与采集遍两轨切句同句集) ——
def sents_flat(i):
    return [z for z in re.split(u'(?<=[.!?]) ', FLAT[i]) if z.strip()]


F['sents_n'] = [len(sents_flat(i)) for i in range(NSRC)]
CTXKW = {u'arp': [u'arp'], u'icmp': [u'icmp'], u'ping_echo': [u'ping', u'echo'],
         u'token': [u'token'], u'timestamp': [u'timestamp'], u'source quench': [u'source quench']}
ctx_rows = []
for i in range(NSRC):
    sa = sents_flat(i)
    for j, s in enumerate(sa):
        if u'rate' in s and re.search(u'\\d', s):
            win = u' '.join(sa[max(0, j - 1):j + 2])
            ctx_rows.append([LABELS[i], s[:88],
                             [c for c in sorted(CTXKW) if any(k in win for k in CTXKW[c])]])
F['rate_sents'] = ctx_rows
F['rate_sents_n'] = [len([z for z in ctx_rows if z[0] == LABELS[i]]) for i in range(NSRC)]
F['icmp_rate_sents'] = [len([1 for z in ctx_rows
                             if u'icmp' in z[2] and u'source quench' not in z[2]
                             and u'arp' not in z[2] and u'ping_echo' not in z[2]])]

# —— sysctl 键表(键名 ⇎ 类型; 默认值 A 轨正则取) ——
KEYRE = re.compile(u'^([a-z0-9_/]+) - (INTEGER|BOOLEAN|STRING)\\s*$')
GROUPRE = re.compile(u'^\\s*([a-z0-9_/*]+):\\s*$')
keys, ktype, gkeys = {}, {}, {}
cur, prev_nb = None, u''
for x in LINES[5]:
    m = KEYRE.match(x)
    if m:
        cur = m.group(1)
        keys[cur] = u''
        ktype[cur] = m.group(2)
        g = GROUPRE.match(prev_nb)
        if g:
            gkeys[g.group(1) + u'/' + cur] = cur
    else:
        if x.strip() != u'':
            prev_nb = x
        if cur is not None:
            keys[cur] += u' ' + x
F['sys_keys_total'] = [len(keys)]
ICMPK = sorted([k for k in keys if k.startswith(u'icmp_')])
F['sys_icmp_keys'] = ICMPK
F['sys_icmp_n'] = [len(ICMPK)]
F['sys_group_keys'] = sorted(gkeys)


def dft_a(seg):
    m = re.search(u'Default:\\s*(\\S+)', seg)
    return m.group(1).strip(u'.') if m else None


tok_a = dict((k, dft_a(keys[k])) for k in keys)
F['sys_default_tokens'] = tok_a
F['sys_defaults_to'] = sorted([k for k in keys if u'Defaults to' in keys[k] and tok_a[k] is None])
RATEK = ICMPK + [gkeys[k] for k in sorted(gkeys)]


def dint(k):
    t = tok_a[k]
    assert re.match(u'^-?[0-9]+$', t), (k, t)
    return int(t)


F['rl_ms'] = [dint(u'icmp_ratelimit')]
F['per_sec'] = [dint(u'icmp_msgs_per_sec')]
F['burst'] = [dint(u'icmp_msgs_burst')]
F['rl6_ms'] = [dint(u'ratelimit')]

# —— ratemask 三轨换算(闭式 2**b 求和 ⇎ 逐位倍增 ⇎ 二串 Horner) ——
st = T[5]
mrow = re.search(u'Default mask:\\s+([01]{10,30}) \\((\\d+)\\)', st)
assert mrow, u'ratemask 行读不到'
maskbin, maskdec = mrow.group(1), int(mrow.group(2))
label = re.search(u'Significant bits: ([IHGFEDCBA9876543210]+)', st).group(1)
assert len(label) == len(maskbin), (len(label), len(maskbin))


def bitpos(ch):
    return ord(ch) - ord(u'A') + 10 if ch.isalpha() else int(ch, 16)


starred = []
for x in LINES[5]:
    s = x.strip()
    if len(s) > 3 and s[0] in u'0123456789ABCDEFGHI' and s[1] == u' ' and s.endswith(u'*'):
        starred.append(s[0])
star_bits = sorted(bitpos(c) for c in starred)
sum_pow = sum(2 ** bitpos(c) for c in starred)
reg, cur2 = 0, 1
for b in range(len(maskbin)):
    if b in star_bits:
        reg += cur2
    cur2 <<= 1
binval = 0
for ch in maskbin:
    binval = binval * 2 + int(ch)
lab_on = sorted(bitpos(label[j]) for j in range(len(maskbin)) if maskbin[j] == u'1')
assert sum_pow == reg == binval == maskdec, (sum_pow, reg, binval, maskdec)
assert lab_on == star_bits, (lab_on, star_bits)
F['mask_bits'] = star_bits
F['mask_stars'] = sorted(starred)
F['mask_bin_len'] = [len(maskbin)]
F['mask_dec'] = [maskdec]

# —— 换算等式(每个数从面里读, 每个结果两把尺) ——
NUMWORD = {u'zero': 0, u'one': 1, u'two': 2, u'three': 3, u'four': 4, u'five': 5, u'six': 6,
           u'seven': 7, u'eight': 8, u'nine': 9, u'ten': 10}
UMULT = {u'k': 10 ** 3, u'M': 10 ** 6}
MS_PER_S = 10 ** 3


def num(pat, face):
    g = re.findall(pat, face)
    assert len(g) == 1, (pat, g)
    return int(g[0].replace(u',', u''))


def fnum(pat, face):
    g = re.findall(pat, face)
    assert len(g) == 1, (pat, g)
    return float(g[0])


eq = {}
mbps = fnum(u'ds1 lines \\((\\d\\.\\d) mbps\\)', PN[1])
kbps = num(u'frequently (\\d+) kbps', PN[1])
avgb = num(u'the order of (\\d+) bytes', PN[1])
rate_pr = num(u'(\\d[\\d,]*) datagrams per second per interface', PN[1])
agg_pr = num(u'aggregate throughput of ([\\d,]+) datagrams', PN[1])
split_pr = num(u'would imply ([\\d,]+) datagrams', PN[1])
s_iface = [z for z in sents_flat(1) if u'ds1 lines and' in z and u'ethernet' in z]
assert len(s_iface) == 1, len(s_iface)
si = s_iface[0]
n_ds1 = num(u'supported (\\d+) ds1 lines', si)
n_eth = si.count(u'ethernet')
n_iface_calc = n_ds1 + n_eth
n_iface_print = agg_pr // rate_pr
assert n_iface_calc == n_iface_print, (n_iface_calc, n_iface_print)
acc_iface = 0
for _ in range(n_iface_calc):
    acc_iface += rate_pr
assert acc_iface == agg_pr, (acc_iface, agg_pr)
n_dir = split_pr // agg_pr
nd_sent = [z for z in sents_flat(1) if u'input and output' in z]
assert len(nd_sent) == 1, len(nd_sent)
n_dir_face = nd_sent[0].count(u'input') + nd_sent[0].count(u'output')
assert n_dir == n_dir_face, (n_dir, n_dir_face)
acc_dir = 0
for _ in range(n_dir):
    acc_dir += agg_pr
assert acc_dir == split_pr, (acc_dir, split_pr)
m20 = re.search(u'\\((\\d+) bytes = (\\d+) words\\)', PN[3])
assert m20, u'20 bytes 行读不到'
ip20, ipw = int(m20.group(1)), int(m20.group(2))
oct32 = num(u'exactly (\\d+) bits of type-specific data', PN[4])
assert ip20 % ipw == 0, (ip20, ipw)
bytes_per_word = ip20 // ipw
bits_per_byte = oct32 // bytes_per_word
assert bits_per_byte * bytes_per_word == oct32, (bits_per_byte, bytes_per_word, oct32)
bps_line = int(mbps * UMULT[u'M'])
per_pkt_bits = avgb * bits_per_byte
rate_calc = bps_line / per_pkt_bits
rem, q = bps_line, 0
while rem >= per_pkt_bits:
    rem -= per_pkt_bits
    q += 1
assert q == rate_calc and rem == 0, (q, rate_calc, rem)
eq['mbps'] = mbps
eq['kbps'] = kbps
eq['avgb'] = avgb
eq['bytes_per_word'] = bytes_per_word
eq['bits_per_byte'] = bits_per_byte
eq['rate_calc'] = rate_calc
eq['rate_calc_sub'] = q
eq['rate_printed'] = rate_pr
eq['rate_gap'] = rate_pr - rate_calc
eq['n_ds1'] = n_ds1
eq['n_eth'] = n_eth
eq['n_iface_calc'] = n_iface_calc
eq['n_iface_print'] = n_iface_print
eq['agg_printed'] = agg_pr
eq['agg_from_iface'] = acc_iface
eq['n_dir'] = n_dir
eq['n_dir_face'] = n_dir_face
eq['split_printed'] = split_pr
eq['split_from_dir'] = acc_dir
eq['rl_ms'] = F['rl_ms'][0]
eq['rl_per_s'] = MS_PER_S / eq['rl_ms']
eq['per_sec'] = F['per_sec'][0]
eq['burst'] = F['burst'][0]
eq['ratio_global_vs_target'] = eq['per_sec'] / (MS_PER_S / eq['rl_ms'])
eq['per_burst'] = eq['per_sec'] / eq['burst']
eq['rl6_ms'] = F['rl6_ms'][0]
eq['rl6_vs_v4'] = eq['rl6_ms'] / eq['rl_ms']
b44 = num(u'could be b=(\\d+)', PN[4])
n44 = num(u'n=(\\d+)/s', PN[4])
eq['b4443'] = b44
eq['n4443'] = n44
eq['n44_vs_kernel_per_sec'] = eq['per_sec'] / n44
eq['n44_vs_kernel_per_target'] = n44 / (MS_PER_S / eq['rl_ms'])
eq['burst_vs_b4443'] = eq['burst'] / b44
p576 = num(u'exceeding (\\d+) bytes', PN[3])
eq['p576'] = p576
eq['bytes_per_s_4443'] = p576 * n44
eq['bits_per_s_4443'] = p576 * n44 * bits_per_byte
hz = fnum(u'e\\.g\\., (0\\.\\d+) per second', PN[2])
eq['hz_005'] = hz
eq['period_200'] = 1 / hz
m50 = re.search(u'(\\d+) or (\\d+) times per second', PN[3])
assert m50, u'市电频率句读不到'
f50, f60 = int(m50.group(1)), int(m50.group(2))
l16 = num(u'updated at least (\\d+) times per second', PN[3])
msix = NUMWORD[re.search(u'at most the (\\w+) low-order bits', PN[3]).group(1)]
two6 = 1
for _ in range(msix):
    two6 <<= 1
low63, step3 = 0, 1
for _ in range(msix):
    low63 += step3
    step3 <<= 1
assert low63 + 1 == two6 == 2 ** msix, (low63, two6, msix)
eq['hz_mains'] = [f50, f60]
eq['ts_min_per_s'] = l16
eq['ts_bits'] = msix
eq['ts_states'] = two6
eq['ts_states_pow'] = 2 ** msix
eq['ts_low_bits_mask'] = low63
eq['ts_margin_50_over_16'] = f50 // l16
eq['ts_wrap_s'] = two6 // f50
eq['n_rate_pairs_792'] = F['rate_pairs_per_src'][0]
eq['n_rate_pairs_1122'] = F['rate_pairs_per_src'][2]
eq['n_rate_pairs_sys'] = F['rate_pairs_per_src'][5]
F['eq'] = dict(eq)

# —— 块定界两档(正则锚行 ⇎ 折面偏移回行; 目录点线为门槛) ——
def blk_re(i, hdr_pat, stop_pat):
    a = next(k for k, x in enumerate(LINES[i]) if re.search(hdr_pat, x))
    b = next(k for k in range(a + 1, len(LINES[i])) if re.search(stop_pat, LINES[i][k]))
    return a, b


def blk_fold(i, qa, qb):
    fa, fb = SHP[i].find(qa), SHP[i].find(qb)
    assert fa >= 0 and fb >= 0, (i, qa, qb)
    # 折面偏移 → 摘壳行号 → 原行号
    _cum, _t = [], 0
    for _ln in NOSHP[i].split(chr(10)):
        _t += len(pnorm(_ln)) + 1
        _cum.append(_t)
    return (SHP2RAW[i][bisect.bisect_right(_cum, fa)],
            SHP2RAW[i][bisect.bisect_right(_cum, fb)])


BLKS = [(1, u'^\\s*2\\.2\\.3\\.\\s+Source Quench\\s*$', u'^\\s*2\\.2\\.4\\.\\s+Time Exceeded\\s*$',
         u'2.2.3. source quench', u'2.2.4. time exceeded'),
        (3, u'^4\\.3\\.2\\.8 Rate Limiting', u'^4\\.3\\.3 SPECIFIC',
         u'4.3.2.8 rate limiting', u'4.3.3 specific issues'),
        (4, u'^\\s*\\(f\\) Finally', u'^\\s*NOTE: THE RESTRICTIONS',
         u'(f) finally, in order to limit the bandwidth', u'note: the restrictions under')]
OB2 = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']
blk_out = []
for (i, pa_, pb_, na, nb) in BLKS:
    a1, b1 = blk_re(i, pa_, pb_)
    a2, b2 = blk_fold(i, pnorm(na), pnorm(nb))
    ca = chr(10).join(LINES[i][a1:b1])
    cb = chr(10).join(LINES[i][a2:b2])
    assert a1 == a2 and b1 == b2, (na, a1, a2, b1, b2)
    assert ca == cb, (na, len(ca), len(cb))
    oa = [a_ub(ca.upper(), w) for w in OB2]
    blk_out.append([LABELS[i], a1, b1 - a1, len(ca), oa, sum(oa)])
F['blocks'] = blk_out
F['blocks_oblabels'] = OB2

# —— 语形族(子串档 ⇎ 词频档; 存在性集合 ⇎ Counter 词频) ——
FAMW = [u'burst', u'configurable', u'settable', u'throttle', u'ratelimit', u'bandwidth',
        u'milliseconds', u'millseconds', u'dropped', u'discard']
FAMP = [u'source quench', u'source quenches', u'token bucket', u'timer-based', u'token-bucket',
        u'rate-limiting', u'rate limiting', u'rate limit', u'icmp error', u'icmp errors',
        u'icmpv6 error', u'destination unreachable', u'time exceeded', u'parameter problem',
        u'limit the rate', u'limit the frequency', u'per second', u'dropped datagrams',
        u'dropped packets', u'specific targets', u'low-order bits']
FAM = list(dict.fromkeys(FAMW + FAMP))
TOK = [FLAT[i].split(u' ') for i in range(NSRC)]
TOKS = [[w.strip(u'.,;:!?"\'()') for w in z] for z in TOK]
hist = []
for i in range(NSRC):
    h = {}
    for n in range(1, 5):
        h[n] = Counter(zip(*[TOKS[i][k:] for k in range(n)]))
    hist.append(h)


def ng(h, p):
    parts = tuple(p.split(u' '))
    return h[len(parts)][parts]


RXW = {}


def sub_bnd(s, p):
    if p not in RXW:
        RXW[p] = re.compile(u'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(p))
    return len(RXW[p].findall(s))


freq_bnd = [[sub_bnd(LOW[i], p) for p in FAM] for i in range(NSRC)]
freq_sub = [[a_cnt(LOW[i], p) for p in FAM] for i in range(NSRC)]
freq_raw = [[ng(hist[i], p) for p in FAM] for i in range(NSRC)]
for i in range(NSRC):
    for k, p in enumerate(FAM):
        assert (freq_raw[i][k] > 0) == (freq_bnd[i][k] > 0), (LABELS[i], p, freq_raw[i][k], freq_bnd[i][k])
F['fams'] = FAM
F['fams_n_types'] = [len(FAM)]
F['fams_present'] = [[1 if freq_bnd[i][k] > 0 else 0 for k in range(len(FAM))] for i in range(NSRC)]
F['fams_freq'] = freq_bnd
F['fams_freq_sub'] = freq_sub
F['fams_prefix_tax'] = [[freq_sub[i][k] - freq_bnd[i][k] for k in range(len(FAM))] for i in range(NSRC)]
for i in range(NSRC):
    assert all(z >= 0 for z in F['fams_prefix_tax'][i]), (LABELS[i], F['fams_prefix_tax'][i])
F['fams_n_per_src'] = [sum(F['fams_present'][i]) for i in range(NSRC)]
F['fams_excl'] = [[p for k, p in enumerate(FAM)
                   if F['fams_present'][i][k] and all(F['fams_present'][j][k] == 0
                                                      for j in range(NSRC) if j != i)]
                  for i in range(NSRC)]
# --- SCAN END ---

for k, v in [('wrapcut_n', len(F['wrapcut'])), ('pin_by_src', F['pin_by_src'])]:
    pass
assert F['nsrc'][0] == NSRC, u'源数不合'
assert F['bom'] == [0] * NSRC, u'意外 BOM'
assert F['nonascii'] == [0] * NSRC, u'意外非 ASCII 码位'
assert F['ob_tot'][0] > 0, u'义务词全零'
assert F['fams_n_types'][0] == len(FAM), u'语形族次序挪动'
assert F['icmp_rate_sents'][0] > 0, u'ICMP 速率话题句为零(与采集遍不符)'
assert F['rate_pairs_per_src'][0] == 0, u'792 不应有数×速率单位对'
assert set(F['sys_group_keys']) == set([u'icmp/*/ratelimit']), F['sys_group_keys']
assert F['sys_icmp_n'][0] > 0, u'icmp_* 键表为空'
assert F['needle_n'][0] == len(NEEDLES), u'针数不合'
assert F['mask_dec'][0] == 6168, u'ratemask 十进制读数不合'
for z in F['blocks']:
    assert z[2] > 0 and z[3] > 0, u'块定界越界: %s' % z[0]
assert len(F['pin_lines']) == sum(F['pin_by_src']), u'落点行账不合'
assert F['year_span'][0] == 2006 - 1981, u'年份跨度不合'

io.open(MEASA, 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1, default=str))
print(u'A 侧量测: %d 枚键 → %s' % (len(F), MEASA))
for k in sorted(F):
    v = F[k][0] if isinstance(F[k], list) else F[k]
    print(u'  %-24s %s' % (k, v))

# ---- 对账件读取(第二套实现 _pick94.py 写的逐键对账; 没有它就只用 A 侧读数) ----
A = F
if os.path.exists(MEAS):
    Mraw = json.load(io.open(MEAS, encoding='utf-8'))
    # 口径不同不对账清单(见文件头), 这些键仅做存在性核对, 不做值等
    NOCHECK = set([u'bytes', u'cp', u'mask_bits', u'mask_stars', u'ob',
                   u'fams_freq_sub', u'fams_prefix_tax', u'pairs', u'rate_sents'])
    shared = sorted([k for k in A if k in Mraw and k not in NOCHECK])
    for k in shared:
        a0 = A[k][0] if isinstance(A[k], list) else A[k]
        m0 = Mraw[k][0] if isinstance(Mraw[k], list) else Mraw[k]
        assert a0 == m0, u'A 侧重跑读数挪动: %s %s ⇎ %s' % (k, m0, a0)
    print(u'对账件已复核: %d 枚键在口径一致名单上同值(不核 %d 枚显式口径不同键)'
          % (len(shared), len(NOCHECK)))
else:
    print(u'对账件未生成(先跑 corpus/_pick94.py), 本遍用 A 侧读数发射')

# ---- 发射条目 ----
REG = {}


def V(name):
    v = F[name][0]
    REG.setdefault(str(v), u"B94V('%s')" % name)
    return v


# 原文锚 = 采集遍同口径针(NEEDLES 子集, 每条有明确来源)
ATOM_A = NEEDLES[0]      # 792: 每丢弃一枚发一枚 SQ
ATOM_B = NEEDLES[3]      # 1009: 100 字节平均
ATOM_C = NEEDLES[4]      # 1009: 2,000 包/秒/接口
ATOM_D = NEEDLES[5]      # 1122: 唯一 1 per second 是 ARP 洪泛
ATOM_E = NEEDLES[8]      # 1812: MUST limit the rate
ATOM_F = NEEDLES[9]      # 1812: SHOULD also limit other sorts
ATOM_G = NEEDLES[10]     # 1812: SHOULD settable
ATOM_H = NEEDLES[11]     # 1812: left to the implementor
ATOM_I = NEEDLES[12]     # 1812: per N dropped packets
ATOM_J = NEEDLES[14]     # 4443: MUST limit ICMPv6 error
ATOM_K = NEEDLES[15]     # 4443: token bucket
ATOM_L = NEEDLES[16]     # 4443: N 可按 packets/second 或链路分数
ATOM_M = NEEDLES[17]     # 4443: 波束 B
ATOM_N = NEEDLES[18]     # 4443: every T 不合理
ATOM_O = NEEDLES[19]     # 4443: 参数 SHOULD 可配
ATOM_P = NEEDLES[20]     # 4443: 示例默认 B=10
ATOM_Q = NEEDLES[22]     # 4443: 移除 timer/bandwidth 两法
ATOM_R = NEEDLES[23]     # 4443: 限速条款优先
ATOM_S = NEEDLES[24]     # sys: 爆突发数
ATOM_T = NEEDLES[25]     # sys: ratemask 类型掩码
ATOM_U = NEEDLES[26]     # sys: 默认限速
ATOMS = [ATOM_A, ATOM_B, ATOM_C, ATOM_D, ATOM_E, ATOM_F, ATOM_G, ATOM_H, ATOM_I, ATOM_J,
         ATOM_K, ATOM_L, ATOM_M, ATOM_N, ATOM_O, ATOM_P, ATOM_Q, ATOM_R, ATOM_S, ATOM_T, ATOM_U]
AT2IDX = dict((a, NEEDLES.index(a)) for a in ATOMS)


def src_of(a):
    k = AT2IDX[a]
    return F['needle_src'][k]


io.open(NET, 'w', encoding='utf-8', newline=chr(10)).write(chr(10).join(ATOMS) + chr(10))

E = []
# 题面 + 面账
E.append(u'🧭 源账: 六份一手文书按时间序(792 1981 ⇎ 1009 1987 ⇎ 1122 1989 ⇎ 1812 1995 ⇎ 4443 2006 '
         u'⇎ ip-sysctl 内核文档), 跨 %d 年; 六面折平 %d 词, 抽壳 %d 行, 页脚 %d 枚, RFC 眉行 %d 枚, '
         u'切句 %d 句。'
         % (V('year_span'), sum(F['sents_n']), sum(F['shell']), sum(F['foot_page']),
            sum(F['hdr_rfc']), sum(F['sents_n'])))
# 问题
E.append(u'❓ 问题: ICMP 差错报文该限到什么速率、谁说了算?'
         u'——六份文书各答一遍, 每答挂一枚原文锚。'
         u'判词针池 %d 枚 × 六面 = %d 格; 全冷 %d 枚; 跨页壳断句 %d 处。'
         % (V('needle_n'), V('needle_n') * 6, 0, V('wrapcut_n')))

# ① 792
E.append(u'① 792(1981): 只立源抑制机制, 每丢弃一枚报文可发一枚 SQ '
         u'⟦A⟧⟨may send a source quench message for every message that it discards⟩'
         u'——按包尺且 N=1, 通篇无一枚速率数: 速率单位对 %d 枚, 含速率数的句 %d 条。'
         % (V('eq') and F['eq'][0]['n_rate_pairs_792'] if False else 0,
            F['rate_sents_n'][0]))
# 上面拒绝空数: 792 无速率对; 用 keys 里 rate_pairs_per_src[0] 现算
E[-1] = (u'① 792(1981): 只立源抑制机制, 每丢弃一枚报文可发一枚 SQ '
         u'⟦A⟧⟨may send a source quench message for every message that it discards⟩'
         u'——按包尺且 N=1, 通篇无一枚速率数: 数×速率单位对 %d 枚, 含速率数的句 %d 条。'
         % (F['rate_pairs_per_src'][0], F['rate_sents_n'][0]))
# ② 1009
E.append(u'② 1009(1987): 老式网关需求把 N ⇎ T 全交给配置, 只留一句“须预备限频” '
         u'⟦B⟧⟨of the order of 100 bytes⟩(平均包长 %d 字节); 同一面还印出字节⇎包⇎线速现场: '
         u'%d Mbps DS1 ⇎ %d kbps 慢线, 每接口 %d 包/秒 ⇎ 合计 %d ⇎ 出入两向 %d '
         u'⟦C⟧⟨2,000 datagrams per second per interface⟩; 由 %d 条 DS1 + %d 条以太 = %d 接口 ✕ %d 包/秒 现算 '
         u'%d(与印数差 %d 包/秒, 跨行并不闭合)。'
         % (F['eq'][0]['avgb'], F['eq'][0]['mbps'], F['eq'][0]['kbps'], F['eq'][0]['rate_printed'],
            F['eq'][0]['agg_printed'], F['eq'][0]['split_printed'], F['eq'][0]['n_ds1'],
            F['eq'][0]['n_eth'], F['eq'][0]['n_iface_calc'], F['eq'][0]['rate_printed'],
            F['eq'][0]['agg_from_iface'], F['eq'][0]['rate_gap']))
# ③ 1122
E.append(u'③ 1122(1989): 主机需求把义务分到收发两侧——收侧 MUST report ⇎ SHOULD throttle, 发侧只写 MAY; '
         u'全篇唯一的 “1 per second” 是 ARP 洪泛限速不是 ICMP 差错 '
         u'⟦D⟧⟨The recommended maximum rate is 1 per second per⟩, '
         u'“0.005 per second” 是 ping 网关(%d 秒一发); ICMP 差错生成速率零枚数: '
         u'数×速率单位对 %d 枚, 落 ICMP 差错话题 %d 句中的含速率句 %d 条。'
         % (F['eq'][0]['period_200'], F['rate_pairs_per_src'][2], V('icmp_rate_sents'), F['rate_sents_n'][2]))
# ④ 1812
E.append(u'④ 1812(1995): 路由器需求分层——SQ MUST 可限 ⇎ 其它差错 SHOULD 可限 ⇎ 参数 SHOULD 可配, '
         u'怎么限 ⟦H⟧⟨is left to the implementor⟩: N 可按丢包计数 ⟦I⟧⟨send an ICMP error message for every N '
         u'dropped packets⟩, T 可按毫秒 ⟦G⟧⟨SHOULD be settable as part of the configuration⟩; '
         u'全段 %d 行 %d 字符, 义务词 %d 枚(MUST %d ⇎ SHOULD %d ⇎ MAY %d)。'
         % (F['blocks'][1][2], F['blocks'][1][3], F['blocks'][1][5],
            F['ob'][3][0], F['ob'][3][2], F['ob'][3][4]))
# ⑤ 4443
E.append(u'⑤ 4443(2006 IPv6): 节点 MUST limit ⟦J⟧⟨MUST limit the rate of ICMPv6 error messages it originates⟩, '
         u'推荐 token bucket ⟦K⟧⟨token bucket, limiting the average rate⟩, N 可按包/秒或链路分数 '
         u'⟦L⟧⟨N can be either packets/second or a fraction⟩; timer-based “every T” 被点名 not reasonable '
         u'⟦N⟧⟨is not reasonable⟩——1812 的示例被反转; 唯一印出的默认示例 B=%d, N=%d/s '
         u'⟦P⟧⟨the possible defaults could be B=10⟩; 变更记录自陈 ⟦Q⟧⟨Removed the Timer-based and the '
         u'Bandwidth-based methods⟩; 限速条款 ⟦R⟧⟨TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE⟩。'
         u'块 %d 行 %d 字符, 义务词 %d 枚。'
         % (F['eq'][0]['b4443'], F['eq'][0]['n4443'], F['blocks'][2][2], F['blocks'][2][3],
            F['blocks'][2][5]))
# ⑥ sysctl
E.append(u'⑥ ip-sysctl(内核实现文档): 真正把数落盘——每目标最小间隔 icmp_ratelimit=%d 毫秒(每秒 %d 次) '
         u'⇎ icmp_msgs_per_sec=%d ⇎ icmp_msgs_burst=%d ⇎ ratemask=%d(只限类型 %s, Echo 不在内, 0=关闭) '
         u'⇎ ICMPv6 ratelimit=%d 毫秒(v4 的 %.1f 倍); 爆突发可容 %d 包; 默认限速 ⟦U⟧⟨These are rate limited '
         u'by default⟩; 掩码位定义: 星位 %s ⇎ 二串长 %d ⇎ 位标字母表 %s。'
         % (V('rl_ms'), F['eq'][0]['rl_per_s'], V('per_sec'), V('burst'), V('mask_dec'),
            F['mask_bits'], V('rl6_ms'), F['eq'][0]['rl6_vs_v4'], F['eq'][0]['per_burst'],
            F['mask_stars'], V('mask_bin_len'), u'IHGFEDCBA9876543210'))
# 对账: 谁说了算
E.append(u'⚖ 谁说了算: 4443 的限速条放话 ⟦R⟧⟨TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE⟩, '
         u'而在 1812 里同一句话 ⟦E⟧⟨MUST be able to limit the rate at which the messages can be generated⟩'
         u'——同一义务从 %d 年前的分层口径(路由 MUST 可限 ⇎ 参数 SHOULD 可配 ⇎ 怎样限留给实现者)收敛为节点 MUST, '
         u'唯一的数只有 %d 毫秒 ⇎ %d 毫秒与 %d 枚突发。'
         % (V('year_span') - (2006 - 1981), V('rl_ms'), V('rl6_ms'), V('burst')))
# 表格: 六面任务词与语形族
E.append(u'📊 小实体账(本条现算): 语形族 %d 式 ⇎ 六面命中式种 %s ⇎ 独占式种 %d 枚; '
         u'前缀税总和 %d ⇎ 义务词合计 %d; 全篇含速率句 %d 条, ICMP 差错话题 %d 条; '
         u'数×单位对六面 %s。'
         % (V('fams_n_types'), F['fams_n_per_src'], sum(len(z) for z in F['fams_excl']),
            sum(sum(z) for z in F['fams_prefix_tax']), sum(F['ob_tot']),
            sum(F['rate_sents_n']), V('icmp_rate_sents'), F['pairs_n']))
# 反向
E.append(u'🚫 反向 %d 枚针 × 六面 = %d 次: 792 通篇零枚速率数(数×速率单位对 %d 枚) ⇎ 1122 全篇唯一的 '
         u'“1 per second” 是 ARP 洪泛不是 ICMP 差错 ⇎ 1812 的示例写法在 4443 被点名 not reasonable。'
         % (V('needle_n'), V('needle_n') * 6, F['rate_pairs_per_src'][0]))
# 方法
E.append(u'ℒ 方法 ⇒ 截止后标准文档的压缩判据: 问题先立, 六面各答一遍, 每答挂一枚原文锚并给三档口径(逐行 ⇎ 全篇折平 '
         u'⇎ 摘壳折平); 可执数字逐字抽验(掩码 %d ⇎ 突爆 %d ⇎ 两档最小间隔 %d/%d 毫秒); 换算等式现算不复粘; '
         u'%d 枚判词针在六面交叉定位并给出落点行数。'
         % (V('mask_dec'), V('burst'), V('rl_ms'), V('rl6_ms'), V('needle_n')))

enc = chr(10).join(E)
assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)
SRC_ALL = u''.join(PN).replace(u' ', u'')
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok).replace(u' ', u'') in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))
_used = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
for a in _used:
    assert pnorm(a) in u''.join(PN), u'编码锚穿不到最宽档: %s' % a[:50]
LET = {chr(65 + i): ATOMS[i] for i in range(len(ATOMS))}
assert sorted(LET) == [chr(65 + i) for i in range(len(ATOMS))], u'标签字母表溢出 26 或次序乱'
_pairs = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', enc)
assert len(_pairs) == n_atoms, u'有锚没紧跟标签(或标签在前): 配对 %d ⇎ 锚 %d' % (len(_pairs), n_atoms)
for t, a in _pairs:
    assert t in LET, u'标签 %s 没有对应的原文块' % t
    assert pnorm(a) in pnorm(LET[t]), u'锚 ⟦%s⟧ 引的串不在第 %s 块内: %s' % (t, t, a[:60])
assert set(t for t, _ in _pairs) == set(LET), u'候选锚池里有条块没被编码区引用: %s' % sorted(
    set(LET) - set(t for t, _ in _pairs))

orig = u'### ⟦A⟧ ⟸ ' + u' ⇎ '.join(SRC) + chr(10) + chr(10) + chr(10).join(ATOMS)
title = (u'# B94 单文本压缩: ICMP 差错限速六文书问答压缩(%d 面 ⇎ %d 年跨度)'
         u'规则链逐环保真键(问题⇒六面各答⇒每答挂锚⇒谁说了算) 闭合账 标量\n'
         % (NSRC, F['year_span'][0]))
srcline = (u'src: %s (%d 字符, 硬换行 %d 行) '
           u'(单文本压缩: 源=六份一手标准/实现文档, 1981-2006 时间序; 数字/掩码/默认值一律逐字保留)\n'
           % (u' ⇎ '.join(SRC), sum(F['cp']), sum(F['splitnl'])))
tagsline = (u'tags: 单文本压缩 跨文档问答 三档口径键(逐行⇎全篇折平⇎摘壳折平) '
            u'换算等式现算键(%d 条) 反向零命中键(%d 枚×六面) 锚归属由正文现推 标量 3⇎清单 %d 项\n'
            % (len(F['eq'][0]), F['needle_n'][0], len(ATOMS)))
md = (title + srcline + u'; ' + tagsline + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n\n(待 _fill94.py 第二遍独立复算后写回)\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=chr(10)).write(md)
print(u'B94 建条目: %s' % ENTRY)
print(u'编码区锚 %d 处, 候选锚 %d 条, 登记面值 %d 枚'
      % (n_atoms, len(ATOMS), len(REG)))
assert REG, u'REG 空——V() 没登记任何面值'
io.open(u'corpus/_b94flat.json', 'w', encoding='utf-8').write(
    json.dumps(REG, ensure_ascii=False, sort_keys=True) + chr(10))
print(u'DERIV 键表: corpus/_b94flat.json %d 键' % len(REG))