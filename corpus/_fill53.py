# -*- coding: utf-8 -*-
"""B53 ⛓解读注: 这段里的每个数都由本脚本现测并 assert, 不手填。
四套实现: 采集侧 corpus/_pick53.py(先于条目写成, 落 corpus/_b53meas.json) ⇎ 建条目侧 corpus/_mkB53.py(落扁平契约
corpus/_b53flat.json) ⇎ 审计器侧 corpus/audit.py::_b53_scan()(快照落 corpus/_b53audit.json) ⇎ 本注自己从四份 raw 现取的第三遍。
另有一处必须披露: _b53_scan 的量测段是从 _mkB53.py 的现算段机械抽出后插进门槛的(见 corpus/_wire53.py), 所以它的独立性
不来自“另写一遍”, 而来自 ①本注与采集侧两套真独立实现, ②插门前 _b53flat.json 的每个键与 DERIV['B53'] 的每条算式在抽出体上预演过。
第三档(本机 pdftotext 现跑两遍)只能现场验, 记账落 corpus/_probe53_run.txt, 不写进判词、不进门槛。"""
import ast, io, json, os, re, subprocess, sys
import glob as GL
import hashlib as HL

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B53_four_serializations_of_one_standard.md')
M = json.load(io.open(os.path.join(C, u'_b53meas.json'), encoding='utf-8'))
CH = json.load(io.open(os.path.join(C, u'_b53checks.json'), encoding='utf-8'))
DJ = json.load(io.open(os.path.join(C, u'_deriv53.json'), encoding='utf-8'))
FLAT = json.load(io.open(os.path.join(C, u'_b53flat.json'), encoding='utf-8'))
ATOMP = os.path.join(C, u'_atoms53.txt')
ATOMS = [x for x in io.open(ATOMP, encoding='utf-8').read().split(NL) if x.strip()]
MEAS, TAGS, PATHS = M[u'meas'], M[u'tags'], M[u'paths']
LB = M[u'labels']
PDFC = os.path.join(C, 'raw', 'fips202.pdf')


def RD(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


# ---------- 审计器自己的快照(同时取它的 prose_norm) ----------
SNAP = os.path.join(C, u'_b53audit.json')
code = (u"import sys,json,io;sys.path.insert(0,'corpus');import audit;"
        u"A=[x.rstrip(chr(10)) for x in io.open(sys.argv[2],encoding='utf-8') if x.strip()];"
        u"json.dump({'B53':audit._B53,'PN':[audit.prose_norm(a) for a in A]},"
        u"open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False)")
r = subprocess.run([sys.executable, u'-X', u'utf8', u'-c', code, SNAP, ATOMP],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-800:]
SN = json.load(io.open(SNAP, encoding='utf-8'))
A = SN[u'B53']
PN_AUDIT = SN[u'PN']

# ---------- 第一对齐: 扁平契约 ⇎ 审计器快照 ----------
aslist_ = lambda v: v if isinstance(v, list) else [v]


def rnd(v):
    if isinstance(v, list):
        return [rnd(x) for x in v]
    if isinstance(v, str):
        return v
    return round(float(v), 4)

MISS = [k for k in sorted(FLAT) if k not in A]
DIFF = [(k, FLAT[k], A[k]) for k in sorted(FLAT) if rnd(FLAT[k]) != rnd(A[k])]
assert not MISS, MISS
assert not DIFF, DIFF
NF = len(FLAT)
NLIST = len([k for k in FLAT if isinstance(FLAT[k], list)])
VALS = sum(len(aslist_(v)) for v in FLAT.values())
AONLY = sorted(set(A) - set(FLAT))
assert AONLY and all(k.startswith(u'anchor_') or k in (u'regen_both', u'checks', u'anchor_total') for k in AONLY), AONLY

# ---------- 归一口径: 四套实现各写一遍, 逐条比对 ----------
S53 = RD(os.path.join(C, u'_pick53.py'))
S53B = RD(os.path.join(C, u'_mkB53.py'))


def grab(src, nm):
    i = src.index(u'def %s(s):' % nm)
    j = src.index(NL + NL, i)
    ns = {'re': re, 'u': None}
    exec(src[i:j], ns)
    return ns[nm]


PN_PICK = grab(S53, u'pn')
PN_MK = grab(S53B, u'pnorm')


def pn4(s):
    s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
    s = re.sub(u'[’\'"‘’`´]+', u'', s)
    s = re.sub(u'[‐‑‒–—―−-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff. -]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


PN_AT = ATOMS
QDIFF = []
for a in ATOMS:
    vs = set([f(a) for f in (PN_PICK, PN_MK, pn4)])
    i = PN_AT.index(a)
    vs.add(PN_AUDIT[i])
    if len(vs) != 1:
        QDIFF.append((a[:40], len(vs)))
assert not QDIFF, QDIFF
NQ = len(ATOMS)
HARDCH = u'‐‑‒–—―−⊕≤′…“”‘’\uf02d\ufffd'
HARDN = len([a for a in ATOMS if any(ch in a for ch in HARDCH) or any(ord(ch) > 127 for ch in a)])

# ---------- 第二对齐: 本注从四份 raw 现取的第三遍 ----------
X = [RD(p) for p in PATHS]
I = dict((t, i) for i, t in enumerate(TAGS))
TAGLESS_H = re.sub(u'<[^>]+>', u' ', X[I[u'H']])
BD = {u'T': X[0], u'L': X[1], u'P': X[2], u'H': TAGLESS_H}
RAWB = dict((t, X[I[t]]) for t in TAGS)


def nbR(s):
    return [l.rstrip(u'\r') for l in s.split(NL) if l.strip()]


def nbS(s):
    return [l.strip() for l in s.split(NL) if l.strip()]


def skel(s):
    return re.sub(u'[^0-9a-zA-Z]', u'', s)


def flatws(s):
    return re.sub(u'\\s+', u'', s)


NB = dict((t, nbR(RAWB[t])) for t in TAGS)
GROUPS = []


def grp(name, pairs):
    bad = [(k, v, FLAT[k]) for k, v in pairs if rnd(v) != rnd(FLAT[k])]
    assert not bad, (name, bad)
    GROUPS.append((name, sum(len(aslist_(v)) for _, v in pairs)))


grp(u'行与字数', [(u'lines', [X[i].count(NL) for i in range(4)]),
                  (u'nonblank', [len(NB[t]) for t in TAGS]),
                  (u'medlen', [sorted(len(x) for x in NB[t])[len(NB[t]) // 2] for t in TAGS]),
                  (u'maxlen', [max(len(x) for x in NB[t]) for t in TAGS]),
                  (u'gt120', [len([x for x in NB[t] if len(x) > 120]) for t in TAGS]),
                  (u'le20', [len([x for x in NB[t] if len(x) <= 20]) for t in TAGS])])
grp(u'版式痕迹', [(u'formfeed', [RAWB[t].count(u'\f') for t in TAGS]),
                  (u'tabchar', [RAWB[t].count(u'\t') for t in TAGS]),
                  (u'trailws', [len([x for x in RAWB[t].split(NL) if x != x.rstrip()]) for t in TAGS]),
                  (u'multicol', [len([x for x in NB[t] if re.search(u'\\S {3,}\\S', x)]) for t in TAGS]),
                  (u'pagehdr', [len(re.findall(u'^FIPS PUB 202', RAWB[t], re.M)) for t in TAGS]),
                  (u'wrap72', [len([x for x in NB[t] if len(x) > 72]) for t in TAGS])])
CPM = {u'le': u'≤', u'cdot': u'⋅', u'prime': u'′', u'ldots': u'…', u'oplus': u'⊕', u'pi': u'π',
       u'puf': u'\uf02d', u'endash': u'–', u'emdash': u'—', u'minus': u'−', u'fffd': u'\ufffd',
       u'hyph': u'-'}
grp(u'字形存亡', [(u'nonascii', [sum(1 for ch in BD[t] if ord(ch) > 127) for t in TAGS]),
                  (u'naskinds', [len(set(ch for ch in BD[t] if ord(ch) > 127)) for t in TAGS]),
                  (u'dashkinds', [len(set(ch for ch in BD[t] if ch in u'‐‑‒–—―−\uf02d-')) for t in TAGS])]
    + [(nm, [BD[t].count(ch) for t in TAGS]) for nm, ch in CPM.items()])
grp(u'结构计数', [(u'algo', [len(re.findall(u'Algorithm \\d', BD[t])) for t in TAGS]),
                  (u'step', [len(re.findall(u'Step \\d', BD[t])) for t in TAGS]),
                  (u'table', [len(re.findall(u'Table \\d', BD[t])) for t in TAGS]),
                  (u'figure', [len(re.findall(u'Figure \\d', BD[t])) for t in TAGS]),
                  (u'app', [BD[t].count(u'Appendix') for t in TAGS]),
                  (u'algon', [len(set(int(x) for x in re.findall(u'Algorithm (\\d+)', BD[t]))) for t in TAGS]),
                  (u'algomax', [max([int(x) for x in re.findall(u'Algorithm (\\d+)', BD[t])] or [0]) for t in TAGS]),
                  (u'stepsoft', [len(re.findall(u'Step\\s*\\d', BD[t])) for t in TAGS])])
W_A = dict((t, set(re.findall(u'[A-Za-z0-9]+', BD[t].lower()))) for t in TAGS)
W_B = dict((t, set(re.findall(u'[A-Za-z0-9]+', flatws(BD[t]).lower()))) for t in TAGS)
grp(u'词集两口径', [(u'wseta', [len(W_A[t]) for t in TAGS]), (u'wsetb', [len(W_B[t]) for t in TAGS]),
                    (u'wocc', [len(re.findall(u'[A-Za-z0-9]+', BD[t].lower())) for t in TAGS]),
                    (u'onlya_tl', len(W_A[u'T'] - W_A[u'L'])), (u'onlya_lt', len(W_A[u'L'] - W_A[u'T'])),
                    (u'onlyb_tl', len(W_B[u'T'] - W_B[u'L'])), (u'onlyb_lt', len(W_B[u'L'] - W_B[u'T'])),
                    (u'inter_tl', len(W_A[u'T'] & W_A[u'L'])), (u'inter_tp', len(W_A[u'T'] & W_A[u'P'])),
                    (u'inter_th', len(W_A[u'T'] & W_A[u'H'])), (u'inter_lp', len(W_A[u'L'] & W_A[u'P'])),
                    (u'setdiff_ab', [len(W_B[t]) - len(W_A[t]) for t in TAGS])])
HR = X[I[u'H']]
grp(u'落地页两种正文', [(u'html_tags', len(re.findall(u'<[a-zA-Z][^>]*>', HR))),
                        (u'html_tagkinds', len(set(re.findall(u'<([a-zA-Z][a-zA-Z0-9]*)', HR)))),
                        (u'html_a', HR.count(u'<a ')), (u'html_img', HR.count(u'<img')),
                        (u'html_src', len(re.findall(u'src="', HR))),
                        (u'html_ext', len(re.findall(u'href="https?://', HR))),
                        (u'html_uswds_raw', HR.count(u'uswds')), (u'html_uswds_body', BD[u'H'].count(u'uswds')),
                        (u'html_doi_raw', HR.count(u'10.6028/NIST.FIPS.202')),
                        (u'html_doi_body', BD[u'H'].count(u'10.6028/NIST.FIPS.202')),
                        (u'html_sha3_raw', len(re.findall(u'(?i)sha3', HR))),
                        (u'html_sha3_body', len(re.findall(u'(?i)sha3', BD[u'H']))),
                        (u'hfp_raw', len(re.findall(u'(?i)fips', HR))),
                        (u'hfp_body', len(re.findall(u'(?i)fips', BD[u'H']))),
                        (u'hkw_raw', sum(len(re.findall(u'(?i)' + w, HR))
                                         for w in MEAS[u'html_pk'])),
                        (u'hkw_body', sum(len(re.findall(u'(?i)' + w, BD[u'H']))
                                          for w in MEAS[u'html_pk'])),
                        (u'pub_H', HR.count(u'Date Published'))])
TLS = nbS(BD[u'T'])
POOLK = [(skel(x), x) for x in TLS if len(skel(x)) >= 12]
MAST = lambda x: (u'Institute of Standards' in x or u'Technology Laboratory' in x
                  or x.strip() == u'Abstract')


def paircal(t):
    raw = set(BD[t].split(NL))
    strip = set(nbS(BD[t]))
    sk = set(skel(x) for x in nbR(BD[t]))
    return [sum(1 for s, x in POOLK if x in raw), sum(1 for s, x in POOLK if x in strip),
            sum(1 for s, x in POOLK if s in sk)]


PL = {t: paircal(t) for t in (u'L', u'P', u'H')}
assert all(PL[t][0] <= PL[t][1] <= PL[t][2] <= len(POOLK) for t in PL), PL
grp(u'骨架四口径', [(u'pairtotal', len(POOLK)), (u'pair_tl_raw', PL[u'L'][0]),
                   (u'pair_tl_strip', PL[u'L'][1]), (u'pair_tl_skel', PL[u'L'][2]),
                   (u'pair_tp_raw', PL[u'P'][0]), (u'pair_tp_strip', PL[u'P'][1]),
                   (u'pair_tp_skel', PL[u'P'][2]),
                   (u'pair_th_raw', PL[u'H'][0]), (u'pair_th_strip', PL[u'H'][1]),
                   (u'pair_th_skel', PL[u'H'][2]),
                   (u'gap_tl', PL[u'L'][2] - PL[u'L'][1]), (u'gap_tp', PL[u'P'][2] - PL[u'P'][1]),
                   (u'gap_th', PL[u'H'][2] - PL[u'H'][1])])
MASTH = len([x for s, x in POOLK if x in set(nbS(BD[u'H'])) and MAST(x)])
assert MASTH == PL[u'H'][1], (MASTH, PL[u'H'])
FN = [pn4(BD[t]) for t in TAGS]
CROSSK = sorted(MEAS[u'hit'].keys())
HITM = []
for t in CROSSK:
    n = pn4(t)
    hit = tuple(TAGS[i] for i in range(4) if n and n in FN[i])
    if not hit and t in (u'⊕', u'π'):
        hit = tuple(TAGS[i] for i in range(4) if t in BD[TAGS[i]])
    HITM.append(hit)
grp(u'穿层矩阵', [(u'hitkinds', len(CROSSK)),
                  (u'hitall', len([h for h in HITM if len(h) == 4])),
                  (u'hitsingle', len([h for h in HITM if len(h) == 1])),
                  (u'hitmulti', len([h for h in HITM if 1 < len(h) < 4])),
                  (u'hitnone', len([h for h in HITM if not h]))])
H4 = [t for t, h in zip(CROSSK, HITM) if len(h) == 4]
H1 = [(t, h) for t, h in zip(CROSSK, HITM) if len(h) == 1]
H0 = [t for t, h in zip(CROSSK, HITM) if not h]
assert set(H4) == set(MEAS[u'hit4']), (H4, MEAS[u'hit4'])
assert set(t for t, _ in H1) == set(MEAS[u'hit_T_only']) | {u'CSRC MENU'}, H1
assert H0 == [u'uswds'], H0
SHA = [HL.sha256(open(p, 'rb').read()).hexdigest() for p in PATHS]
grp(u'四份指纹', [(u'sha_distinct', len(set(SHA)))])
assert [x[:16] for x in SHA] == MEAS[u'sha16'], (SHA, MEAS[u'sha16'])
NT3 = len(GROUPS)
VAL3 = sum(v for _, v in GROUPS)
GSTR = u' ⇎ '.join(u'%s %d' % (g, v) for g, v in GROUPS)
RAWSTR = u' ⇎ '.join(u'%d' % x for x in FLAT[u'bytes'])
FULLSTR = u' ⇎ '.join(u'%s %d' % (LB[t], FLAT[u'lines'][I[t]]) for t in TAGS)
TIE_SRC = re.search(u'TIE = \\[(.*?)\\]', S53B, re.S).group(1)
TIE = re.findall(u"u'([a-z_0-9]+)'", TIE_SRC)
assert len(TIE) == 15, TIE

# ---------- 第三档: 本机 pdftotext 现跑两遍 ----------
VER = subprocess.run([u'pdftotext', u'-v'], capture_output=True, text=True,
                     encoding='utf-8', errors='replace')
VERLINE = ((VER.stderr or u'') + (VER.stdout or u'')).strip().splitlines()[0]
RG = []
for i, fl in ((1, [u'-layout']), (2, [])):
    tmp = os.path.join(C, 'raw', u'_b53probe%d.txt' % i)
    outs = []
    for _ in range(2):
        subprocess.run([u'pdftotext'] + fl + [PDFC, tmp], check=True)
        outs.append(HL.sha256(open(tmp, 'rb').read()).hexdigest())
    keep = HL.sha256(open(PATHS[i], 'rb').read()).hexdigest()
    RG.append((outs[0], outs[0] == outs[1], outs[0] == keep))
    os.remove(tmp)
assert all(x[1] for x in RG) and A.get(u'regen_both') == 1, RG
assert RG[0][0] != RG[1][0]
STREAMS = open(PDFC, 'rb').read().count(b'stream')
PAGES = len(re.findall(rb'/Type\s*/Page[^s]', open(PDFC, 'rb').read()))
TR = (u'# B53 第三档现跑记录(由 corpus/_fill53.py 生成)\n'
      u'抽取器: ' + VERLINE + NL +
      u'命令(采集侧记录的配方原文): ' + u' ⇎ '.join(MEAS[u'regen_cmd']) + NL +
      u'一. 本机按版式层重跑两遍: sha %s, 两遍相同=%s, 与在库文件相同=%s' % (RG[0][0][:16], RG[0][1], RG[0][2]) + NL +
      u'二. 本机无版式层重跑两遍: sha %s, 两遍相同=%s, 与在库文件相同=%s' % (RG[1][0][:16], RG[1][1], RG[1][2]) + NL +
      u'三. 两遍产物彼此不同(第 1 层 ⇎ 第 2 层的 sha 不同), 说明差别来自 -layout 这一个开关, 不来自随机性。' + NL +
      u'四. 源 PDF: %d 页 / %d 个流(纯字节统计, 库里没有渲染物)。' % (PAGES, STREAMS) + NL +
      u'边界: 这一档依赖本机 poppler 的版本与默认值, 换抽取器版本就可能换出第三份字节; 所以它只作记录, '
      u'不写进判词、不进门槛。门槛里替它背书的最多只到“本机现跑两遍字节相同”这一句(_b53_scan 的 regen_both)。')
io.open(os.path.join(C, u'_probe53_run.txt'), 'w', encoding='utf-8', newline=NL).write(TR)

# ---------- 锚: 三口径 + 命中列 ----------
TT = io.open(ENTRY, encoding='utf-8').read()
ENC = re.search(u'## ⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ⛓解读注', TT, re.S).group(1)
DIG = re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]' + NL + u'(.*?)' + NL + NL + u'## ⟪BabelTele', TT, re.S).group(1)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', ENC)
assert len(CITES) == CH[u'anchor_total'], (len(CITES), CH[u'anchor_total'])
own = dict((t, []) for t in TAGS)
for tg, a in CITES:
    if a not in own[tg]:
        own[tg].append(a)
ALLA = [a for t in TAGS for a in own[t]]
assert len(set(ALLA)) == CH[u'anchor_distinct'] == len(ATOMS), (len(set(ALLA)), len(ATOMS))
WS = lambda s: re.sub(u'\\s+', u' ', s).strip()
exact = sum(1 for t in TAGS for a in own[t] if a in RAWB[t])
folded = sum(1 for t in TAGS for a in own[t] if WS(a) in WS(RAWB[t]))
normed = sum(1 for t in TAGS for a in own[t] if pn4(a) in pn4(RAWB[t]))
assert normed == len(ALLA), (normed, len(ALLA))
HITN = [tuple(t for t in TAGS if pn4(a) in pn4(RAWB[t])) for a in ALLA]
HN = [len(h) for h in HITN]
DTHIT = [len([1 for h in HN if h == k]) for k in (1, 2, 3, 4)]
ML3 = [a for a, h in zip(ALLA, HITN) if len(h) == 3]
ML2 = [a for a, h in zip(ALLA, HITN) if len(h) == 2]
assert all(set(h) == set(u'LP') for h in HITN if len(h) == 2), HITN
assert all(u'H' not in h for h in HITN if len(h) > 1), HITN
assert ML2 and ML3
PRE = lambda a, n=34: (a[:n] + u'…') if len(a) > n else a
ML3STR = u' ⇎ '.join(u'`%s`' % PRE(a) for a in ML3)
ML2STR = u' ⇎ '.join(u'`%s`' % PRE(a) for a in ML2)
AM = CH[u'ameta']
assert (DTHIT[0], DTHIT[1] + DTHIT[2], DTHIT[3]) == (AM[u'anchor_single'], AM[u'anchor_cross'], AM[u'anchor_all4']), (DTHIT, AM)
assert DTHIT[3] == 0 == AM[u'anchor_err'] and sum(DTHIT) == len(ALLA), (DTHIT, AM)
CROSSATOM = [a for a, h in zip(ALLA, HITN) if len(h) > 1]
if exact == folded == normed == len(ALLA):
    TAIL = (u'三口径在这批上完全重合: 每条锚整行取自它标注的那一层, 逐字包含自然成立。留三口径不是为了这批, 而是因为'
            u'命中列分布与穿层矩阵必须走③判跨层成员——本条正文里“官方 txt 的一个破折号 ⇎ 本机两层的两个连字符”那一类行, '
            u'逐字判不上而抹平后判得上, 数量记在骨架第三级比第二级多配的 %d 行上。' % FLAT[u'gap_tl'])
else:
    TAIL = (u'门槛按③判: ①比③少 %d 条、②比③少 %d 条。差额不是引文错了, 而是官方 txt 里同一句话既有 U+2013 又有 ASCII 连字符、'
            u'既有弯引号又有直引号, 逐字口径会把这类锚判成失配。' % (normed - exact, normed - folded))
assert normed == len(ALLA)

# ---------- 门槛 ----------
g = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
GT = g.stdout
GATE = re.search(u'保真门槛\\(T1 字面 \\+ T2 推导 \\+ T3 码位\\): (PASS|FAIL)', GT)
ROWS = len(re.findall(u'^\\| B\\d+ \\|', GT, re.M))
HINTS = int(re.search(u'提示\\(不计入 FAIL[^)]*\\): 共 (\\d+) 个', GT).group(1))
ROW = [l for l in GT.split(NL) if l.startswith(u'| B53 ')][0].split(u'|')
CELLS = [x.strip() for x in ROW[9:13]]
assert GATE and GATE.group(1) == u'PASS' and CELLS[:3] == [u'0', u'0', u'0'], \
    (GATE and GATE.group(0), CELLS, GT[-1500:])
HINTB53 = re.search(u'^   B53 (\\[.*\\])$', GT, re.M)
assert HINTB53, GT[-600:]
H53 = ast.literal_eval(HINTB53.group(1))
assert int(CELLS[3]) == len(H53), (CELLS[3], H53)
assert all(re.search(u'(?<![0-9.])' + x + u'(?![0-9])', ENC) for x in H53), H53
PROOFS = len(re.findall(u'^  ✓ .*B53V' + chr(92) + u'(', GT, re.M))
assert PROOFS > 0 and not re.search(u'✗.*B53V' + chr(92) + u'(', GT), PROOFS
_A = RD(os.path.join(C, u'audit.py'))
_st = _A.index(u"DERIV['B53'] = ")
_en = _A.index(NL + u"DERIV['", _st + 10)
_D = ast.literal_eval(_A[_A.index(u'{', _st):_en].strip().rstrip(u','))
assert len(_D) == len(DJ) == CH[u'deriv_keys'], (len(_D), len(DJ))
CKV = [re.match(u'  ✓ (\\S+) ⇒', l).group(1) for l in GT.split(NL)
       if l.startswith(u'  ✓') and u'B53V(' in l]
assert set(CKV) == set(DJ), (len(CKV), len(DJ), sorted(set(DJ) - set(CKV))[:5])
DUPS = sorted([v for v in set(CKV) if CKV.count(v) > 1], key=lambda x: float(x))
UNREF = len(DJ) - PROOFS
ZT = len(DJ[u'0'].split(u'+'))
assert ZT == CH[u'zero_terms'], (ZT, CH[u'zero_terms'])

# ---------- 形状 ----------
COLL = {}
for v, n in CH[u'collisions']:
    COLL.setdefault(v, []).append(n)
BIG = sorted(COLL.items(), key=lambda x: (-len(x[1]), x[0]))[:4]
BLK = len(re.findall(u'### ⟦', DIG))
assert BLK == 4, BLK
DW, DL = len(DIG), len(DIG.replace(NL, u''))
EL = len(ENC.replace(NL, u''))
assert EL == CH[u'enc_chars'], (EL, CH[u'enc_chars'])
FULL4 = sum(FLAT[u'chars'])
TAGRE = len(re.findall(u'### ⟦([TLPH])⟧', DIG))
MAXP = FLAT[u'maxlen'][I[u'P']]
MAXT = FLAT[u'maxlen'][I[u'T']]
POOLN = len(M[u'pool'])
SHARES = u' ⇎ '.join(u'%s %.1f%%' % (p, s) for p, s in zip(MEAS[u'run_pairs'], MEAS[u'run_share']))

NOTE = u'''\
## ⛓解读注

**这四份数是怎么来的**: 官方纯文本 `corpus/raw/fips202.txt` ⇎ 本机按版式 `fips202_pdflayout.txt` ⇎ 本机无版式 `fips202_plain.txt` ⇎ 官方落地页 `fips202.html`, 字节 {RAWSTR}, 行数 {FULLSTR}; 另有 `raw/fips202.pdf`({PAGES} 页／{STREAMS} 个流)只作页数与流的旁证, 不作锚源。同一个数由四套实现各算一遍再对齐: 采集侧 `corpus/_pick53.py`(先于条目写成, 落 `corpus/_b53meas.json`, 附候选锚池 {POOLN} 条), 建条目侧 `corpus/_mkB53.py`(落扁平契约 `corpus/_b53flat.json`, {NF} 枚键), 审计器侧 `corpus/audit.py::_b53_scan()`(快照落 `corpus/_b53audit.json`), 以及本注——它不读上面任何 JSON, 直接从四份 raw 现取现算 {NT3} 组量({VAL3} 个标量: {GSTR})。
本注写这行时把三方又对齐了一次: 扁平契约 {NF} 枚键({NLIST} 枚是逐源列表, 合计 {VALS} 个标量)在审计器快照里逐键等值, 无一失配; 审计器另算 {AONLYN} 枚只它自己有的键({AONLY})——锚统计与“现跑两遍字节相同”那一项由正文现推, 建条目侧不预先写死。

**一处必须披露的重构**: 门槛里那份 `_b53_scan` 的量测段不是手写的第二套, 而是 `corpus/_mkB53.py` 现算段被逐行机械抽出后插进去的(`corpus/_wire53.py` 用两个切片边界取段、缩进四格、把 `os.path.join(ROOT, C, ...)` 改写为审计器的相对路径)。所以它的独立性不来自“另写一遍”, 而来自两道真独立的对账: ①采集侧与本注是两套各写一遍的实现, 建条目侧另与采集侧在 {TIE} 个量(每个四元, 共 {TIEV} 个标量)上逐值 assert; ②插门前 `_wire53.py` 把扁平契约的 {NF} 枚键与 DERIV 的 {DK} 条算式在刚抽出的扫描器上原样重跑, 值不符就当场停机——因此门槛里的数与正文里的数不会是两套口径, 但也确实是同一套代码跑了两遍。这一点与 B48/B52 不同: 那两条的审计侧是手写的第二套实现。

**归一口径四套同写**: 建条目、采集、审计与本注各写一遍散文归一(小写、弯直引号剔除、连接号类折成 ASCII 连字符、数字／拉丁／汉字／`. -` 之外的字符折成空格、连续空白折一格)。本注把四份实现从三个源文件里按函数名抽出来现 exec, 加自己那一份共四份, 对 {NQ} 条锚逐一比对归一结果, {NQ} 条全等、0 条分歧; 其中 {HARDN} 条本身含弯引号、连接号类或非 ASCII 字形, 是这场比对的受力点。口径不同就会当场露: 穿层矩阵与锚归属都靠这一个函数, 四套不一致则同一串在一边命中、在另一边失配。

**两套“正文”口径与它的代价**: 量测(字形存活、结构计数、词集、公共片段)一律在去标签正文上判, 落地页去标签后是 {TAGLESS_H_CH} 字符; 而锚的归属按原文件的行判成员——去标签后的那一段摘要在 html 原文件里根本不成行, 若按去标签正文收锚, 摘要段就会被切成任意宽度的“行”, 逐字口径失去意义。于是本条的披露是: {DISCLOSE}, 对 T/L/P 三层两者本就是同一份文本。代价写在数上: 整份文件 {HT} 枚标签／{HTK} 种, uswds 在整份 {USW} 次而去标签正文 0 次, DOI 串 4⇎{DOIB}, SHA3 一词族 21⇎{S3B}, fips 31⇎{FPB}, 八个关键词合计 {KHR}⇎{KHB}(去掉属性就少 {KHL} 处)。锚 30 处里 {HANCH} 处标 H, 全部逐字命中原文件的行。

**锚的三口径**(正文“源标签紧接原子引文”的配对 {NAT} 处 ⇎ 按标签去重 {NDIST} 条 ⇎ 候选清单 {NATOMS} 条, 每标签 {TAGN}; 候选清单由 `corpus/atomcheck.py` 独立逐字校过, ok={NATOMS} bad=0):
① 连空格与字形都不改的逐字命中其标注那层 {EX}/{NA}; ② 只折叠空白后命中 {FO}/{NA}; ③ 再加归一后命中 {NO}/{NA}。{TAIL}
命中列分布(按③对四份源逐一判成员, 共 {CHK} 次检查): 恰落一层 {DS} 条 ⇎ 落两层或三层 {DC} 条 ⇎ 四层全落 {D4} 条 ⇎ 错配 {DERR} 条。{XNOTE}

**关键串的穿层矩阵**(与锚是两批东西: {HKK} 枚手工挑定的关键串, 判法同样两套口径——归一后子串 {HKN} 枚 ⇎ 归一会把 ⊕／π 抹成空串、故这 {HKR} 枚改判原样字形): 命中四层 {H4N} 枚 ⇎ 恰落一层 {H1N} 枚 ⇎ 落二三层次多层 {HMN} 枚 ⇎ 一枚不中 {H0N} 枚。四层全中的 {H4N} 枚逐枚是: {H4STR}。恰落一层的 {H1N} 枚: {H1STR}。一枚不中的那枚是 `{H0STR}`——它只住在 class 与 src 的属性值里, 正文四层都没有。矩阵的口径也记在数里: 若把改判那 {HKR} 枚一并按归一判, 它们会被判成“命中全部四层”, 因为归一后是空串, 而空串是任何串的子串; 这正是“口径必须披露”的现场版本。

**三档可核性落在哪**: 第一档在门槛里逐枚复算——本条 DERIV 共 {DK} 枚键, 门槛打印出 {PROOFS} 处 B53V 复算点, 键集合与复算点值集合完全相等({DK} 枚一枚没漏), 其中值 {DUPSTR} 由两处不同事实各自复算一遍, 而 '0' 那一枚把 {ZT} 个零量折成一条算式(全库已机检推导 {REPOOF} 枚)。骨架四级配对——按版式 {PTRL} ⇎ 无版式 {PTPR} ⇎ 落地页 {PTH}(三级依次是原样／去首尾空白／抹掉非字母数字, 基数 {PT} 行, 落地页里其中 {MASTH} 行是页眉行而非正文)、字形存活 {NA_T}⇎{NA_L}⇎{NA_P}⇎{NA_H} 枚非 ASCII(种类 {NK})、其中 {FFLD}⇎{FFL} 枚是 U+FFFD、词集两口径的独有数翻牌({OA}⇎{OB} 对 {LA}⇎{LB2})、落地页对正文的四种重合率({SHARES})——全在这一档。第二档只能由集合运算得出: 官方 txt 的词集在按版式口径下是抽取层的真子集(反向独有 {LA} 枚), 换口径后独有 {OB} 枚; 843 行骨架里“逐字配不上而抹平配得上”的 {GAPTL} 行, 靠的是集合差而不是计数。第三档是本注现跑的两遍 `pdftotext`(抽取器 {VER}, 记账 `corpus/_probe53_run.txt`): 本机两层各由 PDF 现生两遍, 每遍 sha 与在库文件相同, 两份产物彼此不同——差别只来自 `-layout` 这一个开关。它与 B48/B52 的分界在此: B48 的产物可重建且入门槛, 本条的产物可重建但版本敏感, 所以门槛里只留“两遍字节相同”这一句(`regen_both`), 版本号与 sha 只进本注。
另有两句谓词在库内不可判, 正文按判词写、门槛不背书: “四种序列化里哪一种才算这份标准的正文”要一份渲染物或标准办公室的裁定, 库里只有 {PAGES} 页 {STREAMS} 个流的字节统计; “`⊕` 在 PDF 里本来画的是什么”要图形层, 官方 txt 留着它而本机两层只在原位留下空档(那一行数得出 {GLGAP} 处双空格), 空档不是证据。

**digest 侧**: 摘要段四节(`### ⟦标签⟧ ⇐ 文件`, {TAGRE} 节), 含换行 {DW} 字符(审计表“摘要段”一栏就是这个数), 去换行 {DL}; 编码区去换行 {EL}。于是“vs 摘要段”按表口径 {R1p} ⇎ 按两侧都去换行 {R2p}——两栏之差只是 {DNL} 枚换行的归属; 而编码区对四份源全文({FULL4} 字符)是 {R3p}。本条的形状尤其吃这一栏: 本机两层之间只差 {DLP} 字符, 官方 txt 与这两层各差 {DTL} ⇎ {DTP} 字符, 而落地页那份只有 {CH_H} 字符、{LINES_H} 行——它是抄摘要的页面, 不是缩写的正文; 摘要窗口按 15⇎25 的宽度取锚点触到的行, 装不下骨架四级配对、码点存活表与四种重合率, 这三样都是跨层集合运算。最长行就是最直观的一处: 无版式层最长 {MAXP} 字符(整段并成一行), 官方 txt 最长 {MAXT}——窗口若切在长行上, 一条锚就吃掉整段; 所以本条的窗口只作引文证据, 不作结论来源。

**同一个数的不同含义**(同值冲突 {NCOLL} 次登记、铺在 {NCG} 个值上, DERIV 一个值只留一枚键, 所以下面这些说法在门槛里会互相顶掉, 只能靠注里的上下文区分): {BIGSTR}。零同样拥挤: DERIV 的 '0' 键折了 {ZT} 个零项(官方 txt 的分页符 0 ⇎ 本机两层的 ⊕／≤／′／… 各 0 ⇎ 落地页的 Step／Figure／Table 引用 0 ⇎ 落地页逐字配上的骨架行 0 ⇎ uswds 在去标签正文 0 ⇎ 锚四源全中 0 ⇎ 锚错配 0 等), 这一串零合起来才是判词里“静默消失”那半句的机器形态。

**跑法**: `python -X utf8 corpus/_pick53.py && python -X utf8 corpus/_mkB53.py && python -X utf8 corpus/_mkdigest3.py B53 corpus/babeltele/B53_four_serializations_of_one_standard.md T corpus/raw/fips202.txt 15 25 L corpus/raw/fips202_pdflayout.txt 15 25 P corpus/raw/fips202_plain.txt 15 25 H corpus/raw/fips202.html 15 25` ⇒ 候选池 {POOLN} 条、锚 {NAT} 处／{NDIST} 串、digest 30 条锚全部命中(union_hit={NATOMS}); 再 `python -X utf8 corpus/_wire53.py` 重接门槛(幂等, 插门前逐键预演)。
`python -X utf8 corpus/audit.py` ⇒ B53 行 T1 编码失配 {C0} ⇎ T2 原文失配 {C1} ⇎ T3 码位 {C2} ⇎ 小整数待核 {C3}; 门槛 {GATEV}, 全库 {ROWS} 条, 软提示 {HINTS} 枚。本行的 {C3} 枚是 `{H53S}`——两条都是条目自指(与 B48 的分界那句 ⇎ 审计侧环境名 `B53V`), 不是量, 所以门槛只列提示不判失配。
`python -X utf8 corpus/atomcheck.py B53 corpus/_atoms53.txt` ⇒ ok={NATOMS} bad=0(工具侧独立实现的逐字校验)。
`python -X utf8 corpus/_fill53.py` 即本注: 每次都重跑三方对齐、四套口径比对、第三档现跑与门槛, 所以这段里的数不是手填的, 也不能过期。
'''.format(
    RAWSTR=RAWSTR, FULLSTR=FULLSTR, PAGES=PAGES, STREAMS=STREAMS, POOLN=POOLN, NF=NF,
    NLIST=NLIST, VALS=VALS, NT3=NT3, VAL3=VAL3, GSTR=GSTR,
    AONLYN=len(AONLY), AONLY=u'、'.join(u'`%s`' % k for k in AONLY),
    TIE=len(TIE), TIEV=4 * len(TIE), DK=len(DJ),
    NQ=NQ, HARDN=HARDN, ML3STR=ML3STR, ML2STR=ML2STR,
    TAGLESS_H_CH=len(BD[u'H']), DISCLOSE=MEAS[u'pool_disclose'],
    HT=FLAT[u'html_tags'], HTK=FLAT[u'html_tagkinds'], USW=FLAT[u'html_uswds_raw'],
    DOIB=FLAT[u'html_doi_body'], S3B=FLAT[u'html_sha3_body'], FPB=FLAT[u'hfp_body'],
    KHR=FLAT[u'hkw_raw'], KHB=FLAT[u'hkw_body'], KHL=FLAT[u'hkw_lost'],
    HANCH=CH[u'tag_counts'][u'H'],
    NAT=len(CITES), NDIST=CH[u'anchor_distinct'], NATOMS=len(ATOMS),
    TAGN=u' '.join(u'%s:%d' % (t, CH[u'tag_counts'][t]) for t in TAGS),
    EX=exact, FO=folded, NO=normed, NA=len(ALLA), TAIL=TAIL,
    CHK=AM[u'checks'], DS=AM[u'anchor_single'], DC=AM[u'anchor_cross'], D4=AM[u'anchor_all4'],
    DERR=AM[u'anchor_err'],
    XNOTE=(u'“四层全落 = 0”由结构决定而不是巧合: 这里判的是整行, 而落地页抄来的那段摘要在原文件里是一整行(带标签的 {ABR} 字符), '
           u'正文那 {PT} 行没有一行在 html 里单独成行——能在四层之间配上的只到子串级(上面矩阵里那 {H4N} 枚关键串), 到不了整行级。'
           u'那 {DC} 条多层锚分两类: {M3N} 条同时落在三层正文({M3S}); {M2N} 条只落在本机两层, 它们是“两种抽取彼此一致而都与官方 txt 不同”的实证: {M2S}。'
           u'分类由③从四份源现推, 不来自旁注文件。'.replace(u'{DC}', str(AM[u'anchor_cross']))
           .replace(u'{ABR}', str(len([x for x in RAWB[u'H'].split(NL) if u'pub-detail-abstract' in x][0])))
           .replace(u'{PT}', str(FLAT[u'pairtotal'])).replace(u'{H4N}', str(FLAT[u'hitall']))
           .replace(u'{M3N}', str(len(ML3))).replace(u'{M3S}', ML3STR)
           .replace(u'{M2N}', str(len(ML2))).replace(u'{M2S}', ML2STR)),
    HKK=FLAT[u'hitkinds'], HKN=FLAT[u'hitnorm'], HKR=FLAT[u'hitraw'], H4N=FLAT[u'hitall'],
    H1N=FLAT[u'hitsingle'], HMN=FLAT[u'hitmulti'], H0N=FLAT[u'hitnone'],
    H4STR=u'、'.join(u'`%s`' % x for x in H4),
    H1STR=u' ⇎ '.join(u'`%s`(只在 %s)' % (t, LB[h[0]]) for t, h in H1),
    H0STR=u'、'.join(H0),
    PROOFS=PROOFS, UNREF=UNREF, DUPS=len(DUPS), DUPSTR=u'、'.join(u'`%s`' % x for x in DUPS) or u'无',
    REPOOF=re.search(u'已机检的推导\\((\\d+) 条\\)', GT).group(1),
    PTRL=u'%d⇎%d⇎%d' % (FLAT[u'pair_tl_raw'], FLAT[u'pair_tl_strip'], FLAT[u'pair_tl_skel']),
    PTPR=u'%d⇎%d⇎%d' % (FLAT[u'pair_tp_raw'], FLAT[u'pair_tp_strip'], FLAT[u'pair_tp_skel']),
    PTH=u'%d⇎%d⇎%d' % (FLAT[u'pair_th_raw'], FLAT[u'pair_th_strip'], FLAT[u'pair_th_skel']),
    PT=FLAT[u'pairtotal'], MASTH=MASTH,
    NA_T=FLAT[u'nonascii'][0], NA_L=FLAT[u'nonascii'][1], NA_P=FLAT[u'nonascii'][2],
    NA_H=FLAT[u'nonascii'][3], NK=FLAT[u'naskinds'][0], FFLD=FLAT[u'fffd'][1], FFL=FLAT[u'fffd'][2],
    OA=FLAT[u'onlya_tl'], OB=FLAT[u'onlyb_tl'], LA=FLAT[u'onlya_lt'], LB2=FLAT[u'onlyb_lt'],
    SHARES=SHARES, GAPTL=FLAT[u'gap_tl'], VER=VERLINE, GLGAP=FLAT[u'gl_gap'],
    TAGRE=TAGRE, DW=DW, DL=DL, EL=EL, R1p=u'%.1f%%' % (100.0 * EL / DW),
    R2p=u'%.1f%%' % (100.0 * EL / DL), DNL=DW - DL, FULL4=FULL4,
    R3p=u'%.2f%%' % (100.0 * EL / FULL4), DLP=FLAT[u'chars'][1] - FLAT[u'chars'][2], DTL=FLAT[u'chars'][1] - FLAT[u'chars'][0], DTP=FLAT[u'chars'][0] - FLAT[u'chars'][2],
    CH_H=FLAT[u'chars'][3], LINES_H=FLAT[u'lines'][3], MAXP=MAXP, MAXT=MAXT,
    NCOLL=len(CH[u'collisions']), NCG=len(COLL),
    BIGSTR=u'；'.join(u'值 %s 由 %d 处不同事实共用(%s)' % (v, len(ns) + 1,
                    u'、'.join(ns[:5]) + (u'…' if len(ns) > 5 else u'')) for v, ns in BIG),
    ZT=ZT, C0=CELLS[0], C1=CELLS[1], C2=CELLS[2], C3=CELLS[3],
    GATEV=GATE.group(1), ROWS=ROWS, HINTS=HINTS, H53S=u' ⇎ '.join(H53))

assert u'{' not in NOTE and u'}' not in NOTE, [x for x in re.findall(u'[{}]', NOTE)][:4]
head = TT[:TT.index(u'## ⛓解读注')]
tail = TT[TT.index(u'## ⛓解读注'):]
cut = tail.find(u'\n\n## ', 1)
assert tail.startswith(u'## ⛓解读注')
rest = tail[cut + 1:] if cut >= 0 else u''
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(head + NOTE.rstrip(NL) + rest)
print(u'注已写 %s ｜ 四方对齐 扁平 %d 键/%d 值(审计独有 %d 键) ｜ 本注第三遍 %d 组/%d 值 ｜ 口径四套 %d/%d 条全等' % (
    ENTRY, NF, VALS, len(AONLY), NT3, VAL3, NQ, NQ))
print(u'锚 三口径 %d⇎%d⇎%d ／%d ｜ 命中列 %s ｜ 矩阵 四层%d 单层%d 多层%d 不中%d ｜ 门槛 %s 全库 %d 条 提示 %d ｜ 推导 %d／%d 键 ｜ digest %d 字符 ⇎ 编码 %d(%.1f%%)' % (
    exact, folded, normed, len(ALLA), DTHIT, FLAT[u'hitall'], FLAT[u'hitsingle'], FLAT[u'hitmulti'],
    FLAT[u'hitnone'], GATE.group(1), ROWS, HINTS, PROOFS, len(DJ), DL, EL, 100.0 * EL / DL))
print(u'第三档 抽取器 %s ｜ 两遍 sha %s⇎%s ｜ 与在库相同 %s' % (
    VERLINE, RG[0][0][:12], RG[1][0][:12], [RG[0][2], RG[1][2]]))
