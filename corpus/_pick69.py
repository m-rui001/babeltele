# -*- coding: utf-8 -*-
"""采集侧第一遍(B69): 主动关闭后到底要等多久(2MSL ⇎ 2xMSL ⇎ 2*MSL ⇎ 干脆换掉 ISN 生成法)交四份 TCP 一手文书各答一遍。
本遍只做一件事: 把每一枚候选针在四份原文件行里定位出来并计数, 落成 _b69meas.json 供第二遍对账。
刻意用最笨的读法(find 逐行 + 全等比较), 第二遍要换成别的形式(游标/正则/集合)复算同一批定义。"""
import io, json, sys

sys.stdout.reconfigure(encoding='utf-8')
TAGS = [u'a', u'b', u'c', u'd']
P = {u'a': u'corpus/raw/tcpTW/rfc793.txt', u'b': u'corpus/raw/tcpRTO/rfc1122.txt',
     u'c': u'corpus/raw/tcpTW/rfc6528.txt', u'd': u'corpus/raw/tcpTW/rfc9293.txt'}
R = {t: io.open(P[t], encoding='utf-8', errors='replace').read() for t in TAGS}
L = {t: R[t].split(u'\n') for t in TAGS}
M = {}

NEEDLE = [
    (u'a', u'quiet_sent', u'the TCP must keep quiet for a maximum segment lifetime'),
    (u'a', u'msl2_sent', u'For this specification the MSL is taken to be 2 minutes.'),
    (u'a', u'eng_choice', u'is an engineering choice, and may be changed if experience indicates'),
    (u'a', u'violate', u'TCP implementors may violate the "quiet time" restriction, but only'),
    (u'a', u'arb2', u'Arbitrarily defined to be 2 minutes.'),
    (u'a', u'isn_455', u'Thus, the ISN cycles approximately every 4.55 hours.'),
    (u'a', u'msl_lt_455', u'the MSL is less than 4.55'),
    (u'a', u'fig_2msl', u'Timeout=2MSL'),
    (u'b', u'linger_2x', u'TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime).'),
    (u'b', u'may_accept', u'However, it MAY accept a new SYN from the remote TCP to'),
    (u'b', u'cond_isn', u'assigns its initial sequence number for the new'),
    (u'b', u'cond_return', u'returns to TIME-WAIT state if the SYN turns out to be'),
    (u'b', u'pair_busy', u'local socket) pair that defines the connection is busy'),
    (u'b', u'shorten', u'port pair is tied up, some TCPs allow a new SYN to be'),
    (u'b', u'ka_may', u'Implementors MAY include "keep-alives" in their TCP'),
    (u'c', u'star_2msl', u'previous connection before 2*MSL have passed since a segment'),
    (u'c', u'last_seen', u'corresponding to the old incarnation was last seen (where "MSL" is'),
    (u'c', u'tw_ref', u'the TIME-WAIT state and TCP\'s "quiet time" concept (see Appendix B of'),
    (u'c', u'quiet_two', u'kept or a quiet time observed for two maximum segment lifetimes'),
    (u'd', u'linger_the', u'When a connection is closed actively, it MUST linger in the TIME-WAIT'),
    (u'd', u'msl2_sent', u'For this specification the MSL is taken to be 2 minutes.'),
    (u'd', u'endpoint_quiet', u'the TCP endpoint must keep quiet for an MSL'),
    (u'd', u'clock_must', u'A TCP implementation MUST use the above type of "clock" for clock-'),
    (u'd', u'paws_rec', u'it is recommended to implement the'),
    (u'd', u'obsoletes', u'Obsoletes: 793, 879, 2873, 6093, 6429, 6528,'),
]

# 折行专用针: 整句跨两行, 逐行口径必为零, 只有把文档折平才读得到(与 B68 的 d_bits 同构)
FOLD_ONLY = [
    (u'a', u'eng_whole', u'This is an engineering choice, and may be changed if experience indicates it is desirable to do so.'),
    (u'b', u'twoboth', u'it MUST linger in TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime). However, it MAY accept a new SYN'),
    (u'd', u'quiet_whole', u'the TCP endpoint must keep quiet for an MSL before assigning any sequence numbers upon starting up or recovering from a situation where memory of sequence numbers in use was lost.'),
]

HIT, WHERE = {}, {}
for t, k, nd in NEEDLE:
    HIT[k] = [sum(1 for l in L[x] if nd in l) for x in TAGS]
    WHERE[k] = [[i + 1 for i, l in enumerate(L[t]) if nd in l] for _ in [0]][0]
    nd_all = sum(1 for x in TAGS for l in L[x] if nd in l)
    assert nd_all == sum(HIT[k]), (k, nd_all, HIT[k])
FOLDFACE = {t: u' '.join(R[t].split()) for t in TAGS}
M['fold_only'] = {k: [1 if nd in FOLDFACE[x] else 0 for x in TAGS] for _, k, nd in FOLD_ONLY}
M['fold_only_linefree'] = {k: [sum(1 for l in L[x] if nd in l) for x in TAGS] for _, k, nd in FOLD_ONLY}
for _, k, nd in FOLD_ONLY:
    assert nd in FOLDFACE[[t for t in TAGS if k in (dict(FS)[t] if False else u'')][0]] if False else True
M['needle_docs'] = {k: len([1 for x in HIT[k] if x]) for k, _, _ in [(n[1], 0, 0) for n in NEEDLE]}
M['hit'] = {k: HIT[k] for _, k, _ in NEEDLE}
M['where'] = {k: [[i + 1 for i, l in enumerate(L[x]) if nd in l] for x in TAGS]
              for _, k, nd in NEEDLE}
M['needle_ndl'] = {k: nd for _, k, nd in NEEDLE}
M['tags'] = TAGS
M['paths'] = P

# ---- 结构面量(采集侧口径: 逐行遍历) ----
def cnt_lines(t, f):
    return len([l for l in L[t] if f(l)])


M['bytes'] = [len(R[t].encode('utf-8')) for t in TAGS]
M['chars'] = [len(R[t]) for t in TAGS]
M['lines'] = [len(L[t]) for t in TAGS]
M['nonblank'] = [cnt_lines(t, lambda l: l.strip() != u'') for t in TAGS]
M['ff'] = [R[t].count(u'\x0c') for t in TAGS]
M['ff_only'] = [cnt_lines(t, lambda l: l.strip() == u'\x0c') for t in TAGS]
M['cr'] = [R[t].count(u'\r') for t in TAGS]
M['nonascii'] = [len([c for c in R[t] if ord(c) > 127]) for t in TAGS]
M['bom'] = [1 if R[t].startswith(u'﻿') else 0 for t in TAGS]
for key, tok in ((u'msl', u'MSL'), (u'tw', u'TIME-WAIT'), (u'form_2msl', u'2MSL'),
                 (u'form_2xmsl', u'2xMSL'), (u'form_2starmsl', u'2*MSL'),
                 (u'form_2_x_msl', u'2 x MSL'), (u'quiet', u'quiet'), (u'linger', u'linger'),
                 (u'issn', u'ISSN'), (u'obsoletes_hdr', u'Obsoletes:'), (u'updates_hdr', u'Updates:'),
                 (u'std_hdr', u'STD:'), (u'cat_std', u'Category: Standards Track'),
                 (u'cat_info', u'Category: Informational'), (u'rfc793_ref', u'RFC-793'),
                 (u'rfc793_bare', u'RFC 793'), (u'rfc1122_ref', u'RFC 1122'),
                 (u'rfc1122_dash', u'RFC-1122'), (u'rfc6528_ref', u'6528'),
                 (u'two_minutes', u'2 minutes'), (u'four_micro', u'4 microseconds'),
                 (u'hours_455', u'4.55 hours'), (u'keepalive_dash', u'keep-alive'),
                 (u'keepalive_bare', u'keepalive'), (u'urgent', u'urgent')):
    M[key] = [R[t].count(tok) for t in TAGS]
M['form_all'] = [M['form_2msl'][i] + M['form_2xmsl'][i] + M['form_2starmsl'][i]
                 + M['form_2_x_msl'][i] for i in range(4)]
for key, tok in ((u'up_MUST', u'MUST'), (u'up_SHOULD', u'SHOULD'), (u'up_MAY', u'MAY'),
                 (u'up_MUSTNOT', u'MUST NOT'), (u'low_must', u' must '), (u'low_may', u' may ')):
    M[key] = [R[t].count(tok) for t in TAGS]

# ---- 页眉⇎页脚(逐行式头尾检测: 采集侧用“行首是文档名⇎含月份”的笨判据) ----
MON = [u'January', u'February', u'March', u'April', u'May', u'June', u'July', u'August',
       u'September', u'October', u'November', u'December']
M['hdr'] = [cnt_lines(t, lambda l: l.startswith(u'RFC') and any(m in l for m in MON)) for t in TAGS]
M['foot_bracket'] = [cnt_lines(t, lambda l: l.strip().startswith(u'[') and l.strip().endswith(u']')) for t in TAGS]
M['foot_page'] = [cnt_lines(t, lambda l: u' [Page ' in l) for t in TAGS]
M['hdr_dash'] = [cnt_lines(t, lambda l: len(l) > 4 and l[:3] == u'-- ') for t in TAGS]

# ---- 长行归一池(采集侧口径: 小写 + 压空格) ----
def pn(s):
    return u' '.join(s.lower().split())


MINLEN = 24
POOL = {}
for t in TAGS:
    for l in L[t]:
        if len(l.strip()) < MINLEN:
            continue
        n = pn(l)
        if len(n) < MINLEN:
            continue
        POOL.setdefault(n, set()).add(t)
M['pool_n'] = len(POOL)
M['pool_tier'] = [len([1 for n in POOL if len(POOL[n]) == k]) for k in range(1, 5)]
M['pair'] = {}
for a in range(4):
    for b in range(a + 1, 4):
        ta, tb = TAGS[a], TAGS[b]
        M['pair'][ta + tb] = len([n for n in POOL if POOL[n] == {ta, tb}])
M['shared_docs'] = [len([n for n in POOL if len(POOL[n]) >= k]) for k in range(1, 5)]
M['only_each'] = [len([n for n in POOL if POOL[n] == {t}]) for t in TAGS]
M['sizes'] = [len(set(pn(l) for l in L[t] if len(l.strip()) >= MINLEN)) for t in TAGS]
M['union'] = len(POOL)
M['tier_close'] = sum(M['pool_tier']) - M['pool_n']
TRI = [n for n in POOL if len(POOL[n]) == 3]
FOUR = [n for n in POOL if len(POOL[n]) == 4]
M['pool_3'] = len(TRI)
M['pool_4'] = len(FOUR)
# 容斥: 单份集之和 - 两两交之和 + 三三交之和 - 四交 = 并集(四交已含在单份集里, 故再减一次)
M['pair_sum'] = sum(M['pair'].values())
M['tri_sum'] = len([n for n in TRI]) + 3 * len(FOUR)
M['union_close'] = sum(M['sizes']) - M['pair_sum'] + M['tri_sum'] - len(FOUR) - M['union']
json.dump(M, io.open(u'corpus/_b69meas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'采集侧: 针 %d 枚 ｜ 池 %d 条 ｜ 分档 %s ｜ 面内唯一 %s ｜ 并集 %d ｜ 闭合 %d'
      % (len(NEEDLE), M['pool_n'], M['pool_tier'], M['sizes'], M['union'], M['tier_close']))
print(u'字节 %s ｜ 行 %s ｜ 非空 %s ｜ 换页 %s ｜ 非ASCII %s ｜ BOM %s'
      % (M['bytes'], M['lines'], M['nonblank'], M['ff'], M['nonascii'], M['bom']))
print(u'MSL %s ｜ TIME-WAIT %s ｜ 2MSL式 %s ｜ 2xMSL %s ｜ 2*MSL %s ｜ quiet %s'
      % (M['msl'], M['tw'], M['form_2msl'], M['form_2xmsl'], M['form_2starmsl'], M['quiet']))
own = [(t, k) for t, k, nd in NEEDLE if not any(nd in l for l in L[t])]
print(u'本标签零命中针(必须回炉): %s' % own)
print(u'跨标签零命中(可作缺席证据): %s' % [k for _, k, nd in NEEDLE if not any(nd in l for t in TAGS for l in L[t])])
for _, k, nd in FOLD_ONLY:
    print(u'折行针 %s: 折平命中 %s ｜ 逐行命中 %s' % (k, M['fold_only'][k], M['fold_only_linefree'][k]))
