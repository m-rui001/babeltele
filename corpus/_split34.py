# -*- coding: utf-8 -*-
# B34 候选原子池: 汕头"12·9"调查报告两转载版(蔓延扩大四条 ⇎ 责任六级+整改八项)按中文句末标点切句
import io
import re

FILES = (u'corpus/raw/prose/cn_fire_report_spread.txt',
         u'corpus/raw/prose/cn_fire_report_liability.txt')
TAGS = (u'S', u'L')
out = []
plain = []
for tag, f in zip(TAGS, FILES):
    t = io.open(f, encoding=u'utf-8').read()
    body = t.split(u'# note:', 1)[1].split(u'\n', 1)[1]
    body = re.sub(u'(?<=[一-鿿]) (?=[一-鿿])', u'', body)
    body = re.sub(u'(?<=[一-鿿])\n(?=[一-鿿])', u'', body)
    for line in body.split(u'\n'):
        line = line.strip()
        if not line:
            continue
        for s in re.split(u'(?<=[。？！])', line):
            s = s.strip()
            if len(s) >= 8:
                out.append(u'%s\t%s' % (tag, s))
                plain.append(s)
io.open(u'corpus/raw/probe/b34_atoms.txt', u'w', encoding=u'utf-8').write(u'\n'.join(out) + u'\n')
io.open(u'corpus/raw/probe/b34_atoms_plain.txt', u'w', encoding=u'utf-8').write(u'\n'.join(plain) + u'\n')
print(u'atoms=%d  S=%d  L=%d' % (len(out), sum(1 for x in out if x.startswith(u'S')),
                                 sum(1 for x in out if x.startswith(u'L'))))
