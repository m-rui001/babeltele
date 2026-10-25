# -*- coding: utf-8 -*-
"""采集遍(B98, 第一套实现): “Retry-After 到底该写多久、谁能省掉它”——五份一手文书各答一遍。
2616(1999 §14.37: 两式初刻 HTTP-date|delta-seconds, 单位口径写 “integer number of seconds (in decimal)
after the time of the response”; 503 只 MAY be indicated, 且独家规定 If no Retry-After is given 之后客户端怎么办)
⇎ 6585(2012 §4: 429 引入者, “MAY include a Retry-After header indicating how long to wait”, 例面只印
3600 秒一种尺, 全文不出现 503 也不出现 HTTP-date) ⇎ 7231(2014 §7.1.3: 单位改名 delay-seconds, 口径写
“a number of seconds to delay after the response is received”, 503 MAY send ⇎ 413 SHOULD generate 两级可省性,
例面 120 并自证换算 “the delay is 2 minutes”) ⇎ 9110(2022 §10.2.3: 两式仍在、语法行逐字照抄 7231, 口径措辞
换成 “after receiving the response”, 429 一字不提) ⇎ curl --retry 文档(实现/客户端指导一手: 全文不写 HTTP-date,
自家退避 first waits one second、doubles、until it reaches 10 minutes, 服务端 Retry-After 可 override)。

本遍八处机制(全部与建条侧 _mkB98.py 相反, 键集口径一致后逐键对账落 corpus/_b98meas.json):
①切句: 本遍 (?<=[.!?]) 正则切句 ⇎ 建条侧逐字符扫句界; ②字面针: 本遍整串 re.findall ⇎ 建条侧游标 find 环;
③共句判定: 本遍集合档(set 交并差) ⇎ 建条侧词频档(Counter 直方图); ④行数账: 本遍 split('\\n') ⇎ 建条侧 splitlines;
⑤Retry-After 定义段: 本遍行号窗口定界(首末行号切片) ⇎ 建条侧块定界(面上偏移取块);
⑥面偏移→原行: 本遍累积长度表 + bisect ⇎ 建条侧逐字符行号表;
⑦分钟⇎秒换算: 本遍一处建表两次查表 ⇎ 建条侧两处现算; ⑧节标题识别: 本遍邻句判断(邻行为空且本行含节号原文)
⇎ 建条侧正则头检测。所有数字本遍量出落 JSON, 一枚不手打。"""
import io, json, re, sys
from bisect import bisect_right

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'2616', u'6585', u'7231', u'9110', u'curl']
NSRC = 5
PATH = [u'corpus/raw/httpretry/rfc2616.txt', u'corpus/raw/httpretry/rfc6585.txt',
        u'corpus/raw/httpretry/rfc7231.txt', u'corpus/raw/httpretry/rfc9110.txt',
        u'corpus/raw/retryafter98/curl_retry.md']
M = {}


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
RAWL = [t.split(NL) for t in T]  # 机制④: split('\n'), 与建条侧 splitlines 相对
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]


def pnorm(s):
    return u' '.join(s.lower().split())


def cnt_re(hay, nd):
    """机制②本遍那把: 整串转义正则计数(建条侧游标环)。"""
    return len(re.findall(re.escape(nd), hay))


# ---------- 0. 面量 ----------
M['face_bytes'] = [len(B[i]) for i in range(NSRC)]
M['face_cp'] = [len(T[i]) for i in range(NSRC)]
M['n_cr'] = [T[i].count(u'\r') for i in range(NSRC)]
M['n_lf'] = [T[i].count(u'\n') for i in range(NSRC)]
M['n_ff'] = [T[i].count(u'\x0c') for i in range(NSRC)]
M['n_splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
M['n_splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
M['n_blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
M['n_nonempty'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
M['maxlen_row'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
M['n_tab'] = [T[i].count(u'\t') for i in range(NSRC)]
M['nonascii_cp'] = [sorted({ord(c) for c in T[i] if ord(c) > 127}) for i in range(NSRC)]
M['ends_lf'] = [1 if T[i].endswith(u'\n') else 0 for i in range(NSRC)]
# splitlines 账: splitlines = LF+FF+1−(尾换行?1:0); split('\n') = LF+1 ⇒ 差 = FF − ends_lf(\x0b 等另计)
M['splitlines_minus_splitnl'] = [M['n_splitlines'][i] - M['n_splitnl'][i] for i in range(NSRC)]
M['n_vt'] = [T[i].count(u'\x0b') for i in range(NSRC)]
for i in range(NSRC):
    pred = M['n_ff'][i] - M['ends_lf'][i] + M['n_vt'][i]
    assert M['splitlines_minus_splitnl'][i] == pred, (i, M['splitlines_minus_splitnl'][i], pred)

FOLD = [pnorm(T[i]) for i in range(NSRC)]


# ---------- 1. 壳行谓词: 机制⑧邻句判断(不跑节头正则) ----------
def prev_ne(i, k):
    j = k - 1
    while j >= 0 and L[i][j].strip() == u'':
        j -= 1
    return L[i][j].strip() if j >= 0 else u''


def is_shell_pick(i, k):
    """页壳两式全凭邻居: [Page 眉行(邻行空/换页) ⇎ 眉行的下一非空行(“RFC nnn …”年行);
       目录点线行单列 toc 档; curl 壳 = 两条 --- 之间(front matter)按邻句递推。"""
    x = L[i][k]
    s = x.strip()
    if not s:
        return u''
    if u'[Page' in s and (ord(s[0]) == 12 or k + 1 >= len(L[i]) or L[i][k + 1].strip() == u''):
        return u'page'
    if u'[Page' in prev_ne(i, k):
        return u'page'
    if re.match(u'^\\s*\\d+\\s', x) and re.search(u'\\.{4,}\\d+$', s):
        return u'toc'
    return u''


SHELL = [[k for k in range(len(L[i])) if is_shell_pick(i, k) == u'page'] for i in range(NSRC)]
TOCR = [[k for k in range(len(L[i])) if is_shell_pick(i, k) == u'toc'] for i in range(NSRC)]
M['shell_rows'] = [len(SHELL[i]) for i in range(NSRC)]
M['toc_rows'] = [len(TOCR[i]) for i in range(NSRC)]
M['body_rows'] = [M['n_nonempty'][i] - M['shell_rows'][i] - M['toc_rows'][i] for i in range(NSRC)]
# curl front matter 另走邻句尺: 第一条 --- 行 ⇎ 第二条 --- 行(含)之间
if L[4][0].strip() == u'---':
    fm_end = next(k for k in range(1, len(L[4])) if L[4][k].strip() == u'---')
    FMROWS = list(range(0, fm_end + 1))
else:
    FMROWS = []
M['curl_fm_rows'] = len(FMROWS)
assert len(FMROWS) >= 10 and L[4][fm_end].strip() == u'---', u'curl front matter 邻句尺失效'

# 摘壳折平 ⇎ 摘壳去标记折平(9110 的 *_..._*、| 引用块逐行剥, 6585 的 HTML 尖括号壳)
def strip_markup(i, txt):
    out = []
    for line in txt.split(NL):
        if line.lstrip().startswith(u'|'):
            line = line.lstrip()[1:]
        line = line.replace(u'*_', u'').replace(u'_*', u'')
        line = re.sub(u'</?[a-zA-Z][^>]*>', u'', line)
        out.append(line)
    return NL.join(out)


NSFOLD = [pnorm(u' '.join(L[i][k] for k in range(len(L[i])) if k not in set(SHELL[i]))) for i in range(NSRC)]
MKFOLD = [pnorm(strip_markup(i, NL.join(L[i][k] for k in range(len(L[i])) if k not in set(SHELL[i]))))
          for i in range(NSRC)]

# ---------- 2. 面偏移→原行: 机制⑥累积长度表 + bisect ----------
def cum_of(i):
    cum, acc = [], 0
    for x in L[i]:
        acc += len(x) + 1
        cum.append(acc)
    return cum


CUM = [cum_of(i) for i in range(NSRC)]


def off_line(i, off):
    return bisect_right(CUM[i], off)


# ---------- 3. Retry-After 定义段: 机制⑤行号窗口定界 ----------
WIN_TITLES = [u'14.37 Retry-After', u'4.  429 Too Many Requests', u'7.1.3.  Retry-After',
              u'10.2.3.  Retry-After', u'# `--retry`']
WIN_ENDS = [u'14.38 Server', u'5.  431 Request Header Fields Too Large', u'7.1.4.  Vary',
            u'10.2.4.  Server', None]


def find_row(i, nd, frm=0):
    """机制⑧(标题判定): 邻句尺——标题行必须顶格起针且下一行是空行(正文节头形状), 不跑节号正则。"""
    for k in range(frm, len(L[i])):
        if L[i][k].startswith(nd):
            nxt = L[i][k + 1] if k + 1 < len(L[i]) else u''
            if nxt.strip() == u'':
                return k
    return -1


WIN = []
for i in range(NSRC):
    a = find_row(i, WIN_TITLES[i])
    assert a >= 0, (i, WIN_TITLES[i])
    b = find_row(i, WIN_ENDS[i], a + 1) if WIN_ENDS[i] else len(L[i])
    assert b > a, (i, b)
    WIN.append((a, b))
M['win_start'] = [w[0] for w in WIN]
M['win_end'] = [w[1] for w in WIN]
M['win_rows'] = [w[1] - w[0] for w in WIN]
M['win_text'] = [NL.join(L[i][WIN[i][0]:WIN[i][1]]) for i in range(NSRC)]
M['win_cp'] = [len(M['win_text'][i]) for i in range(NSRC)]
# 摘壳窗: 窗内去掉页壳行后的正文(句账与共句账都走这一档, 壳混进句里就比不出正文)
SH = [set(SHELL[i]) for i in range(NSRC)]
M['win_ns_text'] = [NL.join(L[i][k] for k in range(WIN[i][0], WIN[i][1]) if k not in SH[i]) for i in range(NSRC)]
M['win_ns_rows'] = [len(M['win_ns_text'][i].split(NL)) for i in range(NSRC)]
M['win_shell_rows'] = [M['win_rows'][i] - M['win_ns_rows'][i] for i in range(NSRC)]

# ---------- 4. 切句: 机制①正则切句(建条侧逐字符) ----------
def sents(txt):
    parts = re.split(u'(?<=[.!?])\\s+', u' '.join(txt.split()))
    return [pnorm(p) for p in parts if pnorm(p)]


# ---------- 5. 针账(全份折平档 ⇎ 窗口行档) ----------
NEEDLES = [
    u'Retry-After', u'retry-after', u'RETRY-After', u'HTTP-date', u'delta-seconds', u'delay-seconds',
    u'either an HTTP-date or an integer number', u'either an HTTP-date or a number of seconds to delay after',
    u'after the time of the response', u'after the response is received', u'after receiving the response',
    u'non-negative decimal integer', u'(in decimal)', u'Retry-After: 120', u'Retry-After: 3600',
    u'Retry-After: Fri, 31 Dec 1999 23:59:59 GMT', u'the delay is 2 minutes',
    u'MAY include a Retry-After', u'MAY send a Retry-After', u'MAY be indicated in a Retry-After',
    u'SHOULD generate a Retry-After', u'MUST send a Retry-After', u'MUST include a Retry-After',
    u'MUST generate a Retry-After', u'ought to wait', u'is asked to wait', u'is asked wait',
    u'If no Retry-After is given', u'can be used with a 503', u'MAY also be used',
    u'complies with the Retry-After', u'can override the retry delay', u'optional; servers cannot be required',
    u'does not imply that a server has to use it', u'first waits one second',
    u'doubles the waiting time until it reaches 10 minutes', u'limit the total retry time',
]
ND = {}
for nd in NEEDLES:
    key = u'nd_' + re.sub(u'[^a-z0-9]+', u'_', nd.lower()).strip(u'_')
    ND[key] = nd
    M[key] = [cnt_re(FOLD[i], pnorm(nd)) for i in range(NSRC)]
M['needle_n'] = len(NEEDLES)
# 最宽档: 未摘壳未去标记的全份折平上跑 MUST×Retry-After 同句对(断“没有一份规定必须写”之前先跑最宽档)
ra_must_wide = []
for i in range(NSRC):
    hits = 0
    for s in sents(T[i]):
        if u'retry-after' in s and u'must' in s:
            hits += 1
    ra_must_wide.append(hits)
M['ra_must_sent_wide'] = ra_must_wide

# 上限谓词最宽档: 全份折平里与 Retry-After 同句出现的界词
CAPWORDS = [u'maximum', u'at most', u'no more than', u'upper bound', u'ceiling', u'cap']
M['ra_capword_sent_wide'] = [
    sum(1 for s in sents(T[i]) if u'retry-after' in s and any(c in s for c in CAPWORDS))
    for i in range(NSRC)]

# ---------- 6. Retry-After 计账: 总数⇎窗内⇎窗外(两路独立) ----------
M['ra_total'] = [cnt_re(T[i], u'Retry-After') for i in range(NSRC)]
M['ra_win'] = [cnt_re(M['win_text'][i], u'Retry-After') for i in range(NSRC)]
OUT = []
for i in range(NSRC):
    seg = NL.join(L[i][:WIN[i][0]] + L[i][WIN[i][1]:])
    OUT.append(cnt_re(seg, u'Retry-After'))
M['ra_out'] = OUT
M['ra_decomp_diff'] = [M['ra_total'][i] - M['ra_win'][i] - M['ra_out'][i] for i in range(NSRC)]
for i in range(NSRC):
    assert M['ra_decomp_diff'][i] == 0, i
M['ra_rows'] = [len([k for k in range(len(L[i])) if u'Retry-After' in L[i][k]]) for i in range(NSRC)]
M['ra_caseless'] = [cnt_re(T[i], u'Retry-After') + cnt_re(T[i], u'Retry-after') +
                    cnt_re(T[i], u'retry-after') + cnt_re(T[i], u'RETRY-AFTER') for i in range(NSRC)]
# ---------- 7. 数值现读(窗口内 “Retry-After: <digits>” ⇎ curl 的 spelled one/10) ----------
M['ex_ra_secs'] = []
for i in range(NSRC):
    m = re.search(u'Retry-After: (\\d+)\\b', u' '.join(M['win_text'][i].split()))
    M['ex_ra_secs'].append(int(m.group(1)) if m else -1)
assert [M['ex_ra_secs'][i] for i in (0, 1, 2, 3)] == [120, 3600, 120, 120]
mins = []
for i in range(NSRC):
    m = re.search(u'delay is (\\d+) minutes', u' '.join(M['win_text'][i].split()))
    mins.append(int(m.group(1)) if m else -1)
M['ex_ra_mins'] = mins
# 机制⑦: 单位换算一处建表, 两处查表(建条侧两处现算)
UNIT = {}
for i in range(NSRC):
    if M['ex_ra_secs'][i] > 0 and M['ex_ra_mins'][i] > 0:
        UNIT[u'minute'] = M['ex_ra_secs'][i] // M['ex_ra_mins'][i]
assert u'minute' in UNIT and UNIT[u'minute'] == 60
M['unit_minute_from_doc'] = [UNIT[u'minute'] if M['ex_ra_mins'][i] > 0 else -1 for i in range(NSRC)]
curlw = pnorm(M['win_text'][4])
curlm = re.search(u'reaches (\\d+) minutes', curlw)
M['curl_cap_minutes'] = int(curlm.group(1))
M['curl_cap_secs'] = M['curl_cap_minutes'] * UNIT[u'minute']  # 第一次查表
# spelled 数词只进查表档: one→1 是词形读数, 不是手填
NUMWORD = {u'one': 1, u'two': 2}
mw = re.search(u'first waits (one|two) second', curlw)
M['curl_first_secs'] = NUMWORD[mw.group(1)]
M['ratio_6585_over_120'] = M['ex_ra_secs'][1] // M['ex_ra_secs'][2]
M['ratio_3600_per_hour'] = -(-M['ex_ra_secs'][1] // UNIT[u'minute'])  # 第二次查表: 3600s=60min? 此处只登记分钟数
assert M['ratio_3600_per_hour'] == 60
M['num_hour_rate'] = int(re.search(u'I only allow (\\d+) requests', M['win_text'][1]).group(1))
assert M['num_hour_rate'] == 50
codes = None
for s in sents(M['win_text'][4]):
    if u'transient error means' in s:
        codes = s
assert codes is not None
M['curl_transient_codes'] = len(re.findall(u'\\b[45]\\d\\d\\b', codes))
M['num_1999'] = [cnt_re(FOLD[i], u'1999') for i in range(NSRC)]
M['rfcref_2616_in_9110'] = cnt_re(FOLD[3], u'rfc 2616') + cnt_re(FOLD[3], u'rfc2616')
# 义务词大写档(案敏感, 只在窗口原文上数)
M['win_caps_may'] = [cnt_re(M['win_ns_text'][i], u'MAY') for i in range(NSRC)]
M['win_caps_should'] = [cnt_re(M['win_ns_text'][i], u'SHOULD') for i in range(NSRC)]
M['win_caps_must'] = [cnt_re(M['win_ns_text'][i], u'MUST') for i in range(NSRC)]
M['win_caps_ought'] = [cnt_re(M['win_ns_text'][i], u'ought') for i in range(NSRC)]
M['hd_win'] = [cnt_re(M['win_ns_text'][i], u'HTTP-date') for i in range(NSRC)]
M['gram_slash'] = [cnt_re(T[i], u'Retry-After = HTTP-date / delay-seconds') for i in range(NSRC)]
M['gram_colon'] = [cnt_re(T[i], u'Retry-After  = "Retry-After" ":" ( HTTP-date | delta-seconds )')
                   for i in range(NSRC)]
M['two_examples'] = [cnt_re(pnorm(M['win_ns_text'][i]), pnorm(u'Two examples of its use are')) for i in range(NSRC)]
M['n429'] = [cnt_re(T[i], u'429') for i in range(NSRC)]
M['n503'] = [cnt_re(T[i], u'503') for i in range(NSRC)]
M['n413'] = [cnt_re(T[i], u'413') for i in range(NSRC)]
M['n3xx'] = [cnt_re(T[i], u'3xx') for i in range(NSRC)]

# ---------- 8. 7231 ⇎ 9110 窗内共句: 机制③集合档 ----------
S7 = sents(M['win_ns_text'][2])
S9 = sents(M['win_ns_text'][3])
setA, setB = set(S7), set(S9)
M['cmp_sents_a'] = len(S7)
M['cmp_sents_b'] = len(S9)
M['cmp_same'] = len(setA & setB)
M['cmp_union'] = len(setA | setB)
M['cmp_only_a'] = len(setA - setB)
M['cmp_only_b'] = len(setB - setA)
assert M['cmp_same'] + M['cmp_only_a'] + M['cmp_only_b'] == M['cmp_union']
M['cmp_incl_excl_diff'] = M['cmp_sents_a'] + M['cmp_sents_b'] - M['cmp_union'] - M['cmp_same']
assert M['cmp_incl_excl_diff'] == 0
# 窗内是否逐句唯一: 句数−句种数 单独入账(集合档现量)
M['dup7'] = len(S7) - len(setA)
M['dup9'] = len(S9) - len(setB)

# ---------- 9. 反向独占针(本份>0 ⇎ 他份全0) ----------
NEG = [(0, u'delta-seconds'), (1, u'Retry-After: 3600'), (2, u'after the response is received'),
       (3, u'after receiving the response'), (4, u'first waits one second'),
       (0, u'integer number of seconds (in decimal)'), (1, u'may include a retry-after')]
M['neg_excl'] = []
for oi, nd in NEG:
    q = pnorm(nd)
    others = [cnt_re(FOLD[i], q) for i in range(NSRC) if i != oi]
    mine = cnt_re(FOLD[oi], q)
    M['neg_excl'].append([oi, mine, sum(others), 1 if (mine > 0 and sum(others) == 0) else 0])
M['neg_clean'] = sum(x[3] for x in M['neg_excl'])
M['neg_n'] = len(NEG)

# ---------- 10. 窗口可读档(行 ⇎ 折 ⇎ 摘壳 ⇎ 去标记): 12 枚跨行风险针 ----------
RISK = [u'either an HTTP-date or an integer number', u'MAY be indicated in a Retry-After',
        u'If no Retry-After is given, the client SHOULD', u'MAY include a Retry-After header indicating how long',
        u'MAY send a Retry-After header field', u'SHOULD generate a Retry-After header field to indicate',
        u'A delay-seconds value is a non-negative decimal integer',
        u'The Retry-After field value can be either an HTTP-date or a number',
        u'complies with the Retry-After: response header', u'curl complies with the Retry-After',
        u'does not imply that a server has to use it', u'optional; servers cannot be required',
        u'The value of this field can be either an HTTP-date or a number of seconds']
RISK = RISK[:12]
# 行档: 整枚针落在某一条原行内 ⇎ 折档: 全份折平可读 ⇎ 摘壳档 ⇎ 去标记档
RROW = [[1 if any(pnorm(nd) in pnorm(x) for x in L[i]) else 0 for i in range(NSRC)] for nd in RISK]
RFOLD = [[cnt_re(FOLD[i], pnorm(nd)) for i in range(NSRC)] for nd in RISK]
RSHELL = [[cnt_re(NSFOLD[i], pnorm(nd)) for i in range(NSRC)] for nd in RISK]
RMK = [[cnt_re(MKFOLD[i], pnorm(nd)) for i in range(NSRC)] for nd in RISK]
M['risk_n'] = len(RISK)
M['risk_row'] = [[RROW[j][i] for j in range(len(RISK))] for i in range(NSRC)]
M['risk_fold'] = [[RFOLD[j][i] for j in range(len(RISK))] for i in range(NSRC)]
M['risk_shell'] = [[RSHELL[j][i] for j in range(len(RISK))] for i in range(NSRC)]
M['risk_mkfree'] = [[RMK[j][i] for j in range(len(RISK))] for i in range(NSRC)]
M['risk_cut_row'] = [len([1 for j in range(len(RISK))
                          if RFOLD[j][i] > 0 and RROW[j][i] == 0]) for i in range(NSRC)]
M['risk_cut_shell'] = [len([1 for j in range(len(RISK))
                            if RSHELL[j][i] > 0 and RFOLD[j][i] == 0]) for i in range(NSRC)]
M['risk_cut_mk'] = [len([1 for j in range(len(RISK))
                         if RMK[j][i] > 0 and RSHELL[j][i] == 0]) for i in range(NSRC)]
assert sum(M['risk_cut_shell']) == 0, M['risk_cut_shell']

# ---------- 11. 句子级窗口读数 ----------
M['win_sents'] = [len(sents(M['win_ns_text'][i])) for i in range(NSRC)]
M['win_verb_rows'] = [
    len([s for s in sents(M['win_ns_text'][i])
         if re.search(u'\\b(MAY|SHOULD|MUST|ought|asked|can)\\b', s)]) for i in range(NSRC)]

# 9110 的三行“适用表” markup 增益: *_Section 10.2.3_* 针
q_tbl = pnorm(u'Retry-After Section 10.2.3')
M['tbl_9110_raw'] = cnt_re(FOLD[3], q_tbl)
M['tbl_9110_mkfree'] = cnt_re(MKFOLD[3], q_tbl)
assert M['tbl_9110_raw'] == 0 and M['tbl_9110_mkfree'] == 3
M['curl_body_cp'] = len(NL.join(L[4][FMROWS[-1] + 1:]))
M['curl_head_rows_after_fm'] = len([x for x in L[4][FMROWS[-1] + 1:] if x.strip()])

with io.open(u'corpus/_b98meas.json', 'w', encoding='utf-8') as f:
    json.dump(M, f, ensure_ascii=False, indent=1, sort_keys=True)
print(u'pick98: %d 键落盘; ra=%s; win=%s; ex=%s; cap=%s; cmp_same=%s; risk_cut_row=%s'
      % (len(M), M['ra_total'], M['win_rows'], M['ex_ra_secs'], M['ra_capword_sent_wide'],
         M['cmp_same'], M['risk_cut_row']))
