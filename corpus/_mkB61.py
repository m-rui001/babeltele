# -*- coding: utf-8 -*-
"""B61 建条目(第二遍现算, 五源): ⟦A⟧rfc1883(1995) ⇎ ⟦B⟧rfc2460(1998) ⇎ ⟦C⟧rfc8200(2017) ⇎ ⟦D⟧rfc2675(Experimental, 超大包) ⇎ ⟦E⟧rfc8201(PMTUD)。
主轴: 一条链路至少要能装多少字节——⟦A⟧ 全篇用 576(九处, 全在 §5), ⟦B⟧/⟦C⟧ 换成 1280, 而 576 在 ⟦B⟧ 只剩变更记录里的一枚墓碑(正文 0 处), 在 ⟦C⟧ 整枚字面都不存在;
净载荷下限 528=576−48 ⇎ 1232=1280−48 ⇎ ⟦C⟧ 把这句删了; 包顶 65,535 五份只用带千分位的写法(无逗号写法全库 0), ⟦D⟧ 把它抬到 4,294,967,295;
⟦E⟧ 通篇不出现任何 MTU 下限数字, 只引用别处的 1500。
配套轴: 超大包(Jumbo Payload option)在 ⟦A⟧ 是正文定义(10 处), 在 ⟦B⟧ 只余变更记录里的“Removed all references to jumbograms”一句(正文 0 处), ⟦C⟧ 只字不提, ⟦D⟧ 整篇接走(63 处);
义务词体例: 2119 的全大写 MUST/SHOULD/MAY 在五份里一处也没有, 小写 must 62⇎56⇎52⇎8⇎28, 而 ⟦E⟧ 自己两处说明了这件事;
分片主语: “performed only by source nodes, not by routers” 三份逐字同在(恒定项), 但后半截“not by routers”被排版折行, 单空格档五份全为 0。
第二遍的独立性: 采集侧用正则族与 re.sub 归一, 本遍一律换成游标档(find 循环 + 逐字符判邻)、折叠面档(先把整篇空白折平再逐字面找)与手工分类(后缀符号用字符测试而非 \\s 类),
形状量用逐字符计数与数换行而非 len/split; 两遍只在定义一致处对账, 对账表 corpus/_b61meas.json 的 94 个键逐个比。
抓取时刻、rfc-editor.org 现行状态页与 IPR/勘误表是否已挂新版只在本机或站外成立, 不进门槛。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
NSRC = 5
ENTRY = u'%s/babeltele/B61_ipv6_mtu_five_answers.md' % C
PATH = [u'corpus/raw/ipv6/rfc1883.txt', u'corpus/raw/ipv6/rfc2460.txt', u'corpus/raw/ipv6/rfc8200.txt',
        u'corpus/raw/ipv6/rfc2675.txt', u'corpus/raw/ipv6/rfc8201.txt']
TAGS = [u'A', u'B', u'C', u'D', u'E']
LB = dict(zip(TAGS, [u'95 初版', u'98 标准', u'17 现行', u'超大包档', u'PMTUD 档']))
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN --- (corpus/_wire61.py 把这一段机械切进 audit.py::_b61_scan)
WCH = u' \t\n\x0b\x0c\r'
DELIM = WCH + u',.;:)-'
DIG = u'0123456789'
ALW = DIG + u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def _isw(c):
    return c in ALW
pnorm = lambda s: u''.join(c for c in s.lower() if (u'a' <= c <= u'z') or (u'0' <= c <= u'9'))
FOLD = []
RAW = [RD(p) for p in PATH]
TXT = RAW[:]
LST = [t.split(NL) for t in TXT]
LOW = [t.lower() for t in TXT]
FAN = [pnorm(t) for t in TXT]
OFOLD = [u' '.join(t.lower().split()) for t in TXT]
FO = [u' '.join(t.split()) for t in TXT]
F = {}


def four(name, f, n=NSRC):
    F[name] = [f(k) for k in range(n)]
    return F[name]


def pos(s, sub, frm=0):
    """游标档: find 循环取出现位置, 与采集侧的 str.count / re.findall 不同法。"""
    out, k = [], s.find(sub, frm)
    while k >= 0:
        out.append(k)
        k = s.find(sub, k + 1)
    return out


def occ(s, sub):
    return len(pos(s, sub))


def sha8(p):
    return hashlib.blake2b(io.open(p, 'rb').read(), digest_size=8).hexdigest()


def numpos(t, num):
    """独立数 token: 前不接数字或逗号、后不接数字(采集侧 (?<![\\d,])N(?!\\d))。"""
    out, k = [], t.find(num)
    while k >= 0:
        e = k + len(num)
        prev = t[k - 1] if k else u''
        nxt = t[e] if e < len(t) else u''
        if prev not in DIG + u',' and nxt not in DIG:
            out.append((k, e))
        k = t.find(num, k + 1)
    return out


def wtok(s, word):
    """词界档由逐字符切词现数: 只在字母/数字边界断开, 与采集侧 \\b…\\b 同判。"""
    out, buf = [], []
    for ch in s + u' ':
        if (u'a' <= ch <= u'z') or (u'A' <= ch <= u'Z') or (u'0' <= ch <= u'9') or ch == u'_':
            buf.append(ch)
        else:
            if buf:
                out.append(u''.join(buf))
                buf = []
    return out


def wcount(s, word, ci=False):
    w = word.lower() if ci else word
    return len([x for x in wtok(s, w) if (x.lower() if ci else x) == w])


# ---- 形状档(逐字符计数、数换行, 而非 len/split) ----
four(u'bytes', lambda i: os.path.getsize(PATH[i]))
four(u'chars', lambda i: sum(1 for _ in TXT[i]))
four(u'lines', lambda i: TXT[i].count(NL) + 1)
four(u'nonblank', lambda i: len([l for l in LST[i] if l.strip()]))
four(u'maxlen', lambda i: max([len(l) for l in LST[i]]))
four(u'trail', lambda i: len([l for l in LST[i] if l != l.rstrip()]))
four(u'cr', lambda i: occ(TXT[i], u'\r'))
four(u'nonascii', lambda i: len([c for c in TXT[i] if ord(c) > 127]))
four(u'pipe', lambda i: occ(TXT[i], u'|'))
four(u'dashes', lambda i: occ(TXT[i], u'-'))
F[u'figbox'] = [len([l for l in LST[i] if l.strip()[:1] == u'|' and l.strip()[-1:] == u'|'])
                for i in range(NSRC)]
F[u'sig'] = [sha8(p) for p in PATH]
F[u'sig_distinct'] = len(set(F[u'sig']))
F[u'chars_split'] = [len(x) for x in TXT]
F[u'lines_nl'] = [len(x.split(NL)) for x in TXT]
F[u'rec_close'] = [F[u'chars'][i] - F[u'chars_split'][i] + F[u'lines'][i] - F[u'lines_nl'][i]
                   for i in range(NSRC)]

# ---- 数字族: 子串出现处 ⇎ 独立数 token ----
for lit in (u'576', u'1280', u'528', u'1232', u'65535', u'4294967295', u'9000', u'1500', u'2048', u'1480'):
    four(u'lit_' + lit, lambda i, lit=lit: occ(TXT[i], lit))
four(u'lit_c65535', lambda i: occ(TXT[i], u'65,535'))
four(u'lit_c4294967295', lambda i: occ(TXT[i], u'4,294,967,295'))
four(u'lit_576-octet', lambda i: occ(TXT[i], u'576-octet'))
four(u'lit_1280-octet', lambda i: occ(TXT[i], u'1280-octet'))
for lit in (u'576', u'1280', u'528', u'1232', u'65535', u'1500'):
    four(u'tok_' + lit, lambda i, lit=lit: len(numpos(TXT[i], lit)))
    F[u'subgap_' + lit] = [F[u'lit_' + lit][i] - F[u'tok_' + lit][i] for i in range(NSRC)]
four(u'tok_c65535', lambda i: len(numpos(TXT[i], u'65,535')))
four(u'tok_c4294967295', lambda i: len(numpos(TXT[i], u'4,294,967,295')))
F[u'comma_only'] = [F[u'lit_c65535'][i] - F[u'lit_65535'][i] for i in range(NSRC)]

# ---- 数 token 的后邻符号分类(逐字符测试, 与采集侧的 \\s 类正则同判) ----


def kind_after(t, b):
    r = t[b:b + 9]
    if r[:6] == u'-octet':
        return u'hy_octet'
    for lead in (1, 0):
        k = 0
        if lead:
            if r[:1] != u' ':
                continue
            k = 1
        else:
            while k < len(r) and r[k] in WCH:
                k += 1
            if k < 1 or (k == 1 and r[0] == u' '):
                continue
        s = r[k:]
        if s[:5] != u'octet':
            continue
        e = 6 if s[5:6] == u's' else 5
        nxt = s[e:e + 1]
        if nxt == u'' or nxt in DELIM:
            return u'sp_octet' if lead else u'wrap_octet'
    if r[:1] == u',':
        return u'comma'
    if r[:1] == u'.':
        return u'dot'
    if r[:1] == u')':
        return u'paren'
    return u'other'


KINDS = (u'hy_octet', u'sp_octet', u'wrap_octet', u'comma', u'dot', u'paren', u'other')
SKLIT = {u'576': u'576', u'1280': u'1280', u'528': u'528', u'1232': u'1232', u'c65535': u'65,535'}
for k in sorted(SKLIT):
    hits = [numpos(TXT[i], SKLIT[k]) for i in range(NSRC)]
    cls = [{c: 0 for c in KINDS} for i in range(NSRC)]
    for i in range(NSRC):
        for a, b in hits[i]:
            cls[i][kind_after(TXT[i], b)] += 1
    for c in KINDS:
        F[u'sk_%s_%s' % (k, c)] = [cls[i][c] for i in range(NSRC)]
    F[u'sk_%s_total' % k] = [len(hits[i]) for i in range(NSRC)]
    F[u'sk_%s_close' % k] = [sum(cls[i].values()) - len(hits[i]) for i in range(NSRC)]
    F[u'skother_' + k] = [[TXT[i][b:b + 8] for a, b in hits[i] if kind_after(TXT[i], b) == u'other']
                          for i in range(NSRC)]

# ---- 窗口: 变更记录附录 ⇎ 正文(整行扫, 取最后一处命中; 目录页也印着同一枚标题) ----


def is_clo(l):
    n = 0
    while n < len(l) and l[n] == u' ' and n < 5:
        n += 1
    if n > 4:
        return False
    c = l[n:]
    if c[:9] == u'Appendix ' and c[9:10] in u'ABCDEFGHIJKLMNOPQRSTUVWXYZ' and c[10:11] == u'.'             and c[11:13] == u'  ':
        return c[13:20] == u'Changes'
    return c[:37] == u'This memo has the following changes from '[:37]


def clo_line(t):
    hit = 0
    for n, l in enumerate(t.split(NL)):
        if is_clo(l):
            hit = n + 1
    return hit


CLN = [clo_line(TXT[i]) for i in range(NSRC)]
F[u'clo_found'] = [1 if c else 0 for c in CLN]
F[u'clo_line'] = CLN
CST = [0 if not c else len(NL.join(LST[i][:c])) + 1 for i, c in enumerate(CLN)]
for k in sorted(SKLIT):
    body, tail = [], []
    for i in range(NSRC):
        if not CLN[i]:
            body.append(occ(TXT[i], SKLIT[k]))
            tail.append(0)
        else:
            body.append(occ(TXT[i][:CST[i]], SKLIT[k]))
            tail.append(occ(TXT[i][CST[i]:], SKLIT[k]))
    F[u'body_' + k] = body
    F[u'tail_' + k] = tail
    F[u'close_' + k] = [body[i] + tail[i] - occ(TXT[i], SKLIT[k]) for i in range(NSRC)]
for w, lit in ((u'jumbo', u'jumbo'), (u'Jumbo', u'Jumbo'), (u'c4294967295', u'4,294,967,295')):
    b = [occ(TXT[i][:CST[i]] if CLN[i] else TXT[i], lit) for i in range(NSRC)]
    tl = [occ(TXT[i][CST[i]:], lit) if CLN[i] else 0 for i in range(NSRC)]
    F[u'body_' + w] = b
    F[u'tail_' + w] = tl
    F[u'close_' + w] = [b[i] + tl[i] - occ(TXT[i], lit) for i in range(NSRC)]


def sec5(i):
    ls = LST[i]
    a = b = 0
    for n, l in enumerate(ls):
        if l[:2] == u'5.' and l[2:3] in u' \t' and not a:
            a = n
        elif a and l[:2] == u'6.' and l[2:3] in u' \t':
            b = n
            break
    return NL.join(ls[a:b]) if a and b else u''


SEC5 = [sec5(i) for i in range(NSRC)]
F[u'sec5_len'] = [len(x) for x in SEC5]
for k in sorted(SKLIT):
    F[u'sec5_' + k] = [occ(SEC5[i], SKLIT[k]) for i in range(NSRC)]
F[u'sec5_out_A'] = [F[u'body_576'][0] - F[u'sec5_576'][0]]
for k in (u'sec5_576', u'sec5_1280', u'sec5_528', u'sec5_1232', u'sec5_c65535'):
    for i in range(NSRC):
        F[u'%s_%s' % (k, TAGS[i])] = F[k][i]
F[u'sec5_out_B'] = [F[u'body_1280'][1] - F[u'sec5_1280'][1]]

# ---- 折行通道双档: 原面逐字面 ⇎ 折平面后逐字面 ----
PAIRS = [(u'routers', u'not by routers'), (u'frag_src', u'performed only by source nodes'),
         (u'jumbo_opt', u'Jumbo Payload option'), (u'1280_oct', u'1280 octets'),
         (u'576_oct', u'576 octets'),
         (u'payload_floor', u'octets (576 minus'), (u'min_mtu', u'minimum IPv6 MTU from 576 to 1280')]
for nm, lit in PAIRS:
    F[u's_' + nm] = [occ(TXT[i], lit) for i in range(NSRC)]
    F[u'w_' + nm] = [occ(FO[i], lit) for i in range(NSRC)]
    F[u'wrap_gap_' + nm] = [F[u'w_' + nm][i] - F[u's_' + nm][i] for i in range(NSRC)]
F[u's_routers'] = [occ(TXT[i], u'not by routers') for i in range(NSRC)]
F[u'w_routers'] = [occ(FO[i], u'not by routers') for i in range(NSRC)]
F[u'wrap_gap_routers'] = [F[u'w_routers'][i] - F[u's_routers'][i] for i in range(NSRC)]
F[u'floor_vals'] = []
F[u'pfloor_pair'] = []
FLIT = u'have an MTU of '
for i in range(NSRC):
    vs, k = [], FO[i].lower().find(u'have an mtu of ')
    while k >= 0:
        j = k + len(FLIT)
        d = u''
        while j < len(FO[i]) and FO[i][j] in DIG:
            d += FO[i][j]
            j += 1
        if d:
            vs.append(d)
        k = FO[i].lower().find(u'have an mtu of ', k + 1)
    F[u'floor_vals'].append(vs)
    pr, k = [], TXT[i].find(u' octets (')
    while k >= 0:
        j = k + 9
        d = u''
        while j < len(TXT[i]) and TXT[i][j] in DIG:
            d += TXT[i][j]
            j += 1
        a = k
        while a > 0 and TXT[i][a - 1] in DIG:
            a -= 1
        if d and a < k and TXT[i][j:j + 6] == u' minus':
            pr.append([TXT[i][a:k], d])
        k = TXT[i].find(u' octets (', k + 1)
    F[u'pfloor_pair'].append(pr)
for i in range(NSRC):
    F[u'floor_vals_' + TAGS[i]] = F[u'floor_vals'][i]
    F[u'pfloor_pair_' + TAGS[i]] = F[u'pfloor_pair'][i]
    F[u'pfloor_pair_' + TAGS[i] + u'_n'] = len(F[u'pfloor_pair'][i])
F[u'w_floor_sent'] = [len(x) for x in F[u'floor_vals']]
# 单空格档: “have an MTU of <数字> octets”必须整行连着写(采集侧 (?i)?no—逐字面 \d+ octets)
F[u's_floor_sent'] = []
for i in range(NSRC):
    c, k = 0, TXT[i].find(FLIT)
    while k >= 0:
        j = k + len(FLIT)
        d = u''
        while j < len(TXT[i]) and TXT[i][j] in DIG:
            d += TXT[i][j]
            j += 1
        if d and TXT[i][j:j + 7] == u' octets':
            c += 1
        k = TXT[i].find(FLIT, k + 1)
    F[u's_floor_sent'].append(c)
# 下限句的两档由谓词现读(宽松=have an MTU of+数字, 严档=其后紧跟单空格 octets), 差值必须来自同一对键
F[u'wrap_gap_floor_sent'] = [F[u'w_floor_sent'][i] - F[u's_floor_sent'][i] for i in range(NSRC)]
F[u'wrap_gap_jumbo'] = [F[u'wrap_gap_jumbo_opt'][i] for i in range(NSRC)]
F[u'wrap_gap_1280'] = [F[u'wrap_gap_1280_oct'][i] for i in range(NSRC)]
F[u'wrap_gap_frag'] = [F[u'wrap_gap_frag_src'][i] for i in range(NSRC)]

# ---- 超大包一族 ----
four(u'jumbo_ci', lambda i: occ(LOW[i], u'jumbo'))
four(u'jumbo_caps', lambda i: occ(TXT[i], u'Jumbo'))
four(u'jumbo_word', lambda i: wcount(TXT[i], u'jumbo', True))
four(u'jumbo_payload', lambda i: len(pos(LOW[i], u'jumbo payload')))
four(u'jumbo_option_def', lambda i: occ(TXT[i], u'Jumbo Payload option'))
four(u'remove_note', lambda i: occ(TXT[i], u'Removed all references to jumbograms'))
F[u'jumbo_hybr'] = [F[u'jumbo_caps'][i] - F[u'jumbo_option_def'][i] for i in range(NSRC)]

# ---- 分片一族 ----
four(u'frag_ci', lambda i: occ(LOW[i], u'fragment'))
four(u'frag_word', lambda i: wcount(TXT[i], u'fragment', True))
four(u'frag_head', lambda i: len(pos(LOW[i], u'fragment header')))
four(u'frag_head_caps', lambda i: occ(TXT[i], u'Fragment header'))
four(u'frag_noun', lambda i: len(pos(LOW[i], u'fragmentation')))
four(u'src_only', lambda i: occ(TXT[i], u'performed only by source nodes'))
four(u'not_routers', lambda i: occ(TXT[i], u'not by routers'))
four(u'frag_and_reas', lambda i: len(pos(LOW[i], u'fragmentation and reassembly')))
four(u'minmtu_sent', lambda i: len(pos(FO[i].lower(), u'every link in the internet have an mtu of')))
F[u'at_least'] = []
for i in range(NSRC):
    F[u'at_least'].append(len([a for a in pos(LOW[i], u'at least ') if LOW[i][a + 9:a + 10].isdigit()]))
F[u'frag_src_share'] = len([1 for l in LST[0] if u'performed only by source nodes' in l
                            and all(any(u'performed only by source nodes' in m for m in LST[k])
                                   for k in range(1, NSRC))])

# ---- MTU 语汇 ----
four(u'mtu_any', lambda i: occ(LOW[i], u'mtu'))
four(u'MTU_caps', lambda i: occ(TXT[i], u'MTU'))
four(u'link_mtu', lambda i: len(pos(LOW[i], u'link mtu')))
four(u'path_mtu', lambda i: len(pos(LOW[i], u'path mtu')))
four(u'pmtu', lambda i: occ(TXT[i], u'PMTU'))
four(u'ptb', lambda i: len(pos(LOW[i], u'packet too big')))
F[u'mtu_wrap'] = [len(pos(FO[i].lower(), u'path mtu')) - F[u'path_mtu'][i] for i in range(NSRC)]

# ---- 义务词体例: 全大写子串档 ⇎ 小写词界档 ⇎ 首字母大写档 ----
for w in (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY', u'REQUIRED', u'RECOMMENDED'):
    four(u'u_' + w.replace(u' ', u'_').lower(), lambda i, w=w: occ(TXT[i], w))
for w in (u'must', u'should', u'may', u'required', u'recommended', u'optional', u'allowed', u'needed'):
    four(u'l_' + w, lambda i, w=w: wcount(TXT[i], w))
for w in (u'Must', u'Should', u'May'):
    four(u'c_' + w.lower(), lambda i, w=w: wcount(TXT[i], w))
F[u'l_must_ci'] = [wcount(TXT[i], u'must', True) for i in range(NSRC)]
F[u'oblig_up'] = [F[u'u_must'][i] + F[u'u_should'][i] + F[u'u_may'][i] for i in range(NSRC)]
F[u'oblig_low'] = [F[u'l_must'][i] + F[u'l_should'][i] + F[u'l_may'][i] for i in range(NSRC)]
four(u'rfc2119_ref', lambda i: occ(TXT[i], u'2119'))
four(u'rfc8174_ref', lambda i: occ(TXT[i], u'8174'))
four(u'key_words_boiler', lambda i: occ(TXT[i], u'key words') + occ(TXT[i], u'Key words'))
four(u'lowercase_selfdoc', lambda i: len(pos(LOW[i], u'only uses lower case')))
F[u'no_cite_2119'] = [occ(LOW[i], u"doesn't cite rfc 2119")
                      + occ(LOW[i], u'does not cite the rfc 2119 definitions') for i in range(NSRC)]

# ---- 文档身份与体例(整行扫, 不用 (?m) 锚) ----
four(u'obsoletes_hdr', lambda i: len([l for l in LST[i]
                                      if l[:10].lower() == u'obsoletes:' and l[10:].strip()[:1].isdigit()]))
four(u'updates_hdr', lambda i: len([l for l in LST[i]
                                    if l[:7].lower() == u'updates' and l[7:8] == u':']))
four(u'category_std', lambda i: occ(TXT[i], u'Category: Standards Track'))
four(u'category_exp', lambda i: occ(TXT[i], u'Experimental'))
four(u'obsoleted_by', lambda i: len(pos(LOW[i], u'obsoleted by')))
four(u'stds_stmt', lambda i: occ(TXT[i], u'Standards Track'))
four(u'errata', lambda i: len(pos(LOW[i], u'errata')))
four(u'change_log_head', lambda i: len([l for l in LST[i]
                                        if l[:1] == u' ' and 2 <= len(l.strip()) and l.strip()[:2].isdigit()
                                        and l.strip()[2:4] == u') ' and len(l) - len(l.lstrip()) <= 4]))
F[u'rfc_refs'] = []
for i in range(NSRC):
    got, k = {}, TXT[i].find(u'RFC')
    while k >= 0:
        j = k + 3
        if j < len(TXT[i]) and TXT[i][j] == u' ':
            j += 1
        d = u''
        while j < len(TXT[i]) and TXT[i][j] in DIG and len(d) < 4:
            d += TXT[i][j]
            j += 1
        if len(d) == 4:
            got[d] = 1
        k = TXT[i].find(u'RFC', k + 1)
    F[u'rfc_refs'].append(sorted(got))
F[u'rfc_ref_n'] = [len(x) for x in F[u'rfc_refs']]


def headnum(i):
    """编号标题行: 行首至多三空格、数字组(可含小节点号)、可选尾点、空白、题文, 且行末为字母(目录行以页码数字结尾)。"""
    out = []
    for l in LST[i]:
        n = 0
        while n < len(l) and l[n] == u' ' and n < 4:
            n += 1
        if n > 3 or not l:
            continue
        if not (u'a' <= l[-1].lower() <= u'z'):
            continue
        j = n
        seg = u''
        while True:
            d = u''
            while j < len(l) and l[j] in DIG:
                d += l[j]
                j += 1
            if not d:
                break
            if j < len(l) and l[j] == u'.':
                if seg and l[j - 1] == u'.':
                    break
                seg += (u'.' if seg else u'') + d + u'.'
                j += 1
                continue
            seg += (u'.' if seg else u'') + d
            break
        if not seg:
            continue
        if seg.endswith(u'.'):
            seg = seg[:-1]
        if j < len(l) and l[j] in u' 	' and l[j:].strip():
            out.append(seg)
    return out


F[u'sec_head'] = [len(headnum(i)) for i in range(NSRC)]
F[u'sec_head_d'] = [len(set(headnum(i))) for i in range(NSRC)]
four(u'section_cite', lambda i: len([1 for a in pos(LOW[i], u'section ')
                                     if LOW[i][a + 8:a + 9].isdigit()
                                     and (a == 0 or not _isw(LOW[i][a - 1]))]))

# ---- 整行搬运(排序合并求交并, 不用集合运算符) ----
GE40 = [sorted(set(pnorm(l) for l in LST[i] if len(l.strip()) >= 40 and pnorm(l))) for i in range(NSRC)]
four(u'lines_ge40', lambda i: len(GE40[i]))


def m_inter(a, b):
    i = j = n = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            n += 1
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return n


def m_union(*sets):
    seen = {}
    for s in sets:
        for x in s:
            seen[x] = 1
    return len(seen)


for a in range(NSRC):
    for b in range(a + 1, NSRC):
        F[u'share_%s%s' % (TAGS[a], TAGS[b])] = m_inter(GE40[a], GE40[b])
F[u'AB_C_inter'] = m_inter(sorted(set(x for x in GE40[0] if x in set(GE40[1]))), GE40[2])
F[u'union_ABC'] = m_union(GE40[0], GE40[1], GE40[2])
F[u'only_A'] = len([x for x in GE40[0] if x not in GE40[1] and x not in GE40[2]])
F[u'only_B'] = len([x for x in GE40[1] if x not in GE40[0] and x not in GE40[2]])
F[u'only_C'] = len([x for x in GE40[2] if x not in GE40[0] and x not in GE40[1]])
F[u'abc_close'] = (F[u'only_A'] + F[u'only_B'] + F[u'only_C'] + F[u'share_AB'] + F[u'share_BC']
                   + F[u'share_AC'] - 2 * F[u'AB_C_inter'] - F[u'union_ABC'])

# ---- 锚候选行 ----
NLITS = (u'576', u'1280', u'528', u'1232', u'65,535', u'4,294,967,295', u'jumbo', u'Jumbo')
four(u'num-lines', lambda i: len([l for l in LST[i] if len(l.strip()) >= 55
                                  and any(x in l for x in NLITS)]))
for i in range(NSRC):
    F[u'num-lines_' + TAGS[i]] = F[u'num-lines'][i]
    F[u'num-lines ' + TAGS[i]] = F[u'num-lines'][i]

# ---- 锚池: 按“这条锚在几份文书里逐字再现”分层 ----
SPECIAL = (u'576', u'1280', u'528', u'1232', u'65,535', u'4,294,967,295', u'Jumbo', u'jumbo',
           u'performed only by source nodes', u'have an MTU of', u'RFC 2119', u'MTU', u'octets')
POOL = set()
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if pnorm(l):
            POOL.add((t, l))
POOL = sorted(POOL)
CROSS = dict(((t, x), sum(1 for k in range(NSRC) if pnorm(x) in FAN[k])) for (t, x) in POOL)
POOLC = [(t, CROSS[(t, x)], x) for (t, x) in POOL]
F[u'pool_n'] = len(POOLC)
four(u'pool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
for n in range(1, NSRC + 1):
    F[u'pool_%d' % n] = len([p for p in POOLC if p[1] == n])
F[u'pool_tiers'] = [F[u'pool_%d' % n] for n in range(1, NSRC + 1)]
F[u'pool_close'] = sum(F[u'pool_tiers']) - F[u'pool_n']
F[u'pool_maxlen'] = max(len(p[2]) for p in POOLC)


def ATOMSEL(kind, tag, *needles):
    ok = (lambda n: n == 1) if kind == u'own' else (lambda n: n == int(kind))
    got = [p for p in POOLC if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
    if not got:
        got = [p for p in POOLC if p[0] == tag and all(x in p[2] for x in needles)]
    assert got, (kind, tag, needles)
    return max(got, key=lambda x: (len(x[2]), x[2]))


USEDATOM = []


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    USEDATOM.append(x[2])
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


CLOSK = sorted([k for k in F if (u'_close' in k or k.endswith(u'_ledger'))
                and isinstance(F[k], (int, float)) and not isinstance(F[k], bool)])
F[u'scalar_clos_n'] = len(CLOSK)
F[u'scalar_clos_sum'] = sum(F[k] for k in CLOSK)
F[u'scalar_clos_list'] = CLOSK
F[u'list_clos_n'] = len([k for k in F if (u'_close' in k or k.endswith(u'_ledger')) and isinstance(F[k], list)])

# --- SCAN END ---

# ---------- DERIV 登记与正文模板 ----------
K, ZERO, COLL, SEENX = {}, [], {}, {}
G, LINES, MISSING = {}, [], []
FN = u'B61V'


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K.setdefault(s, (expr, note))


def dump_deriv():
    out = dict((k, v[0]) for k, v in K.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {u'B61V': BB61}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"%s*(1-(len(set([tuple(y) for y in [%s]]))-1))" % (k, u','.join(exprs))
    return out


def V(name, i=None, note=u''):
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


def CLOS(key, note):
    return V(key, None, note)


def CLOS4(key, note):
    return u' ⇎ '.join(V(key, i, u'%s·%s' % (note, LB[t])) for i, t in enumerate(TAGS))


TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


def JOIN(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LB[t])) for i, t in enumerate(TAGS))


BB61 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B61V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
BARE = re.compile(r'^[0-9+\-*/().,\s]*$')
HELP = re.compile(u"^(V|JOIN|CLOS|CLOS4|TOK|AT)\\(")
_Q = u'"\''


def _split_top(s):
    out, buf, d, q = [], u'', 0, None
    for ch in s:
        if q:
            buf += ch
            if ch == q:
                q = None
            continue
        if ch in _Q:
            q = ch
            buf += ch
            continue
        if ch in u'([{':
            d += 1
        elif ch in u')]})':
            d -= 1
        if ch == u',' and d == 0:
            out.append(buf)
            buf = u''
            continue
        buf += ch
    out.append(buf)
    return [x.strip() for x in out]


def _unlit(x):
    t = x[1:] if x[:1] == u'u' else x
    assert t[0] in _Q and t[-1] == t[0], x
    return t[1:-1]


def _inline(t):
    while True:
        i = t.find(u'{EXPR(')
        if i < 0:
            break
        j = t.index(u'(', i)
        d, k = 0, j
        q = None
        while True:
            c = t[k]
            if q:
                if c == q:
                    q = None
                k += 1
                continue
            if c in _Q:
                q = c
                k += 1
                continue
            if c == u'(':
                d += 1
            elif c == u')':
                d -= 1
                if d == 0:
                    break
            k += 1
        if t[k + 1] != u'}':
            raise AssertionError((u'EXPRSCAN', repr(t[i:k + 4]), repr(t[j + 1:k])))
        args = _split_top(t[j + 1:k])
        assert len(args) == 3, args
        val = eval(args[0], {u'F': F, u'B61V': BB61, u'len': len, u'max': max, u'round': round,
                             u'repr': repr})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]

    def rep(m):
        c = m.group(1).strip()
        if HELP.match(c):
            return eval(c, {u'V': V, u'JOIN': JOIN, u'CLOS': CLOS, u'CLOS4': CLOS4, u'TOK': TOK, u'AT': AT})
        if u'B61V(' not in c:
            return m.group(0)
        assert BARE.match(BCALL.sub(u'0', c)), c
        val = eval(c, {u'B61V': BB61})
        reg(str(val), c.strip(), c.strip())
        return str(val)
    return re.sub(r'\{([^{}]*)\}', rep, t)


class _Ctx(dict):
    def __missing__(self, k):
        MISSING.append(k)
        return u'§' + k


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + _inline(tmpl)).format_map(_Ctx(dict(G, **kw))))

# ---------- 锚(位置由池现推, 不手打) ----------
G[u'A_min'] = AT(u'own', u'A', u'have an MTU of 576')
G[u'B_min'] = AT(u'own', u'B', u'have an MTU of 1280')
G[u'A_528'] = AT(u'own', u'A', u'reduced to 528')
G[u'B_1232'] = AT(u'own', u'B', u'reduced to 1232')
G[u'B_tomb'] = AT(u'own', u'B', u'minimum IPv6 MTU from 576')
G[u'B_rmjumbo'] = AT(u'own', u'B', u'Removed all references to jumbograms')
G[u'A_jumbo'] = AT(u'own', u'A', u'Jumbo Payload option is used')
G[u'D_jumbo'] = AT(u'own', u'D', u'is an IPv6 packet containing a payload')
G[u'D_max'] = AT(u'own', u'D', u'4,294,967,295')
G[u'C_65535'] = AT(u'own', u'C', u'65,535 octets, then')
G[u'ABC_frag'] = AT(u'3', u'A', u'performed only by source nodes')
G[u'E_note'] = AT(u'own', u'E', u'does not cite the RFC 2119 definitions')
G[u'E_chlog'] = AT(u'own', u'E', u"doesn't cite RFC 2119")
G[u'E_1500'] = AT(u'own', u'E', u'1500 octets for IPv6')
G[u'B_1500'] = AT(u'own', u'B', u'MTU of 1500')
G[u'C_hy'] = AT(u'own', u'C', u'1280-octet packet')

# ---------- 正文 ----------
LINE(u'🧭', u"五源字节 {JOIN('bytes')}: 95 初版 ⇎ 98 标准 ⇎ 17 现行 ⇎ 超大包档 ⇎ PMTUD 档; 面内字符 {JOIN('chars')} ⇎ 原文件行 {JOIN('lines')} ⇎ 非空行 {JOIN('nonblank')} ⇎ 最长行 {JOIN('maxlen')} 列 ⇎ 图框行(两端竖线) {JOIN('figbox')} 行。"
     u"五份全是 LF 面: 回车符 {CLOS4('cr', '回车符')} 枚、非 ASCII 字符 {CLOS4('nonascii', '非 ASCII')} 枚, 而行尾空格 {JOIN('trail')} 处——排版只在行内动, 不换行序。"
     u"形状量另用独立算法复算(逐字符计数代 len, 数换行代 split), 两法之差逐份 {JOIN('rec_close')}。五份签名 {V('sig_distinct')} 种(blake2b 前 16 位)。")

LINE(u'📐', u"最小链路 MTU 只由一个句式给出: every link … have an MTU of + 数字 + octets or greater。折叠面现读: 95 初版 {V('floor_vals_A')} ⇎ 98 标准 {V('floor_vals_B')} ⇎ 17 现行 {V('floor_vals_C')} ⇎ 超大包档 {V('floor_vals_D')} ⇎ PMTUD 档 {V('floor_vals_E')}; "
     u"该句式命中 {JOIN('minmtu_sent')} 句。字面出现处 576 {JOIN('lit_576')} ⇎ 1280 {JOIN('lit_1280')}: 576 九处全在 95 初版的 §5 里(§5 内 {V('sec5_576', 0)} 处 ⇎ 正文他处 {V('sec5_out_A', 0)} 处), "
     u"而 98 标准的 1280 十处中 §5 占 {V('sec5_1280', 1)} 处、17 现行的 1280 八处中 §5 占 {V('sec5_1280', 2)} 处——同一节被整体重写了一次。"
     u"净载荷下限由括号算式给出: 95 初版 528=576−48 {A_528} ⇎ 98 标准 1232=1280−48 {B_1232}; 成对读数 {V('pfloor_pair_A_n')}⇎{V('pfloor_pair_B_n')}⇎ 17 现行 {V('pfloor_pair_C_n')} 对——现行版把“至少要能装多少净载荷”这句删了, 只留 1280 本身 {C_hy}。"
     u"PMTUD 档不答这题: 576 {V('lit_576', 4)} 处 ⇎ 1280 {V('lit_1280', 4)} 处 ⇎ 528 {V('lit_528', 4)} 处, 它只引用别处的 {E_1500}。")

LINE(u'⚖', u"墓碑在哪个窗口: 变更记录附录的定位行按“整行扫、两支同收(“Appendix 字母.  Changes…” ⇎ “This memo has the following changes from…”)、取最后一处命中”定位(目录页也印着同一枚标题), 行号 {JOIN('clo_line')}(0=无此附录), 命中 {JOIN('clo_found')}。"
     u"以该行为界把整篇切成 正文 ⇎ 变更记录 两窗, 五份分别读: 576 正文 {JOIN('body_576')} ⇎ 变更记录 {JOIN('tail_576')}, 1280 正文 {JOIN('body_1280')} ⇎ 变更记录 {JOIN('tail_1280')}, "
     u"两半相加减全量 {CLOS4('close_576', '576 两窗闭合')} ⇎ {CLOS4('close_1280', '1280 两窗闭合')}。"
     u"于是 98 标准里 576 只剩一处, 且落在变更记录窗内: {B_tomb}——它不是链路要求, 是“本节把 576 改成 1280”的自我说明; 而 17 现行连这一处也没有(正文 {V('body_576', 2)} ⇎ 变更记录 {V('tail_576', 2)})。"
     u"同一枚附录窗对超大包同样成立: Jumbo 大写 95 初版正文 {V('body_Jumbo', 0)} 处 ⇎ 98 标准正文 {V('body_Jumbo', 1)} 处、变更记录 {V('tail_Jumbo', 1)} 处 {B_rmjumbo} ⇎ 17 现行 {V('body_Jumbo', 2)}⇎{V('tail_Jumbo', 2)} 处。"
     u"判“这条要求还在不在”只能先判窗口: 数出现处会把 98 标准读成仍然要求 576 的一份文书。")

LINE(u'🔁', u"数 token 的后邻符号分档(逐字符判, 窗口九字符): 576 在 95 初版的九处 = 连字符单位 {V('sk_576_hy_octet', 0)} + 空格单位 {V('sk_576_sp_octet', 0)} + 折行单位 {V('sk_576_wrap_octet', 0)} + 逗号 {V('sk_576_comma', 0)} + 句号 {V('sk_576_dot', 0)} + 其余 {V('sk_576_other', 0)}, 合计 {V('sk_576_total', 0)}(闭合 {V('sk_576_close', 0, '576 分档闭合')}); "
     u"1280 在 98 标准的十处 = {V('sk_1280_hy_octet', 1)}+{V('sk_1280_sp_octet', 1)}+{V('sk_1280_wrap_octet', 1)}+{V('sk_1280_comma', 1)}+{V('sk_1280_dot', 1)}+{V('sk_1280_other', 1)} = {V('sk_1280_total', 1)}(闭合 {V('sk_1280_close', 1, '1280 分档闭合')}), 17 现行 {V('sk_1280_total', 2)} 处同构 {V('sk_1280_sp_octet', 2)}⇎{V('sk_1280_wrap_octet', 2)}。"
     u"两代用的是同一套句式骨架, 换的只有数字: 单位后缀的四种相邻符号在两代里各自成对出现。"
     u"值域写法只有一种: 65,535 带千分位 {JOIN('lit_c65535')} 处 ⇎ 无逗号 65535 {JOIN('lit_65535')} 处 ⇎ 差 {CLOS4('comma_only', '只带千分位')}; 独立 token 档 {JOIN('tok_c65535')}(其余被行尾标点或非数字隔开)。"
     u"576 的子串档 {JOIN('lit_576')} ⇎ 独立 token 档 {JOIN('tok_576')}, 差 {CLOS4('subgap_576', '子串比 token 多')} 处; 4,294,967,295 只在超大包档 {V('lit_c4294967295', 3)} 处 {D_max}。")

LINE(u'🧪', u"超大包的一条生命线: jumbo 忽略大小写 {JOIN('jumbo_ci')} 处 ⇎ 大写 Jumbo {JOIN('jumbo_caps')} 处 ⇎ “Jumbo Payload option”逐字面 {JOIN('jumbo_option_def')} 处。"
     u"95 初版把它写进正文选项定义 {A_jumbo}; 98 标准正文 0 处, 只在变更记录留一句移除说明 {B_rmjumbo}(选项定义逐字面 {V('jumbo_option_def', 1)} 处); "
     u"17 现行 {V('jumbo_ci', 2)} 处——整词也不提; 超大包档把它接回去: {V('jumbo_ci', 3)} 处、选项定义 {V('jumbo_option_def', 3)} 处, 定义句 {D_jumbo}, 载荷值域 {D_max}。"
     u"PMTUD 档 {V('jumbo_ci', 4)} 处。同一件事在“标准正文 ⇎ 标准的变更记录 ⇎ 现行标准 ⇎ 实验档”四个位置各有读数: 98 标准的 Jumbo 大写 {V('jumbo_caps', 1)} 处里有 {V('tail_Jumbo', 1)} 处落在变更记录窗内(正文 {V('body_Jumbo', 1)} 处)。"
     u"分档合计: jumbo 小写窗内 {JOIN('body_jumbo')} ⇎ 窗外 {JOIN('tail_jumbo')}, 大写 {JOIN('body_Jumbo')} ⇎ {JOIN('tail_Jumbo')}, 闭合 {CLOS4('close_Jumbo', 'Jumbo 两窗闭合')}。")

LINE(u'⛓', u"折行通道(原面逐字面 ⇎ 整篇空白折平后逐字面): “not by routers”原面 {JOIN('s_routers')} 处 ⇎ 折平 {JOIN('w_routers')} 处, 差 {CLOS4('wrap_gap_routers', '折行补回')}; "
     u"三文书逐字共有的分片主语句 {ABC_frag} 里, 后半截“not by routers”一律被排到下一行行首——用单空格短语搜这份库, 五份全部报“没有这句话”, 而它恰是 IPv6 与 IPv4 最关键的一条分片差别。"
     u"同一通道对单位写法成立: “1280 octets”原面 {JOIN('s_1280_oct')} ⇎ 折平 {JOIN('w_1280_oct')}, 差 {JOIN('wrap_gap_1280_oct')}; 对选项名亦然: “Jumbo Payload option”原面 {JOIN('s_jumbo_opt')} ⇎ 折平 {JOIN('w_jumbo_opt')}, 差 {JOIN('wrap_gap_jumbo_opt')}。"
     u"分片词族本身不受此通道影响: “performed only by source nodes”原面 {JOIN('s_frag_src')} ⇎ 折平 {JOIN('w_frag_src')} 处, 差 {CLOS4('wrap_gap_frag', '该短语折行差')}; fragment 忽略档 {JOIN('frag_ci')} ⇎ 词界档 {JOIN('frag_word')} ⇎ “fragment header”{JOIN('frag_head')} ⇎ “fragmentation and reassembly”{JOIN('frag_and_reas')}。")

LINE(u'📏', u"义务词体例反了: 2119 规定的四枚全大写词在库里一处也没有——MUST {JOIN('u_must')} ⇎ SHOULD {JOIN('u_should')} ⇎ MAY {JOIN('u_may')} ⇎ MUST NOT {JOIN('u_must_not')} 处, 全大写族 {JOIN('oblig_up')} 处; "
     u"小写词界档 must {JOIN('l_must')} ⇎ should {JOIN('l_should')} ⇎ may {JOIN('l_may')} ⇎ required {JOIN('l_required')}, 三词合计 {JOIN('oblig_low')} 处。"
     u"首字母大写档 Must {JOIN('c_must')} ⇎ Should {JOIN('c_should')} ⇎ May {JOIN('c_may')}——超大包档 {V('c_must', 3)} 处 Must 出现在例句里而非规定语。"
     u"PMTUD 档自己说明了体例: 它引用 2119 {V('rfc2119_ref', 4)} 次 ⇎ 另四份 {V('rfc2119_ref', 0)}⇎{V('rfc2119_ref', 1)}⇎{V('rfc2119_ref', 2)}⇎{V('rfc2119_ref', 3)} 次, "
     u"并在引言写明 {E_note}, 在变更记录写明 {E_chlog}——“only uses lower case”两窗各计 {JOIN('lowercase_selfdoc')} 处, “不引用 2119 定义”之说 {JOIN('no_cite_2119')} 处。"
     u"关键词样板(key words)另 {JOIN('key_words_boiler')} 处 ⇎ 规定全大写体例的那份编号文书在此库被引用 {CLOS4('rfc8174_ref', '引用它')} 次。")

LINE(u'🗓', u"MTU 语汇密度与题量不成比例: MTU 忽略档 {JOIN('mtu_any')} ⇎ 大写 MTU {JOIN('MTU_caps')} ⇎ “link mtu”{JOIN('link_mtu')} ⇎ “path mtu”{JOIN('path_mtu')} ⇎ PMTU 缩写 {JOIN('pmtu')} ⇎ “packet too big”{JOIN('ptb')}。"
     u"PMTUD 档 219 处 MTU 而 0 处任何 MTU 下限数字: 576 {V('lit_576', 4)} ⇎ 1280 {V('lit_1280', 4)} ⇎ 65,535 {V('lit_c65535', 4)}——它整篇只讲“怎么量到路径上最小的一环”, 那个最小的环是多少字节由别人规定。"
     u"缩写档在两代标准里 {CLOS4('pmtu', 'PMTU 缩写')} 处, 只在 PMTUD 档 {V('pmtu', 4)} 处; “path mtu”折行档比原面多 {CLOS4('mtu_wrap', 'path mtu 折行差')} 处。"
     u"“at least + 数字”句式 {JOIN('at_least')} 处(95 初版 {V('at_least', 0)} ⇎ 98 标准 {V('at_least', 1)} ⇎ 17 现行 {V('at_least', 2)}), 后接数字者才计——它把下限句与推荐句(“MTU of 1500 octets or greater”{B_1500})同形并列, 只能读数字不能读句式。")

LINE(u'🧾', u"体例与身份: Obsoletes 头 {JOIN('obsoletes_hdr')} 行 ⇎ Updates 头 {JOIN('updates_hdr')} 行 ⇎ “obsoleted by”{JOIN('obsoleted_by')} 处 ⇎ Experimental {JOIN('category_exp')} 处 ⇎ 勘误提及 {JOIN('errata')} 处。"
     u"变更记录条目行(缩进至多四空格后接“0N) ”) {JOIN('change_log_head')} 行——98 标准 {V('change_log_head', 1)} 行自我说明, 另四份 0 行; 附录标题行命中 {JOIN('clo_found')} 份, 行号 {JOIN('clo_line')}。"
     u"章节号行 {JOIN('sec_head')} 行 ⇎ 去重 {JOIN('sec_head_d')} 个; “section 数字”引用 {JOIN('section_cite')} 处; RFC 引用去重 {JOIN('rfc_ref_n')} 枚。"
     u"“Standards Track”印记 {JOIN('stds_stmt')} 处 ⇎ 抬头类目行 {JOIN('category_std')} 行 ⇎ “Experimental”字样 {JOIN('category_exp')} 处: 五份面内一个实验轨标记都没有, "
     u"连把上限写成 {D_max} 的超大包档也只印标准轨——类目由抬头一行给死, 正文不复述。")

LINE(u'⇄', u"整行搬运(行长 ≥40 且归一化非空, 排序后两指针求交): 95⇎98 {V('share_AB')} 行 ⇎ 98⇎17 {V('share_BC')} 行 ⇎ 95⇎17 {V('share_AC')} 行 ⇎ 95⇎超大包 {V('share_AD')} 行 ⇎ 98⇎超大包 {V('share_BD')} 行 ⇎ 17⇎超大包 {V('share_CD')} 行 ⇎ 17⇎PMTUD {V('share_CE')} 行; "
     u"三份同现 {V('AB_C_inter')} 行, 三份并集 {V('union_ABC')} 行, 只在本代 95 {V('only_A')} ⇎ 98 {V('only_B')} ⇎ 17 {V('only_C')} 行; 容斥闭合 {CLOS('abc_close', '三代容斥闭合')}。候选行集大小 {JOIN('lines_ge40')}。"
     u"17 现行与超大包档整行共用 {V('share_CD')} 行、与 PMTUD 档只共用 {V('share_CE')} 行——它换了抬头与页宽排版, 而 §5 那句 1280 要求与 98 标准逐字同现(归一化后同为共用行)。"
     u"含关键数字的长行(≥55 字符) 95 {V('num-lines_A')} ⇎ 98 {V('num-lines_B')} ⇎ 17 {V('num-lines_C')} ⇎ 超大包 {V('num-lines_D')} ⇎ PMTUD {V('num-lines_E')} 行——PMTUD 档一行也没有: 它的每一个 MTU 数都指回别的文书。")

LINE(u'ℒ', u"方法 ⇒ 面对“同一问题五份文书”, 先问答案由哪个句式给出: 本条把下限做成“every link … have an MTU of × 数字 × octets or greater”谓词, 于是“还要不要 576”有可判口径({JOIN('floor_vals')} 现读), "
     u"而“576 这个词还在不在”是另一回事({JOIN('lit_576')} 处, 再按窗口分正文⇎变更记录两档)。其次把窗口判据定死在字节上: 附录标题按整行扫、取最后一处命中, 因为目录页也印着同一枚标题——{V('clo_line', 2)} 行才是 17 现行的附录起点, 取首处会读出 {V('body_1280', 2)} 处为零的假象。"
     u"再次把量测自身的失败做成键: 原面⇎折平两档的差({JOIN('wrap_gap_routers')}⇎{JOIN('wrap_gap_1280_oct')}⇎{JOIN('wrap_gap_jumbo_opt')})逐档登记, 分片主语句“后半截查无”因此在库里可复算, 不靠注释解释; "
     u"数 token 的后邻符号分档相加闭合({V('sk_576_close', 0, '576 分档闭合·95 初版')}⇎{V('sk_1280_close', 1, '1280 分档闭合·98 标准')}⇎{V('sk_c65535_close', 3, '千分位分档闭合·超大包档')}), 两窗相减闭合({V('close_576', 1)}⇎{V('close_Jumbo', 1)}), 容斥闭合({V('abc_close')})——恒零项也占键位, 读得出“这里本可能出错”。"
     u"义务词全大写档与分片主语句同为“定义上该有、字面上全无”: 前者五份 {JOIN('u_must')} 处, 后者原面 {JOIN('s_routers')} 处, 两者都不是漏读, 而是体例与排版的真实状态。")

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 五源各 {JOIN('chars')} 字符, 窗口只能取锚点触到的行; 本条的结论几乎全是跨文书的量: "
     u"下限句集要三份标准并排({V('floor_vals_A', None)}⇎{V('floor_vals_B', None)}⇎{V('floor_vals_C', None)}), 墓碑判读要把同一数按两窗分档(576 正文 {V('body_576', 1)} ⇎ 变更记录 {V('tail_576', 1)}), "
     u"超大包命运要四个位置并排(选项定义 {JOIN('jumbo_option_def')} ⇎ 移除说明 {JOIN('remove_note')} ⇎ 实验档 {V('jumbo_ci', 3)} 处), 值域写法要逗号档与无逗号档各数一遍({JOIN('lit_c65535')} ⇎ {JOIN('lit_65535')}), "
     u"容斥要三份行集全量({V('union_ABC')} 行)。尤其“三份文书逐字同写‘分片只由源节点做, 不由路由器做’, 而后半截在每一份里都被折到下一行”这一条, 任何单源单档量测都看不见——"
     u"它要原面档 {V('s_routers', 1)} 处与折平档 {V('w_routers', 1)} 处同时成立才读得出来。读它请按“这个数由哪份文书、以哪个句式、落在正文还是变更记录里给出”来读, 而不是按“少抄了多少原文”。", **{})

assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCH if 1 < len(HITC[a]) < NSRC]),
       u'all5': len([a for a in ANCH if len(HITC[a]) == NSRC])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'],
         u'anchor_all5': CLS[u'all5'], u'checks': DIST * NSRC}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all5'] == DIST
for n, v in sorted(AMETA.items()):
    reg(str(v), u"%s('%s')" % (FN, n), TOKV.get(n, n))
for n in AMETA:
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
assert u'◘' not in body, u'锚统计量占位符未回填'
for n, v in AMETA.items():
    F[n] = v
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv61.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b61flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms61.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[' + u''.join(TAGS) + u']⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == n]))
                       for c, n in ((u'single', 1), (u'two', 2), (u'three', 3),
                                    (u'four', 4), (u'five', 5))),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
      u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': NSRC, u'flat': F,
      u'closure_keys': [k for k in F if k.endswith(u'close')]}
json.dump(CH, io.open(u'corpus/_b61checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 字符／非空行 %d／下限句 %d 处／576×1280 %d⇎%d 处)' % (
        os.path.basename(PATH[i]), F[u'bytes'][i], F[u'chars'][i], F[u'nonblank'][i],
        F[u'minmtu_sent'][i], F[u'lit_576'][i], F[u'lit_1280'][i]) for i in range(NSRC)) +
    u' (五份 RFC Editor 纯文本面, 全 LF、全 ASCII。数字一律从面内现读, 一个都不手填; 抓取时刻、官网现行状态与勘误表是否已挂新版只在本机或站外成立, 不进门槛)\n')
联结 = (u"；联结不是“同一份数据的两种序列化”, 而是“一条链路至少要装多少字节、一个包最大能多大”在五份一手规范里的五种答法: "
        u"下限句现读 95 初版 %s ⇎ 98 标准 %s ⇎ 17 现行 %s ⇎ 超大包档 %s ⇎ PMTUD 档 %s; "
        u"576 字面 %d⇎%d⇎%d⇎%d⇎%d 处 ⇎ 1280 %d⇎%d⇎%d⇎%d⇎%d 处, 而 98 标准那一枚 576 只活在变更记录窗 %d 处(正文 %d 处): 那句“把最小 MTU 从 576 改成 1280”就是它的全部残留; "
        u"净载荷算式成对读数 %s⇎%s⇎%s; 包顶写法只有带千分位一种: 65,535 %d⇎%d⇎%d⇎%d⇎%d 处 ⇎ 无逗号 65535 全库 0, 超大包档另给 4,294,967,295 %d 处; "
        u"超大包选项: 定义逐字面 %d⇎%d⇎%d⇎%d⇎%d 处 ⇎ jumbo 全族 %d⇎%d⇎%d⇎%d⇎%d 处, 98 标准用一句 %d 处“全部移除”说明它; "
        u"分片主语三份逐字同现(原面搜后半截 0 处 ⇎ 折平 1⇎1⇎1 处); 义务词体例: 全大写 MUST/SHOULD/MAY 五份 0⇎0⇎0⇎0⇎0 处, 小写 must %d⇎%d⇎%d⇎%d⇎%d 处, PMTUD 档两处自陈“只用小写、不引 2119 定义”(2119 引用 %d 次); "
        u"整行共用 95⇎98 %d 行 ⇎ 98⇎17 %d 行 ⇎ 17⇎超大包 %d 行 ⇎ 三份同现 %d 行。\n") % (
    u','.join(F[u'floor_vals'][0]) or u'无', u','.join(F[u'floor_vals'][1]) or u'无',
    u','.join(F[u'floor_vals'][2]) or u'无', u','.join(F[u'floor_vals'][3]) or u'无',
    u','.join(F[u'floor_vals'][4]) or u'无',
    F[u'lit_576'][0], F[u'lit_576'][1], F[u'lit_576'][2], F[u'lit_576'][3], F[u'lit_576'][4],
    F[u'lit_1280'][0], F[u'lit_1280'][1], F[u'lit_1280'][2], F[u'lit_1280'][3], F[u'lit_1280'][4],
    F[u'tail_576'][1], F[u'body_576'][1],
    u'/'.join(F[u'pfloor_pair'][0][0]) if F[u'pfloor_pair'][0] else u'无',
    u'/'.join(F[u'pfloor_pair'][1][0]) if F[u'pfloor_pair'][1] else u'无',
    u'无' if not F[u'pfloor_pair'][2] else u'/'.join(F[u'pfloor_pair'][2][0]),
    F[u'lit_c65535'][0], F[u'lit_c65535'][1], F[u'lit_c65535'][2], F[u'lit_c65535'][3],
    F[u'lit_c65535'][4], F[u'lit_c4294967295'][3],
    F[u'jumbo_option_def'][0], F[u'jumbo_option_def'][1], F[u'jumbo_option_def'][2],
    F[u'jumbo_option_def'][3], F[u'jumbo_option_def'][4],
    F[u'jumbo_ci'][0], F[u'jumbo_ci'][1], F[u'jumbo_ci'][2], F[u'jumbo_ci'][3], F[u'jumbo_ci'][4],
    F[u'remove_note'][1],
    F[u'l_must'][0], F[u'l_must'][1], F[u'l_must'][2], F[u'l_must'][3], F[u'l_must'][4],
    F[u'rfc2119_ref'][4],
    F[u'share_AB'], F[u'share_BC'], F[u'share_CD'], F[u'AB_C_inter'])
title = (u'# B61 一条链路至少要装多少字节、一个 IPv6 包最大能多大，五份规范五种答法：576 ⇎ 1280 ⇎ 只留一句“已改成 1280” ⇎ 拆掉 65 535 上限 ⇎ 通篇不提任何下限（下限句 %d⇎%d⇎%d 句，%d 处读数被排版折行）\n' % (
    F[u'minmtu_sent'][0], F[u'minmtu_sent'][1], F[u'minmtu_sent'][2], sum(F[u'wrap_gap_routers'])))
text = (title + srcline + 联结 +
        u'tags: 最小链路 MTU 句式谓词 正文⇎变更记录两窗分档 数 token 后邻符号分档闭合 带千分位⇎无逗号两档 '
        u'超大包定义⇎自我移除⇎实验档接走 原面⇎折平双档(分片后半截查无) 全大写义务词五份皆零 小写自陈体例 '
        u'整行容斥 无一下限数字的 MTU 专文 锚归属由正文现推 闭合账 标量 %d⇎清单 %d 项\n' % (F[u'scalar_clos_n'], F[u'list_clos_n']) +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill61.py 从 corpus/_b61checks.json 与 corpus/_deriv61.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两至四源 %d ⇎ 五源 %d ⇎ 错配 %d ｜ 池内取用 %d／池 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all5'], len(ERR), CH[u'pool_used'], F[u'pool_n']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(F)))
print(u'闭合键 %d 项 ⇎ 非零 %d ｜ 附录行号 %s ⇎ 576 两窗 %s⇎%s ⇎ 1280 两窗 %s⇎%s' % (
    F[u'scalar_clos_n'], len([k for k in F[u'scalar_clos_list'] if F[k] != 0]), F[u'clo_line'],
    F[u'body_576'], F[u'tail_576'], F[u'body_1280'], F[u'tail_1280']))
print(u'折行差 %s ⇎ 义务小写 %s ⇎ 全大写 %s ⇎ 整行 95⇎98 %d ⇎ 98⇎17 %d ⇎ 容斥闭合 %d' % (
    [F[u'wrap_gap_routers'][i] + F[u'wrap_gap_1280_oct'][i] + F[u'wrap_gap_jumbo_opt'][i] for i in range(NSRC)],
    F[u'l_must'], F[u'u_must'], F[u'share_AB'], F[u'share_BC'], F[u'abc_close']))
MEASP = u'corpus/_b61meas.json'
if os.path.exists(MEASP):
    M = json.load(io.open(MEASP, encoding='utf-8'))
    PL = tuple(M.pop(u'_plain_idx', [0, 1, 2, 3, 4]))
    TIE = []
    for k in sorted(M):
        if k not in F:
            TIE.append((k, u'建条目侧无此键'))
            continue
        got = [F[k][i] for i in PL] if isinstance(F[k], list) and len(F[k]) == NSRC else F[k]
        if got != M[k]:
            TIE.append((k, u'建=%s 采=%s' % (got, M[k])))
    print(u'两侧对账(五份纯文本面): 共有键 %d ／ 不符 %d ｜ %s' % (len(M), len(TIE), TIE[:8]))
else:
    print(u'两侧对账: 无 corpus/_b61meas.json(采集侧未跑)')
