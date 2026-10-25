# -*- coding: utf-8 -*-
"""B68 采集侧(第一遍): 一条 RR 的 TTL 上限到底是多少、谁有权截——四份 DNS 一手文档各答一次。
口径: 纯文本面(无剥壳层), 逐行; 锚=去页壳后归一长度>=55 的长行; 写法分家按"只中和一根轴"的瀑布判。
用法: python -X utf8 corpus/_pick68.py"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')

TAGS = [u'1034', u'1035', u'1536', u'2181']
PATHS = [u'corpus/raw/dnsTTL/rfc%s.txt' % t for t in TAGS]
N = 4
MINLEN = 55

RAW = [io.open(p, encoding='utf-8', errors='replace').read() for p in PATHS]
TXT = [len(r.encode('utf-8')) for r in RAW]
CHR = [len(r) for r in RAW]
LST = [r.split(u'\n') for r in RAW]
LN = [len(l) for l in LST]
NB = [len([x for x in l if x.strip() != u'']) for l in LST]
FF = [len([x for x in l if x.strip() == u'\x0c']) for l in LST]
CR = [r.count(u'\r') for r in RAW]
NA = [len([c for c in r if ord(c) > 127]) for r in RAW]
BOM = [1 if r.startswith(u'﻿') else 0 for r in RAW]

# ---- 页壳: RFC 头行 "RFC <n> <标题> <月 年>" 上下各带分隔线; 页脚同族 ----
def is_hdr(l):
    return bool(re.match(u'^RFC \\d{4}\\s+\\S', l)) or bool(re.match(u'^\\s*[-]{20,}\\s*$', l))


def is_foot(l):
    return bool(re.match(u'^\\s*\\S+\\s+\\d{1,2}\\s*$', l)) and len(l.strip()) < 40


def pnorm(l):
    s = re.sub(u'\\s+', u' ', l.replace(u'\t', u' ').replace(u'\x0c', u' ')).strip().lower()
    s = re.sub(u'[^a-z0-9 .\\-]', u'', s)
    # 剥掉标点后可能留下首尾或连续空格: 再并一次并去两端, 与建条目侧的逐字符档同定义
    return re.sub(u' +', u' ', s).strip()


G = {}
put = lambda k, v, note: G.__setitem__(k, v) or NOTES.__setitem__(k, note)
NOTES = {}
put(u'tags', TAGS, u'四色标签')
put(u'bytes', TXT, u'磁盘字节')
put(u'chars', CHR, u'字符数')
put(u'lines', LN, u'行数(含末空行)')
put(u'nonblank', NB, u'strip 后非空的行')
put(u'ff_only', FF, u'只含换页符的行')
put(u'cr', CR, u'CR 计数')
put(u'nonascii', NA, u'非 ASCII 码点数')
put(u'bom', BOM, u'BOM')
put(u'blank_lines_extra', sum(LN) - sum(NB) - sum(FF), u'总行−非空−换页独占=纯空行数(不是恒等式, 改判据会动)')

# ---- 关键针(词面档 + 折平档) ----
NEEDLE = [
    (u'signed_word', u'signed'),
    (u'unsigned_word', u'unsigned'),
    (u'signed32', u'positive values of a signed 32 bit number'),
    (u'max_lit', u'2147483647'),
    (u'max_pow', u'2^31 - 1'),
    (u'hi31', u'less significant 31 bits'),
    (u'min0', u'minimum value of 0'),
    (u'floor_sent', u'at least the MINIMUM field of the SOA'),
    (u'here_86400', u'here 86400 seconds'),
    (u'one_day', u'or one day'),
    (u'upper_bound', u'upper bound on any TTL'),
    (u'not_mandatory', u'maximum time to live, not a mandatory time to live'),
    (u'cached_for', u'cached for TTL seconds'),
    (u'ttl_expires', u'until the TTL expires'),
    (u'cache_leak', u'Cache Leaks'),
    (u'refresh_kw', u'REFRESH'),
    (u'retry_kw', u'RETRY'),
    (u'expire_kw', u'EXPIRE'),
    (u'minimum_kw', u'MINIMUM'),
    (u'expire_week', u'expire after a week'),
    (u'min_day', u'minimum of a day'),
    (u'different_ttls', u'different TTLs'),
    (u'rrset_same', u'RRSet to have different TTLs'),
]
for k, nd in NEEDLE:
    put(u'lit_' + k, [r.count(nd) for r in RAW], u'原面直搜 %r' % nd)
    fold = re.sub(u'\\s+', u' ', nd)
    put(u'fold_' + k, [len(re.findall(re.escape(fold), re.sub(u'\\s+', u' ', r))) for r in RAW],
        u'折平(空白并一)后搜 %r' % fold)
    put(u'delta_' + k, [G[u'fold_' + k][i] - G[u'lit_' + k][i] for i in range(N)], u'折平−原面(跨行通道)')
put(u'fold_total_delta', sum(sum(G[u'delta_' + k]) for k, _ in NEEDLE), u'全部针的跨行通道合计')

# ---- SOA 五元组: 从示例区把 REFRESH/RETRY/EXPIRE/MINIMUM 的数读出来 ----
SOA = []
for i in range(N):
    rows = {}
    for l in LST[i]:
        # 示例区的五元组行有三种写法: "1800 ;refresh every 30 min"(数与注释粘连小写) / "7200 ; REFRESH"(大写带空格)
        # / "86400) ;minimum of a day"(右括号夹在数与注释之间) —— 字段名大小写两式都要吃
        m = re.match(u'^\\s*(\\d+)\\s*\\)?\\s*;\\s*(SERIAL|REFRESH|RETRY|EXPIRE|MINIMUM|'
                     u'serial|refresh|retry|expire|minimum)\\b', l, re.I)
        if m:
            rows.setdefault(m.group(2).upper(), []).append(int(m.group(1)))
    SOA.append(rows)
put(u'soa_keys', [sorted(v.keys()) for v in SOA], u'每份示例区里读到的 SOA 字段名集')
put(u'soa_vals', [dict((k, sorted(v)) for k, v in s.items()) for s in SOA], u'每份示例区的字段值多重集')
put(u'soa_n_lines', [sum(len(v) for v in s.values()) for s in SOA], u'示例区里读出的字段行数')

# ---- 时长字面集(秒) ----
DURLIT = [u'60', u'600', u'7200', u'1800', u'300', u'86400', u'172800', u'604800', u'3600000',
          u'2147483647']
put(u'dur_set', [[r.count(x) for x in DURLIT] for r in RAW], u'时长字面出现处(含切片)')
put(u'dur_distinct', [len([1 for x in DURLIT if r.count(x)]) for r in RAW], u'每份至少出现一次的时长枚数')
put(u'dur_repeat_extra', sum(sum(c) for c in G[u'dur_set']) - sum(G[u'dur_distinct']),
    u'出现处合计−命中枚数合计=同一字面的重复次')
put(u'dur_distinct_close', sum(G[u'dur_distinct']) - len([1 for i in range(N) for x in DURLIT
                                                         if G[u'dur_set'][i][DURLIT.index(x)]]), u'枚数档闭合')

# ---- SOA 字段名的写法三式: 大写带空格 ⇎ 小写粘连 ⇎ 右括号夹在数与注释之间 ----
KW = [u'SERIAL', u'REFRESH', u'RETRY', u'EXPIRE', u'MINIMUM']
put(u'soa_upper', [sum(r.count(u'; ' + k) for k in KW) for r in RAW], u'大写带空格的注释字段名出现处')
put(u'soa_lower', [sum(r.count(u';' + k.lower()) + r.count(u'; ' + k.lower()) for k in KW) for r in RAW],
    u'小写注释字段名出现处(含粘连)')
put(u'soa_paren', [len(re.findall(u'\\d+\\s*\\)\\s*;', r)) for r in RAW], u'数与注释之间夹右括号的行')
put(u'soa_case_delta', [G[u'soa_lower'][i] - G[u'soa_upper'][i] for i in range(N)], u'小写−大写')

# ---- 锚池: 去页壳的长行按归一分档 ----
CNT = {}
for i in range(N):
    for l in LST[i]:
        if len(l.strip()) >= MINLEN and not (is_hdr(l) or is_foot(l)):
            n = pnorm(l)
            if len(n) < MINLEN:
                continue
            CNT.setdefault(n, set()).add(i)
put(u'pool_n', len(CNT), u'归一长行池(去页壳, 归一后仍 >=55)')
put(u'pool_tier', [len([1 for n in CNT if len(CNT[n]) == k]) for k in range(1, N + 1)], u'池按压在几份里分档')
put(u'pool_tier_close', sum(G[u'pool_tier']) - G[u'pool_n'], u'分档闭合')

S4 = [n for n in CNT if len(CNT[n]) == N]


def raw_forms(i, norm):
    return frozenset(l for l in LST[i] if pnorm(l) == norm)


def axes_of(n):
    forms = sorted({l for i in range(N) for l in raw_forms(i, n)})
    if len(forms) < 2:
        return []
    one = lambda f: len(set(f(x) for x in forms)) == 1
    if one(lambda s: s.lower()):
        return [u'case']
    if one(lambda s: s.lower().replace(u'-', u'')):
        return [u'hyph']
    if one(lambda s: re.sub(u'\\s+', u' ', s.lower().replace(u'-', u'')).strip()):
        return [u'space']
    return [u'multi']


B4 = [n for n in S4 if set.intersection(*[set(raw_forms(i, n)) for i in range(N)])]
put(u'pool_4', len(S4), u'归一后四份同现的长行枚数')
put(u'share4_byte4', len(B4), u'其中逐字节仍同形')
put(u'share4_notbyte', len(S4) - len(B4), u'其中原面按份分家')
for ax in (u'case', u'hyph', u'space', u'multi'):
    put(u'share4_axis_' + ax, len([1 for n in S4 if axes_of(n) == [ax]]), u'只差在 %s 轴' % ax)
put(u'share4_axis_close', sum(G[u'share4_axis_' + a] for a in (u'case', u'hyph', u'space', u'multi'))
    - (len(S4) - len(B4)), u'轴账闭合')
put(u'share4_diff', sorted([[u'+'.join(axes_of(n)), n[:90]] for n in S4 if axes_of(n)]), u'分家清单')

# ---- 两两长行集之交: 行处 ⇎ 字节全等 ⇎ 仅归一同 ----
SETN = [set(pnorm(l) for l in LST[i] if len(l.strip()) >= MINLEN and not (is_hdr(l) or is_foot(l)))
        for i in range(N)]
RAWS = [set(l for l in LST[i] if len(l.strip()) >= MINLEN) for i in range(N)]
PAIR = [(a, b) for a in range(N) for b in range(a + 1, N)]
put(u'pair_share', [len(SETN[a] & SETN[b]) for a, b in PAIR], u'归一长行两两交(行处)')
put(u'pair_byte', [len(RAWS[a] & RAWS[b]) for a, b in PAIR], u'原面长行两两交(逐字节)')
put(u'pair_norm_only', [G[u'pair_share'][k] - G[u'pair_byte'][k] for k in range(len(PAIR))], u'仅归一同')
put(u'pair_close', sum(G[u'pair_share']) - sum(G[u'pair_byte']) - sum(G[u'pair_norm_only']), u'配对闭合')
put(u'tri_share', [len(SETN[a] & SETN[b] & SETN[c]) for a in range(N) for b in range(a + 1, N)
                   for c in range(b + 1, N)], u'三三交(归一长行)')
put(u'set_sizes', [len(s) for s in SETN], u'每份归一长行的值域大小')
put(u'union_all', len(set.union(*SETN)), u'归一长行并集')
put(u'only_each', [len([1 for x in SETN[i] if not any(x in SETN[j] for j in range(N) if j != i)])
                   for i in range(N)], u'只在本份的归一长行')
put(u'union_close', sum(G[u'set_sizes']) - sum(G[u'pair_share']) + sum(G[u'tri_share'])
    - G[u'pool_4'] - G[u'union_all'], u'容斥闭合: Σ单份−Σ两两+Σ三三−Σ四份−并集')

ORDER = [k for k, _ in G.items()]
io.open(u'corpus/_b68meas.json', 'w', encoding='utf-8').write(
    json.dumps(dict((k, G[k]) for k in ORDER), ensure_ascii=False, indent=0, sort_keys=True))
print(u'四色 %s ｜ 键 %d 枚' % (u' ⇎ '.join(TAGS), len(ORDER)))
print(u'字节 %s ｜ 行数 %s ｜ 非空 %s ｜ 换页独占 %s ｜ 非 ASCII %s ｜ 纯空行 %d' % (
    TXT, LN, NB, FF, NA, G[u'blank_lines_extra']))
print(u'池 %d 条, 分档 %s(闭合 %d) ｜ 四份同现 %d 条: 逐字节同形 %d ⇎ 分家 %d ｜ 轴 %s(闭合 %d)' % (
    G[u'pool_n'], G[u'pool_tier'], G[u'pool_tier_close'], G[u'pool_4'], G[u'share4_byte4'],
    G[u'share4_notbyte'], dict((a, G[u'share4_axis_' + a]) for a in (u'case', u'hyph', u'space', u'multi')),
    G[u'share4_axis_close']))
for ax, n in G[u'share4_diff']:
    print(u'  分家 %-6s :: %s' % (ax, n))
print(u'针档(原面⇎折平⇎差):')
for k, nd in NEEDLE:
    if G[u'fold_' + k] != G[u'lit_' + k]:
        print(u'  %-16s %s ⇎ %s ⇎ Δ%s' % (k, G[u'lit_' + k], G[u'fold_' + k], G[u'delta_' + k]))
print(u'关键针: signed %s ⇎ unsigned %s ⇎ 2147483647 %s ⇎ 2^31-1 %s ⇎ 高31位 %s' % (
    G[u'lit_signed_word'], G[u'lit_unsigned_word'], G[u'lit_max_lit'], G[u'lit_max_pow'], G[u'lit_hi31']))
print(u'下限句 %s ⇎ 上界句 %s ⇎ 非强制句 %s ⇎ cached for TTL %s' % (
    G[u'lit_floor_sent'], G[u'lit_upper_bound'], G[u'lit_not_mandatory'], G[u'lit_cached_for']))
print(u'SOA 字段行数 %s ｜ 值集 %s' % (G[u'soa_n_lines'], [G[u'soa_vals'][i] for i in range(N)]))
print(u'时长字面出现处 %s ｜ 命中枚数 %s ｜ 重复次 %d ｜ 枚数闭合 %d' % (
    G[u'dur_set'], G[u'dur_distinct'], G[u'dur_repeat_extra'], G[u'dur_distinct_close']))
print(u'SOA 写法三式: 大写 %s ⇎ 小写 %s ⇎ 夹括号 %s ⇎ 小写−大写 %s' % (
    G[u'soa_upper'], G[u'soa_lower'], G[u'soa_paren'], G[u'soa_case_delta']))
print(u'配对 归一 %s ⇎ 字节 %s ⇎ 仅归一 %s(闭合 %d) ｜ 三三 %s ｜ 值域 %s' % (
    G[u'pair_share'], G[u'pair_byte'], G[u'pair_norm_only'], G[u'pair_close'],
    G[u'tri_share'], G[u'set_sizes']))
print(u'并集 %d ｜ 只在本份 %s ｜ 容斥闭合 %d' % (G[u'union_all'], G[u'only_each'], G[u'union_close']))
