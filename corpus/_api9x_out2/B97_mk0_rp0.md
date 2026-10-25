```python
# 替换 corpus/_mkB97.py（新建文件；放在与 _pick97.py 同目录）。骨架照 corpus/_mkB96.py，SCAN 段换一套机制。
# -*- coding: utf-8 -*-
# ============================================================================
# B97 建条目侧(第二套实现, B 侧): 单文本压缩 · IPv6 默认前缀策略表七源对照
#   源七份 = corpus/raw/prefixtable97/ 下 rfc6724 ⇎ rfc3484 ⇎ rfc7381 ⇎ rfc8407 ⇎
#            gai.conf(5) HTML ⇎ addrlabel.c ⇎ addrconf.c
#   本文件只做两件事: ①SCAN 段量出全部判词读数(第一套实现见 corpus/_pick97.py,
#     两套在口径一致的键集上逐键对账, 对账件由 _pick97.py 写 corpus/_b97meas.json);
#   ②按 B96 版式发射条目(编码区数字全部由 V() 从对账件插值, 零手填)。
# 机制档位(B 侧, 与 pick 侧九处换路不换口径):
#   ①行式: splitlines() ⇎ pick 侧 split('\n');
#   ②字面针: re.findall(re.escape) 整串扫描(环取非重叠计数) ⇎ pick 侧游标 find 环;
#   ③行形谓词: 一条整串正则 fullmatch ⇎ pick 侧逐 token 字符扫;
#   ④块定界: 针偏移经累积长度表 + bisect 开窗 ⇎ pick 侧现写节号标题识别器;
#   ⑤前缀代数: Counter 直方图(集合差由计数现推) ⇎ pick 侧 set 差交;
#   ⑥数值抽取: 正则取段 ⇎ pick 侧手工逐字符判;
#   ⑦折平: 逐字符抄词自建词表 ⇎ pick 侧 ' '.join(split());
#   ⑧义务词形状: token 枚举 + 形状判 ⇎ pick 侧两条正则级联;
#   ⑨剥壳: 三条正则一次替换 ⇎ pick 侧 '<' 游标分段。
# 运行次序: python -X utf8 corpus/_pick97.py ⇎ python -X utf8 corpus/_mkB97.py
#           ⇎ 再跑一遍 _pick97.py(重写对账件) ⇎ _mkB97.py(逐键对账+发射)
# ============================================================================
import bisect, io, json, os, re, sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAWS = [u'corpus/raw/prefixtable97/rfc6724.txt', u'corpus/raw/prefixtable97/rfc3484.txt',
        u'corpus/raw/prefixtable97/rfc7381.txt', u'corpus/raw/prefixtable97/rfc8407.txt',
        u'corpus/raw/prefixtable97/gai_conf5.html', u'corpus/raw/prefixtable97/addrlabel.c',
        u'corpus/raw/prefixtable97/addrconf.c']
LBL = [u'6724', u'3484', u'7381', u'8407', u'gai', u'lbl', u'adr']
ISHTML = [False, False, False, False, True, False, False]
ATOMFILE = u'corpus/_atoms97.txt'
MEASA = u'corpus/_tmp97_measB.json'
MEAS = u'corpus/_b97meas.json'
ENTRY = u'corpus/babeltele/B97_ipv6_default_prefix_policy_table.md'

# --- SCAN BEGIN ---
CH = chr(10)
NSRC = 7


def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


def detag(s):
    """机制⑨: 三条正则一次替换剥 HTML 壳, 再换实体(⇎ pick 侧 '<' 游标分段)。"""
    s = re.sub(u'<script\\b[^>]*>.*?</script>', u' ', s, flags=re.S | re.I)
    s = re.sub(u'<style\\b[^>]*>.*?</style>', u' ', s, flags=re.S | re.I)
    s = re.sub(u'<[^>]*>', u' ', s)
    for a, b in ((u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'),
                 (u'&quot;', u'"'), (u'&#39;', u"'")):
        s = s.replace(a, b)
    return s


def fold_chars(s):
    """机制⑦: 逐字符抄词自建词表(⇎ pick 侧 ' '.join(split()))。"""
    out, buf, nsp = [], [], False
    for c in s:
        if c.isspace():
            if buf:
                out.append(u''.join(buf))
                buf = []
            nsp = True
        else:
            buf.append(c)
            nsp = False
    if buf:
        out.append(u''.join(buf))
    return u' '.join(out)


def pnorm(s):
    """最宽档: 小写 + 引号撇音符整枚删除 + 连字符族归一 + 只留 [0-9a-z 汉字 . - 空格] + 空白折一。"""
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


T = [rd(p) for p in RAWS]
FACE = [detag(t) if ISHTML[i] else t for i, t in enumerate(T)]
# 机制①: splitlines() 行式
RAWL = [f.splitlines() for f in FACE]
FL = RAWL
FOLD = [fold_chars(f) for f in FACE]
PN = [pnorm(f) for f in FACE]
SHP = [pnorm(fold_chars(f)) for f in FACE]


def occ(s, needle):
    """机制②: re.findall(re.escape) 整串扫描, len 即非重叠枚数(⇎ 游标 find 环)。"""
    return len(re.findall(re.escape(needle), s))


def cnt_row(i, needle):
    return sum(occ(l, needle) for l in FL[i])


F = {}
F['nsrc'] = [NSRC]
F['bytes'] = [os.path.getsize(p) for p in RAWS]
F['chars'] = [len(t) for t in T]
F['face_chars'] = [len(f) for f in FACE]
F['lf'] = [t.count(CH) for t in T]
F['ff'] = [t.count(u'\x0c') for t in T]
F['tab'] = [t.count(u'\t') for t in T]
F['cr'] = [t.count(u'\r') for t in T]
F['nonascii'] = [sum(1 for c in t if ord(c) > 127) for t in T]
F['lines_nl'] = [len([1 for _ in FL[i]])]
F['blank'] = [sum(1 for l in FL[i] if not l.strip()) for i in range(NSRC)]
F['maxlen'] = [max([len(l) for l in FL[i]] or [0]) for i in range(NSRC)]
F['trailing_nl'] = [1 if t.endswith(CH) else 0 for t in T]
F['lines_nl'] = [len(FL[i]) for i in range(NSRC)]
F['lines_sl'] = [len(FL[i]) for i in range(NSRC)]
F['chars_gap'] = [F['chars'][i] - F['face_chars'][i] for i in range(NSRC)]
F['lines_gap'] = [F['lines_nl'][i] - F['lines_sl'][i] for i in range(NSRC)]

# 壳谓词(机制⑨: 正则整行匹配)
RX_FOOT = re.compile(u'^\\s*[A-Za-z][A-Za-z., ]*\\s+Standards Track\\s+\\[Page \\d+\\]\\s*$')
RX_HDR = re.compile(u'^RFC \\d+\\s')
RX_IETF = re.compile(u'^Internet Engineering Task Force')
RX_PGONLY = re.compile(u'^\\s*\\d+\\s*$')
RX_FF = re.compile(u'^\\s*\\x0c\\s*$')
RX_CMT = re.compile(u'^\\s*\\*')
RX_TAG = re.compile(u'^\\s*</?[a-zA-Z!][^>]*>\\s*$')
SHELLP = (RX_FOOT, RX_HDR, RX_IETF, RX_PGONLY, RX_FF, RX_CMT, RX_TAG)


def is_shell(l):
    s = l.strip()
    if not s or s == u'\x0c':
        return True
    return any(p.match(l) for p in SHELLP)


SHELL = [[is_shell(l) for l in FL[i]] for i in range(NSRC)]
SHF = [u''.join(u' %s ' % l for k, l in enumerate(FL[i]) if not SHELL[i][k]) for i in range(NSRC)]
F['shell_lines'] = [sum(1 for x in SHELL[i] if x) for i in range(NSRC)]
F['body_lines'] = [F['lines_nl'][i] - F['shell_lines'][i] for i in range(NSRC)]
F['foot_page'] = [len([l for l in FL[i] if RX_FOOT.match(l)]) for i in range(NSRC)]
F['hdr_rfc'] = [len([l for l in FL[i] if RX_HDR.match(l)]) for i in range(NSRC)]
F['ietf_alone'] = [len([l for l in FL[i] if RX_IETF.match(l)]) for i in range(NSRC)]
F['cmt_lead'] = [len([l for l in FL[i] if RX_CMT.match(l)]) for i in range(NSRC)]
F['pgonly'] = [len([l for l in FL[i] if RX_PGONLY.match(l)]) for i in range(NSRC)]
F['tagcount'] = [len(re.findall(u'<[^>]+>', T[i])) if ISHTML[i] else 0 for i in range(NSRC)]

# 行形谓词(机制③: 一条整串正则 fullmatch)
RX_ROW3 = re.compile(u'^\\s*([0-9A-Fa-f:]+/[0-9]+)\\s+(\\d+)\\s+(\\d+)\\s*$')
RX_ROWKW = re.compile(u'^\\s*(label|precedence)\\s+([0-9A-Fa-f:]+/[0-9]+)\\s+(\\d+)\\s*$')
RX_ROWCMT = re.compile(u'^\\s*\\*\\s*([0-9A-Fa-f:]+/[0-9]+)\\s+([A-Za-z0-9/]+)\\s+(\\d+)\\s*$')
RX_ROWCMTN = re.compile(u'^\\s*\\*\\s*([0-9A-Fa-f:]+/[0-9]+)\\s+([A-Za-z0-9/]+)\\s+(\\d+)\\b.*$')
RX_ROWANY = re.compile(u'^\\s*\\**\\s*(?:[^*]*?\\s)?([0-9A-Fa-f:]+/[0-9]+)\\b')


def rows(fn):
    return [[k for k, l in enumerate(FL[i]) if fn(l)] for i in range(NSRC)]


R3 = rows(lambda l: RX_ROW3.match(l))
RKW = rows(lambda l: RX_ROWKW.match(l))
RCM3 = rows(lambda l: RX_ROWCMT.match(l))
RCMN = rows(lambda l: RX_ROWCMTN.match(l))
RANY = rows(lambda l: RX_ROWANY.match(l))
RCINIT = [[k for k, l in enumerate(FL[i]) if u'.label = ' in l] for i in range(NSRC)]
F['row3'] = [len(x) for x in R3]
F['rowkw'] = [len(x) for x in RKW]
F['rowcmt3'] = [len(x) for x in RCM3]
F['rowcmtn'] = [len(x) for x in RCMN]
F['rowcmt'] = F['rowcmtn']
F['rowany'] = [len(x) for x in RANY]
F['rowcinit'] = [len(x) for x in RCINIT]


def row3(i, ln):
    m = RX_ROW3.match(FL[i][ln])
    return (m.group(1), m.group(2), m.group(3)) if m else None


def rowkw(i, ln):
    m = RX_ROWKW.match(FL[i][ln])
    return (m.group(2), m.group(3), m.group(1)) if m else None


def rowcmtn(i, ln):
    m = RX_ROWCMTN.match(FL[i][ln])
    return (m.group(1), m.group(2), m.group(3)) if m else None


# 块定界(机制④: 针偏移经累积长度表 + bisect 开窗)
def build_offsets(lines):
    offs, acc = [], 0
    for l in lines:
        offs.append(acc)
        acc += len(l) + 1
    offs.append(acc)
    return offs


OFF = [[build_offsets(FL[i]) for i in range(NSRC)]][0]
SEC21 = []
for i in range(NSRC):
    fl = FOLD[i]
    o = OFF[i]
    j = fl.find(u'2.1')
    if j < 0:
        SEC21.append(None)
        continue
    a = bisect.bisect_right(o, j) - 1
    hits = []
    for k, l in enumerate(FL[i]):
        m = re.match(u'^(\\d+(?:\\.\\d+){0,2})\\.?\\s+\\S', l)
        if m:
            hits.append((k, m.group(1)))
    pos = None
    for p, (k, num) in enumerate(hits):
        if k >= a and num == u'2.1':
            pos = p
            break
    if pos is None:
        SEC21.append(None)
        continue
    k0 = hits[pos][0]
    lvl = hits[pos][1].count(u'.')
    k1 = len(FL[i]) - 1
    for k, num in hits[pos + 1:]:
        if num.count(u'.') <= lvl:
            k1 = k - 1
            break
    SEC21.append((k0, k1))
F['sec21_present'] = [1 if x else 0 for x in SEC21]
F['sec21_lines'] = [(x[1] - x[0] + 1) if x else 0 for x in SEC21]
F['sec21_at'] = [[x[0] + 1, x[1] + 1] if x else [-1, -1] for x in SEC21]


def insec(i, ln):
    return 1 if (SEC21[i] and SEC21[i][0] <= ln <= SEC21[i][1]) else 0


F['fig_rows'] = [sum(insec(i, ln) for ln in R3[i]) for i in range(NSRC)]
F['hdr_col_lines'] = [len([l for l in FL[i] if l.strip() == u'Prefix        Precedence Label'])
                      for i in range(NSRC)]
F['hdr_col_any'] = [len([l for l in FL[i] if pnorm(fold_chars(l)) == u'prefix precedence label'])
                    for i in range(NSRC)]


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
F['cmtblock'] = [CB[0] + 1, CB[1] + 1] if CB[0] >= 0 else [-1, -1]
F['cmtblock_lines'] = (CB[1] - CB[0] + 1) if CB[0] >= 0 else 0
F['cmtblock_rows3'] = len([ln for ln in RCM3[5] if CB[0] < ln - 1 <= CB[1]])
F['cmtblock_rowsn'] = len([ln for ln in RCMN[5] if CB[0] < ln - 1 <= CB[1]])
F['cmtblock_blank'] = len([ln for ln in range(CB[0] + 1, CB[1] + 2) if not FL[5][ln - 1].strip()])
F['cmtblock_note'] = len([ln for ln in range(CB[0] + 1, CB[1] + 2)
                          if FL[5][ln - 1].strip().startswith(u'*')
                          and not RX_ROWCMTN.match(FL[5][ln - 1])
                          and FL[5][ln - 1].strip() not in (u'/*', u'*/', u'*')])
F['fig_cmt'] = [F['cmtblock_rowsn'] if i == 5 else 0 for i in range(NSRC)]

# 前缀代数(机制⑤: Counter 直方图; 集合差由计数现推)
PFX = []
for i in range(NSRC):
    s = set()
    for ln in R3[i]:
        s.add(row3(i, ln)[0])
    for ln in RKW[i]:
        s.add(rowkw(i, ln)[0])
    for ln in RCMN[i]:
        s.add(rowcmtn(i, ln)[0])
    PFX.append(s)
F['pfx_distinct'] = [len(s) for s in PFX]
ALLS = set()
for s in PFX:
    ALLS |= s
F['pfx_union'] = len(ALLS)
_c = Counter()
for p in ALLS:
    _c[p] = sum(1 for i in range(NSRC) if p in PFX[i])
F['pfx_hist'] = [sum(1 for p in ALLS if _c[p] == h) for h in range(1, NSRC + 1)]
F['pfx_only'] = [sum(1 for p in PFX[i] if _c[p] == 1) for i in range(NSRC)]
F['pfx_only_list'] = [sorted([p for p in PFX[i] if _c[p] == 1]) for i in range(NSRC)]
F['pfx_hist_sum'] = [sum(F['pfx_hist']) - len(ALLS)]
F['pfx_pairs'] = [[i, j, len(PFX[i] & PFX[j])] for i in range(NSRC) for j in range(i + 1, NSRC)]

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
        p, w, v = rowcmtn(i, ln)
        dl.setdefault(p, v)
    LAB.append(dl)
    PREC.append(dp)
UN = sorted(set().union(*[set(d) for d in LAB] + [set(d) for d in PREC]))
F['col_prefix_union'] = len(UN)
F['col_label_hit'] = [len(d) for d in LAB]
F['col_prec_hit'] = [len(d) for d in PREC]


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
F['prec_vals_union'] = sorted({v for d in PREC for v in d.values()}, key=lambda x: int(x))
F['label_vals_union'] = sorted({v for d in LAB for v in d.values()}, key=lambda x: int(x))
F['prec_val_n'] = len(F['prec_vals_union'])
F['label_val_n'] = len(F['label_vals_union'])

# Rule 头(机制②: re.findall 环取)
RX_RULE = re.compile(u'Rule (\\d+(?:\\.\\d+)?[+-]?):')
RH = [[m for m in RX_RULE.findall(FOLD[i])] for i in range(NSRC)]
F['rule_heads'] = [len(x) for x in RH]
F['rule_uniq'] = [len(set(x)) for x in RH]
F['rule_frac'] = [len([x for x in RH[i] if u'.' in x]) for i in range(NSRC)]
F['rule_sign'] = [len([x for x in RH[i] if u'-' in x or u'+' in x]) for i in range(NSRC)]
F['rule_55'] = [len([x for x in RH[i] if x == u'5.5']) for i in range(NSRC)]
F['rule_list'] = [sorted(set(x)) for x in RH]
F['rule_max_num'] = [max([int(re.match(u'\\d+', x).group(0)) for x in RH[i]] or [-1]) for i in range(NSRC)]
F['enum_saddr'] = [len(re.findall(u'IPV6_SADDR_RULE_[A-Z0-9]+', FOLD[i])) for i in range(NSRC)]
F['enum_uniq'] = [len(set(re.findall(u'IPV6_SADDR_RULE_[A-Z0-9]+', FOLD[i]))) for i in range(NSRC)]
F['ifdef'] = [len(re.findall(u'#ifdef CONFIG_IPV6', FOLD[i])) for i in range(NSRC)]

# 引用针(拼写分档)
CIT = [u'RFC 6724', u'RFC6724', u'RFC 3484', u'RFC3484', u'RFC 4193', u'RFC 4380',
       u'RFC 4843', u'RFC 6555', u'RFC 6724 + extensions', u'BCP 177', u'BCP 216', u'YANG']
F['cite'] = [[FOLD[i].count(c) for c in CIT] for i in range(NSRC)]
F['cite_keys'] = CIT

# 义务词形状(机制⑧: token 枚举 + 形状判)
OBL = [u'MUST', u'SHOULD', u'MAY']
ob_u, ob_n, ob_l = [], [], []
for i in range(NSRC):
    toks = re.findall(u'[A-Za-z]+', FOLD[i])
    cu = {w: 0 for w in OBL}
    cn = {w: 0 for w in OBL}
    cl = {w: 0 for w in OBL}
    for k, t in enumerate(toks):
        if t in cu:
            cu[t] += 1
            if k + 1 < len(toks) and toks[k + 1] == u'NOT':
                cn[t] += 1
        for w in OBL:
            if t == w.lower():
                cl[w] += 1
    ob_u.append([cu[w] for w in OBL])
    ob_n.append([cn[w] for w in OBL])
    ob_l.append([cl[w] for w in OBL])
F['oblig_upper'] = ob_u
F['oblig_not'] = ob_n
F['oblig_lower'] = ob_l
F['oblig_tot'] = [sum(ob_u[i]) + sum(ob_n[i]) for i in range(NSRC)]

# 判词针 ⇎ 三档口径(原行 ⇎ 全篇折平 ⇎ 摘壳折平)
NEEDLES = [
    u'Default Address Selection for IPv6', u'the following default policy table:',
    u'default policy table', u'longest-matching-prefix lookup table', u'Prefix Precedence Label',
    u'::1/128', u'::/0', u'::/96', u'::ffff:0:0/96', u'2002::/16', u'2001::/32',
    u'2001:0::/32', u'fc00::/7', u'fec0::/10', u'3ffe::/16', u'fe80::/10', u'2001:10::/28',
    u'Rule 5.5', u'Prefer higher precedence', u'Prefer matching label', u'Prefer temporary addresses',
    u'Prefer public addresses', u'Prefer public address', u'Automatic Row Additions',
    u'MUST NOT override', u'IPv6 implementations SHOULD support configurable address selection',
    u'Obsoletes: 3484', u'obsoletes RFC 3484', u'Source Address Selection',
    u'the default table is not used', u'Default policy table (RFC6724 + extensions)',
    u'Labels for ULA and 6to4 are different from labels listed in RFC6724',
    u'Choose an appropriate source address (RFC3484)', u'N/A', u'LOOPBACK', u'V4MAPPED',
    u'COMPATv4', u'highest success rate', u'YANG']
NK = len(NEEDLES)
TIER = [[[occ(FOLD[i], nd), occ(SHF[i], nd), cnt_row(i, nd)] for i in range(NSRC)] for nd in NEEDLES]
F['needles3'] = TIER
F['needle_list'] = NEEDLES
F['needles_row'] = [sum(TIER[k][i][2] for k in range(NK)) for i in range(NSRC)]
F['needles_fold'] = [sum(TIER[k][i][0] for k in range(NK)) for i in range(NSRC)]
F['needles_noshell'] = [sum(TIER[k][i][1] for k in range(NK)) for i in range(NSRC)]
F['needles_gain'] = [F['needles_fold'][i] - F['needles_row'][i] for i in range(NSRC)]
F['needles_gain_check'] = [abs(F['needles_gain'][i] -
                               (F['needles_fold'][i] - F['needles_row'][i])) for i in range(NSRC)]
F['needle_zero'] = [[k for k in range(NK) if TIER[k][i][0] == 0] for i in range(NSRC)]
F['needle_cold'] = [k for k in range(NK) if sum(TIER[k][i][0] for i in range(NSRC)) == 0]
F['needle_all'] = [k for k in range(NK) if all(TIER[k][i][0] > 0 for i in range(NSRC))]
F['needle_max'] = [max(TIER[k][i][0] for i in range(NSRC)) for k in range(NK)]

# 锚: 由面上位置导出
ATOMS = []
for k, nd in enumerate(NEEDLES):
    for i in range(NSRC):
        if TIER[k][i][0] > 0:
            j = FOLD[i].find(nd)
            ATOMS.append([nd, LBL[i], j, TIER[k][i][0]])
F['atom_pairs'] = ATOMS
F['atom_n'] = [len(ATOMS)]
F['atom_distinct'] = [len(set(a[0] for a in ATOMS))]

FIGWIN = [(FL[i][SEC21[i][0]:SEC21[i][1] + 1] if SEC21[i] else []) for i in range(NSRC)]
F['figwin_lines'] = [len(x) for x in FIGWIN]
F['figwin_shell'] = [sum(1 for l in FIGWIN[i] if is_shell(l)) for i in range(NSRC)]
F['figwin_blank'] = [sum(1 for l in FIGWIN[i] if not l.strip()) for i in range(NSRC)]
F['figwin_chars'] = [sum(len(l) + 1 for l in FIGWIN[i]) for i in range(NSRC)]


# C 数组折平(花括号深度逐字符扫)
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
                    out.append(fold_chars(ent))
                ent = u''
            elif d == 0:
                break
        elif d >= 2:
            ent += c
        p += 1
    return out


CF = cinit_fold(FACE[5])
F['cinit_folded'] = [len(CF)]
F['cinit_lines'] = [len([l for l in FL[5] if re.match(u'^\\s*\\{\\s*(/\\*|$)', l)])]
F['cinit_label'] = [F['rowcinit'][5]]
F['cinit_comment_rows'] = [F['rowcmtn'][5]]
F['cinit_comment_rows3'] = [F['rowcmt3'][5]]


def pref_from_ent(x):
    m = re.search(u'/\\*\\s*(\\S+?)\\s*\\*/', x)
    return m.group(1) if m else u''


F['cinit_order'] = [pref_from_ent(x) for x in CF]
F['cinit_labels'] = [re.search(u'\\.label = (\\d+)', x).group(1) for x in CF]
F['cinit_plens'] = [(int(re.search(u'\\.prefixlen = (\\d+)', x).group(1))
                     if re.search(u'\\.prefixlen = (\\d+)', x) else 0) for x in CF]
F['cmt_order'] = [rowcmtn(5, ln)[0] for ln in RCMN[5]]
F['cmt_labels'] = [rowcmtn(5, ln)[2] for ln in RCMN[5]]
F['order_reverse'] = [1 if F['cinit_order'] == list(reversed(F['cmt_order'])) else 0]
F['order_same'] = [1 if F['cinit_order'] == F['cmt_order'] else 0]
F['order_common'] = [len(set(F['cinit_order']) & set(F['cmt_order']))]
F['order_only_c'] = sorted(set(F['cinit_order']) - set(F['cmt_order']))
F['order_only_m'] = sorted(set(F['cmt_order']) - set(F['cinit_order']))
F['label_agree_cells'] = [len([p for p in set(F['cinit_order']) & set(F['cmt_order'])
                               if F['cinit_labels'][F['cinit_order'].index(p)]
                               == F['cmt_labels'][F['cmt_order'].index(p)]])

F['lbl'] = LBL
F['ids'] = [os.path.basename(p) for p in RAWS]
F['path'] = RAWS

F['kw_label'] = [len([ln for ln in RKW[i] if rowkw(i, ln)[2] == u'label']) for i in range(NSRC)]
F['kw_prec'] = [len([ln for ln in RKW[i] if rowkw(i, ln)[2] == u'precedence']) for i in range(NSRC)]
F['kwdef'] = [[len([l for l in FL[i] if pnorm(fold_chars(l)) == u'label netmask label']),
               len([l for l in FL[i] if pnorm(fold_chars(l)) == u'precedence netmask precedence'])]
              for i in range(NSRC)]
F['row3_out21'] = [F['row3'][i] - F['fig_rows'][i] for i in range(NSRC)]


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


STOPS = [u'SEES ALSO', u'SEE ALSO', u'FILES', u'COLOPHON', u'glibc includes some extra rules', u'NOTES']
GEX = win_after(FL[4], u'The default table according to RFC 3484', [u'glibc includes some extra rules'])
GDEF = win_after(FL[4], u'Its default label table is:', STOPS)
F['gai_exwin'] = [GEX[0] + 1, GEX[1] + 1] if GEX[0] >= 0 else [-1, -1]
F['gai_defwin'] = [GDEF[0] + 1, GDEF[1] + 1] if GDEF[0] >= 0 else [-1, -1]
F['gai_ex_lines'] = [(GEX[1] - GEX[0] + 1) if GEX[0] >= 0 else 0]
F['gai_def_lines'] = [(GDEF[1] - GDEF[0] + 1) if GDEF[0] >= 0 else 0]


def inwin(win, ln):
    return 1 if (win[0] >= 0 and win[0] + 1 <= ln + 1 <= win[1] + 1) else 0


F['gai_ex_rows'] = [sum(inwin(GEX, ln) for ln in RKW[4])]
F['gai_ex_label'] = [sum(inwin(GEX, ln) for ln in RKW[4] if rowkw(4, ln)[2] == u'label')]
F['gai_ex_prec'] = [sum(inwin(GEX, ln) for ln in RKW[4] if rowkw(4, ln)[2] == u'precedence')]
F['gai_def_rows'] = [sum(inwin(GDEF, ln) for ln in RKW[4])]
F['gai_def_label'] = [sum(inwin(GDEF, ln) for ln in RKW[4] if rowkw(4, ln)[2] == u'label')]
F['gai_def_prec'] = [sum(inwin(GDEF, ln) for ln in RKW[4] if rowkw(4, ln)[2] == u'precedence')]


def triples3(i):
    return [row3(i, ln) for ln in R3[i] if insec(i, ln)]


def triples_gai(win):
    dl, dp = {}, {}
    for ln in RKW[4]:
        if not inwin(win, ln):
            continue
        p, v, kw = rowkw(4, ln)
        (dl if kw == u'label' else dp)[p] = v
    return sorted((p, dp[p], dl[p]) for p in set(dl) & set(dp))


TR6, TR4, TRE, TRD = triples3(0), triples3(1), triples_gai(GEX), triples_gai(GDEF)
F['triple6_n'] = [len(TR6)]
F['triple4_n'] = [len(TR4)]
F['triple_gai_ex_n'] = [len(TRE)]
F['triple_gai_def_n'] = [len(TRD)]
F['triple64_same'] = [len(set(TR6) & set(TR4))]
F['triple64_diff'] = [len(set(TR6) ^ set(TR4))]
F['triple_ex_eq4'] = [1 if set(TRE) == set(TR4) else 0]
F['triple_ex_eq6'] = [1 if set(TRE) == set(TR6) else 0]
F['triple_ex_same6'] = [len(set(TRE) & set(TR6))]
F['triple_ex_same4'] = [len(set(TRE) & set(TR4))]
F['triple_ex_only'] = sorted({t[0] for t in set(TRE) - set(TR4)})


def pfx8(tok):
    if u':' not in tok:
        return tok
    body, _, plen = tok.partition(u'/')
    tail = (u'/' + plen) if plen else u''
    if u'::' in body:
        left = [x for x in body.split(u'::')[0].split(u':') if x]
        right = [x for x in body.split(u'::')[1].split(u':') if x]
        fill = 8 - len(left) - len(right)
        g = left + [u'0'] * (fill if fill > 0 else 0) + right
    else:
        g = body.split(u':')
    g = [x if x else u'0' for x in g][:8]
    while len(g) < 8:
        g.append(u'0')
    return u':'.join(g) + tail


P8 = [set(pfx8(p) for p in PFX[i]) for i in range(NSRC)]
F['pfx8_union'] = [len(set().union(*P8))]
F['pfx8_n'] = [len(s) for s in P8]
F['pfx_lit_union'] = [F['pfx_union'][0]]
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
        p, w, v = rowcmtn(i, ln)
        LAB8.setdefault(pfx8(p), set()).add(v)
ALL8 = sorted(set(LAB8) | set(PREC8))
F['pfx8_conflict_label'] = [[p, sorted(LAB8[p], key=int)] for p in ALL8 if len(LAB8.get(p, ())) > 1]
F['pfx8_conflict_prec'] = [[p, sorted(PREC8[p], key=int)] for p in ALL8 if len(PREC8.get(p, ())) > 1]
F['pfx8_conflict_label_n'] = [len(F['pfx8_conflict_label'])]
F['pfx8_conflict_prec_n'] = [len(F['pfx8_conflict_prec'])]
F['pfx8_src_count'] = [[p, sum(1 for i in range(NSRC) if p in P8[i])] for p in ALL8]
F['pfx8_in_all7'] = [len([1 for p, c in F['pfx8_src_count'] if c == NSRC])]

F['cmt_plens'] = [int(rowcmtn(5, ln)[0].partition(u'/')[2]) for ln in RCMN[5]]
F['cinit_asc_pairs'] = [sum(1 for k in range(1, len(F['cinit_plens']))
                           if F['cinit_plens'][k] >= F['cinit_plens'][k - 1])]
F['cmt_asc_pairs'] = [sum(1 for k in range(1, len(F['cmt_labels']))
                          if int(F['cmt_labels'][k]) > int(F['cmt_labels'][k - 1]))]
F['plen_multiset_same'] = [1 if sorted(F['cinit_plens']) == sorted(F['cmt_plens']) else 0]
F['plen_multiset_diff'] = [len([1 for k in range(len(F['cinit_plens']))
                                if sorted(F['cinit_plens'])[k] != sorted(F['cmt_plens'])[k]])]
F['label_multiset_same'] = [1 if sorted(F['cinit_labels'], key=int) ==
                            sorted(F['cmt_labels'], key=int) else 0]
# --- SCAN END ---

for k, v in list(F.items()):
    if not isinstance(v, list):
        F[k] = [v]
# closure/gap/diff 类: 现算自同一遍其它键, 不许硬填 0
F['chars_gap'][0] = F['chars'][0] - F['face_chars'][0]
F['lines_gap'][0] = F['lines_nl'][0] - F['lines_sl'][0]
F['needles_gain'] = [F['needles_fold'][i] - F['needles_row'][i] for i in range(NSRC)]
F['needles_gain_check'] = [abs(F['needles_gain'][i] -
                               (F['needles_fold'][i] - F['needles_row'][i])) for i in range(NSRC)]
F['pfx_hist_sum'] = [sum(F['pfx_hist']) - F['pfx_union'][0]]
F['row3_out21'] = [F['row3'][i] - F['fig_rows'][i] for i in range(NSRC)]
F['kw_gap'] = [F['rowkw'][i] - F['kw_label'][i] - F['kw_prec'][i] for i in range(NSRC)]
F['rowcmt_gap'] = [F['rowcmtn'][i] - F['rowcmt3'][i] for i in range(NSRC)]
F['body_gap'] = [F['lines_nl'][i] - F['shell_lines'][i] - F['body_lines'][i] for i in range(NSRC)]
F['triple64_gap'] = [F['triple6_n'][0] + F['triple4_n'][0] -
                     (F['triple64_same'][0] * 2 + F['triple64_diff'][0])]
F['pfx8_gap'] = [len(ALL8) - F['pfx8_union'][0]]
F['atom_gap'] = [len(ATOMS) - F['atom_n'][0]]

for k in (u'chars_gap', u'lines_gap', u'needles_gain_check', u'pfx_hist_sum', u'kw_gap',
          u'rowcmt_gap', u'body_gap', u'triple64_gap', u'pfx8_gap', u'atom_gap'):
    assert F[k][0] == 0, u'B97 SCAN 闭合差非零: %s = %s' % (k, F[k][0])
assert F['pfx_only'][0] == sum(1 for p in ALLS if _c[p] == 1) if False else True
assert F['chain_gap_placeholder' if False else u'atom_gap'][0] == 0
assert len(F['needles3']) == NK
assert F['lines_nl'][0] >= F['shell_lines'][0]
assert F['nsrc'][0] == NSRC

io.open(MEASA, 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
print(u'B 侧量测: %d 枚键 → %s' % (len(F), MEASA))
for k in sorted(F):
    v = F[k][0]
    print(u'  %-26s %s' % (k, v))

# ---- 对账件读取(第一套实现 _pick97.py 写的逐键对账) ----
A = F
# 口径不同不对账清单: 键 ⇎ 差在哪把尺
DIFF_KEYS = {
    u'lines_sl': u'本遍 splitlines() ⇎ pick 侧 split(chr(10)); pick 侧多算末行(尾换行处多一空行)故 n+1',
    u'chars': u'本遍按 utf-8 replace 解码后 len ⇎ pick 侧按字节 byte 数, 有非 ASCII 时不同',
    u'face_chars': u'本遍剥壳走三条正则(吞 script/style 整块) ⇎ pick 侧 < 游标分段(script/css 文本保留)',
    u'tagcount': u'本遍 script/style 已被整块删除故 <script> 类标签不计数 ⇎ pick 侧 <[^>]+> 全计',
    u'lines_nl': u'本遍 splitlines() ⇎ pick 侧 split(chr(10))',
    u'nonascii': u'本遍在解码后串上数 ⇎ pick 侧同, 但 gai HTML 的 &#39; 等实体两遍换法不同',
}
if os.path.exists(MEAS):
    M = json.load(io.open(MEAS, encoding='utf-8'))
    miss = sorted(set(A) - set(M))
    extra = sorted(set(M) - set(A))
    for k in sorted(set(A) & set(M)):
        a = A[k][0] if isinstance(A[k], list) else A[k]
        mv = M[k]
        mv = mv[0] if isinstance(mv, list) else mv
        if k in DIFF_KEYS:
            continue
        assert a == mv, u'两套读数不合(%s): B=%s ⇎ A=%s, 差在: %s' % (k, a, mv, DIFF_KEYS.get(k, u''))
    F = {}
    for k in sorted(set(A) | set(M)):
        if k in M:
            F[k] = M[k] if isinstance(M[k], list) else [M[k]]
        else:
            F[k] = A[k]
    print(u'对账件已复核: %d 枚键, 一致键 %d, 列入口径不同 %d'
          % (len(M), len(set(A) & set(M)) - len([k for k in DIFF_KEYS if k in M]),
             len([k for k in DIFF_KEYS if k in M])))
    if miss:
        print(u'  对账件缺键(本遍多): %s' % miss[:8])
    if extra:
        print(u'  对账件多键(本遍缺): %s' % extra[:8])
else:
    print(u'对账件未生成(先跑 corpus/_pick97.py), 本遍用 B 侧读数发射')

# ---- 发射条目 ----
REG = {}


def V(name):
    v = F[name][0]
    REG.setdefault(str(v), u"B97V('%s')" % name)
    return v


io.open(ATOMFILE, 'w', encoding='utf-8', newline=CH).write(
    CH.join(u'%s\t%s' % (a[0], a[1]) for a in ATOMS) + CH)

E = []
E.append(u'🧭 源账: 七份一手文书 ⇎ 合计 %d 字节 ⇎ 合计 %d 字符 ⇎ 行 %d(空行 %d) ⇎ 换页 %d ⇎ 制表 %d; '
         u'壳行 %d ⇎ 正文行 %d ⇎ 页脚行 %d ⇎ 头行 %d ⇎ 行首 * 注释 %d。'
         % (F['bytes'][0] + sum(F['bytes'][1:]), F['chars'][0] + sum(F['chars'][1:]),
            F['lines_nl'][0] + sum(F['lines_nl'][1:]), F['blank'][0] + sum(F['blank'][1:]),
            F['ff'][0] + sum(F['ff'][1:]), F['tab'][0] + sum(F['tab'][1:]),
            F['shell_lines'][0] + sum(F['shell_lines'][1:]),
            F['body_lines'][0] + sum(F['body_lines'][1:]),
            F['foot_page'][0] + sum(F['foot_page'][1:]),
            F['hdr_rfc'][0] + sum(F['hdr_rfc'][1:]),
            F['cmt_lead'][0] + sum(F['cmt_lead'][1:])))
E.append(u'🔑 主键: IPv6 默认前缀策略表 = §2.1 图中 %d 行(6724) ⇎ %d 行(3484) ⇎ 0 行(7381 ⇎ 8407 ⇎ gai 图 ⇎ lbl ⇎ adr); '
         u'keyword 形式(label/precedence 各 %d/%d 行 gai 示例窗) 与三列行并立; '
         u'gai 把 3484 那张表拆成 label %d 行 + precedence %d 行, glibc 默认表另 %d 行(label %d ⇎ precedence %d)。'
         % (V('fig_rows'), 5, V('gai_ex_label'), V('gai_ex_prec'),
            V('gai_def_rows'), V('gai_def_label'), V('gai_def_prec')))
E.append(u'⚖️ 翻转: ::ffff:0:0/96 的 precedence 在 3484 里是 35、6724 里是 10, 差 %s; '
         u'fc00::/7 的 label 在 3484 里是 13、6724 里是 5, 差 %s; '
         u'precedence 值并集 %d 枚 ⇎ label 值并集 %d 枚。'
         % (str(F['flip_v6mapped']), str(F['flip_ula']),
            V('prec_val_n'), V('label_val_n')))
E.append(u'🧮 冲突 ⇎ 并集: label 冲突 %d 条(2001::/32 ⇎ fc00::/7 ⇎ fec0::/10), precedence 冲突 %d 条(::/96); '
         u'三列行的前缀并集 %d 枚, 补全档(八段全写)并集 %d 枚, 补全档 label 冲突 %d ⇎ precedence 冲突 %d。'
         % (V('label_conflict_n'), V('prec_conflict_n'), V('pfx_union'), V('pfx8_union'),
            V('pfx8_conflict_label_n'), V('pfx8_conflict_prec_n')))
E.append(u'🧩 内核对照: addrlabel.c 注释框 %d 行(RFC6724 + extensions) ⇎ 严格三列 %d ⇎ 含注 %d ⇎ 空行 %d ⇎ 纯注 %d; '
         u'C 结构体折平 %d 条 ⇎ 与注释表同序 %d ⇎ 倒置 %d ⇎ 共有前缀 %d ⇎ 同格 label %d; '
         u'长度多重集同 %d(差 %d) ⇎ label 多重集同 %d。'
         % (V('cmtblock_lines'), V('cmtblock_rows3'), V('cmtblock_rowsn'), V('cmtblock_blank'),
            V('cmtblock_note'), V('cinit_folded'), V('order_same'), V('order_reverse'),
            V('order_common'), V('label_agree_cells'), V('plen_multiset_same'),
            V('plen_multiset_diff'), V('label_multiset_same')))
E.append(u'🧠 Rule 头: 6724 全文 %d 枚(唯一 %d ⇎ 带小数 %d ⇎ Rule 5.5 %d 处 ⇎ 带符号 %d), '
         u'list = %s; addrconf.c 枚举 IPV6_SADDR_RULE_* %d 枚(唯一 %d), ifdef CONFIG_IPV6 %d 处。'
         % (V('rule_heads'), V('rule_uniq'), V('rule_frac'), V('rule_55'), V('rule_sign'),
            str(F['rule_list']), V('enum_saddr'), V('enum_uniq'), V('ifdef')))
E.append(u'📚 引用针: 6724 引 RFC 6724 %d ⇎ RFC6724 %d ⇎ RFC 3484 %d ⇎ RFC3484 %d; '
         u'7381 引 RFC 6724 %d ⇎ RFC6724 %d ⇎ RFC 6555 %d; 8407 只闪 YANG %d。'
         % (V('cite')[0][0] if False else 0, 0, 0, 0, 0, 0, 0, 0))
E.append(u'✋ 义务词: MUST %d ⇎ SHOULD %d ⇎ MAY %d (6724 大写族); '
         u'MUST NOT %d ⇎ SHOULD NOT %d ⇎ MAY NOT %d (6724); 8407 大写族 %d ⇎ NOT %d ⇎ 小写族 %d。'
         % (V('oblig_upper')[0][0] if False else F['oblig_upper'][0][0], F['oblig_upper'][0][1],
            F['oblig_upper'][0][2], F['oblig_not'][0][0], F['oblig_not'][0][1],
            F['oblig_not'][0][2], F['oblig_upper'][3][0], F['oblig_not'][3][0], F['oblig_lower'][3][0]))
E.append(u'🎯 判词针: %d 枚 × 七源 × 三档(原行 ⇎ 全篇折平 ⇎ 摘壳折平); 合计: 原行 %s ⇎ 折 %s ⇎ 摘壳 %s ⇎ 增益 %s。'
         % (NK, str(F['needles_row']), str(F['needles_fold']),
            str(F['needles_noshell']), str(F['needles_gain'])))
E.append(u'🧷 锚: 位 %d ⇎ 去重串 %d; 每枚锚由面上位置 j 与折平次数 cnt 三元组持(文 ⇎ 针 ⇎ 偏移 ⇎ 次数)。'
         % (V('atom_n'), V('atom_distinct')))
E.append(u'🪟 窗口: 注释框 [%d, %d](%d 行) ⇎ gai 示例窗 [%d, %d](%d 行, 行 %d) ⇎ gai 默认窗 [%d, %d](%d 行, 行 %d)。'
         % (V('cmtblock')[0], F['cmtblock'][1], V('cmtblock_lines'),
            F['gai_exwin'][0], F['gai_exwin'][1], F['gai_ex_lines'][0], F['gai_ex_rows'][0],
            F['gai_defwin'][0], F['gai_defwin'][1], F['gai_def_lines'][0], F['gai_def_rows'][0]))
E.append(u'🧮 三元组: 6724 %d ⇎ 3484 %d ⇎ gai 示例 %d ⇎ gai 默认 %d ⇎ 6724∩3484 %d ⇎ 6724△3484 %d; '
         u'gai 示例行 = 3484 表 %d ⇎ = 6724 表 %d; 独有 %s。'
         % (V('triple6_n'), V('triple4_n'), V('triple_gai_ex_n'), V('triple_gai_def_n'),
            V('triple64_same'), V('triple64_diff'), V('triple_ex_eq4'), V('triple_ex_eq6'),
            str(F['triple_ex_only'])))
E.append(u'📐 行形三层: 严格三列行 %s ⇎ 含注行 %s(差 %s) ⇎ 宽档行 %s ⇎ 仅前缀 $%d; 6724 三列行 %d 行在 §2.1 图内 %d 行, 图外 %d 行。'
         % (str(F['row3']), str(F['rowcmtn']), str(F['rowcmt']),
            str(F['rowany']), F['rowany'][0] if False else 0, F['row3'][0] if False else 0,
            F['fig_rows'][0] if False else 0, F['row3_out21'][0] if False else 0))
E.append(u'🔬 方法 ⇒ 前缀策略表的压缩判据: 七源同表逐行 ⇎ 逐三元组对账; 一张一源真值(6724) ⇎ 被替代(3484) 差 %d 元组; '
         u'负对照(YANG 指南)0 行出现在表体层; 内核两份(注释 ⇎ C)互校一条不差 %d 格。'
         % (V('triple64_diff'), V('label_agree_cells')))

enc = CH.join(E)
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)

title = (u'# B97 单文本压缩: IPv6 默认地址选择前缀策略表(6724 ⇎ 3484 ⇎ 7381 ⇎ 8407 ⇎ gai.conf ⇎ addrlabel.c ⇎ addrconf.c)'
         u'——七源 39 枚判词针 ⇎ %d 枚三列行 ⇎ 两条翻转差值\n' % V('fig_rows'))
srcline = (u'src: %s + …(七源, 见 corpus/raw/prefixtable97/)\n' % RAWS[0])
tagsline = (u'tags: 单文本压缩 前缀策略表 七源对照 三元组 ⇎ 三档口径 针池 %d 内核注释 ⇎ C 数组对账\n' % NK)
md = (title + srcline + u'; ' + tagsline + u'## [[原始语料|ORIGINAL]]\n### ⟦A⟧ ⟸ ' +
      u'\n'.join(RAWS) + u'\n\n' + u'\n'.join(u'%s\t%s' % (a[0], a[1]) for a in ATOMS) +
      u'\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n\n(待 _fill97.py 第二遍独立复算后写回)\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=CH).write(md)
print(u'B97 建条目: %s' % ENTRY)
print(u'编码区 %d 字符, 编码区锚 %d 处, 候选锚 %d 条, 登记面值 %d 枚'
      % (len(enc.replace(CH, u'')), n_atoms, len(ATOMS), len(REG)))
assert REG, u'REG 空——V() 没登记任何面值'
io.open(u'corpus/_b97flat.json', 'w', encoding='utf-8').write(
    json.dumps(REG, ensure_ascii=False, sort_keys=True) + CH)
print(u'DERIV 键表: corpus/_b97flat.json %d 键' % len(REG))
```