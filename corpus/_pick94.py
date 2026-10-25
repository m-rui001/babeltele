# -*- coding: utf-8 -*-
"""采集遍(B94, 双轨独立实现): “ICMP 差错报文该限到什么速率、谁说了算”——六份一手文书各答一遍
792(1981: 只立源抑制机制,  gateway 可为每一枚丢弃的报文发一枚 SQ——按包尺且 N=1, 通篇无一枚速率数)
⇎ 1009(1987 老式网关需求: gateway “must be prepared to limit the frequency”, N ⇎ T 全交给配置,
   另给字节⇎包换算现场: 平均 100 字节 ⇎ 1.5 Mbps DS1 ⇎ 2,000 包/秒 ⇎ 8,000 ⇎ 16,000)
⇎ 1122(1989 主机需求: 收侧 MUST report ⇎ SHOULD throttle, 发侧只写 MAY; 全篇唯一的 “1 per second”
   是 ARP 洪泛限速不是 ICMP 差错, “0.005 per second” 是 ping 网关; ICMP 差错生成速率零枚数)
⇎ 1812(1995 路由器需求: SQ MUST 可限 ⇎ 其它差错 SHOULD 可限 ⇎ 参数 SHOULD 可配 ⇎ 怎么限 “left to
   the implementor”, IMPLEMENTATION 举三机制: count-based ⇎ timer-based ⇎ bandwidth-based)
⇎ 4443(2006 IPv6: 节点 MUST limit; 推荐 token bucket, N 可按 packets/second ⇎ 按链路带宽分数;
   timer-based “every T milliseconds” 被点名 not reasonable——1812 的示例被反转;
   唯一印出的默认值示例 B=10, N=10/s; 变更记录自陈 “Removed the Timer-based and the Bandwidth-based”
   methods; 限速条款 TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE——“谁说了算”有逐字答案)
⇎ ip-sysctl(内核实现文档: 真正把数落盘的文书——icmp_ratelimit=1000 毫秒(每目标最小间隔) ⇎
   icmp_msgs_per_sec=1000(全局每秒) ⇎ icmp_msgs_burst=50 ⇎ ratemask=6168(只限类型 3,4,11,12,
   Echo 不在内), 0=关闭, 另有 ICMPv6 ratelimit=1000)。

本文件内两条实现轨互相对账(换机制不换定义), 至少九处:
①切句: A 轨 re.split('(?<=[.!?]) +') ⇎ B 轨逐字符扫“句末标点+空白”;
②找针: A 轨游标 find 环 ⇎ B 轨 re.findall(re.escape) 整体扫描, 另立重叠档 finditer('(?=针)');
③判形状(页壳): A 轨整行序列正则 ⇎ B 轨 strip 后按 token 形状判, 逐行必须同集;
④单位换算(算术): A 轨闭式(2**b 求和、直接乘除) ⇎ B 轨逐次倍增/逐次累加, 两把尺同数才入账;
⑤块定界: A 轨节题正则上下外推 ⇎ B 轨字面端针偏移切片, 行数字符逐格同;
⑥行号映射: A 轨累积长度表+bisect ⇎ B 轨逐字符挂行号的行表;
⑦集合档⇎词频档: 语形族存在性(set 成员) ⇎ Counter 词频直方图, 两档各数一遍再对 presence;
⑧数×单位对: A 轨一条选择支正则 ⇎ B 轨手工扫数字串就地读邻词;
⑨计数尺: 字节/码位 len() ⇎ 逐字节逐字符迭代; Default 值正则 ⇎ partition 链。
所有键在口径一致的名单上逐键对账, 不符即停机; 对账结论与全部读数落 corpus/_b94meas.json。"""
import io, json, os, re, sys, bisect
from array import array
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'792', u'1009', u'1122', u'1812', u'4443', u'sys']
SRC = [u'corpus/raw/icmpRate/rfc792.txt', u'corpus/raw/icmpRate/rfc1009.txt',
       u'corpus/raw/icmpRate/rfc1122.txt', u'corpus/raw/icmpRate/rfc1812.txt',
       u'corpus/raw/icmpRate/rfc4443.txt', u'corpus/raw/icmpRate/ip-sysctl.txt']
NSRC = 6
M = {}
RECON = {}


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in SRC]
T = [b.decode('utf-8', 'replace') for b in B]
RAWL = [t.split(NL) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]

# ---------- 面非空与错误页特征(停机门槛) ----------
for i in range(NSRC):
    assert len(B[i]) > 4000, (SRC[i], len(B[i]))
    assert re.search(u'(?i)<html|<!doctype|404 Not Found|Cloudflare', T[i][:4000]) is None, SRC[i]
    assert u'ICMP' in T[i], SRC[i]


def pnorm(s):
    return u' '.join(s.lower().split())


FOLDP = [pnorm(T[i]) for i in range(NSRC)]   # split/join 折面(与逐字符铺面互为对账)

# ---------- A 轨工具 ----------
def a_cnt(hay, nd):
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def a_ub(s, w):
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha()):
            c += 1
        i = j + 1


def a_sh(x):
    return (x.strip() == u'' or x == u'\x0c'
            or re.search(u'\\[Page \\d+\\]', x) is not None
            or re.match(u'^RFC ?\\d+\\b', x) is not None
            or re.match(u'^Internet Engineering Task Force\\s*$', x) is not None
            or re.match(u'^\\s*Network Working Group\\s*$', x) is not None
            or re.match(u'^\\s*Request for Comments:\\s*\\d+\\s*$', x) is not None)


# 折面: 逐字符构造 + 每字符挂“原行号”与“原行内偏移”(B 轨行号尺直读, A 轨再经累加表换算)
def build_fold(i, keep):
    out, ix, ln = [], [], []
    for nr in keep:
        one = L[i][nr]
        k, n = 0, len(one)
        while k < n:
            if one[k].isspace():
                j = k
                while j < n and one[j].isspace():
                    j += 1
                if out and not out[-1].isspace():
                    out.append(u' ')
                    ix.append(k)      # 空白游程起点
                    ln.append(nr)
                k = j
            else:
                out.append(one[k].lower())
                ix.append(k)
                ln.append(nr)
                k += 1
        if out and not out[-1].isspace():     # 行缝(换行符处)
            out.append(u' ')
            ix.append(n)
            ln.append(nr)
    while out and out[-1].isspace():          # 面尾空白不入户(与 split/join 口径对齐)
        out.pop()
        ix.pop()
        ln.pop()
    return u''.join(out), ix, ln


FOLD, FIDX, FLINE, SHP, SPX, SPL = [], [], [], [], [], []


def build_faces():
    for i in range(NSRC):
        ka = list(range(len(L[i])))
        ks = [nr for nr in ka if not b_sh(L[i][nr])]
        f, x, n = build_fold(i, ka)
        FOLD.append(f), FIDX.append(x), FLINE.append(n)
        s, xs, ns = build_fold(i, ks)
        SHP.append(s), SPX.append(xs), SPL.append(ns)

SRAW = [NL.join(L[i]) for i in range(NSRC)]
CUMS = []
for i in range(NSRC):
    _a, _t = [], 0
    for _x in L[i]:
        _t += len(_x) + 1
        _a.append(_t)
    CUMS.append(_a)


def shp_to_rawoff(i, foff):
    """摘壳折面偏移 -> 原面码位偏移(经逐字符记录的行号 + 行内偏移回原面)。"""
    nr = SPL[i][foff]
    base = CUMS[i][nr - 1] if nr else 0
    return base + SPX[i][foff]


def a_line(i, rawoff):
    """A 轨: 累积长度表 + 二分查行号(rawoff 为原面码位偏移)。"""
    return bisect.bisect_right(CUMS[i], rawoff)


def fold_line(i, foff):
    """摘壳折面偏移 -> 原行号(随折面记的逐字符行号)。"""
    return SPL[i][foff]


# ---------- B 轨工具 ----------
def b_cnt(hay, nd):
    return len(re.findall(re.escape(nd), hay))


def b_cnt_ovl(hay, nd):
    return len(re.findall(u'(?=%s)' % re.escape(nd), hay))


def b_ub(s, w):
    return len(re.findall(u'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(w), s))


def _yrish(t):
    return len(t) == 4 and t.isdigit() and (t[:2] == u'19' or t[:2] == u'20')


def b_sh(x):
    t = x.strip().split()
    if not t:
        return True
    if x == u'\x0c' or (len(t) == 1 and t[0] == u'\x0c'):
        return True
    if len(t) >= 2 and t[-2] == u'[Page' and t[-1].endswith(u']') and t[-1][:-1].isdigit():
        return True
    if x[:3] == u'RFC' and len(t) > 1 and t[1].isdigit():
        return True
    if x[:3] == u'RFC' and t[0][3:].isdigit():      # 粘连式眉行: RFC1122 ...(须顶格)
        return True
    if t[:4] == [u'Internet', u'Engineering', u'Task', u'Force'] and len(t) == 4:
        return True
    if t[:3] == [u'Network', u'Working', u'Group'] and len(t) == 3:
        return True
    if t[:3] == [u'Request', u'for', u'Comments:'] and len(t) == 4 and t[3].isdigit():
        return True
    return False


# 逐字符行表(B 轨行号尺: 一遍线性铺表, 查行号只下标, 不累加不二分)
CHARMAP = []
for i in range(NSRC):
    m = array('i', [0]) * len(T[i])
    ln = 0
    for k, ch in enumerate(T[i]):
        m[k] = ln
        if ch == NL:
            ln += 1
    CHARMAP.append(m)


def b_line(i, off):
    return CHARMAP[i][off]


build_faces()
assert FOLDP == FOLD, u'逐字符铺折面与 split/join 折面不同面'
for i in range(NSRC):
    assert SHP[i] == pnorm(NL.join([x for x in L[i] if not b_sh(x)])), i
    for foff in (0, len(SHP[i]) - 1):
        assert a_line(i, shp_to_rawoff(i, foff)) == b_line(i, shp_to_rawoff(i, foff)) == \
            fold_line(i, foff), (i, foff)


def sents_a(txt):
    return [pnorm(z) for z in re.split(u'(?<=[.!?]) +', pnorm(txt)) if z]


def sents_b(txt):
    f = pnorm(txt)
    out, start, k, n = [], 0, 0, len(f)
    while k < n:
        if f[k] in u'.!?' and (k + 1 >= n or f[k + 1] == u' '):
            j = k + 1
            while j < n and f[j] == u' ':
                j += 1
            seg = f[start:k + 1]
            if seg.strip():
                out.append(seg)
            start = j
            k = j
            continue
        k += 1
    if start < n and f[start:].strip():
        out.append(f[start:])
    return out


# ---------- 0. 面量 ----------
M['bytes'] = [len(B[i]) for i in range(NSRC)]
M['bytes_iter'] = [sum(1 for _ in B[i]) for i in range(NSRC)]
M['bytes_stat'] = [os.path.getsize(p) for p in SRC]
M['cp'] = [len(T[i]) for i in range(NSRC)]
M['cp_iter'] = [sum(1 for _ in T[i]) for i in range(NSRC)]
M['n_lf'] = [a_cnt(T[i], NL) for i in range(NSRC)]
M['n_lf_re'] = [len(re.findall(u'\\n', T[i])) for i in range(NSRC)]
M['n_cr'] = [T[i].count(u'\r') for i in range(NSRC)]
M['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
M['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
M['ff'] = [T[i].count(u'\x0c') for i in range(NSRC)]
M['ff_alone'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
M['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
M['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
M['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
M['tab'] = [T[i].count(u'\t') for i in range(NSRC)]
M['nonascii'] = [sorted(set(ord(c) for c in T[i] if ord(c) > 127)) for i in range(NSRC)]
M['bom'] = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
assert M['bytes'] == M['bytes_iter'] == M['bytes_stat'], u'字节三把尺不同'
assert M['cp'] == M['cp_iter'], u'码位两把尺不同'
assert M['n_lf'] == M['n_lf_re'], u'换行两把尺不同'
assert sum(M['n_cr']) == 0 and sum(M['bom']) == 0 and sum(len(x) for x in M['nonascii']) == 0, \
    u'出现未见过的编码物种'
RECON['face'] = NSRC * 4
# 行式对账: splitlines − split('\n') = (换页后随换行) − 尾换行
_ffnl = [len(re.findall(u'(?=\x0c' + NL + u')', T[i])) for i in range(NSRC)]
_ffeof = [1 if T[i][-1:] == u'\x0c' else 0 for i in range(NSRC)]
_tnl = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
M['ff_before_nl'], M['ff_at_eof'], M['trailing_nl'] = _ffnl, _ffeof, _tnl
_obs = [M['splitlines'][i] - M['splitnl'][i] for i in range(NSRC)]
_pred = [_ffnl[i] - _tnl[i] + _ffeof[i] for i in range(NSRC)]
M['rows_ledger'] = [a - b for a, b in zip(_obs, _pred)]
assert M['rows_ledger'] == [0] * NSRC, (_obs, _pred)
print(u'0 面量:', json.dumps(dict((k, M[k]) for k in
      ['bytes', 'cp', 'n_lf', 'splitnl', 'splitlines', 'ff', 'blank', 'maxlen', 'tab'])))

# ---------- 1. 页壳两轨 ----------
M['shell_a'] = [len([x for x in L[i] if a_sh(x)]) for i in range(NSRC)]
M['shell_b'] = [len([x for x in L[i] if b_sh(x)]) for i in range(NSRC)]
M['shell_diff'] = [len([x for x in L[i] if a_sh(x) != b_sh(x)]) for i in range(NSRC)]
M['foot_page'] = [len([x for x in L[i] if re.search(u'\\[Page \\d+\\]', x)]) for i in range(NSRC)]
M['hdr_rfc'] = [len([x for x in L[i] if a_sh(x) and x.strip().split()[:1] == [u'RFC']]) for i in range(NSRC)]
M['shell_body'] = [M['splitnl'][i] - M['shell_b'][i] for i in range(NSRC)]
assert M['shell_a'] == M['shell_b'] and M['shell_diff'] == [0] * NSRC, \
    [(LBL[i], j + 1, L[i][j]) for i in range(NSRC) for j in range(len(L[i]))
     if a_sh(L[i][j]) != b_sh(L[i][j])][:8]
RECON['shell'] = sum(M['splitnl'])
print(u'1 壳行 A/B:', M['shell_a'], M['shell_b'], u' 页脚:', M['foot_page'], u' RFC眉行:', M['hdr_rfc'])

# ---------- 2. 年份与抬头 ----------
MONTHS = (u'January|February|March|April|May|June|July|August|September|October|November|December')
_yr = []
for i in range(NSRC):
    mt = re.search(u'(?:%s) ((19|20)\\d\\d)' % MONTHS, T[i])
    _yr.append(int(mt.group(1)) if mt else -1)
M['year'] = _yr
assert _yr[:5] == [1981, 1987, 1989, 1995, 2006], _yr
M['year_gap'] = [_yr[k + 1] - _yr[k] for k in range(4)] + [0]
M['year_span'] = max(_yr) - min([y for y in _yr if y > 0])
print(u'2 年份:', _yr, u' 间隔:', M['year_gap'], u' 跨度:', M['year_span'])

# ---------- 3. 判词针(三档口径: 逐行 ⇎ 全篇折平 ⇎ 摘壳折平) ----------
NEEDLES = [
    u'may send a source quench message for every message that it discards',
    u'should cut back the rate at which it is sending traffic',
    u'when it approaches its capacity limit rather than waiting',
    u'must be implemented by every IP module',
    u'must be prepared to limit the frequency with which it sends',
    u'for every N dropped datagrams',
    u'at most once per T millseconds',
    u'settable as part of the configuration of the gateway',
    u'disables sending Source Quenches',
    u'never sent about ICMP error messages',
    u'of the order of 100 bytes',
    u'2,000 datagrams per second per interface',
    u'throughput of 8,000 datagrams',
    u'would imply 16,000 datagrams',
    u'The recommended maximum rate is 1 per second per',
    u'the recommended maximum rate is 1 per second per destination',
    u'very low rate, e.g., 0.005 per second',
    u'should throttle itself back',
    u'includes the Internet header and at least the first 8',
    u'MUST NOT be sent as the result of receiving',
    u'host MAY send a Source Quench message if it is',
    u'MUST be able to limit the rate at which the messages can be generated',
    u'SHOULD also be able to limit the rate at which it sends other sorts',
    u'SHOULD be settable as part of the configuration',
    u'is left to the implementor',
    u'send an ICMP error message for every N dropped packets',
    u'at most once per T milliseconds',
    u'limit the rate at which ICMP messages are sent over a particular',
    u'SHOULD NOT originate ICMP Source Quench',
    u'exceeding 576 bytes',
    u'(20 bytes = 5 words)',
    u'MUST limit the rate of ICMPv6 error messages it originates',
    u'token bucket, limiting the average rate',
    u'N can be either packets/second or a fraction',
    u'allowing up to B error messages to be transmitted in a burst',
    u'allowing an error message every T',
    u'is not reasonable',
    u'The rate-limiting parameters SHOULD be configurable',
    u'the possible defaults could be B=10',
    u'N=10/s',
    u'Rate-limiting of forwarded ICMP messages is out of scope',
    u'Removed the Timer-based and the Bandwidth-based methods',
    u'TAKE PRECEDENCE OVER ANY REQUIREMENT ELSEWHERE',
    u'exactly 32 bits of type-specific data',
    u'otherwise the minimal space between responses in',
    u'icmp_msgs_per_sec limits the number',
    u'Limit maximal number of ICMP packets sent per second from this host',
    u'controls the burst size of these packets',
    u'Mask made of ICMP types for which rates are being limited',
    u'These are rate limited by default',
    u'violate RFC1122 by sending bogus responses',
    u'0 to disable any limiting',
    u'0000001100000011000 (6168)',
    u'Limit the maximal rates for sending ICMPv6 messages',
    u'left to the implementor',
]
NEEDLES = list(dict.fromkeys(NEEDLES))
NN = len(NEEDLES)
rows3 = []
for nd in NEEDLES:
    q = pnorm(nd)
    r = []
    for i in range(NSRC):
        cl = len([x for x in L[i] if q in pnorm(x)])
        cf = a_cnt(FOLD[i], q)
        cf_b = b_cnt(FOLD[i], q)
        assert cf == cf_b, (nd, i, cf, cf_b)
        cs = a_cnt(SHP[i], q)
        cs_b = b_cnt(SHP[i], q)
        assert cs == cs_b, (nd, i, cs, cs_b)
        r.append((cl, cf, cs))
    rows3.append(r)
M['needles3'] = rows3
M['needle_src'] = [[LBL[i] for i in range(NSRC) if rows3[k][i][2] > 0] for k in range(NN)]
cold = [NEEDLES[k] for k in range(NN) if not M['needle_src'][k]]
assert cold == [], cold
# 跨页壳针: 全篇折面读不到而摘壳面读得到(换页眉脚把句腰截断)
M['wrapcut'] = [[LBL[i], NEEDLES[k][:40]] for k in range(NN) for i in range(NSRC)
                if rows3[k][i][1] == 0 and rows3[k][i][2] > 0]
M['wrapcut_n'] = len(M['wrapcut'])
print(u'3 判词针 %d 枚, 全冷 %d 枚, 跨壳断句 %d 处' % (NN, len(cold), M['wrapcut_n']))

# ---------- 4. 关键句行号定位(三把行号尺: 累加+二分 ⇎ 逐字符铺表 ⇎ 折面随行表) ----------
PIN = []
for k, nd in enumerate(NEEDLES):
    q = pnorm(nd)
    for i in range(NSRC):
        if rows3[k][i][2] <= 0:
            continue
        foff = SHP[i].find(q)
        foff_b = b_cnt_ovl(SHP[i], q)
        rawoff = shp_to_rawoff(i, foff)
        la = a_line(i, rawoff)                       # 累加表 + 二分
        lb = b_line(i, rawoff)                       # 原面逐字符行表
        lc = fold_line(i, foff)                      # 折面随行表(不回原面)
        assert la == lb == lc, (nd, i, la, lb, lc)
        lend = fold_line(i, foff + len(q) - 1)
        assert a_line(i, shp_to_rawoff(i, foff + len(q) - 1)) == lend, (nd, i)
        PIN.append([LBL[i], k, nd[:44], la, lend, foff, foff_b])
M['pin_lines'] = PIN
M['pin_wrap'] = len([z for z in PIN if z[3] != z[4]])
RECON['line'] = len(PIN) * 3
assert len(PIN) == sum(sum(1 for i in range(NSRC) if rows3[k][i][2] > 0) for k in range(NN))
print(u'4 定位 %d 格(其中跨行 %d 格), 首格: %s' % (len(PIN), M['pin_wrap'], PIN[0]))

# ---------- 5. 义务词五式(两轨整词尺: 预大写化游标 ⇎ 引擎内大小写折叠; 混排另记) ----------
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']


def ob_b(s, w):
    """B 轨: 原面不动, 交给 re 的 IGNORECASE(折叠在引擎里, 不在文本里)。"""
    return len(re.findall(u'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(w), s, re.I))


def ob_exact(s, w):
    """第三把尺: 只认三种整写(全大写/全小写/首字母大写)——混写必漏。"""
    return b_ub(s, w) + b_ub(s, w.lower()) + b_ub(s, w.capitalize())


M['ob_fold'] = [[a_ub(T[i].upper(), w) for w in OB] for i in range(NSRC)]
M['ob_fold_b'] = [[ob_b(T[i], w) for w in OB] for i in range(NSRC)]
M['ob_exact'] = [[ob_exact(T[i], w) for w in OB] for i in range(NSRC)]
M['ob_odd_case'] = [[a - b for a, b in zip(M['ob_fold'][i], M['ob_exact'][i])]
                    for i in range(NSRC)]
M['ob_diff'] = [[x - y for x, y in zip(M['ob_fold'][i], M['ob_fold_b'][i])] for i in range(NSRC)]
assert M['ob_diff'] == [[0] * len(OB) for _ in range(NSRC)], \
    [(LBL[i], OB, M['ob_fold'][i], M['ob_fold_b'][i]) for i in range(NSRC)
     if M['ob_diff'][i] != [0] * len(OB)]
M['ob_tot'] = [sum(x) for x in M['ob_fold']]
print(u'5 义务词:', M['ob_fold'], u' 合计:', M['ob_tot'], u' 混写:', M['ob_odd_case'])

# ---------- 6. 数×单位对(两轨) ----------
RX = re.compile(u'(?<![A-Za-z0-9.,])(\\d+(?:[.,]\\d+)?)[ ]?'
                u'(per second|datagrams per second|packets/second|/s|milliseconds|millseconds|'
                u'mbps|kbps|bytes|octets|words|times per second)(?![A-Za-z])', re.I)
UNITW = [u'per second', u'datagrams per second', u'packets/second', u'/s', u'milliseconds',
         u'millseconds', u'mbps', u'kbps', u'bytes', u'octets', u'words', u'times per second']


def scan_pairs(text):
    """B 轨: 手工扫数字串就地读邻词(含 /s 这种前斜杠单位)。"""
    out, i, n = [], 0, len(text)
    low = text.lower()
    while i < n:
        c = text[i]
        if not c.isdigit() or (i > 0 and (text[i - 1].isalnum() or text[i - 1] == u'.')):
            i += 1
            continue
        j, sepd = i, 0
        while j < n and (text[j].isdigit()
                         or (sepd == 0 and text[j] in u'.,' and j + 1 < n and text[j + 1].isdigit())):
            if text[j] in u'.,':
                sepd = 1
            j += 1
        num = text[i:j]
        k = j
        while k < n and text[k] == u' ':
            k += 1
        rest = low[k:k + 24]
        for u_ in sorted([x.lower() for x in UNITW], key=len, reverse=True):
            if rest.startswith(u_) and not (rest[len(u_):len(u_) + 1].isalpha()):
                out.append((num, u_))
                break
        i = j
    return sorted(set(out))


pa = [sorted(set((m[0], m[1].lower()) for m in RX.findall(T[i]))) for i in range(NSRC)]
pb = [scan_pairs(T[i]) for i in range(NSRC)]
M['pairs_a'] = [[list(x) for x in pa[i]] for i in range(NSRC)]
M['pairs_b'] = [[list(x) for x in pb[i]] for i in range(NSRC)]
M['pairs_diff'] = [sorted(set(map(tuple, pa[i])) ^ set(map(tuple, pb[i])))
                   for i in range(NSRC)]
assert M['pairs_diff'] == [[]] * NSRC, M['pairs_diff']
print(u'6 数×单位对:')
for i in range(NSRC):
    print(u'   %s %s' % (LBL[i], M['pairs_a'][i]))

# ---------- 7. 语境裁决: 含“rate”与数字的句子落在哪个话题(三句窗) ----------
assert [sents_a(T[i]) for i in range(NSRC)] == [sents_b(T[i]) for i in range(NSRC)], \
    u'两把切句尺不同句集'
M['sents_n'] = [len(sents_a(T[i])) for i in range(NSRC)]
CTXKW = {u'arp': [u'arp'], u'icmp': [u'icmp'], u'ping_echo': [u'ping', u'echo'],
         u'token': [u'token'], u'timestamp': [u'timestamp'], u'source quench': [u'source quench']}


def ctx_tags(sents, j):
    win = u' '.join(sents[max(0, j - 1):j + 2])
    return [c for c in sorted(CTXKW) if any(k in win for k in CTXKW[c])]


ctx_rows = []
for i in range(NSRC):
    sa = sents_a(T[i])
    for j, s in enumerate(sa):
        if u'rate' in s and re.search(u'\\d', s):
            ctx_rows.append([LBL[i], s[:88], ctx_tags(sa, j)])
M['rate_sents'] = ctx_rows
ctxb = []
for i in range(NSRC):
    sb = sents_b(T[i])
    for j, s in enumerate(sb):
        if u'rate' in s and re.search(u'\\d', s):
            ctxb.append([LBL[i], s[:88], ctx_tags(sb, j)])
assert ctx_rows == ctxb, [(a, b) for a, b in zip(ctx_rows, ctxb) if a != b][:3]
assert len(ctx_rows) == len(ctxb)
M['rate_sents_n'] = [len([z for z in ctx_rows if z[0] == LBL[i]]) for i in range(NSRC)]
M['icmp_rate_sents'] = len([1 for z in ctx_rows
                            if u'icmp' in z[2] and u'source quench' not in z[2]
                            and u'arp' not in z[2] and u'ping_echo' not in z[2]])
print(u'7 含速率与数的句 %d 条(两轨同), 落 ICMP 差错话题 %d 条' % (len(ctx_rows),
                                                                M['icmp_rate_sents']))
for z in ctx_rows:
    print(u'   %s %s %s' % (z[0], z[2], z[1]))



# ---------- 8. sysctl 键表(先建, 供 §10 换算取默认值; Default 两轨读) ----------
KEYRE = re.compile(u'^([a-z0-9_/]+) - (INTEGER|BOOLEAN|STRING)\\s*$')
GROUPRE = re.compile(u'^\\s*([a-z0-9_/*]+):\\s*$')
keys, ktype, gkeys = {}, {}, {}
cur, prev_nb = None, u''
for x in L[5]:
    m = KEYRE.match(x)
    if m:
        cur = m.group(1)
        keys[cur] = u''
        ktype[cur] = m.group(2)
        g = GROUPRE.match(prev_nb)          # 紧邻上一非空行是目录头 => 挂全名
        if g:
            gkeys[g.group(1) + u'/' + cur] = cur
    else:
        if x.strip() != u'':
            prev_nb = x
        if cur is not None:
            keys[cur] += u' ' + x
M['sys_keys_total'] = len(keys)
ICMPK = sorted([k for k in keys if k.startswith(u'icmp_')])
M['sys_icmp_keys'] = ICMPK
M['sys_icmp_n'] = len(ICMPK)
M['sys_group_keys'] = sorted(gkeys)
assert M['sys_group_keys'] == [u'icmp/*/ratelimit'], M['sys_group_keys']


def dft_a(seg):
    """A 轨: 正则取 “Default: <token>”(整段一次搜索, 不切行; 冒号是门槛——'Defaults to 0' 不算)。"""
    m = re.search(u'Default:\\s*(\\S+)', seg)
    return m.group(1).strip(u'.') if m else None


def dft_b(seg):
    """B 轨: 游标逐次找 'Default', 须紧跟冒号, 否则跳到下一处(不经正则、不经 partition)。"""
    n = len(seg)
    k = seg.find(u'Default')
    while k >= 0:
        p = k + len(u'Default')
        if p < n and seg[p] == u':':
            p += 1
            while p < n and seg[p].isspace():
                p += 1
            j = p
            while j < n and not seg[j].isspace():
                j += 1
            if j > p:
                return seg[p:j].strip(u'.')
        k = seg.find(u'Default', k + 1)
    return None


tok_a, tok_b = {}, {}
for k in keys:
    tok_a[k] = dft_a(keys[k])
    tok_b[k] = dft_b(keys[k])
bad = sorted([k for k in keys if tok_a[k] != tok_b[k]])
assert bad == [], bad
M['sys_default_tokens'] = tok_a
M['sys_defaults_to'] = sorted([k for k in keys if u'Defaults to' in keys[k]
                               and tok_a[k] is None])
print(u'8b 只写 “Defaults to” 而无 “Default:” 行的键 %d 枚: %s'
      % (len(M['sys_defaults_to']), M['sys_defaults_to']))
RATEK = ICMPK + [gkeys[k] for k in sorted(gkeys)]
assert all(ktype[k] == u'INTEGER' for k in [u'icmp_ratelimit', u'icmp_msgs_per_sec',
                                            u'icmp_msgs_burst', u'ratelimit']), \
    dict((k, ktype.get(k)) for k in RATEK)


def dint(k):
    """默认值整数化: 只吃纯数字串, 否则停机(BOOLEAN 的 TRUE/FALSE 在此必炸)。"""
    t = tok_a[k]
    assert re.match(u'^-?[0-9]+$', t), (k, t)
    return int(t)


rl, mps, burst, rl6 = (dint(u'icmp_ratelimit'), dint(u'icmp_msgs_per_sec'),
                       dint(u'icmp_msgs_burst'), dint(u'ratelimit'))
print(u'8 键表: 全 %d 枚, icmp_* %d 枚 %s ⇎ 目录头挂名 %s ⇎ 速率键默认 %s'
      % (len(keys), len(ICMPK), ICMPK, M['sys_group_keys'],
         dict((k, tok_a[k]) for k in RATEK)))

# ---------- 9. ratemask 三轨换算(星号位定义表 ⇎ 逐位倍增 ⇎ 二串 Horner ⇎ 位标字母表) ----------
st = T[5]
mrow = re.search(u'Default mask:\\s+([01]{10,30}) \\((\\d+)\\)', st)
assert mrow, u'ratemask 行读不到'
maskbin, maskdec = mrow.group(1), int(mrow.group(2))
label = re.search(u'Significant bits: ([IHGFEDCBA9876543210]+)', st).group(1)
assert len(label) == len(maskbin), (len(label), len(maskbin))


def bitpos(ch):
    return ord(ch) - ord(u'A') + 10 if ch.isalpha() else int(ch, 16)


starred = []                                    # 甲轨: 游标扫位定义行的尾星号
for x in L[5]:
    s = x.strip()
    if len(s) > 3 and s[0] in u'0123456789ABCDEFGHI' and s[1] == u' ' and s.endswith(u'*'):
        starred.append(s[0])
star_bits = sorted(bitpos(c) for c in starred)
sum_pow = sum(2 ** bitpos(c) for c in starred)              # 甲轨: 闭式 2**b 求和
reg, cur2 = 0, 1                                            # 乙轨: 逐位倍增置位(不经 **)
for b in range(len(maskbin)):
    if b in star_bits:
        reg += cur2
    cur2 <<= 1
binval = 0                                                  # 丙轨: 二串逐字符 Horner
for ch in maskbin:
    binval = binval * 2 + int(ch)
lab_on = sorted(bitpos(label[j]) for j in range(len(maskbin)) if maskbin[j] == u'1')
assert sum_pow == reg == binval == maskdec, (sum_pow, reg, binval, maskdec)
assert lab_on == star_bits, (lab_on, star_bits)
M['mask_bits'] = star_bits
M['mask_stars'] = sorted(starred)
M['mask_bin_len'] = len(maskbin)
M['mask_bin'] = maskbin
M['mask_dec'] = maskdec
M['mask_label'] = label
print(u'9 ratemask: 星位 %s ⇎ 闭式和=%d ⇎ 倍增=%d ⇎ Horner=%d ⇎ 印 %d ⇎ 串长 %d ⇎ 位标 %s'
      % (star_bits, sum_pow, reg, binval, maskdec, len(maskbin), lab_on))

# ---------- 10. 换算等式(每个数从面里读, 每个结果两把尺) ----------
NUMWORD = {u'zero': 0, u'one': 1, u'two': 2, u'three': 3, u'four': 4, u'five': 5, u'six': 6,
           u'seven': 7, u'eight': 8, u'nine': 9, u'ten': 10}
UMULT = {u'k': 10 ** 3, u'M': 10 ** 6}      # 单位制常数(千/兆), 不是面读值
MS_PER_S = 10 ** 3                          # 秒⇎毫秒换算常数, 同上
eq = {}


def num(pat, face):
    g = re.findall(pat, face)
    assert len(g) == 1, (pat, g)
    return int(g[0].replace(u',', u''))


def fnum(pat, face):
    g = re.findall(pat, face)
    assert len(g) == 1, (pat, g)
    return float(g[0])


# (甲) 1009 的字节⇎包⇎线速现场
mbps = fnum(u'ds1 lines \\((\\d\\.\\d) mbps\\)', FOLD[1])
kbps = num(u'frequently (\\d+) kbps', FOLD[1])
avgb = num(u'the order of (\\d+) bytes', FOLD[1])
rate_pr = num(u'(\\d[\\d,]*) datagrams per second per interface', FOLD[1])
agg_pr = num(u'aggregate throughput of ([\\d,]+) datagrams', FOLD[1])
split_pr = num(u'would imply ([\\d,]+) datagrams', FOLD[1])
s_iface = [z for z in sents_a(T[1]) if u'ds1 lines and' in z and u'ethernet' in z]
assert len(s_iface) == 1, len(s_iface)
si = s_iface[0]
n_ds1 = num(u'supported (\\d+) ds1 lines', si)
n_eth = si.count(u'ethernet')
n_iface_calc = n_ds1 + n_eth
n_iface_print = agg_pr // rate_pr
assert n_iface_calc == n_iface_print, (n_iface_calc, n_iface_print)
acc_iface = 0                                               # 乙轨: 逐次加 rate_pr 共 n_iface 次
for _ in range(n_iface_calc):
    acc_iface += rate_pr
assert acc_iface == agg_pr, (acc_iface, agg_pr)
n_dir = split_pr // agg_pr
nd_sent = [z for z in sents_a(T[1]) if u'input and output' in z]
assert len(nd_sent) == 1, len(nd_sent)
n_dir_face = nd_sent[0].count(u'input') + nd_sent[0].count(u'output')
assert n_dir == n_dir_face, (n_dir, n_dir_face)
acc_dir = 0
for _ in range(n_dir):
    acc_dir += agg_pr
assert acc_dir == split_pr, (acc_dir, split_pr)
# 位/字节: 1812 “(20 bytes = 5 words)” ⇎ 4443 “exactly 32 bits”
assert len(set(re.findall(u'\\((\\d+) bytes = (\\d+) words\\)', FOLD[3]))) == 1
m20 = re.search(u'\\((\\d+) bytes = (\\d+) words\\)', FOLD[3])
ip20, ipw = int(m20.group(1)), int(m20.group(2))
oct32 = num(u'exactly (\\d+) bits of type-specific data', FOLD[4])
assert ip20 % ipw == 0, (ip20, ipw)
bytes_per_word = ip20 // ipw
bits_per_byte = oct32 // bytes_per_word
assert bits_per_byte * bytes_per_word == oct32, (bits_per_byte, bytes_per_word, oct32)
# 线速推包速: 甲轨闭式除法, 乙轨逐次减法(须整除无余)
bps_line = int(mbps * UMULT[u'M'])
per_pkt_bits = avgb * bits_per_byte
rate_calc = bps_line / per_pkt_bits
rem, q = bps_line, 0
while rem >= per_pkt_bits:
    rem -= per_pkt_bits
    q += 1
assert q == rate_calc and rem == 0, (q, rate_calc, rem)
eq['mbps'] = mbps
eq['kbps'] = kbps
eq['avgb'] = avgb
eq['bytes_per_word'] = bytes_per_word
eq['bits_per_byte'] = bits_per_byte
eq['rate_calc'] = rate_calc
eq['rate_calc_sub'] = q
eq['rate_printed'] = rate_pr
eq['rate_gap'] = rate_pr - rate_calc
eq['n_ds1'] = n_ds1
eq['n_eth'] = n_eth
eq['n_iface_calc'] = n_iface_calc
eq['n_iface_print'] = n_iface_print
eq['agg_printed'] = agg_pr
eq['agg_from_iface'] = acc_iface
eq['n_dir'] = n_dir
eq['n_dir_face'] = n_dir_face
eq['split_printed'] = split_pr
eq['split_from_dir'] = acc_dir
# (乙) 内核四数: 每目标最小间隔 ⇎ 全局每秒 ⇎ 突发
eq['rl_ms'] = rl
eq['rl_per_s'] = MS_PER_S / rl
eq['per_sec'] = mps
eq['burst'] = burst
eq['ratio_global_vs_target'] = mps / (MS_PER_S / rl)
eq['per_burst'] = mps / burst
eq['rl6_ms'] = rl6
eq['rl6_vs_v4'] = rl6 / rl
# (丙) 4443 的示例默认 B=10, N=10/s 放到内核尺上
b44 = num(u'could be b=(\\d+)', FOLD[4])
n44 = num(u'n=(\\d+)/s', FOLD[4])
eq['b4443'] = b44
eq['n4443'] = n44
eq['n44_vs_kernel_per_sec'] = mps / n44
eq['n44_vs_kernel_per_target'] = n44 / (MS_PER_S / rl)
eq['burst_vs_b4443'] = burst / b44
p576 = num(u'exceeding (\\d+) bytes', FOLD[3])
eq['p576'] = p576
eq['bytes_per_s_4443'] = p576 * n44
eq['bits_per_s_4443'] = p576 * n44 * bits_per_byte
# (丁) 1122 的 0.005/s(网关 ping, 不是差错报文)与 1812 的时间戳钟
hz = fnum(u'e\\.g\\., (0\\.\\d+) per second', FOLD[2])
eq['hz_005'] = hz
eq['period_200'] = 1 / hz
m50 = re.search(u'(\\d+) or (\\d+) times per second', FOLD[3])
assert m50, u'市电频率句读不到'
f50, f60 = int(m50.group(1)), int(m50.group(2))
l16 = num(u'updated at least (\\d+) times per second', FOLD[3])
msix = NUMWORD[re.search(u'at most the (\\w+) low-order bits', FOLD[3]).group(1)]
two6 = 1
for _ in range(msix):                                       # 乙轨: 逐次左移
    two6 <<= 1
low63, step3 = 0, 1
for _ in range(msix):                                       # 丙轨: 逐位累加(2**b-1)
    low63 += step3
    step3 <<= 1
assert low63 + 1 == two6 == 2 ** msix, (low63, two6, msix)
eq['hz_mains'] = [f50, f60]
eq['ts_min_per_s'] = l16
eq['ts_bits'] = msix
eq['ts_states'] = two6
eq['ts_states_pow'] = 2 ** msix
eq['ts_low_bits_mask'] = low63
eq['ts_margin_50_over_16'] = f50 // l16
eq['ts_wrap_s'] = two6 // f50
# (戊) 各源有几枚 “数×速率单位”? 792 应为零
RATEU = [u'per second', u'datagrams per second', u'packets/second', u'/s', u'times per second']
M['rate_pairs_per_src'] = [len([p for p in M['pairs_a'][i] if p[1] in RATEU])
                           for i in range(NSRC)]
assert M['rate_pairs_per_src'][0] == 0, M['rate_pairs_per_src']
eq['n_rate_pairs_792'] = M['rate_pairs_per_src'][0]
eq['n_rate_pairs_1122'] = M['rate_pairs_per_src'][2]
eq['n_rate_pairs_sys'] = M['rate_pairs_per_src'][5]
M['eq'] = dict(eq)
print(u'10 等式: ' + json.dumps(dict((k, str(v)) for k, v in eq.items()), ensure_ascii=False))

# ---------- 11. 块定界两轨(正则锚行 ⇎ 折面偏移回行; 目录点线为门槛) ----------
def blk_re(i, hdr_pat, stop_pat):
    a = next(k for k, x in enumerate(L[i]) if re.search(hdr_pat, x))
    b = next(k for k in range(a + 1, len(L[i])) if re.search(stop_pat, L[i][k]))
    return a, b


def find_noleader(s, q, frm=0):
    """B 轨: 折面游标找针, 凡后随(去空白后)两点者弃之——目录点线不算正文。"""
    k = s.find(q, frm)
    while k >= 0:
        if s[k + len(q):k + len(q) + 8].lstrip().startswith(u'..'):
            k = s.find(q, k + 1)
            continue
        return k
    return -1


def blk_fold(i, qa, qb):
    fa = find_noleader(SHP[i], qa)
    assert fa >= 0, (i, qa)
    fb = find_noleader(SHP[i], qb, fa + len(qa))
    assert fb >= 0, (i, qb)
    assert shp_to_rawoff(i, fa) < shp_to_rawoff(i, fb)
    return fold_line(i, fa), fold_line(i, fb)


BLKS = [(1, u'^\\s*2\\.2\\.3\\.\\s+Source Quench\\s*$', u'^\\s*2\\.2\\.4\\.\\s+Time Exceeded\\s*$',
         u'2.2.3. source quench', u'2.2.4. time exceeded'),
        (3, u'^4\\.3\\.2\\.8 Rate Limiting', u'^4\\.3\\.3 SPECIFIC',
         u'4.3.2.8 rate limiting', u'4.3.3 specific issues'),
        (4, u'^\\s*\\(f\\) Finally', u'^\\s*NOTE: THE RESTRICTIONS',
         u'(f) finally, in order to limit the bandwidth', u'note: the restrictions under')]
OB2 = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']
blk_out = []
for (i, pa_, pb_, na, nb) in BLKS:
    a1, b1 = blk_re(i, pa_, pb_)
    a2, b2 = blk_fold(i, pnorm(na), pnorm(nb))
    ca = NL.join(L[i][a1:b1])
    cb = NL.join(L[i][a2:b2])
    assert a1 == a2 and b1 == b2, (na, a1, a2, b1, b2)
    assert ca == cb, (na, len(ca), len(cb))
    oa = [a_ub(ca.upper(), w) for w in OB2]
    ob = [ob_b(ca, w) for w in OB2]
    assert oa == ob, (na, oa, ob)
    blk_out.append([LBL[i], a1, b1 - a1, len(ca), oa, sum(oa),
                    [b_ub(ca, w) for w in [u'MUST', u'SHOULD', u'MAY']]])
M['blocks'] = blk_out
M['blocks_oblabels'] = OB2
print(u'11 块定界:', [(z[0], z[1], z[2], z[3]) for z in blk_out], u' 义务词:',
      [z[4] for z in blk_out])

# ---------- 12. 集合档⇎词频档(子串存在 ⇎ n 元词 histogram; 标点口径另记) ----------
FAMW = [u'burst', u'configurable', u'settable', u'throttle', u'ratelimit', u'bandwidth',
        u'milliseconds', u'millseconds', u'dropped', u'discard']
FAMP = [u'source quench', u'source quenches', u'token bucket', u'timer-based', u'token-bucket',
        u'rate-limiting', u'rate limiting', u'rate limit', u'icmp error', u'icmp errors',
        u'icmpv6 error', u'destination unreachable', u'time exceeded', u'parameter problem',
        u'limit the rate', u'limit the frequency', u'per second', u'dropped datagrams',
        u'dropped packets', u'specific targets', u'low-order bits']
FAM = list(dict.fromkeys(FAMW + FAMP))
TOK = [FOLD[i].split(u' ') for i in range(NSRC)]
TOKS = [[w.strip(u'.,;:!?"\'()') for w in z] for z in TOK]      # 剥标点档
hist, hist_s = [], []
for i in range(NSRC):
    for store, src in ((hist, TOK[i]), (hist_s, TOKS[i])):
        h = {}
        for n in range(1, 5):
            h[n] = Counter(zip(*[src[k:] for k in range(n)]))
        store.append(h)


def ng(h, p):
    parts = tuple(p.split(u' '))
    return h[len(parts)][parts]


RXW = {}


def sub_word(s, p):
    """A 轨: 子串游标数(不带词界, 前缀式全收)。"""
    return a_cnt(s, p)


def sub_bnd(s, p):
    """A' 轨: 带词界的子串数(两头不许贴字母)。"""
    if p not in RXW:
        RXW[p] = re.compile(u'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(p))
    return len(RXW[p].findall(s))


freq_raw = [[ng(hist[i], p) for p in FAM] for i in range(NSRC)]
freq_strip = [[ng(hist_s[i], p) for p in FAM] for i in range(NSRC)]
freq_bnd = [[sub_bnd(FOLD[i], p) for p in FAM] for i in range(NSRC)]
freq_sub = [[sub_word(FOLD[i], p) for p in FAM] for i in range(NSRC)]
for i in range(NSRC):
    for k, p in enumerate(FAM):
        assert (freq_strip[i][k] > 0) == (freq_bnd[i][k] > 0), (LBL[i], p,
                                                                freq_strip[i][k], freq_bnd[i][k])
M['fams'] = FAM
M['fams_n_types'] = len(FAM)
M['fams_present'] = [[1 if freq_bnd[i][k] > 0 else 0 for k in range(len(FAM))]
                     for i in range(NSRC)]
M['fams_freq'] = freq_strip
M['fams_freq_sub'] = freq_sub
M['fams_punct_tax'] = [[freq_bnd[i][k] - freq_raw[i][k] for k in range(len(FAM))]
                       for i in range(NSRC)]
M['fams_prefix_tax'] = [[freq_sub[i][k] - freq_bnd[i][k] for k in range(len(FAM))]
                        for i in range(NSRC)]
M['fams_word_vs_sub'] = [[b_ub(FOLD[i], w) - sum(1 for t in TOKS[i] if t == w) for w in FAMW]
                         for i in range(NSRC)]
for i in range(NSRC):
    assert all(z >= 0 for z in M['fams_word_vs_sub'][i]), (LBL[i], M['fams_word_vs_sub'][i])
    assert all(z >= 0 for z in M['fams_prefix_tax'][i]), (LBL[i], M['fams_prefix_tax'][i])
    assert all(z >= 0 for z in M['fams_punct_tax'][i]), (LBL[i], M['fams_punct_tax'][i])
M['fams_n_per_src'] = [sum(M['fams_present'][i]) for i in range(NSRC)]
M['fams_excl'] = [[p for k, p in enumerate(FAM)
                   if M['fams_present'][i][k] and all(M['fams_present'][j][k] == 0
                                                      for j in range(NSRC) if j != i)]
                  for i in range(NSRC)]
print(u'12 语形族 %d 式: 各源出现式种 %s ⇎ 独占 %s' % (len(FAM), M['fams_n_per_src'],
                                                  M['fams_excl']))
print(u'   税账: 标点税 %d ⇎ 前缀税 %d(子串尺多收) ⇎ 词形税 %d'
      % (sum(sum(z) for z in M['fams_punct_tax']),
         sum(sum(z) for z in M['fams_prefix_tax']),
         sum(sum(z) for z in M['fams_word_vs_sub'])))

# ---------- 13. 针多解与落点行 ----------
multi = []
for k, nd in enumerate(NEEDLES):
    q = pnorm(nd)
    for i in range(NSRC):
        if rows3[k][i][2] > 0:
            occ = b_cnt_ovl(SHP[i], q)
            if occ > 1:
                multi.append([LBL[i], k, occ])
M['multi_hits'] = multi
M['pin_by_src'] = [len([z for z in M['pin_lines'] if z[0] == LBL[i]]) for i in range(NSRC)]
print(u'13 同面多解针格 %d: %s' % (len(multi), multi))

M['nsrc'] = NSRC
M['labels'] = LBL
M['paths'] = SRC
M['needle_n'] = NN
RECON['needle'] = NN * NSRC * 2
RECON['sents'] = sum(M['sents_n'])
RECON['ob'] = NSRC * len(OB)
RECON['pairs'] = sum(len(x) for x in M['pairs_a'])
RECON['default'] = len(keys)
RECON['mask'] = 4
RECON['block'] = len(BLKS) * 3
RECON['fam'] = len(FAM) * NSRC
RECON['eq'] = len([z for z in ('rate_calc', 'agg_printed', 'split_printed', 'ts_states')])
M['recon'] = dict((k, int(v)) for k, v in RECON.items())
M['recon_groups'] = len(M['recon'])
M['recon_cells'] = sum(M['recon'].values())
M['recon_face_ok'] = 1 if M['bytes'] == M['bytes_stat'] else 0
json.dump(M, io.open(u'corpus/_b94meas.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
print(u'采集遍落 corpus/_b94meas.json ｜ 键 %d ｜ 双轨对账 %d 组全符' % (len(M), len(RECON)))
