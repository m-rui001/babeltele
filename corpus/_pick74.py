# -*- coding: utf-8 -*-
"""采集遍(B74, 第一套实现): “投递失败的邮件多久重试一次、什么时候放弃”由五份一手文书各答一遍
821 ⇎ 1123 ⇎ 5321 ⇎ Exim ⇎ Postfix。本遍只用一种机制(正则字面轨 + 行切片), 输出 _b74meas.json
给建条目侧(_mk74*.py, 第二套实现: 非重叠游标 ⇎ 集合代数 ⇎ 段落双尺)逐键对账。

两份 HTML(Exim 规格章 ⇎ Postfix postconf(5) 整页)与三份 txt 的差是本条的档位来源:
(1) txt 的档差在“跨页壳”(1123 的答句正跨一行 [Page N] 页眉);
(2) HTML 的档差在“跨标签”——Exim 把 `<letter>,<cutoff time>,<arguments>` 排成
    `&lt;<span class=docbook_emphasis>letter</span>&gt;,...`, 剥壳用空格替标签得“断面”,
    用空串替标签得“粘面”, 同一处两档读法不同, 两枚针各只在一档读得到;
(3) 转义层三家并存, 本遍逐族点名: Exim 只有 &lt;/&gt;(在 DETAG_SG 表内, 剥壳面还原);
    Postfix 镜像把 & 再转义一次(&amp;amp;gt; ⇎ &amp;amp;#39;), 单趟替换后面上残留 `&amp;>`;
    Postfix 另用数字实体 &#34;/&#39;/&#43;/&#x2F; —— 都不在 DETAG_SG 表内, 原样留在面上。
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'821', u'1123', u'5321', u'exim', u'postfix']
SRC = [u'corpus/raw/mailRetry/rfc821.txt', u'corpus/raw/mailRetry/rfc1123.txt',
       u'corpus/raw/mailRetry/rfc5321.txt', u'corpus/raw/mailRetry/exim4_retry_spec.html',
       u'corpus/raw/mailRetry/postfix_postconf5.html']
ISH = [False, False, False, True, True]          # 本遍记账的 HTML 份
NS = 5
M = {}

# ---------- 面量 ----------
T, L, BYT = [], [], []
for p in SRC:
    b = io.open(p, 'rb').read()
    BYT.append(b)
    t = b.decode('utf-8', 'replace')
    T.append(t)
    L.append(t.split(NL))
M['bytes'] = [len(b) for b in BYT]
M['chars'] = [len(t) for t in T]
M['lines'] = [len(L[i]) for i in range(NS)]
M['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NS)]
M['cr'] = [T[i].count(u'\r') for i in range(NS)]
M['ff'] = [T[i].count(u'\x0c') for i in range(NS)]
M['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NS)]
M['maxlen'] = [max(len(x) for x in L[i]) for i in range(NS)]
M['nonascii'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(NS)]
M['bom'] = [1 if BYT[i][:3] == b'\xef\xbb\xbf' else 0 for i in range(NS)]
M['txt_n'] = NS - sum(ISH)
M['html_n'] = sum(ISH)
assert M['cr'] == [0] * NS and M['bom'] == [0] * NS
# 换页符两档并记: 枚数 ⇎ 独占整行的行数(本库三份 txt 两档相等, 每枚 FF 都自成一行)
assert M['ff'][:3] == [72, 98, 95] and M['ff'][3] == M['ff'][4] == 0
assert sum(M['ff']) == sum(M['ff_exact'])

# ---------- HTML 结构量(只有两份 html 有值) ----------
M['tag_open'] = [len(re.findall(r'(?i)<[a-zA-Z][^<>]*>', T[i])) if ISH[i] else 0 for i in range(NS)]
M['tag_close'] = [len(re.findall(r'(?i)</[a-zA-Z][^<>]*>', T[i])) if ISH[i] else 0 for i in range(NS)]
M['comment'] = [len(re.findall(r'(?s)<!--.*?-->', T[i])) if ISH[i] else 0 for i in range(NS)]
M['br_tag'] = [len(re.findall(r'(?i)<br\s*/?>', T[i])) if ISH[i] else 0 for i in range(NS)]
ENTFAM = [u'&lt;', u'&gt;', u'&amp;', u'&amp;amp;', u'&#34;', u'&#39;', u'&#43;', u'&#x2F;', u'&nbsp;',
          u'&mdash;', u'&rsquo;', u'&quot;']
M['ent_fam'] = ENTFAM
M['ent_raw'] = [[T[i].count(e) for e in ENTFAM] for i in range(NS)]
M['ent_total'] = [sum(x) for x in M['ent_raw']]

SG = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'), (u'&quot;', u'"'),
      (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'), (u'&#215;', u'x'), (u'&rarr;', u'->'),
      (u'&rsquo;', u"'"), (u'&lsquo;', u"'"), (u'&mdash;', u'-'), (u'&ndash;', u'-'), (u'&deg;', u'deg'),
      (u'&infin;', u'inf'), (u'\xa0', u' '), (u'\u2212', u'-'), (u'\u2013', u'-'), (u'\u2014', u'-'),
      (u'\xd7', u'x'), (u'\u2018', u"'"), (u'\u2019', u"'"), (u'\u201c', u'"'), (u'\u201d', u'"'),
      (u'\u2192', u'->')]


def detag(s, fill):
    """剥壳口径照抄 audit.py 的 _atom_face: 注释→空格, <br>→空格, 其余标签→fill, 再单趟实体表。"""
    s = re.sub(r'(?s)<!--.*?-->', u' ', s)
    s = re.sub(r'(?i)<br\s*/?>', u' ', s)
    s = re.sub(r'<[^>]+>', fill, s)
    for a, b in SG:
        s = s.replace(a, b)
    return s


def fold(s):
    return re.sub(u'\\s+', u' ', s).strip()


FOLD = [fold(T[i]) for i in range(NS)]                       # 全篇折平, 未剥壳
# 剥壳两档只送 html: txt 的 ASCII 图里有 `< | | >` 型假标签, 整篇剥壳会吃掉插图字符
# (与 audit.py 的 _atom_face 同口径——它对非 .html/.htm 的份直接返回原文)。
DS = [fold(detag(T[i], u' ')) if ISH[i] else FOLD[i] for i in range(NS)]   # 断面
DJ = [fold(detag(T[i], u'')) if ISH[i] else FOLD[i] for i in range(NS)]    # 粘面
# 面上残留的实体族(转义层是否被单趟替换吃干净, 逐族点名)
M['ent_resid_ds'] = [[DS[i].count(e) for e in ENTFAM] for i in range(NS)]
M['ent_double_left'] = [DS[i].count(u'&amp;') for i in range(NS)]     # 双重转义残留(单趟只吃一层)
M['ent_numeric_left'] = [sum(DS[i].count(e) for e in (u'&#34;', u'&#39;', u'&#43;', u'&#x2F;'))
                         for i in range(NS)]
M['ent_lt_left'] = [DS[i].count(u'&lt;') for i in range(NS)]
assert M['ent_lt_left'] == [0] * NS
assert M['ent_double_left'][4] > 0 and sum(M['ent_double_left'][:4]) == 0
assert M['ent_numeric_left'][4] > 0 and sum(M['ent_numeric_left'][:4]) == 0
assert M['ent_double_left'][3] == 0 and M['ent_numeric_left'][3] == 0

# ---------- 页壳(仅 txt 有; html 无 [Page N] 页眉) ----------
SHELLP = [re.compile(u'^.*\\[Page \\d+\\].*$'),
          re.compile(u'^\\s*RFC ?\\d{3,4}\\s+.*((19|20)\\d\\d)\\s*$'),
          re.compile(u'^\\s*Postel\\s+.*\\d\\d\\d\\d\\s*$'),
          re.compile(u'^\\s*Internet Engineering Task Force\\s+\\[Page \\d+\\]\\s*$')]


def is_shell(x):
    s = x.rstrip()
    if s == u'' or s == u'\x0c' or s.strip(u'\x0c') == u'':
        return True
    return any(p.match(s) for p in SHELLP)


M['shell_n'] = [0 if ISH[i] else len([x for x in L[i] if is_shell(x)]) for i in range(NS)]
M['shell_strip'] = [M['lines'][i] - M['shell_n'][i] for i in range(NS)]
M['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NS)]
M['shell_page'] = [len([x for x in L[i] if re.search(u'\\[Page \\d+\\]', x)]) for i in range(NS)]
M['shell_hdr'] = [len([x for x in L[i] if re.match(u'^\\s*RFC ?\\d{3,4}\\s+.*((19|20)\\d\\d)\\s*$', x)])
                  for i in range(NS)]
assert M['shell_page'][:3] == [68, 98, 95]
assert M['shell_n'][3] == M['shell_n'][4] == 0
SH = [FOLD[i] if ISH[i] else fold(NL.join([x for x in L[i] if not is_shell(x)])) for i in range(NS)]
# txt 无标签 ⇒ 剥壳两档与摘壳档同读数; html 无页壳 ⇒ 摘壳档与全篇折平同读数(减去空白差异)
assert DS[0] == DJ[0] and DS[1] == DJ[1] and DS[2] == DJ[2]
WIDE = [DS[i] if ISH[i] else SH[i] for i in range(NS)]       # 最宽档: 建锚面

# ---------- 答句针(五档) ----------
PATS = [
    # 821: 只分类不定时——两族回复码的定义, 加“难定义 transient”的自认
    (0, u'c821_4yz_class', u'4yz Transient Negative Completion reply'),
    (0, u'c821_5yz_class', u'5yz Permanent Negative Completion reply'),
    (0, u'c821_temporary', u'the error condition is temporary and the action may be requested again'),
    (0, u'c821_hard_to_define', u'It is difficult to assign a meaning to "transient"'),
    (0, u'c821_must_agree', u'must agree on the interpretation'),
    (0, u'c821_different_time', u'Each reply in this category might have a different time value'),
    (0, u'c821_encouraged', u'the sender-SMTP is encouraged to try again'),
    (0, u'c821_rule_of_thumb', u'A rule of thumb to determine if a reply fits into the 4yz'),
    (0, u'c821_discouraged', u'The sender-SMTP is discouraged from repeating the exact request'),
    # 1123: 主机要求——下限三条 + DNS 那一条
    (1, u'c1123_must_delay', u'The sender MUST delay retrying a particular destination'),
    (1, u'c1123_floor_30min', u'the retry interval SHOULD be at least 30 minutes'),
    (1, u'c1123_giveup_45days', u'the give-up time generally needs to be at least 4-5 days'),
    (1, u'c1123_must_configurable', u'The parameters to the retry algorithm MUST be configurable'),
    (1, u'c1123_backoff_once', u'backing off to once every two or three hours'),
    (1, u'c1123_two_in_hour', u'two connection attempts in the first hour'),
    (1, u'c1123_dns_backoff', u'the retry interval SHOULD be constrained by an exponential'),
    (1, u'c1123_dns_5sec', u'default of no less than 5 seconds should be used'),
    (1, u'c1123_queueing_must', u'Any queueing strategy MUST include'),
    # 5321: 同段搬进协议标准 + NDN 例外 + 术语换人
    (2, u'c5321_must_delay', u'The sender MUST delay retrying a particular destination after one'),
    (2, u'c5321_floor_30min', u'the retry interval SHOULD be at least 30 minutes'),
    (2, u'c5321_giveup_45days', u'the give-up time generally needs to be at least 4-5 days'),
    (2, u'c5321_may_shorter_ndn', u'It MAY be appropriate to set a shorter maximum number of retries'),
    (2, u'c5321_ndn_scope', u'delivery notifications and equivalent error messages'),
    (2, u'c5321_must_configurable', u'The parameters to the retry algorithm MUST be configurable'),
    (2, u'c5321_backoff_one', u'backing off to one every two or three hours'),
    (2, u'c5321_queuing_must', u'Any queuing strategy MUST include timeouts on all activities'),
    (2, u'c5321_must_not_cache5yz', u'5yz responses to the MAIL command MUST NOT be cached'),
    (2, u'c5321_sec_head', u'4.5.4.1. Sending Strategy'),
    (1, u'c1123_sec_head', u'5.3.1.1 Sending Strategy'),
    # exim: 阶梯规则串 + 算法字母 + 24h 封顶 + 四天 cutoff
    (3, u'cexim_default_rule', u'* * F,2h,15m; G,16h,1h,1.5; F,4d,6h'),
    (3, u'cexim_cutoff_four_days', u'the cutoff time is four days'),
    (3, u'cexim_letter_def', u'The letter identifies the algorithm for computing a new retry time'),
    (3, u'cexim_cutoff_def', u'the cutoff time is the time beyond which this algorithm no longer applies'),
    (3, u'cexim_from_first_failure', u'measured from the time that the first failure'),
    (3, u'cexim_rim_limits', u'retry_interval_max limits the maximum interval between retries'),
    (3, u'cexim_rim_24h', u'It cannot be set greater than 24h'),
    (3, u'cexim_24h_default', u'which is its default value'),
    (3, u'cexim_every_30min', u'They happen every 30 minutes for 24 hours only'),
    (3, u'cexim_letter_bond_ds', u'< letter >,< cutoff time >,< arguments >'),
    (3, u'cexim_letter_bond_dj', u'<letter>,<cutoff time>,<arguments>'),
    (3, u'cexim_fixed_intervals', u'F : retry at fixed intervals'),
    (3, u'cexim_randomized', u'H : retry at randomized intervals'),
    (3, u'cexim_expire_7days', u'retry_data_expire (default 7 days)'),
    (3, u'cexim_beyond_cutoff', u'If a message has been on the queue for longer than the cutoff time'),
    # postfix: 六个参数默认 + “0=只试一次” + 单位表
    (4, u'cpf_mql_5d', u'maximal_queue_lifetime (default: 5d)'),
    (4, u'cpf_bql_5d', u'bounce_queue_lifetime (default: 5d)'),
    (4, u'cpf_minbo_300s', u'minimal_backoff_time (default: 300s)'),
    (4, u'cpf_maxbo_4000s', u'maximal_backoff_time (default: 4000s)'),
    (4, u'cpf_qrd_300s', u'queue_run_delay (default: 300s)'),
    (4, u'cpf_trt_60s', u'transport_retry_time (default: 60s)'),
    (4, u'cpf_zero_once', u'Specify 0 when mail delivery should be tried only once'),
    (4, u'cpf_min_time', u'The minimal time between attempts to deliver a deferred message'),
    (4, u'cpf_max_time', u'The maximal time between attempts to deliver a deferred message'),
    (4, u'cpf_prior_1000s', u'prior to Postfix 2.4 the default value was 1000s'),
    (4, u'cpf_unit_table', u'Time units: s (seconds), m (minutes), h (hours), d (days), w (weeks)'),
    (4, u'cpf_default_unit_d', u'The default time unit is d (days)'),
    (4, u'cpf_default_unit_s', u'The default time unit is s (seconds)'),
    (4, u'cpf_ge_minbo', u'set to a value greater than or equal to $minimal_backoff_time'),
    (4, u'cpf_ge_qrd', u'set greater than or equal to $queue_run_delay'),
    (4, u'cpf_malfunction', u'contact a malfunctioning message delivery transport'),
]
PR = dict((k, p) for _, k, p in PATS)
M['needle_n'] = len(PATS)
for nm in ('strict', 'fold', 'sh', 'ds', 'dj'):
    M['p_' + nm] = {}
M['p_lines'] = {}
for o, k, _ in PATS:
    lit = PR[k]
    M['p_strict'][k] = len([x for x in L[o] if lit in x])
    M['p_fold'][k] = FOLD[o].count(lit)
    M['p_sh'][k] = SH[o].count(lit)
    M['p_ds'][k] = DS[o].count(lit)
    M['p_dj'][k] = DJ[o].count(lit)
    hits = [n for n, x in enumerate(L[o], 1) if lit in x]
    M['p_lines'][k] = hits[0] if hits else None


def own(i, f):
    return len([k for o, k, _ in PATS if o == i and f[k]])


STRICT = [own(i, M['p_strict']) for i in range(NS)]
FOLDT = [own(i, M['p_fold']) for i in range(NS)]
SHT = [own(i, M['p_sh']) for i in range(NS)]
DST = [own(i, M['p_ds']) for i in range(NS)]
DJT = [own(i, M['p_dj']) for i in range(NS)]
M['sn_strict_docs'] = STRICT
M['sn_fold_docs'] = FOLDT
M['sn_sh_docs'] = SHT
M['sn_ds_docs'] = DST
M['sn_dj_docs'] = DJT
M['fold_minus_strict'] = [FOLDT[i] - STRICT[i] for i in range(NS)]
M['sh_minus_fold'] = [FOLDT[i] - SHT[i] for i in range(NS)]
M['ds_minus_sh'] = [SHT[i] - DST[i] for i in range(NS)]      # 摘壳档在 html 上读不到的针数
M['ds_only_own'] = [DST[i] - SHT[i] for i in range(NS)]
M['dj_vs_ds'] = [DST[i] - DJT[i] for i in range(NS)]
M['wide_n'] = sum(max(0, x) for x in M['ds_only_own'])
M['dead_needles'] = [k for o, k, _ in PATS
                     if max(M['p_fold'][k], M['p_sh'][k], M['p_ds'][k], M['p_dj'][k],
                            M['p_strict'][k]) == 0]
M['strict_only'] = [k for o, k, _ in PATS if M['p_strict'][k]
                    and not max(M['p_fold'][k], M['p_sh'][k], M['p_ds'][k], M['p_dj'][k])]
assert all(STRICT[i] <= FOLDT[i] for i in range(NS))
assert all(STRICT[i] + M['fold_minus_strict'][i] == FOLDT[i] for i in range(NS))
assert sum(M['sh_minus_fold']) >= 0
assert M['dead_needles'] == []
assert M['ds_only_own'][3] > 0 or M['ds_only_own'][4] > 0
M['bond_pair_n'] = len([1 for o, k, _ in PATS if k.startswith(u'cexim_letter_bond')])
assert M['bond_pair_n'] == 2 and M['p_ds'][u'cexim_letter_bond_dj'] == 0
assert M['p_dj'][u'cexim_letter_bond_ds'] == 0

# ---------- 序列化三式(只在原面上看得见, 折平后各自塌成一档) ----------
# (a) 小节编号排版: 1123 代“5.3.1.1 Sending Strategy”(无尾点⇎单空格) ⇎ 5321 代“4.5.4.1.  Sending
#     Strategy”(尾点⇎两空格); 折面上双空格塌成单空格, 两式合一 ⇒ 只有逐行面分得出两代。
HB = u'^\\s*\\d+(?:\\.\\d+)+'
M['hdr_dot2sp'] = [len([x for x in L[i] if re.match(HB + u'\\.  \\S', x)]) for i in range(NS)]
M['hdr_dot1sp'] = [len([x for x in L[i] if re.match(HB + u'\\. \\S', x)]) for i in range(NS)]
M['hdr_nodot'] = [len([x for x in L[i] if re.match(HB + u' \\S', x)]) for i in range(NS)]
M['hdr_dot2sp_fold'] = [len(re.findall(HB + u'\\.  \\S', FOLD[i])) for i in range(NS)]
assert M['hdr_dot2sp_fold'] == [0] * NS
# (b) 折行断字: 行尾连字符 + 下行小写 ⇒ 折面读出“non- delivery”, 跨行字面针必须按带空格的断面写。
M['hyphen_break'] = [len([1 for j in range(len(L[i]) - 1)
                          if L[i][j].rstrip().endswith(u'-') and re.match(u'^\\s*[a-z]', L[i][j + 1])])
                     for i in range(NS)]
M['ndn_hyphen_break'] = [len(re.findall(u'non-' + NL + u'\\s+delivery', T[i])) for i in range(NS)]
assert M['ndn_hyphen_break'][2] >= 1 and M['ndn_hyphen_break'][1] >= 1
# (c) html 双转义: 见 ent_double_left ⇎ ent_numeric_left(上面已逐族点名)

# ---------- 措辞档: 同一问题的五族答法 ----------
TIERP = [u'difficult to assign a meaning', u'SHOULD be at least 30 minutes',
         u'at least 4-5 days', u'MUST be configurable', u'cutoff time',
         u'(default: 5d)', u'(default: 300s)', u'(default: 4000s)', u'(default: 60s)',
         u'tried only once', u'encouraged to try again', u'MAY be appropriate']
M['tier_pats'] = TIERP
M['tier_faces'] = [[WIDE[i].count(p) for p in TIERP] for i in range(NS)]
M['tier_tot'] = [sum(x) for x in M['tier_faces']]
assert M['tier_faces'][0][4] == 0 and M['tier_faces'][0][11] == 0
M['time_digit_docs'] = [len(re.findall(u'\\d+\\s*(minutes?|hours?|days?|seconds?)', WIDE[i]))
                        for i in range(NS)]
M['time_digit_821'] = M['time_digit_docs'][0]

# ---------- 义务词五轨 + 小写 must ----------
TONE = [u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY']
M['tone_pats'] = TONE
M['tone'] = [[len(re.findall(u'(?<![A-Za-z0-9])' + re.escape(p) + u'(?![A-Za-z0-9])', WIDE[i]))
              for p in TONE] for i in range(NS)]
M['tone_tot'] = [sum(x) for x in M['tone']]
M['tone_must_lc'] = [len(re.findall(u'(?<![A-Za-z])must(?![A-Za-z])', WIDE[i])) for i in range(NS)]
M['tone_zero_must'] = [1 if (M['tone'][i][0] + M['tone'][i][1]) == 0 else 0 for i in range(NS)]
M['tone_zero_all'] = [1 if sum(M['tone'][i]) == 0 else 0 for i in range(NS)]
M['kw_clause'] = [len(re.findall(u'(?i)key words', WIDE[i])) for i in range(NS)]
# 821 的两枚大写 SHOULD 出自全大写注, 唯一一枚 MAY 是月份语法 <mon> ::= … | "MAY" | … ——
# 该份连“义务词档”都还没建立(2119 号关键字惯例要到 1997 年才立), 所以档位只能按 MUST 族判零。
M['c821_may_month'] = WIDE[0].count(u'"MAY"')
assert M['tone_zero_must'] == [1, 0, 0, 1, 0]
assert M['tone_zero_all'] == [0, 0, 0, 1, 0]
assert M['c821_may_month'] == 1 and M['tone'][0][2:] == [0, 2, 1]
assert M['kw_clause'][0] == 0 and sum(M['kw_clause'][3:]) == 0
# MUST NOT 先于 MUST 计数: 上面用边界负向断言已分开两档, 此处复核
assert all(M['tone'][i][0] <= M['tone'][i][1] for i in range(NS))

# ---------- 术语尺: 谁在延迟重试 ----------
TERMP = [u'sender-SMTP', u'SMTP client', u'SMTP-receiver', u'receiver-SMTP', u'queueing', u'queuing',
         u'queue', u'retry', u'retries', u'retrying']
M['term_pats'] = TERMP
M['terms'] = [[WIDE[i].count(p) for p in TERMP] for i in range(NS)]
M['sender_smtp'] = [x[0] for x in M['terms']]
M['smtp_client'] = [x[1] for x in M['terms']]
M['receiver_smtp'] = [x[3] for x in M['terms']]
M['spelling_queueing'] = [x[4] for x in M['terms']]
M['spelling_queuing'] = [x[5] for x in M['terms']]
M['retry_word'] = [sum(x[7:]) for x in M['terms']]          # retry ⇎ retries ⇎ retrying
M['queue_word'] = list(x[6] for x in M['terms'])
# 术语换人: 1123 只用旧名(sender-SMTP 17 枚 ⇎ SMTP client 0 枚), 5321 换主名但旧名残留 3 枚,
# Exim 两份 MTA 文书都不用 SMTP 角色名, Postfix 只用新名。
assert M['sender_smtp'][3] == M['sender_smtp'][4] == 0
assert M['sender_smtp'][1] > M['sender_smtp'][2] > 0
assert M['smtp_client'][0] == M['smtp_client'][1] == M['smtp_client'][3] == 0
assert M['smtp_client'][2] > 0 and M['smtp_client'][4] > 0
M['term_new_per_mille'] = [(1000 * M['smtp_client'][i]) // (M['smtp_client'][i] + M['sender_smtp'][i])
                           if (M['smtp_client'][i] + M['sender_smtp'][i]) else -1 for i in range(NS)]
M['spelling_queueing'] = [x[4] for x in M['terms']]
assert M['spelling_queueing'][1] > 0 and M['spelling_queueing'][2] == 0
assert M['spelling_queueing'][3] == 0
assert M['spelling_queuing'][2] > 0 and M['spelling_queuing'][0] == M['spelling_queuing'][1] == 0
assert M['retry_word'][0] == 0 and M['queue_word'][0] == 0
assert min(M['retry_word'][1:]) > 0
M['c821_no_retry_vocabulary'] = 1 if (M['retry_word'][0] == 0 and M['queue_word'][0] == 0) else 0

# ---------- Exim 规则串: 逐枚解析成秒 ----------
UNIT = {u's': 1, u'm': 60, u'h': 3600, u'd': 86400, u'w': 604800}


def secs(tok):
    m = re.match(u'^(\\d+)([smhdw])$', tok)
    assert m, tok
    return int(m.group(1)) * UNIT[m.group(2)]


M['unit_table'] = [[k, UNIT[k]] for k in u'smhwd']
RULES = re.findall(u'\\b([FGPH]),(\\d+\\w),(\\d+\\w)(?:,(\\d+(?:\\.\\d+)?))?\\b', DJ[3])
M['exim_rules_raw'] = sorted(set(u'%s,%s,%s%s' % (a, b, c, (u',' + d) if d else u'')
                                 for a, b, c, d in RULES))
M['exim_rule_n'] = len(M['exim_rules_raw'])
M['exim_sets_n'] = len(RULES)
M['exim_letters'] = sorted(set(a for a, _, _, _ in RULES))
M['exim_cutoff_sec'] = sorted(set(secs(b) for _, b, _, _ in RULES))
M['exim_arg1_sec'] = sorted(set(secs(c) for _, _, c, _ in RULES))
M['exim_mult'] = sorted(set(float(d) for _, _, _, d in RULES if d))
M['exim_default_rule'] = u'* * F,2h,15m; G,16h,1h,1.5; F,4d,6h'
dr = re.findall(u'([FGPH]),(\\d+\\w),(\\d+\\w)(?:,(\\d+(?:\\.\\d+)?))?', M['exim_default_rule'])
M['exim_default_sets'] = [u','.join([x[0], x[1], x[2], x[3]]).strip(u',') for x in dr]
M['exim_default_cutoffs'] = [secs(x[1]) for x in dr]
M['exim_default_first'] = [secs(x[2]) for x in dr]
M['exim_default_mult'] = [float(x[3]) for x in dr if x[3]]
M['exim_rim_cap'] = secs(u'24h')
M['exim_default_span'] = M['exim_default_cutoffs'][-1]
assert M['exim_rule_n'] >= 6 and M['exim_letters'] == ['F', 'G']
assert M['exim_default_cutoffs'] == [7200, 57600, 345600]
assert M['exim_default_first'] == [900, 3600, 21600]
assert M['exim_default_mult'] == [1.5]
assert M['exim_rim_cap'] == 86400

# ---------- Postfix 参数默认: 逐枚解析成秒 ----------
PARAM6 = [u'maximal_queue_lifetime', u'bounce_queue_lifetime', u'minimal_backoff_time',
          u'maximal_backoff_time', u'queue_run_delay', u'transport_retry_time']
M['pf_params'] = PARAM6
DEF = dict((p, re.findall(p + u' \\(default: ([^)]*)\\)', DJ[4])) for p in PARAM6)
M['pf_def_raw'] = dict((p, DEF[p]) for p in PARAM6)
M['pf_def_tok'] = dict((p, sorted(set(re.findall(p + u' \\(default: (\\d+[smhdw])\\)', DJ[4]))))
                       for p in PARAM6)
M['pf_def_sec'] = dict((p, secs(re.findall(p + u' \\(default: (\\d+[smhdw])\\)', DJ[4])[0]))
                       for p in PARAM6)
M['pf_index_hit'] = [1 if len(DEF[p]) == 2 else 0 for p in PARAM6]     # 索引列一枚 + 正文一节
M['pf_body_hit'] = [len(DEF[p]) for p in PARAM6]
M['pf_zero_once'] = DJ[4].count(u'Specify 0 when mail delivery should be tried only once')
M['pf_unit_line'] = DJ[4].count(u'Time units: s (seconds), m (minutes), h (hours), d (days), w (weeks)')
M['pf_default_unit'] = {u's': DJ[4].count(u'The default time unit is s (seconds)'),
                        u'd': DJ[4].count(u'The default time unit is d (days)')}
assert M['pf_def_sec'][u'maximal_queue_lifetime'] == 432000
assert M['pf_def_sec'][u'minimal_backoff_time'] == M['pf_def_sec'][u'queue_run_delay'] == 300
assert M['pf_def_sec'][u'maximal_backoff_time'] == 4000
assert M['pf_def_sec'][u'transport_retry_time'] == 60
assert M['pf_unit_line'] >= 6

# ---------- 跨源时长换算(建条目侧的推导点原料) ----------
FLOOR_30MIN = 1800
CONV = [(u'1123/5321 下限 30 分钟', FLOOR_30MIN),
        (u'exim 首档间隔 15m', secs(u'15m')),
        (u'exim 次档起始 1h', secs(u'1h')),
        (u'postfix minimal_backoff_time 300s', M['pf_def_sec'][u'minimal_backoff_time']),
        (u'postfix queue_run_delay 300s', M['pf_def_sec'][u'queue_run_delay']),
        (u'postfix transport_retry_time 60s', M['pf_def_sec'][u'transport_retry_time']),
        (u'postfix maximal_backoff_time 4000s', M['pf_def_sec'][u'maximal_backoff_time']),
        (u'exim retry_interval_max 24h', M['exim_rim_cap'])]
M['conv_sec'] = dict((k, v) for k, v in CONV)
M['below_floor'] = sorted([k for k, v in CONV if v < FLOOR_30MIN])
M['above_floor'] = sorted([k for k, v in CONV if v >= FLOOR_30MIN])
M['floor_ratio_max'] = max(v for k, v in CONV) / FLOOR_30MIN
GIVEUP_45 = [(4 * 86400, 5 * 86400)]
M['giveup_band_sec'] = GIVEUP_45[0]
M['exim_cutoff_in_band'] = 1 if GIVEUP_45[0][0] <= M['exim_default_span'] <= GIVEUP_45[0][1] else 0
M['pf_lifetime_in_band'] = 1 if GIVEUP_45[0][0] <= M['pf_def_sec'][u'maximal_queue_lifetime'] \
    <= GIVEUP_45[0][1] else 0
M['pf_bql_same_as_mql'] = 1 if M['pf_def_sec'][u'bounce_queue_lifetime'] == \
    M['pf_def_sec'][u'maximal_queue_lifetime'] else 0
M['pf_ge_chain'] = [M['pf_def_sec'][u'maximal_backoff_time'] >= M['pf_def_sec'][u'minimal_backoff_time'],
                    M['pf_def_sec'][u'minimal_backoff_time'] >= M['pf_def_sec'][u'queue_run_delay']]
M['exim_g_steps'] = [secs(u'1h') * (M['exim_default_mult'][0] ** k) for k in range(0, 6)]
M['exim_g_capped_at_rim'] = [1 if v >= M['exim_rim_cap'] else 0 for v in M['exim_g_steps']]

# ---------- 出处头与年份 ----------
M['obs'] = [([y for y in L[i] if y.startswith(u'Obsoletes:')] or [None])[0] for i in range(NS)]
M['upd'] = [([y for y in L[i] if y.startswith(u'Updates:')] or [None])[0] for i in range(NS)]
M['obs_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{4}', M['obs'][i] or u''))) for i in range(NS)]
M['upd_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{4}', M['upd'][i] or u''))) for i in range(NS)]
M['rfc_hdr'] = [(re.findall(u'^Request for Comments: ?(\\d+)', NL.join(L[i][:20]), re.M) or [None])[0]
                for i in range(NS)]
M['years'] = [1982, 1989, 2008, 2012, 2025]
M['year_src'] = [u'页眉 August 1982(68 页重复)', u'页眉 October 1989', u'页眉 October 2008',
                 u'Copyright 行 1995-2012', u'镜像页脚 2025-07-19']
M['year_gaps'] = [M['years'][i + 1] - M['years'][i] for i in range(NS - 1)]
M['year_span'] = M['years'][-1] - M['years'][0]
assert M['years'] == sorted(M['years'])
assert M['obs_ids'][2] == [2821] and M['upd_ids'][2] == [1123]
assert M['obs_ids'][0] == [] and M['obs_ids'][1] == []
assert M['rfc_hdr'] == [None, u'1123', u'5321', None, None]

# ---------- 共用长行池(归一后取交, 逐字节同形另计) ----------
def pn(s):
    return u' '.join(s.lower().split())


PL = [set(pn(x) for x in L[i] if len(pn(x)) >= 40 and not is_shell(x)) for i in range(NS)]
VARY = [{} for _ in range(NS)]
for i in range(NS):
    for y in L[i]:
        if len(pn(y)) >= 40 and not is_shell(y):
            VARY[i].setdefault(pn(y), set()).add(y.rstrip(u'\r'))
PAIRS = [(a, b) for a in range(NS) for b in range(a + 1, NS)]
M['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
M['pair_share'] = [len(PL[a] & PL[b]) for a, b in PAIRS]
RAWS = [set(x.rstrip(u'\r') for x in L[i] if len(pn(x)) >= 40 and not is_shell(x)) for i in range(NS)]
M['pair_byte'] = [len(RAWS[a] & RAWS[b]) for a, b in PAIRS]
M['pair_norm_only'] = [M['pair_share'][n] - M['pair_byte'][n] for n in range(len(PAIRS))]
assert all(M['pair_norm_only'][n] >= 0 for n in range(len(PAIRS)))
M['pair_nonzero'] = len([x for x in M['pair_share'] if x])
M['pair_zero'] = len(PAIRS) - M['pair_nonzero']
PRES = dict((a, tuple(i for i in range(NS) if a in PL[i])) for s in PL for a in s)
M['pool_n'] = len(PRES)
M['pool_tier'] = [len([a for a, v in PRES.items() if len(v) == k]) for k in range(1, NS + 1)]
assert sum(M['pool_tier']) == M['pool_n']
M['pool_2'] = M['pool_tier'][1]
M['pool_3'] = M['pool_tier'][2]
M['pair_max'] = max(M['pair_share'])
M['pair_max_lbl'] = M['pair_lbl'][M['pair_share'].index(M['pair_max'])]
M['pool_html_own'] = len([a for a, v in PRES.items() if 3 in v or 4 in v])
M['pool_html_shared'] = len([a for a, v in PRES.items() if (3 in v or 4 in v) and len(v) >= 2])
assert M['pool_html_shared'] == 0
M['pool_txt_shared'] = len([a for a, v in PRES.items() if len(v) >= 2 and max(v) < 3])
assert M['pool_txt_shared'] == sum(1 for a, v in PRES.items() if len(v) >= 2)

# 写法分家: 归一相同 ⇎ 逐字节不同 ⇒ 按最弱闭合档归一桶(case > hyph > space > multi)
BUCK = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
CAND = set()
for a, b in PAIRS:
    for x in PL[a] & PL[b]:
        if any(p == q for p in VARY[a][x] for q in VARY[b][x]):
            continue
        CAND.add(x)
RANK = {u'case': 0, u'hyph': 1, u'space': 2, u'multi': 3}
for x in sorted(CAND):
    cls = None
    for a, b in PAIRS:
        if x not in PL[a] & PL[b]:
            continue
        for p in VARY[a][x]:
            for q in VARY[b][x]:
                if p == q:
                    continue
                if p.lower() == q.lower():
                    w = u'case'
                elif re.sub(u'-\\s*', u'', p).lower() == re.sub(u'-\\s*', u'', q).lower():
                    w = u'hyph'
                elif p.strip() == q.strip():
                    w = u'space'
                else:
                    w = u'multi'
                cls = w if cls is None else (cls if RANK[cls] <= RANK[w] else w)
    BUCK[cls] += 1
M['axis_distinct'] = len(CAND)
M['axis_counts'] = BUCK
assert sum(BUCK.values()) == len(CAND)
M['axis_str'] = u'case%d⇎hyph%d⇎space%d⇎multi%d' % (BUCK[u'case'], BUCK[u'hyph'],
                                                    BUCK[u'space'], BUCK[u'multi'])

# ---------- 容斥(行尺: 池的分档 ⇎ 两两/三三/四四/五五交) ----------
import itertools as IT
_t1 = sum(len(PL[i]) for i in range(NS))
_t2 = sum(len(PL[a] & PL[b]) for a, b in PAIRS)
_t3 = sum(len(PL[a] & PL[b] & PL[c]) for a, b, c in IT.combinations(range(NS), 3))
_t4 = sum(len(PL[a] & PL[b] & PL[c] & PL[d]) for a, b, c, d in IT.combinations(range(NS), 4))
_t5 = len(PL[0] & PL[1] & PL[2] & PL[3] & PL[4])
M['incl'] = [_t1, _t2, _t3, _t4, _t5]
M['union_incl'] = _t1 - _t2 + _t3 - _t4 + _t5
M['union_close'] = M['pool_n'] - M['union_incl']
assert M['union_close'] == 0
assert _t4 == _t5 == 0

# ---------- 第二把尺: 句级原子(1123 与 5321 是同一段被重排过行宽的, 行尺只撞得出巧合同形的行) ----------
def sents(face):
    return [u' '.join(x.lower().split()) for x in re.split(u'(?<=[.!?])\\s+(?=[A-Z0-9*<])', face)]


SP = [set(x for x in sents(WIDE[i]) if len(x) >= 40) for i in range(NS)]
SPRES = dict((a, tuple(i for i in range(NS) if a in SP[i])) for s in SP for a in s)
M['s_pool_n'] = len(SPRES)
M['s_pool_tier'] = [len([a for a, v in SPRES.items() if len(v) == k]) for k in range(1, NS + 1)]
assert sum(M['s_pool_tier']) == M['s_pool_n']
M['s_pair_share'] = [len(SP[a] & SP[b]) for a, b in PAIRS]
M['s_pair_max'] = max(M['s_pair_share'])
M['s_pair_max_lbl'] = M['pair_lbl'][M['s_pair_share'].index(M['s_pair_max'])]
M['s_pair_html'] = len([n for n, (a, b) in enumerate(PAIRS)
                        if (a >= 3 or b >= 3) and M['s_pair_share'][n]])
assert M['s_pair_html'] == 0
_s1 = sum(len(SP[i]) for i in range(NS))
_s2 = sum(M['s_pair_share'])
_s3 = sum(len(SP[a] & SP[b] & SP[c]) for a, b, c in IT.combinations(range(NS), 3))
_s4 = sum(len(SP[a] & SP[b] & SP[c] & SP[d]) for a, b, c, d in IT.combinations(range(NS), 4))
_s5 = len(SP[0] & SP[1] & SP[2] & SP[3] & SP[4])
M['s_incl'] = [_s1, _s2, _s3, _s4, _s5]
M['s_union_incl'] = _s1 - _s2 + _s3 - _s4 + _s5
M['s_union_close'] = M['s_pool_n'] - M['s_union_incl']
assert M['s_union_close'] == 0
M['s_retry_pair_share'] = M['s_pair_share'][PAIRS.index((1, 2))]
assert M['s_retry_pair_share'] > M['pair_share'][PAIRS.index((1, 2))]
assert M['s_pool_tier'][4] == _s5

# ---------- 窗口(摘要遍取段用) ----------
WIN = {}
for i, k in ((1, u'1123'), (2, u'5321')):
    h = [n for n, x in enumerate(L[i], 1) if re.search(u'Sending Strategy', x) and n > 200]
    g = [n for n, x in enumerate(L[i], 1) if u'MUST delay retrying' in x]
    e = [n for n, x in enumerate(L[i], 1) if u'configurable' in x and n > g[0]]
    WIN[k] = [h[0], g[0], e[0]]
M['win'] = WIN
M['win_821_line'] = [n for n, x in enumerate(L[0], 1) if u'difficult to assign a meaning' in x]
M['win_821_page'] = [int(x) for y in L[0][:M['win_821_line'][0]]
                     for x in re.findall(u'^.*\\[Page (\\d+)\\].*$', y)]
M['win_exim_lines'] = [n for n, x in enumerate(L[3], 1) if u'F,4d,6h' in x]
M['win_pf_lines'] = dict((p, [n for n, x in enumerate(L[4], 1) if p + u' (default:' in x]) for p in PARAM6)

json.dump(M, io.open(u'corpus/_b74meas.json', 'w', encoding='utf-8'), indent=1, sort_keys=True)
print(u'采集遍: 字节 ' + u'⇎'.join(str(x) for x in M['bytes']) + u' ｜ 行 '
      + u'⇎'.join(str(x) for x in M['lines']) + u' ｜ 非空 ' + u'⇎'.join(str(x) for x in M['nonblank'])
      + u' ｜ 换页 ' + u'⇎'.join(str(x) for x in M['ff']) + u' ｜ 壳行 '
      + u'⇎'.join(str(x) for x in M['shell_n']) + u' ｜ 标签 ' + u'⇎'.join(str(x) for x in M['tag_open']))
print(u'针 ' + str(M['needle_n']) + u' 枚五档: 原面 ' + u'⇎'.join(str(x) for x in STRICT) + u' ｜ 折平 '
      + u'⇎'.join(str(x) for x in FOLDT) + u' ｜ 摘壳 ' + u'⇎'.join(str(x) for x in SHT) + u' ｜ 断面 '
      + u'⇎'.join(str(x) for x in DST) + u' ｜ 粘面 ' + u'⇎'.join(str(x) for x in DJT)
      + u' ｜ 折行独有 ' + str(sum(M['fold_minus_strict'])) + u' ｜ 跨壳丢针 ' + str(sum(M['sh_minus_fold']))
      + u' ｜ 剥壳独有 ' + str(M['wide_n']) + u' ｜ 断面−粘面 ' + str(sum(M['dj_vs_ds']))
      + u' ｜ 死集 ' + str(M['dead_needles']) + u' ｜ 仅原面 ' + str(M['strict_only']))
print(u'义务词五轨 ' + u' ⇎ '.join(u'%d/%d/%d/%d/%d' % tuple(M['tone'][i]) for i in range(NS))
      + u' ｜ 小写must ' + u'⇎'.join(str(x) for x in M['tone_must_lc'])
      + u' ｜ MUST 族零份 ' + u'⇎'.join(str(x) for x in M['tone_zero_must'])
      + u' ｜ 五轨全零份 ' + u'⇎'.join(str(x) for x in M['tone_zero_all']))
print(u'术语尺 sender-SMTP ' + u'⇎'.join(str(x) for x in M['sender_smtp']) + u' ｜ SMTP client '
      + u'⇎'.join(str(x) for x in M['smtp_client']) + u' ｜ queueing⇎queuing '
      + u'⇎'.join('%d⇎%d' % (M['spelling_queueing'][i], M['spelling_queuing'][i]) for i in range(NS)))
print(u'exim 规则 ' + str(M['exim_rule_n']) + u' 串/' + str(M['exim_sets_n']) + u' 集 档 '
      + u'⇎'.join(M['exim_rules_raw']) + u' ｜ postfix 默认 '
      + u'⇎'.join(u'%s=%ds' % (p, M['pf_def_sec'][p]) for p in PARAM6))
print(u'池 ' + str(M['pool_n']) + u' 档 ' + u'⇎'.join(str(x) for x in M['pool_tier']) + u' ｜ 最大对 '
      + M['pair_max_lbl'] + u' ' + str(M['pair_max']) + u' ｜ 零共用对 ' + str(M['pair_zero'])
      + u' ｜ 轴 ' + M['axis_str'] + u' ｜ 容斥 ' + u'⇎'.join(str(x) for x in M['incl'])
      + u'→' + str(M['union_incl']))
print(u'句尺池 ' + str(M['s_pool_n']) + u' 档 ' + u'⇎'.join(str(x) for x in M['s_pool_tier'])
      + u' ｜ 句尺对 ' + u'⇎'.join(str(x) for x in M['s_pair_share']) + u' ｜ 1123·5321 句共用 '
      + str(M['s_retry_pair_share']) + u' vs 行共用 ' + str(M['pair_share'][PAIRS.index((1, 2))])
      + u' ｜ 句尺容斥 ' + u'⇎'.join(str(x) for x in M['s_incl']) + u'→' + str(M['s_union_incl']))
print(u'年份 ' + u'⇎'.join(str(x) for x in M['years']) + u' ｜ 废止 '
      + u' ⇎ '.join(str(x) for x in M['obs_ids']) + u' ｜ 更新 '
      + u' ⇎ '.join(str(x) for x in M['upd_ids']) + u' ｜ 窗口 ' + json.dumps(M['win']))
