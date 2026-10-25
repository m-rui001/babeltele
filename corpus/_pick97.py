# -*- coding: utf-8 -*-
"""采集遍(B97, 第一套实现): "IPv6 默认前缀策略表到底有哪几行、各行动作是什么"
七份一手文书各序列化一遍 ——
6724(2012 现行: §2.1 图 9 行三列 ⇎ 全文 6 张表 59 行 ⇎ §5 两条算法的 Rule 头里有一枚 Rule 5.5) ⇎
3484(2003 被替代: §2.1 图 5 行 ⇎ 同两列名 ⇎ ::ffff:0:0/96 的 precedence 由 35 落回 10) ⇎
7381(BCP 177 IPv6 部署建议: 只引 6724 ⇎ 表体行 0 枚) ⇎
8407(题面点名的候选源: 实为 BCP 216 YANG 作者指南 ⇎ 6724 提及 0 枚 ⇎ 表体行 0 枚 —— 负对照) ⇎
gai(发行版配置文档 gai.conf(5): RFC 3484 那张表被拆成 label 5 行 + precedence 5 行两份配置 ⇎
     glibc 自家常用标签表另 8 行 ⇎ 通篇只引 3484 不引 6724) ⇎
lbl(内核 net/ipv6/addrlabel.c: 注释表 10 行(RFC6724 + extensions) ⇎ 同一张表又以 C 结构体数组 10 条再写一遍
    ⇎ 两份顺序相反 ⇎ 只落 label 半张表, precedence 列 0 枚) ⇎
adr(内核 net/ipv6/addrconf.c: 表 0 行 ⇎ 算法侧把 §5 的规则注释成 Rule 0..8 再加一枚 Rule 8- ⇎
    抬头仍写 (RFC3484))。

本遍机制(与建条目侧 _mkB97.py 九处不同, 只换实现不换定义):
①行式: 本遍 split('\\n') ⇎ 建条侧 splitlines();
②字面针: 本遍游标 find 环(逐枚非重叠) ⇎ 建条侧 re.findall(re.escape) 整串扫描;
③行形谓词: 本遍逐 token 字符扫(首 token 是否含冒号 ⇎ 其后 token 是否全数字) ⇎ 建条侧一条整串正则 fullmatch;
④块定界: 本遍现写节号标题识别器取 §2.1 那块 ⇎ 建条侧用针偏移经累积长度表 + bisect 开窗;
⑤前缀代数: 本遍集合档(set 差交) ⇎ 建条侧词频档(Counter 直方图);
⑥数值抽取: 本遍手工逐字符判数字 ⇎ 建条侧正则取段;
⑦折平: 本遍 ' '.join(s.split()) ⇎ 建条侧逐字符抄词自建词表;
⑧义务词形状: 本遍两条正则级联(大写族 ⇎ 后接 NOT) ⇎ 建条侧 token 枚举判形状;
⑨剥壳: 本遍对整行跑序列正则 ⇎ 建条侧 strip 后按 token 形状判; 另本遍剥 HTML 走 '<' 游标分段 ⇎ 建条侧三条正则一次替换。
所有正文数字由本遍量出后落 corpus/_b97meas.json, 一枚都不手打; 锚一律由面上位置导出。"""
import io, json, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'6724', u'3484', u'7381', u'8407', u'gai', u'lbl', u'adr']
NSRC = 7
PATH = [u'corpus/raw/prefixtable97/rfc6724.txt', u'corpus/raw/prefixtable97/rfc3484.txt',
        u'corpus/raw/prefixtable97/rfc7381.txt', u'corpus/raw/prefixtable97/rfc8407.txt',
        u'corpus/raw/prefixtable97/gai_conf5.html', u'corpus/raw/prefixtable97/addrlabel.c',
        u'corpus/raw/prefixtable97/addrconf.c']
IDS = [u'rfc6724.txt', u'rfc3484.txt', u'rfc7381.txt', u'rfc8407.txt',
       u'gai_conf5.html', u'addrlabel.c', u'addrconf.c']
ISHTML = [False, False, False, False, True, False, False]
FAM = [u'cur', u'old', u'dep', u'mis', u'cfg', u'kern', u'kern']
M = {}


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', u'replace') for b in B]
# 机制①: split('\n') 行式(建条侧是 splitlines())
RAWL = [t.split(NL) for t in T]


def detag_cursor(s):
    """剥 HTML 壳: '<' 起 '>' 止整段丢弃并补一枚空格, 再就地换五枚实体, 全程不跑正则。"""
    out, k, n = [], 0, len(s)
    while k < n:
        c = s[k]
        if c == u'<':
            j = k + 1
            while j < n and s[j] != u'>':
                j += 1
            out.append(u' ')
            k = j + 1
        else:
            out.append(c)
            k += 1
    t = u''.join(out)
    for a, b in [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'),
                 (u'&quot;', u'"')]:
        t = t.replace(a, b)
    return t


FACE = [detag_cursor(t) if ISHTML[i] else t for i, t in enumerate(T)]
FL = [f.split(NL) for f in FACE]


def fold(s):
    """机制⑦: 折平走 ' '.join(split()), 逐词而非逐字符。"""
    return u' '.join(s.split())


FOLD = [fold(f) for f in FACE]


def pnorm(s):
    return u' '.join(s.lower().split())


FPF = [pnorm(x) for x in FOLD]

# ---------------- 壳谓词: 机制⑨ 整行序列正则 ----------------
RX_FOOT = re.compile(u'^\\s*[A-Za-z][A-Za-z., ]*\\sStandards Track\\s+\\[Page \\d+\\]\\s*$')
RX_HDR = re.compile(u'^RFC \\d+\\s+\\S')
RX_IETF = re.compile(u'^Internet Engineering Task Force')
RX_PGONLY = re.compile(u'^\\s*\\d+\\s*$')
RX_FF = re.compile(u'^\\s*\\x0c\\s*$')
RX_CMT = re.compile(u'^\\s*\\*')
RX_TAGLINE = re.compile(u'^\\s*</?[a-zA-Z!][^>]*>\\s*$')
SHELLP = [RX_FOOT, RX_HDR, RX_IETF, RX_PGONLY, RX_FF, RX_CMT, RX_TAGLINE]


def is_shell(line):
    s = line.strip()
    if s == u'' or s == u'\x0c':
        return True
    return any(p.match(line) for p in SHELLP)


SHELL = [[is_shell(l) for l in FL[i]] for i in range(NSRC)]
SHF = [fold(u' '.join(u' %s ' % l for k, l in enumerate(FL[i]) if not SHELL[i][k]))
       for i in range(NSRC)]
SHP = [pnorm(x) for x in SHF]
M[u'bytes'] = [os.path.getsize(p) for p in PATH]
M[u'chars'] = [len(t) for t in T]
M[u'face_chars'] = [len(f) for f in FACE]
M[u'lf'] = [t.count(u'\n') for t in T]
M[u'cr'] = [t.count(u'\r') for t in T]
M[u'ff'] = [t.count(u'\x0c') for t in T]
M[u'tab'] = [t.count(u'\t') for t in T]
M[u'nonascii'] = [sum(1 for c in t if ord(c) > 127) for t in T]
M[u'bom'] = [1 if b[:3] == b'\xef\xbb\xbf' else 0 for b in B]
M[u'lines_nl'] = [len(x) for x in FL]
M[u'lines_sl'] = [len(f.splitlines()) for f in FACE]
M[u'blank'] = [sum(1 for l in FL[i] if l.strip() == u'') for i in range(NSRC)]
M[u'shell_lines'] = [sum(1 for x in SHELL[i] if x) for i in range(NSRC)]
M[u'body_lines'] = [M[u'lines_nl'][i] - M[u'shell_lines'][i] for i in range(NSRC)]
M[u'maxlen'] = [max(len(l) for l in FL[i]) for i in range(NSRC)]
M[u'trailing_nl'] = [1 if t.endswith(u'\n') else 0 for t in T]
M[u'utf8_extra'] = [M[u'bytes'][i] - M[u'chars'][i] for i in range(NSRC)]
M[u'foot_page'] = [len([l for l in FL[i] if RX_FOOT.match(l)]) for i in range(NSRC)]
M[u'hdr_rfc'] = [len([l for l in FL[i] if RX_HDR.match(l)]) for i in range(NSRC)]
M[u'ietf_alone'] = [len([l for l in FL[i] if RX_IETF.match(l)]) for i in range(NSRC)]
M[u'cmt_lead'] = [len([l for l in FL[i] if RX_CMT.match(l)]) for i in range(NSRC)]
M[u'pgonly'] = [len([l for l in FL[i] if RX_PGONLY.match(l)]) for i in range(NSRC)]
M[u'tagcount'] = [len(re.findall(u'<[^>]+>', T[i])) if ISHTML[i] else 0 for i in range(NSRC)]

# ---------------- 行形谓词: 机制③ 逐 token 字符扫 ⇎ 机制⑥ 手工读数字 ----------------
HEX = u'0123456789abcdefABCDEF:'


def tok_is_prefix(tok):
    if u':' not in tok:
        return False
    k = 0
    n = len(tok)
    while k < n and tok[k] in HEX:
        k += 1
    if k == 0:
        return False
    if k == n:
        return True
    if tok[k] != u'/':
        return False
    k += 1
    if k >= n:
        return False
    while k < n:
        if tok[k] < u'0' or tok[k] > u'9':
            return False
        k += 1
    return True


def tok_is_num(tok):
    k, n = 0, len(tok)
    if n == 0:
        return False
    while k < n:
        if tok[k] < u'0' or tok[k] > u'9':
            return False
        k += 1
    return True


def tok_is_atype(tok):
    """内核注释表第二列 = 地址类型: 含字母、不含冒号、字符仅取自字母数字与 '/'
    (LOOPBACK ⇎ N/A ⇎ COMPATv4 ⇎ V4MAPPED)。"""
    k, n, alpha = 0, len(tok), 0
    if n == 0 or u':' in tok:
        return False
    while k < n:
        c = tok[k]
        if u'A' <= c <= u'Z' or u'a' <= c <= u'z':
            alpha += 1
        elif not (u'0' <= c <= u'9' or c == u'/'):
            return False
        k += 1
    return alpha > 0


def row_shape3(line):
    t = line.strip().split()
    if len(t) != 3 or not tok_is_prefix(t[0]):
        return None
    if not (tok_is_num(t[1]) and tok_is_num(t[2])):
        return None
    return t


def row_shape_kw(line):
    t = line.strip().split()
    if len(t) != 3 or t[0] not in (u'label', u'precedence'):
        return None
    if not (tok_is_prefix(t[1]) and tok_is_num(t[2])):
        return None
    return [t[1], t[2], t[0]]


def row_shape_cmt(line, note):
    """内核注释表两档: note=False 只认严格三列(表体行), note=True 容行末第四段自由注
    (ULA (RFC 4193) ⇎ Site-local ⇎ 6bone) —— 表体行 ⇎ 含注释行 两档口径并立。"""
    s = line.strip()
    if not s.startswith(u'*'):
        return None
    s = s[1:].strip()
    t = s.split()
    if len(t) < 3 or (not note and len(t) != 3):
        return None
    if not tok_is_prefix(t[0]):
        return None
    if not (tok_is_atype(t[1]) and tok_is_num(t[2])):
        return None
    return t


def row_shape_cmt3(line):
    return row_shape_cmt(line, False)


def row_shape_cmtn(line):
    return row_shape_cmt(line, True)


def row_shape_wide(line):
    """宽档: 剥 '*' 引导后 ⇎ 行内任一枚前缀样 token ⇎ 行尾是一枚纯数字。"""
    s = line.strip()
    while s.startswith(u'*'):
        s = s[1:].strip()
    t = s.split()
    if len(t) < 2:
        return None
    if not any(tok_is_prefix(x) for x in t):
        return None
    if not tok_is_num(t[-1]):
        return None
    return [x for x in t if tok_is_prefix(x)][0:1] + t[1:]


def row_shape_pfxany(line):
    """最宽档(用于"某文书没有这一行"的断言): 剥 '*' 引导后行内任一枚前缀样 token,
    不要求行尾是数字。"""
    s = line.strip()
    while s.startswith(u'*'):
        s = s[1:].strip()
    t = s.split()
    if len(t) < 2:
        return None
    for x in t:
        if tok_is_prefix(x):
            return [x]
    return None


def shape_lines(fn):
    return [[k + 1 for k, l in enumerate(FL[i]) if fn(l)] for i in range(NSRC)]


R3 = shape_lines(row_shape3)
RKW = shape_lines(row_shape_kw)
RCM3 = shape_lines(row_shape_cmt3)
RCMN = shape_lines(row_shape_cmtn)
RWIDE = shape_lines(row_shape_wide)
RANY = shape_lines(row_shape_pfxany)
RCINIT = [[k + 1 for k, l in enumerate(FL[i]) if u'.label = ' in l] for i in range(NSRC)]
M[u'row3'] = [len(x) for x in R3]
M[u'rowkw'] = [len(x) for x in RKW]
M[u'rowcmt3'] = [len(x) for x in RCM3]
M[u'rowcmtn'] = [len(x) for x in RCMN]
M[u'rowcmt'] = M[u'rowcmtn']
M[u'rowwide'] = [len(x) for x in RWIDE]
M[u'rowany'] = [len(x) for x in RANY]
M[u'rowcinit'] = [len(x) for x in RCINIT]

# ---------------- 块定界: 机制④ 节号标题识别器 ----------------
RX_SECHDR = re.compile(u'^(\\d+(?:\\.\\d+){0,2})\\.?\\s+\\S')


def sec_of(lines, want):
    hits = []
    for k, l in enumerate(lines):
        m = RX_SECHDR.match(l)
        if m:
            hits.append((k + 1, m.group(1)))
    for pos, (ln, num) in enumerate(hits):
        if num == want:
            lvl = num.count(u'.')
            end = len(lines)
            for ln2, num2 in hits[pos + 1:]:
                if num2.count(u'.') <= lvl:
                    end = ln2 - 1
                    break
            return ln, end
    return None


SEC21 = [sec_of(FL[i], u'2.1') for i in range(NSRC)]
M[u'sec21_present'] = [1 if x else 0 for x in SEC21]
M[u'sec21_lines'] = [(x[1] - x[0] + 1) if x else 0 for x in SEC21]
M[u'sec21_at'] = [[x[0], x[1]] if x else [-1, -1] for x in SEC21]


def insec(i, ln):
    return 1 if (SEC21[i] and SEC21[i][0] <= ln <= SEC21[i][1]) else 0


M[u'fig_rows'] = [sum(insec(i, ln) for ln in R3[i]) for i in range(NSRC)]
M[u'fig_kw'] = [sum(insec(i, ln) for ln in RKW[i]) for i in range(NSRC)]
M[u'hdr_col_lines'] = [len([l for l in FL[i] if l.strip() == u'Prefix        Precedence Label'])
                       for i in range(NSRC)]
M[u'hdr_col_any'] = [len([l for l in FL[i] if pnorm(fold(l)) == u'prefix precedence label'])
                     for i in range(NSRC)]
M[u'hdr_col_words'] = [len([l for l in FL[i] if l.strip().startswith(u'Prefix')
                            and u'Precedence' in l]) for i in range(NSRC)]

# 内核注释表所在块: 由 '/*' ⇎ '*/' 定界的注释框
def cmt_block(lines, title):
    a = b = -1
    for k, l in enumerate(lines):
        if title in l:
            a = k
            break
    if a < 0:
        return a, b
    j = a
    while j < len(lines) and not lines[j].strip().endswith(u'*/'):
        j += 1
    return a + 1, j


CB = cmt_block(FL[5], u'Default policy table (RFC6724 + extensions)')
M[u'cmtblock'] = [CB[0] + 1, CB[1] + 1] if CB[0] >= 0 else [-1, -1]
M[u'cmtblock_lines'] = (CB[1] - CB[0] + 1) if CB[0] >= 0 else 0
M[u'cmtblock_rows3'] = len([ln for ln in RCM3[5] if CB[0] < ln - 1 <= CB[1]])
M[u'cmtblock_rowsn'] = len([ln for ln in RCMN[5] if CB[0] < ln - 1 <= CB[1]])
M[u'cmtblock_blank'] = len([ln for ln in range(CB[0] + 1, CB[1] + 2) if FL[5][ln - 1].strip() == u''])
M[u'cmtblock_note'] = len([ln for ln in range(CB[0] + 1, CB[1] + 2)
                           if FL[5][ln - 1].strip().startswith(u'*')
                           and not row_shape_cmtn(FL[5][ln - 1])
                           and FL[5][ln - 1].strip() not in (u'/*', u'*/', u'*')])
M[u'fig_cmt'] = [M[u'cmtblock_rowsn'] if i == 5 else 0 for i in range(NSRC)]

# ---------------- 前缀代数: 机制⑤ 集合档 ----------------
def rownorm(fn, line):
    t = fn(line)
    return t


PFX = []
for i in range(NSRC):
    s = set()
    for ln in R3[i] + RKW[i] + RCMN[i]:
        t = (row_shape3(FL[i][ln - 1]) or row_shape_kw(FL[i][ln - 1])
             or row_shape_cmtn(FL[i][ln - 1]))
        if t:
            s.add(t[0])
    PFX.append(s)
M[u'pfx_distinct'] = [len(s) for s in PFX]
ALLS = set().union(*PFX)
M[u'pfx_union'] = len(ALLS)
M[u'pfx_hist'] = [len([p for p in ALLS if sum(1 for i in range(NSRC) if p in PFX[i]) == h])
                  for h in range(1, NSRC + 1)]
M[u'pfx_only'] = [len([p for p in PFX[i] if sum(1 for j in range(NSRC) if p in PFX[j]) == 1])
                  for i in range(NSRC)]
M[u'pfx_only_list'] = [sorted([p for p in PFX[i] if sum(1 for j in range(NSRC) if p in PFX[j]) == 1])
                       for i in range(NSRC)]
M[u'pfx_pairsum'] = [len(PFX[i] & PFX[j]) for i in range(NSRC) for j in range(NSRC) if i <= j]
M[u'pfx_pairs'] = [[i, j, len(PFX[i] & PFX[j])] for i in range(NSRC) for j in range(NSRC) if i < j]

LAB, PREC = [], []
for i in range(NSRC):
    dl, dp = {}, {}
    for ln in R3[i]:
        p, a, b = row_shape3(FL[i][ln - 1])
        dl.setdefault(p, b)
        dp.setdefault(p, a)
    for ln in RKW[i]:
        p, v, kw = row_shape_kw(FL[i][ln - 1])
        (dl if kw == u'label' else dp).setdefault(p, v)
    for ln in RCMN[i]:
        p, w, v = row_shape_cmtn(FL[i][ln - 1])[:3]
        dl.setdefault(p, v)
    LAB.append(dl)
    PREC.append(dp)
PANY = []
for i in range(NSRC):
    s = set()
    for ln in RANY[i]:
        s.add(row_shape_pfxany(FL[i][ln - 1])[0])
    PANY.append(s)
M[u'pfx_any_union'] = len(set().union(*PANY)) if PANY else 0
M[u'pfx_any_n'] = [len(s) for s in PANY]
M[u'pfx_any_rows'] = [len(x) for x in RANY]
UN = sorted(set().union(*[set(x) for x in LAB] + [set(x) for x in PREC]))
M[u'col_prefix_union'] = len(UN)
M[u'col_label_hit'] = [len(LAB[i]) for i in range(NSRC)]
M[u'col_prec_hit'] = [len(PREC[i]) for i in range(NSRC)]


def confl(tables):
    out = []
    for p in UN:
        vals = sorted({d[p] for d in tables if p in d})
        if len(vals) > 1:
            out.append([p, vals])
    return out


CONFL, CONFP = confl(LAB), confl(PREC)
M[u'label_conflict_n'] = len(CONFL)
M[u'label_conflict'] = CONFL
M[u'prec_conflict_n'] = len(CONFP)
M[u'prec_conflict'] = CONFP


def diffpair(tables, a, b):
    out = []
    for d in tables:
        x, y = d.get(a), d.get(b)
        out.append(int(x) - int(y) if x is not None and y is not None else 0)
    return out


M[u'flip_v6mapped'] = diffpair(PREC, u'::ffff:0:0/96', u'::/96')
M[u'flip_ula'] = diffpair(LAB, u'fc00::/7', u'fec0::/10')
M[u'prec_vals_union'] = sorted({v for d in PREC for v in d.values()}, key=lambda x: int(x))
M[u'label_vals_union'] = sorted({v for d in LAB for v in d.values()}, key=lambda x: int(x))
M[u'prec_val_n'] = len(M[u'prec_vals_union'])
M[u'label_val_n'] = len(M[u'label_vals_union'])

# ---------------- 算法规则的序列化: Rule 头(机制② 游标 find 环) ----------------
def rule_heads(s):
    out, k = [], 0
    key = u'Rule '
    while True:
        j = s.find(key, k)
        if j < 0:
            break
        m = j + len(key)
        buf = u''
        while m < len(s) and (s[m].isdigit() or s[m] in u'.+-'):
            buf += s[m]
            m += 1
        if buf and s[m:m + 1] == u':':
            out.append(buf)
        k = j + 1
    return out


RH = [rule_heads(FOLD[i]) for i in range(NSRC)]
M[u'rule_heads'] = [len(x) for x in RH]
M[u'rule_uniq'] = [len(set(x)) for x in RH]
M[u'rule_frac'] = [len([x for x in RH[i] if u'.' in x]) for i in range(NSRC)]
M[u'rule_sign'] = [len([x for x in RH[i] if u'-' in x or u'+' in x]) for i in range(NSRC)]
M[u'rule_55'] = [len([x for x in RH[i] if x == u'5.5']) for i in range(NSRC)]
M[u'rule_list'] = [sorted(set(x)) for x in RH]
M[u'rule_max_num'] = [max([int(x.split(u'.')[0].rstrip(u'-+')) for x in RH[i]] or [-1])
                      for i in range(NSRC)]
M[u'enum_saddr'] = [len(re.findall(u'IPV6_SADDR_RULE_[A-Z0-9]+', FOLD[i])) for i in range(NSRC)]
M[u'enum_uniq'] = [len(set(re.findall(u'IPV6_SADDR_RULE_[A-Z0-9]+', FOLD[i]))) for i in range(NSRC)]
M[u'ifdef'] = [len(re.findall(u'#ifdef CONFIG_IPV6', FOLD[i])) for i in range(NSRC)]

# ---------------- 引用针(拼写分档) ----------------
CIT = [u'RFC 6724', u'RFC6724', u'RFC 3484', u'RFC3484', u'RFC 4193', u'RFC 4380',
       u'RFC 4843', u'RFC 6555', u'RFC 6724 + extensions', u'BCP 177', u'BCP 216', u'YANG']
M[u'cite'] = [[FOLD[i].count(c) for c in CIT] for i in range(NSRC)]
M[u'cite_keys'] = CIT

# ---------------- 义务词形状: 机制⑧ 两条正则级联 ----------------
OBL = [u'MUST', u'SHOULD', u'MAY']
ob_u, ob_n, ob_l = [], [], []
for i in range(NSRC):
    s = FOLD[i]
    ob_u.append([len(re.findall(u'(?<![A-Za-z0-9])%s(?![A-Za-z0-9])' % w, s)) for w in OBL])
    ob_n.append([len(re.findall(u'(?<![A-Za-z0-9])%s NOT(?![A-Za-z0-9])' % w, s)) for w in OBL])
    ob_l.append([len(re.findall(u'(?<![A-Za-z0-9])%s(?![A-Za-z0-9])' % w.lower(), s)) for w in OBL])
M[u'oblig_upper'] = ob_u
M[u'oblig_not'] = ob_n
M[u'oblig_lower'] = ob_l
M[u'oblig_tot'] = [sum(ob_u[i]) + sum(ob_n[i]) for i in range(NSRC)]

# ---------------- 判词针 ⇎ 三档口径(原行 ⇎ 全篇折平 ⇎ 摘壳折平) ----------------
NEEDLES = [
    u'Default Address Selection for IPv6',
    u'the following default policy table:',
    u'default policy table',
    u'longest-matching-prefix lookup table',
    u'Prefix Precedence Label',
    u'::1/128',
    u'::/0',
    u'::/96',
    u'::ffff:0:0/96',
    u'2002::/16',
    u'2001::/32',
    u'2001:0::/32',
    u'fc00::/7',
    u'fec0::/10',
    u'3ffe::/16',
    u'fe80::/10',
    u'2001:10::/28',
    u'Rule 5.5',
    u'Prefer higher precedence',
    u'Prefer matching label',
    u'Prefer temporary addresses',
    u'Prefer public addresses',
    u'Prefer public address',
    u'Automatic Row Additions',
    u'MUST NOT override',
    u'IPv6 implementations SHOULD support configurable address selection',
    u'Obsoletes: 3484',
    u'obsoletes RFC 3484',
    u'Source Address Selection',
    u'the default table is not used',
    u'Default policy table (RFC6724 + extensions)',
    u'Labels for ULA and 6to4 are different from labels listed in RFC6724',
    u'Choose an appropriate source address (RFC3484)',
    u'N/A',
    u'LOOPBACK',
    u'V4MAPPED',
    u'COMPATv4',
    u'highest success rate',
    u'YANG',
]
NK = len(NEEDLES)


def cnt_cur(s, needle):
    """机制②: 游标 find 环数非重叠命中。"""
    n, k = 0, 0
    while True:
        j = s.find(needle, k)
        if j < 0:
            return n
        n += 1
        k = j + len(needle)


def cnt_row(i, needle):
    """原行档: 逐行计出现次数(非行数) —— 与折平档同为"枚数", 增益才可比。"""
    return sum(l.count(needle) for l in FL[i])


TIER = [[[cnt_cur(FOLD[i], nd), cnt_cur(SHF[i], nd), cnt_row(i, nd)]
         for i in range(NSRC)] for nd in NEEDLES]
M[u'needles3'] = TIER
M[u'needle_list'] = NEEDLES
M[u'needles_row'] = [sum(TIER[k][i][2] for k in range(NK)) for i in range(NSRC)]
M[u'needles_fold'] = [sum(TIER[k][i][0] for k in range(NK)) for i in range(NSRC)]
M[u'needles_noshell'] = [sum(TIER[k][i][1] for k in range(NK)) for i in range(NSRC)]
M[u'needles_gain'] = [M[u'needles_fold'][i] - M[u'needles_row'][i] for i in range(NSRC)]
M[u'needle_zero'] = [[k for k in range(NK) if TIER[k][i][0] == 0] for i in range(NSRC)]
M[u'needle_cold'] = [k for k in range(NK) if sum(TIER[k][i][0] for i in range(NSRC)) == 0]
M[u'needle_all'] = [k for k in range(NK) if all(TIER[k][i][0] > 0 for i in range(NSRC))]
M[u'needle_max'] = [max(TIER[k][i][0] for i in range(NSRC)) for k in range(NK)]

# ---------------- 锚: 由面上位置导出 ----------------
ATOMS = []
for k, nd in enumerate(NEEDLES):
    for i in range(NSRC):
        if TIER[k][i][0] > 0:
            j = FOLD[i].find(nd)
            ATOMS.append([nd, LBL[i], j, TIER[k][i][0]])
M[u'atom_pairs'] = ATOMS
M[u'atom_n'] = len(ATOMS)
M[u'atom_distinct'] = len(set(a[0] for a in ATOMS))

# ---------------- 图框窗口 ⇎ 注释框窗口 ----------------
FIGWIN = [(FL[i][SEC21[i][0] - 1:SEC21[i][1]] if SEC21[i] else []) for i in range(NSRC)]
M[u'figwin_lines'] = [len(x) for x in FIGWIN]
M[u'figwin_shell'] = [sum(1 for l in FIGWIN[i] if is_shell(l)) for i in range(NSRC)]
M[u'figwin_blank'] = [sum(1 for l in FIGWIN[i] if l.strip() == u'') for i in range(NSRC)]
M[u'figwin_chars'] = [sum(len(l) + 1 for l in FIGWIN[i]) for i in range(NSRC)]

# ---------------- 内核 C 数组的"折平后行"(机制: 花括号深度逐字符扫) ----------------
def cinit_fold(s):
    start = s.find(u'ip6addrlbl_init_table[] = {')
    if start < 0:
        return []
    p = s.index(u'{', start + len(u'ip6addrlbl_init_table[] = ')) + 1
    n, d, ent, out = len(s), 1, u'', []
    while p < n:
        c = s[p]
        if c == u'{':
            d += 1
            if d == 2:
                ent = u''
        elif c == u'}':
            d -= 1
            if d == 1:
                if u'.label' in ent:
                    out.append(fold(ent))
                ent = u''
            elif d == 0:
                break
        elif d >= 2:
            ent += c
        p += 1
    return out


CF = cinit_fold(FACE[5])
M[u'cinit_folded'] = len(CF)
M[u'cinit_lines'] = len([l for l in FL[5] if re.match(u'^\\s*\\{\\s*(/\\*|$)', l)])
M[u'cinit_label'] = M[u'rowcinit'][5]
M[u'cinit_comment_rows'] = M[u'rowcmtn'][5]
M[u'cinit_comment_rows3'] = M[u'rowcmt3'][5]


def pref_from_ent(x):
    m = re.search(u'/\\*\\s*(\\S+?)\\s*\\*/', x)
    return m.group(1) if m else u''


M[u'cinit_order'] = [pref_from_ent(x) for x in CF]
M[u'cinit_labels'] = [re.search(u'\\.label = (\\d+)', x).group(1) for x in CF]
M[u'cinit_plens'] = [(int(re.search(u'\\.prefixlen = (\\d+)', x).group(1))
                      if re.search(u'\\.prefixlen = (\\d+)', x) else 0) for x in CF]
M[u'cmt_order'] = [row_shape_cmtn(FL[5][ln - 1])[0] for ln in RCMN[5]]
M[u'cmt_labels'] = [row_shape_cmtn(FL[5][ln - 1])[2] for ln in RCMN[5]]
M[u'order_reverse'] = 1 if M[u'cinit_order'] == list(reversed(M[u'cmt_order'])) else 0
M[u'order_same'] = 1 if M[u'cinit_order'] == M[u'cmt_order'] else 0
M[u'order_common'] = len(set(M[u'cinit_order']) & set(M[u'cmt_order']))
M[u'order_only_c'] = sorted(set(M[u'cinit_order']) - set(M[u'cmt_order']))
M[u'order_only_m'] = sorted(set(M[u'cmt_order']) - set(M[u'cinit_order']))
M[u'label_agree_cells'] = len([p for p in set(M[u'cinit_order']) & set(M[u'cmt_order'])
                              if M[u'cinit_labels'][M[u'cinit_order'].index(p)]
                              == M[u'cmt_labels'][M[u'cmt_order'].index(p)]])

M[u'nsrc'] = NSRC
M[u'lbl'] = LBL
M[u'ids'] = IDS
M[u'path'] = PATH

# ---------------- 列名行的两档口径 ⇎ 关键字行的两列拆分 ----------------
M[u'kw_label'] = [len([ln for ln in RKW[i] if row_shape_kw(FL[i][ln - 1])[2] == u'label'])
                  for i in range(NSRC)]
M[u'kw_prec'] = [len([ln for ln in RKW[i] if row_shape_kw(FL[i][ln - 1])[2] == u'precedence'])
                 for i in range(NSRC)]
M[u'kwdef'] = [[len([l for l in FL[i] if pnorm(fold(l)) == u'label netmask label']),
                len([l for l in FL[i] if pnorm(fold(l)) == u'precedence netmask precedence'])]
               for i in range(NSRC)]
M[u'row3_out21'] = [M[u'row3'][i] - M[u'fig_rows'][i] for i in range(NSRC)]

# ---------------- gai 的两块窗口: 示例块 ⇎ glibc 默认块 ----------------
def win_after(lines, needle, stops, cap=60):
    a = -1
    for k, l in enumerate(lines):
        if needle in l:
            a = k
            break
    if a < 0:
        return -1, -1
    b = min(a + cap, len(lines) - 1)
    for k in range(a + 1, b + 1):
        s = lines[k].strip()
        if any(x in s for x in stops):
            return a + 1, k - 1
    return a + 1, b


STOPS = [u'SEES ALSO', u'SEE ALSO', u'FILES', u'COLOPHON', u'glibc includes some extra rules',
         u'NOTES']
GEX = win_after(FL[4], u'The default table according to RFC 3484', [u'glibc includes some extra rules'])
GDEF = win_after(FL[4], u'Its default label table is:', STOPS)
M[u'gai_exwin'] = [GEX[0] + 1, GEX[1] + 1] if GEX[0] >= 0 else [-1, -1]
M[u'gai_defwin'] = [GDEF[0] + 1, GDEF[1] + 1] if GDEF[0] >= 0 else [-1, -1]
M[u'gai_ex_lines'] = (GEX[1] - GEX[0] + 1) if GEX[0] >= 0 else 0
M[u'gai_def_lines'] = (GDEF[1] - GDEF[0] + 1) if GDEF[0] >= 0 else 0


def inwin(win, ln):
    return 1 if (win[0] >= 0 and win[0] + 1 <= ln <= win[1] + 1) else 0


M[u'gai_ex_rows'] = sum(inwin(GEX, ln) for ln in RKW[4])
M[u'gai_ex_label'] = sum(inwin(GEX, ln) for ln in RKW[4]
                         if row_shape_kw(FL[4][ln - 1])[2] == u'label')
M[u'gai_ex_prec'] = sum(inwin(GEX, ln) for ln in RKW[4]
                        if row_shape_kw(FL[4][ln - 1])[2] == u'precedence')
M[u'gai_def_rows'] = sum(inwin(GDEF, ln) for ln in RKW[4])
M[u'gai_def_label'] = sum(inwin(GDEF, ln) for ln in RKW[4]
                          if row_shape_kw(FL[4][ln - 1])[2] == u'label')
M[u'gai_def_prec'] = sum(inwin(GDEF, ln) for ln in RKW[4]
                         if row_shape_kw(FL[4][ln - 1])[2] == u'precedence')

# ---------------- 三元组档: 同一行 = (前缀, precedence, label) 三枚皆同 ----------------
def triples3(i):
    return [(row_shape3(FL[i][ln - 1])[0], row_shape3(FL[i][ln - 1])[1],
             row_shape3(FL[i][ln - 1])[2]) for ln in R3[i] if insec(i, ln)]


def triples_gai(win):
    dl, dp = {}, {}
    for ln in RKW[4]:
        if not inwin(win, ln):
            continue
        p, v, kw = row_shape_kw(FL[4][ln - 1])
        (dl if kw == u'label' else dp)[p] = v
    return sorted((p, dp[p], dl[p]) for p in set(dl) & set(dp))


TR6, TR4, TRE, TRD = triples3(0), triples3(1), triples_gai(GEX), triples_gai(GDEF)
M[u'triple6_n'] = len(TR6)
M[u'triple4_n'] = len(TR4)
M[u'triple_gai_ex_n'] = len(TRE)
M[u'triple_gai_def_n'] = len(TRD)
M[u'triple64_same'] = len(set(TR6) & set(TR4))
M[u'triple64_diff'] = len(set(TR6) ^ set(TR4))
M[u'triple_ex_eq4'] = 1 if set(TRE) == set(TR4) else 0
M[u'triple_ex_eq6'] = 1 if set(TRE) == set(TR6) else 0
M[u'triple_ex_same6'] = len(set(TRE) & set(TR6))
M[u'triple_ex_same4'] = len(set(TRE) & set(TR4))
M[u'triple_ex_only'] = sorted({t[0] for t in set(TRE) - set(TR4)})

# ---------------- 补全档前缀(八段全写)的对照 ⇎ 与字面档并立 ----------------
def pfx8(tok):
    if u':' not in tok:
        return tok
    body, _, plen = tok.partition(u'/')
    tail = (u'/' + plen) if plen else u''
    if u'::' in body:
        left = body.split(u'::')[0].split(u':')
        right = body.split(u'::')[1].split(u':')
        left = [x for x in left if x != u'']
        right = [x for x in right if x != u'']
        fill = 8 - len(left) - len(right)
        g = left + [u'0'] * (fill if fill > 0 else 0) + right
    else:
        g = body.split(u':')
    g = [x if x != u'' else u'0' for x in g][:8]
    while len(g) < 8:
        g.append(u'0')
    return u':'.join(g) + tail


P8 = [set(pfx8(p) for p in PFX[i]) for i in range(NSRC)]
M[u'pfx8_union'] = len(set().union(*P8))
M[u'pfx8_n'] = [len(s) for s in P8]
M[u'pfx_lit_union'] = M[u'pfx_union']
LAB8, PREC8 = {}, {}
for i in range(NSRC):
    for ln in R3[i]:
        p, a, b = row_shape3(FL[i][ln - 1])
        LAB8.setdefault(pfx8(p), set()).add(b)
        PREC8.setdefault(pfx8(p), set()).add(a)
    for ln in RKW[i]:
        p, v, kw = row_shape_kw(FL[i][ln - 1])
        (LAB8 if kw == u'label' else PREC8).setdefault(pfx8(p), set()).add(v)
    for ln in RCMN[i]:
        p, w, v = row_shape_cmtn(FL[i][ln - 1])[:3]
        LAB8.setdefault(pfx8(p), set()).add(v)
ALL8 = sorted(set(LAB8) | set(PREC8))
M[u'pfx8_conflict_label'] = [[p, sorted(LAB8[p], key=int)] for p in ALL8 if len(LAB8.get(p, ())) > 1]
M[u'pfx8_conflict_prec'] = [[p, sorted(PREC8[p], key=int)] for p in ALL8 if len(PREC8.get(p, ())) > 1]
M[u'pfx8_conflict_label_n'] = len(M[u'pfx8_conflict_label'])
M[u'pfx8_conflict_prec_n'] = len(M[u'pfx8_conflict_prec'])
M[u'pfx8_src_count'] = [[p, sum(1 for i in range(NSRC) if p in P8[i])] for p in ALL8]
M[u'pfx8_in_all7'] = len([1 for p, c in M[u'pfx8_src_count'] if c == NSRC])

# ---------------- 内核两份的顺序代数 ----------------
M[u'cinit_plens'] = [int(x) for x in M[u'cinit_plens']]
M[u'cmt_plens'] = [int(row_shape_cmtn(FL[5][ln - 1])[0].partition(u'/')[2]) for ln in RCMN[5]]
M[u'cinit_asc_pairs'] = sum(1 for k in range(1, len(M[u'cinit_plens']))
                            if M[u'cinit_plens'][k] >= M[u'cinit_plens'][k - 1])
M[u'cmt_asc_pairs'] = sum(1 for k in range(1, len(M[u'cmt_labels']))
                          if int(M[u'cmt_labels'][k]) > int(M[u'cmt_labels'][k - 1]))
M[u'plen_multiset_same'] = 1 if sorted(M[u'cinit_plens']) == sorted(M[u'cmt_plens']) else 0
M[u'plen_multiset_diff'] = len([1 for k in range(len(M[u'cinit_plens']))
                                if sorted(M[u'cinit_plens'])[k] != sorted(M[u'cmt_plens'])[k]])
M[u'label_multiset_same'] = 1 if sorted(M[u'cinit_labels'], key=int) == \
    sorted(M[u'cmt_labels'], key=int) else 0

io.open(u'corpus/_b97meas.json', 'w', encoding='utf-8', newline=u'\n').write(
    json.dumps(M, ensure_ascii=False, indent=0, sort_keys=True))
print(u'采集遍: 七份面 ⇎ 键 %d 枚 ⇎ 判词针 %d 枚 ⇎ 三列行 %s ⇎ 关键字行 %s ⇎ '
      u'注释表体行 %s ⇎ 注释含注行 %s ⇎ C 折平 %d ⇎ 宽档 %s ⇎ 最宽档 %s'
      % (len(M), NK, M[u'row3'], M[u'rowkw'], M[u'rowcmt3'], M[u'rowcmtn'],
         M[u'cinit_folded'], M[u'rowwide'], M[u'rowany']))
print(u'§2.1 节窗: %s (行 %s) ⇎ 图内三列行 %s ⇎ 列名行 %s'
      % (M[u'sec21_present'], M[u'sec21_lines'], M[u'fig_rows'], M[u'hdr_col_lines']))
print(u'注释框 %s ⇎ 框行 %d ⇎ 框内表体行 %d ⇎ 框内含注行 %d ⇎ 框内空行 %d ⇎ 框内注行 %d'
      % (M[u'cmtblock'], M[u'cmtblock_lines'], M[u'cmtblock_rows3'], M[u'cmtblock_rowsn'],
         M[u'cmtblock_blank'], M[u'cmtblock_note']))
print(u'Rule 头 %s ⇎ 清单 %s ⇎ 5.5 %s ⇎ 带符号 %s' % (M[u'rule_heads'], M[u'rule_list'],
                                                     M[u'rule_55'], M[u'rule_sign']))
print(u'翻转差 %s ⇎ ULA-site 差 %s' % (M[u'flip_v6mapped'], M[u'flip_ula']))
print(u'标签冲突 %d: %s' % (M[u'label_conflict_n'], M[u'label_conflict']))
print(u'precedence 冲突 %d: %s' % (M[u'prec_conflict_n'], M[u'prec_conflict']))
print(u'前缀并集 %d ⇎ 档 %s ⇎ 独占 %s' % (M[u'pfx_union'], M[u'pfx_hist'], M[u'pfx_only']))
print(u'C 序 %s' % M[u'cinit_order'])
print(u'注 序 %s' % M[u'cmt_order'])
print(u'顺序倒置 %d ⇎ 同序 %d ⇎ 共有 %d ⇎ 只在 C %s ⇎ 只在注 %s ⇎ 同格标签符 %d'
      % (M[u'order_reverse'], M[u'order_same'], M[u'order_common'], M[u'order_only_c'],
         M[u'order_only_m'], M[u'label_agree_cells']))
print(u'针七份全冷: %s' % [[NEEDLES[k] for k in M[u'needle_cold']]])
print(u'针全份皆热: %s' % [[NEEDLES[k] for k in M[u'needle_all']]])
print(u'壳行 %s ⇎ 正文行 %s ⇎ 换页 %s ⇎ 制表 %s ⇎ 非 ASCII %s'
      % (M[u'shell_lines'], M[u'body_lines'], M[u'ff'], M[u'tab'], M[u'nonascii']))
print(u'锚 位 %d ⇎ 去重串 %d' % (M[u'atom_n'], M[u'atom_distinct']))
print(u'针合计 行 %s ⇎ 折 %s ⇎ 摘壳折 %s ⇎ 增益 %s'
      % (M[u'needles_row'], M[u'needles_fold'], M[u'needles_noshell'], M[u'needles_gain']))
print(u'引用针 %s' % M[u'cite'])
print(u'关键字行拆列 label %s ⇎ precedence %s ⇎ 语法说明行 %s ⇎ §2.1 外三列行 %s'
      % (M[u'kw_label'], M[u'kw_prec'], M[u'kwdef'], M[u'row3_out21']))
print(u'列名行 精确 %s ⇎ 抹平 %s' % (M[u'hdr_col_lines'], M[u'hdr_col_any']))
print(u'gai 示例窗 %s(%d 行, 行 %d) ⇎ 默认窗 %s(%d 行, 行 %d)'
      % (M[u'gai_exwin'], M[u'gai_ex_lines'], M[u'gai_ex_rows'],
         M[u'gai_defwin'], M[u'gai_def_lines'], M[u'gai_def_rows']))
print(u'三元组 6724 %d ⇎ 3484 %d ⇎ gai 例 %d ⇎ gai 默认 %d ⇎ 6724∩3484 %d ⇎ 6724△3484 %d'
      % (M[u'triple6_n'], M[u'triple4_n'], M[u'triple_gai_ex_n'], M[u'triple_gai_def_n'],
         M[u'triple64_same'], M[u'triple64_diff']))
print(u'gai 示例块 = 3484 表 %d ⇎ = 6724 表 %d ⇎ 与 6724 同三元组 %d ⇎ 与 3484 同三元组 %d ⇎ 独有 %s'
      % (M[u'triple_ex_eq4'], M[u'triple_ex_eq6'], M[u'triple_ex_same6'], M[u'triple_ex_same4'],
         M[u'triple_ex_only']))
print(u'补全档 并集 %d ⇎ 逐份 %s ⇎ 字面档并集 %d ⇎ 冲突 标签 %d %s ⇎ 优先 %d %s'
      % (M[u'pfx8_union'], M[u'pfx8_n'], M[u'pfx_lit_union'], M[u'pfx8_conflict_label_n'],
         M[u'pfx8_conflict_label'], M[u'pfx8_conflict_prec_n'], M[u'pfx8_conflict_prec']))
print(u'内核序: C 长度 %s ⇎ 注 长度 %s ⇎ C 升序对 %d ⇎ 注 label 升序对 %d ⇎ 长度多重集同 %d(差 %d) ⇎ 标签多重集同 %d'
      % (M[u'cinit_plens'], M[u'cmt_plens'], M[u'cinit_asc_pairs'], M[u'cmt_asc_pairs'],
         M[u'plen_multiset_same'], M[u'plen_multiset_diff'], M[u'label_multiset_same']))
