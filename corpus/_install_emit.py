# -*- coding: utf-8 -*-
# 把 API 收回的发射段整稿装进 corpus/_mkNNemit.py。
# 用法: python -X utf8 corpus/_install_emit.py B95 0 [--final]
# 不加 --final 时条目 md 改落 corpus/_emitbox/(试跑箱), 不污染 corpus/babeltele/。
import io
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TAG, K = sys.argv[1], sys.argv[2]
FIN = u'--final' in sys.argv
NN = TAG[1:]
SRCMD = u'corpus/_api9x_emit_out/%s_em%s.md' % (TAG, K)
s = io.open(SRCMD, encoding='utf-8').read()
m = re.search(u'```python\n(.*?)\n```', s, re.S)
assert m, u'没有 python 代码块: ' + SRCMD
blk = m.group(1).replace(u'BNN', TAG).replace(u'_bNNcontract', u'_b%scontract' % NN)
assert u'BNN' not in blk and u'NNco' not in blk
if not FIN:
    blk = blk.replace(u'corpus/babeltele', u'corpus/_emitbox')
os.makedirs(u'corpus/_emitbox', exist_ok=True)
ast = compile(blk, u'<emit%s_%s>' % (TAG, K), 'exec')
io.open(u'corpus/_mk%semit.py' % NN, 'w', encoding='utf-8', newline=u'\n').write(blk + u'\n')
print(u'%s em%s 已装入 corpus/_mk%semit.py (%d 行, %s)'
      % (TAG, K, NN, blk.count(u'\n') + 1, u'正式' if FIN else u'试跑箱'))
