# -*- coding: utf-8 -*-
# README 表生成器: 逐条实测 enc/anchors/anchorL/outsideL/保留率/vs raw, 并打印合计行
# 用法: python -X utf8 corpus/_v3table.py
import io, os, re, sys, glob

sys.stdout.reconfigure(encoding='utf-8')


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


rows = []
for path in sorted(glob.glob('corpus/babeltele/B*.md')):
    tag = os.path.basename(path).split('_')[0]
    t = io.open(path, encoding='utf-8', errors='replace').read()
    enc = re.search(u'⟪BabelTele⟫\\n(.*?)\\n\\n## ', t, re.S).group(1)
    ats = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
    dig = re.search(r'\[\[原始语料\|ORIGINAL\]\]\n(.*?)\n\n## ⟪BabelTele', t, re.S).group(1)
    an = ''.join(ats)
    ou = re.sub(u'⟨[^⟩]*⟩', '', enc, flags=re.S)
    rawlen = 0
    for line in re.findall(r'^src: (.*)$', t, re.M):
        for m in re.findall(r'corpus/raw/\S+?\.(?:txt|md|html|tab|json)', line):
            if os.path.exists(m):
                rawlen += os.path.getsize(m)
    raw_chars = len(pn(io.open(m, encoding='utf-8', errors='replace').read())) if rawlen else 0
    rows.append(dict(tag=tag, enc=len(enc), n=len(ats), al=len(re.findall(r'[A-Za-z]', an)),
                     ol=len(re.findall(r'[A-Za-z]', ou)),
                     han=len(re.findall(u'[\\u4e00-\\u9fff]', ou)),
                     dig=len(dig), raw=raw_chars, uniq=len(set(enc.replace('\n', '')))))

print('| 条目 | 编码 | 锚数 | 锚内字母 | 锚外字母 | 汉字 | 摘要段 | 保留率↓ | vs raw↓ |')
print('|---|---|---|---|---|---|---|---|---|')
tot = dict(enc=0, n=0, al=0, ol=0, han=0, dig=0)
for r in rows:
    for k in tot:
        tot[k] += r[k]
    print('| %s | %d | %d | %d | %d | %d | %s | %s | %s |' % (
        r['tag'], r['enc'], r['n'], r['al'], r['ol'], r['han'],
        '{:,}'.format(r['dig']),
        '%.1f%%' % (100.0 * r['enc'] / r['dig']) if r['dig'] else '-',
        '%.3f%%' % (100.0 * r['enc'] / r['raw']) if r['raw'] else '-'))
print('| 合计(%d 条) | %s | %d | %s | %d | %d | %s | %s | — |' % (
    len(rows), '{:,}'.format(tot['enc']), tot['n'], '{:,}'.format(tot['al']),
    tot['ol'], tot['han'], '{:,}'.format(tot['dig']),
    '%.1f%%' % (100.0 * tot['enc'] / tot['dig'])))
