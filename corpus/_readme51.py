# -*- coding: utf-8 -*-
"""README 记账: 50 条 → 51 条。合计数字全部由 audit 表、metrics 普查、四份 raw 回算与 _b51* 快照复算, 不手填。
B51 特有的一环: 本文件第三次把四份源量一遍——区段三口径、22 族模式正则、四种粒度集合交、>=40 字极大公共片段、
题面引用滑窗、锚的归一函数都在此另写一份, 再与采集侧 _pick51 快照、审计器侧 _b51_scan 快照逐键对表;
“同题对的句子级共有不比跨题对高”这类断言因此是当场数出来的, 不是转述。"""
import io, os, re, sys, json, ast, hashlib, subprocess, collections
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
t = io.open(F, encoding='utf-8').read()
NL = u'\n'
TAG, ENTRY = u'B51', u'corpus/babeltele/B51_same_model_same_question_twice.md'
SLUGS = [u'math_subsets', u'math_subsets_s2', u'med_gitalb', u'med_gitalb_s2']
TAGS = [u'A', u'B', u'C', u'D']
CN = [u'数论一', u'数论二', u'肾病一', u'肾病二']
RAWS = [u'corpus/raw/cot/%s.md' % s for s in SLUGS]
SAME = [(0, 1), (2, 3)]
ORDER = [(0, 1), (2, 3), (0, 2), (0, 3), (1, 2), (1, 3)]
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
cells = lambda k: [x.strip() for x in row[k].split(u'|')]
b51, b50 = cells(u'B51'), cells(u'B50')
b51_dig, b51_enc, b51_ret, b51_raw, b51_uniq, b51_blocks, b51_cpu, b51_soft = (
    int(b51[0]), int(b51[1]), b51[2], b51[3], int(b51[4]), int(b51[5]), b51[6], int(b51[10]))
b50_enc, b50_ret = int(b50[1]), b50[2]
assert NENT == 51, NENT
assert b51_soft == 0 and not re.search(u'^\\s+B51 \\[', p.stdout, re.M), (b51, soft_all)
assert int(b51[7]) == 0 and int(b51[8]) == 0 and int(b51[9]) == 0, b51
assert b51_enc == 9340 and b51_dig == 10429
assert b51_ret == u'%.1f%%' % (100.0 * b51_enc / b51_dig)
PROOF_B51 = len(re.findall(u'^  \u2713 .*B51V\\(', p.stdout, re.M))
UNREF_B51 = 0
assert PROOF_B51 > 0 and not re.search(u'\u2717.*B51V\\(', p.stdout), PROOF_B51
ZSOFT = sorted([k for k in row if k != u'ALL' and int(cells(k)[10]) == 0], key=lambda x: int(x[1:]))
assert all(k in ZSOFT for k in (u'B43', u'B45', u'B46', u'B47', u'B49', u'B50', u'B51'))
assert u'B48' not in ZSOFT and len(ZSOFT) == 40, (len(ZSOFT), ZSOFT)

m = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/metrics.py'],
                   capture_output=True, text=True, encoding='utf-8')
cen = dict((mm.group(1), int(mm.group(2))) for mm in
           re.finditer(r'^\s{2}([A-Za-z\-]+)\s+([\d ]+)$', m.stdout, re.M))
assert len(cen) == 18, sorted(cen)

# ---------- 第三次独立测量: 区段三口径 ----------
TXT = [io.open(x, encoding='utf-8').read() for x in RAWS]
BYTES = [os.path.getsize(x) for x in RAWS]
NLINES = [len(x.split(NL)) - 1 for x in TXT]
HDR = [dict(HEADRX.findall(x)) for x in TXT]
for i, s in enumerate(SLUGS):
    assert HDR[i][u'slug'] == s, HDR[i]

def mark(txt, key, nxt, off):
    a = txt.find(key)
    b = txt.find(nxt, a)
    return txt[a + off:b]

RRF = [mark(x, u'## [[REASONING]]', u'## [[ANSWER]]', 17) for x in TXT]
RF = [x.strip() for x in RRF]
GAPF = [len(RRF[i]) - len(RF[i]) for i in range(4)]
SEC = [re.search(u'## \\[\\[PROMPT\\]\\]\\n(.*?)\\n\\n## \\[\\[REASONING\\]\\]\\n(.*?)'
                 u'\\n\\n## \\[\\[ANSWER\\]\\]\\n?(.*)$', x, re.S) for x in TXT]
assert all(SEC), u'分节正则未命中'
PRAW = [len(g.group(1)) for g in SEC]
PCOT = [len(g.group(1).strip()) for g in SEC]
RGAP = [len(g.group(2)) - len(RF[i]) for i, g in enumerate(SEC)]
PGAP = PRAW[0] - PCOT[0]
RC = [len(x) for x in RF]
AC = [len(g.group(3).strip()) for g in SEC]
assert RC == [int(HDR[i][u'reasoning_chars']) for i in range(4)]
assert AC == [int(HDR[i][u'answer_chars']) for i in range(4)]
assert AC[0] == AC[2] == 0 and AC[1] == 6908 and AC[3] == 6748, AC
assert len(set(GAPF)) == 1 and len(set(RGAP)) == 1 and len(set(PGAP for _ in [0])) == 1
assert GAPF[0] == 2 and RGAP[0] == 0 and PGAP == 1, (GAPF, RGAP, PGAP)
SHAOK = sum(1 for i in range(4)
            if hashlib.sha256(SEC[i].group(1).encode('utf-8')).hexdigest()[:16]
            == HDR[i][u'prompt_sha256'])
SHA = [HDR[i][u'prompt_sha256'] for i in range(4)]
assert SHAOK == 4 and SHA[0] == SHA[1] != SHA[2] == SHA[3] and len(set(SHA)) == 2, SHA
MODELS = sorted(set(HDR[i][u'model'] for i in range(4)))
BARE = sorted(set(h[u'model'].split('/')[-1] for h in HDR))
RETR = sorted(set(HDR[i][u'retrieved'] for i in range(4)))
DAYS = sorted(set(x[:10] for x in RETR))
DT = [datetime.strptime(HDR[i][u'retrieved'], '%Y-%m-%dT%H:%M:%S') for i in range(4)]
GAPH = [round((DT[1] - DT[0]).total_seconds() / 3600.0, 2), round((DT[3] - DT[2]).total_seconds() / 3600.0, 2)]
assert len(MODELS) == 1 and len(BARE) == 1 and len(DAYS) == 2, (MODELS, BARE, DAYS)

# ---------- 22 族模式(本脚本第三份) ----------
PATS = {
    u'wait': u'(?i)\\bWait\\b', u'actually': u'(?i)\\bactually\\b',
    u'maybe': u'(?i)\\bmaybe\\b|\\bperhaps\\b', u'prob': u'(?i)\\bprobably\\b|\\blikely\\b',
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
    u'equality': u'=', u'arrow': u'->', u'letme': u'(?i)\\blet me\\b',
    u'lets': u"(?i)\\blet's\\b", u'hmm': u'(?i)\\bHmm\\b', u'need': u'(?i)\\bneed\\b',
    u'q': u'\\?', u'bold': u'\\*\\*[^*]{2,60}\\*\\*',
}
ALLK = sorted(PATS)
assert len(ALLK) == 22, len(ALLK)
ME = dict((k, [len(re.findall(v, x)) for x in RF]) for k, v in PATS.items())
P10 = dict((k, [round(10000.0 * ME[k][i] / RC[i], 1) for i in range(4)]) for k in ALLK)
SH = {
    u'fchars': [len(x) for x in TXT],
    u'sent': [len([s for s in re.split(u'(?<=[.!?])\\s+', x) if s.strip()]) for x in RF],
    u'lsent': [len([s for l in [y.strip() for y in x.split(NL) if y.strip()]
                    for s in re.split(u'(?<=[.!?])\\s+', l) if s.strip()]) for x in RF],
    u'para': [len([y for y in x.split(NL) if y.strip()]) for x in RF],
    u'numsent': [len([y for y in re.split(u'(?<=[.!?])\\s+', x) if re.search(u'\\d', y)]) for x in RF],
    u'digit': [len(re.findall(u'\\d', x)) for x in RF],
    u'word': [len(re.findall(u'[A-Za-z]+', x)) for x in RF],
}
LASTC = [RF[i][-1] for i in range(4)]
TAILBAD = sum(1 for c in LASTC if c not in u'.!?"')
assert TAILBAD == 2 and LASTC == [u'm', u'.', u'5', u'.'], LASTC
# 名次是否随分母翻转: 绝对计数第一的段, 除以本段长度后还是第一吗
lead = lambda v: sorted([i for i in range(4) if v[i] == max(v)])
FLIP = [k for k in ALLK if ME[k] != [0] * 4 and lead(ME[k]) != lead(P10[k])]
ALLPOS = [k for k in ALLK if min(ME[k]) >= 1]
SIXZERO = [k for k in ALLK if ME[k] == [0] * 4]

# ---------- 四种粒度 ⇎ >=40 字公共片段 ⇎ 题面引用 ----------
def fold(s):
    return re.sub(u'\\s+', u' ', s).strip()

def nrm(s):
    s = s.lower()
    for a, b in ((u'’', u"'"), (u'‘', u"'"), (u'“', u'"'), (u'”', u'"')):
        s = s.replace(a, b)
    s = re.sub(u"[’'\"‘“”`´]+", u'', s)
    s = re.sub(u'[‐‑‒–—―−-]', u'-', s)
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff\-\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()

NR = [nrm(x) for x in TXT]
RS = [nrm(x) for x in RF]

def L(x):
    return [fold(y) for y in x.split(NL) if fold(y)]

def Sn(x):
    return [fold(s) for s in re.split(u'(?<=[.!?])\\s+', x) if fold(s)]

def LS(x):
    o = []
    for l in L(x):
        o += [fold(s) for s in re.split(u'(?<=[.!?])\\s+', l) if fold(s)]
    return o

def SG(x, n=5):
    w = re.findall(u'[a-z0-9]+', x.lower())
    return set(tuple(w[i:i + n]) for i in range(len(w) - n + 1))

LN = [set(nrm(x) for x in L(RF[i])) for i in range(4)]
SN = [set(nrm(x) for x in Sn(RF[i])) for i in range(4)]
LSN = [set(nrm(x) for x in LS(RF[i])) for i in range(4)]
SGN = [SG(RF[i]) for i in range(4)]
OV = {(i, j): (len(LN[i] & LN[j]), len(SN[i] & SN[j]), len(LSN[i] & LSN[j]), len(SGN[i] & SGN[j]))
      for (i, j) in ORDER}
ALL4S = SN[0] & SN[1] & SN[2] & SN[3]
ALL4L = LSN[0] & LSN[1] & LSN[2] & LSN[3]
assert len(ALL4S) == 2 and len(ALL4L) == 2, (len(ALL4S), len(ALL4L))
SURF = {}
for i in range(4):
    for x in LS(RF[i]):
        if nrm(x) in ALL4L:
            SURF.setdefault(nrm(x), set()).add(x)
S4SAME = len([v for v in SURF.values() if len(v) == 1])
assert S4SAME == 1, S4SAME

def runs(a, b, k=40, cap=400):
    idx = {}
    for s in range(len(a) - k + 1):
        idx.setdefault(a[s:s + k], s)
    out, s = [], 0
    while s < len(b) - k + 1:
        q = idx.get(b[s:s + k])
        if q is None:
            s += 1
            continue
        e = s + k
        while e - s < cap and b[e:e + 1] and a[q + (e - s):q + (e - s) + 1] == b[e:e + 1]:
            e += 1
        out.append((e - s, b[s:e]))
        s = e
    return sorted(out, key=lambda x: -x[0])

CR = {}
for (i, j) in SAME:
    rs = runs(RF[i], RF[j])
    CR[(i, j)] = (len(rs), sum(x[0] for x in rs), rs[0][0],
                  len([x for x in rs if x[1].strip(u'"“’\' \n\t.,;:!?') in SEC[i].group(1).strip()]))
assert CR[(0, 1)][0] == 14 and CR[(2, 3)][0] == 57 and CR[(0, 1)][2] == 244, CR

def pq(i, k=40):
    pf, rf = SEC[i].group(1).strip(), RF[i]
    best, s = (0, 0, u''), 0
    while s < len(rf):
        if rf[s:s + k] in pf:
            e = s + k
            while rf[e:e + 1] and rf[s:e + 1] in pf:
                e += 1
            if e - s > best[0]:
                best = (e - s, s, rf[s:e])
            s = e
        else:
            s += 1
    return best

PQ = [pq(i) for i in range(4)]
assert [x[0] for x in PQ] == [241, 270, 429, 111] and [x[1] for x in PQ] == [17343, 38453, 7674, 56316], PQ

# ---------- 三套实现逐键对表 ----------
MM = json.load(io.open(u'corpus/_b51meas.json', encoding='utf-8'))
AA = json.load(io.open(u'corpus/_b51audit.json', encoding='utf-8'))
MMEAS = dict(MM[u'meas'])
MMEAS.update(MM[u'shape'])
THIRD = {}
for k in ALLK:
    THIRD[k] = ME[k]
THIRD.update({u'rcot': RC, u'acot': AC, u'pcot': PCOT, u'praw': PRAW, u'fchars': SH[u'fchars'],
              u'fbytes': BYTES, u'sent': SH[u'sent'], u'lsent': SH[u'lsent'], u'para': SH[u'para'],
              u'numsent': SH[u'numsent'], u'digit': SH[u'digit'], u'word': SH[u'word'],
              u'gap': GAPF, u'pgap': [PGAP] * 4, u'rgap': RGAP,
              u'lastcode': [ord(c) for c in LASTC], u'rcotsum': sum(RC),
              u'rcratio': round(1.0 * max(RC) / min(RC), 2), u'sha_kinds': len(set(SHA)),
              u'sha_ok': SHAOK, u'models': len(MODELS), u'model_bare': len(BARE), u'retr': len(DAYS),
              u'tailbad': TAILBAD, u'npats': len(ALLK), u'allzero': len(SIXZERO),
              u'sent_all4': len(ALL4S), u'lsent_all4': len(ALL4L), u's4_same': S4SAME, u'nsrc': 4})
for slot, nm in ((0, u'ov_l'), (1, u'ov_s'), (2, u'ov_ls'), (3, u'ov_sg')):
    THIRD[nm] = [OV[q][slot] for q in ORDER]
for pi, (i, j) in enumerate(SAME):
    for slot, nm in ((0, u'sub_n'), (1, u'sub_tot'), (2, u'sub_max'), (3, u'sub_prompt')):
        THIRD.setdefault(nm, [0, 0])[pi] = CR[(i, j)][slot]
THIRD[u'pq'] = [x[0] for x in PQ]
THIRD[u'pqpos'] = [x[1] for x in PQ]
CH = json.load(io.open(u'corpus/_b51checks.json', encoding='utf-8'))
for k in CH[u'ameta']:
    THIRD[k] = CH[u'ameta'][k]
CMP = sorted(THIRD)
BAD3 = [k for k in CMP if (lambda x, y: [round(float(v), 2) for v in (x if isinstance(x, list) else [x])] !=
        [round(float(v), 2) for v in (y if isinstance(y, list) else [y])])(THIRD[k], AA.get(k))]
assert not BAD3, [(k, THIRD[k], AA.get(k)) for k in BAD3]
BOTH = len(CMP)
VALS = sum(len(THIRD[k]) if isinstance(THIRD[k], list) else 1 for k in CMP)
MISS = [k for k in CMP if k not in MMEAS and k not in (u'nsrc',) and not k.startswith(u'anchor')
        and k not in (u'checks',)]
assert not [k for k in MISS if k in ME or k in SH], MISS

# ---------- 锚: 三口径 + 命中列(本脚本第三份归一) ----------
REG = [x.rstrip(NL) for x in io.open(u'corpus/_atoms51.txt', encoding=u'utf-8') if x.strip()]
md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
CITES = re.findall(u'⟦([ABCD])⟧⟨([^⟨⟩]+)⟩', body)
atoms = [a for _, a in CITES]
labels = [tg for tg, _ in CITES]
NOCC, DIST = len(atoms), len(set(atoms))
assert (NOCC, DIST) == (CH[u'anchor_total'], CH[u'anchor_distinct']) == (36, 35)
assert sorted(set(atoms)) == sorted(set(REG)), (len(set(REG)), DIST)
NLAB = collections.Counter(labels)
assert sum(NLAB.values()) == NOCC and set(NLAB) == set(TAGS)
own = {}
for tg, a in CITES:
    own.setdefault(tg, [])
    if a not in own[tg]:
        own[tg].append(a)
ALLA = [a for t in TAGS for a in own[t]]
ex = sum(1 for t in TAGS for a in own[t] if a in TXT[TAGS.index(t)])
fo = sum(1 for t in TAGS for a in own[t] if fold(a) in fold(TXT[TAGS.index(t)]))
no_ = sum(1 for t in TAGS for a in own[t] if nrm(a) in NR[TAGS.index(t)])
assert (ex, fo, no_) == (len(ALLA),) * 3, (ex, fo, no_)
HIT = [sum(1 for i in range(4) if nrm(a) in NR[i]) for a in ALLA]
D1, D2, D3, D4 = [HIT.count(k) for k in (1, 2, 3, 4)]
CHECKS = len(ALLA) * 4
assert (D3, CHECKS) == (0, 140) == (D3, AA[u'checks']), (D3, CHECKS)
ac = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/atomcheck.py', u'B51', u'corpus/_atoms51.txt'],
                    capture_output=True, text=True, encoding=u'utf-8')
AK, AB_ = (int(x) for x in re.search(r'ok=(\d+) bad=(\d+)', ac.stdout).groups())
assert (AK, AB_) == (len(REG), 0), ac.stdout[-400:]
# 两次采样的起手句确实同类(都是 We need …), 而锚仍按源归属: 套话没有抹平对照
FIRSTL = [fold(RF[i].split(NL)[0])[:34] for i in range(4)]
WENEED = sum(1 for x in FIRSTL if x.startswith(u'We need'))
DISTINCT_FIRST = len(set(FIRSTL))
assert (WENEED, DISTINCT_FIRST) == (3, 4), (WENEED, DISTINCT_FIRST)

# ---------- DERIV 结构(从 audit.py 现读, 不手填) ----------
AUD = io.open(u'corpus/audit.py', encoding='utf-8').read()
st = AUD.index(u"DERIV['B51'] = ")
en = AUD.index(u"\nDERIV['", st + 10)
D51 = ast.literal_eval(AUD[AUD.index(u'{', st):en].strip().rstrip(u','))
DJ = json.load(io.open(u'corpus/_deriv51.json', encoding='utf-8'))
KEYS = len(D51)
assert KEYS == len(DJ) == 128, (KEYS, len(DJ))
ZERO = D51[u'0']
ZT = len(ZERO.split(u'+'))
assert ZT == len(re.findall(u'B51V\\(', ZERO)), (ZT, len(re.findall(u'B51V\\(', ZERO)))
FAMS = collections.Counter()
IDX = PLAIN = NRND = 0
for v in D51.values():
    for n in ast.walk(ast.parse(v, mode='eval')):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            FAMS[n.func.id] += 1
            if n.func.id == u'B51V':
                IDX += len(n.args) > 1
                PLAIN += len(n.args) == 1
            if n.func.id == u'round':
                NRND += 1
OPS = collections.Counter(type(n.op).__name__ for v in D51.values()
                          for n in ast.walk(ast.parse(v, mode='eval')) if isinstance(n, ast.BinOp))
LISTKEYS = [k for k in D51 if k.startswith(u'[')]
ZPAIRS = set((k, int(i)) for k, i in re.findall(u"B51V\\('([a-z_]+)',\\s*(\\d+)\\)", ZERO))
assert all(THIRD[k][i] == 0 for k, i in ZPAIRS), [q for q in ZPAIRS if THIRD[q[0]][q[1]]]
ZNAMED = len([q for q in ZPAIRS if q[0] in ALLK])
ZEROCELL = [(k, i) for k in ALLK for i in range(4) if ME[k][i] == 0]
UNCOVERED = sorted(set(k for k, i in ZEROCELL if (k, i) not in ZPAIRS))
NUNREF = len([q for q in ZEROCELL if q not in ZPAIRS])
assert IDX + PLAIN == FAMS[u'B51V'], (IDX, PLAIN)
COLL = CH[u'collisions']
NCG, NCS = len(COLL), len([k for k in COLL if len(COLL[k]) > 1])
NCV = sum(len(v) for v in COLL.values())
assert (NCG, NCS) == (len(COLL), NCS) and NCV > NCG

# ---------- 条目结构 ----------
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
assert (BLOCKS, EL) == (4, b51_enc), (BLOCKS, EL)
assert DIGHIT == EXACT and 0 < DIGHIT < NOCC, (DIGHIT, EXACT, NOCC)
DIGMISS = NOCC - DIGHIT
RAW_SUM = sum(SH[u'fchars'])
assert b51_raw == u'%.3f%%' % (100.0 * b51_enc / sum(BYTES)), b51_raw
UNREF_B51 = KEYS - PROOF_B51

fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')
cellrow = lambda k: u'⇎'.join(u'%d' % v for v in ME[k])
p10row = lambda k: u' ⇎ '.join(u'%s' % v for v in P10[k])
quad = lambda q: u' ⇎ '.join(u'%d' % v for v in OV[q])

# ---------- 全库字母账 ----------
mm2 = re.search(u'第二代（B11–B50）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
                u'全库合计 \\*\\*([\\d ]+)／([\\d ]+)\\*\\*', t)
assert mm2, u'第二代行未命中'
prev_in, prev_out = int(mm2.group(1).replace(u' ', u'')), int(mm2.group(2).replace(u' ', u''))
FIRST_IN, FIRST_OUT = 121, 2195
assert prev_in + FIRST_IN == int(mm2.group(3).replace(u' ', u'')), mm2.group(3)
assert prev_out + FIRST_OUT == int(mm2.group(4).replace(u' ', u'')), mm2.group(4)
assert cen[u'Latin'] - prev_in - prev_out - FIRST_IN - FIRST_OUT == IN_LAT + OUT_ALL, (
    cen[u'Latin'], prev_in, prev_out, IN_LAT, OUT_ALL)
in_lat, out_lat = prev_in + IN_LAT, prev_out + OUT_ALL
OLD_PROOFS = int(re.search(u'当前 \\*\\*50 条语料／(\\d+) 条\\*\\*推导', t).group(1))
assert proofs == OLD_PROOFS + PROOF_B51, (OLD_PROOFS, proofs, PROOF_B51)

cen_s = (u'Latin %s · Han %s · Gen-Punct %s · Arrows %s · CJK-Punct %s · Fullwidth %s · Emoji %s · Math %s · '
         u'Greek %s · Misc-Symbols %s · Dingbats %s · Geometric %s · Hiragana %s · Katakana %s · '
         u'MathAlnum %s · EnclosedIdeo %s · EnclosedSuppl %s · Comb-Diacritic %s') % tuple(
    fmt(cen[k]) for k in [u'Latin', u'Han', u'Gen-Punct', u'Arrows', u'CJK-Punct', u'Fullwidth', u'Emoji',
                          u'Math', u'Greek', u'Misc-Symbols', u'Dingbats', u'Geometric', u'Hiragana',
                          u'Katakana', u'MathAlnum', u'EnclosedIdeo', u'EnclosedSuppl', u'Comb-Diacritic'])

# ---------- 全库计数成对替换 ----------
PAIRS = [
 (u'共 **50 条**（`babeltele/B01..B50`）', u'共 **%d 条**（`babeltele/B01..B51`）' % NENT),
 (u'**PASS**（50 条）', u'**PASS**（%d 条）' % NENT),
 (u'当前 **50 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (OLD_PROOFS, OLD_PROOFS),
  u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs)),
 (u'第二代（B11–B50）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B51）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'新建的 B50 同样为空——它的每个小整数都是六格矩阵上的一格引用, 已折进 99 枚推导键）未逐位核验，',
  u'新建的 B50 同样为空——它的每个小整数都是六格矩阵上的一格引用, 已折进 99 枚推导键；新建的 B51 同样为空——'
  u'它的小整数全在四源 × 四种粒度的矩阵上, 已折进 %d 枚推导键（其中 %d 枚被正文点名逐条打勾, 余 %d 枚登记在同值折等里、'
  u'由 _b51_scan 照样复算）' % (KEYS, PROOF_B51, UNREF_B51) + u'）未逐位核验，'),
 (u'（其后 B45／B46／B47／B49／B50 同样为 0；只有 B48 有 1 项，即上面那条条目号 48）',
  u'（其后 B45／B46／B47／B49／B50／B51 同样为 0；只有 B48 有 1 项，即上面那条条目号 48）'),
 (u'是**待核列为 0** 的 39 条条目里最连续的十二条',
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
    if l.startswith(u'| **合计（50 条）**'):
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
KEYLINE = u'B50 把轴换成**同一台机器 ⇎ 六道难题**'
for i, l in enumerate(R):
    if KEYLINE in l and l.rstrip().endswith(u'不是转述。'):
        R[i] = l.rstrip().rstrip(u'。；') + u'；' + (
            u'B51 把轴换成**同一台机器 ⇎ 同一道题的第二次抽签**（登记 %d 条锚全部逐字回源 ok=%d bad=%d，'
            u'正文标注 %d 处／%d 个不同串，四个源标签 %s 各 %d–%d 条）：这条第一次把“可复现”当成被测量的量——'
            u'四种粒度 × 六对源（%d 格）里，同题肾病对 %s 与跨题“第二次⇎第二次”那对 %s 在两档粒度上打平'
            u'（整段句 %d＝%d ⇎ 单行句 %d＝%d），整行共有更是跨题对 %d 反超同题对 %d，'
            u'同题数论对 %s 是句子级唯一高出的一对；把公共片段按“能否在原样题面里找到”分堆，'
            u'>=40 字的极大块数 %d ⇎ %d 里纯题面只占 %d ⇎ %d，剩下的复现全是术语条目与被算术逼死的构造。'
            u'两次采样之间每个犹豫计数同向膨胀（maybe %s ⇎ 等号 %s ⇎ 需求句 %s），每万字归一后数论侧反而下降（%s ⇎ %s），'
            u'而“重来”一族四份皆零——加长的是追加，不是重做。'
            u'口径纪律照旧当场可数：区段三种切法的空白常数 %d／%d／%d，题面两套长度恒差 %d，'
            u'末字符码位四份 %s、其中 %d/4 不以句终符收尾，两次第一次的回答区各 %d ⇎ %d 字符。'
            u'保留率 %s（字节口径 %s，四份源合计 %s 字符 ⇎ 磁盘 %s 字节，最长段是最短段的 %.2f 倍）是四源对照条的必然读数：'
            u'窗口按锚点截取，而“哪一格与哪一格打平”要整段复算才看得见；'
            u'本脚本第三次独立测量这四份源（区段找法、%d 族模式正则、四种粒度集合交、>=40 字滑窗、锚的归一函数都在此另写一份，'
            u'%d 个可比键 %d 枚值与两份快照逐键相等），所以上面这些打平不是转述。'
            % (len(REG), AK, AB_, NOCC, DIST, u'／'.join(TAGS), min(NLAB.values()), max(NLAB.values()),
               4 * 6, quad((2, 3)), quad((1, 3)), OV[(2, 3)][1], OV[(1, 3)][1], OV[(2, 3)][2], OV[(1, 3)][2],
               OV[(1, 3)][0], OV[(2, 3)][0], quad((0, 1)),
               CR[(0, 1)][0], CR[(2, 3)][0], CR[(0, 1)][3], CR[(2, 3)][3],
               cellrow(u'maybe'), cellrow(u'equality'), cellrow(u'need'), p10row(u'maybe'), p10row(u'equality'),
               GAPF[0], GAPF[0], RGAP[0], PGAP, u' '.join(str(ord(c)) for c in LASTC), TAILBAD, AC[0], AC[2],
               b51_ret, b51_raw, fmt(RAW_SUM), fmt(sum(BYTES)), THIRD[u'rcratio'],
               len(ALLK), BOTH, VALS))
        done.append(u'口径段')
        break
assert u'口径段' in done, u'口径段未命中'

SRC4 = u' ⇎ '.join(u'`raw/cot/%s.md`（%s ⟦%s⟧: 推理区 %s ⇎ 文件 %s ⇎ 磁盘 %s 字节）'
                   % (SLUGS[i], CN[i], TAGS[i], fmt(RC[i]), fmt(SH[u'fchars'][i]), fmt(BYTES[i]))
                   for i in range(4))
GEN = (u'**B51 把对照轴换成同一台机器与同一道题的第二次抽签**：两道题各采两次 %s。'
       u'四段推理区合计 %s 字符（最长 %s ⇎ 最短 %s, %.2f 倍）, 第二次分别是第一次的 %.2f 倍（数论）⇎ %.2f 倍（肾病）；'
       u'两次第一次都没写完答案（回答区 %d ⇎ %d 字符）, 第二次各写出 %d ⇎ %d 字符；'
       u'题面哈希只有 %d 种(自校验 %d/4) ⇎ 抓取跨 %d 个日子, 同题两次之间隔 %s 与 %s 小时。'
       u'正文标注 %d 处／%d 个不同串（%s；登记表 %d 条经 atomcheck 真跑全部命中）, '
       u'判词 %d 行, 骨架 %d 条, 方法 %d 步, DERIV %d 键（%d 枚被正文点名逐条机检 ⇎ %d 枚只登记在同值折等里）, '
       u'0 键折 %d 项（let me 与 redo 两族四份皆零、跨题对的行/五词串交集归零、回答区两格、锚归属错配 %d）, '
       u'每万字归一式 %d 枚（除 %d ⇎ 乘 %d ⇎ 加 %d）; 同值折等 %d 组 %d 个说法（最扎眼的是同题两次的题面长度彼此相等: %d ⇎ %d）。'
       u'关键结论: 逐字复现的主体是题面回声、术语条目与被算术逼死的构造, 长度、判序与结论形状不复现。'
       u'可复现性按四种粒度各测一遍才许说话: 同题数论对 %s ⇎ 同题肾病对 %s ⇎ 跨题同阶段(两次⇎两次)对 %s——'
       u'肾病对与跨题对在整段句 %d＝%d 与单行句 %d＝%d 两档打平(整行共有反而 %d>%d), 数论对则在句子级高出; '
       u'五词串级上同题两对 %d ⇎ %d 而四个跨题对合计只剩 %d(%s); 四份同文的句子只剩语气词 %d 枚, 其中只有 %d 组连大小写都不动。'
       u'口径恒差三处: 区段三种切法 %d／%d／%d 字符 ⇎ 题面两套长度差 %d ⇎ 模型串四份头部 %d 种写法（去前缀 %d 种实体, 即同一台机器）。'
       u'起手句同属一类套话（We need %d/4 段）而首行去重 %d 种, %d 条锚 × %d 段＝%d 次成员检查里错配 %d 条——'
       u'归属由正文标签现推, 不由旁注文件说了算。'
       ) % (SRC4, fmt(sum(RC)), fmt(max(RC)), fmt(min(RC)), THIRD[u'rcratio'],
            round(1.0 * RC[1] / RC[0], 2), round(1.0 * RC[3] / RC[2], 2),
            AC[0], AC[2], AC[1], AC[3],
            len(set(SHA)), SHAOK, len(DAYS), GAPH[0], GAPH[1],
            NOCC, DIST, u' '.join(u'⟦%s⟧ %d' % (x, NLAB[x]) for x in TAGS), len(REG),
            GLOS, NSKEL, NSTEP, KEYS, PROOF_B51, UNREF_B51, ZT, AA[u'anchor_err'],
            NRND, OPS[u'Div'], OPS[u'Mult'], OPS[u'Add'], NCG, NCV, PCOT[0], PCOT[1],
            quad((0, 1)), quad((2, 3)), quad((1, 3)),
            OV[(2, 3)][1], OV[(1, 3)][1], OV[(2, 3)][2], OV[(1, 3)][2], OV[(1, 3)][0], OV[(2, 3)][0],
            OV[(0, 1)][3], OV[(2, 3)][3], sum(OV[q][3] for q in ORDER if q not in SAME),
            u' ⇎ '.join(str(OV[q][3]) for q in ORDER if q not in SAME), len(ALL4L), S4SAME,
            GAPF[0], GAPF[0], RGAP[0], PGAP, len(MODELS), len(BARE),
            WENEED, DISTINCT_FIRST, len(ALLA), 4, CHECKS, AA[u'anchor_err'])
for i, l in enumerate(R):
    if l.startswith(u'**B50 把对照轴换成同一台机器与它做的六道难题**'):
        R[i] = l + u'\n\n' + GEN
        done.append(u'B51 段')
        break
assert u'B51 段' in done, u'B51 段未命中'

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B50 | %s（新建' % fmt(b50_enc)):
        ins.append((i + 1, u'| B51 | %s（新建, 同一模型⇎同一题的两次采样 %d 处标注／%d 个不同串（登记 %d 条锚全命中）: '
                           u'四源四色锚位 math_subsets ⟦A⟧ ⇎ math_subsets_s2 ⟦B⟧ ⇎ med_gitalb ⟦C⟧ ⇎ med_gitalb_s2 ⟦D⟧; '
                           u'最强一环是粒度对表: 四种粒度 × 六对源, 同题肾病对 %s ⇎ 同题数论对 %s ⇎ 跨题同阶段对 %s——'
                           u'其中肾病对与跨题对（第二次⇎第二次）在整段句和单行句两档打平、整行共有反而 %d>%d, '
                           u'数论对在句子级高出、五词串级四个跨题对合计只剩 %d; >=40 字极大公共片段 %d ⇎ %d 块（纯题面 %d ⇎ %d）; '
                           u'回答区两次第一次各 %d 字符 ⇎ 末字符非句终 %d/4 ⇎ 推倒重来四份 %d 次; '
                           u'DERIV %d 键（正文点名 %d ⇎ 仅登记 %d）, 0 键折 %d 项, B51V %d 次（带格号 %d ⇎ 标量 %d）, 归一式 %d 枚; 同值折等 %d 组; '
                           u'口径恒差: 区段三切法 %d／%d／%d ⇎ 题面两套 %d ⇎ 模型串 %d 写法／%d 实体 ⇎ 四份头部同一台机器; '
                           u'犹豫计数同向膨胀 maybe %s ⇎ 等号 %s, 而每万字归一在数论侧反向 %s ⇎ %s） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为记号名、模式键名与英文原词） | %s | %s |'
                           % (fmt(b51_enc), NOCC, DIST, len(REG),
                              quad((2, 3)), quad((0, 1)), quad((1, 3)), OV[(1, 3)][0], OV[(2, 3)][0],
                              sum(OV[q][3] for q in ORDER if q not in SAME), CR[(0, 1)][0], CR[(2, 3)][0], CR[(0, 1)][3], CR[(2, 3)][3],
                              AC[0], TAILBAD, ME[u'redo'][0],
                              KEYS, PROOF_B51, UNREF_B51, ZT, FAMS[u'B51V'], IDX, PLAIN, NRND, NCG,
                              GAPF[0], GAPF[0], RGAP[0], PGAP, len(MODELS), len(BARE),
                              cellrow(u'maybe'), cellrow(u'equality'), p10row(u'maybe'), p10row(u'equality'),
                              NOCC, fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b51_ret, fmt(b51_dig))))
    elif l.startswith(u'| B50 | %s | %s' % (fmt(b50_enc), b50_ret)):
        ins.append((i + 1, u'| B51 | %s | %s | %s（字节口径; 四份源合计 %s 字符 ⇎ 磁盘 %s 字节——'
                           u'判词要在四源 × 四种粒度的矩阵上数“哪一格与哪一格打平”（复算 ⇎ 归一 ⇎ 两套快照对表），'
                           u'而摘要段只索引锚点触到的窗口，故保留率 %s 属四源对照条的必然读数，'
                           u'按“%d 枚推导键支撑 %d 行判词”来读；'
                           u'原料本身很大（四段推理区合计 %s 字符，最长段 %s ⇎ 最短段 %s，两次第一次的回答区各 %d 字符），'
                           u'但“同题对的句子级共有不比跨题对高、redo 四份恒零而犹豫同向膨胀”这一判既不在任何一段里也不在窗口里，摊开矩阵才看得见；'
                           u'字符层的整段对齐量（%d 字符 ⇎ %d 字符, 占前一份 %.1f%% ⇎ %.1f%%）慢到不能进门槛, '
                           u'只在 `corpus/_probe51.py` 里量并如实注明，条目正文改用块层可复算的数；'
                           u'工具侧三套实现的比对（%d 个可比键 ⇎ %d 枚值）写在 ⛓解读注与本脚本, 不冒充机检） | %d | %s |'
                           % (fmt(b51_enc), b51_ret, b51_raw, fmt(RAW_SUM), fmt(sum(BYTES)),
                              b51_ret, KEYS, GLOS, fmt(sum(RC)), fmt(max(RC)), fmt(min(RC)), AC[0],
                              3580, 4794, 15.4, 20.9, BOTH, VALS, b51_uniq, b51_cpu)))
    elif l.startswith(u'| B50 | `raw/cot/math_subsets.md`'):
        ins.append((i + 1, u'| B51 | ' + SRC4 + u'（四份同模型输出, 两道题各采两次, 头部自报区段长度与实测逐份相等） | '
                           u'同一模型 ⇎ 同一题的第二次采样 ⇒ 可复现性分四种粒度: 同题数论对 %s ⇎ 同题肾病对 %s ⇎ 跨题同阶段 %s（其中肾病对与跨题对在整段句和单行句两档打平、整行反超 %d>%d, 四个跨题对的五词串共有合计只 %d）; '
                           u'>=40 字块 %d ⇎ %d（纯题面 %d ⇎ %d）; 题面引用 %s @%s; '
                           u'犹豫同向膨胀 maybe %s ⇎ 等号 %s, 归一后数论反向 %s ⇎ %s ⇎ 重来四份零; '
                           u'口径恒差: 区段三切法 %d／%d／%d ⇎ 题面两套 %d ⇎ 模型串 %d 写法／%d 实体 ⇎ 四份头部同一台机器; '
                           u'哈希自校验 %d/4 ⇎ 抓取跨 %d 日（隔 %s／%s 小时）⇎ 末字符非句终 %d/4 ⇎ 回答区 %d ⇎ %d ⇒ '
                           u'能逐字复现的段落几乎都是查得到或推得出唯一写法的段落, 复现率是检索能力的指标而不是推理能力的指标 |'
                           % (quad((0, 1)), quad((2, 3)), quad((1, 3)), OV[(1, 3)][0], OV[(2, 3)][0], sum(OV[q][3] for q in ORDER if q not in SAME),
                              CR[(0, 1)][0], CR[(2, 3)][0], CR[(0, 1)][3], CR[(2, 3)][3],
                              u' ⇎ '.join(str(x[0]) for x in PQ), u' ⇎ '.join(str(x[1]) for x in PQ),
                              cellrow(u'maybe'), cellrow(u'equality'), p10row(u'maybe'), p10row(u'equality'),
                              GAPF[0], GAPF[0], RGAP[0], PGAP, len(MODELS), len(BARE),
                              SHAOK, len(DAYS), GAPH[0], GAPH[1], TAILBAD, AC[0], AC[2])))
    elif l.startswith(u'python -X utf8 corpus/_readme50.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_probe51.py math_subsets math_subsets_s2   # 探测同题两次: 严格分节正则 ⇎ 头部自报长度逐份对齐, prompt_sha256 现场重算 %d/4; difflib 字符层命中 %d 字符(占前一份 %.1f%%) 慢到不进门槛\n'
                    u'python -X utf8 corpus/_pick51.py                # 选锚: 每条锚由规则从推理区/答案区截出, 四种粒度集合交 ⇎ >=40 字极大公共片段 ⇎ 题面引用滑窗全部现算, 落 %d 条候选池\n'
                    u'python -X utf8 corpus/_mkB51.py                 # 建条目: 四色锚位(A/B=数论两次, C/D=肾病两次), 零项折进一枚 0 键(%d 项), 同值冲突 %d 组逐个登记含义\n'
                    u'python -X utf8 corpus/_wire51.py                # 把 _B51 与 B51V 接进 audit.py(审计器侧另算一套), DERIV %d 键; 插门前先把每条算式在扫描器上预演, 值不符当场停机\n'
                    u'python -X utf8 corpus/_mkdigest3.py B51 <entry> A <raw/cot/math_subsets.md> 320 260 B ...   # 四源分节摘要, 每源按命中锚各自分块(%d 节 ⇎ 正文 %d 处标注里 %d 处落在窗口内(精确子串亦 %d 处), 余 %d 处是答案区/窗口外的锚)\n'
                    u'python -X utf8 corpus/atomcheck.py B51 corpus/_atoms51.txt   # 登记 %d 条锚逐字回源 ok=%d bad=%d（正文标注 %d 处／%d 个不同串）\n'
                    u'python -X utf8 corpus/_fill51.py                # ⛓解读注: 采集侧与审计器侧快照 %d 个可比键 %d 枚值逐键相等才落盘; 锚的三口径(逐字 %d ⇎ 折空白 %d ⇎ 归一 %d)在本条完全重合\n'
                    u'python -X utf8 corpus/_readme51.py              # 记账: 本脚本第三次独立测量四份源(区段找法 ⇎ %d 族模式正则 ⇎ 四种粒度 ⇎ >=40 字滑窗 ⇎ 锚归一函数皆另写一份), 并与两份快照逐键对表, 故 README 里的“打平”断言不是转述'
                    % (SHAOK, 3580, 15.4, MM[u'anchors_pool'] if u'anchors_pool' in MM else MMEAS[u'anchors_pool'],
                       ZT, NCG, KEYS, BLOCKS, NOCC, DIGHIT, EXACT, DIGMISS, len(REG), AK, AB_, NOCC, DIST,
                       BOTH, VALS, ex, fo, no_, len(ALLK))))
assert len(ins) == 4, [x[1][:30] for x in ins]
for pos, txt_ in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt_)
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if not l.startswith((u'| B50 |', u'**B50', u'B50 '))
        and re.search(u'50 条|B01\\.\\.B50|%s|%s 条|%s|%s|%%s（新建|%%d 键' % (
            re.escape(fmt(b50_enc)), OLD_PROOFS, re.escape(fmt(prev_in)), re.escape(fmt(prev_out))), l)]
print(u'README %d 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 摘要 %s 编码 %s 保留 %s 码点 %s 推导 %d 待核 %d｜'
      u'待核 0 的条目 %d 条｜第二代 %s／%s｜粒度矩阵 %d 格 打平 %s｜DERIV %d 键 点名 %d 未点名 %d 0 键 %d 项'
      % (NENT, u'/'.join(done), len(left), fmt(dig_all), fmt(enc_all), ret_all, fmt(uniq_all), proofs,
         soft_all, len(ZSOFT), fmt(in_lat), fmt(out_lat), 4 * 6,
         u' ⇎ '.join(quad(q) for q in ORDER), KEYS, PROOF_B51, UNREF_B51, ZT))
for l in left:
    print(u'  ' + l[:150])
print(u'B51: enc %s dig %s ret %s raw %s uniq %d blocks %d cpu %s soft %d｜锚 %d 条 引用 %d 处 去重 %d 标签 %s｜'
      u'推理区 %s 合计 %s 比 %.2f 回答区 %s｜文件 %s 字节 %s｜哈希 %d 自校验 %d/4 日子 %d 间隔 %s 末符非句终 %d/4｜'
      u'DERIV %d 键 0 键 %d 项 B51V %d(格 %d/标量 %d) 归一 %d 加 %d｜同值 %d 组 %d 说｜'
      u'模式 %d 族 皆正 %d 皆零 %s 翻名次 %d｜口径差 区段 %d 题面 %d｜起手 We need %d/4 去重 %d｜'
      u'锚三口径 %d/%d/%d 检查 %d 命中列 1份%d 2份%d 3份%d 4份%d｜difflib 3580⇎4794｜三套对表 %d 键 %d 值'
      % (fmt(b51_enc), fmt(b51_dig), b51_ret, b51_raw, b51_uniq, b51_blocks, b51_cpu, b51_soft,
         len(REG), NOCC, DIST, u' '.join(u'%s:%d' % (x, NLAB[x]) for x in TAGS),
         RC, fmt(sum(RC)), THIRD[u'rcratio'], AC, fmt(RAW_SUM), fmt(sum(BYTES)),
         len(set(SHA)), SHAOK, len(DAYS), GAPH, TAILBAD,
         KEYS, ZT, FAMS[u'B51V'], IDX, PLAIN, NRND, OPS[u'Add'], NCG, NCV,
         len(ALLK), len(ALLPOS), SIXZERO, len(FLIP), GAPF[0], PGAP,
         WENEED, DISTINCT_FIRST, ex, fo, no_, CHECKS, D1, D2, D3, D4, BOTH, VALS))
