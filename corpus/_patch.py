# -*- coding: utf-8 -*-
"""_patch.py 用法: python -X utf8 corpus/_patch.py <file> <pairs.json>
pairs.json = [[old, new], ...]; 每处先断言在盘上恰出现一次, 全部通过才回写。"""
import io, json, sys

sys.stdout.reconfigure(encoding='utf-8')
path = sys.argv[1]
pairs = json.loads(io.open(sys.argv[2], encoding='utf-8').read())
s = io.open(path, encoding='utf-8').read()
for i, (old, new) in enumerate(pairs):
    n = s.count(old)
    if n != 1:
        print(u'拒绝: 第 %d 处出现 %d 次\n%s' % (i, n, old[:200]))
        sys.exit(1)
    s = s.replace(old, new)
io.open(path, 'w', encoding='utf-8', newline='\n').write(s)
print(u'已打 %d 处' % len(pairs))
