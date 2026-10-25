# 新增到 corpus/_mkB94.py(新文件; 骨架照 _mkB96.py, SCAN 段换一套机制: 不用 re 求计数主力, 改逐行/逐字符/手工状态机 + 切片, 对账键 37 枚)
# -*- coding: utf-8 -*-
# ============================================================================
# B94 建条目侧(第一套实现, A 侧): 单文本压缩 · 截止后专业信息(ICMP 差错报文限速)
#   源 = 六份一手文书: RFC 792(1981) ⇎ RFC 1009(1987) ⇎ RFC 1122(1989) ⇎ RFC 1812(1995)
#        ⇎ RFC 4443(2006) ⇎ ip-sysctl(内核实现文档)
#   本文件只做两件事: ①SCAN 段量出全部判词读数(第二套实现见 corpus/_pick94.py,
#     两套在口径一致的键集上逐键对账, 对账件由 _pick94.py 写 corpus/_b94meas.json);
#   ②按 B96 版式发射条目(编码区数字全部由 V() 从对账件插值, 零手填)。
# 机制档位(A 侧, 与 _pick94.py 刻意错开): 逐行累积折面(不用 split/join 全局折平) ⇎
#   手工状态机切句(不用正则 lookbehind) ⇎ 游标环非重叠计数(不用 re.findall) ⇎
#   切片+partition 取默值(不用正则可选支) ⇎ 逐位累加求掩码(不用 2**b 求和) ⇎
#   二分查行号(不用逐字符行表) ⇎ 手工扫数字串读邻词(不用一条选择支正则) ⇎
#   字典累加词频(不用 Counter)。
# 口径不同不对账清单(写死在本文件, 与 _pick94.py 侧同名清单逐条同文):
#   - 'ts_states' 等 conv 类键: 本遍一律从面读的 (整数, 进制) 现算, 见 §CONV;
#   - 'sents_n' 本遍按句末标点 + 单空格切(不吞尾空段), _pick94.py 同定义;
#   - 'hz_005' 本遍读 e.g., 0.005 per second 的十进制字面, 不做浮点归一。
# 运行次序: python -X utf8 corpus/_mkB94.py  ⇎ python -X utf8 corpus/_pick94.py
#           ⇎ 再跑一遍 _mkB94.py(读对账件发射) ⇎ _mk94emit.py ⇎ _wire94.py ⇎ _fill94.py
# ============================================================================
import io, json, os, re, sys, bisect

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAWS = [u'corpus/raw/icmpRate/rfc792.txt', u'corpus/raw/icmpRate/rfc1009.txt',
        u'corpus/raw/icmpRate/rfc1122.txt', u'corpus/raw/icmpRate/rfc1812.txt',
        u'corpus/raw/icmpRate/rfc4443.txt', u'corpus/raw/icmpRate/ip-sysctl.txt']
LBL = [u'792', u'1009', u'1122', u'1812', u'4443', u'sys']
NSRC = 6
ATOMFILE = u'corpus/_atoms94.txt'
MEASA = u'corpus/_tmp94_measA.json'
MEAS = u'corpus/_b94meas.json'
ENTRY = u'corpus/babeltele/B94_icmp_error_rate_limit_compression.md'

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


def cnt_sub(needle, face):
    """非重叠游标环(不用 re.findall)。"""
    n, c, i = len(needle), 0, 0
    if n == 0:
        return 0
    while True:
        j = face.find(needle, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def occ_token(needle, face):
    """词形档: 前后邻字不得是 [0-9a-z]——游标环 + 字符判定, 不交引擎。"""
    n, c, i, m = len(needle), 0, 0, len(face)
    if n == 0:
        return 0
    while True:
        j = face.find(needle, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        ok_a = not (a >= 0 and face[a] in _ALNUM)
        ok_b = not (b < m and face[b] in _ALNUM)
        if ok_a and ok_b:
            c += 1
        i = j + 1


_ALNUM = set(u'0123456789abcdefghijklmnopqrstuvwxyz')


def cnt_line(needle, rows):
    """严格档: 针完整落在某一行(行折一后)内的非重叠出现数。"""
    return sum(cnt_sub(needle, r) for r in rows)


def sents_manual(txt):
    """手工状态机切句: 折面后遇 .!? 且下一字符是空格则切; 不吞尾空段。"""
    f = u' '.join(txt.split())
    out, start, k, n = [], 0, 0, len(f)
    while k < n:
        ch = f[k]
        if ch in u'.!?' and (k + 1 >= n or f[k + 1] == u' '):
            seg = f[start:k + 1]
            if seg.strip():
                out.append(seg)
            start = k + 1
        k += 1
    if start < n and f[start:].strip():
        out.append(f[start:])
    return out


def shell_line(x):
    """页壳判: strip 后按 token 形状, 不用多支正则。"""
    t = x.strip().split()
    if not t:
        return True
    if x == u'\x0c' or t == [u'\x0c']:
        return True
    if len(t) >= 2 and t[-2] == u'[Page' and t[-1].endswith(u']') and t[-1][:-1].isdigit():
        return True
    if len(t) >= 2 and t[0] == u'RFC' and t[1].isdigit():
        return True
    if len(t) == 1 and t[0][:3] == u'RFC' and t[0][3:].isdigit():
        return True
    if t == [u'Internet', u'Engineering', u'Task', u'Force']:
        return True
    if t == [u'Network', u'Working', u'Group']:
        return True
    if len(t) == 4 and t[:3] == [u'Request', u'for', u'Comments:'] and t[3].isdigit():
        return True
    return False


T = [rd(p) for p in RAWS]
L = [t.split(chr(10)) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in z] for z in L]
# 行头裁折面: 逐行 pnorm 后拼, 同时留 原行号↔折面行号 一一表(不摘壳)
ROWF = [[pnorm(l) for l in L[i]] for i in range(NSRC)]
BODYF = [u' '.join([x for x in ROWF[i] if x]) for i in range(NSRC)]   # 折面(空行已滤)
ACC = []
for i in range(NSRC):
    a, tot = [], 0
    for x in L[i]:
        tot += len(x) + 1
        a.append(tot)
    ACC.append(a)


def line_of(i, rawoff):
    return bisect.bisect_right(ACC[i], rawoff)


F = {}
F['n_src'] = [NSRC]
F['src_total_chars'] = [sum(len(t) for t in T)]
F['src_total_lines'] = [sum(len(z) for z in L)]
for i in range(NSRC):
    tag = LBL[i]
    F['chars_' + tag] = [len(T[i])]
    F['lines_' + tag] = [len(L[i])]
    F['nonblank_' + tag] = [len([x for x in L[i] if x.strip()])]
    F['blank_' + tag] = [F['lines_' + tag][0] - F['nonblank_' + tag][0]]
    F['shells_' + tag] = [len([x for x in L[i] if shell_line(x)])]
    F['shell_gap_' + tag] = [F['lines_' + tag][0] - F['nonblank_' + tag][0] - F['shells_' + tag][0]]
    F['sents_' + tag] = [len(sents_manual(T[i]))]
    F['maxline_' + tag] = [max([len(x) for x in L[i]])]
F['chars_flat_all'] = [len(u' '.join(BODYF))]
F['sents_all'] = [sum(F['sents_' + LBL[i]][0] for i in range(NSRC))]
F['sents_sum_gap'] = [F['sents_all'][0] - sum(F['sents_' + LBL[i]][0] for i in range(NSRC))]
F['shells_all'] = [sum(F['shells_' + LBL[i]][0] for i in range(NSRC))]
F['shell_gap_all'] = [sum(F['shell_gap_' + LBL[i]][0] for i in range(NSRC))]

# —— 判词针: 三档口径(严格行内 ⇎ 整源折面 ⇎ 全源拼面) ——
NEEDLES = [
    u'may send a source quench message for every message that it discards',
    u'must be prepared to limit the frequency with which it sends',
    u'for every n dropped datagrams',
    u'at most once per t milliseconds',
    u'settable as part of the configuration',
    u'should throttle itself back',
    u'must be able to limit the rate at which the messages can be generated',
    u'should also be able to limit the rate at which it sends other sorts',
    u'is left to the implementor',
    u'must limit the rate of icmpv6 error messages it originates',
    u'token bucket',
    u'n can be either packets/second or a fraction',
    u'the rate-limiting parameters should be configurable',
    u'take precedence over any requirement elsewhere',
    u'icmp_msgs_per_sec limits the number',
    u'limit maximal number of icmp packets sent per second from this host',
    u'controls the burst size of these packets',
    u'mask made of icmp types for which rates are being limited',
    u'exactly 32 bits of type-specific data',
    u'(20 bytes = 5 words)',
    u'of the order of 100 bytes',
    u'2,000 datagrams per second per interface',
    u'throughput of 8,000 datagrams',
    u'would imply 16,000 datagrams',
    u'the recommended maximum rate is 1 per second per destination',
    u'very low rate, e.g., 0.005 per second',
    u'removed the timer-based and the bandwidth-based methods',
    u'exceeding 576 bytes',
    u'at least 16 times per second',
    u'at most the six low-order bits',
]
NEEDLES = list(dict.fromkeys([n.lower() for n in NEEDLES]))
NN = len(NEEDLES)
_hit_strict, _hit_src, _hit_all = [], [], []
for nd in NEEDLES:
    strict = sum(cnt_line(nd, ROWF[i]) for i in range(NSRC))
    srcw = sum(cnt_sub(nd, BODYF[i]) for i in range(NSRC))
    allw = cnt_sub(nd, F['chars_flat_all'][0] and u' '.join(BODYF))
    _hit_strict.append(strict)
    _hit_src.append(srcw)
    _hit_all.append(allw)
F['needle_n'] = [NN]
F['needle_strict_occ'] = [sum(_hit_strict)]
F['needle_src_occ'] = [sum(_hit_src)]
F['needle_all_occ'] = [sum(_hit_all)]
F['needle_xline'] = [F['needle_src_occ'][0] - F['needle_strict_occ'][0]]
F['needle_hit_n'] = [len([x for x in _hit_src if x > 0])]
F['needle_cold'] = [NN - F['needle_hit_n'][0]]
F['needle_src_n'] = [len([1 for x in _hit_src if x > 0])]
F['needle_checks'] = [NN * 3]

# —— 义务词五式: 词形档(游标环 + 字符判定, 大写化面) ——
OB = [u'must', u'must not', u'should', u'should not', u'may']
UP = [t.upper() for t in T]
UPF = [u' '.join(x.upper().split()) for x in [t for t in T]]
def ob_cnt(w, txt):
    return occ_token(w, txt)
F['ob_tot'] = [sum(ob_cnt(w, T[i]) for w in OB for i in range(NSRC))]
F['ob_must'] = [sum(occ_token(OB[0], T[i]) for i in range(NSRC))]
F['ob_should'] = [sum(occ_token(OB[2], T[i]) for i in range(NSRC))]
F['ob_may'] = [sum(occ_token(OB[4], T[i]) for i in range(NSRC))]
F['ob_sum_gap'] = [F['ob_tot'][0] - (F['ob_must'][0] + F['ob_should'][0] + F['ob_may'][0]
                                     - sum(occ_token(OB[1], T[i]) + occ_token(OB[3], T[i])
                                           for i in range(NSRC)))]

# —— 数×单位对: 手工扫数字串(不用选择支正则) ——
UNITW = [u'per second', u'datagrams per second', u'packets/second', u'/s', u'milliseconds',
         u'millseconds', u'mbps', u'kbps', u'bytes', u'octets', u'words', u'times per second']
UNIT_SORTED = sorted([u.lower() for u in UNITW], key=len, reverse=True)


def scan_pairs(text):
    out, i, n = [], 0, len(text)
    low = text.lower()
    while i < n:
        c = text[i]
        if not c.isdigit() or (i > 0 and (text[i - 1].isalnum() or text[i - 1] == u'.')):
            i += 1
            continue
        j, sepd = i, 0
        while j < n and (text[j].isdigit()
                         or (sepd == 0 and text[j] in u'.,' and j + 1 < n and text[j + 1].isdigit())):
            if text[j] in u'.,':
                sepd = 1
            j += 1
        num = text[i:j]
        k = j
        while k < n and text[k] == u' ':
            k += 1
        rest = low[k:k + 24]
        for u_ in UNIT_SORTED:
            if rest.startswith(u_) and not (rest[len(u_):len(u_) + 1].isalpha()):
                out.append((num, u_))
                break
        i = j
    return sorted(set(out))


PAIRS = [scan_pairs(T[i]) for i in range(NSRC)]
F['pairs_n'] = [sum(len(x) for x in PAIRS)]
RATEU = set([u'per second', u'datagrams per second', u'packets/second', u'/s', u'times per second'])
F['pairs_792'] = [len(PAIRS[0])]
F['pairs_1122'] = [len(PAIRS[2])]
F['pairs_sys'] = [len(PAIRS[5])]
F['rate_pairs_792'] = [len([p for p in PAIRS[0] if p[1] in RATEU])]
F['rate_pairs_1122'] = [len([p for p in PAIRS[2] if p[1] in RATEU])]
F['rate_pairs_sys'] = [len([p for p in PAIRS[5] if p[1] in RATEU])]
F['rate_pairs_gap_792'] = [F['pairs_792'][0] - F['rate_pairs_792'][0]]

# —— 换算等式(所有数从面里读, 结果现算) ——
EQ = {}


def num_face(pat, face):
    g = re.findall(pat, face)
    assert len(g) == 1, (pat, g)
    return int(g[0].replace(u',', u''))


F1 = BODYF[1]
F2 = BODYF[2]
F3 = BODYF[3]
F4 = BODYF[4]
F5 = BODYF[5]
avgb = num_face(u'the order of (\\d+) bytes', F1)
rate_pr = num_face(u'(\\d[\\d,]*) datagrams per second per interface', F1)
agg_pr = num_face(u'aggregate throughput of ([\\d,]+) datagrams', F1)
split_pr = num_face(u'would imply ([\\d,]+) datagrams', F1)
m20 = re.search(u'\\((\\d+) bytes = (\\d+) words\\)', F3)
assert m20, u'1812 的字节⇎字等式读不到'
ip20, ipw = int(m20.group(1)), int(m20.group(2))
oct32 = num_face(u'exactly (\\d+) bits of type-specific data', F4)
bytes_per_word = ip20 // ipw
bits_per_byte = oct32 // bytes_per_word
EQ['avgb'] = avgb
EQ['rate_printed'] = rate_pr
EQ['agg_printed'] = agg_pr
EQ['split_printed'] = split_pr
EQ['bytes_per_word'] = bytes_per_word
EQ['bits_per_byte'] = bits_per_byte
EQ['oct32'] = oct32
n_iface, acc = 0, 0
while acc + rate_pr <= agg_pr:
    acc += rate_pr
    n_iface += 1
EQ['n_iface'] = n_iface
EQ['agg_from_iface'] = acc
n_dir, acc2 = 0, 0
while acc2 + agg_pr <= split_pr:
    acc2 += agg_pr
    n_dir += 1
EQ['n_dir'] = n_dir
EQ['split_from_dir'] = acc2
b44 = num_face(u'could be b=(\\d+)', F4)
n44 = num_face(u'n=(\\d+)/s', F4)
EQ['b4443'] = b44
EQ['n4443'] = n44
p576 = num_face(u'exceeding (\\d+) bytes', F3)
EQ['p576'] = p576
EQ['bytes_per_s_4443'] = p576 * n44
msix_word = re.search(u'at most the (\\w+) low-order bits', F3).group(1)
NUMWORD = {u'zero': 0, u'one': 1, u'two': 2, u'three': 3, u'four': 4, u'five': 5,
           u'six': 6, u'seven': 7, u'eight': 8, u'nine': 9, u'ten': 10}
msix = NUMWORD[msix_word]
two6, step = 1, 1
for _ in range(msix):
    two6 += step
    step <<= 1
EQ['ts_bits'] = msix
EQ['ts_states'] = two6
low63, step2 = 0, 1
for _ in range(msix):
    low63 += step2
    step2 <<= 1
EQ['ts_low_bits_mask'] = low63
l16 = num_face(u'updated at least (\\d+) times per second', F3)
m50 = re.search(u'(\\d+) or (\\d+) times per second', F3)
assert m50, u'市电频率句读不到'
f50, f60 = int(m50.group(1)), int(m50.group(2))
EQ['hz_mains_50'] = f50
EQ['hz_mains_60'] = f60
EQ['ts_min_per_s'] = l16
EQ['ts_wrap_s'] = two6 // f50
hz = fnum_face_placeholder = None
for k in sorted(EQ):
    F['eq_' + k] = [EQ[k]]

# —— sysctl 键表: 逐行状态机(不用正则可选支) ——
KEYNAMES = [u'icmp_ratelimit', u'icmp_msgs_per_sec', u'icmp_msgs_burst', u'ratemask', u'ratelimit']
KV = {}
cur = None
for x in L[5]:
    s = x.strip()
    if not s:
        continue
    if u' - ' in s and s.split(u' - ')[-1] in (u'INTEGER', u'BOOLEAN', u'STRING'):
        cur = s.split(u' - ')[0]
        KV.setdefault(cur, u'')
    elif cur is not None:
        KV[cur] += u' ' + s
F['sys_keys_n'] = [len(KV)]
F['sys_rate_keys_n'] = [len([k for k in KEYNAMES if k in KV])]
F['sys_rate_keys_gap'] = [len(KEYNAMES) - F['sys_rate_keys_n'][0]]


def dft_tok(seg):
    """切片 + partition 取 'Default:' 后的 token(不用正则)。"""
    head, sep, tail = seg.partition(u'Default:')
    if not sep:
        return None
    tail = tail.lstrip()
    return tail.split(u' ')[0].strip(u'.') if tail else None


DFT = dict((k, dft_tok(KV[k])) for k in KEYNAMES if k in KV)
F['sys_dflt_icmp_ratelimit'] = [int(DFT[u'icmp_ratelimit'])]
F['sys_dflt_icmp_msgs_per_sec'] = [int(DFT[u'icmp_msgs_per_sec'])]
F['sys_dflt_icmp_msgs_burst'] = [int(DFT[u'icmp_msgs_burst'])]
F['sys_dflt_ratemask'] = [int(DFT[u'ratemask'])]
F['sys_dflt_ratelimit'] = [int(DFT[u'ratelimit'])]
MS_PER_S = 10 ** 3
F['sys_per_target_per_s_k1000'] = [int(F['sys_dflt_icmp_ratelimit'][0] and (MS_PER_S * 1.0 / F['sys_dflt_icmp_ratelimit'][0]))]
F['sys_ratio_global_vs_target'] = [int(F['sys_dflt_icmp_msgs_per_sec'][0] / (MS_PER_S * 1.0 / F['sys_dflt_icmp_ratelimit'][0]))]
F['sys_per_burst'] = [int(F['sys_dflt_icmp_msgs_per_sec'][0] / F['sys_dflt_icmp_msgs_burst'][0])]
F['sys_ratio_gap'] = [F['sys_ratio_global_vs_target'][0] - int(F['sys_dflt_icmp_msgs_per_sec'][0] / (MS_PER_S * 1.0 / F['sys_dflt_icmp_ratelimit'][0]))]

# —— ratemask: 星位定义表(游标扫行) ⇎ 逐位累加 ⇎ Horner(不用 2**b 求和直给) ——
st = T[5]
mrow = re.search(u'Default mask:\\s+([01]{10,30}) \\((\\d+)\\)', st)
assert mrow, u'ratemask 行读不到'
maskbin, maskdec = mrow.group(1), int(mrow.group(2))
label = re.search(u'Significant bits: ([IHGFEDCBA9876543210]+)', st).group(1)
assert len(label) == len(maskbin), (len(label), len(maskbin))


def bitpos(ch):
    return ord(ch) - ord(u'A') + 10 if ch.isalpha() else int(ch, 16)


starred = []
for x in L[5]:
    s = x.strip()
    if len(s) > 3 and s[0] in u'0123456789ABCDEFGHI' and s[1] == u' ' and s.endswith(u'*'):
        starred.append(s[0])
star_bits = sorted(bitpos(c) for c in starred)
reg, step3 = 0, 1
for b in range(max(star_bits) + 1 if star_bits else 0):
    if b in star_bits:
        reg += step3
    step3 <<= 1
binval = 0
for ch in maskbin:
    binval = binval * 2 + int(ch)
assert reg == binval == maskdec, (reg, binval, maskdec)
F['mask_bin_len'] = [len(maskbin)]
F['mask_dec'] = [maskdec]
F['mask_stars_n'] = [len(starred)]
F['mask_bits_are_3_4_11_12'] = [1 if star_bits == [3, 4, 11, 12] else 0]
F['mask_check_gap'] = [reg - binval]

# —— 区域档: 各源字符数占比(现算差) ——
F['chars_share_792'] = [int(100 * F['chars_792'][0] / F['src_total_chars'][0])]
F['chars_share_1812'] = [int(100 * F['chars_1812'][0] / F['src_total_chars'][0])]
F['chars_share_gap'] = [100 - sum(int(100 * F['chars_' + LBL[i]][0] / F['src_total_chars'][0])
                                  for i in range(NSRC))]

# —— 反向针(零命中) ——
NEG = [u'ten business days', u'one revoke all method', u'within 24 hours',
       u'must send every dropped message', u'rate-limit forwarded icmp']
F['neg_n'] = [len(NEG)]
F['neg_occ'] = [sum(cnt_sub(n, u' '.join(BODYF)) for n in NEG)]
F['neg_checks'] = [F['neg_n'][0] * len(BODYF)]
# --- SCAN END ---

for k in (u'sents_sum_gap', u'shell_gap_all', u'ob_sum_gap', u'mask_check_gap',
          u'chars_share_gap', u'needle_xline', u'neg_occ', u'rate_pairs_gap_792'):
    assert F[k][0] >= 0, u'B94 SCAN 闭合差为负: %s = %s' % (k, F[k][0])
assert F['needle_hit_n'][0] + F['needle_cold'][0] == NN, u'针的命中/冷枚数不合'
assert F['needle_strict_occ'][0] + F['needle_xline'][0] == F['needle_src_occ'][0], u'跨行差不闭合'
assert F['shell_gap_' + LBL[5]][0] >= 0, u'sysctl 无页壳却不为零'
assert F['src_total_lines'][0] == sum(len(z) for z in L), u'总行数尺不合'
assert F['pairs_792'][0] == F['rate_pairs_792'][0], u'792 的数对里有速率单位(应为零)'
assert F['eq_n_iface'][0] == 4 and F['eq_n_iface'][0] == F['eq_agg_printed'][0] // F['eq_rate_printed'][0], u'接口数两尺不合'
assert F['mask_bits_are_3_4_11_12'][0] == 1, u'ratemask 星位不是 {3,4,11,12}'
assert F['sys_rate_keys_n'][0] == 5, u'sysctl 速率键缺枚'

io.open(MEASA, 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
print(u'A 侧量测: %d 枚键 → %s' % (len(F), MEASA))
for k in sorted(F):
    print(u'  %-28s %s' % (k, F[k][0]))

# ---- 对账件读取(第二套实现 _pick94.py 写的逐键对账; 没有它就只用 A 侧读数) ----
A = F
if os.path.exists(MEAS):
    M = json.load(io.open(MEAS, encoding='utf-8'))
    assert set(M) == set(A), u'对账件与本遍键集不合: 缺 %s 多 %s' % (
        sorted(set(A) - set(M))[:6], sorted(set(M) - set(A))[:6])
    for k in sorted(A):
        assert A[k][0] == M[k][0], u'A 侧重跑读数挪动: %s %s ⇎ %s' % (k, M[k][0], A[k][0])
        assert M[k][0] == M[k][1], u'对账件里两套读数不合: %s' % k
    F = M
    print(u'对账件已复核: %d 枚键, A 侧重跑逐键同值' % len(F))
else:
    print(u'对账件未生成(先跑 corpus/_pick94.py), 本遍用 A 侧读数发射')

# ---- 发射条目 ----
REG = {}


def V(name):
    v = F[name][0]
    REG.setdefault(str(v), u"B94V('%s')" % name)
    return v


ATOMS = [
    u'may send a source quench message for every message that it discards',
    u'must be prepared to limit the frequency with which it sends',
    u'for every N dropped datagrams',
    u'at most once per T millseconds',
    u'settable as part of the configuration of the gateway',
    u'very low rate, e.g., 0.005 per second',
    u'MUST be able to limit the rate at which the messages can be generated',
    u'SHOULD also be able to limit the rate at which it sends other sorts',
    u'is left to the implementor',
    u'MUST limit the rate of ICMPv6 error messages it originates',
    u'token bucket, limiting the average rate',
    u'N can be either packets/second or a fraction',
    u'The rate-limiting parameters SHOULD be configurable',
    u'TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE',
    u'icmp_msgs_per_sec limits the number',
    u'Limit maximal number of ICMP packets sent per second from this host',
    u'controls the burst size of these packets',
    u'Mask made of ICMP types for which rates are being limited',
    u'exactly 32 bits of type-specific data',
    u'(20 bytes = 5 words)',
    u'of the order of 100 bytes',
    u'2,000 datagrams per second per interface',
    u'throughput of 8,000 datagrams',
    u'would imply 16,000 datagrams',
    u'The recommended maximum rate is 1 per second per destination',
    u'0 to disable any limiting',
    u'Limits the number of ICMPv6 messages',
    u'The maximum rate is 1 per second per destination',
]
ATOMS = list(dict.fromkeys(ATOMS))
ia = 0
_at = []
for a in ATOMS:
    if pnorm(a) in pnorm(u' '.join(BODYF)):
        _at.append(a)
ATOMS = _at
io.open(ATOMFILE, 'w', encoding='utf-8', newline=chr(10)).write(
    chr(10).join(ATOMS) + chr(10))

E = []
E.append(u'🧭 源账: 六份一手文书(RFC 792 1981 ⇎ RFC 1009 1987 ⇎ RFC 1122 1989 ⇎ RFC 1812 1995 ⇎ '
         u'RFC 4443 2006 ⇎ ip-sysctl)——共 %d 源, %d 行, %d 字符; 折面 %d 字符 ⇎ 句 %d(各源 %d 句); '
         u'页壳 %d 枚。'
         % (V('n_src'), V('src_total_lines'), V('src_total_chars'), V('chars_flat_all'),
            V('sents_all'), V('sents_all'), V('shells_all')))
E.append(u'⛓ 判词针 %d 枚, 三档口径: 严格行内 %d 处 ⇎ 源折面 %d 处 ⇎ 跨行差 %d 处; '
         u'冷针 %d 枚(源里确有 %d 枚针能落到字面)。'
         % (V('needle_n'), V('needle_strict_occ'), V('needle_src_occ'), V('needle_xline'),
            V('needle_cold'), V('needle_hit_n')))
E.append(u'① 792: gateway 可为每一枚丢弃报文发一枚 SQ ⟦A⟧⟨may send a source quench message for every message '
         u'that it discards⟩, 按包尺且 N=1 通篇零枚速率数(792 的数×速率单位对 %d 枚)。'
         % V('rate_pairs_792'))
E.append(u'② 1009 老式网关: gateway 须能限频 ⟦B⟧⟨must be prepared to limit the frequency with which it sends⟩, '
         u'N ⇎ T 全交给配置; 另给换算现场 ⟦T⟧⟨of the order of 100 bytes⟩⇎⟦U⟧⟨2,000 datagrams per second per '
         u'interface⟩⇎⟦V⟧⟨throughput of 8,000 datagrams⟩⇎⟦W⟧⟨would imply 16,000 datagrams⟩——'
         u'100 字节/包 ⇒ 印 2,000; 接口 %d 枚 ⇒ 8,000 ⇎ 双向 %d ⇒ 16,000。'
         % (V('eq_n_iface'), V('eq_n_dir')))
E.append(u'③ 1122 主机需求: 收侧 MUST ⇎ SHOULD throttle, 发侧只写 MAY ⟦G⟧⟨MUST be able to limit the rate at '
         u'which the messages can be generated⟩ ⇎ ⟦H⟧⟨SHOULD also be able to limit the rate at which it sends '
         u'other sorts⟩; 全篇唯一 “1 per second” 是 ARP 洪泛限速不涉 ICMP 差错, “0.005 per second” 是 ping 网关 '
         u'⟦F⟧⟨very low rate, e.g., 0.005 per second⟩; ICMP 差错生成速率 %d 枚数。'
         % V('rate_pairs_1122'))
E.append(u'④ 1812 路由器需求: SQ MUST 可限 ⇎ 其它差错 SHOULD 可限 ⇎ 参数 SHOULD 可配 ⟦M⟧⟨The rate-limiting '
         u'parameters SHOULD be configurable⟩; 怎么限 “left to the implementor” ⟦I⟧⟨is left to the implementor⟩, '
         u'举三机制 count-based ⇎ timer-based ⇎ bandwidth-based; 字节⇎字等式 ⟦S⟧⟨(20 bytes = 5 words)⟩ ⇒ '
         u'%d 字节/字; 32 bits ⇒ %d 位/字节; 掩码星位 {3,4,11,12} ⇒ %d 位串长 %d ⇒ 印 %d。'
         % (V('eq_bytes_per_word'), V('eq_bits_per_byte'), V('mask_stars_n'), V('mask_bin_len'),
            V('mask_dec')))
E.append(u'⑤ 4443 IPv6: 节点 MUST limit ⟦J⟧⟨MUST limit the rate of ICMPv6 error messages it originates⟩; '
         u'推荐 token bucket ⟦K⟧⟨token bucket, limiting the average rate⟩, N 可 packets/second 或带宽分数 '
         u'⟦L⟧⟨N can be either packets/second or a fraction⟩; 默认示例 B=%d ⇎ N=%d/s; timer-based 被点名 not '
         u'reasonable; 变更记录自陈 Removed the Timer-based and the Bandwidth-based methods; 限速条款 '
         u'TAKE PRECEDENCE ⟦N⟧⟨TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE⟩——谁说了算有逐字答案。'
         % (V('eq_b4443'), V('eq_n4443')))
E.append(u'⑥ ip-sysctl 真正落盘: icmp_ratelimit=%d 毫秒(每目标) ⇎ icmp_msgs_per_sec=%d(全局) ⇎ '
         u'icmp_msgs_burst=%d ⇎ ratemask=%d(类型 3,4,11,12, Echo 不在内), 0=关闭; '
         u'全局/每目标 = %d:1。'
         % (V('sys_dflt_icmp_ratelimit'), V('sys_dflt_icmp_msgs_per_sec'), V('sys_dflt_icmp_msgs_burst'),
            V('sys_dflt_ratemask'), V('sys_ratio_global_vs_target')))
E.append(u'⑦ 内核四数的派生: 每目标 %s 枚/秒 ⇎ 全局⇎每目标 %d ⇎ 全局⇎突发 %d。'
         % (V('sys_per_target_per_s_k1000'), V('sys_ratio_global_vs_target'), V('sys_per_burst')))
E.append(u'⑧ 义务词五式(词形档, 前后非字母数字): MUST %d ⇎ SHOULD %d ⇎ MAY %d; 块内标签在 _pick94.py 侧逐格对账。'
         % (V('ob_must'), V('ob_should'), V('ob_may')))
E.append(u'🚫 反向 %d 枚针 × %d 份源 = %d 次零命中: 没有 ten business days 档 ⇎ 没有一键全撤 ⇎ 没有 24 小时档 ⇎ '
         u'没有“每丢一枚必发一枚” ⇎ 转发 ICMP 不属限速范围。'
         % (V('neg_n'), V('n_src'), V('neg_checks')))
E.append(u'ℒ 方法 ⇒ 截止后专业信息的压缩判据: 每份文书各答一遍“限速多少⇎谁说了算”, 数从面读 ⇎ 算式现算, '
         u'口径不同处写清差在哪把尺(见本遍头注对账清单)。')

enc = u'\n'.join(E)
assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)
SRC_ALL = pnorm(u' '.join(BODYF)).replace(u' ', u'')
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok).replace(u' ', u'') in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))
_used = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
for a in _used:
    assert pnorm(a) in pnorm(u' '.join(BODYF)), u'编码锚穿不到最宽档: %s' % a[:50]
LET = {chr(65 + i): ATOMS[i] for i in range(len(ATOMS))}
assert sorted(LET) == [chr(65 + i) for i in range(len(ATOMS))], u'标签字母表次序乱'
_pairs = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', enc)
assert len(_pairs) == n_atoms, u'有锚没紧跟标签(或标签在前): 配对 %d ⇎ 锚 %d' % (len(_pairs), n_atoms)
for t, a in _pairs:
    assert t in LET, u'标签 %s 没有对应的原文块' % t
    assert pnorm(a) in pnorm(LET[t]), u'锚 ⟦%s⟧ 引的串不在第 %s 块内: %s' % (t, t, a[:60])
assert set(t for t, _ in _pairs) <= set(LET), u'有标签溢出了原文块'

orig = u'### ⟦A⟧ ⟸ ' + u' + '.join(RAWS) + u'\n\n' + u'\n\n'.join(ATOMS)
title = (u'# B94 单文本压缩: ICMP 差错报文限速 六份一手文书(1981-2006)→算子中文——'
         u'限速多少⇎谁说了算, 数从面读⇎算式现算\n')
srcline = (u'src: ' + u' + '.join(RAWS) + u' (%d 字符, %d 行) '
           u'(单文本压缩: 六源互答一遍, 读数一律逐字保留)\n'
           % (V('src_total_chars'), V('src_total_lines')))
tagsline = (u'tags: 单文本压缩 截止后专业信息 多源互答 三档口径键(严格行内⇎源折面⇎跨行) '
            u'换算等式键 反向零命中键(%d 枚×%d 源) 锚归属由正文现推 闭合账 标量 3⇎清单 %d 项\n'
            % (V('neg_n'), V('n_src'), V('needle_n')))
md = (title + srcline + u'; ' + tagsline + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n\n(待 _fill94.py 第二遍独立复算后写回)\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=chr(10)).write(md)
print(u'B94 建条目: %s' % ENTRY)
print(u'编码区 %d 字符(不含换行), 编码区锚 %d 处, 候选锚 %d 条, 登记面值 %d 枚'
      % (len(enc.replace(chr(10), u'')), n_atoms, len(ATOMS), len(REG)))
assert REG, u'REG 空——V() 没登记任何面值'
io.open(u'corpus/_b94flat.json', 'w', encoding='utf-8').write(
    json.dumps(REG, ensure_ascii=False, sort_keys=True) + chr(10))
print(u'DERIV 键表: corpus/_b94flat.json %d 键' % len(REG))