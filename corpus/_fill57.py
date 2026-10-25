# -*- coding: utf-8 -*-
"""B57 ⛓解读注: 这段里的每个数由本脚本现测并 assert, 不手填。
四套实现: 采集侧 corpus/_pick57.py(先于条目写成, 落 corpus/_b57meas.json) ⇎ 建条目侧 corpus/_mkB57.py(落扁平契约
corpus/_b57flat.json, 与采集侧在 TIE 表上逐量对账) ⇎ 审计器侧 corpus/audit.py::_b57_scan()(快照落 corpus/_b57audit.json)
⇎ 本注自己从四份 raw 现取的第四遍。
必须披露的一处非独立性: _b57_scan 的量测段是从 _mkB57.py 的 SCAN 段机械抽出后插进门槛的(见 corpus/_wire57.py),
所以它的独立性不来自“另写一遍”, 而来自 ①采集侧与本注是两套真独立实现, ②插门前 _b57flat.json 的每个键与 DERIV['B57']
的每条算式都在抽出体上预演过, 值不符即停机。
四份字节的磁盘 mtime 与各页眉自写的月份谁新谁旧只在本机成立: 本注测它、写它、并写明它不进门槛。"""
import glob, io, json, os, re, subprocess, sys, time
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B57_four_documents_one_hash_verdict.md')
M = json.load(io.open(os.path.join(C, u'_b57meas.json'), encoding='utf-8'))
CH = json.load(io.open(C + u'/_b57checks.json', encoding='utf-8'))
DJ = json.load(io.open(C + u'/_deriv57.json', encoding='utf-8'))
FLAT = json.load(io.open(C + u'/_b57flat.json', encoding='utf-8'))
ATOMP = os.path.join(C, u'_atoms57.txt')
ATOMS = [x for x in io.open(ATOMP, encoding='utf-8').read().split(NL) if x.strip()]
MEAS, TAGS, PATHS = M[u'meas'], M[u'tags'], M[u'paths']
AMET = CH[u'ameta']
LB = dict(zip(TAGS, [u'1.2 协议', u'旧建议', u'1.3 协议', u'新建议']))
MON = [u'January', u'February', u'March', u'April', u'May', u'June', u'July', u'August',
       u'September', u'October', u'November', u'December']

# ---------- 审计器自己的快照 ----------
SNAP = os.path.join(C, u'_b57audit.json')
code = (u"import sys,json,io;sys.path.insert(0,'corpus');import audit;"
        u"A=[x.rstrip(chr(10)) for x in io.open(sys.argv[2],encoding='utf-8') if x.strip()];"
        u"json.dump({'B57':audit._B57,'SRC':dict((k,list(v)) for k,v in audit.SRC.items()),"
        u"'PN':[audit.prose_norm(a) for a in A]},"
        u"open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False)")
r = subprocess.run([sys.executable, u'-X', u'utf8', u'-c', code, SNAP, ATOMP],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-800:]
JJ = json.load(io.open(SNAP, encoding='utf-8'))
A, SRCALL = JJ[u'B57'], JJ[u'SRC']


def rnd(v):
    if isinstance(v, (dict, list)):
        return [rnd(x) for x in v] if isinstance(v, list) else dict((k, rnd(x)) for k, x in v.items())
    if isinstance(v, str):
        return v
    return round(float(v), 4)


MISS = [k for k in sorted(FLAT) if k not in A]
DIFF = [(k, FLAT[k], A[k]) for k in sorted(FLAT) if rnd(FLAT[k]) != rnd(A[k])]
assert not MISS, MISS
assert not DIFF, DIFF[:6]
TIE = sorted([k for k in FLAT if k in MEAS])
DTIE = [(k, FLAT[k], MEAS[k]) for k in TIE if rnd(FLAT[k]) != rnd(MEAS[k])]
assert not DTIE, DTIE[:6]

# ---------- 本注的第四遍 ----------
# 读法就不同: 先按字节读再 decode, 不用 io.open(encoding=); 分行用 splitlines, 不用 split(NL)
TXT = [io.open(p, 'rb').read().decode('utf-8', u'replace') for p in PATHS]
LS = [t.splitlines() for t in TXT]
pn = lambda s: re.sub(u'[^a-z0-9]', u'', s.lower())
W = lambda t, w: len(re.findall(u'(?<![A-Za-z0-9_])' + w + u'(?![A-Za-z0-9_])', t))
Q4 = {}


def _strict(p):
    try:
        io.open(p, encoding='utf-8').read()
        return 1
    except UnicodeDecodeError:
        return 0


def q(name, val):
    """现取一个量并与契约对账: 键名即契约键名, 值必须逐元素相同(不在契约里的键只登记不比对)。"""
    Q4[name] = val
    if name in FLAT:
        assert rnd(val) == rnd(FLAT[name]), (name, val, FLAT[name])
    return val


# 形状档
q(u'bytes', [os.path.getsize(p) for p in PATHS])
q(u'chars', [len(t) for t in TXT])
q(u'lines', [t.count(NL) for t in TXT])
q(u'nonblank', [sum(1 for l in LS[i] if l.strip()) for i in range(4)])
q(u'maxlen', [max(len(l) for l in LS[i]) for i in range(4)])
q(u'tabs', [t.count(u'\t') for t in TXT])
q(u'trailws', [sum(1 for l in LS[i] if l[-1:] in (u' ', u'\t')) for i in range(4)])
q(u'nonascii', [sum(1 for c in t if ord(c) > 127) for t in TXT])
q(u'crlf', [t.count(u'\r') for t in TXT])
q(u'bom', [1 if t[:1] == u'\ufeff' else 0 for t in TXT])
q(u'utf8_strict', [1 if _strict(p) else 0 for p in PATHS])
q(u'sha_distinct', len(set(__import__('hashlib').sha256(io.open(p, 'rb').read()).hexdigest()[:16]
                          for p in PATHS)))

# 强度词八档: lookaround 正则(建条目侧用逐次 find 扫描, 采集侧用 TXT.count)
mn, sa, ra = [W(t, u'MUST NOT') for t in TXT], [W(t, u'SHOULD NOT') for t in TXT], [W(t, u'NOT RECOMMENDED') for t in TXT]
ma, aa, ra2 = [W(t, u'MUST') for t in TXT], [W(t, u'SHOULD') for t in TXT], [W(t, u'RECOMMENDED') for t in TXT]
q(u'kw_mustnot', mn)
q(u'kw_must', [ma[i] - mn[i] for i in range(4)])
q(u'kw_shouldnot', sa)
q(u'kw_should', [aa[i] - sa[i] for i in range(4)])
q(u'kw_notrecommended', ra)
q(u'kw_recommended', [ra2[i] - ra[i] for i in range(4)])
q(u'kw_may', [W(t, u'MAY') for t in TXT])
q(u'kw_required', [W(t, u'required') for t in TXT])
q(u'kw_optional', [W(t, u'optional') for t in TXT])
q(u'kw_rationale', [t.count(u'Rationale:') for t in TXT])
q(u'kwbullet_o', [sum(1 for l in LS[i] if re.match(u'^   o {2}', l)) for i in range(4)])
q(u'kwbullet_star', [sum(1 for l in LS[i] if re.match(u'^   [*] {2}', l)) for i in range(4)])
q(u'kw_mix_docs', sum(1 for i in range(4) if Q4[u'kwbullet_o'][i] and Q4[u'kwbullet_star'][i]))
q(u'kw_bullets_onlyone', sum(1 for i in range(4) if bool(Q4[u'kwbullet_o'][i]) != bool(Q4[u'kwbullet_star'][i])))

# 拼写可见度: 纯子串档用 str.count(建条目侧是 find 循环)
for k, w in ((u'sp_sha1_hy', u'SHA-1'), (u'sp_sha1_plain', u'SHA1'), (u'sp_hmac_sha1', u'HMAC-SHA1'),
             (u'sp_sha1_lower', u'sha1'), (u'sp_md5_hy', u'MD5'), (u'sp_md5sha1', u'MD5-SHA1'),
             (u'sp_sha256_hy', u'SHA-256'), (u'sp_sha384_hy', u'SHA-384'), (u'sp_gcm_sha256', u'GCM_SHA256')):
    q(k, [t.count(w) for t in TXT])
q(u'sp_sha1_net', [Q4[u'sp_sha1_plain'][i] - Q4[u'sp_hmac_sha1'][i] for i in range(4)])
q(u'sp_case_variants', [sum(1 for v in (Q4[u'sp_sha1_hy'][i], Q4[u'sp_sha1_net'][i],
                                        Q4[u'sp_sha1_lower'][i]) if v > 0) for i in range(4)])
q(u'sp_total_sha1_family', [Q4[u'sp_sha1_hy'][i] + Q4[u'sp_sha1_net'][i] + Q4[u'sp_sha1_lower'][i]
                            + Q4[u'sp_hmac_sha1'][i] for i in range(4)])

# 页式档: 逐行含 “[Page ” 判(建条目侧是整篇字符扫描, 采集侧是 \\[Page \\d+\\] 正则)
q(u'pagemarks', [sum(1 for l in LS[i] if u'[Page ' in l) for i in range(4)])
q(u'hdr', [sum(1 for l in LS[i] if re.match(u'^RFC \\d{4}', l)) for i in range(4)])
q(u'page_gap', [Q4[u'pagemarks'][i] - Q4[u'hdr'][i] for i in range(4)])
q(u'author_hdr', [len(set(l.split()[-1] for l in LS[i] if l[:4] == u'RFC ')) for i in range(4)])

# 判决行与门限行: 逐行布尔积
q(u'line_sha_mustnot', [sum(1 for l in LS[i] if u'MUST NOT' in l and (u'SHA-1' in l or u'MD5' in l))
                        for i in range(4)])
q(u'line_sha_in_enum', [sum(1 for l in LS[i] if u'sha1' in l and u'(0x' in l) for i in range(4)])
q(u'line_rationale_mustnot', [sum(1 for k in range(len(LS[i])) if u'MUST NOT' in LS[i][k]
                                  and any(u'Rationale:' in LS[i][j]
                                          for j in range(k, min(k + 7, len(LS[i]))))) for i in range(4)])
for k, w in ((u'bits_112', u'112 bits'), (u'bits_128', u'128 bits'), (u'bits_192', u'192 bits'),
             (u'bits_224', u'224 bits')):
    q(k, [W(t, w) for t in TXT])
q(u'modulus_2048', [W(t, u'2048-bit') + W(t, u'2048 bits') for t in TXT])
q(u'curves_below_224', [t.count(u'less than 224 bits') for t in TXT])
q(u'fwd_secrecy', [t.count(u'forward secrecy') for t in TXT])
q(u'ssl_v2_ban', [sum(1 for l in LS[i] if u'MUST NOT negotiate SSL version 2' in l) for i in range(4)])

# 套件名: {8,} 量词正则(建条目侧手工扩字符)
SUIT4 = [re.findall(u'TLS_[A-Z0-9_]{8,}', t) for t in TXT]
SU4 = [set(x) for x in SUIT4]
q(u'suite_distinct', [len(x) for x in SU4])
q(u'suite_occ', [len(x) for x in SUIT4])
q(u'frag_tail', [sum(1 for s in SUIT4[i] if s.endswith(u'_')) for i in range(4)])
q(u'sp_suite_endsha', [sum(1 for s in SUIT4[i] if s.endswith(u'_SHA')) for i in range(4)])
q(u'suite_common_TF', len(SU4[0] & SU4[2]))
q(u'suite_common_ON', len(SU4[1] & SU4[3]))
q(u'suite_T_only', len(SU4[0] - SU4[1] - SU4[2] - SU4[3]))
q(u'suite_F_only', len(SU4[2] - SU4[0] - SU4[1] - SU4[3]))
q(u'suite_endsha_T', len([s for s in SU4[0] if s.endswith(u'_SHA')]))
for s, dn, d2, pre in ((3, 0, 2, u'suite_from_N'), (1, 0, 2, u'suite_from_O')):
    q(pre + u'_in_T', len(SU4[s] & SU4[dn]))
    q(pre + u'_in_F', len(SU4[s] & SU4[d2]))
    q(pre + u'_in_none', len(SU4[s] - SU4[dn] - SU4[d2]))
    q(pre + u'_total', len(SU4[s]))

# 引用与时间: lookaround 数号码(建条目侧逐字符扫描, 采集侧 \\b\\d{4}\\b)
DOCN = [5246, 7525, 8446, 9325]
PAIR4 = {}
for a in range(4):
    for b in range(4):
        if a != b:
            PAIR4[(a, b)] = len(re.findall(u'(?<![A-Za-z0-9])%d(?![A-Za-z0-9])' % DOCN[b], TXT[a]))
q(u'cite_pairs_total', len(PAIR4))
q(u'cite_pairs_nonzero', len([1 for v in PAIR4.values() if v]))
q(u'cite_pairs_zero', len([1 for v in PAIR4.values() if not v]))
q(u'cite_pairs_occ', sum(PAIR4.values()))
for (a, b), v in PAIR4.items():
    q(u'cite_%s_to_%s' % (TAGS[a], TAGS[b]), v)
MONY = u'(%s) (\\d{4})' % u'|'.join(MON)
YM4 = []
for i in range(4):
    c = Counter(re.findall(MONY, TXT[i][:6000]))
    m = c.most_common(1)[0][0]
    YM4.append((int(m[1]), MON.index(m[0]) + 1))
q(u'date_raw', [u'%s %d' % (MON[b - 1], a) for a, b in YM4])
q(u'month_num', [a * 12 + b for a, b in YM4])
q(u'month_span', Q4[u'month_num'][3] - Q4[u'month_num'][0])
q(u'date_seg_n', sum(1 for i in range(1, 4) if YM4[i] > YM4[i - 1]))
BKV = len([k for k, v in PAIR4.items() if v and YM4[k[1]] > YM4[k[0]]])
q(u'cite_backward_violations', BKV)

# 搬运: 同一判据(去空白归一的整行集求交 ⇎ lookahead 断句)换算法——先建字典再取键
def normset(i):
    d = {}
    for l in LS[i]:
        s = l.strip()
        if len(s) >= 20:
            d[pn(s)] = s
    return set(d)


NO, NN_ = normset(1), normset(3)
q(u'carry_line_o', len(NO))
q(u'carry_line_n', len(NN_))
q(u'carry_shared', len(NO & NN_))
q(u'carry_union', len(NO | NN_))
q(u'carry_only_o', len(NO - NN_))
q(u'carry_only_n', len(NN_ - NO))


def blob(i):
    return u' '.join(TXT[i].split())


SO4 = set(s.strip() for s in re.split(u'(?<=[.:;]) (?=[A-Z])', blob(1)) if len(s.strip()) >= 20)
SN4 = set(s.strip() for s in re.split(u'(?<=[.:;]) (?=[A-Z])', blob(3)) if len(s.strip()) >= 20)
q(u'carry_sent_o', len(SO4))
q(u'carry_sent_n', len(SN4))
q(u'carry_sent_shared', len(SO4 & SN4))
q(u'carry_sent_rat', len([x for x in SO4 & SN4 if u'Rationale:' in x]))
q(u'carry_thr_192', len([x for x in SO4 & SN4 if u'192 bits' in x]))
q(u'carry_thr_224', len([x for x in SO4 & SN4 if u'224 bits' in x]))
RAW4 = [x for x in LS[1] if x.strip() and len(x.strip()) >= 20 and pn(x.strip()) in NN_]
R4 = len([x for x in RAW4 if u'[RFC' in x])
T4 = len([x for x in RAW4 if u'[RFC' not in x and re.match(u'^\\d+(\\.\\d+)*\\s+\\S', x.strip())])
q(u'carry_shared_raw', len(RAW4))
q(u'carry_shared_ref', R4)
q(u'carry_shared_toc', T4)
q(u'carry_shared_prose', len(RAW4) - R4 - T4)
# 与契约同判据: 先取“去重后的 ≥20 字符整行”, 再判它的归一串是否在新文里再现
FOUR4 = [set(l.strip() for l in LS[i] if len(l.strip()) >= 20) for i in range(4)]
q(u'carry_o_in_n_text', sum(1 for x in FOUR4[1] if pn(x) and pn(x) in pn(TXT[3])))
q(u'carry_n_in_o_text', sum(1 for x in FOUR4[3] if pn(x) and pn(x) in pn(TXT[1])))
q(u'carry_sub_overlap', Q4[u'carry_o_in_n_text'] + Q4[u'carry_n_in_o_text'])

# 枚举与遗留块: 按注释块起讫切子串再数(建条目侧用 finditer 配 “下一个 /* 或 }” 定界)
LEG4 = []
for i in range(4):
    t = TXT[i]
    n = 0
    for m in re.finditer(u'/\\* Legacy algorithms \\*/', t):
        stop = t.find(u'/*', m.end() + 1)
        n += len(re.findall(u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\\(',
                            t[m.end():stop if stop > 0 else len(t)]))
    LEG4.append(n)
q(u'id_legacy_block', LEG4)
for k, w in ((u'id_rsa_pkcs1_sha1', u'rsa_pkcs1_sha1'), (u'id_ecdsa_sha1', u'ecdsa_sha1'),
             (u'id_dsa_sha1', u'dsa_sha1'), (u'id_rsa_pkcs1_sha256', u'rsa_pkcs1_sha256'),
             (u'id_rsa_pss_rsae_sha256', u'rsa_pss_rsae_sha256'),
             (u'id_ecdsa_secp256r1_sha256', u'ecdsa_secp256r1_sha256')):
    q(k, [W(t, w) for t in TXT])
q(u'id_dsa_sha1_text', [t.count(u'dsa_sha1') for t in TXT])
q(u'id_scheme_total', [len(re.findall(u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\\(', t)) for t in TXT])
q(u'id_sha1_schemes', [len([m for m in re.findall(u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\\(', t)
                            if u'sha1' in m[:-1]]) for t in TXT])
q(u'id_enum_lines', [sum(1 for l in LS[i] if u'(0x' in l
                         and re.search(u'\\b(?:rsa|ecdsa|eddsa|dsa)\\w*\\(', l)) for i in range(4)])
MSS4 = re.search(u'A TLS-compliant application MUST support digital signatures with(.{0,400}?)secp256r1',
                 TXT[2], re.S)
MS4 = re.findall(u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+', MSS4.group(1)) if MSS4 else []
q(u'id_must_support_n', len(MS4))
q(u'id_must_support_sha1', len([x for x in MS4 if u'sha1' in x]))
QN = len(Q4)
QE = sum(len(v) if isinstance(v, list) else 1 for v in Q4.values())

# 指纹与本机时刻(旁证, 不进门槛)
SHA = [__import__('hashlib').sha256(io.open(p, 'rb').read()).hexdigest() for p in PATHS]
MT = [os.path.getmtime(p) for p in PATHS]
DAYS = [(time.mktime(time.strptime(u'%d-%02d-15' % (a, b), u'%Y-%m-%d')) - m) / 86400.0
        for m, (a, b) in zip(MT, YM4)]

NT = []
add = lambda s: NT.append(s)

add(u'- 四套实现与一处非独立: 采集侧 _pick57.py ⇎ 建条目侧 _mkB57.py(扁平契约 %d 键, 与采集侧共有 %d 个量, '
    u'本注重跑仍是不符 %d 个) ⇎ 门槛内 _b57_scan()。本注是第四遍: 契约 %d 键逐个与审计器快照对齐(不符即停机), '
    u'另自行从四份字节现取 %d 个量(共 %d 个数)并与契约逐一对账: 形状档走 splitlines 与字节 decode, '
    u'强度词八档走 lookaround 正则(建条目侧是逐次 find 扫描, 采集侧是 TXT.count), 拼写九档走 str.count, '
    u'页标走“逐行含 [Page ”, 页眉走 ^RFC \\d{4}, 判决行走逐行布尔积, 套件名走 TLS_[A-Z0-9_]{8,} 量词正则 '
    u'(建条目侧手工扩字符), 引用 12 对走号码 lookaround, 搬运的整行集先建字典再取键、断句改用 (?<=[.:;]) (?=[A-Z]) '
    u'的正则切, 遗留块按 “下一个 /*” 定界。换路子不是为了让数不同, 而是为了证明这些数不依赖某一种切法。'
    % (len(FLAT), len(TIE), len(DTIE), len(FLAT), QN, QE))
add(u'- _b57_scan 的量测段由 _wire57.py 从 _mkB57.py 的 SCAN 段逐行抽出(只改路径常量与模块别名), 插门前把 '
    u'_b57flat.json 的 %d 个键与 DERIV[\'B57\'] 的 %d 条算式(%d 个复算点)在抽出体上跑过, 值不符即停机; '
    u'因此真正独立的两遍是 _pick57.py 与本注。采集侧与建条目侧在 %d 个共有量上一开始有 20 处不符, 查到底分成两种性质: '
    u'①定义不同——页标(整篇字符扫描, 因为 “[Page N]” 缀在页眉行右端而不单独成行)、词边界是否把下划线算词字符 '
    u'(小写 sha1 落在 ecdsa_sha1 里就不该计)、\'optional\' 的大小写两档、\'Rationale:\' 少写冒号、门限的两种拼法 '
    u'(2048-bit ⇎ 2048 bits)、月份年的剥离口径、锚池的页眉窗口(%d 字符)／触发词表(六枚)／下限(只有整行档要 ≥%d 字符) '
    u'／归一后为空的行(纯 +---+ 分隔线在每个源都“命中”, 必须剔出池); '
    u'②同名不同形的假不符——池的 per-tag 列表与全局标量曾共用 pool_1 一个键名, 时间单调曾一处返 4 元一处返 3 元, '
    u'这两处不改判而是改名(pool_tag_1 ⇎ pool_1, date_seg_ok ⇎ 旧名), 因为把两种口径压进同一个键名只会让门槛假装它们相同。'
    % (len(FLAT), len(DJ) - 1, sum(v.count(u'B57V') for v in DJ.values()), len(TIE), 40, 20))
CL2 = dict((k, v) for k, v in CH[u'collisions'].items() if len(v) > 1)
add(u'- 门槛的账: DERIV 键 %d 个 ⇎ 引用点 %d 处 ⇎ 同数共键 %d 组(两名以上 %d 组) ⇎ 0 键折 %d 项。'
    u'同数的字面不取第一条算式, 而是复合式 LIT*(1-(max(全部算式)-min(全部算式))): 每条算式都等于该字面时括号才为 1。'
    u'这一档在插门前抓到一条真错: “在写理由的文书份数”登记的字面由非零源数出来是对的, 而配给它的算式误写成 '
    u'B57V(\'kw_rationale\',0)+B57V(\'kw_rationale\',2)——那是两份协议的理由条合计=0, 于是复合式对出 -2 并停机; '
    u'改成逐源 >0 求和后算式与字面才同指一物。字面一直没错, 错的是“哪条算式支持这个字面”, 复合式的作用就在这里。'
    % (len(DJ), CH[u'deriv_points'], len(CH[u'collisions']), len(CL2), CH[u'zero_terms']))
for k, v in sorted(CL2.items(), key=lambda x: (-len(x[1]), x[0]))[:5]:
    add(u'  - 同数 %s(%d 条): %s' % (k, len(v), u' ⇎ '.join(v)))
add(u'- 主轴的来历(必须写, 因为它一度给出两个不可能的数): 搬运那档最早把“共用行数”按逐字子串再现来数(%d 枚), '
    u'又把“独有”按整行归一集合去减, 闭合差算出 -108 这种不可能的负数——同一个键名里混了两种口径。 '
    u'现在三口径各自登记并各自校住: 整行归一集合交 %d(独有 %d⇎%d, 并集 %d, 三档相加减并集=%d), '
    u'再现口径旧行在新文再现 %d ⇎ 反向 %d(合计 %d), 句子口径共用 %d(并集 %d, 闭合 %d), 两口径之差 %d 单独立键。 '
    u'共用那批整行的体裁是本注现数的: 参考文献行 %d ⇎ 章节号行 %d ⇎ 正文行 %d(相加校住 %d)——只有第三类才是'
    u'“同一条声明原样搬过去”。另一处: “共用句里含门限那句”数出 %d⇎%d 两个 0 像是巧合, 其实是断句口径的产物, '
    u'它成立的真理由是这两行互不等价: %s ⇎ %s; 而同一批共用池里 \'Rationale:\' 也 0 命中(%d), '
    u'说明搬走的是理由、改掉的是门限——这两句都能由字节复算, 而“改判”这个判断本身只在正文的对照里成立。'
    % (FLAT[u'carry_o_in_n_text'], FLAT[u'carry_shared'], FLAT[u'carry_only_o'], FLAT[u'carry_only_n'],
       FLAT[u'carry_union'], FLAT[u'carry_close'], FLAT[u'carry_o_in_n_text'], FLAT[u'carry_n_in_o_text'],
       FLAT[u'carry_sub_overlap'], FLAT[u'carry_sent_shared'], FLAT[u'carry_sent_union'],
       FLAT[u'carry_sent_close'], FLAT[u'carry_caliber_gap'], R4, T4, len(RAW4) - R4 - T4,
       FLAT[u'carry_shared_raw'], FLAT[u'carry_thr_192'], FLAT[u'carry_thr_224'],
       u'less than 192 bits SHOULD NOT be used.', u'Curves of less than 224 bits MUST NOT be used.',
       FLAT[u'carry_sent_rat']))
add(u'- 四档身份的账本(全由在库字节复算): 点名层 \'SHA-1\' %s ⇎ 小写 %s ⇎ 净 SHA1(刨 HMAC-SHA1) %s ⇎ HMAC-SHA1 %s, '
    u'非零拼写种数 %s(旧建议 %d 种都不写, 它唯一一次提到是给 MAC 定强度下限), 四档相加 %s; '
    u'共现层 “MUST NOT 与 SHA-1⇎MD5 同一行” %s(合计 %d 处); 从句层 1.3 那份带 unless 从句而新建议那份不带(不可数, 只进正文); '
    u'强度层 MUST NOT %s ⇎ 纯 MUST %s ⇎ SHOULD NOT %s ⇎ 纯 SHOULD %s ⇎ MAY %s ⇎ NOT RECOMMENDED %s, '
    u'六档排他闭合差 %s／%s／%s 全 0; 理由层 \'Rationale:\' %s(协议两份共 %d 条 ⇎ 建议两份共 %d 条 ⇎ 在写的文书 %d 份)。'
    u'身份层: 1.3 的枚举行 %d 处共 %d 枚, 名里含 sha1 的 %d 枚全在 Legacy 块内(块内 %d 枚), '
    u'而明文“必须支持”的 %d 枚里含 sha1 的 %d 枚——两集交 0。'
    % (u' ⇎ '.join(map(str, FLAT[u'sp_sha1_hy'])), u' ⇎ '.join(map(str, FLAT[u'sp_sha1_lower'])),
       u' ⇎ '.join(map(str, FLAT[u'sp_sha1_net'])), u' ⇎ '.join(map(str, FLAT[u'sp_hmac_sha1'])),
       u' ⇎ '.join(map(str, FLAT[u'sp_case_variants'])), FLAT[u'sp_case_variants'][1],
       u' ⇎ '.join(map(str, FLAT[u'sp_total_sha1_family'])), u' ⇎ '.join(map(str, Q4[u'line_sha_mustnot'])),
       sum(Q4[u'line_sha_mustnot']), u' ⇎ '.join(map(str, FLAT[u'kw_mustnot'])),
       u' ⇎ '.join(map(str, FLAT[u'kw_must'])), u' ⇎ '.join(map(str, FLAT[u'kw_shouldnot'])),
       u' ⇎ '.join(map(str, FLAT[u'kw_should'])), u' ⇎ '.join(map(str, FLAT[u'kw_may'])),
       u' ⇎ '.join(map(str, FLAT[u'kw_notrecommended'])), u' ⇎ '.join(map(str, FLAT[u'kw_close'])),
       u' ⇎ '.join(map(str, FLAT[u'kw_close2'])), u' ⇎ '.join(map(str, FLAT[u'kw_close3'])),
       u' ⇎ '.join(map(str, FLAT[u'kw_rationale'])), FLAT[u'kw_rationale'][0] + FLAT[u'kw_rationale'][2],
       FLAT[u'kw_rationale'][1] + FLAT[u'kw_rationale'][3],
       len([1 for i in range(4) if FLAT[u'kw_rationale'][i]]), FLAT[u'id_enum_lines'][2],
       FLAT[u'id_enum_total'][2], FLAT[u'id_sha1_schemes'][2], FLAT[u'id_legacy_block'][2],
       FLAT[u'id_must_support_n'], FLAT[u'id_must_support_sha1']))
add(u'- 套件名的跨代零交集与两条桥(本注用第三种切法复算): 1.2 与 1.3 的套件名集合交 %d 枚(T 独有 %d ⇎ F 独有 %d), '
    u'以裸 _SHA 结尾的在 1.2 有 %d 种(出现 %d 处)而在 1.3 为 %d 枚; 两版建议点名的套件在库内协议文本里的落点三档闭合: '
    u'新建议 %d＋%d＋%d−%d=%d ⇎ 旧建议 %d＋%d＋%d−%d=%d, 两版建议自己的交集 %d 枚。 '
    u'那 %d⇎%d 枚两份协议都不在的套件, 其正式出处是库里没有的规范(AES-GCM 与 ECDHE 那一族, 本库只收这四份): '
    u'“它们是否合法存在”不可由在库文件判定, 能判的只有“这四份文件里点没点名”——所以这条只进注不进门槛。'
    % (FLAT[u'suite_common_TF'], FLAT[u'suite_T_only'], FLAT[u'suite_F_only'], FLAT[u'suite_endsha_T'],
       FLAT[u'sp_suite_endsha'][0], FLAT[u'sp_suite_endsha'][2], FLAT[u'suite_from_N_in_T'],
       FLAT[u'suite_from_N_in_F'], FLAT[u'suite_from_N_in_none'], FLAT[u'suite_N_total'],
       FLAT[u'suite_bridge_close'], FLAT[u'suite_from_O_in_T'], FLAT[u'suite_from_O_in_F'],
       FLAT[u'suite_from_O_in_none'], FLAT[u'suite_O_total'], FLAT[u'suite_O_bridge_close'],
       FLAT[u'suite_common_ON'], FLAT[u'suite_from_N_in_none'], FLAT[u'suite_from_O_in_none']))
add(u'- 引用与时间方向: 12 个有序对里非零 %d ⇎ 零 %d ⇎ 出现处 %d, 本注按“被引者出版月晚于引用者”判违例得 %d 处(契约 %d); '
    u'方向全对不是假设: 非零的 %d 对是 %s。谱系行 Obsoletes 列 %s ⇎ Updates 列 %s, 其中在库可验的取代关系 %d 对'
    u'(1.3 废 1.2 ⇎ 新建议废旧建议), 库里没有对应文件的那批是 %s 枚; 新建议提它自己废掉的旧建议 %d 处——'
    u'废掉不等于不提。门限那句的数值与强度同时迁移: 字面 \'192 bits\' %s ⇎ \'224 bits\' %s ⇎ “less than 224 bits” %s, '
    u'而 \'less than 192 bits\' 只在旧建议出现; MUST NOT 行之后 6 行内出现 \'Rationale:\' 的行数 %s——'
    u'建议两份各 %d＋%d 枚, 协议两份 %d＋%d 枚。'
    % (FLAT[u'cite_pairs_nonzero'], FLAT[u'cite_pairs_zero'], FLAT[u'cite_pairs_occ'], BKV,
       FLAT[u'cite_backward_violations'], FLAT[u'cite_pairs_nonzero'],
       u' ／ '.join(u'%s→%s %d 处' % (LB[TAGS[a]], LB[TAGS[b]], PAIR4[(a, b)])
                    for (a, b), v in sorted(PAIR4.items()) if v),
       u' ⇎ '.join(map(str, FLAT[u'cite_obsoletes_n'])), u' ⇎ '.join(map(str, FLAT[u'cite_updates_n'])),
       FLAT[u'cite_obsoleted_inrepo_all'], u' ⇎ '.join(map(str, FLAT[u'cite_obsoletes_notinrepo'])),
       FLAT[u'cite_N_to_O'], u' ⇎ '.join(map(str, FLAT[u'bits_192'])),
       u' ⇎ '.join(map(str, FLAT[u'bits_224'])), u' ⇎ '.join(map(str, FLAT[u'curves_below_224'])),
       u' ⇎ '.join(map(str, FLAT[u'line_rationale_mustnot'])), FLAT[u'line_rationale_mustnot'][1],
       FLAT[u'line_rationale_mustnot'][3], FLAT[u'line_rationale_mustnot'][0],
       FLAT[u'line_rationale_mustnot'][2]))
add(u'- 四份字节的指纹与两代页式(旁证, 判词里只报“种数”而不报串, 因为串里的数字段无法由字节直接命中): %s; '
    u'sha16 种数 %d ⇎ 最长行四份同为 %d 列 ⇎ 平均行长 %s ⇎ 制表符 %s ⇎ 行尾空白 %s——四份一个制表符都不用, '
    u'排版全靠 72 列折行, 这就是折行残片(悬空下划线 %s 枚)与“整行口径虚高”的来源。'
    u'前三份是带页标的旧式序列化(页标 %s ⇎ 页眉 %s, 差恒 %s, 即首页无顶栏 ⇎ 页眉姓列种数 %s), '
    u'新建议页眉页标各 0 而带 BOM(%d)与非 ASCII(%d 枚, 字节减字符 %d): 严格 UTF-8 解码四份全过(%s), '
    u'所以“字符数=字节数”只在 %d 份上成立。项目符也换了记号: \'o\' 行 %s ⇎ \'*\' 行 %s, 同一份里两种混用 %d 份, '
    u'只用一种的 %d／4——同一条 SSLv2 禁令在旧建议以 \'o\' 开头、在新建议换成 \'*\' 而整句其余逐字不变(禁令行两份各 %d 处)。'
    % (u' ⇎ '.join(SHA), FLAT[u'sha_distinct'], FLAT[u'maxlen'][0],
       u' ⇎ '.join(map(str, FLAT[u'meanlen'])), u' ⇎ '.join(map(str, FLAT[u'tabs'])),
       u' ⇎ '.join(map(str, FLAT[u'trailws'])), u' ⇎ '.join(map(str, FLAT[u'frag_tail'])),
       u' ⇎ '.join(map(str, Q4[u'pagemarks'])), u' ⇎ '.join(map(str, Q4[u'hdr'])),
       u' ⇎ '.join(map(str, Q4[u'page_gap'])), u' ⇎ '.join(map(str, Q4[u'author_hdr'])),
       FLAT[u'bom'][3], FLAT[u'nonascii'][3], FLAT[u'bytegap'][3],
       u' ⇎ '.join(map(str, FLAT[u'utf8_strict'])), FLAT[u'eqc'],
       u' ⇎ '.join(map(str, Q4[u'kwbullet_o'])), u' ⇎ '.join(map(str, Q4[u'kwbullet_star'])),
       Q4[u'kw_mix_docs'], Q4[u'kw_bullets_onlyone'], FLAT[u'ssl_v2_ban'][1]))
add(u'- 只在本机成立的一笔(不进门槛): 四份字节的磁盘 mtime 与它们自写的 “月份 年份” 相差 %+.2f ⇎ %+.2f ⇎ %+.2f ⇎ %+.2f 天'
    u'(自写日期 %s, 本注取每月 15 日为中点算差; 新建议无页眉, 其日期由前 6000 字符里最频繁的月份年推出, '
    u'这一档与建条目侧“取首个匹配”是两种取法而结果相同)。谁抓到的、抓于何时, 在库文件里没有依据; '
    u'同理不可判的还有: 这四份 .txt 是否各号的当前版本(rfc-editor 会在改版后重发序列化, 库里没有第二个版本可比), '
    u'以及 “1.3 为什么对证书里的 SHA-1 留 unless 从句” 的部署数据(正文只给从句不给数字)。'
    % (-DAYS[0], -DAYS[1], -DAYS[2], -DAYS[3], u' ⇎ '.join(FLAT[u'date_raw'])))
SH = []
for src_i, p in enumerate(PATHS):
    for f in glob.glob(u'corpus/babeltele/B*.md'):
        t = os.path.basename(f).split(u'_')[0]
        if t == u'B57' or SRCALL.get(t) and p not in SRCALL[t]:
            continue
        ep = glob.glob(u'corpus/babeltele/%s_*.md' % t)
        AT2 = set()
        if ep:
            TT2 = io.open(ep[0], encoding='utf-8').read()
            mm = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT2, re.S)
            AT2 = set(re.findall(u'⟨([^⟨⟩]+)⟩', mm.group(1))) if mm else set()
        SH.append((t, src_i, len(AT2), len(AT2 & set(ATOMS))))
SH.sort()
add(u'- 同一份字节是否还被别的条目当过源: 按门槛里的 SRC 表逐份查, 共用处 %d 处%s。'
    u'这四份 IETF 规范此前没有进过任何条目, 本条是第一次——所以本条没有“同料不同问”的历史包袱, 也没有需要与旧条目对齐的量; '
    u'而“72 列折行＋页眉页标这套旧式序列化 ⇎ 新式序列化”这一档是 B53(同一份 FIPS 202 的四种序列化)的量法在这批原料上的延伸, '
    u'但那里量的是载体而这里量的是判词, 两处不共用键。'
    % (len(SH), u'（%s）' % u' ／ '.join(u'%s(源%s, 锚%d, 交%d)' % x for x in SH) if SH else u''))
add(u'- 锚的可核性: %d 处带标签锚 ⇎ %d 串去重, 按标签判成员得只属一源 %d ⇎ 属两或三源 %d ⇎ 四源全在 %d(相加校住 %d), '
    u'逐源判成员共 %d 次检查(=去重串×4), 错配 %d 处; 标签按源分 %s。归属不读旁注文件, 由正文里“源标签紧接原子引文”的配对现推。 '
    u'不可由在库文件判定因而只写在本注的: IANA 注册表此刻对这些码位的弃用标记, 库里没有的规范里那批套件名的合法性, '
    u'以及“新建议为什么把 MAC 下限从 HMAC-SHA1 抬走”的取词过程(正文只给强度判据)。'
    % (AMET[u'anchor_total'], AMET[u'anchor_distinct'], AMET[u'anchor_single'], AMET[u'anchor_cross'],
       AMET[u'anchor_all4'], AMET[u'anchor_distinct'], AMET[u'checks'], AMET[u'anchor_err'],
       u' ⇎ '.join(u'%s %d 枚' % (LB[t], CH[u'tag_counts'][t]) for t in TAGS)))

body = NL.join(NT)
T = io.open(ENTRY, encoding='utf-8').read()
head = u'## ⛓解读注'
i = T.index(head)
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(T[:i] + head + NL + NL + body + NL)
print(u'注已写: %d 段 ｜ 契约 %d 键全对齐审计器 ⇎ 采集侧共有 %d 量零不符 ｜ 第四遍现取 %d 个量／%d 个数全等契约 '
      u'｜ 共用源 %d 处 ｜ mtime 与自写月份差 %+.2f ⇎ %+.2f ⇎ %+.2f ⇎ %+.2f 天(只在本机)' % (
          len(NT), len(FLAT), len(TIE), QN, QE, len(SH), -DAYS[0], -DAYS[1], -DAYS[2], -DAYS[3]))
