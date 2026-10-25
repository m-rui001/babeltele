# -*- coding: utf-8 -*-
"""批量记账遍: 把 audit 已出行而未进转化指标表的所有条目一次补成直出机械行, 并把
条数陈述 ⇎ 门槛标题 ⇎ 推导陈述 ⇎ 合计行 ⇎ 机械行注 ⇎ 命令块五处改成与当下 audit 相符的话。

与 `_readme_metrics9.py` 的差别(那遍是 PASS 且只差 9 行):
① 本遍允许总判 FAIL——红列逐枚现采并把枚数写进句子, 不写死编号;
② 未列入集合 = audit 行集 − 表内行集, 由现算得出而非硬编码(本批 8 枚新建条 ⇎ B87–B91 都在其中);
③ 表内倒挂对逐对现算 pin 住(前一遍只 pin 住 (26,23) 一对, 本遍按当下表算, 对数与内容都写进收据);
④ 合计行五处数字全部来自本遍新跑的 audit, 且“一一对齐 ⇎ 逐格相符于 ALL 行”这两句只在真成立时才写;
⑤ 唯一码点那格是全库并集, 先逐条与 audit 现算值对拍(每条两格: 编码字符 ⇎ 唯一码点), 再取并集断言等于 ALL 格;
⑥ 门槛表 ⇎ 语料表两行不在本遍范围(新条的口径注各条自己那一遍记), 本遍把这一点在机械行注里如实写明。

用法: python -X utf8 corpus/_readme_batch.py [--dry]   (--dry 只跑量测与断言, 不落盘)
"""
import ast
import glob
import io
import json
import os
import re
import subprocess
import sys
ast_lit = ast.literal_eval

sys.stdout.reconfigure(encoding='utf-8')
DRY = u'--dry' in sys.argv
MARK = u'_readme_batch'


def fmt(n):
    s = u'%d' % n if isinstance(n, int) else u'%g' % n
    if u'.' in s:
        a, b = s.split(u'.', 1)
        return fmt(int(a)) + u'.' + b
    if not s.isdigit() or len(s) <= 3:
        return s
    g = [s[x:x + 3] for x in range(len(s) - 3, -1, -3)][::-1]
    if len(s) % 3:
        g = [s[:len(s) % 3]] + g
    return u' '.join(g)


def num(x):
    t = u''.join(c for c in x if c.isdigit())
    assert t, (u'无数字: %r' % x,)
    return int(t)


def ranges(ids):
    """把编号列表压成 `B01..B65、B67..B91` 这样的区间串: 断点必须真断(本库 B66 不在), 不写死通式。"""
    g, cur = [], [ids[0]]
    for a, b in zip(ids, ids[1:]):
        if b == a + 1:
            cur.append(b)
        else:
            g.append(cur)
            cur = [b]
    g.append(cur)
    out = []
    for c in g:
        if len(c) == 1:
            out.append(u'B%02d' % c[0])
        elif len(c) == 2:
            out.append(u'B%02d、B%02d' % (c[0], c[1]))
        else:
            out.append(u'B%02d..B%02d' % (c[0], c[-1]))
    s = u'、'.join(out)
    assert len(ids) == sum((c[-1] - c[0] + 1) if len(c) > 2 else len(c) for c in g)
    return s


AUD = (io.open(sys.argv[sys.argv.index(u'--audit-file') + 1], encoding=u'utf-8', errors=u'replace').read()
       if u'--audit-file' in sys.argv else
       subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                      text=True, encoding=u'utf-8').stdout)
VERD = [l for l in AUD.split(u'\n') if l.startswith(u'保真门槛(T1 字面 + T2 推导 + T3 码位):')]
assert len(VERD) == 1, VERD
GATE_PASS = VERD[0].endswith(u'PASS')
FDET = {}
for l in AUD.split(u'\n'):
    m = re.match(u'^  (B\\d+): 编码侧=(\\[.*?\\]) 原文侧=(\\[.*?\\]) 码位=(\\[.*?\\])\\s*$', l)
    if m:
        FDET[m.group(1)] = (m.group(2), m.group(3), m.group(4))
assert GATE_PASS or FDET, (VERD, FDET)
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])
SELFRED = [k for k in FDET if k == u'SELF']
assert not SELFRED, FDET

GROW, ALLR = [], None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        GROW.append([x.strip() for x in l.split(u'|')[1:-1]])
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR, AUD.split(u'\n')[:3]
ROWS = dict((c[0], c) for c in GROW)
IDS = sorted(int(c[0][1:]) for c in GROW)
FILES = glob.glob(u'corpus/babeltele/B*_*.md')
FIDS = sorted(int(re.match(r'corpus[/\\]babeltele[/\\]B(\d+)_', f).group(1)) for f in FILES)
assert FIDS == IDS, (FIDS[:5], IDS[:5], len(FILES))
assert len(GROW) == len(IDS) == len(set(IDS)) == len(FILES), (len(GROW), len(FILES))

# ---------- 编码区逐条现数 ⇎ 全库并集 ----------
ENCS, EN, DG = {}, {}, {}
for t, c in ROWS.items():
    f = glob.glob(u'corpus/babeltele/%s_*.md' % t)
    assert len(f) == 1, (t, len(f))
    tt = io.open(f[0], encoding=u'utf-8').read()
    mm = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', tt, re.S)
    assert mm, t
    e = mm.group(1).replace(u'\n', u'')
    assert len(e) == num(c[2]), (t, len(e), c[2])
    assert len(set(e)) == num(c[5]), (t, len(set(e)), c[5])
    ENCS[t] = set(e)
    EN[t] = len(e)
    DG[t] = num(c[1])
UNI = set().union(*[ENCS[t] for t in ROWS])
assert len(UNI) == num(ALLR[5]), (len(UNI), ALLR[5])
TOT_E, TOT_D = sum(EN.values()), sum(DG.values())
assert TOT_E == num(ALLR[2]) and TOT_D == num(ALLR[1]), (TOT_E, ALLR[2], TOT_D, ALLR[1])
assert u'%.1f%%' % (100.0 * TOT_E / TOT_D) == ALLR[3].strip(u'*'), (ALLR[3], TOT_E, TOT_D)

# ---------- README 现状 ----------
S = io.open(u'corpus/README.md', encoding=u'utf-8').read()
NL = u'\r\n' if u'\r\n' in S else u'\n'
L2 = S.split(NL)
h2 = [i for i, l in enumerate(L2) if l.startswith(u'| entry | 编码字符 |')]
assert len(h2) == 1, h2
t2 = [i for i in range(h2[0], len(L2)) if L2[i].startswith(u'| **合计（')]
assert len(t2) == 1, t2
RIDX = [(i, L2[i].split(u'|')[1].strip()) for i in range(h2[0] + 2, t2[0])]
assert all(lab.startswith(u'B') for _, lab in RIDX)
LISTED = [lab for _, lab in RIDX]
MARKED0 = len([l for l in L2[h2[0] + 2:t2[0]] if u'本行为 audit 直出' in l])
assert len(LISTED) == len(set(LISTED)), LISTED
UNACC = sorted([t for t in ROWS if t not in LISTED], key=lambda k: int(k[1:]))
assert UNACC, u'表已与 audit 对齐, 本遍无事可做'
NUM0 = [int(x[1:]) for x in LISTED]
INV0 = [(a, b) for a, b in zip(NUM0, NUM0[1:]) if b < a]


def mkrow(t):
    c = ROWS[t]
    assert EN[t] == num(c[2]) and len(ENCS[t]) == num(c[5])
    return (u'| %s | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
            % (t, fmt(EN[t]), c[3], c[4], fmt(num(c[5])), c[7]))


ADD = {}
for t in UNACC:
    prev = [i for i, lab in RIDX if int(lab[1:]) < int(t[1:])]
    idx = (max(prev) + 1) if prev else h2[0] + 2
    ADD.setdefault(idx, []).append(mkrow(t))
for idx in sorted(ADD, reverse=True):
    L2[idx:idx] = ADD[idx]
assert sum(len(v) for v in ADD.values()) == len(UNACC)
t2n = [i for i in range(h2[0], len(L2)) if L2[i].startswith(u'| **合计（')]
assert len(t2n) == 1
LAB = [L2[i].split(u'|')[1].strip() for i in range(h2[0] + 2, t2n[0])]
assert set(LAB) == set(ROWS) and len(LAB) == len(ROWS), (len(LAB), len(ROWS))
NUM1 = [int(x[1:]) for x in LAB]
INV1 = [(a, b) for a, b in zip(NUM1, NUM1[1:]) if b < a]
assert INV1 == INV0, (INV0, INV1)
HC = len(L2[h2[0]].split(u'|'))
for t in UNACC:
    row = [l for l in L2 if l.startswith(u'| %s | %s |' % (t, fmt(EN[t])))]
    assert len(row) == 1, (t, len(row))
    assert len(row[0].split(u'|')) == HC, (t, len(row[0].split(u'|')), HC)

# ---------- 合计行: 现算五格 ----------
ADDE, ADDG = sum(EN[t] for t in UNACC), sum(DG[t] for t in UNACC)
cells = L2[t2n[0]].split(u'|')
assert len(cells) == HC, (len(cells), HC)
OLDN = num(cells[1])
assert OLDN == len(LISTED), (OLDN, len(LISTED))
PREV_UNI = num(cells[5])
PREV_CLAIM = re.findall(u'合计（(\\d+) 条）', cells[1])
assert len(PREV_CLAIM) == 1 and int(PREV_CLAIM[0]) == len(LISTED), (PREV_CLAIM, len(LISTED))
cells[1] = u' **合计（%d 条）** ' % len(LAB)
cells[2] = u' **%s** ' % fmt(TOT_E)
assert len(UNI) >= PREV_UNI, (len(UNI), PREV_UNI)
cells[3] = (u' **%s**（摘要段合计 %s, 本遍直补 %s 共 %d 枚 %s 编码／%s 摘要; '
            u'本表 %d 行与 audit 的 %d 行一一对齐, '
            u'两列合计 ⇎ 保留率 ⇎ 唯一码点四格逐格相符于 ALL 行（%s ⇎ %s ⇎ %s ⇎ %s）; '
            u'唯一码点那格由本遍按 audit 的编码区正则逐条现数取并集（拼接后去重, 非各条之和）, '
            u'%d 条并集 %d 枚比上一遍登记的 %d 枚多 %d） '
            % (ALLR[3].strip(u'*'), fmt(TOT_D), u'／'.join(UNACC), len(UNACC), fmt(ADDE), fmt(ADDG),
               len(LAB), len(ROWS), ALLR[2], ALLR[1], ALLR[3], ALLR[5],
               len(LAB), len(UNI), PREV_UNI, len(UNI) - PREV_UNI))
cells[5] = u' **%s** ' % fmt(len(UNI))
assert cells[3].count(u'（') == cells[3].count(u'）'), (cells[3].count(u'（'), cells[3].count(u'）'))
assert u'|' not in cells[3]
L2[t2n[0]] = u'|'.join(cells)
assert len(L2[t2n[0]].split(u'|')) == HC

# ---------- 机械行注: 枚数与范围现采 ----------
NOTE = [i for i, l in enumerate(L2) if l.startswith(u'（B54 起的 ')]
assert len(NOTE) == 1, NOTE
m0 = re.match(u'（B54 起的 (\\d+) 行是按', L2[NOTE[0]])
assert m0, L2[NOTE[0]][:40]
DECLAIMED = int(m0.group(1))
i2 = [i for i, l in enumerate(L2) if l.startswith(u'| entry | 编码字符 |')][0]
t2b = [i for i in range(i2, len(L2)) if L2[i].startswith(u'| **合计（')][0]
MARKED1 = len([l for l in L2[i2 + 2:t2b] if u'本行为 audit 直出' in l])
MECH = len([x for x in LAB if int(x[1:]) >= 54])
L2[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与'
               u'字符/语义单元五格, 不重写各条的口径注; 本遍再直补 %s 共 %d 枚, 至此本表 %d 行与 audit 的 %d 行'
               u'一一对齐, 合计行的两列 ⇎ 保留率 ⇎ 唯一码点四格逐格相符于 ALL 行; 本遍直补的这几枚里, '
               u'新建条目的门槛表 ⇎ 语料表两行仍归各条自己那一遍记, 本遍不代其写口径注'
               u'（上一遍该注自称直补标记 %d 行, 本遍数得 %d 行, 补 %d 枚后 %d 行, 逐枚现数）。）'
               % (MECH, u'／'.join(UNACC), len(UNACC), len(LAB), len(ROWS),
                  DECLAIMED, MARKED0, len(UNACC), MARKED1))
assert L2[NOTE[0]].count(u'（') == L2[NOTE[0]].count(u'）')
assert MARKED1 == MARKED0 + len(UNACC), (MARKED0, MARKED1, len(UNACC))

# ---------- 条数陈述 ----------
HD = [i for i, l in enumerate(L2) if u'实际转化集，共 **' in l]
assert len(HD) == 1, HD
i0 = L2[HD[0]].index(u'共 **')
j = L2[HD[0]].index(u'），分两代。')
assert j > i0, (i0, j)
SEG = L2[HD[0]][i0:j + 1]
assert SEG.count(u'（') == SEG.count(u'）'), SEG[-40:]
NSEG = (u'共 **%d 条**（`babeltele/%s`, 本遍把 audit 已出行而未进转化指标表的 %s 共 %d 枚各补一行直出机械行, '
        u'合计行随之按本表所列 %d 条现算 ⇎ 与 audit 的 %d 行一一对齐 ⇎ 唯一码点逐条现数取并集 %d 枚'
        % (len(ROWS), ranges(IDS), u'／'.join(UNACC), len(UNACC), len(LAB), len(ROWS), len(UNI)))
L2[HD[0]] = L2[HD[0]][:i0] + NSEG + u'）' + L2[HD[0]][j + 1:]
_line = L2[HD[0]]
assert _line.count(u'（') == _line.count(u'）'), _line[-90:]
assert u'**%d 条**' % len(ROWS) in _line and u'，分两代。' in _line

# ---------- 门槛标题 ⇎ 推导陈述 ----------
GT = [i for i, l in enumerate(L2) if l.startswith(u'## 保真门槛：')]
assert len(GT) == 1, GT
PD = [i for i, l in enumerate(L2) if u'结果按锚点小数位四舍五入相等。当前' in l]
assert len(PD) == 1, PD
if GATE_PASS:
    L2[GT[0]] = (u'## 保真门槛：`python corpus/audit.py` → **PASS**（%d 条: 逐条 T1 字面回源 ⇎ T2 推导复算 ⇎ '
                 u'T3 码位清单全绿, 无红灯）' % len(ROWS))
    L2[PD[0]] = (u'   结果按锚点小数位四舍五入相等。当前 **%d 条语料／%d 条**推导: 无一条未回源'
                 u'（audit 自报“已机检的推导 %d 条”, 行集与条目文件数相符 %d 行 ⇎ %d 个文件）, 如'
                 % (len(ROWS), PROOFS, PROOFS, len(ROWS), len(FILES)))
else:
    REDS = sorted(FDET, key=lambda k: int(k[1:]))
    NEWRED = [t for t in UNACC if t in FDET]
    CNT = lambda i: u'⇎'.join(str(len(ast_lit(FDET[r][i]))) for r in REDS)
    CP = lambda r: sum(len(ast_lit(x)) for x in FDET[r])
    L2[GT[0]] = (u'## 保真门槛：`python corpus/audit.py` → **FAIL**（%d 条: 红灯 %s 共 %d 枚, '
                 u'编码侧 %s ⇎ 原文侧 %s ⇎ 码位 %s; 本遍直补的 %d 枚里 %s 枚在红列）'
                 % (len(ROWS), u'／'.join(REDS), len(REDS), CNT(0), CNT(1), CNT(2), len(UNACC),
                    u'%d' % len(NEWRED)))
    L2[PD[0]] = (u'   结果按锚点小数位四舍五入相等。当前 **%d 条语料／%d 条**推导: 除 %s 共 %d 枚的 T1 数字锚未回源'
                 u'（编码侧 %s ⇎ 原文侧 %s ⇎ 码位 %s, 逐枚合计 %s）之外全部通过（audit 自报“已机检的推导 %d 条”, '
                 u'行集与条目文件数相符 %d 行 ⇎ %d 个文件; 本遍直补的 %d 枚中在红列的是 %s）, 如'
                 % (len(ROWS), PROOFS, u'／'.join(REDS), len(REDS), CNT(0), CNT(1), CNT(2),
                    u'⇎'.join(str(CP(r)) for r in REDS), PROOFS, len(ROWS), len(FILES),
                    len(UNACC), u'／'.join(NEWRED) if NEWRED else u'无'))
for l in (L2[GT[0]], L2[PD[0]]):
    assert l.count(u'（') == l.count(u'）'), l[:80]
    assert u'|' not in l, l[:80]

# ---------- 命令块: 登记本遍这一枚脚本(二次及以后跑就地改写那一行, 不追加第二行) ----------
CMD = [i for i, l in enumerate(L2) if l.startswith(u'python -X utf8 corpus/_readme53.py')]
assert len(CMD) == 1, CMD
LINE = (u'python -X utf8 corpus/%s.py            # 批量记账: 真跑 audit 后把已出行未列表的 %d 枚各补一行直出机械行,'
        u' 表从 %d 行推到 %d 行 ⇎ 与 audit 的 %d 行对齐; 编码区逐条现数（%d 条×2 格与 audit 对拍）取并集=%s'
        % (MARK, len(UNACC), len(LISTED), len(LAB), len(ROWS), len(LAB), fmt(len(UNI))))
SELF = [i for i, l in enumerate(L2) if l.startswith(u'python -X utf8 corpus/%s.py' % MARK)]
if SELF:
    assert len(SELF) == 1 and u'本行首跑登记' not in L2[SELF[0]], SELF
    L2[SELF[0]] = LINE
else:
    L2[CMD[0]:CMD[0]] = [LINE]
assert len([l for l in L2 if l.startswith(u'python -X utf8 corpus/%s.py' % MARK)]) == 1

NEW = NL.join(L2)
assert len(NEW.split(NL)) == len(L2)
assert NEW != S
assert NEW.count(u'## 转化指标') == 1

RECEIPT = {u'added': UNACC, u'added_n': len(UNACC), u'added_enc': ADDE, u'added_dig': ADDG,
           u'listed_before_n': len(LISTED), u'listed_after': LAB, u'listed_after_n': len(LAB),
           u'audit_rows': len(ROWS), u'files': len(FILES), u'enc': TOT_E, u'dig': TOT_D,
           u'retention': ALLR[3].strip(u'*'), u'union': len(UNI), u'union_prev': PREV_UNI,
           u'union_delta': len(UNI) - PREV_UNI, u'all_enc': ALLR[2], u'all_dig': ALLR[1],
           u'proofs': PROOFS, u'gate': u'PASS' if GATE_PASS else u'FAIL',
           u'red': {k: [len(ast_lit(v[0])), len(ast_lit(v[1])), len(ast_lit(v[2]))] for k, v in FDET.items()},
           u'inversion': INV1, u'mech_rows': MECH, u'dry': DRY, u'delta_chars': len(NEW) - len(S)}

if DRY:
    json.dump(RECEIPT, io.open(u'corpus/_batchreadme_dry.json', u'w', encoding=u'utf-8'),
              ensure_ascii=False, indent=1)
    print(u'[dry] 量测与断言全过: 待补 %s ⇎ 表 %d→%d 行 ⇎ 合计 %s／%s ⇎ 并集 %d(+%d) ⇎ 总判 %s ⇎ 红列 %s'
          % (u'／'.join(UNACC), len(LISTED), len(LAB), fmt(TOT_E), fmt(TOT_D), len(UNI),
             len(UNI) - PREV_UNI, RECEIPT[u'gate'], u'／'.join(sorted(FDET)) or u'无'))
else:
    io.open(u'corpus/README.md.tmpbatch', u'w', encoding=u'utf-8', newline=NL).write(NEW)
    json.dump(RECEIPT, io.open(u'corpus/_batchreadme.json', u'w', encoding=u'utf-8'),
              ensure_ascii=False, indent=1)
    os.replace(u'corpus/README.md.tmpbatch', u'corpus/README.md')
    print(u'批量记账完成: 转化指标表 %d 行 → %d 行（补 %s） ｜ 合计 %s 编码 ⇎ %s 摘要 ⇎ %s ⇎ 并集 %s ｜ '
          u'四格相符于 ALL（%s ⇎ %s ⇎ %s ⇎ %s） ｜ 逐条对拍 %d 条×2 格 ｜ audit %d 行 ⇎ 文件 %d ⇎ 推导 %d 条 ｜ '
          u'总判 %s ⇎ 红列 %s ｜ 倒挂对 %s ｜ 机械行 %d 枚 ｜ 净变化 %+d 字符'
          % (len(LISTED), len(LAB), u'⇎'.join(UNACC), fmt(TOT_E), fmt(TOT_D), ALLR[3], fmt(len(UNI)),
             ALLR[2], ALLR[1], ALLR[3], ALLR[5], len(LAB), len(ROWS), len(FILES), PROOFS,
             RECEIPT[u'gate'], u'／'.join(sorted(FDET)) or u'无', INV1, MECH, len(NEW) - len(S)))

