# -*- coding: utf-8 -*-
"""B64 ⛓解读注(第四遍): 本注每个数都是现测并 assert 的, 不手填。
四套实现: 采集侧 corpus/_pick64.py(正则收时长与表行、集合运算求搬运、sha 签名档)
⇎ 建条目侧 corpus/_mkB64.py(游标档 find 循环、逐字符形状档、表行先按 '|' 再按字符类切、OLD:/NEW: 标签配对、
  退避序列面内仿真, 扁平契约 corpus/_b64flat.json)
⇎ 门槛侧 corpus/audit.py::_b64_scan()(由 corpus/_wire64.py 从 SCAN 段机械抽出, 插门前把全部扁平键与 DERIV 算式逐条预演)
⇎ 本注第四遍, 与前三遍都换算法不换定义:
①形状档全部走字符串法而非字符状态机: 行数 len(t.split(NL)) ⇎ t.count(NL)+1 两式互证、非空行按 l.strip() 真值计数、
  “只认空格/制表/回车”的宽口径按 l.strip(' \\t\\r')、独占换页符的行按“窄口径非空 ⇎ 全篇判空”两条同时成立筛出;
②字面档用 re.findall(re.escape(针)) (建条目侧是 find 循环), 窗档用 finditer 取全部起点后按窗区间筛——
  窗外不是“总数减窗内”, 而是位置表的补集;
③表行切列用两条正则: 竖线档 ^\\|([^|]+)\\|\\s*([\\d,]+)、空白档 ^([A-Z][A-Z0-9_]{2,})[ \\t]+([\\d,]+),
  表头与终止条件按“同行含 Parameter 与 Default 且短行”⇎“行首 \\d+\\.\\d+”——建条目侧是逐字符走位;
④OLD:/NEW: 配对用 ^\\s*(OLD:|NEW:)\\s*$ 收标签行, 名值从块首行按上面两条正则现取, 无名时退到块内首个长度≥3 的大写串;
⑤答数档: 针的**第一处**命中(建条目侧同为 find, 但本注用 re.search 取位置)后紧跟锚定正则
  ^([\\d,]+)(空白类)(单位族)(?![A-Za-z]), 单位族按建条目侧同序(长名先试), 跨行标志数的是针尾到单位头之间的换行;
⑥退避序列由面内首值仿真到封顶(4→8→16→32→64), 不手填任何一项; 夹逼上下界由一条
  (\\d+)\\s*<= "value" <=\\s*(\\d+) 一次取两端(建条目侧是 num_before/num_after 两趟走位);
⑦时长族一条正则收非重叠 token(\\d[\\d,]*)(空白类)(单位族)(?![A-Za-z]), 与建条目侧的逐字符扫描对拍出现处、取值集、
  单位种数、跨行枚与窗内⇎窗外两档;
⑧义务词两档: 全大写族按转义 findall(故 MUST 一档含 "MUST NOT" 内的), 小写族按 [A-Za-z0-9_]+ 词流整词相等;
⑨壳账: 页眉两式 ^RFC \\d{4}(?!\\d) 带题文 ⇎ ^RFC\\d{4}(?!\\d)( |$), 页脚两式 \\[(?:Page )\\d+\\]$ ⇎ (^|[[ \\t])Page \\d+$,
  “[Page ” 子串档另立; 逐字符⇎正则两式必须同数;
⑩搬运账归一只留 a-z0-9(re.sub), 交用集合运算符 &、并用 itertools 逐对; 并集用 |; 容斥按 1−3+3−1 阶本注自己列齐;
⑪恒等式与 DERIV 的账: 27 条恒等式的算式由 ast.parse 在建条目侧源码的赋值语句里现取(ZID 字面量, 只搬算式不搬数),
  全部 DERIV 算式取自 corpus/_deriv64.json, 分两档复算: 数值键按 |读数−键| < 1e-9, 字面值键(表头行号 ⇎ 序列 ⇎ 值集 ⇎
  单位名 ⇎ 标题串)按 读数==键 或 str(读数)==键; 两条通道都用**本注的读数**求值——算式是第二遍的宣称, 数是第四遍现测的;
⑫锚归属由条目正文 ⟦标签⟧⟨引文⟩ 配对现推, 成员判据双轨: ①逐行流式拼归一面(每批只留末尾 len(锚)−1 字符续接, 不现造整篇面)
  ②单行表 ⇎ 相邻两行拼接表按子串判; 两式必须同判; 另求“这枚锚最少压在几行上”(1..6 行滑窗)得行跨度分布。
不可由在库文件判定的只写在本注: 四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧、rfc-editor.org 此刻给这四份挂的状态页与
Obsoletes/Updates 图、勘误表是否已改动 3315 的 §5.5、各家 DHCP 客户端把 SOL_MAX_RT 实际记多久(掉电⇎重启⇎换接口之后)、
以及 3600 秒的缺省在真实网络里是否真如 13 所说减少聚合流量——都不进判词与门槛。
"""
import io, os, re, sys, json, ast, bisect, hashlib, itertools

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
WCH = u' \t\n\x0b\x0c\r'
WCHR = u'\\ \\t\\n\\x0b\\x0c\\r'
DIG = u'0123456789'
ENTRY = os.path.join(C, 'babeltele', 'B64_dhcp_retransmit_cap_four_answers.md')
PATH = [u'corpus/raw/dhcp/rfc2131.txt', u'corpus/raw/dhcp/rfc3315.txt',
        u'corpus/raw/dhcp/rfc7083.txt', u'corpus/raw/dhcp/rfc8415.txt']
TAGS = [u'A', u'B', u'C', u'D']
LB = dict(zip(TAGS, [u'97 六十四', u'03 一百二', u'13 倍三十', u'18 可下发']))
NSRC = 4
FLAT = json.load(io.open(C + u'/_b64flat.json', encoding=u'utf-8'))
MEAS = json.load(io.open(C + u'/_b64meas.json', encoding=u'utf-8'))
CH = json.load(io.open(C + u'/_b64checks.json', encoding=u'utf-8'))
DER = json.load(io.open(C + u'/_deriv64.json', encoding=u'utf-8'))

RAWB = [open(p, 'rb').read() for p in PATH]
TXT = [b.decode('utf-8-sig') for b in RAWB]
LST = [t.split(NL) for t in TXT]
LOW = [t.lower() for t in TXT]
FO = [re.sub(u'[' + WCHR + u']+', u' ', t) for t in TXT]
J = lambda xs: u'⇎'.join(str(x) for x in xs)


def nrm(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


FAN = [nrm(t) for t in TXT]
M = {}
MIS = []
SEEN = set()


def chk(name, val):
    """本注现测值与扁平契约对拍; 键在采集表里时一并再比一次。"""
    val = list(val) if isinstance(val, (list, tuple)) else val
    if name in FLAT:
        if FLAT[name] != val:
            MIS.append((name, FLAT[name], val))
            raise AssertionError((name, FLAT[name], val))
    else:
        MIS.append((u'缺键', name, None))
    if name in MEAS and MEAS[name] != val:
        MIS.append((u'采集侧' + name, MEAS[name], val))
        raise AssertionError((u'pick', name, MEAS[name], val))
    M[name] = val
    SEEN.add(name)
    return val


def cnt(t, needle):
    return len(re.findall(re.escape(needle), t))


def occpos(t, needle):
    return [m.start() for m in re.finditer(re.escape(needle), t)]


# ---------- ①形状档: 字符串法 ----------
four = lambda name, f: chk(name, [f(i) for i in range(NSRC)])
four(u'bytes', lambda i: len(RAWB[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'chars_no_nl', lambda i: len(TXT[i]) - TXT[i].count(NL))
four(u'lines', lambda i: len(LST[i]))
assert [len(t.split(NL)) for t in TXT] == M[u'lines']
assert [t.count(NL) + 1 for t in TXT] == M[u'lines']
four(u'rec_close', lambda i: M[u'lines'][i] - (TXT[i].count(NL) + 1))
four(u'nonblank', lambda i: len([l for l in LST[i] if l.strip()]))
four(u'nonblank_asciib', lambda i: len([l for l in LST[i] if l.strip(u' \t\r')]))
four(u'nb_gap', lambda i: M[u'nonblank_asciib'][i] - M[u'nonblank'][i])
four(u'ff_only_lines', lambda i: len([l for l in LST[i] if l.strip(u' \t\r') and not l.strip()]))
four(u'cr', lambda i: TXT[i].count(u'\r'))
four(u'nonascii', lambda i: len([ch for ch in TXT[i] if ord(ch) > 127]))
four(u'bom', lambda i: 1 if RAWB[i][:3] == bytes([239, 187, 191]) else 0)
four(u'formfeed', lambda i: TXT[i].count(u'\x0c'))
four(u'maxlen', lambda i: max(len(l) for l in LST[i]))
four(u'trail', lambda i: len([l for l in LST[i] if l != l.rstrip()]))
chk(u'bytes_span', max(M[u'bytes']) - min(M[u'bytes']))
chk(u'sig', [hashlib.blake2b(RAWB[i], digest_size=8).hexdigest() for i in range(NSRC)])
chk(u'sig_distinct', len(set(M[u'sig'])))
chk(u'nb_ff_sum', sum(M[u'nb_gap'][i] - M[u'ff_only_lines'][i] for i in range(NSRC)))

# ---------- ⑨壳账: 页眉两式 ⇎ 页脚两式 ----------
H_SP = re.compile(u'^RFC \\d{4}(?!\\d) [' + WCHR + u']*[^' + WCHR + u']')
H_NS = re.compile(u'^RFC\\d{4}(?!\\d)(?:[ ]|$)')
F_BR = re.compile(u'\\[(?:Page )\\d+\\]$')
F_OLD = re.compile(u'(?:^|[\\[ \\t])Page \\d+$')
four(u'hdr_sp', lambda i: len([l for l in LST[i] if H_SP.match(l)]))
four(u'hdr_ns', lambda i: len([l for l in LST[i] if H_NS.match(l) and not H_SP.match(l)]))
four(u'hdr', lambda i: len([l for l in LST[i] if H_SP.match(l) or H_NS.match(l)]))
four(u'foot_brk', lambda i: len([l for l in LST[i] if F_BR.search(l.strip())]))
four(u'foot', lambda i: len([l for l in LST[i] if F_BR.search(l.strip()) or F_OLD.search(l.strip())]))
four(u'pg', lambda i: cnt(TXT[i], u'[Page '))
chk(u'pagelines', [M[u'hdr'][i] + M[u'foot'][i] for i in range(NSRC)])
chk(u'pages_est', [M[u'formfeed'][i] if M[u'formfeed'][i] else max(M[u'hdr'][i], M[u'foot'][i])
                   for i in range(NSRC)])
chk(u'hdr_ledger', [M[u'hdr_sp'][i] + M[u'hdr_ns'][i] - M[u'hdr'][i] for i in range(NSRC)])
chk(u'hdr_ledger_sum', sum(M[u'hdr_ledger']))
chk(u'ff_foot_sum', sum([M[u'formfeed'][i] - M[u'foot'][i] for i in range(NSRC)]))
chk(u'pg_foot_sum', sum([M[u'pg'][i] - M[u'foot'][i] for i in range(NSRC)]))
assert [M[u'formfeed'][i] - M[u'trail'][i] for i in range(NSRC)] == [0] * 4
assert M[u'foot'] == M[u'foot_brk'] == M[u'trail'] == M[u'formfeed'] == M[u'pg'] == M[u'nb_gap']

# ---------- ②字面档 ----------
LITK = {
    u'max64': u'maximum of 64 seconds', u'd64': u'64 seconds', u'd4s': u'4 seconds', u'd8s': u'8 seconds',
    u'reback': u'randomized exponential backoff', u'retrans': u'retransmi', u'solmaxrt': u'SOL_MAX_RT',
    u'infmaxrt': u'INF_MAX_RT', u'reqmaxrt': u'REQ_MAX_RT', u'renmaxrt': u'REN_MAX_RT', u'rebmaxrt': u'REB_MAX_RT',
    u'reqmaxrc': u'REQ_MAX_RC', u'relmaxrc': u'REL_MAX_RC', u'decmaxrc': u'DEC_MAX_RC', u'cnfmaxrt': u'CNF_MAX_RT',
    u'solmaxdelay': u'SOL_MAX_DELAY', u'soltimeout': u'SOL_TIMEOUT', u'rectimeout': u'REC_TIMEOUT',
    u's120': u'120 secs', u's3600': u'3600 secs', u's600': u'600 secs', u's1sec': u'1 sec',
    u'v86400': u'86400', u'v604800': u'604800', u'v3600': u'3600', u'v120': u'120',
    u'clamp': u'60 <=', u'ignore': u'MUST ignore any', u'irt': u'IRT', u'irc': u'IRC',
    u'infreq': u'Information-request', u'ta': u'IA_TA', u'pd': u'IA_PD',
    u't1': u'T1', u't2': u'T2', u'p50': u'50%', u'p875': u'87.5', u'p05': u'0.5', u'p08': u'0.8',
    u'infin': u'infinity', u'ffffffff': u'0xffffffff', u'preferre': u'shortest preferred lifetime',
    u'leasedur': u'lease duration', u'oldlbl': u'OLD:', u'newlbl': u'NEW:',
    u'discard': u'discards the IA', u'optionreq': u'Option Request option',
}
for k in sorted(LITK):
    four(u'lit_' + k, lambda i, k=k: cnt(TXT[i], LITK[k]))
four(u'lit_durdef', lambda i: cnt(TXT[i], u'0.5 * duration_of_lease'))
four(u'lit_durdef875', lambda i: cnt(TXT[i], u'0.875 * duration_of_lease'))
four(u'lit_durdef875_fold', lambda i: cnt(FO[i], u'0.875 * duration_of_lease'))
chk(u'lit_durdef875_gap', [M[u'lit_durdef875_fold'][i] - M[u'lit_durdef875'][i] for i in range(NSRC)])
chk(u'lit_durdef875_gap_sum', sum(M[u'lit_durdef875_gap']))
four(u'lit_durword', lambda i: cnt(TXT[i], u'duration_of_lease'))
four(u'lit_t1def', lambda i: cnt(TXT[i], u'T1 defaults') + cnt(TXT[i], u'T2 defaults'))
four(u'lit_sameacross', lambda i: cnt(TXT[i], u'the same values across all IAs'))
four(u'lit_iface', lambda i: cnt(TXT[i], u'applies only to the network interface'))
four(u'lit_retain', lambda i: cnt(TXT[i], u'this value is expected to be retained'))
four(u'lit_retain_sp', lambda i: cnt(TXT[i], u'retained for as long as practically possible'))
four(u'lit_srt_minus_irt', lambda i: M[u'lit_solmaxrt'][i] - M[u'lit_irt'][i])

# ---------- ③表行切列: 两条正则 ----------
R_PIPE = re.compile(u'^\\|([^|]+)\\|[' + WCHR + u']*([\\d,]+)')
R_WS = re.compile(u'^([A-Z][A-Z0-9_]{2,})[' + WCHR + u']+([\\d,]+)')
KNAMES = [u'SOL_MAX_RT', u'INF_MAX_RT', u'REN_MAX_RT', u'REB_MAX_RT', u'REQ_MAX_RT', u'SOL_TIMEOUT',
          u'REQ_TIMEOUT', u'REB_TIMEOUT', u'INF_TIMEOUT', u'REL_TIMEOUT', u'DEC_TIMEOUT', u'CNF_TIMEOUT',
          u'REC_TIMEOUT', u'SOL_MAX_DELAY', u'CNF_MAX_DELAY', u'INF_MAX_DELAY', u'CNF_MAX_RD',
          u'REQ_MAX_RC', u'REL_MAX_RC', u'DEC_MAX_RC', u'CNF_MAX_RC', u'REC_MAX_RC', u'MAX_RC']


def row(l):
    s = l.strip()
    if not s:
        return None
    if u'|' in s:
        m = R_PIPE.match(s)
        if not m:
            return None
        nm, v = m.group(1).strip(), m.group(2)
    else:
        m = R_WS.match(s)
        if not m:
            return None
        nm, v = m.group(1), m.group(2)
    if not nm or nm != nm.upper() or len(nm) < 3 or any(ch not in DIG + u',' for ch in v):
        return None
    return nm, int(v.replace(u',', u''))


def tables(i):
    out, cur = [], None
    for n, l in enumerate(LST[i]):
        s = l.strip()
        if u'Parameter' in s and u'Default' in s and len(s) < 96:
            if cur is not None and cur[1]:
                out.append((cur[0], dict(cur[1])))
            cur = [n, {}]
            continue
        if cur is None or not s:
            continue
        r = row(l)
        if r:
            cur[1][r[0]] = r[1]
            continue
        if re.match(u'^\\d+\\.\\d+', s) and cur[1]:
            out.append((cur[0], dict(cur[1])))
            cur = None
    if cur is not None and cur[1]:
        out.append((cur[0], dict(cur[1])))
    return out


TB = [tables(i) for i in range(NSRC)]
four(u'tbl_n', lambda i: len(TB[i]))
chk(u'tbl_rows', [[len(d) for _, d in TB[i]] for i in range(NSRC)])
chk(u'tbl_start', [[st for st, _ in TB[i]] for i in range(NSRC)])
chk(u'tbl_rows_0', [(r[0] if r else 0) for r in M[u'tbl_rows']])
chk(u'tbl_row_delta', M[u'tbl_rows_0'][3] - M[u'tbl_rows_0'][1])
for k in KNAMES:
    four(u'pv_' + k.lower(), lambda i, k=k: sorted(set(d[k] for _, d in TB[i] if k in d)))
BD = [(k, TB[1][0][1].get(k), TB[3][0][1].get(k)) for k in KNAMES] if (TB[1] and TB[3]) else []
BD = [x for x in BD if x[1] is not None and x[2] is not None]
chk(u'bd_n', len(BD))
chk(u'bd_same', len([x for x in BD if x[1] == x[2]]))
chk(u'bd_diff', [[x[0], x[1], x[2]] for x in BD if x[1] != x[2]])
chk(u'bd_diff_n', len(M[u'bd_diff']))
chk(u'bd_ratio', [x[2] // x[1] for x in BD if x[1] and x[2] % x[1] == 0])
chk(u'bd_close', M[u'bd_same'] + M[u'bd_diff_n'] - M[u'bd_n'])
chk(u'bd_pv_same', len([k for k in KNAMES if M[u'pv_' + k.lower()][1] and M[u'pv_' + k.lower()][3]
                        and M[u'pv_' + k.lower()][1] == M[u'pv_' + k.lower()][3]]))
chk(u'bd_unproposed', [x[0] for x in M[u'bd_diff'] if x[0] not in (u'SOL_MAX_RT', u'INF_MAX_RT')])
chk(u'bd_unproposed_n', len(M[u'bd_unproposed']))
chk(u'cap_ratio_d_b', M[u'pv_sol_max_rt'][3][0] // M[u'pv_sol_max_rt'][1][0])

# ---------- ④OLD:/NEW: 标签配对 ----------
R_LBL = re.compile(u'^\\s*(OLD:|NEW:)\\s*$')
R_UPRUN = re.compile(u'[A-Z][A-Z0-9_]{2,}')


def oldnew(i):
    rows = [(n, m.group(1)) for n, l in enumerate(LST[i]) for m in [R_LBL.match(l)] if m]
    out, k = [], 0
    while k + 1 < len(rows) and rows[k][1] == u'OLD:' and rows[k + 1][1] == u'NEW:':
        na, nb = rows[k][0], rows[k + 1][0]
        wa = NL.join(LST[i][na + 1:na + 4])
        wb = NL.join(LST[i][nb + 1:nb + 4])
        fa = wa.split(NL)[0].strip()
        fb = wb.split(NL)[0].strip()
        ca = R_WS.match(fa) or R_PIPE.match(fa)
        cb = R_WS.match(fb) or R_PIPE.match(fb)
        if ca:
            nm, va = ca.group(1), int(ca.group(2))
        else:
            m = R_UPRUN.search(wa)
            nm, va = (m.group(0) if m else u''), None
        vb = int(cb.group(2)) if cb else None
        out.append([nm, va, vb, nb - na])
        k += 2
    return out, len(rows)


ON = {}
for i, t in enumerate(TAGS):
    pr, nr = oldnew(i)
    ON[t] = pr
    chk(u'on_pair_' + t.lower(), pr)
    chk(u'on_n_' + t.lower(), nr)
chk(u'on_changed', [p[0] for p in ON[u'C'] if p[1] and p[2] and p[1] != p[2]])
chk(u'on_changed_n', len(M[u'on_changed']))
chk(u'on_ratio', [p[2] // p[1] for p in ON[u'C'] if p[1] and p[2] and p[2] % p[1] == 0])
chk(u'on_span', sum(p[3] for p in ON[u'C']))
chk(u'on_ratio_cap_close', M[u'on_ratio'][0] - M[u'cap_ratio_d_b'])

# ---------- ⑤答数档 ----------
MUL = {u'milliseconds': 1, u'millisecond': 1, u'secs': 1000, u'seconds': 1000,
       u'sec': 1000, u'second': 1000, u'ms': 1}
UALT = u'milliseconds|millisecond|secs|seconds|sec|second|ms'
R_ANCHOR = re.compile(u'^([' + DIG + u',]+)([' + WCHR + u']*)(' + UALT + u')(?![A-Za-z])')


def dur_after(t, needle):
    m = re.search(re.escape(needle), t)
    if not m:
        return (0, u'', u'', 0)
    p = m.end()
    q = p
    while q < len(t) and t[q] in WCH:
        q += 1
    dm = re.match(u'[' + DIG + u',]+', t[q:])
    if not dm:
        return (0, u'', u'', 1 if NL in t[p:q] else 0)
    d = dm.group(0)
    nm = R_ANCHOR.match(t[q:])
    if not nm or nm.group(1) != d:
        return (0, d, u'', 1 if NL in t[p:q + len(d)] else 0)
    gap = nm.group(2)
    return (int(d.replace(u',', u'')) * MUL[nm.group(3)], d, nm.group(3),
            1 if (NL in t[p:q + len(d)] or NL in gap) else 0)


def dur_near(t, needle, span=64):
    m = re.search(re.escape(needle), t)
    if not m:
        return (0, u'', u'', 0)
    w = t[m.end():m.end() + span]
    q = re.search(u'[' + DIG + u']', w)
    if not q:
        return (0, u'', u'', 0)
    return dur_after(w[q.start():], u'')


def dur_tagged(t, tag, word, span=96):
    for m in re.finditer(re.escape(tag), t):
        seg = t[m.end():m.end() + span]
        if word in seg:
            return dur_near(seg, word)
    return (0, u'', u'', 0)


ANSN = {u'A': u'up to a maximum of ', u'B': u'SOL_MAX_RT      ', u'D': u'| SOL_MAX_RT      | '}
ANS = [dur_tagged(TXT[i], u'NEW:', u'SOL_MAX_RT') if TAGS[i] == u'C' else dur_after(TXT[i], ANSN[TAGS[i]])
       for i in range(NSRC)]
chk(u'y_ans_ms', [a[0] for a in ANS])
chk(u'y_ans_num', [a[1] for a in ANS])
chk(u'y_ans_unit', [a[2] for a in ANS])
chk(u'y_ans_wrap', [a[3] for a in ANS])
chk(u'y_ans_s', [M[u'y_ans_ms'][i] // 1000 for i in range(NSRC)])
chk(u'y_ans_distinct', len(set(M[u'y_ans_ms'])))
chk(u'y_ans_max', max(M[u'y_ans_ms']))
chk(u'y_ans_min', min(M[u'y_ans_ms']))
chk(u'y_ans_ratio', M[u'y_ans_max'] // M[u'y_ans_min'])
chk(u'y_ans_rem', M[u'y_ans_max'] - M[u'y_ans_ratio'] * M[u'y_ans_min'])
chk(u'y_ans_span_close', M[u'y_ans_max'] - M[u'y_ans_ratio'] * M[u'y_ans_min'] - M[u'y_ans_rem'])
chk(u'y_cd_ans_close', M[u'y_ans_ms'][2] - M[u'y_ans_ms'][3])
chk(u'y_bc_ans_gap', M[u'y_ans_ms'][1] - M[u'y_ans_ms'][0])
chk(u'y_db_ans_gap', M[u'y_ans_ms'][3] - M[u'y_ans_ms'][1])

# ---------- ⑥A 的翻倍序列仿真 ⇎ 夹逼两界 ----------
FR = dur_near(TXT[0], u'the delay before the first retransmission SHOULD')
NR = dur_near(TXT[0], u'The delay before the next retransmission SHOULD')
chk(u'y_a_first', FR[0])
chk(u'y_a_next', NR[0])
chk(u'y_a_first_wrap', FR[3])
chk(u'y_a_next_wrap', NR[3])
seq, s = [], M[u'y_a_first']
while s and s <= M[u'y_ans_ms'][0]:
    seq.append(s)
    s *= 2
chk(u'a_seq_ms', seq)
chk(u'a_seq', [x // 1000 for x in seq])
chk(u'a_seq_n', len(seq))
chk(u'a_doublings', len(seq) - 1)
chk(u'a_ratio', seq[-1] // seq[0])
chk(u'a_seq_close', seq[-1] - M[u'y_ans_ms'][0])
chk(u'a_seq_next_close', seq[1] - M[u'y_a_next'])
chk(u'a_ratio_pow_close', M[u'a_ratio'] - 2 ** M[u'a_doublings'])
chk(u'a_cap_x_first_close', M[u'y_a_first'] * M[u'a_ratio'] - M[u'y_ans_ms'][0])
chk(u'a_cap_ratio_d_b', M[u'y_ans_ms'][3] // M[u'y_ans_ms'][0])
four(u'a_first_lit', lambda i: cnt(TXT[i], u'randomized by the value of a uniform'))
R_CLAMP = re.compile(u'([0-9]+)\\s*<= "value" <=\\s*([0-9]+)')
CL = [R_CLAMP.search(t) for t in TXT]
chk(u'clamp_lo', [int(m.group(1)) if m else 0 for m in CL])
chk(u'clamp_hi', [int(m.group(2)) if m else 0 for m in CL])
LO60 = max([x for x in M[u'clamp_lo'] if x])
chk(u'clamp_span', max(M[u'clamp_hi']) // LO60)
chk(u'clamp_span_close', M[u'clamp_span'] * LO60 - max(M[u'clamp_hi']))
chk(u'clamp_cd_lo_close', M[u'clamp_lo'][2] - M[u'clamp_lo'][3])
chk(u'clamp_cd_hi_close', M[u'clamp_hi'][2] - M[u'clamp_hi'][3])
four(u'y_clamp_lit', lambda i: cnt(TXT[i], u'60 <= "value" <= 86400'))
four(u'y_clamp_86400', lambda i: cnt(TXT[i], u'or more than 86400'))
four(u'y_ignore_srt', lambda i: cnt(TXT[i], u'MUST ignore any SOL_MAX_RT'))
four(u'y_ignore_inf', lambda i: cnt(TXT[i], u'MUST ignore any INF_MAX_RT'))
four(u'y_must_ignore_n', lambda i: cnt(TXT[i], u'MUST ignore any'))

# ---------- C ⇎ D 夹逼句逐行对照 ----------
CS = [l for l in LST[2] if u'60 <= "value"' in l]
DS = [l for l in LST[3] if u'60 <= "value"' in l]
chk(u'y_cd_lines', [len(CS), len(DS)])
PAIR = list(zip(CS, DS))
chk(u'al_n', len(PAIR))
chk(u'al_same_bytes', len([1 for a, b in PAIR if a == b]))
chk(u'al_punct_only', len([1 for a, b in PAIR if a != b and nrm(a) == nrm(b)]))
chk(u'al_norm_diff', len([1 for a, b in PAIR if nrm(a) != nrm(b)]))
chk(u'al_close', M[u'al_same_bytes'] + M[u'al_punct_only'] + M[u'al_norm_diff'] - M[u'al_n'])
chk(u'al_char_delta', sum(len(b) - len(a) for a, b in PAIR))

# ---------- ⑦折行两档 ----------
SN = [(u'c120', u'values of SOL_MAX_RT and INF_MAX_RT to be 120 seconds.'),
      (u'c3600', u'every 3600 seconds rather than every'),
      (u'clampfull', u'MUST be in this range: 60 <= "value" <= 86400'),
      (u'ignorefull', u'MUST ignore any SOL_MAX_RT option values that are less'),
      (u'max64full', u'The retransmission delay SHOULD be doubled with\n   subsequent retransmissions up to a maximum of 64 seconds.'),
      (u'max64sp', u'The retransmission delay SHOULD be doubled with subsequent retransmissions up to a maximum of 64 seconds.'),
      (u'retainfull', u'this value is expected to be retained for as long as practically possible'),
      (u'samefull', u'The T1/T2 times set in each applicable IA option for a Reply MUST be'),
      (u'discfull', u'If a client receives an IA_NA with T1 greater than T2'),
      (u'reback', u'client MUST adopt a retransmission strategy that incorporates a'),
      (u'ifacefull', u'An updated SOL_MAX_RT value applies only to the network interface')]
TN = [(u'p05', u'0.5'), (u'p08', u'0.8'), (u'ld', u'lease duration'),
      (u'spl', u'shortest preferred lifetime'), (u'userval', u'MUST use the'),
      (u'zerorule', u'are set to 0')]
for k, s in SN:
    four(u's_' + k, lambda i, s=s: cnt(TXT[i], s))
    four(u's_' + k + u'_fold', lambda i, s=s: cnt(FO[i], u' '.join(s.split())))
    chk(u'wrapgap_' + k, [M[u's_' + k + u'_fold'][i] - M[u's_' + k][i] for i in range(NSRC)])
chk(u'wrap_sn_n', len(SN))
chk(u'wrap_sn_hit', len([1 for k, _ in SN if max(M[u'wrapgap_' + k]) > 0]))
chk(u'wrap_sn_total', sum([sum(M[u'wrapgap_' + k]) for k, _ in SN]))
for k, s in TN:
    four(u'n_' + k, lambda i, s=s: cnt(TXT[i], s))
    four(u'n_' + k + u'_fold', lambda i, s=s: cnt(FO[i], u' '.join(s.split())))
    chk(u'wrap_' + k, [M[u'n_' + k + u'_fold'][i] - M[u'n_' + k][i] for i in range(NSRC)])
chk(u'wrap_pin_n', len(TN))
chk(u'wrap_pin_hit', len([1 for k, _ in TN if max(M[u'wrap_' + k]) > 0]))
chk(u'wrap_total', sum([sum(M[u'wrap_' + k]) for k, _ in TN]))

# ---------- ⑧规范窗: 一次收全篇编号标题 ----------
R_HEAD = re.compile(u'^[' + WCHR + u']*([0-9]+(?:\\.[0-9]+)*\\.?)[' + WCHR + u']+\\S')
RULE = {u'A': u'up to a maximum of 64 seconds', u'B': u'SOL_MAX_RT      120 secs',
        u'C': u'SOL_MAX_RT     3600 secs', u'D': u'| SOL_MAX_RT      | 3600 secs'}
OFF = [list(itertools.accumulate([0] + [len(l) + 1 for l in LST[i]]))[:-1] for i in range(NSRC)]
SECW, SECN = [], []
for i in range(NSRC):
    ls = LST[i]
    hits = [n for n, l in enumerate(ls) if RULE[TAGS[i]] in l]
    r = hits[-1]
    hd = {}
    for n, l in enumerate(ls):
        m = R_HEAD.match(l)
        if m and len(l.strip()) > 3:
            hd[n] = m.group(1)
    a = max([n for n in hd if n <= r])
    pre = ls[a].strip().split(u' ')[0]
    b = len(ls)
    for n in sorted(k for k in hd if k > r):
        s = ls[n].strip()
        if s == ls[a].strip() or s.startswith(pre):
            continue
        b = n
        break
    SECW.append((a, b))
    SECN.append(hd[a])
chk(u'sec_w', [list(w) for w in SECW])
chk(u'sec_a', [w[0] for w in SECW])
chk(u'sec_b', [w[1] for w in SECW])
chk(u'sec_hit', [len([l for l in LST[i] if RULE[TAGS[i]] in l]) for i in range(NSRC)])
chk(u'sec_head', [LST[i][SECW[i][0]].strip()[:64] for i in range(NSRC)])
chk(u'sec_len', [len(NL.join(LST[i][SECW[i][0]:SECW[i][1]])) for i in range(NSRC)])
for i in range(NSRC):
    chk(u'sec_len_' + TAGS[i].lower(), M[u'sec_len'][i])
    chk(u'sec_off_' + TAGS[i].lower(), [OFF[i][SECW[i][0]],
                                         OFF[i][SECW[i][1]] - 1 if SECW[i][1] < len(OFF[i]) else len(TXT[i])])
def inwin(i, p):
    a, b = M[u'sec_off_' + TAGS[i].lower()]
    return a <= p < b


# 编号串的写法差异申报在本注: 本注按正则收 '4.1 ⇎ 5.5. ⇎ 3.', 建条目侧的逐字符档写作 '4..1 ⇎ 5..5 ⇎ 3';
# 两式折叠点号再去尾部点号后同值
FOLD = lambda x: re.sub(u'\\.+$', u'', re.sub(u'\\.+', u'.', x))
assert [FOLD(x) for x in SECN] == [FOLD(x) for x in FLAT[u'sec_num']], (SECN, FLAT[u'sec_num'])
M[u'sec_num'] = [FOLD(x) for x in SECN]
WINS = [(u'solmaxrt', u'SOL_MAX_RT'), (u'infmaxrt', u'INF_MAX_RT'), (u'v86400', u'86400'),
        (u's120', u'120 secs'), (u's3600', u'3600 secs'), (u'ignore', u'MUST ignore any'),
        (u't1', u'T1'), (u'infin', u'infinity')]
for k, s in WINS:
    PS = [occpos(TXT[i], s) for i in range(NSRC)]
    four(u'secw_' + k, lambda i, k=k, PS=PS: len([p for p in PS[i] if inwin(i, p)]))
    four(u'outw_' + k, lambda i, k=k: M[u'lit_' + k][i] - M[u'secw_' + k][i])
for k, s in ((u'may', u'MAY'), (u'must', u'MUST'), (u'should', u'SHOULD'), (u'should_not', u'MUST NOT')):
    four(u'y_secw_' + k, lambda i, s=s: len([p for p in occpos(TXT[i], s) if inwin(i, p)]))
    four(u'y_outw_' + k, lambda i, s=s, k=k: cnt(TXT[i], s) - M[u'y_secw_' + k][i])

# ---------- ⑦时长族: 一条正则收 token ----------
DURRE = re.compile(u'([' + DIG + u'][' + DIG + u',]*)([' + WCHR + u']*)(' + UALT + u')(?![A-Za-z])')
DU = [[(int(m.group(1).replace(u',', u'')) * MUL[m.group(3)], m.start(), m.group(1), m.group(3),
        1 if NL in m.group(2) else 0) for m in DURRE.finditer(t)] for t in TXT]
for i in range(NSRC):
    vs = sorted(set(x[0] for x in DU[i] if x[0] > 0))
    chk(u'durms_' + TAGS[i].lower(), vs)
    chk(u'durms_n_' + TAGS[i].lower(), len(vs))
    chk(u'durlit_' + TAGS[i].lower(), len(DU[i]))
chk(u'dur_ms_lo', min(min(M[u'durms_' + t.lower()]) for t in TAGS))
chk(u'dur_ms_hi', max(max(M[u'durms_' + t.lower()]) for t in TAGS))
chk(u'dur_ratio', [M[u'dur_ms_hi'] // M[u'dur_ms_lo']])
chk(u'dur_rem', [M[u'dur_ms_hi'] % M[u'dur_ms_lo']])
chk(u'y_dur_wrap', [len([x for x in DU[i] if x[4]]) for i in range(NSRC)])
chk(u'y_dur_wrap_ms', [sorted(set(x[0] for x in DU[i] if x[4])) for i in range(NSRC)])
chk(u'y_unit_used', [sorted(set(x[3] for x in DU[i])) for i in range(NSRC)])
chk(u'y_unit_n', [len(M[u'y_unit_used'][i]) for i in range(NSRC)])
WIN, OUT = [], []
for i in range(NSRC):
    a, b = M[u'sec_off_' + TAGS[i].lower()]
    WIN.append(sorted(set(x[0] for x in DU[i] if x[0] > 0 and a <= x[1] < b)))
    OUT.append(sorted(set(x[0] for x in DU[i] if x[0] > 0 and not (a <= x[1] < b))))
chk(u'y_dur_win', WIN)
chk(u'y_dur_out', OUT)
chk(u'y_dur_win_n', [len(x) for x in WIN])
chk(u'y_dur_out_n', [len(x) for x in OUT])

# ---------- 义务词 / 语汇 / 身份 / 引用 ----------
WK = [(u'dhcp', u'DHCP'), (u'dhcp4', u'DHCPv4'), (u'dhcp6', u'DHCPv6'), (u'solicit', u'Solicit'),
      (u'renew', u'Renew'), (u'rebind', u'Rebind'), (u'inform', u'Information-request'),
      (u'timeout', u'timeout'), (u'timer', u'timer'), (u'backoff', u'backoff'),
      (u'retransword', u'retransmission'), (u'admin', u'administrator'), (u'traffic', u'traffic'),
      (u'interface', u'interface'), (u'server', u'server'), (u'client', u'client')]
for k, s in WK:
    four(u'v_' + k, lambda i, s=s: cnt(TXT[i], s))
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED'):
    four(u'u_' + w.replace(u' ', u'_').lower(), lambda i, w=w: cnt(TXT[i], w))
chk(u'oblig_up', [M[u'u_must'][i] + M[u'u_should'][i] + M[u'u_may'][i] for i in range(NSRC)])
chk(u'y_oblig_win', [M[u'y_secw_may'][i] + M[u'y_secw_must'][i] + M[u'y_secw_should'][i]
                     for i in range(NSRC)])
WT = re.compile(u'[A-Za-z0-9_]+')
for w in (u'must', u'should', u'may'):
    four(u'l_' + w, lambda i, w=w: len([x for x in WT.findall(TXT[i]) if x == w]))
chk(u'oblig_low', [M[u'l_must'][i] + M[u'l_should'][i] + M[u'l_may'][i] for i in range(NSRC)])
four(u'rfc2119_ref', lambda i: cnt(TXT[i], u'2119'))
HK = [(u'cat_std', u'Category: Standards Track'), (u'cat_bcp', u'Category: Best Current Practices'),
      (u'cat_info', u'Category: Informational'), (u'cat_exp', u'Category: Experimental'),
      (u'obs_hdr', u'Obsoletes:'), (u'upd_hdr', u'Updates:'), (u'issn_hdr', u'ISSN:'),
      (u'req_rc', u'Request for Comments:')]
for k, s in HK:
    four(k, lambda i, s=s: cnt(TXT[i], s))
four(u'obsoleted_by', lambda i: cnt(LOW[i], u'obsoleted by'))
CITE = {}
for n in (u'2131', u'2132', u'3315', u'7083', u'8415', u'4941', u'6221', u'7542', u'2119'):
    four(u'cite_' + n, lambda i, n=n: len(re.findall(u'RFC ?' + n + u'(?![' + DIG + u'])', TXT[i])))
    CITE[n] = M[u'cite_' + n]
four(u'cite_3315_sp', lambda i: cnt(TXT[i], u'RFC 3315'))
four(u'cite_3315_ns', lambda i: cnt(TXT[i], u'RFC3315'))
chk(u'cite_ns_3315', [M[u'cite_3315_sp'][i] + M[u'cite_3315_ns'][i] for i in range(NSRC)])
chk(u'y_cite_ledger_3315', [M[u'cite_3315'][i] - M[u'cite_3315_sp'][i] - M[u'cite_3315_ns'][i]
                            for i in range(NSRC)])
chk(u'y_cite_ledger_3315_sum', sum(M[u'y_cite_ledger_3315']))
SELFNUM = (u'2131', u'3315', u'7083', u'8415')
four(u'y_self_lit', lambda i: cnt(TXT[i], SELFNUM[i]))

# ---------- 长行 / 数字行 ----------
NLITS = (u'SOL_MAX_RT', u'64 seconds', u'120', u'3600', u'86400', u'T1', u'T2')
four(u'num_lines', lambda i: len([l for l in LST[i] if len(l.strip()) >= 55
                                  and any(x in l for x in NLITS)]))
for i in range(NSRC):
    chk(u'num_lines_' + TAGS[i].lower(), M[u'num_lines'][i])

GE40, GE40N, GERAW = [], [], []
for i in range(NSRC):
    GE40.append(sorted(set(nrm(l) for l in LST[i]
                           if len(l.strip()) >= 40 and len(nrm(l)) >= 40)))
    GE40N.append(sorted(set(nrm(l) for l in LST[i]
                            if not (H_SP.match(l) or H_NS.match(l) or F_BR.search(l.strip())
                                    or F_OLD.search(l.strip()))
                            and len(l.strip()) >= 40 and len(nrm(l)) >= 40)))
    GERAW.append(sorted(set(l for l in LST[i]
                            if len(l.strip()) >= 40 and len(nrm(l)) >= 40)))
chk(u'lines_ge40', [len(s) for s in GE40])
chk(u'lines_ge40_nos', [len(s) for s in GE40N])
S40 = [set(x) for x in GE40]
S40N = [set(x) for x in GE40N]
for suf, SS in ((u'', S40), (u'_nos', S40N)):
    for a, b in itertools.combinations(range(NSRC), 2):
        chk(u'share_%s%s%s' % (TAGS[a].lower(), TAGS[b].lower(), suf), len(SS[a] & SS[b]))
    chk(u'union_abc' + suf, len(SS[0] | SS[1] | SS[2]))
    chk(u'union_abcd' + suf, len(SS[0] | SS[1] | SS[2] | SS[3]))
    chk(u'only_c' + suf, len(SS[2] - SS[0] - SS[1] - SS[3]))
chk(u'shell_delta', [M[u'lines_ge40'][i] - M[u'lines_ge40_nos'][i] for i in range(NSRC)])
chk(u'union_delta', M[u'union_abcd'] - M[u'union_abc'])
inc = sum(M[u'lines_ge40'])
for a, b in itertools.combinations(range(NSRC), 2):
    inc -= len(S40[a] & S40[b])
for t3 in itertools.combinations(range(NSRC), 3):
    inc += len(S40[t3[0]] & S40[t3[1]] & S40[t3[2]])
inc -= len(S40[0] & S40[1] & S40[2] & S40[3])
chk(u'abcd_incl', inc)
chk(u'abcd_close', M[u'abcd_incl'] - M[u'union_abcd'])
RAWM = [set(x) for x in GERAW]
chk(u'y_bd_byte_shared', len(RAWM[1] & RAWM[3]))
chk(u'y_bd_norm_only', M[u'share_bd'] - M[u'y_bd_byte_shared'])
chk(u'y_cd_byte_shared', len(RAWM[2] & RAWM[3]))
chk(u'y_cd_norm_only', M[u'share_cd'] - M[u'y_cd_byte_shared'])

# ---------- 锚候选池 ----------
SPECIAL = (u'SOL_MAX_RT', u'INF_MAX_RT', u'64 seconds', u'120 secs', u'3600 secs', u'86400',
           u'OLD:', u'NEW:', u'infinity', u'duration_of_lease', u'retransmi', u'60 <=',
           u'MUST ignore any', u'Parameter')
POOLC = []
for i, t in enumerate(TAGS):
    cand = sorted(set(l for l in LST[i]
                      if (len(l) >= 20 or any(x in l for x in SPECIAL)) and nrm(l)))
    for l in cand:
        POOLC.append((t, sum(1 for k in range(NSRC) if nrm(l) in FAN[k]), l))
chk(u'pool_n', len(POOLC))
four(u'pool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
for n in range(1, NSRC + 1):
    chk(u'pool_%d' % n, len([p for p in POOLC if p[1] == n]))
chk(u'pool_tiers', [M[u'pool_%d' % n] for n in range(1, NSRC + 1)])
chk(u'pool_close', sum(M[u'pool_tiers']) - M[u'pool_n'])

# ---------- 锚归属: 双轨成员判据 ----------
TTXT = io.open(ENTRY, encoding=u'utf-8').read()
MARK = u'## ⛓解读注'
# 锚只从条目正文(⟪BabelTele⟫ 及其之前)取, 本注重写自己不能改变锚数——否则第二遍起会把注里的示例当锚
BODY = TTXT[:TTXT.index(MARK)]
CITES = re.findall(u'⟦([A-D])⟧⟨([^⟩]*)⟩', BODY)
DIS4 = sorted(set(q for _, q in CITES))


def stream_hit(tag, anchor):
    """流式拼面: 逐行归一相接, 每批只留末尾 len(锚)-1 字符续接。"""
    na = nrm(anchor)
    if not na:
        return False
    buf, keep = u'', len(na) - 1
    for l in LST[IDX4[tag]]:
        buf += nrm(l)
        if na in buf:
            return True
        if len(buf) > keep:
            buf = buf[-keep:] if keep > 0 else u''
    return False


def line_hit(tag, anchor):
    na = nrm(anchor)
    if not na:
        return False
    ls = [nrm(l) for l in LST[IDX4[tag]]]
    return any(na in u''.join(ls[k:k + w]) for w in range(1, 7) for k in range(len(ls) - w + 1))


IDX4 = dict((t, i) for i, t in enumerate(TAGS))
ATTR, ERR, SPX = {}, [], {}
for q in DIS4:
    hit = [t for t in TAGS if stream_hit(t, q)]
    hit2 = [t for t in TAGS if line_hit(t, q)]
    if hit != hit2:
        ERR.append((q, hit, hit2))
    ATTR[q] = hit
    spans = []
    for t in hit:
        ls = [nrm(l) for l in LST[IDX4[t]]]
        na = nrm(q)
        best = 0
        for w in range(1, 7):
            got = [k for k in range(len(ls)) if k + w <= len(ls) and na in u''.join(ls[k:k + w])]
            if got:
                best = w
                break
        spans.append(best or 6)
    SPX[q] = spans
chk(u'anchor_total', len(CITES))
chk(u'anchor_distinct', len(DIS4))
chk(u'checks', len(DIS4) * NSRC)
for t in TAGS:
    chk(u'tag_' + t, len([x for x in CITES if x[0] == t]))
SIN = len([q for q in DIS4 if len(ATTR[q]) == 1])
CRS = len([q for q in DIS4 if 1 < len(ATTR[q]) < NSRC])
ALL4 = len([q for q in DIS4 if len(ATTR[q]) == NSRC])
chk(u'anchor_single', SIN)
chk(u'anchor_cross', CRS)
chk(u'anchor_all4', ALL4)
chk(u'anchor_err', len(ERR))
assert SIN + CRS + ALL4 == len(DIS4) and not ERR
assert all(len(ATTR[q]) >= 1 for q in DIS4)
POOLN = [nrm(p[2]) for p in POOLC]
assert all(any(nrm(q) in p for p in POOLN) for q in DIS4)
SP1 = len([q for q in DIS4 if max(SPX[q]) == 1])
SP2 = len([q for q in DIS4 if max(SPX[q]) == 2])
SPX3 = len([q for q in DIS4 if max(SPX[q]) >= 3])
MULTI = len([q for q in DIS4 if len(set(SPX[q])) > 1])

# ---------- ⑪恒等式与 DERIV: 算式取自第二遍登记册, 数取自本注 ----------
# 抽取档: 把建条目侧源码 parse 成语法树, 在赋值语句里找 ZID 字面量(不靠行列正则匹配, 也不搬它的数)
ZTREE = ast.parse(io.open(C + u'/_mkB64.py', encoding=u'utf-8').read())
IDENTS = []
for ZT in ast.walk(ZTREE):
    if isinstance(ZT, ast.Assign) and any(getattr(t, u'id', u'') == u'ZID' for t in ZT.targets):
        IDENTS = ast.literal_eval(ZT.value)
assert len(IDENTS) == FLAT[u'x_ident_n'], (len(IDENTS), FLAT[u'x_ident_n'])
GV = lambda k, i=None: (M[k] if i is None else M[k][i])
EENV = {u'GV': GV, u'max': max, u'min': min, u'sum': sum, u'len': len, u'abs': abs, u'round': round,
        u'sorted': sorted, u'set': set, u'list': list, u'int': int, u'float': float, u'pow': pow}
EV = lambda e: eval(e.replace(u'B64V', u'GV'), EENV)
IDENT_BAD = [(e, EV(e)) for e, _ in IDENTS if EV(e) != 0]
assert not IDENT_BAD, IDENT_BAD[:3]
chk(u'x_ident_n', len(IDENTS))
CLOSK = sorted([k for k in FLAT if (u'_close' in k or u'_resid' in k or u'_ledger' in k)
                and isinstance(FLAT[k], (int, float)) and not isinstance(FLAT[k], bool)])
chk(u'scalar_clos_n', len(CLOSK))
chk(u'scalar_clos_sum', sum(M[k] for k in CLOSK))
chk(u'list_clos_n', len([k for k in FLAT if (u'_close' in k or u'_ledger' in k)
                         and isinstance(FLAT[k], list)]))
CLOC = sorted([k for k in FLAT if u'_close' in k])
assert sorted(CH[u'closure_keys']) == CLOC, (CLOC, CH[u'closure_keys'])
DER_KEYS = sorted([k for k in DER if re.match(u'^-?\\d+$', k)], key=lambda x: int(x))
DER_BAD = []
for k in DER_KEYS:
    try:
        v = EV(DER[k])
    except Exception as ex:
        DER_BAD.append((k, repr(ex)))
        continue
    if abs(v - int(k)) > 1e-9:
        DER_BAD.append((k, v, DER[k]))
assert not DER_BAD, DER_BAD[:3]
DER_TXT = []
for k in DER:
    if re.match(u'^-?\\d+$', k):
        continue
    v = EV(DER[k])
    if not (v == k or (not isinstance(v, str) and u'%s' % (v,) == k)):
        DER_TXT.append((k, v))
assert not DER_TXT, DER_TXT[:3]
# 本注下文要举例的三条下标算式先向登记册核实, 不凭记忆写
assert DER[u'4000'] == u"4000*(1-(max([B64V('y_a_first'),B64V('a_seq_ms', 0)])" \
    u"-min([B64V('y_a_first'),B64V('a_seq_ms', 0)])))", DER[u'4000']
assert DER[u'851'] == u"B64V('tbl_start', 1)[0]" and DER[u'1471'] == u"B64V('tbl_start', 3)[0]"
assert u"B64V('durms_a', 2)" in DER[u'60000'] and EV(DER[u'60000']) == 60000

# ---------- 采集侧(第一遍)与本注对账 ----------
COMMON = [k for k in MEAS if k in M]
BADP = [k for k in COMMON if MEAS[k] != M[k]]
assert not BADP, BADP[:5]
UNFLAT = [k for k in FLAT if k not in M]
assert len(SEEN) + 1 + len(UNFLAT) == len(FLAT) and u'sec_num' not in SEEN, (len(SEEN), len(UNFLAT), len(FLAT))
NOTE_ROWS = []


def A(s):
    NOTE_ROWS.append(s)


def r(meth, way, read, keys):
    A(u'| {0} | {1} | {2} | {3} |'.format(meth, way, read, keys))


ANS_MS, ANS_S, UNIT = M[u'y_ans_ms'], M[u'y_ans_s'], M[u'y_ans_unit']
SEQ = M[u'a_seq']
CAP_HI = M[u'clamp_hi'][2]
CAP_LO = M[u'clamp_lo'][2]
r(u'形状⇎序列化', u'行=split 段数并以 count(换行)+1 互证; 非空行两口径按 strip() ⇎ strip(" \\t\\r"); 独占换页行=窄口径非空⇎宽口径空',
  u'字节 {0} ⇎ 字符 {1} ⇎ 行 {2} ⇎ 非空行 {3} ⇎ 宽口径 {4} ⇎ 差 {5}=换页独占行 {6} ⇎ 最长行 {7} ⇎ 签名 {8} 种'.format(
      J(M[u'bytes']), J(M[u'chars']), J(M[u'lines']), J(M[u'nonblank']), J(M[u'nonblank_asciib']),
      J(M[u'nb_gap']), J(M[u'ff_only_lines']), J(M[u'maxlen']), M[u'sig_distinct']),
  u'与 bytes/chars/chars_no_nl/lines/rec_close ⇎ nonblank(_asciib) ⇎ nb_gap/ff_only_lines ⇎ formfeed ⇎ sig(_distinct) 一致; '
  u'四份全 LF、无 BOM、无非 ASCII(各档全 0), 记录闭合 {0}'.format(J(M[u'rec_close'])))
r(u'壳账', u'页眉两式 ^RFC \\d{4} 带题文 ⇎ ^RFC\\d{4} 不带空格; 页脚两式 \\[Page \\d+\\]$ ⇎ 旧式 (\\[|空白)Page \\d+$; '
  u'“[Page ” 子串档用 findall 另立',
  u'页眉 {0}(带空格 {1} ⇎ 无空格 {2}, 账 {3}) ⇎ 页脚 {4}(方括号档同数) ⇎ “[Page ” {5} 处 ⇎ 换页 {6} ⇎ 行尾空格 {7} ⇎ 版面行 {8} ⇎ 估计页 {9}'.format(
      J(M[u'hdr']), J(M[u'hdr_sp']), J(M[u'hdr_ns']), M[u'hdr_ledger_sum'], J(M[u'foot']), J(M[u'pg']),
      J(M[u'formfeed']), J(M[u'trail']), J(M[u'pagelines']), J(M[u'pages_est'])),
  u'与 hdr/hdr_sp/hdr_ns/hdr_ledger_sum ⇎ foot/foot_brk/pg/pagelines/pages_est ⇎ formfeed/trail/nb_gap ⇎ ff_foot_sum/pg_foot_sum 一致; '
  u'四份都靠换页符分页, 页脚=换页=行尾空格=“[Page ”三式逐份全等, 合计闭合 {0}⇎{1}⇎{2}'.format(
      M[u'ff_foot_sum'], M[u'pg_foot_sum'], M[u'nb_ff_sum']))
r(u'答数载体', u'针的第一处命中后紧跟锚定正则 (数)(空白类)(单位族)(?![A-Za-z]); 13 从每处 NEW: 起 96 字符窗内找 SOL_MAX_RT 再读数',
  u'{0} 毫秒 ⇎ 字面 {1} ⇎ 单位 {2} ⇎ 数与单位被排版拆开 {3}; 去重 {4} 枚, 两端比 {5} 倍余 {6}(闭合 {7})'.format(
      J(ANS_MS), J(M[u'y_ans_num']), J(UNIT), J(M[u'y_ans_wrap']), M[u'y_ans_distinct'],
      M[u'y_ans_ratio'], M[u'y_ans_rem'], M[u'y_ans_span_close']),
  u'与 y_ans_ms/num/unit/wrap/s ⇎ y_ans_distinct/max/min/ratio/rem/span_close ⇎ y_bc_ans_gap({0}) ⇎ y_db_ans_gap({1}) ⇎ y_cd_ans_close({2}) 一致'.format(
      M[u'y_bc_ans_gap'], M[u'y_db_ans_gap'], M[u'y_cd_ans_close']))
r(u'翻倍序列仿真', u'从面内现读的首枚延时起每次×2, 直至超过面内封顶即停; 全程无手填常数',
  u'首值 {0} 秒(跨行标志 {1}) ⇎ 下次 {2} 秒 ⇎ 序列 {3} 共 {4} 项 ⇎ 翻倍 {5} 次 ⇎ 末÷首={6}=2^{5}(闭合 {7}); '
  u'末项−封顶 {8} ⇎ 第二项−下次重传 {9} ⇎ 首×比−封顶 {10}'.format(
      M[u'y_a_first'] // 1000, M[u'y_a_first_wrap'], M[u'y_a_next'] // 1000,
      u'→'.join(str(x) for x in SEQ), M[u'a_seq_n'], M[u'a_doublings'], M[u'a_ratio'],
      M[u'a_ratio_pow_close'], M[u'a_seq_close'], M[u'a_seq_next_close'], M[u'a_cap_x_first_close']),
  u'与 a_seq(_ms)/a_seq_n/a_doublings/a_ratio ⇎ a_seq_close/a_seq_next_close/a_ratio_pow_close/a_cap_x_first_close ⇎ '
  u'num_lines_a 一致; 97 面内 “randomized by the value of a uniform” {0}, SOL_MAX_RT 字样 {1}(它没有 v6 的参数名)'.format(
      J(M[u'a_first_lit']), M[u'lit_solmaxrt'][0]))
r(u'参数表切列', u'两条正则: 竖线档 ^\\|([^|]+)\\|\\s*(数)、空白档 ^([A-Z][A-Z0-9_]{2,})\\s+(数); 表头按同行 Parameter+Default 短行, 终止按行首 \\d+\\.\\d+',
  u'表块 {0} 张 ⇎ 行数 {1} ⇎ 表头行 {2} ⇎ 18 比 03 多 {3} 行; 同名参数 {4} 枚: 同值 {5} ⇎ 改值 {6}(闭合 {7}) ⇎ 整除比值列 {8}'.format(
      J(M[u'tbl_n']), M[u'tbl_rows'], M[u'tbl_start'], M[u'tbl_row_delta'], M[u'bd_n'], M[u'bd_same'],
      M[u'bd_diff'], M[u'bd_close'], J(M[u'bd_ratio'])),
  u'与 tbl_n/tbl_rows(_0)/tbl_start/tbl_row_delta ⇎ pv_* ⇎ bd_n/same/diff(_n)/ratio/close/pv_same 一致; '
  u'改动 4 枚里 {0} 是 13 没提的(自改 {1} 枚), 18/03 的 SOL_MAX_RT 之比 {2} 倍'.format(
      J(M[u'bd_unproposed']), M[u'bd_unproposed_n'], M[u'cap_ratio_d_b']))
r(u'OLD:/NEW: 标签配对', u'标签行按 ^\\s*(OLD:|NEW:)\\s*$ 收; 名值从块首行按上面两条正则现取, 无名时退到块内首个长度≥3 的大写串; 行距=两标签行号差',
  u'13 标签 {0} 枚 ⇎ 成对 {1}; 改动参数 {2} ⇎ 比值 {3} ⇎ 行距合计 {4}; 其余三份标签行 {5}'.format(
      M[u'on_n_c'], M[u'on_pair_c'], M[u'on_changed'], M[u'on_ratio'], M[u'on_span'],
      J([M[u'on_n_' + t.lower()] for t in TAGS])),
  u'与 on_pair_/on_n_ ⇎ on_changed(_n) ⇎ on_ratio ⇎ on_span ⇎ on_ratio_cap_close({0}) 一致——提案的 30 倍与标准的表间 30 倍是同一枚数; '
  u'两对无秒数的配对是 13 的散文替换(MUST/If 段)'.format(M[u'on_ratio_cap_close']))
r(u'可下发 ⇎ 越界即弃', u'一条 (\\d+)\\s*<= "value" <=\\s*(\\d+) 同取上下界(建条目侧是 num_before/num_after 两趟走位); 弃置句按字面 findall',
  u'值域 {0}..{1}(比 {2} 倍, 闭合 {3}) ⇎ C⇎D 上下界各自闭合 {4}⇎{5} ⇎ 字面 “60 <= "value" <= 86400” {6} ⇎ '
  u'“or more than 86400” {7} ⇎ MUST ignore any {8}(SOL {9} ⇎ INF {10}); 存活期句 {11} ⇎ 接口句 {12} ⇎ 同值跨 IA {13}'.format(
      J(M[u'clamp_lo']), J(M[u'clamp_hi']), M[u'clamp_span'], M[u'clamp_span_close'],
      M[u'clamp_cd_lo_close'], M[u'clamp_cd_hi_close'], J(M[u'y_clamp_lit']), J(M[u'y_clamp_86400']),
      J(M[u'y_must_ignore_n']), J(M[u'y_ignore_srt']), J(M[u'y_ignore_inf']),
      J(M[u'lit_retain']), J(M[u'lit_iface']), J(M[u'lit_sameacross'])),
  u'与 clamp_lo/hi/span/span_close ⇎ clamp_cd_* ⇎ y_clamp_lit/y_clamp_86400 ⇎ y_ignore_srt/y_ignore_inf/y_must_ignore_n ⇎ '
  u'lit_retain(_sp)/lit_iface/lit_sameacross 一致; 13 提出可下发却一条覆盖约束都没写(0⇎0⇎0⇎1⇎2)')
r(u'夹逼句逐行对照', u'含 60 <= "value" 的行按出现次序配对, 逐字节 ⇎ 归一(re.sub 去非 a-z0-9) ⇎ 字符净差三档',
  u'配对 {0} 行 ⇎ 字节全等 {1} ⇎ 仅标点差 {2} ⇎ 归一也不同 {3}(闭合 {4}) ⇎ 净增 {5} 字符'.format(
      M[u'al_n'], M[u'al_same_bytes'], M[u'al_punct_only'], M[u'al_norm_diff'], M[u'al_close'],
      M[u'al_char_delta']),
  u'与 y_cd_lines/al_n/same_bytes/punct_only/norm_diff/close/char_delta 一致——标准复写提案时改的是措辞与角标, 不是数')
r(u'时长归一毫秒', u'一条正则收非重叠 token (\\d[\\d,]*)(空白类)(单位族)(?![A-Za-z]), 单位族按长名先试; 跨行标志查组 2 里有无换行',
  u'取值集 {0} ⇎ 出现处 {1} ⇎ 单位种数 {2}({3}) ⇎ 跨行 token {4} 枚(值 {5}); 全库两端 {6}⇎{7} 毫秒 = 比 {8} 倍余 {9}'.format(
      J([M[u'durms_' + t.lower()] for t in TAGS]), J([M[u'durlit_' + t.lower()] for t in TAGS]),
      J(M[u'y_unit_n']), J(M[u'y_unit_used']), J(M[u'y_dur_wrap']), M[u'y_dur_wrap_ms'],
      M[u'dur_ms_lo'], M[u'dur_ms_hi'], M[u'dur_ratio'][0], M[u'dur_rem'][0]),
  u'与 durms_/durlit_ ⇎ dur_ms_lo/hi/ratio/rem ⇎ y_dur_wrap(_ms) ⇎ y_unit_used/n 一致; 窗档 {0} 枚内 ⇎ {1} 枚外'
  u'——97 窗外的 60000 毫秒是 v4 别的定时器(退避/重绑), 与封顶无关'.format(J(M[u'y_dur_win_n']), J(M[u'y_dur_out_n'])))
r(u'规范窗⇎窗外', u'全篇编号标题一次收成行号→编号表(本注按正则 ^\\d+(\\.\\d+)*\\.? 空白 词, 尾点可省), 答数行回溯最近标题为窗起, '
  u'下一处编号标题为窗止(同题 ⇎ 前缀同族两式否判); 窗内用起点位置表筛, 窗外=总数−窗内',
  u'窗 {0} ⇎ 编号 {1} ⇎ 标题 {2} ⇎ 窗长 {3} ⇎ needle 窗内命中 {4}; SOL_MAX_RT 窗内 {5} ⇎ 窗外 {6} ⇎ “86400” 窗内 {7} ⇎ 窗外 {8} ⇎ '
  u'“120 secs” 窗内 {9} ⇎ 窗外 {10} ⇎ “3600 secs” 窗内 {11} ⇎ 窗外 {12}'.format(
      M[u'sec_w'], J(M[u'sec_num']), J(M[u'sec_head']), J(M[u'sec_len']), J(M[u'sec_hit']),
      J(M[u'secw_solmaxrt']), J(M[u'outw_solmaxrt']), J(M[u'secw_v86400']), J(M[u'outw_v86400']),
      J(M[u'secw_s120']), J(M[u'outw_s120']), J(M[u'secw_s3600']), J(M[u'outw_s3600'])),
  u'与 sec_w/a/b/num/head/len(_t)/off(_t)/sec_hit ⇎ secw_/outw_ 八族一致(逐族闭合 {0}); 编号串的写法差异在本注申报: '
  u'本注收 4.1 ⇎ 5.5 ⇎ 3 ⇎ 7.6, 建条目侧的逐字符档写作 {1}(点号重复), 折叠后同值——同一枚标题、两把尺'.format(
      J([M[u'secw_' + k][i] + M[u'outw_' + k][i] - M[u'lit_' + k][i] for k, _ in WINS for i in range(NSRC)][:8]),
      J(FLAT[u'sec_num'])))
r(u'折行两档', u'原面档按转义 findall, 折平档把整篇空白类压成单空格再 findall; 差=该行被排版折断的处数',
  u'主线 {0} 枚针里 {1} 枚有差, 合计 {2} 处——97 的封顶句(wrapgap_max64sp {3}) ⇎ 18 的保留句(wrapgap_retainfull {4}); '
  u'次轴 {5} 枚针 {6} 枚有差, 合计 {7} 处: 97 的 T2 缺省式原面 {8} ⇎ 折平 {9}'.format(
      M[u'wrap_sn_n'], M[u'wrap_sn_hit'], M[u'wrap_sn_total'], M[u'wrapgap_max64sp'][0],
      M[u'wrapgap_retainfull'][3], M[u'wrap_pin_n'], M[u'wrap_pin_hit'], M[u'wrap_total'],
      M[u'lit_durdef875'][0], M[u'lit_durdef875_fold'][0]),
  u'与 s_*/s_*_fold/wrapgap_*(11 族) ⇎ n_*/n_*_fold/wrap_*(6 族) ⇎ wrap_sn_n/hit/total ⇎ wrap_pin_n/hit/total ⇎ '
  u'lit_durdef875(_fold/_gap/_gap_sum) 一致; 逐针差全表 {0}'.format(
      J([sum(M[u'wrapgap_' + k]) for k, _ in SN])))
r(u'义务词两档 ⇎ 窗内', u'全大写族按转义 findall(故 MUST 一档含 "MUST NOT" 之内的), 小写族按 [A-Za-z0-9_]+ 词流整词相等; 窗内改按位置筛',
  u'MUST {0} ⇎ SHOULD {1} ⇎ MAY {2} ⇎ MUST NOT {3} ⇎ REQUIRED {4} ⇎ 三词合计 {5}; must {6} ⇎ should {7} ⇎ may {8} ⇎ 合计 {9}; '
  u'窗内三词合计 {10} ⇎ 窗外 MUST {11}'.format(
      J(M[u'u_must']), J(M[u'u_should']), J(M[u'u_may']), J(M[u'u_must_not']), J(M[u'u_required']),
      J(M[u'oblig_up']), J(M[u'l_must']), J(M[u'l_should']), J(M[u'l_may']), J(M[u'oblig_low']),
      J(M[u'y_oblig_win']), J(M[u'y_outw_must'])),
  u'与 u_*/l_*/oblig_up/oblig_low ⇎ y_secw_*/y_outw_*/y_oblig_win 一致——97 的答数句挂 SHOULD(散文), '
  u'18 的答数只是表里一个数, 它的义务句全在窗外那一节')
r(u'语汇⇎引用⇎身份', u'字面 findall; 引用号一条 RFC ?编号(?!数字) 收全; 自编号子串另立; 抬头八族各按字面',
  u'SOL_MAX_RT {0} ⇎ INF_MAX_RT {1} ⇎ IRT {2} ⇎ SRT−IRT {3} ⇎ retransmi {4} ⇎ Solicit {5} ⇎ timeout {6} ⇎ backoff {7}; '
  u'引 2131 {8} ⇎ 3315 {9}(带空格 {10} ⇎ 黏写 {11}, 账 {12}) ⇎ 7083 {13} ⇎ 8415 {14} ⇎ 2119 {15}; '
  u'面内自编号 {16} 处'.format(
      J(M[u'lit_solmaxrt']), J(M[u'lit_infmaxrt']), J(M[u'lit_irt']), J(M[u'lit_srt_minus_irt']),
      J(M[u'lit_retrans']), J(M[u'v_solicit']), J(M[u'v_timeout']), J(M[u'v_backoff']),
      J(CITE[u'2131']), J(CITE[u'3315']), J(M[u'cite_3315_sp']), J(M[u'cite_3315_ns']),
      M[u'y_cite_ledger_3315_sum'], J(CITE[u'7083']), J(CITE[u'8415']), J(CITE[u'2119']),
      J(M[u'y_self_lit'])),
  u'与 v_*/lit_*/cite_*(9 号) ⇎ cite_3315_sp/ns/cite_ns_3315/y_cite_ledger_3315(_sum) ⇎ y_self_lit ⇎ '
  u'cat_std({0}) ⇎ obs_hdr({1}) ⇎ upd_hdr({2}) ⇎ obsoleted_by({3}) ⇎ issn_hdr({4}) 一致; '
  u'13 引 03 {5} 次零次引 18(它早五年), 18 引 13 {6} 次把提案收进标准'.format(
      J(M[u'cat_std']), J(M[u'obs_hdr']), J(M[u'upd_hdr']), J(M[u'obsoleted_by']), J(M[u'issn_hdr']),
      CITE[u'3315'][2], CITE[u'7083'][3]))
r(u'整行搬运', u'归一 re.sub 去非 a-z0-9; 交用集合运算符 &、并集用 |、only 用集合差; 字节档另按原行串; 容斥按 1−3+3−1 阶本注列齐',
  u'两两 {0} ⇎ 三份并集 {1} ⇎ 四份并集 {2} ⇎ 加进 18 多 {3} 行 ⇎ 容斥−并集 {4}; 只在本份 13 {5} 行 ⇎ 去壳只挪 {6} 行; '
  u'03⇎18 字节档 {7} ⇎ 仅归一同 {8} ⇎ 13⇎18 字节档 {9} ⇎ 仅归一同 {10}'.format(
      J([M[u'share_%s%s' % (TAGS[a].lower(), TAGS[b].lower())]
         for a, b in itertools.combinations(range(NSRC), 2)]), M[u'union_abc'], M[u'union_abcd'],
      M[u'union_delta'], M[u'abcd_close'], M[u'only_c'], J(M[u'shell_delta']),
      M[u'y_bd_byte_shared'], M[u'y_bd_norm_only'], M[u'y_cd_byte_shared'], M[u'y_cd_norm_only']),
  u'与 share_*(六对×两档) ⇎ union_abc/abcd(_nos) ⇎ union_delta ⇎ only_c(_nos) ⇎ lines_ge40(_nos) ⇎ shell_delta ⇎ '
  u'abcd_incl/close ⇎ y_bd_*/y_cd_* 一致; 含关键数字的长行 {0} 行'.format(J(M[u'num_lines'])))
r(u'锚池⇎归属', u'池按“整篇归一串含这条锚的份数”分四档; 归属判据双轨: ①逐行流式拼归一面(每批只留末尾 len(锚)−1 字符续接) '
  u'②单行 ⇎ 相邻两行拼接; 两式必须同判, 另按 1..6 行滑窗求锚的最小行跨度',
  u'池 {0} 条分档 {1}(逐份 {2}, 闭合 {3}); 锚 {4} 处／去重 {5} 串／一源 {6} ⇎ 两至三源 {7} ⇎ 四源 {8} ⇎ 错配 {9} ⇎ 检查 {10} 次; '
  u'标签 A⇎B⇎C⇎D 各 {11} 处; 压一行 {12} ⇎ 两行 {13} ⇎ 三行以上 {14}, 同一锚跨源跨度不同 {15} 串'.format(
      M[u'pool_n'], J(M[u'pool_tiers']), J(M[u'pool_tag_n']), M[u'pool_close'], M[u'anchor_total'],
      M[u'anchor_distinct'], M[u'anchor_single'], M[u'anchor_cross'], M[u'anchor_all4'], M[u'anchor_err'],
      M[u'checks'], J([M[u'tag_' + t] for t in TAGS]), SP1, SP2, SPX3, MULTI),
  u'与 pool_n/pool_1..4/pool_tiers/pool_close/pool_tag_n ⇎ anchor_*/checks/tag_* 一致; 去重的 {0} 串全部来自池中'
  u'(池中实际用作锚 {1} 条)'.format(M[u'anchor_distinct'], CH[u'pool_used']))
r(u'恒等式⇎DERIV', u'27 条恒等式的算式由语法树在建条目侧源码里现取(ZID 字面量, 只搬算式不搬数), '
  u'{0} 条 DERIV 算式取自 corpus/_deriv64.json; 两条通道都用本注的读数求值——算式是第二遍的宣称, 数是第四遍现测'.format(len(DER)),
  u'恒等式 {0} 条全部为真(3 600 000={1}×{2}+{3} ⇎ 64→8→…→64=2^{4} ⇎ {5}×30={6} ⇎ 值域 {7}..{8} ⇎ '
  u'页眉两式=并档 ⇎ 换页=页脚=行尾空格=“[Page ”); DERIV 数值键 {9} 条按本注读数重算全对 ⇎ '
  u'字面值键 {10} 条(表头行号 ⇎ 序列 ⇎ 值集 ⇎ 单位名 ⇎ 标题串)按 str(读数)==键 复算全对; '
  u'标量闭合 {11} 项(合计 {12})⇎清单闭合 {13} 项; 整串打印的列表元素各自补下标算式'
  u'(4 000=B64V(\'y_a_first\') ⇎ 851/1 471=B64V(\'tbl_start\', i)[0] ⇎ 60 000=B64V(\'durms_a\', 2))'.format(
      M[u'x_ident_n'], M[u'y_ans_ratio'], M[u'y_ans_min'], M[u'y_ans_rem'], M[u'a_doublings'],
      M[u'y_ans_s'][1], M[u'y_ans_s'][3], M[u'dur_ms_lo'], M[u'dur_ms_hi'], len(DER_KEYS),
      len(DER) - len(DER_KEYS), M[u'scalar_clos_n'], M[u'scalar_clos_sum'], M[u'list_clos_n']),
  u'与 x_ident_n ⇎ scalar_clos_n/sum ⇎ list_clos_n ⇎ DERIV 全部键一致; 扁平契约 {0} 键里本注逐键 assert 同值 {1} 个 ⇎ '
  u'sec_num 1 个按折叠等式比对 ⇎ 余 {2} 个是派生键(走 DERIV 通道复算), 原测键零缺漏'.format(
      len(FLAT), len(SEEN), len(UNFLAT)))
r(u'两侧对账', u'采集侧 {0} 键在四份面上逐键与本注比(本注不参与其算法)'.format(len(MEAS)),
  u'共有 {0} ／ 不符 {1} ⇎ 扁平 {2} 键 = 逐键同值 {3} + 折叠等式 1 + 派生 {4}(三档相加闭合 {5})'.format(
      len(COMMON), len(BADP), len(FLAT), len(SEEN), len(UNFLAT),
      len(SEEN) + 1 + len(UNFLAT) - len(FLAT)),
  u'97⇎03⇎13⇎18 是同一问题的四种载体: 散文句 ⇎ 表行 ⇎ 提案重印 ⇎ 表+选项+丢弃句; 分页壳四份同族(全 LF、无 BOM)')

A(u'')
A(u'### 读法')
A(u'')
A(u'一、四个答数写在四种载体里, 倍差却最大: {0} 毫秒是 {1} 毫秒的 {2} 倍余 {3}。97 把它埋在散文里——同一段先给首枚延时 {4} 秒, '
  u'再要求“每次翻倍”, 于是 64 秒不是孤立字面而是序列末项({5} 共 {6} 项, 末÷首={7}=2^{8}); '
  u'03 把它钉成参数表里的一行(“120 secs”全文 {9} 处, 恰是 SOL ⇎ INF 两行, 客户端无从改变); '
  u'13 不进表, 它把 03 那两行用 OLD:/NEW: 原样重印再改(比值 {10}); 18 收下 {11} 秒却来自表({12} 行)。'
  u'问“封顶在哪一秒”, 97 答的是自己翻倍的上限, 03/13/18 答的是 SOL_MAX_RT——同名不同量, 得先问管哪一步。'
  .format(M[u'y_ans_max'], M[u'y_ans_min'], M[u'y_ans_ratio'], M[u'y_ans_rem'], M[u'y_a_first'] // 1000,
          u'→'.join(str(x) for x in SEQ), M[u'a_seq_n'], M[u'a_ratio'], M[u'a_doublings'],
          M[u'lit_s120'][1], M[u'cap_ratio_d_b'], M[u'y_ans_s'][3], M[u'tbl_rows_0'][3]))
A(u'二、提案只改两枚, 标准落地四枚: 18 与 03 都有值的同名参数 {0} 枚, 同值 {1} ⇎ 改动 {2}(闭合 {3}), '
  u'其中 {4} 由 120→3600(比值 {5}), 另两枚 {6} 由 5→4 是 18 自己改的、13 通篇没提(自改 {7} 枚)。'
  u'13 的 {8} 枚标签行成对解出 4 对: 前缀/后缀两对只是散文替换, 无秒数; 行距合计 {9}。'
  u'提案的 30 倍与标准的表间 30 倍是同一枚数(闭合 {10})——这是全条最硬的一根桥: 一年前的“建议”与五年后的“缺省”在同一格对上。'
  .format(M[u'bd_n'], M[u'bd_same'], J(M[u'bd_diff']), M[u'bd_close'],
          u' ⇎ '.join(x[0] for x in M[u'bd_diff'][:2]), M[u'cap_ratio_d_b'],
          u' ⇎ '.join(M[u'bd_unproposed']), M[u'bd_unproposed_n'], M[u'on_n_c'], M[u'on_span'],
          M[u'on_ratio_cap_close']))
A(u'三、可下发不等于照收: 18 在收下 13 的选项时写下夹逼 {0}..{1}(比 {2} 倍, 上下界与 13 各自闭合 {3}⇎{4}), '
  u'并规定越界即弃 ⟦D⟧⟨A DHCP client MUST ignore any SOL_MAX_RT option values that are less⟩(现读 SOL {5} ⇎ INF {6} 处, '
  u'同份 MUST ignore any 共 {7} 处, 而 13 只 {8} 处)。它还独有两条例外: 值要留住 ⟦D⟧⟨this value is expected to be retained⟩({9} 处) '
  u'⇎ 只在触发它的那块接口生效({10} 处)——提案只改数值, 标准还得回答“这条覆盖算谁的、算多久”。'
  u'两句在 13 都缺({11}⇎{12} 处)。复写也不是逐字: 含夹逼式的行两份各 {13} 行, 配对 {14} 行里字节全等 {15} ⇎ 仅标点差 {16} ⇎ '
  u'归一也不同 {17}, 净增 {18} 字符——改的是措辞与角标。'
  .format(CAP_LO, CAP_HI, M[u'clamp_span'], M[u'clamp_cd_lo_close'], M[u'clamp_cd_hi_close'],
          M[u'y_ignore_srt'][3], M[u'y_ignore_inf'][3], M[u'y_must_ignore_n'][3], M[u'y_must_ignore_n'][2],
          M[u'lit_retain'][3], M[u'lit_iface'][3], M[u'lit_retain'][2], M[u'lit_iface'][2],
          M[u'y_cd_lines'][0], M[u'al_n'], M[u'al_same_bytes'], M[u'al_punct_only'], M[u'al_norm_diff'],
          M[u'al_char_delta']))
A(u'四、次轴“多久去续租”换了基准: 97 写 T1=0.5×duration_of_lease ⇎ T2=0.875×同一标识符(全篇 {0} 处), 其 T2 式被排版劈在两行'
  u'(原面 {1} 处 ⇎ 折平 {2} 处)——不折平的复算者会读成 0 处并断言“97 没写 T2 缺省式”。'
  u'v6 三份改用 shortest preferred lifetime 作基准({3}⇎{4}⇎{5} 处)并把 T1/T2 交给服务器下发; '
  u'“infinity”一族的两种写法 {6} ⇎ {7} 处, 97 把它用在无限租约那一行。97 窗外的时长 {8} 毫秒属于 v4 别的定时器, '
  u'把整篇值域当答案会读出另一个问题: 全库 {9}..{10} 毫秒, 比 {11} 倍余 {12}。'
  .format(M[u'lit_durword'][0], M[u'lit_durdef875'][0], M[u'lit_durdef875_fold'][0],
          M[u'lit_preferre'][1], M[u'lit_preferre'][2], M[u'lit_preferre'][3],
          J(M[u'lit_infin']), J(M[u'lit_ffffffff']), J(M[u'y_dur_out'][0]),
          M[u'dur_ms_lo'], M[u'dur_ms_hi'], M[u'dur_ratio'][0], M[u'dur_rem'][0]))
A(u'五、壳在这里比内容更能骗人: 四份全靠换页符分页({0}⇎{1}⇎{2}⇎{3} 页), 页脚=换页符=行尾空格=“[Page ”子串四式逐份全等'
  u'(合计闭合 {4}⇎{5}); 非空行有两个口径——按 isspace 判空 {6}, 只认空格/制表/回车 {7}, 差 {8} 恰是换页符独占行 {9}(闭合 {10})。'
  u'自编号另有两条隐形通道: 18 面内 “8415” {11} 处, 其中每页重印的带空格页眉就占 {12} 行; 03 面内 “3315” {13} 处 ⇎ '
  u'带空格式 {14} ⇎ 黏写式 {15}(两式相加与引用总数逐份闭合 {16})。义务词也不成差轴: 三词合计 {17}, '
  u'而 18 的答数行只是表里一个数——窗内三词合计 {18}(97 的答数句挂 SHOULD 写在散文里, 13⇎18 的窗只吞下表行)。'
  .format(M[u'formfeed'][0], M[u'formfeed'][1], M[u'formfeed'][2], M[u'formfeed'][3],
          M[u'ff_foot_sum'], M[u'pg_foot_sum'], J(M[u'nonblank']), J(M[u'nonblank_asciib']),
          J(M[u'nb_gap']), J(M[u'ff_only_lines']), M[u'nb_ff_sum'],
          M[u'y_self_lit'][3], M[u'hdr'][3], M[u'cite_3315'][1], M[u'cite_3315_sp'][1], M[u'cite_3315_ns'][1],
          M[u'y_cite_ledger_3315_sum'], J(M[u'oblig_up']), J(M[u'y_oblig_win'])))
A(u'')
A(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
A(u'')
A(u'① 四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; ② rfc-editor.org 此刻给这四份挂的类目与状态页——库内抬头只印 '
  u'Category: Standards Track {0}⇎{1}⇎{2}⇎{3} 行 ⇎ Obsoletes 头 {4}⇎{5}⇎{6}⇎{7}(97 一枚 ⇎ 18 废止 03) ⇎ '
  u'Updates 头 {8}⇎{9}⇎{10}⇎{11}(只有 13 写它更新 03) ⇎ 正文 “obsoleted by” 字样 {12} 处全在 18 的对照附录; '
  u'③ 勘误表是否已把 03 的 §5.5 或 18 的表行改成别的数; '
  u'④ 各家 DHCP 客户端把 SOL_MAX_RT 实际记多久(掉电、重启、换接口之后是否仍留住), 以及它是否真按 18 的接口作用域实现——属站外核验; '
  u'⑤ 3600 秒的缺省在真实网络里是否真如 13 所说“显著减少聚合流量”, 以及服务器下发的值在现网分布到哪儿——文书只给结论不给测量。'
  u'这些都不进判词与门槛。'
  .format(M[u'cat_std'][0], M[u'cat_std'][1], M[u'cat_std'][2], M[u'cat_std'][3],
          M[u'obs_hdr'][0], M[u'obs_hdr'][1], M[u'obs_hdr'][2], M[u'obs_hdr'][3],
          M[u'upd_hdr'][0], M[u'upd_hdr'][1], M[u'upd_hdr'][2], M[u'upd_hdr'][3],
          sum(M[u'obsoleted_by'])))
A(u'')
A(u'### 编码与门的账')
A(u'')
A(u'编码区 {0} 字符(不含换行); 锚 {1} 处 ⇎ 去重 {2} 串 ⇎ 归属检查 {3} 次 ⇎ 错配 {4}; '
  u'一源 {5} ⇎ 两至三源 {6} ⇎ 四源 {7}; 标签 A⇎B⇎C⇎D 各 {8}⇎{9}⇎{10}⇎{11} 处。'
  .format(CH[u'enc_chars'], M[u'anchor_total'], M[u'anchor_distinct'], M[u'checks'], M[u'anchor_err'],
          M[u'anchor_single'], M[u'anchor_cross'], M[u'anchor_all4'],
          M[u'tag_A'], M[u'tag_B'], M[u'tag_C'], M[u'tag_D']))
A(u'DERIV {0} 键 ⇎ 复算点 {1} 处 ⇎ 同数共键 {2} 组 ⇎ 0 折 {3} 项; 扁平键 {4} 个(本注逐键同值 {5} 个 ⇎ 折叠等式比对的 1 个 ⇎ 余 {6} 个为派生键); '
  u'闭合账 标量 {7} 项(合计 {8})⇎ 清单 {9} 项 ⇎ 面内恒等式 {10} 条; 锚候选池 {11} 条按逐字再现份数分 4 档({12}), 分档闭合 {13}, '
  u'池中实际用作锚 {14} 条。'
  .format(CH[u'deriv_keys'], CH[u'deriv_points'], len(CH[u'collisions']), CH[u'zero_terms'],
          len(FLAT), len(SEEN), len(UNFLAT),
          M[u'scalar_clos_n'], M[u'scalar_clos_sum'], M[u'list_clos_n'], M[u'x_ident_n'],
          M[u'pool_n'], u'⇎'.join(str(x) for x in M[u'pool_tiers']), M[u'pool_close'], CH[u'pool_used']))
A(u'门槛三遍: T1 字面逐锚回原文 ⇎ T2 DERIV 每条算式重跑 ⇎ T3 码位与字母账; '
  u'本注另加第四遍复测, 上表 {0} 行全部 assert(含 {1} 条 DERIV 算式与 27 条恒等式按本注读数重算), 不符即停机。'
  .format(len(NOTE_ROWS), len(DER)))
NOTE = NL.join(NOTE_ROWS)
assert not re.findall(u'%[sdifg]|%\\(', NOTE)
HEAD = TTXT[:TTXT.index(u'## ⛓解读注') + len(u'## ⛓解读注')]
io.open(ENTRY, 'w', encoding=u'utf-8', newline=NL).write(HEAD + NL + NL + NOTE + NL)
print(u'⛓解读注已写 %d 字符 ｜ 第四遍 assert 全过 ｜ 复测 %d/%d 扁平键 ｜ 采集对账 %d 键 0 不符 ｜ '
      u'恒等式 %d 条 ⇎ DERIV %d 条按本注读数重算全对 ｜ 锚 %d 处／去重 %d 串／错配 %d'
      % (len(NOTE), len([k for k in FLAT if k in M]), len(FLAT), len(COMMON), M[u'x_ident_n'],
         len(DER), M[u'anchor_total'], M[u'anchor_distinct'], M[u'anchor_err']))
