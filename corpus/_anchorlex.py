# -*- coding: utf-8 -*-
# 锚词汇表生成器(主线程, 机械): 把采集遍的 NEEDLES 逐枚在源面上穿一遍,
# 记下每枚针落在哪几份源(最宽档: 网页先剥壳两档, 纯文本直接折平), 落成 corpus/_atomsNN.txt
# (格式同 _atoms92.txt: 标签<TAB>针文本)。外派写稿只准引用这份词汇表, 不许自造引文。
# 用法: python -X utf8 corpus/_anchorlex.py 95 98 99
import ast
import io
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SG = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'),
      (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'),
      (u'&#215;', u'x'), (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"),
      (u'&mdash;', u'-'), (u'&ndash;', u'-'), (u'&deg;', u'deg'), (u'&infin;', u'inf'),
      (u'\xa0', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
      (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->')]


def detag(t, fill):
    buf, i, n = [], 0, len(t)
    while i < n:
        if t[i] == u'<':
            j = t.find(u'>', i)
            if j >= 0:
                buf.append(fill)
                i = j + 1
                continue
        buf.append(t[i])
        i += 1
    s = u''.join(buf)
    for a, b in SG:
        s = s.replace(a, b)
    return s


def norm(s):
    s = re.sub(u"[’‘`´\"']", u'', s.lower())
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\.]', u' ', s)
    return u' '.join(s.split())


for NN in sys.argv[1:]:
    pick = io.open(u'corpus/_pick%s.py' % NN, encoding='utf-8').read()
    tree = ast.parse(pick)
    needles, srcs, lbl = None, None, None
    for nd in tree.body:
        if isinstance(nd, ast.Assign) and isinstance(nd.targets[0], ast.Name):
            nm = nd.targets[0].id
            if nm == u'NEEDLES' and isinstance(nd.value, ast.List):
                needles = [e.value for e in nd.value.elts if isinstance(e, ast.Constant)]
            elif nm in (u'SRC', u'FILES', u'PATH') and isinstance(nd.value, ast.List):
                got = [e.value for e in nd.value.elts
                       if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                if len(got) == len(nd.value.elts):
                    srcs = got
                else:   # D + u'x' 一类的拼接形: 取 D 前缀再拼
                    dpre = None
                    for nd2 in tree.body:
                        if (isinstance(nd2, ast.Assign) and isinstance(nd2.targets[0], ast.Name)
                                and nd2.targets[0].id == u'D' and isinstance(nd2.value, ast.Constant)):
                            dpre = nd2.value.value
                    got = []
                    for el in nd.value.elts:
                        assert dpre is not None and isinstance(el, ast.BinOp) \
                            and isinstance(el.right, ast.Constant), ast.dump(el)
                        got.append(dpre + el.right.value)
                    srcs = got
            elif nm == u'LBL':
                lbl = [e.value for e in nd.value.elts if isinstance(e, ast.Constant)]
    assert needles and srcs and lbl, (NN, bool(needles), bool(srcs), bool(lbl))
    TAGS = [chr(ord('A') + i) for i in range(len(srcs))]
    FACES = []
    for f in srcs:
        t = io.open(f, encoding='utf-8', errors='replace').read()
        if f.lower().endswith((u'.html', u'.htm')):
            FACES.append(norm(detag(t, u'')) + u'\u0001' + norm(detag(t, u' ')))
        else:
            FACES.append(norm(t))
    rows = []
    miss = []
    for nd in needles:
        nn = norm(nd)
        if len(nn) < 8:
            miss.append((nd, u'短于 8 字符'))
            continue
        hit = False
        for i, fc in enumerate(FACES):
            if nn in fc:
                rows.append((TAGS[i], lbl[i], nd))
                hit = True
        if not hit:
            miss.append((nd, u'面上穿不到'))
    seen = set()
    out = []
    for tg, lb, nd in rows:
        if (tg, nd) in seen:
            continue
        seen.add((tg, nd))
        out.append(u'%s\t%s\n' % (tg, nd))
    io.open(u'corpus/_atoms%s.txt' % NN, 'w', encoding='utf-8', newline=u'\n').write(u''.join(out))
    print(u'_atoms%s.txt: 针 %d 枚 → 带归属锚 %d 条(源 %d 份 %s; 未穿到 %d 枚)'
          % (NN, len(needles), len(out), len(srcs), '/'.join(lbl), len(needles) - len(set(nd for _, _, nd in rows))))
    for nd, why in miss:
        print(u'  未穿 %s: %r' % (why, nd[:64]))
