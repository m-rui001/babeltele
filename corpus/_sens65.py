# -*- coding: utf-8 -*-
"""B65 反向对照: 每个 DERIV 复算点与每条面内恒等式都改一处读数看它会不会 nonzero。
量三件事: ①纯复述点(算式就是 B65V('x') 本身, 没有重算) ②自差式恒等式(两枚操作数是同一个键)
③敏感性: 把某键读数 +1 后有多少条判词/恒等式会倒——一次都不倒的键是装饰。"""
import ast, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
F = json.load(io.open(u'corpus/_b65flat.json', encoding='utf-8'))
DER = json.load(io.open(u'corpus/_deriv65.json', encoding='utf-8'))
SRC = io.open(u'corpus/_mkB65.py', encoding='utf-8').read()
ZID = None
for nd in ast.walk(ast.parse(SRC)):
    if isinstance(nd, ast.Assign) and any(isinstance(t, ast.Name) and t.id == u'ZID' for t in nd.targets):
        try:
            ZID = ast.literal_eval(nd.value)
        except Exception:
            pass
assert ZID
VAL = dict((k, v) for k, v in F.items() if isinstance(v, (int, float)) and not isinstance(v, bool))
LISTK = dict((k, v) for k, v in F.items() if isinstance(v, list))
ENV = {}
def gv(k, i=None):
    x = F[k]
    return x if i is None else x[i]
def run(e, over=None):
    over = over or {}
    env = {u'B65V': (lambda k, i=None: (over.get((k, i), gv(k, i)))),
           u'max': max, u'min': min, u'sum': sum, u'abs': abs, u'len': len,
           u'sorted': sorted, u'set': set, u'int': int, u'round': round}
    return eval(e, env)
def refs(e):
    out = []
    for m in re.finditer(r"B65V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)", e):
        out.append((m.group(1), int(m.group(2)) if m.group(2) else None))
    return out
PURE = [(k, e) for k, e in DER.items() if re.match(r"^B65V\('[a-z0-9_]+(?:, \d+)?'\)$", e.strip())]
SELF = [e for e, _ in ZID if len(set(refs(e))) == 1 and u'-' in e]
print(u'DERIV %d 条 ⇎ 恒等式 %d 条' % (len(DER), len(ZID)))
print(u'①纯复述点 %d: %s' % (len(PURE), PURE[:6]))
print(u'②自差恒等式 %d: %s' % (len(SELF), SELF[:4]))
INV = {}
ALL = [(u'D:' + k, e) for k, e in DER.items()] + [(u'Z%d' % n, e) for n, (e, _) in enumerate(ZID)]
def _ok(e):
    try:
        return run(e)
    except Exception:
        return None
for tag, e in ALL:
    for r in refs(e):
        INV.setdefault(r, []).append(tag)
BADT = [t for t, e in ALL if _ok(e) is None]
print(u'①b 算式在此环境跑不通的判定点 %d/%d: %s' % (len(BADT), len(ALL), BADT[:8]))
SORTK = lambda x: (x[0], x[1] is not None, x[1] or 0)
never, errsk = [], []
for rk in sorted(INV, key=SORTK):
    if rk[0] not in VAL and rk[0] not in LISTK:
        never.append((rk, u'缺键')); continue
    v0 = gv(rk[0], rk[1])
    if isinstance(v0, bool) or not isinstance(v0, (int, float)):
        errsk.append((rk, u'非数')); continue
    flipped = errs = 0
    for tag, e in ALL:
        if rk not in refs(e):
            continue
        try:
            base = run(e)
            now = run(e, {rk: v0 + 1})
        except Exception:
            errs += 1
            continue
        if (now != base):
            flipped += 1
    if errs:
        errsk.append((rk, errs))
    elif flipped == 0:
        never.append((rk, len(INV[rk])))
print(u'③a 算式跑不通(无从判定)的键 %d: %s' % (len(errsk), errsk[:8]))
print(u'③b 可判定但+1 后从不改变任何判定的键 %d: %s' % (len(never), never[:12]))
deg = sorted(INV.items(), key=lambda kv: -len(kv[1]))[:8]
print(u'④支持判词最多的键: %s' % deg)
print(u'⑤只被 1 条判定引用的键 %d 个' % len([1 for k, v in INV.items() if len(v) == 1]))
