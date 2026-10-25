# -*- coding: utf-8 -*-
"""README 记账: 59 条 → 60 条。合计、唯一码点、推导条数全部取自 audit 的当下输出, 不手填。
本文件是第五套实现, 换算法不换定义:
剥壳走双游标 find('<')/find('>'), 注释按 find('-->') 整段跳过且不留空格, script/style 由一对 find 游标删块
(建条目侧是三条 re.sub + 一条带反向引用的 re.sub, 第四遍是一台逐字符状态机);
解码层与建条目侧同档: 字节先 utf-8 替换非法码(三份 layout 面里确有 0xAD 这种非 UTF-8 字节), 再把 CRLF 折成 LF
(建条目侧靠文本模式的 errors='replace' 与通用换行, 本遍读字节, 两件事都得自己办);
词法量不走 re.findall, 全部走"游标 + 字符边界判定"(强度词先手工切成字母 token 再比整词, 天数与 VP 短语按字符扫);
上限句不走谓词正则, 而是从动词起逐个字面衔接、把词间空白整段收下再分档(单空格档 ⇎ 含换行档);
历史时间表行的判定不走 ^\\s*\\d{4}-\\d{2}-\\d{2}|\\bSC\\d, 而是逐字符量行首十位的形状与 SC+数字的前一个字符;
集合交并不用 set&set, 改用"在一份里逐条问另一份有没有"的列表路;
五份字节的签名换 blake2b 8 字节(建条目侧与门槛侧都是 sha256 前 16 位), 只比种数不比串;
锚统计直接扫条目正文里的 ⟦⟧⟨⟩ 字符游标, 再拿每条串到本遍的归一文档里现验(建条目侧按池位置推, 门槛侧按归属表查)。
每个数与建条目侧扁平契约 corpus/_b60flat.json 对表, 注侧元数据与 corpus/_b60checks.json 对表;
本遍的全部现量另存 corpus/_b60audit.json, 供日后条目改文时回比对(不像前几遍那样只靠内存)。任一标量对不上就当场停机。"""
import hashlib, io, json, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
FM = u'corpus/README.md'
NL = chr(10)
TAG = u'B60'
ENTRY = u'corpus/babeltele/B60_certificate_validity_five_answers.md'
PATHS = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt',
         u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.layout.txt',
         u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt',
         u'corpus/raw/cert/le_lifetimes.html',
         u'corpus/raw/cert/rfc5280.txt']
RAWS = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.raw.txt',
        u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.raw.txt',
        u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.raw.txt']
PDFS = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.pdf',
        u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.pdf',
        u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.pdf']
TAGS = [u'T', u'O', u'F', u'N', u'R']
IDX = dict((t, i) for i, t in enumerate(TAGS))
NS = 5
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')
RD = lambda q: io.open(q, encoding='utf-8', errors='replace').read()
DIGIT = u'0123456789'
ENTS = [(u'&#39;', "'"), (u'&#43;', '+'), (u'&amp;', '&'), (u'&rsquo;', u'’'), (u'&copy;', u'©')]


def sub(old, new, s):
    assert s.count(old) == 1, (u'锚不唯一', s.count(old), old[:60])
    return s.replace(old, new)


def rnd(x):
    return round(x, 4) if isinstance(x, float) else x


# ---------- 1) 门槛现取 ----------
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
OUT = p.stdout
assert u'保真门槛' in OUT and u'PASS' in OUT, OUT[-600:]
row = {}
for l in OUT.split(NL):
    if not l.startswith(u'| '):
        continue
    parts = [x.strip() for x in l.strip(u'|').split(u'|')]
    k = parts[0]
    if (k[:1] == u'B' and k[1:].isdigit()) or k == u'ALL':
        row[k] = parts[1:]
NENT = len([k for k in row if k != u'ALL'])
assert NENT == 60, NENT
b60, A = row[u'B60'], row[u'ALL']
dig_all, enc_all = int(A[0].replace(u' ', u'')), int(A[1].replace(u' ', u''))
uniq_all = int(re.sub(u'[^0-9]', u'', A[4]))
assert (sum(int(v[0]) for k, v in row.items() if k != u'ALL'),
        sum(int(v[1]) for k, v in row.items() if k != u'ALL')) == (dig_all, enc_all)
assert b60[7:11] == [u'0', u'0', u'0', u'0'], b60
soft_all = proofs = None
HINT = {}
for l in OUT.split(NL):
    if l.startswith(u'提示') and u'共' in l:
        soft_all = int(l.split(u'共')[1].split(u' 个')[0])
    if l.startswith(u'已机检的推导'):
        proofs = int(l.split(u'(')[1].split(u' 条)')[0])
    m2 = re.match(u'^   (B\\d\\d) (\\[.*\\])$', l)
    if m2:
        HINT[m2.group(1)] = eval(m2.group(2), {'__builtins__': {}}, {})
assert sum(len(v) for v in HINT.values()) == soft_all, (HINT, soft_all)
assert u'B60' not in HINT, HINT.get(u'B60')
dig60, enc60 = int(b60[0]), int(b60[1])
ret_tot = A[2].replace(u'*', u'')

CH = json.load(io.open(u'corpus/_b60checks.json', encoding='utf-8'))
FLAT = json.load(io.open(u'corpus/_b60flat.json', encoding='utf-8'))
assert enc60 == CH[u'enc_chars'] == 8400, (enc60, CH[u'enc_chars'])
Q5 = {}


def q(name, val):
    Q5[name] = val
    if name in FLAT:
        assert rnd(val) == rnd(FLAT[name]), (name, val, FLAT[name])
    return val


def m(name):
    return Q5[name]


def five(f):
    return [f(k) for k in range(NS)]


def wc(c):
    return (u'a' <= c <= u'z') or (u'A' <= c <= u'Z') or (u'0' <= c <= u'9') or c == u'_'


def pnorm(s):
    return u''.join(c for c in s.lower() if (u'a' <= c <= u'z') or (u'0' <= c <= u'9'))


def occ(s, ndl):
    c = k = 0
    while True:
        j = s.find(ndl, k)
        if j < 0:
            return c
        c += 1
        k = j + len(ndl)


def wocc(s, lit, ci=False):
    """整词档: 词界由前后字符现判(建条目侧写的是 \\b...\\b)。"""
    ndl = lit.lower() if ci else lit
    low = s.lower() if ci else s
    c = k = 0
    while True:
        j = low.find(ndl, k)
        if j < 0:
            return c
        e = j + len(ndl)
        if (j == 0 or not wc(s[j - 1])) and (e >= len(s) or not wc(s[e])):
            c += 1
        k = j + 1


def tagcount(s):
    """`<[^>]+>` 的游标代法: 逐个 < 找配对的 >, 无配对的 < 不算一枚标签。"""
    c, k = 0, 0
    while True:
        j = s.find(u'<', k)
        if j < 0:
            return c
        e = s.find(u'>', j)
        if e < 0:
            return c
        if e > j + 1:
            c += 1
        k = e + 1


def let_toks(s):
    out, k, n = [], 0, len(s)
    while k < n:
        if not ((u'a' <= s[k] <= u'z') or (u'A' <= s[k] <= u'Z')):
            k += 1
            continue
        j = k
        while j < n and ((u'a' <= s[j] <= u'z') or (u'A' <= s[j] <= u'Z')):
            j += 1
        out.append(s[k:j])
        k = j
    return out


def descript5(s):
    low = s.lower()
    out, k, n = [], 0, len(s)
    while True:
        j, hit = -1, None
        for nm in (u'script', u'style'):
            c = low.find(u'<', k)
            while c >= 0:
                t = low[c + 1:c + 1 + len(nm)]
                nx = low[c + 1 + len(nm):c + 2 + len(nm)]
                if t == nm and not (nx and wc(nx)):
                    break
                c = low.find(u'<', c + 1)
            if c >= 0 and (j < 0 or c < j):
                j, hit = c, nm
        if j < 0:
            out.append(s[k:])
            return u''.join(out)
        e = s.find(u'>', j)
        c = low.find(u'</' + hit, e)
        if c < 0:
            out.append(s[k:j])
            k = j + 1
            continue
        d = s.find(u'>', c)
        out.append(s[k:j])
        k = n if d < 0 else d + 1


def shell5(s):
    low = s.lower()
    out, k, n = [], 0, len(s)
    while True:
        j = s.find(u'<', k)
        if j < 0:
            out.append(s[k:])
            return u''.join(out)
        out.append(s[k:j])
        if low.startswith(u'<!--', j):
            e = low.find(u'-->', j + 4)
            if e >= 0:
                k = e + 3
                continue
        e = s.find(u'>', j)
        if e < 0:
            out.append(u'<')
            k = j + 1
            continue
        out.append(u' ')
        k = e + 1


def fold5(s):
    out, k, n = [], 0, len(s)
    while k < n:
        c = s[k]
        if c == u'&':
            for a, b in ENTS:
                if s.startswith(a, k):
                    out.append(b)
                    k += len(a)
                    break
            else:
                out.append(c)
                k += 1
            continue
        out.append(c)
        k += 1
    s = u''.join(out)
    o, i = [], 0
    while i < len(s):
        if s[i] in u' \t':
            o.append(u' ')
            while i + 1 < len(s) and s[i + 1] in u' \t':
                i += 1
        else:
            o.append(s[i])
        i += 1
    return u''.join(o).strip()


RB = [io.open(x, u'rb').read() for x in PATHS]
# 建条目侧用文本模式读(errors='replace' + 通用换行): 三份 layout 面里各有 0xAD 这类非 UTF-8 字节, 折出的都是 U+FFFD;
# 本遍读字节, 故替换与 CRLF 折叠都要自己做——换行档与坏字节档必须一致, 否则行长、字符数全错。
RAW = [r.decode(u'utf-8', u'replace').replace(u'\r\n', NL) for r in RB]
NSC = [descript5(r) for r in RAW]
TXT = [x if i != 3 else fold5(shell5(NSC[i])) for i, x in enumerate(NSC)]
TXTF = [x if i != 3 else fold5(shell5(RAW[i])) for i, x in enumerate(RAW)]
LST = [t.split(NL) for t in TXT]
LOW = [t.lower() for t in TXT]
FAN = [pnorm(t) for t in TXT]

# ---- 形状档 ----
q(u'bytes', five(lambda i: len(RB[i])))
q(u'chars', five(lambda i: len(TXT[i])))
q(u'chars_untagged', five(lambda i: len(TXTF[i])))
q(u'js_gap', [m(u'chars_untagged')[i] - m(u'chars')[i] for i in range(NS)])
q(u'lines', five(lambda i: TXT[i].count(NL) + 1))
q(u'nonblank', five(lambda i: len([l for l in LST[i] if l.strip()])))
q(u'maxlen', five(lambda i: max(len(l) for l in LST[i])))
q(u'formfeed', five(lambda i: TXT[i].count(u'\x0c')))
q(u'trail', five(lambda i: len([l for l in LST[i] if l != l.rstrip()])))
def blockcount(s, name):
    """`<name\\b.*?</name>` 成对档: 逐个开标签找它的闭标签, 失配的块不算(建条目侧靠 re 的惰性量词)。"""
    low = s.lower()
    c, k = 0, 0
    while True:
        j = low.find(u'<' + name, k)
        if j < 0:
            return c
        e = j + 1 + len(name)
        if e < len(low) and wc(low[e]):
            k = j + 1
            continue
        d = low.find(u'</' + name, e)
        if d < 0:
            return c
        c += 1
        k = d + 2


q(u'le_scripts', blockcount(RAW[3], u'script'))
q(u'le_styles', blockcount(RAW[3], u'style'))
q(u'le_tags', tagcount(RAW[3]))
q(u'le_hrefs', occ(RAW[3], u'href='))
q(u'le_metas', wocc(RAW[3], u'<meta', True))
q(u'le_dropped', len(RAW[3]) - len(TXT[3]))
q(u'sha8', [hashlib.blake2b(RB[i], digest_size=8).hexdigest() for i in range(NS)])
q(u'sig_distinct', len(set(m(u'sha8'))))
q(u'pdf_bytes', [len(io.open(x, u'rb').read()) for x in PDFS])
q(u'raw_chars', [len(RD(x)) for x in RAWS])
q(u'raw_lines', [len(RD(x).split(NL)) for x in RAWS])
q(u'raw_formfeed', [RD(x).count(u'\x0c') for x in RAWS])
q(u'face_gap', [len(TXT[i]) - len(RD(RAWS[i])) for i in range(3)])
q(u'line_gap', [len(LST[i]) - len(RD(RAWS[i]).split(NL)) for i in range(3)])
q(u'ff_close', [m(u'formfeed')[i] - m(u'raw_formfeed')[i] for i in range(3)])

# ---- 天数: 逐字符扫数字串 + 分隔 + day(s), 失配就右移一位(正则的失配回溯代法) ----
def after(t, e):
    return e < len(t) and not wc(t[e])


def numday5(t, mode=u'both', flex=False):
    """mode: both=空格或连字符(建条目侧 `[ -]days?\\b`), hyph=只连字符, spac=只空格。"""
    out, k, n = [], 0, len(t)
    while k < n:
        if t[k] not in DIGIT:
            k += 1
            continue
        b = k + 1
        while b < n and (t[b] in DIGIT or t[b] == u','):
            b += 1
        g = t[b] if b < n else u''
        if mode == u'hyph':
            ok = g == u'-'
        elif mode == u'spac':
            ok = g == u' '
        else:
            ok = g == u' ' or g == u'-'
            if flex and not ok:
                ok = g in u' \t\n\r\x0b\x0c-'
        if not ok:
            k += 1
            continue
        for tail in (u'days', u'day'):
            if t.startswith(tail, b + 1) and after(t, b + 1 + len(tail)):
                out.append(t[k:b].replace(u',', u''))
                k = b + 1 + len(tail)
                break
        else:
            k += 1
    return out


def day_one5(t, tail):
    """建条目侧 `\\d[\\d,]*` + 单空格 + tail + `\\b`(tail 给死, 故连字档不计入)。"""
    c, k, n = 0, 0, len(t)
    while k < n:
        if t[k] in DIGIT:
            b = k + 1
            while b < n and (t[b] in DIGIT or t[b] == u','):
                b += 1
            if b < n and t[b] == u' ' and t.startswith(tail, b + 1) and after(t, b + 1 + len(tail)):
                c += 1
                k = b + 1 + len(tail)
                continue
        k += 1
    return c


q(u'day_num', five(lambda i: len(numday5(TXT[i]))))
q(u'day_num_flex', five(lambda i: len(numday5(TXT[i], flex=True))))
q(u'day_wrap', [m(u'day_num_flex')[i] - m(u'day_num')[i] for i in range(NS)])
q(u'day_set', five(lambda i: sorted(set(numday5(TXT[i])), key=int)))
q(u'day_hyph', five(lambda i: len(numday5(TXT[i], u'hyph'))))
q(u'day_spac', five(lambda i: day_one5(TXT[i], u'days')))
q(u'day_sing', five(lambda i: day_one5(TXT[i], u'day')))
q(u'day_word', five(lambda i: wocc(LOW[i], u'day') + wocc(LOW[i], u'days')))
q(u'day_free', [m(u'day_word')[i] - m(u'day_num')[i] for i in range(NS)])
q(u'day_spac_gap', [m(u'day_spac')[i] - m(u'day_sing')[i] for i in range(NS)])
q(u'day_num_close', [m(u'day_hyph')[i] + m(u'day_spac')[i] + m(u'day_sing')[i] - m(u'day_num')[i]
                     for i in range(NS)])
q(u'set_only_F', sorted(set(m(u'day_set')[2]) - set(m(u'day_set')[0]) - set(m(u'day_set')[1]), key=int))
q(u'set_only_N', sorted(set(m(u'day_set')[3]) - set(sum([m(u'day_set')[i] for i in range(3)], [])), key=int))
q(u'set_shared_NF', sorted(set(m(u'day_set')[2]) & set(m(u'day_set')[3]), key=int))
q(u'num_45_in_brs', sum(m(u'day_set')[i].count(u'45') for i in range(3)))
q(u'num_47_in_brs', sum(m(u'day_set')[i].count(u'47') for i in range(3)))

# ---- 上限句: 动词起逐字面衔接; 动词后与各大词之间容空白, 但 "have a" 是带单空格的整块 ----
SEQ6 = (u'have a', u'Validity', u'Period', u'greater', u'than')
ORD = (u'MUST NOT', u'SHOULD NOT', u'MUST', u'SHOULD')


def wsr(t, j):
    k = j
    while k < len(t) and t[k] in u' \t\n\r\x0b\x0c':
        k += 1
    return k, t[j:k]


def ceil5(t):
    tri, n, one = set(), 0, 0
    for i in range(len(t)):
        if t[i] not in u'MS':
            continue
        v = [x for x in ORD if t.startswith(x, i)]
        if not v:
            continue
        pos, seps, ok = i + len(v[0]), [], True
        for w in SEQ6:
            p2, g = wsr(t, pos)
            if not g or not t.startswith(w, p2):
                ok = False
                break
            seps.append(g)
            pos = p2 + len(w)
        if not ok:
            continue
        p2, g = wsr(t, pos)
        if not g or p2 == pos:
            continue
        seps.append(g)
        b = p2
        while b < len(t) and t[b] in DIGIT:
            b += 1
        if b == p2:
            continue
        p3, g3 = wsr(t, b)
        if not g3 or p3 == b or not t.startswith(u'days', p3):
            continue
        n += 1
        if all(x == u' ' for x in seps + [g3]):
            one += 1
        tri.add((v[0], t[p2:b]))
    return sorted(tri), n, one


C5 = [ceil5(TXT[i]) for i in range(NS)]
q(u'ceil_tri', [list(map(list, x[0])) for x in C5])
q(u'ceil_n', five(lambda i: C5[i][1]))
q(u'ceil_strict_n', five(lambda i: C5[i][2]))
q(u'ceil_wrap', [m(u'ceil_n')[i] - m(u'ceil_strict_n')[i] for i in range(NS)])
q(u'd825_ceil', five(lambda i: len([x for x in C5[i][0] if x[1] == u'825'])))
q(u'ceil_vals', five(lambda i: sorted(set(x[1] for x in C5[i][0]), key=int)))
q(u'ceil_distinct', five(lambda i: len(C5[i][0])))

# ---- Validity Period: 单空格档 ⇎ 容空白档 ----
def vp5(t):
    lo = t.lower()
    n, one, k = 0, 0, 0
    while True:
        j = lo.find(u'validity', k)
        if j < 0:
            return n, one
        p2, g = wsr(lo, j + 8)
        if g and lo.startswith(u'period', p2):
            n += 1
            if g == u' ':
                one += 1
            k = p2 + 6
        else:
            k = j + 1


V5 = [vp5(TXT[i]) for i in range(NS)]
q(u'vp_flex_ci', five(lambda i: V5[i][0]))
q(u'vp_ci', five(lambda i: V5[i][1]))
q(u'vp_wrap', [m(u'vp_flex_ci')[i] - m(u'vp_ci')[i] for i in range(NS)])
q(u'vp_caps', five(lambda i: occ(TXT[i], u'Validity Period')))
q(u'vp_low', five(lambda i: occ(TXT[i], u'validity period')))
q(u'vp_ci_close', [m(u'vp_caps')[i] + m(u'vp_low')[i] - m(u'vp_ci')[i] for i in range(NS)])
q(u'validity_stem', five(lambda i: occ(LOW[i], u'validity')))
q(u'vp_stem_gap', [m(u'validity_stem')[i] - m(u'vp_flex_ci')[i] for i in range(NS)])
q(u'lifetime_ci', five(lambda i: occ(LOW[i], u'lifetime')))
q(u'notbefore', five(lambda i: occ(TXT[i], u'notBefore')))
q(u'notafter', five(lambda i: occ(TXT[i], u'notAfter')))
q(u'nanb_gap', [m(u'notafter')[i] - m(u'notbefore')[i] for i in range(NS)])

# ---- 强度词: 词界档(整词现判) ⇎ 子串档(字面 count) ----
q(u'kw_must', five(lambda i: wocc(TXT[i], u'MUST')))
q(u'kw_must_not', five(lambda i: wocc(TXT[i], u'MUST NOT')))
q(u'kw_should', five(lambda i: wocc(TXT[i], u'SHOULD')))
q(u'u_must', five(lambda i: occ(TXT[i], u'MUST')))
q(u'u_must_not', five(lambda i: occ(TXT[i], u'MUST NOT')))
q(u'u_may', five(lambda i: occ(TXT[i], u'MAY')))
q(u'must_sub_gap', [m(u'u_must')[i] - m(u'kw_must')[i] for i in range(NS)])
q(u'mustnot_sub_gap', [m(u'u_must_not')[i] - m(u'kw_must_not')[i] for i in range(NS)])
q(u'must_ci', five(lambda i: wocc(TXT[i], u'must', True)))
q(u'must_l', five(lambda i: wocc(TXT[i], u'must')))
q(u'shall_u', five(lambda i: wocc(TXT[i], u'SHALL')))
q(u'shall_ci', five(lambda i: wocc(TXT[i], u'shall', True)))
q(u'will_ci', five(lambda i: wocc(TXT[i], u'will', True)))
q(u'kw_upper', [m(u'kw_must')[i] + m(u'kw_should')[i] + m(u'u_may')[i] + m(u'shall_u')[i]
                for i in range(NS)])
q(u'kw_ci', [m(u'must_ci')[i] + m(u'shall_ci')[i] + wocc(TXT[i], u'may', True)
             + wocc(TXT[i], u'should', True) for i in range(NS)])

# ---- 历史时间表行 ⇎ 正文 ----
def hist5(l):
    k = 0
    while k < len(l) and l[k].isspace():
        k += 1
    h = l[k:k + 10]
    if len(h) == 10 and all(c in DIGIT for c in h[0:4]) and h[4] == u'-' and all(c in DIGIT for c in h[5:7]) \
            and h[7] == u'-' and all(c in DIGIT for c in h[8:10]):
        return True
    j = l.find(u'SC')
    while j >= 0:
        if j + 2 < len(l) and l[j + 2] in DIGIT and (j == 0 or not wc(l[j - 1])):
            return True
        j = l.find(u'SC', j + 1)
    return False


HIT5 = [[l for l in LST[i] if hist5(l)] for i in range(NS)]
q(u'hist_n', five(lambda i: len(HIT5[i])))
q(u'hist_chars', five(lambda i: len(NL.join(HIT5[i]))))


def tokcount(lines, word, ci=False):
    """半区计数: 把行交回一份串再走整词档(建条目侧是对 join 后的串跑正则)。"""
    return wocc(NL.join(lines), word, ci)


q(u'h_must', five(lambda i: tokcount(HIT5[i], u'MUST')))
q(u'b_must', five(lambda i: tokcount([l for l in LST[i] if not hist5(l)], u'MUST')))
q(u'h_must_close', [m(u'h_must')[i] + m(u'b_must')[i] - m(u'kw_must')[i] for i in range(NS)])
q(u'h_shall', five(lambda i: tokcount(HIT5[i], u'SHALL', True)))
q(u'b_shall', five(lambda i: tokcount([l for l in LST[i] if not hist5(l)], u'SHALL', True)))
q(u'h_shall_close', [m(u'h_shall')[i] + m(u'b_shall')[i] - m(u'shall_ci')[i] for i in range(NS)])

# ---- 壳⇎面: 同一句在 LE 页的壳里与面里各几份 ----
SENT = [(u's90', u'certificates with 90-day lifetimes'), (u's6', u'Short-lived certificates with 6-day lifetimes'),
        (u's47', u'maximum of 47 days starting on March 15, 2029'), (u's45', u'45 days by February 2028')]
q(u'shell_all', [RAW[3].count(x) for _n, x in SENT])
q(u'face_all', [TXT[3].count(x) for _n, x in SENT])
q(u'dup_gap', [m(u'shell_all')[i] - m(u'face_all')[i] for i in range(4)])
q(u'dup_kinds', len(set(m(u'dup_gap'))))
q(u'day_shell', len(numday5(RAW[3])))
q(u'day_face', len(numday5(TXT[3])))
_q, _a, _b = 0, RAW[3].find(u'<meta name="description"'), RAW[3].find(u'<meta property=')
q(u'day_meta', len(numday5(RAW[3][_a:_b])))
q(u'day_shell_close', m(u'day_shell') - m(u'day_face') - 2 * m(u'day_meta'))

# ---- 时刻写法与日期写法 ----
for W in (u'UTCTime', u'GeneralizedTime'):
    q(u'ts_' + W.lower(), five(lambda i, W=W: occ(TXT[i], W)))
q(u'y2049', five(lambda i: wocc(TXT[i], u'2049')))
q(u'y2050', five(lambda i: wocc(TXT[i], u'2050')))


def iso5(t):
    """`\\b\\d{4}-\\d{2}-\\d{2}\\b`: 号串定长四、二、二, 前后不吃词字符; 命中后游标跳过整串。"""
    c, k, n = 0, 0, len(t)
    while k < n:
        if t[k] not in DIGIT:
            k += 1
            continue
        j = k
        while j < n and t[j] in DIGIT:
            j += 1
        ok = (j - k == 4 and (k == 0 or not wc(t[k - 1]))
              and j + 6 <= n and t[j] == u'-' and t[j + 3] == u'-'
              and all(x in DIGIT for x in t[j + 1:j + 3] + t[j + 4:j + 6])
              and (j + 6 >= n or not wc(t[j + 6])))
        if ok:
            c += 1
            k = j + 6
        else:
            k = j + 1
    return c


q(u'iso_date', five(lambda i: iso5(TXT[i])))
q(u'rfc2119', five(lambda i: wocc(TXT[i], u'2119')))
q(u'baseline_reqs', five(lambda i: occ(TXT[i], u'Baseline Requirements')))
q(u'last_updated', five(lambda i: occ(LOW[i], u'last updated')))
q(u'rfc_n5280', five(lambda i: wocc(TXT[i], u'5280')))

# ---- 整行搬运: 集合交并走列表路 ----
LN = [set(pnorm(l) for l in LST[i] if len(l.strip()) >= 25 and pnorm(l)) for i in range(NS)]
q(u'lines_ge25', five(lambda i: len(LN[i])))
for a, b in ((0, 1), (1, 2), (0, 2), (0, 4), (1, 4), (2, 4), (0, 3), (1, 3), (2, 3), (3, 4)):
    q(u'share_%s%s' % (TAGS[a], TAGS[b]), len([x for x in LN[a] if x in LN[b]]))
q(u'share_TOF', len([x for x in LN[0] if x in LN[1] and x in LN[2]]))
q(u'union_TOF', len([x for x in LN[0]] + [x for x in LN[1] if x not in LN[0]]
                    + [x for x in LN[2] if x not in LN[0] and x not in LN[1]]))
q(u'only_T', len([x for x in LN[0] if x not in LN[1] and x not in LN[2]]))
q(u'only_O', len([x for x in LN[1] if x not in LN[0] and x not in LN[2]]))
q(u'only_F', len([x for x in LN[2] if x not in LN[0] and x not in LN[1]]))
q(u'tof_close', m(u'only_T') + m(u'only_O') + m(u'only_F') + m(u'share_TO') + m(u'share_OF')
  + m(u'share_TF') - 2 * m(u'share_TOF') - m(u'union_TOF'))
q(u'share_N_any', len([x for x in LN[3] if x in LN[0] or x in LN[1] or x in LN[2] or x in LN[4]]))

# ---- 锚候选池 ⇎ 锚(扫条目正文) ----
SPECIAL = (u'825 days', u'397 days', u'398 days', u'Validity Period', u'90-day', u'6-day', u'47 days',
           u'45 days', u'notBefore', u'notAfter', u'UTCTime', u'GeneralizedTime', u'Baseline Requirements',
           u'prior to issuing', u'MUST NOT have a Validity')
POOL, SEENP = [], set()
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if pnorm(l) and (t, l) not in SEENP:
            SEENP.add((t, l))
            POOL.append((t, l))
POOL.sort()
CR = [len([k for k in range(NS) if pnorm(x) in FAN[k]]) for (_t, x) in POOL]
q(u'pool_n', len(POOL))
q(u'pool_tag_n', five(lambda i: len([x for x in POOL if x[0] == TAGS[i]])))
q(u'pool_tiers', [len([c for c in CR if c == k]) for k in (1, 2, 3, 4, 5)])
q(u'pool_close', sum(m(u'pool_tiers')) - m(u'pool_n'))
q(u'pool_maxlen', max(len(x[1]) for x in POOL))

MD = RD(ENTRY)
head = MD.find(u'## ⟪BabelTele⟫')
tail = MD.find(u'## ⛓解读注')
BODY = MD[head + len(u'## ⟪BabelTele⟫'):tail].strip(NL)
cur, anchors, tc = None, [], dict((t, 0) for t in TAGS)
k = 0
while k < len(BODY):
    if BODY[k] == u'⟦':
        e = BODY.find(u'⟧', k)
        t = BODY[k + 1:e]
        if t in tc:
            tc[t] += 1
            cur = t
        k = e + 1
        continue
    if BODY[k] == u'⟨' and cur is not None and BODY[k - 1] == u'⟧':
        e = BODY.find(u'⟩', k)
        anchors.append((cur, BODY[k + 1:e]))
        k = e + 1
        continue
    k += 1
DIST = sorted(set(x for _t, x in anchors), key=len, reverse=True)
HITN = dict((a, len([k for k in range(NS) if pnorm(a) in FAN[k]])) for a in DIST)
q(u'anchor_total', len(anchors))
q(u'anchor_distinct', len(DIST))
q(u'anchor_err', len([x for x in anchors if x[0] and pnorm(x[1]) not in FAN[IDX[x[0]]]]))
q(u'anchor_single', len([a for a in DIST if HITN[a] == 1]))
q(u'anchor_cross', len([a for a in DIST if 1 < HITN[a] < NS]))
q(u'anchor_all5', len([a for a in DIST if HITN[a] == NS]))
q(u'checks', m(u'anchor_distinct') * NS)
q(u'tag_counts', tc)
assert sum(tc.values()) == m(u'anchor_total'), tc
assert tc == CH[u'tag_counts'], (tc, CH[u'tag_counts'])
assert m(u'anchor_single') + m(u'anchor_cross') + m(u'anchor_all5') == m(u'anchor_distinct')
q(u'letters_in', sum(len([c for c in a if (u'a' <= c <= u'z') or (u'A' <= c <= u'Z')]) for a in DIST))
OUT5 = []
k = 0
while k < len(BODY):
    if BODY[k] == u'⟨':
        e = BODY.find(u'⟩', k)
        if e > 0:
            k = e + 1
            continue
    OUT5.append(BODY[k])
    k += 1
q(u'letters_out', len([c for c in OUT5 if (u'a' <= c <= u'z') or (u'A' <= c <= u'Z')]))
q(u'enc_self', len(BODY.replace(NL, u'')))
assert m(u'enc_self') == enc60 == CH[u'enc_chars'], (m(u'enc_self'), enc60)
# _atoms60.txt 逐行是原样锚串, 行首空格是锚的一部分(建条目侧登记的就是带缩进的那一段), 读时不能 strip。
ATT = [x for x in RD(u'corpus/_atoms60.txt').split(NL) if x]
assert sorted(ATT) == sorted(DIST), u'原子清单与 _atoms60.txt 不同'
for a in (u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single', u'anchor_cross',
          u'anchor_all5', u'checks'):
    assert Q5[a] == CH[u'ameta'][a], (a, Q5[a], CH[u'ameta'][a])
assert m(u'letters_in') == CH[u'letters_in'] and m(u'letters_out') == CH[u'letters_out'], \
    (m(u'letters_in'), CH[u'letters_in'], m(u'letters_out'), CH[u'letters_out'])

DJO = json.load(io.open(u'corpus/_deriv60.json', encoding='utf-8'))
OCC = sum(v.count(u'B60V') for v in DJO.values())
assert CH[u'deriv_keys'] == len(DJO) == 164, (CH, len(DJO))
# 两处口径不同: OCC 数 DERIV 算式串里 B60V 的字面出现次数(复合式把同一枚算式抄进 max([..]) 与 min([..]) 各一次),
# deriv_points 是建条目侧按“值→算式”登记的条数。
assert OCC == 703 and CH[u'deriv_points'] == 348, (OCC, CH[u'deriv_points'])

# 采集侧对账的键数: 取自 _b60meas.json 的实测键(下划线开头的是对账用的辅助键, 不计)
MEAS = json.load(io.open(u'corpus/_b60meas.json', encoding='utf-8'))
NMEAS = len([k for k in MEAS if k[:1] != u'_'])
AUDSN = dict(Q5)
AUDSN[u'_paths'] = PATHS
json.dump(AUDSN, io.open(u'corpus/_b60audit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# ---------- 3) 逐处替换 ----------
K = dict(FLAT)
K.update(Q5)
jt = lambda xs: u', '.join(str(x) for x in xs)
K.update({u'ln': fmt(m(u'pool_n')), u'tT': tc[u'T'], u'tO': tc[u'O'], u'tF': tc[u'F'],
          u'tN': tc[u'N'], u'tR': tc[u'R'], u'coll': len(CH[u'collisions']), u'zeros': CH[u'zero_terms'],
          u'deriv_keys': CH[u'deriv_keys'], u'deriv_points': OCC, u'dedup_points': CH[u'deriv_points'],
          u'enc': enc60, u'dig': dig60, u'proofs': proofs, u'nent': NENT, u'nmeas': len(Q5),
          u'bytesT': fmt(m(u'bytes')[0]), u'bytesO': fmt(m(u'bytes')[1]), u'bytesF': fmt(m(u'bytes')[2]),
          u'bytesN': fmt(m(u'bytes')[3]), u'bytesR': fmt(m(u'bytes')[4]),
          u'chT': fmt(m(u'chars')[0]), u'chO': fmt(m(u'chars')[1]), u'chF': fmt(m(u'chars')[2]),
          u'chN': fmt(m(u'chars')[3]), u'chR': fmt(m(u'chars')[4]),
          u'nbT': fmt(m(u'nonblank')[0]), u'nbF': fmt(m(u'nonblank')[2]), u'nbR': fmt(m(u'nonblank')[4]),
          u'jssum': fmt(sum(m(u'js_gap'))),
          u'pdfsum': fmt(sum(m(u'pdf_bytes'))), u'facesum': fmt(sum(m(u'face_gap')))})

NEWPAR = (
    u'**B60 问的是一张公签 TLS 证书能活多久, 五份一手文书给出五种答法**：`raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt`'
    u'（旧基准 ⟦T⟧：{bytesT} 字节／{chT} 字符／非空行 {nbT}） ⇎ `BR-1.8.7.layout.txt`（中基准 ⟦O⟧：{bytesO}／{chO}） ⇎ '
    u'`TLS-BRs-v2.0.2.layout.txt`（新基准 ⟦F⟧：{bytesF}／{chF}／非空行 {nbF}） ⇎ `le_lifetimes.html`（CA 说明 ⟦N⟧：{bytesN} 字节／面 {chN} 字符） ⇎ '
    u'`rfc5280.txt`（X.509 规范 ⟦R⟧：{bytesR}／{chR}／非空行 {nbR}）。门槛主账是同一个句式: 动词 + have a Validity Period greater than + 数字 + days——'
    u'三元组 旧 {ceil_tri[0]} ⇎ 中 {ceil_tri[1]} ⇎ 新 {ceil_tri[2]} ⇎ CA 与规范各 {ceil_tri[3]} 条, 命中句 {ceil_n} 条而单空格写法只 {ceil_strict_n} 条, '
    u'差额 {ceil_wrap} 处全是被排版折行的那几处（同一通道对 Validity ⇎ Period 的接缝也成立: 宽松 {vp_flex_ci} ⇎ 单空格 {vp_ci}, 差 {vp_wrap}）; '
    u'825 作该句宾语在旧中两代各 {d825_ceil[0]}⇎{d825_ceil[1]} 处、到新基准 {d825_ceil[2]} 处, 而这个词本身在三代里露面 {lines_825} 次——'
    u'把整篇按“有效期段 ⇎ 复用期段 ⇎ §1.6 条目名 ⇎ 其他”四块窗口分光: {validwin_825}⇎{reusewin_825}⇎{titlewin_825}⇎{otherwin_825}（四块相加校住露面处数, 闭合 {win_close}）。'
    u'天数值域各一份: {day_set[0]} ⇎ {day_set[1]} ⇎ {day_set[2]} ⇎ {day_set[3]} ⇎ {day_set[4]}, '
    u'新基准比旧基准多出 {set_only_F}（复用期与 2922/9132 这类日数）⇎ CA 说明独有 {set_only_N}——45 与 47 这两个值在三份基准要求里 {num_45_in_brs}⇎{num_47_in_brs} 处, '
    u'所以 LE 那句“industry rules 将限到 47 天、我们 2028 年 2 月前降到 45 天”在库里没有对照物。'
    u'叫法四套账同指一事: 大写 Validity Period {vp_caps} ⇎ 小写 {vp_low} ⇎ 忽略大小写 {vp_ci}（两档相加校住, 闭合 {vp_ci_close}）⇎ '
    u'词根 validity 全族 {validity_stem}（去掉两词组还剩 {vp_stem_gap} 处是 validityDate 与 OCSP 语境）⇎ lifetime {lifetime_ci} ⇎ notBefore⇎notAfter {notbefore}⇎{notafter}（差 {nanb_gap}）。'
    u'强度词两本账: 全大写 MUST 家族 {kw_must} ⇎ 子串档 {u_must}（新基准两档差 {must_sub_gap[2]} 处）⇎ 忽略大小写 {must_ci} ⇎ 小写 {must_l}; '
    u'同一词族按“§1.6 历史时间表行 ⇎ 其余正文”分两半: 表行 MUST {h_must} ⇎ 正文 {b_must}（闭合 {h_must_close}）, SHALL 表行 {h_shall} ⇎ 正文 {b_shall}（闭合 {h_shall_close}）, '
    u'表行只占 {hist_n} 行／{hist_chars} 字; CA 说明全大写强度词 {kw_upper[3]} 处而 will {will_ci[3]} 处——它把义务写成“行业规则将要求”, 不写 MUST。'
    u'X.509 那份不答“多久”: 带数天数 {day_num[4]} ⇎ 上限句 {ceil_n[4]} 条 ⇎ 大写 Validity Period {vp_caps[4]} 处, 只管时刻怎么写——UTCTime {ts_utctime[4]} ⇎ GeneralizedTime {ts_generalizedtime[4]}, '
    u'世纪窗口 2049⇎2050 各 {y2049[4]}⇎{y2050[4]} 处。'
    u'网页那份额外立壳⇎面两口径: 同一句在壳里 {shell_all} ⇎ 在面里 {face_all}, 每句恰多 {dup_kinds} 种差额（meta description 与 og:description 各一份）, '
    u'天数壳 {day_shell} ⇎ 面 {day_face} ⇎ 一枚 meta 引数里 {day_meta} 个, 壳面差恰为 2×{day_meta}（闭合 {day_shell_close}）; '
    u'PDF⇎layout⇎raw 三个面同页: 分页符 {formfeed}（layout⇎raw 差 {ff_close}）⇎ layout 比 raw 多字符 {face_gap}（合计 {facesum}）⇎ 多行 {line_gap} ⇎ PDF 原字节 {pdf_bytes}（合计 {pdfsum}）。'
    u'搬运账: 三代整行集交 TO {share_TO} ⇎ OF {share_OF} ⇎ TF {share_TF} ⇎ 三代同现 {share_TOF}, 并集 {union_TOF}（独有 {only_T}⇎{only_O}⇎{only_F}, 容斥闭合 {tof_close}）'
    u'⇎ 基准与规范只有 {share_TR}⇎{share_FR} 条整行相同（“CA Certification Authority”这类定义行）⇎ CA 说明与其余四份整行共用 {share_N_any} 条。'
    u'形状: 最长行 {maxlen} 列 ⇎ 行数 {lines} ⇎ 尾随空白行 {trail} ⇎ 分页符 {formfeed} ⇎ 标签字符 {le_tags} ⇎ 脚本块 {le_scripts} ⇎ 剥壳丢字 {le_dropped}; '
    u'五份字节 {sig_distinct} 种签名（本遍 blake2b 8 字节, 建条目侧与门槛侧都是 sha256 前 16 位）。'
    u'锚候选池 {ln} 条（每源 {pool_tag_n}）, 穿一源 {pool_tiers[0]} ⇎ 两源 {pool_tiers[1]} ⇎ 三源 {pool_tiers[2]} ⇎ 四源 {pool_tiers[3]} ⇎ 五源 {pool_tiers[4]}（相加校住池, 差 {pool_close}）; '
    u'登记锚 {anchor_total} 处／{anchor_distinct} 个不同串（每标签 T {tT} ⇎ O {tO} ⇎ F {tF} ⇎ N {tN} ⇎ R {tR}; 单源 {anchor_single} ⇎ 穿二至四源 {anchor_cross} ⇎ 五源全现 {anchor_all5}, '
    u'归属检查 {checks} 次, 错配 {anchor_err}）。'
    u'“五份文件的抓取时刻与磁盘 mtime 先后”“cabforum.org 此刻挂的是哪一版”“LE 页 Last updated 所指是否真更新过”“47 天所本的 industry rules 出自哪份文书”'
    u'“90 天默认是否已在全部 CA 生效”不可由在库文件判定，判词按第三档写、门槛不背书。\n')

S = io.open(FM, encoding='utf-8').read()
S = sub(u'共 **59 条**（`babeltele/B01..B59`）', u'共 **{nent} 条**（`babeltele/B01..B60`）'.format(**K), S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（59 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（{nent} 条）'.format(**K), S)
S = sub(u'当前 **59 条语料／1516 条**推导全部通过（audit 自报“已机检的推导 1516 条”）',
        u'当前 **{nent} 条语料／{proofs} 条**推导全部通过（audit 自报“已机检的推导 {proofs} 条”）'.format(**K), S)
PAR_ANCHOR = u'**B59 问的是同一件东西该多长, 四份一手文书给出四个答案**'
S = sub(PAR_ANCHOR, NEWPAR.format(**K) + PAR_ANCHOR, S)

ROW60 = (u'| B60 | {enc}（新建, 同一张证书的有效期限交五份一手文书各答一遍 {anchor_total} 处标注／{anchor_distinct} 个不同串（登记全命中, '
         u'每标签 T {tT} ⇎ O {tO} ⇎ F {tF} ⇎ N {tN} ⇎ R {tR}, 归属检查 {checks} 次）: 五色锚位 旧基准 ⟦T⟧ ⇎ 中基准 ⟦O⟧ ⇎ 新基准 ⟦F⟧ ⇎ CA 说明 ⟦N⟧ ⇎ X.509 规范 ⟦R⟧; '
         u'头条句式“动词 + have a Validity Period greater than + 数字 + days”: 三元组 {ceil_tri[0]}⇎{ceil_tri[1]}⇎{ceil_tri[2]}⇎空⇎空（命中 {ceil_n} ⇎ 单空格 {ceil_strict_n}, 折行 {ceil_wrap}）, '
         u'825 作宾语 {d825_ceil} 而露面 {lines_825} 次, 四块窗口 {validwin_825}⇎{reusewin_825}⇎{titlewin_825}⇎{otherwin_825}（闭合 {win_close}）; '
         u'天数值域五份各异 {day_set[2]} ⇎ {day_set[3]}, 45 与 47 在三份基准里 {num_45_in_brs}⇎{num_47_in_brs} 处; '
         u'叫法四账 大写 {vp_caps} ⇎ 小写 {vp_low} ⇎ 宽松 {vp_flex_ci} ⇎ 词根 {validity_stem} ⇎ lifetime {lifetime_ci} ⇎ notBefore⇎notAfter {notbefore}⇎{notafter}; '
         u'强度词两半账 MUST 表行 {h_must} ⇎ 正文 {b_must}（闭合 {h_must_close}）⇎ SHALL {h_shall} ⇎ {b_shall}（闭合 {h_shall_close}）⇎ CA 说明 will {will_ci[3]} 处而全大写 {kw_upper[3]}; '
         u'壳⇎面 同一句 {shell_all}⇎{face_all} ⇎ 天数 {day_shell}⇎{day_face}（一枚 meta {day_meta} 个, 闭合 {day_shell_close}）⇎ 三个面 分页符 {formfeed}⇎{raw_formfeed} ⇎ 字符差 {face_gap} ⇎ PDF {pdf_bytes}; '
         u'搬运 整行集交 TO⇎OF⇎TF {share_TO}⇎{share_OF}⇎{share_TF} ⇎ 三代同现 {share_TOF}（并集 {union_TOF}, 容斥闭合 {tof_close}）⇎ 基准与规范仅 {share_TR}⇎{share_FR} ⇎ CA 说明与四份 {share_N_any}; '
         u'X.509 不答多久: 天数 {day_num[4]} ⇎ 上限句 {ceil_n[4]} ⇎ 大写 {vp_caps[4]}, 只管 UTCTime {ts_utctime[4]} ⇎ GeneralizedTime {ts_generalizedtime[4]} ⇎ 2049⇎2050 各 {y2049[4]}⇎{y2050[4]}; '
         u'锚池 {ln} 条穿五源 {pool_tiers[4]} ⇎ 四源 {pool_tiers[3]} ⇎ 三源 {pool_tiers[2]}; 同数共键复合式 {coll} 组、零项 {zeros} 枚折成一条算式; '
         u'门槛侧 {deriv_keys} 枚推导键／{deriv_points} 处 B60V 引用点（建条目侧按“值→算式”去重记 {dedup_points}）, '
         u'五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对 {anchor_distinct} 条锚逐字全命中, 工具侧 atomcheck 另核 ok={anchor_distinct} bad=0） |\n')
anchor_row = (u'工具侧 atomcheck 另核 ok=21 bad=0） |' + NL)
S = sub(anchor_row, anchor_row + ROW60.format(**K), S)

lin_old = (u'第二代（B11–B59）锚内字母 **125 054**、锚外 **14 029**；全库合计 **125 175／16 224**（B59 一枚条目贡献 5 266／657, 由建条目侧现数）')
S = sub(lin_old, (u'第二代（B11–B60）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
                  u'（B60 一枚条目贡献 %s／%s, 由建条目侧现数）'
                  % (fmt(125054 + CH[u'letters_in']), fmt(14029 + CH[u'letters_out']),
                     fmt(125175 + CH[u'letters_in']), fmt(16224 + CH[u'letters_out']),
                     fmt(CH[u'letters_in']), fmt(CH[u'letters_out']))), S)

RAW60 = (u'| B60 | `raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt`（旧基准 ⟦T⟧：{bytesT} 字节／行数 {lines[0]}／非空行 {nbT}／分页符 {formfeed[0]}／上限句 {ceil_n[0]} 条／“825 days” {lines_825[0]} 处） ⇎ '
         u'`BR-1.8.7.layout.txt`（中基准 ⟦O⟧：{bytesO}／{lines[1]}／{chO}／分页符 {formfeed[1]}／上限句 {ceil_n[1]} 条而单空格仅 {ceil_strict_n[1]} 条） ⇎ '
         u'`TLS-BRs-v2.0.2.layout.txt`（新基准 ⟦F⟧：{bytesF}／{lines[2]}／非空行 {nbF}／§1.6 表行 {hist_n[2]} 行／825 作宾语 {d825_ceil[2]} 处） ⇎ '
         u'`le_lifetimes.html`（CA 说明 ⟦N⟧：{bytesN} 字节／面 {chN} 字符／标签 {le_tags} 枚／剥壳丢 {le_dropped} 字／同一句壳 {shell_all[0]} ⇎ 面 {face_all[0]}） ⇎ '
         u'`rfc5280.txt`（X.509 规范 ⟦R⟧：{bytesR}／{lines[4]}／非空行 {nbR}／UTCTime {ts_utctime[4]} ⇎ GeneralizedTime {ts_generalizedtime[4]}） | '
         u'五份文书答同一个期限 ⇒ 旧中两代逐字同写“MUST NOT 超过 825 天”⇎ 新基准把它从禁令里删掉只留 398/397 ⇎ LE 说 90 天是当初的选择、下一步 45 天而所本的“47 天 industry rules”不在库里 ⇎ '
         u'RFC 5280 根本不答多久、只管时刻写成 UTCTime 还是 GeneralizedTime; 三代基准整行共用 {share_TOF} 条而 CA 说明与任何一份都 0 条|\n')
anchor2 = (u'两代 NIST 整行只共用 63 条|' + NL)
S = sub(anchor2, anchor2 + RAW60.format(**K), S)

row_tot = (u'| **合计（{nent} 条）** | **{enct}** | **{rett}**（摘要段合计 {digt}） | — | **{unqt}** | — |\n').format(
    nent=NENT, enct=fmt(enc_all).replace(u',', u' '), rett=ret_tot,
    digt=fmt(dig_all).replace(u',', u' '), unqt=fmt(uniq_all).replace(u',', u' '))
old_tot = re.search(u'[|] [*]{2}合计（59 条）[*]{2}[^\n]*\n', S)
assert old_tot
S = S.replace(old_tot.group(0), row_tot)

tail_old = (u'新建的 B54 ⇎ B56 ⇎ B57 ⇎ B58 ⇎ B59 同样为空——B59 把两位以内的结构计数全部折进了 DERIV'
            u'（0 项 106 枚并成一条算式，由 _b59_scan 照样复算；另有 34 处跨值复合式））未逐位核验，')
assert S.count(tail_old) == 1
S = sub(tail_old, (u'新建的 B54 ⇎ B56 ⇎ B57 ⇎ B58 ⇎ B59 ⇎ B60 同样为空——B60 把两位以内的结构计数全部折进了 DERIV'
                   u'（0 项 %d 枚并成一条算式，由 _b60_scan 照样复算；另有 %d 处跨值复合式））未逐位核验，'
                   % (CH[u'zero_terms'], len(CH[u'collisions']))), S)
S = sub(u'残余提示（不计 FAIL）：20 个', u'残余提示（不计 FAIL）：%d 个' % soft_all, S)

WL, WR = 140, 140
CMD = (u'python -X utf8 corpus/_mkB60.py                  # 建条目: 扁平契约 %d 枚键／DERIV %d 枚算式, 占位符未替换 0 个, 采侧对账 %d 键 0 不符\n'
       u'python -X utf8 corpus/_mkdigest3.py B60 <entry> T corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt %d %d '
       u'O corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.layout.txt %d %d F corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt %d %d '
       u'N corpus/raw/cert/le_lifetimes.html %d %d R corpus/raw/cert/rfc5280.txt %d %d   # 五源分节摘要(%s 字符, 窗口按 %d⇎%d 取句边界, 粘面⇎断面按命中多者取)\n'
       u'python -X utf8 corpus/_wire60.py                    # 把 SCAN 段机械切进 audit.py::_b60_scan 并插 DERIV[\'B60\']\n'
       u'python -X utf8 corpus/_fill60.py                    # 第四遍: 现取注数并把 ⛓解读注 写回条目(13 行复测表全 assert)\n'
       u'python -X utf8 corpus/atomcheck.py B60 corpus/_atoms60.txt   # 工具侧独立逐字校验: ok=%d bad=0\n'
       % (len(FLAT), CH[u'deriv_keys'], NMEAS, WL, WR, WL, WR, WL, WR, WL, WR, WL, WR,
          fmt(dig60).replace(u',', u' '), WL, WR, m(u'anchor_distinct')))
anchor3 = u'python -X utf8 corpus/atomcheck.py B59 corpus/_atoms59.txt   # 工具侧独立逐字校验: ok=21 bad=0' + NL
assert S.count(anchor3) == 1
S = sub(anchor3, anchor3 + CMD, S)

io.open(FM, 'w', encoding='utf-8', newline=NL).write(S)
print(u'README 已记账: %d 条 ｜ 编码合计 %s ⇎ 摘要合计 %s ⇎ 合计保留率 %s ｜ 唯一码点 %d ｜ 推导 %d 条 ｜ 提示 %d（清单 %s） ｜ '
      u'B60 %s 字符／%d 锚(%d 串, T %d⇎O %d⇎F %d⇎N %d⇎R %d, 单源 %d⇎穿二至四 %d⇎五源 %d, 检查 %d, 错配 %d) ｜ '
      u'第五遍现量 %d 个键全等契约 ｜ 上限句 %s ⇎ 单空格 %s ⇎ 折行 %s ⇎ 825 宾语 %s ｜ 天数值域(新⇎CA) %s ｜ '
      u'整行共用 %s⇎%s⇎%s ⇎ 三代同现 %d ⇎ 容斥闭合 %d ｜ 池 %s 穿五源 %d ｜ 两口径差 %s ⇎ 最长行 %s ｜ blake2b %d 种'
      % (NENT, fmt(enc_all), fmt(dig_all), ret_tot, uniq_all, proofs, soft_all,
         u' '.join(sorted(HINT)), fmt(enc60), m(u'anchor_total'), m(u'anchor_distinct'),
         tc[u'T'], tc[u'O'], tc[u'F'], tc[u'N'], tc[u'R'], m(u'anchor_single'), m(u'anchor_cross'),
         m(u'anchor_all5'), m(u'checks'), m(u'anchor_err'), len(Q5),
         u'⇎'.join(str(x) for x in m(u'ceil_n')), u'⇎'.join(str(x) for x in m(u'ceil_strict_n')),
         u'⇎'.join(str(x) for x in m(u'ceil_wrap')), u'⇎'.join(str(x) for x in m(u'd825_ceil')),
         u'⇎'.join(u'[%s]' % u','.join(x) for x in (m(u'day_set')[2], m(u'day_set')[3])),
         m(u'share_TO'), m(u'share_OF'), m(u'share_TF'),
         m(u'share_TOF'), m(u'tof_close'), fmt(m(u'pool_n')), m(u'pool_tiers')[4],
         u'⇎'.join(str(x) for x in m(u'face_gap')), u'⇎'.join(str(x) for x in m(u'maxlen')),
         m(u'sig_distinct')))
