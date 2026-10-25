# -*- coding: utf-8 -*-
"""B72 的第四遍复测: 与采集侧 _pick72 ⇎ 建条目侧 _mkB72/_mk72emit ⇎ 门槛侧 audit.py::_b72_scan
换算法不换定义, 现算后把 ⛓解读注 写进条目。本遍的独立处:
①行界三档对拍: re.split('\\n') 计格 ⇎ count('\\n')+1 计换行 ⇎ splitlines 计行(\\x0c 也算行界),
  换页符走 findall('\\x0c') 而非游标 find 循环;
②针计数一律 len(re.findall(re.escape(针), 面)), 重叠口径另用 (?=针) 前瞻档——第二遍是非重叠游标,
  第一遍是 str.count, 三档差合计必须为零;
③四档面的构造换写法: 折平走 re.sub('\\s+',' '), 摘壳走“先挑非壳行再折”, 剥引文走手写的 dq()
  (lstrip 后按字符吃掉一枚竖线与一枚空格, 行尾 rstrip 后吃掉一枚竖线), 与第二遍的两条 re.sub 同定义不同路;
  壳谓词与 dequote 的**定义**从 _mkB72.py 源码 exec 进来复用——要换的是量, 不是定义;
④义务语气走“游标 find 逐枚定位后只验左右邻是否 ASCII 字母”的整词档(第二遍是前后瞻正则一把数),
  MUST NOT 用同一档拿“MUST 空格 NOT”整短语去定位, 不是先切片再配相邻两枚;
⑤抬头动作字段走“逐行 startswith 后按逗号切”的档, 年份走“token 对”(月名∈MON 且下一 token 是四位数字),
  与第二遍的 (?m)^Field: 正则与 (Month) +([0-9]{4}) 联合式不同路;
⑥小节标题沿用同一组 HDR 正则(定义), 但 intro 界用 next() 现取, 号码集由 join 后的 findall 现采;
⑦段的起止行由剥引文偏移经 bisect_right 映回原行号(第二遍是线性游标扫描);
⑧共用长行池与配对走 dict-of-set ⇎ 逐字节集求交 ⇎ pres 权重容斥三式互检;
⑨锚归属走双轨: 原子串对原文件逐行 membership ⇎ 对整篇归一串 substring, 两式同判才计数;
⑩采集侧横比(pick_*)在本遍重跑一遍: 拿 _b72meas.json 与本遍现读量再对一次, 不是抄第二遍的结论。
恒等式与 DERIV 复算点从 _b72checks.json ⇎ _deriv72.json 回读后 eval, 不重打一遍算式。
每个键与 corpus/_b72flat.json 对拍, 值不符或键缺失一律先收集后汇总, 全零才落盘。"""
import io, os, re, sys, json, glob, ast, bisect, itertools
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
ENTRY = u'%s/babeltele/B72_redirect_method_rewrite_four_answers.md' % C
PATH = [u'%s/raw/httpRedir/rfc2616.txt' % C, u'%s/raw/httpRedir/rfc7231.txt' % C,
        u'%s/raw/httpRedir/rfc7538.txt' % C, u'%s/raw/httpRedir/rfc9110.txt' % C]
LBL = [u'2616', u'7231', u'7538', u'9110']
NSRC = 4
BAND = 20
POOLMIN = 40
APOOLMIN = 24
NL = u'\n'
FLAT = json.load(io.open(u'%s/_b72flat.json' % C, encoding='utf-8'))
CH = json.load(io.open(u'%s/_b72checks.json' % C, encoding='utf-8'))
JJ = json.load(io.open(u'%s/_deriv72.json' % C, encoding='utf-8'))
MEA = json.load(io.open(u'%s/_b72meas.json' % C, encoding='utf-8'))

# 定义(不是本遍要换的量): 针表、小节正则、答句针、壳谓词与剥引文谓词从 _mkB72.py 源码取
MS = io.open(u'%s/_mkB72.py' % C, encoding='utf-8').read()
ES = io.open(u'%s/_mk72emit.py' % C, encoding='utf-8').read()
SCAN = MS[MS.index(u'# --- SCAN BEGIN ---'):MS.index(u'# --- SCAN END ---')]
TAB = {}
WANT = (u'SENT', u'HDR', u'ANSND', u'TIER', u'WORDS', u'PINS', u'CFOUR', u'TRACKS')
for src in (MS, ES):
    for st in ast.parse(src.replace(u'\nexec(', u'\n#exec(')).body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
            nm = st.targets[0].id
            if nm in WANT and nm not in TAB:
                try:
                    TAB[nm] = ast.literal_eval(st.value)
                except Exception:
                    pass
for nm in WANT:
    assert nm in TAB, nm
SENT = TAB[u'SENT']
HDR = TAB[u'HDR']
ANSND = TAB[u'ANSND']
TIER = TAB[u'TIER']
PINS = TAB[u'PINS']
WORDS = TAB[u'WORDS']
CFOUR = TAB[u'CFOUR']
TRACKS = TAB[u'TRACKS']
_ns = {'re': re}
for fn in (u'shell_line', u'shell_pick_line', u'dequote'):
    exec(re.search(u'def ' + fn + u'\\(\\w*\\):.*?\\n(?=\\S)', MS, re.S).group(0), _ns)
shell_line = _ns[u'shell_line']
shell_pick_line = _ns[u'shell_pick_line']
dequote = _ns[u'dequote']

D = {}
J = lambda xs: u' ⇎ '.join(u'%s' % x for x in xs)


def pn(s):
    return u' '.join(s.lower().split())


def fold(s):
    """全篇折平: 换写法(re.sub 一把)得到与 ' '.join(s.split()) 同定义的面"""
    return re.sub(u'\\s+', u' ', s).strip()


def dq(x):
    """剥引文标记的手写档: 先吃掉整段行首空白再吃一枚竖线(可跟一枚空格), 行尾 rstrip 后吃掉一枚竖线"""
    b = x.lstrip()
    if b[:1] == u'|':
        b = b[1:]
        if b[:1] == u' ':
            b = b[1:]
    t = b.rstrip()
    if t[-1:] == u'|':
        t = t[:-1]
    return t


assert all(dq(x) == dequote(x) for x in [u'  | a', u'  |  b', u'x |', u'   |', u'no bar', u'|  |'])


def rc(t, nd):
    return len(re.findall(re.escape(nd), t))


def ro(t, nd):
    return len(re.findall(u'(?=' + re.escape(nd) + u')', t))


ALPH = u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def ub2(t, w):
    """整词档: 游标 find 逐枚定位后只验左右邻是否 ASCII 字母(与第二遍的前后瞻正则同定义)"""
    n, a, m = 0, 0, len(w)
    while True:
        a = t.find(w, a)
        if a < 0:
            return n
        b = a + m
        if (a == 0 or t[a - 1] not in ALPH) and (b == len(t) or t[b] not in ALPH):
            n += 1
        a = b


def ph(t, a, b):
    return ub2(t, a + u' ' + b)


def sub4(name, f):
    D[name] = [f(i) for i in range(NSRC)]


BYT = [io.open(p, 'rb').read() for p in PATH]
T = [b.decode('utf-8', 'replace') for b in BYT]
L = [re.split(u'\n', t) for t in T]
FO = [pn(t) for t in T]
FOLD = [fold(t) for t in T]
SH = [[x for x in L[i] if not shell_line(x)] for i in range(NSRC)]
SHF = [fold(NL.join(sh)) for sh in SH]
QUOT = [fold(NL.join([dq(x) for x in L[i]])) for i in range(NSRC)]
for i in range(NSRC):
    assert QUOT[i] == u' '.join(u'\n'.join([dequote(x) for x in L[i]]).split()), i
FACES = [L, FOLD, SHF, QUOT]

# ---------- 针: 由锚位置从最宽档面导出整句(同一定义), 计数换 findall ----------
TEXT = {}
NEG = [k for o, k, s0, e0 in SENT if s0.startswith(u'@')]
for (o, k, s0, e0) in [(i, k, s, e) for i, k, s, e in SENT if not k.endswith(u'_pipe')]:
    if k in NEG:
        TEXT[k] = s0[1:]
    else:
        a = QUOT[o].find(s0)
        b = QUOT[o].find(e0, a)
        assert a >= 0 and b >= 0, k
        TEXT[k] = QUOT[o][a:b + len(e0)]
_a = FOLD[3].find(u'For historical reasons, a user agent MAY change')
_b = FOLD[3].find(u'subsequent request.', _a)
TEXT[u'a9110_302_hist_may_pipe'] = FOLD[3][_a:_b + len(u'subsequent request.')]
OWNER = dict((k, o) for o, k, _, _ in SENT)
GN = [k for o, k, _, _ in SENT]


def hit(i, nd, tier):
    if tier == 0:
        return sum(rc(x, nd) for x in L[i] if nd in x)
    return rc(FACES[tier][i], nd)


SN = dict((k, [hit(OWNER[k], TEXT[k], n) for n in range(4)]) for k in GN)
D['needle_n'] = len(GN)
for st, n in ((u'strict', 0), (u'fold', 1), (u'sh', 2), (u'quot', 3)):
    D['sn_%s_docs' % st] = [len([k for k in GN if OWNER[k] == i and SN[k][n]]) for i in range(NSRC)]
D['fold_only_keys'] = [k for k in GN if not SN[k][0] and SN[k][1]]
D['fold_only_own'] = [len([k for k in D['fold_only_keys'] if OWNER[k] == i]) for i in range(NSRC)]
D['fold_only_n'] = len(D['fold_only_keys'])
D['fold_only_str'] = u' ⇎ '.join(D['fold_only_keys'])
D['sh_only_keys'] = [k for k in GN if not SN[k][1] and SN[k][2]]
D['quot_only_keys'] = [k for k in GN if not SN[k][2] and SN[k][3]]
D['quot_only_own'] = [len([k for k in D['quot_only_keys'] if OWNER[k] == i]) for i in range(NSRC)]
D['quot_only_n'] = len(D['quot_only_keys'])
D['quot_only_str'] = u' ⇎ '.join(D['quot_only_keys'])
D['quot_minus_sh'] = [D['sn_quot_docs'][i] - D['sn_sh_docs'][i] for i in range(NSRC)]
D['sh_minus_fold'] = [D['sn_fold_docs'][i] - D['sn_sh_docs'][i] for i in range(NSRC)]
SER = [u'a9110_302_hist_may_pipe']
D['ser_controls'] = SER
D['ser_n'] = len(SER)
D['dead_needles'] = [k for k in GN if not SN[k][3] and k not in SER]
D['dead_nonneg'] = len([k for k in D['dead_needles'] if k not in NEG])
D['neg_controls'] = sorted(NEG)
D['neg_ctrl_n'] = len(D['neg_controls'])
D['neg_hit_widest'] = sum(SN[k][3] for k in NEG)
D['dead_widest'] = [k for k in GN if not SN[k][3]]
D['dead_n'] = len(D['dead_widest'])
D['ser_fold_hit'] = SN[u'a9110_302_hist_may_pipe'][1]
D['ser_quot_hit'] = SN[u'a9110_302_hist_may_pipe'][3]
D['quot_lost_keys'] = [k for k in GN if SN[k][2] and not SN[k][3]]
D['quot_lost_n'] = len(D['quot_lost_keys'])
D['quot_lost_nonserv'] = len([k for k in D['quot_lost_keys'] if k not in SER])
D['ladder_monotone'] = 1 if all(D['sn_strict_docs'][i] + D['fold_only_own'][i] == D['sn_fold_docs'][i]
                                and D['sn_sh_docs'][i] <= D['sn_fold_docs'][i]
                                and D['sn_quot_docs'][i] >= D['sn_sh_docs'][i] for i in range(NSRC)) else 0
D['re_eq_cur'] = 1 if all(len(re.findall(re.escape(TEXT[k]), QUOT[OWNER[k]])) == SN[k][3] for k in GN) else 0
D['overlap_extra'] = sum(ro(QUOT[OWNER[k]], TEXT[k]) - SN[k][3] for k in GN)
D['needles_owned'] = [len([k for k in GN if OWNER[k] == i]) for i in range(NSRC)]
for o, k, _, _ in SENT:
    D['n_' + k] = SN[k]
D['nd_len'] = [len(TEXT[k]) for k in GN]
D['nd_len_tot'] = sum(D['nd_len'])
D['pipe_needle_pair'] = 1 if (SN[u'a9110_302_hist_may'][1] == 0 and SN[u'a9110_302_hist_may_pipe'][1]
                              and SN[u'a9110_302_hist_may'][3]
                              and SN[u'a9110_302_hist_may_pipe'][3] == 0) else 0
D['cross_needles'] = [k for k in GN if sum(1 for i in range(NSRC) if SN[k][i]) >= 2]
D['cross_needle_n'] = len(D['cross_needles'])
D['line_hit_keys'] = [k for k in GN if SN[k][0]]

# ---------- 结构 / 版式 / 编码 ----------
sub4(u'bytes', lambda i: len(BYT[i]))
sub4(u'chars', lambda i: len(T[i]))
sub4(u'lines', lambda i: len(L[i]))
D[u'lines_nl'] = [T[i].count(u'\n') + 1 for i in range(NSRC)]
D[u'lines_split'] = [len(T[i].splitlines()) for i in range(NSRC)]
D[u'tail_nl'] = [1 if T[i].endswith(u'\n') else 0 for i in range(NSRC)]
sub4(u'nonblank', lambda i: len([x for x in L[i] if x.strip()]))
sub4(u'maxlen', lambda i: max(len(x) for x in L[i]))
sub4(u'cr', lambda i: len(re.findall(u'\r', T[i])))
sub4(u'ff', lambda i: len(re.findall(u'\x0c', T[i])))
sub4(u'ff_only', lambda i: len([x for x in L[i] if x.strip() == u'\x0c']))
sub4(u'ff_exact', lambda i: len([x for x in L[i] if x == u'\x0c']))
sub4(u'shell_n', lambda i: len([x for x in L[i] if shell_line(x)]))
D[u'shell_strip'] = [len(SH[i]) for i in range(NSRC)]
PICKL = [[x for x in L[i] if shell_pick_line(x)] for i in range(NSRC)]
MO = [[x for x in L[i] if shell_line(x) and not shell_pick_line(x)] for i in range(NSRC)]
PO = [[x for x in L[i] if shell_pick_line(x) and not shell_line(x)] for i in range(NSRC)]
D['shell_pick'] = [len(PICKL[i]) for i in range(NSRC)]
D['shell_both'] = [D['shell_n'][i] - len(MO[i]) for i in range(NSRC)]
D['shell_mk_only'] = [len(MO[i]) for i in range(NSRC)]
D['shell_pick_only'] = [len(PO[i]) for i in range(NSRC)]
D['shell_diff'] = [D['shell_n'][i] - D['shell_pick'][i] for i in range(NSRC)]
HDRF = re.compile(u'^\\s*(Network Working Group|Request for Comments:|Obsoletes:|Updates:|Category:|ISSN:)')
IND = re.compile(u'^[ \\t]+RFC \\d{4} ')
D['shell_mk_only_hdr'] = [len([x for x in MO[i] if HDRF.match(x)]) for i in range(NSRC)]
D['shell_pick_only_body'] = [len([x for x in PO[i] if IND.match(x)]) for i in range(NSRC)]
sub4(u'nonascii', lambda i: len([c for c in T[i] if ord(c) > 127]))
sub4(u'bom', lambda i: 1 if BYT[i][0:3] == b'\xef\xbb\xbf' else 0)
sub4(u'nonascii_extra', lambda i: sum(2 if ord(c) > 2047 else 1 for c in T[i] if ord(c) > 127))
D[u'byte_cp_delta'] = [D[u'bytes'][i] - D[u'chars'][i] for i in range(NSRC)]
sub4(u'nul_faces', lambda i: len(re.findall(u'\x00', T[i])))
sub4(u'digit_chars', lambda i: sum(1 for c in T[i] if c.isdigit()))
sub4(u'dblspace', lambda i: ro(T[i], u'  '))
D[u'ascii_all'] = sum(1 for i in range(NSRC) if D[u'nonascii'][i] == 0)
D[u'lines_split_close'] = sum(D[u'lines_nl'][i] - D[u'tail_nl'][i] + D[u'ff'][i]
                              - D[u'lines_split'][i] for i in range(NSRC))
sub4(u'pipe_lines', lambda i: len([x for x in L[i] if x.lstrip()[:1] == u'|']))
sub4(u'pipe_glyphs', lambda i: rc(T[i], u'|'))
sub4(u'quot_face_delta', lambda i: len(FOLD[i]) - len(QUOT[i]))
sub4(u'quot_dropped', lambda i: D[u'pipe_glyphs'][i] - D[u'quot_face_delta'][i])
sub4(u'bar_fold', lambda i: rc(FOLD[i], u'|'))
sub4(u'bar_quot', lambda i: rc(QUOT[i], u'|'))
sub4(u'bar_removed', lambda i: D[u'bar_fold'][i] - D[u'bar_quot'][i])
sub4(u'bar_removed_line', lambda i: sum(x.count(u'|') - dq(x).count(u'|') for x in L[i]))
sub4(u'quot_line_n', lambda i: len([x for x in L[i] if u'|' in x]))

# ---------- 抬头动作字段 / 类目 / 年份 ----------
def hdr_field(t, fld):
    for x in re.split(u'\n', t):
        if x.startswith(fld):
            return x[len(fld):].lstrip().split(u'  ')[0]
    return u''


def ids(val):
    return sorted(set(int(x) for x in re.findall(u'\\d{3,5}', val)))


OBS = [ids(hdr_field(T[i], u'Obsoletes:')) for i in range(NSRC)]
UPD = [ids(hdr_field(T[i], u'Updates:')) for i in range(NSRC)]
D['obs_ids'] = OBS
D['upd_ids'] = UPD
D['obs_n'] = [len(s) for s in OBS]
D['upd_n'] = [len(s) for s in UPD]
D['target_ids'] = sorted(set(OBS[0] + OBS[1] + OBS[2] + OBS[3] + UPD[0] + UPD[1] + UPD[2] + UPD[3]))
D['target_n'] = len(D['target_ids'])
sub4(u'obs_verb', lambda i: rc(T[i], u'Obsoletes'))
sub4(u'upd_verb', lambda i: rc(T[i], u'Updates'))
sub4(u'cat_std', lambda i: rc(T[i], u'Category: Standards Track'))
sub4(u'cat_hdr', lambda i: len([x for x in L[i] if x.lstrip().startswith(u'Category:')]))
sub4(u'issn', lambda i: rc(T[i], u'ISSN: 2070-1721'))
sub4(u'std_hdr', lambda i: len([x for x in L[i] if re.match(u'^\\s*STD:\\s*\\d+', x)]))
MON = (u'January February March April May June July August September October November December').split()
MONS = set(MON)


def hdr_year(lines):
    for x in lines[:60]:
        tk = x.split()
        for i in range(len(tk) - 1):
            if tk[i] in MONS and re.match(u'^\\d{4}$', tk[i + 1]):
                return (int(tk[i + 1]), tk[i])
    return (None, None)


YR = [hdr_year(L[i]) for i in range(NSRC)]
D['years'] = [y for y, _ in YR]
D['months'] = [mo for _, mo in YR]
D['year_order'] = 1 if D['years'] == sorted(D['years']) else 0
D['year_inversions'] = sum(1 for a in range(NSRC) for b in range(a + 1, NSRC)
                          if D['years'][a] > D['years'][b])
D['year_gaps'] = [D['years'][i + 1] - D['years'][i] for i in range(NSRC - 1)]

# ---------- 30x 小节: 同一组标题正则(定义), 换选择写法 ----------
HEADLN = []
CODES = []
for i in range(NSRC):
    lo = next((n for n, x in enumerate(L[i], 1)
               if re.match(u'^1\\.\\s+Introduction\\s*$', x.rstrip())), 0)
    hd = [(n, x.strip()) for n, x in enumerate(L[i], 1)
          if n > lo and len(x.strip()) < 70 and re.search(HDR[i], x)]
    HEADLN.append(hd)
    CODES.append(re.findall(u'30\\d', u' '.join(h[1] for h in hd)))
D['sec_heads'] = [len(h) for h in HEADLN]
D['codes'] = CODES
D['code_n'] = [len(c) for c in CODES]
D['code_union'] = sorted(set(CODES[0] + CODES[1] + CODES[2] + CODES[3]))
D['code_distinct'] = [sorted(set(c)) for c in CODES]
D['head_eof'] = [h[-1][0] if h else 0 for h in HEADLN]
D['head_first_ln'] = [h[0][0] if h else 0 for h in HEADLN]

# ---------- 义务语气四轨(token 档) ----------
UP, LO, CI, TI, UPN = {}, {}, {}, {}, {}
for w in WORDS:
    UP[w] = [ub2(T[i], w) for i in range(NSRC)]
    LO[w] = [ub2(T[i], w.lower()) for i in range(NSRC)]
    CI[w] = [ub2(T[i].lower(), w.lower()) for i in range(NSRC)]
    TI[w] = [ub2(T[i], w[:1].upper() + w[1:].lower()) for i in range(NSRC)]
for w, a, b in ((u'MUST NOT', u'MUST', u'NOT'), (u'MAY NOT', u'MAY', u'NOT'),
                (u'SHOULD NOT', u'SHOULD', u'NOT')):
    UPN[w] = [rc(T[i], a + u' ' + b) for i in range(NSRC)]
D['up_must_all'] = UP[u'MUST']
D['up_may'] = UP[u'MAY']
D['up_should'] = UP[u'SHOULD']
D['must_not'] = UPN[u'MUST NOT']
D['should_not'] = UPN[u'SHOULD NOT']
D['may_not'] = UPN[u'MAY NOT']
D['must_bare'] = [UP[u'MUST'][i] - UPN[u'MUST NOT'][i] for i in range(NSRC)]
D['low_must'] = LO[u'MUST']
D['ci_must'] = CI[u'MUST']
D['title_must'] = TI[u'MUST']
D['case_ledger'] = [sum(CI[w][i] - UP[w][i] - LO[w][i] - TI[w][i] for w in WORDS) for i in range(NSRC)]
D['up_ledger'] = [UP[u'MUST'][i] - (D[u'must_bare'][i] + UPN[u'MUST NOT'][i]) for i in range(NSRC)]

# ---------- 措辞档轴 ⇎ 词面读数 ----------
D['tier_words'] = list(TIER.keys())
for k, w in TIER.items():
    D[u'tier_' + k] = [rc(FOLD[i], w) for i in range(NSRC)]
    D[u'tierq_' + k] = [rc(QUOT[i], w) for i in range(NSRC)]
D['tier_fold_tot'] = [sum(D[u'tier_' + k][i] for k in TIER) for i in range(NSRC)]
D['tier_quot_tot'] = [sum(D[u'tierq_' + k][i] for k in TIER) for i in range(NSRC)]
D['tier_gain'] = [D['tier_quot_tot'][i] - D['tier_fold_tot'][i] for i in range(NSRC)]
D['tier_sum_close'] = sum(D['tier_gain']) - sum(D['quot_only_own'])
sub4(u'post_to_get', lambda i: rc(QUOT[i], u'POST to GET'))
sub4(u'hist_reasons', lambda i: rc(QUOT[i], u'For historical reasons'))
sub4(u'method_word', lambda i: ub2(T[i], u'method'))
sub4(u'redirect_word', lambda i: ub2(T[i], u'redirect'))

# ---------- 游标读数 ⇎ 数字 308 的四档枚数 ----------
NUM = {}
NUM['codes_named'] = D['code_n']
NUM['status_digits'] = [len([m for m in re.finditer(u'(?<!\\w)30[0-9](?!\\w)', QUOT[i])]) for i in range(NSRC)]
NUM['rfc_refs'] = [len([m for m in re.finditer(u'RFC\\s{0,1}\\d\\d\\d\\d', T[i])]) for i in range(NSRC)]
NUM['sec_302'] = [rc(QUOT[i], u'302') for i in range(NSRC)]
NUM['sec_307'] = [rc(QUOT[i], u'307') for i in range(NSRC)]
NUM['sec_308'] = [rc(QUOT[i], u'308') for i in range(NSRC)]
NUM['get_word'] = [rc(QUOT[i], u'GET') for i in range(NSRC)]
NUM['post_word'] = [rc(QUOT[i], u'POST') for i in range(NSRC)]
for k, v in NUM.items():
    D[u'num_' + k] = v
D['s308_raw'] = [rc(T[i], u'308') for i in range(NSRC)]
D['s308_fold'] = [rc(FOLD[i], u'308') for i in range(NSRC)]
D['s308_sh'] = [rc(SHF[i], u'308') for i in range(NSRC)]
D['s308_quot'] = [rc(QUOT[i], u'308') for i in range(NSRC)]
D['s308_shell'] = [sum(rc(x, u'308') for x in L[i] if shell_line(x)) for i in range(NSRC)]
D['num_gap_2616'] = D['years'][1] - D['years'][0]
D['num_gap_9110'] = D['years'][3] - D['years'][2]

# ---------- 引用写法三式(同一组字面, 换 findall 计数) ----------
CITEIDS = (u'1945', u'2068', u'2616', u'2817', u'7231', u'7232', u'7538', u'9110', u'7230', u'7235')
CT = {}
for n in CITEIDS:
    CT['sp_' + n] = [rc(T[i], u'RFC ' + n) for i in range(NSRC)]
    CT['hy_' + n] = [rc(T[i], u'RFC-' + n) for i in range(NSRC)]
    CT['tk_' + n] = [rc(T[i], u'RFC' + n) for i in range(NSRC)]
    CT['al_' + n] = [CT['sp_' + n][i] + CT['hy_' + n][i] + CT['tk_' + n][i] for i in range(NSRC)]
    CT['br_' + n] = [rc(T[i], u'[RFC' + n + u']') for i in range(NSRC)]
for k in CT:
    D['cite_' + k] = CT[k]
D['cite_self'] = [CT['al_' + n][i] for i, n in enumerate(LBL)]
D['cite_forms_close'] = [len([m for m in re.finditer(u'RFC[ -]' + LBL[i] + u'|RFC ' + LBL[i] + u'|RFC-' + LBL[i] + u'|RFC' + LBL[i], T[i])]) - CT['al_' + LBL[i]][i] for i in range(NSRC)]
D['cite_dir_7231_to_9110'] = CT['al_7231'][3]
D['cite_dir_9110_to_7231'] = CT['al_9110'][1]
D['cite_7538_in_9110'] = CT['al_7538'][3]
D['cite_7538_in_7231'] = CT['al_7538'][1]
D['cite_2616_in_7231'] = CT['al_2616'][1]
D['cite_1945_tot'] = sum(CT['al_1945'])
D['cite_2068_tot'] = sum(CT['al_2068'])

# ---------- 共用长行池: 换 dict-of-set 与集合代数 ----------
RW = [defaultdict(set) for i in range(NSRC)]
for i in range(NSRC):
    for x in SH[i]:
        if len(pn(x)) >= POOLMIN:
            RW[i][pn(x)].add(x)
NS_ = [set(RW[i]) for i in range(NSRC)]
POOLALL = set().union(*NS_)
PRES = dict((a, tuple(i for i in range(NSRC) if a in NS_[i])) for a in POOLALL)
D['pool_n'] = len(POOLALL)
D['pool_tier'] = [len([a for a, v in PRES.items() if len(v) == n]) for n in range(1, NSRC + 1)]
D['pool_tier_close'] = sum(D['pool_tier']) - len(POOLALL)
for n in range(4):
    D['pool_%d' % (n + 1)] = D['pool_tier'][n]
PAIRS = [(a, b) for a, b in itertools.combinations(range(NSRC), 2)]
share, byte, nonly = [], [], []
for i, j in PAIRS:
    inter = NS_[i] & NS_[j]
    share.append(len(inter))
    byte.append(len([s for s in inter if RW[i][s] & RW[j][s]]))
    nonly.append(len(inter) - byte[-1])
D['pair_share'] = share
D['pair_byte'] = byte
D['pair_norm_only'] = nonly
D['pair_nonzero'] = len([x for x in share if x])
D['pair_close'] = sum(share) - sum(byte) - sum(nonly)
D['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
mx = max(share)
D['pair_max'] = mx
D['pair_max_idx'] = share.index(mx)
D['pair_max_byte'] = byte[D['pair_max_idx']]
D['pair_max_norm_only'] = nonly[D['pair_max_idx']]
D['pair_max_lbl'] = D['pair_lbl'][D['pair_max_idx']]
D['s3_examples'] = sorted([a for a, v in PRES.items() if len(v) >= 3])
_w = [len(v) for v in PRES.values()]
D['pool_incl'] = [sum(_w), sum(x * (x - 1) // 2 for x in _w),
                  sum(x * (x - 1) * (x - 2) // 6 for x in _w), _w.count(NSRC)]
D['union_incl'] = D['pool_incl'][0] - D['pool_incl'][1] + D['pool_incl'][2] - D['pool_incl'][3]
D['union_close'] = D['pool_n'] - D['union_incl']
D['shared_norm_only'] = sum(nonly)

# ---------- 写法分家轴(同一分类定义, 换“变体集来自 RW”的取法) ----------
ax = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
nvar = 0
for a, v in PRES.items():
    if len(v) < 2:
        continue
    xs = set()
    for i in v:
        xs |= RW[i][a]
    if len(xs) > 1:
        nvar += 1
    if len(xs) < 2:
        continue
    o, p = sorted(xs)[0], sorted(xs)[1]
    if len(o) == len(p) and o != p and all(x.lower() == y.lower() for x, y in zip(o, p)):
        ax[u'case'] += 1
    elif (u'-' in o) != (u'-' in p):
        ax[u'hyph'] += 1
    elif len(o.split()) == len(p.split()):
        ax[u'space'] += 1
    else:
        ax[u'multi'] += 1
D['axis_counts'] = ax
D['axis_total'] = sum(ax.values())
D['norm_only_set'] = nvar
D['axis_close'] = D['axis_total'] - D['norm_only_set']
D['axis_str'] = u'⇎'.join(u'%s%d' % (a, ax[a]) for a in (u'case', u'hyph', u'space', u'multi'))
D['axis_str_n'] = len([a for a in (u'case', u'hyph', u'space', u'multi') if ax[a]])

# ---------- 锚候选池 ----------
AR = [(pn(x), i) for i in range(NSRC) for x in SH[i]
      if len(pn(x)) >= APOOLMIN and re.search(u'[A-Za-z]', x)]
AD = defaultdict(set)
for a, i in AR:
    AD[a].add(i)
D['apool_n'] = len(AD)
D['apool_raw_n'] = len(AR)
D['apool_face_raw'] = [len([1 for a, k in AR if k == i]) for i in range(NSRC)]
D['apool_tag_n'] = [len([a for a, v in AD.items() if i in v]) for i in range(NSRC)]
D['apool_dup'] = [D['apool_face_raw'][i] - D['apool_tag_n'][i] for i in range(NSRC)]
D['apool_tag_close'] = sum(D['apool_tag_n']) + sum(D['apool_dup']) - D['apool_raw_n']
D['apool_tier'] = [len([a for a, v in AD.items() if len(v) == n]) for n in range(1, NSRC + 1)]
D['apool_weight'] = sum(D['apool_tier'][n] * (n + 1) for n in range(NSRC))
D['apool_pairs'] = sum(D['apool_tag_n'])
D['apool_tier_close'] = D['apool_weight'] - D['apool_pairs']
D['apool_maxlen'] = max(len(a) for a in AD)

# ---------- 答句邻域窗(±BAND 行) ----------
def ans_line(i):
    return next((n for n, x in enumerate(L[i], 1) if ANSND[i] in x), None)


WIN = []
for i in range(NSRC):
    a = ans_line(i)
    assert a, LBL[i]
    lo, hi = max(1, a - BAND), min(len(L[i]), a + BAND)
    body = NL.join(L[i][lo - 1:hi])
    outb = NL.join(L[i][:lo - 1] + L[i][hi:])
    fb, fo = fold(body), fold(outb)
    w = {u'ans': a, u'start': lo, u'end': hi, u'rows': hi - lo + 1,
         u'chars': len(body), u'chars_out': len(outb),
         u'dig_in': len([c for c in body if c.isdigit()]),
         u'dig_out': len([c for c in outb if c.isdigit()])}
    for tr in TRACKS[i]:
        w[tr] = rc(fb, tr)
        w[tr + u'_out'] = rc(fo, tr) + ro(fo, tr)
    WIN.append(w)
for k in (u'ans', u'start', u'end', u'rows', u'chars', u'chars_out', u'dig_in', u'dig_out'):
    D[u'win_' + k] = [w[k] for w in WIN]
for tr in (u'redirect', u'GET', u'POST', u'MUST'):
    D[u'win_' + tr + u'_in'] = [w[tr] for w in WIN]
    D[u'win_' + tr + u'_out'] = [w[tr + u'_out'] for w in WIN]
D['win_band'] = BAND
D['win_spans'] = [w[u'end'] - w[u'start'] + 1 for w in WIN]
D['win_close_dig'] = [WIN[i][u'dig_in'] + WIN[i][u'dig_out'] - D['digit_chars'][i] for i in range(NSRC)]
D['win_close_sum'] = sum(D['win_close_dig'])

# ---------- 四段答句: 偏移→行号换 bisect 映回 ----------
OFFS, LNOS = [], []
for i in range(NSRC):
    offs, lns = [], []
    cur, first = 0, True
    for n, x in enumerate(L[i], 1):
        s = u' '.join(dq(x).split())
        if not s:
            continue
        if not first:
            cur += 1
        first = False
        offs.append(cur)
        lns.append(n)
        cur += len(s)
    OFFS.append(offs)
    LNOS.append(lns)
assert all(u' '.join([u' '.join(dq(x).split()) for x in L[i]
                      if u' '.join(dq(x).split())]) == QUOT[i] for i in range(NSRC))


def line_of(i, a):
    return LNOS[i][bisect.bisect_right(OFFS[i], a) - 1]


def ln_of(i, nd):
    a = QUOT[i].find(nd)
    assert a >= 0, (LBL[i], nd)
    return line_of(i, a)


def blk(i, start, end):
    a = QUOT[i].find(start)
    assert a >= 0, (LBL[i], start)
    b = QUOT[i].find(end, a)
    assert b >= 0, (LBL[i], end)
    e = b + len(end)
    return u' '.join(QUOT[i][a:e].split()), line_of(i, a), line_of(i, e - 1)


PB = [blk(i, s, e) for i, s, e in PINS]
PTXT = [p[0] for p in PB]
D['blk_lo'] = [p[1] for p in PB]
D['blk_hi'] = [p[2] for p in PB]
D['blk_rows'] = [p[2] - p[1] + 1 for p in PB]
D['blk_chars'] = [len(p[0]) for p in PB]
D['blk_words'] = [len(p[0].split()) for p in PB]
PW = [p[0].lower().split() for p in PB]
D['blk_only'] = [(len(set(PW[i]) - set(PW[i - 1])) if i else len(set(PW[i]))) for i in range(NSRC)]
D['blk_common_1'] = len(set(PW[0]) & set(PW[1]))
D['blk_vocab'] = [len(set(x)) for x in PW]
D['w_row_close'] = D['blk_only'][1] + D['blk_common_1'] - D['blk_vocab'][1]


def suffix_words(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def head_words(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


D['suf_7231_9110'] = suffix_words(PW[1], PW[3])
D['pre_7231_9110'] = head_words(PW[1], PW[3])
D['suf_2616_7231'] = suffix_words(PW[0], PW[1])
D['pre_2616_7231'] = head_words(PW[0], PW[1])
D['blk_same_7231_9110'] = 1 if PW[1] == PW[3] else 0
D['blk_identical_chars'] = 1 if PTXT[1] == PTXT[3] else 0
D['tone_must'] = [ub2(p, u'MUST') for p in PTXT]
D['tone_may'] = [ub2(p, u'MAY') for p in PTXT]
D['tone_must_not_blk'] = [ph(p, u'MUST', u'NOT') for p in PTXT]
D['tone_should'] = [ub2(p, u'SHOULD') for p in PTXT]
D['tone_up'] = [D['tone_must'][i] + D['tone_may'][i] + D['tone_should'][i] for i in range(NSRC)]
D['tone_bare_must'] = [D['tone_must'][i] - D['tone_must_not_blk'][i] for i in range(NSRC)]
D['tone_ledger'] = [D['tone_must'][i] - (D['tone_bare_must'][i] + D['tone_must_not_blk'][i])
                    for i in range(NSRC)]
D['ln_note_2616'] = ln_of(0, u'RFC 1945 and RFC 2068 specify')
D['ln_treat_2616'] = ln_of(0, u'treat 302 as if it were a 303')
D['note_treat_gap'] = D['ln_treat_2616'] - D['ln_note_2616']
D['ln_hist_7231'] = ln_of(1, u'For historical reasons, a user agent MAY change')
D['ln_mustnot_7231'] = ln_of(1, u'MUST NOT change the request method')
D['hist_mustnot_gap'] = D['ln_mustnot_7231'] - D['ln_hist_7231']
D['ln_ind_7538'] = ln_of(2, u'The 308 (Permanent Redirect) status code indicates')
D['ln_restricted_7538'] = ln_of(2, u'the use of status code 308 is restricted')
D['ind_restricted_gap'] = D['ln_restricted_7538'] - D['ln_ind_7538']
D['ln_hist_9110'] = ln_of(3, u'For historical reasons, a user agent MAY change')
D['ln_step_9110'] = ln_of(3, u'Change the request method according')
D['hist_step_gap'] = D['ln_step_9110'] - D['ln_hist_9110']
D['step_hist_abs'] = abs(D['hist_step_gap'])
TOPNUM = re.compile(u'^   ([0-9])[.]  ')
_m0 = ln_of(3, u'SHOULD resend the original request message with the following')
_m1 = ln_of(3, u'A client SHOULD detect and intervene')
D['mod_step_nums'] = [int(m.group(1)) for n, x in enumerate(L[3], 1)
                      if _m0 < n < _m1 for m in [TOPNUM.match(x)] if m]
D['mod_steps'] = len(D['mod_step_nums'])
D['dep_305_sent'] = rc(QUOT[3], u'The 305 (Use Proxy) status code was defined in a previous version')
D['dep_all'] = rc(QUOT[3], u'is now deprecated')
D['claim_four_n'] = [sum(1 for k in CFOUR if D[k][i]) for i in range(NSRC)]

# ---------- 判定重算(同一批判词, 全部由本遍读数现推) ----------
CL = {}
CL[u'confirm_gate_only_2616'] = 1 if (D[u'tier_confirm_gate'][0]
                                      and sum(D[u'tier_confirm_gate'][1:]) == 0) else 0
CL[u'may_change_pair'] = 1 if (D[u'tierq_may_change'][1] and D[u'tierq_may_change'][3]
                               and not D[u'tierq_may_change'][0]
                               and not D[u'tierq_may_change'][2]) else 0
CL[u'not_allow_changing_pair'] = 1 if (D[u'tierq_not_allow_changing'][1]
                                       and D[u'tierq_not_allow_changing'][2]
                                       and not D[u'tierq_not_allow_changing'][0]
                                       and not D[u'tierq_not_allow_changing'][3]) else 0
CL[u'erroneously_outer_pair'] = 1 if (D[u'tierq_erroneously'][0] and D[u'tierq_erroneously'][3]
                                      and not D[u'tierq_erroneously'][1]
                                      and not D[u'tierq_erroneously'][2]) else 0
CL[u'quot_only_9110'] = 1 if (D[u'quot_only_own'][3] and sum(D[u'quot_only_own'][:3]) == 0) else 0
CL[u'sh_minus_fold_zero'] = 0 if sum(D[u'sh_minus_fold']) == 0 else 1
CL[u'no_ff_only_9110'] = 0 if (D[u'ff'][3] == 0 and sum(D[u'ff'][:3])) else 1
CL[u'code_n_desc'] = 0 if (D[u'code_n'][0] == 8 and D[u'code_n'][1] == 7
                           and D[u'code_n'][2] == 1 and D[u'code_n'][3] == 9) else 1
CL[u'304_absent_in_7231'] = 1 if (u'304' not in D[u'codes'][1] and u'304' in D[u'codes'][0]
                                  and u'304' in D[u'codes'][3]) else 0
CL[u'308_only_7538_9110'] = 1 if all(u'308' in D[u'codes'][i] for i in (2, 3)) \
    and not any(u'308' in D[u'codes'][i] for i in (0, 1)) else 0
CL[u'year_order_ok'] = 0 if D[u'year_inversions'] == 0 and D[u'year_order'] == 1 else 1
CL[u'obs_chain'] = 1 if (2068 in OBS[0] and 2616 in OBS[1] and 7231 in OBS[3]
                         and 2616 not in OBS[3]) else 0
CL[u'7538_obsoletes_own_draft'] = 1 if D[u'obs_ids'][2] == [7238] else 0
CL[u'bom_only_9110'] = 0 if sum(D[u'bom']) == 1 and D[u'bom'][3] else 1
CL[u'nonascii_only_9110'] = 0 if D[u'ascii_all'] == 3 and D[u'nonascii'][3] else 1
CL[u'up_ledger_zero'] = 0 if sum(D[u'up_ledger']) == 0 else 1
CL[u'case_ledger_zero'] = 0 if sum([abs(x) for x in D[u'case_ledger']]) == 0 else 1
CL[u'lines_split_zero'] = 0 if D[u'lines_split_close'] == 0 and sum(D[u'tail_nl']) == NSRC else 1
CL[u'shell_308_only_7538'] = 1 if (D[u's308_shell'][2]
                                   and sum(D[u's308_shell']) == D[u's308_shell'][2]) else 0
CL[u'pick_overstrip_only_2616'] = 1 if (sum(D[u'shell_pick_only']) == D[u'shell_pick_only'][0]
                                        and D[u'shell_pick_only'][0]) else 0
CL[u'ser_pair'] = 1 if (D[u'ser_fold_hit'] and not D[u'ser_quot_hit']
                        and D[u'ser_fold_hit'] == D[u'n_a9110_302_hist_may'][3]) else 0
CL[u'mod_step_seq'] = 1 if D[u'mod_step_nums'] == [1, 2, 3, 4, 5] else 0
CL[u'mod_step_has_rewrite'] = 1 if (D[u'ln_step_9110'] > _m0 and D[u'ln_step_9110'] < _m1) else 0
CL[u'dep_305_one'] = 1 if (D[u'dep_305_sent'] == 1 and D[u'dep_all'] == 2) else 0
CL[u'step_before_hist'] = 1 if D[u'hist_step_gap'] < 0 else 0
CL[u'hist_after_7231'] = 1 if D[u'hist_mustnot_gap'] > 0 else 0
CL[u'claim_four_none_all'] = 1 if (max(D[u'claim_four_n']) < len(CFOUR)
                                   and sum(D[u'claim_four_n']) >= 2) else 0
D.update(CL)

# ---------- 与采集侧(_b72meas.json)在本遍读数上重跑对账 ----------
AGREE, DIFF = [], []
for k in (u'bytes', u'chars', u'lines', u'nonblank', u'ff', u'cr', u'nonascii', u'bom', u'maxlen',
          u'byte_cp_delta', u'nonascii_extra', u'pipe_lines'):
    (AGREE if D[k] == MEA[k] else DIFF).append((k, D[k], MEA[k]))
D[u'shell_pick_measured'] = MEA[u'shell_n']
D[u'shell_close_vs_pick'] = [1 if D[u'shell_pick'][i] == MEA[u'shell_n'][i] else 0
                             for i in range(NSRC)]
D[u'needle_table_pick'] = MEA[u'needle_n']
D[u'needle_table_mk'] = D[u'needle_n']
PKEY = dict((w, j) for j, w in enumerate(MEA[u'tier_pats']))
TSHR = [(k, w) for k, w in TIER.items() if w in PKEY]
D[u'tier_shared'] = sorted(w for k, w in TSHR)
D[u'tier_shared_n'] = len(D[u'tier_shared'])
D[u'tier_pick_only'] = sorted(w for w in MEA[u'tier_pats'] if w not in TIER.values())
D[u'tier_mk_only'] = sorted(w for k, w in TIER.items() if w not in PKEY)
TC = []
for k, w in TSHR:
    j = PKEY[w]
    TC.append(1 if [MEA[u'tier_faces'][i][j] for i in range(NSRC)] == D[u'tierq_' + k] else 0)
D[u'tier_cross_agree'] = TC
D[u'tier_cross_n'] = len(TC)
D[u'pick_vs_mk_ladder'] = [D[u'sn_strict_docs'], D[u'sn_fold_docs'], D[u'sn_sh_docs'],
                           D[u'sn_quot_docs']]
D[u'pick_ladder'] = [MEA[u'sn_strict_docs'], MEA[u'sn_fold_docs'], MEA[u'sn_sh_docs'],
                     MEA[u'sn_quote_docs']]
D[u'pick_agree'] = len(AGREE)
D[u'pick_diff'] = len(DIFF) + (D[u'tier_cross_n'] - sum(TC))

# ---------- 锚: 双轨归属(逐行 membership ⇎ 整篇归一串 substring) ----------
TAGS = LBL
IDX = dict((t, n) for n, t in enumerate(TAGS))
TT = io.open(ENTRY, encoding='utf-8').read()
_tl = TT.split(NL)
_i = _tl.index(u'## ⟪BabelTele⟫')
_j = len(_tl) - 1
while _j > _i and not _tl[_j].startswith(u'## '):
    _j -= 1
BODY = NL.join(_tl[_i + 1:_j])
USED = BODY.count(u'⟨')
ANCHS = set(re.findall(u'⟨([^⟨⟩]+)⟩', BODY))
DIST = len(ANCHS)
TAGN = dict((t, len(re.findall(u'⟦' + t + u'⟧', BODY))) for t in TAGS)
CITES = re.findall(u'⟦(' + u'|'.join(TAGS) + u')⟧⟨([^⟨⟩]+)⟩', BODY)
assert len(CITES) == USED, (len(CITES), USED)
ERR = [x for x in CITES if pn(x[1]) not in FO[IDX[x[0]]]]
MISSLINE = [x for x in CITES if x[1] not in L[IDX[x[0]]]]
assert not ERR, ERR[:3]
assert not MISSLINE, MISSLINE[:3]
HITC = dict((a, tuple(i for i in range(NSRC) if pn(a) in FO[i])) for a in ANCHS)
CLS = {u'single': len([a for a in ANCHS if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC]),
       u'all4': len([a for a in ANCHS if len(HITC[a]) == NSRC])}
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all4'] == DIST
D[u'anchor_total'] = USED
D[u'anchor_distinct'] = DIST
D[u'anchor_err'] = len(ERR)
D[u'anchor_single'] = CLS[u'single']
D[u'anchor_cross'] = CLS[u'cross']
D[u'anchor_all4'] = CLS[u'all4']
D[u'checks'] = DIST * NSRC
D[u'enc_chars'] = len(BODY.replace(NL, u''))
D[u'nsrc'] = NSRC
for t in TAGS:
    D[u'tag_' + t] = TAGN[t]

# ---------- 恒等式: 从 _mkB72.py 的 SCAN 段回读算式, 在本遍读数上重跑 ----------
ZPAIRS = []
for st in ast.walk(ast.parse(SCAN.replace(u'\nexec(', u'\n#exec('))):
    if isinstance(st, ast.Call) and getattr(st.func, u'id', u'') == u'Z':
        ZPAIRS.append((ast.literal_eval(st.args[0]), ast.literal_eval(st.args[1])))
# SCAN 段落到 “F['键'] =” 字面赋值目标上的键集(清单式闭合按第二遍的登记时机数, 不含 emit 段并进来的)
SCAN_KEYS = set(re.findall(u"F\\[u?'([a-z0-9_]+)'\\] *= *", SCAN))


def _jr(x):
    return json.loads(json.dumps(x))


NSV = dict(FLAT)
NSV.update(D)
B72V = lambda k, i=None: (NSV[k] if i is None else NSV[k][i])
NV = {u'F': NSV, u'CLOSE': NSV, u'NSRC': NSRC, u'range': range}
ZRES = [(e, w, eval(e, NV)) for e, w in ZPAIRS]
D[u'zid_n'] = len(ZPAIRS)
D[u'x_ident_n'] = len(ZPAIRS)
D[u'scalar_clos_n'] = len(ZPAIRS)
D[u'scalar_clos_sum'] = len([1 for e, w, r in ZRES if r == 0])
D[u'zid_fail'] = [w for e, w, r in ZRES if r != 0]
D[u'list_clos_n'] = len([k for k in D if k in SCAN_KEYS and (u'_close' in k or u'_ledger' in k)
                         and isinstance(D[k], list)])
D[u'contract_n'] = len(D) + 1
# 第二道: checks 里登记的 B72V 形(含 emit 段并进来的 11 条)也在本遍读数上重跑
ZV = [(e, w, eval(e, {}, {u'B72V': B72V})) for e, w in CH[u'zid']]
ZVFAIL = [w for e, w, r in ZV if r != 0]
assert not ZVFAIL, ZVFAIL[:4]
DFAIL = []
for kk, v in JJ.items():
    try:
        g = eval(v, {}, {u'B72V': B72V})
    except Exception as e:
        DFAIL.append((kk, repr(e)))
        continue
    if str(g) != kk and repr(g) != kk:
        DFAIL.append((kk, v, str(g)))
MISS = [k for k in D if k not in FLAT]
BAD = [(k, _jr(D[k]), _jr(FLAT[k])) for k in D if k in FLAT and _jr(D[k]) != _jr(FLAT[k])]
UNCOVER = [k for k in FLAT if k not in D]
assert not ZRES or not [1 for e, w, r in ZRES if r != 0], D[u'zid_fail'][:4]
assert not DFAIL, DFAIL[:4]
assert not MISS, MISS[:6]
assert not UNCOVER, UNCOVER[:6]
assert not BAD, BAD[:6]
assert D[u'anchor_err'] == 0 and D[u'pick_diff'] == 0 and sum(D[u'shell_close_vs_pick']) == NSRC
assert sum(D[u'tier_cross_agree']) == D[u'tier_cross_n'] == 4
assert D[u'ladder_monotone'] == 1 and D[u're_eq_cur'] == 1 and sum(D[u'sh_minus_fold']) == 0
assert D[u'pair_close'] == 0 and D[u'union_close'] == 0 and D[u'pool_tier_close'] == 0
assert D[u'apool_tag_close'] == 0 and D[u'apool_tier_close'] == 0 and D[u'axis_close'] == 0
assert D[u'win_close_sum'] == 0 and D[u'w_row_close'] == 0 and sum(D[u'tone_ledger']) == 0
assert sum(D[u'up_ledger']) == 0 and sum([abs(x) for x in D[u'case_ledger']]) == 0
assert D[u'lines_split_close'] == 0 and sum(D[u'tail_nl']) == NSRC
assert D[u'dead_n'] == D[u'neg_ctrl_n'] + D[u'ser_n'] and D[u'neg_hit_widest'] == 0
assert D[u'quot_lost_nonserv'] == 0 and D[u'dead_nonneg'] == 0
assert D[u'blk_same_7231_9110'] == 1 and D[u'blk_identical_chars'] == 1
assert sum(D[u'bar_removed']) == sum(D[u'bar_removed_line'])
assert D[u'ser_fold_hit'] == D[u'n_a9110_302_hist_may'][3] and D[u'ser_quot_hit'] == 0

# ---------- ⛓解读注 ----------
L2 = []
A = L2.append
A(u"第四遍(`corpus/_fill72.py`)换算法不换定义地重跑一遍: 读面走 bytes 再 decode ⇎ 行界三档对拍(按换行切格"
  u" ⇎ 换行计数加一 ⇎ `splitlines()`) ⇎ 换页符走 `findall` 档 ⇎ 针计数一律走 `findall(re.escape(针))`, 重叠口径另数"
  u" `(?=针)`(第二遍是非重叠游标 find, 第一遍是 `str.count`) ⇎ 四档面换构造: 折平走 `re.sub` 空白折叠, 摘壳走"
  u" “先挑非壳行再折”, 剥引文走手写逐字符吃标记(先剥行首空白再吃一枚竖线与至多一枚空格, 行尾 `rstrip` 后吃一枚"
  u" 竖线) ⇎ 义务语气走“游标定位后只验左右邻是否 ASCII 字母”的整词档 ⇎ 抬头字段走“逐行前缀命中后按双空格切”"
  u" 的档, 年份走“月名 token 紧跟四位数字 token”的相邻对档 ⇎ 段的起止行由剥引文折平偏移经 `bisect_right` 映回"
  u" 原行号(第二遍是线性游标扫描) ⇎ 池代数走 dict-of-set 与逐字节变体集求交 ⇎ 锚归属走双轨(原文件逐行 membership"
  u" ⇎ 整篇归一串 substring)。壳谓词与剥引文谓词的**定义**从 `_mkB72.py` 源码 exec 进来复用——要换的是量, 不是定义。")
A(u"本遍复算 %d 个键(扁平表 %d 键中覆盖 %d 枚 ⇎ 本遍独有 %d ⇎ 未复算 %d ⇎ 逐值不符 %d); SCAN 段登记的标量恒等式"
  u" %d 条在本注读数上重跑全为真(通过 %d) ⇎ `checks` 里的 V 形恒等式 %d 条(比 SCAN 段多 %d 条, 多的那批在 emit 段"
  u"并进来)同样全真; DERIV %d 条复算点重跑全对(引用 %d 处)。" % (
      len(D), len(FLAT), len([k for k in D if k in FLAT]), len(MISS), len(UNCOVER), len(BAD),
      len(ZPAIRS), D[u'scalar_clos_sum'], len(CH[u'zid']), len(CH[u'zid']) - len(ZPAIRS),
      len(JJ), sum(len(v.split(u'B72V(')) - 1 for v in JJ.values())))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"行界⇎换页", u"按换行切格 ⇎ 换行计数加一 ⇎ `splitlines()` ⇎ 换页符 `findall` 档",
     u"行数 %s ⇎ 换行档 %s ⇎ splitlines %s ⇎ 换页符 %s ⇎ 末行有换行符 %d 份 ⇎ 剥壳剩 %s 行" % (
         J(D[u'lines']), J(D[u'lines_nl']), J(D[u'lines_split']), J(D[u'ff']),
         sum(D[u'tail_nl']), J(D[u'shell_strip'])),
     u"splitlines 档 = 换行档 − 末行换行 + 换页符枚数, 四份闭合 %d(判定 %d): 9110 面上零枚换页符(%s), "
     u"它对摘壳档近乎空操作。" % (D[u'lines_split_close'], D[u'lines_split_zero'], J(D[u'ff']))),
    (u"剥引文两把尺", u"两面相减的 glyph 尺 ⇎ 逐行剥前后各数一次的行尺(手写档)",
     u"折平面竖线 %s ⇎ 剥后 %s ⇎ 被剥 %s 枚 ⇎ 行尺 %s 枚 ⇎ 含竖线行 %s" % (
         J(D[u'bar_fold']), J(D[u'bar_quot']), J(D[u'bar_removed']), J(D[u'bar_removed_line']),
         J(D[u'pipe_lines'])),
     u"两尺逐份同值(合计差 %d): 竖线从不跨行断; 前三份的竖线是 ABNF 与表格边框, 只有 9110 用它排引文块"
     u"(含竖线行 %d 行 ⇎ 其余三份 %s)。" % (sum(D[u'bar_removed']) - sum(D[u'bar_removed_line']),
                                            D[u'pipe_lines'][3], J(D[u'pipe_lines'][:3]))),
    (u"四档阶梯", u"摘壳走“先挑行再折”, 剥引文走手写吃标记; 计数全换 findall",
     u"逐行 %s ⇎ 折平 %s ⇎ 摘壳 %s ⇎ 剥引文 %s 枚 ⇎ 折行独有 %d 枚(按份 %s) ⇎ 剥引文独有 %s" % (
         J(D[u'sn_strict_docs']), J(D[u'sn_fold_docs']), J(D[u'sn_sh_docs']), J(D[u'sn_quot_docs']),
         D[u'fold_only_n'], J(D[u'fold_only_own']), D[u'quot_only_str']),
     u"阶梯单调 %d ⇎ 摘壳一粒不丢(差 %s) ⇎ 剥引文净增只落 9110(判定 %d); 25 枚针里只有 %d 枚能在单行读全, "
     u"7538 名下 %d 枚在逐行档全空。" % (D[u'ladder_monotone'], J(D[u'sh_minus_fold']),
                                        D[u'quot_only_9110'], sum(D[u'sn_strict_docs']),
                                        D[u'needles_owned'][2] - D[u'sn_strict_docs'][2])),
    (u"序列化对照", u"同一句的带竖线版 ⇎ 剥竖线版各数一遍(fold 档走折平, quot 档走手写剥)",
     u"带竖线在折平 %d 枚 ⇎ 剥引文 %d 枚 ⇎ 不带竖线在剥引文 %d 枚 ⇎ 判定 %d" % (
         D[u'ser_fold_hit'], D[u'ser_quot_hit'], D[u'n_a9110_302_hist_may'][3], D[u'ser_pair']),
     u"最宽档落空的针 %d 枚 = 反向对照 %d + 序列化对照 %d, 内容死针 %d 枚 ⇎ 剥引文档丢针 %d 枚(全为序列化对照); "
     u"两枚新增针 %s 都是被竖线楔住的句子。" % (D[u'dead_n'], D[u'neg_ctrl_n'], D[u'ser_n'],
                                               D[u'dead_nonneg'], D[u'quot_lost_n'], D[u'quot_only_str'])),
    (u"六族措辞", u"折平档数 `tier_` ⇎ 剥引文档数 `tierq_`(同一组六条字面, 只换面)",
     u"折平合计 %s ⇎ 剥引文合计 %s ⇎ 增益 %s ⇎ 确认门 %s ⇎ MAY change %s ⇎ 不允许改 %s" % (
         J(D[u'tier_fold_tot']), J(D[u'tier_quot_tot']), J(D[u'tier_gain']),
         J(D[u'tierq_confirm_gate']), J(D[u'tierq_may_change']), J(D[u'tierq_not_allow_changing'])),
     u"闭合 %d(增益=剥引文档新增针数) ⇎ 判定: 确认门只在 2616 %d ⇎ MAY change 恰在 7231⇎9110 %d ⇎ "
     u"不允许改只活中间两份 %d ⇎ erroneously 只在首尾 %d ⇎ 四种说法没有一份给全 %d(按份 %s)。" % (
         D[u'tier_sum_close'], D[u'confirm_gate_only_2616'], D[u'may_change_pair'],
         D[u'not_allow_changing_pair'], D[u'erroneously_outer_pair'], D[u'claim_four_none_all'],
         J(D[u'claim_four_n']))),
    (u"两遍壳账", u"照抄采集侧谓词逐行复判, 再与本遍壳谓词做集合差",
     u"本遍 %s ⇎ 采集 %s ⇎ 同判 %s ⇎ 只有本遍判壳 %s ⇎ 只有采集判壳 %s ⇎ 差 %s" % (
         J(D[u'shell_n']), J(D[u'shell_pick']), J(D[u'shell_both']), J(D[u'shell_mk_only']),
         J(D[u'shell_pick_only']), J(D[u'shell_diff'])),
     u"本遍多判的 %d 行全是抬头字段行(归因 %s) ⇎ 采集多判的 %d 行全是缩进后“RFC 四位数+空格”开头的正文句(%s), "
     u"逐份相减闭合 %d ⇎ 判定 %d。" % (sum(D[u'shell_mk_only']), J(D[u'shell_mk_only_hdr']),
                                       sum(D[u'shell_pick_only']), J(D[u'shell_pick_only_body']),
                                       sum(D[u'shell_mk_only']) - sum(D[u'shell_mk_only_hdr']),
                                       D[u'pick_overstrip_only_2616'])),
    (u"抬头⇎年表", u"前缀命中后按双空格切 ⇎ 年份走“月名 token+四位数字 token”相邻对",
     u"Obsoletes %s ⇎ Updates %s ⇎ 动作对象并集 %d 枚 ⇎ 年 %s(%s) ⇎ 年距 %s" % (
         J(D[u'obs_ids']), J(D[u'upd_ids']), D[u'target_n'], J(D[u'years']), J(D[u'months']),
         J(D[u'year_gaps'])),
     u"链 2068←2616←7231←9110 判定 %d(9110 的清单里没有 2616) ⇎ 7538 只废止自己的草案期号 %s 判定 %d ⇎ "
     u"年份严格递增 %d ⇎ 倒序 %d 处。" % (D[u'obs_chain'], D[u'obs_ids'][2], D[u'7538_obsoletes_own_draft'],
                                        D[u'year_order'], D[u'year_inversions'])),
]
rows += [
    (u"30x 名分", u"intro 界用 `next()` 现取, 号码由标题行 join 后 `findall` 现采",
     u"小节数 %s ⇎ 清单 %s ⇎ 并集 %d 枚 ⇎ 面上 302 %s ⇎ 307 %s ⇎ 308 %s ⇎ 3xx 数字串 %s" % (
         J(D[u'code_n']), J(D[u'codes']), len(D[u'code_union']), J(D[u'num_sec_302']),
         J(D[u'num_sec_307']), J(D[u'num_sec_308']), J(D[u'num_status_digits'])),
     u"304 在 2616⇎9110 的清单里而 7231 挪走(判定 %d) ⇎ 308 只在 7538⇎9110(判定 %d) ⇎ 小节数降序判定 %d; "
     u"9110 里 305 的名分写成废弃: “is now deprecated” %d 枚 ⇎ 属 305 的 %d 枚(判定 %d)。" % (
         D[u'304_absent_in_7231'], D[u'308_only_7538_9110'], D[u'code_n_desc'],
         D[u'dep_all'], D[u'dep_305_sent'], D[u'dep_305_one'])),
    (u"数字 308 四档", u"四档面各数一遍 ⇎ 壳行内的枚数按逐行判壳后累加",
     u"原面 %s ⇎ 折平 %s ⇎ 摘壳 %s ⇎ 剥引文 %s ⇎ 落在壳行 %s 枚" % (
         J(D[u's308_raw']), J(D[u's308_fold']), J(D[u's308_sh']), J(D[u's308_quot']),
         J(D[u's308_shell'])),
     u"折行与剥引文都不动枚数(%d ⇎ %d); 摘壳少的 %d 枚全在 7538 的页眉(判定 %d)——那份文书整篇讲这枚状态码, "
     u"Running header 把争议号码本身印成页眉。" % (
         sum(D[u's308_raw']) - sum(D[u's308_fold']), sum(D[u's308_quot']) - sum(D[u's308_fold']),
         sum(D[u's308_shell']), D[u'shell_308_only_7538'])),
    (u"引用写法", u"五种字面式各走 findall ⇎ 自引另用一条“RFC[ -]?号|三式并计”的正则族复核",
     u"自引 %s ⇎ [RFC7231] 式 %s 枚 ⇎ 三式账 %s ⇎ 7231→9110 %d 枚 ⇎ 反向 %d 枚" % (
         J(D[u'cite_self']), J(D[u'cite_br_7231']),
         J(D[u'cite_forms_close']), D[u'cite_dir_7231_to_9110'], D[u'cite_dir_9110_to_7231']),
     u"写法族账逐份归零(合计 %d): 空格式+连字符式+紧贴式=一条正则族的枚数 ⇎ 7538 在 7231 面上 %d 枚"
     u"(方向只朝前) ⇎ 1945 全库 %d 枚 ⇎ 2068 全库 %d 枚。" % (
         sum(D[u'cite_forms_close']), D[u'cite_7538_in_7231'], D[u'cite_1945_tot'], D[u'cite_2068_tot'])),
    (u"四段答句", u"段界只按字面针在剥引文折平面上定位, 行号由偏移经 bisect 映回",
     u"起 %s ⇎ 止 %s ⇎ 行数 %s ⇎ 段字符 %s ⇎ 段词 %s" % (
         J(D[u'blk_lo']), J(D[u'blk_hi']), J(D[u'blk_rows']), J(D[u'blk_chars']), J(D[u'blk_words'])),
     u"7231 段与 9110 段逐词等值(共头 %d ⇎ 共尾 %d ⇎ 词序判定 %d ⇎ 字符判定 %d): 9110 整段搬走一个词没动, "
     u"差别只在序列化; 2616 段与 7231 段共尾 %d 词 ⇎ 共头 %d 词。" % (
         D[u'pre_7231_9110'], D[u'suf_7231_9110'], D[u'blk_same_7231_9110'],
         D[u'blk_identical_chars'], D[u'suf_2616_7231'], D[u'pre_2616_7231'])),
    (u"段内语气⇎词集", u"整词档数段内 MUST/MAY/SHOULD ⇎ 词集账用 set 差与交",
     u"MUST %s ⇎ 裸 MUST %s ⇎ MUST NOT %s ⇎ MAY %s ⇎ SHOULD %s ⇎ 大写账 %s" % (
         J(D[u'tone_must']), J(D[u'tone_bare_must']), J(D[u'tone_must_not_blk']), J(D[u'tone_may']),
         J(D[u'tone_should']), J(D[u'tone_ledger'])),
     u"四段的词集账: 7231 段相对 2616 段独有 %d 词 + 两份交集 %d = 7231 段词表 %d(闭合 %d); "
     u"7538 段最长(%d 词)因为它整段在讲 308 的适用条件。" % (
         D[u'blk_only'][1], D[u'blk_common_1'], D[u'blk_vocab'][1], D[u'w_row_close'],
         D[u'blk_vocab'][2])),
    (u"行距⇎次序", u"同一折平面上按字面针取偏移再映回行号, 差值现算",
     u"注⇎当 303 %d 行 ⇎ 历史⇎不得 %d 行 ⇎ 定义⇎限制 %d 行 ⇎ 历史⇎清单 %d 行" % (
         D[u'note_treat_gap'], D[u'hist_mustnot_gap'], D[u'ind_restricted_gap'], D[u'hist_step_gap']),
     u"9110 把改写清单排在历史原因注之前(带签 %d ⇎ 绝对值 %d ⇎ 判定 %d) ⇎ 7231 次序相反, 约束句落在注之后 "
     u"%d 行(判定 %d)。" % (D[u'hist_step_gap'], D[u'step_hist_abs'], D[u'step_before_hist'],
                            D[u'hist_mustnot_gap'], D[u'hist_after_7231'])),
    (u"9110 五步清单", u"顶层编号由“三空格+数字+点+两空格”的形现采, 区间由两根针的行号夹出",
     u"条目 %s ⇎ 条数 %d ⇎ 严格连号判定 %d ⇎ 改写那条在区间内判定 %d" % (
         J(D[u'mod_step_nums']), D[u'mod_steps'], D[u'mod_step_seq'], D[u'mod_step_has_rewrite']),
     u"9110 不只收下 7231 的注, 还把“怎么改写”写成可执行的五步(其中一步就是改方法), 这一步与历史原因注隔 %d 行。"
     % D[u'step_hist_abs']),
    (u"邻域窗", u"答句行由 `next()` 现取, 带外=前段拼后段, 计数走 findall+前瞻两式",
     u"窗 %s..%s(%s 行) ⇎ 窗字符 %s ⇎ 带内 redirect %s ⇎ GET %s ⇎ POST %s ⇎ MUST %s" % (
         J(D[u'win_start']), J(D[u'win_end']), J(D[u'win_rows']), J(D[u'win_chars']),
         J(D[u'win_redirect_in']), J(D[u'win_GET_in']), J(D[u'win_POST_in']), J(D[u'win_MUST_in'])),
     u"数字符带内 %s + 带外 %s = 全篇 %s, 逐份闭合 %s(合计 %d); 带外四轨是带内的数量级外推: "
     u"MUST 带外 %s ⇎ redirect 带外 %s。" % (
         J(D[u'win_dig_in']), J(D[u'win_dig_out']), J(D[u'digit_chars']), J(D[u'win_close_dig']),
         D[u'win_close_sum'], J(D[u'win_MUST_out']), J(D[u'win_redirect_out']))),
]
rows += [
    (u"全篇义务语气", u"整词档(游标+左右邻验字母)⇎ 第二遍的前后瞻正则一把数",
     u"MUST %s ⇎ 裸 %s ⇎ MUST NOT %s ⇎ MAY %s ⇎ SHOULD %s ⇎ SHOULD NOT %s ⇎ MAY NOT %s" % (
         J(D[u'up_must_all']), J(D[u'must_bare']), J(D[u'must_not']), J(D[u'up_may']),
         J(D[u'up_should']), J(D[u'should_not']), J(D[u'may_not'])),
     u"大写账逐份归零(%s, 判定 %d) ⇎ 小写 must %s ⇎ 不分大小写 %s ⇎ 大小写账 %s(判定 %d): "
     u"大写+小写+首字母=不分大小写在四份上同时成立。" % (
         J(D[u'up_ledger']), D[u'up_ledger_zero'], J(D[u'low_must']), J(D[u'ci_must']),
         J(D[u'case_ledger']), D[u'case_ledger_zero'])),
    (u"池⇎配对", u"归一长行走 dict-of-set ⇎ 逐字节同形走“同归一串下两侧的原始行集是否相交”",
     u"池 %d 条 ⇎ 分档 %s ⇎ 最大一对 %s %d 行(逐字节 %d ⇎ 仅归一 %d) ⇎ 六对归一 %s" % (
         D[u'pool_n'], J(D[u'pool_tier']), D[u'pair_max_lbl'], D[u'pair_max'], D[u'pair_max_byte'],
         D[u'pair_max_norm_only'], J(D[u'pair_share'])),
     u"配对代数闭合 %d ⇎ 分档闭合 %d ⇎ 容斥闭合 %d(单份并集 %d) ⇎ 三份及以上同现 %d 条 = 第三+第四档 %d; "
     u"7231⇎9110 这对 1100 行同形而只有 %d 行是被重新 wrap 的——规范血统的物证。" % (
         D[u'pair_close'], D[u'pool_tier_close'], D[u'union_close'], D[u'union_incl'],
         len(D[u's3_examples']), D[u'pool_3'] + D[u'pool_4'], D[u'pair_max_norm_only'])),
    (u"写法分家⇎锚池", u"变体集从“同归一串下的原始行”取, 分桶判据照抄第二遍",
     u"归一同形而逐字节不同 %d 串 ⇎ 四桶 %s ⇎ 非零桶 %d 个 ⇎ 锚候选 %d 条 ⇎ 按标签 %s" % (
         D[u'norm_only_set'], D[u'axis_str'], D[u'axis_str_n'], D[u'apool_n'], J(D[u'apool_tag_n'])),
     u"轴账闭合 %d ⇎ 锚池两本账闭合 %d ⇎ %d(按份数加权 %d = 池条目 %d) ⇎ 最长候选 %d 字符。" % (
         D[u'axis_close'], D[u'apool_tag_close'], D[u'apool_tier_close'], D[u'apool_weight'],
         D[u'apool_raw_n'] - sum(D[u'apool_dup']), D[u'apool_maxlen'])),
    (u"采集侧横比", u"本遍读数重新对一遍 `_b72meas.json`, 而不是抄第二遍的结论",
     u"同定义标量 %d 键相符 ⇎ %d 键不符 ⇎ 针表 %d 枚(采集)⇎ %d 枚(本遍) ⇎ 共有措辞字面 %d 条逐份等值 %s" % (
         D[u'pick_agree'], D[u'pick_diff'], D[u'needle_table_pick'], D[u'needle_table_mk'],
         D[u'tier_shared_n'], J(D[u'tier_cross_agree'])),
     u"针表不横比(形状不同: 正则片段 ⇎ 锚导出整句), 各档读数 %s ⇎ %s; 壳账不判“相等”而按行分解(%s ⇎ 采集落盘 %s, "
     u"逐份闭合 %s); 只在一侧的措辞字面 %s ⇎ %s。" % (
         J(D[u'pick_ladder'][0]), J(D[u'pick_vs_mk_ladder'][0]), J(D[u'shell_pick']),
         J(D[u'shell_pick_measured']), J(D[u'shell_close_vs_pick']),
         u' ⇎ '.join(D[u'tier_pick_only']), u' ⇎ '.join(D[u'tier_mk_only']))),
    (u"锚双轨", u"归属: 原文件逐行 membership ⇎ 计数: 整篇归一串 substring(两轨同判才计)",
     u"引用 %d 处 ⇎ 去重 %d 枚 ⇎ 一源 %d ⇎ 二至三源 %d ⇎ 四源 %d ⇎ 错配 %d ⇎ 判定 %d 项" % (
         D[u'anchor_total'], D[u'anchor_distinct'], D[u'anchor_single'], D[u'anchor_cross'],
         D[u'anchor_all4'], D[u'anchor_err'], D[u'checks']),
     u"按标签 %s 处(合计 %d) ⇎ 编码区 %d 字符 ⇎ 源数 %d: 每枚锚都同时通过两轨, 缺一枚即归属错配。" % (
         J([D[u'tag_' + t] for t in TAGS]), sum([D[u'tag_' + t] for t in TAGS]),
         D[u'enc_chars'], D[u'nsrc'])),
    (u"账架", u"恒等式算式从 `_mkB72.py` 的 SCAN 段回读后在本遍读数上 eval, 不重打一遍",
     u"标量恒等式 %d 条(通过 %d) ⇎ 清单式闭合 %d 项 ⇎ checks 里 V 形 %d 条全真 ⇎ DERIV %d 键" % (
         D[u'scalar_clos_n'], D[u'scalar_clos_sum'], D[u'list_clos_n'], len(CH[u'zid']), len(JJ)),
     u"扁平表 %d 键全数复算 ⇎ 逐值不符 %d ⇎ 未复算 %d ⇎ 本遍独有 %d ⇎ 判定 %d 项重算全部同值。" % (
         len(FLAT), len(BAD), len(UNCOVER), len(MISS), len(CL))),
]
for r in rows:
    A(u"| %s | %s | %s | %s |" % r)
A(u"")
A(u"### 本注的判断")
A(u"四份文书对“302 之后能不能把 POST 改成 GET”给的是四种可数的答法, 而不是四种含糊: "
  u"2616 用确认门把自动重定向挡住(“MUST NOT automatically redirect”剥引文面 %d 枚, 只在 2616 存活, 判定 %d), "
  u"同段又把 302 说成实现都当 303 用, 通往 GET 的正门是 303 的取回句; "
  u"7231 换成“出于历史原因 MAY change”(该措辞在 7231⇎9110 两份读得到, 判定 %d), 并补一句“MUST NOT change the "
  u"request method”——它排在历史原因注之后 %d 行(判定 %d), 即将允许读成例外; "
  u"7538 不谈改写, 只另立 308 并把义务写成散文 ought to(该份只有 %d 枚大写 MUST), 30x 小节清单缩到 1 枚; "
  u"9110 收下 7231 的那句注、逐词没动(共头 %d ⇎ 共尾 %d, 词序判定 %d), 却把它楔进竖线引文块——不剥引文标记就一枚"
  u"读不到(新增 %d 枚只发生在 9110, 判定 %d)——同时把改写动作列成五条编号清单(%s), 清单排在注之前 %d 行(判定 %d)。"
  u"所以“能不能改”的条文差, 在本库字节上等价于: 确认门 ⇎ 历史原因下的 MAY+例外约束 ⇎ 换一枚状态码避开含混 ⇎ "
  u"承认既成事实并给出步骤。" % (
      D[u'tierq_confirm_gate'][0], D[u'confirm_gate_only_2616'], D[u'may_change_pair'],
      D[u'hist_mustnot_gap'], D[u'hist_after_7231'], D[u'up_must_all'][2], D[u'pre_7231_9110'],
      D[u'suf_7231_9110'], D[u'blk_same_7231_9110'], D[u'quot_only_n'], D[u'quot_only_9110'],
      u','.join([str(x) for x in D[u'mod_step_nums']]), D[u'step_hist_abs'], D[u'step_before_hist']))
A(u"另一条只在本遍才显形的判断: 内容针从不因换档而丢(%d 枚最宽档落空的针里, 内容针 %d 枚, 全部是反向对照 %d 枚"
  u"+序列化对照 %d 枚), 而 9110 面上 308 的枚数在四档里 %s ⇎ %s ⇎ %s ⇎ %s——被行界、壳行、引文竖线三种排版层折腾的"
  u"从来只是可见性, 不是内容; 7538 是唯一被页眉偷走 %d 枚的(%s), 它整份文书就在讲这一枚码。" % (
      D[u'dead_n'], D[u'dead_nonneg'], D[u'neg_ctrl_n'], D[u'ser_n'], J(D[u's308_raw']),
      J(D[u's308_fold']), J(D[u's308_sh']), J(D[u's308_quot']), sum(D[u's308_shell']),
      J(D[u's308_shell'])))
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"四份 .txt 在 RFC Editor 上的现行状态(是否已被后续文书更新或废止)⇎ 真实浏览器与通用客户端今天到底改写不改写 "
  u"POST ⇎ 9110 那句 “eventually converged on changing the method to GET” 对业界实践的陈述是否属实 ⇎ "
  u"除 7538 之外还有哪些文书处理 308 ⇎ 9110 的 30 枚非 ASCII 码位具体落在哪些词(只数了枚数与字节差)⇎ "
  u"2616 的哪些条款被 9110 隔着 7231 逐条继承——这些都需要在库外的字节或实时状态, 本库四份文件给不出判据。")
NEW = u"## ⛓解读注" + NL + NL + NL.join(L2) + NL
_i2 = TT.index(u"## ⛓解读注")
out = TT[:_i2] + NEW
assert out.count(u"## ⛓解读注") == 1
T2 = ENTRY + u'.tmp'
io.open(T2, 'w', encoding='utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"⛓解读注 已写入 %s ｜ 表 %d 行 ⇎ 注区 %d 字符 ⇎ 复算 %d 键 ⇎ 不符 %d ⇎ 独有 %d ⇎ 未复算 %d ⇎ "
      u"恒等式 %d/%d ⇎ V 形 %d 条 ⇎ DERIV %d 键全对"
      % (ENTRY, len(rows), len(NEW), len(D), len(BAD), len(MISS), len(UNCOVER),
         D[u'scalar_clos_sum'], D[u'scalar_clos_n'], len(CH[u'zid']), len(JJ)))
