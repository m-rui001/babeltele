# -*- coding: utf-8 -*-
"""采集遍(B86, 第一套实现): “RTO 重传几次/多久之后放弃”由五份一手文书各答一遍
793(1981 TCP 规范: 事件表把 RTO 超时写成无条件循环, 全文没有任何阈值) ⇎ 1122(1989 主机需求: 引入 R1/R2 双阈值,
且声明两把尺可任选) ⇎ 9293(2022 STD 1: 逐句重印 1122 那段并挂 MUST-n/SHLD-n 编号, 同时原样保留 793 的无限循环,
另在 SEND 调用里给 “five minutes”) ⇎ 6298(2011 RTO 计算: 只封顶单次超时 at least 60 seconds, 不谈总放弃)
⇎ Linux ip-sysctl.txt(实现文档: 把 R1/R2 落成 tcp_retries1=3 ⇎ tcp_retries2=15, 并给 (N, N+1) 错位口径、
924.6 秒的 hypothetical timeout、syn_retries 6→63→127 的可复算等式, 以及 SCTP 那一组纯次数阈值)。

五份不是同一序列化家族: 793 ⇎ 1122 是旧 RFC Editor 页壳(眉行带年份 ⇎ [Page n] 独立行), 9293 ⇎ 6298 是新式页壳
(无 [Page 字样? 待实测), ip-sysctl.txt 是键值表(`^\\w+ - (INTEGER|BOOLEAN)` ⇎ `Default:` 行)。壳账在本遍实测后写死。
所有正文数字由本遍量出后落 JSON, 一枚都不手打。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'793', u'1122', u'9293', u'6298', u'lin']
SRC = [u'corpus/raw/tcpRetr/rfc793.txt', u'corpus/raw/tcpRetr/rfc1122.txt',
       u'corpus/raw/tcpRetr/rfc9293.txt', u'corpus/raw/tcpRetr/rfc6298.txt',
       u'corpus/raw/tcpRetr/ip-sysctl.txt']
YR = [1981, 1989, 2022, 2011, 2026]
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


def foldmap(txt):
    """折平面 + (面偏移 → 原行) 区间表: 只数非空格字符, 段间一枚空格。"""
    lines = txt.split(NL)
    offs, pos, seg = [], 0, []
    for i, l in enumerate(lines):
        c = pnorm(l)
        if not c:
            continue
        offs.append((pos, pos + len(c), i))
        seg.append(c)
        pos += len(c) + 1
    face = u' '.join(seg)
    assert len(face) == (pos - 1 if pos else 0), (len(face), pos)
    return face, offs


def line_of_face(offs, s0):
    cand = [o[2] for o in offs if o[0] <= s0]
    return cand[-1] if cand else None


def find_line(i, nd):
    """折平 needle → needle 起点所在行(0-based): needle 可能跨行, 4 行滑窗在折平面上试,
       返回的是 needle 首字符所在的原行, 不是窗口起始行。"""
    q = pnorm(nd)
    head = q[:min(16, len(q))]
    for a in range(len(L[i])):
        win = NL.join(L[i][a:a + 4])
        pw = pnorm(win)
        if head not in pw:
            continue
        face, offs = foldmap(win)
        s0 = face.find(q)
        if s0 >= 0:
            return a + line_of_face(offs, s0)
    return -1


def digit_runs(x):
    n, prev = 0, False
    for c in x:
        cur = c.isdigit()
        if cur and not prev:
            n += 1
        prev = cur
    return n


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
M['bom'] = [1 if T[i][:1] == u'﻿' else 0 for i in range(NSRC)]
M['tab'] = [cnt_cur(T[i], u'\t') for i in range(NSRC)]
print(u'0 面量:', json.dumps(dict((k, M[k]) for k in
      ['bytes', 'n_lf', 'n_cr', 'splitlines', 'splitnl', 'ff', 'ff_led', 'blank', 'maxlen', 'bom', 'tab'])))
print(u'  非ASCII码位:', M['nonascii'])
FFNL = [len(re.findall(u'(?=\x0c' + NL + u')', T[i])) for i in range(NSRC)]
FFEOF = [1 if T[i][-1:] == u'\x0c' else 0 for i in range(NSRC)]
TRAILNL = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
M['ff_before_nl'], M['ff_at_eof'], M['trailing_nl'] = FFNL, FFEOF, TRAILNL
OBS = [M['splitlines'][i] - M['splitnl'][i] for i in range(NSRC)]
PRE = [FFNL[i] - TRAILNL[i] for i in range(NSRC)]
print(u'  行式对账 splitlines−splitnl =', OBS, u' 预测 FF后随换行−尾换行 =', PRE)
assert OBS == PRE, u'行式对账不平'

# ---------- 1. 壳形: 三种序列化家族 ----------
def foot(x):
    return re.search(u'\\[Page \\d+\\]', x) is not None


def hdr_793(x):
    return re.match(u'^\\s*(September 1981|Transmission Control Protocol)\\s*$', x) is not None


def hdr_1122(x):
    return re.match(u'^RFC1122 +\\S', x) is not None


def ietf_line(x):
    return re.match(u'^Internet Engineering Task Force\\s*$', x) is not None


def hdr_new(x):
    """新式页壳(9293/6298): 眉/脚是“作者/状态 + RFC 号 + 月份年”的一行。"""
    return re.search(u'RFC ?\\d{4}[^A-Za-z0-9]+.*((19|20)\\d\\d)\\s*$', x) is not None or \
        re.match(u'^\\s*(Internet Engineering Task Force|Internet-Draft)', x) is not None


def keylin(x):
    return re.match(u'^[a-z_][a-z_0-9]* - (INTEGER|BOOLEAN|STRING|DWORD)\\s*$', x) is not None


M['foot_page'] = [len([x for x in L[i] if foot(x)]) for i in range(NSRC)]
M['hdr_793'] = [len([x for x in L[i] if hdr_793(x)]) for i in range(NSRC)]
M['hdr_rfc1122'] = [len([x for x in L[i] if hdr_1122(x)]) for i in range(NSRC)]
M['ietf_alone'] = [len([x for x in L[i] if ietf_line(x)]) for i in range(NSRC)]
M['hdr_new'] = [len([x for x in L[i] if hdr_new(x)]) for i in range(NSRC)]
M['pgnum'] = [len([x for x in L[i] if x.strip() != u''
                  and not [c for c in x if not (c.isdigit() or c.isspace())] and digit_runs(x) == 1])
              for i in range(NSRC)]
M['default_keys'] = [len([x for x in L[i] if keylin(x)]) for i in range(NSRC)]
M['default_lines'] = [len([x for x in L[i] if re.match(u'^\\s*Default:', x)]) for i in range(NSRC)]
for i in range(NSRC):
    print(u'1 %s 页脚样本 %r' % (LBL[i], [x for x in L[i] if foot(x)][:2]))
    print(u'  %s 眉/键样本 %r' % (LBL[i], [x for x in L[i] if hdr_793(x) or hdr_1122(x) or ietf_line(x)
                                      or hdr_new(x) or keylin(x)][:3]))
print(u'  [Page]行:', M['foot_page'], u' 793眉:', M['hdr_793'], u' RFC1122眉:', M['hdr_rfc1122'],
      u' IETF独立行:', M['ietf_alone'], u' 新式眉:', M['hdr_new'], u' 独立页码行:', M['pgnum'],
      u' 键行:', M['default_keys'], u' Default行:', M['default_lines'])


def is_shell(x, i):
    return (foot(x) or hdr_793(x) or hdr_1122(x) or ietf_line(x) or hdr_new(x)
            or ffline(x) or x.strip() == u'')


def ffline(x):
    return x == u'\x0c'


M['shell_lines'] = [len([1 for x in L[i] if is_shell(x, i)]) for i in range(NSRC)]
print(u'  壳行合计:', M['shell_lines'])

# ---------- 2. 义务词与编号标注 ----------
OB = [u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY']
M['ob_line'] = [[sum([ub(x, w) for x in L[i]]) for w in OB] for i in range(NSRC)]
M['ob_fold'] = [[ub(fold(T[i]), w) for w in OB] for i in range(NSRC)]
M['ob_wrap'] = [M['ob_fold'][i][k] - M['ob_line'][i][k] for i in range(NSRC) for k in range(len(OB))]
M['tag_paren'] = [len(re.findall(u'\\((MUST|SHOULD|MAY|SHLD|ED) \\d+\\)', T[i])) for i in range(NSRC)]
M['tag_dash'] = [len(re.findall(u'\\b(MUST|SHOULD|MAY|SHLD|ED)-\\d+\\b', T[i])) for i in range(NSRC)]
print(u'2 义务词 逐行:', M['ob_line'], u' 折平:', M['ob_fold'])
print(u'  跨行涨量(折−行):', M['ob_wrap'])
print(u'  (MUST 27)括号形:', M['tag_paren'], u' MUST-27横杠形:', M['tag_dash'])

# ---------- 3. “几次 / 多久”两把尺的语形 ----------
GRP = [u'retransmission', u'retransmissions', u'retransmit', u'retransmitted', u'retransmits',
       u'time units', u'count of retransmissions', u'threshold', u'excessive retransmissions',
       u'at least', u'before killing', u'time out', u'timeout', u'time-out', u'give up',
       u'abort', u'five minutes', u'3 minutes', u'100 seconds', u'60 seconds', u'924.6',
       u'tcp_retries1', u'tcp_retries2', u'tcp_syn_retries', u'tcp_synack_retries',
       u'tcp_orphan_retries', u'association_max_retrans', u'path_max_retrans', u'pf_retrans',
       u'max_init_retransmits', u'TCP_RTO_MIN', u'N times', u'(N+1)th', u'Default']
FL = [pnorm(T[i]) for i in range(NSRC)]
M['spell'] = [[cnt_cur(FL[i], pnorm(p)) for p in GRP] for i in range(NSRC)]
print(u'3 语形(整篇折平小写子串):')
for k, p in enumerate(GRP):
    print(u'   %-24s %s' % (p, [M['spell'][i][k] for i in range(NSRC)]))

# ---------- 4. 数字×单位对 ⇎ 次数式 ----------
RXU = re.compile(u'(?<![A-Za-z0-9.])(\\d+(?:[.,]\\d+)?)[ ]?(milliseconds|microseconds|seconds|ms|s)(?![A-Za-z])')
M['numunit'] = [[list(z) for z in sorted(set(RXU.findall(T[i])))] for i in range(NSRC)]
print(u'4 数字×单位对:')
for i in range(NSRC):
    print(u'   %s %s' % (LBL[i], M['numunit'][i]))
RXN = re.compile(u'(?<![A-Za-z0-9])(\\d+|N)(?:[ ]?(?:retransmissions|times|tries))\\b')
M['numtimes'] = [[list(z) for z in sorted(set(RXN.findall(pnorm(T[i]))))] for i in range(NSRC)]
print(u'  次数式:', M['numtimes'])

# ---------- 5. 判词针三档(逐行 ⇎ 全篇折平 ⇎ 摘壳折平) ----------
SHF = [pnorm(NL.join([x for x in L[i] if not is_shell(x, i)])) for i in range(NSRC)]
FOL = [pnorm(T[i]) for i in range(NSRC)]
NEEDLES = [
    u'send the segment at the front of the retransmission queue again',      # 793/9293 事件表
    u'reinitialize the retransmission timer, and return',
    u'There are two thresholds R1 and R2 measuring the amount of retransmission',
    u'R1 and R2 might be measured in time units or as a count of retransmissions',
    u'pass negative advice',
    u'to trigger dead-gateway diagnosis',
    u'close the connection',
    u'An application MUST be able to set the value for R2',
    u'set R2 to "infinity"',
    u'The value of R1 SHOULD correspond to at least 3 retransmissions, at the current RTO',
    u'The value of R2 SHOULD correspond to at least 100 seconds',
    u'SYN retransmissions MUST be handled in the general way',
    u'R2 for a SYN segment MUST be set large enough',
    u'for at least 3 minutes',
    u'give up on the open attempt',
    u'A maximum value MAY be placed on RTO provided it is at least 60 seconds',
    u'The present global default is five minutes',
    u'would retransmit N times before killing the connection at the (N+1)th RTO',
    u'The default value of 15 yields a hypothetical timeout of 924.6 seconds',
    u'RFC 1122 recommends at least 100 seconds for the timeout, which corresponds to a value of at least 8',
    u'RFC 1122 recommends at least 3 retransmissions, which is the default',
    u'corresponds to 63seconds till the last retransmission',
    u'happen after 127seconds',
    u'corresponds to 31seconds till the last retransmission',
    u'happen after 63seconds',
    u'with the current initial RTO of 1second',
    u'If this value is exceeded, the association is terminated',
    u'The maximum number of retransmissions that will be attempted on a given path',
]
print(u'5 判词针三档:')
rows = []
for nd in NEEDLES:
    q = pnorm(nd)
    r = []
    for i in range(NSRC):
        cl = len([x for x in L[i] if q in pnorm(x)])
        cf = cnt_cur(FOL[i], q)
        cs = cnt_cur(SHF[i], q)
        r.append((cl, cf, cs))
    rows.append((nd, r))
    print(u'   %-62s %s  摘壳命中=%s' % (nd[:62], r, [LBL[i] for i in range(NSRC) if r[i][2] > 0]))
M['needles3'] = [[list(z) for z in [r[i] for i in range(NSRC)]] for nd, r in rows]
M['needle_src'] = [[LBL[i] for i in range(NSRC) if r[i][2] > 0] for nd, r in rows]

# ---------- 6. 关键句行号定位(供锚) ----------
PINL = []
for nd in [n for n, r in rows if any(z[2] > 0 for z in r)]:
    for i in range(NSRC):
        a = find_line(i, nd)
        if a >= 0:
            nq = len([k for k in range(len(L[i])) if k <= a + 3 and pnorm(nd) in pnorm(NL.join(L[i][k:k + 4]))])
            PINL.append([LBL[i], nd, a + 1, nq])
            print(u'6 %s L%d «%s»' % (LBL[i], a + 1, nd[:70]))
M['pin_lines'] = PINL

# ---------- 7. 1122 §4.2.3.5.5 ⇎ 9293 对应节 逐句对照 ----------
def blk(i, a, b):
    return NL.join(L[i][a:b])


k1 = [find_line(1, u'The following procedure MUST be used to handle excessive')]
k2 = [find_line(2, u'The following procedure MUST be used to handle excessive')]
e1 = [find_line(1, u'give up on the open attempt) sooner, of course')]
e2 = [find_line(2, u'give up on the open attempt) sooner, of course')]
print(u'7 段落首末行 1122:', k1, e1, u' 9293:', k2, e2)
assert k1[0] >= 0 and k2[0] >= 0 and e1[0] >= 0 and e2[0] >= 0, u'段落端点未找到'
TAGRE = re.compile(u' \\((?:MUST|SHOULD|MAY|SHLD|ED)-\\d+\\)', re.I)


def sents(txt):
    return [pnorm(z) for z in re.split(u'(?<=[.!?]) +', pnorm(txt)) if z]


def canon(z):
    return (z.replace(u'implementers', u'implementors').replace(u'acknowledgment', u'acknowledgement')
            .replace(u'endpoint', u'site'))


B1 = blk(1, k1[0], e1[0] + 1)
B2 = blk(2, k2[0], e2[0] + 1)


def cut(txt, stop):
    j = txt.find(stop)
    return txt if j < 0 else txt[:j]


P1 = cut(B1, NL + u'4.2.3.6 ')
P2 = cut(B2, NL + u'3.8.4.')
print(u'  块首行 %r 块尾行 %r ｜ 1122 %d 行 ⇎ 9293 %d 行'
      % (P1.split(NL)[0][:40], P1.split(NL)[-1][:40], len(P1.split(NL)), len(P2.split(NL))))
s1, s2 = sents(P1), sents(P2)
s2c = [TAGRE.sub(u'', z).strip() for z in s2]
shared = [z for z in s2c if z in s1]
shared2 = [z for z in s2c if canon(z) in [canon(y) for y in s1]]
M['ovl_s1'], M['ovl_s2'], M['ovl_same'], M['ovl_same2'] = len(s1), len(s2), len(shared), len(shared2)
print(u'  1122块句数', len(s1), u' 9293块句数', len(s2), u' 去编号后全等', len(shared), u' 再归一后全等', len(shared2))
for z in s2:
    zc = TAGRE.sub(u'', z).strip()
    print(u'   [%s] %s' % (u'同' if zc in s1 else (u'拼' if canon(zc) in [canon(y) for y in s1] else u'新'), z[:104]))

# ---------- 8. 内核键值表: 与“放弃”有关的键 ----------
KEYS = {}
for i in range(NSRC):
    if LBL[i] != u'lin':
        continue
    cur = None
    for x in L[i]:
        if keylin(x):
            cur = x.split(u' - ')[0]
            KEYS[cur] = u''
        elif cur is not None:
            KEYS[cur] += u' ' + x
REL = [k for k in KEYS if re.search(u'retr|retry|timeout|_rto|rto_', k)]
print(u'8 内核相关键 %d 枚:' % len(REL))
M['lin_keys_total'] = len(KEYS)
M['lin_rel_keys'] = sorted(REL)
M['lin_rel_body'] = dict((k, re.sub(u'\\s+', u' ', KEYS[k]).strip()) for k in sorted(REL))
for k in sorted(REL):
    print(u'   %-26s %s' % (k, M['lin_rel_body'][k][:150]))
DEFN, DSH = {}, {}
for k, v in M['lin_rel_body'].items():
    m = re.search(u'(?i)Default: +([^ .;,)]+)', v)
    if m:
        DEFN[k], DSH[k] = m.group(1), u'Default:'
        continue
    m = re.search(u'(?i)default value is +(\\S+)', v)
    if m:
        DEFN[k], DSH[k] = m.group(1), u'default value is'
        continue
    m = re.search(u'(?i)default value of +(\\S+)', v)
    if m:
        DEFN[k], DSH[k] = m.group(1), u'default value of'
        continue
    m = re.search(u'(?i)at least (\\d+)[a-z ]*retransmissions, which is the default', v)
    if m:
        DEFN[k], DSH[k] = m.group(1), u'借参考句'
        continue
    DEFN[k], DSH[k] = None, u'无'
M['lin_defaults'], M['lin_default_shape'] = DEFN, DSH
print(u'  默认值:', DEFN)
print(u'  句式档:', DSH)

# ---------- 9. 等式候选(只在面上出现的数, 由本遍现算) ----------
def face_num(i, nd):
    return cnt_cur(FOL[i], pnorm(nd))


EQ = []
for a, b, c in [(6, 63, 127), (5, 31, 63)]:
    s = sum(2 ** k for k in range(a))
    EQ.append([a, s, s + 2 ** a, c, b])
    print(u'9 N=%d: 2^0..2^(N-1) 之和=%d, +2^N=%d ｜ 文档印 %d ⇎ %d' % (a, s, s + 2 ** a, b, c))
M['eq_syn'] = EQ

# ---------- 10. 两处 “five minutes” 的上下文 ⇎ 793 的无条件循环 ----------
CTX = {}
for tag, li, nd in [(u'793', 0, u'The present global default is five minutes'),
                    (u'9293', 2, u'The present global default is five minutes'),
                    (u'793', 0, u'send the segment at the front of the retransmission queue again'),
                    (u'9293', 2, u'send the segment at the front of the retransmission queue again'),
                    (u'6298', 3, u'A maximum value MAY be placed on RTO'),
                    (u'lin', 4, u'The default value of 15 yields')]:
    a = find_line(li, nd)
    assert a >= 0, (tag, nd)
    win = NL.join(L[li][max(0, a - 6):a + 4])
    CTX[tag + u'|' + nd] = re.sub(u'\\s+', u' ', win)
    print(u'10 [%s L%d] %s' % (tag, a + 1, CTX[tag + u'|' + nd][:520]))
M['ctx'] = CTX
KEYWORD = [len(re.findall(u'\\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY)\\b', T[i])) for i in range(NSRC)]
LOWKW = [len(re.findall(u'(?i)\\b(must|should|may)\\b', T[i])) - KEYWORD[i] for i in range(NSRC)]
M['kw_allcaps'], M['kw_lowercase'] = KEYWORD, LOWKW
print(u'  大写义务词形(全篇, 含引用他文处):', KEYWORD, u' 小写同词:', LOWKW)

json.dump(M, io.open(u'corpus/_b86meas.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
print(u'已落 corpus/_b86meas.json ｜ 键 %d' % len(M))
