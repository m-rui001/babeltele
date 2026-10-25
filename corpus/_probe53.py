# -*- coding: utf-8 -*-
"""B53 侦察: 同一份 FIPS 202 的四种序列化——官方 txt ⇎ 官方 html ⇎ 本地 pdftotext -layout ⇎ 本地 plain。
两份是本机现生的(可重跑), 两份是下载的; 本脚本把它们放在同一套口径下数一遍, 并回答三个问题:
① 官方 txt 与本机 txt 抽取是不是同一份内容(词集包含关系 ⇎ 公共片段长度)?
② 官方 html 到底是全文还是落地页(与全文的词集交有多大)?
③ 版式里的数学符号(ω ⇎ ← ⇎ ⊕)在哪一层还活着(文本层计数 ⇎ PDF 资源层证据)?
结果落 corpus/_b53probe.json 与 corpus/_b53probe.txt, 只作选材与量纲, 不进判词。"""
import io, os, re, sys, json, hashlib, subprocess, collections

sys.stdout.reconfigure(encoding='utf-8')
ROOT = u'corpus/raw'
NL = u'\n'
PDF = os.path.join(ROOT, u'fips202.pdf')
OFF_T = os.path.join(ROOT, u'fips202.txt')
OFF_H = os.path.join(ROOT, u'fips202.html')
GEN_L = os.path.join(ROOT, u'fips202_pdflayout.txt')
GEN_P = os.path.join(ROOT, u'fips202_plain.txt')


def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline=NL).write(s)


def sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def regen():
    for flags, out in (([u'-layout'], GEN_L), ([], GEN_P)):
        cmd = [u'pdftotext'] + flags + [PDF, out]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        assert r.returncode == 0 and os.path.exists(out), (cmd, r.stderr[:200])


regen()
NAME = {u'off_txt': OFF_T, u'off_html': OFF_H, u'gen_layout': GEN_L, u'gen_plain': GEN_P}
X = dict((k, rd(v)) for k, v in NAME.items())
BYTES = dict((k, os.path.getsize(v)) for k, v in NAME.items())
TAGLESS = re.sub(u'<[^>]+>', u' ', X[u'off_html'])
BODY = {u'off_txt': X[u'off_txt'], u'off_html': TAGLESS,
        u'gen_layout': X[u'gen_layout'], u'gen_plain': X[u'gen_plain']}


def words(s):
    return re.findall(u'[A-Za-z0-9]+', s.lower())


def nwords(s):
    return len(words(s))


W = dict((k, set(words(v))) for k, v in BODY.items())
M = {}
M[u'bytes'] = dict((k, BYTES[k]) for k in NAME)
M[u'chars'] = dict((k, len(X[k])) for k in NAME)
M[u'lines'] = dict((k, X[k].count(NL)) for k in NAME)
M[u'nonblank'] = dict((k, len([l for l in X[k].split(NL) if l.strip()])) for k in NAME)
M[u'wocc'] = dict((k, nwords(v)) for k, v in BODY.items())
M[u'wset'] = dict((k, len(W[k])) for k in W)
M[u'html_tags'] = len(re.findall(u'<[a-zA-Z]', X[u'off_html']))
M[u'html_tagkinds'] = len(set(re.findall(u'<([a-zA-Z][a-zA-Z0-9]*)', X[u'off_html'])))
M[u'html_a'] = X[u'off_html'].count(u'<a ')
M[u'html_title'] = (re.findall(u'<title>([^<]*)</title>', X[u'off_html']) or [u''])[0].strip()
M[u'pdf_pages'] = len(re.findall(rb'/Type\s*/Page[^s]', open(PDF, 'rb').read()))
M[u'pdf_streams'] = open(PDF, 'rb').read().count(b'stream')

# 伪码与数学符号: 文本层存活率
SYM = {u'StepN': u'Step \\d', u'AlgorithmN': u'Algorithm \\d', u'omega': u'ω',
       u'leftarrow': u'←', u'oplus': u'⊕', u'pi': u'π', u'ell': u'ℓ', u'bar': u'‾',
       u'sponge': u'(?i)sponge', u'absorb': u'(?i)absorb', u'squeeze': u'(?i)squeeze',
       u'rate': u'(?i)\\brate\\b', u'capacity': u'(?i)capacity', u'padding': u'(?i)pad(128|ding)?',
       u'appendix': u'Appendix [A-Z]', u'sha3': u'(?i)sha3', u'shakexof': u'(?i)shake'}
M[u'sym'] = dict((k, [len(re.findall(SYM[x], BODY[k])) for x in sorted(SYM)])
                 for k in sorted(BODY))
M[u'symk'] = sorted(SYM)

# 官方 txt ⇎ 本机 layout: 词序列层面的包含与最大公共片段
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
        out.append((e - s, s))
        s = e
    return out


def flat(s):
    return re.sub(u'\\s+', u'', s)


FL = dict((k, flat(BODY[k])) for k in BODY)
M[u'run_layout_vs_off'] = [x[0] for x in runmax(FL[u'gen_layout'], FL[u'off_txt'])]
M[u'run_plain_vs_off'] = [x[0] for x in runmax(FL[u'gen_plain'], FL[u'off_txt'])]
M[u'run_layout_vs_plain'] = [x[0] for x in runmax(FL[u'gen_layout'], FL[u'gen_plain'])]
M[u'run_html_vs_off'] = [x[0] for x in runmax(FL[u'off_html'], FL[u'off_txt'])]
M[u'wset_inter'] = {u'layout_off': len(W[u'gen_layout'] & W[u'off_txt']),
                    u'plain_off': len(W[u'gen_plain'] & W[u'off_txt']),
                    u'html_off': len(W[u'off_html'] & W[u'off_txt']),
                    u'layout_plain': len(W[u'gen_layout'] & W[u'gen_plain'])}
M[u'wset_only'] = {u'off_not_layout': len(W[u'off_txt'] - W[u'gen_layout']),
                   u'layout_not_off': len(W[u'gen_layout'] - W[u'off_txt']),
                   u'plain_not_layout': len(W[u'gen_plain'] - W[u'gen_layout']),
                   u'off_not_plain': len(W[u'off_txt'] - W[u'gen_plain'])}
M[u'sha'] = dict((k, sha(X[k])[:16]) for k in X)

# 行结构: 同一句话在 layout ⇎ plain 里各占几行
def sent_lines(s, k=48):
    L = [l.strip() for l in s.split(NL) if l.strip()]
    return L


LS = dict((k, sent_lines(X[k])) for k in X)
M[u'linelen_med'] = dict((k, sorted(len(x) for x in v)[len(v) // 2]) for k, v in LS.items())
M[u'lines_gt120'] = dict((k, len([x for x in v if len(x) > 120])) for k, v in LS.items())
M[u'lines_le20'] = dict((k, len([x for x in v if len(x) <= 20])) for k, v in LS.items())
json.dump({u'meas': M}, io.open(u'corpus/_b53probe.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# ---------- 可复现性: 同一命令跑两遍, 产物须字节相同(rung-1 证据, 照 B48 的先例) ----------
TMP = os.path.join(ROOT, u'_b53det.txt')
subprocess.run([u'pdftotext', u'-layout', PDF, TMP], check=True)
h_new = hashlib.sha256(open(TMP, 'rb').read()).hexdigest()
h_keep = hashlib.sha256(open(GEN_L, 'rb').read()).hexdigest()
M[u'regen_equal'] = h_new == h_keep
M[u'regen_sha'] = h_keep[:16]
os.remove(TMP)

# ---------- 候选锚池: 逐源归属 + 跨源命中(挑引文用, 不作判词) ----------
def PN(s):
    s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
    s = re.sub(u'[’\'"\u2018\u2019`´]+', u'', s)
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


FN = dict((k, PN(v)) for k, v in BODY.items())
ORDER = [u'off_txt', u'off_html', u'gen_layout', u'gen_plain']
POOL, SEEN = [], set()
for src in ORDER:
    for l in X[src].split(NL):
        s = l.strip()
        if len(s) < 24 or NL in s:
            continue
        n = PN(s)
        if len(n) < 16 or n in SEEN:
            continue
        SEEN.add(n)
        hits = tuple(k for k in ORDER if n in FN[k])
        if not hits:
            continue
        POOL.append([src, list(hits), s])
M[u'pool_n'] = len(POOL)
M[u'pool_own'] = dict((k, len([p for p in POOL if p[0] == k])) for k in ORDER)
M[u'pool_multi'] = len([p for p in POOL if len(p[1]) > 1])
M[u'pool_cross'] = dict(('%s×%d层' % a, c) for a, c in sorted(collections.Counter(
    (p[0], len(p[1])) for p in POOL if len(p[1]) > 1).items()))
json.dump({u'meas': M, u'pool': POOL}, io.open(u'corpus/_b53probe.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
assert M[u'regen_equal'] and M[u'pool_n'] > 200 and M[u'pool_multi'] > 0, M
print(u'池 %d 条(自有 %d ⇎ 跨层 %d) ｜ 重跑字节相同 %s' % (
    M[u'pool_n'], M[u'pool_n'] - M[u'pool_multi'], M[u'pool_multi'], M[u'regen_equal']))
print(u'跨层分布(源⇎命中层数⇎条数): %s' % u' ⇎ '.join(
    u'%s %d' % (k, c) for k, c in sorted(M[u'pool_cross'].items())))

OUT = [u'# B53 侦察(FIPS 202 四种序列化; 本机 pdftotext 现生两份, 官方两份), 仅选材与量纲']
for k in sorted(M):
    if k not in (u'sym', u'symk', u'sha'):
        OUT.append(u'%-22s %s' % (k, M[k]))
for i, sname in enumerate(M[u'symk']):
    OUT.append(u'sym %-10s %s' % (sname, u' ⇎ '.join(
        u'%s %d' % (n, M[u'sym'][n][i]) for n in sorted(M[u'sym']))))
OUT.append(u'sha ' + u' ⇎ '.join(u'%s %s' % (k, M[u'sha'][k]) for k in sorted(M[u'sha'])))
wr(u'corpus/_b53probe.txt', NL.join(OUT) + NL)
print(NL.join(OUT[:14]))
print(u'符号表: ' + u' ⇎ '.join(u'%s %d/%d/%d/%d' % (M[u'symk'][i], M[u'sym'][u'gen_layout'][i],
      M[u'sym'][u'gen_plain'][i], M[u'sym'][u'off_txt'][i], M[u'sym'][u'off_html'][i])
      for i in range(len(M[u'symk']))))
