# -*- coding: utf-8 -*-
"""B62 现探(采集侧, 只测量不设门槛): 五份 RFC Editor 纯文本对"新建连接第一个 RTT 里允许立刻发多少字节"的答法。
⟦A⟧rfc2581(1999) ⇎ ⟦B⟧rfc3390(2002) ⇎ ⟦C⟧rfc5681(2009) ⇎ ⟦D⟧rfc6928(2013, Experimental) ⇎ ⟦E⟧rfc9002(2021, QUIC)。
采集侧一律用正则(re.findall / (?<!…) 前后瞻); 键名一律 [a-z0-9_]（门槛的 B62V('…') 引用式只认这个字符集）:
星号/逗号/括号都换成词形, 如 lit_4smss='4*SMSS', lit_c14720='14,720', lit_p1='(1)', lit_minp='min ('。
抓取时刻、rfc-editor.org 现行状态页、勘误表是否挂新版都不可由在库文件判定, 不进这张表。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NL = u'\n'
D = u'corpus/raw/tcpiw/'
TAGS = (u'A', u'B', u'C', u'D', u'E')
PATH = [D + u'rfc2581.txt', D + u'rfc3390.txt', D + u'rfc5681.txt', D + u'rfc6928.txt', D + u'rfc9002.txt']
N = 5
G = {}
REC = []


def put(k, v, note=u''):
    G[k] = v
    REC.append((k, note))


RB = [open(p, 'rb').read() for p in PATH]
T = [r.decode('utf-8-sig') for r in RB]
LOW = [t.lower() for t in T]
FO = [u' '.join(t.split()) for t in T]
FOL = [x.lower() for x in FO]
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
put('nonascii', [len([c for c in t if ord(c) > 127]) for t in T], u'')
put('bom', [1 if r[:3] == b'\xef\xbb\xbf' else 0 for r in RB], u'UTF-8 BOM')
def is_hdr(l):
    return bool(re.match(r'^RFC \d{4} +\S', l))


def is_foot(l):
    s = l.strip()
    return bool(re.search(r'\[Page \d+\]$', s) or re.search(r'Page \d+$', s))


put(u'hdr', [len([l for l in L if is_hdr(l)]) for L in LST], u'页眉行')
put(u'foot', [len([l for l in L if is_foot(l)]) for L in LST], u'页脚行')
put(u'foot_brk', [len([l for l in L if re.search(r'\[Page \d+\]$', l.strip())]) for L in LST], u'方括号式页脚')
put(u'foot_old', [len([l for l in L if re.search(r'Page \d+$', l.strip())
                       and not re.search(r'\[Page \d+\]$', l.strip())]) for L in LST], u'旧式页脚')
put(u'pagelines', [h + f for h, f in zip(G['hdr'], G['foot'])], u'')
put(u'hdr_title', [len([l for l in L if is_hdr(l) and u'Initial Window' in l]) for L in LST],
    u'页眉里印着标题“Initial Window”的行数')
put(u'iw_word_nos', [len(re.findall(u'(?i)initial window',
                                    NL.join([l for l in L if not (is_hdr(l) or is_foot(l))]))) for L in LST],
    u'去壳面的 initial window 出现处')
put('sig_sha256_16', [hashlib.sha256(r).hexdigest()[:16] for r in RB], u'采集侧用 sha256; 建条目侧换 blake2b 另立键')
put('sig_distinct', len(set(G['sig_sha256_16'])), u'')

# ---- 字面出现处(子串) ----
LITK = {u'4380': u'4380', u'2190': u'2190', u'1095': u'1095', u'14600': u'14600', u'14720': u'14720',
        u'c14600': u'14,600', u'c14720': u'14,720', u'1500': u'1500', u'1460': u'1460', u'1200': u'1200',
        u'333': u'333', u'4k': u'4K', u'2smss': u'2*SMSS', u'4smss': u'4*SMSS', u'2mss': u'2*MSS',
        u'4mss': u'4*MSS', u'10mss': u'10*MSS', u'2sp_smss': u'2 * SMSS', u'3sp_smss': u'3 * SMSS',
        u'4sp_smss': u'4 * SMSS', u'minp': u'min (', u'maxp': u'max (', u'p1': u'(1)'}
for k, s in sorted(LITK.items()):
    put(u'lit_' + k, [t.count(s) for t in T], u'字面 %r' % s)

# ---- 独立数 token(前不接数字或逗号句点、后不接数字) ----
for k in (u'4380', u'2190', u'1095', u'14600', u'14720', u'1500', u'1460', u'1200'):
    put(u'tok_' + k, [len(re.findall(u'(?<![\\d,.])' + k + u'(?![\\d])', t)) for t in T], u'')
put(u'tok_c14720', [len(re.findall(u'(?<![\\d,.])14,720', t)) for t in T], u'')
put(u'tok_c14600', [len(re.findall(u'(?<![\\d,.])14,600', t)) for t in T], u'')
for k in (u'14600', u'14720', u'1460'):
    put(u'subgap_' + k, [G[u'lit_' + k][i] - G[u'tok_' + k][i] for i in range(N)], u'子串−独立数')
put(u'bare_only_14600', [G[u'lit_14600'][i] - G[u'lit_c14600'][i] for i in range(N)], u'不带千分位的 14600')
put(u'comma_only_14720', [G[u'lit_c14720'][i] - G[u'lit_14720'][i] for i in range(N)], u'只带千分位的 14720')

# ---- 数值带: 两端各取一份面内读数(B/C 的最矮阈值 ⇎ E 的封顶值) ----
NUM = re.compile(u'(?<![\\d,.])(\\d{4,5})(?![\\d])')
put(u'nb_lo', 1095, u'下界=B/C 表里最矮的一枚阈值')
put(u'nb_hi', 14720, u'上界=21 QUIC 的封顶值')
for i, tg in enumerate(TAGS):
    vs = sorted(set(int(m.group(1)) for m in NUM.finditer(T[i]) if 1095 <= int(m.group(1)) <= 14720))
    put(u'numband_' + tg.lower(), vs, u'')
    put(u'numband_n_' + tg.lower(), len(vs), u'')

# ---- 规则窗口: 从规范句回溯到最近小节标题, 再到下一节标题 ----
HEAD = re.compile(r'^\s*(\d+(?:\.\d+)*)\.?\s+\S')
RULE = [u'IW, the initial value of cwnd, MUST be less', u'The upper bound for the initial window is given more precisely',
        u'IW, the initial value of cwnd, MUST be set', u'More precisely, the upper bound for the initial window',
        u'Initial and Minimum Congestion Window']
SECW, SECH, SECLEN = [], [], []
for i in range(N):
    ls = LST[i]
    hits = [n for n, l in enumerate(ls) if RULE[i] in l]
    if not hits:
        SECW.append((0, 0)); SECH.append(u''); SECLEN.append(0); continue
    r = hits[-1]
    a = None
    for n in range(r, -1, -1):
        m = HEAD.match(ls[n])
        if m and len(ls[n].strip()) > 3:
            a = n; break
    b = len(ls)
    if a is None:
        a = r
    for n in range(r + 1, len(ls)):
        m = HEAD.match(ls[n])
        if m and ls[n].strip()[:len(ls[a].strip())] != ls[a].strip()[:len(ls[n].strip())]:
            b = n; break
    SECW.append((a, b)); SECLEN.append(len(NL.join(ls[a:b])))
    SECH.append(ls[a].strip()[:60] if a < len(ls) else u'')
put(u'sec_w', list(SECW), u'')
put(u'sec_len', SECLEN, u'')
for i, tg in enumerate(TAGS):
    put(u'sec_len_' + tg.lower(), SECLEN[i], u'')
    put(u'sec_head_' + tg.lower(), SECH[i], u'')
WINS = [(u'4380', u'4380'), (u'2190', u'2190'), (u'1095', u'1095'), (u'14600', u'14600'),
        (u'c14720', u'14,720'), (u'minp', u'min ('), (u'maxp', u'max (')]
for k, s in WINS:
    put(u'secw_' + k, [T[i][len(NL.join(LST[i][:SECW[i][0]])) + 1: len(NL.join(LST[i][:SECW[i][1]])) + 1].count(s)
        if SECW[i][1] > SECW[i][0] else 0 for i in range(N)], u'')
    put(u'outw_' + k, [G[u'lit_' + k][i] - G[u'secw_' + k][i] for i in range(N)], u'')

# ---- 字面窗(正则族, 采集侧) ----
W = [(u'min4', u'min \\( ?(4|10)\\*(MSS|SMSS)'), (u'cap4380', u'max \\( ?2\\*(MSS|SMSS), ?4380'),
     (u'cap14600', u'max \\( ?2\\*(MSS|SMSS), ?14600'), (u'ten_mds', u'ten times the maximum datagram size'),
     (u'seg10', u'(?:10|ten) segments'), (u'iw_word', u'initial window'),
     (u'two_smss', u'(?:less than or equal to|MUST NOT be more than) ?2\\*(SMSS|MSS)'),
     (u'tier2190', u'2190 bytes'), (u'tier1095', u'1095 bytes'),
     (u'dont_allow', u'We do NOT allow this change'), (u'udp8', u'8-byte overhead'),
     (u'tcp20', u'20-byte overhead'), (u'large_of', u'the larger of'),
     (u'cite6928', u'RFC ?6928'), (u'cite3390', u'RFC ?3390')]
for k, rx in W:
    r = re.compile(rx, re.I if k in (u'ten_mds', u'seg10', u'iw_word', u'large_of') else 0)
    put(u'w_' + k, [len(r.findall(t)) for t in T], u'/\\%s\\/' % rx)
    put(u'w_' + k + u'_ci', [len(re.compile(rx, re.I).findall(t)) for t in T], u'')
put(u'iw_word_gap', [G[u'w_iw_word'][i] - G[u'iw_word_nos'][i] for i in range(N)],
    u'含壳面 − 去壳面 = 页眉贡献的出现处')

# ---- 单空格档 ⇎ 折平档 ----
SN = [(u'min4', u'min (4*'), (u'min10', u'min (10*'), (u'cap4380', u'max (2*MSS, 4380'),
      (u'cap14600', u'max (2*MSS, 14600)'), (u'seg10', u'10 segments'), (u'two_smss', u'2*SMSS'),
      (u's4smss', u'4*SMSS'), (u's4mss', u'4*MSS'), (u'dont_allow', u'We do NOT allow this change'),
      (u'large_of', u'the larger of'), (u'udp8', u'8-byte overhead'), (u'tcp20', u'20-byte overhead'),
      (u'ten_times', u'ten times the maximum datagram size'), (u'iw_of', u'IW, the initial value of cwnd')]
for k, s in SN:
    a = [t.count(s) for t in T]
    b = [x.count(s) for x in FO]
    put(u's_' + k, a, u'原面 %r' % s)
    put(u's_' + k + u'_fold', b, u'折平 %r' % s)
    put(u'wrap_gap_' + k, [b[i] - a[i] for i in range(N)], u'折平−原面')

# ---- 语汇 ----
WK = [(u'mss', u'MSS'), (u'smss', u'SMSS'), (u'mds', u'max_datagram_size'), (u'datagram', u'datagram'),
      (u'iw', u'IW'), (u'cwnd', u'cwnd'), (u'initwin_lower', u'initial window'),
      (u'initwin_caps', u'Initial Window'), (u'icw', u'initial congestion window'),
      (u'slow_start', u'slow start'), (u'slowstart_hy', u'Slow-Start'), (u'slowstart_flat', u'SlowStart')]
for k, s in WK:
    put(u'v_' + k, [t.count(s) for t in T], u'')
put(u'v_smss_ci', [len(re.findall(u'SMSS', t, re.I)) for t in T], u'')
put(u'v_iw_word', [len(re.findall(u'(?i)\\binitial\\s+window\\b', t)) for t in T], u'')

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
      (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'), (u'issn_hdr', u'ISSN:')]
for k, s in HK:
    put(k, [t.count(s) for t in T], u'')
put(u'obsoleted_by', [len(re.findall(u'(?i)obsoleted by', t)) for t in T], u'')
put(u'errata', [len(re.findall(u'(?i)errata', t)) for t in T], u'')
for n in (u'2581', u'3390', u'5681', u'6928', u'9002', u'2414', u'2001', u'2988', u'6298', u'1122'):
    put(u'cite_' + n, [len(re.findall(u'RFC ?' + n, t)) for t in T], u'')

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
    put(u'union_abcd' + suf, len(S[0] | S[1] | S[2] | S[3]), u'')
    put(u'only_c' + suf, len(S[2] - S[0] - S[1] - S[3]), u'')
    put(u'only_d' + suf, len(S[3] - S[0] - S[1] - S[2]), u'')
    put(u'only_e' + suf, len(S[4] - S[0] - S[1] - S[2] - S[3]), u'')
    put(u'share_bc_plus' + suf, len((S[1] & S[2] & S[3]) | (S[1] & S[2] & S[4])), u'')

# ---- B ⇎ C 同阈值不同形状: 三档表逐行 ----
TB = [l.rstrip() for l in LST[1] if (u'4380' in l or u'1095' in l or u'2190' in l) and len(l.strip()) > 10]
TC = [l.rstrip() for l in LST[2] if (u'1095' in l or u'2190' in l) and len(l.strip()) > 10]
put(u'tier_lines_b', [len(TB), TB], u'')
put(u'tier_lines_c', [len(TC), TC], u'')
put(u'tier_norm_same', len(set(NRM(x) for x in TB) & set(NRM(x) for x in TC)), u'两份档位行归一后交集')
for k, s in ((u'const_cap', u'win <= 4380'), (u'grow_cap', u'3 * SMSS'), (u'ifparen', u'If (MSS'),
             (u'ifsmss', u'If SMSS'), (u'ifsmsq', u'if SMSS'), (u'lesscap', u'less than or equal to 2*SMSS')):
    put(u'tier_' + k, [t.count(s) for t in T], u'')
put(u'arith_caps', [4380, 14600, 14720], u'三份文书各自的上限常数')
put(u'arith_tiers', [1095, 2190, 2190], u'')
put(u'arith_check', [4380 == 3 * 1460, 14600 == 10 * 1460, 14720 == 14600 + 10 * (20 - 8),
                     1095 == 4380 // 4, 2190 == 4380 // 2, 6570 - 4380 == 2190], u'')

# ---- 锚候选行 ----
NLITS = (u'4380', u'2190', u'1095', u'14600', u'14,720', u'14,600', u'SMSS', u'MSS', u'IW')
put(u'num_lines', [len([l for l in L if len(l.strip()) >= 55 and any(x in l for x in NLITS)]) for L in LST], u'')
for i, tg in enumerate(TAGS):
    put(u'num_lines_' + tg.lower(), G[u'num_lines'][i], u'')

ORDER = [k for k, _ in REC]
MISS = [k for k in ORDER if not re.match(r'^[a-z0-9_]+$', k)]
io.open(u'corpus/_b62meas.json', 'w', encoding='utf-8').write(
    json.dumps(dict((k, G[k]) for k in ORDER), ensure_ascii=False, indent=0, sort_keys=True))
print(u'非 [a-z0-9_] 键名: %s' % (MISS or u'无'))
for tg, s in zip(TAGS, (u'2581', u'3390', u'5681', u'6928', u'9002')):
    print(u'%s=rfc%s' % (tg, s), end=u' ')
print()
for k in (u'bytes', u'chars', u'lines', u'nonblank', u'maxlen', u'trail', u'cr', u'nonascii', u'bom',
          u'hdr', u'foot', u'foot_brk', u'foot_old', u'pagelines', u'sig_distinct',
          u'hdr_title', u'iw_word_nos', u'iw_word_gap'):
    print(u'%-22s %s' % (k, G[k]))
print(u'--- 数字字面(子串出现处) ---')
for k in (u'4380', u'2190', u'1095', u'14600', u'14720', u'c14600', u'c14720', u'1500', u'1460', u'1200', u'333', u'4k'):
    print(u'%-22s %s' % (u'lit_' + k, G[u'lit_' + k]))
print(u'--- 独立数 token ---')
for k in (u'4380', u'2190', u'1095', u'14600', u'14720', u'1500', u'1460', u'1200', u'c14720', u'c14600'):
    print(u'%-22s %s' % (u'tok_' + k, G[u'tok_' + k]))
for k in (u'14600', u'14720', u'1460'):
    print(u'%-22s %s' % (u'subgap_' + k, G[u'subgap_' + k]))
print(u'%-22s %s' % (u'bare_only_14600', G[u'bare_only_14600']))
print(u'%-22s %s' % (u'comma_only_14720', G[u'comma_only_14720']))
print(u'--- 算式家族字面 ---')
for k in (u'2smss', u'4smss', u'2mss', u'4mss', u'10mss', u'2sp_smss', u'3sp_smss', u'4sp_smss', u'minp', u'maxp', u'p1'):
    print(u'%-22s %s' % (u'lit_' + k, G[u'lit_' + k]))
print(u'--- 数值带成员数 ---')
print(u'%-22s %s' % (u'numband_n', [G[u'numband_n_' + x.lower()] for x in TAGS]))
for tg in TAGS:
    print(u'  %s: %s' % (tg, G[u'numband_' + tg.lower()]))
print(u'--- 规范窗 ---')
print(u'%-22s %s' % (u'sec_w', G[u'sec_w']))
print(u'%-22s %s' % (u'sec_len', G[u'sec_len']))
for tg in TAGS:
    print(u'  %s 标题: %s' % (tg, G[u'sec_head_' + tg.lower()]))
for k, _ in WINS:
    print(u'%-22s %s / out %s' % (u'secw_' + k, G[u'secw_' + k], G[u'outw_' + k]))
print(u'--- 正则窗档 ---')
for k, rx in W:
    print(u'%-22s %s  ci %s' % (u'w_' + k, G[u'w_' + k], G[u'w_' + k + u'_ci']))
print(u'--- 单空格档 ⇎ 折平档 ---')
for k, s in SN:
    print(u'%-18s s %s fold %s gap %s' % (k, G[u's_' + k], G[u's_' + k + u'_fold'], G[u'wrap_gap_' + k]))
print(u'--- 语汇 ---')
for k, s in WK:
    print(u'%-22s %s' % (u'v_' + k, G[u'v_' + k]))
print(u'%-22s %s' % (u'v_smss_ci', G[u'v_smss_ci']))
print(u'%-22s %s' % (u'v_iw_word', G[u'v_iw_word']))
print(u'--- 义务词 ---')
for w in (u'must_not', u'must', u'should_not', u'should', u'may', u'required'):
    print(u'%-22s %s' % (u'u_' + w, G[u'u_' + w]))
print(u'%-22s %s / low %s' % (u'oblig_up', G[u'oblig_up'], G[u'oblig_low']))
for w in (u'must', u'should', u'may'):
    print(u'%-22s %s' % (u'l_' + w, G[u'l_' + w]))
print(u'%-22s %s / boiler %s' % (u'rfc2119_ref', G[u'rfc2119_ref'], G[u'key_words_boiler']))
print(u'--- 身份 ---')
for k, s in HK:
    print(u'%-22s %s' % (k, G[k]))
print(u'%-22s %s' % (u'obsoleted_by', G[u'obsoleted_by']))
print(u'%-22s %s' % (u'errata', G[u'errata']))
for n in (u'2581', u'3390', u'5681', u'6928', u'9002', u'2414', u'2001', u'2988', u'6298', u'1122'):
    print(u'%-22s %s' % (u'cite_' + n, G[u'cite_' + n]))
print(u'--- 搬运账 ---')
for suf in (u'_nos', u''):
    print(u'%-22s %s' % (u'lines_ge40' + suf, G[u'lines_ge40' + suf]))
    for a in range(N):
        for b in range(a + 1, N):
            kk = u'share_%s%s%s' % (TAGS[a].lower(), TAGS[b].lower(), suf)
            print(u'  %s = %d' % (kk, G[kk]))
    print(u'%-22s %s  only_c/d/e %s/%s/%s  bc+ %s' % (
        u'union_abcd' + suf, G[u'union_abcd' + suf], G[u'only_c' + suf], G[u'only_d' + suf],
        G[u'only_e' + suf], G[u'share_bc_plus' + suf]))
print(u'--- 档位表 ---')
print(u'tier_lines_b %d 行: %s' % (G[u'tier_lines_b'][0], G[u'tier_lines_b'][1]))
print(u'tier_lines_c %d 行: %s' % (G[u'tier_lines_c'][0], G[u'tier_lines_c'][1]))
print(u'%-22s %s' % (u'tier_norm_same', G[u'tier_norm_same']))
for k in (u'const_cap', u'grow_cap', u'ifparen', u'ifsmss', u'ifsmsq', u'lesscap'):
    print(u'%-22s %s' % (u'tier_' + k, G[u'tier_' + k]))
print(u'%-22s %s' % (u'arith_check', G[u'arith_check']))
print(u'--- 锚候选行 ---')
print(u'%-22s %s' % (u'num_lines', G[u'num_lines']))
print(u'已写 corpus/_b62meas.json ｜ 键 %d' % len(ORDER))
