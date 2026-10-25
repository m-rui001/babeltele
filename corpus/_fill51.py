# -*- coding: utf-8 -*-
"""B51 ⛓解读注: 只写工具侧现算的数, 每个数都由本脚本重新测一遍并 assert, 不手填。
三套实现互检: 采集侧 corpus/_pick51.py ⇎ 建条目侧 corpus/_mkB51.py ⇎ 审计器侧 corpus/audit.py::_b51_scan(),
后者的快照落盘 corpus/_b51audit.json。字符层(difflib)的量由 corpus/_probe51.py 侧测, 落盘 corpus/_probe51_ab.txt ⇎ _cd.txt。"""
import ast, io, json, os, re, subprocess, sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B51_same_model_same_question_twice.md')
M = json.load(io.open(os.path.join(C, u'_b51meas.json'), encoding='utf-8'))
CH = json.load(io.open(os.path.join(C, u'_b51checks.json'), encoding='utf-8'))
DJ = json.load(io.open(os.path.join(C, u'_deriv51.json'), encoding='utf-8'))
ATOMS = [x for x in io.open(os.path.join(C, u'_atoms51.txt'), encoding='utf-8').read().split(NL) if x.strip()]
MEAS, SHAPE = dict(M[u'meas']), dict(M[u'shape'])
MEAS.update(SHAPE)
TAGS = M[u'tags']
RAWS = [u'corpus/raw/cot/%s.md' % s for s in M[u'slugs']]
ORDER = [(0, 1), (2, 3), (0, 2), (0, 3), (1, 2), (1, 3)]
SAME = [(0, 1), (2, 3)]

# ---------- 快照: 从审计器里取它自己算的那份 _B51 ----------
SNAP = os.path.join(C, u'_b51audit.json')
code = (u"import sys,json;sys.path.insert(0,'corpus');import audit;"
        u"json.dump(audit._B51, open(sys.argv[1],'w',encoding='utf-8'), ensure_ascii=False)")
r = subprocess.run([sys.executable, '-X', 'utf8', '-c', code, SNAP],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-600:]
AT_ = r.stdout
A = json.load(io.open(SNAP, encoding='utf-8'))

# ---------- 两套实现的可比键 ----------
LISTK = [u'rcot', u'acot', u'pcot', u'praw', u'fchars', u'fbytes', u'sent', u'lsent', u'usent',
         u'shang', u'para', u'numsent', u'digit', u'word', u'gap', u'pgap', u'rgap']
PATK = [u'wait', u'actually', u'maybe', u'prob', u'assume', u'unsure', u'verif', u'redo', u'wrong',
        u'therefore', u'however', u'must', u'caveat', u'final', u'equality', u'arrow', u'letme',
        u'lets', u'hmm', u'need', u'q', u'bold']
SCALK = [u'sha_kinds', u'sha_ok', u'models', u'model_bare', u'retr', u'tailbad', u'rcratio',
         u'sent_all4', u'lsent_all4', u's4_same', u'npats', u'allzero']
PAIRK = {u'ov_l': 0, u'ov_s': 1, u'ov_ls': 2, u'ov_sg': 3}
SUBK = {u'sub_n': 0, u'sub_tot': 1, u'sub_max': 2, u'sub_prompt': 3}
ANCHK = [u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_pair', u'anchor_cross',
         u'anchor_single', u'anchor_all4', u'checks']
aslist_ = lambda v: v if isinstance(v, list) else [v]
rnd = lambda v: [round(float(x), 2) for x in aslist_(v)]
CMP, DIFF = [], []
for k in LISTK + PATK:
    CMP.append((k, MEAS[k], A[k]))
MEAS[u'npats'] = len(PATK)
MEAS[u'allzero'] = len([k for k in PATK if max(MEAS[k]) == 0])
for k in SCALK:
    CMP.append((k, MEAS[k], A[k]))
CMP.append((u'rcotsum', sum(MEAS[u'rcot']), A[u'rcotsum']))
CMP.append((u'nsrc', len(RAWS), A[u'nsrc']))
CMP.append((u'lastcode', [ord(x) for x in SHAPE[u'lastc']], A[u'lastcode']))
for k, slot in PAIRK.items():
    CMP.append((k, [M[u'pairs'][u'%d%d' % p][slot] for p in ORDER], A[k]))
for k, slot in SUBK.items():
    CMP.append((k, [MEAS[u'sub'][u'AB' if i == 0 else u'CD'][slot] for i in range(2)], A[k]))
CMP.append((u'pq', [x[0] for x in M[u'prompt_quote']], A[u'pq']))
CMP.append((u'pqpos', [x[1] for x in M[u'prompt_quote']], A[u'pqpos']))
for k in ANCHK:
    CMP.append((k, CH[u'ameta'][k], A[k]))
for k, x, y in CMP:
    if rnd(x) != rnd(y):
        DIFF.append((k, x, y))
assert not DIFF, DIFF
BOTH = len(CMP)
VALS = sum(len(aslist_(x)) for _, x, _ in CMP)

# ---------- 锚: 归属由正文现推, 命中按三口径各测一遍 ----------
T = io.open(ENTRY, encoding='utf-8').read()
ENC = re.search(u'## ⟪BabelTele⟫\\n(.*?)\\n\\n## ⛓解读注', T, re.S).group(1)
DIG = re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', T, re.S).group(1)
CITES = re.findall(u'⟦([ABCD])⟧⟨([^⟨⟩]+)⟩', ENC)
assert len(CITES) == CH[u'anchor_total'], (len(CITES), CH[u'anchor_total'])

def norm_strict(s):
    return re.sub(r'\s+', ' ', s).strip()

def pn(s):
    out = []
    for ch in s:
        t = ch.lower()
        for a, b in ((u'’', "'"), (u'‘', "'"), (u'“', '"'), (u'”', '"'), (u'´', '')):
            t = t.replace(a, b)
        t = t.replace('"', '').replace("'", '')
        for d in u'‐‑‒–—―−':
            t = t.replace(d, '-')
        for x in t:
            k = x if ((x.isalnum() and x.isascii()) or u'一' <= x <= u'鿿' or x in ' -.') else ' '
            if k != ' ' or (out and out[-1][0] != ' '):
                out.append((k, 0))
    return u''.join(c for c, _ in out)

FULLT = [io.open(p, encoding='utf-8', errors='replace').read() for p in RAWS]
SRCT = [norm_strict(x) for x in FULLT]
PNR = [pn(x) for x in FULLT]
DIS = []          # 正文里的去重锚串(跨标签去重)
for _, a in CITES:
    if a not in DIS:
        DIS.append(a)
own = dict((t, []) for t in TAGS)
for tg, a in CITES:
    if a not in own[tg]:
        own[tg].append(a)
ALLA = [a for t in TAGS for a in own[t]]
exact = sum(1 for t in TAGS for a in own[t] if a in FULLT[TAGS.index(t)])
folded = sum(1 for t in TAGS for a in own[t] if norm_strict(a) in SRCT[TAGS.index(t)])
normed = sum(1 for t in TAGS for a in own[t] if pn(a) in PNR[TAGS.index(t)])
assert normed == len(ALLA), (normed, len(ALLA))
HC = [(a, sum(1 for i in range(4) if pn(a) in PNR[i])) for a in ALLA]
DTHIT = [len([1 for _, h in HC if h == k]) for k in (1, 2, 3, 4)]
assert sum(DTHIT) == len(ALLA) and DTHIT[2] == 0, DTHIT
assert DTHIT[0] == CH[u'ameta'][u'anchor_single'] and DTHIT[1] == CH[u'ameta'][u'anchor_pair'] + CH[u'ameta'][u'anchor_cross'] and DTHIT[3] == CH[u'ameta'][u'anchor_all4'], (DTHIT, CH[u'ameta'])
if exact == folded == normed == len(ALLA):
    TAIL = (u'三口径在这批上完全重合: 门槛按③判, 但①②也无缺口——四段的锚都落在原文自己的字形上, '
            u'没有靠归一才救回来的引号或连接号。留着三口径是为了换一批抓取时能立刻量出字形问题的条数。')
else:
    TAIL = (u'门槛按③判: ①比③少 %d 条、②比③少 %d 条, 差额来自原文混用的同形异码引号与连接号(不写口径就会把这类锚判成失配)。'
            % (normed - exact, normed - folded))

# ---------- 门槛(同一份子进程输出) ----------
GATE = re.search(u'保真门槛\\(T1 字面 \\+ T2 推导 \\+ T3 码位\\): (PASS|FAIL)', AT_)
ROWS = len(re.findall(u'^\\| B\\d+ \\|', AT_, re.M))
HINTS = int(re.search(u'提示\\(不计入 FAIL[^)]*\\): 共 (\\d+) 个', AT_).group(1))
B51ROW = [l for l in AT_.split(NL) if l.startswith(u'| B51 ')][0].split(u'|')
MISMATCH = [x.strip() for x in B51ROW[9:13]]
assert GATE and GATE.group(1) == 'PASS' and all(x == '0' for x in MISMATCH), (GATE.group(0) if GATE else None, MISMATCH)
PROOFS = len(re.findall(u'^  ✓ .*B51V'+chr(92)+u'(', AT_, re.M))
UNREF = len(DJ) - PROOFS
assert PROOFS > 0 and not re.search(u'✗.*B51V'+chr(92)+u'(', AT_), (PROOFS, len(DJ))

_A = io.open(u'corpus/audit.py', encoding='utf-8').read()
_st = _A.index(u"DERIV['B51'] = ")
_en = _A.index(u"\nDERIV['", _st + 10)
_D = ast.literal_eval(_A[_A.index(u'{', _st):_en].strip().rstrip(u','))
NTOT = len(_D)
NLK = len([k for k in _D if k.startswith(u'[')])
assert NTOT == NLK + len(DJ), (NTOT, NLK, len(DJ))

# ---------- 抓取时刻 ⇎ 两次之间的间隔 ----------
RT = [x for x in MEAS[u'retr_list']]
DT = [datetime.strptime(x, '%Y-%m-%dT%H:%M:%S') for x in RT]
GAP_H = [round((DT[1] - DT[0]).total_seconds() / 3600.0, 2), round((DT[3] - DT[2]).total_seconds() / 3600.0, 2)]
assert len(set(x[:10] for x in RT)) == 2

# ---------- 字符层(difflib)由 _probe51.py 侧量 ----------
PB = {}
for nm, f in ((u'AB', u'_probe51_ab.txt'), (u'CD', u'_probe51_cd.txt')):
    s = io.open(os.path.join(C, f), encoding='utf-8').read()
    cm = re.search(u'字符层: 逐字命中共 (\\d+) 字符 \\(占A ([\\d.]+)% ⇎ SequenceMatcher ratio ([.\\d]+)\\), 最长连续 (\\d+) 字符', s)
    sp = re.search(u'复现拆解\\(块>=8 字, 共 (\\d+) 块 (\\d+) 字符\\): 题面回声 (\\d+) \\([\\d.]+%\\) ⇎ 推理复用 (\\d+) \\([\\d.]+%\\)', s)
    assert cm and sp, (nm, s[-400:])
    PB[nm] = dict(char=int(cm.group(1)), pct=float(cm.group(2)), ratio=float(cm.group(3)),
                 lcs=int(cm.group(4)), blocks=int(sp.group(1)), tot=int(sp.group(2)),
                 echo=int(sp.group(3)), reuse=int(sp.group(4)))
    assert PB[nm][u'echo'] + PB[nm][u'reuse'] == PB[nm][u'tot'] and PB[nm][u'tot'] <= PB[nm][u'char'], PB[nm]

ZT = len(DJ[u'0'].split(u'+'))
KEYS = len(DJ)
COLL = CH[u'collisions']
NC = len(COLL)
SINGLE = [k for k in sorted(COLL) if len(COLL[k]) > 1]
BLK = len(re.findall(u'### ⟦', DIG))
assert BLK == 4, BLK
DW, DL = len(DIG), len(DIG.replace(NL, u''))
EL = len(ENC.replace(NL, u''))
assert DW - DL == DIG.count(NL)
assert EL == CH[u'enc_chars'], (EL, CH[u'enc_chars'])
RAW4 = sum(MEAS[u'rcot'])

NOTE = u'''\
## ⛓解读注

**这套数是怎么来的**: 两道题各采两次(同一模型、同一抓取器 `corpus/fetch_cot.py`): 数论题 `math_subsets.md` ⇎ `math_subsets_s2.md`, 肾病题 `med_gitalb.md` ⇎ `med_gitalb_s2.md`; 题面 sha 只有 %d 种(各自校验 %d/4), 抓取跨 %d 个日子——第一次在 %s, 第二次在 %s 与 %s, 同题两次之间隔 %s 与 %s 小时。
每条数由三套独立实现各算一遍再对齐: 采集侧 `corpus/_pick51.py` ⇎ 建条目侧 `corpus/_mkB51.py` ⇎ 审计器侧 `corpus/audit.py::_b51_scan()`。
本注写这行时又比对了一次: 可比键 %d 个、键内数值 %d 枚(四段长度、四种粒度集合交、公共片段四格、题面引用长度与起点、%d 族词法计数、末字符码位、锚统计), 三边全部相等(快照 `corpus/_b51audit.json`)。
审计器另算另证的推导键 %d 枚, 其中 `%s` 一枚折 %d 个零项: 四份皆零的 let me 与 redo 两族、跨题对归零的行/五词串交集、以及各段为零的回答区/结论标记/粗体/犹豫/明说不确定/必须/假设/推翻; 锚归属错配也在这枚键里(实测 0)。

**锚的三口径**(正文引用 %d 处 ⇎ 去重 %d 串 ⇎ 注册 %d 条, 每标签 %s):
① 完全逐字(连空格与引号字形都不动)命中其标注那一段的 %d/%d 条;
② 只折叠空白后命中 %d/%d 条;
③ 再加撇号/引号剔除、连接号归一与大小写归一(即 `audit.py` 的 `prose_norm`)后 %d/%d 条。%s
命中列分布(按③对四份源逐一判成员, 共 %d 次检查): 恰命中 1 份 %d 条 ⇎ 恰命中 2 份 %d 条(同题对 %d ⇎ 跨题 %d)⇎ 恰命中 3 份 %d 条 ⇎ 四份皆命中 %d 条; 错配 %d 条。
“恰命中 3 份 = 0”不是巧合而是构造约束: 一截文字若同时出现在同题两次采样里, 它就与第三道题无关。

**三档可核性**: 第一档进门槛(`_b51_scan` 秒级复算)——块层用 >=40 字极大公共片段滑窗(同题对 %d ⇎ %d 块, 合计 %d ⇎ %d 字), 句子层与词组层用集合交。第二档由集合运算得出(名次随分母翻转的每万字口径)。第三档只能靠工具侧整段对齐: `difflib.SequenceMatcher(autojunk=False)` 在 %d 字 × %d 字上量得逐字命中 %d 字符(占前一份 %.1f%%, ratio %.3f, 最长连续 %d 字), 肾病对 %d 字符(%.1f%%, ratio %.3f, 最长 %d 字); 拆成两档后, 数论对 %d 块 %d 字符里题面回声 %d ⇎ 推理复用 %d, 肾病对 %d 块 %d 字符里回声 %d ⇎ 复用 %d。这一档慢到不能进门槛(分钟级), 所以只在 `corpus/_probe51.py` 里量并如实注明——条目正文里凡是“复现了多少字符”的说法都改写成块层可复算的数, 而不是这个比例。

**digest 侧**: 四段各出一节(`### ⟦标签⟧ ⟸ 文件`), 共 %d 节。摘要段含换行 %d 字符(审计表“摘要段”一栏取的就是这个数), 去掉换行 %d; 编码区不含换行 %d。于是“vs 摘要段”按表口径是 %.1f%% ⇎ 按“两侧都去换行”是 %.1f%%——两栏之差只是 %d 枚换行的归属, 两个数在此都登记。这条的编码/原文整段比是 %.2f%%: 四段推理区合计 %d 字符, 摘要只能取锚点触到的窗口, 而本条的锚特意选了长片段(题面引用一枚就 %d/%d/%d/%d 字符), 因为它们要被同题两份源同时命中才算数。真正的结论不住在窗口里——“同题对的句子级共有不比跨题对高”“纯题面块数与总块数之比”“犹豫计数同向膨胀而 redo 恒零”都是四格矩阵上的形状, 要整段复算才看得见。

**同一数的不同含义**(同值冲突 %d 组, DERIV 一个值只留一枚键, 所以这些说法必须靠注里的上下文区分): %s
最扎眼的一组是题面长度: 同一道题两次采样的题面字符数相同(%d ⇎ %d), 于是“推理区长度”“题面长度”“词法计数”在同值键上会互相顶掉——这也是本条把每种口径都单独登记成 B51V 表达式而不是只写数字的原因。

**跑法**: `python -X utf8 corpus/audit.py` ⇒ B51 行 T1/T2 编码失配 %s ⇎ 原文失配 %s ⇎ T3 码位 %s ⇎ 小整数待核 %s; 门槛 %s, 全库 %d 条, 软提示 %d 枚未增长, 本条被点名的推导 %d 枚全部成立(另 %d 枚登记在同值折等里、正文没有把它们写成独立数字, 但 `_b51_scan` 照样复算它们)。
`python -X utf8 corpus/atomcheck.py B51 corpus/_atoms51.txt` ⇒ ok=%d bad=0。
`python -X utf8 corpus/_wire51.py` 重复运行会先摘旧块再插新块(幂等), 且插门前先把 DERIV 的 %d 条算式在刚写好的扫描器上预演一遍, 值不符就当场停机。
''' % (
    MEAS[u'sha_kinds'], MEAS[u'sha_ok'], MEAS[u'retr'], RT[0], RT[1], RT[3], GAP_H[0], GAP_H[1],
    BOTH, VALS, MEAS[u'npats'], KEYS, u'0', ZT,
    CH[u'anchor_total'], CH[u'anchor_distinct'], len(ATOMS),
    u' '.join(u'%s:%d' % (t, CH[u'tag_counts'][t]) for t in TAGS),
    exact, len(ALLA), folded, len(ALLA), normed, len(ALLA), TAIL,
    CH[u'ameta'][u'checks'], DTHIT[0], DTHIT[1], CH[u'ameta'][u'anchor_pair'], CH[u'ameta'][u'anchor_cross'],
    DTHIT[2], DTHIT[3], CH[u'ameta'][u'anchor_err'],
    A[u'sub_n'][0], A[u'sub_n'][1], A[u'sub_tot'][0], A[u'sub_tot'][1],
    MEAS[u'rcot'][0], MEAS[u'rcot'][1], PB[u'AB'][u'char'], PB[u'AB'][u'pct'], PB[u'AB'][u'ratio'], PB[u'AB'][u'lcs'],
    PB[u'CD'][u'char'], PB[u'CD'][u'pct'], PB[u'CD'][u'ratio'], PB[u'CD'][u'lcs'],
    PB[u'AB'][u'blocks'], PB[u'AB'][u'tot'], PB[u'AB'][u'echo'], PB[u'AB'][u'reuse'],
    PB[u'CD'][u'blocks'], PB[u'CD'][u'tot'], PB[u'CD'][u'echo'], PB[u'CD'][u'reuse'],
    BLK, DW, DL, EL, 100.0 * EL / DW, 100.0 * EL / DL, DW - DL,
    100.0 * EL / RAW4, RAW4, A[u'pq'][0], A[u'pq'][1], A[u'pq'][2], A[u'pq'][3],
    NC, u'；'.join(u'%s=%s' % (k, u'、'.join(COLL[k])) for k in SINGLE),
    MEAS[u'pcot'][0], MEAS[u'pcot'][1],
    *MISMATCH, GATE.group(1), ROWS, HINTS, PROOFS, UNREF, len(ALLA), KEYS)

assert u'%d' not in NOTE and u'%s' not in NOTE and u'%.1f' not in NOTE and u'{' not in NOTE.replace(u'⟪', u'')
head = T[:T.index(u'## ⛓解读注')]
tail = T[T.index(u'## ⛓解读注'):]
cut = tail.find(u'\n\n## ', 1)
assert tail.startswith(u'## ⛓解读注')
rest = tail[cut + 1:] if cut >= 0 else u''
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(head + NOTE.rstrip(NL) + rest)
print(u'注已写: 可比键 %d/%d 值 %d ｜ 锚 逐字 %d ⇎ 折空白 %d ⇎ 归一 %d ／%d ｜ 命中列 %s ｜ difflib AB %d(%.1f%%) CD %d(%.1f%%) ｜ digest %d 节 %d 字符 ⇎ 编码 %d 字符(%.1f%%) ｜ DERIV %d 键(0 折 %d) 冲突 %d 组' % (
    BOTH, len(CMP), VALS, exact, folded, normed, len(ALLA), DTHIT,
    PB[u'AB'][u'char'], PB[u'AB'][u'pct'], PB[u'CD'][u'char'], PB[u'CD'][u'pct'],
    BLK, DL, EL, 100.0 * EL / DL, KEYS, ZT, NC))
