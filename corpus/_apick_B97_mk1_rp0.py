# 新增到 corpus/_mkB97.py(整文件新建; 骨架照 corpus/_mkB96.py, 与 corpus/_pick97.py 逐键对账)
# -*- coding: utf-8 -*-
# ============================================================================
# B97 建条目侧(第二套实现, A 侧): 多文本压缩 · IPv6 默认前缀策略表
#   七源 = RFC 6724(2012 现行) ⇎ RFC 3484(2003 被替代) ⇎ RFC 7381(BCP 177) ⇎
#          RFC 8407(负对照: 题面点名却实为 BCP 216 YANG 指南) ⇎ gai.conf(5)(发行版配置) ⇎
#          net/ipv6/addrlabel.c(内核注释表 + C 结构体) ⇎ net/ipv6/addrconf.c(内核算法侧)
#   本文件只做两件事: ①SCAN 段把七份原文面各量一遍(与 corpus/_pick97.py 是同一套口径的
#     两套机制, 对账件由 _pick97.py 写 corpus/_b97meas.json); ②按问题⇎五份文书各答一遍⇎
#     每答挂一枚原文锚 的次序发射条目(编码区数字全部由 V() 插值, 零手填)。
# 机制档位(A 侧, 与采集遍九处不同): splitlines 行式 ⇎ re.findall(re.escape) 整串扫描 ⇎
#   一条整串正则 fullmatch 判行形 ⇎ 针偏移经累积长度表 + bisect 开窗 ⇎ Counter 直方图档 ⇎
#   正则取数字段 ⇎ 逐字符抄词自建词表折平 ⇎ token 枚举判义务词形状 ⇎ 三条正则一次剥壳。
# 运行次序: python -X utf8 corpus/_pick97.py ⇎ python -X utf8 corpus/_mkB97.py
#           ⇎ python -X utf8 corpus/_mk97emit.py ⇎ python -X utf8 corpus/_wire97.py
# ============================================================================
import io, json, os, re, sys
from bisect import bisect_left, bisect_right
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAWS = [u'corpus/raw/prefixtable97/rfc6724.txt', u'corpus/raw/prefixtable97/rfc3484.txt',
        u'corpus/raw/prefixtable97/rfc7381.txt', u'corpus/raw/prefixtable97/rfc8407.txt',
        u'corpus/raw/prefixtable97/gai_conf5.html', u'corpus/raw/prefixtable97/addrlabel.c',
        u'corpus/raw/prefixtable97/addrconf.c']
LBL = [u'6724', u'3484', u'7381', u'8407', u'gai', u'lbl', u'adr']
NSRC = 7
ISHTML = [False, False, False, False, True, False, False]
ATOMFILE = u'corpus/_atoms97.txt'
MEASA = u'corpus/_tmp97_measA.json'
MEAS = u'corpus/_b97meas.json'
ENTRY = u'corpus/babeltele/B97_ipv6_default_prefix_policy_table_compression.md'

# 口径不同不对账清单(逐键写明差在哪把尺; 其余键一律逐键对账)
DIFF_OK = {
    u'lines_nl': u'A 侧 splitlines 折 CRLF/FF 尾, 采集侧 split("\\n"); 差 = 换页与尾行计法',
    u'lines_sl': u'同上倒过来: 采集侧 splitlines 计换页为断行, A 侧先 split("\\n") 再拆',
    u'pfx_pairsum': u'A 侧按字母序 all-pairs 展开成扁平表, 采集侧按 (i,j) 上三角三元组表; 枚数同口径值不同序列化',
    u'pfx_pairs': u'同上: 结构不同, 不入对账',
    u'cinit_asc_pairs': u'A 侧逐对 >= 计(含等), 采集侧同定义但顺序取 cinit_plens 原序; 值应同, 若不同按本清单记',
}

# --- SCAN BEGIN ---
def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


def striptags3(s):
    """机制⑨': 三条正则一次剥壳(采集侧是 '<' 游标分段)。"""
    s = re.sub(u'<[^>]*>', u' ', s)
    s = re.sub(u'&nbsp;', u' ', s)
    s = re.sub(u'&amp;', u'&', s)
    return s


def foldc(s):
    """机制⑦': 逐字符抄词自建词表折平(采集侧是 ' '.join(split()))。"""
    out, cur = [], []
    for ch in s:
        if ch.isspace():
            if cur:
                out.append(u''.join(cur))
                cur = []
        else:
            cur.append(ch)
    if cur:
        out.append(u''.join(cur))
    return u' '.join(out)


RAW = [rd(p) for p in RAWS]
FACE = [striptags3(RAW[i]) if ISHTML[i] else RAW[i] for i in range(NSRC)]
LINES = [f.splitlines() for f in FACE]            # 机制①': splitlines
NLINES = [[l.split(u'\n') for l in [f]][0] for f in FACE]
FOLD = [foldc(f) for f in FACE]
PNF = [foldc(FOLD[i].lower()) for i in range(NSRC)]


def cnt_cur(s, needle):
    """机制②': re.findall(re.escape) 整串扫描(非重叠枚数), 采集侧是游标 find 环。"""
    return len(re.findall(re.escape(needle), s))


def cnt_row(i, needle):
    return sum(l.count(needle) for l in LINES[i])


# —— 面尺 ——
F = {}
F['bytes'] = [os.path.getsize(p) for p in RAWS]
F['chars'] = [len(RAW[i]) for i in range(NSRC)]
F['face_chars'] = [len(FACE[i]) for i in range(NSRC)]
F['lf'] = [RAW[i].count(u'\n') for i in range(NSRC)]
F['cr'] = [RAW[i].count(u'\r') for i in range(NSRC)]
F['ff'] = [RAW[i].count(u'\x0c') for i in range(NSRC)]
F['tab'] = [RAW[i].count(u'\t') for i in range(NSRC)]
F['nonascii'] = [sum(1 for c in RAW[i] if ord(c) > 127) for i in range(NSRC)]
F['bom'] = [1 if RAW[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
F['lines_nl'] = [len(NLINES[i]) for i in range(NSRC)]
F['lines_sl'] = [len(LINES[i]) for i in range(NSRC)]
F['blank'] = [sum(1 for l in LINES[i] if l.strip() == u'') for i in range(NSRC)]
F['maxlen'] = [max(len(l) for l in LINES[i]) for i in range(NSRC)]
F['trailing_nl'] = [1 if RAW[i].endswith(u'\n') else 0 for i in range(NSRC)]
F['utf8_extra'] = [F['bytes'][i] - F['chars'][i] for i in range(NSRC)]
RX_FOOT = re.compile(u'^\\s*[A-Za-z][A-Za-z., ]*\\sStandards Track\\s+\\[Page \\d+\\]\\s*$')
RX_HDR = re.compile(u'^RFC \\d+\\s+\\S')
RX_IETF = re.compile(u'^Internet Engineering Task Force')
RX_PGONLY = re.compile(u'^\\s*\\d+\\s*$')
RX_CMTLEAD = re.compile(u'^\\s*\\*')
RX_TAGONLY = re.compile(u'^\\s*</?[a-zA-Z!][^>]*>\\s*$')
SHELLP = [RX_FOOT, RX_HDR, RX_IETF, RX_PGONLY, RX_CMTLEAD, RX_TAGONLY]


def is_shell(line):
    s = line.strip()
    if s == u'' or s == u'\x0c':
        return True
    for p in SHELLP:
        if p.match(line):
            return True
    return False


SHELL = [[is_shell(l) for l in LINES[i]] for i in range(NSRC)]
F['shell_lines'] = [sum(1 for x in SHELL[i] if x) for i in range(NSRC)]
F['body_lines'] = [F['lines_nl'][i] - F['shell_lines'][i] for i in range(NSRC)]
F['foot_page'] = [len([l for l in LINES[i] if RX_FOOT.match(l)]) for i in range(NSRC)]
F['hdr_rfc'] = [len([l for l in LINES[i] if RX_HDR.match(l)]) for i in range(NSRC)]
F['ietf_alone'] = [len([l for l in LINES[i] if RX_IETF.match(l)]) for i in range(NSRC)]
F['cmt_lead'] = [len([l for l in LINES[i] if RX_CMTLEAD.match(l)]) for i in range(NSRC)]
F['pgonly'] = [len([l for l in LINES[i] if RX_PGONLY.match(l)]) for i in range(NSRC)]
F['tagcount'] = [len(re.findall(u'<[^>]+>', RAW[i])) if ISHTML[i] else 0 for i in range(NSRC)]
SHF = [foldc(u' '.join(u' %s ' % l for k, l in enumerate(LINES[i]) if not SHELL[i][k]))
       for i in range(NSRC)]
SHP = [foldc(x.lower()) for x in SHF]

# —— 行形谓词: 机制③' 一条整串正则 fullmatch ——
RX_PFX = re.compile(u'^[0-9a-fA-F:]+(?:/[0-9]+)?$')
RX_NUM = re.compile(u'^[0-9]+$')
RX_ATYPE = re.compile(u'^[A-Za-z0-9/]+$')
RX_ROW3 = re.compile(u'^(?P<p>[0-9a-fA-F:]+(?:/[0-9]+)?)\\s+(?P<a>[0-9]+)\\s+(?P<b>[0-9]+)$')
RX_ROWKW = re.compile(u'^(?P<kw>label|precedence)\\s+(?P<p>[0-9a-fA-F:]+(?:/[0-9]+)?)\\s+(?P<v>[0-9]+)$')
RX_ROWCM3 = re.compile(u'^\\*\\s*(?P<p>[0-9a-fA-F:]+(?:/[0-9]+)?)\\s+(?P<w>[A-Za-z0-9/]+)\\s+(?P<v>[0-9]+)$')
RX_ROWCMN = re.compile(u'^\\*\\s*(?P<p>[0-9a-fA-F:]+(?:/[0-9]+)?)\\s+(?P<w>[A-Za-z0-9/]+)\\s+(?P<v>[0-9]+)(?:\\s+.*)?$')


def lines_shape(rx, i):
    return [k + 1 for k, l in enumerate(LINES[i]) if rx.match(l.strip())]


R3 = [lines_shape(RX_ROW3, i) for i in range(NSRC)]
RKW = [lines_shape(RX_ROWKW, i) for i in range(NSRC)]
RCM3 = [lines_shape(RX_ROWCM3, i) for i in range(NSRC)]
RCMN = [lines_shape(RX_ROWCMN, i) for i in range(NSRC)]
RCINIT = [[k + 1 for k, l in enumerate(LINES[i]) if u'.label = ' in l] for i in range(NSRC)]


def row_of(rx, i, ln):
    m = rx.match(LINES[i][ln - 1].strip())
    return m.groupdict() if m else None


def row3(i, ln):
    d = row_of(RX_ROW3, i, ln)
    return [d['p'], d['a'], d['b']] if d else None


def rowkw(i, ln):
    d = row_of(RX_ROWKW, i, ln)
    return [d['p'], d['v'], d['kw']] if d else None


def rowcmn(i, ln):
    d = row_of(RX_ROWCMN, i, ln)
    return [d['p'], d['w'], d['v']] if d else None


F['row3'] = [len(x) for x in R3]
F['rowkw'] = [len(x) for x in RKW]
F['rowcmt3'] = [len(x) for x in RCM3]
F['rowcmtn'] = [len(x) for x in RCMN]
F['rowcmt'] = [len(x) for x in RCMN]
F['rowcinit'] = [len(x) for x in RCINIT]
RX_WIDE = re.compile(u'^\\*?\\s*(?:[^\\s]*\\s+)*?[0-9a-fA-F:]+(?:/[0-9]+)?[^\\s]*\\s+.*[0-9]+$')
F['rowwide'] = [len([1 for l in LINES[i] if RX_WIDE.match(l.strip())]) for i in range(NSRC)]
RX_PFXANY = re.compile(u'^(?:\\*\\s*)?(?:[^\\s]+\\s+)*?[0-9a-fA-F:]*:[0-9a-fA-F:]+(?:/[0-9]+)?(?:\\s+.*)?$')


def any_pfx(i):
    out = []
    for l in LINES[i]:
        m = RX_PFXANY.match(l.strip())
        if m:
            for tok in l.replace(u'*', u' ').split():
                if RX_PFX.match(tok) and u':' in tok:
                    out.append(tok)
                    break
    return out


RANY = [any_pfx(i) for i in range(NSRC)]
F['rowany'] = [len(x) for x in RANY]

# —— 块定界: 机制④' 针偏移经累积长度表 + bisect 开窗 ——
CUML = [[len(x) + 1 for x in LINES[i]] for i in range(NSRC)]
POS, ACC = [], []
for i in range(NSRC):
    a = [0]
    for c in CUML[i]:
        a.append(a[-1] + c)
    POS.append(a)


def line_of(i, pos):
    return bisect_right(POS[i], pos)


RX_SECHDR = re.compile(u'^(\\d+(?:\\.\\d+){0,2})\\.?\\s+\\S')


def sec_of2(i, want):
    hits = []
    for k, l in enumerate(LINES[i]):
        m = RX_SECHDR.match(l)
        if m:
            hits.append((k + 1, m.group(1)))
    for pos, (ln, num) in enumerate(hits):
        if num == want:
            lvl = num.count(u'.')
            end = len(LINES[i])
            for ln2, num2 in hits[pos + 1:]:
                if num2.count(u'.') <= lvl:
                    end = ln2 - 1
                    break
            return ln, end
    return None


SEC21 = [sec_of2(i, u'2.1') for i in range(NSRC)]
F['sec21_present'] = [1 if x else 0 for x in SEC21]
F['sec21_lines'] = [(x[1] - x[0] + 1) if x else 0 for x in SEC21]
F['sec21_at'] = [[x[0], x[1]] if x else [-1, -1] for x in SEC21]


def insec(i, ln):
    return 1 if (SEC21[i] and SEC21[i][0] <= ln <= SEC21[i][1]) else 0


F['fig_rows'] = [sum(insec(i, ln) for ln in R3[i]) for i in range(NSRC)]
F['fig_kw'] = [sum(insec(i, ln) for ln in RKW[i]) for i in range(NSRC)]
F['hdr_col_lines'] = [len([l for l in LINES[i] if l.strip() == u'Prefix        Precedence Label'])
                      for i in range(NSRC)]
F['hdr_col_any'] = [len([l for l in LINES[i] if foldc(l.lower()) == u'prefix precedence label'])
                    for i in range(NSRC)]
F['hdr_col_words'] = [len([l for l in LINES[i] if l.strip().startswith(u'Prefix')
                           and u'Precedence' in l]) for i in range(NSRC)]


def cmtblock2(i, title):
    a = -1
    for k, l in enumerate(LINES[i]):
        if title in l:
            a = k
            break
    if a < 0:
        return -1, -1
    j = a
    while j < len(LINES[i]) and not LINES[i][j].strip().endswith(u'*/'):
        j += 1
    return a + 1, j


CB = cmtblock2(5, u'Default policy table (RFC6724 + extensions)')
F['cmtblock'] = [CB[0] + 1, CB[1] + 1] if CB[0] >= 0 else [-1, -1]
F['cmtblock_lines'] = (CB[1] - CB[0] + 1) if CB[0] >= 0 else 0
F['cmtblock_rows3'] = len([ln for ln in RCM3[5] if CB[0] < ln - 1 <= CB[1]])
F['cmtblock_rowsn'] = len([ln for ln in RCMN[5] if CB[0] < ln - 1 <= CB[1]])
F['cmtblock_blank'] = len([ln for ln in range(CB[0] + 1, CB[1] + 2) if LINES[5][ln - 1].strip() == u''])
F['cmtblock_note'] = len([ln for ln in range(CB[0] + 1, CB[1] + 2)
                          if LINES[5][ln - 1].strip().startswith(u'*')
                          and not RX_ROWCMN.match(LINES[5][ln - 1].strip())
                          and LINES[5][ln - 1].strip() not in (u'/*', u'*/', u'*')])
F['fig_cmt'] = [F['cmtblock_rowsn'] if i == 5 else 0 for i in range(NSRC)]

# —— 前缀代数: 机制⑤' Counter 直方图档 ——
PFX = []
for i in range(NSRC):
    c = Counter()
    for ln in R3[i]:
        c[row3(i, ln)[0]] += 1
    for ln in RKW[i]:
        c[rowkw(i, ln)[0]] += 1
    for ln in RCMN[i]:
        c[rowcmn(i, ln)[0]] += 1
    PFX.append(set(c))
ALLS = sorted(set().union(*PFX)) if NSRC else []
hist = Counter()
for p in ALLS:
    hist[sum(1 for i in range(NSRC) if p in PFX[i])] += 1
F['pfx_distinct'] = [len(s) for s in PFX]
F['pfx_union'] = len(ALLS)
F['pfx_hist'] = [hist.get(h, 0) for h in range(1, NSRC + 1)]
F['pfx_only'] = [len([p for p in PFX[i] if sum(1 for j in range(NSRC) if p in PFX[j]) == 1])
                 for i in range(NSRC)]
F['pfx_only_list'] = [sorted([p for p in PFX[i] if sum(1 for j in range(NSRC) if p in PFX[j]) == 1])
                      for i in range(NSRC)]
_pairs = []
for i in range(NSRC):
    for j in range(NSRC):
        if i <= j:
            _pairs.append(len(PFX[i] & PFX[j]))
F['pfx_pairsum'] = _pairs
F['pfx_pairs'] = [[i, j, len(PFX[i] & PFX[j])] for i in range(NSRC) for j in range(NSRC) if i < j]

LAB, PREC = [], []
for i in range(NSRC):
    dl, dp = {}, {}
    for ln in R3[i]:
        p, a, b = row3(i, ln)
        dl.setdefault(p, b)
        dp.setdefault(p, a)
    for ln in RKW[i]:
        p, v, kw = rowkw(i, ln)
        (dl if kw == u'label' else dp).setdefault(p, v)
    for ln in RCMN[i]:
        p, w, v = rowcmn(i, ln)[:3]
        dl.setdefault(p, v)
    LAB.append(dl)
    PREC.append(dp)
PANY = [set(x) for x in RANY]
F['pfx_any_union'] = len(set().union(*PANY)) if PANY else 0
F['pfx_any_n'] = [len(s) for s in PANY]
F['pfx_any_rows'] = [len(x) for x in RANY]
UN = sorted(set().union(*[set(d) for d in LAB] + [set(d) for d in PREC])) if NSRC else []
F['col_prefix_union'] = len(UN)
F['col_label_hit'] = [len(LAB[i]) for i in range(NSRC)]
F['col_prec_hit'] = [len(PREC[i]) for i in range(NSRC)]


def confl(tables):
    out = []
    for p in UN:
        vals = sorted({d[p] for d in tables if p in d})
        if len(vals) > 1:
            out.append([p, vals])
    return out


CONFL, CONFP = confl(LAB), confl(PREC)
F['label_conflict_n'] = len(CONFL)
F['label_conflict'] = CONFL
F['prec_conflict_n'] = len(CONFP)
F['prec_conflict'] = CONFP


def diffpair(tables, a, b):
    out = []
    for d in tables:
        x, y = d.get(a), d.get(b)
        out.append(int(x) - int(y) if x is not None and y is not None else 0)
    return out


F['flip_v6mapped'] = diffpair(PREC, u'::ffff:0:0/96', u'::/96')
F['flip_ula'] = diffpair(LAB, u'fc00::/7', u'fec0::/10')
F['prec_vals_union'] = sorted({v for d in PREC for v in d.values()}, key=int)
F['label_vals_union'] = sorted({v for d in LAB for v in d.values()}, key=int)
F['prec_val_n'] = len(F['prec_vals_union'])
F['label_val_n'] = len(F['label_vals_union'])

# —— Rule 头(算法侧) ——
def rule_heads(s):
    return re.findall(u'Rule ([0-9][0-9.+-]*):', s)


RH = [rule_heads(FOLD[i]) for i in range(NSRC)]
F['rule_heads'] = [len(x) for x in RH]
F['rule_uniq'] = [len(set(x)) for x in RH]
F['rule_frac'] = [len([x for x in RH[i] if u'.' in x]) for i in range(NSRC)]
F['rule_sign'] = [len([x for x in RH[i] if u'-' in x or u'+' in x]) for i in range(NSRC)]
F['rule_55'] = [len([x for x in RH[i] if x == u'5.5']) for i in range(NSRC)]
F['rule_list'] = [sorted(set(x)) for x in RH]
F['rule_max_num'] = [max([int(x.split(u'.')[0].rstrip(u'-+')) for x in RH[i]] or [-1])
                     for i in range(NSRC)]
F['enum_saddr'] = [len(re.findall(u'IPV6_SADDR_RULE_[A-Z0-9]+', FOLD[i])) for i in range(NSRC)]
F['enum_uniq'] = [len(set(re.findall(u'IPV6_SADDR_RULE_[A-Z0-9]+', FOLD[i]))) for i in range(NSRC)]
F['ifdef'] = [len(re.findall(u'#ifdef CONFIG_IPV6', FOLD[i])) for i in range(NSRC)]

# —— 引用针 ——
CIT = [u'RFC 6724', u'RFC6724', u'RFC 3484', u'RFC3484', u'RFC 4193', u'RFC 4380',
       u'RFC 4843', u'RFC 6555', u'RFC 6724 + extensions', u'BCP 177', u'BCP 216', u'YANG']
F['cite_keys'] = CIT
F['cite'] = [[FOLD[i].count(c) for c in CIT] for i in range(NSRC)]

# —— 义务词形状: 机制⑧' token 枚举判形状 ——
OBL = [u'MUST', u'SHOULD', u'MAY']
ob_u, ob_n, ob_l = [], [], []
for i in range(NSRC):
    toks = FOLD[i].split()
    c_u = {w: 0 for w in OBL}
    c_n = {w: 0 for w in OBL}
    c_l = {w: 0 for w in OBL}
    for k, t in enumerate(toks):
        for w in OBL:
            if t == w:
                c_u[w] += 1
                if k + 1 < len(toks) and toks[k + 1] == u'NOT':
                    c_n[w] += 1
            if t == w.lower():
                c_l[w] += 1
    ob_u.append([c_u[w] for w in OBL])
    ob_n.append([c_n[w] for w in OBL])
    ob_l.append([c_l[w] for w in OBL])
F['oblig_upper'] = ob_u
F['oblig_not'] = ob_n
F['oblig_lower'] = ob_l
F['oblig_tot'] = [sum(ob_u[i]) + sum(ob_n[i]) for i in range(NSRC)]

# —— 判词针 ⇎ 三档口径 ——
NEEDLES = [
    u'Default Address Selection for IPv6',
    u'the following default policy table:',
    u'default policy table',
    u'longest-matching-prefix lookup table',
    u'Prefix Precedence Label',
    u'::1/128', u'::/0', u'::/96', u'::ffff:0:0/96', u'2002::/16', u'2001::/32',
    u'2001:0::/32', u'fc00::/7', u'fec0::/10', u'3ffe::/16', u'fe80::/10', u'2001:10::/28',
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
    u'N/A', u'LOOPBACK', u'V4MAPPED', u'COMPATv4',
    u'highest success rate',
    u'YANG',
]
NK = len(NEEDLES)
TIER = [[[cnt_cur(FOLD[i], nd), cnt_cur(SHF[i], nd), cnt_row(i, nd)]
         for i in range(NSRC)] for nd in NEEDLES]
F['needles3'] = TIER
F['needle_list'] = NEEDLES
F['needles_row'] = [sum(TIER[k][i][2] for k in range(NK)) for i in range(NSRC)]
F['needles_fold'] = [sum(TIER[k][i][0] for k in range(NK)) for i in range(NSRC)]
F['needles_noshell'] = [sum(TIER[k][i][1] for k in range(NK)) for i in range(NSRC)]
F['needles_gain'] = [F['needles_fold'][i] - F['needles_row'][i] for i in range(NSRC)]
F['needle_zero'] = [[k for k in range(NK) if TIER[k][i][0] == 0] for i in range(NSRC)]
F['needle_cold'] = [k for k in range(NK) if sum(TIER[k][i][0] for i in range(NSRC)) == 0]
F['needle_all'] = [k for k in range(NK) if all(TIER[k][i][0] > 0 for i in range(NSRC))]
F['needle_max'] = [max(TIER[k][i][0] for i in range(NSRC)) for k in range(NK)]

# —— 锚: 由面上位置导出(与采集遍同定义: 折平面 find 位置) ——
ATOMS = []
for k, nd in enumerate(NEEDLES):
    for i in range(NSRC):
        if TIER[k][i][0] > 0:
            j = FOLD[i].find(nd)
            ATOMS.append([nd, LBL[i], j, TIER[k][i][0]])
F['atom_pairs'] = ATOMS
F['atom_n'] = len(ATOMS)
F['atom_distinct'] = len(set(a[0] for a in ATOMS))

# —— 图框窗口 ⇎ 注释框窗口 ——
FIGWIN = [(LINES[i][SEC21[i][0] - 1:SEC21[i][1]] if SEC21[i] else []) for i in range(NSRC)]
F['figwin_lines'] = [len(x) for x in FIGWIN]
F['figwin_shell'] = [sum(1 for l in FIGWIN[i] if is_shell(l)) for i in range(NSRC)]
F['figwin_blank'] = [sum(1 for l in FIGWIN[i] if l.strip() == u'') for i in range(NSRC)]
F['figwin_chars'] = [sum(len(l) + 1 for l in FIGWIN[i]) for i in range(NSRC)]

# —— 内核 C 数组的"折平后行": 花括号深度逐字符扫 ——
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
                    out.append(foldc(ent))
                ent = u''
            elif d == 0:
                break
        elif d >= 2:
            ent += c
        p += 1
    return out


CF = cinit_fold(FACE[5])
F['cinit_folded'] = len(CF)
F['cinit_lines'] = len([l for l in LINES[5] if re.match(u'^\\s*\\{\\s*(/\\*|$)', l)])
F['cinit_label'] = F['rowcinit'][5]
F['cinit_comment_rows'] = F['rowcmtn'][5]
F['cinit_comment_rows3'] = F['rowcmt3'][5]


def pref_from_ent(x):
    m = re.search(u'/\\*\\s*(\\S+?)\\s*\\*/', x)
    return m.group(1) if m else u''


F['cinit_order'] = [pref_from_ent(x) for x in CF]
F['cinit_labels'] = [re.search(u'\\.label = (\\d+)', x).group(1) for x in CF]
F['cinit_plens'] = [(int(re.search(u'\\.prefixlen = (\\d+)', x).group(1))
                     if re.search(u'\\.prefixlen = (\\d+)', x) else 0) for x in CF]
F['cmt_order'] = [rowcmn(5, ln)[0] for ln in RCMN[5]]
F['cmt_labels'] = [rowcmn(5, ln)[2] for ln in RCMN[5]]
F['order_reverse'] = 1 if F['cinit_order'] == list(reversed(F['cmt_order'])) else 0
F['order_same'] = 1 if F['cinit_order'] == F['cmt_order'] else 0
F['order_common'] = len(set(F['cinit_order']) & set(F['cmt_order']))
F['order_only_c'] = sorted(set(F['cinit_order']) - set(F['cmt_order']))
F['order_only_m'] = sorted(set(F['cmt_order']) - set(F['cinit_order']))
F['label_agree_cells'] = len([p for p in set(F['cinit_order']) & set(F['cmt_order'])
                              if F['cinit_labels'][F['cinit_order'].index(p)]
                              == F['cmt_labels'][F['cmt_order'].index(p)]])

F['nsrc'] = NSRC
F['lbl'] = LBL
F['ids'] = [os.path.basename(p) for p in RAWS]
F['path'] = RAWS

# —— 列名行的两档口径 ⇎ 关键字行的两列拆分 ——
F['kw_label'] = [len([ln for ln in RKW[i] if rowkw(i, ln)[2] == u'label']) for i in range(NSRC)]
F['kw_prec'] = [len([ln for ln in RKW[i] if rowkw(i, ln)[2] == u'precedence']) for i in range(NSRC)]
F['kwdef'] = [[len([l for l in LINES[i] if foldc(l.lower()) == u'label netmask label']),
               len([l for l in LINES[i] if foldc(l.lower()) == u'precedence netmask precedence'])]
              for i in range(NSRC)]
F['row3_out21'] = [F['row3'][i] - F['fig_rows'][i] for i in range(NSRC)]


# —— gai 的两块窗口 ——
def win_after(i, needle, stops, cap=60):
    a = -1
    for k, l in enumerate(LINES[i]):
        if needle in l:
            a = k
            break
    if a < 0:
        return -1, -1
    b = min(a + cap, len(LINES[i]) - 1)
    for k in range(a + 1, b + 1):
        s = LINES[i][k].strip()
        if any(x in s for x in stops):
            return a + 1, k - 1
    return a + 1, b


STOPS = [u'SEES ALSO', u'SEE ALSO', u'FILES', u'COLOPHON', u'glibc includes some extra rules', u'NOTES']
GEX = win_after(4, u'The default table according to RFC 3484', [u'glibc includes some extra rules'])
GDEF = win_after(4, u'Its default label table is:', STOPS)
F['gai_exwin'] = [GEX[0] + 1, GEX[1] + 1] if GEX[0] >= 0 else [-1, -1]
F['gai_defwin'] = [GDEF[0] + 1, GDEF[1] + 1] if GDEF[0] >= 0 else [-1, -1]
F['gai_ex_lines'] = (GEX[1] - GEX[0] + 1) if GEX[0] >= 0 else 0
F['gai_def_lines'] = (GDEF[1] - GDEF[0] + 1) if GDEF[0] >= 0 else 0


def inwin(win, ln):
    return 1 if (win[0] >= 0 and win[0] + 1 <= ln <= win[1] + 1) else 0


F['gai_ex_rows'] = sum(inwin(GEX, ln) for ln in RKW[4])
F['gai_ex_label'] = sum(inwin(GEX, ln) for ln in RKW[4] if rowkw(4, ln)[2] == u'label')
F['gai_ex_prec'] = sum(inwin(GEX, ln) for ln in RKW[4] if rowkw(4, ln)[2] == u'precedence')
F['gai_def_rows'] = sum(inwin(GDEF, ln) for ln in RKW[4])
F['gai_def_label'] = sum(inwin(GDEF, ln) for ln in RKW[4] if rowkw(4, ln)[2] == u'label')
F['gai_def_prec'] = sum(inwin(GDEF, ln) for ln in RKW[4] if rowkw(4, ln)[2] == u'precedence')

# —— 三元组档 ——
def triples3(i):
    return [(row3(i, ln)[0], row3(i, ln)[1], row3(i, ln)[2]) for ln in R3[i] if insec(i, ln)]


def triples_gai(win):
    dl, dp = {}, {}
    for ln in RKW[4]:
        if not inwin(win, ln):
            continue
        p, v, kw = rowkw(4, ln)
        (dl if kw == u'label' else dp)[p] = v
    return sorted((p, dp[p], dl[p]) for p in set(dl) & set(dp))


TR6, TR4, TRE, TRD = triples3(0), triples3(1), triples_gai(GEX), triples_gai(GDEF)
F['triple6_n'] = len(TR6)
F['triple4_n'] = len(TR4)
F['triple_gai_ex_n'] = len(TRE)
F['triple_gai_def_n'] = len(TRD)
F['triple64_same'] = len(set(TR6) & set(TR4))
F['triple64_diff'] = len(set(TR6) ^ set(TR4))
F['triple_ex_eq4'] = 1 if set(TRE) == set(TR4) else 0
F['triple_ex_eq6'] = 1 if set(TRE) == set(TR6) else 0
F['triple_ex_same6'] = len(set(TRE) & set(TR6))
F['triple_ex_same4'] = len(set(TRE) & set(TR4))
F['triple_ex_only'] = sorted({t[0] for t in set(TRE) - set(TR4)})

# —— 补全档前缀(八段全写) ——
def pfx8(tok):
    if u':' not in tok:
        return tok
    body, _, plen = tok.partition(u'/')
    tail = (u'/' + plen) if plen else u''
    if u'::' in body:
        left = [x for x in body.split(u'::')[0].split(u':') if x != u'']
        right = [x for x in body.split(u'::')[1].split(u':') if x != u'']
        fill = 8 - len(left) - len(right)
        g = left + [u'0'] * (fill if fill > 0 else 0) + right
    else:
        g = body.split(u':')
    g = [x if x != u'' else u'0' for x in g][:8]
    while len(g) < 8:
        g.append(u'0')
    return u':'.join(g) + tail


P8 = [set(pfx8(p) for p in PFX[i]) for i in range(NSRC)]
F['pfx8_union'] = len(set().union(*P8))
F['pfx8_n'] = [len(s) for s in P8]
F['pfx_lit_union'] = F['pfx_union']
LAB8, PREC8 = {}, {}
for i in range(NSRC):
    for ln in R3[i]:
        p, a, b = row3(i, ln)
        LAB8.setdefault(pfx8(p), set()).add(b)
        PREC8.setdefault(pfx8(p), set()).add(a)
    for ln in RKW[i]:
        p, v, kw = rowkw(i, ln)
        (LAB8 if kw == u'label' else PREC8).setdefault(pfx8(p), set()).add(v)
    for ln in RCMN[i]:
        p, w, v = rowcmn(i, ln)[:3]
        LAB8.setdefault(pfx8(p), set()).add(v)
ALL8 = sorted(set(LAB8) | set(PREC8))
F['pfx8_conflict_label'] = [[p, sorted(LAB8[p], key=int)] for p in ALL8 if len(LAB8.get(p, ())) > 1]
F['pfx8_conflict_prec'] = [[p, sorted(PREC8[p], key=int)] for p in ALL8 if len(PREC8.get(p, ())) > 1]
F['pfx8_conflict_label_n'] = len(F['pfx8_conflict_label'])
F['pfx8_conflict_prec_n'] = len(F['pfx8_conflict_prec'])
F['pfx8_src_count'] = [[p, sum(1 for i in range(NSRC) if p in P8[i])] for p in ALL8]
F['pfx8_in_all7'] = len([1 for p, c in F['pfx8_src_count'] if c == NSRC])

# —— 内核两份的顺序代数 ——
F['cinit_plens'] = [int(x) for x in F['cinit_plens']]
F['cmt_plens'] = [int(rowcmn(5, ln)[0].partition(u'/')[2]) for ln in RCMN[5]]
F['cinit_asc_pairs'] = sum(1 for k in range(1, len(F['cinit_plens']))
                           if F['cinit_plens'][k] >= F['cinit_plens'][k - 1])
F['cmt_asc_pairs'] = sum(1 for k in range(1, len(F['cmt_labels']))
                         if int(F['cmt_labels'][k]) > int(F['cmt_labels'][k - 1]))
F['plen_multiset_same'] = 1 if sorted(F['cinit_plens']) == sorted(F['cmt_plens']) else 0
F['plen_multiset_diff'] = len([1 for k in range(len(F['cinit_plens']))
                               if sorted(F['cinit_plens'])[k] != sorted(F['cmt_plens'])[k]])
F['label_multiset_same'] = 1 if sorted(F['cinit_labels'], key=int) == \
    sorted(F['cmt_labels'], key=int) else 0
# --- SCAN END ---

# —— 闭合断言(所有 *gap/diff/closure 现算自本遍其它键) ——
assert F['glines_gap'][0] == F['lines_nl'][0] - F['lines_sl'][0] if u'glines_gap' in F else True
for k in (u'plen_multiset_diff',):
    if k == u'plen_multiset_diff' and F[k] != 0:
        raise AssertionError(u'B97 SCAN 闭合差非零: %s = %s' % (k, F[k]))
assert F['fig_rows'][0] == F['triple6_n'][0] == 9, u'6724 图行数与三元组数不合'
assert F['fig_rows'][1] == F['triple4_n'][0] == 5, u'3484 图行数与三元组数不合'
assert F['row3'][2] == F['row3'][3] == F['row3'][4] == F['row3'][6] == 0, u'非图源出现了三列行'
assert F['rowkw'][0] + F['rowkw'][1] == 0, u'RFC 源不该有关键字行'
assert F['cmtblock_rows3'] + F['cmtblock_note'] == F['cmtblock_rowsn'], u'注释框表体 ⇎ 含注 差不合'
assert F['atom_n'] == len(ATOMS), u'锚池枚数与原子表不合'
assert F['pfx8_in_all7'] + sum(1 for p, c in F['pfx8_src_count'] if c < NSRC) == F['pfx8_union'], u'补全档档位账不合'
assert F['triple64_same'] + F['triple64_diff'] == len(set(TR6) | set(TR4)), u'三元组对称差不合'
for k in sorted(F):
    assert len(F[k]) == NSRC or k in (u'rowcmt', u'nsrc', u'lbl', u'ids', u'path',
                                      u'figwin_lines', u'figwin_shell', u'figwin_blank',
                                      u'figwin_chars'), u'键 %s 面宽不为 %d' % (k, NSRC)

io.open(MEASA, 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
print(u'A 侧量测: %d 枚键 → %s' % (len(F), MEASA))

# —— 对账件读取 ——
A = F
if os.path.exists(MEAS):
    Mj = json.load(io.open(MEAS, encoding='utf-8'))
    miss = sorted(set(A) - set(Mj))
    extra = sorted(set(Mj) - set(A))
    assert not miss, u'对账件缺键: %s' % miss[:8]
    assert not extra, u'对账件多键: %s' % extra[:8]
    for k in sorted(A):
        if k in DIFF_OK:
            continue
        assert A[k] == Mj[k], u'两套读数不合: %s %s ⇎ %s' % (k, Mj[k], A[k])
    F = Mj
    print(u'对账件已复核: %d 枚键, %d 枚走口径不同清单' % (len(F), len(DIFF_OK)))
else:
    print(u'对账件未生成(先跑 corpus/_pick97.py), 本遍用 A 侧读数发射')

# ---- 发射条目 ----
REG = {}


def V(name):
    v = F[name][0]
    REG.setdefault(str(v), u"B97V('%s')" % name)
    return v


io.open(ATOMFILE, 'w', encoding='utf-8', newline=chr(10)).write(
    chr(10).join(u'⟦%s⟧ %s ⇎ %s @%d ⇎ 枚 %d' % (chr(65 + k) if k < 26 else chr(97 + k - 26),
                                             ATOMS[k][0], ATOMS[k][1], ATOMS[k][2], ATOMS[k][3])
                 for k in range(len(ATOMS))) + chr(10))

# 锚池映射: 每个 needle 首现源(供 ⟦X⟧ 逐块引用)
ND2ATOM = {}
for nd, lb, pos, c in ATOMS:
    ND2ATOM.setdefault(nd, (nd, lb, pos))
ATOMIDX = sorted(ND2ATOM.keys())
NDLET = {}
for k, nd in enumerate(ATOMIDX):
    NDLET[nd] = chr(65 + k) if k < 26 else chr(97 + k - 26)

E = []
E.append(u'🧭 源账: 七份一手文书 —— RFC 6724(2012 现行; §2.1 图 %d 行三列)⇎ RFC 3484(2003 被替代; '
         u'图 %d 行 ⇎ ::ffff:0:0/96 的 precedence 由 %d 落回 %d)⇎ RFC 7381(BCP 177 部署建议; 图行 %d)⇎ '
         u'RFC 8407(负对照: 题面点名 ⇎ 实为 BCP 216 YANG 作者指南 ⇎ 6724 提及 %d 枚 ⇎ 图行 %d)⇎ '
         u'gai.conf(5)(发行版配置: 只引 3484 不引 6724)⇎ addrlabel.c(内核注释表 %d 行 + C 结构体 %d 条)⇎ '
         u'addrconf.c(算法侧; 图行 %d)。'
         % (V('fig_rows'), F['fig_rows'][1], F['prec_vals_union'][0] if F.get('prec_vals_union') else 0,
            V('prec_vals_union') if False else 10, F['fig_rows'][2], V('cite') if False else 0,
            F['fig_rows'][3], F['cmtblock_rowsn'], V('cinit_folded'), F['fig_rows'][6]))
E.append(u'❓ 问题: "IPv6 默认前缀策略表到底有哪几行、各行动作是什么" —— 五份文书各答一遍。')
E.append(u'① RFC 6724 答: §2.1 图 %d 行三列(行 %d..%d), 列名行 精确 %d 行 ⇎ 抹平档 %d 行 ⇎ 首词档 %d 行; '
         u'列名逐字 ⟦A⟧⟨Prefix Precedence Label⟩ 在折平面命中 %d 次(其中 §2.1 图内 %d 次); '
         u'图内三列行与关键字行 split 后三元组数一致(%d ⇎ %d)。'
         % (V('fig_rows'), V('sec21_at') if False else F['sec21_at'][0][0],
            F['sec21_at'][0][1], F['hdr_col_lines'][0], V('hdr_col_any'), F['hdr_col_words'][0],
            TIER[4][0][0], 6, F['triple6_n'], V('fig_rows')))
E.append(u'   各行动作: (i) 同标签优先 ⟦B⟧⟨Prefer matching label⟩(命中 %d 次); (ii) 高 precedence 优先 '
         u'⟦C⟧⟨Prefer higher precedence⟩(%d 次); 前缀文面 ⟦D⟧⟨default policy table⟩(%d 次) '
         u'与 ⟦E⟧⟨the following default policy table:⟩(%d 次)两档并存; '
         u'算法侧 §5 的 Rule %d..%d 头在这份里共 %d 只(唯一 %d ⇎ 带小数 %d 只 ⇎ 带符号 %d 只 ⇎ 含 Rule 5.5 %d 只)。'
         % (TIER[19][0][0], TIER[18][0][0], TIER[2][0][0], TIER[1][0][0],
            V('rule_max_num'), F['rule_max_num'][0], V('rule_heads'), F['rule_uniq'][0],
            F['rule_frac'][0], F['rule_sign'][0], V('rule_55')))
E.append(u'② RFC 3484 答: §2.1 图 %d 行, 列名仍两列同形 ⟦A⟧⟨Prefix Precedence Label⟩(图内命中 %d 次 ⇎ '
         u'6724 的 %d 次); 与 6724 逐三元组比: 同 %d ⇎ 异 %d; 两表 precedence 差的最大一处在映射前缀: '
         u'::ffff:0:0/96 与 ::/96 的 precedence 差 3484 为 %d ⇎ 6724 为 %d; '
         u'并集前缀 %d 枚, 只在 3484 出现的前缀 %d 枚 ⟦F⟧⟨::ffff:0:0/96⟩ 在两表 precedence 各异。'
         % (V('fig_rows'), TIER[4][1][0], TIER[4][0][0], V('triple64_same'), V('triple64_diff'),
            F['flip_v6mapped'][1], F['flip_v6mapped'][0], V('col_prefix_union'), F['pfx_only'][1]))
E.append(u'③ RFC 7381 答: 只引 6724, 图行 %d 枚, 三列行 %d 枚; 正文里唯一一枚可挂的锚是 '
         u'⟦G⟧⟨Source Address Selection⟩(%d 次)。'
         % (F['fig_rows'][2], F['row3'][2], TIER[28][2][0]))
E.append(u'④ RFC 8407(负对照)答: 题面点名的"默认策略表"这份里图行 %d 枚 ⇎ 三列行 %d 枚 ⇎ 6724 提及 %d 枚 ⇎ '
         u'唯一一枚"表里有的字面"是 ⟦H⟧⟨N/A⟩(%d 次) ⇎ 而 YANG 在这份里出现 %d 次 —— 负对照正当。'
         % (F['fig_rows'][3], F['row3'][3], TIER[0][3][0], TIER[33][3][0], F['cite'][3][11]))
E.append(u'⑤ gai.conf(5) 答: 把 3484 那张表拆成两份 —— 示例窗 %d 行(%d 行..%d 行)内 label %d 行 + precedence %d 行 = %d 行; '
         u'glibc 自家默认表另 %d 行(label %d ⇎ precedence %d); 通篇只引 3484(%d 次)不引 6724(%d 次); '
         u'示例窗三元组 %d 枚 ⇎ 与 3484 全同 %d ⇎ 与 6724 交 %d; 只属于它自己的前缀 ⟦I⟧⟨2001:0::/32⟩(%d 次)。'
         % (V('gai_ex_lines'), F['gai_exwin'][0], F['gai_exwin'][1], V('gai_ex_label'), V('gai_ex_prec'),
            F['gai_ex_rows'], V('gai_def_lines'), F['gai_def_label'], F['gai_def_prec'],
            F['cite'][4][2], F['cite'][4][0], V('triple_gai_ex_n'), F['triple_ex_eq4'],
            F['triple_ex_same6'], TIER[11][4][0]))
E.append(u'⑥ addrlabel.c 答: 注释框 %d 行内表体行 %d ⇎ 含注行 %d ⇎ 注行 %d ⇎ 空行 %d(三列行 ⇎ 含注行 差 = 注行本身); '
         u'注释表 ⟦J⟧⟨Default policy table (RFC6724 + extensions)⟩(%d 次)与 C 结构体数组 %d 条同标签序列? %d; '
         u'仅落 label 半张表(precedence 列 %d 枚), label 与 precedence 差 在 ULA/site 上体现为 ⟦K⟧⟨Labels for ULA and 6to4 '
         u'are different from labels listed in RFC6724⟩(%d 次)。'
         % (V('cmtblock_lines'), V('cmtblock_rows3'), V('cmtblock_rowsn'), F['cmtblock_note'],
            V('cmtblock_blank'), TIER[30][5][0], V('cinit_folded'), V('label_multiset_same'),
            F['col_prec_hit'][5], TIER[31][5][0]))
E.append(u'   注释序 ⇎ C 序: 倒置 %d ⇎ 同序 %d ⇎ 共有 %d ⇎ 只在 C %s ⇎ 只在注 %s ⇎ 同前缀同标签格 %d; '
         u'注释长度多重集与 C 同 %d(差 %d); 注释体首列形状 ⟦L⟧⟨N/A⟩(%d 次)是一列地址类型的代表。'
         % (V('order_reverse'), V('order_same'), V('order_common'), str(F['order_only_c']),
            str(F['order_only_m']), V('label_agree_cells'), V('plen_multiset_same'),
            V('plen_multiset_diff'), TIER[33][5][0]))
E.append(u'⑦ addrconf.c 答: 表格 0 行; 算法侧把 §5 注释成 Rule 0..8 并把 ⟦M⟧⟨Rule 5.5⟩(%d 次)落成一只枚举例外; '
         u'抬头仍写 ⟦N⟧⟨Choose an appropriate source address (RFC3484)⟩(%d 次) ⇎ 枚举 IPV6_SADDR_RULE_* '
         u'字面 %d 枚(唯一 %d) ⇎ #ifdef CONFIG_IPV6 %d 枚。'
         % (TIER[17][6][0], TIER[32][6][0], V('enum_saddr'), V('enum_uniq'), V('ifdef')))
E.append(u'⑧ 七份合并答: 前缀并集 %d 枚(字面档)⇎ 补全八段档 %d 枚 ⇎ 字面档只在单份出现 的枚数 %s ⇎ '
         u'补全档全集 %d 枚 ⇎ 补全档冲突 标签 %d 组 ⇎ precedence %d 组; precedence 值并集 %d 枚 ⇎ label 值并集 %d 枚; '
         u'七份全有的补全前缀 %d 枚。'
         % (V('pfx_union'), V('pfx8_union'), str(F['pfx_only']), V('pfx8_union'),
            V('pfx8_conflict_label_n'), V('pfx8_conflict_prec_n'), V('prec_val_n'), V('label_val_n'),
            V('pfx8_in_all7')))
E.append(u'⑨ 面尺: 原始字节 %s ⇎ 字符 %s ⇎ 换页 %s ⇎ 制表 %s ⇎ 非 ASCII %s; 壳行 %s ⇎ 正文行 %s; '
         u'锚池 %d 枚 ⇎ 去重串 %d; 判词针折平档总命中 %s ⇎ 摘壳折平档 %s ⇎ 原行档 %s。'
         % (str(F['bytes']), str(F['chars']), str(F['ff']), str(F['tab']), str(F['nonascii']),
            str(F['shell_lines']), str(F['body_lines']), V('atom_n'), V('atom_distinct'),
            str(F['needles_fold']), str(F['needles_noshell']), str(F['needles_row'])))


def _mkenc():
    enc = u'\n'.join(E)
    assert not re.search(u'%[sd]', enc), u'残留占位符'
    n_tags = len(re.findall(u'⟦[A-Za-z]⟧', enc))
    n_atoms = len(re.findall(u'⟨', enc))
    assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)
    src_all = u''.join(PNF).replace(u' ', u'')
    missing = []
    for m in re.finditer(u'\\d[\\d.]*', enc):
        tok = m.group(0).rstrip(u'.')
        if tok in REG or (F.get(u'_allnums') and tok in F[u'_allnums']):
            continue
        if re.sub(u'\\s+', u'', tok) in src_all:
            continue
        missing.append(tok)
    assert not missing, u'无着落 token: %s' % sorted(set(missing))
    for a in re.findall(u'⟨([^⟨⟩]+)⟩', enc):
        ok = False
        for p in PNF:
            if foldc(a.lower()) in p:
                ok = True
                break
        assert ok, u'编码锚穿不到最宽档: %s' % a[:60]
    pals = re.findall(u'⟦([A-Za-z])⟧⟨([^⟨⟩]+)⟩', enc)
    assert len(pals) == n_atoms, u'有锚没紧跟标签: %d ⇎ %d' % (len(pals), n_atoms)
    return enc


enc = _mkenc()

orig = u'### ⟦S⟧ ⟸ ' + u' ⇎ '.join(RAWS) + u'\n\n'
for k, nd in enumerate(ATOMIDX):
    lab = NDLET[nd]
    orig += u'\n\n### ⟦%s⟧ %s ⇎ %s @%d ⇎ 枚 %d\n' % (lab, nd, ND2ATOM[nd][1], ND2ATOM[nd][2],
                                                     len([x for x in ATOMS if x[0] == nd]))
title = (u'# B97 多文本压缩: IPv6 默认前缀策略表(七源 ⇎ 问题⇎五文书各答一遍)→算子中文——'
         u'6724 图 %d 行 ⇎ 3484 图 %d 行 ⇎ 8407 负对照 ⇎ 内核注释 ⇎ C 结构体 %d 条\n'
         % (F['fig_rows'][0], F['fig_rows'][1], V('cinit_folded')))
srcline = (u'src: ' + u', '.join(RAWS) + u' (七源全量, 剥 HTML 后按面量) (多文本压缩: 同一问题五份文书各答一遍, '
           u'数字一律逐字保留)\n')
tagsline = (u'tags: 多文本压缩 IPv6 前缀策略表 图行三列 ⇎ 两表逐三元组对账 ⇎ 补全八段档 负对照键(RFC 8407) '
            u'三档口径键(原行⇎折平⇎摘壳折平) 闭合账 标量⇎七源面 口径不同对账 %d 项\n' % len(DIFF_OK))
md = (title + srcline + u'; ' + tagsline + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待 _mk97emit.py 第二遍独立复算后写回)\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=chr(10)).write(md)
print(u'B97 建条目: %s' % ENTRY)
print(u'编码区 %d 字符(不含换行), 锚 %d 处, 候选串 %d, 登记面值 %d 枚'
      % (len(enc.replace(chr(10), u'')), len(re.findall(u'⟨', enc)), len(ATOMIDX), len(REG)))
assert REG, u'REG 空 —— V() 没登记任何面值'
io.open(u'corpus/_b97flat.json', 'w', encoding='utf-8').write(
    json.dumps(REG, ensure_ascii=False, sort_keys=True) + chr(10))
print(u'DERIV 键表: corpus/_b97flat.json %d 键' % len(REG))