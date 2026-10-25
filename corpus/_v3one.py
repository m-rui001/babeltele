# -*- coding: utf-8 -*-
# 单条 v3 计量: 锚内/锚外 拉丁字母与汉字, 编码/摘要/raw 三方比值
import io
import re
import sys
import os

tag, entry = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


t = io.open(entry, encoding=u'utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', t, re.S).group(1)
orig = re.search(u'\[\[原始语料\|ORIGINAL\]\]\n(.*?)\n\n## ⟪BabelTele', t, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
in_li = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
in_han = sum(len(re.findall(u'[一-鿿]', a)) for a in atoms)
out = re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)
out_li = len(re.findall(u'[A-Za-z]', out))
out_han = len(re.findall(u'[一-鿿]', out))
raw_chars = 0
raw_bytes = 0
for f in sys.argv[3:]:
    s = io.open(f, encoding=u'utf-8').read()
    raw_chars += len(s)
    raw_bytes += os.path.getsize(f)
print(u'anchors=%d 锚内字母=%d 锚内汉字=%d 锚外字母=%d 锚外汉字=%d' % (len(atoms), in_li, in_han, out_li, out_han))
print(u'enc=%d digest=%d raw_chars=%d raw_bytes=%d' % (len(enc), len(orig), raw_chars, raw_bytes))
print(u'保留率=%.1f%%  vs raw字节=%.3f%%  vs raw字符=%.1f%%' % (100.0 * len(enc) / len(orig), 100.0 * len(enc) / raw_bytes, 100.0 * len(enc) / raw_chars))
