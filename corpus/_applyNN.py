# -*- coding: utf-8 -*-
# 主线程串行贴入器(通用): 把 corpus/_tmpNN_audit_patch.py 里某一枚 ====BEGIN/END Bxx==== 横幅
# 之下的三段文本贴进 corpus/audit.py 的三处锚行之前。锚行必须恰现一次, 幂等哨兵 = DERIV['Bxx']。
# 用法: python -X utf8 corpus/_applyNN.py B96      (先 --check 只看不写)
import io, re, sys

TAG = sys.argv[1]
CHK = u'--check' in sys.argv
P, PT = u'corpus/audit.py', u'corpus/_tmpNN_audit_patch.py'
s = io.open(P, encoding='utf-8').read()
pt = io.open(PT, encoding='utf-8').read()
if "DERIV['%s']" % TAG in s:
    print(u'%s 已在 audit.py, 贴入器不动文件' % TAG)
    raise SystemExit
BAN = re.search(u'# ====BEGIN %s====.*?# ====END %s====' % (TAG, TAG), pt, re.S)
assert BAN, u'补丁文件里没有 %s 横幅' % TAG
SEG = {}
for k in (u'A', u'B', u'C'):
    m = re.search(u"SEG_%s_%s = r'''(.*?)'''" % (k, TAG), BAN.group(0), re.S)
    assert m, u'缺 SEG_%s_%s' % (k, TAG)
    SEG[k] = m.group(1).strip(u'\n') + u'\n'

A1 = u'rows, fails, proofs, soft_all = [], [], [], []'
A2 = u'               B86V=B86V)'
assert s.count(A1) == 1 and s.count(A2) == 1, (s.count(A1), s.count(A2))
for k in (u'A', u'B'):
    assert s.count(SEG[k]) == 0, u'SEG_%s 已存在但哨兵缺失(半贴状态)' % k
out = s.replace(A1, SEG[u'A'] + SEG[u'B'] + A1)
out = out.replace(A2, SEG[u'C'] + A2)
import ast
ast.parse(out)
assert out.count(u'def _b%s_scan(' % TAG[1:].lower()) == 1
assert out.count(u'= _b%s_scan()' % TAG[1:].lower()) == 1
if CHK:
    print(u'--check 通过: 拟新增 %d 行' % (out.count(u'\n') - s.count(u'\n')))
else:
    io.open(P, 'w', encoding='utf-8', newline=u'\n').write(out)
    print(u'%s 已贴入 %s(+%d 行)' % (TAG, P, out.count(u'\n') - s.count(u'\n')))
