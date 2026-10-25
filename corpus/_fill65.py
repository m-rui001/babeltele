# -*- coding: utf-8 -*-
"""B65 ⛓解读注(第四遍): 本注每个数都是现测并 assert 的, 不手填。
四套实现: 采集侧 corpus/_pick65.py(正则族收针与义务词、集合运算求搬运、按行切表)
⇎ 建条目侧 corpus/_mkB65.py(游标档 find 循环、逐字符形状档、句内游标解析上限、bisect 档求交、窗口按标题行定位,
  扁平契约 corpus/_b65flat.json)
⇎ 门槛侧 corpus/audit.py::_b65_scan()(由 corpus/_wire65.py 从 SCAN 段机械抽出, 插门前把全部扁平键与 DERIV 算式逐条预演)
⇎ 本注第四遍, 与前三遍都换算法不换定义:
①形状档走字符串法: 行数用 len(split) ⇎ count(换行)+1 两式互证, 非空行按 l.strip() 真值, 宽口径按 strip(' \\t\\r'),
  独占换页符的行按“宽口径非空 ⇎ 窄口径空”两条同时成立筛出, 最长行用 max(len)、行尾空格用 l != l.rstrip();
②字面档一律 re.findall(re.escape(针)) (建条目侧是 find 循环逐处数), 折平档先把针做 ' '.join(split()) 再在同一函数里数;
③上限数字由锚定正则 (AT MOST|more than)[ \\t]+(\\d+) 现读(建条目侧是逐字符走位连读), 读数只取首个带数字的命中;
④节窗档: 标题行用 (?m)^[ \\t]*前缀\\.?[ \\t]+标题 一条正则收全份(目录行也在内), 窗取最后一枚, 止行用
  ^[ \\t]*[0-9.]+[ \\t]+大写起头 且长度<46 且不含 '...' 的下一枚标题; 窗外不是“总数减窗内”而是行表切片拼接;
⑤义务词两档: 全大写族按 findall(转义) 故 MUST 一档含 "MUST NOT" 内的那枚, 全小写族按词流 [A-Za-z][A-Za-z0-9_]* 整词相等;
⑥搬运账归一只留 a-z0-9(re.sub), 交用集合 &、并用 |, 四元容斥按 1−3+3−1 阶由本注自己列齐;
⑦表外两把尺: 含页壳 ⇎ 去页壳(页眉两式 ⇎ 页脚一式判定后剔除), 逐字节档不归一, 与归一档之差即“仅归一同”;
⑧断行档: 行尾连字符行数与“其下一行以小写字母续写”的行数各按行表筛, server-side ⇎ "server- side" 两式并档;
⑨引用档: RFC 号由 \\bRFC[ ]?(\\d{4})(?!\\d) 一次收全, 自编号−页眉即“真引用”账; [RFC nnnn] 具名方括号档按位置配对右括号;
⑩锚池按“归一长行压在几份里”分层(集合运算); 四份同现者回原面取逐字节交集(本注用四份行集 dict 交, 建条目侧用逐面清单顺次交), 再拿三把写法尺(忽略大小写 ⇎ 去连字符 ⇎ 折空格)判差异落在哪一根轴上——一根长行只许差在一根轴上, 差两根即停机;
⑪恒等式与 DERIV 的账: 52 条恒等式的算式由 ast.parse 在建条目侧源码的赋值语句里现取(ZID 字面量, 只搬算式不搬数),
  全部 DERIV 算式取自 corpus/_deriv65.json, 两条通道都用**本注的读数**求值——算式是第二遍的宣称, 数是第四遍现测的;
⑫锚归属由条目正文 ⟦标签⟧⟨引文⟩ 配对现推, 成员判据双轨: ①逐行流式拼归一面(每批只留末尾 len(锚)−1 字符续接)
  ②单行表 ⇎ 相邻两行拼接表按子串判; 两式必须同判; 另求“这枚锚最少压在几行上”(1..6 行滑窗)得行跨度分布。
不可由在库文件判定的只写在本注: 四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧、rfc-editor.org 此刻给这四份挂的状态页与
Obsoletes/Updates 图、勘误表是否已改动 2616 的 §8.1.4、各家浏览器对同一域名实际同时开几条连接、
现网服务器把空闲超时配成多少秒、以及 2 条上限在真实客户端里是否还被遵守——都不进判词与门槛。
"""
import io, os, re, sys, json, ast, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
TAGS = [u'A', u'B', u'C', u'D']
LB = dict(zip(TAGS, [u'97 最多二', u'99 不得超', u'14 撤上限', u'22 同句撤']))
NSRC = 4
IDX = dict((t, i) for i, t in enumerate(TAGS))
PATH = [C + u'/raw/httpKA/rfc2068.txt', C + u'/raw/httpKA/rfc2616.txt',
        C + u'/raw/httpKA/rfc7230.txt', C + u'/raw/httpKA/rfc9112.txt']
ENTRY = C + u'/babeltele/B65_http_connection_ceiling_four_answers.md'
FLAT = json.load(io.open(C + u'/_b65flat.json', encoding=u'utf-8'))
CH = json.load(io.open(C + u'/_b65checks.json', encoding=u'utf-8'))
MEAS = json.load(io.open(C + u'/_b65meas.json', encoding=u'utf-8'))
DER = json.load(io.open(C + u'/_deriv65.json', encoding=u'utf-8'))
J = lambda xs: u'⇎'.join(str(x) for x in xs)


def nrm(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


RAWB = [io.open(p, 'rb').read() for p in PATH]
TXT = [r.decode('utf-8-sig') for r in RAWB]
LST = [t.split(NL) for t in TXT]
LOW = [t.lower() for t in TXT]
FO = [u' '.join(t.split()) for t in TXT]
FAN = [nrm(t) for t in TXT]
M = {}
MIS = []
SEEN = set()


def chk(name, val):
    """本注现测值与扁平契约对拍; 键在采集表里时一并再比一次。"""
    val = list(val) if isinstance(val, (list, tuple)) else val
    if name in FLAT:
        if FLAT[name] != val:
            raise AssertionError((name, FLAT[name], val))
    else:
        MIS.append((u'缺键', name, None))
    if name in MEAS and MEAS[name] != val:
        raise AssertionError((u'pick', name, MEAS[name], val))
    M[name] = val
    SEEN.add(name)
    return val


def four(name, f, n=NSRC):
    return chk(name, [f(k) for k in range(n)])


def cnt(t, needle):
    return len(re.findall(re.escape(needle), t))


def occ(t, needle):
    return cnt(t, needle)


def posn(t, needle):
    return [m.start() for m in re.finditer(re.escape(needle), t)]


# ---------- 抽取档: 建条目侧的针表与登记册由语法树现取(只搬定义不搬数) ----------
TREE = ast.parse(io.open(C + u'/_mkB65.py', encoding=u'utf-8').read())
DEF = {}
for ND in ast.walk(TREE):
    if isinstance(ND, ast.Assign):
        for t in ND.targets:
            if isinstance(t, ast.Name) and t.id in (
                    u'LITK', u'SN', u'SECP', u'CCH', u'RULE', u'NLITS', u'SELFN', u'HK', u'WK', u'SPECIAL', u'ZID'):
                try:
                    DEF[t.id] = ast.literal_eval(ND.value)
                except Exception:
                    pass
for nm in (u'LITK', u'SN', u'SECP', u'CCH', u'RULE', u'NLITS', u'SELFN', u'HK', u'WK', u'SPECIAL', u'ZID'):
    assert nm in DEF, nm
LITK, SN, SECP, CCH = DEF[u'LITK'], DEF[u'SN'], DEF[u'SECP'], DEF[u'CCH']
RULE, NLITS, SELFN, HK, WK, SPECIAL = (DEF[u'RULE'], DEF[u'NLITS'], DEF[u'SELFN'], DEF[u'HK'],
                                       DEF[u'WK'], DEF[u'SPECIAL'])
ZID = DEF[u'ZID']
FOLD = lambda s: u' '.join(s.split())

# ---------- ①形状档 ----------
chk(u'bytes', [len(r) for r in RAWB])
chk(u'chars', [len(t) for t in TXT])
chk(u'lines', [len(l) for l in LST])
assert [t.count(NL) + 1 for t in TXT] == M[u'lines']
four(u'nonblank', lambda i: len([l for l in LST[i] if l.strip()]))
four(u'nonblank_asciib', lambda i: len([l for l in LST[i] if l.strip(u' \t\r')]))
four(u'ff_only_lines', lambda i: len([l for l in LST[i] if l.strip(u' \t\r') and not l.strip()]))
four(u'nb_gap', lambda i: M[u'nonblank_asciib'][i] - M[u'nonblank'][i])
four(u'maxlen', lambda i: max(len(l) for l in LST[i]))
four(u'trail', lambda i: len([l for l in LST[i] if l != l.rstrip()]))
four(u'cr', lambda i: TXT[i].count(u'\r'))
four(u'nonascii', lambda i: len([c for c in TXT[i] if ord(c) > 127]))
four(u'nonascii_cp', lambda i: [hex(ord(c)) for c in TXT[i] if ord(c) > 127])
four(u'nonascii_utf8_extra', lambda i: sum(len(c.encode(u'utf-8')) - 1 for c in TXT[i] if ord(c) > 127))
four(u'bom', lambda i: 1 if RAWB[i][:3] == b'\xef\xbb\xbf' else 0)
four(u'formfeed', lambda i: TXT[i].count(u'\x0c'))
chk(u'bc_delta', [M[u'bytes'][i] - M[u'chars'][i] for i in range(NSRC)])
chk(u'enc_close', [M[u'bc_delta'][i] - (3 * M[u'bom'][i] + M[u'nonascii_utf8_extra'][i]) for i in range(NSRC)])
chk(u'nonascii_cp_close', sum(M[u'nonascii'][i] - len(M[u'nonascii_cp'][i]) for i in range(NSRC)))
chk(u'sig', [hashlib.blake2b(r, digest_size=8).hexdigest() for r in RAWB])
chk(u'sig_distinct', len(set(M[u'sig'])))

# ---------- ②壳账: 正则两式 ⇎ 逐字符两式 ----------
HDR_SP = re.compile(u'(?m)^RFC (\\d{4})(?![\\d])')
HDR_NS = re.compile(u'(?m)^RFC(\\d{4})(?![\\d])')
FOOTR = re.compile(u'\\[Page (\\d+)\\]$')


def hdr_sp_line(l):
    m = HDR_SP.match(l)
    return bool(m) and (m.end() >= len(l) or l[m.end()] == u' ') and bool(l[8:].strip())


def hdr_ns_line(l):
    m = HDR_NS.match(l)
    return bool(m) and (m.end() >= len(l) or l[m.end()] == u' ')


def foot_line(l):
    return bool(FOOTR.search(l.strip()))


is_hdr = lambda l: hdr_sp_line(l) or hdr_ns_line(l)
is_foot = foot_line


four(u'hdr_sp', lambda i: len([l for l in LST[i] if hdr_sp_line(l)]))
four(u'hdr_ns', lambda i: len([l for l in LST[i] if hdr_ns_line(l)]))
chk(u'hdr', [M[u'hdr_sp'][i] + M[u'hdr_ns'][i] for i in range(NSRC)])
four(u'foot', lambda i: len([l for l in LST[i] if foot_line(l)]))
four(u'pg', lambda i: cnt(TXT[i], u'[Page '))
four(u'toc_lines', lambda i: len([l for l in LST[i]
                                  if u'...' in l and l.rstrip()[-1:].isdigit()
                                  and (l.lstrip()[:1].isdigit() or l.lstrip().startswith(u'.'))]))
chk(u'pagelines', [M[u'hdr'][i] + M[u'foot'][i] for i in range(NSRC)])
chk(u'pages_est', [max(M[u'hdr'][i], M[u'foot'][i]) for i in range(NSRC)])
chk(u'ff_foot_sum', sum(M[u'formfeed']) - sum(M[u'foot']))
chk(u'pg_foot_sum', sum(M[u'pg']) - sum(M[u'foot']))
chk(u'nb_ff_sum', sum(M[u'nb_gap']) - sum(M[u'ff_only_lines']))
chk(u'pagelines_close', sum(M[u'pagelines']) - sum(M[u'hdr']) - sum(M[u'foot']))

# ---------- ③上限数字: 锚定正则现读 ----------
CEILR = {u'a_ceil': (0, re.compile(u'AT MOST[ \\t]+(\\d+)')),
         u'b_ceil': (1, re.compile(u'more than[ \\t]+(\\d+)'))}
for nm, (i, rx) in CEILR.items():
    mm = rx.search(TXT[i])
    assert mm, nm
    chk(nm, int(mm.group(1)))
chk(u'ceil_close', M[u'a_ceil'] - M[u'b_ceil'])
for k, s in sorted(LITK.items()):
    four(u'lit_' + k, lambda i, s=s: occ(TXT[i], s))
four(u'ceil_docs', lambda i: 1 if (M[u'lit_atmost2'][i] or M[u'lit_more2'][i]) else 0)
chk(u'ceil_docs_n', sum(M[u'ceil_docs']))
four(u'nomandate_docs', lambda i: 1 if occ(TXT[i], LITK[u'nomandate']) else 0)
chk(u'nomandate_docs_n', sum(M[u'nomandate_docs']))
chk(u'ceil_nomandate_ledger', M[u'ceil_docs_n'] + M[u'nomandate_docs_n'] - NSRC)
chk(u'lit_two_both', [M[u'lit_atmost2'][i] + M[u'lit_more2'][i] for i in range(NSRC)])
chk(u'lit_hyphen_gap', M[u'lit_timeout_h'])
chk(u'lit_plain_in_ab', [M[u'lit_timeout_p'][i] - M[u'lit_timeout_h'][i] for i in range(NSRC)])
four(u'pol_a', lambda i: occ(TXT[i], u'SHOULD maintain AT MOST'))
four(u'pol_b', lambda i: occ(TXT[i], u'SHOULD NOT maintain more than'))
chk(u'pol_own', [M[u'pol_a'][0], M[u'pol_b'][1], 0, 0])
chk(u'pol_cross_ab', M[u'pol_b'][0])
chk(u'pol_cross_ba', M[u'pol_a'][1])
chk(u'pol_cross_close', M[u'pol_b'][0] + M[u'pol_a'][1])
chk(u'proxy_cd_sum', M[u'lit_pn'][2] + M[u'lit_pn'][3])
four(u'gen_h', lambda i: 1 if M[u'lit_timeout_h'][i] else 0)
four(u'gen_p', lambda i: 1 if M[u'lit_timeout_p'][i] else 0)
chk(u'gen_split_close', [M[u'gen_h'][i] + M[u'gen_p'][i] - 1 for i in range(NSRC)])
for _k in (u'abortedseq', u'seqidem', u'sidec', u'sided'):
    four(u'lit_' + _k + u'_fold', lambda i, _k=_k: occ(FO[i], FOLD(LITK[_k])))
chk(u'srvto_pair_close', [M[u'lit_srvto_h'][i] + M[u'lit_srvto_p'][i] - 1 for i in range(NSRC)])
for _k in (u'abortedseq', u'seqidem', u'sided', u'sidec'):
    chk(_k + u'_wrap', [M[u'lit_' + _k + u'_fold'][i] - M[u'lit_' + _k][i] for i in range(NSRC)])
chk(u'retry_form_close', M[u'lit_seqidem_fold'][0] + M[u'lit_methodid'][1])
chk(u'rem_decl_close', M[u'lit_removed2'][2] + M[u'lit_removed2'][3] - 1)
chk(u'retrydef_close', sum(M[u'lit_retrydef'][:3]))
chk(u'sec922_close', sum(M[u'lit_sec922'][:3]))
chk(u'idemhave_ab_close', M[u'lit_idemhave'][0] + M[u'lit_idemhave'][1])
chk(u'idem_cd_n', M[u'lit_idemhave'][2] + M[u'lit_idemhave'][3])
chk(u'keepa_ab_lower_zero', M[u'lit_keepa_lower'][0] + M[u'lit_keepa_lower'][1])

# ---------- ④答数行定位(原面 ⇎ 折平) ----------
for i, s in enumerate(RULE):
    t = TXT[i]
    chk(u'ans_line_' + TAGS[i].lower(),
        [n + 1 for n, l in enumerate(LST[i]) if s in l])
    chk(u'ans_linefold_' + TAGS[i].lower(),
        [n + 1 for n, l in enumerate(LST[i]) if FOLD(s) in FOLD(l)])
four(u'ans_lit_present', lambda i: 1 if RULE[i] in TXT[i] else 0)
four(u'ans_fold_present', lambda i: 1 if FOLD(RULE[i]) in FO[i] else 0)
chk(u'ans_gap', [M[u'ans_fold_present'][i] - M[u'ans_lit_present'][i] for i in range(NSRC)])
chk(u'ans_line_n', [len(M[u'ans_line_' + t.lower()]) for t in TAGS])
chk(u'ans_line_close', sum(M[u'ans_line_n']) - NSRC)

# ---------- ⑤节标题行与窗口 ----------
for key, cands in SECP:
    rows = []
    for i in range(NSRC):
        rr = []
        for n, l in enumerate(LST[i]):
            for pfx, title in cands:
                rx = re.compile(u'^[ \\t]*' + re.escape(pfx) + u'\\.?[ \\t]+'
                                + (re.escape(title) if title else u'\\S'))
                if rx.match(l):
                    rr.append(n + 1)
                    break
        rows.append(rr)
    chk(u'sec_' + key, [len(r) for r in rows])
    chk(u'sec_' + key + u'_line', rows)
chk(u'sec_keys', [len([1 for k in (u'practical', u'concurrency', u'failures') if M[u'sec_' + k][i]])
                  for i in range(NSRC)])
chk(u'sec_pair_close', [(M[u'sec_practical'][i] + M[u'sec_concurrency'][i] + M[u'sec_failures'][i])
                        - 2 * M[u'sec_keys'][i] for i in range(NSRC)])
chk(u'sec_keys_ledger', sum(M[u'sec_keys']) - 6)

SEC_HEAD = re.compile(u'^[ \\t]*([0-9.]+)[ \\t]+(\\S.*)$')


def is_sec_head(l):
    m = SEC_HEAD.match(l)
    if not m:
        return False
    rest = m.group(2).rstrip()
    return rest[:1].isupper() and len(rest) < 46 and u'...' not in l


def window(i):
    for key in (u'practical', u'concurrency'):
        ls = M[u'sec_' + key + u'_line'][i]
        if len(ls) >= 2:
            h = ls[-1] - 1
            j = h + 1
            while j < len(LST[i]) and not is_sec_head(LST[i][j]):
                j += 1
            return h, j, NL.join(LST[i][h:j])
    raise AssertionError(i)


WIN = [window(i) for i in range(NSRC)]
four(u'sec_head', lambda i: LST[i][WIN[i][0]].strip())
four(u'sec_len', lambda i: len(WIN[i][2]))
four(u'sec_a', lambda i: WIN[i][0] + 1)
four(u'sec_b', lambda i: WIN[i][1])
UPW = [(u'MUST NOT', u'must_not'), (u'MUST', u'must'), (u'SHOULD NOT', u'should_not'),
       (u'SHOULD', u'should'), (u'MAY', u'may'), (u'REQUIRED', u'required'),
       (u'RECOMMENDED', u'recommended'), (u'MAY NOT', u'may_not')]
for w, nm in UPW:
    four(u'u_' + nm, lambda i, w=w: occ(TXT[i], w))
OUTL = lambda i: NL.join(LST[i][:WIN[i][0]] + LST[i][WIN[i][1]:])
for w in (u'MUST', u'SHOULD', u'MAY'):
    four(u'secw_' + w.lower(), lambda i, w=w: occ(WIN[i][2], w))
    four(u'outw_' + w.lower(), lambda i, w=w: occ(OUTL(i), w))
    four(u'win_close_' + w.lower(), lambda i, w=w: M[u'secw_' + w.lower()][i] + M[u'outw_' + w.lower()][i]
         - occ(TXT[i], w))
four(u'secw_ought', lambda i: occ(WIN[i][2], u'ought to'))
four(u'outw_ought', lambda i: occ(OUTL(i), u'ought to'))
four(u'secw_atmost', lambda i: occ(WIN[i][2], u'AT MOST'))
four(u'secw_nomandate', lambda i: occ(WIN[i][2], LITK[u'nomandate']))
four(u'secw_lit_pn', lambda i: occ(WIN[i][2], LITK[u'pn']))
SEC6 = [k for k, _ in SN if k in (u'a2', u'b2', u'proxy', u'remove', u'c_nmand', u'cd_len')]
assert len(SEC6) == 6, SEC6
chk(u'oblig_up', [M[u'u_must'][i] + M[u'u_should'][i] + M[u'u_may'][i] for i in range(NSRC)])
chk(u'oblig_up_close', sum(M[u'u_must'][i] + M[u'u_should'][i] + M[u'u_may'][i] - M[u'oblig_up'][i]
                           for i in range(NSRC)))
for _w in (u'must', u'should', u'may'):
    chk(_w + u'_win_close', [M[u'secw_' + _w][i] + M[u'outw_' + _w][i] - M[u'u_' + _w][i] for i in range(NSRC)])
chk(u'must_win_close_sum', sum(M[u'must_win_close']))
WORDRX = re.compile(u'[A-Za-z][A-Za-z0-9_]*')
for w in (u'must', u'should', u'may'):
    four(u'lo_' + w, lambda i, w=w: len([x for x in WORDRX.findall(TXT[i]) if x == w]))
chk(u'oblig_low', [M[u'lo_must'][i] + M[u'lo_should'][i] + M[u'lo_may'][i] for i in range(NSRC)])
chk(u'oblig_low_close', sum(M[u'oblig_low'][i] - (M[u'lo_must'][i] + M[u'lo_should'][i] + M[u'lo_may'][i])
                            for i in range(NSRC)))
four(u'rfc2119_ref', lambda i: occ(TXT[i], u'2119'))
for k, s in WK:
    four(u'v_' + k, lambda i, s=s: occ(TXT[i], s))

# ---------- ⑥主线针: 严格档 ⇎ 折平档 ----------
for k, s in SN:
    four(u's_' + k, lambda i, s=s: occ(TXT[i], s))
    four(u's_' + k + u'_fold', lambda i, s=s: occ(FO[i], FOLD(s)))
    four(u'wrapgap_' + k, lambda i, k=k: M[u's_' + k + u'_fold'][i] - M[u's_' + k][i])
chk(u'wrap_sn_n', len(SN))
chk(u'wrap_sn_hit', len([1 for k, _ in SN if any(M[u'wrapgap_' + k])]))
chk(u'wrap_sn_total', sum(sum(M[u'wrapgap_' + k]) for k, _ in SN))
four(u'sn_strict_docs', lambda i: len([1 for k, _ in SN if M[u's_' + k][i]]))
four(u'sn_fold_docs', lambda i: len([1 for k, _ in SN if M[u's_' + k + u'_fold'][i]]))
chk(u'sn_only_fold', [k for k, _ in SN if any(M[u'wrapgap_' + k])])
chk(u'wrap_onlyfold_n', len(M[u'sn_only_fold']))
chk(u'wrap_hit_minus_onlyfold', M[u'wrap_sn_hit'] - M[u'wrap_onlyfold_n'])
chk(u'wrap_proxy_ab', sum(M[u'wrapgap_proxy']))
chk(u'cd_verdict_same', M[u's_cd_same_fold'][2] + M[u's_cd_same_fold'][3])
chk(u'cd_prose_diff', M[u's_hol_c_fold'][2] + M[u's_hol_d_fold'][3])
chk(u'hol_excl', M[u'lit_payloadblk'][3] + M[u'lit_bigcontent'][2])
chk(u'cd_verdict_same_minus_hol', M[u'cd_verdict_same'] - M[u'cd_prose_diff'])
four(u'grace_docs', lambda i: 1 if (M[u's_grace_it_fold'][i] or M[u's_grace_that_fold'][i]) else 0)
chk(u'grace_all_close', sum(M[u'grace_docs']) - NSRC)
chk(u'grace_pair_close', [M[u's_grace_it_fold'][i] + M[u's_grace_that_fold'][i] - 1 for i in range(NSRC)])
chk(u'grace_trac_close', [M[u's_grace_trac'][i] + M[u's_grace_conn_fold'][i] - 1 for i in range(NSRC)])
chk(u'tline_both_docs', [1 if (M[u's_tline_h_fold'][i] or M[u's_tline_p_fold'][i]) else 0 for i in range(NSRC)])
chk(u'tline_pair_close', [M[u's_tline_h_fold'][i] + M[u's_tline_p_fold'][i] - 1 for i in range(NSRC)])
four(u'main6_fold', lambda i: len([1 for k in SEC6 if M[u's_' + k + u'_fold'][i]]))
four(u'sn_other_fold', lambda i: M[u'sn_fold_docs'][i] - M[u'main6_fold'][i])
SECWIN = [len([1 for k in SEC6 if occ(u' '.join(WIN[i][2].split()), FOLD(dict(SN)[k]))])
          for i in range(NSRC)]

# ---------- ⑦断行世代 ----------
four(u'hyb_eol', lambda i: len([l for l in LST[i] if l.endswith(u'-')]))
four(u'hyb_cont', lambda i: len([1 for a, b in zip(LST[i], LST[i][1:])
                                 if a.endswith(u'-') and b.lstrip()[:1].islower()]))
four(u'srv_side_raw', lambda i: occ(TXT[i], u'server-side'))
four(u'srv_side_art', lambda i: occ(FO[i], u'server- side'))
chk(u'srv_side_sum', [M[u'srv_side_raw'][i] + M[u'srv_side_art'][i] for i in range(NSRC)])
chk(u'srv_side_cd_close', M[u'srv_side_sum'][2] + M[u'srv_side_sum'][3] - 2)
for _k, _one, _two in CCH:
    four(u'ch_' + _k, lambda i, s=_one: occ(TXT[i], s))
    four(u'ch_' + _k + u'_two', lambda i, s=_two: occ(TXT[i], s))
    four(u'ch_' + _k + u'_fold', lambda i, s=_one: occ(FO[i], s))
chk(u'ch_fold_gain', [M[u'ch_c64_fold'][i] - M[u'ch_c64'][i] for i in range(NSRC)])
chk(u'ch_d94_gain', [M[u'ch_d94_fold'][i] - M[u'ch_d94'][i] for i in range(NSRC)])
chk(u'ch_c64_two', [M[u'ch_c64_fold'][i] - M[u'ch_c64'][i] for i in range(NSRC)])
chk(u'ch_fold_eq', [M[u'ch_c64_fold'][i] + M[u'ch_d94_fold'][i] - M[u'ch_c64'][i] - M[u'ch_c64_two'][i]
                    - M[u'ch_d94'][i] - M[u'ch_d94_two'][i] for i in range(NSRC)])

# ---------- ⑧身份头与引用网 ----------
for k, s in HK:
    if k == u'obsoleted_by':
        continue
    four(k, lambda i, s=s: occ(TXT[i], s))
chk(u'obsoleted_by', [len([1 for p in posn(LOW[i], u'obsoleted by')]) for i in range(NSRC)])
RFCRX = re.compile(u'RFC[ ]?(\\d{4})(?!\\d)')


def cite(t, n):
    return len([m for m in RFCRX.finditer(t) if m.group(1) == n])


for n in (u'2068', u'2616', u'2145', u'7230', u'7231', u'9110', u'9112', u'2119', u'7235'):
    four(u'cite_' + n, lambda i, n=n: cite(TXT[i], n))
chk(u'cite_self', [cite(TXT[i], SELFN[i]) for i in range(NSRC)])
chk(u'selfcite_ledger', [M[u'cite_self'][i] - M[u'hdr'][i] for i in range(NSRC)])
chk(u'selfcite_close3', sum(M[u'selfcite_ledger'][:3]))
four(u'cite_http_brk', lambda i: occ(TXT[i], u'[HTTP]'))
BRKR = re.compile(u'\\[RFC[ ]?(\\d{4})\\]')
four(u'cite_rfc_brk', lambda i: len(BRKR.findall(TXT[i])))
four(u'num_lines', lambda i: len([l for l in LST[i] if len(l.strip()) >= 55
                                  and any(x in l for x in NLITS)]))

# ---------- ⑨搬运: 两把尺与四元容斥 ----------
GE40 = [sorted({nrm(l) for l in LST[i] if len(l.strip()) >= 40 and len(nrm(l)) >= 40}) for i in range(NSRC)]
GE40N = [sorted({nrm(l) for l in LST[i] if not (is_hdr(l) or is_foot(l))
                 and len(l.strip()) >= 40 and len(nrm(l)) >= 40}) for i in range(NSRC)]
GERAW = [sorted({l for l in LST[i] if len(l.strip()) >= 40 and len(nrm(l)) >= 40}) for i in range(NSRC)]
S40 = [set(x) for x in GE40]
S40N = [set(x) for x in GE40N]
chk(u'lines_ge40', [len(s) for s in GE40])
chk(u'lines_ge40_nos', [len(s) for s in GE40N])
for suf, SS in ((u'', S40), (u'_nos', S40N)):
    for a in range(NSRC):
        for b in range(a + 1, NSRC):
            chk(u'share_%s%s%s' % (TAGS[a].lower(), TAGS[b].lower(), suf), len(SS[a] & SS[b]))
    chk(u'union_all' + suf, len(set().union(*SS)))
    chk(u'only_a' + suf, len([x for x in SS[0] if not any(x in SS[j] for j in (1, 2, 3))]))
    chk(u'only_d' + suf, len([x for x in SS[3] if not any(x in SS[j] for j in (0, 1, 2))]))
chk(u'union_abc', len(set().union(S40[0], S40[1], S40[2])))
chk(u'union_delta', M[u'union_all'] - M[u'union_abc'])
chk(u'shell_delta', [M[u'lines_ge40'][i] - M[u'lines_ge40_nos'][i] for i in range(NSRC)])
chk(u'share_cd_delta', M[u'share_cd'] - M[u'share_cd_nos'])
trip = lambda a, b, c: len(S40[a] & S40[b] & S40[c])
chk(u'abcd_incl', sum(M[u'lines_ge40']) - sum(M[u'share_%s%s' % (TAGS[a].lower(), TAGS[b].lower())]
                                              for a in range(NSRC) for b in range(a + 1, NSRC))
     + trip(0, 1, 2) + trip(0, 1, 3) + trip(0, 2, 3) + trip(1, 2, 3) - len(S40[0] & S40[1] & S40[2] & S40[3]))
chk(u'abcd_close', M[u'abcd_incl'] - M[u'union_all'])
chk(u'y_ab_byte_shared', len(set(GERAW[0]) & set(GERAW[1])))
chk(u'y_ab_norm_only', M[u'share_ab'] - M[u'y_ab_byte_shared'])
chk(u'y_cd_byte_shared', len(set(GERAW[2]) & set(GERAW[3])))
chk(u'y_cd_norm_only', M[u'share_cd'] - M[u'y_cd_byte_shared'])
chk(u'd_shell_zero', M[u'hdr'][3] + M[u'foot'][3] + M[u'formfeed'][3] + M[u'trail'][3])

# ---------- ⑩锚池分层 ----------
CNT = {}
for i in range(NSRC):
    for l in LST[i]:
        n = nrm(l)
        if len(l.strip()) >= 55 and len(n) >= 55 and not (is_hdr(l) or is_foot(l)):
            CNT.setdefault(n, set()).add(i)
chk(u'pool_n', len(CNT))
chk(u'pool_tier', [len([1 for n in CNT if len(CNT[n]) == k]) for k in range(1, NSRC + 1)])
chk(u'pool_tier_close', sum(M[u'pool_tier']) - M[u'pool_n'])
for n in range(1, NSRC + 1):
    chk(u'pool_%d' % n, M[u'pool_tier'][n - 1])
for n, i in ((u'2068', 0), (u'2616', 1), (u'7230', 2), (u'9112', 3)):
    chk(u'pool_share1_' + n, len([x for x in CNT if CNT[x] == {i}]))
chk(u'pool_share2_ab', len([x for x in CNT if CNT[x] == {0, 1}]))
chk(u'pool_share2_cd', len([x for x in CNT if CNT[x] == {2, 3}]))
S4 = [x for x in CNT if len(CNT[x]) == NSRC]
RV = [{} for _ in range(NSRC)]
for _i in range(NSRC):
    for l in LST[_i]:
        n = nrm(l)
        if n in CNT and len(CNT[n]) == NSRC:
            RV[_i].setdefault(n, set()).add(l)


def common_raw(n):
    ss = [RV[i].get(n, set()) for i in range(NSRC)]
    out = ss[0]
    for s in ss[1:]:
        out = out & s
    return out


def axes_of(n):
    forms = sorted({l for i in range(NSRC) for l in RV[i].get(n, set())})
    if len(forms) < 2:
        return []
    one = lambda f: len(set(f(x) for x in forms)) == 1
    if one(lambda s: s.lower()):
        return [u'case']
    if one(lambda s: s.lower().replace(u'-', u'')):
        return [u'hyph']
    if one(lambda s: u' '.join(s.lower().replace(u'-', u'').split())):
        return [u'space']
    return [u'multi']


chk(u'share4_byte4', len([1 for x in S4 if common_raw(x)]))
chk(u'share4_notbyte', len(S4) - M[u'share4_byte4'])
for _a in (u'case', u'hyph', u'space', u'multi'):
    chk(u'share4_axis_' + _a, len([1 for x in S4 if axes_of(x) == [_a]]))
chk(u'share4_axis_close', sum(M[u'share4_axis_' + a] for a in (u'case', u'hyph', u'space', u'multi'))
    - M[u'share4_notbyte'])
assert M[u'share4_axis_multi'] == 0
chk(u'pool_share4', sorted(x for x in CNT if len(CNT[x]) == NSRC)[:6])
chk(u'share4_diff', sorted([[u'+'.join(axes_of(x)), x] for x in S4 if axes_of(x)]))
assert [len(axes_of(x)) for x in S4 if axes_of(x)] == [1] * M[u'share4_notbyte']
assert M[u'share4_byte4'] + M[u'share4_notbyte'] == M[u'pool_4']
POOL = {(TAGS[i], l) for i in range(NSRC) for l in LST[i]
        if (len(l) >= 20 or any(x in l for x in SPECIAL)) and nrm(l)}
POOL = sorted(POOL)
POOLC = [(t, sum(1 for k in range(NSRC) if nrm(x) in FAN[k]), x) for (t, x) in POOL]
chk(u'apool_n', len(POOLC))
four(u'apool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
for n in range(1, NSRC + 1):
    chk(u'apool_%d' % n, len([p for p in POOLC if p[1] == n]))

# ---------- ⑪闭合账 ⇎ 恒等式 ⇎ DERIV(全用本注读数) ----------
# 建条目侧的 CLOSK 是在源码某一行的 F 快照上数的; 本遍用语法树定位那一行,
# 把它之后才被赋值的 F 键剔掉——否则“标量闭合枚数”量的就不是同一时刻的账本。
CLLINE = None
for ST in TREE.body:
    if isinstance(ST, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == u'CLOSK' for t in ST.targets):
        CLLINE = ST.lineno
assert CLLINE, u'找不到 CLOSK 赋值行'
AFTER = set()
for ST in TREE.body:
    if ST.lineno > CLLINE:
        for sub in ast.walk(ST):
            if isinstance(sub, ast.Assign):
                for t in sub.targets:
                    if (isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                            and t.value.id == u'F' and isinstance(t.slice, ast.Constant)
                            and isinstance(t.slice.value, str)):
                        AFTER.add(t.slice.value)
CLOSK = sorted([k for k in FLAT if (u'_close' in k or u'_ledger' in k)
                and isinstance(FLAT[k], (int, float)) and not isinstance(FLAT[k], bool)
                and k not in AFTER and k not in (u'scalar_clos_n', u'scalar_clos_sum')])
assert len(CLOSK) == FLAT[u'scalar_clos_n'], (len(CLOSK), FLAT[u'scalar_clos_n'], sorted(AFTER))
chk(u'scalar_clos_n', len(CLOSK))
MISSC = [k for k in CLOSK if k not in M]
assert not MISSC, MISSC[:8]
chk(u'scalar_clos_sum', sum(M[k] for k in CLOSK))
chk(u'list_clos_n', len([k for k in FLAT if (u'_close' in k or u'_ledger' in k)
                         and isinstance(FLAT[k], list) and k not in AFTER]))
GV = lambda k, i=None: (M[k] if i is None else M[k][i])
EENV = {u'GV': GV, u'max': max, u'min': min, u'sum': sum, u'len': len, u'abs': abs, u'round': round,
        u'sorted': sorted, u'set': set, u'list': list, u'int': int, u'float': float, u'pow': pow}
EV = lambda e: eval(e.replace(u'B65V', u'GV'), EENV)
IDENTS = [e for e, _ in ZID]
assert len(IDENTS) == FLAT[u'x_ident_n'], (len(IDENTS), FLAT[u'x_ident_n'])
chk(u'x_ident_n', len(IDENTS))

# ---------- ⑫采集侧(第一遍)与本注对账 ----------
COMMON = [k for k in MEAS if k in M]
BADP = [k for k in COMMON if MEAS[k] != M[k]]
assert not BADP, BADP[:5]

# ---------- 锚归属: 双轨成员判据 ⇎ 行跨度 ----------
TTXT = io.open(ENTRY, encoding=u'utf-8').read()
ENC = re.search(u'\u27eaBabelTele\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TTXT, re.S).group(1)
CITES = re.findall(u'\u27e6([' + u''.join(TAGS) + u'])\u27e7\u27e8([^\u27e8\u27e9]+)\u27e9', ENC)
assert CITES and len(re.findall(u'\u27e8', ENC)) == len(CITES)
DIS = []
for _, a in CITES:
    if a not in DIS:
        DIS.append(a)


def stream_hit(tag, anchor):
    """逐行流式拼归一面: 每批只留末尾 len(锚)−1 字符的续接窗口, 不现造整篇面。"""
    na = nrm(anchor)
    if not na:
        return False
    tail, w = u'', len(na) - 1
    i = IDX[tag]
    for l in LST[i]:
        cur = tail + nrm(l)
        if na in cur:
            return True
        tail = cur[-w:] if w > 0 else u''
    return False


def line_hit(tag, anchor):
    na = nrm(anchor)
    i = IDX[tag]
    single = any(na == nrm(l) or na in nrm(l) for l in LST[i])
    if single:
        return True
    adj = any(na in (nrm(a) + nrm(b)) for a, b in zip(LST[i], LST[i][1:]))
    return adj


def min_span(anchor):
    """这枚锚最少压在几行上: 1..6 行滑窗, 归一后拼接判子串。"""
    na = nrm(anchor)
    got = None
    for i in range(NSRC):
        ls = LST[i]
        for k in range(1, 7):
            if na and any(na in u''.join(nrm(x) for x in ls[n:n + k]) for n in range(len(ls))):
                got = k if got is None else min(got, k)
                break
    return got


BAD_ANCH = [(t, a) for t, a in CITES if nrm(a) not in FAN[IDX[t]]]
assert not BAD_ANCH, BAD_ANCH[:3]
DUAL = [(t, a) for t, a in CITES if stream_hit(t, a) != line_hit(t, a)]
assert not DUAL, DUAL[:3]
SPANS = dict((a, min_span(a)) for a in DIS)
SPD = {}
for v in SPANS.values():
    SPD[v] = SPD.get(v, 0) + 1
HC = [tuple(i for i in range(NSRC) if nrm(a) and nrm(a) in FAN[i]) for a in DIS]
chk(u'anchor_total', len(CITES))
chk(u'anchor_distinct', len(DIS))
chk(u'anchor_err', len(BAD_ANCH))
chk(u'anchor_single', len([h for h in HC if len(h) == 1]))
chk(u'anchor_cross', len([h for h in HC if 1 < len(h) < NSRC]))
chk(u'anchor_all4', len([h for h in HC if len(h) == NSRC]))
chk(u'checks', len(DIS) * NSRC)
for t in TAGS:
    chk(u'tag_' + t, len(re.findall(u'\u27e6%s\u27e7' % t, ENC)))
assert M[u'anchor_single'] + M[u'anchor_cross'] + M[u'anchor_all4'] == M[u'anchor_distinct']
assert sum(M[u'tag_' + t] for t in TAGS) == M[u'anchor_total']

# ---------- ⑬恒等式 ⇎ DERIV: 算式取自建条目侧宣称, 数全部用本注读数 ----------
NEED = sorted({k for e in IDENTS + list(DER.values())
               for k in re.findall(u"B65V\\('([^']+)'", e)} - SEEN)
assert not NEED, NEED[:20]
IDENT_BAD = [(e, EV(e)) for e in IDENTS if EV(e) != 0]
assert not IDENT_BAD, IDENT_BAD[:3]
DER_NUM_BAD, DER_TXT_BAD = [], []
for k, e in DER.items():
    try:
        v = EV(e)
    except Exception as ex:
        (DER_NUM_BAD if re.match(u'^-?\\d+$', k) else DER_TXT_BAD).append((k, repr(ex)))
        continue
    if re.match(u'^-?\\d+$', k):
        if not isinstance(v, (int, float)) or abs(v - int(k)) > 1e-9:
            DER_NUM_BAD.append((k, v, e))
    elif not (v == k or (not isinstance(v, str) and u'%s' % (v,) == k)):
        DER_TXT_BAD.append((k, v, e))
assert not DER_NUM_BAD, DER_NUM_BAD[:3]
assert not DER_TXT_BAD, DER_TXT_BAD[:3]
UNFLAT = [k for k in FLAT if k not in M]
assert not UNFLAT and not MIS, (UNFLAT[:6], MIS[:6])

# ---------- 写注 ----------
NOTE_ROWS = []


def A(s):
    NOTE_ROWS.append(s)


def r(meth, way, read, keys):
    A(u'| {0} | {1} | {2} | {3} |'.format(meth, way, read, keys))


A(u'本注是第四遍复测: 采集侧 `_pick65` ⇎ 建条目侧 `_mkB65` ⇎ 门槛侧 `audit.py::_b65_scan` ⇎ 本注, 四套实现换算法不换定义。')
A(u'下面每一行的数都是本注从四份字节现读后与 `corpus/_b65flat.json` 逐键对拍的结果, 任一键不符即停机; '
  u'标量闭合账 {0} 项合计 {1}, 清单账 {2} 项, 面内恒等式 {3} 条按本注读数重算全归零, DERIV {4} 条复算点全对。'.format(
      M[u'scalar_clos_n'], M[u'scalar_clos_sum'], M[u'list_clos_n'], M[u'x_ident_n'], CH[u'deriv_keys']))
A(u'')
A(u'| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |')
A(u'|---|---|---|---|')
r(u'形状⇎编码', u'行数 len(split) ⇎ count(换行)+1 两式互证; 非空行两口径 strip() ⇎ strip(" \\t\\r"); '
  u'独占换页行=宽口径非空⇎窄口径空; 签名为 blake2b 前 16 位',
  u'字节 {0} ⇎ 字符 {1} ⇎ 行 {2} ⇎ 非空行 {3} ⇎ 宽口径 {4} ⇎ 差 {5}=换页独占行 {6} ⇎ 最长行 {7} ⇎ 签名 {8} 种'.format(
      J(M[u'bytes']), J(M[u'chars']), J(M[u'lines']), J(M[u'nonblank']), J(M[u'nonblank_asciib']),
      J(M[u'nb_gap']), J(M[u'ff_only_lines']), J(M[u'maxlen']), M[u'sig_distinct']),
  u'全 LF(回车 {0}); BOM {1} ⇎ 非 ASCII 码点 {2}(码位 {3})⇎ 字节−字符 {4} ⇎ 闭合 {5}——'
  u'22 一份的 4 字节差由 BOM 3 字节 + 一枚两字节变音符解释'.format(
      J(M[u'cr']), J(M[u'bom']), J(M[u'nonascii']), M[u'nonascii_cp'], J(M[u'bc_delta']), J(M[u'enc_close'])))
r(u'壳账', u'页眉两式 ^RFC \\d{4} 带题文 ⇎ ^RFC\\d{4} 不带空格; 页脚 \\[Page \\d+\\]$ 一式; 点线目录行按“含 ... ⇎ 行尾数字”',
  u'页眉 {0}(带空格 {1} ⇎ 无空格 {2}) ⇎ 页脚 {3} ⇎ “[Page ” {4} 处 ⇎ 换页 {5} ⇎ 行尾空格 {6} ⇎ 版面行 {7} ⇎ 目录行 {8}'.format(
      J(M[u'hdr']), J(M[u'hdr_sp']), J(M[u'hdr_ns']), J(M[u'foot']), J(M[u'pg']), J(M[u'formfeed']),
      J(M[u'trail']), J(M[u'pagelines']), J(M[u'toc_lines'])),
  u'换页−页脚 {0} ⇎ “[Page ”−页脚 {1} ⇎ 非空行−独占换页 {2} ⇎ 版面行−(页眉+页脚) {3} 全为零; '
  u'22 页壳四档全零(合计 {4}), 去页壳只挪动 {5} 行(14 那份)'.format(
      M[u'ff_foot_sum'], M[u'pg_foot_sum'], M[u'nb_ff_sum'], M[u'pagelines_close'],
      M[u'd_shell_zero'], J(M[u'shell_delta'])))
r(u'上限读数', u'锚定正则 (AT MOST|more than)[ \\t]+(\\d+) 现读(建条目侧是逐字符连读数字), 只取首个带数字的命中',
  u'A {0} 条 ⇎ B {1} 条 ⇎ 差 {2}; 给数的份数 {3} ⇎ 撤数的份数 {4} ⇎ 对四份闭合 {5}'.format(
      M[u'a_ceil'], M[u'b_ceil'], M[u'ceil_close'], M[u'ceil_docs_n'], M[u'nomandate_docs_n'],
      M[u'ceil_nomandate_ledger']),
  u'两式本句式各 {0} ⇎ {1}(合计 {2}); 交叉侵入 A 面读 B 句式 {3} ⇎ B 面读 A 句式 {4} ⇎ 闭合 {5}; '
  u'“2*N connections” {6} 处——代理乘法句在 14⇎22 整段删除(合计 {7})'.format(
      M[u'pol_a'][0], M[u'pol_b'][1], J(M[u'pol_own']), M[u'pol_cross_ab'], M[u'pol_cross_ba'],
      M[u'pol_cross_close'], J(M[u'lit_pn']), M[u'proxy_cd_sum']))
r(u'答数行', u'针在原面的行号由 enumerate 现取, 严格档 ⇎ 折平档各走一遍',
  u'严格档行号 {0} ⇎ {1} ⇎ {2} ⇎ {3}; 折平档 {4} ⇎ {5} ⇎ {6} ⇎ {7}; 每份恰 1 枚(闭合 {8})'.format(
      M[u'ans_line_a'], M[u'ans_line_b'], M[u'ans_line_c'], M[u'ans_line_d'],
      M[u'ans_linefold_a'], M[u'ans_linefold_b'], M[u'ans_linefold_c'], M[u'ans_linefold_d'],
      M[u'ans_line_close']),
  u'折平而原面读不到的份 {0}(答数句在 C⇎D 被跨行劈开 {1}); 四枚都在自己的答题窗内: '
  u'窗长 {2} ⇎ {3} ⇎ {4} ⇎ {5} 字符, 窗起行 {6} ⇎ {7} ⇎ {8} ⇎ {9}, 窗止行 {10} ⇎ {11} ⇎ {12} ⇎ {13}; '
  u'窗标题 {14}; 节标题枚数账 {15}'.format(
      J(M[u'ans_gap']), J(M[u'ans_lit_present']),
      *[M[u'sec_len'][i] for i in range(NSRC)],
      *[M[u'sec_a'][i] for i in range(NSRC)],
      *[M[u'sec_b'][i] for i in range(NSRC)],
      u' ⇎ '.join(repr(h) for h in M[u'sec_head']), M[u'sec_keys_ledger']))
r(u'窗内外', u'窗外=行表切片拼接(不是总数减窗内); 窗=最后一枚标题行到下一枚标题行',
  u'六枚主线针本面命中 {0} ⇎ 其余 {1}(和=容行档 {2}); MUST 窗内 {3} ⇎ 窗外 {4} ⇎ 全篇 {5}; SHOULD {6} ⇎ {7} ⇎ {8}; MAY {9} ⇎ {10} ⇎ {11}'.format(
      J(M[u'main6_fold']), J(M[u'sn_other_fold']), J(M[u'sn_fold_docs']),
      J(M[u'secw_must']), J(M[u'outw_must']), J(M[u'u_must']),
      J(M[u'secw_should']), J(M[u'outw_should']), J(M[u'u_should']), J(M[u'secw_may']),
      J(M[u'outw_may']), J(M[u'u_may'])),
  u'三档逐份闭合 {0}⇎{1}⇎{2}(和 {3}); “AT MOST” 只在 A 窗内 {4} ⇎ 撤数式在 C⇎D 窗内 {5} ⇎ 代理乘法窗内 {6}; '
  u'六枚里真压在节窗内的只有 {7}(其余跨出窗止行); '
  u'“ought to” 窗内 {7} ⇎ 窗外 {8}'.format(
      J(M[u'must_win_close']), J(M[u'should_win_close']), J(M[u'may_win_close']), M[u'must_win_close_sum'],
      J(M[u'secw_atmost']), J(M[u'secw_nomandate']), J(M[u'secw_lit_pn']), J(M[u'secw_ought']), J(M[u'outw_ought'])))
r(u'严格⇎折平', u'针折平后在同一 re.findall(转义) 通道重数; 每针之差即跨行账',
  u'针 {0} 枚 ⇎ 有差 {1} 枚 ⇎ 差合计 {2} 处; 严格档每份 {3} 枚 ⇎ 容行档 {4} 枚'.format(
      M[u'wrap_sn_n'], M[u'wrap_sn_hit'], M[u'wrap_sn_total'], J(M[u'sn_strict_docs']), J(M[u'sn_fold_docs'])),
  u'逐份“严格+差=容行”成立: {0}; 只靠折平才读得到的针 {1} 枚(与有差枚数之差 {2}); '
  u'97 上限句劈行 {3} ⇎ 99 {4} ⇎ 代理句折平 A⇎B 合计 {5}'.format(
      u'；'.join('%d+%d=%d' % (M[u'sn_strict_docs'][i], sum(M[u'wrapgap_' + q][i] for q in M[u'sn_only_fold']),
                              M[u'sn_fold_docs'][i]) for i in range(NSRC)),
      M[u'wrap_onlyfold_n'], M[u'wrap_hit_minus_onlyfold'], M[u'wrapgap_a2'], M[u'wrapgap_b2'], M[u'wrap_proxy_ab']))
r(u'世代拼写', u'带连字符 ⇎ 不带连字符两式各按 findall 数, 每份“落进一档”由两式之和判',
  u'“time-out” {0} ⇎ “timeout” {1}; 每份恰好一档(闭合 {2}); 插语“(or existence)” {3}; '
  u'“have some time-out value” {4} ⇎ “have some timeout value” {5}(成对闭合 {6})'.format(
      J(M[u'lit_timeout_h']), J(M[u'lit_timeout_p']), J(M[u'gen_split_close']), J(M[u'lit_orx']),
      J(M[u'lit_srvto_h']), J(M[u'lit_srvto_p']), J(M[u'srvto_pair_close'])),
  u'“优雅关闭”主语式换代: 旧式折平 {0} ⇎ 新式折平 {1}(每份闭合 {2}); 带 transport 的旧宾语式 {3} ⇎ 新宾语式折平 {4} '
  u'(闭合 {5}); 四份都有一种主语写法(账 {6})'.format(
      J(M[u's_grace_it_fold']), J(M[u's_grace_that_fold']), J(M[u'grace_pair_close']),
      J(M[u's_grace_trac']), J(M[u's_grace_conn_fold']), J(M[u'grace_trac_close']), M[u'grace_all_close']))
r(u'撤数⇎论证', u'撤数整段(三句连排)与论证段各立折平档; 互斥判据用对方针在自己面上的命中',
  u'撤数段折平档 {0} ⇎ 原面档 {1}(劈行差在 C⇎D 各 {2}⇎{3}); 撤数段 C⇎D 同现 {4} 枚 ⇎ 论证段各一枚合计 {5} ⇎ 差 {6}'.format(
      J(M[u's_cd_same']), M[u's_cd_same_fold'], M[u'wrapgap_cd_same'][2], M[u'wrapgap_cd_same'][3],
      M[u'cd_verdict_same'], M[u'cd_prose_diff'], M[u'cd_verdict_same_minus_hol']),
  u'C 的 payload 句在 D 面 {0} 处 ⇎ D 的 large-content 句在 C 面 {1} 处(互斥账 {2}); '
  u'“server-side” 原面 {3} ⇎ 折平 “server- side” {4} ⇎ 并档 {5}(C+D 闭合 {6}); '
  u'两代节标题排版分家: 6.4 单空格形 {7} 处 ⇎ 折平并档 {8} 处, 9.4 单空格 {9} 处 ⇎ 双空格 {10} 处'.format(
      M[u'lit_payloadblk'][3], M[u'lit_bigcontent'][2], M[u'hol_excl'],
      J(M[u'srv_side_raw']), J(M[u'srv_side_art']), J(M[u'srv_side_sum']), M[u'srv_side_cd_close'],
      J(M[u'ch_c64']), J(M[u'ch_c64_fold']), J(M[u'ch_d94']), J(M[u'ch_d94_two'])))
r(u'重试粒度', u'方法式 ⇎ 序列式各立原面与折平两档; 新措辞按四份原面合计判零字面',
  u'“aborted request” {0} ⇎ “aborted sequence of requests” {1}(折平 {2}, 跨行差 {3}); '
  u'“request method is idempotent” {4} ⇎ “request sequence is idempotent” 原面 {5} 全零⇎折平只读到 99 的 {6}'.format(
      J(M[u'lit_abortedreq']), J(M[u'lit_abortedseq']), J(M[u'lit_abortedseq_fold']), J(M[u'abortedseq_wrap']),
      J(M[u'lit_methodid']), J(M[u'lit_seqidem']), J(M[u'lit_seqidem_fold'])),
  u'判据回摆: 14⇎22 改用 “have idempotent methods” {0} 处(前两代合计 {1}); 22 独一条委派句 “Section 9.2.2 of [HTTP]” {2} 处'
  u'(前三份合计 {3}); 14 的撤数宣告 {4} 处而 22 复述 {5}(账 {6}); retransmi 词干 {7} 处——22 已归零'.format(
      J(M[u'lit_idemhave']), M[u'idemhave_ab_close'], J(M[u'lit_sec922']), M[u'sec922_close'],
      M[u'lit_removed2'][2], M[u'lit_removed2'][3], M[u'rem_decl_close'], J(M[u'v_retransmit'])))
r(u'义务词两档', u'全大写族 findall(转义); 全小写族按词流整词相等(大写形与复合词都不算)',
  u'大写三词合计 {0} ⇎ 小写三词合计 {1}; MUST {2} ⇎ should 家族小写 {3}; REQUIRED {4} ⇎ RECOMMENDED {5}'.format(
      J(M[u'oblig_up']), J(M[u'oblig_low']), J(M[u'u_must']), J(M[u'lo_should']),
      J(M[u'u_required']), J(M[u'u_recommended'])),
  u'小写账闭合 {0}; 措辞换代: “SHOULD limit the number” {1} ⇎ “ought to limit” {2}(互不重叠); '
  u'RFC 2119 被引 {3} 次而 “2119” 字样 {4} 处'.format(
      M[u'oblig_low_close'], J(M[u'lit_shouldlimit']), J(M[u'lit_oughttolimit']),
      J(M[u'rfc2119_ref']), J(M[u'cite_2119'])))
r(u'搬运两把尺', u'归一只留 a-z0-9(re.sub), 交用 &、并用 |; 逐字节档不归一; 四元容斥本注自己列齐',
  u'归一 A⇎B {0} 行(逐字节 {1} ⇎ 仅归一同 {2}) ⇎ C⇎D {3} 行(逐字节 {4} ⇎ 仅归一 {5}); 去页壳之差 {6}'.format(
      M[u'share_ab'], M[u'y_ab_byte_shared'], M[u'y_ab_norm_only'], M[u'share_cd'],
      M[u'y_cd_byte_shared'], M[u'y_cd_norm_only'], M[u'share_cd_delta']),
  u'两两搬运 {0}⇎{1}⇎{2}⇎{3}⇎{4}⇎{5}; 四份并集 {6} ⇎ 去 D 并集 {7} ⇎ 差 {8}=D 独占 {9}; '
  u'容斥 {10} 对并集差 {11}; A 独占长行 {12} 行'.format(
      M[u'share_ab'], M[u'share_ac'], M[u'share_ad'], M[u'share_bc'], M[u'share_bd'], M[u'share_cd'],
      M[u'union_all'], M[u'union_abc'], M[u'union_delta'], M[u'only_d'], M[u'abcd_incl'],
      M[u'abcd_close'], M[u'only_a']))
r(u'锚池⇎引用', u'池按“归一长行压在几份里”分层(集合运算); 四份同现者回原面取逐字节交集, 再用三把写法尺(忽略大小写 ⇎ 去连字符 ⇎ 折空格)定差在哪一根轴',
  u'池 {0} 条: 一档 {1} ⇎ 二档 {2} ⇎ 三档 {3} ⇎ 四档 {4}(闭合 {5}); 四档里逐字节仍同形 {6} 条 ⇎ 有写法差 {7} 条; '
  u'轴账闭合 {8}: 大小写 {9} ⇎ 连字符 {10} ⇎ 句后空格 {11} ⇎ 跨两根轴 {12}'.format(
      M[u'pool_n'], M[u'pool_1'], M[u'pool_2'], M[u'pool_3'], M[u'pool_4'],
      M[u'pool_tier_close'], M[u'share4_byte4'], M[u'share4_notbyte'], M[u'share4_axis_close'],
      M[u'share4_axis_case'], M[u'share4_axis_hyph'], M[u'share4_axis_space'],
      M[u'share4_axis_multi']),
  u'一源四枚分档 {0}⇎{1}⇎{2}⇎{3}; 跨行候选池 {4} 条按标签 {5}; 22 引 14 {6} 次而引 99 {7} 次, '
  u'具名方括号引用 {8} 处(14 引入 {9} 处⇎97 {10} 处)'.format(
      M[u'pool_share1_2068'], M[u'pool_share1_2616'], M[u'pool_share1_7230'], M[u'pool_share1_9112'],
      M[u'apool_n'], J(M[u'apool_tag_n']), M[u'cite_7230'][3], M[u'cite_2616'][3],
      M[u'cite_http_brk'][3], M[u'cite_rfc_brk'][2], M[u'cite_rfc_brk'][0]))
r(u'锚归属', u'双轨判据: ①逐行流式拼归一面(只留末尾 len(锚)−1 字符续接) ②单行表 ⇎ 相邻两行拼接按子串判; 两式同判才放行',
  u'锚 {0} 处 ⇎ 去重 {1} 串 ⇎ 归属检查 {2} 次 ⇎ 错配 {3}; 一源 {4} ⇎ 两至三源 {5} ⇎ 四源 {6}; 标签 A⇎B⇎C⇎D {7}⇎{8}⇎{9}⇎{10}'.format(
      M[u'anchor_total'], M[u'anchor_distinct'], M[u'checks'], M[u'anchor_err'], M[u'anchor_single'],
      M[u'anchor_cross'], M[u'anchor_all4'], M[u'tag_A'], M[u'tag_B'], M[u'tag_C'], M[u'tag_D']),
  u'行跨度分布(最少压在几行上): {0}; 唯一一枚归一后四份同现的锚是“服务器总会有自己的超时值”句, '
  u'它在四档池里正是唯一一枚差在连字符轴上的(轴账 hyph {1} ⇎ space {2} ⇎ case {3}), '
  u'故原面按 time-out⇎timeout 分家'.format(
      u'⇎'.join(u'%d 行 %d 枚' % (k, SPD[k]) for k in sorted(SPD)),
      M[u'share4_axis_hyph'], M[u'share4_axis_space'], M[u'share4_axis_case']))
A(u'')
A(u'### 不可由在库文件判定(只写在这里, 不进判词与门槛)')
A(u'四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; rfc-editor.org 此刻给这四份挂的现行状态页与勘误页(是否已改动 2616 的 §8.1.4);'
  u'各家浏览器此刻对同一域名实际同时开几条连接(2 条上限在 2014 年被撤, 但实现层的并行度从未由规范决定);'
  u'现网服务器把空闲超时配成多少秒; 14⇎22 撤掉数字之后“保守地多开”在真实客户端里被解释成什么。')
A(u'这些量要么在本机之外、要么随实现漂移, 复算通道里没有它们的位置; 若要把它们变成判词, 需要先取回带时间戳的另一手快照, '
  u'再按本注同一套键重跑——门槛只认在库字节。')
NOTE = NL.join(NOTE_ROWS)
assert not re.findall(u'%[sdifg]|%\\(', NOTE)
HEAD = TTXT[:TTXT.index(u'## ⛓解读注') + len(u'## ⛓解读注')]
io.open(ENTRY, 'w', encoding=u'utf-8', newline=NL).write(HEAD + NL + NL + NOTE + NL)
print(u'⛓解读注已写 %d 字符 ｜ 第四遍 assert 全过 ｜ 复测 %d/%d 扁平键 ｜ 采集对账 %d 键 0 不符 ｜ '
      u'恒等式 %d 条 ⇎ DERIV %d 条按本注读数重算全对 ｜ 锚 %d 处／去重 %d 串／错配 %d ｜ 未测扁平键 %d ｜ 契约外键 %d'
      % (len(NOTE), len([k for k in FLAT if k in M]), len(FLAT), len(COMMON), M[u'x_ident_n'],
         len(DER), M[u'anchor_total'], M[u'anchor_distinct'], M[u'anchor_err'], len(UNFLAT), len(MIS)))
print(u'六枚本面命中 vs 真落窗内: %s ⇎ %s ｜ 行跨度 %s' % (M[u'main6_fold'], SECWIN, SPD))
