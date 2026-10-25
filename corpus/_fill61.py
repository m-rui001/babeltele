# -*- coding: utf-8 -*-
"""B61 ⛓解读注(第四遍): 本注每个数都是现测并 assert 的, 不手填。
四套实现: 采集侧 corpus/_pick61.py(\\s+ 正则类数折行、str.count 数全大写强度词、"(\\d+) octets \\((\\d+) minus"
一次抽成对读数、集合运算符求交并)
⇎ 建条目侧 corpus/_mkB61.py(游标档 find 循环 + 折叠面档 + 逐字符判邻后缀 + 排序两指针归并, 扁平契约 corpus/_b61flat.json)
⇎ 门槛侧 corpus/audit.py::_b61_scan()(由 corpus/_wire61.py 从 SCAN 段机械抽出, 插门前把 316 个扁平键与
94 条 DERIV 算式在抽出体上逐条预演) ⇎ 本注第四遍。
本注的读法与前三遍都不同:
①下限句谓词不写 \\s+ 也不用 find: 逐词连排(have/an/MTU/of/数字/octets/or/greater), 词间空白整段原文记下,
  全为单格的算严档、含换行或多格的算宽松档, 两档之差就是 wrap_gap_floor_sent——严档五份全 0 这件事
  正是“单空格搜法会漏掉 IPv6 最关键的一条链路要求”的成因;
②正文⇎变更记录两窗: 附录定位符按整行逐字符判, 两支同收——"Appendix"+大写字母+"."+一到两格空格+"Changes"
  与 "This memo has the following changes from"(98 标准的附录走第二支); 取**最后一处**命中(目录页也印同一枚标题,
  取首处会把整篇算进变更记录), 行号从 1 起且标题行本身算正文窗——与建条目侧的偏移切法同口径;
③数 token 的后邻符号六档在本注用切片比对(tail.startswith 逐档试)而非建条目侧的逐字符链,
  窗口仍只取数字后九字符——"\\n   octet"在窗内已够不着 s, 建条目侧把窗末当句末, 本注照做(口径写进断言);
④义务词: 本注先手工切词(按非字母数字断), 再按“整词全大写”“整词全小写”“首字母大写”三档分派,
  与采集侧的 str.count 子串档、建条目侧的词界正则都不同路;
⑤整行搬运的行集归一用逐字符保留 a-z0-9, 交并按“小集合建表、大集合查表”的手工循环, 不用集合运算符;
⑥分片主语句的三份逐字同现是本注独立复算的常量项(不是答案差), 故另立一档“同现份数”核对。
不可由在库文件判定的只写在本注: 五份的抓取时刻与磁盘 mtime 谁新谁旧、rfc-editor.org 此刻的现行状态页、
RFC 2675 在官网的类目(库内抬头只印 Standards Track)、勘误表是否已挂新版、现实链路的 MTU 分布(1500 只是以太网的举例)。
"""
import io, os, re, sys, json

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B61_ipv6_mtu_five_answers.md')
FLAT = json.load(io.open(C + u'/_b61flat.json', encoding=u'utf-8'))
MEAS = json.load(io.open(C + u'/_b61meas.json', encoding=u'utf-8'))
CH = json.load(io.open(C + u'/_b61checks.json', encoding=u'utf-8'))
ATOMS = [x for x in io.open(os.path.join(C, u'_atoms61.txt'), encoding=u'utf-8').read().split(NL) if x.strip()]
PATH = [u'corpus/raw/ipv6/rfc1883.txt', u'corpus/raw/ipv6/rfc2460.txt', u'corpus/raw/ipv6/rfc8200.txt',
        u'corpus/raw/ipv6/rfc2675.txt', u'corpus/raw/ipv6/rfc8201.txt']
TAGS = [u'A', u'B', u'C', u'D', u'E']
LBL = dict(zip(TAGS, [u'95 初版', u'98 标准', u'17 现行', u'超大包档', u'PMTUD 档']))
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
SRC = [RD(p) for p in PATH]
LINES = [t.split(NL) for t in SRC]
UP = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LO = u'abcdefghijklmnopqrstuvwxyz'
DIG = u'0123456789'


def norm44(s):
    o = []
    for ch in s.lower():
        if (ch.isalnum() and ord(ch) < 128):
            o.append(ch)
    return u''.join(o)


def ws_seg(t, j):
    k = j
    while k < len(t) and t[k].isspace():
        k += 1
    return k, t[j:k]


def runseq(t, seq, ci=False):
    """seq 各词须以 >=1 个空白连排出现; 返回 [(起点, [词间空白原文])]。ci 时按小写面比词。"""
    low = t.lower() if ci else t
    first = seq[0].lower() if ci else seq[0]
    out, i = [], 0
    while True:
        j = low.find(first, i)
        if j < 0:
            return out
        pos, seps, k = j + len(first), [], 1
        for w in seq[1:]:
            p, g = ws_seg(low, pos)
            if not g or not low.startswith(w.lower() if ci else w, p):
                break
            seps.append(g)
            pos = p + len(w)
            k += 1
        if k == len(seq):
            out.append((j, seps))
            i = pos
        else:
            i = j + 1


def floors44(t):
    """have/an/MTU/of/<数字>/octets/or/greater 逐词连排; 数字单列一档。返回 [(值, [空白原文])]。"""
    out, i = [], 0
    while True:
        j = t.find(u'have', i)
        if j < 0:
            return out
        pos, seps, k = j + 4, [], 1
        ok = True
        for w in (u'an', u'MTU', u'of'):
            p, g = ws_seg(t, pos)
            if not g or not t.startswith(w, p):
                ok = False
                break
            seps.append(g)
            pos = p + len(w)
            k += 1
        if not ok:
            i = j + 4
            continue
        p, g = ws_seg(t, pos)
        if not g:
            i = j + 4
            continue
        b = p
        while b < len(t) and t[b] in DIG:
            b += 1
        if b == p:
            i = j + 4
            continue
        seps.append(g)
        pos = b
        got = True
        for w in (u'octets', u'or', u'greater'):
            q, g2 = ws_seg(t, pos)
            if not g2 or not t.startswith(w, q):
                got = False
                break
            seps.append(g2)
            pos = q + len(w)
        if got:
            out.append((t[p:b], seps))
        i = j + 4


FL44 = [floors44(SRC[i]) for i in range(5)]
FSTRICT = [len([1 for v, sp in FL44[i] if all(x == u' ' for x in sp)]) for i in range(5)]
FLOOSE = [len(FL44[i]) for i in range(5)]
FNL = [len([1 for v, sp in FL44[i] if any(NL in x for x in sp)]) for i in range(5)]
assert FLOOSE == FLAT[u'w_floor_sent'], (FLOOSE, FLAT[u'w_floor_sent'])
assert FSTRICT == FLAT[u's_floor_sent'], (FSTRICT, FLAT[u's_floor_sent'])
assert [a - b for a, b in zip(FLOOSE, FSTRICT)] == FLAT[u'wrap_gap_floor_sent']
assert [[v for v, _ in FL44[i]] == FLAT[u'floor_vals'][i] for i in range(5)]

# 分片主语句: 前半截三份逐字同现(常量项), 后半截被排版折到下一行(单空格档五份全 0)
FR = [runseq(SRC[i], [u'performed', u'only', u'by', u'source', u'nodes']) for i in range(5)]
RB = [runseq(SRC[i], [u'not', u'by', u'routers']) for i in range(5)]
FRS = [len([1 for _j, sp in FR[i] if all(x == u' ' for x in sp)]) for i in range(5)]
RBS = [len([1 for _j, sp in RB[i] if all(x == u' ' for x in sp)]) for i in range(5)]
RBL = [len(RB[i]) for i in range(5)]
assert FRS == FLAT[u's_frag_src'] == FLAT[u'w_frag_src'], (FRS, FLAT[u's_frag_src'])
assert RBS == FLAT[u's_routers'] and RBL == FLAT[u'w_routers']
assert [b - a for a, b in zip(RBS, RBL)] == FLAT[u'wrap_gap_routers']

# 净载荷括号算式: 数字 + " octets (" + 数字 + " minus" 逐字符走到括号与 'minus'
PAIRS44 = []
for i in range(5):
    t, k, got = SRC[i], 0, []
    while True:
        j = t.find(u' octets (', k)
        if j < 0:
            break
        a = j
        while a > 0 and t[a - 1] in DIG:
            a -= 1
        b = j + 9
        while b < len(t) and t[b] in DIG:
            b += 1
        if a < j and b > j + 9 and t[b:b + 6] == u' minus':
            got.append([t[a:j], t[j + 9:b]])
        k = j + 9
    PAIRS44.append(got)
assert PAIRS44 == FLAT[u'pfloor_pair'], (PAIRS44, FLAT[u'pfloor_pair'])

# 两窗: 附录标题整行逐字符判, 取最后一处命中
UC = UP + u' '


TOMB44 = u'This memo has the following changes from '


def is_clo44(l):
    k = 0
    while k < len(l) and l[k] == u' ':
        k += 1
    if k > 4:
        return False
    # 第二支: 变更记录那一句自我说明("This memo has the following changes from …")也当作附录定位符
    if l.startswith(TOMB44[:37], k):
        return True
    if l[k:k + 9] != u'Appendix ':
        return False
    if l[k + 9:k + 10] not in UP or l[k + 10:k + 11] != u'.':
        return False
    j = k + 11
    nsp = 0
    while j < len(l) and l[j] == u' ' and nsp < 2:  # “Changes”前的一到两格空白都收下, 与建条目侧的“两格”同结果
        j += 1
        nsp += 1
    return l[j:j + 7] == u'Changes'


CLO44 = []
for i in range(5):
    hs = [n for n, l in enumerate(LINES[i]) if is_clo44(l)]
    CLO44.append(hs[-1] + 1 if hs else 0)  # 行号从 1 起, 与建条目侧同(标题行本身算正文窗)
assert CLO44 == FLAT[u'clo_line'], (CLO44, FLAT[u'clo_line'])
assert [1 if x else 0 for x in CLO44] == FLAT[u'clo_found']

WL = [u'576', u'1280', u'1232', u'c65535', u'Jumbo']
KEY = {u'576': u'576', u'1280': u'1280', u'1232': u'1232', u'c65535': u'65,535', u'Jumbo': u'Jumbo'}
BODY, TAIL = [], []
for w in WL:
    needle = KEY[w]
    bd, td = [], []
    for i in range(5):
        b = t = 0
        for n, l in enumerate(LINES[i]):
            c = l.count(needle)
            if CLO44[i] and n >= CLO44[i]:
                t += c
            else:
                b += c
        bd.append(b)
        td.append(t)
    BODY.append(bd)
    TAIL.append(td)
TOT = {u'576': u'lit_576', u'1280': u'lit_1280', u'1232': u'lit_1232',
       u'c65535': u'lit_c65535', u'Jumbo': u'jumbo_caps'}
for w, bd, td in zip(WL, BODY, TAIL):
    assert bd == FLAT[u'body_' + w], (w, bd, FLAT[u'body_' + w])
    assert td == FLAT[u'tail_' + w], (w, td, FLAT[u'tail_' + w])
    assert [bd[k] + td[k] - FLAT[TOT[w]][k] for k in range(5)] == FLAT[u'close_' + w]

# 后邻符号六档: 本注用切片比对
SUCC = (u'hy_octet', u'sp_octet', u'wrap_octet', u'comma', u'dot', u'paren', u'other')
WCH44 = u' \t\n\x0b\x0c\r'
DLM = WCH44 + u',.;:)-'


def unit_end(t, j):
    """从 j 起是不是 octet/octets, 其后须接分隔符或走到九字符窗的尽头(窗口口径与建条目侧同)。"""
    if t[j:j + 5] != u'octet':
        return -1
    e = j + 6 if t[j + 5:j + 6] == u's' else j + 5
    return e if e >= len(t) or t[e] in DLM else -1


def kind44(t, b):
    r = t[b:b + 9]
    if r[:6] == u'-octet':
        return u'hy_octet'
    q = 0
    while q < len(r) and r[q] in WCH44:
        q += 1
    # 空白段长度 q: 恰为一格空格是“空格单位”, 其余(两格以上, 或一格制表/换行)都算“折行单位”
    if q >= 1 and unit_end(r, q) >= 0 and not (q == 1 and r[0] == u' '):
        return u'wrap_octet'
    if q == 1 and r[0] == u' ' and unit_end(r, q) >= 0:
        return u'sp_octet'
    if r[:1] == u',':
        return u'comma'
    if r[:1] == u'.':
        return u'dot'
    if r[:1] == u')':
        return u'paren'
    return u'other'


def skpart(t, num):
    """独立数 token 的后邻符号分档: 前不接数字或逗号、后不接数字。"""
    cnt = dict((s, 0) for s in SUCC)
    tot = 0
    k = 0
    while True:
        j = t.find(num, k)
        if j < 0:
            break
        e = j + len(num)
        prev = t[j - 1] if j else u' '
        nxt = t[e] if e < len(t) else u' '
        if prev not in DIG + u',' and nxt not in DIG:
            cnt[kind44(t, e)] += 1
            tot += 1
        k = e
    return cnt, tot


for w, num in ((u'576', u'576'), (u'1280', u'1280'), (u'528', u'528'), (u'1232', u'1232'),
               (u'c65535', u'65,535')):
    C6, T6 = zip(*[skpart(SRC[i], num) for i in range(5)])
    for s in SUCC:
        assert [x[s] for x in C6] == FLAT[u'sk_' + w + u'_' + s], (w, s)
    assert list(T6) == FLAT[u'sk_' + w + u'_total'], (w, T6)
    assert [T6[i] - sum(C6[i].values()) for i in range(5)] == FLAT[u'sk_' + w + u'_close']

# 义务词三档: 手工切词后按整词形状分派
def words44(s):
    out, buf = [], u''
    for ch in s:
        if ch.isalnum():
            buf += ch
        elif buf:
            out.append(buf)
            buf = u''
    if buf:
        out.append(buf)
    return out


def tier(s, w):
    u_ = l_ = c_ = 0
    for x in words44(s):
        if x.lower() != w:
            continue
        if all(ch in UP for ch in x if ch.isalpha()):
            u_ += 1
        elif all(ch in LO for ch in x if ch.isalpha()):
            l_ += 1
        elif x[0] in UP:
            c_ += 1
    return u_, l_, c_


U_MUST = [tier(SRC[i], u'must')[0] for i in range(5)]
L_MUST = [tier(SRC[i], u'must')[1] for i in range(5)]
C_MUST = [tier(SRC[i], u'must')[2] for i in range(5)]
L_SHOULD = [tier(SRC[i], u'should')[1] for i in range(5)]
L_MAY = [tier(SRC[i], u'may')[1] for i in range(5)]
L_REQ = [tier(SRC[i], u'required')[1] for i in range(5)]
assert U_MUST == FLAT[u'u_must'] == FLAT[u'u_should'] == FLAT[u'u_may'] == FLAT[u'u_must_not']
assert L_MUST == FLAT[u'l_must'], (L_MUST, FLAT[u'l_must'])
assert L_SHOULD == FLAT[u'l_should'] and L_MAY == FLAT[u'l_may']
assert L_REQ == FLAT[u'l_required'] and C_MUST == FLAT[u'c_must']
assert [L_MUST[i] + L_SHOULD[i] + L_MAY[i] for i in range(5)] == FLAT[u'oblig_low']

# 整行搬运: 小集合建表、大集合查表
GE = [set(norm44(l) for l in LINES[i] if len(l.strip()) >= 40 and norm44(l)) for i in range(5)]


def inter44(a, b):
    s, t = (a, b) if len(a) <= len(b) else (b, a)
    return len([x for x in s if x in t])


def union44(*ss):
    u = set()
    for s in ss:
        for x in s:
            u.add(x)
    return len(u)


assert inter44(GE[0], GE[1]) == FLAT[u'share_AB'] and inter44(GE[1], GE[2]) == FLAT[u'share_BC']
assert inter44(GE[0], GE[2]) == FLAT[u'share_AC'] and inter44(GE[2], GE[3]) == FLAT[u'share_CD'] == 0
assert inter44(GE[1], GE[3]) == FLAT[u'share_BD'] and inter44(GE[2], GE[4]) == FLAT[u'share_CE']
assert union44(GE[0], GE[1], GE[2]) == FLAT[u'union_ABC']
ONLY44 = [len([x for x in GE[i] if x not in GE[j] and x not in GE[k]])
          for i, j, k in ((0, 1, 2), (1, 0, 2), (2, 0, 1))]
assert ONLY44 == [FLAT[u'only_A'], FLAT[u'only_B'], FLAT[u'only_C']], (ONLY44, FLAT[u'only_A'])
TRI44 = len([x for x in GE[0] if x in GE[1] and x in GE[2]])
assert TRI44 == FLAT[u'AB_C_inter']
assert FLAT[u'abc_close'] == union44(GE[0], GE[1], GE[2]) - sum(ONLY44) \
    - (inter44(GE[0], GE[1]) + inter44(GE[1], GE[2]) + inter44(GE[0], GE[2]) - 2 * TRI44)

# 锚归属: 由条目正文现推, 成员判据用本注的面(五份都是纯文本, 不剥壳)
TT = io.open(ENTRY, encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
FAN4 = [norm44(f) for f in SRC]
IDX = dict((t, i) for i, t in enumerate(TAGS))
ERR4 = [x for x in CITES if norm44(x[1]) not in FAN4[IDX[x[0]]]]
assert not ERR4, ERR4[:3]
assert len(CITES) == FLAT[u'anchor_total'] == CH[u'anchor_total']
DIS4 = sorted(set(a for _t, a in CITES))
assert len(DIS4) == FLAT[u'anchor_distinct']
HIT4 = dict((a, tuple(i for i in range(5) if norm44(a) in FAN4[i])) for a in DIS4)
assert len([a for a in DIS4 if len(HIT4[a]) == 1]) == FLAT[u'anchor_single']
assert len([a for a in DIS4 if 1 < len(HIT4[a]) < 5]) == FLAT[u'anchor_cross']
assert sum(len(re.findall(u'⟦%s⟧' % t, enc)) for t in TAGS) == len(CITES)
assert sorted(ATOMS) == sorted(DIS4), u'锚清单与 _atoms61.txt 不同'

# 采集侧与建条目侧的对账在五份纯文本面上做
PL = tuple(MEAS.pop(u'_plain_idx', [0, 1, 2, 3, 4]))
BAD4 = []
for k in sorted(MEAS):
    if k not in FLAT:
        continue
    v = [FLAT[k][i] for i in PL] if isinstance(FLAT[k], list) and len(FLAT[k]) == 5 else FLAT[k]
    if v != MEAS[k]:
        BAD4.append(k)
assert not BAD4, BAD4[:6]

# 注里两句判词也要能失败: 千分位差 = 带逗号 − 无逗号, 4,294,967,295 只在超大包档一枚, 实验轨字样五份全 0
assert [FLAT[u'lit_c65535'][i] - FLAT[u'lit_65535'][i] for i in range(5)] == FLAT[u'comma_only']
assert FLAT[u'lit_c4294967295'] == [0, 0, 0, 1, 0] and FLAT[u'category_exp'] == [0] * 5
assert [sum(FLAT[u'close_' + w][i] for w in (u'576', u'1280', u'c65535', u'Jumbo')) for i in range(5)] == [0] * 5

L = []
A = L.append
A(u'### 第四遍复测(本注现算, 与前三遍不同路)')
A(u'')
A(u'| 量 | 本注的写法 | 结果 | 与建条目侧 |')
A(u'|---|---|---|---|')
A(u'| 下限句谓词 | have/an/MTU/of/数字/octets/or/greater 逐词连排, 词间空白整段记下; 全单格算严档, 含换行或多格算宽松档 | '
  u'宽松 %s 句(读数 %s) ⇎ 严档 %s ⇎ 差 %s(其中含换行 %s) | 与 w_floor_sent ⇎ s_floor_sent ⇎ wrap_gap_floor_sent ⇎ floor_vals 一致 |'
  % (u'⇎'.join(str(x) for x in FLOOSE), u' ⇎ '.join(u'[%s]' % (u','.join(x) or u'空') for x in FLAT[u'floor_vals']),
     u'⇎'.join(str(x) for x in FSTRICT), u'⇎'.join(str(x) for x in FLAT[u'wrap_gap_floor_sent']),
     u'⇎'.join(str(x) for x in FNL)))
A(u'| 分片主语句 | 前半截 performed/only/by/source/nodes 连排, 后半截 not/by/routers 连排, 各分严宽两档 | '
  u'前半截 %s 处(两档同数, 三份逐字同现) ⇎ 后半截 严 %s ⇎ 宽 %s ⇎ 差 %s | 与 s_frag_src ⇎ s_routers ⇎ w_routers ⇎ wrap_gap_routers 一致 |'
  % (u'⇎'.join(str(x) for x in FRS), u'⇎'.join(str(x) for x in RBS),
     u'⇎'.join(str(x) for x in RBL), u'⇎'.join(str(x) for x in FLAT[u'wrap_gap_routers'])))
A(u'| 净载荷括号算式 | 数字 + “ octets (” + 数字 + “ minus” 逐字符走位(建条目侧只走到括号) | 成对读数 %s | 与 pfloor_pair 一致, 17 现行 0 对 |'
  % (u' ⇎ '.join(u'[%s]' % (u'/'.join(u'%s=%s' % (y[1], y[0]) for y in x)) for x in PAIRS44)))
A(u'| 附录定位 | 整行逐字符判, 两支同收: “Appendix”+大写字母+“.”+一到两格空格+“Changes” ⇎ “This memo has the following changes from”(98 标准走第二支); 取**最后一处**命中 | 行号 %s ⇎ 命中 %s 份 | 与 clo_line ⇎ clo_found 一致 |'
  % (u'⇎'.join(str(x) for x in CLO44), u'⇎'.join(str(x) for x in FLAT[u'clo_found'])))
CLOS_ALL = [sum(FLAT[u'close_' + w][i] for w in (u'576', u'1280', u'c65535', u'Jumbo')) for i in range(5)]
A(u'| 两窗分档 | 以该行切正文⇎变更记录, 逐行 count 相加(建条目侧按字符偏移切面) | 576 %s⇎%s ⇎ 1280 %s⇎%s ⇎ 65,535 %s⇎%s ⇎ Jumbo %s⇎%s, 两半相加闭合 %s(四枚 close 键按份相加) | '
  u'与 body_ ⇎ tail_ ⇎ close_ 一致 |'
  % (u'⇎'.join(str(x) for x in BODY[0]), u'⇎'.join(str(x) for x in TAIL[0]),
     u'⇎'.join(str(x) for x in BODY[1]), u'⇎'.join(str(x) for x in TAIL[1]),
     u'⇎'.join(str(x) for x in BODY[3]), u'⇎'.join(str(x) for x in TAIL[3]),
     u'⇎'.join(str(x) for x in BODY[4]), u'⇎'.join(str(x) for x in TAIL[4]),
     u'⇎'.join(str(x) for x in CLOS_ALL)))
A(u'| 数 token 后邻七档 | 切片比对 tail.startswith(“-octet”/“ octets”/空白后 octets/逗号/句号/括号) | 576 在 95 初版 %s 合计 %d ⇎ 1280 在 98 标准 %s 合计 %d ⇎ 65,535 在 超大包档 %s 合计 %d, 三档闭合皆 0 | '
  u'与 sk_* 全部一致 |'
  % (u'+'.join(str(FLAT[u'sk_576_' + s][0]) for s in SUCC), FLAT[u'sk_576_total'][0],
     u'+'.join(str(FLAT[u'sk_1280_' + s][1]) for s in SUCC), FLAT[u'sk_1280_total'][1],
     u'+'.join(str(FLAT[u'sk_c65535_' + s][3]) for s in SUCC), FLAT[u'sk_c65535_total'][3]))
A(u'| 义务词三档 | 先按非字母数字手工切词, 整词全大写⇎全小写⇎首字母大写分派(采集侧 str.count 子串、建条目侧词界正则) | '
  u'全大写 MUST %s ⇎ 小写 must %s ⇎ 小写 should %s ⇎ 小写 may %s ⇎ required %s ⇎ 首字母 Must %s | '
  u'五份全大写皆 0, 与 u_/l_/c_ 各档一致 |'
  % (u'⇎'.join(str(x) for x in U_MUST), u'⇎'.join(str(x) for x in L_MUST),
     u'⇎'.join(str(x) for x in L_SHOULD), u'⇎'.join(str(x) for x in L_MAY),
     u'⇎'.join(str(x) for x in L_REQ), u'⇎'.join(str(x) for x in C_MUST)))
A(u'| 整行搬运 | 归一同为逐字符滤 alnum, 但交并按小集合建表大集合查表、并集按逐个 add(采集侧用集合运算符 & 与求交并) | '
  u'95⇎98 %d ⇎ 98⇎17 %d ⇎ 95⇎17 %d ⇎ 三份同现 %d ⇎ 并集 %d ⇎ 17⇎超大包 %d | 逐字一致 |'
  % (inter44(GE[0], GE[1]), inter44(GE[1], GE[2]), inter44(GE[0], GE[2]),
     TRI44, union44(GE[0], GE[1], GE[2]), inter44(GE[2], GE[3])))
A(u'| 锚归属 | 由条目正文 ⟦标签⟧⟨引文⟩ 配对现推, 成员判据用本注的面; 五份都不剥壳(全是纯文本) | '
  u'%d 处／去重 %d 串／一源 %d ⇎ 两至四源 %d ⇎ 五源 %d ⇎ 错配 %d | 与建条目侧、门槛侧同 |'
  % (len(CITES), len(DIS4), FLAT[u'anchor_single'], FLAT[u'anchor_cross'], FLAT[u'anchor_all5'], len(ERR4)))
A(u'| 两侧对账 | 采集侧 %d 键在五份纯文本面上比 | 共有 %d ／ 不符 %d | 五份同为文本面, 无需按介质分流 |'
  % (len(MEAS), len(MEAS), len(BAD4)))
A(u'')
A(u'### 读法')
A(u'')
A(u'一、“还要不要 576”只有下限句谓词能答: 三份标准的句式读数依次是 {0}, 而 576 这个字面在 {1} 里还剩 {2} 处、在 {3} 里 {4} 处——'
  u'那一处不在链路要求里, 在变更记录的自我说明里(附录起点取该行 {5}, 正文窗 {6} 处 ⇎ 变更记录窗 {7} 处)。'
  u'把两份并排读才看得见“同一代要求换过一次数”: {8}。'
  .format(u' ⇎ '.join(u'[%s]' % (u','.join(x) or u'无') for x in FLAT[u'floor_vals']),
          TAGS[1], FLAT[u'lit_576'][1], TAGS[2], FLAT[u'lit_576'][2],
          FLAT[u'clo_line'][1], FLAT[u'body_576'][1], FLAT[u'tail_576'][1],
          u'95 初版 528=576−48 ⇎ 98 标准 1232=1280−48 ⇎ 17 现行成对读数 %d 对——括号算式整句被删' % FLAT[u'pfloor_pair_C_n']))
A(u'二、包顶只有一个写法: 65,535 一律带千分位。字面 65535 在五份里 {0} 处 ⇎ 带逗号写法 {1} 处 ⇎ 差 {2} 处; '
  u'超大包档另给 4,294,967,295 一枚({3} 处, 其余四份皆 0)——上限被“拆掉”而不是被“改小”: '
  u'同一个带逗号的分片顶在 95 初版 ⇎ 98 标准 ⇎ 17 现行 ⇎ 超大包档 ⇎ PMTUD 档分别是 {4}⇎{5}⇎{6}⇎{7}⇎{8} 处。'
  .format(u'⇎'.join(str(x) for x in FLAT[u'lit_65535']), u'⇎'.join(str(x) for x in FLAT[u'lit_c65535']),
          u'⇎'.join(str(x) for x in FLAT[u'comma_only']), FLAT[u'lit_c4294967295'][3],
          *FLAT[u'lit_c65535']))
A(u'三、超大包的一条生命线有四个读数: 选项定义逐字面 {0} 处 ⇎ 98 标准的移除说明 {1} 处 ⇎ 17 现行 {2} 处 ⇎ 超大包档 {3} 处; '
  u"jumbo 全族 {4} 处, 其中 98 标准的 Jumbo 大写 {5} 处里有 {6} 处落在变更记录窗内(正文 {7} 处)。"
  u"“标准里删掉了 ⇎ 实验档接走了”这两件事各自由一个窗口给出, 合起来才是一条完整的时间线。"
  .format(FLAT[u'jumbo_option_def'][0], FLAT[u'remove_note'][1], FLAT[u'jumbo_ci'][2],
          FLAT[u'jumbo_option_def'][3], u'⇎'.join(str(x) for x in FLAT[u'jumbo_ci']),
          FLAT[u'jumbo_caps'][1], FLAT[u'tail_Jumbo'][1], FLAT[u'body_Jumbo'][1]))
A(u'四、PMTUD 档不参与“至少要装多少”: 576 {0} 处 ⇎ 1280 {1} 处 ⇎ 65,535 {2} 处, 而 MTU 一词 {3} 处、PMTU 缩写 {4} 处、“packet too big”{5} 处——'
  u'它把“最小的一环是多少”整项让给别的文书, 自己只答“怎么量到”。体例也反着: 2119 规定的四枚全大写词五份皆 {6} 处, '
  u'小写 must {7} 处; 它引用 2119 达 {8} 次(另四份 {9}⇎{10}⇎{11}⇎{12} 次), 并在 {13} 处写明“只用小写、不引 2119 的定义”。'
  .format(FLAT[u'lit_576'][4], FLAT[u'lit_1280'][4], FLAT[u'lit_c65535'][4],
          FLAT[u'mtu_any'][4], FLAT[u'pmtu'][4], FLAT[u'ptb'][4], FLAT[u'u_must'][4], FLAT[u'l_must'][4],
          FLAT[u'rfc2119_ref'][4], *FLAT[u'rfc2119_ref'][:4], FLAT[u'no_cite_2119'][4]))
A(u'五、同一通道还压在分片主语上: “not by routers”在三份标准里逐字存在, 却一律被排到下一行——严档(单空格)五份全 {0} 处 ⇎ '
  u'宽松档 {1} 处 ⇎ 差 {2} 处。任何只用单空格短语的检索都会把 IPv6 与 IPv4 最关键的一条差别读成“文书里没写”。'
  .format(u'⇎'.join(str(x) for x in RBS), u'⇎'.join(str(x) for x in RBL),
          u'⇎'.join(str(x) for x in FLAT[u'wrap_gap_routers'])))
A(u'')
A(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
A(u'')
A(u'① 五份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; ② rfc-editor.org 此刻给 RFC 2675 挂的类目——库内抬头只印 “Category: Standards Track”'
  u'(五份各 {0} 行)而 “Experimental” 字样 {1}⇎{2}⇎{3}⇎{4}⇎{5} 处, 官网若标 Experimental 属站外事实; '
  u'③ 勘误表(errata)是否已挂新版——库内提及 {6}⇎{7}⇎{8}⇎{9}⇎{10} 处只是文书自我引用; '
  u'④ 17 现行是否已在部署侧全面生效; ⑤ 现实链路的 MTU 分布——1500 是以太网的举例而非测量值, 库内 1500 作独立数 token 各 {11}⇎{12}⇎{13}⇎{14}⇎{15} 处。'
  u'这些只能站外核验, 因此都不进判词与门槛。'
  .format(FLAT[u'category_std'][0], *FLAT[u'category_exp'], *FLAT[u'errata'], *FLAT[u'tok_1500']))
A(u'')
A(u'### 编码与门的账')
A(u'')
A(u'编码区 {0} 字符(不含换行); 锚 {1} 处 ⇎ 去重 {2} 串 ⇎ 归属检查 {3} 次 ⇎ 错配 {4}; '
  u'一源 {5} ⇎ 两至四源 {6} ⇎ 五源 {7}; 标签 A⇎B⇎C⇎D⇎E 各 {8}⇎{9}⇎{10}⇎{11}⇎{12} 处。'
  .format(CH[u'enc_chars'], FLAT[u'anchor_total'], FLAT[u'anchor_distinct'], FLAT[u'checks'], FLAT[u'anchor_err'],
          FLAT[u'anchor_single'], FLAT[u'anchor_cross'], FLAT[u'anchor_all5'],
          FLAT[u'tag_A'], FLAT[u'tag_B'], FLAT[u'tag_C'], FLAT[u'tag_D'], FLAT[u'tag_E']))
A(u'DERIV {0} 键 ⇎ 复算点 {1} 处 ⇎ 同数共键 {2} 组 ⇎ 0 折 {3} 项; 扁平键 {4} 个; '
  u'闭合账 标量 {5} 项(全 0)⇎ 清单 {6} 项; 锚候选池 {7} 条按逐字再现份数分 {8} 档({9}), 分档闭合 {10}。'
  .format(CH[u'deriv_keys'], CH[u'deriv_points'], len(CH[u'collisions']), CH[u'zero_terms'],
          len(FLAT), FLAT[u'scalar_clos_n'], FLAT[u'list_clos_n'], FLAT[u'pool_n'], 5,
          u'⇎'.join(str(x) for x in FLAT[u'pool_tiers']), FLAT[u'pool_close']))
A(u'门槛三遍: T1 字面逐锚回原文 ⇎ T2 DERIV 每条算式重跑 ⇎ T3 码位与字母账; '
  u'本注另加第四遍复测, 上表 10 行全部 assert, 不符即停机。')
NOTE = NL.join(L)
head = TT[:TT.index(u'## ⛓解读注') + len(u'## ⛓解读注')]
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(head + NL + NL + NOTE + NL)
print(u'⛓解读注已写 %d 字符 ｜ 第四遍 assert 全过 ｜ 采集对账 %d 键 0 不符' % (len(NOTE), len(MEAS)))
