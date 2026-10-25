# -*- coding: utf-8 -*-
# B71 第一遍(采集): "一张 TLS 会话恢复票据到底能活多久、零值是什么意思、一张票能不能复用",
# 交 4507(06) ⇎ 5077(08) ⇎ 8446(18) ⇎ 9001(21) 四份一手文书各答一遍。
# 采集侧口径与建条目侧(_mkB71.py)不同: 这里用 str.count(C 层非重叠) ⇎ 逐行 in ⇎ 词元流档 ⇎
# split 断言档读数字 ⇎ lstrip+fullmatch 的页壳档; 建条目侧用游标逐字符档、正则字面档、重叠口径档、
# read_after 游标读数与 itertools 配对档。两边在口径一致的键上逐量对账, 口径不同的键只报差不拉平。
# 结果 dump 到 corpus/_b71meas.json。
from __future__ import print_function
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
PATHS = [u'corpus/raw/tlsTicket/rfc4507.txt', u'corpus/raw/tlsTicket/rfc5077.txt',
         u'corpus/raw/ietf/rfc8446.txt', u'corpus/raw/tlsTicket/rfc9001.txt']
LBL = [u'4507', u'5077', u'8446', u'9001']
N = 4

T = []
L = []
B = []
FO = []
SH = []
for p in PATHS:
    b = io.open(p, 'rb').read()
    t = b.decode('utf-8', 'replace')
    B.append(b)
    T.append(t)
    L.append(t.split(u'\n'))
    FO.append(u' '.join(t.split()))


def fold(s):
    return u' '.join(s.split())


# ---- 页壳档: 一条合并 alternation + lstrip/fullmatch (建条目侧是 10 条 re.match 顺链) ----
SHELLPAT = re.compile(
    u'|'.join([
        u'\\[?P(?:a)?g?e?\\s?\\d*\\]?',
        u'RFC-?\\d+\\s+\\S.*\\s(?:[A-Z][a-z]+ \\d{4}|\\d{4})',
        u'\\S.*\\s(?:Standards Track|Experimental|Informational|Historic)\\s+\\[?P?a?g?e?\\s?\\d*\\]?',
        u'Network Working Group\\s+\\S.*',
        u'(?:Request for Comments:|Obsoletes:|Updates:|Category:|ISSN:|Internet-Draft).*']),
    re.S)


def is_shell(l):
    s = l.strip()
    if s == u'':
        return True
    if u'\x0c' in l:
        return True
    if s.isdigit() and len(s) <= 3:
        return True
    return bool(SHELLPAT.fullmatch(s))


for i in range(N):
    SH.append([x for x in L[i] if not is_shell(x)])

M = {'path': PATHS, 'LBL': LBL}
M['base'] = []
for i in range(N):
    t = T[i]
    M['base'].append({
        'bytes': len(B[i]),
        'chars': len(t),
        'lines': len(L[i]),
        'nonblank': len([x for x in L[i] if x.strip()]),
        'maxlen': max(len(x) for x in L[i]),
        'ff': t.count(u'\x0c'),
        'ff_exact': len([x for x in L[i] if x == u'\x0c']),
        'cr': t.count(u'\r'),
        'nul': t.count(u'\x00'),
        'bom': 1 if B[i][:3] == b'\xef\xbb\xbf' else 0,
        'nonascii': len([c for c in t if ord(c) > 127]),
        'digits': len([c for c in t if c.isdigit()]),
        'dblspace': len(re.findall(u'(?=  )', t)),
        'shell_n': len(SH[i]),
        'shell_strip': len(L[i]) - len(SH[i]),
    })

# ---- 义务词词元流档: 相邻词元组, 不看正则 lookaround ----
STREAM = []
for i in range(N):
    STREAM.append(re.findall(u'[A-Za-z]+', T[i]))


def tok_count(ts, phrase):
    p = phrase.split()
    if len(p) == 1:
        return len([x for x in ts if x == p[0]])
    return len([k for k in range(len(ts) - len(p) + 1) if ts[k:k + len(p)] == p])


M['obligations'] = []
for i in range(N):
    ts = STREAM[i]
    o = {}
    for w in (u'MUST', u'MAY', u'SHOULD', u'REQUIRED'):
        o[w] = tok_count(ts, w)
    for w in (u'MUST NOT', u'MAY NOT', u'SHOULD NOT'):
        o[w] = tok_count(ts, w)
    for w in (u'must', u'may', u'should'):
        o[w] = tok_count(ts, w)
    for w in (u'must not', u'may not', u'should not'):
        o[w] = tok_count(ts, w)
    o['MUST_bare'] = o[u'MUST'] - o[u'MUST NOT']
    o['ci_must'] = len([x for x in ts if x.upper() == u'MUST'])
    o['ci_may'] = len([x for x in ts if x.upper() == u'MAY'])
    o['ci_should'] = len([x for x in ts if x.upper() == u'SHOULD'])
    o['opt'] = tok_count(ts, u'optional')
    M['obligations'].append(o)

# ---- 字面针: 逐行 in ⇎ 原面 count ⇎ 折平 count ⇎ 摘壳折平 count ----
NEEDLE = [
    (0, u'z4507_zero_reserved', u'A value of zero is reserved to indicate that the lifetime of the ticket'),
    (0, u'z4507_unspec_end', u'is unspecified.'),
    (0, u'z4507_should_delete', u'A client SHOULD delete the ticket and associated state when the time expires'),
    (0, u'z4507_or_longer', u'A server MAY treat a ticket as valid for a shorter or longer period of time than what is stated in the ticket_lifetime_hint'),
    (0, u'z4507_no_relative', u'relative to when the ticket is received'),
    (0, u'z4507_24hour', u'The ticket lifetime may be longer than the 24-hour lifetime recommended in [RFC2246]'),
    (0, u'z4507_may_be_unspec', u'Since the lifetime of a ticket may be unspecified'),
    (0, u'z4507_hint_def', u'ticket_lifetime_hint field contains a hint from the server about how long the ticket should be stored'),
    (1, u'z5077_zero_reserved', u'A value of zero is reserved to indicate that the lifetime of the ticket is unspecified.'),
    (1, u'z5077_relative', u'in seconds as a 32-bit unsigned integer in network byte order relative to when the ticket is received'),
    (1, u'z5077_should_delete', u'A client SHOULD delete the ticket and associated state when the time expires'),
    (1, u'z5077_or_longer', u'A server MAY treat a ticket as valid for a shorter or longer period of time than what is stated in the ticket_lifetime_hint'),
    (1, u'z5077_24hour', u'The ticket lifetime may be longer than the 24-hour lifetime recommended in [RFC4346]'),
    (1, u'z5077_hint_def', u'ticket_lifetime_hint field contains a hint from the server about how long the ticket should be stored'),
    (2, u'z8446_cap', u'Servers MUST NOT use any value greater than 604800 seconds (7 days)'),
    (2, u'z8446_zero_discard', u'The value of zero indicates that the ticket should be discarded immediately'),
    (2, u'z8446_cache7', u'Clients MUST NOT cache tickets for longer than 7 days, regardless of the ticket_lifetime'),
    (2, u'z8446_shorter_only', u'A server MAY treat a ticket as valid for a shorter period of time than what is stated in the ticket_lifetime'),
    (2, u'z8446_lifetime_from', u'Indicates the lifetime in seconds as a 32-bit unsigned integer in network byte order from the time of ticket issuance'),
    (2, u'z8446_must_not_attempt', u'Clients MUST NOT attempt to use tickets which have ages greater than the "ticket_lifetime" value'),
    (2, u'z8446_week', u'Because ticket lifetimes are restricted to a week, 32 bits is enough to represent any plausible age, even in milliseconds'),
    (2, u'z8446_reuse', u'Clients SHOULD NOT reuse a ticket for multiple connections'),
    (2, u'z8446_mod232', u'modulo 2^32'),
    (3, u'z9001_seven_days', u'[TLS13] sets a limit of seven days on the time between the original connection and any attempt to use 0-RTT'),
    (3, u'z9001_reuse', u'Clients SHOULD NOT reuse tickets as that allows entities other than the server to correlate connections'),
    (3, u'z9001_cap_ref', u'sets a limit of seven days'),
    (3, u'z9001_zero', u'A value of zero'),
    (3, u'z9001_lifetime_word', u'lifetime'),
]
REG = []
for (o, k, nd) in NEEDLE:
    fl = fold(nd)
    REG.append({
        'o': o, 'k': k,
        'line': len([x for x in L[o] if nd in x]),
        'own_fold': FO[o].count(fl),
        'own_sh': fold(u'\n'.join(SH[o])).count(fl),
        'x_fold': [FO[i].count(fl) for i in range(N)],
        'x_sh': [fold(u'\n'.join(SH[i])).count(fl) for i in range(N)],
    })

# ---- 长行共现: 归一 + 逐行集合, 嵌套循环配对 (建条目侧走 itertools.combinations) ----
def pn(s):
    return u' '.join(s.lower().split())


sets = [set(pn(x) for x in SH[i] if len(pn(x)) >= 40) for i in range(N)]
pres = {}
for i, s in enumerate(sets):
    for a in s:
        pres.setdefault(a, []).append(i)
PR = {}
for a, v in pres.items():
    if len(v) >= 2:
        for x in range(len(v)):
            for y in range(x + 1, len(v)):
                PR[(v[x], v[y])] = PR.get((v[x], v[y]), 0) + 1
M['pool_n'] = len(pres)
M['pool_tier'] = [len([a for a, v in pres.items() if len(v) == n]) for n in range(1, N + 1)]
M['pairs'] = {u'%s·%s' % (LBL[a], LBL[b]): c for (a, b), c in sorted(PR.items())}
RAWSH = [dict((pn(x), set()) for x in SH[i]) for i in range(N)]
for i in range(N):
    for x in SH[i]:
        RAWSH[i][pn(x)].add(x)
M['pair_byte'] = {}
for (a, b), c in sorted(PR.items()):
    M['pair_byte'][u'%s·%s' % (LBL[a], LBL[b])] = len(
        [s for s in sets[a] & sets[b] if RAWSH[a][s] & RAWSH[b][s]])

# ---- 同段逐字账: 4507 ⇎ 5077 的 hint 段 ⇎ 8446 的改名段, 词元集换一套切法 ----
def para(i, lo, hi):
    return fold(u'\n'.join(L[i][lo - 1:hi]))


M['paras'] = {'4507_389_403': para(0, 389, 403), '5077_438_443': para(1, 438, 443),
              '8446_4124_4126': para(2, 4124, 4126)}
w45 = set(u.lower() for u in re.findall(u"[A-Za-z][A-Za-z0-9'-]*", M['paras']['4507_389_403']))
w50 = set(u.lower() for u in re.findall(u"[A-Za-z][A-Za-z0-9'-]*", M['paras']['5077_438_443']))
w84 = set(u.lower() for u in re.findall(u"[A-Za-z][A-Za-z0-9'-]*", M['paras']['8446_4124_4126']))
M['para_words'] = {'n45': len(w45), 'n50': len(w50), 'n84': len(w84),
                   'x4550': len(w45 & w50), 'o45': len(w45 - w50), 'o50': len(w50 - w45),
                   'x4584': len(w45 & w84), 'o84': len(w84 - w45)}

# ---- 数字读数: 用 split 断言而非 read_after 游标 ----
CAP = FO[2].split(u'value greater than ')[1].split()
D24 = FO[0].split(u'longer than the ')[1].split()
MOD = FO[2].split(u'modulo 2^')[0].split()
M['numbers'] = {'cap_secs': int(CAP[0].strip(u'(),.')), 'cap_days': int(CAP[2].strip(u'(),.')),
                 'd24_hours': int(D24[0].split(u'-')[0]), 'mod_exp': 32}
M['numbers']['ratio'] = M['numbers']['cap_secs'] // (M['numbers']['d24_hours'] * 3600)
M['numbers']['remainder'] = M['numbers']['cap_secs'] % (M['numbers']['d24_hours'] * 3600)

# ---- 头部字段 ⇎ 标题页年份: 行界切, 不用 hdr_ids 的 (?m) 正则 ----
M['hdrs'] = []
MON = u'January|February|March|April|May|June|July|August|September|October|November|December'
for i in range(N):
    hd = {}
    for fld in (u'Obsoletes', u'Updates', u'Category'):
        hits = [x for x in L[i] if x.lower().startswith(fld.lower() + u':')]
        hd[fld] = sorted(set(int(x) for x in re.findall(u'\\d{3,5}', u' '.join(hits))))
    ys = []
    for x in L[i][:60]:
        m = re.search(u'(?:%s) +(\\d{4})\\s*$' % MON, x) or re.search(u'\\s(\\d{4})\\s*$', x)
        if m:
            ys.append(int(m.group(1)))
    hd['years'] = ys[:4]
    hd['page_year'] = ys[0] if ys else None
    M['hdrs'].append(hd)

# ---- 引用三式: 连写档 ⇎ 空格档 ⇎ 短横档 ----
CIT = {}
for nm in (u'4507', u'5077', u'8446', u'9001', u'2246', u'4346', u'5246', u'6066', u'5705', u'6961'):
    CIT[nm] = [T[i].count(u'RFC' + nm) for i in range(N)]
    CIT[nm + u'_sp'] = [len(re.findall(u'RFC ' + nm, T[i])) for i in range(N)]
M['cites'] = CIT

io.open(u'corpus/_b71meas.json', u'wb').write(
    json.dumps(M, ensure_ascii=False, indent=1).encode('utf-8'))

# ---- 与建条目侧的扁平读数逐量对账 ----
FLAT = json.load(io.open(u'corpus/_b71flat.json', encoding='utf-8'))
PAIRK = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
AGREE = []
for key, got, want in [
        (u'bytes', [r['bytes'] for r in M['base']], FLAT[u'bytes']),
        (u'chars', [r['chars'] for r in M['base']], FLAT[u'chars']),
        (u'lines', [r['lines'] for r in M['base']], FLAT[u'lines']),
        (u'nonblank', [r['nonblank'] for r in M['base']], FLAT[u'nonblank']),
        (u'maxlen', [r['maxlen'] for r in M['base']], FLAT[u'maxlen']),
        (u'ff', [r['ff'] for r in M['base']], FLAT[u'ff']),
        (u'cr', [r['cr'] for r in M['base']], FLAT[u'cr']),
        (u'nonascii', [r['nonascii'] for r in M['base']], FLAT[u'nonascii']),
        (u'bom', [r['bom'] for r in M['base']], FLAT[u'bom']),
        (u'digit_chars', [r['digits'] for r in M['base']], FLAT[u'digit_chars']),
        (u'dblspace', [r['dblspace'] for r in M['base']], FLAT[u'dblspace']),
        (u'up_must_all', [o[u'MUST'] for o in M['obligations']], FLAT[u'up_must_all']),
        (u'must_bare', [o[u'MUST_bare'] for o in M['obligations']], FLAT[u'must_bare']),
        (u'must_not', [o[u'MUST NOT'] for o in M['obligations']], FLAT[u'must_not']),
        (u'up_may', [o[u'MAY'] for o in M['obligations']], FLAT[u'up_may']),
        (u'up_should', [o[u'SHOULD'] for o in M['obligations']], FLAT[u'up_should']),
        (u'should_not', [o[u'SHOULD NOT'] for o in M['obligations']], FLAT[u'should_not']),
        (u'low_must', [o[u'must'] for o in M['obligations']], FLAT[u'low_must']),
        (u'ci_must', [o[u'ci_must'] for o in M['obligations']], FLAT[u'ci_must']),
        (u'ci_may', [o[u'ci_may'] for o in M['obligations']], FLAT[u'ci_may']),
        (u'ci_should', [o[u'ci_should'] for o in M['obligations']], FLAT[u'ci_should']),
        (u'years', [h[u'years'][0] for h in M['hdrs']], FLAT[u'years']),
        (u'pool_tier', M['pool_tier'], FLAT[u'pool_tier']),
        (u'pool_n', M['pool_n'], FLAT[u'pool_n']),
        (u'pair_share', [PR.get(k, 0) for k in PAIRK], FLAT[u'pair_share']),
        (u'pair_byte', [M['pair_byte'][u'%s·%s' % (LBL[a], LBL[b])] for a, b in PAIRK],
         FLAT[u'pair_byte']),
        (u'cap_secs', M['numbers'][u'cap_secs'], FLAT[u'num_cap_faces'][2]),
        (u'cap_days', M['numbers'][u'cap_days'], FLAT[u'num_cap_days'][2]),
        (u'd24_hours', M['numbers'][u'd24_hours'], FLAT[u'num_d24']),
        (u'ratio', M['numbers'][u'ratio'], FLAT[u'num_cap_ratio']),
        (u'day_seconds', M['numbers'][u'd24_hours'] * 3600, FLAT[u'num_day_seconds']),
        (u'remainder', M['numbers'][u'remainder'], FLAT[u'num_cap_remainder'])]:
    AGREE.append((key, got, want, u'OK' if got == want else u'DIFF'))
NEED_AGREE = []
for e in REG:
    k = u'n_' + e['k']
    if k in FLAT:
        NEED_AGREE.append((e['k'], e['own_fold'], FLAT[k][e['o']],
                           u'OK' if e['own_fold'] == FLAT[k][e['o']] else u'DIFF'))
SHELL_AGREE = [(u'shell_n', [r['shell_n'] for r in M['base']], FLAT[u'shell_n']),
               (u'shell_strip', [r['shell_strip'] for r in M['base']], FLAT[u'shell_strip'])]

print(u'== 采集 ⇎ 建条目 对账 ==')
for row in AGREE:
    if row[3] != u'OK':
        print(u'DIFF %-14s pick=%s flat=%s' % (row[0], row[1], row[2]))
print(u'对账键 %d 枚, 相符 %d 枚' % (len(AGREE), len([r for r in AGREE if r[3] == u'OK'])))
print(u'针面 %d 枚, 相符 %d 枚, 不符 %s' % (
    len(NEED_AGREE), len([r for r in NEED_AGREE if r[3] == u'OK']),
    [r[0] for r in NEED_AGREE if r[3] != u'OK']))
for nm, got, want in SHELL_AGREE:
    print(u'%s pick=%s flat=%s' % (nm, got, want))
print(u'摘壳后长行池 pick=%d flat=%s' % (M['pool_n'], FLAT[u'pool_n']))
print(u'词元组: n45=%d n50=%d x4550=%d o45=%d o50=%d | n84=%d x4584=%d o84=%d' % (
    M['para_words'][u'n45'], M['para_words'][u'n50'], M['para_words'][u'x4550'],
    M['para_words'][u'o45'], M['para_words'][u'o50'], M['para_words'][u'n84'],
    M['para_words'][u'x4584'], M['para_words'][u'o84']))
print(u'flat 词集: blk_words=%s w_common=%s w45_only_n=%s w50_only_n=%s' % (
    FLAT[u'blk_words'], FLAT[u'w_common'], FLAT[u'w45_only_n'], FLAT[u'w50_only_n']))
# 池差 2 枚来自页壳档口径: 采集档少剥的两行就是这两行(只动单份档, 两两交与逐字节交仍相符)
def mk_shell(l):
    # 只作差分诊断用: 建条目侧那 10 条 re.match 顺链的等价复刻
    if l.strip() == u'' or u'\x0c' in l:
        return True
    for r in (u'^\\s*\\[?Page \\d+\\]?\\s*$', u'^\\s*\\[?P\\[?a\\]?g?e?\\s?\\d*\\]?\\s*$',
              u'^\\s*RFC-\\d+\\s.*\\s[A-Z][a-z]+ \\d{4}\\s*$',
              u'^\\s*RFC \\d+\\s+\\S.*\\s([A-Z][a-z]+ \\d{4}|\\d{4})\\s*$',
              u'^\\s*\\S.*\\s(Standards Track|Experimental|Informational|Historic)\\s+\\[?P?age? ?\\d*\\]?\\s*$',
              u'^\\s*Network Working Group\\s+\\S.*$',
              u'^\\s*(Request for Comments:|Obsoletes:|Updates:|Category:|ISSN:|Internet-Draft)'):
        if re.match(r, l):
            return True
    return False


EXTRA = []
for i in range(N):
    for x in SH[i]:
        if len(pn(x)) >= 40 and mk_shell(x):
            k = u'%s|%s' % (LBL[i], fold(x)[:60])
            if k not in EXTRA:
                EXTRA.append(k)
print(u'池差候选行(采集档判非壳, 建条目档判壳) 池差 %d 枚, 去重后列出 %d 枚:' % (
    M['pool_n'] - FLAT[u'pool_n'], len(EXTRA)))
for x in EXTRA[:6]:
    print(u'  %s' % x)
# mk 侧的 “只在 4507” 是拿整份 5077 面做对照组的, 不是拿 5077 那段; 两种对照各算一遍
print(u'only 对照: 段⇎段 o45=%d o50=%d | 段⇎整面 o45=%d o50=%d (flat %s/%s)' % (
    M['para_words'][u'o45'], M['para_words'][u'o50'],
    len(w45 - set(u.lower() for u in re.findall(u"[A-Za-z][A-Za-z0-9'-]*", FO[1]))),
    len(w50 - set(u.lower() for u in re.findall(u"[A-Za-z][A-Za-z0-9'-]*", FO[0]))),
    FLAT[u'w45_only_n'], FLAT[u'w50_only_n']))
print(u'DUMPED corpus/_b71meas.json')
