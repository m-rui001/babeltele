# -*- coding: utf-8 -*-
# B31 去冗余(只在 ⟪BabelTele⟫ 段内操作, 摘要段随后由 _mkdigest3 重生成)
import io
import re

E = u'corpus/babeltele/B31_edata_substantive_review.md'
A = [l.rstrip(u'\n') for l in io.open(u'corpus/raw/probe/b31_atoms.txt', encoding=u'utf-8') if l.strip()]
B = [l.rstrip(u'\n') for l in io.open(u'corpus/raw/probe/b31_atoms2.txt', encoding=u'utf-8') if l.strip()]
full = io.open(E, encoding=u'utf-8').read()
m = re.search(u'(## ⟪BabelTele⟫\n)(.*?)(\n\n## )', full, re.S)
pre, enc, post = m.group(1), m.group(2), m.group(3)


def cut(s, expect=1):
    global enc
    assert enc.count(s) == expect, (s, enc.count(s))
    enc = enc.replace(s, u'')


def swap(a, b):
    global enc
    assert enc.count(a) == 1, a
    enc = enc.replace(a, b)


for s in [u' ‖ ⟦T⟧⟨%s⟩' % A[1],
          u' ‖ ⟦T⟧⟨%s⟩' % A[70],
          u' ‖ ⟦T⟧⟨%s⟩' % A[68],
          u' ‖ ⟦P⟧⟨%s⟩' % B[11],
          u' + ⟦P⟧⟨%s⟩' % B[13]]:
    cut(s)

swap(u' ‖ 各配专属失败态: 来源⟦T⟧⟨%s⟩' % A[7], u' ‖ 各配专属失败态: 来源[失基础]')
swap(u' ‖ 背景 ⟦P⟧⟨%s⟩' % A[81], u' ‖ 背景 ⟦P⟧⟨%s⟩' % A[81][16:])
swap(u' ⇎ ⟦T⟧⟨%s⟩ ⇒ 『三种处置' % A[60][24:], u' ⇎ [审慎使用留给承办] ⇒ 『三种处置')
swap(u' ⇎ ⟦T⟧⟨%s⟩ ⇒ 『两源分写' % A[60][24:], u' ⇎ [同疑点不得过关行] ⇒ 『两源分写')
swap(u'(原始聊天环境／原始账户流水)', u'')
swap(u'两源都未交代这个落差(漏报／程序门槛／口径), 编者标为未答问题', u'落差成因(漏报／程序门槛／口径)两源未答')
swap(u'与理论篇外围信息更有证明价值同路线', u'即完整关与解释关在元数据层的重跑')

full = full[:m.start(2)] + enc + full[m.end(2):]
io.open(E, u'w', encoding=u'utf-8').write(full)
ats = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
print(u'enc=%d anchors=%d 》=%d' % (len(enc), len(ats), enc.count(u'》')))
io.open(u'corpus/raw/probe/b31_entry_atoms.txt', u'w', encoding=u'utf-8').write(u'\n'.join(ats) + u'\n')
