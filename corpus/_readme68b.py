# -*- coding: utf-8 -*-
"""README 记账补遍(B68 之后): 「转化指标」表只写到 B53, 合计行却按 67 条算——本遍把缺的行按 audit 当下输出补齐,
并把合计行的唯一码点那格换成 audit ALL 行的现算值(此前一直沿用上上遍读数)。
只做行级增补与两格改数, 不动任何条目的判词与叙述。"""
import io, json, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\r\n' if u'\r\n' in io.open(u'corpus/README.md', encoding='utf-8').read() else u'\n'
S = io.open(u'corpus/README.md', encoding='utf-8').read()
AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                     text=True, encoding='utf-8').stdout
assert u'T3 码位): PASS' in AUD, AUD[-500:]


def num(x):
    return int(''.join(c for c in x if c.isdigit()))


ROWS = {}
ALLR = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        c = [x.strip() for x in l.split(u'|')[1:-1]]
        ROWS[c[0]] = c
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR and len(ROWS) == 67, (len(ROWS), bool(ALLR))
UNIQ_ALL = num(ALLR[5])


def fmt(n):
    s = u'%d' % n
    if len(s) <= 3:
        return s
    g = [s[x:x + 3] for x in range(len(s) - 3, -1, -3)][::-1]
    if len(s) % 3:
        g = [s[:len(s) % 3]] + g
    return u' '.join(g)


L = S.split(NL)
h = [i for i, l in enumerate(L) if l.startswith(u'| entry | 编码字符 |')]
assert len(h) == 1, h
tot = [i for i in range(h[0], len(L)) if L[i].startswith(u'| **合计（')]
assert len(tot) == 1, tot
T = tot[0]
present = [l.split(u'|')[1].strip() for l in L[h[0] + 2:T]]
assert all(p.startswith(u'B') for p in present), present[:3]
missing = [k for k in ROWS if k not in present]
order = sorted(missing, key=lambda k: int(k[1:]))
NEW = [u'| %s | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
       % (k, fmt(num(ROWS[k][2])), ROWS[k][3], ROWS[k][4], ROWS[k][5], ROWS[k][7]) for k in order]
L[T:T] = NEW
cells = L[T + len(NEW)].split(u'|')
assert cells[5].strip().startswith(u'**2 230**') or cells[5].strip().startswith(u'**2 2'), cells[5]
OLD = L[T + len(NEW)]
cells[5] = u' **%s** ' % fmt(UNIQ_ALL)
cells[3] = cells[3].replace(u'唯一码点那列沿用上一遍读数、本遍未重算全库码点） ',
                             u'唯一码点那格改取本遍 audit 的 ALL 行现算值，B54 起的行由本遍补齐） ')
assert u'ALL 行现算值' in cells[3], cells[3][:80]
L[T + len(NEW)] = u'|'.join(cells)
NOTE = (u'（B54 起的 %d 行是本遍按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与'
        u'字符/语义单元五格, 不重写各条的口径注; 合计行的唯一码点即 ALL 行那个全库并集值。）' % len(NEW))
L.insert(T + len(NEW) + 1, u'')
L.insert(T + len(NEW) + 2, NOTE)
S = NL.join(L)
io.open(u'corpus/README.md', 'w', encoding='utf-8', newline=NL).write(S)
json.dump(dict(rows=len(ROWS), added=order, uniq_all=UNIQ_ALL,
               enc=num(ALLR[2]), dig=num(ALLR[1])),
          io.open(u'corpus/_b68metrics.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'转化指标表补 %d 行(%s)…%s ｜ 合计唯一码点 → %s ｜ 合计编码 %s／摘要 %s ｜ 表现共 %d 行'
      % (len(NEW), order[0], order[-1], fmt(UNIQ_ALL), fmt(num(ALLR[2])), fmt(num(ALLR[1])),
         len(present) + len(NEW)))
