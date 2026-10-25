# -*- coding: utf-8 -*-
# 回剪(v3)自检: 逐锚核验 + (思维链条目)锚必须落在 reasoning 区内 + 指标打印
# 用法: python -X utf8 corpus/_v3check.py <entry.md> <raw.(txt|md)> [cot]
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

entry, raw_path = sys.argv[1], sys.argv[2]
is_cot = len(sys.argv) > 3 and sys.argv[3] == 'cot'

def pairs(s):
    o = []
    for ch in s.lower():
        for a, b in ((u'’', "'"), (u'‘', "'"), (u'“', '"'), (u'”', '"'), (u'´', '')):
            ch = ch.replace(a, b)
        ch = ch.replace('"', '').replace("'", '')
        for d in u'‐‑‒–—―−':
            ch = ch.replace(d, '-')
        k = ch if ((ch.isalnum() and ch.isascii()) or u'一' <= ch <= u'鿿' or ch in ' -.') else ' '
        if k != ' ' or (o and o[-1] != ' '):
            o.append(k)
    return ''.join(o)

def pn(s):
    return re.sub(r' +', ' ', pairs(s)).strip()

R = pn(re.sub(r'\s+', ' ', io.open(raw_path, encoding='utf-8').read()))
t = io.open(entry, encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\\n(.*?)\\n\\n## ', t, re.S).group(1)
ats = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
region = ''
if is_cot:
    src = io.open(raw_path, encoding='utf-8').read()
    region = pn(src[src.index(u'## [[REASONING]]'):])
miss = [a for a in ats if pn(a) not in R]
out = [a for a in ats if is_cot and pn(a) not in region]
an = ''.join(ats)
ou = re.sub(u'⟨[^⟩]*⟩', '', enc, flags=re.S)
print('%-46s enc=%5d anchors=%3d atom_chars=%5d anchorL=%5d outsideL=%4d han=%4d en=%.0f%%' % (
    entry.split('/')[-1], len(enc), len(ats), sum(len(a) for a in ats),
    len(re.findall(r'[A-Za-z]', an)), len(re.findall(r'[A-Za-z]', ou)),
    len(re.findall(u'[\\u4e00-\\u9fff]', ou)),
    100.0 * (len(re.findall(r'[A-Za-z]', an)) + len(re.findall(r'[A-Za-z]', ou))) /
    max(1, len(re.findall(r'[A-Za-z]', an)) + len(re.findall(r'[A-Za-z]', ou)) + len(re.findall(u'[\\u4e00-\\u9fff]', ou)))))
print('  miss_in_raw=%d %s' % (len(miss), [m[:60] for m in miss]))
if is_cot:
    print('  miss_in_reasoning=%d %s' % (len(out), [m[:60] for m in out]))
d = re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', t, re.S).group(1)
print('  digest=%d retention=%.1f%%' % (len(d), 100.0 * len(enc) / len(d)))
