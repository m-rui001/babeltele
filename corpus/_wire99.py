# -*- coding: utf-8 -*-
# 幂等生成 B99 接线补丁(照 _wire96.py 的横幅 splice 机制): _b99_scan 的函数体不重写,
# 直接从 corpus/_mkB99.py 的 # --- SCAN BEGIN/END --- ⇎ # --- PICK BEGIN/END --- 之间摘出
# 同一段量测+对账代码, 前置它依赖的常量块(NL ⇎ LBL ⇎ IDS ⇎ PATH ⇎ NSRC ⇎ FAM ⇎ F ⇎ DER ⇎ LITK),
# 其中 PATH 换成 SRC['B99']; 诊断 print 机械换成 _sil(空函数), sys.stdout.flush() 换成 pass,
# 行结构一行不动, 所以进门后的现量与建条目遍用的算法逐字符同一条。
# 本脚本绝不写 corpus/audit.py——只把三段文本 splice 进 corpus/_tmpNN_audit_patch.py 的横幅之间;
# 贴之前先在内存里 exec 一遍函数体, 与 corpus/_b99flat.json 逐键比, 不同就不出补丁。
import ast
import io
import json
import os
import re
import sys

TAG = u'B99'
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
tree = ast.parse(mk)

# 常量块: 只取 SCAN 之前的模块级简单赋值, PATH 那一枚换成 SRC['B99']
CONST = []
for nd in tree.body:
    if not isinstance(nd, ast.Assign) or nd.lineno >= S0:
        continue
    tgt = nd.targets[0]
    if not (isinstance(tgt, ast.Name) and tgt.id in
            (u'NL', u'LBL', u'IDS', u'PATH', u'NSRC', u'FAM', u'F', u'DER', u'LITK')):
        continue
    if tgt.id == u'PATH':
        CONST.append(u'PATH = SRC[u\'%s\']' % TAG)
        continue
    CONST.extend(ml[nd.lineno - 1:nd.end_lineno])
assert len(CONST) >= 8, CONST
BODY = CONST + ml[S0:S1] + ml[K0:K1]
BODY.append(u'return F')

# 诊断语句换空操作(保留行结构: print 的续行照旧缩进, 只是首词改名)
DROP = []
for i, l in enumerate(BODY):
    t = l.lstrip()
    if t.startswith(u'sys.stdout.flush()'):
        BODY[i] = l.replace(u'sys.stdout.flush()', u'pass')
    assert not t.startswith((u'import ', u'from ')), l
PRINTS = [i for i, l in enumerate(BODY) if l.lstrip().startswith(u'print(')]
BODY = [l.replace(u'print(', u'_sil(', 1) if l.lstrip().startswith(u'print(') else l for l in BODY]
WR = [l for l in BODY if (u"'w'" in l or u'"w"' in l or u"'a'" in l or u'babeltele' in l)]
assert not WR, u'摘出的段里有落盘动作: %s' % WR[:2]
assert u'SRC[u\'%s\']' % TAG in u'\n'.join(BODY), u'源没换成 SRC[\'%s\']' % TAG

FN = [u'def _b%s_scan():' % NN,
      u'    """B99 现量(摘自 corpus/_mkB99.py 的 SCAN+PICK 段, 与建条目遍同一套代码): 一条 TLS 记录',
      u'    最多装多少明文——8446 ⇎ 5246 ⇎ 8449 ⇎ 6066 ⇎ OpenSSL split_send_fragment.pod 五份一手文书',
      u'    的四档读面阶梯(逐行 ⇎ 折平 ⇎ 摘壳 ⇎ 摘壳+幂式归一)、三轨行尺、单位词档、等式族 ⇎ 与采集遍',
      u'    _pick99 的逐键对账, 一律在此现算。"""',
      u'    import json',
      u'    import bisect',
      u'    from collections import Counter',
      u'    _sil = lambda *a, **k: None']
BLOCK = u'\n'.join(FN + [u'    ' + l for l in BODY])
ast.parse(BLOCK + u'\n')

# 门内现算必须与建条目遍逐键同值——先在内存 exec 一遍再出补丁
PATHL = None
for nd in tree.body:
    if isinstance(nd, ast.Assign) and isinstance(nd.targets[0], ast.Name)             and nd.targets[0].id == u'PATH':
        PATHL = ast.literal_eval(nd.value)
assert isinstance(PATHL, list) and len(PATHL) == 5, PATHL
NS = {u'SRC': {TAG: PATHL}, u'io': io, u're': re, u'json': json, u'os': os, u'sys': sys}
exec(compile(BLOCK, u'<b99scan>', u'exec'), NS)
GOT = NS[u'_b%s_scan' % NN]()
EXP = json.load(io.open(FLAT, encoding=u'utf-8'))
DIF = [k for k in EXP if k not in (u'pick_excl',) and json.dumps(GOT.get(k), sort_keys=True)
       != json.dumps(EXP[k], sort_keys=True)]
assert not DIF, u'门内现量与建条目遍不同值: %s' % DIF[:8]
print(u'门内现算自校: %d 键逐键同值(采集键表除外)' % len(EXP))

REG = json.load(io.open(CONTRACT, encoding=u'utf-8'))
# 键形: 十进制数, 允许负号(-1 来自 rows_ledger——pod 那份无换页符 ⇎ 文件以换行收尾,
# splitlines 档比 split('\n') 档少一行), 允许小数点(差值档)
assert REG and all(re.match(u'^-?[0-9][0-9.]*$', k) for k in REG), sorted(REG)[:5]
assert all(v.startswith(u"%sV('" % TAG) for v in REG.values()), sorted(REG.values())[:3]
# 每条 DERIV 表达式在门内真值必须与建条目时同值(否则门槛判的是别的数)
BAD = []
for k, v in REG.items():
    try:
        got = eval(v.replace(u'%sV' % TAG, u'(lambda kk, ii=None: GOT[kk] if ii is None else GOT[kk][ii])'),
                   {u'GOT': GOT})
    except Exception as e:
        BAD.append((k, v, repr(e)[:60]))
        continue
    if u'%s' % got != k:
        BAD.append((k, v, u'现值 %r' % (got,)))
assert not BAD, u'DERIV 现值不符: %s' % BAD[:6]
print(u'DERIV %d 枚键全可在门内复算, 现值与登记值逐枚同' % len(REG))

FS = NS[u'SRC'][TAG]
assert s.count(u'rows, fails, proofs, soft_all = [], [], [], []') == 1
assert s.count(u'               B86V=B86V)') == 1

SEG_B = [u"SRC['%s'] = [%s]" % (TAG, u', '.join([repr(f) for f in FS])),
         u"ATOM.add('%s')" % TAG,
         u"_B%s = _b%s_scan()" % (NN, NN),
         u"%sV = lambda k, i=None: (_B%s[k] if i is None else _B%s[k][i])" % (TAG, NN, NN),
         u"DERIV['%s'] = %s" % (TAG, json.dumps(REG, ensure_ascii=False))]

block = u'\n'.join([
    u'# ====BEGIN %s==== (DERIV 键表 corpus/_b%scontract.json=%d 键 ⇎ 现量 %d 行)' % (TAG, NN, len(REG),
                                                                                      len(BODY)),
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
      % (TAG, OUT, BLOCK.count(u'\n') + 1, len(CONST), S1 - S0 + K1 - K0, len(PRINTS), len(FS), len(REG)))
