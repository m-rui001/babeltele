# -*- coding: utf-8 -*-
"""B74 的第五遍复测: 与采集侧 _pick74 ⇎ 建条目侧 _mkB74/_mk74emit ⇎ 门槛侧 audit.py::_b74_scan
换算法不换定义, 现算后把 ⛓解读注 写进条目。本遍的独立处:
①行界: 手写索引循环切 '\n'(第二遍 t.split, 采集侧 re.split), 换行枚数用 str.count 而非游标 find;
②折平: ' '.join(s.split())(第二遍是 re.sub('\\s+',' ')); 归一尺另走 re.sub 档, 与 pnorm 逐样本对拍;
③剥标签: 另起三趟字符串扫描(注释趟 ⇎ <br> 趟 ⇎ '<'切档拼合)代第二遍的三条 re.sub,
  整档断言 my_detag == detag(两枚 fill 各一次), 不等即停;
④组面: 自己走一遍“切点只在标签/注释之外”的扫描代第二遍的 tag_groups, 输出逐元组对拍;
⑤行号尺: 偏移映回原行号走 bisect_right(第二遍是线性游标扫描), 段界另用 str.find 定位;
⑥针计数: len(re.findall(re.escape(针), 面)), 重叠档另数 (?=针), 逐行档手写循环代列表解析——三档差合计归零;
⑦语气词: 单词走“按非字母数字切 token 后比对整词”的 token 档, 短语走 finditer 定位后验左右邻是否 alnum
  (第二遍是游标 find + occ_at, 门槛侧又叠了一条负向断言正则) ⇒ tone_re_ledger 由本遍读数对正则档;
⑧Exim 规则串: 时长/数字判定换成一条 fullmatch 正则(第二遍是 tok[:-1].isdigit() + 末字符∈UNIT),
  提示行窗口换成 lower() 包含判定, G 档阶梯换成累加循环;
⑨Postfix 默认值: 换成 finditer(名字+' (default: ')+捕获到 ')' 的一枚(第二遍是游标 find 两跳),
  标签区间尺换成 my_tagspans;
⑩池代数: 归属向量走 Counter(len(v)) 直方图(第二遍是对 pool_all 逐档扫五遍), 配对走集合求交,
  写法分家的 dehyph 换成 re.sub('-\\s+','')(第二遍是逐字符吃);
⑪抬头/年份: 字段行走 startswith+按双空格切, 年份走“月名 token 紧跟四位数字 token”的相邻对档;
⑫引用写法: 'RFC n'/'RFCn'/'RFC-n' 三式全换 findall, 写法族账另用一条正则族的 finditer 计数;
⑬锚归属双轨: 原子串对 ALN 逐行 membership ⇎ 对整篇归一串 substring, 两式同判才计数;
⑭恒等式与 DERIV: 标量式从 _mkB74.py 源码 ast 摘 Z(...) 再 eval, DERIV 207 条复算点从 _deriv74.json
  回读 eval, 不重打一遍算式; 采集侧 51 键对账在本遍重跑。
每个键与 corpus/_b74flat.json 逐值对拍, 值不符或键缺失一律先收集后汇总; 覆盖不足也要如实报数。"""
import io, os, re, sys, json, glob, ast, bisect, itertools
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
ENTRY = u'%s/babeltele/B74_mail_retry_schedule_five_answers.md' % C
PATH = [u'%s/raw/mailRetry/rfc821.txt' % C, u'%s/raw/mailRetry/rfc1123.txt' % C,
        u'%s/raw/mailRetry/rfc5321.txt' % C, u'%s/raw/mailRetry/exim4_retry_spec.html' % C,
        u'%s/raw/mailRetry/postfix_postconf5.html' % C]
LBL = [u'821', u'1123', u'5321', u'exim', u'postfix']
NSRC = 5
ISH = [False, False, False, True, True]
NL = u'\n'
POOLMIN = 40
APOOLMIN = 24
FLOOR = 1800
FLAT = json.load(io.open(u'%s/_b74flat.json' % C, encoding='utf-8'))
CH = json.load(io.open(u'%s/_b74checks.json' % C, encoding='utf-8'))
DER = json.load(io.open(u'%s/_deriv74.json' % C, encoding='utf-8'))
MEA = json.load(io.open(u'%s/_b74meas.json' % C, encoding='utf-8'))

MS = io.open(u'%s/_mkB74.py' % C, encoding='utf-8').read()
ES = io.open(u'%s/_mk74emit.py' % C, encoding='utf-8').read()

# ---- 定义(不是本遍要换的量): 字面表用 ast 摘, 谓词函数用 exec 取 ----
TABS = (u'SENT', u'SG', u'TONE', u'TERMP', u'TIER', u'PARAM6', u'ENTFAM', u'UNIT', u'CITEN')
TAB = {}
for src in (MS, ES):
    for st in ast.parse(src.replace(u'\nexec(', u'\n#exec(')).body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
            nm = st.targets[0].id
            if nm in TABS and nm not in TAB:
                try:
                    TAB[nm] = ast.literal_eval(st.value)
                except Exception:
                    pass
TAB[u'PINS'] = None
for src in (ES, MS):
    for st in ast.parse(src).body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name) and st.targets[0].id == u'PINS':
            TAB[u'PINS'] = ast.literal_eval(st.value)
for nm in list(TABS) + [u'PINS']:
    assert TAB.get(nm) is not None, nm
SENT = TAB[u'SENT']
SG = TAB[u'SG']
TONE = TAB[u'TONE']
TERMP = TAB[u'TERMP']
TIER = TAB[u'TIER']
PARAM6 = TAB[u'PARAM6']
ENTFAM = TAB[u'ENTFAM']
UNIT = TAB[u'UNIT']
CITEN = TAB[u'CITEN']
PINS = TAB[u'PINS']

_ns = {u're': re, u'SG': SG, u'NL': NL, u'u': u'', u'PARAM6': PARAM6}
for src, fns in ((MS, (u'pnorm', u'detag', u'shell_line', u'is_shell_pick', u'pf_defs')),
                 (ES, (u'tag_groups',))):
    for fn in fns:
        m = re.search(u'def ' + fn + u'\\(.*?\\):.*?\\n(?=\\S)', src, re.S)
        assert m, fn
        exec(m.group(0).replace(u'\nexec(', u'\n#exec('), _ns)
for fn in (u'pnorm', u'detag', u'shell_line', u'is_shell_pick', u'pf_defs', u'tag_groups'):
    assert fn in _ns, fn
mk_pnorm = _ns[u'pnorm']
mk_detag = _ns[u'detag']
shell_line = _ns[u'shell_line']
is_shell_pick = _ns[u'is_shell_pick']
mk_pf_defs = _ns[u'pf_defs']
mk_tag_groups = _ns[u'tag_groups']

G = {}
J = lambda xs: u' ⇎ '.join(u'%s' % x for x in xs)


# ---- 本遍自己的尺 ----
def pn2(s):
    """归一: re.sub 档(第二遍是 ' '.join(split()))"""
    return re.sub(u'\\s+', u' ', s.lower()).strip()


assert all(pn2(x) == mk_pnorm(x) for x in (u'  A  b ', u'', u'X\nY\t', u'  ', u'aB'))


def my_split(t):
    """行界: 手写索引循环(第二遍是 str.split)"""
    out, i, n = [], 0, len(t)
    while True:
        j = t.find(NL, i)
        if j < 0:
            out.append(t[i:])
            return out
        out.append(t[i:j])
        i = j + 1


def cnt(t, nd):
    """针计数: str.count(第二遍是游标 find, 采集侧是 re.findall)"""
    return t.count(nd)


def rc(t, nd):
    return len(re.findall(re.escape(nd), t))


def ro(t, nd):
    return len(re.findall(u'(?=' + re.escape(nd) + u')', t))


assert rc(u'aXbX', u'X') == cnt(u'aXbX', u'X') == 2 and ro(u'aaa', u'aa') == 2 and ro(u'aa', u'aa') == 1


def _spans(s):
    """<…> 区间档: 逐枚 '<' 吃到第一枚 '>'(代 <[^>]+>)"""
    out, i = [], 0
    while True:
        a = s.find(u'<', i)
        if a < 0:
            return out
        b = s.find(u'>', a)
        if b < 0:
            return out
        out.append((a, b + 1))
        i = b + 1


def my_detag(s, fill):
    """剥标签三趟字符串扫描: 注释→空格 ⇎ <br…>→空格 ⇎ 其余 <…>→fill, 再照抄 SG 实体表"""
    out, a, i = [], 0, 0
    while True:
        j = s.find(u'<!--', i)
        if j < 0:
            break
        k = s.find(u'-->', j)
        if k < 0:
            break
        out.append(s[a:j])
        out.append(u' ')
        a = i = k + 3
    out.append(s[a:])
    s = u''.join(out)
    out, a = [], 0
    for x, y in _spans(s):
        h = s[x + 1:y - 1]
        if h[:2].lower() == u'br' and h[2:3] in (u'', u'>', u'/', u' ', u'\t'):
            out.append(s[a:x])
            out.append(u' ')
            a = y
    out.append(s[a:])
    s = u''.join(out)
    out, a = [], 0
    for x, y in _spans(s):
        out.append(s[a:x])
        out.append(fill)
        a = y
    out.append(s[a:])
    s = u''.join(out)
    for p, q in SG:
        s = s.replace(p, q)
    return s


def my_tagspans(s):
    """标签区间(注释也算一枚): 与 detag 的注释/标签两趟同尺, 供 tag_open/comment/属性尺复用"""
    out, i = [], 0
    while True:
        a = s.find(u'<', i)
        if a < 0:
            return out
        if s.startswith(u'!--', a + 1):
            b = s.find(u'-->', a)
            if b < 0:
                return out
            out.append((a, b + 3))
            i = b + 3
            continue
        b = s.find(u'>', a)
        if b < 0:
            return out
        out.append((a, b + 1))
        i = b + 1


def in_tag2(s, needle):
    """只在 <…> 区间内数针, 区间由 my_tagspans 给出(第二遍是 find('<')/find('>') 两跳)"""
    return sum(s[a:b].count(needle) for a, b in my_tagspans(s))


def phr(s, w):
    """短语档: finditer 定位后只验左右邻居是否 alnum"""
    return len([m for m in re.finditer(re.escape(w), s)
                if not (m.start() > 0 and s[m.start() - 1].isalnum())
                and not (m.end() < len(s) and s[m.end()].isalnum())])


def ub3(s, w):
    """整词档: 线性扫一遍把连续 alnum 切成 token 后整串比对(第二遍是游标 find + 邻居判定)"""
    if u' ' in w:
        return phr(s, w)
    n, i, m = 0, 0, len(s)
    while i < m:
        if s[i].isalnum():
            j = i
            while j < m and s[j].isalnum():
                j += 1
            if s[i:j] == w:
                n += 1
            i = j
        else:
            i += 1
    return n


TM_RE = re.compile(u'^\\d+[smhdw]$')
NUM_RE = re.compile(u'^\\d+(\\.\\d+)?$')


def is_time3(t):
    return bool(TM_RE.match(t))


def secs3(t):
    assert TM_RE.match(t), t
    return int(t[:-1]) * UNIT[t[-1]]


def val3(t):
    return secs3(t) if TM_RE.match(t) else float(t)


LETS = (u'F', u'G', u'H', u'P')


def parse_rule3(s):
    """规则串: 逗号段首字母 → 之后只吃时长或纯数字, 遇散文即停(定义同第二遍, 判符换正则)"""
    out = []
    for grp in s.split(u';'):
        toks_ = [x.strip() for x in grp.split(u',') if x.strip()]
        if toks_ and toks_[0] not in LETS:
            w = toks_[0].split()
            if w and w[-1] in LETS:
                toks_[0] = w[-1]
        if not toks_ or toks_[0] not in LETS:
            continue
        args = []
        for t in toks_[1:]:
            if not (TM_RE.match(t) or NUM_RE.match(t)):
                break
            args.append(t)
        if len(args) < 2:
            continue
        out.append((toks_[0], secs3(args[0]), args[1:], [val3(x) for x in args[1:]]))
    return out


# ---------- 面 ----------
BYT = [io.open(p, 'rb').read() for p in PATH]
T = [b.decode('utf-8', 'replace') for b in BYT]
L = [my_split(t) for t in T]
FOLD = [u' '.join(t.split()) for t in T]
SHP = [[x for x in L[i] if not is_shell_pick(x)] for i in range(NSRC)]
SHL = [[x for x in L[i] if not shell_line(x)] for i in range(NSRC)]
SH = [u' '.join(NL.join(SHP[i]).split()) if not ISH[i] else FOLD[i] for i in range(NSRC)]
DS, DJ = [], []
for i in range(NSRC):
    if ISH[i]:
        for fill, box in ((u' ', DS), (u'', DJ)):
            box.append(u' '.join(my_detag(T[i], fill).split()))
        assert my_detag(T[i], u' ') == mk_detag(T[i], u' ') and my_detag(T[i], u'') == mk_detag(T[i], u'')
        DS[i] = u' '.join(my_detag(T[i], u' ').split())
        DJ[i] = u' '.join(my_detag(T[i], u'').split())
    else:
        DS.append(FOLD[i])
        DJ.append(FOLD[i])
assert all(DS[i] == DJ[i] == FOLD[i] for i in range(3))
assert all(SH[i] == FOLD[i] for i in range(3, NSRC))
WIDE = [DS[i] if ISH[i] else SH[i] for i in range(NSRC)]
FACES = [L, FOLD, SH, DS, DJ]

# ---------- 本遍的组扫描 ⇎ 行号 ----------
def my_groups(t):
    """切点只在标签/注释之外的换行处: 本遍先把标签/注释覆盖的字符标进保护掩码, 再按掩码外的换行切片
    (第二遍是单游标跳过), 末尾与 tag_groups 逐元组对拍"""
    prot = [False] * len(t)
    i, n = 0, len(t)
    while i < n:
        if t.startswith(u'<!--', i):
            j = t.find(u'-->', i)
            j = n if j < 0 else j + 3
        elif t[i] == u'<':
            j = t.find(u'>', i)
            j = n if j < 0 else j + 1
        else:
            i += 1
            continue
        for k in range(i, j):
            prot[k] = True
        i = j
    out, a = [], 0
    for k in range(n):
        if t[k] == NL and not prot[k]:
            out.append((a, k + 1))
            a = k + 1
    out.append((a, n))
    res = []
    for a, b in out:
        seg = t[a:b]
        if seg.strip() != u'':
            res.append((1 + t.count(NL, 0, a), seg))
    return res


def num_lines(lines):
    """行号由本遍自己累加(第二遍是 enumerate)"""
    out, n = [], 0
    for x in lines:
        n += 1
        out.append((n, x))
    return out


def glued(x):
    """组内是否跨行: 先手工剥掉首尾的换行再看剩余里有没有换行(第二遍是 strip(NL) 后 in 判定)"""
    a, b = 0, len(x)
    while a < b and x[a] == NL:
        a += 1
    while b > a and x[b - 1] == NL:
        b -= 1
    return NL in x[a:b]


def vfind(hay, nd, frm=0):
    """定位针: 编译一次转义正则后 search(第二遍是 str.find)"""
    m = re.compile(re.escape(nd)).search(hay, frm)
    return -1 if m is None else m.start()


MON = u'January|February|March|April|May|June|July|August|September|October|November|December'
MONS = set(MON.split(u'|'))

# ---------- 针 ----------
NEG = [k for o, k, fa, s0, e0 in SENT if s0.startswith(u'@')]
FAI = {u'fold': 1, u'sh': 2, u'ds': 3, u'dj': 4}
FACE = {u'sh': SH, u'ds': DS, u'dj': DJ, u'fold': FOLD}
TEXT = {}
for (o, k, fa, s0, e0) in SENT:
    if k in NEG:
        TEXT[k] = s0[1:]
        continue
    f = FACE[fa][o]
    a = f.find(s0)
    assert a >= 0, (LBL[o], s0[:40])
    if e0 == u'':
        TEXT[k] = f[a:a + len(s0)]
    else:
        b = f.find(e0, a)
        assert b >= 0, (LBL[o], e0[:40])
        TEXT[k] = f[a:b + len(e0)]
OWNER = dict((k, o) for o, k, _, _, _ in SENT)
GN = [k for o, k, _, _, _ in SENT]


def hit(i, nd, tier):
    if tier == 0:
        n = 0
        for x in L[i]:
            if nd in x:
                n += 1
        return n
    return cnt(FACES[tier][i], nd)


SN = dict((k, [hit(OWNER[k], TEXT[k], n) for n in range(5)]) for k in GN)
G['needle_n'] = len(GN)
G['neg_n'] = len(NEG)
TIERN = {0: u'strict', 1: u'fold', 2: u'sh', 3: u'ds', 4: u'dj'}
for n in range(5):
    G[u'sn_' + TIERN[n] + u'_docs'] = [len([k for k in GN if OWNER[k] == i and SN[k][n]]) for i in range(NSRC)]
for k in GN:
    G[u'n_' + k] = SN[k]
G['needles_owned'] = [len([k for k in GN if OWNER[k] == i]) for i in range(NSRC)]
G['fold_minus_strict_keys'] = [k for k in GN if not SN[k][0] and SN[k][1]]
G['fold_minus_strict_own'] = [len([k for k in G['fold_minus_strict_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['fold_minus_strict_n'] = len(G['fold_minus_strict_keys'])
G['sh_minus_fold'] = [G['sn_fold_docs'][i] - G['sn_sh_docs'][i] for i in range(NSRC)]
G['ds_only_keys'] = [k for k in GN if not SN[k][2] and SN[k][3]]
G['ds_only_own'] = [len([k for k in G['ds_only_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['ds_only_n'] = len(G['ds_only_keys'])
G['dj_only_keys'] = [k for k in GN if not SN[k][3] and SN[k][4]]
G['dj_only_n'] = len(G['dj_only_keys'])
G['dj_only_own'] = [len([k for k in G['dj_only_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['ds_no_dj_keys'] = [k for k in GN if SN[k][3] and not SN[k][4]]
G['ds_no_dj_own'] = [len([k for k in G['ds_no_dj_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['ds_no_dj_n'] = len(G['ds_no_dj_keys'])
G['sn_dj_minus_ds'] = [G['sn_dj_docs'][i] - G['sn_ds_docs'][i] for i in range(NSRC)]
G['dead_needles'] = [k for k in GN if k not in NEG and max(SN[k]) == 0]
G['neg_controls'] = sorted(NEG)
G['neg_own'] = [len([k for k in NEG if OWNER[k] == i]) for i in range(NSRC)]
G['neg_hit_widest'] = sum(max(SN[k]) for k in NEG)
G['neg_hit_strict'] = sum(SN[k][0] for k in NEG)
G['fold_gt_ds_keys'] = [k for k in GN if ISH[OWNER[k]] and SN[k][1] > SN[k][3]]
G['attr_loss'] = [sum(SN[k][1] - SN[k][3] for k in G['fold_gt_ds_keys'] if OWNER[k] == i) for i in range(NSRC)]
G['attr_loss_n'] = sum(G['attr_loss'])
G['attr_loss_docs'] = [len([k for k in G['fold_gt_ds_keys'] if OWNER[k] == i]) for i in range(NSRC)]
G['bond_pair'] = 1 if (SN[u'aexim_bond_ds'][3] and not SN[u'aexim_bond_ds'][4]
                       and SN[u'aexim_bond_dj'][4] and not SN[u'aexim_bond_dj'][3]) else 0
G['letter_pair'] = 1 if (SN[u'aexim_F_ds'][3] and not SN[u'aexim_F_ds'][4]
                         and SN[u'aexim_F_dj'][4] and not SN[u'aexim_F_dj'][3]) else 0
G['head_pair'] = 1 if (SN[u'a5321_head'][0] and SN[u'a5321_head'][1]) else 0
G['ladder_monotone'] = 1 if all(G['sn_strict_docs'][i] + G['fold_minus_strict_own'][i]
                                == G['sn_fold_docs'][i]
                                and G['sn_sh_docs'][i] >= G['sn_fold_docs'][i]
                                and G['sn_ds_docs'][i] >= G['sn_fold_docs'][i] for i in range(NSRC)) else 0
RQ = 0
for k in GN:
    if not TEXT[k] or k in NEG:
        continue
    for n in range(1, 5):
        if len(re.findall(re.escape(TEXT[k]), FACES[n][OWNER[k]])) != SN[k][n]:
            RQ += 1
G['re_eq_cur'] = 1 if RQ == 0 else 0
G['overlap_extra'] = sum(ro(WIDE[OWNER[k]], TEXT[k]) - cnt(WIDE[OWNER[k]], TEXT[k])
                         for k in GN if TEXT[k])
G['nd_len'] = [len(TEXT[k]) for k in GN]
G['nd_len_tot'] = sum(G['nd_len'])
G['nd_len_max'] = max(G['nd_len'])

# ---------- 结构面量 ----------
G['bytes'] = [len(b) for b in BYT]
G['chars'] = [len(t) for t in T]
G['lines'] = [len(L[i]) for i in range(NSRC)]
G['lines_nl'] = [cnt(T[i], NL) + 1 for i in range(NSRC)]
G['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
G['blank'] = [len(L[i]) - G['nonblank'][i] for i in range(NSRC)]
G['maxlen'] = [max(len(x) for x in L[i]) for i in range(NSRC)]
G['cr'] = [cnt(T[i], u'\r') for i in range(NSRC)]
G['ff'] = [cnt(T[i], u'\x0c') for i in range(NSRC)]
G['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
G['ff_only'] = [len([x for x in L[i] if x.strip() == u'\x0c']) for i in range(NSRC)]
G['nonascii'] = [len(re.findall(u'[^\\x00-\\x7f]', T[i])) for i in range(NSRC)]
G['bom'] = [1 if b[:3] == b'\xef\xbb\xbf' else 0 for b in BYT]
G['txt_n'] = NSRC - sum(1 for x in ISH if x)
G['html_n'] = sum(1 for x in ISH if x)
G['nul'] = [cnt(t, u'\x00') for t in T]
G['digit_chars'] = [len(re.findall(u'\\d', t)) for t in T]
G['nonascii_extra'] = [len(t.encode('utf-8')) - len(t) for t in T]
G['byte_cp_delta'] = [G['bytes'][i] - G['chars'][i] for i in range(NSRC)]
G['tail_nl'] = [1 if T[i].endswith(NL) else 0 for i in range(NSRC)]
G['lines_split'] = [len(T[i].splitlines()) for i in range(NSRC)]
G['lines_split_close'] = sum(G['lines_nl'][i] - G['tail_nl'][i] + G['ff'][i] - G['lines_split'][i]
                             for i in range(NSRC))

# ---------- HTML 结构: 逐枚 '<' 看紧跟的首字符(finditer 档, 第二遍是 split('<')) ----------
TO, TC, BR = [0] * NSRC, [0] * NSRC, [0] * NSRC
for i in range(NSRC):
    if not ISH[i]:
        continue
    for m in re.finditer(u'<', T[i]):
        nxt = T[i][m.end():m.end() + 1]
        if nxt == u'/':
            TC[i] += 1
        elif nxt.isalpha():
            TO[i] += 1
        if T[i][m.end():m.end() + 2].lower() == u'br' and T[i][m.end() + 2:m.end() + 3] in (
                u'>', u'/', u' ', u'\t'):
            BR[i] += 1
G['tag_open'] = TO
G['tag_close'] = TC
G['tag_tot'] = [TO[i] + TC[i] for i in range(NSRC)]
G['comment'] = [len([m for m in re.finditer(u'<!--', T[i])]) if ISH[i] else 0 for i in range(NSRC)]
G['br_tag'] = BR
G['ent_fam'] = ENTFAM
G['ent_raw'] = [[cnt(T[i], e) for e in ENTFAM] for i in range(NSRC)]
G['ent_total'] = [sum(x) for x in G['ent_raw']]
ENTOK = [Counter(re.findall(u'&[#a-zA-Z0-9]{1,10};', T[i])) if ISH[i] else Counter() for i in range(NSRC)]
G['ent_distinct'] = [len(ENTOK[i]) for i in range(NSRC)]
G['ent_all'] = [sum(ENTOK[i].values()) for i in range(NSRC)]
G['ent_top'] = [[w for w, _ in ENTOK[i].most_common(3)] for i in range(NSRC)]
G['ent_double_left'] = [cnt(DS[i], u'&amp;') for i in range(NSRC)]
G['ent_numeric_left'] = [sum(cnt(DS[i], e) for e in (u'&#34;', u'&#39;', u'&#43;', u'&#x2F;'))
                         for i in range(NSRC)]
G['ent_lt_left'] = [cnt(DS[i], u'&lt;') for i in range(NSRC)]
G['ent_amp_raw'] = [cnt(T[i], u'&amp;') for i in range(NSRC)]
G['ent_amp_eaten'] = [G['ent_amp_raw'][i] - G['ent_double_left'][i] for i in range(NSRC)]

# ---------- 页壳两遍账 ----------
G['shell_pick'] = [len(L[i]) - len(SHP[i]) for i in range(NSRC)]
G['shell_n'] = [len(L[i]) - len(SHL[i]) for i in range(NSRC)]
MO, PO = [], []
for i in range(NSRC):
    a = b = 0
    for x in L[i]:
        if shell_line(x) and not is_shell_pick(x):
            a += 1
        if is_shell_pick(x) and not shell_line(x):
            b += 1
    MO.append(a)
    PO.append(b)
G['shell_both'] = [G['shell_n'][i] - MO[i] for i in range(NSRC)]
G['shell_mk_only'] = MO
G['shell_pick_only'] = PO
G['shell_diff'] = [G['shell_n'][i] - G['shell_pick'][i] for i in range(NSRC)]
G['shell_page'] = [len([x for x in L[i] if re.search(u'\\[Page \\d+\\]', x)]) for i in range(NSRC)]
G['shell_hdr'] = [len([1 for x in L[i] if re.match(u'^\\s*RFC ?\\d{3,4}\\s+.*((19|20)\\d\\d)\\s*$', x)])
                  for i in range(NSRC)]
G['shell_blank'] = G['blank']
MKH, POB = [0] * NSRC, [0] * NSRC
for i in range(NSRC):
    for x in L[i]:
        if shell_line(x) and not is_shell_pick(x) and re.match(
                u'^\\s*(Request for Comments:|Obsoletes:|Updates:|Replaces:|Category:|ISSN:|RFC ?\\d)', x):
            MKH[i] += 1
        if is_shell_pick(x) and not shell_line(x) and re.match(u'^[ \\t]+\\S', x):
            POB[i] += 1
G['shell_mk_only_hdr'] = MKH
G['shell_pick_only_body'] = POB
G['shell_ledger_close'] = sum(abs(G['shell_pick'][i] + G['shell_mk_only'][i]
                                  - G['shell_pick_only'][i] - G['shell_n'][i]) for i in range(NSRC))

# ---------- 序列化三式 ----------
def hb_rest(x):
    """手写档: 吃掉“空白 + 数字(.数字)+”的编号前缀, 返回其余串(代 ^\\s*\\d+(?:\\.\\d+)+)"""
    i, n = 0, len(x)
    while i < n and x[i] in u' \t':
        i += 1
    if i >= n or not x[i].isdigit():
        return None
    while i < n and x[i].isdigit():
        i += 1
    dots = 0
    while i + 1 < n and x[i] == u'.' and x[i + 1].isdigit():
        i += 1
        while i < n and x[i].isdigit():
            i += 1
        dots += 1
    return x[i:] if dots else None


D2, D1, DN = [0] * NSRC, [0] * NSRC, [0] * NSRC
for i in range(NSRC):
    for x in L[i]:
        r = hb_rest(x)
        if r is None:
            continue
        if r[:1] == u'.' and r[1:3] == u'  ' and len(r) > 3 and not r[3].isspace():
            D2[i] += 1
        elif r[:1] == u'.' and r[1:2] == u' ' and len(r) > 2 and not r[2].isspace():
            D1[i] += 1
        elif r[:1] == u' ' and len(r) > 1 and not r[1].isspace():
            DN[i] += 1
G['hdr_dot2sp'] = D2
G['hdr_dot1sp'] = D1
G['hdr_nodot'] = DN
G['dblspace_in_fold'] = [cnt(FOLD[i], u'  ') for i in range(NSRC)]
G['dot_dblspace_anywhere'] = [len(re.findall(u'\\S\\.  \\S', FOLD[i])) for i in range(NSRC)]
HY, NDH = [0] * NSRC, [0] * NSRC
for i in range(NSRC):
    for j in range(len(L[i]) - 1):
        a, b = L[i][j], L[i][j + 1]
        if a.rstrip().endswith(u'-') and re.match(u'^\\s*[a-z]', b):
            HY[i] += 1
        if a.rstrip().endswith(u'non-') and b.lstrip().startswith(u'delivery'):
            NDH[i] += 1
G['hyphen_break'] = HY
G['ndn_hyphen_break'] = NDH
G['ndn_unbroken'] = [cnt(WIDE[i], u'non-delivery') for i in range(NSRC)]
G['ndn_broken'] = [cnt(WIDE[i], u'non- delivery') for i in range(NSRC)]
G['ndn_other'] = [ro(WIDE[i], u'non-') - (G['ndn_unbroken'][i] + G['ndn_broken'][i]) for i in range(NSRC)]

# ---------- 义务语气五轨 ----------
G['tone_pats'] = TONE
for w in TONE:
    G[u'tone_' + w.replace(u' ', u'_')] = [ub3(WIDE[i], w) for i in range(NSRC)]
G['tone'] = [[G[u'tone_' + w.replace(u' ', u'_')][i] for w in TONE] for i in range(NSRC)]
G['tone_tot'] = [sum(G['tone'][i]) for i in range(NSRC)]
G['tone_must_lc'] = [ub3(WIDE[i], u'must') for i in range(NSRC)]
G['tone_zero_must'] = [1 if (G['tone'][i][0] + G['tone'][i][1]) == 0 else 0 for i in range(NSRC)]
G['tone_zero_all'] = [1 if G['tone_tot'][i] == 0 else 0 for i in range(NSRC)]
G['kw_clause'] = [len(re.findall(u'[Kk]ey [Ww]ords', WIDE[i])) for i in range(NSRC)]
G['c821_may_month'] = [cnt(WIDE[i], u'"MAY"') for i in range(NSRC)]
G['must_bare'] = [G['tone'][i][1] - G['tone'][i][0] for i in range(NSRC)]
G['tone_ledger'] = [G['tone'][i][1] - (G['must_bare'][i] + G['tone'][i][0]) for i in range(NSRC)]
G['tone_re_ledger'] = [[len(re.findall(u'(?<![A-Za-z0-9])' + re.escape(w) + u'(?![A-Za-z0-9])', WIDE[i]))
                        - G[u'tone_' + w.replace(u' ', u'_')][i] for w in TONE] for i in range(NSRC)]
G['tone_ruler_close'] = sum(sum(abs(x) for x in v) for v in G['tone_re_ledger'])
G['tone_per_attempt'] = [G['tone'][i][1] for i in range(NSRC)]

# ---------- 术语尺 ----------
G['term_pats'] = TERMP
G['terms'] = [[cnt(WIDE[i], p) for p in TERMP] for i in range(NSRC)]
G['sender_smtp'] = [x[0] for x in G['terms']]
G['smtp_client'] = [x[1] for x in G['terms']]
G['receiver_smtp'] = [x[3] for x in G['terms']]
G['spelling_queueing'] = [x[4] for x in G['terms']]
G['spelling_queuing'] = [x[5] for x in G['terms']]
G['queue_word'] = [x[6] for x in G['terms']]
G['retry_word'] = [x[7] + x[8] + x[9] for x in G['terms']]
G['term_new_per_mille'] = [(1000 * G['smtp_client'][i]) // (G['smtp_client'][i] + G['sender_smtp'][i])
                           if (G['smtp_client'][i] + G['sender_smtp'][i]) else -1 for i in range(NSRC)]
G['c821_no_retry_vocabulary'] = 1 if (G['retry_word'][0] == 0 and G['queue_word'][0] == 0) else 0
for nm, nd in ((u'word_expo', u'exponential'), (u'word_geo', u'geometric'), (u'word_cutoff', u'cutoff'),
               (u'word_giveup', u'give up'), (u'word_transient', u'transient'),
               (u'word_permanent', u'permanent'), (u'word_deferred', u'deferred')):
    G[nm] = [cnt(WIDE[i], nd) for i in range(NSRC)]
G['word_timeout'] = [cnt(WIDE[i], u'Timeout') + cnt(WIDE[i], u'timeout') for i in range(NSRC)]

# ---------- 措辞十二族 ----------
G['tier_words'] = list(TIER.keys())
G['tier_pats'] = list(TIER.values())
for k, w in TIER.items():
    G[u'tier_' + k] = [cnt(WIDE[i], w) for i in range(NSRC)]
    G[u'tierf_' + k] = [cnt(FOLD[i], w) for i in range(NSRC)]
G['tier_tot'] = [sum(G[u'tier_' + k][i] for k in TIER) for i in range(NSRC)]
G['tier_fold_tot'] = [sum(G[u'tierf_' + k][i] for k in TIER) for i in range(NSRC)]
G['tier_wide_minus_fold'] = [G['tier_tot'][i] - G['tier_fold_tot'][i] for i in range(NSRC)]
G['tier_zero_fams'] = [len([k for k in TIER if G[u'tier_' + k][i] == 0]) for i in range(NSRC)]
G['tier_hit_fams'] = [len([k for k in TIER if G[u'tier_' + k][i]]) for i in range(NSRC)]
G['time_digit_docs'] = [len(re.findall(u'\\d+\\s*(minutes?|hours?|days?|seconds?)', WIDE[i]))
                        for i in range(NSRC)]

# ---------- Exim 规则串 ----------
DL3 = [mk_detag(x, u'') for x in L[3]]
PR = [n for n, x in enumerate(DL3) if u'default retry rule' in x.lower()]
DEF_RULE = u''
for n in PR:
    for m in range(n + 1, min(n + 9, len(DL3))):
        s = DL3[m].strip()
        if s.startswith(u'* * ') and s[4:5] in LETS and s[5:6] == u',' and u',' in s:
            if not DEF_RULE:
                DEF_RULE = s
            break
assert DEF_RULE, u'B74: 默认规则串没在面上读到'
ALT = [x for x in [u' '.join(y.split()) for y in DL3]
       if x.startswith(u'* * ') and x[4:5] in LETS and x[5:6] == u',']
OTH = [x for x in ALT if x != DEF_RULE]
assert len(OTH) == 1, OTH
OTHER_RULE = OTH[0]
DEF_HITS = cnt(WIDE[3], DEF_RULE)
assert OTHER_RULE.split(u';')[:2] == DEF_RULE.split(u';')[:2]
G['ex_def_rule'] = DEF_RULE
G['ex_star_star_rules'] = len(ALT)
G['ex_star_star_distinct'] = len(set(ALT))
G['ex_def_rule_prompt'] = len(PR)
_d = parse_rule3(DEF_RULE)
G['ex_def_sets'] = len(_d)
G['ex_def_letters'] = sorted(set(x[0] for x in _d))
G['ex_def_cutoffs'] = [x[1] for x in _d]
G['ex_def_first'] = [x[3][0] for x in _d]
G['ex_def_mults'] = [float(x[2][1]) for x in _d if x[0] == u'G']
G['ex_def_args'] = [len(x[2]) for x in _d]
G['ex_def_span'] = G['ex_def_cutoffs'][-1]
RL = [x for x in DL3 if re.search(u'[FGPH],\\d+\\w', x)]
RS = []
for x in RL:
    RS.extend(parse_rule3(x.strip()))
G['ex_rule_lines'] = len(RL)
G['ex_sets_n'] = len(RS)
G['ex_letters'] = sorted(set(x[0] for x in RS))
G['ex_cutoff_sec'] = sorted(set(x[1] for x in RS))
G['ex_first_sec'] = sorted(set(x[3][0] for x in RS))
G['ex_mults'] = sorted(set(float(x[2][1]) for x in RS if x[0] == u'G' and len(x[2]) > 1))
LET = sorted(set(re.findall(u'([FGPH]): retry at', DJ[3])))
G['ex_letters_def'] = LET
G['ex_letters_used_only'] = sorted(set(G['ex_letters']) - set(LET))
G['ex_letters_def_only'] = sorted(set(LET) - set(G['ex_letters']))
G['ex_rim_cap'] = secs3(u'24h')
G['ex_rim_default_line'] = cnt(DJ[3], u'24h, which is its default value')
G['ex_expire_days'] = secs3(u'7d')
G['ex_f1_attempts'] = G['ex_def_cutoffs'][0] // G['ex_def_first'][0]
G['ex_f3_attempts'] = G['ex_def_cutoffs'][2] // G['ex_def_first'][2]
_g, _t, _i = [], 0.0, float(G['ex_def_first'][1])
while _t < G['ex_def_cutoffs'][1] and len(_g) < 40:
    _g.append(int(_i))
    _t += _i
    _i *= G['ex_def_mults'][0]
G['ex_g_steps'] = len(_g)
G['ex_g_step_sec'] = _g
G['ex_g_total'] = sum(_g)
G['ex_attempts_tot'] = G['ex_f1_attempts'] + G['ex_g_steps'] + G['ex_f3_attempts']
G['ex_sched_sec'] = G['ex_def_cutoffs']

# ---------- Postfix 默认值 ----------
G['pf_params'] = PARAM6


def pf_defs3(face):
    """finditer 档: 名字 + ' (default: ' 之后吃到第一枚 ')' """
    out = []
    for p in PARAM6:
        out.append([m.group(1) for m in
                    re.finditer(re.escape(p + u' (default: ') + u'([^)]*)\\)', face)])
    return out


G['pf_defs_dj'] = pf_defs3(DJ[4])
G['pf_defs_fold'] = pf_defs3(FOLD[4])
assert G['pf_defs_dj'] == mk_pf_defs(DJ[4]) and G['pf_defs_fold'] == mk_pf_defs(FOLD[4])
G['pf_body_hit'] = [len(x) for x in G['pf_defs_dj']]
G['pf_fold_hit'] = [len(x) for x in G['pf_defs_fold']]
G['pf_attr_only'] = [G['pf_fold_hit'][n] - G['pf_body_hit'][n] for n in range(len(PARAM6))]
G['pf_attr_docs_n'] = len([n for n in range(len(PARAM6)) if G['pf_attr_only'][n]])
G['pf_default_in_tag'] = sum(in_tag2(FOLD[4], p + u' (default: ') for p in PARAM6)
G['pf_nd_default_all'] = cnt(FOLD[4], u' (default: ')
G['pf_nd_default_tag'] = in_tag2(FOLD[4], u' (default: ')
G['pf_nd_default_dj'] = cnt(DJ[4], u' (default: ')
G['pf_value_in_fold'] = sum(1 for n in range(len(PARAM6))
                            for v in G['pf_defs_dj'][n] if v in G['pf_defs_fold'][n])
G['pf_def_tok'] = [x[0] for x in G['pf_defs_dj']]
G['pf_def_sec'] = [secs3(x[0]) for x in G['pf_defs_dj']]
G['pf_zero_once'] = cnt(DJ[4], u'Specify 0 when mail delivery should be tried only once')
G['pf_unit_line'] = cnt(DJ[4], u'Time units: s (seconds), m (minutes), h (hours), d (days), w (weeks).')
G['pf_unit_s'] = cnt(DJ[4], u'The default time unit is s (seconds).')
G['pf_unit_d'] = cnt(DJ[4], u'The default time unit is d (days).')
G['pf_unit_h'] = cnt(DJ[4], u'The default time unit is h (hours).')
G['pf_le_qrd'] = cnt(DJ[4], u'set less than or equal to $minimal_backoff_time')
G['pf_ge_minbo'] = cnt(DJ[4], u'greater than or equal to $minimal_backoff_time')
G['pf_ge_qrd'] = cnt(DJ[4], u'greater than or equal to $queue_run_delay')
G['pf_prior_1000s'] = cnt(DJ[4], u'prior to Postfix 2.4 the default value was 1000s')
G['pf_5d'] = cnt(DJ[4], u'(default: 5d)')

# ---------- 跨源时长换算 ----------
CVN = [u'1123/5321 下限 30 分钟', u'exim 首档间隔 15m', u'exim 次档起始 1h',
       u'postfix minimal_backoff_time', u'postfix queue_run_delay', u'postfix transport_retry_time',
       u'postfix maximal_backoff_time', u'exim retry_interval_max 封顶', u'exim 默认末档跨度',
       u'postfix 队列寿命默认']
CVV = [FLOOR, secs3(u'15m'), secs3(u'1h'), G['pf_def_sec'][2], G['pf_def_sec'][4], G['pf_def_sec'][5],
       G['pf_def_sec'][3], G['ex_rim_cap'], G['ex_def_span'], G['pf_def_sec'][0]]
G['cv_names'] = CVN
G['cv_sec'] = CVV
G['cv_floor'] = FLOOR
G['cv_below_n'] = len([v for v in CVV if v < FLOOR])
G['cv_above_n'] = len([v for v in CVV if v >= FLOOR])
G['cv_close'] = G['cv_below_n'] + G['cv_above_n'] - len(CVV)
G['cv_below'] = sorted([CVV[n] for n in range(len(CVV)) if CVV[n] < FLOOR])
G['band_lo'] = 4 * 86400
G['band_hi'] = 5 * 86400
G['cv_floor_in_band'] = 1 if G['band_lo'] <= FLOOR <= G['band_hi'] else 0
G['ex_cutoff_in_band'] = 1 if G['band_lo'] <= G['ex_def_span'] <= G['band_hi'] else 0
G['pf_life_in_band'] = 1 if G['band_lo'] <= G['pf_def_sec'][0] <= G['band_hi'] else 0
G['pf_bql_same_mql'] = 1 if G['pf_def_sec'][0] == G['pf_def_sec'][1] else 0
G['band_edge_hits'] = len([v for v in (G['ex_def_span'], G['pf_def_sec'][0])
                           if v in (G['band_lo'], G['band_hi'])])
G['pf_chain'] = [1 if G['pf_def_sec'][3] >= G['pf_def_sec'][2] else 0,
                 1 if G['pf_def_sec'][2] >= G['pf_def_sec'][4] else 0]
G['cv_ratio_exim_vs_floor'] = G['ex_def_first'][0] * 1000 // FLOOR
G['cv_ratio_pf_vs_floor'] = G['pf_def_sec'][2] * 1000 // FLOOR
G['cv_floor_minus_exim'] = FLOOR - G['ex_def_first'][0]
G['cv_floor_minus_pf'] = FLOOR - G['pf_def_sec'][2]
G['cv_pf_x_by_floor'] = FLOOR // G['pf_def_sec'][2] if G['pf_def_sec'][2] else 0
G['cv_exim_x_by_floor'] = FLOOR // G['ex_def_first'][0]
G['day_sec'] = 86400

# ---------- 出处头 / 年份 / 引用 ----------
def hdr_field(lines, field):
    for x in lines:
        if x.startswith(field + u':'):
            return x
    return u''


G['obs_line'] = [hdr_field(L[i], u'Obsoletes') for i in range(NSRC)]
G['upd_line'] = [hdr_field(L[i], u'Updates') for i in range(NSRC)]
G['repl_line'] = [hdr_field(L[i], u'Replaces') for i in range(NSRC)]
G['obs_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{3,4}', G['obs_line'][i].split(u'  ')[0])))
                for i in range(NSRC)]
G['upd_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{3,4}', G['upd_line'][i]))) for i in range(NSRC)]
G['repl_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{3,4}', G['repl_line'][i].split(u'  ')[0])))
                 for i in range(NSRC)]
G['obs_n'] = [len(x) for x in G['obs_ids']]
G['upd_n'] = [len(x) for x in G['upd_ids']]
G['repl_n'] = [len(x) for x in G['repl_ids']]
G['target_ids'] = sorted(set().union(*[set(x) for x in G['obs_ids'] + G['upd_ids'] + G['repl_ids']]))
G['target_n'] = len(G['target_ids'])
G['rfc_hdr'] = [(re.findall(u'^Request for Comments: ?(\\d+)', NL.join(L[i][:20]), re.M) or [None])[0]
                for i in range(NSRC)]


def hdr_year(lines):
    """相邻 token 对档: 月名紧跟四位数字(第二遍是 (MON) +\\d{4} 联合正则)"""
    for x in lines[:90]:
        tk = x.split()
        for n in range(len(tk) - 1):
            if tk[n] in MONS and re.match(u'^\\d{4}$', tk[n + 1]):
                return (int(tk[n + 1]), tk[n])
    return (None, None)


YR = [hdr_year(L[i]) for i in range(NSRC)]
G['years_txt'] = [y for y, _ in YR]
G['months_txt'] = [mo for _, mo in YR]
G['year_copyright'] = [int(x) for x in re.findall(u'Copyright ©\\d{4}-(\\d{4})', T[3])]
G['year_stamp'] = re.findall(u'\\d{4}-\\d{2}-\\d{2}T', T[4])
G['year_stamp_n'] = len(G['year_stamp'])
G['year_stamp_first'] = G['year_stamp'][0][:4] if G['year_stamp'] else None
G['year_stamp_last'] = G['year_stamp'][-1][:4] if G['year_stamp'] else None
G['years'] = [None] * NSRC
for i in range(3):
    G['years'][i] = YR[i][0]
G['years'][3] = G['year_copyright'][0] if G['year_copyright'] else None
G['years'][4] = int(G['year_stamp'][-1][:4]) if G['year_stamp'] else None
G['year_gaps'] = [G['years'][i + 1] - G['years'][i] for i in range(NSRC - 1)]
G['year_span'] = G['years'][-1] - G['years'][0]
G['year_inversions'] = len([1 for a in range(NSRC) for b in range(a + 1, NSRC) if G['years'][a] > G['years'][b]])
G['year_close'] = sum(G['year_gaps']) - G['year_span']

CITE = {}
for n in CITEN:
    CITE['sp_' + n] = [cnt(T[i], u'RFC ' + n) for i in range(NSRC)]
    CITE['tk_' + n] = [cnt(T[i], u'RFC' + n) for i in range(NSRC)]
    CITE['hy_' + n] = [cnt(T[i], u'RFC-' + n) for i in range(NSRC)]
    CITE['2f_' + n] = [CITE['sp_' + n][i] + CITE['tk_' + n][i] for i in range(NSRC)]
    CITE['3f_' + n] = [CITE['2f_' + n][i] + CITE['hy_' + n][i] for i in range(NSRC)]
for k in CITE:
    G['cite_' + k] = CITE[k]
G['cite_self'] = [CITE['2f_' + LBL[i]][i] if i < 3 else 0 for i in range(NSRC)]
G['cite_forms_close'] = [len(re.findall(u'RFC[- ]?%s\\b' % LBL[i], T[i])) - CITE['3f_' + LBL[i]][i]
                         if i < 3 else 0 for i in range(NSRC)]
G['cite_821_in_5321'] = CITE['2f_821'][2]
G['cite_1123_in_5321'] = CITE['2f_1123'][2]
G['cite_821_in_1123'] = CITE['2f_821'][1]
G['cite_821_hy_in_1123'] = CITE['hy_821'][1]
G['cite_821_3f_in_1123'] = CITE['3f_821'][1]
G['cite_2821_tot'] = sum(CITE['2f_2821'])
G['cite_rfc_word'] = [len(re.findall(u'RFC ?\\d', T[i])) for i in range(NSRC)]


# ---------- 共用长行池 ----------
def pool_lines(i):
    return [x for x in SHP[i] if len(pn2(x)) >= POOLMIN]


NPOOL = []
RAWBY = []
for i in range(NSRC):
    d = defaultdict(list)
    for x in pool_lines(i):
        d[pn2(x)].append(x)
    RAWBY.append(d)
    NPOOL.append(set(d))
pool_all = set().union(*NPOOL)
PRES = {}
for a in pool_all:
    v = []
    for i in range(NSRC):
        if a in NPOOL[i]:
            v.append(i)
    PRES[a] = tuple(v)
G['pool_n'] = len(pool_all)
TH = Counter(len(v) for v in PRES.values())
G['pool_tier'] = [TH.get(n, 0) for n in range(1, NSRC + 1)]
G['pool_tier_close'] = sum(G['pool_tier']) - len(pool_all)
for n in range(3):
    G['pool_%d' % (n + 1)] = G['pool_tier'][n]
PAIRS = [(a, b) for a, b in itertools.combinations(range(NSRC), 2)]
share, byte, nonly = [], [], []
for i, j in PAIRS:
    inter = NPOOL[i] & NPOOL[j]
    b = 0
    for s in inter:
        for x in RAWBY[i][s]:
            if x in set(RAWBY[j][s]):
                b += 1
                break
    share.append(len(inter))
    byte.append(b)
    nonly.append(len(inter) - b)
G['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
G['pair_share'] = share
G['pair_byte'] = byte
G['pair_norm_only'] = nonly
G['pair_nonzero'] = len([x for x in share if x])
G['pair_zero'] = len(PAIRS) - G['pair_nonzero']
G['pair_close'] = sum(share) - sum(byte) - sum(nonly)
mx = max(share)
G['pair_max'] = mx
G['pair_max_idx'] = share.index(mx)
G['pair_max_byte'] = byte[G['pair_max_idx']]
G['pair_max_norm_only'] = nonly[G['pair_max_idx']]
G['pair_max_lbl'] = G['pair_lbl'][G['pair_max_idx']]
G['retry_pair_idx'] = PAIRS.index((1, 2))
G['pair_1123_5321'] = share[G['retry_pair_idx']]
G['pair_821_5321'] = share[PAIRS.index((0, 2))]
_w = [len(v) for v in PRES.values()]
G['pool_incl'] = [sum(_w), sum(x * (x - 1) // 2 for x in _w), sum(x * (x - 1) * (x - 2) // 6 for x in _w),
                  sum(x * (x - 1) * (x - 2) * (x - 3) // 24 for x in _w), _w.count(NSRC)]
G['union_incl'] = G['pool_incl'][0] - G['pool_incl'][1] + G['pool_incl'][2] - G['pool_incl'][3] + G['pool_incl'][4]
G['union_close'] = G['pool_n'] - G['union_incl']
G['pool_html_own'] = len([a for a, v in PRES.items() if 3 in v or 4 in v])
G['pool_html_shared'] = len([a for a, v in PRES.items() if (3 in v or 4 in v) and len(v) >= 2])
G['pool_txt_shared'] = len([a for a, v in PRES.items() if len(v) >= 2])
G['shared_norm_only'] = sum(nonly)


def dehyph(s):
    """脱去连字符与其后成串空白(代第二遍的逐字符吃): 一条 re.sub 同定义不同路"""
    return re.sub(u'-[ \\t]*', u'', s).lower()


RANK = {u'case': 0, u'hyph': 1, u'space': 2, u'multi': 3}


def bucket(o, p):
    if o.lower() == p.lower():
        return u'case'
    if dehyph(o) == dehyph(p):
        return u'hyph'
    if o.strip() == p.strip():
        return u'space'
    return u'multi'


axis = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
cand = []
for a, v in PRES.items():
    if len(v) < 2:
        continue
    var = dict((i, set(RAWBY[i][a])) for i in v)
    dif = [(o, p) for i, j in itertools.combinations(v, 2) for o in var[i] for p in var[j] if o != p]
    if not dif:
        continue
    cand.append(a)
    axis[min((bucket(o, p) for o, p in dif), key=lambda w: RANK[w])] += 1
G['axis_counts'] = axis
G['axis_total'] = sum(axis.values())
G['norm_only_set'] = len(cand)
G['axis_close'] = G['axis_total'] - G['norm_only_set']
G['axis_str'] = u' ⇎ '.join(u'%s%d' % (a, axis[a]) for a in (u'case', u'hyph', u'space', u'multi'))
G['axis_str_n'] = len([a for a in (u'case', u'hyph', u'space', u'multi') if axis[a]])


# ---------- 句级原子 ----------
def sents3(face):
    return [u' '.join(x.lower().split()) for x in
            re.split(u'(?<=[.!?])\\s+(?=[A-Z0-9*<])', face)]


SP = [set(x for x in sents3(WIDE[i]) if len(x) >= 40) for i in range(NSRC)]
SPRES = {}
for i, s in enumerate(SP):
    pass
SPRES = dict((a, tuple(i for i in range(NSRC) if a in SP[i])) for s in SP for a in s)
G['s_pool_n'] = len(SPRES)
SH_ = Counter(len(v) for v in SPRES.values())
G['s_pool_tier'] = [SH_.get(k, 0) for k in range(1, NSRC + 1)]
G['s_pool_tier_close'] = sum(G['s_pool_tier']) - G['s_pool_n']
G['s_pair_share'] = [len(SP[a] & SP[b]) for a, b in PAIRS]
G['s_pair_max'] = max(G['s_pair_share'])
G['s_pair_max_idx'] = G['s_pair_share'].index(G['s_pair_max'])
G['s_pair_max_lbl'] = G['pair_lbl'][G['s_pair_max_idx']]
G['s_pair_1123_5321'] = G['s_pair_share'][G['retry_pair_idx']]
G['s_pair_821_5321'] = G['s_pair_share'][PAIRS.index((0, 2))]
G['s_ruler_gain_1123_5321'] = G['s_pair_1123_5321'] - G['pair_1123_5321']
G['s_ruler_gain_821_5321'] = G['s_pair_821_5321'] - G['pair_821_5321']
G['s_pair_html'] = len([n for n, (a, b) in enumerate(PAIRS)
                        if (a >= 3 or b >= 3) and G['s_pair_share'][n]])
_sw = [len(v) for v in SPRES.values()]
G['s_incl'] = [sum(len(SP[i]) for i in range(NSRC)), sum(x * (x - 1) // 2 for x in _sw),
               sum(x * (x - 1) * (x - 2) // 6 for x in _sw),
               sum(x * (x - 1) * (x - 2) * (x - 3) // 24 for x in _sw), _sw.count(NSRC)]
G['s_union_incl'] = (G['s_incl'][0] - G['s_incl'][1] + G['s_incl'][2]
                     - G['s_incl'][3] + G['s_incl'][4])
G['s_union_close'] = G['s_pool_n'] - G['s_union_incl']

# ---------- 锚候选池 ----------
AP = defaultdict(set)
araw, apn = [], [0] * NSRC
for i in range(NSRC):
    for x in SHP[i]:
        a = pn2(x)
        if len(a) >= APOOLMIN and re.search(u'[A-Za-z]', x):
            AP[a].add(i)
            araw.append((a, i))
            apn[i] += 1
G['apool_n'] = len(AP)
G['apool_raw_n'] = len(araw)
G['apool_face_raw'] = apn
G['apool_tag_n'] = [len([a for a, v in AP.items() if i in v]) for i in range(NSRC)]
G['apool_dup'] = [G['apool_face_raw'][i] - G['apool_tag_n'][i] for i in range(NSRC)]
G['apool_tag_close'] = sum(G['apool_tag_n']) + sum(G['apool_dup']) - G['apool_raw_n']
AT = Counter(len(v) for v in AP.values())
G['apool_tier'] = [AT.get(n, 0) for n in range(1, NSRC + 1)]
G['apool_weight'] = sum(G['apool_tier'][n] * (n + 1) for n in range(NSRC))
G['apool_pairs'] = sum(G['apool_tag_n'])
G['apool_tier_close'] = G['apool_weight'] - G['apool_pairs']
G['apool_maxlen'] = max(len(a) for a in AP)

# ---------- 标量判定 ----------
CLOSE = {}
CLOSE[u'dead_needles_none'] = 0 if len(G['dead_needles']) else 1
CLOSE[u'neg_all_cold'] = 0 if (G['neg_hit_widest'] or G['neg_n'] != len(G['neg_controls'])) else 1
CLOSE[u'bond_pair'] = G['bond_pair']
CLOSE[u'letter_pair'] = G['letter_pair']
CLOSE[u'head_pair'] = G['head_pair']
CLOSE[u'no_needle_lost_by_detag'] = 0 if G['attr_loss_n'] else 1
CLOSE[u'ds_only_exim_only'] = 1 if (G['ds_only_own'][3] and G['ds_only_own'][4]
                                    and sum(G['ds_only_own'][:3]) == 0) else 0
CLOSE[u'no_retry_vocab_821'] = G['c821_no_retry_vocabulary']
CLOSE[u'tone_zero_must_pair'] = 1 if (G['tone_zero_must'][0] and G['tone_zero_must'][3]
                                      and G['tone_zero_must'][1] + G['tone_zero_must'][2]
                                      + G['tone_zero_must'][4] == 0) else 0
CLOSE[u'exim_no_tone'] = 1 if G['tone_zero_all'][3] and sum(
    G['tone_zero_all'][:3] + G['tone_zero_all'][4:]) == 0 else 0
CLOSE[u'tier_821_only_hard'] = 1 if (G['tier_hard_define'][0] and sum(G['tier_hard_define'][1:]) == 0) else 0
CLOSE[u'cutoff_exim_only'] = 1 if (G['word_cutoff'][3] and sum(
    G['word_cutoff'][:3] + G['word_cutoff'][4:]) == 0) else 0
CLOSE[u'client_only_5321_pf'] = 1 if (G['smtp_client'][2] and G['smtp_client'][4]
                                      and G['smtp_client'][0] + G['smtp_client'][1]
                                      + G['smtp_client'][3] == 0) else 0
CLOSE[u'ex_cutoff_in_band'] = G['ex_cutoff_in_band']
CLOSE[u'pf_life_in_band'] = G['pf_life_in_band']
CLOSE[u'pf_bql_eq_mql'] = G['pf_bql_same_mql'] if u'pf_bql_same_mql' in G else G['pf_bql_same_mql']
CLOSE[u'pf_chain_up'] = 1 if min(G['pf_chain']) == 1 else 0
CLOSE[u'below_floor_four'] = 1 if G['cv_below_n'] == 4 else 0
CLOSE[u'cite_hy_only_1123'] = 1 if (G['cite_821_in_1123'] == 0 and G['cite_821_hy_in_1123'] > 0) else 0
CLOSE[u'obs_5321_line'] = 1 if G['obs_ids'][2] == [2821] and G['upd_ids'][2] == [1123] else 0
CLOSE[u'repl_821_only'] = 1 if (G['repl_n'][0] == 3 and sum(G['repl_n'][1:]) == 0) else 0
CLOSE[u'year_monotone'] = 0 if G['year_inversions'] else 1
CLOSE[u'letters_def_three_used_two'] = 1 if (G['ex_letters_def'] == [u'F', u'G', u'H']
                                             and G['ex_letters'] == [u'F', u'G']) else 0
CLOSE[u'html_shell_none'] = 0 if (G['shell_pick'][3] or G['shell_pick'][4]) else 1
CLOSE[u'txt_no_tag'] = 0 if sum(G['tag_open'][:3]) else 1
CLOSE[u'split_tail_close'] = 0 if (G['lines_split_close'] or sum(G['tail_nl']) != NSRC) else 1
G.update(CLOSE)

# ---------- 恒等式: 从源码 ast 摘 Z(...) 再 eval ----------
ZID = []
for st in ast.parse(MS).body:
    c = st.value if isinstance(st, ast.Expr) else st
    if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == u'Z':
        ZID.append((ast.literal_eval(c.args[0]), ast.literal_eval(c.args[1])))


def ev(e):
    return eval(e.strip().replace(NL, u''), {u'NSRC': NSRC, u're': re}, {u'F': G, u'CLOSE': CLOSE})


assert len(ZID) == 78, len(ZID)
ZF = [w for e, w in ZID if ev(e)]
G['zid_fail'] = ZF
G['scalar_clos_n'] = len(ZID)
G['scalar_clos_sum'] = sum(1 for e, w in ZID if not ev(e))
G['list_clos_n'] = len([k for k in G if (u'_close' in k or u'_ledger' in k) and isinstance(G[k], list)])
G['x_ident_n'] = len(ZID)
# ---------- 与采集侧对账 ----------
AGREE, DIFF = [], []
PK = (u'bytes', u'chars', u'lines', u'nonblank', u'blank', u'cr', u'ff', u'ff_exact', u'maxlen',
      u'nonascii', u'bom', u'shell_page', u'shell_hdr', u'tag_open', u'tag_close',
      u'comment', u'br_tag', u'ent_total', u'hdr_dot2sp', u'hdr_dot1sp', u'hdr_nodot',
      u'hyphen_break', u'tone', u'tone_tot', u'tone_must_lc', u'kw_clause',
      u'terms', u'sender_smtp', u'smtp_client', u'spelling_queueing', u'spelling_queuing',
      u'retry_word', u'queue_word', u'time_digit_docs', u'tier_tot', u'years',
      u'obs_ids', u'upd_ids', u'pool_n', u'pool_tier', u'pair_share', u'pair_byte',
      u'pair_norm_only', u'pair_nonzero', u'union_incl', u's_pool_n', u's_pool_tier',
      u's_pair_share', u's_incl', u's_union_incl', u'rfc_hdr')
for k in PK:
    (AGREE if G[k] == MEA[k] else DIFF).append((k, G[k], MEA[k]))
G['shell_vs_pick_txt'] = [G['shell_pick'][i] for i in range(3)]
G['shell_replicate_pick'] = 1 if G['shell_vs_pick_txt'] == MEA['shell_n'][:3] else 0
G['shell_two_ruler_txt'] = 1 if [G['shell_n'][i] for i in range(3)] == MEA['shell_n'][:3] else 0
MEA_TIERP = MEA[u'tier_pats']
G['tier_pat_shared'] = sorted(set(MEA_TIERP) & set(G[u'tier_pats']))
G['tier_pat_pick_only'] = sorted(set(MEA_TIERP) - set(G[u'tier_pats']))
G['tier_pat_mk_only'] = sorted(set(G[u'tier_pats']) - set(MEA_TIERP))
PMAP = dict((w, j) for j, w in enumerate(MEA_TIERP))
G['tier_cross_agree'] = [1 if [MEA[u'tier_faces'][i][PMAP[w]] for i in range(NSRC)] == G[u'tier_' + k]
                         else 0 for k, w in TIER.items() if w in PMAP]
G['tier_cross_n'] = len(G['tier_cross_agree'])
G['exim_rule_pick'] = MEA[u'exim_rule_n']
G['exim_rule_mk'] = G['ex_rule_lines']
G['ex_sets_pick'] = MEA[u'exim_sets_n']
G['pf_def_pick'] = [MEA[u'pf_def_sec'][p] for p in PARAM6]
G['pf_chain_pick'] = [1 if x else 0 for x in MEA[u'pf_ge_chain']]
G['axis_pick_str'] = MEA[u'axis_str']
G['pair_max_pick'] = MEA[u'pair_max']
G['needle_table_pick'] = MEA[u'needle_n']
G['needle_table_mk'] = G['needle_n']
G['pick_ladder'] = [MEA[u'sn_strict_docs'], MEA[u'sn_fold_docs'], MEA[u'sn_sh_docs'],
                    MEA[u'sn_ds_docs'], MEA[u'sn_dj_docs']]
G['mk_ladder'] = [G[u'sn_strict_docs'], G[u'sn_fold_docs'], G[u'sn_sh_docs'],
                  G[u'sn_ds_docs'], G[u'sn_dj_docs']]
G['pick_agree'] = len(AGREE)
G['pick_diff'] = len(DIFF) + (G['tier_cross_n'] - sum(G['tier_cross_agree']))
G['pick_below_floor'] = MEA[u'below_floor']
G['giveup_band_pick'] = MEA[u'giveup_band_sec']

# ---------- 段落层: 组面 ⇎ 锚平面 ⇎ 窗平面 ----------
GRP = []
for i in range(NSRC):
    if ISH[i]:
        g = my_groups(T[i])
        assert g == mk_tag_groups(T[i]), (i, len(g), len(mk_tag_groups(T[i])))
        GRP.append(g)
    else:
        GRP.append([])
VNS = [num_lines(L[i]) for i in range(NSRC)]
VSH = [[(n, x) for n, x in VNS[i] if not is_shell_pick(x)] for i in range(NSRC)]
for i in range(3):
    assert [x for _, x in VSH[i]] == SHP[i], i
G['grp_n'] = [len(GRP[i]) if ISH[i] else len(VSH[i]) for i in range(NSRC)]
G['nonblank_pick'] = [len([1 for x in L[i] if pn2(x) != u'']) for i in range(NSRC)]
G['grp_glued'] = [len([1 for _, x in GRP[i] if glued(x)]) if ISH[i] else 0 for i in range(NSRC)]
G['grp_minus_nonblank'] = [G['grp_n'][i] - G['nonblank_pick'][i] for i in range(NSRC)]
GRP_SH = [len([1 for x in L[i] if pn2(x) != u'' and is_shell_pick(x)]) for i in range(3)]
G['shell_nonblank_pick'] = GRP_SH + [0, 0]
G['grp_close'] = [G['nonblank_pick'][i] - G['grp_n'][i]
                  - (G['grp_glued'][i] if ISH[i] else G['shell_nonblank_pick'][i]) for i in range(NSRC)]
# 锚平面: txt=非壳原行(带原行号) ⇎ html=组按粘面剥标签后的读数
ALN = [(VSH[i] if not ISH[i] else
       [(ln, u' '.join(my_detag(seg, u'').split())) for ln, seg in GRP[i]]) for i in range(NSRC)]
# 窗平面: 与 WIDE 逐字同果的 (行号, 折平片段); 只剩标签的组折平为空串, 要丢掉才不多出空格
PP = [([(n, u' '.join(x.split())) for n, x in VSH[i]] if not ISH[i] else
       [(ln, u' '.join(my_detag(seg, u' ').split())) for ln, seg in GRP[i]]) for i in range(NSRC)]
PP = [[p for p in pp if p[1] != u''] for pp in PP]
OFFS, LNS = [], []
for i in range(NSRC):
    assert u' '.join(x for _, x in PP[i]) == WIDE[i], i
    offs, lns, off, first = [], [], 0, True
    for ln, s in PP[i]:
        if not first:
            off += 1
        first = False
        offs.append(off)
        lns.append(ln)
        off += len(s)
    OFFS.append(offs)
    LNS.append(lns)
    for k, (ln, s) in enumerate(PP[i]):
        assert WIDE[i][offs[k]:offs[k] + len(s)] == s, (i, k, ln)


def line_of2(i, a):
    """偏移映回原行号: 段界表先排好, 再走 bisect_right(第二遍是线性游标一路扫到尾)"""
    return LNS[i][bisect.bisect_right(OFFS[i], a) - 1]


def blk2(i, start, end):
    a = vfind(WIDE[i], start)
    assert a >= 0, (LBL[i], start[:40])
    b = vfind(WIDE[i], end, a)
    assert b >= 0, (LBL[i], end[:40])
    e = b + len(end)
    return u' '.join(WIDE[i][a:e].split()), line_of2(i, a), line_of2(i, e - 1)


def ln_of2(i, nd, frm=0):
    a = vfind(WIDE[i], nd, frm)
    assert a >= 0, (LBL[i], nd[:40])
    return a, line_of2(i, a)


def ln_end2(i, nd, frm=0):
    """止针看它结束在哪一行: 72 列硬换行会把收束短语切成两行"""
    a = vfind(WIDE[i], nd, frm)
    assert a >= 0, (LBL[i], nd[:40])
    return a, line_of2(i, a + len(nd) - 1)


PB = [blk2(i, s, e) for i, s, e in PINS]
PTXT = [p[0] for p in PB]
G['blk_lo'] = [p[1] for p in PB]
G['blk_hi'] = [p[2] for p in PB]
G['blk_rows'] = [p[2] - p[1] + 1 for p in PB]
G['blk_chars'] = [len(p[0]) for p in PB]
G['blk_words'] = [len(p[0].split()) for p in PB]
PW = [p[0].lower().split() for p in PB]
G['blk_vocab'] = [len(Counter(x)) for x in PW]
G['blk_five_chars'] = sum(G['blk_chars'][:5])
G['blk_five_words'] = sum(G['blk_words'][:5])
G['tone_must'] = [ub3(p, u'MUST') for p in PTXT]
G['tone_may'] = [ub3(p, u'MAY') for p in PTXT]
G['tone_should'] = [ub3(p, u'SHOULD') for p in PTXT]
G['tone_must_not_blk'] = [ub3(p, u'MUST NOT') for p in PTXT]
G['blk_must_cur'] = [cnt(p, u'MUST') for p in PTXT]
G['blk_must_re'] = [rc(p, u'MUST') for p in PTXT]
G['blk_tone_ruler_close'] = (sum(abs(G['tone_must'][n] - G['blk_must_cur'][n]) for n in range(len(PB)))
                             + sum(abs(G['tone_must'][n] - G['blk_must_re'][n]) for n in range(len(PB))))
G['tone_in_blk'] = [G['tone_must'][n] + G['tone_may'][n] + G['tone_should'][n] for n in range(len(PB))]
# 词集容斥: 本遍走 Counter 的键域(减法不能直接用 Counter 差集: 那是按枚数抵消, 不是“另一侧没有”)
G['w_only_5321'] = len([k for k in set(PW[2]) if k not in set(PW[1])])
G['w_common_12'] = len(Counter(PW[1]) & Counter(PW[2]))
G['w_only_1123'] = len([k for k in set(PW[1]) if k not in set(PW[2])])
G['w_close_5321'] = G['w_only_5321'] + G['w_common_12'] - G['blk_vocab'][2]
G['w_close_1123'] = G['w_only_1123'] + G['w_common_12'] - G['blk_vocab'][1]
G['w_sym_diff'] = G['w_only_5321'] + G['w_only_1123']


def suf2(a, b):
    """共尾词数: 反向 zip 逐对吃(第二遍是下标 while 循环)"""
    n = 0
    for x, y in zip(reversed(a), reversed(b)):
        if x != y:
            break
        n += 1
    return n


def pre2(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


G['suf_1123_5321'] = suf2(PW[1], PW[2])
G['pre_1123_5321'] = pre2(PW[1], PW[2])
G['suf_queu_1123_5321'] = suf2(PW[5], PW[6])
G['pre_queu_1123_5321'] = pre2(PW[5], PW[6])
G['suf_giveup_1123_5321'] = suf2(PW[10], PW[11])
G['pre_giveup_1123_5321'] = pre2(PW[10], PW[11])
G['blk_same_1123_5321'] = 1 if PW[1] == PW[2] else 0
G['giveup_sent_same'] = 1 if PTXT[10] == PTXT[11] else 0
G['giveup_chars'] = [len(PTXT[10]), len(PTXT[11])]
G['queu_same'] = 1 if PTXT[5] == PTXT[6] else 0
G['blk_identical_chars'] = 1 if PTXT[1] == PTXT[2] else 0
G['ln_delay_1123'] = ln_of2(1, u'The sender MUST delay retrying')[1]
_p_g1 = ln_of2(1, u'Retries continue until the message is transmitted',
               vfind(WIDE[1], u'The sender MUST delay retrying'))
G['ln_giveup_1123'] = _p_g1[1]
G['ln_conf_head_1123'] = ln_of2(1, u'MUST be configurable', _p_g1[0])[1]
G['ln_conf_1123'] = ln_end2(1, u'algorithm MUST be configurable.', _p_g1[0])[1]
G['ln_delay_5321'] = ln_of2(2, u'The sender MUST delay retrying')[1]
_p_g2 = ln_of2(2, u'Retries continue until the message is transmitted',
               vfind(WIDE[2], u'The sender MUST delay retrying'))
G['ln_giveup_5321'] = _p_g2[1]
G['ln_conf_head_5321'] = ln_of2(2, u'MUST be configurable', _p_g2[0])[1]
G['ln_conf_5321'] = ln_end2(2, u'algorithm MUST be configurable.', _p_g2[0])[1]
G['delay_giveup_gap_1123'] = G['ln_giveup_1123'] - G['ln_delay_1123']
G['delay_giveup_gap_5321'] = G['ln_giveup_5321'] - G['ln_delay_5321']
G['giveup_conf_gap_1123'] = G['ln_conf_1123'] - G['ln_giveup_1123']
G['giveup_conf_gap_5321'] = G['ln_conf_5321'] - G['ln_giveup_5321']
G['conf_delay_span_1123'] = G['ln_conf_1123'] - G['ln_delay_1123']
G['conf_delay_span_5321'] = G['ln_conf_5321'] - G['ln_delay_5321']
# 同一枚止针的两把尺: 首字所在行 ⇎ 末字所在行
G['conf_straddle_1123'] = G['ln_conf_1123'] - G['ln_conf_head_1123']
G['conf_straddle_5321'] = G['ln_conf_5321'] - G['ln_conf_head_5321']
G['ln_hard_821'] = ln_of2(0, u'It is difficult to assign a meaning')[1]
G['ln_4yz_821'] = ln_of2(0, u'4yz Transient Negative')[1]
G['ln_5yz_821'] = ln_of2(0, u'5yz Permanent Negative')[1]
G['ln_thumb_821'] = ln_of2(0, u'A rule of thumb')[1]
G['hard_4yz_gap'] = G['ln_hard_821'] - G['ln_4yz_821']
G['yz_gap'] = G['ln_5yz_821'] - G['ln_4yz_821']
G['thumb_hard_gap'] = G['ln_thumb_821'] - G['ln_hard_821']
_p_rule = vfind(WIDE[3], u'default retry rule')
G['ln_rule_exim'] = ln_of2(3, G['ex_def_rule'], _p_rule)[1]
G['ln_rim_exim'] = ln_of2(3, u'retry_interval_max limits')[1]
G['ln_cut_exim'] = ln_of2(3, u'the cutoff time is four days.')[1]
G['ln_30min_exim'] = ln_of2(3, u'They happen every 30 minutes')[1]
G['rule_prompt_off'] = _p_rule
G['rule_prompt_line'] = line_of2(3, _p_rule)
G['rule_prompt_gap'] = G['ln_rule_exim'] - G['rule_prompt_line']
G['rule_first_off'] = vfind(WIDE[3], G['ex_def_rule'])
G['rule_first_line'] = line_of2(3, G['rule_first_off'])
G['rule_two_lines'] = G['ln_rule_exim'] - G['rule_first_line']
G['rule_rim_gap'] = G['ln_rule_exim'] - G['ln_rim_exim']
G['rim_cut_gap'] = G['ln_cut_exim'] - G['ln_rim_exim']
G['cut_30min_gap'] = G['ln_30min_exim'] - G['ln_cut_exim']
G['cut_30min_abs'] = abs(G['cut_30min_gap'])
_p_mql = ln_of2(4, u'Consider a message as undeliverable')
G['ln_mql_pf'] = _p_mql[1]
G['ln_minbo_pf'] = ln_of2(4, u'The minimal time between attempts')[1]
G['ln_zero_pf'] = ln_of2(4, u'Specify 0 when mail delivery should be tried only once', _p_mql[0])[1]
G['ln_zero_first_pf'] = line_of2(4, vfind(WIDE[4], u'tried only once'))
G['zero_repeats'] = rc(WIDE[4], u'tried only once')
G['mql_minbo_gap'] = G['ln_minbo_pf'] - G['ln_mql_pf']
G['zero_mql_gap'] = G['ln_zero_pf'] - G['ln_mql_pf']
G['zero_mql_abs'] = abs(G['zero_mql_gap'])
G['delay_shift_5321'] = G['ln_delay_5321'] - G['ln_delay_1123']
G['giveup_shift_5321'] = G['ln_giveup_5321'] - G['ln_giveup_1123']
G['shift_delta'] = G['delay_shift_5321'] - G['giveup_shift_5321']
G['hi_shift_delay'] = G['blk_hi'][2] - G['blk_hi'][1]
G['hi_shift_giveup'] = G['blk_hi'][11] - G['blk_hi'][10]
G['blk_five_rows'] = sum(G['blk_rows'][:5])
G['blk_rows_tot'] = sum(G['blk_rows'])
G['blk_words_tot'] = sum(G['blk_words'])
ANSET = [set(x for _, x in ALN[i]) for i in range(NSRC)]
ALND = [dict(ALN[i]) for i in range(NSRC)]
assert all(len(d) == len(ALN[i]) for i, d in enumerate(ALND))


def line_holds2(i, ln, nd):
    """行号尺复核: 拿行号回锚平面取那一行, 看针是否真落在这一行内(第二遍是逐行扫, 本遍查表)"""
    assert ln in ALND[i], (LBL[i], ln)
    return 1 if pn2(nd) in pn2(ALND[i][ln]) else 0


WRAPND = u'configurable.'
RT = [(1, G['ln_delay_1123'], u'The sender MUST delay retrying'),
      (1, G['ln_giveup_1123'], u'Retries continue until the message'),
      (1, G['ln_conf_1123'], WRAPND),
      (1, G['blk_hi'][1], WRAPND),
      (2, G['ln_delay_5321'], u'The sender MUST delay retrying'),
      (2, G['ln_giveup_5321'], u'Retries continue until the message'),
      (2, G['ln_conf_5321'], WRAPND),
      (2, G['blk_hi'][2], WRAPND),
      (0, G['ln_hard_821'], u'It is difficult to assign a meaning'),
      (0, G['ln_4yz_821'], u'4yz Transient Negative'),
      (0, G['ln_5yz_821'], u'5yz Permanent Negative'),
      (0, G['ln_thumb_821'], u'A rule of thumb')]
G['pin_rt'] = [line_holds2(i, ln, nd) for i, ln, nd in RT]
G['pin_rt_n'] = len(G['pin_rt'])
G['pin_rt_ok'] = sum(G['pin_rt'])
G['pin_rt_lbl'] = [LBL[i] for i, _, _ in RT]
G['pin_rt_src'] = [len([1 for i, _, _ in RT if i == n]) for n in range(NSRC)]
# 反向对照: 跨行短语的末字拿到它的首字行去验, 两份都该落空
G['pin_wrongline'] = sum([line_holds2(1, G['ln_conf_head_1123'], WRAPND),
                          line_holds2(2, G['ln_conf_head_5321'], WRAPND)])
G['sec_word'] = [cnt(WIDE[i], u'seconds') for i in range(NSRC)]
G['sec_word_rfc'] = sum(G['sec_word'][:3])
C2 = {}
C2[u'blk_tone_none_exim_pf'] = 1 if (G['tone_in_blk'][3] == 0 and G['tone_in_blk'][4] == 0) else 0
C2[u'blk_may_only_5321'] = 1 if (G['tone_may'][2] > 0 and G['tone_may'][1] == 0) else 0
C2[u'pin_rt_all'] = 1 if G['pin_rt_ok'] == G['pin_rt_n'] else 0
C2[u'pin_wrap_probe'] = 1 if G['pin_wrongline'] == 0 else 0
C2[u'sec_only_1123'] = 1 if (G['sec_word_rfc'] == 1 and G['sec_word'][0] == 0
                             and G['sec_word'][2] == 0 and G['sec_word'][3] == 0) else 0
C2[u'sec_html_gt_rfc'] = 1 if G['sec_word'][4] > G['sec_word_rfc'] else 0
C2[u'w_ledger_close'] = 0 if (G['w_close_5321'] or G['w_close_1123']) else 1
C2[u'blk_5321_longer'] = 1 if G['blk_chars'][2] > G['blk_chars'][1] else 0
C2[u'exim_rule_after_rim'] = 1 if G['rule_rim_gap'] > 0 else 0
C2[u'exim_rule_after_prompt'] = 1 if G['rule_prompt_gap'] > 0 else 0
C2[u'exim_rule_reprinted'] = 1 if G['rule_two_lines'] > 0 else 0
C2[u'hard_before_thumb_821'] = 1 if G['thumb_hard_gap'] > 0 else 0
C2[u'zero_after_mql_pf'] = 1 if G['zero_mql_gap'] > 0 else 0
C2[u'grp_ledger_close'] = 0 if sum(abs(x) for x in G['grp_close']) else 1
C2[u'giveup_inside_delay'] = 1 if (G['blk_lo'][10] > G['blk_lo'][1]
                                   and G['blk_lo'][11] > G['blk_lo'][2]) else 0
C2[u'queu_before_delay'] = 1 if (G['blk_lo'][5] < G['blk_lo'][1]
                                 and G['blk_lo'][6] < G['blk_lo'][2]) else 0
C2[u'exim_rim_before_four'] = 1 if (G['blk_lo'][3] < G['blk_lo'][8]
                                    and G['rule_prompt_line'] < G['ln_cut_exim']) else 0
C2[u'pf_mql_before_minbo'] = 1 if (G['blk_lo'][4] < G['blk_lo'][9] and G['mql_minbo_gap'] > 0) else 0
C2[u'blk_shift_equal'] = 1 if G['delay_shift_5321'] == G['giveup_shift_5321'] else 0
G.update(C2)

# ---------- 锚归属: 不读旁注, 从条目文件现推 ----------
TAGS, IDX = LBL, dict((t, n) for n, t in enumerate(LBL))
assert all(pn2(T[i]) == mk_pnorm(T[i]) for i in range(NSRC))
FAN = [pn2(T[i]) if not ISH[i] else pn2(my_detag(T[i], u'')) + u' #' + pn2(my_detag(T[i], u' '))
       for i in range(NSRC)]
TT = io.open(ENTRY, encoding='utf-8').read()
_hd = TT.index(u'⟪BabelTele⟫' + NL) + len(u'⟪BabelTele⟫' + NL)
enc = TT[_hd:TT.index(NL + NL + u'## ', _hd)]


def my_cites(s):
    """锚配对: 逐枚 '⟦' 手吃到 '⟩'(第二遍是一条 findall 正则)"""
    out, k = [], 0
    while True:
        a = s.find(u'⟦', k)
        if a < 0:
            return out
        b, c, d = s.find(u'⟧', a), s.find(u'⟨', a), s.find(u'⟩', a)
        assert 0 <= a < b < c < d, (a, b, c, d)
        assert s[a + 1:b] in TAGS, s[a + 1:b]
        out.append((s[a + 1:b], s[c + 1:d]))
        k = d + 1


CITES = my_cites(enc)
assert enc.count(u'⟨') == len(CITES) and enc.count(u'⟩') == len(CITES)
assert enc.count(u'⟦') == len(CITES) and enc.count(u'⟧') == len(CITES)
assert enc.find(u'⟧⟨⟦') < 0
ERR = [x for x in CITES if not pn2(x[1]) or pn2(x[1]) not in FAN[IDX[x[0]]]]
MISSLINE = [x for x in CITES if x[1] not in ANSET[IDX[x[0]]]]
DIS = []
for _, a in CITES:
    if a not in DIS:
        DIS.append(a)
HC = [tuple(i for i in range(NSRC) if pn2(a) and pn2(a) in FAN[i]) for a in DIS]
G['anchor_total'] = len(CITES)
G['anchor_distinct'] = len(DIS)
G['anchor_err'] = len(ERR)
G['anchor_single'] = len([h for h in HC if len(h) == 1])
G['anchor_cross'] = len([h for h in HC if 1 < len(h) < NSRC])
G['anchor_all5'] = len([h for h in HC if len(h) == NSRC])
G['checks'] = len(DIS) * NSRC
G['nsrc'] = NSRC
G['enc_chars'] = len(enc.replace(NL, u''))
for t in TAGS:
    G['tag_' + t] = len([x for x in CITES if x[0] == t])
G['contract_n'] = len(G) + 1
assert not ERR, ERR[:3]
assert not MISSLINE, MISSLINE[:3]
assert sum(G['tag_' + t] for t in TAGS) == G['anchor_total']
assert all(G['tag_' + t] > 0 for t in TAGS)
assert G['anchor_single'] + G['anchor_cross'] + G['anchor_all5'] == G['anchor_distinct']
assert all(len(h) < NSRC for h in HC)

# ---------- 逐值对账 ⇎ 恒等式与 DERIV 重跑 ----------
_jr = lambda x: json.loads(json.dumps(x))
NSV = dict(FLAT)
NSV.update(G)
B74V = lambda k, i=None: (NSV[k] if i is None else NSV[k][i])
ZV2 = [(e, w, eval(e, {}, {u'B74V': B74V})) for e, w in CH[u'zid']]
ZVFAIL = [w for e, w, r in ZV2 if r != 0]
assert not ZVFAIL, ZVFAIL[:4]
DFL = []
for kk, v in DER.items():
    try:
        g = eval(v, {}, {u'B74V': B74V})
    except Exception as e:
        DFL.append((kk, repr(e)))
        continue
    if str(g) != kk and repr(g) != kk:
        DFL.append((kk, v, str(g)))
MISS = [k for k in G if k not in FLAT]
BAD = [(k, _jr(G[k]), _jr(FLAT[k])) for k in G if k in FLAT and _jr(G[k]) != _jr(FLAT[k])]
UNCOVER = [k for k in FLAT if k not in G]
assert not DFL, DFL[:4]
assert not MISS, MISS[:6]
assert not UNCOVER, UNCOVER[:6]
assert not BAD, BAD[:6]
assert G['anchor_err'] == 0 and G['pick_diff'] == 0
assert sum(G['tier_cross_agree']) == G['tier_cross_n'] == 12
assert G['ladder_monotone'] == 1 and G['re_eq_cur'] == 1
assert sum(G['sh_minus_fold']) == 0 and sum(G['attr_loss']) == 0
assert G['pair_close'] == 0 and G['union_close'] == 0 and G['pool_tier_close'] == 0
assert G['apool_tag_close'] == 0 and G['apool_tier_close'] == 0 and G['axis_close'] == 0
assert G['s_union_close'] == 0 and G['s_pool_tier_close'] == 0 and G['s_pair_html'] == 0
assert G['tone_ruler_close'] == 0 and sum(G['tone_ledger']) == 0
assert G['lines_split_close'] == 0 and sum(G['tail_nl']) == NSRC
assert G['dead_needles'] == [] and G['neg_hit_widest'] == 0 and G['neg_hit_strict'] == 0
assert G['shell_ledger_close'] == 0 and G['shell_replicate_pick'] == 1
assert G['pin_rt_all'] == 1 and G['pin_wrap_probe'] == 1
assert G['grp_ledger_close'] == 1 and G['grp_glued'][3] == 0
assert G['w_ledger_close'] == 1 and G['blk_tone_ruler_close'] == 0
assert G['scalar_clos_n'] == G['scalar_clos_sum'] == len(CH[u'zid']) - 19 == 78
assert G['contract_n'] == len(FLAT) == 624
print(u'第四遍复算完成: 扁平 %d 键全覆盖 ⇎ 逐值不符 %d ⇎ 本遍独有 %d ⇎ 未复算 %d ｜ 标量恒等式 %d/%d ⇎ V 形 %d 条全真 '
      u'⇎ DERIV %d 键全对' % (len(FLAT), len(BAD), len(MISS), len(UNCOVER), G['scalar_clos_sum'],
                              G['scalar_clos_n'], len(ZV2), len(DER)))
# ---------- ⛓解读注 ----------
L2 = []
A = L2.append
A(u"第四遍(`corpus/_fill74.py`)换算法不换定义地重跑一遍: 行界由手写索引循环按 `\\n` 切(第二遍是 `str.split`, 采集侧是"
  u" `re.split`), 换行枚数走 `str.count` ⇎ 行数三档(切格数 ⇎ 换行数加一 ⇎ `splitlines()`)互相对拍; 折平走"
  u" `' '.join(s.split())`, 归一尺另走 `re.sub('\\s+',' ')` 档并逐样本与 `pnorm` 对拍; 剥标签不起正则, 改三趟字符串扫描"
  u" (注释趟 ⇎ `<br>` 趟 ⇎ `<…>` 趟, 区间由自写的 `_spans` 给出), 再照抄实体表 `SG`——整档断言"
  u" `my_detag == detag`(两枚 fill 各一次, 五份两档共十次); 组面自走一遍“切点只在标签/注释之外的换行”的保护掩码扫描,"
  u" 与 `tag_groups` 逐元组对拍; 偏移映回原行号走 `bisect_right`(第二遍是线性游标扫到尾), 段界定位把 `str.find` 换成"
  u" `re.compile(re.escape(针)).search(hay, frm)`; 针计数三档 `str.count` ⇎ `findall(re.escape)` ⇎ `findall('(?=针)')`"
  u" 差合计归零; 义务词整词档换成“按 alnum 切 token 后整串比对”、短语档换成 `finditer` 后验左右邻; Exim 时长尺换成"
  u" 一条 `fullmatch` 正则、Postfix 默认值尺换成 `finditer(名 + ' (default: ')` 捕获到 `)`; 池代数走 `Counter(len(v))`"
  u" 直方图与 `re.sub('-[ \\t]*','')` 的写法归一; 抬头字段走 `startswith` 加双空格切, 年份走“月名 token 紧跟四位数字"
  u" token”的相邻对档; 引用三式全换 `findall`; 锚归属走双轨(源标签紧接的原子引文: 一轨对锚平面逐行 membership,"
  u" 一轨对整篇归一串 substring); 恒等式与 DERIV 不重打算式——78 条标量式从 `_mkB74.py` 源码用 `ast` 摘 `Z(...)` 后在本遍"
  u" 读数上 eval, 97 条 V 形 ⇎ 207 条 DERIV 复算点从 `_b74checks.json` ⇎ `_deriv74.json` 回读 eval。壳谓词 `shell_line`"
  u" ⇎ `is_shell_pick`、剥标签实体表、`tag_groups`、58 枚针表 `SENT` ⇎ 12 族 `TIER` ⇎ 10 词 `TERMP` ⇎ 12 段 `PINS` 的"
  u" **定义**从源码 `ast`/`exec` 复用——要换的是量, 不是定义。")
A(u"本遍复算 %d 个键(扁平表 %d 键全覆盖 ⇎ 本遍独有 %d ⇎ 未复算 %d ⇎ 逐值不符 %d); SCAN 段登记的标量恒等式 %d 条在"
  u" 本注读数上重跑全为真(通过 %d) ⇎ `checks` 里的 V 形恒等式 %d 条(比 SCAN 段多 %d 条, 多的那批在 emit 段并进来)全真"
  u" ⇎ DERIV %d 条复算点重跑全对(引用 %d 处) ⇎ 与采集遍逐键横比 %d 键相符 ⇎ %d 键不符。" % (
      len(G), len(FLAT), len(MISS), len(UNCOVER), len(BAD), G['scalar_clos_n'], G['scalar_clos_sum'],
      len(ZV2), len(ZV2) - G['scalar_clos_n'], len(DER),
      sum(len(v.split(u'B74V(')) - 1 for v in DER.values()), G['pick_agree'], G['pick_diff']))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"行界⇎换页", u"手写索引循环切 `\\n` ⇎ `str.count` 数换行 ⇎ `splitlines()` 三档并立",
     u"原行 %s ⇎ 换行枚数 %s ⇎ splitlines %s ⇎ 换页符 %s 枚 ⇎ 末行带换行 %d 份" % (
         J(G['lines']), J(G['lines_nl']), J(G['lines_split']), J(G['ff']), sum(G['tail_nl'])),
     u"三档账 %d(行数=换行+1−末行换行+换页符, 逐份闭合); 判定 %d。" % (
         G['lines_split_close'], G['split_tail_close'])),
    (u"折平⇎归一", u"`' '.join(split())` 折平 ⇎ `re.sub` 空白折叠归一, 两尺逐样本对拍",
     u"面内码位 %s ⇎ 字节−码位差 %s ⇎ 全库回车 %s ⇎ NUL %s" % (
         J(G['chars']), J(G['byte_cp_delta']), J(G['cr']), J(G['nul'])),
     u"两份尺在五份全文上同值(断言级); 归一尺与 `pnorm` 逐份相等。"),
    (u"剥标签", u"三趟字符串扫描(注释 ⇎ `<br>` ⇎ `<…>`)代三条 `re.sub`, 实体表照抄",
     u"开标签 %s ⇎ 闭标签 %s ⇎ `<br>` %s 枚 ⇎ 实体 %s ⇎ 数字实体剥后仍留 %s 枚" % (
         J(G['tag_open']), J(G['tag_close']), J(G['br_tag']), J(G['ent_total']),
         J(G['ent_numeric_left'])),
     u"整档断言 `my_detag == detag` 五份×两档=%d 次全过 ⇎ `&lt;` 剥后残留 %d ⇎ 双逃 &amp; 剩 %d 枚(只在此侧)。" % (
         NSRC * 2, sum(G['ent_lt_left']), sum(G['ent_double_left']))),
    (u"五档面⇎针", u"面构造换 `' '.join(split())` ⇎ `bisect` 定位, `SENT` 表照抄不重打",
     u"名下针读到的枚数 %s ⇎ 五档逐行 %s ⇎ 折平 %s ⇎ 摘壳 %s ⇎ 断面 %s ⇎ 粘面 %s" % (
         J(G['needles_owned']), J(G['sn_strict_docs']), J(G['sn_fold_docs']), J(G['sn_sh_docs']),
         J(G['sn_ds_docs']), J(G['sn_dj_docs'])),
     u"死集 %s ⇎ 反向 %d 枚最宽档命中 %d ⇎ 摘壳掉枚 %d ⇎ 折行独有 %d 枚按份 %s ⇎ 正则档与游标档同值判定 %d。" % (
         G['dead_needles'], G['neg_n'], G['neg_hit_widest'], sum(G['sh_minus_fold']),
         G['fold_minus_strict_n'], J(G['fold_minus_strict_own']), G['re_eq_cur'])),
    (u"组面⇎壳账", u"自写保护掩码扫描代 `tag_groups`, 输出逐元组对拍; 跨行判定手工剥首尾换行",
     u"组数 %s ⇎ 非空行 %s ⇎ 差 %s ⇎ 跨行组 %s ⇎ 本遍壳 %s ⇎ 采集壳 %s" % (
         J(G['grp_n']), J(G['nonblank_pick']), J(G['grp_minus_nonblank']), J(G['grp_glued']),
         J(G['shell_n']), J(G['shell_pick'])),
     u"三本账逐份 %s ⇎ 闭合判定 %d ⇎ 两遍壳谓词分解(本遍多判 %s ⇎ 采集多判 %s)相加 %d ⇎ txt 侧复现判定 %d。" % (
         J(G['grp_close']), G['grp_ledger_close'], J(G['shell_mk_only']), J(G['shell_pick_only']),
         G['shell_ledger_close'], G['shell_replicate_pick'])),
    (u"行号尺", u"偏移→行号走 `bisect_right`; 复核表 `ALND` 由锚平面现建(第二遍逐行扫)",
     u"12 段起行 %s ⇎ 止行 %s ⇎ 行数 %s" % (
         J(G['blk_lo']), J(G['blk_hi']), J(G['blk_rows'])),
     u"独立行针 %d 枚回原行自验命中 %d(判定 %d) ⇎ 反向: 跨行短语末字拿到首字行验命中 %d(判定 %d) ⇎ 收束短语被硬换行切开 %d ⇎ %d 行。" % (
         G['pin_rt_n'], G['pin_rt_ok'], G['pin_rt_all'], G['pin_wrongline'], G['pin_wrap_probe'],
         G['conf_straddle_1123'], G['conf_straddle_5321'])),
    (u"语气", u"整词档=按 alnum 切 token 后整串比对 ⇎ 短语档=`finditer` 验左右邻(第二遍是游标 find+邻居判定)",
     u"五轨合计 %s ⇎ 裸 MUST %s ⇎ 小写 must %s ⇎ 段内 MUST %s" % (
         J(G['tone_tot']), J(G['must_bare']), J(G['tone_must_lc']), J(G['tone_must'])),
     u"手扫⇎游标⇎正则三轨逐轨逐份差合计 %d ⇎ 段内三把尺 %d ⇎ 五轨−裸−MUST NOT 账 %s ⇎ 零大写 MUST 的恰两份判定 %d。" % (
         G['tone_ruler_close'], G['blk_tone_ruler_close'], J(G['tone_ledger']), G['tone_zero_must_pair'])),
    (u"换算表⇎规则串", u"时长判定换 `fullmatch` 正则 ⇎ 阶梯走累加循环 ⇎ 默认值走 `finditer` 捕获",
     u"10 档秒 %s ⇎ Exim 规则串 %d 段(字母 %s, 文档另定义 %s)⇎档数 %d ⇎ 封顶 %d ⇎ 截止 %d ⇎ Postfix 六参数 %s" % (
         J(CVV), G['ex_def_sets'], J(G['ex_letters']), J(G['ex_letters_def']), G['ex_attempts_tot'],
         G['ex_rim_cap'], G['ex_def_span'], J(G['pf_def_sec'])),
     u"低于下限 %d 档 ⇎ 不低于 %d 档 ⇎ 相加−表长 %d ⇎ 窗两端命中 %d 处 ⇎ 队列寿命⇎回弹同值 %d ⇎ 300s×%d=下限。" % (
         G['cv_below_n'], G['cv_above_n'], G['cv_close'], G['band_edge_hits'], G['pf_bql_eq_mql'],
         G['cv_pf_x_by_floor'])),
    (u"段词集⇎共头共尾", u"词表走 `Counter` 键域 ⇎ 共头共尾走正向 zip ⇎ 反向 zip(第二遍是下标循环)",
     u"1123 段 ⇎ 5321 段: 独有 %d ⇎ %d 词 ⇎ 共有 %d ⇎ 对称差 %d ⇎ 共头 %d ⇎ 共尾 %d 词 ⇎ 给弃句 %d ⇎ %d 字符" % (
         G['w_only_1123'], G['w_only_5321'], G['w_common_12'], G['w_sym_diff'], G['pre_1123_5321'],
         G['suf_1123_5321'], G['giveup_chars'][0], G['giveup_chars'][1]),
     u"两侧容斥各自归零 %d ⇎ %d(判定 %d) ⇎ 段全同 %d ⇎ 句全同 %d ⇎ 队列清单那句共头 %d ⇎ 共尾 %d。" % (
         G['w_close_1123'], G['w_close_5321'], G['w_ledger_close'], G['blk_same_1123_5321'],
         G['giveup_sent_same'], G['pre_queu_1123_5321'], G['suf_queu_1123_5321'])),
    (u"池代数⇎写法分家", u"归属向量走 `Counter(len(v))` 直方图 ⇎ 配对走集合求交 ⇎ dehyph 换 `re.sub('-[ \\t]*','')` 一把尺",
     u"行池 %s 条分档 %s ⇎ 句池 %s 条分档 %s ⇎ 两两共用(行) %s ⇎ 锚候选 %s 条" % (
         G['pool_n'], J(G['pool_tier']), G['s_pool_n'], J(G['s_pool_tier']),
         J(G['pair_share']), G['apool_n']),
     u"容斥并集 %d ⇎ 行池闭合 %d ⇎ 句池闭合 %d ⇎ 分档闭合 %d ⇎ 锚池两本账 %d ⇎ %d; 归一同形 %d 串分四桶 %s ⇎ 桶账 %d。" % (
         G['union_incl'], G['union_close'], G['s_union_close'], G['pool_tier_close'],
         G['apool_tag_close'], G['apool_tier_close'], G['norm_only_set'], G['axis_str'], G['axis_close'])),
    (u"引用⇎谱系⇎措辞", u"三式全换 `findall` ⇎ 抬头走 `startswith`+双空格切 ⇎ 年份走相邻 token 对档",
     u"抬头年 %s ⇎ 年距 %s ⇎ 首末跨 %d 年 ⇎ 5321 头 %s ⇎ %s ⇎ 1123 面上 RFC-821 短横 %d 枚 ⇎ 空格式 %d 枚 ⇎ 十二族措辞共测 %d 条" % (
         J(G['years']), J(G['year_gaps']), G['year_span'], G['obs_line'][2], G['upd_line'][2],
         G['cite_821_hy_in_1123'], G['cite_821_in_1123'], G['tier_cross_n']),
     u"写法族账逐份 %s ⇎ 年代逆序 %d ⇎ 措辞族共测逐条同值 %s ⇎ 只在某一遍出现的模式串 %d ⇎ %d 条(不横比, 正则不同源)。" % (
         J(G['cite_forms_close']), G['year_inversions'], J(G['tier_cross_agree']),
         len(G['tier_pat_pick_only']), len(G['tier_pat_mk_only']))),
    (u"采集侧横比", u"本遍读数重新对一遍 `_b74meas.json`, 而不是抄第二遍的结论",
     u"同定义标量 %d 键相符 ⇎ %d 键不符 ⇎ 针表 %d 枚(采集)⇎ %d 枚(本遍) ⇎ 措辞共测 %d 条" % (
         G['pick_agree'], G['pick_diff'], G['needle_table_pick'], G['needle_table_mk'],
         G['tier_cross_n']),
     u"针表不横比(采集数字面针 ⇎ 本遍数面上导出的锚句), 五档阶梯两遍各 %s ⇎ %s; 壳账分解到行后再判复现(%s ⇎ 采集 %s)。" % (
         J(G['pick_ladder'][0]), J(G['mk_ladder'][0]), J(G['shell_n']), J(G['shell_pick']))),
    (u"锚双轨", u"归属: 锚平面逐行 membership ⇎ 计数: 整篇归一串 substring(两轨同判才计); 配对由 `⟦` 手吃到 `⟩`",
     u"引用 %d 处 ⇎ 去重 %d 枚 ⇎ 一源 %d ⇎ 二至四源 %d ⇎ 五源 %d ⇎ 错配 %d ⇎ 判定 %d 项 ⇎ 编码区 %d 字符" % (
         G['anchor_total'], G['anchor_distinct'], G['anchor_single'], G['anchor_cross'],
         G['anchor_all5'], G['anchor_err'], G['checks'], G['enc_chars']),
     u"按标签 %s 处(合计 %d=引用数) ⇎ 源数 %d: 每枚锚都同时过两轨, 非锚面零枚原行落空 ⇎ 一枚答话不可能五份同源(%d)。" % (
         J([G['tag_' + t] for t in TAGS]), sum([G['tag_' + t] for t in TAGS]), G['nsrc'],
         G['anchor_all5'])),
    (u"账架", u"恒等式算式从 `_mkB74.py` 的 SCAN 段用 `ast` 摘出后在本遍读数上 eval, 不重打一遍",
     u"标量恒等式 %d 条(通过 %d) ⇎ 清单式闭合 %d 项 ⇎ checks 里 V 形 %d 条全真 ⇎ DERIV %d 键 ⇎ 扁平 %d 键" % (
         G['scalar_clos_n'], G['scalar_clos_sum'], G['list_clos_n'], len(ZV2), len(DER), len(FLAT)),
     u"逐值不符 %d ⇎ 未复算 %d ⇎ 本遍独有 %d ⇎ 键数自证 %d=%d+1 ⇎ 判定项 %d 枚全数重算同值。" % (
         len(BAD), len(UNCOVER), len(MISS), G['contract_n'], len(G) - 1, len(CLOSE) + len(C2))),
]
for r in rows:
    for c in r:
        assert u'|' not in c and c.count(u'`') % 2 == 0, r[0]
    A(u"| %s | %s | %s | %s |" % r)
A(u"")
A(u"### 本注的判断")
A(u"五份给的其实不是“三个不同的数”, 而是三种不同**类型**的答案, 而且这个类型差在字节上可数: 821 只交付类别"
  u"(⟦821⟧⟨4yz Transient⟩ 与 5yz 相距 %d 行)并当场自认“难定 transient”(⟦821⟧⟨It is difficult to assign a meaning⟩ 距前者 %d 行, "
  u"经验法则再后 %d 行), 它全份 retry 族 %d 枚 ⇎ queue 族 %d 枚 ⇎ 大写五轨只有 SHOULD %d ⇎ MAY %d, 小写 must 却有 %d 枚——"
  u"它描述的是协议对答, 不是运维日程; 1123 第一次把日程写成三句义务(下限那句在 1123 全篇 %d 枚 ⇎ “MUST be configurable”全篇 %d 枚, "
  u"而主答段本身只 %d 词), "
  u"5321 逐字收下(共头 %d 词 ⇎ 共尾 %d 词)却只多留一枚 MAY; 两份 MTA 一枚义务词也不给(段内三轨合计 %d ⇎ %d), 给的是能算的数——"
  u"Exim 把整份日程压进一条规则串 %s(%d 段 %d 档 %d 秒), Postfix 把日程摊成六个参数的默认值 %s。所以“多久再试一次”的五种答法, "
  u"在本库字节上是: 类别 ⇎ 下限 ⇎ 逐字继承+放宽一句 ⇎ 可解析阶梯 ⇎ 参数表, 而不是五个数。" % (
      G['yz_gap'], G['hard_4yz_gap'], G['thumb_hard_gap'], G['retry_word'][0], G['queue_word'][0],
      G['tone'][0][3], G['tone'][0][4], G['tone_must_lc'][0], G['tier_floor_30min'][1], G['tier_configurable'][1],
      G['blk_words'][1], G['pre_1123_5321'], G['suf_1123_5321'], G['tone_in_blk'][3], G['tone_in_blk'][4],
      G['ex_def_rule'], G['ex_def_sets'], G['ex_attempts_tot'], G['ex_def_span'], J(G['pf_def_sec'])))
A(u"“什么时候不再试”这一问只有两份答得到秒: Exim 的截止 %d 秒正落在 1123 那句“至少 4-5 天”的下端 ⇎ Postfix 的 "
  u"maximal_queue_lifetime %d 秒落在上端(窗两端各被一份踩住, 命中 %d 处, 判定 %d/%d), 三份 RFC 一个也不给确切时刻"
  u"——“cutoff”这个字样在 RFC 面上 %d ⇎ %d ⇎ %d 枚, 只在 Exim 面 %d 枚。换算表 %d 档里有 %d 档低于 1123 的下限(60 ⇎ 300 ⇎ 300 ⇎ 900 秒), "
  u"即两份 MTA 的**首档**都比主机要求的下限勤得多, 差别被阶梯吃掉: Exim 的 G 段 %d 档几何级数(倍数 %s)走到 %d 秒才停, "
  u"Postfix 则用 minimal_backoff⇎maximal_backoff(300 ⇎ 4000 秒)与 queue_run_delay(300 秒)三档链把退避显式化(链上判定 %s)。"
  u"于是“放弃”的语义分家是可数的: 放弃=不再入队(Postfix 的参数说明 ⟦postfix⟧⟨Consider a message as undeliverable⟩)⇎"
  u"放弃=截止时刻(Exim ⟦exim⟧⟨the cutoff time is four days.⟩, 该句距封顶句 %d 行 ⇎ 距 30 分钟示例 %d 行)⇎放弃=“一般要 4-5 天”"
  u"的经验值(1123/5321, 其给弃句在两份各占 %d ⇎ %d 字符, 共头 %d 词而共尾 %d 词——同句不同尾)。" % (
      G['ex_def_span'], G['pf_def_sec'][0], G['band_edge_hits'], G['ex_cutoff_in_band'],
      G['pf_life_in_band'], G['word_cutoff'][0], G['word_cutoff'][1], G['word_cutoff'][2],
      G['word_cutoff'][3], len(CVV), G['cv_below_n'], G['ex_g_steps'], J(G['ex_def_mults']),
      G['ex_g_total'], J(G['pf_chain']), G['rim_cut_gap'], G['cut_30min_abs'],
      G['giveup_chars'][0], G['giveup_chars'][1], G['pre_giveup_1123_5321'], G['suf_giveup_1123_5321']))
A(u"谱系声明 ⇎ 字面共有在本遍对不齐, 这是第五遍才显形的一条: 5321 抬头只写 ⟦5321⟧⟨Obsoletes: 2821⟩ ⇎ ⟦5321⟧⟨Updates: 1123⟩, "
  u"但句尺上它与 821 共用 %d 句 ⇎ 与 1123 只共用 %d 句(行尺 %d ⇎ %d 条)——它名义上更新的那份, 字面共有量只有它没提的 821 的一半; "
  u"4yz/5yz 那套类别语言是直接从 821 搬的, 而“重试下限”那段才走 1123。两把尺的差本身是版式的物证: 同两对, 行尺→句尺各增益 "
  u"%d ⇎ %d 条(72 列硬换行把一句切成多行, 行尺看不见跨行的同文); 两份 MTA 与三份 RFC 之间共用句 %d 句 ⇎ 共用行 %d 条——"
  u"同一句话在规范面与手册面上从来没有同形过, 但 Exim 自家面上就印着两条不同的 `* *` 规则行(%d 枚 ⇎ 去重 %d 枚, 前两段逐字"
  u"相同只差末档 `%s` ⇎ `%s`), 而“默认规则”那一条在面上只印 %d 处: 它就排在提示行后 %d 行, 与自己首处差 %d 行。"
  u"搬字量的口径一变就翻倍, 所以本条不用“谁抄了谁”"
  u"而用“两把尺给出的序是否一致”: 821·5321 > 1123·5321 在行尺(29>2)与句尺(41>19)都成立, 序稳 ⇎ 而 5321 的抬头对共有量最大的那一头"
  u"(821)只字不提, 只把 1123 写进 ⟦5321⟧⟨Updates: 1123⟩。" % (
      G['s_pair_821_5321'], G['s_pair_1123_5321'], G['pair_821_5321'], G['pair_1123_5321'],
      G['s_ruler_gain_821_5321'], G['s_ruler_gain_1123_5321'], G['s_pair_html'],
      sum(G['pair_share'][n] for n, (a, b) in enumerate(PAIRS) if (a >= 3) != (b >= 3)),
      G['ex_star_star_rules'], G['ex_star_star_distinct'], OTHER_RULE, DEF_RULE,
      DEF_HITS, G['rule_prompt_gap'], G['rule_two_lines']))
A(u"术语换代也能落到枚数上, 且换代点唯一: sender-SMTP %s ⇎ receiver-SMTP %s ⇎ SMTP client %s——旧名在 821 满页(32 ⇎ 41 枚), "
  u"1123 减半, 5321 只剩 %d ⇎ %d 枚而 SMTP client 起 %d 枚, Postfix 直接沿用新名 %d 枚; 拼法也分家(queueing %s ⇎ queuing %s), "
  u"5321 一份之内两种拼法并存(%d ⇎ %d 枚)。同一节里的义务词也在换代: 1123 段内 SHOULD %d ⇎ MUST %d ⇎ MAY 0, 5321 段内 %d ⇎ %d ⇎ %d, "
  u"多出的那一枚 MAY 正是它相对 1123 的唯一语义增补(⟦5321⟧⟨may be appropriate to protect the host⟩), 19 枚新词与 2 枚失踪词的"
  u"对称差 %d 词把这次“搬家不是复制”钉住; 而两份 MTA 段内三轨全零 ⇎ 全篇语气 Exim %d 枚 ⇎ Postfix %d 枚——手册不谈义务, 只谈默认值。" % (
      J(G['sender_smtp']), J([x[3] for x in G['terms']]), J(G['smtp_client']), G['sender_smtp'][2],
      G['terms'][2][3], G['smtp_client'][2], G['smtp_client'][4], J(G['spelling_queueing']),
      J(G['spelling_queuing']), G['spelling_queueing'][2], G['spelling_queuing'][2], G['tone_should'][1],
      G['tone_must'][1], G['tone_should'][2], G['tone_must'][2], G['tone_may'][2], G['w_sym_diff'],
      G['tone_tot'][3], G['tone_tot'][4]))
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"五份文件在 RFC Editor 上的此刻状态(821 ⇎ 1123 是否已被标 Historic、5321 是否有后续勘误、被 5321 废止的 2821 自己的现行文本)⇎"
  u" 现网 Exim/Postfix 装机到底按什么参数跑(在库只有手册默认值, 配置覆盖不在库内)⇎ 镜像页两个时间戳 2024-03-06T ⇎ 2025-07-19T "
  u"是何时生成的 ⇎ Exim 规则串里 H 档(文档定义了 %d 种字母, 默认串只用 F ⇎ G)在别的版本文档里是否被默认启用 ⇎ "
  u"Postfix 六参数之外还有哪些参数同样影响重试(只点了表上六枚)——这些都要在库外字节或实时状态, 本库五份文件给不出判据。" % (
      len(G['ex_letters_def'])))
NEW = u"## ⛓解读注" + NL + NL + NL.join(L2) + NL
_i2 = TT.index(u"## ⛓解读注")
out = TT[:_i2] + NEW
assert out.count(u"## ⛓解读注") == 1
T2 = ENTRY + u'.tmp'
io.open(T2, 'w', encoding='utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"⛓解读注 已写入 %s ｜ 表 %d 行 ⇎ 注区 %d 字符 ⇎ 复算 %d 键 ⇎ 不符 %d ⇎ 独有 %d ⇎ 未复算 %d ⇎ "
      u"恒等式 %d/%d ⇎ V 形 %d 条 ⇎ DERIV %d 键全对"
      % (ENTRY, len(rows), len(NEW), len(G), len(BAD), len(MISS), len(UNCOVER),
         G['scalar_clos_sum'], G['scalar_clos_n'], len(ZV2), len(DER)))
