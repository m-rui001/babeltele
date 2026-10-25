# -*- coding: utf-8 -*-
# 幂等生成 B98 接线补丁(照 _wire99.py 的横幅 splice 机制): _b98_scan 的函数体不重写,
# 直接从 corpus/_mkB98.py 的 # --- SCAN BEGIN/END --- 之间摘出同一段量测+对账代码(对账段
# PICK 本就嵌在 SCAN 之内, 所以只摘一段), 前置它依赖的模块级常量块(NL ⇎ LBL ⇎ NSRC ⇎ PATH ⇎
# F ⇎ DER ⇎ LITK), 其中 PATH 换成 SRC['B98']; 诊断 print 机械换成 _sil(空函数),
# sys.stdout.flush() 换成 pass, 行结构一行不动, 所以进门后的现量与建条目遍用的算法逐字符同一条。
# 本脚本绝不写 corpus/audit.py——只把三段文本 splice 进 corpus/_tmpNN_audit_patch.py 的横幅之间;
# 贴之前先在内存里 exec 一遍函数体, 与 corpus/_b98flat.json 逐键比, 不同就不出补丁;
# 再把契约 81 键逐枚在门内复算(契约里 34 枚是复合式而非直取值, 所以这里不能像 B99 那样
# 只验 "B98V('k', i)" 的键形, 必须真 eval)。
import ast
import io
import json
import os
import re
import sys

TAG = u'B98'
NN = TAG[1:].lower()
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = u'corpus/audit.py'
SRCMK = u'corpus/_mk%s.py' % TAG
FLAT = u'corpus/_b%sflat.json' % NN
CONTRACT = u'corpus/_b%scontract.json' % NN
OUT = u'corpus/_tmpNN_audit_patch.py'

s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['%s']" % TAG in s:
    print(u'%s 已在 audit.py 接线, 跳过(补丁无须再贴)' % TAG)
    raise SystemExit

mk = io.open(SRCMK, encoding='utf-8').read()
ml = mk.split(u'\n')


def span(a, b):
    i0 = [i for i, l in enumerate(ml) if l.startswith(a)][0]
    i1 = [i for i, l in enumerate(ml) if l.startswith(b)][0]
    return i0 + 1, i1


S0, S1 = span(u'# --- SCAN BEGIN ---', u'# --- SCAN END ---')
K0, K1 = span(u'# --- PICK BEGIN ---', u'# --- PICK END ---')
assert S0 < K0 < K1 <= S1, (S0, K0, K1, S1)
tree = ast.parse(mk)

# 常量块: 只取 SCAN 之前的模块级简单赋值, PATH 那一枚换成 SRC['B98']
CONST = []
for nd in tree.body:
    if not isinstance(nd, ast.Assign) or nd.lineno >= S0:
        continue
    tgt = nd.targets[0]
    if not (isinstance(tgt, ast.Name) and tgt.id in
            (u'NL', u'LBL', u'NSRC', u'PATH', u'F', u'DER', u'LITK')):
        continue
    if tgt.id == u'PATH':
        CONST.append(u"PATH = SRC[u'%s']" % TAG)
        continue
    CONST.extend(ml[nd.lineno - 1:nd.end_lineno])
assert len(CONST) >= 7, CONST
BODY = CONST + ml[S0:S1]
BODY.append(u'return F')

# 诊断语句换空操作(保留行结构: print 的续行照旧缩进, 只是首词改名)
IMPORTS = []
for i, l in enumerate(BODY):
    t = l.lstrip()
    if t.startswith(u'sys.stdout.flush()'):
        BODY[i] = l.replace(u'sys.stdout.flush()', u'pass')
    if t.startswith((u'import ', u'from ')):
        IMPORTS.append(t)
PRINTS = [i for i, l in enumerate(BODY) if l.lstrip().startswith(u'print(')]
BODY = [l.replace(u'print(', u'_sil(', 1) if l.lstrip().startswith(u'print(') else l for l in BODY]
WR = [l for l in BODY if (u"'w'" in l or u'"w"' in l or u"'a'" in l or u'babeltele' in l)]
assert not WR, u'摘出的段里有落盘动作: %s' % WR[:2]
assert u"SRC[u'%s']" % TAG in u'\n'.join(BODY), u"源没换成 SRC['%s']" % TAG

FN = [u'def _b%s_scan():' % NN,
      u'    """B98 现量(摘自 corpus/_mkB98.py 的 SCAN 段, 与建条目遍同一套代码): Retry-After 该写',
      u'    多久、谁能省掉它——RFC 2616 ⇎ 6585 ⇎ 7231 ⇎ 9110 ⇎ curl 手册五份一手文书的面尺三轨行账、',
      u'    定义窗块定界、四档可读性(逐行 ⇎ 折平 ⇎ 摘壳 ⇎ 去标记)、单位词档、独占针与 7231/9110 窗内',
      u'    句集容斥 ⇎ 与采集遍 _pick98 的逐键对账, 一律在此现算。"""',
      u'    import json',
      u'    from collections import Counter',
      u'    _sil = lambda *a, **k: None']
BLOCK = u'\n'.join(FN + [u'    ' + l for l in BODY])
ast.parse(BLOCK + u'\n')

# 门内现算必须与建条目遍逐键同值——先在内存 exec 一遍再出补丁
PATHL = None
for nd in tree.body:
    if isinstance(nd, ast.Assign) and isinstance(nd.targets[0], ast.Name) \
            and nd.targets[0].id == u'PATH':
        PATHL = ast.literal_eval(nd.value)
assert isinstance(PATHL, list) and len(PATHL) == 5, PATHL
NS = {u'SRC': {TAG: PATHL}, u'io': io, u're': re, u'json': json, u'os': os, u'sys': sys}
exec(compile(BLOCK, u'<b98scan>', u'exec'), NS)
GOT = NS[u'_b%s_scan' % NN]()
EXP = json.load(io.open(FLAT, encoding=u'utf-8'))
DIF = [k for k in EXP if json.dumps(GOT.get(k), sort_keys=True) != json.dumps(EXP[k], sort_keys=True)]
assert not DIF, u'门内现量与建条目遍不同值: %s' % DIF[:8]
print(u'门内现算自校: %d 键逐键同值' % len(EXP))

REG = json.load(io.open(CONTRACT, encoding=u'utf-8'))
# 键形: 十进制数(可负 ⇎ 可带小数点——差值档), 值形不做键形约束(B98 契约 34/81 枚是复合式),
# 改为逐枚真 eval: 表达式只准用 B98V 取 F 值 ⇎ 聚合内建 ⇎ range, 门内现值必须等于登记值。
assert REG and all(re.match(u'^-?[0-9][0-9.]*$', k) for k in REG), sorted(REG)[:5]
_V = lambda kk, ii=None: (GOT[kk] if ii is None else GOT[kk][ii])
BAD = []
for k, v in REG.items():
    try:
        got = eval(v.replace(u'%sV' % TAG, u'_V'), {u'_V': _V, u'sum': sum, u'len': len,
                                                   u'max': max, u'min': min, u'range': range,
                                                   u'sorted': sorted, u'abs': abs, u'round': round})
    except Exception as e:
        BAD.append((k, v[:60], repr(e)[:60]))
        continue
    if u'%s' % got != k:
        BAD.append((k, v[:60], u'现值 %r' % (got,)))
assert not BAD, u'DERIV 现值不符: %s' % BAD[:6]
print(u'DERIV %d 枚键全可在门内复算(复合式 %d 枚), 现值与登记值逐枚同'
      % (len(REG), len([v for v in REG.values() if not v.startswith(u"%sV('" % TAG)])))

FS = NS[u'SRC'][TAG]
assert s.count(u'rows, fails, proofs, soft_all = [], [], [], []') == 1
assert s.count(u'               B86V=B86V)') == 1

SEG_B = [u"SRC['%s'] = [%s]" % (TAG, u', '.join([repr(f) for f in FS])),
         u"ATOM.add('%s')" % TAG,
         u"_B%s = _b%s_scan()" % (NN, NN),
         u"%sV = lambda k, i=None: (_B%s[k] if i is None else _B%s[k][i])" % (TAG, NN, NN),
         u"DERIV['%s'] = %s" % (TAG, json.dumps(REG, ensure_ascii=False))]

block = u'\n'.join([
    u'# ====BEGIN %s==== (DERIV 键表 corpus/_b%scontract.json=%d 键 ⇎ 现量 %d 行 ⇎ 摘内 import %d 行)'
    % (TAG, NN, len(REG), len(BODY), len(IMPORTS)),
    u"SEG_A_%s = r'''" % TAG,
    BLOCK,
    u"'''",
    u"",
    u"SEG_B_%s = r'''" % TAG,
    u'\n'.join(SEG_B),
    u"'''",
    u"",
    u"SEG_C_%s = r'''" % TAG,
    u"               %sV=%sV," % (TAG, TAG),
    u"'''",
    u'# ====END %s====' % TAG,
    u'',
])
full = io.open(OUT, encoding=u'utf-8').read() if os.path.exists(OUT) else u''
pat = re.compile(u'# ====BEGIN %s====.*?# ====END %s====\n' % (TAG, TAG), re.S)
full = pat.sub(block, full) if pat.search(full) else full.rstrip(u'\n') + u'\n\n' + block
io.open(OUT, 'w', encoding='utf-8', newline=u'\n').write(full)
print(u'%s 补丁段已写入 %s: 函数体 %d 行(常量 %d ⇎ 摘文 %d ⇎ print 静默 %d 处), SRC %d 份, DERIV %d 键'
      % (TAG, OUT, BLOCK.count(u'\n') + 1, len(CONST), S1 - S0, len(PRINTS), len(FS), len(REG)))
