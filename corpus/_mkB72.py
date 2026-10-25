# -*- coding: utf-8 -*-
"""建条目第二遍(B72): “收到 30x 之后 POST 到底能不能改成 GET”, 交四份 HTTP 一手规范各答一遍:
2616(99) 正文 MUST NOT 自动重定向 + 注释自认“1945/2068 说不允许, 而实现都当 303 用” ⇎
7231(14) 把确认门整句删掉, 改注“历史理由 MAY 把 POST 改成 GET”, 307 才 MUST NOT change ⇎
7538(15) 不自改 302, 另立 308 说“it does not allow changing the request method from POST to GET” ⇎
9110(22) 收下 MAY 那句但把它排成竖线引文块, 正文另给叙述式(converged on changing)与步骤式(Change the request method…)两轨。

本遍与采集侧(_pick72.py, 正则字面轨)换实现: 非重叠游标 ⇎ 集合代数 ⇎ 句子由锚位置导出而非手打;
四档阶梯=原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 剥引文竖线折平(第四档是本条新增的转义层, 9110 的 MAY 句只在它上面读得到)。
所有正文数字都由 V()/J()/EXPR() 注册后插值, 一枚都不手打; 键名等于所量之物。"""
import io, itertools, json, re, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'2616', u'7231', u'7538', u'9110']
NSRC = 4
PATH = [u'corpus/raw/httpRedir/rfc2616.txt', u'corpus/raw/httpRedir/rfc7231.txt',
        u'corpus/raw/httpRedir/rfc7538.txt', u'corpus/raw/httpRedir/rfc9110.txt']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire72.py 把这一段 ⇎ _mk72emit.py 的 SCAN2 段机械切进 audit.py::_b72_scan)


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
L = [t.split(u'\n') for t in T]


def pnorm(s):
    return u' '.join(s.lower().split())


def cnt_cur(hay, nd):
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def cnt_ovl(hay, nd):
    c, i = 0, 0
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + 1


def read_after(hay, token, pat):
    i = hay.find(token)
    if i < 0:
        return None
    m = re.compile(pat).search(hay, i + len(token))
    return None if not m else m.group(1)


def shell_line(l):
    if l.strip() == u'':
        return True
    if u'\x0c' in l:
        return True
    if re.match(u'^\\s*\\[?Page \\d+\\]?\\s*$', l):
        return True
    if re.match(u'^\\s*RFC \\d+\\s+\\S.*\\s([A-Z][a-z]+ \\d{4}|\\d{4})\\s*$', l):
        return True
    if re.match(u'^\\s*\\S.*\\s(Standards Track|Experimental|Informational|Historic)\\s+\\[?P?age? ?\\d*\\]?\\s*$', l):
        return True
    if re.match(u'^\\s*Network Working Group\\s+\\S.*$', l):
        return True
    if re.match(u'^\\s*(Request for Comments:|Obsoletes:|Updates:|Category:|ISSN:|Internet-Draft)', l):
        return True
    return False


def dequote(x):
    """剥 9110 的竖线引文标记: 行首 `| ` 与行尾 `|` 各是一枚排版层, 不是内容"""
    y = re.sub(u'^\\s*\\| ?', u'', x)
    return re.sub(u'\\|\\s*$', u'', y.rstrip())


def shell_pick_line(x):
    """采集遍的壳谓词, 逐字照抄 _pick72.py 的 is_shell —— 只为把两遍的壳账拆开到行"""
    s = x.rstrip()
    if s == u'':
        return True
    if re.match(u'^[ \\t]*\\S.*\\[Page \\d+\\][ \\t]*$', s):
        return True
    if re.match(u'^[ \\t]*RFC \\d{4} ', s):
        return True
    return False


SH = [[x for x in L[i] if not shell_line(x)] for i in range(NSRC)]
SHF = [u' '.join(u'\n'.join(sh).split()) for sh in SH]
FOLD = [u' '.join(t.split()) for t in T]
QUOT = [u' '.join(u'\n'.join([dequote(x) for x in L[i]]).split()) for i in range(NSRC)]
# 四档面: 0 原面逐行 / 1 全篇折平 / 2 摘壳折平 / 3 剥引文折平
FACES = [L, FOLD, SHF, QUOT]


def hit_face(k, tier):
    nd = TEXT[k]
    o = OWNER[k]
    if tier == 0:
        return cnt_cur(u'\n'.join([x for x in L[o] if nd in x]), nd)
    if tier == 1:
        return cnt_cur(FOLD[o], nd)
    if tier == 2:
        return cnt_cur(SHF[o], nd)
    return cnt_cur(QUOT[o], nd)


# ---------- 针: 由锚位置从最宽档面导出整句, 不手打 ----------
SENT = [
    (0, u'a2616_301_confirm', u'the user agent MUST NOT automatically redirect', u'was issued.'),
    (0, u'a2616_301_erroneous', u'some existing HTTP/1.0 user agents will', u'GET request.'),
    (0, u'a2616_302_not_allowed', u'RFC 1945 and RFC 2068 specify', u'redirected request.'),
    (0, u'a2616_302_treat_as_303', u'most existing user agent implementations', u'request method.'),
    (0, u'a2616_303_get', u'SHOULD be retrieved using', u'that resource.'),
    (0, u'a2616_307_repeat', u'the information necessary for a user', u'new URI.'),
    (0, u'a2616_no_historical', u'@For historical reasons', u''),
    (1, u'a7231_301_hist_may', u'a user agent MAY change the request', u'subsequent request.'),
    (1, u'a7231_307_must_not_change', u'MUST NOT change the request method', u'to that URI.'),
    (1, u'a7231_306_not_allow', u'does not allow changing the request', u'POST to GET.'),
    (1, u'a7231_303_retrieval', u'can perform a retrieval request', u'using HTTP'),
    (1, u'a7231_302_confirm', u'@MUST NOT automatically redirect', u''),
    (2, u'a7538_308_indicates', u'The 308 (Permanent Redirect) status code', u'enclosed URIs.'),
    (2, u'a7538_308_not_allow', u'does not allow changing the request', u'POST to GET.'),
    (2, u'a7538_cacheable', u'A 308 response is cacheable', u'cache controls'),
    (2, u'a7538_restricted', u'the use of status code 308 is restricted', u'confidence'),
    (2, u'a7538_confirm', u'@MUST NOT automatically redirect', u''),
    (3, u'a9110_302_hist_may', u'For historical reasons, a user agent MAY change', u'subsequent request.'),
    (3, u'a9110_302_hist_may_pipe', u'a user agent MAY change the | request', u'subsequent request.'),
    (3, u'a9110_307_must_not_change', u'MUST NOT change the request method', u'to that URI.'),
    (3, u'a9110_converged', u'converged on changing the method', u'GET.'),
    (3, u'a9110_step', u'Change the request method according', u'status code.'),
    (3, u'a9110_308_indicates', u'The 308 (Permanent Redirect) status code', u'enclosed URIs.'),
    (3, u'a9110_305_deprecated', u'is now deprecated', u'deprecated'),
    (3, u'a9110_confirm', u'@MUST NOT automatically redirect', u''),
]


def mk_nd(i, start, end):
    """在剥引文折平面上由起止锚导出整句(保证字面存在), 返回该句"""
    a = QUOT[i].find(start)
    if a < 0:
        raise AssertionError(u'锚起针落空 %s %s' % (LBL[i], start[:40]))
    b = QUOT[i].find(end, a)
    if b < 0:
        raise AssertionError(u'锚止针落空 %s %s' % (LBL[i], end[:40]))
    return QUOT[i][a:b + len(end)]


TEXT = {}
NEG = [k for o, k, s0, e0 in SENT if s0.startswith(u'@')]
for (o, k, s0, e0) in [(i, k, s, e) for i, k, s, e in SENT if not k.endswith(u'_pipe')]:
    if k in NEG:
        TEXT[k] = s0[1:]
    elif k == u'a9110_302_hist_may_pipe':
        TEXT[k] = u''
    else:
        TEXT[k] = mk_nd(o, s0, e0)
# 带竖线的那一枚直接从含竖线的折平面取, 它是“同一句的两种序列化”的证据针
_a = FOLD[3].find(u'For historical reasons, a user agent MAY change')
_b = FOLD[3].find(u'subsequent request.', _a)
TEXT[u'a9110_302_hist_may_pipe'] = FOLD[3][_a:_b + len(u'subsequent request.')]
assert TEXT[u'a9110_302_hist_may_pipe'] != TEXT[u'a9110_302_hist_may']
OWNER = dict((o, o) for o, k, _, _ in [(i, k, s, e) for i, k, s, e in SENT])
OWNER = dict((k, o) for o, k, _, _ in SENT)
GN = [k for o, k, _, _ in SENT]
LITK.update(TEXT)
SN = dict((k, [hit_face(k, n) for n in range(4)]) for k in GN)
for o, k, _, _ in SENT:
    SN[k] = [hit_face(k, n) for n in range(4)]
    assert k in TEXT and TEXT[k], k
F['needle_n'] = len(GN)
F['sn_strict_docs'] = [len([k for k in GN if OWNER[k] == i and SN[k][0]]) for i in range(NSRC)]
F['sn_fold_docs'] = [len([k for k in GN if OWNER[k] == i and SN[k][1]]) for i in range(NSRC)]
F['sn_sh_docs'] = [len([k for k in GN if OWNER[k] == i and SN[k][2]]) for i in range(NSRC)]
F['sn_quot_docs'] = [len([k for k in GN if OWNER[k] == i and SN[k][3]]) for i in range(NSRC)]
F['fold_only_keys'] = [k for k in GN if not SN[k][0] and SN[k][1]]
F['fold_only_own'] = [len([k for k in F['fold_only_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['fold_only_n'] = len(F['fold_only_keys'])
F['sh_only_keys'] = [k for k in GN if not SN[k][1] and SN[k][2]]
F['quot_only_keys'] = [k for k in GN if not SN[k][2] and SN[k][3]]
F['quot_only_own'] = [len([k for k in F['quot_only_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['quot_minus_sh'] = [F['sn_quot_docs'][i] - F['sn_sh_docs'][i] for i in range(NSRC)]
F['sh_minus_fold'] = [F['sn_fold_docs'][i] - F['sn_sh_docs'][i] for i in range(NSRC)]
SER = [u'a9110_302_hist_may_pipe']
F['ser_controls'] = SER
F['dead_needles'] = [k for k in GN if not SN[k][3] and k not in SER]
F['dead_nonneg'] = len([k for k in F['dead_needles'] if k not in NEG])
F['neg_controls'] = sorted(NEG)
F['neg_hit_widest'] = sum(SN[k][3] for k in NEG)
F['ser_fold_hit'] = SN[u'a9110_302_hist_may_pipe'][1]
F['ser_quot_hit'] = SN[u'a9110_302_hist_may_pipe'][3]
F['quot_lost_keys'] = [k for k in GN if SN[k][2] and not SN[k][3]]
F['quot_lost_n'] = len(F['quot_lost_keys'])
F['quot_lost_nonserv'] = len([k for k in F['quot_lost_keys'] if k not in SER])
F['ladder_monotone'] = 1 if all(F['sn_strict_docs'][i] + F['fold_only_own'][i] == F['sn_fold_docs'][i]
                                and F['sn_sh_docs'][i] <= F['sn_fold_docs'][i]
                                and F['sn_quot_docs'][i] >= F['sn_sh_docs'][i] for i in range(NSRC)) else 0
F['re_eq_cur'] = 1 if all(len(re.findall(re.escape(TEXT[k]), QUOT[OWNER[k]])) == SN[k][3] for k in GN) else 0
F['overlap_extra'] = sum(cnt_ovl(QUOT[OWNER[k]], TEXT[k]) - SN[k][3] for k in GN)
F['needles_owned'] = [len([k for k in GN if OWNER[k] == i]) for i in range(NSRC)]
for o, k, _, _ in SENT:
    F['n_' + k] = SN[k]
F['nd_len'] = [len(TEXT[k]) for k in GN]
F['nd_len_tot'] = sum(F['nd_len'])
F['pipe_needle_pair'] = 1 if (SN[u'a9110_302_hist_may'][1] == 0 and SN[u'a9110_302_hist_may_pipe'][1]
                             and SN[u'a9110_302_hist_may'][3] and SN[u'a9110_302_hist_may_pipe'][3] == 0) else 0

# ---------- 结构面量 ----------
F['bytes'] = [len(b) for b in B]
F['chars'] = [len(t) for t in T]
F['lines'] = [len(L[i]) for i in range(NSRC)]
F['lines_nl'] = [T[i].count(u'\n') + 1 for i in range(NSRC)]
F['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['maxlen'] = [max(len(x) for x in L[i]) for i in range(NSRC)]
F['ff'] = [cnt_cur(T[i], u'\x0c') for i in range(NSRC)]
F['ff_only'] = [len([x for x in L[i] if x.strip() == u'\x0c']) for i in range(NSRC)]
F['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
F['shell_n'] = [len(L[i]) - len(SH[i]) for i in range(NSRC)]
F['shell_strip'] = [len(SH[i]) for i in range(NSRC)]
# 两遍壳谓词的账: 交集/各-self-only, 并把“只有哪一侧判成壳”的行按谓词归因
PICK = [[x for x in L[i] if shell_pick_line(x)] for i in range(NSRC)]
MO = [[x for x in L[i] if shell_line(x) and not shell_pick_line(x)] for i in range(NSRC)]
PO = [[x for x in L[i] if shell_pick_line(x) and not shell_line(x)] for i in range(NSRC)]
F['shell_pick'] = [len(PICK[i]) for i in range(NSRC)]
F['shell_both'] = [F['shell_n'][i] - len(MO[i]) for i in range(NSRC)]
F['shell_mk_only'] = [len(MO[i]) for i in range(NSRC)]
F['shell_pick_only'] = [len(PO[i]) for i in range(NSRC)]
F['shell_diff'] = [F['shell_n'][i] - F['shell_pick'][i] for i in range(NSRC)]
HDRF = re.compile(u'^\\s*(Network Working Group|Request for Comments:|Obsoletes:|Updates:|Category:|ISSN:)')
IND = re.compile(u'^[ \\t]+RFC \\d{4} ')
F['shell_mk_only_hdr'] = [len([x for x in MO[i] if HDRF.match(x)]) for i in range(NSRC)]
F['shell_pick_only_body'] = [len([x for x in PO[i] if IND.match(x)]) for i in range(NSRC)]
F['cr'] = [cnt_cur(T[i], u'\r') for i in range(NSRC)]
F['nonascii'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(NSRC)]
F['bom'] = [1 if b[:3] == b'\xef\xbb\xbf' else 0 for b in B]
F['pipe_lines'] = [len([x for x in L[i] if x.lstrip().startswith(u'|')]) for i in range(NSRC)]
F['pipe_glyphs'] = [cnt_cur(T[i], u'|') for i in range(NSRC)]
F['quot_dropped'] = [F['pipe_glyphs'][i] - (len(FOLD[i]) - len(QUOT[i])) for i in range(NSRC)]
F['quot_face_delta'] = [len(FOLD[i]) - len(QUOT[i]) for i in range(NSRC)]
F['bar_fold'] = [cnt_cur(FOLD[i], u'|') for i in range(NSRC)]
F['bar_quot'] = [cnt_cur(QUOT[i], u'|') for i in range(NSRC)]
F['bar_removed'] = [F['bar_fold'][i] - F['bar_quot'][i] for i in range(NSRC)]
# 第二条尺: 逐行剥前后各数一次竖线, 与“两面相减”的 glyph 尺独立
F['bar_removed_line'] = [sum(x.count(u'|') - dequote(x).count(u'|') for x in L[i]) for i in range(NSRC)]
F['quot_line_n'] = [len([x for x in L[i] if u'|' in x]) for i in range(NSRC)]


def utf8_extra(s):
    return sum(len(c.encode('utf-8')) - 1 for c in s if ord(c) > 127)


F['nonascii_extra'] = [utf8_extra(t) for t in T]
F['byte_cp_delta'] = [F['bytes'][i] - F['chars'][i] for i in range(NSRC)]
F['nul_faces'] = [len([1 for c in t if c == u'\x00']) for t in T]
F['digit_chars'] = [len([c for c in t if c.isdigit()]) for t in T]
F['dblspace'] = [cnt_ovl(T[i], u'  ') for i in range(NSRC)]
F['ascii_all'] = sum(1 for i in range(NSRC) if F['nonascii'][i] == 0)
F['tail_nl'] = [1 if T[i].endswith(u'\n') else 0 for i in range(NSRC)]
F['lines_split'] = [len(T[i].splitlines()) for i in range(NSRC)]
F['lines_split_close'] = sum(F['lines_nl'][i] - F['tail_nl'][i] + F['ff'][i] - F['lines_split'][i]
                             for i in range(NSRC))

# ---------- 头部动作字段与年份 ----------
def hdr_ids(t, field):
    m = re.search(u'(?m)^' + field + u':\\s*(.+)$', t)
    if not m:
        return frozenset()
    val = m.group(1).split(u'  ')[0]
    return frozenset(int(x) for x in re.findall(u'\\d{3,5}', val))


OBS = [hdr_ids(T[i], u'Obsoletes') for i in range(NSRC)]
UPD = [hdr_ids(T[i], u'Updates') for i in range(NSRC)]
F['obs_ids'] = [sorted(s) for s in OBS]
F['upd_ids'] = [sorted(s) for s in UPD]
F['obs_n'] = [len(s) for s in OBS]
F['upd_n'] = [len(s) for s in UPD]
F['target_ids'] = sorted(set().union(*[set(s) for s in OBS + UPD]))
F['target_n'] = len(F['target_ids'])
F['obs_verb'] = [cnt_cur(T[i], u'Obsoletes') for i in range(NSRC)]
F['upd_verb'] = [cnt_cur(T[i], u'Updates') for i in range(NSRC)]
F['cat_std'] = [cnt_cur(T[i], u'Category: Standards Track') for i in range(NSRC)]
F['cat_hdr'] = [len([1 for x in L[i] if re.match(u'^\\s*Category:', x)]) for i in range(NSRC)]
F['issn'] = [cnt_cur(T[i], u'ISSN: 2070-1721') for i in range(NSRC)]
F['std_hdr'] = [len([1 for x in L[i] if re.match(u'^\\s*STD:\\s*\\d+', x)]) for i in range(NSRC)]
MON = u'January|February|March|April|May|June|July|August|September|October|November|December'
RYR = re.compile(u'(%s) +(\\d{4})' % MON)


def hdr_year(lines):
    for x in lines[:60]:
        m = RYR.search(x.strip())
        if m:
            return (int(m.group(2)), m.group(1))
    return (None, None)


YR = [hdr_year(L[i]) for i in range(NSRC)]
F['years'] = [y for y, _ in YR]
F['months'] = [mo for _, mo in YR]
F['year_order'] = 1 if [y for y in F['years']] == sorted(F['years']) else 0
F['year_inversions'] = len([1 for a in range(NSRC) for b in range(a + 1, NSRC)
                            if F['years'][a] > F['years'][b]])
F['year_gaps'] = [F['years'][i + 1] - F['years'][i] for i in range(NSRC - 1)]

# ---------- 30x 小节: 正文标题行(排除 TOC), 码号集与块界 ----------
HDR = [u'^10\\.3\\.\\d+ 30\\d', u'^6\\.4\\.\\d+\\.?  30\\d', u'^3\\.  308 Permanent', u'^15\\.4\\.\\d+\\.?  30\\d']
HEADLN = []
CODES = []
for i in range(NSRC):
    intro = [n for n, x in enumerate(L[i], 1) if re.match(u'^1\\.\\s+Introduction\\s*$', x.rstrip())]
    lo = intro[0] if intro else 0
    hd = [(n, x.strip()) for n, x in enumerate(L[i], 1)
          if re.search(HDR[i], x) and n > lo and len(x.strip()) < 70]
    HEADLN.append(hd)
    CODES.append(re.findall(u'(30\\d)', u' '.join(h[1] for h in hd)))
F['sec_heads'] = [len(h) for h in HEADLN]
F['codes'] = CODES
F['code_n'] = [len(c) for c in CODES]
F['code_union'] = sorted(set().union(*[set(c) for c in CODES]))
F['code_distinct'] = [sorted(set(c)) for c in CODES]
F['head_eof'] = [HEADLN[i][-1][0] if HEADLN[i] else 0 for i in range(NSRC)]
F['head_first_ln'] = [HEADLN[i][0][0] if HEADLN[i] else 0 for i in range(NSRC)]

# ---------- 义务语气四轨 ----------
def ub(s, w):
    return len(re.findall(u'(?<![A-Za-z])' + w + u'(?![A-Za-z])', s))


WORDS = (u'MUST', u'MAY', u'SHOULD')
UP, LO, CI, TI, UPN = {}, {}, {}, {}, {}
for w in WORDS:
    UP[w] = [ub(T[i], w) for i in range(NSRC)]
    LO[w] = [ub(T[i], w.lower()) for i in range(NSRC)]
    CI[w] = [ub(T[i].lower(), w.lower()) for i in range(NSRC)]
    TI[w] = [ub(T[i], w[:1].upper() + w[1:].lower()) for i in range(NSRC)]
for w in (u'MUST NOT', u'MAY NOT', u'SHOULD NOT'):
    UPN[w] = [cnt_cur(T[i], w) for i in range(NSRC)]
F['up_must_all'] = UP[u'MUST']
F['up_may'] = UP[u'MAY']
F['up_should'] = UP[u'SHOULD']
F['must_not'] = UPN[u'MUST NOT']
F['should_not'] = UPN[u'SHOULD NOT']
F['may_not'] = UPN[u'MAY NOT']
F['must_bare'] = [UP[u'MUST'][i] - UPN[u'MUST NOT'][i] for i in range(NSRC)]
F['low_must'] = LO[u'MUST']
F['ci_must'] = CI[u'MUST']
F['title_must'] = TI[u'MUST']
F['case_ledger'] = [sum(CI[w][i] - UP[w][i] - LO[w][i] - TI[w][i] for w in WORDS) for i in range(NSRC)]
F['up_ledger'] = [UP[u'MUST'][i] - (F['must_bare'][i] + UPN[u'MUST NOT'][i]) for i in range(NSRC)]

# ---------- 措辞档轴(同一问题的四族答法, 折平面计数) ----------
TIER = {
    u'confirm_gate': u'MUST NOT automatically redirect',
    u'not_allowed': u'not allowed to change the method',
    u'may_change': u'MAY change the request method',
    u'must_not_change': u'MUST NOT change the request method',
    u'not_allow_changing': u'does not allow changing the request method',
    u'erroneously': u'erroneously',
}
F['tier_words'] = list(TIER.keys())
for k, w in TIER.items():
    F[u'tier_' + k] = [cnt_cur(FOLD[i], w) for i in range(NSRC)]
    F[u'tierq_' + k] = [cnt_cur(QUOT[i], w) for i in range(NSRC)]
F['tier_fold_tot'] = [sum(F[u'tier_' + k][i] for k in TIER) for i in range(NSRC)]
F['tier_quot_tot'] = [sum(F[u'tierq_' + k][i] for k in TIER) for i in range(NSRC)]
F['tier_gain'] = [F['tier_quot_tot'][i] - F['tier_fold_tot'][i] for i in range(NSRC)]
F['tier_sum_close'] = sum(F['tier_gain']) - sum(F['quot_only_own'])
F['post_to_get'] = [cnt_cur(QUOT[i], u'POST to GET') for i in range(NSRC)]
F['hist_reasons'] = [cnt_cur(QUOT[i], u'For historical reasons') for i in range(NSRC)]
F['method_word'] = [ub(T[i], u'method') for i in range(NSRC)]
F['redirect_word'] = [ub(T[i], u'redirect') for i in range(NSRC)]

# ---------- 句内游标读数 ----------
NUM = {}
NUM['codes_named'] = F['code_n']
NUM['status_digits'] = [len(re.findall(u'\\b30\\d\\b', QUOT[i])) for i in range(NSRC)]
NUM['rfc_refs'] = [len(re.findall(u'RFC\\s?\\d{4}', T[i])) for i in range(NSRC)]
NUM['sec_302'] = [cnt_cur(QUOT[i], u'302') for i in range(NSRC)]
NUM['sec_307'] = [cnt_cur(QUOT[i], u'307') for i in range(NSRC)]
NUM['sec_308'] = [cnt_cur(QUOT[i], u'308') for i in range(NSRC)]
NUM['get_word'] = [cnt_cur(QUOT[i], u'GET') for i in range(NSRC)]
NUM['post_word'] = [cnt_cur(QUOT[i], u'POST') for i in range(NSRC)]
for k, v in NUM.items():
    F[u'num_' + k] = v
# 308 这枚数字在四档面上的枚数各数一遍(数字是否跨行断、是否在引文竖线里, 都由这里现读)
F['s308_raw'] = [cnt_cur(T[i], u'308') for i in range(NSRC)]
F['s308_fold'] = [cnt_cur(FOLD[i], u'308') for i in range(NSRC)]
F['s308_sh'] = [cnt_cur(SHF[i], u'308') for i in range(NSRC)]
F['s308_quot'] = [cnt_cur(QUOT[i], u'308') for i in range(NSRC)]
F['s308_shell'] = [len([1 for x in L[i] if shell_line(x) for _ in range(cnt_cur(x, u'308'))])
                   for i in range(NSRC)]
F['num_gap_2616'] = F['years'][1] - F['years'][0]
F['num_gap_9110'] = F['years'][3] - F['years'][2]

# ---------- 引用写法三式 ----------
CITE = {}
for n in (u'1945', u'2068', u'2616', u'2817', u'7231', u'7232', u'7538', u'9110', u'7230', u'7235'):
    CITE['sp_' + n] = [cnt_cur(T[i], u'RFC ' + n) for i in range(NSRC)]
    CITE['hy_' + n] = [cnt_cur(T[i], u'RFC-' + n) for i in range(NSRC)]
    CITE['tk_' + n] = [cnt_cur(T[i], u'RFC' + n) for i in range(NSRC)]
    CITE['al_' + n] = [CITE['sp_' + n][i] + CITE['hy_' + n][i] + CITE['tk_' + n][i] for i in range(NSRC)]
    CITE['br_' + n] = [cnt_cur(T[i], u'[RFC' + n + u']') for i in range(NSRC)]
for k in CITE:
    F['cite_' + k] = CITE[k]
F['cite_self'] = [CITE['al_' + n][i] for i, n in enumerate(LBL)]
F['cite_forms_close'] = [len(re.findall(u'RFC[ -]?%s' % LBL[i], T[i])) - CITE['al_' + LBL[i]][i]
                         for i in range(NSRC)]
F['cite_dir_7231_to_9110'] = CITE['al_7231'][3]
F['cite_dir_9110_to_7231'] = CITE['al_9110'][1]
F['cite_7538_in_9110'] = CITE['al_7538'][3]
F['cite_7538_in_7231'] = CITE['al_7538'][1]
F['cite_2616_in_7231'] = CITE['al_2616'][1]
F['cite_1945_tot'] = sum(CITE['al_1945'])
F['cite_2068_tot'] = sum(CITE['al_2068'])

# ---------- 共用长行池与配对代数 ----------
def pool_lines(i):
    return [x for x in SH[i] if len(pnorm(x)) >= 40]


POOLC = [Counter(pnorm(x) for x in pool_lines(i)) for i in range(NSRC)]
NPOOL = [set(POOLC[i]) for i in range(NSRC)]
pool_all = set().union(*NPOOL)
tier2 = [0, 0, 0, 0]
pres = defaultdict(list)
for a in pool_all:
    ds = tuple(i for i in range(NSRC) if a in NPOOL[i])
    pres[a] = ds
    tier2[len(ds) - 1] += 1
F['pool_n'] = len(pool_all)
F['pool_tier'] = tier2
F['pool_tier_close'] = sum(tier2) - len(pool_all)
F['pool_4'] = tier2[3]
F['pool_3'] = tier2[2]
F['pool_2'] = tier2[1]
F['pool_1'] = tier2[0]
PAIRS = [(a, b) for a, b in itertools.combinations(range(NSRC), 2)]
pair_share, pair_byte, pair_norm_only = [], [], []
for i, j in PAIRS:
    inter = NPOOL[i] & NPOOL[j]
    bo = sum(1 for s in inter if any(pnorm(x) == s and x in SH[j] for x in pool_lines(i)))
    pair_share.append(len(inter))
    pair_byte.append(bo)
    pair_norm_only.append(len(inter) - bo)
F['pair_share'] = pair_share
F['pair_byte'] = pair_byte
F['pair_norm_only'] = pair_norm_only
F['pair_nonzero'] = len([x for x in pair_share if x])
F['pair_close'] = sum(pair_share) - sum(pair_byte) - sum(pair_norm_only)
F['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
mx = max(pair_share)
F['pair_max'] = mx
F['pair_max_idx'] = pair_share.index(mx)
F['pair_max_byte'] = pair_byte[F['pair_max_idx']]
F['pair_max_norm_only'] = pair_norm_only[F['pair_max_idx']]
F['pair_max_lbl'] = F['pair_lbl'][F['pair_max_idx']]
F['s3_examples'] = sorted([a for a, v in pres.items() if len(v) >= 3])
_t1 = sum(len(v) for v in pres.values())
_t2 = sum(len(v) * (len(v) - 1) // 2 for v in pres.values())
_t3 = sum(len(v) * (len(v) - 1) * (len(v) - 2) // 6 for v in pres.values())
_t4 = len([v for v in pres.values() if len(v) == NSRC])
F['pool_incl'] = [_t1, _t2, _t3, _t4]
F['union_incl'] = _t1 - _t2 + _t3 - _t4
F['union_close'] = F['pool_n'] - F['union_incl']
F['shared_norm_only'] = sum(pair_norm_only)

# ---------- 写法分家轴 ----------
axis = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
for a, v in pres.items():
    if len(v) < 2:
        continue
    xs = set()
    for i in v:
        xs |= set(x for x in SH[i] if pnorm(x) == a)
    if len(xs) < 2:
        continue
    o, p = sorted(xs)[0], sorted(xs)[1]
    if len(o) == len(p) and o != p and all(x.lower() == y.lower() for x, y in zip(o, p)):
        axis[u'case'] += 1
    elif (u'-' in o) != (u'-' in p):
        axis[u'hyph'] += 1
    elif len(re.split(u' +', o.strip())) == len(re.split(u' +', p.strip())):
        axis[u'space'] += 1
    else:
        axis[u'multi'] += 1
F['axis_counts'] = axis
F['axis_total'] = sum(axis.values())
F['norm_only_set'] = len([a for a, v in pres.items() if len(v) >= 2
                          and len(set(x for i in v for x in SH[i] if pnorm(x) == a)) > 1])
F['axis_close'] = F['axis_total'] - F['norm_only_set']
F['axis_str'] = u'⇎'.join(u'%s%d' % (a, axis[a]) for a in (u'case', u'hyph', u'space', u'multi'))
F['axis_str_n'] = len([a for a in (u'case', u'hyph', u'space', u'multi') if axis[a]])

# ---------- 锚候选池 ----------
apool = []
for i in range(NSRC):
    for x in SH[i]:
        if len(pnorm(x)) >= 24 and re.search(u'[A-Za-z]', x):
            apool.append((pnorm(x), i))
AP = defaultdict(set)
for a, i in apool:
    AP[a].add(i)
F['apool_n'] = len(AP)
F['apool_raw_n'] = len(apool)
F['apool_face_raw'] = [len([1 for a, k in apool if k == i]) for i in range(NSRC)]
F['apool_tag_n'] = [len([a for a, v in AP.items() if i in v]) for i in range(NSRC)]
F['apool_dup'] = [F['apool_face_raw'][i] - F['apool_tag_n'][i] for i in range(NSRC)]
F['apool_tag_close'] = sum(F['apool_tag_n']) + sum(F['apool_dup']) - F['apool_raw_n']
F['apool_tier'] = [len([a for a, v in AP.items() if len(v) == n]) for n in range(1, NSRC + 1)]
F['apool_weight'] = sum(F['apool_tier'][n] * (n + 1) for n in range(NSRC))
F['apool_pairs'] = sum(F['apool_tag_n'])
F['apool_tier_close'] = F['apool_weight'] - F['apool_pairs']
F['apool_maxlen'] = max(len(a) for a in AP)

# ---------- 答句邻域窗(±BAND 行) ----------
BAND = 20
ANSND = {0: u'RFC 1945 and RFC 2068 specify', 1: u'MAY change the request',
         2: u'the use of status code 308', 3: u'converged on changing'}
TRACKS = {0: (u'redirect', u'GET', u'POST', u'MUST'), 1: (u'redirect', u'GET', u'POST', u'MUST'),
          2: (u'redirect', u'GET', u'POST', u'MUST'), 3: (u'redirect', u'GET', u'POST', u'MUST')}


def ans_line(i):
    for n, x in enumerate(L[i], 1):
        if ANSND[i] in x:
            return n
    return None


WIN = []
for i in range(NSRC):
    a = ans_line(i)
    assert a, LBL[i]
    lo, hi = max(1, a - BAND), min(len(L[i]), a + BAND)
    body = u'\n'.join(L[i][lo - 1:hi])
    outb = u'\n'.join(L[i][:lo - 1] + L[i][hi:])
    fb, fo = u' '.join(body.split()), u' '.join(outb.split())
    w = {u'ans': a, u'start': lo, u'end': hi, u'rows': hi - lo + 1,
         u'chars': len(body), u'chars_out': len(outb)}
    for tr in TRACKS[i]:
        c = cnt_cur(fb, tr)
        w[tr] = c
        w[tr + u'_out'] = cnt_cur(fo, tr) + cnt_ovl(fo, tr) - c * 0
        w[tr + u'_ovl_out'] = cnt_ovl(fo, tr)
    w[u'dig_in'] = len([c for c in body if c.isdigit()])
    w[u'dig_out'] = len([c for c in outb if c.isdigit()])
    WIN.append(w)
for k in (u'ans', u'start', u'end', u'rows', u'chars', u'chars_out', u'dig_in', u'dig_out'):
    F[u'win_' + k] = [w[k] for w in WIN]
for tr in (u'redirect', u'GET', u'POST', u'MUST'):
    F[u'win_' + tr + u'_in'] = [w[tr] for w in WIN]
    F[u'win_' + tr + u'_out'] = [w[tr + u'_out'] for w in WIN]
F['win_band'] = BAND
F['win_spans'] = [w[u'end'] - w[u'start'] + 1 for w in WIN]
F['win_close_dig'] = [WIN[i][u'dig_in'] + WIN[i][u'dig_out'] - F['digit_chars'][i] for i in range(NSRC)]
F['win_close_sum'] = sum(F['win_close_dig'])

# ---------- 闭合判定 ----------
CLOSE = {}
CLOSE[u'confirm_gate_only_2616'] = 1 if (F['tier_confirm_gate'][0]
                                         and sum(F['tier_confirm_gate'][1:]) == 0) else 0
CLOSE[u'may_change_pair'] = 1 if (F['tierq_may_change'][1] and F['tierq_may_change'][3]
                                  and not F['tierq_may_change'][0]
                                  and not F['tierq_may_change'][2]) else 0
CLOSE[u'not_allow_changing_pair'] = 1 if (F['tierq_not_allow_changing'][1]
                                          and F['tierq_not_allow_changing'][2]
                                          and not F['tierq_not_allow_changing'][0]
                                          and not F['tierq_not_allow_changing'][3]) else 0
CLOSE[u'erroneously_outer_pair'] = 1 if (F['tierq_erroneously'][0] and F['tierq_erroneously'][3]
                                         and not F['tierq_erroneously'][1]
                                         and not F['tierq_erroneously'][2]) else 0
CLOSE[u'quot_only_9110'] = 1 if (F['quot_only_own'][3] and sum(F['quot_only_own'][:3]) == 0) else 0
CLOSE[u'pipe_needle_pair'] = F[u'pipe_needle_pair']
CLOSE[u'sh_minus_fold_zero'] = 0 if sum(F['sh_minus_fold']) == 0 else 1
CLOSE[u'no_ff_only_9110'] = 0 if (F['ff'][3] == 0 and sum(F['ff'][:3])) else 1
CLOSE[u'code_n_desc'] = 0 if F['code_n'][0] == 8 and F['code_n'][1] == 7 and F['code_n'][2] == 1 \
    and F['code_n'][3] == 9 else 1
CLOSE[u'304_absent_in_7231'] = 1 if (u'304' not in F['codes'][1] and u'304' in F['codes'][0]
                                     and u'304' in F['codes'][3]) else 0
CLOSE[u'308_only_7538_9110'] = 1 if all(u'308' in F['codes'][i] for i in (2, 3)) \
    and not any(u'308' in F['codes'][i] for i in (0, 1)) else 0
CLOSE[u'year_order_ok'] = 0 if F['year_inversions'] == 0 and F['year_order'] == 1 else 1
CLOSE[u'obs_chain'] = 1 if (2068 in OBS[0] and 2616 in OBS[1] and 7231 in OBS[3]
                            and 2616 not in OBS[3]) else 0
CLOSE[u'7538_obsoletes_own_draft'] = 1 if F['obs_ids'][2] == [7238] else 0
CLOSE[u'bom_only_9110'] = 0 if sum(F['bom']) == 1 and F['bom'][3] else 1
CLOSE[u'nonascii_only_9110'] = 0 if F['ascii_all'] == 3 and F['nonascii'][3] else 1
CLOSE[u'up_ledger_zero'] = 0 if sum(F['up_ledger']) == 0 else 1
CLOSE[u'case_ledger_zero'] = 0 if sum([abs(x) for x in F['case_ledger']]) == 0 else 1
CLOSE[u'lines_split_zero'] = 0 if F['lines_split_close'] == 0 and sum(F['tail_nl']) == NSRC else 1
CLOSE[u'shell_308_only_7538'] = 1 if (F['s308_shell'][2]
                                      and sum(F['s308_shell']) == F['s308_shell'][2]) else 0
CLOSE[u'pick_overstrip_only_2616'] = 1 if (sum(F['shell_pick_only']) == F['shell_pick_only'][0]
                                           and F['shell_pick_only'][0]) else 0
CLOSE[u'ser_pair'] = 1 if (F['ser_fold_hit'] and not F['ser_quot_hit']
                           and F['ser_fold_hit'] == F['n_a9110_302_hist_may'][3]) else 0
for k in CLOSE:
    F[k] = CLOSE[k]

ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"F['ladder_monotone'] - 1", u'四档阶梯单调: 逐行档+折行独有档=折平档, 摘壳≤折平, 剥引文≥摘壳')
Z(u"F['re_eq_cur'] - 1", u'正则字面轨与非重叠游标轨在最宽档上逐枚相等')
Z(u"F['overlap_extra']", u'重叠口径减非重叠口径在全库针上合计为零')
Z(u"sum(F['sh_minus_fold'])", u'摘壳档一枚不丢(壳行里没有答句)')
Z(u"F['dead_nonneg']", u'死集=反向对照针集(内容针在最宽档全读得到)')
Z(u"len(F['neg_controls']) - 4", u'反向对照针恰 4 枚: 2616 无 historical reasons, 后三份无确认门')
Z(u"F['neg_hit_widest']", u'反向针在最宽档合计零命中')
Z(u"F['ser_fold_hit'] * F['ser_quot_hit']", u'带竖线那枚: 折平档读得到、剥引文档一枚不剩')
Z(u"F['ser_fold_hit'] - F['n_a9110_302_hist_may'][3]",
  u'同一句的两种序列化枚数相等: 剥引文只是把它从带竖线搬到不带, 不多造一枚')
Z(u"sum(F['fold_only_own']) - F['fold_only_n']", u'折行独有针按份分账=总数')
Z(u"sum(F['quot_only_own']) - sum(F['quot_minus_sh']) - F['quot_lost_n']",
  u'剥引文档净增(该档−摘壳档)=新增针数−丢针数')
Z(u"F['quot_lost_nonserv']", u'剥引文档丢的只有序列化对照那枚: 内容针在最窄到最宽的换档里一枚不丢')
Z(u"F['tier_sum_close']", u'措辞档全库合计的“剥引文−折平”增益=剥引文独有针数')
Z(u"F['pair_close']", u'两两“归一同形”=“逐字节同形”+“只归一同形”(池代数闭合)')
Z(u"F['pool_tier_close']", u'共用长行按份数分档之和=池条数')
Z(u"F['axis_close']", u'写法分家轴四桶之和=归一同形而逐字节不同的去重串数')
Z(u"F['union_close']", u'容斥对账: 单份并集=Σ单份−Σ两两交+Σ三重−Σ四重')
Z(u"F['apool_tier_close']", u'锚候选池按“几份面上出现”加权分档之和=池条目数')
Z(u"F['apool_tag_close']", u'锚候选池按标签分布之和=池条目数')
Z(u"sum(F['up_ledger'])", u'大写 MUST 总数 = 裸 MUST + MUST NOT')
Z(u"sum([abs(x) for x in F['case_ledger']])", u'每份面: 大写+小写+首字母大写=不分大小写')
Z(u"F['win_close_sum']", u'答句邻域窗的数字符带内+带外=全篇')
Z(u"sum(F['cr'])", u'四份 CR 全零(纯 LF 面)')
Z(u"sum(F['nul_faces'])", u'四份面上 NUL 全零')
Z(u"F['lines_split_close']", u'splitlines 行数=换行计数+1−末行换行+换页符(\\x0c 也是行界)')
Z(u"sum(F['bom']) - 1", u'BOM 恰一枚: 只有 9110 带')
Z(u"max([abs(F['byte_cp_delta'][i] - F['nonascii_extra'][i]) for i in range(NSRC)])",
  u'字节−码位差=每枚非 ASCII 的 utf-8 加字节(9110 的差恰由 BOM 补足)')
Z(u"F['ascii_all'] - (NSRC - 1)", u'四份里三份是纯 ASCII 面')
Z(u"F['ff'][3]", u'9110 零换页符 ⇒ 摘壳档对它近乎空操作')
Z(u"sum(F['cite_forms_close'])", u'自引三式相加=一条正则族读出的枚数(写法族账闭合)')
Z(u"len(F['s3_examples']) - (F['pool_3'] + F['pool_4'])", u'三份及以上同现的共用长行=池分档第三+第四档')
Z(u"CLOSE['confirm_gate_only_2616'] - 1", u'确认门那句 MUST NOT automatically redirect 只在 2616 存活')
Z(u"CLOSE['not_allow_changing_pair'] - 1",
  u'“does not allow changing the request method”这一族措辞只活在 7231⇎7538 中间两份里')
Z(u"CLOSE['erroneously_outer_pair'] - 1",
  u'“erroneously”(误改写)只在首尾两份出现: 2616 数 3 枚 ⇎ 9110 把这枚词捡回来数 2 枚')
Z(u"CLOSE['may_change_pair'] - 1", u'“MAY change the request method”恰在 7231⇎9110 两份读得到(剥引文档)')
Z(u"CLOSE['quot_only_9110'] - 1", u'剥引文档新增只发生在 9110(其余三份无引文竖线)')
Z(u"CLOSE['pipe_needle_pair'] - 1", u'同一句 MAY 的两种序列化: 带竖线版只在折平档, 剥竖线版只在剥引文档')
Z(u"CLOSE['304_absent_in_7231'] - 1", u'304 在 2616 与 9110 的 30x 小节里, 7231 把它挪走了')
Z(u"CLOSE['308_only_7538_9110'] - 1", u'308 只活在 7538 与 9110 的小节清单里')
Z(u"CLOSE['code_n_desc']", u'30x 小节数 8⇎7⇎1⇎9(按正文标题行现读)')
Z(u"CLOSE['obs_chain'] - 1", u'废止链 2068←2616←7231←9110 逐号可查, 而 2616 不在 9110 的 Obsoletes 里')
Z(u"CLOSE['7538_obsoletes_own_draft'] - 1", u'7538 的 Obsoletes: 只列自己的草案期号 7238')
Z(u"CLOSE['year_order_ok']", u'标题页年份 1999→2014→2015→2022 严格递增、零倒序')
Z(u"CLOSE['no_ff_only_9110']", u'换页符只在前三份, 9110 面上零枚')
Z(u"CLOSE['bom_only_9110']", u'BOM 只在 9110')
Z(u"CLOSE['nonascii_only_9110']", u'非 ASCII 只在 9110')
Z(u"CLOSE['up_ledger_zero']", u'大写义务词账归零')
Z(u"CLOSE['case_ledger_zero']", u'大小写语气账归零')
Z(u"CLOSE['lines_split_zero']", u'行数恒等式成立')
Z(u"CLOSE['shell_308_only_7538'] - 1", u'页眉印着 308 的只有 7538——它整份文书就在讲这一枚状态码')
Z(u"CLOSE['pick_overstrip_only_2616'] - 1", u'采集遍壳谓词多剥的正文句只出现在 2616')
Z(u"CLOSE['ser_pair'] - 1", u'序列化对照针三条同时成立: 折平读得到 ⇎ 剥引文读不到 ⇎ 剥后枚数不变')
Z(u"F['num_gap_2616'] - (F['years'][1] - F['years'][0])", u'2616→7231 的年距由标题页现读')
Z(u"sum(F['needles_owned']) - F['needle_n']", u'按份名下的针数相加=在册针总数')
Z(u"sum(F['s308_fold']) - sum(F['s308_raw'])", u'数字 308 从不被行界劈开: 原面枚数=折平枚数')
Z(u"sum(F['s308_quot']) - sum(F['s308_fold'])", u'剥引文竖线也不动 308 的枚数')
Z(u"sum(F['s308_raw']) - sum(F['s308_sh']) - sum(F['s308_shell'])",
  u'摘壳档少的 308 恰好全在壳行上: 7538 的页眉把争议数字本身印成 Running header')
Z(u"sum(F['s308_shell']) - F['s308_shell'][2]", u'壳行里的 308 一枚不落在其余三份')
Z(u"sum(F['bar_removed']) - sum(F['bar_removed_line'])",
  u'被剥掉的竖线枚数: 两面相减的 glyph 尺 ⇎ 逐行剥前后各数一次的行尺, 两尺同值')
Z(u"sum([abs(F['shell_diff'][i] - (F['shell_mk_only'][i] - F['shell_pick_only'][i])) for i in range(NSRC)])",
  u'两遍壳账之差 = 本遍多判的壳行 − 采集多判的壳行(逐份相减, 不是合计相抵)')
Z(u"sum(F['shell_mk_only']) - sum(F['shell_mk_only_hdr'])",
  u'本遍多判的壳行全是抬头字段行(工作组/RFC 号/Obsoletes/Updates/Category/ISSN)')
Z(u"sum(F['shell_pick_only']) - sum(F['shell_pick_only_body'])",
  u'采集多判的壳行全是缩进后以“RFC 四位数+空格”开头的正文句(2616 的引文行)')
F['zid_n'] = len(ZID)


def _ev(e):
    return eval(e.strip().replace(u'\n', u''))


ZF = [w for e, w in ZID if _ev(e)]
F['zid_fail'] = ZF
for e, w in ZID:
    if _ev(e):
        print(u'  失败: ' + w + u' <= ' + e.strip() + u' -> ' + repr(_ev(e)))
F['scalar_clos_n'] = len(ZID)
F['scalar_clos_sum'] = sum(1 for e, w in ZID if not _ev(e))
F['list_clos_n'] = len([k for k in F if (u'_close' in k or u'_ledger' in k) and isinstance(F[k], list)])
F['x_ident_n'] = len(ZID)
# --- SCAN END ---

# ---------- 与采集侧(_b72meas.json)逐键对账 ----------
MEA = json.load(io.open(u'corpus/_b72meas.json', encoding='utf-8'))
AGREE = []
DIFF = []
for k in (u'bytes', u'chars', u'lines', u'nonblank', u'ff', u'cr', u'nonascii', u'bom', u'maxlen',
          u'byte_cp_delta', u'nonascii_extra', u'pipe_lines'):
    (AGREE if F[k] == MEA[k] else DIFF).append((k, F[k], MEA[k]))
# 壳账不比对“相等”, 比对“差得可解释”: 采集侧壳数 ⇎ 本遍壳数 ⇎ 两遍各行谓词的分解
F['shell_pick_measured'] = MEA[u'shell_n']
F['shell_close_vs_pick'] = [1 if F['shell_pick'][i] == MEA[u'shell_n'][i] else 0 for i in range(NSRC)]
# 针表本身不同量(采集 24 枚正则片段 ⇎ 本遍 25 枚由锚导出的整句), 所以阶梯不横比;
# 能横比的是措辞档: 采集侧把六族字面读在剥引文面上(_pick72.py 的 QF), 本遍拿同一档 tierq_ 对拍
F['needle_table_pick'] = MEA[u'needle_n']
F['needle_table_mk'] = F['needle_n']
PKEY = dict((w, j) for j, w in enumerate(MEA[u'tier_pats']))
SHARED = [(k, w) for k, w in TIER.items() if w in PKEY]
F['tier_shared'] = sorted(w for k, w in SHARED)
F['tier_shared_n'] = len(F['tier_shared'])
F['tier_pick_only'] = sorted(w for w in MEA[u'tier_pats'] if w not in TIER.values())
F['tier_mk_only'] = sorted(w for k, w in TIER.items() if w not in PKEY)
TC = []
for k, w in SHARED:
    j = PKEY[w]
    TC.append(1 if [MEA[u'tier_faces'][i][j] for i in range(NSRC)] == F[u'tierq_' + k] else 0)
F['tier_cross_agree'] = TC
F['tier_cross_n'] = len(TC)
STRICT2 = F['sn_strict_docs']
F['pick_vs_mk_ladder'] = [STRICT2, F['sn_fold_docs'], F['sn_sh_docs'], F['sn_quot_docs']]
F['pick_ladder'] = [MEA[u'sn_strict_docs'], MEA[u'sn_fold_docs'], MEA[u'sn_sh_docs'], MEA[u'sn_quote_docs']]
F['pick_agree'] = len(AGREE)
F['pick_diff'] = len(DIFF) + (F['tier_cross_n'] - sum(F['tier_cross_agree']))
for k, a, b in DIFF:
    print(u'  采集⇎建条目不符: %s %s vs %s' % (k, a, b))
assert sum(F['shell_close_vs_pick']) == NSRC, F['shell_close_vs_pick']
assert sum(F['tier_cross_agree']) == F['tier_cross_n'], (F['tier_shared'], F['tier_cross_agree'])
assert F['tier_shared_n'] == 4 and len(F['tier_pick_only']) == len(F['tier_mk_only']) == 2
print(u'  壳谓词复现: 本遍照抄采集侧 is_shell 后逐份复算 %s ⇎ 采集落盘 %s(逐份相等)'
      % (F['shell_pick'], F['shell_pick_measured']))
print(u'  措辞横比: 两表共有字面 %s 在剥引文面上全部逐份等值; 只在一侧的字面 %s ⇎ %s'
      % (F['tier_shared'], F['tier_pick_only'], F['tier_mk_only']))
print(u'  针表不对拍(不横比): 采集 %d 枚正则片段 ⇎ 本遍 %d 枚整句, 各档读数 %s ⇎ %s'
      % (F['needle_table_pick'], F['needle_table_mk'], F['pick_ladder'], F['pick_vs_mk_ladder']))
print(u'  壳账分解: 本遍 %s ⇎ 采集 %s ⇎ 两遍同判 %s ⇎ 本遍多判 %s ⇎ 采集多判 %s'
      % (F['shell_n'], F['shell_pick_measured'], F['shell_both'], F['shell_mk_only'],
         F['shell_pick_only']))

# ---------- ZID 的 B72V 形(与 python 形逐条对拍后送 DERIV) ----------
BB72 = lambda name, i=None: (F[name] if i is None else F[name][i])
FN = u'B72V'
_to_v = re.compile(r"(?:F|CLOSE)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B72V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(4)').replace(u'NSRC', u'4')


K_, ZERO, COLL, SEENX = {}, [], {}, {}


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K_:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K_.setdefault(s, (expr, note))


def V(name, i=None, note=u''):
    if name not in F:
        raise AssertionError(u'无此键 ' + name)
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def J(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LBL[i])) for i in range(NSRC))


def JL(name, note=u''):
    return V(name, None, note) if isinstance(F[name], (list, dict)) else J(name, note)


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


ZV = []
for e, w in ZID:
    v = to_v(e.replace(u'\n', u''))
    if eval(v, {FN: BB72}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))
    reg(str(_ev(e)), v, w)


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB72}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([tuple(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


for k, v in dump_deriv().items():
    DER[k] = v
io.open(u'corpus/_b72flat.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True))
io.open(u'corpus/_deriv72.json', 'w', encoding='utf-8').write(
    json.dumps(DER, ensure_ascii=False, indent=1, sort_keys=True))

print(u'第二遍量测完成: 扁平键 %d ｜ 恒等式 %d ｜ 失败 %d ｜ 针 %d ｜ 池 %d ｜ 锚池 %d ｜ 对采集 %d 符 %d 不符'
      % (len(F), len(ZID), len(ZF), len(GN), F['pool_n'], F['apool_n'], F['pick_agree'], F['pick_diff']))
print(u'四档阶梯 strict=%s fold=%s sh=%s quot=%s ｜ 折行独有=%s(%d) 剥引文独有=%s 死集=%s'
      % (F['sn_strict_docs'], F['sn_fold_docs'], F['sn_sh_docs'], F['sn_quot_docs'],
         F['fold_only_own'], F['fold_only_n'], F['quot_only_own'], F['dead_needles']))
print(u'措辞档 fold=%s quot=%s gain=%s ｜ POSTtoGET=%s hist=%s' % (
    F['tier_fold_tot'], F['tier_quot_tot'], F['tier_gain'], F['post_to_get'], F['hist_reasons']))
print(u'小节 %s codes=%s ｜ 年份 %s ｜ 废止 %s 更新 %s' % (
    F['code_n'], F['codes'], F['years'], F['obs_ids'], F['upd_ids']))
print(u'结构 bytes=%s lines=%s ff=%s shell=%s pipe=%s glyph=%s nonascii=%s bom=%s'
      % (F['bytes'], F['lines'], F['ff'], F['shell_n'], F['pipe_lines'], F['pipe_glyphs'],
         F['nonascii'], F['bom']))
print(u'池 %s tier=%s 最大对=%s(%d) 轴=%s ｜ 判定 %s' % (
    F['pool_n'], F['pool_tier'], F['pair_max_lbl'], F['pair_max'], F['axis_str'],
    dict((k, F[k]) for k in CLOSE)))

exec(io.open(u'corpus/_mk72emit.py', encoding='utf-8').read())
