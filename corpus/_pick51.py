# -*- coding: utf-8 -*-
"""B51 选锚 + 现算: 同一模型、同一道题的两次采样(A⇎B 数论, C⇎D 肾病)。
锚不手抄: 全部由本脚本从推理区按规则切出(句子级, 空白折叠后逐字), 所以“逐字命中”是构造出来的;
再对四个源逐一算命中列, 按“题面对 ⇎ 单源 ⇎ 跨题 ⇎ 四源皆有”分档。
字符层的对齐量(difflib)只由 _probe51.py 侧量, 本脚本只做集合运算(秒级), 便于接进 audit 的扫描。
所有发布数字写进 _b51meas.json。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = u'corpus'
SLUGS = [u'math_subsets', u'math_subsets_s2', u'med_gitalb', u'med_gitalb_s2']
TAGS = [u'A', u'B', u'C', u'D']          # A⇎B 同一道数论题, C⇎D 同一道肾病题
PATH = [u'%s/raw/cot/%s.md' % (C, s) for s in SLUGS]
RD = lambda p: io.open(os.path.join(ROOT, p), encoding='utf-8').read()
NL = u'\n'
PAIRS = [(0, 1), (2, 3)]                 # 同题对
OFFS = [(0, 2), (0, 3), (1, 2), (1, 3)]  # 跨题对

FULL = [RD(p) for p in PATH]
HDR = [dict(re.findall(u'^(model|slug|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$', T, re.M))
       for T in FULL]
for i, s in enumerate(SLUGS):
    assert HDR[i][u'slug'] == s, HDR[i]

# ---------- 区段找法(两种口径, 与 B50 同一套纪律) ----------
def region(i):
    """采集侧同款: ## [[REASONING]] 之后 17 字符起, 到 ## [[ANSWER]] 之前, 再去两侧空白。"""
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

SECRX = (u'## \\[\\[PROMPT\\]\\]\\n(.*?)\\n\\n## \\[\\[REASONING\\]\\]\\n(.*?)'
         u'\\n\\n## \\[\\[ANSWER\\]\\]\\n?(.*)$')
SEC = [re.search(SECRX, T, re.S) for T in FULL]
assert all(SEC), u'严格分节正则未命中'

R = [region(i) for i in range(4)]
RC = [len(R[i]) for i in range(4)]
AC = [len(ans(i)) for i in range(4)]
RAW_R = [len(raw_region(i)) for i in range(4)]
GAP = [RAW_R[i] - RC[i] for i in range(4)]
assert RC == [int(HDR[i][u'reasoning_chars']) for i in range(4)], (RC, [HDR[i][u'reasoning_chars'] for i in range(4)])
assert AC == [int(HDR[i][u'answer_chars']) for i in range(4)]
assert len(set(GAP)) == 1 and GAP[0] == 2, GAP     # a+17 只少吃一枚前导换行; 尾部 strip 掉两枚空白
RGAP = [len(SEC[i].group(2)) - RC[i] for i in range(4)]
assert len(set(RGAP)) == 1, RGAP                    # 严格正则段与 strip 段的固定差(见打印)

PF = [SEC[i].group(1) for i in range(4)]
PC = [len(PF[i].strip()) for i in range(4)]
PGAP = [len(PF[i]) - PC[i] for i in range(4)]
assert set(PGAP) == {1}, PGAP
SHA = [hashlib.sha256(PF[i].encode('utf-8')).hexdigest()[:16] for i in range(4)]
assert SHA == [HDR[i][u'prompt_sha256'] for i in range(4)], SHA
assert SHA[0] == SHA[1] and SHA[2] == SHA[3] and SHA[0] != SHA[2], SHA
NHASH = len(set(SHA))                              # 四份文件只有两道题

# ---------- 句子/行/串 集合 ----------
def lines(x):
    return [l.strip() for l in x.split(NL) if l.strip()]

def sents(x):
    return [s.strip() for s in re.split(u'(?<=[.!?])\\s+', x) if s.strip()]

def lsents(x):
    """逐行再分句: 锚必须是单行片段, 跨行的“句子”在原文里被换行切断, 不能整体逐字命中。"""
    o = []
    for l in lines(x):
        o += [s.strip() for s in re.split(u'(?<=[.!?])\\s+', l) if s.strip()]
    return o

def shingles(x, n=5):
    w = re.findall(u'[a-z0-9]+', x.lower())
    return set(tuple(w[i:i + n]) for i in range(len(w) - n + 1))

def pnorm(s):
    s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
    s = re.sub(u'[’\'"‘`´]+', u'', s)
    s = re.sub(u'[‐-―−-]', u'-', s)
    s = re.sub(r'[^0-9a-z一-鿿\-\. ]+', u' ', s)
    return re.sub(r'\s+', u' ', s).strip()

PN = [pnorm(R[i]) for i in range(4)]
LN = [set(pnorm(x) for x in lines(R[i])) for i in range(4)]
SN = [set(pnorm(x) for x in sents(R[i])) for i in range(4)]
SG = [shingles(R[i]) for i in range(4)]
LRAW = [lines(R[i]) for i in range(4)]
SRAW = [sents(R[i]) for i in range(4)]

LS = [set(pnorm(x) for x in lsents(R[i])) for i in range(4)]
LSRAW = [lsents(R[i]) for i in range(4)]

def pair_stats(i, j):
    return (len(LN[i] & LN[j]), len(SN[i] & SN[j]), len(LS[i] & LS[j]), len(SG[i] & SG[j]))

PS = dict(((i, j), pair_stats(i, j)) for (i, j) in PAIRS + OFFS)

# ---------- 词法模式(与 B50/_probe50 同名同义, 少掉领域专属三条) ----------
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
    u'equality': u'=',
    u'arrow': u'->',
    u'letme': u'(?i)\\blet me\\b',
    u'lets': u"(?i)\\blet's\\b",
    u'hmm': u'(?i)\\bHmm\\b',
    u'need': u'(?i)\\bneed\\b',
    u'q': u'\\?',
    u'bold': u'\\*\\*[^*]{2,60}\\*\\*',
}
CNT = lambda txt, p: len(re.findall(p, txt))
MEAS = dict((k, [CNT(R[i], PATS[k]) for i in range(4)]) for k in sorted(PATS))
SHAPE = {
    u'rcot': RC, u'acot': AC, u'pcot': PC, u'praw': [len(PF[i]) for i in range(4)],
    u'fchars': [len(FULL[i]) for i in range(4)],
    u'fbytes': [os.path.getsize(os.path.join(ROOT, p)) for p in PATH],
    u'sent': [len(SRAW[i]) for i in range(4)],
    u'lsent': [len(LSRAW[i]) for i in range(4)],
    u'usent': [len(LS[i]) for i in range(4)],
    u'shang': [len(SG[i]) for i in range(4)],
    u'para': [len(LRAW[i]) for i in range(4)],
    u'numsent': [len([x for x in SRAW[i] if re.search(u'\\d', x)]) for i in range(4)],
    u'gap': GAP, u'pgap': PGAP, u'rgap': RGAP,
    u'lastc': [R[i][-1] for i in range(4)],
    u'lastw': [R[i].split()[-1] for i in range(4)],
    u'digit': [len(re.findall(u'\\d', R[i])) for i in range(4)],
    u'word': [len(re.findall(u'[A-Za-z]+', R[i])) for i in range(4)],
}

# ---------- 题面引用: 每份推理里原样出现的题面片段 ----------
def prompt_quote(i, minlen=40):
    """在推理区里找“能同时在题面里原样找到”的最长连续片段(滑窗+跳跃, 秒级)。"""
    pf, rf = PF[i].strip(), R[i]
    best = (0, 0, u'')
    k = minlen
    s = 0
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

PQ = [prompt_quote(i) for i in range(4)]

def common_runs(a, b, k=40, cap=400):
    """两段推理之间所有 >=k 字符的连续公共片段(滑窗 + 极大化延伸)。
    比 difflib 的整段对齐快几个数量级, 且给出的是同一种对象: 逐字复现的极大块。"""
    idx = {}
    for s in range(len(a) - k + 1):
        idx.setdefault(a[s:s + k], s)
    out, s = [], 0
    while s < len(b) - k + 1:
        p = idx.get(b[s:s + k])
        if p is None:
            s += 1
            continue
        e = s + k
        while e - s < cap and b[e:e + 1] and a[p + (e - s):p + (e - s) + 1] == b[e:e + 1]:
            e += 1
        out.append((e - s, b[s:e]))
        s = e
    return sorted(out, key=lambda x: -x[0])

CR = {p: common_runs(R[p[0]], R[p[1]]) for p in PAIRS}

# ---------- 候选锚池(按规则切, 不手抄) ----------
def hits_of(s):
    n = pnorm(s)
    return tuple(i for i in range(4) if n in PN[i])

def class_of(h):
    if len(h) == 4:
        return u'all4'
    if len(h) == 2:
        return u'pair' if tuple(h) in PAIRS else u'cross'
    return u'single'

CAND = []
FILEN = [pnorm(FULL[i]) for i in range(4)]     # 答案区的锚在推理区之外, 命中列要按整份文件算
def add(kind, i, s, scope=None, tag_own=None, nmin=24):
    s = s.strip()
    if len(s) < nmin or s.count(NL):
        return
    h = hits_of(s) if scope is None else tuple(k for k in range(4) if pnorm(s) in scope[k])
    if not h:
        return
    CAND.append((kind, TAGS[i], s, u''.join(TAGS[k] for k in h), class_of(h), len(s)))

ALLSH = set(SN[0]) & set(SN[1]) & set(SN[2]) & set(SN[3])
ALLSH_L = set(LS[0]) & set(LS[1]) & set(LS[2]) & set(LS[3])
# 1) 同题对里共有且较长的单行句 ⇒ “逐字复现”的证据
for (i, j) in PAIRS:
    for s in sorted(set(LSRAW[i]) & set(LSRAW[j]), key=len, reverse=True)[:12]:
        add(u'shared_sent', i, s)
    for s in sorted(set(LRAW[i]) & set(LRAW[j]), key=len, reverse=True)[:6]:
        add(u'shared_line', i, s)
# 1b) 四源皆有的句子 ⇒ 与题无关的脚手架(换了题照样出现)
for s in sorted(set(x for x in LSRAW[0] if pnorm(x) in ALLSH), key=len, reverse=True)[:8]:
    add(u'scaffold', 0, s)
# 1b2) 四源同文“句子”的原形: 短到语气词也要锚住, 并核对四份的表面写法是否同一串
S4 = {}
for i in range(4):
    for x in LSRAW[i]:
        if pnorm(x) in ALLSH_L:
            S4.setdefault(pnorm(x), []).append(x)
MEAS4 = dict((k, v) for k, v in S4.items())
for n, v in sorted(S4.items(), key=lambda kv: len(kv[1][0])):
    add(u'scaffold4', 0, v[0], nmin=2)
# 1c) 同角色跨题共有(第一次⇎第一次 / 第二次⇎第二次) ⇒ 同阶段套话
for (i, j) in ((0, 2), (1, 3)):
    for s in sorted(set(LSRAW[i]) & set(LSRAW[j]), key=len, reverse=True)[:5]:
        add(u'cross_sent', i, s)
# 2) 只在自己的源里出现、且含数字的句子 ⇒ “必须重推”的证据
for i in range(4):
    uniq = [s for s in LSRAW[i] if hits_of(s) == (i,) and re.search(u'\\d', s) and len(s) > 40]
    for s in sorted(uniq, key=len, reverse=True)[:12]:
        add(u'digit_only', i, s)
# 3) 只在自己的源里出现、带犹豫/推翻词的句子
HEIDX = u'\\bwrong\\b|\\bmistake\\b|\\berror\\b|\\boops\\b|\\bredo\\b|\\bstart over\\b|\\bWait\\b'
for i in range(4):
    uniq = [s for s in LSRAW[i] if hits_of(s) == (i,)
            and re.search(HEIDX, s, re.I) and len(s) > 40]
    for s in sorted(uniq, key=len, reverse=True)[:8]:
        add(u'hedge_only', i, s)
# 4) 题面引用的最长片段
for i in range(4):
    if PQ[i][0]:
        add(u'prompt_quote', i, PQ[i][2])
# 4b) 同题两次之间 >=40 字符的极大公共片段(逐字复现的实体)
SUB = {}
for (i, j) in PAIRS:
    rs = CR[(i, j)]
    SUB[(i, j)] = (len(rs), sum(x[0] for x in rs), rs[0][0] if rs else 0,
                   sum(1 for x in rs if x[1].strip(u'"“’\' \n\t.,;:!?') in PF[i].strip()))
    for (ln, txt) in rs[:10]:
        add(u'pair_sub', i, txt)
# 5) 末行截尾 + 开场句(两次采样的第一句)
for i in range(4):
    add(u'tail', i, LRAW[i][-1].rstrip()[-52:])
    add(u'opening', i, LSRAW[i][0])
# 6) 答案区判词(只有第二次采样走到了答案区, 命中列按整份文件算)
for i in (1, 3):
    for s in sorted([x for x in lsents(ans(i)) if len(x) > 48], key=len, reverse=True)[:8]:
        add(u'answer_judge', i, s, scope=FILEN)

seen = set()
POOL = []
for c in CAND:
    if c[2] in seen:
        continue
    seen.add(c[2])
    POOL.append(c)

out = []
for n, (kind, tg, s, hs, cl, ln) in enumerate(POOL):
    out.append(u'%3d %-13s ⟦%s⟧ [%s:%s] %d %s' % (n, kind, tg, hs, cl, ln, s[:100].replace(NL, u' ⏎ ')))
io.open(os.path.join(ROOT, C, u'_pool51.txt'), 'w', encoding='utf-8', newline='\n').write(NL.join(out) + NL)

MEAS[u'anchors_pool'] = len(POOL)
# ---------- 身份/口径标量(建条目时直接引用, audit 侧由 _b51_scan 复算) ----------
MEAS[u'sha_kinds'] = NHASH
MEAS[u'sha_ok'] = sum(1 for i in range(4) if hashlib.sha256(PF[i].encode('utf-8')).hexdigest()[:16] == HDR[i][u'prompt_sha256'])
FULLM = sorted(set(HDR[i][u'model'] for i in range(4)))
BARE = sorted(set(HDR[i][u'model'].split('/')[-1] for i in range(4)))
MEAS[u'models'] = len(FULLM)
MEAS[u'model_names'] = FULLM
MEAS[u'model_bare'] = len(BARE)
MEAS[u'model_bare_names'] = BARE
RETR = [HDR[i][u'retrieved'] for i in range(4)]
MEAS[u'retr'] = len(set(x[:10] for x in RETR))
MEAS[u'retr_list'] = RETR
MEAS[u'tailbad'] = sum(1 for c in SHAPE[u'lastc'] if c not in u'.!?"”')
MEAS[u'rcotsum'] = sum(RC)
MEAS[u'rcratio'] = round(1.0 * max(RC) / min(RC), 2)
MEAS[u'sent_all4'] = len(ALLSH)
MEAS[u'lsent_all4'] = len(ALLSH_L)
MEAS[u's4_same'] = sum(1 for v in S4.values() if len(set(v)) == 1)
MEAS[u's4_surfaces'] = dict((k, sorted(set(v))) for k, v in S4.items())
MEAS[u'sub'] = dict(('%s%s' % (TAGS[i], TAGS[j]), SUB[(i, j)]) for (i, j) in SUB)
json.dump(dict(meas=MEAS, shape=SHAPE, sha=SHA, slugs=SLUGS, tags=TAGS,
               pairs=dict(('%d%d' % p, PS[p]) for p in PS),
               prompt_quote=[(PQ[i][0], PQ[i][1]) for i in range(4)],
               pool=[(k, t, s, h, c, l) for (k, t, s, h, c, l) in POOL]),
          io.open(os.path.join(ROOT, C, u'_b51meas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print(u'四源: %s' % u' ⇎ '.join(u'%s %d 字/%d 句/%d 行/回答 %d' % (
    TAGS[i], RC[i], SHAPE[u'sent'][i], SHAPE[u'para'][i], AC[i]) for i in range(4)))
print(u'口径差: 采集侧 gap %s ⇎ 严格正则 rgap %s ⇎ 题面 pgap %s' % (GAP[0], RGAP[0], PGAP[0]))
print(u'题面 sha: %s (四份文件 %d 道题)' % (u' ⇎ '.join(x[:8] for x in SHA), NHASH))
print(u'时刻: %s' % u' ⇎ '.join(HDR[i][u'retrieved'] for i in range(4)))
print(u'共有(行/句/单行句/五词串): 同题 A⇎B %s ‖ C⇎D %s' % (PS[(0, 1)], PS[(2, 3)]))
for p in OFFS:
    print(u'  跨题 %s⇎%s %s' % (TAGS[p[0]], TAGS[p[1]], PS[p]))
print(u'公共片段(>=40 字): A⇎B 块数 %d 共 %d 字 最长 %d 字 其中纯题面 %d 块 ‖ C⇎D 块数 %d 共 %d 字 最长 %d 字 其中纯题面 %d 块' % (
    SUB[(0, 1)][0], SUB[(0, 1)][1], SUB[(0, 1)][2], SUB[(0, 1)][3],
    SUB[(2, 3)][0], SUB[(2, 3)][1], SUB[(2, 3)][2], SUB[(2, 3)][3]))
print(u'题面引用最长片段: %s' % u' ⇎ '.join(u'%s %d 字@%d' % (TAGS[i], PQ[i][0], PQ[i][1]) for i in range(4)))
print(u'末字符 %s ｜ 末词 %s' % (SHAPE[u'lastc'], SHAPE[u'lastw']))
for k in sorted(PATS):
    print(u'  %-11s %s' % (k, MEAS[k]))
print(u'候选锚池 %d 条 → corpus/_pool51.txt' % len(POOL))
print(u'四源同文句子: 整段句 %d ｜ 单行句 %d ｜ 模型串 %d 种(去前缀 %d: %s) ｜ 抓取日 %d ｜ 末字符非句终 %d' % (
    len(ALLSH), len(ALLSH_L), len(FULLM), len(BARE), BARE, MEAS[u'retr'], MEAS[u'tailbad']))
print(u'推理区合计 %d 字符 ｜ 最长⇎最短 %s 倍' % (MEAS[u'rcotsum'], MEAS[u'rcratio']))
print(u'四源同文原形(同一串的组数 %d): %s' % (MEAS[u's4_same'], MEAS[u's4_surfaces']))
