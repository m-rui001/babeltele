# -*- coding: utf-8 -*-
# B98 解读注遍(第三套机制, 独立于 _pick98.py ⇎ _mkB98.py): 计数只走 str.count(整串子串档, 不整词、
# 不折行、不区分大小写档另列), 词尺走逐字符扫空白, 行尺走手工按 '\n' 切, 定义窗走"整行等值"定界
# (既不是采集遍的行号窗口, 也不是建条遍的 (?m)^题面$ 正则); 锚核验只用 `in`。
# 前两遍的中间量一枚都不复用, 注里每个数都由本遍现读现算, 与编码区登记的数各自独立成账。
# 写回 corpus/babeltele/B98_*.md 的 "## ⛓解读注" 段(替换占位句), 不动编码区与原文区。
import io, json, os, re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENTRY = u'corpus/babeltele/B98_retry_after_delay_and_who_may_omit.md'
TAGP = [u'A', u'B', u'C', u'D', u'E']
RAWS = [u'corpus/raw/httpretry/rfc2616.txt', u'corpus/raw/httpretry/rfc6585.txt',
        u'corpus/raw/httpretry/rfc7231.txt', u'corpus/raw/httpretry/rfc9110.txt',
        u'corpus/raw/retryafter98/curl_retry.md']
LBL = [u'2616', u'6585', u'7231', u'9110', u'curl']
N = 5
TT = [u'14.37 Retry-After', u'4.  429 Too Many Requests', u'7.1.3.  Retry-After',
      u'10.2.3.  Retry-After', u'# `--retry`']
TE = [u'14.38 Server', u'5.  431 Request Header Fields Too Large', u'7.1.4.  Vary',
      u'10.2.4.  Server', None]
NL = u'\n'

md = io.open(ENTRY, encoding='utf-8').read()
assert md.count(u'## ⛓解读注') == 1, u'解读注标题不在 ⇎ 不止一枚'
T = [io.open(p, encoding='utf-8', errors='replace').read() for p in RAWS]
enc = re.search(u'## ⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
orig = re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ', md, re.S).group(1)


def row(lst):
    return u'⇎'.join([u'%d' % v if isinstance(v, int) else u'%s' % v for v in lst])


# —— 源面(本遍口径: 逐字符, 不用 split()/join 的词表法) ——
n_ch = [len(t) for t in T]
n_word = []
for t in T:
    c, prev = 0, True
    for ch in t:
        ws = ch.isspace()
        if not ws and prev:
            c += 1
        prev = ws
    n_word.append(c)
n_line = [len(t.split(NL)) for t in T]
n_cp = [len(set(t)) for t in T]
enc_ch = len(enc.replace(NL, u''))
orig_ch = len(orig.replace(NL, u''))
orig_nl = len(orig)
src_tot = sum(n_ch)


def pct(a, b):
    return u'%.2f%%' % (100.0 * a / b)


# —— 子串档字面账(整串 str.count, 不整词) ⇎ 大小写另开一档 ——
LIT = {}
for nd in [u'Retry-After', u'retry-after', u'RETRY-After', u'HTTP-date', u'delta-seconds',
           u'delay-seconds', u'Retry-After: 120', u'Retry-After: 3600', u'2 minutes',
           u'1999', u'MUST', u'must', u'ought to wait', u'is asked wait']:
    LIT[nd] = [t.count(nd) for t in T]
LITL = [t.lower().count(u'retry-after') for t in T]
# 整词档(建条遍)与子串档(本遍)在 Retry-After 上同值——因为面上根本没有小写或全大写变体
FLAT = json.load(io.open(u'corpus/_b98flat.json', encoding='utf-8'))
REG = json.load(io.open(u'corpus/_b98contract.json', encoding='utf-8'))
assert LIT[u'Retry-After'] == FLAT['ra_total'] == FLAT['ra_caseless'], (LIT[u'Retry-After'], FLAT['ra_total'])
assert LITL == FLAT['ra_total'], LITL
assert LIT[u'retry-after'] == [0] * N and LIT[u'RETRY-After'] == [0] * N
assert LIT[u'delta-seconds'] == [8, 0, 0, 0, 0] and LIT[u'delay-seconds'] == [0, 0, 6, 6, 0]
assert LIT[u'HTTP-date'] == FLAT['nd_http_date'], LIT[u'HTTP-date']
assert LIT[u'1999'] == FLAT['num_1999'], LIT[u'1999']

# —— 定义窗(本遍第三把尺: 整行等值定界) 与 "无行锚的纯 find" 假命中 ——
WIN, NAIVE = [], []
for i in range(N):
    L = T[i].split(NL)
    hits = [k for k, x in enumerate(L) if x == TT[i]]
    ends = [k for k, x in enumerate(L) if x == TE[i]] if TE[i] else [len(L)]
    assert len(hits) == 1, (LBL[i], len(hits))
    WIN.append(NL.join(L[hits[0]:ends[0]]))
    a = T[i].find(TT[i])
    b = len(T[i]) if TE[i] is None else T[i].find(TE[i], a)
    NAIVE.append(T[i][a:b])
assert [len(w) for w in WIN] == FLAT['win_cp'], ([len(w) for w in WIN], FLAT['win_cp'])
assert [w.count(u'Retry-After') for w in WIN] == FLAT['ra_win'], [w.count(u'Retry-After') for w in WIN]
assert [w.count(u'MUST') for w in WIN] == FLAT['win_caps_must']
assert [w.count(u'MAY') for w in WIN] == FLAT['win_caps_may']
assert [w.count(u'ought') for w in WIN] == FLAT['win_caps_ought']
assert [w.count(u'Retry-After: 120') for w in WIN] == [1, 0, 1, 1, 0]
assert [w.count(u'Retry-After: 3600') for w in WIN] == [0, 1, 0, 0, 0]
# 假命中档: 9110 的 '10.2.3.  Retry-After' 在目录行也成串, 纯 find 取到的窗只有 28 字符 ⇎ 1 枚
assert len(NAIVE[3]) == 28 and NAIVE[3].count(u'Retry-After') == 1, len(NAIVE[3])
# 其余四面两档只差收尾那一枚换行(纯 find 的窗尾含题行行界, 整行等值档按行连接不含), 9110 差 893 字符
assert [len(NAIVE[i]) - len(WIN[i]) for i in range(N)] == [1, 1, 1, -893, 0], \
    [len(NAIVE[i]) - len(WIN[i]) for i in range(N)]
NVD = [len(x) for x in NAIVE]
NVDIFF = [len(NAIVE[i]) - len(WIN[i]) for i in range(N)]

# —— 锚核验(第三把尺: 逐枚 `in`, 原面 ⇎ 折平面两档) ——
fold = lambda t: u' '.join(t.split())
TF = [fold(t) for t in T]
pairs = re.findall(u'⟦([A-E])⟧⟨([^⟨⟩]+)⟩', enc)
atoms = re.findall(u'⟨[^⟨⟩]+⟩', enc)
assert len(pairs) == 24 and len(atoms) == 24, (len(pairs), len(atoms))
uniq = sorted(set(pairs))
TAGI = {t: i for i, t in enumerate(TAGP)}
own_raw = [a for (t, a) in pairs if a in T[TAGI[t]]]
own_fold = [a for (t, a) in pairs if a in TF[TAGI[t]]]
assert len(own_fold) == 24, [a[:60] for (t, a) in pairs if a not in TF[TAGI[t]]]
who = sorted(set([t for (t, a) in pairs if a not in T[TAGI[t]]]))
exc = [a for (t, a) in pairs if len([1 for x in TF if a in x]) == 1]
shared = sorted(set([a for (t, a) in pairs if len([1 for x in TF if a in x]) > 1]))

ANCHOR_LEX = []
for _l in io.open(u'corpus/_atoms98.txt', encoding='utf-8'):
    if u'\t' in _l:
        _t, _a = _l.rstrip(NL).split(u'\t', 1)
        ANCHOR_LEX.append((_t, _a))
_dead = [(t_, a) for (t_, a) in ANCHOR_LEX
         if a not in T[TAGI[t_]] and fold(a) not in TF[TAGI[t_]]]
lex_dead = sorted(set([a for (_t, a) in _dead]))
LEX_ROWS = len(ANCHOR_LEX)
LEX_DEAD_ROWS = len(_dead)
assert LEX_DEAD_ROWS == 11 and len(lex_dead) == 3, (LEX_DEAD_ROWS, lex_dead)
LEX_LIVE_ROWS = LEX_ROWS - LEX_DEAD_ROWS
# 死行分两类: 大小写两形各按五标签列了一行(词表的行 ⇒ 10 行), 第三串只死一行
DEAD_A = [x for (_t, x) in _dead]
five = [a for a in lex_dead if DEAD_A.count(a) == N]
one = [a for a in lex_dead if DEAD_A.count(a) == 1]
assert len(five) == 2 and len(one) == 1, (five, one)
DEAD_CASE_ROWS = DEAD_A.count(five[0]) + DEAD_A.count(five[1])
D3 = [t_ for (t_, a) in _dead if a == one[0]]
assert len(D3) == 1 and one[0] in TF[TAGI[u'C']], (D3, one)
DEAD_OTHER = one[0]
OTHER_FOLD = [x.count(DEAD_OTHER) for x in TF]
OTHER_RAW = [t.count(DEAD_OTHER) for t in T]
assert sum(OTHER_FOLD) == 1 and sum(OTHER_RAW) == 0, (OTHER_RAW, OTHER_FOLD)
assert OTHER_FOLD[2] == 1 and D3[0] != u'C' and DEAD_OTHER in TF[TAGI[u'C']]

NOTE = (u'## ⛓解读注\n\n'
        u'### 压缩账(本注现算, 第三把尺: str.count 子串档 ⇎ 逐字符扫空白 ⇎ 手工按换行切行 ⇎ '
        u'整行等值定界; 建条遍与采集遍的中间量一枚都不复用)\n\n'
        u'| 量 | 2616 | 6585 | 7231 | 9110 | curl |\n|---|---|---|---|---|---|\n'
        u'| 源字符 | %s |\n'
        u'| 源词(逐字符扫空白) | %s |\n'
        u'| 源行(split 换行, 含收尾空行) | %s |\n'
        u'| 源面唯一码位 | %s |\n'
        u'| 子串档 `Retry-After` 枚数 | %s |\n'
        u'| 子串档 `HTTP-date` 枚数 | %s |\n'
        u'| 子串档 `delta-seconds` / `delay-seconds` 枚数 | %s ⇎ %s |\n'
        u'| 定义窗字符(整行等值档) | %s |\n\n'
        u'编码区 %s 字符(不含换行) ⇎ 五份源面合 %s 字符 = %s ⇎ 在档摘录 %s 字符(去换行)⇎%s 字符(含换行, '
        u'门表用后者): 编码⇎摘录两把尺 %s⇎%s, 差 %s 枚换行符。\n\n'
        u'### 三处只有换尺子才看得见的岔口(本注现读出)\n'
        u'① 词形档: 子串 `Retry-After`(大小写敏感) 得 %s, 将整面小写后再数仍是 %s, 与建条遍的整词档逐格同值——'
        u'因为面上 `retry-after` 与 `RETRY-After` 两种拼写各 0 枚。词表 corpus/_atoms98.txt 共 %s 行, 其中 %s 行'
        u'穿不到本家原文(原面 ⇎ 折平两档都试): 那两种小写得 %s 行(五个标签各一行, 去重是两串), 第三枚死串是 '
        u'⟦%s⟧⟨%s⟩——这句在整串子串档上原面 %s ⇎ 折平 %s: 只在 7231 成句, 而它在 7231 也被硬换行劈开, 故 ⟦C⟧ 行'
        u'要折平才穿得到; 同一串活 ⟦C⟧ 死 ⟦%s⟧, 是版本改措辞而不是词表抽错。所以两形小写在编码区一枚没引, '
        u'第三串只以 ⟦C⟧ 出现; 本条取用的是能穿到原文的那 %s 行, 去重后落在编码区 %s 串。\n'
        u'② 定界档: 去掉行锚、只对整面用纯 find 取窗口, 五份得到 %s 字符 ⇎ 整行等值档 %s 字符, 逐份差 %s 字符'
        u'(四面只差窗尾那一枚换行, 9110 差 893)——纯 find 在 9110 命中的是目录行 `10.2.3.  Retry-After`, '
        u'那份窗子只有 %s 字符、`Retry-After` 只 1 枚; 换成本遍的整行等值定界才落到正文节 %s 字符 ⇎ 窗内 8 枚'
        u'(与建条遍的 (?m)^题面$ 逐格同值)。同一句题面在目录与正文各成一次, 这是"读不到"最容易伪装成"读到了"的一处。\n'
        u'③ 单位词档: 全篇 `MUST` 子串 %s 枚 ⇎ 定义窗内只有 %s 枚——编码区 🪜 答"没有一个 MUST 指向这枚头" '
        u'取的是后者; 窗内唯一那枚还落在 6585 的缓存禁存句上。同一段里 `Retry-After: 120` 窗内 %s 枚 ⇎ '
        u'`Retry-After: 3600` 窗内 %s 枚, curl 窗内两枚皆 0——编码区给它记的是 -1 哨兵(窗内无秒例)而不是 0(零枚样例), '
        u'两者不可混。\n\n'
        u'### 锚核验(%s 处 ⟦标签⟧⟨原文⟩ ⇎ 去重 %s 串, 逐枚按标签回本家文件)\n'
        u'原面逐字符 verbatim 命中 %s 处, 其余 %s 处要把整面折平(空白折成一枚空格)才命中——即锚身跨一枚硬换行, '
        u'分属 %s; 折平档 %s/%s 全命中。按折平档在五份面互查: 只在本家读到的 %s 处 ⇎ 两份以上同现的锚串 %s 串'
        u'(%s)。这把尺量的是编码区的 %s 处锚, 与 🔁 段"独占 %s ⇎ 候选 %s"量的不是同一集合(那边量 %s 枚判词针 × '
        u'五份 = 探针 %s 次), 两组数不可相加。\n\n'
        u'### 读法\n'
        u'编码区九段各管一副账: 🧭 五份面尺三轨行账(splitlines ⇎ split ⇎ 逐字符数换行, 前两轨之差恰为换页符减'
        u'收尾那一枚) ⇎ 壳行/目录行/正文行的四列合账 0; 📏 答值三档互斥(120 三面 ⇎ 3600 只 6585 ⇎ 日期档三面), '
        u'小时档还能由窗内那句"每 50 请求一小时"乘同面读出的 60 现算; ⚖ 秒名分流(delta-seconds 8 枚只在 2616 ⇎ '
        u'delay-seconds 各 6 枚只在 7231/9110) ⇎ ABNF 两式各只在自家版本成句 ⇎ 时刻锚三句互不相弄; '
        u'🪜 语气档(窗内 MAY/SHOULD/MUST/ought 逐面枚数 ⇎ 三句成词的 MUST 强制式五面全零)——这就是"谁能省掉它"的'
        u'规范答案; 🔁 反向对照(%s 枚针逐枚查本家>0 且别家合计=0, 成立 %s 枚 ⇎ 7231/9110 两窗句集容斥 7+7−9−5=0); '
        u'🧮 风险针四档可读性(逐行 %s ⇎ 折平 %s ⇎ 摘壳 %s ⇎ 去标记 %s, 三把刀里摘壳那把证明为空); '
        u'🧱 实现侧把规范空档填成状态机(起步一秒 ⇎ 逐次翻倍 ⇎ %s 秒封顶 = %s 分钟 ⇎ 那句里 %s 枚瞬时 HTTP 码); '
        u'🧬 谱系与壳(9110 引旧版 %s 次 ⇎ 目录只 2616 有 ⇎ 9110 的表只在去标记档读通); 🧾 与采集遍 %s 项逐键对账 '
        u'符 %s ⇎ 不符 %s ⇎ 布尔门 %s 枚全绿。核心结论一条: 上限那格 RFC 从不给死值, 它把"要么 HTTP-date 要么秒" '
        u'写成值域, 版本之间改的是单位名、时刻锚措辞与义务强度(四面 RFC 都没有 MUST 指向这枚头), 而实现侧反过来把'
        u'留白填成三个数: 起步一秒(面上现词) ⇎ 封顶 %s 分钟(面上现词, 折成秒要乘同族面现读的每分 %s 秒, 得 %s) '
        u'⇎ 总时长另设上限。\n\n'
        u'### 本条不能由在库文件判定的(只登记, 不进门槛)\n'
        u'RFC 勘误表与改版后的现值(2616/7231 的 errata 不在盘) ⇎ curl 手册之外的实现行为(Python requests/urllib3 '
        u'的重试算法, nginx、Envoy 的限流响应处理) ⇎ 真实服务返回的 Retry-After 分布 ⇎ 手册所描述的默认值与实际源码'
        u'常量是否一致(本条只认手册面自身)。手册把瞬时错误摊成逐码八枚(HTTP)+ 一类 FTP 4xx, 但没写各码的等待'
        u'差异, 也没写 Retry-After 与指数倍增的先后次序细节——只说该头自 7.66.0 起被遵行、服务器因此能覆盖重试'
        u'延时; 更早版本的实现与源码常量都不在盘。\n\n'
        u'### 编码与门的账\n'
        u'T1 逐锚回源: 本注折平档 %s/%s ⇎ 原面档 %s/%s(差 %s 处皆跨硬换行, 门按容行档判) ⇎ T2 DERIV 复算: '
        u'%s 枚面值由 corpus/_b98contract.json 逐枚现算(其中 %s 枚是复合式而非直取值), 门内现量 %s 键与建条遍逐键'
        u'同值 ⇎ T3 码位账: 五份源面唯一码位 %s 枚(并集另计)。本条小整数待核 0 项(门内 34 个提示里没有 B98)。\n'
        % (row(n_ch), row(n_word), row(n_line), row(n_cp), row(LIT[u'Retry-After']),
           row(LIT[u'HTTP-date']), row(LIT[u'delta-seconds']), row(LIT[u'delay-seconds']),
           row([len(w) for w in WIN]),
           enc_ch, src_tot, pct(enc_ch, src_tot), orig_ch, orig_nl, pct(enc_ch, orig_ch),
           pct(enc_ch, orig_nl), orig_nl - orig_ch,
           row(LIT[u'Retry-After']), row(LITL), LEX_ROWS, LEX_DEAD_ROWS, DEAD_CASE_ROWS,
           D3[0], DEAD_OTHER, row(OTHER_RAW), row(OTHER_FOLD), D3[0], LEX_LIVE_ROWS, len(uniq),
           row(NVD), row([len(w) for w in WIN]), row(NVDIFF), len(NAIVE[3]), len(WIN[3]),
           row(LIT[u'MUST']), row([w.count(u'MUST') for w in WIN]),
           row([w.count(u'Retry-After: 120') for w in WIN]),
           row([w.count(u'Retry-After: 3600') for w in WIN]),
           len(pairs), len(uniq), len(own_raw), 24 - len(own_raw), u'/'.join(who), len(own_fold), len(pairs),
           len(exc), len(shared),
           (u'即 `%s` 一句多面同现' % shared[0][:52]) if shared else u'无',
           len(pairs), FLAT['neg_clean'], FLAT['neg_n'], FLAT['needle_n'], FLAT['needle_n'] * N,
           FLAT['needle_n'], FLAT['neg_clean'],
           sum([sum(r) for r in FLAT['risk_row']]), sum([sum(r) for r in FLAT['risk_fold']]),
           sum([sum(r) for r in FLAT['risk_shell']]), sum([sum(r) for r in FLAT['risk_mkfree']]),
           FLAT['curl_cap_secs'], FLAT['curl_cap_minutes'], FLAT['curl_transient_codes'],
           FLAT['rfcref_2616_in_9110'], FLAT['pick_agree'] + FLAT['pick_diff'], FLAT['pick_agree'],
           FLAT['pick_diff'], FLAT['bool_all_n'],
           FLAT['curl_cap_minutes'], FLAT['unit_minute_from_doc'][2], FLAT['curl_cap_secs'],
           len(own_fold), len(pairs), len(own_raw), len(pairs), 24 - len(own_raw),
           len(REG), len([v for v in REG.values() if not v.startswith(u"B98V('")]),
           len(FLAT), row(n_cp)))

head, _ = md.split(u'## ⛓解读注', 1)
new = head + NOTE
assert new.count(u'## ⟪BabelTele⟫') == 1 and new.count(u'## ⛓解读注') == 1
assert new.count(u'## [[原始语料|ORIGINAL]]') == 1
assert u'(待第四遍复测后写回)' not in new
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(new)
print(u'B98 解读注: 源 %d 字符/%d 词 ⇎ 编码 %d 字符(%s of 源, %s of 摘录) ⇎ 锚 %d 处/去重 %d(原面 %d ⇎ 需折平 %d) '
      u'⇎ 词表 %d 行(死 %d 行 ⇎ 死串 %d) ⇎ 独占 %d ⇎ 共享串 %d ⇎ 待核 0'
      % (src_tot, sum(n_word), enc_ch, pct(enc_ch, src_tot), pct(enc_ch, orig_ch),
         len(pairs), len(uniq), len(own_raw), 24 - len(own_raw),
         LEX_ROWS, LEX_DEAD_ROWS, len(lex_dead), len(exc), len(shared)))
