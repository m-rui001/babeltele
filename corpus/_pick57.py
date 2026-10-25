# -*- coding: utf-8 -*-
"""B57 第一遍(独立采集, 先于建条目写成): 只从四份在库 IETF 纯文本现量, 不重新抓取。
T = rfc5246(TLS1.2 协议, 2008-08) ⇎ O = rfc7525(BCP195 旧建议, 2015-05)
F = rfc8446(TLS1.3 协议, 2018-08) ⇎ N = rfc9325(BCP195 新建议, 2022-11, Obsoletes 7525).
本遍的轴: 同一问题(TLS 里哪些算法/套件还能用)在“协议规范⇎判决建议”两种文体、两代文书里的在场差异——
SHA-1/MD5 拼写可见度、MUST NOT 判决句的行级定位、N 点名套件在 T/F 的落点矩阵、引用方向(晚引早)与谱系。
落 corpus/_b57meas.json: {tags, paths, labels, meas, pool}. 计数一律区分大小写, 除非键注释里明说。
体例参照 _pick56.py(同项目上一遍), 但 B57 是另一批文件、另一套轴, 未照抄其量。
"""
import hashlib, io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NL = chr(10)
TAGS = [u'T', u'O', u'F', u'N']
PATHS = [u'corpus/raw/ietf/rfc5246.txt', u'corpus/raw/ietf/rfc7525.txt',
         u'corpus/raw/ietf/rfc8446.txt', u'corpus/raw/ietf/rfc9325.txt']
LABELS = {u'T': u'1.2 协议', u'O': u'旧建议', u'F': u'1.3 协议', u'N': u'新建议'}
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATHS]
LS = [t.split(NL) for t in TXT]
M = {}


def two(name, f):
    M[name] = [f(i) for i in range(4)]


DOCNUM = [int(re.search(r'\d{4}', os.path.basename(p)).group(0)) for p in PATHS]  # 5246/7525/8446/9325
MON = [u'January', u'February', u'March', u'April', u'May', u'June', u'July',
       u'August', u'September', u'October', u'November', u'December']
MYRE = re.compile(u'(%s) (20\\d\\d)' % u'|'.join(MON))
MY_STRIP = MYRE  # 引用档里剥“月-年”串用同一张月名表

# ---------- 形状档 ----------
two(u'bytes', lambda i: os.path.getsize(PATHS[i]))
two(u'chars', lambda i: len(TXT[i]))
two(u'lines', lambda i: TXT[i].count(NL))
two(u'nonblank', lambda i: len([l for l in LS[i] if l.strip()]))
two(u'blank', lambda i: len([l for l in LS[i] if not l.strip()]))
two(u'tabs', lambda i: TXT[i].count(u'\t'))
two(u'trailws', lambda i: len([l for l in LS[i] if l.endswith(u' ') or l.endswith(u'\t')]))
two(u'nonascii', lambda i: len([c for c in TXT[i] if ord(c) > 127]))
two(u'maxlen', lambda i: max(len(l) for l in LS[i]))
two(u'meanlen', lambda i: int(round(sum(len(l) for l in LS[i] if l.strip()) /
                                    max(1, len([l for l in LS[i] if l.strip()])))))
two(u'sha16', lambda i: hashlib.sha256(open(PATHS[i], 'rb').read()).hexdigest()[:16])


def strict(i):
    try:
        open(PATHS[i], 'rb').read().decode('utf-8')
        return 1
    except UnicodeDecodeError:
        return 0


two(u'utf8_strict', strict)
two(u'pagemarks', lambda i: len(re.findall(r'\[Page \d+\]', TXT[i])))
two(u'hdr', lambda i: len([l for l in LS[i] if re.match(r'^RFC \d{4}', l)]))  # 页眉行(顶栏)数
two(u'page_gap', lambda i: M[u'pagemarks'][i] - M[u'hdr'][i])  # 页标比页眉多 1(首页无顶栏); 9325 新格式两头皆 0
two(u'crlf', lambda i: TXT[i].count(u'\r'))
two(u'hdr_style', lambda i: next((l for l in LS[i] if re.match(r'^RFC \d{4}', l)), u''))
# author_hdr: 页脚行里 '[Page' 之前第一列(作者姓列)的种数——判“换页重复了多少个署名串”
two(u'author_hdr', lambda i: len(set(
    re.split(r'\s{2,}', l.strip())[0] for l in LS[i] if u'[Page' in l and l.strip())))

# ---------- 关键词档(排他口径: MUST 不含 MUST NOT 里那枚; 全量另存 kw_must_all 作闭合原料) ----------
BC = lambda pat, t: len(re.findall(pat, t))
two(u'kw_mustnot', lambda i: BC(r'\bMUST NOT\b', TXT[i]))
two(u'kw_must_all', lambda i: BC(r'\bMUST\b', TXT[i]))  # 附带原料: 判排他口径是否闭合的分母
M[u'kw_must'] = [M[u'kw_must_all'][i] - M[u'kw_mustnot'][i] for i in range(4)]
two(u'kw_shouldnot', lambda i: BC(r'\bSHOULD NOT\b', TXT[i]))
M[u'kw_should'] = [BC(r'\bSHOULD\b', TXT[i]) - M[u'kw_shouldnot'][i] for i in range(4)]
two(u'kw_may', lambda i: BC(r'\bMAY\b', TXT[i]))
two(u'kw_required', lambda i: BC(r'\brequired\b', TXT[i]))
two(u'kw_notrecommended', lambda i: BC(r'\bNOT RECOMMENDED\b', TXT[i]))
M[u'kw_recommended'] = [BC(r'\bRECOMMENDED\b', TXT[i]) - M[u'kw_notrecommended'][i] for i in range(4)]
two(u'kw_optional', lambda i: BC(r'\boptional\b', TXT[i]))  # 小写词面; 大写 OPTIONAL 不计
two(u'kw_rationale', lambda i: TXT[i].count(u'Rationale:'))
two(u'kwbullet_star', lambda i: len([l for l in LS[i] if re.match(r'^   \*  ', l)]))
two(u'kwbullet_o', lambda i: len([l for l in LS[i] if re.match(r'^   o  ', l)]))
two(u'kwbullet_num', lambda i: len([l for l in LS[i] if re.match(r'^      \d+\.  ', l)]))
# 每份的 (MUST NOT + 排他MUST) - 全集MUST, 应当全 0(排他口径闭合差)
M[u'kw_close'] = [M[u'kw_mustnot'][i] + M[u'kw_must'][i] - M[u'kw_must_all'][i] for i in range(4)]

# ---------- 拼写可见度档(子串口径, 区分大小写; net = SHA1 里刨掉 HMAC-SHA1 的净出现) ----------
two(u'sp_sha1_hy', lambda i: TXT[i].count(u'SHA-1'))
two(u'sp_sha1_plain', lambda i: TXT[i].count(u'SHA1'))
two(u'sp_hmac_sha1', lambda i: TXT[i].count(u'HMAC-SHA1'))
M[u'sp_sha1_net'] = [M[u'sp_sha1_plain'][i] - M[u'sp_hmac_sha1'][i] for i in range(4)]
two(u'sp_sha1_lower', lambda i: TXT[i].count(u'sha1'))
two(u'sp_md5_hy', lambda i: TXT[i].count(u'MD5'))
two(u'sp_md5_lower', lambda i: TXT[i].count(u'md5'))
two(u'sp_md5sha1', lambda i: TXT[i].count(u'MD5-SHA1'))
two(u'sp_sha256_hy', lambda i: TXT[i].count(u'SHA-256'))
two(u'sp_sha256_lower', lambda i: TXT[i].count(u'sha256'))
two(u'sp_sha384_hy', lambda i: TXT[i].count(u'SHA-384'))
two(u'sp_gcm_sha256', lambda i: TXT[i].count(u'GCM_SHA256'))
two(u'sp_suite_endsha', lambda i: BC(r'TLS_[A-Z0-9_]*_SHA\b', TXT[i]))  # 以裸 _SHA 结尾=SHA-1 套件全名
# 带连字符/不带(取 net)/小写 三种拼写里有几种非零
M[u'sp_case_variants'] = [sum(1 for v in (M[u'sp_sha1_hy'][i], M[u'sp_sha1_net'][i],
                                          M[u'sp_sha1_lower'][i]) if v > 0) for i in range(4)]
# 四档闭合和: hy + net(非 HMAC) + lower + hmac
M[u'sp_total_sha1_family'] = [M[u'sp_sha1_hy'][i] + M[u'sp_sha1_net'][i] +
                              M[u'sp_sha1_lower'][i] + M[u'sp_hmac_sha1'][i] for i in range(4)]

# ---------- 算法标识符档(词边界口径, 免得 dsa_sha1 被 ecdsa_sha1 蹭计) ----------
IDW = lambda i, n: BC(r'\b%s\b' % n, TXT[i])
two(u'id_rsa_pkcs1_sha1', lambda i: IDW(i, u'rsa_pkcs1_sha1'))
two(u'id_ecdsa_sha1', lambda i: IDW(i, u'ecdsa_sha1'))
two(u'id_dsa_sha1', lambda i: IDW(i, u'dsa_sha1'))
two(u'id_rsa_pkcs1_sha256', lambda i: IDW(i, u'rsa_pkcs1_sha256'))
two(u'id_rsa_pss_rsae_sha256', lambda i: IDW(i, u'rsa_pss_rsae_sha256'))
two(u'id_ecdsa_secp256r1_sha256', lambda i: IDW(i, u'ecdsa_secp256r1_sha256'))
two(u'id_rsa_pss_pss_sha256', lambda i: IDW(i, u'rsa_pss_pss_sha256'))
two(u'id_scheme_total', lambda i: BC(r'\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\(', TXT[i]))
M[u'id_sha1_schemes'] = [len([m for m in re.findall(
    r'\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\(', TXT[i]) if 'sha1' in m[:-1]]) for i in range(4)]


def legacy_block(i):
    # 仅 F: 每个 '/* Legacy algorithms */' 注释块到下一注释块(或 '}' )之间的枚举项, 多块求和
    if i != 2:
        return 0
    t, n = TXT[i], 0
    for m in re.finditer(r'/\* Legacy algorithms \*/', t):
        stop = len(t)
        for nxt in re.finditer(r'/\*|\}', t[m.end():]):
            stop = m.end() + nxt.start()
            break
        n += len(re.findall(r'\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\(', t[m.end():stop]))
    return n


two(u'id_legacy_block', legacy_block)

# ---------- 套件名跨文档矩阵(全名 = 同一行内 TLS_[A-Z0-9_]{8,} 一次到位; 72 列折行会切出悬空碎片) ----------
SUITE = [set(re.findall(r'TLS_[A-Z0-9_]{8,}', t)) for t in TXT]  # 注意: 通配 'TLS_RSA_WITH_*' 与简写也按字面入账
two(u'suite_distinct', lambda i: len(SUITE[i]))
two(u'suite_occ', lambda i: len(re.findall(r'TLS_[A-Z0-9_]{8,}', TXT[i])))
two(u'frag_tail', lambda i: len([s for s in re.findall(r'TLS_[A-Z0-9_]{8,}', TXT[i]) if s.endswith(u'_')]))


def bridge(src, dst1, dst2):
    s = SUITE[src]
    a = len(s & SUITE[dst1])
    b = len(s & SUITE[dst2])
    z = len(s - SUITE[dst1] - SUITE[dst2])
    return a, b, z, len(s), a + b + z - len(s)  # 闭合差 = (dst1∩dst2∩s) 的双重计入, 应当 0


M[u'suite_from_N_in_T'], M[u'suite_from_N_in_F'], M[u'suite_from_N_in_none'], \
    M[u'suite_N_total'], M[u'suite_bridge_close'] = bridge(3, 0, 2)
M[u'suite_from_O_in_T'], M[u'suite_from_O_in_F'], M[u'suite_from_O_in_none'], \
    M[u'suite_O_total'], M[u'suite_O_bridge_close'] = bridge(1, 0, 2)
M[u'suite_F_only'] = len(SUITE[2] - SUITE[0] - SUITE[1] - SUITE[3])
M[u'suite_T_only'] = len(SUITE[0] - SUITE[1] - SUITE[2] - SUITE[3])
M[u'suite_common_TF'] = len(SUITE[0] & SUITE[2])

# ---------- 引用与谱系档 ----------
two(u'cite_rfc_tokens', lambda i: BC(r'\bRFC ?\d{4}\b', TXT[i]))
two(u'cite_rfc_distinct', lambda i: len(set(re.findall(r'\bRFC ?(\d{4})\b', TXT[i]))))
two(u'cite_bracket', lambda i: BC(r'\[RFC\d{4}\]', TXT[i]))
# Updates:/Obsoletes: 行右侧同栏还挂着发表日期(如 8446 'Obsoletes: ... August 2018'),
# 先剥掉“月-年”串再数四位数, 判的是“列出的 RFC 编号个数”而非任意四位数(剥除表见文件头 MY_STRIP)。
two(u'cite_updates_n', lambda i: sum(len(re.findall(r'\b\d{4}\b', MY_STRIP.sub(u'', l)))
                                     for l in LS[i] if re.match(r'^Updates:', l)))
two(u'cite_obsoletes_n', lambda i: sum(len(re.findall(r'\b\d{4}\b', MY_STRIP.sub(u'', l)))
                                        for l in LS[i] if re.match(r'^Obsoletes:', l)))
PAIRS = [(a, b) for a in range(4) for b in range(4) if a != b]  # 12 个有序对
for a, b in PAIRS:
    M[u'cite_%s_to_%s' % (TAGS[a], TAGS[b])] = len(re.findall(r'\b%d\b' % DOCNUM[b], TXT[a]))
M[u'cite_pairs_nonzero'] = len([1 for a, b in PAIRS
                                if M[u'cite_%s_to_%s' % (TAGS[a], TAGS[b])] > 0])
M[u'cite_pairs_total'] = 12

# ---------- 时间档(月序数 = 年*12+月; date_raw 取页眉行里的月-年串, 9325 无页眉则取全文首个) ----------


def raw_date(i):
    hl = [l for l in LS[i] if re.match(r'^RFC \d{4}', l)]
    src = NL.join(hl) if hl else TXT[i]
    m = MYRE.search(src)
    return m.group(0) if m else u''


M[u'date_raw'] = [raw_date(i) for i in range(4)]


def _ym(i):
    m = MYRE.search(M[u'date_raw'][i])
    return int(m.group(2)) * 12 + MON.index(m.group(1)) if m else -1


M[u'date_ym'] = [[int(MYRE.search(d).group(2)), MON.index(MYRE.search(d).group(1)) + 1]
                 if d else [0, 0] for d in M[u'date_raw']]
ORDM = [_ym(i) for i in range(4)]
M[u'month_gap_prev'] = [0] + [ORDM[i] - ORDM[i - 1] for i in range(1, 4)]
M[u'month_span'] = ORDM[3] - ORDM[0]
# 文档号排序与日期排序同构 ⇔ 每个位置的秩相等
RK = lambda xs: [sorted(xs).index(x) for x in xs]
M[u'date_order_ok'] = [1 if RK(DOCNUM)[i] == RK(ORDM)[i] else 0 for i in range(4)]
# 自败引用: N 正文里 7525 的出现处数(N 的“前身”编号)
M[u'cite_self_obsoleted'] = M[u'cite_N_to_O']
# 反向引用违规: X 早于 Y 却引到 Y 的编号(成文时 Y 还不存在), 应当 0(ORDM 已在时间档算好)
M[u'cite_backward_violations'] = len([1 for a, b in PAIRS
                                      if M[u'cite_%s_to_%s' % (TAGS[a], TAGS[b])] > 0 and ORDM[a] < ORDM[b]])

# ---------- 判决句定位 ----------
two(u'line_sha_mustnot', lambda i: len([l for l in LS[i]
                                        if (u'SHA-1' in l or u'MD5' in l) and u'MUST NOT' in l]))
two(u'line_sha_mustnot_hy', lambda i: len([l for l in LS[i]
                                           if u'SHA-1' in l and u'MUST NOT' in l]))
ENUMHIT = lambda l: u'(0x' in l or u'= { 0x' in l
two(u'line_sha_in_enum', lambda i: len([l for l in LS[i] if u'sha1' in l and ENUMHIT(l)]))


def ref_block(i):
    # 可复现判法: References 章 = 标题行(^[空缩进][编号.]References$)起, 到下一个顶层标题止
    # (Appendix / Acknowledg / Authors / “N. 大写标题”且不含点编号, 故 10.1 小节不会截断)
    RS = RE = -1
    for j, l in enumerate(LS[i]):
        if re.match(r'^\s*(?:\d+\.\s+)*References\s*$', l):
            RS = j
            break
    if RS >= 0:
        RE = len(LS[i])
        for j in range(RS + 1, len(LS[i])):
            s = LS[i][j].strip()
            if re.match(r'^(?:Appendix\b|Acknowledg|Authors|\d+\.\s+[A-Z])', s):
                RE = j
                break
    return RS, RE


def in_prose(i):
    RS, RE = ref_block(i)
    n = 0
    for j, l in enumerate(LS[i]):
        if u'SHA-1' not in l or ENUMHIT(l):
            continue
        if RS >= 0 and RS <= j < RE:
            continue
        n += 1
    return n


two(u'line_sha_in_prose', in_prose)
# MUST NOT 行之后 6 行内出现 Rationale: 的(协议规范从不解释, 建议文几乎每条都解释——文体差)
two(u'line_rationale_mustnot', lambda i: len(
    [j for j, l in enumerate(LS[i]) if u'MUST NOT' in l and
     any(u'Rationale:' in LS[i][k] for k in range(j + 1, min(j + 7, len(LS[i]))))]))

# ---------- 位长门限档 ----------
# bits_* 取 “N bits” 词组(modulus 之外); modulus_* 取 “N bits”+“N-bit” 两种写法之和
two(u'bits_112', lambda i: BC(r'\b112 bits\b', TXT[i]))
two(u'bits_128', lambda i: BC(r'\b128 bits\b', TXT[i]))
two(u'bits_224', lambda i: BC(r'\b224 bits\b', TXT[i]))
two(u'bits_256', lambda i: BC(r'\b256 bits\b', TXT[i]))
two(u'modulus_2048', lambda i: BC(r'\b2048 bits\b', TXT[i]) + BC(r'\b2048-bit\b', TXT[i]))
two(u'modulus_1024', lambda i: BC(r'\b1024 bits\b', TXT[i]) + BC(r'\b1024-bit\b', TXT[i]))
two(u'curves_below_224', lambda i: TXT[i].count(u'less than 224 bits'))

# ---------- 锚候选池 ----------
TRIG = [u'SHA-1', u'sha1', u'MUST NOT', u'Rationale:', u'Obsoletes:', u'Updates:']
PN = [re.sub(u'[^a-z0-9]', u'', t.lower()) for t in TXT]  # 与 B56 门槛同口径: 归一化全文(不含空格)
CAND = []
for i in range(4):
    seen = set()

    def add(s):
        if s and (TAGS[i], s) not in seen:
            seen.add((TAGS[i], s))
            CAND.append((TAGS[i], s))

    for j, l in enumerate(LS[i]):
        s = l.strip()
        if not s:
            continue
        if len(s) >= 20:
            add(s)
        if j < 40 and re.match(r'^[0-9.]+\s+[A-Z]', s):  # 前 40 行内的章节标题行(含目录残行)
            add(s)
        if any(k in s for k in TRIG):  # 触发词整行, 哪怕短
            add(s)
POOL = []
for tag, s in CAND:
    pn = re.sub(u'[^a-z0-9]', u'', s.lower())
    nc = sum(1 for i in range(4) if pn and pn in PN[i])
    if nc >= 1 and len(s) <= 120:
        POOL.append((tag, nc, s))
POOL.sort(key=lambda x: (x[0], -x[1], -len(x[2])))
M[u'pool_n'] = len(POOL)
M[u'pool_by_tag'] = [len([x for x in POOL if x[0] == t]) for t in TAGS]
for k in (1, 2, 3, 4):
    M[u'pool_%d' % k] = len([x for x in POOL if x[1] == k])
M[u'pool_close'] = M[u'pool_1'] + M[u'pool_2'] + M[u'pool_3'] + M[u'pool_4'] - M[u'pool_n']

# ---------- 落盘 ----------
OUT = {u'tags': TAGS, u'paths': PATHS, u'labels': LABELS, u'meas': M,
       u'pool': [[a, b, c] for (a, b, c) in POOL]}
json.dump(OUT, io.open(u'corpus/_b57meas.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)

# ---------- 打印分组对照表(先打全表再做断言: 断言失败时 stdout 里已留有真实数字可看冲突) ----------
GROUPS = [
    (u'形状', [u'bytes', u'chars', u'lines', u'nonblank', u'blank', u'tabs', u'trailws',
               u'nonascii', u'maxlen', u'meanlen', u'sha16', u'utf8_strict', u'pagemarks',
               u'hdr', u'page_gap', u'crlf', u'hdr_style', u'author_hdr']),
    (u'关键词', [u'kw_mustnot', u'kw_must_all', u'kw_must', u'kw_shouldnot', u'kw_should', u'kw_may',
                u'kw_required', u'kw_notrecommended', u'kw_recommended', u'kw_optional', u'kw_rationale',
                u'kwbullet_star', u'kwbullet_o', u'kwbullet_num', u'kw_close']),
    (u'拼写可见度', [u'sp_sha1_hy', u'sp_sha1_plain', u'sp_sha1_net', u'sp_sha1_lower', u'sp_hmac_sha1',
                   u'sp_md5_hy', u'sp_md5_lower', u'sp_md5sha1', u'sp_sha256_hy', u'sp_sha256_lower',
                   u'sp_sha384_hy', u'sp_gcm_sha256', u'sp_suite_endsha', u'sp_case_variants',
                   u'sp_total_sha1_family']),
    (u'算法标识符', [u'id_rsa_pkcs1_sha1', u'id_ecdsa_sha1', u'id_dsa_sha1', u'id_rsa_pkcs1_sha256',
                   u'id_rsa_pss_rsae_sha256', u'id_ecdsa_secp256r1_sha256', u'id_rsa_pss_pss_sha256',
                   u'id_scheme_total', u'id_sha1_schemes', u'id_legacy_block']),
    (u'套件矩阵', [u'suite_distinct', u'suite_occ', u'frag_tail', u'suite_from_N_in_T', u'suite_from_N_in_F',
                 u'suite_from_N_in_none', u'suite_N_total', u'suite_bridge_close', u'suite_from_O_in_T',
                 u'suite_from_O_in_F', u'suite_from_O_in_none', u'suite_O_total', u'suite_O_bridge_close',
                 u'suite_F_only', u'suite_T_only', u'suite_common_TF']),
    (u'引用与谱系', [u'cite_rfc_tokens', u'cite_rfc_distinct', u'cite_bracket', u'cite_updates_n',
                   u'cite_obsoletes_n'] + [u'cite_%s_to_%s' % (TAGS[a], TAGS[b]) for a, b in PAIRS] +
                   [u'cite_pairs_nonzero', u'cite_pairs_total', u'cite_backward_violations',
                    u'cite_self_obsoleted']),
    (u'时间', [u'date_raw', u'date_ym', u'month_gap_prev', u'month_span', u'date_order_ok']),
    (u'判决句定位', [u'line_sha_mustnot', u'line_sha_mustnot_hy', u'line_sha_in_enum',
                   u'line_sha_in_prose', u'line_rationale_mustnot']),
    (u'位长门限', [u'bits_112', u'bits_128', u'bits_224', u'bits_256', u'modulus_2048',
                 u'modulus_1024', u'curves_below_224']),
    (u'池', [u'pool_n', u'pool_by_tag', u'pool_1', u'pool_2', u'pool_3', u'pool_4', u'pool_close']),
]
print(u'==== B57 量测对照(T=1.2协议 ⇎ O=旧建议 ⇎ F=1.3协议 ⇎ N=新建议) ====')
PERFILE = set([k for g, ks in GROUPS for k in ks]) - set([
    u'suite_from_N_in_T', u'suite_from_N_in_F', u'suite_from_N_in_none', u'suite_N_total',
    u'suite_bridge_close', u'suite_from_O_in_T', u'suite_from_O_in_F', u'suite_from_O_in_none',
    u'suite_O_total', u'suite_O_bridge_close', u'suite_F_only', u'suite_T_only', u'suite_common_TF',
    u'cite_pairs_nonzero', u'cite_pairs_total', u'cite_backward_violations', u'cite_self_obsoleted',
    u'month_span', u'pool_n', u'pool_1', u'pool_2', u'pool_3', u'pool_4', u'pool_close'] +
    [u'cite_%s_to_%s' % (TAGS[a], TAGS[b]) for a, b in PAIRS])
for gname, keys in GROUPS:
    print(u'--- %s ---' % gname)
    for k in keys:
        v = M[k]
        if isinstance(v, list) and len(v) == 4 and k in PERFILE:
            print(u'%s = %s' % (k, u' ⇎ '.join(str(x) for x in v)))
        else:
            print(u'%s = %s' % (k, json.dumps(v, ensure_ascii=False)))
print(u'meas 键数 %d ｜ pool 条数 %d ｜ 单源/两源/三源/四源 = %d/%d/%d/%d' % (
    len(M), M[u'pool_n'], M[u'pool_1'], M[u'pool_2'], M[u'pool_3'], M[u'pool_4']))

# ---------- 自校断言(末尾一轮; 键齐全 + 每份档长度 4 + 闭合差与规定值) ----------
REQ = set(k for g, ks in GROUPS for k in ks) | {u'kw_close'}
assert REQ <= set(M.keys()), [u'缺键', sorted(REQ - set(M.keys()))]
for k in PERFILE:
    assert k in M and isinstance(M[k], list) and len(M[k]) == 4, [u'长度非4', k]
assert all(x == 0 for x in M[u'kw_close']), [u'kw 排他口径不闭合', M[u'kw_close']]
assert M[u'suite_bridge_close'] == 0, [u'N 套件桥不闭合', M[u'suite_bridge_close']]
assert M[u'suite_O_bridge_close'] == 0, [u'O 套件桥不闭合', M[u'suite_O_bridge_close']]
assert M[u'pool_close'] == 0, [u'池分档不闭合', M[u'pool_close']]
assert M[u'cite_backward_violations'] == 0, [u'存在早文引晚号', M[u'cite_backward_violations']]
assert M[u'cite_pairs_total'] == 12
assert all(x == 1 for x in M[u'date_order_ok']), [u'编号-日期秩序不一致', M[u'date_order_ok']]
assert M[u'pool_n'] == sum(M[u'pool_by_tag']), [u'池按标签不闭合']
assert M[u'page_gap'] == [M[u'pagemarks'][i] - M[u'hdr'][i] for i in range(4)]
print(u'自校通过: 断言 %d 条, 全部命中规定值。' % 11)
