# -*- coding: utf-8 -*-
"""采集遍(B81, 第一套实现): “一个 AQM 该把排队延迟压到多少、依据什么”由五份一手文书各答一遍
7567(2015 BCP) ⇎ madp(2016 论文) ⇎ 8033(2017 实验规范) ⇎ cake(2018 论文) ⇎ 8289(2018 标准轨道)。

五份来自两种序列化, 面量因此要分两套谓词: 三份 RFC Editor txt 是 72 列硬换行 ⇎ 换页符独占整行
⇎ “[Page N]” 脚注 ⇎ 眉行 ⇎ 纯 ASCII ⇎ LF 行尾; 两份本机 pdftotext 抽的 arXiv PDF 是整段落在一行
⇎ 换页符粘在下一页第一行行首(连页码一起粘走: “\\x0c2”) ⇎ 逐行 CRLF ⇎ 面上留着连字 ﬁ ﬂ 与弯引号。
本条的档位(每句都对应采集遍量出的数, 量不出的已删):
(1) 拼写换代: 五份里只有 madp(queuing 76 ⇎ queueing 0)与 8289(0 ⇎ 8)一边倒, 7567 是 1:19、
    8033 是 26:1、cake 是 1:22 —— 少数拼法每份都留 1~2 枚, 单串检索必漏;
    术语换代不是“一边倒”而是斜度跨两个数量级: 同一个量 8289 说 delay 50 次 ⇎ latency 1 次(50 倍),
    8033 说 73:78(1.1 倍), madp 94:12(7.8 倍), cake 4:28 —— 五份里少数词最少也留 1 枚(没有一边倒),
    斜度却从 1.1 倍拉到 50 倍;
    第三种坏只在论文面: pdftotext 把字距拉开, “RTT” 抽成 “RT T”, 大写尺读 madp 14 枚别处 0 枚,
    改用小写不敏感的 “rt t” 会在 7567 的 transport ⇎ report ⇎ short TCP 词中间多吃 7 枚假命中;
    连字把 configuration 里的 fi 并成单码位 ⇒ 子串 needle 要先拆字: cake 的 configuration 在未拆字面上读到 0 枚,
    拆字后读到 7 枚; madp 的 53 枚 ﬁ 一枚也不落在这个词上(它通篇不写 config* 族)——拆字尺的涨是逐词的事;
(2) 给数字的份各用一种单位制, 而且单位尺本身有两把: 8033 面上 “ms” 作子串读到 13 枚(藏在 terms、
    problems 里), 作整词读到 0 枚, 全称 milliseconds 14 枚 ⇎ 缩写 0 枚 ⇒ “15 ms” 针读它为零,
    必须换 “15 milliseconds”(10 枚); 同一把尺换词界就换答案。8033 并按场景换两个数量级
    (15 ms ⇎ 15 µs), 8289 把 TARGET 定义成 RTT 的百分比, madp 报的是“别人的默认值”, cake 只报实测,
    7567 全文一枚带单位的时长也不给(放宽到裸 “s” 才读到一对, 还是年代 “1980s”);
(3) 同一个 100 ms 在两份里扮演六种角色(8289 的 INTERVAL 规定值 ⇎ 8289 的过丢包失效界 ⇎ 8289 的 RTT
    天花板 ⇎ madp 里 CoDel 的 RTT 假设 ⇎ madp 里 PIE 的突发容忍 ⇎ madp 里 MADPIE 不起作用的界),
    逐角色立针而不共用一个键;
(4) 判词被三种东西切开, 三种切法分开记账(27 根语义针): 逐行尺读到 19 根 ⇎ 漏 8 根;
    折平尺多读 6 根 —— 其中 6 根里 5 根在 8289、1 根在 8033, 是 72 列硬换行把 MUST 级句子切成
    2~5 行(MUST 词本身也会被切: 8289 的 SHOULD 由 14 枚涨到 15 枚), 剩下 1 根不是切分而是
    7567 的 4.3 标题在目录与正文各印一次; 摘壳折平尺再多读 2 根, 才是页壳从句子中间插进去
    (8289 “…that gives consistently | Nichols, et al. Experimental [Page 9] RFC 8289 … | high utilization…”、
    8033 “…respectively. | Pan, et al. Experimental [Page 17] RFC 8033 … | Since the data path…”),
    拆字尺相对摘壳尺在这 27 根针上涨 0 枚(针面不含连字), 它的涨只落在 cake 的 configuration 一词上(0 枚 ⇎ 7 枚);
(5) “免配置”住在三种位置, 而“默认值住在专节”这个直觉是错的: 7567 把规范语句写进节标题本身
    (4.3 标题占一行, 含 SHOULD NOT), 8289 写 “CoDel can be parameter-free for consumer use”,
    其导出数值句(“minimum TARGET of 5 ms and INTERVAL of 100 ms”)落在 §4 “Overview of the CoDel AQM”
    第 702 行, 专讲该参数的 §4.3 “Setting TARGET” 要到第 774 行才出现 ⇒ 按标题切窗自动把锚归给总述节;
    8033 写 “PIE is intended to be self-configuring” 却随即在 §8 部署节给出双档默认值,
    madp 引述别人的默认值则住在 §I 引言; 只有 cake 通篇不作免配置宣称(宣称 0 枚);
(6) 同一百分比 5-10% 在 8289 一份里挂两个不同的量(“5-10% of the connection round-trip time” ⇎
    “some other value in the 5-10% of INTERVAL”), 论文面(madp)说 PIE 默认 20 ms/突发 100 ms,
    晚一年的规范面(8033)写 15 ms/150 ms —— 两代默认值不同档。
7567 的规范性标题还与推荐清单同形, 标题尺要靠缩进与编号级数分三档: 缩进多级的是目录行(4 枚)
⇎ 缩进单级的是推荐清单列表项(6 枚)⇎ 顶格多级的是真节标题(4 枚), 剩下 1 枚是以 “3168 by allowing…”
打头的正文续行(数字开头即撞标题形); 目录行的引道符是空格隔开的点(“. . . .”), 常规 “\\.{3,}” 尺
在 4 枚目录行里一枚也读不到, 换成 “(?:\\.\\s*){3,}” 也只读到 1 枚 —— 其余 3 枚的点线被 72 列换行
推到了下一行, 所以目录档只能靠缩进+编号级数认, 不能靠引道符认。
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'7567', u'madp', u'8033', u'cake', u'8289']
SRC = [u'corpus/raw/qdelay/rfc7567.txt', u'corpus/raw/qdelay/piehdp.txt',
       u'corpus/raw/qdelay/rfc8033.txt', u'corpus/raw/qdelay/cake.txt',
       u'corpus/raw/qdelay/rfc8289.txt']
FAM = [u'rfc', u'paper', u'rfc', u'paper', u'rfc']
IDS = [u'7567', u'', u'8033', u'', u'8289']
YR = [2015, 2016, 2017, 2018, 2018]
NS = 5
RFCI = [i for i in range(NS) if FAM[i] == u'rfc']
PAPI = [i for i in range(NS) if FAM[i] == u'paper']
M = {}


def cnt_cur(hay, nd):
    """左起非重叠游标计数(第一套实现的唯一计数原语, 后面所有尺都走它)。"""
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def fold(s):
    return u' '.join(s.split())


def ub(hay, nd):
    return len(re.findall(u'(?<![A-Za-z])' + re.escape(nd) + u'(?![A-Za-z])', hay))


# ---------- 面量 ----------
T, L, BYT, RAWL = [], [], [], []
for p in SRC:
    b = io.open(p, u'rb').read()
    BYT.append(b)
    t = b.decode(u'utf-8', u'replace')
    T.append(t)
    # 两份论文由本机 pdftotext 在 Windows 上抽出, 行尾是 CRLF; 三份 RFC txt 是纯 LF。
    # 行尺一律在“剥掉行尾回车”的面上量, 回车本身单独立账(cr ⇎ newlines 两把尺)。
    rl = t.split(NL)
    RAWL.append(rl)
    L.append([x[:-1] if x.endswith(u'\r') else x for x in rl])
M['label'] = LBL
M['src'] = SRC
M['fam'] = FAM
M['ids'] = IDS
M['years'] = YR
M['bytes'] = [len(b) for b in BYT]
M['chars'] = [len(t) for t in T]
M['lines'] = [len(L[i]) for i in range(NS)]
M['newlines'] = [T[i].count(NL) for i in range(NS)]
M['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NS)]
M['blank'] = [M['lines'][i] - M['nonblank'][i] for i in range(NS)]
M['maxlen'] = [max(len(x) for x in L[i]) for i in range(NS)]
M['over72'] = [len([x for x in L[i] if len(x) > 72]) for i in range(NS)]
M['ff'] = [T[i].count(u'\x0c') for i in range(NS)]
M['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NS)]
M['ff_inline'] = [M['ff'][i] - M['ff_exact'][i] for i in range(NS)]
M['ff_lead'] = [len([x for x in L[i] if x.startswith(u'\x0c')]) for i in range(NS)]
M['cr'] = [T[i].count(u'\r') for i in range(NS)]
M['cr_rows'] = [len([x for x in RAWL[i] if x.endswith(u'\r')]) for i in range(NS)]
M['nul'] = [BYT[i].count(b'\x00') for i in range(NS)]
M['nonascii'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(NS)]
M['bom'] = [1 if BYT[i][:3] == b'\xef\xbb\xbf' else 0 for i in range(NS)]
M['tail_nl'] = [1 if T[i].endswith(NL) else 0 for i in range(NS)]
M['byte_cp_delta'] = [M['bytes'][i] - M['chars'][i] for i in range(NS)]
M['crlf_rows'] = [1 if M['cr'][i] == M['newlines'][i] else 0 for i in range(NS)]
for i in range(NS):
    assert M['lines'][i] == M['newlines'][i] + 1, i
    assert M['cr'][i] == M['cr_rows'][i], i                       # 回车数=带回车的行数(没有行中回车)
assert M['nul'] == [0] * NS and sum(M['bom']) == 0
# 行尾制: 三份 RFC 纯 LF ⇎ 两份论文逐行 CRLF(“无回车”⇎“每行都有回车”, 没有中间档)
assert M['cr'] == [0, 675, 0, 333, 0], M['cr']
assert [M['crlf_rows'][i] for i in PAPI] == [1, 1] and [M['crlf_rows'][i] for i in RFCI] == [0, 0, 0]
# 字节−码位差只由非 ASCII 贡献(回车是 ASCII: 一字节一码位)
M['utf8_extra'] = [sum(len(c.encode(u'utf-8')) - 1 for c in T[i] if ord(c) > 127) for i in range(NS)]
M['byte_cp_ledger'] = [M['byte_cp_delta'][i] - M['utf8_extra'][i] for i in range(NS)]
assert M['byte_cp_ledger'] == [0] * NS, M['byte_cp_ledger']
assert M['byte_cp_delta'] == [0, 393, 0, 549, 0], M['byte_cp_delta']
# 换页符两档: RFC 面每枚 FF 独占一行(页壳), 论文面一枚也不独占而是粘在下一页第一行行首
# (粘住的正是页码 “\x0c2” ⇎ 附录标题 “\x0cA. Bandwidth Shaping”), 各留一枚在文件末尾成空页
assert M['ff_exact'] == [31, 1, 30, 1, 25], M['ff_exact']
assert M['ff_inline'] == [0, 5, 0, 5, 0], M['ff_inline']
assert [M['ff_lead'][i] == M['ff'][i] for i in PAPI] == [True, True]
assert [M['ff_lead'][i] for i in RFCI] == [31, 30, 25]

# ---------- 非 ASCII 的四类成分(转写层必须点名) ----------
# 只有连字 ﬁ/ﬂ 会吃掉子串检索(词内两字母并为单码位); 希腊符号是论文面的参数名; 弯引号与长划是排版残片;
# 其余(变音字母 ⇎ 数学符号 ⇎ 项目符)住在作者名、公式与图注里。四类相加 = 非 ASCII 枚数(真分割, 能失败)。
PAIR = [u'ﬁ', u'ﬂ']
GREEK = [u'τ', u'λ', u'α', u'β']
DASHQ = [u'’', u'“', u'”', u'‘', u'—', u'–', u'−']
LIGS = [(u'ﬁ', u'fi'), (u'ﬂ', u'fl'), (u'’', u"'"), (u'—', u'-'), (u'–', u'-'),
        (u'“', u'"'), (u'”', u'"'), (u'−', u'-'), (u'‘', u"'")]
NA = [[c for c in T[i] if ord(c) > 127] for i in range(NS)]
M['lig_pair'] = [[T[i].count(a) for a in PAIR] for i in range(NS)]
M['lig_total'] = [sum(x) for x in M['lig_pair']]
M['na_greek'] = [len([c for c in NA[i] if c in GREEK]) for i in range(NS)]
M['na_dashq'] = [len([c for c in NA[i] if c in DASHQ]) for i in range(NS)]
M['na_total'] = [len(x) for x in NA]
M['na_other'] = [len([c for c in NA[i] if c not in PAIR + GREEK + DASHQ]) for i in range(NS)]
M['na_other_set'] = [sorted(set(c for c in NA[i] if c not in PAIR + GREEK + DASHQ)) for i in range(NS)]
M['na_ledger'] = [M['lig_total'][i] + M['na_greek'][i] + M['na_dashq'][i] + M['na_other'][i]
                  - M['na_total'][i] for i in range(NS)]
assert M['na_total'] == M['nonascii'] and M['na_ledger'] == [0] * NS, M['na_ledger']
assert [M['na_total'][i] for i in RFCI] == [0, 0, 0]
assert M['lig_pair'] == [[0, 0], [53, 31], [0, 0], [86, 89], [0, 0]], M['lig_pair']
assert [M['na_greek'][i] for i in PAPI] == [33, 0], M['na_greek']     # 希腊符号只在 madp 面上

# ---------- 页壳行账(两种序列化两套谓词, 各自闭合) ----------
M['pg_lines'] = [len([x for x in L[i] if re.search(u'\\[Page \\d+\\]', x)]) for i in range(NS)]
M['hdr_lines'] = [len([x for x in L[i] if re.match(u'^RFC \\d+\\b', x)]) for i in range(NS)]
M['hdr_lines_tight'] = [len([x for x in L[i]
                             if re.match(u'^RFC \\d{4} +\\S.*((19|20)\\d\\d)\\s*$', x)]) for i in range(NS)]
# 页码行两把尺: 独立数字行(naive 谓词) ⇎ 只有行首带 FF 的数字行(真页码)
M['pgnum_naive'] = [len([x for x in L[i] if re.match(u'^\\s*\\d+\\s*$', x)]) for i in range(NS)]
M['pgnum_ffled'] = [len([x for x in L[i] if re.match(u'^\\x0c\\d+\\s*$', x)]) for i in range(NS)]
M['pgnum_overstrip'] = [M['pgnum_naive'][i] - M['pgnum_ffled'][i] for i in range(NS)]
for i in range(NS):
    # RFC 面每页一枚 “[Page N]” 脚注 ⇎ 论文面一枚也没有(页码被 FF 粘走); 眉行数 = 页数 − 1(首页是题录块)
    assert M['pg_lines'][i] == (M['ff'][i] if FAM[i] == u'rfc' else 0), i
    if FAM[i] == u'rfc':
        assert M['hdr_lines_tight'][i] == M['ff'][i] - 1, i


def is_shell(x, fam):
    if fam == u'rfc':
        return (re.search(u'\\[Page \\d+\\]', x) is not None
                or re.match(u'^RFC \\d{4} +\\S.*((19|20)\\d\\d)\\s*$', x) is not None
                or x.strip() == u'')
    return re.match(u'^\\x0c\\d+\\s*$', x) is not None or x.strip() == u''


M['shell_lines'] = [len([x for x in L[i] if is_shell(x, FAM[i])]) for i in range(NS)]
M['shell_ledger'] = [M['shell_lines'][i] - M['blank'][i]
                     - (M['pg_lines'][i] + M['hdr_lines_tight'][i] if FAM[i] == u'rfc'
                        else M['pgnum_ffled'][i]) for i in range(NS)]
assert M['shell_ledger'] == [0] * NS, M['shell_ledger']
assert M['shell_lines'] == [598, 310, 662, 115, 429], M['shell_lines']
# naive 页码谓词在论文面会多吃表格数据行(数字单元独占一行), 在 RFC 面一枚也吃不到
assert M['pgnum_ffled'] == [0, 5, 0, 0, 0] and M['pgnum_overstrip'] == [0, 97, 0, 18, 0]
assert [M['pgnum_naive'][i] for i in RFCI] == [0, 0, 0]

FOLD = [fold(T[i]) for i in range(NS)]
LOWFOLD = [x.lower() for x in FOLD]
SH = [fold(NL.join(x for x in L[i] if not is_shell(x, FAM[i]))) for i in range(NS)]
M['fold_chars'] = [len(FOLD[i]) for i in range(NS)]
M['sh_chars'] = [len(SH[i]) for i in range(NS)]
M['sh_minus_fold'] = [M['sh_chars'][i] - M['fold_chars'][i] for i in range(NS)]
# 剥壳在折平面上少读的字符数: 只由“有内容的壳行”贡献(空行折平本来就被吞, 剥不剥一样)。
# cake 的 115 行壳全是空行 ⇒ 差为 0, 它的页家具只剩换页符本身, 而 fold 把换页符当空白吞掉。
M['shell_text_chars'] = [-(M['sh_minus_fold'][i]) for i in range(NS)]
M['shell_nonblank'] = [len([x for x in L[i] if is_shell(x, FAM[i]) and x.strip() != u''])
                       for i in range(NS)]
M['shell_blank_only'] = [1 if M['shell_nonblank'][i] == 0 else 0 for i in range(NS)]
assert M['sh_minus_fold'] == [-3311, -10, -1824, 0, -1638], M['sh_minus_fold']
assert M['shell_nonblank'] == [61, 5, 59, 0, 49], M['shell_nonblank']
assert M['shell_blank_only'] == [0, 0, 0, 1, 0]
assert all(M['sh_minus_fold'][i] <= 0 for i in range(NS))
LOW_SH = [x.lower() for x in SH]

# ---------- 拆字面: 连字/弯引号还原后的第三把尺 ----------
LIG = [FOLD[i] for i in range(NS)]
for a, b in LIGS:
    LIG = [x.replace(a, b) for x in LIG]
LOWLIG = [x.lower() for x in LIG]
SHLIG = [SH[i] for i in range(NS)]
for a, b in LIGS:
    SHLIG = [x.replace(a, b) for x in SHLIG]
LOW_SHLIG = [x.lower() for x in SHLIG]
assert [cnt_cur(LOWLIG[i], u'configuration') - cnt_cur(LOWFOLD[i], u'configuration')
        for i in RFCI] == [0, 0, 0]
assert [cnt_cur(LOWLIG[i], u'configuration') - cnt_cur(LOWFOLD[i], u'configuration')
        for i in range(NS)] == [0, 0, 0, 7, 0]


# ---------- 拼写换代 ⇎ 术语换代(一边倒要能数) ----------
SPELL = [u'queuing', u'queueing', u'queue delay', u'queuing delay', u'queueing delay']
M['spell_fam'] = SPELL
M['spell'] = [[cnt_cur(LOW_SHLIG[i], nd) for nd in SPELL] for i in range(NS)]
M['spell_side'] = [u'queuing' if M['spell'][i][0] > M['spell'][i][1] else
                   (u'queueing' if M['spell'][i][1] > M['spell'][i][0] else u'两拼都有')
                   for i in range(NS)]
M['spell_minor'] = [min(M['spell'][i][0], M['spell'][i][1]) for i in range(NS)]
M['spell_major'] = [max(M['spell'][i][0], M['spell'][i][1]) for i in range(NS)]
M['spell_onel-sided_n'] = len([x for x in M['spell_minor'] if x == 0])
# 短语档: “queue/queuing delay”三式相加与两式相加不等, 因为裸 “queue delay” 与带拼式重叠
M['spell_phrase_sum'] = [sum(M['spell'][i][2:]) for i in range(NS)]
M['spell_phrase_two'] = [M['spell'][i][3] + M['spell'][i][4] for i in range(NS)]
assert M['spell_major'] == [19, 76, 26, 22, 8], M['spell_major']
assert M['spell_minor'] == [1, 0, 1, 1, 0] and M['spell_onel-sided_n'] == 2
assert M['spell_phrase_sum'] == [3, 77, 3, 1, 8] and M['spell_phrase_two'] == [2, 76, 0, 1, 2]
TERM = [u'delay', u'latency', u'queuing delay', u'queueing delay', u'queue delay', u'latency spike',
        u'induced latency', u'sojourn']
M['term_fam'] = TERM
M['term'] = [[cnt_cur(LOW_SHLIG[i], nd) for nd in TERM] for i in range(NS)]
M['term_side'] = [(u'latency' if M['term'][i][1] > M['term'][i][0] else u'delay') for i in range(NS)]
# 斜度尺: 多数词/少数词。少数词全不为零 ⇒ “逐份一边倒”不成立; 但斜度跨 1.1~50 倍
M['term_minor'] = [min(M['term'][i][0], M['term'][i][1]) for i in range(NS)]
M['term_major'] = [max(M['term'][i][0], M['term'][i][1]) for i in range(NS)]
M['term_skew'] = [round(float(M['term_major'][i]) / M['term_minor'][i], 1) for i in range(NS)]
# 只在一份里出现的术语(第五种名字): sojourn 只在 8289(39 枚), 其余四份 0 枚
M['term_own'] = [[TERM[k] for k in range(len(TERM)) if M['term'][i][k]
                  and all(M['term'][j][k] == 0 for j in range(NS) if j != i)] for i in range(NS)]
assert M['term_minor'] == [20, 12, 73, 4, 1] and M['term_skew'] == [1.8, 7.8, 1.1, 7.0, 50.0], M['term_skew']
assert M['term_own'] == [[], [u'queuing delay'], [], [u'latency spike', u'induced latency'], [u'sojourn']]
assert [M['term'][i][7] for i in range(NS)] == [0, 0, 0, 0, 39]      # 同一个量的第五个名字

# ---------- 字距拉开: pdftotext 把 “RTT” 抽成 “RT T” ----------
M['rtt_tight'] = [cnt_cur(LOW_SHLIG[i], u'rtt') for i in range(NS)]
# 大写尺: 拉开的字距保持大写, 所以 “RT T” 只能按大小写敏感检索(五份里只有 madp 有, 14 枚)
M['rtt_kern'] = [cnt_cur(SHLIG[i], u'RT T') for i in range(NS)]
# 小写不敏感的裸子串尺: 会在 transport ⇎ report ⇎ short TCP 这类词的中间多吃假命中
M['rtt_loose'] = [cnt_cur(LOW_SHLIG[i], u'rt t') for i in range(NS)]
M['rtt_loose_false'] = [M['rtt_loose'][i] - M['rtt_kern'][i] for i in range(NS)]
M['rtt_split_share'] = [M['rtt_tight'][i] + M['rtt_kern'][i] for i in range(NS)]
assert M['rtt_kern'] == [0, 14, 0, 0, 0] and M['rtt_tight'] == [11, 79, 0, 0, 29], M['rtt_kern']
assert M['rtt_loose'] == [7, 14, 0, 1, 0] and M['rtt_loose_false'] == [7, 0, 0, 1, 0]
assert [M['rtt_tight'][i] for i in (2, 3)] == [0, 0]                 # 8033/cake 面上根本没有 “RTT”

# ---------- 单位制 ⇎ 数值集(两把尺: 严单位 ⇎ 宽到裸 s) ----------
UNIT = [u'ms', u'milliseconds', u'microseconds', u'second', u'µs', u'%']
M['unit_fam'] = UNIT
M['unit'] = [[cnt_cur(LOW_SHLIG[i], nd) for nd in UNIT] for i in range(NS)]
# 同一批单位换整词尺(与子串尺同面同大小写, 差只由词边界贡献): 8033 的 “ms” 子串 13 枚全是
# terms/problems 的词中碎片, 整词读 0; “second” 整词在多数份读 0 —— 词尾 s 被否定前瞻挡掉
M['unit_word'] = [[ub(LOW_SHLIG[i], nd) for nd in UNIT] for i in range(NS)]
M['unit_sub_over'] = [M['unit'][i][0] - M['unit_word'][i][0] for i in range(NS)]
M['unit_word_sec_sub'] = [len(re.findall(u'(?<![A-Za-z])seconds(?![A-Za-z])', LOW_SHLIG[i]))
                          for i in range(NS)]
assert M['unit_word'] == [[0, 0, 0, 4, 0, 0], [121, 0, 0, 2, 0, 14], [0, 14, 3, 0, 0, 3],
                          [9, 0, 0, 1, 0, 4], [21, 2, 0, 4, 0, 11]], M['unit_word']
assert M['unit_sub_over'] == [84, 8, 13, 13, 21], M['unit_sub_over']
NUMRE = re.compile(u'(?<![\\d.])(\\d+(?:[.,]\\d+)?) ?(ms|milliseconds|microseconds|seconds)\\b')
NUMRE_S = re.compile(u'(?<![\\d.])(\\d+(?:[.,]\\d+)?) ?(ms|milliseconds|microseconds|second|s)\\b')
M['numvals'] = [sorted(set((v, u) for v, u in NUMRE.findall(LOW_SHLIG[i]))) for i in range(NS)]
M['numval_n'] = [len(x) for x in M['numvals']]
M['numval_s_pairs'] = [sorted(set((v, u) for v, u in NUMRE_S.findall(LOW_SHLIG[i]))) for i in range(NS)]
# 两把尺互不包含: 放宽到裸 “s” 会多读年代(7567 的 “1980s”), 却把 “5 seconds” 读丢
# (选择支 “second” 后跟一枚 s 使 \\b 失败, 退回单字母 “s” 又撞上后续字母) —— 宽尺不是超集
M['numval_s_extra'] = [[x for x in M['numval_s_pairs'][i] if x not in M['numvals'][i]]
                       for i in range(NS)]
M['numval_s_lost'] = [[x for x in M['numvals'][i] if x not in M['numval_s_pairs'][i]]
                      for i in range(NS)]
assert M['numval_n'] == [0, 19, 4, 6, 6], M['numval_n']       # 7567: 一枚带单位的时长也没有
assert M['numval_s_pairs'][0] == [(u'1980', u's')] and [len(x) for x in M['numval_s_extra']] == [1, 4, 0, 0, 2]
assert [len(x) for x in M['numval_s_lost']] == [0, 0, 0, 1, 0]
# 8033 通篇不写缩写: 面上只有全称, 一把 “15 ms” 检索读它为零
assert [x for x in M['numvals'][2]] == [(u'15', u'microseconds'), (u'15', u'milliseconds'),
                                        (u'150', u'microseconds'), (u'150', u'milliseconds')]

# ---------- 数字族(字面针): 同一个 “100 ms” 在不同份里是不同东西 ----------
NUM = [u'5 ms', u'15 ms', u'100 ms', u'20 ms', u'30 ms', u'50 ms', u'200 ms', u'500 ms',
       u'10 ms', u'300 ms', u'15 milliseconds', u'150 milliseconds', u'15 microseconds',
       u'150 microseconds', u'10 mbps', u'5-10%', u'90 ms']
M['num_fam'] = NUM
M['num'] = [[cnt_cur(LOW_SHLIG[i], nd) for nd in NUM] for i in range(NS)]
M['num_raw'] = [[cnt_cur(LOWFOLD[i], nd) for nd in NUM] for i in range(NS)]
M['num_lig_gap'] = [sum(M['num'][i]) - sum(M['num_raw'][i]) for i in range(NS)]
M['num_nofold'] = [[k for k in range(len(NUM)) if M['num'][i][k] and not M['num_raw'][i][k]]
                   for i in range(NS)]
M['num_tot'] = [sum(x) for x in M['num']]
M['num_own'] = [[NUM[k] for k in range(len(NUM)) if M['num'][i][k]
                 and all(M['num'][j][k] == 0 for j in range(NS) if j != i)] for i in range(NS)]
M['num_zero_n'] = [len([k for k in range(len(NUM)) if M['num'][i][k] == 0]) for i in range(NS)]
M['num_shared_n'] = [len([k for k in range(len(NUM)) if sum(1 for j in range(NS) if M['num'][j][k]) > 1])
                     for i in range(NS)]
# 7567 在 17 枚数字针上全零(它一枚时长也不给); “10 mbps” 只属于 cake+madp, 8289 面上 0 枚
assert M['num'][0] == [0] * len(NUM) and M['num_zero_n'][0] == 17
assert M['num_own'] == [[], [u'20 ms', u'30 ms', u'90 ms'],
                        [u'15 milliseconds', u'150 milliseconds', u'15 microseconds',
                         u'150 microseconds'], [u'200 ms'], [u'10 ms', u'5-10%']], M['num_own']
assert M['num_lig_gap'] == [0] * NS and M['num_nofold'] == [[], [], [], [], []]
assert M['num_shared_n'] == [6] * NS

# ---------- 角色针(每根带语义角色, 三把尺: 逐行 ⇎ 折平 ⇎ 摘壳折平) ----------
ROLE = [
    (u'7567', u'免配置写成规范标题(目录与正文各印一次)', u'aqm algorithm deployment should not require operational tuning'),
    (u'7567', u'免配置写成推荐清单', u'aqm algorithms should not require tuning of initial or'),
    (u'7567', u'定性作答(全文无时长数值)', u'undue loss or undue round-trip delay'),
    (u'madp', u'引述 PIE 的默认目标', u'its default target delay of 20 ms'),
    (u'madp', u'引述 PIE 的突发容忍', u'burst allowance of 100 ms'),
    (u'madp', u'引述 CoDel 的 RTT 假设', u'round trip time (rtt) is 100 ms'),
    (u'madp', u'MADPIE 不起作用的界', u'does not affect pie'),
    (u'madp', u'新参数只加一个', u'requires only one additional parameter'),
    (u'8033', u'双档默认(非数据中心)', u'defaulted to 15 milliseconds and 150 milliseconds'),
    (u'8033', u'双档默认(数据中心)', u'15 microseconds and 150 microseconds'),
    (u'8033', u'两个数量级之差', u'a reduction of two orders of magnitude'),
    (u'8033', u'免配置宣称', u'users should not need to configure any design parameters'),
    (u'cake', u'实测基线', u'10 mbps link with 50 ms baseline latency'),
    (u'cake', u'稳态', u'steady state around 200 ms'),
    (u'cake', u'振荡区间', u'oscillating between 50 and 500 ms'),
    (u'cake', u'高优先级流的代价', u'latency increase is only 5 ms'),
    (u'8289', u'TARGET 的定义式(挂 RTT)', u'an ideal target is 5-10% of the connection round-trip time'),
    (u'8289', u'同一百分比改挂 INTERVAL', u'other value in the 5-10% of interval'),
    (u'8289', u'RTT 天花板', u'most unbloated rtts to have a ceiling of 100 ms'),
    (u'8289', u'由此导出的下限', u'minimum target of 5 ms and interval of 100 ms'),
    (u'8289', u'INTERVAL 的规定值', u'interval should have a value of 100 ms'),
    (u'8289', u'过丢包的失效界', u'tcp has an rtt longer than 100 ms'),
    (u'8289', u'实验跨度(窄)', u'the range from 10 ms to 300 ms'),
    (u'8289', u'实验跨度(宽)', u'range of rtts from 10 ms to 1 second'),
    (u'8289', u'免配置宣称', u'codel can be parameter-free for consumer use'),
    (u'8289', u'被页壳从中间切开的判词', u'that gives consistently high utilization while controlling delay'),
    (u'8033', u'被页壳从中间切开的判词', u'data-center switches, respectively. since the data path'),
]
M['role_src'] = [x[0] for x in ROLE]
M['role_kind'] = [x[1] for x in ROLE]
ROLEN = [x[2] for x in ROLE]
M['role_fam'] = ROLEN
M['role_line'] = [[sum(cnt_cur(y.lower(), nd) for y in L[i]) for nd in ROLEN] for i in range(NS)]
M['role_fold'] = [[cnt_cur(LOWFOLD[i], nd) for nd in ROLEN] for i in range(NS)]
LOW_SH = [x.lower() for x in SH]
M['role_sh'] = [[cnt_cur(LOW_SH[i], nd) for nd in ROLEN] for i in range(NS)]
M['role_lig'] = [[cnt_cur(LOW_SHLIG[i], nd) for nd in ROLEN] for i in range(NS)]
# 三把尺的间距各归一种转写损伤, 分开记账: 硬换行(fold−line 里 line=0 的部分) ⇎
# 目录与正文同印(fold−line 里 line>0 的多余枚) ⇎ 页壳(sh−fold) ⇎ 连字(lig−sh)
M['role_wrap'] = [[k for k in range(len(ROLEN)) if M['role_src'][k] == LBL[i]
                   and M['role_line'][i][k] == 0 and M['role_fold'][i][k] >= 1] for i in range(NS)]
M['role_dup'] = [[k for k in range(len(ROLEN)) if M['role_src'][k] == LBL[i]
                  and M['role_line'][i][k] >= 1 and M['role_fold'][i][k] > M['role_line'][i][k]]
                 for i in range(NS)]
M['role_wrap_n'] = [len(x) for x in M['role_wrap']]
M['role_dup_n'] = [len(x) for x in M['role_dup']]
M['role_straddle'] = [sum(M['role_fold'][i]) - sum(M['role_line'][i]) for i in range(NS)]
M['role_straddle_ledger'] = [M['role_straddle'][i] - M['role_wrap_n'][i] - M['role_dup_n'][i]
                             for i in range(NS)]
M['role_shell_gain'] = [sum(M['role_sh'][i]) - sum(M['role_fold'][i]) for i in range(NS)]
M['role_lig_gain'] = [sum(M['role_lig'][i]) - sum(M['role_sh'][i]) for i in range(NS)]
assert M['role_straddle_ledger'] == [0] * NS, M['role_straddle_ledger']
assert M['role_wrap_n'] == [0, 0, 1, 0, 5] and M['role_dup_n'] == [1, 0, 0, 0, 0], M['role_wrap_n']
assert M['role_shell_gain'] == [0, 0, 1, 0, 1] and M['role_lig_gain'] == [0] * NS
M['role_shell_only'] = [k for k in range(len(ROLEN))
                        if M['role_fold'][LBL.index(M['role_src'][k])][k] == 0
                        and M['role_sh'][LBL.index(M['role_src'][k])][k] == 1]
M['role_line_miss'] = [k for k in range(len(ROLEN))
                       if M['role_line'][LBL.index(M['role_src'][k])][k] == 0]
M['role_own'] = [[k for k in range(len(ROLEN)) if M['role_lig'][i][k]
                  and all(M['role_lig'][j][k] == 0 for j in range(NS) if j != i)] for i in range(NS)]
M['role_hit_other'] = [[k for k in range(len(ROLEN)) if M['role_lig'][i][k] and M['role_src'][k] != LBL[i]]
                       for i in range(NS)]
for k in range(len(ROLEN)):
    i = LBL.index(M['role_src'][k])
    assert M['role_lig'][i][k] >= 1, (k, ROLEN[k])          # 每根针在自己那份的最宽面读得到
    # 且只在自己那份读得到(自己份内读两次的是“目录⇎正文”同印的标题针)
    assert sum(M['role_lig'][j][k] for j in range(NS)) == M['role_lig'][i][k], (k, ROLEN[k])
M['role_multi'] = [(M['role_src'][k], M['role_kind'][k], M['role_lig'][LBL.index(M['role_src'][k])][k])
               for k in range(len(ROLEN)) if M['role_lig'][LBL.index(M['role_src'][k])][k] > 1]
M['role_line_miss_n'] = len(M['role_line_miss'])
M['role_shell_only_n'] = len(M['role_shell_only'])
M['role_line_read_n'] = len(ROLEN) - M['role_line_miss_n']
# 逐行尺漏掉的针必须正好等于“被硬换行切开”+“被页壳切开”两类, 没有第三种原因
WRAPK = sorted([k for x in M['role_wrap'] for k in x])
SHELLK = sorted([k for i in range(NS) for k in range(len(ROLEN))
                 if M['role_src'][k] == LBL[i]
                 and M['role_fold'][i][k] == 0 and M['role_sh'][i][k] == 1])
M['role_miss_ledger'] = sorted(WRAPK + SHELLK) == sorted(M['role_line_miss'])
assert M['role_miss_ledger'] and M['role_line_miss'] == [11, 18, 19, 20, 21, 24, 25, 26], \
    M['role_line_miss']
# 100 ms 一族: 六根针共享同一个字面串, 语义角色互不相干
M['ms100_roles'] = [(M['role_src'][k], M['role_kind'][k]) for k in range(len(ROLEN))
                    if u'100 ms' in ROLEN[k]]
assert len(M['ms100_roles']) == 6 and len(set(x[1] for x in M['ms100_roles'])) == 6
M['ms100_count'] = [M['num'][i][NUM.index(u'100 ms')] for i in range(NS)]

# ---------- 参数名: 规范用大写全名 ⇎ 论文用希腊符号 ⇎ 论文面还留着实现名 ----------
PAR = [u'TARGET', u'INTERVAL', u'QDELAY_REF', u'MAX_BURST', u'τ', u'λ', u'α', u'β', u'pdrop',
       u'time_t target', u'ms2time']
M['par_fam'] = PAR
M['par'] = [[cnt_cur(SHLIG[i], nd) for nd in PAR] for i in range(NS)]
M['par_upper_n'] = [len([k for k in range(4) if M['par'][i][k]]) for i in range(NS)]
M['par_greek_n'] = [len([k for k in range(4, 8) if M['par'][i][k]]) for i in range(NS)]
M['par_impl_n'] = [len([k for k in range(8, 11) if M['par'][i][k]]) for i in range(NS)]
M['par_impl'] = [[(PAR[k], M['par'][i][k]) for k in range(8, 11) if M['par'][i][k]] for i in range(NS)]
assert M['par_upper_n'] == [0, 0, 2, 0, 2] and M['par_greek_n'] == [0, 4, 0, 0, 0]
# 实现名只在 madp 面上(pdrop 4 枚); 在库两份 RFC 里没有 C 代码段: time_t target ⇎ ms2time 全 0 枚
# (“规范面带代码片段”这一读法在别处成立, 在这五份的在库字节里不成立)
assert M['par_impl_n'] == [0, 1, 0, 0, 0] and M['par_impl'] == [[], [(u'pdrop', 4)], [], [], []]
assert sum(M['par'][i][9] + M['par'][i][10] for i in range(NS)) == 0

# ---------- 免配置宣称 ⇎ 要配置的实情 ----------
CFG = [u'parameter-free', u'self-configuring', u'should not need to configure', u'require operational',
       u'should not require tuning', u'auto-tuning', u'configuration', u'configurable', u'tuning',
       u'deployments']
M['cfg_fam'] = CFG
M['cfg'] = [[cnt_cur(LOW_SHLIG[i], nd) for nd in CFG] for i in range(NS)]
M['cfg_claim'] = [sum(M['cfg'][i][:6]) for i in range(NS)]
M['cfg_own'] = [[CFG[k] for k in range(len(CFG)) if M['cfg'][i][k]
                 and all(M['cfg'][j][k] == 0 for j in range(NS) if j != i)] for i in range(NS)]
assert [len(x) for x in M['cfg_own']] == [2, 0, 2, 0, 1], M['cfg_own']
M['cfg_zero_n'] = len([i for i in range(NS) if M['cfg_claim'][i] == 0])
assert M['cfg_own'][3] == [] and M['cfg_claim'] == [8, 1, 2, 0, 1] and M['cfg_zero_n'] == 1
# madp 不作任何“独有”宣称: 它只引述别人的默认值(self-configuring ⇎ parameter-free 都不在它面上)
assert [M['cfg'][i][0] + M['cfg'][i][1] for i in range(NS)] == [0, 0, 1, 0, 1]

# ---------- 义务词阶梯 ⇎ 标题里的规范性语言三档 ----------
TONE = [u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY']
M['tone_fam'] = TONE
M['tone_raw'] = [[ub(T[i], nd) for nd in TONE] for i in range(NS)]         # 原面(含页壳, 含硬换行)
M['tone_sh'] = [[ub(SHLIG[i], nd) for nd in TONE] for i in range(NS)]      # 摘壳+拆字面
M['tone_straddle_k'] = [[M['tone_sh'][i][k] - M['tone_raw'][i][k] for k in range(5)] for i in range(NS)]
M['tone_straddle'] = [sum(x) for x in M['tone_straddle_k']]
M['tone_lc'] = [[cnt_cur(LOW_SHLIG[i], w) for w in (u'must', u'should', u'may', u'can')]
                for i in range(NS)]
M['tone_must_pure'] = [len(re.findall(u'(?<![A-Za-z])MUST(?![A-Za-z])(?! NOT)', SHLIG[i]))
                       for i in range(NS)]
M['tone_must_ledger'] = [M['tone_sh'][i][1] - M['tone_sh'][i][0] - M['tone_must_pure'][i]
                         for i in range(NS)]
assert M['tone_must_ledger'] == [0] * NS, M['tone_must_ledger']
HEADRX = u'^\\s*(\\d+(?:\\.\\d+)*)\\.?\\s+\\S'
LEADER = re.compile(u'\\.{3,}')                       # 常规目录引道符尺
LEADER_SP = re.compile(u'(?:\\.\\s*){3,}')            # RFC txt 真正用的: 点之间还有空格
TOCRX = u'^ +\\d+\\.\\d'                              # 缩进 + 多级编号 = 目录行
LISTRX = u'^ +\\d+\\.\\s+\\S'                         # 缩进 + 单级编号 = 列表项
SECRX = u'^\\d+\\.\\d'                                # 顶格 + 多级编号 = 真节标题
TONED = lambda x: any(ub(x, nd) for nd in TONE)
M['head_tone_toc'] = [len([x for x in L[i] if re.match(TOCRX, x) and TONED(x)]) for i in range(NS)]
M['head_tone_list'] = [len([x for x in L[i] if re.match(LISTRX, x) and not re.match(TOCRX, x)
                            and TONED(x)]) for i in range(NS)]
M['head_tone_sec'] = [len([x for x in L[i] if re.match(SECRX, x) and TONED(x)]) for i in range(NS)]
M['head_tone_shape'] = [len([x for x in L[i] if re.match(HEADRX, x) and TONED(x)]) for i in range(NS)]
M['head_tone_stray'] = [M['head_tone_shape'][i] - M['head_tone_toc'][i] - M['head_tone_list'][i]
                        - M['head_tone_sec'][i] for i in range(NS)]
M['head_tone_ledger'] = M['head_tone_stray']
# 引道符尺的漏读: 4 枚目录行全带点线, 但点之间隔着空格(“. . . .”), 常规 “\.{3,}” 一枚也读不到
M['head_toc_leader_strict'] = [len([x for x in L[i] if re.match(TOCRX, x) and TONED(x)
                                    and LEADER.search(x)]) for i in range(NS)]
M['head_toc_leader_spaced'] = [len([x for x in L[i] if re.match(TOCRX, x) and TONED(x)
                                    and LEADER_SP.search(x)]) for i in range(NS)]
# 假标题形: 正文续行以数字打头即撞 HEADRX
M['head_tone_stray_lines'] = [[x.strip() for x in L[i] if re.match(HEADRX, x) and TONED(x)
                               and not re.match(TOCRX, x) and not re.match(LISTRX, x)
                               and not re.match(SECRX, x)] for i in range(NS)]
M['head_tone_lines'] = [[x.strip() for x in L[i] if re.match(HEADRX, x) and TONED(x)] for i in range(NS)]
assert M['head_tone_toc'] == [4, 0, 0, 0, 0] and M['head_tone_list'] == [6, 0, 0, 0, 0], \
    M['head_tone_list']
assert M['head_tone_sec'] == [4, 0, 0, 0, 0] and M['head_tone_shape'] == [15, 0, 0, 0, 0]
assert M['head_tone_stray'] == [1, 0, 0, 0, 0]
assert M['head_tone_stray_lines'][0] == [u'3168 by allowing that an implementation MAY use more than one']
assert M['head_toc_leader_strict'] == [0, 0, 0, 0, 0] and M['head_toc_leader_spaced'] == [1, 0, 0, 0, 0]

# ---------- 语态与施事 ----------
VOICE = [u'we ', u'this document', u'this memo', u'we propose', u'we show', u'we observe',
         u'we present', u'it is recommended', u'recommend']
M['voice_fam'] = VOICE
M['voice'] = [[cnt_cur(LOW_SHLIG[i], nd) for nd in VOICE] for i in range(NS)]
M['voice_we'] = [M['voice'][i][0] for i in range(NS)]
M['voice_impersonal'] = [M['voice'][i][1] + M['voice'][i][2] for i in range(NS)]
# 第一人称动词组(we propose/show/observe/present): 论文面 6 枚 ⇎ 2 枚, 三份 RFC 面上 0 枚
M['voice_weverb'] = [sum(M['voice'][i][3:7]) for i in range(NS)]
assert M['voice_weverb'] == [0, 8, 0, 2, 0] and M['voice'][1][3] == 1 and M['voice'][3][6] == 2
# “we” 本身不是体裁尺: 实验规范 8289 用了 25 次, 比两篇论文还多; 尺要用非人称自指
# (this document ⇎ this memo): 三份 RFC 36/17/21 枚, 两份论文 0 枚 —— 两把尺各证一件事
assert M['voice_impersonal'] == [36, 0, 17, 0, 21] and M['voice_we'] == [11, 24, 9, 24, 25]
assert max(M['voice_we'][i] for i in RFCI) > min(M['voice_we'][i] for i in PAPI)

# ---------- 引用代际 ----------
CIT = [u'RFC 7567', u'RFC 8033', u'RFC 8289', u'RFC 8034', u'CoDel', u'PIE', u'CAKE', u'cake',
       u'[CHARB2007]', u'[1]', u'[9]', u'[24]']
M['cit_fam'] = CIT
M['cit'] = [[cnt_cur(SHLIG[i], nd) for nd in CIT] for i in range(NS)]
M['cit_brk'] = [len(re.findall(u'\\[\\d+\\]', SHLIG[i])) for i in range(NS)]
M['cit_rfc'] = [len(re.findall(u'RFC \\d{4}', SHLIG[i])) for i in range(NS)]
M['cite_matrix'] = [[(0 if i == j or not IDS[j] else
                      len([1 for y in SHLIG[i].split(u'RFC ')
                           if y.startswith(IDS[j] + u' ') or y.startswith(IDS[j] + u',')]))
                     for j in range(NS)] for i in range(NS)]
# 谱系断点: 最新的 8289 既不提 BCP 7567 也不提同族实验规范 8033; cake 谁都不提
assert M['cite_matrix'][4] == [0, 0, 0, 0, 0] and M['cite_matrix'][2][0] == 2
assert M['cite_matrix'][3] == [0, 0, 0, 0, 0] and M['cite_matrix'][1][0] == 1
# 引用形式不是体裁尺: 两篇论文也印 “RFC nnnn”(1 枚 ⇎ 4 枚), 只是另用方括号编号(26 ⇎ 53 枚);
# 三份 RFC 面上 [n] 式编号 0 枚 —— 单向可分(RFC 面无方括号), 反向不可分(论文面两种都用)
assert [M['cit_brk'][i] for i in RFCI] == [0, 0, 0] and [M['cit_rfc'][i] for i in PAPI] == [1, 4]
assert [M['cit_brk'][i] for i in PAPI] == [26, 53] and M['cit_rfc'] == [40, 1, 8, 4, 7]

# ---------- 节窗: 默认值/实测值那一节住在哪 ----------
WIN = [u'AQM Algorithm Deployment SHOULD NOT Require Operational',
       u'its default target delay of 20 ms',
       u'defaulted to 15 milliseconds', u'50 ms baseline latency', u'minimum TARGET of 5 ms']
ARAB = re.compile(u'^\\s*(\\d+(?:\\.\\d+)*)\\.?\\s+\\S')
ROMAN = re.compile(u'^\\s*([IVX]+)\\.\\s+[A-Z]')
M['sec_no'] = []
M['sec_title'] = []
M['sec_lines'] = []
M['sec_chars'] = []
M['sec_tone'] = []
M['sec_numval'] = []
M['sec_par'] = []
M['sec_role'] = []
TOCL = []
BODYL = []
HITN = []
for i in range(NS):
    hit = [x for x, y in enumerate(L[i]) if WIN[i] in y]
    assert hit, (i, WIN[i])
    HITN.append(len(hit))
    TOCL.append(hit[0] + 1 if len(hit) > 1 else None)
    k = hit[-1]
    BODYL.append(k + 1)
    rx = ARAB if FAM[i] == u'rfc' else ROMAN
    heads = [(x, rx.match(L[i][x])) for x in range(len(L[i]))
             if rx.match(L[i][x]) and not LEADER.search(L[i][x])]
    beg = [h for h in heads if h[0] <= k][-1]
    lvl = len(beg[1].group(1).split(u'.')) if FAM[i] == u'rfc' else 1
    cur = tuple(int(z) for z in beg[1].group(1).split(u'.')) if FAM[i] == u'rfc' else None
    nxt = len(L[i])
    for x, m in heads:
        if x <= beg[0]:
            continue
        if FAM[i] == u'rfc':
            tup = tuple(int(z) for z in m.group(1).split(u'.'))
            if len(tup) <= lvl and tup >= cur:
                nxt = x
                break
        else:
            nxt = x
            break
    w = fold(NL.join(x for x in L[i][beg[0]:nxt] if not is_shell(x, FAM[i])))
    M['sec_no'].append(beg[1].group(1))
    M['sec_title'].append(fold(L[i][beg[0]]))
    M['sec_lines'].append(nxt - beg[0])
    M['sec_chars'].append(len(w))
    M['sec_tone'].append([ub(w, nd) for nd in TONE])
    M['sec_numval'].append(sorted(set((v, u) for v, u in NUMRE.findall(w.lower()))))
    M['sec_par'].append([cnt_cur(w, nd) for nd in PAR])
    M['sec_role'].append([k for k in range(len(ROLEN)) if M['role_src'][k] == LBL[i]
                          and ROLEN[k] in w.lower()])
M['sec_hit_n'] = HITN
M['sec_toc_line'] = TOCL
M['sec_body_line'] = BODYL
M['sec_tone_tot'] = [sum(x) for x in M['sec_tone']]
M['sec_span_pct'] = [round(100.0 * M['sec_chars'][i] / M['sh_chars'][i], 1) for i in range(NS)]
assert M['sec_no'] == [u'4.3', u'I', u'8', u'IV', u'4'], M['sec_no']
# 7567 的锚在目录(136)与正文(1071)各出现一次, 节窗必须取后者; 4.3 的标题在正文里占一行
assert M['sec_hit_n'][0] == 2 and M['sec_toc_line'][0] == 136 and M['sec_body_line'][0] == 1071
assert [x is None for x in M['sec_toc_line']] == [False, True, True, True, True]
assert M['sec_lines'] == [69, 8, 32, 113, 91] and M['sec_chars'] == [2743, 3642, 1108, 7355, 4469]
assert M['sec_tone_tot'] == [9, 0, 0, 0, 4] and M['sec_span_pct'] == [4.2, 13.8, 2.4, 22.9, 8.2]
# 8289 的锚(“minimum TARGET of 5 ms …”)在 §4 总述节第 702 行, 专讲 TARGET 的 §4.3 在其后
# ⇒ “默认值住在专节”这一读法错: 按标题切窗自动把锚归给上一级总述节
SUB43 = [x + 1 for x, y in enumerate(L[4]) if re.match(u'^4\\.3\\.\\s', y)]
assert len(SUB43) == 1 and SUB43[0] > M['sec_body_line'][4], SUB43
M['sec_sub_line'] = SUB43[0]
M['sec_sub_title'] = fold(L[4][SUB43[0] - 1])
# 窗内义务词: 7567 §4.3 有 9 枚(它整节都在下规范性语句), 8289 §4 有 4 枚,
# 而 8033 的 §8 “Incremental Deployment” 给完双档默认值却一枚规范语也不用(0 枚), 两篇论文也 0 枚
assert M['sec_tone'][2] == [0, 0, 0, 0, 0] and [M['sec_tone'][i] for i in PAPI] == [[0]*5, [0]*5]

# ---------- 答案句(锚由位置导出, 段落窗=锚所在的不跨空行块) ----------
ANS = []
SPAN = []
BLOCKN = []
ANSHELL = []
for i, pat in enumerate(WIN):
    hit = [x for x, y in enumerate(L[i]) if pat in y]
    ln = hit[-1]
    lo = ln
    while lo - 1 >= 0 and L[i][lo - 1].strip() != u'':
        lo -= 1
    hi = ln
    while hi + 1 < len(L[i]) and L[i][hi + 1].strip() != u'':
        hi += 1
    blk = L[i][lo:hi + 1]
    # 段块里的页壳行(眉行/脚注)不参与句子拼接, 但单独立账: 它正好插在句子中间
    ANSHELL.append(len([x for x in blk if is_shell(x, FAM[i]) and x.strip() != u'']))
    rows = [fold(x) for x in blk if x.strip() != u'' and not is_shell(x, FAM[i])]
    txt, offs = u'', []
    for y in rows:
        offs.append(len(txt))
        txt += (u'' if txt == u'' else u' ') + y
    st = txt.lower().find(pat.lower())
    assert st >= 0, (LBL[i], pat)
    tail = txt[st + len(pat):]
    mm = re.search(u'\\.\\s(?=[A-Z(“"])', tail)
    if mm:
        en = st + len(pat) + mm.start()
    else:
        d = tail.rfind(u'.')
        en = len(txt) - 1 if d < 0 else st + len(pat) + d
    ANS.append(txt[st:en + 1])
    SPAN.append(len([kk for kk in range(len(rows))
                     if offs[kk] <= en and offs[kk] + len(rows[kk]) >= st]))
    BLOCKN.append(len(rows))
M['ans'] = ANS
M['ans_words'] = [len(x.split()) for x in ANS]
M['ans_span'] = SPAN
M['ans_block_lines'] = BLOCKN
M['ans_shell_rows'] = ANSHELL
M['ans_one_line_n'] = len([x for x in SPAN if x == 1])
# 五根锚的最短完整读法: 7567 的标题行(1 行)⇎ 两份论文整段在一行(1 行)⇎ 8033 跨 3 行 ⇎ 8289 跨 2 行
# ⇒ “跨行”只发生在两份 72 列折行的 RFC 面上, 而 7567 那一枚的“单行”是标题而非句子
assert M['ans_span'] == [1, 1, 3, 1, 2] and M['ans_one_line_n'] == 3, M['ans_span']
assert M['ans_block_lines'] == [1, 7, 6, 5, 14] and M['ans_words'] == [8, 24, 22, 4, 10]
# 五个答案块里的页壳行数全为 0 ⇒ 跨页切句不发生在答案块上(它发生在另两根专挑的针上)
assert M['ans_shell_rows'] == [0] * NS
assert M['ans'][0].endswith(u'Tuning') and M['ans'][2].endswith(u'respectively.')
for i in range(NS):
    assert M['ans'][i].lower().startswith(WIN[i].lower()[:20]), (LBL[i], M['ans'][i][:60])

json.dump(M, io.open(u'corpus/_b81meas.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)
print(u'采集 B81: 五份 %s 字节 ⇎ 行 %s ⇎ 最长行 %s ⇎ 超 72 列 %s ⇎ 回车 %s ⇎ 尾换行 %s' % (
    [format(x, u',') for x in M['bytes']], M['lines'], M['maxlen'], M['over72'], M['cr'], M['tail_nl']))
print(u'  换页符 %s（独占 %s ⇎ 行首粘 %s ⇎ 行首 %s）⇎ [Page] %s ⇎ 眉行 %s ⇎ 剥壳 %s ⇎ 账 %s' % (
    M['ff'], M['ff_exact'], M['ff_inline'], M['ff_lead'], M['pg_lines'], M['hdr_lines_tight'],
    M['shell_lines'], M['shell_ledger']))
print(u'  页码两尺 naive %s ⇎ FFled %s ⇎ 多吃 %s' % (M['pgnum_naive'], M['pgnum_ffled'], M['pgnum_overstrip']))
print(u'  非 ASCII %s（连字 %s ⇎ 希腊 %s ⇎ 弯引长划 %s ⇎ 其余 %s ⇎ 账 %s ⇎ 其余字符集 %s）' % (
    M['na_total'], M['lig_total'], M['na_greek'], M['na_dashq'], M['na_other'], M['na_ledger'],
    [u''.join(x) for x in M['na_other_set']]))
print(u'  面字符: 折平 %s ⇎ 摘壳 %s ⇎ 差 %s' % (M['fold_chars'], M['sh_chars'], M['sh_minus_fold']))
print(u'  拼写 %s ⇎ 主拼 %s ⇎ 少数 %s ⇎ 一边倒 %d 份 ⇎ 短语三式 %s ⇎ 两式 %s' % (
    M['spell'], M['spell_side'], M['spell_minor'], M['spell_onel-sided_n'],
    M['spell_phrase_sum'], M['spell_phrase_two']))
print(u'  术语 %s ⇎ 主词 %s ⇎ 少数 %s ⇎ 斜度 %s ⇎ 独有术语 %s' % (
    M['term'], M['term_side'], M['term_minor'], M['term_skew'], M['term_own']))
print(u'  RTT 三尺: 紧 %s ⇎ 拉开(大写) %s ⇎ 裸子串(不敏感) %s ⇎ 假命中 %s' % (
    M['rtt_tight'], M['rtt_kern'], M['rtt_loose'], M['rtt_loose_false']))
print(u'  单位 %s ⇎ 整词 %s ⇎ 子串多读 %s ⇎ 值集枚数 %s ⇎ 宽尺多读 %s ⇎ 宽尺读丢 %s' % (
    M['unit'], M['unit_word'], M['unit_sub_over'], M['numval_n'], M['numval_s_extra'], M['numval_s_lost']))
print(u'  数字族 %s ⇎ 合计 %s ⇎ 零枚 %s ⇎ 独有 %s ⇎ 拆字后新读 %s' % (
    M['num'], M['num_tot'], M['num_zero_n'], M['num_own'], M['num_nofold']))
print(u'  角色针 %d 根: 逐行读到 %d ⇎ 读不到 %d ⇎ 硬换行切开 %s ⇎ 目录正文同印 %s ⇎ 只在摘壳面读到 %s ⇎ 跨份误读 %s' % (
    len(ROLEN), M['role_line_read_n'], M['role_line_miss_n'], M['role_wrap'], M['role_dup'],
    M['role_shell_only'], [x for y in M['role_hit_other'] for x in y]))
print(u'  100 ms 角色 %s ⇎ 字面出现 %s' % (M['ms100_roles'], M['ms100_count']))
print(u'  参数名 %s ⇎ 大写 %s ⇎ 希腊 %s ⇎ 实现名 %s ⇎ 代码名(全库应为 0) %s' % (
    M['par'], M['par_upper_n'], M['par_greek_n'], M['par_impl'],
    [M['par'][i][9] + M['par'][i][10] for i in range(NS)]))
print(u'  免配置族 %s ⇎ 宣称 %s ⇎ 独有 %s ⇎ 零宣称 %d 份' % (
    M['cfg'], M['cfg_claim'], M['cfg_own'], M['cfg_zero_n']))
print(u'  义务词(原面) %s ⇎ 摘壳面 %s ⇎ 被切 %s ⇎ 小写 %s ⇎ MUST 账 %s' % (
    M['tone_raw'], M['tone_sh'], M['tone_straddle_k'], M['tone_lc'], M['tone_must_ledger']))
print(u'  标题规范语四档: 目录 %s ⇎ 列表 %s ⇎ 顶格节 %s ⇎ 假形 %s ⇎ 形尺合计 %s ⇎ 引道符 常规 %s/空格点 %s' % (
    M['head_tone_toc'], M['head_tone_list'], M['head_tone_sec'], M['head_tone_stray_lines'],
    M['head_tone_shape'], M['head_toc_leader_strict'], M['head_toc_leader_spaced']))
print(u'  节窗: 窗后专节行 %s（%s）' % (M['sec_sub_line'], M['sec_sub_title']))
print(u'  语态 we %s ⇎ 非人称 %s' % (M['voice_we'], M['voice_impersonal']))
print(u'  引用: RFC 式 %s ⇎ 方括号 %s ⇎ 谱系 %s' % (M['cit_rfc'], M['cit_brk'], M['cite_matrix']))
print(u'  节窗: 节号 %s ⇎ 标题 %s' % (M['sec_no'], M['sec_title']))
print(u'         行 %s ⇎ 字符 %s ⇎ 占比 %s ⇎ 义务词 %s ⇎ 值集 %s' % (
    M['sec_lines'], M['sec_chars'], M['sec_span_pct'], M['sec_tone_tot'],
    [len(x) for x in M['sec_numval']]))
print(u'         锚出现次 %s ⇎ 目录行 %s ⇎ 正文行 %s ⇎ 窗内针 %s' % (
    M['sec_hit_n'], M['sec_toc_line'], M['sec_body_line'], M['sec_role']))
print(u'  答句: %s' % [x[:40] for x in M['ans']])
print(u'        词 %s ⇎ 跨行 %s ⇎ 块行数 %s ⇎ 单行读全 %d' % (
    M['ans_words'], M['ans_span'], M['ans_block_lines'], M['ans_one_line_n']))
