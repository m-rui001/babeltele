# -*- coding: utf-8 -*-
"""B63 现探(采集侧, 只测量不设门槛): 四份 RFC Editor 纯文本对"还没有 RTT 样本时第一个重传超时设多久"的答法。
⟦A⟧rfc1122(1989, Host Requirements Backport) ⇎ ⟦B⟧rfc2988(2000) ⇎ ⟦C⟧rfc6298(2011, Obsoletes: 2988 ⇎ Updates: 1122)
⇎ ⟦D⟧rfc9002(2021, QUIC; 与 B62 的 E 同一份字节, 本条只用它的超时侧)。
采集侧一律用正则(re.findall / 前后瞻); 键名只允许 [a-z0-9_]（门槛的 B63V('…') 引用式只认这个字符集）:
星号/逗号/括号都换成词形, 如 lit_rtoarrow='RTO <- ', lit_rtovalue='RTO = ', dur_333ms='333 ms'。
三条版式断层是本条最容易读错的地方, 因此页眉分“带空格 ⇎ 不带空格”两档、页脚分“作者名 ⇎ IETF 字样”两档, 换页符单独立键。
抓取时刻、rfc-editor.org 此刻给这四份挂的状态、各 OS 实现里 TCP_RTO_MIN 的实际取值都不可由在库文件判定, 不进这张表。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NL = u'\n'
TAGS = (u'A', u'B', u'C', u'D')
PATH = [u'corpus/raw/tcpRTO/rfc1122.txt', u'corpus/raw/tcpRTO/rfc2988.txt', u'corpus/raw/tcpRTO/rfc6298.txt',
        u'corpus/raw/tcpiw/rfc9002.txt']
N = 4
G = {}
REC = []


def put(k, v, note=u''):
    G[k] = v
    REC.append((k, note))


RB = [open(p, 'rb').read() for p in PATH]
T = [r.decode('utf-8-sig') for r in RB]
LOW = [t.lower() for t in T]
FO = [u' '.join(t.split()) for t in T]
LST = [t.split(NL) for t in T]

# ---- 形状 ----
put('bytes', [len(r) for r in RB], u'面内字节')
put('chars', [len(t) for t in T], u'码点数(已去 BOM)')
put('chars_no_nl', [len(t) - t.count(NL) for t in T], u'')
put('lines', [len(l) for l in LST], u'')
put('nonblank', [len([l for l in L if l.strip()]) for L in LST], u'')
put('maxlen', [max([len(l) for l in L]) for L in LST], u'')
put('trail', [len([l for l in L if l != l.rstrip()]) for L in LST], u'')
put('cr', [t.count(u'\r') for t in T], u'')
put('nonascii', [len([c for c in t if ord(c) > 127]) for t in T], u'utf-8-sig 解码后计数')
put('nonascii_raw', [len([c for c in r.decode('utf-8', 'replace') if ord(c) > 127]) for r in RB],
    u'utf-8(不吃 BOM) 解码后计数: BOM 本身算 1 枚')
put('bom', [1 if r[:3] == b'\xef\xbb\xbf' else 0 for r in RB], u'UTF-8 BOM')
put('formfeed', [t.count(u'\x0c') for t in T], u'换页符(分页版式的页边界)')

HDR_SP = re.compile(r'^RFC \d{4}(?!\d)(?: |$)')
HDR_NS = re.compile(r'^RFC\d{4}(?!\d)(?: |$)')
FOOT_BRK = re.compile(r'\[Page \d+\]$')
FOOT_IETF = re.compile(r'^Internet Engineering Task Force')


def is_hdr(l):
    return bool(HDR_SP.match(l) or HDR_NS.match(l))


def is_foot(l):
    s = l.strip()
    return bool(FOOT_BRK.search(s) or re.search(r'Page \d+$', s))


put(u'hdr_sp', [len([l for l in L if HDR_SP.match(l) and l[8:].strip()]) for L in LST], u'页眉写 “RFC nnnn”(带空格)')
put(u'hdr_ns', [len([l for l in L if HDR_NS.match(l)]) for L in LST], u'页眉写 “RFCnnnn”(不带空格)')
put(u'hdr', [len([l for l in L if is_hdr(l)]) for L in LST], u'两档之和')
put(u'foot', [len([l for l in L if is_foot(l)]) for L in LST], u'页脚行')
put(u'foot_brk', [len([l for l in L if FOOT_BRK.search(l.strip())]) for L in LST], u'')
put(u'foot_ietf', [len([l for l in L if FOOT_BRK.search(l.strip()) and FOOT_IETF.match(l.strip())]) for L in LST],
    u'页脚左侧印 “Internet Engineering Task Force” 的行数')
put(u'foot_old', [len([l for l in L if re.search(r'Page \d+$', l.strip()) and not FOOT_BRK.search(l.strip())])
                  for L in LST], u'旧式无方括号页脚')
put(u'pagelines', [h + f for h, f in zip(G['hdr'], G['foot'])], u'')
put(u'pages_est', [len([c for c in t if c == u'\x0c']) or max(h, f) for t, h, f in zip(T, G['hdr'], G['foot'])],
    u'页数估计: 有换页符按换页符, 否则按页眉页脚较大者')
put(u'sig_sha256_16', [hashlib.sha256(r).hexdigest()[:16] for r in RB], u'采集侧用 sha256; 建条目侧换 blake2b 另立键')
put(u'sig_distinct', len(set(G['sig_sha256_16'])), u'')

# ---- 字面出现处(子串) ----
LITK = {u'3seconds': u'3 seconds', u'1second': u'1 second', u'333ms': u'333 ms', u'1ms': u'1 ms',
        u'200ms': u'200 ms', u'rtoarrow': u'RTO <- ', u'rtovalue': u'RTO = ', u'setrto': u'set RTO',
        u'inirto': u'initial RTO', u'rounded': u'rounded up', u'kgran': u'kGranularity',
        u'kinirtt': u'kInitialRtt', u'smoothed': u'smoothed_rtt', u'rttvar_l': u'rttvar', u'rttvar_u': u'RTTVAR',
        u'srtt': u'SRTT', u'pto': u'PTO', u'rto': u'RTO', u'4xrttvar': u'4*rttvar', u'4k_rttvar': u'4 * rttvar',
        u'backoff': u'backing off', u'commab': u'less than 1 second then the',
        u'commac': u'less than 1 second, then the', u'revert': u'MUST be re-initialized to 3 seconds',
        u'onesecclaim': u'a PTO of 1 second', u'tcpinitrto': u"TCP's initial", u'jaco': u'Jacobson',
        u'333full': u'333 milliseconds',
        u'half': u'rttvar = kInitialRtt / 2', u'pto_eq': u'PTO = smoothed_rtt',
        u'smoothinit': u'smoothed_rtt = kInitialRtt'}
for k, s in sorted(LITK.items()):
    put(u'lit_' + k, [t.count(s) for t in T], u'字面 %r' % s)
put(u'assign_forms', [G[u'lit_rtoarrow'][i] + G[u'lit_rtovalue'][i] for i in range(N)], u'赋值符两档之和')
put(u'assign_gap', [G[u'lit_rtoarrow'][i] - G[u'lit_rtovalue'][i] for i in range(N)], u'箭头 − 等号')
put(u'floor_forms_gap', [G[u'lit_commab'][i] + G[u'lit_commac'][i] for i in range(N)],
    u'“不到 1 秒就上取到 1 秒”条款的两种标点各计一次之和')
put(u'unit_both_333', [1 if G[u'lit_333ms'][i] and G[u'lit_333full'][i] else 0 for i in range(N)],
    u'“333 ms” ⇎ “333 milliseconds” 两种拼法同时出现')

# ---- 时长 token: 数字+单位, 归一到毫秒 ----
DUR = re.compile(u'(\\d[\\d,]*)\\s*(milliseconds?|ms|seconds?|sec|useconds?)(?![A-Za-z])')
MULT = {u'milliseconds': 1, u'millisecond': 1, u'ms': 1, u'seconds': 1000, u'second': 1000, u'sec': 1000,
        u'useconds': 0}


def durs(t):
    out = []
    for m in DUR.finditer(t):
        v = int(m.group(1).replace(u',', u''))
        u = m.group(2).lower()
        out.append(v * MULT[u] if MULT[u] else 0)
    return sorted(set(x for x in out if x > 0))


for i, tg in enumerate(TAGS):
    put(u'durms_' + tg.lower(), durs(T[i]), u'归一到毫秒后的时长取值集')
    put(u'durms_n_' + tg.lower(), len(durs(T[i])), u'')
    put(u'durlit_' + tg.lower(), len(DUR.findall(T[i])), u'“数字+单位”出现处(含重复)')
put(u'dur_ms_lo', min([min(durs(t)) for t in T]), u'四份里最小的时长(毫秒)')
put(u'dur_ms_hi', max([max(durs(t)) for t in T]), u'四份里最大的时长(毫秒)')
put(u'dur_ratio', [G[u'dur_ms_hi'] // G[u'dur_ms_lo']], u'两端之比')
for k, s in ((u'seconds', u'second'), (u'ms', u'ms'), (u'mill word', u'millisecond')):
    put(u'unit_' + k.replace(u' ', u'_'), [t.count(s) for t in T], u'')

# ---- 规范句所在窗口: 从答数行回溯到最近小节标题, 再到下一节标题 ----
HEAD = re.compile(r'^\s*(\d+(?:\.\d+)*)\.?\s+\S')
SUB = re.compile(r'^\s*\(?([a-z])\)\s+\S')
RULE = [u'(b)  RTO = 3 seconds', u'set RTO <- 3 seconds (per RFC 1122', u'set RTO <- 1 second',
        u'SHOULD be set to 333 milliseconds']
SECW, SECH, SECLEN, SECSUB = [], [], [], []
for i in range(N):
    ls = LST[i]
    hits = [n for n, l in enumerate(ls) if RULE[i] in l]
    r = hits[-1] if hits else 0
    a = None
    for n in range(r, -1, -1):
        if HEAD.match(ls[n]) and len(ls[n].strip()) > 3:
            a = n
            break
    if a is None:
        a = r
    b = len(ls)
    for n in range(r + 1, len(ls)):
        m = HEAD.match(ls[n])
        if m and len(ls[n].strip()) > 3 and ls[n].strip() != ls[a].strip() and \
           not ls[n].strip().startswith(ls[a].strip().split(u' ')[0]):
            b = n
            break
    SECW.append((a, b))
    SECLEN.append(len(NL.join(ls[a:b])))
    SECH.append(ls[a].strip()[:64])
    SECSUB.append(len([1 for l in ls[a:b] if SUB.match(l)]))
put(u'sec_w', list(SECW), u'')
put(u'sec_len', SECLEN, u'')
put(u'sec_head', SECH, u'')
put(u'sec_sub', SECSUB, u'窗内 (a)/(b) 式子条目行数')
for i, tg in enumerate(TAGS):
    put(u'sec_len_' + tg.lower(), SECLEN[i], u'')
WINS = [(u'3seconds', u'3 seconds'), (u'1second', u'1 second'), (u'333ms', u'333 ms'),
        (u'333full', u'333 milliseconds'), (u'rtoarrow', u'RTO <- '),
        (u'rounded', u'rounded up'), (u'kgran', u'kGranularity')]
for k, s in WINS:
    ws = []
    for i in range(N):
        ls = LST[i]
        a, b = SECW[i]
        ws.append(NL.join(ls[a:b]).count(s) if b > a else 0)
    put(u'secw_' + k, ws, u'')
    put(u'outw_' + k, [G[u'lit_' + k][i] - ws[i] for i in range(N)], u'')

# ---- 单空格档 ⇎ 折平档(跨行通道) ----
SN = [(u'init3', u'set RTO <- 3 seconds (per RFC 1122'), (u'init1', u'set RTO <- 1 second'),
      (u'floor', u'Whenever RTO is computed, if it is less than 1 second'),
      (u'rounded', u'RTO SHOULD be rounded up to 1 second'), (u'revert', u'MUST be re-initialized to 3 seconds'),
      (u'v3', u'(b)  RTO = 3 seconds'), (u'ms333', u'SHOULD be set to 333 milliseconds'),
      (u'claim1s', u'a PTO of 1 second'), (u'pto_eq', u'PTO = smoothed_rtt + max(4*rttvar, kGranularity) + max_ack_delay'),
      (u'half', u'rttvar = kInitialRtt / 2'), (u'tcpinit', u"as recommended for TCP's initial"),
      (u'cite6298', u'see Section 2 of [RFC6298]'), (u'granrec', u'recommends a value of 1 ms'),
      (u'backoff5', u'the "backing off" on repeated')]
for k, s in SN:
    a = [t.count(s) for t in T]
    b = [x.count(u' '.join(s.split())) for x in FO]
    put(u's_' + k, a, u'原面 %r' % s[:40])
    put(u's_' + k + u'_fold', b, u'折平')
    put(u'wrap_gap_' + k, [b[i] - a[i] for i in range(N)], u'折平−原面')
put(u'wrap_pin_n', len(SN), u'跨行针数')
put(u'wrap_pin_hit', len([1 for k, _ in SN if any(G[u'wrap_gap_' + k])]), u'跨行有差的针数')
put(u'wrap_gap_total', sum(sum(G[u'wrap_gap_' + k]) for k, _ in SN), u'')

# ---- 语汇 ----
WK = [(u'rto', u'RTO'), (u'pto', u'PTO'), (u'retrans', u'retransmi'), (u'rtt', u'RTT'),
      (u'rtt_low', u'rtt'), (u'clock', u'clock granularity'), (u'gran', u'granularity'),
      (u'initrto_cap', u'Initial RTO'), (u'initrto_low', u'initial RTO'), (u'timer', u'timer'),
      (u'persist', u'persistent'), (u'probe', u'probe'), (u'slowstart', u'slow start'),
      (u'congest', u'congestion control'), (u'variance', u'variance'), (u'backoff_word', u'back off')]
for k, s in WK:
    put(u'v_' + k, [t.count(s) for t in T], u'')

# ---- 义务词体例 ----
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED'):
    put(u'u_' + w.replace(u' ', u'_').lower(), [t.count(w) for t in T], u'')
put(u'oblig_up', [G[u'u_must'][i] + G[u'u_should'][i] + G[u'u_may'][i] for i in range(N)], u'')
for w in (u'must', u'should', u'may'):
    put(u'l_' + w, [len(re.findall(u'(?<![A-Za-z])' + w + u'(?![A-Za-z])', t)) for t in T], u'')
put(u'oblig_low', [G[u'l_must'][i] + G[u'l_should'][i] + G[u'l_may'][i] for i in range(N)], u'')
put(u'rfc2119_ref', [t.count(u'2119') for t in T], u'')
put(u'key_words_boiler', [t.count(u'key words') + t.count(u'Key words') for t in T], u'')

# ---- 文档身份 ----
HK = [(u'cat_std', u'Category: Standards Track'), (u'cat_exp', u'Category: Experimental'),
      (u'cat_info', u'Category: Informational'), (u'cat_hist', u'Category: Historic'),
      (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'), (u'issn_hdr', u'ISSN:'),
      (u'rfc_hdr', u'RFC Internet Engineering Task Force'), (u'braden_foot', u'Braden'),
      (u'editor_hdr', u'Editor'), (u'req_rc', u'Request for Comments:')]
for k, s in HK:
    put(k, [t.count(s) for t in T], u'')
put(u'obsoleted_by', [len(re.findall(u'(?i)obsoleted by', t)) for t in T], u'')
put(u'errata', [len(re.findall(u'(?i)errata', t)) for t in T], u'')
put(u'std_lvl', [len(re.findall(u'Standards Track', t)) for t in T], u'')
for n in (u'1122', u'1123', u'2988', u'6298', u'9002', u'793', u'1122b'):
    if n == u'1122b':
        put(u'cite_ns_1122', [len(re.findall(u'RFC ?1122', t)) for t in T], u'带空格或不带空格都算')
        continue
    put(u'cite_' + n, [len(re.findall(u'RFC ?' + n + u'(?!\\d)', t)) for t in T], u'')
put(u'cite_1122_sp', [len(re.findall(u'RFC 1122', t)) for t in T], u'')
put(u'cite_1122_ns', [len(re.findall(u'RFC1122', t)) for t in T], u'页眉式(无空格)')

# ---- 搬运账: 归一 a-z0-9 长行集合(含壳 ⇎ 去页眉页脚) ----
NRM = lambda l: re.sub(u'[^a-z0-9]', u'', l.lower())


def line_set(i, shell=True):
    out = set()
    for l in LST[i]:
        if not shell and (is_hdr(l) or is_foot(l)):
            continue
        n = NRM(l)
        if len(l.strip()) >= 40 and len(n) >= 40:
            out.add(n)
    return out


for shell, suf in ((True, u''), (False, u'_nos')):
    S = [line_set(i, shell) for i in range(N)]
    put(u'lines_ge40' + suf, [len(s) for s in S], u'')
    for a in range(N):
        for b in range(a + 1, N):
            put(u'share_%s%s%s' % (TAGS[a].lower(), TAGS[b].lower(), suf), len(S[a] & S[b]), u'')
    put(u'union_abc' + suf, len(S[0] | S[1] | S[2]), u'')
    put(u'union_abcd' + suf, len(set().union(*S)), u'')
    put(u'only_b' + suf, len(S[1] - S[0] - S[2]), u'')
    put(u'only_c' + suf, len(S[2] - S[0] - S[1] - S[3]), u'')
    put(u'only_d' + suf, len(S[3] - S[0] - S[1] - S[2]), u'')
    put(u'share_bc_plus' + suf, len((S[1] & S[2] & S[3]) | (S[1] & S[2] & S[0])), u'')
put(u'shell_delta', [G[u'lines_ge40'][i] - G[u'lines_ge40_nos'][i] for i in range(N)], u'')
put(u'union_delta', G[u'union_abcd'] - G[u'union_abc'], u'')

# ---- B ⇎ C 条款逐行对照(废止链上的标点差) ----
FL = [(i, n, l) for i in (1, 2) for n, l in enumerate(LST[i]) if u'rounded up' in l]
put(u'floor_lines', [len(FL), [l.strip() for _, _, l in FL]], u'含 “rounded up” 的行')
FB = [l for i, n, l in FL if i == 1]
FC = [l for i, n, l in FL if i == 2]
put(u'floor_pair', [len(FB), len(FC)], u'B ⇎ C 各自的上取整条款行数')
put(u'floor_same_bytes', [len([1 for a, b in zip(FB, FC) if a == b])], u'')
put(u'floor_same_norm', [len([1 for a, b in zip(FB, FC) if NRM(a) == NRM(b)])], u'')
put(u'floor_diff_bytes', [len([1 for a, b in zip(FB, FC) if a != b])], u'')
put(u'floor_close', G[u'floor_same_norm'][0] - G[u'floor_same_bytes'][0] - G[u'floor_diff_bytes'][0], u'归一同−字节同−字节异')
# (2.4) 条款在两文档里各占 2 行: 逐行对照, 标点差只在第一行
AI = []
for i in (1, 2):
    AI.append(max([n for n, l in enumerate(LST[i]) if u'Whenever RTO is computed' in l]))
PAIR = [(LST[1][AI[0] + k], LST[2][AI[1] + k]) for k in range(4)
        if AI[0] + k < len(LST[1]) and AI[1] + k < len(LST[2])]
put(u'clause_lines', [len(PAIR), [a.strip() for a, b in PAIR], [b.strip() for a, b in PAIR]],
    u'B ⇎ C 的 (2.4) 条款逐行')
put(u'align_n', len(PAIR), u'对照窗口行数')
put(u'align_same_bytes', len([1 for a, b in PAIR if a == b]), u'')
put(u'align_punct_only', len([1 for a, b in PAIR if a != b and NRM(a) == NRM(b)]), u'仅标点/空白差')
put(u'align_norm_diff', len([1 for a, b in PAIR if NRM(a) != NRM(b)]), u'')
put(u'align_close', G[u'align_same_bytes'] + G[u'align_punct_only'] + G[u'align_norm_diff'] - G[u'align_n'], u'')

# ---- 锚候选行 ----
NLITS = (u'RTO', u'PTO', u'3 seconds', u'1 second', u'333', u'kGranularity', u'kInitialRtt')
put(u'num_lines', [len([l for l in L if len(l.strip()) >= 55 and any(x in l for x in NLITS)]) for L in LST], u'')
for i, tg in enumerate(TAGS):
    put(u'num_lines_' + tg.lower(), G[u'num_lines'][i], u'')

ORDER = [k for k, _ in REC]
MISS = [k for k in ORDER if not re.match(r'^[a-z0-9_]+$', k)]
io.open(u'corpus/_b63meas.json', 'w', encoding='utf-8').write(
    json.dumps(dict((k, G[k]) for k in ORDER), ensure_ascii=False, indent=0, sort_keys=True))
print(u'非 [a-z0-9_] 键名: %s' % (MISS or u'无'))
for tg, s in zip(TAGS, (u'1122', u'2988', u'6298', u'9002')):
    print(u'%s=rfc%s' % (tg, s), end=u' ')
print()
for k in (u'bytes', u'chars', u'lines', u'nonblank', u'maxlen', u'trail', u'cr', u'nonascii', u'nonascii_raw',
          u'bom', u'formfeed', u'hdr_sp', u'hdr_ns', u'hdr', u'foot', u'foot_brk', u'foot_ietf', u'foot_old',
          u'pagelines', u'pages_est', u'sig_distinct'):
    print(u'%-20s %s' % (k, G[k]))
print(u'--- 赋值符与答数 ---')
for k in (u'3seconds', u'1second', u'333ms', u'1ms', u'rtoarrow', u'rtovalue', u'setrto', u'inirto',
          u'rounded', u'commab', u'commac', u'revert', u'onesecclaim', u'4xrttvar', u'4k_rttvar', u'kgran',
          u'kinirtt', u'backoff', u'tcpinitrto', u'jaco', u'smoothed', u'rttvar_l', u'rttvar_u', u'srtt',
          u'pto', u'rto', u'half', u'pto_eq', u'smoothinit', u'333full'):
    print(u'%-20s %s' % (u'lit_' + k, G[u'lit_' + k]))
print(u'%-20s %s / %-16s %s' % (u'assign_forms', G[u'assign_forms'], u'unit_both_333', G[u'unit_both_333']))
print(u'--- 时长归一(毫秒) ---')
for tg in TAGS:
    print(u'  %s durms=%s n=%d lit=%d' % (tg, G[u'durms_' + tg.lower()], G[u'durms_n_' + tg.lower()],
                                          G[u'durlit_' + tg.lower()]))
print(u'%-20s %s / hi %s / ratio %s' % (u'dur_ms_lo', G[u'dur_ms_lo'], G[u'dur_ms_hi'], G[u'dur_ratio']))
print(u'--- 规范窗 ---')
print(u'%-20s %s' % (u'sec_w', G[u'sec_w']))
print(u'%-20s %s' % (u'sec_len', G[u'sec_len']))
print(u'%-20s %s' % (u'sec_sub', G[u'sec_sub']))
for i, tg in enumerate(TAGS):
    print(u'  %s 标题: %s' % (tg, G[u'sec_head'][i][:60]))
for k, _ in WINS:
    print(u'%-20s %s / out %s' % (u'secw_' + k, G[u'secw_' + k], G[u'outw_' + k]))
print(u'--- 跨行通道 ---')
for k, s in SN:
    print(u'%-14s s %s fold %s gap %s' % (k, G[u's_' + k], G[u's_' + k + u'_fold'], G[u'wrap_gap_' + k]))
print(u'%-20s %s hit %s total %s' % (u'wrap_pin_n', G[u'wrap_pin_n'], G[u'wrap_pin_hit'], G[u'wrap_gap_total']))
print(u'--- 语汇 ---')
for k, s in WK:
    print(u'%-20s %s' % (u'v_' + k, G[u'v_' + k]))
print(u'--- 义务词 ---')
for w in (u'must_not', u'must', u'should_not', u'should', u'may', u'required'):
    print(u'%-20s %s' % (u'u_' + w, G[u'u_' + w]))
print(u'%-20s %s / low %s' % (u'oblig_up', G[u'oblig_up'], G[u'oblig_low']))
print(u'%-20s %s / boiler %s' % (u'rfc2119_ref', G[u'rfc2119_ref'], G[u'key_words_boiler']))
print(u'--- 身份 ---')
for k, s in HK:
    print(u'%-20s %s' % (k, G[k]))
print(u'%-20s %s errata %s std_lvl %s' % (u'obsoleted_by', G[u'obsoleted_by'], G[u'errata'], G[u'std_lvl']))
for n in (u'1122', u'1123', u'2988', u'6298', u'9002', u'793'):
    print(u'%-20s %s' % (u'cite_' + n, G[u'cite_' + n]))
print(u'%-20s %s / ns %s' % (u'cite_1122_sp', G[u'cite_1122_sp'], G[u'cite_1122_ns']))
print(u'--- 搬运账 ---')
for suf in (u'_nos', u''):
    print(u'%-20s %s' % (u'lines_ge40' + suf, G[u'lines_ge40' + suf]))
    for a in range(N):
        for b in range(a + 1, N):
            print(u'  share_%s%s%s = %d' % (TAGS[a].lower(), TAGS[b].lower(), suf,
                                            G[u'share_%s%s%s' % (TAGS[a].lower(), TAGS[b].lower(), suf)]))
    print(u'%-20s %s abc %s  only_b/c/d %s/%s/%s  bc+ %s' % (
        u'union_abcd' + suf, G[u'union_abcd' + suf], G[u'union_abc' + suf], G[u'only_b' + suf],
        G[u'only_c' + suf], G[u'only_d' + suf], G[u'share_bc_plus' + suf]))
print(u'%-20s %s' % (u'shell_delta', G[u'shell_delta']))
print(u'--- B⇎C 条款对照 ---')
print(u'floor_lines %d: %s' % (G[u'floor_lines'][0], G[u'floor_lines'][1]))
print(u'clause_lines B: %s' % (G[u'clause_lines'][1],))
print(u'clause_lines C: %s' % (G[u'clause_lines'][2],))
for k in (u'floor_pair', u'floor_same_bytes', u'floor_same_norm', u'floor_diff_bytes', u'floor_close',
          u'align_n', u'align_same_bytes', u'align_punct_only', u'align_norm_diff', u'align_close'):
    print(u'%-20s %s' % (k, G[k]))
print(u'--- 锚候选行 ---')
print(u'%-20s %s' % (u'num_lines', G[u'num_lines']))
print(u'已写 corpus/_b63meas.json ｜ 键 %d' % len(ORDER))
