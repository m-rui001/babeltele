# -*- coding: utf-8 -*-
"""全库补记遍: 把 9 条“已接线而未进转化指标表”的条目补成 `audit.py` 直出的机械行, 合计行从 75 条推到 84 条。

本遍是真跑 `corpus/audit.py` 后按当下输出记账, 不引用任何采集侧留档:
① 合计行两列自本遍起与 audit 的 ALL 行逐格相符——前一遍那句“故不取 audit 的 ALL 行”是因为表里缺 9 行,
   补全之后它失效, 必须改写而不是留着;
② 唯一码点那格是全库并集（把 84 份编码区拼接后去重）, 不是各条唯一码点之和; 本遍按 audit 的编码区切法
   逐条现数, 84 条逐条与 audit 现算值对拍后再取并集, 并断言并集恰等于 ALL 行那一格;
③ 表内行序不按编号（在库那处 B26 先于 B23 是前一遍直补留下的）: 插入按“数值上邻接”定位, 末尾断言除这一处
   倒挂外全表升序——倒挂对由本遍现算并 pin 住, 不写死成通式;
④ 一条条目在 README 里应有三处表行: 门槛表 ⇎ 语料表 ⇎ 转化指标表。本遍只补第三格, 落盘前断言这 9 条
   各自已有前两行（各 2 枚 `| Bxx |` 行）, 落盘后各 3 枚;
⑤ 改写第 9 行那句条数陈述用 index 定位“，分两代。”而不是正则吞括号: 那句里外两层括号, 替换文本必须保持
   （ ⇎ ）各两枚, 否则每跑一遍挪一枚;
⑥ 本遍不改条数（84 ⇎ 84）也不改推导数, 但要把这两处现算值与新跑的 audit 对拍, 不符就如实改文而不是沉默;
⑦ 记入命令块的只有本遍这一枚新脚本, 不回补前几遍未登记的 `_readmeNN.py` 行——那是前几遍的选择, 本遍不替它们重写历史。
"""
import glob
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
NLROWS = 9
UNACC_IDS = [73, 75, 76, 77, 78, 79, 83, 84, 85]


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
    return int(u''.join(c for c in x if c.isdigit()))


AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                     text=True, encoding=u'utf-8').stdout
VERD = [l for l in AUD.split(u'\n') if l.startswith(u'保真门槛(T1 字面 + T2 推导 + T3 码位):')]
assert len(VERD) == 1, VERD
GATE_PASS = VERD[0].endswith(u'PASS')
FAILED = [l.split(u':')[0].strip() for l in AUD.split(u'\n') if re.match(u'^  B\\d+: ', l)]
assert GATE_PASS and not FAILED, (VERD, FAILED)
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])

GROW, ALLR = [], None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        GROW.append([x.strip() for x in l.split(u'|')[1:-1]])
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR and len(GROW) >= 80
ROWS = dict((c[0], c) for c in GROW)
IDS = sorted(int(c[0][1:]) for c in GROW)
FILES = glob.glob(u'corpus/babeltele/B*_*.md')
assert len(GROW) == len(IDS) == len(set(IDS)) == len(FILES), (len(GROW), len(FILES))

# ---------- 编码区: 照 audit 的切法逐条现数 ----------
ENCS, EN, DG = {}, {}, {}
for t, c in ROWS.items():
    f = glob.glob(u'corpus/babeltele/%s_*.md' % t)
    assert len(f) == 1, t
    tt = io.open(f[0], encoding=u'utf-8').read()
    mm = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', tt, re.S)
    assert mm, t
    e = mm.group(1).replace(u'\n', u'')
    assert len(e) == num(c[2]), (t, len(e), c[2])
    assert len(set(e)) == num(c[5]), t
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
assert len(h2) == 1
t2 = [i for i in range(h2[0], len(L2)) if L2[i].startswith(u'| **合计（')]
assert len(t2) == 1
RIDX = [(i, L2[i].split(u'|')[1].strip()) for i in range(h2[0] + 2, t2[0])]
assert all(lab.startswith(u'B') for _, lab in RIDX)
LISTED = [lab for _, lab in RIDX]
assert len(LISTED) == len(set(LISTED))
UNACC = [t for t in ROWS if t not in LISTED]
assert sorted(int(x[1:]) for x in UNACC) == UNACC_IDS, sorted(UNACC)
assert len(UNACC) == NLROWS, sorted(UNACC)
NUM0 = [int(x[1:]) for x in LISTED]
INV = [(a, b) for a, b in zip(NUM0, NUM0[1:]) if b < a]
assert INV == [(26, 23)], INV
for t in UNACC:
    nrow = len([l for l in L2 if l.startswith(u'| %s | ' % t)])
    assert nrow == 2, (t, nrow)
# 门槛表 ⇎ 语料表两行确已在前几遍记过: 逐条查两种形状的表行都在
for t in UNACC:
    assert any(l.startswith(u'| %s | ' % t) and u'（新建' in l for l in L2), t
    assert any(l.startswith(u'| %s | `' % t) or (l.startswith(u'| %s | ' % t) and u'`raw/' in l)
               for l in L2), t

# ---------- 9 枚机械行: 全部取本遍新跑的 audit 值 ----------
def mkrow(t):
    c = ROWS[t]
    assert EN[t] == num(c[2]) and len(ENCS[t]) == num(c[5])
    return (u'| %s | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
            % (t, fmt(EN[t]), c[3], c[4], fmt(num(c[5])), c[7]))


ADD = {}
for t in sorted(UNACC, key=lambda k: int(k[1:])):
    prev = [i for i, lab in RIDX if int(lab[1:]) < int(t[1:])]
    idx = (max(prev) + 1) if prev else h2[0] + 2
    ADD.setdefault(idx, []).append(mkrow(t))
for idx in sorted(ADD, reverse=True):
    L2[idx:idx] = ADD[idx]
assert sum(len(v) for v in ADD.values()) == NLROWS
t2n = [i for i in range(h2[0], len(L2)) if L2[i].startswith(u'| **合计（')]
assert len(t2n) == 1
LAB = [L2[i].split(u'|')[1].strip() for i in range(h2[0] + 2, t2n[0])]
NUM1 = [int(x[1:]) for x in LAB]
INV1 = [(a, b) for a, b in zip(NUM1, NUM1[1:]) if b < a]
assert INV1 == [(26, 23)], INV1
assert set(LAB) == set(ROWS) and len(LAB) == len(ROWS), (len(LAB), len(ROWS))
HC = len(L2[h2[0]].split(u'|'))
for t in UNACC:
    row = [l for l in L2 if l.startswith(u'| %s | %s |' % (t, fmt(EN[t])))]
    assert len(row) == 1, t
    assert len(row[0].split(u'|')) == HC, (t, len(row[0].split(u'|')), HC)

# ---------- 合计行: 两列 ⇎ 保留率 ⇎ 唯一码点四格改为与 ALL 行相符 ----------
ADDE, ADDG = sum(EN[t] for t in UNACC), sum(DG[t] for t in UNACC)
cells = L2[t2n[0]].split(u'|')
assert len(cells) == HC, (len(cells), HC)
OLDN = num(cells[1])
assert OLDN == len(LISTED), (OLDN, len(LISTED))
cells[1] = u' **合计（%d 条）** ' % len(LAB)
cells[2] = u' **%s** ' % fmt(TOT_E)
cells[3] = (u' **%s**（摘要段合计 %s，本遍补记的 %d 枚为 %s 编码／%s 摘要；本表所列 %d 条与 audit 的 %d 行一一对齐，'
             u'两列合计 ⇎ 保留率 ⇎ 唯一码点四格逐格等于 audit 的 ALL 行——前一遍那句“故不取 audit 的 ALL 行”是因为表里'
             u'缺这 %d 行，本遍补全后它失效，故改为“与 ALL 行相符”；唯一码点那格由本遍按 audit 的编码区正则逐条现数'
             u'取并集（拼接后去重，非各条之和），%d 条逐条与 audit 现算值对拍） '
             % (ALLR[3].strip(u'*'), fmt(TOT_D), NLROWS, fmt(ADDE), fmt(ADDG), len(LAB), len(ROWS), NLROWS, len(LAB)))
cells[5] = u' **%s** ' % fmt(len(UNI))
L2[t2n[0]] = u'|'.join(cells)
assert len(L2[t2n[0]].split(u'|')) == HC
assert cells[3].count(u'（') == cells[3].count(u'）'), (cells[3].count(u'（'), cells[3].count(u'）'))

# ---------- 机械行注 ----------
NOTE = [i for i, l in enumerate(L2) if l.startswith(u'（B54 起的 ')]
assert len(NOTE) == 1, NOTE
m0 = re.match(u'（B54 起的 (\\d+) 行是按', L2[NOTE[0]])
assert m0, L2[NOTE[0]][:40]
MECH = len([x for x in LAB if int(x[1:]) >= 54])
assert MECH == int(m0.group(1)) + NLROWS == 31, (MECH, m0.group(1))
L2[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与'
               u'字符/语义单元五格, 不重写各条的口径注; 本遍再直补 %s 共 %d 枚, 至此本表 %d 行与 audit 的 %d 行'
               u'一一对齐, 合计行的两列 ⇎ 保留率 ⇎ 唯一码点四格逐格相符于 ALL 行。）'
               % (MECH, u'⇎'.join(u'B%d' % x for x in UNACC_IDS), NLROWS, len(LAB), len(ROWS)))
assert L2[NOTE[0]].count(u'（') == L2[NOTE[0]].count(u'）')

# ---------- 第 9 行的条数陈述 ----------
HD = [i for i, l in enumerate(L2) if u'实际转化集，共 **' in l]
assert len(HD) == 1, HD
i0 = L2[HD[0]].index(u'共 **')
j = L2[HD[0]].index(u'，分两代。')
SEG = L2[HD[0]][i0:j]
assert SEG.count(u'（') == SEG.count(u'）') == 2, SEG[-40:]
assert u'%d 条' % len(ROWS) in SEG.split(u'（')[0], SEG[:20]
NSEG = (u'共 **%d 条**（`babeltele/B01..B65、B67..B85`, 本遍把已接线而未进转化指标表的 %s 共 %d 条各补一行 '
        u'`audit.py` 直出的机械行, 合计行随之按本表所列 %d 条现算 ⇎ 与 audit 的 %d 行一一对齐, 唯一码点逐条现数'
        u'（这 %d 条的门槛表⇎语料表两行前几遍已记, 本遍不重记其记账数））'
        % (len(ROWS), u'／'.join(u'B%d' % x for x in UNACC_IDS), NLROWS, len(LAB), len(ROWS), NLROWS))
assert NSEG.count(u'（') == NSEG.count(u'）') == 2, NSEG
L2[HD[0]] = L2[HD[0]][:i0] + NSEG + L2[HD[0]][j:]
_line = L2[HD[0]]
assert _line.count(u'（') == _line.count(u'）'), _line[-90:]
assert _line.count(u'**%d 条**' % len(ROWS)) == 1

# ---------- 保真门槛标题 ⇎ 推导数两处: 现算对拍 ----------
GT = [i for i, l in enumerate(L2) if l.startswith(u'## 保真门槛：')]
assert len(GT) == 1
assert u'**PASS**（%d 条）' % len(ROWS) in L2[GT[0]], L2[GT[0]]
PD = [i for i, l in enumerate(L2) if u'条**推导全部通过' in l]
assert len(PD) == 1, PD
assert u'已机检的推导 %d 条' % PROOFS in L2[PD[0]], (PROOFS, L2[PD[0]][:120])
assert u'**%d 条语料／%d 条**' % (len(ROWS), PROOFS) in L2[PD[0]], L2[PD[0]][:120]
assert u'行集与文件数相符 %d ⇎ %d' % (len(ROWS), len(FILES)) in L2[PD[0]], L2[PD[0]][:160]

# ---------- 命令块: 只登记本遍这一枚新脚本 ----------
CMD = [i for i, l in enumerate(L2) if l.startswith(u'python -X utf8 corpus/_readme53.py')]
assert len(CMD) == 1, CMD
assert u'_readme_metrics9' not in S
L2[CMD[0]:CMD[0]] = [u'python -X utf8 corpus/_readme_metrics9.py       # 全库补记: 真跑 audit 后把未进转化指标表的 %d 条'
                     u'各补一行直出机械行, 合计行从 %d 条推到 %d 条; 编码区逐条现数（%d 条逐条与 audit 对拍）取并集=%s,'
                     u' 两列合计 ⇎ 保留率 ⇎ 并集四格逐格相符于 ALL 行'
                     % (NLROWS, OLDN, len(LAB), len(LAB), fmt(len(UNI)))]

NEW = NL.join(L2)
assert NEW.count(u'| B82 | ') == 3 and NEW.count(u'## 转化指标') == 1
assert len(NEW.split(NL)) == len(L2)
assert NEW != S

io.open(u'corpus/README.md.tmp9', u'w', encoding=u'utf-8', newline=NL).write(NEW)
json.dump(dict(added=[u'B%d' % x for x in UNACC_IDS], added_n=NLROWS, added_enc=ADDE, added_dig=ADDG,
               listed_before=LISTED, listed_after=LAB, listed_n=len(LAB), audit_rows=len(ROWS), files=len(FILES),
               enc=TOT_E, dig=TOT_D, retention=ALLR[3], uniq=len(UNI), all_enc=ALLR[2], all_dig=ALLR[1],
               all_uniq=ALLR[5], proofs=PROOFS, gate=GATE_PASS, inversion=INV1, mech_rows=MECH,
               per_row_checks=len(LAB) * 2, delta_chars=len(NEW) - len(S)),
          io.open(u'corpus/_metrics9readme.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)
os.replace(u'corpus/README.md.tmp9', u'corpus/README.md')
print(u'全库补记完成: 转化指标表 %d 行 → %d 行（补 %s） ｜ 合计 %s 编码 ⇎ %s 摘要 ⇎ %s ⇎ 唯一码点(并集) %s ｜ '
      u'与 ALL 行四格相符（%s ⇎ %s ⇎ %s ⇎ %s） ｜ 本遍逐条对拍 %d 条×2 格 ｜ audit 行 %d ⇎ 文件 %d ⇎ 推导 %d 条 ｜ '
      u'总判 %s ｜ 倒挂对 %s ｜ 机械行注改口: B54 起 %d 行 ｜ 净变化 %+d 字符'
      % (len(LISTED), len(LAB), u'⇎'.join(u'B%d' % x for x in UNACC_IDS), fmt(TOT_E), fmt(TOT_D), ALLR[3],
         fmt(len(UNI)), ALLR[2], ALLR[1], ALLR[3], ALLR[5], len(LAB), len(ROWS), len(FILES), PROOFS,
         u'PASS' if GATE_PASS else u'FAIL', INV1, MECH, len(NEW) - len(S)))
