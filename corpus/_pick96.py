# -*- coding: utf-8 -*-
"""
_pick96.py —— B96 的选源记录(此文档即审计口径的源头说明)⇎ 第二套独立实现(B 侧量测)

【运行】python -X utf8 corpus/_pick96.py
   前置: 先跑 python -X utf8 corpus/_mkB96.py(它写 corpus/_tmp96_measA.json 与 corpus/_atoms96.txt)
   本遍: 用另一套机制把同一批键重算, 逐键与 A 侧对账, 写 corpus/_b96meas.json(每键 [A 值, B 值])
   后续: 再跑一遍 _mkB96.py(它读对账件发射)⇒ _mk96emit.py ⇒ _wire96.py ⇒ _fill96.py

【为什么是这一篇(2026-10-25 本地实测, 全部 curl, 零凭据)】
 1) 池子与通路(实测状态码 ⇎ 字节数, 现跑现记):
    · CourtListener —— 用户点名排除(已知被墙), 本轮未发起请求。
    · https://www.federalregister.gov/documents/full_text/text/2026-10-26/2026-21821.txt
      → HTTP 404(错误页 4569 字节)——FR 官方的 .txt 全文端点对本篇不可用, 弃。
    · https://www.federalregister.gov/api/v1/documents.json → HTTP 200;
      fields[]=agency ⇒ 400 {"field 'agency' not valid"}; agencies[]=faa ⇒ 400;
      必须写整 slug(federal-aviation-administration / securities-and-exchange-commission /
      food-and-drug-administration / federal-communications-commission)。
    · https://www.govinfo.gov/content/pkg/FR-2026-10-26/html/2026-21821.htm
      → HTTP 200, 41139 字节的 <pre> 块 ⇒ 选定通路(剥标签 + 实体还原, 保留 FR 硬换行)。
 2) 候选篇目(同一 API 的现量计数):
    · FAA: 2026-10-01 起 38 条 RULE;最近一篇 2026-21590(General Electric 发动机适航指令,
      91 FR 66631, 2026-10-22,govinfo htm 30870 字节)——与 B87 同机构同文种(适航指令), 排重弃。
    · SEC: 2026-09-01 起仅 3 条 RULE;最近 2026-20461(Adoption of Updated EDGAR Filer Manual,
      91 FR 63476)——正文只引用外部手册, 自身规则链稀薄, 弃。
    · FDA: 2026-09-01 起 22 条;最近 2026-20979(动物饲料添加剂, 91 FR 65109,htm 11013 字节)
      ——单项添加剂许可, 没有时限/词表/撤销机制这类可执行硬字段, 弃。
    · NIST: 2026-09-01 起 0 条;且仓库已用 FIPS 202(corpus/raw/fips202.html), 弃。
    · FCC: 2026-10 期 42 条文档;2026-10-26 当天两条 RULE:
      2026-21821(Enhancing the Ability of Consumers To Control the Robocalls, 91 FR 67214-67219,
      htm 41139 字节)⇎ 2026-21808(Closed Captioning of Video Programming, 91 FR 67220,htm 30112 字节)。
 3) 选定 2026-21821 的理由:
    · 时间: 刊发日 2026-10-26, 本地 2026-10-25T14:25:33 抓得全文(govinfo 提前一日挂出)⇒ 截止后专业信息。
    · 一手性: 终规本体即 47 CFR 64.1200(a)(9)(iii)(A),(10)-(12) 的修订条文, 外加序文与 FRFA;
      同批配套的拟规 2026-21820(FNPRM)尚未定稿 ⇒ 只有本篇是可执行文本。
    · 规则密度: 撤销权⇒专属方式三选⇒七枚标准词⇒十个工作日上限⇒五分钟确认推定⇒可反驳推定
      ⇒范围分档⇒金融机构可靠来源⇒生效链⇒授权链, 共 chain_n 枚硬字段针;
      另有两张表可按行尾三格现算复验(round(100×小家/总家, 2))。
    · 篇幅: 剥壳后正文 40257 字符, 折平 37769 字符 ⇎ 5482 词 ⇎ 698 硬换行行 ——
      FR 硬换行让"严格档 ⇎ 容行档"两把尺有意义(16 枚针只有 1 枚完整落在单行内)。
 4) 仓库排重: grep corpus/raw/ 与 corpus/babeltele/ ——FCC/robocall 此前未被任何条目使用
    (在库的是 FAA 适航指令、OCC 稳定币条文、FIPS 202、CFTC 掉期等)。

【与 _mkB96.py(A 侧)的机制差异(逐条, 共 12 处;差异只换算法不换定义)】
 1. 行式: A 用 BODY.split('\\n') 列表 ⇎ B 用 BODY.splitlines() + 尾换行单独判补 lines_nl。
 2. 折平面: A 用 ' '.join(BODY.split()) ⇎ B 用逐字符状态机切非空白游程再拼接, 并由"逐行折平后滤空"二次拼接同面(两条构造必须同值)。
 3. 空白游程: A 逐字符 isspace() 计游程 ⇎ B 先数全部游程再减首游程 ⇎ 面尺 ws_body 由 chars_body 减词长和反推。
 4. 子串档: A 用 str.count ⇎ B 手写 find 游标环(非重叠)。
 5. 词形档: A 用环视正则 (?<![0-9a-z])kw(?![0-9a-z]) ⇎ B 逐候选位置手工取左右邻字判边界(命中跳 len, 未中跳 1)。
 6. 词次/唯一词形: A 用 re.findall + set() ⇎ B 用逐字符白名单状态机 + dict 计数 + 排序后"相邻不等才留"去重。
 7. 句节: A 用 re.split('(?<=[.!?]) ') ⇎ B 逐字符扫句末标点且后邻空格才置切点, 再按切片判空。
 8. 最宽档 pnorm: A 四段正则链 ⇎ B 单遍逐字符(引号删除表 ⇒ 连字符映射表 ⇒ 有序码位白名单 ⇒ 空白折一)。
 9. 严格档 ⇎ 跨行档: A 逐行游标环数针(只看单行面) ⇎ B 折平时同步建"逐字符行号表", 一次游标环按命中首末字符的行号分档(可容跨三行以上的针), 再与逐行 split 计数 ⇎ 相邻两行拼接跨界计数互检。
10. 表格行: A 用正则 \\s\\d{6}\\s ⇎ B 按空白切格后逐格验"长度 6 且全数字"。
11. 百分比复算: A 用 round(100*s/t, 2) 浮点差 <0.005 ⇎ B 纯整数判据 2*|10000*s − pc_h*t| < t(pc_h 由字符串手工拆成百分位整数)。
12. 区域界/表位: A 用 next(i for …) ⇎ B 手写 while 循环找第一个满足条件的行下标。
"""
import io
import json
import os
import re

RAW = u'corpus/raw/late96/fcc_2026-21821.txt'
MEASA = u'corpus/_tmp96_measA.json'
MEAS = u'corpus/_b96meas.json'
ATOMFILE = u'corpus/_atoms96.txt'

DIG = set(u'0123456789')
LOW = set(u'abcdefghijklmnopqrstuvwxyz')
UPP = set(u'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
ALN = DIG | LOW | UPP
WSTAB = (u' \t\n\r\x0b\x0c\x1c\x1d\x1e\x1f\x85\xa0'
         u'\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a'
         u'\u2028\u2029\u202f\u205f\u3000')       # 显式空白码位表(A 侧直接调 ch.isspace())
WSCH = set(WSTAB)
QUO = set(u'\u2019\u2018\'`\u00b4')
HYP = set(u'\u2010\u2011\u2012\u2013\u2014\u2015\u2212-')


def tok_runs(s):
    """B 侧词游程: 逐字符扫非空白段(不用 split)。"""
    out, buf, inw = [], [], False
    for ch in s:
        if ch in WSCH:
            if inw:
                out.append(u''.join(buf))
                buf, inw = [], False
        else:
            buf.append(ch)
            inw = True
    if inw:
        out.append(u''.join(buf))
    return out


def pnorm_b(s):
    """最宽档单遍实现: 引号删 ⇒ 连字符归一 ⇒ 码位白名单 ⇒ 空白折一。"""
    out, prev_sp = [], True
    for ch in s.lower():
        if ch in QUO:
            continue
        if ch in HYP:
            nx = u'-'
        elif ch in DIG or ch in LOW or (u'\u4e00' <= ch <= u'\u9fff') or ch == u' ' or ch == u'.':
            nx = ch
        else:
            nx = u' '
        if nx == u' ':
            if not prev_sp:
                out.append(u' ')
            prev_sp = True
        else:
            out.append(nx)
            prev_sp = False
    return u''.join(out).strip()


def cnt_sub_b(needle, face):
    """子串档: find 游标环, 非重叠(A 侧用 str.count)。"""
    n = needle.lower()
    c, k = 0, 0
    L = len(n)
    while True:
        j = face.find(n, k)
        if j < 0:
            return c
        c += 1
        k = j + L


def cnt_tok_b(needle, face):
    """词形档: 候选位置逐一取左右邻字判边界(等价环视正则, 手工实现)。"""
    n = needle.lower()
    L = len(n)
    c, k = 0, 0
    while True:
        j = face.find(n, k)
        if j < 0:
            return c
        a = face[j - 1] if j > 0 else u''
        b = face[j + L] if j + L < len(face) else u''
        if (a not in ALN) and (b not in ALN):
            c += 1
            k = j + L
        else:
            k = j + 1
    return c


def num_runs(s):
    """数字游程: 起于数字, 逗号/点号仅当后跟数字才续吃(A 侧用正则 \\d[\\d,]*(?:\\.\\d+)? )。"""
    out = []
    i, N = 0, len(s)
    while i < N:
        if s[i] in DIG:
            buf = [s[i]]
            i += 1
            while i < N:
                if s[i] in DIG:
                    buf.append(s[i])
                elif s[i] in u',.' and i + 1 < N and s[i + 1] in DIG:
                    buf.append(s[i])
                else:
                    break
                i += 1
            out.append(u''.join(buf))
        else:
            i += 1
    return out


def cents(x):
    """'1,234.56' ⇎ '99.9' ⇎ '7' ⇒ 百分位整数(纯字符串拆, 不走 float)。"""
    x = x.replace(u',', u'')
    if u'.' in x:
        a, b = x.split(u'.', 1)
    else:
        a, b = x, u''
    b = (b + u'00')[:2]
    return int(a) * 100 + int(b)


def sent_split(face):
    """句节: 逐字符扫, 标点 ∈ .!? 且后邻空格 ⇒ 该空格前为切点。"""
    cuts, i, N = [], 0, len(face)
    while i < N - 1:
        if face[i] in u'.!?' and face[i + 1] == u' ':
            cuts.append(i + 1)
            i += 2
        else:
            i += 1
    segs, k = [], 0
    for c in cuts:
        segs.append(face[k:c])
        k = c
    segs.append(face[k:])
    return [s for s in segs if s.strip()]


def dedup_sorted(xs):
    """排序后相邻不等才留(A 侧用 set)。"""
    y = sorted(xs)
    out = []
    for x in y:
        if not out or out[-1] != x:
            out.append(x)
    return out


def first_index(pred, seq):
    i = 0
    for x in seq:
        if pred(x):
            return i
        i += 1
    return -1


# —— 面: 两套构造互检 ——
raw = io.open(RAW, encoding='utf-8', errors='replace').read()
cut = raw.find(u'\n\n')
BODY = raw[cut + 2:]
SL = BODY.splitlines()                       # 差异 1
LINES = SL + [u''] if BODY.endswith(u'\n') else SL
NL = [u' '.join(r) for r in [tok_runs(l) for l in SL]]        # 逐行折平(B 侧游程)
NE = [x for x in NL if x]
FACE_A = u' '.join(tok_runs(BODY))           # 差异 2: 状态机切词再拼
FACE_B = u' '.join(NE)                       # 差异 2 的第二条构造路径: 逐行折平再拼
assert FACE_A == FACE_B, u'B 侧两条折平构造不同面'
FACE = FACE_A
LOWF = FACE.lower()
PN = pnorm_b(FACE)


def fold_map(lines):
    """差异 9: 折平面 ⇎ 逐字符行号表一起构造(每枚接缝空格记它右侧那行的行号)。"""
    chs, lmap = [], []
    for idx, l in enumerate(lines):
        for w in tok_runs(l):
            if chs:
                chs.append(u' ')
                lmap.append(idx)
            chs.append(w)
            lmap.extend([idx] * len(w))
    return u''.join(chs), lmap


FACE_M, LINEOF = fold_map(SL)
assert FACE_M == FACE, u'B 侧带行号表的折平结果与面尺不合'
assert len(LINEOF) == len(FACE), u'B 侧行号表长度与面长不合'


def occ_tiers(needle):
    """一次游标环扫折平面, 用行号表把命中分成 严格档(首末同 line)⇎ 跨行档(含跨三行以上)。"""
    n = needle.lower()
    L = len(n)
    st = xl = 0
    k = 0
    while True:
        j = LOWF.find(n, k)
        if j < 0:
            return st, xl
        a = LINEOF[j]
        b = LINEOF[j + L - 1]
        if a >= 0 and a == b:
            st += 1
        else:
            xl += 1
        k = j + L

G = {}
chars_body = len(BODY)
toks = tok_runs(BODY)
words_flat = len(toks)
ws_all = 1 if BODY[:1] in WSCH else 0
_k = 1
while _k < chars_body:                       # 差异 3: 游程"起始位"计数
    if BODY[_k] in WSCH and BODY[_k - 1] not in WSCH:
        ws_all += 1
    _k += 1
ws_runs = ws_all - (1 if BODY[:1] in WSCH else 0)
trailing = 1 if BODY[-1:] in WSCH else 0
ws_runs_interior = ws_runs - trailing
G['chars_body'] = [chars_body]
G['chars_flat'] = [len(FACE)]
G['ws_body'] = [chars_body - sum(len(w) for w in toks)]       # 差异 3: 反推
G['ws_runs'] = [ws_runs]
G['ws_runs_interior'] = [ws_runs_interior]
G['flat_identity_gap'] = [chars_body - G['ws_body'][0] + ws_runs_interior - len(FACE)]
G['words_flat'] = [words_flat]
G['words_line_sum'] = [sum(len(tok_runs(l)) for l in SL)]
G['words_line_gap'] = [G['words_line_sum'][0] - words_flat]
G['lines_nl'] = [BODY.count(u'\n') + 1]
G['lines_sl'] = [len(SL)]
G['lines_tail_nl'] = [1 if BODY.endswith(u'\n') else 0]
G['lines_nonblank'] = [len([x for x in NL if x])]
G['lines_blank'] = [G['lines_nl'][0] - G['lines_nonblank'][0]]
_ml = 0
for l in LINES:
    if len(l) > _ml:
        _ml = len(l)
G['line_longest'] = [_ml]

# —— 词次 ⇎ 唯一词形: 逐字符白名单状态机 + dict 计数 ——
_tk, _buf = [], []
CLS = set(DIG) | set(LOW) | set([u"'"])
for ch in LOWF + u' ':
    if ch in CLS:
        _buf.append(ch)
    elif _buf:
        _tk.append(u''.join(_buf))
        _buf = []
cnt_map = {}
for w in _tk:
    cnt_map[w] = cnt_map.get(w, 0) + 1
G['tokens_total'] = [len(_tk)]
G['tokens_distinct'] = [len(cnt_map)]
G['tokens_repeat'] = [G['tokens_total'][0] - G['tokens_distinct'][0]]
G['tokens_vs_words_gap'] = [G['tokens_total'][0] - words_flat]
G['tokens_sum_close'] = [sum(cnt_map.values()) - G['tokens_total'][0]]
assert all(w for w in _tk), u'B 侧词形状态机切出了空 token'
assert sum(len(w) for w in _tk) <= len(LOWF), u'B 侧词形切片总长超过面长'
assert G['tokens_repeat'][0] + G['tokens_distinct'][0] == G['tokens_total'][0], u'B 侧词次账不合'

_a = _u = _m = _p = 0
for w in toks:
    hl = hd = False
    for ch in w.lower():
        if ch in LOW:
            hl = True
        elif ch in DIG:
            hd = True
    if hl and hd:
        _m += 1
    elif hd:
        _u += 1
    elif hl:
        _a += 1
    else:
        _p += 1
G['word_alpha'] = [_a]
G['word_num'] = [_u]
G['word_mixed'] = [_m]
G['word_punct'] = [_p]
G['word_shape_gap'] = [_a + _u + _m + _p - words_flat]

# —— 区域档(差异 12: while 找界)——
ir = -1
_i = 0
for x in LINES:
    if x.strip() == u'Final Rules':
        ir = _i
        break
    _i += 1
assert ir >= 0, u"B 侧找不到 'Final Rules' 分界行"
PRE = u' '.join([x for x in NL[:ir] if x]).lower()
RULE = u' '.join([x for x in NL[ir:] if x]).lower()
G['rule_start_line'] = [ir]
G['lines_pre'] = [ir]
G['lines_rule'] = [G['lines_nl'][0] - ir]
G['lines_region_gap'] = [ir + G['lines_rule'][0] - G['lines_nl'][0]]
G['chars_flat_pre'] = [len(PRE)]
G['chars_flat_rule'] = [len(RULE)]
G['words_flat_rule'] = [len([w for w in RULE.split(u' ') if w])]

SUB_KW = [u'consent', u'revocation', u'revoke', u'revocations', u'revocation request', u'revoke all',
          u'exclusive means', u'exclusive', u'caller', u'callers', u'called party', u'text message',
          u'robocall', u'informational', u'telemarketing', u'advertisement', u'business days',
          u'ten business days', u'reasonable time', u'reasonable means', u'reasonable manner',
          u'rebuttable presumption', u'totality of circumstances', u'financial institution',
          u'reliable source', u'prior express consent', u'prior express written consent',
          u'64.1200', u'tcpa', u'commission', u'cgb', u'enforcement bureau',
          u'reassigned numbers database', u'paperwork reduction act', u'congressional review act',
          u'regulatory flexibility act', u'small business administration', u'delegate', u'delegation',
          u'standardized words', u'confirmation', u'effective', u'synopsis', u'commenter',
          u'amend', u'revising', u'supersede', u'further notice of proposed rulemaking', u'end']
for k in SUB_KW:
    G['n_sub_' + k.replace(u' ', u'_')] = [cnt_sub_b(k, LOWF)]
REG_KW = [u'consent', u'revocation request', u'exclusive means', u'caller', u'text message',
          u'financial institution', u'revoke', u'robocall']
for k in REG_KW:
    a, b = cnt_sub_b(k, PRE), cnt_sub_b(k, RULE)
    kk = k.replace(u' ', u'_')
    G['n_pre_' + kk] = [a]
    G['n_rule_' + kk] = [b]
    G['n_region_gap_' + kk] = [a + b - G['n_sub_' + kk][0]]
TOK_KW = [u'caller', u'callers', u'text', u'stop', u'quit', u'end', u'revoke', u'cancel',
          u'unsubscribe', u'opt out', u'consent', u'robocall', u'robocalls', u'telemarketing']
for k in TOK_KW:
    G['n_tok_' + k.replace(u' ', u'_')] = [cnt_tok_b(k, LOWF)]
G['end_word_gap'] = [G['n_sub_end'][0] - G['n_tok_end'][0]]

# —— 规则链 ⇎ 锚池 ⇎ 反向针(针池与 A 侧同定义, 计数机制见差异 4/5/9)——
CHAIN = [
    u'A called party may revoke prior express consent, including prior express written consent',
    u'Callers may designate any of the following methods as the exclusive means to revoke consent',
    u'an automated, interactive voice or key press-activated opt-out mechanism on a call',
    u'must be honored within a reasonable time not to exceed ten business days from receipt of such request',
    u'The use of any means to revoke consent not listed in paragraph (a)(10) of this section creates a rebuttable presumption',
    u'a totality of circumstances analysis will determine whether the caller can demonstrate',
    u'Callers that do not designate an exclusive means to revoke consent pursuant to paragraph (a)(10)',
    u'must process revocation requests made by any reasonable means',
    u'Callers may interpret a revocation request made in response to an informational call',
    u'Revocation requests made in response to calls or text messages that contain an advertisement',
    u'If the confirmation text is sent within five minutes of receipt',
    u'two-way texting is not available due to technical limitations of the texting protocol',
    u'supplied by a spouse or other family member who is authorized to be on the account',
    u'The revised rule amendments contained herein become effective November 25, 2026',
    u'previously extended to January 31, 2027',
    u'We make clear that substantive changes to these rules are excluded from this delegation of authority',
]
NEG = [u'must be honored within ten business days', u'within ten business days from receipt',
       u'two business days', u'five business days', u'thirty business days', u'ten calendar days',
       u'immediately upon receipt', u'within 24 hours', u'one revocation request revokes all consent',
       u'revoke all categories of robocalls', u'must provide a revoke all method',
       u'effective january 31, 2027', u'opt-in', u'revocation must be processed within one business day',
       u'callers are required to honor every revocation regardless of method',
       u'confirmation text may include marketing information']
ATOMS = [x.strip() for x in io.open(ATOMFILE, encoding='utf-8').read().split(u'\n') if x.strip()]


def occ_line_b(needle, lines):
    """严格档(A 侧游标环 ⇎ B 侧 split 计数)。"""
    n = needle.lower()
    c = 0
    for l in lines:
        c += len(l.lower().split(n)) - 1
    return c


def occ_straddle_b(needle):
    """跨行档: 相邻两行折平面里跨界命中(B 侧独有构造, 用来反推严格档)。"""
    n = needle.lower()
    c = 0
    for i in range(len(NE) - 1):
        left = NE[i].lower()
        joined = left + u' ' + NE[i + 1].lower()
        k, L = 0, len(n)
        while True:
            j = joined.find(n, k)
            if j < 0:
                break
            if j < len(left) and j + L > len(left):
                c += 1
            k = j + L
    return c


for name, pool, pre in ((u'chain', CHAIN, u'chain'), (u'atom', ATOMS, u'atom')):
    tiers = [occ_tiers(x) for x in pool]
    strict = sum(t[0] for t in tiers)
    xline = sum(t[1] for t in tiers)
    flat = sum(cnt_sub_b(x, LOWF) for x in pool)
    assert strict + xline == flat, u'%s 侧: 严格 %d + 跨行 %d ≠ 折平 %d' % (name, strict, xline, flat)
    assert strict == sum(occ_line_b(x, NE) for x in pool), \
        u'%s 侧: 行号表严格档与逐行 split 计数不合' % name
    strad = sum(occ_straddle_b(x) for x in pool)
    assert strad <= xline, u'%s 侧: 相邻两行拼接的跨界 %d 大于跨行档 %d' % (name, strad, xline)
    G[pre + u'_n' if name == u'chain' else pre + u'_pool'] = [len(pool)]
    G[pre + u'_strict_occ' if name == u'chain' else pre + u'_strict'] = [strict]
    if name == u'chain':
        G['chain_flat_occ'] = [flat]
        G['chain_xline_occ'] = [xline]
        G['chain_needles_noline'] = [len([x for x in pool if occ_line_b(x, NE) == 0])]
        G['chain_needles_oneline'] = [len([x for x in pool if occ_line_b(x, NE) > 0])]
        G['chain_needles_hit'] = [len([x for x in pool if cnt_sub_b(x, LOWF) > 0])]
        G['chain_pnorm_occ'] = [sum(PN.count(pnorm_b(x)) for x in pool)]
        G['chain_shell_only'] = [len([x for x in pool
                                      if cnt_sub_b(x, LOWF) == 0 and PN.count(pnorm_b(x)) > 0])]
    else:
        G['atom_pool'] = [len(pool)]
        G['atom_flat_hit'] = [len([x for x in pool if cnt_sub_b(x, LOWF) > 0])]
        G['atom_pnorm_hit'] = [len([x for x in pool if pnorm_b(x) in PN])]
        G['atom_xline'] = [G['atom_pnorm_hit'][0] - strict]
        G['atom_shell_only'] = [len([x for x in pool
                                     if cnt_sub_b(x, LOWF) == 0 and pnorm_b(x) in PN])]
        G['atom_bad'] = [G['atom_pool'][0] - G['atom_pnorm_hit'][0]]
        G['atom_checks'] = [G['atom_pool'][0] * 3]

G['neg_n'] = [len(NEG)]
G['neg_strict'] = [sum(occ_line_b(x, NE) for x in NEG)]
G['neg_flat'] = [sum(cnt_sub_b(x, LOWF) for x in NEG)]
G['neg_pnorm'] = [sum(PN.count(pnorm_b(x)) for x in NEG)]
G['neg_checks'] = [G['neg_n'][0] * 3]
assert G['neg_strict'][0] == 0, u'B 侧反向针在严格档命中'
assert G['neg_flat'][0] == 0, u'B 侧反向针在容行档命中'
assert G['neg_pnorm'][0] == 0, u'B 侧反向针在最宽档命中'

# —— 结构档 ——
t1 = first_index(lambda l: u'Table 1--' in l, LINES)
t2 = first_index(lambda l: u'Table 2--' in l, LINES)
assert t1 > 0 and t2 > t1, u'B 侧表位下标不合'
SEG1 = LINES[t1:t2]
SEG2 = LINES[t2:]


def has6(line):
    for c in tok_runs(line):
        if len(c) == 6 and all(ch in DIG for ch in c):
            return True
    return False


def cells6(line):
    return [c for c in tok_runs(line) if len(c) == 6 and all(ch in DIG for ch in c)]


rows1 = [l for l in SEG1 if has6(l)]
G['t1_rows'] = [len(rows1)]
G['t1_naics'] = [len(dedup_sorted([c for l in rows1 for c in cells6(l)]))]
codes = [c for l in SEG1 for c in cells6(l)]
G['naics_cells'] = [len(codes)]


def pct_ok(row):
    """差异 11: 纯整数判据 2*|10000*小 − pc_h*总| < 总(A 侧 round 后比浮点差)。"""
    ns = num_runs(row)
    if len(ns) < 3:
        return None
    tot, small, pc = int(ns[-3].replace(u',', u'')), int(ns[-2].replace(u',', u'')), cents(ns[-1])
    return 2 * abs(10000 * small - pc * tot) < tot


def judge(rows, tag):
    j = [pct_ok(l) for l in rows]
    G[tag + u'_pct_ok'] = [len([x for x in j if x is True])]
    G[tag + u'_pct_bad'] = [len([x for x in j if x is False])]
    G[tag + u'_pct_na'] = [len([x for x in j if x is None])]


judge(rows1, u't1')


def tail_three(line):
    ns = num_runs(line)
    return len(ns) >= 3 and ns[-1].count(u'.') == 1 and len(ns[-1].split(u'.')[1]) == 2 \
        and len(ns[-1].split(u'.')[0]) in (2, 3) and len(ns[-2]) >= 2 and len(ns[-3]) >= 2


def dotted(line):
    """表二引导点行: 手工找连续 5 个以上 '.'(A 侧用正则 \\.{5,})。"""
    i, run = 0, 0
    while i < len(line):
        if line[i] == u'.':
            run += 1
            if run == 5:
                return True
        else:
            run = 0
        i += 1
    return False


rows2dot = [l for l in SEG2 if dotted(l) and tail_three(l)]
rows2tail = [l for l in SEG2 if tail_three(l)]
judge(rows2tail, u't2')
G['t2_rows_dot'] = [len(rows2dot)]
G['t2_rows_tail'] = [len(rows2tail)]
G['t2_rows_nodot'] = [G['t2_rows_tail'][0] - G['t2_rows_dot'][0]]

J1 = u'\n'.join(SEG1)
_d = []
_i = J1.find(u'$')
while _i >= 0:
    buf, k = [], _i + 1
    while k < len(J1) and (J1[k] in DIG or J1[k] in u',.'):
        buf.append(J1[k])
        k += 1
    if buf and J1[k:k + 8] == u' million':
        _d.append(u''.join(buf))
    _i = J1.find(u'$', _i + 1)
G['dollars_distinct'] = [len(dedup_sorted(_d))]
_p = 0
for i in range(2, len(FACE) - 2):
    if FACE[i] == u'.' and FACE[i - 2] in DIG and FACE[i - 1] in DIG \
            and FACE[i + 1] in DIG and FACE[i + 2] in DIG:
        _p += 1
G['pct_two_dp'] = [_p]

_s = FACE.find(u'standardized words: ')
_e = FACE.find(u'and/or', _s + 1)
assert _s > 0 and _e > _s, u'B 侧找不到标准词表的两端'
_seg = FACE[_s + len(u'standardized words: '):_e]
_w, _i, _c = 0, 0, 0
while True:
    a = _seg.find(u'``', _i)
    if a < 0:
        break
    b = _seg.find(u"''", a + 2)
    if b < 0:
        break
    _c += 1
    _i = b + 2
G['std_words'] = [_c]
assert _seg.count(u'``') == _c, u'B 侧标准词的开引号数与词数不合'

_q = FACE.find(u'revising paragraphs ')
_r = FACE.find(u' to read as follows', _q + 1)
assert _q > 0 and _r > _q, u'B 侧找不到被改段落短语'
PHRASE = FACE[_q + len(u'revising paragraphs '):_r]
_items, buf, i = [], u'', 0
while i < len(PHRASE):
    if PHRASE[i:i + 6] == u', and ':
        _items.append(buf)
        buf, i = u'', i + 6
    elif PHRASE[i:i + 2] == u', ':
        _items.append(buf)
        buf, i = u'', i + 2
    else:
        buf += PHRASE[i]
        i += 1
_items.append(buf)
G['para_items'] = [len([x for x in _items if any(ch in DIG for ch in x)])]
G['para_cells'] = [PHRASE.count(u')')]

_n2 = 0
for l in LINES:
    s = l.strip()
    i = 0
    while i < len(s) and s[i] in DIG:
        i += 1
    if i >= 1 and s[i:i + 2] == u'. ' and i + 2 < len(s) and s[i + 2] not in WSCH:
        _n2 += 1
G['amend_instr'] = [_n2]

_HL, _HR = [], []
for l in LINES:
    s = l.strip()
    if len(s) >= 5 and s[0] in u'ABCDEFGHIJKL' and s[1:3] == u'. ' and s[3] in UPP and s[4] in LOW:
        _HL.append(s)
    for cand in (u'III', u'II', u'I'):
        if s.startswith(cand) and s[len(cand):len(cand) + 2] == u'. ' \
                and len(s) > len(cand) + 2 and s[len(cand) + 2] in UPP:
            _HR.append(s)
            break
G['heads_letters'] = [len(_HL)]
G['heads_roman'] = [len(_HR)]
G['heads_overlap'] = [len([s for s in _HL if s[:2] == u'I.'])]
G['heads_union'] = [G['heads_letters'][0] + G['heads_roman'][0] - G['heads_overlap'][0]]

_ps = 0
for l in LINES:
    s = l.strip()
    if s.startswith(u'[[Page ') and s.endswith(u']]'):
        body = s[7:-2]
        if body and all(ch in DIG for ch in body):
            _ps += 1
G['page_shells'] = [_ps]
_pg = BODY.find(u'Pages ')
_i2 = _pg + 6
while BODY[_i2] == u' ':
    _i2 += 1
_j2 = _i2
while BODY[_j2] in DIG:
    _j2 += 1
first_pg = int(BODY[_i2:_j2])
assert BODY[_j2] == u'-'
_j3 = _j2 + 1
while BODY[_j3] in DIG:
    _j3 += 1
last_pg = int(BODY[_j2 + 1:_j3])
G['page_first'] = [first_pg]
G['page_last'] = [last_pg]
G['pages_span'] = [last_pg - first_pg + 1]
G['zero_lines'] = [len([l for l in LINES if l.strip() == u'0'])]

_sf = sent_split(FACE)
_sp = sent_split(PRE)
_sr = sent_split(RULE)
G['sents_flat'] = [len(_sf)]
G['sents_pre'] = [len(_sp)]
G['sents_rule'] = [len(_sr)]
G['sents_region_gap'] = [G['sents_pre'][0] + G['sents_rule'][0] - G['sents_flat'][0]]
G['sents_ten_days'] = [len([s for s in _sr if cnt_sub_b(u'ten business days', s.lower()) > 0])]
G['sents_five_min'] = [len([s for s in _sr if cnt_sub_b(u'five minutes', s.lower()) > 0])]
G['sents_must'] = [len([s for s in _sr if cnt_tok_b(u'must', s.lower()) > 0])]
G['date_nov25'] = [cnt_sub_b(u'november 25, 2026', LOWF)]
G['date_jan27'] = [cnt_sub_b(u'january 31, 2027', LOWF)]
G['months_12'] = [cnt_sub_b(u'12 months', LOWF)]
G['usc_cites'] = [cnt_sub_b(u'u.s.c.', LOWF)]
G['sec_cites'] = [cnt_tok_b(u'sec', LOWF)]

# —— 与 A 侧对账 ——
A = json.load(io.open(MEASA, encoding='utf-8'))
only_b = sorted(set(G) - set(A))
only_a = sorted(set(A) - set(G))
print(u'B 侧量测: %d 枚键; 键集差 ⇎ 只在 B: %d 枚 ⇎ 只在 A: %d 枚' % (
    len(G), len(only_b), len(only_a)))
if only_a or only_b:
    print(u'  只在 A 的键: %s' % only_a[:12])
    print(u'  只在 B 的键: %s' % only_b[:12])
    raise SystemExit(u'B96 对账: 键集不一致, 不写对账件')
bad = []
for k in sorted(A):
    av, bv = A[k][0], G[k][0]
    if isinstance(av, (int, float)) and isinstance(bv, (int, float)) and abs(av - bv) < 1e-9:
        continue
    bad.append((k, av, bv))
for k, av, bv in bad[:40]:
    print(u'  读数不合 %-30s A=%s B=%s' % (k, av, bv))
if bad:
    raise SystemExit(u'B96 对账: %d 枚键两套实现读数不合, 不写对账件' % len(bad))
json.dump({k: [A[k][0], G[k][0]] for k in sorted(A)}, io.open(
    MEAS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'对账通过: %d 枚键两套实现逐键同值 ⇒ %s' % (len(A), MEAS))
