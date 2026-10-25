# -*- coding: utf-8 -*-
# 幂等生成 B96 接线补丁(照 _wire91.py 的横幅 splice 机制, 但 _b96_scan 的函数体不重写:
# 直接从 corpus/_mkB96.py 的 # --- SCAN BEGIN/END --- 之间摘出同一套量测代码, 缩进挂进函数,
# 前置摘入它依赖的五组常量(RAWS ⇎ ATOMS ⇎ CHAIN ⇎ NEG ⇎ REG_KW)。摘的是原文, 不是复述,
# 所以进门后的现量与建条目遍用的算法逐字符同一条。
# 本脚本绝不写 corpus/audit.py——只把三段文本 splice 进共享补丁
# corpus/_tmpNN_audit_patch.py 的 ====BEGIN/END B96==== 横幅之间。
# audit.py 已含 DERIV['B96'] 即视为已接线, 跳过。
import io, json, os, re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
SRCMK = 'corpus/_mkB96.py'
OUT = 'corpus/_tmpNN_audit_patch.py'
FLAT = 'corpus/_b96flat.json'
TAG = 'B96'
RAWF = u'corpus/raw/late96/fcc_2026-21821.txt'

s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['%s']" % TAG in s:
    print('%s 已在 audit.py 接线, 跳过(补丁无须再贴)' % TAG)
    raise SystemExit

mk = io.open(SRCMK, encoding='utf-8').read().split(u'\n')
i0 = [i for i, l in enumerate(mk) if l.startswith(u'# --- SCAN BEGIN ---')][0] + 1
i1 = [i for i, l in enumerate(mk) if l.startswith(u'# --- SCAN END ---')][0]
SCAN = mk[i0:i1]
assert not [l for l in SCAN if l.lstrip().startswith(u'print(')], u'SCAN 段里有 print'


def const(name):
    j = [i for i, l in enumerate(mk) if l.startswith(name + u' =')][0]
    k = j + 1
    while not mk[k].strip().endswith(u']'):
        k += 1
    return mk[j:k + 1]


# SCAN 段(28..294)里已经自带 ATOMS ⇎ CHAIN ⇎ NEG ⇎ REG_KW 四组常量, 唯独 RAWS 在它上面;
# 进门后源路径只认 audit 的 SRC['B96'], 所以只补这一行别名, 不往函数体里搬多行常量。
PRE = []
for l in PRE + SCAN:
    assert not l.lstrip().startswith((u'import ', u'from ')), l

BODY = [u'def _b96_scan():',
        u'    """B96 现量(摘自 corpus/_mkB96.py 的 SCAN 段, 与建条目遍同一套代码): FCC 终规单文本压缩。"""',
        u"    raw0 = io.open(SRC['B96'][0], encoding='utf-8', errors='replace').read()",
        u"    RAWS = [SRC['B96'][0]]"]
# 采集遍自带一个读文件的小助手 rd; 进门后源由 raw0 一次读定, 助手连同它的 open 一并摘掉。
DROP = [i for i, l in enumerate(SCAN) if l.startswith(u'def rd(p):')]
assert len(DROP) == 1 and SCAN[DROP[0] + 1].strip().startswith(u'return io.open'), SCAN[:3]
SCAN = SCAN[:DROP[0]] + SCAN[DROP[0] + 2:]
BODY += [u'    ' + l for l in SCAN]
BODY.append(u'    return F')
BLOCK = u'\n'.join(BODY).replace(u'RAWS[0]', u'RAWS[0]').replace(u'__RAWF__', RAWF)
# 采集遍读的是 MEASA 落盘件; 进门后不写盘, 只把 raw 变量名对齐 SRC['B96']
BLOCK = re.sub(r'\n\s*raw = rd\(RAWS\[0\]\)\n', u"\n    raw = raw0\n", BLOCK)
assert u'raw = raw0' in BLOCK, u'源读句没换成 SRC[\'B96\']'
assert u'open(' not in re.sub(r"errors='replace'", u'', BLOCK.replace(u"io.open(SRC['B96'][0]", u'')), \
    u'SCAN 段里还有落盘动作'

REG = json.load(io.open(FLAT, encoding='utf-8'))
assert REG and all(re.match(u'^[0-9][0-9.]*$', k) for k in REG), sorted(REG)[:5]
assert all(v.startswith(u"B96V('") for v in REG.values()), sorted(REG.values())[:3]

assert s.count('rows, fails, proofs, soft_all = [], [], [], []') == 1
assert s.count('               B86V=B86V)') == 1

block = u'\n'.join([
    u'# ====BEGIN %s==== (DERIV 键表 corpus/_b96flat.json=%d 键)' % (TAG, len(REG)),
    u"SEG_A_%s = r'''" % TAG,
    BLOCK,
    u"'''",
    u"",
    u"SEG_B_%s = r'''" % TAG,
    u"SRC['B96'] = ['" + RAWF + u"']",
    u"ATOM.add('B96')",
    u"_B96 = _b96_scan()",
    u"B96V = lambda k, i=None: (_B96[k][0] if i is None else _B96[k][i])",
    u"DERIV['B96'] = " + json.dumps(REG, ensure_ascii=False),
    u"'''",
    u"",
    u"SEG_C_%s = r'''" % TAG,
    u"               B96V=B96V,",
    u"'''",
    u'# ====END %s====' % TAG,
    u'',
])
ast_ok = u'\n'.join([BLOCK, u"B96V = None", u"DERIV = {}", u"SRC = {}", u"ATOM = set()"])
import ast
ast.parse(ast_ok)

if os.path.exists(OUT):
    full = io.open(OUT, encoding='utf-8').read()
else:
    full = u''
pat = re.compile(u'# ====BEGIN %s====.*?# ====END %s====\n' % (TAG, TAG), re.S)
if pat.search(full):
    full = pat.sub(block, full)
else:
    full = full.rstrip(u'\n') + u'\n\n' + block
io.open(OUT, 'w', encoding='utf-8', newline=u'\n').write(full)
print(u'B96 补丁段已写入 %s: SCAN %d 行 + 常量 %d 行, DERIV %d 键' % (OUT, len(SCAN), len(PRE), len(REG)))
