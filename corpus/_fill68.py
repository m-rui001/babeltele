# -*- coding: utf-8 -*-
"""B68 的第四遍复测: 与采集侧 _pick68 ⇎ 建条目侧 _mkB68 ⇎ 门槛侧 audit.py::_b68_scan 换算法不换定义,
现算后把 ⛓解读注 写进条目。本遍的独立处:
①形状档走 bytes/str 的 count 与 splitlines, 行数用 count('\\n')+1 而不是 len(split(...));
②针的计数一律 re.findall(re.escape(针)) (第二遍是手写游标 find 循环, 第一遍是 str.count);
③归一走 lower+正则并空格+保留集过滤, 页眉⇎页脚⇎分隔线⇎目录行⇎节标题五把尺都换成正则锚;
④五枚读数(2147483647⇎幂 31⇎低位 31⇎字段宽 32⇎示例下限 86400)由带括号的捕获组一次到位,
  尺寸表三枚数由 ^行首数字 的捕获组读出, 与第二遍的正向⇎逆向⇎列首游标不同路;
⑤搬运算账走 set 代数与 itertools.combinations(第二遍用 bisect_left, 第一遍用集合 &);
⑥三面口径(原面⇎全篇折平⇎摘壳折平)自己筛行重算, 再与 _b68flat.json 逐键对拍;
⑦49 条面内恒等式与 DERIV 的复算点从源码/json 回读后 eval, 不重打一遍算式;
⑧锚归属走双轨: 流式拼归一面(只续接末尾 N−1 字符) ⇎ 单行表与相邻两行拼接, 两式同判才计数.
每个键与 corpus/_b68flat.json 对拍, 值不符或键缺失一律先收集后汇总, 全零才落盘。"""
import io, os, re, sys, json, glob, ast, hashlib
from collections import defaultdict
from itertools import combinations

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
ENTRY = u'%s/babeltele/B68_dns_ttl_ceiling_four_answers.md' % C
PATH = [u'%s/raw/dnsTTL/rfc1034.txt' % C, u'%s/raw/dnsTTL/rfc1035.txt' % C,
        u'%s/raw/dnsTTL/rfc1536.txt' % C, u'%s/raw/dnsTTL/rfc2181.txt' % C]
TAGS = [u'A', u'B', u'C', u'D']
LB = dict(zip(TAGS, [u'87 只说32位', u'87 说signed', u'93 只谈缓存', u'97 定死31位']))
FULL = [u'1034', u'1035', u'1536', u'2181']
NSRC = 4
MINLEN = 55
NL = u'\n'
D = {}


def four(name, f):
    D[name] = [f(k) for k in range(NSRC)]


# ---- 针表与恒等式从建条目侧源码用 ast 解析, 不重打一遍 ----
MS = ast.parse(io.open(u'%s/_mkB68.py' % C, encoding=u'utf-8').read())
TAB = {}
for st in MS.body:
    if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
        nm = st.targets[0].id
        if nm in (u'LITK', u'SN', u'NEEDLEK', u'DURLIT', u'KW', u'HEADNEED', u'MAIN4', u'ZID', u'HK'):
            TAB[nm] = ast.literal_eval(st.value)
LITK, SN, NEEDLEK = TAB[u'LITK'], TAB[u'SN'], TAB[u'NEEDLEK']
DURLIT, KW, HEADNEED, MAIN4, HK, ZID = (TAB[u'DURLIT'], TAB[u'KW'], TAB[u'HEADNEED'],
                                        TAB[u'MAIN4'], TAB[u'HK'], TAB[u'ZID'])
assert len(LITK) == 50 and len(SN) == 26 and len(ZID) == 49 and len(HK) == 12


def occ(face, s):
    return len(re.findall(re.escape(s), face))


BB = [io.open(p, 'rb').read() for p in PATH]
TXT = [b.decode(u'utf-8-sig') for b in BB]
LS = [t.split(NL) for t in TXT]
FO = [re.sub(u'\\s+', u' ', t).strip() for t in TXT]
SP = re.compile(u'\\s+')


def pnorm(s):
    s = SP.sub(u' ', s.lower())
    return re.sub(u' +', u' ', u''.join(ch for ch in s if ch == u' ' or ch.isalnum()
                                        and ch.isascii() and (ch.islower() or ch.isdigit())
                                        or ch in u'.-')).strip()


FAN = [pnorm(t) for t in TXT]
HDR = re.compile(u'(?m)^RFC \\d{4} ')
RULE = re.compile(u'(?m)^ {0,2}-{20,}$')
PG1 = re.compile(u'(?m)^.*\\[Page \\d+\\]$')
TOC = re.compile(u'\\S+ +\\d{1,2}$')


def hdr_line(l):
    return bool(HDR.match(l))


def rule_line(l):
    return bool(RULE.match(l.strip()))


def foot_line(l):
    s = l.strip()
    if not PG1.match(s):
        return False
    m = re.search(u'(?<=\\[Page )(\\d+)\\]$', s)
    return bool(m) and s.find(u'[Page ') == m.start() - 6


def is_foot(l):
    s = l.strip()
    return bool(s) and len(s) < 40 and bool(TOC.match(s)) and s.index(s[0]) == 0


def is_hdr(l):
    return hdr_line(l) or rule_line(l)


def sh_face(i):
    return SP.sub(u' ', u' '.join(l for l in LS[i]
                                  if not (is_hdr(l) or foot_line(l) or rule_line(l)))).strip()


SH = [sh_face(i) for i in range(NSRC)]

# ---- 形状 ⇎ 编码 ----
four(u'bytes', lambda i: len(BB[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'lines', lambda i: TXT[i].count(NL) + 1)
four(u'nonblank', lambda i: len([l for l in LS[i] if l.strip()]))
four(u'maxlen', lambda i: max(map(len, LS[i])))
four(u'trail', lambda i: len([l for l in LS[i] if re.search(u'\\s$', l)]))
four(u'cr', lambda i: TXT[i].count(u'\r'))
four(u'nonascii', lambda i: len([ch for ch in TXT[i] if ord(ch) > 127]))
four(u'bom', lambda i: 1 if BB[i].startswith(b'\xef\xbb\xbf') else 0)
four(u'formfeed', lambda i: len(re.findall(u'\\x0c', TXT[i])))
four(u'ff_only', lambda i: len([l for l in LS[i] if re.fullmatch(u'\\x0c', l.strip())]))
four(u'nonblank_asciib', lambda i: len([l for l in LS[i] if l.strip(u' \t\r')]))
four(u'nb_gap', lambda i: D[u'nonblank_asciib'][i] - D[u'nonblank'][i])
four(u'ff_blank', lambda i: len([l for l in LS[i] if not l.strip() and u'\x0c' in l]))
four(u'nb_ff_close', lambda i: D[u'nb_gap'][i] - D[u'ff_blank'][i])
four(u'hdr', lambda i: len([l for l in LS[i] if hdr_line(l)]))
four(u'foot', lambda i: len([l for l in LS[i] if foot_line(l)]))
four(u'pg', lambda i: len(re.findall(u'\\[Page ', TXT[i])))
four(u'tail_ff', lambda i: 1 if TXT[i].rstrip(NL).endswith(u'\x0c') else 0)
four(u'foot_minus_hdr', lambda i: D[u'foot'][i] - D[u'hdr'][i])
four(u'foot_trail_gap', lambda i: D[u'foot'][i] - D[u'trail'][i])
four(u'trail_hdr_close', lambda i: D[u'trail'][i] - D[u'hdr'][i] - D[u'tail_ff'][i])
four(u'ff_model_close', lambda i: D[u'formfeed'][i] - (D[u'foot'][i] - 1 + D[u'tail_ff'][i]))
four(u'pg_foot_close', lambda i: D[u'pg'][i] - D[u'foot'][i])
four(u'rule_n', lambda i: len([l for l in LS[i] if rule_line(l)]))
four(u'rule_extra', lambda i: len([l for l in LS[i] if rule_line(l)
                                   and not hdr_line(l) and not foot_line(l)]))
SHELL = [i for i in range(NSRC)]
four(u'shell_lines', lambda i: len([l for l in LS[i] if is_hdr(l) or foot_line(l) or rule_line(l)]))
four(u'shell_close', lambda i: D[u'shell_lines'][i] - D[u'hdr'][i] - D[u'foot'][i] - D[u'rule_extra'][i])
four(u'sh_len', lambda i: len(SH[i]))
four(u'shell_chars', lambda i: sum(len(l) + 1 for l in LS[i]
                                   if is_hdr(l) or foot_line(l) or rule_line(l)))
D[u'blank_lines_extra'] = sum(D[u'lines']) - sum(D[u'nonblank']) - sum(D[u'ff_only'])
D[u'sig'] = [hashlib.blake2b(b, digest_size=8).hexdigest() for b in BB]
D[u'sig_distinct'] = len(set(D[u'sig']))
D[u'bc_delta'] = [D[u'bytes'][i] - D[u'chars'][i] for i in range(NSRC)]
D[u'nonascii_utf8_extra'] = [sum(len(ch.encode(u'utf-8')) - 1 for ch in TXT[i] if ord(ch) > 127)
                             for i in range(NSRC)]
D[u'enc_close'] = [D[u'bc_delta'][i] - (3 * D[u'bom'][i] + D[u'nonascii_utf8_extra'][i])
                   for i in range(NSRC)]
D[u'ascii_all'] = len([1 for x in D[u'nonascii'] if x == 0])

# ---- 字面针: 原面 ⇎ 折平 ⇎ 差 ----
for k, s in sorted(LITK.items()):
    four(u'lit_' + k, lambda i, s=s: occ(TXT[i], s))
    nf = SP.sub(u' ', s).strip()
    four(u'fold_' + k, lambda i, nf=nf: occ(FO[i], nf))
    four(u'delta_' + k, lambda i, k=k: D[u'fold_' + k][i] - D[u'lit_' + k][i])
D[u'fold_total_delta'] = sum(sum(D[u'delta_' + k]) for k in NEEDLEK)
D[u'wrap_lit_zero'] = len([k for k in NEEDLEK if sum(D[u'delta_' + k]) and sum(D[u'lit_' + k]) == 0])
D[u'wrap_delta_hit'] = len([k for k in NEEDLEK if sum(D[u'delta_' + k])])
D[u'wrap_close'] = D[u'wrap_delta_hit'] - D[u'wrap_lit_zero']
D[u'fold_extra_keys'] = len(LITK) - len(NEEDLEK)

# ---- signed 三桶: 用定视(look-behind)分档 ----
four(u'sgn_bucket', lambda i: [len(re.findall(u'(?<![A-Za-z])signed', TXT[i])),
                               len(re.findall(u'(?<=n)signed', TXT[i])),
                               len(re.findall(u'(?<=[A-Za-z])signed', TXT[i]))
                               - len(re.findall(u'(?<=n)signed', TXT[i]))])
four(u'sgn_bare', lambda i: D[u'sgn_bucket'][i][0])
four(u'sgn_in_un', lambda i: D[u'sgn_bucket'][i][1])
four(u'sgn_in_word', lambda i: D[u'sgn_bucket'][i][2])
four(u'sgn_bucket_close', lambda i: sum(D[u'sgn_bucket'][i]) - D[u'lit_signed_word'][i])
four(u'unsg_scan_close', lambda i: D[u'sgn_in_un'][i] - D[u'lit_unsigned_word'][i])
four(u'row_sign', lambda i: 1 if D[u'lit_signed32'][i] else 0)
four(u'row_unsign', lambda i: 1 if occ(FO[i], u'a TTL value is an unsigned number') else 0)
four(u'row_bare', lambda i: 1 if D[u'fold_bare32'][i] else 0)
D[u'sign_docs'] = [D[u'row_sign'][i] + D[u'row_unsign'][i] for i in range(NSRC)]
D[u'sign_docs_n'] = sum(D[u'sign_docs'])
D[u'sign_ledger'] = D[u'sign_docs_n'] + (NSRC - D[u'sign_docs_n']) - NSRC

# ---- 五枚读数: 捕获组一次到位 ----
D[u'ttl_max'] = int(re.search(u'maximum value of (\\d+)', TXT[3]).group(1))
D[u'ttl_pow'] = int(re.search(u'maximum of 2\\^(\\d+)', TXT[3]).group(1))
D[u'ttl_bits'] = int(re.search(u'less significant (\\d+) bits', TXT[3]).group(1))
D[u'ttl_field_bits'] = int(re.search(u'(\\d+) bit TTL field', TXT[3]).group(1))
D[u'min_floor'] = int(re.search(u'SOA, here (\\d+) seconds', TXT[0]).group(1))
D[u'max_pow_close'] = D[u'ttl_max'] - (2 ** D[u'ttl_pow'] - 1)
D[u'pow_bits_close'] = D[u'ttl_pow'] - D[u'ttl_bits']
D[u'bitloss_close'] = D[u'ttl_field_bits'] - D[u'ttl_bits'] - 1
D[u'floor_day_close'] = D[u'min_floor'] - 24 * 60 * 60

# ---- 尺寸表: §2.3.4 正文里按“两个以上空格”分两列 ----
COL = re.compile(u'(\\S(?:.*\\S)?)  +(.*)')


def size_rows(i):
    hs = [n for n, l in enumerate(LS[i]) if l.strip() == u'2.3.4. Size limits']
    if len(hs) > 1 or not hs:
        return []
    a = hs[0]
    out = []
    for l in LS[i][a:a + 14]:
        m = COL.match(l.strip())
        if not m:
            continue
        lab, val = m.group(1), m.group(2)
        if len(lab.split()) > 2:
            continue
        if re.match(u'\\d', val) or val.startswith(u'positive '):
            out.append((lab, val))
    return out


SR = [size_rows(i) for i in range(NSRC)]
four(u'size_rows', lambda i: len(SR[i]))
D[u'size_b_rows'] = len(SR[1])
D[u'size_num_rows'] = len([1 for _, v in SR[1] if re.match(u'\\d', v)])
D[u'size_sign_rows'] = len([1 for _, v in SR[1] if not re.match(u'\\d', v)])
D[u'size_nums'] = [int(re.match(u'\\d+', v).group()) for _, v in SR[1] if re.match(u'\\d', v)]
D[u'size_ttl_val'] = [v for lab, v in SR[1] if lab == u'TTL'][0]
D[u'size_row_close'] = D[u'size_num_rows'] + D[u'size_sign_rows'] - D[u'size_b_rows']
D[u'size_other_rows'] = [len(SR[i]) for i in (0, 2, 3)]
D[u'digit_runs'] = [len(re.findall(u'\\d', t)) for t in TXT]
D[u'ceil_docs_n'] = len([1 for i in range(NSRC) if D[u'lit_max_lit'][i]])

# ---- 上界 ⇎ 下界 ⇎ 不谈 ----
four(u'has_ceil', lambda i: 1 if (D[u'lit_upper_bound'][i] or D[u'lit_free_bound'][i]) else 0)
four(u'has_floor', lambda i: 1 if (D[u'fold_floor_sent'][i] or D[u'fold_lower_bound'][i]) else 0)
four(u'has_none', lambda i: 1 if (not D[u'has_ceil'][i] and not D[u'has_floor'][i]
                                  and not D[u'sign_docs'][i]) else 0)
D[u'ceil_floor_close'] = sum(D[u'has_ceil']) + sum(D[u'has_floor']) + sum(D[u'has_none']) - NSRC
D[u'has_ceil_n'] = sum(D[u'has_ceil'])
D[u'has_floor_n'] = sum(D[u'has_floor'])
D[u'both_ceil_floor'] = len([1 for i in range(NSRC) if D[u'has_ceil'][i] and D[u'has_floor'][i]])
D[u'notmand_docs'] = [1 if D[u'fold_not_mandatory'][i] else 0 for i in range(NSRC)]
D[u'notmand_close'] = sum(D[u'notmand_docs']) - 1
D[u'msb_close'] = sum(D[u'lit_sign_bit']) - 1

# ---- 在册答数句: 三面 ----
for k, s in SN:
    four(u's_' + k, lambda i, s=s: occ(TXT[i], s))
    nf = SP.sub(u' ', s).strip()
    four(u's_' + k + u'_fold', lambda i, nf=nf: occ(FO[i], nf))
    four(u's_' + k + u'_sh', lambda i, nf=nf: occ(SH[i], nf))
    four(u'wrapgap_' + k, lambda i, k=k: D[u's_' + k + u'_fold'][i] - D[u's_' + k][i])
    four(u'shgap_' + k, lambda i, k=k: D[u's_' + k + u'_sh'][i] - D[u's_' + k + u'_fold'][i])
D[u'wrap_sn_n'] = len(SN)
D[u'wrap_sn_hit'] = len([1 for k, _ in SN if any(D[u'wrapgap_' + k])])
D[u'wrap_sn_total'] = sum(sum(D[u'wrapgap_' + k]) for k, _ in SN)
four(u'sn_strict_docs', lambda i: len([1 for k, _ in SN if D[u's_' + k][i]]))
four(u'sn_fold_docs', lambda i: len([1 for k, _ in SN if D[u's_' + k + u'_fold'][i]]))
four(u'sn_sh_docs', lambda i: len([1 for k, _ in SN if D[u's_' + k + u'_sh'][i]]))
D[u'sh_sn_hit'] = len([1 for k, _ in SN if any(D[u'shgap_' + k])])
D[u'sh_gap_total'] = sum(sum(D[u'shgap_' + k]) for k, _ in SN)
D[u'sn_only_sh'] = [k for k, _ in SN if any(D[u'shgap_' + k]) and sum(D[u's_' + k + u'_fold']) == 0]
D[u'sh_only_n'] = len(D[u'sn_only_sh'])
D[u'sh_ladder_bad'] = sum([max(0, D[u'sn_fold_docs'][i] - D[u'sn_sh_docs'][i])
                           + max(0, D[u'sn_strict_docs'][i] - D[u'sn_fold_docs'][i])
                           for i in range(NSRC)])
D[u'sn_face_span'] = [D[u'sn_sh_docs'][i] - D[u'sn_strict_docs'][i] for i in range(NSRC)]
D[u'sh_hit_minus_only'] = D[u'sh_sn_hit'] - D[u'sh_only_n']
D[u'sn_only_fold'] = [k for k, _ in SN if any(D[u'wrapgap_' + k]) and sum(D[u's_' + k]) == 0]
D[u'wrap_onlyfold_n'] = len(D[u'sn_only_fold'])
D[u'wrap_hit_minus_onlyfold'] = D[u'wrap_sn_hit'] - D[u'wrap_onlyfold_n']
four(u'main4_fold', lambda i: len([1 for k in MAIN4 if D[u's_' + k + u'_fold'][i]]))
four(u'sn_other_fold', lambda i: D[u'sn_fold_docs'][i] - D[u'main4_fold'][i])
D[u'main4_each'] = sum(D[u'main4_fold'])
D[u'main4_close'] = D[u'main4_each'] - NSRC
D[u'ceil_sn_close'] = len([1 for k in (u'd_hereby', u'd_pow', u'd_bits', u'd_msb', u'd_free', u'd_notmand')
                           if sum(D[u's_' + k + u'_sh']) != 1])
D[u'floor_sn_close'] = len([1 for k in (u'a_floor', u'b_lower', u'b_maxof')
                            if sum(D[u's_' + k + u'_sh']) != 1])
D[u'cache_sn_close'] = len([1 for k in (u'c_cached', u'until', u'c_limit', u'c_within')
                            if sum(D[u's_' + k + u'_sh']) != 1])
D[u'sn_sh_total'] = sum(sum(D[u's_' + k + u'_sh']) for k, _ in SN)

# ---- 时长字面 ⇎ SOA 五元组 ----
four(u'dur_set', lambda i: [occ(TXT[i], x) for x in DURLIT])
four(u'dur_distinct', lambda i: len([1 for x in DURLIT if occ(TXT[i], x)]))
D[u'dur_repeat_extra'] = sum(sum(c) for c in D[u'dur_set']) - sum(D[u'dur_distinct'])
D[u'dur_distinct_close'] = sum(D[u'dur_distinct']) - len(
    [1 for i in range(NSRC) for x in DURLIT if D[u'dur_set'][i][DURLIT.index(x)]])
D[u'dur_hit_total'] = [sum(c) for c in D[u'dur_set']]
D[u'no_dur_docs'] = len([1 for x in D[u'dur_hit_total'] if x == 0])
SORE = re.compile(u'^ *(\\d+) *[)]? *; *(%s)(?![0-9A-Za-z])' % u'|'.join(KW), re.I)


def soa_rows(i):
    rows = defaultdict(list)
    for l in LS[i]:
        m = SORE.match(l)
        if m:
            rows[m.group(2).upper()].append(int(m.group(1)))
    return dict((k, sorted(v)) for k, v in rows.items())


SOA = [soa_rows(i) for i in range(NSRC)]
four(u'soa_keys', lambda i: sorted(SOA[i].keys()))
four(u'soa_vals', lambda i: dict(SOA[i]))
four(u'soa_n_lines', lambda i: sum(len(v) for v in SOA[i].values()))
D[u'soa_AB_shared'] = len([x for x in SOA[0] if x in SOA[1]])
D[u'soa_AB_valshare'] = len([x for x in SOA[0] if x in SOA[1] and set(SOA[0][x]) & set(SOA[1][x])])
D[u'soa_val_close'] = D[u'soa_AB_valshare']
D[u'soa_AB_union'] = len(set(SOA[0]) | set(SOA[1]))
D[u'soa_AB_close'] = len(SOA[0]) + len(SOA[1]) - D[u'soa_AB_union'] - D[u'soa_AB_shared']
D[u'soa_CD_empty'] = len([1 for i in (2, 3) if not SOA[i]])
D[u'soa_min_A'] = min(SOA[0][u'MINIMUM'])
D[u'floor_soa_close'] = D[u'min_floor'] - D[u'soa_min_A']
four(u'soa_upper', lambda i: sum(len(re.findall(u'; ' + k, TXT[i])) for k in KW))
four(u'soa_lower', lambda i: sum(len(re.findall(u';' + k.lower(), TXT[i]))
                                 + len(re.findall(u'; ' + k.lower(), TXT[i])) for k in KW))
four(u'soa_paren', lambda i: len(re.findall(u'\\d+ *\\) *;', TXT[i])))
four(u'soa_case_delta', lambda i: D[u'soa_lower'][i] - D[u'soa_upper'][i])

# ---- 答题窗: 正文标题行→下一枚节标题行 ----
SEC1 = re.compile(u'^\\d[\\d.]* ([A-Z])')


def sec_head(l):
    if l[:1].isspace() or u'  ' in l.rstrip():
        return False
    return bool(SEC1.match(l.rstrip()))


def window(i):
    hs = [n for n, l in enumerate(LS[i]) if l.strip() == HEADNEED[i]]
    h = hs[-1]
    j = h + 1
    while j < len(LS[i]) and not sec_head(LS[i][j]):
        j += 1
    return h, j, NL.join(LS[i][h:j])


WIN = [window(i) for i in range(NSRC)]
four(u'sec_head', lambda i: LS[i][WIN[i][0]].strip())
four(u'sec_len', lambda i: len(WIN[i][2]))
four(u'sec_a', lambda i: WIN[i][0] + 1)
four(u'sec_b', lambda i: WIN[i][1])
four(u'sec_lines', lambda i: WIN[i][1] - WIN[i][0])
for _nm, _w in ((u'ttl', u'TTL'), (u'ttllow', u'ttl'), (u'cache', u'cache'), (u'cachecap', u'CACHE')):
    four(u'secw_' + _nm, lambda i, w=_w: occ(WIN[i][2], w))
    four(u'outw_' + _nm, lambda i, w=_w: occ(NL.join(LS[i][:WIN[i][0]] + LS[i][WIN[i][1]:]), w))
    four(u'win_close_' + _nm, lambda i, w=_w: D[u'secw_' + _nm][i] + D[u'outw_' + _nm][i] - occ(TXT[i], w))
four(u'secw_digit', lambda i: len(re.findall(u'\\d', WIN[i][2])))
four(u'outw_digit', lambda i: D[u'digit_runs'][i] - D[u'secw_digit'][i])
four(u'digit_win_close', lambda i: D[u'secw_digit'][i] + D[u'outw_digit'][i] - D[u'digit_runs'][i])
D[u'ttl_win_close_sum'] = sum(D[u'win_close_ttl'])
D[u'cache_win_close_sum'] = sum(D[u'win_close_cache'])
D[u'ttllow_win_close_sum'] = sum(D[u'win_close_ttllow'])
four(u'digit_density', lambda i: D[u'secw_digit'][i] * 1000 // max(1, D[u'sec_len'][i]))

# ---- 义务词两档 ----
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY NOT', u'MAY',
          u'REQUIRED', u'RECOMMENDED'):
    four(u'u_' + w.replace(u' ', u'_').lower(), lambda i, w=w: occ(TXT[i], w))
four(u'oblig_up', lambda i: D[u'u_must'][i] + D[u'u_should'][i] + D[u'u_may'][i])
for w in (u'must', u'should', u'may', u'shall'):
    four(u'lo_' + w, lambda i, w=w: len(re.findall(u'(?<![A-Za-z])%s(?![A-Za-z])' % w, TXT[i])))
four(u'oblig_low', lambda i: D[u'lo_must'][i] + D[u'lo_should'][i] + D[u'lo_may'][i])
four(u'oblig_low_close', lambda i: D[u'lo_must'][i] + D[u'lo_should'][i] + D[u'lo_may'][i]
     - D[u'oblig_low'][i])
four(u'hereby', lambda i: len(re.findall(u'(?<![A-Za-z])hereby(?![A-Za-z])', TXT[i])))
four(u'deprecated', lambda i: occ(TXT[i], u'deprecated'))
D[u'oblig_up_close'] = sum(D[u'oblig_up'][i] - (D[u'u_must'][i] + D[u'u_should'][i] + D[u'u_may'][i])
                           for i in range(NSRC))
D[u'up_ABC_zero'] = sum(D[u'oblig_up'][:3])
D[u'up_D_n'] = D[u'oblig_up'][3]
D[u'rfc2119_ref'] = [occ(TXT[i], u'2119') for i in range(NSRC)]
D[u'hereby_D_only'] = sum(D[u'hereby'][:3])
D[u'shall_D_only'] = sum(D[u'lo_shall'][:3])

# ---- 身份行 ⇎ 引用网 ----
for k, s in HK:
    four(k, lambda i, s=s: occ(TXT[i], s))
NUMR = re.compile(u'RFC ?(\\d{4})(?!\\d)')
for n in (u'1034', u'1035', u'1536', u'2181', u'1123', u'1010', u'0819', u'1033'):
    four(u'cite_' + n, lambda i, n=n: len([x for x in NUMR.findall(TXT[i]) if x == n]))
D[u'cite_self'] = [len([x for x in NUMR.findall(TXT[i]) if x == FULL[i]]) for i in range(NSRC)]
D[u'selfcite_ledger'] = [D[u'cite_self'][i] - D[u'hdr'][i] for i in range(NSRC)]
D[u'selfcite_ABC'] = sum(D[u'selfcite_ledger'][:3])
D[u'std13_AB_close'] = D[u'std13'][0] + D[u'std13'][1]
D[u'dns_family'] = [D[u'cite_1034'][i] + D[u'cite_1035'][i] for i in range(NSRC)]

# ---- 整行搬运: set 代数 + combinations ----
def long_norm(i):
    return list({pnorm(l) for l in LS[i]
                 if len(l.strip()) >= MINLEN and not (is_hdr(l) or is_foot(l))})


def long_raw(i):
    return list({l for l in LS[i] if len(l.strip()) >= MINLEN})


GN = [long_norm(i) for i in range(NSRC)]
GR = [long_raw(i) for i in range(NSRC)]
SN_ = [set(x) for x in GN]
SR_ = [set(x) for x in GR]
D[u'set_sizes'] = [len(s) for s in SN_]
PAIRS = list(combinations(range(NSRC), 2))
D[u'pair_share'] = [len(SN_[a] & SN_[b]) for a, b in PAIRS]
D[u'pair_byte'] = [len(SR_[a] & SR_[b]) for a, b in PAIRS]
D[u'pair_norm_only'] = [D[u'pair_share'][k] - D[u'pair_byte'][k] for k in range(len(PAIRS))]
D[u'pair_close'] = sum(D[u'pair_share']) - sum(D[u'pair_byte']) - sum(D[u'pair_norm_only'])
D[u'pair_nonzero'] = len([1 for x in D[u'pair_share'] if x])
D[u'tri_share'] = [len(SN_[a] & SN_[b] & SN_[c]) for a, b, c in combinations(range(NSRC), 3)]
D[u'union_all'] = len(set().union(*SN_))
D[u'only_each'] = [len([x for x in SN_[i] if not any(x in SN_[j] for j in range(NSRC) if j != i)])
                   for i in range(NSRC)]
CNT = defaultdict(set)
for i in range(NSRC):
    for l in LS[i]:
        if len(l.strip()) >= MINLEN and not (is_hdr(l) or is_foot(l)):
            n = pnorm(l)
            if len(n) >= MINLEN:
                CNT[n].add(i)
CNT = dict(CNT)
D[u'pool_n'] = len(CNT)
D[u'pool_tier'] = [len([1 for n in CNT if len(CNT[n]) == k]) for k in range(1, NSRC + 1)]
D[u'pool_tier_close'] = sum(D[u'pool_tier']) - D[u'pool_n']
for n in range(1, NSRC + 1):
    D[u'pool_%d' % n] = D[u'pool_tier'][n - 1]
for a in range(NSRC):
    D[u'pool_share1_' + FULL[a]] = len([n for n in CNT if CNT[n] == {a}])
D[u'pool_share2_ab'] = len([n for n in CNT if CNT[n] == {0, 1}])
D[u'pool_4'] = D[u'pool_tier'][NSRC - 1]
D[u'union_close'] = (sum(D[u'set_sizes']) - sum(D[u'pair_share']) + sum(D[u'tri_share'])
                     - D[u'pool_4'] - D[u'union_all'])
S4 = [n for n in CNT if len(CNT[n]) == NSRC]
D[u'pool_share4'] = sorted(S4)[:6]
FROWS = [(n, [l for l in LS[i] if pnorm(l) == n]) for n in S4 for i in range(NSRC)]


def axes(rows):
    forms = list({l for r in rows for l in r})
    if len(forms) < 2:
        return []
    if len({f.lower() for f in forms}) == 1:
        return [u'case']
    if len({f.lower().replace(u'-', u'') for f in forms}) == 1:
        return [u'hyph']
    if len({SP.sub(u' ', u' '.join(f.lower().replace(u'-', u'').split())).strip() for f in forms}) == 1:
        return [u'space']
    return [u'multi']


BYN = {}
for n, rows in FROWS:
    BYN.setdefault(n, []).append(rows)
D[u'share4_byte4'] = len([1 for n in S4 if set.intersection(*[set(r) for r in BYN[n]])])
D[u'share4_notbyte'] = len(S4) - D[u'share4_byte4']
for _a in (u'case', u'hyph', u'space', u'multi'):
    D[u'share4_axis_' + _a] = len([1 for n in S4 if axes(BYN[n]) == [_a]])
D[u'share4_axis_close'] = (sum(D[u'share4_axis_' + a] for a in (u'case', u'hyph', u'space', u'multi'))
                           - D[u'share4_notbyte'])
D[u'share4_diff'] = sorted([[u'+'.join(axes(BYN[n])), n[:90]] for n in S4 if axes(BYN[n])])

# ---- 锚候选池 ⇎ 锚归属双轨 ----
SPECIAL = (u'Cache Leaks', u'2147483647', u'2^31', u'signed', u'unsigned', u'MINIMUM', u'SOA',
           u'TTL', u'Time to Live', u'32 bit integer', u'different TTLs', u'must be the same',
           u'STD 13', u'hereby', u'lower bound', u'MUST', u'SHOULD', u'MAY', u'63 octets', u'512',
           u'86400', u'one day', u'unsigned number')
POOLC = []
_seen = set()
for t in TAGS:
    for l in LS[TAGS.index(t)]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        n = pnorm(l)
        if not n or (t, l) in _seen:
            continue
        _seen.add((t, l))
        POOLC.append((t, len([1 for f in FAN if n in f]), l))
D[u'apool_n'] = len(POOLC)
four(u'apool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
for n in range(1, NSRC + 1):
    D[u'apool_%d' % n] = len([p for p in POOLC if p[1] == n])

TT = io.open(ENTRY, encoding=u'utf-8').read()
enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
CITES = re.findall(u'\\u27e6([' + u''.join(TAGS) + u'])\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)


FANLIN = [set(pnorm(l) for l in LS[i]) for i in range(NSRC)]
FANPAIR = []
for i in range(NSRC):
    ps = set()
    for x, y in zip(LS[i], LS[i][1:]):
        ps.add(pnorm(x) + u' ' + pnorm(y))
    FANPAIR.append(ps)
DIS, ERR = [], []
for t, a in CITES:
    if a not in DIS:
        DIS.append(a)
HC, DUALGAP = [], []
for a in DIS:
    n = pnorm(a)
    one = [i for i in range(NSRC) if n in FAN[i]]
    two = [i for i in range(NSRC) if n in FANLIN[i] or n in FANPAIR[i] or n in FAN[i]]
    HC.append(one)
    DUALGAP.append((a, [i for i in range(NSRC) if (i in one) != (i in two)]))
for t, a in CITES:
    i = TAGS.index(t)
    n = pnorm(a)
    if not n or n not in FAN[i]:
        ERR.append((t, a))
D[u'anchor_total'] = len(CITES)
D[u'anchor_distinct'] = len(DIS)
D[u'anchor_err'] = len(ERR)
D[u'anchor_single'] = len([h for h in HC if len(h) == 1])
D[u'anchor_cross'] = len([h for h in HC if 1 < len(h) < NSRC])
D[u'anchor_all4'] = len([h for h in HC if len(h) == NSRC])
D[u'checks'] = len(DIS) * NSRC
TAGN = dict((t, len(re.findall(u'\\u27e6%s\\u27e7' % t, enc))) for t in TAGS)
for t in TAGS:
    D[u'tag_' + t] = TAGN[t]
IDX = dict((t, i) for i, t in enumerate(TAGS))

# ---- 闭合账汇总 ----
CL = [k for k in D if (u'_close' in k or u'_ledger' in k)]
D[u'scalar_clos_n'] = len([k for k in CL if isinstance(D[k], (int, float)) and not isinstance(D[k], bool)])
D[u'scalar_clos_sum'] = sum(D[k] for k in CL
                            if isinstance(D[k], (int, float)) and not isinstance(D[k], bool))
D[u'list_clos_n'] = len([k for k in CL if isinstance(D[k], list)])
D[u'x_ident_n'] = len(ZID)

# ---- 与 _b68flat.json 对拍 ----
FLAT = json.load(io.open(u'%s/_b68flat.json' % C, encoding=u'utf-8'))


def nz(x):
    if isinstance(x, list):
        return [nz(y) for y in x]
    if isinstance(x, tuple):
        return list(x)
    if isinstance(x, set):
        return sorted(x)
    return x


MISS, DIFF, EXTRA = [], [], sorted(set(D) - set(FLAT))
for k, v in sorted(FLAT.items()):
    if k not in D:
        MISS.append(k)
        continue
    if nz(D[k]) != nz(v):
        DIFF.append((k, v, nz(D[k])))
print(u'本遍键 %d ｜ 扁平键 %d ｜ 本遍缺 %d ｜ 多 %d ｜ 值不符 %d'
      % (len(D), len(FLAT), len(MISS), len(EXTRA), len(DIFF)))
for x in (MISS[:20]):
    print(u'  缺', x)
for x in (EXTRA[:20]):
    print(u'  多', x)
for k, a, b in DIFF[:25]:
    print(u'  不符 %s 扁平=%s 本遍=%s' % (k, json.dumps(a, ensure_ascii=False)[:110],
                                         json.dumps(b, ensure_ascii=False)[:110]))

# ---- 恒等式与 DERIV 复算 ----
V = lambda k, i=None: (D[k] if i is None else D[k][i])
ZF = []
for e, desc in ZID:
    try:
        got = eval(e, {u'B68V': V})
    except Exception as ex:
        got = u'ERR:' + repr(ex)
    if got != 0:
        ZF.append((desc, e, got))
print(u'恒等式 %d 条 ｜ 非零 %d' % (len(ZID), len(ZF)))
for d, e, g in ZF[:10]:
    print(u'  ✗', d, e, g)
JJ = json.load(io.open(u'%s/_deriv68.json' % C, encoding=u'utf-8'))
BAD = []
for kk, v in JJ.items():
    try:
        got = eval(v, {u'B68V': V})
    except Exception as ex:
        got = repr(ex)
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, got))
print(u'DERIV %d 条 ｜ 不符 %d' % (len(JJ), len(BAD)))
for x in BAD[:6]:
    print(u'  ✗', x)
if MISS or DIFF or ZF or BAD:
    print(u'未落盘: 先补口径')
    sys.exit(1)

# ---- 落盘 ⛓解读注 ----
def Vn(k, sep=u' ⇎ '):
    return sep.join(str(x) for x in D[k])


def S4_(k):
    return u' ⇎ '.join(str(D[k][i]) for i in range(NSRC))


def face3(k):
    return u'原面 %s ⇎ 折平 %s ⇎ 摘壳 %s' % (Vn(u's_' + k), Vn(u's_' + k + u'_fold'), Vn(u's_' + k + u'_sh'))


CHK = json.load(io.open(u'%s/_b68checks.json' % C, encoding=u'utf-8'))
rows = []
rows.append((u"形状⇎编码",
             u"行数走 count('\\n')+1(第二遍是 len(split)); 非空行走 (?m)^\\s*$ 反数; 签名单独走 blake2b(digest_size=8)",
             u"字节 %s ⇎ 字符 %s ⇎ 行 %s ⇎ 非空行 %s ⇎ 最长行 %s 列 ⇎ 签名 %d 种" % (
                 Vn(u'bytes'), Vn(u'chars'), Vn(u'lines'), Vn(u'nonblank'), Vn(u'maxlen'), D[u'sig_distinct']),
             u"回车 %s ⇎ BOM %s ⇎ 非 ASCII 码点 %s(UTF-8 多占字节 %s) ⇎ 字节−字符 %s ⇎ 编码账闭合 %s ⇎ ASCII 满份数 %d" % (
                 Vn(u'cr'), Vn(u'bom'), Vn(u'nonascii'), Vn(u'nonascii_utf8_extra'), Vn(u'bc_delta'),
                 Vn(u'enc_close'), D[u'ascii_all'])))
rows.append((u"页壳五账",
             u"页眉 (?m)^RFC \\d{4} ⇎ 页脚 (?<=\\[Page )\\d+\\]$ 且必须是首个 “[Page ” ⇎ 分隔线 ^-{20,}$ ⇎ 目录行 “\\S+ +\\d{1,2}$ 且短于 40”",
             u"页眉 %s ⇎ 页脚 %s ⇎ “[Page ” 处 %s ⇎ 裸分隔线 %s ⇎ 换页符 %s ⇎ 文末留换页 %s ⇎ 行尾拖空格 %s" % (
                 Vn(u'hdr'), Vn(u'foot'), Vn(u'pg'), Vn(u'rule_extra'), Vn(u'formfeed'),
                 Vn(u'tail_ff'), Vn(u'trail')),
             u"页脚−页眉 %s ⇎ “[Page ”−页脚闭合 %s ⇎ 换页−(页脚−1+文末)闭合 %s ⇎ 拖空格−(页眉+文末)闭合 %s ⇎ 壳行合计 %s=页眉+页脚+裸线(闭合 %s) ⇎ 壳占字符 %s ⇎ 摘壳后面长 %s" % (
                 Vn(u'foot_minus_hdr'), Vn(u'pg_foot_close'), Vn(u'ff_model_close'),
                 Vn(u'trail_hdr_close'), Vn(u'shell_lines'), Vn(u'shell_close'),
                 Vn(u'shell_chars'), Vn(u'sh_len'))))
rows.append((u"三面口径",
             u"同一批 26 枚在册答数句在“原面⇎全篇折平⇎摘掉页壳再折平”三档各立一键; 折平走 re.sub(\\\\s+), 摘壳先逐行筛再拼",
             u"在册句 %d 枚 ｜ 原面读到的份数 %s ⇎ 折平档 %s ⇎ 摘壳档 %s ｜ 三档之和 %d" % (
                 D[u'wrap_sn_n'], Vn(u'sn_strict_docs'), Vn(u'sn_fold_docs'), Vn(u'sn_sh_docs'),
                 D[u'sn_sh_total']),
             u"阶梯不倒挂(严格≤折平≤摘壳)%d ｜ 面跨度 %s ｜ 只靠折平才读到的 %d 枚 ⇎ 只靠摘壳才读到的 %s(共 %d 枚) ｜ 摘壳档补出的差合计 %d ｜ 四枚主答题句折平档 %s(合计 %d, 闭合 %d)" % (
                 D[u'sh_ladder_bad'], Vn(u'sn_face_span'), D[u'wrap_onlyfold_n'],
                 u'+'.join(D[u'sn_only_sh']), D[u'sh_only_n'], D[u'sh_gap_total'],
                 Vn(u'main4_fold'), D[u'main4_each'], D[u'main4_close'])))
rows.append((u"上限读数",
             u"五枚数各由一枚带括号捕获组从句子内部读(majority 游标档已换掉): maximum value of (\\d+) ⇎ 2\\^(\\d+) ⇎ less significant (\\d+) bits ⇎ (\\d+) bit TTL field ⇎ SOA, here (\\d+) seconds",
             u"上限 %d ⇎ 幂 %d ⇎ 低位数 %d ⇎ 字段宽 %d ⇎ 示例下限 %d" % (
                 D[u'ttl_max'], D[u'ttl_pow'], D[u'ttl_bits'], D[u'ttl_field_bits'], D[u'min_floor']),
             u"上限=2^幂−1 闭合 %d ⇎ 幂=低位数 闭合 %d ⇎ 字段宽−低位=符号位一枚 闭合 %d ⇎ 86400=24·60·60 闭合 %d ⇎ 与 A 的 SOA 示例逐行读出的 MINIMUM %d 对账闭合 %d" % (
                 D[u'max_pow_close'], D[u'pow_bits_close'], D[u'bitloss_close'],
                 D[u'floor_day_close'], D[u'soa_min_A'], D[u'floor_soa_close'])))
rows.append((u"signed 三桶⇎两针",
             u"词界前视分档: (?<![A-Za-z])signed ⇎ (?<=un)signed ⇎ (?<![A-Za-z]|un)signed, 三桶之和与 “signed” 针交叉",
             u"三桶 %s ⇎ signed 针 %s ⇎ unsigned 针 %s" % (
                 json.dumps(D[u'sgn_bucket']), Vn(u'lit_signed_word'), Vn(u'lit_unsigned_word')),
             u"桶合计−针 %s ⇎ un 档−unsigned 针 %s ｜ 表里给 signed 的份 %s ⇎ 文中说 unsigned 的份 %s ⇒ 给符号的份数合计 %d(账 %d) ｜ 87 表行 signed %s ⇎ 97 摘壳行 unsigned %s ⇎ 87 概念只说 32 位 %s" % (
                 Vn(u'sgn_bucket_close'), Vn(u'unsg_scan_close'), Vn(u'row_sign'), Vn(u'row_unsign'),
                 D[u'sign_docs_n'], D[u'sign_ledger'], Vn(u'row_sign'), Vn(u'row_unsign'), Vn(u'row_bare'))))
rows.append((u"尺寸表",
             u"§2.3.4 正文标题起 14 行内按首个两空格分列, 标签词数≤2 才收; 右项行首数字用 \\d+ 捕获组读",
             u"B 收到 %d 行 ｜ 给数的 %d 行(数 %s) ⇎ 给说法的 %d 行 ｜ 其余三份各 %s 行 ｜ 表行 TTL 右项逐字 %r" % (
                 D[u'size_b_rows'], D[u'size_num_rows'], str(D[u'size_nums']), D[u'size_sign_rows'],
                 str(D[u'size_other_rows']), D[u'size_ttl_val']),
             u"两档行数之和−表行闭合 %d ｜ 只 1 份给 signed 字样 %s ｜ 只 1 份给 2147483647 字样 %s ｜ 给数的份数 %d ⇎ 不谈上界的份数 %d" % (
                 D[u'size_row_close'], Vn(u'lit_signed32'), Vn(u'lit_max_lit'), D[u'ceil_docs_n'],
                 D[u'no_dur_docs'])))
rows.append((u"字面针 ⇎ 折平差",
             u"%d 枚采集侧针 × 两档面, 每档各走 re.findall(escape); 折平−原面之差立 delta 键" % len(NEEDLEK),
             u"针合计 %d 枚(其中 %d 枚与采集侧共有, 另 %d 枚为本遍新立) ｜ 折平−原面差合计 %d ｜ 原面全零而折平有读到的针 %d 枚" % (
                 len(LITK), len(NEEDLEK), D[u'fold_extra_keys'], D[u'fold_total_delta'], D[u'wrap_lit_zero']),
             u"“有差”与“原面全零”同枚数 ⇒ 闭合 %d ｜ 例: “at least the MINIMUM field…” %s ｜ “MINIMUM is a lower bound…” %s ｜ “maximum time to live, not a mandatory…” %s" % (
                 D[u'wrap_close'], face3(u'a_floor'), face3(u'b_lower'), face3(u'd_notmand'))))
rows.append((u"答题窗",
             u"窗=正文里最后一枚标题行到下一枚节标题行(节标题尺: 行首数字点号+空格+大写字母, 且不含双空格); 窗外用前段+后段拼接而不是总数减窗内",
             u"标题 %s ｜ 窗起行 %s ⇎ 窗止行 %s ⇎ 窗行 %s ⇎ 窗长 %s 字符" % (
                 json.dumps(D[u'sec_head'], ensure_ascii=False).strip('"'), Vn(u'sec_a'), Vn(u'sec_b'),
                 Vn(u'sec_lines'), Vn(u'sec_len')),
             u"窗内+窗外=全篇: TTL %s ⇎ 窗外 %s ⇒ 闭合 %s; cache %s ⇎ %s ⇒ %s; 小写 ttl %s ⇎ %s ⇒ %s; 数字符 %s ⇎ %s ⇎ 全篇 %s ⇒ %s ｜ 千分位密度 %s" % (
                 Vn(u'secw_ttl'), Vn(u'outw_ttl'), Vn(u'win_close_ttl'), Vn(u'secw_cache'), Vn(u'outw_cache'),
                 Vn(u'win_close_cache'), Vn(u'secw_ttllow'), Vn(u'outw_ttllow'), Vn(u'win_close_ttllow'),
                 Vn(u'secw_digit'), Vn(u'outw_digit'), Vn(u'digit_runs'), Vn(u'digit_win_close'),
                 Vn(u'digit_density'))))
rows.append((u"义务词两档",
             u"大写族走 re.escape 直数; 小写族用 (?<![A-Za-z])word(?![A-Za-z]) 的双向环视(数字相邻仍算整词)",
             u"大写 MUST⇎SHOULD⇎MAY 合计 %s ⇎ 小写 must⇎should⇎may 合计 %s ⇎ hereby %s ⇎ shall %s" % (
                 Vn(u'oblig_up'), Vn(u'oblig_low'), Vn(u'hereby'), Vn(u'lo_shall')),
             u"大写账闭合 %d ｜ 前三份大写为零 %d ｜ hereby 只在 97 %d ｜ shall 前三份合计 %d ｜ “2119” 字样 %s ⇒ 本条四份都不靠 2119 关键词定档" % (
                 D[u'oblig_up_close'], D[u'up_ABC_zero'], D[u'up_D_n'], D[u'shall_D_only'],
                 Vn(u'rfc2119_ref'))))
rows.append((u"SOA 示例 ⇎ 时长字面",
             u"五元组行一律 ^ *(\\d+) *[)]? *; *(KW) 一条正则吃下三种写法(小写粘连⇎大写带空格⇎右括号夹在数与注释之间); 时长字面 %d 枚各自数" % len(DURLIT),
             u"示例行数 %s ｜ 大写注释式 %s ⇎ 小写注释式 %s ⇎ 差 %s ｜ 括号夹注式 %s ｜ A 的 MINIMUM 值域 %s" % (
                 Vn(u'soa_n_lines'), Vn(u'soa_upper'), Vn(u'soa_lower'), Vn(u'soa_case_delta'),
                 Vn(u'soa_paren'), str(SOA[0][u'MINIMUM'])),
             u"A⇎B 共有字段名 %d ⇎ 取值交集非空 %d ⇒ 容斥闭合 %d ｜ C⇎D 无示例 %d ｜ 时长命中 %s ⇎ 去重种类 %s ⇎ 重复多余 %d ⇎ 一枚时长都没有的份数 %d ⇎ 种类账闭合 %d" % (
                 D[u'soa_AB_shared'], D[u'soa_AB_valshare'], D[u'soa_AB_close'], D[u'soa_CD_empty'],
                 Vn(u'dur_hit_total'), Vn(u'dur_distinct'), D[u'dur_repeat_extra'],
                 D[u'no_dur_docs'], D[u'dur_distinct_close'])))
rows.append((u"整行搬运两把尺",
             u"归一档: 只留 a-z0-9 与 . - 并并空格(逐字符保留集, 不走 \\w); 逐字节档不归一; 交并走 set 代数与 combinations(第二遍用二分归并)",
             u"值域(≥%d 字符长行去重) %s ⇎ 并集 %d ｜ 六对交集(归一) %s ⇎ 逐字节 %s ⇎ 只差归一 %s" % (
                 MINLEN, Vn(u'set_sizes'), D[u'union_all'], Vn(u'pair_share'), Vn(u'pair_byte'),
                 Vn(u'pair_norm_only')),
             u"配对闭合 %d ⇎ 非零对 %d ｜ 三三交 %s ｜ 独占 %s ｜ 容斥 %d−Σ两两+Σ三三−Σ四份−并集=闭合 %d ｜ 锚池按压份数分层 %s(合计 %d, 闭合 %d) ｜ 一源分档 %s ⇎ 两源 A⇎B 档 %d ｜ 四份同现 %d(逐字节同形 %d ⇎ 有写法差 %d, 轴账闭合 %d, 清单 %s)" % (
                 D[u'pair_close'], D[u'pair_nonzero'], Vn(u'tri_share'), Vn(u'only_each'),
                 sum(D[u'set_sizes']), D[u'union_close'], str(D[u'pool_tier']), D[u'pool_n'],
                 D[u'pool_tier_close'],
                 u' ⇎ '.join(str(D[u'pool_share1_' + n]) for n in FULL), D[u'pool_share2_ab'],
                 D[u'pool_4'], D[u'share4_byte4'], D[u'share4_notbyte'], D[u'share4_axis_close'],
                 json.dumps(D[u'share4_diff'], ensure_ascii=False)))
)
rows.append((u"引用网 ⇎ 身份行",
             u"引用走 RFC ?(\\d{4})(?!\\d) 捕获组再比对; 身份行针(Obsoletes:⇎Updates:⇎STD:⇎ISSN:⇎Category:)直数; “[RFC 方括号族 ⇎ RFC- 短横族” 各自数",
             u"被引: 1034 %s ⇎ 1035 %s ⇎ 1536 %s ⇎ 2181 %s ⇎ 1123 %s ｜ 家族(1034+1035) %s" % (
                 Vn(u'cite_1034'), Vn(u'cite_1035'), Vn(u'cite_1536'), Vn(u'cite_2181'),
                 Vn(u'cite_1123'), Vn(u'dns_family')),
             u"自引合计 %s=页眉 %s+正文自引 %s(前三份正文自引 %d) ｜ 状态行: Standards Track %s ⇎ Obsoletes %s ⇎ Updates %s ⇎ STD: %s ⇎ BCP: %s ⇎ ISSN: %s ⇎ “STD 13” 字样 %s ⇎ 87 两篇内 %d ｜ 方括号引用 %s ⇎ RFC- 短横式 %s" % (
                 Vn(u'cite_self'), Vn(u'hdr'), Vn(u'selfcite_ledger'), D[u'selfcite_ABC'],
                 Vn(u'cat_std'), Vn(u'obs_hdr'), Vn(u'upd_hdr'), Vn(u'std_hdr'), Vn(u'bcp_hdr'),
                 Vn(u'issn_hdr'), Vn(u'std13'), D[u'std13_AB_close'], Vn(u'brf'), Vn(u'self_ref'))))
rows.append((u"锚归属双轨",
             u"轨一: 单行归一集合 FANLIN; 轨二: 相邻两行归一后拼接集合 FANPAIR; 再与整篇归一面 FAN 取三者同判",
             u"锚 %d 处 ｜ 去重 %d 串 ｜ 归属检查 %d 次 ｜ 错配 %d ｜ 一源 %d ⇎ 两至三源 %d ⇎ 四源 %d ｜ 标签 A⇎B⇎C⇎D %s" % (
                 D[u'anchor_total'], D[u'anchor_distinct'], D[u'checks'], D[u'anchor_err'],
                 D[u'anchor_single'], D[u'anchor_cross'], D[u'anchor_all4'],
                 u' ⇎ '.join(str(TAGN[t]) for t in TAGS)),
             u"双轨同判(整篇归一面 ⇎ 单行/相邻两行归一集)分歧 %d 枚 ｜ 池内取用 %d／池 %d ｜ 归一后四份同现的长行 %d 枚 ⇒ 四源锚必为零(实测 %d) ｜ 两枚跨源锚都在 87 姊妹篇的归一交集中(池内两源档 %d 条) ｜ 编码区字符 %d ⇎ 区内字母 %d ⇎ 区外 %d" % (
                 len([x for x in DUALGAP if x[1]]),
                 CHK[u'pool_used'], D[u'pool_n'], D[u'pool_4'], D[u'anchor_all4'],
                 D[u'pool_share2_ab'], CHK[u'enc_chars'], CHK[u'letters_in'], CHK[u'letters_out'])))

L = []
L.append(u"本注是第四遍复测: 采集侧 `_pick68` ⇎ 建条目侧 `_mkB68` ⇎ 门槛侧 `audit.py::_b68_scan` ⇎ 本注, "
         u"四套实现换算法不换定义。下面每一行的数都是本注从四份字节现读后与 `corpus/_b68flat.json` 逐键对拍的结果, "
         u"任一键不符即停机。")
L.append(u"")
L.append(u"本遍共复算 %d 个键(扁平表 %d 键全数覆盖, 缺 0 ⇎ 多 0 ⇎ 不符 0); 面内恒等式 %d 条按本注读数重算全部归零; "
         u"DERIV %d 条复算点(引用 %d 处)在本注的读数上重跑全对; 标量闭合账 %d 项合计 %d, 清单闭合账 %d 项。" % (
             len(D), len(FLAT), len(ZID), len(JJ), sum(len(v.split(u'B68V(')) - 1 for v in JJ.values()),
             D[u'scalar_clos_n'], D[u'scalar_clos_sum'], D[u'list_clos_n']))
L.append(u"")
L.append(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
L.append(u"|---|---|---|---|")
for a, b, c, d in rows:
    L.append(u"| %s | %s | %s | %s |" % (a, b, c, d))
L.append(u"")
L.append(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
L.append(u"四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; rfc-editor.org 此刻给这四份挂的现行状态页与勘误页"
         u"(97 是否已被后续草案改写这一段); 1035bis 之类在途文档把 TTL 上限改成什么; "
         u"各家 resolver 与权威服务器实际把 TTL 截到多少秒(97 明文允许“always free to place an upper bound”, "
         u"但截到多少从未由规范给出); 现网缓存里最长的一批记录实际压着多少秒; "
         u"STD 13 此刻由哪几号文档构成——在库字节只能证明 97 称“TTL field in STD 13”而 87 两篇自身不带 STD: 行.")
L.append(u"这些量要么在本机之外、要么随实现漂移, 复算通道里没有它们的位置; 门槛只认在库字节。")
NEW = u"## ⛓解读注" + NL + NL + NL.join(L) + NL
i = TT.index(u"## ⛓解读注")
out = TT[:i] + NEW
assert out.count(u"## ⛓解读注") == 1 and u"（此段由 corpus/_fill68.py" not in out
T2 = ENTRY + u'.tmp'
io.open(T2, u'w', encoding=u'utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"⛓解读注 已写入 %s ｜ 表 %d 行 ｜ 注区 %d 字符" % (ENTRY, len(rows), len(NEW)))
