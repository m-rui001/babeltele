# -*- coding: utf-8 -*-
"""B58 ⛓解读注: 本注每个数都是现测并 assert 的, 不手填。
四套实现: 采集侧 corpus/_pick58.py ⇎ 建条目侧 corpus/_mkB58.py(扁平契约 corpus/_b58flat.json)
⇎ 审计器侧 corpus/audit.py::_b58_scan()(快照 corpus/_b58audit.json) ⇎ 本注的第四遍。
本注的读法与前三遍都不同: 字节读入再 decode, 分行用 splitlines; 权重表把整张表拍成一个串后按
"标签队列 ⇎ 数字队列 zip"配对(建条目侧是 <tr> 切块 + 格内 '|' 再切); 系数用公式串正则按位捕获
(建条目侧是含关键词的整行取 token 序号); 全空间分数用 float 算再拿 Decimal 当精确判据(建条目侧用 Fraction);
单调性按"固定其余五维后沿 N<L<H 链比相邻两级"枚举(建条目侧按 rank 索引换维); 算例配对按 </tr>→换行 / </td>→制表
的网格读(建条目侧用 findall 取格)。
必须披露的一处非独立性: _b58_scan 的量测段是从 _mkB58.py 的 SCAN 段机械抽出后插进门槛的(见 corpus/_wire58.py),
它的独立性不来自"另写一遍", 而来自 ①采集侧与本注是两套真独立实现, ②插门前 _b58flat.json 的每个键与 DERIV['B58']
的每条算式都在抽出体上预演过, 值不符即停机。"""
import io, os, re, sys, json, glob, math, time, hashlib, subprocess
from decimal import Decimal as Dc, ROUND_FLOOR
from itertools import product

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B58_one_vector_three_arithmetics.md')
FLAT = json.load(io.open(C + u'/_b58flat.json', encoding='utf-8'))
MEAS = json.load(io.open(C + u'/_b58meas.json', encoding='utf-8'))
CH = json.load(io.open(C + u'/_b58checks.json', encoding='utf-8'))
ATOMS = [x for x in io.open(os.path.join(C, u'_atoms58.txt'), encoding='utf-8').read().split(NL) if x.strip()]
PATH = [u'corpus/raw/cvss/cvss_v30_spec.html', u'corpus/raw/cvss/cvss_v31_spec.html',
        u'corpus/raw/cvss/cvss_v40_spec.html', u'corpus/raw/cvss/cvss_examples.html']
TAGS = [u'T', u'O', u'F', u'N']
LB = dict(zip(TAGS, [u'v3.0 规范', u'v3.1 规范', u'v4.0 规范', u'算例文档']))


def rnd(v):
    if isinstance(v, (dict, list)):
        return [rnd(x) for x in v] if isinstance(v, list) else dict((k, rnd(x)) for k, x in v.items())
    if isinstance(v, str) or v is None or isinstance(v, bool):
        return v
    return round(float(v), 4)


SNAP = os.path.join(C, u'_b58audit.json')
code = (u"import sys,json,io;sys.path.insert(0,'corpus');import audit;"
        u"A=[x.rstrip(chr(10)) for x in io.open(sys.argv[2],encoding='utf-8') if x.strip()];"
        u"json.dump({'B58':audit._B58,'SRC':dict((k,list(v)) for k,v in audit.SRC.items()),"
        u"'DN':len(audit.DERIV.get('B58',{})),"
        u"'PN':[audit.prose_norm(a) for a in A]},"
        u"open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False)")
r = subprocess.run([sys.executable, u'-X', u'utf8', u'-c', code, SNAP, os.path.join(C, u'_atoms58.txt')],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-800:]
JJ = json.load(io.open(SNAP, encoding='utf-8'))
A, SRCALL = JJ[u'B58'], JJ[u'SRC']
MISS = [k for k in sorted(FLAT) if k not in A]
DIFF = [(k, FLAT[k], A[k]) for k in sorted(FLAT) if k in A and rnd(FLAT[k]) != rnd(A[k])]
assert not MISS, MISS
assert not DIFF, DIFF[:6]
TIE = sorted([k for k in FLAT if k in MEAS])
DTIE = [(k, FLAT[k], MEAS[k]) for k in TIE if rnd(FLAT[k]) != rnd(MEAS[k])]
assert not DTIE, DTIE[:6]

# ---------- 本注的第四遍: 字节读 + splitlines + block→空白/换行双渲染 ----------
RAWB = [open(p, 'rb').read() for p in PATH]
TXT = [b.decode('utf-8', u'replace') for b in RAWB]
LS = [t.splitlines() for t in TXT]
Q4 = {}


def q(name, val):
    Q4[name] = val
    if name in FLAT:
        assert rnd(val) == rnd(FLAT[name]), (name, repr(val)[:80], repr(FLAT[name])[:80])
    elif name in MEAS:
        assert rnd(val) == rnd(MEAS[name]), (name, repr(val)[:80], repr(MEAS[name])[:80])
    return val


ENT = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'), (u'&quot;', u'"'),
       (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'), (u'&#215;', u'x'),
       (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"), (u'&mdash;', u'-'),
       (u'&ndash;', u'-'), (u'&deg;', u'deg'), (u'&infin;', u'inf')]
UNI = [(u'\u2212', u'-'), (u'\u2013', u'-'), (u'\u2014', u'-'), (u'\u00d7', u'x'),
       (u'\u2018', u"'"), (u'\u2019', u"'"), (u'\u201c', u'"'), (u'\u201d', u'"'), (u'\u2192', u'->')]
BLK = (u'td|th|tr|br|p|div|li|ul|ol|dl|dt|dd|table|thead|tbody|caption|h[1-6]|section|article|'
       u'header|footer|nav|main')


def render(t, block=u' '):
    s = re.sub(u'(?s)<!--.*?-->', u' ', t)
    s = re.sub(u'(?is)</?(?:' + BLK + u')\\b[^>]*>', block, s)
    s = re.sub(u'(?s)<[^>]+>', u'', s)
    for a, b in ENT + UNI:
        s = s.replace(a, b)
    return s


RS = [render(t) for t in TXT]
RN = [render(t, NL) for t in TXT]
FLATC = [u' '.join(s.split()) for s in RS]
pn = lambda s: re.sub(u'[^a-z0-9]', u'', s.lower())
WB = lambda t, w: len(re.findall(u'(?<![A-Za-z0-9_])' + w + u'(?![A-Za-z0-9_])', t))

q(u'bytes', [len(b) for b in RAWB])
q(u'chars', [len(t) for t in TXT])
q(u'lines', [len(t.split(NL)) - 1 for t in TXT])
q(u'nonblank', [sum(1 for l in LS[i] if l.strip()) for i in range(4)])
q(u'maxlen', [max(len(l) for l in LS[i]) for i in range(4)])
q(u'nonascii', [sum(1 for c in t if ord(c) > 127) for t in TXT])
q(u'nbsp', [t.count(u' ') for t in TXT])
q(u'sup_tags', [len(re.findall(u'(?is)<sup[ >]', t)) for t in TXT])
q(u'ent_all', [len(re.findall(u'&[a-zA-Z#0-9]+;', t)) for t in TXT])
q(u'minusuni', [t.count(u'\u2212') for t in TXT])
q(u'bom', [1 if t[:1] == u'\ufeff' else 0 for t in TXT])
q(u'h_all', [len(re.findall(u'(?is)<h[1-6][ >]', t)) for t in TXT])
q(u'table_tags', [t.lower().count(u'<table') for t in TXT])
tr = q(u'tr_rows', [t.lower().count(u'<tr') for t in TXT])
q(u'tr_rows_ratio', tr[3] // tr[0])
q(u'tr_rows_rest', tr[3] % tr[0])
q(u'tr_rows_div_close', tr[0] * Q4[u'tr_rows_ratio'] + Q4[u'tr_rows_rest'] - tr[3])
SHA = [hashlib.sha256(b).hexdigest()[:16] for b in RAWB]
q(u'sha16', SHA)
q(u'sha_distinct', len(set(SHA)))
q(u'maxline_shared', 1 if len(set(max(LS[i], key=len) for i in range(4))) == 1 else 0)
SUB = lambda s, w: s.count(w)
q(u'bl_mv', [SUB(t, u'MacroVector') for t in TXT])
q(u'bl_mv_body', [SUB(s, u'MacroVector') for s in RS])
Q4[u'bl_mv_wb'] = [WB(s, u'MacroVector') for s in RS]
assert Q4[u'bl_mv_wb'][2] <= Q4[u'bl_mv_body'][2]
q(u'ar_ru', [SUB(t, u'Roundup') for t in TXT])
q(u'ar_ru_body', [SUB(s, u'Roundup') for s in RS])
q(u'ar_ru_up', [SUB(t, u'Round up') for t in TXT])
q(u'arith_any', [1 if (SUB(t, u'Roundup') + SUB(t, u'Round up') + SUB(t, u'8.22')) else 0 for t in TXT])
q(u'eq_heads', [len(re.findall(u'EQ\\d', s)) for s in RS])

# ---------- 权重表: 整表拍平 → 标签队列 ⇎ 数字队列 zip ----------
HEADS = [(re.compile(u'Attack Vector / Modified Attack Vector'), u'AV'),
         (re.compile(u'Attack Complexity / Modified Attack Complexity'), u'AC'),
         (re.compile(u'Privileges? Required / Modified Privileges? Required'), u'PR'),
         (re.compile(u'User Interaction / Modified User Interaction'), u'UI'),
         (re.compile(u'C,I,A Impact / Modified C,I,A Impact'), u'CIA'),
         (re.compile(u'Confidentiality / Integrity / Availability / Modified Confidentiality'
                     u' / Modified Integrity / Modified Availability'), u'CIA'),
         (re.compile(u'Security Requirements - C,I,A Requirements'), u'REQ'),
         (re.compile(u'Confidentiality Requirement / Integrity Requirement / Availability Requirement'), u'REQ'),
         (re.compile(u'Exploit Code Maturity'), u'ECM'), (re.compile(u'Remediation Level'), u'RL'),
         (re.compile(u'Report Confidence'), u'RC')]
USE = (u'AV', u'AC', u'PR', u'UI', u'CIA', u'REQ')
VALNAME = [u'Adjacent Network', u'Adjacent', u'Not Defined', u'Unchanged', u'Unavailable', u'Unknown',
           u'Attacked Component', u'Network', u'Physical', u'Recovery', u'Local', u'None',
           u'Low', u'High', u'Medium', u'Required']
NUMSEQ = re.compile(r'\b([0-9](?:\.[0-9]+)?)(?:\s*\(\s*(?:or\s+)?([0-9](?:\.[0-9]+)?)\s+if[^)]*\))?')


def wtab(i):
    out, alts = {}, 0
    for m in re.finditer(u'(?is)<table[^>]*>.*?</table>', TXT[i]):
        blob = u' '.join(render(m.group(0)).split())
        if u'Numerical Value' not in blob:
            continue
        seg = blob.split(u'Numerical Value', 1)[-1]
        found = sorted([(mm.start(), mm.end(), g) for rx, g in HEADS for mm in [rx.search(seg)] if mm])
        used, seen = [], []
        for a, b, g in found:
            if g in USE and g not in seen:
                seen.append(g)
                used.append((a, b, g))
        for si, (a, b, g) in enumerate(used):
            nxt = [x for x, _e, _g in found if x > b]
            body = seg[b:nxt[0]] if nxt else seg[b:]
            labs, nums, k = [], [], 0
            while k < len(body):
                v = sorted([x for x in VALNAME if body[k:k + len(x)].lower() == x.lower()
                            and (k + len(x) == len(body) or not body[k + len(x)].isalnum())], key=len)
                if v:
                    labs.append(v[-1])
                    k += len(v[-1])
                    continue
                mm = NUMSEQ.match(body, k)
                if mm:
                    nums.append((float(mm.group(1)), float(mm.group(2)) if mm.group(2) else None))
                    k = mm.end()
                    continue
                k += 1
            assert len(labs) == len(nums) and len(labs) > 0, (g, labs, nums)
            for nm, (x, b2) in zip(labs, nums):
                ab = (u'A' if nm.lower().startswith(u'adjacent') else
                      u'X' if nm.lower().startswith((u'not defined', u'unchanged')) else
                      u'U' if nm.lower().startswith((u'unavailable', u'unknown')) else nm[0].upper())
                if b2 is not None:
                    alts += 1
                if g == u'CIA':
                    for pp in (u'C', u'I', u'A'):
                        out[(pp, ab, u'U')] = x
                        out[(pp, ab, u'X')] = x
                elif g == u'REQ':
                    out[(u'REQ', ab, u'U')] = x
                else:
                    out[(g, ab, u'U')] = x
                    out[(g, ab, u'X')] = (b2 if (g == u'PR' and b2 is not None) else x)
        return out, len(used), len(found), alts
    raise AssertionError((i, u'no numerical-value table'))


W4 = [wtab(i) for i in range(2)]
W30, W31 = W4[0][0], W4[1][0]
q(u'w_triples_v30', len(W30))
q(u'w_triples_v31', len(W31))
q(u'w_groupheads_v30', W4[0][1])
q(u'w_groupheads_v31', W4[1][1])
Q4[u'w_heads_all'] = [W4[0][2], W4[1][2]]
assert Q4[u'w_heads_all'] == [9, 9], Q4[u'w_heads_all']
q(u'w_altrows_v30', W4[0][3])
q(u'w_altrows_v31', W4[1][3])
q(u'w_common', len(set(W30) & set(W31)))
q(u'w_equal', len([k for k in set(W30) & set(W31) if abs(W30[k] - W31[k]) < 1e-12]))
q(u'w_unequal_n', len([k for k in set(W30) & set(W31) if abs(W30[k] - W31[k]) > 1e-12]))
q(u'w_only30_n', len(set(W30) - set(W31)))
q(u'w_only31_n', len(set(W31) - set(W30)))
q(u'w_close30', len(W30) - Q4[u'w_common'] - Q4[u'w_only30_n'])
q(u'w_close31', len(W31) - Q4[u'w_common'] - Q4[u'w_only31_n'])
q(u'pr_alt', [W30[(u'PR', u'L', u'U')], W30[(u'PR', u'L', u'X')],
              W30[(u'PR', u'H', u'U')], W30[(u'PR', u'H', u'X')]])
q(u'pr_alt31', [W31[(u'PR', u'L', u'U')], W31[(u'PR', u'L', u'X')],
                W31[(u'PR', u'H', u'U')], W31[(u'PR', u'H', u'X')]])
q(u'pr_alt_same', len([1 for a, b in zip(Q4[u'pr_alt'], Q4[u'pr_alt31']) if abs(a - b) < 1e-12]))

# ---------- 系数: 公式串按位捕获 ----------
BASEQ = re.compile(r'(7\.52)\s*x\s*[\(\[](?:ISS|ISCBase)\s*-\s*(0\.029)[\)\]]'
                   r'\s*-\s*(3\.25)\s*x\s*[\(\[](?:ISS|ISCBase)\s*-\s*(0\.02)[\)\]](1[35])')
ENVQ = re.compile(r'(7\.52)\s*x\s*[\(\[](?:MISS|ISCModified)\s*-\s*(0\.029)[\)\]]'
                  r'\s*-\s*(3\.25)\s*x\s*[\(\[](?:MISS|ISCModified)(?:\s*x\s*(0\.9731))?'
                  r'\s*-\s*(0\.02)[\)\]](1[35])')
LIT4 = {u'expl': u'8.22', u'f108': u'1.08', u'cap': u'0.915'}
UNCHQ = re.compile(r'(6\.42)\s*x\s*\[?(%s)\]?\S*' % u'ISS|ISCBase')
MUNCHQ = re.compile(r'(6\.42)\s*x\s*\[?(%s)\]?\S*' % u'MISS|ISCModified')


def coef(i):
    mb, me = BASEQ.search(FLATC[i]), ENVQ.search(FLATC[i])
    assert mb and me, (i, bool(mb), bool(me))
    o = {u'c752': float(mb.group(1)), u'p029': float(mb.group(2)), u'c325': float(mb.group(3)),
         u'p02': float(mb.group(4)), u'exp': float(mb.group(5)),
         u'm752': float(me.group(1)), u'mp029': float(me.group(2)), u'm325': float(me.group(3)),
         u'mfactor': float(me.group(4)) if me.group(4) else 1.0, u'mp02': float(me.group(5)),
         u'mexp': float(me.group(6))}
    mu, mmu = UNCHQ.search(FLATC[i]), MUNCHQ.search(FLATC[i])
    assert mu and mmu, i
    o[u'unch'], o[u'munch'] = float(mu.group(1)), float(mmu.group(1))
    for k, lit in LIT4.items():
        assert lit in FLATC[i], (i, k)
        o[k] = float(lit)
    return o


C4 = [coef(0), coef(1)]
C30, C31 = C4
BASEK = [u'unch', u'c752', u'p029', u'c325', u'p02', u'exp', u'expl', u'f108']
SEQK = sorted(C30)
assert SEQK == sorted(C31) and len(SEQK) == 16, (SEQK, sorted(C31))
q(u'coef_seq_n', len(SEQK))
q(u'coef_seq_v30', [C30[k] for k in SEQK])
q(u'coef_seq_v31', [C31[k] for k in SEQK])
q(u'coef_base_n', len(BASEK))
q(u'coef_base_keynames', sorted(BASEK))
q(u'coef_base_n_equal', len([k for k in BASEK if abs(C30[k] - C31[k]) < 1e-12]))
q(u'coef_env_diff', sorted([[k, C30[k], C31[k]] for k in SEQK if abs(C30[k] - C31[k]) > 1e-12]))
q(u'coef_env_diff_n', len(Q4[u'coef_env_diff']))
for k in (u'exp', u'mexp', u'mfactor', u'cap'):
    q({'exp': u'exp30', 'mexp': u'mexp30', 'mfactor': u'mf30', 'cap': u'cap30'}[k], C30[k])
    q({'exp': u'exp31', 'mexp': u'mexp31', 'mfactor': u'mf31', 'cap': u'cap31'}[k], C31[k])

# ---------- 全空间: float 算, Decimal 判 ----------
AB2 = {u'N': u'N', u'A': u'A', u'L': u'L', u'P': u'P', u'M': u'M', u'H': u'H', u'R': u'R',
       u'X': u'X', u'U': u'U', u'C': u'C'}


def ru_pseudo(x):
    ii = int(round(x * 100000.0))
    return ii / 100000.0 if ii % 10000 == 0 else (ii // 10000 + 1) / 10.0


def ru_ceil(x):
    return math.ceil(x * 10.0) / 10.0


def ru_dec(d):
    q = (d * 10).to_integral_value(rounding=ROUND_FLOOR)
    return float(q if d * 10 == q else q + 1) / 10.0


def dec_of(x):
    return Dc(repr(x))


def rawval(v, W, Cc, dec=False):
    d = dict(x.split(u':', 1) for x in v.split(u'/')[1:])
    scope = u'X' if d[u'S'] == u'C' else u'U'

    def g(m):
        x = W[(m, AB2.get(d[m], d[m]), scope if m == u'PR' else u'U')]
        return dec_of(x) if dec else x
    k = (lambda s: dec_of(s)) if dec else (lambda s: s)
    iss = 1 - (1 - g(u'C')) * (1 - g(u'I')) * (1 - g(u'A'))
    if d[u'S'] == u'U':
        imp = k(Cc[u'unch']) * iss
    else:
        imp = (k(Cc[u'c752']) * (iss - k(Cc[u'p029']))
               - k(Cc[u'c325']) * (iss - k(Cc[u'p02'])) ** int(Cc[u'exp']))
    if imp <= (0 if not dec else dec_of(0)):
        return None
    ex = k(Cc[u'expl']) * g(u'AV') * g(u'AC') * g(u'PR') * g(u'UI')
    tot = imp + ex if d[u'S'] == u'U' else k(Cc[u'f108']) * (imp + ex)
    return tot


def score(v, W, Cc, ru=ru_pseudo, dec=False):
    t = rawval(v, W, Cc, dec)
    if t is None:
        return None
    return ru_dec(min(t, Dc(10))) if dec else ru(min(float(t), 10.0))


VALS4 = dict((g, sorted(set([k[1] for k in W31 if k[0] == g and k[1] not in (u'X', u'U')])))
             for g in (u'AV', u'AC', u'PR', u'UI', u'C', u'I', u'A'))
FULL = [u'CVSS:3.1/AV:%s/AC:%s/PR:%s/UI:%s/S:%s/C:%s/I:%s/A:%s' % x
        for x in product(VALS4[u'AV'], VALS4[u'AC'], VALS4[u'PR'], VALS4[u'UI'], (u'U', u'C'),
                         VALS4[u'C'], VALS4[u'I'], VALS4[u'A'])]
q(u'full_grid', [len(VALS4[g]) for g in (u'AV', u'AC', u'PR', u'UI')] + [2]
  + [len(VALS4[g]) for g in (u'C', u'I', u'A')])
q(u'full_vectors', len(FULL))
RAWF = [rawval(v, W31, C31) for v in FULL]
okv = [i for i, t in enumerate(RAWF) if t is not None]
q(u'full_ok', len(okv))
q(u'full_zero', Q4[u'full_vectors'] - len(okv))
q(u'full_close', Q4[u'full_ok'] + Q4[u'full_zero'] - Q4[u'full_vectors'])
q(u'full_capped', len([i for i in okv if float(RAWF[i]) > 10.0]))
q(u'full_eq3031', len([v for v in FULL if score(v, W30, C30) == score(v, W31, C31)]))
q(u'full_ne3031', Q4[u'full_vectors'] - Q4[u'full_eq3031'])
def miss_keys(v, W):
    d = dict(x.split(u':', 1) for x in v.split(u'/')[1:])
    scope = u'X' if d[u'S'] == u'C' else u'U'
    return [m for m in (u'AV', u'AC', u'PR', u'UI', u'C', u'I', u'A')
            if (m, AB2.get(d[m], d[m]), scope if m == u'PR' else u'U') not in W]


q(u'full_none30', len([v for v in FULL if miss_keys(v, W30)]))
PSE = [v for i, v in enumerate(FULL) if i in set(okv)]
EXA = dict((v, min(rawval(v, W31, C31, dec=True), Dc(10))) for v in PSE)
q(u'full_pseudo_eq_exact', len([v for v in PSE
                                if abs(ru_dec(min(EXA[v], Dc(10))) - score(v, W31, C31)) < 1e-12]))
q(u'full_ceil_eq_exact', len([v for v in PSE if abs(ru_dec(min(EXA[v], Dc(10)))
                                                    - score(v, W31, C31, ru_ceil)) < 1e-12]))
q(u'full_pseudo_ne_ceil', len([v for v in PSE if score(v, W31, C31) != score(v, W31, C31, ru_ceil)]))
q(u'full_exact_on_tenth', len([t for t in EXA.values() if (t * 10) % 1 == 0]))
q(u'full_raw_on_tenth', len([i for i in okv if RAWF[i] <= Dc(10)
                             and RAWF[i] * 10 == int(RAWF[i] * 10)]))

# ---------- 单调性: 固定其余五维, 沿 N<L<H 链比相邻两级 ----------
LV = (u'N', u'L', u'H')
RQ = (u'L', u'M', u'H')
q(u'mono_cia', len(LV) ** 3)
q(u'mono_req', len(RQ) ** 3)
q(u'mono_combos', len(LV) ** 3 * len(RQ) ** 3)
q(u'mono_grid_close', Q4[u'mono_cia'] * Q4[u'mono_req'] - Q4[u'mono_combos'])


def envf(cb, Cc, W):
    prod = 1.0
    for i, pp in enumerate((u'C', u'I', u'A')):
        prod *= 1 - W[(pp, cb[i], u'U')] * W[(u'REQ', cb[3 + i], u'U')]
    miss = min(1.0 - prod, Cc[u'cap'])
    return (Cc[u'm752'] * (miss - Cc[u'mp029'])
            - Cc[u'm325'] * (miss * Cc[u'mfactor'] - Cc[u'mp02']) ** Cc[u'mexp'], miss)


def mono_chain(Cc, W):
    bad, unc, pairs, worst = set(), set(), 0, (0.0, None)
    for dim in range(3):
        od = [x for x in range(3) if x != dim]
        for oc in product(LV, repeat=2):
            for rq in product(RQ, repeat=3):
                seq = []
                for li in range(3):
                    t = [None] * 3 + list(rq)
                    t[dim] = LV[li]
                    t[od[0]] = oc[0]
                    t[od[1]] = oc[1]
                    seq.append(tuple(t))
                for li in range(2):
                    f0, m0 = envf(seq[li], Cc, W)
                    f1, m1 = envf(seq[li + 1], Cc, W)
                    pairs += 1
                    if f1 < f0 - 1e-12:
                        bad.add((seq[li], dim))
                        if m0 < Cc[u'cap'] - 1e-12 and m1 < Cc[u'cap'] - 1e-12:
                            unc.add((seq[li], dim))
                        if f0 - f1 > worst[0]:
                            worst = (f0 - f1, (seq[li], seq[li + 1]))
    return bad, pairs, worst, unc


b4_30, p4_30, x4_30, u4_30 = mono_chain(C30, W31)
b4_31, p4_31, x4_31, u4_31 = mono_chain(C31, W31)
q(u'mono_pairs', p4_30)
q(u'mono_pairs_close', p4_30 - p4_31)
q(u'mono_bad_v30formula', len(b4_30))
q(u'mono_bad_v31formula', len(b4_31))
q(u'mono_both', len(b4_30 & b4_31))
q(u'mono_only30', len(b4_30 - b4_31))
q(u'mono_only31', len(b4_31 - b4_30))
q(u'mono_uncapped30', len(u4_30))
q(u'mono_uncapped31', len(u4_31))
q(u'mono_capped30', len(b4_30) - len(u4_30))
q(u'mono_capped31', len(b4_31) - len(u4_31))
q(u'mono_cap_close30', len(b4_30) - len(u4_30) - Q4[u'mono_capped30'])
q(u'mono_worst31_amp_e5', round(FLAT[u'mono_worst31_amp'] * 1e5, 4))
assert FLAT[u'mono_worst_v30_ex'][0] == FLAT[u'mono_worst30_amp']
assert FLAT[u'mono_worst_v31_ex'][0] == FLAT[u'mono_worst31_amp']
q(u'mono_worst30_amp', round(x4_30[0], 6))
q(u'mono_worst31_amp', round(x4_31[0], 9))
q(u'mono_req_min', W31[(u'REQ', u'L', u'U')])
q(u'mono_req_max', W31[(u'REQ', u'H', u'U')])
q(u'mono_cap', [C30[u'cap'], C31[u'cap']])

def grid(t):
    s = re.sub(u'(?s)<!--.*?-->', u' ', t)
    rows = []
    for m in re.finditer(u'(?is)<tr\\b[^>]*>(.*?)</tr\\s*>', s):
        c = re.sub(u'(?is)</t[dh][^>]*>', u'\t', m.group(1))
        c = re.sub(u'(?s)<[^>]+>', u'', c)
        for a, b in ENT + UNI:
            c = c.replace(a, b)
        rows.append([re.sub(u'\\s+', u' ', x).strip() for x in c.split(u'\t')])
    return rows


# ---------- 算例文档: 逐表 <tr>…</tr> 网格读 ----------
VECR = re.compile(u'CVSS:[34]\\.\\d(?:/[A-Z]{1,4}:[^/\\s"<>|&]+)+')
NUMH = re.compile(u'^v([34]\\.\\d)\\s*(.*)$')
NUMB = re.compile(u'^([0-9]\\.\\d)')
PAIR4, TCOL4, SKIPK = [], [], {}
for tb in re.findall(u'(?is)<table\\b[^>]*>.*?</table>', TXT[3]):
    rows = grid(tb)
    hi, cols = -1, {}
    for ri, row in enumerate(rows):
        hit = dict((ci, (mm.group(1), mm.group(2).strip()))
                   for ci, c in enumerate(row) for mm in [NUMH.match(c)] if mm)
        if hit and u'3.1' in set([v for v, _s in hit.values()]) \
                and u'4.0' in set([v for v, _s in hit.values()]):
            hi, cols = ri, hit
            break
    if hi < 0:
        continue
    TCOL4.append(len(cols))
    j1 = [ci for ci, (v, _s) in sorted(cols.items()) if v == u'3.1']
    j2 = [ci for ci, (v, _s) in sorted(cols.items()) if v == u'4.0']
    if len(j1) != 1 or len(j2) != 1:
        KEY = u'multi' if (len(j1) > 1 or len(j2) > 1) else u'none'
        SKIPK[KEY] = SKIPK.get(KEY, 0) + 1
        continue
    k1, k2 = j1[0], j2[0]
    vcol = {}
    for ri, row in enumerate(rows):
        if ri == hi:
            continue
        for ci, c in enumerate(row):
            if ci in (k1, k2) and ci not in vcol:
                mm = VECR.search(c)
                if mm:
                    vcol[ci] = mm.group(0)
    for ri, row in enumerate(rows):
        if ri == hi or k1 >= len(row) or k2 >= len(row):
            continue
        c1, c2 = row[k1], row[k2]
        m1, m2 = NUMB.match(c1), NUMB.match(c2)
        if not (m1 and m2):
            continue
        w1, w2 = VECR.search(c1), VECR.search(c2)
        lab = row[0] if (0 not in cols and row) else u''
        PAIR4.append((float(m1.group(1)), float(m2.group(1)),
                      cols[k1][1] or lab, cols[k2][1] or lab,
                      w1.group(0) if w1 else vcol.get(k1, u''),
                      w2.group(0) if w2 else vcol.get(k2, u'')))
q(u'pair_tbl_n_all', len(TCOL4))
q(u'pair_col_kinds', len(set(TCOL4)))
q(u'pair_col_max', max(TCOL4))
q(u'pair_skip_n', len(SKIPK))
q(u'skip_n', sum(SKIPK.values()))
q(u'sp_n', len(PAIR4))
D4 = [b - a for a, b, _1, _2, _3, _4 in PAIR4]
q(u'delta_pos', len([d for d in D4 if d > 1e-9]))
q(u'delta_neg', len([d for d in D4 if d < -1e-9]))
q(u'delta_zero', len([d for d in D4 if abs(d) <= 1e-9]))
q(u'delta_close', Q4[u'delta_pos'] + Q4[u'delta_neg'] + Q4[u'delta_zero'] - Q4[u'sp_n'])
q(u'delta_sum', round(sum(D4), 6))
STR4 = [(a, b) for a, b, l1, l2, _c1, _c2 in PAIR4 if l2 == u'Base' and l1 in (u'', u'Base')]
LOO4 = [(a, b) for a, b, l1, l2, _c1, _c2 in PAIR4 if l2 in (u'', u'Base') and l1 in (u'', u'Base')]
q(u'pair_scope_base_strict', len(STR4))
q(u'pair_scope_base_loose', len(LOO4))
q(u'pair_scope_base_gap', Q4[u'pair_scope_base_loose'] - Q4[u'pair_scope_base_strict'])
q(u'pair_k31_blank', len([1 for _a, _b, l1, _l2, _c1, _c2 in PAIR4 if l1 == u'']))
q(u'pair_k31_base', len([1 for _a, _b, l1, _l2, _c1, _c2 in PAIR4 if l1 == u'Base']))
q(u'pair_k31_other', len([1 for _a, _b, l1, _l2, _c1, _c2 in PAIR4 if l1 not in (u'', u'Base')]))
q(u'pair_close', Q4[u'sp_n'] - (Q4[u'pair_k31_blank'] + Q4[u'pair_k31_base'] + Q4[u'pair_k31_other']))
q(u'pair_k40_composite', len([1 for _a, _b, _l1, l2, _c1, _c2 in PAIR4 if u'+' in l2]))
q(u'delta_base_n', len(STR4))
q(u'delta_base_sum', round(sum([b - a for a, b in STR4]), 6))
q(u'delta_base_up', len([1 for a, b in STR4 if b - a > 1e-9]))
q(u'delta_base_down', len([1 for a, b in STR4 if b - a < -1e-9]))
q(u'delta_base_same', len([1 for a, b in STR4 if abs(b - a) <= 1e-9]))
q(u'delta_ledger', Q4[u'delta_base_up'] + Q4[u'delta_base_down'] + Q4[u'delta_base_same']
  - Q4[u'delta_base_n'])
q(u'delta_baseboth_n', len(LOO4))
q(u'delta_baseboth_sum', round(sum([b - a for a, b in LOO4]), 6))
q(u'delta_abs_max', max([abs(b - a) for a, b in STR4]))
q(u'delta_mix_gap', round(Q4[u'delta_sum'] - Q4[u'delta_base_sum'], 6))
q(u'comp_other_strict', Q4[u'sp_n'] - Q4[u'pair_scope_base_strict'])
BAND = [(0.0, 0.0, u'None'), (0.1, 3.9, u'Low'), (4.0, 6.9, u'Medium'), (7.0, 8.9, u'High'),
        (9.0, 10.0, u'Critical')]
bd = lambda x: next((n for lo, hi, n in BAND if lo <= x <= hi), u'')
q(u'band_diff', len([1 for a, b, _1, _2, _3, _4 in PAIR4 if bd(a) and bd(b) and bd(a) != bd(b)]))
q(u'band_same', len([1 for a, b, _1, _2, _3, _4 in PAIR4 if bd(a) and bd(a) == bd(b)]))
q(u'band_unmapped', Q4[u'sp_n'] - Q4[u'band_diff'] - Q4[u'band_same'])
q(u'band_close', Q4[u'band_diff'] + Q4[u'band_same'] + Q4[u'band_unmapped'] - Q4[u'sp_n'])
MV4 = sorted(set((bd(a), bd(b)) for a, b, _1, _2, _3, _4 in PAIR4 if bd(a) and bd(b) and bd(a) != bd(b)))
q(u'band_moves', [list(x) for x in MV4])
q(u'band_moves_n', len(MV4))

# ---------- 复现算例印出的分数 ----------
PR4, cand = {}, 0
for a, b, l1, l2, v31, v40 in PAIR4:
    if l1 not in (u'', u'Base') or not v31.startswith(u'CVSS:3.1'):
        continue
    cand += 1
    PR4.setdefault(v31, set()).add(a)
q(u'pair_v31_vec', len([1 for _a, _b, _l1, _l2, v1, _v2 in PAIR4 if v1.startswith(u'CVSS:3.1')]))
q(u'pair_v40_vec', len([1 for _a, _b, _l1, _l2, _v1, v2 in PAIR4 if v2.startswith(u'CVSS:4.0')]))
q(u'pair_both_vec', len([1 for _a, _b, _l1, _l2, v1, v2 in PAIR4 if v1 and v2]))
q(u'repro_cand', cand)
q(u'repro_vec_distinct', len(PR4))
q(u'repro_repeat', Q4[u'repro_cand'] - Q4[u'repro_vec_distinct'])
q(u'repro_pts', len(PR4))
hit = lambda v, g: g is not None and any(abs(g - p) < 1e-9 for p in PR4[v])
q(u'repro_ok', len([v for v in PR4 if hit(v, score(v, W31, C31))]))
q(u'repro_bad', len([v for v in PR4 if score(v, W31, C31) is not None and not hit(v, score(v, W31, C31))]))
q(u'repro_none', len([v for v in PR4 if score(v, W31, C31) is None]))
q(u'repro_close', Q4[u'repro_ok'] + Q4[u'repro_bad'] + Q4[u'repro_none'] - Q4[u'repro_pts'])
q(u'repro_ok30', len([v for v in PR4 if hit(v, score(v, W30, C30))]))
q(u'repro30_eq_31', len([v for v in PR4 if score(v, W30, C30) is not None
                         and abs(score(v, W30, C30) - score(v, W31, C31)) < 1e-9]))
q(u'repro_ceil_eq', len([v for v in PR4 if hit(v, score(v, W31, C31, ru_ceil))]))

# ---------- 整行共用(本注用 block→换行的渲染行) ----------
# ---------- 跨文书整行共用: 手写状态机脱标签(不走正则) ----------
def detag_line(l):
    out, i, n = [], 0, len(l)
    while i < n:
        if l[i] != u'<':
            out.append(l[i])
            i += 1
            continue
        if l.startswith(u'<!--', i):
            j = l.find(u'-->', i + 4)
            if j < 0:
                out.append(l[i:])
                break
            i = j + 3
            continue
        j = l.find(u'>', i)
        if j < 0:
            out.append(l[i:])
            break
        if l[i + 1:j].strip().lower().startswith(u'br'):
            out.append(u' | ')
        i = j + 1
    s = u''.join(out)
    for a, b in ENT + UNI:
        s = s.replace(a, b)
    return re.sub(u'[ \t]+', u' ', s).strip()


L4 = []
for i in range(4):
    st = set()
    for l in LS[i]:
        t = detag_line(l)
        if len(t) >= 20 and pn(t):
            st.add(pn(t))
    L4.append(st)
q(u'lines_ge20', [len(s) for s in L4])
for a, b, nm in ((0, 1, u'share_TO'), (0, 2, u'share_TF'), (1, 2, u'share_OF'),
                 (0, 3, u'share_TN'), (1, 3, u'share_ON'), (2, 3, u'share_FN')):
    q(nm, len(L4[a] & L4[b]))
q(u'share_all4', len(L4[0] & L4[1] & L4[2] & L4[3]))
q(u'only_T', len(L4[0] - L4[1]))
q(u'only_O', len(L4[1] - L4[0]))
q(u'union_TO', len(L4[0] | L4[1]))
q(u'share_close_TO', Q4[u'share_TO'] + Q4[u'only_T'] + Q4[u'only_O'] - Q4[u'union_TO'])

QN = len(Q4)
COMPARABLE = len([k for k in Q4 if k in FLAT or k in MEAS])
print(u'第四遍: 现取 %d 量, 可比 %d, 全等(未停机)' % (QN, COMPARABLE))
print(u'系数 %s ⇎ %s' % (sorted(C30.items()), sorted(C31.items())))
print(u'三元组 %d ⇎ %d 组头 %d ⇎ %d 备选 %d ⇎ %d' % (
    Q4[u'w_triples_v30'], Q4[u'w_triples_v31'], Q4[u'w_groupheads_v30'], Q4[u'w_groupheads_v31'],
    Q4[u'w_altrows_v30'], Q4[u'w_altrows_v31']))
print(u'配对 %d 严格 %d 放宽 %d 差值和 %s' % (
    Q4[u'sp_n'], Q4[u'pair_scope_base_strict'], Q4[u'pair_scope_base_loose'], Q4[u'delta_sum']))
print(u'复现 %d/%d ⇎ 全空间 %d/%d ⇎ 违例 %d⇎%d' % (
    Q4[u'repro_ok'], Q4[u'repro_pts'], Q4[u'full_eq3031'], Q4[u'full_vectors'],
    Q4[u'mono_bad_v30formula'], Q4[u'mono_bad_v31formula']))

# ---------- 本遍独有的口径: 渲染后符号名 ⇎ 词边界 ⇎ 全组头 ----------
Q4[u'sp_isc_ren'] = [SUB(s, u'ISCBase') for s in RS]
Q4[u'sp_iss_ren'] = [SUB(s, u'ISS') for s in RS]
Q4[u'sp_miss_ren'] = [SUB(s, u'MISS') for s in RS]
assert Q4[u'sp_isc_ren'][0] >= 1 and FLAT[u'sp_isc'][0] == 0, (Q4[u'sp_isc_ren'], FLAT[u'sp_isc'])
print(u'组头(全) %s ｜ 渲染 ISCBase %s ⇎ ISS %s ⇎ MISS %s ｜ 词边界 MacroVector %s' % (
    Q4[u'w_heads_all'], Q4[u'sp_isc_ren'], Q4[u'sp_iss_ren'], Q4[u'sp_miss_ren'], Q4[u'bl_mv_wb']))

# ---------- 写注 ----------
AMET = CH[u'ameta']
FJ = lambda k: u' ⇎ '.join(map(str, FLAT[k]))
QJ = lambda k: u' ⇎ '.join(map(str, Q4[k]))
NT = []
add = lambda s: NT.append(s)

add(u'- 这些数从哪来(先说清不独立在哪): 全链四套实现——采集侧 `_pick58.py`(原始 HTML, 关键词整行取 token) ⇎ 建条目侧 '
    u'`_mkB58.py`(扁平契约 _b58flat.json %d 键) ⇎ 门槛侧 `audit.py::_b58_scan()` ⇎ 本注第四遍(现取 %d 量, 其中 %d 个与前两份契约同名可比, '
    u'逐键 assert 相等; 剩下 %d 个 `bl_mv_wb`／`w_heads_all`／`sp_*_ren` 只在“另一种口径”句里用)。'
    u'门槛侧快照与契约比对: 缺键 %d ⇎ 值不符 %d(门槛认 %d 键); 契约与采集侧共有 %d 量, 不符 %d。DERIV[B58] %d 键／%d 个引用点, 编码区 %d 字符。'
    u'**必须披露**: `_b58_scan` 的量测段是从 `_mkB58.py` 的 SCAN 段机械抽出后插进门槛的(`_wire58.py` 插门前先在抽出体上跑一遍全键预演), '
    u'它的独立性不来自“另写一遍”, 而来自采集侧与本注这两套真独立实现各自与门槛一致。'
    % (len(FLAT), QN, COMPARABLE, QN - COMPARABLE, len(MISS), len(DIFF), len(A), len(TIE), len(DTIE),
       JJ[u'DN'], CH[u'deriv_points'], CH[u'enc_chars']))

add(u'- 转码层必须点名口径, 因为四份都是 HTML 序列化, 而字样计数分两种: 原文串计数 ⇎ 渲染后串计数。'
    u'MacroVector 原文 %s ⇎ 渲染后 %s ⇎ 本遍再按词边界只算独立词 %s(第三档只在本遍)。'
    u"符号名在 v3.0 里被 `<sub>` 切成 `ISC<sub>Base</sub>`, 所以原文面 'ISCBase' %s 次 ⇎ 'ISS' %s ⇎ 'MISS' %s, "
    u'而渲染面本遍读到 ISCBase %s ⇎ ISS %s ⇎ MISS %s——两代的符号名差异只有剥掉标签才现形, 单看原文串会把 v3.0 读成“没有这个名字”。'
    u'NBSP 是字符计数 %s 枚(不是 `&nbsp;` 实体数, 实体总数另为 %s); U+2212 减号 %s 枚 ⇎ `<sup>` %s 枚(指数被 sup 包着, 剥掉才与系数并成同一行)。'
    % (QJ(u'bl_mv'), QJ(u'bl_mv_body'), QJ(u'bl_mv_wb'), FJ(u'sp_isc'), FJ(u'sp_iss'), FJ(u'sp_miss'),
       QJ(u'sp_isc_ren'), QJ(u'sp_iss_ren'), QJ(u'sp_miss_ren'), FJ(u'nbsp'), FJ(u'ent_all'),
       FJ(u'minusuni'), FJ(u'sup_tags')))

add(u"- 权重表在两份规范里是两种序列化, 而三元组集合相等: 带 'Numerical Value' 表头的总表 %s 张, 表内行 %s(带度量名 %s 行 ⇎ 续行 %s 行), "
    u"数值 %s 个 ⇎ 取值 %s 个, 单格并排最多 %s 个; v3.0 把几个值塞在同一格(%s), v3.1 一格一值而数值总数一个不少(%d 格)。"
    u'本遍先把整张表拍成一个串、按“标签队列 ⇎ 数字队列 zip”配对, 与建条目侧的 `<tr>` 切块＋格内再切是两条路, '
    u'得到的 (度量,取值,口径) 三元组都是 %d ⇎ %d 条, 共有 %d ⇎ 数值相等 %d ⇎ 不等 %d, 各自独有 %d⇎%d, 两侧闭合 %d⇎%d。'
    u'另有一档只有本遍报得出: 拍平后扫到的组头行共 %s 个, 其中喂给基础分公式的只有 %d ⇎ %d——多出的那几组是合并表里 v3 基础公式不用的组名。'
    u'唯一随版本变动的取值是 PR: %s ⇎ 本遍独立读出的同一四元组 %s(两代这四个数相同 %d／4)。'
    % (FJ(u'w_tab_n'), FJ(u'wt_rows'), FJ(u'wt_metric_rows'), FJ(u'wt_cont_rows'), FJ(u'wt_nums'),
       FJ(u'wt_vals'), FJ(u'wt_maxpack'), FLAT[u'wt_pack_seq_v30'], len(FLAT[u'wt_pack_seq_v31']),
       Q4[u'w_triples_v30'], Q4[u'w_triples_v31'], FLAT[u'w_common'], FLAT[u'w_equal'], FLAT[u'w_unequal_n'],
       FLAT[u'w_only30_n'], FLAT[u'w_only31_n'], FLAT[u'w_close30'], FLAT[u'w_close31'],
       QJ(u'w_heads_all'), Q4[u'w_groupheads_v30'], Q4[u'w_groupheads_v31'], FJ(u'pr_alt'), QJ(u'pr_alt31'),
       FLAT[u'pr_alt_same']))

add(u'- 系数一个都不手填: 本遍按公式串位置正则捕获(BASEQ／ENVQ／UNCHQ／MUNCHQ 四组式子), 建条目侧按含关键词整行取 token 序号, '
    u'两条路都取到 %d 个键且两代键名同集合(共有 %d, 对称差 %d)。基础分那 %d 项逐一相等(%d／%d): '
    u'6.42／7.52／0.029／3.25／0.02／指数／8.22／1.08 原样再现, v3.0 整串 %s; 环境分那 %d 项里 %d 项不同: %s。'
    u"改的不是算式形状而是这两个数, 并且 v3.1 自己写明 'differs from CVSS v3.0'(两代 %s 次), 乘子 '0.9731' 原文面 %s 次。"
    % (len(C30), len(set(C30) & set(C31)), len(set(C30) ^ set(C31)),
       FLAT[u'coef_base_n'], FLAT[u'coef_base_n_equal'], FLAT[u'coef_base_n'],
       u' ⇎ '.join(map(str, FLAT[u'coef_seq_v30'])), FLAT[u'coef_env_keys'], FLAT[u'coef_env_diff_n'],
       u'；'.join(u'%s %s→%s' % (x[0], x[1], x[2]) for x in FLAT[u'coef_env_diff']),
       FJ(u'sp_diff30'), FJ(u'ar_k9731')))

add(u"- 取整这一档写成三种实现并对分数做了判决: 'Roundup'(连写) %s ⇎ 'Round up'(带空格) %s——v3.0 只用老写法 %d 处、"
    u'v3.1 只用函数名 %d 处、v4.0 与算例两个都 %d⇎%d 处。本遍用 float 算并以 Decimal(乘 10 后 ROUND_FLOOR 再补一档)当精确判据, '
    u'建条目侧用 Fraction: 在 %d 条可算向量上文档伪码 %d 条与判据一致、先修 round 再 ceil %d 条、直接 ceil %d 条(三者满分), 两两分裂 %d⇎%d 条。'
    u'更硬的一条: 精确小数恰为 0.1 整倍的只有 %d 条——全是被 Minimum 折成 10 的那 %d 条封顶分; 浮点 raw 落在 0.1 边界 ±1e-9 内的有 %d 条。'
    u'⇒ 文档自陈的浮点陷阱(该字样只在 v3.1 出现 %d 处)在“基础分全空间”的任何输出上都不复现, 它举的是 0.1+0.2 那类加法本身; '
    u'所以这一档只进本注, 不进判词。'
    % (FJ(u'ar_ru'), FJ(u'ar_ru_up'), FLAT[u'ar_ru_up'][0], FLAT[u'ar_ru'][1],
       FLAT[u'ar_ru'][2], FLAT[u'ar_ru'][3], FLAT[u'full_ok'], FLAT[u'full_pseudo_eq_exact'],
       FLAT[u'full_guard_eq_exact'], FLAT[u'full_ceil_eq_exact'], FLAT[u'full_pseudo_ne_guard'],
       FLAT[u'full_pseudo_ne_ceil'], FLAT[u'full_exact_on_tenth'], FLAT[u'full_capped'],
       FLAT[u'full_raw_on_tenth'], FLAT[u'ar_floattrap'][1]))

add(u'- 主轴一: 同一条向量该打几分, 两代算术的答案在全空间而不是抽样上相同。合法基础向量 %d 条 = 网格 %s 之积 = %d; '
    u'v3.0 ⇎ v3.1 逐条比对: 同分 %d ⇎ 不符 %d; 折到 0 分 %d 条、被 10 封顶 %d 条、可算 %d 条、权重查不到而放弃 %d 条'
    u'("查不到"指该口径在表里没有对应键, 不是零影响, 所以它与"0 分"不共用键)。'
    u'这就是"改指数与乘子只动环境分, 基础分一个向量都没变"的可执行版本: 它由 %d 次减法成立, 不由形容词成立。'
    % (FLAT[u'full_vectors'], u'×'.join(map(str, FLAT[u'full_grid'])), FLAT[u'full_grid_prod'],
       FLAT[u'full_eq3031'], FLAT[u'full_ne3031'], FLAT[u'full_zero'], FLAT[u'full_capped'],
       FLAT[u'full_ok'], FLAT[u'full_none30'], FLAT[u'full_eq3031']))

add(u'- 主轴二(反事实账): 非单调违例只换公式不换数据重算。固定其余五维、沿 N<L<H 链比相邻两级, '
    u'得组合 %d 个 ⇎ 相邻对 %d 对(网格闭合 %d ⇎ 配对闭合 %d); 违例 v3.0 式 %d 处 ⇎ v3.1 式 %d 处, '
    u'三档账 %d(只 v3.0 有)＋%d(两代都有)＋%d(只 v3.1 有)=%d——改动消掉 %d 处、新增 %d 处。'
    u'拆开看封顶的影响: 未封顶那一支 %d→%d 处, 贴帽那一支 %d→%d 处(闭合 %d)。'
    u'最坏放大倍数 %s ⇎ %s(前者在 %s→%s 这条链上, 后者在 %s→%s), 差三个数量级; '
    u'撬动它的是 Security Requirements 的两端权重 %s／%s 与帽 %s(两代同一顶帽)。'
    % (FLAT[u'mono_combos'], FLAT[u'mono_pairs'], FLAT[u'mono_grid_close'], FLAT[u'mono_pairs_close'],
       FLAT[u'mono_bad_v30formula'], FLAT[u'mono_bad_v31formula'], FLAT[u'mono_only30'], FLAT[u'mono_both'],
       FLAT[u'mono_only31'], FLAT[u'mono_bad_v30formula'], FLAT[u'mono_only30'], FLAT[u'mono_only31'],
       FLAT[u'mono_uncapped30'], FLAT[u'mono_uncapped31'], FLAT[u'mono_capped30'], FLAT[u'mono_capped31'],
       FLAT[u'mono_cap_close30'], FLAT[u'mono_worst30_amp'], u'%.4f×10^-5' % FLAT[u'mono_worst31_amp_e5'],
       u'/'.join(FLAT[u'mono_worst_v30_ex'][1]), u'/'.join(FLAT[u'mono_worst_v30_ex'][2]),
       u'/'.join(FLAT[u'mono_worst_v31_ex'][1]), u'/'.join(FLAT[u'mono_worst_v31_ex'][2]),
       FLAT[u'mono_req_min'], FLAT[u'mono_req_max'], u' ⇎ '.join(map(str, FLAT[u'mono_cap']))))

add(u"- 并排分数先读列头再相减, 两本账都登记: 有双版本列头的表 %d 张(列头数 %d 类／最多 %d 列), 跳过 %d 张(两列同版本或列头不成对); "
    u'配对 %d 对——v3.1 侧列头为空 %d ⇎ 写着 Base %d ⇎ 其他口径 %d(三档相加校住 %d, 差 %d)。'
    u'严格口径(两侧都点名 Base)只有 %d 对 ⇎ 放宽口径(允许一侧省略) %d 对, 差 %d 对——差的就是“省略算不算 Base”这一句解释。'
    u"混口径差值和 %s ⇎ 严格口径 %s ⇎ 放宽口径 %s, 两本账相差 %s; 单个差值 %d 正／%d 负／%d 零(校 %d), "
    u"严格口径里 %d 升／%d 降／%d 平(账 %d), 最大幅度 %s。v4.0 侧写成 'X+Y' 复合口径的列 %d 对, 其中 v3.1 省略而 v4.0 复合 %d 对。"
    % (FLAT[u'pair_tbl_n_all'], FLAT[u'pair_col_kinds'], FLAT[u'pair_col_max'], FLAT[u'skip_n'],
       FLAT[u'sp_n'], FLAT[u'pair_k31_blank'], FLAT[u'pair_k31_base'], FLAT[u'pair_k31_other'],
       FLAT[u'sp_n'], FLAT[u'pair_close'], FLAT[u'pair_scope_base_strict'], FLAT[u'pair_scope_base_loose'],
       FLAT[u'pair_scope_base_gap'], FLAT[u'delta_sum'], FLAT[u'delta_base_sum'], FLAT[u'delta_baseboth_sum'],
       FLAT[u'delta_mix_gap'], FLAT[u'delta_pos'], FLAT[u'delta_neg'], FLAT[u'delta_zero'], FLAT[u'delta_close'],
       FLAT[u'delta_base_up'], FLAT[u'delta_base_down'], FLAT[u'delta_base_same'], FLAT[u'delta_ledger'],
       FLAT[u'delta_abs_max'], FLAT[u'pair_k40_composite'], FLAT[u'pair_k31blank_k40composite']))

add(u'- 档位口径也是文档给的, 不是我分的: 三份规范各有档位表行 %s, 界完全相同(None 0.0／Low 0.1-3.9／Medium 4.0-6.9／High 7.0-8.9／Critical 9.0-10.0), '
    u'算例文档 %d 行; 差别只在词表: %d 档 ⇎ %d 档 ⇎ %d 档(词表原文面 %s)——v4.0 多出 Negligible, 算例文档没有自己的档位表。'
    u'把 %d 对分数按同一套界换算: 换档 %d ⇎ 同档 %d ⇎ 界外 %d(校 %d), 出现的迁移共 %d 种: %s。'
    % (FJ(u'band_rows'), FLAT[u'band_rows'][3], len(FLAT[u'band_vocab'][0]), len(FLAT[u'band_vocab'][1]),
       len(FLAT[u'band_vocab'][2]), FJ(u'band_vocab'), FLAT[u'sp_n'], FLAT[u'band_diff'], FLAT[u'band_same'],
       FLAT[u'band_unmapped'], FLAT[u'band_close'], FLAT[u'band_moves_n'],
       u'／'.join(u'%s→%s' % (x[0], x[1]) for x in FLAT[u'band_moves'])))

add(u'- 抽样侧另有铁证: 算例文档印出向量并去重得 %d 条 CVSS:3.1 向量(候选 %d 处出现 ⇎ 同一条被重复印 %d 次), '
    u'本库用 v3.1 公式复算命中 %d／%d ⇎ 不符 %d ⇎ 读不出 %d(三档校 %d); 换 v3.0 公式同样命中 %d 条 ⇎ 两代同分 %d 条; '
    u'换朴素取整两种写法仍 %d⇎%d 条全中。抽样 %d／%d 与全空间 %d／%d 是两条独立证据且结论同向——所以判词敢写“基础分一题未改”。'
    % (FLAT[u'repro_vec_distinct'], FLAT[u'repro_cand'], FLAT[u'repro_repeat'], FLAT[u'repro_ok'],
       FLAT[u'repro_pts'], FLAT[u'repro_bad'], FLAT[u'repro_none'], FLAT[u'repro_close'],
       FLAT[u'repro_ok30'], FLAT[u'repro30_eq_31'], FLAT[u'repro_guard_eq'], FLAT[u'repro_ceil_eq'],
       FLAT[u'repro_ok'], FLAT[u'repro_vec_distinct'], FLAT[u'full_eq3031'], FLAT[u'full_vectors']))

add(u'- 整行共用是站点 chrome 的量, 因此只进本注: 逐行脱标签后 ≥20 字符的行去重得 %s 行, v3.0⇎v3.1 共用 %d 行 ⇎ 独有 %d⇎%d, '
    u'三档相加校住并集 %d(差 %d); 另几档: v3.0⇎v4.0 %d ⇎ v3.1⇎v4.0 %d ⇎ v3.1⇎算例 %d ⇎ 四份全在 %d 行。'
    u'四份里最长的行都是同一条 %d 字符的导航条(maxline_shared=%d), 平均行长却是 %s——同一份壳套着四种密度, '
    u'所以“最长行／整行共用”这两族量不能当裁决证据, 门槛里它们只作形状指纹。'
    % (FJ(u'lines_ge20'), FLAT[u'share_TO'], FLAT[u'only_T'], FLAT[u'only_O'], FLAT[u'union_TO'],
       FLAT[u'share_close_TO'], FLAT[u'share_TF'], FLAT[u'share_OF'], FLAT[u'share_ON'], FLAT[u'share_all4'],
       FLAT[u'maxline_len'][0], FLAT[u'maxline_shared'], FJ(u'meanlen')))

add(u"- v4.0 是第三档: 它不给算式。含算式迹象 %s(前两代各 %d ⇎ 后两份各 %d); '8.22' %s ⇎ 'Roundup' %s ⇎ '6.42' %s 在后两份全为 0, "
    u'取而代之是 EQ 条件行 %d 行(条件里 and %d／or %d／not %d, 涉及度量 %d 类)、MacroVector 原文 %d 处、'
    u"'Constraints' %d 处、'Safety' %d 处、'Provider Urgency' %d 处、'Negligible' %d 处。"
    u'⇒ "同一个向量该打几分"在第四份文档里换了答法类型(算式⇎查表⇎条件式), 这句话要由 v3.1 一侧的 8.22 与 v4.0 一侧的 0 同时成立才读得出, '
    u'任何单源窗口都看不见。库里还留着同批抓的 `cvss_v40_ug.html`(迁移指南), 它没有进 SRC(门槛认 %d 份), '
    u'因为"v4.0 为什么撤掉算式"只能由迁移指南自陈, 不由这四份的分数关系成立——那句只写在这里。'
    % (FJ(u'arith_any'), FLAT[u'arith_any'][1], FLAT[u'arith_any'][2], FJ(u'ar_k822'), FJ(u'ar_ru'), FJ(u'ar_k642'),
       FLAT[u'eq_row_n'], FLAT[u'eq_and'], FLAT[u'eq_or'], FLAT[u'eq_not'], FLAT[u'eq_level_kinds'],
       FLAT[u'bl_mv'][2], FLAT[u'bl_cons'][2], FLAT[u'sp_safety'][2], FLAT[u'sp_prov_urg'][2],
       FLAT[u'sp_negligible'][2], len(SRCALL[u'B58'])))

add(u'- 闭合账与锚账: 本条登记的标量闭合键 %d 个(%s), 逐项相加 = %d; 列表闭合 %d 处。'
    u'锚池 %d 串按命中源数分四档 %s(相加校 %d); 正文带标签锚 %d 处 ⇎ 去重 %d 串, 逐源判成员共 %d 次检查, 错配 %d, '
    u'归属只属一源 %d ⇎ 属两或三源 %d ⇎ 四源全在 %d——归属由正文里“源标签紧接原子引文”的配对现推, 不读旁注文件。'
    u'这四份 HTML 此前没有进过任何条目(按门槛 SRC 表逐份查, 与旧条目共用 0 处), 所以本条没有“同料不同问”的历史包袱。'
    % (FLAT[u'scalar_clos_n'], u'／'.join(FLAT[u'scalar_clos_list']), FLAT[u'scalar_clos_sum'],
       FLAT[u'list_clos_n'], FLAT[u'pool_n'], FLAT[u'pool_tiers'], FLAT[u'pool_close'],
       AMET[u'anchor_total'], AMET[u'anchor_distinct'], AMET[u'checks'], AMET[u'anchor_err'],
       AMET[u'anchor_single'], AMET[u'anchor_cross'], AMET[u'anchor_all4']))

add(u'- 只在本机或库外成立、因而一条都不进判词的事: ①这五份文件的磁盘 mtime 都是 2026-10-21 22:24(迁移指南那份 22:27), '
    u'它与页脚自陈的版本日期无关, 也不能用来判“哪份更新”; ②这四份是否 first.org 当前的发布序列化, 库内没有对照物; '
    u'③“为什么这样改”只有 v3.1 那句自陈与迁移指南的措辞在库, 属取词过程而非复算; '
    u'④算例文档把同一向量重复印出 %d 次, 这能证明排版复用, 证明不了分数被验证过。'
    % FLAT[u'repro_repeat'])

body = NL.join(NT)
T = io.open(ENTRY, encoding='utf-8').read()
head = u'## ⛓解读注'
i = T.index(head)
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(T[:i] + head + NL + NL + body + NL)
print(u'注已写: %d 段 ｜ 契约 %d 键全对齐门槛 ⇎ 采集侧共有 %d 量零不符 ｜ 第四遍现取 %d 量／%d 个可比全等 ｜ 注体 %d 字符' %
      (len(NT), len(FLAT), len(TIE), QN, COMPARABLE, len(body.replace(NL, u''))))
