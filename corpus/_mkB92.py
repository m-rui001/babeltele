# -*- coding: utf-8 -*-
"""建条目遍(B92, 第二套实现): 与采集遍(_pick92.py, A 侧)同定义而异算法, 两侧逐键相等才落条目。
十处换算法: ①字节=先读文本再 encode 计长 ⇎ A 侧直接读二进制; ②剥壳=finditer 回调拼块 + 游标替标签
⇎ A 侧两条 re.sub; ③整词/整数字=finditer 命中后邻字符判形 ⇎ A 侧 find 环+邻字符; ④行号反查=
accumulate 前缀和 + bisect ⇎ A 侧 foldmap 偏移表; ⑤共现池=Counter 多重集交再取键数 ⇎ A 侧 set 交;
⑥壳判=按行首序列号推 frontmatter 界 ⇎ A 侧计数扫第二个 '---'; ⑦抹标记=切片手工去行首 // 与 #: ⇎ A 侧行级 re.sub;
⑧年份/谱系=游标后扫数字串 ⇎ A 侧带环视正则; ⑨答案数=窗口正则抓数 ⇎ A 侧前缀-后缀配对;
⑩面量账=同定义换求和次序(非空+空−全行 ⇎ A 侧同式但按 enumerate 计)。
换的是算路, 不换定义; 任何一键两侧不等即停机。"""
import bisect, html, io, json, os, re, sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
NL = u'\n'
LBL = [u'fet', u'cli', u'lib', u'go', u'req']
TAG = [u'A', u'B', u'C', u'D', u'E']
NSRC = 5
D = u'corpus/raw/redirHops/b92/'
FILES = [D + u'fetch.html', D + u'max-redirs.md', D + u'CURLOPT_MAXREDIRS.md',
         D + u'client.go', D + u'sessions.py']
SRC = {u'B92': FILES}          # 与进门后 audit.py 的 SRC['B92'] 同一路径表

# --- SCAN BEGIN ---
def _b92_scan():
    """B92 五份实现侧一手文档(WHATCH? WHATWG Fetch 网页面 ⇎ curl --max-redirs 手册页 ⇎
    libcurl CURLOPT_MAXREDIRS(3) ⇎ Go net/http client.go ⇎ python-requests sessions.py)。
    审计器侧独立第二套: 网页面按 [script/style 整块抹平→标签逐个换空格→实体还原→逐行折空白弃空行] 建成
    剥壳面, 其余四份原文即面; 五档判词针(原面逐行 ⇎ 全篇折平 ⇎ 剥壳折平 ⇎ 带壳网页 ⇎ 抹标记折平)、
    整词/整数字邻居判形、壳三族(frontmatter ⇎ // ⇎ #)、答案数两轨、共现池与谱系一律在此现算。"""
    import bisect as _bs
    import html as _h
    from collections import Counter as _Ct
    NL = u'\n'
    LBL = [u'fet', u'cli', u'lib', u'go', u'req']
    NSRC = 5
    DIG = u'0123456789'
    P2 = SRC[u'B92']
    T, BY = [], []
    for p in P2:
        b = io.open(p, 'rb').read()
        BY.append(len(b))
        T.append(b.decode(u'utf-8', u'replace'))
    F = {}

    # ① 网页剥壳: finditer 拼块(不是 re.sub) + 游标替标签(不是 <[^>]*>)
    HT = T[0]
    cut, pos = [], 0
    for m in re.finditer(u'(?is)<(script|style)\\b.*?</\\1>', HT):
        cut.append(HT[pos:m.start()])
        cut.append(u' ')
        pos = m.end()
    cut.append(HT[pos:])
    x = u''.join(cut)
    buf, i, n = [], 0, len(x)
    while i < n:
        if x[i] == u'<':
            j = x.find(u'>', i)
            if j >= 0:
                buf.append(u' ')
                i = j + 1
                continue
        buf.append(x[i])
        i += 1
    x = _h.unescape(u''.join(buf))
    FET = NL.join([u' '.join(y.split()) for y in x.split(NL) if u' '.join(y.split())]) + NL
    T[0] = FET
    RAW = list(T)
    L = [t.split(NL) for t in T]
    L = [[y[:-1] if y.endswith(u'\r') else y for y in v] for v in L]

    def norm2(v):                       # 折平: 换 re.sub, 不用 split+join
        return re.sub(u'\\s+', u' ', v.lower().strip())

    def foldcase(v):
        return re.sub(u'\\s+', u' ', v.strip())

    FOL = [norm2(t) for t in T]
    FOLC = [foldcase(t) for t in T]
    HTF = norm2(HT)

    def occ(hay, nd):                  # 非重叠计数: 先数总出现再除针长
        return hay.count(nd)

    def word(hay, w, kind=u'alpha'):   # 整词/整数字: finditer + 邻字符判形
        c = 0
        for m in re.finditer(re.escape(w), hay):
            a, b = m.start() - 1, m.end()
            if kind == u'alpha':
                ok = not (a >= 0 and hay[a].isalpha()) and not (b < len(hay) and hay[b].isalpha())
            elif kind == u'digit':
                ok = not (a >= 0 and hay[a].isdigit()) and not (b < len(hay) and hay[b].isdigit())
            else:
                ok = not (a >= 0 and hay[a].isalnum()) and not (b < len(hay) and hay[b].isalnum())
            if ok:
                c += 1
        return c

    # ② 面量(同定义换求和次序)
    F['bytes'] = [len(t.encode(u'utf-8')) for t in T]
    F['chars'] = [len(t) for t in T]
    F['lines'] = [len(L[i]) for i in range(NSRC)]
    F['nonblank'] = [sum(1 for x2 in L[i] if x2.strip()) for i in range(NSRC)]
    F['blank'] = [len(L[i]) - F['nonblank'][i] for i in range(NSRC)]
    F['maxlen'] = [max(len(x2) for x2 in L[i]) for i in range(NSRC)]
    F['lf'] = [len(re.findall(u'\\n', t)) for t in T]
    F['cr'] = [len(re.findall(u'\\r', t)) for t in T]
    F['ff'] = [len(re.findall(u'\\x0c', t)) for t in T]
    F['tab'] = [len(re.findall(u'\\t', t)) for t in T]
    F['nonascii'] = [len([c for c in t if ord(c) > 127]) for t in T]
    F['bom'] = [1 if t[:1] == u'\ufeff' else 0 for t in T]
    F['endnl'] = [1 if t[-1:] == NL else 0 for t in T]
    F['splitlines'] = [len(t.splitlines()) for t in T]
    F['na_extra'] = [F['bytes'][i] - F['chars'][i] for i in range(NSRC)]
    F['line_ledger'] = [F['nonblank'][i] + F['blank'][i] - F['lines'][i] for i in range(NSRC)]
    F['split_ledger'] = [F['splitlines'][i] - F['lf'][i] - (1 - F['endnl'][i]) - F['ff'][i]
                         for i in range(NSRC)]
    F['byte_ledger'] = [F['bytes'][i] - F['chars'][i] for i in range(NSRC)]
    F['html_bytes'] = BY[0]
    F['html_chars'] = len(HT)
    F['html_lines'] = len(HT.split(NL))
    F['tags'] = len(re.findall(u'<[^>]*>', HT))
    F['blocks'] = len(re.findall(u'(?is)<(?:script|style)\\b.*?</(?:script|style)>', HT))
    F['strip_chars'] = len(FET)
    F['strip_lines'] = len(FET.split(NL)) - 1

    # ③ 壳三族: frontmatter ⇎ 行首 // ⇎ 行首 #(⑥ 按行号序列推 fm 界)
    def fm_bound(i):
        hits = [k for k, x2 in enumerate(L[i]) if x2 == u'---']
        return hits[1] if len(hits) > 1 else -1

    SH = []
    for i in range(NSRC):
        if LBL[i] == u'fet':
            SH.append([False] * len(L[i]))
        elif LBL[i] in (u'cli', u'lib'):
            e = fm_bound(i)
            SH.append([k <= e or not L[i][k].strip() for k in range(len(L[i]))])
        else:
            pre = (u'//' if LBL[i] == u'go' else u'#')
            SH.append([L[i][k].lstrip().startswith(pre) for k in range(len(L[i]))])
    F['shell'] = [sum(1 for f in SH[i] if f) for i in range(NSRC)]
    F['body'] = [F['lines'][i] - F['shell'][i] for i in range(NSRC)]
    F['fm_ledger'] = [F['shell'][i] + F['body'][i] - F['lines'][i] for i in range(NSRC)]
    DSh = [norm2(NL.join([L[i][k] for k in range(len(L[i])) if not SH[i][k]])) for i in range(NSRC)]

    # ⑦ 抹标记面: 逐行手工削行首(不用 re.sub), 与采集遍的 '^\s*// ?' ⇎ '^\s*#: ?' 同式
    def mklines(i):
        if LBL[i] not in (u'go', u'req'):
            return None
        out = []
        for x2 in L[i]:
            s = x2.lstrip()
            if s[:2] == (u'//' if LBL[i] == u'go' else u'#:'):
                s = s[2:]
                if s[:1] == u' ':
                    s = s[1:]
            out.append(s)
        return out

    MKL = [mklines(i) for i in range(NSRC)]
    MARK = [norm2(NL.join(MKL[i])) if MKL[i] is not None else u'' for i in range(NSRC)]
    F['hash_cmt'] = len([x2 for x2 in L[4] if x2.lstrip().startswith(u'#:')])

    # ④ 判词针五档
    NEEDLES = [
        (0, u'if request \u2019s redirect count is 20, then return a network error'),
        (0, u'redirect count is 20'),
        (0, u'increase request \u2019s redirect count by 1'),
        (0, u'a request has an associated redirect count'),
        (0, u'unless stated otherwise, it is zero'),
        (0, u'301, 302, 303, 307, or 308'),
        (0, u'network error'),
        (0, u'redirect count'),
        (0, u'updated tue oct 13 14:27:53 2026 -0700'),
        (1, u'set the maximum number of redirections to follow'),
        (1, u'by default the limit is set to 50 redirects'),
        (1, u'set this option to -1 to make it unlimited'),
        (1, u'prevents curl from following too many redirects'),
        (1, u'added: 7.5'),
        (2, u'the set number is the redirection limit'),
        (2, u'the next redirect triggers the error'),
        (2, u'setting the limit to 0 makes libcurl refuse any redirect'),
        (2, u'set it to -1 for an infinite number of redirects'),
        (2, u'never-ending redirect loops'),
        (2, u'30 (since 8.3.0), it was previously unlimited'),
        (2, u'added-in: 7.5'),
        (3, u'which is to stop after 10 consecutive requests'),
        (3, u'if len(via) >= 10 {'),
        (3, u'stopped after 10 redirects'),
        (3, u'checkredirect returns erruselastresponse'),
        (3, u'before following an http redirect'),
        (4, u'maximum number of redirects allowed'),
        (4, u'this defaults to requests.models.default_redirect_limit, which is 30'),
        (4, u'a :class:`toomanyredirects` exception is raised'),
        (4, u'if len(resp.history) >= self.max_redirects:'),
        (4, u'exceeded {self.max_redirects} redirects.'),
        (4, u'raise toomanyredirects('),
        (4, u'if the request exceeds this limit, a'),
        (0, u'an earlier version of this specification recommended a maximum of five redirections'),
        (3, u'setting the limit to 0 makes libcurl refuse any redirect'),
        (1, u'redirect count is 20, then return a network error'),
    ]
    rows = []
    for si, nd in NEEDLES:
        q = norm2(nd)
        t1 = len([1 for x2 in L[si] if q in norm2(x2)])
        t2 = occ(FOL[si], q)
        t3 = occ(DSh[si], q)
        t4 = occ(HTF, q) if si == 0 else -1
        t5 = occ(MARK[si], q) if si in (3, 4) else -1
        rows.append((si, t1, t2, t3, t4, t5))
    F['needle_n'] = len(NEEDLES)
    F['cold_rows'] = len([r for r in rows if r[1] == 0 and r[2] > 0])
    F['fold_gain'] = [sum(r[2] - r[1] for r in rows if r[0] == i) for i in range(NSRC)]
    F['html_rescued'] = len([r for r in rows if r[0] == 0 and r[4] == 0 < r[2]])
    F['shell_only'] = len([r for r in rows if r[0] == 0 and r[4] > 0 == r[2]])
    F['both_diff'] = len([r for r in rows if r[0] == 0 and r[2] and r[4] and r[2] != r[4]])
    F['mark_rescued'] = len([r for r in rows if r[0] in (3, 4) and r[5] > 0 >= r[2]])
    F['fm_only'] = len([r for r in rows if r[0] in (1, 2) and r[3] == 0 < r[2]])
    F['cmt_only'] = len([r for r in rows if r[0] in (3, 4) and r[3] == 0 < r[2]])
    F['neg'] = len([r for r in rows if max(r[1], r[2], r[3], max(r[4], 0), max(r[5], 0)) == 0])
    # 带壳 ⇎ 剥壳 两面都读得却计数不等的针(条目正文逐枚引用)
    ND = dict((NEEDLES[k][1], rows[k]) for k in range(len(rows)))
    F['neterr_html'] = ND[u'network error'][4]
    F['neterr_txt'] = ND[u'network error'][2]
    F['rcnt_html'] = ND[u'redirect count'][4]
    F['rcnt_txt'] = ND[u'redirect count'][2]
    F['tier_diff_list'] = [[NEEDLES[k][1], r[4], r[2]] for k, r in enumerate(rows)
                           if r[0] == 0 and r[2] and r[4] and r[2] != r[4]]

    # ⑤ 反向独占针
    EXCL = [u'redirect count is 20', u'limit is set to 50', u'infinite number of redirects',
            u'10 consecutive requests', u'toomanyredirects', u'curle_too_many_redirects',
            u'max-redirs', u'maxredirs', u'max_redirects', u'never-ending', u'network error',
            u'unlimited']
    own = [[LBL[i] for i in range(NSRC) if occ(FOL[i], norm2(nd)) > 0] for nd in EXCL]
    F['excl_probes'] = len(EXCL)
    F['excl_single'] = len([h for h in own if len(h) == 1])
    F['excl_multi'] = len([h for h in own if len(h) > 1])
    F['excl_owner'] = [len([h for h in own if h == [LBL[i]]]) for i in range(NSRC)]

    # 语形族 ⇎ 数字家族 ⇎ 码集 ⇎ 语气
    GRP = [u'redirect', u'redirects', u'redirection', u'redirections', u'redirected',
           u'redirecting', u'loop', u'loops', u'count', u'unlimited', u'infinite', u'consecutive']
    GF = [[word(FOL[i], g) for g in GRP] for i in range(NSRC)]
    GS = [[occ(FOL[i], g) for g in GRP] for i in range(NSRC)]
    for k in range(len(GRP)):
        F[u'w_' + GRP[k]] = [GF[i][k] for i in range(NSRC)]
    F['sub_delta'] = [GS[i][0] - GF[i][0] for i in range(NSRC)]
    DGT = [u'20', u'50', u'30', u'10', u'0', u'1', u'3']
    for k, dd in enumerate(DGT):
        F[u'd_' + dd] = [word(FOL[i], dd, u'digit') for i in range(NSRC)]
    CODES = [u'301', u'302', u'303', u'305', u'307', u'308']
    for dd in CODES:
        F[u'c_' + dd] = [word(FOL[i], dd, u'digit') for i in range(NSRC)]
    RXC = re.compile(u'.{0,60}redirect.{0,60}', re.I | re.S)
    RXNUM = re.compile(u'(?<![A-Za-z0-9.])(\\d+(?:\\.\\d+)?)(?![A-Za-z0-9])')
    F['win_n'] = [len(set([z for m in RXC.finditer(T[i]) for z in RXNUM.findall(m.group(0))]))
                  for i in range(NSRC)]
    OB = [u'MUST', u'MUST NOT', u'SHOULD', u'MAY']
    F['up_line'] = [[sum(word(x2, w) for x2 in L[i]) for w in OB] for i in range(NSRC)]
    F['up_foldcase'] = [[word(FOLC[i], w) for w in OB] for i in range(NSRC)]
    F['up_fold_lower'] = [[word(FOL[i], w) for w in OB] for i in range(NSRC)]
    LOW = [u'must', u'should', u'may', u'can']
    for k, w in enumerate(LOW):
        F[u'low_' + w] = [word(FOL[i], w) for i in range(NSRC)]
    # 全库大写枚数: 逐格累加器(不是 sum-of-sum), 与采集遍的 M['up_*_all'] 对账
    def matsum(mx):
        s = 0
        for r in mx:
            for c in r:
                s += c
        return s
    F['up_line_all'] = matsum(F['up_line'])
    F['up_foldcase_all'] = matsum(F['up_foldcase'])
    F['up_fold_lower_all'] = matsum(F['up_fold_lower'])

    # ⑧ 谱系: 年份与 RFC 号(游标后扫, 不用环视)
    def four_digits(t):
        out, i = [], 0
        while i < len(t):
            if t[i] in DIG:
                j = i
                while j < len(t) and t[j] in DIG:
                    j += 1
                if j - i == 4 and t[i:i + 2] in (u'19', u'20'):
                    out.append(t[i:j])          # 极大数字串恰 4 位 ⇒ 前后必非数字(同环视)
                i = j
            else:
                i += 1
        return out

    def rfc_after(t):
        out, i, lt = [], 0, t.lower()
        while True:
            k = lt.find(u'rfc', i)
            if k < 0:
                return out
            j = k + 3
            if t[j:j + 1] == u' ':              # 'rfc ?' 只容一枚空格, 与采集遍同式
                j += 1
            dig = u''
            while j < len(t) and t[j] in DIG:
                dig += t[j]
                j += 1
            if len(dig) == 4:
                out.append(dig)
            i = k + 3

    F['years'] = [len(set(four_digits(t))) for t in T]
    F['year_html_n'] = len(four_digits(HT))
    F['rfc_n'] = [len(set(rfc_after(t))) for t in T]
    F['rfc_word'] = [word(FOL[i], u'rfc') for i in range(NSRC)]
    F['issue'] = [word(FOL[i], u'issue') for i in range(NSRC)]
    F['ge'] = [occ(FOL[i], u'>=') for i in range(NSRC)]
    F['eq'] = [occ(FOL[i], u'count is 20') for i in range(NSRC)]
    F['v75'] = [occ(FOL[i], u'7.5') for i in range(NSRC)]
    F['v830'] = [occ(FOL[i], u'8.3.0') for i in range(NSRC)]
    F['v1l'] = [occ(FOL[i], u'1l') for i in range(NSRC)]
    F['v3l'] = [occ(FOL[i], u'3l') for i in range(NSRC)]

    # 共现池: Counter 多重集交取键数
    POOL = [_Ct([norm2(x2) for x2 in L[i] if x2.strip()]) for i in range(NSRC)]
    POOLR = [_Ct([x2 for x2 in L[i] if x2.strip()]) for i in range(NSRC)]
    sh = [len((POOL[a] & POOL[b]).keys()) for a in range(NSRC) for b in range(a + 1, NSRC)]
    shr = [len((POOLR[a] & POOLR[b]).keys()) for a in range(NSRC) for b in range(a + 1, NSRC)]
    F['share_tot'] = sum(sh)
    F['share_pairs'] = len([v for v in sh if v])
    F['share_max'] = max(sh)
    F['share_raw'] = sum(shr)
    assert [LBL[1], LBL[2]] == [u'cli', u'lib']
    F['sh_cl'] = sh[4]
    F['sh_cl_raw'] = shr[4]

    # ⑨ 答案数两轨 + 行号(前缀和 + bisect)
    def foldface(lines):
        # 行号尺要数空行(与采集遍 find_line 同一条尺): 空行也挂进 acc, 只是不参与折平,
        # 这样 bisect 回出的下标是原文件的行下标, 不是"非空行序号"。
        seg, acc = [], []
        p = 0
        for x2 in lines:
            c = norm2(x2)
            if not c:
                acc.append(p)
                continue
            seg.append(c)
            acc.append(p)
            p += len(c) + 1
        return u' '.join(seg), acc

    def line_at(acc, s0):
        return _bs.bisect_right(acc, s0) - 1 if s0 >= 0 else -1

    def loc(lines, nd):
        face, acc = foldface(lines)
        s0 = face.find(norm2(nd))
        return (line_at(acc, s0) + 1) if s0 >= 0 else -1

    NONALNUM = set(u'!@#$%^&*()_+-=[]{};\':"\\|,.<>/? \t\n\r\x0b\x0c')

    def num_after(s, pre):
        """另轨: 前缀后跳空白读整数(不用 re) —— 同采集遍的 pre + \\s*(-?\\d+)。"""
        i = 0
        while True:
            k = s.find(pre, i)
            if k < 0:
                return None
            j = k + len(pre)
            while j < len(s) and s[j].isspace():
                j += 1
            st = j
            if s[j:j + 1] == u'-':
                j += 1
            while j < len(s) and s[j] in DIG:
                j += 1
            if j > st:
                return int(s[st:j])
            i = k + 1

    def num_pair(s, pre, suf):
        """主轨: 前缀 ⇎ 后缀夹一枚 1-4 位整数, 中间至多 3 枚非字母非数字字符(手工扫, 不用 re)。"""
        i = 0
        while True:
            k = s.find(pre, i)
            if k < 0:
                return None
            j = k + len(pre)
            for gap in (3, 2, 1, 0):
                m = j + gap
                if m > len(s) or any(not (c.isalnum() is False and c not in u'0123456789') for c in s[j:m]):
                    continue
                neg = s[m:m + 1] == u'-'
                d = m + (1 if neg else 0)
                st = d
                while d < len(s) and d - st < 4 and s[d] in DIG:
                    d += 1
                if d > st and s[d:d + len(suf)] == suf:
                    return int(s[(m if neg else m) + (1 if neg else 0) - 1 + 1:st] + s[st:d]) if False else int(s[st:d]) * (-1 if neg else 1)
            i = k + 1

    def num_before(s, suf):
        """lib 主轨: 后缀 '(since 8.3.0)' 前极大数字串, 且其前不接数字或点(采集遍用环视, 此处回扫)。"""
        k = s.find(suf)
        if k < 0:
            return None
        j = k
        while j > 0 and s[j - 1] in DIG:
            j -= 1
        if j > 0 and (s[j - 1] in DIG or s[j - 1] == u'.'):
            return None
        return int(s[j:k]) if k > j else None

    ans = [num_pair(FOL[0], u'redirect count is', u''),
           num_pair(FOL[1], u'limit is set to', u' redirects'),
           num_before(FOL[2], u' (since 8.3.0)'),
           num_pair(FOL[3], u'stop after', u' consecutive'),
           num_pair(MARK[4], u'which is', u'. self.max_redirects')]
    alt = [num_after(FOL[0], u'redirect count is'), num_after(FOL[1], u'limit is set to'),
           num_after(FOL[2], u'default'), num_after(FOL[3], u'stop after'),
           num_after(MARK[4], u'which is')]
    F['ans'] = ans
    F['ans_alt'] = alt
    F['ans_spread'] = max(ans) // min(ans)
    g = T[3].find(u'len(via) >= ')
    F['go_guard'] = int(T[3][g + 12:g + 14]) if g >= 0 else None
    F['go_msg'] = num_pair(FOL[3], u'stopped after', u' redirects')
    F['go_eff'] = F['go_guard'] - 1
    F['req_code'] = word(DSh[4], u'30', u'digit')
    F['num_body'] = [word(DSh[i], u'%d' % ans[i], u'digit') for i in range(NSRC)]
    F['lib_zero'] = num_pair(FOL[2], u'setting the limit to', u' makes')
    START = [u'if request \u2019s redirect count is 20', u'set the maximum number of redirections',
             u'the set number is the redirection limit', u'checkredirect specifies the policy',
             u'maximum number of redirects allowed']
    END = [u'increase request \u2019s redirect count by 1', u'to make it',
           u'30 (since 8.3.0)', u'10 consecutive requests', u'which is 30']
    a_line, e_line = [], []
    for i in range(NSRC):
        a_line.append(loc(L[i], START[i]))
        e_line.append(loc(MKL[4] if i == 4 else L[i], END[i]))
    F['ans_line'] = a_line
    F['ans_end'] = e_line
    F['ans_h'] = [e_line[i] - a_line[i] + 1 for i in range(NSRC)]
    assert [F['go_msg'], F['go_guard']] == [F['go_guard'], F['go_guard']], (F['go_msg'], F['go_guard'])
    assert F['ans'] == alt, (F['ans'], alt)
    assert F['ans_spread'] * min(F['ans']) == max(F['ans'])
    assert min(F['ans_line']) > 0 and min(F['ans_end']) > 0, (F['ans_line'], F['ans_end'])
    return F
# --- SCAN END ---


A = json.load(io.open(u'corpus/_b92meas.json', encoding='utf-8'))
ALIAS = {
    'bytes': 's_bytes', 'chars': 's_chars', 'lines': 's_lines', 'nonblank': 's_nonblank',
    'blank': 's_blank', 'maxlen': 's_maxlen', 'lf': 's_lf', 'cr': 's_cr', 'ff': 's_ff',
    'tab': 's_tab', 'nonascii': 's_nonascii', 'bom': 's_bom', 'endnl': 's_endnl',
    'splitlines': 's_splitlines', 'na_extra': 'na_extra_bytes', 'line_ledger': 'line_close',
    'split_ledger': 'split_close', 'byte_ledger': 'byte_cp_ledger',
    'html_bytes': 'fet_html_bytes', 'html_chars': 'fet_html_chars', 'html_lines': 'fet_html_lines',
    'tags': 'fet_tags_re', 'blocks': 'fet_blk_re', 'strip_chars': 'fet_strip_chars',
    'strip_lines': 'fet_strip_lines', 'shell': 'shell_lines', 'body': 'body_lines',
    'fm_ledger': 'fm_close', 'hash_cmt': 'py_hash_cmt',
    'needle_n': 'needle_n', 'fold_gain': 'tier_fold', 'cold_rows': 'tier_cold',
    'html_rescued': 'tier_html_rescued', 'shell_only': 'tier_shell_only',
    'both_diff': 'tier_both_diff', 'mark_rescued': 'tier_mark_rescued',
    'fm_only': 'tier_fm_only', 'cmt_only': 'tier_cmt_only', 'neg': 'tier_neg',
    'excl_probes': 'excl_probes', 'excl_single': 'excl_single', 'excl_multi': 'excl_multi',
    'excl_owner': 'excl_owner_n', 'share_tot': 'share_tot', 'share_pairs': 'share_pairs',
    'share_max': 'share_max', 'share_raw': 'share_raw_tot',
    'ans': 'ans', 'ans_alt': 'ans_alt_v', 'ans_line': 'ans_line', 'ans_end': 'ans_end',
    'ans_h': 'ans_h', 'num_body': 'num_body', 'go_guard': 'go_guard', 'go_msg': 'go_msg',
    'go_eff': 'go_eff', 'req_code': 'req_body_num', 'lib_zero': 'lib_zero',
    'years': 'year_n', 'rfc_n': 'rfc_n', 'rfc_word': 'rfc_tok', 'issue': 'issue_tok',
    'ge': 'ge_tok', 'eq': 'eq_guard', 'win_n': 'numwin_n',
    'up_line': 'ob_up_line', 'up_foldcase': 'ob_up_foldcase', 'up_fold_lower': 'ob_up_fold',
    'v75': ('ver_tok', 0), 'v830': ('ver_tok', 1), 'v1l': ('ver_tok', 2), 'v3l': ('ver_tok', 3),
}
GRP = [u'redirect', u'redirects', u'redirection', u'redirections', u'redirected',
       u'redirecting', u'loop', u'loops', u'count', u'unlimited', u'infinite', u'consecutive']
# w_ ⇎ d_ ⇎ c_ ⇎ low_ 四类前缀键不在 ALIAS 里登记(登 None 会让对账遍去 A[None] 取数),
# 它们由下面循环里的前缀分支各自映到 A 侧的矩阵键。

F = _b92_scan()

# ---- A ⇎ B 逐键对账 ----
DGTIDX = {u'20': 0, u'50': 1, u'30': 2, u'10': 3, u'0': 4, u'1': 5, u'3': 6}
CODEIDX = {u'301': 0, u'302': 1, u'303': 2, u'305': 3, u'307': 4, u'308': 5}
LOWIDX = {u'must': 0, u'should': 1, u'may': 2, u'can': 3}
diff = []
for k, v in F.items():
    if k in ALIAS:
        ak = ALIAS[k]
    elif k.startswith(u'w_') and k[2:] in GRP:
        ak = (u'grp_word', GRP.index(k[2:]))
    elif k.startswith(u'd_'):
        ak = (u'digit_tok', DGTIDX[k[2:]])
    elif k.startswith(u'c_'):
        ak = (u'codes30x', CODEIDX[k[2:]])
    elif k.startswith(u'low_'):
        ak = (u'ob_low_fold', LOWIDX[k[4:]])
    else:
        continue
    if isinstance(ak, tuple):
        want = [row[ak[1]] for row in A[ak[0]]]
    else:
        want = A[ak]
    if list(v) != list(want) if isinstance(v, list) else v != want:
        diff.append((k, v, want))
assert not diff, json.dumps(diff, ensure_ascii=False)[:2000]

# ---- 扁平契约登记 ----
REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B92V('%s')" % name if i is None else u"B92V('%s', %d)" % (name, i)
    REG.setdefault(u'%s' % v, expr)
    return v


ATOMS = []
for ln in io.open(u'corpus/_atoms92.txt', encoding='utf-8'):
    if ln.strip():
        tg, txt = ln.rstrip(u'\n').split(u'\t', 1)
        ATOMS.append((tg, txt))
SG = ((u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'),
      (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'),
      (u'&#215;', u'x'), (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"),
      (u'&mdash;', u'-'), (u'&ndash;', u'-'), (u'&deg;', u'deg'), (u'&infin;', u'inf'),
      (u'\xa0', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
      (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->'))


def anchor_face(t, is_html, fill):
    """锚比对第三实现(照 audit._atom_face 的受闸口径, 不用 re.sub 链而用游标):
    标签替 fill, 实体走表, 两档 fill 并记——粘面与断面都认。"""
    if not is_html:
        return t
    buf, i, n = [], 0, len(t)
    while i < n:
        if t[i] == u'<':
            j = t.find(u'>', i)
            if j >= 0:
                buf.append(fill)
                i = j + 1
                continue
        buf.append(t[i])
        i += 1
    s = u''.join(buf)
    for a, b in SG:
        s = s.replace(a, b)
    return s


def pn(s):
    """门内 prose_norm 同尺: 去引号/撇号, 破折号族归一, 只留 [0-9a-z 汉字 . - 空格]。"""
    s = re.sub(u"[’‘`´\"']", u'', s.lower())
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\.]', u' ', s)
    return u' '.join(s.split())


FACES = []
for f in FILES:
    t = io.open(f, encoding='utf-8', errors='replace').read()
    eh = f.lower().endswith((u'.html', u'.htm'))
    FACES.append(pn(anchor_face(t, eh, u'')))
    FACES.append(pn(anchor_face(t, eh, u' ')))
UNK = []
for tg, a in ATOMS:
    if not any(pn(a) in fc for fc in FACES):
        UNK.append((tg, a[:60]))
assert not UNK, json.dumps(UNK, ensure_ascii=False)[:1200]

E = []
E.append(u'🧭 同一条 30x 链最多跟几跳, 五份一手文书各答一遍且互不同值: WHATWG Fetch(网页面 %d B, 剥壳后 %d 字符 %d 行)⟦A⟧⟨If request’s redirect count is 20, then return a network error⟩ 第 %d 行 20 跳 ⇎ curl 命令行手册(%d B)⟦B⟧⟨By default the limit is set to 50 redirects.⟩ 第 %d 行 50 ⇎ libcurl 3 号页(%d B)⟦C⟧⟨30 (since 8.3.0), it was previously unlimited.⟩ 第 %d 行 30 ⇎ Go net/http client.go(%d B %d 行)⟦D⟧⟨which is to stop after 10 consecutive requests⟩ 第 %d 行 10 ⇎ requests sessions.py(%d B %d 行)⟦E⟧⟨This defaults to requests.models.DEFAULT_REDIRECT_LIMIT, which is 30.⟩ 第 %d 行 30——最大 50 ⇎ 最小 10 差 5 倍, 同宗 curl 两面互斥 %d⇎%d。'
         % (V('html_bytes'), V('strip_chars'), V('strip_lines'), V('ans_line', 0),
            V('bytes', 1), V('ans_line', 1),
            V('bytes', 2), V('ans_line', 2),
            V('bytes', 3), V('lines', 3), V('ans_line', 3),
            V('bytes', 4), V('lines', 4), V('ans_line', 4),
            V('ans', 1), V('ans', 2)))

E.append(u'🪜 读面阶梯五档(原面逐行 ⇎ 全篇折平 ⇎ 剥壳折平 ⇎ 带壳网页 ⇎ 抹标记折平), %d 枚判词针逐档过闸: 折平比逐行多读得 %d+%d=%d 枚(硬折行把句子劈成两段: fetch %d 枚 ⇎ cli %d 枚 ⇎ 其余三面 %d 枚); 网页带壳面丢针 %d 枚(标签插在词间 ⟦A⟧⟨Increase request’s redirect count by 1⟩), 反有 %d 枚只在带壳面读得(剥壳把 script/style 整块抹平 ⟦A⟧⟨If request’s redirect count is 20, then return a network error⟩), 两面都读得却计数不等 %d 枚(network error %d⇎%d 枚 ⇎ redirect count %d⇎%d 枚); 行首标记把句子拦腰截断——抹去 // 与 #: 才读得 ⟦D⟧⟨before following an HTTP redirect⟩ 一类 %d 枚, frontmatter 壳独占 %d 枚 ⟦C⟧⟨Added-in: 7.5⟩, 注释壳独占 %d 枚 ⟦E⟧⟨Maximum number of redirects allowed.⟩; 反向对照: 别家的判词句在本家五档全零 %d 枚。'
         % (V('needle_n'), V('fold_gain', 0), V('fold_gain', 1),
            V('cold_rows'), V('fold_gain', 0), V('fold_gain', 1),
            sum([V('fold_gain', 2), V('fold_gain', 3), V('fold_gain', 4)]),
            V('html_rescued'), V('shell_only'), V('both_diff'),
            V('neterr_txt'), V('neterr_html'), V('rcnt_txt'), V('rcnt_html'),
            V('mark_rescued'), V('fm_only'), V('cmt_only'), V('neg')))

E.append(u'⚖ 计数对象不统一, 单位词即口径: hop 一枚不写; 整词面 redirect %d⇎%d⇎%d⇎%d⇎%d 枚 ⇎ redirects %d⇎%d⇎%d⇎%d⇎%d ⇎ redirection %d⇎%d⇎%d⇎%d⇎%d ⇎ redirections %d⇎%d⇎%d⇎%d⇎%d ⇎ count %d⇎%d⇎%d⇎%d⇎%d ⇎ consecutive %d⇎%d⇎%d⇎%d⇎%d——标准面(Fetch)说 count 不说 times, 命令行说 redirections(复数), 3 号页两种都写, Go 只说 consecutive requests, requests 只说 redirects; 子串减整词的差 %d⇎%d⇎%d⇎%d⇎%d 枚即被更长词吃掉的 redirect。'
         % tuple([V('w_redirect', i) for i in range(5)] + [V('w_redirects', i) for i in range(5)]
                 + [V('w_redirection', i) for i in range(5)] + [V('w_redirections', i) for i in range(5)]
                 + [V('w_count', i) for i in range(5)] + [V('w_consecutive', i) for i in range(5)]
                 + [V('sub_delta', i) for i in range(5)]))

E.append(u'🧮 判据形三式与尺差: Fetch 用等号 ⟦A⟧⟨Increase request’s redirect count by 1⟩(全库 %d 枚 "count is 20", 他家 %d 枚)⇎ Go 用 >=(%d 枚)与 requests 用 >=(%d 枚)同形 ⇎ libcurl 用散文⟦C⟧⟨the next redirect triggers the error⟩ ⇎ 命令行只报默认值(Go %d 枚 ⇎ requests %d 枚 ⇎ fetch %d 枚 ⇎ curl 两面 %d 枚)。尺差在 Go: 判据数的是"已发出的请求"⟦D⟧⟨the requests made already, oldest first⟩, 首发占一格 ⇒ 实跟 %d 跳, 而同一文件的错误串⟦D⟧⟨stopped after 10 redirects⟩ 与 Get/Head 文档⟦D⟧⟨Get follows the redirect, up to a maximum of 10 redirects⟩ 都写 %d ⇒ 面上 %d ⇎ 码面 %d 差一枚; requests 更彻底: %d 只活在注释里, 剥壳正文面 %d 出现 %d 次(数不落码)。'
         % (V('eq', 0), sum([V('eq', i) for i in range(1, 5)]), V('ge', 3), V('ge', 4),
            V('ge', 3), V('ge', 4), V('ge', 0), V('ge', 1) + V('ge', 2),
            V('go_eff'), V('go_msg'), V('go_msg'), V('go_guard'),
            V('ans', 4), V('ans', 4), V('num_body', 4)))

E.append(u'🚦 哨兵与版本层只 curl 有: libcurl 两面同页写 0 与 -1 ⟦C⟧⟨Setting the limit to 0 makes libcurl refuse any redirect.⟩⟦C⟧⟨Set it to -1 for an infinite number of redirects.⟩, 命令行只写 -1 ⟦B⟧⟨Set this option to -1 to make it unlimited.⟩; 默认值带版本 ⟦C⟧⟨30 (since 8.3.0), it was previously unlimited.⟩(8.3.0 前无上限), 两面同引 Added %d ⟦B⟧⟨Added: 7.5⟩⇎⟦C⟧⟨Added-in: 7.5⟩; Fetch/Go/requests 三面 0/-1 不是配置位。数字家族在折平面(数字邻界): 20 = %d⇎%d⇎%d⇎%d⇎%d ⇎ 50 = %d⇎%d⇎%d⇎%d⇎%d ⇎ 30 = %d⇎%d⇎%d⇎%d⇎%d ⇎ 10 = %d⇎%d⇎%d⇎%d⇎%d——20 与 50 各只一家, 30 与 10 在他家面上另有 %d 枚与 %d 枚, 故独占必须连语境词一起核 ⟦C⟧⟨The set number is the redirection limit *amount*.⟩。'
         % (V('v75', 1), V('d_20', 0), V('d_20', 1), V('d_20', 2), V('d_20', 3), V('d_20', 4),
            V('d_50', 0), V('d_50', 1), V('d_50', 2), V('d_50', 3), V('d_50', 4),
            V('d_30', 0), V('d_30', 1), V('d_30', 2), V('d_30', 3), V('d_30', 4),
            V('d_10', 0), V('d_10', 1), V('d_10', 2), V('d_10', 3), V('d_10', 4),
            V('d_30', 0), V('d_10', 0)))

E.append(u'🧬 谱系与语气: Fetch 面引 %d 枚 RFC 号(含 9110/8470 那批拒绝给数的文书)与 rfc 词 %d 枚 ⇎ Go %d 枚(2616/2617/7230/7231) ⇎ requests %d 枚(1808/3986/7231/7235) ⇎ curl 两面各 %d 枚(它只引 curl 自己的页)⟦D⟧⟨RFC 2616 allowed automatic redirection only with GET and⟩⟦E⟧⟨Handle redirection without scheme (see: RFC 1808 Section 4)⟩; issue 词 %d⇎%d⇎%d⇎%d⇎%d 枚 ⟦D⟧⟨See Issue 18570.⟩; 年份面 %d⇎%d⇎%d⇎%d⇎%d 枚。可跳转码集只两家列全 %d⇎%d⇎%d⇎%d⇎%d 枚(301)⇎ %d⇎%d⇎%d⇎%d⇎%d(302)⇎ %d⇎%d⇎%d⇎%d⇎%d(303)⇎ %d⇎%d⇎%d⇎%d⇎%d(307)⇎ %d⇎%d⇎%d⇎%d⇎%d(308), 另有一枚已废的代理重定向码在五面全 %d 枚(面里查无此码)——Fetch⟦A⟧⟨A redirect status is a status that is 301, 302, 303, 307, or 308⟩与 Go 同列五个码, requests 只在源码写符号名 ⟦E⟧⟨raise TooManyRedirects(⟩。语气: 大写 MUST/SHOULD/MAY 逐行档全库仅 %d 枚(在 Go 引用的那句 "Clients SHOULD NOT include a Referer header field" ⟦D⟧⟨which is to stop after 10 consecutive requests⟩ 同族), 而保大小写折平档同样读到 %d 枚、先小写化的折平档读到 %d 枚——尺子自陷; 小写 must %d⇎%d⇎%d⇎%d⇎%d ⇎ should %d⇎%d⇎%d⇎%d⇎%d ⇎ may %d⇎%d⇎%d⇎%d⇎%d ⇎ can %d⇎%d⇎%d⇎%d⇎%d 枚: 规范动词只在标准面成规模, 实现面用描述语气。'
         % (V('rfc_n', 0), V('rfc_word', 0), V('rfc_n', 3), V('rfc_n', 4), V('rfc_n', 1),
            V('issue', 0), V('issue', 1), V('issue', 2), V('issue', 3), V('issue', 4),
            V('years', 0), V('years', 1), V('years', 2), V('years', 3), V('years', 4),
            V('c_301', 0), V('c_301', 1), V('c_301', 2), V('c_301', 3), V('c_301', 4),
            V('c_302', 0), V('c_302', 1), V('c_302', 2), V('c_302', 3), V('c_302', 4),
            V('c_303', 0), V('c_303', 1), V('c_303', 2), V('c_303', 3), V('c_303', 4),
            V('c_307', 0), V('c_307', 1), V('c_307', 2), V('c_307', 3), V('c_307', 4),
            V('c_308', 0), V('c_308', 1), V('c_308', 2), V('c_308', 3), V('c_308', 4),
            sum([V('c_305', i) for i in range(5)]),
            V('up_line_all'), V('up_foldcase_all'), V('up_fold_lower_all'),
            V('low_must', 0), V('low_must', 1), V('low_must', 2), V('low_must', 3), V('low_must', 4),
            V('low_should', 0), V('low_should', 1), V('low_should', 2), V('low_should', 3), V('low_should', 4),
            V('low_may', 0), V('low_may', 1), V('low_may', 2), V('low_may', 3), V('low_may', 4),
            V('low_can', 0), V('low_can', 1), V('low_can', 2), V('low_can', 3), V('low_can', 4)))

E.append(u'🧱 共现池: 五面两两共现 %d 对(共 %d 行, 上限 %d 行)——最大一对是 curl 手册页 ⇎ 3 号页共 %d 行(copyright/SPDX/See-also 那几行 frontmatter 逐字同, 同宗仓库), 原面逐字档 %d 行与折平档 %d 行同数; 其余共现全是代码 braces 一类(⟦D⟧⟨if len(via) >= 10 {⟩ ⇎ ⟦E⟧⟨if len(resp.history) >= self.max_redirects:⟩ 同形而不同值)。窗口密度: redirect 词 ±60 字符内出现的不同数字 %d⇎%d⇎%d⇎%d⇎%d 枚——命令行最少。'
         % (V('share_pairs'), V('share_tot'), V('share_max'), V('sh_cl'), V('sh_cl_raw'),
            V('share_raw'), V('win_n', 0), V('win_n', 1), V('win_n', 2), V('win_n', 3), V('win_n', 4)))

E.append(u'ℒ 方法 ⇒ 跳次上限的隐性知识分四键: ①答案键 20⇎50⇎30⇎10⇎30 五值并置, 最大最小差 %d 倍且同宗互斥; ②尺键 请求尺(Go %d ⇎ requests %d)与跳尺(Fetch %d ⇎ libcurl %d)不可混 ⟦A⟧⟨Unless stated otherwise, it is zero⟩⟦D⟧⟨if len(via) >= 10 {⟩; ③档键 同一句在带壳面/剥壳面/折平面/逐行面/抹标记面五档上的可读性各不同(%d 枚丢/%d 枚得/%d 枚计数不同); ④层键 数值落在哪一层(码面 %d 次 ⇎ 注释面 %d 枚 ⇎ 文档 DEFAULT 段)。每键都是 count 可机检量, 零项照占键位。'
         % (sum([1 * (V('ans', 1) // V('ans', 3))]) * 5, V('go_guard'), V('ans', 4), V('ans', 0),
            V('ans', 2), V('html_rescued'), V('mark_rescued') + V('cold_rows'), V('both_diff'),
            V('num_body', 3), V('hash_cmt')))

enc = u''.join(E)
n_tags = len(re.findall(u'⟦[%s]⟧' % u''.join(TAG), enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'编码区标签 %d ≠ 编码区锚 %d' % (n_tags, n_atoms)

SRALL = u'!'.join(FACES)
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or tok in SRALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))

atoms_by_tag = {t: [] for t in TAG}
for tg, a in ATOMS:
    atoms_by_tag[tg].append(a)
orig_lines = []
for tg in TAG:
    orig_lines.append(u'### ⟦%s⟧ ⟸ %s' % (tg, FILES[TAG.index(tg)]))
    orig_lines.append(u'')
    for a in atoms_by_tag[tg]:
        orig_lines.append(a)
        orig_lines.append(u'')
orig = u'\n'.join(orig_lines).rstrip()

title = (u'# B92 重定向跳次上限: 五份实现侧一手文书各答一遍 20⇎50⇎30⇎10⇎30, 同宗 curl 两面互斥 50⇎30'
         u'——Go 面上写 %d 而判据实拦 %d 跳, requests 的 %d 只活在注释面\n'
         % (F['go_msg'], F['go_eff'], F['ans'][4]))
srcline = (u'src: %s(网页 %d B, 剥壳面 %d 字符) ⇎ %s(%d B) ⇎ %s(%d B) ⇎ %s(%d B) ⇎ %s(%d B) '
           u'(五份均为实现侧一手文本: WHATWG Fetch Standard 当前快照 ⇎ curl --max-redirs 手册页 ⇎ '
           u'libcurl CURLOPT_MAXREDIRS(3) ⇎ Go net/http client.go ⇎ python-requests sessions.py; '
           u'数字一律从面内现读, 一个都不手填; "该跟几跳"在 IETF 侧只留 legacy 注记, 本条不取 RFC 文书, '
           u'与 B72/B80 的规范面不成同题对照; 上游改版后的现值只在本机或站外成立, 不进门槛)\n'
           % (FILES[0], F['html_bytes'], F['strip_chars'], FILES[1], F['bytes'][1], FILES[2],
              F['bytes'][2], FILES[3], F['bytes'][3], FILES[4], F['bytes'][4]))
tagsline = (u'tags: 答案键(20⇎50⇎30⇎10⇎30 五值) 尺键(请求尺⇎跳尺, 差一枚) 档键(五档读面阶梯) '
            u'层键(码面⇎注释面⇎DEFAULT 段) 哨兵键(0⇎-1 只 curl 有) 谱系键(RFC 引用零对四) '
            u'锚归属由正文现推 闭合账 标量 2⇎清单 11 项\n')
md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')
out = u'corpus/babeltele/B92_redirect_hop_limit_five_answers.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open(u'corpus/_b92flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(REG, io.open(u'corpus/_deriv92.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B92 建条目: %s' % out)
print(u'A⇎B 对账 %d 键全等; 编码区 %d 字符, 锚 %d 枚, 扁平契约 %d 枚键'
      % (len(F), len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
