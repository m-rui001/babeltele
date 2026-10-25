# -*- coding: utf-8 -*-
"""README 记账: 49 条 → 50 条。合计数字全部由 audit 表、metrics 普查、六份 raw 回算与 _b50* 快照复算, 不手填。
B50 特有的一环: 这里第三次把六份源量一遍——区段找法、28 条模式正则、锚的归一函数都在本文件另写一份,
再与采集侧 _pick50 的快照、审计器侧 _b50_scan 的快照逐键对表; 六格矩阵 168 格里哪几格为零也因此是当场数出来的。"""
import io, os, re, sys, json, ast, hashlib, subprocess, collections

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
t = io.open(F, encoding='utf-8').read()

TAG, ENTRY = u'B50', u'corpus/babeltele/B50_one_model_six_domains.md'
NL = u'\n'
SLUGS = [u'math_subsets', u'med_gitalb', u'law_ewca_method', u'fin_credit_cmte',
         u'ind_creep_rupture', u'str_quake_slab']
TAGS = [u'M', u'D', u'L', u'F', u'I', u'S']
CN = [u'数论', u'肾病', u'判例', u'信贷', u'炉管', u'震后']
RAWS = [u'corpus/raw/cot/%s.md' % s for s in SLUGS]
HEADRX = re.compile(u'^(model|slug|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$', re.M)

# ---------- audit / metrics ----------
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-600:]
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
dig_all, enc_all, ret_all, uniq_all = (int(allc[0].replace(u' ', u'')), int(allc[1].replace(u' ', u'')),
                                       allc[2], int(allc[4]))
soft_all = int(re.search(u'提示\\(不计入 FAIL, 1-2 位结构计数未逐位核验\\): 共 (\\d+) 个', p.stdout).group(1))
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
NENT = len(row) - 1
cells = lambda tag: [x.strip() for x in row[tag].split(u'|')]
b50, b49 = cells(u'B50'), cells(u'B49')
b50_dig, b50_enc, b50_ret, b50_raw, b50_uniq, b50_blocks, b50_cpu, b50_soft = (
    int(b50[0]), int(b50[1]), b50[2], b50[3], int(b50[4]), int(b50[5]), b50[6], int(b50[10]))
b49_enc, b49_ret = int(b49[1]), b49[2]
assert NENT == 50, NENT
assert b50_soft == 0 and not re.search(u"^\\s+B50 \\[", p.stdout, re.M), (b50, soft_all)
assert int(b50[7]) == 0 and int(b50[8]) == 0 and int(b50[9]) == 0, b50
assert b50_enc == 6369 and b50_dig == 4097
assert b50_ret == u'%.1f%%' % (100.0 * b50_enc / b50_dig)
ZSOFT = sorted([k for k in row if k != u'ALL' and int(cells(k)[10]) == 0], key=lambda x: int(x[1:]))
assert all(k in ZSOFT for k in (u'B32', u'B43', u'B45', u'B46', u'B47', u'B49', u'B50'))
assert u'B48' not in ZSOFT and len(ZSOFT) == 39, (len(ZSOFT), ZSOFT)

m = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/metrics.py'],
                   capture_output=True, text=True, encoding='utf-8')
cen = dict((mm.group(1), int(mm.group(2))) for mm in
           re.finditer(r'^\s{2}([A-Za-z\-]+)\s+([\d ]+)$', m.stdout, re.M))
assert len(cen) == 18, sorted(cen)

# ---------- 第三次独立测量: 两套区段找法必须给出同一批长度 ----------
TXT = [io.open(x, encoding='utf-8').read() for x in RAWS]
BYTES = [os.path.getsize(x) for x in RAWS]
NLINES = [len(x.split(NL)) - 1 for x in TXT]
NASC = [len(re.findall(u'[^\x00-\x7f]', x)) for x in TXT]
HDR = [dict(HEADRX.findall(x)) for x in TXT]
for i, s in enumerate(SLUGS):
    assert HDR[i][u'slug'] == s, HDR[i]


def mark(txt, key, nxt):
    a = txt.find(key)
    b = txt.find(nxt, a)
    return txt[a + len(key):b]


# 找法 A: 标记偏移(采集侧同款规则, 本文件另写)
RF = [mark(x, u'## [[REASONING]]', u'## [[ANSWER]]').strip() for x in TXT]
AC = [len(x[x.find(u'## [[ANSWER]]') + 13:].strip()) for x in TXT]
PCOT = [len(mark(x, u'## [[PROMPT]]', u'## [[REASONING]]').strip()) for x in TXT]
GAPF = [len(mark(x, u'## [[REASONING]]', u'## [[ANSWER]]')) - len(RF[i]) for i, x in enumerate(TXT)]
# 采集侧的切片多跳一格(a+17 而非 a+16), 少掉前导换行: 同一件事的两种写法, 恒差 1
GAP = [GAPF[i] - 1 for i in range(6)]
# 找法 B: 严格分节正则(探测侧同款结构, 本文件另写)
SEC = [re.search(u'## \\[\\[PROMPT\\]\\]\\n(.*?)\\n\\n## \\[\\[REASONING\\]\\]\\n(.*?)'
                 u'\\n\\n## \\[\\[ANSWER\\]\\]\\n?(.*)$', x, re.S) for x in TXT]
assert all(SEC), u'分节正则未命中'
PRAW = [len(g.group(1)) for g in SEC]
assert [len(g.group(2).rstrip(u'\n')) for g in SEC] == [len(x) for x in RF]
assert len(set(GAP)) == 1 and len(set([PRAW[i] - PCOT[i] for i in range(6)])) == 1
assert GAP[0] == 2 and GAPF[0] == 3 and PRAW[0] - PCOT[0] == 1
RGAP = [len(g.group(2)) - len(RF[i]) for i, g in enumerate(SEC)]
assert len(set(RGAP)) == 1 and RGAP[0] == 0, RGAP
PGAP = PRAW[0] - PCOT[0]
RC = [len(x) for x in RF]
assert RC == [int(HDR[i][u'reasoning_chars']) for i in range(6)] and AC == [0] * 6

# ---------- 28 条模式正则(本脚本第三份, 与 _probe50 / _pick50 各写一次) ----------
PATS = {
    u'wait': u'(?i)\\bWait\\b',
    u'actually': u'(?i)\\bactually\\b',
    u'maybe': u'(?i)\\bmaybe\\b|\\bperhaps\\b',
    u'prob': u'(?i)\\bprobably\\b|\\blikely\\b',
    u'assume': u'(?i)\\bassume[ds]?\\b|\\bassuming\\b',
    u'unsure': u'(?i)\\bnot sure\\b|\\bunclear\\b|\\bi (?:think|believe)\\b',
    u'verif': u'(?i)\\bcheck\\b|\\bverify\\b|\\bsanity\\b|\\bdouble[- ]check\\b|\\bconfirm\\b',
    u'redo': u'(?i)\\bredo\\b|\\bstart over\\b|\\blet me (?:recompute|recheck)\\b',
    u'wrong': u'(?i)\\bwrong\\b|\\bmistake\\b|\\berror\\b|\\boops\\b',
    u'therefore': u'(?i)\\btherefore\\b|\\bthus\\b|\\bhence\\b|\\bso\\b',
    u'however': u'(?i)\\bhowever\\b|\\bbut\\b|\\balthough\\b|\\bwhereas\\b',
    u'must': u'(?i)\\bmust\\b',
    u'caveat': u'(?i)\\bcaveat\\b|\\bcaution\\b|\\bcareful\\b|\\bbeware\\b',
    u'final': u'(?i)\\bfinal\\b|\\bconclusion\\b|\\banswer:|\\brecommend',
    u'quote': u'"[^"]{10,60}"',
    u'equality': u'=',
    u'unit': u'(?i)\\b(?:mm|MPa|kN|GPa|°C|kg|m|s|y|years|months|mm/yr|kW|Hz|Bq|Sv|Gy|%)\\b',
    u'cfr': u'(?i)\\b(?:article|section|§|clause|paragraph|paragraphs)\\b',
    u'study': u'(?i)\\bstudy\\b|\\bpaper\\b|\\bauthor',
}
EXTRA = {
    u'restart_word': u'(?i)\\brestart(?:s|ed|ing)?\\b',
    u'uncertain_word': u'(?i)\\buncertain(?:ty|ly)?\\b',
    u'bold': u'\\*\\*[^*]{2,60}\\*\\*',
    u'hmm': u'(?i)\\bHmm\\b',
    u'lets': u"(?i)\\blet's\\b",
    u'letme': u'(?i)\\blet me\\b',
    u'need': u'(?i)\\bneed\\b',
    u'q': u'\\?',
    u'arrow': u'->',
}
ALLK = sorted(PATS) + sorted(EXTRA)
assert len(ALLK) == 28, len(ALLK)
ME = dict((k, [len(re.findall(v, x)) for x in RF]) for k, v in list(PATS.items()) + list(EXTRA.items()))
SH = {
    u'fchars': [len(x) for x in TXT],
    u'sent': [len(re.findall(r'[.!?](?:\s|$)', x)) for x in RF],
    u'para': [len([y for y in x.split(NL) if y.strip()]) for x in RF],
    u'numsent': [len([y for y in re.split(r'(?<=[.!?])\s+', x) if re.search(r'\d', y)]) for x in RF],
}

# 与探测侧落盘的统计表逐行回表
ST = {}
for l in io.open(u'corpus/_f50stats.txt', encoding='utf-8').read().split(NL):
    if u'\t' in l:
        k, v = l.split(u'\t')
        ST[k] = [int(x) for x in v.split(u' ')] if re.match(u'^[0-9 ]+$', v) else v.split(u' ')
for k in sorted(PATS):
    assert ME[k] == ST[k], (k, ME[k], ST[k])
for k in (u'sent', u'para', u'numsent', u'fchars'):
    assert SH[k] == ST[k], (k, SH[k], ST[k])
assert BYTES == ST[u'fbytes'], (BYTES, ST[u'fbytes'])
assert (ST[u'rcot'], ST[u'acot']) == (RC, AC) and ST[u'pcot'] == PRAW
assert PCOT == [x - PGAP for x in PRAW]

# 与采集侧 ⇎ 审计器侧两份快照对表(本脚本是第三套)
M = json.load(io.open(u'corpus/_b50meas.json', encoding='utf-8'))
A = json.load(io.open(u'corpus/_b50audit.json', encoding='utf-8'))
CMP = [u'rcot', u'acot', u'pcot', u'praw', u'fchars', u'fbytes', u'sent', u'para', u'numsent',
       u'gap', u'pgap', u'wait', u'actually', u'maybe', u'prob', u'assume', u'unsure', u'verif',
       u'redo', u'wrong', u'therefore', u'however', u'must', u'caveat', u'final', u'quote',
       u'equality', u'unit', u'cfr', u'study', u'restart_word', u'uncertain_word', u'bold',
       u'hmm', u'lets', u'letme', u'arrow', u'flip', u'allpos', u'sixzero', u'npats', u'nsrc',
       u'models', u'model_bare', u'hashes', u'sha_ok', u'retr', u'tailbad', u'rcotsum',
       u'rcratio', u'anchor_total', u'anchor_distinct', u'cross', u'checks']
ASLIST = (u'flip', u'allpos', u'sixzero', u'models')
CV = lambda k, side: (len(side[k]) if k in ASLIST and isinstance(side[k], list) else side[k])
aslist_ = lambda v: v if isinstance(v, list) else [v]
rnd = lambda v: [round(float(x), 1) for x in aslist_(v)]
MODELS = sorted(set(HDR[i][u'model'] for i in range(6)))
BARE = sorted(set(h[u'model'].split('/')[-1] for h in HDR))
SHA_OK = sum(1 for i in range(6)
             if hashlib.sha256(SEC[i].group(1).encode('utf-8')).hexdigest()[:16]
             == HDR[i][u'prompt_sha256'])
HASHES = len(set(HDR[i][u'prompt_sha256'] for i in range(6)))
RETR = len(set(HDR[i][u'retrieved'] for i in range(6)))
LASTC = [RF[i][-1] for i in range(6)]
TAILBAD = sum(1 for c in LASTC if c not in u'.!?"“”\u201d')
P10 = dict((k, [round(10000.0 * ME[k][i] / RC[i], 1) for i in range(6)]) for k in ALLK)


def lead(v):
    mx = max(v)
    return sorted([i for i in range(6) if v[i] == mx])


FLIP = [k for k in sorted(PATS) if lead(ME[k]) != lead(P10[k])]
ALLPOS = [k for k in sorted(PATS) if min(ME[k]) >= 1]
SIXZERO = [k for k in sorted(PATS) if ME[k] == [0] * 6]
THIRD = dict((k, None) for k in CMP)
THIRD.update(ME)
THIRD.update({u'rcot': RC, u'acot': AC, u'pcot': PCOT, u'praw': PRAW, u'fchars': SH[u'fchars'],
              u'fbytes': BYTES, u'sent': SH[u'sent'], u'para': SH[u'para'],
              u'numsent': SH[u'numsent'], u'gap': GAP, u'pgap': PGAP,
              u'models': len(MODELS), u'model_bare': len(BARE), u'sha_ok': SHA_OK, u'hashes': HASHES,
              u'retr': RETR, u'tailbad': TAILBAD, u'flip': len(FLIP), u'allpos': len(ALLPOS),
              u'sixzero': len(SIXZERO), u'npats': len(PATS), u'nsrc': 6,
              u'rcotsum': sum(RC), u'rcratio': round(1.0 * max(RC) / min(RC), 1)})
assert SIXZERO == [u'redo'] and TAILBAD == 6 and len(BARE) == 1 and len(MODELS) == 2
assert SHA_OK == HASHES == 6 and RETR == 4 and len(FLIP) == 6 and len(ALLPOS) == 9
assert sum(RC) == 267538 and THIRD[u'rcratio'] == 3.1

# ---------- 六格矩阵: 零格在哪里 ----------
ZEROCELL = [(k, i) for k in ALLK for i in range(6) if ME[k][i] == 0]
ZEX = len([1 for k, i in ZEROCELL if k in EXTRA])
MIXED = [k for k in ALLK if min(ME[k]) == 0 and max(ME[k]) > 0]
ZP = len([1 for k, i in ZEROCELL if k in PATS])
assert MIXED and len(ZEROCELL) == ZP + ZEX == 27 + 21

# ---------- 锚: 三口径 + 互斥(本脚本第三份归一) ----------
REG = [x.rstrip(NL) for x in io.open(u'corpus/_atoms50.txt', encoding=u'utf-8') if x.strip()]
OWNER = {}
for tg, lst in M[u'atomlist'].items():
    for a in lst:
        OWNER[a] = tg
assert len(OWNER) == len(REG) == 54 and set(OWNER.values()) == set(TAGS)
fold = lambda s: re.sub(u'\\s+', u' ', s).strip()


def nrm(s):
    s = s.lower()
    for a, b in ((u'’', u"'"), (u'‘', u"'"), (u'“', u'"'), (u'”', u'"')):
        s = s.replace(a, b)
    s = re.sub(u"[’'\"‘“”`´]+", u'', s)
    s = re.sub(u'[‐‑‒–—―−-]', u'-', s)
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff\-\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


NR = [nrm(x) for x in TXT]
exact = sum(1 for a in REG if a in TXT[TAGS.index(OWNER[a])])
folded = sum(1 for a in REG if fold(a) in fold(TXT[TAGS.index(OWNER[a])]))
normed = sum(1 for a in REG if nrm(a) in NR[TAGS.index(OWNER[a])])
assert (exact, folded, normed) == (54, 54, 54), (exact, folded, normed)
MULTI = sum(1 for a in REG if sum(1 for j in range(6) if nrm(a) in NR[j]) > 1)
CHECKS = len(REG) * 6
assert MULTI == 0 and CHECKS == 324 == A[u'checks']
ac = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/atomcheck.py', u'B50', u'corpus/_atoms50.txt'],
                    capture_output=True, text=True, encoding=u'utf-8')
AK, AB_ = (int(x) for x in re.search(r'ok=(\d+) bad=(\d+)', ac.stdout).groups())
assert (AK, AB_) == (len(REG), 0), ac.stdout[-400:]
# 起手套话确实同类, 而锚仍互斥: 这才是“对照没被套话抹平”的证据
FIRSTL = [fold(RF[i].split(NL)[0])[:32] for i in range(6)]
WENEED = sum(1 for x in FIRSTL if x.startswith(u'We need'))
DISABL = sum(1 for x in FIRSTL if u'disabled' in x)
DISTINCT_FIRST = len(set(FIRSTL))
assert (WENEED, DISABL, DISTINCT_FIRST) == (4, 2, 6), (WENEED, DISABL, DISTINCT_FIRST)

# ---------- 三套实现逐键对表(本脚本 ⇎ _pick50 快照 ⇎ audit._B50 快照) ----------
THIRD[u'anchor_total'] = len(REG)
THIRD[u'anchor_distinct'] = len(set(REG))
THIRD[u'cross'] = MULTI
THIRD[u'checks'] = CHECKS
BAD3 = [k for k in CMP if THIRD.get(k) is None or rnd(CV(k, THIRD)) != rnd(CV(k, A))
        or rnd(CV(k, THIRD)) != rnd(CV(k, M))]
assert not BAD3, [(k, THIRD.get(k), A.get(k), M.get(k)) for k in BAD3]
BOTH = len(CMP)
VALS = sum(len(aslist_(CV(k, THIRD))) for k in CMP)

# ---------- 条目结构 ----------
md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
labels = re.findall(u'⟦([A-Z])⟧⟨', body)
NOCC, DIST = len(atoms), len(set(atoms))
assert (NOCC, DIST) == (35, 32), (NOCC, DIST)
NLAB = collections.Counter(labels)
assert sum(NLAB.values()) == NOCC and sorted(NLAB.values(), reverse=True) == [7, 7, 6, 5, 5, 5], NLAB
assert set(NLAB) == set(TAGS)
UNCITED = len([x for x in REG if x not in set(atoms)])
CH = json.load(io.open(u'corpus/_b50checks.json', encoding='utf-8'))
assert (CH[u'anchor_total'], CH[u'used'], CH[u'distinct'], CH[u'uncited'], UNCITED) == (54, 35, 32, 22, 22)
GLOS = len([l for l in body.split(NL) if l.strip()])
NSKEL = len(re.findall(u'[①-⑳]', [l for l in body.split(NL) if l.startswith(u'∴')][0]))
NSTEP = len(re.findall(u'第[一二三四五六]步', body))
IN_LAT = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
OUT_ALL = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
TAG_LAT = len(labels)
OUT_LAT = OUT_ALL - TAG_LAT
DIG = md[:md.index(u'## ⟪BabelTele⟫')]
ENC = re.search(u'## ⟪BabelTele⟫\n(.*?)\n\n## ⛓解读注', md, re.S).group(1)
BLOCKS = len(re.findall(u'### ⟦', DIG))
DL, EL = len(DIG.replace(NL, u'')), len(ENC.replace(NL, u''))
DIGHIT = len([a for a in atoms if fold(a) in fold(DIG)])
EXACT = len([a for a in atoms if a in DIG])
assert (BLOCKS, DIGHIT, EXACT, EL) == (6, NOCC, NOCC, b50_enc), (BLOCKS, DIGHIT, EXACT, EL)
RAW_SUM = sum(SH[u'fchars'])
assert b50_raw == u'%.3f%%' % (100.0 * b50_enc / sum(BYTES)), b50_raw

# ---------- DERIV 结构(从 audit.py 现读, 不手填) ----------
AUD = io.open(u'corpus/audit.py', encoding='utf-8').read()
st = AUD.index(u"DERIV['B50'] = ")
en = AUD.index(u"\nDERIV['", st + 10)
B50D = ast.literal_eval(AUD[AUD.index(u'{', st):en].strip().rstrip(u','))
DJ = json.load(io.open(u'corpus/_deriv50.json', encoding='utf-8'))
KEYS = len(B50D)
ZERO = B50D[u'0']
ZT = len(ZERO.split(u'+'))
FAMS = collections.Counter()
IDX = PLAIN = NRND = 0
for v in B50D.values():
    for n in ast.walk(ast.parse(v, mode='eval')):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            FAMS[n.func.id] += 1
            if n.func.id == u'B50V':
                IDX += len(n.args) > 1
                PLAIN += len(n.args) == 1
            if n.func.id == u'round':
                NRND += 1
OPS = collections.Counter(type(n.op).__name__ for v in B50D.values()
                          for n in ast.walk(ast.parse(v, mode='eval')) if isinstance(n, ast.BinOp))
LISTKEYS = [k for k in B50D if k.startswith(u'[')]
assert (KEYS, len(DJ), len(LISTKEYS)) == (104, 99, 5), (KEYS, len(DJ), LISTKEYS)
assert ZT == len(re.findall(u'B50V\\(', ZERO)) == 40
# 0 键折的 40 项里, 有多少是矩阵零格: 逐项回表(键名+格号都得在 ME 里真的是 0)
ZPAIRS = set((k, int(i)) for k, i in re.findall(u"B50V\\('([a-z_]+)',\\s*(\\d)\\)", ZERO))
assert all(THIRD[k][i] == 0 for k, i in ZPAIRS), [p for p in ZPAIRS if THIRD[p[0]][p[1]]]
ZNAMED = len([p for p in ZPAIRS if p[0] in ALLK])
UNCOVERED = sorted(set(k for k, i in ZEROCELL if (k, i) not in ZPAIRS))
NUNREF = len([p for p in ZEROCELL if p not in ZPAIRS])
assert (ZNAMED, NUNREF) == (38, 10) and ZT == ZNAMED + 2, (ZNAMED, NUNREF, ZT)
assert UNCOVERED == [u'assume', u'caveat', u'study', u'wrong']
assert IDX + PLAIN == FAMS[u'B50V'] == 151 and set(FAMS) == {u'B50V', u'round'}
assert OPS[u'Add'] == 39 and OPS[u'Div'] == OPS[u'Mult'] == NRND == 8
PROOF_B50 = len(re.findall(u'^  ✓ .*B50V\\(', p.stdout, re.M))
assert PROOF_B50 == len(DJ) == proofs - (proofs - PROOF_B50), (PROOF_B50, proofs)
COLL = CH[u'collisions']
NCG, NCS = len(COLL), len([k for k in COLL if len(COLL[k]) > 1])
NCV = sum(len(v) for v in COLL.values())
assert (NCG, NCS, NCV) == (16, 16, 57), (NCG, NCS, NCV)

fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')
six = lambda k, f=lambda x: x: u' ⇎ '.join(u'%s' % f(v) for v in ME[k]) if f is None else \
    u' ⇎ '.join(u'%s' % f(v) for v in ME[k])
cellrow = lambda k: u'⇎'.join(u'%d' % v for v in ME[k])
p10row = lambda k: u' ⇎ '.join(u'%s' % v for v in P10[k])

# ---------- 全库字母账(与上一版 README 对齐, 不手填) ----------
mm = re.search(u'第二代（B11–B49）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
               u'全库合计 \\*\\*([\\d ]+)／([\\d ]+)\\*\\*', t)
assert mm, u'第二代行未命中'
prev_in, prev_out = int(mm.group(1).replace(u' ', u'')), int(mm.group(2).replace(u' ', u''))
FIRST_IN, FIRST_OUT = 121, 2195
assert prev_in + FIRST_IN == int(mm.group(3).replace(u' ', u'')), mm.group(3)
assert prev_out + FIRST_OUT == int(mm.group(4).replace(u' ', u'')), mm.group(4)
assert cen[u'Latin'] - prev_in - prev_out - FIRST_IN - FIRST_OUT == IN_LAT + OUT_ALL, (
    cen[u'Latin'], prev_in, prev_out, IN_LAT, OUT_ALL)
in_lat, out_lat = prev_in + IN_LAT, prev_out + OUT_ALL
OLD_PROOFS = int(re.search(u'当前 \\*\\*49 条语料／(\\d+) 条\\*\\*推导', t).group(1))
assert proofs == OLD_PROOFS + len(DJ), (OLD_PROOFS, proofs)

cen_s = (u'Latin %s · Han %s · Gen-Punct %s · Arrows %s · CJK-Punct %s · Fullwidth %s · Emoji %s · Math %s · '
         u'Greek %s · Misc-Symbols %s · Dingbats %s · Geometric %s · Hiragana %s · Katakana %s · '
         u'MathAlnum %s · EnclosedIdeo %s · EnclosedSuppl %s · Comb-Diacritic %s') % tuple(
    fmt(cen[k]) for k in [u'Latin', u'Han', u'Gen-Punct', u'Arrows', u'CJK-Punct', u'Fullwidth', u'Emoji',
                          u'Math', u'Greek', u'Misc-Symbols', u'Dingbats', u'Geometric', u'Hiragana',
                          u'Katakana', u'MathAlnum', u'EnclosedIdeo', u'EnclosedSuppl', u'Comb-Diacritic'])

# ---------- 全库计数成对替换 ----------
PAIRS = [
 (u'共 **49 条**（`babeltele/B01..B49`）', u'共 **%d 条**（`babeltele/B01..B50`）' % NENT),
 (u'**PASS**（49 条）', u'**PASS**（%d 条）' % NENT),
 (u'当前 **49 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (OLD_PROOFS, OLD_PROOFS),
  u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs)),
 (u'第二代（B11–B49）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B50）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'新建的 B49 待核列为空——它把两位以内的结构计数全部折进了 DERIV）未逐位核验，',
  u'新建的 B49 待核列为空——它把两位以内的结构计数全部折进了 DERIV；新建的 B50 同样为空——它的每个小整数都是六格矩阵上的一格引用, 已折进 %d 枚推导键）未逐位核验，' % len(DJ)),
 (u'（其后 B45／B46／B47／B49 同样为 0；只有 B48 有 1 项，即上面那条条目号 48）',
  u'（其后 B45／B46／B47／B49／B50 同样为 0；只有 B48 有 1 项，即上面那条条目号 48）'),
 (u'是**待核列为 0** 的 38 条条目里最连续的十二条',
  u'是**待核列为 0** 的 %d 条条目里最连续的十二条' % len(ZSOFT)),
]
for old, new in PAIRS:
    n = t.count(old)
    if n != 1:
        print(u'注意: 未命中或多处 -> %r (%d)' % (old[:50], n))
    assert n >= 1, old[:50]
    t = t.replace(old, new, 1)

R = t.split(u'\n')
done = []
for i, l in enumerate(R):
    if l.startswith(u'| **合计（49 条）**'):
        R[i] = (u'| **合计（%d 条）** | **%s** | **%s**（摘要段合计 %s） | — | **%s** | — |'
                % (NENT, fmt(enc_all), ret_all.strip(u'*'), fmt(dig_all), fmt(uniq_all)))
        done.append(u'合计')
        break
for i, l in enumerate(R):
    if l.startswith(u'Latin ') and u'· Han ' in l:
        R[i] = cen_s
        done.append(u'普查')
        break
for i, l in enumerate(R):
    if l.startswith(u'唯一码点 '):
        R[i] = u'唯一码点 %s / %s ≈ %.1f%%' % (fmt(uniq_all), fmt(enc_all), 100.0 * uniq_all / enc_all)
        done.append(u'唯一码点')
        break
for i, l in enumerate(R):
    if u'B49 把轴换成**表 ⇎ 检查这张表的程序 ⇎ 它检查的数据**' in l and l.rstrip().endswith(u'都不在任何窗口里。'):
        R[i] = l.rstrip() + (
            u'B50 把轴换成**同一台机器 ⇎ 六道难题**（登记 %d 条锚全部逐字回源 ok=%d bad=%d，正文标注 %d 处／%d 个不同串，'
            u'六个源标签 %s 各 %d–%d 条）：这条没有第三份文件作对照，形状全在六格矩阵的零格里——'
            u'%d 个键 × %d 格＝%d 格，为零的 %d 格（19 条老模式 %d 格＋9 条追加模式 %d 格）；一枚 0 键折 %d 项证明＝%d 个零格＋回答区那一格＋跨源命中数一项，'
            u'剩下 %d 格（%s）不进证明；回答区六段各 %d 字符、推倒重来六段 %d 次，'
            u'而等号在判例段 %d 枚、条款词在数论段 %d 枚、粗体只在两段出现，零比正更承重，因为零才跟着题目走。'
            u'三条口径纪律当场可数：区段三种切法的空白常数各 %d／%d／%d 字符（标记切片 ⇎ 采集侧多跳一格 ⇎ 严格正则不吃），题面两套长度恒差 %d；原始计数与每万字归一在 %d 条模式上翻名次、'
            u'六段末字符 %d/6 不是句终——“结论”这个词不在源里。'
            u'保留率 %s（字节口径 %s，六份源合计 %s 字符 ⇎ 磁盘 %s 字节，最长段是最短段的 %.1f 倍）是六源条的必然读数：'
            u'窗口按锚点截取，而“哪几格为零”要整段复算才看得见；'
            u'本脚本第三次独立测量这六份源（区段找法、%d 条模式正则、锚的归一函数都在此另写一份，%d 个可比键 %d 枚值与两份快照逐键相等），'
            u'所以上面这些零不是转述。'
            % (len(REG), AK, AB_, NOCC, DIST, u'／'.join(TAGS), min(NLAB.values()), max(NLAB.values()),
               len(ALLK), 6, len(ALLK) * 6, len(ZEROCELL), ZP, ZEX, ZT, ZNAMED, NUNREF,
               u'／'.join(UNCOVERED), min(AC), ME[u'redo'][0], ME[u'equality'][2], ME[u'cfr'][0],
               GAPF[0], GAP[0], RGAP[0], PGAP, len(FLIP), TAILBAD,
               b50_ret, b50_raw, fmt(RAW_SUM), fmt(sum(BYTES)), THIRD[u'rcratio'],
               len(ALLK), BOTH, VALS))
        done.append(u'口径段')
        break
assert u'口径段' in done, u'口径段未命中'

SRC6 = u' ⇎ '.join(u'`raw/cot/%s.md`（%s ⟦%s⟧: 推理区 %s ⇎ 文件 %s ⇎ 磁盘 %s 字节）'
                   % (SLUGS[i], CN[i], TAGS[i], fmt(RC[i]), fmt(SH[u'fchars'][i]), fmt(BYTES[i]))
                   for i in range(6))
GEN = (u'**B50 把对照轴换成同一台机器与它做的六道难题**：六份思维链 %s。'
       u'六段推理区合计 %s 字符（最长段 %s ⇎ 最短段 %s, %.1f 倍）, 回答区六段各 %d 字符；'
       u'同一模型有两种写法（%d 种: %s ⇎ %s, 去掉 `opencode/` 前缀后 %d 种）⇎ 题面哈希 %d 种且 %d/6 现场重算命中 ⇎ 抓取时刻 %d 组。'
       u'正文标注 %d 处／%d 个不同串（%s；登记表 %d 条经 atomcheck 真跑全部命中, 其中 %d 条只登记未在正文引用）, '
       u'判词 %d 行, 骨架 %d 条, 方法 %d 步, DERIV %d 键（%d 枚数值键逐条机检 ⇎ %d 枚名单键）, '
       u'0 键折 %d 项（%d 项是六格矩阵里为零的单元格、另 2 项是回答区一格与跨源命中数: 本条 %d 次 B50V 里 %d 次带格号 ⇎ %d 次取标量）, 每万字归一式 %d 枚（除 %d ⇎ 乘 %d ⇎ 加 %d）; 同值折等式 %d 组 %d 个说法。'
       u'关键结论: 风格可拆两层——跨题不变的词法习惯属机器, 记号选择属题目。'
       u'机器那层只问三种问题: 六格全正 %d 条（%s）⇎ 六格全零 %d 条（%s）⇎ 有零有正的算领域函数。'
       u'后者当场可数: 等号 %s ⇎ 归一 %s, 条款词 %s, must %s, 粗体 %s, 箭头 %s。'
       u'口径恒差三处: 区段三种切法 %d／%d／%d 字符 ⇎ 题面两套长度差 %d ⇎ 模型串 %d 种写法折成 %d 种实体。'
       u'词形陷阱两处点名: 数 restart 得 %s（非零那枚在说装置重启）⇎ 只按 not sure 一族数“承认不确定”得 %s 而 uncertain 词形是 %s（震后段明说 %d 次、词形 %d 次）。'
       u'六段起手同属两类套话（We need %d 段 ⇎ …disabled %d 段）而首行去重 %d 种, %d 条锚 × %d 段＝%d 次成员检查里跨源命中 %d 条——套话没有把对照抹平。'
       ) % (SRC6, fmt(sum(RC)), fmt(A[u'rcmax']), fmt(A[u'rcmin']), THIRD[u'rcratio'], min(AC),
            len(MODELS), MODELS[0], MODELS[1], len(BARE), HASHES, SHA_OK, RETR,
            NOCC, DIST, u' '.join(u'⟦%s⟧ %d' % (x, NLAB[x]) for x in TAGS), len(REG), UNCITED,
            GLOS, NSKEL, NSTEP, KEYS, len(DJ), len(LISTKEYS), ZT, ZNAMED, FAMS[u'B50V'], IDX, PLAIN,
            NRND, NRND, NRND, OPS[u'Add'], NCG, NCV,
            len(ALLPOS), u'、'.join(ALLPOS), len(SIXZERO), u'、'.join(SIXZERO),
            cellrow(u'equality'), p10row(u'equality'), cellrow(u'cfr'), cellrow(u'must'),
            cellrow(u'bold'), cellrow(u'arrow'),
            GAPF[0], GAP[0], RGAP[0], PGAP, len(MODELS), len(BARE),
            cellrow(u'restart_word'), cellrow(u'unsure'), cellrow(u'uncertain_word'),
            ME[u'unsure'][5], ME[u'uncertain_word'][5],
            WENEED, DISABL, DISTINCT_FIRST, len(REG), 6, CHECKS, MULTI)
for i, l in enumerate(R):
    if l.startswith(u'**B49 把对照轴换成表、检查这张表的程序与它检查的数据**'):
        R[i] = l + u'\n\n' + GEN
        done.append(u'B50 段')
        break
assert u'B50 段' in done, u'B50 段未命中'

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B49 | %s（新建' % fmt(b49_enc)):
        ins.append((i + 1, u'| B50 | %s（新建, 同一模型⇎六道难题 %d 处标注／%d 个不同串（登记 %d 条锚全命中, %d 条未引用）: '
                           u'六源六色锚位 math_subsets ⟦M⟧ ⇎ med_gitalb ⟦D⟧ ⇎ law_ewca_method ⟦L⟧ ⇎ fin_credit_cmte ⟦F⟧ ⇎ ind_creep_rupture ⟦I⟧ ⇎ str_quake_slab ⟦S⟧; '
                           u'最强一环是六格矩阵的零格: %d 键 × %d 格＝%d 格里 %d 格为零, 一枚 0 键折 %d 项（%d 项是零格＋回答区一格＋跨源命中数一项）, 剩下 %d 格不进证明; '
                           u'回答区六段各 %d 字符 ⇎ 推倒重来 %d 次 ⇎ 末字符非句终 %d/6, 故“结论”不在源内; '
                           u'DERIV %d 键（数值 %d ⇎ 名单 %d）, B50V %d 次（带格号 %d ⇎ 标量 %d）, 归一式 %d 枚; 同值折等式 %d 组; '
                           u'口径恒差: 区段三切法 %d／%d／%d ⇎ 题面两套 %d ⇎ 模型串 %d 写法／%d 实体; 词形陷阱: restart 非零 %d 枚说的是装置 ⇎ uncertain 词形 %d 次而明说 0 次; '
                           u'起手套话两类（We need %d ⇎ disabled %d）而首行去重 %d 种, 锚跨源命中 %d 条） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为记号名、模式键名与英文原词） | %s | %s |'
                           % (fmt(b50_enc), NOCC, DIST, len(REG), UNCITED,
                              len(ALLK), 6, len(ALLK) * 6, len(ZEROCELL), ZT, ZNAMED, NUNREF,
                              min(AC), ME[u'redo'][0], TAILBAD,
                              KEYS, len(DJ), len(LISTKEYS), FAMS[u'B50V'], IDX, PLAIN, NRND, NCG,
                              GAPF[0], GAP[0], RGAP[0], PGAP, len(MODELS), len(BARE), ME[u'restart_word'][4],
                              ME[u'uncertain_word'][5], WENEED, DISABL, DISTINCT_FIRST, MULTI,
                              NOCC, fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b50_ret, fmt(b50_dig))))
    elif l.startswith(u'| B49 | %s | %s' % (fmt(b49_enc), b49_ret)):
        ins.append((i + 1, u'| B50 | %s | %s | %s（字节口径; 六份源合计 %s 字符 ⇎ 磁盘 %s 字节——'
                           u'判词要在六格矩阵上数“哪几格为零”（复算 ⇎ 归一 ⇎ 两套快照对表），而摘要段只索引锚点触到的窗口，'
                           u'故保留率 %s 属六源对照条的必然读数，按“%d 枚数值键支撑 %d 行判词”来读；'
                           u'原料本身很大（六段推理区合计 %s 字符，最长段 %s ⇎ 最短段 %s，而六段的回答区各 %d 字符），'
                           u'但“推倒重来六段皆零、等号密度差三个数量级”这一判既不在任何一段里也不在窗口里，摊开六格才看得见；'
                           u'工具侧两套实现的比对（%d 个可比键 ⇎ %d 枚值）与第三次独立复算写在 ⛓解读注与本脚本, 不冒充机检） | %d | %s |'
                           % (fmt(b50_enc), b50_ret, b50_raw, fmt(RAW_SUM), fmt(sum(BYTES)),
                              b50_ret, len(DJ), GLOS, fmt(sum(RC)), fmt(A[u'rcmax']), fmt(A[u'rcmin']),
                              min(AC), BOTH, VALS, b50_uniq, b50_cpu)))
    elif l.startswith(u'| B49 | `raw/tz/zone1970.tab`'):
        ins.append((i + 1, u'| B50 | ' + SRC6 + u'（六份同模型输出, 头部自报区段长度与实测逐份相等） | 同一模型 ⇎ 六道题 ⇒ 风格拆两层: '
                           u'六格全正 %d 条（%s）⇎ 全零 %d 条（%s）⇎ 有零有正算题目; 零格 %d／%d 格（%d 格写进 0 键, %d 格未进证明）; '
                           u'等号 %s ⇎ 条款词 %s ⇎ 粗体 %s ⇎ 箭头 %s; 归一后翻名次 %d 条; '
                           u'口径恒差: 区段三切法 %d／%d／%d ⇎ 题面两套 %d ⇎ 模型串 %d 写法／%d 实体; '
                           u'哈希自校验 %d/6 ⇎ 抓取时刻 %d 组 ⇎ 末字符非句终 %d/6 ⇎ 回答区 %d 字符 × 6 ⇒ '
                           u'“会不会写算式”是题目的函数, “等一下才继续”才是机器的习惯 |'
                           % (len(ALLPOS), u'、'.join(ALLPOS), len(SIXZERO), u'、'.join(SIXZERO),
                              len(ZEROCELL), len(ALLK) * 6, ZNAMED, NUNREF,
                              cellrow(u'equality'), cellrow(u'cfr'), cellrow(u'bold'), cellrow(u'arrow'),
                              len(FLIP), GAPF[0], GAP[0], RGAP[0], PGAP, len(MODELS), len(BARE),
                              SHA_OK, RETR, TAILBAD, min(AC))))
    elif l.startswith(u'python -X utf8 corpus/_readme49.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_probe50.py               # 探测六份源: 头部自报 reasoning/answer 长度 ⇎ 实测区段逐份对齐, prompt_sha256 现场重算 %d/6 命中; 19 条核心模式落 corpus/_f50stats.txt\n'
                    u'python -X utf8 corpus/_pick50.py                # 选锚: 每条锚由正则从“它那一段”截出, 再验 %d 条锚 × 6 段＝%d 次成员检查里跨源命中 %d 条; 六格矩阵、两种区段口径与每万字归一全部现算\n'
                    u'python -X utf8 corpus/_mkB50.py                 # 建条目: 六色锚位(M/D/L/F/I/S), 六格矩阵的零格折进一枚 0 键(%d 项), 同值冲突 %d 组逐个登记含义\n'
                    u'python -X utf8 corpus/_wire50.py                # 把 _B50 与 B50V 接进 audit.py(审计器侧另算一套), DERIV %d 键\n'
                    u'python -X utf8 corpus/_mkdigest3.py B50 <entry> M <raw/cot/math_subsets.md> 40 90 D ...   # 六源分节摘要, 每源按命中锚各自分块(%d 节 ⇎ 正文 %d 处标注全部命中窗口, 精确子串亦 %d 处)\n'
                    u'python -X utf8 corpus/atomcheck.py B50 corpus/_atoms50.txt   # 登记 %d 条锚逐字回源 ok=%d bad=%d（正文标注 %d 处／%d 个不同串, %d 条只登记未引用）\n'
                    u'python -X utf8 corpus/_fill50.py                # ⛓解读注: 两套实现快照 %d 个可比键 %d 枚值逐键相等才落盘; 锚的三口径(逐字 %d ⇎ 折空白 %d ⇎ 归一 %d)在本条完全重合\n'
                    u'python -X utf8 corpus/_readme50.py              # 记账: 本脚本第三次独立测量六份源(区段找法 ⇎ %d 条模式正则 ⇎ 锚归一函数皆另写一份), 并与两份快照逐键对表, 故 README 里的零格断言不是转述'
                    % (SHA_OK, len(REG), CHECKS, MULTI, ZT, NCG, KEYS,
                       BLOCKS, DIGHIT, EXACT, len(REG), AK, AB_, NOCC, DIST, UNCITED,
                       BOTH, VALS, exact, folded, normed, len(ALLK))))
assert len(ins) == 4, [x[1][:30] for x in ins]
for pos, txt_ in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt_)
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if not l.startswith((u'| B49 |', u'**B49', u'B49 '))
        and re.search(u'49 条|B01\\.\\.B49|%s|%s 条|%s|%s|%%s（新建|%%d 键' % (
            re.escape(fmt(b49_enc)), OLD_PROOFS, re.escape(fmt(prev_in)), re.escape(fmt(prev_out))), l)]
print(u'README %d 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 摘要 %s 编码 %s 保留 %s 码点 %s 推导 %d 待核 %d｜'
      u'待核 0 的条目 %d 条｜第二代 %s／%s｜零格 %d／%d 写进 0 键 %d 未进证明 %d'
      % (NENT, u'/'.join(done), len(left), fmt(dig_all), fmt(enc_all), ret_all, fmt(uniq_all), proofs,
         soft_all, len(ZSOFT), fmt(in_lat), fmt(out_lat), len(ZEROCELL), len(ALLK) * 6, ZNAMED, NUNREF))
for l in left:
    print(u'  ' + l[:150])
print(u'B50: enc %s dig %s ret %s raw %s uniq %d blocks %d cpu %s soft %d｜锚 %d/%d 串 引用 %d 处 未引 %d 标签 %s｜'
      u'推理区 %s 合计 %s 比 %.1f 回答区 %s｜文件 %s 字节 %s 行 %s 非ASCII %s｜'
      u'模型 %d 种→%d 哈希 %d 自校验 %d/6 时刻 %d 组 末符非句终 %d/6｜'
      u'DERIV %d 键(数值 %d ⇎ 名单 %d) 0 键 %d 项 B50V %d(格 %d/标量 %d) 归一 %d 加 %d｜同值 %d 组 %d 说｜'
      u'模式 %d+额外 %d 矩阵格 %d 零格 %d 点名 %d 未引 %d(%s)｜翻转 %d 皆正 %d 皆零 %s｜'
      u'口径差 区段 %d 题面 %d｜起手 We need %d/disabled %d/去重 %d｜锚三口径 %d/%d/%d 互斥检查 %d 跨源 %d｜'
      u'digest %d 节 %d 字符 ⇎ 编码 %d(%.1f%%)｜三套对表 %d 键 %d 值'
      % (fmt(b50_enc), fmt(b50_dig), b50_ret, b50_raw, b50_uniq, b50_blocks, b50_cpu, b50_soft,
         len(REG), len(set(REG)), NOCC, UNCITED, u' '.join(u'%s:%d' % (x, NLAB[x]) for x in TAGS),
         RC, fmt(sum(RC)), THIRD[u'rcratio'], AC, SH[u'fchars'], BYTES, NLINES, NASC,
         len(MODELS), len(BARE), HASHES, SHA_OK, RETR, TAILBAD,
         KEYS, len(DJ), len(LISTKEYS), ZT, FAMS[u'B50V'], IDX, PLAIN, NRND, OPS[u'Add'],
         NCG, NCV, len(PATS), len(EXTRA), len(ALLK) * 6, len(ZEROCELL), ZNAMED, NUNREF,
         u'／'.join(UNCOVERED), len(FLIP), len(ALLPOS), SIXZERO, GAP[0], PGAP,
         WENEED, DISABL, DISTINCT_FIRST, exact, folded, normed, CHECKS, MULTI,
         BLOCKS, DL, EL, 100.0 * EL / DL, BOTH, VALS))
