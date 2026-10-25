# -*- coding: utf-8 -*-
"""采集遍(B92, 第一套实现): “30x 重定向链到底该限制在几次”由五份实现侧一手文档各答一遍
fet(WHATCH? WHATWG Fetch Standard 剥壳正文: 次数挂在请求对象上 “redirect count is 20”, 触顶 return a network error)
⇎ cli(curl 命令行文档 --max-redirs: 面上写 “default the limit is set to 50 redirects”, -1 为不限)
⇎ lib(libcurl CURLOPT_MAXREDIRS: DEFAULT 段 “30 (since 8.3.0), it was previously unlimited”, 0 拒绝任何重定向)
⇎ go(Go net/http client.go: 文档注释 “stop after 10 consecutive requests” ⇎ 代码 “len(via) >= 10” ⇎ 错误串 “10 redirects”)
⇎ req(python-requests sessions.py: 注释 “which is 30” ⇎ 代码只拿变量 self.max_redirects, 数不落码面)。
候选 RFC 2616/7231/9110/8470 在库已核(httpRedir/httpretry 两处均有同名文件, 且 B65/B72/B80 已进门), 按规矩换源。

本遍机制(A 侧): ①字面针=游标 find 环; ②整词尺=邻居字符手扫; ③行切=split(NL); ④折平=' '.join(split()) 整串归一;
⑤HTML 剥壳=两条正则(块删+标签替换)+html.unescape; ⑥frontmatter/注释壳=整行序列正则判形; ⑦句界=(?<=[.!?]) + 正则切;
⑧数值=一条选择支正则抓窗; ⑨行号=4 行滑窗在折平面上试; ⑩共现池=set 交集。建条侧(_mkB92.py)十处全换算法不换定义。
所有正文数字由本遍量出后落 JSON, 一枚都不手打。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'fet', u'cli', u'lib', u'go', u'req']
NSRC = 5
D = u'corpus/raw/redirHops/b92/'
SRC = [D + u'fetch.html', D + u'max-redirs.md', D + u'CURLOPT_MAXREDIRS.md',
       D + u'client.go', D + u'sessions.py']
FACE_TXT = [D + u'fetch.txt', D + u'max-redirs.md', D + u'CURLOPT_MAXREDIRS.md',
            D + u'client.go', D + u'sessions.py']
M = {}


def rd(p):
    return io.open(p, 'rb').read()


# ---------- 0. fetch 剥壳(A 侧: 正则档) ----------
def strip_html_A(raw):
    x = re.sub(u'<(script|style)\\b.*?</\\1>', u' ', raw, flags=re.S | re.I)
    x = re.sub(u'<[^>]*>', u' ', x)
    import html as _h
    x = _h.unescape(x)
    out = []
    for l in x.split(NL):
        c = u' '.join(l.split())
        if c:
            out.append(c)
    return NL.join(out) + NL


HB = rd(SRC[0])
HT = HB.decode(u'utf-8', u'replace')
FET = strip_html_A(HT)
io.open(FACE_TXT[0], 'wb').write(FET.encode(u'utf-8'))
M['fet_tags_re'] = len(re.findall(u'<[^>]*>', HT))
M['fet_blk_re'] = len(re.findall(u'<(script|style)\\b.*?</\\1>', HT, flags=re.S | re.I))
M['fet_html_bytes'] = len(HB)
M['fet_html_chars'] = len(HT)
M['fet_strip_chars'] = len(FET)
M['fet_strip_lines'] = len(FET.split(NL)) - 1  # 尾 NL

B = [rd(FACE_TXT[i]) for i in range(NSRC)]
T = [b.decode(u'utf-8', u'replace') for b in B]
RAWL = [t.split(NL) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]
M['fet_html_lines'] = len(HT.split(NL))


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


def ub_A(s, w, kind=u'alpha'):
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if kind == u'alpha':
            ok = not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha())
        elif kind == u'digit':
            ok = not (a >= 0 and s[a].isdigit()) and not (b < len(s) and s[b].isdigit())
        else:
            ok = not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())
        if ok:
            c += 1
        i = j + 1


# ---------- 1. 面量 ----------
M['s_bytes'] = [len(B[i]) for i in range(NSRC)]
M['s_chars'] = [len(T[i]) for i in range(NSRC)]
M['s_lf'] = [cnt_cur(T[i], NL) for i in range(NSRC)]
M['s_cr'] = [cnt_cur(T[i], u'\r') for i in range(NSRC)]
M['s_ff'] = [cnt_cur(T[i], u'\x0c') for i in range(NSRC)]
M['s_tab'] = [cnt_cur(T[i], u'\t') for i in range(NSRC)]
M['s_lines'] = [len(L[i]) for i in range(NSRC)]
M['s_nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
M['s_blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
M['s_maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
M['s_nonascii'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(NSRC)]
M['s_bom'] = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
M['s_endnl'] = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
M['s_splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
M['byte_cp_ledger'] = [M['s_bytes'][i] - M['s_chars'][i] for i in range(NSRC)]
NAEXTRA = []
for i in range(NSRC):
    ex = 0
    for c in T[i]:
        if ord(c) > 127:
            ex += len(c.encode(u'utf-8')) - 1
    NAEXTRA.append(ex)
M['na_extra_bytes'] = NAEXTRA
M['line_close'] = [M['s_nonblank'][i] + M['s_blank'][i] - M['s_lines'][i] for i in range(NSRC)]
M['split_close'] = [M['s_splitlines'][i] - (M['s_lf'][i] + 1 - M['s_endnl'][i]) - M['s_ff'][i]
                    for i in range(NSRC)]
print(u'0 面量:', json.dumps(dict((k, M[k]) for k in
      ['s_bytes', 's_chars', 's_lines', 's_nonblank', 's_blank', 's_maxlen', 's_tab',
       's_nonascii', 's_bom', 's_endnl', 'byte_cp_ledger', 'na_extra_bytes',
       'line_close', 'split_close', 'fet_strip_chars', 'fet_strip_lines'])))

# ---------- 2. 壳三族: html 标签 ⇎ frontmatter ⇎ 注释 ----------
def fm_end(lines):
    # A 侧: 列表扫第二个 '---'
    k = -1
    n = 0
    for i, x in enumerate(lines):
        if x == u'---':
            n += 1
            if n == 2:
                k = i
                break
    return k


def cmt_A(i):
    if LBL[i] == u'go':
        return [x.lstrip().startswith(u'//') for x in L[i]]
    if LBL[i] == u'req':
        return [x.lstrip().startswith(u'#') for x in L[i]]
    return [False] * len(L[i])


SH = []
for i in range(NSRC):
    if LBL[i] == u'fet':
        SH.append([0] * len(L[i]))
    elif LBL[i] in (u'cli', u'lib'):
        e = fm_end(L[i])
        SH.append([True] * (e + 1) + [x.strip() == u'' for x in L[i][e + 1:]])
    else:
        SH.append(cmt_A(i))
M['shell_lines'] = [sum(1 for f in SH[i] if f) for i in range(NSRC)]
M['body_lines'] = [len(L[i]) - M['shell_lines'][i] for i in range(NSRC)]
M['fm_close'] = [M['shell_lines'][i] + M['body_lines'][i] - M['s_lines'][i] for i in range(NSRC)]
DSh = [pnorm(NL.join([L[i][k] for k in range(len(L[i])) if not SH[i][k]])) for i in range(NSRC)]
FOL = [pnorm(T[i]) for i in range(NSRC)]
# 注释标记档: 逐行抹去行首标记 (go '//', req '#:') 后折平 (A 侧: 行级 re.sub)
def markface(i):
    if LBL[i] == u'go':
        return NL.join([re.sub(u'^\\s*// ?', u'', x) for x in L[i]])
    if LBL[i] == u'req':
        return NL.join([re.sub(u'^\\s*#: ?', u'', x) for x in L[i]])
    return u''
MARKRAW = [markface(i) for i in range(NSRC)]
MARK = [pnorm(MARKRAW[i]) for i in range(NSRC)]
M['py_hash_cmt'] = len([x for x in L[4] if x.lstrip().startswith(u'#:')])
print(u'2 壳行:', M['shell_lines'], u' 剥壳后行:', M['body_lines'], u' 账:', M['fm_close'],
      u' py #: 行:', M['py_hash_cmt'])

# ---------- 3. 判词针五档 ----------
NEEDLES = [
    (u'fet', u'if request \u2019s redirect count is 20, then return a network error'),
    (u'fet', u'redirect count is 20'),
    (u'fet', u'increase request \u2019s redirect count by 1'),
    (u'fet', u'a request has an associated redirect count'),
    (u'fet', u'unless stated otherwise, it is zero'),
    (u'fet', u'301, 302, 303, 307, or 308'),
    (u'fet', u'network error'),
    (u'fet', u'redirect count'),
    (u'fet', u'updated tue oct 13 14:27:53 2026 -0700'),
    (u'cli', u'set the maximum number of redirections to follow'),
    (u'cli', u'by default the limit is set to 50 redirects'),
    (u'cli', u'set this option to -1 to make it unlimited'),
    (u'cli', u'prevents curl from following too many redirects'),
    (u'cli', u'added: 7.5'),
    (u'lib', u'the set number is the redirection limit'),
    (u'lib', u'the next redirect triggers the error'),
    (u'lib', u'setting the limit to 0 makes libcurl refuse any redirect'),
    (u'lib', u'set it to -1 for an infinite number of redirects'),
    (u'lib', u'never-ending redirect loops'),
    (u'lib', u'30 (since 8.3.0), it was previously unlimited'),
    (u'lib', u'added-in: 7.5'),
    (u'go', u'which is to stop after 10 consecutive requests'),
    (u'go', u'if len(via) >= 10 {'),
    (u'go', u'stopped after 10 redirects'),
    (u'go', u'checkredirect returns erruselastresponse'),
    (u'go', u'before following an http redirect'),
    (u'req', u'maximum number of redirects allowed'),
    (u'req', u'this defaults to requests.models.default_redirect_limit, which is 30'),
    (u'req', u'a :class:`toomanyredirects` exception is raised'),
    (u'req', u'if len(resp.history) >= self.max_redirects:'),
    (u'req', u'exceeded {self.max_redirects} redirects.'),
    (u'req', u'raise toomanyredirects('),
    (u'req', u'if the request exceeds this limit, a'),
    # 反向对照针: 别家的判词句在本家五档上必须全零
    (u'fet', u'an earlier version of this specification recommended a maximum of five redirections'),
    (u'go', u'setting the limit to 0 makes libcurl refuse any redirect'),
    (u'cli', u'redirect count is 20, then return a network error'),
]
IDX = dict((LBL[i], i) for i in range(NSRC))
HTF = pnorm(HT)
rows = []
for si, nd in NEEDLES:
    i = IDX[si]
    q = pnorm(nd)
    t1 = len([x for x in L[i] if q in pnorm(x)])
    t2 = cnt_cur(FOL[i], q)
    t3 = cnt_cur(DSh[i], q)
    t4 = cnt_cur(HTF, q) if si == u'fet' else -1
    t5 = cnt_cur(MARK[i], q) if si in (u'go', u'req') else -1
    rows.append((si, nd, t1, t2, t3, t4, t5))
M['needle5'] = [[r[0]] + list(r[1:]) for r in rows]
M['fold_gain'] = [sum(r[3] - r[2] for k, r in enumerate(rows) if r[0] == LBL[i]) for i in range(NSRC)]
M['rescued_html'] = [k for k, r in enumerate(rows) if r[0] == u'fet' and r[5] == 0 < r[3]]
M['shell_only'] = [k for k, r in enumerate(rows) if r[0] == u'fet' and r[5] > 0 == r[3]]
M['mark_rescued'] = [k for k, r in enumerate(rows) if r[0] in (u'go', u'req') and r[6] > 0 >= r[3]]
M['fm_only'] = [k for k, r in enumerate(rows) if r[0] in (u'cli', u'lib') and r[4] == 0 < r[3]]
M['cmt_only'] = [k for k, r in enumerate(rows) if r[0] in (u'go', u'req') and r[4] == 0 < r[3]]
M['row_cold'] = [k for k, r in enumerate(rows) if r[2] == 0 and r[3] > 0]
print(u'3 判词针 (行 ⇎ 折 ⇎ 剥壳 ⇎ 带壳html ⇎ 抹标记):')
for k, r in enumerate(rows):
    print(u'  [%02d] %-4s %3d %3d %3d %4s %4s  %s' % (k, r[0], r[2], r[3], r[4], r[5], r[6], r[1][:66]))

# ---------- 4. 反向独占针 ----------
EXCL = [u'redirect count is 20', u'limit is set to 50', u'infinite number of redirects',
        u'10 consecutive requests', u'toomanyredirects', u'curle_too_many_redirects',
        u'max-redirs', u'maxredirs', u'max_redirects', u'never-ending', u'network error',
        u'unlimited']
mat = []
for p in EXCL:
    q = pnorm(p)
    mat.append([LBL[i] for i in range(NSRC) if cnt_cur(FOL[i], q) > 0])
M['excl_mat'] = mat
for p, hs in zip(EXCL, mat):
    print(u'4 独占 %-32s -> %s' % (p, hs))

# ---------- 5. 语形族 ⇎ 数字×语境 ----------
GRP = [u'redirect', u'redirects', u'redirection', u'redirections', u'redirected',
       u'redirecting', u'loop', u'loops', u'count', u'unlimited', u'infinite', u'consecutive']
FL = [pnorm(T[i]) for i in range(NSRC)]
M['grp_word'] = [[ub_A(FL[i], g) for g in GRP] for i in range(NSRC)]
M['grp_sub'] = [[cnt_cur(FL[i], g) for g in GRP] for i in range(NSRC)]
M['sub_delta'] = [M['grp_sub'][i][0] - M['grp_word'][i][0] for i in range(NSRC)]
print(u'5 语形 整词:')
for i in range(NSRC):
    print(u'   %-4s %s' % (LBL[i], M['grp_word'][i]))
print(u'   子串-整词差:', [[M['grp_sub'][i][k] - M['grp_word'][i][k] for k in range(len(GRP))]
                          for i in range(NSRC)])
RXC = re.compile(u'.{0,60}redirect.{0,60}', re.I | re.S)
RXNUM = re.compile(u'(?<![A-Za-z0-9.])(\\d+(?:\\.\\d+)?)(?![A-Za-z0-9])')
NW = []
for i in range(NSRC):
    toks = []
    for m in RXC.finditer(T[i]):
        toks += [z for z in RXNUM.findall(m.group(0))]
    NW.append(sorted(set(toks)))
M['numwin'] = NW
M['numwin_n'] = [len(x) for x in NW]
RXN2 = re.compile(u'.{0,15}redirect count.{0,15}', re.I | re.S)
NW2 = []
for i in range(NSRC):
    toks = []
    for m in RXN2.finditer(T[i]):
        toks += [z for z in RXNUM.findall(m.group(0))]
    NW2.append(sorted(set(toks)))
M['numwin_narrow'] = NW2
print(u'5 数字×redirect 窗(±60):', NW, u' 窄窗±15(redirect count):', NW2)
DGT = [u'20', u'50', u'30', u'10', u'0', u'1', u'3']
M['digit_tok'] = [[ub_A(FL[i], d, u'digit') for d in DGT] for i in range(NSRC)]
print(u'5 数字token(折平, 数字界):', M['digit_tok'])
M['codes30x'] = [[ub_A(FL[i], c, u'digit') for c in [u'301', u'302', u'303', u'305', u'307', u'308']]
                 for i in range(NSRC)]
print(u'5 30x:', M['codes30x'])

# ---------- 6. 语气词 ----------
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'MAY']
M['ob_up_line'] = [[sum([ub_A(x, w) for x in L[i]]) for w in OB] for i in range(NSRC)]
M['ob_up_fold'] = [[ub_A(FOL[i], w) for w in OB] for i in range(NSRC)]
LOW = [u'must', u'should', u'may', u'can']
M['ob_low_fold'] = [[ub_A(FOL[i], w) for w in LOW] for i in range(NSRC)]
FOLC = [u' '.join(T[i].split()) for i in range(NSRC)]          # 保大小写的整篇折平
M['ob_up_foldcase'] = [[ub_A(FOLC[i], w) for w in OB] for i in range(NSRC)]
M['up_line_tot'] = [sum(x) for x in M['ob_up_line']]
M['up_foldcase_tot'] = [sum(x) for x in M['ob_up_foldcase']]
M['up_fold_lowered_tot'] = sum(sum(x) for x in M['ob_up_fold'])
M['up_line_all'] = sum(M['up_line_tot'])                 # 全库大写枚数(行和再求和)
M['up_foldcase_all'] = sum(M['up_foldcase_tot'])
M['up_fold_lower_all'] = M['up_fold_lowered_tot']
print(u'6 大写:', M['ob_up_fold'], u' 小写:', M['ob_low_fold'],
      u' 保形折平:', M['ob_up_foldcase'], u' 行和⇎折和:', M['up_line_tot'], M['up_foldcase_tot'])

# ---------- 7. 年份与版本 ----------
RY = re.compile(u'(?<![0-9])((?:19|20)\\d\\d)(?![0-9])')
M['year_txt'] = [sorted(set(RY.findall(T[i]))) for i in range(NSRC)]
M['year_html'] = sorted(set(RY.findall(HT)))
M['year_html_n'] = len(RY.findall(HT))
M['ver_tok'] = [[cnt_cur(FL[i], v) for v in [u'7.5', u'8.3.0', u'1l', u'3l']] for i in range(NSRC)]
print(u'7 年(面):', M['year_txt'], u' 年(html):', M['year_html'], u'x', M['year_html_n'],
      u' 版本token [7.5,8.3.0,1L,3L]:', M['ver_tok'])

# ---------- 8. 共现行池 ----------
SETS = [set(pnorm(x) for x in L[i] if x.strip()) for i in range(NSRC)]
PAIR = []
for a in range(NSRC):
    for b in range(a + 1, NSRC):
        sh = SETS[a] & SETS[b]
        if sh:
            rawa = set(x for x in L[a] if x.strip())
            rawb = set(x for x in L[b] if x.strip())
            PAIR.append([LBL[a], LBL[b], len(sh), len(rawa & rawb), sorted(sh)[:3]])
M['pair_share'] = PAIR
print(u'8 共现行对:', PAIR)

# ---------- 9. 答句窗(行号 A 侧: foldmap 折平面对照表) ----------
def foldmap(txt):
    lines = txt.split(NL)
    offs, pos, seg = [], 0, []
    for i, l in enumerate(lines):
        c = pnorm(l)
        if not c:
            continue
        offs.append((pos, pos + len(c), i))
        seg.append(c)
        pos += len(c) + 1
    face = u' '.join(seg)
    assert len(face) == (pos - 1 if pos else 0), (len(face), pos)
    return face, offs


def line_of_face(offs, s0):
    cand = [o[2] for o in offs if o[0] <= s0]
    return cand[-1] if cand else None


def find_line(i, nd):
    q = pnorm(nd)
    face, offs = foldmap(T[i])
    s0 = face.find(q)
    if s0 < 0:
        return -1, -1
    return s0, (line_of_face(offs, s0) if s0 >= 0 else -1)


WINS = [(u'fet', u'if request \u2019s redirect count is 20', u'increase request \u2019s redirect count by 1'),
        (u'cli', u'set the maximum number of redirections to follow', u'to make it'),
        (u'lib', u'the set number is the redirection limit', u'30 (since 8.3.0)'),
        (u'go', u'checkredirect specifies the policy', u'10 consecutive requests'),
        (u'req', u'maximum number of redirects allowed', u'which is 30')]
W = []
for si, s, e in WINS:
    i = IDX[si]
    o1, a = find_line(i, s)
    if e == u'which is 30':
        face, offs = foldmap(MARKRAW[4])
        o2 = face.find(pnorm(e))
        b = line_of_face(offs, o2) if o2 >= 0 else -1
    else:
        o2, b = find_line(i, e)
    W.append([si, a + 1, b + 1, b - a + 1 if a >= 0 and b >= 0 else -1])
M['ans_win'] = W
for w in W:
    print(u'9 窗 %s 首 %d 末 %d 高 %d' % tuple(w))

# ---------- 10. 答案数读数(两轨) ----------
# 轨1: 语境正则抓数; 轨2: 数字token邻接词读数
def after_num(s, pre):
    m = re.search(re.escape(pre) + u'\\s*(-?\\d+)', s, re.I)
    return int(m.group(1)) if m else None
def ctx_pair(hay, pre, suf):
    m = re.search(re.escape(pre) + u'[^a-z0-9]{0,3}(-?\\d{1,4})' + re.escape(suf), hay)
    return int(m.group(1)) if m else None
ANS = {}
ANS[u'fet_rgx'] = ctx_pair(FOL[0], u'redirect count is', u'')
ANS[u'fet_alt'] = after_num(FOL[0], u'redirect count is')
ANS[u'cli_rgx'] = ctx_pair(FOL[1], u'limit is set to', u' redirects')
ANS[u'cli_alt'] = after_num(FOL[1], u'limit is set to')
m = re.search(u'(?<![0-9.])\\d+(?= \\(since 8\\.3\\.0\\))', FOL[2])
ANS[u'lib_rgx'] = int(m.group(0)) if m else None
ANS[u'lib_alt'] = after_num(FOL[2], u'default')
ANS[u'lib_zero'] = ctx_pair(FOL[2], u'setting the limit to', u' makes')
ANS[u'go_rgx'] = ctx_pair(FOL[3], u'stop after', u' consecutive')
ANS[u'go_alt'] = after_num(FOL[3], u'stop after')
m = re.search(u'len\\(via\\) >= (\\d+)', T[3])
ANS[u'go_code'] = int(m.group(1)) if m else None
ANS[u'go_err'] = ctx_pair(FOL[3], u'stopped after', u' redirects')
ANS[u'req_rgx'] = ctx_pair(MARK[4], u'which is', u'. self.max_redirects')
m = re.search(u'(?<![0-9.])\\d+(?=\\. self\\.max_redirects)', MARK[4])
ANS[u'req_alt'] = int(m.group(0)) if m else None
ANS[u'req_code30'] = ub_A(DSh[4], u'30', u'digit')
M['ans_read'] = ANS
print(u'10 答案数:', ANS)
M['ans_doc_code_diff'] = [ANS[u'go_rgx'] - ANS[u'go_code'],
                          ANS[u'req_rgx'] - ANS[u'req_code30']]
READS = {u'fet': ANS[u'fet_rgx'], u'cli': ANS[u'cli_rgx'], u'lib': ANS[u'lib_rgx'],
         u'go': ANS[u'go_rgx'], u'req': ANS[u'req_rgx']}
ALT = {u'fet': ANS[u'fet_alt'], u'cli': ANS[u'cli_alt'], u'lib': ANS[u'lib_alt'],
       u'go': ANS[u'go_alt'], u'req': ANS[u'req_alt']}
M['ans_reads'] = READS
M['ans_alts'] = ALT
print(u'10 主轨 ⇎ 另轨:', READS, ALT, u' 码面差:', M['ans_doc_code_diff'])

# ---------- 11. 汇总针: 档阶计数 ⇎ 独占针计数 ⇎ 共现池账 ----------
M['needle_n'] = len(rows)
M['tier_fold'] = M['fold_gain']
M['tier_html_rescued'] = len(M['rescued_html'])
M['tier_shell_only'] = len(M['shell_only'])
M['tier_mark_rescued'] = len(M['mark_rescued'])
M['tier_fm_only'] = len(M['fm_only'])
M['tier_cmt_only'] = len(M['cmt_only'])
M['tier_cold'] = len(M['row_cold'])
M['needle_cold_list'] = [k for k, r in enumerate(rows)
                         if not any(x > 0 for x in (r[2], r[3], r[4], r[5], r[6]))]
M['tier_neg'] = len(M['needle_cold_list'])
M['tier_both_diff'] = len([r for r in rows if r[0] == u'fet' and r[3] and r[5] and r[3] != r[5]])
M['excl_probes'] = len(EXCL)
M['excl_single'] = len([h for h in mat if len(h) == 1])
M['excl_multi'] = len([h for h in mat if len(h) > 1])
M['excl_owner_n'] = [len([h for h in mat if h == [LBL[i]]]) for i in range(NSRC)]
M['share_tot'] = sum(p[2] for p in PAIR)
M['share_pairs'] = len(PAIR)
M['share_max'] = max(p[2] for p in PAIR)
M['share_raw_tot'] = sum(p[3] for p in PAIR)
print(u'11 档阶计数:', M['needle_n'], M['tier_html_rescued'], M['tier_shell_only'],
      M['tier_mark_rescued'], M['tier_fm_only'], M['tier_cmt_only'], M['tier_cold'],
      u' 独占:', M['excl_probes'], M['excl_single'], M['excl_multi'], M['excl_owner_n'],
      u' 共现:', M['share_tot'], M['share_pairs'], M['share_max'], M['share_raw_tot'])

# ---------- 12. 答数落到的层(文档面 ⇎ 剥壳正文面) ⇎ 谱系 ⇎ 判据形 ----------
ANSI = [READS[LBL[i]] for i in range(NSRC)]
M['ans'] = ANSI
M['ans_alt_v'] = [ALT[LBL[i]] for i in range(NSRC)]
M['ans_line'] = [w[1] for w in W]
M['ans_end'] = [w[2] for w in W]
M['ans_h'] = [w[3] for w in W]
M['num_body'] = [ub_A(DSh[i], u'%d' % ANSI[i], u'digit') for i in range(NSRC)]
M['go_guard'] = ANS[u'go_code']
M['go_msg'] = ANS[u'go_err']
M['go_eff'] = ANS[u'go_code'] - 1
M['req_body_num'] = ANS[u'req_code30']
M['lib_zero'] = ANS[u'lib_zero']
RXRFC = re.compile(u'(?i)rfc ?(\\d{4})(?!\\d)')
M['rfc_nums'] = [sorted(set(RXRFC.findall(T[i]))) for i in range(NSRC)]
M['rfc_n'] = [len(set(RXRFC.findall(T[i]))) for i in range(NSRC)]
M['rfc_tok'] = [ub_A(FOL[i], u'rfc') for i in range(NSRC)]
M['issue_tok'] = [ub_A(FOL[i], u'issue') for i in range(NSRC)]
M['ge_tok'] = [cnt_cur(FOL[i], u'>=') for i in range(NSRC)]
M['eq_guard'] = [cnt_cur(FOL[i], u'count is 20') for i in range(NSRC)]
M['year_n'] = [len(x) for x in M['year_txt']]
print(u'12 答数:', M['ans'], u' 行:', M['ans_line'], u' 末:', M['ans_end'], u' 高:', M['ans_h'],
      u' 剥壳面落数:', M['num_body'], u' go 码面/消息/实跟:', M['go_guard'], M['go_msg'], M['go_eff'],
      u' req 码面:', M['req_body_num'], u' lib 零哨:', M['lib_zero'])
print(u'12 谱系 rfc号:', M['rfc_nums'], u' rfc枚:', M['rfc_n'], u' rfc词:', M['rfc_tok'],
      u' issue词:', M['issue_tok'], u' >=:', M['ge_tok'], u' 等号判据:', M['eq_guard'],
      u' 年份枚:', M['year_n'])

# ---------- 13. 账目断言(每条都能红) ----------
print(u'13 增益账: 折−行', M['fold_gain'], u' html救回', M['rescued_html'],
      u' 壳独占', M['shell_only'], u' 标记救回', M['mark_rescued'],
      u' frontmatter独占', M['fm_only'], u' 注释独占', M['cmt_only'])
assert M['line_close'] == [0] * NSRC, M['line_close']
assert M['split_close'] == [0] * NSRC, M['split_close']
assert M['byte_cp_ledger'] == M['na_extra_bytes'], (M['byte_cp_ledger'], M['na_extra_bytes'])
assert M['fm_close'] == [0] * NSRC, M['fm_close']
assert M['fet_strip_lines'] == len([x for x in FET.split(NL) if x.strip()]), M['fet_strip_lines']
assert sum(1 for r in rows if r[3] < r[2]) == 0, u'折平档比逐行档还少: 口径不单调'
assert all(READS[k] == ALT[k] for k in READS), (READS, ALT)
for b, hs in zip(EXCL, mat):
    if len(hs) == 1:
        q = pnorm(b)
        assert all(cnt_cur(FOL[i], q) == 0 for i in range(NSRC) if LBL[i] not in hs), (b, hs)
assert M['fet_strip_chars'] < M['fet_html_chars'], u'剥壳后应更短'
assert M['ans'] == M['ans_alt_v'], (M['ans'], M['ans_alt_v'])
assert sum(M['excl_owner_n']) == M['excl_single'], (M['excl_owner_n'], M['excl_single'])
assert M['excl_single'] + M['excl_multi'] == M['excl_probes']
assert M['share_pairs'] == len([p for p in PAIR if p[2] > 0])
nfet = len([r for r in rows if r[0] == u'fet'])
assert len([r for r in rows if r[0] == u'fet' and r[3] == r[5]]) \
       + M['tier_html_rescued'] + M['tier_shell_only'] + M['tier_both_diff'] == nfet, u'fet 四档不闭合'
assert sum(M['eq_guard']) == 1 and M['eq_guard'][0] == 1, u'等号判据应当只有 fetch 一枚'
assert M['ge_tok'][1] == 0 == M['ge_tok'][2], u'curl 两面不该有比较算符'
assert M['rfc_n'][1] == 0 == M['rfc_n'][2], u'curl 两面不该引 RFC 号'
assert M['req_body_num'] == M['num_body'][4] == 0, u'requests 的数应不落码面'
assert M['go_msg'] == M['go_guard'] and M['go_eff'] == M['go_guard'] - 1
assert M['up_line_tot'] == M['up_foldcase_tot'], (M['up_line_tot'], M['up_foldcase_tot'])
assert M['up_fold_lowered_tot'] == 0, u'折平档先小写化, 大写语气词必归零(尺子自陷)'
assert list(M['needle_cold_list']) == [M['needle_n'] - 3, M['needle_n'] - 2, M['needle_n'] - 1], \
    M['needle_cold_list']

# ---------- 14. 条目正文直引的组合读数(两侧同尺, 由针表回取) ----------
ND = dict((r[1], r) for r in rows)
for nm, key in [(u'neterr', u'network error'), (u'rcnt', u'redirect count')]:
    r = ND[key]
    M[nm + u'_html'] = r[5]          # 带壳网页面
    M[nm + u'_txt'] = r[3]           # 剥壳折平面
M['tier_diff_list'] = [[r[1], r[5], r[3]] for r in rows
                       if r[0] == u'fet' and r[3] and r[5] and r[3] != r[5]]
M['ans_spread'] = max(M['ans']) // min(M['ans'])
CL = [p for p in PAIR if p[0] == u'cli' and p[1] == u'lib']
assert len(CL) == 1, CL
M['sh_cl'] = CL[0][2]
M['sh_cl_raw'] = CL[0][3]
assert len(M['tier_diff_list']) == M['tier_both_diff'], M['tier_diff_list']
assert M['neterr_html'] > M['neterr_txt'] and M['rcnt_html'] > M['rcnt_txt']
assert M['ans_spread'] * min(M['ans']) == max(M['ans'])
assert M['sh_cl'] == M['share_max'] and M['sh_cl_raw'] <= M['sh_cl']
print(u'14 组合读数:', M['neterr_html'], M['neterr_txt'], M['rcnt_html'], M['rcnt_txt'],
      u' 倍差:', M['ans_spread'], u' curl 两页共现:', M['sh_cl'], M['sh_cl_raw'])
json.dump(M, io.open(u'corpus/_b92meas.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
print(u'已落 corpus/_b92meas.json ｜ 键 %d' % len(M))
