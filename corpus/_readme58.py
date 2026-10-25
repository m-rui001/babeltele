# -*- coding: utf-8 -*-
"""README 记账: 57 条 → 58 条。合计、唯一码点、推导条数全部取自 audit 的当下输出, 不手填。
本文件是第五套实现, 换算法不换定义:
形状档从字节走起(rb 计数／rb.split(b'\\n')／BOM 看前三字节／最长行用排序取尾), 建条目侧用的是 os.path.getsize 与 str.split('\\n');
标签计数与实体计数改成按 '<' 与 '&' 手工分段扫描(建条目侧是三条正则, 门槛侧 _detag 又是另外三条);
词面指纹一律走 str.find 逐次游标(建条目侧与解读注侧都用 .count);
转码层重写成一台状态机: 注释删成空串、只把 <br> 替成分隔符、其余标签删净、数字实体按码位解、命名实体查表——
建条目侧按固定映射表 replace, 门槛侧把块级标签替成空格, 三套口径互不相同;
四份字节的签名摘要换 blake2b 8 字节(建条目侧用 sha256 前 16 位), 只比种数不比串;
向量出现档走 finditer 逐条取 group(建条目侧 findall 后再 startswith);
锚的穿源档按条目正文的 ⟨⟩ 直读, 再拿每条串到四份渲染文里现验(建条目侧按池位置推, 门槛侧按归属表查).
每个数与两份快照对表: 建条目侧扁平契约 corpus/_b58flat.json ⇎ 门槛侧 corpus/_b58audit.json。任一标量对不上就当场停机。
算术族(2592 全空间同分、114⇎6 单调账、38 对配对分数)不在本遍另算: 它们由第四遍 _fill58.py 与门槛侧 _b58_scan 各自独立复现, 本遍只与两份快照对表。"""
import hashlib, io, json, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
FM = u'corpus/README.md'
NL = chr(10)
TAG = u'B58'
ENTRY = u'corpus/babeltele/B58_one_vector_three_arithmetics.md'
PATHS = [u'corpus/raw/cvss/cvss_v30_spec.html', u'corpus/raw/cvss/cvss_v31_spec.html',
         u'corpus/raw/cvss/cvss_v40_spec.html', u'corpus/raw/cvss/cvss_examples.html']
TAGS = [u'T', u'O', u'F', u'N']
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')
RD = lambda q: io.open(q, encoding='utf-8', errors='replace').read()

ENT = {u'nbsp': u' ', u'amp': u'&', u'lt': u'<', u'gt': u'>', u'quot': u'"', u'apos': u"'",
       u'times': u'x', u'minus': u'-', u'rarr': u'->', u'larr': u'<-', u'mdash': u'-',
       u'ndash': u'-', u'deg': u'deg', u'infin': u'inf', u'hellip': u'...', u'ge': u'>=',
       u'le': u'<='}
UNI = [(u' ', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
       (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->')]
VOCAB = (u'None', u'Low', u'Medium', u'High', u'Critical', u'Negligible')
WORDS = [(u'ar_ru', u'Roundup'), (u'ar_ru_up', u'Round up'), (u'ar_k642', u'6.42'),
         (u'ar_k752', u'7.52'), (u'ar_k822', u'8.22'), (u'ar_k108', u'1.08'),
         (u'ar_k9731', u'0.9731'), (u'ar_k0915', u'0.915'), (u'ar_pseudo', u'pseudocode'),
         (u'ar_appA', u'Appendix A'), (u'ar_floattrap', u'0.30000000000000004'),
         (u'bl_mv', u'MacroVector'), (u'bl_lookup', u'lookup table'),
         (u'bl_interp', u'interpolation'), (u'bl_cons', u'Constraints'),
         (u'sp_negligible', u'Negligible'), (u'sp_prov_urg', u'Provider Urgency'),
         (u'sp_exploitability', u'Exploitability'), (u'sp_isc', u'ISCBase'),
         (u'sp_iss', u'ISS'), (u'sp_miss', u'MISS'),
         (u'sp_diff30', u'differs from CVSS v3.0'), (u'sp_safety', u'Safety')]
BODYW = [(u'ar_ru_body', u'Roundup'), (u'ar_ru_up_body', u'Round up'), (u'bl_mv_body', u'MacroVector'),
         (u'bl_lookup_body', u'lookup table'), (u'bl_interp_body', u'interpolation'),
         (u'bl_cons_body', u'constraints'), (u'sp_negligible_body', u'Negligible')]


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
assert NENT == 58, NENT
b58, A = row[u'B58'], row[u'ALL']
dig_all, enc_all = int(A[0].replace(u' ', u'')), int(A[1].replace(u' ', u''))
uniq_all = int(re.sub(u'[^0-9]', u'', A[4]))
assert (sum(int(v[0]) for k, v in row.items() if k != u'ALL'),
        sum(int(v[1]) for k, v in row.items() if k != u'ALL')) == (dig_all, enc_all)
assert int(b58[5]) == 9 and b58[7:11] == [u'0', u'0', u'0', u'0'], b58
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
assert soft_all == 20 and proofs == 1405, (soft_all, proofs)
assert sum(len(v) for v in HINT.values()) == soft_all, (HINT, soft_all)
assert u'B58' not in HINT, HINT.get(u'B58')
dig58, enc58 = int(b58[0]), int(b58[1])
ret_tot = A[2].replace(u'*', u'')

# ---------- 2) 第五遍: 自己从四份字节现量 ----------
CH = json.load(io.open(u'corpus/_b58checks.json', encoding='utf-8'))
FLAT = json.load(io.open(u'corpus/_b58flat.json', encoding='utf-8'))
SN = json.load(io.open(u'corpus/_b58audit.json', encoding='utf-8'))
SNAP, SRCALL = SN[TAG], SN[u'SRC']
assert enc58 == CH[u'enc_chars'] and dig58 == 3254, (enc58, CH[u'enc_chars'], dig58)

RB = [io.open(q, 'rb').read() for q in PATHS]
TXT = [r.decode(u'utf-8') for r in RB]        # 严格解码: 与建条目侧的 errors='replace' 走法不同
assert [len(TXT[i]) for i in range(4)] == FLAT[u'chars']
Q5 = {}


def q(name, val):
    Q5[name] = val
    if name in FLAT:
        assert rnd(val) == rnd(FLAT[name]), (name, val, FLAT[name])
    if name in SNAP:
        assert rnd(val) == rnd(SNAP[name]), (name, u'快照', val, SNAP[name])
    return val


def m(name):
    return Q5[name]


def q4(name, f):
    v = [f(k) for k in range(4)]
    q(name, v)
    return v


def hcnt(hay, word):
    """子词出现处数: 逐次 find 游标, 不用 .count(建条目侧与解读注侧都是 .count)。"""
    n, k = 0, hay.find(word)
    while k >= 0:
        n += 1
        k = hay.find(word, k + len(word))
    return n


def tagcount(low, head):
    """<table / <tr / <br / <sup 这类标签前缀: 按 '<' 手工分段扫, 只认字母开头的标签名。"""
    n, k = 0, low.find(u'<')
    while k >= 0:
        e = low.find(u'>', k)
        if e < 0:
            break
        nm = low[k + 1:e]
        j = 0
        while j < len(nm) and nm[j] not in u' >/':
            j += 1
        if nm[:j].startswith(head):
            n += 1
        k = low.find(u'<', k + 1)
    return n


def hcount(low):
    """<h1>..<h6> 且紧随空格或 '>': 逐枚 <h 命中后看尾字符。"""
    n, k = 0, low.find(u'<h')
    while k >= 0:
        a, b = low[k + 2:k + 3], low[k + 3:k + 4]
        if a in u'123456' and b in (u' ', u'>'):
            n += 1
        k = low.find(u'<h', k + 2)
    return n


def entcount(s):
    n, k = 0, s.find(u'&')
    while k >= 0:
        j = k + 1
        while j < len(s) and (s[j].isalnum() or s[j] == u'#'):
            j += 1
        if j > k + 1 and j < len(s) and s[j] == u';':
            n += 1
            k = s.find(u'&', j + 1)
        else:
            k = s.find(u'&', k + 1)
    return n


def render(s, br=u' '):
    """转码层状态机: 注释删空 → 只把 <br> 替成 br → 其余标签删净 → 实体/Unicode 折 ASCII → 并空白."""
    out, k = [], 0
    while True:
        j = s.find(u'<', k)
        if j < 0:
            out.append(s[k:])
            break
        out.append(s[k:j])
        if s.startswith(u'<!--', j):
            e = s.find(u'-->', j)
            k = len(s) if e < 0 else e + 3
            continue
        e = s.find(u'>', j)
        if e < 0:
            out.append(s[j:])
            break
        nm = re.match(u'(?is)/?([a-zA-Z][a-zA-Z0-9]*)', s[j + 1:e])
        out.append(br if (nm and nm.group(1).lower() == u'br') else u'')
        k = e + 1
    s = u''.join(out)
    s = re.sub(u'&#(\\d+);', lambda x: chr(int(x.group(1))), s)
    s = re.sub(u'&#x([0-9a-fA-F]+);', lambda x: chr(int(x.group(1), 16)), s)
    s = re.sub(u'&([a-zA-Z]+);', lambda x: ENT.get(x.group(1).lower(), x.group(0)), s)
    for a, b in UNI:
        s = s.replace(a, b)
    return re.sub(u'[ \t]+', u' ', s).strip()


B5 = [render(TXT[i]) for i in range(4)]
L5 = [[render(l, u' | ') for l in TXT[i].split(NL)] for i in range(4)]
LOW = [TXT[i].lower() for i in range(4)]

# 形状档: 全部从字节走起
q4(u'bytes', lambda i: len(RB[i]))
q4(u'chars', lambda i: len(TXT[i]))
q4(u'lines', lambda i: RB[i].count(b'\n'))
NB5 = []
for i in range(4):
    n = 0
    for l in TXT[i].split(NL):
        n += 1 if l.strip() else 0
    NB5.append(n)
q(u'nonblank', NB5)
q4(u'tabs', lambda i: RB[i].count(b'\t'))
q4(u'nonascii', lambda i: len([c for c in TXT[i] if ord(c) > 127]))
q4(u'bom', lambda i: 1 if RB[i][:3] == b'\xef\xbb\xbf' else 0)
q4(u'final_nl', lambda i: 1 if RB[i].endswith(b'\n') else 0)
q4(u'maxlen', lambda i: max([len(x) for x in [l.decode(u'utf-8') for l in RB[i].split(b'\n')]]))
q4(u'meanlen', lambda i: int(round(1.0 * sum(len(l) for l in TXT[i].split(NL) if l.strip()) /
                                   m(u'nonblank')[i])))
LINES5 = [sorted([len(l) for l in TXT[i].split(NL)], reverse=True) for i in range(4)]
q(u'maxline_len', [x[0] for x in LINES5])
TAIL = []
for i in range(4):
    best, bl = u'', 0
    for l in TXT[i].split(NL):        # 取“第一条最长行”, 与建条目侧 max(key=len) 同定义、不同写法
        if len(l) > bl:
            best, bl = l, len(l)
    TAIL.append(best)
q(u'maxline_shared', 1 if len(set(TAIL)) == 1 else 0)
q4(u'table_tags', lambda i: tagcount(LOW[i], u'table'))
q4(u'tr_rows', lambda i: tagcount(LOW[i], u'tr'))
q4(u'br_tags', lambda i: tagcount(LOW[i], u'br'))
q4(u'sup_tags', lambda i: tagcount(LOW[i], u'sup'))
q(u'tr_rows_ratio', m(u'tr_rows')[3] // m(u'tr_rows')[0])
q(u'tr_rows_rest', m(u'tr_rows')[3] % m(u'tr_rows')[0])
q(u'tr_rows_div_close', m(u'tr_rows')[0] * m(u'tr_rows_ratio') + m(u'tr_rows_rest') - m(u'tr_rows')[3])
q4(u'h_all', lambda i: hcount(LOW[i]))
q4(u'ent_all', lambda i: entcount(TXT[i]))
q4(u'ent_lt', lambda i: hcnt(TXT[i], u'&lt;'))
q4(u'minusuni', lambda i: len([1 for c in TXT[i] if c == u'−']))
q4(u'nbsp', lambda i: hcnt(TXT[i], u'&nbsp;') + len([c for c in TXT[i] if c == u' ']))
B2 = [hashlib.blake2b(RB[i], digest_size=8).hexdigest() for i in range(4)]
q(u'sha_distinct', len(set(B2)))

# 词面指纹: 原文侧走游标, 渲染侧走状态机后的游标
for nm, w in WORDS:
    q(nm, [hcnt(TXT[i], w) for i in range(4)])
for nm, w in BODYW:
    q(nm, [hcnt(B5[i], w) for i in range(4)])
q(u'arith_any', [1 if (hcnt(B5[i], u'Roundup') + hcnt(B5[i], u'Round up') + hcnt(B5[i], u'8.22')) else 0
                 for i in range(4)])
q(u'name_variants', [[hcnt(TXT[i], w) for w in (u'Privilege Required', u'Privileges Required',
                                                u'Adjacent Network', u'Adjacent')] for i in range(4)])
for nm, i, j in ((u'v30_sg', 0, 0), (u'v30_pl', 0, 1), (u'v30_adjnet', 0, 2),
                 (u'v31_sg', 1, 0), (u'v31_pl', 1, 1), (u'v31_adjnet', 1, 2)):
    q(nm, m(u'name_variants')[i][j])

# 向量出现档: finditer 逐条取串(建条目侧 findall 后 startswith)
VECR = re.compile(u'CVSS:[34]\\.\\d(?:/[A-Z]{1,4}:[^/\\s"<>|&]+)+')
VS = [[x.group(0) for x in VECR.finditer(B5[i])] for i in range(4)]
q(u'vec_occ', [len(x) for x in VS])
q(u'vec_distinct', [len(set(x)) for x in VS])
q(u'vec_occ_31', [len([x for x in VS[i] if x[:8] == u'CVSS:3.1']) for i in range(4)])
q(u'vec_occ_40', [len([x for x in VS[i] if x[:8] == u'CVSS:4.0']) for i in range(4)])
q(u'vec_pr_doublecolon', [hcnt(B5[i], u'PR::') for i in range(4)])


def wb(hay, word):
    """词边界口径: 逐次 find 再查左右邻(建条目侧用 .count, 解读注侧用  正则)。"""
    n, k = 0, hay.find(word)
    while k >= 0:
        a = hay[k - 1] if k else u''
        b = hay[k + len(word)] if k + len(word) < len(hay) else u''
        n += 1 if not (a.isalnum() or b.isalnum()) else 0
        k = hay.find(word, k + 1)
    return n


q(u'bl_mv_wb', [wb(B5[i], u'MacroVector') for i in range(4)])
assert m(u'bl_mv_wb')[2] <= m(u'bl_mv_body')[2]
q(u'sp_isc_ren', [hcnt(B5[i], u'ISCBase') for i in range(4)])
q(u'sp_iss_ren', [hcnt(B5[i], u'ISS') for i in range(4)])
q(u'sp_miss_ren', [hcnt(B5[i], u'MISS') for i in range(4)])
assert m(u'sp_isc_ren')[0] >= 1 and m(u'sp_isc')[0] == 0
q(u'band_vocab_inbody', [sorted([x for x in VOCAB if x in B5[i]]) for i in range(4)])
q(u'band_label_lines', [len([x for x in VOCAB if x in [l.strip() for l in L5[i]]]) for i in range(4)])

# 锚: 从条目正文直读 ⟨⟩, 再拿每条串到四份渲染文里现验
T5 = io.open(ENTRY, encoding='utf-8').read()
BODYREG = T5[T5.index(u'⟪BabelTele⟫'):T5.index(u'## ⛓解读注')]
CAND = re.findall(u'⟨([^⟩]+)⟩', BODYREG)
DIS = sorted(set(CAND))


def pn5(x):
    """锚归属口径: 剥壳后只留 ascii 字母数字(建条目侧同口径, 但那里用正则剥壳、这里用状态机;
    门槛侧 T3 用的是保留点号与空格的另一档, 那一档更松, 只用于逐字命中校验)。"""
    return u''.join([c for c in x.lower() if c.isalnum() and c.isascii()])


PB = [pn5(B5[i]) for i in range(4)]
HC = dict((a, [t for t in range(4) if pn5(a) in PB[t]]) for a in DIS)
q(u'anchor_total', len(CAND))
q(u'anchor_distinct', len(DIS))
q(u'anchor_single', len([h for h in HC.values() if len(h) == 1]))
q(u'anchor_cross', len([h for h in HC.values() if 1 < len(h) < 4]))
q(u'anchor_all4', len([h for h in HC.values() if len(h) == 4]))
q(u'anchor_err', len([a for a in CAND if not HC.get(a)]))
q(u'checks', len(DIS) * 4)
assert m(u'anchor_single') + m(u'anchor_cross') + m(u'anchor_all4') == m(u'anchor_distinct')
assert m(u'anchor_err') == 0
tc = {}
for tg in TAGS:
    seg = BODYREG[BODYREG.index(u'⟦%s⟧' % tg):] if u'⟦%s⟧' % tg in BODYREG else u''
    tc[tg] = 0
lab = re.findall(u'⟦([TOFN])⟧|⟨([^⟩]+)⟩', BODYREG)
cur, tc = None, dict((t, 0) for t in TAGS)
for a, b in lab:
    if a:
        cur = a
    elif b is not None and a == u'':
        tc[cur] += 1 if cur else 0
assert sum(tc.values()) == m(u'anchor_total'), tc
assert tc == CH[u'tag_counts'], (tc, CH[u'tag_counts'])

# 共用源: 这四份字节此前有没有被别的条目当过源
shared = []
for k, v in sorted(SRCALL.items()):
    if k == TAG:
        continue
    for g in v:
        if any(g.replace(u'\\', u'/') == x.replace(u'\\', u'/') for x in PATHS):
            shared.append((k, g))
assert len(shared) == 0, shared

DJO = json.load(io.open(u'corpus/_deriv58.json', encoding='utf-8'))
OCC = sum(v.count(u'B58V') for v in DJO.values())
assert CH[u'deriv_keys'] == len(DJO) == 98 and CH[u'zero_terms'] == 112, (CH, len(DJO))
assert OCC == 534 and CH[u'deriv_points'] == 233, (OCC, CH[u'deriv_points'])
assert len(CH[u'collisions']) == 35, len(CH[u'collisions'])
ONLY5 = sorted(k for k in Q5 if k not in FLAT and k not in SNAP)
assert ONLY5 == [u'bl_mv_wb', u'sp_isc_ren', u'sp_iss_ren', u'sp_miss_ren'], ONLY5

# ---------- 3) 逐处替换 ----------
K = dict(FLAT)
K.update(Q5)
K.update({u'u1': m(u'anchor_single'), u'u23': m(u'anchor_cross'), u'u4': m(u'anchor_all4'),
          u'tT': tc[u'T'], u'tO': tc[u'O'], u'tF': tc[u'F'], u'tN': tc[u'N'],
          u'coll': len(CH[u'collisions']), u'zeros': CH[u'zero_terms'],
          u'deriv_keys': CH[u'deriv_keys'], u'deriv_points': OCC, u'dedup_points': CH[u'deriv_points'],
          u'enc': enc58, u'dig': dig58, u'proofs': proofs, u'nent': NENT, u'nshared': len(shared),
          u'pool_nf': fmt(m(u'pool_n') if u'pool_n' in Q5 else FLAT[u'pool_n']),
          u'bytesT': fmt(m(u'bytes')[0]), u'bytesO': fmt(m(u'bytes')[1]),
          u'bytesF': fmt(m(u'bytes')[2]), u'bytesN': fmt(m(u'bytes')[3]),
          u'nbT': fmt(m(u'nonblank')[0]), u'nbO': fmt(m(u'nonblank')[1]),
          u'nbF': fmt(m(u'nonblank')[2]), u'nbN': fmt(m(u'nonblank')[3]),
          u'lnT': fmt(m(u'lines')[0]),
          u'mlT': fmt(m(u'maxlen')[0]), u'mlN': fmt(m(u'maxlen')[3]),
          u'worst31': u'%.4f' % FLAT[u'mono_worst31_amp_e5']})
K[u'lines'] = FLAT[u'lines']
K[u'delta_abs_max'] = u'%.1f' % FLAT[u'delta_abs_max']
K[u'bvc'] = [len(x) for x in m(u'band_vocab_inbody')]
K[u'maxlen'] = m(u'maxlen')

NEWPAR = (
    u'**B58 把同一条向量交给四份一手文书各算一遍**：`raw/cvss/cvss_v30_spec.html`（v3.0 算法 ⟦T⟧：{bytesT} 字节／行数 {lines[0]}／非空行 {nbT}） ⇎ '
    u'`cvss_v31_spec.html`（v3.1 算法 ⟦O⟧：{bytesO} 字节／{lines[1]}／{nbO}） ⇎ `cvss_v40_spec.html`（v4.0 查表 ⟦F⟧：{bytesF} 字节／{lines[2]}／{nbF}） ⇎ '
    u'`cvss_examples.html`（算例 ⟦N⟧：{bytesN} 字节／{lines[3]}／{nbN}，行数是 T 的 {tr_rows_ratio} 倍余 {tr_rows_rest}——按 `<tr>` 数也是 {tr_rows[3]} ⇎ {tr_rows[0]}）。'
    u'两代算法的“相同”是逐项核出来的：基础分系数 {coef_base_n} 项里 {coef_base_n_equal} 项逐一相等 ⇎ 环境那 {coef_env_keys} 项只有 {coef_env_diff_n} 项被动过'
    u'（指数 {mexp30}→{mexp31} ⇎ 乘子 {mf30}→{mf31}），权重表 {w_triples_v30} ⇎ {w_triples_v31} 条三元组交集 {w_common} 且取值全等（不等 {w_unequal_n}，'
    u'只一代有 {w_only30_n}＋{w_only31_n}）；PR 在两种 Scope 下的备选值 {pr_alt[0]}⇎{pr_alt[1]}⇎{pr_alt[2]}⇎{pr_alt[3]} 两代同（同 {pr_alt_same} 枚）。'
    u'改动被 v3.1 自己点出来：那句“differs from CVSS v3.0”只出现在第二份（{sp_diff30[0]} ⇎ {sp_diff30[1]} ⇎ {sp_diff30[2]} ⇎ {sp_diff30[3]}）。'
    u'同分不是抽样话：{full_vectors} 条合法基础向量逐条比，两代 {full_eq3031} 条同分 ⇎ 不同 {full_ne3031} 条 ⇎ 算不出 {full_none30} 条；'
    u'其中 {full_zero} 条打分为零、{full_capped} 条越过 10 被封顶。取整另写三种实现与一条精确小数判据：伪码⇎加保护⇎直接 ceil 三者互差 '
    u'{full_pseudo_ne_guard} ⇎ {full_pseudo_ne_ceil} 条，且各自与 Fraction 判据 {full_pseudo_eq_exact}⇎{full_guard_eq_exact}⇎{full_ceil_eq_exact} 条全等（判分母为整十分位的有 {full_exact_on_tenth} 条），'
    u'文档自陈的浮点陷阱在基础分全空间取不到（原始值恰在十分位 {full_raw_on_tenth} 条）。'
    u'非单调性按同一维 N<L<H 的相邻链数出 {mono_pairs} 对（{mono_combos} 组组合 × 每维一档，组合账 {mono_grid_close}）：v3.0 公式违例 {mono_bad_v30formula} 对 ⇎ '
    u'v3.1 公式只剩 {mono_bad_v31formula} 对，差的 {mono_only30} 对全在 MISS 未封顶那一支（未封顶 {mono_uncapped30}→{mono_uncapped31}），'
    u'被 {mono_cap[0]} 封顶那一支两代都留着（{mono_capped30} ⇎ {mono_capped31}）；两代共有 {mono_both} 对 ⇎ 只 v3.1 有 {mono_only31} 对。'
    u'最坏一档 v3.0 降 {mono_worst30_amp}，v3.1 只降 {worst31}×10^-5——后者已到浮点噪声级。'
    u'v4.0 一份算式都不给（含 Roundup/Round up/8.22 的算式存在位：{arith_any[0]} ⇎ {arith_any[1]} ⇎ {arith_any[2]} ⇎ {arith_any[3]}），'
    u'换成 MacroVector 查表（原文 {bl_mv[0]}⇎{bl_mv[1]}⇎{bl_mv[2]}⇎{bl_mv[3]} ⇎ 渲染体 {bl_mv_body[2]} ⇎ 词边界 {bl_mv_wb[2]}）与 {eq_row_n} 行 EQ 约束'
    u'（表内 {eq_heads[2]} 处行头，and/or/not 各 {eq_and}⇎{eq_or}⇎{eq_not}，左端等级取值 {eq_level_kinds} 种）；Negligible 档只活在 v4.0 与算例里（{sp_negligible[0]}⇎{sp_negligible[1]}⇎{sp_negligible[2]}⇎{sp_negligible[3]}），'
    u'三份规范给的档位区间逐字相同（{band_rows[0]}⇎{band_rows[1]}⇎{band_rows[2]} 行 ⇎ 算例 {band_rows[3]}），档位词表 {bvc[0]}⇎{bvc[1]}⇎{bvc[2]}⇎{bvc[3]} 种（算例多一枚 Negligible）。'
    u'算例文档把两代分数并排印出 {sp_n} 对（表头有 3.1 与 4.0 两列，列数 {pair_col_kinds} 种、最多 {pair_col_max} 列）：严格“两列都是 Base”只 {pair_scope_base_strict} 对 ⇎ '
    u'放宽到空标签也算 {pair_scope_base_loose} 对（差 {pair_scope_base_gap} 对），差值和按全表 {delta_sum} ⇎ 只 Base {delta_base_sum} ⇎ Base＋空标签 {delta_baseboth_sum}'
    u'（混进来的 {pair_scope_base_gap} 对使两账相差 {delta_mix_gap}）；升 {delta_pos} ⇎ 降 {delta_neg} ⇎ 平 {delta_zero}，绝对值最大 {delta_abs_max}。'
    u'向量随分数印出的 {pair_v31_vec} ⇎ {pair_v40_vec} 对，另有 {pair_skip_n} 张表因同列出现多枚 3.1/4.0 表头被跳过。'
    u'可复现性抽 {repro_cand} 对候选（去重后 {repro_vec_distinct} 条向量，重复 {repro_repeat} 条）：按 v3.1 公式复算 {repro_ok}⇎{repro_bad}⇎算不出 {repro_none}，'
    u'换成 v3.0 公式仍 {repro_ok30} 条对 ⇎ 与 v3.1 结果相同 {repro30_eq_31} 条——印出来的分数分不出这两代。'
    u'转码层三口径：`&nbsp;` 字符 {nbsp[0]}⇎{nbsp[1]}⇎{nbsp[2]}⇎{nbsp[3]}、上标标签 {sup_tags[0]}⇎{sup_tags[1]}⇎{sup_tags[2]}⇎{sup_tags[3]}、'
    u'U+2212 减号 {minusuni[0]}⇎{minusuni[1]}⇎{minusuni[2]}⇎{minusuni[3]}；权重表两种序列化——v3.0 一行打包最多 {wt_maxpack[0]} 枚数值（{wt_pack_seq_v30} 组），'
    u'v3.1 拆成 {wt_rows[1]} 行每行一枚（{wt_maxpack[1]}）；组头命中 {w_groupheads_v30}⇎{w_groupheads_v31} 段 ⇎ 度量名行 {w_names_v30}⇎{w_names_v31} 行。'
    u'`ISCBase` 在原文里根本不成词（原文 {sp_isc[0]} ⇎ 渲染 {sp_isc_ren[0]}，源码写的是 `ISC<sub>Base</sub>`），`ISS`/`MISS` 倒只在 v3.1 成词（{sp_iss[1]} ⇎ {sp_miss[1]}）。'
    u'整行共用那笔账归站点装饰：T⇎O 共用 {share_TO} 行 ⇎ T⇎F {share_TF} ⇎ O⇎F {share_OF} ⇎ 四源全现 {share_all4}（只 T {only_T} ⇎ 只 O {only_O}，并集 {union_TO}，闭合差 {share_close_TO}）。'
    u'形状档也留了不对齐：四份最长行同长 {maxline_len[0]} 字符且是同一行（{maxline_shared}）⇎ 平均行长 {meanlen[0]}⇎{meanlen[1]}⇎{meanlen[2]}⇎{meanlen[3]}；'
    u'四份字节四种签名 {sha_distinct} 种（本遍用 blake2b 8 字节，建条目侧用 sha256 前 16 位，两种算法各数出 4 种）。'
    u'锚候选池 {pool_nf} 条（每源 {pool_tag_n[0]} ⇎ {pool_tag_n[1]} ⇎ {pool_tag_n[2]} ⇎ {pool_tag_n[3]}），穿一源 {pool_1} ⇎ 两源 {pool_2} ⇎ 三源 {pool_3} ⇎ 四源 {pool_4}（相加校住池，差 {pool_close}）；'
    u'登记锚 {anchor_total} 处／{anchor_distinct} 个不同串（每标签 T {tT} ⇎ O {tO} ⇎ F {tF} ⇎ N {tN}；单源 {u1} ⇎ 穿二或三源 {u23} ⇎ 四源全现 {u4}，归属检查 {checks} 次，错配 {anchor_err}）。'
    u'共用源 {nshared} 处（这四份 FIRST 字节此前没被任何条目当过源）。'
    u'“这四份 HTML 此刻是否还是各版本的官方发布页”“v4.0 印出的分数在库内能否复算（v4.0 规范不给算式）”“抓取时刻与磁盘 mtime 的先后”'
    u'不可由在库文件判定，判词按第三档写、门槛不背书。\n')

# ---------- 4) README ----------
S = io.open(FM, encoding='utf-8').read()
S = sub(u'共 **57 条**（`babeltele/B01..B57`）', u'共 **{nent} 条**（`babeltele/B01..B58`）'.format(**K), S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（57 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（{nent} 条）'.format(**K), S)
S = sub(u'当前 **57 条语料／1307 条**推导全部通过（audit 自报“已机检的推导 1307 条”）',
        u'当前 **{nent} 条语料／{proofs} 条**推导全部通过（audit 自报“已机检的推导 {proofs} 条”）'.format(**K), S)

ANCHOR_OLD = (u'“IANA 此刻是否还把 sha1 系签名算法列在可协商的注册表里”不可由在库文件判定，判词按第三档写、门槛不背书。\n')
S = sub(ANCHOR_OLD, ANCHOR_OLD + NEWPAR.format(**K), S)

ROW58 = (u'| B58 | {enc}（新建, 同一条向量交四份一手文书各算一遍 {anchor_total} 处标注／{anchor_distinct} 个不同串（登记 {anchor_distinct} 条锚全命中, '
         u'每标签 T {tT} ⇎ O {tO} ⇎ F {tF} ⇎ N {tN}, 归属检查 {checks} 次）: 四色锚位 v3.0 算法 ⟦T⟧ ⇎ v3.1 算法 ⟦O⟧ ⇎ v4.0 查表 ⟦F⟧ ⇎ 算例 ⟦N⟧; '
         u'头条是“两代闭式算式在 {full_vectors} 条向量上逐条同分”——系数 {coef_base_n} 项里 {coef_base_n_equal} 项相等 ⇎ 环境族只动 {coef_env_diff_n} 项（指数 {mexp30}→{mexp31}、乘子 {mf30}→{mf31}）⇎ 权重三元组 {w_triples_v30}⇎{w_triples_v31} 交集 {w_common} 且不等 {w_unequal_n}; '
         u'非单调账 {mono_bad_v30formula}⇎{mono_bad_v31formula}（未封顶 {mono_uncapped30}→{mono_uncapped31} ⇎ 封顶 {mono_capped30}⇎{mono_capped31}, 最坏幅度 {mono_worst30_amp}→{worst31}×10^-5）; 取整三实现互差 {full_pseudo_ne_guard}⇎{full_pseudo_ne_ceil} 且与 Fraction 判据 {full_pseudo_eq_exact} 条全等 ⇎ 自陈浮点陷阱不可达 {full_raw_on_tenth}; '
         u'v4.0 无算式 {arith_any[0]}⇎{arith_any[1]}⇎{arith_any[2]}⇎{arith_any[3]}（MacroVector 原文 {bl_mv[2]} ⇎ 词边界 {bl_mv_wb[2]} ／ EQ 约束 {eq_row_n} 行 and⇎or⇎not {eq_and}⇎{eq_or}⇎{eq_not}）; '
         u'算例配对 {sp_n} 对: 严格 {pair_scope_base_strict} ⇎ 放宽 {pair_scope_base_loose}（差 {pair_scope_base_gap}）, 差值和 {delta_sum}⇎{delta_base_sum}⇎{delta_baseboth_sum}（混档拉低 {delta_mix_gap}）⇎ 升 {delta_pos}／降 {delta_neg}／平 {delta_zero}; '
         u'抽样 {repro_vec_distinct} 条向量按两代公式各复算 {repro_ok}⇎{repro_ok30} 全对（两代相同 {repro30_eq_31}）; '
         u'权重序列化 打包 {wt_maxpack[0]} 枚/行 ⇎ 拆行 {wt_rows[1]} 行（组头命中 {w_groupheads_v30} ⇎ 度量名行 {w_names_v30}）⇎ `ISCBase` 原文 {sp_isc[0]} ⇎ 渲染 {sp_isc_ren[0]}; '
         u'档位区间三份同 {band_rows[0]}⇎{band_rows[1]}⇎{band_rows[2]} ⇎ 词表算例多 Negligible {sp_negligible[3]}; 形状 最长行四份同长 {maxline_len[0]}（同一行 {maxline_shared}）⇎ 平均 {meanlen[0]}⇎{meanlen[1]}⇎{meanlen[2]}⇎{meanlen[3]} ⇎ `&nbsp;` {nbsp[0]}⇎{nbsp[1]}⇎{nbsp[2]}⇎{nbsp[3]} ⇎ U+2212 {minusuni[0]}⇎{minusuni[1]}⇎{minusuni[2]}⇎{minusuni[3]}; '
         u'整行共用 {share_TO}⇎{share_TF}⇎{share_OF}（四源 {share_all4}, 闭合差 {share_close_TO}）是 chrome; 锚池 {pool_nf} 条穿四源 {pool_4} ⇎ 三源 {pool_3}; '
         u'同数共键复合式 {coll} 组、零项 {zeros} 枚折成一条算式; 门槛侧 {deriv_keys} 枚推导键／{deriv_points} 处 B58V 引用点（建条目侧按“值→算式”去重记 {dedup_points}），五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对 {anchor_distinct} 条锚逐字全命中, 工具侧 atomcheck 另核 ok={anchor_distinct} bad=0） |\n')
anchor_row = (u'门槛侧 105 枚推导键／532 处 B57V 引用点（建条目侧按“值→算式”去重记 239），'
              u'四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 27 条锚逐字全命中） |\n')
assert S.count(anchor_row) == 1
S = sub(anchor_row, anchor_row + ROW58.format(**K), S)

lin = (u'第二代（B11–B57）锚内字母 **118 794**、锚外 **12 766**；全库合计 **118 915／14 961**'
       u'（B57 一枚条目贡献 949／592, 由建条目侧现数）')
S = sub(lin, (u'第二代（B11–B58）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
              u'（B58 一枚条目贡献 %s／%s, 由建条目侧现数）'
              % (fmt(118794 + CH[u'letters_in']), fmt(12766 + CH[u'letters_out']),
                 fmt(118915 + CH[u'letters_in']), fmt(14961 + CH[u'letters_out']),
                 fmt(CH[u'letters_in']), fmt(CH[u'letters_out']))), S)

RAW58 = (u'| B58 | `raw/cvss/cvss_v30_spec.html`（v3.0 算法 ⟦T⟧：{bytesT} 字节／行数 {lines[0]}／非空行 {nbT}／平均行长 {meanlen[0]}／`<tr>` {tr_rows[0]} 行／`Roundup` {ar_ru[0]} 次） ⇎ '
         u'`raw/cvss/cvss_v31_spec.html`（v3.1 算法 ⟦O⟧：{bytesO} 字节／{lines[1]}／{nbO}／{meanlen[1]}／`<tr>` {tr_rows[1]} 行／`Roundup` {ar_ru[1]} 次 ⇎ `Round up` {ar_ru_up[1]} 次） ⇎ '
         u'`raw/cvss/cvss_v40_spec.html`（v4.0 查表 ⟦F⟧：{bytesF} 字节／{lines[2]}／{nbF}／`<tr>` {tr_rows[2]} 行／MacroVector {bl_mv[2]} ⇎ 词边界 {bl_mv_wb[2]}／算式存在位 {arith_any[2]}） ⇎ '
         u'`raw/cvss/cvss_examples.html`（算例 ⟦N⟧：{bytesN} 字节／{lines[3]}／{nbN}／`<tr>` {tr_rows[3]} 行／表 {table_tags[3]} 张／向量出现 {vec_occ[3]} ⇎ 去重 {vec_distinct[3]}） | '
         u'四份文书算同一条向量 ⇒ 两代闭式在 {full_vectors} 条向量上 {full_eq3031} 条同分（违例账 {mono_bad_v30formula}⇎{mono_bad_v31formula}），v4.0 只给查表与 {eq_row_n} 行布尔约束（算式 {arith_any[2]}），'
         u'算例并排印出 {sp_n} 对分数（严格 Base {pair_scope_base_strict} ⇎ 放宽 {pair_scope_base_loose}，差值和 {delta_sum}），抽样 {repro_vec_distinct} 条两代公式都复算得出（{repro_ok}⇎{repro_ok30}）|\n')
anchor2 = (u'两份建议之间整行共用 299 ⇎ 正文行只 257 ⇎ 句子档共用 66，而含门限的改判句在共用池里 0＋0 处命中|\n')
assert S.count(anchor2) == 1
S = sub(anchor2, anchor2 + RAW58.format(**K), S)

row_tot = (u'| **合计（{nent} 条）** | **{enct}** | **{rett}**（摘要段合计 {digt}） | — | **{unqt}** | — |\n').format(
    nent=NENT, enct=fmt(enc_all).replace(u',', u' '), rett=ret_tot,
    digt=fmt(dig_all).replace(u',', u' '), unqt=fmt(uniq_all).replace(u',', u' '))
old_tot = re.search(u'[|] [*]{2}合计（57 条）[*]{2}[^\n]*\n', S)
assert old_tot
S = S.replace(old_tot.group(0), row_tot)

PROSE = set(u'B03 B06 B09 B15 B27 B28 B29 B30 B31 B44 B48 B49 B50 B51 B52'.split())
extra = sorted([k for k in HINT if k not in PROSE])
EMPTY = [k for k in (u'B54', u'B56', u'B57', u'B58') if k not in HINT]
xstr = u' ⇎ '.join(u'%s 的 `%s`' % (k, u'／'.join(HINT[k])) for k in extra)
tail_old = (u'新建的 B54 ⇎ B56 ⇎ B57 同样为空——B57 把两位以内的结构计数全部折进了 DERIV'
            u'（0 项 109 枚并成一条算式，由 _b57_scan 照样复算））未逐位核验，')
assert S.count(tail_old) == 1
S = sub(tail_old, (u'新建的 B54 ⇎ B56 ⇎ B57 ⇎ B58 同样为空——B58 把两位以内的结构计数全部折进了 DERIV'
                   u'（0 项 %d 枚并成一条算式，由 _b58_scan 照样复算；另有 %d 处跨值复合式））未逐位核验，'
                   % (CH[u'zero_terms'], len(CH[u'collisions']))), S)
S = sub(u'残余提示（不计 FAIL）：20 个', u'残余提示（不计 FAIL）：%d 个' % soft_all, S)

WL, WR = 160, 200
CMD = (u'python -X utf8 corpus/_mkB58.py                  # 建条目: 扁平契约 %d 枚键／DERIV %d 枚算式, 占位符未替换 0 个\n'
       u'python -X utf8 corpus/_mkdigest3.py B58 <entry> T corpus/raw/cvss/cvss_v30_spec.html %d %d '
       u'O corpus/raw/cvss/cvss_v31_spec.html %d %d F corpus/raw/cvss/cvss_v40_spec.html %d %d '
       u'N corpus/raw/cvss/cvss_examples.html %d %d   # 四源分节摘要(%s 字符, 窗口按 %d⇎%d 取句边界)\n'
       u'python -X utf8 corpus/_wire58.py                    # 把 SCAN 段机械切进 audit.py::_b58_scan 并插 DERIV[\'B58\']\n'
       u'python -X utf8 corpus/_fill58.py                    # 第四遍: 现取注数并把 ⛓解读注 写回条目(与契约 %d 键逐一对表)\n'
       u'python -X utf8 corpus/atomcheck.py B58 corpus/_atoms58.txt   # 工具侧独立逐字校验: ok=%d bad=0\n'
       % (len(FLAT), CH[u'deriv_keys'], WL, WR, WL, WR, WL, WR, WL, WR,
          fmt(dig58).replace(u',', u' '), WL, WR, len(FLAT), m(u'anchor_distinct')))
anchor3 = u'python -X utf8 corpus/atomcheck.py B57 corpus/_atoms57.txt   # 工具侧独立逐字校验: ok=27 bad=0' + NL
assert S.count(anchor3) == 1
S = sub(anchor3, anchor3 + CMD, S)

io.open(FM, 'w', encoding='utf-8', newline=NL).write(S)
print(u'README 已记账: %d 条 ｜ 编码合计 %s ⇎ 摘要合计 %s ⇎ 合计保留率 %s ｜ 唯一码点 %d ｜ 推导 %d 条 ｜ 提示 %d（清单 %s） ｜ '
      u'B58 %s 字符／%d 锚(%d 串, T %d⇎O %d⇎F %d⇎N %d, 单源 %d⇎穿二三 %d⇎四源 %d, 检查 %d) ｜ '
      u'第五遍: 现量 %d 个键全等契约⇎快照 ｜ 形状 最长行 %s⇎平均 %s ⇎ `&nbsp;` %s ｜ 词面 Roundup %s ⇎ MacroVector %s(渲染 %s) ⇎ ISCBase 原文 %s⇎渲染 %s ｜ '
      u'向量 出现 %s ⇎ 去重 %s ｜ blake2b 签名 %d 种 ｜ 共用源 %d 处 ｜ 复合式 %d 组⇎零项 %d 枚'
      % (NENT, fmt(enc_all), fmt(dig_all), ret_tot, uniq_all, proofs, soft_all,
         u' '.join(sorted(HINT)), fmt(enc58), m(u'anchor_total'), m(u'anchor_distinct'),
         tc[u'T'], tc[u'O'], tc[u'F'], tc[u'N'], m(u'anchor_single'), m(u'anchor_cross'),
         m(u'anchor_all4'), m(u'checks'), len(Q5), fmt(m(u'maxlen')[0]),
         u'⇎'.join(str(x) for x in m(u'meanlen')), u'⇎'.join(str(x) for x in m(u'nbsp')),
         u'⇎'.join(str(x) for x in m(u'ar_ru')), u'⇎'.join(str(x) for x in m(u'bl_mv')),
         m(u'bl_mv_body')[2], m(u'sp_isc')[0], m(u'sp_isc_ren')[0],
         u'⇎'.join(str(x) for x in m(u'vec_occ')), u'⇎'.join(str(x) for x in m(u'vec_distinct')),
         m(u'sha_distinct'), len(shared), len(CH[u'collisions']), CH[u'zero_terms']))
