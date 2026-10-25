# -*- coding: utf-8 -*-
# 多源条目摘要段生成(用于 B27 这类跨模型对照条): 每条 raw 只取命中于它的锚点拼窗口, 分节带标签写回
# 用法: python -X utf8 corpus/_mkdigest3.py <tag> <entry.md> <lbl1> <raw1> <wl1> <wr1> [<lbl2> <raw2> <wl2> <wr2> ...]
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')

tag, ENTRY = sys.argv[1], sys.argv[2]
GROUPS = [sys.argv[i:i + 4] for i in range(3, len(sys.argv), 4)]


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


ENT_SG = ((u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'),
          (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'),
          (u'&#215;', u'x'), (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"),
          (u'&mdash;', u'-'), (u'&ndash;', u'-'), (u'&deg;', u'deg'), (u'&infin;', u'inf'),
          (u' ', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
          (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->'))


def render(path, fill=u''):
    """真带标签的 HTML 按渲染文本开窗(注释删除; 分段/格标签换成空格; 行内标签按 fill 替——
    '' 得粘面 "</a>."→"2028.", ' ' 得断面 "2028 ."); 实体还原; 已渲染成纯文本的 .html 原样返回。
    建条目侧的剥壳层本就分两代(B58/B59 用游标粘面, B60 用正则断面), 所以两面都试, 取命中锚多的一面。"""
    s = io.open(path, encoding='utf-8', errors='replace').read()
    dt = bool(re.match(u'(?is)\\s*(<!doctype html|<html)', s[:400]))
    if dt:
        s = re.sub(u'(?s)<!--.*?-->', u' ', s)
        s = re.sub(u'(?is)</?(?:td|th|tr|br|p|div|li|ul|ol|dl|dt|dd|table|thead|tbody|caption|'
                   u'h[1-6]|section|article|header|footer|nav|main)\\b[^>]*>', u' ', s)
        s = re.sub(u'(?is)<[^>]+>', fill, s)
        for a, b in ENT_SG:
            s = s.replace(a, b)
    return s, dt


t = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\\n(.*?)\\n\\n## ', t, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
na_all = [re.sub(r' +', ' ', ''.join(c for c, _ in pairs(a))).strip() for a in atoms]

blocks, hit = [], set()
for lbl, raw, wl, wr in GROUPS:
    C = P = N = None
    DT = FILL = u''
    best = -1

    def faceof(fill):
        R0, dt = render(raw, fill)
        c = re.sub(r'\s+', ' ', R0)
        p = pairs(c)
        return c, p, re.sub(r' +', ' ', ''.join(ch for ch, _ in p)), dt

    for fill in (u'', u' '):
        c, p, n, dt = faceof(fill)
        got = sum(1 for na in na_all if n.find(na) >= 0)
        if got > best:
            C, P, N, DT, FILL, best = c, p, n, dt, fill, got
        if got == len(na_all):
            break

    WL, WR = int(wl), int(wr)

    def snap(a, b):
        x = max([k for k in (C.rfind('. ', max(0, a - WL), a), C.rfind('? ', max(0, a - WL), a),
                             C.rfind(u'。', max(0, a - WL), a), C.rfind(u'？', max(0, a - WL), a),
                             C.rfind(u'！', max(0, a - WL), a)) if k >= 0] or [-1])
        if x >= 0:
            a = x + (2 if C[x] in '.?' else 1)
        r = min([k for k in (C.find('. ', b, b + WR), C.find(u'。', b, b + WR), C.find(u'？', b, b + WR),
                             C.find(u'！', b, b + WR), C.find(u'”', b, b + WR)) if k >= 0] or [-1])
        return a, ((r + 1) if r >= 0 else min(b + 25, len(C)))

    spans = []
    for i, na in enumerate(na_all):
        j = N.find(na)
        if j < 0:
            continue
        hit.add(i)
        spans.append((P[j][1], P[min(j + len(na) - 1, len(P) - 1)][1] + 1))
    sp = sorted(snap(a, b) for a, b in spans)
    merged = []
    for a, b in sp:
        if merged and a <= merged[-1][1] + 30:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    blocks.append(u'### ⟦%s⟧ ⟸ %s%s\n\n' % (lbl, raw,
                  u'（渲染层: 注释删除, 分段/格标签各换成一个空格, 行内标签%s, 实体还原, 空白并列一个——本面按此档取到 %d/%d 枚锚）'
                  % (u'整体删除' if FILL == u'' else u'换成一个空格', best, len(na_all))
                  if DT else u'')
                  + u'\n\n'.join(C[a:b].strip() for a, b in merged))
    print('%s: anchors=%d/%d blocks=%d digest_chars=%d' % (lbl, len(spans), len(atoms), len(merged), len(blocks[-1])))

miss = [atoms[i][:70] for i in range(len(atoms)) if i not in hit]
if miss:
    print('MISS(no raw hit): %d %s' % (len(miss), miss))
    sys.exit(1)
dup = [i for i in range(len(atoms))
       if sum(1 for lbl, raw, wl, wr in GROUPS
              if any(re.sub(r' +', ' ', ''.join(c for c, _ in pairs(atoms[i]))).strip()
                     in re.sub(r' +', ' ', ''.join(c for c, _ in pairs(re.sub(r'\s+', ' ', render(raw, f)[0]))))
                     for f in (u'', u' '))) > 1]
print('atoms=%d union_hit=%d cross-labeled(may be substring of another model too)=%d' % (len(atoms), len(hit), len(dup)))

digest = u'\n\n'.join(blocks)
mark = u'## [[原始语料|ORIGINAL]]\n'
cut = t.index(u'## ⟪BabelTele')
io.open(ENTRY, 'w', encoding='utf-8').write(t[:t.index(mark) + len(mark)] + digest + u'\n\n' + t[cut:])
print('digest_total=%d' % len(digest))
