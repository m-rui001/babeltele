# -*- coding: utf-8 -*-
"""建条目第二遍(B74): “投递失败的邮件多久重试一次、什么时候放弃”, 交五份一手文书各答一遍
821(82) 只分类不定时——4yz/5yz 两族回复码的定义 + 自认“两个站点很难对 transient 取得一致”,
全份零 MUST 零 retry 零 queue 词汇 ⇎
1123(89) 主机要求——下限 “SHOULD be at least 30 minutes” + “give-up time … at least 4-5 days” +
“parameters MUST be configurable”, 另有一条 DNS 指数退避与 5 秒下限 ⇎
5321(08) 把同一段搬进协议标准, 术语换成 SMTP client, 并加一句 NDN 可以少试几次的 MAY 例外 ⇎
Exim(12) 不给义务词, 给阶梯规则串 F,2h,15m; G,16h,1h,1.5; F,4d,6h 与 24h 封顶 ⇎
Postfix(25 镜像) 只列参数默认: 5d/5d/300s/4000s/300s/60s 与 “0=只试一次”。

本遍与采集侧(_pick74.py, 正则字面轨 + 按行取值)换实现: 非重叠游标 ⇎ 集合代数 ⇎ 锚句由面上位置导出
⇎ 规则串按分词切 ⇎ 语气词按邻居字符手扫。五档口径: 原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平(txt) ⇎
断面(标签替空格, html) ⇎ 粘面(标签替空串, html); txt 不剥壳(其 ASCII 图里有 <尖括号> 伪标签),
html 不摘壳(无页眉), 两条口径都照抄 audit.py::_atom_face 的按扩展名分派。
所有正文数字由 V()/J()/EXPR() 注册后插值, 一枚都不手打; 键名等于所量之物。"""
import io, itertools as IT, json, re, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'821', u'1123', u'5321', u'exim', u'postfix']
NSRC = 5
ISH = [False, False, False, True, True]
PATH = [u'corpus/raw/mailRetry/rfc821.txt', u'corpus/raw/mailRetry/rfc1123.txt',
        u'corpus/raw/mailRetry/rfc5321.txt', u'corpus/raw/mailRetry/exim4_retry_spec.html',
        u'corpus/raw/mailRetry/postfix_postconf5.html']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire74.py 把这一段 ⇎ _mk74emit.py 的 SCAN2 段机械切进 audit.py::_b74_scan)


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
L = [t.split(NL) for t in T]


def pnorm(s):
    return u' '.join(s.lower().split())


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


def occ_at(s, w, i):
    """手扫边界: 命中词的左右邻居都不是字母数字才算一枚——与采集侧的负向断言正则相互独立。"""
    a = i - 1
    b = i + len(w)
    return not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())


def ub(s, w):
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        if occ_at(s, w, j):
            c += 1
        i = j + 1


# 剥壳口径照抄 audit.py(注释→空格, <br>→空格, 其余标签→fill, 再单趟 DETAG_SG 实体表)
SG = ((u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'), (u'&quot;', u'"'),
      (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'), (u'&#215;', u'x'), (u'&rarr;', u'->'),
      (u'&rsquo;', u"'"), (u'&lsquo;', u"'"), (u'&mdash;', u'-'), (u'&ndash;', u'-'), (u'&deg;', u'deg'),
      (u'&infin;', u'inf'), (u'\xa0', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
      (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->'))


def detag(s, fill):
    s = re.sub(u'(?s)<!--.*?-->', u' ', s)
    s = re.sub(u'(?i)<br\\s*/?>', u' ', s)
    s = re.sub(u'<[^>]+>', fill, s)
    for a, b in SG:
        s = s.replace(a, b)
    return s


def fold(s):
    return re.sub(u'\\s+', u' ', s).strip()


FOLD = [fold(T[i]) for i in range(NSRC)]
DS = [fold(detag(T[i], u' ')) if ISH[i] else FOLD[i] for i in range(NSRC)]
DJ = [fold(detag(T[i], u'')) if ISH[i] else FOLD[i] for i in range(NSRC)]


def is_shell_pick(x):
    """采集遍 _pick74.py 的壳谓词, 逐字照抄——只为把两遍的壳账拆开到行"""
    s = x.rstrip()
    if s == u'' or s == u'\x0c' or s.strip(u'\x0c') == u'':
        return True
    return bool(re.match(u'^.*\\[Page \\d+\\].*$', s)
                or re.match(u'^\\s*RFC ?\\d{3,4}\\s+.*((19|20)\\d\\d)\\s*$', s)
                or re.match(u'^\\s*Postel\\s+.*\\d\\d\\d\\d\\s*$', s)
                or re.match(u'^\\s*Internet Engineering Task Force\\s+\\[Page \\d+\\]\\s*$', s))


def shell_line(x):
    """本遍壳谓词: 不用整序正则, 改用“剥掉空白后看形状”的逐步判定(与采集遍同集, 但机制不同)"""
    s = x.rstrip()
    if s.strip() == u'' or s.strip(u'\x0c') == u'':
        return True
    if u'[Page ' in s and s.rstrip().endswith(u']'):
        return True
    if re.match(u'^\\s*(\\[?Page \\d+\\]?|Request for Comments:|Obsoletes:|Updates:|Replaces:|Category:|ISSN:)\\s*$', s):
        return True
    if u'RFC' in s and re.search(u'\\[(19|20)\\d\\d]\\s*$', s.rstrip()):
        return True
    toks = s.split()
    if len(toks) >= 3 and toks[-1].isdigit() and len(toks[-1]) == 4 and u'.' not in s:
        return True
    if u'Postel' in s and re.search(u'19\\d\\d\\s*$', s):
        return True
    return False


SHP = [[x for x in L[i] if not is_shell_pick(x)] for i in range(NSRC)]
SHL = [[x for x in L[i] if not shell_line(x)] for i in range(NSRC)]
SH = [fold(NL.join(SHP[i])) if not ISH[i] else FOLD[i] for i in range(NSRC)]
# 五档面: 0 原面逐行 / 1 全篇折平 / 2 摘壳折平(仅 txt) / 3 断面(仅 html) / 4 粘面(仅 html)
FACES = [L, FOLD, SH, DS, DJ]
WIDE = [DS[i] if ISH[i] else SH[i] for i in range(NSRC)]
# txt 无标签⇒断面/粘面与全篇折平同读数; html 无页壳⇒摘壳档与全篇折平同读数
assert all(DS[i] == DJ[i] == FOLD[i] for i in range(3))
assert all(SH[i] == FOLD[i] for i in range(3, NSRC))


def hit_face(k, tier):
    nd = TEXT[k]
    o = OWNER[k]
    if not nd:
        return 0
    if tier == 0:
        return len([x for x in L[o] if nd in x])
    return cnt_cur(FACES[tier][o], nd)


# ---------- 锚句: 由起止针在指定面上导出整句, 不手打 ----------
# (owner, key, 导出面, 起针, 止针; 起针以 @ 开头者为反向对照针)
SENT = [
    (0, u'a821_4yz', u'sh', u'4yz Transient Negative Completion reply', u'the action may be requested again.'),
    (0, u'a821_hard', u'sh', u'It is difficult to assign a meaning', u'must agree on the interpretation.'),
    (0, u'a821_enc', u'sh', u'Each reply in this category might have', u'encouraged to try again.'),
    (0, u'a821_thumb', u'sh', u'A rule of thumb to determine', u'in properties of the sender or receiver.'),
    (0, u'a821_5yz', u'sh', u'5yz Permanent Negative Completion reply', u'exact request (in the same sequence).'),
    (0, u'a821_human', u'sh', u'Even some', u'direct the sender-SMTP to reinitiate'),
    (0, u'n821_retry', u'sh', u'@retry', u''),
    (0, u'n821_queue', u'sh', u'@queue', u''),
    (0, u'n821_must', u'sh', u'@MUST', u''),
    (0, u'n821_cutoff', u'sh', u'@cutoff', u''),
    (0, u'n821_giveup', u'sh', u'@4-5 days', u''),
    (1, u'a1123_delay', u'sh', u'The sender MUST delay retrying a particular destination', u'at least 30 minutes'),
    (1, u'a1123_giveup', u'sh', u'Retries continue until the message is transmitted', u'MUST be configurable.'),
    (1, u'a1123_two', u'sh', u'policy of two connection attempts', u'every two or three hours.'),
    (1, u'a1123_queuing', u'sh', u'Any queueing strategy MUST include', u'in response to error messages.'),
    (1, u'a1123_dns', u'sh', u'retry interval SHOULD be constrained by an exponential', u'no less than 5 seconds should be used.'),
    (1, u'a1123_model', u'sh', u'The general model of a sender-SMTP', u'transmit outgoing mail.'),
    (1, u'n1123_client', u'sh', u'@SMTP client', u''),
    (1, u'n1123_cutoff', u'sh', u'@cutoff', u''),
    (2, u'a5321_delay', u'sh', u'The sender MUST delay retrying', u'reason for non-delivery.'),
    (2, u'a5321_giveup', u'sh', u'Retries continue until the message is transmitted', u'MUST be configurable.'),
    (2, u'a5321_queuing', u'sh', u'Any queuing strategy MUST include timeouts', u'under any circumstances.'),
    (2, u'a5321_cache', u'sh', u'5yz responses to the MAIL command MUST NOT be cached.', u''),
    (2, u'a5321_thumb', u'sh', u'A rule of thumb to determine whether a reply', u'in properties'),
    (2, u'a5321_model', u'sh', u'The general model for an SMTP client', u'transmit outgoing mail.'),
    (2, u'a5321_head', u'fold', u'4.5.4.1.', u'Sending Strategy'),
    (2, u'n5321_cutoff', u'sh', u'@cutoff', u''),
    (2, u'n5321_expo', u'sh', u'@constrained by an exponential', u''),
    (3, u'aexim_letter', u'ds', u'The letter identifies the algorithm', u'no longer applies'),
    (3, u'aexim_meas', u'ds', u'The cutoff time is measured from the time', u'not from the time the message was received.'),
    (3, u'aexim_rim', u'ds', u'retry_interval_max limits the maximum interval', u'which is its default value.'),
    (3, u'aexim_rule', u'ds', u'* * F,2h,15m; G,16h,1h,1.5; F,4d,6h', u''),
    (3, u'aexim_four', u'ds', u'the cutoff time is four days.', u'recipient address that counts.'),
    (3, u'aexim_30min', u'ds', u'They happen every 30 minutes', u'for 24 hours only.'),
    (3, u'aexim_bond_ds', u'ds', u'< letter >,< cutoff time >,< arguments >', u''),
    (3, u'aexim_bond_dj', u'dj', u'<letter>,<cutoff time>,<arguments>', u''),
    (3, u'aexim_F_ds', u'ds', u'F : retry at fixed intervals.', u'specifying the interval.'),
    (3, u'aexim_F_dj', u'dj', u'F: retry at fixed intervals.', u'the interval.'),
    (3, u'aexim_G_dj', u'dj', u'G: retry at geometrically increasing intervals.', u'at each retry.'),
    (3, u'aexim_H_dj', u'dj', u'H: retry at randomized intervals.', u'randomly between them.'),
    (3, u'aexim_exp', u'ds', u'retry_data_expire (default 7 days)', u'a retry time as if it were failing'),
    (3, u'aexim_beyond', u'ds', u'If a message has been on the queue for longer than the cutoff time', u'the address is'),
    (3, u'nexim_must', u'ds', u'@MUST', u''),
    (3, u'nexim_expo', u'ds', u'@constrained by an exponential', u''),
    (3, u'nexim_sender', u'ds', u'@sender-SMTP', u''),
    (4, u'apf_zero', u'dj', u'Specify 0 when mail delivery should be tried only once.', u''),
    (4, u'apf_minbo', u'dj', u'The minimal time between attempts to deliver a deferred message', u'destination status cache.'),
    (4, u'apf_maxbo', u'dj', u'The maximal time between attempts', u'See also $queue_run_delay.'),
    (4, u'apf_mqlb', u'dj', u'Consider a message as undeliverable', u'the maximal_queue_lifetime limit.'),
    (4, u'apf_bqlb', u'dj', u'Consider a bounce message as undeliverable', u'this limit is the same as for regular mail.'),
    (4, u'apf_qrdb', u'dj', u'The time between deferred queue scans by the queue manager', u'default value was 1000s.'),
    (4, u'apf_le', u'dj', u'set less than or equal to $minimal_backoff_time', u'See also $maximal_backoff_time.'),
    (4, u'apf_unit', u'dj', u'Time units: s (seconds), m (minutes), h (hours), d (days), w (weeks).', u''),
    (4, u'apf_units', u'dj', u'The default time unit is s (seconds).', u''),
    (4, u'apf_mal', u'dj', u'contact a malfunctioning message delivery transport', u'transport.'),
    (4, u'npf_giveup', u'dj', u'@4-5 days', u''),
    (4, u'npf_expo', u'dj', u'@constrained by an exponential', u''),
    (4, u'npf_sender', u'dj', u'@sender-SMTP', u''),
]
FACE = {u'sh': SH, u'ds': DS, u'dj': DJ, u'fold': FOLD}


def mk_nd(i, start, end, face):
    f = FACE[face][i]
    a = f.find(start)
    if a < 0:
        raise AssertionError(u'锚起针落空 %s %s' % (LBL[i], start[:40]))
    if end == u'':
        return f[a:a + len(start)]
    b = f.find(end, a)
    if b < 0:
        raise AssertionError(u'锚止针落空 %s %s' % (LBL[i], end[:40]))
    return f[a:b + len(end)]


TEXT = {}
NEG = [k for o, k, fa, s0, e0 in SENT if s0.startswith(u'@')]
for (o, k, fa, s0, e0) in SENT:
    TEXT[k] = s0[1:] if k in NEG else mk_nd(o, s0, e0, fa)
OWNER = dict((k, o) for o, k, _, _, _ in SENT)
GN = [k for o, k, _, _, _ in SENT]
LITK.update(TEXT)
SN = dict((k, [hit_face(k, n) for n in range(5)]) for k in GN)
FAI = {u'fold': 1, u'sh': 2, u'ds': 3, u'dj': 4}
for o, k, fa, s0, e0 in SENT:
    if k in NEG:
        assert max(SN[k]) == 0, (k, SN[k])
        continue
    assert TEXT[k] == u'' or TEXT[k] in FACE[fa][o], k
    assert SN[k][FAI[fa]] > 0, k
F['needle_n'] = len(GN)
F['neg_n'] = len(NEG)
TIERN = {0: u'strict', 1: u'fold', 2: u'sh', 3: u'ds', 4: u'dj'}
for n in range(5):
    F[u'sn_' + TIERN[n] + u'_docs'] = [len([k for k in GN if OWNER[k] == i and SN[k][n]]) for i in range(NSRC)]
for k in GN:
    F[u'n_' + k] = SN[k]
F['needles_owned'] = [len([k for k in GN if OWNER[k] == i]) for i in range(NSRC)]
F['fold_minus_strict_keys'] = [k for k in GN if not SN[k][0] and SN[k][1]]
F['fold_minus_strict_own'] = [len([k for k in F['fold_minus_strict_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['fold_minus_strict_n'] = len(F['fold_minus_strict_keys'])
F['sh_minus_fold'] = [F['sn_fold_docs'][i] - F['sn_sh_docs'][i] for i in range(NSRC)]
F['ds_only_keys'] = [k for k in GN if not SN[k][2] and SN[k][3]]
F['ds_only_own'] = [len([k for k in F['ds_only_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['ds_only_n'] = len(F['ds_only_keys'])
F['dj_only_keys'] = [k for k in GN if not SN[k][3] and SN[k][4]]
F['dj_only_n'] = len(F['dj_only_keys'])
F['dj_only_own'] = [len([k for k in F['dj_only_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['ds_no_dj_keys'] = [k for k in GN if SN[k][3] and not SN[k][4]]
F['ds_no_dj_own'] = [len([k for k in F['ds_no_dj_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['ds_no_dj_n'] = len(F['ds_no_dj_keys'])
F['sn_dj_minus_ds'] = [F['sn_dj_docs'][i] - F['sn_ds_docs'][i] for i in range(NSRC)]
F['dead_needles'] = [k for k in GN if k not in NEG and max(SN[k]) == 0]
F['neg_controls'] = sorted(NEG)
F['neg_own'] = [len([k for k in NEG if OWNER[k] == i]) for i in range(NSRC)]
F['neg_hit_widest'] = sum(max(SN[k]) for k in NEG)
F['neg_hit_strict'] = sum(SN[k][0] for k in NEG)
# 属性面: 括号里的默认值既写在 TOC 链接的 title 属性里, 也写在标题行里; 剥壳只留正文那一枚
F['fold_gt_ds_keys'] = [k for k in GN if ISH[OWNER[k]] and SN[k][1] > SN[k][3]]
F['attr_loss'] = [sum(SN[k][1] - SN[k][3] for k in F['fold_gt_ds_keys'] if OWNER[k] == i) for i in range(NSRC)]
F['attr_loss_n'] = sum(F['attr_loss'])
F['attr_loss_docs'] = [len([k for k in F['fold_gt_ds_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['bond_pair'] = 1 if (SN[u'aexim_bond_ds'][3] and not SN[u'aexim_bond_ds'][4]
                       and SN[u'aexim_bond_dj'][4] and not SN[u'aexim_bond_dj'][3]) else 0
F['letter_pair'] = 1 if (SN[u'aexim_F_ds'][3] and not SN[u'aexim_F_ds'][4]
                         and SN[u'aexim_F_dj'][4] and not SN[u'aexim_F_dj'][3]) else 0
F['head_pair'] = 1 if (SN[u'a5321_head'][0] and SN[u'a5321_head'][1]) else 0
F['ladder_monotone'] = 1 if all(F['sn_strict_docs'][i] + F['fold_minus_strict_own'][i]
                                == F['sn_fold_docs'][i]
                                and F['sn_sh_docs'][i] >= F['sn_fold_docs'][i]
                                and F['sn_ds_docs'][i] >= F['sn_fold_docs'][i] for i in range(NSRC)) else 0
# 判定轨也换过: 正则字面轨在五个折档面上逐档与游标轨对拍
F['re_eq_cur'] = 1 if all(len(re.findall(re.escape(TEXT[k]), FACES[n][OWNER[k]])) == SN[k][n]
                          for k in GN if TEXT[k] and k not in NEG for n in range(1, 5)) else 0
F['overlap_extra'] = sum(cnt_ovl(WIDE[OWNER[k]], TEXT[k]) - cnt_cur(WIDE[OWNER[k]], TEXT[k])
                         for k in GN if TEXT[k])
F['nd_len'] = [len(TEXT[k]) for k in GN]
F['nd_len_tot'] = sum(F['nd_len'])
F['nd_len_max'] = max(F['nd_len'])

# ---------- 结构面量 ----------
F['bytes'] = [len(b) for b in B]
F['chars'] = [len(t) for t in T]
F['lines'] = [len(L[i]) for i in range(NSRC)]
F['lines_nl'] = [cnt_cur(T[i], u'\n') + 1 for i in range(NSRC)]
F['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
F['maxlen'] = [max(len(x) for x in L[i]) for i in range(NSRC)]
F['cr'] = [cnt_cur(T[i], u'\r') for i in range(NSRC)]
F['ff'] = [cnt_cur(T[i], u'\x0c') for i in range(NSRC)]
F['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
F['ff_only'] = [len([x for x in L[i] if x.strip() == u'\x0c']) for i in range(NSRC)]
F['nonascii'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(NSRC)]
F['bom'] = [1 if b[:3] == b'\xef\xbb\xbf' else 0 for b in B]
F['txt_n'] = NSRC - sum(1 for x in ISH if x)
F['html_n'] = sum(1 for x in ISH if x)
F['nul'] = [cnt_cur(t, u'\x00') for t in T]
F['digit_chars'] = [len([c for c in t if c.isdigit()]) for t in T]
F['nonascii_extra'] = [sum(len(c.encode('utf-8')) - 1 for c in T[i] if ord(c) > 127) for i in range(NSRC)]
F['byte_cp_delta'] = [F['bytes'][i] - F['chars'][i] for i in range(NSRC)]
F['tail_nl'] = [1 if T[i].endswith(NL) else 0 for i in range(NSRC)]
F['lines_split'] = [len(T[i].splitlines()) for i in range(NSRC)]
F['lines_split_close'] = sum(F['lines_nl'][i] - F['tail_nl'][i] + F['ff'][i] - F['lines_split'][i]
                             for i in range(NSRC))

# ---------- HTML 结构: 标签按“切 < 再看首字符”数, 与采集侧的整序正则不同机制 ----------
def tag_split(t):
    op = cl = 0
    for seg in t.split(u'<')[1:]:
        if not seg:
            continue
        if seg[0] == u'/':
            cl += 1
        elif seg[0].isalpha():
            op += 1
    return op, cl


F['tag_open'] = [0] * NSRC
F['tag_close'] = [0] * NSRC
for i in range(NSRC):
    if ISH[i]:
        F['tag_open'][i], F['tag_close'][i] = tag_split(T[i])
F['tag_tot'] = [F['tag_open'][i] + F['tag_close'][i] for i in range(NSRC)]
F['comment'] = [T[i].count(u'<!--') if ISH[i] else 0 for i in range(NSRC)]
def br_split(t):
    """切 '<' 看紧跟其后的两字符: 与采集侧 <br\\s*/?> 整序正则同一件事, 机制不同"""
    return len([x for x in t.split(u'<')[1:]
                if x[:2].lower() == u'br' and x[2:3] in (u'>', u'/', u' ', u'\t')])


F['br_tag'] = [br_split(T[i]) if ISH[i] else 0 for i in range(NSRC)]
ENTFAM = [u'&lt;', u'&gt;', u'&amp;', u'&amp;amp;', u'&#34;', u'&#39;', u'&#43;', u'&#x2F;', u'&nbsp;',
          u'&mdash;', u'&rsquo;', u'&quot;']
F['ent_fam'] = ENTFAM
F['ent_raw'] = [[cnt_cur(T[i], e) for e in ENTFAM] for i in range(NSRC)]
F['ent_total'] = [sum(x) for x in F['ent_raw']]
# 第二条尺: 按 &…; 记号切出的实体 token 种数(采集侧没有这个量)
ENTOK = [Counter(re.findall(u'&[#a-zA-Z0-9]{1,10};', T[i])) if ISH[i] else Counter() for i in range(NSRC)]
F['ent_distinct'] = [len(ENTOK[i]) for i in range(NSRC)]
F['ent_all'] = [sum(ENTOK[i].values()) for i in range(NSRC)]
F['ent_top'] = [[w for w, _ in ENTOK[i].most_common(3)] for i in range(NSRC)]
F['ent_double_left'] = [cnt_cur(DS[i], u'&amp;') for i in range(NSRC)]
F['ent_numeric_left'] = [sum(cnt_cur(DS[i], e) for e in (u'&#34;', u'&#39;', u'&#43;', u'&#x2F;'))
                         for i in range(NSRC)]
F['ent_lt_left'] = [cnt_cur(DS[i], u'&lt;') for i in range(NSRC)]
F['ent_amp_raw'] = [cnt_cur(T[i], u'&amp;') for i in range(NSRC)]
F['ent_amp_eaten'] = [F['ent_amp_raw'][i] - F['ent_double_left'][i] for i in range(NSRC)]

# ---------- 页壳两遍账(逐行分解, 不比对“相等”) ----------
F['shell_pick'] = [len(L[i]) - len(SHP[i]) for i in range(NSRC)]
F['shell_n'] = [len(L[i]) - len(SHL[i]) for i in range(NSRC)]
MO = [[x for x in L[i] if shell_line(x) and not is_shell_pick(x)] for i in range(NSRC)]
PO = [[x for x in L[i] if is_shell_pick(x) and not shell_line(x)] for i in range(NSRC)]
F['shell_both'] = [F['shell_n'][i] - len(MO[i]) for i in range(NSRC)]
F['shell_mk_only'] = [len(MO[i]) for i in range(NSRC)]
F['shell_pick_only'] = [len(PO[i]) for i in range(NSRC)]
F['shell_diff'] = [F['shell_n'][i] - F['shell_pick'][i] for i in range(NSRC)]
F['shell_page'] = [len([x for x in L[i] if re.search(u'\\[Page \\d+\\]', x)]) for i in range(NSRC)]
F['shell_hdr'] = [len([x for x in L[i] if re.match(u'^\\s*RFC ?\\d{3,4}\\s+.*((19|20)\\d\\d)\\s*$', x)])
                  for i in range(NSRC)]
F['shell_blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
F['shell_mk_only_hdr'] = [len([x for x in MO[i] if re.match(u'^\\s*(Request for Comments:|Obsoletes:|Updates:|Replaces:|Category:|ISSN:|RFC ?\\d)', x)])
                          for i in range(NSRC)]
F['shell_pick_only_body'] = [len([x for x in PO[i] if re.match(u'^[ \\t]+\\S', x)]) for i in range(NSRC)]
# 两把尺不同源, 于是只要求账平: 采集数 + 本遍多判 − 采集多判 = 本遍数(逐份相加归零)
F['shell_ledger_close'] = sum(abs(F['shell_pick'][i] + F['shell_mk_only'][i]
                                  - F['shell_pick_only'][i] - F['shell_n'][i]) for i in range(NSRC))

# ---------- 序列化三式(只在逐行原面上分得出) ----------
HB = u'^\\s*\\d+(?:\\.\\d+)+'
F['hdr_dot2sp'] = [len([x for x in L[i] if re.match(HB + u'\\.  \\S', x)]) for i in range(NSRC)]
F['hdr_dot1sp'] = [len([x for x in L[i] if re.match(HB + u'\\. \\S', x)]) for i in range(NSRC)]
F['hdr_nodot'] = [len([x for x in L[i] if re.match(HB + u' \\S', x)]) for i in range(NSRC)]
# 折面上这一式子整体读不到(^\s* 失去行首), 双空格本身却还在——两档各数一遍以分清“消失的是式还是空格”
F['dblspace_in_fold'] = [cnt_cur(FOLD[i], u'  ') for i in range(NSRC)]
F['dot_dblspace_anywhere'] = [len([x for x in re.finditer(u'\\S\\.  \\S', FOLD[i])]) for i in range(NSRC)]


def ndn_break(lines):
    """折行断字: 行尾以 non- 收尾且下行以 delivery 起头(可带缩进)——逐对邻行手扫, 不写成一条正则"""
    n = 0
    for j in range(len(lines) - 1):
        if lines[j].rstrip().endswith(u'non-') and lines[j + 1].lstrip().startswith(u'delivery'):
            n += 1
    return n


F['hyphen_break'] = [len([1 for j in range(len(L[i]) - 1)
                          if L[i][j].rstrip().endswith(u'-')
                          and re.match(u'^\\s*[a-z]', L[i][j + 1])]) for i in range(NSRC)]
F['ndn_hyphen_break'] = [ndn_break(L[i]) for i in range(NSRC)]
F['ndn_unbroken'] = [cnt_cur(WIDE[i], u'non-delivery') for i in range(NSRC)]
F['ndn_broken'] = [cnt_cur(WIDE[i], u'non- delivery') for i in range(NSRC)]
F['ndn_other'] = [cnt_ovl(WIDE[i], u'non-') - (F['ndn_unbroken'][i] + F['ndn_broken'][i])
                  for i in range(NSRC)]

# ---------- 义务语气五轨(手扫邻居 ⇎ 采集侧负向断言) ----------
TONE = [u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY']
F['tone_pats'] = TONE
for j, w in enumerate(TONE):
    F[u'tone_' + w.replace(u' ', u'_')] = [ub(WIDE[i], w) for i in range(NSRC)]
F['tone'] = [[F[u'tone_' + w.replace(u' ', u'_')][i] for w in TONE] for i in range(NSRC)]
F['tone_tot'] = [sum(F['tone'][i]) for i in range(NSRC)]
F['tone_must_lc'] = [ub(WIDE[i], u'must') for i in range(NSRC)]
F['tone_zero_must'] = [1 if (F['tone'][i][0] + F['tone'][i][1]) == 0 else 0 for i in range(NSRC)]
F['tone_zero_all'] = [1 if F['tone_tot'][i] == 0 else 0 for i in range(NSRC)]
F['kw_clause'] = [len([x for x in re.finditer(u'[Kk]ey [Ww]ords', WIDE[i])]) for i in range(NSRC)]
F['c821_may_month'] = [cnt_cur(WIDE[i], u'"MAY"') for i in range(NSRC)]
F['must_bare'] = [F['tone'][i][1] - F['tone'][i][0] for i in range(NSRC)]
F['tone_ledger'] = [F['tone'][i][1] - (F['must_bare'][i] + F['tone'][i][0]) for i in range(NSRC)]
# 第二把尺: 同一批词用整序正则再数一次, 两尺之差必须逐份归零
F['tone_re_ledger'] = [[len(re.findall(u'(?<![A-Za-z0-9])' + re.escape(w) + u'(?![A-Za-z0-9])', WIDE[i]))
                        - F[u'tone_' + w.replace(u' ', u'_')][i] for w in TONE] for i in range(NSRC)]
F['tone_ruler_close'] = sum(sum(abs(x) for x in v) for v in F['tone_re_ledger'])
F['tone_per_attempt'] = [F['tone'][i][1] for i in range(NSRC)]

# ---------- 术语尺: 谁在延迟重试 ----------
TERMP = [u'sender-SMTP', u'SMTP client', u'SMTP-receiver', u'receiver-SMTP', u'queueing', u'queuing',
         u'queue', u'retry', u'retries', u'retrying']
F['term_pats'] = TERMP
F['terms'] = [[cnt_cur(WIDE[i], p) for p in TERMP] for i in range(NSRC)]
F['sender_smtp'] = [x[0] for x in F['terms']]
F['smtp_client'] = [x[1] for x in F['terms']]
F['receiver_smtp'] = [x[3] for x in F['terms']]
F['spelling_queueing'] = [x[4] for x in F['terms']]
F['spelling_queuing'] = [x[5] for x in F['terms']]
F['queue_word'] = [x[6] for x in F['terms']]
F['retry_word'] = [x[7] + x[8] + x[9] for x in F['terms']]
F['term_new_per_mille'] = [(1000 * F['smtp_client'][i]) // (F['smtp_client'][i] + F['sender_smtp'][i])
                           if (F['smtp_client'][i] + F['sender_smtp'][i]) else -1 for i in range(NSRC)]
F['c821_no_retry_vocabulary'] = 1 if (F['retry_word'][0] == 0 and F['queue_word'][0] == 0) else 0
F['word_expo'] = [cnt_cur(WIDE[i], u'exponential') for i in range(NSRC)]
F['word_geo'] = [cnt_cur(WIDE[i], u'geometric') for i in range(NSRC)]
F['word_cutoff'] = [cnt_cur(WIDE[i], u'cutoff') for i in range(NSRC)]
F['word_giveup'] = [cnt_cur(WIDE[i], u'give up') for i in range(NSRC)]
F['word_transient'] = [cnt_cur(WIDE[i], u'transient') for i in range(NSRC)]
F['word_permanent'] = [cnt_cur(WIDE[i], u'permanent') for i in range(NSRC)]
F['word_deferred'] = [cnt_cur(WIDE[i], u'deferred') for i in range(NSRC)]
F['word_timeout'] = [cnt_cur(WIDE[i], u'Timeout') + cnt_cur(WIDE[i], u'timeout') for i in range(NSRC)]

# ---------- 措辞档: 同一问题的十二族答法 ----------
TIER = {
    u'hard_define': u'difficult to assign a meaning',
    u'floor_30min': u'SHOULD be at least 30 minutes',
    u'giveup_45days': u'at least 4-5 days',
    u'configurable': u'MUST be configurable',
    u'cutoff': u'cutoff time',
    u'd5': u'(default: 5d)',
    u'300s': u'(default: 300s)',
    u'4000s': u'(default: 4000s)',
    u'60s': u'(default: 60s)',
    u'zero_once': u'tried only once',
    u'encourage': u'encouraged to try again',
    u'may_shorter': u'MAY be appropriate',
}
F['tier_words'] = list(TIER.keys())
F['tier_pats'] = list(TIER.values())
for k, w in TIER.items():
    F[u'tier_' + k] = [cnt_cur(WIDE[i], w) for i in range(NSRC)]
    F[u'tierf_' + k] = [cnt_cur(FOLD[i], w) for i in range(NSRC)]
F['tier_tot'] = [sum(F[u'tier_' + k][i] for k in TIER) for i in range(NSRC)]
F['tier_fold_tot'] = [sum(F[u'tierf_' + k][i] for k in TIER) for i in range(NSRC)]
F['tier_wide_minus_fold'] = [F['tier_tot'][i] - F['tier_fold_tot'][i] for i in range(NSRC)]
F['tier_zero_fams'] = [len([k for k in TIER if F[u'tier_' + k][i] == 0]) for i in range(NSRC)]
F['tier_hit_fams'] = [len([k for k in TIER if F[u'tier_' + k][i]]) for i in range(NSRC)]
F['time_digit_docs'] = [len(re.findall(u'\\d+\\s*(minutes?|hours?|days?|seconds?)', WIDE[i]))
                        for i in range(NSRC)]

# ---------- Exim 规则串: 按分词切(采集侧用整序 findall) ----------
UNIT = {u's': 1, u'm': 60, u'h': 3600, u'd': 86400, u'w': 604800}


def is_time(tok):
    return len(tok) > 1 and tok[:-1].isdigit() and tok[-1] in UNIT


def secs(tok):
    assert is_time(tok), tok
    return int(tok[:-1]) * UNIT[tok[-1]]


def val(tok):
    return secs(tok) if is_time(tok) else float(tok)


def is_num(tok):
    return bool(re.match(u'\\d+(\\.\\d+)?$', tok))


def parse_rule(s):
    """按分词切规则串: 逗号段以字母开头, 后续段只吃“时长或纯数字”, 遇到例句散文即停。"""
    out = []
    for grp in s.split(u';'):
        toks = [x.strip() for x in grp.split(u',') if x.strip()]
        if toks and toks[0] not in (u'F', u'G', u'H', u'P'):
            # 规则字母可以跟在地址段(* * F)或例句散文之后
            w = toks[0].split()
            if w and w[-1] in (u'F', u'G', u'H', u'P'):
                toks[0] = w[-1]
        if not toks or toks[0] not in (u'F', u'G', u'H', u'P'):
            continue
        args = []
        for t in toks[1:]:
            if not (is_time(t) or is_num(t)):
                break
            args.append(t)
        if len(args) < 2:
            continue
        out.append((toks[0], secs(args[0]), args[1:], [val(x) for x in args[1:]]))
    return out


DL3 = [detag(x, u'') for x in L[3]]
# 默认规则串不手打: 由 “using the default retry rule:” 这句之后第一份以地址段 * 开头的行现取
_p = [n for n, x in enumerate(DL3) if re.search(u'default retry rule', x, re.I)]
DEF_RULE = u''
DEF_ALT = []
for n in _p:
    for m in range(n + 1, min(n + 9, len(DL3))):
        s = DL3[m].strip()
        if re.match(u'^\\* \\* [FGPH],', s) and u',' in s:
            DEF_RULE = DEF_RULE or s
            break
for n, x in enumerate(DL3):
    s = u' '.join(x.split())
    if re.match(u'^\\* \\* [FGPH],', s):
        DEF_ALT.append(s)
assert DEF_RULE, u'B74: 默认规则串没在面上读到'
F['ex_def_rule'] = DEF_RULE
F['ex_star_star_rules'] = len(DEF_ALT)
F['ex_star_star_distinct'] = len(set(DEF_ALT))
F['ex_def_rule_prompt'] = len(_p)
_d = parse_rule(DEF_RULE)
F['ex_def_sets'] = len(_d)
F['ex_def_letters'] = sorted(set(x[0] for x in _d))
F['ex_def_cutoffs'] = [x[1] for x in _d]
F['ex_def_first'] = [x[3][0] for x in _d]
F['ex_def_mults'] = [float(x[2][1]) for x in _d if x[0] == u'G']
F['ex_def_args'] = [len(x[2]) for x in _d]
F['ex_def_span'] = F['ex_def_cutoffs'][-1]
# 规则串全集: 在“逐行粘面”上按 “字母,时长” 的行扫出所有规则串, 再逐串分词
RL = [x for x in DL3 if re.search(u'[FGPH],\\d+\\w', x)]
RS = []
for x in RL:
    RS.extend(parse_rule(x.strip()))
F['ex_rule_lines'] = len(RL)
F['ex_sets_n'] = len(RS)
F['ex_letters'] = sorted(set(x[0] for x in RS))
F['ex_cutoff_sec'] = sorted(set(x[1] for x in RS))
F['ex_first_sec'] = sorted(set(x[3][0] for x in RS))
F['ex_mults'] = sorted(set(float(x[2][1]) for x in RS if x[0] == u'G' and len(x[2]) > 1))
# 字母定义: 文档里 “字母: retry at …” 的每一行
LET = sorted(set(x[0] for x in re.findall(u'([FGPH]): retry at', DJ[3])))
F['ex_letters_def'] = LET
F['ex_letters_used_only'] = sorted(set(F['ex_letters']) - set(LET))
F['ex_letters_def_only'] = sorted(set(LET) - set(F['ex_letters']))
F['ex_rim_cap'] = secs(u'24h')
F['ex_rim_default_line'] = cnt_cur(DJ[3], u'24h, which is its default value')
F['ex_expire_days'] = secs(u'7d')
# 按默认规则串现算的档数: F 档=间隔整数倍, G 档=逐次乘倍数直到越过 cutoff
F['ex_f1_attempts'] = F['ex_def_cutoffs'][0] // F['ex_def_first'][0]
F['ex_f3_attempts'] = F['ex_def_cutoffs'][2] // F['ex_def_first'][2]
_g = []
_t = 0.0
_i = float(F['ex_def_first'][1])
while _t < F['ex_def_cutoffs'][1] and len(_g) < 40:
    _g.append(int(_i))
    _t += _i
    _i *= F['ex_def_mults'][0]
F['ex_g_steps'] = len(_g)
F['ex_g_step_sec'] = _g
F['ex_g_total'] = sum(_g)
F['ex_attempts_tot'] = F['ex_f1_attempts'] + F['ex_g_steps'] + F['ex_f3_attempts']
F['ex_sched_sec'] = F['ex_def_cutoffs']

# ---------- Postfix 参数默认: 在粘面上按 “ (default: ” 记号游标切 ----------
PARAM6 = [u'maximal_queue_lifetime', u'bounce_queue_lifetime', u'minimal_backoff_time',
          u'maximal_backoff_time', u'queue_run_delay', u'transport_retry_time']
F['pf_params'] = PARAM6


def pf_defs(face):
    out = []
    for p in PARAM6:
        got = []
        i = 0
        while True:
            j = face.find(p + u' (default: ', i)
            if j < 0:
                break
            k = face.find(u')', j)
            got.append(face[j + len(p) + 11:k])
            i = j + 1
        out.append(got)
    return out


F['pf_defs_dj'] = pf_defs(DJ[4])
F['pf_defs_fold'] = pf_defs(FOLD[4])
F['pf_body_hit'] = [len(x) for x in F['pf_defs_dj']]
F['pf_fold_hit'] = [len(x) for x in F['pf_defs_fold']]
F['pf_attr_only'] = [F['pf_fold_hit'][n] - F['pf_body_hit'][n] for n in range(len(PARAM6))]
F['pf_attr_docs_n'] = len([n for n in range(len(PARAM6)) if F['pf_attr_only'][n]])


def in_tag(s, needle):
    """另起一把尺: 只在 <…> 标签区间内数针——属性值里的文字会被剥标签一起吃掉"""
    n, i = 0, 0
    while True:
        a = s.find(u'<', i)
        if a < 0:
            return n
        b = s.find(u'>', a)
        if b < 0:
            return n
        n += cnt_cur(s[a:b + 1], needle)
        i = b + 1


F['pf_default_in_tag'] = sum(in_tag(FOLD[4], p + u' (default: ') for p in PARAM6)
# 整页尺: 目录把每一个参数的默认值都印在 title 属性里, 剥标签丢的串应当正好等于标签区间里的串
F['pf_nd_default_all'] = cnt_cur(FOLD[4], u' (default: ')
F['pf_nd_default_tag'] = in_tag(FOLD[4], u' (default: ')
F['pf_nd_default_dj'] = cnt_cur(DJ[4], u' (default: ')
F['pf_value_in_fold'] = sum(1 for n in range(len(PARAM6))
                            for v in F['pf_defs_dj'][n] if v in F['pf_defs_fold'][n])
F['pf_def_tok'] = [x[0] for x in F['pf_defs_dj']]
F['pf_def_sec'] = [secs(x[0]) for x in F['pf_defs_dj']]
F['pf_zero_once'] = cnt_cur(DJ[4], u'Specify 0 when mail delivery should be tried only once')
F['pf_unit_line'] = cnt_cur(DJ[4], u'Time units: s (seconds), m (minutes), h (hours), d (days), w (weeks).')
F['pf_unit_s'] = cnt_cur(DJ[4], u'The default time unit is s (seconds).')
F['pf_unit_d'] = cnt_cur(DJ[4], u'The default time unit is d (days).')
F['pf_unit_h'] = cnt_cur(DJ[4], u'The default time unit is h (hours).')
F['pf_le_qrd'] = cnt_cur(DJ[4], u'set less than or equal to $minimal_backoff_time')
F['pf_ge_minbo'] = cnt_cur(DJ[4], u'greater than or equal to $minimal_backoff_time')
F['pf_ge_qrd'] = cnt_cur(DJ[4], u'greater than or equal to $queue_run_delay')
F['pf_prior_1000s'] = cnt_cur(DJ[4], u'prior to Postfix 2.4 the default value was 1000s')
F['pf_5d'] = cnt_cur(DJ[4], u'(default: 5d)')

# ---------- 跨源时长换算(全部由上面的现读数导出) ----------
CVN = [u'1123/5321 下限 30 分钟', u'exim 首档间隔 15m', u'exim 次档起始 1h',
       u'postfix minimal_backoff_time', u'postfix queue_run_delay', u'postfix transport_retry_time',
       u'postfix maximal_backoff_time', u'exim retry_interval_max 封顶', u'exim 默认末档跨度',
       u'postfix 队列寿命默认']
FLOOR = 1800
CVV = [FLOOR, secs(u'15m'), secs(u'1h'), F['pf_def_sec'][2], F['pf_def_sec'][4], F['pf_def_sec'][5],
       F['pf_def_sec'][3], F['ex_rim_cap'], F['ex_def_span'], F['pf_def_sec'][0]]
F['cv_names'] = CVN
F['cv_sec'] = CVV
F['cv_floor'] = FLOOR
F['cv_below_n'] = len([v for v in CVV if v < FLOOR])
F['cv_above_n'] = len([v for v in CVV if v >= FLOOR])
F['cv_close'] = F['cv_below_n'] + F['cv_above_n'] - len(CVV)
F['cv_below'] = sorted([CVV[n] for n in range(len(CVV)) if CVV[n] < FLOOR])
F['band_lo'] = 4 * 86400
F['band_hi'] = 5 * 86400
F['cv_floor_in_band'] = 0
F['ex_cutoff_in_band'] = 1 if F['band_lo'] <= F['ex_def_span'] <= F['band_hi'] else 0
F['pf_life_in_band'] = 1 if F['band_lo'] <= F['pf_def_sec'][0] <= F['band_hi'] else 0
F['pf_bql_same_mql'] = 1 if F['pf_def_sec'][0] == F['pf_def_sec'][1] else 0
F['band_edge_hits'] = len([v for v in (F['ex_def_span'], F['pf_def_sec'][0]) if v in (F['band_lo'], F['band_hi'])])
F['pf_chain'] = [1 if F['pf_def_sec'][3] >= F['pf_def_sec'][2] else 0,
                 1 if F['pf_def_sec'][2] >= F['pf_def_sec'][4] else 0]
F['cv_ratio_exim_vs_floor'] = F['ex_def_first'][0] * 1000 // FLOOR
F['cv_ratio_pf_vs_floor'] = F['pf_def_sec'][2] * 1000 // FLOOR
F['cv_floor_minus_exim'] = FLOOR - F['ex_def_first'][0]
F['cv_floor_minus_pf'] = FLOOR - F['pf_def_sec'][2]
F['cv_pf_x_by_floor'] = F['pf_def_sec'][2] and FLOOR // F['pf_def_sec'][2] or 0
F['cv_exim_x_by_floor'] = FLOOR // F['ex_def_first'][0]
F['day_sec'] = 86400

# ---------- 出处头 / 年份 / 引用写法 ----------
def hdr_field(lines, field):
    for x in lines:
        if x.startswith(field + u':'):
            return x
    return u''


F['obs_line'] = [hdr_field(L[i], u'Obsoletes') for i in range(NSRC)]
F['upd_line'] = [hdr_field(L[i], u'Updates') for i in range(NSRC)]
F['repl_line'] = [hdr_field(L[i], u'Replaces') for i in range(NSRC)]
F['obs_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{3,4}', F['obs_line'][i].split(u'  ')[0])))
                for i in range(NSRC)]
F['upd_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{3,4}', F['upd_line'][i]))) for i in range(NSRC)]
F['repl_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{3,4}', F['repl_line'][i].split(u'  ')[0])))
                 for i in range(NSRC)]
F['obs_n'] = [len(x) for x in F['obs_ids']]
F['upd_n'] = [len(x) for x in F['upd_ids']]
F['repl_n'] = [len(x) for x in F['repl_ids']]
F['target_ids'] = sorted(set().union(*[set(x) for x in F['obs_ids'] + F['upd_ids'] + F['repl_ids']]))
F['target_n'] = len(F['target_ids'])
F['rfc_hdr'] = [(re.findall(u'^Request for Comments: ?(\\d+)', NL.join(L[i][:20]), re.M) or [None])[0]
                for i in range(NSRC)]
MON = u'January|February|March|April|May|June|July|August|September|October|November|December'
RYR = re.compile(u'(%s) +(\\d{4})' % MON)


def hdr_year(lines):
    for x in lines[:90]:
        m = RYR.search(x.strip())
        if m:
            return (int(m.group(2)), m.group(1))
    return (None, None)


YR = [hdr_year(L[i]) for i in range(NSRC)]
F['years_txt'] = [y for y, _ in YR]
F['months_txt'] = [mo for _, mo in YR]
F['year_copyright'] = [int(x) for x in re.findall(u'Copyright ©\\d{4}-(\\d{4})', T[3])]
F['year_stamp'] = [x for x in re.findall(u'\\d{4}-\\d{2}-\\d{2}T', T[4])]
F['year_stamp_n'] = len(F['year_stamp'])
F['year_stamp_first'] = F['year_stamp'][0][:4] if F['year_stamp'] else None
F['year_stamp_last'] = F['year_stamp'][-1][:4] if F['year_stamp'] else None
F['years'] = [None] * NSRC
for i in range(3):
    F['years'][i] = YR[i][0]
F['years'][3] = F['year_copyright'][0] if F['year_copyright'] else None
# 镜像页面上的时间戳有两枚(生成期 ⇎ 页脚), 取页脚那枚=最新的一次序列化
F['years'][4] = int(F['year_stamp'][-1][:4]) if F['year_stamp'] else None
F['year_gaps'] = [F['years'][i + 1] - F['years'][i] for i in range(NSRC - 1)]
F['year_span'] = F['years'][-1] - F['years'][0]
F['year_inversions'] = len([1 for a in range(NSRC) for b in range(a + 1, NSRC) if F['years'][a] > F['years'][b]])
F['year_close'] = sum(F['year_gaps']) - F['year_span']
CITEN = [u'821', u'1123', u'2821', u'5321', u'788', u'780', u'772', u'1982', u'2008']
CITE = {}
for n in CITEN:
    CITE['sp_' + n] = [cnt_cur(T[i], u'RFC ' + n) for i in range(NSRC)]
    CITE['tk_' + n] = [cnt_cur(T[i], u'RFC' + n) for i in range(NSRC)]
    CITE['hy_' + n] = [cnt_cur(T[i], u'RFC-' + n) for i in range(NSRC)]
    CITE['2f_' + n] = [CITE['sp_' + n][i] + CITE['tk_' + n][i] for i in range(NSRC)]
    CITE['3f_' + n] = [CITE['2f_' + n][i] + CITE['hy_' + n][i] for i in range(NSRC)]
for k in CITE:
    F['cite_' + k] = CITE[k]
# 自引: 三份 RFC 的面上数自己的号; 两份 MTA 文档不是 RFC, 没有“自号”可引, 记 0 并注明口径
F['cite_self'] = [CITE['2f_' + LBL[i]][i] if i < 3 else 0 for i in range(NSRC)]
F['cite_forms_close'] = [len(re.findall(u'RFC[- ]?%s\\b' % LBL[i], T[i])) - CITE['3f_' + LBL[i]][i]
                        if i < 3 else 0 for i in range(NSRC)]
F['cite_821_in_5321'] = CITE['2f_821'][2]
F['cite_1123_in_5321'] = CITE['2f_1123'][2]
F['cite_821_in_1123'] = CITE['2f_821'][1]
F['cite_821_hy_in_1123'] = CITE['hy_821'][1]
F['cite_821_3f_in_1123'] = CITE['3f_821'][1]
F['cite_2821_tot'] = sum(CITE['2f_2821'])
F['cite_rfc_word'] = [len(re.findall(u'RFC ?\\d', T[i])) for i in range(NSRC)]

# ---------- 共用长行池(第一把尺: 行) ----------
def pool_lines(i):
    return [x for x in SHP[i] if len(pnorm(x)) >= 40]


POOLC = [Counter(pnorm(x) for x in pool_lines(i)) for i in range(NSRC)]
NPOOL = [set(POOLC[i]) for i in range(NSRC)]
pool_all = set().union(*NPOOL)
tier2 = [0] * NSRC
pres = {}
for a in pool_all:
    ds = tuple(i for i in range(NSRC) if a in NPOOL[i])
    pres[a] = ds
    tier2[len(ds) - 1] += 1
F['pool_n'] = len(pool_all)
F['pool_tier'] = tier2
F['pool_tier_close'] = sum(tier2) - len(pool_all)
F['pool_1'] = tier2[0]
F['pool_2'] = tier2[1]
F['pool_3'] = tier2[2]
PAIRS = [(a, b) for a, b in IT.combinations(range(NSRC), 2)]
pair_share, pair_byte, pair_norm_only = [], [], []
for i, j in PAIRS:
    inter = NPOOL[i] & NPOOL[j]
    bo = sum(1 for s in inter if any(pnorm(x) == s and x in SHP[j] for x in pool_lines(i)))
    pair_share.append(len(inter))
    pair_byte.append(bo)
    pair_norm_only.append(len(inter) - bo)
F['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
F['pair_share'] = pair_share
F['pair_byte'] = pair_byte
F['pair_norm_only'] = pair_norm_only
F['pair_nonzero'] = len([x for x in pair_share if x])
F['pair_zero'] = len(PAIRS) - F['pair_nonzero']
F['pair_close'] = sum(pair_share) - sum(pair_byte) - sum(pair_norm_only)
mx = max(pair_share)
F['pair_max'] = mx
F['pair_max_idx'] = pair_share.index(mx)
F['pair_max_byte'] = pair_byte[F['pair_max_idx']]
F['pair_max_norm_only'] = pair_norm_only[F['pair_max_idx']]
F['pair_max_lbl'] = F['pair_lbl'][F['pair_max_idx']]
F['retry_pair_idx'] = PAIRS.index((1, 2))
F['pair_1123_5321'] = pair_share[F['retry_pair_idx']]
F['pair_821_5321'] = pair_share[PAIRS.index((0, 2))]
_t1 = sum(len(v) for v in pres.values())
_t2 = sum(len(v) * (len(v) - 1) // 2 for v in pres.values())
_t3 = sum(len(v) * (len(v) - 1) * (len(v) - 2) // 6 for v in pres.values())
_t4 = sum(len(v) * (len(v) - 1) * (len(v) - 2) * (len(v) - 3) // 24 for v in pres.values())
_t5 = len([v for v in pres.values() if len(v) == 5])
F['pool_incl'] = [_t1, _t2, _t3, _t4, _t5]
F['union_incl'] = _t1 - _t2 + _t3 - _t4 + _t5
F['union_close'] = F['pool_n'] - F['union_incl']
F['pool_html_own'] = len([a for a, v in pres.items() if 3 in v or 4 in v])
F['pool_html_shared'] = len([a for a, v in pres.items() if (3 in v or 4 in v) and len(v) >= 2])
F['pool_txt_shared'] = len([a for a, v in pres.items() if len(v) >= 2])
F['shared_norm_only'] = sum(pair_norm_only)
# 写法分家轴: 归一相同 ⇎ 逐字节不同 ⇒ 按“差在哪”归最弱一档(case > hyph > space > multi)
# 采集侧用三条正则做比较, 本遍用手写字符扫描脱去连字符与首尾空白, 定义同、机制不同
RANK = {u'case': 0, u'hyph': 1, u'space': 2, u'multi': 3}


def dehyph(s):
    out = []
    j = 0
    while j < len(s):
        if s[j] == u'-':
            j += 1
            while j < len(s) and s[j] in u' \t':
                j += 1
            continue
        out.append(s[j])
        j += 1
    return u''.join(out).lower()


def bucket(o, p):
    if o.lower() == p.lower():
        return u'case'
    if dehyph(o) == dehyph(p):
        return u'hyph'
    if o.strip() == p.strip():
        return u'space'
    return u'multi'


axis = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
cand = []
for a, v in pres.items():
    if len(v) < 2:
        continue
    var = dict((i, set(x for x in pool_lines(i) if pnorm(x) == a)) for i in v)
    dif = [(o, p) for i, j in IT.combinations(v, 2) for o in var[i] for p in var[j] if o != p]
    if not dif:
        continue
    cand.append(a)
    axis[min((bucket(o, p) for o, p in dif), key=lambda w: RANK[w])] += 1
F['axis_counts'] = axis
F['axis_total'] = sum(axis.values())
F['norm_only_set'] = len(cand)
F['axis_close'] = F['axis_total'] - F['norm_only_set']
F['axis_str'] = u' ⇎ '.join(u'%s%d' % (a, axis[a]) for a in (u'case', u'hyph', u'space', u'multi'))
F['axis_str_n'] = len([a for a in (u'case', u'hyph', u'space', u'multi') if axis[a]])

# ---------- 第二把尺: 句级原子(1123 与 5321 把同一段重排过行宽) ----------
def sents(face):
    return [u' '.join(x.lower().split()) for x in
            re.split(u'(?<=[.!?])\\s+(?=[A-Z0-9*<])', face)]


SP = [set(x for x in sents(WIDE[i]) if len(x) >= 40) for i in range(NSRC)]
SPRES = dict((a, tuple(i for i in range(NSRC) if a in SP[i])) for s in SP for a in s)
F['s_pool_n'] = len(SPRES)
F['s_pool_tier'] = [len([a for a, v in SPRES.items() if len(v) == k]) for k in range(1, NSRC + 1)]
F['s_pool_tier_close'] = sum(F['s_pool_tier']) - F['s_pool_n']
F['s_pair_share'] = [len(SP[a] & SP[b]) for a, b in PAIRS]
F['s_pair_max'] = max(F['s_pair_share'])
F['s_pair_max_idx'] = F['s_pair_share'].index(F['s_pair_max'])
F['s_pair_max_lbl'] = F['pair_lbl'][F['s_pair_max_idx']]
F['s_pair_1123_5321'] = F['s_pair_share'][F['retry_pair_idx']]
F['s_pair_821_5321'] = F['s_pair_share'][PAIRS.index((0, 2))]
F['s_ruler_gain_1123_5321'] = F['s_pair_1123_5321'] - F['pair_1123_5321']
F['s_ruler_gain_821_5321'] = F['s_pair_821_5321'] - F['pair_821_5321']
F['s_pair_html'] = len([n for n, (a, b) in enumerate(PAIRS) if (a >= 3 or b >= 3) and F['s_pair_share'][n]])
_s1 = sum(len(SP[i]) for i in range(NSRC))
_s2 = sum(len(v) * (len(v) - 1) // 2 for v in SPRES.values())
_s3 = sum(len(v) * (len(v) - 1) * (len(v) - 2) // 6 for v in SPRES.values())
_s4 = sum(len(v) * (len(v) - 1) * (len(v) - 2) * (len(v) - 3) // 24 for v in SPRES.values())
_s5 = len([v for v in SPRES.values() if len(v) == 5])
F['s_incl'] = [_s1, _s2, _s3, _s4, _s5]
F['s_union_incl'] = _s1 - _s2 + _s3 - _s4 + _s5
F['s_union_close'] = F['s_pool_n'] - F['s_union_incl']

# ---------- 锚候选池 ----------
apool = []
for i in range(NSRC):
    for x in SHP[i]:
        if len(pnorm(x)) >= 24 and re.search(u'[A-Za-z]', x):
            apool.append((pnorm(x), i))
AP = defaultdict(set)
for a, i in apool:
    AP[a].add(i)
F['apool_n'] = len(AP)
F['apool_raw_n'] = len(apool)
F['apool_face_raw'] = [len([1 for a, k in apool if k == i]) for i in range(NSRC)]
F['apool_tag_n'] = [len([a for a, v in AP.items() if i in v]) for i in range(NSRC)]
F['apool_dup'] = [F['apool_face_raw'][i] - F['apool_tag_n'][i] for i in range(NSRC)]
F['apool_tag_close'] = sum(F['apool_tag_n']) + sum(F['apool_dup']) - F['apool_raw_n']
F['apool_tier'] = [len([a for a, v in AP.items() if len(v) == n]) for n in range(1, NSRC + 1)]
F['apool_weight'] = sum(F['apool_tier'][n] * (n + 1) for n in range(NSRC))
F['apool_pairs'] = sum(F['apool_tag_n'])
F['apool_tier_close'] = F['apool_weight'] - F['apool_pairs']
F['apool_maxlen'] = max(len(a) for a in AP)

# ---------- ZID: 标量恒等式(全部由上面的现读数导出) ----------
CLOSE = {}
CLOSE[u'dead_needles_none'] = 0 if len(F['dead_needles']) else 1
CLOSE[u'neg_all_cold'] = 0 if (F['neg_hit_widest'] or F['neg_n'] != len(F['neg_controls'])) else 1
CLOSE[u'bond_pair'] = F['bond_pair']
CLOSE[u'letter_pair'] = F['letter_pair']
CLOSE[u'head_pair'] = F['head_pair']
CLOSE[u'no_needle_lost_by_detag'] = 0 if F['attr_loss_n'] else 1
CLOSE[u'ds_only_exim_only'] = 1 if (F['ds_only_own'][3] and F['ds_only_own'][4]
                                    and sum(F['ds_only_own'][:3]) == 0) else 0
CLOSE[u'no_retry_vocab_821'] = F['c821_no_retry_vocabulary']
CLOSE[u'tone_zero_must_pair'] = 1 if (F['tone_zero_must'][0] and F['tone_zero_must'][3]
                                     and F['tone_zero_must'][1] + F['tone_zero_must'][2]
                                     + F['tone_zero_must'][4] == 0) else 0
CLOSE[u'exim_no_tone'] = 1 if F['tone_zero_all'][3] and sum(F['tone_zero_all'][:3] + F['tone_zero_all'][4:]) == 0 else 0
CLOSE[u'tier_821_only_hard'] = 1 if (F['tier_hard_define'][0] and sum(F['tier_hard_define'][1:]) == 0) else 0
CLOSE[u'cutoff_exim_only'] = 1 if (F['word_cutoff'][3] and sum(F['word_cutoff'][:3] + F['word_cutoff'][4:]) == 0) else 0
CLOSE[u'client_only_5321_pf'] = 1 if (F['smtp_client'][2] and F['smtp_client'][4]
                                      and F['smtp_client'][0] + F['smtp_client'][1] + F['smtp_client'][3] == 0) else 0
CLOSE[u'ex_cutoff_in_band'] = F['ex_cutoff_in_band']
CLOSE[u'pf_life_in_band'] = F['pf_life_in_band']
CLOSE[u'pf_bql_eq_mql'] = F['pf_bql_same_mql']
CLOSE[u'pf_chain_up'] = 1 if min(F['pf_chain']) == 1 else 0
CLOSE[u'below_floor_four'] = 1 if F['cv_below_n'] == 4 else 0
CLOSE[u'cite_hy_only_1123'] = 1 if (F['cite_821_in_1123'] == 0 and F['cite_821_hy_in_1123'] > 0) else 0
CLOSE[u'obs_5321_line'] = 1 if F['obs_ids'][2] == [2821] and F['upd_ids'][2] == [1123] else 0
CLOSE[u'repl_821_only'] = 1 if (F['repl_n'][0] == 3 and sum(F['repl_n'][1:]) == 0) else 0
CLOSE[u'year_monotone'] = 0 if F['year_inversions'] else 1
CLOSE[u'letters_def_three_used_two'] = 1 if (F['ex_letters_def'] == [u'F', u'G', u'H']
                                            and F['ex_letters'] == [u'F', u'G']) else 0
CLOSE[u'html_shell_none'] = 0 if (F['shell_pick'][3] or F['shell_pick'][4]) else 1
CLOSE[u'txt_no_tag'] = 0 if sum(F['tag_open'][:3]) else 1
CLOSE[u'split_tail_close'] = 0 if (F['lines_split_close'] or sum(F['tail_nl']) != NSRC) else 1
for k in CLOSE:
    F[k] = CLOSE[k]

ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"F['ladder_monotone'] - 1", u'五档单调: 逐行档+折行独有档=折平档, 摘壳档与断面档都≥折平档')
Z(u"F['re_eq_cur'] - 1", u'正则字面轨与非重叠游标轨在最宽档上逐枚相等')
Z(u"F['overlap_extra']", u'重叠口径减非重叠口径在全库锚句上合计为零')
Z(u"len(F['dead_needles'])", u'死集为空: 每枚内容锚句都在某一档读得到')
Z(u"sum(F['neg_own']) - F['neg_n']", u'反向对照针按份分账=总数')
Z(u"F['neg_hit_strict']", u'反向针在最窄档也零命中')
Z(u"sum(F['fold_minus_strict_own']) - F['fold_minus_strict_n']", u'折行独有针按份分账=总数')
Z(u"sum(F['sh_minus_fold'])", u'摘壳档一枚不丢(txt 的答句不在壳行里)')
Z(u"F['ds_only_n'] - sum(F['ds_only_own'])", u'剥壳独有针按份分账=总数')
Z(u"F['ds_only_n'] - len(F['ds_only_keys'])", u'剥壳独有针清单与计数同枚')
Z(u"F['dj_only_n'] - len(F['dj_only_keys'])", u'粘面独有针清单与计数同枚')
Z(u"sum(F['dj_only_own']) - F['dj_only_n']", u'粘面独有针按份分账=总数')
Z(u"F['sn_dj_docs'][3] - F['sn_ds_docs'][3] - F['dj_only_own'][3] + F['ds_no_dj_own'][3]",
  u'Exim 两档换尺的进出账: 粘面比断面多读的枚数=新读到的针−换一种粘法后丢的针')
Z(u"F['sn_dj_docs'][4] - F['sn_ds_docs'][4] - F['dj_only_own'][4] + F['ds_no_dj_own'][4]",
  u'Postfix 同一本换尺账')
Z(u"F['dj_only_own'][0] + F['dj_only_own'][1] + F['dj_only_own'][2]",
  u'三份 RFC 的剥壳两档恒等(不剥壳), 粘面独有针一枚也不落在它们名下')
Z(u"F['bond_pair'] - 1", u'同一处尖括号序列化: 断面带空格、粘面不带, 两枚针各只在自己的档读得到')
Z(u"F['letter_pair'] - 1", u'算法字母“F : / F:”同一处两档各一枚')
Z(u"F['attr_loss_n'] - F['attr_loss'][4]",
  u'针级的剥标签损失为零(丢的是 Postfix 的默认值条目, 不是锚句)')
Z(u"sum(F['tone_ledger'])", u'大写 MUST 总数 = 裸 MUST + MUST NOT, 五份归零相加')
Z(u"F['tone_ruler_close']", u'手扫邻居尺与负向断言正则尺在五轨上逐份逐轨同值')
Z(u"F['tone_zero_must'][0] + F['tone_zero_must'][3] - 2", u'MUST 族零枚的恰是 821 与 Exim 两份')
Z(u"F['c821_no_retry_vocabulary'] - 1", u'821 面上零枚 retry 与零枚 queue: 这一份还没有重试词汇')
Z(u"sum(F['spelling_queueing']) - F['spelling_queueing'][1]",
  u'queueing 这种拼法只在 1123 名下')
Z(u"F['spelling_queuing'][0] + F['spelling_queuing'][1] + F['spelling_queuing'][3]",
  u'queuing 这种拼法不在 821/1123/Exim 名下(5321 与 Postfix 各数)')
Z(u"F['retry_word'][0]", u'retry 三形在 821 合计零枚')
Z(u"F['word_cutoff'][0] + F['word_cutoff'][1] + F['word_cutoff'][2] + F['word_cutoff'][4]",
  u'cutoff 一词只在 Exim 出现')
Z(u"F['ex_def_sets'] - 3", u'Exim 默认规则串恰三段')
Z(u"F['ex_def_args'][0] + F['ex_def_args'][2] - 2", u'F 段各带一枚参数, 两段共两枚')
Z(u"F['ex_def_args'][1] - 2", u'G 段带两枚参数(起始间隔与倍数)')
Z(u"F['ex_attempts_tot'] - (F['ex_f1_attempts'] + F['ex_g_steps'] + F['ex_f3_attempts'])",
  u'按规则串现算的档数=三段之和')
Z(u"F['ex_f1_attempts'] * F['ex_def_first'][0] - F['ex_def_cutoffs'][0]", u'首段: 档数×间隔=该段跨度')
Z(u"F['ex_f3_attempts'] * F['ex_def_first'][2] - F['ex_def_cutoffs'][2]", u'末段: 档数×间隔=四天跨度')
Z(u"F['ex_g_step_sec'][0] - F['ex_def_first'][1]", u'G 段首档就是它的起始间隔')
Z(u"len(F['ex_letters_def']) - 3", u'文档定义了 F/G/H 三种字母')
Z(u"len(F['ex_letters']) - 2", u'规则串里只用两枚字母')
Z(u"len(F['ex_letters_def_only']) - 1", u'定义了却一次没用: 恰一枚(H)')
Z(u"len(F['ex_letters_used_only'])", u'规则串里没有用了却未定义的字母')
Z(u"F['ex_rim_cap'] - 86400", u'retry_interval_max 封顶 24h=86400 秒')
Z(u"F['ex_def_span'] - F['band_lo']", u'Exim 默认末档跨度恰是四天=4×86400')
Z(u"F['pf_def_sec'][0] - F['band_hi']", u'Postfix 队列寿命默认恰是五天=5×86400')
Z(u"F['pf_def_sec'][0] - F['pf_def_sec'][1]", u'bounce_queue_lifetime 与 maximal_queue_lifetime 默认同值')
Z(u"F['pf_def_sec'][2] - F['pf_def_sec'][4]", u'minimal_backoff_time 与 queue_run_delay 默认同值 300s')
Z(u"len([n for n in range(len(F['pf_attr_only'])) if F['pf_attr_only'][n]]) - F['pf_attr_docs_n']",
  u'丢枚数的参数个数=六枚参数全都在目录属性里多印一遍')
Z(u"sum(F['pf_attr_only']) - F['pf_default_in_tag']",
  u'“折平−剥后”每参数丢的一枚, 逐枚都能在 <…> 标签区间里找到出处')
Z(u"F['pf_nd_default_all'] - F['pf_nd_default_tag'] - F['pf_nd_default_dj']",
  u'整页加法: 折平面上的 “ (default: ” 全枚数 = 标签区间内枚数 + 剥标签后剩余枚数')
Z(u"sum(F['pf_body_hit']) - len(F['pf_body_hit']) * F['pf_body_hit'][0]",
  u'六参数在剥后面上各读到同样的枚数(两枚默认值: 目录条目 ⇎ 正文条目)')
Z(u"F['pf_value_in_fold'] - sum(F['pf_body_hit'])",
  u'剥后面上读出的每一枚默认值, 在折平面上同名参数里都读得到(少的只是条目数, 不是值)')
Z(u"F['pf_zero_once'] - 2", u'Postfix 面上“0=只试一次”这句话印了两遍(mql ⇎ bql 各一)')
Z(u"F['cv_close']", u'低于/不低于 30 分钟下限的档位相加=换算表条目数')
Z(u"F['cv_below_n'] - 4", u'低于下限的四档: Exim 首档 15m ⇎ Postfix 的 300s 两枚与 60s 一枚')
Z(u"F['cv_floor'] - 1800", u'下限 30 分钟=1800 秒由 60 现乘')
Z(u"F['cv_floor_minus_exim'] - 900", u'下限减 Exim 首档间隔=900 秒')
Z(u"F['cv_floor_minus_pf'] - 1500", u'下限减 Postfix 300s=1500 秒')
Z(u"F['cv_pf_x_by_floor'] * F['pf_def_sec'][2] - F['cv_floor']", u'300s×6=1800s: Postfix 默认恰好是下限的六分之一')
Z(u"F['band_edge_hits'] - 2", u'四天的下沿 ⇎ 五天的上沿: 两份 MTA 的默认各踩住 4-5 天区间一端')
Z(u"F['year_close']", u'相邻年距相加=首末跨度')
Z(u"F['year_span'] - 43", u'1982→2025 跨 43 年')
Z(u"F['obs_n'][0] + F['repl_n'][0] - 3", u'821 没有 Obsoletes, 只有 Replaces 三行号')
Z(u"F['target_n'] - (F['obs_n'][2] + F['upd_n'][2] + F['repl_n'][0])", u'动作头对象并集=各份对象数相加(无重叠)')
Z(u"sum(F['cite_forms_close'])", u'引用三式(空格式⇎连写式⇎短横式)相加=弹性正则在同一名号上读出的枚数, 三份 RFC 各自归零')
Z(u"F['cite_821_3f_in_1123'] - F['cite_821_hy_in_1123'] - F['cite_821_in_1123']",
  u'1123 面上 RFC 821 的三个写法相加=它的总引用数')
Z(u"F['pool_tier_close']", u'共用长行按份数分档之和=池条数')
Z(u"F['union_close']", u'行尺容斥: Σ单份−Σ两两+Σ三三−Σ四四+Σ五五=并集')
Z(u"F['pair_close']", u'两两“归一同形”=“逐字节同形”+“只归一同形”')
Z(u"F['axis_close']", u'写法分家四桶之和=归一同形而逐字节不同的去重串数')
Z(u"F['s_pool_tier_close']", u'句尺分档之和=句池条数')
Z(u"F['s_union_close']", u'句尺容斥闭合=零')
Z(u"F['s_ruler_gain_1123_5321'] - (F['s_pair_1123_5321'] - F['pair_1123_5321'])", u'句尺对 1123·5321 的增益=两尺之差')
Z(u"F['s_pair_html']", u'句尺上两份 MTA 与三份 RFC 之间零共用句')
Z(u"F['apool_tag_close']", u'锚候选池按标签分布之和=池条目数')
Z(u"F['apool_tier_close']", u'锚候选池按份数加权=按标签相加')
Z(u"F['lines_split_close']", u'splitlines 行数=换行计数+1−末行换行+换页符')
Z(u"sum(F['ent_lt_left'])", u'断面面上零枚 &lt; 残留(Exim/Postfix 的尖括号都被实体表还原)')
Z(u"F['ent_double_left'][3]", u'Exim 单趟实体表吃得干净: 零枚 &amp; 残留')
Z(u"sum(F['ent_numeric_left'][:4])", u'数字实体只出现在 Postfix 一侧')
Z(u"sum(F['nul']) + sum(F['cr'])", u'五份面全无 CR 与 NUL')
Z(u"F['shell_ledger_close']", u'两遍壳谓词逐行分账后账平: 采集数+本遍多判−采集多判=本遍数(五份相加)')
Z(u"F['txt_n'] + F['html_n'] - NSRC", u'三份 txt ⇎ 两份 html 相加=五份')


def _ev(e):
    return eval(e.strip().replace(u'\n', u''))


ZF = [w for e, w in ZID if _ev(e)]
F['zid_fail'] = ZF
for e, w in ZID:
    if _ev(e):
        print(u'  失败: ' + w + u' <= ' + e.strip() + u' -> ' + repr(_ev(e)))
F['scalar_clos_n'] = len(ZID)
F['scalar_clos_sum'] = sum(1 for e, w in ZID if not _ev(e))
F['list_clos_n'] = len([k for k in F if (u'_close' in k or u'_ledger' in k) and isinstance(F[k], list)])
F['x_ident_n'] = len(ZID)
# --- SCAN END ---

# --- PICK BEGIN --- (与采集侧(_b74meas.json)逐键对账; 同一段也由 corpus/_wire74.py 机械切进 audit.py::_b74_scan)
MEA = json.load(io.open(u'corpus/_b74meas.json', encoding='utf-8'))
AGREE = []
DIFF = []
for k in (u'bytes', u'chars', u'lines', u'nonblank', u'blank', u'cr', u'ff', u'ff_exact', u'maxlen',
          u'nonascii', u'bom', u'shell_page', u'shell_hdr', u'tag_open', u'tag_close',
          u'comment', u'br_tag', u'ent_total', u'hdr_dot2sp', u'hdr_dot1sp', u'hdr_nodot',
          u'hyphen_break', u'tone', u'tone_tot', u'tone_must_lc', u'kw_clause',
          u'terms', u'sender_smtp', u'smtp_client', u'spelling_queueing', u'spelling_queuing',
          u'retry_word', u'queue_word', u'time_digit_docs', u'tier_tot', u'years',
          u'obs_ids', u'upd_ids', u'pool_n', u'pool_tier', u'pair_share', u'pair_byte',
          u'pair_norm_only', u'pair_nonzero', u'union_incl', u's_pool_n', u's_pool_tier',
          u's_pair_share', u's_incl', u's_union_incl', u'rfc_hdr'):
    (AGREE if F[k] == MEA[k] else DIFF).append((k, F[k], MEA[k]))
# 壳账两问: (1) 本遍照抄采集谓词后能否复现采集的三份 txt 壳数; (2) 本遍自己的谓词与采集差在哪几行
F['shell_vs_pick_txt'] = [F['shell_pick'][i] for i in range(3)]
F['shell_replicate_pick'] = 1 if F['shell_vs_pick_txt'] == MEA['shell_n'][:3] else 0
F['shell_two_ruler_txt'] = 1 if [F['shell_n'][i] for i in range(3)] == MEA['shell_n'][:3] else 0
MEA_TIERP = MEA[u'tier_pats']
MK_TIERP = F[u'tier_pats']
F['tier_pat_shared'] = sorted(set(MEA_TIERP) & set(MK_TIERP))
F['tier_pat_pick_only'] = sorted(set(MEA_TIERP) - set(MK_TIERP))
F['tier_pat_mk_only'] = sorted(set(MK_TIERP) - set(MEA_TIERP))
# 采集侧的 TIERP 与本遍 TIER 同字面(只是顺序不同), 于是逐族面读数可逐枚对拍
PMAP = dict((w, j) for j, w in enumerate(MEA_TIERP))
F['tier_cross_agree'] = [1 if [MEA[u'tier_faces'][i][PMAP[w]] for i in range(NSRC)] == F[u'tier_' + k]
                         else 0 for k, w in TIER.items() if w in PMAP]
F['tier_cross_n'] = len(F['tier_cross_agree'])
F['exim_rule_pick'] = MEA[u'exim_rule_n']
F['exim_rule_mk'] = F['ex_rule_lines']
F['ex_sets_pick'] = MEA[u'exim_sets_n']
F['pf_def_pick'] = [MEA[u'pf_def_sec'][p] for p in PARAM6]
F['pf_chain_pick'] = [1 if x else 0 for x in MEA[u'pf_ge_chain']]
F['axis_pick_str'] = MEA[u'axis_str']
F['pair_max_pick'] = MEA[u'pair_max']
F['needle_table_pick'] = MEA[u'needle_n']
F['needle_table_mk'] = F['needle_n']
F['pick_ladder'] = [MEA[u'sn_strict_docs'], MEA[u'sn_fold_docs'], MEA[u'sn_sh_docs'],
                     MEA[u'sn_ds_docs'], MEA[u'sn_dj_docs']]
F['mk_ladder'] = [F[u'sn_strict_docs'], F[u'sn_fold_docs'], F[u'sn_sh_docs'],
                   F[u'sn_ds_docs'], F[u'sn_dj_docs']]
F['pick_agree'] = len(AGREE)
F['pick_diff'] = len(DIFF) + (F['tier_cross_n'] - sum(F['tier_cross_agree']))
F['pick_below_floor'] = MEA[u'below_floor']
F['giveup_band_pick'] = MEA[u'giveup_band_sec']
for k, a, b in DIFF:
    print(u'  采集⇎建条目不符: %s %s vs %s' % (k, a, b))
assert F['tier_cross_n'] == len(TIER), (F['tier_pat_pick_only'], F['tier_pat_mk_only'])
assert sum(F['tier_cross_agree']) == F['tier_cross_n'], F['tier_cross_agree']
assert F['needle_table_pick'] != F['needle_table_mk']
print(u'  壳谓词复现: 本遍照抄采集侧 is_shell 后逐份复算 %s ⇎ 采集落盘 %s'
      % (F['shell_pick'], MEA[u'shell_n']))
print(u'  两遍壳账: 本遍 %s ⇎ 多判 %s ⇎ 采集多判 %s(逐行分解)' % (F['shell_n'], F['shell_mk_only'], F['shell_pick_only']))
print(u'  对账: %d 键符 ⇎ %d 键不符; 针表不横比(采集 %d 枚字面 ⇎ 本遍 %d 枚锚句)'
      % (F['pick_agree'], F['pick_diff'], F['needle_table_pick'], F['needle_table_mk']))
# --- PICK END ---

BB74 = lambda name, i=None: (F[name] if i is None else F[name][i])
FN = u'B74V'
_to_v = re.compile(r"(?:F|CLOSE)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B74V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(5)').replace(u'NSRC', u'5')


K_, ZERO, COLL, SEENX = {}, [], {}, {}


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K_:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K_.setdefault(s, (expr, note))


def V(name, i=None, note=u''):
    if name not in F:
        raise AssertionError(u'无此键 ' + name)
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def J(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LBL[i])) for i in range(NSRC))


def JL(name, note=u''):
    return V(name, None, note) if isinstance(F[name], (list, dict)) else J(name, note)


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


ZV = []
for e, w in ZID:
    v = to_v(e.replace(u'\n', u''))
    if eval(v, {FN: BB74}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))
    reg(str(_ev(e)), v, w)


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB74}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([tuple(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


for k, v in dump_deriv().items():
    DER[k] = v
io.open(u'corpus/_b74flat.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True))
io.open(u'corpus/_deriv74.json', 'w', encoding='utf-8').write(
    json.dumps(DER, ensure_ascii=False, indent=1, sort_keys=True))

print(u'第二遍量测完成: 扁平键 %d ｜ 恒等式 %d ｜ 失败 %d ｜ 锚针 %d(反向 %d) ｜ 行池 %d ｜ 句池 %d'
      % (len(F), len(ZID), len(ZF), F['needle_n'], F['neg_n'], F['pool_n'], F['s_pool_n']))
print(u'五档阶梯 strict=%s fold=%s sh=%s ds=%s dj=%s ｜ 折行独有 %d 剥壳独有 %d 死集 %s'
      % (F['sn_strict_docs'], F['sn_fold_docs'], F['sn_sh_docs'], F['sn_ds_docs'], F['sn_dj_docs'],
         F['fold_minus_strict_n'], F['ds_only_n'], F['dead_needles']))
print(u'语气 %s ｜ 零MUST份 %s ｜ 五轨全零 %s ｜ 术语 新名千分 %s'
      % (F['tone'], F['tone_zero_must'], F['tone_zero_all'], F['term_new_per_mille']))
print(u'exim %d 串/%d 集 字母 定义%s⇎用%s 档数 %d ｜ postfix 默认 %s ｜ 换算表 %s'
      % (F['ex_rule_lines'], F['ex_sets_n'], F['ex_letters_def'], F['ex_letters'],
         F['ex_attempts_tot'], F['pf_def_sec'], F['cv_sec']))
print(u'池 行尺 %d 最大 %s(%d) 1123·5321=%d ｜ 句尺 %d 1123·5321=%d 增益 %d ｜ 年 %s 跨度 %d'
      % (F['pool_n'], F['pair_max_lbl'], F['pair_max'], F['pair_1123_5321'], F['s_pool_n'],
         F['s_pair_1123_5321'], F['s_ruler_gain_1123_5321'], F['years'], F['year_span']))

exec(io.open(u'corpus/_mk74emit.py', encoding='utf-8').read())
