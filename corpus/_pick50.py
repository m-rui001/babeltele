# -*- coding: utf-8 -*-
"""B50 选锚 + 现算: 六份同模型思维链。
锚一律由正则从推理区截出(保证逐字), 再验“只命中自己的源”; 所有发布数字写进 _b50meas.json。
计数与 _probe50.py 的 19 条模式逐一回表(_f50stats.txt), 两份脚本不许各说一套。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = u'corpus'
SLUGS = [u'math_subsets', u'med_gitalb', u'law_ewca_method', u'fin_credit_cmte',
         u'ind_creep_rupture', u'str_quake_slab']
TAGS = [u'M', u'D', u'L', u'F', u'I', u'S']
PATH = [u'%s/raw/cot/%s.md' % (C, s) for s in SLUGS]
RD = lambda p: io.open(os.path.join(ROOT, p), encoding='utf-8').read()
NL = u'\n'

FULL = [RD(p) for p in PATH]
HDR = [dict(re.findall(u'^(model|slug|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$', T, re.M)) for T in FULL]
for i, s in enumerate(SLUGS):
    assert HDR[i][u'slug'] == s, HDR[i]

def region(i):
    """抓取器同款找法(## [[REASONING]] 之后到 ## [[ANSWER]] 之前), 再 strip 掉两侧空行。"""
    a = FULL[i].find(u'## [[REASONING]]')
    b = FULL[i].find(u'## [[ANSWER]]', a)
    return FULL[i][a + 17:b].strip()

def raw_region(i):
    a = FULL[i].find(u'## [[REASONING]]')
    b = FULL[i].find(u'## [[ANSWER]]', a)
    return FULL[i][a + 17:b]

def ans(i):
    b = FULL[i].find(u'## [[ANSWER]]')
    return FULL[i][b + 13:].strip()

R = [region(i) for i in range(6)]
RC = [len(R[i]) for i in range(6)]
RAW_R = [len(raw_region(i)) for i in range(6)]
assert RC == [int(HDR[i][u'reasoning_chars']) for i in range(6)], (RC, [HDR[i][u'reasoning_chars'] for i in range(6)])
AC = [len(ans(i)) for i in range(6)]
assert AC == [int(HDR[i][u'answer_chars']) for i in range(6)] == [0] * 6, AC
GAP = [RAW_R[i] - RC[i] for i in range(6)]
assert set(GAP) == set(GAP) and len(set(GAP)) == 1, GAP

# ---------- 19 条模式(与 _probe50.py 同一张表) ----------
PATS = {
    u'wait': r'(?i)\bWait\b',
    u'actually': r'(?i)\bactually\b',
    u'maybe': r'(?i)\bmaybe\b|\bperhaps\b',
    u'prob': r'(?i)\bprobably\b|\blikely\b',
    u'assume': r'(?i)\bassume[ds]?\b|\bassuming\b',
    u'unsure': r'(?i)\bnot sure\b|\bunclear\b|\bi (?:think|believe)\b',
    u'verif': r'(?i)\bcheck\b|\bverify\b|\bsanity\b|\bdouble[- ]check\b|\bconfirm\b',
    u'redo': r'(?i)\bredo\b|\bstart over\b|\blet me (?:recompute|recheck)\b',
    u'wrong': r'(?i)\bwrong\b|\bmistake\b|\berror\b|\boops\b',
    u'therefore': r'(?i)\btherefore\b|\bthus\b|\bhence\b|\bso\b',
    u'however': r'(?i)\bhowever\b|\bbut\b|\balthough\b|\bwhereas\b',
    u'must': r'(?i)\bmust\b',
    u'caveat': r'(?i)\bcaveat\b|\bcaution\b|\bcareful\b|\bbeware\b',
    u'final': r'(?i)\bfinal\b|\bconclusion\b|\banswer:|\brecommend',
    u'quote': r'"[^"]{10,60}"',
    u'equality': r'=',
    u'unit': r'(?i)\b(?:mm|MPa|kN|GPa|°C|kg|m|s|y|years|months|mm/yr|kW|Hz|Bq|Sv|Gy|%)\b',
    u'cfr': r'(?i)\b(?:article|section|§|clause|paragraph|paragraphs)\b',
    u'study': r'(?i)\bstudy\b|\bpaper\b|\bauthor',
}
EXTRA = {
    u'restart_word': r'(?i)\brestart(?:s|ed|ing)?\b',
    u'uncertain_word': r'(?i)\buncertain(?:ty|ly)?\b',
    u'bold': r'\*\*[^*]{2,60}\*\*',
    u'hmm': r'(?i)\bHmm\b',
    u'lets': r"(?i)\blet's\b",
    u'letme': r'(?i)\blet me\b',
    u'need': r'(?i)\bneed\b',
    u'q': r'\?',
    u'arrow': r'->',
}
CNT = lambda txt, p: len(re.findall(p, txt, re.I))
MEAS = {}
for k in sorted(PATS) + sorted(EXTRA):
    pat = (PATS.get(k) or EXTRA[k])
    MEAS[k] = [CNT(R[i], pat) for i in range(6)]
SHAPE = {
    u'rcot': RC,
    u'acot': AC,
    u'pcot': [len(FULL[i][FULL[i].find(u'## [[PROMPT]]') + 14:FULL[i].find(u'## [[REASONING]]')].strip()) for i in range(6)],
    u'fchars': [len(FULL[i]) for i in range(6)],
    u'fbytes': [os.path.getsize(os.path.join(ROOT, p)) for p in PATH],
    u'sent': [len(re.findall(r'[.!?](?:\s|$)', R[i])) for i in range(6)],
    u'para': [len([x for x in R[i].split(NL) if x.strip()]) for i in range(6)],
    u'numsent': [len([x for x in re.split(r'(?<=[.!?])\s+', R[i]) if re.search(r'\d', x)]) for i in range(6)],
    u'gap': GAP,
    u'taillen': [len([l for l in R[i].split(NL) if not l.strip()]) for i in range(6)],
}
# 与 _probe50 落盘的那份统计表逐行回表
ST = {}
for l in io.open(os.path.join(ROOT, C, u'_f50stats.txt'), encoding='utf-8').read().split(NL):
    if l.strip():
        k, v = l.split(u'\t')
        ST[k] = v.split(u' ')
for k in sorted(PATS):
    assert MEAS[k] == [int(x) for x in ST[k]], (k, MEAS[k], ST[k])
for k in (u'sent', u'para', u'numsent'):
    assert SHAPE[k] == [int(x) for x in ST[k]], (k, SHAPE[k], ST[k])
assert RC == [int(x) for x in ST[u'rcot']] and AC == [int(x) for x in ST[u'acot']]

# ---------- 截断: 六段末尾字符 ----------
LASTC = [R[i][-1] for i in range(6)]
assert all(c not in u'.!?"\u201d' for c in LASTC), LASTC
LASTW = [R[i].split()[-1] for i in range(6)]
assert len(LASTW) == 6
# ---------- 模型串 / 哈希 / 抓取时刻 ----------
MODELS = sorted(set(HDR[i][u'model'] for i in range(6)))
bare = [h[u'model'].split('/')[-1] for h in HDR]
assert len(set(bare)) == 1 and len(MODELS) == 2, (MODELS, set(bare))
SHA_OK = 0
for i in range(6):
    pf = FULL[i][FULL[i].find(u'## [[PROMPT]]') + 14:FULL[i].find(u'\n\n## [[REASONING]]')]
    if hashlib.sha256(pf.encode('utf-8')).hexdigest()[:16] == HDR[i][u'prompt_sha256']:
        SHA_OK += 1
assert SHA_OK == 6, SHA_OK
PFSTRIP = [len(FULL[i][FULL[i].find(u'## [[PROMPT]]') + 14:FULL[i].find(u'## [[REASONING]]')].strip()) for i in range(6)]
assert PFSTRIP == SHAPE[u'pcot']
PRAW = [len(FULL[i][FULL[i].find(u'## [[PROMPT]]') + 14:FULL[i].find(u'\n\n## [[REASONING]]')]) for i in range(6)]
PGAP = [PRAW[i] - PFSTRIP[i] for i in range(6)]
assert set(PGAP) == {1}, (PRAW, PFSTRIP, PGAP)
HASHES = sorted(set(HDR[i][u'prompt_sha256'] for i in range(6)))
assert len(HASHES) == 6, HASHES
RETR = [HDR[i][u'retrieved'] for i in range(6)]

# ---------- 每万字归一 + 名次翻转 ----------
P10 = dict((k, [round(10000.0 * MEAS[k][i] / RC[i], 1) for i in range(6)]) for k in MEAS)
def lead(v):
    m = max(v)
    return sorted([i for i in range(6) if v[i] == m])
FLIP = [k for k in sorted(PATS) if lead(MEAS[k]) != lead(P10[k])]
assert len(FLIP) == len(set(FLIP))
ALLPOS = [k for k in sorted(PATS) if min(MEAS[k]) >= 1]
ALLZERO = [k for k in sorted(PATS) if max(MEAS[k]) == 0]
SIXZERO = [k for k in sorted(PATS) if MEAS[k] == [0] * 6]
assert SIXZERO == [u'redo'], SIXZERO
CONST = [k for k in (u'wait', u'actually', u'probably_none') if k in ALLPOS]

# ---------- 选锚 ----------
A = []
def pick(tag, rx, note=u''):
    i = TAGS.index(tag)
    m = re.search(rx, R[i])
    if not m:
        A.append((tag, None, rx, note))
        return
    A.append((tag, m.group(0), rx, note))

def tail(tag, n=52):
    """末行截尾: 取最后一段非空行的末尾 n 字符(不含换行), 这是“思维链被切断”的直接字面证据。"""
    i = TAGS.index(tag)
    ll = [x for x in R[i].split(NL) if x.strip()][-1].rstrip()
    A.append((tag, ll[-n:], u'TAIL', u'末行末尾 %d 字符' % n))

pick(u'M', r"We need solve math problem\. Need rigorous, research style, small n, conjecture, proof, dead ends, key invariant\.")
pick(u'M', r"Wait ab/\(a\+b\) integer iff \(a\+b\)\|ab\.")
pick(u'M', r"Actually a\+b \| ab iff 1/a \+ 1/b = \(a\+b\)/ab is reciprocal integer\?")
pick(u'M', r"Try small n\.")
pick(u'M', r"No, not any\.")
pick(u'M', r"some special form\? Hmm\.")
pick(u'M', r"Thus all cliques are essentially scaled primitive sets\.")
pick(u'M', r"Let's compute\.")
tail(u'M')
pick(u'D', r"We need answer clinical reasoning\. Need be thorough\. Need reason as nephrologist\.")
pick(u'D', r"Wait, how does Gitelman cause hypocalciuria\? Need explain correctly\.")
pick(u'D', r"but urine Cl 104 eliminates\.")
pick(u'D', r"unless chloride diarrhea or laxative\? Hmm\.")
pick(u'D', r"thiazide is the only thing that exactly mimics Gitelman\.")
pick(u'D', r"Need enumerate every cause of hypokalemic metabolic alkalosis with normal-to-low BP\.")
pick(u'D', r"Actually classic Bartter III has variable phenotype")
tail(u'D')
pick(u'L', r"All tools disabled\. I must answer from reasoning\.")
pick(u'L', r"I don.t have it in my training data\.")
pick(u'L', r"Wait: If both are English law")
pick(u'L', r"Kookmin Bank v Rainy Sky\*\? No\.")
pick(u'L', r"Non-circular: Do not determine the applicable law by first characterising the issue under that law\.")
pick(u'L', r"Let me recall: The 2019 Hague Judgments Convention")
pick(u'L', r"distinction between the \*lex fori\* \(recognition\) and the \*lex loci protectionis\* \(ownership\)\.")
pick(u'L', r"held that the plea of issue estoppel was governed by \*\*English law\*\*")
tail(u'L')
pick(u'F', r"Websearch disabled\. Need rely knowledge\.")
pick(u'F', r"Could there be a \*\*unit error\*\*")
pick(u'F', r"The premise is wrong\.")
pick(u'F', r"12 CFR 32, a national bank.s loans to one borrower cannot exceed 15% of unimpaired capital and surplus")
pick(u'F', r"480/36 = 13\.3333\.")
pick(u'F', r"decisive, caveated, arithmetic\.")
pick(u'F', r"that would be wrong\. The binding constraints are prudential, not legal\.")
tail(u'F')
pick(u'I', r"We need answer complex forensic engineering\.")
pick(u'I', r"client asserts API 560 requires annual creep inspection, owner per se negligent\. False;")
pick(u'I', r"Wait 6 weeks plus 11 days\?")
pick(u'I', r"D = t1/L1 \+ t2/L2\.")
pick(u'I', r"Procedure revision 5 months earlier swapped two valve line-items in lighting checklist\.")
pick(u'I', r"Need no tools really\.")
pick(u'I', r"restart after 21-day turnaround\.")
pick(u'I', r"registers left wrong\.")
pick(u'I', r"not replaced -> loss of independent temperature indication")
tail(u'I')
pick(u'S', r"We need answer forensic structural engineering\. Need work, not clean conclusion\.")
pick(u'S', r"Residual storey drift 45 mm over 3\.6 m = 1\.25%\.")
pick(u'S', r"owner says diagonal cosmetic; we must rule\.")
pick(u'S', r'not rejected until verified')
pick(u'S', r"higher -> worse")
pick(u'S', r"This is a category error\.")
pick(u'S', r"The only alternative I cannot reject is punching shear; that is the point\.")
pick(u'S', r"Wait full bays, not partial\.")
pick(u'S', r"is wrong as a blanket")
tail(u'S')

def pnorm(s):
    s = s.lower().replace(u'\u2019', u"'").replace(u'\u2018', u"'").replace(u'\u201c', u'"').replace(u'\u201d', u'"')
    s = re.sub(u'[\u2019\'"\u2018`´]+', '', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', '-', s)
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff\-\. ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

PN = [pnorm(R[i]) for i in range(6)]
bad = [x for x in A if x[1] is None]
for t, s_, rx, nt in bad:
    print(u'MISS ⟦%s⟧ %s' % (t, rx))
dup = {}
cross = []
for t, s_, rx, nt in A:
    if s_ is None:
        continue
    n = pnorm(s_)
    hits = [i for i in range(6) if n in PN[i]]
    assert len(hits) == 1 and TAGS[hits[0]] == t, (t, s_[:40], hits)
    dup.setdefault(n, []).append(t)
ATOMS = [s_ for t, s_, rx, nt in A if s_ is not None]
MULTI = dict((k, v) for k, v in dup.items() if len(v) > 1)
print(u'锚: 候选 %d 命中 %d 互斥 %s 同串跨源 %d' % (len(A), len(ATOMS), len(ATOMS) == len(set(ATOMS)), len(MULTI)))
io.open(os.path.join(ROOT, C, u'_atoms50.txt'), 'w', encoding='utf-8', newline='\n').write(NL.join(ATOMS) + NL)

MEAS[u'models'] = len(MODELS)
MEAS[u'model_names'] = MODELS
MEAS[u'sha_ok'] = SHA_OK
MEAS[u'hashes'] = len(HASHES)
MEAS[u'lastc'] = LASTC
MEAS[u'lastw'] = LASTW
MEAS[u'flip'] = len(FLIP)
MEAS[u'flip_names'] = FLIP
MEAS[u'allpos'] = len(ALLPOS)
MEAS[u'allpos_names'] = ALLPOS
MEAS[u'sixzero'] = len(SIXZERO)
MEAS[u'sixzero_names'] = SIXZERO
MEAS[u'pcot'] = SHAPE[u'pcot']
MEAS[u'praw'] = PRAW
MEAS[u'pgap'] = PGAP[0]
MEAS[u'gap'] = GAP
MEAS[u'retr'] = len(set(RETR))
MEAS[u'retr_list'] = RETR
MEAS[u'per10k'] = P10
MEAS[u'shape'] = SHAPE
MEAS[u'cross'] = sum(1 for v in dup.values() if len(v) > 1)
MEAS[u'checks'] = len(ATOMS) * 6
for k in (u'rcot', u'acot', u'fchars', u'fbytes', u'sent', u'para', u'numsent', u'taillen'):
    MEAS[k] = SHAPE[k]
MEAS[u'model_bare'] = len(set(bare))
MEAS[u'tailbad'] = sum(1 for c in LASTC if c not in u'.!?"”')
MEAS[u'rcotsum'] = sum(RC)
MEAS[u'rcratio'] = round(1.0 * max(RC) / min(RC), 1)
MEAS[u'npats'] = len(PATS)
MEAS[u'nextra'] = len(EXTRA)
MEAS[u'nsrc'] = 6
MEAS[u'slugs'] = SLUGS
MEAS[u'tags'] = TAGS
MEAS[u'atomlist'] = dict((t, [x[1] for x in A if x[0] == t and x[1]]) for t in TAGS)
MEAS[u'anchors_per_tag'] = dict((t, len([x for x in A if x[0] == t and x[1]])) for t in TAGS)
MEAS[u'anchor_total'] = len(ATOMS)
MEAS[u'anchor_distinct'] = len(set(ATOMS))
json.dump(MEAS, io.open(os.path.join(ROOT, C, u'_b50meas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(u'翻转模式 %d: %s' % (len(FLIP), FLIP))
print(u'六源皆有 %s ｜ 六源皆空 %s' % (ALLPOS, SIXZERO))
print(u'redo %s ｜ restart_word %s ｜ uncertain_word %s' % (MEAS[u'redo'], MEAS[u'restart_word'], MEAS[u'uncertain_word']))
print(u'bold %s ｜ lets %s ｜ letme %s ｜ arrow %s' % (MEAS[u'bold'], MEAS[u'lets'], MEAS[u'letme'], MEAS[u'arrow']))
print(u'lastc %s' % LASTC)
print(u'每行末词 %s' % LASTW)
