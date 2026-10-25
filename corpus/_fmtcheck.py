# -*- coding: utf-8 -*-
# 发射段静态门: 逐段核对模板占位符数与实参数数(实跑若少给参数不会报错, 只会静默漏字)。
# 用法: python -X utf8 corpus/_fmtcheck.py corpus/_mkNNemit.py
import ast
import io
import re
import sys


def collect(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return collect(n.left) + collect(n.right)
    return u''


bad = 0
tree = ast.parse(io.open(sys.argv[1], encoding='utf-8').read())
for node in ast.walk(tree):
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == u'append'):
        continue
    a = node.args[0]
    if not (isinstance(a, ast.BinOp) and isinstance(a.op, ast.Mod)):
        continue
    tpl = collect(a.left)
    nspec = len(re.findall(r'(?<!%)%[ds]', tpl)) + len(re.findall(r'%%', tpl))
    nargs = len(a.right.elts) if isinstance(a.right, ast.Tuple) else 1
    lit = len(re.findall(r'\{[0-9]*\}', tpl))
    if nspec != nargs or lit:
        bad += 1
        print(u'第 %d 行: 占位符 %d ⇎ 实参 %d ⇎ 花括号 %d  *** 不符' % (node.lineno, nspec, nargs, lit))
print(u'静态核对 %d 段: %s' % (len([1 for n in ast.walk(tree) if isinstance(n, ast.BinOp)
                                 and isinstance(n.op, ast.Mod)]), u'全平' if not bad else u'%d 段不符' % bad))
