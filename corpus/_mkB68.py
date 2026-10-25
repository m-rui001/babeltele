# -*- coding: utf-8 -*-
"""B68 建条目(第二遍现算, 四源): ⟦A⟧rfc1034(1987 概念) ⇎ ⟦B⟧rfc1035(1987 实现, 与 A 同月同作者)
⇎ ⟦C⟧rfc1536(1993 常见实现错误) ⇎ ⟦D⟧rfc2181(1997 澄清)。
主轴: 一条 RR 的 TTL 上限到底是多少、谁有权截——
A 只说“This field is a 32 bit integer in units of seconds”(不碰符号也不碰数);
B 的尺寸表里 TTL 行是唯一不带数字的一行, 却写明“positive values of a signed 32 bit number”,
   同一份文档的 SOA MINIMUM 行又写作“unsigned 32 bit”, 并把 MINIMUM 定成 TTL 的下界;
C 通篇没有一个时长字面, 只说按 TTL 缓存到过期(cache leak);
D 先点名 STD 13 说得不够清楚, 再 hereby 定死 unsigned ⇎ 0..2147483647 = 2^31−1 ⇎ 只用低 31 位 ⇎ 最高位按 0 处理,
   然后声明收方“always free to place an upper bound on any TTL received”, 并把 TTL 说成 maximum 而非 mandatory。
第二遍的独立性: 采集侧(_pick68.py)用正则族与集合运算; 本遍换成游标档(find 循环逐处数)、逐字符形状档、
句内游标解析数字(2147483647⇎31⇎31⇎32 都是读出来的)、B 尺寸表逐行按“两个以上空格”分列、
bisect 档求整行交、窗口档先定位正文标题行再按行切。两遍只在定义一致处对账, 逐键比 corpus/_b68meas.json。
抓取时刻、官网现行状态、此后 1035bis 怎么改的、现网 resolver 实际把 TTL 截到多少都只在本机或站外成立, 不进门槛。"""
import io, os, re, sys, json, hashlib
from bisect import bisect_left

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
NSRC = 4
ENTRY = u'%s/babeltele/B68_dns_ttl_ceiling_four_answers.md' % C
PATH = [u'corpus/raw/dnsTTL/rfc1034.txt', u'corpus/raw/dnsTTL/rfc1035.txt',
        u'corpus/raw/dnsTTL/rfc1536.txt', u'corpus/raw/dnsTTL/rfc2181.txt']
TAGS = [u'A', u'B', u'C', u'D']
LB = dict(zip(TAGS, [u'87 只说32位', u'87 说signed', u'93 只谈缓存', u'97 定死31位']))
IDX = dict((t, i) for i, t in enumerate(TAGS))
FULL = [u'1034', u'1035', u'1536', u'2181']
MINLEN = 55

# --- SCAN BEGIN --- (corpus/_wire68.py 把这一段机械切进 audit.py::_b68_scan)
RAWB = [io.open(p, 'rb').read() for p in PATH]
TXT = [r.decode('utf-8-sig') for r in RAWB]
LST = [t.split(NL) for t in TXT]
LOW = [t.lower() for t in TXT]
FO = [u' '.join(t.split()) for t in TXT]
F = {}


def pnorm(s):
    """归一只留 a-z0-9 与 . - 三种, 空白并成一枚空格(与采集侧同定义, 本遍逐字符走)。"""
    o, sp = [], False
    for ch in s.lower():
        if ch == u'\t' or ch == u'\x0c':
            ch = u' '
        if ch.isspace():
            if o and not sp:
                o.append(u' ')
            sp = True
        elif (u'a' <= ch <= u'z') or (u'0' <= ch <= u'9') or ch in u'.-':
            o.append(ch)
            sp = False
    return u''.join(o).strip()


FAN = [pnorm(t) for t in TXT]


def four(name, f, n=NSRC):
    F[name] = [f(k) for k in range(n)]
    return F[name]


def pos(s, sub, frm=0, to=None):
    out, k = [], s.find(sub, frm)
    lim = len(s) if to is None else to
    while k >= 0 and k < lim:
        out.append(k)
        k = s.find(sub, k + 1)
    return out


def occ(s, sub):
    return len(pos(s, sub))


def isdig(c):
    return u'0' <= c <= u'9'


def is_alpha(c):
    return bool(c) and ((u'a' <= c <= u'z') or (u'A' <= c <= u'Z'))


def hdr_line(l):
    """页眉: 行首 'RFC ' + 四位数字 + 空格(游标档, 不用正则)。"""
    if not l.startswith(u'RFC '):
        return False
    d, k = u'', 4
    while k < len(l) and isdig(l[k]):
        d += l[k]
        k += 1
    return len(d) == 4 and k < len(l) and l[k] == u' '


def rule_line(l):
    s = l.strip()
    return len(s) >= 20 and all(c == u'-' for c in s)


def is_hdr(l):
    return hdr_line(l) or rule_line(l)


def foot_line(l):
    """页脚: 行尾的 “[Page n]”(署名与页号同处一行)。"""
    s = l.strip()
    k = s.find(u'[Page ')
    if k < 0 or not s.endswith(u']'):
        return False
    mid = s[k + 6:-1]
    return bool(mid) and all(isdig(x) for x in mid)


def is_foot(l):
    """采集侧同定义: 一枚词元 + 空格 + 行尾 1~2 位数字, 且 strip 后短于 40(目录行因长度或词元数被排除)。逐字符游标档。"""
    s = l.strip()
    if not s or len(s) >= 40:
        return False
    j = len(s) - 1
    d = u''
    while j >= 0 and isdig(s[j]) and len(d) < 3:
        d = s[j] + d
        j -= 1
    if not d or len(d) > 2:
        return False
    if j < 0 or not s[j].isspace():
        return False
    while j >= 0 and s[j].isspace():
        j -= 1
    if j < 0:
        return False
    while j >= 0 and not s[j].isspace():
        j -= 1
    return j < 0


def num_before(s, trail):
    """trail 之前紧挨的那串数字(逆向游标): 用于 “… bits of the 32 bit TTL field”。"""
    k = s.find(trail)
    assert k >= 0, trail
    j = k
    while j > 0 and s[j - 1] == u' ':
        j -= 1
    e = j
    while j > 0 and isdig(s[j - 1]):
        j -= 1
    assert e > j, trail
    return int(s[j:e])


def num_after(s, lead):
    """lead 之后紧挨的那串数字(正向游标): 上限/幂次/位数/示例下限都是读出来的, 一个都不手填。"""
    k = -1
    while True:
        k = s.find(lead, k + 1)
        assert k >= 0, lead
        if isdig(s[k + len(lead)]):
            break
    j = k + len(lead)
    d = u''
    while j < len(s) and isdig(s[j]):
        d += s[j]
        j += 1
    return int(d)


def cite(t, n):
    c, k = 0, 0
    while True:
        i = t.find(u'RFC', k)
        if i < 0:
            return c
        j = i + 3
        if j < len(t) and t[j] == u' ':
            j += 1
        d = u''
        while j < len(t) and isdig(t[j]) and len(d) < 5:
            d += t[j]
            j += 1
        if len(d) == 4 and d == n and not (j < len(t) and isdig(t[j])):
            c += 1
        k = i + 3


def low_word(t, w):
    """全小写且前后不接字母(大写形与复合词都不算): 逐字符词界档。"""
    c, k = 0, t.find(w)
    while k >= 0:
        a = t[k - 1] if k > 0 else u''
        b = t[k + len(w)] if k + len(w) < len(t) else u''
        if not is_alpha(a) and not is_alpha(b):
            c += 1
        k = t.find(w, k + 1)
    return c


def sh_face(i):
    """第三档面: 逐行摘掉页眉/分隔线/“[Page n]”页脚之后再折平。页壳会把一整句答题话劈到两页,
    原面读不出, 连全篇折平档也读不出——只有摘壳档能把它接回一句。"""
    keep = [l for l in LST[i] if not (is_hdr(l) or foot_line(l) or rule_line(l))]
    return u' '.join(u' '.join(keep).split())


SH = [sh_face(i) for i in range(NSRC)]


# ---- 形状 ----
four(u'bytes', lambda i: len(RAWB[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'lines', lambda i: len(LST[i]))
four(u'nonblank', lambda i: len([l for l in LST[i] if l.strip()]))
four(u'maxlen', lambda i: max(len(l) for l in LST[i]))
four(u'trail', lambda i: len([l for l in LST[i] if l != l.rstrip()]))
four(u'cr', lambda i: occ(TXT[i], u'\r'))
four(u'nonascii', lambda i: len([ch for ch in TXT[i] if ord(ch) > 127]))
four(u'bom', lambda i: 1 if RAWB[i][:3] == b'\xef\xbb\xbf' else 0)
four(u'formfeed', lambda i: occ(TXT[i], u'\x0c'))
four(u'ff_only', lambda i: len([l for l in LST[i] if l.strip() == u'\x0c']))
four(u'nonblank_asciib', lambda i: len([l for l in LST[i] if l.strip(u' \t\r')]))
four(u'nb_gap', lambda i: F[u'nonblank_asciib'][i] - F[u'nonblank'][i])
four(u'ff_blank', lambda i: len([l for l in LST[i] if (not l.strip()) and u'\x0c' in l]))
four(u'nb_ff_close', lambda i: F[u'nb_gap'][i] - F[u'ff_blank'][i])
four(u'hdr', lambda i: len([l for l in LST[i] if hdr_line(l)]))
four(u'foot', lambda i: len([l for l in LST[i] if foot_line(l)]))
four(u'pg', lambda i: occ(TXT[i], u'[Page '))
four(u'tail_ff', lambda i: 1 if TXT[i].rstrip(u'\n').endswith(u'\x0c') else 0)
four(u'foot_minus_hdr', lambda i: F[u'foot'][i] - F[u'hdr'][i])
four(u'foot_trail_gap', lambda i: F[u'foot'][i] - F[u'trail'][i])
four(u'trail_hdr_close', lambda i: F[u'trail'][i] - F[u'hdr'][i] - F[u'tail_ff'][i])
four(u'ff_model_close', lambda i: F[u'formfeed'][i] - (F[u'foot'][i] - 1 + F[u'tail_ff'][i]))
four(u'pg_foot_close', lambda i: F[u'pg'][i] - F[u'foot'][i])
four(u'rule_n', lambda i: len([l for l in LST[i] if rule_line(l)]))
four(u'rule_extra', lambda i: len([l for l in LST[i]
                                   if rule_line(l) and not hdr_line(l) and not foot_line(l)]))
four(u'shell_lines', lambda i: len([l for l in LST[i]
                                    if is_hdr(l) or foot_line(l) or rule_line(l)]))
four(u'shell_close', lambda i: F[u'shell_lines'][i] - F[u'hdr'][i] - F[u'foot'][i]
     - F[u'rule_extra'][i])
four(u'sh_len', lambda i: len(SH[i]))
four(u'shell_chars', lambda i: sum(len(l) + 1 for l in LST[i]
                                   if is_hdr(l) or foot_line(l) or rule_line(l)))
F[u'blank_lines_extra'] = sum(F[u'lines']) - sum(F[u'nonblank']) - sum(F[u'ff_only'])
F[u'sig'] = [hashlib.blake2b(r, digest_size=8).hexdigest() for r in RAWB]
F[u'sig_distinct'] = len(set(F[u'sig']))
F[u'bc_delta'] = [F[u'bytes'][i] - F[u'chars'][i] for i in range(NSRC)]
F[u'nonascii_utf8_extra'] = [sum(len(ch.encode(u'utf-8')) - 1 for ch in TXT[i] if ord(ch) > 127)
                             for i in range(NSRC)]
F[u'enc_close'] = [F[u'bc_delta'][i] - (3 * F[u'bom'][i] + F[u'nonascii_utf8_extra'][i])
                   for i in range(NSRC)]
F[u'ascii_all'] = len([1 for x in F[u'nonascii'] if x == 0])

# ---- 字面针(与采集侧同一批, 本遍用游标档重数; 原面 ⇎ 折平 两档) ----
LITK = {
    u'signed_word': u'signed', u'unsigned_word': u'unsigned',
    u'signed32': u'positive values of a signed 32 bit number',
    u'max_lit': u'2147483647', u'max_pow': u'2^31 - 1', u'hi31': u'less significant 31 bits',
    u'min0': u'minimum value of 0', u'floor_sent': u'at least the MINIMUM field of the SOA',
    u'here_86400': u'here 86400 seconds', u'one_day': u'or one day',
    u'upper_bound': u'upper bound on any TTL',
    u'not_mandatory': u'maximum time to live, not a mandatory time to live',
    u'cached_for': u'cached for TTL seconds', u'ttl_expires': u'until the TTL expires',
    u'cache_leak': u'Cache Leaks', u'refresh_kw': u'REFRESH', u'retry_kw': u'RETRY',
    u'expire_kw': u'EXPIRE', u'minimum_kw': u'MINIMUM', u'expire_week': u'expire after a week',
    u'min_day': u'minimum of a day', u'different_ttls': u'different TTLs',
    u'rrset_same': u'RRSet to have different TTLs',
    # 建条目侧另立的针(采集侧没有, 不参与对账)
    u'bare32': u'32 bit integer', u'time_limit': u'time limit on how long an RR can be',
    u'negcache': u'cache, negative results with TTLs',
    u'wrap_neg': u'between the most positive and most negative 32 bit numbers',
    u'unsg_min': u'unsigned 32 bit minimum TTL field', u'unsg32': u'unsigned 32 bit',
    u'lower_bound': u'lower bound on the TTL field',
    u'max_of': u'the maximum of the TTL field from the RR',
    u'not_load': u'not when the zone is loaded from a master file',
    u'typo_prov': u'this provison is to allow future dynamic update',
    u'typo_anis': u'an is primarily used',
    u'hereby_ttl': u'hereby specified that a TTL value is an unsigned number',
    u'std13_ttl': u'TTL field in STD 13', u'not_clear': u'not as clear as it could be',
    u'sgn_or_un': u'whether the value is signed or unsigned',
    u'sign_bit': u'most significant, or sign, bit set to zero',
    u'msb_zero': u'as if the entire value received was zero',
    u'free_bound': u'always free to place an upper bound',
    u'diff_dep': u'use of differing TTLs in an RRSet is hereby',
    u'same_ttl': u'the TTLs of all RRs in an RRSet must be the same',
    u'cachesize': u'impose a limit on the cache size', u'within_ttl': u'within a TTL period',
    u'time_live': u'time to live', u'ttl_cap': u'TTL', u'ttl_low': u'ttl',
    u'sec434': u'4.3.4', u'sec52': u'5.2. TTLs of RRs in an RRSet',
}
for k, s in sorted(LITK.items()):
    four(u'lit_' + k, lambda i, s=s: occ(TXT[i], s))
    nf = u' '.join(s.split())
    four(u'fold_' + k, lambda i, nf=nf: occ(FO[i], nf))
    four(u'delta_' + k, lambda i, k=k: F[u'fold_' + k][i] - F[u'lit_' + k][i])
NEEDLEK = [u'signed_word', u'unsigned_word', u'signed32', u'max_lit', u'max_pow', u'hi31', u'min0',
           u'floor_sent', u'here_86400', u'one_day', u'upper_bound', u'not_mandatory', u'cached_for',
           u'ttl_expires', u'cache_leak', u'refresh_kw', u'retry_kw', u'expire_kw', u'minimum_kw',
           u'expire_week', u'min_day', u'different_ttls', u'rrset_same']
F[u'fold_total_delta'] = sum(sum(F[u'delta_' + k]) for k in NEEDLEK)
F[u'wrap_lit_zero'] = len([k for k in NEEDLEK if sum(F[u'delta_' + k]) and sum(F[u'lit_' + k]) == 0])
F[u'wrap_delta_hit'] = len([k for k in NEEDLEK if sum(F[u'delta_' + k])])
F[u'wrap_close'] = F[u'wrap_delta_hit'] - F[u'wrap_lit_zero']
F[u'fold_extra_keys'] = len(LITK) - len(NEEDLEK)

# ---- signed 词的三桶(游标逐字符词界, 与“signed”⇎“unsigned”两枚针交叉验) ----
def sign_buckets(t):
    bare = un = other = 0
    k = t.find(u'signed')
    while k >= 0:
        a = t[k - 1] if k > 0 else u''
        if not is_alpha(a):
            bare += 1
        elif a == u'n':
            un += 1
        else:
            other += 1
        k = t.find(u'signed', k + 1)
    return bare, un, other


F[u'sgn_bucket'] = [list(sign_buckets(t)) for t in TXT]
four(u'sgn_bare', lambda i: F[u'sgn_bucket'][i][0])
four(u'sgn_in_un', lambda i: F[u'sgn_bucket'][i][1])
four(u'sgn_in_word', lambda i: F[u'sgn_bucket'][i][2])
four(u'sgn_bucket_close', lambda i: F[u'sgn_bare'][i] + F[u'sgn_in_un'][i] + F[u'sgn_in_word'][i]
     - F[u'lit_signed_word'][i])
four(u'unsg_scan_close', lambda i: F[u'sgn_in_un'][i] - F[u'lit_unsigned_word'][i])
four(u'row_sign', lambda i: 1 if F[u'lit_signed32'][i] else 0)
four(u'row_unsign', lambda i: 1 if occ(FO[i], u'a TTL value is an unsigned number') else 0)
four(u'row_bare', lambda i: 1 if F[u'fold_bare32'][i] else 0)
F[u'sign_docs'] = [F[u'row_sign'][i] + F[u'row_unsign'][i] for i in range(NSRC)]
F[u'sign_docs_n'] = sum(F[u'sign_docs'])
F[u'sign_ledger'] = F[u'sign_docs_n'] + (NSRC - F[u'sign_docs_n']) - NSRC

# ---- 数字: 句内游标 ⇎ 逆向游标 ⇎ 尺寸表逐行 ----
F[u'ttl_max'] = num_after(TXT[3], u'maximum value of ')
F[u'ttl_pow'] = num_after(TXT[3], u'maximum of 2^')
F[u'ttl_bits'] = num_after(TXT[3], u'less significant ')
F[u'ttl_field_bits'] = num_before(TXT[3], u' bit TTL field')
F[u'min_floor'] = num_after(TXT[0], u'SOA, here ')
F[u'max_pow_close'] = F[u'ttl_max'] - (2 ** F[u'ttl_pow'] - 1)
F[u'pow_bits_close'] = F[u'ttl_pow'] - F[u'ttl_bits']
F[u'bitloss_close'] = F[u'ttl_field_bits'] - F[u'ttl_bits'] - 1
F[u'floor_day_close'] = F[u'min_floor'] - 24 * 60 * 60


def lead_num(s):
    """行首连读数字(游标档): '63 octets or less' ⇒ 63。"""
    d = u''
    for c in s:
        if not isdig(c):
            break
        d += c
    assert d, s
    return int(d)


def size_rows(i):
    """B 的 §2.3.4 表: 正文那处标题起, 按“两个以上空格”拆成 标签 ⇎ 右项 两列。"""
    L = LST[i]
    hs = [n for n, l in enumerate(L) if l.strip() == u'2.3.4. Size limits']
    assert len(hs) <= 1, hs
    if not hs:
        return []
    a = hs[0]
    rows = []
    for l in L[a:a + 14]:
        k = l.find(u'  ')
        if k < 1:
            continue
        lab, val = l[:k].strip(), l[k:].strip()
        if len(lab.split()) > 2:
            continue
        if isdig(val[:1]) or val.startswith(u'positive '):
            rows.append((lab, val))
    return rows


SR = [size_rows(i) for i in range(NSRC)]
F[u'size_rows'] = [len(r) for r in SR]
F[u'size_b_rows'] = len(SR[1])
F[u'size_num_rows'] = len([1 for _, v in SR[1] if isdig(v[:1])])
F[u'size_sign_rows'] = len([1 for _, v in SR[1] if not isdig(v[:1])])
F[u'size_nums'] = [lead_num(v) for _, v in SR[1] if isdig(v[:1])]
F[u'size_ttl_val'] = [v for lab, v in SR[1] if lab == u'TTL'][0]
F[u'size_row_close'] = F[u'size_num_rows'] + F[u'size_sign_rows'] - F[u'size_b_rows']
F[u'size_other_rows'] = [len(r) for r in (SR[0], SR[2], SR[3])]
F[u'digit_runs'] = [len([1 for c in TXT[i] if isdig(c)]) for i in range(NSRC)]
F[u'ceil_docs_n'] = len([1 for i in range(NSRC) if F[u'lit_max_lit'][i]])

# ---- 上界 ⇎ 下界 ⇎ 不谈: 三档分账 ----
four(u'has_ceil', lambda i: 1 if (F[u'lit_upper_bound'][i] or F[u'lit_free_bound'][i]) else 0)
four(u'has_floor', lambda i: 1 if (F[u'fold_floor_sent'][i] or F[u'fold_lower_bound'][i]) else 0)
four(u'has_none', lambda i: 1 if (not F[u'has_ceil'][i] and not F[u'has_floor'][i]
                                  and not F[u'sign_docs'][i]) else 0)
F[u'ceil_floor_close'] = sum(F[u'has_ceil']) + sum(F[u'has_floor']) + sum(F[u'has_none']) - NSRC
F[u'has_ceil_n'] = sum(F[u'has_ceil'])
F[u'has_floor_n'] = sum(F[u'has_floor'])
F[u'both_ceil_floor'] = len([1 for i in range(NSRC) if F[u'has_ceil'][i] and F[u'has_floor'][i]])
F[u'notmand_docs'] = [1 if F[u'fold_not_mandatory'][i] else 0 for i in range(NSRC)]
F[u'notmand_close'] = sum(F[u'notmand_docs']) - 1
F[u'msb_close'] = sum(F[u'lit_sign_bit']) - 1

# ---- 答数句表(原面 ⇎ 折平 两档; 采集侧没有这一段) ----
SN = [
    (u'a_bare32', u'This field is a 32 bit integer in units of seconds'),
    (u'a_timelimit', u'The meaning of the TTL field is a time limit on how long an RR can be kept in a cache.'),
    (u'a_floor', u'forces the TTL of all authoritative RRs to be at least the MINIMUM field of the SOA, '
                 u'here 86400 seconds, or one day.'),
    (u'a_neg', u'name servers to distribute, and resolvers to cache, negative results with TTLs.'),
    (u'a_wrap', u'with comparisons around the boundary between the most positive and most negative 32 bit numbers.'),
    (u'b_row', u'TTL             positive values of a signed 32 bit number.'),
    (u'b_unsgmin', u'MINIMUM         The unsigned 32 bit minimum TTL field that should be exported with any RR '
                   u'from this zone.'),
    (u'b_maxof', u'the TTL field is set to the maximum of the TTL field from the RR and the MINIMUM field in the '
                 u'appropriate SOA.'),
    (u'b_lower', u'Thus MINIMUM is a lower bound on the TTL field for all RRs in a zone.'),
    (u'b_notload', u'MINIMUM should occur when the RRs are copied into the response and not when the zone is '
                   u'loaded from a master file or via a zone transfer.'),
    (u'b_typo', u'The reason for this provison is to allow future dynamic update facilities to change the SOA RR '
                u'with known semantics.'),
    (u'c_cached', u'Every resource record returned by a server is cached for TTL seconds, where the TTL value is '
                  u'returned with the RR.'),
    (u'until', u'Full-service (or stub) resolvers cache the RR and answer any queries based on this cached '
               u'information, in the future, until the TTL expires.'),
    (u'c_limit', u'They might impose a limit on the cache size or might not interpret the TTL value correctly.'),
    (u'c_within', u'queries repeated within a TTL period of a RR constitute a cache leak.'),
    (u'd_notclear', u'The definition of values appropriate to the TTL field in STD 13 is not as clear as it could '
                    u'be, with respect to how many significant bits exist, and whether the value is signed or '
                    u'unsigned.'),
    (u'd_hereby', u'It is hereby specified that a TTL value is an unsigned number, with a minimum value of 0, and '
                  u'a maximum value of 2147483647.'),
    (u'd_pow', u'That is, a maximum of 2^31 - 1.'),
    (u'd_bits', u'When transmitted, this value shall be encoded in the less significant 31 bits of the 32 bit TTL '
                u'field, with the most significant, or sign, bit set to zero.'),
    (u'd_msb', u'Implementations should treat TTL values received with the most significant bit set as if the '
               u'entire value received was zero.'),
    (u'd_free', u'Implementations are always free to place an upper bound on any TTL received, and treat any '
                u'larger values as if they were that upper bound.'),
    (u'd_notmand', u'The TTL specifies a maximum time to live, not a mandatory time to live.'),
    (u'd_diff', u'It is possible for the RRs in an RRSet to have different TTLs.'),
    (u'd_dep', u'Consequently the use of differing TTLs in an RRSet is hereby deprecated, the TTLs of all RRs in '
               u'an RRSet must be the same.'),
    (u'd_same', u'Should a client receive a response containing RRs from an RRSet with differing TTLs, it should '
                u'treat this as an error.'),
    (u'd_1034sec', u'RFC1034 section 4.3.4 refers to this technique but mentions the additional section of the '
                   u'response.'),
]
for k, s in SN:
    four(u's_' + k, lambda i, s=s: occ(TXT[i], s))
    nf = u' '.join(s.split())
    four(u's_' + k + u'_fold', lambda i, nf=nf: occ(FO[i], nf))
    four(u's_' + k + u'_sh', lambda i, nf=nf: occ(SH[i], nf))
    four(u'wrapgap_' + k, lambda i, k=k: F[u's_' + k + u'_fold'][i] - F[u's_' + k][i])
    four(u'shgap_' + k, lambda i, k=k: F[u's_' + k + u'_sh'][i] - F[u's_' + k + u'_fold'][i])
F[u'wrap_sn_n'] = len(SN)
F[u'wrap_sn_hit'] = len([1 for k, _ in SN if any(F[u'wrapgap_' + k])])
F[u'wrap_sn_total'] = sum(sum(F[u'wrapgap_' + k]) for k, _ in SN)
four(u'sn_strict_docs', lambda i: len([1 for k, _ in SN if F[u's_' + k][i]]))
four(u'sn_fold_docs', lambda i: len([1 for k, _ in SN if F[u's_' + k + u'_fold'][i]]))
four(u'sn_sh_docs', lambda i: len([1 for k, _ in SN if F[u's_' + k + u'_sh'][i]]))
F[u'sh_sn_hit'] = len([1 for k, _ in SN if any(F[u'shgap_' + k])])
F[u'sh_gap_total'] = sum(sum(F[u'shgap_' + k]) for k, _ in SN)
F[u'sn_only_sh'] = [k for k, _ in SN if any(F[u'shgap_' + k]) and sum(F[u's_' + k + u'_fold']) == 0]
F[u'sh_only_n'] = len(F[u'sn_only_sh'])
F[u'sh_ladder_bad'] = sum([max(0, F[u'sn_fold_docs'][i] - F[u'sn_sh_docs'][i])
                           + max(0, F[u'sn_strict_docs'][i] - F[u'sn_fold_docs'][i])
                           for i in range(NSRC)])
F[u'sn_face_span'] = [F[u'sn_sh_docs'][i] - F[u'sn_strict_docs'][i] for i in range(NSRC)]
F[u'sh_hit_minus_only'] = F[u'sh_sn_hit'] - F[u'sh_only_n']
F[u'sn_only_fold'] = [k for k, _ in SN if any(F[u'wrapgap_' + k]) and sum(F[u's_' + k]) == 0]
F[u'wrap_onlyfold_n'] = len(F[u'sn_only_fold'])
F[u'wrap_hit_minus_onlyfold'] = F[u'wrap_sn_hit'] - F[u'wrap_onlyfold_n']
MAIN4 = [u'a_bare32', u'b_row', u'c_cached', u'd_hereby']
four(u'main4_fold', lambda i: len([1 for k in MAIN4 if F[u's_' + k + u'_fold'][i]]))
four(u'sn_other_fold', lambda i: F[u'sn_fold_docs'][i] - F[u'main4_fold'][i])
F[u'main4_each'] = sum(F[u'main4_fold'])
F[u'main4_close'] = F[u'main4_each'] - NSRC
F[u'ceil_sn_close'] = len([1 for k in (u'd_hereby', u'd_pow', u'd_bits', u'd_msb', u'd_free', u'd_notmand')
                           if sum(F[u's_' + k + u'_sh']) != 1])
F[u'floor_sn_close'] = len([1 for k in (u'a_floor', u'b_lower', u'b_maxof')
                            if sum(F[u's_' + k + u'_sh']) != 1])
F[u'cache_sn_close'] = len([1 for k in (u'c_cached', u'until', u'c_limit', u'c_within')
                            if sum(F[u's_' + k + u'_sh']) != 1])
F[u'sn_sh_total'] = sum(sum(F[u's_' + k + u'_sh']) for k, _ in SN)

# ---- 时长字面 ⇎ SOA 示例五元组 ----
DURLIT = [u'60', u'600', u'7200', u'1800', u'300', u'86400', u'172800', u'604800', u'3600000',
          u'2147483647']
four(u'dur_set', lambda i: [occ(TXT[i], x) for x in DURLIT])
four(u'dur_distinct', lambda i: len([1 for x in DURLIT if occ(TXT[i], x)]))
F[u'dur_repeat_extra'] = sum(sum(c) for c in F[u'dur_set']) - sum(F[u'dur_distinct'])
F[u'dur_distinct_close'] = sum(F[u'dur_distinct']) - len(
    [1 for i in range(NSRC) for x in DURLIT if F[u'dur_set'][i][DURLIT.index(x)]])
F[u'dur_hit_total'] = [sum(c) for c in F[u'dur_set']]
F[u'no_dur_docs'] = len([1 for x in F[u'dur_hit_total'] if x == 0])

KW = [u'SERIAL', u'REFRESH', u'RETRY', u'EXPIRE', u'MINIMUM']


def soa_rows(i):
    """示例区五元组行: 三种写法都要吃(小写粘连 ⇎ 大写带空格 ⇎ 右括号夹在数与注释之间)。游标档逐行扫。"""
    rows = {}
    for l in LST[i]:
        k = 0
        while k < len(l) and l[k] == u' ':
            k += 1
        d = u''
        while k < len(l) and isdig(l[k]):
            d += l[k]
            k += 1
        if not d:
            continue
        while k < len(l) and l[k] == u' ':
            k += 1
        if k < len(l) and l[k] == u')':
            k += 1
        while k < len(l) and l[k] == u' ':
            k += 1
        if k >= len(l) or l[k] != u';':
            continue
        k += 1
        while k < len(l) and l[k] == u' ':
            k += 1
        for w in KW:
            if l[k:k + len(w)].upper() != w:
                continue
            nxt = l[k + len(w):k + len(w) + 1]
            if nxt and (is_alpha(nxt) or isdig(nxt)):
                continue
            rows.setdefault(w, []).append(int(d))
            break
    return dict((k, sorted(v)) for k, v in rows.items())


SOA = [soa_rows(i) for i in range(NSRC)]
four(u'soa_keys', lambda i: sorted(SOA[i].keys()))
four(u'soa_vals', lambda i: dict(SOA[i]))
four(u'soa_n_lines', lambda i: sum(len(v) for v in SOA[i].values()))
F[u'soa_AB_shared'] = len([x for x in SOA[0] if x in SOA[1]])
F[u'soa_AB_valshare'] = len([x for x in SOA[0] if x in SOA[1] and set(SOA[0][x]) & set(SOA[1][x])])
F[u'soa_val_close'] = F[u'soa_AB_valshare']
F[u'soa_AB_union'] = len(set(SOA[0]) | set(SOA[1]))
F[u'soa_AB_close'] = len(SOA[0]) + len(SOA[1]) - F[u'soa_AB_union'] - F[u'soa_AB_shared']
F[u'soa_CD_empty'] = len([1 for i in (2, 3) if not SOA[i]])
F[u'soa_min_A'] = min(SOA[0][u'MINIMUM'])
F[u'floor_soa_close'] = F[u'min_floor'] - F[u'soa_min_A']
four(u'soa_upper', lambda i: sum(TXT[i].count(u'; ' + k) for k in KW))
four(u'soa_lower', lambda i: sum(TXT[i].count(u';' + k.lower()) + TXT[i].count(u'; ' + k.lower())
                                 for k in KW))


def paren_count(t):
    """数字与注释之间夹一枚右括号: “86400) ;minimum of a day”(逆向+正向游标, 不用正则)。"""
    c, k = 0, t.find(u')')
    while k >= 0:
        j = k - 1
        while j >= 0 and t[j] == u' ':
            j -= 1
        h = k + 1
        while h < len(t) and t[h] == u' ':
            h += 1
        if j >= 0 and isdig(t[j]) and h < len(t) and t[h] == u';':
            c += 1
        k = t.find(u')', k + 1)
    return c


four(u'soa_paren', lambda i: paren_count(TXT[i]))
four(u'soa_case_delta', lambda i: F[u'soa_lower'][i] - F[u'soa_upper'][i])

# ---- 窗口: 四份各自的答题节(正文标题行→下一节标题行) ----
HEADNEED = [u'3.6. Resource Records', u'2.3.4. Size limits', u'5. Cache Leaks:',
            u'8. Time to Live (TTL)']


def is_sec_head(l):
    """节标题行: 行首为数字与点, 紧跟一枚空格, 再跟大写字母; 目录行(右侧带页号)按两空格档排除。"""
    if l != l.lstrip() or u'  ' in l.rstrip():
        return False
    t = l.rstrip()
    k = 0
    while k < len(t) and (isdig(t[k]) or t[k] == u'.'):
        k += 1
    if k == 0 or t[k:k + 1] != u' ':
        return False
    rest = t[k + 1:]
    return bool(rest) and rest[0].isupper()


def window(i):
    hs = [n for n, l in enumerate(LST[i]) if l.strip() == HEADNEED[i]]
    assert len(hs) >= 1, (i, hs)
    h = hs[-1]
    j = h + 1
    while j < len(LST[i]) and not is_sec_head(LST[i][j]):
        j += 1
    return h, j, NL.join(LST[i][h:j])


WIN = [window(i) for i in range(NSRC)]
four(u'sec_head', lambda i: LST[i][WIN[i][0]].strip())
four(u'sec_len', lambda i: len(WIN[i][2]))
four(u'sec_a', lambda i: WIN[i][0] + 1)
four(u'sec_b', lambda i: WIN[i][1])
four(u'sec_lines', lambda i: WIN[i][1] - WIN[i][0])
for _nm, _w in ((u'ttl', u'TTL'), (u'ttllow', u'ttl'), (u'cache', u'cache'), (u'cachecap', u'CACHE')):
    four(u'secw_' + _nm, lambda i, w=_w: occ(WIN[i][2], w))
    four(u'outw_' + _nm, lambda i, w=_w: occ(NL.join(LST[i][:WIN[i][0]] + LST[i][WIN[i][1]:]), w))
    four(u'win_close_' + _nm, lambda i, w=_w: F[u'secw_' + _nm][i] + F[u'outw_' + _nm][i] - occ(TXT[i], w))
four(u'secw_digit', lambda i: len([1 for ch in WIN[i][2] if isdig(ch)]))
four(u'outw_digit', lambda i: F[u'digit_runs'][i] - F[u'secw_digit'][i])
four(u'digit_win_close', lambda i: F[u'secw_digit'][i] + F[u'outw_digit'][i] - F[u'digit_runs'][i])
F[u'ttl_win_close_sum'] = sum(F[u'win_close_ttl'])
F[u'cache_win_close_sum'] = sum(F[u'win_close_cache'])
F[u'ttllow_win_close_sum'] = sum(F[u'win_close_ttllow'])
four(u'digit_density', lambda i: int(F[u'secw_digit'][i] * 1000 // max(1, F[u'sec_len'][i])))

# ---- 义务词: 大写 2119 形 ⇎ 全小写词界形 ----
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY NOT', u'MAY',
          u'REQUIRED', u'RECOMMENDED'):
    four(u'u_' + w.replace(u' ', u'_').lower(), lambda i, w=w: occ(TXT[i], w))
four(u'oblig_up', lambda i: F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i])
four(u'lo_must', lambda i: low_word(TXT[i], u'must'))
four(u'lo_should', lambda i: low_word(TXT[i], u'should'))
four(u'lo_may', lambda i: low_word(TXT[i], u'may'))
four(u'lo_shall', lambda i: low_word(TXT[i], u'shall'))
four(u'oblig_low', lambda i: F[u'lo_must'][i] + F[u'lo_should'][i] + F[u'lo_may'][i])
four(u'oblig_low_close', lambda i: F[u'lo_must'][i] + F[u'lo_should'][i] + F[u'lo_may'][i]
     - F[u'oblig_low'][i])
four(u'hereby', lambda i: low_word(TXT[i], u'hereby'))
four(u'deprecated', lambda i: occ(TXT[i], u'deprecated'))
F[u'oblig_up_close'] = sum(F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i] - F[u'oblig_up'][i]
                           for i in range(NSRC))
F[u'up_ABC_zero'] = sum(F[u'oblig_up'][:3])
F[u'up_D_n'] = F[u'oblig_up'][3]
F[u'rfc2119_ref'] = [occ(TXT[i], u'2119') for i in range(NSRC)]
F[u'hereby_D_only'] = sum(F[u'hereby'][:3])
F[u'shall_D_only'] = sum(F[u'lo_shall'][:3])

# ---- 文档身份 / 引用网 ----
HK = [(u'cat_std', u'Category: Standards Track'), (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'),
      (u'std_hdr', u'STD:'), (u'bcp_hdr', u'BCP:'), (u'issn_hdr', u'ISSN:'),
      (u'req_rc', u'Request for Comments:'), (u'ise', u'Internet Engineering Task Force'),
      (u'nwgroup', u'Network Working Group'), (u'std13', u'STD 13'), (u'brf', u'[RFC'),
      (u'self_ref', u'RFC-')]
for k, s in HK:
    four(k, lambda i, s=s: occ(TXT[i], s))
for n in (u'1034', u'1035', u'1536', u'2181', u'1123', u'1010', u'0819', u'1033'):
    four(u'cite_' + n, lambda i, n=n: cite(TXT[i], n))
F[u'cite_self'] = [cite(TXT[i], FULL[i]) for i in range(NSRC)]
F[u'selfcite_ledger'] = [F[u'cite_self'][i] - F[u'hdr'][i] for i in range(NSRC)]
F[u'selfcite_ABC'] = sum(F[u'selfcite_ledger'][:3])
F[u'std13_AB_close'] = F[u'std13'][0] + F[u'std13'][1]
F[u'dns_family'] = [F[u'cite_1034'][i] + F[u'cite_1035'][i] for i in range(NSRC)]

# ---- 整行搬运(归一 ⇎ 逐字节; 本遍用 bisect 档求交) ----
def norm_index(i):
    seen = {}
    for l in LST[i]:
        if len(l.strip()) >= MINLEN and not (is_hdr(l) or is_foot(l)):
            seen[pnorm(l)] = 1
    return sorted(seen)


def raw_index(i):
    seen = {}
    for l in LST[i]:
        if len(l.strip()) >= MINLEN:
            seen[l] = 1
    return sorted(seen)


GN = [norm_index(i) for i in range(NSRC)]
GR = [raw_index(i) for i in range(NSRC)]


def bis_iset(a, b):
    out = []
    for x in a:
        k = bisect_left(b, x)
        if k < len(b) and b[k] == x:
            out.append(x)
    return out


def n_union(*sets):
    seen = {}
    for s in sets:
        for x in s:
            seen[x] = 1
    return len(seen)


PAIR = [(a, b) for a in range(NSRC) for b in range(a + 1, NSRC)]
F[u'set_sizes'] = [len(s) for s in GN]
F[u'pair_share'] = [len(bis_iset(GN[a], GN[b])) for a, b in PAIR]
F[u'pair_byte'] = [len(bis_iset(GR[a], GR[b])) for a, b in PAIR]
F[u'pair_norm_only'] = [F[u'pair_share'][k] - F[u'pair_byte'][k] for k in range(len(PAIR))]
F[u'pair_close'] = sum(F[u'pair_share']) - sum(F[u'pair_byte']) - sum(F[u'pair_norm_only'])
F[u'pair_nonzero'] = len([1 for x in F[u'pair_share'] if x])
F[u'tri_share'] = [len(bis_iset(bis_iset(GN[a], GN[b]), GN[c]))
                   for a in range(NSRC) for b in range(a + 1, NSRC) for c in range(b + 1, NSRC)]
F[u'union_all'] = n_union(*GN)
F[u'only_each'] = [len([x for x in GN[i] if not any(x in GN[j] for j in range(NSRC) if j != i)])
                   for i in range(NSRC)]
CNT = {}
for i in range(NSRC):
    for l in LST[i]:
        if len(l.strip()) >= MINLEN and not (is_hdr(l) or is_foot(l)):
            n = pnorm(l)
            if len(n) < MINLEN:
                continue
            if n not in CNT:
                CNT[n] = set()
            CNT[n].add(i)
F[u'pool_n'] = len(CNT)
F[u'pool_tier'] = [len([1 for n in CNT if len(CNT[n]) == k]) for k in range(1, NSRC + 1)]
F[u'pool_tier_close'] = sum(F[u'pool_tier']) - F[u'pool_n']
for n in range(1, NSRC + 1):
    F[u'pool_%d' % n] = F[u'pool_tier'][n - 1]
for a in range(NSRC):
    F[u'pool_share1_' + FULL[a]] = len([n for n in CNT if CNT[n] == {a}])
F[u'pool_share2_ab'] = len([n for n in CNT if CNT[n] == {0, 1}])
F[u'pool_4'] = F[u'pool_tier'][NSRC - 1]
F[u'union_close'] = (sum(F[u'set_sizes']) - sum(F[u'pair_share']) + sum(F[u'tri_share'])
                     - F[u'pool_4'] - F[u'union_all'])
S4 = [n for n in CNT if len(CNT[n]) == NSRC]


def face_raw(i, norm):
    return [l for l in LST[i] if pnorm(l) == norm]


def raw_common(rows):
    common = set(rows[0])
    for r in rows[1:]:
        common = common & set(r)
    return common


def write_axes(rows):
    forms = []
    for r in rows:
        for l in r:
            if l not in forms:
                forms.append(l)
    if len(forms) < 2:
        return []
    if len(set(f.lower() for f in forms)) == 1:
        return [u'case']
    if len(set(f.lower().replace(u'-', u'') for f in forms)) == 1:
        return [u'hyph']
    if len(set(u' '.join(f.lower().replace(u'-', u'').split()) for f in forms)) == 1:
        return [u'space']
    return [u'multi']


S4R = [(n, [face_raw(i, n) for i in range(NSRC)]) for n in S4]
F[u'share4_byte4'] = len([1 for n, rows in S4R if raw_common(rows)])
F[u'share4_notbyte'] = len(S4R) - F[u'share4_byte4']
for _a in (u'case', u'hyph', u'space', u'multi'):
    F[u'share4_axis_' + _a] = len([1 for n, rows in S4R if write_axes(rows) == [_a]])
F[u'share4_axis_close'] = (F[u'share4_axis_case'] + F[u'share4_axis_hyph'] + F[u'share4_axis_space']
                           + F[u'share4_axis_multi'] - F[u'share4_notbyte'])
F[u'share4_diff'] = sorted([[u'+'.join(write_axes(rows)), n[:90]] for n, rows in S4R if write_axes(rows)])
F[u'pool_share4'] = sorted(n for n in CNT if len(CNT[n]) == NSRC)[:6]
assert F[u'share4_byte4'] + F[u'share4_notbyte'] == F[u'pool_4']

# ---- 候选锚池(整行, 短行须带 SPECIAL 标记) ----
SPECIAL = (u'Cache Leaks', u'2147483647', u'2^31', u'signed', u'unsigned', u'MINIMUM', u'SOA',
           u'TTL', u'Time to Live', u'32 bit integer', u'different TTLs', u'must be the same',
           u'STD 13', u'hereby', u'lower bound', u'MUST', u'SHOULD', u'MAY', u'63 octets', u'512',
           u'86400', u'one day', u'unsigned number')
POOL = set()
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if pnorm(l):
            POOL.add((t, l))
POOL = sorted(POOL)
CROSS = dict(((t, x), sum(1 for k in range(NSRC) if pnorm(x) in FAN[k])) for (t, x) in POOL)
POOLC = [(t, CROSS[(t, x)], x) for (t, x) in POOL]
F[u'apool_n'] = len(POOLC)
four(u'apool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
for n in range(1, NSRC + 1):
    F[u'apool_%d' % n] = len([p for p in POOLC if p[1] == n])

ATOMFAIL = []


def ATOMSEL(kind, tag, *needles):
    ok = (lambda n: n == 1) if kind == u'own' else (lambda n: n == int(kind))
    got = [p for p in POOLC if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
    if not got:
        got = [p for p in POOLC if p[0] == tag and all(x in p[2] for x in needles)]
    if not got:
        ATOMFAIL.append((kind, tag, needles))
        return None
    return max(got, key=lambda x: (len(x[2]), x[2]))


USEDATOM = []
ANCHORX = []


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    if x is None:
        return u'⟦%s⟧⟨MISSING⟩' % tag
    USEDATOM.append(x[2])
    ANCHORX.append((tag, x[1], x[2]))
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


CLOSK = sorted([k for k in F if (u'_close' in k or u'_ledger' in k)
                and isinstance(F[k], (int, float)) and not isinstance(F[k], bool)])
F[u'scalar_clos_n'] = len(CLOSK)
F[u'scalar_clos_sum'] = sum(F[k] for k in CLOSK)
F[u'list_clos_n'] = len([k for k in F if (u'_close' in k or u'_ledger' in k) and isinstance(F[k], list)])
# ---------- 恒等式 ----------
ZID = [
    (u"B68V('max_pow_close')", u'句内游标读出的上限=2 的 31 次方减一(两枚数各自独立解析)'),
    (u"B68V('pow_bits_close')", u'“maximum of 2^n” 的 n ⇎ “less significant n bits” 的 n 同枚'),
    (u"B68V('bitloss_close')", u'TTL 字段宽 32 位 ⇎ 只用低 31 位: 差恰为符号位一枚'),
    (u"B68V('sign_ledger')", u'给符号的份数+不给符号的份数=四份'),
    (u"B68V('ceil_floor_close')", u'明写上界的⇎写明下界的⇎两者都不写的, 三档恰分四份'),
    (u"B68V('notmand_close')", u'“maximum 而非 mandatory”那句只在 97'),
    (u"B68V('msb_close')", u'“最高位/符号位”那句只在 97'),
    (u"B68V('size_row_close')", u'尺寸表四行=有数字的行+只有符号的行'),
    (u"B68V('sgn_bucket_close',0)+B68V('sgn_bucket_close',1)+B68V('sgn_bucket_close',2)"
     u"+B68V('sgn_bucket_close',3)", u'signed 词的三桶(独立⇎un 之后⇎别的字母之后)之和=针总数'),
    (u"B68V('unsg_scan_close',0)+B68V('unsg_scan_close',1)+B68V('unsg_scan_close',2)"
     u"+B68V('unsg_scan_close',3)", u'桶档里“接在 un 之后”那桶=unsigned 针的读数'),
    (u"B68V('dur_distinct_close')", u'时长枚数档穷尽'),
    (u"B68V('soa_val_close')", u'87 姊妹篇的 SOA 示例没有一个字段取值相同'),
    (u"B68V('soa_AB_close')", u'两份示例的字段名并集=各自枚数之和−共有枚数'),
    (u"B68V('pool_tier_close')", u'锚池按压份数分档穷尽'),
    (u"B68V('share4_axis_close')", u'四份同现长行的写法差各落一根轴'),
    (u"B68V('share4_byte4')+B68V('share4_notbyte')-B68V('pool_4')", u'归一同现=逐字节同形+有写法差'),
    (u"B68V('pair_close')", u'配对: 归一长行交=逐字节交+仅归一交'),
    (u"B68V('union_close')", u'四份长行容斥=并集实数'),
    (u"B68V('enc_close',0)+B68V('enc_close',1)+B68V('enc_close',2)+B68V('enc_close',3)",
     u'字节−码位差=BOM 三字节+非 ASCII 的 UTF-8 扩展字节'),
    (u"B68V('ff_model_close',0)+B68V('ff_model_close',1)+B68V('ff_model_close',2)"
     u"+B68V('ff_model_close',3)", u'换页符枚数=页脚行数−1+文末是否留一枚'),
    (u"B68V('pg_foot_close',0)+B68V('pg_foot_close',1)+B68V('pg_foot_close',2)"
     u"+B68V('pg_foot_close',3)", u'“[Page ” 子串处数=页脚行数(逐份)'),
    (u"B68V('foot_minus_hdr',0)+B68V('foot_minus_hdr',1)+B68V('foot_minus_hdr',2)"
     u"+B68V('foot_minus_hdr',3)-4", u'每份页脚都比页眉多一枚'),
    (u"B68V('trail_hdr_close',0)+B68V('trail_hdr_close',1)+B68V('trail_hdr_close',2)"
     u"+B68V('trail_hdr_close',3)", u'行尾拖空格的行=页眉行+文末是否留换页符'),
    (u"B68V('nb_ff_close',0)+B68V('nb_ff_close',1)+B68V('nb_ff_close',2)+B68V('nb_ff_close',3)",
     u'两口径非空行之差=只由含换页符的空白组成的行'),
    (u"B68V('oblig_up_close')", u'大写三词合计逐份闭合'),
    (u"B68V('oblig_low_close',0)+B68V('oblig_low_close',1)+B68V('oblig_low_close',2)"
     u"+B68V('oblig_low_close',3)", u'小写词界三词合计逐份闭合'),
    (u"B68V('up_ABC_zero')", u'三份旧文书零枚大写义务词'),
    (u"B68V('hereby_D_only')", u'hereby 的词界形不在前三份'),
    (u"B68V('shall_D_only')", u'shall 的词界形不在前三份'),
    (u"B68V('ttl_win_close_sum')", u'窗内+窗外=TTL 全篇(逐份求和)'),
    (u"B68V('cache_win_close_sum')", u'窗内+窗外=cache 全篇(逐份求和)'),
    (u"B68V('ttllow_win_close_sum')", u'窗内+窗外=小写 ttl 全篇(逐份求和)'),
    (u"B68V('digit_win_close',0)+B68V('digit_win_close',1)+B68V('digit_win_close',2)"
     u"+B68V('digit_win_close',3)", u'窗内+窗外=数字符全篇(逐份)'),
    (u"B68V('wrap_hit_minus_onlyfold')", u'有跨行差的在册句原面一律零命中'),
    (u"B68V('wrap_close')", u'采集侧针档里跨行差全为原面零命中'),
    (u"B68V('ceil_sn_close')", u'97 的六枚上限句每枚全篇只出现一次'),
    (u"B68V('floor_sn_close')", u'87 两份的下界句每枚全篇只出现一次'),
    (u"B68V('cache_sn_close')", u'93 的四枚缓存句每枚全篇只出现一次'),
    (u"B68V('main4_close')", u'四份的主轴答数句各恰落一枚'),
    (u"B68V('std13_AB_close')", u'“STD 13”这个称呼不在它自己两份里'),
    (u"B68V('selfcite_ABC')", u'87⇎87⇎93 的自编号出现处恰为页眉数'),
    (u"B68V('soa_CD_empty')-2", u'93⇎97 的示例区读不出 SOA 五元组'),
    (u"B68V('no_dur_docs')-1", u'通篇没有一个时长字面的只有一份'),
    (u"B68V('ceil_docs_n')-1", u'把上限写成具体数字的只有一份'),
    (u"B68V('floor_day_close')", u'示例下限 86400 秒=24×60×60(游标读数后再算)'),
    (u"B68V('floor_soa_close')", u'句内游标读的下限=示例区逐行读出的 MINIMUM'),
    (u"B68V('sh_ladder_bad')", u'三档面严格⇎折平⇎摘壳只增不减'),
    (u"B68V('sh_hit_minus_only')", u'摘壳档新现身的句子在折平档一律零命中'),
    (u"B68V('shell_close',0)+B68V('shell_close',1)+B68V('shell_close',2)+B68V('shell_close',3)",
     u'页壳行=页眉+页脚+裸分隔线(逐份)'),
]
F[u'x_ident_n'] = len(ZID)

# --- SCAN END ---

# ---------- DERIV 登记与正文模板 ----------
K_, ZERO, COLL, SEENX = {}, [], {}, {}
G, LINES, MISSING = {}, [], []
FN = u'B68V'


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


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {u'B68V': BB68}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([tuple(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


VKMISS = []


def V(name, i=None, note=u''):
    if name not in F:
        VKMISS.append((name, i))
        return u'?'
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


def CLOS(key, note):
    return V(key, None, note)


def CLOS4(key, note):
    return u' ⇎ '.join(V(key, i, u'%s·%s' % (note, LB[t])) for i, t in enumerate(TAGS))


TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


def JOIN(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LB[t])) for i, t in enumerate(TAGS))


BB68 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B68V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
BARE = re.compile(r'^[0-9+\-*/().,\s]*$')
HELP = re.compile(u"^(V|JOIN|CLOS|CLOS4|TOK|AT)\\(")
_Q = u'"\''


def _split_top(s):
    out, buf, d, q = [], u'', 0, None
    for ch in s:
        if q:
            buf += ch
            if ch == q:
                q = None
            continue
        if ch in _Q:
            q = ch
            buf += ch
            continue
        if ch in u'([{':
            d += 1
        elif ch in u')]})':
            d -= 1
        if ch == u',' and d == 0:
            out.append(buf)
            buf = u''
            continue
        buf += ch
    out.append(buf)
    return [x.strip() for x in out]


def _unlit(x):
    t = x[1:] if x[:1] == u'u' else x
    assert t[0] in _Q and t[-1] == t[0], x
    return t[1:-1]


def _inline(t):
    while True:
        i = t.find(u'{EXPR(')
        if i < 0:
            break
        j = t.index(u'(', i)
        d, k = 0, j
        q = None
        while True:
            c = t[k]
            if q:
                if c == q:
                    q = None
                k += 1
                continue
            if c in _Q:
                q = c
                k += 1
                continue
            if c == u'(':
                d += 1
            elif c == u')':
                d -= 1
                if d == 0:
                    break
            k += 1
        if t[k + 1] != u'}':
            raise AssertionError((u'EXPRSCAN', repr(t[i:k + 4]), repr(t[j + 1:k])))
        args = _split_top(t[j + 1:k])
        assert len(args) == 3, args
        val = eval(args[0], {u'F': F, u'B68V': BB68, u'len': len, u'max': max, u'min': min,
                             u'round': round, u'repr': repr})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]

    def rep(m):
        c = m.group(1).strip()
        if HELP.match(c):
            return eval(c, {u'V': V, u'JOIN': JOIN, u'CLOS': CLOS, u'CLOS4': CLOS4, u'TOK': TOK, u'AT': AT})
        if u'B68V(' not in c:
            return m.group(0)
        assert BARE.match(BCALL.sub(u'0', c)), c
        val = eval(c, {u'B68V': BB68})
        reg(str(val), c.strip(), c.strip())
        return str(val)
    return re.sub(r'\{([^{}]*)\}', rep, t)


class _Ctx(dict):
    def __missing__(self, k):
        MISSING.append(k)
        return u'§' + k


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + _inline(tmpl)).format_map(_Ctx(dict(G, **kw))))

# ---------- 锚 ----------
G[u'A_bare32'] = AT(u'own', u'A', u'This field is a 32')
G[u'A_timelimit'] = AT(u'own', u'A', u'time limit on how long an RR')
G[u'A_floor'] = AT(u'own', u'A', u'at least the MINIMUM field')
G[u'A_neg'] = AT(u'own', u'A', u'cache, negative results')
G[u'A_wrap'] = AT(u'own', u'A', u'most positive and most')
G[u'B_row'] = AT(u'own', u'B', u'positive values of a signed')
G[u'B_unsgmin'] = AT(u'own', u'B', u'The unsigned 32 bit minimum')
G[u'B_lower'] = AT(u'own', u'B', u'Thus MINIMUM is a lower')
G[u'B_maxof'] = AT(u'own', u'B', u'set to the maximum of the TTL field')
G[u'B_typo'] = AT(u'own', u'B', u'this provison is to allow')
G[u'B_udp'] = AT(u'own', u'B', u'UDP messages')
G[u'C_cached'] = AT(u'own', u'C', u'is cached for TTL seconds')
G[u'C_head'] = AT(u'own', u'C', u'Cache Leaks')
G[u'C_limit'] = AT(u'own', u'C', u'impose a limit on the cache size')
G[u'C_within'] = AT(u'own', u'C', u'constitute a cache leak')
G[u'D_notclear'] = AT(u'own', u'D', u'not as clear as it could be')
G[u'D_hereby'] = AT(u'own', u'D', u'an unsigned number, with a')
G[u'D_pow'] = AT(u'own', u'D', u'maximum of 2^31')
G[u'D_bits'] = AT(u'own', u'D', u'less significant 31 bits')
G[u'D_signbit'] = AT(u'own', u'D', u'or sign, bit set to zero')
G[u'D_msb'] = AT(u'own', u'D', u'entire value received was zero')
G[u'D_free'] = AT(u'own', u'D', u'free to place an upper bound')
G[u'D_notmand'] = AT(u'own', u'D', u'not a mandatory')
G[u'D_dep'] = AT(u'own', u'D', u'differing TTLs in an RRSet')
G[u'D_same'] = AT(u'own', u'D', u'RRs in an RRSet must be the same')
G[u'D_1034sec'] = AT(u'own', u'D', u'section 4.3.4 refers to this technique')
G[u'X_boiler'] = AT(u'2', u'A', u'and any existing rules for the object')
G[u'X_boiler2'] = AT(u'2', u'B', u'appear in examples to be current')

if ATOMFAIL:
    for kind, tag, needles in ATOMFAIL:
        print(u'--- MISS kind=%s tag=%s needles=%s' % (kind, tag, needles))
        for nd in needles:
            tk = sorted(nd.replace(u'(', u'').replace(u')', u'').split(), key=len)[-1]
            for p in [q for q in POOLC if q[0] == tag and tk in q[2]][:4]:
                print(u'    cross=%s |%s|' % (p[1], p[2]))
    raise SystemExit(1)
for a in ANCHORX:
    print(u'ANCHOR %s cross=%s |%s|' % a)



# ---------- 正文 ----------
LINE(u'🧭', u"四源字节 {JOIN('bytes')} ⇎ 面内字符 {JOIN('chars')} ⇎ 原文件行 {JOIN('lines')} ⇎ 非空行 {JOIN('nonblank')} ⇎ 最长行 {JOIN('maxlen')} 列: 87 只说32位 ⇎ 87 说signed ⇎ 93 只谈缓存 ⇎ 97 定死31位。"
     u"体量两代分野: 87 姊妹篇 {V('bytes',0)}⇎{V('bytes',1)} 字节 ⇎ 93 {V('bytes',2)} ⇎ 97 {V('bytes',3)}——后两份合起来还不到前面一份的一半, 因为它们只改自己关心的那几节。"
     u"版式同族: 页眉(“RFC 编号 标题 月 年”) {JOIN('hdr')} 行 ⇎ 页脚(“[Page n]”) {JOIN('foot')} 行 ⇎ 换页符 {JOIN('formfeed')} 枚, 每份页脚都比页眉多一枚(逐份差 {JOIN('foot_minus_hdr')}, 合计对四枚闭合 {CLOS('foot_minus_hdr','首页无眉')}); 换页符枚数=页脚−1+文末是否留一枚(逐份闭合 {CLOS4('ff_model_close','换页账')}): 前三份文件末尾还有换页符 {JOIN('tail_ff')} ⇎ 97 以页脚收尾。"
     u"“[Page ” 子串处数与页脚行数逐份相等(闭合 {CLOS('pg_foot_close','页脚两档')}), 行尾拖空格的行 {JOIN('trail')} 恰为页眉行加文末那枚换页符所在的行(逐份闭合 {CLOS4('trail_hdr_close','拖空格账')} ⇎ 与页脚之差 {JOIN('foot_trail_gap')})。"
     u"编码层最干净: BOM {CLOS4('bom','带 BOM')} ⇎ 非 ASCII 码点 {JOIN('nonascii')} 枚 ⇎ CR {JOIN('cr')} ⇎ 字节−码位差 {JOIN('bc_delta')} 全为零(闭合 {CLOS('enc_close','编码差')}), 四份都是纯 ASCII 的 LF 面(全 ASCII 份数 {V('ascii_all')}/4); 四份签名 {V('sig_distinct')} 种(blake2b 前 16 位)。"
     u"空行账: 总行−非空行−只含换页符的行 = 纯空行 {V('blank_lines_extra')} 行(这是改判据就会动的余量, 不是恒等式); 两口径非空行之差 {JOIN('nb_gap')} 恰为“strip 判空但含换页符”的行 {JOIN('ff_blank')}(逐份闭合 {CLOS('nb_ff_close','两口径之差')})。")

LINE(u'📐', u"上限数字全部由句内游标解析, 一个都不手填: 97 {D_hereby} 之后连读出 {V('ttl_max')}, {D_pow} 的 2^ 之后读出 {V('ttl_pow')}, {D_bits} 里“less significant ”之后读出 {V('ttl_bits')} 位, 同一句的逆向游标在“ bit TTL field”之前读出字段宽 {V('ttl_field_bits')} 位——"
     u"四枚数互相对账: 上限=2^{V('ttl_pow')}−1(闭合 {CLOS('max_pow_close','上限⇎幂式')}), 幂指数=低位数(闭合 {CLOS('pow_bits_close','两枚31')}), 字段宽−可用位=符号位(闭合 {CLOS('bitloss_close','32−31=1')}); 低 31 位⇎32 位字段这两件事只在 97 面上同时写出。"
     u"87 的 {B_row} 里一个数字都没有, 只有符号: 把 §2.3.4 那张表按“两个以上空格”拆成两列, 读出 {V('size_b_rows')} 行, 其中带数字的 {V('size_num_rows')} 行(值 {V('size_nums')} 由列首游标解析), 只有符号的 {V('size_sign_rows')} 行(闭合 {CLOS('size_row_close','表格分档')}); TTL 那一行的右项长 {EXPR(len(F[u'size_ttl_val']), u\"len(B68V('size_ttl_val'))\", u'尺寸表 TTL 行右项长度')} 个字符, 是四行里唯一用形容词代替数字的一行, 其余三份的同类表读作 {V('size_other_rows')} 行。"
     u"87 面上另一处数字来自示例区: {A_floor} 把下限写成“here ”之后解析出的 {V('min_floor')} 秒(=24×60×60, 闭合 {CLOS('floor_day_close','86400 的天数账')} ⇎ 与示例区逐行读出的 MINIMUM {V('soa_min_A')} 对账 {CLOS('floor_soa_close','两处读数同值')}), 而 {B_unsgmin} 的 MINIMUM 行在 {V('soa_n_lines',0)}⇎{V('soa_n_lines',1)} 枚字段行里给的是另一批取值。"
     u"时长字面档: 十枚字面(60⇎600⇎7200⇎1800⇎300⇎86400⇎172800⇎604800⇎3600000⇎2147483647)在四份的出现处合计 {JOIN('dur_hit_total')} 次 ⇎ 每份至少出现一次的枚数 {JOIN('dur_distinct')}(枚数档闭合 {CLOS('dur_distinct_close','时长枚数')}), 同一字面的重复次 {V('dur_repeat_extra')}——"
     u"93 一份是 {V('dur_hit_total',2)} 次(闭合 {CLOS('no_dur_docs','无时长份数')}): 它通篇不写任何秒数, 而 97 只写一枚, 就是那枚上限 {V('lit_max_lit',3)} 处; 把上限写成具体数字的份数 {CLOS('ceil_docs_n','上限成数')}。")

LINE(u'⚖', u"头条不是“哪个数更大”, 而是“谁给了符号、谁给了数、谁只管下限”: 87 {A_bare32} 只说是 32 位整数(不碰符号也不碰数) ⇎ 87 {B_row} 给了符号 ⇎ 93 {C_cached} 不谈上限只谈按 TTL 缓存 ⇎ 97 {D_hereby} 把符号⇎下限⇎上限一次给全。"
     u"符号档由三桶游标扫描证明 87 面上那六枚 “signed” 全是幌子: 独立词形 {V('sgn_bare',0)} ⇎ 接在 un 之后 {V('sgn_in_un',0)} ⇎ 接在别的字母之后(designed⇎assigned) {V('sgn_in_word',0)}(三桶闭合 {CLOS('sgn_bucket_close','signed 三桶')} ⇎ un 桶对 unsigned 针闭合 {CLOS('unsg_scan_close','unsigned 桶')}), 87 面一枚独立 signed 都没有; 87 面恰好相反: 独立形 {V('sgn_bare',1)} ⇎ un 之后 {V('sgn_in_un',1)}。"
     u"同一份文档内部也自相矛盾: {B_row} 说 TTL 取 signed 32 位的正值, 而 {B_unsgmin} 说 SOA 的 minimum TTL 字段是 unsigned 32 位——同一份面上 signed 独立形 {V('sgn_bare',1)} 枚 ⇎ unsigned {V('lit_unsigned_word',1)} 枚, “unsigned 32 bit”整串 {V('lit_unsg32',1)} 处(SERIAL⇎MINIMUM 两行)。"
     u"97 先把病名写出来再下判词: {D_notclear}(“not as clear as it could be… whether the value is signed or unsigned”, 折平 {V('fold_not_clear',3)} 处) ⇎ 紧接着 hereby 定死; 全篇 hereby 词界形 {JOIN('hereby')} 处 ⇎ shall {JOIN('lo_shall')} 处, 两份旧文书都读不到(闭合 {CLOS('hereby_D_only','hereby 独占')} ⇎ {CLOS('shall_D_only','shall 独占')})。"
     u"截权与强制力是第二层分歧: 97 {D_free} 把截上界的权利明文给收方(“upper bound on any TTL” 原面 {V('lit_upper_bound',3)} 处), 又用 {D_notmand} 声明 TTL 是 maximum 而不是 mandatory; 87 两份给的是反方向的约束——下限: {A_floor} ⇎ {B_lower}(“Thus MINIMUM is a lower bound on the TTL field”, 只在折平档读得到), 三档分账(写上界⇎写下界⇎都不写)闭合 {CLOS('ceil_floor_close','上⇎下⇎不谈')}。"
     u"93 站在账外: 它说 {C_limit}(缓存大小可能设限、TTL 可能解释错) ⇎ {C_within}(TTL 期内重复查询就是 cache leak), 通篇 {V('secw_ttl',2)} 枚 TTL 里没有一枚配数字(窗外 {V('outw_ttl',2)} 枚, 窗账闭合由 🧪 行验)。")

LINE(u'🔁', u"引用与被引用: 97 不点名 RFC 号而点 STD 号 {D_notclear}(“TTL field in STD 13” 原面 {JOIN('lit_std13_ttl')} 处 ⇎ “STD 13” 字样 {JOIN('std13')} 处), 而 STD 13 就是 87 这两份——它自己两份里零枚 STD 13 字样(闭合 {CLOS('std13_AB_close','称呼在账外')}): 自指不用后来的集合号。"
     u"自编号账: 页眉 {JOIN('hdr')} 行 ⇎ 自编号出现处 {JOIN('cite_self')}, 逐份作差 {JOIN('selfcite_ledger')}——87 姊妹篇与 93 的差为 {V('selfcite_ledger',0)}⇎{V('selfcite_ledger',1)}⇎{V('selfcite_ledger',2)}, 97 的 {V('selfcite_ledger',3)} 处才是正文引用(前三份合计闭合 {CLOS('selfcite_ABC','自编号=页眉')})。"
     u"97 还纠 87 的节号: {D_1034sec}——它一边引用 87 的 §4.3.4, 一边指出那份文档把 negative caching 的 SOA 写在 authority 段而不是 additional 段; “4.3.4” 字样在四份面上分别 {JOIN('lit_sec434')} 处 ⇎ 折平 {JOIN('fold_sec434')} 处, 87 自己那枚是节标题 ⇎ 97 那枚是它引用的号。"
     u"身份头: Category: Standards Track {JOIN('cat_std')} ⇎ Obsoletes 头 {JOIN('obs_hdr')} ⇎ Updates 头 {JOIN('upd_hdr')} ⇎ STD: 头 {JOIN('std_hdr')} ⇎ BCP: 头 {JOIN('bcp_hdr')} ⇎ ISSN 头 {JOIN('issn_hdr')} ⇎ Request for Comments 行 {JOIN('req_rc')} ⇎ Network Working Group 抬头 {JOIN('nwgroup')} ⇎ IETF 抬头 {JOIN('ise')}: 87 两份同月同作者同抬头, 93 挂 BCP 族 ⇎ 97 唯一带 Category 行。"
     u"引用网: 1034 {JOIN('cite_1034')} ⇎ 1035 {JOIN('cite_1035')} ⇎ 1536 {JOIN('cite_1536')} ⇎ 2181 {JOIN('cite_2181')} ⇎ 1123 {JOIN('cite_1123')} ⇎ 1010 {JOIN('cite_1010')} 次; 后来两份对 87 姊妹篇的合计引用 {V('dns_family',2)}⇎{V('dns_family',3)} 次, 而 87 两份互引 {V('dns_family',0)}⇎{V('dns_family',1)} 次——后来者把这两份当作一个整体引用。")

LINE(u'🧪', u"窗口口径: 四份各自的答题节是 87 §3.6 Resource Records ⇎ 87 §2.3.4 Size limits ⇎ 93 §5 Cache Leaks: ⇎ 97 §8 Time to Live (TTL)——标题行 {JOIN('sec_head')} ⇎ 窗起行 {JOIN('sec_a')} ⇎ 窗止行 {JOIN('sec_b')} ⇎ 窗长 {JOIN('sec_len')} 字符 ⇎ 窗内行数 {JOIN('sec_lines')}。"
     u"窗内外分账: TTL 字样窗内 {JOIN('secw_ttl')} ⇎ 窗外 {JOIN('outw_ttl')}(逐份合计闭合 {CLOS('ttl_win_close_sum','TTL 窗账')}), 小写 ttl 窗内 {JOIN('secw_ttllow')} ⇎ 窗外 {JOIN('outw_ttllow')}(闭合 {CLOS('ttllow_win_close_sum','小写 ttl 账')}), cache 词干窗内 {JOIN('secw_cache')} ⇎ 窗外 {JOIN('outw_cache')}(合计 {CLOS('cache_win_close_sum','cache 窗账')}), 数字符窗内 {JOIN('secw_digit')} ⇎ 窗外 {JOIN('outw_digit')}(逐份闭合 {CLOS4('digit_win_close','数字窗账')})。"
     u"窗长与数字密度的对照: 97 的答题节最长({V('sec_len',3)} 字符)却只有 {V('secw_digit',3)} 枚数字符(千分位密度 {V('digit_density',3)}) ⇎ 87 的 §2.3.4 只有 {V('sec_len',1)} 字符而带 {V('secw_digit',1)} 枚数字符(密度 {V('digit_density',1)}) ⇎ 93 的答题节 {V('sec_len',2)} 字符零枚数字——把上限说清楚靠的不是篇幅而是那枚 2^31−1。"
     u"句数口径: 主轴四枚答数句(87 的裸 32 位句 ⇎ 87 的符号行 ⇎ 93 的缓存句 ⇎ 97 的 hereby 句)按折平在本面命中 {JOIN('main4_fold')} 枚, 四份合计 {V('main4_each')} 枚(闭合 {CLOS('main4_close','主轴各一枚')}); 全部 {V('wrap_sn_n')} 枚在册句里折平档 {JOIN('sn_fold_docs')} ⇎ 严格档 {JOIN('sn_strict_docs')}, 其余主线针 {JOIN('sn_other_fold')} 枚。")

LINE(u'⛓', u"折行通道在本条是必需档: {V('wrap_sn_n')} 枚在册句里 {V('wrap_sn_hit')} 枚有跨行差, 折平−原面合计 {V('wrap_sn_total')} 处, 而这 {V('wrap_sn_hit')} 枚在原面一律零命中(闭合 {CLOS('wrap_hit_minus_onlyfold','跨行差全为折行')}); 采集侧那批针的差合计 {V('fold_total_delta')} 枚, 其中原面零命中的 {V('wrap_delta_hit')} 枚(针档闭合 {CLOS('wrap_close','针档折行')})。"
     u"第三档是摘壳档, 本条有一枚答案句非它不可: 97 的编码句被页壳劈在两页之间——原面 {V('s_d_bits',3)} 处 ⇎ 全篇折平 {V('s_d_bits_fold',3)} 处(页眉页脚还留在串里)⇎ 摘掉页壳行才读出 {V('s_d_bits_sh',3)} 处; "
     u"在册 {V('wrap_sn_n')} 枚句子里摘壳档新增 {V('sh_sn_hit')} 枚 ⇎ 其中折平档零命的 {V('sh_only_n')} 枚(清单 {V('sn_only_sh')}, 闭合 {CLOS('sh_hit_minus_only','摘壳只补跨页句')}), 新增处数合计 {V('sh_gap_total')}; "
     u"三档逐份读到的在册句数 {JOIN('sn_strict_docs')} ⇎ {JOIN('sn_fold_docs')} ⇎ {JOIN('sn_sh_docs')}(只增不减 {CLOS('sh_ladder_bad','三档单调')} ⇎ 逐份跨度 {JOIN('sn_face_span')} 枚 ⇎ 摘壳档在册句合计 {V('sn_sh_total')} 处); "
     u"页壳行数 {JOIN('shell_lines')} = 页眉 {JOIN('hdr')} + 页脚 {JOIN('foot')} + 裸分隔线 {JOIN('rule_extra')}(逐份闭合 {CLOS4('shell_close','页壳三件')}), 摘壳后字符数 {JOIN('sh_len')} 而摘掉的壳行占 {JOIN('shell_chars')} 字符; "
     u"六枚上限句、三枚下限句、四枚缓存句在摘壳档全篇各只现一次(上限 {CLOS('ceil_sn_close','上限句各一')} ⇎ 下限 {CLOS('floor_sn_close','下限句各一')} ⇎ 缓存 {CLOS('cache_sn_close','缓存句各一')})。"
     u"三处最锋利的: 87 的“a 32 ”与“bit integer”被劈在行界两侧, 整句照抄进 needle 原面 {V('s_a_bare32',0)} 处 ⇎ 折平 {V('s_a_bare32_fold',0)} 处; 97 的“not a mandatory ”与“time to live.”同理(原面 {V('s_d_notmand',3)} ⇎ 折平 {V('s_d_notmand_fold',3)}); 87 的“Thus MINIMUM is a lower ”与“bound on the TTL field”也劈行({V('s_b_lower',1)} ⇎ {V('s_b_lower_fold',1)})——三份文档的答案句全都跨行, 只按行搜就全读不到。"
     u"跨行差按份分布 {JOIN('wrapgap_a_bare32')} ⇎ {JOIN('wrapgap_d_notmand')} ⇎ {JOIN('wrapgap_b_lower')}, 严格档读到的在册句数 {JOIN('sn_strict_docs')} ⇎ 容行档 {JOIN('sn_fold_docs')}; 只在折平档才现身的句子 {V('wrap_onlyfold_n')} 枚(清单 {V('sn_only_fold')})。"
     u"写法分家在本条不成立: 归一后四份同现的长行 {V('pool_4')} 条(池 {V('pool_n')} 条按压份数分档 {JOIN('pool_tier')}, 闭合 {CLOS('pool_tier_close','池分层')}), 因此“逐字节同形⇎只差一根轴”两档都空(轴账闭合 {CLOS('share4_axis_close','写法轴')} ⇎ 字节同形 {V('share4_byte4')} ⇎ 分家 {V('share4_notbyte')}), 分家清单 {V('share4_diff')}——四份文档没有共用的正文行, 分歧只能靠整句针与窗口判。"
     u"页壳是隐形通道: 页眉行把 RFC 号抬高 {JOIN('hdr')} 次 ⇎ 正文自引用 {JOIN('selfcite_ledger')} 次; “只含换页符的行”按 strip 口径是 {JOIN('ff_only')} 行, 按含换页符的空白行口径是 {JOIN('ff_blank')} 行——同一份面上两把尺差出整个空行档, 这就是 93 的时长账为什么必须点明口径。"
     u"示例区也是通道: SOA 五元组的字段行按三种写法读(小写粘连 ⇎ 大写带空格 ⇎ 右括号夹在数与注释之间), 字段名行 {JOIN('soa_n_lines')} 枚 ⇎ 大写注释 {JOIN('soa_upper')} ⇎ 小写注释 {JOIN('soa_lower')} ⇎ 夹括号 {JOIN('soa_paren')} ⇎ 小写−大写 {JOIN('soa_case_delta')}; 87 姊妹篇两份额度里的字段名共有 {V('soa_AB_shared')} 枚而取值相同的 {V('soa_AB_valshare')} 枚(闭合 {CLOS('soa_val_close','示例互斥')} ⇎ {CLOS('soa_AB_close','字段名并集账')}): 同一个可选机制, 两份各造了一个数值完全不同的示例区。")

LINE(u'📏', u"义务档位不成差轴, 成轴的是大写三词的缺席: 全大写 MUST {JOIN('u_must')} ⇎ SHOULD {JOIN('u_should')} ⇎ MAY {JOIN('u_may')} ⇎ MUST NOT {JOIN('u_must_not')} ⇎ SHOULD NOT {JOIN('u_should_not')} ⇎ REQUIRED {JOIN('u_required')} ⇎ RECOMMENDED {JOIN('u_recommended')}, 三词合计 {JOIN('oblig_up')}(闭合 {CLOS('oblig_up_close','大写合计')} ⇎ 前三份合计 {CLOS('up_ABC_zero','旧文书零大写形')}); 97 一份里三词各一枚(共 {V('up_D_n')} 枚), 而那枚 MUST 正是 {D_same}。"
     u"全小写词界形 must {JOIN('lo_must')} ⇎ should {JOIN('lo_should')} ⇎ may {JOIN('lo_may')}, 合计 {JOIN('oblig_low')}(逐份闭合 {CLOS4('oblig_low_close','小写合计')}); 定义这组义务词的那份规范, 其编号在四份面上被引 {JOIN('rfc2119_ref')} 次——一处都没有, 义务档位靠排版世代而不是引用建立。"
     u"同一件判词的措辞换代可判: 97 用 “It is hereby specified”(折平 {V('fold_hereby_ttl',3)} 处) ⇎ “Implementations should treat”(“as if the entire value received was zero” 原面 {V('lit_msb_zero',3)} 处) ⇎ “is hereby deprecated, … must be the same”(原面 {V('lit_same_ttl',3)} ⇎ 折平 {V('fold_same_ttl',3)}); 93 通篇用 might/should 讲实现错(小写三词 {V('oblig_low',2)} 处), 87 姊妹篇用 is/should({V('oblig_low',0)}⇎{V('oblig_low',1)} 处)。"
     u"词面密度: 大写 TTL {JOIN('lit_ttl_cap')} 枚 ⇎ 小写 ttl {JOIN('lit_ttl_low')} 枚 ⇎ “time to live” {JOIN('lit_time_live')} 处 ⇎ “32 bit integer” 原面 {JOIN('lit_bare32')} ⇎ 折平 {JOIN('fold_bare32')}——97 是唯一同时写大写 TTL ⇎ 小写 ttl ⇎“Time To Live” ({V('lit_time_live',3)} 处)三种称呼的一份。")

LINE(u'🗓', u"符号位针: “positive values of a signed 32 bit number” 原面 {JOIN('lit_signed32')} ⇎ “less significant 31 bits” {JOIN('lit_hi31')} ⇎ “2^31 - 1” {JOIN('lit_max_pow')} ⇎ “minimum value of 0” {JOIN('lit_min0')}, 四枚全为 0⇎0⇎0⇎1 档, 即上限的完整表述只有一份文书写过; 处理档 “most significant, or sign, bit set to zero” {JOIN('lit_sign_bit')} ⇎ “as if the entire value received was zero” {JOIN('lit_msb_zero')}(闭合 {CLOS('msb_close','最高位句')})。"
     u"下限侧针: “at least the MINIMUM field of the SOA” 原面 {JOIN('lit_floor_sent')} ⇎ 折平 {JOIN('fold_floor_sent')}(差 {JOIN('delta_floor_sent')}), “lower bound on the TTL field” 原面 {JOIN('lit_lower_bound')} ⇎ 折平 {JOIN('fold_lower_bound')}(差 {JOIN('delta_lower_bound')}), “here 86400 seconds” {JOIN('lit_here_86400')} ⇎ “or one day” {JOIN('lit_one_day')} ⇎ “expire after a week” {JOIN('lit_expire_week')} ⇎ “minimum of a day” {JOIN('lit_min_day')}——87 两份各用一种写法把同一个 MINIMUM 说成下界, 一份举数值例一份立规则。"
     u"缓存侧针: “cached for TTL seconds” {JOIN('lit_cached_for')} ⇎ “until the TTL expires” {JOIN('lit_ttl_expires')} ⇎ “Cache Leaks” {JOIN('lit_cache_leak')} ⇎ “impose a limit on the cache size” {JOIN('lit_cachesize')} ⇎ “within a TTL period” {JOIN('lit_within_ttl')}, 五枚都只在 93; “upper bound on any TTL” {JOIN('lit_upper_bound')} ⇎ “maximum time to live, not a mandatory time to live” {JOIN('lit_not_mandatory')} 只在 97(折平档分别 {JOIN('fold_upper_bound')} ⇎ {JOIN('fold_not_mandatory')})。"
     u"RRSet 档: “different TTLs” {JOIN('lit_different_ttls')} ⇎ “RRSet to have different TTLs” {JOIN('lit_rrset_same')} ⇎ “the TTLs of all RRs in an RRSet must be the same” 原面 {JOIN('lit_same_ttl')} ⇎ 折平 {JOIN('fold_same_ttl')} ⇎ “use of differing TTLs in an RRSet is hereby” {JOIN('lit_diff_dep')}——87 面上这枚词干出现在“两份服务器给出不同 TTL 说明缓存时刻不同”的叙事里, 97 把它升格成一致性要求并 deprecated。"
     u"节号与称呼: “5.2. TTLs of RRs in an RRSet” {JOIN('lit_sec52')} 处 ⇎ “4.3.4” {JOIN('lit_sec434')} 处 ⇎ “STD 13” {JOIN('std13')} 处——93 的七节目录里没有一节谈 TTL 取值, 它的 TTL 叙事全在 §5 那一节内(见 🧪 窗账)。")

LINE(u'🧾', u"文档身份独立一轴: 87 姊妹篇的标题分别是 Domain Concepts and Facilities ⇎ Domain Implementation and Specification, 93 是 Common DNS Implementation Errors, 97 是 Clarifications to the DNS Specification——四份里只有 97 用“澄清”自居, 它的答题节也因此最短而最硬(窗长 {V('sec_len',3)} 字符 ⇎ 数字符 {V('secw_digit',3)} 枚)。"
     u"引用写法: 97 用 [RFC1034, RFC1035] 方括号族(“[RFC” {JOIN('brf')} 处) ⇎ 87 两份用 “RFC-1010”“RFC-882” 短横族(“RFC-” {JOIN('self_ref')} 处) ⇎ 93 两种混用; 自编号 {JOIN('cite_self')} 处对页眉 {JOIN('hdr')} 处的逐份差 {JOIN('selfcite_ledger')}。"
     u"笔误档: 87 概念篇写 “an is primarily used”(多一枚词, {V('lit_typo_anis',0)} 处 ⇎ 折平 {V('fold_typo_anis',0)} 处) ⇎ 87 实现篇写 “this provison is to allow”(少一枚字母, {V('lit_typo_prov',1)} 处 ⇎ 折平 {V('fold_typo_prov',1)} 处)——这类字面缺陷只证明面没被校订, 不参与上限判定, 但可作为“同一份文档后来被 97 逐段重写”的旁证。"
     u"93 把 DNS 实现错误分成七节, TTL 只在“Cache Leaks”一节里出现, 该节窗内 TTL {V('secw_ttl',2)} 枚而数字符 {V('secw_digit',2)} 枚(窗账见 🧪 行): 它诊断的是“缓存在 TTL 期内被绕过”, 而不是“TTL 该设多大”。")

LINE(u'⇄', u"整行搬运(≥55 字符、归一只留 a-z0-9 与 . - ⇎ 原面逐字节, bisect 档求交): 六对配对里非零的 {V('pair_nonzero')} 对——归一长行交 {JOIN('pair_share')} ⇎ 逐字节同形 {JOIN('pair_byte')} ⇎ 仅归一同 {JOIN('pair_norm_only')}(配对闭合 {CLOS('pair_close','两把搬运尺')}); 最大的一对正是 87⇎87({V('pair_share',0)} 行, 其中逐字节 {V('pair_byte',0)} ⇎ 仅归一 {V('pair_norm_only',0)}), 而 93⇎97 之间只有 {V('pair_share',5)} 行。"
     u"那些共实行不是正文而是壳层: 采一例如 {X_boiler} ⇎ {X_boiler2}——87 姊妹篇共用“状态说明/参考文献”段, 正文各写各的; 归一口径里 87⇎87 那 {V('pair_norm_only',0)} 行只差在大小写或标点, 因为两份的版心宽度不同。"
     u"值域⇎并集账: 每份归一长行的值域大小 {JOIN('set_sizes')}, 四份并集 {V('union_all')} 行, 只在本份 {JOIN('only_each')}, 四份同现 {V('pool_4')} 行 ⇒ 容斥 Σ单份−Σ两两+Σ三三−Σ四份−并集 = {CLOS('union_close','容斥')}(三三交读数 {JOIN('tri_share')})。"
     u"池口径与值域口径不同源: 锚池 {V('pool_n')} 条(额外要求归一后仍 ≥55 字符)比值域合计少, 因此“仅一份”在两档下分别是 {V('pool_share1_1034')}⇎{V('pool_share1_1035')}⇎{V('pool_share1_1536')}⇎{V('pool_share1_2181')}(池档, 两份同现档 {V('pool_share2_ab')}) 与 {JOIN('only_each')}(值域档)——同一件事两把尺, 报数必须点明口径。")

LINE(u'ℒ', u"方法 ⇒ 面对“同一个字段的取值范围到底谁说了算”的四份文书, 本遍把三件事做成可判口径: "
     u"①数字由句子内部解析而不是抄表格——上限 {V('ttl_max')} ⇎ 幂 {V('ttl_pow')} ⇎ 位 {V('ttl_bits')} ⇎ 字段宽 {V('ttl_field_bits')} ⇎ 示例下限 {V('min_floor')} 五枚数各来自不同游标(正向读 ⇎ 逆向读), 三式互证(闭合 {CLOS('max_pow_close','上限式')} ⇎ {CLOS('pow_bits_close','两枚31')} ⇎ {CLOS('bitloss_close','32−31')}), 任何一处读数漂移都会同时倒掉多条判定; "
     u"②词形分桶而不是搜词——signed 的三桶(独立⇎un 之后⇎别的字母之后)把 87 面的六枚幌子与 87 面的真符号分开, 并与 unsigned 针交叉闭合(闭合 {CLOS('sgn_bucket_close','三桶')} ⇎ {CLOS('unsg_scan_close','桶⇎针')}); "
     u"③上界⇎下界⇎不谈三档分账(闭合 {CLOS('ceil_floor_close','三档分账')})——93 不是“给了更小的上限”, 而是根本不在这本账上。"
     u"严格档 ⇎ 容行档在本条不是冗余: {V('wrap_sn_n')} 枚在册句里 {V('wrap_sn_hit')} 枚只有折平档读得到, 若只按行搜整句, 87 的裸 32 位句 ⇎ 87 的下界句 ⇎ 97 的非强制句一律零命中。{V('x_ident_n')} 条恒等式全部由面内现读构成并送门槛重算, 标量闭合 {V('scalar_clos_n')} 枚 ⇎ 总账 {CLOS('scalar_clos_sum','闭合合计')} ⇎ 清单闭合 {V('list_clos_n')} 枚。")

LINE(u'✂️', u"为什么这份编码比答题窗口长 ⇒ 四源各 {JOIN('chars')} 字符 ⇎ 答题窗各 {JOIN('sec_len')} 字符: 窗只占全篇的千分位(87 概念 {EXPR(int(F[u'sec_len'][0]*1000//F[u'chars'][0]), u\"B68V('sec_len',0)*1000//B68V('chars',0)\", u'窗占比千分位')}‰ ⇎ 87 实现 {EXPR(int(F[u'sec_len'][1]*1000//F[u'chars'][1]), u\"B68V('sec_len',1)*1000//B68V('chars',1)\", u'窗占比千分位')}‰ ⇎ 93 {EXPR(int(F[u'sec_len'][2]*1000//F[u'chars'][2]), u\"B68V('sec_len',2)*1000//B68V('chars',2)\", u'窗占比千分位')}‰ ⇎ 97 {EXPR(int(F[u'sec_len'][3]*1000//F[u'chars'][3]), u\"B68V('sec_len',3)*1000//B68V('chars',3)\", u'窗占比千分位')}‰)。"
     u"答数只有一枚 2147483647, 但“谁敢定符号、谁只给形容词、谁把示例当规则、谁把截权推给收方”要跨四份并排读: 87 面上 signed 六枚幌子 ⇎ 一枚真符号在 87 的表行 ⇎ 97 面上 unsigned⇎0⇎2147483647⇎2^31−1⇎低 31 位⇎最高位按 0⇎可自截⇎非强制八事齐写; 93 面上时长字面 {V('dur_hit_total',2)} 次都为零。"
     u"读它请按“这个数字是谁给的、以什么句式给的、句子被劈在哪一行、收方有没有截它的权利”来读, 而不是按“少抄了多少原文”。")

if VKMISS:
    for nm in sorted(set(x[0] for x in VKMISS)):
        print(u'NOKEY %s %s' % (nm, [y[1] for y in VKMISS if y[0] == nm][:4]))
    raise SystemExit(1)
assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
ZFAIL = []
for _e, _n in ZID:
    _v = eval(_e, {u'B68V': BB68})
    if _v != 0:
        ZFAIL.append((_n, _e, _v))
    else:
        reg(u'0', _e, _n)
if ZFAIL:
    for _n, _e, _v in ZFAIL:
        print(u'ZFAIL %s |%s| = %s' % (_n, _e, _v))
    raise SystemExit(1)
body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCH if 1 < len(HITC[a]) < NSRC]),
       u'all4': len([a for a in ANCH if len(HITC[a]) == NSRC])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'],
         u'anchor_all4': CLS[u'all4'], u'checks': DIST * NSRC}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all4'] == DIST
for n, v in sorted(AMETA.items()):
    reg(str(v), u"%s('%s')" % (FN, n), TOKV.get(n, n))
for n in AMETA:
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
for n in AMETA:
    F[n] = v = AMETA[n]
    reg(str(v), u"%s('%s')" % (FN, n), n)


# ---- 整串打印的列表键: 元素也是判词里的字面数, 按下标补登记算式 ----
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
SRC_HARD = set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', u''.join(TXT)))
BODY_HARD = sorted(set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', body)
                       if len(m.group(0).rstrip(u'.')) >= 3), key=lambda x: (len(x), x))
NOEXPR = []
for s in BODY_HARD:
    if s in K_ or s in SRC_HARD:
        continue
    got = [e for e in ELEMS.get(s, []) if eval(e, {u'B68V': BB68}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, NOEXPR
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv68.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b68flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms68.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[' + u''.join(TAGS) + u']⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == n]))
                       for c, n in ((u'single', 1), (u'two', 2), (u'three', 3), (u'four', 4))),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
      u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': NSRC, u'flat': F,
      u'closure_keys': [k for k in F if k.endswith(u'close')]}
json.dump(CH, io.open(u'corpus/_b68checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 字符／原行 %d／非空行 %d／TTL 表述 %s／页眉 %d⇎页脚 %d⇎换页 %d)' % (
        os.path.basename(PATH[i]), F[u'bytes'][i], F[u'chars'][i], F[u'lines'][i], F[u'nonblank'][i],
        [u'只说 32 位整数', u'signed 32 位的正值', u'不谈上限',
         u'unsigned⇎0..%d⇎低 %d 位' % (F[u'ttl_max'], F[u'ttl_bits'])][i],
        F[u'hdr'][i], F[u'foot'][i], F[u'formfeed'][i])
    for i in range(NSRC)) +
    u' (四份 RFC Editor 纯文本面, 全 ASCII／全 LF、无 BOM; 上限、幂次、位数、字段宽与示例下限都由句内游标现读, 一个都不手填。'
    u'抓取时刻、RFC Editor 此刻的现行状态页与勘误页、此后 1035bis 把这段并入哪一节、现网 resolver 实际把 TTL 截到多少秒'
    u'都只在本机或站外成立, 不进门槛)\n')
联结 = (u"；联结不是“同一份数据的两种序列化”, 而是“一条 RR 的 TTL 上限到底是多少、谁有权截”在四份一手 DNS 文书里的四种答法: "
        u"87 概念篇把 TTL 说成 32 位整数(在册句折平档 {0} 枚 ⇎ 原面 {1} 枚, 因为“a 32 ”与“bit integer”被劈在行界两侧), 不碰符号也不碰数——它面上 6 枚 “signed” 字样全在 designed⇎assigned 里, 独立词形 {2} 枚; ⇎ "
        u"87 实现篇的 §2.3.4 尺寸表把 TTL 行写成“positive values of a signed 32 bit number”, 表 {3} 行里带数字的只有 {4} 行(63⇎255⇎512)而 TTL 行只有形容词(闭合 {5}); 同一份文档的 SOA MINIMUM 行却写“unsigned 32 bit”(整串 {6} 处)并把 MINIMUM 定成 TTL 的下界——signed⇎unsigned 在同一页上各说一个字段; ⇎ "
        u"93 把 TTL 用在缓存叙事里, 十枚时长字面在它面上出现 {7} 次, 既不谈上限也不谈符号; ⇎ "
        u"97 先点名 STD 13 说得不够清楚, 再 hereby 定死 unsigned⇎0..{8}⇎2^{9}−1⇎只用低 {10} 位⇎字段宽 {11} 位(游标读数互证闭合 {12}⇎{13}⇎{14}); "
        u"截权随后给出: 收方“always free to place an upper bound on any TTL received”(原面 {15} ⇎ 折平 {16} 枚) ⇎ 同一节又声明 TTL 是 maximum 而非 mandatory(折平 {17} 枚, 只在 97: 闭合 {18}), 上界⇎下界⇎不谈三档分四份闭合 {19}; "
        u"RRSet 一致性也是 97 的手笔: “the TTLs of all RRs in an RRSet must be the same” 原面 {20} ⇎ 折平 {21} 枚, 而 87 面上“different TTLs”({22} 处)只是两份服务器缓存时刻不同的证据; "
        u"义务档位换代: 大写 MUST⇎SHOULD⇎MAY 三词在 87⇎87⇎93 一律零枚而 97 各一枚(合计闭合 {23}), hereby 词界形 {24} 处 ⇎ shall {25} 处都只在 97 ⇎ 定义义务词的那份规范编号全篇零枚({26}); "
        u"折行通道是必需档: 在册 {27} 枚句子里 {28} 枚只有折平档读得到(合计 {29} 处), 严格档读到 {30}⇎{31}⇎{32}⇎{33} 枚 ⇎ 容行档 {34}⇎{35}⇎{36}⇎{37} 枚; "
        u"整行搬运六对里非零 {38} 对, 最大一对是 87 姊妹篇的壳层共实行: 归一 {39} 行(逐字节 {40} ⇎ 仅归一 {41}), 归一后四份同现的长行 {42} 条——四份文档没有共用正文行, 写法分家那档因此空转(闭合 {43}).\n").format(
    F[u's_a_bare32_fold'][0], F[u's_a_bare32'][0], F[u'sgn_bare'][0],
    F[u'size_b_rows'], F[u'size_num_rows'], F[u'size_row_close'],
    F[u'lit_unsg32'][1], F[u'dur_hit_total'][2], F[u'ttl_max'], F[u'ttl_pow'], F[u'ttl_bits'],
    F[u'ttl_field_bits'], F[u'max_pow_close'], F[u'pow_bits_close'], F[u'bitloss_close'],
    F[u'lit_free_bound'][3], F[u'fold_free_bound'][3], F[u'fold_not_mandatory'][3], F[u'notmand_close'],
    F[u'ceil_floor_close'], F[u'lit_same_ttl'][3], F[u'fold_same_ttl'][3], F[u'lit_different_ttls'][0],
    F[u'up_ABC_zero'], sum(F[u'hereby']), sum(F[u'lo_shall']), sum(F[u'rfc2119_ref']),
    F[u'wrap_sn_n'], F[u'wrap_sn_hit'], F[u'wrap_sn_total'],
    F[u'sn_strict_docs'][0], F[u'sn_strict_docs'][1], F[u'sn_strict_docs'][2], F[u'sn_strict_docs'][3],
    F[u'sn_fold_docs'][0], F[u'sn_fold_docs'][1], F[u'sn_fold_docs'][2], F[u'sn_fold_docs'][3],
    F[u'pair_nonzero'], F[u'pair_share'][0], F[u'pair_byte'][0], F[u'pair_norm_only'][0],
    F[u'pool_4'], F[u'share4_axis_close'])
title = (u'# B68 一条 RR 的 TTL 上限到底是多少、谁有权截，四份 DNS 一手文书四种答法：只说 32 位整数 ⇎ signed 32 位的正值却不给数 ⇎ 通篇不谈上限只谈按 TTL 漏缓存 ⇎ 明写 unsigned⇎0..2147483647⇎2^31−1⇎只用低 31 位⇎收方可自截（符号⇎数字⇎下界⇎截权四件事没有一份给全）\n')
text = (title + srcline + 联结 +
        u'tags: 符号位⇎数字⇎下界⇎截权 四件事分给四份文书 句内游标解析(正向⇎逆向) 上限=2^n−1⇎n=低位数⇎字段宽−可用位=1 '
        u'signed 三桶词界档(designed/assigned 幌子⇎un 之后⇎独立形) 同文档内 signed 表行⇎unsigned MINIMUM 行 '
        u'尺寸表逐行分列(TTL 行唯一无数字) MINIMUM 是下界而非上界(87 举 86400 例⇎87 立规则) '
        u'93 时长字面零枚⇎97 只写一枚就是上限 折行通道必需档(裸32位句⇎下界句⇎非强制句全跨行) '
        u'上界⇎下界⇎不谈三档分账 always free to place an upper bound ⇎ maximum 而非 mandatory '
        u'RRSet 内 TTL 必须相同(97 hereby deprecated ⇎ 87 只当缓存时刻不同的证据) STD 13 称呼在自指之外 '
        u'2119 大写形三份旧文书全零⇎97 各一枚 hereby⇎shall 独占 97 纠 87 的节号误引 页脚比页眉多一枚⇎换页符=页脚−1+文末留否 '
        u'拖空格行=页眉+文末换页 两把空行尺(strip⇎含换页符) 池按压份数分档闭合⇎四份同现零枚(写法分家空转) '
        u'87 姊妹篇壳层共实行(归一⇎字节两把尺) SOA 示例区字段名同而取值全互斥 闭合账 标量 %d⇎清单 %d 项⇎恒等式 %d 条\n' % (
            F[u'scalar_clos_n'], F[u'list_clos_n'], F[u'x_ident_n']) +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill68.py 从 corpus/_b68checks.json 与 corpus/_deriv68.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两至三源 %d ⇎ 四源 %d ⇎ 错配 %d ｜ 池内取用 %d／池 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], len(ERR), CH[u'pool_used'], F[u'pool_n']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(F)))
print(u'上限 %d ⇎ 幂 %d ⇎ 低 %d 位 ⇎ 字段 %d 位 ⇎ 示例下限 %d ｜ 闭合 %d/%d/%d' % (
    F[u'ttl_max'], F[u'ttl_pow'], F[u'ttl_bits'], F[u'ttl_field_bits'], F[u'min_floor'],
    F[u'max_pow_close'], F[u'pow_bits_close'], F[u'bitloss_close']))
print(u'signed 三桶 %s ⇎ unsigned 针 %s ｜ 尺寸表 %s 行(带数 %s ⇎ 带符号 %s ⇎ 数 %s)' % (
    F[u'sgn_bucket'], F[u'lit_unsigned_word'], F[u'size_b_rows'], F[u'size_num_rows'],
    F[u'size_sign_rows'], F[u'size_nums']))
print(u'三档分账 上界 %s ⇎ 下界 %s ⇎ 不谈 %s 闭合 %d ｜ 时长字面 %s ⇎ 无时长份数 %d' % (
    F[u'has_ceil'], F[u'has_floor'], F[u'has_none'], F[u'ceil_floor_close'],
    F[u'dur_hit_total'], F[u'no_dur_docs']))
print(u'跨行: 在册句 %d 有差 %d 合计 %d ｜ 严格档 %s ⇎ 容行档 %s ｜ 针差合计 %d' % (
    F[u'wrap_sn_n'], F[u'wrap_sn_hit'], F[u'wrap_sn_total'], F[u'sn_strict_docs'],
    F[u'sn_fold_docs'], F[u'fold_total_delta']))
print(u'SOA 示例 %s ⇎ 共有字段 %d 同值 %d ｜ 大写 %s ⇎ 小写 %s ⇎ 夹括号 %s' % (
    F[u'soa_n_lines'], F[u'soa_AB_shared'], F[u'soa_AB_valshare'], F[u'soa_upper'],
    F[u'soa_lower'], F[u'soa_paren']))
print(u'搬运 归一 %s ⇎ 字节 %s ⇎ 仅归一 %s 非零对 %d ｜ 值域 %s 并集 %d 只在本份 %s 容斥闭合 %d' % (
    F[u'pair_share'], F[u'pair_byte'], F[u'pair_norm_only'], F[u'pair_nonzero'],
    F[u'set_sizes'], F[u'union_all'], F[u'only_each'], F[u'union_close']))
print(u'池 %s tier %s 闭合 %d ｜ 四份同现 %d 字节同形 %d 轴闭合 %d' % (
    F[u'pool_n'], F[u'pool_tier'], F[u'pool_tier_close'], F[u'pool_4'], F[u'share4_byte4'],
    F[u'share4_axis_close']))
print(u'窗 %s ⇎ 标题 %s ⇎ TTL 窗账 %s ⇎ cache 窗账 %s ⇎ 数字密度 %s' % (
    F[u'sec_len'], F[u'sec_head'], F[u'win_close_ttl'], F[u'win_close_cache'], F[u'digit_density']))
print(u'义务 大写 %s ⇎ 小写 %s ⇎ hereby %s ⇎ shall %s ⇎ 前三份大写零枚闭合 %d' % (
    F[u'oblig_up'], F[u'oblig_low'], F[u'hereby'], F[u'lo_shall'], F[u'up_ABC_zero']))
print(u'页壳 眉 %s ⇎ 脚 %s ⇎ 换页 %s ⇎ 文末留否 %s ⇎ 模型闭合 %s ⇎ 拖空格闭合 %s' % (
    F[u'hdr'], F[u'foot'], F[u'formfeed'], F[u'tail_ff'], F[u'ff_model_close'], F[u'trail_hdr_close']))
print(u'闭合键 %d 项 ⇎ 恒等式 %d 条 ⇎ 标量合计 %d ⇎ 清单闭合 %d' % (
    F[u'scalar_clos_n'], F[u'x_ident_n'], F[u'scalar_clos_sum'], F[u'list_clos_n']))
MEASP = u'corpus/_b68meas.json'
COLONLY = (u'tags', u'sig', u'sig_distinct')
if os.path.exists(MEASP):
    M = json.load(io.open(MEASP, encoding='utf-8'))
    TIE, MISSK = [], []
    for k in sorted(M):
        if k in COLONLY:
            continue
        if k not in F:
            MISSK.append(k)
            continue
        got = F[k]
        if isinstance(got, tuple) or (isinstance(got, list) and any(isinstance(x, tuple) for x in got)):
            got = json.loads(json.dumps(got))
        if got != M[k]:
            TIE.append((k, u'建=%s 采=%s' % (got, M[k])))
    print(u'两侧对账(四份纯文本面): 采集键 %d ／ 采集侧独有关 %d(+%d 项声明) ／ 不符 %d ｜ %s' % (
        len(M), len(MISSK), len(COLONLY), len(TIE), TIE[:12]))
    print(u'  采集侧独有(正则族/独立档, 建条目侧另立口径): %s' % (MISSK[:16],))
else:
    print(u'两侧对账: 无 corpus/_b68meas.json(采集侧未跑)')
