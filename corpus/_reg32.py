# -*- coding: utf-8 -*-
import io, json

E = json.load(io.open(u'corpus/raw/probe/b32_deriv.json', encoding='utf-8'))
lines = []
for i, k in enumerate(sorted(E)):
    pad = u'         ' if i else u" 'B32': {"
    lines.append(u"%s'%s': %r," % (pad, k, E[k]))
lines[-1] = lines[-1] + u'}'
block = u'\n'.join(lines) + u'\n'

p = u'corpus/audit.py'
s = io.open(p, encoding='utf-8').read()
assert u"'B32': {" not in s, 'already registered'
anchor = u"         '91.6': 'round(L(\"724\")/L(\"790\")*100,1)'},\n"
assert s.count(anchor) == 1, 'anchor not unique'
s = s.replace(anchor, anchor + block)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print(block[:200])
print('entries=', len(E))
