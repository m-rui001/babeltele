# -*- coding: utf-8 -*-
"""采集遍(B82, 第一套实现): “一条空闲连接多久该关掉”由五份一手文书各答一遍
1122(1981/1989 TCP 需求) ⇎ 9293(2022 TCP 规范) ⇎ 9112(2021 HTTP/1.1) ⇎ 9113(2022 HTTP/2) ⇎ 9000(2021 QUIC)。
五份都是 RFC Editor txt(同一序列化家族), 壳账与档位在本遍实测后写死。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'1122', u'9293', u'9112', u'9113', u'9000']
SRC = [u'corpus/raw/tcpRTO/rfc1122.txt', u'corpus/raw/tcpTW/rfc9293.txt',
       u'corpus/raw/httpKA/rfc9112.txt', u'corpus/raw/idle/rfc9113.txt',
       u'corpus/raw/idle/rfc9000.txt']
YR = [1981, 2022, 2021, 2022, 2021]
NSRC = 5
M = {}


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in SRC]
T = [b.decode('utf-8', 'replace') for b in B]
RAWL = [t.split(NL) for t in T]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]


def pnorm(s):
    return u' '.join(s.lower().split())


def fold(s):
    return u' '.join([c for c in re.split(u'\\s', s) if c != u''])


def cnt_cur(hay, nd):
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def ub(s, w, kind=u'alpha'):
    """词界尺: 两侧都不是字母(alpha) ⇎ 都不是数字(digit) ⇎ 都不是字母数字(alnum)。"""
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if kind == u'alpha':
            ok = not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha())
        elif kind == u'digit':
            ok = not (a >= 0 and s[a].isdigit()) and not (b < len(s) and s[b].isdigit())
        else:
            ok = not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())
        if ok:
            c += 1
        i = j + 1


# ---------- 0. 面量 ----------
M['bytes'] = [len(B[i]) for i in range(NSRC)]
M['n_lf'] = [cnt_cur(T[i], NL) for i in range(NSRC)]
M['n_cr'] = [cnt_cur(T[i], u'\r') for i in range(NSRC)]
M['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
M['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
M['ff'] = [cnt_cur(T[i], u'\x0c') for i in range(NSRC)]
M['ff_led'] = [len([x for x in L[i] if len(x) and ord(x[0]) == 12]) for i in range(NSRC)]
M['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
M['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
M['nonascii'] = [sorted(set([ord(c) for c in T[i] if ord(c) > 127])) for i in range(NSRC)]
print(u'0 面量:', json.dumps(dict((k, M[k]) for k in
      ['bytes', 'n_lf', 'n_cr', 'splitlines', 'splitnl', 'ff', 'ff_led', 'blank', 'maxlen'])))
print(u'  非ASCII码位:', M['nonascii'])

# ---------- 1. 壳形: 两代 RFC Editor 页眉页脚 ----------
RX_PG = [len([x for x in L[i] if re.search(u'\\[Page \\d+\\]', x)]) for i in range(NSRC)]
RX_HDR = [len([x for x in L[i] if re.match(u'^RFC \\d{4} +\\S.*((19|20)\\d\\d)\\s*$', x)]) for i in range(NSRC)]
M['pg_foot'] = RX_PG
M['hdr_rfc_year'] = RX_HDR
# 页码独立成行(只由空白与数字组成, 数字恰一段)
def digit_runs(x):
    n, prev = 0, False
    for c in x:
        cur = c.isdigit()
        if cur and not prev:
            n += 1
        prev = cur
    return n


M['pgnum'] = [len([x for x in L[i] if not [c for c in x if not (c.isdigit() or c.isspace())]
                  and digit_runs(x) == 1]) for i in range(NSRC)]
# 每份的页壳样本
for i in range(NSRC):
    smp = [x for x in L[i] if re.search(u'\\[Page \\d+\\]', x)][:2]
    hdr = [x for x in L[i] if re.match(u'^RFC \\d{4} ', x)][:2]
    print(u'1 %s 页脚样本 %r 眉行样本 %r' % (LBL[i], smp, hdr))
print(u'  [Page计数]', M['pg_foot'], u' 眉行计数', M['hdr_rfc_year'], u' 独立页码行', M['pgnum'])

# ---------- 2. 拼写族 ----------
GRP = [u'keep-alive', u'keepalive', u'keep alive', u'keeps alive', u'keep-alives',
       u'idle', u'idle timeout', u'inactive', u'persistent', u'acknowledgement',
       u'acknowledgment', u'implementors', u'implementers', u'two hours', u'time out']
M['spell'] = [[cnt_cur(pnorm(T[i]), p) for p in GRP] for i in range(NSRC)]
print(u'2 拼写族(整篇折平小写):')
for k, p in enumerate(GRP):
    print(u'   %-14s %s' % (p, [M['spell'][i][k] for i in range(NSRC)]))

# ---------- 3. 义务词与编号 ----------
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']
M['ob_line'] = [[sum([ub(x, w) for x in L[i]]) for w in OB] for i in range(NSRC)]
M['ob_fold'] = [[ub(fold(T[i]), w) for w in OB] for i in range(NSRC)]
M['ob_wrap'] = [M['ob_fold'][i][k] - M['ob_line'][i][k] for i in range(NSRC) for k in range(len(OB))]
TAG = re.compile(u'\\((MUST|SHOULD|MAY|SHLD|ED) \\d+\\)|(MUST|SHOULD|MAY|SHLD)-\\d+')
M['tag_paren'] = [len(re.findall(u'\\((MUST|SHOULD|MAY|SHLD|ED) \\d+\\)', T[i])) for i in range(NSRC)]
M['tag_dash'] = [len(re.findall(u'\\b(MUST|SHOULD|MAY|SHLD)-\\d+\\b', T[i])) for i in range(NSRC)]
print(u'3 义务词 逐行:', M['ob_line'])
print(u'  义务词 折平:', M['ob_fold'])
print(u'  跨行涨量(折-行):', [M['ob_fold'][i][k] - M['ob_line'][i][k] for i in range(NSRC) for k in range(5)])
print(u'  (MUST 27) 括号形:', M['tag_paren'], u' MUST-27 横杠形:', M['tag_dash'])

# ---------- 4. 时长语形 ----------
DUR = [u'two hours', u'no less than two hours', u'120 minutes', u'three times',
       u'3 times', u'milliseconds', u' ms', u'second', u'Timeout', u'timeout']
M['dur'] = [[cnt_cur(pnorm(T[i]).replace(u' 3 times', u' 3 times'), d.lower()) for d in DUR] for i in range(NSRC)]
print(u'4 时长语形(整篇折平小写子串):')
for k, d in enumerate(DUR):
    print(u'   %-24s %s' % (d, [M['dur'][i][k] for i in range(NSRC)]))
# 数字+单位对
RXU = re.compile(u'(?<![A-Za-z0-9.])(\\d+(?:[.,]\\d+)?)[ ]?(milliseconds|microseconds|seconds|ms|s)(?![A-Za-z])')
pairs = [sorted(set([tuple(x) for x in RXU.findall(T[i])])) for i in range(NSRC)]
M['numunit'] = [[list(z) for z in p] for p in pairs]
print(u'  数字×单位对:', pairs)

# ---------- 5. 判词针候选: 三档面(逐行 ⇎ 全篇折平 ⇎ 摘壳折平) ----------
def is_shell(x, i):
    return (re.search(u'\\[Page \\d+\\]', x) is not None
            or re.match(u'^RFC \\d{4} +\\S.*((19|20)\\d\\d)\\s*$', x) is not None
            or x.strip() == u'')


SHF = [pnorm(NL.join([x for x in L[i] if not is_shell(x, i)])) for i in range(NSRC)]
FOL = [pnorm(T[i]) for i in range(NSRC)]
LIN = [L[i] for i in range(NSRC)]
NEEDLES = [
    u'they MUST default to off',                                   # 1122/9293 同款
    u'MUST default to no less than two hours',                     # 两代同句(跨行)
    u'no less than two hours',
    u'interval MUST be configurable',
    u'is said to be "idle"',
    u'no incoming segments received',
    u'to confirm that an idle connection is still active',
    u'MUST NOT interpret failure to respond',
    u'a dead connection',
    u'no requirements on the length (or existence) of this timeout',
    u'Servers will usually have some timeout value',
    u'Connections can be closed at any time',
    u'at any time',
    u'issue a graceful close',
    u'encouraged to maintain open connections for as long as possible',
    u'permitted to terminate idle connections',
    u'SHOULD first send a GOAWAY',
    u'the terminating endpoint',
    u'a value of zero',
    u'max_idle_timeout',
    u'the minimum of the two advertised values',
    u'sole advertised value',
    u'MUST increase the idle timeout period',
    u'at least three times the current Probe Timeout',
    u'current Probe Timeout (PTO)',
    u'excessively small idle timeout periods',
    u'Liveness Testing',
    u'SETTINGS_TIMEOUT',
    u'connection for liveness',
    u'silent',
]
print(u'5 判词针三档:')
rows = []
for nd in NEEDLES:
    q = pnorm(nd)
    r = []
    for i in range(NSRC):
        cl = len([x for x in LIN[i] if q in pnorm(x)])
        cf = cnt_cur(FOL[i], q)
        cs = cnt_cur(SHF[i], q)
        r.append((cl, cf, cs))
    rows.append((nd, r))
    hit = [LBL[i] for i in range(NSRC) if r[i][2] > 0]
    print(u'   %-58s %s  摘壳命中=%s' % (nd, r, hit))
M['needles3'] = [[list(z) for z in [r[i] for i in range(NSRC)]] for nd, r in rows]

# ---------- 6. 关键句行号定位(供锚) ----------
print(u'6 关键句行号定位(供锚):')
PINL = []
for nd in [u'no less than two hours', u'is said to be', u'no requirements on the length',
           u'permitted to terminate idle', u'the minimum of the two advertised',
           u'at least three times', u'MUST default to off']:
    for i in range(NSRC):
        qs = [k for k, x in enumerate(L[i]) if pnorm(nd) in pnorm(x)]
        if qs:
            PINL.append([LBL[i], nd, qs[0], len(qs)])
            print(u'6 %s «%s» 行号 %s' % (LBL[i], nd, qs))
M['pin_lines'] = PINL

# ---------- 7. 节标题 ----------
for i in range(NSRC):
    for k, x in enumerate(L[i]):
        if re.match(u'^\\d+(\\.\\d+)*\\.? +.*([Kk]eep|[Ii]dle|[Tt]imeout|[Ff]ailur)', x) and len(x.strip()) > 5:
            print(u'7 %s L%d %r' % (LBL[i], k, x))

json.dump(M, io.open(u'corpus/_tmp82pick.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'已落 corpus/_tmp82pick.json')

# ---------- 8. 壳账(修正后的谓词) ----------
def foot(x):
    return re.search(u'\[Page \d+\]', x) is not None


def hdr1122(x):
    return re.match(u'^RFC1122 +\S', x) is not None


def ffline(x):
    return x == u'\x0c'


FFNL = [len(re.findall(u'(?=\x0c' + NL + u')', T[i])) for i in range(NSRC)]
FFEOF = [1 if T[i][-1:] == u'\x0c' else 0 for i in range(NSRC)]
TRAILNL = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
M['ff_before_nl'] = FFNL
M['ff_at_eof'] = FFEOF
M['trailing_nl'] = TRAILNL
print(u'8 FF后随换行:', FFNL, u' FF在文尾:', FFEOF, u' 尾换行:', TRAILNL)
PRE = [FFNL[i] - TRAILNL[i] for i in range(NSRC)]
OBS = [M['splitlines'][i] - M['splitnl'][i] for i in range(NSRC)]
print(u'  行式对账(splitlines−splitnl):', OBS, u' 预测(FF后随换行−尾换行):', PRE)
assert OBS == PRE, u'行式对账不平'
SHELL_OLD = [foot(x) or hdr1122(x) or ffline(x) or x.strip() == u'' for x in L[0]]
SHELL_NEW = [[x.strip() == u'' for x in L[i]] for i in range(1, NSRC)]
M['shell_lines'] = [len([1 for x in SHELL_OLD if x])] + [len([1 for y in SHELL_NEW[i - 1] if y]) for i in range(1, NSRC)]
M['foot'] = [len([x for x in L[i] if foot(x)]) for i in range(NSRC)]
M['hdr_old'] = [len([x for x in L[i] if hdr1122(x)]) for i in range(NSRC)]
M['ff_alone'] = [len([x for x in L[i] if ffline(x)]) for i in range(NSRC)]
M['bom'] = [1 if L[i][0] == u'\ufeff' else 0 for i in range(NSRC)]
print(u'  壳行:', M['shell_lines'], u' 页脚:', M['foot'], u' 眉行:', M['hdr_old'],
      u' FF独占:', M['ff_alone'], u' BOM首行:', M['bom'])

# ---------- 9. 两段保活节的逐句对照(1122 §4.2.3.6 ⇎ 9293 §3.8.4) ----------
def blk(i, a, b):
    return NL.join(L[i][a:b])


B1122 = [k for k, x in enumerate(L[0]) if re.match(u'^\\s*4\\.2\\.3\\.6 +TCP Keep-Alives', x)][-1:]
B9293 = [k for k, x in enumerate(L[1]) if re.match(u'^3\\.8\\.4\\.', x) or re.match(u'^3\\.8\\.5\\.', x)]
print(u'9 节题行号 1122:', B1122, u' 9293:', B9293)
E1 = [k for k in range(B1122[0] + 1, len(L[0])) if re.match(u'^\\s+4\\.2\\.3\\.7 +', L[0][k])]
BODY1 = L[0][B1122[0] + 1:E1[0]]
DIS = [k for k, x in enumerate(BODY1) if x.strip() == u'DISCUSSION:']
SPECK = BODY1[:DIS[0]] if DIS else BODY1
SPECK_SH = [x for x in SPECK if not (foot(x) or hdr1122(x) or ffline(x) or x.strip() == u'')]
s1 = [pnorm(z) for z in re.split(u'(?<=[.!?]) +', pnorm(NL.join(SPECK))) if z]
s2 = [pnorm(z) for z in re.split(u'(?<=[.!?]) +', pnorm(blk(1, B9293[0] + 1, B9293[1]))) if z]
TAGRE = re.compile(u' \\((?:MUST|SHOULD|MAY|SHLD|ED)-\\d+\\)', re.I)
s2c = [TAGRE.sub(u'', z).strip() for z in s2]
SHIN = len([x for x in SPECK if foot(x) or hdr1122(x) or ffline(x)])
print(u'  1122规格块行数', len(SPECK), u' 其中壳行', SHIN, u' 摘壳后', len(SPECK_SH))
def canon(z):
    return z.replace(u'implementers', u'implementors').replace(u'acknowledgment', u'acknowledgement')
shared = [z for z in s2c if z in s1]
shared2 = [z for z in s2c if canon(z) in [canon(y) for y in s1]]
print(u'  1122块句数', len(s1), u' 9293块句数', len(s2),
      u' 去编号后逐句全等', len(shared), u' 再拼写归一后全等', len(shared2))
for z in s2:
    zc = TAGRE.sub(u'', z).strip()
    print(u'   [%s] %s' % (u'同' if zc in s1 else (u'拼' if canon(zc) in [canon(y) for y in s1] else u'新'), z[:96]))
M['ovl_s1'], M['ovl_s2'], M['ovl_same'], M['ovl_same2'], M['ovl_shell_in_block'] = len(s1), len(s2), len(shared), len(shared2), SHIN

# ---------- 10. 追加判词针三档 ----------
NEEDLES2 = [u'Idle timeout is disabled', u'specify a value of 0', u'connection is silently closed',
            u'abandons the connection', u'restarts its idle timer', u'Deferring Idle Timeout',
            u'sent a SETTINGS frame but did not receive', u'in a timely manner',
            u'idle connection is still functional', u'no longer maintain an inactive connection',
            u'Proxy servers might make this a higher value', u'MAY close the transport connection',
            u'received closure signal', u'to elicit a response', u'SEG.SEQ = SND.NXT-1',
            u'one garbage octet', u'issue a graceful close', u'reclaimed',
            u'Timeouts', u'Settings Synchronization']
print(u'10 追加判词针:')
ROWS2 = []
for nd in NEEDLES2:
    q = pnorm(nd)
    r = []
    for i in range(NSRC):
        cl = len([x for x in L[i] if q in pnorm(x)])
        cf = cnt_cur(FOL[i], q)
        sh = u'\x0c' if False else None
        shf = pnorm(NL.join([x for x in L[i]
                             if not (foot(x) or hdr1122(x) or ffline(x) or x.strip() == u'')])) if i == 0 else FOL[i]
        cs = cnt_cur(shf, q)
        r.append((cl, cf, cs))
    ROWS2.append((nd, r))
    hit = [LBL[i] for i in range(NSRC) if r[i][2] > 0]
    print(u'   %-46s %s  %s' % (nd, r, hit))
M['needles3b'] = [[list(z) for z in [r[i] for i in range(NSRC)]] for nd, r in ROWS2]

# ---------- 11. 十六进制形与编号形 ----------
M['hexes'] = [len(re.findall(u'(?<![0-9A-Za-z])0x[0-9A-Fa-f]{2}(?![0-9A-Za-z])', T[i])) for i in range(NSRC)]
M['sec_refs'] = [len(re.findall(u'Section \d', T[i])) for i in range(NSRC)]
print(u'11 十六进制码位:', M['hexes'], u' Section N 引用:', M['sec_refs'])

# ---------- 12. 收口: 全量重落 ----------
json.dump(M, io.open(u'corpus/_b82meas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print(u'已落 corpus/_b82meas.json ｜ 键 %d' % len(M))
