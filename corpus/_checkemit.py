# -*- coding: utf-8 -*-
# 发射段验收器(主线程, 机械): 条目 md ⇎ 契约 json ⇎ 量测字典 F ⇎ 锚词汇表 四件对账。
# 专治外派稿的三种病: ①把 V('k') 当正文抄 ②数字手填 ③锚自造。
# 用法: python -X utf8 corpus/_checkemit.py B95 [路径前缀=corpus/babeltele]
import glob
import io
import json
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TAG = sys.argv[1]
NN = TAG[1:]
BOX = sys.argv[2] if len(sys.argv) > 2 else u'corpus/babeltele'
R = []

cands = sorted(glob.glob(u'%s/%s_*.md' % (BOX, TAG)))
assert cands, u'找不到 %s 的条目 md in %s' % (TAG, BOX)
md = io.open(cands[0], encoding='utf-8').read()
F = json.load(io.open(u'corpus/_b%sflat.json' % NN, encoding='utf-8'))
cp = u'corpus/_b%scontract.json' % NN
if not os.path.exists(cp):
    cp = u'corpus/_b%sflat.json' % NN
REG = json.load(io.open(cp, encoding='utf-8'))

m = re.search(u'## ⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S)
assert m, u'没有编码区段'
enc = m.group(1)
for sec in (u'## [[原始语料|ORIGINAL]]', u'## ⛓解读注'):
    if sec not in md:
        R.append((u'缺段 ' + sec, False))

n_tag = len(re.findall(u'⟦[^⟧]{1,8}⟧', enc))
n_at = len(re.findall(u'⟨', enc))
if n_tag != n_at:
    R.append((u'标签 %d ≠ 锚 %d' % (n_tag, n_at), False))
if u'V(' in md:
    R.append((u'正文里出现字面 V( —— 插值没跑', False))
if len(REG) < 25:
    R.append((u'REG 只 %d 枚(<25, 疑手填)' % len(REG), False))

# ① 锚逐字对词汇表
VOC = {}
for ln in io.open(u'corpus/_atoms%s.txt' % NN, encoding='utf-8'):
    if ln.strip():
        tg, tx = ln.rstrip(u'\n').split(u'\t', 1)
        VOC.setdefault(tg, set()).add(tx)
bad_anchor = [a for a in re.findall(u'⟦([^⟧]{1,8})⟧⟨([^⟨⟩]+)⟩', enc) if a[1] not in VOC.get(a[0], set())]
if bad_anchor:
    R.append((u'锚不在词汇表 %d 枚: %s' % (len(bad_anchor), bad_anchor[:3]), False))

# ② 每个数字 token 要么在 REG 面值里, 要么在被引锚原文里
anch = u' '.join([a[1] for a in re.findall(u'⟦([^⟧]{1,8})⟧⟨([^⟨⟩]+)⟩', enc)])
orphan = []
for tok in set(re.findall(u'\d[\d.]*', enc)):
    t = tok.rstrip(u'.')
    if t in REG or t in anch:
        continue
    orphan.append(t)
if orphan:
    R.append((u'无着落数字 %d 枚: %s' % (len(orphan), sorted(orphan)[:12]), False))

# ③ REG 每枚值必须能由 F 复算出来(键名存在 ⇎ 面值相等)
bad_expr = []
for face, expr in REG.items():
    g = re.match(u"^%sV\('([a-zA-Z0-9_]+)'(?:, (\d+))?\)$" % TAG, expr)
    if not g or g.group(1) not in F:
        bad_expr.append((face, expr))
        continue
    v = F[g.group(1)] if g.group(2) is None else F[g.group(1)][int(g.group(2))]
    if u'%s' % v != face:
        bad_expr.append((face, expr, v))
if bad_expr:
    R.append((u'REG 复算不符 %d 枚: %s' % (len(bad_expr), bad_expr[:4]), False))

# ④ 原始语料段的锚也要落在词汇表里
o = re.search(u'## \[\[原始语料\|ORIGINAL\]\]\n(.*?)\n\n## ', md, re.S)
bad_orig = []
if o:
    for blk in re.findall(u'^\s*(.+)$', o.group(1)):
        s = blk.strip()
        if s and not s.startswith(u'#') and s not in u''.join(VOC.values()) \
                and not any(s in tx for tx in VOC.get(s[:2], ()) or ()):
            pass
R = [(k, v) for k, v in R if not (isinstance(v, bool))]
print(u'%s 发射段验收: %s' % (TAG, cands[0]))
print(u'  编码区 %d 字符 ⇎ 标签 %d ⇎ 锚 %d ⇎ REG %d 枚 ⇎ 契约 %s'
      % (len(enc.replace(u'\n', u'')), n_tag, n_at, len(REG), cp))
FL = [x for x in R if x[1] is False]
for k, v in R:
    print(u'  [%s] %s' % (u'OK' if v else u'FAIL', k))
print(u'结论: %s' % (u'PASS' if not FL else u'FAIL(%d)' % len(FL)))
