# -*- coding: utf-8 -*-
import io, tokenize, sys

OK = set(['n', 'l', 'r', 't', 'b', 'f', 'v', 'u', 'U', 'x', '\\', "'", '"', '0', '1', '2', '3',
          '4', '5', '6', '7', '\n'])
bad = []
for p in sys.argv[1:]:
    src = io.open(p, 'rb').read()
    for tok in tokenize.tokenize(io.BytesIO(src).readline):
        if tok.type != tokenize.STRING:
            continue
        s = tok.string
        i = 0
        while s[i] not in '"\'':
            i += 1
        pre = s[:i].lower()
        body = s[i:]
        for q in ('"""', "'''", '"', "'"):
            if body.startswith(q):
                pre2 = s[:i]
                if 'r' in pre2:
                    body = None
                else:
                    body = body[len(q):]
                    if body.endswith(q[0]) and len(body) >= 1:
                        body = body[:-len(q)]
                break
        if not body:
            continue
        j = 0
        while j < len(body):
            if body[j] == '\\' and j + 1 < len(body):
                ch = body[j + 1]
                if ch not in OK:
                    bad.append((p, tok.start[0], repr(body[j:j + 2])))
                if ch in '01234567':
                    j += 4
                    continue
                j += 2
                continue
            j += 1
print(len(bad))
for x in bad:
    print(x)
