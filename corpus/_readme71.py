# -*- coding: utf-8 -*-
"""README 记账第五遍(B71): 判词段 ⇎ 门槛表行 ⇎ 语料表行 ⇎ 转化指标行 ⇎ 聚合行, 全按本遍现跑的 audit
与 raw 字节现量, 一个数都不抄建条目侧快照。
本遍的第五套实现: 面量直接吃二进制(字节数 ⇎ 行数按 \\n 计数 ⇎ 码位 ⇎ 换页符两种口径 ⇎ BOM 按解码后的首字符);
针的判定用自写的逐行 in ⇎ 折平面切片 in, 折平走 re.sub('\\s+'); 剥壳谓词照抄建条目侧的 shell_line(从源码里切出来 exec, 不另立定义);
义务语气走手写字母边界扫描(第二遍是正则词界, 第三遍门槛同二遍, 第四遍是切片数整词);
字段名走三把尺: hint 式用字母边界 ⇎ 裸式用整 token 切段(建条目侧的 \\b 把下划线当词字符, 字母边界尺会退化成子串档, 两者量的是不同的东西)
⇎ 子串档用非重叠游标, 三档逐枚对账 fld_sub = fld_hint + fld_plain;
锚的归类把条目编码区的 ⟨⟩ 串在折平面重数一遍, 单源⇎穿源⇎四源分档与门槛登记口径对拍。"""
import io, json, re, subprocess, sys, ast

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\r\n' if u'\r\n' in io.open(u'corpus/README.md', encoding='utf-8').read() else u'\n'
S = io.open(u'corpus/README.md', encoding='utf-8').read()
FP = json.load(io.open(u'corpus/_b71flat.json', encoding='utf-8'))
DER = json.load(io.open(u'corpus/_deriv71.json', encoding='utf-8'))
SRC = [u'corpus/raw/tlsTicket/rfc4507.txt', u'corpus/raw/tlsTicket/rfc5077.txt',
       u'corpus/raw/ietf/rfc8446.txt', u'corpus/raw/tlsTicket/rfc9001.txt']
SHW = [u'`raw/tlsTicket/rfc4507.txt`', u'`raw/tlsTicket/rfc5077.txt`',
       u'`raw/ietf/rfc8446.txt`', u'`raw/tlsTicket/rfc9001.txt`']
LBL = [u'4507', u'5077', u'8446', u'9001']
YR = [u'06', u'08', u'18', u'21']
ANS = [u'hint 字段 + 零值=寿命未定、不封顶、可更短也可更长',
       u'整句照搬 4507, 只把起点补成“相对收到那一刻”, 仍不封顶',
       u'改名去掉 hint、零值翻成立即丢弃、MUST NOT 超 604800 秒(7 日)、只留更短',
       u'自己不写时长, 转述 [TLS13] 的 seven days, 另补一条不得复用']

AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                     text=True, encoding='utf-8').stdout
assert u'T3 码位): PASS' in AUD, AUD[-500:]
assert u'证明失败' not in AUD, AUD[-500:]


def gk(k):
    assert k in FP, k
    return FP[k]


def fmt(n):
    s = u'%d' % n if isinstance(n, int) else u'%g' % n
    if u'.' in s:
        a, b = s.split(u'.', 1)
        return fmt(int(a)) + u'.' + b
    if not s.isdigit() or len(s) <= 3:
        return s
    g = [s[x:x + 3] for x in range(len(s) - 3, -1, -3)][::-1]
    if len(s) % 3:
        g = [s[:len(s) % 3]] + g
    return u' '.join(g)


def num(x):
    return int(''.join(c for c in x if c.isdigit()))


def occ(s, ndl):
    c, i = 0, 0
    while True:
        j = s.find(ndl, i)
        if j < 0:
            return c
        c += 1
        i = j + len(ndl)


def L4(v):
    return u' ⇎ '.join(u'—' if x is None else fmt(x) for x in v)


# ---- 逐份面量(第五套实现: 吃 raw 字节, 行数按 \\n 计数) ----
BS, LN, NB, EF, FFC, CR, NA, ML, DELTA, EXTRA, BOM = [], [], [], [], [], [], [], [], [], [], []
T4, LF4 = [], []
for p in SRC:
    b = io.open(p, 'rb').read()
    BS.append(len(b))
    raw = b.decode('utf-8', 'replace')
    assert not set(raw) & set(u'\x1c\x1d\x1e\x1f'), p
    T4.append(raw)
    LF4.append(raw.split(u'\n'))
    LN.append(raw.count(u'\n') + 1)
    NB.append(len([x for x in LF4[-1] if x.strip() != u'']))
    EF.append(len([x for x in LF4[-1] if x == u'\x0c']))
    FFC.append(occ(raw, u'\x0c'))
    CR.append(occ(raw, u'\r'))
    NA.append(len([c for c in raw if ord(c) > 127]))
    ML.append(max(len(x) for x in LF4[-1]))
    DELTA.append(len(b) - len(raw))
    EXTRA.append(sum(len(c.encode('utf-8')) - 1 for c in raw if ord(c) > 127))
    BOM.append(1 if raw.startswith(u'﻿') else 0)
    assert NB[-1] + EF[-1] <= LN[-1]
assert EF == FFC == gk(u'ff') == gk(u'ff_exact')
assert [BS, LN, NB, CR, NA, ML, DELTA, EXTRA, BOM] == \
       [gk(u'bytes'), gk(u'lines'), gk(u'nonblank'), gk(u'cr'), gk(u'nonascii'),
        gk(u'maxlen'), gk(u'byte_cp_delta'), gk(u'nonascii_extra'), gk(u'bom')]
assert gk(u'ff_only') == [len([1 for x in xs if x.strip() == u'\x0c']) for xs in LF4] == [0, 0, 0, 0]
assert gk(u'chars') == [len(t) for t in T4]
assert [BS[i] - len(T4[i]) for i in range(4)] == gk(u'byte_cp_delta')


def bcnt(t, w):
    """手写字母边界扫描: 前后邻字不是字母才计数"""
    n, i, k = 0, 0, len(w)
    while True:
        j = t.find(w, i)
        if j < 0:
            return n
        a = t[j - 1] if j else u''
        z = t[j + k] if j + k < len(t) else u''
        if not (a.isalpha() or z.isalpha()):
            n += 1
        i = j + k


def wcnt(t, w):
    """整 token 档: 按非词字符切片后逐段等值比(字段名用这条)"""
    return len([x for x in re.split(u'[^A-Za-z0-9_]+', t) if x == w])


UPM = [bcnt(t, u'MUST') for t in T4]
UPN = [occ(t, u'MUST NOT') for t in T4]
LOW = [bcnt(t, u'must') for t in T4]
CIM = [bcnt(t.lower(), u'must') for t in T4]
assert UPM == gk(u'up_must_all') and UPN == gk(u'must_not')
assert [UPM[i] - UPN[i] for i in range(4)] == gk(u'must_bare')
assert LOW == gk(u'low_must') and CIM == gk(u'ci_must')
assert gk(u'up_must_all')[:2] == [18, 18] and gk(u'must_not')[:2] == [9, 9]
assert sum(gk(u'up_ledger')) == 0 and sum(gk(u'case_ledger')) == 0
FH = [bcnt(t, u'ticket_lifetime_hint') for t in T4]
FP_ = [wcnt(t, u'ticket_lifetime') for t in T4]
FS = [occ(t, u'ticket_lifetime') for t in T4]
assert FH == gk(u'fld_hint') and FP_ == gk(u'fld_plain') and FS == gk(u'fld_sub')
assert [FS[i] - FH[i] - FP_[i] for i in range(4)] == [0, 0, 0, 0] == gk(u'fld_close')
assert wcnt(T4[2], u'ticket_lifetime') == gk(u'fld_plain')[2] == 7
assert wcnt(T4[2], u'ticket_lifetime_hint') == 0

# ---- 三面阶梯: 逐行 ⇎ 全篇折平 ⇎ 剥壳折平(剥壳谓词从建条目侧源码切出 exec) ----
MS = io.open(u'corpus/_mkB71.py', encoding='utf-8').read()
SHELL_SRC = re.search(u'def shell_line\\(l\\):.*?\\n(?=SH =)', MS, re.S).group(0)
NS = {u'u': None}
exec(u'import re\n' + SHELL_SRC, NS)
is_shell = NS[u'shell_line']
TAB = {}
for st in ast.parse(MS.replace(u'\nexec(', u'\n#exec(')).body:
    if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name) and st.targets[0].id == u'NEEDLE':
        TAB[u'NEEDLE'] = ast.literal_eval(st.value)
NEEDLE = TAB[u'NEEDLE']
OWNER = dict((k, o) for o, k, _ in NEEDLE)
NEEDL = dict((k, nd) for o, k, nd in NEEDLE)
KEYS = [k for _, k, _ in NEEDLE]
FOLD4 = [re.sub(u'\\s+', u' ', t) for t in T4]
SHF4 = [re.sub(u'\\s+', u' ', u'\n'.join([l for l in LF4[i] if not is_shell(l)])) for i in range(4)]
STRICT, FOLDD, SHD = [], [], []
for i in range(4):
    o = [k for k in KEYS if OWNER[k] == i]
    STRICT.append(len([k for k in o if any(NEEDL[k] in l for l in LF4[i])]))
    FOLDD.append(len([k for k in o if re.sub(u'\\s+', u' ', NEEDL[k]) in FOLD4[i]]))
    SHD.append(len([k for k in o if re.sub(u'\\s+', u' ', NEEDL[k]) in SHF4[i]]))
assert len(KEYS) == gk(u'needle_n') == 28
assert [len([k for k in KEYS if OWNER[k] == i]) for i in range(4)] == gk(u'needles_owned')
assert STRICT == gk(u'sn_strict_docs') and FOLDD == gk(u'sn_fold_docs') and SHD == gk(u'sn_sh_docs')
assert [gk(u'sn_fold_docs')[i] - gk(u'sn_sh_docs')[i] for i in range(4)] == gk(u'sh_minus_fold')
FONLY = [k for k in KEYS if re.sub(u'\\s+', u' ', NEEDL[k]).lower()
         in re.sub(u'\\s+', u' ', FOLD4[OWNER[k]]).lower()
         and not any(NEEDL[k] in l for l in LF4[OWNER[k]])]
assert sorted(FONLY) == sorted(gk(u'fold_only_keys')), (len(FONLY), gk(u'fold_only_n'))
FOWN = [len([k for k in FONLY if OWNER[k] == i]) for i in range(4)]
assert FOWN == gk(u'fold_only_own')
assert [STRICT[i] + FOWN[i] for i in range(4)] == FOLDD
assert gk(u'ladder_monotone') == 1 and gk(u're_eq_cur') == 1
DEAD = [k for k in KEYS if not re.sub(u'\\s+', u' ', NEEDL[k]) in FOLD4[OWNER[k]]]
assert sorted(DEAD) == sorted(gk(u'dead_needles')) == [u'z4507_no_relative', u'z9001_zero']
assert gk(u'n_z4507_no_relative')[0] == 0 and gk(u'n_z9001_zero')[3] == 0
assert gk(u'zero_carry_sh') == [1, 1] and gk(u'zero_carry_fold') == [1, 0]
assert gk(u'zero_flip') == 1 and gk(u'zero_split_gap') == 10
assert gk(u'ln_unspec_4507') - gk(u'ln_zero_4507') == gk(u'zero_split_gap')

# ---- 锚的归一分类(串取自条目编码区, 归类只看小写折叠面) ----
ENT = io.open(u'corpus/babeltele/B71_tls_ticket_lifetime_four_answers.md', encoding='utf-8').read()
BODY = ENT.split(u'## ⟪BabelTele⟫')[1].split(u'## ⛓解读注')[0]
ASTR = sorted(set(re.findall(u'⟨([^⟨⟩]+)⟩', BODY)))
FAN4 = [u' '.join(t.lower().split()) for t in T4]
HIT = dict((a, tuple(i for i in range(4) if u' '.join(a.lower().split()) in FAN4[i])) for a in ASTR)
ASIN = len([a for a in ASTR if len(HIT[a]) == 1])
ACRO2 = len([a for a in ASTR if len(HIT[a]) == 2])
ATRI = len([a for a in ASTR if len(HIT[a]) == 3])
AALL4 = len([a for a in ASTR if len(HIT[a]) == 4])
APAIR = {}
for a in ASTR:
    if len(HIT[a]) >= 2:
        kk = tuple(LBL[i] for i in HIT[a])
        APAIR[kk] = APAIR.get(kk, 0) + 1
assert (ASIN, ACRO2 + ATRI, AALL4, len(ASTR)) == (gk(u'anchor_single'), gk(u'anchor_cross'),
                                                  gk(u'anchor_all4'), gk(u'anchor_distinct'))
assert APAIR == {(u'4507', u'5077'): gk(u'anchor_cross')}
assert sum(len(a) for a in ASTR) < gk(u'enc_chars')

# ---- 共用长行池 ⇎ 配对(第五套: 只用集合代数, 不抄四遍的 dict-of-set) ----
def pn(s):
    return u' '.join(s.lower().split())


PL = [set(pn(x) for x in LF4[i] if len(pn(x)) >= 40 and not is_shell(x)) for i in range(4)]
PR = [[len(PL[a] & PL[b]) for a, b in
       [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]] for _ in [0]][0]
assert PR == gk(u'pair_share'), (PR, gk(u'pair_share'))
PRES = dict((a, tuple(i for i in range(4) if a in PL[i])) for s in PL for a in s)
TIER = [len([a for a, v in PRES.items() if len(v) == k]) for k in range(1, 5)]
assert TIER == gk(u'pool_tier') and len(PRES) == gk(u'pool_n')
assert sum(TIER) == len(PRES)
assert gk(u'pair_close') == 0 and gk(u'union_close') == 0 and gk(u'axis_close') == 0
assert gk(u'axis_counts')[u'space'] == 28 and gk(u'axis_counts')[u'multi'] == 0
assert gk(u'apool_tag_close') == 0 == gk(u'apool_tier_close')


def bkeys(s):
    o = set()
    for ch in s.split(u'B71V(')[1:]:
        q = ch[0]
        if q in (u'"', u"'"):
            o.add(ch[1:ch.find(q, 1)])
    return o


DKEYS = len(bkeys(json.dumps(DER, ensure_ascii=False)) & set(FP))
assert 0 < DKEYS < len(FP), DKEYS
CLOSEK = len([k for k in FP if u'close' in k])

# ---- 门槛表 B71 行 ----
GCOL = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B71 |'):
        GCOL = [x.strip() for x in l.split(u'|')[1:-1]]
assert GCOL and len(GCOL) >= 3, GCOL
DIG71 = num(GCOL[1])
E71 = num(GCOL[2])
assert E71 == gk(u'enc_chars'), (E71, gk(u'enc_chars'))
HEADROW = (u'| B71 | ' + fmt(E71) + u'（新建, 一张 TLS 会话恢复票据到底能活多久、零值是什么意思 交四份会话票据一手文书各答一遍 '
           + str(gk(u'anchor_total')) + u' 处标注／' + str(gk(u'anchor_distinct'))
           + u' 个不同串（登记全命中, 单源 ' + str(gk(u'anchor_single')) + u' ⇎ 穿二三源 ' + str(gk(u'anchor_cross'))
           + u' ⇎ 四源全现 ' + str(gk(u'anchor_all4')) + u'——穿源的 ' + str(gk(u'anchor_cross'))
           + u' 枚全落在 4507⇎5077 这一对, 逐字搬运把同一行留在两份里; 编码区 ' + fmt(gk(u'enc_chars'))
           + u' 字符, 归属检查 ' + str(gk(u'checks')) + u' 次, 错配 ' + str(gk(u'anchor_err')) + u'）: 四色锚位 '
           + u' ⇎ '.join(x + u' ⟦' + y + u'⟧' for x, y in zip(LBL, u'ABCD'))
           + u'; 答句四种（hint＋零值=未定 ⇎ 照搬＋补计时起点 ⇎ 改名＋硬上限＋零值=立即丢弃 ⇎ 不表态只转述）: '
           + u' ⇎ '.join(ANS) + u'; 三面阶梯（原面 ⇎ 全篇折平 ⇎ 摘壳折平）按文档读到 '
           + u'⇎'.join(str(x) for x in STRICT) + u' ／ ' + u'⇎'.join(str(x) for x in FOLDD) + u' ／ '
           + u'⇎'.join(str(x) for x in SHD) + u'（针表 ' + str(gk(u'needle_n')) + u' 枚, 归各份 '
           + u'⇎'.join(str(x) for x in gk(u'needles_owned')) + u' 枚, 折平才现 '
           + str(gk(u'fold_only_n')) + u' 枚, 按份新增 ⇎'.join(str(x) for x in FOWN)
           + u'——4507 的 ' + str(gk(u'sn_fold_docs')[0]) + u' 枚自家针逐行档只命中 '
           + str(gk(u'sn_strict_docs')[0]) + u' 枚, 5077 的 ' + str(gk(u'sn_fold_docs')[1])
           + u' 枚一枚都不在逐行档, 摘壳档比折平档一粒不少（差 ' + L4(gk(u'sh_minus_fold')) + u'）; '
           + u'阶梯读不到的两枚恰是该零命中的两枚反向针 ' + u' ⇎ '.join(gk(u'dead_needles'))
           + u', 死集等于判定集; 锚池 ' + fmt(gk(u'pool_n')) + u' 条分档 '
           + u'⇎'.join(fmt(x) for x in gk(u'pool_tier')) + u'（闭合 ' + str(gk(u'pool_tier_close'))
           + u'）, 四份同现长行 ' + str(gk(u'pool_4')) + u' 条 ⇎ 三份 ' + str(gk(u'pool_3'))
           + u' 条 ⇒ 写法轴开两档 ' + gk(u'axis_str') + u'（轴账闭合 ' + str(gk(u'axis_close'))
           + u'）——同一句在两份里只差行首缩进的有 ' + str(gk(u'axis_counts')[u'space']) + u' 枚; 长行池最大一对 '
           + gk(u'pair_max_lbl') + u'（' + fmt(gk(u'pair_max')) + u' 归一／' + str(gk(u'pair_max_byte'))
           + u' 逐字节／' + str(gk(u'pair_max_norm_only')) + u' 仅归一）, 配对闭合 ' + str(gk(u'pair_close'))
           + u' ⇎ 容斥闭合 ' + str(gk(u'union_close')) + u'; 义务语气四轨: MUST 全计 ' + L4(gk(u'up_must_all'))
           + u' ⇎ 裸 MUST ' + L4(gk(u'must_bare')) + u' ⇎ MUST NOT ' + L4(gk(u'must_not')) + u'（大写账 '
           + L4(gk(u'up_ledger')) + u'）⇎ 小写 must ' + L4(gk(u'low_must')) + u' ⇎ 不分大小写 ' + L4(gk(u'ci_must'))
           + u'（大小写账 ' + L4(gk(u'case_ledger')) + u'）——4507⇎5077 两份逐枚相等, 8446 涨到 '
           + str(gk(u'up_must_all')[2]) + u' 枚而 9001 面上封顶句 0 枚（判定 ' + str(gk(u'up_zero_9001_cap'))
           + u'⇒成立）; 字段名三式: hint 式 ' + L4(gk(u'fld_hint')) + u' ⇎ 裸式 ' + L4(gk(u'fld_plain')) + u' ⇎ 子串 '
           + L4(gk(u'fld_sub')) + u'（三式闭合 ' + L4(gk(u'fld_close')) + u'）⇎ 声明行 ' + L4(gk(u'uint32_hint'))
           + u'⇎' + L4(gk(u'uint32_plain')) + u'（改名判定 ' + str(gk(u'field_renamed')) + u'）; 同一枚零值三种语义: 4507 的整句被一页壳劈开——'
           u'摘壳面 ' + str(gk(u'zero_carry_sh')[1]) + u' 枚 ⇎ 含壳面 ' + str(gk(u'zero_carry_fold')[1])
           + u' 枚（差 ' + str(gk(u'zero_flip')) + u', 相隔 ' + str(gk(u'zero_split_gap')) + u' 行）⇎ 8446 翻成立即丢弃（唯一判定 '
           + str(gk(u'zero_ind_unique')) + u'）⇎ 9001 面上句式 0 枚; 上限只活在一份里: ' + fmt(gk(u'num_cap_faces')[2])
           + u' = 每日 ' + fmt(gk(u'num_day_seconds')) + u' × ' + str(gk(u'num_cap_ratio')) + u' 日（余 '
           + str(gk(u'num_cap_remainder')) + u' ⇎ 括注 ' + str(gk(u'num_cap_days')[2]) + u' 日同值 ⇎ 位宽 2^'
           + str(gk(u'num_mod_pow')) + u'）⇎ 旧的 24 小时建议 ' + L4(gk(u'd24_hour')) + u' ⇎ 9001 只用文字转述（seven days '
           + str(gk(u'seven_days')[3]) + u' 枚 ⇎ [TLS13] 括号引用 ' + str(gk(u'num_tls13_refs')[3]) + u' 枚）; '
           u'谁废止谁现读: 5077 Obsoletes ' + str(gk(u'obs_set_5077')) + u' ⇎ 8446 Obsoletes ' + str(gk(u'obs_set_8446'))
           + u' ⇎ Updates ' + str(gk(u'upd_set_8446')) + u', 对象并集 ' + str(gk(u'target_n')) + u' 枚, 链路闭合 '
           + str(gk(u'chain_closed')) + u', 标题页年份 ' + L4(gk(u'years')) + u'（倒序 ' + str(gk(u'year_inversions'))
           + u' 处 ⇎ 年距 ' + u'⇎'.join(str(x) for x in gk(u'year_gaps')) + u'）, 引用单向（8446 面上引 9001 '
           + str(gk(u'cite_dir_8446_to_9001')) + u' 枚 ⇎ 反向 ' + str(gk(u'cite_dir_9001_to_8446')) + u' 枚, 判定 '
           + str(gk(u'cite_dir')) + u'）; 答句邻域按 ±' + str(gk(u'win_band')) + u' 行带切, 五轨（lifetime ⇎ zero ⇎ 604800 ⇎ '
           u'reuse ⇎ 数字符）带内外分账闭合 ' + str(gk(u'win_close_sum')) + u'（窗 ' + L4(gk(u'win_spans'))
           + u' 行 ⇎ 命到小节标题 ' + str(gk(u'win_named')) + u' 份）; 同数共键 ' + str(len(DER)) + u' 枚算式／'
           + str(gk(u'x_ident_n')) + u' 条面内恒等式（标量闭账 ' + str(gk(u'scalar_clos_n')) + u' 项, 通过 '
           + str(gk(u'scalar_clos_sum')) + u' ⇎ 含 close 的键 ' + str(CLOSEK) + u' 枚其中逐份清单 '
           + str(gk(u'list_clos_n')) + u' 枚）, 扁平契约 ' + str(len(FP))
           + u' 枚键全数复测; 五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对锚逐字复核'
           u'；工具侧 atomcheck 的 SRC 表未登记本条, 四份纯文本面的逐字性由门槛侧 ' + str(gk(u'checks'))
           + u' 次归属检查承担（逐字命中 ' + str(gk(u'anchor_total')) + u' 处 ⇎ 错配 ' + str(gk(u'anchor_err')) + u'） |')

SRCLINE = SHW
C71 = (u'| B71 | ' + u' ⇎ '.join(
    SRCLINE[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／面内码位 ' + fmt(gk(u'chars')[i])
    + u'／行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i]) + u'（换页符 ' + str(FFC[i]) + u' 枚，独占整行 ' + str(EF[i])
    + u' 行）／最长行 ' + str(ML[i]) + u' 列／答句 ' + ANS[i] + u'／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i])
    + u'／BOM ' + str(BOM[i]) + u'）' for i in range(4))
           + u' | 四份答同一个问题 ⇒ 4507 把时长写成 hint、零值只算“寿命未定”（“A value of zero is reserved…”句 '
             + str(gk(u'n_z4507_zero_reserved')[0]) + u' 枚 ⇎ “is unspecified.” ' + str(gk(u'n_z4507_unspec_end')[0])
             + u' 枚, 两者相隔 ' + str(gk(u'zero_split_gap')) + u' 行而被一页壳劈开），一个上限数字都不给，只引 2246 的 24 小时建议（'
             + str(gk(u'd24_hour')[0]) + u' 枚）⇎ 5077 把那段整句照搬（共尾共头各 ' + str(gk(u'suf_45_50'))
             + u' 枚词 ⇎ 段内词集账闭合 ' + str(gk(u'w_row_close')) + u'），唯一补的是起点 relative to when the ticket is received（'
             + str(gk(u'relative_in')[1]) + u' 枚），仍不封顶 ⇎ 8446 改名去掉 hint（裸式 ' + str(gk(u'fld_plain')[2])
             + u' 枚 ⇎ hint 式 0 枚）、零值翻成立即丢弃（全库唯一）、MUST NOT 超 ' + fmt(gk(u'num_cap_faces')[2])
             + u' 秒（= ' + str(gk(u'num_cap_days')[2]) + u' 日整），把“shorter or longer”砍成“shorter”（判定 '
             + str(gk(u'drop_or_longer')) + u'），起点再换成 issuance（判定 ' + str(gk(u'from_issuance_only'))
             + u'）⇎ 9001 面上 604800 0 枚 ⇎ 上限句 0 枚，只转述“[TLS13] sets a limit of seven days”（判定 '
             + str(gk(u'delegates')) + u'）；三面阶梯在本条的空转全在逐行档（4507 ' + str(gk(u'sn_strict_docs')[0])
             + u'⇎5077 ' + str(gk(u'sn_strict_docs')[1]) + u' 枚），' + str(gk(u'fold_only_n'))
             + u' 枚整句被行界劈开靠折行救回，而摘壳档一粒不多（差 ' + L4(gk(u'sh_minus_fold')) + u'） |' + NL)

PARA = (u'**B71 问的是一张 TLS 会话恢复票据到底能活多久、寿命字段里的零值是什么意思，四份一手文书给出四种答法**：'
        + u' ⇎ '.join(SRCLINE[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
                      + u'／非空行 ' + fmt(NB[i]) + u'／换页符 ' + str(FFC[i]) + u' 枚（独占整行 ' + str(EF[i])
                      + u' 行）／答句 ' + ANS[i] + u'／非 ASCII ' + str(NA[i]) + u'／BOM ' + str(BOM[i]) + u'）'
                      for i in range(4))
        + u'——前三份同为 RFC Editor 纯文本面且逐字节纯 ASCII，只有 9001 带 BOM ⇎ ' + str(gk(u'nonascii')[3])
          + u' 枚非 ASCII 字符（排版引号与长横），字节−码位差 ' + L4(gk(u'byte_cp_delta')) + u' ⇎ 非 ASCII 加字节 '
          + L4(gk(u'nonascii_extra')) + u' 逐枚相等，纯 ASCII 面 ' + str(gk(u'ascii_all')) + u' 份；换页符 '
          + L4(FFC) + u' 枚且全部独占整行（' + L4(EF) + u' 行），而建条目侧 ff_only 按 x.strip()==FF 判——strip 先吃掉换页符本身，'
          + u'该档恒零（' + L4(gk(u'ff_only')) + u'，口径陷阱如实记）；9001 换页符 ' + str(gk(u'ff')[3])
          + u' 枚，它的摘壳折平面与含壳折平面对针的读数逐枚相同（差 ' + str(gk(u'sh_minus_fold')[3])
          + u'）——这一条里“剥壳”只对前三份有意义。4507 把时长写成 hint（面上 hint 字样 ' + str(gk(u'hint_word')[0])
          + u' 枚），零值只算“寿命未定”（“A value of zero is reserved…”' + str(gk(u'n_z4507_zero_reserved')[0])
          + u' 枚），还主动允许服务器把票当作“更短或更长”有效（or longer ' + str(gk(u'orlonger')[0])
          + u' 枚），全篇一个上限数字都不给 ⇎ 5077 逐字收下那段（段共尾共头各 ' + str(gk(u'suf_45_50'))
          + u' 枚词，词集账闭合 ' + str(gk(u'w_row_close')) + u'），唯一补上的是计时起点 relative to when the ticket is received（'
          + str(gk(u'relative_in')[1]) + u' 枚，比定义句晚 ' + str(gk(u'relative_span')) + u' 行），仍不封顶 ⇎ 8446 一次改五处：字段改名去掉 hint'
          + u'（裸式 ' + str(gk(u'fld_plain')[2]) + u' 枚 ⇎ hint 式 0 枚 ⇎ 声明行 ' + str(gk(u'uint32_hint')[0]) + u'⇎'
          + str(gk(u'uint32_plain')[2]) + u'），零值翻成立即丢弃（“immediately”字样 ' + str(gk(u'imm_word')[2])
          + u' 枚），写出 MUST NOT 超 ' + fmt(gk(u'num_cap_faces')[2]) + u' 秒即 ' + str(gk(u'num_cap_days')[2])
          + u' 日（每日 ' + fmt(gk(u'num_day_seconds')) + u' 秒 ⇒ 商 ' + str(gk(u'num_cap_ratio')) + u' ⇎ 余 '
          + str(gk(u'num_cap_remainder')) + u' ⇎ 位宽 2^' + str(gk(u'num_mod_pow')) + u'），把“或更长”砍掉只剩更短，起点换成 issuance'
          + u' ⇎ 9001 一枚自己的时长规则都不写（面上 604800 0 枚 ⇎ 大写封顶句 0 枚），只转述“[TLS13] sets a limit of seven days”'
          + u'（seven days ' + str(gk(u'seven_days')[3]) + u' 枚 ⇎ [TLS13] 括号引用 ' + str(gk(u'num_tls13_refs')[3])
          + u' 枚），另补一条复用禁令（reuse 字样 4507/5077 ' + str(gk(u'reuse_word')[0]) + u' ⇎ 8446 '
          + str(gk(u'reuse_word')[2]) + u' ⇎ 9001 ' + str(gk(u'reuse_word')[3]) + u' 枚）。'
          u'三面阶梯：在册 ' + str(gk(u'needle_n')) + u' 枚答句针按原面读到 ' + u'⇎'.join(str(x) for x in STRICT)
          + u'、全篇折平 ' + u'⇎'.join(str(x) for x in FOLDD) + u'、摘壳折平 ' + u'⇎'.join(str(x) for x in SHD)
          + u'——最刺眼的是 4507⇎5077：两份的答句整段被行界劈开（逐行档 ' + str(gk(u'sn_strict_docs')[0]) + u'⇎'
          + str(gk(u'sn_strict_docs')[1]) + u' 枚 ⇎ 折平档 ' + str(gk(u'sn_fold_docs')[0]) + u'⇎'
          + str(gk(u'sn_fold_docs')[1]) + u' 枚），折行独有 ' + str(gk(u'fold_only_n')) + u' 枚按份新增 ⇎'.join(str(x) for x in FOWN)
          + u'，阶梯单调 ' + str(gk(u'ladder_monotone')) + u'；摘壳档比折平档一粒不少（差 ' + L4(gk(u'sh_minus_fold'))
          + u'）——本条必需的是折行，剥壳只用来救那枚被页脚劈开的整句零值句（含壳面 ' + str(gk(u'zero_carry_fold')[1])
          + u' 枚 ⇎ 摘壳面 ' + str(gk(u'zero_carry_sh')[1]) + u' 枚）。谁抄谁可量：归一长行两两交集 ' + L4(gk(u'pair_share'))
          + u' ⇎ 逐字节同形 ' + L4(gk(u'pair_byte')) + u' ⇎ 仅归一 ' + L4(gk(u'pair_norm_only')) + u'（非零对 '
          + str(gk(u'pair_nonzero')) + u'，配对闭合 ' + str(gk(u'pair_close')) + u' ⇎ 容斥闭合 ' + str(gk(u'union_close'))
          + u'）——最大一对 ' + gk(u'pair_max_lbl') + u' 归一 ' + fmt(gk(u'pair_max')) + u' 行里 ' + str(gk(u'pair_max_byte'))
          + u' 行逐字节同形 ⇒ 4507→5077 是真的行级搬运；写法轴四桶 ' + gk(u'axis_str') + u'（轴账闭合 '
          + str(gk(u'axis_close')) + u'）——分家几乎全在缩进上。语气换代不按时钟走：标题页年份 ' + L4(gk(u'years'))
          + u'（月份 ' + u'⇎'.join(gk(u'months')) + u'），零处倒序 ⇒ 文书顺序与时间顺序同向，“取最新”在这条里不会被年份骗，'
          + u'只会被 9001 的转述骗；动作头现读：5077 Obsoletes ' + str(gk(u'obs_set_5077')) + u' ⇎ 8446 Obsoletes '
          + str(gk(u'obs_set_8446')) + u' ⇎ Updates ' + str(gk(u'upd_set_8446')) + u'（对象并集 ' + str(gk(u'target_n'))
          + u' 枚，链路闭合 ' + str(gk(u'chain_closed')) + u'）；互引只单向——8446 面上引 9001 ' + str(gk(u'cite_dir_8446_to_9001'))
          + u' 枚 ⇎ 反向 ' + str(gk(u'cite_dir_9001_to_8446')) + u' 枚（判定 ' + str(gk(u'cite_dir')) + u'）。'
          u'答句邻域按 ±' + str(gk(u'win_band')) + u' 行带切，五轨（lifetime ⇎ zero ⇎ 604800 ⇎ reuse ⇎ 数字符）带内外分账闭合 '
          + str(gk(u'win_close_sum')) + u'（窗 ' + L4(gk(u'win_spans')) + u' 行 ⇎ 四份都命到小节标题 ' + str(gk(u'win_named'))
          + u' 份）。门槛侧 ' + str(len(DER)) + u' 枚算式／' + str(gk(u'x_ident_n')) + u' 条面内恒等式（标量 '
          + str(gk(u'scalar_clos_n')) + u' 项通过 ' + str(gk(u'scalar_clos_sum')) + u'），扁平契约 ' + str(len(FP))
          + u' 枚键由第四 ⇎ 第五套实现逐枚复测；其中 ' + str(DKEYS) + u' 枚进得了 DERIV 算式 ⇎ 余下 '
          + str(len(FP) - DKEYS) + u' 枚是形状清单、字符串表与窗口切片；' + str(len(ASTR)) + u' 枚不同锚串按折叠面重分类 单源 '
          + str(ASIN) + u' ⇎ 穿源 ' + str(ACRO2 + ATRI) + u' ⇎ 四源 ' + str(AALL4) + u'，与门槛登记口径一致。')

L = S.split(NL)
assert L and S.count(u'**B71 问的是') == 0
assert S.count(u'| B71 |') == 0


def sub(old, new, s, cnt=1):
    assert s.count(old) == cnt, (u'锚点不唯一', old[:60], s.count(old))
    return s.replace(old, new)


def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:60])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


# ---- 1) 判词段(紧跟 B70 段) 2) 门槛表行 3) 语料表行 ----
S = after(S, u'**B70 问的是一条 UDP 报文的校验和到底是不是非算不可', PARA + NL + NL)
S = after(S, u'| B70 | 8 097（新建,', HEADROW + NL)
S = after(S, u'| B70 | `raw/udpCK/rfc768.txt`', C71)

# ---- 4) 转化指标表: 按 audit 当下输出补 B71 机械行, 合计行按 ALL 行现算 ----
ROWS = {}
ALLR = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        c = [x.strip() for x in l.split(u'|')[1:-1]]
        ROWS[c[0]] = c
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR and len(ROWS) == 70, (len(ROWS), bool(ALLR))
L = S.split(NL)
h = [i for i, l in enumerate(L) if l.startswith(u'| entry | 编码字符 |')]
assert len(h) == 1, h
tot = [i for i in range(h[0], len(L)) if L[i].startswith(u'| **合计（')]
assert len(tot) == 1, tot
T = tot[0]
present = [l.split(u'|')[1].strip() for l in L[h[0] + 2:T]]
assert all(p.startswith(u'B') for p in present), present[:3]
missing = [k for k in sorted(ROWS, key=lambda k: int(k[1:])) if k not in present]
assert missing == [u'B71'], missing
NEWROW = (u'| %s | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
          % (missing[0], fmt(num(ROWS[missing[0]][2])), ROWS[missing[0]][3], ROWS[missing[0]][4],
             ROWS[missing[0]][5], ROWS[missing[0]][7]))
L[T:T] = [NEWROW]
enc_all = sum(num(c[2]) for c in ROWS.values())
dig_all = sum(num(c[1]) for c in ROWS.values())
assert enc_all == num(ALLR[2]) and dig_all == num(ALLR[1]), (enc_all, num(ALLR[2]))
UNIQ_ALL = num(ALLR[5])
OLD = L[T + 1]
cells = OLD.split(u'|')
assert cells[2].strip().startswith(u'**4'), cells[2]
cells[1] = u' **合计（' + str(len(ROWS)) + u' 条）** '
cells[2] = u' **' + fmt(enc_all) + u'** '
cells[3] = (u' **%.1f%%**（摘要段合计 ' % (100.0 * enc_all / dig_all) + fmt(dig_all)
            + u'，本遍补记的一枚为 ' + fmt(E71) + u' 编码／' + fmt(DIG71)
            + u' 摘要；条目数与两列合计均取自本遍现跑的 audit，唯一码点那格取本遍 ALL 行现算值） ')
cells[5] = u' **%s** ' % fmt(UNIQ_ALL)
assert len(cells) == len(OLD.split(u'|')), (len(cells), len(OLD.split(u'|')))
L[T + 1] = u'|'.join(cells)
NOTE = [i for i, l in enumerate(L) if l.startswith(u'（B54 起的 ') and u'机械行' in l]
assert len(NOTE) == 1, NOTE
L[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与'
              u'字符/语义单元五格, 不重写各条的口径注; 本遍再直补 B71 一枚, 合计行的唯一码点即 ALL 行那个全库并集值。）'
              % len([x for x in present + missing if int(x[1:]) >= 54]))
S = NL.join(L)

# ---- 5) 条数与推导数 ----
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])
S = sub(u'共 **69 条**（`babeltele/B01..B65、B67..B70`, 本遍补上 B70 的四处记账行, 合计按 audit 当下输出重算）',
        u'共 **70 条**（`babeltele/B01..B65、B67..B71`, 本遍补上 B71 的四处记账行, 合计按 audit 当下输出重算）', S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（69 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（70 条）', S)
PV = [l for l in S.split(NL) if u'条语料／' in l and u'推导全部通过' in l]
assert len(PV) == 1, PV
i0 = PV[0].find(u'当前 **')
j = PV[0].find(u'）', PV[0].find(u'audit 自报', i0))
while PV[0][j + 1:j + 2] == u'）':
    j += 1
S = S[:S.find(PV[0]) + i0] + (u'当前 **70 条语料／' + str(PROOFS) + u' 条**推导全部通过（audit 自报“已机检的推导 '
                              + str(PROOFS) + u' 条”）') + S[S.find(PV[0]) + j + 1:]

CMD = u'python -X utf8 corpus/_fill70.py'
assert S.count(CMD) == 1
S = after(S, u'python -X utf8 corpus/_fill70.py',
          u'python -X utf8 corpus/_mkB71.py                    # 建条目(前半, 与 _mk71emit.py 同场 exec): 扁平契约 '
          + str(len(FP)) + u' 枚键／恒等式 ' + str(gk(u'x_ident_n')) + u' 条 ⇎ DERIV ' + str(len(DER))
          + u' 枚算式, 非重叠游标 ⇎ 正则字面轨 ⇎ 集合代数三机制, 采集侧对账 30/32 枚(两枚为壳谓词与对照组口径差)' + NL)
S = after(S, u'python -X utf8 corpus/_mkB71.py',
          u'python -X utf8 corpus/_mkdigest3.py B71 <entry> 4507 corpus/raw/tlsTicket/rfc4507.txt 160 260 '
          u'5077 corpus/raw/tlsTicket/rfc5077.txt 160 260 8446 corpus/raw/ietf/rfc8446.txt 160 260 '
          u'9001 corpus/raw/tlsTicket/rfc9001.txt 160 260   # 四源分节摘要(' + fmt(DIG71) + u' 字符, '
          + str(gk(u'anchor_total')) + u'/' + str(gk(u'anchor_total')) + u' 锚全命中)' + NL)
S = after(S, u'python -X utf8 corpus/_mkdigest3.py B71',
          u'python -X utf8 corpus/_wire71.py                    # 幂等接线: SRC/ATOM/SCAN(审计器侧第三套实现)/DERIV/'
          u'B71V 进 audit.py, 落盘前复跑 ' + str(len(FP)) + u' 枚扁平键 ⇎ ' + str(len(DER)) + u' 枚算式' + NL)
S = after(S, u'python -X utf8 corpus/_wire71.py',
          u'python -X utf8 corpus/_fill71.py                    # 第四遍: 三面阶梯⇎段落双尺⇎集合代数⇎词轨各重导一次, '
          + str(gk(u'x_ident_n')) + u' 条恒等式现算归零后写回 ⛓解读注（16 行复测表 ⇎ 复算 357 键对账 0 不符 ⇎ 独有 10 枚）' + NL)

io.open(u'corpus/README.md', 'w', encoding='utf-8', newline=NL).write(S)
json.dump(dict(entries=len(ROWS), enc=enc_all, dig=dig_all, proofs=PROOFS, b71_enc=E71, b71_dig=DIG71,
               bytes=BS, lines=LN, nonblank=NB, formfeed_only=EF, ff_occ=FFC, cr=CR, nonascii=NA, bom=BOM,
               maxlen=ML, strict=STRICT, fold=FOLDD, sh=SHD, fold_only_n=gk(u'fold_only_n'),
               fold_only_own=FOWN, up=UPM, low=LOW, ci=CIM, fld_hint=FH, fld_plain=FP_, fld_sub=FS,
               close_keys=CLOSEK, uniq_all=UNIQ_ALL, keys=len(FP), deriv=len(DER),
               ident=gk(u'x_ident_n'), pairs=gk(u'pair_share'), pairs_byte=gk(u'pair_byte'),
               pool_tier=TIER, anchors=len(ASTR)),
          io.open(u'corpus/_b71readme.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（' + str(len(ROWS)) + u' 条）编码 ' + fmt(enc_all) + u' ⇎ 摘要 ' + fmt(dig_all)
      + u' ⇎ 保留 %.1f%%' % (100.0 * enc_all / dig_all) + u' ｜ 推导 ' + str(PROOFS) + u' 条 ｜ B71 行 ' + fmt(E71)
      + u'／' + fmt(DIG71) + u' ｜ 锚 ' + str(gk(u'anchor_total')) + u' 处⇎错配 ' + str(gk(u'anchor_err'))
      + u' ｜ 三面阶梯 ' + u'⇎'.join(str(x) for x in STRICT) + u'／' + u'⇎'.join(str(x) for x in FOLDD)
      + u'／' + u'⇎'.join(str(x) for x in SHD) + u' ｜ 折行独有 ' + str(gk(u'fold_only_n')) + u' 枚'
      + u' ｜ 逐份字节 ' + u'⇎'.join(fmt(x) for x in BS))
