# -*- coding: utf-8 -*-
"""README 记账第五遍(B70): 判词段 ⇎ 门槛表行 ⇎ 语料表行 ⇎ 转化指标行 ⇎ 聚合行, 全按本遍现跑的 audit
与 raw 字节现量, 一个数都不抄建条目侧快照。
本遍的第五套实现: 面量直接吃二进制(字节数 ⇎ 行数按 \\n 计数 ⇎ 码位 ⇎ 换页符两种口径);
针的判定用自写的逐行 in ⇎ 折平面切片 in, 折平走 re.sub('\\s+'); 剥壳谓词照抄建条目侧的 shell_line(从源码里切出来 exec, 不另立定义);
义务语气走手写字母边界扫描(第二遍是正则词界, 第三遍门槛同二遍, 第四遍是 re.findall 转义);
锚的归类把条目编码区的 ⟨⟩ 串在折平面重数一遍, 与 _b70flat.json 逐键对账。"""
import io, json, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\r\n' if u'\r\n' in io.open(u'corpus/README.md', encoding='utf-8').read() else u'\n'
S = io.open(u'corpus/README.md', encoding='utf-8').read()
FP = json.load(io.open(u'corpus/_b70flat.json', encoding='utf-8'))
DER = json.load(io.open(u'corpus/_deriv70.json', encoding='utf-8'))
SRC = [u'corpus/raw/udpCK/rfc768.txt', u'corpus/raw/tcpRTO/rfc1122.txt',
       u'corpus/raw/udpCK/rfc8200.txt', u'corpus/raw/udpCK/rfc6935.txt']
SHW = [u'`raw/udpCK/rfc768.txt`', u'`raw/tcpRTO/rfc1122.txt`', u'`raw/udpCK/rfc8200.txt`', u'`raw/udpCK/rfc6935.txt`']
LBL = [u'768', u'1122', u'8200', u'6935']
YR = [u'80', u'89', u'17', u'13']
ANS = [u'零值直说“没算”、全篇零枚大写义务词、一种进制都不给',
       u'能力 MUST ⇎ 每报文 MAY optionally ⇎ 默认 MUST 开, 同节注里又写 UDP checksum is optional',
       u'IPv6 侧整句降成小写 must: not optional 是默认行为、零值改 hex FFFF',
       u'引那份小写原文判它该删、换大写 MUST 并插 by default, 且比它更新的 8200 早四年发出']

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
BS, LN, NB, EF, FFC, CR, NA, ML, DELTA, EXTRA = [], [], [], [], [], [], [], [], [], []
BOM = []
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
# 换页符全部独占整行(EF=FFC) ⇎ 建条目侧 ff_only 按 x.strip()=='\x0c' 判定——strip 本身吃掉 \x0c, 该档恒零(口径陷阱, 如实入注)
assert EF == FFC == gk(u'ff')
assert [BS, LN, NB, CR, NA, ML, DELTA, EXTRA, BOM] == \
       [gk(u'bytes'), gk(u'lines'), gk(u'nonblank'), gk(u'cr'),
        gk(u'nonascii'), gk(u'maxlen'), gk(u'byte_cp_delta'), gk(u'nonascii_extra'), gk(u'bom')]
assert gk(u'ff_only') == [len([1 for x in xs if x.strip() == u'\x0c']) for xs in LF4] == [0, 0, 0, 0]
assert gk(u'chars') == [len(t) for t in T4]


def bcnt(t, w):
    """手写字母边界扫描: 前后邻字不是字母才计数(与二遍的正则词界、四遍的 findall 各走一路)"""
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


UPM = [bcnt(t, u'MUST') for t in T4]
UPN = [occ(t, u'MUST NOT') for t in T4]
LOW = [bcnt(t, u'must') for t in T4]
CIM = [bcnt(t.lower(), u'must') for t in T4]
OPTW = [occ(t, u'optional') for t in T4]
assert UPM == gk(u'up_must_all') and UPN == gk(u'must_not')
assert [UPM[i] - UPN[i] for i in range(4)] == gk(u'must_bare')
assert LOW == gk(u'low_must')
assert CIM == gk(u'ci_must')
assert [gk(u'up_ledger')[i] for i in range(4)] == [0, 0, 0, 0]
assert [gk(u'case_ledger')[i] for i in range(4)] == [0, 0, 0, 0]
assert OPTW == gk(u'opt_word')

# ---- 三面阶梯: 逐行 ⇎ 全篇折平 ⇎ 剥壳折平(剥壳谓词从建条目侧源码切出 exec) ----
MS = io.open(u'corpus/_mkB70.py', encoding='utf-8').read()
SHELL_SRC = re.search(u'def shell_line\\(l\\):.*?\\n(?=SH = \\[)', MS, re.S).group(0)
NS = {}
exec(u'import re\n' + SHELL_SRC, NS)
is_shell = NS[u'shell_line']
TAB = {}
for st in __import__('ast').parse(MS).body:
    if isinstance(st, __import__('ast').Assign) and isinstance(st.targets[0], __import__('ast').Name):
        if st.targets[0].id == u'NEEDLE':
            TAB[u'NEEDLE'] = __import__('ast').literal_eval(st.value)
NEEDLE = TAB[u'NEEDLE']
OWNER = dict((k, o) for o, k, _ in NEEDLE)
NEEDL = dict((k, nd) for o, k, nd in NEEDLE)
KEYS = [k for _, k, _ in NEEDLE]
FOLD4 = [re.sub(u'\\s+', u' ', t) for t in T4]
SHF4 = [re.sub(u'\\s+', u' ', u'\n'.join([l for l in LF4[i] if not is_shell(l)])) for i in range(4)]


def nz(nd):
    return re.sub(u'\\s+', u' ', nd).lower()


STRICT, FOLDD, SHD = [], [], []
for i in range(4):
    o = [k for k in KEYS if OWNER[k] == i]
    STRICT.append(len([k for k in o if any(NEEDL[k] in l for l in LF4[i])]))
    FOLDD.append(len([k for k in o if re.sub(u'\\s+', u' ', NEEDL[k]) in FOLD4[i]]))
    SHD.append(len([k for k in o if re.sub(u'\\s+', u' ', NEEDL[k]) in SHF4[i]]))
assert len(KEYS) == gk(u'needle_n')
assert STRICT == gk(u'sn_strict_docs') and FOLDD == gk(u'sn_fold_docs') and SHD == gk(u'sn_sh_docs')
FONLY = [k for k in KEYS if re.sub(u'\\s+', u' ', NEEDL[k]).lower() in nz(FOLD4[OWNER[k]])
         and not any(NEEDL[k] in l for l in LF4[OWNER[k]])]
assert FONLY == gk(u'fold_only_keys'), (FONLY, gk(u'fold_only_keys'))
FOWN = [len([k for k in FONLY if OWNER[k] == i]) for i in range(4)]
assert FOWN == gk(u'fold_only_own')
assert [gk(u'sn_fold_docs')[i] - gk(u'sn_sh_docs')[i] for i in range(4)] == gk(u'sh_minus_fold')
assert sum(STRICT) + sum(FOWN) == sum(FOLDD)
NOTOPT = [occ(re.sub(u'\\s+', u' ', t).lower(), u'not optional') for t in T4]
assert NOTOPT == gk(u'not_opt')

# ---- 锚的归一分类(串取自条目编码区, 归类只看小写折叠面) ----
ENT = io.open(u'corpus/babeltele/B70_udp_checksum_mandatory_four_answers.md', encoding='utf-8').read()
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
assert APAIR[(u'8200', u'6935')] == 7 and ATRI == 1 and AALL4 == 0


def bkeys(s):
    o = set()
    for ch in s.split(u'B70V(')[1:]:
        q = ch[0]
        if q in (u'"', u"'"):
            o.add(ch[1:ch.find(q, 1)])
    return o


DKEYS = len(bkeys(json.dumps(DER, ensure_ascii=False)) & set(FP))
assert 0 < DKEYS < len(FP), DKEYS
CLOSEK = len([k for k in FP if u'close' in k])

# ---- 门槛表 B70 行 ----
GCOL = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B70 |'):
        GCOL = [x.strip() for x in l.split(u'|')[1:-1]]
assert GCOL and len(GCOL) >= 3, GCOL
DIG70 = num(GCOL[1])
E70 = num(GCOL[2])
assert E70 == gk(u'enc_chars'), (E70, gk(u'enc_chars'))
HEADROW = (u'| B70 | ' + fmt(E70) + u'（新建, 一条 UDP 报文的校验和到底是不是非算不可、算出零值怎么办 交四份 UDP 一手文书各答一遍 '
           + str(gk(u'anchor_total')) + u' 处标注／' + str(gk(u'anchor_distinct'))
           + u' 个不同串（登记全命中, 单源 ' + str(gk(u'anchor_single')) + u' ⇎ 穿二三源 ' + str(gk(u'anchor_cross'))
           + u' ⇎ 四源全现 ' + str(gk(u'anchor_all4')) + u'——穿源的 ' + str(gk(u'anchor_cross'))
           + u' 枚按归一折叠面配对 8200⇎6935 ' + str(APAIR[(u'8200', u'6935')])
           + u' ⇎ 三源共现 1 枚（那一枚是标题页的通用套行, 共现于 '
           + u'⇎'.join(x for x in [k for k in APAIR if len(k) == 3][0]) + u'）, 四源同现零枚; 长行池的最大一对 8200⇎6935（'
           + fmt(gk(u'pair_share')[5]) + u' 归一／' + str(gk(u'pair_byte')[5]) + u' 逐字节／'
           + str(gk(u'pair_norm_only')[5]) + u' 仅归一）, 归属检查 '
           + str(gk(u'checks')) + u' 次, 错配 ' + str(gk(u'anchor_err')) + u'）: 四色锚位 '
           + u' ⇎ '.join(x + u' ⟦' + y + u'⟧' for x, y in zip(LBL, u'ABCD'))
           + u'; 答句四种（零值直说没算 ⇎ 三层拆分自带矛盾 ⇎ 降成小写默认行为 ⇎ 引原文判删再整句升格）: '
           + u' ⇎ '.join(ANS) + u'; 三面阶梯（原面 ⇎ 全篇折平 ⇎ 摘壳折平）按文档读到 '
           + u'⇎'.join(str(x) for x in STRICT) + u' ／ ' + u'⇎'.join(str(x) for x in FOLDD) + u' ／ '
           + u'⇎'.join(str(x) for x in SHD) + u'（针表 ' + str(gk(u'needle_n')) + u' 枚, 折平才现 '
           + str(gk(u'fold_only_n')) + u' 枚, 按份新增 ⇎'.join(str(x) for x in FOWN)
           + u'——8200 的答句整段被行界劈开：逐行档 ' + str(gk(u'sn_strict_docs')[2]) + u' 枚, 折平档 '
           + str(gk(u'sn_fold_docs')[2]) + u' 枚, 本条的必需通道是折行而非摘壳（摘壳比折平少 '
           + L4(gk(u'sh_minus_fold')) + u' 枚, 单调 ' + str(gk(u'ladder_monotone')) + u'）; 锚池 '
           + fmt(gk(u'pool_n')) + u' 条分档 ' + u'⇎'.join(fmt(x) for x in gk(u'pool_tier')) + u'（闭合 '
           + str(gk(u'pool_tier_close')) + u'）, 四份同现长行 ' + str(gk(u'pool_4')) + u' 条 ⇒ 写法轴档只开一 '
           + gk(u'axis_str') + u'（轴账闭合 ' + str(gk(u'axis_close')) + u'）——8200⇎6935 共有的 '
           + str(gk(u'pair_share')[5]) + u' 条长行里 ' + str(gk(u'pair_byte')[5]) + u' 条逐字节同形'
           u'（全是 IETF 许可/状态样板与 [RFC2460]／[RFC6936] 参考文献行）, 唯一归一同形而逐字节不同是那条 FFFF 句（只差缩进）; '
           u'义务语气四轨: MUST 全计 ' + L4(gk(u'up_must_all')) + u' ⇎ 裸 MUST ' + L4(gk(u'must_bare')) + u' ⇎ MUST NOT '
           + L4(gk(u'must_not')) + u'（大写账 ' + L4(gk(u'up_ledger')) + u'）⇎ 小写 must ' + L4(gk(u'low_must'))
           + u' ⇎ 不分大小写 ' + L4(gk(u'ci_must')) + u'（大小写账 ' + L4(gk(u'case_ledger'))
           + u'）——8200 带 STD 号与 Proposed Standard 类别行（' + str(gk(u'std_hdr')[2]) + u'⇎' + str(gk(u'cat_std')[2])
           + u'）而全篇大写义务词 ' + str(gk(u'up_must_all')[2]) + u' 枚（判定 ' + str(gk(u'std_no_upper')) + u'）; 同一枚补码值两种进制: '
           u'十进制游标 ' + fmt(gk(u'num_all1s_dec')) + u'（1122）⇎ 十六进制折十 ' + fmt(gk(u'num_ffff_8200')) + u'⇎'
           + fmt(gk(u'num_ffff_6935')) + u'（8200⇎6935）, 三读数闭合 ' + str(gk(u'base_value_agree')) + u' ⇎ 768 一种进制都不给'
           u'（给进制份数 ' + str(gk(u'num_radix_face_n')) + u' ⇎ 游标落空 ' + str(gk(u'num_cursor_miss')) + u'）; optional 的贴法 '
           + L4(gk(u'opt_word')) + u' ⇎ “not optional”折平 ' + L4(gk(u'not_opt')) + u' ⇎ 逐行 ' + L4(gk(u'not_opt_line'))
           + u'; 谁改谁现读: 8200 Obsoletes ' + str(gk(u'obs_n')[2]) + u' 枚 ⇎ 6935 Updates ' + str(gk(u'upd_n')[3])
           + u' 枚, 对象并集只 ' + str(gk(u'target_n')) + u' 枚（同一对象闭合 ' + str(gk(u'both_2460')) + u'）, 标题页年份 '
           + L4(gk(u'years')) + u'（倒序 ' + str(gk(u'year_inversions')) + u' 处, 6935 比它更新的 8200 早 '
           + str(gk(u'year_gap_6935_8200')) + u' 年, 置换闭合 ' + str(gk(u'year_perm_close')) + u'）; 同数共键 '
           + str(len(DER)) + u' 枚算式／' + str(gk(u'x_ident_n')) + u' 条面内恒等式（标量闭账 ' + str(gk(u'scalar_clos_n'))
           + u' 项, 通过 ' + str(gk(u'scalar_clos_sum')) + u' ⇎ 含 close 的键 ' + str(CLOSEK) + u' 枚其中逐份清单 '
           + str(gk(u'list_clos_n')) + u' 枚）, 扁平契约 ' + str(len(FP))
           + u' 枚键全数复测; 五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对锚逐字复核'
           u'；工具侧 atomcheck 的 SRC 表未登记本条, 四份纯文本面的逐字性由门槛侧 ' + str(gk(u'checks'))
           + u' 次归属检查承担（逐字命中 ' + str(gk(u'anchor_total')) + u' 处 ⇎ 错配 ' + str(gk(u'anchor_err')) + u'） |')

SRCLINE = SHW
C70 = (u'| B70 | ' + u' ⇎ '.join(
    SRCLINE[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／面内码位 ' + fmt(gk(u'chars')[i])
    + u'／行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i]) + u'（换页符 ' + str(FFC[i]) + u' 枚，独占整行 ' + str(EF[i])
    + u' 行）／最长行 ' + str(ML[i]) + u' 列／答句 ' + ANS[i] + u'／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i])
    + u'／BOM ' + str(BOM[i]) + u'）' for i in range(4))
           + u' | 四份答同一个问题 ⇒ 768 全篇大写义务词 ' + str(gk(u'up_must_all')[0]) + u' 枚, 把“没算”写成零值本身（'
             u'“all ones”句 ' + str(gk(u'num_cursor_miss')) + u' 枚游标之外, 一种进制都不给）而唯一的 optional 贴在 Source Port 上 ⇎ '
             u'1122 拆三层: 能力 MUST implement ⇎ 每报文 ' + str(gk(u'low_must')[1]) + u' 枚小写 must 同文 ⇎ 默认 MUST default to '
             u'checksumming on, 同一节 IMPLEMENTATION 注却写 the UDP checksum is optional（离默认句 '
             + str(gk(u'ctrl_opt_span')) + u' 行 ⇎ 离能力句 ' + str(gk(u'impl_opt_span')) + u' 行），还把 TCP 侧写成 never optional（全库恰 '
             + str(sum(gk(u'never_opt'))) + u' 枚） ⇎ 8200 把 IPv6 那句整段降成小写（大写 ' + str(gk(u'up_must_all')[2])
             + u' ⇎ 小写 ' + str(gk(u'low_must')[2]) + u'），零值改 hex FFFF ⇎ 6935 引用那份小写原文并下令删除（删除指令 '
             + str(gk(u'delete_order')) + u' 枚, [RFC2460] 方括号 ' + str(gk(u'quote_marker_6935'))
             + u' 枚）再换成大写 MUST＋插入 by default; 引用单向: 8200 面上引 6935 ' + str(gk(u'cite_dir_8200_to_6935'))
             + u' 枚 ⇎ 6935 面上引 8200 ' + str(gk(u'cite_dir_6935_to_8200')) + u' 枚（判定 ' + str(gk(u'cite_dir_unique'))
             + u'）——可是 6935 比 8200 早 ' + str(gk(u'year_gap_6935_8200')) + u' 年; 三面阶梯在本条只有一处空转在 8200 的逐行档（'
             + str(gk(u'sn_strict_docs')[2]) + u' 枚），' + str(gk(u'fold_only_n')) + u' 枚整句被行界劈开靠折行救回 |' + NL)

PARA = (u'**B70 问的是一条 UDP 报文的校验和到底是不是非算不可、算出零值该怎么办，四份一手文书给出四种答法**：'
        + u' ⇎ '.join(SRCLINE[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
                      + u'／非空行 ' + fmt(NB[i]) + u'／换页符 ' + str(FFC[i]) + u' 枚（独占整行 ' + str(EF[i])
                      + u' 行）／答句 ' + ANS[i] + u'／非 ASCII ' + str(NA[i]) + u'／BOM ' + str(BOM[i]) + u'）'
                      for i in range(4))
        + u'——四份同为 RFC Editor 的纯文本面, 全 LF、行长一律 ' + str(ML[0]) + u' 列封顶, 换页符共 ' + str(sum(FFC))
          + u' 枚且全部独占整行（' + L4(EF) + u' 行, 逐枚 ' + L4(FFC) + u'）, 而建条目侧 ff_only 按 x.strip()==FF 判——strip 先吃掉换页符本身, 该档恒零（'
          + L4(gk(u'ff_only')) + u', 口径陷阱如实记）, 字节−码位差 ' + L4(DELTA)
          + u' 与非 ASCII 加字节 ' + L4(EXTRA) + u' 同为全零（纯 ASCII 面 ' + str(gk(u'ascii_all')) + u' 份）, 名分头按份计 STD '
          + L4(gk(u'std_hdr')) + u' ⇎ 类别行 Proposed Standard ' + L4(gk(u'cat_std')) + u'。768 全篇大写义务词 '
          + str(gk(u'up_must_all')[0]) + u' 枚——它连“可以不算”都不写成权利, 只把零值写成“没算”（“all ones”一个数字都不给, '
          + str(gk(u'opt_word')[0]) + u' 枚 optional 唯一贴在 Source Port 上, 与 checksum 同枚 '
          + str(gk(u'opt_line_ck')[0]) + u'）⇎ 1122 把同一件事拆成三层: 能力 MUST implement ⇎ 应用 MAY optionally 控制 ⇎ 默认 '
          + u'MUST default to checksumming on（游标读出十进制 ' + fmt(gk(u'num_all1s_dec')) + u'）, 却在同一节 IMPLEMENTATION 注里写 '
          u'the UDP checksum is optional——它离默认句 ' + str(gk(u'ctrl_opt_span')) + u' 行、离能力句 '
          + str(gk(u'impl_opt_span')) + u' 行（先后向判定 ' + str(gk(u'opt_vs_must_dir')) + u'）, 还自认 controversial ⇎ '
          u'8200 在 IPv6 侧把整句降成小写: not optional 是默认行为（折平 ' + str(gk(u'not_opt')[2]) + u' 枚 ⇎ 逐行 '
          + str(gk(u'not_opt_line')[2]) + u' 枚——那句被行界劈开）, 零值改 hex FFFF（游标折十 ' + fmt(gk(u'num_ffff_8200'))
          + u'）, 全篇大写 ' + str(gk(u'up_must_all')[2]) + u' 枚 ⇎ 小写 ' + str(gk(u'low_must')[2])
          + u' 枚, 而它带着 STD 号与 Proposed Standard 类别行（判定 ' + str(gk(u'std_no_upper')) + u'/' + str(gk(u'low_only_8200'))
          + u'）⇎ 6935 同时做两件事: 把 8200 那条小写规则引出来判“该删”（删除指令 ' + str(gk(u'delete_order')) + u' 枚, [RFC2460] '
          + str(gk(u'quote_marker_6935')) + u' 枚）, 再换上大写 MUST 并插入 by default（' + str(gk(u'repl_bydefault'))
          + u' 枚）把“必须丢弃”降成默认丢弃。同一条规则在两处的词级差可以逐词算: 三段定界起 ' + L4(gk(u'blk_lo'))
          + u' ⇎ 止 ' + L4(gk(u'blk_hi')) + u' 行（占 ' + L4(gk(u'blk_rows')) + u' 行）, 8200 段与 6935 引文共有词 '
          + str(gk(u'w_common')) + u' 枚、各自独有 ' + str(gk(u'w82_only_n')) + u'⇎' + str(gk(u'w6q_only_n'))
          + u' 枚（词集闭合 ' + str(gk(u'w_row_close')) + u'）, 共尾 ' + str(gk(u'suf_82_q69')) + u' 枚词 ⇎ 共头只到 '
          + str(gk(u'pre_82_q69')) + u' 枚——尾巴接得上、头被换掉; 语气换向 ' + str(gk(u'tone_swap'))
          + u' 枚（枚数一枚不动只换字面档）, 反向三项之和 ' + str(gk(u'tone_rev_close')) + u'——三段各只活一种语气。'
          u'进制面: 同一枚补码值 1122 写十进制 ⇎ IPv6 两份写 hex FFFF 折十 ' + fmt(gk(u'num_ffff_6935')) + u'（三读数闭合 '
          + str(gk(u'base_value_agree')) + u'）, 768 不给数; 位宽 16 ⇎ 128 ⇎ 32, 比值 ' + str(gk(u'bits_ratio128')) + u'⇎'
          + str(gk(u'bits_ratio32')) + u'（整除闭合 ' + str(gk(u'bits128_close')) + u'/' + str(gk(u'bits32_close')) + u'）。'
          u'谁抄谁可量: 归一长行两两交集 ' + L4(gk(u'pair_share')) + u' ⇎ 逐字节同形 ' + L4(gk(u'pair_byte')) + u' ⇎ 仅归一 '
          + L4(gk(u'pair_norm_only')) + u'（非零对 ' + str(gk(u'pair_nonzero')) + u', 配对闭合 ' + str(gk(u'pair_close'))
          + u'）——唯一非零对 8200⇎6935 归一 ' + str(gk(u'pair_share')[5]) + u' 行里 ' + str(gk(u'pair_byte')[5])
          + u' 行逐字节同形（全是许可/状态样板与参考文献行）, 仅归一的那一行就是 FFFF 句（只差缩进）⇒ 真正的内容差全在句子内部; '
          '四份同现长行 ' + str(gk(u'pool_4')) + u' 条 ⇒ 写法轴只开一 ' + gk(u'axis_str') + u'（轴账闭合 '
          + str(gk(u'axis_close')) + u'）——本条的分裂不住在写法上而住在“大小写与默认值”上。三面阶梯: 在册 '
          + str(gk(u'needle_n')) + u' 枚答句针按原面读到 ' + u'⇎'.join(str(x) for x in STRICT) + u'、全篇折平 '
          + u'⇎'.join(str(x) for x in FOLDD) + u'、摘壳折平 ' + u'⇎'.join(str(x) for x in SHD) + u'——最刺眼的是 8200: '
          '逐行档 ' + str(gk(u'sn_strict_docs')[2]) + u' 枚, 它的答句整段被行界劈开, 只按逐行口径搜就会把这份读成“没写这条规则”; '
          '折行独有 ' + str(gk(u'fold_only_n')) + u' 枚按份新增 ⇎'.join(str(x) for x in FOWN) + u', 阶梯单调 '
          + str(gk(u'ladder_monotone')) + u'; 摘壳档比折平档一粒不少（差 ' + L4(gk(u'sh_minus_fold'))
          + u'）——本条必需的是折行而不是摘壳。语气换代不按时钟走: 标题页年份 ' + L4(gk(u'years')) + u', 恰一处倒序 '
          + str(gk(u'year_inversions')) + u'——写小写默认行为的 8200（' + str(gk(u'years')[2]) + u'）比把它改回大写的 6935（'
          + str(gk(u'years')[3]) + u'）晚 ' + str(gk(u'year_gap_6935_8200')) + u' 年发出, 而 6935 的 Updates: 2460 ⇎ 8200 的 Obsoletes: 2460 '
          '指向同一对象（并集 ' + str(gk(u'target_n')) + u' 枚, 闭合 ' + str(gk(u'both_2460')) + u'）, 互引只单向（8200 面上引 6935 '
          + str(gk(u'cite_dir_8200_to_6935')) + u' 枚 ⇎ 反向 ' + str(gk(u'cite_dir_6935_to_8200')) + u' 枚, 判定 '
          + str(gk(u'cite_dir_unique')) + u'）——“大写替代段在前、小写默认行为在后”这件反直觉的事在四份自己的字节里就读得出。'
          '引用三式并计: 2460 空格式 ⇎ 短横式 ⇎ 连写式逐份 ' + L4(gk(u'cite_al_2460')) + u'（写法族账 ' + L4(gk(u'cite_forms_close'))
          + u'）, 6935 用连写式把被改的那份钉在括号里。答句邻域按 ±' + str(gk(u'win_band')) + u' 行带切, 五轨（checksum ⇎ zero ⇎ '
          'optional ⇎ 大写义务词 ⇎ 数字符）带内外分账闭合 ' + str(gk(u'win_close_sum')) + u'。门槛侧 ' + str(len(DER))
          + u' 枚算式／' + str(gk(u'x_ident_n')) + u' 条面内恒等式（标量 ' + str(gk(u'scalar_clos_n')) + u' 项通过 '
          + str(gk(u'scalar_clos_sum')) + u'）, 扁平契约 ' + str(len(FP)) + u' 枚键由第四 ⇎ 第五套实现逐枚复测; 其中 ' + str(DKEYS)
          + u' 枚进得了 DERIV 算式 ⇎ 余下 ' + str(len(FP) - DKEYS) + u' 枚是形状清单、字符串表与窗口切片; '
          + str(len(ASTR)) + u' 枚不同锚串按折叠面重分类 单源 ' + str(ASIN) + u' ⇎ 穿二源 ' + str(ACRO2) + u' ⇎ 穿三源 '
          + str(ATRI) + u' ⇎ 四源 ' + str(AALL4) + u', 与门槛登记口径一致。')

L = S.split(NL)
assert L and S.count(u'**B70 问的是') == 0
assert S.count(u'| B70 |') == 0


def sub(old, new, s, cnt=1):
    assert s.count(old) == cnt, (u'锚点不唯一', old[:60], s.count(old))
    return s.replace(old, new)


def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:60])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


# ---- 1) 判词段(紧跟 B69 段) 2) 门槛表行 3) 语料表行 ----
S = after(S, u'**B69 问的是主动关掉一条 TCP 连接之后到底要等多久', PARA + NL + NL)
S = after(S, u'| B69 | 8 042（新建,', HEADROW + NL)
S = after(S, u'| B69 | `raw/tcpTW/rfc793.txt`', C70)

# ---- 4) 转化指标表: 按 audit 当下输出补 B70 机械行, 合计行按 ALL 行现算 ----
ROWS = {}
ALLR = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        c = [x.strip() for x in l.split(u'|')[1:-1]]
        ROWS[c[0]] = c
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR and len(ROWS) == 69, (len(ROWS), bool(ALLR))
L = S.split(NL)
h = [i for i, l in enumerate(L) if l.startswith(u'| entry | 编码字符 |')]
assert len(h) == 1, h
tot = [i for i in range(h[0], len(L)) if L[i].startswith(u'| **合计（')]
assert len(tot) == 1, tot
T = tot[0]
present = [l.split(u'|')[1].strip() for l in L[h[0] + 2:T]]
assert all(p.startswith(u'B') for p in present), present[:3]
missing = [k for k in sorted(ROWS, key=lambda k: int(k[1:])) if k not in present]
assert missing == [u'B70'], missing
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
            + u'，本遍补记的一枚为 ' + fmt(E70) + u' 编码／' + fmt(DIG70)
            + u' 摘要；条目数与两列合计均取自本遍现跑的 audit，唯一码点那格取本遍 ALL 行现算值） ')
cells[5] = u' **%s** ' % fmt(UNIQ_ALL)
assert len(cells) == len(OLD.split(u'|')), (len(cells), len(OLD.split(u'|')))
L[T + 1] = u'|'.join(cells)
NOTE = [i for i, l in enumerate(L) if l.startswith(u'（B54 起的 ') and u'机械行' in l]
assert len(NOTE) == 1, NOTE
L[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与'
              u'字符/语义单元五格, 不重写各条的口径注; 本遍再直补 B70 一枚, 合计行的唯一码点即 ALL 行那个全库并集值。）'
              % len([x for x in present + missing if int(x[1:]) >= 54]))
S = NL.join(L)

# ---- 5) 条数与推导数 ----
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])
S = sub(u'共 **68 条**（`babeltele/B01..B65、B67..B69`, 本遍补上 B69 的四处记账行, 合计按 audit 当下输出重算）',
        u'共 **69 条**（`babeltele/B01..B65、B67..B70`, 本遍补上 B70 的四处记账行, 合计按 audit 当下输出重算）', S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（68 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（69 条）', S)
PV = [l for l in S.split(NL) if u'条语料／' in l and u'推导全部通过' in l]
assert len(PV) == 1, PV
i0 = PV[0].find(u'当前 **')
j = PV[0].find(u'）', PV[0].find(u'audit 自报', i0))
while PV[0][j + 1:j + 2] == u'）':
    j += 1
S = S[:S.find(PV[0]) + i0] + (u'当前 **69 条语料／' + str(PROOFS) + u' 条**推导全部通过（audit 自报“已机检的推导 '
                              + str(PROOFS) + u' 条”）') + S[S.find(PV[0]) + j + 1:]

CMD = u'python -X utf8 corpus/_fill69.py'
assert S.count(CMD) == 1
S = after(S, u'python -X utf8 corpus/_fill69.py',
          u'python -X utf8 corpus/_mkB70.py                    # 建条目(前半, 与 _mk70emit.py 同场 exec): 扁平契约 '
          + str(len(FP)) + u' 枚键／恒等式 ' + str(gk(u'x_ident_n')) + u' 条 ⇎ DERIV ' + str(len(DER))
          + u' 枚算式, 非重叠游标 ⇎ 正则字面轨 ⇎ 集合代数三机制, 采集侧对账 0 不符' + NL)
S = after(S, u'python -X utf8 corpus/_mkB70.py',
          u'python -X utf8 corpus/_mkdigest3.py B70 <entry> 768 corpus/raw/udpCK/rfc768.txt 160 260 '
          u'1122 corpus/raw/tcpRTO/rfc1122.txt 160 260 8200 corpus/raw/udpCK/rfc8200.txt 160 260 '
          u'6935 corpus/raw/udpCK/rfc6935.txt 160 260   # 四源分节摘要(' + fmt(DIG70) + u' 字符, '
          + str(gk(u'anchor_total')) + u'/' + str(gk(u'anchor_total')) + u' 锚全命中)' + NL)
S = after(S, u'python -X utf8 corpus/_mkdigest3.py B70',
          u'python -X utf8 corpus/_wire70.py                    # 幂等接线: SRC/ATOM/SCAN(审计器侧第三套实现)/DERIV/'
          u'B70V 进 audit.py, 落盘前复跑 ' + str(len(FP)) + u' 枚扁平键 ⇎ ' + str(len(DER)) + u' 枚算式' + NL)
S = after(S, u'python -X utf8 corpus/_wire70.py',
          u'python -X utf8 corpus/_fill70.py                    # 第四遍: 三面阶梯⇎段落双尺⇎集合代数⇎词轨各重导一次, '
          + str(gk(u'x_ident_n')) + u' 条恒等式现算归零后写回 ⛓解读注（16 行复测表 ⇎ 复算 339 键对账 0 不符 ⇎ 独有 2 枚）' + NL)

io.open(u'corpus/README.md', 'w', encoding='utf-8', newline=NL).write(S)
json.dump(dict(entries=len(ROWS), enc=enc_all, dig=dig_all, proofs=PROOFS, b70_enc=E70, b70_dig=DIG70,
               bytes=BS, lines=LN, nonblank=NB, formfeed_only=EF, ff_occ=FFC, cr=CR, nonascii=NA, bom=BOM,
               maxlen=ML, strict=STRICT, fold=FOLDD, sh=SHD, fold_only_n=gk(u'fold_only_n'),
               fold_only_own=FOWN, up=UPM, low=LOW, ci=CIM, opt=OPTW, notopt=NOTOPT,
               close_keys=CLOSEK, uniq_all=UNIQ_ALL, keys=len(FP), deriv=len(DER),
               ident=gk(u'x_ident_n'), pairs=gk(u'pair_share'), pairs_byte=gk(u'pair_byte')),
          io.open(u'corpus/_b70readme.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（69 条）编码 ' + fmt(enc_all) + u' ⇎ 摘要 ' + fmt(dig_all) + u' ⇎ 保留 '
      + u'%.1f%%' % (100.0 * enc_all / dig_all) + u' ｜ 推导 ' + str(PROOFS) + u' 条 ｜ B70 行 ' + fmt(E70)
      + u'／' + fmt(DIG70) + u' ｜ 锚 ' + str(gk(u'anchor_total')) + u' 处⇎错配 ' + str(gk(u'anchor_err'))
      + u' ｜ 三面阶梯 ' + u'⇎'.join(str(x) for x in STRICT) + u'／' + u'⇎'.join(str(x) for x in FOLDD)
      + u'／' + u'⇎'.join(str(x) for x in SHD) + u' ｜ 折行独有 ' + str(gk(u'fold_only_n')) + u' 枚'
      + u' ｜ 逐份字节 ' + u'⇎'.join(fmt(x) for x in BS))
