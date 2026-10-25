# -*- coding: utf-8 -*-
"""建条遍(B98, 第二套实现): “Retry-After 到底该写多久、谁能省掉它”。
键集与口径与采集遍(_pick98.py)逐枚同名同义, 八处机制全部相反:
①句界: 采集侧 (?<=[.!?])\\s+ 正则切句 ⇎ 本遍逐字符扫“句末标点+空格”(先手工折平, 不经 str.split);
②字面针: 采集侧 re.findall(re.escape) 整串扫 ⇎ 本遍游标 find 环(枚枚非重叠);
③共句判定: 采集侧集合档(set 交并差) ⇎ 本遍词频档(Counter 直方图 + 逐键查表);
④行数账与行阵: 采集侧 split('\\n') 建行阵 ⇎ 本遍 splitlines(keepends) 再按“只认 \\n 收线”重胶;
⑤定义段: 采集侧行号窗口定界(首末行号切片) ⇎ 本遍块定界(在面上 find 标题偏移、切 [a_off,b_off) 块, 行号由偏移反查);
⑥面偏移→原行: 采集侧累积长度表 + bisect ⇎ 本遍逐字符行号表(每枚字符现挂原行下标);
⑦分钟⇎秒: 采集侧一处建表两次查表 ⇎ 本遍两处各自现算(600=10×(120//2)、60=⌈3600/(120//2)⌉ 各自当场除);
⑧节标题/壳判定: 采集侧邻句判断(顶格起针+下一行空; 壳靠邻居含针) ⇎ 本遍逐行正则头检测((?m)^题面$ 整行锚、toc 一条整行正则、[Page 由 finditer 命中再按行号扩展)。
数值读数同样换尺: 采集侧 re.search 分组 ⇎ 本遍游标定位+就地吃数字串+尾词校验。
所有数字本遍量出, 与采集遍逐键对账落 corpus/_b98meas.json, 一枚不手打; 布尔门与恒等式全平才放行。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'2616', u'6585', u'7231', u'9110', u'curl']
NSRC = 5
PATH = [u'corpus/raw/httpretry/rfc2616.txt', u'corpus/raw/httpretry/rfc6585.txt',
        u'corpus/raw/httpretry/rfc7231.txt', u'corpus/raw/httpretry/rfc9110.txt',
        u'corpus/raw/retryafter98/curl_retry.md']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire98.py 把这一段 ⇎ _mk98emit.py 的 SCAN2 段机械切进 audit.py::_b98_scan)


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]


def lines_splitglue(t):
    """机制④: splitlines(keepends) 再胶回“\\n 行”。splitlines 认的所有其他界符(\\x0c 等)都留在行内。"""
    out, cur = [], u''
    for seg in t.splitlines(True):
        if seg[-1:] == NL:
            body = cur + seg[:-1]
            out.append(body[:-1] if body.endswith(u'\r') else body)
            cur = u''
        else:
            cur += seg
    if cur != u'':                                    # 末段没有 \n 收线(如面以 \x0c 收尾): 它是未 terminated 尾行
        out.append(cur[:-1] if cur.endswith(u'\r') else cur)
    elif t == u'' or t.endswith(NL):                  # 与 split('\n') 同义: 尾 \n 之后还有一枚空行
        out.append(u'')
    return out


L = [lines_splitglue(T[i]) for i in range(NSRC)]
for i in range(NSRC):
    assert NL.join(L[i]) == T[i], u'行阵回环不等于原面 ' + LBL[i]      # 只收纯 LF 面, 不中即红
    assert u'\r' not in T[i], u'面上有回车 ' + LBL[i]


def pnorm(s):
    return u' '.join(s.lower().split())


def cnt_cur(hay, nd):
    """机制②: 游标 find 环(采集侧是整串 re.findall)。"""
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def flat_chars(txt):
    """手工折平: 逐字符收词、空白压成一枚空格(采集侧借 str.split 现折)。"""
    out, k, n = [], 0, len(txt)
    while k < n:
        while k < n and txt[k].isspace():
            k += 1
        if k >= n:
            break
        if out:
            out.append(u' ')
        while k < n and not txt[k].isspace():
            out.append(txt[k])
            k += 1
    return u''.join(out)


def sents(txt):
    """机制①: 逐字符扫“句末标点+空格”切句(采集侧是一条 re.split)。"""
    face = flat_chars(txt)
    out, start, k, n = [], 0, 0, len(face)
    while k < n:
        if face[k] in u'.!?' and k + 1 < n and face[k + 1] == u' ':
            j = k + 1
            while j < n and face[j] == u' ':
                j += 1
            out.append(pnorm(face[start:k + 1]))
            start = j
            k = j
            continue
        k += 1
    if start < n:
        out.append(pnorm(face[start:n]))
    return [z for z in out if z]


# ---------- 0. 面量 ----------
F['face_bytes'] = [len(B[i]) for i in range(NSRC)]
F['face_cp'] = [len(T[i]) for i in range(NSRC)]
F['n_cr'] = [cnt_cur(T[i], u'\r') for i in range(NSRC)]
F['n_lf'] = [cnt_cur(T[i], NL) for i in range(NSRC)]
F['n_ff'] = [cnt_cur(T[i], u'\x0c') for i in range(NSRC)]
F['n_splitnl'] = [len(L[i]) for i in range(NSRC)]                      # 胶回来的行数, 口径同采集侧 split('\n')
F['n_splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]      # 这一档才用裸 splitlines
F['n_blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
F['n_nonempty'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['maxlen_row'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
F['n_tab'] = [cnt_cur(T[i], u'\t') for i in range(NSRC)]
_na = []
for i in range(NSRC):
    s = set()
    for ch in T[i]:                                                    # 逐字符收码位, 不经推导式集合档
        if ord(ch) > 127:
            s.add(ord(ch))
    _na.append(sorted(s))
F['nonascii_cp'] = _na
F['ends_lf'] = [1 if T[i].endswith(NL) else 0 for i in range(NSRC)]
F['splitlines_minus_splitnl'] = [F['n_splitlines'][i] - F['n_splitnl'][i] for i in range(NSRC)]
F['n_vt'] = [cnt_cur(T[i], u'\x0b') for i in range(NSRC)]
_pred_rows = [F['n_ff'][i] - F['ends_lf'][i] + F['n_vt'][i] for i in range(NSRC)]
F['splitlines_ledger_diff'] = [F['splitlines_minus_splitnl'][i] - _pred_rows[i] for i in range(NSRC)]
for i in range(NSRC):
    assert F['splitlines_ledger_diff'][i] == 0, (i, F['splitlines_minus_splitnl'][i], _pred_rows[i])

FOLD = [pnorm(T[i]) for i in range(NSRC)]


# ---------- 1. 壳判定: 机制⑧(逐行正则 finditer + 行号扩展, 不跑邻居谓词) ----------
PGRX = re.compile(u'\\[Page')
FFRX = re.compile(u'^\\x0c')
TORX = re.compile(u'^\\s*\\d+\\s.*\\.{4,}\\d+$')                        # 一条整行正则(采集侧拆两枚各跑一次)


def shell_sets(i):
    sl = [x.strip() for x in L[i]]
    hits = [k for k in range(len(L[i])) if sl[k] != u'' and PGRX.search(sl[k]) is not None]
    page = set()
    for k in hits:                                                     # 眉行本体: 换页起头 ⇎ 次行空 ⇎ 到文件尾
        if FFRX.match(sl[k]) or k + 1 >= len(L[i]) or sl[k + 1] == u'':
            page.add(k)
    for k in hits:                                                     # 行号扩展: 命中行的下一非空行也归壳
        j = k + 1
        while j < len(L[i]) and sl[j] == u'':
            j += 1
        if j < len(L[i]):
            page.add(j)
    toc = [k for k in range(len(L[i])) if sl[k] != u'' and TORX.match(sl[k]) is not None and k not in page]
    return sorted(page), toc


SHELL = [shell_sets(i)[0] for i in range(NSRC)]
TOCR = [shell_sets(i)[1] for i in range(NSRC)]
F['shell_rows'] = [len(SHELL[i]) for i in range(NSRC)]
F['toc_rows'] = [len(TOCR[i]) for i in range(NSRC)]
F['body_rows'] = [F['n_nonempty'][i] - F['shell_rows'][i] - F['toc_rows'][i] for i in range(NSRC)]

SH = [set(SHELL[i]) for i in range(NSRC)]


def strip_markup(i, txt):
    out = []
    for line in txt.split(NL):
        if line.lstrip().startswith(u'|'):
            line = line.lstrip()[1:]
        line = line.replace(u'*_', u'').replace(u'_*', u'')
        line = re.sub(u'</?[a-zA-Z][^>]*>', u'', line)
        out.append(line)
    return NL.join(out)


NSFOLD = [pnorm(u' '.join(L[i][k] for k in range(len(L[i])) if k not in SH[i])) for i in range(NSRC)]
MKFOLD = [pnorm(strip_markup(i, NL.join(L[i][k] for k in range(len(L[i])) if k not in SH[i])))
          for i in range(NSRC)]

# ---------- 2. 面偏移→原行: 机制⑥逐字符行号表(采集侧是累积长度 + bisect) ----------
LSTART, LINTAB = [], []
for i in range(NSRC):
    st, tab, pos = [], [], 0
    for k, x in enumerate(L[i]):
        st.append(pos)
        for _ch in x:
            tab.append(k)
            pos += 1
        tab.append(k)                                                  # 行尾换行符归它收掉的那一行
        pos += 1
    LSTART.append(st)
    LINTAB.append(tab)
LEOF = [len(T[i]) for i in range(NSRC)]


def off_line(i, off):
    tab = LINTAB[i]
    return tab[off] if 0 <= off < len(tab) else len(L[i])


# ---------- 3. 定义段: 机制⑤块定界 + 机制⑧(?m) 整行标题正则 ----------
WIN_TITLES = [u'14.37 Retry-After', u'4.  429 Too Many Requests', u'7.1.3.  Retry-After',
              u'10.2.3.  Retry-After', u'# `--retry`']
WIN_ENDS = [u'14.38 Server', u'5.  431 Request Header Fields Too Large', u'7.1.4.  Vary',
            u'10.2.4.  Server', None]


def hdr_hit(i, title, frm_line=0):
    rx = re.compile(u'(?m)^' + re.escape(title) + u'[ \t]*$')
    for m in rx.finditer(T[i]):
        ln = off_line(i, m.start())
        if ln >= frm_line:
            return ln, m.start()
    return -1, -1


WIN = []
for i in range(NSRC):
    a, a_off = hdr_hit(i, WIN_TITLES[i])
    assert a >= 0, (i, WIN_TITLES[i])
    if WIN_ENDS[i]:
        b, b_off = hdr_hit(i, WIN_ENDS[i], a + 1)
        assert b > a, (i, WIN_ENDS[i])
    else:
        b, b_off = len(L[i]), LEOF[i]
    WIN.append((a, b, a_off, b_off))
F['win_start'] = [w[0] for w in WIN]
F['win_end'] = [w[1] for w in WIN]
F['win_rows'] = [w[1] - w[0] for w in WIN]
# 块定界: 直接从面上切 [a_off, b_off), 只剥块尾那一枚换行(它是上一行的行界, 不是块内容)
F['win_text'] = []
for i in range(NSRC):
    blk = T[i][WIN[i][2]:WIN[i][3]]
    if WIN[i][3] < LEOF[i] and blk.endswith(NL):
        blk = blk[:-1]
    F['win_text'].append(blk)
    assert blk == NL.join(L[i][WIN[i][0]:WIN[i][1]]), u'块定界与行阵切片不同串 ' + LBL[i]
F['win_cp'] = [len(F['win_text'][i]) for i in range(NSRC)]
F['win_ns_text'] = [NL.join(L[i][k] for k in range(WIN[i][0], WIN[i][1]) if k not in SH[i]) for i in range(NSRC)]
F['win_ns_rows'] = [len(F['win_ns_text'][i].split(NL)) for i in range(NSRC)]
F['win_shell_rows'] = [F['win_rows'][i] - F['win_ns_rows'][i] for i in range(NSRC)]

# ---------- 4. 针账(全份折平档 ⇎ 窗口行档) ----------
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
    F[key] = [cnt_cur(FOLD[i], pnorm(nd)) for i in range(NSRC)]
F['needle_n'] = len(NEEDLES)
_must_wide, _cap_wide = [], []
CAPWORDS = [u'maximum', u'at most', u'no more than', u'upper bound', u'ceiling', u'cap']
for i in range(NSRC):
    hm, hc = 0, 0
    for s in sents(T[i]):
        if u'retry-after' in s and u'must' in s:
            hm += 1
        if u'retry-after' in s:
            for cw in CAPWORDS:
                if cw in s:
                    hc += 1
                    break
    _must_wide.append(hm)
    _cap_wide.append(hc)
F['ra_must_sent_wide'] = _must_wide
F['ra_capword_sent_wide'] = _cap_wide

# ---------- 5. Retry-After 计账: 总数 ⇎ 窗内 ⇎ 窗外(窗外走块余集) ----------
F['ra_total'] = [cnt_cur(T[i], u'Retry-After') for i in range(NSRC)]
F['ra_win'] = [cnt_cur(F['win_text'][i], u'Retry-After') for i in range(NSRC)]
F['ra_out'] = [cnt_cur(T[i][:WIN[i][2]] + T[i][WIN[i][3]:], u'Retry-After') for i in range(NSRC)]
F['ra_decomp_diff'] = [F['ra_total'][i] - F['ra_win'][i] - F['ra_out'][i] for i in range(NSRC)]
for i in range(NSRC):
    assert F['ra_decomp_diff'][i] == 0, i
F['ra_rows'] = [len([1 for x in L[i] if u'Retry-After' in x]) for i in range(NSRC)]
F['ra_caseless'] = [F['ra_total'][i] + cnt_cur(T[i], u'Retry-after') +
                    cnt_cur(T[i], u'retry-after') + cnt_cur(T[i], u'RETRY-AFTER') for i in range(NSRC)]


# ---------- 6. 数值现读: 游标定位 + 就地吃数字串(采集侧是 re.search 分组) ----------
def num_after(face, kw, tail=None):
    """从 kw 之后吃一串数字; 要求字界, 可选校验尾词(tail 前须恰一枚空格)。枚枚试到第一处成功。"""
    i, n = 0, len(face)
    while True:
        j = face.find(kw, i)
        if j < 0:
            return -1
        k = j + len(kw)
        m = k
        while m < n and face[m].isdigit():
            m += 1
        rb = m >= n or not (face[m].isalnum() or face[m] == u'_')
        if m > k and rb and (tail is None or face[m:m + 1 + len(tail)] == u' ' + tail):
            return int(face[k:m])
        i = j + 1


F['ex_ra_secs'] = [num_after(flat_chars(F['win_text'][i]), u'Retry-After: ') for i in range(NSRC)]
F['ex_ra_mins'] = [num_after(flat_chars(F['win_text'][i]), u'delay is ', u'minutes') for i in range(NSRC)]
assert F['ex_ra_secs'][:4] == [120, 3600, 120, 120] and F['ex_ra_secs'][4] < 0, F['ex_ra_secs']
# 机制⑦: 分钟⇎秒两处各自现算(采集侧一处建表两次查表)
F['unit_minute_from_doc'] = [F['ex_ra_secs'][i] // F['ex_ra_mins'][i]
                             if (F['ex_ra_secs'][i] > 0 and F['ex_ra_mins'][i] > 0) else -1
                             for i in range(NSRC)]
curlw = pnorm(F['win_text'][4])
F['curl_cap_minutes'] = num_after(curlw, u'reaches ', u'minutes')
assert F['curl_cap_minutes'] == 10
F['curl_cap_secs'] = F['curl_cap_minutes'] * (F['ex_ra_secs'][2] // F['ex_ra_mins'][2])      # 当场除#1
_numw = dict(zip([u'zero', u'one', u'two', u'three', u'four'], range(5)))                    # 词形⇎数目对照表(语言定义, 非读数)
_p = curlw.find(u'first waits ')
_word = curlw[_p + 12:curlw.find(u' ', _p + 12)]
assert _word in _numw and curlw[_p + 12 + len(_word):] .startswith(u' second'), curlw[_p:p + 30]
F['curl_first_secs'] = _numw[_word]
F['ratio_6585_over_120'] = F['ex_ra_secs'][1] // F['ex_ra_secs'][2]
_f60b = F['ex_ra_secs'][3] // F['ex_ra_mins'][3]                                             # 当场除#2
F['ratio_3600_per_hour'] = -(-F['ex_ra_secs'][1] // _f60b)
assert F['ratio_3600_per_hour'] == 60
F['num_hour_rate'] = num_after(flat_chars(F['win_text'][1]), u'I only allow ', u'requests')   # 保大小写: 折平不转 lowercase
assert F['num_hour_rate'] == 50


def codes3(s):
    """逐字符吃数字游程: 恰三枚、首枚 4/5、两侧不是字界内字符才算一码。"""
    n, k = 0, 0
    while k < len(s):
        if s[k].isdigit():
            m = k
            while m < len(s) and s[m].isdigit():
                m += 1
            lb = k == 0 or not (s[k - 1].isalnum() or s[k - 1] == u'_')
            rb = m >= len(s) or not (s[m].isalnum() or s[m] == u'_')
            if m - k == 3 and s[k] in u'45' and lb and rb:
                n += 1
            k = m
        else:
            k += 1
    return n


_tset = None
for s in sents(F['win_text'][4]):
    if u'transient error means' in s:
        _tset = s
assert _tset is not None
F['curl_transient_codes'] = codes3(_tset)
F['num_1999'] = [cnt_cur(FOLD[i], u'1999') for i in range(NSRC)]
F['rfcref_2616_in_9110'] = cnt_cur(FOLD[3], u'rfc 2616') + cnt_cur(FOLD[3], u'rfc2616')
F['win_caps_may'] = [cnt_cur(F['win_ns_text'][i], u'MAY') for i in range(NSRC)]
F['win_caps_should'] = [cnt_cur(F['win_ns_text'][i], u'SHOULD') for i in range(NSRC)]
F['win_caps_must'] = [cnt_cur(F['win_ns_text'][i], u'MUST') for i in range(NSRC)]
F['win_caps_ought'] = [cnt_cur(F['win_ns_text'][i], u'ought') for i in range(NSRC)]
F['hd_win'] = [cnt_cur(F['win_ns_text'][i], u'HTTP-date') for i in range(NSRC)]
F['gram_slash'] = [cnt_cur(T[i], u'Retry-After = HTTP-date / delay-seconds') for i in range(NSRC)]
F['gram_colon'] = [cnt_cur(T[i], u'Retry-After  = "Retry-After" ":" ( HTTP-date | delta-seconds )')
                   for i in range(NSRC)]
F['two_examples'] = [cnt_cur(pnorm(F['win_ns_text'][i]), pnorm(u'Two examples of its use are'))
                     for i in range(NSRC)]
F['n429'] = [cnt_cur(T[i], u'429') for i in range(NSRC)]
F['n503'] = [cnt_cur(T[i], u'503') for i in range(NSRC)]
F['n413'] = [cnt_cur(T[i], u'413') for i in range(NSRC)]
F['n3xx'] = [cnt_cur(T[i], u'3xx') for i in range(NSRC)]

# ---------- 7. 7231 ⇎ 9110 窗内共句: 机制③词频档(采集侧是 set 交并差) ----------
from collections import Counter
S7 = sents(F['win_ns_text'][2])
S9 = sents(F['win_ns_text'][3])
cA, cB = Counter(S7), Counter(S9)
F['cmp_sents_a'] = len(S7)
F['cmp_sents_b'] = len(S9)
F['cmp_same'] = len([z for z in cA if cB[z] > 0])
F['cmp_only_a'] = len([z for z in cA if z not in cB])
F['cmp_only_b'] = len([z for z in cB if z not in cA])
F['cmp_union'] = F['cmp_same'] + F['cmp_only_a'] + F['cmp_only_b']
F['cmp_incl_excl_diff'] = F['cmp_sents_a'] + F['cmp_sents_b'] - F['cmp_union'] - F['cmp_same']
assert F['cmp_same'] + F['cmp_only_a'] + F['cmp_only_b'] == F['cmp_union']
F['dup7'] = len(S7) - len(cA)
F['dup9'] = len(S9) - len(cB)

# ---------- 8. 反向独占针 ----------
NEG = [(0, u'delta-seconds'), (1, u'Retry-After: 3600'), (2, u'after the response is received'),
       (3, u'after receiving the response'), (4, u'first waits one second'),
       (0, u'integer number of seconds (in decimal)'), (1, u'may include a retry-after')]
F['neg_excl'] = []
for oi, nd in NEG:
    q = pnorm(nd)
    mine = cnt_cur(FOLD[oi], q)
    others = sum(cnt_cur(FOLD[i], q) for i in range(NSRC) if i != oi)
    F['neg_excl'].append([oi, mine, others, 1 if (mine > 0 and others == 0) else 0])
F['neg_clean'] = sum(x[3] for x in F['neg_excl'])
F['neg_n'] = len(NEG)

# ---------- 9. 窗口可读档(行 ⇎ 折 ⇎ 摘壳 ⇎ 去标记) ----------
RISK = [u'either an HTTP-date or an integer number', u'MAY be indicated in a Retry-After',
        u'If no Retry-After is given, the client SHOULD', u'MAY include a Retry-After header indicating how long',
        u'MAY send a Retry-After header field', u'SHOULD generate a Retry-After header field to indicate',
        u'A delay-seconds value is a non-negative decimal integer',
        u'The Retry-After field value can be either an HTTP-date or a number',
        u'complies with the Retry-After: response header', u'curl complies with the Retry-After',
        u'does not imply that a server has to use it', u'optional; servers cannot be required']
RISK = RISK[:12]
RROW = [[1 if any(pnorm(nd) in pnorm(x) for x in L[i]) else 0 for i in range(NSRC)] for nd in RISK]
RFOLD = [[cnt_cur(FOLD[i], pnorm(nd)) for i in range(NSRC)] for nd in RISK]
RSHELL = [[cnt_cur(NSFOLD[i], pnorm(nd)) for i in range(NSRC)] for nd in RISK]
RMK = [[cnt_cur(MKFOLD[i], pnorm(nd)) for i in range(NSRC)] for nd in RISK]
F['risk_n'] = len(RISK)
F['risk_row'] = [[RROW[j][i] for j in range(len(RISK))] for i in range(NSRC)]
F['risk_fold'] = [[RFOLD[j][i] for j in range(len(RISK))] for i in range(NSRC)]
F['risk_shell'] = [[RSHELL[j][i] for j in range(len(RISK))] for i in range(NSRC)]
F['risk_mkfree'] = [[RMK[j][i] for j in range(len(RISK))] for i in range(NSRC)]
F['risk_cut_row'] = [len([1 for j in range(len(RISK))
                          if RFOLD[j][i] > 0 and RROW[j][i] == 0]) for i in range(NSRC)]
F['risk_cut_shell'] = [len([1 for j in range(len(RISK))
                            if RSHELL[j][i] > 0 and RFOLD[j][i] == 0]) for i in range(NSRC)]
F['risk_cut_mk'] = [len([1 for j in range(len(RISK))
                         if RMK[j][i] > 0 and RSHELL[j][i] == 0]) for i in range(NSRC)]
assert sum(F['risk_cut_shell']) == 0, F['risk_cut_shell']

# 9b. 针账换尺现算(游标 find 环 ⇎ 整串正则): 差值落键, 恒等式段只查键归零(可入 DERIV 重放)
F['needle_ruler_diff'] = sum(abs(cnt_cur(FOLD[i], pnorm(nd))
                                 - len(re.findall(re.escape(pnorm(nd)), FOLD[i])))
                             for nd in NEEDLES for i in range(NSRC))
F['risk_ruler_diff'] = sum(abs(cnt_cur(FOLD[i], pnorm(nd))
                               - len(re.findall(re.escape(pnorm(nd)), FOLD[i])))
                           for nd in RISK for i in range(NSRC))

# ---------- 10. 句子级窗口读数 ⇎ curl front matter ----------
F['win_sents'] = [len(sents(F['win_ns_text'][i])) for i in range(NSRC)]
F['win_verb_rows'] = [
    len([s for s in sents(F['win_ns_text'][i])
         if re.search(u'\\b(MAY|SHOULD|MUST|ought|asked|can)\\b', s)]) for i in range(NSRC)]
q_tbl = pnorm(u'Retry-After Section 10.2.3')
F['tbl_9110_raw'] = cnt_cur(FOLD[3], q_tbl)
F['tbl_9110_mkfree'] = cnt_cur(MKFOLD[3], q_tbl)
assert F['tbl_9110_raw'] == 0 and F['tbl_9110_mkfree'] == 3
_fm = -1
if L[4][0].strip() == u'---':
    for k in range(1, len(L[4])):
        if L[4][k].strip() == u'---':
            _fm = k
            break
assert _fm >= 9 and L[4][_fm].strip() == u'---', u'curl front matter 尺失效'
F['curl_fm_rows'] = _fm + 1
F['curl_body_cp'] = len(T[4][LSTART[4][_fm + 1]:])                       # 块余集口径(机制⑤)
F['curl_head_rows_after_fm'] = len([x for x in L[4][_fm + 1:] if x.strip()])

# ---------- 11. 与采集遍逐键对账 ----------
# --- PICK BEGIN --- (corpus/_wire98.py 把对账段也一并看住: 采集遍落盘 corpus/_b98meas.json)
PK = json.load(io.open(u'corpus/_b98meas.json', encoding='utf-8'))
AGREE, DIFFK = [], []
for _k in sorted(PK):
    if _k in F and F[_k] == PK[_k]:
        AGREE.append(_k)
    else:
        DIFFK.append(_k)
F['pick_agree'] = len(AGREE)
F['pick_diff'] = len(DIFFK)
F['pick_diffk'] = sorted(DIFFK)
# --- PICK END ---

# ---------- 布尔门(每道都能红) ----------
CLOSE = []


def K(name, expr, note):
    CLOSE.append((name, expr, note))


G = []
G.append((u'五份全LF面', sum(F['n_cr']) == 0))
G.append((u'行阵回环等于原面', all([NL.join(L[i]) == T[i] for i in range(NSRC)])))
G.append((u'行账逐份平', F['splitlines_ledger_diff'] == [0] * NSRC))
G.append((u'窗块两把尺同串', all([F['win_text'][i] == NL.join(L[i][WIN[i][0]:WIN[i][1]])
                                for i in range(NSRC)])))
G.append((u'RA分解账全零', F['ra_decomp_diff'] == [0] * NSRC))
G.append((u'壳档不吃新读', sum(F['risk_cut_shell']) == 0))
G.append((u'样例秒数120⇎3600⇎120⇎120⇎无', F['ex_ra_secs'] == [120, 3600, 120, 120, -1]))
G.append((u'MUST乘RA最宽档全零', F['ra_must_sent_wide'] == [0] * NSRC))
G.append((u'界词乘RA最宽档全零', F['ra_capword_sent_wide'] == [0] * NSRC))
G.append((u'6585不写HTTP-date', F['nd_http_date'][1] == 0 and F['hd_win'][1] == 0))
G.append((u'curl不写HTTP-date', F['nd_http_date'][4] == 0))
G.append((u'curl两种秒名全无', F['nd_delta_seconds'][4] == 0 and F['nd_delay_seconds'][4] == 0))
G.append((u'delta秒只在2616', F['nd_delta_seconds'][0] > 0
                                and sum(F['nd_delta_seconds'][1:]) == 0))
G.append((u'delay秒只在7231⇎9110', F['nd_delay_seconds'][2] > 0 and F['nd_delay_seconds'][3] > 0
                                    and F['nd_delay_seconds'][0] + F['nd_delay_seconds'][1]
                                    + F['nd_delay_seconds'][4] == 0))
G.append((u'7231⇎9110同五句各二异', F['cmp_same'] == 5 and F['cmp_only_a'] == 2 and F['cmp_only_b'] == 2
                                     and F['cmp_union'] == 9))
G.append((u'窗内无重句', F['dup7'] == 0 and F['dup9'] == 0))
G.append((u'独占针七式全清', F['neg_clean'] == F['neg_n'] == 7))
G.append((u'9110表格只在去标记档读通', F['tbl_9110_raw'] == 0 and F['tbl_9110_mkfree'] == 3))
G.append((u'curl封顶=分钟乘当场除出的六十', F['curl_cap_secs'] == F['curl_cap_minutes'] * 60))
G.append((u'3600⇎120等比三十', F['ratio_6585_over_120'] * F['ex_ra_secs'][2] == F['ex_ra_secs'][1]))
G.append((u'6585通篇无503', F['n503'][1] == 0))
G.append((u'9110通篇无429', F['n429'][3] == 0))
G.append((u'413两级只在7231⇎9110', [F['nd_should_generate_a_retry_after'][i] > 0 for i in range(NSRC)]
                                      == [False, False, True, True, False]))
G.append((u'If_no_Retry-After只在2616', F['nd_if_no_retry_after_is_given'][0] > 0
                                        and sum(F['nd_if_no_retry_after_is_given'][1:]) == 0))
G.append((u'ought只在7231⇎9110', [F['win_caps_ought'][i] > 0 for i in range(NSRC)]
                                 == [False, False, True, True, False]))
G.append((u'对账无不符键', F['pick_diff'] == 0))
GK = []
for gi, (nm, val) in enumerate(G):
    sl = re.sub(u'[^a-z0-9]', u'', nm)[:12]
    key = u'gc_' + (sl if sl != u'' else u'g%02d' % gi)
    while key in F:
        key += u'x'
    F[key] = 1 if val else 0
    GK.append([key, nm, 1 if val else 0])
F['gate_keys'] = GK
F['bool_all_n'] = len(G)
F['bool_green'] = len([1 for nm, v in G if v])
F['bool_red'] = [nm for nm, v in G if not v]
print(u'布尔门 %d 道, 绿 %d ⇎ 红 %s' % (F['bool_all_n'], F['bool_green'], F['bool_red']))
assert F['bool_green'] == F['bool_all_n'], F['bool_red']

# ---------- 恒等式(ZID: 全归零才算平) ----------
ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"sum(F['splitlines_ledger_diff'])", u'行数账: splitlines − split(\\n) = 换页 − 尾换行 + 竖tab, 逐份相减归零')
Z(u"sum(F['ra_decomp_diff'])", u'RA 枚数: 全份 = 窗块 + 块余集, 逐份相减')
Z(u"sum([F['win_rows'][i] - F['win_ns_rows'][i] - F['win_shell_rows'][i] for i in range(5)])",
  u'窗高 = 摘壳行 + 页壳行(逐份)')
Z(u"sum([F['n_nonempty'][i] - F['shell_rows'][i] - F['toc_rows'][i] - F['body_rows'][i] for i in range(5)])",
  u'非空行 = 壳 + 目录 + 正文(逐份)')
Z(u"sum(F['ra_caseless']) - sum(F['ra_total'])", u'RA 四种大小写形相加只多出零枚(全份只有题面一形)')
Z(u"F['cmp_same'] + F['cmp_only_a'] + F['cmp_only_b'] - F['cmp_union']", u'共句容斥: 同 + 只甲 + 只乙 = 并')
Z(u"F['cmp_sents_a'] + F['cmp_sents_b'] - F['cmp_union'] - F['cmp_same'] - F['dup7'] - F['dup9']",
  u'句数账: 两窗句数相加 = 并 + 同 + 重句(词频档 ⇎ 集合档换算)')
Z(u"F['neg_clean'] - sum(x[3] for x in F['neg_excl'])", u'独占针清账: 标志相加 = 清数')
Z(u"len(F['neg_excl']) - F['neg_n']", u'独占针: 矩阵行数 = 式数')
Z(u"sum([len([1 for j in range(12) if F['risk_fold'][i][j] > 0 and F['risk_row'][i][j] == 0]) "
  u"- F['risk_cut_row'][i] for i in range(5)])", u'折平吃进的针数逐份重枚 = 登记值')
Z(u"F['curl_cap_secs'] - F['curl_cap_minutes'] * (F['ex_ra_secs'][2] // F['ex_ra_mins'][2])",
  u'curl 封顶秒数 = 10 分钟 × 当场除出的 60')
Z(u"F['ratio_3600_per_hour'] * (F['ex_ra_secs'][3] // F['ex_ra_mins'][3]) - F['ex_ra_secs'][1]",
  u'60 分 × 60 秒 = 样例那枚 3600')
Z(u"F['ratio_6585_over_120'] * F['ex_ra_secs'][2] - F['ex_ra_secs'][1]", u'30 × 120 = 6585 那枚 3600')
Z(u"F['needle_ruler_diff']", u'针账换尺: 37 针×5 份, 游标 find 环 ⇎ 整串正则枚数逐枚相符(现算于 9b 段)')
Z(u"F['risk_ruler_diff']", u'风险针换尺: 12 针×5 份, 游标 ⇎ 正则枚数相符(现算于 9b 段)')
Z(u"F['pick_diff']", u'与采集遍逐键对账: 不符数为零')
Z(u"F['bool_green'] - F['bool_all_n']", u'布尔门全绿')
for e, w in ZID:
    v = eval(e, {u'F': F, u'range': range, u'sum': sum, u'len': len, u'max': max, u'abs': abs})
    if v != 0:
        print(u'ZID 不平: %s ⇒ %s' % (w, v))
        raise SystemExit(1)
print(u'恒等式 %d 条全平' % len(ZID))
F['zid_scan_n'] = len(ZID)
F['scan_key_n'] = len(F)
# --- SCAN END --- (以上由 _wire98.py 机械切进 audit.py::_b98_scan)

BB98 = lambda name, i=None: (F[name] if i is None else F[name][i])


def _ev(e):
    return eval(e, {u'B98V': BB98, u'NSRC': NSRC, u'range': range, u'F': F, u'len': len, u'sum': sum})


FN = u'B98V'
_to_v = re.compile(r"(?:F)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B98V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(5)').replace(u'NSRC', u'5')


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
    return


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


ZV = []
for e, w in ZID:
    v = to_v(e.replace(u'\n', u''))
    if eval(v, {FN: BB98, u'range': range, u'sum': sum, u'len': len, u'max': max, u'abs': abs}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))
    reg(str(_ev(e)), v, w)


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB98}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([str(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


for k, v in dump_deriv().items():
    DER[k] = v

print(u'第二遍量测完成: 扁平键 %d ⇎ 恒等式 %d 全平 ⇎ 布尔门 %d 全绿 ⇎ 针 %d(反向 %d) ⇎ 对账 %d 符 %d 不符'
      % (len(F), len(ZID), F['bool_all_n'], F['needle_n'], F['neg_n'], F['pick_agree'], F['pick_diff']))
io.open(u'corpus/_b98flat.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True))

exec(io.open(u'corpus/_mk98emit.py', encoding='utf-8').read())
