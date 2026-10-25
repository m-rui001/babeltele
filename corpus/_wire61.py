# -*- coding: utf-8 -*-
"""把 B61 的独立复算器(_b61_scan / B61V)接进 audit.py, 并生成 DERIV['B61']。
幂等: 重复运行先摘旧块再插新块。
_b61_scan 的量测段从 corpus/_mkB61.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自四处:
①采集侧 corpus/_pick61.py 是先于建条目写好的另一套实现(它用 (?i)\\b 词界数义务词、str.count 数全大写强度词、
  按 "(\\d+) octets \\((\\d+) minus" 一次抽成对读数、'\\s+' 类判折行单位后缀、行集求交算搬运),
  两边在 95 个口径一致的键上逐量对账(五份都是纯文本面, 无需按介质分流;
  对账行由 _mkB61.py 末尾打印, 现况 95／不符 0);
②抽出的代码在插门之前要把 _b61flat.json 的每个键与 DERIV['B61'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 五源一律按归一串判成员;
④下限句谓词与第一遍不同: 建条目侧先把整篇空白折平再逐字面找(采集侧用 \\s+ 正则类), 后缀符号分类
  用逐字符判邻而非 \\s 类, 附录定位取最后一处命中而非第一处(目录页也印同一枚标题),
  于是原面档⇎折平档之差(wrap_gap_routers⇎wrap_gap_1280_oct⇎wrap_gap_jumbo_opt)与两窗之差
  都是门可复算的量, 不是注释里的解释。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB61.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/ipv6/rfc1883.txt', u'corpus/raw/ipv6/rfc2460.txt',
        u'corpus/raw/ipv6/rfc8200.txt', u'corpus/raw/ipv6/rfc2675.txt',
        u'corpus/raw/ipv6/rfc8201.txt']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u"WCH = u' \\t\\n\\x0b\\x0c\\r'", u'# --- SCAN END ---')
assert u'F[u' in MEAS and u'POOL' in MEAS and u'floor_vals' in MEAS and u'abc_close' in MEAS
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
assert u'FAN' in MEAS and u'ATOMSEL' in MEAS and u'pnorm' in MEAS

HEAD = u'''
# B61: 一条链路至少要能装多少字节、一个 IPv6 包最大能多大——五份规范五种答法:
# raw/ipv6/rfc1883.txt(A 全篇用 576, 九处全在 §5, 净载荷下限 528=576−48, 并把 Jumbo Payload option 写进正文)
# ⇎ rfc2460.txt(B 换成 1280 十处, 净载荷 1232=1280−48; 576 只剩变更记录一枚墓碑“changed the minimum IPv6 MTU from 576 to 1280”,
#   同一窗里另有一句 Removed all references to jumbograms)
# ⇎ rfc8200.txt(C 现行版 1280 八处而 576 整枚字面不存在, 净载荷算式被删, 超大包只字不提)
# ⇎ rfc2675.txt(D 把包顶抬到 4,294,967,295 而通篇不给下限, jumbo 一族 63 处)
# ⇎ rfc8201.txt(E 不答“至少要装多少”: 576⇎1280⇎65,535 各 0 处, 只谈怎么量到路径上最小的一环, MTU 219 处、PMTU 缩写 109 处)。
# 本函数从五份字节独立复算: 下限句谓词(折叠面现读数字)与净载荷括号成对读数,
# 正文⇎变更记录两窗划分(附录标题取最后一处命中)与两窗相加闭合,
# 字面出现处⇎独立数 token⇎后邻符号六档(连字⇎空格⇎折行单位⇎逗号⇎句号⇎其余)相加闭合,
# 原面逐字面⇎整篇空白折平两档之差(分片主语句后半截、1280 octets、选项名),
# 超大包一族(定义⇎自我移除⇎现行只字不提⇎实验档接走), 义务词全大写⇎小写⇎首字母三档(五份全大写皆 0),
# MTU 语汇密度、章节号与体例身份、锚候选池按逐字再现份数五层划分与锚归属由正文现推、三代整行容斥。
# 不可由在库文件判定的: 五份的抓取时刻与磁盘 mtime 谁新谁旧、rfc-editor.org 此刻的现行状态页、
# 勘误表是否已挂新版、A 抬头那个 August 1998 与正文版本谁真——只进解读注, 不进门槛。
def _b61_scan():
    import hashlib as _hl
    import os as _os
    P2 = SRC['B61']
    NSRC = 5
    TAGS = [u'A', u'B', u'C', u'D', u'E']
    LB = dict(zip(TAGS, [u'95 初版', u'98 标准', u'17 现行', u'超大包档', u'PMTUD 档']))
    PATH = P2
    IDX = dict((t, i) for i, t in enumerate(TAGS))
    RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
    ROOT = u''
    C = u'corpus'
    NL = chr(10)
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
for a, b in ((u'os.path.getsize(', u'_os.path.getsize('), (u'hashlib.', u'_hl.')):
    BODYTXT = re.sub(u'(?<![.\\w])' + re.escape(a), b, BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert u'_os.open(' not in BODYTXT, u'裸 open( 被误改写'
assert u'_hl.blake2b' in BODYTXT and u'_os.path.getsize' in BODYTXT

TAIL = u'''
    # ---- 结构性自检: 五答、两窗划分、token 六档闭合、折行双档、义务词三档、搬运容斥 ----
    assert F[u'bytes'] == [82089, 85890, 93162, 17320, 42751] and F[u'sig_distinct'] == 5
    assert len(set(F[u'sig'])) == 5 and F[u'chars'] == F[u'bytes'] and F[u'nonascii'] == [0] * 5
    assert F[u'lines'] == [2076, 2188, 2356, 508, 1068] and F[u'nonblank'] == [1315, 1387, 1488, 303, 682]
    assert F[u'maxlen'] == [73, 72, 72, 72, 72] and F[u'rec_close'] == [0, 0, 0, 0, 0]
    assert F[u'cr'] == [0] * 5 and F[u'figbox'] == [99, 97, 86, 2, 0]
    assert F[u'floor_vals'] == [[u'576'], [u'1280'], [u'1280'], [], []]
    assert F[u'w_floor_sent'] == [1, 1, 1, 0, 0] and F[u's_floor_sent'] == [0, 0, 0, 0, 0]
    assert F[u'wrap_gap_floor_sent'] == [F[u'w_floor_sent'][i] - F[u's_floor_sent'][i] for i in range(5)] \
        == [1, 1, 1, 0, 0]
    assert F[u'pfloor_pair'] == [[[u'528', u'576']], [[u'1232', u'1280']], [], [], []]
    assert F[u'lit_576'] == [9, 1, 0, 0, 0] and F[u'lit_1280'] == [0, 10, 8, 0, 0]
    assert F[u'tok_576'] == F[u'lit_576'] and F[u'subgap_576'] == [0] * 5
    assert F[u'sec5_576'] == [9, 0, 0, 0, 0] and F[u'sec5_1280'] == [0, 9, 6, 0, 0]
    assert F[u'sec5_528'] == [1, 0, 0, 0, 0] and F[u'sec5_1232'] == [0, 1, 0, 0, 0]
    assert F[u'sec5_c65535'] == [0, 0, 0, 10, 0] and F[u'sec5_out_A'] == [0] and F[u'sec5_out_B'] == [0]
    assert F[u'clo_line'] == [0, 1985, 2137, 0, 923] and F[u'clo_found'] == [0, 1, 1, 0, 1]
    assert F[u'body_576'] == [9, 0, 0, 0, 0] and F[u'tail_576'] == [0, 1, 0, 0, 0]
    assert F[u'body_1280'] == [0, 9, 7, 0, 0] and F[u'tail_1280'] == [0, 1, 1, 0, 0]
    assert F[u'close_576'] == [0] * 5 and F[u'close_1280'] == [0] * 5
    assert F[u'body_1232'] == [0, 1, 0, 0, 0] and F[u'tail_1232'] == [0] * 5
    assert F[u'body_c65535'] == [5, 1, 1, 17, 0] and F[u'tail_c65535'] == [0] * 5
    assert F[u'body_c4294967295'] == [0, 0, 0, 1, 0] and F[u'lit_c4294967295'] == [0, 0, 0, 1, 0]
    assert F[u'lit_65535'] == [0] * 5 and F[u'lit_c65535'] == [5, 1, 1, 17, 0]
    assert F[u'tok_c65535'] == [5, 1, 1, 17, 0] and F[u'comma_only'] == [5, 1, 1, 17, 0]
    assert F[u'sk_576_total'] == [9, 1, 0, 0, 0]
    assert F[u'sk_576_hy_octet'][0] + F[u'sk_576_sp_octet'][0] + F[u'sk_576_wrap_octet'][0] \\
        + F[u'sk_576_comma'][0] + F[u'sk_576_dot'][0] + F[u'sk_576_other'][0] == F[u'sk_576_total'][0]
    assert F[u'sk_576_close'] == [0] * 5 and F[u'sk_1280_close'] == [0] * 5
    assert F[u'sk_1280_total'] == [0, 10, 8, 0, 0] and F[u'sk_1280_wrap_octet'] == [0, 2, 2, 0, 0]
    assert F[u'sk_c65535_total'] == [5, 1, 1, 17, 0] and F[u'sk_c65535_close'] == [0] * 5
    assert F[u'sk_c65535_other'][3] == 6 and F[u'skother_c65535'][3][0] == u' + 40, w'
    assert F[u'skother_576'] == [[u' minus 4'], [u' to 1280'], [], [], []]
    assert F[u'jumbo_ci'] == [15, 4, 0, 63, 0] and F[u'jumbo_caps'] == [15, 2, 0, 49, 0]
    assert F[u'jumbo_option_def'] == [10, 0, 0, 26, 0] and F[u'remove_note'] == [0, 1, 0, 0, 0]
    assert F[u'body_Jumbo'] == [15, 0, 0, 49, 0] and F[u'tail_Jumbo'] == [0, 2, 0, 0, 0]
    assert F[u'close_Jumbo'] == [0] * 5 and F[u'body_jumbo'] == [0, 0, 0, 14, 0]
    assert F[u's_routers'] == [0] * 5 and F[u'w_routers'] == [1, 1, 1, 0, 0]
    assert F[u'wrap_gap_routers'] == [1, 1, 1, 0, 0]
    assert F[u's_1280_oct'] == [0, 3, 3, 0, 0] and F[u'w_1280_oct'] == [0, 6, 5, 0, 0]
    assert F[u'wrap_gap_1280_oct'] == [0, 3, 2, 0, 0]
    assert F[u'w_jumbo_opt'] == [10, 1, 0, 27, 0] and F[u'wrap_gap_jumbo_opt'] == [0, 1, 0, 1, 0]
    assert F[u's_frag_src'] == [1, 1, 1, 0, 0] and F[u'w_frag_src'] == [1, 1, 1, 0, 0]
    assert F[u'wrap_gap_frag_src'] == [0] * 5 and F[u'frag_src_share'] == 0
    assert F[u'frag_ci'] == [139, 137, 209, 3, 18] and F[u'frag_word'] == [91, 87, 140, 3, 2]
    assert F[u'frag_head'] == [21, 18, 33, 3, 1] and F[u'frag_and_reas'] == [1, 1, 1, 0, 2]
    assert F[u'u_must'] == [0] * 5 and F[u'u_should'] == [0] * 5 and F[u'u_may'] == [0] * 5
    assert F[u'u_must_not'] == [0] * 5 and F[u'oblig_up'] == [0] * 5
    assert F[u'l_must'] == [62, 56, 52, 8, 28] and F[u'l_should'] == [16, 14, 27, 1, 25]
    assert F[u'l_may'] == [28, 26, 32, 7, 33] and F[u'oblig_low'] == [106, 96, 111, 16, 86]
    assert F[u'c_must'] == [0, 0, 0, 1, 0] and F[u'c_may'] == [0, 0, 2, 1, 1]
    assert F[u'rfc2119_ref'] == [0, 0, 0, 0, 7] and F[u'rfc8174_ref'] == [0] * 5
    assert F[u'lowercase_selfdoc'] == [0, 0, 0, 0, 1] and F[u'no_cite_2119'] == [0, 0, 0, 0, 2]
    assert F[u'mtu_any'] == [24, 27, 27, 11, 219] and F[u'pmtu'] == [0, 0, 0, 0, 109]
    assert F[u'path_mtu'] == [9, 10, 6, 2, 65] and F[u'link_mtu'] == [3, 3, 5, 2, 16]
    assert F[u'ptb'] == [1, 3, 3, 0, 28] and F[u'mtu_wrap'] == [0, 1, 3, 0, 0]
    assert F[u'lit_1500'] == [3, 6, 4, 0, 1] and F[u'lit_9000'] == [0] * 5 and F[u'lit_2048'] == [0] * 5
    assert F[u'at_least'] == [2, 1, 1, 0, 0] and F[u'minmtu_sent'] == [1, 1, 1, 0, 0]
    assert F[u'obsoletes_hdr'] == [0, 1, 1, 1, 1] and F[u'updates_hdr'] == [0] * 5
    assert F[u'category_std'] == [1] * 5 and F[u'category_exp'] == [0] * 5
    assert F[u'obsoleted_by'] == [0, 0, 0, 0, 1] and F[u'errata'] == [0, 0, 6, 0, 1]
    assert F[u'change_log_head'] == [0, 24, 0, 0, 0] and F[u'stds_stmt'] == [38, 40, 44, 10, 21]
    assert F[u'sec_head'] == [20, 21, 26, 15, 17] and F[u'sec_head_d'] == [18, 21, 26, 15, 17]
    assert F[u'section_cite'] == [10, 29, 33, 4, 21] and F[u'rfc_ref_n'] == [8, 9, 29, 7, 18]
    assert F[u'num-lines'] == [22, 14, 7, 53, 0] and F[u'dashes'] == [3356, 3433, 3224, 128, 70]
    assert F[u'share_AB'] == 576 and F[u'share_BC'] == 424 and F[u'share_AC'] == 357
    assert F[u'AB_C_inter'] == 343 and F[u'union_ABC'] == 1737
    assert F[u'only_A'] == 262 and F[u'only_B'] == 230 and F[u'only_C'] == 574
    assert F[u'abc_close'] == F[u'union_ABC'] - (F[u'only_A'] + F[u'only_B'] + F[u'only_C']
                                                 + F[u'share_AB'] + F[u'share_AC'] + F[u'share_BC']
                                                 - 2 * F[u'AB_C_inter']) == 0
    assert F[u'share_AD'] == 6 and F[u'share_BD'] == 25 and F[u'share_CD'] == 0
    assert F[u'share_CE'] == 36 and F[u'share_DE'] == 0 and F[u'lines_ge40'] == [852, 887, 1012, 197, 549]
    assert F[u'pool_n'] == 4169 and F[u'pool_tiers'] == [1652, 719, 1620, 121, 57]
    assert F[u'pool_close'] == 0 and sum(F[u'pool_tiers']) == F[u'pool_n']
    assert F[u'pool_tag_n'] == [1010, 1072, 1200, 256, 631] and sum(F[u'pool_tag_n']) == F[u'pool_n']
    assert F[u'pool_maxlen'] == 73 and F[u'scalar_clos_n'] == 2 and F[u'list_clos_n'] == 6
    assert F[u'scalar_clos_sum'] == 0 and F[u'scalar_clos_list'] == [u'abc_close', u'pool_close']

    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 五源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B61_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B61: 正文里没有带标签的锚'
    assert len(re.findall(u'⟨', enc)) == len(CITES), u'B61: 有锚没带源标签'
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
    F[u'anchor_all5'] = len([h for h in HC if len(h) == NSRC])
    F[u'checks'] = len(DIS) * NSRC
    for t in TAGS:
        F[u'tag_' + t] = len(re.findall(u'⟦%s⟧' % t, enc))
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all5'] == len(DIS)
    assert all(F[u'tag_' + t] > 0 for t in TAGS), u'有五源标签没锚'
    return F

_B61 = _b61_scan()
B61V = lambda k, i=None: (_B61[k] if i is None else _B61[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b61 block>', 'exec')

o = NL + u'_B61 = _b61_scan()'
assert S.count(NL + u'_B60 = _b60_scan()') == 1, u'anchor _b60_scan'
B61ENV = u'B60V=B60V,' + NL + u'               B61V=B61V)'
i0 = S.find(u'# B61: 一条链路至少要能装多少字节')
while i0 >= 0:
    i1 = S.index(u'_B60 = _b60_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B61: 一条链路至少要能装多少字节')
if B61ENV in S:
    S = S.replace(B61ENV, u'B60V=B60V)')
S = S.replace(NL + u'_B60 = _b60_scan()', BLK + NL + u'_B60 = _b60_scan()')
assert S.count(u'B60V=B60V)') == 1, u'anchor env'
S = S.replace(u'B60V=B60V)', B61ENV)

PS = u"SRC['B60'] = ["
blk = (u"SRC['B61'] = ['corpus/raw/ipv6/rfc1883.txt', 'corpus/raw/ipv6/rfc2460.txt', "
       u"'corpus/raw/ipv6/rfc8200.txt', 'corpus/raw/ipv6/rfc2675.txt', 'corpus/raw/ipv6/rfc8201.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B59', 'B60'}", u"'B59', 'B60', 'B61'}"
# 只加进 ATOM(锚比对集), 不加进 HTMLSRC——五份都是纯文本面, 没有壳⇎面两口径
if NEW not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B61'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B61'" + S[m.end(1):]

M1 = u'# ---- B61 DERIV (generated by corpus/_wire61.py from corpus/_deriv61.json; do not hand-edit) ----'
M2 = u'# ---- /B61 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B60'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv61.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B61'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B61': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b61 block>', 'exec'), NS)
env = NS['B61V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b61flat.json', encoding='utf-8'))


def deep(x):
    return [deep(y) for y in x] if isinstance(x, list) else list(x) if isinstance(x, tuple) else x


for k, v in FLAT.items():
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
        got = eval(v, dict(NS), {'B61V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b60_scan' in S and u'_b61_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b61_scan+B61V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values()),
         env('anchor_total'), env('anchor_distinct'), env('checks')))
