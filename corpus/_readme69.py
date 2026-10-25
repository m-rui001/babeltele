# -*- coding: utf-8 -*-
"""README 记账第五遍(B69): 判词段 ⇎ 门槛表行 ⇎ 语料表行 ⇎ 转化指标行 ⇎ 聚合行, 全按本遍现跑的 audit
与 raw 字节现量, 一个数都不抄建条目侧快照。
本遍的第五套实现: 字面量直接吃二进制面(字节数 ⇎ 行数按 \\n 计数而非 splitlines ⇎ 码位 ⇎ 换页符两种口径),
三面阶梯按“逐行 re.search ⇎ 全篇 \\s+ 折平 ⇎ 剥壳后折平”三条通道各自重导, 与 _b69flat.json 逐键对账。"""
import io, json, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\r\n' if u'\r\n' in io.open(u'corpus/README.md', encoding='utf-8').read() else u'\n'
S = io.open(u'corpus/README.md', encoding='utf-8').read()
FP = json.load(io.open(u'corpus/_b69flat.json', encoding='utf-8'))
DER = json.load(io.open(u'corpus/_deriv69.json', encoding='utf-8'))
SRC = [u'corpus/raw/tcpTW/rfc793.txt', u'corpus/raw/tcpRTO/rfc1122.txt',
       u'corpus/raw/tcpTW/rfc6528.txt', u'corpus/raw/tcpTW/rfc9293.txt']
SHW = [u'`raw/tcpTW/rfc793.txt`', u'`raw/tcpRTO/rfc1122.txt`', u'`raw/tcpTW/rfc6528.txt`', u'`raw/tcpTW/rfc9293.txt`']
LBL = [u'793', u'1122', u'6528', u'9293']
YR = [u'81', u'89', u'12', u'22']
ANS = [u'定 MSL 为“2 minutes”却同段许可违背 quiet time', u'MUST linger 2xMSL 但两条件下 MAY 立刻接受新 SYN',
       u'不问等待、从 last seen 起算 2*MSL', u'收下 2 分钟句、主语改 endpoint 并 Obsoletes 前三份']

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
BS, LN, NB, FF, FFC, CR, NA, ML, DELTA, EXTRA = [], [], [], [], [], [], [], [], [], []
BOM, TOK, CIT, MUSTS = [], {}, {}, []
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
    FF.append(len([x for x in LF4[-1] if x == u'\x0c']))
    FFC.append(occ(raw, u'\x0c'))
    CR.append(occ(raw, u'\r'))
    NA.append(len([c for c in raw if ord(c) > 127]))
    ML.append(max(len(x) for x in LF4[-1]))
    DELTA.append(len(b) - len(raw))
    EXTRA.append(sum(len(c.encode('utf-8')) - 1 for c in raw if ord(c) > 127))
    BOM.append(1 if raw.startswith(u'﻿') else 0)
    assert NB[-1] + FF[-1] <= LN[-1]
for k, nd in [(u'msl', u'MSL'), (u'tw', u'TIME-WAIT'), (u'twospace', u'TIME-WAIT state'),
               (u'f2msl', u'2MSL'), (u'f2x', u'2xMSL'), (u'f2star', u'2*MSL'), (u'f2xsp', u'2 x MSL'),
               (u'quiet', u'quiet'), (u'linger', u'linger'), (u'c2m', u'2 minutes'),
               (u'isn', u'ISN'), (u'iss', u'ISS'), (u'ka', u'keep-alive'), (u'timestamp', u'Timestamp'),
               (u'reboot', u'reboot'), (u'up_must_all', u'MUST'), (u'must_not', u'MUST NOT')]:
    TOK[k] = [occ(t, nd) for t in T4]
for k, nd in [(u'r793d', u'RFC-793'), (u'r793s', u'RFC 793'), (u'r1122d', u'RFC-1122'), (u'r1122s', u'RFC 1122')]:
    CIT[k] = [occ(t, nd) for t in T4]
MUSTS = [len(re.findall(u'\\bMUST(?! NOT)\\b', t)) for t in T4]
for k in (u'msl', u'tw', u'twospace', u'f2msl', u'f2x', u'f2star', u'f2xsp', u'quiet', u'linger', u'c2m',
          u'isn', u'iss', u'ka', u'timestamp', u'reboot', u'up_must_all', u'must_not'):
    assert TOK[k] == gk(k), (k, TOK[k], gk(k))
assert CIT[u'r793d'] == gk(u'r793d') and CIT[u'r793s'] == gk(u'r793s')
assert CIT[u'r1122d'] == gk(u'r1122d') and CIT[u'r1122s'] == gk(u'r1122s')
assert MUSTS == gk(u'must_bare') == gk(u'up_must')
assert [BS, LN, NB, FF, FFC, CR, NA, ML, DELTA, EXTRA, BOM] == \
       [gk(u'bytes'), gk(u'lines'), gk(u'nonblank'), gk(u'ff_only'), gk(u'ff'), gk(u'cr'),
        gk(u'nonascii'), gk(u'maxlen'), gk(u'byte_cp_delta'), gk(u'nonascii_extra'), gk(u'bom')]
FORMALL = [TOK[u'f2msl'][i] + TOK[u'f2x'][i] + TOK[u'f2star'][i] + TOK[u'f2xsp'][i] for i in range(4)]
assert FORMALL == gk(u'form_all') and LBL and True

# ---- 三面阶梯: 逐行 ⇎ 全篇折平 ⇎ 剥壳折平(剥壳谓词照抄建条目侧的三条头规与脚规) ----
NEEDLE = [
    (0, u'a_quiet', u'the TCP must keep quiet for a maximum segment lifetime'),
    (0, u'a_msl2', u'For this specification the MSL is taken to be 2 minutes.'),
    (0, u'a_eng', u'is an engineering choice, and may be changed if experience indicates'),
    (0, u'a_violate', u'TCP implementors may violate the "quiet time" restriction, but only'),
    (0, u'a_arb2', u'Arbitrarily defined to be 2 minutes.'),
    (0, u'a_isn455', u'Thus, the ISN cycles approximately every 4.55 hours.'),
    (0, u'a_lt455', u'the MSL is less than 4.55'),
    (0, u'a_fig', u'Timeout=2MSL'),
    (1, u'b_linger', u'TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime).'),
    (1, u'b_mayaccept', u'However, it MAY accept a new SYN from the remote TCP to'),
    (1, u'b_cond1', u'assigns its initial sequence number for the new'),
    (1, u'b_cond2', u'returns to TIME-WAIT state if the SYN turns out to be'),
    (1, u'b_busy', u'local socket) pair that defines the connection is busy'),
    (1, u'b_shorten', u'port pair is tied up, some TCPs allow a new SYN to be'),
    (1, u'b_ka', u'Implementors MAY include "keep-alives" in their TCP'),
    (2, u'c_star', u'previous connection before 2*MSL have passed since a segment'),
    (2, u'c_lastseen', u'corresponding to the old incarnation was last seen (where "MSL" is'),
    (2, u'c_twref', u'the TIME-WAIT state and TCP\'s "quiet time" concept (see Appendix B of'),
    (2, u'c_quiettwo', u'kept or a quiet time observed for two maximum segment lifetimes'),
    (3, u'd_linger', u'When a connection is closed actively, it MUST linger in the TIME-WAIT'),
    (3, u'd_msl2', u'For this specification the MSL is taken to be 2 minutes.'),
    (3, u'd_endpoint', u'the TCP endpoint must keep quiet for an MSL'),
    (3, u'd_clockmust', u'A TCP implementation MUST use the above type of "clock" for clock-'),
    (3, u'd_paws', u'it is recommended to implement the'),
    (3, u'd_obsoletes', u'Obsoletes: 793, 879, 2873, 6093, 6429, 6528,'),
]
FOLD = [
    (0, u'a_eng_whole', u'This is an engineering choice, and may be changed if experience indicates it is desirable to do so.'),
    (1, u'b_two_both', u'it MUST linger in TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime). However, it MAY accept a new SYN'),
    (3, u'd_quiet_whole', u'the TCP endpoint must keep quiet for an MSL before assigning any sequence numbers upon starting up or recovering from a situation where memory of sequence numbers in use was lost.'),
]
HDR = [re.compile(u'^\\s*RFC\\d+\\s+\\S.*\\s([A-Z][a-z]+)\\s+\\d{4}\\s*$'),
       re.compile(u'^[A-Z]+\\d+\\s+.{5,}.*\\s\\d{4}\\s*$'),
       re.compile(u'^RFC\\s+\\d+\\s+\\S')]
FOOT = [re.compile(u'^\\s*\\[?Page \\d+\\]?\\s*$'), re.compile(u'^\\s*\\[Page \\d+\\]\\s*$')]


def is_shell(l):
    if u'\x0c' in l:
        return True
    return any(rx.search(l) for rx in HDR + FOOT)


FACES = []
for i in range(4):
    fold = re.sub(u'\\s+', u' ', T4[i].lower())
    sh = re.sub(u'\\s+', u' ', u'\n'.join(filter(lambda l: not is_shell(l), LF4[i])).lower())
    FACES.append((fold, sh))
STRICT, FOLDD, SHD = [], [], []
KEYS, OWNER, NEEDL = [], {}, {}
for i, k, nd in NEEDLE + FOLD:
    KEYS.append(k)
    OWNER[k] = i
    NEEDL[k] = nd


def nz(nd):
    return re.sub(u'\\s+', u' ', nd.lower())


for i in range(4):
    o = [k for k in KEYS if OWNER[k] == i]
    STRICT.append(len([k for k in o if len([1 for l in LF4[i] if NEEDL[k] in l])]))
    FOLDD.append(len([k for k in o if nz(NEEDL[k]) in FACES[i][0]]))
    SHD.append(len([k for k in o if nz(NEEDL[k]) in FACES[i][1]]))
assert len(KEYS) == gk(u'needle_n') and len(NEEDLE) + len(FOLD) == 28
assert STRICT == gk(u'sn_strict_docs') and FOLDD == gk(u'sn_fold_docs') and SHD == gk(u'sn_sh_docs')
FONLY = [k for k in KEYS if nz(NEEDL[k]) in FACES[OWNER[k]][0] and not any(NEEDL[k] in l for l in LF4[OWNER[k]])]
assert FONLY == gk(u'fold_only_keys'), (FONLY, gk(u'fold_only_keys'))
FOWN = [len([k for k in FONLY if OWNER[k] == i]) for i in range(4)]
assert FOWN == gk(u'fold_only_own')
assert [gk(u'sn_fold_docs')[i] - gk(u'sn_sh_docs')[i] for i in range(4)] == gk(u'sh_minus_fold') == [0, 0, 0, 0]
assert sum(STRICT) + sum(FOWN) == sum(FOLDD)
SHL = gk(u'ff')
assert SHL[3] == 0, SHL

# ---- 锚的归一分类(第五套实现: 串取自条目编码区, 归类只看折叠面) ----
ENT = io.open(u'corpus/babeltele/B69_tcp_timewait_linger_four_answers.md', encoding='utf-8').read()
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
                                                  gk(u'anchor_all4'), gk(u'anchor_distinct')), (ASIN, ACRO2, ATRI)


def bkeys(s):
    o = set()
    for ch in s.split(u'B69V(')[1:]:
        q = ch[0]
        if q in (u'"', u"'"):
            o.add(ch[1:ch.find(q, 1)])
    return o


DKEYS = len(bkeys(json.dumps(DER, ensure_ascii=False)) & set(FP))
assert 0 < DKEYS < len(FP), DKEYS

# ---- 门槛表 B69 行 ----
GCOL = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B69 |'):
        GCOL = [x.strip() for x in l.split(u'|')[1:-1]]
assert GCOL and len(GCOL) >= 3, GCOL
DIG69 = num(GCOL[1])
E69 = num(GCOL[2])
assert E69 == gk(u'enc_chars'), (E69, gk(u'enc_chars'))
CLOSEK = len([k for k in FP if u'close' in k])
HEADROW = (u'| B69 | ' + fmt(E69) + u'（新建, 主动关掉一条连接之后到底要等多久、这段等待能不能跳过 交四份 TCP 一手文书各答一遍 '
           + str(gk(u'anchor_total')) + u' 处标注／' + str(gk(u'anchor_distinct'))
           + u' 个不同串（登记全命中, 单源 ' + str(gk(u'anchor_single')) + u' ⇎ 穿二三源 ' + str(gk(u'anchor_cross'))
           + u' ⇎ 四源全现 ' + str(gk(u'anchor_all4')) + u'——穿源的 ' + str(gk(u'anchor_cross'))
           + u' 枚按归一折叠面配对 793⇎9293 ' + str(APAIR[(u'793', u'9293')]) + u' ⇎ 1122⇎9293 '
           + str(APAIR[(u'1122', u'9293')]) + u' ⇎ 三源共现 ' + str(ATRI)
           + u' 枚（那一枚就是状态机记号行, 三份共抄同一行而各写散文）, 四源同现零枚; 长行池的最大一对 793⇎9293（'
           + fmt(gk(u'pair_ad_share')) + u' 归一／'
           + str(gk(u'pair_ad_byte')) + u' 逐字节／' + fmt(gk(u'pair_ad_norm_only')) + u' 仅归一）, 归属检查 '
           + str(gk(u'checks')) + u' 次, 错配 ' + str(gk(u'anchor_err')) + u'）: 四色锚位 '
           + u' ⇎ '.join(x + u' ⟦' + y + u'⟧' for x, y in zip(LBL, u'ABCD'))
           + u'; 答句四种（任意定且许可违背 ⇎ 定死但自带出口 ⇎ 取消等待换起算点 ⇎ 收下并废止前三份）: '
           + u' ⇎ '.join(ANS) + u'; 三面阶梯（原面 ⇎ 全篇折平 ⇎ 摘壳折平）按文档读到 '
           + u'⇎'.join(str(x) for x in STRICT) + u' ／ ' + u'⇎'.join(str(x) for x in FOLDD) + u' ／ '
           + u'⇎'.join(str(x) for x in SHD) + u'（针表 ' + str(gk(u'needle_n')) + u' 枚, 折平才现 '
           + str(gk(u'fold_only_n')) + u' 枚 ' + u','.join(FONLY) + u', 按份新增 ⇎'.join(str(x) for x in FOWN)
           + u'——本条第三档空转：' + SHW[3] + u' 零换页符⇒摘壳=全篇折平, 阶梯只走到两阶, 单调 '
           + str(gk(u'ladder_monotone')) + u'）; 锚池 ' + fmt(gk(u'pool_n')) + u' 条分档 '
           + u'⇎'.join(fmt(x) for x in gk(u'pool_tier')) + u'（闭合 ' + str(gk(u'pool_tier_close'))
           + u'）, 四份同现长行 ' + str(gk(u'pool_4')) + u' 条 ⇒ 写法轴档四只开一 ' + gk(u'axis_str')
           + u'（轴账闭合 ' + str(gk(u'axis_close')) + u'）——本条的分裂不住在写法上而住在“要不要等”上; '
           u'大写义务词换代（793 零枚 ⇎ 1122/9293 百枚级）: MUST 全计 ' + L4(gk(u'up_must_all'))
           + u' ⇎ 裸 MUST ' + L4(gk(u'must_bare')) + u' ⇎ MUST NOT ' + L4(gk(u'must_not'))
           + u'（账平 ' + L4(gk(u'up_ledger')) + u'）; 2MSL 四式并计 连字 ' + L4(gk(u'f2msl')) + u' ⇎ 2x '
           + L4(gk(u'f2x')) + u' ⇎ 2* ' + L4(gk(u'f2star')) + u' ⇎ 带空格 ' + L4(gk(u'f2xsp')) + u'（合计 '
           + L4(gk(u'form_all')) + u'）; 引用两式: RFC-793 ' + L4(gk(u'r793d')) + u' ⇎ RFC 793 '
           + L4(gk(u'r793s')) + u' ⇎ RFC 1122 ' + L4(gk(u'r1122s')) + u'（短横式 RFC-1122 '
           + L4(gk(u'r1122d')) + u' 一枚不现）; 同数共键 ' + str(len(DER)) + u' 枚算式／'
           + str(gk(u'x_ident_n')) + u' 条面内恒等式（标量闭账 ' + str(gk(u'scalar_clos_n')) + u' 项, 归零 '
           + str(gk(u'scalar_clos_sum')) + u' ⇎ 含 close 的键 ' + str(CLOSEK) + u' 枚其中逐份清单 '
           + str(gk(u'list_clos_n')) + u' 枚）, 扁平契约 ' + str(len(FP))
           + u' 枚键全数复测; 五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对锚逐字复核'
           u'；工具侧 atomcheck 的 SRC 表未登记本条, 四份纯文本面的逐字性由门槛侧 ' + str(gk(u'checks'))
           + u' 次归属检查承担（逐字命中 ' + str(gk(u'anchor_total')) + u' 处 ⇎ 错配 ' + str(gk(u'anchor_err')) + u'） |')

SRCLINE = SHW
C69 = (u'| B69 | ' + u' ⇎ '.join(
    SRCLINE[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／面内码位 ' + fmt(gk(u'chars')[i])
    + u'／行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i]) + u'（换页符 ' + str(FFC[i]) + u' 枚，独占整行 ' + str(FF[i])
    + u' 行）／最长行 ' + str(ML[i]) + u' 列／答句 ' + ANS[i] + u'／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i])
    + u'／BOM ' + str(BOM[i]) + u'）' for i in range(4))
           + u' | 四份答同一个问题 ⇒ 793 把 MSL 任意定成 2 分钟、同段承认“这是工程选择”并把违背 quiet time 写成明文许可'
             u'（全篇大写 MUST ' + str(gk(u'up_must_all')[0]) + u' 枚），1122 换成 MUST linger 两枚 MSL 却把 MAY accept a new SYN'
             u' 写进同一句（两条件各再现 ' + str(gk(u'n_b_cond1')[3]) + u'⇎' + str(gk(u'n_b_cond2')[3]) + u' 次于 9293 面） ⇎ '
             u'6528 取消“等”这个动作、改按“自上一段报文最后被见到起是否已过 2*MSL”，且全篇不写 MSL 等于几分钟（“2 minutes” '
             + str(gk(u'c2m')[2]) + u' 处） ⇎ 9293 同时收下三家：793 那句 2 分钟在它面上逐字再现（同形闭合 '
             + str(gk(u'msl2_same_bytes')) + u'）、1122 的 linger 句两条件各再现，而 793 的 keep-quiet 整句被改写主语'
             u'（判定 ' + str(gk(u'quiet_rewritten')) + u'）、一页 Obsoletes 掉 ' + str(gk(u'obsoletes')[3]) + u' 枚含 6528 的清单; '
             u'三面阶梯在本条只走到两阶——第三档对 9293 是空操作（零换页符），真正的通道是折行（'
             + str(gk(u'fold_only_n')) + u' 枚整句被行界劈开） |' + NL)

PARA = (u'**B69 问的是主动关掉一条 TCP 连接之后到底要等多久、这段等待能不能跳过，四份一手文书给出四种答法**：'
        + u' ⇎ '.join(SRCLINE[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
                      + u'／非空行 ' + fmt(NB[i]) + u'／换页符 ' + str(FFC[i]) + u' 枚（独占整行 ' + str(FF[i])
                      + u' 行）／答句 ' + ANS[i] + u'／非 ASCII ' + str(NA[i]) + u'／BOM ' + str(BOM[i]) + u'）'
                      for i in range(4))
        + u'——四份同为 RFC Editor 的纯文本面, 全 LF、行长一律 ' + str(ML[0]) + u' 列封顶, 只有 9293 带一枚 BOM 与两枚取变音符'
          u'（字节−码位差 ' + L4(DELTA) + u' 恰等于每枚非 ASCII 的加字节 ' + L4(EXTRA)
          + u'）, 名分头按份计 Obsoletes ' + L4(gk(u'obsoletes')) + u' ⇎ Updates ' + L4(gk(u'updates')) + u' ⇎ STD '
          + L4(gk(u'std')) + u'。793 任意把 MSL 定成 2 分钟（“taken to be”句式 ' + L4(gk(u'msl_taken'))
          + u' 枚, 9293 逐字收下同一句）并在同段写明“这是工程选择、可改”且许可违背 quiet time, 全篇大写 MUST '
          + str(gk(u'up_must_all')[0]) + u' 枚 ⇎ 1122 把同一件事写成 MUST linger 两枚 MSL（linger ' + L4(gk(u'linger'))
          + u'），式样 ' + L4(gk(u'f2x')) + u' 枚 2xMSL, 却在同一句自带 MAY accept a new SYN 的出口与两条条件（'
          + str(gk(u'n_b_cond1')[1]) + u'⇎' + str(gk(u'n_b_cond2')[1]) + u' 枚），还嫌端口 tied up 而允许缩短 '
          + str(gk(u'n_b_shorten')[1]) + u' 枚 ⇎ 6528 干脆取消等待：判据换成“自上一段报文最后被见到起是否已过 2*MSL”（'
          + str(gk(u'f2star')[2]) + u' 枚星号式），全篇不给 MSL 的分钟数（“2 minutes” ' + str(gk(u'c2m')[2])
          + u' 处 ⇎ taken-to-be ' + str(gk(u'msl_taken')[2]) + u' 枚），把 ISS 生成换成慢时钟＋伪随机（ISN '
          + L4(gk(u'isn')) + u' 枚而 MSL 只 ' + str(gk(u'msl')[2]) + u' 枚） ⇎ 9293 同时收下三家又改写主语：keep-quiet 义务主体从 TCP 变成 '
          u'TCP endpoint（' + str(gk(u'n_d_endpoint')[3]) + u' 枚, reboot 句 ' + str(gk(u'reboot')[3])
          + u' 枚），linger 句与两条件逐字再现，而 793 那句 keep quiet 在它面上按原行零命中（改写判定 '
          + str(gk(u'quiet_rewritten')) + u'）, 并一页 Obsoletes 含 6528 的清单。时长面可以逐字量出来：句内游标读出的 MSL 分钟数两份一致（'
          + L4(gk(u'msl_minutes')) + u', 闭合 ' + str(gk(u'minutes_agree')) + u'），绕回小时 ' + L4(gk(u'cycle_h'))
          + u' 只活在 793⇎9293（' + str(gk(u'cycle_docs')) + u' 份）且推理是单向的“MSL 必须短于它”，时钟步长 '
          + L4(gk(u'usec')) + u' 微秒两份相等（闭合 ' + str(gk(u'usec_agree')) + u'）；全库时长串命中 '
          + L4(gk(u'dur_hit_total')) + u' 处／不同值 ' + L4(gk(u'dur_distinct')) + u' 个, 并集 ' + str(gk(u'dur_union'))
          + u' 个值(值⇎单位成对 ' + str(len(gk(u'dur_pairs'))) + u' 对)。谁抄谁同样可量：归一长行两两交集 '
        + L4(gk(u'pair_share')) + u' ⇎ 逐字节同形 ' + L4(gk(u'pair_byte')) + u' ⇎ 仅归一 '
        + L4(gk(u'pair_norm_only')) + u'（非零对 ' + str(gk(u'pair_nonzero')) + u', 配对闭合 '
        + str(gk(u'pair_close')) + u'）——最大一对 793⇎9293 归一 ' + fmt(gk(u'pair_ad_share')) + u' 行（其中逐字节 '
        + str(gk(u'pair_ad_byte')) + u' ⇎ 仅归一 ' + fmt(gk(u'pair_ad_norm_only')) + u'），6528⇎9293 归一 '
        + str(gk(u'pair_share')[5]) + u' 行而逐字节 ' + str(gk(u'pair_byte')[5]) + u' 行，1122⇎9293 归一 '
        + str(gk(u'pair_share')[4]) + u' 行而逐字节 ' + str(gk(u'pair_byte')[4]) + u' 行——算法收下、句子重写；四份同现的长行 ' + str(gk(u'pool_4'))
        + u' 条 ⇒ 写法分家四档只开一档（' + gk(u'axis_str') + u'，开的这一档正是三源共现的那枚长行, 归一同形而逐字节不同共 ' + str(gk(u'shared_norm_only')) + u' 条, 轴账闭合 ' + str(gk(u'axis_close'))
        + u'）, 本条的分裂不住在写法上而住在“要不要等”上。三面阶梯在本条只走到两阶：在册 '
        + str(gk(u'needle_n')) + u' 枚答句针按原面读到 ' + u'⇎'.join(str(x) for x in STRICT) + u'、全篇折平 '
        + u'⇎'.join(str(x) for x in FOLDD) + u'、摘壳折平 ' + u'⇎'.join(str(x) for x in SHD)
        + u'——9293 零换页符（' + str(FFC[3]) + u' 枚）使剥壳对它是空操作，所以第三档一粒新增都没有（差 '
        + L4(gk(u'sh_minus_fold')) + u'）；真正的必需通道是折行：' + str(gk(u'fold_only_n')) + u' 枚整句被行界劈开（'
        + u' ⇎ '.join(u'⟦' + LBL[OWNER[k]] + u'⟧' + k for k in FONLY) + u'）, 按份新增 '
        + u'⇎'.join(str(x) for x in FOWN) + u', 阶梯单调 ' + str(gk(u'ladder_monotone')) + u'。最锋利的一处：1122 把“MUST 等两枚 MSL”'
        u'与“MAY 立刻接受新 SYN”写进同一句而中间隔着行界——只按行搜 MUST linger 就读不到它自带的出口。引用必须两式并计：'
        u'RFC-793 短横式独占 1122（' + str(gk(u'r793d')[1]) + u' 枚 ⇎ 空格式 ' + str(gk(u'r793s')[1]) + u' 枚），'
        + u'RFC 793 空格式独占 6528⇎9293（' + str(gk(u'r793s')[2]) + u'⇎' + str(gk(u'r793s')[3]) + u' 枚），'
        u'而 RFC-1122 一枚不现（' + L4(gk(u'r1122d')) + u'）——只认短横式就会把 9293 引 793 的 '
        + str(gk(u'r793s')[3]) + u' 次全读漏。答句邻域按 ±' + str(gk(u'win_band')) + u' 行带切, 三轨（MSL ⇎ TIME-WAIT ⇎ 数字符）'
        u'带内外分账闭合 ' + str(gk(u'win_close_sum')) + u'。门槛侧 ' + str(len(DER)) + u' 枚算式／' + str(gk(u'x_ident_n'))
        + u' 条面内恒等式（标量 ' + str(gk(u'scalar_clos_n')) + u' 项全零）, 扁平契约 ' + str(len(FP))
        + u' 枚键由第四 ⇎ 第五套实现逐枚复测; 其中 ' + str(DKEYS) + u' 枚进得了 DERIV 算式（'
        + str(len(DER)) + u' 枚算式按登记字面现跑逐一对账 ⇎ ' + str(gk(u'x_ident_n'))
        + u' 条面内恒等式现算归零）⇎ 余下 ' + str(len(FP) - DKEYS)
        + u' 枚是形状清单、字符串表与窗口切片, 不进任何算式、只由两套实现按键逐枚对账; '
        + str(len(ASTR)) + u' 枚不同锚串按折叠面重分类 单源 ' + str(ASIN) + u' ⇎ 穿二源 ' + str(ACRO2)
        + u' ⇎ 穿三源 ' + str(ATRI) + u' ⇎ 四源 ' + str(AALL4) + u', 与门槛登记口径一致。')

L = S.split(NL)
assert L and S.count(u'**B69 问的是') == 0
assert S.count(u'| B69 |') == 0


def sub(old, new, s, cnt=1):
    assert s.count(old) == cnt, (u'锚点不唯一', old[:60], s.count(old))
    return s.replace(old, new)


def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:60])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


# ---- 1) 判词段(紧跟 B68 段) 2) 门槛表行 3) 语料表行 ----
S = after(S, u'**B68 问的是一条资源记录的 TTL 上限', PARA + NL + NL)
S = after(S, u'| B68 | 12 675（新建,', HEADROW + NL)
S = after(S, u'| B68 | `raw/dnsTTL/rfc1034.txt`', C69)

# ---- 4) 转化指标表: 按 audit 当下输出补 B69 机械行, 并把合计行的唯一码点改为 ALL 行现算值 ----
ROWS = {}
ALLR = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        c = [x.strip() for x in l.split(u'|')[1:-1]]
        ROWS[c[0]] = c
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR and len(ROWS) == 68, (len(ROWS), bool(ALLR))
L = S.split(NL)
h = [i for i, l in enumerate(L) if l.startswith(u'| entry | 编码字符 |')]
assert len(h) == 1, h
tot = [i for i in range(h[0], len(L)) if L[i].startswith(u'| **合计（')]
assert len(tot) == 1, tot
T = tot[0]
present = [l.split(u'|')[1].strip() for l in L[h[0] + 2:T]]
assert all(p.startswith(u'B') for p in present), present[:3]
missing = [k for k in sorted(ROWS, key=lambda k: int(k[1:])) if k not in present]
assert missing == [u'B69'], missing
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
            + u'，本遍补记的一枚为 ' + fmt(E69) + u' 编码／' + fmt(DIG69)
            + u' 摘要；条目数与两列合计均取自本遍现跑的 audit，唯一码点那格取本遍 ALL 行现算值） ')
cells[5] = u' **%s** ' % fmt(UNIQ_ALL)
assert len(cells) == len(OLD.split(u'|')), (len(cells), len(OLD.split(u'|')))
L[T + 1] = u'|'.join(cells)
NOTE = [i for i, l in enumerate(L) if l.startswith(u'（B54 起的 ') and u'机械行' in l]
assert len(NOTE) == 1, NOTE
L[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与'
              u'字符/语义单元五格, 不重写各条的口径注; 本遍再直补 B69 一枚, 合计行的唯一码点即 ALL 行那个全库并集值。）'
              % len([x for x in present + missing if int(x[1:]) >= 54]))
S = NL.join(L)

# ---- 5) 条数与推导数 ----
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])
S = sub(u'共 **67 条**（`babeltele/B01..B65、B67..B68`, 本遍补上 B68 的三处记账行, 合计按 audit 当下输出重算）',
        u'共 **68 条**（`babeltele/B01..B65、B67..B69`, 本遍补上 B69 的四处记账行, 合计按 audit 当下输出重算）', S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（67 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（68 条）', S)
PV = [l for l in S.split(NL) if u'条语料／' in l and u'推导全部通过' in l]
assert len(PV) == 1, PV
i0 = PV[0].find(u'当前 **')
j = PV[0].find(u'）', PV[0].find(u'audit 自报', i0))
while PV[0][j + 1:j + 2] == u'）':
    j += 1
S = S[:S.find(PV[0]) + i0] + (u'当前 **68 条语料／' + str(PROOFS) + u' 条**推导全部通过（audit 自报“已机检的推导 '
                              + str(PROOFS) + u' 条”）') + S[S.find(PV[0]) + j + 1:]

CMD = u'python -X utf8 corpus/_fill68.py'
assert S.count(CMD) == 1
S = after(S, u'python -X utf8 corpus/_fill68.py',
          u'python -X utf8 corpus/_mkB69.py                    # 建条目: 扁平契约 ' + str(len(FP))
          + u' 枚键／恒等式 ' + str(gk(u'x_ident_n')) + u' 条 ⇎ DERIV ' + str(len(DER))
          + u' 枚算式, 句内游标 ⇎ 集合代数 ⇎ 分档并集三种机制, 采集侧对账 0 不符' + NL)
S = after(S, u'python -X utf8 corpus/_mkB69.py',
          u'python -X utf8 corpus/_mkdigest3.py B69 <entry> 793 corpus/raw/tcpTW/rfc793.txt 160 120 1122 … 160 120 '
          u'6528 … 160 120 9293 … 160 120   # 四源分节摘要(' + fmt(DIG69) + u' 字符, '
          + str(gk(u'anchor_total')) + u'/' + str(gk(u'anchor_total')) + u' 锚全命中)' + NL)
S = after(S, u'python -X utf8 corpus/_mkdigest3.py B69',
          u'python -X utf8 corpus/_wire69.py                    # 幂等接线: SRC/ATOM/SCAN(审计器侧第三套实现)/DERIV/'
          u'B69V 进 audit.py, 落盘前复跑 ' + str(len(FP)) + u' 枚扁平键 ⇎ ' + str(len(DER)) + u' 枚算式' + NL)
S = after(S, u'python -X utf8 corpus/_wire69.py',
          u'python -X utf8 corpus/_fill69.py                    # 第四遍: 三面阶梯⇎窗口⇎集合代数⇎词轨各重导一次, '
          + str(gk(u'x_ident_n')) + u' 条恒等式现算归零后写回 ⛓解读注（15 行复测表 ⇎ 复算 '
          + str(len(FP) - 1) + u'/' + str(len(FP)) + u' 枚键对账 0 不符 ⇎ 未覆盖 1 枚（生成期自计数））' + NL)

io.open(u'corpus/README.md', 'w', encoding='utf-8', newline=NL).write(S)
json.dump(dict(entries=len(ROWS), enc=enc_all, dig=dig_all, proofs=PROOFS, b69_enc=E69, b69_dig=DIG69,
               bytes=BS, lines=LN, nonblank=NB, formfeed_only=FF, cr=CR, nonascii=NA, bom=BOM,
               maxlen=ML, forms=dict((k, TOK[k]) for k in (u'f2msl', u'f2x', u'f2star', u'f2xsp', u'r793d',
                                                            u'r793s', u'r1122s')),
               strict=STRICT, fold=FOLDD, sh=SHD, fold_only=FONLY, close_keys=CLOSEK, uniq_all=UNIQ_ALL,
               keys=len(FP), deriv=len(DER), ident=gk(u'x_ident_n')),
          io.open(u'corpus/_b69readme.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（68 条）编码 ' + fmt(enc_all) + u' ⇎ 摘要 ' + fmt(dig_all) + u' ⇎ 保留 '
      + u'%.1f%%' % (100.0 * enc_all / dig_all) + u' ｜ 推导 ' + str(PROOFS) + u' 条 ｜ B69 行 ' + fmt(E69)
      + u'／' + fmt(DIG69) + u' ｜ 锚 ' + str(gk(u'anchor_total')) + u' 处⇎错配 ' + str(gk(u'anchor_err'))
      + u' ｜ 三面阶梯 ' + u'⇎'.join(str(x) for x in STRICT) + u'／' + u'⇎'.join(str(x) for x in FOLDD)
      + u'／' + u'⇎'.join(str(x) for x in SHD) + u' ｜ 折行独有 ' + u','.join(FONLY)
      + u' ｜ 逐份字节 ' + u'⇎'.join(fmt(x) for x in BS))
