# -*- coding: utf-8 -*-
"""把 B50 的独立复算器(_b50_scan / B50V)接进 audit.py, 并留出 DERIV['B50'] 的生成块位。
幂等: 重复运行先摘旧块再插新块。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()

BLK = u'''
# B50: 同一模型 ⇎ 六个领域的六份思维链。区段长度、词法计数与每万字归一全在审计器里独立复算,
# 与采集侧脚本 corpus/_mkB50.py 各写一遍, 两边不符就证明失败。
def _b50_scan():
    import hashlib as _hl
    F = [open(SRC['B50'][i], encoding='utf-8', errors='replace').read() for i in range(6)]
    HEAD = lambda i, k: dict(re.findall(u'^(model|slug|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$', F[i], re.M))[k]
    R = []
    for i in range(6):
        a = F[i].find(u'## [[REASONING]]')
        b = F[i].find(u'## [[ANSWER]]', a)
        R.append(F[i][a + 17:b].strip())
    RAWR = []
    for i in range(6):
        a = F[i].find(u'## [[REASONING]]')
        b = F[i].find(u'## [[ANSWER]]', a)
        RAWR.append(F[i][a + 17:b])
    PFR = []
    for i in range(6):
        a = F[i].find(u'## [[PROMPT]]')
        b = F[i].find(u'## [[REASONING]]', a)
        PFR.append(F[i][a + 14:F[i].find(u'\\n\\n## [[REASONING]]', a)])
    d = {}
    d['rcot'] = [len(R[i]) for i in range(6)]
    d['raucot'] = [int(HEAD(i, 'reasoning_chars')) for i in range(6)]
    d['rawr'] = [len(RAWR[i]) for i in range(6)]
    d['gap'] = [len(RAWR[i]) - len(R[i]) for i in range(6)]
    d['acot'] = [len(_answer('B50', i).strip()) for i in range(6)]
    d['pcot'] = [len(PFR[i].strip()) for i in range(6)]
    d['praw'] = [len(PFR[i]) for i in range(6)]
    d['fchars'] = [len(F[i]) for i in range(6)]
    d['fbytes'] = [os.path.getsize(SRC['B50'][i]) for i in range(6)]
    d['nascii'] = [len(re.findall(u'[^\\x00-\\x7f]', F[i])) for i in range(6)]
    d['lines'] = [len(R[i].split(chr(10))) for i in range(6)]
    d['sent'] = [len(re.findall(r'[.!?](?:\\s|$)', R[i])) for i in range(6)]
    d['para'] = [len([x for x in R[i].split(chr(10)) if x.strip()]) for i in range(6)]
    d['numsent'] = [len([x for x in re.split(r'(?<=[.!?])\\s+', R[i]) if re.search(r'\\d', x)]) for i in range(6)]
    PATS = {
        'wait': r'(?i)\\bWait\\b',
        'actually': r'(?i)\\bactually\\b',
        'maybe': r'(?i)\\bmaybe\\b|\\bperhaps\\b',
        'prob': r'(?i)\\bprobably\\b|\\blikely\\b',
        'assume': r'(?i)\\bassume[ds]?\\b|\\bassuming\\b',
        'unsure': r'(?i)\\bnot sure\\b|\\bunclear\\b|\\bi (?:think|believe)\\b',
        'verif': r'(?i)\\bcheck\\b|\\bverify\\b|\\bsanity\\b|\\bdouble[- ]check\\b|\\bconfirm\\b',
        'redo': r'(?i)\\bredo\\b|\\bstart over\\b|\\blet me (?:recompute|recheck)\\b',
        'wrong': r'(?i)\\bwrong\\b|\\bmistake\\b|\\berror\\b|\\boops\\b',
        'therefore': r'(?i)\\btherefore\\b|\\bthus\\b|\\bhence\\b|\\bso\\b',
        'however': r'(?i)\\bhowever\\b|\\bbut\\b|\\balthough\\b|\\bwhereas\\b',
        'must': r'(?i)\\bmust\\b',
        'caveat': r'(?i)\\bcaveat\\b|\\bcaution\\b|\\bcareful\\b|\\bbeware\\b',
        'final': r'(?i)\\bfinal\\b|\\bconclusion\\b|\\banswer:|\\brecommend',
        'quote': r'"[^"]{10,60}"',
        'equality': '=',
        'unit': r'(?i)\\b(?:mm|MPa|kN|GPa|\\u00b0C|kg|m|s|y|years|months|mm/yr|kW|Hz|Bq|Sv|Gy|%)\\b',
        'cfr': r'(?i)\\b(?:article|section|\\u00a7|clause|paragraph|paragraphs)\\b',
        'study': r'(?i)\\bstudy\\b|\\bpaper\\b|\\bauthor',
        'restart_word': r'(?i)\\brestart(?:s|ed|ing)?\\b',
        'uncertain_word': r'(?i)\\buncertain(?:ty|ly)?\\b',
        'bold': r'\\*\\*[^*]{2,60}\\*\\*',
        'lets': r"(?i)\\blet's\\b",
        'letme': r'(?i)\\blet me\\b',
        'need': r'(?i)\\bneed\\b',
        'q': r'\\?',
        'arrow': '->',
        'hmm': r'(?i)\\bHmm\\b',
    }
    CORE = ['wait', 'actually', 'maybe', 'prob', 'assume', 'unsure', 'verif', 'redo', 'wrong',
            'therefore', 'however', 'must', 'caveat', 'final', 'quote', 'equality', 'unit', 'cfr', 'study']
    for k, p in PATS.items():
        d[k] = [len(re.findall(p, R[i], re.I)) for i in range(6)]
    for k in list(d):
        if k in PATS:
            d[k + '_p'] = [round(10000.0 * d[k][i] / d['rcot'][i], 1) for i in range(6)]
    lead = lambda v: sorted([i for i in range(6) if v[i] == max(v)])
    d['flip'] = len([k for k in sorted(CORE) if lead(d[k]) != lead(d[k + '_p'])])
    d['npats'] = len(CORE)
    d['nextra'] = len(PATS) - len(CORE)
    d['nsrc'] = len(SRC['B50'])
    d['allpos'] = len([k for k in sorted(CORE) if min(d[k]) >= 1])
    d['sixzero'] = len([k for k in sorted(CORE) if max(d[k]) == 0])
    d['models'] = len(set(HEAD(i, 'model') for i in range(6)))
    d['model_bare'] = len(set(HEAD(i, 'model').split('/')[-1] for i in range(6)))
    d['hashes'] = len(set(HEAD(i, 'prompt_sha256') for i in range(6)))
    d['sha_ok'] = len([1 for i in range(6)
                       if _hl.sha256(PFR[i].encode('utf-8')).hexdigest()[:16] == HEAD(i, 'prompt_sha256')])
    d['retr'] = len(set(HEAD(i, 'retrieved') for i in range(6)))
    d['tailbad'] = len([1 for i in range(6) if R[i][-1] not in u'.!?"'])
    d['pgap'] = len(PFR[0]) - len(PFR[0].strip())
    assert all(len(PFR[i]) - len(PFR[i].strip()) == d['pgap'] for i in range(6))
    d['rcotsum'] = sum(d['rcot'])
    d['rcmax'] = max(d['rcot'])
    d['rcmin'] = min(d['rcot'])
    d['rcratio'] = round(1.0 * max(d['rcot']) / min(d['rcot']), 1)
    ATOMF = 'corpus/_atoms50.txt'
    A50 = [x.strip() for x in open(ATOMF, encoding='utf-8').read().split(chr(10)) if x.strip()] if os.path.exists(ATOMF) else []
    def _pn(s):
        s = s.lower()
        for a, b in ((chr(8217), chr(39)), (chr(8220), chr(34)), (chr(8221), chr(34))):
            s = s.replace(a, b)
        s = re.sub(u'[' + chr(8217) + chr(8220) + chr(8221) + chr(39) + chr(34) + u'`´]+', '', s)
        s = re.sub(u'[^0-9a-z\\u4e00-\\u9fff. -]', ' ', s)
        return re.sub(u'\\\\s+', ' ', s).strip()
    RR = [_pn(x) for x in R]
    RR = [re.sub(u' +', ' ', x) for x in RR]
    hits = [len([j for j in range(6) if _pn(x) in RR[j]]) for x in A50]
    d['anchor_total'] = len(A50)
    d['anchor_distinct'] = len(set(_pn(x) for x in A50))
    d['cross'] = len([h for h in hits if h != 1])
    d['checks'] = len(A50) * len(SRC['B50'])
    return d

_B50 = _b50_scan()
B50V = lambda k, i=None: (_B50[k] if i is None else _B50[k][i])
'''

compile(BLK, u'<b50 block>', 'exec')
o = u'\n_B49 = _b49_scan()'
o2 = u'B49V=B49V, B49_LINES=B49_LINES, B49_DROP=B49_DROP, B49_BYTES=B49_BYTES)'
o2b = u'B49V=B49V, B49_LINES=B49_LINES, B49_DROP=B49_DROP, B49_BYTES=B49_BYTES,\n               B50V=B50V)'
if BLK in S:
    S = S.replace(BLK, u'')
if o2b in S:
    S = S.replace(o2b, o2)
assert S.count(o) == 1
S = S.replace(o, BLK + o)
assert S.count(o2) == 1
S = S.replace(o2, o2b)

M1 = u'# ---- B50 DERIV (generated by corpus/_mkB50.py; do not hand-edit) ----'
M2 = u'# ---- /B50 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + u'\\n', re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1
J = __import__('json').load(io.open(u'corpus/_deriv50.json', encoding='utf-8'))
body = M1 + u'\n' + u"DERIV['B50'] = " + repr(J) + u'\n' + M2 + u'\n'
S = S.replace(o3, body + o3)
assert len(S) > 100000 and u'_b49_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
__import__('os').replace(T, P)
print('audit.py wired: scan+env+DERIV(%d keys)' % len(J))
