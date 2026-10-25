# -*- coding: utf-8 -*-
"""B50 ⛓解读注: 只写工具侧现算的数, 每个数都由本脚本重新测一遍并 assert, 不手填。
落盘 corpus/_b50audit.json(审计器侧 _B50 字典) 作为两套实现的互检快照。"""
import ast, io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B50_one_model_six_domains.md')
M = json.load(io.open(os.path.join(C, u'_b50meas.json'), encoding='utf-8'))
CH = json.load(io.open(os.path.join(C, u'_b50checks.json'), encoding='utf-8'))
DJ = json.load(io.open(os.path.join(C, u'_deriv50.json'), encoding='utf-8'))
ATOMS = [x for x in io.open(os.path.join(C, u'_atoms50.txt'), encoding='utf-8').read().split(NL) if x.strip()]
RAWS = M[u'slugs'] and [u'corpus/raw/cot/%s.md' % s for s in M[u'slugs']]
TAGS = M[u'tags']

# ---------- 快照: 从审计器里取它自己算的那份 _B50 ----------
SNAP = os.path.join(C, u'_b50audit.json')
code = (u"import sys,json;sys.path.insert(0,'corpus');import audit;"
        u"json.dump(audit._B50, open(sys.argv[1],'w',encoding='utf-8'), ensure_ascii=False)")
r = subprocess.run([sys.executable, '-X', 'utf8', '-c', code, SNAP],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-600:]
AT_ = r.stdout
A = json.load(io.open(SNAP, encoding='utf-8'))

# 两套实现的可比键(采集侧平铺 ⇎ 审计器侧 _B50)
CMP = [u'rcot', u'acot', u'pcot', u'praw', u'fchars', u'fbytes', u'sent', u'para', u'numsent',
       u'gap', u'pgap', u'wait', u'actually', u'maybe', u'prob', u'assume', u'unsure', u'verif',
       u'redo', u'wrong', u'therefore', u'however', u'must', u'caveat', u'final', u'quote',
       u'equality', u'unit', u'cfr', u'study', u'restart_word', u'uncertain_word', u'bold',
       u'hmm', u'lets', u'letme', u'arrow', u'flip', u'allpos', u'sixzero', u'npats', u'nsrc',
       u'models', u'model_bare', u'hashes', u'sha_ok', u'retr', u'tailbad', u'rcotsum',
       u'rcratio', u'anchor_total', u'anchor_distinct', u'cross', u'checks']
# 采集侧把 flip/allpos/sixzero 存成模式名列表, 审计器侧存成条数: 统一成"条数"再比
ASLIST = (u'flip', u'allpos', u'sixzero', u'models')
CV = lambda k, side: (len(side[k]) if k in ASLIST and isinstance(side[k], list) else side[k])
have = [k for k in CMP if k in M and k in A]
aslist_ = lambda v: v if isinstance(v, list) else [v]
rnd = lambda v: [round(float(x), 1) for x in aslist_(v)]
diff = [k for k in have if rnd(CV(k, M)) != rnd(CV(k, A))]
assert len(have) == len(CMP), [k for k in CMP if k not in have or k not in A]
assert not diff, [(k, CV(k, M), CV(k, A)) for k in diff]
BOTH = len(have)
VALS = sum(len(aslist_(CV(k, M))) for k in have)

# ---------- 锚的三种命中口径 ----------
def norm_strict(s):
    return re.sub(r'\s+', ' ', s).strip()

SRCT = [re.sub(r'\s+', ' ', io.open(p, encoding='utf-8', errors='replace').read()) for p in RAWS]


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


PNR = [pn(io.open(p, encoding='utf-8', errors='replace').read()) for p in RAWS]


def owner(i):
    """该锚在 _b50meas 的 atomlist 里挂在哪个标签下(注册时的唯一归属)。"""
    a = ATOMS[i]
    for t, lst in M[u'atomlist'].items():
        if a in lst:
            return t
    return None


exact = sum(1 for i, a in enumerate(ATOMS) if a in io.open(RAWS[TAGS.index(owner(i))], encoding='utf-8', errors='replace').read())
folded = sum(1 for i, a in enumerate(ATOMS) if norm_strict(a) in SRCT[TAGS.index(owner(i))])
normed = sum(1 for i, a in enumerate(ATOMS) if pn(a) in pn(io.open(RAWS[TAGS.index(owner(i))], encoding='utf-8', errors='replace').read()))
assert normed == len(ATOMS), normed
MULTI = sum(1 for a in ATOMS if sum(1 for j in range(6) if pn(a) in PNR[j]) > 1)
assert MULTI == 0 and folded == len(ATOMS)

# ---------- 门槛(同一份子进程输出) ----------
GATE = re.search(u'保真门槛\\(T1 字面 \\+ T2 推导 \\+ T3 码位\\): (PASS|FAIL)', AT_)
ROWS = len(re.findall(u'^\\| B\\d+ \\|', AT_, re.M))
HINTS = int(re.search(u'提示\\(不计入 FAIL[^)]*\\): 共 (\\d+) 个', AT_).group(1))
B50ROW = [l for l in AT_.split(NL) if l.startswith(u'| B50 ')][0].split(u'|')
MISMATCH = [x.strip() for x in B50ROW[9:13]]
assert GATE and GATE.group(1) == 'PASS' and all(x == '0' for x in MISMATCH), (GATE.group(0) if GATE else None, MISMATCH)
PROOFS = len(re.findall(u'^  ✓ .*B50V\\(', AT_, re.M))
assert PROOFS == len(DJ), (PROOFS, len(DJ))
# DERIV 总键数(含以名单为键的那几枚)与数值键数: 注里要把 99 和 README 的 104 对上
_A = io.open(u'corpus/audit.py', encoding='utf-8').read()
_st = _A.index(u"DERIV['B50'] = "); _en = _A.index(u"\nDERIV['", _st + 10)
_B50D = ast.literal_eval(_A[_A.index(u'{', _st):_en].strip().rstrip(u','))
NLK = len([k for k in _B50D if k.startswith(u'[')])
NTOT = len(_B50D)
assert NTOT - NLK == len(DJ) == PROOFS and NLK == 5, (NTOT, NLK, len(DJ), PROOFS)

# ---------- 摘要段 ----------
T = io.open(ENTRY, encoding='utf-8').read()
DIG = re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', T, re.S).group(1)
ENC = re.search(u'## ⟪BabelTele⟫\\n(.*?)\\n\\n## ⛓解读注', T, re.S).group(1)
BLOCKS = len(re.findall(u'### ⟦', DIG))
assert BLOCKS == 6, BLOCKS
DL, EL = len(DIG.replace(NL, u'')), len(ENC.replace(NL, u''))
DW = len(DIG)
assert DW - DL == DIG.count(NL), (DW, DL)

# ---------- DERIV 结构 ----------
ZT = len(DJ[u'0'].split(u'+'))
KEYS = len(DJ)
COLL = CH[u'collisions']
NC = len(COLL)
NOTES = CH[u'notes']
SINGLE = [k for k in sorted(COLL) if len(COLL[k]) > 1]
if exact == folded == normed == len(ATOMS):
    TAIL = (u'三口径在这批上完全重合: 门槛按③判, 但①②也无缺口——六段的锚都落在原文自己的字形上, '
            u'没有靠归一才救回来的引号或连接号。留着三口径是为了换一批抓取时能立刻量出字形问题的条数。')
else:
    TAIL = (u'门槛按③判: ①比③少 %d 条、②比③少 %d 条, 差额来自原文混用的同形异码引号与连接号(不写口径就会把这类锚判成失配)。'
            % (normed - exact, normed - folded))

NOTE = u'''\
## ⛓解读注

**这套数是怎么来的**: 六道题的同一次批量抓取(抓取器 `corpus/fetch_cot.py`, 模型 `opencode/deepseek-v4.1-flash-free`, 抓取时刻 %d 组)。
每条数都由两套独立实现的脚本各算一遍再对齐: 采集侧 `corpus/_pick50.py` ⇎ 审计器侧 `corpus/audit.py::_b50_scan()`。
本注写这行时又比对了一次: 可比键 %d 个、键内数值 %d 枚, 全部相等(快照 `corpus/_b50audit.json`)。
审计器另算另证的推导键 %d 枚(README 表里写的 DERIV %d 键是同一个字典的总键数, 多出的 %d 枚以名单本身为键, 机检逐条打勾的是这 %d 枚数值键), 其中 `%s` 一枚键折 %d 个零项: 六源皆零的 redo 类、跨源命中数、以及各段为零的等号/条款词/粗体/箭头/明说不确定/restart/uncertain/let me/结论标记/回答区。

**锚的三口径**(注册 %d 条 ⇎ 正文引用 %d 处、去重 %d 串、未引用 %d 条, 每标签 %s):
① 完全逐字(连空格与引号字形都不动)命中其标注那一段的 %d/%d 条;
② 只折叠空白(把连续空白压成一格)后命中 %d/%d 条;
③ 再加撇号/引号剔除、连接号归一与大小写归一(即 `atomcheck.py`/`audit.py` 的 `prose_norm`)后 %d/%d 条。%s
互斥性按③复核: %d 条锚 × 6 段 = %d 次成员检查, 命中数≠1 的 %d 条(即没有任何原子在别的段里也能逐字找到)。

**digest 侧**: 六段各出一节(`### ⟦标签⟧ ⟸ 文件`), 共 %d 节。摘要段含换行 %d 字符(审计表“摘要段”一栏取的就是这个数), 去掉换行 %d; 编码区不含换行 %d。于是“vs 摘要段”按表口径是 %s ⇎ 按“两侧都去换行”是 %s——两栏之差只是 %d 枚换行的归属, 在此两个数都登记, 免得读作两套不同的量。这条编码比窗口长, 因为要表达的是六格矩阵的形状(哪几格为零)而不是摘录句子。

**同一数的不同含义**(同值冲突 %d 组, DERIV 一个值只留一枚键, 所以这些说法必须靠注里的上下文区分): %s

**跑法**: `python -X utf8 corpus/audit.py` ⇒ B50 行 T1/T2 编码失配 %s ⇎ 原文失配 %s ⇎ T3 码位 %s ⇎ 小整数待核 %s; 门槛 %s, 全库 %d 条, 软提示 %d 枚未增长, 本条被点名的推导 %d 枚全部成立。
`python -X utf8 corpus/atomcheck.py B50 corpus/_atoms50.txt` ⇒ ok=%d bad=0。
''' % (
    M[u'retr'], BOTH, VALS, KEYS, NTOT, NLK, KEYS, u'0', ZT,
    CH[u'anchor_total'], CH[u'used'], CH[u'distinct'], CH[u'uncited'],
    u' '.join(u'%s:%d' % (t, CH[u'tag_counts'][t]) for t in TAGS),
    exact, len(ATOMS), folded, len(ATOMS), normed, len(ATOMS), TAIL,
    len(ATOMS), len(ATOMS) * 6, M[u'cross'],
    BLOCKS, DW, DL, EL, u'%.1f%%' % (100.0 * EL / DW), u'%.1f%%' % (100.0 * EL / DL), DW - DL,
    NC, u'；'.join(u'%s=%s' % (k, u'、'.join(COLL[k])) for k in SINGLE),
    *MISMATCH, GATE.group(1), ROWS, HINTS, PROOFS, len(ATOMS))

# 门槛自检: 注里不许出现未测的占位
assert u'{' not in NOTE.replace(u'⟪', u'') and u'%d' not in NOTE and u'%s' not in NOTE and u'%.1f' not in NOTE
head = T[:T.index(u'## ⛓解读注')]
tail = T[T.index(u'## ⛓解读注'):]
endmark = u'\n\n## '
cut = tail.find(endmark, 1)
assert tail.startswith(u'## ⛓解读注')
rest = tail[cut + 1:] if cut >= 0 else u''
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(head + NOTE.rstrip(NL) + rest)
print(u'注已写: 可比键 %d/%d 值 %d ｜ 锚 逐字 %d ⇎ 折空白 %d ⇎ 归一 %d ／%d ｜ digest %d 节 %d 字符 ⇎ 编码 %d 字符(%.1f%%) ｜ DERIV %d 键(0 折 %d) 冲突 %d 组' % (
    BOTH, len(CMP), VALS, exact, folded, normed, len(ATOMS), BLOCKS, DL, EL, 100.0 * EL / DL, KEYS, ZT, NC))
