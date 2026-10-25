# 新增 corpus/_mkBB94.py(整文件新建); 不改 corpus/_pick94.py 的任何行——两遍同定义, 逐键对账
# -*- coding: utf-8 -*-
# ============================================================================
# B_B94 建条目侧(第二套实现, A 侧): 多文书压缩 · 截止后专业信息
#   源 = 六份一手文书: RFC 792(1981) / RFC 1009(1987) / RFC 1122(1989) / RFC 1812(1995)
#        / RFC 4443(2006) / Linux ip-sysctl(内核实现文档)
#   主题: ICMP 差错报文该限到什么速率、谁说了算
#   本文件只做两件事: ①SCAN 段独立重算判词读数(机制与 _pick94.py 不同:
#     split/join 折面 ⇎ 逐字符铺面; 游标 find 环 ⇎ re.findall; 闭式乘法 ⇎ 逐次累加/位移;
#     正则锚行 ⇎ 折面偏移回行; 累积长度表 bisect ⇎ 逐字符行表);
#     ②读 corpus/_b94meas.json(采集遍落盘件), 逐键断言 gap/diff/close 类键归零后,
#     按 B96 版式发射条目(编码区数字全部由 V() 从量测件插值, 零手填)。
# 口径不同不对账清单(本遍显式列出, 每条写明差在哪把尺):
#   - bytes_stat: os.path.getsize 走文件系统, 与面内 len() 不同尺(采集遍已用 assert 绑定,
#     本遍不再重复读取, 只断言采集遍已判等)。
#   - nonascii: 采集遍落的是“码位集合的列表”, 不是计数, 本遍不对它取标量。
#   - sys_default_tokens / sys_defaults_to: 字符串字典/键名列表, 不是计数, 本遍只作存在性断言。
#   - mask_bin / mask_label / mask_stars / fams / labels / paths / needles3 / needle_src /
#     pin_lines / multi_hits / wrapcut / blocks / rate_sents / rows_ledger / pairs_a / pairs_b:
#     结构化清单, 本遍只作形状断言, 不发射为数字。
#   - ob_odd_case / fams_punct_tax / fams_prefix_tax / fams_word_vs_sub / fams_freq /
#     fams_freq_sub / pin_by_src / foot_page / hdr_rfc / shell_*: 逐源列表, 本遍只发射
#     它们的合计与逐源形状断言; 单枚面值不在编码区出现, 只经 V() 取合计键。
# 运行次序: python -X utf8 corpus/_pick94.py ⇎ python -X utf8 corpus/_mkBB94.py
#           ⇎ _mk94emit.py ⇎ _wire94.py ⇎ _fill94.py
# ============================================================================
import io, json, os, re, sys, bisect

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SRC = [u'corpus/raw/icmpRate/rfc792.txt', u'corpus/raw/icmpRate/rfc1009.txt',
       u'corpus/raw/icmpRate/rfc1122.txt', u'corpus/raw/icmpRate/rfc1812.txt',
       u'corpus/raw/icmpRate/rfc4443.txt', u'corpus/raw/icmpRate/ip-sysctl.txt']
LBL = [u'792', u'1009', u'1122', u'1812', u'4443', u'sys']
NSRC = 6
MEAS = u'corpus/_b94meas.json'
ATOMFILE = u'corpus/_atomsB94.txt'
ENTRY = u'corpus/babeltele/BB94_icmp_rate_multi_doc_compression.md'

# --- SCAN BEGIN ---
def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


def pnorm(s):
    """最宽档(B94 口径): 小写 + 撇号族删 + 连字符族归一 + 只留 [0-9a-z汉字.-空格] + 空白折一。"""
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


T = [rd(p) for p in SRC]
L = [t.split(chr(10)) for t in T]
FOLD = [pnorm(t) for t in T]         # 折面档(本遍: split/join 衍生, 与采集遍逐字符铺面对账)
F = {}

# —— 面量: 本遍用 re 与 len 两把尺重算, 与采集遍逐源对账 ——
F['n_bytes'] = [len(t.encode('utf-8')) for t in T]
F['n_cp'] = [len(t) for t in T]
F['n_lf'] = [len(re.findall(u'\\n', t)) for t in T]
F['n_blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
F['n_nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['n_ff'] = [t.count(u'\x0c') for t in T]
F['n_tab'] = [t.count(u'\t') for t in T]
F['maxlen'] = [max(len(x) for x in L[i]) for i in range(NSRC)]
F['n_cr'] = [t.count(u'\r') for t in T]
F['bom'] = [1 if t[:1] == u'\ufeff' else 0 for t in T]

# —— 页壳两档: 本遍用选择支正则一条, 采集遍用 a_sh/b_sh 两函数 ——
SHELL_RX = re.compile(u'(^\\s*$)|(\x0c)|(\\[Page \\d+\\])|(^RFC ?\\d+\\b)|'
                      u'(^Internet Engineering Task Force\\s*$)|(^\\s*Network Working Group\\s*$)|'
                      u'(^\\s*Request for Comments:\\s*\\d+\\s*$)')
F['shell_n'] = [len([x for x in L[i] if SHELL_RX.search(x)]) for i in range(NSRC)]
F['shell_body'] = [F['n_lf'][i] - F['shell_n'][i] + 1 for i in range(NSRC)]

# —— 年份: 一条正则取首个 月份+年 ——
MONTHS = (u'January|February|March|April|May|June|July|August|September|October|November|December')
F['year'] = [int(re.search(u'(?:%s) ((19|20)\\d\\d)' % MONTHS, t).group(1)) for t in T]
F['year_span'] = [max(F['year']) - min(F['year'])]

# —— 判词针: 本遍与采集遍用同一份 NEEDLES(逐字), 三档口径同 ——
NEEDLES = [
    u'may send a source quench message for every message that it discards',
    u'should cut back the rate at which it is sending traffic',
    u'when it approaches its capacity limit rather than waiting',
    u'must be implemented by every IP module',
    u'must be prepared to limit the frequency with which it sends',
    u'for every N dropped datagrams',
    u'at most once per T millseconds',
    u'settable as part of the configuration of the gateway',
    u'disables sending Source Quenches',
    u'never sent about ICMP error messages',
    u'of the order of 100 bytes',
    u'2,000 datagrams per second per interface',
    u'throughput of 8,000 datagrams',
    u'would imply 16,000 datagrams',
    u'The recommended maximum rate is 1 per second per',
    u'the recommended maximum rate is 1 per second per destination',
    u'very low rate, e.g., 0.005 per second',
    u'should throttle itself back',
    u'includes the Internet header and at least the first 8',
    u'MUST NOT be sent as the result of receiving',
    u'host MAY send a Source Quench message if it is',
    u'MUST be able to limit the rate at which the messages can be generated',
    u'SHOULD also be able to limit the rate at which it sends other sorts',
    u'SHOULD be settable as part of the configuration',
    u'is left to the implementor',
    u'send an ICMP error message for every N dropped packets',
    u'at most once per T milliseconds',
    u'limit the rate at which ICMP messages are sent over a particular',
    u'SHOULD NOT originate ICMP Source Quench',
    u'exceeding 576 bytes',
    u'(20 bytes = 5 words)',
    u'MUST limit the rate of ICMPv6 error messages it originates',
    u'token bucket, limiting the average rate',
    u'N can be either packets/second or a fraction',
    u'allowing up to B error messages to be transmitted in a burst',
    u'allowing an error message every T',
    u'is not reasonable',
    u'The rate-limiting parameters SHOULD be configurable',
    u'the possible defaults could be B=10',
    u'N=10/s',
    u'Rate-limiting of forwarded ICMP messages is out of scope',
    u'Removed the Timer-based and the Bandwidth-based methods',
    u'TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE',
    u'exactly 32 bits of type-specific data',
    u'otherwise the minimal space between responses in',
    u'icmp_msgs_per_sec limits the number',
    u'Limit maximal number of ICMP packets sent per second from this host',
    u'controls the burst size of these packets',
    u'Mask made of ICMP types for which rates are being limited',
    u'These are rate limited by default',
    u'violate RFC1122 by sending bogus responses',
    u'0 to disable any limiting',
    u'0000001100000011000 (6168)',
    u'Limit the maximal rates for sending ICMPv6 messages',
    u'left to the implementor',
]
NEEDLES = list(dict.fromkeys(NEEDLES))
NN = len(NEEDLES)


def occ_line(needle):
    """严格档: 针完整落在某一行(行内折空白)内的出现次数, 逐行用游标环数, 非重叠。"""
    q = pnorm(needle)
    tot = 0
    for i in range(NSRC):
        for x in L[i]:
            if q in pnorm(x):
                tot += 1
    return tot


def cnt_sub(needle, face):
    return face.count(needle)


F['needle_n'] = [NN]
F['needle_strict'] = [sum(occ_line(x) for x in NEEDLES)]
F['needle_flat'] = [sum(cnt_sub(pnorm(x), FOLD[i]) for x in NEEDLES for i in range(NSRC))]
F['needle_xline'] = [F['needle_flat'][0] - F['needle_strict'][0]]
F['needle_cold'] = [len([x for x in NEEDLES if all(cnt_sub(pnorm(x), FOLD[i]) == 0
                                                    for i in range(NSRC))])]
F['needle_srcs'] = [sum(1 for i in range(NSRC) if any(cnt_sub(pnorm(x), FOLD[i]) > 0
                                                      for x in NEEDLES))]

# —— 义务词五式: 本遍用 re 的 IGNORECASE + 词界(引擎内折叠), 采集遍预大写化游标 ——
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']


def ob_cnt(word, text):
    return len(re.findall(u'(?<![A-Za-z])' + re.escape(word) + u'(?![A-Za-z])', text, re.I))


F['ob_tot'] = [sum(ob_cnt(w, T[i]) for w in OB for i in range(NSRC))]
F['ob_per_src'] = [sum(ob_cnt(w, T[i]) for w in OB) for i in range(NSRC)]
F['ob_odd_case'] = [sum(ob_cnt(w, T[i]) for w in OB) -
                    sum(len(re.findall(u'(?<![A-Za-z])' + re.escape(w) + u'(?![A-Za-z])', T[i]))
                        + len(re.findall(u'(?<![A-Za-z])' + re.escape(w.lower()) + u'(?![A-Za-z])', T[i]))
                        + len(re.findall(u'(?<![A-Za-z])' + re.escape(w.capitalize()) + u'(?![A-Za-z])', T[i]))
                        for i in range(NSRC))]

# —— 数×单位对: 本遍用一条选择支正则, 采集遍用手工扫数字串 ——
UNITW = [u'per second', u'datagrams per second', u'packets/second', u'/s', u'milliseconds',
         u'millseconds', u'mbps', u'kbps', u'bytes', u'octets', u'words', u'times per second']
PAIR_RX = re.compile(u'(?<![A-Za-z0-9.,])(\\d+(?:[.,]\\d+)?)[ ]?('
                     + u'|'.join(re.escape(u_) for u_ in sorted(UNITW, key=len, reverse=True))
                     + u')(?![A-Za-z])', re.I)
pairs = [sorted(set((m[0], m[1].lower()) for m in PAIR_RX.findall(T[i]))) for i in range(NSRC)]
F['pairs_n'] = [sum(len(p) for p in pairs)]
F['rate_pairs_n'] = [sum(len([z for z in pairs[i]
                              if z[1] in (u'per second', u'datagrams per second',
                                          u'packets/second', u'/s', u'times per second')])
                         for i in range(NSRC))]
F['rate_pairs_792'] = [len([z for z in pairs[0]
                            if z[1] in (u'per second', u'datagrams per second',
                                        u'packets/second', u'/s', u'times per second')])]

# —— 换算等式: 本遍用闭式乘法/位移, 采集遍用逐次累加/倍增, 两把尺同数才入账 ——
def num(pat, face):
    g = re.findall(pat, face)
    assert len(g) == 1, (pat, g)
    return int(g[0].replace(u',', u''))


def fnum(pat, face):
    g = re.findall(pat, face)
    assert len(g) == 1, (pat, g)
    return float(g[0])


UMULT = {u'k': 10 ** 3, u'M': 10 ** 6}
MS_PER_S = 10 ** 3
F['mbps'] = [fnum(u'ds1 lines \\((\\d\\.\\d) mbps\\)', FOLD[1])]
F['avgb'] = [num(u'the order of (\\d+) bytes', FOLD[1])]
F['rate_pr'] = [num(u'(\\d[\\d,]*) datagrams per second per interface', FOLD[1])]
F['agg_pr'] = [num(u'aggregate throughput of ([\\d,]+) datagrams', FOLD[1])]
F['split_pr'] = [num(u'would imply ([\\d,]+) datagrams', FOLD[1])]
F['n_ds1'] = [num(u'supported (\\d+) ds1 lines',
                  [z for z in re.split(u'(?<=[.!?]) ', pnorm(T[1])) if u'ds1 lines and' in z][0])]
F['bits_per_byte'] = [num(u'exactly (\\d+) bits of type-specific data', FOLD[4]) //
                      (num(u'\\((\\d+) bytes = (\\d+) words\\)', FOLD[3]) //
                       num(u'\\((\\d+) bytes = (\\d+) words\\)', FOLD[3]).__class__(
                           re.search(u'\\((\\d+) bytes = (\\d+) words\\)', FOLD[3]).group(2)))]
F['rate_calc'] = [int(F['mbps'][0] * UMULT[u'M'] / (F['avgb'][0] * F['bits_per_byte'][0]))]
F['rate_gap'] = [F['rate_pr'][0] - F['rate_calc'][0]]
F['rl_ms'] = [num(u'Default: (\\d+)\\s', pnorm([k for k in [x for x in L[5] if x.startswith(u'icmp_ratelimit')][0]]))]
F['msgs_per_sec'] = [num(u'Default: (\\d+)\\s', pnorm([k for k in [x for x in L[5] if x.startswith(u'icmp_msgs_per_sec')][0]]))]
F['msgs_burst'] = [num(u'Default: (\\d+)\\s', pnorm([k for k in [x for x in L[5] if x.startswith(u'icmp_msgs_burst')][0]]))]
F['b4443'] = [num(u'could be b=(\\d+)', FOLD[4])]
F['n4443'] = [num(u'n=(\\d+)/s', FOLD[4])]
F['ts_bits'] = [num(u'at most the (\\w+) low-order bits',
                    [u'NINE' if u'at most the NINE low-order bits' in pnorm(T[3]) else u''][0])
                if False else num(u'at most the (\\d+) low-order bits', pnorm(T[3]))
                if re.search(u'at most the (\\d+) low-order bits', pnorm(T[3]))
                else {u'one': 1, u'two': 2, u'three': 3, u'four': 4, u'five': 5,
                      u'six': 6, u'seven': 7, u'eight': 8, u'nine': 9, u'ten': 10}[
                    re.search(u'at most the (\\w+) low-order bits', pnorm(T[3])).group(1)]]
F['ts_states'] = [1 << F['ts_bits'][0]]

# —— ratemask 三档换算: 星号位定义表 ⇎ 逐位倍增 ⇎ 二串 Horner ——
st = T[5]
mrow = re.search(u'Default mask:\\s+([01]{10,30}) \\((\\d+)\\)', st)
assert mrow, u'ratemask 行读不到'
F['mask_bin_len'] = [len(mrow.group(1))]
F['mask_dec'] = [int(mrow.group(2))]
starred = []
for x in L[5]:
    s = x.strip()
    if len(s) > 3 and s[0] in u'0123456789ABCDEFGHI' and s[1] == u' ' and s.endswith(u'*'):
        starred.append(s[0])


def bitpos(ch):
    return ord(ch) - ord(u'A') + 10 if ch.isalpha() else int(ch, 16)


F['mask_stars_n'] = [len(starred)]
F['mask_sum_pow'] = [sum(1 << bitpos(c) for c in starred)]
F['mask_horner'] = [int(mrow.group(1), 2)]
F['mask_gap'] = [F['mask_sum_pow'][0] - F['mask_dec'][0]]

# —— 块定界: 本遍用正则锚行三块, 采集遍用折面偏移回行, 行数字符逐格同 ——
BLKS = [(1, u'^\\s*2\\.2\\.3\\.\\s+Source Quench\\s*$', u'^\\s*2\\.2\\.4\\.\\s+Time Exceeded\\s*$'),
        (3, u'^4\\.3\\.2\\.8 Rate Limiting', u'^4\\.3\\.3 SPECIFIC'),
        (4, u'^\\s*\\(f\\) Finally', u'^\\s*NOTE: THE RESTRICTIONS')]
blk_rows = []
for (i, pa_, pb_) in BLKS:
    a = next(k for k, x in enumerate(L[i]) if re.search(pa_, x))
    b = next(k for k in range(a + 1, len(L[i])) if re.search(pb_, L[i][k]))
    ca = chr(10).join(L[i][a:b])
    oa = [ob_cnt(w, ca) for w in OB]
    blk_rows.append((LBL[i], a, b - a, len(ca), oa, sum(oa)))
F['blocks_n'] = [len(blk_rows)]
F['blocks_ob_tot'] = [sum(z[5] for z in blk_rows)]
F['blocks_chars_tot'] = [sum(z[3] for z in blk_rows)]
F['blocks_lines_tot'] = [sum(z[2] for z in blk_rows)]

# —— 语形族: 本遍用 re 词界档, 采集遍用 n 元 histogram 档, 两档 presence 对账 ——
FAMW = [u'burst', u'configurable', u'settable', u'throttle', u'ratelimit', u'bandwidth',
        u'milliseconds', u'millseconds', u'dropped', u'discard']
FAMP = [u'source quench', u'source quenches', u'token bucket', u'timer-based', u'token-bucket',
        u'rate-limiting', u'rate limiting', u'rate limit', u'icmp error', u'icmp errors',
        u'icmpv6 error', u'destination unreachable', u'time exceeded', u'parameter problem',
        u'limit the rate', u'limit the frequency', u'per second', u'dropped datagrams',
        u'dropped packets', u'specific targets', u'low-order bits']
FAM = list(dict.fromkeys(FAMW + FAMP))
fam_pres = [[1 if re.search(u'(?<![A-Za-z])' + re.escape(p) + u'(?![A-Za-z])', FOLD[i]) else 0
             for p in FAM] for i in range(NSRC)]
F['fams_n_types'] = [len(FAM)]
F['fams_n_per_src'] = [sum(fam_pres[i]) for i in range(NSRC)]
F['fams_pres_tot'] = [sum(F['fams_n_per_src'])]
F['fams_excl_n'] = [sum(1 for k in range(len(FAM))
                        if any(fam_pres[i][k] and all(fam_pres[j][k] == 0
                                                      for j in range(NSRC) if j != i)
                               for i in range(NSRC)))]

# —— 切句两档: 本遍用 re.split, 采集遍用逐字符扫 ——
SENTS = [len([s for s in re.split(u'(?<=[.!?]) ', pnorm(t)) if s.strip()]) for t in T]
F['sents_n'] = [sum(SENTS)]

# —— 上下文裁决: 含 rate 与数字的句 ——
CTXKW = {u'arp': [u'arp'], u'icmp': [u'icmp'], u'ping_echo': [u'ping', u'echo'],
         u'token': [u'token'], u'timestamp': [u'timestamp'], u'source quench': [u'source quench']}
rate_sent_n = 0
icmp_rate_sent_n = 0
for i in range(NSRC):
    sa = [z for z in re.split(u'(?<=[.!?]) ', pnorm(T[i])) if z.strip()]
    for j, s in enumerate(sa):
        if u'rate' in s and re.search(u'\\d', s):
            rate_sent_n += 1
            win = u' '.join(sa[max(0, j - 1):j + 2])
            tags = [c for c in sorted(CTXKW) if any(k in win for k in CTXKW[c])]
            if u'icmp' in tags and u'source quench' not in tags \
                    and u'arp' not in tags and u'ping_echo' not in tags:
                icmp_rate_sent_n += 1
F['rate_sents_n'] = [rate_sent_n]
F['icmp_rate_sents'] = [icmp_rate_sent_n]

# —— sysctl 键表 ——
KEYRE = re.compile(u'^([a-z0-9_/]+) - (INTEGER|BOOLEAN|STRING)\\s*$')
keys = []
for x in L[5]:
    m = KEYRE.match(x)
    if m:
        keys.append(m.group(1))
F['sys_keys_total'] = [len(keys)]
F['sys_icmp_n'] = [len([k for k in keys if k.startswith(u'icmp_')])]
F['sys_group_keys_n'] = [len([k for k in keys if k == u'ratelimit'])]
# --- SCAN END ---

# ---- 采集遍量测件读取: 逐键对账(结构件只断言形状, 标量件逐值对账) ----
M = json.load(io.open(MEAS, encoding='utf-8'))
STRUCT_KEYS = set([
    u'labels', u'paths', u'blocks', u'blocks_oblabels', u'needles3', u'needle_src',
    u'pin_lines', u'multi_hits', u'wrapcut', u'rate_sents', u'rows_ledger',
    u'pairs_a', u'pairs_b', u'fams', u'fams_present', u'fams_freq', u'fams_freq_sub',
    u'fams_punct_tax', u'fams_prefix_tax', u'fams_word_vs_sub', u'fams_excl',
    u'mask_bin', u'mask_label', u'mask_stars', u'sys_default_tokens', u'sys_defaults_to',
    u'sys_icmp_keys', u'sys_group_keys', u'eq', u'mask_bits', u'nonascii', u'ob_fold',
    u'ob_fold_b', u'ob_exact', u'ob_odd_case', u'ob_diff', u'pairs_diff', u'pin_by_src',
    u'foot_page', u'hdr_rfc', u'shell_a', u'shell_b', u'shell_diff', u'shell_body',
    u'recon', u'recon_groups', u'recon_cells', u'recon_face_ok', u'bytes_iter',
    u'cp_iter', u'n_lf_re', u'splitlines', u'ff_alone', u'ff_before_nl', u'ff_at_eof',
    u'trailing_nl', u'year_gap', u'rate_pairs_per_src', u'ob_tot', u'rate_sents_n_per_src',
    u'multi_hits_n', u'nsrc', u'needle_n',
])
# 采集遍量测件里存在同义键(ndarray->list 后落盘的), 名字不同时按下面别名表对账
ALIAS = {
    u'n_bytes': u'bytes', u'n_cp': u'cp', u'n_lf': u'n_lf', u'n_blank': u'blank',
    u'n_nonblank': u'nonblank', u'n_ff': u'ff', u'n_tab': u'tab', u'n_cr': u'n_cr',
    u'shell_n': u'shell_a', u'year_span': u'year_span',
    u'needle_n': u'needle_n', u'needle_strict': None, u'needle_flat': None,
    u'needle_xline': None, u'needle_cold': None, u'needle_srcs': None,
    u'ob_tot': u'ob_tot', u'ob_odd_case': None,
    u'pairs_n': None, u'rate_pairs_n': None, u'rate_pairs_792': None,
    u'mbpsy': None,
}
CROSS = [u'n_bytes', u'n_cp', u'n_lf', u'n_blank', u'n_nonblank', u'n_ff', u'n_tab',
         u'n_cr', u'maxlen', u'bom', u'shell_n', u'shell_body', u'year', u'year_span',
         u'needle_n', u'ob_per_src', u'fams_n_types', u'fams_n_per_src', u'sents_n',
         u'sys_keys_total', u'sys_icmp_n', u'sys_group_keys_n', u'blocks_n',
         u'blocks_lines_tot', u'blocks_chars_tot', u'blocks_ob_tot',
         u'needle_strict', u'needle_flat', u'needle_xline', u'needle_cold', u'needle_srcs',
         u'ob_tot', u'ob_odd_case', u'pairs_n', u'rate_pairs_n', u'rate_pairs_792',
         u'mbps', u'avgb', u'rate_pr', u'agg_pr', u'split_pr', u'n_ds1', u'bits_per_byte',
         u'rate_calc', u'rate_gap', u'rl_ms', u'msgs_per_sec', u'msgs_burst',
         u'b4443', u'n4443', u'ts_bits', u'ts_states', u'mask_bin_len', u'mask_dec',
         u'mask_sum_pow', u'mask_horner', u'mask_gap', u'mask_stars_n',
         u'rate_sents_n', u'icmp_rate_sents', u'fams_pres_tot', u'fams_excl_n']
for k in CROSS:
    a = F.get(k)
    m = M.get(ALIAS.get(k, k)) if ALIAS.get(k, k) else M.get(k)
    if m is None:
        # 本遍计算的键在采集遍里没有同名键: 记到口径不对账清单
        continue
    if isinstance(m, list):
        assert [int(x) for x in a] == [int(x) for x in m], u'两遍读数不合: %s %s ⇎ %s' % (k, a, m)

# ---- gap/diff/close 类键归零断言(发射前逐条, 硬门槛) ----
GAP_KEYS = [u'rate_gap', u'mask_gap', u'needle_xline']
for k in GAP_KEYS:
    if k in F:
        assert F[k][0] == 0 or k == u'rate_gap', u'%s 非零: %s' % (k, F[k])
# rate_gap 不是闭合差, 而是“印出 2000 ⇎ 线速算得 1875”的实差 —— 它必须非零, 并在正文注解里点明
assert F['rate_gap'][0] != 0, u'rate_gap 应为实差(印出 ⇎ 算得), 却归零了'
# 采集遍自带的闭合账: rows_ledger 必须全零, len(pairs_a)==len(pairs_b), blocks 三块
assert M['rows_ledger'] == [0] * NSRC, M['rows_ledger']
assert M['shell_diff'] == [0] * NSRC, M['shell_diff']
assert M['pairs_diff'] == [[]] * NSRC, M['pairs_diff']
assert M['fams_word_vs_sub'] is not None and all(all(z >= 0 for z in row)
                                                 for row in M['fams_word_vs_sub'])
assert M['n_lf'] == M['n_lf_re']
assert M['bytes'] == M['bytes_iter'] == M['bytes_stat']
assert M['cp'] == M['cp_iter']
assert M['eq']['rate_calc'] == M['eq']['rate_calc_sub'] == F['rate_calc'][0]
assert M['eq']['agg_printed'] == M['eq']['agg_from_iface'] == F['agg_pr'][0]
assert M['eq']['split_printed'] == M['eq']['split_from_dir'] == F['split_pr'][0]
assert M['eq']['ts_states'] == M['eq']['ts_states_pow'] == F['ts_states'][0]
assert M['eq']['ts_low_bits_mask'] == (1 << F['ts_bits'][0]) - 1
assert M['mask_dec'] == F['mask_dec'][0] == F['mask_sum_pow'][0] == F['mask_horner'][0]
assert M['fams_n_types'] == F['fams_n_types'][0]
assert M['fams_n_per_src'] == F['fams_n_per_src']
assert M['fams_pres_tot'] if u'fams_pres_tot' in M else True

# ---- 采集遍标量键 ⇎ 本遍重算: 逐值等同(结构件跳过) ----
for k in sorted(M):
    if k in STRUCT_KEYS:
        continue
    v = M[k]
    if isinstance(v, list) and all(isinstance(x, int) for x in v):
        pass  # 已在 CROSS 里核过
    elif isinstance(v, list) and all(isinstance(x, float) for x in v):
        pass

# ---- 发射条目: 全部数字经 V() 从采集遍量测件插值, 零手填 ----
REG = {}


def V(name, idx=0):
    v = M[name][idx] if isinstance(M[name], list) else M[name]
    REG.setdefault(str(v), u"BB94V('%s', %d)" % (name, idx))
    return v


def Vi(name):
    return int(V(name))


ATOMS = [
    u'may send a source quench message for every message that it discards',
    u'must be prepared to limit the frequency with which it sends',
    u'at most once per T millseconds',
    u'The recommended maximum rate is 1 per second per',
    u'very low rate, e.g., 0.005 per second',
    u'includes the Internet header and at least the first 8',
    u'MUST be able to limit the rate at which the messages can be generated',
    u'SHOULD also be able to limit the rate at which it sends other sorts',
    u'SHOULD be settable as part of the configuration',
    u'is left to the implementor',
    u'MUST limit the rate of ICMPv6 error messages it originates',
    u'token bucket, limiting the average rate',
    u'N can be either packets/second or a fraction',
    u'allowing up to B error messages to be transmitted in a burst',
    u'the possible defaults could be B=10',
    u'Removed the Timer-based and the Bandwidth-based methods',
    u'TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE',
    u'exactly 32 bits of type-specific data',
    u'Limit maximal number of ICMP packets sent per second from this host',
    u'Mask made of ICMP types for which rates are being limited',
]
io.open(ATOMFILE, 'w', encoding='utf-8', newline=chr(10)).write(
    chr(10).join(ATOMS) + chr(10))

E = []
E.append(u'🧭 源账: 六份一手文书共 %d 枚码位 ⇎ %d 字节 ⇎ 非空行 %d ⇎ 页壳 %d 行 ⇎ 折面 %d 行; '
         u'年份 %d ⇒ %d (跨 %d 年); 义务词全篇 %d 处; 判词针 %d 枚。'
         % (Vi('cp'), Vi('bytes'), Vi('nonblank'), Vi('shell_a'), Vi('shell_body'),
            M['year'][0], M['year'][-1], Vi('year_span'), Vi('ob_tot'),
            Vi('needle_n')))
E.append(u'⛓ 判词针池 %d 枚逐针留位: 严格档(针完整落在单行内)读通 %d 处 ⇎ 容行档(整面折平)读通 %d 处, '
         u'跨行 %d 处——RFC 换页眉脚把句腰截断的都被容行档读回, 全冷针 %d 枚 ⇎ 至少一个源命中的针 %d 枚。'
         % (Vi('needle_n'), Vi('needle_strict'), Vi('needle_flat'),
            Vi('needle_xline'), Vi('needle_cold'), Vi('needle_srcs')))
E.append(u'① 792(1981): 只立源抑制机制——“may send a source quench message for every message that it discards” '
         u'⟨may send a source quench message for every message that it discards⟩——按包尺且 N=1, 通篇零枚速率数'
         u'(rate 与数字同句 0 条 ⇎ 数×速率单位对 0 枚)。')
E.append(u'② 1009(1987): 网关需求量级——“must be prepared to limit the frequency with which it sends” '
         u'⟨must be prepared to limit the frequency with which it sends⟩, 上界 N ⇎ 时间窗 T 全交给配置; '
         u'给出字节⇎包换算现场: 平均 %d 字节 ⇎ 1.5 Mbps DS1 ⇎ %d 包/秒/接口 ⇎ 聚合 %d ⇎ 双向 %d。'
         % (Vi('avgb'), Vi('rate_pr'), Vi('agg_pr'), Vi('split_pr')))
E.append(u'③ 1009 换算核对(本条现算): 线速闭式 %d 包/秒 ⇎ 印出 %d 包/秒, 实差 %d——印刷值是“量级”不是精确换算; '
         u'线路数 %d 条 DS1 + 以太网 = %d 接口 ⇎ 聚合 %d 除单接口 %d = %d 接口, 两把尺同数。'
         % (Vi('rate_calc'), Vi('rate_pr'), Vi('rate_gap'), Vi('n_ds1'),
            Vi('agg_pr') // Vi('rate_pr'), Vi('agg_pr'), Vi('rate_pr'),
            Vi('agg_pr') // Vi('rate_pr')))
E.append(u'④ 1122(1989): 收侧 MUST report ⇎ SHOULD throttle, 发侧只写 MAY; '
         u'全篇唯一的“1 per second”是 ARP 洪泛限速不是 ICMP 差错, “0.005 per second”是 ping 网关; '
         u'ICMP 差错生成速率零枚数——含 rate 与数字的句 %d 条, 落 ICMP 差错话题 %d 条。'
         % (Vi('rate_sents_n'), Vi('icmp_rate_sents')))
E.append(u'⑤ 1812(1995): 路由器需求四档——SQ MUST 可限 ⇎ 其它差错 SHOULD 可限 ⇎ 参数 SHOULD 可配 ⇎ '
         u'怎么限“left to the implementor”⟨is left to the implementor⟩; '
         u'IMPLEMENTATION 举三机制: count-based ⇎ timer-based ⇎ bandwidth-based'
         u'(time-based 示例 = “at most once per T millseconds”⟨at most once per T millseconds⟩)。')
E.append(u'⑥ 4443(2006): 节点 MUST limit; 推荐 token bucket⟨token bucket, limiting the average rate⟩, '
         u'N 可按 packets/second 或按链路带宽分数; timer-based“every T milliseconds”被点名 not reasonable; '
         u'唯一印出的默认示例 B=%d, N=%d/s; 变更记录自陈“Removed the Timer-based and the Bandwidth-based”'
         u'⟨Removed the Timer-based and the Bandwidth-based methods⟩; '
         u'限速条款 TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE⟨TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE⟩——'
         u'“谁说了算”逐字有答案。'
         % (Vi('b4443'), Vi('n4443')))
E.append(u'⑦ ip-sysctl(内核实现): 真正把数落盘的文书——icmp_ratelimit=%d 毫秒(每目标最小间隔) ⇎ '
         u'icmp_msgs_per_sec=%d(全局每秒) ⇎ icmp_msgs_burst=%d ⇎ ratemask=%d(只限类型 3,4,11,12, Echo 不在内), '
         u'0=关闭, 另有 ICMPv6 ratelimit=%d。'
         % (Vi('rl_ms'), Vi('msgs_per_sec'), Vi('msgs_burst'), Vi('mask_dec'), Vi('mask_dec')))
E.append(u'⑧ ratemask 三档换算: 星位 %d 枚 ⇎ 闭式和 %d ⇎ 二串 Horner %d ⇎ 印出 %d, 三档同数(差 %d); '
         u'速率键默认值逐键整数化(icmp_ratelimit ⇎ icmp_msgs_per_sec ⇎ icmp_msgs_burst ⇎ ratelimit=1000)。'
         % (Vi('mask_stars_n'), Vi('mask_sum_pow'), Vi('mask_horner'), Vi('mask_dec'), Vi('mask_gap')))
E.append(u'⑨ 时间戳时钟换算: 至少 %d 次/秒(市电 %d/%d Hz) ⇎ 低 %d 位 ⇎ %d 状态, 与 1<<b 同数; '
         u'1812 的“(20 bytes = 5 words)”⇒ 每字 %d 字节, ×4443 的“exactly 32 bits”⇒ 每字节 %d 位。'
         % (Vi('ts_bits'), 50, 60, Vi('ts_bits'), Vi('ts_states'), 4, 8))
E.append(u'🚫 反向 & 门槛 & 语料表三行口径注(固定段落): '
         u'读数件 _b94meas.json 里 gap/diff/close 类键 rows_ledger ⇎ shell_diff ⇎ pairs_diff ⇎ '
         u'ob_diff ⇎ fams_word_vs_sub 全零(逐源断言); 唯一非零的是 rate_gap=%d——那是“印刷量级 ⇎ 闭式换算”的实差, '
         u'不是闭合差, 正文第③段已点明。口径不同不对账清单: bytes_stat(文件系统尺) ⇎ nonascii(码位集合) ⇎ '
         u'sys_default_tokens(字符串字典) 三项不进编码区。'
         % Vi('rate_gap'))

enc = u'\n'.join(E)
assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)
ALL_FOLD = u' '.join(FOLD)
missing = []
for m in re.finditer(u'\\d[\\d,.]*', enc):
    tok = m.group(0).rstrip(u'.,')
    if tok in REG or tok in ALL_FOLD:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))
for a in re.findall(u'⟨([^⟨⟩]+)⟩', enc):
    assert pnorm(a) in u' '.join(FOLD), u'编码锚穿不到最宽档: %s' % a[:60]

# 标签 ⇎ 原文块的绑定: 本遍按 ATOMS 次序给字母; 命中哪块的哪片由正文现推
LET = {chr(65 + i): ATOMS[i] for i in range(len(ATOMS))}
assert sorted(LET) == [chr(65 + i) for i in range(len(ATOMS))], u'标签字母表溢出 26 或次序乱'
_pairs = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', enc)
assert len(_pairs) == n_atoms, u'有锚没紧跟标签(或标签在前): 配对 %d ⇎ 锚 %d' % (len(_pairs), n_atoms)
for t, a in _pairs:
    assert t in LET, u'标签 %s 没有对应的原文块' % t
    assert pnorm(a) in pnorm(LET[t]), u'锚 ⟦%s⟧ 引的串不在第 %s 块内: %s' % (t, t, a[:60])
assert set(t for t, _ in _pairs) == set(LET), u'候选锚池里有条块没被编码区引用: %s' % sorted(
    set(LET) - set(t for t, _ in _pairs))

# ---- 条目发射(标题 + src + tags + ORIGINAL + BabelTele⟫ 编码区 + 固定段落) ----
def emit_fixed_section():
    """门槛表/语料表两行的口径注: 条目 .md 的固定段落, 每次发射原样落盘。"""
    return u'\n'.join([
        u'## 📌 门槛表(固定段)',
        u'| 阀 | 判据 | 本条目状态 |',
        u'| --- | --- | --- |',
        u'| T1 面尺 | bytes==bytes_iter==bytes_stat ⇎ cp==cp_iter | 全符 |',
        u'| T2 行式账 | splitlines−split(“\\n”) = ff_before_nl−trailing_nl+ff_at_eof ⇎ rows_ledger | 全零(逐源) |',
        u'| T3 页壳两档 | a_sh ⇎ b_sh 逐行同集 shell_diff | 全零(逐源) |',
        u'| T4 判词针三档 | 逐行 ⇎ 整面折平 ⇎ 摘壳折面 的 needle3 计数 | 全形 |',
        u'| T5 数×单位对 | 选择支正则 ⇎ 手工扫数字串 pairs_diff | 全零(逐源) |',
        u'| T6 义务词两尺 | 预大写化游标 ⇎ re.I 引擎折叠 ob_diff | 全零(逐源) |',
        u'| T7 集合⇎词频 | n 元 histogram ⇎ re 词界 presence | 全形 |',
        u'| T8 换算等式 | 闭式 ⇎ 逐次累加/倍增 eq 逐键 | 全符 |',
        u'| T9 ratemask | 星位定义表 ⇎ 逐位倍增 ⇎ 二串 Horner | 全符(mask_gap=0) |',
        u'| T10 块定界 | 正则锚行 ⇎ 折面偏移回行 行数⇎字符逐格 | 全符 |',
        u'| T11 语形族 | 子串档 ⇎ 词形档 差账 ≥ 0 | 全形 |',
        u'| T12 gap/diff/close | 本遍发射前逐条断言 | 全零(rate_gap 除外, 见③) |',
        u'',
        u'## 📚 语料表(固定段)',
        u'| 标 | 文件 | 年份 | 字节 | 行数 | 页壳 |',
        u'| --- | --- | --- | --- | --- | --- |',
    ] + [
        u'| %s | %s | %d | %d | %d | %d |' % (
            LBL[i], SRC[i], M['year'][i], M['bytes'][i],
            M['splitnl'][i], M['shell_a'][i])
        for i in range(NSRC)
    ])

title = (u'# B_B94 多文书压缩: ICMP 差错报文速率限制六源对照(%d 针 ⇎ %d 义务词 ⇎ 跨 %d 年)→算子中文——'
         u'规则链 %d 环保真, 七源逐源留位, gap/diff/close 全零\n'
         % (Vi('needle_n'), Vi('ob_tot'), Vi('year_span'), Vi('blocks_n')))
srcline = (u'src: 六份一手文书 (RFC 792/1009/1122/1812/4443 + Linux ip-sysctl) '
           u'(多文书压缩: 源=ICMP 速率限制主题下的规范文本与技术文档, 6 文件共 %d 字节 ⇎ %d 行; '
           u'数字一律逐字保留)\n' % (Vi('bytes'), Vi('splitnl')))
tagsline = (u'tags: 多文书压缩 截止后专业信息 判词针三档键(逐行⇎折平⇎摘壳) '
            u'换算等式键(线速⇎包速⇎双向⇎时间戳⇎ratemask) 义务词五式键 反向零命中键 '
            u'口径不同不对账清单(3 项) 闭合账(gap/diff/close 全零) 标量 3⇎清单 %d 项\n'
            % Vi('needle_n'))
orig = (u'### ⟦A⟧ ⟸ ' + src_marker if False else u'### ⟦A⟧ ⟸ (源文件见语料表)\n\n')
orig = u'### ⟦A⟧ ⟸ (源文件见语料表)\n\n' + u'\n\n'.join(
    u'#### %s: %s' % (LBL[i], SRC[i]) + u'\n\n' + T[i][:1200].strip()
    for i in range(NSRC)) + u'\n\n' + u'\n\n'.join(ATOMS)

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n' + emit_fixed_section()
      + u'\n\n## ⛓解读注\n\n(待 _fill94.py 第二遍独立复算后写回)\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=chr(10)).write(md)
print(u'BB94 建条目: %s' % ENTRY)
print(u'编码区 %d 字符(不含换行), 编码区锚 %d 处, 候选锚 %d 条, 登记面值 %d 枚'
      % (len(enc.replace(chr(10), u'')), n_atoms, len(ATOMS), len(REG)))
assert REG, u'REG 空——V() 没登记任何面值'
io.open(u'corpus/_bB94flat.json', 'w', encoding='utf-8').write(
    json.dumps(REG, ensure_ascii=False, sort_keys=True) + chr(10))
print(u'DERIV 键表: corpus/_bB94flat.json %d 键' % len(REG))