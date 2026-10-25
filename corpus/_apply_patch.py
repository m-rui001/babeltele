# -*- coding: utf-8 -*-
"""串行贴线器: 把各条代理生成的 `_tmpNN_audit_patch.py` 三段文本贴进共享的 `corpus/audit.py`。

存在的理由: audit.py 与 README 一样是全库唯一共享写点, 代理只准生成待贴文本, 由主线程逐枚应用;
并发贴会写出半文件, 而全库审计随时在读。用法:
    python -X utf8 corpus/_apply_patch.py 92 96 99        # 依次贴, 每枚贴完即 ast.parse 全文件自检
    python -X utf8 corpus/_apply_patch.py 92 --dry        # 只跑校验不落盘

四类现算校验, 不是“看起来对”:
① 补丁文件用 ast 解析取 SEG_A/B/C 常量, 不 import 不执行(补丁里的 scan 函数会读盘, 执行即副作用);
② 锚点行必须在贴之前数得恰好 1 枚(`rows, fails...` / env 字典尾行), 且 `DERIV['BNN']` 不在位——两条合起来才是“未贴过”,
   只查其一会在 SELF 自检红(重复定义)时才发现;
③ 每贴一枚立刻对**整个 audit.py** 跑 ast.parse, 并对该条断言 `def _bNN_scan` 恰 1 定义 ⇎ `= _bNN_scan()` 恰 1 调用;
④ SEG_B 必须是单行 `DERIV['BNN'] = {...}` 且 JSON 键数与 `_bNNflat.json` 相符, 防“贴了个空表”。
"""
import ast
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
DRY = u'--dry' in sys.argv
TAGS = [a for a in sys.argv[1:] if a.isdigit()]
assert TAGS, u'用法: python -X utf8 corpus/_apply_patch.py NN [NN ...] [--dry]'

ANCHOR_LOOP = u"rows, fails, proofs, soft_all = [], [], [], []"
ANCHOR_ENV = u"               B86V=B86V)"
P = u'corpus/audit.py'


def segs_of(n):
    """从补丁源码里取 SEG_A/SEG_B/SEG_C 三个字面量: 走 ast 而非 exec——exec 会把 scan 函数跑一遍。"""
    tree = ast.parse(io.open(n, encoding='utf-8').read(), n)
    got = {}
    for st in tree.body:
        if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
            nm = st.targets[0].id
            if nm in ('SEG_A', 'SEG_B', 'SEG_C') and isinstance(st.value, ast.Constant):
                assert isinstance(st.value.value, str), (n, nm)
                got[nm] = st.value.value
    assert set(got) == {'SEG_A', 'SEG_B', 'SEG_C'}, (n, sorted(got))
    return got


def body(txt, n):
    """剥掉 r''' 包裹留下的首尾换行, 并拒绝 tab——audit.py 全篇空格缩进。"""
    b = txt.strip(u'\n')
    assert b and u'\t' not in b, n
    return b


REPORT = []
for t in TAGS:
    tag = u'B%d' % int(t)
    cand = glob.glob(u'corpus/_tmp%s_audit_patch.py' % t)
    assert len(cand) == 1, (tag, cand)
    s = io.open(P, encoding='utf-8').read()
    assert ANCHOR_LOOP in s and s.count(ANCHOR_LOOP) == 1
    assert ANCHOR_ENV in s and s.count(ANCHOR_ENV) == 1, s.count(ANCHOR_ENV)
    assert u"DERIV['%s']" % tag not in s, u'%s 已在 audit.py 接线, 别贴第二遍(SELF 自检会红)' % tag
    G = segs_of(cand[0])
    A, B, C = body(G['SEG_A'], tag), body(G['SEG_B'], tag), body(G['SEG_C'], tag)
    m = re.match(u"DERIV\\['B(\\d+)'\\] = (\\{.*\\})$", B, re.S)
    assert m and int(m.group(1)) == int(t), (tag, B[:60])
    KEYS = json.loads(m.group(2))
    flat = json.load(io.open(u'corpus/_b%sflat.json' % t, encoding='utf-8'))
    assert KEYS == flat, (tag, sorted(set(KEYS) ^ set(flat)) or [k for k in KEYS if KEYS[k] != flat.get(k)])
    assert re.search(u'^SRC\\[\'B%d\'\\] = \\[' % int(t), A), (tag, A[:60])
    assert (u'%sV=%sV,' % (tag, tag)) in C, (tag, C)
    nsrc = len(re.findall(u'def _b%s_scan\\(' % t, A))
    ncall = len(re.findall(u'= _b%s_scan\\(\\)' % t, A))
    assert nsrc == 1 and ncall == 1, (tag, nsrc, ncall)
    assert u'ATOM.add' in A and u'DERIV[' in B and u'io.open' in A, (tag, A[:60], B[:40])

    L = s.split(u'\n')
    N0 = len(L)
    i_loop = [i for i, l in enumerate(L) if l == ANCHOR_LOOP]
    i_env = [i for i, l in enumerate(L) if l == ANCHOR_ENV]
    assert len(i_loop) == len(i_env) == 1, (i_loop, i_env)
    assert i_env[0] < i_loop[0], (i_env[0], i_loop[0])
    # env 字典在 audit.py 前半部, 主循环在其后: 先插下标大的 loop 段, 再插 env, 先前算的下标才不失效
    L[i_loop[0]:i_loop[0]] = (A + u'\n' + B).strip(u'\n').split(u'\n')
    L[i_env[0]:i_env[0]] = C.strip(u'\n').split(u'\n')
    NEW = u'\n'.join(L)
    ast.parse(NEW, P)
    assert NEW.count(u"DERIV['%s']" % tag) == 1 and NEW.count(ANCHOR_ENV) == 1
    assert NEW.count(u'def _b%s_scan(' % t) == NEW.count(u'= _b%s_scan()' % t) == 1
    added = len(NEW.split(u'\n')) - N0
    assert added == len(A.split(u'\n')) + len(B.split(u'\n')) + len(C.split(u'\n')), (added, A.count(u'\n'))
    REPORT.append((tag, len(KEYS), added, len(s), len(NEW)))
    if DRY:
        print(u'[dry] %s 可贴: DERIV %d 键, 新增 %d 行 (audit.py %d → %d 字符)' % (tag, len(KEYS), added, len(s), len(NEW)))
    else:
        io.open(P + '.tmpapply', 'w', encoding='utf-8', newline=u'\n').write(NEW)
        os.replace(P + '.tmpapply', P)
        print(u'贴线完成 %s: DERIV %d 键 ⇎ 新增 %d 行 ⇎ audit.py %d → %d 字符' % (tag, len(KEYS), added, len(s), len(NEW)))

if DRY:
    print(u'[dry] %d 枚全部过校验, audit.py 未动' % len(TAGS))
json.dump([{u'tag': r[0], u'deriv_keys': r[1], u'added_lines': r[2], u'before_chars': r[3],
            u'after_chars': r[4], u'dry': DRY} for r in REPORT],
          io.open(u'corpus/_tmpapply%s.json' % u'_'.join(TAGS), u'w', encoding=u'utf-8'),
          ensure_ascii=False, indent=1)
