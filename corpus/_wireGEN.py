# -*- coding: utf-8 -*-
# 通用接线生成器(主线程, 只产文本不碰共享件): 从 corpus/_mkNN.py 的
#   # --- SCAN BEGIN/END --- 之间逐字符摘出第二套实现的量测函数, 挂进 audit.py 的
#   _bNN_scan(); 源路径/标签表/DERIV 键表分别取自 mk 的 SRC 表与 _bNNflat.json。
# 摘原文而不是复述, 所以进门后的现量与建条目遍用的算法逐字符同一条。
# 三段文本 splice 进 corpus/_tmpNN_audit_patch.py 的 ====BEGIN/END Bxx==== 横幅之间,
# 由 corpus/_applyNN.py 贴入 audit.py。
import ast, io, json, os, re, sys

TAG = sys.argv[1]
NN = TAG[1:].lower()
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = u'corpus/audit.py'
SRCMK = u'corpus/_mk%s.py' % TAG
FLAT = u'corpus/_b%sflat.json' % NN
OUT = u'corpus/_tmpNN_audit_patch.py'

s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['%s']" % TAG in s:
    print(u'%s 已在 audit.py 接线, 跳过(补丁无须再贴)' % TAG)
    raise SystemExit

mk = io.open(SRCMK, encoding='utf-8').read()
ml = mk.split(u'\n')
assert ml.count(u'# --- SCAN BEGIN ---') == 1 and ml.count(u'# --- SCAN END ---') == 1
i0 = [i for i, l in enumerate(ml) if l.startswith(u'# --- SCAN BEGIN ---')][0] + 1
i1 = [i for i, l in enumerate(ml) if l.startswith(u'# --- SCAN END ---')][0]
SCAN = ml[i0:i1]
FN = u'def _b%s_scan():' % NN
assert SCAN[0] == FN, SCAN[0]
BAD = [l for l in SCAN if l.lstrip().startswith(u'print(')]
assert not BAD, u'SCAN 段里有 print: %s' % BAD[:2]
WR = [l for l in SCAN if (u"'w'" in l or u'"w"' in l or u"'a'" in l)]
assert not WR, u'SCAN 段里有落盘动作: %s' % WR[:2]
assert u'F = {}' in u'\n'.join(SCAN), u'SCAN 段不建 F 字典'

# 源路径表: 取 mk 里 FILES 赋值(D 前缀 + 字面量), 逐字符核对后换成 SRC['Bxx'] 同源表
tree = ast.parse(mk)
files, dpre, srckey = None, None, None
for nd in tree.body:
    if isinstance(nd, ast.Assign):
        tgt = nd.targets[0]
        if not isinstance(tgt, ast.Name):
            continue
        if tgt.id == u'D' and isinstance(nd.value, ast.Constant):
            dpre = nd.value.value
        if tgt.id == u'FILES':
            files = nd.value
        if tgt.id == u'SRC' and isinstance(nd.value, ast.Dict):
            for kk, vv in zip(nd.value.keys, nd.value.values):
                if isinstance(kk, ast.Constant) and kk.value == TAG:
                    srckey = vv
assert files is not None and dpre is not None, u'缺 FILES ⇎ D 常量'
FS = []
for el in files.elts:
    assert (isinstance(el, ast.BinOp) and isinstance(el.left, ast.Name)
            and el.left.id == u'D' and isinstance(el.right, ast.Constant)), ast.dump(el)
    FS.append(dpre + el.right.value)
assert srckey is not None and isinstance(srckey, ast.Name) and srckey.id == u'FILES'
BODY = list(SCAN)
NL_ = u'\n'.join(BODY)
assert u'SRC[' in NL_ or u'SRC.get' in NL_, u'SCAN 段不从 SRC 取源(无法接线)'

REG = json.load(io.open(FLAT, encoding='utf-8'))
assert REG, u'扁平契约表为空'
assert all(re.match(u'^[0-9][0-9.]*$', k) for k in REG), sorted(REG)[:5]
assert all(v.startswith(u"%sV('" % TAG) for v in REG.values()), sorted(REG.values())[:3]

HTML = [f for f in FS if f.lower().endswith((u'.html', u'.htm'))]

SEG_B = [u"SRC['%s'] = [%s]" % (TAG, u', '.join([repr(f) for f in FS])),
         u"ATOM.add('%s')" % TAG]
if HTML:
    SEG_B.append(u"HTMLSRC.add('%s')  # %d 份带标签网页: 锚比对面按 audit._atom_face 剥壳"
                 % (TAG, len(HTML)))
SEG_B += [u"_B%s = _b%s_scan()" % (NN, NN),
          # V 的形状必须与建条目遍逐字同尺: i=None 给整值(标量), 给 i 取第 i 元素。
          u"%sV = lambda k, i=None: (_B%s[k] if i is None else _B%s[k][i])" % (TAG, NN, NN),
          u"DERIV['%s'] = %s" % (TAG, json.dumps(REG, ensure_ascii=False))]

block = u'\n'.join([
    u'# ====BEGIN %s==== (DERIV 键表 corpus/_b%sflat.json=%d 键)' % (TAG, NN, len(REG)),
    u"SEG_A_%s = r'''" % TAG,
    NL_,
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
import ast as _ast
_ast.parse(u'\n'.join([NL_, u"DERIV = {}", u"SRC = {}", u"ATOM = set()", u"HTMLSRC = set()"]))

full = io.open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else u''
pat = re.compile(u'# ====BEGIN %s====.*?# ====END %s====\n' % (TAG, TAG), re.S)
full = pat.sub(block, full) if pat.search(full) else full.rstrip(u'\n') + u'\n\n' + block
io.open(OUT, 'w', encoding='utf-8', newline=u'\n').write(full)
print(u'%s 补丁段已写入 %s: SCAN %d 行, SRC %d 份(网页 %d), DERIV %d 键'
      % (TAG, OUT, len(SCAN), len(FS), len(HTML), len(REG)))
