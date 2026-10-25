# -*- coding: utf-8 -*-
# 由三份 CoT 的 reasoning 区切候选原子池(只取 reasoning, 思维链锚须落在 reasoning 区)
# 输出 corpus/raw/probe/b36_pool.txt, 每行 "<标签>|<句子>"; 标签 D=deepseek, G=glm, N=nemotron
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
FILES = [(u'D', u'corpus/raw/cot/b36_tdi_deepseek.md'),
         (u'G', u'corpus/raw/cot/b36_tdi_glm.md'),
         (u'N', u'corpus/raw/cot/b36_tdi_nemotron.md')]
KEY = (u'已定', u'未决', u'表观', u'证据不存在', u'排除', u'临时', u'矛盾', u'旁路', u'联锁', u'热切割',
       u'聚合物', u'金相', u'LEL', u'上风向', u'防火墙', u'机理', u'阈值', u'需要', u'不能', u'因此',
       'settled', 'conclude', 'eliminat', 'cannot', 'evidence', 'interim', 'bypass', 'polymer',
       'metallogr', 'LEL', 'windward', 'contradict', 'threshold', 'deflagration', 'hot work')


def reason(p):
    s = io.open(p, encoding='utf-8').read()
    a = s.find(u'## [[REASONING]]')
    b = s.find(u'## [[ANSWER]]', a)
    return s[a + 17:b] if b > 0 else s[a + 17:]


def sentences(txt):
    txt = re.sub(u'[ \\t]+', u' ', txt)
    parts = re.split(u'(?<=[。！？；])', txt)
    parts = [q for p in parts for q in re.split(u'(?<=[.!?])\\n|\\n|(?<=\\.) (?=[A-Z])', p)]
    out = []
    for x in parts:
        x = x.strip().strip(u'#*|->')
        x = re.sub(u'^\\d+[\\.)]\\s*', u'', x)
        x = x.strip()
        if 14 <= len(x) <= 120 and any(k in x for k in KEY):
            out.append(x)
    return out


seen = set()
n = 0
for tag, f in FILES:
    keep = []
    for s in sentences(reason(f)):
        k = s.lower()
        if k in seen:
            continue
        seen.add(k)
        keep.append(s)
    io.open(u'corpus/raw/probe/b36_pool_%s.txt' % tag, 'w', encoding='utf-8').write(
        u'\n'.join(keep) + u'\n')
    print(tag, len(keep))
    n += len(keep)
allp = []
for tag, f in FILES:
    for line in io.open(u'corpus/raw/probe/b36_pool_%s.txt' % tag, encoding='utf-8'):
        if line.strip():
            allp.append(tag + u'|' + line.strip())
io.open(u'corpus/raw/probe/b36_pool.txt', 'w', encoding='utf-8').write(u'\n'.join(allp) + u'\n')
print('pool total', n)
