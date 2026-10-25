# -*- coding: utf-8 -*-
"""B82 建条目第二遍的发射段: 由 _mkB82.py 在顶层 exec 进来, 与前半共享同一批现读量。
段一 SCAN2 是段落层、行号尺、被换行切开的判词与义务词、被编号切开的判词、套版长行池(按版式两代分家);
锚的机制与 B81 不同: 五份都是 RFC Editor 纯文本面(72 列硬换行), 所以命中区间先经逐字符对照表映回原行,
再按整词切成窗口——拆字表在这份条里是空表(五份面无连字), 映回只处理折平吃掉的行首换页符与行尾空格。
段二是编码区正文, 每一枚三位以上的数都由 V()/J()/EXPR() 注册过算式;
段三自 replay 恒等式、复核锚归属、落盘 flat/deriv/atoms/checks 与条目文件。"""

# --- SCAN2 BEGIN --- (段落层 ⇎ 行号尺 ⇎ 切开判词 ⇎ 义务词跨行 ⇎ 模板行池: 同一段也由 corpus/_wire82.py 机械切进 audit.py::_b82_scan)
TAGS = LBL
IDX = dict((t, n) for n, t in enumerate(LBL))
# 门槛对面(audit.py::_atom_face): 纯文本条目不剥壳, 整份原文归一后就是比对面
FAN = [pnorm(t) for t in T]
ATOMFAIL = []
BLKFAIL = []
PROBE = (u'B82PROBE' in __import__('os').environ)
LIMW = 92
LMAPC = {}
# 建条侧的行号读数先留一份副本, 本段用另一张表重导之后再逐份对拍
F['mk_ans_sent_line'] = list(F['ans_sent_line'])
F['mk_ans_sent_end'] = list(F['ans_sent_end'])
F['mk_ans_sent_span'] = list(F['ans_sent_span'])
F['mk_ans_needle_line'] = list(F['ans_needle_line'])
F['num_fam'] = NUMLIT


def row_fd(raw):
    """折平(词间留一枚空格)并拆字, 同时给每个结果字符记下它来自原行的哪一个下标。
    锚要靠这张表映回原文才谈得上“逐字”: 摘壳丢掉的行首换页符与行尾空格都会让偏移错位,
    所以映射必须与串同时构造, 不能事后按长度折算。"""
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


# 片段序列用采集侧壳谓词(is_shell_pick)挑行, 摘壳面 SHP 用本遍的 token 形状尺(shell_by_shape)——
# 两条独立实现必须逐行给同一个集合, 否则下面 SHC 的重构就对不上。
ROWS = [[(n, x) for n, x in enumerate(L[i], 1) if not is_shell_pick(x, FAM[i])] for i in range(NSRC)]
F['shell_pred_diff'] = sum([1 for i in range(NSRC) for n in range(len(L[i]))
                            if is_shell_pick(L[i][n], FAM[i]) != shell_by_shape(L[i][n], FAM[i])])
FD = []
for i in range(NSRC):
    arr = []
    for n, x in ROWS[i]:
        f, ix = row_fd(x)
        assert len(f) == len(ix) and len(f.lower()) == len(f), (LBL[i], n)
        arr.append((n, x, f, ix))
    FD.append(arr)
    assert [a[1] for a in FD[i]] == SHP[i], i
    assert u' '.join(a[2] for a in FD[i]) == SHC[i], i
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
    assert u' '.join(x for _, x in PP[i]) == SHC[i], i


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
    """折平面上的一枚偏移 → (原行号, 该偏移在本行折平串里的位置)"""
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
    """锚由面上位置导出: 在本行的折平串上找针, 命中后把区间映回原行、按整词切成窗口串。
    短行整行给出, 长行给窗口——两种都是原行的逐字片段。"""
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
        assert key in pnorm(seg), (LBL[i], n, nd)
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
    return u' '.join(SHC[i][a:e].split()), line_of(i, a), line_of(i, e - 1)


def ln_of(i, nd, frm=0):
    a = LOW_SHLIG[i].find(pnorm(nd), frm)
    if a < 0:
        raise AssertionError(u'窗针落空 %s %s' % (LBL[i], nd))
    return a, line_of(i, a)


def ln_end(i, nd, frm=0):
    """短语落在哪一行要看它结束在哪一行: 72 列硬换行会把 “no less than two hours” 切成两行"""
    a, ln = ln_of(i, nd, frm)
    return a, line_of(i, a + len(pnorm(nd)) - 1)


def line_holds(i, ln, nd):
    """行号尺复核: 拿行号回原文件取那一行, 看针是否真落在这一行内(在折平行串上判)"""
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


def pair_anchor(i, mh, mt, nd):
    """义务词跨行的两半: 首行那一半取该式前一词所在的原行片段, 末行那一半取该式后一词所在的原行片段"""
    w = pnorm(nd).split(u' ')
    x, y = L[i][mh - 1], L[i][mt - 1]
    a = x.lower().rfind(w[0])
    assert a >= 0, (LBL[i], mh, nd)
    hx, _, _ = grow(x, a, a + len(w[0]), 46)
    b = y.lower().find(u' '.join(w[1:]))
    assert b >= 0, (LBL[i], mt, nd)
    tx, _, _ = grow(y, b, b + len(u' '.join(w[1:])), 46)
    assert hx in x and tx in y
    ALOG.append((LBL[i], nd[:14] + u'[上]', mh, 1, nd))
    ALOG.append((LBL[i], nd[:14] + u'[下]', mt, 1, nd))
    return (u'⟦%s⟧⟨%s⟩' % (LBL[i], hx), u'⟦%s⟧⟨%s⟩' % (LBL[i], tx))


# 段界全部由字面针导出: 前 5 段是五份的主答句所在段, 其后是讨论段 ⇎ 探活段 ⇎ 3×PTO 段 ⇎ SETTINGS_TIMEOUT 段
# ⇎ 关闭时机段 ⇎ 发送方式段 ⇎ 四份的“关键词”模板段(1122 那一代还没有这段)
PINS = [(0, u'implementors may include "keep-alives" in their TCP implementations',
         u'MUST default to no less than two hours.'),
        (1, u'If keep-alives are included, the application MUST be able',
         u'MUST default to no less than two hours (MUST-28).'),
        (2, u'Servers will usually have some timeout value', u'for either the client or the server.'),
        (3, u'Servers are encouraged to maintain open connections',
         u'gracefully complete or terminate any necessary remaining tasks.'),
        (4, u'If a max_idle_timeout is specified by either endpoint',
         u'if it abandons the connection prior to the effective value.'),
        (0, u'Discussion: A "keep-alive" mechanism periodically probes',
         u'even when there is no data to be sent.'),
        (1, u'to confirm that an idle connection is still active', u'one garbage octet of data.'),
        (4, u'To avoid excessively small idle timeout periods', u'prior to idle timeout.'),
        (3, u'If the sender of a SETTINGS frame does not receive an acknowledgment',
         u'might result in spurious errors.'),
        (2, u'A client or server that wishes to time out', u'allocated system resources to be reclaimed.'),
        (0, u'An implementation SHOULD send a keep-alive segment with no data',
         u'for compatibility with erroneous TCP implementations.'),
        (1, u'The key words', u'as described in BCP 14 [3] [12]'),
        (2, u'The key words', u'as described in BCP 14 [RFC2119] [RFC8174]'),
        (3, u'The key words', u'as described in BCP 14 [RFC2119] [RFC8174]'),
        (4, u'The key words', u'as described in BCP 14 [RFC2119] [RFC8174]')]
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


def TONED(s):
    return sum([ub_re(s, w) for w in TONE]) > 0


F['tone_must_blk'] = [ub(p, u'MUST') for p in PTXT]
F['tone_may_blk'] = [ub(p, u'MAY') for p in PTXT]
F['tone_should_blk'] = [ub(p, u'SHOULD') for p in PTXT]
F['tone_mustnot_blk'] = [ub(p, u'MUST NOT') for p in PTXT]
F['tone_tag_blk'] = [len(TAGRE.findall(p)) for p in PTXT]
F['tone_in_blk'] = [F['tone_must_blk'][n] + F['tone_may_blk'][n] + F['tone_should_blk'][n]
                    for n in range(len(PB))]
F['blk_must_cur'] = [cnt_cur(p, u'MUST') for p in PTXT]
F['blk_must_re'] = [len(re.findall(u'MUST', p)) for p in PTXT]
F['blk_tone_ruler_close'] = (sum(abs(F['tone_must_blk'][n] - F['blk_must_cur'][n]) for n in range(len(PB)))
                             + sum(abs(F['tone_must_blk'][n] - F['blk_must_re'][n]) for n in range(len(PB))))
# 两份 TCP 文书的主答句段: 段长差与逐字重印的账由对齐遍另立(见下方 blk_tcp_*)
F['blk_tcp_len_gap'] = F['blk_chars'][1] - F['blk_chars'][0]
F['blk_tcp_tag_chars'] = sum([len(m.group(0)) for m in TAGR.finditer(PTXT[1])])
F['blk_tcp_tag_widths'] = [len(m.group(0)) for m in TAGR.finditer(PTXT[1])]


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


# 四份“关键词”模板段(11=9293 ⇎ 12=9112 ⇎ 13=9113 ⇎ 14=9000): 共头一律到 “are to be interpreted as”, 尾巴各家接各家的引用
KWK = [11, 12, 13, 14]
KWPAIR = [(a, b) for x, a in enumerate(KWK) for b in KWK[x + 1:]]
F['kw_head_pre'] = [head_words(PW[a], PW[b]) for a, b in KWPAIR]
F['kw_head_suf'] = [suffix_words(PW[a], PW[b]) for a, b in KWPAIR]
F['kw_same'] = [1 if PTXT[a] == PTXT[b] else 0 for a, b in KWPAIR]
F['kw_pair_lbl'] = [u'%s-%s' % (LBL[PINS[a][0]], LBL[PINS[b][0]]) for a, b in KWPAIR]
F['kw_head_min'] = min(F['kw_head_pre'])
F['kw_head_max'] = max(F['kw_head_pre'])
F['kw_same_n'] = sum(F['kw_same'])
F['kw_suf_tot'] = sum(F['kw_head_suf'])
F['kw_suf_zero_n'] = len([x for x in F['kw_head_suf'] if x == 0])
F['kw_vocab_max'] = max([F['blk_vocab'][n] for n in KWK])
# 共尾为零档 ⇎ 全文相同档由另一把尺复核: 段窗报出的首末行回原文件截那段逐行序列, 逐字比对
def raw_span(i, lo, hi):
    return tuple(x.strip() for x in L[i][lo - 1:hi] if x.strip() != u'')


F['kw_same_raw'] = [1 if raw_span(PINS[a][0], PB[a][1], PB[a][2])
                    == raw_span(PINS[b][0], PB[b][1], PB[b][2]) else 0 for a, b in KWPAIR]
F['kw_same_raw_n'] = sum(F['kw_same_raw'])
# 两把尺的差单列一格: 折平段落串相同 ⇎ 原行序列不同 = 同样的词在两份文书里换了分行位置
F['kw_wrap_diff'] = len([m for m in range(len(KWPAIR))
                         if F['kw_same'][m] and not F['kw_same_raw'][m]])
F['kw_face_close'] = sum(abs(F['kw_same'][m] - F['kw_same_raw'][m]) for m in range(len(KWPAIR)))
F['kw_suf_nz_n'] = len([x for x in F['kw_head_suf'] if x > 0])
# 1122 面上根本没有“关键词”这一段: 口径不存在登记 -1, 不是零
KWPOS = [LOW_SHLIG[i].find(pnorm(u'The key words')) for i in range(NSRC)]
F['kw_minus_row'] = [line_of(i, x) if x >= 0 else -1 for i, x in enumerate(F['kw_at'])]


def head_words_all(wordlists):
    n = 0
    while all(len(x) > n for x in wordlists) and all(x[n] == wordlists[0][n] for x in wordlists):
        n += 1
    return n


# 四段齐头由四路扫描现导, 与两两共头的最长值各算一遍
F['kw_all_head'] = head_words_all([PW[n] for n in KWK])

# ---------- 两份 TCP 文书的主答句段: 逐词对齐由序列匹配器现导, 不靠手打片段 ----------
# 9293 把 1122 的这一段重印了, 但重印伴三种动作: 删掉 1122 的开场句、往里添一句条件、给义务词缀编号。
# 相同词段由对齐器给出(不预设是哪句), 删除数 − 插入数 = 两份的词数差, 这才是能失败的账平。
difflib = __import__(u'difflib')
T1W = tag_strip(PTXT[1]).lower().split()
OPC = difflib.SequenceMatcher(None, PW[0], T1W).get_opcodes()
F['blk_tcp_op_tags'] = [x[0] for x in OPC]
F['blk_tcp_op_n'] = len(OPC)
F['blk_tcp_equal'] = sum([x[2] - x[1] for x in OPC if x[0] == u'equal'])
F['blk_tcp_equal_runs'] = len([x for x in OPC if x[0] == u'equal'])
F['blk_tcp_equal_max'] = max([x[2] - x[1] for x in OPC if x[0] == u'equal'])
F['blk_tcp_drop'] = sum([x[2] - x[1] for x in OPC if x[0] in (u'delete', u'replace')])
F['blk_tcp_insert'] = sum([x[4] - x[3] for x in OPC if x[0] in (u'insert', u'replace')])
F['blk_tcp_replace'] = len([x for x in OPC if x[0] == u'replace'])
F['blk_tcp_word_ledger'] = F['blk_tcp_equal'] + F['blk_tcp_drop'] - len(PW[0])
F['blk_tcp_word_ledger2'] = F['blk_tcp_equal'] + F['blk_tcp_insert'] - len(T1W)
F['blk_tcp_word_gap_ledger'] = F['blk_tcp_drop'] - F['blk_tcp_insert'] - (len(PW[0]) - len(T1W))
# 字符档同上一式: 相同词段的字符在两面各量一遍, 余下的字数差应等于删/插两档之差
F['blk_tcp_char_drop'] = sum([len(u' '.join(PW[0][x[1]:x[2]])) + (1 if x[2] < len(PW[0]) else 0)
                              for x in OPC if x[0] in (u'delete', u'replace')])
F['blk_tcp_char_insert'] = sum([len(u' '.join(T1W[x[3]:x[4]])) + (1 if x[4] < len(T1W) else 0)
                                for x in OPC if x[0] in (u'insert', u'replace')])
F['blk_tcp_naked_chars'] = len(tag_strip(PTXT[1]))
F['blk_tcp_char_ledger'] = (F['blk_chars'][0] - F['blk_tcp_char_drop'] + F['blk_tcp_char_insert']
                            - F['blk_tcp_naked_chars'])
F['blk_tcp_verbatim_sub'] = 1 if T1W and u' '.join(T1W) in tag_strip(PTXT[0]) else 0
# 主答句五段: 五份都是 RFC Editor 面, 一段被 72 列硬换行切成多行——“一行读全”只在标题行那种场合出现
F['blk_words_per_row'] = [F['blk_words'][n] // F['blk_rows'][n] for n in range(5)]
F['blk_is_one_line'] = [1 if F['blk_rows'][n] == 1 else 0 for n in range(5)]
F['blk_one_line_n'] = sum(F['blk_is_one_line'])
# 答句的行号 ⇎ 跨行数由段窗尺重导一遍: 拿建条侧的整句(逐字符句界那轨的产物)在摘壳折平面上取首次
# 命中, 命中偏移经 fmap 映回原行——与建条侧“累积长度表 sh_line_of”是两张不同的表, 对拍才谈得上复核。
F['ans_head'] = [LOW_SHLIG[i].find(pnorm(WIN[i])) for i in range(NSRC)]
F['ans_head_line'] = [line_of(i, a) for i, a in enumerate(F['ans_head'])]
F['ans_tail_line'] = [line_of(i, a + len(pnorm(WIN[i])) - 1) for i, a in enumerate(F['ans_head'])]
F['ans_needle_span'] = [F['ans_tail_line'][i] - F['ans_head_line'][i] + 1 for i in range(NSRC)]
F['ans_sent_at'] = [LOW_SHLIG[i].find(pnorm(F['ans'][i])) for i in range(NSRC)]
assert all(x >= 0 for x in F['ans_sent_at']), [LBL[i] for i in range(NSRC) if F['ans_sent_at'][i] < 0]
F['ans_sent_line'] = [line_of(i, F['ans_sent_at'][i]) for i in range(NSRC)]
F['ans_sent_end'] = [line_of(i, F['ans_sent_at'][i] + len(pnorm(F['ans'][i])) - 1) for i in range(NSRC)]
F['ans_sent_span'] = [F['ans_sent_end'][i] - F['ans_sent_line'][i] + 1 for i in range(NSRC)]
F['ans_span_ind'] = [len([1 for n, x, f, ix in FD[i]
                          if F['ans_head_line'][i] <= n <= F['ans_tail_line'][i]]) for i in range(NSRC)]
F['ans_line_close'] = sum(abs(F['ans_sent_line'][i] - F['mk_ans_sent_line'][i]) for i in range(NSRC))
F['ans_span_close'] = sum(abs(F['ans_sent_span'][i] - F['mk_ans_sent_span'][i]) for i in range(NSRC))
F['ans_needle_gap'] = [F['ans_span'][i] - F['ans_needle_span'][i] for i in range(NSRC)]
F['ans_row_ledger'] = [F['ans_sent_end'][i] - F['ans_sent_line'][i] + 1
                       - len([1 for n, x, f, ix in FD[i]
                              if F['ans_sent_line'][i] <= n <= F['ans_sent_end'][i]])
                       for i in range(NSRC)]

# ---------- 切开判词: 逐行漏读的针, 一半在首行 ⇎ 一半在末行 ----------
SPLITREC = []
WRAPK2 = sorted([k for i, k in F['role_wrap_keys']])
TAGCUTK = [k for (i, k) in F['role_tagcut_keys']]
assert WRAPK2 == WRAPK and not (set(WRAPK2) & set(TAGCUTK))
for i, k in F['role_wrap_keys']:
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
F['split_half_ok'] = sum([line_holds(x[1], x[2], pnorm(split_pieces(x[1], ROLEN[x[0]])[2]))
                          for x in SPLITREC])
F['split_gap_rows'] = [len([1 for n in range(x[2] + 1, x[3]) if shell_by_shape(L[x[1]][n - 1], FAM[x[1]])])
                       for x in SPLITREC]
F['split_wrap_n'] = len(WRAPK)
F['split_tagcut_n'] = len(TAGCUTK)
F['split_ledger'] = F['split_n'] - F['role_line_miss_n']
F['split_adj_n'] = len([x for x in SPLITREC if x[3] - x[2] == 1])

# 被编号标注切开的针: 摘壳面读不通 ⇎ 去掉标注才读通。
# 机制: 逐枚记下 tag_strip 抹掉的区间, 给去编号面的每个字符配上它在摘壳面的下标;
# 针在去编号面命中后靠这张对照表映回摘壳面, 两半之间夹着的就现形——两半与标注都是摘壳面的逐字片段。
def tag_kept(face):
    kept, k = [], 0
    for m in TAGR.finditer(face):
        while k < m.start():
            kept.append(k)
            k += 1
        k = m.end()
    while k < len(face):
        kept.append(k)
        k += 1
    assert len(kept) == len(tag_strip(face)), u'编号对照表与去编号面不同长'
    return kept


KEEP = [tag_kept(SHC[i]) for i in range(NSRC)]
F['tag_eaten'] = [len(SHC[i]) - len(SHTAGC[i]) for i in range(NSRC)]


def row_of_fd(i, n):
    for y in FD[i]:
        if y[0] == n:
            return y
    raise AssertionError(u'行号无对应原行 %s %d' % (LBL[i], n))


def face_window(i, a, ln):
    """摘壳面的一段 [a, a+ln) 落回它自己那一行, 按整词扩成原行的逐字窗口串"""
    n, o = loc(i, a)
    _, raw, f, ix = row_of_fd(i, n)
    assert f[o:o + ln] == SHC[i][a:a + ln] or pnorm(f[o:o + ln]) == pnorm(SHC[i][a:a + ln]), (LBL[i], n)
    e = min(o + ln, len(f)) - 1
    seg, s, t = grow(raw, ix[o], ix[e] + 1, 40)
    assert seg in raw, (LBL[i], n)
    return n, seg


TAGCUTREC = []
for i, k in F['role_tagcut_keys']:
    key = pnorm(ROLEN[k])
    p = LOW_TAG[i].find(key)
    assert p >= 0 and LOW_SHLIG[i].find(key) < 0, (LBL[i], key)
    a, b = KEEP[i][p], KEEP[i][p + len(key) - 1] + 1
    tags = [(m.group(0), m.start(), m.end()) for m in TAGR.finditer(SHC[i])
            if m.start() >= a and m.end() <= b]
    assert tags, (LBL[i], key)
    head, tail = SHC[i][a:tags[0][1]], SHC[i][tags[-1][2]:b]
    assert pnorm(head + tail) == key, (LBL[i], key, head, tail)
    hn, hw = face_window(i, a, len(head))
    tn, tw = face_window(i, tags[-1][2], len(tail))
    TAGCUTREC.append((k, i, hn, tn, head, tail, [x[0] for x in tags],
                      b - a - len(key), sum(len(x[0]) for x in tags), hw, tw))
F['tagcut_k'] = [x[0] for x in TAGCUTREC]
F['tagcut_lbl'] = [LBL[x[1]] for x in TAGCUTREC]
F['tagcut_needle'] = [ROLEN[x[0]] for x in TAGCUTREC]
F['tagcut_head'] = [x[4] for x in TAGCUTREC]
F['tagcut_tail'] = [x[5] for x in TAGCUTREC]
F['tagcut_head_row'] = [x[2] for x in TAGCUTREC]
F['tagcut_tail_row'] = [x[3] for x in TAGCUTREC]
F['tagcut_span'] = [x[3] - x[2] + 1 for x in TAGCUTREC]
F['tagcut_mid'] = [u''.join(x[6]) for x in TAGCUTREC]
F['tagcut_mid_n'] = [len(x[6]) for x in TAGCUTREC]
F['tagcut_eaten'] = [x[7] for x in TAGCUTREC]
F['tagcut_tag_chars'] = [x[8] for x in TAGCUTREC]
F['tagcut_mid_chars'] = [len(x[9]) + len(x[10]) for x in TAGCUTREC]
F['tagcut_win_head'] = [x[9] for x in TAGCUTREC]
F['tagcut_win_tail'] = [x[10] for x in TAGCUTREC]
F['tagcut_n'] = len(TAGCUTREC)
# 账平: 摘壳面里被标注吃掉的字符 = 两半之间的宽度 − 针长, 逐枚应与标注字符数相等
F['tagcut_ledger'] = [x[7] - x[8] for x in TAGCUTREC]
F['tagcut_eaten_close'] = [F['tag_eaten'][i]
                           - sum([len(m.group(0)) for m in TAGR.finditer(SHC[i])])
                           for i in range(NSRC)]

# ---------- 被换行切开的义务词: 逐行读不到 ⇎ 折平读到的那一式, 由原面逐行现定位 ----------
def straddle_pair(i, nd):
    """在原文件逐行面上找“上一行以此式的前词收尾 ⇎ 下一枚非空行以后词起头”的行对——
    两行之间只允许夹空行(折平不吃字符), 夹页脚的就不是跨行式。"""
    w = pnorm(nd).split(u' ')
    out = []
    for m in range(len(L[i])):
        p = fold(L[i][m])
        if not p.lower().endswith(w[0]):
            continue
        k, blanks = m + 1, 0
        while k < len(L[i]) and fold(L[i][k]) == u'':
            blanks += 1
            k += 1
        if k < len(L[i]) and fold(L[i][k]).lower().startswith(u' '.join(w[1:])):
            out.append((m + 1, k + 1, blanks))
    return out


TSK = [k for k in range(5) if sum([F['tone_wrap_gain'][i * 5 + k] for i in range(NSRC)])]
F['tone_straddle_nd'] = [TONE[k] for k in TSK]
TSP = []
for kk in TSK:
    for i in range(NSRC):
        for (mh, mt, bl) in straddle_pair(i, TONE[kk]):
            TSP.append((LBL[i], kk, mh, mt, bl))
F['tone_straddle'] = [len([x for x in TSP if x[0] == LBL[i]]) for i in range(NSRC)]
F['tone_straddle_by_kind'] = [len([x for x in TSP if x[1] == kk]) for kk in TSK]
F['tone_straddle_n'] = len(TSP)
F['tone_straddle_adj'] = len([x for x in TSP if x[3] - x[2] == 1])
F['tone_straddle_blank'] = F['tone_straddle_n'] - F['tone_straddle_adj']
F['tone_straddle_blank_rows'] = sum([x[4] for x in TSP])
# 跨行式两行之间夹的必须全是空行: 夹了正文或壳行的, 折平串里就多出一段词, 那一式就不是同一句
F['tone_straddle_gap_shell'] = sum([len([1 for n in range(x[2], x[3] - 1)
                                         if fold(L[LBL.index(x[0])][n - 1]) != u'']) for x in TSP])
F['tone_wrap_gain_mn'] = [F['tone_wrap_gain'][i * 5 + 1] for i in range(NSRC)]
F['tone_straddle_ledger'] = sum(F['tone_wrap_gain_mn']) - F['tone_straddle_n']
assert F['tone_straddle_n'] >= 1 and F['tone_straddle_ledger'] == 0, (F['tone_straddle'], F['tone_wrap_gain_mn'])

# ---------- 行号尺往返: 段窗首末行回原文件那一行自验 ----------
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
F['blk_ans_inside'] = [1 if (F['blk_lo'][n] <= F['ans_anchor_line'][n]
                             and F['ans_sent_end'][n] <= F['blk_hi'][n]) else 0 for n in range(5)]


# ---------- 模板长行池: 版式两代各自成套, 旧式 1122 与新式四份无一枚共用 ----------
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
OLDSET = set(LBL[i] for i in OLD)
NEWSET = set(LBL[i] for i in NEW)
OLDPAIR = [k for k in F['pool_pair'] if any(z in OLDSET for z in k.split(u'-'))]
NEWPAIR = [k for k in F['pool_pair'] if all(z in NEWSET for z in k.split(u'-'))]
F['pool_pair_by'] = [F['pool_pair'][u'%s-%s' % (LBL[a], LBL[b])] for a, b in PAIRS]
F['pool_pair_old_keys'] = sorted(OLDPAIR)
F['pool_pair_new_keys'] = sorted(NEWPAIR)
F['pool_pair_old'] = sum(F['pool_pair'][k] for k in OLDPAIR)
F['pool_pair_new'] = sum(F['pool_pair'][k] for k in NEWPAIR)
F['pool_pair_old_n'] = len([k for k in OLDPAIR if F['pool_pair'][k] == 0])
F['pool_max_pair'] = max(F['pool_pair'].values())
F['pool_min_pair_new'] = min(F['pool_pair'][k] for k in NEWPAIR)
F['pool_tier_close'] = sum(F['pool_tier']) - F['pool_union']
F['pool_sum_close'] = sum(F['pool_tier'][m] * (m + 1) for m in range(NSRC)) - F['pool_sum']
# 共用的到底是哪些行: 按“带不带义务词 ⇎ 带不带 RFC 编号 ⇎ 是不是本文档抬头”分档现读
SHARED = set()
for k in NEWPAIR:
    a, b = [LBL.index(z) for z in k.split(u'-')]
    SHARED |= (POOL[a] & POOL[b])
F['pool_shared_new'] = len(SHARED)
F['pool_shared_toned'] = len([x for x in SHARED if TONED(x)])
F['pool_shared_rfcline'] = len([x for x in SHARED if cnt_re(x, u'RFC') > 0])
F['pool_shared_status'] = len([x for x in SHARED if cnt_re(x.lower(), u'status of this document') > 0])
F['pool_shared_bom'] = len([x for x in SHARED if u'\ufeff' in x])
F['pool_old_toned'] = len([x for x in POOL[0] if TONED(x)])
F['pool_new_toned'] = sum(len([x for x in POOL[i] if TONED(x)]) for i in NEW)
# 1122 与谁共行: 只有 9293, 而且共的是 TCP 正文行(RCV 表 ⇎ SEQ/ACK 式 ⇎ ERROR_REPORT 签名), 不是套版行
OSHAL = POOL[0] & POOL[1]
F['pool_old_shared'] = len(OSHAL)
F['pool_old_shared_pres'] = [pres_n(x) for x in sorted(OSHAL)]
F['pool_old_shared_toned'] = len([x for x in OSHAL if TONED(x)])
F['pool_old_shared_status'] = len([x for x in OSHAL if cnt_re(x.lower(), u'status of this document') > 0])
F['pool_old_shared_rfcline'] = len([x for x in OSHAL if cnt_re(x, u'RFC') > 0])
F['pool_old_shared_bom'] = len([x for x in OSHAL if u'\ufeff' in x])
F['pool_all_five'] = F['pool_tier'][NSRC - 1]
F['pool_new_four'] = F['pool_tier'][3]

# ---------- 转置尺: 族量按“这一式在五份里各读几枚”横过来逐份读 ----------
F['dur_docs'] = [[F['dur'][i][k] for i in range(NSRC)] for k in range(len(DUR))]
F['numw_docs'] = [[F['numw'][i][k] for i in range(NSRC)] for k in range(len(NUMW))]
F['spell_docs'] = [[F['spell'][i][k] for i in range(NSRC)] for k in range(len(SPELL))]
F['tone_docs'] = [[F['tone_sh'][i][k] for i in range(NSRC)] for k in range(5)]
F['num_docs'] = [[F['num'][i][k] for i in range(NSRC)] for k in range(len(NUMLIT))]
F['num_cold'] = [NUMLIT[k] for k in range(len(NUMLIT)) if sum(F['num_docs'][k]) == 0]
F['num_cold_n'] = len(F['num_cold'])
F['num_hot_n'] = len(NUMLIT) - F['num_cold_n']
F['num_own_tot'] = sum(len(x) for x in F['num_own'])
F['spell_tot_docs'] = [sum(x) for x in F['spell_docs']]
F['dur_tot'] = [sum(x) for x in F['dur_docs']]
F['role_by_face'] = [[sum(F['role_line'][i]) if k == 0 else sum(F['role_fold'][i]) if k == 1
                      else sum(F['role_sh'][i]) if k == 2 else sum(F['role_tag'][i])
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
F['gain_tag'] = [F['role_tag'][i][k] - F['role_sh'][i][k]
                 for i in range(NSRC) for k in range(len(ROLEN))]
F['gain_fold_tot'] = sum(F['gain_fold'])
F['gain_sh_tot'] = sum(F['gain_sh'])
F['gain_tag_tot'] = sum(F['gain_tag'])
F['gain_fold_key'] = len([x for x in F['gain_fold'] if x > 0])
F['gain_tag_key'] = len([x for x in F['gain_tag'] if x > 0])
F['gain_fold_dup'] = sum([F['role_fold'][i][k] - F['role_line'][i][k] for i in range(NSRC)
                          for k in range(len(ROLEN)) if F['role_line'][i][k] > 0])
F['gain_sh_dup'] = sum([F['role_sh'][i][k] - F['role_fold'][i][k] for i in range(NSRC)
                        for k in range(len(ROLEN)) if F['role_fold'][i][k] > 0])
F['ans_words_tot'] = sum(F['ans_words'])
F['sec_lines_tot2'] = sum(F['sec_lines'])
F['sec_chars_tot'] = sum(F['sec_chars'])

# ---------- 逐句对照: 9293 相对 1122 新增的句子在面上的位置 ----------
# 新句是从摘壳句列里剥掉编号标注之后留下的, 所以定位走第四档(去编号面), 再靠编号对照表映回摘壳面取行号
OVLNEW = [z for z in A2T if z not in A1 and canon(z) not in [canon(y) for y in A1]
          and canon(z) not in [canon(y) for y in D1]]
F['ovl_new_tagloc'] = [LOW_TAG[1].find(pnorm(z)) for z in OVLNEW]
assert min(F['ovl_new_tagloc']) >= 0, [z[:40] for z in OVLNEW if LOW_TAG[1].find(pnorm(z)) < 0]
F['ovl_new_loc'] = [KEEP[1][p] for p in F['ovl_new_tagloc']]
F['ovl_new_end'] = [KEEP[1][p + len(pnorm(z)) - 1] for p, z in zip(F['ovl_new_tagloc'], OVLNEW)]
F['ovl_new_lines'] = [line_of(1, a) for a in F['ovl_new_loc']]
F['ovl_new_rows'] = [line_of(1, e) - line_of(1, a) + 1
                     for a, e in zip(F['ovl_new_loc'], F['ovl_new_end'])]
F['ovl_new_n'] = len(OVLNEW)
F['ovl_new_close'] = F['ovl_new'] - F['ovl_disc_promoted'] - F['ovl_new_n']
F['ovl_new_tagcut'] = [len([1 for m in TAGR.finditer(SHC[1]) if a <= m.start() and m.end() <= e + 1])
                       for a, e in zip(F['ovl_new_loc'], F['ovl_new_end'])]

CLOSE2 = {}
CLOSE2[u'shell_pred_agree'] = 1 if F['shell_pred_diff'] == 0 else 0
CLOSE2[u'seg_rt_all'] = 1 if F['seg_rt_ok'] == F['seg_rt_n'] else 0
CLOSE2[u'split_reverse_cold'] = 1 if (F['split_full_on_head'] == 0 and F['split_half_ok'] == F['split_n']) else 0
CLOSE2[u'split_ledger_close'] = 1 if (F['split_ledger'] == 0 and F['split_wrap_n'] == sum(F['role_wrap_n'])
                                      and F['split_tagcut_n'] == len(F['role_tagcut_keys'])
                                      and F['split_adj_n'] == F['split_n']) else 0
CLOSE2[u'tagcut_between_is_tag'] = 1 if (len(F['tagcut_mid']) == 1 and F['tagcut_mid_n'] == [1]
                                        and TAGR.fullmatch(F['tagcut_mid'][0]) is not None
                                        and F['tagcut_eaten'] == F['tagcut_tag_chars']
                                        and sum(F['tagcut_ledger']) == 0) else 0
CLOSE2[u'tagcut_halves_are_face_pieces'] = 1 if (
    all([pnorm(x[4] + x[5]) == pnorm(ROLEN[x[0]]) for x in TAGCUTREC])
    and all([F['tagcut_head'][j] in SHC[F['role_tagcut_keys'][j][0]]
             and F['tagcut_tail'][j] in SHC[F['role_tagcut_keys'][j][0]]
             for j in range(F['tagcut_n'])])
    and all([F['tagcut_win_head'][j] in L[F['role_tagcut_keys'][j][0]][F['tagcut_head_row'][j] - 1]
             and F['tagcut_win_tail'][j] in L[F['role_tagcut_keys'][j][0]][F['tagcut_tail_row'][j] - 1]
             for j in range(F['tagcut_n'])])) else 0
CLOSE2[u'ans_ruler_rematch'] = 1 if (F['ans_line_close'] == 0 and F['ans_span_close'] == 0) else 0
CLOSE2[u'ans_inside_block'] = 1 if F['blk_ans_inside'] == [1] * 5 else 0
CLOSE2[u'kw_four_variants'] = 1 if (
    F['kw_face_close'] == F['kw_wrap_diff'] and F['kw_same_n'] == F['kw_same_raw_n'] + F['kw_wrap_diff']
    and F['kw_all_head'] == F['kw_head_min'] and F['kw_all_head'] <= F['kw_head_max']
    and F['kw_suf_zero_n'] == 3 and F['kw_suf_nz_n'] + F['kw_suf_zero_n'] == len(F['kw_same'])
    and F['kw_wrap_diff'] >= 1) else 0
CLOSE2[u'kw_absent_in_1122_row'] = 1 if (F['kw_docs'] == 4 and F['kw_minus_row'][0] == -1
                                         and min(F['kw_minus_row'][1:]) >= 2) else 0
CLOSE2[u'tcp_block_rewritten_not_reprinted'] = 1 if (
    F['blk_tcp_word_ledger'] == 0 and F['blk_tcp_word_ledger2'] == 0
    and F['blk_tcp_word_gap_ledger'] == 0
    and F['blk_tcp_verbatim_sub'] == 0
    and F['blk_tcp_drop'] >= 1 and F['blk_tcp_insert'] >= 1 and F['blk_tcp_replace'] >= 1
    and F['blk_tcp_equal_max'] >= 20
    and F['tone_tag_blk'][0] == 0 and F['tone_tag_blk'][1] == 5
    and set(F['blk_tcp_tag_widths']) == set([10])
    and F['blk_tcp_tag_chars'] == sum(F['blk_tcp_tag_widths'])) else 0
CLOSE2[u'pool_old_shares_only_tcp_body'] = 1 if (
    F['pool_pair_old'] == F['pool_pair_by'][0] and F['pool_pair_by'][0] >= 1
    and sum(F['pool_pair_by'][1:4]) == 0
    and F['pool_old_shared'] == F['pool_pair_by'][0]
    and set(F['pool_old_shared_pres']) == set([2])
    and F['pool_old_shared_status'] == 0 and F['pool_old_shared_toned'] >= 1
    and F['pool_all_five'] == 0 and F['pool_new_four'] >= 1) else 0
CLOSE2[u'old_pool_three_cold'] = 1 if (F['pool_pair_old_n'] == len(OLDPAIR) - 1
                                       and len([k for k in NEWPAIR if F['pool_pair'][k] > 0]) == len(NEWPAIR)
                                       and F['pool_pair_new'] == F['pool_pair_tot'] - F['pool_pair_old']
                                       and F['pool_pair_old'] >= 1) else 0
CLOSE2[u'pool_ie'] = 1 if F['pool_ie_close'] == 0 else 0
CLOSE2[u'blk_tone_ruler'] = 1 if F['blk_tone_ruler_close'] == 0 else 0
CLOSE2[u'straddle_is_mustnot_only'] = 1 if (F['tone_straddle_by_kind'] == [F['tone_straddle_n']]
                                            and F['tone_straddle_ledger'] == 0
                                            and F['tone_straddle_gap_shell'] == 0
                                            and F['tone_straddle'] == F['tone_wrap_gain_mn']) else 0
CLOSE2[u'pp_gap_is_shell_nonblank'] = 1 if F['pp_gap_close'] == 0 and sum(F['pp_gap_rows']) > 0 else 0
CLOSE2[u'num_cold_split'] = 1 if (F['num_cold_n'] + F['num_hot_n'] == len(NUMLIT)
                                  and F['num_cold_n'] >= 1) else 0
CLOSE2[u'ovl_new_locatable'] = 1 if (F['ovl_new_n'] >= 1 and F['ovl_new_close'] == 0
                                     and max(F['ovl_new_rows']) >= 2) else 0
CLOSE2[u'page_lit_eaten_by_shell'] = 1 if (
    F['page_lit_fold'][0] >= 1 and sum(F['page_lit_fold'][1:]) == 0
    and sum(F['page_lit_sh']) == 0 and F['page_lit_rows_shell'] == 0
    and len(F['page_lit_rows'][0]) == F['page_lit_fold'][0]) else 0
F.update(CLOSE2)

Z2 = []


def ZEXP(expr, what):
    Z2.append((expr, what))
    ZV.append((expr, what))


ZEXP(u"B82V('shell_pred_diff')", u'两遍壳谓词逐行同集: 整行序列正则 ⇎ token 形状尺无一行判得不一样')
ZEXP(u"B82V('pp_gap_close')", u'片段序列比非空行少的行数 = 非空壳行枚数(页脚与眉行)')
ZEXP(u"sum(B82V('pp_rows')) + sum(B82V('shell_lines')) - sum(B82V('lines'))",
     u'片段序列行数加壳行数等于原行数(空行全归壳, 无一行两头都不算)')
ZEXP(u"B82V('split_ledger')", u'切开针总数 = 逐行漏读针总数(只由硬换行切开, 无壳切)')
ZEXP(u"B82V('kw_suf_zero_n') + B82V('kw_suf_nz_n') - len(B82V('kw_same'))",
     u'四段模板段逐对分档: 共尾为零的对数加共尾非零的对数 = 全部配对数')
ZEXP(u"B82V('split_wrap_n') - sum(B82V('role_wrap_n'))", u'折平档才读通的针数 = 逐份切开计数之和')
ZEXP(u"B82V('split_tagcut_n') - len(B82V('role_tagcut_keys'))", u'去编号档才读通的针数 = 编号切开针清单长度')
ZEXP(u"B82V('split_adj_n') - B82V('split_n')", u'切开针的首末行一律相邻: 这一代的切开只由硬换行造成')
ZEXP(u"B82V('split_full_on_head')", u'反向对照: 跨行针的整串拿到首行那一行内应当一枚也读不通')
ZEXP(u"B82V('split_half_ok') - B82V('split_n')", u'每根跨行针的两半各自回自己那一行读得通')
ZEXP(u"B82V('seg_rt_ok') - B82V('seg_rt_n')", u'段窗首末行自验: 每一枚段针都落在段窗报出的那一行内')
ZEXP(u"B82V('seg_rt_whole') + B82V('seg_rt_cut') - B82V('seg_rt_n')",
     u'段针两档相加=总数: 整针在一行 ⇎ 被硬换行推到相邻行, 无第三档')
ZEXP(u"B82V('seg_rt_head') + B82V('seg_rt_tail') - B82V('seg_rt_ok')",
     u'落到所报行的段针按侧相加=总数: 段首看头一枚词 ⇎ 段末看末一枚词')
ZEXP(u"B82V('ans_line_close') + B82V('ans_span_close')",
     u'答句行号与跨行数由发射段的行号表重导一遍, 与建条侧逐份同值')
ZEXP(u"sum(B82V('ans_row_ledger'))", u'首末行行距减窗口内实有行数=零(答句所在段无空行壳行)')
ZEXP(u"sum(B82V('blk_ans_inside')) - 5", u'五份的主答句都在自己的段窗内')
ZEXP(u"B82V('blk_tcp_word_ledger')",
     u'对齐器的相同词段加删除词段 = 1122 那一段的全部词数(逐词不漏, 手打片段一律不算证据)')
ZEXP(u"B82V('blk_tcp_word_ledger2')",
     u'相同词段加插入词段 = 9293 去编号那一段的全部词数')
ZEXP(u"B82V('blk_tcp_word_gap_ledger')",
     u'删除词数减插入词数 = 两份段落的词数差(9293 删一句又添一句, 账要摊得开)')
ZEXP(u"B82V('pool_pair_tot') - B82V('pool_pair_new') - B82V('pool_pair_old')",
     u'十对配对按“牵不牵进 1122”分家, 两档相加=全部共用长行对')
ZEXP(u"sum(B82V('pool_pair_by')) - B82V('pool_pair_tot')",
     u'按份次顺序逐对读数相加 = 全部配对合计(两种枚举同一集)')
ZEXP(u"B82V('pool_old_shared') - B82V('pool_pair_by',0)",
     u'1122 与 9293 的共用长行集大小 = 逐对尺上这一对的读数(取集合 ⇎ 取计数两把尺)')
ZEXP(u"B82V('tone_straddle_ledger')", u'跨行义务词行对枚数 = 折平档相对逐行档的 MUST NOT 增益')
ZEXP(u"B82V('tone_straddle_adj') + B82V('tone_straddle_blank') - B82V('tone_straddle_n')",
     u'跨行式按“紧邻 ⇎ 只夹空行”分档, 两档相加=总数')
ZEXP(u"B82V('pool_ie_close')", u'容斥: 各份之和 − 两两共用 + 三三共用 − 四份共用 = 并集')
ZEXP(u"B82V('pool_tier_close')", u'按“几份共用”分档相加 = 并集枚数')
ZEXP(u"B82V('pool_sum_close')", u'分档乘份数相加 = 各份枚数之和')
ZEXP(u"B82V('pool_old_shared_pres',2) - 2",
     u'1122 与 9293 共用的那一行只印在这两份里: 全库出现次数恰为二')
ZEXP(u"B82V('pool_sum') - sum(B82V('pool_raw_rows')) + B82V('pool_dup')",
     u'去重枚数 = 原行枚数 − 重复印的次数')
ZEXP(u"B82V('kw_head_min') - B82V('kw_all_head')",
     u'四段模板段两两共头的最短值 = 四路扫描齐读到的那一处: 两把尺一般高')
ZEXP(u"B82V('kw_same_n') - B82V('kw_same_raw_n') - B82V('kw_wrap_diff')",
     u'折平档相同的对数 = 原行档相同的对数 + 词相同但分行不同的对数')
ZEXP(u"B82V('num_cold_n') + B82V('num_hot_n') - len(B82V('num_fam'))",
     u'数值十四式按“五份全冷 ⇎ 至少一份读通”分家, 两档相加=族长')
ZEXP(u"B82V('face_tot',1) - B82V('face_tot',0) - B82V('gain_fold_tot')",
     u'折平档相对行尺的读数差 = 按枚登记的换行增益')
ZEXP(u"B82V('face_tot',2) - B82V('face_tot',1) - B82V('gain_sh_tot')",
     u'摘壳档相对折平档的读数差 = 按枚登记的页壳增益')
ZEXP(u"B82V('face_tot',3) - B82V('face_tot',2) - B82V('gain_tag_tot')",
     u'去编号档相对摘壳档的读数差 = 按枚登记的编号增益')
ZEXP(u"B82V('gain_fold_tot') - B82V('split_wrap_n') - B82V('gain_fold_dup')",
     u'换行增益按枚 = 切开针数 + 已在行内读通的针新增的那些枚(两把口径的差单列一格, 不混)')
ZEXP(u"B82V('gain_sh_tot')", u'页壳增益按枚为零: 摘壳不再让任何判词针成式(新式四份根本没有页脚可摘)')
ZEXP(u"B82V('ovl_new_close')", u'块内新句按“面上可定位 ⇎ 早在 1122 讨论节里说过”分家, 两档相加=新句总数')
ZEXP(u"sum(B82V('tagcut_ledger'))",
     u'编号切开针被吃掉的宽度 = 夹在两半之间的标注字符数(逐枚账平, 不多不少一枚字符)')
ZEXP(u"sum(B82V('tagcut_eaten_close'))",
     u'摘壳面与去编号面的长度差 = 面上全部标注字符数: 抹掉标注不留一个空格')
ZEXP(u"B82V('kw_face_close') - B82V('kw_wrap_diff')",
     u'两把尺判得不一致的对数 = 词面相同而分行不同的对数: 差只可能来自换行, 不来自用词')
ZEXP(u"B82V('bool_clos2_sum') - B82V('bool_clos2_n')", u'本段布尔门全绿')
ZEXP(u"B82V('page_lit_rows_shell')",
     u'“[Page 1]” 所在的原始行没有一行落在壳尺之外(所以摘壳面一枚也读不到它)')
ZEXP(u"sum(B82V('page_lit_sh'))",
     u'同一式换摘壳面重读: 五份全为零 ⇎ 折平面那枚整行被壳吃掉')
ZEXP(u"B82V('page_lit_fold', 0) - len(B82V('page_lit_rows', 0))",
     u'折平面读到的枚数 = 它所在的原始行数(每枚各在其行, 没有跨行拼出来的)')
F['zid_scan_n'] = len(ZID)
F['zid_scan2_n'] = len(Z2)
F['bool_clos2_n'] = len(CLOSE2)
F['bool_clos2_sum'] = sum(CLOSE2.values())
F['bool_all_n'] = F['bool_clos_n'] + F['bool_clos2_n']
F['bool_all_sum'] = F['bool_clos_sum'] + F['bool_clos2_sum']
print(u'发射段: 扁平键 %d ｜ 恒等式 %d ⇎ 布尔门 %d/%d 绿 ｜ 段窗 %d 枚 %d 行 %d 字 ⇎ 切开 %d(编号切 %d ⇎ 跨行义务词 %d)'
      % (len(F), len(Z2), F['bool_clos2_sum'], F['bool_clos2_n'], len(PB), F['blk_rows_tot'],
         sum(F['blk_chars']), F['split_n'], F['split_tagcut_n'], F['tone_straddle_n']))
print(u'  模板段: 共头 %d..%d 词 ⇎ 相同对 %d ⇎ 共尾零对 %d ⇎ 两把尺判法同 %d ｜ 1122 无此段行号 %d'
      % (F['kw_head_min'], F['kw_head_max'], F['kw_same_n'], F['kw_suf_zero_n'],
         F['kw_face_close'], F['kw_minus_row'][0]))
print(u'  编号切开: 针 %s ⇎ 夹 %s(%d 字符) ⇎ 两半 %s ⇎ %s ｜ 行 %s'
      % (F['tagcut_needle'], F['tagcut_mid'], F['tagcut_tag_chars'][0] if F['tagcut_n'] else 0,
         F['tagcut_head'], F['tagcut_tail'], F['tagcut_head_row']))
if PROBE:
    BADV = [k for k in F if isinstance(F[k], list)
            and any(not isinstance(y, int) for y in F[k])]
    BADV += [k for k in F if not isinstance(F[k], (list, dict, int, float))]
    print(u'  非整数键 %d: %s' % (len(BADV), BADV[:18]))
    print(u'  落空: 段 %d 锚 %d' % (len(BLKFAIL), len(ATOMFAIL)))
    for x in BLKFAIL[:12]:
        print(u'   BLK %s %s %s' % (x[0], x[1][:40], x[2]))
    for x in ATOMFAIL[:12]:
        print(u'   ATOM %s %s' % (x[0], x[1][:40]))
    for g in sorted(CLOSE2):
        if not CLOSE2[g]:
            print(u'   红门 %s' % g)
    for e, w in Z2:
        v = _ev(e)
        if v != 0:
            print(u'   不平 %s = %s (%s)' % (e, v, w))
# --- SCAN2 END ---

# --- 段二 BEGIN --- (编码区正文: 每枚三位以上的数都由 V()/J()/C()/WS()/EXPR() 登记过算式, 锚一律由面导位置)
PLBL = [u'%s#%d' % (LBL[i], n + 1) for n, (i, s, e) in enumerate(PINS)]
KWLBL = [u'%s·%s' % (LBL[PINS[a][0]], LBL[PINS[b][0]]) for a, b in KWPAIR]
POOLLBL = [u'%s-%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
BADREAD = []


def _try(tag, name, pos, thunk):
    if PROBE:
        try:
            return thunk()
        except Exception as e:
            BADREAD.append((tag, name, pos, repr(e)[:60]))
            return u'?'
    return thunk()


def PJ(name, note=u''):
    return u' ⇎ '.join(V(name, n, u'%s·%s' % (note or name, PLBL[n])) for n in range(len(PINS)))


def PKW(name, note=u''):
    return u' ⇎ '.join(u'%s=%s' % (KWLBL[n], V(name, n, u'%s·%s' % (note or name, KWLBL[n])))
                       for n in range(len(KWPAIR)))


def PAI(name, note=u''):
    return u' ⇎ '.join(u'%s=%s' % (POOLLBL[n], V(name, n, u'%s·%s' % (note or name, POOLLBL[n])))
                       for n in range(len(PAIRS)))


def C(name, i, j, note=u''):
    return _try(u'C', name, u'%d,%d' % (i, j),
                lambda: EXPR(F[name][i][j], u"%s('%s', %d)[%d]" % (FN, name, i, j),
                             note or u'%s·%s' % (name, LBL[i])))


def CC(name, i, j, k, note=u''):
    return _try(u'CC', name, u'%d,%d,%d' % (i, j, k),
                lambda: EXPR(F[name][i][j][k], u"%s('%s', %d)[%d][%d]" % (FN, name, i, j, k),
                             note or name))


def WS(name, note=u''):
    return _try(u'WS', name, u'',
                lambda: EXPR(sum(F[name]), u"sum([%s])" % u','.join(
                    [u"%s('%s', %d)" % (FN, name, i) for i in range(NSRC)]), note or name))


def _rowhit(i, cut, lo):
    key = pnorm(cut)
    return len([1 for n, x, f, ix in ALN[i] if n >= lo and key in pnorm(f)])


def AF(i, nd, lo=0):
    """锚由面上位置导出; 针若被硬换行切开, 就同长度先从针头截、再从针尾截,
    退到某一枚词串能单独成行读通为止(短针本身只有一词时不嫌弃, 长针退成单词一律算失败)。"""
    ws = pnorm(nd).split(u' ')
    m = len(ws)
    for n in range(m, 0, -1):
        for cut in ([u' '.join(ws[:n]), u' '.join(ws[m - n:m])] if n > 1 else [u' '.join(ws[:n])]):
            if n == 1 and m > 1:
                continue
            if _rowhit(i, cut, lo):
                return AN(i, cut, lo)
    ATOMFAIL.append((LBL[i], nd))
    if PROBE:
        ALOG.append((LBL[i], nd[:34], 0, 0, nd))
        return u'[无锚:%s]' % nd[:24]
    raise AssertionError(u'锚退让失败 %s %s' % (LBL[i], nd))


def AO(nd, lo=0):
    """归属由面现导: 哪几份的去编号面读得到这一式, 就给哪几份的行内锚"""
    hs = [i for i in range(NSRC) if LOW_TAG[i].find(pnorm(nd)) >= 0]
    if not hs:
        ATOMFAIL.append((u'无主', nd))
        if PROBE:
            return u'[无主:%s]' % nd[:24]
        raise AssertionError(u'无主针 ' + nd)
    return u' ⇎ '.join(AF(i, nd, lo) for i in hs)


def SPC(x):
    a, b = split_anchor(x[1], ROLEN[x[0]])
    return u'%s ⇎ %s' % (a, b)


def TPC(x):
    i = x[1]
    ALOG.append((LBL[i], ROLEN[x[0]][:30] + u'[编号前]', x[2], 1, ROLEN[x[0]]))
    ALOG.append((LBL[i], ROLEN[x[0]][:30] + u'[编号后]', x[3], 1, ROLEN[x[0]]))
    return u'⟦%s⟧⟨%s⟩ ⇎ ⟦%s⟧⟨%s⟩' % (LBL[i], x[9], LBL[i], x[10])


def AR(k, lo=0):
    """第 k 枚判词针的锚: 换行切开的给两半(每份各一对), 编号切开的给标注前后两半, 其余给单行读通的那些份"""
    nd = ROLEN[k]
    rec = [x for x in SPLITREC if x[0] == k]
    if rec:
        return u' ‖ '.join(SPC(x) for x in rec)
    trec = [x for x in TAGCUTREC if x[0] == k]
    if trec:
        return u' ‖ '.join(TPC(x) for x in trec)
    hs = [i for i in range(NSRC) if F['role_line'][i][k]]
    if not hs:
        ATOMFAIL.append((u'无行', nd))
        if PROBE:
            return u'[无行:%s]' % nd[:24]
        raise AssertionError(u'逐行无主 ' + nd)
    return u' ⇎ '.join(AF(i, nd, lo) for i in hs)


def ANSW(i):
    return AF(i, WIN[i], F['sec_body_line'][i])


def ASEC(i):
    return AF(i, SECTTL[i], F['sec_body_line'][i])


def JT(name, note=u''):
    """只有 1122 ⇎ 9293 两份的对照键(不能按五份的 J 走)"""
    return u' ⇎ '.join(V(name, n, u'%s·%s' % (note or name, LBL[n])) for n in range(2))


def JS(name, note=u''):
    """逐枚新句的键, 长度由数据自己说"""
    return u' ⇎ '.join(V(name, n, u'%s·新句%d' % (note or name, n + 1)) for n in range(len(F[name])))


LINES = []
if PROBE:
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
    u'📜 五份同一副版式, 都是 RFC Editor 纯文本面: 最长行一律 ' + V(u'maxlen', 0, u'72 列') + u' 列硬换行'
    u'(逐份 ' + J(u'maxlen', u'最长行') + u'), 字节 ' + J(u'bytes', u'字节') + u', 面内码位 ' + J(u'chars', u'码位')
    + u'——只有 1122 两数相等(非 ASCII ' + V(u'na_total', 0, u'旧式非ASCII') + u' 枚 ⇎ BOM ' + V(u'bom', 0, u'旧式BOM')
    + u' 枚), 别四份码位比字节少 3·BOM+2·非ASCII 那一类的差额见下面 UTF-8 账。 行数三把尺各读一遍: split("\\n") '
    + J(u'splitnl', u'split尺') + u' ⇎ splitlines() ' + J(u'splitlines', u'splitlines尺') + u' ⇎ 逐行读入 '
    + J(u'lines', u'逐行尺') + u', 结尾换行 ' + J(u'trailing_nl', u'尾换行') + u' 枚, 账 ' + J(u'row_form_ledger', u'三尺账')
    + u': 1122 的 splitlines 比逐行多 ' + EXPR(F['splitlines'][0] - F['lines'][0],
                                              u"B82V('splitlines',0)-B82V('lines',0)", u'splitlines多出的行')
    + u' 行, 正是换页符 ' + V(u'ff', 0, u'旧式换页') + u' 枚吃出来的(splitlines 把 \\x0c 也断行, 逐行读入不认)。 '
    + u'换页全在 1122 面上: ' + J(u'ff', u'换页枚') + u' 枚里独占整行的 ' + J(u'ff_alone', u'FF独占行')
    + u' 枚 ⇎ 紧接换行的 ' + J(u'ff_before_nl', u'FF贴换行') + u' 枚 ⇎ 落在文件尾的 ' + J(u'ff_at_eof', u'FF在EOF')
    + u' 枚, 账 ' + J(u'ff_led', u'换页账') + u'; 换行符本身 ' + J(u'lf', u'LF枚') + u' 枚 ⇎ 回车 ' + J(u'cr', u'CR枚')
    + u' 枚——五份全是 LF 面, 没有 CRLF。 非空行 ' + J(u'nonblank', u'非空行') + u' 行。')

LINES.append(
    u'🧾 页壳按 token 形状尺判: 壳行 ' + J(u'shell_lines', u'壳行') + u' 行 = 空行 ' + J(u'blank', u'空行')
    + u' + 页脚 ' + J(u'foot', u'页脚') + u' + 眉行 ' + J(u'hdr_old', u'眉行') + u', 账 ' + J(u'shell_ledger', u'壳账')
    + u' 全平(眉行只可能是 1122 那代才有: 整行以 “RFC1122” 起头 ' + V(u'hdr_old', 0, u'眉行') + u' 行)。 '
    + u'两条独立实现必须同集: 采集遍用整行序列正则挑壳(“片段序列”比非空行少 ' + J(u'pp_gap_rows', u'缺口行')
    + u' 行), 本遍用 token 形状尺, 逐行不一致 ' + V(u'shell_pred_diff', None, u'壳谓词分歧') + u' 行 ⇎ 少的行数与非空壳行枚数'
    + u'逐份相等(账 ' + V(u'pp_gap_close', None, u'缺口账') + u'); 片段序列 ' + J(u'pp_rows', u'片段行') + u' 行。 '
    + u'页码另有两把尺: “整行只由数字与空格组成且只含一段数字”报 ' + J(u'pgnum', u'naive页码') + u' 行, 其中被壳尺认下的只有 '
    + J(u'pgnum_shell', u'壳内页码') + u' 行——多吃 ' + J(u'pgnum_overstrip', u'多吃页码') + u' 行, '
    + u'它们是 1122 第 ' + V(u'pgnum', 0, u'naive页码1122') + u' 枚落在 ' + C(u'pgnum_row_lines', 0, 0, u'表格行')
    + u' 行的 RCV 表, 与 9293 的 ' + C(u'pgnum_row_lines', 1, 0, u'抬头行') + u'/' + C(u'pgnum_row_lines', 1, 1, u'表行')
    + u'/' + C(u'pgnum_row_lines', 1, 2, u'表行2') + u' 行(编号抬头与表体), 真页码行反倒带方括号 “[Page n]” 不在这一式里。 '
    + u'目录里那一行靠点线引路: 严格 “…” ' + J(u'head_toc_leader_strict', u'点线严格') + u' ⇎ 放宽到 “点+空格” '
    + J(u'head_toc_leader_spaced', u'点线宽松') + u'——两份旧新 TCP 文书都不靠它。')

LINES.append(
    u'🈏 换代留下的字符痕迹只在参考文献与署名里: BOM ' + J(u'bom', u'BOM') + u' 枚(新式四份各一枚, 折平后仍在 '
    + V(u'bom_survives', None, u'BOM存活') + u' 枚), 非 ASCII ' + J(u'na_total', u'非ASCII枚') + u' 枚 ⇎ 逐行 '
    + J(u'na_lines', u'非ASCII行') + u' 行 ⇎ 旧式两份合计 ' + V(u'na_old_total', None, u'旧式非ASCII合计') + u' 枚; '
    + u'成分账 ' + J(u'na_ledger', u'非ASCII账') + u' ⇎ 位置账 ' + J(u'na_place_ledger', u'位置账') + u' 全平: '
    + u'署名行 ' + J(u'na_name_lines', u'署名行') + u' ⇎ 参考条目行 ' + J(u'na_ref_entry_lines', u'参考条目')
    + u' ⇎ 地址块 ' + J(u'na_addr_bullet', u'地址块') + u' ⇎ 其余 ' + J(u'na_other_lines', u'其余非ASCII行')
    + u' 行; 不同码位 ' + V(u'na_cp_tot', None, u'码位合计') + u' 个全部属新式(' + V(u'na_cp_new', None, u'新式码位')
    + u' 个)。 这些字符离 References 标题多远: 该标题在 ' + J(u'ref_print_n', u'References印次') + u' 处印出(目录 '
    + J(u'ref_toc_line', u'Ref目录行') + u' ⇎ 正文 ' + J(u'ref_body_line', u'Ref正文行') + u' 行, 账 '
    + J(u'ref_ledger', u'Ref账') + u'), 首枚非ASCII 距正文那次 ' + J(u'na_first_after_ref', u'首个非ASCII距离')
    + u' 行——-1 是口径不存在(1122 面上连 “References” 标题也没有 ⇎ 9113 那一枚只在署名行, 在 References 之前)。 '
    + u'署名抬头 ' + J(u'addr_head_n', u'署名抬头印次') + u' 次 ⇎ ' + J(u'addr_head_line', u'署名抬头行') + u' 行。')

LINES.append(
    u'🪜 同一个问题——一条空闲连接多久该关掉——五份各答一次, 答句逐字取面: ' + ANSW(0) + u' ⇎ ' + ANSW(1) + u' ⇎ '
    + ANSW(2) + u' ⇎ ' + ANSW(3) + u' ⇎ ' + ANSW(4) + u'。 词 ' + J(u'ans_words', u'答句词数') + u'(合计 '
    + V(u'ans_words_tot', None, u'五句词合计') + u') ⇎ 字符 ' + J(u'ans_chars', u'答句字符') + u' ⇎ 整句跨 '
    + J(u'ans_sent_span', u'答句跨行') + u' 行 ⇎ 锚针只跨 ' + J(u'ans_needle_span', u'锚针跨行') + u' 行(句比针多 '
    + J(u'ans_needle_gap', u'针句行差') + u' 行) ⇎ 所在自然段 ' + J(u'ans_block_lines', u'段行数') + u' 行。 '
    + u'首行 ' + J(u'ans_sent_line', u'答句首行') + u' ⇎ 末行 ' + J(u'ans_sent_end', u'答句末行') + u' —— 这两排数由发射遍的'
    + u'逐字符对照表(fmap)导出, 建条遍另用累积长度表读过同一句(副本 ' + J(u'mk_ans_sent_line', u'建条遍首行') + u'/'
    + J(u'mk_ans_sent_span', u'建条遍跨行') + u'), 两把尺对拍 ' + V(u'ans_line_close', None, u'首行对拍') + u' ⇎ '
    + V(u'ans_span_close', None, u'跨行对拍') + u'; 行距减窗内实有非壳行 ' + J(u'ans_row_ledger', u'窗内行账')
    + u'(答句那几行没有一行页壳: ' + J(u'ans_shell_rows', u'段内壳行') + u')。 '
    + u'五句里唯一逐字复述的一对是两份 TCP 文书: 9293 的答句比 1122 多 ' + V(u'ans_tagdiff', None, u'答句字符差')
    + u' 字符, 恰是它给同一句缀的两枚编号标注(' + V(u'ans_tag_len', None, u'标注字符') + u', 账 '
    + V(u'ans_tag_len_ledger', None, u'标注账') + u'; 逐句标注数 ' + J(u'ans_tag_n_in_sent', u'答句内编号')
    + u'), 去掉标注两式同句(' + V(u'ans_pair_same', None, u'去编号同句') + u')。 五句全以句点收尾('
    + J(u'ans_punct', u'答句带句点') + u'), 全为 ASCII(' + J(u'ans_na', u'答句非ASCII') + u')。')

LINES.append(
    u'🔤 说法换了三代, 拼写也跟着换: keep-alive 家族 ' + J(u'ka_hyphen', u'连字拼法') + u' 枚带连字符, 拼法种数 '
    + J(u'ka_form_n', u'拼法种数') + u'——1122/9293 同用 “keep-alive”+“keep-alives” 两式('
    + J(u'ka_forms', u'拼法清单') + u'), 9112/9113 只剩连字一式, 9000 通篇不用这个词(合并写法 '
    + V(u'ka_merged', None, u'合并拼法') + u' 枚)。 “idle” 整词 ' + J(u'idle_term', u'idle枚') + u' 枚 ⇎ 复合术语 '
    + u'“idle timeout” ' + J(u'idle_compound', u'idle timeout枚') + u' 枚(9000 独占), “persistent” '
    + J(u'persist', u'persistent枚') + u' 枚(9112 一代 HTTP/1.1 的说法, 9113 只剩 ' + V(u'persist', 3, u'9113 persistent')
    + u' 枚, 别三份 ' + V(u'persist', 0, u'1122 persistent') + u' 枚)。 拼写对峙两式并存的只有旧拼法那份:'
    u' acknowledgement/acknowledgment ' + J(u'ack', u'ack两式') + u'(少数派 ' + J(u'ack_minor', u'ack少数')
    + u' 枚, 偏斜 ' + J(u'ack_skew', u'ack偏斜') + u'——-1 是那一式一枚也没有, 口径不存在), '
    + u'implementors/implementers ' + J(u'impl', u'implement两式') + u'(独有一式 ' + JL(u'impl_own', u'各家独有') + u')。 '
    + u'拼写族总量 ' + J(u'spell_tot', u'拼写总量') + u' ⇎ 全库独有的式 ' + V(u'spell_own_tot', None, u'独有式')
    + u' 条(' + JL(u'spell_own', u'独有清单') + u')。 子串尺与整词尺之差合计 ' + V(u'spell_ruler_gap_tot', None, u'拼写尺差')
    + u' 枚——“keep-alive” 被子串尺读进 “keep-alives” 里那一枚就是这类。')

LINES.append(
    u'🔢 时长的三种写法在五份里各占一档: 词写 “two hours” ' + J(u'num_word_two', u'词写两小时') + u' 枚 ⇎ '
    + u'长写 “no less than two hours” ' + J(u'num_longform_two', u'长写两小时') + u' 枚 ⇎ 数字写(“2 hours”/“120 minutes”) '
    + V(u'num_digit_two_tot', None, u'数字写合计') + u' 枚——两份 TCP 文书把唯一的定值写成词, 数字写一枚也没有('
    + J(u'num_digit_two', u'数字写逐份') + u')。 带单位的数值项由邻接尺现读: ' + J(u'numval_n', u'数值项') + u' 项 ⇎ '
    + u'把单数 “s” 也算上 ' + J(u'numval_wide_n', u'数值项宽尺') + u' 项 ⇎ 采集遍那条正则选择支读到 '
    + JL(u'num_pairs_pick', u'正则读数') + u' —— 两把尺的差 ' + J(u'num_ruler_gap', u'数值尺差') + u' 枚在 1122 面上: '
    + u'它那枚 “120 seconds”(IP 重组窗)在原面被硬换行切在 ' + C(u'numw', 0, 7, u'120 seconds 行内') + u' 行行首行尾两侧, '
    + u'邻接尺读不到; 宽尺比严尺多读的那两枚是 “3 s”(1122)与 “10 s”(9293): ' + JL(u'numval_s_extra', u'宽尺多读') + u'。 '
    + u'14 个候选数字式里全库一枚也读不到的 ' + V(u'num_cold_n', None, u'冷档数') + u' 式(' + JL(u'num_cold', u'冷档清单')
    + u'), 热档 ' + V(u'num_hot_n', None, u'热档数') + u' 式; 各家独有的数值 ' + V(u'num_own_tot', None, u'独有数值')
    + u' 项(' + JL(u'num_own', u'独有数值清单') + u'), 命名列相加=去重枚数(账 ' + J(u'num_lit_close', u'数值账') + u')。 '
    + u'9000 不定值而定倍数: “three times” ' + C(u'numw', 4, 4, u'9000 三次') + u' 枚, 判词 ' + AR(27) + u'; '
    + u'参数名带下划线式 ' + J(u'par_under', u'下划线名') + u' 枚 ⇎ 五个候选名合计 ' + J(u'par_n', u'参数名合计')
    + u' 枚, 其中只在本面出现的 ' + JL(u'par_own', u'独有参数名') + u'(9113 的 SETTINGS_TIMEOUT ⇎ 9000 的 max_idle_timeout): '
    + AR(21) + u' ⇎ ' + AR(23) + u'。 十六进制字面量 ' + J(u'hexes', u'十六进制') + u' 枚——HTTP/2 与 QUIC 面各给一整套('
    + V(u'hexes', 3, u'9113 十六进制') + u'/' + V(u'hexes', 4, u'9000 十六进制') + u'), 两份 TCP 文书一枚也没有。')

LINES.append(
    u'✂ 判词针 ' + V(u'needle_n', None, u'针总数') + u' 枚 × ' + str(NSRC) + u' 份, 四档口径各读一遍: '
    + u'原面逐行 ' + J(u'role_line_n', u'逐行档') + u' ⇎ 全篇折平 ' + J(u'role_fold_n', u'折平档') + u' ⇎ 摘壳折平 '
    + J(u'role_sh_n', u'摘壳档') + u' ⇎ 摘壳去编号 ' + J(u'role_tag_n', u'去编号档') + u'(四档合计 ' + JL(u'face_tot', u'四档合计')
    + u', 逐档增益 ' + JL(u'face_gain', u'档间增益') + u' ⇎ 单调上升的档 ' + V(u'face_mono', None, u'单调档') + u'/3)。 '
    + u'逐行漏读而折平读到的 ' + V(u'role_line_miss_n', None, u'逐行漏读') + u' 枚全由硬换行切开(壳切 '
    + V(u'gain_sh_tot', None, u'摘壳增益') + u' 枚 ⇎ ' + J(u'role_shell_n', u'壳切针') + u'), 按份 '
    + J(u'role_wrap_n', u'切开针逐份') + u'; 增益按“枚”记 ' + V(u'gain_fold_tot', None, u'折平增益枚') + u' 枚 = 切开针数 '
    + V(u'split_wrap_n', None, u'切开针数') + u' + 本来行内就读通那些针新增的 ' + V(u'gain_fold_dup', None, u'折平重读')
    + u' 枚。 ' + V(u'split_n', None, u'切开总数') + u' 枚切开针的两半各归一行(首末行一律相邻: ' + V(u'split_adj_n', None, u'相邻数')
    + u'), 两半合计 ' + V(u'split_rows_tot', None, u'两半字符') + u' 字符——整串拿到首行那一行一枚也读不通(反向命中 '
    + V(u'split_full_on_head', None, u'整串首行') + u'), 两半各自回自己那一行全读得通(' + V(u'split_half_ok', None, u'两半读通')
    + u'/' + V(u'split_n', None, u'切开总数') + u'): ' + u'; '.join(SPC(x) for x in SPLITREC) + u'。 '
    + u'第四档另救一枚, 不是换行而是编号标注把它切开: ' + AR(2) + u'(针 ' + JL(u'tagcut_needle', u'编号切针')
    + u' ⇎ 夹 ' + JL(u'tagcut_mid', u'标注原文') + u' ' + V(u'tagcut_tag_chars', 0, u'标注字符') + u' 字符 ⇎ 两半之宽减针长 '
    + V(u'tagcut_eaten', 0, u'吃掉宽') + u', 账 ' + V(u'tagcut_ledger', 0, u'编号切账') + u' ⇎ 全篇被标注吃掉的字符 '
    + J(u'tag_eaten', u'标注吃字') + u')。 还有 ' + V(u'tone_straddle_n', None, u'跨行义务词') + u' 对义务词整词跨行, '
    + u'由原面逐行现定位(' + J(u'tone_straddle', u'跨行逐份') + u'), 式样只有一种(' + JL(u'tone_straddle_nd', u'跨行式样')
    + u'), 两行之间不夹壳行(' + V(u'tone_straddle_gap_shell', None, u'跨行夹壳') + u' ⇎ 夹空行 '
    + V(u'tone_straddle_blank', None, u'跨行夹空') + u'), 与折平档的增益逐份账平(' + V(u'tone_straddle_ledger', None, u'跨行账')
    + u'): ' + u'; '.join(pair_anchor(LBL.index(x[0]), x[2], x[3], TONE[x[1]])[0] + u' ⇎ '
                           + pair_anchor(LBL.index(x[0]), x[2], x[3], TONE[x[1]])[1] for x in TSP) + u'。')

LINES.append(
    u'🏷 关掉连接的权利五份交给五处: 1122 把默认交给实现者且默认关 ' + AR(0) + u', 间隔定值 ' + AR(1)
    + u'; 9293 同一句照登并加编号, 另把可配置性写成判词 ' + AR(2) + u'/' + AR(3) + u'; 9112 一个数也不定 '
    + AR(8) + u', 只说服务器通常有某个值 ' + AR(9) + u' ⇎ 连接可随时关 ' + AR(10) + u'; 9113 把决定权给服务器 '
    + AR(17) + u' ⇎ 又劝两端尽量保持 ' + AR(16) + u' ⇎ 关闭要先发 GOAWAY ' + AR(18) + u'; 9000 给算法不给定值: 取两端宣告值的最小 '
    + AR(24) + u' ⇎ 只一端宣告时取那一枚 ' + AR(25) + u' ⇎ 且不许低于 3×PTO ' + AR(27)
    + u'。 五处判词所在节: ' + V(u'sec_no', 0, u'1122节号') + u'/' + V(u'sec_no', 1, u'9293节号') + u'/'
    + V(u'sec_no', 2, u'9112节号') + u'/' + V(u'sec_no', 3, u'9113节号') + u'/' + V(u'sec_no', 4, u'9000节号')
    + u' 节, 标题逐份 ' + J(u'sec_print_n', u'节标题印次') + u' 次(目录 ' + J(u'sec_toc_line', u'节目录行') + u' ⇎ 正文 '
    + J(u'sec_body_line', u'节正文行') + u' 行, 缩进 ' + J(u'sec_body_indent', u'节正文缩进') + u' 列), 窗宽 '
    + J(u'sec_lines', u'节窗行') + u' 行 ⇎ ' + J(u'sec_chars', u'节窗字符') + u' 字符 ⇎ 占全篇 ' + J(u'sec_span_pct', u'节占比')
    + u'% ⇎ 窗内页壳 ' + J(u'sec_shell_rows', u'节窗壳行') + u' 行 ⇎ 子节 ' + J(u'sec_child', u'节内子节') + u' 个; 答句距节首 '
    + J(u'sec_ans_gap', u'答句距节首') + u' 行 ⇎ 五句都在自己那节内(账 ' + WS(u'sec_ans_inside', u'节内含答句') + u'); 节标题在正文面命中 '
    + J(u'sec_hit_n', u'节标题命中') + u' 次(9000 的 “Idle Timeout” 是通用词, ' + V(u'sec_hit_n', 4, u'9000节标题命中')
    + u' 次)。 节内义务词 ' + J(u'sec_tone_tot', u'节内义务词') + u' 枚(合计 ' + V(u'sec_tone_tot_all', None, u'节内义务词合计')
    + u'), 一枚也没有的节 ' + V(u'sec_tone_zero_n', None, u'零义务节') + u' 个。 各节摘出来逐行看: ' + ASEC(0) + u' ⇎ '
    + ASEC(1) + u' ⇎ ' + ASEC(2) + u' ⇎ ' + ASEC(3) + u' ⇎ ' + ASEC(4) + u'。')

LINES.append(
    u'🎭 义务词四档读数(摘壳整词): ' + J(u'tone_tot', u'义务词总量') + u' 枚 ⇎ 裸 MUST(MUST 减 MUST NOT) '
    + J(u'must_bare', u'裸MUST') + u' ⇎ MUST NOT 恒不大于 MUST(' + WS(u'mustnot_of_must', u'MUSTNOT含于MUST') + u'), 账 '
    + J(u'tone_must_ledger', u'MUST账') + u'/' + J(u'tone_ledger', u'义务词账') + u' 全平。 编号族是 9293 一家的: 摘壳面 '
    + V(u'tag_sh', 1, u'9293编号枚') + u' 枚 ⇎ 原行面 ' + V(u'tag_raw', 1, u'9293编号原行') + u' 枚(折行不吞编号)⇎ 四种形状: '
    + u'括号式 ' + V(u'tag_paren', 1, u'括号式') + u' ⇎ 括号带说明 ' + V(u'tag_paren_prose', 1, u'括号说明') + u' 枚('
    + AF(1, u'MUST-4 -- note') + u') ⇎ 方括号式 '
    + V(u'tag_paren_bracket', 1, u'方括号式') + u' ⇎ 裸式 ' + V(u'tag_bare', 1, u'裸编号') + u', 账 '
    + V(u'tag_form_ledger', 1, u'形状账') + u'; 按词种 MUST/SHOULD/MAY/SHLD/ED ' + C(u'tag_kinds', 1, 0, u'编号MUST') + u'/'
    + C(u'tag_kinds', 1, 2, u'编号MAY') + u'/' + C(u'tag_kinds', 1, 3, u'编号SHLD') + u'/' + C(u'tag_kinds', 1, 4, u'编号ED')
    + u' 枚(和 ' + V(u'tag_kind_sum', 1, u'编号词种和') + u', 账 ' + V(u'tag_kind_close', 1, u'词种账') + u'); 括号式落点: 句末句号前 '
    + V(u'tag_paren_period', 1, u'编号在句号前') + u' ⇎ 逗号前 ' + V(u'tag_paren_comma', 1, u'编号在逗号前') + u' ⇎ 句中 '
    + V(u'tag_paren_mid', 1, u'编号在句中') + u' 枚(账 ' + V(u'tag_paren_place_close', 1, u'落点账') + u'); 最大编号 '
    + V(u'tag_max_num', 1, u'最大编号') + u' ⇎ “individually labeled” 声明 ' + J(u'tag_decl', u'编号声明') + u' 行。 '
    + u'剥掉编号, 整词读数跌 ' + V(u'tone_drop_tot', 1, u'剥编号跌幅') + u' 枚(MUST ' + C(u'tone_drop_tag', 1, 0, u'跌MUST')
    + u' ⇎ MAY ' + C(u'tone_drop_tag', 1, 4, u'跌MAY') + u')——括号里的 MUST 本身也是整词, 所以这不是义务词少了而是口径没了。 '
    + u'引用与语态的换代: “RFC nnnn” 写法 ' + J(u'cit_rfc', u'RFC空格引用') + u' 处 ⇎ 连字符式 ' + J(u'cit_rfc_hyphen', u'RFC连字引用')
    + u' 处(只在 1122)⇎ 方括号式 ' + J(u'cit_brk', u'方括号引用') + u' 处 ⇎ 本表十编号里引到别家的 ' + J(u'cite_own', u'引用他家数')
    + u' 家; 第一人称 “we + 动词” ' + J(u'voice_weverb', u'第一人称动词') + u' 枚 ⇎ 非人称 “this document/this specification” '
    + J(u'voice_impersonal', u'非人称') + u' 枚。')

LINES.append(
    u'📐 套版长行池(折平 ≥40 字符): 各份去重 ' + J(u'pool_n', u'池枚数') + u' 枚 ⇎ 原行 ' + J(u'pool_raw_rows', u'池原行')
    + u' 枚(重复印 ' + V(u'pool_dup', None, u'池重复') + u' 次), 五份并集 ' + V(u'pool_union', None, u'池并集') + u' 枚; '
    + u'放宽到 ≥25 字符并集多 ' + V(u'pool_widen', None, u'池放宽') + u' 枚(' + J(u'pool_n25', u'池25枚数') + u'/'
    + V(u'pool_union25', None, u'池25并集') + u')。 按“几份共用”分档 ' + J(u'pool_tier', u'共用分档') + u': 五份全用 '
    + V(u'pool_all_five', None, u'五份共用') + u' 枚 ⇎ 恰好新式四份共用 ' + V(u'pool_new_four', None, u'四份共用')
    + u' 枚, 两档相加 ' + V(u'pool_tier_close', None, u'分档账') + u' 账平 ⇎ 乘份数 ' + V(u'pool_sum_close', None, u'份数账')
    + u'; 容斥 各份之和 − 两两 + 三三 − 四四 − 并集 = ' + V(u'pool_ie_close', None, u'容斥账') + u'。 两两配对 '
    + PAI(u'pool_pair_by', u'配对枚数') + u'(合计 ' + V(u'pool_pair_tot', None, u'配对合计') + u'), 最热的对 '
    + V(u'pool_max_pair', None, u'最热配对') + u' 枚 ⇎ 新式最冷的对 ' + V(u'pool_min_pair_new', None, u'新式冷对')
    + u' 枚。 1122 只与 9293 共行, 共 ' + V(u'pool_old_shared', None, u'旧式共行') + u' 枚, 而且共的是 TCP 正文行不是套版行: '
    + u'带义务词 ' + V(u'pool_old_shared_toned', None, u'旧式共行带义务') + u' ⇎ 提 RFC ' + V(u'pool_old_shared_rfcline', None, u'旧式共行提RFC')
    + u' ⇎ 讲本文件 status ' + V(u'pool_old_shared_status', None, u'旧式共行status') + u' ⇎ 带 BOM '
    + V(u'pool_old_shared_bom', None, u'旧式共行BOM') + u' 枚——牵进 1122 的其余 ' + V(u'pool_pair_old_n', None, u'旧式冷对数')
    + u' 对全为 0(' + V(u'pool_pair_old', None, u'旧式配对') + u' 枚), 与它共用最多的 ' + V(u'pool_max_pair', None, u'最热配对')
    + u' 枚也只在 TCP 那一侧。 例: ' + AR(34) + u' ⇎ ' + AF(0, u'one garbage octet', F['blk_lo'][5]) + u' ⇎ '
    + AF(1, u'one garbage octet', F['blk_lo'][6]) + u'。 新式四份共用的那一堆 ' + V(u'pool_shared_new', None, u'新式共用枚')
    + u' 枚里带义务词 ' + V(u'pool_shared_toned', None, u'新式共用带义务') + u' ⇎ 提 RFC ' + V(u'pool_shared_rfcline', None, u'新式共用提RFC')
    + u' ⇎ 讲 status ' + V(u'pool_shared_status', None, u'新式共用status') + u' 枚——套版行确实套版, 判词行不外流('
    + V(u'pool_old_toned', None, u'旧式带义务枚') + u'/' + V(u'pool_new_toned', None, u'新式带义务枚') + u')。')

LINES.append(
    u'🔗 9293 把 1122 的保活节重写了一遍: 段内句数 ' + V(u'ovl_s1', None, u'1122句数') + u' ⇎ ' + V(u'ovl_s2', None, u'9293句数')
    + u' 句(块 ' + JT(u'ovl_block_lines', u'块行') + u' 行 ⇎ 正文段 ' + JT(u'ovl_spec_lines', u'正文段行') + u' 行, 其中壳行 '
    + V(u'ovl_shell_in_block', None, u'正文段壳行') + u' 行 ⇎ 去壳后 ' + V(u'ovl_spec_lines_content', 0, u'1122正文行')
    + u'/' + V(u'ovl_spec_lines_content', 1, u'9293正文行')
    + u' 行); 逐字相同的句子 ' + V(u'ovl_same_raw', None, u'逐字同句') + u' ⇎ 去编号后 ' + V(u'ovl_same_tag', None, u'去编号同句')
    + u' ⇎ 再把 implementers→implementors/acknowledgment→acknowledgement 归拼后 ' + V(u'ovl_same_canon', None, u'归拼同句')
    + u' 句(只靠去编号多出 ' + V(u'ovl_tag_only', None, u'编号独有') + u' 句 ⇎ 三档单调 ' + V(u'ovl_monotone', None, u'同句单调')
    + u'), 新句 ' + V(u'ovl_new', None, u'新句数') + u' 句 = 讨论段升格 ' + V(u'ovl_disc_promoted', None, u'讨论升格')
    + u' + 全新生 ' + V(u'ovl_new_n', None, u'全新生') + u'(账 ' + V(u'ovl_new_close', None, u'新句账') + u')。 新句的位置也由面导: '
    u'首行 ' + JS(u'ovl_new_lines', u'新句首行') + u' ⇎ 各跨 ' + JS(u'ovl_new_rows', u'新句跨行') + u' 行 ⇎ 窗内被编号切开 '
    + JS(u'ovl_new_tagcut', u'新句编号切') + u' 处, 逐句 ' + u' ‖ '.join(
        AF(1, z[:26], F['ovl_new_lines'][j]) for j, z in enumerate(OVLNEW[:4])) + u'。 主答句那一段的逐词对照由序列匹配器现导('
    + u'不预设哪句相同): 动作序列 ' + JL(u'blk_tcp_op_tags', u'对齐动作') + u' 段, 相同词 ' + V(u'blk_tcp_equal', None, u'相同词')
    + u' 词分 ' + V(u'blk_tcp_equal_runs', None, u'相同段数') + u' 段(最长 ' + V(u'blk_tcp_equal_max', None, u'最长相同段')
    + u' 词) ⇎ 删 ' + V(u'blk_tcp_drop', None, u'删词') + u' ⇎ 插 ' + V(u'blk_tcp_insert', None, u'插词') + u' ⇎ 替换 '
    + V(u'blk_tcp_replace', None, u'替换处') + u' 处; 三本词账 ' + V(u'blk_tcp_word_ledger', None, u'词账1') + u'/'
    + V(u'blk_tcp_word_ledger2', None, u'词账2') + u'/' + V(u'blk_tcp_word_gap_ledger', None, u'词差账') + u' ⇎ 字符账 '
    + V(u'blk_tcp_char_ledger', None, u'字符账') + u'(删 ' + V(u'blk_tcp_char_drop', None, u'删字符') + u' ⇎ 插 '
    + V(u'blk_tcp_char_insert', None, u'插字符') + u' ⇎ 去编号后 ' + V(u'blk_tcp_naked_chars', None, u'裸段字符')
    + u' 字符); 9293 那一段不是 1122 的子串(' + V(u'blk_tcp_verbatim_sub', None, u'子串判定') + u'), 段长差 '
    + V(u'blk_tcp_len_gap', None, u'段长差') + u' 字符里 ' + V(u'blk_tcp_tag_chars', None, u'编号字符') + u' 字符是五枚编号, '
    + u'每枚 ' + V(u'blk_tcp_tag_widths', 0, u'单枚编号宽') + u' 字符。 删掉的是 1122 的开场句 '
    + AF(0, PINS[0][1], F['blk_lo'][0]) + u', 添进来的是 ' + AF(1, PINS[1][1], F['blk_lo'][1]) + u'。')

LINES.append(
    u'🧩 “The key words …” 模板段 1122 面上根本没有: 段首偏移 ' + J(u'kw_at', u'模板段偏移') + u' ⇎ 首行 '
    + J(u'kw_minus_row', u'模板段首行') + u' 行——-1 是口径不存在, 不是零(' + V(u'kw_docs', None, u'模板段份数')
    + u' 份有这段)。 六对之间整段逐字相同 ' + PKW(u'kw_same', u'整段相同') + u' 对(共 ' + V(u'kw_same_n', None, u'相同对数')
    + u'), 而拿段窗报出的首末行回原文件截那段逐行序列再比, 只有 ' + V(u'kw_same_raw_n', None, u'逐字相同对') + u' 对也相同——'
    + u'差的 ' + V(u'kw_wrap_diff', None, u'分行差对') + u' 对是同样的词在两份文书里换了分行位置, 两把尺判法之和 '
    + V(u'kw_face_close', None, u'两尺判法') + u'。 共头 ' + PKW(u'kw_head_pre', u'共头词') + u'(最短 '
    + V(u'kw_head_min', None, u'共头最短') + u' ⇎ 最长 ' + V(u'kw_head_max', None, u'共头最长') + u' 词, 四路齐头 '
    + V(u'kw_all_head', None, u'四路齐头') + u' 词)⇎ 共尾 ' + PKW(u'kw_head_suf', u'共尾词') + u' 词, 其中零尾 '
    + V(u'kw_suf_zero_n', None, u'零尾对') + u' 对 ⇎ 非零尾 ' + V(u'kw_suf_nz_n', None, u'非零尾对') + u' 对(和 '
    + V(u'kw_suf_tot', None, u'共尾合计') + u'), 词汇最多的一段 ' + V(u'kw_vocab_max', None, u'模板词汇') + u' 个不同词。 '
    + u'尾巴各家接各家: ' + AF(1, u'BCP 14 [3] [12]', F['blk_lo'][11]) + u' ⇎ ' + AF(2, u'BCP 14 [RFC2119] [RFC8174]', F['blk_lo'][12])
    + u'(该式命中 ' + J(u'kw_cite_pair', u'新式引用命中') + u' 次 ⇎ 旧式 ' + J(u'kw_cite_bcp', u'旧式引用命中') + u' 次)。')

LINES.append(
    u'¶ 段落层共 ' + str(len(PINS)) + u' 段(段界一律由字面针在摘壳折平面上现取, '
    u'首末行经 fmap 映回原行): 五份主答句段 + 两份 TCP 的讨论段与探活段 ⇎ 9000 的 3×PTO 段 ⇎ 9113 的 SETTINGS 段 ⇎ '
    u'9112 的关闭时机段 ⇎ 9113 的发送方式段 ⇎ 四份关键词模板段。 行数 ' + PJ(u'blk_rows', u'段行') + u'(合计 '
    + V(u'blk_rows_tot', None, u'段行合计') + u' ⇎ 五段 ' + V(u'blk_five_rows', None, u'五段行') + u') ⇎ 字符 '
    + PJ(u'blk_chars', u'段字符') + u'(合计 ' + V(u'blk_words_tot', None, u'段词合计') + u' 词/' + V(u'blk_five_chars', None, u'五段字符')
    + u' 字符 ⇎ 五段 ' + V(u'blk_five_words', None, u'五段词') + u' 词) ⇎ 不同词 ' + PJ(u'blk_vocab', u'段词汇') + u'。 '
    + u'主答句五段每行 ' + J(u'blk_words_per_row', u'每行词') + u' 词, 单行成段的 ' + V(u'blk_one_line_n', None, u'单行段')
    + u' 段——72 列硬换行下没有一段塞得进一行。 段窗首行比答句首行早 ' + J(u'blk_head_gap', u'段首提前') + u' 行('
    + J(u'blk_head_row', u'段首行') + u'/' + J(u'blk_tail_row', u'段末行') + u'), 五句都落在自己的窗内('
    + J(u'blk_ans_inside', u'答句在窗内') + u')。 段窗首末行回原文件自验 ' + V(u'seg_rt_ok', None, u'段行自验') + u'/'
    + V(u'seg_rt_n', None, u'段行自验数') + u': 整串就在那一行读通的 ' + V(u'seg_rt_whole', None, u'段行整串') + u' 处 ⇎ '
    u'靠两半读通的 ' + V(u'seg_rt_cut', None, u'段行切开') + u' 处(首 ' + V(u'seg_rt_head', None, u'段行首半') + u' ⇎ 末 '
    + V(u'seg_rt_tail', None, u'段行末半') + u')。 段内义务词三轨同值(MUST ' + PJ(u'tone_must_blk', u'段内MUST') + u' ⇎ '
    u'MAY ' + PJ(u'tone_may_blk', u'段内MAY') + u' ⇎ SHOULD ' + PJ(u'tone_should_blk', u'段内SHOULD') + u' ⇎ '
    u'MUST NOT ' + PJ(u'tone_mustnot_blk', u'段内MUSTNOT') + u' ⇎ 编号 ' + PJ(u'tone_tag_blk', u'段内编号') + u'), '
    + u'与游程尺、正则尺的差 ' + V(u'blk_tone_ruler_close', None, u'三轨账') + u'; 1122 段内编号 ' + V(u'tone_tag_blk', 0, u'1122段内编号')
    + u' ⇎ 9293 主答句段 ' + V(u'tone_tag_blk', 1, u'9293段内编号') + u' 枚。')

LINES.append(
    u'🔁 反向对照 ' + V(u'neg_n', None, u'反向针数') + u' 式 ⇎ ' + V(u'neg_probes', None, u'反向探针') + u' 次探针: 被排除的那几份上'
    + u'命中 ' + V(u'neg_zero_hits', None, u'反向命中') + u' 枚 ⇎ 每一式在自己那一份都读得到(' + V(u'neg_owner_present', None, u'反向有主')
    + u'/' + V(u'neg_n', None, u'反向针数') + u'), 一枚全冷的也没有(' + JL(u'neg_cold_probes', u'全冷反向') + u')。 有主的式由面导锚: '
    + AO(u'max_idle_timeout') + u' 只在 9000 ⇎ ' + AO(u'SETTINGS_TIMEOUT') + u' 只在 9113 ⇎ ' + AO(u'the key words')
    + u' 四份有 ⇎ ' + AO(u'keep-alive') + u' 前四份有; 没主的三式只能报整词读数: “PTO”“quic”“http/2” 在被排除的那几份上'
    + u'一律 ' + V(u'neg_zero_hits', None, u'反向整词零') + u' 枚 ⇎ 同一格换子串尺就有: 1122 面 “PTO” '
    + C(u'neg_sub', 0, 13, u'1122 PTO 子串') + u' ⇎ 整词 ' + C(u'neg_word', 0, 13, u'1122 PTO 整词') + u' 枚(promptly 里), '
    + u'1122 面 “quic” ' + C(u'neg_sub', 0, 9, u'1122 quic 子串') + u' ⇎ 整词 ' + C(u'neg_word', 0, 9, u'1122 quic 整词')
    + u' 枚(quickly 里)。 唯一一枚换档的反向针是 “[Page 1]”——它走全篇折平面: 该面 1122 '
    + V(u'page_lit_fold', 0, u'折平面Page1') + u' 枚 ⇎ 摘壳面 ' + WS(u'page_lit_sh', u'摘壳面Page1合计') + u' 枚, '
    + u'因为它整行住在 1122 第 ' + V(u'page_lit_rows', 0, u'Page1所在行') + u' 行的眉/页脚里, '
    + V(u'page_lit_rows_shell', None, u'Page1壳外行') + u' 行在壳尺之外——壳面的锚给不出, 只能以读数登记('
    + u'唯一换档 ' + V(u'neg_fold_n', None, u'反向换档') + u' 式)。 '
    + u'两把词尺的差要单列: 子串尺在 ' + str(len(F[u'neg_sub_false_rows'])) + u' 个(份,式)格上多读 ' + V(u'neg_sub_false', None, u'子串多读')
    + u' 枚(该格子串尺共读 ' + V(u'neg_sub_ruler', None, u'子串尺读数') + u'), 例: 9000 面 “quic” '
    + C(u'neg_sub', 4, 9, u'9000 quic 子串') + u' ⇎ 整词 ' + C(u'neg_word', 4, 9, u'9000 quic 整词') + u' 枚, 1122 面 “keep-alive” '
    + C(u'neg_sub', 0, 8, u'1122 KA 子串') + u' ⇎ 整词 ' + C(u'neg_word', 0, 8, u'1122 KA 整词') + u' 枚。')

LINES.append(
    u'🧮 闭合账: 布尔门 ' + V(u'bool_clos_n', None, u'采集遍门') + u' + ' + V(u'bool_clos2_n', None, u'发射遍门') + u' = '
    + V(u'bool_all_n', None, u'门合计') + u' 道全绿(' + V(u'bool_all_sum', None, u'门绿数') + u'), 每道都能红; 恒等式 '
    + V(u'zid_scan_n', None, u'采集遍恒等式') + u' + ' + V(u'zid_scan2_n', None, u'发射遍恒等式') + u' = '
    + EXPR(F[u'zid_scan_n'] + F[u'zid_scan2_n'], u"B82V('zid_scan_n')+B82V('zid_scan2_n')", u'恒等式合计') + u' 条全平, 每条都减掉了真量。 '
    + u'与采集遍逐键对账 ' + V(u'pick_agree', None, u'对账符') + u' 键符 ⇎ ' + V(u'pick_diff', None, u'对账不符') + u' 键不符 ⇎ '
    + u'判词针数差 ' + V(u'pick_needle_gap', None, u'针数差') + u'。 本遍的四档读数不抄采集遍的正则, 而是把 '
    + V(u'needle_n', None, u'针总数') + u' 枚针在四张面串上各数一遍(' + WS(u'role_hit_by_face', u'逐份读到的针数') + u' 枚逐份): '
    + u'换行切开 ' + V(u'split_wrap_n', None, u'切开针数') + u' + 壳切 ' + WS(u'role_shell_n', u'壳切针和') + u' 枚 = 逐行漏读 '
    + V(u'role_line_miss_n', None, u'逐行漏读') + u' 枚(Z 式), 第四档再救 ' + V(u'gain_tag_key', None, u'去编号增益格')
    + u' 枚 = 编号切开清单长度 ' + V(u'split_tagcut_n', None, u'编号切数') + u' 枚。 谱系: ' + J(u'years', u'抬头年') + u', 跨 '
    + EXPR(max(F[u'years']) - min(F[u'years']),
           u"max([%s])-min([%s])" % (u','.join([u"%s('years', %d)" % (FN, i) for i in range(NSRC)]),
                                     u','.join([u"%s('years', %d)" % (FN, i) for i in range(NSRC)])), u'年代跨度')
    + u' 年; 版式两代之间没有一枚共用的长行(牵进 1122 的配对除 TCP 那 ' + V(u'pool_old_shared', None, u'旧式共行')
    + u' 枚外全冷), 换代换的是措辞与版式, 不是那份 RFC 的编号。')
# --- 段二 END ---

# --- 段三 BEGIN --- (自 replay 恒等式 → 复核锚归属 → 落盘 flat/deriv/atoms/checks 与条目文件)
BADZID = []
for v, w in Z2:
    got = eval(v, {FN: BB82})
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
        print(u'  针多解: %s 针=%s 首行=%d 候选=%d 全针=%s' % (x[0], x[1], x[2], x[3], x[4][:70]))
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
    got = [e for e in ELEMS.get(s, []) if eval(e, {FN: BB82}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, [(x, body[max(0, body.index(x) - 90):body.index(x) + 30]) for x in NOEXPR[:3]]
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv82.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
F['contract_n'] = len(F) + 1
json.dump(F, io.open(u'corpus/_b82flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms82.txt', 'w', encoding='utf-8', newline=NL).write(
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
           u'needle_n': F[u'needle_n'], u'needles': ROLEN, u'win': WIN, u'neg': [[x[0], x[1], x[2]] for x in NEG],
           u'zid': [[v, w] for v, w in ZV], u'litk': LITK,
           u'blk': PTXT, u'pins': [[LBL[i], s, e] for i, s, e in PINS],
           u'split': [[LBL[LBL.index(LBL[x[1]])] + u'#' + str(x[0]), ROLEN[x[0]], x[2], x[3]] for x in SPLITREC],
           u'tagcut': [[LBL[x[1]], ROLEN[x[0]], x[2], x[3], x[6], x[9], x[10]] for x in TAGCUTREC],
           u'straddle': [[x[0], TONE[x[1]], x[2], x[3], x[4]] for x in TSP],
           u'new_sent': OVLNEW, u'new_lines': F[u'ovl_new_lines'], u'ans': F[u'ans'],
           u'tcp_ops': [[x[0], x[1], x[2], x[3], x[4]] for x in OPC],
           u'tcp_1122': PTXT[0], u'tcp_9293': PTXT[1],
           u'kw': [PTXT[n] for n in KWK], u'kw_lbl': [LBL[PINS[n][0]] for n in KWK],
           u'pool_pair': F['pool_pair'], u'pool_trip': F['pool_trip'], u'pool_quad': F['pool_quad'],
           u'oshares': sorted(OSHAL), u'qshares': sorted([x for x in SHARED if pres_n(x) >= 3]),
           u'num_pairs': [[list(x) for x in F[u'num_pairs'][i]] for i in range(NSRC)],
           u'pgnum_rows': F[u'pgnum_row_lines'],
           u'closure_keys': sorted([k for k in F if u'close' in k or u'ledger' in k]),
           u'flat': F})
json.dump(CH, io.open(u'corpus/_b82checks.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

ANS5 = [u'定值 + 默认关: keep-alives 由实现者自行取舍, 一旦用上间隔 MUST 不少于两小时(词写, 不带数字)',
        u'同一句照登并给义务词编上号(MUST-27/MUST-28), 另添一句“应用必须能自己关掉连接”',
        u'一个值也不给: 对这个超时(乃至它是否存在)不提任何要求, 只说服务器通常有这么个值',
        u'把刀交给服务器: 服务器可以终止空闲连接, 又劝两端尽量保持; 主动关闭要先发 GOAWAY',
        u'给算法不给定值: 空闲超时 = 两端宣告值的最小值, 且 MUST ≥ 三倍 PTO, 0 才是禁用']
ENTRY = u'corpus/babeltele/B82_idle_connection_timeout_five_answers.md'
srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 码位／原行 %d／非空行 %d／最长行 %d 列／换页 %d 枚／答句 %s)' % (
        PATH[i].split('/')[-1], F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        F[u'maxlen'][i], F[u'ff'][i], ANS5[i]) for i in range(NSRC))
    + u' (五份都是 RFC Editor 纯文本面: 回车 ' + str(sum(F[u'cr'])) + u' 枚 ⇎ 连字 0 枚 ⇎ 换页 '
    + str(sum(F[u'ff'])) + u' 枚只在 1122 ⇎ 页壳行 ' + str(sum(F[u'shell_lines'])) + u' 行 ⇎ 非 ASCII '
    + str(sum(F[u'na_total'])) + u' 枚全在新式四份; BOM ' + str(sum(F[u'bom'])) + u' 枚); 抬头年 '
    + u'⇎'.join(str(y) for y in F[u'years']) + u', 跨 ' + str(max(F[u'years']) - min(F[u'years'])) + u' 年; '
      + u'五句答话 ⇎ 十五段段落层 ⇎ 两把行号尺的对拍 ⇎ ' + str(F[u'split_n']) + u' 枚被硬换行切开的判词与 '
      + str(F[u'tagcut_n']) + u' 枚被编号标注切开的判词, 全部由面上位置导出, 一个都不手填。 '
      + u'RFC Editor 此刻的现行状态页与勘误页(9293 的 MUST-27/28 有没有被 errata 改过措辞、9112/9113 是否又被后继文档'
        u'替换了这句默认值)、现网服务器与内核实际取的空闲超时(规范给的数不等于装机行为)、'
        u'9293 把 1122 那节重写的编辑意图(文档里没有 changelog 判定)、各份 RFC 的现行引用关系, 都不可由在库文件判定, '
        u'只进解读注, 不进门槛)\n')
link = (u"；联结不是“同一份数据的两种序列化”, 而是“一条空闲连接多久该关掉、由谁说了算”在五份一手文书里的五种答法: "
        u"1122 给词写定值(“no less than two hours” " + str(F[u'num_longform_two'][1]) + u" 枚只在 9293 复述时出现, 1122 自己写“two hours” "
        + str(F[u'num_word_two'][0]) + u" 枚 ⇎ 带单位的数字项 " + str(F[u'numval_n'][0]) + u" 项里没有一个用于保活); "
        u"⇎ 9293 把同一句照登并加 " + str(F[u'tag_sh'][1]) + u" 枚编号(其中答句 " + str(F[u'ans_tag_n_in_sent'][1])
        + u" 枚), 删掉 1122 的开场句(" + str(F[u'blk_tcp_drop']) + u" 词)又添一句(" + str(F[u'blk_tcp_insert'])
        + u" 词), 逐字重印读不通(" + str(F[u'blk_tcp_verbatim_sub']) + u"); "
        u"⇎ 9112 一句定值也不给(" + str(F[u'numval_n'][2]) + u" 项带单位数值, 全库最少), 只把“服务器通常有某个值”写成陈述句; "
        u"⇎ 9113 把刀交给服务器(“permitted to terminate idle connections”), 同时要求主动关闭先发 GOAWAY; "
        u"⇎ 9000 不给定值给算法(取两端宣告值的最小, 且“at least three times the current Probe Timeout”, “three times” "
        + str(F[u'numw'][4][4]) + u" 枚), 并首次把 max_idle_timeout 写成可协商参数(“idle timeout” 复合术语 "
        + str(F[u'idle_compound'][4]) + u" 枚为一家所有)。 三线同时换代: 术语 keep-alive(" + u'⇎'.join(
            str(x) for x in F[u'ka_hyphen']) + u")→idle(" + u'⇎'.join(str(x) for x in F[u'idle_term'])
        + u")⇎ 义务词是否编号(" + u'⇎'.join(str(x) for x in F[u'tag_sh']) + u")⇎ 套版长行池里牵进 1122 的每一对除与 9293 共的 "
        + str(F[u'pool_old_shared']) + u" 枚 TCP 正文行外全为零, 而恰好新式四份共用的有 " + str(F[u'pool_new_four'])
        + u" 枚(" + str(F[u'pool_all_five']) + u" 枚为五份共用)。\n")
tags = (u'五答: 1122 词写两小时默认关(%d 词跨 %d 行) ⇎ 9293 同句加两枚编号(%d 词跨 %d 行, 多 %d 字符) ⇎ '
        u'9112 不定值(%d 词跨 %d 行, 带单位数值 %d 项) ⇎ 9113 交给服务器(%d 词跨 %d 行) ⇎ 9000 最小值+3×PTO(%d 词跨 %d 行) '
        u'四档口径: 行 %d ⇎ 折 %d ⇎ 摘壳 %d ⇎ 去编号 %d 枚命中, 换行切开 %d ⇎ 壳切 %d ⇎ 编号切 %d '
        u'切开针两半合计 %d 字符, 整串在首行读不通(反向 %d)⇎ 两半 %d/%d; 义务词跨行 %d 对全为 %s '
        u'反向 %d 枚针 %d 次探针全冷, 子串轨多读 %d 枚 '
        u'节窗 %s ⇎ %s 行 ⇎ 占比 %s%% ⇎ 节内义务词 %s '
        u'套版长行池并集 %d 枚, 两两 %d ⇎ 三三 %d ⇎ 四四 %d ⇎ 1122 只共 %d 枚, 容斥 %d '
        u'关键词模板段四份有(1122 首行 -1): 共头 %d..%d 词 ⇎ 整段相同 %d 对 ⇎ 逐行序列也相同 %d 对 ⇎ 换行不同 %d 对 '
        u'9293 相对 1122: 句 %d⇎%d ⇎ 逐字同 %d ⇎ 去编号同 %d ⇎ 归拼同 %d ⇎ 新句 %d(升格 %d) ⇎ 相同词段 %d 词/%d 段 '
        u'闭合账 布尔门 %d ⇎ 恒等式 %d ⇎ 对账 %d 键符 %d 不符 ⇎ 锚 %d 处去重 %d '
        u'谱系 %s 跨 %d 年'
        % (F[u'ans_words'][0], F[u'ans_sent_span'][0], F[u'ans_words'][1], F[u'ans_sent_span'][1], F[u'ans_tagdiff'],
           F[u'ans_words'][2], F[u'ans_sent_span'][2], F[u'numval_n'][2],
           F[u'ans_words'][3], F[u'ans_sent_span'][3], F[u'ans_words'][4], F[u'ans_sent_span'][4],
           F[u'face_tot'][0], F[u'face_tot'][1], F[u'face_tot'][2], F[u'face_tot'][3],
           F[u'split_wrap_n'], sum(F[u'role_shell_n']), F[u'split_tagcut_n'],
           F[u'split_rows_tot'], F[u'split_full_on_head'], F[u'split_half_ok'], F[u'split_n'],
           F[u'tone_straddle_n'], u'⇎'.join(F[u'tone_straddle_nd']),
           F[u'neg_n'], F[u'neg_probes'], F[u'neg_sub_false'],
           u'⇎'.join(F[u'sec_no']), u'⇎'.join(str(x) for x in F[u'sec_lines']),
           u'⇎'.join(str(x) for x in F[u'sec_span_pct']), u'⇎'.join(str(x) for x in F[u'sec_tone_tot']),
           F[u'pool_union'], F[u'pool_pair_tot'], F[u'pool_trip_tot'], F[u'pool_quad_tot'],
           F[u'pool_old_shared'], F[u'pool_ie_close'],
           F[u'kw_head_min'], F[u'kw_head_max'], F[u'kw_same_n'], F[u'kw_same_raw_n'], F[u'kw_wrap_diff'],
           F[u'ovl_s1'], F[u'ovl_s2'], F[u'ovl_same_raw'], F[u'ovl_same_tag'], F[u'ovl_same_canon'],
           F[u'ovl_new'], F[u'ovl_disc_promoted'], F[u'blk_tcp_equal'], F[u'blk_tcp_equal_runs'],
           F[u'bool_all_n'], F[u'zid_scan_n'] + F[u'zid_scan2_n'], F[u'pick_agree'], F[u'pick_diff'], USED, DIST,
           u'⇎'.join(str(y) for y in F[u'years']), max(F[u'years']) - min(F[u'years'])))
title = (u'# B82 一条空闲连接多久该关掉，五份一手文书五种答法：'
         u'1122 把定值写成词（“two hours” %d 枚 ⇎ 数字写 %d 枚）并默认关 ⇎ '
         u'9293 复述同一句但缀上 %d 枚编号（答句内 %d 枚，多 %d 字符） ⇎ '
         u'9112 带单位数值仅 %d 项，对这个超时“不提任何要求” ⇎ '
         u'9113 不说多久，只说服务器“可以”关掉空闲连接（“idle” %d 枚） ⇎ '
         u'9000 不给定值给算法：两端最小值 ⇎ 不少于三倍 PTO（“three times” %d 枚 ⇎ “idle timeout” 复合术语 %d 枚）'
         u'（术语换代 keep-alive %s ⇎ idle %s ⇎ 编号族 %s 枚只在 9293；'
         u'套版长行 1122 只与 9293 共 %d 枚 ⇎ 新式四份共用 %d 枚 ⇎ 五份共用 %d 枚）\n') % (
             F[u'num_word_two'][0], F[u'num_digit_two_tot'], F[u'tag_sh'][1], F[u'ans_tag_n_in_sent'][1],
             F[u'ans_tagdiff'], F[u'numval_n'][2], F[u'idle_term'][3], F[u'numw'][4][4], F[u'idle_compound'][4],
             u'⇎'.join(str(x) for x in F[u'ka_hyphen']), u'⇎'.join(str(x) for x in F[u'idle_term']),
             u'⇎'.join(str(x) for x in F[u'tag_sh']), F[u'pool_old_shared'], F[u'pool_new_four'],
             F[u'pool_all_five'])
text = (title + srcline + link + tags +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n'
        + u'## ⟪BabelTele⟫\n' + body + u'\n\n'
        + u'## ⛓解读注\n\n（此段由 corpus/_fill82.py 从 corpus/_b82checks.json 与 corpus/_deriv82.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s ｜ 归属错配 %d ⇎ 非锚面线 %d ｜ 多行可读针 %d' % (
    USED, DIST, TAGN, len(ERR), len(MISSLINE), len(AMB)))
for x in AMB[:20]:
    print(u'  针多解: %s 针=%s 首行=%d 候选=%d' % (x[0], x[1], x[2], x[3]))
print(u'一源 %d ⇎ 二至四源 %d ⇎ 五源 %d ｜ 段 %d 行合计 %d ⇎ 主答句 %d 行 %d 词 ⇎ 单行段 %d ｜ 段行 %d/%d(整 %d ⇎ 切 %d)' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all5'], len(PINS), F['blk_rows_tot'],
    F['blk_five_rows'], F['blk_five_words'], F['blk_one_line_n'],
    F['seg_rt_ok'], F['seg_rt_n'], F['seg_rt_whole'], F['seg_rt_cut']))
print(u'切开 %d 枚(换行 %d ⇎ 编号 %d) 两半 %d 字符 ⇎ 反向首行命中 %d ⇎ 两半 %d/%d ⇎ 义务词跨行 %d 对' % (
    F['split_n'] + F['split_tagcut_n'], F['split_wrap_n'], F['split_tagcut_n'], F['split_rows_tot'],
    F['split_full_on_head'], F['split_half_ok'], F['split_n'], F['tone_straddle_n']))
print(u'池 各份 %s 并集 %d ⇎ 两两 %s ⇎ 三三 %d ⇎ 四四 %d ⇎ 容斥 %d ｜ TCP 对照 删 %d 插 %d 同 %d 段 %d' % (
    F['pool_n'], F['pool_union'], F['pool_pair'], F['pool_trip_tot'], F['pool_quad_tot'], F['pool_ie_close'],
    F['blk_tcp_drop'], F['blk_tcp_insert'], F['blk_tcp_equal'], F['blk_tcp_equal_runs']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ⇎ 恒等式 %d ⇎ 扁平键 %d' % (
    len(DERIV), sum(len(v) for v in SEENX.values()), len(COLL), len(ZERO), len(ZV), len(F)))
print(u'判定 %s' % (dict((k, v) for k, v in CLOSE2.items() if v == 0),))
# --- 段三 END ---
