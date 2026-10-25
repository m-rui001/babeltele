# -*- coding: utf-8 -*-
"""采集遍(B80, 第一套实现): “失败的 HTTP 请求到底能不能自动重来一次”由五份一手文书各答一遍
2616 ⇎ 7231 ⇎ 6585 ⇎ 8470 ⇎ 9110。本遍只用一种机制(正则字面轨 + 行切片 + 节窗), 输出
_b80meas.json 给建条目侧(_mkB80.py + _mk80emit.py, 第二套实现: 非重叠游标 ⇎ 集合代数 ⇎ 句尺)逐键对账。

五份都是 RFC Editor 的 txt(无 HTML 档差), 本条的档位来自另外四处:
(1) 72 列硬换行切开的是判词的“动词段”, 不是关键词本身: 五份各取一条判词短语, 逐行尺有 4 份读不到
    (2616 的 “sequences / MUST NOT be automatically retried”、7231 的 “can be / repeated automatically”、
    8470 的 “expected to retry / the request when receiving a 425”、9110 的 “automatically retrying /
    the requests that failed”), 而义务词组合本身也被切开(MUST NOT 被切 3⇎1⇎0⇎0⇎5 枚, 9110 另有
    SHOULD NOT 4 枚), 裸词 idempotent 两把尺相等(从不被切);
(2) 同一概念落在三个节号(2616 §9.1.2 ⇎ 7231 §4.2.2 ⇎ 9110 §9.2.2), 6585 与 8470 根本没有这一节;
    9110 的同名标题在面上出现两次(目录 182 行 ⇎ 正文 3861 行), 节窗必须取后者;
(3) 判词的施事者随世代换位: 2616 全库唯一一枚被动式判词 “Non-idempotent methods or sequences / MUST NOT
    be automatically retried”(不点谁的名, 只给 user agents MAY offer 一个选择) ⇎ 9110 点名 proxy
    (MUST NOT)与 client(SHOULD NOT), 还写下 “a user agent can repeat a POST request automatically”;
(4) 6585 通篇零枚 automat*×retry 族, 答法是 429 + Retry-After: 3600 + 一句自认“不定义服务器怎么数请求”;
    8470 给阶梯(are expected to retry ⇎ SHOULD retry automatically ⇎ any retries MUST NOT be sent in
    early data ⇎ intermediary MAY automatically retry)。
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'2616', u'7231', u'6585', u'8470', u'9110']
SRC = [u'corpus/raw/httpretry/rfc2616.txt', u'corpus/raw/httpretry/rfc7231.txt',
       u'corpus/raw/httpretry/rfc6585.txt', u'corpus/raw/httpretry/rfc8470.txt',
       u'corpus/raw/httpretry/rfc9110.txt']
NS = 5
M = {}


def cnt_cur(hay, nd):
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def cnt_ovl(hay, nd):
    c, i = 0, 0
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + 1
    return c


def fold(s):
    return u' '.join(s.split())


# ---------- 面量 ----------
T, L, BYT = [], [], []
for p in SRC:
    b = io.open(p, u'rb').read()
    BYT.append(b)
    t = b.decode(u'utf-8', u'replace')
    T.append(t)
    L.append(t.split(NL))
M['label'] = LBL
M['src'] = SRC
M['bytes'] = [len(b) for b in BYT]
M['chars'] = [len(t) for t in T]
M['lines'] = [len(L[i]) for i in range(NS)]               # split(NL) 的切格数
M['newlines'] = [T[i].count(NL) for i in range(NS)]       # 真换行枚数
M['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NS)]
M['maxlen'] = [max(len(x) for x in L[i]) for i in range(NS)]
M['ff'] = [T[i].count(u'\x0c') for i in range(NS)]
M['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NS)]
M['cr'] = [T[i].count(u'\r') for i in range(NS)]
M['nul'] = [BYT[i].count(b'\x00') for i in range(NS)]
M['nonascii'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(NS)]
M['bom'] = [1 if BYT[i][:3] == b'\xef\xbb\xbf' else 0 for i in range(NS)]
M['byte_cp_delta'] = [M['bytes'][i] - M['chars'][i] for i in range(NS)]
M['tail_nl'] = [1 if T[i].endswith(NL) else 0 for i in range(NS)]
# 切格数 = 真换行 + 1; splitlines = 切格 − 尾换行 + 换页符(换页符自成一行而 splitlines 也切它, 这里逐份验)
for i in range(NS):
    assert M['lines'][i] == M['newlines'][i] + 1, i
    assert len(T[i].splitlines()) == M['lines'][i] - M['tail_nl'][i] + M['ff'][i] - \
        len([x for x in L[i] if u'\x0c' in x and x != u'\x0c']), i
assert M['cr'] == [0] * NS and M['nul'] == [0] * NS
assert M['lines'] == [9860, 5660, 564, 676, 10786], M['lines']
# 72 列档并非铁板: 7231 有若干行(ABNF 定义行)溢出到 75 列, 逐份数出来而不是当作噪声
M['over72'] = [len([x for x in L[i] if len(x) > 72]) for i in range(NS)]
assert M['maxlen'] == [72, 75, 72, 72, 72], M['maxlen']

# ---------- 换页符两档 ⇎ 页壳行 ----------
SHELL = re.compile(u'^\\s*(\\[Page \\d+\\]|RFC \\d+ +(?:HTTP|Additional|Using|Hypertext|HTTP Semantics)|'
                   u'(?:(?:Fielding|Nottingham|Reschke|Thomson|Gettys|Mogul|Masinter|Leach|Berners-Lee|Frystyk)[^\\n]*)$)')
M['pg_lines'] = [len([x for x in L[i] if re.search(u'\\[Page \\d+\\]', x)]) for i in range(NS)]
M['hdr_lines'] = [len([x for x in L[i] if re.match(u'^RFC \\d+\\b', x)]) for i in range(NS)]
M['ff_only_lines'] = M['ff_exact']
M['blank'] = [M['lines'][i] - M['nonblank'][i] for i in range(NS)]
for i in range(NS):
    assert M['ff'][i] == M['ff_exact'][i], (i, M['ff'][i], M['ff_exact'][i])   # 每枚 FF 独占一行
assert M['ff'] == [176, 101, 10, 12, 0], M['ff']
# 9110 既无换页符也无 “[Page N]” 行: 2022 年的 RFC Editor 纯文本干脆不分页, 页壳只剩空行
M['pageless'] = [1 if (M['ff'][i] == 0 and M['pg_lines'][i] == 0) else 0 for i in range(NS)]
assert M['pg_lines'][:4] == [176, 101, 10, 12] and M['pageless'] == [0, 0, 0, 0, 1]

# ---------- 折平面 ⇎ 摘壳折平面 ----------
FOLD = [fold(T[i]) for i in range(NS)]


def is_shell(x):
    return (re.match(u'^\\s*\\[Page \\d+\\]\\s*$', x) is not None
            or re.match(u'^\\s*RFC \\d+ +\\S.*((19|20)\\d\\d)\\s*$', x) is not None
            or x.strip() == u'')


SH = [fold(NL.join(x for x in L[i] if not is_shell(x))) for i in range(NS)]
M['shell_lines'] = [len([x for x in L[i] if is_shell(x)]) for i in range(NS)]
M['fold_chars'] = [len(FOLD[i]) for i in range(NS)]
M['sh_chars'] = [len(SH[i]) for i in range(NS)]
M['sh_minus_fold'] = [M['sh_chars'][i] - M['fold_chars'][i] for i in range(NS)]

# ---------- 抬头谱系 ----------
HEAD = ['\n'.join(L[i][:22]) for i in range(NS)]
M['obs_ids'] = [[x.strip() for x in re.search(u'Obsoletes: +([0-9, ]+)', HEAD[i]).group(1).split(u',')]
                if re.search(u'Obsoletes: +([0-9, ]+)', HEAD[i]) else [] for i in range(NS)]
M['upd_ids'] = [[x.strip() for x in re.search(u'Updates: +([0-9, ]+)', HEAD[i]).group(1).split(u',')]
                if re.search(u'Updates: +([0-9, ]+)', HEAD[i]) else [] for i in range(NS)]
M['obs_line'] = [next((x.strip() for x in L[i][:22] if x.strip().startswith(u'Obsoletes:')), None) for i in range(NS)]
M['upd_line'] = [next((x.strip() for x in L[i][:22] if x.strip().startswith(u'Updates:')), None) for i in range(NS)]
M['std_line'] = [next((x.strip() for x in L[i][:22] if re.match(u'^\\s*STD:', x)), None) for i in range(NS)]
M['issn_hdr'] = [1 if any(x.strip().startswith(u'ISSN:') for x in L[i][:22]) else 0 for i in range(NS)]
M['years'] = [1999, 2014, 2012, 2018, 2022]
MON = re.compile(u'(January|February|March|April|May|June|July|August|September|October|November|December) (19|20)\\d\\d')
M['months'] = []
M['months_txt'] = []
for i in range(NS):
    m = MON.search(HEAD[i])
    M['months'].append(m.group(1) if m else None)
    M['months_txt'].append(m.group(0) if m else None)
assert M['months'] == [u'June', u'June', u'April', u'September', u'June'], M['months']
M['year_span'] = max(M['years']) - min(M['years'])
M['year_inversions'] = len([(a, b) for a in range(NS) for b in range(NS) if a < b and M['years'][a] > M['years'][b]])
# 谱系点名 vs 库内作废: 被 6585 更新的 2616 在本库里同时出现在 7231 与 9110 的 Obsoletes 清单里
OBS = set(x for i in range(NS) for x in M['obs_ids'][i])
M['upd_target_obsoleted'] = [len([x for x in M['upd_ids'][i] if x in OBS]) for i in range(NS)]
M['obs_target_in_lib'] = [len([x for x in M['obs_ids'][i] if x in u' '.join(LBL)]) for i in range(NS)]
M['obs_total'] = sum(len(x) for x in M['obs_ids'])
M['upd_total'] = sum(len(x) for x in M['upd_ids'])
M['lineage_no_edge'] = [i for i in range(NS) if not M['obs_ids'][i] and not M['upd_ids'][i]]
assert M['obs_ids'][3] == [] and M['upd_ids'][3] == [] and M['obs_ids'][0] == [u'2068']
assert M['upd_target_obsoleted'][2] == 1 and M['upd_target_obsoleted'][1] == 0

# ---------- 自动重试词汇族(两把尺: 逐行原面 ⇎ 全篇折平) ----------
# 族内针互相包含("automatically retry" ⊂ "automatically retrying"), 所以"各针相加"≠"出现枚数":
# 另立一把并集尺(同一族一次左起非重叠扫描), 两把之差就是被重复计数的针数。
AUTOFAM = [u'automatically retry', u'automatically retried', u'automatically retrying',
           u'automatic retry', u'retry automatically', u'automatically repeat']
ALT = re.compile(u'|'.join(re.escape(x) for x in sorted(AUTOFAM, key=lambda s: -len(s))))
LOWFOLD = [x.lower() for x in FOLD]
LOW = [[y.lower() for y in L[i]] for i in range(NS)]      # 逐行小写(原面尺)
M['auto_fam'] = AUTOFAM
M['auto_line'] = [[sum(cnt_cur(y, nd) for y in LOW[i]) for nd in AUTOFAM] for i in range(NS)]
M['auto_line_rows'] = [[len([y for y in LOW[i] if nd in y]) for nd in AUTOFAM] for i in range(NS)]
M['auto_fold'] = [[cnt_cur(LOWFOLD[i], nd) for nd in AUTOFAM] for i in range(NS)]
M['auto_union_fold'] = [len(ALT.findall(LOWFOLD[i])) for i in range(NS)]
M['auto_fam_overlap'] = [sum(M['auto_fold'][i]) - M['auto_union_fold'][i] for i in range(NS)]
M['auto_gain'] = [sum(M['auto_fold'][i]) - sum(M['auto_line'][i]) for i in range(NS)]
M['auto_tot_line'] = [sum(M['auto_line'][i]) for i in range(NS)]
M['auto_tot_fold'] = [sum(M['auto_fold'][i]) for i in range(NS)]
M['auto_bare'] = [cnt_cur(LOWFOLD[i], u'automatic') for i in range(NS)]
M['auto_bare_line'] = [sum(cnt_cur(y, u'automatic') for y in LOW[i]) for i in range(NS)]
# 摘壳尺(第三把): 页壳行剥掉后词汇族不应变化
M['auto_sh'] = [[cnt_cur(SH[i].lower(), nd) for nd in AUTOFAM] for i in range(NS)]
M['auto_sh_minus_fold'] = [sum(M['auto_sh'][i]) - sum(M['auto_fold'][i]) for i in range(NS)]
M['auto_bare_minus_union'] = [M['auto_bare'][i] - M['auto_union_fold'][i] for i in range(NS)]

# ---------- 跨行短横: “non-/idempotent” 这类被换行切开的复合词 ----------
M['hyb_idem'] = [cnt_cur(T[i], u'non-' + NL + u'idempotent') for i in range(NS)]
M['idem_str'] = [cnt_cur(LOWFOLD[i], u'idempotent') for i in range(NS)]
M['idem_line_occ'] = [sum(cnt_cur(y, u'idempotent') for y in LOW[i]) for i in range(NS)]
M['idem_line_rows'] = [len([y for y in LOW[i] if u'idempotent' in y]) for i in range(NS)]
M['idem_hyb_line'] = [sum(cnt_cur(y, u'non-idempotent') for y in LOW[i]) for i in range(NS)]
M['idem_hyb_fold'] = [cnt_cur(LOWFOLD[i], u'non-idempotent') for i in range(NS)]
M['hyb_straddle'] = [M['idem_hyb_fold'][i] - M['idem_hyb_line'][i] for i in range(NS)]
# 裸词 “idempotent” 从不被换行切开, 切开的是带短横的复合词: 两把尺之差只应出现在后者
assert M['idem_str'] == M['idem_line_occ'], (M['idem_str'], M['idem_line_occ'])
assert M['hyb_straddle'] == M['hyb_idem'], (M['hyb_straddle'], M['hyb_idem'])
assert M['idem_str'] == [15, 14, 0, 0, 18], M['idem_str']
# 族相加 ≥ 并集(重叠只多不少), 逐行尺 ≤ 折平尺(缝上的只会被读宽), 摘壳尺不应再读出新枚
assert all(M['auto_fam_overlap'][i] >= 0 for i in range(NS)), M['auto_fam_overlap']
assert all(M['auto_tot_line'][i] <= M['auto_tot_fold'][i] for i in range(NS)), M['auto_gain']
assert M['auto_sh_minus_fold'] == [0] * NS, M['auto_sh_minus_fold']
assert all(M['auto_bare'][i] >= M['auto_union_fold'][i] for i in range(NS)), M['auto_bare_minus_union']

# ---------- 幂等节窗(第三把尺: 只在答句那一节里数) ----------
SEC = re.compile(u'^\\s*(\\d+(?:\\.\\d+)*)\\.?\\s+Idempotent (?:Methods|Request Methods)\\s*$')
M['sec_no'] = []
M['sec_head_line'] = []
ENDK = []
ENDH = []
HITN = []
TOCL = []
BODYL = []
IDW = []
for i in range(NS):
    hit = [(k, SEC.match(x)) for k, x in enumerate(L[i])]
    hit = [(k, m) for k, m in hit if m]
    if not hit:
        M['sec_no'].append(None)
        M['sec_head_line'].append(None)
        ENDK.append(None)
        ENDH.append(None)
        HITN.append(0)
        TOCL.append(None)
        BODYL.append(None)
        IDW.append(None)
        continue
    k, m = hit[-1]     # 同名标题可能先出现在目录里(9110 的目录是光秃秃的标题表, 没有点线页码),
    HITN.append(len(hit))
    TOCL.append(hit[0][0] + 1 if len(hit) > 1 else None)
    BODYL.append(k + 1)
    M['sec_head_line'].append(L[i][k].strip())
    M['sec_no'].append(m.group(1))
    lvl = len(m.group(1).split(u'.'))
    cur = tuple(int(z) for z in m.group(1).split(u'.'))
    # 节尾 = 第一个“同级或更高级、且编号在本文里往后走”的标题行。两条都要:
    # 尾点漏了(“4.3.  Common…”)会一路吞到文件末尾; 不比对编号大小会被文中的编号列表(“1.  xxx”)
    # 当场截断, 于是“节窗大小”这把尺本身要先能失败。
    nxt = len(L[i])
    end_kind = u'eof'
    for j in range(k + 1, len(L[i])):
        mm = re.match(u'^\\s*(\\d+(?:\\.\\d+)*)\\.?\\s+\\S', L[i][j])
        if not mm:
            continue
        tup = tuple(int(z) for z in mm.group(1).split(u'.'))
        if len(tup) <= lvl and tup >= cur:
            nxt = j
            end_kind = u'heading'
            break
    IDW.append(NL.join(L[i][k:nxt]))
    ENDK.append(end_kind)
    ENDH.append(L[i][nxt].strip() if nxt < len(L[i]) else None)
M['sec_end_kind'] = ENDK
M['sec_end_head'] = ENDH
M['sec_hit_n'] = HITN
M['sec_toc_line'] = TOCL
M['sec_body_line'] = BODYL
M['sec_found_n'] = len([x for x in M['sec_no'] if x])
M['sec_lines'] = [len(x.split(NL)) if x else 0 for x in IDW]
M['sec_chars'] = [len(x) if x else 0 for x in IDW]
M['sec_words'] = [len(x.split()) if x else 0 for x in IDW]
M['sec_sents'] = [len(re.findall(u'\\.\\s', x)) if x else 0 for x in IDW]

# ---------- 义务词阶梯(三把尺: 规范大写字面 ⇎ 不分大小写字面 ⇎ 节窗) ----------
TONE = [u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY']


def ub(hay, nd):
    return len(re.findall(u'(?<![A-Za-z])' + nd + u'(?![A-Za-z])', hay))


M['tone_fam'] = TONE
M['tone_norm'] = [[ub(T[i], nd) for nd in TONE] for i in range(NS)]            # 原面大写字面尺
M['tone_norm_fold'] = [[ub(FOLD[i], nd) for nd in TONE] for i in range(NS)]    # 折平大写字面尺
M['tone_straddle_k'] = [[M['tone_norm_fold'][i][k] - M['tone_norm'][i][k] for k in range(len(TONE))]
                        for i in range(NS)]
M['tone_straddle'] = [sum(M['tone_straddle_k'][i]) for i in range(NS)]
M['tone_case'] = [[cnt_cur(LOWFOLD[i], nd.lower()) for nd in TONE] for i in range(NS)]  # 不分大小写
M['tone_case_gap'] = [sum(M['tone_case'][i]) - sum(M['tone_norm_fold'][i]) for i in range(NS)]
M['tone_sec'] = [[ub(IDW[i], nd) for nd in TONE] if IDW[i] else [0] * len(TONE) for i in range(NS)]
M['tone_sec_tot'] = [sum(M['tone_sec'][i]) for i in range(NS)]
M['tone_tot'] = [sum(M['tone_norm'][i]) for i in range(NS)]
# 容斥账: MUST 针把 "MUST NOT" 里的 MUST 也数进去, 减去 NOT 组合应等于纯 MUST(独立再数一次)
M['tone_must_pure'] = [len(re.findall(u'(?<![A-Za-z])MUST(?![A-Za-z])(?! NOT)', T[i])) for i in range(NS)]
M['tone_must_ledger'] = [M['tone_norm'][i][1] - M['tone_norm'][i][0] - M['tone_must_pure'][i]
                         for i in range(NS)]
M['tone_word_lc'] = [[cnt_cur(LOWFOLD[i], w) for w in (u'must', u'should', u'may', u'can')]
                     for i in range(NS)]

# ---------- 逐字搬字: 7231 §4.2.2 ⇎ 9110 §9.2.2 ----------
def body_rows(i):
    return [fold(x) for x in L[i] if len(x.strip()) >= 30 and not is_shell(x)]


POOL = [body_rows(i) for i in range(NS)]
PAIR = [(1, 4), (0, 1), (0, 4), (0, 3), (1, 3), (2, 3), (2, 4), (3, 4), (0, 2), (1, 2)]
P2 = {}
for a, b in PAIR:
    sa = set(POOL[a])
    P2[u'%s-%s' % (LBL[a], LBL[b])] = len([x for x in set(POOL[b]) if x in sa])
M['pair_shared'] = P2
M['pair_max_lbl'] = max(P2, key=lambda k: P2[k])
M['pair_max'] = P2[M['pair_max_lbl']]
# 同一对再按“逐字节同”数一次(不折平), 两把尺的差就是硬换行挪位造成的
BA, BB = None, None
for a, b in PAIR:
    if M['pair_max_lbl'] == u'%s-%s' % (LBL[a], LBL[b]):
        BA, BB = a, b
rawA = set(x for x in L[BA] if len(x.strip()) >= 30)
rawB = set(x for x in L[BB] if len(x.strip()) >= 30)
M['pair_max_byte'] = len([x for x in rawB if x in rawA])
M['pair_max_norm_only'] = M['pair_max'] - M['pair_max_byte']
M['pool_n'] = sum(len(x) for x in POOL)
M['pair_lbl_idx'] = [BA, BB]
assert M['pair_max_lbl'] == u'7231-9110', M['pair_max_lbl']

# ---------- Retry-After 轴 ----------
M['ra_count'] = [cnt_cur(T[i], u'Retry-After') for i in range(NS)]
# ABNF 规则行按“行”找而不是按字面needle找: 2616 写 `Retry-After  = "Retry-After" ":" ( HTTP-date |
# delta-seconds )`(两个空格+竖线), 7231/9110 写 `Retry-After = HTTP-date / delay-seconds`(斜杠),
# 同一份里规范节与注册表各印一次, 于是规则行数≠取值形式数。
RAB = re.compile(u'^\\s*Retry-After\\s*=')
RABLINE = [[x for x in L[i] if RAB.match(x)] for i in range(NS)]
M['ra_abnf_lines'] = [len(x) for x in RABLINE]
M['ra_abnf_forms'] = [len(set(fold(x) for x in RABLINE[i])) for i in range(NS)]
M['ra_abnf_bar'] = [len([x for x in RABLINE[i] if u'|' in x]) for i in range(NS)]
M['ra_abnf_slash'] = [len([x for x in RABLINE[i] if u' / ' in x]) for i in range(NS)]
M['ra_abnf_quoted'] = [len([x for x in RABLINE[i] if u'"Retry-After"' in x]) for i in range(NS)]
M['ra_abnf_ledger'] = [M['ra_abnf_bar'][i] + M['ra_abnf_slash'][i] - M['ra_abnf_lines'][i]
                       for i in range(NS)]
M['ra_exp_date'] = [cnt_cur(T[i], u'Retry-After: Fri, 31 Dec 1999 23:59:59 GMT') for i in range(NS)]
M['ra_exp_120'] = [cnt_cur(T[i], u'Retry-After: 120') for i in range(NS)]
M['ra_exp_3600'] = [cnt_cur(T[i], u'Retry-After: 3600') for i in range(NS)]
M['ra_two_minutes'] = [cnt_cur(LOWFOLD[i], u'the delay is 2 minutes') for i in range(NS)]
M['ra_delta_def'] = [cnt_cur(LOWFOLD[i], u'non-negative decimal integer') for i in range(NS)]
assert M['ra_abnf_ledger'] == [0] * NS, M['ra_abnf_ledger']
assert M['ra_abnf_lines'] == [1, 2, 0, 0, 2] and M['ra_abnf_forms'] == [1, 1, 0, 0, 1]
assert M['ra_abnf_quoted'] == [1, 0, 0, 0, 0]
assert M['ra_exp_date'] == [1, 1, 0, 0, 1] and M['ra_exp_120'] == [1, 1, 0, 0, 1]
assert M['ra_exp_3600'] == [0, 0, 1, 0, 0]

# ---------- 429 / 425 / Early-Data 词汇的归属(反向对照 + 两把数字尺) ----------
# 裸串尺会在参考文献里读到假状态码: 9110 的 “RFC 4289” 里含 “428”, 2616 的某个长数字里含 “425”。
NEG = [u'429', u'Too Many Requests', u'Too Early', u'Early-Data', u'rate limiting', u'428',
       u'Precondition Required', u'425', u'idempotent']
M['neg_fam'] = NEG
M['neg_digit'] = [k for k, nd in enumerate(NEG) if nd.isdigit()]


def nbound(nd):
    return (u'(?<!\\d)' + nd + u'(?!\\d)') if nd.isdigit() else (
        u'(?<![A-Za-z])' + re.escape(nd) + u'(?![A-Za-z])')


M['neg_raw'] = [[cnt_cur(T[i], nd) for nd in NEG] for i in range(NS)]
M['neg_bnd'] = [[len(re.findall(nbound(nd), T[i])) for nd in NEG] for i in range(NS)]
M['neg_false_sub'] = [sum(M['neg_raw'][i]) - sum(M['neg_bnd'][i]) for i in range(NS)]
M['neg_zero_n'] = [len([k for k in range(len(NEG)) if M['neg_bnd'][i][k] == 0]) for i in range(NS)]
M['neg_own'] = [[k for k in range(len(NEG)) if M['neg_bnd'][i][k]
                and all(M['neg_bnd'][j][k] == 0 for j in range(NS) if j != i)] for i in range(NS)]
M['neg_own_lbl'] = [[NEG[k] for k in M['neg_own'][i]] for i in range(NS)]
assert M['neg_raw'][0][7] == 1 and M['neg_bnd'][0][7] == 0        # 2616 的 “425” 是子串
assert M['neg_raw'][4][5] == 1 and M['neg_bnd'][4][5] == 0        # 9110 的 “428” 来自 RFC 4289
assert M['neg_false_sub'] == [1, 0, 0, 0, 1], M['neg_false_sub']
assert M['neg_bnd'][2][0] == 9 and M['neg_bnd'][3][3] == 23 and M['neg_bnd'][4][0] == 0

# ---------- 状态码清单: 六码族在哪几份里被定义 ----------
CODES = [u'400', u'401', u'403', u'404', u'405', u'408', u'416', u'428', u'429', u'425', u'431', u'500',
         u'503', u'504', u'505', u'506', u'507', u'508', u'510', u'511']
M['code_fam'] = CODES
# 定义行 = “编号(可多级带尾点) + 状态码 + 名字”那一行; 节号必须整段读, 少写 (?:\.\d+)* 会把
# 2616 的 “10.4.1  400 Bad Request” 判成没定义。目录里的同名行带点线引道符(三个以上连点+页码),
# 必须剥掉, 否则“定义了 12 个码”其实是“目录列了 12 行”
LEADER = re.compile(u'\\.{3,}')
# 逐行 match 而非在全文上 findall: 全文模式下行首的 ^\s* 会把换行也吃掉, 于是 IANA 清单里
# “4\n      400 Bad Request (status code)  58” 这种跨行残片被当成定义行, 定义数虚高两枚
CODE_ROWS = [[[x for x in L[i]
               if re.match(u'^\\s*\\d+(?:\\.\\d+)*\\.?\\s+(?:%s)(?![\\d.])' % c, x)]
              for c in CODES] for i in range(NS)]
M['code_defined_raw'] = [len([y for rows in CODE_ROWS[i] for y in rows]) for i in range(NS)]
M['code_defined'] = [[len([y for y in rows if not LEADER.search(y)]) for rows in CODE_ROWS[i]]
                     for i in range(NS)]
M['code_defined_n'] = [sum(x) for x in M['code_defined']]
M['code_toc'] = [M['code_defined_raw'][i] - M['code_defined_n'][i] for i in range(NS)]
M['code_defined_lbl'] = [[CODES[k] for k in range(len(CODES)) if M['code_defined'][i][k]]
                         for i in range(NS)]
# 三种码名在两代文书里有两种印法: 定义行“10.4.1  400 Bad Request” ⇎ 括号引用“425 (Too Early)”
PAREN = [u'425 (Too Early)', u'428 (Precondition Required)', u'429 (Too Many Requests)']
M['paren_fam'] = PAREN
M['paren'] = [[cnt_cur(FOLD[i], nd) for nd in PAREN] for i in range(NS)]
M['paren_line'] = [[sum(cnt_cur(y, nd) for y in L[i]) for nd in PAREN] for i in range(NS)]
M['paren_straddle'] = [sum(M['paren'][i]) - sum(M['paren_line'][i]) for i in range(NS)]
assert M['code_defined_n'] == [11, 9, 8, 0, 22], M['code_defined_n']
assert M['code_defined'][2][7] == 2 and M['code_defined'][0][8] == 0
assert M['code_defined'][2][7] == 2 and M['code_defined'][2][8] == 2
# 9110(2022, 现行 HTTP 语义规范)既不定义也不提名 428/429: 限速重来的答案只活在 6585 里
assert M['code_defined'][4][7] == 0 and M['code_defined'][4][8] == 0
assert M['neg_bnd'][4][0] == 0 and M['neg_bnd'][4][5] == 0

# ---------- 答案句(锚由位置导出, 不手打) ----------
ANS = []
ANS_HEAD = [u'Non-idempotent methods or sequences',
            u'Idempotent methods are distinguished because',
            u'The 429 status code indicates',
            u'User agents that send a request in early data are expected',
            u'A proxy MUST NOT automatically retry']
# 答句里的“判词短语”: 逐行尺读不到 ⇎ 折行尺读到, 差值就是被 72 列换行切开的那一口
ANS_PH = [u'sequences MUST NOT be automatically retried',
          u'request can be\nrepeated automatically',
          u'MAY include a Retry-After header indicating how long',
          u'expected to retry\nthe request when receiving a 425',
          u'automatically retrying\nthe requests that failed']
for i, pat in enumerate(ANS_HEAD):
    k = T[i].find(pat)
    assert k >= 0, (i, pat)
    ln = T[i][:k].count(NL)
    # 段落 = 答句所在行起到下一个空行; 句界在“折平流”上找, 因为 72 列换行把句号留在了行中
    # (“…retrying the request(s). Confirmation by”——一行里装着两句话, 按行尾找句号会多读)
    pl = []
    j = ln
    while j < len(L[i]) and L[i][j].strip() != u'':
        pl.append(j)
        j += 1
    txt, offs = u'', []
    for idx in pl:
        offs.append(len(txt))
        txt += (u'' if txt == u'' else u' ') + fold(L[i][idx])
    st = txt.find(pat)
    assert st >= 0, (i, u'答句起点不在段落折平流里')
    mm = re.search(u'\\.\\s*(?=[A-Z(]|$)', txt[st + len(pat):])
    en = st + len(pat) + (mm.end() if mm else len(txt) - st - len(pat)) - 1
    cover = [kk for kk in range(len(pl))
             if offs[kk] <= en and offs[kk] + len(fold(L[i][pl[kk]])) >= st]
    ANS.append(txt[st:en + 1])
    M.setdefault(u'ans_span', []).append(len(cover))
    M.setdefault(u'ans_first_line', []).append(ln)
    M.setdefault(u'ans_para_span', []).append(len(pl))
    M.setdefault(u'ans_lead_words', []).append(
        len(fold(L[i][ln])[:fold(L[i][ln]).find(pat)].split()) if pat in fold(L[i][ln]) else 0)
    M.setdefault(u'ans_lines_abs', []).append([pl[kk] + 1 for kk in range(len(cover))])
M['ans'] = ANS
M['ans_words'] = [len(x.split()) for x in ANS]
M['ans_one_line_n'] = len([x for x in M['ans_span'] if x == 1])


def is_page_shell(x):
    return (re.match(u'^\\s*\\[Page \\d+\\]\\s*$', x) is not None
            or re.match(u'^\\s*RFC \\d+ +\\S.*((19|20)\\d\\d)\\s*$', x) is not None)


# 答句跨不跨页: 跨页的句子在原行尺上被抬头/页脚打断, 只有摘壳尺能连读
M['ans_page_break'] = [len([y for y in M['ans_lines_abs'][i] if is_page_shell(L[i][y - 1])])
                       for i in range(NS)]
M['ans_para_tail'] = [M['ans_para_span'][i] - M['ans_span'][i] for i in range(NS)]
M['ph_line'] = [sum(cnt_cur(y.lower(), ANS_PH[i].lower().replace(NL, u' ')) for y in L[i])
                for i in range(NS)]
M['ph_fold'] = [cnt_cur(LOWFOLD[i], ANS_PH[i].lower().replace(NL, u' ')) for i in range(NS)]
M['ph_straddle'] = [M['ph_fold'][i] - M['ph_line'][i] for i in range(NS)]
M['ph_raw_line'] = [len([y for y in L[i] if ANS_PH[i] in y]) for i in range(NS)]
M['ans_ph'] = ANS_PH
assert M['ph_fold'] == [1] * NS, M['ph_fold']
assert M['ans_span'] == [3, 3, 2, 2, 1], M['ans_span']
assert M['ans_one_line_n'] == 1 and M['ans_lead_words'] == [4, 0, 0, 0, 0]

# ---------- “重来”用词族: 同一件事五份各说什么词(针间互相包含, 另立并集尺) ----------
REWORD = [u'retry', u'retrying', u'repeated', u'repeat', u'resubmit', u'try again',
          u'make a new request', u'follow-up request']
RALT = re.compile(u'|'.join(re.escape(x) for x in sorted(REWORD, key=lambda s: -len(s))))
M['reword_fam'] = REWORD
M['reword'] = [[cnt_cur(LOWFOLD[i], nd.lower()) for nd in REWORD] for i in range(NS)]
M['reword_union'] = [len(RALT.findall(LOWFOLD[i])) for i in range(NS)]
M['reword_overlap'] = [sum(M['reword'][i]) - M['reword_union'][i] for i in range(NS)]
M['reword_tot'] = [sum(x) for x in M['reword']]
M['reword_zero_n'] = [len([k for k in range(len(REWORD)) if M['reword'][i][k] == 0]) for i in range(NS)]
M['reword_own'] = [[REWORD[k] for k in range(len(REWORD)) if M['reword'][i][k]
                   and all(M['reword'][j][k] == 0 for j in range(NS) if j != i)] for i in range(NS)]
assert all(M['reword_overlap'][i] >= 0 for i in range(NS)), M['reword_overlap']

# ---------- 判词的施事者: 谁被禁止自动重来, 五份各点谁的名 ----------
# 针里带 \n 的是“在折平尺才连得起来”的判词, 逐行尺读到 0 枚, 差值即被换行切开的那一条
SUBJ = [u'A proxy MUST NOT automatically retry', u'A client SHOULD NOT automatically retry',
        u'user agents MAY offer', u'SHOULD retry automatically', u'MAY automatically retry',
        u'can repeat a POST request automatically', u'might\nautomatically retry a POST',
        u'are expected to retry', u'MUST NOT be automatically retried']
PASSIVE = 8                                   # 只有被动式的一条不点施事者的名
M['subj_fam'] = SUBJ
M['subj'] = [[cnt_cur(FOLD[i], nd.replace(NL, u' ')) for nd in SUBJ] for i in range(NS)]
M['subj_line'] = [[sum(cnt_cur(y, nd) for y in L[i]) for nd in SUBJ] for i in range(NS)]
M['subj_straddle'] = [sum(M['subj'][i]) - sum(M['subj_line'][i]) for i in range(NS)]
M['subj_n'] = [len([k for k in range(len(SUBJ)) if M['subj'][i][k]]) for i in range(NS)]
M['subj_active'] = [sum(M['subj'][i][:PASSIVE]) for i in range(NS)]
M['subj_passive'] = [M['subj'][i][PASSIVE] for i in range(NS)]
assert M['subj_passive'] == [1, 0, 0, 0, 0] and M['subj_active'][0] == 1
assert M['subj_active'][2] == 0 and M['subj_active'][1] == 0
assert M['subj'][4][:PASSIVE] == [1, 2, 0, 0, 0, 1, 1, 0], M['subj'][4]
assert M['subj'][3][3] == 1 and M['subj'][3][4] == 1 and M['subj'][3][7] == 1
M['subj_straddle_k'] = [[M['subj'][i][kk] - M['subj_line'][i][kk] for kk in range(len(SUBJ))]
                        for i in range(NS)]
M['subj_straddled'] = [[SUBJ[kk] for kk in range(len(SUBJ)) if M['subj_straddle_k'][i][kk]]
                       for i in range(NS)]
assert M['subj_straddle'] == [0, 0, 0, 0, 2], M['subj_straddle']
assert M['subj_straddled'][4] == [u'A client SHOULD NOT automatically retry',
                                  u'might\nautomatically retry a POST'], M['subj_straddled'][4]

# ---------- 判词点到的“谁”: 施事者名词族(单数用零宽尺, 否则 “user agent” 会被 “user agents” 吃掉) ----------
ACT = [u'user agent', u'user agents', u'client', u'proxy', u'intermediar', u'origin server', u'server']
M['act_fam'] = ACT
M['act'] = [[cnt_cur(LOWFOLD[i], nd) for nd in ACT] for i in range(NS)]
M['act_sg'] = [len(re.findall(u'user agent(?!s)', LOWFOLD[i])) for i in range(NS)]
M['act_sg_plus_pl'] = [M['act_sg'][i] + M['act'][i][1] - M['act'][i][0] for i in range(NS)]
M['act_sec'] = [[cnt_cur(IDW[i].lower(), nd) for nd in ACT] if IDW[i] else [0] * len(ACT)
                for i in range(NS)]
M['act_sec_tot'] = [sum(x) for x in M['act_sec']]
assert all(M['act_sg_plus_pl'][i] == 0 for i in range(NS)), M['act_sg_plus_pl']

# ---------- 判词里的数字: 谁给了时长/次数, 谁只给词(纯数字针一律带边界, 否则读到子串) ----------
NUM = [u'3600', u'120', u'50 requests per hour', u'2 minutes', u'delay-seconds',
       u'delta-seconds', u'HTTP-date']
M['num_fam'] = NUM
M['num'] = [[len(re.findall(nbound(nd.lower()), LOWFOLD[i])) if nd[0].isdigit()
             else cnt_cur(LOWFOLD[i], nd.lower()) for nd in NUM] for i in range(NS)]
M['num_raw'] = [[cnt_cur(LOWFOLD[i], nd.lower()) for nd in NUM] for i in range(NS)]
M['num_sub'] = [sum(M['num_raw'][i]) - sum(M['num'][i]) for i in range(NS)]
M['num_tot'] = [sum(x) for x in M['num']]
M['num_own'] = [[NUM[k] for k in range(len(NUM)) if M['num'][i][k]
                 and all(M['num'][j][k] == 0 for j in range(NS) if j != i)] for i in range(NS)]
# 同一支时长单位在两代规范里换了名: 2616 写 delta-seconds, 7231/9110 写 delay-seconds
M['num_rename'] = [M['num'][i][4] - M['num'][i][5] for i in range(NS)]

# ---------- 幂等节里点名的方法 ----------
METH = [u'GET', u'HEAD', u'PUT', u'DELETE', u'POST', u'TRACE', u'OPTIONS', u'CONNECT']
M['meth_fam'] = METH
M['meth_sec'] = [[ub(IDW[i], nd) for nd in METH] if IDW[i] else [0] * len(METH) for i in range(NS)]
M['meth_sec_n'] = [len([x for x in M['meth_sec'][i] if x]) for i in range(NS)]
M['meth_post_sec'] = [M['meth_sec'][i][4] for i in range(NS)]

assert M['sec_no'] == [u'9.1.2', u'4.2.2', None, None, u'9.2.2'], M['sec_no']
assert M['sec_end_kind'] == [u'heading', u'heading', None, None, u'heading'], M['sec_end_kind']

json.dump(M, io.open(u'corpus/_b80meas.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)
print(u'采集 B80: 五份 %s 字节 ⇎ 折平 %s 字符 ⇎ 摘壳 %s 字符' % (
    [format(x, u',') for x in M['bytes']], [format(x, u',') for x in M['fold_chars']],
    [format(x, u',') for x in M['sh_chars']]))
print(u'  换页符 %s ⇎ 页壳行 %s ⇎ 最长行 %s' % (M['ff'], M['shell_lines'], M['maxlen']))
print(u'  谱系 Obsoletes %s ⇎ Updates %s ⇎ 无向边 %s ⇎ 被更新者已作废 %s' % (
    M['obs_ids'], M['upd_ids'], M['lineage_no_edge'], M['upd_target_obsoleted']))
print(u'  年 %s（跨 %d 年, 逆序 %d 处）' % (M['years'], M['year_span'], M['year_inversions']))
print(u'  自动重试族: 逐行 %s ⇎ 折平 %s ⇎ 摘壳 %s ⇎ 增益 %s' % (
    M['auto_tot_line'], M['auto_tot_fold'], [sum(x) for x in M['auto_sh']], M['auto_gain']))
print(u'  idempotent: 折平 %s ⇎ 行内 %s ⇎ 短横跨行 %s ⇎ non-idempotent 被切 %s' % (
    M['idem_str'], M['idem_line_rows'], M['idem_line_occ'], M['hyb_straddle']))
print(u'  幂等节: 节号 %s ⇎ 同名标题命中 %s（目录行 %s）⇎ 节尾 %s ⇎ 行数 %s ⇎ 词数 %s ⇎ 句数 %s ⇎ 节内义务词 %s' % (
    M['sec_no'], M['sec_hit_n'], M['sec_toc_line'], M['sec_end_head'],
    M['sec_lines'], M['sec_words'], M['sec_sents'], M['tone_sec']))
print(u'  义务词(大写原面尺) %s ⇎ 折平尺 %s ⇎ 被换行切开 %s ⇎ 不分大小写 %s ⇎ 小写日常语 %s' % (
    M['tone_norm'], M['tone_norm_fold'], M['tone_straddle_k'], M['tone_case'], M['tone_word_lc']))
print(u'  义务词: 全文合计 %s ⇎ 节内 %s ⇎ 纯MUST账差 %s ⇎ 大小写尺多读 %s' % (
    M['tone_tot'], M['tone_sec_tot'], M['tone_must_ledger'], M['tone_case_gap']))
print(u'  搬字: 各对 %s ⇎ 最大 %s=%d（逐字节同 %d ⇎ 只归一同 %d）' % (
    M['pair_shared'], M['pair_max_lbl'], M['pair_max'], M['pair_max_byte'], M['pair_max_norm_only']))
print(u'  Retry-After: 词面 %s ⇎ ABNF 规则行 %s（取值式 %s ⇎ 引号式 %s ⇎ 竖线 %s ⇎ 斜杠 %s ⇎ 账 %s）⇎ 例子 3600 %s ⇎ 120 %s' % (
    M['ra_count'], M['ra_abnf_lines'], M['ra_abnf_forms'], M['ra_abnf_quoted'],
    M['ra_abnf_bar'], M['ra_abnf_slash'], M['ra_abnf_ledger'], M['ra_exp_3600'], M['ra_exp_120']))
print(u'  反向对照(带边界尺) %s ⇎ 零枚族数 %s ⇎ 独有 %s ⇎ 子串假阳性 %s' % (
    M['neg_bnd'], M['neg_zero_n'], M['neg_own_lbl'], M['neg_false_sub']))
print(u'  答句: 词数 %s ⇎ 跨行 %s ⇎ 单行读全 %d 份 ⇎ 跨页 %s ⇎ 判词短语被切 %s ⇎ 短语折平 %s' % (
    M['ans_words'], M['ans_span'], M['ans_one_line_n'], M['ans_page_break'],
    M['ph_straddle'], M['ph_fold']))
print(u'  “重来”用词 %s ⇎ 合计 %s ⇎ 零枚 %s ⇎ 独有 %s' % (
    M['reword'], M['reword_tot'], M['reword_zero_n'], M['reword_own']))
print(u'  禁令主语/POST: %s ⇎ 行尺 %s ⇎ 被切 %s ⇎ 命中针数 %s' % (
    M['subj'], M['subj_line'], M['subj_straddle'], M['subj_n']))
print(u'  节内点名方法 %s ⇎ 种类 %s ⇎ POST %s' % (M['meth_sec'], M['meth_sec_n'], M['meth_post_sec']))
print(u'  施事者 %s ⇎ 单数(带零宽) %s ⇎ 节内 %s ⇎ 节内合计 %s' % (
    M['act'], M['act_sg'], M['act_sec'], M['act_sec_tot']))
print(u'  数字族(带边界) %s ⇎ 裸串 %s ⇎ 子串多读 %s ⇎ 合计 %s ⇎ 独有 %s ⇎ delay−delta %s' % (
    M['num'], M['num_raw'], M['num_sub'], M['num_tot'], M['num_own'], M['num_rename']))
print(u'  状态码定义行 %s（目录行另 %s）⇎ 点名的码 %s' % (M['code_defined_n'], M['code_toc'], M['code_defined_lbl']))
print(u'  括号引用 %s ⇎ 行尺 %s ⇎ 被切 %s' % (M['paren'], M['paren_line'], M['paren_straddle']))

