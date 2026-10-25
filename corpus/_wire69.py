# -*- coding: utf-8 -*-
"""把 B69 的独立复算器(_b69_scan / B69V)接进 audit.py, 并生成 DERIV['B69']。
幂等: 重复运行先摘旧块再插新块; 只动 B69 自己的区域, 并行 agent 的 B65/B67/B68 行段原样保留。
_b69_scan 的量测段从 corpus/_mkB69.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间 ⇎
corpus/_mk69emit.py 的 SCAN2 BEGIN ⇎ SCAN2 END 之间逐行机械抽出, 只在头部换成 audit 自己的
路径常量与模块别名; 真正的独立性来自六处:
①采集侧 corpus/_pick69.py 是先于建条目写好的另一套实现(str.count/逐行 in 收针), 建条目侧改立
  游标逐字符档、正则档、集合代数档与 itertools 配对档, 两边在口径一致的键上逐量对账;
②抽出的代码在插门之前要把 _b69flat.json 的每个键与 DERIV['B69'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按归一串判成员;
④数字读数一律从面内现读: 793/9293 的 MSL 分钟数、术语表里那枚任意值、绕回小时 4.55、时钟步长微秒
  都由正向或逆向游标从句子内部解析; 带的起行⇎止行⇎答句行由答句在原文件行里的位置现定位;
⑤三面口径是本条的支柱: 在册 28 枚答句针在"原面逐行⇎全篇折平⇎摘壳再折平"三档各立一键,
  三枚针只在折平面存在(整句被行界劈开), 而 9293 零换页符使第三档对它空转——这类差只能由复算给出;
⑥搬运⇎重写是可算的量: 归一长行的两两交=逐字节交+仅归一, 793⇎9293 那一档再拆成"只此两份 ⇎ 三份同压",
  四份同现零枚⇒写法轴四桶空转, 义务语气两轨(子串档⇎正则档)必须互相咬合。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB69.py', encoding='utf-8').read()
EM = io.open(u'corpus/_mk69emit.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/tcpTW/rfc793.txt', u'corpus/raw/tcpRTO/rfc1122.txt',
        u'corpus/raw/tcpTW/rfc6528.txt', u'corpus/raw/tcpTW/rfc9293.txt']


def cut(src, a, b):
    i = src.index(a)
    j = src.index(b, i)
    return src[i:j]


MEAS = cut(MK, u'# --- SCAN BEGIN ---', u'# --- SCAN END ---')
MEAS = MEAS[MEAS.index(NL) + 1:]
MEAS2 = cut(EM, u'# --- SCAN2 BEGIN ---', u'# --- SCAN2 END ---')
MEAS2 = MEAS2[MEAS2.index(NL) + 1:]
MEAS = MEAS.rstrip() + NL + NL + MEAS2.rstrip() + NL
assert u'PN' not in u'' and u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
for nm in (u'pnorm', u'cnt_cur', u'read_after', u'sec_window', u'HEADND', u'POOLC', u'ZID',
           u'CLOSE', u'FOLD', u'NEEDLE', u'GN', u'GR', u'CNT', u'SN', u'SNF', u'SNS', u'NUM',
           u'win_close_sum', u'up_ledger', u'nonascii_extra', u'pair_ad_excl', u'apool_tag_n',
           u'n_', u'num_'):
    assert nm in MEAS, nm

HEAD = u'''
# B69: 主动关掉一条 TCP 连接之后到底要等多久、这段等待能不能跳过——四份一手 TCP 文书四种答法:
# raw/tcpTW/rfc793.txt(A 793/1981: 把 MSL 任意定成 "For this specification the MSL is taken to be 2 minutes",
#   术语表另处再写一遍 "Arbitrarily defined to be 2 minutes", 状态图里那枚超时器写 Timeout=2MSL,
#   同一句还明文许可实现者违背自己刚立的 quiet time("TCP implementors may violate the quiet time restriction");
#   全篇大写 MUST 零枚——它那份文书早于 RFC 2119 的语气表)
# ⇎ raw/tcpRTO/rfc1122.txt(B 1122/1989: 换成命令式 "it MUST linger in the TIME-WAIT state for a time 2xMSL",
#   却把出口写进同一句(MAY accept a new SYN, 两个条件各一行), 又嫌端口 tied up 而允许某些 TCP 缩短等待)
# ⇎ raw/tcpTW/rfc6528.txt(C 6528/2012: 取消"等"这个动作, 判据改成 "before 2*MSL have passed since a segment
#   ... was last seen"; 通篇不写 MSL 等于几分钟, 同时把 ISS 生成换成慢时钟加伪随机)
# ⇎ raw/tcpTW/rfc9293.txt(D 9293/2022: 逐字收下 793 那句 2 分钟(两份该句逐字节同形), 收下 1122 的 linger
#   与两条件(内容搬走而句子重写), 把 keep-quiet 的义务主语换成 TCP endpoint, 一页 Obsoletes 掉含 6528 的七份)。
# 本函数从四份字节独立复算: 句内游标五枚数(正读 ⇎ 逆读到带小数的全数), 三面口径的在册答句针档
# (原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平)与严格/折平/摘壳三档单调账, 2MSL 四式(连字⇎2x⇎2*⇎带空格)与同面并存,
# 义务语气两轨(子串档 ⇎ 正则档)互咬, 大写/裸/MUST NOT 三本账, 引用写法短横族⇎空格式两族分计,
# 整行搬运的归一⇎逐字节两把尺⇎四源长行容斥⇎三三交分档, 答句邻域带(±40 行)的带内外三轨余量对账,
# 编码层(BOM ⇎ 非 ASCII 码位 ⇎ 每枚带来的加字节 ⇎ 字节−码位差), 锚候选池按标签⇎按份数两本账。
# 恒等式(分钟数两份一致 ⇎ 绕回小时同现份数 ⇎ 图式 Timeout=2MSL 只此两式 ⇎ 裸 MUST+MUST NOT=大写 MUST ⇎
# 归一交=逐字节交+仅归一 ⇎ AD 那档再拆只此两份/三份同压 ⇎ 带内+带外=全篇 MSL/TIME-WAIT/数字符 ⇎
# Σ单份−Σ两两+Σ三三−Σ四份=并集 ⇎ 分档之和=池条数)全归零送门槛重算。
# 不可由在库文件判定的: 四份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 此后哪份文档又动了这段、现网内核实际把 TIME-WAIT 设成多久——只进解读注, 不进门槛。
def _b69_scan():
    import io, re, itertools, hashlib as _hl
    from collections import Counter, defaultdict
    P2 = SRC['B69']
    NSRC = 4
    LBL = [u'793', u'1122', u'6528', u'9293']
    TAGS = LBL
    YR = [u'81', u'89', u'12', u'22']
    PATH = P2
    NL = chr(10)
    F = {}
    DER = {}
    LITK = {}
    IDX = dict((t, n) for n, t in enumerate(LBL))

    def _dv(x):
        if isinstance(x, tuple):
            return [_dv(y) for y in x]
        if isinstance(x, list):
            return [_dv(y) for y in x]
        if isinstance(x, dict):
            return dict((k, _dv(v)) for k, v in x.items())
        return x
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
BODYTXT = re.sub(u'(?<![.\\w])hashlib\\.', u'_hl.', BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
BODYTXT = BODYTXT.replace(u'print(', u'_sil(')
assert u'_sil(' in BODYTXT
EVSRC = u"eval(e.strip().replace(u'\\n', u''))"
assert BODYTXT.count(EVSRC) == 2, BODYTXT.count(EVSRC)
BODYTXT = BODYTXT.replace(EVSRC, u"eval(e.strip().replace(u'\\n', u''), "
                                u"dict(globals(), F=F, CLOSE=CLOSE, NSRC=NSRC, "
                                u"len=len, sum=sum, max=max, min=min, abs=abs, range=range, re=re))")

ANCHORK = {u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single',
           u'anchor_cross', u'anchor_all4', u'checks',
           u'tag_793', u'tag_1122', u'tag_6528', u'tag_9293'}
FLAT = json.load(io.open(u'corpus/_b69flat.json', encoding='utf-8'))
FAM = sorted({k.split(u'_')[0] for k in FLAT})


def fam(k):
    h = k.split(u'_')[0]
    return FAM.index(h) if h in FAM else len(FAM)


def lit(v):
    return repr(v).replace(u'u+', u'')


def gen_asserts(keys=None):
    ks = sorted([k for k in (keys if keys is not None else FLAT)
                 if k not in ANCHORK], key=lambda k: (fam(k), k))
    lines, buf = [], []
    for k in ks:
        piece = u"_dv(F[u'%s']) == %s" % (k, lit(FLAT[k]))
        if buf and sum(len(x) + 5 for x in buf) + len(piece) > 100:
            lines.append(u'    assert ' + u' and '.join(buf))
            buf = []
        buf.append(piece)
    if buf:
        lines.append(u'    assert ' + u' and '.join(buf))
    return NL.join(lines) + NL


HAND = u'''    # ---- 结构性自检: 游标五枚数、四式并计、三面单调、义务两轨、搬运容斥、带内外三轨 ----
    assert F[u'num_minutes_a'] == F[u'num_minutes_d'] == F[u'num_minutes_arb'] == 2
    assert F[u'num_hours_a'] == 4 and F[u'cycle_h'] == [4.55, None, None, 4.55]
    assert F[u'num_usec_a'] == F[u'num_usec_d'] == 4 and F[u'num_twoms_a'] == 2
    assert F[u'msl_taken'] == [1, 0, 0, 1] and F[u'c2m'] == [2, 1, 0, 1]
    assert F[u'msl2_same_bytes'] == 1 and F[u'arb_eq_spec'] == 0
    assert F[u'f2msl'] == [1, 0, 0, 2] and F[u'f2x'] == [0, 3, 0, 1]
    assert F[u'f2star'] == [0, 1, 1, 0] and F[u'form_distinct'] == [1, 2, 1, 2]
    assert F[u'sn_strict_docs'] == [8, 7, 4, 6] and F[u'sn_fold_docs'] == [9, 8, 4, 7]
    assert F[u'sn_sh_docs'] == [9, 8, 4, 7] and F[u'ladder_monotone'] == 1
    assert F[u'fold_only_keys'] == [u'a_eng_whole', u'b_two_both', u'd_quiet_whole']
    assert F[u'fold_line_zero'] == 0 and F[u'sh_minus_fold'] == [0, 0, 0, 0]
    assert F[u'must_bare'] == [0, 180, 2, 221] and F[u'up_must_all'] == [0, 200, 4, 228]
    assert F[u'up_ledger'] == [0, 0, 0, 0] and F[u'quiet_rewritten'] == 1
    assert F[u'r793d'] == [0, 34, 0, 0] and F[u'r793s'] == [0, 0, 5, 60]
    assert F[u'pair_share'] == [1, 0, 351, 0, 16, 16] and F[u'pair_byte'] == [0, 0, 29, 0, 0, 15]
    assert F[u'pair_close'] == 0 and F[u'pair_nonzero'] == 4
    assert F[u'pair_ad_share'] == 351 and F[u'pair_ad_excl'] == 350 and F[u'pair_ad_in3'] == 1
    assert F[u'pair_ad_split'] == F[u'pair_ad_pair_close'] == F[u'pair_ad_close'] == 0
    assert F[u'pool_n'] == 9149 and F[u'pool_tier'] == [8767, 381, 1, 0] and F[u'pool_4'] == 0
    assert F[u'pool_3'] == 1 and F[u's3_docs'] == 3 and F[u'axis_close'] == 0
    assert F[u'tri_share'] == [0, 1, 0, 0] and F[u'union_close'] == 0
    assert F[u'win_band'] == 40 and F[u'win_named'] == 4
    assert F[u'win_start'] == [1812, 5119, 91, 1067] and F[u'win_end'] == [1892, 5199, 171, 1147]
    assert F[u'win_center'] == [1852, 5159, 131, 1107] and F[u'win_rows'] == [81, 81, 81, 81]
    assert F[u'win_close_sum'] == 0 and F[u'win_close_msl'] == [0, 0, 0, 0]
    assert F[u'bytes'] == [172710, 289148, 26917, 263696]
    assert F[u'lines'] == [5248, 6845, 676, 5577] and F[u'nonblank'] == [2975, 4549, 437, 4370]
    assert F[u'bom'] == [0, 0, 0, 1] and F[u'nonascii'] == [0, 0, 0, 3]
    assert F[u'nonascii_extra'] == [0, 0, 0, 4] and F[u'byte_cp_delta'] == [0, 0, 0, 4]
    assert F[u'cr'] == [0, 0, 0, 0] and F[u'ff'] == [91, 116, 12, 0]
    assert F[u'msl'] == [16, 8, 2, 21] and F[u'tw'] == [28, 8, 4, 47]
    assert F[u'isn'] == [12, 1, 38, 20] and F[u'reboot'] == [0, 0, 0, 14]
    assert F[u'apool_n'] == 10737 and F[u'apool_tag_close'] == F[u'apool_tier_close'] == 0
'''

ANCH = u'''
    FAN = FO
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B69_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6(' + u'|'.join(TAGS) + u')\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B69: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B69: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B69: 标签嵌套'
    ERR = [x for x in CITES if not pnorm(x[1]) or pnorm(x[1]) not in FAN[IDX[x[0]]]]
    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [tuple(i for i in range(NSRC) if pnorm(a) and pnorm(a) in FAN[i]) for a in DIS]
    F[u'anchor_total'] = len(CITES)
    F[u'anchor_distinct'] = len(DIS)
    F[u'anchor_err'] = len(ERR)
    F[u'anchor_single'] = len([h for h in HC if len(h) == 1])
    F[u'anchor_cross'] = len([h for h in HC if 1 < len(h) < NSRC])
    F[u'anchor_all4'] = len([h for h in HC if len(h) == NSRC])
    F[u'checks'] = len(DIS) * NSRC
    F[u'nsrc'] = NSRC
    F[u'enc_chars'] = len(enc.replace(NL, u''))
    assert F[u'enc_chars'] == 8042 and F[u'nsrc'] == 4
    for t in TAGS:
        F[u'tag_' + t] = len(re.findall(u'\\u27e6%s\\u27e7' % t, enc))
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all4'] == len(DIS)
    assert all(F[u'tag_' + t] > 0 for t in TAGS), u'有四源标签没锚'
    assert F[u'anchor_all4'] == 0 and F[u'pool_4'] == 0, u'B69: 归一后四份同现的长行为零, 不该有四源锚'
    AX = [a for h, a in zip(HC, DIS) if len(h) > 1]
    assert F[u'anchor_cross'] == len(AX) == 9
    assert all(3 in h for h in HC if len(h) > 1), u'B69: 跨源锚里有一枚不落进 9293 面'
    assert F[u'anchor_single'] == len(DIS) - 9 == 13
    assert F[u'anchor_err'] == 0 and F[u'anchor_distinct'] == 22 and F[u'anchor_total'] == 26
    return F

_B69 = _b69_scan()
B69V = lambda k, i=None: (_B69[k] if i is None else _B69[k][i])
'''

ANCH_A, ANCH_B = ANCH.split(u'    return F')
BLK = (HEAD + u'    def _sil(*a):\n        pass\n' + BODYTXT + HAND + ANCH_A
       + gen_asserts() + u'    return F' + ANCH_B)
compile(BLK, u'<b69 block>', u'exec')

assert S.count(NL + u"_B65 = _b65_scan()") == 1, u'anchor _b65_scan'
i0 = S.find(u'# B69: 主动关掉一条 TCP 连接')
while i0 >= 0:
    i1 = S.index(u'_B65 = _b65_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B69: 主动关掉一条 TCP 连接')
if u'B69V=B69V,' in S:
    S = S.replace(u'B69V=B69V,' + NL, NL)
S = S.replace(NL + u"_B65 = _b65_scan()", BLK + NL + u"_B65 = _b65_scan()")
if u'B69V=B69V' not in S:
    ME = re.search(u'B68V=B68V((?:,\\s*\\w+=\\w+)*)\\)', S)
    assert ME, u'anchor env'
    S = S[:ME.end(1)] + u',\n               B69V=B69V' + S[ME.end(1):]

PS = u"SRC['B65'] = ["
blk = (u"SRC['B69'] = ['corpus/raw/tcpTW/rfc793.txt', 'corpus/raw/tcpRTO/rfc1122.txt', "
       u"'corpus/raw/tcpTW/rfc6528.txt', 'corpus/raw/tcpTW/rfc9293.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
if u"'B69'" not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B69'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B69'" + S[m.end(1):]

M1 = u'# ---- B69 DERIV (generated by corpus/_wire69.py from corpus/_deriv69.json; do not hand-edit) ----'
M2 = u'# ---- /B69 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o4 = u'# ---- B65 DERIV (generated by corpus/_wire65.py'
assert S.count(o4) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv69.json', encoding='utf-8'))
S = S.replace(o4, M1 + NL + u"DERIV['B69'] = " + repr(J) + NL + M2 + NL + o4)

NS = {'SRC': {'B69': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
try:
    exec(compile(BLK, u'<b69 block>', u'exec'), NS)
except AssertionError:
    import traceback
    tb = sys.exc_info()[2]
    while tb.tb_next:
        tb = tb.tb_next
    ls = BLK.split(NL)
    print(u'块内断言失败于第 %d 行:\n%s' % (tb.tb_lineno, ls[tb.tb_lineno - 1]))
    raise
env = NS['B69V']
BAD, MISMATCH = [], []


def deep(x):
    return [deep(y) for y in x] if isinstance(x, list) else list(x) if isinstance(x, tuple) else x


for k, v in FLAT.items():
    if k in (u'nsrc', u'enc_chars'):
        continue
    try:
        got = env(k)
    except Exception as e:
        BAD.append((k, repr(e)))
        continue
    if deep(got) != deep(v):
        MISMATCH.append((k, v, got))
assert not BAD, BAD[:6]
assert not MISMATCH, MISMATCH[:6]
for kk, v in J.items():
    try:
        got = eval(v, dict(NS), {'B69V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b65_scan' in S and u'_b69_scan' in S
compile(S, u'<audit.py wired>', u'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b69_scan+B69V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
