# -*- coding: utf-8 -*-
"""把 B51 的独立复算器(_b51_scan / B51V)接进 audit.py, 并留出 DERIV['B51'] 的生成块位。
幂等: 重复运行先摘旧块再插新块。
_b51_scan 与采集侧 corpus/_pick51.py、建条目侧 corpus/_mkB51.py 各写一遍同一套算法
(区段三口径、四种粒度集合交、>=40 字极大公共片段、题面引用滑窗、锚归属由正文现推), 两边不符就证明失败。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()

BLK = r'''
# B51: 同一模型 ⇎ 同一道题的两次采样(数论一对 ⇎ 肾病一对)。四份 raw 的区段口径、四种粒度的逐字复现量、
# >=40 字极大公共片段、题面回声的长度与起点、二十二族词法计数、末字符码位, 以及正文锚的归属,
# 全部由本函数从四份 raw 与条目正文独立复算; 采集侧 corpus/_pick51.py 与建条目侧 corpus/_mkB51.py 各写一遍,
# 三边不符就证明失败。
def _b51_scan():
    import hashlib as _hl
    P4 = SRC['B51']
    N = len(P4)
    F = [open(P4[i], encoding='utf-8', errors='replace').read() for i in range(N)]
    H = [dict(re.findall(u'^(model|slug|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$', F[i], re.M))
         for i in range(N)]
    NL = chr(10)
    TG = [u'A', u'B', u'C', u'D']
    SAME = [(0, 1), (2, 3)]
    ORDER = [(0, 1), (2, 3), (0, 2), (0, 3), (1, 2), (1, 3)]

    def cut(i, head, off, nxt):
        a = F[i].find(head)
        b = -1 if nxt is None else F[i].find(nxt, a)
        return F[i][a + off:] if b < 0 else F[i][a + off:b]

    RR = [cut(i, u'## [[REASONING]]', 17, u'## [[ANSWER]]') for i in range(N)]
    R = [x.strip() for x in RR]
    AAll = [cut(i, u'## [[ANSWER]]', 13, None).strip() for i in range(N)]
    RX = re.compile(u'## \\[\\[PROMPT\\]\\]\\n(.*?)\\n\\n## \\[\\[REASONING\\]\\]\\n(.*?)'
                    u'\\n\\n## \\[\\[ANSWER\\]\\]\\n?(.*)$', re.S)
    SEC = [RX.search(F[i]) for i in range(N)]
    assert all(SEC), u'B51: 严格分节正则未命中'
    PF = [SEC[i].group(1) for i in range(N)]
    SHAOK = 0
    for i in range(N):
        assert len(R[i]) == int(H[i][u'reasoning_chars']), i
        assert len(AAll[i]) == int(H[i][u'answer_chars']), i
        SHAOK += _hl.sha256(PF[i].encode('utf-8')).hexdigest()[:16] == H[i][u'prompt_sha256']
    assert SHAOK == N, SHAOK

    def lines(x):
        return [l.strip() for l in x.split(NL) if l.strip()]

    def sents(x):
        return [s.strip() for s in re.split(u'(?<=[.!?])' + chr(92) + u's+', x) if s.strip()]

    def lsents(x):
        o = []
        for l in lines(x):
            o += [s.strip() for s in re.split(u'(?<=[.!?])' + chr(92) + u's+', l) if s.strip()]
        return o

    def shingles(x, n=5):
        w = re.findall(u'[a-z0-9]+', x.lower())
        return set(tuple(w[i:i + n]) for i in range(len(w) - n + 1))

    def pn(s):
        s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
        s = re.sub(u'[’\'"\u2018\u2019`´]+', u'', s)
        s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
        s = re.sub(u'[^0-9a-z\u4e00-\u9fff. -]', u' ', s)
        return re.sub(u'\\s+', u' ', s).strip()

    FN = [pn(F[i]) for i in range(N)]
    PN = [pn(R[i]) for i in range(N)]
    LN = [set(pn(x) for x in lines(R[i])) for i in range(N)]
    SN = [set(pn(x) for x in sents(R[i])) for i in range(N)]
    LSN = [set(pn(x) for x in lsents(R[i])) for i in range(N)]
    SG = [shingles(R[i]) for i in range(N)]
    d = {}
    d['rcot'] = [len(R[i]) for i in range(N)]
    d['acot'] = [len(AAll[i]) for i in range(N)]
    d['gap'] = [len(RR[i]) - len(R[i]) for i in range(N)]
    d['pcot'] = [len(PF[i].strip()) for i in range(N)]
    d['praw'] = [len(PF[i]) for i in range(N)]
    d['pgap'] = [len(PF[i]) - len(PF[i].strip()) for i in range(N)]
    d['rgap'] = [len(SEC[i].group(2)) - len(R[i]) for i in range(N)]
    assert len(set(d['gap'])) == 1 and d['gap'][0] == 2, d
    assert len(set(d['pgap'])) == 1 and len(set(d['rgap'])) == 1, d
    d['fchars'] = [len(F[i]) for i in range(N)]
    d['fbytes'] = [os.path.getsize(P4[i]) for i in range(N)]
    d['para'] = [len(lines(R[i])) for i in range(N)]
    d['sent'] = [len(sents(R[i])) for i in range(N)]
    d['lsent'] = [len(lsents(R[i])) for i in range(N)]
    d['usent'] = [len(LSN[i]) for i in range(N)]
    d['shang'] = [len(SG[i]) for i in range(N)]
    d['numsent'] = [len([x for x in sents(R[i]) if re.search(u'\\d', x)]) for i in range(N)]
    d['digit'] = [len(re.findall(u'\\d', R[i])) for i in range(N)]
    d['word'] = [len(re.findall(u'[A-Za-z]+', R[i])) for i in range(N)]
    d['lastcode'] = [ord(R[i][-1]) for i in range(N)]
    d['nsrc'] = N
    d['sha_ok'] = SHAOK
    d['rcotsum'] = sum(d['rcot'])
    d['rcratio'] = round(1.0 * max(d['rcot']) / min(d['rcot']), 2)
    d['models'] = len(set(H[i][u'model'] for i in range(N)))
    d['model_bare'] = len(set(H[i][u'model'].split('/')[-1] for i in range(N)))
    d['sha_kinds'] = len(set(H[i][u'prompt_sha256'] for i in range(N)))
    d['retr'] = len(set(H[i][u'retrieved'][:10] for i in range(N)))
    d['tailbad'] = len([1 for i in range(N) if R[i][-1] not in u'.!?"'])

    PATS = {
        'wait': r'(?i)\bWait\b',
        'actually': r'(?i)\bactually\b',
        'maybe': r'(?i)\bmaybe\b|\bperhaps\b',
        'prob': r'(?i)\bprobably\b|\blikely\b',
        'assume': r'(?i)\bassume[ds]?\b|\bassuming\b',
        'unsure': r'(?i)\bnot sure\b|\bunclear\b|\bi (?:think|believe)\b',
        'verif': r'(?i)\bcheck\b|\bverify\b|\bsanity\b|\bdouble[- ]check\b|\bconfirm\b',
        'redo': r'(?i)\bredo\b|\bstart over\b|\blet me (?:recompute|recheck)\b',
        'wrong': r'(?i)\bwrong\b|\bmistake\b|\berror\b|\boops\b',
        'therefore': r'(?i)\btherefore\b|\bthus\b|\bhence\b|\bso\b',
        'however': r'(?i)\bhowever\b|\bbut\b|\balthough\b|\bwhereas\b',
        'must': r'(?i)\bmust\b',
        'caveat': r'(?i)\bcaveat\b|\bcaution\b|\bcareful\b|\bbeware\b',
        'final': r'(?i)\bfinal\b|\bconclusion\b|\banswer:|\brecommend',
        'equality': '=',
        'arrow': '->',
        'letme': r'(?i)\blet me\b',
        'lets': r"(?i)\blet's\b",
        'hmm': r'(?i)\bHmm\b',
        'need': r'(?i)\bneed\b',
        'q': r'\?',
        'bold': r'\*\*[^*]{2,60}\*\*',
    }
    for k, p in PATS.items():
        d[k] = [len(re.findall(p, R[i])) for i in range(N)]
    d['npats'] = len(PATS)
    d['allzero'] = len([k for k in sorted(PATS) if max(d[k]) == 0])

    # 四种粒度的集合交: 行 ⇎ 整段句 ⇎ 单行句 ⇎ 五词串, 六对全测
    OV = {'ov_l': [], 'ov_s': [], 'ov_ls': [], 'ov_sg': []}
    for (i, j) in ORDER:
        OV['ov_l'].append(len(LN[i] & LN[j]))
        OV['ov_s'].append(len(SN[i] & SN[j]))
        OV['ov_ls'].append(len(LSN[i] & LSN[j]))
        OV['ov_sg'].append(len(SG[i] & SG[j]))
    d.update(OV)
    d['sent_all4'] = len(SN[0] & SN[1] & SN[2] & SN[3])
    d['lsent_all4'] = len(LSN[0] & LSN[1] & LSN[2] & LSN[3])
    S4 = {}
    for i in range(N):
        for x in lsents(R[i]):
            if pn(x) in (LSN[0] & LSN[1] & LSN[2] & LSN[3]):
                S4.setdefault(pn(x), set()).add(x)
    d['s4_same'] = len([v for v in S4.values() if len(v) == 1])

    def prompt_quote(i, minlen=40):
        pf, rf = PF[i].strip(), R[i]
        best = (0, 0, u'')
        k, s = minlen, 0
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

    PQ = [prompt_quote(i) for i in range(N)]
    d['pq'] = [PQ[i][0] for i in range(N)]
    d['pqpos'] = [PQ[i][1] for i in range(N)]

    def common_runs(a, b, k=40, cap=400):
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

    CR = [common_runs(R[i], R[j]) for (i, j) in SAME]
    d['sub_n'] = [len(CR[p]) for p in range(len(SAME))]
    d['sub_tot'] = [sum(x[0] for x in CR[p]) for p in range(len(SAME))]
    d['sub_max'] = [CR[p][0][0] if CR[p] else 0 for p in range(len(SAME))]
    d['sub_prompt'] = [len([x for x in CR[p]
                            if x[1].strip(u'"“’\' \n\t.,;:!?') in PF[SAME[p][0]].strip()])
                       for p in range(len(SAME))]

    # 锚归属: 不读旁注文件, 直接从条目正文的“源标签紧接原子引文”配对现推
    ep = glob.glob(u'corpus/babeltele/B51_*.md')
    assert len(ep) == 1, ep
    T = open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + chr(10) + u'(.*?)' + chr(10) + chr(10) + u'## ', T, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TG) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B51: 正文里没有带标签的锚'

    def hitset(a):
        n = pn(a)
        return tuple(i for i in range(N) if n in FN[i])

    def cls(h):
        if len(h) == N:
            return u'all4'
        if len(h) == 2:
            return u'pair' if tuple(h) in SAME else u'cross'
        return u'single'

    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [hitset(a) for a in DIS]
    d['anchor_total'] = len(CITES)
    d['anchor_distinct'] = len(DIS)
    d['anchor_err'] = len([h for h in HC if not h])
    for c in (u'pair', u'cross', u'single', u'all4'):
        d['anchor_' + c] = len([h for h in HC if cls(h) == c])
    d['checks'] = len(DIS) * N
    assert sum(d['anchor_' + c] for c in (u'pair', u'cross', u'single', u'all4')) == len(DIS)
    return d

_B51 = _b51_scan()
B51V = lambda k, i=None: (_B51[k] if i is None else _B51[k][i])
'''

compile(BLK, u'<b51 block>', 'exec')
o = u'\n_B50 = _b50_scan()'
o2 = u'B50V=B50V)'
o2b = u'B50V=B50V,\n               B51V=B51V)'
if BLK in S:
    S = S.replace(BLK, u'')
if o2b in S:
    S = S.replace(o2b, o2)
assert S.count(o) == 1
S = S.replace(o, BLK + o)
assert S.count(o2) == 1
S = S.replace(o2, o2b)

# SRC['B51'] ⇎ ATOM 名单
PS = u"SRC['B49'] = ["
blk = (u"SRC['B51'] = ['corpus/raw/cot/math_subsets.md', 'corpus/raw/cot/math_subsets_s2.md',\n"
       u"            'corpus/raw/cot/med_gitalb.md', 'corpus/raw/cot/med_gitalb_s2.md']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1
S = S.replace(PS, blk + PS)
OLD = u"'B48', 'B49', 'B50'}"
NEW = u"'B48', 'B49', 'B50', 'B51'}"
if NEW in S:
    pass
else:
    assert S.count(OLD) == 1
    S = S.replace(OLD, NEW)

M1 = u'# ---- B51 DERIV (generated by corpus/_mkB51.py; do not hand-edit) ----'
M2 = u'# ---- /B51 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + u'\\n', re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1
J = __import__('json').load(io.open(u'corpus/_deriv51.json', encoding='utf-8'))
body = M1 + u'\n' + u"DERIV['B51'] = " + repr(J) + u'\n' + M2 + u'\n'
S = S.replace(o3, body + o3)

# 预演: 用刚写好的扫描器把 DERIV 的每一条算一遍, 值不符就当场停机, 别让门槛去猜
NS = {'SRC': {'B51': ['corpus/raw/cot/math_subsets.md', 'corpus/raw/cot/math_subsets_s2.md',
                      'corpus/raw/cot/med_gitalb.md', 'corpus/raw/cot/med_gitalb_s2.md']},
      're': re, 'os': __import__('os'), 'glob': __import__('glob')}
exec(compile(BLK, u'<b51 block>', 'exec'), NS)
env = NS['B51V']
BAD = []
for k, v in J.items():
    try:
        got = eval(v, dict(NS), {'B51V': env})
    except Exception as e:
        BAD.append((k, v, repr(e)))
        continue
    if str(got) != k and repr(got) != k:
        BAD.append((k, v, str(got)))
assert not BAD, BAD
assert len(S) > 100000 and u'_b50_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
__import__('os').replace(T, P)
print(u'audit.py wired: scan+env+DERIV(%d keys, 预演全对)' % len(J))
