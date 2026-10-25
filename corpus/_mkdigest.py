# 通用: 把条目里 ⟨…⟩ 锚点在 raw 源中的相邻句段拼成 [[原始语料]] 摘要段(逐字, 仅剔页眉/折行)
# 用法: python corpus/_mkdigest.py <tag> <entry.md> <raw.txt> [左窗=110] [右窗=90]
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

tag, ENTRY, RAW = sys.argv[1], sys.argv[2], sys.argv[3]
WL = int(sys.argv[4]) if len(sys.argv) > 4 else 110
WR = int(sys.argv[5]) if len(sys.argv) > 5 else 90

C = re.sub(r'\s+', ' ', open(RAW, encoding='utf-8').read())
C = re.sub(r'\s*\d{1,3}\s+investigation report CSB public record\s+', ' ', C, flags=re.I)
C = re.sub(r'\s+CSB public record as pertaining to\s+', ' ', C, flags=re.I)


def pairs(s):
    out = []
    for i, ch in enumerate(s):
        t = ch.lower()
        for a, b in ((u'’', "'"), (u'‘', "'"), (u'“', '"'), (u'”', '"'), (u'´', '')):
            t = t.replace(a, b)
        t = t.replace('"', '').replace("'", '')
        for d in u'‐‑‒–—―−':
            t = t.replace(d, '-')
        for x in t:
            k = x if ((x.isalnum() and x.isascii()) or u'一' <= x <= u'鿿' or x in ' -.') else ' '
            if k != ' ' or (out and out[-1][0] != ' '):
                out.append((k, i))
    return out


P = pairs(C)
N = re.sub(r' +', ' ', ''.join(c for c, _ in P))
t = open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\\n(.*?)\\n\\n## ', t, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
spans, miss = [], []
for a in atoms:
    na = re.sub(r' +', ' ', ''.join(c for c, _ in pairs(a))).strip()
    i = N.find(na)
    if i < 0:
        miss.append(a)
        continue
    spans.append((P[i][1], P[min(i + len(na) - 1, len(P) - 1)][1] + 1))


def snap(a, b):
    x = max(C.rfind('. ', max(0, a - WL), a), C.rfind('? ', max(0, a - WL), a),
            C.rfind('.” ', max(0, a - WL), a),
            C.rfind(u'。', max(0, a - WL), a), C.rfind(u'？', max(0, a - WL), a),
            C.rfind(u'！', max(0, a - WL), a))
    if x >= 0:
        a = x + (2 if C[x] in '.?' else 1)
    r = min([k for k in (C.find('. ', b, b + WR), C.find(u'。', b, b + WR),
                         C.find(u'？', b, b + WR), C.find(u'！', b, b + WR),
                         C.find(u'”', b, b + WR)) if k >= 0] or [-1])
    return a, ((r + 1) if r >= 0 else min(b + 25, len(C)))


sp = sorted(snap(a, b) for a, b in spans)
merged = []
for a, b in sp:
    if merged and a <= merged[-1][1] + 30:
        merged[-1][1] = max(merged[-1][1], b)
    else:
        merged.append([a, b])
digest = '\n\n'.join(C[a:b].strip() for a, b in merged)
print('%s: atoms=%d miss=%d blocks=%d atom_chars=%d digest_chars=%d'
      % (tag, len(atoms), len(miss), len(merged), sum(b - a for a, b in spans), len(digest)))
for m in miss:
    print('MISS', ascii(m[:80]))
if miss:
    sys.exit(1)
head, rest = t.split(u'## [[原始语料|ORIGINAL]]\n', 1)
cut = rest.index(u'## ⟪BabelTele')
open(ENTRY, 'w', encoding='utf-8').write(head + u'## [[原始语料|ORIGINAL]]\n' + digest
                                       + u'\n\n' + rest[cut:])
