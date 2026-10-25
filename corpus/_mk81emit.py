# -*- coding: utf-8 -*-
"""B81 建条目第二遍的发射段: 由 _mkB81.py 在顶层 exec 进来, 与前半共享同一批现读量。
段一 SCAN2 是段落层、行号尺、切开判词与模板行池(同一段也由 corpus/_wire81.py 机械切进 audit.py::_b81_scan);
锚在这里换了一把尺: 论文面一行动辄上千字符, 整行当锚就等于没锚, 于是命中区间先映回原行偏移, 再按整词
切成窗口——映回靠 row_fd 给的逐字符对照表, 所以窗口里的连字与弯引号仍是原行的逐字字节。
段二是编码区正文, 每一枚三位以上的数都由 V()/J()/EXPR() 注册过算式;
段三自 replay 恒等式、复核锚归属、落盘 flat/deriv/atoms/checks 与条目文件。"""

# --- SCAN2 BEGIN --- (段落层 ⇎ 行号尺 ⇎ 切开判词 ⇎ 模板行池: 同一段也由 corpus/_wire81.py 机械切进 audit.py::_b81_scan)
TAGS = LBL
IDX = dict((t, n) for n, t in enumerate(LBL))
# 门槛对面(audit.py::_atom_face): 纯文本条目不剥壳, 整份原文归一后就是比对面
FAN = [pnorm(t) for t in T]
ATOMFAIL = []
BLKFAIL = []
PROBE = (u'B81PROBE' in __import__('os').environ)
LONGROW = 100
LIMW = 92
LMAPC = LIGMAP


def row_fd(raw):
    """折平(词间留一枚空格)并拆字, 同时给每个结果字符记下它来自原行的哪一个下标。
    窗口锚要靠这张表映回原文, 才谈得上“逐字”二字——拆字把 ﬁ 展开成两字符, 折平把行首 \\x0c 与行尾空格抹掉,
    两处都会让偏移错位, 所以映射必须与串同时构造, 不能事后按长度折算。"""
    s, idx, k, n = [], [], 0, len(raw)
    while k < n:
        while k < n and raw[k].isspace():
            k += 1
        if k >= n:
            break
        if s:
            s.append(u' ')
            idx.append(k)
        while k < n and not raw[k].isspace():
            d = LMAPC.get(ord(raw[k]), raw[k])
            for ch in d:
                s.append(ch)
                idx.append(k)
            k += 1
    return u''.join(s), idx


ROWS = [[(n, x) for n, x in enumerate(L[i], 1) if not is_shell_pick(x, FAM[i])] for i in range(NSRC)]
FD = []
for i in range(NSRC):
    arr = []
    for n, x in ROWS[i]:
        f, ix = row_fd(x)
        assert len(f) == len(ix) and len(f.lower()) == len(f), (LBL[i], n)
        arr.append((n, x, f, ix))
    FD.append(arr)
    assert [a[1] for a in FD[i]] == SHP[i], i
    assert u' '.join(a[2] for a in FD[i]) == SHLIG[i], i
PP = [[(a[0], a[2]) for a in FD[i]] for i in range(NSRC)]
ALN = FD
ANSET = [set(a[1] for a in FD[i]) for i in range(NSRC)]
# 行级对面: 逐行归一后用一枚正文里不可能出现的分隔符粘起来——锚若跨了两行, 归一串里就横着 \x01, 判不出来
ROWSRAW = [u'\x01'.join(pnorm(a[1]) for a in FD[i]) for i in range(NSRC)]
F['pp_rows'] = [len(PP[i]) for i in range(NSRC)]
F['pp_gap_rows'] = [F['nonblank'][i] - F['pp_rows'][i] for i in range(NSRC)]
F['pp_shell_nonblank'] = [F['shell_lines'][i] - F['blank'][i] for i in range(NSRC)]
F['pp_gap_close'] = sum(abs(F['pp_gap_rows'][i] - F['pp_shell_nonblank'][i]) for i in range(NSRC))
for i in range(NSRC):
    assert u' '.join(x for _, x in PP[i]) == SHLIG[i], i


def fmap(i):
    mp, off, first = [], 0, True
    for n, s in PP[i]:
        if not first:
            off += 1
        first = False
        mp.append((off, n))
        off += len(s)
    return mp


FMP = [fmap(i) for i in range(NSRC)]


def line_of(i, a):
    r = 0
    for o, n in FMP[i]:
        if o <= a:
            r = n
        else:
            break
    return r


def loc(i, a):
    """拆字折平面上的一枚偏移 → (原行号, 该偏移在本行折平串里的位置)"""
    st, n = 0, 0
    for o, nn in FMP[i]:
        if o <= a:
            st, n = o, nn
        else:
            break
    return n, a - st


def word_left(raw, k):
    while k > 0 and not raw[k - 1].isspace():
        k -= 1
    return k


def word_right(raw, k):
    while k < len(raw) and not raw[k].isspace():
        k += 1
    return k


def grow(raw, a, b, lim):
    """命中区间 [a,b) 先扩到整词, 再两侧交替扩到 lim 字符——每步扩一整词, 故窗口两端必落在词边界"""
    lo, hi = word_left(raw, a), word_right(raw, b)
    while True:
        cand = []
        j = lo - 1
        while j >= 0 and raw[j].isspace():
            j -= 1
        if j >= 0:
            left = word_left(raw, j + 1)
            cand.append((lo - left, u'l', left))
        k = hi
        while k < len(raw) and raw[k].isspace():
            k += 1
        if k < len(raw):
            right = word_right(raw, k)
            cand.append((right - hi, u'r', right))
        if not cand:
            break
        d, side, pos = min(cand)
        if hi - lo + d > lim:
            break
        if side == u'l':
            lo = pos
        else:
            hi = pos
    return raw[lo:hi], lo, hi


ALOG = []


def _anline(i, nd, exact, lo, lim=LIMW):
    """锚由面上位置导出: 在本行的拆字折平串上找针, 命中后把区间映回原行、按整词切成窗口串。
    短行(≤LONGROW)整行给出, 长行(论文的 pdftotext 面)给窗口——两种都是原行的逐字片段。"""
    hits = []
    key = pnorm(nd)
    for n, x, f, ix in ALN[i]:
        if n < lo:
            continue
        p = f.lower()
        if exact:
            if pnorm(p) != key:
                continue
            a, b = 0, len(f)
        else:
            k = p.find(key)
            if k < 0:
                continue
            a, b = k, k + len(nd)
        seg, s, e = grow(x, ix[a], ix[min(b, len(ix)) - 1] + 1, lim)
        assert seg in x, (LBL[i], n)
        assert key in pnorm(delig(seg)), (LBL[i], n, nd)
        hits.append((n, seg, x))
    if not hits:
        ATOMFAIL.append((LBL[i], nd))
        if PROBE:
            ALOG.append((LBL[i], nd[:34], 0, 0, nd))
            return u'⟦%s⟧⟨MISS:%s⟩' % (LBL[i], nd[:28])
        raise AssertionError(u'锚导出失败 %s %s' % (LBL[i], nd))
    n, seg, x = hits[0]
    assert pnorm(seg) in FAN[i], (LBL[i], seg[:60])
    ALOG.append((LBL[i], nd[:34], n, len(hits), nd))
    return u'⟦%s⟧⟨%s⟩' % (LBL[i], seg)


def AN(i, nd, lo=0):
    return _anline(i, nd, False, lo)


def ANX(i, nd):
    """整行只由这一串组成(编号标题行 ⇎ 它的目录行): 拿到目录里的 “…… 12” 就走不通"""
    return _anline(i, nd, True, 0)


def ANL(i, lo, nd):
    """同一串在目录与正文各印一次时只取不早于 lo 的那一枚"""
    return _anline(i, nd, False, lo)


def off_last(i, nd):
    f = LOW_SHLIG[i]
    a = f.rfind(pnorm(nd))
    assert a >= 0, (LBL[i], nd)
    return a


def blk(i, start, end, frm=0):
    a = LOW_SHLIG[i].find(pnorm(start), frm)
    if a < 0:
        BLKFAIL.append((LBL[i], start, u'起'))
        if not PROBE:
            raise AssertionError(u'段起针落空 %s %s' % (LBL[i], start))
        return u' ', -1, -1
    b = LOW_SHLIG[i].find(pnorm(end), a)
    if b < 0:
        BLKFAIL.append((LBL[i], end, u'止'))
        if not PROBE:
            raise AssertionError(u'段止针落空 %s %s' % (LBL[i], end))
        return u' ', line_of(i, a), line_of(i, a)
    e = b + len(pnorm(end))
    return u' '.join(SHLIG[i][a:e].split()), line_of(i, a), line_of(i, e - 1)


def ln_of(i, nd, frm=0):
    a = LOW_SHLIG[i].find(pnorm(nd), frm)
    if a < 0:
        raise AssertionError(u'窗针落空 %s %s' % (LBL[i], nd))
    return a, line_of(i, a)


def ln_end(i, nd, frm=0):
    """短语落在哪一行要看它结束在哪一行: 72 列硬换行会把 “a ceiling of 100 ms” 切成两行"""
    a, ln = ln_of(i, nd, frm)
    return a, line_of(i, a + len(pnorm(nd)) - 1)


def line_holds(i, ln, nd):
    """行号尺复核: 拿行号回原文件取那一行, 看针是否真落在这一行内(在拆字折平行串上判)"""
    for n, x, f, ix in ALN[i]:
        if n == ln:
            return 1 if pnorm(nd) in pnorm(f) else 0
    raise AssertionError(u'行号无对应原行 %s %d' % (LBL[i], ln))


def split_pieces(i, nd, last=False):
    """跨行针的两半: 首行那一半从针头读到该行行尾, 末行那一半从该行行首读到针尾。
    两半都是原行的逐字片段, 整串却在首行读不通——这就是硬换行把判词切开的证据。"""
    f = LOW_SHLIG[i]
    key = pnorm(nd)
    a = f.rfind(key) if last else f.find(key)
    assert a >= 0, (LBL[i], nd)
    e = a + len(key) - 1
    h, t = line_of(i, a), line_of(i, e)
    _, rh, fh, ixh = [y for y in ALN[i] if y[0] == h][0]
    _, rt, ft, ixt = [y for y in ALN[i] if y[0] == t][0]
    _, ao = loc(i, a)
    _, te = loc(i, e)
    head = rh[ixh[ao]:ixh[len(fh) - 1] + 1]
    tail = rt[ixt[0]:ixt[te] + 1]
    assert head in rh and tail in rt, (LBL[i], nd)
    return h, t, head, tail


def split_anchor(i, nd, last=False):
    h, t, head, tail = split_pieces(i, nd, last)
    ALOG.append((LBL[i], nd[:34] + u'[首]', h, 1, nd))
    ALOG.append((LBL[i], nd[:34] + u'[末]', t, 1, nd))
    return (u'⟦%s⟧⟨%s⟩' % (LBL[i], head), u'⟦%s⟧⟨%s⟩' % (LBL[i], tail))


# 段界全部由字面针导出: 前 5 段是五份的主答句所在段, 其后是引述段 ⇎ 免配置段 ⇎ 实测段 ⇎ 三份的“关键词”模板段
PINS = [(0, u'A number of AQM algorithms have been proposed', u'in operational networks.'),
        (1, u'PIE has been shown to be less sensitive to traffic loads', u'assumptions on the RTT.'),
        (2, u'Upon installation, the two user-configurable parameters', u'data-center switches, respectively.'),
        (3, u'all tests are run on a symmetrical 10 Mbps link', u'baseline latency.'),
        (4, u'Section 3.2 shows that an ideal TARGET', u'and INTERVAL of 100 ms.'),
        (1, u'its default 5 ms of maximum allowed queuing delay', u'(RTT) is 100 ms'),
        (4, u'the only setting CoDel requires is the INTERVAL value', u'parameter-free for consumer use.'),
        (2, u'PIE is intended to be self-configuring', u'configure any design parameters.'),
        (3, u'The absolute magnitude of the latency increase', u'latency increase is only 5 ms.'),
        (0, u'The key words', u'described in [RFC2119].'),
        (2, u'The key words', u'described in RFC 2119 [RFC2119].'),
        (4, u'The key words', u'they appear in all capitals'),
        (0, u'Network devices SHOULD use an algorithm to drop excessive traffic', u'ECN-capable transport.'),
        (3, u'We use the Flent testing tool', u'companion web site')]
PB = [blk(i, s, e) for i, s, e in PINS]
PTXT = [p[0] for p in PB]
F['blk_lo'] = [p[1] for p in PB]
F['blk_hi'] = [p[2] for p in PB]
F['blk_rows'] = [p[2] - p[1] + 1 for p in PB]
F['blk_chars'] = [len(p[0]) for p in PB]
F['blk_words'] = [len(p[0].split()) for p in PB]
PW = [p[0].lower().split() for p in PB]
F['blk_vocab'] = [len(set(x)) for x in PW]
F['blk_five_chars'] = sum(F['blk_chars'][:5])
F['blk_five_rows'] = sum(F['blk_rows'][:5])
F['blk_five_words'] = sum(F['blk_words'][:5])
F['blk_rows_tot'] = sum(F['blk_rows'])
F['blk_words_tot'] = sum(F['blk_words'])
F['tone_must_blk'] = [ub(p, u'MUST') for p in PTXT]
F['tone_may_blk'] = [ub(p, u'MAY') for p in PTXT]
F['tone_should_blk'] = [ub(p, u'SHOULD') for p in PTXT]
F['tone_mustnot_blk'] = [ub(p, u'MUST NOT') for p in PTXT]
F['tone_in_blk'] = [F['tone_must_blk'][n] + F['tone_may_blk'][n] + F['tone_should_blk'][n]
                    for n in range(len(PB))]
F['blk_must_cur'] = [cnt_cur(p, u'MUST') for p in PTXT]
F['blk_must_re'] = [len(re.findall(u'MUST', p)) for p in PTXT]
F['blk_tone_ruler_close'] = (sum(abs(F['tone_must_blk'][n] - F['blk_must_cur'][n]) for n in range(len(PB)))
                             + sum(abs(F['tone_must_blk'][n] - F['blk_must_re'][n]) for n in range(len(PB))))
# 段内小写语气词: 两份论文全靠小写 can/will 说话, 规范面才有大写轨
F['blk_lc'] = [cnt_re(p.lower(), u'can ') + cnt_re(p.lower(), u'should ') + cnt_re(p.lower(), u'will ')
               for p in PTXT]


def suffix_words(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def head_words(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


# 三份“关键词”模板段(9=7567 ⇎ 10=8033 ⇎ 11=8289): 共头很长, 共尾为零——尾巴各家接各家的引用
F['pre_kw_7567_8033'] = head_words(PW[9], PW[10])
F['pre_kw_7567_8289'] = head_words(PW[9], PW[11])
F['pre_kw_8033_8289'] = head_words(PW[10], PW[11])
F['suf_kw_7567_8033'] = suffix_words(PW[9], PW[10])
F['suf_kw_7567_8289'] = suffix_words(PW[9], PW[11])
F['suf_kw_8033_8289'] = suffix_words(PW[10], PW[11])
F['kw_same_7567_8033'] = 1 if PTXT[9] == PTXT[10] else 0
F['kw_all_same'] = 1 if (PTXT[9] == PTXT[10] == PTXT[11]) else 0
F['kw_min_head'] = min(F['pre_kw_7567_8033'], F['pre_kw_7567_8289'], F['pre_kw_8033_8289'])
F['kw_max_head'] = max(F['pre_kw_7567_8033'], F['pre_kw_7567_8289'], F['pre_kw_8033_8289'])
F['suf_kw_tot'] = F['suf_kw_7567_8033'] + F['suf_kw_7567_8289'] + F['suf_kw_8033_8289']
F['kw_vocab_max'] = max(F['blk_vocab'][9], F['blk_vocab'][10], F['blk_vocab'][11])
# 8289 的模板段比另两份多一枚 NOT RECOMMENDED: 逐份在段内现读
F['kw_notrec'] = [ub(PTXT[n], u'NOT RECOMMENDED') for n in (9, 10, 11)]
F['kw_notrec_tot'] = sum(F['kw_notrec'])
# 两份论文面上根本没有“关键词”这一段: 口径不存在登记 -1, 不是零
KWPOS = [LOW_SHLIG[i].find(pnorm(u'The key words')) for i in range(NSRC)]
F['kw_at'] = [x if x >= 0 else -1 for x in KWPOS]
F['kw_docs'] = len([x for x in F['kw_at'] if x >= 0])
F['kw_minus_row'] = [line_of(i, x) if x >= 0 else -1 for i, x in enumerate(F['kw_at'])]
# “as described in” 在 7567 面上有两枚候选行(版权段一枚 ⇎ 关键词段末行一枚): 锚要落进段里就得带行下限
ASDESC = pnorm(u'as described in')
F['as_desc_rows'] = [n for n, x, f, ix in ALN[0] if ASDESC in f.lower()]
F['as_desc_n'] = len(F['as_desc_rows'])
# 主答句五段: “一行读全”落在两份论文段上, pdftotext 把一个段落在一行里
F['blk_words_per_row'] = [F['blk_words'][n] // F['blk_rows'][n] for n in range(5)]
F['blk_is_one_line'] = [1 if F['blk_rows'][n] == 1 else 0 for n in range(5)]
F['blk_one_line_n'] = sum(F['blk_is_one_line'])
# 答句的行号 ⇎ 跨行数由段窗尺重导一遍: 拿建条侧的整句(逐字符句界那轨的产物)在摘壳折平面上取最后一次
# 命中, 命中偏移经 fmap 映回原行——与建条侧“句串数行”是两把不同的尺, 对拍才谈得上复核。
# 针本身(短串)往往只落一行, 整句才跨数行, 所以两档分开登记, 不混为一谈。
F['ans_head'] = [off_last(i, WIN[i]) for i in range(NSRC)]
F['ans_head_line'] = [line_of(i, a) for i, a in enumerate(F['ans_head'])]
F['ans_tail_line'] = [line_of(i, a + len(pnorm(WIN[i])) - 1) for i, a in enumerate(F['ans_head'])]
F['ans_needle_span'] = [F['ans_tail_line'][i] - F['ans_head_line'][i] + 1 for i in range(NSRC)]
F['ans_sent_at'] = [LOW_SHLIG[i].rfind(pnorm(F['ans'][i])) for i in range(NSRC)]
assert all(x >= 0 for x in F['ans_sent_at']), [LBL[i] for i in range(NSRC) if F['ans_sent_at'][i] < 0]
F['ans_sent_line'] = [line_of(i, F['ans_sent_at'][i]) for i in range(NSRC)]
F['ans_sent_end'] = [line_of(i, F['ans_sent_at'][i] + len(pnorm(F['ans'][i])) - 1)
                     for i in range(NSRC)]
F['ans_sent_span'] = [F['ans_sent_end'][i] - F['ans_sent_line'][i] + 1 for i in range(NSRC)]
F['ans_span_ind'] = [len([1 for n, x, f, ix in FD[i]
                          if F['ans_head_line'][i] <= n <= F['ans_tail_line'][i]]) for i in range(NSRC)]
F['ans_line_close'] = sum(abs(F['ans_sent_line'][i] - F['ans_anchor_line'][i]) for i in range(NSRC))
F['ans_span_close'] = sum(abs(F['ans_sent_span'][i] - F['ans_span'][i]) for i in range(NSRC))
F['ans_needle_gap'] = [F['ans_span'][i] - F['ans_needle_span'][i] for i in range(NSRC)]
F['ans_row_ledger'] = [F['ans_sent_end'][i] - F['ans_sent_line'][i] + 1
                       - len([1 for n, x, f, ix in FD[i]
                              if F['ans_sent_line'][i] <= n <= F['ans_sent_end'][i]])
                       for i in range(NSRC)]

# ---------- 切开判词: 逐行漏读的针, 一半在首行 ⇎ 一半在末行 ----------
SPLITREC = []
WRAPK2 = sorted([x for y in F['role_wrap'] for x in y])
SHELLK = sorted(F['role_shell_needles'])
assert WRAPK2 == WRAPK and SHELLK == sorted(F['role_shell_needles']) and not (set(WRAPK2) & set(SHELLK))
for k in WRAPK2:
    i = LBL.index(F['role_src'][k])
    h, t, head, tail = split_pieces(i, ROLEN[k])
    SPLITREC.append((k, i, h, t, len(head), len(tail)))
for k in SHELLK:
    i = LBL.index(F['role_src'][k])
    h, t, head, tail = split_pieces(i, ROLEN[k])
    SPLITREC.append((k, i, h, t, len(head), len(tail)))
F['split_k'] = [x[0] for x in SPLITREC]
F['split_lbl'] = [LBL[x[1]] for x in SPLITREC]
F['split_head'] = [x[2] for x in SPLITREC]
F['split_tail'] = [x[3] for x in SPLITREC]
F['split_span'] = [x[3] - x[2] + 1 for x in SPLITREC]
F['split_span_tot'] = sum(F['split_span'])
F['split_head_chars'] = [x[4] for x in SPLITREC]
F['split_tail_chars'] = [x[5] for x in SPLITREC]
F['split_n'] = len(SPLITREC)
F['split_rows_tot'] = sum(F['split_head_chars']) + sum(F['split_tail_chars'])
# 反向对照: 整串拿到首行那一行内应当读不通; 首行 ⇎ 末行各自读得通自己那一半
F['split_full_on_head'] = sum(line_holds(x[1], x[2], ROLEN[x[0]]) for x in SPLITREC)
F['split_half_ok'] = sum([line_holds(x[1], x[2], pnorm(delig(split_pieces(x[1], ROLEN[x[0]])[2])))
                         for x in SPLITREC])
F['split_shell_between'] = []
for x in SPLITREC:
    if x[0] in SHELLK:
        i = x[1]
        F['split_shell_between'].append(
            len([y for y in L[i][x[2]:x[3] - 1] if is_shell_pick(y, FAM[i]) and y.strip() != u'']))
F['split_wrap_n'] = len(WRAPK)
F['split_shell_n'] = len(SHELLK)
F['split_ledger'] = F['split_n'] - len(F['role_line_miss'])
F['split_span_vs_miss'] = F['split_span_tot'] - F['split_n'] - sum(
    [len([1 for n2, x2, f2, ix2 in FD[LBL.index(F['role_src'][k])]
          if split_pieces(LBL.index(F['role_src'][k]), ROLEN[k])[0] <= n2
          <= split_pieces(LBL.index(F['role_src'][k]), ROLEN[k])[1]]) for k in F['split_k']])

# ---------- 行号尺往返: 段窗首末行回原文件那一行自验 ----------
# 锚本身在 _anline 里逐枚验过“窗口串是本行逐字片段”(段三再按对面复核归属), 这里复核的是段窗的行号
def needle_at(i, ln, nd, side):
    key = pnorm(nd)
    w = key.split(u' ')
    for m in range(len(ALN[i])):
        if ALN[i][m][0] != ln:
            continue
        p = pnorm(ALN[i][m][2])
        if key in p:
            return 2
        prev = pnorm(ALN[i][m - 1][2]) if m else u''
        nxt = pnorm(ALN[i][m + 1][2]) if m + 1 < len(ALN[i]) else u''
        for j in range(1, len(w)):
            if side == u'head' and p.endswith(u' '.join(w[:j])) and nxt.startswith(u' '.join(w[j:])):
                return 1
            if side == u'tail' and p.startswith(u' '.join(w[j:])) and prev.endswith(u' '.join(w[:j])):
                return 1
        return 0
    raise AssertionError(u'行号无对应原行 %s %d' % (LBL[i], ln))


SEGRT = []
for n, (i, s, e) in enumerate(PINS):
    if PB[n][1] < 0:
        continue
    SEGRT.append((i, PB[n][1], pnorm(s), u'head'))
    SEGRT.append((i, PB[n][2], pnorm(e), u'tail'))
F['seg_rt'] = [needle_at(i, ln, nd, sd) for i, ln, nd, sd in SEGRT]
F['seg_rt_n'] = len(F['seg_rt'])
F['seg_rt_ok'] = len([x for x in F['seg_rt'] if x])
F['seg_rt_whole'] = len([x for x in F['seg_rt'] if x == 2])
F['seg_rt_cut'] = len([x for x in F['seg_rt'] if x == 1])
F['seg_rt_head'] = len([1 for (i, ln, nd, sd), v in zip(SEGRT, F['seg_rt']) if sd == u'head' and v])
F['seg_rt_tail'] = F['seg_rt_ok'] - F['seg_rt_head']
F['blk_head_row'] = [PB[n][1] for n in range(5)]
F['blk_tail_row'] = [PB[n][2] for n in range(5)]
F['blk_head_gap'] = [F['blk_head_row'][n] - F['ans_anchor_line'][n] for n in range(5)]


# ---------- 模板长行池: 三份 RFC 共用同一批套版行, 两份论文与谁都不共用 ----------
def pool_of(i, lim):
    s = set()
    for n, x in ROWS[i]:
        f = fold(x)
        if len(f) >= lim:
            s.add(f)
    return s


PAIRS = [(a, b) for a in range(NSRC) for b in range(a + 1, NSRC)]
TRIPS = [(a, b, c) for a in range(NSRC) for b in range(a + 1, NSRC) for c in range(b + 1, NSRC)]
QUADS = [(a, b, c, d) for a in range(NSRC) for b in range(a + 1, NSRC)
         for c in range(b + 1, NSRC) for d in range(c + 1, NSRC)]
POOL = [pool_of(i, 40) for i in range(NSRC)]
POOL25 = [pool_of(i, 25) for i in range(NSRC)]
UNION = set()
for x in POOL:
    UNION |= x
UNION25 = set()
for x in POOL25:
    UNION25 |= x
F['pool_n'] = [len(x) for x in POOL]
F['pool_sum'] = sum(F['pool_n'])
F['pool_union'] = len(UNION)
F['pool_raw_rows'] = [len([x for n, x in ROWS[i] if len(fold(x)) >= 40]) for i in range(NSRC)]
F['pool_dup'] = sum(F['pool_raw_rows']) - F['pool_sum']
F['pool_n25'] = [len(x) for x in POOL25]
F['pool_union25'] = len(UNION25)
F['pool_widen'] = F['pool_union25'] - F['pool_union']


def pres_n(k):
    return len([1 for x in POOL if k in x])


F['pool_tier'] = [len([k for k in UNION if pres_n(k) == m]) for m in range(1, NSRC + 1)]
F['pool_pair'] = dict((u'%s-%s' % (LBL[a], LBL[b]), len(POOL[a] & POOL[b])) for a, b in PAIRS)
F['pool_trip'] = dict((u'%s-%s-%s' % (LBL[a], LBL[b], LBL[c]), len(POOL[a] & POOL[b] & POOL[c]))
                      for a, b, c in TRIPS)
F['pool_quad'] = dict((u'%s-%s-%s-%s' % (LBL[a], LBL[b], LBL[c], LBL[d]),
                       len(POOL[a] & POOL[b] & POOL[c] & POOL[d])) for a, b, c, d in QUADS)
F['pool_pair_tot'] = sum(F['pool_pair'].values())
F['pool_trip_tot'] = sum(F['pool_trip'].values())
F['pool_quad_tot'] = sum(F['pool_quad'].values())
F['pool_ie_close'] = F['pool_sum'] - F['pool_pair_tot'] + F['pool_trip_tot'] - F['pool_quad_tot'] \
    - F['pool_union']
RFCSET = set(LBL[i] for i in RFCI)
PAPSET = set(LBL[i] for i in PAPI)
RFCPAIR = [k for k in F['pool_pair'] if all(z in RFCSET for z in k.split(u'-'))]
PAPAIR = [k for k in F['pool_pair'] if any(z in PAPSET for z in k.split(u'-'))]
F['pool_pair_by'] = [F['pool_pair'][u'%s-%s' % (LBL[a], LBL[b])] for a, b in PAIRS]
F['pool_pair_rfc_keys'] = sorted(RFCPAIR)
F['pool_pair_rfc'] = sum(F['pool_pair'][k] for k in RFCPAIR)
F['pool_pair_paper'] = sum(F['pool_pair'][k] for k in PAPAIR)
F['pool_pair_paper_n'] = len([k for k in PAPAIR if F['pool_pair'][k] == 0])
F['pool_max_pair'] = max(F['pool_pair'].values())
F['pool_min_pair_rfc'] = min(F['pool_pair'][k] for k in RFCPAIR)
F['pool_tier_close'] = sum(F['pool_tier']) - F['pool_union']
F['pool_sum_close'] = sum(F['pool_tier'][m] * (m + 1) for m in range(NSRC)) - F['pool_sum']
# 共用的到底是哪些行: 按“带不带义务词 ⇎ 带不带 RFC 编号”分档现读
SHARED = set()
for k in RFCPAIR:
    a, b = [LBL.index(z) for z in k.split(u'-')]
    SHARED |= (POOL[a] & POOL[b])
F['pool_shared_rfc'] = len(SHARED)
F['pool_shared_toned'] = len([x for x in SHARED if TONED(x)])
F['pool_shared_rfcline'] = len([x for x in SHARED if cnt_re(x, u'RFC') > 0])
F['pool_shared_status'] = len([x for x in SHARED if cnt_re(x.lower(), u'status of this document') > 0])
F['pool_paper_in_toned'] = sum(len([x for x in POOL[i] if TONED(x)]) for i in PAPI)
F['pool_rfc_in_toned'] = sum(len([x for x in POOL[i] if TONED(x)]) for i in RFCI)


# ---------- 转置尺: 族量按“这一式在五份里各读几枚”横过来逐份读 ----------
F['unit_docs'] = [[F['unit'][i][k] for i in range(NSRC)] for k in range(len(UNIT))]
F['unit_word_docs'] = [[F['unit_word'][i][k] for i in range(NSRC)] for k in range(len(UNIT))]
F['spell_docs'] = [[F['spell'][i][k] for i in range(NSRC)] for k in range(len(SPELL))]
F['term_docs'] = [[F['term'][i][k] for i in range(NSRC)] for k in range(len(TERM))]
F['tone_docs'] = [[F['tone_sh'][i][k] for i in range(NSRC)] for k in range(5)]
F['num_docs'] = [[F['num'][i][k] for i in range(NSRC)] for k in range(len(NUM))]
F['num_cold'] = [NUM[k] for k in range(len(NUM)) if sum(F['num_docs'][k]) == 0]
F['num_cold_n'] = len(F['num_cold'])
F['num_hot_n'] = len(NUM) - F['num_cold_n']
F['num_own_tot'] = sum(len(x) for x in F['num_own'])
F['cfg_own_tot'] = sum(len(x) for x in F['cfg_own'])
F['term_own_tot'] = sum(len(x) for x in F['term_own'])
F['spell_tot'] = [sum(x) for x in F['spell_docs']]
F['term_tot'] = [sum(x) for x in F['term_docs']]
F['unit_tot'] = [sum(x) for x in F['unit_docs']]
F['role_by_face'] = [[sum(F['role_line'][i]) if k == 0 else sum(F['role_fold'][i]) if k == 1
                      else sum(F['role_sh'][i]) if k == 2 else sum(F['role_lig'][i])
                      for i in range(NSRC)] for k in range(4)]
F['face_tot'] = [sum(F['role_by_face'][k]) for k in range(4)]
F['face_gain'] = [F['face_tot'][k] - F['face_tot'][k - 1] for k in range(1, 4)]
F['face_mono'] = sum([1 for k in range(1, 4) if F['face_tot'][k] >= F['face_tot'][k - 1]])
# 增益按“枚”记而不只按“针”记: 一根针可以在别处行内读通、又在某处被换行切开, 那样它进不了切开针清单
# 却照样给折平档添上一枚——两把口径的差必须显式登记, 不然“针数=增益”这一眼看上去就对的话是假的
F['gain_fold'] = [F['role_fold'][i][k] - F['role_line'][i][k]
                  for i in range(NSRC) for k in range(len(ROLEN))]
F['gain_sh'] = [F['role_sh'][i][k] - F['role_fold'][i][k]
                for i in range(NSRC) for k in range(len(ROLEN))]
F['gain_lig'] = [F['role_lig'][i][k] - F['role_sh'][i][k]
                 for i in range(NSRC) for k in range(len(ROLEN))]
F['gain_fold_tot'] = sum(F['gain_fold'])
F['gain_sh_tot'] = sum(F['gain_sh'])
F['gain_lig_tot'] = sum(F['gain_lig'])
F['gain_fold_key'] = len([x for x in F['gain_fold'] if x > 0])
F['gain_sh_key'] = len([x for x in F['gain_sh'] if x > 0])
F['gain_fold_dup'] = sum([F['role_fold'][i][k] - F['role_line'][i][k] for i in range(NSRC)
                          for k in range(len(ROLEN)) if F['role_line'][i][k] > 0])
F['gain_sh_dup'] = sum([F['role_sh'][i][k] - F['role_fold'][i][k] for i in range(NSRC)
                        for k in range(len(ROLEN)) if F['role_fold'][i][k] > 0])
F['ans_words_tot'] = sum(F['ans_words'])
F['sec_lines_tot'] = sum(F['sec_lines'])
F['sec_chars_tot'] = sum(F['sec_chars'])
F['sec_tone_tot_all'] = sum(F['sec_tone_tot'])

# ---------- 被换行切开的义务词: 原面读不到 ⇎ 摘壳折平读得到的那一式, 由逐行面现定位 ----------
def tone_straddle_pair(i, nd):
    """在逐行面上找“上一行以此式的前词收尾 ⇎ 下一行以后词起头”的行对——原面里两行之间隔着换行,
    字面尺读不通; 折平之后才成为一式。相邻行=硬换行切开, 隔行=页壳切开, 两档分账。"""
    w = nd.split(u' ')
    out = []
    for m in range(len(FD[i]) - 1):
        if FD[i][m][2].endswith(w[0]) and FD[i][m + 1][2].startswith(u' '.join(w[1:])):
            out.append((FD[i][m][0], FD[i][m + 1][0]))
    return out


TSK = [k for k in range(5) if F['tone_straddle_k'][4][k]]
F['tone_straddle_nd'] = [TONE[k] for k in TSK]
TSP = []
for kk in TSK:
    TSP.extend(tone_straddle_pair(4, TONE[kk]))
F['tone_straddle_lines'] = [list(x) for x in TSP]
F['tone_straddle_n'] = len(TSP)
F['tone_straddle_adj'] = len([x for x in TSP if x[1] - x[0] == 1])
F['tone_straddle_shell'] = F['tone_straddle_n'] - F['tone_straddle_adj']
F['tone_straddle_ledger'] = F['tone_straddle'][4] - F['tone_straddle_n']
assert F['tone_straddle_n'] >= 1 and F['tone_straddle_ledger'] == 0

CLOSE2 = {}
CLOSE2[u'seg_rt_all'] = 1 if F['seg_rt_ok'] == F['seg_rt_n'] else 0
CLOSE2[u'split_reverse_cold'] = 1 if (F['split_full_on_head'] == 0 and F['split_half_ok'] == F['split_n']) else 0
CLOSE2[u'split_ledger_close'] = 1 if F['split_ledger'] == 0 and F['split_wrap_n'] == sum(F['role_wrap_n']) \
    and F['split_shell_n'] == len(F['role_shell_needles']) else 0
CLOSE2[u'shell_split_has_shell'] = 1 if (len(F['split_shell_between']) == F['split_shell_n']
                                         and sum(1 for x in F['split_shell_between'] if x >= 1)
                                         == F['split_shell_n']) else 0
CLOSE2[u'ans_ruler_rematch'] = 1 if (F['ans_line_close'] == 0 and F['ans_span_close'] == 0) else 0
CLOSE2[u'kw_three_variants'] = 1 if (F['kw_same_7567_8033'] == 0 and F['kw_all_same'] == 0
                                     and F['kw_max_head'] == F['pre_kw_7567_8033']
                                     and F['kw_min_head'] < F['kw_max_head']
                                     and F['suf_kw_tot'] == F['suf_kw_7567_8033'] == 1) else 0
CLOSE2[u'kw_only_rfc'] = 1 if (F['kw_docs'] == 3 and sum(F['kw_at'][i] for i in PAPI) == -2) else 0
CLOSE2[u'notrec_only_8289'] = 1 if (F['kw_notrec'][2] == 1 and F['kw_notrec'][0] + F['kw_notrec'][1] == 0) else 0
CLOSE2[u'as_desc_amb_resolved'] = 1 if (F['as_desc_n'] == 2
                                        and F['as_desc_rows'][1] == F['blk_hi'][9]
                                        and F['as_desc_rows'][0] < F['blk_lo'][9]) else 0
CLOSE2[u'paper_pool_cold'] = 1 if (F['pool_pair_paper'] == 0
                                   and F['pool_pair_paper_n'] == len(PAPAIR)
                                   and len([k for k in RFCPAIR if F['pool_pair'][k] > 0]) == 3
                                   and F['pool_pair_rfc'] == F['pool_pair_tot']) else 0
CLOSE2[u'pool_ie'] = 1 if F['pool_ie_close'] == 0 else 0
CLOSE2[u'blk_one_line_only_paper'] = 1 if (F['blk_one_line_n'] == 2
                                           and sum(F['blk_is_one_line'][i] for i in PAPI) == 2
                                           and sum(F['blk_is_one_line'][i] for i in RFCI) == 0) else 0
CLOSE2[u'blk_tone_ruler'] = 1 if F['blk_tone_ruler_close'] == 0 else 0
CLOSE2[u'only_8289_tone_straddle'] = 1 if (F['tone_straddle'] == [0, 0, 0, 0, 1]
                                           and F['tone_straddle_k'][4][2] == 1
                                           and F['tone_straddle_n'] == F['tone_straddle'][4]) else 0
CLOSE2[u'pp_gap_is_shell_nonblank'] = 1 if F['pp_gap_close'] == 0 and sum(F['pp_gap_rows']) > 0 else 0
CLOSE2[u'num_cold_split'] = 1 if (F['num_cold_n'] + F['num_hot_n'] == len(NUM)
                                  and F['num_cold_n'] >= 1) else 0
F.update(CLOSE2)

Z2 = []


def ZEXP(expr, what):
    Z2.append((expr, what))
    ZV.append((expr, what))


ZEXP(u"B81V('pp_gap_close')", u'片段序列比非空行少的行数 = 非空壳行枚数: 摘壳丢下的每一行都记在页壳上')
ZEXP(u"sum(B81V('pp_rows')) + sum(B81V('shell_lines')) - sum(B81V('lines'))",
     u'片段序列行数加壳行数等于原行数(空行全归壳, 无一行两头都不算)')
ZEXP(u"B81V('split_ledger')", u'切开针总数 = 逐行漏读针总数(硬换行切开 ⇎ 页壳切开, 两档无重叠)')
ZEXP(u"B81V('split_wrap_n') - sum(B81V('role_wrap_n'))",
     u'折平档才读通的针数 = 逐份切开计数之和')
ZEXP(u"B81V('split_shell_n') - len(B81V('role_shell_needles'))",
     u'摘壳档才读通的针数 = 壳切针清单长度')
ZEXP(u"B81V('split_full_on_head')", u'反向对照: 跨行针的整串拿到首行那一行内应当一枚也读不通')
ZEXP(u"B81V('split_half_ok') - B81V('split_n')", u'每根跨行针的两半各自回自己那一行读得通')
ZEXP(u"B81V('seg_rt_ok') - B81V('seg_rt_n')",
     u'段窗首末行自验: 每一枚段针的头一枚词都落在段窗报出的那一行内')
ZEXP(u"B81V('seg_rt_whole') + B81V('seg_rt_cut') - B81V('seg_rt_n')",
     u'段针两档相加=总数: 整针在一行 ⇎ 被硬换行推到下一行, 无第三档')
ZEXP(u"B81V('seg_rt_head') + B81V('seg_rt_tail') - B81V('seg_rt_ok')",
     u'落到所报行的段针按侧相加=总数: 段首看头一枚词 ⇎ 段末看末一枚词')
ZEXP(u"B81V('ans_line_close') + B81V('ans_span_close')",
     u'答句行号与跨行数由段窗尺重导一遍, 与建条侧逐份同值')
ZEXP(u"sum(B81V('ans_row_ledger'))", u'首末行行距减窗口内实有行数=零(答句所在段无空行壳行)')
ZEXP(u"B81V('pool_ie_close')", u'容斥: 各份之和 − 两两共用 + 三三共用 = 并集')
ZEXP(u"B81V('pool_tier_close')", u'按“几份共用”分档相加 = 并集枚数')
ZEXP(u"B81V('pool_sum_close')", u'分档乘份数相加 = 各份枚数之和')
ZEXP(u"B81V('pool_pair_tot') - B81V('pool_pair_rfc')",
     u'两两共用合计 = 三份 RFC 之间的那些(论文与谁都不共用)')
ZEXP(u"B81V('pool_pair_paper')", u'凡牵进一份论文的配对, 共用长行全为零')
ZEXP(u"B81V('pool_sum') - sum(B81V('pool_raw_rows')) + B81V('pool_dup')",
     u'去重枚数 = 原行枚数 − 重复印的次数')
ZEXP(u"B81V('kw_max_head') - B81V('pre_kw_7567_8033')",
     u'三段模板段的最长共头就是 7567⇎8033 那一对(8289 多插一枚 NOT RECOMMENDED, 与谁都在那里断开)')
ZEXP(u"B81V('suf_kw_tot') - B81V('suf_kw_7567_8033')",
     u'共尾只可能来自 7567⇎8033 那一对: 8289 那一段以 RFC 8174 的措辞收尾, 与谁都不共尾')
ZEXP(u"B81V('as_desc_rows')[1] - B81V('blk_hi',9)",
     u'“as described in” 的第二枚候选行就是关键词模板段的末行(锚带下限取的那一枚)')
ZEXP(u"B81V('kw_notrec_tot') - B81V('kw_notrec')[2]",
     u'模板段里的 NOT RECOMMENDED 只在 8289 那一段出现一次')
ZEXP(u"B81V('kw_docs') - 3", u'“关键词”模板段只在三份 RFC 面上存在(两份论文登记 -1)')
ZEXP(u"B81V('num_cold_n') + B81V('num_hot_n') - len(B81V('num_fam'))",
     u'数值十七式按“五份全冷 ⇎ 至少一份读通”分家, 两档相加=族长')
ZEXP(u"B81V('face_tot',1) - B81V('face_tot',0) - B81V('gain_fold_tot')",
     u'折平档相对行尺的读数差 = 按枚登记的换行增益')
ZEXP(u"B81V('face_tot',2) - B81V('face_tot',1) - B81V('gain_sh_tot')",
     u'摘壳档相对折平档的读数差 = 按枚登记的页壳增益')
ZEXP(u"B81V('gain_fold_tot') - B81V('split_wrap_n') - B81V('gain_fold_dup')",
     u'换行增益按枚 = 切开针数 + 已在行内读通的针新增的那些枚(两把口径的差单列一格, 不混)')
ZEXP(u"B81V('gain_sh_tot') - B81V('split_shell_n') - B81V('gain_sh_dup')",
     u'页壳增益按枚 = 壳切针数 + 折平档已读通的针新增的那些枚')
ZEXP(u"B81V('face_gain')[2]", u'拆字档相对摘壳档在二十七根判词针上一枚也不新增')
ZEXP(u"B81V('bool_clos2_sum') - B81V('bool_clos2_n')", u'本段布尔门全绿')
F['zid_scan_n'] = len(ZID)
F['zid_scan2_n'] = len(Z2)
F['bool_clos2_n'] = len(CLOSE2)
F['bool_clos2_sum'] = sum(CLOSE2.values())
F['bool_all_n'] = F['bool_clos_n'] + F['bool_clos2_n']
F['bool_all_sum'] = F['bool_clos_sum'] + F['bool_clos2_sum']
# --- SCAN2 END ---

PLBL = [u'%s#%d' % (LBL[i], n + 1) for n, (i, s, e) in enumerate(PINS)]
PAIRLBL = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]


def PJ(name, note=u''):
    return u' ⇎ '.join(V(name, n, u'%s·%s' % (note or name, PLBL[n])) for n in range(len(PINS)))


def PK_(name, note=u''):
    return u' ⇎ '.join(u'%s=%s' % (PAIRLBL[n], V(name, n, u'%s·%s' % (note or name, PAIRLBL[n])))
                       for n in range(len(PAIRS)))


def RK(k, note=u''):
    """第 k 枚判词针的锚: 逐行漏读的那几枚给两半(首行 ⇎ 末行), 其余给整行或整词窗口"""
    i = LBL.index(F['role_src'][k])
    if k in F['split_k']:
        a, b = split_anchor(i, ROLEN[k])
        return u'%s ⇎ %s' % (a, b)
    return AN(i, ROLEN[k])


LINES = []
if PROBE:
    BADREAD = []
    _V0, _J0, _JL0 = V, J, JL

    def V(name, i=None, note=u''):
        try:
            return _V0(name, i, note)
        except Exception as e:
            BADREAD.append((u'V', name, i, repr(e)[:70]))
            return u'?'

    def J(name, note=u''):
        try:
            return _J0(name, note)
        except Exception as e:
            BADREAD.append((u'J', name, None, repr(e)[:70]))
            return u'?'

    def JL(name, note=u''):
        try:
            return _JL0(name, note)
        except Exception as e:
            BADREAD.append((u'JL', name, None, repr(e)[:70]))
            return u'?'

LINES.append(
    u'📜 五份先按版式分家: 三份 RFC Editor 纯文本面 ⇎ 两份 pdftotext 论文面。 字节 ' + J(u'bytes', u'字节')
    + u', 面内码位 ' + J(u'chars', u'码位') + u', 原行 ' + J(u'lines', u'原行') + u' ⇎ 非空行 '
    + J(u'nonblank', u'非空行') + u', 最长行 ' + J(u'maxlen', u'最长行')
    + u' 列——三份规范同为 ' + V(u'maxlen', 0, u'规范基线列') + u' 列硬换行(溢出 ' + J(u'over72', u'超72行')
    + u' 行), 两份论文一行为一段: madp ' + V(u'maxlen', 1, u'madp最长行') + u' 列 ⇎ cake '
    + V(u'maxlen', 3, u'cake最长行') + u' 列。 只有论文面带 CRLF(回车 ' + J(u'cr', u'回车枚')
    + u', 且行数=回车数: ' + J(u'crlf_rows', u'CRLF整行') + u'), 换页符 ' + J(u'ff', u'换页枚')
    + u' 枚里独占一行的 ' + J(u'ff_exact', u'独占换页') + u' 枚 ⇎ 嵌在行内的 ' + J(u'ff_inline', u'行内换页')
    + u' 枚。 非 ASCII ' + J(u'nonascii', u'非ASCII') + u' 枚全在两份论文面上(四档账 '
    + J(u'na_ledger', u'四成分账') + u' 归零): 连字 ﬁ/ﬂ ' + JL(u'lig_pair', u'连字对') + u' 枚 ⇎ 希腊字母 '
    + J(u'na_greek', u'希腊字母') + u' 枚 ⇎ 弯引号与破折号 ' + J(u'na_dashq', u'弯引破折')
    + u' 枚; 三份规范面逐枚纯 ASCII(' + EXPR(sum(F['nonascii'][i] for i in RFCI),
       u"sum([B81V('nonascii',0),B81V('nonascii',2),B81V('nonascii',4)])", u'规范面非ASCII')
    + u' 枚)。 四档口径的字符账: 全篇折平 ' + J(u'fold_chars', u'折平字符') + u' ⇎ 摘壳折平 '
    + J(u'sh_chars', u'摘壳字符') + u' ⇎ 摘壳加拆字 ' + J(u'shlig_chars', u'拆字字符')
    + u'; 摘壳少读 ' + J(u'sh_minus_fold', u'摘壳差') + u' 字符 ⇎ 拆字加回 ' + J(u'lig_char_add', u'拆字增字符')
    + u' 字符(与连字枚数逐份同值, 账 ' + J(u'lig_add_close', u'拆字账') + u')。 页壳行 '
    + J(u'shell_lines', u'壳行') + u' 行 = 空行 ' + J(u'blank', u'空行') + u' ⇎ 非空壳行 '
    + J(u'shell_nonblank', u'非空壳行') + u' 行(论文 cake 一枚也没有: ' + J(u'shell_blank_only', u'只吃空行')
    + u'); 页码行 ' + J(u'pg_lines', u'页码行') + u' 行 ⇎ 眉行 ' + J(u'hdr_lines_tight', u'眉行')
    + u' 行, 账 ' + J(u'shell_ledger', u'壳账') + u' 全平。 用“整行只由数字与空格组成”当页码尺会吃掉表格: naive '
    + J(u'pgnum_naive', u'naive页码') + u' 枚里真页码只有 ' + J(u'pgnum_ffled', u'FF页码')
    + u' 枚, 多吃 ' + J(u'pgnum_overstrip', u'多吃页码') + u' 枚(整行只由数字与空格组成的表格行), '
    + u'再放宽到“数字成两段以上”还要多吃 ' + J(u'pgnum_ruler_gap', u'尺差') + u' 枚。')

LINES.append(
    u'🪜 同一个问题(排队延迟压到多少 ⇎ 依据什么)五份各答一次, 五句答话逐字取面: '
    + AN(0, WIN[0], 1000) + u'(§4.3 标题行, ' + V(u'ans_words', 0, u'答句词数·7567') + u' 词单行读全, 通篇不带句点: '
    + J(u'ans_punct', u'答句带句点') + u'); ⇎ ' + AN(1, WIN[1]) + u'; ⇎ ' + AN(2, WIN[2]) + u'; ⇎ '
    + AN(3, WIN[3]) + u'; ⇎ ' + AN(4, WIN[4]) + u'。 答句 ' + J(u'ans_words', u'答句词数') + u' 词 ⇎ 整句跨 '
    + J(u'ans_span', u'答句跨行') + u' 行 ⇎ 锚针本身只跨 ' + J(u'ans_needle_span', u'锚针跨行')
    + u' 行(句比针多 ' + J(u'ans_needle_gap', u'针句行差') + u' 行) ⇎ 所在自然段 '
    + J(u'ans_block_lines', u'段行数')
    + u' 行 ⇎ 段内页壳行 ' + J(u'ans_shell_rows', u'段内壳行') + u' 行; 整句一行读全的 '
    + V(u'ans_one_line_n', None, u'单行读全数') + u' 份 ⇎ 合计 ' + V(u'ans_span_tot', None, u'答句跨行合计')
    + u' 行。 行号 ' + J(u'ans_anchor_line', u'答句行号') + u' 由“取面上最后一次命中”导出(7567 的标题在目录 '
    + V(u'sec_toc_line', 0, u'目录行') + u' 行也印一次), 再由段窗尺拿整句重导一遍对拍: 首行差合计 '
    + V(u'ans_line_close', None, u'行号对拍') + u' ⇎ 跨行差合计 ' + V(u'ans_span_close', None, u'跨行对拍')
    + u' ⇎ 句窗内空壳账 ' + J(u'ans_row_ledger', u'句窗空壳') + u'。')

LINES.append(
    u'🔤 术语先分家: queuing/queueing 两拼 ' + JL(u'spell', u'两拼') + u' 枚, 少数拼式 '
    + J(u'spell_minor', u'少数拼') + u' ⇎ 多数拼式 ' + J(u'spell_major', u'多数拼')
    + u'(账 ' + J(u'spell_sum_close', u'两拼账') + u'), 只读到一个方向的 ' + V(u'spell_one_n', None, u'单向份数')
    + u' 份; 短语式(“queue delay/queuing delay/queueing delay”) ' + J(u'spell_phrase_sum', u'短语式')
    + u' 枚, 其中 -ing/-e- 两式并存 ' + J(u'spell_phrase_two', u'短语两式') + u' 枚。 delay ⇎ latency 的对峙 '
    + J(u'term', u'术语族') + u' 枚, 偏斜比 ' + J(u'term_skew', u'偏斜比') + u'(8289 一边倒 '
    + V(u'term_skew', 4, u'偏斜·8289') + u'), 少数侧最小值 ' + V(u'term_minor', 4, u'少数侧·8289')
    + u' 枚——没有一枚是零, 所以不能说“只用一个词”, 只能说一边倒; 独有术语 ' + JL(u'term_own', u'独有术语')
    + u'。 逗留时间 sojourn 只活在 8289(' + EXPR(F['term'][4][7], u"B81V('term',4)[7]", u'sojourn·8289')
    + u' 枚 ⇎ 其余四份 '
    + EXPR(sum(F['term'][i][7] for i in range(4)),
           u"B81V('term',0)[7]+B81V('term',1)[7]+B81V('term',2)[7]+B81V('term',3)[7]", u'sojourn 别份')
    + u' 枚)。 同一根针换尺要分账: 子串尺比词窗尺多读 ' + J(u'spell_ruler_gap', u'拼写尺差') + u' ⇎ '
    + J(u'term_ruler_gap', u'术语尺差') + u' 枚(delayed ⇎ latency-related 这类词内部吃掉的)。 RTT 三把尺: 紧 '
    + J(u'rtt_tight', u'RTT紧尺') + u' ⇎ 字距拉开 ' + J(u'rtt_kern', u'字距拉开') + u' ⇎ 裸子串 '
    + J(u'rtt_loose', u'裸子串') + u' 枚, 裸子串的假命中 ' + J(u'rtt_loose_false', u'裸子串假命中')
    + u' 枚住在这些词里(由面上位置现取): ' + u' ⇎ '.join(
        u'%s=%s' % (LBL[i], u','.join(F['rtt_false_words'][i]) if F['rtt_false_words'][i] else u'无')
        for i in range(NSRC)) + u'。')

LINES.append(
    u'🔢 时长写法三代同库: 单位六式 ' + JL(u'unit', u'单位族') + u', 整词尺 ' + JL(u'unit_word', u'单位整词')
    + u', 子串尺多读 ' + J(u'unit_sub_over', u'单位尺差') + u' 枚(requirements 里的 m/s ⇎ milliseconds 里的 ms)。 '
    + u'8033 通篇把毫秒写全: 缩写 ms 整词 ' + EXPR(F['unit_word'][2][0], u"B81V('unit_word',2)[0]", u'8033的ms整词')
    + u' 枚 ⇎ 全称 ' + EXPR(F['num'][2][NUM.index(u'15 milliseconds')], u"B81V('num',2)[10]", u'15 milliseconds·8033')
    + u'/' + EXPR(F['num'][2][NUM.index(u'150 milliseconds')], u"B81V('num',2)[11]", u'150 milliseconds·8033')
    + u'/' + EXPR(F['num'][2][NUM.index(u'15 microseconds')], u"B81V('num',2)[12]", u'15 microseconds·8033')
    + u'/' + EXPR(F['num'][2][NUM.index(u'150 microseconds')], u"B81V('num',2)[13]", u'150 microseconds·8033')
    + u' 枚全称(缩写形一枚也不给); '
    + u'单位表在拆字前后读数相等(账 ' + J(u'num_lig_gap', u'数值拆字账') + u')。 '
    + u'数值集(数字串就地读单位, 去重): ' + JL(u'numvals', u'数值集') + u', 共 '
    + J(u'numval_n', u'数值枚数') + u' 项——7567 一枚带单位时长也没有(' + V(u'numval_n', 0, u'数值枚·7567')
    + u' 项), 它只把定性话写成规范: '
    + AN(0, u'without incurring undue loss or undue round-trip delay') + u'。 宽尺(容裸 s)与严尺的差: 多读 '
    + EXPR(sum(len(x) for x in F['numval_s_extra']), u"sum(len(B81V('numval_s_extra',i)) for i in range(5))",
           u'宽尺多读') + u' 项 ⇎ 丢 ' + EXPR(sum(len(x) for x in F['numval_s_lost']),
           u"sum(len(B81V('numval_s_lost',i)) for i in range(5))", u'宽尺丢') + u' 项。 '
    + u'数值十七式五份全冷的 ' + V(u'num_cold_n', None, u'全冷式') + u' 式(' + u','.join(F['num_cold'])
    + u'), 至少一份读通 ' + V(u'num_hot_n', None, u'读通式') + u' 式; 各家独有 ' + JL(u'num_own', u'独有数值')
    + u' 共 ' + V(u'num_own_tot', None, u'独有数值合计') + u' 式。 100 ms 这一枚值在六句判词里指六件事: madp '
    + EXPR(F['ms100_count'][1], u"B81V('ms100_count',1)", u'100ms·madp') + u' 枚 ⇎ 8289 '
    + EXPR(F['ms100_count'][4], u"B81V('ms100_count',4)", u'100ms·8289') + u' 枚 ⇎ 其余三份 '
    + EXPR(sum(F['ms100_count'][i] for i in (0, 2, 3)),
           u"B81V('ms100_count',0)+B81V('ms100_count',2)+B81V('ms100_count',3)", u'100ms·别三份')
    + u' 枚; 角色清单 '
    + u' ⇎ '.join(u'%s“%s”' % (x[0], x[1]) for x in F['ms100_roles']) + u'('
    + EXPR(len(F['ms100_roles']), u"len(B81V('ms100_roles'))", u'100ms角色数')
    + u' 个角色)。 madp 那两枚全住在引述句里(引别家的假设 ⇎ 评别家的默认, 自己不立一个新数): '
    + AN(1, u'its default 5 ms of maximum allowed queuing delay') + u'。')

LINES.append(
    u'✂ 判词针族 ' + EXPR(len(ROLEN), u"len(B81V('role_fam'))", u'判词针数') + u' 枚走四档口径: 逐行 '
    + V(u'role_line_read_n', None, u'行尺读通') + u' 枚读通 ⇎ ' + V(u'role_line_miss_n', None, u'行尺漏读')
    + u' 枚读不通(' + V(u'face_tot', 0, u'行尺合计') + u' 次命中), 折平 '
    + V(u'face_tot', 1, u'折平合计') + u' 次 ⇎ 摘壳 '
    + V(u'face_tot', 2, u'摘壳合计') + u' 次 ⇎ 拆字 '
    + V(u'face_tot', 3, u'拆字合计')
    + u' 次, 增益 ' + JL(u'face_gain', u'口径增益') + u' ⇎ 单调 ' + V(u'face_mono', None, u'单调档') + u' 档。 '
    + u'增益按枚记账比按针记账多 ' + EXPR(F['gain_fold_tot'] + F['gain_sh_tot'] - F['split_n'],
       u"B81V('gain_fold_tot')+B81V('gain_sh_tot')-B81V('split_n')", u'枚针账差')
    + u' 枚: 折平档 ' + V(u'gain_fold_tot', None, u'折平增益枚') + u' 枚 = 切开针 '
    + V(u'split_wrap_n', None, u'换行切开数') + u' 枚 + 别处已读通的针新添的 '
    + V(u'gain_fold_dup', None, u'折平重复增益') + u' 枚(7567 的规范性标题: 正文那一枚在 '
    + V(u'sec_body_line', 0, u'标题正文行') + u' 行行内读通, 目录那一枚被换行推到 '
    + V(u'sec_toc_line', 0, u'目录行') + u'→下一行才成式); '
    + u'摘壳档 ' + V(u'gain_sh_tot', None, u'摘壳增益枚') + u' 枚 = 壳切针 ' + V(u'split_shell_n', None, u'壳切数')
    + u' 枚 + ' + V(u'gain_sh_dup', None, u'摘壳重复增益') + u' 枚; 拆字档 ' + V(u'gain_lig_tot', None, u'拆字增益枚')
    + u' 枚。 '
    + u'逐行读不通的 ' + V(u'role_line_miss_n', None, u'漏读针数') + u' 枚分两种。 硬换行切开('
    + J(u'role_wrap_n', u'换行切开') + u' 枚): ' + RK(18) + u' ⇎ ' + RK(24) + u'; 页壳从中间切开('
    + EXPR(len(SHELLK), u"len(B81V('role_shell_needles'))", u'壳切针数') + u' 枚): ' + RK(25) + u' ⇎ ' + RK(26)
    + u'。 两半各回自己那一行都读得通(' + V(u'split_half_ok', None, u'两半读通') + u'/'
    + V(u'split_n', None, u'切开针数') + u' 枚), 整串拿到首行那一行内一枚也读不通(反向对照 '
    + V(u'split_full_on_head', None, u'整串首行') + u' 命中); 壳切那两枚的两行之间确实夹着非空壳行: '
    + JL(u'split_shell_between', u'壳切夹壳行') + u' 枚。 切开总账 ' + V(u'split_ledger', None, u'切开总账')
    + u' ⇎ 跨行幅度合计 ' + V(u'split_span_tot', None, u'跨行幅度') + u' 行 ⇎ 两半字数 '
    + J(u'split_head_chars', u'首半字数') + u'+' + J(u'split_tail_chars', u'末半字数') + u'='
    + V(u'split_rows_tot', None, u'两半合计') + u' 字符。 语气词也被硬换行切开: 摘壳档比原面多读 '
    + J(u'tone_straddle', u'语气切开') + u' 枚, 全在 8289, 一式(' + J(u'tone_straddle_k', u'切开式分布')
    + u' 逐式)——上一行以 ' + AN(4, u'that extra delay') + u' 收尾, 下一行以 '
    + AN(4, u'not be adjusted for such short-term bursts') + u' 起头, SHOULD NOT 因此只在折平后成式。 '
    + u'行对 ' + V(u'tone_straddle_n', None, u'切开行对') + u' 对里相邻 '
    + V(u'tone_straddle_adj', None, u'相邻行对') + u' 对(隔页壳 ' + V(u'tone_straddle_shell', None, u'隔壳行对')
    + u' 对), 行号 ' + EXPR(F['tone_straddle_lines'][0][0], u"B81V('tone_straddle_lines')[0][0]", u'切开首行')
    + u'→' + EXPR(F['tone_straddle_lines'][0][1], u"B81V('tone_straddle_lines')[0][1]", u'切开末行')
    + u', 切开账减摘壳增益 ' + V(u'tone_straddle_ledger', None, u'切开差账') + u'。')

TOCT = split_anchor(0, u'AQM Algorithm Deployment SHOULD NOT Require Operational Tuning')
LINES.append(
    u'🏷 免配置这一主张在三份文书里安在三个位置: 7567 把它写成规范性标题('
    + ANX(0, u'4.3.  AQM Algorithm Deployment SHOULD NOT Require Operational Tuning')
    + u'; 同一串在目录 ' + V(u'sec_toc_line', 0, u'目录行') + u' 行被硬换行切开: '
    + TOCT[0] + u' → ' + TOCT[1]
    + u', 到正文 ' + V(u'sec_body_line', 0, u'正文行') + u' 行才一行读全), '
    + u'8033 把它写成陈述句(' + AN(2, u'PIE is intended to be self-configuring') + u'), 8289 把它写成结论句('
    + AN(4, u'parameter-free for consumer use') + u'); cake 一处也不写(宣称族六式命中 '
    + V(u'cfg_claim', 3, u'宣称·cake') + u' 枚)。 族内独有 ' + JL(u'cfg_own', u'独有宣称') + u' 共 '
    + V(u'cfg_own_tot', None, u'独有宣称合计') + u' 式 ⇎ 全家命中 ' + JL(u'cfg', u'宣称族') + u'。 '
    + u'“configuration” 一词在 cake 面上不拆字读不到: 拆字增益 ' + J(u'cfg_lig_gain', u'拆字增益')
    + u' 枚 ⇎ 拆字读数 ' + J(u'cfg_lig_needle', u'拆字读数') + u' 枚 ⇎ 受益词数 ' + J(u'cfg_lig_words', u'受益词数')
    + u'——madp 有 ' + EXPR(F['lig_pair'][1][0], u"B81V('lig_pair',1)[0]", u'madp的fi') + u'+'
    + EXPR(F['lig_pair'][1][1], u"B81V('lig_pair',1)[1]", u'madp的fl')
    + u' 枚连字却没有一枚落在 config 族里。 节窗: ' + J(u'sec_no', u'节号') + u' 节 ⇎ '
    + J(u'sec_lines', u'节行数') + u' 行 ⇎ ' + J(u'sec_chars', u'节字符') + u'(占摘壳面 '
    + J(u'sec_span_pct', u'节占比') + u'%), 节内义务词 ' + J(u'sec_tone_tot', u'节内义务词') + u' 枚(合计 '
    + V(u'sec_tone_tot_all', None, u'节内义务词合计') + u'——三份论文面与 8033 的节窗一枚也不给)。 '
    + u'标题分档 ' + V(u'head_tone_toc', 0, u'目录档') + u'/' + V(u'head_tone_list', 0, u'列表档') + u'/'
    + V(u'head_tone_sec', 0, u'正文档') + u'/' + V(u'head_tone_stray', 0, u'零余') + u' 枚(7567), 形尺总数 '
    + V(u'head_tone_shape', 0, u'形尺总数') + u' 枚 ⇎ 逐档账 ' + J(u'head_tier_close', u'逐档账') + u'; 目录引道符: '
    u'常规点线尺读 ' + J(u'head_toc_leader_strict', u'点线尺') + u' 枚 ⇎ 空格点尺读 '
    + J(u'head_toc_leader_spaced', u'空格点尺') + u' 枚(其余三枚的点线被 72 列换行推到下一行)。 '
    + u'8289 的答案句在 §4 总述节第 ' + V(u'sec_body_line', 4, u'8289正文行') + u' 行, 专讲 TARGET 的 §4.3 在 '
    + V(u'sec_sub_line', None, u'子节行') + u' 行 ⇎ 相隔 ' + EXPR(F['sec_sub_line'] - F['sec_body_line'][4],
       u"B81V('sec_sub_line')-B81V('sec_body_line',4)", u'子节距离') + u' 行。')

LINES.append(
    u'🎭 语态与引用两条尺: 第一人称动词式(we propose/show/observe/present) ' + J(u'voice_weverb', u'第一人称动词')
    + u' 枚 ⇎ 非人称式(this document ⇎ this memo) ' + J(u'voice_impersonal', u'非人称') + u' 枚 ⇎ we 计数 '
    + J(u'voice_we', u'we计数') + u' 枚——规范面的 we 一枚也不比论文少(8289 ' + V(u'voice_we', 4, u'we·8289')
    + u' 枚 ⇎ 两份论文各 ' + V(u'voice_we', 1, u'we·madp') + u'/' + V(u'voice_we', 3, u'we·cake')
    + u' 枚), 所以语态不能当体裁判据; 论文的第一人称就写在实测句里: '
    + AN(3, u'We use the Flent testing tool') + u'。 引用写法分家: 方括号编号 '
    + J(u'cit_brk', u'方括号引用') + u' 枚只在论文面(规范面 '
    + EXPR(sum(F['cit_brk'][i] for i in RFCI), u"B81V('cit_brk',0)+B81V('cit_brk',2)+B81V('cit_brk',4)", u'规范面编号')
    + u' 枚) ⇎ “RFC 编号”式 ' + J(u'cit_rfc', u'RFC式引用') + u' 枚, 论文面也读 '
    + V(u'cit_rfc', 1, u'RFC式·madp') + u'/' + V(u'cit_rfc', 3, u'RFC式·cake') + u' 枚。 谁引谁(在拆字面上数“RFC+编号”紧接): '
    + u' ⇎ '.join(u'%s→%s' % (LBL[i], u','.join(str(x) for x in F['cite_matrix'][i])) for i in range(NSRC))
    + u'; 最新两份(cake ⇎ 8289)对外引用 ' + EXPR(sum(F['cite_matrix'][3]) + sum(F['cite_matrix'][4]),
       u"sum(B81V('cite_matrix',3))+sum(B81V('cite_matrix',4))", u'最新两份外引')
    + u' 枚——8289 不引 7567 也不引 8033, madp→7567 ' + EXPR(F['cite_matrix'][1][0], u"B81V('cite_matrix',1)[0]",
         u'madp引7567') + u' 枚 ⇎ 8033→7567 ' + EXPR(F['cite_matrix'][2][0], u"B81V('cite_matrix',2)[0]",
         u'8033引7567') + u' 枚。 参数名三代: 大写式 ' + J(u'par_upper_n', u'大写参数名') + u' 式 ⇎ 希腊字母 '
    + J(u'par_greek_n', u'希腊参数名') + u' 式 ⇎ 代码式 ' + J(u'par_impl_n', u'代码参数名') + u' 式('
    + u' ⇎ '.join(u'%s:%s' % (LBL[i], u','.join(u'%s=%d' % y for y in F['par_impl'][i]) if F['par_impl'][i] else u'无')
                  for i in range(NSRC)) + u'); 逐式 ' + JL(u'par', u'参数名族') + u' 枚。 '
    + AN(4, u'time_t TARGET = MS2TIME(5)') + u' ⇎ ' + AN(4, u'time_t INTERVAL = MS2TIME(100)')
    + u'——附录代码里的标识符是大写 MS2TIME, 小写 ms2time 在面上读 ' + EXPR(F['par'][4][10],
       u"B81V('par',4)[10]", u'小写ms2time') + u' 枚(反向对照登记的是逐字符等值轨)。')

LINES.append(
    u'📐 套版行池(摘壳后逐行折平——不拆字 ⇎ 不改大小写——长度 ≥40 字符的行去重): 各份 ' + J(u'pool_n', u'池枚数')
    + u' 枚 ⇎ 并集 ' + V(u'pool_union', None, u'池并集') + u' 枚 ⇎ 原行 ' + J(u'pool_raw_rows', u'池原行')
    + u' 枚(同文重印 ' + V(u'pool_dup', None, u'池重印') + u' 枚)。 阈值放宽到 25 字符: 各份 '
    + J(u'pool_n25', u'宽池枚数') + u' ⇎ 并集 '
    + V(u'pool_union25', None, u'宽池并集') + u' 枚(多 ' + V(u'pool_widen', None, u'池放宽增') + u' 枚)。 '
    + u'按“几份共用”分档 ' + J(u'pool_tier', u'池分档') + u' 枚 ⇎ 两两共用 ' + PK_(u'pool_pair_by', u'池配对')
    + u' ⇎ 三三共用 ' + EXPR(F['pool_trip_tot'], u"B81V('pool_trip_tot')", u'三三共用') + u' 枚 ⇎ 四份以上 '
    + V(u'pool_quad_tot', None, u'四份共用') + u' 枚。 容斥账 ' + V(u'pool_ie_close', None, u'容斥账')
    + u'(各份之和 ' + V(u'pool_sum', None, u'池合计') + u' − 两两 ' + V(u'pool_pair_tot', None, u'两两合计')
    + u' + 三三 ' + V(u'pool_trip_tot', None, u'三三合计') + u' = 并集 ' + V(u'pool_union', None, u'池并集2')
    + u')。 牵进一份论文的每一对都是零(' + V(u'pool_pair_paper', None, u'论文配对') + u' 枚, '
    + V(u'pool_pair_paper_n', None, u'零配对数') + u' 对全冷) ⇎ 三份 RFC 之间 '
    + V(u'pool_pair_rfc', None, u'RFC配对') + u' 枚(' + u','.join(F['pool_pair_rfc_keys']) + u'), 最大 '
    + V(u'pool_max_pair', None, u'最大配对') + u' ⇎ 最小 ' + V(u'pool_min_pair_rfc', None, u'最小配对') + u'。 '
    + u'共用的这 ' + V(u'pool_shared_rfc', None, u'共用枚数') + u' 枚里带义务词的 ' + V(u'pool_shared_toned', None, u'共用带义务')
    + u' 枚 ⇎ 带“RFC”字样的 ' + V(u'pool_shared_rfcline', None, u'共用带RFC') + u' 枚 ⇎ 讲“本文档现状”的 '
    + V(u'pool_shared_status', None, u'共用现状行') + u' 枚——套版行就是抬头 ⇎ 关键词 ⇎ 版权那几类, 不是判词。 '
    + u'关键词模板段三份各印一次而互不相同: ' + ANL(0, F['blk_lo'][9], u'The key words') + u' ⇎ '
    + ANL(2, F['blk_lo'][10], u'The key words') + u' ⇎ ' + ANL(4, F['blk_lo'][11], u'The key words') + u'; 两两共头 ' + V(u'pre_kw_7567_8033', None, u'共头7567·8033') + u'/'
    + V(u'pre_kw_7567_8289', None, u'共头7567·8289') + u'/' + V(u'pre_kw_8033_8289', None, u'共头8033·8289')
    + u' 词——最长共头是 ' + V(u'kw_max_head', None, u'最长共头') + u' 词那一对, 8289 与谁都在 '
    + V(u'kw_min_head', None, u'最短共头') + u' 词处断开(它多插一枚 NOT RECOMMENDED: ' + JL(u'kw_notrec', u'关键词NOTREC')
    + u' 枚); 共尾 ' + V(u'suf_kw_7567_8033', None, u'共尾7567·8033') + u'/'
    + V(u'suf_kw_7567_8289', None, u'共尾7567·8289') + u'/' + V(u'suf_kw_8033_8289', None, u'共尾8033·8289')
    + u' 词, 合计 ' + V(u'suf_kw_tot', None, u'共尾合计') + u' 词: 7567 收尾 '
    + ANL(0, F['blk_lo'][9], u'as described in')
    + u' ⇎ 8033 收尾 ' + AN(2, u'in RFC 2119') + u'——两份只差一处措辞, 末一枚同为 “[RFC2119].”; '
    + u'8289 换成 ' + AN(4, u'capitals, as shown here') + u' 一路收尾, 与谁都不共尾。 '
    + u'两份论文面上这一段不存在(口径不存在登记 -1: ' + J(u'kw_at', u'关键词位置') + u' ⇎ 行 '
    + J(u'kw_minus_row', u'关键词行号') + u')。')

LINES.append(
    u'¶ 段落层十四段(五份主答句段 ⇎ 引述段 ⇎ 免配置段 ⇎ 实测段 ⇎ 三份模板段), 每段的行 ⇎ 字符 ⇎ 词 ⇎ 词表: '
    + PJ(u'blk_rows', u'段行数') + u' 行 ⇎ ' + PJ(u'blk_chars', u'段字符') + u' 字符 ⇎ ' + PJ(u'blk_words', u'段词数')
    + u' 词 ⇎ 词表 ' + PJ(u'blk_vocab', u'段词表') + u'; 首行 ' + PJ(u'blk_lo', u'段首行') + u' ⇎ 末行 '
    + PJ(u'blk_hi', u'段末行') + u'。 五段主答句共 ' + V(u'blk_five_rows', None, u'主答句行合计') + u' 行 ⇎ '
    + V(u'blk_five_words', None, u'主答句词合计') + u' 词 ⇎ ' + V(u'blk_five_chars', None, u'主答句字合计')
    + u' 字符, 其中 ' + V(u'blk_one_line_n', None, u'主答句单行') + u' 段在一行里读全——两份论文 (pdftotext 把整段落在一行: madp '
    + V(u'blk_words_per_row', 1, u'每行词·madp') + u' 词一行 ⇎ cake ' + V(u'blk_words_per_row', 3, u'每行词·cake')
    + u' 词一行); 三份 RFC 的段被 72 列硬换行切开 (7567 ' + V(u'blk_words_per_row', 0, u'每行词·7567')
    + u' 词/行 ⇎ 8033 ' + V(u'blk_words_per_row', 2, u'每行词·8033') + u' ⇎ 8289 '
    + V(u'blk_words_per_row', 4, u'每行词·8289') + u' 词/行)。 段内义务词 MUST ' + PJ(u'tone_must_blk', u'段MUST')
    + u' ⇎ MUST NOT ' + PJ(u'tone_mustnot_blk', u'段MUSTNOT') + u' ⇎ SHOULD '
    + PJ(u'tone_should_blk', u'段SHOULD') + u' ⇎ MAY ' + PJ(u'tone_may_blk', u'段MAY')
    + u', 三轨 (逐段现扫 ⇎ 游标步进 ⇎ 正则) 对十四段的差异合计 ' + V(u'blk_tone_ruler_close', None, u'段三轨差')
    + u'; 段内小写 can/should/will ' + PJ(u'blk_lc', u'段小写') + u' 枚。 段窗首行相对答句行 '
    + J(u'blk_head_gap', u'段对答句距') + u' 行: 7567 的正 ' + V(u'blk_head_gap', 0, u'段距·7567')
    + u' 是答句本身就是 §4.3 标题行 ' + V(u'ans_anchor_line', 0, u'答句行·7567')
    + u', 段窗从标题空一行以后的正文起; 两份论文的 0 是一段一行 ⇎ 与答句行重合; 8033 ⇎ 8289 把答句包在段窗后半, 负 '
    + V(u'blk_head_gap', 4, u'段距·8289') + u' 行最深。 '
    + u'段窗行号往返: 十四段的首末行共 ' + V(u'seg_rt_n', None, u'段行复核数')
    + u' 枚针逐枚拿行号回原文件那一行自验, 命中 ' + V(u'seg_rt_ok', None, u'段行通过') + u' 枚 (首侧 '
    + V(u'seg_rt_head', None, u'段针首侧') + u' ⇎ 末侧 ' + V(u'seg_rt_tail', None, u'段针末侧')
    + u'), 其中整针落在一行 ' + V(u'seg_rt_whole', None, u'段针整行') + u' 枚 ⇎ 被硬换行推到相邻行 '
    + V(u'seg_rt_cut', None, u'段针切开') + u' 枚——切开按首侧读下半 ⇎ 末侧读上半来验, 不按整串落一行验。')

LINES.append(
    u'🧮 闭合账口径: 布尔门 ' + V(u'bool_all_n', None, u'布尔门总数') + u' 道全绿(建条侧 '
    + V(u'bool_clos_n', None, u'布尔门·建条') + u' ⇎ 段落侧 ' + V(u'bool_clos2_n', None, u'布尔门·段落')
    + u'), 恒等式 ' + EXPR(len(ZV), u"B81V('zid_scan_n')+B81V('zid_scan2_n')", u'恒等式总数') + u' 条归零(建条侧 '
    + V(u'zid_scan_n', None, u'恒等式·建条') + u' ⇎ 段落侧 ' + V(u'zid_scan2_n', None, u'恒等式·段落') + u')。 '
    + u'与采集遍逐键对账 ' + V(u'pick_agree', None, u'对账相符') + u'/' + V(u'pick_same_n', None, u'对账键数')
    + u' 键符 ⇎ ' + V(u'pick_diff', None, u'对账不符') + u' 键不符; 答句两轨(逐字符句界 ⇎ 采集侧前瞻正则)逐份同串 '
    + J(u'ans_vs_pick', u'答句等值') + u' ⇎ 尾随空白 ' + J(u'ans_tail_ws', u'答句尾空') + u' 字符; 两遍壳谓词逐行同集 '
    + V(u'shell_pred_diff', None, u'壳谓词差') + u' 行分歧。 内容针 ' + V(u'needle_n', None, u'针总数')
    + u' 枚 ⇎ 反向针 ' + V(u'neg_n', None, u'反向针') + u' 枚(' + V(u'neg_probes', None, u'反向探针')
    + u' 次探针在应冷处读 ' + V(u'neg_zero_hits', None, u'反向命中') + u' ⇎ 有主针 ' + V(u'neg_owner_present', None, u'有主针')
    + u'/' + V(u'neg_n', None, u'反向针2') + u' 枚), 子串轨比整词轨多读 ' + V(u'neg_sub_false', None, u'反向假阳')
    + u' 枚, 集中在 ' + u','.join(u'%s@%s=%d⇎%d' % (x[0], x[1], x[2], x[3]) for x in F['neg_sub_false_rows'])
    + u'。 锚只由面上位置导出, 同一串有多枚候选行时带行下限取段内那一枚: 7567 的 “as described in” 全文有 '
    + V(u'as_desc_n', None, u'asDesc枚数') + u' 枚候选, 版权那枚在 ' + V(u'as_desc_rows', 0, u'asDesc版权行')
    + u' 行 ⇎ 关键词段末枚在 ' + V(u'as_desc_rows', 1, u'asDesc段末行')
    + u' 行, 上面引的是末枚(不带上限就会读到版权段的 “Section 4.e”)。')

BADZID = []
for v, w in Z2:
    got = eval(v, {FN: BB81})
    if got != 0:
        BADZID.append((v, w, got))
assert not BADZID, BADZID[:3]
for v, w in Z2:
    reg(u'0', v, w)

body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCHS = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCHS)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦(' + u'|'.join(TAGS) + u')⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
MISSLINE = [x for x in CITES
            if x[1] not in ANSET[IDX[x[0]]] and pnorm(x[1]) not in ROWSRAW[IDX[x[0]]]]
assert not ATOMFAIL, ATOMFAIL[:3]
if not PROBE:
    assert not ERR, ERR[:3]
    assert not MISSLINE, MISSLINE[:3]
AMB = [x for x in ALOG if x[3] > 1]
if PROBE:
    for x in sorted(set(BADREAD)):
        print(u'  读数针落空: %s %s[%s] %s' % x)
    for x in sorted(set(BLKFAIL)):
        print(u'  段针落空: %s %s @%s' % (x[0], x[2], x[1]))
    for x in sorted(set(ATOMFAIL)):
        print(u'  锚针落空: %s %s' % x)
    print(u'探针汇总: 读数 %d ⇎ 段针 %d ⇎ 锚针 %d ｜ 正文 %d 字符 ｜ 多行可读针 %d' % (
        len(BADREAD), len(BLKFAIL), len(ATOMFAIL), len(body), len(AMB)))
    for x in AMB:
        print(u'  针多解: %s 针=%s 首行=%d 候选=%d' % (x[0], x[1], x[2], x[3]))
    raise SystemExit(0)
HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCHS)
CLS = {u'single': len([a for a in ANCHS if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC]),
       u'all5': len([a for a in ANCHS if len(HITC[a]) == NSRC])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'], u'anchor_all5': CLS[u'all5'],
         u'checks': DIST * NSRC, u'enc_chars': len(body.replace(NL, u'')), u'nsrc': NSRC}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all5'] == DIST
F.update(AMETA)
for n, v in sorted(AMETA.items()):
    reg(str(v), u"%s('%s')" % (FN, n), n)


def _walk(v, path):
    if isinstance(v, list):
        for i, x in enumerate(v):
            for it in _walk(x, path + (i,)):
                yield it
    elif isinstance(v, int) and not isinstance(v, bool):
        yield v, path


def _expr(k, path):
    head = u"%s('%s'%s)" % (FN, k, (u', ' + repr(path[0])) if path else u'')
    return head + u''.join(u'[%d]' % i for i in path[1:])


ELEMS = {}
for kk, vv in F.items():
    for num, pp in _walk(vv, ()):
        if num >= 100:
            ELEMS.setdefault(str(num), []).append(_expr(kk, pp))
SRC_HARD = set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', u''.join(T)))
BODY_HARD = sorted(set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', body)
                       if len(m.group(0).rstrip(u'.')) >= 3), key=lambda x: (len(x), x))
NOEXPR = []
for s in BODY_HARD:
    if s in K_ or s in SRC_HARD:
        continue
    got = [e for e in ELEMS.get(s, []) if eval(e, {FN: BB81}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, [(x, body[max(0, body.index(x) - 90):body.index(x) + 30]) for x in NOEXPR[:3]]
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv81.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
F['contract_n'] = len(F) + 1
json.dump(F, io.open(u'corpus/_b81flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms81.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCHS, key=len, reverse=True)) + NL)

CH = dict(AMETA)
CH.update({u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCHS))),
           u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
           u'classes': dict((c, sorted([a for a in ANCHS if len(HITC[a]) == n]))
                            for c, n in ((u'single', 1), (u'cross', 2), (u'three', 3), (u'four', 4), (u'five', 5))),
           u'collisions': dict((k, v) for k, v in COLL.items()),
           u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
           u'deriv_points': sum(len(v) for v in SEENX.values()), u'notes': NOTES,
           u'anchor_ambiguous': len(AMB), u'anchor_lines': [[x[0], x[1], x[2], x[3]] for x in ALOG],
           u'needle_n': F[u'needle_n'], u'zid': [[v, w] for v, w in ZV], u'litk': LITK,
           u'blk': PTXT, u'pins': [[LBL[i], s, e] for i, s, e in PINS],
           u'split': [[LBL[LBL.index(F['role_src'][k])] + u'#' + str(k), ROLEN[k]]
                      for k in F['split_k']],
           u'pool_pair': F['pool_pair'], u'pool_trip': F['pool_trip'],
           u'kw': [PTXT[9], PTXT[10], PTXT[11]],
           u'closure_keys': sorted([k for k in F if u'close' in k or u'ledger' in k]),
           u'flat': F})
json.dump(CH, io.open(u'corpus/_b81checks.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

ANS5 = [u'判词只写成规范标题: 免配置是“SHOULD NOT Require Operational Tuning”, 全文一枚带单位时长也不给',
        u'引述别家默认值作答: PIE 的 20 ms ⇎ CoDel 的 5 ms 与 100 ms 假设, 自己一个新数也不定',
        u'给双档默认: 15/150 milliseconds ⇎ 15/150 microseconds, 并宣称用户不必配置任何设计参数',
        u'不答该压到多少, 只报实测: 50 ms 基线 ⇎ 稳态 200 ms ⇎ 5–500 ms 振荡 ⇎ 代价 5 ms',
        u'给定义式再给导出值: TARGET = RTT 的 5-10%, 由 100 ms 天花板导出 TARGET 5 ms ⇎ INTERVAL 100 ms']
ENTRY = u'corpus/babeltele/B81_aqm_queuing_delay_target_five_answers.md'
srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 码位／原行 %d／非空行 %d／最长行 %d 列／换页 %d 枚／答句 %s)' % (
        PATH[i].split('/')[-1], F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        F[u'maxlen'][i], F[u'ff'][i], ANS5[i]) for i in range(NSRC))
    + u' (三份 RFC Editor 纯文本面 ⇎ 两份 pdftotext 论文面; 换页 ' + str(sum(F[u'ff'])) + u' 枚 ⇎ 页壳行 '
    + str(sum(F['shell_lines'])) + u' 行; 非 ASCII ' + str(sum(F[u'nonascii'])) + u' 枚全在论文面上, '
    + str(sum(F['nonascii'][i] for i in RFCI)) + u' 枚在规范面上——论文带 CRLF('
    + str(sum(F['cr'])) + u' 枚回车)与连字 ' + str(sum(F['lig_total'])) + u' 枚); 抬头年 '
    + u'⇎'.join(str(y) for y in F[u'years']) + u', 跨 ' + str(max(F[u'years']) - min(F[u'years'])) + u' 年; '
      + u'五句答话 ⇎ 十四段段落层 ⇎ 行号尺的往返复核 ⇎ 八枚跨行判词的两半, 全部由面上位置导出, 一个都不手填。 '
      + u'抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页(7567 此刻是否仍挂 BCP、'
        u'8033 与 8289 有没有新 errata 改过这两句默认值)、两份会议论文此刻是否被撤稿或改版、'
        u'现网路由器与内核实现实际取哪个 TARGET(论文 ⇎ 标准给出的数字不等于装机行为)、'
        u'PDF 原版式与此纯文本面的排版差异, 都不可由在库文件判定, 只进解读注, 不进门槛)\n')
link = (u"；联结不是“同一份数据的两种序列化”, 而是“一个 AQM 该把排队延迟压到多少、依据什么”在五份一手文书里的五种答法: "
        u"7567 把主张写成规范性标题(§4.3, 目录 " + str(F[u'sec_toc_line'][0]) + u" 行 ⇎ 正文 "
        + str(F[u'sec_body_line'][0]) + u" 行各印一次), 全文 " + str(F[u'numval_n'][0]) + u" 枚带单位时长; "
        u"⇎ madp 自己不数字, 把 PIE 的 20 ms ⇎ CoDel 的 5 ms 与 100 ms 假设引述一遍("
        + str(F[u'num'][1][NUM.index(u'20 ms')]) + u" 枚 20 ms 全库仅此一份); "
        u"⇎ 8033 给双档默认 15/150 milliseconds ⇎ 15/150 microseconds("
        + str(F[u'numval_n'][2]) + u" 项数值, 缩写 ms 整词 " + str(F[u'unit_word'][2][0]) + u" 枚——通篇写全称); "
        u"⇎ cake 不作任何宣称, 只报实测(宣称族命中 " + str(F[u'cfg_claim'][3]) + u" 枚); "
        u"⇎ 8289 先给定义式 TARGET=RTT 的 5-10%, 再由 100 ms 天花板导出 5 ms ⇎ 100 ms("
        + str(F[u'term'][4][7]) + u" 枚 sojourn 为一家术语)。 术语 ⇎ 单位 ⇎ 语态三线同时分家: delay⇎latency 偏斜 "
        + u'⇎'.join(str(x) for x in F[u'term_skew']) + u" ⇎ 两拼之比为 " + u'⇎'.join(str(x) for x in F[u'term_skew'][:1])
        + u" ⇎ 套版长行池里三份 RFC 之间共用 " + str(F[u'pool_pair_rfc']) + u" 枚而凡牵进论文的每一对为零("
        + str(F[u'pool_pair_paper']) + u" 枚) ⇎ 第一人称动词只在两份论文与 madp 面出现(" + u'⇎'.join(str(x) for x in F[u'voice_weverb']) + u")。\n")
tags = (u'五答: 7567 标题式判词(%d 词单行, 无句点) ⇎ madp 引述别家默认(%d 词跨 %d 行) ⇎ 8033 双档默认全称(%d 词跨 %d 行, 段 %d 行) ⇎ cake 实测基线(%d 词) ⇎ 8289 定义式导出(%d 词跨 %d 行) '
        u'四档口径: 行 %d ⇎ 折 %d ⇎ 摘壳 %d ⇎ 拆字 %d 次命中, 切开救 %d 枚 ⇎ 壳切 %d 枚 ⇎ 拆字新增 %d 枚 '
        u'反向 %d 枚针 %d 次探针全冷, 子串轨假阳 %d 枚 '
        u'节窗 %s ⇎ %s 行 ⇎ 占比 %s%% ⇎ 节内义务词 %s '
        u'套版长行池 %d 枚, 两两 %d ⇎ 三三 %d ⇎ 论文配对 %d, 容斥 %d '
        u'关键词模板段三份各异: 共头 %d/%d/%d 词 ⇎ 共尾 %d/%d/%d ⇎ NOT RECOMMENDED 只在 8289 ⇎ 论文面 -1 '
        u'切开判词 %d 枚两半各归一行, 整串在首行读不通(反向 %d 命中) ⇎ 语气词切开 %s 枚 '
        u'免配置三处安放: 标题 ⇎ 陈述句 ⇎ 结论句 ⇎ cake 一处不写(宣称 %d 枚) '
        u'谱系 %s 跨 %d 年 '
        u'闭合账 布尔门 %d ⇎ 恒等式 %d ⇎ 对账 %d 键符 %d 不符 ⇎ 锚 %d 处去重 %d'
        % (F[u'ans_words'][0], F[u'ans_words'][1], F[u'ans_span'][1], F[u'ans_words'][2], F[u'ans_span'][2],
           F[u'ans_block_lines'][2], F[u'ans_words'][3], F[u'ans_words'][4], F[u'ans_span'][4],
           F[u'face_tot'][0], F[u'face_tot'][1], F[u'face_tot'][2], F[u'face_tot'][3],
           sum(F[u'role_wrap_n']), F[u'split_shell_n'], F[u'face_gain'][2],
           F[u'neg_n'], F[u'neg_probes'], F[u'neg_sub_false'],
           u'⇎'.join(F[u'sec_no']), u'⇎'.join(str(x) for x in F[u'sec_lines']),
           u'⇎'.join(str(x) for x in F[u'sec_span_pct']), u'⇎'.join(str(x) for x in F[u'sec_tone_tot']),
           F[u'pool_union'], F[u'pool_pair_tot'], F[u'pool_trip_tot'], F[u'pool_pair_paper'],
           F[u'pool_ie_close'],
           F[u'pre_kw_7567_8033'], F[u'pre_kw_7567_8289'], F[u'pre_kw_8033_8289'],
           F[u'suf_kw_7567_8033'], F[u'suf_kw_7567_8289'], F[u'suf_kw_8033_8289'],
           F[u'split_n'], F[u'split_full_on_head'], u'⇎'.join(str(x) for x in F[u'tone_straddle']),
           F[u'cfg_claim'][3], u'⇎'.join(str(y) for y in F[u'years']),
           max(F[u'years']) - min(F[u'years']),
           F[u'bool_all_n'], len(ZV), F[u'pick_agree'], F[u'pick_diff'], USED, DIST))
title = (u'# B81 排队延迟该压到多少，五份一手文书五种答法：'
         u'7567 一个带单位的时长也不给（数值集 %d 项），只把答句写成规范性标题（目录 ⇎ 正文各印一次） ⇎ '
         u'madp 面上时长命中 %d 枚，其中“100 ms”%d 枚 ⇎ '
         u'8033 把毫秒写全：全称“15 milliseconds”%d 枚 ⇎ 缩写 ms 整词 %d 枚 ⇎ '
         u'cake 时长 %d 枚 ⇎ 大写义务词 %d 枚（只报实测，不提配置） ⇎ '
         u'8289 把 TARGET 写成 RTT 的比例（“5-10%%”%d 枚）并给“100 ms”%d 枚'
         u'（术语对峙 delay ⇎ latency 偏斜比 %s ⇎ sojourn 只在 8289 %d 枚 ⇎ 别四份 %d 枚；'
         u'套版长行三份 RFC 之间共用 %d 枚 ⇎ 凡牵进论文者 %d 枚）\n') % (
             F[u'numval_n'][0], F[u'num_tot'][1], F[u'ms100_count'][1],
             F[u'num'][2][NUM.index(u'15 milliseconds')], F[u'unit_word'][2][0],
             F[u'num_tot'][3], sum(F[u'tone_sh'][3]),
             F[u'num'][4][NUM.index(u'5-10%')], F[u'ms100_count'][4],
             F[u'term_skew'][4], F[u'term'][4][7], sum(F[u'term'][i][7] for i in range(4)),
             F[u'pool_pair_rfc'], F[u'pool_pair_paper'])
text = (title + srcline + link + tags +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n'
        + u'## ⟪BabelTele⟫\n' + body + u'\n\n'
        + u'## ⛓解读注\n\n（此段由 corpus/_fill81.py 从 corpus/_b81checks.json 与 corpus/_deriv81.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s ｜ 归属错配 %d ⇎ 非锚面线 %d ｜ 多行可读针 %d' % (
    USED, DIST, TAGN, len(ERR), len(MISSLINE), len(AMB)))
for x in AMB:
    print(u'  针多解: %s 针=%s 首行=%d 候选=%d' % (x[0], x[1], x[2], x[3]))
print(u'一源 %d ⇎ 二至四源 %d ⇎ 五源 %d ｜ 段 %d 行合计 %d ⇎ 主答句 %d 行 %d 词 ⇎ 单行段 %d ｜ 段行 %d/%d(整 %d ⇎ 切 %d)' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all5'], len(PINS), F['blk_rows_tot'],
    F['blk_five_rows'], F['blk_five_words'], F['blk_one_line_n'],
    F['seg_rt_ok'], F['seg_rt_n'], F['seg_rt_whole'], F['seg_rt_cut']))
print(u'切开 %d 枚(换行 %d ⇎ 壳 %d) 跨行合计 %d 行 ⇎ 反向首行命中 %d ⇎ 两半 %d/%d' % (
    F['split_n'], F['split_wrap_n'], F['split_shell_n'], F['split_span_tot'],
    F['split_full_on_head'], F['split_half_ok'], F['split_n']))
print(u'池 各份 %s 并集 %d ⇎ 两两 %s ⇎ 三三 %d ⇎ 论文 %d ⇎ 容斥 %d ｜ 关键词共头 %s' % (
    F['pool_n'], F['pool_union'], F['pool_pair'], F['pool_trip_tot'], F['pool_pair_paper'],
    F['pool_ie_close'], [F['pre_kw_7567_8033'], F['pre_kw_7567_8289'], F['pre_kw_8033_8289']]))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ⇎ 恒等式 %d ⇎ 扁平键 %d' % (
    len(DERIV), sum(len(v) for v in SEENX.values()), len(COLL), len(ZERO), len(ZV), len(F)))
print(u'判定 %s' % (dict((k, v) for k, v in CLOSE2.items() if v == 0),))
