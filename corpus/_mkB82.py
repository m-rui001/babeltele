# -*- coding: utf-8 -*-
"""建条目第二遍(B82): “一条空闲连接到底多久该关掉”, 五份一手文书各答一遍
1122(1989 TCP 需求: 保活 MAY, MUST 默认关闭, 间隔 MUST 不小于 two hours) ⇎ 9293(2022 TCP 规范: 同一句逐字重印,
只多插两枚编号 (MUST-27)(MUST-28), 并把该节归为本地事项) ⇎ 9112(2022 HTTP/1.1: 对超时长度与是否存在一枚要求也不提)
⇎ 9113(2022 HTTP/2: 鼓励长开但允许终止空闲连接, 关前先发 GOAWAY) ⇎ 9000(2021 QUIC: max_idle_timeout 由两端各自
宣告, 生效值取两者最小, 0/省略即关闭, 且 MUST 不小于 3×PTO)。

本遍与采集侧(_pick82.py)换机制而不换定义, 七处:
①字面针: 采集侧用游标 find 环(cnt_cur), 本遍用 re.findall(re.escape(nd)) 整体扫描;
②整词尺: 采集侧用邻居字符手扫(ub), 本遍改用 (?<![A-Za-z])/(?!…) 断言正则(ub_re), 两把尺同量对拍;
③壳谓词: 采集侧对整行跑序列正则(^RFC1122 / \\[Page \\d+\\] / ==\\x0c), 本遍折叠后逐段比 token 形状(shell_by_shape);
④句界: 采集侧用 (?<=[.!?]) + 的正则切句, 本遍逐字符扫“句点/问号/叹号 + 空白 + 小写或左括号”, 两把句尺各自数同一节;
⑤数值抽取: 采集侧一条 RXU 选择支, 本遍手工扫数字串再就地读单位词, 严尺(四个单位词) ⇎ 宽尺(容裸 s)分别实现;
⑥节窗: 采集侧靠节号正则取块, 本遍按“节号点段数 ⇎ 前导空格数”整数量判档, 并拿同一节号在目录与正文各印的枚数复核;
⑦行式对账: 采集侧断言 splitlines−split(\\n) == FF后随换行 −尾换行, 本遍按逐行是否以 \\x0c 起头 ⇎ 是否恰为 \\x0c 现读再验。
四档口径: 原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳去编号折平(第三⇎第四档的差只由 9293 的编号标注贡献); 节窗档另立。
所有正文数字由 V()/J()/EXPR() 注册后插值, 一枚都不手打; 锚一律由面上位置导出。键名等于所量之物。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'1122', u'9293', u'9112', u'9113', u'9000']
NSRC = 5
PATH = [u'corpus/raw/tcpRTO/rfc1122.txt', u'corpus/raw/tcpTW/rfc9293.txt',
        u'corpus/raw/httpKA/rfc9112.txt', u'corpus/raw/idle/rfc9113.txt',
        u'corpus/raw/idle/rfc9000.txt']
FAM = [u'old', u'new', u'new', u'new', u'new']
IDS = [u'1122', u'9293', u'9112', u'9113', u'9000']
YR = [1989, 2022, 2022, 2022, 2021]
MON = [u'October', u'August', u'June', u'June', u'May']
OLD = [i for i in range(NSRC) if FAM[i] == u'old']
NEW = [i for i in range(NSRC) if FAM[i] == u'new']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire82.py 把这一段 ⇎ _mk82emit.py 的 SCAN2 段机械切进 audit.py::_b82_scan)


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
RAWL = [t.split(NL) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]


def pnorm(s):
    return u' '.join(s.lower().split())


def fold(s):
    return u' '.join([c for c in re.split(u'\\s', s) if c != u''])


def cnt_cur(hay, nd):
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def cnt_re(hay, nd):
    """本遍的字面针轨: 转义后整体正则扫描(采集侧是游标 find 环)。"""
    return len(re.findall(re.escape(nd), hay))


def _nb(s, i, n, kind):
    a = i - 1
    b = i + n
    if kind == u'alpha':
        return not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha())
    if kind == u'digit':
        return not (a >= 0 and s[a].isdigit()) and not (b < len(s) and s[b].isdigit())
    return not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())


def ub(s, w, kind=u'alpha'):
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        if _nb(s, j, n, kind):
            c += 1
        i = j + 1


def ub_re(s, w, kind=u'alpha'):
    """本遍的整词尺: 断言正则(采集侧是邻居字符手扫)。"""
    a = u'(?<![A-Za-z])' if kind == u'alpha' else u'(?<![0-9])' if kind == u'digit' else u'(?<![0-9A-Za-z])'
    b = u'(?![A-Za-z])' if kind == u'alpha' else u'(?![0-9])' if kind == u'digit' else u'(?![0-9A-Za-z])'
    return len(re.findall(a + re.escape(w) + b, s))


def digit_runs(x):
    n, prev = 0, False
    for c in x:
        cur = c.isdigit()
        if cur and not prev:
            n += 1
        prev = cur
    return n


TAGR = re.compile(u' \\((MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHLD|ED)-[0-9]+\\)', re.I)
TAGRE = re.compile(u'\\b(MUST|SHOULD|MAY|SHLD|ED)-([0-9]+)\\b')


def tag_strip(s):
    return TAGR.sub(u'', s)


def is_shell_pick(x, fam):
    """采集侧壳谓词的逐字照抄(整行序列正则), 供两遍壳集对拍用。"""
    if re.search(u'\\[Page \\d+\\]', x) is not None:
        return True
    if fam == u'old' and re.match(u'^RFC1122 +\\S', x) is not None:
        return True
    if x.strip() == u'':
        return True
    return False


def shell_by_shape(x, fam):
    """本遍壳谓词: 不跑序列正则, 折叠后比 token 形状。
    旧式页脚在末尾两 token('[Page','N]'), 眉行在首 token('RFC1122')加末 token 的 19xx/20xx 年形;
    新式只认空行——它的页码已被 RFC Editor 从正文里删净, 只剩行本身。"""
    s = fold(x)
    if s == u'':
        return True
    tk = s.split(u' ')
    if len(tk) >= 2 and tk[-2] == u'[Page':
        y = tk[-1]
        if len(y) >= 2 and y[-1] == u']' and y[:-1].isdigit():
            return True
    if fam == u'old':
        if len(tk) >= 4 and tk[0] == u'RFC1122':
            y = tk[-1]
            if len(y) == 4 and (y[:2] == u'19' or y[:2] == u'20') and y[2:].isdigit():
                return True
    return False


# ---------- 0. 面量 ⇎ 行式 ⇎ 壳账 ----------
F['bytes'] = [len(B[i]) for i in range(NSRC)]
F['chars'] = [len(T[i]) for i in range(NSRC)]
F['lines'] = [len(L[i]) for i in range(NSRC)]
F['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
F['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
F['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
F['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
F['cr'] = [cnt_cur(T[i], u'\r') for i in range(NSRC)]
F['lf'] = [cnt_cur(T[i], NL) for i in range(NSRC)]
F['ff'] = [cnt_cur(T[i], u'\x0c') for i in range(NSRC)]
F['ff_alone'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
F['ff_led'] = [len([x for x in L[i] if len(x) and ord(x[0]) == 12]) for i in range(NSRC)]
F['ff_before_nl'] = [cnt_cur(T[i], u'\x0c' + NL) for i in range(NSRC)]
F['ff_at_eof'] = [1 if T[i][-1:] == u'\x0c' else 0 for i in range(NSRC)]
F['trailing_nl'] = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
F['row_form_ledger'] = [(F['splitlines'][i] - F['splitnl'][i]) - (F['ff_before_nl'][i] - F['trailing_nl'][i])
                        for i in range(NSRC)]
F['foot'] = [len([x for x in L[i] if shell_by_shape(x, FAM[i]) and u'[Page' in fold(x)]) for i in range(NSRC)]
F['hdr_old'] = [len([x for x in L[i] if FAM[i] == u'old' and fold(x).split(u' ')[0] == u'RFC1122'])
                for i in range(NSRC)]
F['shell_lines'] = [len([x for x in L[i] if shell_by_shape(x, FAM[i])]) for i in range(NSRC)]
F['shell_ledger'] = [F['shell_lines'][i] - (F['blank'][i] + F['foot'][i] + F['hdr_old'][i]) for i in range(NSRC)]
F['bom'] = [1 if L[i][0] == u'\ufeff' else 0 for i in range(NSRC)]
F['end_nl'] = [1 if T[i].endswith(NL) else 0 for i in range(NSRC)]
F['pgnum'] = [len([x for x in L[i] if not [c for c in x if not (c.isdigit() or c.isspace())]
                  and digit_runs(x) == 1 and x.strip() != u'']) for i in range(NSRC)]
F['pgnum_shell'] = [len([x for x in L[i] if not [c for c in x if not (c.isdigit() or c.isspace())]
                         and digit_runs(x) == 1 and x.strip() != u'' and shell_by_shape(x, FAM[i])])
                    for i in range(NSRC)]
F['pgnum_overstrip'] = [F['pgnum'][i] - F['pgnum_shell'][i] for i in range(NSRC)]
F['pgnum_row_lines'] = [[n + 1 for n in range(len(L[i]))
                        if not [c for c in L[i][n] if not (c.isdigit() or c.isspace())]
                        and digit_runs(L[i][n]) == 1 and L[i][n].strip() != u''
                        and not shell_by_shape(L[i][n], FAM[i])] for i in range(NSRC)]
LOW = [pnorm(T[i]) for i in range(NSRC)]
FOLDC = [fold(T[i]) for i in range(NSRC)]
SHP = [[x for x in L[i] if not shell_by_shape(x, FAM[i])] for i in range(NSRC)]
SHC = [u' '.join(fold(x) for x in SHP[i]) for i in range(NSRC)]
LOW_SHLIG = [SHC[i].lower() for i in range(NSRC)]
SHTAGC = [tag_strip(SHC[i]) for i in range(NSRC)]
LOW_TAG = [SHTAGC[i].lower() for i in range(NSRC)]
SHFOLD = [pnorm(NL.join(SHP[i])) for i in range(NSRC)]
assert LOW_SHLIG == [pnorm(x) for x in SHC], u'折平两轨不等'
# 逐行偏移表: 摘壳折平面上第若干字符落在原文件第几行(本遍用累积长度, 发射段用另一张表复核)
LNOF = []
for i in range(NSRC):
    arr, off, first = [], 0, True
    for n in range(len(L[i])):
        if shell_by_shape(L[i][n], FAM[i]):
            continue
        s = fold(L[i][n])
        arr.append((off, off + len(s), n + 1))
        off += 1 + len(s) if not first else len(s)
        first = False
    LNOF.append(arr)


def sh_line_of(i, a):
    r = 0
    for st, e, n in LNOF[i]:
        if st <= a:
            r = n
        else:
            break
    return r


assert u' '.join([fold(x) for x in SHP[0]]) == SHC[0]

# ---------- 1. 非 ASCII: 只在参考文献与署名地址里 ----------
F['nonascii'] = [sorted(set([ord(c) for c in T[i] if ord(c) > 127])) for i in range(NSRC)]
F['na_total'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(NSRC)]
F['na_bom'] = [F['bom'][i] for i in range(NSRC)]
F['na_other'] = [F['na_total'][i] - F['na_bom'][i] for i in range(NSRC)]
F['na_ledger'] = [F['na_total'][i] - F['na_bom'][i] - F['na_other'][i] for i in range(NSRC)]
# 后段起点: References 标题在目录印一次、正文印一次(可带节号), 取后印的那一次; 旧式 1122 连这个标题也没有
REFHEAD = re.compile(u'^(?:\\d+(?:\\.\\d+)*\\.? +)?references$')
REFH = []
for i in range(NSRC):
    ks = [n for n in range(len(L[i])) if REFHEAD.match(pnorm(L[i][n]))]
    REFH.append(ks)
F['ref_toc_line'] = [(ks[0] + 1 if ks else -1) for ks in REFH]
F['ref_body_line'] = [(ks[-1] + 1 if ks else -1) for ks in REFH]
F['ref_print_n'] = [len(ks) for ks in REFH]
F['ref_ledger'] = [F['ref_print_n'][i] - (1 if F['ref_toc_line'][i] > 0 else 0)
                   - (1 if F['ref_body_line'][i] > 0 and F['ref_body_line'][i] != F['ref_toc_line'][i] else 0)
                   for i in range(NSRC)]
ADDRH = []
for i in range(NSRC):
    ks = [n for n in range(len(L[i]))
          if pnorm(L[i][n]) in (u"author's address", u"authors' addresses", u'contributors')]
    ADDRH.append(ks)
F['addr_head_n'] = [len(ks) for ks in ADDRH]
F['addr_head_line'] = [(max(ks) + 1 if ks else -1) for ks in ADDRH]
NAL = []
for i in range(NSRC):
    NAL.append([n + 1 for n in range(len(L[i]))
                if [c for c in L[i][n] if ord(c) > 127] and L[i][n] != u'\ufeff'])
F['na_lines'] = [len([x for x in L[i] if [c for c in x if ord(c) > 127]]) for i in range(NSRC)]
F['na_name_lines'] = [len(x) for x in NAL]
F['na_bom_line'] = [F['na_lines'][i] - F['na_name_lines'][i] for i in range(NSRC)]
F['na_after_ref'] = [len([n for n in NAL[i]
                          if F['ref_body_line'][i] > 0 and n > F['ref_body_line'][i]]) for i in range(NSRC)]
F['na_before_ref'] = [F['na_name_lines'][i] - F['na_after_ref'][i] for i in range(NSRC)]
F['na_first_after_ref'] = [(min([n - F['ref_body_line'][i] for n in NAL[i]])
                            if (NAL[i] and F['ref_body_line'][i] > 0) else -1) for i in range(NSRC)]
F['na_ref_entry_lines'] = [len([n for n in NAL[i] if re.match(u'^\\s*\\[[A-Z]', L[i][n - 1])])
                           for i in range(NSRC)]
F['na_addr_bullet'] = [len([n for n in NAL[i] if L[i][n - 1].strip().startswith(u'*')]) for i in range(NSRC)]
F['na_other_lines'] = [F['na_name_lines'][i] - F['na_ref_entry_lines'][i] - F['na_addr_bullet'][i]
                       for i in range(NSRC)]
F['na_place_ledger'] = [F['na_name_lines'][i] - F['na_ref_entry_lines'][i] - F['na_addr_bullet'][i]
                        - F['na_other_lines'][i] for i in range(NSRC)]
F['na_cp_tot'] = sum([len(x) for x in F['nonascii']])
F['na_cp_new'] = sum([len(x) for i, x in enumerate(F['nonascii']) if FAM[i] == u'new'])
F['bom_in_fold'] = [1 if u'\ufeff' in SHC[i] else 0 for i in range(NSRC)]
F['bom_survives'] = sum(F['bom_in_fold'])
F['na_old_total'] = sum(F['na_total'][i] for i in OLD)

# ---------- 2. 拼写族 ⇎ 术语换代 ----------
SPELL = [u'keep-alive', u'keepalive', u'keep alive', u'keeps alive', u'keep-alives',
         u'idle', u'idle timeout', u'inactive', u'persistent', u'acknowledgement',
         u'acknowledgment', u'implementors', u'implementers', u'two hours', u'time out']
F['spell'] = [[cnt_re(LOW[i], p) for p in SPELL] for i in range(NSRC)]
F['spell_word'] = [[ub_re(LOW[i], p) for p in SPELL] for i in range(NSRC)]
F['spell_ruler_gap'] = [F['spell'][i][k] - F['spell_word'][i][k] for i in range(NSRC) for k in range(len(SPELL))]
F['spell_ruler_gap_tot'] = sum(F['spell_ruler_gap'])
F['spell_tot'] = [sum(F['spell'][i]) for i in range(NSRC)]
F['ka_forms'] = [[k for k in (0, 1, 2, 3, 4) if F['spell'][i][k]] for i in range(NSRC)]
F['ka_form_n'] = [len(x) for x in F['ka_forms']]
F['ka_merged'] = sum(F['spell'][i][1] for i in range(NSRC))
F['ka_hyphen'] = [F['spell'][i][0] for i in range(NSRC)]
F['ack'] = [[F['spell'][i][9], F['spell'][i][10]] for i in range(NSRC)]
F['ack_both'] = [1 if min(F['ack'][i]) > 0 else 0 for i in range(NSRC)]
F['ack_minor'] = [min(F['ack'][i]) for i in range(NSRC)]
F['ack_major'] = [max(F['ack'][i]) for i in range(NSRC)]
F['ack_skew'] = [round(F['ack_major'][i] / float(F['ack_minor'][i]), 2) if F['ack_minor'][i] else -1
                 for i in range(NSRC)]
F['impl'] = [[F['spell'][i][11], F['spell'][i][12]] for i in range(NSRC)]
F['impl_own'] = [[u'implementors' if F['impl'][i][0] and not F['impl'][i][1] else u'',
                  u'implementers' if F['impl'][i][1] and not F['impl'][i][0] else u''] for i in range(NSRC)]
F['idle_term'] = [F['spell'][i][5] for i in range(NSRC)]
F['idle_compound'] = [F['spell'][i][6] for i in range(NSRC)]
F['persist'] = [F['spell'][i][8] for i in range(NSRC)]
F['spell_own'] = [[SPELL[k] for k in range(len(SPELL))
                   if F['spell'][i][k] and sum(1 for j in range(NSRC) if F['spell'][j][k]) == 1]
                  for i in range(NSRC)]
F['spell_own_tot'] = sum(len(x) for x in F['spell_own'])

# ---------- 3. 义务词四档 ⇎ 编号族 ----------
TONE = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']
F['tone_line'] = [[sum([ub_re(x, w) for x in L[i]]) for w in TONE] for i in range(NSRC)]
F['tone_fold'] = [[ub_re(FOLDC[i], w) for w in TONE] for i in range(NSRC)]
F['tone_sh'] = [[ub_re(SHC[i], w) for w in TONE] for i in range(NSRC)]
F['tone_tag'] = [[ub_re(SHTAGC[i], w) for w in TONE] for i in range(NSRC)]
F['tone_wrap_gain'] = [F['tone_fold'][i][k] - F['tone_line'][i][k] for i in range(NSRC) for k in range(5)]
F['tone_sh_gain'] = [F['tone_sh'][i][k] - F['tone_fold'][i][k] for i in range(NSRC) for k in range(5)]
F['tone_tag_gain'] = [F['tone_tag'][i][k] - F['tone_sh'][i][k] for i in range(NSRC) for k in range(5)]
F['tone_tot'] = [sum(F['tone_sh'][i]) for i in range(NSRC)]
F['tone_ledger'] = [F['tone_sh'][i][0] - F['tone_sh'][i][1] - (F['tone_sh'][i][0] - F['tone_sh'][i][1])
                    for i in range(NSRC)]
F['must_bare'] = [F['tone_sh'][i][0] - F['tone_sh'][i][1] for i in range(NSRC)]
F['mustnot_of_must'] = [1 if F['tone_sh'][i][1] <= F['tone_sh'][i][0] else 0 for i in range(NSRC)]
F['tone_must_ledger'] = [F['tone_sh'][i][0] - F['tone_sh'][i][1] - F['must_bare'][i] for i in range(NSRC)]
F['tag_raw'] = [len(TAGRE.findall(T[i])) for i in range(NSRC)]
F['tag_sh'] = [len(TAGRE.findall(SHC[i])) for i in range(NSRC)]
F['tag_decl'] = [cnt_re(LOW_SHLIG[i], pnorm(u'individually labeled')) for i in range(NSRC)]
F['tag_kinds'] = [[len([1 for m in TAGRE.finditer(SHC[i]) if m.group(1) == w])
                   for w in (u'MUST', u'SHOULD', u'MAY', u'SHLD', u'ED')] for i in range(NSRC)]
F['tag_kind_sum'] = [sum(x) for x in F['tag_kinds']]
F['tag_kind_close'] = [F['tag_kind_sum'][i] - F['tag_sh'][i] for i in range(NSRC)]
F['tag_paren'] = [len(TAGR.findall(SHC[i])) for i in range(NSRC)]


def _prev(face, j, k):
    return face[j - k] if j - k >= 0 else u''


F['tag_bare'] = [len([m for m in TAGRE.finditer(SHC[i]) if _prev(SHC[i], m.start(), 1) != u'('])
                 for i in range(NSRC)]
TAGBRK = re.compile(u'\\[\\((?:MUST|SHOULD|MAY|SHLD|ED)-[0-9]+\\)\\]')
TAGPR = re.compile(u'\\((?:MUST|SHOULD|MAY|SHLD|ED)-[0-9]+ -- ')
F['tag_paren_bracket'] = [len(TAGBRK.findall(SHC[i])) for i in range(NSRC)]
F['tag_paren_prose'] = [len(TAGPR.findall(SHC[i])) for i in range(NSRC)]
F['tag_paren_prose_samples'] = [[SHC[i][m.start():m.end() + 20] for m in TAGPR.finditer(SHC[i])][:2]
                                for i in range(NSRC)]
F['tag_bracket_samples'] = [[SHC[i][max(0, m.start() - 16):m.end() + 6] for m in TAGBRK.finditer(SHC[i])][:3]
                         for i in range(NSRC)]
F['tag_form_ledger'] = [F['tag_paren'][i] + F['tag_paren_prose'][i] + F['tag_paren_bracket'][i]
                        + F['tag_bare'][i] - F['tag_sh'][i] for i in range(NSRC)]
F['tag_paren_kind'] = [[len([1 for m in TAGR.finditer(SHC[i]) if m.group(1).upper() == w])
                        for w in (u'MUST', u'MUST NOT', u'SHOULD NOT', u'SHOULD', u'MAY', u'SHLD', u'ED')]
                       for i in range(NSRC)]
F['tag_paren_kind_close'] = [sum(F['tag_paren_kind'][i]) - F['tag_paren'][i] for i in range(NSRC)]


def _after(face, j):
    while j < len(face) and face[j] == u' ':
        j += 1
    return face[j:j + 1]


F['tag_paren_period'] = [len([m for m in TAGR.finditer(SHC[i]) if _after(SHC[i], m.end()) == u'.'])
                         for i in range(NSRC)]
F['tag_paren_comma'] = [len([m for m in TAGR.finditer(SHC[i]) if _after(SHC[i], m.end()) == u','])
                        for i in range(NSRC)]
F['tag_paren_mid'] = [F['tag_paren'][i] - F['tag_paren_period'][i] - F['tag_paren_comma'][i]
                      for i in range(NSRC)]
F['tag_paren_place_close'] = [F['tag_paren_period'][i] + F['tag_paren_comma'][i]
                              + F['tag_paren_mid'][i] - F['tag_paren'][i] for i in range(NSRC)]
F['tag_max_num'] = [max([int(m.group(2)) for m in TAGRE.finditer(T[i])] or [0]) for i in range(NSRC)]
# 去编号档相对摘壳档在义务词上的跌落: 括号标注里的 MUST/MAY 本身也是整词, 剥掉就少数
F['tone_drop_tag'] = [[F['tone_sh'][i][k] - F['tone_tag'][i][k] for k in range(5)] for i in range(NSRC)]
F['tone_drop_tot'] = [sum(x) for x in F['tone_drop_tag']]
F['tone_drop_ledger'] = [F['tone_drop_tot'][i] - sum([abs(x) for x in F['tone_tag_gain'][i * 5:i * 5 + 5]])
                         for i in range(NSRC)]

# ---------- 4. 时长语形: 词写 ⇎ 数字写 ⇎ 两把单位尺 ----------
DUR = [u'two hours', u'no less than two hours', u'120 minutes', u'three times', u'3 times',
       u'milliseconds', u' ms', u'second', u'Timeout', u'timeout']
F['dur'] = [[cnt_re(LOW_SHLIG[i], d.lower()) for d in DUR] for i in range(NSRC)]
F['dur_word'] = [[ub_re(LOW_SHLIG[i], d.lower()) for d in DUR] for i in range(NSRC)]
F['dur_ruler_gap'] = [F['dur'][i][k] - F['dur_word'][i][k] for i in range(NSRC) for k in range(len(DUR))]
NUMW = [u'two hours', u'one hour', u'ten minutes', u'some long amount of time', u'three times',
        u'120 minutes', u'2 hours', u'120 seconds']
F['numw'] = [[cnt_re(LOW_SHLIG[i], w.lower()) for w in NUMW] for i in range(NSRC)]
F['num_digit_two'] = [F['numw'][i][5] + F['numw'][i][6] for i in range(NSRC)]
F['num_digit_two_tot'] = sum(F['num_digit_two'])
F['num_word_two'] = [F['numw'][i][0] + F['numw'][i][1] for i in range(NSRC)]
F['num_longform_two'] = [F['numw'][i][3] for i in range(NSRC)]
UNITW = [u'milliseconds', u'microseconds', u'seconds', u'ms']
UNITW_S = UNITW + [u's']
UNIT_IDX = {u'milliseconds': 0, u'microseconds': 1, u'seconds': 2, u'ms': 3, u's': 4}


def num_pairs(text, units):
    """手工扫数字串(含小数与千分位逗号), 再就地读紧跟其后的单位词; 采集侧是一条正则选择支。"""
    out, k, n = [], 0, len(text)
    while k < n:
        if not text[k].isdigit():
            k += 1
            continue
        st = k
        while k < n and (text[k].isdigit() or (text[k] in u'.,' and k + 1 < n and text[k + 1].isdigit())):
            k += 1
        num = text[st:k]
        j = k
        while j < n and text[j] == u' ':
            j += 1
        for u in units:
            if text[j:j + len(u)].lower() == u and not (j + len(u) < n and text[j + len(u)].isalpha()):
                out.append((num, u))
                break
    return out


RXU_PICK = re.compile(u'(?<![A-Za-z0-9.])(\\d+(?:[.,]\\d+)?)[ ]?'
                      u'(milliseconds|microseconds|seconds|ms|s)(?![A-Za-z])')


def num_pairs_re(text):
    """采集侧那条正则选择支的逐字照抄, 只为与手工扫描尺对拍(两把尺的差另立键)。"""
    return sorted(set([tuple(x) for x in RXU_PICK.findall(text)]))


NUMLIT = [u'0', u'0.5', u'1', u'1.0', u'10', u'20', u'25', u'3', u'30', u'34', u'5', u'6', u'60', u'100']
UORD = [u'ms', u'seconds', u'milliseconds', u'microseconds', u's']
F['num_pairs'] = [sorted(set(num_pairs(T[i], UNITW))) for i in range(NSRC)]
F['num_pairs_wide'] = [sorted(set(num_pairs(T[i], UNITW_S))) for i in range(NSRC)]
F['numval_n'] = [len(x) for x in F['num_pairs']]
F['numval_wide_n'] = [len(x) for x in F['num_pairs_wide']]
F['numval_s_extra'] = [[list(x) for x in F['num_pairs_wide'][i] if x not in F['num_pairs'][i]] for i in range(NSRC)]
F['numval_s_lost'] = [[list(x) for x in F['num_pairs'][i] if x not in F['num_pairs_wide'][i]] for i in range(NSRC)]
F['num'] = [[len([1 for x in F['num_pairs'][i] if x[0] == v]) for v in NUMLIT] for i in range(NSRC)]
F['num_unlisted'] = [[u'%s %s' % (v, u) for (v, u) in F['num_pairs'][i] if v not in NUMLIT]
                     for i in range(NSRC)]
F['num_unlisted_n'] = [len(x) for x in F['num_unlisted']]
F['num_lit_close'] = [sum(F['num'][i]) + F['num_unlisted_n'][i] - F['numval_n'][i] for i in range(NSRC)]
F['num_tot'] = [sum([cnt_re(T[i], v + u' ') for v in NUMLIT]) for i in range(NSRC)]
F['num_pairs_pick'] = [num_pairs_re(T[i]) for i in range(NSRC)]
F['num_ruler_gap'] = [len(set(F['num_pairs_wide'][i]) - set(F['num_pairs_pick'][i]))
                      + len(set(F['num_pairs_pick'][i]) - set(F['num_pairs_wide'][i])) for i in range(NSRC)]
F['num_own'] = [[u'%s %s' % (v, u) for (v, u) in F['num_pairs'][i]
                  if sum(1 for j in range(NSRC) if (v, u) in F['num_pairs'][j]) == 1]
                 for i in range(NSRC)]
F['digit_form_two_hours'] = [cnt_re(T[i], u'2 hours') + cnt_re(T[i], u'120 minutes') for i in range(NSRC)]

# ---------- 5. 判词针四档 ----------
ROLEN = [
    u'they MUST default to off',
    u'MUST default to no less than two hours',
    u'configurable and MUST default',
    u'interval MUST be configurable',
    u'is said to be "idle"',
    u'no incoming segments received',
    u'to confirm that an idle connection is still active',
    u'MUST NOT interpret failure to respond',
    u'no requirements on the length (or existence) of this timeout',
    u'Servers will usually have some timeout value',
    u'Connections can be closed at any time',
    u'issue a graceful close',
    u'no longer maintain an inactive connection',
    u'MAY close the transport connection',
    u'received closure signal',
    u'Proxy servers might make this a higher value',
    u'encouraged to maintain open connections for as long as possible',
    u'permitted to terminate idle connections',
    u'SHOULD first send a GOAWAY',
    u'the terminating endpoint',
    u'sent a SETTINGS frame but did not receive',
    u'idle connection is still functional',
    u'SETTINGS_TIMEOUT',
    u'max_idle_timeout',
    u'the minimum of the two advertised values',
    u'sole advertised value',
    u'MUST increase the idle timeout period',
    u'at least three times the current Probe Timeout',
    u'excessively small idle timeout periods',
    u'Idle timeout is disabled',
    u'connection is silently closed',
    u'abandons the connection',
    u'restarts its idle timer',
    u'Deferring Idle Timeout',
    u'SEG.SEQ = SND.NXT-1',
    u'one garbage octet',
    u'to elicit a response',
]
F['role_line'] = [[len([x for x in L[i] if cnt_re(pnorm(x), pnorm(r))]) for r in ROLEN] for i in range(NSRC)]
F['role_fold'] = [[cnt_re(LOW[i], pnorm(r)) for r in ROLEN] for i in range(NSRC)]
F['role_sh'] = [[cnt_re(LOW_SHLIG[i], pnorm(r)) for r in ROLEN] for i in range(NSRC)]
F['role_tag'] = [[cnt_re(LOW_TAG[i], pnorm(r)) for r in ROLEN] for i in range(NSRC)]
F['role_line_n'] = [sum(F['role_line'][i]) for i in range(NSRC)]
F['role_fold_n'] = [sum(F['role_fold'][i]) for i in range(NSRC)]
F['role_sh_n'] = [sum(F['role_sh'][i]) for i in range(NSRC)]
F['role_tag_n'] = [sum(F['role_tag'][i]) for i in range(NSRC)]
F['role_line_read_n'] = sum([1 for i in range(NSRC) for k in range(len(ROLEN)) if F['role_line'][i][k]])
F['role_line_miss_n'] = sum([1 for i in range(NSRC) for k in range(len(ROLEN))
                             if F['role_line'][i][k] == 0 and F['role_fold'][i][k]])
F['role_wrap'] = [[k for k in range(len(ROLEN)) if F['role_line'][i][k] == 0 and F['role_fold'][i][k] > 0]
                  for i in range(NSRC)]
F['role_wrap_n'] = [len(x) for x in F['role_wrap']]
F['role_wrap_keys'] = [(i, k) for i in range(NSRC) for k in F['role_wrap'][i]]
F['role_shell'] = [[k for k in range(len(ROLEN)) if F['role_fold'][i][k] == 0 and F['role_sh'][i][k] > 0]
                   for i in range(NSRC)]
F['role_shell_n'] = [len(x) for x in F['role_shell']]
F['role_shell_needles'] = [(i, k) for i in range(NSRC) for k in F['role_shell'][i]]
F['role_tagcut'] = [[k for k in range(len(ROLEN)) if F['role_sh'][i][k] == 0 and F['role_tag'][i][k] > 0]
                    for i in range(NSRC)]
F['role_tagcut_n'] = [len(x) for x in F['role_tagcut']]
F['role_tagcut_keys'] = [(i, k) for i in range(NSRC) for k in F['role_tagcut'][i]]
F['role_gain_fold'] = [F['role_fold_n'][i] - F['role_line_n'][i] for i in range(NSRC)]
F['role_gain_sh'] = [F['role_sh_n'][i] - F['role_fold_n'][i] for i in range(NSRC)]
F['role_gain_tag'] = [F['role_tag_n'][i] - F['role_sh_n'][i] for i in range(NSRC)]
F['role_src'] = {k: LBL[i] for i in range(NSRC) for k in range(len(ROLEN)) if F['role_line'][i][k] == 0
                 and F['role_tag'][i][k] > 0}
F['role_read_tag_n'] = sum([1 for i in range(NSRC) for k in range(len(ROLEN)) if F['role_tag'][i][k]])
F['needle_n'] = len(ROLEN)
F['role_hit_by_face'] = [sum([1 for k in range(len(ROLEN)) if F['role_tag'][i][k]]) for i in range(NSRC)]
WRAPK = sorted([k for i, k in F['role_wrap_keys']])
F['role_wrap_flat'] = [[LBL[i], ROLEN[k]] for i in range(NSRC) for k in F['role_wrap'][i]]
F['role_tagcut_flat'] = [[LBL[i], ROLEN[k]] for i in range(NSRC) for k in F['role_tagcut'][i]]

# ---------- 6. 反向对照针(默认摘壳折平面 ⇎ 页码壳针走全篇折平面) ----------
NEG = [(u'max_idle_timeout', [0, 1, 2, 3], u'sh'), (u'SETTINGS_TIMEOUT', [0, 1, 2, 4], u'sh'),
       (u'GOAWAY', [0, 1, 2, 4], u'sh'), (u'two hours', [2, 3, 4], u'sh'),
       (u'no less than two hours', [2, 3, 4], u'sh'), (u'(MUST-27)', [0, 2, 3, 4], u'sh'),
       (u'the key words', [0], u'sh'), (u'[Page 1]', [1, 2, 3, 4], u'fold'),
       (u'keep-alive', [4], u'sh'), (u'quic', [0, 2], u'sh'), (u'http/2', [0, 1, 2], u'sh'),
       (u'RFC 2119', [], u'sh'), (u'persistent connection', [0, 4], u'sh'),
       (u'PTO', [0, 1, 2, 3], u'sh'), (u'idle timeout', [0, 1, 2, 3], u'sh')]
FACEK = {u'sh': LOW_SHLIG, u'fold': LOW}
# 页码壳针 “[Page 1]” 在两把面尺上的读数与它所在的原始行(摘壳面把它当壳吃了, 所以它进不了锚)
F['page_lit_fold'] = [cnt_re(LOW[i], pnorm(u'[Page 1]')) for i in range(NSRC)]
F['page_lit_sh'] = [cnt_re(LOW_SHLIG[i], pnorm(u'[Page 1]')) for i in range(NSRC)]
F['page_lit_rows'] = [[n for n, y in enumerate(L[i], 1) if u'[page 1]' in pnorm(y)] for i in range(NSRC)]
F['page_lit_rows_shell'] = sum([1 for i in range(NSRC) for n in F['page_lit_rows'][i]
                                if not is_shell_pick(L[i][n - 1], FAM[i])])
F['neg_faces'] = [x[2] for x in NEG]
F['neg_fold_n'] = len([x for x in F['neg_faces'] if x != u'sh'])
F['neg_n'] = len(NEG)
F['neg_probes'] = sum(len(x[1]) for x in NEG)
F['neg_word'] = [[ub_re(FACEK[f][i], pnorm(nd)) for nd, ex, f in NEG] for i in range(NSRC)]
F['neg_sub'] = [[cnt_re(FACEK[f][i], pnorm(nd)) for nd, ex, f in NEG] for i in range(NSRC)]
F['neg_zero_hits'] = sum([sum([F['neg_word'][i][k] for i in ex]) for k, (nd, ex, f) in enumerate(NEG)])
F['neg_owner_present'] = len([1 for k, (nd, ex, f) in enumerate(NEG)
                              if sum([F['neg_word'][i][k] for i in range(NSRC) if i not in ex]) > 0])
F['neg_cold_probes'] = [NEG[k][0] for k, (nd, ex, f) in enumerate(NEG)
                        if sum([F['neg_word'][i][k] for i in range(NSRC) if i not in ex]) == 0]
F['neg_sub_false_rows'] = [[LBL[i], NEG[k][0], F['neg_sub'][i][k], F['neg_word'][i][k]]
                           for i in range(NSRC) for k in range(len(NEG))
                           if F['neg_sub'][i][k] > F['neg_word'][i][k]]
F['neg_sub_false'] = sum([x[2] - x[3] for x in F['neg_sub_false_rows']])
F['neg_sub_ruler'] = sum([x[2] for x in F['neg_sub_false_rows']])

# ---------- 7. 答句: 逐字符句界 ----------
WIN = [u'MUST default to no less than two hours', u'MUST default to no less than two hours',
       u'places no requirements on the length', u'permitted to terminate idle connections',
       u'computed as the minimum of the two advertised values']


def sent_bounds(face, at):
    a = 0
    k = at
    while k > 0:
        c = face[k - 1]
        if c in u'.!?' and face[k:k + 1] in (u' ', u'\n') and (k + 1 >= len(face) or
                                                              not face[k + 1:k + 2].isdigit()):
            a = k
            break
        k -= 1
    b = len(face)
    k = at + 1
    while k < len(face):
        if face[k] in u'.!?' and (k + 1 >= len(face) or face[k + 1:k + 2] in (u' ', u'\n')):
            b = k + 1
            break
        k += 1
    return a, b


F['ans_at'] = [LOW_SHLIG[i].find(pnorm(WIN[i])) for i in range(NSRC)]
assert all(x >= 0 for x in F['ans_at']), F['ans_at']
F['ans'] = [SHC[i][sent_bounds(LOW_SHLIG[i], F['ans_at'][i])[0]:sent_bounds(LOW_SHLIG[i], F['ans_at'][i])[1]]
            for i in range(NSRC)]
F['ans_pair_same'] = 1 if tag_strip(F['ans'][1]) == F['ans'][0] else 0
F['ans_words'] = [len(F['ans'][i].split()) for i in range(NSRC)]
F['ans_chars'] = [len(F['ans'][i]) for i in range(NSRC)]
F['ans_start_line'] = [sh_line_of(i, F['ans_at'][i]) for i in range(NSRC)]
F['ans_end_line'] = [sh_line_of(i, F['ans_at'][i] + len(pnorm(WIN[i])) - 1) for i in range(NSRC)]
F['ans_span'] = [F['ans_end_line'][i] - F['ans_start_line'][i] + 1 for i in range(NSRC)]
F['ans_needle_line'] = [sh_line_of(i, F['ans_at'][i]) for i in range(NSRC)]
F['ans_sent_line'] = [sh_line_of(i, LOW_SHLIG[i].find(pnorm(F['ans'][i]))) for i in range(NSRC)]
F['ans_sent_end'] = [sh_line_of(i, LOW_SHLIG[i].find(pnorm(F['ans'][i])) + len(pnorm(F['ans'][i])) - 1)
                     for i in range(NSRC)]
F['ans_sent_span'] = [F['ans_sent_end'][i] - F['ans_sent_line'][i] + 1 for i in range(NSRC)]
F['ans_anchor_line'] = [F['ans_sent_line'][i] for i in range(NSRC)]
F['ans_span_tot'] = sum(F['ans_sent_span'])
F['ans_block_lines'] = [F['ans_sent_span'][i] for i in range(NSRC)]
F['ans_shell_rows'] = [0] * NSRC
F['ans_tagdiff'] = F['ans_chars'][1] - F['ans_chars'][0]
F['ans_tag_len'] = sum([len(m.group(0)) for m in TAGR.finditer(F['ans'][1])])
F['ans_tag_len_ledger'] = F['ans_chars'][1] - F['ans_chars'][0] - F['ans_tag_len']
F['ans_tag_n_in_sent'] = [len(TAGRE.findall(F['ans'][i])) for i in range(NSRC)]
F['ans_na'] = [len([c for c in F['ans'][i] if ord(c) > 127]) for i in range(NSRC)]
F['ans_punct'] = [1 if F['ans'][i].strip().endswith(u'.') else 0 for i in range(NSRC)]

# ---------- 8. 两段保活节的逐句对照(1122 §4.2.3.6 ⇎ 9293 §3.8.4) ----------
H1122 = [n for n in range(len(L[0])) if L[0][n].strip().startswith(u'4.2.3.6')][-1]
H9293 = [n for n in range(len(L[1])) if L[1][n].startswith(u'3.8.4.')][0]
N9293 = [n for n in range(H9293 + 1, len(L[1])) if L[1][n].startswith(u'3.8.5.')][0]
N1122 = [n for n in range(H1122 + 1, len(L[0])) if re.match(u'^\\s+4\\.2\\.3\\.7 +', L[0][n])][0]
B1 = L[0][H1122 + 1:N1122]
B2 = L[1][H9293 + 1:N9293]
DIS1 = [n for n in range(len(B1)) if B1[n].strip() == u'DISCUSSION:'][0]
S1 = B1[:DIS1]
S2 = B2
F['ovl_head_line'] = [H1122 + 1, H9293 + 1]
F['ovl_block_lines'] = [len(B1), len(B2)]
F['ovl_spec_lines'] = [len(S1), len(S2)]
F['ovl_shell_in_block'] = len([x for x in S1 if shell_by_shape(x, FAM[0])])
F['ovl_spec_lines_content'] = [len([x for x in S1 if not shell_by_shape(x, FAM[0])]), len(S2)]


def sents(lines):
    out, buf = [], []
    for x in lines:
        buf.append(x)
    face = pnorm(NL.join(buf))
    k, st = 0, 0
    for m in re.finditer(u'[.!?]', face):
        j = m.end()
        if j >= len(face) or face[j] != u' ':
            continue
        nxt = face[j + 1:j + 2]
        if nxt == u'':
            continue
        out.append(face[st:j + 1].strip())
        st = j + 1
    if face[st:].strip():
        out.append(face[st:].strip())
    return [x for x in out if x]


A1 = sents(S1)
A2 = sents(S2)
A2T = [tag_strip(x).strip() for x in A2]


def canon(z):
    return z.replace(u'implementers', u'implementors').replace(u'acknowledgment', u'acknowledgement')


F['ovl_s1'] = len(A1)
F['ovl_s2'] = len(A2)
F['ovl_same_raw'] = len([z for z in A2 if z in A1])
F['ovl_same_tag'] = len([z for z in A2T if z in A1])
F['ovl_same_canon'] = len([z for z in A2T if canon(z) in [canon(y) for y in A1]])
F['ovl_new'] = F['ovl_s2'] - F['ovl_same_canon']
D1 = sents(B1[DIS1 + 1:])
F['ovl_disc_promoted'] = len([z for z in A2T if z not in A1 and canon(z) not in [canon(y) for y in A1]
                              and canon(z) in [canon(y) for y in D1]])
F['ovl_same_ledger'] = F['ovl_s2'] - F['ovl_same_canon'] - F['ovl_new']
F['ovl_monotone'] = sum([1 for a, b in ((F['ovl_same_raw'], F['ovl_same_tag']),
                                        (F['ovl_same_tag'], F['ovl_same_canon'])) if a <= b])
F['ovl_tag_only'] = F['ovl_same_tag'] - F['ovl_same_raw']

# ---------- 9. 节窗 ⇎ 目录行 ⇎ 引道符 ----------
SECND = [u'4.2.3.6', u'3.8.4', u'9.5', u'9.1', u'10.1']
SECTTL = [u'TCP Keep-Alives', u'TCP Keep-Alives', u'Failures and Timeouts',
          u'Connection Management', u'Idle Timeout']
F['sec_no'] = SECND
F['sec_print_n'] = []
F['sec_body_line'] = []
F['sec_toc_line'] = []
F['sec_toc_indent'] = []
F['sec_body_indent'] = []
F['sec_shell_rows'] = []
F['sec_end_no'] = []
F['sec_lines'] = []
F['sec_chars'] = []
F['sec_tone_tot'] = []
F['sec_child'] = []
F['sec_hit_n'] = []
F['head_toc_leader_strict'] = []
F['head_toc_leader_spaced'] = []
for i in range(NSRC):
    cands = [n for n in range(len(L[i])) if pnorm(L[i][n]).startswith(SECND[i] + u' ')
             or pnorm(L[i][n]) == pnorm(SECND[i] + u'. ' + SECTTL[i])]
    body = [n for n in cands if len(re.findall(u'\\.{3,}', L[i][n])) == 0
            and not shell_by_shape(L[i][n], FAM[i])]
    toc = [n for n in cands if len(re.findall(u'\\.{3,}', L[i][n])) > 0]
    bd = body[-1] if body else -1
    tt = toc[0] if toc else (cands[0] if cands else -1)
    depth = SECND[i].count(u'.')
    end = len(L[i])
    for n in range(bd + 1, len(L[i])):
        s = L[i][n].strip()
        if len(re.findall(u'\\.{3,}', L[i][n])) or shell_by_shape(L[i][n], FAM[i]):
            continue
        m = re.match(u'^(\\d+(?:\\.\\d+)*)\\.[ ]|^(\\d+(?:\\.\\d+)*)[ ]{2}', s)
        if m:
            num = (m.group(1) or m.group(2))
            if num.count(u'.') <= depth and num != SECND[i]:
                end = n
                break
    win = L[i][bd:end]
    shell_rows = len([x for x in win if shell_by_shape(x, FAM[i])])
    txt = pnorm(NL.join([x for x in win if not shell_by_shape(x, FAM[i])]))
    F['sec_print_n'].append(len(cands))
    F['sec_body_line'].append(bd + 1)
    F['sec_toc_line'].append(tt + 1 if tt >= 0 else -1)
    F['sec_toc_indent'].append(len(L[i][tt]) - len(L[i][tt].lstrip()) if tt >= 0 else -1)
    F['sec_body_indent'].append(len(L[i][bd]) - len(L[i][bd].lstrip()) if bd >= 0 else -1)
    F['sec_shell_rows'].append(shell_rows)
    F['sec_lines'].append(end - bd)
    F['sec_chars'].append(len(txt))
    F['sec_tone_tot'].append(sum([ub_re(txt.upper(), w) for w in TONE]))
    F['sec_child'].append(len([1 for x in win if re.match(u'^\\s*' + re.escape(SECND[i]) + u'\\.\\d', x.strip())]))
    F['sec_hit_n'].append(cnt_re(LOW_SHLIG[i], pnorm(SECTTL[i])))
    F['head_toc_leader_strict'].append(1 if tt >= 0 and len(re.findall(u'\\.{3,}', L[i][tt])) else 0)
    F['head_toc_leader_spaced'].append(1 if tt >= 0 and len(re.findall(u'(?:\\.\\s*){3,}', L[i][tt])) else 0)
    F['sec_end_no'].append(L[i][end].strip().split(u' ')[0] if end < len(L[i]) and L[i][end].strip() else u'')
F['sec_lines_tot'] = sum(F['sec_lines'])
F['sec_shell_tot'] = sum(F['sec_shell_rows'])
F['sec_tone_tot_all'] = sum(F['sec_tone_tot'])
F['sec_tone_only_n'] = len([x for x in F['sec_tone_tot'] if x])
F['sec_tone_zero_n'] = len([x for x in F['sec_tone_tot'] if x == 0])
F['sec_span_pct'] = [round(100.0 * F['sec_chars'][i] / len(LOW_SHLIG[i]), 2) for i in range(NSRC)]
F['sec_ans_inside'] = [1 if (F['sec_body_line'][i] <= F['ans_anchor_line'][i]
                             and F['ans_sent_end'][i] <= F['sec_body_line'][i] + F['sec_lines'][i]) else 0
                       for i in range(NSRC)]
F['sec_ans_gap'] = [F['ans_anchor_line'][i] - F['sec_body_line'][i] for i in range(NSRC)]
F['kw_at'] = []
for i in range(NSRC):
    a = LOW_SHLIG[i].find(pnorm(u'The key words'))
    F['kw_at'].append(a if a >= 0 else -1)
F['kw_docs'] = len([x for x in F['kw_at'] if x >= 0])
F['kw_cite_bcp'] = [cnt_re(LOW_SHLIG[i], pnorm(u'as described in BCP 14 [3] [12]')) for i in range(NSRC)]
F['kw_cite_pair'] = [cnt_re(LOW_SHLIG[i], pnorm(u'as described in BCP 14 [RFC2119] [RFC8174]'))
                     for i in range(NSRC)]
F['kw_head'] = [LOW_SHLIG[i][F['kw_at'][i]:F['kw_at'][i] + 190] for i in range(NSRC)]

# ---------- 10. 语态 ⇎ 引用 ⇎ 参数名 ----------
F['voice_we'] = [ub_re(LOW_SHLIG[i], u'we') for i in range(NSRC)]
F['voice_weverb'] = [sum([ub_re(LOW_SHLIG[i], u'we ' + v) for v in
                          (u'propose', u'show', u'observe', u'present', u'specify', u'define', u'use')])
                     for i in range(NSRC)]
F['voice_impersonal'] = [sum([cnt_re(LOW_SHLIG[i], pnorm(w)) for w in (u'this document', u'this specification')])
                         for i in range(NSRC)]
F['cit_brk'] = [len(re.findall(u'\\[RFC[0-9]{4}\\]', T[i])) for i in range(NSRC)]
F['cit_rfc'] = [len(re.findall(u'RFC [0-9]{4}', T[i])) for i in range(NSRC)]
F['cit_rfc_hyphen'] = [len(re.findall(u'RFC-[0-9]{4}', T[i])) for i in range(NSRC)]
CITED = [1122, 9293, 9112, 9113, 9000, 2119, 8174, 793, 7230, 7540]
F['cite_matrix'] = [[cnt_re(T[i], u'RFC %d' % c) for c in CITED] for i in range(NSRC)]
F['cite_own'] = [len([1 for j, c in enumerate(CITED) if F['cite_matrix'][i][j] and c != int(IDS[i])])
                 for i in range(NSRC)]
F['hexes'] = [len(re.findall(u'(?<![0-9A-Za-z])0x[0-9A-Fa-f]{2}(?![0-9A-Za-z])', T[i])) for i in range(NSRC)]
F['sec_refs'] = [len(re.findall(u'Section [0-9]', T[i])) for i in range(NSRC)]
PARA = [u'max_idle_timeout', u'SETTINGS_TIMEOUT', u'IDLE_TIMEOUT', u'initial_rtt', u'max_datagram_size']
F['par'] = [[cnt_re(T[i], p) for p in PARA] for i in range(NSRC)]
F['par_n'] = [sum(x) for x in F['par']]
F['par_under'] = [len(re.findall(u'\\b[a-z]+_[a-z_]+\\b', T[i])) for i in range(NSRC)]
F['par_own'] = [[PARA[k] for k in range(len(PARA))
                 if F['par'][i][k] and sum(1 for j in range(NSRC) if F['par'][j][k]) == 1] for i in range(NSRC)]
F['years'] = YR

# --- PICK BEGIN --- (与采集遍逐键对账: 同一把定义, 第二套实现)
PK = json.load(io.open(u'corpus/_b82meas.json', encoding='utf-8'))
SAMEK = [u'bytes', u'blank', u'maxlen', u'ff', u'nonascii', u'spell', u'pgnum', u'hexes', u'sec_refs',
         u'shell_lines', u'foot', u'bom', u'tag_raw']
AGREE, DIFFK = [], []
for kk in SAMEK:
    if kk == u'tag_raw':
        a, b = F[u'tag_raw'], PK[u'tag_dash']
    elif kk == u'foot':
        a, b = F[u'foot'], PK[u'foot']
    else:
        a, b = F[kk], PK[kk]
    if a == b:
        AGREE.append(kk)
    else:
        DIFFK.append((kk, u'值不符'))
SAMEK2 = [(u'tone_line', u'ob_line'), (u'tone_fold', u'ob_fold'), (u'lf', u'n_lf'), (u'cr', u'n_cr')]
for mk_k, pk_k in SAMEK2:
    if F[mk_k] == PK[pk_k]:
        AGREE.append(mk_k)
    else:
        DIFFK.append((mk_k, pk_k))
# 判词针两档(逐行 ⇎ 全篇折平)与采集遍三档的前两档逐枚对拍
ROLEPK = PK[u'needles3']
NEEDLEN = None
F['pick_needle_gap'] = 0
# 采集遍的 NEEDLES 前 30 枚与本遍 ROLEN 的交集按串对齐
PKND = [u'they MUST default to off', u'MUST default to no less than two hours', u'no less than two hours',
        u'interval MUST be configurable', u'is said to be "idle"', u'no incoming segments received',
        u'to confirm that an idle connection is still active', u'MUST NOT interpret failure to respond',
        u'a dead connection', u'no requirements on the length (or existence) of this timeout',
        u'Servers will usually have some timeout value', u'Connections can be closed at any time',
        u'at any time', u'issue a graceful close',
        u'encouraged to maintain open connections for as long as possible',
        u'permitted to terminate idle connections', u'SHOULD first send a GOAWAY', u'the terminating endpoint',
        u'a value of zero', u'max_idle_timeout', u'the minimum of the two advertised values',
        u'sole advertised value', u'MUST increase the idle timeout period',
        u'at least three times the current Probe Timeout', u'current Probe Timeout (PTO)',
        u'excessively small idle timeout periods', u'Liveness Testing', u'SETTINGS_TIMEOUT',
        u'connection for liveness', u'silent']
AGREE2, DIFF2 = [], []
for k, nd in enumerate(PKND):
    if nd not in ROLEN:
        continue
    j = ROLEN.index(nd)
    if [x[0] for x in ROLEPK[k]] == [F['role_line'][i][j] for i in range(NSRC)]:
        AGREE2.append(nd)
    else:
        DIFF2.append((nd, u'逐行档不符'))
    if [x[1] for x in ROLEPK[k]] == [F['role_fold'][i][j] for i in range(NSRC)]:
        AGREE2.append(nd + u'⇎折平')
    else:
        DIFF2.append((nd, u'折平档不符'))
F['numunit_pick'] = [[list(x) for x in F['num_pairs_pick'][i]] for i in range(NSRC)]
NUMAGREE = 1 if [[list(x) for x in F['num_pairs_pick'][i]] for i in range(NSRC)] == PK[u'numunit'] else 0
if NUMAGREE:
    AGREE.append(u'numunit')
else:
    DIFFK.append((u'numunit', u'两把单位尺对拍不符'))
PINP = [(lab, nd, ln0, ncnt) for lab, nd, ln0, ncnt in PK[u'pin_lines']
        if pnorm(nd) in pnorm(WIN[LBL.index(lab)])]
F['pin_checked'] = len(PINP)
F['pin_line_close'] = sum([abs(F['ans_needle_line'][LBL.index(lab)] - 1 - ln0) for lab, nd, ln0, ncnt in PINP])
if F['pin_line_close'] == 0 and F['pin_checked'] >= 2:
    AGREE.append(u'pin_line')
else:
    DIFFK.append((u'pin_line', u'答句首行与采集遍不符'))
F['pick_agree'] = len(AGREE) + len(AGREE2)
F['pick_diff'] = len(DIFFK) + len(DIFF2)
F['pick_same_n'] = len(SAMEK) + len(SAMEK2) + 2 + 2 * len([nd for nd in PKND if nd in ROLEN])
F['pick_diff_keys'] = [x[0] for x in DIFFK] + [x[0] for x in DIFF2]
assert not DIFFK, DIFFK[:4]
assert not DIFF2, DIFF2[:4]
# --- PICK END ---

# ---------- 布尔门(每道都能失败) ----------
CLOSE = {}
CLOSE[u'two_format_generations'] = 1 if (FAM == [u'old', u'new', u'new', u'new', u'new']
                                         and sum(F['foot'][i] for i in NEW) == 0
                                         and F['foot'][0] == 116 and F['hdr_old'][0] == 115) else 0
CLOSE[u'row_form_identity'] = 1 if sum([abs(x) for x in F['row_form_ledger']]) == 0 else 0
CLOSE[u'shell_ledger_zero'] = 1 if sum(F['shell_ledger']) == 0 and F['ff_alone'][0] == 116 \
    and F['ff'][0] == 116 else 0
CLOSE[u'na_all_in_back_matter'] = 1 if (sum(F['na_before_ref']) == 0 and sum(F['na_after_ref']) == 9
                                        and F['na_old_total'] == 0 and F['ref_print_n'] == [1, 2, 2, 2, 2]) else 0
CLOSE[u'bom_survives_shell'] = 1 if (F['bom_survives'] == 4 and F['bom'][0] == 0
                                     and F['na_bom_line'] == [0, 1, 1, 1, 1]) else 0
CLOSE[u'pgnum_naive_eats_content'] = 1 if (F['pgnum_shell'] == [0] * NSRC and F['pgnum'] == [1, 3, 0, 0, 0]
                                           and sum(F['pgnum_overstrip']) == 4) else 0
CLOSE[u'keepalive_merged_never'] = 1 if (F['ka_merged'] == 0 and sum(F['ka_hyphen'][i] for i in range(4)) >= 4
                                         and F['ka_hyphen'][4] == 0) else 0
CLOSE[u'idle_compound_quic_only'] = 1 if (F['idle_compound'][4] == 19 and sum(F['idle_compound'][i] for i in NEW[:3])
                                          + F['idle_compound'][0] == 0) else 0
CLOSE[u'ack_two_sides_both_present'] = 1 if (min(F['ack_minor'][i] for i in (0, 1)) >= 1
                                             and F['ack'][2] == [4, 0] and F['ack'][3] == [0, 8]) else 0
CLOSE[u'implementors_1122_only'] = 1 if (F['impl'][0][0] == 8 and sum(F['impl'][i][0] for i in range(1, NSRC)) == 0) else 0
CLOSE[u'tone_wrap_only_mustnot'] = 1 if (
    [F['tone_wrap_gain'][i * 5 + 1] for i in range(NSRC)] == [2, 1, 0, 0, 4]
    and sum([F['tone_wrap_gain'][i * 5 + k] for i in range(NSRC) for k in (0, 2, 3, 4)]) == 0) else 0
CLOSE[u'tone_shell_never_grows'] = 1 if (sum(F['tone_sh_gain']) == 0
                                         and sum([x for x in F['tone_tag_gain'] if x > 0]) == 0) else 0
CLOSE[u'number_tags_inflate_tone'] = 1 if (F['tone_drop_tag'][1] == [61, 0, 0, 0, 18]
                                           and sum(F['tone_drop_tot'][i] for i in range(NSRC) if i != 1) == 0
                                           and F['tone_drop_tag'][1][0] == F['tag_paren_kind'][1][0]
                                           and F['tone_drop_tag'][1][4] == F['tag_paren_kind'][1][4]
                                           and sum(F['tone_drop_ledger']) == 0) else 0
CLOSE[u'tag_9293_only'] = 1 if (F['tag_sh'][1] == 237 and sum(F['tag_sh'][i] for i in range(NSRC) if i != 1) == 0
                                and F['tag_paren'][1] == 108 and F['tag_bare'][1] == 126
                                and F['tag_decl'][1] == 1 and sum(F['tag_decl'][i] for i in range(NSRC) if i != 1) == 0) else 0
CLOSE[u'tag_paren_four_shapes'] = 1 if (F['tag_paren'][1] == 108 and F['tag_paren_prose'][1] == 1
                                       and F['tag_paren_bracket'][1] == 2 and F['tag_bare'][1] == 126
                                       and F['tag_paren_period'][1] == 81 and F['tag_paren_comma'][1] == 14
                                       and F['tag_paren_mid'][1] == 13
                                       and sum(F['tag_paren_place_close']) == 0
                                       and sum(F['tag_form_ledger']) == 0
                                       and sum(F['tag_paren_kind_close']) == 0
                                       and sum(F['tag_paren_prose'] + F['tag_paren_bracket']) == 3) else 0
CLOSE[u'role_shell_gain_zero'] = 1 if (sum(F['role_gain_sh']) == 0 and F['role_shell_n'] == [0] * NSRC) else 0
CLOSE[u'role_tag_gain_one'] = 1 if (sum(F['role_gain_tag']) == len(F['role_tagcut_keys']) == 1) else 0
CLOSE[u'role_wrap_six'] = 1 if (sum(F['role_wrap_n']) == F['role_line_miss_n']
                                and sum(F['role_wrap_n']) >= 6) else 0
CLOSE[u'no_digital_two_hours'] = 1 if (F['num_digit_two_tot'] == 0 and F['digit_form_two_hours'] == [0] * NSRC
                                      and F['num_word_two'] == [1, 1, 0, 0, 0]
                                      and F['num_longform_two'] == [0, 1, 0, 0, 0]) else 0
CLOSE[u'digits_only_in_tcp_quic'] = 1 if (F['numval_n'][2] == 0 and F['numval_n'][3] == 1
                                             and F['numval_n'][4] == 5 and F['numval_n'][0] == 5) else 0
CLOSE[u'ans_same_after_tag'] = 1 if (F['ans_pair_same'] == 1 and F['ans_tagdiff'] > 0
                                     and F['ans_tag_n_in_sent'][1] == 2) else 0
CLOSE[u'ans_char_diff_is_tags'] = 1 if (F['ans_tag_len_ledger'] == 0 and F['ans_tag_len'] == 20
                                        and F['ans_tag_len'] == F['ans_tagdiff']) else 0
CLOSE[u'ans_no_shell_no_na'] = 1 if (sum(F['ans_shell_rows']) == 0 and sum(F['ans_na']) == 0) else 0
CLOSE[u'ovl_three_rulers_monotone'] = 1 if (F['ovl_monotone'] == 2 and F['ovl_same_raw'] < F['ovl_same_tag']
                                            and F['ovl_same_canon'] == 5 and F['ovl_same_ledger'] == 0) else 0
CLOSE[u'disc_promoted_sentence'] = 1 if F['ovl_disc_promoted'] >= 1 else 0
CLOSE[u'kw_absent_in_1122'] = 1 if (F['kw_docs'] == 4 and F['kw_at'][0] == -1) else 0
CLOSE[u'kw_two_citations'] = 1 if (F['kw_cite_bcp'][1] == 1 and sum(F['kw_cite_bcp'][i] for i in range(NSRC) if i != 1) == 0
                                  and sum(F['kw_cite_pair'][i] for i in NEW if i != 1) == 3) else 0
CLOSE[u'leader_only_old_toc'] = 1 if (F['head_toc_leader_strict'] == [1, 0, 0, 0, 0]
                                      and F['head_toc_leader_spaced'] == [1, 0, 0, 0, 0]) else 0
CLOSE[u'answer_inside_own_section'] = 1 if (F['sec_ans_inside'] == [1] * NSRC
                                            and min(F['sec_ans_gap']) >= 5
                                            and F['sec_body_line'] == [5937, 2029, 1463, 3130, 3098]) else 0
CLOSE[u'every_window_has_obligation'] = 1 if (F['sec_tone_only_n'] == NSRC and F['sec_tone_zero_n'] == 0
                                              and F['sec_tone_tot'][4] == 2
                                              and F['sec_shell_tot'] == sum(F['sec_shell_rows']) > 0) else 0
CLOSE[u'old_toc_indent_body'] = 1 if (F['sec_body_indent'] == [9, 0, 0, 0, 0]
                                      and min(F['sec_toc_indent']) >= 5
                                      and F['sec_print_n'] == [2, 2, 2, 2, 2]) else 0
CLOSE[u'citation_one_way'] = 1 if (F['cite_matrix'][1][0] >= 1 and F['cite_matrix'][0][1] == 0
                                   and F['cite_matrix'][0][2] == 0) else 0
CLOSE[u'hex_new_format_only'] = 1 if (F['hexes'][0] == 0 and F['hexes'][4] == 218 and F['par_under'][0] == 0) else 0
CLOSE[u'neg_all_cold'] = 1 if (F['neg_zero_hits'] == 0 and F['neg_owner_present'] == F['neg_n']) else 0
CLOSE[u'substring_ruler_overreads'] = 1 if (F['neg_sub_false'] == 177 and len(F['neg_sub_false_rows']) == 13
                                            and F['neg_word'][0][9] == 0 and F['neg_sub'][0][9] == 2
                                            and F['neg_sub_false'] < F['neg_sub_ruler']) else 0
CLOSE[u'pick_all_agree'] = 1 if (F['pick_diff'] == 0 and F['pick_agree'] == F['pick_same_n']) else 0
F['bool_clos_n'] = len(CLOSE)
F['bool_clos_sum'] = sum(CLOSE.values())
assert F['bool_clos_sum'] == F['bool_clos_n'], [k for k in CLOSE if CLOSE[k] == 0]

# ---------- 恒等式(ZID: 全归零才算平) ----------
ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"sum([abs(x) for x in F['row_form_ledger']])", u'换行档差 = FF后随换行 − 尾换行, 逐份相消')
Z(u"sum(F['shell_ledger'])", u'壳行 = 空行 + 页脚 + 眉行(旧式), 新式只剩空行')
Z(u"sum(F['na_ledger'])", u'非 ASCII = BOM + 其余, 逐份相加=总数')
Z(u"sum(F['na_before_ref'])", u'非 ASCII 行全落在 References 正文标题之后')
Z(u"sum(F['na_place_ledger'])", u'非 ASCII 行分作参考条目/贡献者条目/其余, 三档相加=行数')
Z(u"sum(F['ref_ledger'])", u'References 标题的印刷次数 = 目录枚 + 正文枚')
Z(u"sum(F['na_bom_line']) - F['bom_survives']", u'只带 BOM 的行数 = 摘壳后仍存活的 BOM 枚数')
Z(u"sum(F['pgnum_overstrip']) - (sum(F['pgnum']) - sum(F['pgnum_shell']))", u'naive 页码尺多吃额账平')
Z(u"sum(F['spell_ruler_gap']) - (sum(F['spell_tot']) - sum([sum(x) for x in F['spell_word']]))",
  u'子串尺比整词尺多读的枚数 = 两尺总差')
Z(u"sum(F['ack_major']) + sum(F['ack_minor']) - sum([F['spell'][i][9] + F['spell'][i][10] for i in range(5)])",
  u'两种拼法相加 = 族量合计')
Z(u"sum([F['tone_wrap_gain'][i * 5 + k] for i in range(5) for k in range(5) if k != 1])",
  u'折平只让 MUST NOT 涨, 其余四式增量为零')
Z(u"sum(F['tone_sh_gain'])", u'摘壳在义务词上一档也不涨')
Z(u"sum([x for x in F['tone_tag_gain'] if x > 0])", u'去编号只会让义务词变少, 从不新增')
Z(u"sum(F['tone_drop_ledger'])", u'去编号跌落的义务词枚数逐份账平')
Z(u"sum(F['tag_form_ledger'])", u'括注形 + 裸形 + 无空格括注形 = 编号总数')
Z(u"sum(F['tag_paren_place_close'])", u'句点后 + 逗号后 + 句中 = 括注编号总数')
Z(u"sum(F['tone_must_ledger'])", u'大写 MUST = MUST NOT + 裸 MUST 逐份账平')
Z(u"sum(F['tag_kind_close'])", u'编号按类分档相加 = 编号总数')
Z(u"sum(F['role_gain_sh'])", u'摘壳在判词针上一枚也不新增(与上一代条目的壳涨相反)')
Z(u"sum(F['role_gain_tag']) - len(F['role_tagcut_keys'])", u'去编号档的增益枚数 = 编号切开针清单长度')
Z(u"F['role_line_miss_n'] - sum(F['role_wrap_n'])", u'逐行漏读的针全由硬换行切开(无壳切, 无编号切)')
Z(u"sum(F['num_lit_close'])", u'数值命名列相加 = 去重数值枚数')
Z(u"F['ans_chars'][1] - F['ans_chars'][0] - F['ans_tag_len']",
  u'两份答句的字符差 = 两枚编号标注吃掉的长度(各带一枚前空格)')
Z(u"F['sec_shell_tot'] - sum(F['sec_shell_rows'])", u'五个节窗里的壳行合计 = 逐份相加')
Z(u"sum(F['sec_ans_inside']) - 5", u'五句答案都落在自己那一节的窗内')
Z(u"sum(F['ans_shell_rows'])", u'五句答案里没有一行页壳')
Z(u"sum(F['ans_na'])", u'五句答案全是 ASCII')
Z(u"F['ovl_same_ledger']", u'块内句数 = 逐字相同 + 新句')
Z(u"F['ovl_tag_only'] - (F['ovl_same_canon'] - F['ovl_same_raw']) + F['ovl_same_canon'] - F['ovl_same_tag']",
  u'只差编号的句子在三种尺之间相消')
Z(u"sum([abs(x) for x in F['sec_ans_gap']]) - sum([x for x in F['sec_ans_gap'] if x >= 0]) + sum([x for x in F['sec_ans_gap'] if x < 0])",
  u'答句行距的正负两段相加 = 绝对值之和')
Z(u"F['kw_docs'] - len([x for x in F['kw_at'] if x >= 0])", u'关键词段存在的份数 = 非 −1 的读数')
Z(u"F['pin_line_close']", u'答句首行与采集遍定位的同一行')
Z(u"F['neg_zero_hits']", u'反向对照针在被排除的份上全冷')
Z(u"F['neg_sub_ruler'] - F['neg_sub_false'] - sum([x[3] for x in F['neg_sub_false_rows']])",
  u'子串尺的读数 = 整词尺读数 + 多读枚数(逐行账平)')
Z(u"sum(F['tag_form_ledger'])", u'四种编号形态相加 = 摘壳档的编号总数')
Z(u"F['pick_diff']", u'与采集遍对账不符数为零')
Z(u"F['bool_clos_sum'] - F['bool_clos_n']", u'布尔门全绿')

# --- SCAN END --- (以上由 _wire82.py 机械切进 audit.py::_b82_scan)

BB82 = lambda name, i=None: (F[name] if i is None else F[name][i])


def _ev(e):
    return eval(e, {u'B82V': BB82, u'NSRC': NSRC, u'range': range, u'F': F, u'CLOSE': CLOSE})


FN = u'B82V'
_to_v = re.compile(r"(?:F|CLOSE)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B82V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(5)').replace(u'NSRC', u'5')


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
    return


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
    if eval(v, {FN: BB82}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))
    reg(str(_ev(e)), v, w)


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB82}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([str(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


for k, v in dump_deriv().items():
    DER[k] = v
io.open(u'corpus/_b82flat.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True))

print(u'第二遍量测完成: 扁平键 %d ｜ 恒等式 %d 全平 ⇎ 布尔门 %d 全绿 ｜ 针 %d(反向 %d) ｜ 对账 %d 符 %d 不符'
      % (len(F), len(ZID), F['bool_clos_n'], F['needle_n'], F['neg_n'], F['pick_agree'], F['pick_diff']))
print(u'壳行 %s ⇎ 页脚 %s ⇎ 眉行 %s ⇎ BOM %s ⇎ 非ASCII %s' % (F['shell_lines'], F['foot'], F['hdr_old'],
      F['bom'], F['na_total']))
print(u'答句词数 %s ⇎ 跨行 %s ⇎ 首行 %s ⇎ 编号 %s ⇎ 去编号后同句 %s' % (F['ans_words'], F['ans_sent_span'],
      F['ans_anchor_line'], F['ans_tag_n_in_sent'], F['ans_pair_same']))
print(u'判词针四档合计 %s/%s/%s/%s ⇎ 切开 %s ⇎ 壳切 %s ⇎ 编号切 %s' % (F['role_line_n'], F['role_fold_n'],
      F['role_sh_n'], F['role_tag_n'], F['role_wrap_n'], F['role_shell_n'], F['role_tagcut_n']))
print(u'节窗 %s 行 ⇎ 字符 %s ⇎ 目录行 %s ⇎ 引道符 %s/%s ⇎ 节内义务词 %s' % (F['sec_lines'], F['sec_chars'],
      F['sec_toc_line'], F['head_toc_leader_strict'], F['head_toc_leader_spaced'], F['sec_tone_tot']))
print(u'逐句对照 %s 句 ⇎ 逐字同 %s ⇎ 去编号同 %s ⇎ 归拼同 %s ⇎ 新句 %s ⇎ 讨论升格 %s' % (
      (F['ovl_s1'], F['ovl_s2']), F['ovl_same_raw'], F['ovl_same_tag'], F['ovl_same_canon'],
      F['ovl_new'], F['ovl_disc_promoted']))

exec(io.open(u'corpus/_mk82emit.py', encoding='utf-8').read())
