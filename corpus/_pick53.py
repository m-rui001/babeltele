# -*- coding: utf-8 -*-
"""B53 采集(第一遍现算): 同一份 FIPS 202 的四种序列化——官方 txt(T) ⇎ 本机 pdftotext -layout(L)
⇎ 本机 pdftotext raw(P) ⇎ 官方 html(H, 实为 CSRC 落地页)。
本脚本独立实现一套量纲/词集两口径/公共片段/符号存活/穿层矩阵/分层锚池, 不复用 _probe53 的任何结果;
建条目侧 corpus/_mkB53.py 与审计侧 audit.py::_b53_scan() 各再写一遍同一套算法, 三边不符即证明失败。
可判性分档(承 B52): “哪一种序列化才是这份标准”“PDF 里符号长什么样”由本库文件判不出来, 只进解读注;
本脚本只数得出文件里有什么、本机重跑两遍字节是否相同。落 corpus/_b53meas.json / _b53meas.txt。"""
import io, os, re, sys, json, hashlib, subprocess, collections, unicodedata

sys.stdout.reconfigure(encoding='utf-8')
ROOT = u'corpus/raw'
NL = u'\n'
PDF = os.path.join(ROOT, u'fips202.pdf')
PATH = {u'T': os.path.join(ROOT, u'fips202.txt'),
        u'L': os.path.join(ROOT, u'fips202_pdflayout.txt'),
        u'P': os.path.join(ROOT, u'fips202_plain.txt'),
        u'H': os.path.join(ROOT, u'fips202.html')}
ORDER = [u'T', u'L', u'P', u'H']
CMD = {u'L': u'pdftotext -layout fips202.pdf fips202_pdflayout.txt',
       u'P': u'pdftotext fips202.pdf fips202_plain.txt',
       u'T': None, u'H': None}


def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


X = dict((k, rd(PATH[k])) for k in ORDER)
BYTES = dict((k, os.path.getsize(PATH[k])) for k in ORDER)
SHA = dict((k, hashlib.sha256(open(PATH[k], 'rb').read()).hexdigest()) for k in ORDER)
TAGS = re.findall(u'<[a-zA-Z][^>]*>', X[u'H'])
TAGLESS = re.sub(u'<[^>]+>', u' ', X[u'H'])
BODY = {u'T': X[u'T'], u'L': X[u'L'], u'P': X[u'P'], u'H': TAGLESS}
M = {}

# ---------- 1. 量纲: 同一份标准的四种“行数” ----------
def nonblank(s):
    return [l.rstrip(u'\r') for l in s.split(NL) if l.strip()]


NB = dict((k, nonblank(X[k])) for k in ORDER)
M[u'bytes'] = [BYTES[k] for k in ORDER]
M[u'chars'] = [len(X[k]) for k in ORDER]
M[u'lines'] = [X[k].count(NL) for k in ORDER]
M[u'nonblank'] = [len(NB[k]) for k in ORDER]
M[u'blank'] = [M[u'lines'][i] - M[u'nonblank'][i] for i in range(4)]
assert sum(M[u'blank']) == sum(M[u'lines'][i] - M[u'nonblank'][i] for i in range(4))
MED = dict((k, sorted(len(x) for x in NB[k])[len(NB[k]) // 2]) for k in ORDER)
M[u'linelen_med'] = [MED[k] for k in ORDER]
M[u'linelen_max'] = [max(len(x) for x in NB[k]) for k in ORDER]
M[u'lines_gt120'] = [len([x for x in NB[k] if len(x) > 120]) for k in ORDER]
M[u'lines_le20'] = [len([x for x in NB[k] if len(x) <= 20]) for k in ORDER]
M[u'lines_mid'] = [M[u'nonblank'][i] - M[u'lines_gt120'][i] - M[u'lines_le20'][i] for i in range(4)]
M[u'sha16'] = [SHA[k][:16] for k in ORDER]
M[u'sha_all_diff'] = len(set(SHA.values())) == 4

# ---------- 2. 本机两份的重跑可复现( rung-1 证据 ) ----------
REGEN = {}
TMP = os.path.join(ROOT, u'_b53tmp.txt')
for tag in (u'L', u'P'):
    flags = [u'-layout'] if tag == u'L' else []
    hs = []
    for _ in range(2):
        subprocess.run([u'pdftotext'] + flags + [PDF, TMP], check=True)
        hs.append(hashlib.sha256(open(TMP, 'rb').read()).hexdigest())
    REGEN[tag] = (hs[0] == hs[1], hs[0] == SHA[tag])
os.remove(TMP)
M[u'regen_selfequal'] = [REGEN[u'L'][0], REGEN[u'P'][0]]
M[u'regen_match_kept'] = [REGEN[u'L'][1], REGEN[u'P'][1]]
M[u'regen_cmd'] = [CMD[u'L'], CMD[u'P']]
assert all(all(REGEN[t]) for t in (u'L', u'P')), REGEN
M[u'gen_n'] = len([CMD[k] for k in ORDER if CMD[k]])
M[u'dl_n'] = 4 - M[u'gen_n']

# ---------- 3. 词集: 两个口径, 包含关系随口径翻牌 ----------
def toks(s):
    return re.findall(u'[A-Za-z0-9]+', s.lower())


def flat(s):
    return re.sub(u'\\s+', u'', s)


WA = dict((k, set(toks(BODY[k]))) for k in ORDER)
WB = dict((k, set(toks(flat(BODY[k])))) for k in ORDER)
M[u'wocc'] = [len(toks(BODY[k])) for k in ORDER]
M[u'wset_a'] = [len(WA[k]) for k in ORDER]
M[u'wset_b'] = [len(WB[k]) for k in ORDER]
M[u'inter_a'] = [len(WA[u'T'] & WA[u'L']), len(WA[u'T'] & WA[u'P']),
                 len(WA[u'T'] & WA[u'H']), len(WA[u'L'] & WA[u'P'])]
M[u'only_a'] = [len(WA[u'T'] - WA[u'L']), len(WA[u'L'] - WA[u'T']),
                len(WA[u'P'] - WA[u'L']), len(WA[u'H'] - WA[u'T'])]
M[u'only_b'] = [len(WB[u'T'] - WB[u'L']), len(WB[u'L'] - WB[u'T']),
                len(WB[u'P'] - WB[u'L']), len(WB[u'H'] - WB[u'T'])]
M[u'setdiff_ab'] = [M[u'wset_b'][i] - M[u'wset_a'][i] for i in range(4)]
M[u'tl_subset_a'] = (len(WA[u'T'] - WA[u'L']) == 0)
M[u'tl_subset_b'] = (len(WB[u'T'] - WB[u'L']) == 0)

# html 带标签 ⇎ 去标签: 同一份文件的两种“正文”
def cnt(s, pat):
    return len(re.findall(pat, s))


PP = {u'sha3': u'(?i)sha3', u'shake': u'(?i)shake', u'sponge': u'(?i)sponge',
      u'keccak': u'(?i)keccak', u'nist': u'(?i)nist', u'fips': u'(?i)fips',
      u'algorithm': u'Algorithm \\d', u'step': u'Step \\d'}
M[u'html_tagged'] = [cnt(X[u'H'], PP[k]) for k in sorted(PP)]
M[u'html_tagless'] = [cnt(TAGLESS, PP[k]) for k in sorted(PP)]
M[u'html_pk'] = sorted(PP)
M[u'html_lost'] = [M[u'html_tagged'][i] - M[u'html_tagless'][i] for i in range(len(PP))]
M[u'html_tags'] = len(TAGS)
M[u'html_tagkinds'] = len(set(re.findall(u'<([a-zA-Z][a-zA-Z0-9]*)', X[u'H'])))
M[u'html_a'] = X[u'H'].count(u'<a ')
M[u'html_img'] = X[u'H'].count(u'<img')
M[u'html_title'] = (re.findall(u'<title>([^<]*)</title>', X[u'H']) or [u''])[0].strip()
M[u'html_h1'] = [re.sub(u'<[^>]+>', u'', x).strip() for x in re.findall(u'<h1[^>]*>.*?</h1>', X[u'H'], re.S)]
M[u'html_href_hash'] = len([t for t in re.findall(u'href="([^"]*)"', X[u'H']) if t.startswith(u'#')])
M[u'html_uswds'] = X[u'H'].count(u'uswds')

# ---------- 4. 数学符号在四层文本里的存活 ----------
GL = {u'oplus': u'⊕', u'pi': u'π', u'omega': u'ω', u'leftarrow': u'←', u'ell': u'ℓ',
      u'le': u'≤', u'middot': u'⋅', u'prime': u'′', u'ldots': u'…', u'arrow_right': u'→',
      u'p10s1': u'Pad10', u'x': u'∥'}
M[u'glyphs'] = [cnt(BODY[k], GL[g]) for g in sorted(GL) for k in ORDER]
M[u'glyphk'] = sorted(GL)
GLN = dict((g, [cnt(BODY[k], GL[g]) for k in ORDER]) for g in GL)
M[u'glyph_only_T'] = sorted([g for g, v in GLN.items() if v[0] and not any(v[1:])])
M[u'glyph_all_zero'] = sorted([g for g, v in GLN.items() if not any(v)])
M[u'nonascii'] = [sum(1 for ch in BODY[k] if ord(ch) > 127) for k in ORDER]
M[u'nonascii_kinds'] = [len(set(ch for ch in BODY[k] if ord(ch) > 127)) for k in ORDER]

# 伪码结构: 同一份标准的算法/步骤在四层各被数出几个
STR = {u'algorithm': u'Algorithm \\d', u'step': u'Step \\d', u'table': u'Table \\d',
       u'figure': u'Figure \\d', u'appendix': u'Appendix [A-Z]', u'listing': u'Listing \\d'}
M[u'struct'] = [cnt(BODY[k], STR[s]) for s in sorted(STR) for k in ORDER]
M[u'structk'] = sorted(STR)
def algoset(k):
    return sorted(set(int(x) for x in re.findall(u'Algorithm (\\d+)', BODY[k])))


ALG = dict((k, algoset(k)) for k in ORDER)
M[u'algo'] = dict((k, ALG[k]) for k in ORDER)
M[u'algo_n'] = [len(ALG[k]) for k in ORDER]
M[u'algo_max'] = [max(ALG[k]) if ALG[k] else 0 for k in ORDER]
M[u'algo_equal_tl'] = ALG[u'T'] == ALG[u'L']
M[u'algo_equal_lp'] = ALG[u'L'] == ALG[u'P']

# ---------- 5. 折叠空白后的最长公共片段(跨层重复率) ----------
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


FL = dict((k, flat(BODY[k])) for k in ORDER)
PAIR = [(u'L', u'T'), (u'P', u'T'), (u'H', u'T'), (u'L', u'P')]
RS = dict(((a, b), runmax(FL[b], FL[a])) for a, b in PAIR)
M[u'run_pairs'] = [u'%s⇎%s' % (a, b) for a, b in PAIR]
M[u'run_pieces'] = [len(RS[p]) for p in PAIR]
M[u'run_total'] = [sum(RS[p]) for p in PAIR]
M[u'run_max'] = [max(RS[p]) for p in PAIR]
M[u'run_top3'] = [sorted(RS[p], reverse=True)[:3] for p in PAIR]
M[u'run_share'] = [round(100.0 * sum(RS[p]) / len(FL[p[0]]), 1) for p in PAIR]
assert all(M[u'run_pieces'][i] > 0 for i in range(4))

# ---------- 6. 行结构差异: 同一句话占几行 ----------
def wrapratio(k, w=72):
    ls = NB[k]
    return len([x for x in ls if len(x) > w])


M[u'wrap_72'] = [wrapratio(k) for k in ORDER]
M[u'multicol'] = [len([x for x in NB[k] if re.search(u'\\S {3,}\\S', x)]) for k in ORDER]
M[u'trailing_ws'] = [len([x for x in X[k].split(NL) if x != x.rstrip()]) for k in ORDER]
M[u'tabchar'] = [X[k].count(u'\t') for k in ORDER]
M[u'formfeed'] = [X[k].count(u'\f') for k in ORDER]
M[u'page_hdr'] = [len(re.findall(u'^FIPS PUB 202', X[k], re.M)) for k in ORDER]

# ---------- 7. 时间戳与出处字样 ----------
DATES = {u'aug2015': u'August 2015', u'y2015': u'2015', u'y2016': u'2016', u'y2024': u'2024',
         u'doi': u'dx\\.doi\\.org/10\\.6028/NIST\\.FIPS\\.202', u'issn': u'1943-1546',
         u'updated': u'Last Updated', u'published': u'Date Published',
         u'supersede': u'supersede', u'withdraw': u'(?i)withdraw'}
M[u'datek'] = sorted(DATES)
M[u'dates'] = [cnt(BODY[k], DATES[d]) for d in sorted(DATES) for k in ORDER]
DN = dict((d, [cnt(BODY[k], DATES[d]) for k in ORDER]) for d in DATES)
M[u'date_only_H'] = sorted([d for d, v in DN.items() if v[3] and not any(v[:3])])
M[u'date_all'] = sorted([d for d, v in DN.items() if all(v)])
M[u'htmldate'] = re.findall(u'(?:datePublished|dateModified|Last Updated)[^<]{0,40}', X[u'H'])[:4]

# ---------- 8. 同名穿层矩阵 ----------
CROSS = [u'FIPS PUB 202', u'SHA-3 Standard', u'Permutation-Based Hash', u'Extendable-Output Functions',
         u'August 2015', u'10.6028/NIST.FIPS.202', u'Algorithm 1', u'Step 1', u'⊕', u'π',
         u'sponge function', u'sha3-256', u'shake256', u'CSRC MENU', u'uswds', u'Keccak',
         u'Information Technology Laboratory', u'Pad10*1', u'rate', u'capacity']


def pn(s):
    # 与 audit.prose_norm 同一口径: 三套实现各写一遍, 口径不同则穿层矩阵与锚归属会对不上
    s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
    s = re.sub(u'[’\'"\u2018\u2019`´]+', u'', s)
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


# 锚的“正文”口径: 落地页取原文件行(去标签后的整段在原文件里被标签切开), 其余三层取去标签正文
SRCL = dict((k, (X[k] if k == u'H' else BODY[k])) for k in ORDER)
FA = dict((k, pn(SRCL[k])) for k in ORDER)
FULL = dict((k, pn(BODY[k])) for k in ORDER)
HITS, HITCAL = [], []
for t in CROSS:
    n = pn(t)
    if n:
        h = tuple(k for k in ORDER if n in FULL[k])
        HITCAL.append(u'norm')
    else:
        # 归一函数会把 ⊕ ⇎ π 这类字形抹成空串: 空串在任何文本里都“命中”, 所以这两行改按原样数
        h = tuple(k for k in ORDER if t in BODY[k])
        HITCAL.append(u'raw')
    HITS.append(h)
M[u'hitkinds'] = len(CROSS)
M[u'hitnorm'] = HITCAL.count(u'norm')
M[u'hitrawglyph'] = HITCAL.count(u'raw')
M[u'hitsingle'] = len([h for h in HITS if len(h) == 1])
M[u'hitmulti'] = len([h for h in HITS if len(h) > 1])
M[u'hitnone'] = len([h for h in HITS if not h])
assert M[u'hitsingle'] + M[u'hitmulti'] + M[u'hitnone'] == M[u'hitkinds']
M[u'hit'] = dict((t, (u'—' if not h else u'⇎'.join(h))) for t, h in zip(CROSS, HITS))
M[u'hit4'] = [t for t, h in zip(CROSS, HITS) if len(h) == 4]
M[u'hit_T_only'] = [t for t, h in zip(CROSS, HITS) if h == (u'T',)]

# ---------- 8b. 骨架四口径: 原样逐字 ⇎ 去空白逐字 ⇎ 抹掉非 ASCII 后相同 ⇎ 对不上 ----------
def skel(s):
    return re.sub(u'[^0-9a-zA-Z]', u'', s)


def nbS(s):
    return [l.strip() for l in s.split(NL) if l.strip()]


TL = nbS(BODY[u'T'])
POOLKEY = [(skel(x), x) for x in TL if len(skel(x)) >= 12]
M[u'pair_total'] = len(POOLKEY)


def paircal(k):
    raw = set(BODY[k].split(NL))
    strip = set(nbS(BODY[k]))
    sk = set(skel(x) for x in nonblank(BODY[k]))
    v_raw = sum(1 for s, x in POOLKEY if x in raw)
    v_str = sum(1 for s, x in POOLKEY if x in strip)
    v_skl = sum(1 for s, x in POOLKEY if s in sk)
    return [v_raw, v_str, v_skl, len(POOLKEY)]


M[u'pair_TL'] = paircal(u'L')
M[u'pair_TP'] = paircal(u'P')
M[u'pair_TH'] = paircal(u'H')
M[u'pair_gap'] = [M[u'pair_TL'][2] - M[u'pair_TL'][1], M[u'pair_TP'][2] - M[u'pair_TP'][1],
                  M[u'pair_TH'][2] - M[u'pair_TH'][1]]
assert all(M[u'pair_' + c][0] <= M[u'pair_' + c][1] <= M[u'pair_' + c][2] <= M[u'pair_total']
           for c in (u'TL', u'TP', u'TH')), (M[u'pair_TL'], M[u'pair_TP'], M[u'pair_TH'])
def is_mast(x):
    return (u'Institute of Standards' in x or u'Technology Laboratory' in x
            or x.strip() == u'Abstract')


H_STRIP = set(nbS(BODY[u'H']))
M[u'pair_th_mast'] = len([x for s, x in POOLKEY if x in H_STRIP and is_mast(x)])
assert M[u'pair_th_mast'] == M[u'pair_TH'][1], (M[u'pair_th_mast'], M[u'pair_TH'])
assert M[u'pair_TH'][0] == 0 and M[u'pair_TH'][2] <= 8, M[u'pair_TH']

# ---------- 8c. 码点命运: 同一个“减号”在四层里各是什么字符, 抽取后又剩下什么 ----------
CP = {u'u2212': u'−', u'uf02d': u'﹀', u'u2013': u'–', u'u2014': u'—',
      u'ascii_hyphen': u'-', u'u2264': u'≤', u'u2295': u'⊕', u'ufffd': u''}
CP[u'uf02d'] = u'\uf02d'
CP[u'ufffd'] = u'\ufffd'
CPN = dict((c, [BODY[k].count(v) for k in ORDER]) for c, v in CP.items())
M[u'cpk'] = sorted(CP)
M[u'cp'] = [CPN[c] for c in sorted(CP)]
M[u'cp_nonascii_T'] = [sum(CPN[c][i] for c in CPN if c != u'ascii_hyphen') for i in range(4)]
M[u'cp_fffd_gen'] = CPN[u'ufffd'][1] == CPN[u'ufffd'][2]
M[u'dash_kinds'] = [len(set(ch for ch in BODY[k]
                            if unicodedata.category(ch).startswith(u'Pd') or ch in u'−–—‐‑‒\uf02d'))
                    for k in ORDER]

# ---------- 8d. html 的“正文”取决于是否连属性一起算 ----------
HRAW = X[u'H']
M[u'html_doi_raw'] = HRAW.count(u'10.6028/NIST.FIPS.202')
M[u'html_doi_tagless'] = TAGLESS.count(u'10.6028/NIST.FIPS.202')
M[u'html_uswds_raw'] = HRAW.count(u'uswds')
M[u'html_uswds_tagless'] = TAGLESS.count(u'uswds')
M[u'html_ext'] = len(re.findall(u'href="https?://', HRAW))
M[u'html_src'] = len(re.findall(u'src="', HRAW))

# ---------- 9. 候选锚池: 逐源截取 + 命中层数, 分层排序键 ----------
POOL, SEEN = [], set()
DOT = 0
GLYPHCH = u''.join(set(v for c, v in CP.items() if c != u'ascii_hyphen'))
for k in ORDER:
    for l in SRCL[k].split(NL):
        s = l.strip()
        if len(s) < 22:
            continue
        if re.search(u'\\.{6,}', s):
            DOT += 1  # 目录引导点: 长度够但不是话, 只计数不作锚
            continue
        n = pn(s)
        if len(n) < 14 or n in SEEN:
            continue
        SEEN.add(n)
        h = tuple(t for t in ORDER if n in FA[t])
        if not h:
            continue
        POOL.append([k, list(h), s])
M[u'pool_dot'] = DOT
M[u'pool_n'] = len(POOL)
M[u'pool_disclose'] = u'锚命中判定: T/L/P 用去标签正文, H 用原文件行'
M[u'pool_own'] = [len([p for p in POOL if p[0] == k and len(p[1]) == 1]) for k in ORDER]
M[u'pool_by_src'] = [len([p for p in POOL if p[0] == k]) for k in ORDER]
M[u'pool_hitn'] = [len([p for p in POOL if len(p[1]) == n]) for n in (1, 2, 3, 4)]
assert sum(M[u'pool_hitn']) == M[u'pool_n']
SEL = {}
for k in ORDER:
    own = [p for p in POOL if p[0] == k and len(p[1]) == 1]
    own.sort(key=lambda p: (-len(pn(p[2])), pn(p[2])))
    og = [p for p in own if any(ch in p[2] for ch in GLYPHCH)]
    og.sort(key=lambda p: (-len(pn(p[2])), pn(p[2])))
    c2 = [p for p in POOL if p[0] == k and len(p[1]) == 2]
    c2.sort(key=lambda p: (-len(pn(p[2])), pn(p[2])))
    allk = [p for p in POOL if p[0] == k and len(p[1]) == 4]
    allk.sort(key=lambda p: (-len(pn(p[2])), pn(p[2])))
    SEL[k] = {u'own': own[:14], u'own_n': len(own), u'glyph': og[:12], u'glyph_n': len(og),
              u'c2': c2[:6], u'c2_n': len(c2), u'all4': allk[:6], u'all4_n': len(allk)}
M[u'sel_own_n'] = [SEL[k][u'own_n'] for k in ORDER]
M[u'sel_glyph_n'] = [SEL[k][u'glyph_n'] for k in ORDER]
M[u'sel_c2_n'] = [SEL[k][u'c2_n'] for k in ORDER]
M[u'sel_all4_n'] = [SEL[k][u'all4_n'] for k in ORDER]
assert all(SEL[k][u'own'] for k in ORDER), {k: SEL[k][u'own_n'] for k in ORDER}
assert SEL[u'T'][u'glyph_n'] > 0 and SEL[u'L'][u'glyph_n'] > 0, M[u'sel_glyph_n']
GP = [p for p in POOL if any(ch in p[2] for ch in GLYPHCH)]
M[u'pool_glyph'] = len(GP)
M[u'pool_glyph_src'] = [len([p for p in GP if p[0] == k]) for k in ORDER]
M[u'pool_glyph_hitn'] = [len([p for p in GP if len(p[1]) == n]) for n in (1, 2, 3, 4)]
assert sum(M[u'pool_glyph_hitn']) == M[u'pool_glyph']

json.dump({u'meas': M, u'pool': POOL, u'sel': SEL, u'tags': ORDER,
           u'paths': [PATH[k] for k in ORDER],
           u'labels': {u'T': u'官方纯文本', u'L': u'本机按版式', u'P': u'本机无版式', u'H': u'官方落地页'}},
          io.open(u'corpus/_b53meas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

OUT = [u'# B53 采集: FIPS 202 四种序列化(官方 txt ⇎ 本机 layout ⇎ 本机 raw ⇎ 官方落地页 html), 第一遍现算']
for k in sorted(M):
    if k != u'hit':
        OUT.append(u'%-16s %s' % (k, M[k]))
OUT.append(u'hit matrix:')
for t in CROSS:
    OUT.append(u'  %-34s %s' % (t, M[u'hit'][t]))
OUT.append(u'glyphs: ' + u' ⇎ '.join(
    u'%s %s' % (g, M[u'glyphs'][i * 4:i * 4 + 4]) for i, g in enumerate(M[u'glyphk'])))
io.open(u'corpus/_b53meas.txt', 'w', encoding='utf-8', newline=NL).write(NL.join(OUT) + NL)
print(NL.join(OUT))
print(u'池 %d 条 ｜ 自有 %s ｜ 命中层数 %s ｜ 选取上限 own %s' % (
    M[u'pool_n'], M[u'pool_own'], M[u'pool_hitn'], M[u'sel_own_n']))
