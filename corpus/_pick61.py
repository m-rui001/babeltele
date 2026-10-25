# -*- coding: utf-8 -*-
"""B61 现探(采集侧, 只测量不设门槛): 五份 RFC Editor 纯文本对“链路至少要装多少字节 ⇎ 一个包最大能多大 ⇎ 超了谁切碎”。
源: ⟦A⟧rfc1883(1995) ⇎ ⟦B⟧rfc2460(1998) ⇎ ⟦C⟧rfc8200(2017) ⇎ ⟦D⟧rfc2675(Experimental, Jumbograms) ⇎ ⟦E⟧rfc8201(PMTUD)。
本遍用正则族与集合运算; 建条目侧(_mkB61)换算法不换定义(游标档 ⇎ 词界档), 两遍口径一致的键才进对账表 _b61meas.json。
已知先量得的差: 最小 MTU 576⇎1280⇎1280⇎无⇎无; 净载荷算式 528⇎1232⇎删; jumbograms 在标准正文⇎明文移除⇎只字不提⇎实验档接走;
大写义务词五份全 0 而小写满篇; “only by source nodes, not by routers” 三份逐字同在(恒定项, 不作答案差)。"""
import io
import json
import os
import re

D = u'corpus/raw/ipv6/'
TAGS = (u'A', u'B', u'C', u'D', u'E')
PATH = [D + u'rfc1883.txt', D + u'rfc2460.txt', D + u'rfc8200.txt', D + u'rfc2675.txt', D + u'rfc8201.txt']
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
T = [RD(p) for p in PATH]
LOW = [t.lower() for t in T]
NL = u'\n'
LST = [t.split(NL) for t in T]
REC = {}
WLIT = {u'576': u'576', u'1280': u'1280', u'528': u'528', u'1232': u'1232',
        u'c65535': u'65,535', u'jumbo': u'jumbo', u'Jumbo': u'Jumbo'}


def show(name, vals):
    REC.setdefault(name, []).append(vals)
    print(u'%-24s %s' % (name, vals))


print(u'--- 字节/字符/行 ---')
show(u'bytes', [os.path.getsize(p) for p in PATH])
show(u'chars', [len(x) for x in T])
show(u'chars_no_nl', [len(x.replace(NL, u'')) for x in T])
show(u'lines', [len(x.split(NL)) for x in T])
show(u'nonblank', [len([l for l in x.split(NL) if l.strip()]) for x in T])
show(u'maxlen', [max(len(l) for l in x.split(NL)) for x in T])
show(u'trail', [len([l for l in x.split(NL) if l != l.rstrip()]) for x in T])
show(u'cr', [x.count(u'\r') for x in T])
show(u'nonascii', [len([c for c in x if ord(c) > 127]) for x in T])
show(u'pipe', [x.count(u'|') for x in T])
show(u'dashes', [x.count(u'-') for x in T])

print(u'--- 数字族: 字面出现处 ⇎ 带千分位 ⇎ 词界 ---')
LITK = {u'c65535': u'65,535', u'c4294967295': u'4,294,967,295', u'576-octet': u'576-octet',
        u'1280-octet': u'1280-octet', u'1280-octets': u'1280-octets'}
for lit in (u'576', u'1280', u'528', u'1232', u'65535', u'4294967295', u'9000', u'1500', u'2048',
            u'1480', u'1492', u'1452', u'40'):
    show(u'lit_' + lit, [x.count(lit) for x in T])
for k, lit in LITK.items():
    show(u'lit_' + k, [x.count(lit) for x in T])
NUM = re.compile(u'(?<![\\d,])(\\d[\\d,]{2,11})(?![\\d,])')
for i in range(5):
    vals = sorted(set(m.group(1).replace(u',', u'') for m in NUM.finditer(T[i])
                      if 500 <= int(m.group(1).replace(u',', u'')) <= 10000), key=int)
    show(u'numband500_10k ' + TAGS[i], vals[:12])

print(u'--- 折行通道双档: 单空格严档 ⇎ 空白容忍档(差值=排版折行) ---')
W = [(u'w_routers', u'not by\s+routers'), (u'w_floor_sent', u'have an MTU of\s+(\\d+)'),
     (u'w_payload_floor', u'(\\d+) octets \((\\d+) minus'), (u'w_jumbo_opt', u'Jumbo\s+Payload\s+option'),
     (u'w_frag_src', u'performed only by source\s+nodes'), (u'w_1280_oct', u'1280\s+octets'),
     (u'w_576_oct', u'576\s+octets'), (u'w_min_mtu', u'minimum IPv6 MTU from\s+(\\d+)\s+to\s+(\\d+)')]
S = [(u's_routers', u'not by routers'), (u's_floor_sent', u'have an MTU of \\d+ octets'),
     (u's_payload_floor', u'\\d+ octets \\(\\d+ minus'), (u's_jumbo_opt', u'Jumbo Payload option'),
     (u's_frag_src', u'performed only by source nodes'), (u's_1280_oct', u'1280 octets'),
     (u's_576_oct', u'576 octets')]
for nm, pat in W:
    show(nm, [len(re.findall(pat, x)) for x in T])
for nm, pat in S:
    show(nm, [len(re.findall(pat, x)) for x in T])
for i in range(5):
    show(u'floor_vals ' + TAGS[i], re.findall(u'have an MTU of\s+(\\d+)', T[i]))
    show(u'pfloor_pair ' + TAGS[i], re.findall(u'(\\d+) octets \((\\d+) minus', T[i]))
show(u'wrap_gap_routers', [REC[u'w_routers'][-1][i] - REC[u's_routers'][-1][i] for i in range(5)])
show(u'wrap_gap_jumbo', [REC[u'w_jumbo_opt'][-1][i] - REC[u's_jumbo_opt'][-1][i] for i in range(5)])
show(u'wrap_gap_1280', [REC[u'w_1280_oct'][-1][i] - REC[u's_1280_oct'][-1][i] for i in range(5)])
show(u'wrap_gap_frag', [REC[u'w_frag_src'][-1][i] - REC[u's_frag_src'][-1][i] for i in range(5)])
show(u'wrap_gap_floor_sent', [REC[u'w_floor_sent'][-1][i] - REC[u's_floor_sent'][-1][i] for i in range(5)])

print(u'--- 字面串 ⇎ 独立数 token: 差值=它作为更长数字的一部分 ---')
for lit in (u'576', u'1280', u'528', u'1232', u'65535', u'1500', u'1480', u'2112'):
    tok = [len(re.findall(u'(?<![\\d,])%s(?!\\d)' % lit, x)) for x in T]
    show(u'tok_' + lit, tok)
    show(u'subgap_' + lit, [T[i].count(lit) - tok[i] for i in range(5)])
show(u'tok_c65535', [len(re.findall(u'(?<![\\d,])65,535(?!\\d)', x)) for x in T])
show(u'tok_c4294967295', [len(re.findall(u'(?<![\\d,])4,294,967,295(?!\\d)', x)) for x in T])
show(u'dotline', [len(re.findall(u'(?m)^\\s*[|+\\-]{4,}', x)) for x in T])
show(u'figbox', [len(re.findall(u'(?m)^\\s*\\|.*\\|\\s*$', x)) for x in T])

print(u'--- 数 token 的相邻符号分区(必须闭合到 total) ---')


def succ_kind(t, j):
    """j 是 token 末位下标; 分类其后紧邻的排版符号。"""
    rest = t[j:j + 9]
    if rest.startswith(u'-octet'):
        return u'hy_octet'
    if re.match(u' octets?[\\s,.;:)\\-]', rest) or re.match(u' octets?$', rest):
        return u'sp_octet'
    if re.match(u'\\s+octets?[\\s,.;:)\\-]', rest) or re.match(u'\\s+octets?$', rest):
        return u'wrap_octet'
    if rest.startswith(u','):
        return u'comma'
    if rest.startswith(u'.'):
        return u'dot'
    if rest.startswith(u')'):
        return u'paren'
    return u'other'


KINDS = (u'hy_octet', u'sp_octet', u'wrap_octet', u'comma', u'dot', u'paren', u'other')
for k in WLIT:
    if k in (u'jumbo', u'Jumbo'):
        continue
    lit = WLIT[k]
    mat = [[(m.start(), m.end()) for m in re.finditer(u'(?<![\\d,])' + re.escape(lit) + u'(?!\\d)', T[i])]
           for i in range(5)]
    cnt = [{c: 0 for c in KINDS} for i in range(5)]
    for i in range(5):
        for a, b in mat[i]:
            cnt[i][succ_kind(T[i], b)] += 1
    for c in KINDS:
        show(u'sk_%s_%s' % (k, c), [cnt[i][c] for i in range(5)])
    show(u'sk_%s_total' % k, [len(mat[i]) for i in range(5)])
    show(u'sk_%s_close' % k, [sum(cnt[i].values()) - len(mat[i]) for i in range(5)])
    show(u'skother_' + k, [[T[i][b:b + 6] for a, b in mat[i] if succ_kind(T[i], b) == u'other']
                           for i in range(5)])

print(u'--- jumbograms 一族 ---')
show(u'jumbo_ci', [len(re.findall(u'(?i)jumbo', x)) for x in T])
show(u'jumbo_caps', [x.count(u'Jumbo') for x in T])
show(u'jumbo_word', [len(re.findall(u'(?i)\\bjumbo\\b', x)) for x in T])
show(u'jumbo_payload', [len(re.findall(u'(?i)jumbo payload', x)) for x in T])
show(u'jumbo_option_def', [len(re.findall(u'Jumbo Payload option', x)) for x in T])
show(u'remove_note', [x.count(u'Removed all references to jumbograms') for x in T])

print(u'--- 分片一族: 义务主语 ⇎ 术语 ---')
FRAG = [(u'frag_ci', u'(?i)fragment'), (u'frag_word', u'(?i)\\bfragment\\b'),
        (u'frag_head', u'(?i)fragment header'), (u'frag_head_caps', u'Fragment header'),
        (u'frag noun', u'(?i)fragmentation'), (u'src_only', u'performed only by source nodes'),
        (u'not_routers', u'not by routers'), (u'frag_and_reas', u'(?i)fragmentation and reassembly')]
for nm, pat in FRAG:
    show(nm, [len(re.findall(pat, x)) for x in T])
show(u'minmtu_sent', [len(re.findall(u'(?i)every link in the\\s+internet have an MTU of', x)) for x in T])
show(u'at_least', [len(re.findall(u'(?i)at least (\\d+)', x)) for x in T])

print(u'--- MTU 语汇 ---')
for nm, pat in ((u'mtu_any', u'(?i)mtu'), (u'MTU_caps', u'MTU'), (u'link_mtu', u'(?i)link mtu'),
                (u'path_mtu', u'(?i)path mtu'), (u'pmtu', u'PMTU'), (u'ptb', u'(?i)packet too big')):
    show(nm, [len(re.findall(pat, x)) for x in T])

print(u'--- 义务词体例: 全大写(2119 规定) ⇎ 小写(实际写法) ---')
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED', u'RECOMMENDED', u'OPTIONAL'):
    show(u'u_' + w.replace(u' ', u'_').lower(), [x.count(w) for x in T])
for w in (u'must', u'should', u'may', u'required', u'recommended', u'optional', u'allowed', u'needed'):
    show(u'l_' + w, [len(re.findall(u'\\b%s\\b' % w, x)) for x in T])
for w in (u'Must', u'Should', u'May'):
    show(u'c_' + w.lower(), [len(re.findall(u'\\b%s\\b' % w, x)) for x in T])
show(u'rfc2119_ref', [len(re.findall(u'2119', x)) for x in T])
show(u'rfc8174_ref', [len(re.findall(u'8174', x)) for x in T])
show(u'key_words_boiler', [x.count(u'key words') + x.count(u'Key words') for x in T])
show(u'lowercase_selfdoc', [len(re.findall(u'(?i)only uses lower case', x)) for x in T])
show(u'no_cite_2119', [len(re.findall(u"(?i)(doesn't cite RFC 2119|does not cite the RFC 2119 definitions)", x)) for x in T])

print(u'--- 文档身份与废止链 ---')
show(u'obsoletes_hdr', [len(re.findall(u'(?i)^Obsoletes: \\d+', x, re.M)) for x in T])
show(u'updates_hdr', [len(re.findall(u'(?i)^Updates: \\d+', x, re.M)) for x in T])
show(u'category_std', [len(re.findall(u'Category: Standards Track', x)) for x in T])
show(u'category_exp', [len(re.findall(u'Experimental', x)) for x in T])
show(u'obsoleted_by', [len(re.findall(u'(?i)obsoleted by', x)) for x in T])
show(u'stds_stmt', [len(re.findall(u'Standards Track', x)) for x in T])
show(u'errata', [len(re.findall(u'(?i)errata', x)) for x in T])
show(u'change_log_head', [len(re.findall(u'(?m)^ {1,4}\\d\\d\\) ', x)) for x in T])
show(u'rfc_refs', [sorted(set(re.findall(u'RFC\\s?(\\d{4})', x)))[:6] for x in T])
show(u'rfc_ref_n', [len(set(re.findall(u'RFC\\s?(\\d{4})', x))) for x in T])

print(u'--- 窗口切分: 变更记录附录 ⇎ 正文(墓碑句在哪个窗口) ---')
CLO = re.compile(u'(?m)^(?: {0,4}Appendix [A-Z]\\. {1,2}Changes| {0,4}This memo has the following changes from)')


def clo_start(t):
    # 取最后一处: 目录页里同样印着 “Appendix B.  Changes …”, 真附录在其后。
    ms = list(CLO.finditer(t))
    return -1 if not ms else ms[-1].start()


CS = [clo_start(t) for t in T]
show(u'clo_found', [1 if c >= 0 else 0 for c in CS])
show(u'clo_line', [(0 if c < 0 else 1 + T[i].count(NL, 0, c)) for i, c in enumerate(CS)])
for k, lit in sorted(WLIT.items()):
    body, tail = [], []
    for i in range(5):
        if CS[i] < 0:
            body.append(T[i].count(lit))
            tail.append(0)
        else:
            body.append(T[i][:CS[i]].count(lit))
            tail.append(T[i][CS[i]:].count(lit))
    show(u'body_' + k, body)
    show(u'tail_' + k, tail)
    show(u'close_' + k, [body[i] + tail[i] - T[i].count(lit) for i in range(5)])
for i in range(5):
    a = re.search(u'(?m)^5\\.[ \\t]+\\S', T[i])
    b = re.search(u'(?m)^6\\.[ \\t]+\\S', T[i])
    seg = T[i][a.start():b.start()] if a and b else u''
    show(u'sec5_len ' + TAGS[i], len(seg))
    for lit in (u'576', u'1280', u'528', u'1232', u'c65535'):
        show(u'sec5_' + lit + u'_' + TAGS[i], seg.count(WLIT[lit]))

print(u'--- 章节号 ---')
# 编号标题行: 行首至多三空格 + 数字组 + 可选点 + 空白 + 题文, 且行末是字母(目录行以页码数字结尾, 被排除)
HEAD = r'(?m)^ {0,3}(\d+(?:\.\d+)*)\.?[ \t]+\S.*[A-Za-z]$'
show(u'sec_head', [len(re.findall(HEAD, x)) for x in T])
show(u'sec_head_d', [len(set(re.findall(HEAD, x))) for x in T])
show(u'section_cite', [len(re.findall(u'(?i)\\bsection \\d', x)) for x in T])

print(u'--- 整行搬运(归一 a-z0-9, 行长按 strip 计) ---')
N = lambda s: re.sub(u'[^a-z0-9]', u'', s.lower())
L = [set(N(l) for l in LST[i] if len(l.strip()) >= 40 and N(l)) for i in range(5)]
show(u'lines_ge40', [len(x) for x in L])
for a in range(5):
    for b in range(a + 1, 5):
        show(u'share %s%s' % (TAGS[a], TAGS[b]), len(L[a] & L[b]))
show(u'AB_C_inter', len(L[0] & L[1] & L[2]))
show(u'union_ABC', len(L[0] | L[1] | L[2]))
show(u'only_A', len(L[0] - L[1] - L[2]))
show(u'only_C', len(L[2] - L[0] - L[1]))

print(u'--- 锚候选: 含关键数字的长行 ---')
for i in range(5):
    cands = [l.strip() for l in LST[i] if len(l.strip()) >= 55
             and re.search(u'(576|1280|528|1232|65,535|4,294,967,295|jumbo|Jumbo)', l)]
    show(u'num-lines ' + TAGS[i], len(cands))
    for c in cands[:3]:
        show(u'  >', c[:170])

G = {}
PLAIN = (0, 1, 2, 3, 4)


def pl(name):
    v = REC[name][-1]
    return [v[i] for i in PLAIN] if isinstance(v, list) else v


for nm in (u'bytes', u'chars', u'lines', u'nonblank', u'maxlen', u'trail', u'cr', u'nonascii', u'pipe',
           u'jumbo_ci', u'jumbo_caps', u'jumbo_word', u'jumbo_payload', u'jumbo_option_def', u'remove_note',
           u'frag_ci', u'frag_word', u'frag_head', u'frag_head_caps', u'frag_noun', u'frag_and_reas',
           u'minmtu_sent', u'at_least',
           u'w_routers', u'w_floor_sent', u'w_payload_floor', u'w_jumbo_opt', u'w_frag_src',
           u'w_1280_oct', u'w_576_oct', u'w_min_mtu',
           u's_routers', u's_floor_sent', u's_payload_floor', u's_jumbo_opt', u's_frag_src',
           u's_1280_oct', u's_576_oct',
           u'wrap_gap_routers', u'wrap_gap_jumbo', u'wrap_gap_1280', u'wrap_gap_frag', u'wrap_gap_floor_sent',
           u'mtu_any', u'MTU_caps', u'link_mtu', u'path_mtu', u'pmtu', u'ptb',
           u'u_must', u'u_may', u'u_should', u'u_must_not', u'u_should_not', u'u_required',
           u'l_must', u'l_should', u'l_may', u'l_required', u'l_allowed', u'l_needed',
           u'c_must', u'rfc2119_ref', u'rfc8174_ref', u'key_words_boiler',
           u'lowercase_selfdoc', u'no_cite_2119',
           u'category_exp', u'obsoleted_by', u'errata', u'change_log_head', u'rfc_ref_n',
           u'sec_head', u'sec_head_d', u'section_cite', u'lines_ge40', u'clo_found',
           u'share_AB', u'share_BC', u'share_AC', u'share_CD', u'share_CE', u'share_AD', u'share_BD',
           u'AB_C_inter', u'union_ABC', u'only_A', u'only_C'):
    if nm in REC:
        G[nm] = pl(nm)
for lit in (u'576', u'1280', u'528', u'1232', u'65535', u'4294967295', u'9000', u'1500', u'2048', u'1480',
            u'1492', u'1452', u'c65535', u'c4294967295', u'576-octet', u'1280-octet'):
    G[u'lit_' + lit] = pl(u'lit_' + lit)
for lit in (u'576', u'1280', u'528', u'1232', u'c65535', u'jumbo', u'Jumbo'):
    for w in (u'body', u'tail', u'close'):
        key = w + u'_' + lit
        if key in REC:
            G[key] = pl(key)
for i in range(5):
    for lit in (u'576', u'1280', u'528', u'1232', u'c65535'):
        G[u'sec5_%s_%s' % (lit, TAGS[i])] = REC[u'sec5_%s_%s' % (lit, TAGS[i])][-1]
    G[u'sec5_len_' + TAGS[i]] = REC[u'sec5_len ' + TAGS[i]][-1]
for lit in (u'576', u'1280', u'528', u'1232', u'65535', u'1500', u'1480', u'2112'):
    G[u'tok_' + lit] = pl(u'tok_' + lit)
    G[u'subgap_' + lit] = pl(u'subgap_' + lit)
for nm in (u'tok_c65535', u'tok_c4294967295', u'dotline', u'figbox', u'clo_line',
           u'c_should', u'c_may'):
    if nm in REC:
        G[nm] = pl(nm)
for nm in sorted(REC):
    if nm.startswith(u'sk_'):
        G[nm] = pl(nm)
for nm in (u'src_only', u'not_routers', u'obsoletes_hdr', u'updates_hdr', u'category_std', u'stds_stmt',
           u'l_recommended', u'u_recommended', u'dashes', u'chars_no_nl', u'num-lines A', u'num-lines B',
           u'num-lines C', u'num-lines D', u'num-lines E'):
    if nm in REC:
        G[nm] = pl(nm) if nm not in (u'num-lines A', u'num-lines B', u'num-lines C', u'num-lines D',
                                     u'num-lines E') else REC[nm][-1]
for a in range(5):
    for b in range(a + 1, 5):
        G[u'share_%s%s' % (TAGS[a], TAGS[b])] = REC[u'share %s%s' % (TAGS[a], TAGS[b])][-1]
for nm in (u'floor_vals', u'pfloor_pair'):
    for i in range(5):
        G[u'%s_%s' % (nm, TAGS[i])] = REC[u'%s %s' % (nm, TAGS[i])][-1]
KEEP = (
    u'bytes', u'chars', u'lines', u'nonblank',
    u'lit_576', u'lit_1280', u'lit_528', u'lit_1232', u'lit_c65535', u'lit_65535', u'lit_c4294967295',
    u'tok_576', u'subgap_576', u'tok_c65535',
    u'sk_576_hy_octet', u'sk_576_sp_octet', u'sk_576_wrap_octet', u'sk_576_total', u'sk_576_close',
    u'sk_1280_sp_octet', u'sk_1280_wrap_octet', u'sk_1280_total', u'sk_1280_close',
    u'sk_c65535_other', u'sk_c65535_total', u'sk_c65535_close',
    u'clo_found', u'body_576', u'tail_576', u'close_576', u'body_1280', u'tail_1280', u'close_1280',
    u'body_Jumbo', u'tail_Jumbo', u'close_Jumbo',
    u'sec5_576_A', u'sec5_1280_B', u'sec5_1280_C',
    u'w_routers', u's_routers', u'w_floor_sent', u's_floor_sent', u'wrap_gap_floor_sent',
    u'w_jumbo_opt', u's_jumbo_opt',
    u'jumbo_ci', u'jumbo_caps', u'jumbo_option_def', u'remove_note',
    u'frag_ci', u'frag_word', u'src_only', u'not_routers', u'minmtu_sent', u'at_least',
    u'u_must', u'u_may', u'l_must', u'l_may', u'rfc2119_ref', u'lowercase_selfdoc', u'no_cite_2119',
    u'mtu_any', u'link_mtu', u'path_mtu', u'pmtu', u'ptb',
    u'lines_ge40', u'share_AB', u'share_BC', u'share_AC', u'share_CD', u'share_CE',
    u'AB_C_inter', u'union_ABC', u'only_A', u'only_C',
    u'obsoletes_hdr', u'category_exp', u'category_std', u'obsoleted_by', u'errata',
    u'change_log_head', u'rfc_ref_n',
    u'sec_head', u'sec_head_d', u'section_cite',
    u'floor_vals_A', u'floor_vals_B', u'pfloor_pair_A', u'pfloor_pair_B', u'pfloor_pair_C',
    u'num-lines A', u'num-lines E')
G = dict((k, G[k]) for k in KEEP)
G[u'_plain_idx'] = list(PLAIN)
json.dump(G, io.open(u'corpus/_b61meas.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
print(u'已写 corpus/_b61meas.json ｜ 键 %d' % (len(G) - 1))
