# -*- coding: utf-8 -*-
"""README 记账: 56 条 → 57 条。合计、唯一码点、推导条数全部取自 audit 的当下输出, 不手填。
本文件是第五套实现: 强度词的单空格口径走 str.count，另用“空白分词 + 二元 n-gram”再数一遍并把两口径之差登记为跨行断开的禁令数（建条目侧的口径要求 MUST 与 NOT 之间恰一个空格，换行断开的那几处它数不到），阈值词走一/二元 n-gram 计数(采集侧用正则 \\b、建条目侧用逐次 find 扫描、解读注侧用正则环视),
拼写可见度也走 str.count(建条目侧手写 find 循环), 形状档从字节走起(len(rb)／rb.count(b'\\r')／BOM 看前三字节／行档用 splitlines 补尾行),
页标用 '\\[Page \\d+\\]'(建条目侧逐字符判数字尾巴), 套件名用 {8,} 量词(建条目侧手工扩字符), 谱系右栏剥月份用 re.sub(建条目侧逐月 find 删串),
搬运的句子档用 look-behind 断句(建条目侧按字符类别扫下标), 归一走 isalnum∧isascii 过滤(建条目侧用 re.sub),
签名摘要换 blake2b 8 字节(建条目侧用 sha256 前 16 位)——只比种数不比串, 两种算法的串本就不同;
锚的穿源档按条目正文的 ⟦⟧⟨⟩ 直读(建条目侧按池位置推); 引用点的两口径在本遍现数(文本出现次数 ⇎ 建条目侧按“值→算式”去重)。
每个数与两份快照对表: 建条目侧扁平契约 corpus/_b57flat.json ⇎ 门槛侧 corpus/_b57audit.json。任一标量对不上就当场停机。"""
import hashlib, io, json, re, string, subprocess, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
FM = u'corpus/README.md'
NL = chr(10)
TAG = u'B57'
ENTRY = u'corpus/babeltele/B57_four_documents_one_hash_verdict.md'
PATHS = [u'corpus/raw/ietf/rfc5246.txt', u'corpus/raw/ietf/rfc7525.txt',
         u'corpus/raw/ietf/rfc8446.txt', u'corpus/raw/ietf/rfc9325.txt']
TAGS = [u'T', u'O', u'F', u'N']
DOCALL = [5246, 7525, 8446, 9325]
MONA = [u'January', u'February', u'March', u'April', u'May', u'June', u'July', u'August',
        u'September', u'October', u'November', u'December']
MONY = u'(?:' + u'|'.join(MONA) + u')'
PUN = u''.join([c for c in string.punctuation if c != u'_'])
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')
RD = lambda q: io.open(q, encoding='utf-8', errors='replace').read()
WL57, WR57 = 10, 25   # 分节摘要窗口: 这一组逐字重现条目里那 2 271 字符的四块(整条文件也逐字相同)


def sub(old, new, s):
    assert s.count(old) == 1, (u'锚不唯一', s.count(old), old[:60])
    return s.replace(old, new)


def rnd(x):
    return round(x, 4) if isinstance(x, float) else x


# ---------- 1) 门槛现取 ----------
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
OUT = p.stdout
assert u'保真门槛' in OUT and u'PASS' in OUT, OUT[-600:]
row = {}
for l in OUT.split(NL):
    if not l.startswith(u'| '):
        continue
    parts = [x.strip() for x in l.strip(u'|').split(u'|')]
    k = parts[0]
    if (k[:1] == u'B' and k[1:].isdigit()) or k == u'ALL':
        row[k] = parts[1:]
NENT = len([k for k in row if k != u'ALL'])
assert NENT == 57, NENT
b57, A = row[u'B57'], row[u'ALL']
dig_all, enc_all = int(A[0].replace(u' ', u'')), int(A[1].replace(u' ', u''))
uniq_all = int(re.sub(u'[^0-9]', u'', A[4]))
assert (sum(int(v[0]) for k, v in row.items() if k != u'ALL'),
        sum(int(v[1]) for k, v in row.items() if k != u'ALL')) == (dig_all, enc_all)
soft_all = proofs = None
HINT = {}
for l in OUT.split(NL):
    if l.startswith(u'提示') and u'共' in l:
        soft_all = int(l.split(u'共')[1].split(u' 个')[0])
    if l.startswith(u'已机检的推导'):
        proofs = int(l.split(u'(')[1].split(u' 条)')[0])
    m2 = re.match(u'^   (B\\d\\d) (\\[.*\\])$', l)
    if m2:
        HINT[m2.group(1)] = eval(m2.group(2), {'__builtins__': {}}, {})
assert soft_all == 20 and proofs == 1307, (soft_all, proofs)
assert sum(len(v) for v in HINT.values()) == soft_all, (HINT, soft_all)
dig57, enc57 = int(b57[0]), int(b57[1])
ret_tot = A[2].replace(u'*', u'')   # 保留率一律照抄 audit 的 ALL 行(编码合计 ÷ 摘要段合计), 不在本遍另推口径

# ---------- 2) 第五遍: 自己从四份字节现量 ----------
CH = json.load(io.open(u'corpus/_b57checks.json', encoding='utf-8'))
FLAT = json.load(io.open(u'corpus/_b57flat.json', encoding='utf-8'))
SN = json.load(io.open(u'corpus/_b57audit.json', encoding='utf-8'))
SNAP, SRCALL = SN[TAG], SN[u'SRC']
assert enc57 == CH[u'enc_chars'] and dig57 == 2271, (enc57, CH[u'enc_chars'], dig57)

TXT = [RD(q) for q in PATHS]
RB = [io.open(q, 'rb').read() for q in PATHS]
LST = [t.splitlines() for t in TXT]
TAIL = [1 if t.endswith(NL) else 0 for t in TXT]
Q5 = {}


def q(name, val):
    Q5[name] = val
    if name in FLAT:
        assert rnd(val) == rnd(FLAT[name]), (name, val, FLAT[name])
    if name in SNAP:
        assert rnd(val) == rnd(SNAP[name]), (name, u'快照', val, SNAP[name])
    return val


def m(name):
    # 复合量一律由本遍现量的分量再算一遍, 不回读契约(回读就等于承认没另算)
    return Q5[name]


def q4(name, f):
    v = [f(k) for k in range(4)]
    q(name, v)
    return v


def bd(hay, word):
    # 词边界的可见度: 逐次 find 再查左右邻, 不用 (与建条目侧的 find 扫描也不是同一份代码)
    n, k = 0, hay.find(word)
    while k >= 0:
        L = hay[k - 1] if k else u''
        R = hay[k + len(word)] if k + len(word) < len(hay) else u''
        n += 1 if not (L.isalnum() or R.isalnum()) else 0
        k = hay.find(word, k + 1)
    return n


def pn(s):
    return u''.join([ch for ch in s.lower() if ch.isalnum() and ch.isascii()])


def _lines(i):
    return len([l for l in LST[i] if l.strip()])


# 形状档: 字节侧走 rb, 行档走 splitlines(补尾行才是“换行次数”口径)
q4(u'bytes', lambda i: len(RB[i]))
q4(u'chars', lambda i: len(TXT[i]))
q4(u'nonblank', _lines)
q(u'lines', [len(TXT[i].split(NL)) - 1 for i in range(4)])
BL5 = [len(TXT[i].split(NL)) - m(u'nonblank')[i] for i in range(4)]
q(u'blank', BL5)
# 换页符也断行: splitlines 口径比 split(\\n) 口径多切出 FF 段, 本遍把两套都数出来
FF = [RB[i].count(b'\x0c') for i in range(4)]
BLF = [len(LST[i]) + TAIL[i] - m(u'nonblank')[i] for i in range(4)]
assert [BLF[i] - BL5[i] - FF[i] for i in range(4)] == [0, 0, 0, 0], (BLF, BL5, FF)
q4(u'tabs', lambda i: RB[i].count(b'\t'))
q4(u'crlf', lambda i: RB[i].count(b'\r'))
q4(u'trailws', lambda i: len([l for l in LST[i] if l[-1:] in (u' ', u'\t')]))
q4(u'nonascii', lambda i: len([c for c in TXT[i] if not c.isascii()]))
q4(u'bom', lambda i: 1 if RB[i][:3] == b'\xef\xbb\xbf' else 0)
q4(u'maxlen', lambda i: max([len(l) for l in LST[i]]))
q4(u'meanlen', lambda i: int(round(1.0 * sum(len(l) for l in LST[i] if l.strip()) /
                                   max(1, _lines(i)))))
q(u'bytegap', [m(u'bytes')[i] - m(u'chars')[i] for i in range(4)])
q(u'ascii_eq', [1 if m(u'nonascii')[i] == 0 else 0 for i in range(4)])
q(u'eqc', sum(m(u'ascii_eq')))
q(u'eqb', len([1 for i in range(4) if m(u'bytegap')[i] == 0]))
DIG = [hashlib.blake2b(RB[i], digest_size=8).hexdigest() for i in range(4)]
q(u'sha_distinct', len(set(DIG)))


def _strict(i):
    try:
        RB[i].decode(u'utf-8')
        return 1
    except UnicodeDecodeError:
        return 0


q4(u'utf8_strict', _strict)
q4(u'pagemarks', lambda i: len(re.findall(u'\\[Page \\d+\\]', TXT[i])))
q4(u'hdr', lambda i: len([l for l in LST[i] if re.match(u'^RFC \\d{4}', l)]))
q(u'page_gap', [m(u'pagemarks')[i] - m(u'hdr')[i] for i in range(4)])
q4(u'author_hdr', lambda i: len(set(l.rpartition(u' ')[2] for l in LST[i] if l[:4] == u'RFC ')))

# 强度词: 空白分词 + 一/二元 n-gram 计数
TOK = [[w.strip(PUN) for w in t.split()] for t in TXT]
C1 = [Counter(x) for x in TOK]
C2 = [Counter([tuple(x[i:i + 2]) for i in range(len(x) - 1)]) for x in TOK]
W1 = lambda i, w: C1[i][w]
W2 = lambda i, a, b: C2[i][(a, b)]
# 第三种切词: 非[字母数字下划线]一律断词——连字符复合词里的 MUST 就此与空白分词口径分开
W3 = [re.split(u'[^0-9A-Za-z_]+', t) for t in TXT]
W4 = lambda i, w: len([x for x in W3[i] if x == w])

q4(u'kw_mustnot', lambda i: TXT[i].count(u'MUST NOT'))
q4(u'kw_must_all', lambda i: W4(i, u'MUST'))
q(u'kw_must', [m(u'kw_must_all')[i] - m(u'kw_mustnot')[i] for i in range(4)])
q4(u'kw_shouldnot', lambda i: TXT[i].count(u'SHOULD NOT'))
q4(u'kw_should_all', lambda i: W4(i, u'SHOULD'))
q(u'kw_should', [m(u'kw_should_all')[i] - m(u'kw_shouldnot')[i] for i in range(4)])
q4(u'kw_may', lambda i: W4(i, u'MAY'))
q4(u'kw_required', lambda i: W4(i, u'required'))
q4(u'kw_notrecommended', lambda i: TXT[i].count(u'NOT RECOMMENDED'))
q4(u'kw_rec_all', lambda i: W4(i, u'RECOMMENDED'))
q(u'kw_recommended', [m(u'kw_rec_all')[i] - m(u'kw_notrecommended')[i] for i in range(4)])
q4(u'kw_optional', lambda i: W4(i, u'optional'))
q4(u'kw_optional_up', lambda i: W4(i, u'OPTIONAL'))
q4(u'kw_rationale', lambda i: TXT[i].count(u'Rationale:'))
q4(u'kwbullet_o', lambda i: len([l for l in LST[i] if l.startswith(u'   o  ')]))
q4(u'kwbullet_star', lambda i: len([l for l in LST[i] if l.startswith(u'   *  ')]))
q4(u'kwbullet_num', lambda i: len([l for l in LST[i] if re.match(u'^      \\d+\\.  ', l)]))
q(u'kw_close', [m(u'kw_mustnot')[i] + m(u'kw_must')[i] - m(u'kw_must_all')[i] for i in range(4)])
q(u'kw_close2', [m(u'kw_shouldnot')[i] + m(u'kw_should')[i] - m(u'kw_should_all')[i] for i in range(4)])
q(u'kw_close3', [m(u'kw_notrecommended')[i] + m(u'kw_recommended')[i] -
                 m(u'kw_rec_all')[i] for i in range(4)])
q(u'kw_mix', [1 if (m(u'kwbullet_o')[i] and m(u'kwbullet_star')[i]) else 0 for i in range(4)])
q(u'kw_mix_docs', sum(m(u'kw_mix')))
q(u'kw_bullets_oneway', len([1 for i in range(4)
                             if m(u'kwbullet_o')[i] + m(u'kwbullet_star')[i] > 0]))
q(u'kw_bullets_onlyone', len([1 for i in range(4)
                              if bool(m(u'kwbullet_o')[i]) != bool(m(u'kwbullet_star')[i])]))
q(u'prot', len([1 for i in range(4) if m(u'kw_rationale')[i] > 0]))
# 第二口径: 空白分词后的二元 n-gram 把“跨行断开的禁令”也算进来, 与单空格口径之差逐档数出来
W2CAL = {u'MUST NOT': [W2(i, u'MUST', u'NOT') for i in range(4)],
         u'SHOULD NOT': [W2(i, u'SHOULD', u'NOT') for i in range(4)],
         u'NOT RECOMMENDED': [W2(i, u'NOT', u'RECOMMENDED') for i in range(4)]}
WRAP = {u'MUST NOT': [W2CAL[u'MUST NOT'][i] - m(u'kw_mustnot')[i] for i in range(4)],
        u'SHOULD NOT': [W2CAL[u'SHOULD NOT'][i] - m(u'kw_shouldnot')[i] for i in range(4)],
        u'NOT RECOMMENDED': [W2CAL[u'NOT RECOMMENDED'][i] - m(u'kw_notrecommended')[i]
                             for i in range(4)]}
WRAP.update({u'2048 bits': [W2(i, u'2048', u'bits') - TXT[i].count(u'2048 bits') for i in range(4)],
               u'1024 bits': [W2(i, u'1024', u'bits') - TXT[i].count(u'1024 bits') for i in range(4)]})
WRAPTOT = [sum(WRAP[k][i] for k in WRAP) for i in range(4)]
assert WRAP[u'MUST NOT'][0] == 3, WRAP
# 复合词口径差: 同一枚词在“空白分词”里不算、按词边界算的, 全是 MUST⇎SHOULD-level 这类连字写法
HYPH = {w: [W4(i, w) - W1(i, w) for i in range(4)] for w in (u'MUST', u'SHOULD', u'MAY')}
assert (sum(HYPH[u'MUST']), sum(HYPH[u'SHOULD']), sum(HYPH[u'MAY'])) == (4, 4, 0), HYPH
assert set(i for w in HYPH for i in range(4) if HYPH[w][i]) == {3}

# 拼写可见度: str.count
q4(u'sp_sha1_hy', lambda i: TXT[i].count(u'SHA-1'))
q4(u'sp_sha1_plain', lambda i: TXT[i].count(u'SHA1'))
q4(u'sp_hmac_sha1', lambda i: TXT[i].count(u'HMAC-SHA1'))
q(u'sp_sha1_net', [m(u'sp_sha1_plain')[i] - m(u'sp_hmac_sha1')[i] for i in range(4)])
q4(u'sp_sha1_lower', lambda i: TXT[i].count(u'sha1'))
q4(u'sp_md5_hy', lambda i: TXT[i].count(u'MD5'))
q4(u'sp_md5_lower', lambda i: TXT[i].count(u'md5'))
q4(u'sp_md5sha1', lambda i: TXT[i].count(u'MD5-SHA1'))
q4(u'sp_sha256_hy', lambda i: TXT[i].count(u'SHA-256'))
q4(u'sp_sha256_lower', lambda i: TXT[i].count(u'sha256'))
q4(u'sp_sha384_hy', lambda i: TXT[i].count(u'SHA-384'))
q4(u'sp_gcm_sha256', lambda i: TXT[i].count(u'GCM_SHA256'))
q4(u'sp_case_variants', lambda i: len([1 for v in (m(u'sp_sha1_hy')[i], m(u'sp_sha1_net')[i],
                                                   m(u'sp_sha1_lower')[i]) if v > 0]))
q(u'sp_total_sha1_family', [m(u'sp_sha1_hy')[i] + m(u'sp_sha1_net')[i] +
                            m(u'sp_sha1_lower')[i] + m(u'sp_hmac_sha1')[i] for i in range(4)])
SU5 = [re.findall(u'\\bTLS_[A-Z0-9_]{8,}', TXT[i]) for i in range(4)]
SS5 = [set(x) for x in SU5]
q4(u'sp_suite_endsha', lambda i: len([s for s in SU5[i] if s.endswith(u'_SHA')]))

# 算法标识符
q4(u'id_rsa_pkcs1_sha1', lambda i: W4(i, u'rsa_pkcs1_sha1'))
q4(u'id_ecdsa_sha1', lambda i: W4(i, u'ecdsa_sha1'))
q4(u'id_dsa_sha1', lambda i: W4(i, u'dsa_sha1'))
q4(u'id_dsa_sha1_text', lambda i: TXT[i].count(u'dsa_sha1'))
q4(u'id_rsa_pkcs1_sha256', lambda i: W4(i, u'rsa_pkcs1_sha256'))
q4(u'id_rsa_pss_rsae_sha256', lambda i: W4(i, u'rsa_pss_rsae_sha256'))
q4(u'id_ecdsa_secp256r1_sha256', lambda i: W4(i, u'ecdsa_secp256r1_sha256'))
q4(u'id_rsa_pss_pss_sha256', lambda i: W4(i, u'rsa_pss_pss_sha256'))
ESCHEME = u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+\\('
SCH = [re.findall(ESCHEME, TXT[i]) for i in range(4)]
q4(u'id_scheme_total', lambda i: len(SCH[i]))
q4(u'id_sha1_schemes', lambda i: len([x for x in SCH[i] if u'sha1' in x[:-1]]))
PHRASE = u'/* Legacy algorithms */'


def leg_occ(i):
    # 同一句话在一份文书里可能出现两次(协议正文的枚举 ⇎ IANA 那节的注册表), 逐次取块而不是只取第一块
    t, out, k = TXT[i], [], TXT[i].find(PHRASE)
    while k >= 0:
        nxt = [x for x in (t.find(u'/*', k + len(PHRASE)), t.find(u'}', k + len(PHRASE))) if x >= 0]
        e = min(nxt) if nxt else len(t)
        out.append(len(re.findall(ESCHEME, t[k + len(PHRASE):e])))
        k = t.find(PHRASE, k + 1)
    return out


LEGB = [leg_occ(i) for i in range(4)]
q(u'id_legacy_block', [sum(x) for x in LEGB])
LEGPH = [len(x) for x in LEGB]   # 这句话在各份里出现的次数: 本遍独有的量, 契约里没有对应键
assert LEGB == [[], [], [2, 2], []], LEGB
MS = re.search(u'MUST support digital signatures with(.{0,400}?)secp256r1', TXT[2], re.S)
MSN = re.findall(u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+', MS.group(1))
q(u'id_must_support_n', len(MSN))
q(u'id_must_support_sha1', len([x for x in MSN if u'sha1' in x]))
q4(u'id_enum_lines', lambda i: len([l for l in LST[i] if u'(0x' in l and re.search(
    u'\\b(?:rsa|ecdsa|eddsa|dsa)\\w*\\(', l)]))
q4(u'id_enum_total', lambda i: len(re.findall(
    u'\\b(?:rsa|ecdsa|eddsa|dsa)[a-z0-9_]*_[a-z0-9_]+ ?\\(0x[0-9A-Fa-f]{4}\\)', TXT[i])))

# 套件名矩阵
q4(u'suite_distinct', lambda i: len(SS5[i]))
q4(u'suite_occ', lambda i: len(SU5[i]))
q4(u'frag_tail', lambda i: len([s for s in SU5[i] if s.endswith(u'_')]))


def brg(s, d1, d2):
    return (len(SS5[s] & SS5[d1]), len(SS5[s] & SS5[d2]),
            len(SS5[s] - SS5[d1] - SS5[d2]), len(SS5[s]))


a, b, c, n = brg(3, 0, 2)
q(u'suite_from_N_in_T', a)
q(u'suite_from_N_in_F', b)
q(u'suite_from_N_in_none', c)
q(u'suite_N_total', n)
q(u'suite_bridge_close', a + b + c - n)
a, b, c, n = brg(1, 0, 2)
q(u'suite_from_O_in_T', a)
q(u'suite_from_O_in_F', b)
q(u'suite_from_O_in_none', c)
q(u'suite_O_total', n)
q(u'suite_O_bridge_close', a + b + c - n)
q(u'suite_F_only', len(SS5[2] - SS5[0] - SS5[1] - SS5[3]))
q(u'suite_T_only', len(SS5[0] - SS5[1] - SS5[2] - SS5[3]))
q(u'suite_common_TF', len(SS5[0] & SS5[2]))
q(u'suite_common_ON', len(SS5[1] & SS5[3]))
q(u'suite_endsha_T', len([s for s in SS5[0] if s.endswith(u'_SHA')]))

# 引用与谱系
occ5 = lambda i, num: len(re.findall(u'(?<![0-9A-Za-z])%d(?![0-9A-Za-z])' % num, TXT[i]))
q4(u'cite_rfc_tokens', lambda i: len(re.findall(u'\\bRFC ?(\\d{4})\\b', TXT[i])))
CITED = [set(re.findall(u'\\bRFC ?(\\d{4})\\b', TXT[i])) for i in range(4)]
q4(u'cite_rfc_distinct', lambda i: len(CITED[i]))
q4(u'cite_bracket', lambda i: len(re.findall(u'\\[RFC\\d{4}\\]', TXT[i])))
for _a in range(4):
    for _b in range(4):
        if _a != _b:
            q(u'cite_%s_to_%s' % (TAGS[_a], TAGS[_b]), occ5(_a, DOCALL[_b]))
            q(u'cite_rfc_%s_to_%s' % (TAGS[_a], TAGS[_b]),
              len([x for x in re.findall(u'\\bRFC ?(\\d{4})\\b', TXT[_a]) if int(x) == DOCALL[_b]]))
PAIRV = [m(u'cite_%s_to_%s' % (TAGS[a2], TAGS[b2]))
         for a2 in range(4) for b2 in range(4) if a2 != b2]
RFCPV = [m(u'cite_rfc_%s_to_%s' % (TAGS[a2], TAGS[b2]))
         for a2 in range(4) for b2 in range(4) if a2 != b2]
q(u'cite_pairs_total', len(PAIRV))
q(u'cite_pairs_nonzero', len([v for v in PAIRV if v]))
q(u'cite_pairs_zero', len([v for v in PAIRV if not v]))
q(u'cite_rfc_pairs_total', len(RFCPV))
q(u'cite_rfc_pairs_nonzero', len([v for v in RFCPV if v]))
q(u'cite_pairs_occ', sum(PAIRV))
q(u'cite_rfc_pairs_occ', sum(RFCPV))


def gene(i, key):
    line = next((l for l in LST[i] if l.startswith(key)), u'')
    line = re.sub(MONY + u' *\\d*', u'', line)
    return re.findall(u'\\b\\d{4}\\b', line)


q4(u'cite_obsoletes_n', lambda i: len(gene(i, u'Obsoletes:')))
q4(u'cite_updates_n', lambda i: len(gene(i, u'Updates:')))
OBS5 = [gene(i, u'Obsoletes:') for i in range(4)]
q4(u'cite_obsoleted_inrepo', lambda i: len([x for x in OBS5[i] if int(x) in DOCALL]))
q(u'cite_obsoletes_notinrepo', [m(u'cite_obsoletes_n')[i] - m(u'cite_obsoleted_inrepo')[i]
                                for i in range(4)])
q(u'cite_obsoleted_inrepo_all', sum(m(u'cite_obsoleted_inrepo')))


def mnum5(i):
    mm = re.search(MONY + u' (\\d{4})', TXT[i])
    return int(mm.group(1)) * 12 + MONA.index(mm.group(0).split()[0]) + 1


q(u'month_num', [mnum5(i) for i in range(4)])
q(u'month_gap_prev', [0] + [m(u'month_num')[i] - m(u'month_num')[i - 1] for i in range(1, 4)])
q(u'month_span', m(u'month_num')[3] - m(u'month_num')[0])
q(u'date_seg_ok', [1 if m(u'month_num')[i] > m(u'month_num')[i - 1] else 0 for i in range(1, 4)])
q(u'date_seg_n', sum(m(u'date_seg_ok')))
q(u'date_docnum_mono', len([1 for i in range(1, 4)
                            if DOCALL[i] > DOCALL[i - 1] and m(u'month_num')[i] > m(u'month_num')[i - 1]]))
q(u'cite_backward_violations', len([1 for a2 in range(4) for b2 in range(4) if a2 != b2
                                    and m(u'cite_%s_to_%s' % (TAGS[a2], TAGS[b2]))
                                    and mnum5(a2) < mnum5(b2)]))
q(u'cite_self_obsoleted', m(u'cite_N_to_O'))


def raw5(i):
    for l in LST[i]:
        if l[:4] == u'RFC ':
            mm = re.search(MONY + u' \\d{4}', l)
            if mm:
                return mm.group(0)
    mm = re.search(MONY + u' \\d{4}', TXT[i])
    return mm.group(0) if mm else u''


q(u'date_raw', [raw5(i) for i in range(4)])
q(u'date_ym', [[int(d.split()[1]), MONA.index(d.split()[0]) + 1] for d in m(u'date_raw')])

# 判决行定位
q4(u'line_sha_mustnot', lambda i: len([l for l in LST[i]
                                       if u'MUST NOT' in l and (u'SHA-1' in l or u'MD5' in l)]))
q4(u'line_sha_mustnot_hy', lambda i: len([l for l in LST[i] if u'MUST NOT' in l and u'SHA-1' in l]))
q4(u'line_sha_in_enum', lambda i: len([l for l in LST[i] if u'sha1' in l and u'(0x' in l]))
q4(u'line_rationale_mustnot', lambda i: len(
    [k for k in range(len(LST[i])) if u'MUST NOT' in LST[i][k]
     and any(u'Rationale:' in LST[i][j] for j in range(k, min(k + 7, len(LST[i]))))]))
DELP = set(pn(l) for l in LST[3] if u'(0x' in l)
q4(u'line_sha_in_prose', lambda i: len([l for l in LST[i] if u'SHA-1' in l and u'(0x' not in l
                                        and pn(l) not in DELP]))

# 两版建议之间的搬运
FOUR5 = [set(l.strip() for l in LST[i] if len(l.strip()) >= 20) for i in range(4)]
FAN5 = [pn(t) for t in TXT]
LO = set(pn(x) for x in FOUR5[1] if pn(x))
LN = set(pn(x) for x in FOUR5[3] if pn(x))
q(u'carry_line_o', len(LO))
q(u'carry_line_n', len(LN))
q(u'carry_shared', len(LO & LN))
q(u'carry_only_o', len(LO - LN))
q(u'carry_only_n', len(LN - LO))
q(u'carry_union', len(LO | LN))
q(u'carry_close', len(LO - LN) + len(LN - LO) + len(LO & LN) - len(LO | LN))
q(u'carry_o_in_n_text', len([x for x in FOUR5[1] if pn(x) and pn(x) in FAN5[3]]))
q(u'carry_n_in_o_text', len([x for x in FOUR5[3] if pn(x) and pn(x) in FAN5[1]]))
q(u'carry_sub_overlap', m(u'carry_o_in_n_text') + m(u'carry_n_in_o_text'))
WJ5 = [u' '.join(t.split()) for t in TXT]
S5 = [set(x for x in re.split(u'(?<=[.:;]) (?=[A-Z])', WJ5[i]) if len(x) >= 20) for i in range(4)]
SO5, SN5 = S5[1], S5[3]
q(u'carry_sent_o', len(SO5))
q(u'carry_sent_n', len(SN5))
q(u'carry_sent_shared', len(SO5 & SN5))
q(u'carry_sent_union', len(SO5 | SN5))
q(u'carry_sent_close', (len(SO5) - len(SO5 & SN5)) + (len(SN5) - len(SO5 & SN5))
  + len(SO5 & SN5) - len(SO5 | SN5))
SR5 = [x for x in FOUR5[1] if pn(x) and pn(x) in LN]
q(u'carry_shared_raw', len(SR5))
q(u'carry_shared_ref', len([x for x in SR5 if u'[RFC' in x]))
q(u'carry_shared_toc', len([x for x in SR5
                            if re.match(u'^\\d+(\\.\\d+)*\\s+\\S', x) and u'[RFC' not in x]))
q(u'carry_shared_prose', m(u'carry_shared_raw') - m(u'carry_shared_ref') - m(u'carry_shared_toc'))
q(u'carry_split_close', m(u'carry_shared_ref') + m(u'carry_shared_toc')
  + m(u'carry_shared_prose') - m(u'carry_shared_raw'))
q(u'carry_sent_rat', len([x for x in (SO5 & SN5) if u'Rationale:' in x]))
q(u'carry_thr_192', len([x for x in (SO5 & SN5) if u'192 bits' in x]))
q(u'carry_thr_224', len([x for x in (SO5 & SN5) if u'224 bits' in x]))
q(u'carry_caliber_gap', m(u'carry_shared') - m(u'carry_sent_shared'))
q4(u'bits_112', lambda i: W2(i, u'112', u'bits'))
q4(u'bits_128', lambda i: W2(i, u'128', u'bits'))
q4(u'bits_192', lambda i: W2(i, u'192', u'bits'))
q4(u'bits_224', lambda i: W2(i, u'224', u'bits'))
q(u'modulus_2048', [bd(TXT[i], u'2048-bit') + TXT[i].count(u'2048 bits') for i in range(4)])
q(u'modulus_1024', [bd(TXT[i], u'1024-bit') + TXT[i].count(u'1024 bits') for i in range(4)])
q4(u'curves_below_224', lambda i: TXT[i].count(u'less than 224 bits'))
q4(u'fwd_secrecy', lambda i: TXT[i].count(u'forward secrecy'))
q4(u'ssl_v2_ban', lambda i: len([l for l in LST[i] if u'MUST NOT negotiate SSL version 2' in l]))

# 锚候选池: 三条规则各自重建, 穿源数按归一串缓存
SPECIAL = (u'SHA-1', u'sha1', u'MUST NOT', u'Rationale:', u'Obsoletes:', u'Updates:')
POOL5 = {}
for i, t in enumerate(TAGS):
    for l in LST[i]:
        s = l.strip()
        if len(s) >= 20 or any(x in s for x in SPECIAL):   # 标题行不设下限, 但只认前 40 行(见下面那个循环)
            POOL5[(t, s)] = 1
    for l in LST[i][:40]:
        s = l.strip()
        if re.match(u'^[0-9.]+\\s+[A-Z]', s):
            POOL5[(t, s)] = 1
CACHE = {}
P5 = []
for (t, s) in POOL5:
    g = pn(s)
    if not g:
        continue
    if g not in CACHE:
        CACHE[g] = len([1 for k in range(4) if g in FAN5[k]])
    P5.append((t, CACHE[g], s))
q(u'pool_n', len(P5))
TN = Counter([x[0] for x in P5])
T1 = Counter([x[0] for x in P5 if x[1] == 1])
q(u'pool_tag_n', [TN[t] for t in TAGS])
q(u'pool_tag_1', [T1[t] for t in TAGS])
q(u'pool_tag_x', [TN[t] - T1[t] for t in TAGS])
TI = Counter([x[1] for x in P5])
q(u'pool_1', TI[1])
q(u'pool_2', TI[2])
q(u'pool_3', TI[3])
q(u'pool_4', TI[4])
q(u'pool_tiers', [m(u'pool_1'), m(u'pool_2'), m(u'pool_3'), m(u'pool_4')])
q(u'pool_close', sum(m(u'pool_tiers')) - m(u'pool_n'))

# 锚: 直读条目正文的 ⟦⟧⟨⟩
EPT = RD(ENTRY)
BODY5 = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', EPT, re.S).group(1)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', BODY5)
tc = Counter([x[0] for x in CITES])
DIS = []
for _, a in CITES:
    if a not in DIS:
        DIS.append(a)
HC = [tuple(i for i in range(4) if pn(a) in FAN5[i]) for a in DIS]
q(u'anchor_total', len(CITES))
q(u'anchor_distinct', len(DIS))
q(u'anchor_err', len([x for x in CITES if not pn(x[1])
                      or pn(x[1]) not in FAN5[TAGS.index(x[0])]]))
q(u'anchor_single', len([h for h in HC if len(h) == 1]))
q(u'anchor_cross', len([h for h in HC if 1 < len(h) < 4]))
q(u'anchor_all4', len([h for h in HC if len(h) == 4]))
q(u'checks', len(DIS) * 4)
q(u'pool_used', len([a for a in DIS if a in [x[2] for x in P5]]))
assert m(u'anchor_single') + m(u'anchor_cross') + m(u'anchor_all4') == m(u'anchor_distinct')
assert len(re.findall(u'⟨', BODY5)) == m(u'anchor_total')
assert m(u'anchor_err') == 0

# 共用源: 这四份字节此前有没有被别的条目当过源
shared = []
for k, v in sorted(SRCALL.items()):
    if k == TAG:
        continue
    for i, g in enumerate(v):
        if any(g.replace(u'\\', u'/') == x.replace(u'\\', u'/') for x in PATHS):
            shared.append((k, i))
assert len(shared) == 0, shared

DJO = json.load(io.open(u'corpus/_deriv57.json', encoding='utf-8'))
OCC = sum(v.count(u'B57V') for v in DJO.values())
COMPOS = [v for v in DJO.values() if u'max([' in v]
assert CH[u'deriv_keys'] == len(DJO) == 105 and CH[u'zero_terms'] == 109, (CH, len(DJO))
assert OCC == 532 and CH[u'deriv_points'] == 239, (OCC, CH[u'deriv_points'])
assert len(CH[u'collisions']) == len(COMPOS) == 30, (len(CH[u'collisions']), len(COMPOS))
# 两枚键只有本遍与 checks 侧有(契约里没登记): prot=写理由的份数, pool_used=锚取自池的条数
assert m(u'pool_used') == CH[u'pool_used'], (m(u'pool_used'), CH[u'pool_used'])
ONLY5 = sorted(k for k in Q5 if k not in FLAT and k not in SNAP)
assert ONLY5 == [u'pool_used', u'prot'], ONLY5

# ---------- 3) 逐处替换 ----------
K = dict(FLAT)
K.update(Q5)
K.update({u'u1': m(u'anchor_single'), u'u23': m(u'anchor_cross'), u'u4': m(u'anchor_all4'),
          u'tT': tc[u'T'], u'tO': tc[u'O'], u'tF': tc[u'F'], u'tN': tc[u'N'],
          u'coll': len(CH[u'collisions']), u'zeros': CH[u'zero_terms'],
          u'deriv_keys': CH[u'deriv_keys'], u'deriv_points': OCC, u'dedup_points': CH[u'deriv_points'],
          u'enc': enc57, u'dig': dig57, u'proofs': proofs, u'nent': NENT, u'nshared': len(shared),
          u'pool_nf': fmt(m(u'pool_n')), u'datet': u' ⇎ '.join(m(u'date_raw')),
          u'gapsum': sum(m(u'month_gap_prev')[1:]),
          u'notinrepo_tot': sum(m(u'cite_obsoletes_notinrepo')),
          u'two_ban': sum(m(u'line_sha_mustnot')),
          u'digset': len(set(DIG)),
          u'bytesT': fmt(m(u'bytes')[0]), u'bytesO': fmt(m(u'bytes')[1]),
          u'bytesF': fmt(m(u'bytes')[2]), u'bytesN': fmt(m(u'bytes')[3]),
          u'nbT': fmt(m(u'nonblank')[0]), u'nbO': fmt(m(u'nonblank')[1]),
          u'nbF': fmt(m(u'nonblank')[2]), u'nbN': fmt(m(u'nonblank')[3]),
          u'ff': FF, u'ffgap': [BLF[i] - BL5[i] for i in range(4)],
          u'wraptot': WRAPTOT, u'wrapT': WRAP[u'2048 bits'], u'legB2': LEGB[2], u'legph': LEGPH,
          u'hyphM': HYPH[u'MUST'], u'hyphS': HYPH[u'SHOULD'], u'wrap': WRAP[u'MUST NOT'],
          u'wrapS': WRAP[u'SHOULD NOT'], u'wrapR': WRAP[u'NOT RECOMMENDED']})

S = io.open(FM, encoding='utf-8').read()
S = sub(u'共 **56 条**（`babeltele/B01..B56`）', u'共 **{nent} 条**（`babeltele/B01..B57`）'.format(**K), S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（56 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（{nent} 条）'.format(**K), S)
S = sub(u'当前 **56 条语料／1215 条**推导全部通过（audit 自报“已机检的推导 1215 条”）',
        u'当前 **{nent} 条语料／{proofs} 条**推导全部通过（audit 自报“已机检的推导 {proofs} 条”）'.format(**K), S)

NEWPAR = (
    u'**B57 把同一个签名哈希交给四份文书各判一次**：`raw/ietf/rfc5246.txt`（1.2 协议 ⟦T⟧：{bytesT} 字节／非空行 {nbT}／'
    u'页标 {pagemarks[0]} 枚） ⇎ `rfc7525.txt`（旧建议 ⟦O⟧：{bytesO} 字节／{nbO}） ⇎ `rfc8446.txt`（1.3 协议 ⟦F⟧：{bytesF} 字节／{nbF}） ⇎ '
    u'`rfc9325.txt`（新建议 ⟦N⟧：{bytesN} 字节／{nbN}）。四份里 SHA-1 的“身份”不同：T 把它写进算法枚举（`SHA-1` {sp_sha1_hy[0]} 次 ⇎ '
    u'小写 `sha1` {sp_sha1_lower[0]} 次 ⇎ 裸 `SHA1` 净 {sp_sha1_net[0]} 次 ⇎ `HMAC-SHA1` {sp_hmac_sha1[0]} 次，非零拼写种数 {sp_case_variants[0]}），'
    u'O 连拼写都不提（`SHA-1` {sp_sha1_hy[1]} ⇎ `sha1` {sp_sha1_lower[1]}，家族合计 {sp_total_sha1_family[1]}，非零种数 {sp_case_variants[1]}），'
    u'F 把它关进 Legacy 枚举块（枚举行 {id_enum_lines[2]} 行／带码点 {id_enum_total[2]} 项，含 sha1 的 {id_sha1_schemes[2]} 项）⇎ '
    u'而那句 MUST support 点名的 {id_must_support_n} 枚里 sha1 {id_must_support_sha1} 枚；块内那 {id_legacy_block[2]} 项是因为 “Legacy algorithms” 这句话在同一份里写了两遍（协议正文的枚举 ⇎ IANA 那节的注册表，这句话出现 {legph[2]} 次、各 {legB2[0]} 枚，只取第一次出现会数成 {legB2[0]}），N 把它与 MD5 并列禁死'
    u'（SHA/MD5 与 MUST NOT 同一行的行数：{line_sha_mustnot[0]} ⇎ {line_sha_mustnot[1]} ⇎ {line_sha_mustnot[2]} ⇎ {line_sha_mustnot[3]}，两份文书各一行 ⇎ 合计 {two_ban} 行）。'
    u'强度词各写各的：MUST NOT {kw_mustnot[0]} ⇎ {kw_mustnot[1]} ⇎ {kw_mustnot[2]} ⇎ {kw_mustnot[3]} ⇎ 纯 MUST '
    u'{kw_must[0]} ⇎ {kw_must[1]} ⇎ {kw_must[2]} ⇎ {kw_must[3]}（两账相加校住 MUST 总数，开口 {kw_close[0]}⇎{kw_close[1]}⇎{kw_close[2]}⇎{kw_close[3]}）；'
    u'`Rationale:` 只有两份写（{kw_rationale[0]} ⇎ {kw_rationale[1]} ⇎ {kw_rationale[2]} ⇎ {kw_rationale[3]}，写理由的份数 {prot}），'
    u'“跨行断开”与“当形容词用”两种写法各吃掉一口径：MUST NOT 换行断开的 {wrap[0]} ⇎ {wrap[1]} ⇎ {wrap[2]} ⇎ {wrap[3]} 处 ⇎ SHOULD NOT 断开 {wrapS[0]} ⇎ {wrapS[1]} ⇎ {wrapS[2]} ⇎ {wrapS[3]} 处（空白分词看得见，要求中间恰一个空格的数法看不见）；'
    u'同一口径差也吃掉门限写法：`2048 bits` 写成跨行的 {wrapT[0]} ⇎ {wrapT[1]} ⇎ {wrapT[2]} ⇎ {wrapT[3]} 处，禁令＋门限两类词的两口径合计差 {wraptot[0]} ⇎ {wraptot[1]} ⇎ {wraptot[2]} ⇎ {wraptot[3]} 处；'
    u'而把强度词写成连字符复合词的只有新建议（`MUST-level` {hyphM[3]} 处 ⇎ `SHOULD-level` {hyphS[3]} 处，前三份 {hyphM[0]}＋{hyphS[0]} ⇎ {hyphM[1]}＋{hyphS[1]} ⇎ {hyphM[2]}＋{hyphS[2]} 处——按空白切词它们不算 MUST，按词边界切就算）；'
    u'MUST NOT 之后 6 行内确有 Rationale 的行数 {line_rationale_mustnot[0]} ⇎ {line_rationale_mustnot[1]} ⇎ {line_rationale_mustnot[2]} ⇎ {line_rationale_mustnot[3]}；'
    u'项目符两种各占一份文书（`o` {kwbullet_o[0]} ⇎ {kwbullet_o[1]} ⇎ {kwbullet_o[2]} ⇎ {kwbullet_o[3]} ⇎ `*` {kwbullet_star[0]} ⇎ {kwbullet_star[1]} ⇎ '
    u'{kwbullet_star[2]} ⇎ {kwbullet_star[3]}，混用两种的 {kw_mix_docs} 份 ⇎ 只用一种的 {kw_bullets_onlyone} 份）。'
    u'阈值词四档排开：`112 bits` {bits_112[0]} ⇎ {bits_112[1]} ⇎ {bits_112[2]} ⇎ {bits_112[3]} ⇎ `128 bits` {bits_128[0]} ⇎ {bits_128[1]} ⇎ {bits_128[2]} ⇎ {bits_128[3]} ⇎ '
    u'`192 bits` {bits_192[0]} ⇎ {bits_192[1]} ⇎ {bits_192[2]} ⇎ {bits_192[3]} ⇎ `224 bits` {bits_224[0]} ⇎ {bits_224[1]} ⇎ {bits_224[2]} ⇎ {bits_224[3]}；'
    u'`2048-bit/2048 bits` {modulus_2048[0]} ⇎ {modulus_2048[1]} ⇎ {modulus_2048[2]} ⇎ {modulus_2048[3]} ⇎ `1024-*` {modulus_1024[0]} ⇎ {modulus_1024[1]} ⇎ '
    u'{modulus_1024[2]} ⇎ {modulus_1024[3]}；`less than 224 bits` {curves_below_224[0]} ⇎ {curves_below_224[1]} ⇎ {curves_below_224[2]} ⇎ {curves_below_224[3]} ⇎ '
    u'`forward secrecy` {fwd_secrecy[0]} ⇎ {fwd_secrecy[1]} ⇎ {fwd_secrecy[2]} ⇎ {fwd_secrecy[3]} ⇎ SSLv2 禁令行 {ssl_v2_ban[0]} ⇎ {ssl_v2_ban[1]} ⇎ {ssl_v2_ban[2]} ⇎ {ssl_v2_ban[3]}。'
    u'套件名的桥只在建议与协议之间：种数 {suite_distinct[0]} ⇎ {suite_distinct[1]} ⇎ {suite_distinct[2]} ⇎ {suite_distinct[3]}（出现处 {suite_occ[0]} ⇎ {suite_occ[1]} ⇎ '
    u'{suite_occ[2]} ⇎ {suite_occ[3]}）；两版协议交集 {suite_common_TF} ⇎ 两份建议交集 {suite_common_ON}；N 的 {suite_N_total} 枚里在 T {suite_from_N_in_T} ⇎ 在 F {suite_from_N_in_F} ⇎ '
    u'两边都不在 {suite_from_N_in_none}（三档相加校住总数，桥差 {suite_bridge_close}），O 的 {suite_O_total} 枚 {suite_from_O_in_T} ⇎ {suite_from_O_in_F} ⇎ {suite_from_O_in_none}（桥差 {suite_O_bridge_close}）；'
    u'T 独有 {suite_T_only} ⇎ F 独有 {suite_F_only}；以 `_SHA` 结尾的套件名 {sp_suite_endsha[0]} ⇎ {sp_suite_endsha[1]} ⇎ {sp_suite_endsha[2]} ⇎ {sp_suite_endsha[3]}，'
    u'T 去重后 {suite_endsha_T} 枚 ⇎ 被截断的下划线碎片行 {frag_tail[0]} ⇎ {frag_tail[1]} ⇎ {frag_tail[2]} ⇎ {frag_tail[3]}。'
    u'谱系：12 个有序引用对里非零 {cite_pairs_nonzero} ⇎ 零 {cite_pairs_zero}，号码在场 {cite_pairs_occ} 处 ⇎ 写成 `RFC nnnn` 的 {cite_rfc_pairs_occ} 处（令牌 {cite_rfc_tokens[0]} ⇎ {cite_rfc_tokens[1]} ⇎ '
    u'{cite_rfc_tokens[2]} ⇎ {cite_rfc_tokens[3]}，去重号 {cite_rfc_distinct[0]} ⇎ {cite_rfc_distinct[1]} ⇎ {cite_rfc_distinct[2]} ⇎ {cite_rfc_distinct[3]} ⇎ 机读方括号形 {cite_bracket[0]} ⇎ {cite_bracket[1]} ⇎ '
    u'{cite_bracket[2]} ⇎ {cite_bracket[3]}）；新建议回指旧建议 {cite_N_to_O} 处 ⇎ 指两份协议 {cite_N_to_T}＋{cite_N_to_F}，反向引用违规 {cite_backward_violations} 处——'
    u'月份号 {month_num[0]} ⇎ {month_num[1]} ⇎ {month_num[2]} ⇎ {month_num[3]}（{datet}）单调 {date_seg_n}／{date_seg_n} 段，段差 {month_gap_prev[1]} ⇎ {month_gap_prev[2]} ⇎ {month_gap_prev[3]}（相加 {gapsum} ＝ 全程 {month_span} 个月），'
    u'文档号与日期同序 {date_docnum_mono} 段；Obsoletes 列出 {cite_obsoletes_n[0]} ⇎ {cite_obsoletes_n[1]} ⇎ {cite_obsoletes_n[2]} ⇎ {cite_obsoletes_n[3]} 枚，'
    u'其中在库 {cite_obsoleted_inrepo[0]} ⇎ {cite_obsoleted_inrepo[1]} ⇎ {cite_obsoleted_inrepo[2]} ⇎ {cite_obsoleted_inrepo[3]}（合计 {cite_obsoleted_inrepo_all}，被废的两份都在库里 ⇎ 不在库 {notinrepo_tot} 枚：'
    u'{cite_obsoletes_notinrepo[0]} ⇎ {cite_obsoletes_notinrepo[1]} ⇎ {cite_obsoletes_notinrepo[2]} ⇎ {cite_obsoletes_notinrepo[3]}，那些要去库外才看得见）。'
    u'两版建议之间的搬运记三口径：整行集交 {carry_shared}（旧 {carry_line_o} ⇎ 新 {carry_line_n}，只旧 {carry_only_o} ⇎ 只新 {carry_only_n}，并集 {carry_union}，闭合差 {carry_close}） ⇎ '
    u'“逐字再现一次”口径 {carry_o_in_n_text}＋{carry_n_in_o_text}＝{carry_sub_overlap}（比集交多 {carry_caliber_gap}，因为它把别人的子串也算搬走） ⇎ '
    u'句子档 {carry_sent_o} ⇎ {carry_sent_n} 句共用 {carry_sent_shared}（并集 {carry_sent_union}，闭合差 {carry_sent_close}）；共用那 {carry_shared_raw} 行的体裁：'
    u'参考文献行 {carry_shared_ref} ⇎ 章节号行 {carry_shared_toc} ⇎ 正文行 {carry_shared_prose}（相加校住，差 {carry_split_close}）——真正“同一条声明原样搬过去”的只有 {carry_shared_prose} 行，'
    u'而其中含 `Rationale:` 的 {carry_sent_rat} 句 ⇎ 含 192/224 bits 阈值的 {carry_thr_192}＋{carry_thr_224} 句（改判那句不在共用池里，两版建议各写各的门限）。'
    u'形状档也留了一处不对齐：{bytegap[0]} ⇎ {bytegap[1]} ⇎ {bytegap[2]} ⇎ {bytegap[3]} 的字节−字符差，'
    u'第四份有 {nonascii[3]} 枚非 ASCII 与 {bom[3]} 枚 BOM 而前三份 {eqc} 份纯 ASCII；页标 {pagemarks[0]} ⇎ {pagemarks[1]} ⇎ {pagemarks[2]} ⇎ {pagemarks[3]} 与页眉 {hdr[0]} ⇎ {hdr[1]} ⇎ {hdr[2]} ⇎ {hdr[3]} '
    u'各差 {page_gap[0]} ⇎ {page_gap[1]} ⇎ {page_gap[2]} ⇎ {page_gap[3]}——前三份是分页印刷版 `.txt`，第四份根本没有页标（署名行 {author_hdr[0]} ⇎ {author_hdr[1]} ⇎ {author_hdr[2]} ⇎ {author_hdr[3]}）；'
    u'断行本身也有两套口径：换页符 {ff[0]} ⇎ {ff[1]} ⇎ {ff[2]} ⇎ {ff[3]} 枚，按换行数出的空行 {blank[0]} ⇎ {blank[1]} ⇎ {blank[2]} ⇎ {blank[3]}，'
    u'按“换页也算断行”数则多 {ffgap[0]} ⇎ {ffgap[1]} ⇎ {ffgap[2]} ⇎ {ffgap[3]} 段，多的恰是换页符数；'
    u'四份字节四种签名 {digset} 种（本遍用 blake2b 8 字节，建条目侧用 sha256 前 16 位，两种算法各数出 4 种）。'
    u'锚候选池 {pool_nf} 条（每源 {pool_tag_n[0]} ⇎ {pool_tag_n[1]} ⇎ {pool_tag_n[2]} ⇎ {pool_tag_n[3]}），穿一源 {pool_1} ⇎ 两源 {pool_2} ⇎ 三源 {pool_3} ⇎ 四源 {pool_4}（相加校住池，差 {pool_close}）；'
    u'登记锚 {anchor_total} 处／{anchor_distinct} 个不同串（每标签 T {tT} ⇎ O {tO} ⇎ F {tF} ⇎ N {tN}；单源 {u1} ⇎ 穿二或三源 {u23} ⇎ 四源全现 {u4}，归属检查 {checks} 次，错配 {anchor_err}）。'
    u'共用源 {nshared} 处（这四份 IETF 字节此前没被任何条目当过源）。'
    u'“四份之外还有几份文书在判同一个哈希”（AES-GCM 与 ECDHE 那一族，本库只收这四份）“IANA 此刻是否还把 sha1 系签名算法列在可协商的注册表里”'
    u'不可由在库文件判定，判词按第三档写、门槛不背书。\n')

ANCHOR_OLD = (u'“ISO 官方此刻在用哪一个名串”“注册表把 East Timor 留在已弃码 TP 而把 TL 另立的流程理由”'
              u'不可由在库文件判定，判词按第三档写、门槛不背书。\n')
S = sub(ANCHOR_OLD, ANCHOR_OLD + NEWPAR.format(**K), S)

ROW57 = (u'| B57 | {enc}（新建, 四份规范判同一个哈希 {anchor_total} 处标注／{anchor_distinct} 个不同串（登记 {anchor_distinct} 条锚全命中, '
         u'每标签 T {tT} ⇎ O {tO} ⇎ F {tF} ⇎ N {tN}, 归属检查 {checks} 次）: 四色锚位 1.2 协议 ⟦T⟧ ⇎ 旧建议 ⟦O⟧ ⇎ 1.3 协议 ⟦F⟧ ⇎ 新建议 ⟦N⟧; '
         u'头条是“同一个哈希在四份文书里各有身份”——写进枚举 {sp_sha1_hy[0]} 次 ⇎ 连拼写都不提 {sp_sha1_hy[1]} 次 ⇎ 关进 Legacy 块 {id_sha1_schemes[2]} 项（MUST support 的 {id_must_support_n} 枚里 sha1 {id_must_support_sha1}）⇎ 与 MD5 并列禁死 {line_sha_mustnot[3]} 行; '
         u'`Rationale:` {kw_rationale[0]}⇎{kw_rationale[1]}⇎{kw_rationale[2]}⇎{kw_rationale[3]}（写理由的份数 {prot}）⇎ MUST NOT 后 6 行内有理由 {line_rationale_mustnot[0]}⇎{line_rationale_mustnot[1]}⇎{line_rationale_mustnot[2]}⇎{line_rationale_mustnot[3]}; '
         u'项目符 `o`⇎`*` 各只在一份（混用 {kw_mix_docs} ⇎ 只用一种 {kw_bullets_onlyone}）; 阈值四档 112 {bits_112[0]}⇎{bits_112[1]}⇎{bits_112[2]}⇎{bits_112[3]} ⇎ 224 {bits_224[0]}⇎{bits_224[1]}⇎{bits_224[2]}⇎{bits_224[3]} ⇎ '
         u'曲线 `less than 224 bits` {curves_below_224[3]} ⇎ forward secrecy {fwd_secrecy[0]}⇎{fwd_secrecy[1]}⇎{fwd_secrecy[2]}⇎{fwd_secrecy[3]}; '
         u'套件桥 {suite_distinct[0]}⇎{suite_distinct[1]}⇎{suite_distinct[2]}⇎{suite_distinct[3]} 种: 协议两版交集 {suite_common_TF}（整套换了名）⇎ 两份建议交集 {suite_common_ON}, N 的 {suite_N_total} 枚 {suite_from_N_in_T}⇎{suite_from_N_in_F}⇎{suite_from_N_in_none}(桥差 {suite_bridge_close}) ⇎ O 的 {suite_O_total} 枚 {suite_from_O_in_T}⇎{suite_from_O_in_F}⇎{suite_from_O_in_none}(桥差 {suite_O_bridge_close}) ⇎ T 独 {suite_T_only}／F 独 {suite_F_only}; '
         u'谱系 12 对里非零 {cite_pairs_nonzero}⇎零 {cite_pairs_zero}, 反向违规 {cite_backward_violations}, 月份差 {month_gap_prev[1]}⇎{month_gap_prev[2]}⇎{month_gap_prev[3]} 相加 {gapsum}＝全程 {month_span}, Obsoletes 在库 {cite_obsoleted_inrepo_all}⇎不在库 {notinrepo_tot}; '
         u'搬运三口径 整行交 {carry_shared}（并集 {carry_union}, 闭合差 {carry_close}）⇎ 子串再现 {carry_sub_overlap}（口径差 {carry_caliber_gap}）⇎ 句子档共用 {carry_sent_shared}（其中 Rationale {carry_sent_rat} ⇎ 阈值 {carry_thr_192}＋{carry_thr_224}）, 体裁 参考文献 {carry_shared_ref}⇎章节号 {carry_shared_toc}⇎正文 {carry_shared_prose}(差 {carry_split_close}); '
         u'形状 字节−字符差 {bytegap[0]}⇎{bytegap[1]}⇎{bytegap[2]}⇎{bytegap[3]}（非 ASCII {nonascii[3]} ⇎ BOM {bom[3]}）⇎ 页标−页眉差 {page_gap[0]}⇎{page_gap[1]}⇎{page_gap[2]}⇎{page_gap[3]} ⇎ 换页符断行多出 {ffgap[0]}⇎{ffgap[1]}⇎{ffgap[2]}⇎{ffgap[3]} 段; '
         u'锚池 {pool_nf} 条穿四源 {pool_4} ⇎ 三源 {pool_3}; 同数共键复合式 {coll} 组、零项 {zeros} 枚折成一条算式; '
         u'门槛侧 {deriv_keys} 枚推导键／{deriv_points} 处 B57V 引用点（建条目侧按“值→算式”去重记 {dedup_points}），四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 {anchor_distinct} 条锚逐字全命中） |\n')
anchor_row = (u'门槛侧 72 枚推导键／274 处 B56V 引用点，四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 26 条锚逐字全命中） |\n')
assert S.count(anchor_row) == 1
S = sub(anchor_row, anchor_row + ROW57.format(**K), S)

lin = (u'第二代（B11–B56）锚内字母 **117 845**、锚外 **12 174**；全库合计 **117 966／14 369**'
       u'（B56 一枚条目贡献 653／479, 由建条目侧现数）')
S = sub(lin, (u'第二代（B11–B57）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
              u'（B57 一枚条目贡献 %s／%s, 由建条目侧现数）'
              % (fmt(117845 + CH[u'letters_in']), fmt(12174 + CH[u'letters_out']),
                 fmt(117966 + CH[u'letters_in']), fmt(14369 + CH[u'letters_out']),
                 fmt(CH[u'letters_in']), fmt(CH[u'letters_out']))), S)

RAW57 = (u'| B57 | `raw/ietf/rfc5246.txt`（1.2 协议 ⟦T⟧：{bytesT} 字节／非空行 {nbT}／`SHA-1` {sp_sha1_hy[0]} 次／`Rationale:` {kw_rationale[0]} 条／页标 {pagemarks[0]} 枚／`TLS_` 套件 {suite_distinct[0]} 种） ⇎ '
         u'`raw/ietf/rfc7525.txt`（旧建议 ⟦O⟧：{bytesO} 字节／{nbO}／`SHA-1` {sp_sha1_hy[1]} 次／`Rationale:` {kw_rationale[1]} 条／`o` 项目行 {kwbullet_o[1]}） ⇎ '
         u'`raw/ietf/rfc8446.txt`（1.3 协议 ⟦F⟧：{bytesF} 字节／{nbF}／枚举 {id_enum_total[2]} 项（Legacy 块 {id_legacy_block[2]}）／套件 {suite_distinct[2]} 种／`Rationale:` {kw_rationale[2]} 条） ⇎ '
         u'`raw/ietf/rfc9325.txt`（新建议 ⟦N⟧：{bytesN} 字节／{nbN}／无页标 {pagemarks[3]} 枚／BOM {bom[3]} 枚／`*` 项目行 {kwbullet_star[3]}／`Rationale:` {kw_rationale[3]} 条） | '
         u'四份规范判同一个哈希 ⇒ 同一个 SHA-1 四种身份: 枚举里的一个值 {sp_sha1_hy[0]}⇎连拼写都不提 {sp_sha1_hy[1]}⇎关进遗留块并留豁免 {id_sha1_schemes[2]}⇎与 MD5 并列禁死 {line_sha_mustnot[3]}; '
         u'两份建议之间整行共用 {carry_shared} ⇎ 正文行只 {carry_shared_prose} ⇎ 句子档共用 {carry_sent_shared}，而含门限的改判句在共用池里 {carry_thr_192}＋{carry_thr_224} 处命中|\n')
anchor2 = (u'同名对 249 双里逐字等 202 ⇎ 不等 47（只换写法 10 ⇎ 换词 37）|\n')
assert S.count(anchor2) == 1
S = sub(anchor2, anchor2 + RAW57.format(**K), S)

row_tot = (u'| **合计（{nent} 条）** | **{enct}** | **{rett}**（摘要段合计 {digt}） | — | **{unqt}** | — |\n').format(
    nent=NENT, enct=fmt(enc_all).replace(u',', u' '), rett=ret_tot,
    digt=fmt(dig_all).replace(u',', u' '), unqt=fmt(uniq_all).replace(u',', u' '))
old_tot = re.search(u'[|] [*]{2}合计（56 条）[*]{2}[^\n]*\n', S)
assert old_tot
S = S.replace(old_tot.group(0), row_tot)

# 残余提示: 条目号与枚数一律从 audit 的当下清单生成, 不手抄
PROSE = set(u'B03 B06 B09 B15 B27 B28 B29 B30 B31 B44 B48 B49 B50 B51 B52'.split())
extra = sorted([k for k in HINT if k not in PROSE])
EMPTY = [k for k in (u'B54', u'B56', u'B57') if k not in HINT]
xstr = u' ⇎ '.join(u'%s 的 `%s`' % (k, u'／'.join(HINT[k])) for k in extra)
tail_old = u'由 _b52_scan 照样复算））未逐位核验，'
assert S.count(tail_old) == 1
S = sub(tail_old, (u'由 _b52_scan 照样复算）；%s 是后建的对照条里同样的 1–2 位计数，一并按未核记着（清单取自 audit 当下输出）；'
                   u'新建的 %s 同样为空——B57 把两位以内的结构计数全部折进了 DERIV（0 项 %d 枚并成一条算式，由 _b57_scan 照样复算））'
                   u'未逐位核验，'
                   % (xstr, u' ⇎ '.join(EMPTY), CH[u'zero_terms'])), S)
S = sub(u'残余提示（不计 FAIL）：17 个', u'残余提示（不计 FAIL）：%d 个' % soft_all, S)

CMD = (u'python -X utf8 corpus/_mkB57.py                  # 建条目: 扁平契约 %d 枚键／DERIV %d 枚算式, 占位符未替换 0 个\n'
       u'python -X utf8 corpus/_mkdigest3.py B57 <entry> T corpus/raw/ietf/rfc5246.txt %d %d '
       u'O corpus/raw/ietf/rfc7525.txt %d %d F corpus/raw/ietf/rfc8446.txt %d %d '
       u'N corpus/raw/ietf/rfc9325.txt %d %d   # 四源分节摘要(%s 字符, 窗口按 %d⇎%d 取句边界)\n'
       u'python -X utf8 corpus/_wire57.py                    # 把 SCAN 段机械切进 audit.py::_b57_scan 并插 DERIV[\'B57\']\n'
       u'python -X utf8 corpus/_fill57.py                    # 第四遍: 现取注数并把 ⛓解读注 写回条目(与契约 %d 键逐一对表)\n'
       u'python -X utf8 corpus/atomcheck.py B57 corpus/_atoms57.txt   # 工具侧独立逐字校验: ok=%d bad=0\n'
       % (len(FLAT), CH[u'deriv_keys'], WL57, WR57, WL57, WR57, WL57, WR57, WL57, WR57,
          fmt(dig57).replace(u',', u' '), WL57, WR57, len(FLAT), CH[u'anchor_distinct']))
anchor3 = u'python -X utf8 corpus/atomcheck.py B56 corpus/_atoms56.txt   # 工具侧独立逐字校验: ok=26 bad=0' + NL
assert S.count(anchor3) == 1
S = sub(anchor3, anchor3 + CMD, S)

io.open(FM, 'w', encoding='utf-8', newline=NL).write(S)
print(u'README 已记账: %d 条 ｜ 编码合计 %s ⇎ 摘要合计 %s ⇎ 合计保留率 %s ｜ 唯一码点 %d ｜ 推导 %d 条 ｜ 提示 %d（清单 %s） ｜ '
      u'B57 %s 字符／%d 锚(%d 串, T %d⇎O %d⇎F %d⇎N %d, 单源 %d⇎穿二三 %d⇎四源 %d, 检查 %d) ｜ '
      u'第五遍: 现量 %d 个键全等契约⇎快照 ｜ 强度词 MUST NOT %s ⇎ Rationale %s ｜ 套件桥 N %d⇎%d⇎%d ⇎ O %d⇎%d⇎%d ｜ '
      u'引用非零 %d／12 反向违规 %d ⇎ 月份差和 %d＝%d ｜ 搬运 整行 %d⇎子串 %d⇎句 %d(体裁 %d⇎%d⇎%d) ｜ '
      u'池 %d 穿四源 %d ⇎ 用锚 %d ｜ 签名 %d 种(blake2b) ｜ 引用点 %d 文本⇎%d 去重 ｜ 共用源 %d 处'
      % (NENT, fmt(enc_all), fmt(dig_all), ret_tot, uniq_all, proofs, soft_all,
         u' '.join(sorted(HINT)), fmt(enc57), m(u'anchor_total'), m(u'anchor_distinct'),
         tc[u'T'], tc[u'O'], tc[u'F'], tc[u'N'], m(u'anchor_single'), m(u'anchor_cross'),
         m(u'anchor_all4'), m(u'checks'), len(Q5),
         u'⇎'.join(str(x) for x in m(u'kw_mustnot')), u'⇎'.join(str(x) for x in m(u'kw_rationale')),
         m(u'suite_from_N_in_T'), m(u'suite_from_N_in_F'), m(u'suite_from_N_in_none'),
         m(u'suite_from_O_in_T'), m(u'suite_from_O_in_F'), m(u'suite_from_O_in_none'),
         m(u'cite_pairs_nonzero'), m(u'cite_backward_violations'),
         sum(m(u'month_gap_prev')[1:]), m(u'month_span'),
         m(u'carry_shared'), m(u'carry_sub_overlap'), m(u'carry_sent_shared'),
         m(u'carry_shared_ref'), m(u'carry_shared_toc'), m(u'carry_shared_prose'),
         m(u'pool_n'), m(u'pool_4'), m(u'pool_used'), len(set(DIG)), OCC, CH[u'deriv_points'],
         len(shared)))
