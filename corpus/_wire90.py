# -*- coding: utf-8 -*-
# 幂等生成 B90 接线补丁段(照 _wire87ge.py 结构: SRC/ATOM/_b90_scan/DERIV/B90V)。
# 本脚本绝不写 corpus/audit.py——只把主线程要贴的三段文本splice进共享补丁
# corpus/_tmpNN_audit_patch.py 的 ====BEGIN/END B90==== 横幅之间(其它条目的横幅原样保留)。
# audit.py 已含 DERIV['B90'] 即视为已接线, 跳过。
import ast, io, json, os, re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

P = 'corpus/audit.py'
OUT = 'corpus/_tmpNN_audit_patch.py'
TAG = 'B90'
s = io.open(P, encoding='utf-8', errors='replace').read()
if "DERIV['%s']" % TAG in s:
    print('%s 已在 audit.py 接线, 跳过(补丁无须再贴)' % TAG)
    raise SystemExit

BLOCK = u'''SRC['B90'] = ['corpus/raw/papers/arxiv_2610.31657.txt']
ATOM.add('B90')


def _b90_scan():
    """B90 现量: 源面 = 去壳正文(壳=首个空行之前)折平空白; 表内数一律由摘要面的现读句柄正则取回."""
    raw = io.open(SRC['B90'][0], encoding='utf-8', errors='replace').read()
    shell = raw.partition(u'\\n\\n')[0]
    body = raw.partition(u'\\n\\n')[2]
    flat = u' '.join(body.split())
    low = flat.lower()
    F = {}
    F['chars'] = [len(flat)]
    F['words'] = [len(flat.split())]
    F['submit_year'] = [int(re.search(r'submitted (\\d{4})', shell).group(1))]
    F['arxiv_id'] = [re.search(r'src: arXiv:([0-9.]+)', shell).group(1)]
    F['ticket_corpus'] = [int(re.search(r'public ([\\d,]+)-ticket', flat).group(1).replace(',', ''))]
    F['test_subset'] = [int(re.search(r'stratified ([\\d,]+)-ticket', flat).group(1).replace(',', ''))]
    F['thr'] = [float(re.search(r'threshold of ([0-9.]+)', flat).group(1))]
    F['cost_before'] = [float(re.search(r'cost from ([0-9.]+) to', flat).group(1))]
    F['cost_after'] = [float(re.search(r'cost from ([0-9.]+) to ([0-9.]+)', flat).group(2))]
    F['ci_lo'] = [float(re.search(r'CI \\[([\\d.]+)%, ([\\d.]+)%\\]', flat).group(1))]
    F['ci_hi'] = [float(re.search(r'CI \\[([\\d.]+)%, ([\\d.]+)%\\]', flat).group(2))]
    F['wrong_before'] = [float(re.search(r'wrong routes from ([\\d.]+)%', flat).group(1))]
    F['wrong_after'] = [float(re.search(r'wrong routes from [\\d.]+% to ([\\d.]+)%', flat).group(1))]
    F['llm_acc'] = [float(re.search(r'reaches ([0-9.]+) accuracy', flat).group(1))]
    F['bert_acc'] = [float(re.search(r'versus ([0-9.]+) for fine-tuned', flat).group(1))]
    F['auroc_flat'] = [float(re.search(r'AUROC (\\d+(?:\\.\\d+)*)', flat).group(1))]
    F['breakeven_p'] = [float(re.search(r'break-even probability ([0-9.]+)', flat).group(1))]
    for kw in [u'cost', u'calibration', u'abstention', u'ticket', u'policy']:
        F['n_' + kw] = [low.count(kw)]
    return F


_B90 = _b90_scan()
B90V = lambda k, i=None: (_B90[k][0] if i is None else _B90[k][i])'''

REG = json.load(io.open('corpus/_b90flat.json', encoding='utf-8'))
assert s.count('rows, fails, proofs, soft_all = [], [], [], []') == 1
assert s.count('               B86V=B86V)') == 1

HEADER = u'''# -*- coding: utf-8 -*-
# B89/B90/B91 接线补丁汇总(各条目一个 ====BEGIN/END tag==== 横幅段; 由 corpus/_wire89.py,
# _wire90.py, _wire91.py 各自幂等splice自己的横幅, 互不覆盖)。本文件不执行、不 import audit。
# 主线程按 B89→B90→B91 串行把三段贴进 corpus/audit.py, 每段内三处(各处锚行在当前 audit.py 均唯一):
#   [SEG_A] 整段插在行 "rows, fails, proofs, soft_all = [], [], [], []" 之前
#   [SEG_B] 整段紧接 [SEG_A] 之后、同一行之前(即挂在同一条锚行前, 顺序 A→B)
#   [SEG_C] 插在 make_env 的 env 字典中、行 "               B86V=B86V)" 之前(新行自带逗号尾, B86V 保持行尾收括号)
# 幂等哨兵: audit.py 出现 DERIV['B89'] / DERIV['B90'] / DERIV['B91'] 即该条已接线。
# 语法自检: python -X utf8 -c "import ast,io;ast.parse(io.open('corpus/_tmpNN_audit_patch.py',encoding='utf-8').read())"
'''

block = u'\n'.join([
    u'# ====BEGIN %s==== (DERIV 键表 corpus/_b90flat.json=%d 键, _deriv90.json 同表)' % (TAG, len(REG)),
    u"SEG_A_%s = r'''" % TAG,
    BLOCK,
    u"'''",
    u"",
    u"SEG_B_%s = r'''" % TAG,
    u"DERIV['B90'] = " + json.dumps(REG, ensure_ascii=False),
    u"'''",
    u"",
    u"SEG_C_%s = r'''" % TAG,
    u"               B90V=B90V,",
    u"'''",
    u'# ====END %s====' % TAG,
    u'',
])

if os.path.exists(OUT):
    full = io.open(OUT, encoding='utf-8').read()
else:
    full = HEADER
beg, end = u'# ====BEGIN %s====' % TAG, u'# ====END %s====' % TAG
if beg in full and end in full:
    pat = re.compile(re.escape(beg) + u'.*?' + re.escape(end) + u'\n?', re.S)
    full = pat.sub(lambda m: block, full, count=1)
else:
    full = full.rstrip(u'\n') + u'\n\n' + block
ast.parse(full, 'audit_patch')  # 语法自检: 汇总后的补丁文本整体必须可解析
io.open(OUT, 'w', encoding='utf-8', newline=chr(10)).write(full)
print('wire90 完成: %d 键 → %s [%s 横幅段] (audit.py 未动)' % (len(REG), OUT, TAG))
