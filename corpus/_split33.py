# -*- coding: utf-8 -*-
# B33 原子池: 三份 CSB 文件按句切(保护缩写点), 逐行带 tag 前缀输出, 保证每个原子是同一行内的连续片段
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

FILES = [(u'U', u'corpus/raw/prose/csb_clairton_update.txt'),
         (u'I', u'corpus/raw/prose/csb_clairton_interim.txt'),
         (u'F', u'corpus/raw/prose/csb_clairton_final.txt')]

PROTECT = [u'U.S.', u'C.F.R.', u'pp.', u'p.', u'Inc.', u'Ltd.', u'No.', u'e.g.,', u'i.e.,',
           u'Sec.', u'U.S.C.', u'Ps.', u'Fig.', u'vs.', u'Dr.', u'Mr.']

out = []
for tag, path in FILES:
    t = io.open(path, encoding=u'utf-8').read().split(u'# note:', 1)[1].split(u'\n', 1)[1]
    t = u' '.join(x.strip() for x in t.split(u'\n') if x.strip())
    for k in PROTECT:
        t = t.replace(k, k.replace(u'.', u'\u2024'))
    for s in re.split(u'(?<=[.。!?:]) +', t):
        s = s.strip()
        for k in PROTECT:
            s = s.replace(k.replace(u'.', u'\u2024'), k)
        if len(s) >= 12:
            out.append(u'%s\t%s' % (tag, s))

io.open(u'corpus/raw/probe/b33_atoms.txt', u'w', encoding=u'utf-8').write(u'\n'.join(out) + u'\n')
io.open(u'corpus/raw/probe/b33_atoms_plain.txt', u'w', encoding=u'utf-8').write(
    u'\n'.join(x.split(u'\t', 1)[1] for x in out) + u'\n')
print(u'atoms=%d' % len(out))
