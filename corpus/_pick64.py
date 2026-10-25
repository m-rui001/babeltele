# -*- coding: utf-8 -*-
"""B64 现探(采集侧, 只测量不设门槛): 四份 RFC Editor 纯文本对"没人应答时重传退避封顶在哪一秒"的答法。
⟦A⟧rfc2131(1997, DHCPv4) ⇎ ⟦B⟧rfc3315(2003, DHCPv6, 后被 8415 废止) ⇎ ⟦C⟧rfc7083(2013, 只改这一枚参数的短文)
⇎ ⟦D⟧rfc8415(2018, DHCPv6 现行, Obsoletes: 3315)。
主轴答数: 64 seconds(A) ⇎ 120 secs(B) ⇎ 60<=值<=86400 且建议缺省 3600(C) ⇎ 缺省 3600 secs 且越界 MUST ignore(D)。
次轴(同一批文件回答的第二个问题): 拿到租约后多久去续——A 的 50%/87.5% of lease duration ⇎ B/D 的 0.5/0.8 of shortest preferred lifetime。
采集侧一律 re.findall / 子串计数; 键名只允许 [a-z0-9_](门槛的 B64V('…') 引用式只认这个字符集)。
三处版式断层最容易读错: C 把同一张参数表印了两遍(改前/改后), B 用制表式空格对齐、D 用竖线表格, A 根本没有 SOL_MAX_RT 这个词。
抓取时刻、rfc-editor.org 此刻给这四份挂的状态、各家客户端实际把 SOL_MAX_RT 记多久, 都不可由在库文件判定, 不进这张表。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NL = u'\n'
TAGS = (u'A', u'B', u'C', u'D')
PATH = [u'corpus/raw/dhcp/rfc2131.txt', u'corpus/raw/dhcp/rfc3315.txt',
        u'corpus/raw/dhcp/rfc7083.txt', u'corpus/raw/dhcp/rfc8415.txt']
N = 4
G = {}
REC = []


def put(k, v, note=u''):
    G[k] = v
    REC.append((k, note))


RB = [open(p, 'rb').read() for p in PATH]
T = [r.decode('utf-8-sig') for r in RB]
FO = [u' '.join(t.split()) for t in T]
LST = [t.split(NL) for t in T]

# ---- 形状 ----
put('bytes', [len(r) for r in RB], u'面内字节')
put('chars', [len(t) for t in T], u'码点数(已去 BOM)')
put('lines', [len(l) for l in LST], u'')
put('nonblank', [len([l for l in L if l.strip()]) for L in LST], u'判空按 strip() 同义即 isspace()')
put('maxlen', [max([len(l) for l in L]) for L in LST], u'')
put('trail', [len([l for l in L if l != l.rstrip()]) for L in LST], u'')
put('cr', [t.count(u'\r') for t in T], u'')
put('nonascii', [len([c for c in t if ord(c) > 127]) for t in T], u'utf-8-sig 解码后计数')
put('bom', [1 if r[:3] == b'\xef\xbb\xbf' else 0 for r in RB], u'UTF-8 BOM')
put('formfeed', [t.count(u'\x0c') for t in T], u'换页符')
put('nonblank_asciib', [len([l for l in L if l.strip(u' \t\r')]) for L in LST],
    u'手写空判口径(只认 空格/制表/回车): 把换页符独占行算作非空')
put('ff_only_lines', [len([l for l in L if l.strip(u' \t\r') and not l.strip()]) for L in LST],
    u'仅由 \x0c 之类“空格类但非 空格/制表/回车”的字符独占的行数')
put('nb_gap', [G[u'nonblank_asciib'][i] - G[u'nonblank'][i] for i in range(N)], u'两口径之差, 应等于 ff_only_lines')

HDR_SP = re.compile(r'^RFC \d{4}(?!\d)(?: |$)')
HDR_NS = re.compile(r'^RFC\d{4}(?!\d)(?: |$)')
FOOT_BRK = re.compile(r'\[Page \d+\]$')


def is_hdr(l):
    return bool(HDR_SP.match(l) or HDR_NS.match(l))


def is_foot(l):
    return bool(FOOT_BRK.search(l.strip()))


put(u'hdr_sp', [len([l for l in L if HDR_SP.match(l) and l[8:].strip()]) for L in LST], u'页眉 “RFC nnnn”(带空格)')
put(u'hdr_ns', [len([l for l in L if HDR_NS.match(l)]) for L in LST], u'页眉 “RFCnnnn”(不带空格)')
put(u'hdr', [len([l for l in L if is_hdr(l)]) for L in LST], u'两档之和')
put(u'foot', [len([l for l in L if is_foot(l)]) for L in LST], u'`[Page n]` 页脚行')
put(u'pg', [t.count(u'[Page ') for t in T], u'“[Page ” 子串出现处')
put(u'pagelines', [h + f for h, f in zip(G['hdr'], G['foot'])], u'')
put(u'pages_est', [max(h, f) for h, f in zip(G['hdr'], G['foot'])], u'页数估计')
put(u'sig_sha256_16', [hashlib.sha256(r).hexdigest()[:16] for r in RB], u'采集侧 sha256; 建条目侧换 blake2b 另立键')
put(u'sig_distinct', len(set(G['sig_sha256_16'])), u'')

# ---- 字面出现处 ----
LITK = {
    u'max64': u'maximum of 64 seconds', u'd64': u'64 seconds', u'd4s': u'4 seconds', u'd8s': u'8 seconds',
    u'reback': u'randomized exponential backoff', u'retrans': u'retransmi', u'solmaxrt': u'SOL_MAX_RT',
    u'infmaxrt': u'INF_MAX_RT', u'reqmaxrt': u'REQ_MAX_RT', u'renmaxrt': u'REN_MAX_RT', u'rebmaxrt': u'REB_MAX_RT',
    u'reqmaxrc': u'REQ_MAX_RC', u'relmaxrc': u'REL_MAX_RC', u'decmaxrc': u'DEC_MAX_RC', u'cnfmaxrt': u'CNF_MAX_RT',
    u'solmaxdelay': u'SOL_MAX_DELAY', u'soltimeout': u'SOL_TIMEOUT', u'rectimeout': u'REC_TIMEOUT',
    u's120': u'120 secs', u's3600': u'3600 secs', u's600': u'600 secs', u's1sec': u'1 sec',
    u'v86400': u'86400', u'v604800': u'604800', u'v3600': u'3600', u'v120': u'120',
    u'clamp': u'60 <=', u'ignore': u'MUST ignore any', u'irt': u'IRT', u'irc': u'IRC',
    u'infreq': u'Information-request', u'ta': u'IA_TA', u'pd': u'IA_PD',
    u't1': u'T1', u't2': u'T2', u'p50': u'50%', u'p875': u'87.5', u'p05': u'0.5', u'p08': u'0.8',
    u'infin': u'infinity', u'ffffffff': u'0xffffffff', u'preferre': u'shortest preferred lifetime',
    u'leasedur': u'lease duration', u'retain': u'this value is expected to be retained',
    u'iface': u'applies only to the network interface', u'sameacross': u'the same values across all IAs',
    u'discard': u'discards the IA', u'optionreq': u'Option Request option',
}
for k, s in sorted(LITK.items()):
    put(u'lit_' + k, [t.count(s) for t in T], u'字面 %r' % s)
put(u'lit_srt_minus_irt', [G[u'lit_solmaxrt'][i] - G[u'lit_irt'][i] for i in range(N)], u'')
put(u'lit_ratio_120_3600', [G[u'lit_s3600'][3], G[u'lit_s120'][1], G[u'lit_s3600'][3] // max(G[u'lit_s120'][1], 1)],
    u'D 的 3600 secs 行数 ÷ B 的 120 secs 行数')

# ---- 参数表: 同一名参数在各表里的默认值 ----
ROW = re.compile(u'^\\s*\\|?\\s*([A-Z][A-Z_0-9]{2,})\\s*\\|?\\s+(\\d+)\\s*(secs?|sec|s)\\s*\\|?\\s*(.*)$')
RC_ = re.compile(u'^\\s*\\|?\\s*([A-Z][A-Z_0-9]{2,})\\s*\\|?\\s+(\\d+)\\s*(?![\\d.])\\s*\\|?\\s*(.*)$')
HDRROW = re.compile(u'^\\s*\\|?\\s*Parameter\\s*\\|?\\s*Default')


def tables(i):
    """按 “Parameter / Default” 表头切块, 返回 [(表头行号, {参数: 秒值})]。"""
    ls, out, cur, blk = LST[i], [], None, []
    for n, l in enumerate(ls):
        if HDRROW.match(l):
            if cur is not None and blk:
                out.append((cur, dict(blk)))
            cur, blk = n, {}
            continue
        if cur is None:
            continue
        if not l.strip():
            continue
        m = ROW.match(l) or RC_.match(l)
        if m:
            blk[m.group(1)] = int(m.group(2))
        elif re.match(u'^\\s*\\d+\\.\\d+', l.strip()) and len(blk):
            out.append((cur, dict(blk)))
            cur, blk = None, []
    if cur is not None and blk:
        out.append((cur, dict(blk)))
    return out


TB = [tables(i) for i in range(N)]
put(u'tbl_n', [len(x) for x in TB], u'各文书里 “Parameter/Default” 表的块数')
put(u'tbl_rows', [[len(d) for _, d in x] for x in TB], u'每块行数')
put(u'tbl_start', [[st for st, _ in x] for x in TB], u'各块表头行号(0 起)')
for i, tg in enumerate(TAGS):
    put(u'tblkeys_' + tg.lower(), sorted(set(k for _, d in TB[i] for k in d)), u'表内参数名并集')
K = [u'SOL_MAX_RT', u'INF_MAX_RT', u'REN_MAX_RT', u'REB_MAX_RT', u'REQ_MAX_RT', u'SOL_TIMEOUT',
     u'REQ_TIMEOUT', u'REB_TIMEOUT', u'INF_TIMEOUT', u'REL_TIMEOUT', u'DEC_TIMEOUT', u'CNF_TIMEOUT',
     u'REC_TIMEOUT', u'SOL_MAX_DELAY', u'CNF_MAX_DELAY', u'INF_MAX_DELAY', u'CNF_MAX_RD',
     u'REQ_MAX_RC', u'REL_MAX_RC', u'DEC_MAX_RC', u'CNF_MAX_RC', u'REC_MAX_RC', u'MAX_RC']
for k in K:
    put(u'pv_' + k.lower(), [sorted(set(d[k] for _, d in TB[i] if k in d)) for i in range(N)], u'')
# C 文书里同一张表印两遍(改前 ⇎ 改后): 取两块的 SOL_MAX_RT/INF_MAX_RT 差
CBLK = TB[2]
put(u'c_block_n', len(CBLK), u'C 的表块数')
put(u'c_pair', [[d.get(u'SOL_MAX_RT'), d.get(u'INF_MAX_RT')] for _, d in CBLK], u'C 各块的 (SOL_MAX_RT, INF_MAX_RT)')
put(u'c_diff', [len([1 for _, d in CBLK if d.get(u'SOL_MAX_RT') == 120]),
                len([1 for _, d in CBLK if d.get(u'SOL_MAX_RT') == 3600])], u'C 内 120 档 ⇎ 3600 档块数')
# B ⇎ D 同名参数逐枚对照
BD = [(k, TB[1][0][1].get(k) if TB[1] else None, TB[3][0][1].get(k) if TB[3] else None) for k in K]
BD = [x for x in BD if x[1] is not None and x[2] is not None]
put(u'bd_n', len(BD), u'B ⇎ D 都有值的参数枚数')
put(u'bd_same', len([x for x in BD if x[1] == x[2]]), u'')
put(u'bd_diff', [[x[0], x[1], x[2]] for x in BD if x[1] != x[2]], u'')
put(u'bd_ratio', [x[2] // x[1] for x in BD if x[1] and x[2] % x[1] == 0], u'D÷B 整除的比值')
put(u'bd_close', G[u'bd_same'] + len(G[u'bd_diff']) - G[u'bd_n'], u'同+异−总')

# ---- 退避递推: A 文内 4→8→…→64 可由字面复算 ----
seq = [4, 8, 16, 32, 64]
put(u'a_seq', seq, u'A 的翻倍序列(首两值取自文内, 其后按“翻倍至 64”递推)')
put(u'a_seq_n', len(seq), u'')
put(u'a_seq_lit', [G[u'lit_d4s'][i] + G[u'lit_d8s'][i] + G[u'lit_d64'][i] for i in range(N)],
    u'文内直接印出 4 秒/8 秒/64 秒的行数合计')
put(u'a_doublings', len(seq) - 1, u'翻倍次数')
put(u'a_ratio', seq[-1] // seq[0], u'末项÷首项')
def pv1(i, k):
    v = G[u'pv_' + k.lower()][i]
    return v[0] if v else 0


put(u'cap_ratio_d_b', pv1(3, u'SOL_MAX_RT') // max(pv1(1, u'SOL_MAX_RT'), 1), u'D 缺省 ÷ B 常数')
put(u'clamp_span', 86400 // 60, u'夹逼上下界之比')

# ---- 次轴: T1/T2 ----
TN = [(u'p05', u'0.5'), (u'p08', u'0.8'), (u'ld', u'lease duration'),
      (u'spl', u'shortest preferred lifetime'), (u'userval', u'MUST use the'), (u'zerorule', u'are set to 0')]
for k, s in TN:
    a = [t.count(s) for t in T]
    b = [x.count(u' '.join(s.split())) for x in FO]
    put(u'n_' + k, a, u'原面 %r' % s)
    put(u'n_' + k + u'_fold', b, u'折平')
    put(u'wrap_' + k, [b[i] - a[i] for i in range(N)], u'折平−原面')
put(u'wrap_pin_n', len(TN), u'跨行针数')
put(u'wrap_pin_hit', len([1 for k, _ in TN if any(G[u'wrap_' + k])]), u'跨行有差的针数')
put(u'wrap_total', sum(sum(G[u'wrap_' + k]) for k, _ in TN), u'')

# ---- 跨行针(主轴线) ----
SN = [(u'max64full', u'The retransmission delay SHOULD be doubled with\n   subsequent retransmissions up to a maximum of 64 seconds.'),
      (u'c120', u'values of SOL_MAX_RT and INF_MAX_RT to be 120 seconds.'),
      (u'c3600', u'every 3600 seconds rather than every'),
      (u'clampfull', u'MUST be in this range: 60 <= "value" <= 86400'),
      (u'ignorefull', u'MUST ignore any SOL_MAX_RT option values that are less'),
      (u'retainfull', u'this value is expected to be retained for as long as practically possible'),
      (u'samefull', u'The T1/T2 times set in each applicable IA option for a Reply MUST be'),
      (u'discfull', u'If a client receives an IA_NA with T1 greater than T2'),
      (u'max64sp', u'The retransmission delay SHOULD be doubled with subsequent retransmissions up to a maximum of 64 seconds.'),
      (u'reback', u'client MUST adopt a retransmission strategy that incorporates a'),
      (u'ifacefull', u'An updated SOL_MAX_RT value applies only to the network interface')]
for k, s in SN:
    a = [t.count(s) for t in T]
    b = [x.count(u' '.join(s.split())) for x in FO]
    put(u's_' + k, a, u'原面 %r' % s[:36])
    put(u's_' + k + u'_fold', b, u'折平')
    put(u'wrapgap_' + k, [b[i] - a[i] for i in range(N)], u'')
put(u'wrap_sn_n', len(SN), u'')
put(u'wrap_sn_hit', len([1 for k, _ in SN if any(G[u'wrapgap_' + k])]), u'')
put(u'wrap_sn_total', sum(sum(G[u'wrapgap_' + k]) for k, _ in SN), u'')

# ---- 语汇 / 义务词 ----
WK = [(u'dhcp', u'DHCP'), (u'dhcp4', u'DHCPv4'), (u'dhcp6', u'DHCPv6'), (u'solicit', u'Solicit'),
      (u'renew', u'Renew'), (u'rebind', u'Rebind'), (u'inform', u'Information-request'),
      (u'timeout', u'timeout'), (u'timer', u'timer'), (u'backoff', u'backoff'),
      (u'retransword', u'retransmission'), (u'admin', u'administrator'), (u'traffic', u'traffic'),
      (u'interface', u'interface'), (u'server', u'server'), (u'client', u'client')]
for k, s in WK:
    put(u'v_' + k, [t.count(s) for t in T], u'')
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED'):
    put(u'u_' + w.replace(u' ', u'_').lower(), [t.count(w) for t in T], u'')
put(u'oblig_up', [G[u'u_must'][i] + G[u'u_should'][i] + G[u'u_may'][i] for i in range(N)], u'')
put(u'rfc2119_ref', [t.count(u'2119') for t in T], u'')

# ---- 文档身份 / 引用 ----
HK = [(u'cat_std', u'Category: Standards Track'), (u'cat_bcp', u'Category: Best Current Practices'),
      (u'cat_info', u'Category: Informational'), (u'cat_exp', u'Category: Experimental'),
      (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'), (u'issn_hdr', u'ISSN:'),
      (u'req_rc', u'Request for Comments:'), (u'obsoleted_by', u'obsoleted by')]
for k, s in HK:
    put(k, [t.count(s) for t in T], u'')
put(u'obsoleted_by', [len(re.findall(u'(?i)obsoleted by', t)) for t in T], u'')
for n in (u'2131', u'2132', u'3315', u'7083', u'8415', u'8252', u'4941', u'6221', u'7542', u'3315x'):
    if n == u'3315x':
        put(u'cite_ns_3315', [len(re.findall(u'RFC ?3315', t)) for t in T], u'带空格或不带空格都算')
        continue
    put(u'cite_' + n, [len(re.findall(u'RFC ?' + n + u'(?!\\d)', t)) for t in T], u'')
put(u'cite_3315_sp', [len(re.findall(u'RFC 3315', t)) for t in T], u'')
put(u'cite_3315_ns', [len(re.findall(u'RFC3315', t)) for t in T], u'页眉式(无空格)')

# ---- 搬运账 ----
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
    put(u'union_all' + suf, len(set().union(*S)), u'')
    put(u'only_c' + suf, len(S[2] - S[0] - S[1] - S[3]), u'')
    put(u'share_bd' + suf, len(S[1] & S[3]), u'')
put(u'shell_delta', [G[u'lines_ge40'][i] - G[u'lines_ge40_nos'][i] for i in range(N)], u'')
put(u'share_bd_delta', G[u'share_bd'] - G[u'share_bd_nos'], u'')

# ---- 答数所在窗 ----
RULE = [u'maximum of 64 seconds', u'SOL_MAX_RT      120 secs', u'SOL_MAX_RT     3600 secs', u'SOL_MAX_RT      | 3600 secs']
for i, s in enumerate(RULE):
    hits = [n + 1 for n, l in enumerate(LST[i]) if s in l]
    put(u'ans_line_' + TAGS[i].lower(), hits, u'答数行(1 起) %r' % s)
put(u'ans_lit_present', [1 if RULE[i] in T[i] else 0 for i in range(N)], u'')
put(u'ans_fold_present', [1 if u' '.join(RULE[i].split()) in FO[i] else 0 for i in range(N)], u'折平后命中')
put(u'ans_gap', [G[u'ans_fold_present'][i] - G[u'ans_lit_present'][i] for i in range(N)], u'')

NLITS = (u'SOL_MAX_RT', u'64 seconds', u'120', u'3600', u'86400', u'T1', u'T2')
put(u'num_lines', [len([l for l in L if len(l.strip()) >= 55 and any(x in l for x in NLITS)]) for L in LST], u'')

# ---- 2131 的 T1/T2 缺省式 ⇎ 7083 的 OLD/NEW 逐块对照 ----
put(u'lit_durdef', [t.count(u'0.5 * duration_of_lease') for t in T], u'A 的 T1 缺省式')
put(u'lit_durdef875', [t.count(u'0.875 * duration_of_lease') for t in T], u'A 的 T2 缺省式(原面, 折行处应为 0)')
put(u'lit_durdef875_fold', [x.count(u'0.875 * duration_of_lease') for x in FO], u'A 的 T2 缺省式(折平)')
put(u'lit_durdef875_gap', [G[u'lit_durdef875_fold'][i] - G[u'lit_durdef875'][i] for i in range(N)], u'折平−原面')
put(u'lit_durword', [t.count(u'duration_of_lease') for t in T], u'A 用词: 租约时长(带下划线的标识符)')
put(u'lit_t1def', [t.count(u'T1 defaults') + t.count(u'T2 defaults') for t in T], u'“defaults to” 式缺省句行数')
OLDNEW = re.compile(u'^\\s*(OLD|NEW):\\s*$')
for i, tg in enumerate(TAGS):
    rows = [n for n, l in enumerate(LST[i]) if OLDNEW.match(l)]
    pair = []
    for k in range(0, len(rows) - 1, 2):
        na, nb = rows[k], rows[k + 1]
        wa = NL.join(LST[i][na + 1:na + 4])
        wb = NL.join(LST[i][nb:nb + 4])
        pa = re.search(u'([A-Z][A-Z_0-9]{2,})', wa)
        va = re.search(u'(\\d+)\\s*secs?', wa)
        vb = re.search(u'(\\d+)\\s*secs?', wb)
        pair.append([pa.group(1) if pa else None, int(va.group(1)) if va else None,
                     int(vb.group(1)) if vb else None, nb - na])
    put(u'on_pair_' + tg.lower(), pair, u'OLD/NEW 相邻对: [参数名, 旧秒, 新秒, 行距]')
    put(u'on_n_' + tg.lower(), len(rows), u'OLD:/NEW: 标签行数')
    put(u'on_ratio_' + tg.lower(), [p[2] // p[1] for p in pair if p[1] and p[2] and p[2] % p[1] == 0], u'新÷旧')
print(u'--- OLD/NEW 与 v4 缺省式 ---')
for k in (u'lit_durdef', u'lit_durdef875', u'lit_durdef875_fold', u'lit_durdef875_gap', u'lit_durword', u'lit_t1def'):
    print(u'%-22s %s' % (k, G[k]))
for tg in TAGS:
    print(u'%-4s on_n %s pair %s ratio %s' % (tg, G[u'on_n_' + tg.lower()], G[u'on_pair_' + tg.lower()],
                                              G[u'on_ratio_' + tg.lower()]))

ORDER = [k for k, _ in REC]
MISS = [k for k in ORDER if not re.match(r'^[a-z0-9_]+$', k)]
io.open(u'corpus/_b64meas.json', 'w', encoding='utf-8').write(
    json.dumps(dict((k, G[k]) for k in ORDER), ensure_ascii=False, indent=0, sort_keys=True))
print(u'非 [a-z0-9_] 键名: %s' % (MISS or u'无'))
print(u'%s = rfc%s' % (u' ⇎ '.join(TAGS), u' ⇎ rfc'.join((u'2131', u'3315', u'7083', u'8415'))))
for k in (u'bytes', u'chars', u'lines', u'nonblank', u'nonblank_asciib', u'ff_only_lines', u'nb_gap', u'maxlen', u'trail', u'cr',
          u'nonascii', u'bom', u'formfeed', u'hdr_sp', u'hdr_ns', u'hdr', u'foot', u'pg', u'pagelines',
          u'pages_est', u'sig_distinct'):
    print(u'%-22s %s' % (k, G[k]))
print(u'--- 字面 ---')
for k in sorted(LITK):
    print(u'%-22s %s' % (u'lit_' + k, G[u'lit_' + k]))
print(u'%-22s %s' % (u'lit_srt_minus_irt', G[u'lit_srt_minus_irt']))
print(u'--- 参数表 ---')
print(u'%-22s %s rows %s' % (u'tbl_n', G[u'tbl_n'], G[u'tbl_rows']))
for k in K:
    print(u'%-22s %s' % (u'pv_' + k.lower(), G[u'pv_' + k.lower()]))
print(u'%-22s %s' % (u'c_block_n', G[u'c_block_n']))
print(u'%-22s %s' % (u'c_pair', G[u'c_pair']))
print(u'%-22s %s' % (u'c_diff', G[u'c_diff']))
print(u'%-22s %s same %s ratio %s close %s' % (u'bd_n', G[u'bd_n'], G[u'bd_same'], G[u'bd_ratio'], G[u'bd_close']))
for x in G[u'bd_diff']:
    print(u'  diff %s: B %s -> D %s' % (x[0], x[1], x[2]))
print(u'--- 递推 ---')
for k in (u'a_seq', u'a_seq_n', u'a_seq_lit', u'a_doublings', u'a_ratio', u'cap_ratio_d_b', u'clamp_span',
          u'lit_ratio_120_3600'):
    print(u'%-22s %s' % (k, G[k]))
print(u'--- 次轴跨行 ---')
for k, s in TN:
    print(u'%-14s n %s fold %s gap %s' % (k, G[u'n_' + k], G[u'n_' + k + u'_fold'], G[u'wrap_' + k]))
print(u'%-22s %s hit %s total %s' % (u'wrap_pin_n', G[u'wrap_pin_n'], G[u'wrap_pin_hit'], G[u'wrap_total']))
print(u'--- 主线跨行 ---')
for k, s in SN:
    print(u'%-14s s %s fold %s gap %s' % (k, G[u's_' + k], G[u's_' + k + u'_fold'], G[u'wrapgap_' + k]))
print(u'%-22s %s hit %s total %s' % (u'wrap_sn_n', G[u'wrap_sn_n'], G[u'wrap_sn_hit'], G[u'wrap_sn_total']))
print(u'--- 语汇/义务 ---')
for k, s in WK:
    print(u'%-22s %s' % (u'v_' + k, G[u'v_' + k]))
for w in (u'must_not', u'must', u'should_not', u'should', u'may', u'required'):
    print(u'%-22s %s' % (u'u_' + w, G[u'u_' + w]))
print(u'--- 身份/引用 ---')
for k, s in HK:
    print(u'%-22s %s' % (k, G[k]))
for n in (u'2131', u'2132', u'3315', u'7083', u'8415', u'8252', u'4941', u'6221', u'7542'):
    print(u'%-22s %s' % (u'cite_' + n, G[u'cite_' + n]))
print(u'%-22s %s / ns %s' % (u'cite_3315_sp', G[u'cite_3315_sp'], G[u'cite_3315_ns']))
print(u'--- 搬运 ---')
for suf in (u'_nos', u''):
    print(u'%-22s %s  only_c %s  share_bd %s  union %s' % (
        u'lines_ge40' + suf, G[u'lines_ge40' + suf], G[u'only_c' + suf], G[u'share_bd' + suf], G[u'union_all' + suf]))
print(u'%-22s %s / bd %s' % (u'shell_delta', G[u'shell_delta'], G[u'share_bd_delta']))
print(u'--- 答数窗 ---')
for tg in TAGS:
    print(u'%-22s %s' % (u'ans_line_' + tg.lower(), G[u'ans_line_' + tg.lower()]))
print(u'%-22s %s / fold %s / gap %s' % (u'ans_lit_present', G[u'ans_lit_present'],
                                         G[u'ans_fold_present'], G[u'ans_gap']))
print(u'%-22s %s' % (u'num_lines', G[u'num_lines']))
print(u'已写 corpus/_b64meas.json ｜ 键 %d' % len(ORDER))
