# -*- coding: utf-8 -*-
import re, io

SRC = {'N': u'corpus/raw/prose/cn_csrc_manipulation_fourmen.txt',
       'O': u'corpus/raw/prose/cn_csrc_manipulation_tenmen.txt',
       'K': u'corpus/raw/prose/cn_csrc_fake_info_lurunkai.txt'}
out = []
for tag in ('N', 'O', 'K'):
    t = io.open(SRC[tag], encoding='utf-8').read()
    body = t.split(u'# note:', 1)[1].split(u'\n', 1)[1]
    for line in body.split(u'\n'):
        line = line.strip()
        if not line:
            continue
        for p in re.split(u'(?<=[。；:])', line):
            p = p.strip()
            if len(p) >= 5:
                out.append(u'%s\t%s' % (tag, p))
io.open(u'corpus/raw/probe/b32_atoms.txt', 'w', encoding='utf-8', newline='\n').write(u'\n'.join(out) + u'\n')
for i, l in enumerate(out):
    print(i, l)
print('total', len(out))
