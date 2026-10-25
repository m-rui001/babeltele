# -*- coding: utf-8 -*-
"""B53 建条目(第二遍现算): 同一份 FIPS 202 的四种序列化——官方 txt ⇎ 本机 pdftotext -layout
⇎ 本机 pdftotext raw ⇎ 官方 CSRC 落地页 html。
锚只按特征子串从 _pick53.py 的候选池取(不手抄原文); 每个数字在这里独立现算并登记成 audit.py 里 B53V 的复算式,
零值折进 '0' 键; 同一套算式采集侧(_pick53)与审计侧(_b53_scan)各再写一遍, 三边不符即证明失败。
不可核的一句话(“哪一种序列化才是这份标准”“PDF 里那个格子本来画的是什么”)按成因写进判词, 不写成待核。"""
import io, os, re, sys, json, hashlib, collections

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = u'corpus'
NL = u'\n'
ENTRY = u'%s/babeltele/B53_four_serializations_of_one_standard.md' % C
J = json.load(io.open(os.path.join(ROOT, C, u'_b53meas.json'), encoding='utf-8'))
MM, POOL, SEL = J[u'meas'], J[u'pool'], J[u'sel']
TAGS, PATH = J[u'tags'], J[u'paths']
LB = dict(zip(TAGS, [u'官方纯文本', u'本机按版式', u'本机无版式', u'官方落地页']))
RD = lambda p: io.open(os.path.join(ROOT, p), encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATH]
IDX = dict((t, i) for i, t in enumerate(TAGS))


def pnorm(s):
    s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
    s = re.sub(u'[’\'"\u2018\u2019`´]+', u'', s)
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff\-\. ]+', u' ', s)
    return re.sub(r'\s+', u' ', s).strip()


def hitset(a):
    n = pnorm(a)
    return tuple(i for i in range(4) if n and n in FA[i])


def cls_of(h):
    return u'all4' if len(h) == 4 else (u'cross' if len(h) > 1 else (u'single' if h else u'err'))


def nbS(s):
    return [l.strip() for l in s.split(NL) if l.strip()]


def nbR(s):
    return [l.rstrip(u'\r') for l in s.split(NL) if l.strip()]


def skel(s):
    return re.sub(u'[^0-9a-zA-Z]', u'', s)


def flat(s):
    return re.sub(u'\\s+', u'', s)


TAGLESS = {u'H': re.sub(u'<[^>]+>', u' ', TXT[IDX[u'H']])}
BODY = {u'T': TXT[0], u'L': TXT[1], u'P': TXT[2], u'H': TAGLESS[u'H']}
RAWB = dict((k, TXT[IDX[k]]) for k in TAGS)
HRAW = TXT[IDX[u'H']]
FN = [pnorm(BODY[TAGS[i]]) for i in range(4)]
# 锚的命中判定: 落地页按原文件行判, 其余三层按去标签正文判(与 _pick53.py 同一处口径)
FA = [pnorm(RAWB[TAGS[i]]) if TAGS[i] == u'H' else pnorm(BODY[TAGS[i]]) for i in range(4)]
NB = dict((k, nbR(BODY[k])) for k in TAGS)
NBF = dict((k, nbR(RAWB[k]) if k != u'H' else nbR(HRAW)) for k in TAGS)
F = {}


def four(name, f):
    F[name] = [f(k) for k in TAGS]


four(u'bytes', lambda k: os.path.getsize(PATH[IDX[k]]))
four(u'chars', lambda k: len(RAWB[k]))
four(u'lines', lambda k: RAWB[k].count(NL))
four(u'nonblank', lambda k: len(NBF[k]))
four(u'blank', lambda k: F[u'lines'][IDX[k]] - F[u'nonblank'][IDX[k]])
four(u'medlen', lambda k: sorted(len(x) for x in NBF[k])[len(NBF[k]) // 2])
four(u'maxlen', lambda k: max(len(x) for x in NBF[k]))
four(u'gt120', lambda k: len([x for x in NBF[k] if len(x) > 120]))
four(u'le20', lambda k: len([x for x in NBF[k] if len(x) <= 20]))
four(u'wocc', lambda k: len(re.findall(u'[A-Za-z0-9]+', BODY[k].lower())))
four(u'wseta', lambda k: len(set(re.findall(u'[A-Za-z0-9]+', BODY[k].lower()))))
WB = dict((k, set(re.findall(u'[A-Za-z0-9]+', flat(BODY[k]).lower()))) for k in TAGS)
four(u'wsetb', lambda k: len(WB[k]))
WA = dict((k, set(re.findall(u'[A-Za-z0-9]+', BODY[k].lower()))) for k in TAGS)
four(u'nonascii', lambda k: sum(1 for ch in BODY[k] if ord(ch) > 127))
four(u'naskinds', lambda k: len(set(ch for ch in BODY[k] if ord(ch) > 127)))
four(u'formfeed', lambda k: RAWB[k].count(u'\f'))
four(u'tabchar', lambda k: RAWB[k].count(u'\t'))
four(u'trailws', lambda k: len([x for x in RAWB[k].split(NL) if x != x.rstrip()]))
four(u'multicol', lambda k: len([x for x in NBF[k] if re.search(u'\\S {3,}\\S', x)]))
four(u'pagehdr', lambda k: len(re.findall(u'^FIPS PUB 202', RAWB[k], re.M)))
four(u'wrap72', lambda k: len([x for x in NBF[k] if len(x) > 72]))
F[u'onlya_tl'] = len(WA[u'T'] - WA[u'L'])
F[u'onlya_lt'] = len(WA[u'L'] - WA[u'T'])
F[u'onlyb_tl'] = len(WB[u'T'] - WB[u'L'])
F[u'onlyb_lt'] = len(WB[u'L'] - WB[u'T'])
F[u'inter_tl'] = len(WA[u'T'] & WA[u'L'])
F[u'inter_tp'] = len(WA[u'T'] & WA[u'P'])
F[u'inter_th'] = len(WA[u'T'] & WA[u'H'])
F[u'inter_lp'] = len(WA[u'L'] & WA[u'P'])
F[u'setdiff_ab'] = [F[u'wsetb'][IDX[k]] - F[u'wseta'][IDX[k]] for k in TAGS]

# 码点命运
CP = {u'le': u'≤', u'cdot': u'⋅', u'prime': u'′', u'ldots': u'…', u'oplus': u'⊕', u'pi': u'π',
      u'puf': u'\uf02d', u'endash': u'–', u'emdash': u'—', u'minus': u'−', u'fffd': u'\ufffd',
      u'hyph': u'-'}
for nm, ch in CP.items():
    four(nm, lambda k, ch=ch: BODY[k].count(ch))
F[u'glyphkinds_T'] = len([nm for nm in CP if nm != u'hyph' and F[nm][0]])
F[u'glyphkinds_gen'] = len([nm for nm in CP if F[nm][1] or F[nm][2]])
F[u'dashkinds'] = [len(set(ch for ch in BODY[k] if ch in u'‐‑‒–—―−\uf02d-')) for k in TAGS]
F[u'cp_nonascii'] = [sum(F[nm][IDX[k]] for nm in CP if nm != u'hyph') for k in TAGS]

# 结构计数
ST = {u'algo': u'Algorithm \\d', u'step': u'Step \\d', u'table': u'Table \\d',
      u'figure': u'Figure \\d', u'app': u'Appendix'}
for nm, pat in ST.items():
    four(nm, lambda k, pat=pat: len(re.findall(pat, BODY[k])))
ALG = dict((k, sorted(set(int(x) for x in re.findall(u'Algorithm (\\d+)', BODY[k])))) for k in TAGS)
F[u'algon'] = [len(ALG[k]) for k in TAGS]
F[u'algomax'] = [max(ALG[k]) if ALG[k] else 0 for k in TAGS]
F[u'algosame'] = 1 if ALG[u'T'] == ALG[u'L'] == ALG[u'P'] else 0

# 骨架四口径
TL = nbS(BODY[u'T'])
KEY = [(skel(x), x) for x in TL if len(skel(x)) >= 12]
F[u'pairtotal'] = len(KEY)


def paircal(k):
    raw = set(BODY[k].split(NL))
    strip = set(nbS(BODY[k]))
    sk = set(skel(x) for x in NB[k])
    return (sum(1 for s, x in KEY if x in raw), sum(1 for s, x in KEY if x in strip),
            sum(1 for s, x in KEY if s in sk))


for pre, k in ((u'tl', u'L'), (u'tp', u'P'), (u'th', u'H')):
    a, b, c = paircal(k)
    F[u'pair_' + pre + u'_raw'] = a
    F[u'pair_' + pre + u'_strip'] = b
    F[u'pair_' + pre + u'_skel'] = c
    F[u'gap_' + pre] = c - b

# 折叠空白后的最长公共片段
def runmax(a, b, k=40, cap=4000):
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
        out.append(e - s)
        s = e
    return out


FL = dict((k, flat(BODY[k])) for k in TAGS)
RS = dict((p, runmax(FL[p[1]], FL[p[0]])) for p in ((u'L', u'T'), (u'P', u'T'), (u'H', u'T'), (u'L', u'P')))
F[u'run_pieces'] = [len(RS[p]) for p in ((u'L', u'T'), (u'P', u'T'), (u'H', u'T'), (u'L', u'P'))]
F[u'run_total'] = [sum(RS[p]) for p in ((u'L', u'T'), (u'P', u'T'), (u'H', u'T'), (u'L', u'P'))]
F[u'run_max'] = [max(RS[p]) for p in ((u'L', u'T'), (u'P', u'T'), (u'H', u'T'), (u'L', u'P'))]
F[u'run_share'] = [int(round(100.0 * sum(RS[p]) / len(FL[p[0]])))
                   for p in ((u'L', u'T'), (u'P', u'T'), (u'H', u'T'), (u'L', u'P'))]

# html 的两种“正文”
F[u'html_tags'] = len(re.findall(u'<[a-zA-Z][^>]*>', HRAW))
F[u'html_tagkinds'] = len(set(re.findall(u'<([a-zA-Z][a-zA-Z0-9]*)', HRAW)))
F[u'html_a'] = HRAW.count(u'<a ')
F[u'html_img'] = HRAW.count(u'<img')
F[u'html_src'] = len(re.findall(u'src="', HRAW))
F[u'html_ext'] = len(re.findall(u'href="https?://', HRAW))
F[u'html_uswds_raw'] = HRAW.count(u'uswds')
F[u'html_uswds_body'] = BODY[u'H'].count(u'uswds')
F[u'html_doi_raw'] = HRAW.count(u'10.6028/NIST.FIPS.202')
F[u'html_doi_body'] = BODY[u'H'].count(u'10.6028/NIST.FIPS.202')
F[u'html_sha3_raw'] = len(re.findall(u'(?i)sha3', HRAW))
F[u'html_sha3_body'] = len(re.findall(u'(?i)sha3', BODY[u'H']))
four(u'doi_occ', lambda k: BODY[k].count(u'10.6028/NIST.FIPS.202'))
four(u'aug_occ', lambda k: BODY[k].count(u'August 2015'))
F[u'pub_H'] = HRAW.count(u'Date Published')
F[u'title'] = (re.findall(u'<title>([^<]*)</title>', HRAW) or [u''])[0].strip()
F[u'pdf_pages'] = len(re.findall(rb'/Type\s*/Page[^s]', open(os.path.join(ROOT, C, u'raw/fips202.pdf'), 'rb').read()))
F[u'pdf_streams'] = open(os.path.join(ROOT, C, u'raw/fips202.pdf'), 'rb').read().count(b'stream')

# 穿层矩阵
CROSS = [u'FIPS PUB 202', u'SHA-3 Standard', u'Permutation-Based Hash', u'Extendable-Output Functions',
         u'August 2015', u'10.6028/NIST.FIPS.202', u'Algorithm 1', u'Step 1', u'⊕', u'π',
         u'sponge function', u'sha3-256', u'shake256', u'CSRC MENU', u'uswds', u'Keccak',
         u'Information Technology Laboratory', u'Pad10*1', u'rate', u'capacity']
HS, CAL = [], []
for t in CROSS:
    n = pnorm(t)
    if n:
        HS.append(tuple(i for i in range(4) if n in FN[i]))
        CAL.append(u'norm')
    else:
        HS.append(tuple(i for i in range(4) if t in BODY[TAGS[i]]))
        CAL.append(u'raw')
F[u'hitkinds'] = len(CROSS)
F[u'hitnorm'] = CAL.count(u'norm')
F[u'hitraw'] = CAL.count(u'raw')
F[u'hitsingle'] = len([h for h in HS if len(h) == 1])
F[u'hitmulti'] = len([h for h in HS if 1 < len(h) < 4])
F[u'hitall'] = len([h for h in HS if len(h) == 4])
F[u'hitnone'] = len([h for h in HS if not h])
assert F[u'hitsingle'] + F[u'hitmulti'] + F[u'hitall'] + F[u'hitnone'] == F[u'hitkinds']

# 候选池只作选材记录(池机器住在 _pick53.py, 由解读注现算引用), 不进扁平表
four(u'prime', lambda k: BODY[k].count(u'′'))
four(u'dots', lambda k: BODY[k].count(u'…'))
four(u'stepsoft', lambda k: len(re.findall(u'Step\\s*\\d', BODY[k])))
F[u'skmin'] = 12
KW = [u'algorithm', u'fips', u'keccak', u'nist', u'sha3', u'shake', u'sponge', u'step']
F[u'hkw_raw'] = sum(len(re.findall(u'(?i)' + x, HRAW)) for x in KW)
F[u'hkw_body'] = sum(len(re.findall(u'(?i)' + x, BODY[u'H'])) for x in KW)
F[u'hkw_lost'] = F[u'hkw_raw'] - F[u'hkw_body']
F[u'hfp_raw'] = len(re.findall(u'(?i)fips', HRAW))
F[u'hfp_body'] = len(re.findall(u'(?i)fips', BODY[u'H']))
F[u'stepwrap'] = F[u'stepsoft'][0] - F[u'step'][0]
F[u'gen_n'] = 2
F[u'dl_n'] = 2
F[u'sha_distinct'] = len(set(hashlib.sha256(t.encode(u'utf-8')).hexdigest() for t in TXT))
F[u'nsrc'] = 4

TIE = [u'bytes', u'chars', u'lines', u'nonblank', u'medlen', u'maxlen', u'gt120', u'le20',
       u'wocc', u'formfeed', u'trailws', u'multicol', u'pagehdr', u'nonascii', u'naskinds']
TIE_MAP = {u'medlen': u'linelen_med', u'maxlen': u'linelen_max', u'gt120': u'lines_gt120',
           u'le20': u'lines_le20', u'trailws': u'trailing_ws', u'naskinds': u'nonascii_kinds',
           u'pagehdr': u'page_hdr'}
BAD = [(k, F[k], MM[TIE_MAP.get(k, k)]) for k in TIE if F[k] != MM[TIE_MAP.get(k, k)]]
assert not BAD, BAD
assert [F[u'onlya_tl'], F[u'onlyb_tl']] == [MM[u'only_a'][0], MM[u'only_b'][0]], F[u'onlya_tl']
assert [F[u'pair_tl_skel'], F[u'pair_th_skel'], F[u'pairtotal']] == [
    MM[u'pair_TL'][2], MM[u'pair_TH'][2], MM[u'pair_total']], (F[u'pair_tl_skel'], F[u'pair_th_skel'])
assert F[u'hitkinds'] == MM[u'hitkinds'] and F[u'hitnone'] == MM[u'hitnone']
assert F[u'html_uswds_body'] == 0 and F[u'html_uswds_raw'] > 0

# ---------- 锚: 从池里按特征子串取 ----------
USEDATOM, USEDTAGS = [], []
K, ZERO, COLL = {}, [], []


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K and K[s][0] != expr:
        COLL.append((s, note))
    K.setdefault(s, (expr, note))


def V(name, i=None, note=u''):
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"B53V('%s'%s)" % (name, u'' if i is None else u', %d' % i), note or name)
    return s


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


TOKV = {}


def ATOMSEL(kind, tag, *needles):
    def ok(p):
        n = len(p[1])
        if kind == u'own':
            return n == 1
        if kind.startswith(u'c') and kind[1:].isdigit():
            return n == int(kind[1:])
        if kind == u'any':
            return True
        raise ValueError(kind)
    got = [p for p in POOL if p[0] == tag and ok(p) and all(x in p[2] for x in needles)]
    assert got, (kind, tag, needles)
    return max(got, key=lambda x: (len(x[2]), x[2]))


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    USEDATOM.append(x[2])
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


PAIRN = [u'按版式⇎官方', u'无版式⇎官方', u'落地页⇎官方', u'两抽取层之间']


def JOINP(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, PAIRN[i])) for i in range(4))


def JOIN(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LB[t])) for i, t in enumerate(TAGS))


G = {}
LINES = []


def LINE(em, tmpl, **kw):
    LINES.append((em + u' ' + tmpl).format(**kw))


def EXPR(s, expr, note):
    reg(s, expr, note)
    return s


# 那一行里 ⊕ 的枚数, 与它在按版式层留下的空档数: 锚句自带的事实, 也登记成可复算式
GLINE = [x for x in nbS(BODY[u'T']) if u'C[x, z] = A[x, 0, z]' in x][0]
LLINE = [x for x in nbS(BODY[u'L']) if u'C[x, z] = A[x, 0, z]' in x][0]
F[u'gl_opl'] = GLINE.count(u'⊕')
F[u'gl_gap'] = len(re.findall(u'  ', LLINE))
G[u'aTtl'] = AT(u'c3', u'T', u'SHA-3 Standard: Permutation')
G[u'aAbs'] = AT(u'own', u'H', u'This Standard specifies the Secure Hash')
G[u'atdash'] = AT(u'own', u'T', u'digests from hash functions')
G[u'astep'] = AT(u'any', u'P', u'The dot in the right side')
G[u'aquot'] = AT(u'c3', u'T', u'“absorbed”')
G[u'atab'] = AT(u'c3', u'T', u'Table 3:  Input block sizes')
G[u'ap1600'] = AT(u'c3', u'T', u'p[1600,24] permutation')
G[u'aredir'] = AT(u'own', u'H', u'potential security issue')
G[u'acaps'] = AT(u'c3', u'P', u'the capacity is double')
G[u'aweb'] = AT(u'own', u'H', u'An official website')
G[u'acol'] = AT(u'own', u'L', u'A[0, 0, 1] = S [1]')
G[u'atitle'] = AT(u'own', u'H', u'FIPS 202, SHA-3 Standard')
G[u'gl'] = AT(u'c3', u'T', u'C[x, z] = A[x, 0, z]')
G[u'gl2'] = AT(u'c2', u'L', u'D[x, z] = C[(x1) mod 5')
G[u'stab'] = AT(u'own', u'L', u'Function  Output')
G[u'salg'] = AT(u'own', u'P', u'SHA-1 SHA-224')
G[u'st2'] = AT(u'c3', u'T', u'Step 2a')
G[u'adash'] = AT(u'c2', u'L', u'--generally do exhibit')
G[u'aell'] = AT(u'own', u'T', u'Lane (0, 0) = A[0, 0, 0]')
G[u'aprime'] = AT(u'own', u'T', u'for all z such that 0')
G[u'aminus'] = AT(u'own', u'T', u'D[x, z] = C[(x')
G[u'amast'] = AT(u'c3', u'P', u'Gaithersburg, MD')
G[u'alongs'] = AT(u'own', u'P', u'The KECCAK-p permutations were designed')
G[u'adoi'] = AT(u'c3', u'T', u'http://dx.doi.org')
G[u'ashake'] = AT(u'c3', u'L', u'The SHA-3 XOF that generally supports 128')
G[u'aframe'] = AT(u'own', u'H', u'unauthorized frame window')
G[u'adata'] = AT(u'own', u'H', u'window.dataLayer')
G[u'aurl'] = AT(u'c3', u'T', u'keccak.noekeon.org/Keccak-submission')
G[u'by'] = JOIN(u'bytes', u'字节')
G[u'ch'] = JOIN(u'chars', u'字符')
G[u'nb'] = JOIN(u'nonblank', u'非空行')
G[u'ly'] = JOIN(u'lines', u'行数')
G[u'med'] = JOIN(u'medlen', u'中位行长')
G[u'maxl'] = JOIN(u'maxlen', u'最长行')
G[u'ff'] = JOIN(u'formfeed', u'分页符')
G[u'tw'] = JOIN(u'trailws', u'行尾空格')
G[u'mc'] = JOIN(u'multicol', u'三空格断栏')
G[u'mcl'] = V(u'multicol', IDX[u'L'])
G[u'w72'] = JOIN(u'wrap72', u'超 72 字行')
G[u'ph'] = JOIN(u'pagehdr', u'页首页眉')
G[u'glop'] = V(u'gl_opl')
G[u'glgap'] = V(u'gl_gap')
G[u'le'] = JOIN(u'le', u'小于等号')
G[u'op'] = JOIN(u'oplus', u'异或圈')
G[u'lev'] = V(u'le', IDX[u'T'])
G[u'opv'] = V(u'oplus', IDX[u'T'])
G[u'fffd'] = JOIN(u'fffd', u'替换符')
G[u'na'] = JOIN(u'nonascii', u'非 ASCII 个')
G[u'nak'] = JOIN(u'naskinds', u'非 ASCII 种')
G[u'cpna'] = JOIN(u'cp_nonascii', u'这些码点合计')
G[u'dk'] = JOIN(u'dashkinds', u'破折号码点种')
G[u'yh'] = JOIN(u'hyph', u'连字符')
G[u'pt2'] = V(u'pairtotal')
G[u'tlr'], G[u'tls'], G[u'tlk'] = V(u'pair_tl_raw'), V(u'pair_tl_strip'), V(u'pair_tl_skel')
G[u'tpr'], G[u'tps'], G[u'tpk'] = V(u'pair_tp_raw'), V(u'pair_tp_strip'), V(u'pair_tp_skel')
G[u'thr'], G[u'ths'], G[u'thk'] = V(u'pair_th_raw'), V(u'pair_th_strip'), V(u'pair_th_skel')
G[u'pTL'] = u' ⇎ '.join([G[u'tlr'], G[u'tls'], G[u'tlk']])
G[u'pTP'] = u' ⇎ '.join([G[u'tpr'], G[u'tps'], G[u'tpk']])
G[u'pTH'] = u' ⇎ '.join([G[u'thr'], G[u'ths'], G[u'thk']])
G[u'gaptl'] = V(u'gap_tl')
G[u'gaptp'] = V(u'gap_tp')
G[u'gapth'] = V(u'gap_th')
G[u'ws'] = JOIN(u'wseta', u'词集')
G[u'wsb'] = JOIN(u'wsetb', u'压空白后词集')
G[u'oat'], G[u'oal'] = V(u'onlya_tl'), V(u'onlya_lt')
G[u'obt'], G[u'obl'] = V(u'onlyb_tl'), V(u'onlyb_lt')
G[u'itl'], G[u'ith'] = V(u'inter_tl'), V(u'inter_th')
G[u'itp'], G[u'ilp'] = V(u'inter_tp'), V(u'inter_lp')
G[u'absw'] = V(u'wocc', IDX[u'H']) + u' ⇎ ' + V(u'wocc', IDX[u'T'])
G[u'ht'] = V(u'html_tags')
G[u'htk'] = V(u'html_tagkinds')
G[u'ha'] = V(u'html_a')
G[u'himg'] = V(u'html_img')
G[u'hsrc'] = V(u'html_src')
G[u'hext'] = V(u'html_ext')
G[u'usw'] = V(u'html_uswds_raw') + u' ⇎ ' + V(u'html_uswds_body')
G[u'doi2'] = V(u'html_doi_raw') + u' ⇎ ' + V(u'html_doi_body')
G[u'sha3h'] = V(u'html_sha3_raw') + u' ⇎ ' + V(u'html_sha3_body')
G[u'ap'] = JOIN(u'algo', u'Algorithm 引用')
G[u'asp'] = JOIN(u'step', u'Step 引用')
G[u'af'] = JOIN(u'figure', u'Figure 引用')
G[u'at'] = JOIN(u'table', u'Table 引用')
G[u'aap'] = JOIN(u'app', u'Appendix 字样')
G[u'sa'] = JOIN(u'algon', u'算法号种')
G[u'almx'] = JOIN(u'algomax', u'最大算法号')
G[u'stpd'] = EXPR(str(F[u'step'][2] - F[u'step'][0]),
                  u"B53V('step', 2)-B53V('step', 0)", u'Step 引用在无版式层多出的一处')
G[u'pp'] = V(u'pdf_pages')
G[u'ps'] = V(u'pdf_streams')
G[u'aug'] = JOIN(u'aug_occ', u'August 2015')
G[u'doi'] = JOIN(u'doi_occ', u'DOI 串')
G[u'pub'] = V(u'pub_H')
G[u'rp'] = JOINP(u'run_pieces', u'公共片段段')
G[u'rt'] = JOINP(u'run_total', u'公共字符')
G[u'rx'] = JOINP(u'run_max', u'最长片段')
G[u'rs'] = JOINP(u'run_share', u'共享比例')
G[u'rsh'] = V(u'run_share', 2, u'共享比例·落地页⇎官方')
G[u'ffl'] = V(u'formfeed', IDX[u'L'], u'分页符·本机按版式')
G[u'ffq'] = V(u'formfeed', IDX[u'P'], u'分页符·本机无版式')
G[u'prm'] = JOIN(u'prime', u'撇号 ′')
G[u'ldt'] = JOIN(u'dots', u'省略号 …')
G[u'sof'] = JOIN(u'stepsoft', u'Step 加空白加数字')
G[u'swr'] = V(u'stepwrap', None, u'官方 txt 里被折行切开的 Step 引用')
G[u'g01'] = EXPR(str(F[u'pair_tl_strip'] - F[u'pair_tl_raw']),
                  u"B53V('pair_tl_strip')-B53V('pair_tl_raw')", u'原样到去空白多配的行')
G[u'dtl'] = EXPR(str(F[u'pair_tl_skel'] - F[u'pair_tl_raw']),
                 u"B53V('pair_tl_skel')-B53V('pair_tl_raw')", u'原样到骨架多配的行')
G[u'skm'] = V(u'skmin', None, u'骨架行长度门槛')
G[u'nasc'] = V(u'nonascii', 0, u'非 ASCII 个·官方纯文本')
G[u'nal'] = V(u'nonascii', IDX[u'L'], u'非 ASCII 个·本机按版式')
assert F[u'fffd'][1] == F[u'nonascii'][1] and F[u'fffd'][2] == F[u'nonascii'][2], (
    F[u'fffd'], F[u'nonascii'])
G[u'nadiff'] = EXPR(str(F[u'nonascii'][0] - F[u'nonascii'][1]),
                    u"B53V('nonascii', 0)-B53V('nonascii', 1)", u'两套非 ASCII 计数之差')
G[u'kwr'] = V(u'hkw_raw', None, u'八个关键词·整份 html')
G[u'kwb'] = V(u'hkw_body', None, u'八个关键词·去标签正文')
G[u'kwl'] = V(u'hkw_lost', None, u'八个关键词·随标签丢掉')
G[u'fpr'] = V(u'hfp_raw', None, u'fips 字样·整份 html')
G[u'fpb'] = V(u'hfp_body', None, u'fips 字样·去标签正文')
G[u'phv'] = V(u'pagehdr', IDX[u'T'], u'页首页眉·官方纯文本')
G[u'phh'] = V(u'pagehdr', IDX[u'H'], u'页首页眉·官方落地页')
G[u'rsp'] = V(u'run_share', 3, u'共享比例·两抽取层之间')
G[u'maxp'] = V(u'maxlen', IDX[u'P'], u'最长行·无版式')
G[u'maxt'] = V(u'maxlen', IDX[u'T'], u'最长行·官方纯文本')
G[u'twt'] = V(u'trailws', IDX[u'T'], u'行尾空格·官方纯文本')
G[u'twl'] = V(u'trailws', IDX[u'L'], u'行尾空格·本机按版式')
G[u'twq'] = V(u'trailws', IDX[u'P'], u'行尾空格·本机无版式')
G[u'fft'] = V(u'formfeed', IDX[u'T'], u'分页符·官方纯文本')
G[u'doit'] = V(u'doi_occ', IDX[u'T'], u'DOI 串·官方纯文本')
G[u'doih'] = V(u'html_doi_raw', None, u'DOI 串·整份 html 文件')
G[u'hitk'] = V(u'hitkinds')
G[u'h4'], G[u'h1'], G[u'hn'] = V(u'hitall'), V(u'hitsingle'), V(u'hitnone')
G[u'hl3'] = V(u'hitmulti')
G[u'hcal'] = V(u'hitnorm') + u' ⇎ ' + V(u'hitraw')
G[u'sd'] = V(u'sha_distinct')
G[u'gen'] = V(u'gen_n')
G[u'dl'] = V(u'dl_n')
G[u'nat'] = TOK(u'anchor_total', u'正文锚处数')
G[u'ndist'] = TOK(u'anchor_distinct', u'去重锚串数')
G[u'nsgl'] = TOK(u'anchor_single', u'单层锚')
G[u'ncross'] = TOK(u'anchor_cross', u'跨层锚')
G[u'nall'] = TOK(u'anchor_all4', u'四源锚')
G[u'checked'] = TOK(u'checks', u'成员检查次数')
G[u'aerr'] = TOK(u'anchor_err', u'错配数')

LINE(u'🧭', u"体例 {aTtl} ‖ {aAbs} ‖ {aweb} ⇒ 四份材料是同一份 FIPS 202 的四种序列化: 官方纯文本、"
        u"本机 pdftotext 的两种抽取(留版式 ⇎ 不留版式)、官网那页 html。其中 {gen} 份由本机现生、{dl} 份由官网取来; "
        u"四份的 sha {sd} 种全不同, 字节 {by}, 行数 {ly}, 非空行 {nb}, 字符 {ch}——"
        u"所以“同一份标准”这句话在这里只能由内容重叠支撑, 不能由“同一个文件”支撑。", **G)

LINE(u'📏', u"同一页内容在四层里各是几种行 {ly} ‖ 非空 {nb} ‖ 中位行长 {med} ‖ 最长行 {maxl} ⇒ "
        u"无版式抽取把整段并成一条 {maxp} 字的行({alongs}——这一行本身就长过官方 txt 的最长行 {maxt} 字), "
        u"分页符 {ff} 与行尾空格 {tw} 恰好相反: 官方 txt 一个分页符都不留却留着 {twt} 行行尾空格, "
        u"本机两份各留 {ffl} 个分页符、只留 {twl}⇎{twq} 行行尾空格。行数、行长、分页、行尾空格都是抽取器的属性, 不是这份标准的属性。", **G)

LINE(u'🔤', u"关键字形只活在官方 txt 一层 {gl}(这一行在官方 txt 里有 {glop} 枚 ⊕) ‖ {aminus}(同一行的减号、en-dash 与 ⊕) ‖ {gl2}(这两句在按版式抽取里) ‖ {aprime} ‖ {aell} ⇒ "
        u"⊕ {op} ⇎ ≤ {le} ⇎ 替换符 U+FFFD {fffd} ⇎ 非 ASCII 总个数 {na}(种类 {nak})。"
        u"三种命运同时存在: 官方 txt 原样留着; 本机两份里 ⊕ 与 ≤ 静默消失、只在原位留下空档(那一行在按版式层数得出 {glgap} 处双空格); "
        u"而减号一类既可能变成 U+FFFD 也可能直接不见(锚句里的 (x−1) 在按版式层成了 (x1)); "
        u"′ 只住在 {aprime} 那一行, 在本机两层里同样一个不剩(′ {prm}, 省略号 … {ldt}), {aell} 那行的省略号点也一样。"
        u"这 11 族(连同 U+FFFD)的码点合计 {cpna}: 本机两层的 {nal} 枚全在替换符那一项, 上面 ⊕／≤／′／… 各行的本机两列本就都是 0; "
        u"破折号码点种类 {dk}, ASCII 连字符 {yh}。"
        u"官方 txt 的 {nasc} 枚与按版式的 {nal} 枚是同一口径下的两份文件, 相减只得 {nadiff}, "
        u"而 {nadiff} 不是“丢掉的字形个数”——本机两层的 {nal} 枚非 ASCII 全是 U+FFFD。"
        u"落地页那 11 枚与这份标准的字形无关: 是页面自身的不可断空格与曲引号。", **G)

LINE(u'🧱', u"“同一行”有四级判法 ⇒ 第一级是基数本身: 官方 txt 里骨架长度 ≥{skm} 的行共 {pt2} 行; 拿这批行去按版式抽取里配——"
        u"第二级原样逐字 {tlr}, 第三级去掉行首尾空白 {tls}(多配 {g01} 行), 第四级再抹掉所有非字母数字 {tlk}(再多配 {gaptl} 行), "
        u"从原样到骨架共多配 {dtl} 行; 无版式层 {pTP}, 落地页 {pTH}, 到骨架这一级的步增依次是 {gaptl} ⇎ {gaptp} ⇎ {gapth}。多出来那些行是“话还是那句话, 字已经不是那些字”: "
        u"例如 {atdash} 在按版式层成了 {adash}——官方 txt 在这一处写作一个破折号, 本机两层各写作两个连字符, 逐字判不上而抹平后判得上。"
        u"四级命中数逐级不减, 这条单调性由同一份 {pt2} 行基数当场校住。", **G)

LINE(u'🧲', u"词集的包含关系随分词口径翻牌 先分词 {ws} ⇎ 先压掉全部空白再分词 {wsb} ⇒ "
        u"口径一: 官方 txt 独有 {oat} 个、按版式抽取独有 {oal} 个(前者是后者的子集); "
        u"口径二: 官方 txt 独有 {obt} 个、按版式独有 {obl} 个——同一个“独有”换了口径就从 {oat} 跳到 {obt}。"
        u"落地页与官方 txt 的词集交只有 {ith}(按版式层与它是 {itl}, 无版式层与它是 {itp}, 两抽取层之间 {ilp}), "
        u"它的词汇总数 {absw} 也说明它不是正文。", **G)

LINE(u'🖼', u"落地页的“正文”取决于算不算属性 {atitle} ‖ {adata} ‖ {aframe} ⇒ 整份文件 {ht} 枚标签／{htk} 种／锚 {ha} 枚／图 {himg} 张／src {hsrc} 处／外链 {hext} 处; "
        u"把标签连同属性一起去掉再数: uswds {usw}, DOI {doi2}, SHA3 {sha3h}。"
        u"uswds 在文件里出现 9 次而正文里 0 次——它只住在 class 与 src 的值里; 页面另用 Date Published 字段写日期({pub} 处), "
        u"而正文三种序列化都写作 August 2015。"
        u"八个关键词家族(algorithm／fips／keccak／nist／sha3／shake／sponge／step)在整份文件 {kwr} 次、去标签正文 {kwb} 次, {kwl} 次随标签一起被删掉——单看 fips 字样是 {fpr} ⇎ {fpb}; {aredir} 这类告警行只住在容器里。", **G)

LINE(u'📐', u"结构计数在同一份标准里给出四组数 Algorithm {ap} ⇎ Step {asp} ⇎ Figure {af} ⇎ Table {at} ⇎ Appendix 字样 {aap} ⇒ "
        u"算法号种类 {sa}, 最大号 {almx}: 三层抽取的算法号集合完全一致, 落地页只提到一个号。"
        u"Step 引用在无版式层多出 {stpd} 处, 成因当场可查: 把模式放宽成“Step＋任意空白＋数字”后四层是 {sof}, "
        u"官方 txt 里被折行切开(行尾停在 Step, 编号落在下一行)的正是 {swr} 处, 无版式层把它们并回一行, 严格模式因此多数出一处。"
        u"版面与合并的证据: {stab}(按版式独有的表头行) ‖ {salg}(无版式独有的并行) ‖ {astep}(并回来的那一处) ‖ {st2} ‖ {atab}。", **G)

LINE(u'🧵', u"版式留下的痕迹可以数 {acol} ‖ {ashake} ‖ {amast}(抬头三行被并成一行) ‖ 断栏 {mc} ⇎ 超 72 字行 {w72} ⇎ 页首页眉 {ph} ⇒ "
        u"三空格以上断栏的行: 官方 txt 只有 1 行, 按版式抽取 {mcl} 行——那是双栏页被拉直后剩下的空档, 上一句的锚就是它造出来的; "
        u"而“FIPS PUB 202”在三种文本序列化里各只出现在行首 {phv} 次、在落地页 {phh} 次, 这份 PDF 有 {pp} 页／{ps} 个流——每页是否都印着页眉不可由在库文件判定, "
        u"“数页眉校页数”这种想当然在这里不成立。", **G)

LINE(u'⏳', u"时间与出处在四层的写法 August 2015 {aug} ⇎ DOI 串 {doi} ⇎ 网页字段 {pub} ⇒ "
        u"DOI 在三种文本层各 {doit} 次({adoi}), 参考文献的 URL 同样留到三层({aurl}), 但它在落地页正文 0 次、在整份文件里 {doih} 次(住在 href 里)。"
        u"折叠空白后的最长公共片段(四段依序为 按版式⇎官方、无版式⇎官方、落地页⇎官方、两抽取层之间): 段数 {rp} ⇎ 合计字符 {rt} ⇎ 最长 {rx} ⇎ 占该层比例 {rs}, "
        u"落地页对官方 txt 只占 {rsh}, 而两份本机抽取之间占 {rsp}——它抄的是摘要那几句, 不是正文。", **G)

LINE(u'🗂', u"同名穿层: {hitk} 枚关键串按两种口径判 {hcal}(归一后子串 ⇎ 归一函数会抹成空串的字形改判原样), "
        u"命中四层 {h4} 枚 ⇎ 命中二三层次多层 {hl3} 枚 ⇎ 只命中单层 {h1} 枚 ⇎ 一枚不中 {hn} 枚。"
        u"单层的三枚里两枚是 ⊕ 与 π——若不披露这层口径, 空串对谁都算命中, 单层就数不出 3 枚; "
        u"零层那枚是 uswds(矩阵按去标签正文判, 它在整份文件⇎正文 {usw} 次); 四层的 {h4} 枚在注里逐枚列出, 都是标题、DOI、算法名这类骨架词。"
        u"口径披露两笔: 穿层矩阵对四层都用去标签正文, 而正文锚的命中判定对落地页改用原文件的行——去标签后并成一段的话在原文件里被标签切成几处, 两种口径都写在这里, 不留给读者猜。", **G)

LINE(u'🧪', u"这条的可核事实分三档 {gl} ‖ {aframe} ‖ {adoi} ⇒ 第一档 B53V 可复算: 四份源的字节/行/行长/词集两级口径/码点存活表/"
        u"骨架四级配对/结构计数与折行成因/穿层矩阵/关键词家族两种正文, 以及本机两份重跑两遍字节相同(命令两条; 入门槛的只有“两遍字节相同”这一句, 抽取器版本与产物 sha 只进注)。"
        u"第二档只能对账不能对源: 官方两份与本机产物互不相同核得动, “它们与官网现在那份相同”核不动。"
        u"第三档不可核, 也是本条与 B48 的分界: ⊕ 在 PDF 里本来是什么(字体码位还是图形对象)、"
        u"哪一种序列化才算这份标准的正文——库里只有 {pp} 页与 {ps} 个流的字节统计, 没有渲染物, "
        u"所以这句话写进判词而不写成待核, 门槛里没有一项替它背书。"
        u"锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 {nat} 处／{ndist} 条去重串, "
        u"命中列分布是一源 {nsgl} ⇎ 多源 {ncross} ⇎ 四源 {nall}, 每条去重串对四份源逐一判成员共 {checked} 次检查, 错配 {aerr} 处; "
        u"归属由正文现推, 不由旁注文件说了算。", **G)

LINE(u'∴', u"骨架 ⇒ ① 四源 {by} 字节 ⇎ 非空行 {nb} ⇎ 行 {ly}, 中位行长 {med}, 最长行 {maxl}; "
           u"② 官方 txt 的 {pt2} 个骨架行在按版式层原样 {tlr} ⇎ 去空白 {tls} ⇎ 骨架 {tlk}(逐级多配 {g01}⇎{gaptl}), 在无版式层 {tpk}, 在落地页 {thk}; "
           u"③ 字形只在官方 txt 活着: ⊕ {opv} ⇎ ≤ {lev} ⇎ 非 ASCII 种 {nak}, 本机两份换成替换符 {fffd}; "
           u"④ 词集包含关系随口径翻牌: 官方 txt 独有由 {oat} 变 {obt}, 落地页与正文词交 {ith}; "
           u"⑤ 落地页的正文随算不算属性而变: uswds {usw} ⇎ DOI {doi2} ⇎ SHA3 {sha3h}, 标签 {ht} 枚, 八个关键词家族随标签丢掉 {kwl} 次; "
           u"⑥ 结构计数三层一致({sa} 种／最大号 {almx})而 Step 层多 {stpd} 处(放宽空白后 {sof}, 被折行切开 {swr} 处), 断栏行 {mcl} ⇎ 页首页眉 {ph}; "
           u"⑦ 本机两份重跑字节相同({gen} 份), 官方两份无此证据({dl} 份), 四份 sha 全不同({sd}); "
           u"⑧ {hitk} 枚关键串穿层 {h4}⇎{hl3}⇎{h1}⇎{hn}, 口径两式 {hcal}。"
           u"判词: 一份文件“是什么”在四种序列化里没有单一答案——行数、行长、分页、词集包含、符号存活全部随抽取器改口; "
           u"能确定的只有可复算的那部分: 同一句话逐字对不上的行数、同一码点在四层各剩几个、以及本机产物重跑仍字节相同。", **G)

LINE(u'ℒ', u"方法 ⇒ 读“同一份文件的几种序列化”先定口径再读数: 每个数都写清三件事——在哪一层数、算不算标签与属性、"
        u"逐字还是抹平后逐字。本条把“同一行”拆成四级(原样⇎去空白⇎抹非 ASCII⇎骨架长度门槛), 单调性当场可查。"
        u"第二步给符号单独建码点表: 不数“有没有丢”, 而是逐码点数它在四层各剩几个, 于是同一行的三种命运(原样／替换符／静默空档)分得开。"
        u"第三步把容器与内容分开: 落地页只抄摘要这件事用词集交 {ith}、骨架配对 {thk}(这 {thk} 行的页眉／正文之分见注)、公共片段占比 {rsh} 三种独立量各说一遍, 不用一个比例糊过去。"
        u"第四步给不可核留位置并写成因(PDF 的符号表示不在库内), 顺手记下四份文件的 sha 互不相同——"
        u"“同一份标准”是内容层的主张, 不是文件层的事实。", **G)

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 四份源各自 {ch} 字符, 窗口只能取锚点触到的行; "
        u"而本条的结论全是跨层量: 骨架四级配对的 ladder、11 个码点在四层的存活表、落地页对正文的三种重合率({thk}／{ith}／{rsh})。"
        u"尤其 {pt2} 行的四级配对与码点命运表, 任何单窗口都装不下它们的对照。"
        u"读它请按“这个数是在哪一层、用哪种逐字口径数出来的”来读, 而不是按“少抄了多少原文”。", **G)

body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([TLPH])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FA[IDX[x[0]]]]
HITC = dict((a, hitset(a)) for a in ANCH)
CLS = dict((c, len([a for a in ANCH if cls_of(HITC[a]) == c])) for c in (u'single', u'cross', u'all4'))
AMETA = {u'anchor_total': len(CITES), u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'],
         u'anchor_all4': CLS[u'all4'], u'checks': DIST * 4}
assert not ERR, ERR[:3]
for k, v in sorted(AMETA.items()):
    reg(str(v), u"B53V('%s')" % k, TOKV.get(k, k))
for n in (u'anchor_total', u'anchor_distinct', u'anchor_single', u'anchor_cross',
          u'anchor_all4', u'checks', u'anchor_err'):
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
assert u'◘' not in body, u'锚统计量占位符未回填'
assert sum(CLS[c] for c in (u'single', u'cross', u'all4')) == DIST
DERIV = dict((k, v[0]) for k, v in K.items())
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(os.path.join(ROOT, C, u'_deriv53.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(os.path.join(ROOT, C, u'_b53flat.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(os.path.join(ROOT, C, u'_atoms53.txt'), 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[TLPH]⟧', body)),
      u'classes': dict((c, [a for a in sorted(ANCH) if cls_of(HITC[a]) == c])
                       for c in (u'single', u'cross', u'all4')),
      u'collisions': COLL, u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV), u'notes': NOTES,
      u'pool_used': len(set(USEDATOM) & set(ANCH)), u'enc_chars': len(body.replace(NL, u'')),
      u'nsrc': 4, u'flat': F}
json.dump(CH, io.open(os.path.join(ROOT, C, u'_b53checks.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

srcline = (u'src: ' + u' ⇎ '.join(u'%s (%s 字节／非空行 %s)' % (PATH[i], F[u'bytes'][i], F[u'nonblank'][i])
                                 for i in range(4)) +
           u' (本机两份由 pdftotext 现生, 重跑两遍字节相同; 官方两份为下载; 另有 raw/fips202.pdf 只作页数与流的旁证, 不作锚源)\n')
联结 = (u'；联结不是“四份材料”, 而是“同一份 FIPS 202 的四种序列化”: 官方纯文本留着 %d 个非 ASCII 字形(共 %d 种), '
        u'本机两种抽取把它们变成静默消失或 %d 枚替换符, 而官方 html 其实是只抄了摘要的落地页(与正文的骨架行配对 %d⇎%d); '
        u'“同一行”在原样／去空白／抹非 ASCII 三种口径下分别配出 %d／%d／%d 行\n') % (
    F[u'nonascii'][0], F[u'naskinds'][0], F[u'fffd'][1], F[u'pair_th_skel'], F[u'pairtotal'],
    F[u'pair_tl_raw'], F[u'pair_tl_strip'], F[u'pair_tl_skel'])
text = (u'# B53 同一份标准的四种序列化：行数、字形与词集都随抽取器改口，只有可复算的部分不变\n' + srcline + 联结 +
        u'tags: 骨架四口径配对 字形三层命运 码点存活表 词集包含随口径翻牌 落地页只抄摘要 标签与属性两种正文 '
        u'断栏痕迹 页眉非每页 本机产物字节可复现 穿层命中矩阵 归一口径须披露 锚归属由正文现推\n' +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill53.py 从 corpus/_b53checks.json 与 corpus/_b53meas.json 现算写入）\n')
io.open(os.path.join(ROOT, ENTRY), 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d 串 ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'DERIV %d 键(0 键折 %d 项) ｜ 同数冲突 %d 组' % (len(DERIV), len(ZERO), len(COLL)))
for k, n in COLL[:12]:
    print(u'  同数 %s ← %s' % (k, n))
print(u'残留未替换占位符 %d' % len(re.findall(u'\\{[a-zA-Z_0-9]+\\}', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))))
print(u'锚内拉丁 %d ｜ 锚外拉丁 %d ｜ 标签 %d 枚 ｜ 池内取用 %d ｜ 扁平键 %d 个' % (
    CH[u'letters_in'], CH[u'letters_out'], CH[u'tagn'], CH[u'pool_used'], len(F)))
