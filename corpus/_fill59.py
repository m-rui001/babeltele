# -*- coding: utf-8 -*-
"""B59 ⛓解读注: 本注每个数都是现测并 assert 的, 不手填。
四套实现: 采集侧 corpus/_pick59.py('<' 游标扫描 + 逐量 findall) ⇎ 建条目侧 corpus/_mkB59.py
(整篇三次 re.sub 剥壳 + 全篇切词进 Counter, 扁平契约 corpus/_b59flat.json) ⇎ 门槛侧
corpus/audit.py::_b59_scan()(快照 corpus/_b59audit.json) ⇎ 本注第四遍。
本注的读法与前三遍都不同: ①先把原文切成 正文/注释/标签 三型片段队列(一遍扫描, 三型标记), 两口径剥壳与
“整篇渲染 ⇎ 逐行渲染”都从同一队列上按不同开关组装——建条目侧是“整篇 strip() 两遍 + 逐行 strip() 一遍”, 采集侧是
“find('<') 游标各走一遍”; ②词法档只做一次: 按 ASCII 字母 ⇎ 按词字符各切一条 token 流(带 token 间的 gap 串),
强度词四档写法 ⇎ SHALL NOT 复合 ⇎ password 单复数 ⇎ 门槛数字 ⇎ 位数 N bits ⇎ Sec./Section ⇎ block/black 词族
全部从这两条流上回查(建条目侧每族量各写一条正则, 采集侧各写一条带字母边界的正则);
③ASVS 矩阵按“表头单元名 → 列号”左索引取列(建条目侧与采集侧都从行尾右数第几格);
④条款标题号按“逐段手拆 数字.数字 并手看号后一个字符”判形(建条目侧用 (?m) 正则)。
必须披露的一处非独立性: _b59_scan 的量测段是从 _mkB59.py 的 SCAN 段机械抽出后插进门槛的(见 corpus/_wire59.py),
它的独立性不来自“另写一遍”, 而来自 ①采集侧与本注是两套真独立实现, ②插门前 _b59flat.json 的每个键与 DERIV['B59']
的每条算式都在抽出体上预演过, 值不符即停机。"""
import io, os, re, sys, json, hashlib, subprocess

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B59_one_password_four_answers.md')
FLAT = json.load(io.open(C + u'/_b59flat.json', encoding=u'utf-8'))
MEAS = json.load(io.open(C + u'/_b59meas.json', encoding=u'utf-8'))
CH = json.load(io.open(C + u'/_b59checks.json', encoding=u'utf-8'))
ATOMS = [x for x in io.open(os.path.join(C, u'_atoms59.txt'), encoding=u'utf-8').read().split(NL) if x.strip()]
PATH = [u'corpus/raw/pwd/nist_63b_rev3.html', u'corpus/raw/pwd/asvs_40_v2.md',
        u'corpus/raw/pwd/nist_63b_rev4.html', u'corpus/raw/pwd/owasp_auth_cs.html']
TAGS = [u'T', u'O', u'F', u'N']
LBL = dict(zip(TAGS, [u'旧规范', u'验证标准', u'新草案', u'备忘单']))
ENT = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'), (u'&sect;', u'S'),
       (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'), (u'&#215;', u'x'),
       (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"), (u'&mdash;', u'-'),
       (u'&ndash;', u'-'), (u'&deg;', u'deg'), (u'&infin;', u'inf')]
UNI = [(u' ', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
       (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->'), (u'–', u'-')]
WORDNUM = {u'six': 6, u'eight': 8, u'twelve': 12, u'fifteen': 15, u'four': 4, u'ten': 10}
NORMW = [u'SHALL', u'SHOULD', u'MAY', u'MUST']
BITS = (u'20', u'32', u'40', u'64', u'112')
LET = set(u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
WORDCH = LET | set(u'0123456789_')
WS1 = set(u' \t\n')


def rnd(v):
    if isinstance(v, (dict, list)):
        return [rnd(x) for x in v] if isinstance(v, list) else dict((k, rnd(x)) for k, x in v.items())
    if isinstance(v, str) or v is None or isinstance(v, bool):
        return v
    return round(float(v), 4)


SNAP = os.path.join(C, u'_b59audit.json')
code = (u"import sys,json,io;sys.path.insert(0,'corpus');import audit;"
        u"A=[x.rstrip(chr(10)) for x in io.open(sys.argv[2],encoding='utf-8') if x.strip()];"
        u"json.dump({'B59':audit._B59,'SRC':dict((k,list(v)) for k,v in audit.SRC.items()),"
        u"'DN':len(audit.DERIV.get('B59',{})),"
        u"'PN':[audit.prose_norm(a) for a in A]},"
        u"open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False)")
r = subprocess.run([sys.executable, u'-X', u'utf8', u'-c', code, SNAP, os.path.join(C, u'_atoms59.txt')],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-800:]
JJ = json.load(io.open(SNAP, encoding=u'utf-8'))
A, SRCALL = JJ[u'B59'], JJ[u'SRC']
MISS = [k for k in sorted(FLAT) if k not in A]
DIFF = [(k, FLAT[k], A[k]) for k in sorted(FLAT) if k in A and rnd(FLAT[k]) != rnd(A[k])]
assert not MISS, MISS
assert not DIFF, DIFF[:6]
TIE = sorted([k for k in FLAT if k in MEAS])
DTIE = [(k, FLAT[k], MEAS[k]) for k in TIE if rnd(FLAT[k]) != rnd(MEAS[k])]
assert not DTIE, DTIE[:6]


# ---------- 本注的实现: 片段队列 → 四种组装 ----------
def occ(hay, ndl):
    n, i = 0, hay.find(ndl)
    while i >= 0:
        n += 1
        i = hay.find(ndl, i + len(ndl))
    return n


def segs(s):
    """一遍扫描分成 ('t' 正文 | 'c' 注释 | 'g' 标签); '<>' 与无 '>' 的 '<' 都退回正文。"""
    out, i, n, low = [], 0, len(s), s.lower()
    while i < n:
        k = s.find(u'<', i)
        if k < 0:
            out.append((u't', s[i:]))
            break
        if k > i:
            out.append((u't', s[i:k]))
        if low.startswith(u'<!--', k):
            j2 = s.find(u'-->', k + 3)
            if j2 >= 0:
                j2 += 2
                out.append((u'c', s[k:j2 + 1]))
                i = j2 + 1
                continue
        j = s.find(u'>', k + 1)
        if j < 0 or j == k + 1:
            out.append((u't', s[k:k + 1]))
            i = k + 1
            continue
        out.append((u'g', s[k:j + 1]))
        i = j + 1
    return out


def tname(tag):
    x = tag[1:-1].strip().lower()
    cls = x.startswith(u'/')
    if cls:
        x = x[1:]
    return (cls, re.split(u'[ \\t\\n/]', x)[0])


def fold(s):
    for a, b in ENT + UNI:
        s = s.replace(a, b)
    return re.sub(u'[ \t]+', u' ', s).strip()


def build(S, br=u' ', keep=False, bare=False):
    """同一队列四种组装: keep=True 只删标签(脚本正文留下) ⇎ keep=False 连正文一起丢 ⇎ bare=True 整块丢壳留形(供逐行再剥)。"""
    out, inside, mark = [], None, 0
    for kind, txt in segs(S):
        if kind == u'c':
            if bare and inside is None:
                out.append(txt)
            continue
        if kind == u'g':
            cls, nm = tname(txt)
            if cls:
                if nm == inside:
                    if bare:
                        del out[mark:]
                    inside = None
                elif bare:
                    out.append(txt)
                continue
            if nm in (u'script', u'style') and not keep:
                if bare:
                    out.append(txt)
                if inside is None:
                    inside, mark = nm, len(out) - (1 if bare else 0)
                continue
            if bare:
                out.append(txt)
            elif nm.startswith(u'br'):
                out.append(br)
            continue
        if inside is None or keep:
            out.append(txt)
    s = u''.join(out)
    return s if bare else fold(s)


RAWB = [open(p, 'rb').read() for p in PATH]
TXT0 = [b.decode('utf-8', u'replace') for b in RAWB]
TXT = [build(t) for t in TXT0]
TXTF = [build(t, keep=True) for t in TXT0]
UNSCR = [build(t, bare=True) for t in TXT0]
RL = [t.split(NL) for t in TXT0]
LST = [[build(l) for l in UNSCR[i].split(NL)] for i in range(4)]
TLINES = [TXT[i].split(NL) for i in range(4)]
pn = lambda s: u''.join([c for c in s.lower() if (u'a' <= c <= u'z') or (u'0' <= c <= u'9')])


def tokrun(s, cls):
    """切 token 并保留每个 token 之后的 gap 串(复合词与 'Sec.' 的判定都要用它)。"""
    out, i, n = [], 0, len(s)
    while i < n:
        j = i
        while j < n and s[j] in cls:
            j += 1
        if j > i:
            k = j
            while k < n and s[k] not in cls:
                k += 1
            out.append([s[i:j], i, j, s[j:k]])
            i = k
        else:
            i += 1
    return out


TL = [tokrun(t, LET) for t in TXT]
TW = [tokrun(t, WORDCH) for t in TXT]
Q4 = {}


def q(name, val):
    Q4[name] = val
    if name in FLAT:
        assert rnd(val) == rnd(FLAT[name]), (name, repr(val)[:90], repr(FLAT[name])[:90])
    elif name in MEAS:
        assert rnd(val) == rnd(MEAS[name]), (name, repr(val)[:90], repr(MEAS[name])[:90])
    return val


def kwf(i, word, mode):
    c = 0
    for t in TL[i]:
        x = t[0]
        if mode == u'u' and x == word:
            c += 1
        elif mode == u'l' and x == word.lower():
            c += 1
        elif mode == u't' and x == word[0] + word[1:].lower():
            c += 1
        elif mode == u'ci' and x.upper() == word:
            c += 1
    return c


def pair(i, w1, w2, ci=False):
    """复合规范词: 首词必须是完整 LET token 且 gap 恰为一个空格; ci 档照 mk 的子串口径只再看后三个字母。"""
    c, s = 0, TXT[i]
    ts = TL[i]
    for k in range(len(ts)):
        t = ts[k]
        if t[3] != u' ':
            continue
        j = t[2] + 1
        if ci:
            if t[0].upper() == w1 and s[j:j + len(w2)].upper() == w2:
                c += 1
        elif k + 1 < len(ts) and t[0] == w1 and ts[k + 1][0] == w2:
            c += 1
    return c


def gapfam(s, head, tail, gforms):
    """词族分档: 合写(一个 token) ⇎ 分写(gap 落在给定形态里)。"""
    ts = tokrun(s, WORDCH)
    fused = sp = 0
    for k, t in enumerate(ts):
        v = t[0].lower()
        if v == head + tail:
            fused += 1
            continue
        if v != head or k + 1 >= len(ts) or ts[k + 1][0].lower() != tail:
            continue
        if t[3] in gforms:
            sp += 1
    return fused, sp


BLK = set([u'', u' ', u'\t', u'\n', u'-', u' -', u'\t-', u'\n-'])
SPC = set([u' ', u'\t', u'-'])
WSP = set(u' \t')


def blkscan(s):
    """block/black × list 的四形态计数(合写 ⇎ 单字符 gap ⇎ 纯空格 gap ⇎ 两字符 gap); 词尾按前缀判, 与 mk 的子串口径同。"""
    ts = tokrun(s, WORDCH)
    o = dict((h, dict((f, 0) for f in (u'fused', u'g1', u'g1s', u'ws', u'hy', u'g2')))
             for h in (u'block', u'black'))
    for k, t in enumerate(ts):
        v = t[0].lower()
        if v.startswith(u'blocklist') or v.startswith(u'blacklist'):
            o[v[:5]][u'fused'] += 1
            continue
        if v not in (u'block', u'black') or k + 1 >= len(ts):
            continue
        if not ts[k + 1][0].lower().startswith(u'list'):
            continue
        g = t[3]
        if g in BLK:
            o[v][u'g1'] += 1
        if g in SPC:
            o[v][u'g1s'] += 1
        if g and set(g) <= WSP:
            o[v][u'ws'] += 1
        if u'-' in g:
            o[v][u'hy'] += 1
        if g in (u' -', u'\t-', u'\n-'):
            o[v][u'g2'] += 1
    return o


BS = [blkscan(t) for t in TXT]
blkline = lambda l: (blkscan(l)[u'block'][u'fused'] + blkscan(l)[u'block'][u'g1']) > 0

# ---------- 形状档 ----------
q(u'bytes', [len(b) for b in RAWB])
q(u'chars', [len(t) for t in TXT])
q(u'chars_untagged', [len(t) for t in TXTF])
q(u'js_gap', [len(TXTF[i]) - len(TXT[i]) for i in range(4)])
q(u'lines', [len(RL[i]) - 1 for i in range(4)])
q(u'rlines', [len(LST[i]) - 1 for i in range(4)])
q(u'nonblank', [len([l for l in RL[i] if l.strip()]) for i in range(4)])
q(u'rnonblank', [len([l for l in LST[i] if l]) for i in range(4)])
q(u'maxlen', [max(len(l) for l in LST[i]) for i in range(4)])
q(u'lt_tags', [occ(t, u'<') for t in TXT0])
q(u'script_tags', [occ(t.lower(), u'<script') for t in TXT0])
q(u'style_tags', [occ(t.lower(), u'<style') for t in TXT0])
q(u'table_tags', [occ(t.lower(), u'<table') for t in TXT0])
q(u'tr_rows', [occ(t.lower(), u'<tr') for t in TXT0])
q(u'pipe_cells', [t.count(u'|') for t in TXT0])
q(u'bold_marks', [occ(t, u'**') // 2 for t in TXT0])
q(u'md_links', [occ(t, u'](http') for t in TXT0])
q(u'ent_all', [len(re.findall(u'&[a-zA-Z#0-9]+;', t)) for t in TXT0])
q(u'tabs', [t.count(u'\t') for t in TXT])
q(u'nonascii', [sum(1 for c in t if ord(c) > 127) for t in TXT0])
q(u'bom', [1 if t[:1] == u'﻿' else 0 for t in TXT0])
SHA = [hashlib.sha256(b).hexdigest()[:16] for b in RAWB]
q(u'sha16', SHA)
q(u'sig_distinct', len(set(SHA)))
q(u'pipe_vs_row', Q4[u'pipe_cells'][1] - (Q4[u'tr_rows'][0] + Q4[u'tr_rows'][2]))

# ---------- 门槛数字: 同一条词字符 token 流上的记法两档 ----------
def ctx_pairs(s):
    out = []
    ts = tokrun(s, WORDCH)
    for k, t in enumerate(ts):
        v, g = t[0], t[3]
        nxt = ts[k + 1] if k + 1 < len(ts) else None
        if nxt is None or g not in (u'-', u' ') or nxt[0].lower() not in (u'character', u'characters'):
            continue
        if v.isdigit() and len(v) <= 3:
            out.append((int(v), True))
        elif v.lower() in WORDNUM:
            out.append((WORDNUM[v.lower()], False))
    return out


CP = [ctx_pairs(t) for t in TXT]
q(u'ctx_occ', [len(x) for x in CP])
q(u'ctx_set', [sorted(set(y[0] for y in x)) for x in CP])
q(u'ctx_distinct', [len(set(y[0] for y in x)) for x in CP])
q(u'ctx_word_form', [len([y for y in x if not y[1]]) for x in CP])
q(u'ctx_digit_form', [len([y for y in x if y[1]]) for x in CP])
q(u'ctx_form_close', [Q4[u'ctx_word_form'][i] + Q4[u'ctx_digit_form'][i] - Q4[u'ctx_occ'][i]
                      for i in range(4)])
for nm, lit in ((u'th_digit8', u'8 characters'), (u'th_word_eight', u'eight characters'),
                (u'th_digit12', u'12 characters'), (u'th_digit15', u'15 characters'),
                (u'th_digit64', u'64 characters'), (u'th_digit128', u'128 characters'),
                (u'th_digit6', u'6 characters')):
    q(nm, [occ(t, lit) for t in TXT])
q(u'ctx_eight_docs', len([i for i in range(4) if u'eight characters' in TXT[i]]))
q(u'ctx_d8_docs', len([i for i in range(4) if Q4[u'th_digit8'][i]]))
q(u'ctx_815_docs', len([i for i in range(4) if set([y[0] for y in CP[i]]) >= set([8, 15])]))
q(u'ctx_12_only', len([i for i in range(4) if 12 in [y[0] for y in CP[i]]]))
q(u'ctx_128_only', len([i for i in range(4) if 128 in [y[0] for y in CP[i]]]))


def hasnum(l):
    ts = tokrun(l, WORDCH)
    for k, t in enumerate(ts):
        if t[0].isdigit() and k + 1 < len(ts) and t[3] in (u'-', u' ') \
                and ts[k + 1][0].lower() in (u'character', u'characters'):
            return True
    return False


q(u'th_line_norm', [len([l for l in LST[i] if hasnum(l) and u'SHALL' in l]) for i in range(4)])
q(u'th_line_bare', [len([l for l in LST[i] if hasnum(l) and not any(w in l for w in NORMW)])
                    for i in range(4)])

# ---------- 强度词四账 + 禁令复合 ----------
for W in NORMW:
    for m in (u'u', u'l', u't', u'ci'):
        q(u'kw_%s_%s' % (W.lower(), m), [kwf(i, W, m) for i in range(4)])
q(u'kw_close', dict((W, [kwf(i, W, u'u') + kwf(i, W, u'l') + kwf(i, W, u't') - kwf(i, W, u'ci')
                         for i in range(4)]) for W in NORMW))
q(u'kw_close_sum', sum(sum(v) for v in Q4[u'kw_close'].values()))
q(u'must_upper_all4', sum(Q4[u'kw_must_u']))
q(u'kw_upper_total', [sum(Q4[u'kw_%s_u' % W.lower()][i] for W in NORMW) for i in range(4)])
q(u'kw_ci_total', [sum(Q4[u'kw_%s_ci' % W.lower()][i] for W in NORMW) for i in range(4)])
q(u'kw_gap', [Q4[u'kw_ci_total'][i] - Q4[u'kw_upper_total'][i] for i in range(4)])
for W in (u'SHALL', u'SHOULD'):
    q(u'kw_%snot_u' % W.lower(), [pair(i, W, u'NOT') for i in range(4)])
    q(u'kw_%snot_ci' % W.lower(), [pair(i, W, u'NOT', ci=True) for i in range(4)])
    q(u'kw_%snot_gap' % W.lower(), [Q4[u'kw_%snot_ci' % W.lower()][i] - Q4[u'kw_%snot_u' % W.lower()][i]
                                    for i in range(4)])

# ---------- 术语换代 ----------
def mscount(s):
    ts = tokrun(s, LET)
    return len([k for k in range(len(ts) - 1)
                if ts[k][0].upper() == u'MEMORIZED' and ts[k][3] == u' '
                and ts[k + 1][0].upper().startswith(u'SECRET')])


q(u'tm_memorized', [mscount(t) for t in TXT])
q(u'tm_memorized_caps', [occ(t, u'Memorized Secrets') for t in TXT])
q(u'tm_pw_sing', [len([t for t in TW[i] if t[0].lower() == u'password']) for i in range(4)])
q(u'tm_pw_plural', [len([t for t in TW[i] if t[0].lower() == u'passwords']) for i in range(4)])
q(u'tm_pw_any', [len([t for t in TW[i] if t[0].lower() in (u'password', u'passwords')]) for i in range(4)])
q(u'tm_close', [Q4[u'tm_pw_sing'][i] + Q4[u'tm_pw_plural'][i] - Q4[u'tm_pw_any'][i] for i in range(4)])


def bridge(s):
    c, low, i = 0, s.lower(), 0
    while True:
        i = low.find(u'called', i)
        if i < 0:
            return c
        for d in (0, 1, 2, 3):
            if s[i + 6 + d:i + 6 + d + 17].lower() == u'memorized secrets':
                c += 1
                break
        i += 6


q(u'tm_bridge', [bridge(t) for t in TXT])
q(u'tm_defline', [len([l for l in LST[i] if u'intended to be memorized' in l]) for i in range(4)])
q(u'blk_def_lines', len([l for l in LST[2] if u'blocklist' in l and u'SHALL' in l]))
q(u'mc_blocklist', [BS[i][u'block'][u'fused'] + BS[i][u'block'][u'g1'] for i in range(4)])
q(u'bl_blacklist', [BS[i][u'black'][u'fused'] for i in range(4)])
q(u'bl_spaced', [BS[i][u'black'][u'ws'] for i in range(4)])
q(u'bl_black', [BS[i][u'black'][u'fused'] + BS[i][u'black'][u'g1s'] for i in range(4)])
q(u'bl_black_close', [Q4[u'bl_blacklist'][i] + Q4[u'bl_spaced'][i] - Q4[u'bl_black'][i] for i in range(4)])
q(u'bl_word_any', [BS[i][u'block'][u'fused'] + BS[i][u'black'][u'fused']
                   + BS[i][u'block'][u'g1s'] + BS[i][u'black'][u'g1s'] for i in range(4)])
q(u'bl_word_close', [Q4[u'mc_blocklist'][i] + Q4[u'bl_black'][i] - Q4[u'bl_word_any'][i] for i in range(4)])

# ---------- 机制词 ----------
SUBS = {u'breach': (u'breach',), u'entropy': (u'entropy',), u'arbitrary': (u'arbitrary',),
        u'copypaste': (u'copy and paste',), u'composition': (u'composition rules',),
        u'forcechange': (u'force a change',), u'periodic': (u'periodic', u'regular change')}
PRE = {u'hint': u'hint', u'lockout': u'lock'}


def subfam(s, head, tail):
    """字符面复算 mk 的 head+.?+tail 子串口径: gap 为 0 或 1 个任意字符, 命中后从词尾续扫(与 findall 同不重叠)。"""
    low, n, i = s.lower(), 0, 0
    while True:
        i = low.find(head, i)
        if i < 0:
            return n
        j = i + len(head)
        d = 0 if low[j:j + len(tail)] == tail else (1 if low[j + 1:j + 1 + len(tail)] == tail else None)
        if d is None:
            i += 1
            continue
        n += 1
        i = j + d + len(tail)


def mech(s, k):
    if k in SUBS:
        low = s.lower()
        return sum(occ(low, x) for x in SUBS[k])
    ts = tokrun(s, WORDCH)
    if k in PRE:
        return len([t for t in ts if t[0].lower().startswith(PRE[k])])
    if k == u'ratelimit':
        return subfam(s, u'rate', u'limit') + occ(s.lower(), u'throttl')
    if k == u'multifactor':
        return len([t for t in ts if t[0].lower() == u'mfa']) + subfam(s, u'multi', u'factor')
    raise AssertionError(k)


for k in list(SUBS) + list(PRE) + [u'ratelimit', u'multifactor']:
    q(u'mc_%s' % k, [mech(t, k) for t in TXT])
q(u'mc_blocklist_lines', [len([l for l in LST[i] if blkline(l)]) for i in range(4)])
for k in [x for x in SUBS if x != u'blocklist'] + list(PRE) + [u'ratelimit', u'multifactor']:
    q(u'mc_%s_lines' % k, [len([l for l in LST[i] if mech(l, k) > 0]) for i in range(4)])
q(u'comp_shouldnot', [len([l for l in LST[i] if u'composition rules' in l.lower() and u'SHOULD NOT' in l])
                       for i in range(4)])
q(u'comp_shallnot', [len([l for l in LST[i] if u'composition rules' in l.lower() and u'SHALL NOT' in l])
                     for i in range(4)])
q(u'comp_norm_free', [Q4[u'mc_composition_lines'][i] - Q4[u'comp_shouldnot'][i] - Q4[u'comp_shallnot'][i]
                      for i in range(4)])
def chgline(l):
    low = l.lower()
    return u'change passwords' in low or u'change memorized secrets' in low


q(u'chg_shallnot', [len([l for l in LST[i] if chgline(l) and u'SHALL NOT' in l]) for i in range(4)])
q(u'chg_shouldnot', [len([l for l in LST[i] if chgline(l) and u'SHOULD NOT' in l]) for i in range(4)])

# ---------- 引用形态与谱系 ----------
for k, lit, ci in ((u'url_nist', u'pages.nist.gov', False), (u'spaced', u'NIST SP 800-63', False),
                   (u'unspaced', u'SP800-63B', False), (u'rev4num', u'800-63-4', False),
                   (u'rev3num', u'800-63-3', False), (u'superseded', u'superseded', True),
                   (u'draftself', u'initial public draft', True)):
    q(u'cite_%s' % k, [occ(t.lower(), lit) if ci else occ(t, lit) for t in TXT])
q(u'cite_http_any', [occ(t, u'http://') + occ(t, u'https://') for t in TXT])
q(u'sup_openid', len([l for l in LST[3] if u'superseded' in l.lower() and u'OpenID' in l]))
q(u'sup_nist', len([l for l in LST[0] if u'superseded' in l.lower() and u'63-4' in l]))
q(u'cite_63b_docs', len([i for i in range(4) if u'800-63b' in TXT[i].lower()]))
q(u'cite_forms', len([x for x in (Q4[u'cite_url_nist'][1], Q4[u'cite_unspaced'][3],
                                  Q4[u'cite_spaced'][0]) if x]))


# ---------- 条款标题号: 手拆段 + 手看号后一个字符 ----------
def headnum(s, last):
    x = s.lstrip()
    for rep in (3, 2):
        p, k, ok = [], 0, True
        for _ in range(rep):
            j = k
            while j < len(x) and x[j].isdigit():
                j += 1
            if j == k or j >= len(x) or x[j] != u'.':
                ok = False
                break
            p.append(x[k:j])
            k = j + 1
        if not ok:
            continue
        j = k
        while j < len(x) and x[j].isdigit():
            j += 1
        if j == k:
            continue
        p.append(x[k:j])
        if j < len(x):
            if x[j] in (u' ', u'\t', u'\r'):
                return u'.'.join(p)
        elif not last:
            return u'.'.join(p)
    return None


def heads(i):
    ls, out = TLINES[i], []
    for k, l in enumerate(ls):
        h = headnum(l, k == len(ls) - 1)
        if h:
            out.append(h)
    return out


HEADS = [heads(i) for i in range(4)]
q(u'sec_head_n', [len(h) for h in HEADS])
SECT = sorted(set(HEADS[0]))
SECF = sorted(set(HEADS[2]))
q(u'sec_T_set', SECT)
q(u'sec_F_set', SECF)
q(u'sec_T_n', len(SECT))
q(u'sec_F_n', len(SECF))
q(u'sec_shared', len([x for x in SECT if x in SECF]))
q(u'sec_T_inF_text', len([x for x in SECT if x in TXT[2]]))

# ---------- ASVS 矩阵: 表头单元名 → 列号 ----------
def cells(l):
    return [x.strip() for x in l.split(u'|')]


HDRC = [cells(l) for l in LST[1] if l.startswith(u'|') and any(c == u'L1' for c in cells(l))]
CIDX = dict((c, HDRC[0].index(c)) for c in (u'L1', u'L2', u'L3', u'CWE'))
CIDX[u'ref'] = [k for k, c in enumerate(HDRC[0]) if c.startswith(u'[NIST')][0]
assert len(HDRC) > 1 and CIDX == {u'L1': 3, u'L2': 4, u'L3': 5, u'CWE': 6, u'ref': 7}, (len(HDRC), CIDX)
ROWS = [l for l in LST[1] if l.startswith(u'|') and cells(l)[1].count(u'**') == 2
        and re.match(u'^2\\.\\d+\\.\\d+$', cells(l)[1].strip(u'*'))]
CL = [cells(l) for l in ROWS]
q(u'asvs_req_rows', len(ROWS))
q(u'asvs_row_widths', sorted(set(len(c) for c in CL)))
REFS = [c[CIDX[u'ref']] for c in CL if re.match(u'^\\d+(\\.\\d+){1,3}$', c[CIDX[u'ref']])]
q(u'asvs_ref_occ', len(REFS))
q(u'asvs_refs', sorted(set(REFS)))
q(u'asvs_ref_distinct', len(set(REFS)))
q(u'asvs_rows_noref', Q4[u'asvs_req_rows'] - Q4[u'asvs_ref_occ'])
q(u'asvs_ref_inT', len([x for x in sorted(set(REFS)) if x in SECT]))
q(u'asvs_ref_inF', len([x for x in sorted(set(REFS)) if x in SECF]))
q(u'asvs_ref_inT_text', len([x for x in sorted(set(REFS)) if x in TXT[0]]))
q(u'asvs_ref_inF_text', len([x for x in sorted(set(REFS)) if x in TXT[2]]))
q(u'asvs_ref_missT', [x for x in sorted(set(REFS)) if x not in SECT])
q(u'asvs_ref_missF', [x for x in sorted(set(REFS)) if x not in SECF])
q(u'asvs_ref_close', Q4[u'asvs_ref_inT'] + len(Q4[u'asvs_ref_missT']) - Q4[u'asvs_ref_distinct'])
q(u'asvs_tick_cols', [len([c for c in CL if c[CIDX[nm]] == u'✓']) for nm in (u'L1', u'L2', u'L3')])
q(u'asvs_tick_total', sum(Q4[u'asvs_tick_cols']))
q(u'asvs_tick_legend', len([l for l in LST[1] if u'✓' in l and l not in ROWS]))
q(u'asvs_tick_glyph', occ(TXT0[1], u'✓'))
q(u'asvs_tick_close', Q4[u'asvs_tick_total'] + Q4[u'asvs_tick_legend'] - Q4[u'asvs_tick_glyph'])
q(u'asvs_cwe', sorted(set(c[CIDX[u'CWE']] for c in CL if c[CIDX[u'CWE']].isdigit())))
q(u'asvs_cwe_distinct', len(Q4[u'asvs_cwe']))
q(u'asvs_url_head', occ(TXT0[1], u'pages.nist.gov/800-63-3'))
q(u'asvs_bold_ids', len([p for k, p in enumerate(TXT0[1].split(u'**')) if k % 2 == 1
                         and re.match(u'^2\\.\\d+\\.\\d+$', p)]))
q(u'asvs_5112', [occ(t, u'5.1.1.2') for t in TXT])
q(u'id_211_bold', occ(TXT0[1], u'**2.1.1**'))
q(u'id_211_occ', [occ(t, u'2.1.1') for t in TXT])
q(u'id_211_docs', len([i for i in range(4) if u'2.1.1' in TXT[i]]))

# ---------- 条款引用面: Sec. ⇎ Section ⇎ 合并 ----------
def citecount(i, mode):
    c = 0
    for k, t in enumerate(TW[i]):
        v, nxt = t[0], (TW[i][k + 1] if k + 1 < len(TW[i]) else None)
        if nxt is None or not nxt[0][:1].isdigit():
            continue
        if mode == u'sec':
            if v == u'Sec' and t[3] in (u'.', u'. '):
                c += 1
        elif mode == u'word':
            if v.upper() == u'SECTION' and t[3] == u' ':
                c += 1
        elif v.upper() in (u'SEC', u'SECTION'):
            g = t[3][1:] if t[3][:1] == u'.' and v.upper() == u'SEC' else t[3]
            if g and set(g) <= set(u' \t'):
                c += 1
    return c


q(u'sec_cite_sec', [citecount(i, u'sec') for i in range(4)])
q(u'sec_cite_word', [citecount(i, u'word') for i in range(4)])
q(u'sec_cite_any', [citecount(i, u'any') for i in range(4)])
q(u'sec_cite_close', [Q4[u'sec_cite_sec'][i] + Q4[u'sec_cite_word'][i] - Q4[u'sec_cite_any'][i]
                      for i in range(4)])

# ---------- 熵的位账 ----------
def bitlist(s):
    out = []
    ts = tokrun(s, WORDCH)
    for k, t in enumerate(ts):
        nxt = ts[k + 1] if k + 1 < len(ts) else None
        if t[0].isdigit() and nxt is not None and nxt[0].lower() == u'bits' and set(t[3]) <= set(u' \t\n\r'):
            out.append(t[0])
    return out


q(u'bit_any', [len(bitlist(t)) for t in TXT])
q(u'bit_set', [sorted(set(bitlist(t))) for t in TXT])
for b in BITS:
    q(u'bit_%s' % b, [occ(t, b + u' bits') for t in TXT])
q(u'bit_close', [Q4[u'bit_any'][i] - sum(Q4[u'bit_%s' % b][i] for b in BITS) for i in range(4)])
q(u'bit_lost', sorted(set(Q4[u'bit_set'][0]) - set(Q4[u'bit_set'][2])))
q(u'bit_new', sorted(set(Q4[u'bit_set'][2]) - set(Q4[u'bit_set'][0])))

# ---------- 整行共用 / 子串再现 / 句子档 ----------
FAN = [pn(t) for t in TXT]
LN = [set(pn(l) for l in LST[i] if len(l) >= 20 and pn(l)) for i in range(4)]
q(u'lines_ge20', [len(s) for s in LN])
for a, b in ((0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3)):
    q(u'share_%s%s' % (TAGS[a], TAGS[b]), len(LN[a] & LN[b]))
q(u'share_all4', len(LN[0] & LN[1] & LN[2] & LN[3]))
q(u'only_T', len(LN[0] - LN[2]))
q(u'only_F', len(LN[2] - LN[0]))
q(u'union_TF', len(LN[0] | LN[2]))
q(u'share_close_TF', Q4[u'share_TF'] + Q4[u'only_T'] + Q4[u'only_F'] - Q4[u'union_TF'])
q(u'only_O', len(LN[1] - LN[3]))
q(u'only_N', len(LN[3] - LN[1]))
q(u'union_ON', len(LN[1] | LN[3]))
q(u'share_close_ON', Q4[u'share_ON'] + Q4[u'only_O'] + Q4[u'only_N'] - Q4[u'union_ON'])
q(u'carry_shared', Q4[u'share_TF'])
q(u'carry_sub_TF', len([l for l in LN[0] if l in FAN[2]]))
q(u'carry_sub_FT', len([l for l in LN[2] if l in FAN[0]]))
q(u'carry_sub_overlap', Q4[u'carry_sub_TF'] + Q4[u'carry_sub_FT'])
q(u'carry_caliber_gap', Q4[u'carry_sub_overlap'] - Q4[u'carry_shared'])
GEN = LN[0] & LN[2]
q(u'carry_ref', len([x for x in GEN if u'sp800' in x or u'doiorg' in x or u'nistgov' in x]))
q(u'carry_toc', len([x for x in GEN if x[:1].isdigit()]))
q(u'carry_prose', Q4[u'carry_shared'] - Q4[u'carry_ref'] - Q4[u'carry_toc'])
q(u'carry_split_close', Q4[u'carry_ref'] + Q4[u'carry_toc'] + Q4[u'carry_prose'] - Q4[u'carry_shared'])


def sents_buf(i):
    out, buf = [], u''
    for l in LST[i]:
        if not l:
            continue
        buf += (u' ' if buf else u'') + l
        parts = buf.split(u'. ')
        buf = parts.pop()
        out += [p for p in parts if len(p) >= 12]
    if len(buf) >= 12:
        out.append(buf)
    return [pn(x) for x in out if pn(x)]


def sents_join(i):
    j = u' '.join([l for l in LST[i] if l])
    return [pn(x) for x in j.split(u'. ') if len(x) >= 12 and pn(x)]


SE = [sents_join(i) for i in range(4)]
for i in range(4):
    assert set(sents_buf(i)) == set(SE[i]), (i, len(sents_buf(i)), len(SE[i]))
q(u'sent_n', [len(set(SE[i])) for i in range(4)])
q(u'sent_shared_TF', len(set(SE[0]) & set(SE[2])))
q(u'sent_shared_ON', len(set(SE[1]) & set(SE[3])))
q(u'sent_union_TF', len(set(SE[0]) | set(SE[2])))
q(u'sent_only_T', len(set(SE[0]) - set(SE[2])))
q(u'sent_only_F', len(set(SE[2]) - set(SE[0])))
q(u'sent_close_TF', Q4[u'sent_shared_TF'] + Q4[u'sent_only_T'] + Q4[u'sent_only_F'] - Q4[u'sent_union_TF'])
q(u'sent_share_th', len([x for x in (set(SE[0]) & set(SE[2]))
                         if re.search(u'(8|15|64|eight|fifteen) ?character', x)]))

# ---------- 锚池 ----------
SPECIAL = (u'8 characters', u'eight characters', u'12 characters', u'15 characters', u'64 characters',
           u'128 characters', u'memorized secret', u'blocklist', u'composition rules',
           u'pages.nist.gov', u'SP8210', u'superseded', u'initial public draft', u'2.1.1',
           u'Memorized Secrets', u'112 bits', u'multi-factor', u'copy and paste', u'single-factor')
POOL = set()
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if pn(l):
            POOL.add((t, l))
POOL = sorted(POOL)
CROSS = dict((p, len([k for k in range(4) if pn(p[1]) in FAN[k]])) for p in POOL)
q(u'pool_n', len(POOL))
q(u'pool_tag_n', [len([p for p in POOL if p[0] == TAGS[i]]) for i in range(4)])
for n in (1, 2, 3, 4):
    q(u'pool_%d' % n, len([p for p in POOL if CROSS[p] == n]))
q(u'pool_tiers', [Q4[u'pool_1'], Q4[u'pool_2'], Q4[u'pool_3'], Q4[u'pool_4']])
q(u'pool_close', sum(Q4[u'pool_tiers']) - Q4[u'pool_n'])
q(u'pool_maxlen', max(len(p[1]) for p in POOL))

# ---------- 本遍独有的第二口径 ----------
Q4[u'raw_chars'] = [len(t) for t in TXT0]
Q4[u'words'] = [len(t.split()) for t in TXT]
Q4[u'th_digit8_raw'] = [occ(t, u'8 characters') for t in TXT0]
Q4[u'ctx_raw_occ'] = [len(ctx_pairs(t)) for t in TXT0]
Q4[u'ctx_raw_set'] = [sorted(set([x[0] for x in ctx_pairs(t)])) for t in TXT0]
Q4[u'ctx_raw_close'] = [Q4[u'ctx_raw_occ'][i] - Q4[u'ctx_occ'][i] for i in range(4)]
assert Q4[u'ctx_raw_set'] == Q4[u'ctx_set'] and set(Q4[u'ctx_raw_close']) == set([0])
Q4[u'may_naive'] = [occ(t.upper(), u'MAY') for t in TXT]
Q4[u'may_gap'] = [Q4[u'may_naive'][i] - Q4[u'kw_may_ci'][i] for i in range(4)]
Q4[u'pw_lines'] = [len([l for l in LST[i] if u'password' in l.lower()]) for i in range(4)]
Q4[u'ms_lines'] = [len([l for l in LST[i] if u'memorized secret' in l.lower()]) for i in range(4)]
Q4[u'kw_lines'] = [len([l for l in LST[i] if any(w in l for w in NORMW)]) for i in range(4)]
Q4[u'blk_fused'] = [BS[i][u'block'][u'fused'] + BS[i][u'black'][u'fused'] for i in range(4)]
Q4[u'blk_ws'] = [BS[i][u'block'][u'ws'] + BS[i][u'black'][u'ws'] for i in range(4)]
Q4[u'blk_hy'] = [BS[i][u'block'][u'hy'] + BS[i][u'black'][u'hy'] for i in range(4)]
Q4[u'blk_g2'] = [BS[i][u'block'][u'g2'] + BS[i][u'black'][u'g2'] for i in range(4)]
Q4[u'blk_form_close'] = [FLAT[u'bl_word_any'][i]
                         - (Q4[u'blk_fused'][i] + Q4[u'blk_ws'][i] + Q4[u'blk_hy'][i]) for i in range(4)]
assert sum(Q4[u'blk_g2']) == 0 and set(Q4[u'blk_form_close']) == set([0]), Q4[u'blk_form_close']
PRIOR = dict((t, [k for k, v in SRCALL.items() if k != u'B59' and any(p in v for p in PATH)])
             for t in TAGS)

QN = len(Q4)
COMPARABLE = len([k for k in Q4 if k in FLAT or k in MEAS])


def QJ(k):
    v = Q4[k]
    return u' ⇎ '.join(map(str, v)) if isinstance(v, list) else str(v)


print(u'第四遍: 现取 %d 量, 可比 %d, 全等(未停机)' % (QN, COMPARABLE))
print(u'渲染字符 %s ｜ 两口径差 %s ｜ 原文件行 %s ⇎ 渲染行 %s' % (QJ(u'chars'), QJ(u'js_gap'),
                                                                QJ(u'lines'), QJ(u'rlines')))
print(u'门槛集 %s ｜ 草案词面 %d ⇎ 数字 %d ｜ ASVS 末格 %d 枚/%d 不同 命中旧 %d ⇎ 新 %d' % (
    Q4[u'ctx_set'], Q4[u'ctx_word_form'][2], Q4[u'ctx_digit_form'][2], Q4[u'asvs_ref_occ'],
    Q4[u'asvs_ref_distinct'], Q4[u'asvs_ref_inT'], Q4[u'asvs_ref_inF']))
print(u'强度词大写 SHALL %s ⇎ MUST %s ⇎ 小写 must %s ｜ 裸子串 MAY %s ⇎ token %s' % (
    Q4[u'kw_shall_u'], Q4[u'kw_must_u'], Q4[u'kw_must_l'], Q4[u'may_naive'], Q4[u'kw_may_ci']))
print(u'Sec. %s ⇎ Section %s ｜ 标题号 %d⇎%d 共用 %d ｜ 池 %d 分层 %s ｜ 词族 合写%s 空格%s 连字符%s' % (
    Q4[u'sec_cite_sec'], Q4[u'sec_cite_word'], Q4[u'sec_T_n'], Q4[u'sec_F_n'], Q4[u'sec_shared'],
    Q4[u'pool_n'], Q4[u'pool_tiers'], Q4[u'blk_fused'], Q4[u'blk_ws'], Q4[u'blk_hy']))

# ---------- 写注 ----------
AMET = CH[u'ameta']
FJ = lambda k: u' ⇎ '.join(map(str, FLAT[k]))
NT = []
add = lambda s: NT.append(s)

add(u'- 这些数从哪来(先说清不独立在哪): 全链四套实现——采集侧 `_pick59.py`(游标剥壳 + 逐量 findall) ⇎ 建条目侧 '
    u'`_mkB59.py`(整篇三次 re.sub + 全篇切词进 Counter; 扁平契约 _b59flat.json %d 键) ⇎ 门槛侧 `audit.py::_b59_scan()` '
    u'⇎ 本注第四遍(先把原文切成 正文/注释/标签 三型片段队列, 两口径剥壳与整篇/逐行渲染都从这一条队列按开关组装; '
    u'词法量全部回查两条 token 流(字母档 ⇎ 词字符档)而不是逐族写正则; ASVS 矩阵按表头单元名定列号。'
    u'现取 %d 量, 其中 %d 个与前两份契约同名可比, 逐键 assert 相等; 剩下 %d 个 `raw_chars`／`words`／`may_naive`／'
    u'`may_gap`／`th_digit8_raw`／`pw_lines`／`ms_lines`／`kw_lines`／`blk_fused`／`blk_ws`／`blk_hy` 只在“另一种口径”句里用)。'
    u'门槛侧快照与契约比对: 缺键 %d ⇎ 值不符 %d(门槛认 %d 键); 契约与采集侧共有 %d 量, 不符 %d。'
    u'DERIV[B59] %d 键／%d 个引用点, 编码区 %d 字符。**必须披露**: `_b59_scan` 的量测段是从 `_mkB59.py` 的 SCAN 段'
    u'机械抽出后插进门槛的(`_wire59.py` 插门前先在抽出体上跑一遍全键与全算式预演), 它的独立性不来自“另写一遍”, '
    u'而来自采集侧与本注这两套真独立实现各自与门槛一致。'
    % (len(FLAT), QN, COMPARABLE, QN - COMPARABLE, len(MISS), len(DIFF), len(A), len(TIE), len(DTIE),
       JJ[u'DN'], CH[u'deriv_points'], CH[u'enc_chars']))

add(u'- 剥壳刀在一库之内走了三种走法而同得一个数: 建条目侧“整篇三次 re.sub”、采集侧“find(< 游标各走一遍”、本注“三型片段队列按开关组装”。'
    u'四源 原文件 %s 字节 ⇎ 渲染 %s 字符 ⇎ 第二口径(只删标签、脚本正文留下) %s 字符, 两口径差 %s 字——'
    u'那 %d 字是脚本与样式的正文; 第二份 < 字符 %d 枚、js_gap=%d: 它是 Markdown, 同一把刀在它身上只折实体。'
    u'口径差也落在行数上: 原文件行 %s ⇎ 渲染行 %s, 非空行 %s ⇎ 渲染非空行 %s(旧规范 %d→%d、草案 %d→%d: '
    u'被删的整是 HTML 的缩进与空标签行)。壳形: 标签字符 %s 枚 ⇎ <script> %s ⇎ <style> %s ⇎ <table> %s ⇎ 表行 %s ⇎ '
    u'实体 %s ⇎ 竖线 %s ⇎ 粗体对 %s ⇎ MD 链接 %s; 最长行 %s 列。四份签名 %s, 去重 %d 种——同库四份没有两枚字节相同。'
    % (QJ(u'bytes'), QJ(u'chars'), QJ(u'chars_untagged'), QJ(u'js_gap'), sum(Q4[u'js_gap']),
       FLAT[u'lt_tags'][1], Q4[u'js_gap'][1], QJ(u'lines'), QJ(u'rlines'), QJ(u'nonblank'), QJ(u'rnonblank'),
       FLAT[u'nonblank'][0], FLAT[u'rnonblank'][0], FLAT[u'nonblank'][2], FLAT[u'rnonblank'][2],
       QJ(u'lt_tags'), QJ(u'script_tags'), QJ(u'style_tags'), QJ(u'table_tags'), QJ(u'tr_rows'),
       QJ(u'ent_all'), QJ(u'pipe_cells'), QJ(u'bold_marks'), QJ(u'md_links'), QJ(u'maxlen'), FJ(u'sha16'),
       FLAT[u'sig_distinct']))

add(u'- 主轴一(口令最短多长)的数不是抄来的, 是“值 + character(s)”这一族 token 邻接关系现推的: 命中处数 %s ⇎ 不同数值 %s 个 ⇎ '
    u'取值集合 %s(旧规范 %s ⇎ 验证标准 %s ⇎ 草案 %s ⇎ 备忘单 %s)。'
    u'记法分两档且只在并排时可见: 草案数字写法 %d 处 ⇎ 英文词写法 %d 处(“eight characters” 全库只有草案那 %d 处); '
    u'“8 characters” 四份分布 %s(旧规范 %d ⇎ 草案 %d), 两档相加校住命中处数, 四份闭合差 %s。'
    u'上界与门槛分家: “128 characters” 只在验证标准 %s 处(唯一写明“超过就拒收”的一份), “64 characters” %s 处四份都在; '
    u'同时含 8 与 15 两个门槛的文书 %d 份 ⇎ 含 12 的 %d 份 ⇎ 含 128 的 %d 份 ⇎ 写着 “eight characters” 的 %d 份。'
    u'强度也按行分档: 行内含“数+characters”且带大写 SHALL 的 %s 行 ⇎ 一个规范词都没有的 %s 行。'
    u'再核一面: “8 characters” 在未剥壳的原文件面 %s 次 ⇎ 剥壳渲染面 %s 次, 逐份差 %s; 把同一把邻接刀整个换到原文件面上重跑, '
    u'四份的取值集合 %s 与处数 %s 和渲染面一字不差——门槛句在这四份里都不跨标签, 这一族对剥壳不敏感(与上面的行数、非空行差正相反)。'
    % (QJ(u'ctx_occ'), QJ(u'ctx_distinct'), QJ(u'ctx_set'), Q4[u'ctx_set'][0], Q4[u'ctx_set'][1],
       Q4[u'ctx_set'][2], Q4[u'ctx_set'][3], FLAT[u'ctx_digit_form'][2], FLAT[u'ctx_word_form'][2],
       FLAT[u'th_word_eight'][2], FJ(u'th_digit8'), FLAT[u'th_digit8'][0], FLAT[u'th_digit8'][2],
       FJ(u'ctx_form_close'),
       FJ(u'th_digit128'), FJ(u'th_digit64'), FLAT[u'ctx_815_docs'], FLAT[u'ctx_12_only'],
       FLAT[u'ctx_128_only'], FLAT[u'ctx_eight_docs'], FJ(u'th_line_norm'), FJ(u'th_line_bare'),
       QJ(u'th_digit8_raw'), FJ(u'th_digit8'),
       u' ⇎ '.join([str(FLAT[u'th_digit8'][i] - Q4[u'th_digit8_raw'][i]) for i in range(4)]),
       QJ(u'ctx_raw_set'), QJ(u'ctx_raw_occ')))

add(u'- 强度词四档写法是同一条字母 token 流上分四次判的(建条目侧把整篇切词塞进 Counter, 采集侧逐词跑四条带字母边界的正则): '
    u'大写 SHALL %s ⇎ SHOULD %s ⇎ MAY %s ⇎ MUST %s——四份没有一个全大写 MUST, 可小写 must %s 处(草案另有首字母 %s 处), '
    u'“必须”这件事照样在。四份大写规范词合计 %s ⇎ 忽略大小写 %s, 差额 %s 全来自小写与首字母写法; '
    u'四词×四份的三账闭合合计 %d。切词与找子串也并排跑了一遍: “MAY” 的裸子串(忽略大小写)得 %s ⇎ token 档 %s, '
    u'逐份差 %s——这批规范文书里没有 maybe 那类词内命中, 两口径此处重合; 但子串口径会把它们算进来, 所以本条仍只取 token 档。'
    u'禁令也换档: SHALL NOT 大写 %s ⇎ 忽略大小写 %s(多出 %s 全是小写与首字母) ⇎ SHOULD NOT %s ⇎ %s(%s); '
    u'同一条 composition rules 的行里 SHOULD NOT %s 行(旧规范) ⇎ SHALL NOT %s 行(草案), 无规范词 %s; '
    u'周期改口令那句 SHOULD NOT %s ⇎ SHALL NOT %s, 加上“发现泄露才强制改” %s 处。'
    u'行处与词处也是两口径: 含 password 字样的行 %s 行 ⇎ password 词(单复合并) %s 个 ⇎ 含 memorized secret 的行 %s 行 ⇎ 词组 %s 处。'
    % (FJ(u'kw_shall_u'), FJ(u'kw_should_u'), FJ(u'kw_may_u'), FJ(u'kw_must_u'), FJ(u'kw_must_l'),
       FJ(u'kw_must_t'), FJ(u'kw_upper_total'), FJ(u'kw_ci_total'), FJ(u'kw_gap'), FLAT[u'kw_close_sum'],
       QJ(u'may_naive'), FJ(u'kw_may_ci'), QJ(u'may_gap'), FJ(u'kw_shallnot_u'), FJ(u'kw_shallnot_ci'),
       FJ(u'kw_shallnot_gap'), FJ(u'kw_shouldnot_u'), FJ(u'kw_shouldnot_ci'), FJ(u'kw_shouldnot_gap'),
       FJ(u'comp_shouldnot'), FJ(u'comp_shallnot'), FJ(u'comp_norm_free'), FJ(u'chg_shouldnot'),
       FJ(u'chg_shallnot'), FJ(u'mc_forcechange'), QJ(u'pw_lines'), FJ(u'tm_pw_any'), QJ(u'ms_lines'),
       FJ(u'tm_memorized')))

add(u'- 术语换代与它的桥: memorized secret 忽略大小写 %s 处(旧规范单数写法 “Memorized Secrets” %s 处) ⇎ password 单数 %s ⇎ '
    u'复数 %s ⇎ 合并全数 %s, 单复相加校住全数、四份闭合差 %s。桥句只有一份: “called … Memorized Secrets” 这类显式换算只在 '
    u'验证标准 %s 处(本遍按 called 后 0–3 个字符的窗口手探, 建条目侧用 called .{0,3} 正则), 草案重写定义的那句 '
    u'“intended to be memorized” 也只 %s 处(四份共 %s)。'
    u'黑名单一族分四形态才闭合: blocklist %s ⇎ blacklist %s ⇎ 带空格的 black list %s ⇎ black 词形合计 %s(闭合差 %s), '
    u'两词族全库 %s 枚(与两词形相加的闭合差 %s); 草案里带大写 SHALL 的 blocklist 定义行 %d 行。'
    u'形态账本遍现推: 合写(blocklist/blacklist 连体) ⇎ 纯空格 gap ⇎ 连字符 gap 三形态四份各为 %s／%s／%s, '
    u'三形相加 %d 与建条目侧词族正则的全库 %d 逐份闭合差 %s, 两字符 gap 全库 %d 枚——数据里只有单字符 gap 这一种断开写法。'
    % (FJ(u'tm_memorized'), FJ(u'tm_memorized_caps'), FJ(u'tm_pw_sing'), FJ(u'tm_pw_plural'), FJ(u'tm_pw_any'),
       FJ(u'tm_close'), FLAT[u'tm_bridge'][1], FLAT[u'tm_defline'][2], FJ(u'tm_defline'),
       FJ(u'mc_blocklist'), FJ(u'bl_blacklist'), FJ(u'bl_spaced'), FJ(u'bl_black'), FJ(u'bl_black_close'),
       FJ(u'bl_word_any'), FJ(u'bl_word_close'), FLAT[u'blk_def_lines'],
       QJ(u'blk_fused'), QJ(u'blk_ws'), QJ(u'blk_hy'),
       sum(Q4[u'blk_fused']) + sum(Q4[u'blk_ws']) + sum(Q4[u'blk_hy']),
       sum(FLAT[u'bl_word_any']), QJ(u'blk_form_close'), sum(Q4[u'blk_g2'])))

add(u'- 主轴二(谁在替谁说话)靠表格列位而不是行位置: 验证标准是 Markdown, 每行以竖线分格; 本遍先把 %d 张表头行按单元名 '
    u'(L1/L2/L3/CWE/NIST) 定出列号 {%s}, 建条目侧与采集侧都从行尾右数——两条路得到同一张矩阵: '
    u'要求 %s 行 ⇎ 行宽 %s 格 ⇎ 三列勾数 %s(合计 %d ⇎ 文件里勾号字符 %d 枚 ⇎ 表头图例行 %d 行, 闭合差 %d: '
    u'差的那一枚在 “✓ | Required” 图例行, 它不是任何一条要求) ⇎ CWE 号 %d 种 ⇎ 末格带号 %s 处 ⇎ 无号 %s 条 ⇎ 不同号 %s 枚。'
    u'把这些号拿去逐字撞两版规范的标题号集(本遍手拆“数字.数字”段并手看号后一个字符, 建条目侧用 (?m) 正则): '
    u'旧规范标题号 %d 枚 ⇎ 草案 %d 枚 ⇎ 两版共用 %d 枚 ⇎ 旧规范行首号 %s 个; 命中旧 %d ⇎ 命中新 %d, '
    u'换成整篇正文再撞仍是 %d ⇎ %d, 未命中清单旧侧 %d 枚 ⇎ 新侧 %d 枚, 闭合差 %d。'
    u'⇒ 这张第三方映射表的整列跟着旧版失效, 而“草案重排了标题号”是唯一能解释 0 命中的库内事实。'
    % (len(HDRC), u', '.join(u'%s:%d' % (k, v) for k, v in sorted(CIDX.items())), QJ(u'asvs_req_rows'),
       QJ(u'asvs_row_widths'), QJ(u'asvs_tick_cols'), FLAT[u'asvs_tick_total'], FLAT[u'asvs_tick_glyph'],
       FLAT[u'asvs_tick_legend'], FLAT[u'asvs_tick_close'], FLAT[u'asvs_cwe_distinct'], QJ(u'asvs_ref_occ'),
       QJ(u'asvs_rows_noref'), QJ(u'asvs_ref_distinct'), FLAT[u'sec_T_n'], FLAT[u'sec_F_n'],
       FLAT[u'sec_shared'], FJ(u'sec_head_n'), FLAT[u'asvs_ref_inT'], FLAT[u'asvs_ref_inF'],
       FLAT[u'asvs_ref_inT_text'], FLAT[u'asvs_ref_inF_text'], len(FLAT[u'asvs_ref_missT']),
       len(FLAT[u'asvs_ref_missF']), FLAT[u'asvs_ref_close']))

add(u'- 引用形态与自我标注各写各的: 直连 URL “pages.nist.gov” 只在验证标准 %s 处(其中写着 63-3 的 %d 处), '
    u'带空格 “NIST SP 800-63” %s ⇎ 无空格 “SP800-63B” 只在备忘单 %s 处; “800-63B” 字样四份共 %d 份文书自带, '
    u'三种形态同时非零的档数 %d。旧规范页里写自己被 “800-63-4” 废止 %s 处 ⇎ 草案自标 initial public draft %s 处 ⇎ '
    u'草案回指旧版 800-63-3 %s 处 ⇎ 验证标准 %s 处 ⇎ 旧规范 %s 处 ⇎ 全库链接数 %s。'
    u'“superseded” 一词两份各说一事: 旧规范说自己的 %d 句 ⇎ 备忘单说 OpenID 2.0 的 %d 句(该词出现 %s 处)。'
    u'条款引用前缀也换代: “Sec.” 写法 旧规范 %d ⇎ 草案 %d, 而 “Section” 全词 %d ⇎ %d, 两式相加校住合并计数(闭合差 %s)——'
    u'同一个条号在两代文书里换了前缀词, 所以按前缀词做全文检索会把草案侧读成 0。'
    % (FJ(u'cite_url_nist'), FLAT[u'asvs_url_head'], FJ(u'cite_spaced'), FJ(u'cite_unspaced'),
       FLAT[u'cite_63b_docs'], FLAT[u'cite_forms'], FJ(u'cite_rev4num'), FJ(u'cite_draftself'),
       FJ(u'cite_rev3num'), FLAT[u'cite_rev3num'][1], FLAT[u'cite_rev3num'][0], FJ(u'cite_http_any'),
       FLAT[u'sup_nist'], FLAT[u'sup_openid'], FJ(u'cite_superseded'),
       FLAT[u'sec_cite_sec'][0], FLAT[u'sec_cite_sec'][2], FLAT[u'sec_cite_word'][0],
       FLAT[u'sec_cite_word'][2], FJ(u'sec_cite_close')))

add(u'- 同形不同物与位数账: 串 “2.1.1” 逐字出现在 %d 份文书、共 %s 处, 但它在验证标准是带粗体的要求号(**2.1.1** %d 处, '
    u'该份 %s 处全是这一族), 在草案只是一枚更长条款号的尾巴(Sec. 4.2.1.1, 该份 %s 处), 旧规范与备忘单 %s⇎%s 处; '
    u'“5.1.1.2” 更分裂: %s 处——验证标准末格用得最多(%d), 旧规范里的真条款(%d), 草案 %d。'
    u'本遍把粗体要求号按 “**切段后取奇数段” 数得 %d 族, 与建条目侧的 count(**2.) 同数 %d。'
    u'熵的位账换代可逐字核: 出现集合 旧 %s ⇎ 验证 %s ⇎ 草案 %s ⇎ 备忘单 %s, 草案丢 %s ⇎ 增 %s; '
    u'112 bits %s ⇎ 64 %s ⇎ 32 %s ⇎ 20 %s ⇎ 40 %s, 五种相加校住 “N bits” 全数 %s(余量 %s)。'
    u'位数用 token 邻接判(数字 token + 纯空白 gap + bits 词), 与建条目侧的 (?i)\\d+\\s*bits 同数——四份里位数只有这五种。'
    % (FLAT[u'id_211_docs'], FJ(u'id_211_occ'), FLAT[u'id_211_bold'], FLAT[u'id_211_occ'][1],
       FLAT[u'id_211_occ'][2], FLAT[u'id_211_occ'][0], FLAT[u'id_211_occ'][3], FJ(u'asvs_5112'),
       FLAT[u'asvs_5112'][1], FLAT[u'asvs_5112'][0], FLAT[u'asvs_5112'][2], Q4[u'asvs_bold_ids'],
       FLAT[u'asvs_bold_ids'], FLAT[u'bit_set'][0], FLAT[u'bit_set'][1], FLAT[u'bit_set'][2],
       FLAT[u'bit_set'][3], FJ(u'bit_lost'), FJ(u'bit_new'), FJ(u'bit_112'), FJ(u'bit_64'),
       FJ(u'bit_32'), FJ(u'bit_20'), FJ(u'bit_40'), FJ(u'bit_any'), FJ(u'bit_close')))

add(u'- 跨文书搬运记三口径, 且体裁要拆: 整行集交(≥20 字符、归一后求交)得 旧⇎验证 %d ⇎ 两代 NIST %d ⇎ 验证⇎草案 %d ⇎ '
    u'旧⇎备忘 %d ⇎ 两家 OWASP %d ⇎ 草案⇎备忘 %d ⇎ 四份全同 %s; 两代 NIST 侧: 共用 %d ⇎ 旧独有 %d ⇎ 新独有 %d, '
    u'并集 %d(闭合差 %d)。两家 OWASP 文书整行共用 %d 条 ⇎ 句子档却共用 1 句——两档的切法本就不同(按行 ⇎ 按 “. ” 断句), '
    u'所以这条只在注里报数, 不进判词。'
    u'“在对方正文里逐字再现一次”口径 T→F %d ⇎ F→T %d, 合计 %d, 比集交多 %d 条(它把别人的子串也算搬走了)。'
    u'共用那 %d 行按体裁拆: 参考条目 %d ⇎ 章节号行 %d ⇎ 正文行 %d(相加校住, 差 %d)——真正“同一条声明原样搬过去”的是 %d 行。'
    u'句子档另算: 每份句子数(≥12 字符、按 “. ” 断句) %s ⇎ 两代共用 %d 句 ⇎ 两家 OWASP 共用 %d 句, '
    u'并集 %d ⇎ 独有 %d⇎%d(闭合差 %d); 共用句里含门槛数字的只有 %d 句 ⇒ 两份各写各的门限。'
    u'本遍把断句实现成“非空行先 join 成一个串再切”, 与建条目侧的逐行游标缓存逐份 set 全等(四份都 assert 过)。'
    % (FLAT[u'share_TO'], FLAT[u'share_TF'], FLAT[u'share_OF'], FLAT[u'share_TN'], FLAT[u'share_ON'],
       FLAT[u'share_FN'], FLAT[u'share_all4'], FLAT[u'share_TF'], FLAT[u'only_T'], FLAT[u'only_F'],
       FLAT[u'union_TF'],
       FLAT[u'share_close_TF'], FLAT[u'share_ON'], FLAT[u'carry_sub_TF'], FLAT[u'carry_sub_FT'],
       FLAT[u'carry_sub_overlap'], FLAT[u'carry_caliber_gap'], FLAT[u'carry_shared'], FLAT[u'carry_ref'],
       FLAT[u'carry_toc'], FLAT[u'carry_prose'], FLAT[u'carry_split_close'], FLAT[u'carry_prose'],
       FJ(u'sent_n'), FLAT[u'sent_shared_TF'], FLAT[u'sent_shared_ON'], FLAT[u'sent_union_TF'],
       FLAT[u'sent_only_T'], FLAT[u'sent_only_F'], FLAT[u'sent_close_TF'], FLAT[u'sent_share_th']))

add(u'- 机制词的词处 ⇎ 行处两口径都登记(行处=该份里命中过的渲染行数): blocklist %s⇎%s ⇎ breach %s⇎%s ⇎ '
    u'限流 %s⇎%s ⇎ 锁定 %s⇎%s ⇎ 多因子 %s⇎%s ⇎ 熵 %s⇎%s ⇎ composition rules %s⇎%s ⇎ copy and paste %s⇎%s ⇎ '
    u'hint %s⇎%s ⇎ arbitrary %s⇎%s ⇎ 周期性 %s⇎%s ⇎ force a change %s⇎%s。'
    u'这几族本遍是分别按“子串 ⇎ token 前缀 ⇎ 合写+分写”三条路现推的(建条目侧一律一条正则): '
    u'“lock” 词族按 token 前缀数(包含 unlock)与 (?i)\\block\\w* 同数 %s, 限流按字符面 “rate”+0 或 1 个任意字符+“limit” '
    u'与 (?i)rate.?limit 同数 %s——连字符写法 rate-limiting 与词尾变形 rate-limited 都在这条子串口径里算一处, '
    u'所以这一族本遍不能只停在 token 邻接档。'
    % (FJ(u'mc_blocklist'), FJ(u'mc_blocklist_lines'), FJ(u'mc_breach'), FJ(u'mc_breach_lines'),
       FJ(u'mc_ratelimit'), FJ(u'mc_ratelimit_lines'), FJ(u'mc_lockout'), FJ(u'mc_lockout_lines'),
       FJ(u'mc_multifactor'), FJ(u'mc_multifactor_lines'), FJ(u'mc_entropy'), FJ(u'mc_entropy_lines'),
       FJ(u'mc_composition'), FJ(u'mc_composition_lines'), FJ(u'mc_copypaste'), FJ(u'mc_copypaste_lines'),
       FJ(u'mc_hint'), FJ(u'mc_hint_lines'), FJ(u'mc_arbitrary'), FJ(u'mc_arbitrary_lines'),
       FJ(u'mc_periodic'), FJ(u'mc_periodic_lines'), FJ(u'mc_forcechange'), FJ(u'mc_forcechange_lines'),
       FJ(u'mc_lockout'), FJ(u'mc_ratelimit')))

add(u'- 锚账与池账(归属由正文现推, 不读旁注): 池 %d 串(每源 %s), 按命中源数分四档 %d⇎%d⇎%d⇎%d(相加校住, 差 %d), '
    u'池内最长行 %d 列。正文带标签锚 %d 处 ⇎ 去重 %d 串 ⇎ 逐标签 T %d ⇎ O %d ⇎ F %d ⇎ N %d, 归属检查 %d 次, 错配 %d。'
    u'要如实报一档: 本条挑的锚全部只落在自己那一源(单源 %d ⇎ 穿两或三源 %d ⇎ 四源全现 %d)——池里四源全现的只有 %d 串, '
    u'它们是被两代 NIST 与两家 OWASP 的站点壳共用的行而非可断言的句子, 所以跨源锚退回单源档; '
    u'“同一个门槛四份各写各的”这一条本来就体现在 %d 组互不相同的取值集合上, 不体现在共线上。'
    u'这 %d 个原子引文全部命中各自源文件(atomcheck; 编码区 %d 字符, 摘要窗口每源取 160–200 行宽); '
    u'这四份原料与此前条目的共用情况: %s。'
    % (FLAT[u'pool_n'], FJ(u'pool_tag_n'), FLAT[u'pool_1'], FLAT[u'pool_2'], FLAT[u'pool_3'], FLAT[u'pool_4'],
       FLAT[u'pool_close'], FLAT[u'pool_maxlen'], AMET[u'anchor_total'], AMET[u'anchor_distinct'],
       FLAT[u'tag_T'], FLAT[u'tag_O'], FLAT[u'tag_F'], FLAT[u'tag_N'], AMET[u'checks'], AMET[u'anchor_err'],
       AMET[u'anchor_single'], AMET[u'anchor_cross'], AMET[u'anchor_all4'], FLAT[u'pool_4'],
       len(set([tuple(x) for x in FLAT[u'ctx_set']])), len(ATOMS), CH[u'enc_chars'],
       u'／'.join(u'%s(%s): %s' % (t, LBL[t], u' ⇎ '.join(PRIOR[t]) if PRIOR[t] else u'首次入库')
                  for t in TAGS)))

add(u'- 只在本机或库外成立、因而一条都不进判词的事: ①这五份文件(含未进 SRC 的 `raw/pwd/ncsc_passwords.html`)的磁盘 mtime '
    u'都在 2026-10-22 08:54–08:58, 它与页脚自陈的年份无关, 也不能用来判“哪份是现行版”; ②草案此刻是否已定稿、'
    u'旧规范页的废止横幅何时挂上, 库内没有对照物, 只有那 %d 处 “initial public draft” 自标; '
    u'③备忘单那句 “(NIST SP800-63B)” 究竟指旧规范那一版还是草案这一版——“800-63B” 这个串在库里同时出现在 %d 份文书, '
    u'不可由在库文件判定它归给哪一版; ④“为什么这样改”只有各文自己的措辞在库, 属取词过程而非复算; '
    u'⑤渲染行 ⇎ 原文件行、词处 ⇎ 行处这类口径差是本库的剥壳选择, 不是文书自身的性质; ⑥未入库那份 NCSC 文档没有进门槛'
    u'(门槛认 %d 份原料), 它只能作为“另有一家在写同一件事”的旁证留在注里。'
    % (FLAT[u'cite_draftself'][2], FLAT[u'cite_63b_docs'], len(SRCALL[u'B59'])))

body = NL.join(NT)
T = io.open(ENTRY, encoding='utf-8').read()
head = u'## ⛓解读注'
i = T.index(head)
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(T[:i] + head + NL + NL + body + NL)
print(u'注已写: %d 段 ｜ 契约 %d 键全对齐门槛 ⇎ 采集侧共有 %d 量零不符 ｜ 第四遍现取 %d 量／%d 个可比全等 ｜ 注体 %d 字符' % (
    len(NT), len(FLAT), len(TIE), QN, COMPARABLE, len(body.replace(NL, u''))))
