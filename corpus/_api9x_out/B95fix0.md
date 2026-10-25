```python
# 替换 corpus/_mkB95.py 中 shell_shape/is_shell_pick 定义段与 "1. 壳账" 段(从 def is_shell_pick 到 assert F['shell_pred_diff'] ... 那一行)
def is_shell_pick(x, i):
    """唯一壳判据(RFC 世代): 整行序列正则, 逐字符重扫版 sh_* 只作为它的逐行复算。"""
    if i <= 2:
        return (re.search(u'\\[Page \\d+\\]', x) is not None
                or re.match(u'^RFC \\d{4} +\\S', x) is not None
                or re.match(u'^Internet Engineering Task Force\\s*$', x) is not None
                or (len(x) == 1 and ord(x[0]) == 12) or x.strip() == u'')
    if i == 3:
        return (re.match(u'^\\s*pg\\. \\d+\\s*$', x) is not None
                or (len(x) == 1 and ord(x[0]) == 12) or x.strip() == u'')
    return False


def sh_blank(x):
    return x.strip() == u''


def sh_ff(x):
    return x == u'\x0c'


def sh_foot(x):
    """逐字符复算 '[Page ' + 数字 + ']'(口径以 is_shell_pick 的正则为准)。"""
    k, n = 0, len(x)
    while True:
        k = x.find(u'[Page ', k)
        if k < 0:
            return False
        j, d0 = k + 6, k + 6
        while j < n and x[j].isdigit():
            j += 1
        if j > d0 and j < n and x[j] == u']':
            return True
        k += 1


def sh_hdr_rfc(x):
    """逐字符复算 'RFC ' + 恰四数字 + 空格串 + 非空白。"""
    if x[:4] != u'RFC ':
        return False
    j, d0 = 4, 4
    while j < len(x) and x[j].isdigit():
        j += 1
    if j - d0 != 4:
        return False
    sp = j
    while j < len(x) and x[j] == u' ':
        j += 1
    return j > sp and j < len(x) and not x[j].isspace()


def sh_ietf(x):
    pre = u'Internet Engineering Task Force'
    return x[:len(pre)] == pre and x[len(pre):].strip() == u''


def sh_pg(x):
    k = 0
    while k < len(x) and x[k].isspace():
        k += 1
    if x[k:k + 4] != u'pg. ':
        return False
    j, d0 = k + 4, k + 4
    while j < len(x) and x[j].isdigit():
        j += 1
    return j > d0 and x[j:].strip() == u''


SHPRED = [sh_blank, sh_ff, sh_foot, sh_hdr_rfc, sh_ietf, sh_pg]


def selpred(i):
    if i == 4:
        return []
    if i == 3:
        return [SHPRED[0], SHPRED[1], SHPRED[5]]
    return SHPRED[0:5]


def shell_shape(x, i):
    """壳行判据的唯一出处: 直接取 is_shell_pick(整行序列正则)。
       逐字符形谓词 selpred(i) 不再决定壳行, 只用于下面 shape_hits/shape_ovl 的复算对账。"""
    return is_shell_pick(x, i)


def sent_cuts(face):
    n, out, start, k = len(face), [], 0, 0
    while k < n:
        if face[k] in u'.!?' and (k + 1 >= n or face[k + 1] == u' '):
            j = k + 1
            while j < n and face[j] == u' ':
                j += 1
            out.append((start, k + 1))
            start = j
            k = j
            continue
        k += 1
    if start < n:
        out.append((start, n))
    return [(a, b) for a, b in out if face[a:b].strip() != u'']


def sents_re(txt):
    return [pnorm(z) for z in re.split(u'(?<=[.!?]) +', pnorm(txt)) if z]


def sents_char(txt):
    face = pnorm(txt)
    return [face[a:b] for a, b in sent_cuts(face)]


# 全篇折平面(含壳行): 面偏移→原行 由累积长度表 + bisect 现映
CUM = []
FACC = []
OFFS = []
for i in range(NSRC):
    acc, a = [], 0
    for x in L[i]:
        a += len(x) + 1
        acc.append(a)
    CUM.append(acc)
    seg, offs, pos = [], [], 0
    for k, x in enumerate(L[i]):
        c = pnorm(x)
        if not c:
            continue
        offs.append((pos, pos + len(c), k))
        seg.append(c)
        pos += len(c) + 1
    FACC.append(u' '.join(seg))
    OFFS.append(offs)
import bisect as _bs


def off_line(i, s0):
    o = OFFS[i]
    if not o or s0 < o[0][0]:
        return -1
    lo, hi = 0, len(o) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if o[mid][0] <= s0:
            lo = mid
        else:
            hi = mid - 1
    return o[lo][2]


def find_line_b(i, nd, minrow=0):
    q = pnorm(nd)
    o = OFFS[i]
    if minrow > 0:
        if not o:
            return -1
        lo = _bs.bisect_left([z[2] for z in o], minrow)
        smin = o[lo][0] if lo < len(o) else len(FACC[i]) + 1
    else:
        smin = 0
    s0 = FACC[i].find(q, smin)
    return -1 if s0 < 0 else off_line(i, s0)


def cum_line_raw(i, off):
    return _bs.bisect_right(CUM[i], off)


# ---------- 0. 面量 ⇎ 行式对账 ----------
F['bytes'] = [len(B[i]) for i in range(NSRC)]
F['bytes_stat'] = [os.path.getsize(p) for p in PATH]
F['cp'] = [sum(1 for _ in T[i]) for i in range(NSRC)]
F['chars'] = list(F['cp'])
F['n_lf'] = [len([m.start() for m in re.finditer(u'\\n', T[i])]) for i in range(NSRC)]
F['n_cr'] = [len([m.start() for m in re.finditer(u'\\r', T[i])]) for i in range(NSRC)]
F['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
F['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
F['readlines'] = [sum(1 for _ in io.StringIO(T[i])) for i in range(NSRC)]
BDSET = u'\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029\r'
F['other_names'] = [c for c in BDSET if c != u'\r']
_ob = []
for i in range(NSRC):
    cnt = dict((c, 0) for c in F['other_names'])
    for ch in T[i]:
        if ch in cnt:
            cnt[ch] += 1
    _ob.append([cnt[c] for c in F['other_names']])
F['other_bounds'] = _ob
F['ff'] = [sum(1 for ch in T[i] if ch == u'\x0c') for i in range(NSRC)]
F['trail_bound'] = [1 if T[i][-1:] in (NL + BDSET) else 0 for i in range(NSRC)]
F['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
F['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
F['maxlen_scan'] = []
for i in range(NSRC):
    _m, _c = 0, 0
    for ch in T[i]:
        if ch == NL:
            _m = _c if _c > _m else _m
            _c = 0
        elif ch != u'\r':
            _c += 1
    _m = _c if _c > _m else _m
    F['maxlen_scan'].append(_m)
F['tab'] = [sum(1 for ch in T[i] if ch == u'\t') for i in range(NSRC)]
F['bom'] = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
NAOFF = [[m.start() for m in re.finditer(u'[^\\x00-\\x7f]', T[i])] for i in range(NSRC)]
F['na_total'] = [len(NAOFF[i]) for i in range(NSRC)]
F['na_codepoints'] = [sorted(set(ord(T[i][k]) for k in NAOFF[i])) for i in range(NSRC)]
F['rows_ledger'] = [F['splitlines'][i] - F['splitnl'][i] for i in range(NSRC)]
F['rows_pred'] = [sum(_ob[i]) - F['trail_bound'][i] for i in range(NSRC)]
F['rows_ledger_diff'] = [F['rows_ledger'][i] - F['rows_pred'][i] for i in range(NSRC)]
F['byte_cp_ledger'] = [F['bytes'][i] - F['cp'][i] for i in range(NSRC)]
F['utf8_extra'] = [sum(len(ch.encode('utf-8')) - 1 for ch in T[i] if ord(ch) > 127)
                   for i in range(NSRC)]
F['line_split_ledger'] = [F['nonblank'][i] + F['blank'][i] - F['splitnl'][i] for i in range(NSRC)]
F['bytes_vs_stat'] = 0 if F['bytes'] == F['bytes_stat'] else 1
print(u'0 面量: bytes', F['bytes'], u' cp', F['cp'], u' 行式账', F['rows_ledger'], F['rows_pred'])
assert F['rows_ledger'] == F['rows_pred'], u'行式对账不平'

# ---------- 1. 壳账: 唯一判据 is_shell_pick, 逐字符形谓词只做复算 ----------
F['foot_page'] = [len([x for x in L[i] if sh_foot(x)]) for i in range(NSRC)]
F['hdr_rfc'] = [len([x for x in L[i] if sh_hdr_rfc(x)]) for i in range(NSRC)]
F['ietf_alone'] = [len([x for x in L[i] if sh_ietf(x)]) for i in range(NSRC)]
F['br_pgnum'] = [len([x for x in L[i] if sh_pg(x)]) for i in range(NSRC)]
F['ff_led'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
F['shell_pick'] = [len([1 for x in L[i] if is_shell_pick(x, i)]) for i in range(NSRC)]
# 复算: 壳行集合必须逐行等于形谓词命中集; 任何一行两路不一是硬错(不是断言二选一)
_recalc = [len([1 for x in L[i] if any(f(x) for f in selpred(i))]) for i in range(NSRC)]
F['shell_shape'] = list(_recalc)
F['shell_pred_diff'] = [len([1 for k, x in enumerate(L[i]) if is_shell_pick(x, i) != any(f(x) for f in selpred(i))])
                        for i in range(NSRC)]
F['shell_lines'] = F['shell_pick']
F['body_lines'] = [F['splitnl'][i] - F['shell_lines'][i] for i in range(NSRC)]
F['shape_hits'] = [sum([len([1 for x in L[i] if f(x)]) for f in selpred(i)]) for i in range(NSRC)]
F['shape_ovl'] = [sum([max(0, len([1 for f in selpred(i) if f(x)]) - 1) for x in L[i]])
                  for i in range(NSRC)]
F['shell_ledger'] = [F['shell_lines'][i] - (F['shape_hits'][i] - F['shape_ovl'][i]) for i in range(NSRC)]
F['page_pair_gap'] = [F['foot_page'][i] - F['hdr_rfc'][i] for i in range(NSRC)]
print(u'1 壳: [Page]', F['foot_page'], u'RFC眉', F['hdr_rfc'], u'pg.', F['br_pgnum'],
      u'壳行(唯一判据)', F['shell_lines'], u'复算形谓词', F['shell_shape'], u'逐行不一致', F['shell_pred_diff'])
assert F['shell_pred_diff'] == [0] * NSRC, u'形谓词复算与唯一壳判据逐行不同集'
assert F['shell_ledger'] == [0] * NSRC, u'壳账容斥不平'
```