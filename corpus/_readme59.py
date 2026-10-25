# -*- coding: utf-8 -*-
"""README 记账: 58 条 → 59 条。合计、唯一码点、推导条数全部取自 audit 的当下输出, 不手填。
本文件是第五套实现, 换算法不换定义:
剥壳走一台单游标状态机——注释跳到 `-->`(无闭合就落回标签分支, 与建条目侧单行正则失配的行为一致),
script/style 另由 `descript` 单独一遍删块(建条目侧用带反向引用的 re.sub, 第四遍用片段队列的截断开关);
实体与 unicode 折成一次左到右的查表扫描(建条目侧按 ENT 表逐对 replace 十七遍, 门槛侧又是另外三条正则);
词法量不走 re.split+Counter, 而是手工走 isalnum 生成两条 token 流(字母档 ⇎ 词字符档), 子串档一律 find 游标;
门槛数字族反着推: 先抓 `character(s)` 再往回要看导出的号与分隔符(建条目侧从前往后用 (?i)\\b(...) 正则);
ASVS 矩阵的列号从行尾倒数(-2 是 NIST 号, -3 是 CWE, -6..-4 是三列勾), 建条目侧从左往右数 c[6]/c[7], 第四遍按表头单元名定列;
节号手拆行首 token 的 `.` 段数与末段是否纯数字(建条目侧用 (?m)^\\s*((?:\\d+\\.){2,3}\\d+)\\s);
断句先把 `. ` 换成换行符再切(建条目侧维护跨行缓冲);
集合交并不用 set&set, 改用“在一份里逐条问另一份有没有”的列表路;
四份字节的签名摘要换 blake2b 8 字节(建条目侧用 sha256 前 16 位), 只比种数不比串;
锚统计直接扫条目正文里的 ⟦⟧⟨⟩ 字符游标, 再拿每条串到本遍的归一文档里现验(建条目侧按池位置推, 门槛侧按归属表查)。
每个数与两份快照对表: 建条目侧扁平契约 corpus/_b59flat.json ⇎ 门槛侧 corpus/_b59audit.json。任一标量对不上就当场停机。"""
import hashlib, io, json, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
FM = u'corpus/README.md'
NL = chr(10)
TAG = u'B59'
ENTRY = u'corpus/babeltele/B59_one_password_four_answers.md'
PATHS = [u'corpus/raw/pwd/nist_63b_rev3.html', u'corpus/raw/pwd/asvs_40_v2.md',
         u'corpus/raw/pwd/nist_63b_rev4.html', u'corpus/raw/pwd/owasp_auth_cs.html']
TAGS = [u'T', u'O', u'F', u'N']
IDX = dict((t, i) for i, t in enumerate(TAGS))
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')
RD = lambda q: io.open(q, encoding='utf-8', errors='replace').read()
DIGIT = u'0123456789'
SPC = u' \t'
NORMW = [u'SHALL', u'SHOULD', u'MAY', u'MUST']
WORDNUM = {u'six': 6, u'eight': 8, u'twelve': 12, u'fifteen': 15, u'four': 4, u'ten': 10}

ENTS = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'), (u'&sect;', u'S'),
        (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'), (u'&#215;', u'x'),
        (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"), (u'&mdash;', u'-'), (u'&ndash;', u'-'),
        (u'&deg;', u'deg'), (u'&infin;', u'inf')]
UNIS = {u'\xa0': u' ', u'−': u'-', u'–': u'-', u'—': u'-', u'×': u'x', u'‘': u"'",
        u'’': u"'", u'“': u'"', u'”': u'"', u'→': u'->'}


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
assert NENT == 59, NENT
b59, A = row[u'B59'], row[u'ALL']
dig_all, enc_all = int(A[0].replace(u' ', u'')), int(A[1].replace(u' ', u''))
uniq_all = int(re.sub(u'[^0-9]', u'', A[4]))
assert (sum(int(v[0]) for k, v in row.items() if k != u'ALL'),
        sum(int(v[1]) for k, v in row.items() if k != u'ALL')) == (dig_all, enc_all)
assert b59[7:11] == [u'0', u'0', u'0', u'0'], b59
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
assert u'B59' not in HINT, HINT.get(u'B59')
dig59, enc59 = int(b59[0]), int(b59[1])
ret_tot = A[2].replace(u'*', u'')

# ---------- 2) 第五遍: 自己从四份字节现量 ----------
CH = json.load(io.open(u'corpus/_b59checks.json', encoding='utf-8'))
FLAT = json.load(io.open(u'corpus/_b59flat.json', encoding='utf-8'))
SN = json.load(io.open(u'corpus/_b59audit.json', encoding='utf-8'))
SNAP, SRCALL = SN[TAG], SN[u'SRC']
assert enc59 == CH[u'enc_chars'] and dig59 == 8624, (enc59, CH[u'enc_chars'], dig59)

RB = [io.open(q, u'rb').read() for q in PATHS]
RAW = [r.decode(u'utf-8') for r in RB]          # 严格解码: 建条目侧用 errors='replace'
Q5 = {}


def q(name, val):
    Q5[name] = val
    if name in FLAT:
        assert rnd(val) == rnd(FLAT[name]), (name, val, FLAT[name])
    if name in SNAP:
        assert rnd(val) == rnd(SNAP[name]), (name, u'快照', val, SNAP[name])
    return val


def m(name):
    return Q5[name]


def four(name, f):
    return q(name, [f(k) for k in range(4)])


def wc(c):
    return (u'a' <= c <= u'z') or (u'A' <= c <= u'Z') or (u'0' <= c <= u'9') or c == u'_'


def pnorm(s):
    return u''.join(c for c in s.lower() if (u'a' <= c <= u'z') or (u'0' <= c <= u'9'))


def tagnm(t):
    """标签名: 取到第一个非字母数字字符; 空名(注释残留、<!…)返回 ''。"""
    out = u''
    for c in t:
        if (u'a' <= c <= u'z') or (u'0' <= c <= u'9'):
            out += c
        else:
            break
    return out


def descript(s):
    """只删 script/style 整块(含边界), 其余一字不动——对应建条目侧的 unscript。"""
    low = s.lower()
    out, k, n = [], 0, len(s)
    while True:
        j = -1
        for nm in (u'script', u'style'):
            c = low.find(u'<', k)
            while c >= 0:
                t = low[c + 1:c + 1 + len(nm)]
                nx = low[c + 1 + len(nm):c + 2 + len(nm)]
                if t == nm and not (nx and ((u'a' <= nx <= u'z') or (u'0' <= nx <= u'9'))):
                    break
                c = low.find(u'<', c + 1)
            if c >= 0 and (j < 0 or c < j):
                j, hit = c, nm
        if j < 0:
            out.append(s[k:])
            break
        e = s.find(u'>', j)
        c = low.find(u'</' + hit, e)
        if c < 0:
            out.append(s[k:j])
            k = j + 1
            continue
        d = s.find(u'>', c)
        out.append(s[k:j])
        k = n if d < 0 else d + 1
    return u''.join(out)


def shell(s):
    """单游标剥壳: 注释 → <br> → 标签; 注释无闭合时落回标签分支(与单行正则失配同行为)。"""
    low = s.lower()
    out, k, n = [], 0, len(s)
    while True:
        j = s.find(u'<', k)
        if j < 0:
            out.append(s[k:])
            break
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
        out.append(u' ' if low[j + 1:e].startswith(u'br') else u'')
        k = e + 1
    return u''.join(out)


def unfold(s):
    """实体与 unicode: 一次左到右查表; 然后并 [ \\t]+ 为一个空格, 首尾去空白。"""
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
        if c in UNIS:
            out.append(UNIS[c])
            k += 1
            continue
        out.append(c)
        k += 1
    s = u''.join(out)
    out, k, n = [], 0, len(s)
    while k < n:
        if s[k] in SPC:
            while k < n and s[k] in SPC:
                k += 1
            out.append(u' ')
        else:
            out.append(s[k])
            k += 1
    return u''.join(out).strip()


def render(s):
    return unfold(shell(s))


NS = [descript(r) for r in RAW]
TXT = [render(t) for t in NS]
TXTF = [render(r) for r in RAW]
LST = [[render(l) for l in NS[i].split(NL)] for i in range(4)]
RLB = [r.split(b'\n') for r in RB]
RLOW = [r.lower() for r in RAW]
LOW = [t.lower() for t in TXT]
FAN = [pnorm(t) for t in TXT]

# ---- 形状档 ----
four(u'bytes', lambda i: len(RB[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'chars_untagged', lambda i: len(TXTF[i]))
four(u'js_gap', lambda i: len(TXTF[i]) - len(TXT[i]))
four(u'script_tags', lambda i: RLOW[i].count(u'<script'))
four(u'style_tags', lambda i: RLOW[i].count(u'<style'))
four(u'lt_tags', lambda i: sum(1 for c in RAW[i] if c == u'<'))
four(u'lines', lambda i: RB[i].count(b'\n'))
four(u'nonblank', lambda i: len([l for l in RLB[i] if l.strip()]))
four(u'rlines', lambda i: NS[i].count(u'\n'))
four(u'rnonblank', lambda i: len([l for l in LST[i] if l]))
four(u'tabs', lambda i: sum(1 for c in TXT[i] if c == u'\t'))
four(u'nonascii', lambda i: sum(1 for c in RAW[i] if ord(c) > 127))
four(u'bom', lambda i: 1 if RB[i][:3] == b'\xef\xbb\xbf' else 0)
four(u'maxlen', lambda i: max(len(l) for l in LST[i]))
q(u'sha8', [hashlib.blake2b(RB[i], digest_size=8).hexdigest() for i in range(4)])
q(u'sig_distinct', len(set(m(u'sha8'))))
four(u'pipe_cells', lambda i: RAW[i].count(u'|'))
four(u'bold_marks', lambda i: RAW[i].count(u'**') // 2)


def occ(s, ndl):
    c = k = 0
    while True:
        j = s.find(ndl, k)
        if j < 0:
            return c
        c += 1
        k = j + len(ndl)


four(u'md_links', lambda i: occ(RAW[i], u']' + u'(http'))
four(u'table_tags', lambda i: occ(RLOW[i], u'<table'))
four(u'tr_rows', lambda i: occ(RLOW[i], u'<tr'))


def entcount(s):
    """'&[a-zA-Z#0-9]+;' 的游标口径: 从每个 & 起吞字母数字与 #, 再看是否落在 ;。"""
    c = 0
    n = len(s)
    i = 0
    while True:
        j = s.find(u'&', i)
        if j < 0:
            return c
        k = j + 1
        while k < n and ((u'a' <= s[k] <= u'z') or (u'A' <= s[k] <= u'Z')
                         or (u'0' <= s[k] <= u'9') or s[k] == u'#'):
            k += 1
        if k > j + 1 and k < n and s[k] == u';':
            c += 1
            i = k + 1
        else:
            i = j + 1


four(u'ent_all', lambda i: entcount(RAW[i]))
q(u'nist_row_sum', m(u'tr_rows')[0] + m(u'tr_rows')[2])
q(u'pipe_vs_row', m(u'pipe_cells')[1] - m(u'nist_row_sum'))

# ---- matcher 族: 位置上的匹配长度, 0 表示不匹配 ----
def mt_lit(ndl):
    return lambda s, i: len(ndl) if s.startswith(ndl, i) else 0


def mt_optgap(head, tail, gaps):
    """head + 可选分隔(按给定优先序试, 每个分隔是一条谓词串) + tail。"""
    def f(s, i):
        if not s.startswith(head, i):
            return 0
        for g in gaps:
            k = i + len(head)
            ok = True
            for pr in g:
                if k >= len(s) or not pr(s[k]):
                    ok = False
                    break
                k += 1
            if ok and s.startswith(tail, k):
                return k + len(tail) - i
        return 0
    return f


def mt_run(head, tail, cls):
    """head + 至少一个 cls 字符 + tail(贪心取最长串; 尾串不含 cls 字符, 故无须回溯)。"""
    def f(s, i):
        if not s.startswith(head, i):
            return 0
        k = i + len(head)
        j = k
        while j < len(s) and s[j] in cls:
            j += 1
        if j == k or not s.startswith(tail, j):
            return 0
        return j + len(tail) - i
    return f


def mt_anygap(head, tail, maxg=1):
    """head + 0..maxg 个非换行字符 + tail, 贪心先长后短。"""
    def f(s, i):
        if not s.startswith(head, i):
            return 0
        for g in range(maxg, -1, -1):
            k = i + len(head) + g
            if g and u'\n' in s[i + len(head):k]:
                continue
            if s.startswith(tail, k):
                return k + len(tail) - i
        return 0
    return f


def mt_bprefix(ndl, eat=False, both=False):
    """\\b 前界; eat=随后吞词字符(\\w*); both=另需 \\b 后界。"""
    def f(s, i):
        if i and wc(s[i - 1]):
            return 0
        if not s.startswith(ndl, i):
            return 0
        k = i + len(ndl)
        if eat:
            while k < len(s) and wc(s[k]):
                k += 1
            return k - i
        if both and k < len(s) and wc(s[k]):
            return 0
        return len(ndl)
    return f


def mt_alts(ms):
    def f(s, i):
        for g in ms:
            k = g(s, i)
            if k:
                return k
        return 0
    return f


def mt_numword(word):
    """\\d+ 后接 \\s* 再接词; 返回匹配长度。"""
    def f(s, i):
        if s[i] not in DIGIT:
            return 0
        k = i
        while k < len(s) and s[k] in DIGIT:
            k += 1
        run = k
        while k < len(s) and s[k] in u' \t\n\r\x0b\x0c':
            k += 1
        if s.startswith(word, k):
            return k + len(word) - i
        return 0
    f.digits = True
    return f


WS = lambda c: c in u' \t\n\r\x0b\x0c'
HY = lambda c: c == u'-'
SPH = lambda c: c in u' \t-'
M_BLOCK = mt_optgap(u'block', u'list', [[WS, HY], [WS], [HY], []])
M_BLBLACK = mt_optgap(u'black', u'list', [[SPH], []])
M_BLKANY = mt_alts([mt_optgap(u'block', u'list', [[SPH], []]), mt_optgap(u'black', u'list', [[SPH], []])])
M_RATE = mt_alts([mt_anygap(u'rate', u'limit'), mt_lit(u'throttl')])
M_MFA = mt_alts([mt_bprefix(u'mfa', both=True), mt_anygap(u'multi', u'factor')])
MC = ((u'blocklist', M_BLOCK), (u'breach', mt_lit(u'breach')),
      (u'composition', mt_lit(u'composition rules')), (u'hint', mt_bprefix(u'hint')),
      (u'copypaste', mt_lit(u'copy and paste')), (u'ratelimit', M_RATE),
      (u'lockout', mt_bprefix(u'lock', eat=True)),
      (u'periodic', mt_alts([mt_lit(u'periodic'), mt_lit(u'regular change')])),
      (u'entropy', mt_lit(u'entropy')), (u'multifactor', M_MFA),
      (u'arbitrary', mt_lit(u'arbitrary')), (u'forcechange', mt_lit(u'force a change')))


def cnt(s, mt):
    c = i = 0
    while i < len(s):
        k = mt(s, i)
        if k:
            c += 1
            i += k
        else:
            i += 1
    return c


def has(s, mt):
    i = 0
    while i < len(s):
        if mt(s, i):
            return True
        i += 1
    return False


# ---- 门槛数字: 从 character(s) 反向往回推 ----
def ctx_back(s):
    """返回 (数值表, 词面处数, 数字处数)。口径: \\b(1~3位数字|六个词)[- ]characters?\\b。"""
    low = s.lower()
    vals, w, d = [], 0, 0
    i = 0
    while True:
        j = low.find(u'character', i)
        if j < 0:
            return vals, w, d
        if j < 2 or low[j - 1] not in u' -':
            i = j + 9
            continue
        p = j - 1
        r = p
        while r > 0 and low[r - 1] in DIGIT:
            r -= 1
        got = None
        if r < p:
            if (r == 0 or not wc(low[r - 1])) and 1 <= p - r <= 3:
                got = int(low[r:p])
                d += 1
        else:
            r = p
            while r > 0 and u'a' <= low[r - 1] <= u'z':
                r -= 1
            t = low[r:p]
            if t in WORDNUM and (r == 0 or not wc(low[r - 1])):
                got = WORDNUM[t]
                w += 1
        if got is None:
            i = j + 9
            continue
        e = j + 9
        if low[e:e + 1] == u's':
            e += 1
        if e < len(low) and wc(low[e]):
            i = j + 9
            continue
        vals.append(got)
        i = e


def ctx_vals(i):
    return ctx_back(TXT[i])[0]


def has_numchar(line):
    """(?i)\\d+[- ]characters? —— 号前不要求词界, character 后也不要求。"""
    low = line.lower()
    i = 0
    while True:
        j = low.find(u'character', i)
        if j < 0:
            return False
        if j >= 1 and low[j - 1] in u' -':
            r = j - 1
            while r > 0 and low[r - 1] in DIGIT:
                r -= 1
            if r < j - 1:
                return True
        i = j + 9


four(u'th_digit8', lambda i: occ(TXT[i], u'8 characters'))
four(u'th_word_eight', lambda i: occ(TXT[i], u'eight characters'))
four(u'th_digit12', lambda i: occ(TXT[i], u'12 characters'))
four(u'th_digit15', lambda i: occ(TXT[i], u'15 characters'))
four(u'th_digit64', lambda i: occ(TXT[i], u'64 characters'))
four(u'th_digit128', lambda i: occ(TXT[i], u'128 characters'))
four(u'th_digit6', lambda i: occ(TXT[i], u'6 characters'))
four(u'ctx_occ', lambda i: len(ctx_vals(i)))
four(u'ctx_distinct', lambda i: len(set(ctx_vals(i))))
four(u'ctx_set', lambda i: sorted(set(ctx_vals(i))))
four(u'ctx_word_form', lambda i: ctx_back(TXT[i])[1])
four(u'ctx_digit_form', lambda i: ctx_back(TXT[i])[2])
q(u'ctx_form_close', [m(u'ctx_word_form')[i] + m(u'ctx_digit_form')[i] - m(u'ctx_occ')[i] for i in range(4)])
q(u'ctx_eight_docs', len([i for i in range(4) if u'eight characters' in TXT[i]]))
q(u'ctx_d8_docs', len([i for i in range(4) if m(u'th_digit8')[i]]))
q(u'ctx_815_docs', len([i for i in range(4) if 8 in ctx_vals(i) and 15 in ctx_vals(i)]))
q(u'ctx_12_only', len([i for i in range(4) if 12 in ctx_vals(i)]))
q(u'ctx_128_only', len([i for i in range(4) if 128 in ctx_vals(i)]))
four(u'th_line_norm', lambda i: len([l for l in LST[i] if has_numchar(l) and u'SHALL' in l]))
four(u'th_line_bare', lambda i: len([l for l in LST[i]
                                     if has_numchar(l) and not any(w in l for w in NORMW)]))

# ---- 强度词: 手工走字母 token ----
def let_toks(s):
    out, k, n = [], 0, len(s)
    while k < n:
        if not (u'a' <= s[k] <= u'z' or u'A' <= s[k] <= u'Z'):
            k += 1
            continue
        j = k
        while j < n and (u'a' <= s[j] <= u'z' or u'A' <= s[j] <= u'Z'):
            j += 1
        out.append(s[k:j])
        k = j
    return out


LETT = [let_toks(t) for t in TXT]
for W in NORMW:
    four(u'kw_%s_u' % W.lower(), lambda i, W=W: len([t for t in LETT[i] if t == W]))
    four(u'kw_%s_l' % W.lower(), lambda i, W=W: len([t for t in LETT[i] if t == W.lower()]))
    four(u'kw_%s_t' % W.lower(), lambda i, W=W: len([t for t in LETT[i] if t == W[0] + W[1:].lower()]))
    four(u'kw_%s_ci' % W.lower(), lambda i, W=W: len([t for t in LETT[i] if t.upper() == W]))
q(u'kw_close', dict((W, [m(u'kw_%s_u' % W.lower())[i] + m(u'kw_%s_l' % W.lower())[i]
                         + m(u'kw_%s_t' % W.lower())[i] - m(u'kw_%s_ci' % W.lower())[i]
                         for i in range(4)]) for W in NORMW))
q(u'kw_close_sum', sum(sum(v) for v in m(u'kw_close').values()))
q(u'must_upper_all4', sum(m(u'kw_must_u')))
q(u'kw_upper_total', [sum(m(u'kw_%s_u' % W.lower())[i] for W in NORMW) for i in range(4)])
q(u'kw_ci_total', [sum(m(u'kw_%s_ci' % W.lower())[i] for W in NORMW) for i in range(4)])
q(u'kw_gap', [m(u'kw_ci_total')[i] - m(u'kw_upper_total')[i] for i in range(4)])
four(u'kw_shallnot_u', lambda i: occ(TXT[i], u'SHALL NOT'))
four(u'kw_shallnot_ci', lambda i: occ(LOW[i], u'shall not'))
four(u'kw_shouldnot_u', lambda i: occ(TXT[i], u'SHOULD NOT'))
four(u'kw_shouldnot_ci', lambda i: occ(LOW[i], u'should not'))
q(u'kw_shallnot_gap', [m(u'kw_shallnot_ci')[i] - m(u'kw_shallnot_u')[i] for i in range(4)])
q(u'kw_shouldnot_gap', [m(u'kw_shouldnot_ci')[i] - m(u'kw_shouldnot_u')[i] for i in range(4)])

# ---- 术语换代 ----
four(u'tm_memorized', lambda i: cnt(LOW[i], mt_lit(u'memorized secret')))
four(u'tm_memorized_caps', lambda i: occ(TXT[i], u'Memorized Secrets'))
four(u'tm_pw_sing', lambda i: cnt(LOW[i], mt_bprefix(u'password', both=True)))
four(u'tm_pw_plural', lambda i: cnt(LOW[i], mt_bprefix(u'passwords', both=True)))
four(u'tm_pw_any', lambda i: cnt(LOW[i], mt_alts([mt_bprefix(u'passwords', both=True),
                                                  mt_bprefix(u'password', both=True)])))
def m_called(s, i):
    """(?i)called .{0,3}Memorized Secrets: 贪心先长 gap 后短, gap 内不含换行。"""
    if not s.startswith(u'called', i):
        return 0
    for g in (3, 2, 1, 0):
        if u'\n' in s[i + 6:i + 6 + g]:
            continue
        if s.startswith(u'memorized secrets', i + 6 + g):
            return 6 + g + len(u'memorized secrets')
    return 0


four(u'tm_bridge', lambda i: cnt(LOW[i], m_called))
q(u'tm_defline', [len([l for l in LST[i] if u'intended to be memorized' in l]) for i in range(4)])
q(u'tm_close', [m(u'tm_pw_sing')[i] + m(u'tm_pw_plural')[i] - m(u'tm_pw_any')[i] for i in range(4)])

# ---- 机制词: 词处 ⇎ 行处 ----
for k, mt in MC:
    four(u'mc_%s' % k, lambda i, mt=mt: cnt(LOW[i], mt))
    four(u'mc_%s_lines' % k, lambda i, mt=mt: len([l for l in LST[i] if has(l.lower(), mt)]))
q(u'comp_shouldnot', [len([l for l in LST[i] if u'composition rules' in l and u'SHOULD NOT' in l]) for i in range(4)])
q(u'comp_shallnot', [len([l for l in LST[i] if u'composition rules' in l and u'SHALL NOT' in l]) for i in range(4)])
q(u'comp_norm_free', [m(u'mc_composition_lines')[i] - m(u'comp_shouldnot')[i] - m(u'comp_shallnot')[i] for i in range(4)])
q(u'chg_shallnot', [len([l for l in LST[i] if (u'change passwords' in l.lower()
                                               or u'change memorized secrets' in l.lower())
                         and u'SHALL NOT' in l]) for i in range(4)])
q(u'chg_shouldnot', [len([l for l in LST[i] if (u'change passwords' in l.lower()
                                                or u'change memorized secrets' in l.lower())
                          and u'SHOULD NOT' in l]) for i in range(4)])
q(u'blk_def_lines', len([l for l in LST[2] if u'blocklist' in l and u'SHALL' in l]))
four(u'bl_blacklist', lambda i: cnt(LOW[i], mt_lit(u'blacklist')))
four(u'bl_spaced', lambda i: cnt(LOW[i], mt_run(u'black', u'list', u' \t')))
four(u'bl_black', lambda i: cnt(LOW[i], M_BLBLACK))
four(u'bl_word_any', lambda i: cnt(LOW[i], M_BLKANY))
q(u'bl_word_close', [m(u'mc_blocklist')[i] + m(u'bl_black')[i] - m(u'bl_word_any')[i] for i in range(4)])
q(u'bl_black_close', [m(u'bl_blacklist')[i] + m(u'bl_spaced')[i] - m(u'bl_black')[i] for i in range(4)])

# ---- 引用形态与谱系 ----
CITE = ((u'url_nist', (TXT, u'pages.nist.gov')), (u'spaced', (TXT, u'NIST SP 800-63')),
        (u'unspaced', (TXT, u'SP800-63B')), (u'rev4num', (TXT, u'800-63-4')),
        (u'rev3num', (TXT, u'800-63-3')), (u'superseded', (LOW, u'superseded')),
        (u'draftself', (LOW, u'initial public draft')), (u'http_any', (LOW, u'http')))
for k, (src, ndl) in CITE:
    if k == u'http_any':
        four(u'cite_%s' % k, lambda i: cnt(LOW[i], mt_alts([mt_lit(u'https://'), mt_lit(u'http://')])) )
    else:
        four(u'cite_%s' % k, lambda i, src=src, ndl=ndl: occ(src[i], ndl))
q(u'sup_openid', len([l for l in LST[3] if u'superseded' in l.lower() and u'OpenID' in l]))
q(u'sup_nist', len([l for l in LST[0] if u'superseded' in l.lower() and u'63-4' in l]))
q(u'cite_63b_docs', len([i for i in range(4) if u'800-63b' in LOW[i]]))
q(u'cite_forms', len([x for x in (m(u'cite_url_nist')[1], m(u'cite_unspaced')[3], m(u'cite_spaced')[0]) if x]))

# ---- 节号: 手拆行首段 ----
def sec_nums(t):
    out = []
    for l in t.split(NL):
        k = 0
        while k < len(l) and l[k] in u' \t\n\r\x0b\x0c':
            k += 1
        j = k
        while j < len(l) and (l[j] in DIGIT or l[j] == u'.'):
            j += 1
        if j == k or (j < len(l) and not l[j].isspace()):
            continue
        parts = l[k:j].split(u'.')
        if len(parts[-1]) == 0 or not all(p and all(c in DIGIT for c in p) for p in parts):
            continue
        if 2 <= len(parts) - 1 <= 3:
            out.append(l[k:j])
    return out


four(u'sec_head_n', lambda i: len(sec_nums(TXT[i])))
ST = sorted(set(sec_nums(TXT[0])))
SF = sorted(set(sec_nums(TXT[2])))
q(u'sec_T_set', ST)
q(u'sec_F_set', SF)
q(u'sec_T_n', len(ST))
q(u'sec_F_n', len(SF))
q(u'sec_shared', len([x for x in ST if x in SF]))
q(u'sec_T_inF_text', len([x for x in ST if x in TXT[2]]))

# ---- ASVS 矩阵: 列号从行尾倒数 ----
def is_req(l):
    if not l.startswith(u'|'):
        return False
    k = 1
    while k < len(l) and l[k] in u' \t':
        k += 1
    if not l.startswith(u'**2.', k):
        return False
    j = k + 4
    a = j
    while j < len(l) and l[j] in DIGIT:
        j += 1
    if j == a or j >= len(l) or l[j] != u'.':
        return False
    j += 1
    a = j
    while j < len(l) and l[j] in DIGIT:
        j += 1
    return j > a and l.startswith(u'**', j)


ROWS = [l for l in LST[1] if is_req(l)]
CELLS = [[c.strip() for c in r.split(u'|')] for r in ROWS]
assert len(set(len(c) for c in CELLS)) == 1, set(len(c) for c in CELLS)
WIDTH = len(CELLS[0])
q(u'asvs_row_width', WIDTH)
q(u'asvs_req_rows', len(ROWS))
q(u'asvs_bold_ids', RAW[1].count(u'**2.'))


def dotted(x):
    ps = x.split(u'.')
    return len(ps) >= 2 and all(p and all(c in DIGIT for c in p) for p in ps) and len(ps) <= 4


REFS = sorted(set([c[WIDTH - 2] for c in CELLS if dotted(c[WIDTH - 2])]))
q(u'asvs_refs', REFS)
q(u'asvs_ref_occ', len([c[WIDTH - 2] for c in CELLS if dotted(c[WIDTH - 2])]))
q(u'asvs_ref_distinct', len(REFS))
q(u'asvs_rows_noref', m(u'asvs_req_rows') - m(u'asvs_ref_occ'))
q(u'asvs_ref_inT', len([x for x in REFS if x in ST]))
q(u'asvs_ref_inF', len([x for x in REFS if x in SF]))
q(u'asvs_ref_inT_text', len([x for x in REFS if x in TXT[0]]))
q(u'asvs_ref_inF_text', len([x for x in REFS if x in TXT[2]]))
q(u'asvs_ref_missT', [x for x in REFS if x not in ST])
q(u'asvs_ref_missF', [x for x in REFS if x not in SF])
q(u'asvs_ref_close', m(u'asvs_ref_inT') + len(m(u'asvs_ref_missT')) - m(u'asvs_ref_distinct'))
q(u'asvs_tick_cols', [len([c for c in CELLS if c[WIDTH - 6 + j] == u'✓']) for j in (0, 1, 2)])
q(u'asvs_tick_total', sum(m(u'asvs_tick_cols')))
q(u'asvs_tick_legend', len([l for l in LST[1] if u'✓' in l and not is_req(l)]))
q(u'asvs_tick_glyph', occ(RAW[1], u'✓'))
q(u'asvs_tick_close', m(u'asvs_tick_total') + m(u'asvs_tick_legend') - m(u'asvs_tick_glyph'))
q(u'asvs_cwe', sorted(set([c[WIDTH - 3] for c in CELLS if c[WIDTH - 3].isdigit()])))
q(u'asvs_cwe_distinct', len(m(u'asvs_cwe')))
q(u'asvs_url_head', occ(RAW[1], u'pages.nist.gov/800-63-3'))
q(u'asvs_5112', [occ(t, u'5.1.1.2') for t in TXT])
q(u'id_211_bold', RAW[1].count(u'**2.1.1**'))
q(u'id_211_occ', [occ(t, u'2.1.1') for t in TXT])
q(u'id_211_docs', len([i for i in range(4) if u'2.1.1' in TXT[i]]))
def m_secform(s, i):
    """'Sec\\. ?\\d' 的大小写敏感口径。"""
    if not s.startswith(u'Sec.', i):
        return 0
    k = i + 4
    if s[k:k + 1] == u' ':
        k += 1
    return (k + 1 - i) if s[k:k + 1].isdigit() else 0


def m_secall(s, i):
    """(?i)(?:sec\\.?|section)[ \\t]+\\d: 先 sec. 再 sec 再 section, 分隔贪心。"""
    for head in (u'sec.', u'sec', u'section'):
        if not s.startswith(head, i):
            continue
        k = i + len(head)
        j = k
        while j < len(s) and s[j] in SPC:
            j += 1
        if j > k and s[j:j + 1].isdigit():
            return j + 1 - i
    return 0


def m_secword(s, i):
    if i and wc(s[i - 1]):
        return 0
    if not s.startswith(u'section ', i):
        return 0
    return 9 if s[i + 8:i + 9].isdigit() else 0


four(u'sec_cite_sec', lambda i: cnt(TXT[i], m_secform))
four(u'sec_cite_word', lambda i: cnt(LOW[i], m_secword))
four(u'sec_cite_any', lambda i: cnt(LOW[i], m_secall))
q(u'sec_cite_close', [m(u'sec_cite_sec')[i] + m(u'sec_cite_word')[i] - m(u'sec_cite_any')[i] for i in range(4)])

# ---- 熵/位 ----
for b in (u'20', u'32', u'40', u'64', u'112'):
    four(u'bit_%s' % b, lambda i, b=b: occ(TXT[i], b + u' bits'))
four(u'bit_any', lambda i: cnt(LOW[i], mt_numword(u'bits')))


def bit_set(i):
    low = LOW[i]
    nw = mt_numword(u'bits')
    out = []
    j = 0
    while j < len(low):
        if low[j] in DIGIT and nw(low, j):
            k = j
            while low[k] in DIGIT:
                k += 1
            out.append(low[j:k])
            j = k
        else:
            j += 1
    return sorted(set(out))


four(u'bit_set', bit_set)
q(u'bit_close', [m(u'bit_any')[i] - sum(m(u'bit_%s' % b)[i] for b in (u'20', u'32', u'40', u'64', u'112'))
                 for i in range(4)])
q(u'bit_lost', sorted(set(m(u'bit_set')[0]) - set(m(u'bit_set')[2])))
q(u'bit_new', sorted(set(m(u'bit_set')[2]) - set(m(u'bit_set')[0])))

# ---- 整行共用(集合交并走列表路) ----
LN = [set(pnorm(l) for l in LST[i] if len(l) >= 20 and pnorm(l)) for i in range(4)]
four(u'lines_ge20', lambda i: len(LN[i]))
for a, b in ((0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3)):
    q(u'share_%s%s' % (TAGS[a], TAGS[b]), len([x for x in LN[a] if x in LN[b]]))
q(u'share_all4', len([x for x in LN[0] if x in LN[1] and x in LN[2] and x in LN[3]]))
q(u'only_T', len([x for x in LN[0] if x not in LN[2]]))
q(u'only_F', len([x for x in LN[2] if x not in LN[0]]))
q(u'union_TF', len([x for x in LN[0]] + [x for x in LN[2] if x not in LN[0]]))
q(u'share_close_TF', m(u'share_TF') + m(u'only_T') + m(u'only_F') - m(u'union_TF'))
q(u'only_O', len([x for x in LN[1] if x not in LN[3]]))
q(u'only_N', len([x for x in LN[3] if x not in LN[1]]))
q(u'union_ON', len([x for x in LN[1]] + [x for x in LN[3] if x not in LN[1]]))
q(u'share_close_ON', m(u'share_ON') + m(u'only_O') + m(u'only_N') - m(u'union_ON'))
q(u'carry_sub_TF', len([l for l in LN[0] if l in FAN[2]]))
q(u'carry_sub_FT', len([l for l in LN[2] if l in FAN[0]]))
q(u'carry_sub_overlap', m(u'carry_sub_TF') + m(u'carry_sub_FT'))
q(u'carry_caliber_gap', m(u'carry_sub_overlap') - m(u'share_TF'))


def sents5(i):
    txt = u' '.join([l for l in LST[i] if l])
    ps = txt.replace(u'. ', u'\x00').split(u'\x00')
    return [pnorm(x) for x in ps if len(x) >= 12 and pnorm(x)]


SE = [sents5(i) for i in range(4)]
four(u'sent_n', lambda i: len(set(SE[i])))
q(u'sent_shared_TF', len([x for x in set(SE[0]) if x in set(SE[2])]))
q(u'sent_shared_ON', len([x for x in set(SE[1]) if x in set(SE[3])]))
q(u'sent_union_TF', len(set(SE[0]) | set(SE[2])))
q(u'sent_only_T', len([x for x in set(SE[0]) if x not in set(SE[2])]))
q(u'sent_only_F', len([x for x in set(SE[2]) if x not in set(SE[0])]))
q(u'sent_close_TF', m(u'sent_shared_TF') + m(u'sent_only_T') + m(u'sent_only_F') - m(u'sent_union_TF'))
q(u'sent_share_th', len([x for x in (set(SE[0]) & set(SE[2]))
                         if has(x, mt_alts([mt_lit(u'8character'), mt_lit(u'15character'),
                                            mt_lit(u'64character'), mt_lit(u'eightcharacter'),
                                            mt_lit(u'fifteencharacter')]))]))
GEN = sorted([x for x in LN[0] if x in LN[2]])
q(u'carry_shared', m(u'share_TF'))
q(u'carry_ref', len([x for x in GEN if u'sp800' in x or u'doiorg' in x or u'nistgov' in x]))
q(u'carry_toc', len([x for x in GEN if x[:1] in DIGIT]))
q(u'carry_prose', m(u'carry_shared') - m(u'carry_ref') - m(u'carry_toc'))
q(u'carry_split_close', m(u'carry_ref') + m(u'carry_toc') + m(u'carry_prose') - m(u'carry_shared'))

# ---- 锚池 ----
SPECIAL = (u'8 characters', u'eight characters', u'12 characters', u'15 characters', u'64 characters',
           u'128 characters', u'memorized secret', u'blocklist', u'composition rules',
           u'pages.nist.gov', u'SP8210', u'superseded', u'initial public draft', u'2.1.1',
           u'Memorized Secrets', u'112 bits', u'multi-factor', u'copy and paste', u'single-factor')
POOL, SEENP = [], set()
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if pnorm(l) and (t, l) not in SEENP:
            SEENP.add((t, l))
            POOL.append((t, l))
POOL.sort()
CROSSC = [sum(1 for k in range(4) if pnorm(x) in FAN[k]) for (_t, x) in POOL]
POOLC = [(POOL[j][0], CROSSC[j], POOL[j][1]) for j in range(len(POOL))]
q(u'pool_n', len(POOLC))
four(u'pool_tag_n', lambda i: len([x for x in POOLC if x[0] == TAGS[i]]))
for n in (1, 2, 3, 4):
    q(u'pool_%d' % n, len([x for x in POOLC if x[1] == n]))
q(u'pool_tiers', [m(u'pool_1'), m(u'pool_2'), m(u'pool_3'), m(u'pool_4')])
q(u'pool_close', sum(m(u'pool_tiers')) - m(u'pool_n'))
q(u'pool_maxlen', max(len(x[2]) for x in POOLC))

# ---- 锚: 直接扫条目正文 ----
MD = RD(ENTRY)
head = MD.find(u'## ⟪BabelTele⟫')
tail = MD.find(u'## ⛓解读注')
BODY = MD[head + len(u'## ⟪BabelTele⟫'):tail].strip(NL)
cur, anchors, tc = None, [], dict((t, 0) for t in TAGS)
k = 0
while k < len(BODY):
    if BODY[k] == u'⟦':
        e = BODY.find(u'⟧', k)
        cur = BODY[k + 1:e]
        if cur in tc:
            tc[cur] += 1
        k = e + 1
        continue
    if BODY[k] == u'⟨':
        e = BODY.find(u'⟩', k)
        if e > 0:
            anchors.append((cur if cur in tc else u'', BODY[k + 1:e]))
            k = e + 1
            continue
    k += 1
DIST = sorted(set(x for _t, x in anchors), key=len, reverse=True)
q(u'anchor_total', len(anchors))
q(u'anchor_distinct', len(DIST))
q(u'anchor_err', len([x for x in anchors if x[0] and pnorm(x[1]) not in FAN[IDX[x[0]]]]))
HITN = dict((a, len([k for k in range(4) if pnorm(a) in FAN[k]])) for a in DIST)
q(u'anchor_single', len([a for a in DIST if HITN[a] == 1]))
q(u'anchor_cross', len([a for a in DIST if 1 < HITN[a] < 4]))
q(u'anchor_all4', len([a for a in DIST if HITN[a] == 4]))
q(u'checks', m(u'anchor_distinct') * 4)
q(u'tag_T', tc[u'T'])
q(u'tag_O', tc[u'O'])
q(u'tag_F', tc[u'F'])
q(u'tag_N', tc[u'N'])
assert sum(tc.values()) == m(u'anchor_total'), tc
assert tc == CH[u'tag_counts'], (tc, CH[u'tag_counts'])
q(u'letters_in', sum(len([c for c in a if (u'a' <= c <= u'z' or u'A' <= c <= u'Z')]) for a in DIST))
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
q(u'letters_out', len([c for c in OUT5 if (u'a' <= c <= u'z' or u'A' <= c <= u'Z')]))
q(u'enc_self', len(BODY.replace(NL, u'')))
assert m(u'enc_self') == enc59 == CH[u'enc_chars'], (m(u'enc_self'), enc59)
ATT = [x.strip() for x in RD(u'corpus/_atoms59.txt').split(NL) if x.strip()]
# 只比内容与条数: 等长原子在两处的相对先后取决于各自的稳定序来源(set 迭代序 ⇎ 写盘序), 不可比。
assert len(ATT) == len(set(ATT)) == m(u'anchor_distinct'), (len(ATT), len(set(ATT)))
assert sorted(ATT) == sorted(DIST), u'原子清单与 _atoms59.txt 不同'

# 共用源: 这四份字节此前有没有被别的条目当过源
shared = []
for k2, v2 in sorted(SRCALL.items()):
    if k2 == TAG:
        continue
    for g in v2:
        if any(g.replace(u'\\', u'/') == x.replace(u'\\', u'/') for x in PATHS):
            shared.append((k2, g))
assert len(shared) == 0, shared

DJO = json.load(io.open(u'corpus/_deriv59.json', encoding='utf-8'))
OCC = sum(v.count(u'B59V') for v in DJO.values())
assert CH[u'deriv_keys'] == len(DJO) == 120, (CH, len(DJO))
# 两处口径不同: OCC 数 DERIV 算式串里 B59V 的字面出现次数(复合式把同一枚算式抄进 max([..]) 与 min([..]) 各一次),
# deriv_points 是建条目侧按“值→算式”登记的条数。
assert OCC == 533 and CH[u'deriv_points'] == 253, (OCC, CH[u'deriv_points'])
MISS = [k2 for k2 in FLAT if k2 not in Q5]
assert set(SNAP) == set(FLAT), (len(SNAP), len(FLAT))

# ---------- 3) 逐处替换 ----------
K = dict(FLAT)
K.update(Q5)
jt = lambda xs: u', '.join(str(x) for x in xs)
K.update({u'ln': fmt(m(u'pool_n')), u'tT': tc[u'T'], u'tO': tc[u'O'], u'tF': tc[u'F'], u'tN': tc[u'N'],
          u'coll': len(CH[u'collisions']), u'zeros': CH[u'zero_terms'],
          u'deriv_keys': CH[u'deriv_keys'], u'deriv_points': OCC, u'dedup_points': CH[u'deriv_points'],
          u'enc': enc59, u'dig': dig59, u'proofs': proofs, u'nent': NENT, u'nshared': len(shared),
          u'bytesT': fmt(m(u'bytes')[0]), u'bytesO': fmt(m(u'bytes')[1]),
          u'bytesF': fmt(m(u'bytes')[2]), u'bytesN': fmt(m(u'bytes')[3]),
          u'chT': fmt(m(u'chars')[0]), u'chO': fmt(m(u'chars')[1]),
          u'chF': fmt(m(u'chars')[2]), u'chN': fmt(m(u'chars')[3]),
          u'nbT': fmt(m(u'nonblank')[0]), u'nbO': fmt(m(u'nonblank')[1]),
          u'nbF': fmt(m(u'nonblank')[2]), u'nbN': fmt(m(u'nonblank')[3]),
          u'linesT': fmt(m(u'lines')[0]), u'linesF': fmt(m(u'lines')[2]),
          u'jsT': fmt(m(u'js_gap')[0]), u'jsF': fmt(m(u'js_gap')[2]), u'jsN': fmt(m(u'js_gap')[3]),
          u'jssum': fmt(sum(m(u'js_gap'))), u'ltF': fmt(m(u'lt_tags')[2]),
          u'entsum': fmt(sum(m(u'ent_all'))), u'poolF': fmt(m(u'pool_4')),
          u'setF': jt(m(u'ctx_set')[2]), u'setT': jt(m(u'ctx_set')[0]),
          u'setO': jt(m(u'ctx_set')[1]), u'setN': jt(m(u'ctx_set')[3]),
          u'missF': u'／'.join(m(u'asvs_ref_missF'))})

NEWPAR = (
    u'**B59 问的是同一件东西该多长, 四份一手文书给出四个答案**：`raw/pwd/nist_63b_rev3.html`（旧规范 ⟦T⟧：{bytesT} 字节／渲染 {chT} 字符／非空行 {nbT}） ⇎ '
    u'`asvs_40_v2.md`（验证标准 ⟦O⟧：{bytesO} 字节／{chO}／{nbO}, 唯一一份 Markdown） ⇎ `nist_63b_rev4.html`（新草案 ⟦F⟧：{bytesF} 字节／{chF}／{nbF}） ⇎ '
    u'`owasp_auth_cs.html`（备忘单 ⟦N⟧：{bytesN} 字节／{chN}／{nbN}）。同一把剥壳刀走两遍得两种口径: 连脚本正文一起删 ⇎ 只删标签, 差额 {jsT}⇎0⇎{jsF}⇎{jsN} 字（合计 {jssum}）, '
    u'而第二份恒为 0——它没有壳可剥；表格也有两种序列化: HTML 侧表行 {tr_rows[0]}⇎0⇎{tr_rows[2]}⇎{tr_rows[3]} 条 ⇎ Markdown 侧靠竖线 {pipe_cells[1]} 枚分格, '
    u'两份 NIST 的表行相加 {nist_row_sum} 条, 与 MD 竖线相差 {pipe_vs_row}。'
    u'门槛主账: “数+characters”语境的取值集合 [6, 8, 64] ⇎ [6, 12, 64, 128] ⇎ [4, 6, 8, 15, 64] ⇎ [8, 15, 64]（命中处数 {ctx_occ} ⇎ 不同值 {ctx_distinct} 个）; '
    u'草案把 8 写成英文词——“eight characters” 全库只有草案那 1 处, 而数字写法 “8 characters” 在旧规范 {th_digit8[0]} 处 ⇎ 草案 {th_digit8[2]} 处, '
    u'同一族里数字写法 {ctx_digit_form[2]} 处 ⇎ 词面写法 {ctx_word_form[2]} 处（相加校住 {ctx_occ[2]}, 四份闭合差 {ctx_form_close}）; '
    u'上界另有一本账: “64 characters” 四份都在 {th_digit64} ⇎ “128 characters” 只在验证标准 {th_digit128[1]} 处 ⇎ 15 出现两份 {th_digit15[2]}⇎{th_digit15[3]}。'
    u'第三方映射表整列跟着旧版失效: 验证标准 {asvs_req_rows} 条要求里 {asvs_ref_occ} 处末格填了 NIST 条款号（{asvs_ref_distinct} 枚不同）, '
    u'拿去逐字撞旧规范的 {sec_T_n} 个标题号命中 {asvs_ref_inT} 枚 ⇎ 撞草案的 {sec_F_n} 个号命中 {asvs_ref_inF} 枚（换成整篇正文再撞仍是 {asvs_ref_inT_text} ⇎ {asvs_ref_inF_text}）, '
    u'三列勾数 {asvs_tick_cols}（合计 {asvs_tick_total} ⇎ 文件里勾号 {asvs_tick_glyph} 枚 ⇎ 图例 {asvs_tick_legend} 行, 闭合差 {asvs_tick_close}）⇎ CWE 号 {asvs_cwe_distinct} 种。'
    u'术语换代可逐字核: memorized secret {tm_memorized}, 反过来 password 单数 {tm_pw_sing} ⇎ 复数 {tm_pw_plural} ⇎ 合并 {tm_pw_any}（单复相加校住, 闭合差 {tm_close}）; '
    u'强度词三档写法闭合差合计 {kw_close_sum}: 大写 SHALL {kw_shall_u} ⇎ SHOULD {kw_should_u} ⇎ MAY {kw_may_u} ⇎ MUST {kw_must_u}——四份没有一个全大写 MUST, '
    u'而小写 must {kw_must_l} 处照在（大写合计 {kw_upper_total} ⇎ 忽略大小写 {kw_ci_total}, 差额 {kw_gap}）; 同一句 composition rules 禁令从 SHOULD NOT '
    u'{comp_shouldnot} 行升为 SHALL NOT {comp_shallnot} 行; blocklist 整套机制只在草案 {mc_blocklist}（其中含 SHALL 的定义行 {blk_def_lines} 行）, '
    u'旧规范说同一件事用 blacklist {bl_blacklist} ⇎ 带空格 black list {bl_spaced}, black 词族 {bl_black}（闭合差 {bl_black_close}）⇎ 两词族全库 {bl_word_any}。'
    u'熵的位账换代: 位数集合 旧规范 {bit_set[0]} ⇎ 草案 {bit_set[2]} ⇎ 验证标准 {bit_set[1]} ⇎ 备忘单 {bit_set[3]}（草案丢 {bit_lost} ⇎ 增 {bit_new}）。'
    u'搬运记三口径: 两代 NIST 整行集交 {share_TF} 条（旧独有 {only_T} ⇎ 新独有 {only_F}, 并集 {union_TF}, 闭合差 {share_close_TF}）⇎ “在对方正文里逐字再现” {carry_sub_TF}＋{carry_sub_FT}＝{carry_sub_overlap}（比集交多 {carry_caliber_gap}）'
    u'⇎ 句子档共用 {sent_shared_TF} 句（{sent_n}, 并集 {sent_union_TF}, 闭合差 {sent_close_TF}; 含门槛数字的共用句只 {sent_share_th} 句）; '
    u'共用那 {share_TF} 行按体裁拆成参考⇎章节号⇎正文 = {carry_ref}⇎{carry_toc}⇎{carry_prose}（差 {carry_split_close}）; 两家 OWASP 文书整行共用 {share_ON} 条却共用句子 {sent_shared_ON} 句, 四份全同 {share_all4} 条。'
    u'引用形态三档: URL “pages.nist.gov” 只在验证标准 {cite_url_nist[1]} 处（写 63-3 的 {asvs_url_head} 处）⇎ 带空格 {cite_spaced} ⇎ 无空格 “SP800-63B” 只在备忘单 {cite_unspaced[3]} 处; '
    u'自我标注: 旧规范自陈被 800-63-4 废止 {cite_rev4num[0]} ⇎ 草案自标 initial public draft {cite_draftself[2]} ⇎ 草案回指 800-63-3 {cite_rev3num[2]} 处; '
    u'条款前缀也换代: “Sec.” 旧 {sec_cite_sec[0]} ⇎ 草案 {sec_cite_sec[2]}, 全词 Section {sec_cite_word}, 两式相加校住 {sec_cite_any}（闭合差 {sec_cite_close}）; '
    u'同形不同物: 串 2.1.1 在 {id_211_docs} 份文书 {id_211_occ} 处——验证标准里是带粗体的要求号（{id_211_bold} 处）, 草案里只是 Sec. 4.2.1.1 的尾巴（{id_211_occ[2]} 处）。'
    u'形状: 最长行 {maxlen} 列 ⇎ 标签字符 {lt_tags} ⇎ 实体 {ent_all} ⇎ 竖线 {pipe_cells} ⇎ 粗体对 {bold_marks} ⇎ MD 链接 {md_links} ⇎ 非 ASCII {nonascii}; 四份字节 {sig_distinct} 种签名（本遍 blake2b 8 字节, 建条目侧 sha256 前 16 位）。'
    u'锚候选池 {ln} 条（每源 {pool_tag_n}）, 穿一源 {pool_1} ⇎ 两源 {pool_2} ⇎ 三源 {pool_3} ⇎ 四源 {poolF}（相加校住池, 差 {pool_close}）; '
    u'登记锚 {anchor_total} 处／{anchor_distinct} 个不同串（每标签 T {tT} ⇎ O {tO} ⇎ F {tF} ⇎ N {tN}; 单源 {anchor_single} ⇎ 穿二或三源 {anchor_cross} ⇎ 四源全现 {anchor_all4}, 归属检查 {checks} 次, 错配 {anchor_err}）。'
    u'共用源 {nshared} 处（这四份字节此前没被任何条目当过源）。'
    u'“草案此刻是否已定稿”“备忘单那句 (NIST SP800-63B) 归给哪一版”“四份文件的抓取时刻与磁盘 mtime 先后”不可由在库文件判定，判词按第三档写、门槛不背书。\n')

# ---------- 4) README ----------
S = io.open(FM, encoding='utf-8').read()
S = sub(u'共 **58 条**（`babeltele/B01..B58`）', u'共 **{nent} 条**（`babeltele/B01..B59`）'.format(**K), S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（58 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（{nent} 条）'.format(**K), S)
S = sub(u'当前 **58 条语料／1405 条**推导全部通过（audit 自报“已机检的推导 1405 条”）',
        u'当前 **{nent} 条语料／{proofs} 条**推导全部通过（audit 自报“已机检的推导 {proofs} 条”）'.format(**K), S)

ANCHOR_OLD = (u'“抓取时刻与磁盘 mtime 的先后”不可由在库文件判定，判词按第三档写、门槛不背书。\n')
S = sub(ANCHOR_OLD, ANCHOR_OLD + NEWPAR.format(**K), S)

ROW59 = (u'| B59 | {enc}（新建, 同一个口令门槛交四份一手文书各答一遍 {anchor_total} 处标注／{anchor_distinct} 个不同串（登记 {anchor_distinct} 条锚全命中, '
         u'每标签 T {tT} ⇎ O {tO} ⇎ F {tF} ⇎ N {tN}, 归属检查 {checks} 次）: 四色锚位 旧规范 ⟦T⟧ ⇎ 验证标准 ⟦O⟧ ⇎ 新草案 ⟦F⟧ ⇎ 备忘单 ⟦N⟧; '
         u'头条是“同一个门槛四个答法”——取值集合 [6, 8, 64] ⇎ [6, 12, 64, 128] ⇎ [4, 6, 8, 15, 64] ⇎ [8, 15, 64]（处数 {ctx_occ}）, 草案的 8 是英文词 {ctx_word_form[2]} 处 ⇎ 数字 {th_digit8[2]} 处, '
         u'记法两档相加校住 {ctx_occ[2]}（闭合差 {ctx_form_close}）; 上界 64 四份都在 {th_digit64} ⇎ 128 只在验证标准 {th_digit128[1]}; '
         u'第三方映射 {asvs_req_rows} 行要求／{asvs_ref_occ} 处带号／{asvs_ref_distinct} 枚不同号撞两版标题号集 {asvs_ref_inT}⇎{asvs_ref_inF}（整篇再撞仍 {asvs_ref_inT_text}⇎{asvs_ref_inF_text}, 未命中 {asvs_ref_distinct} 枚 ⇎ 0 枚）; '
         u'术语 memorized secret {tm_memorized} ⇎ password 单 {tm_pw_sing}／复 {tm_pw_plural}／合 {tm_pw_any}（闭合 {tm_close}）; '
         u'强度词三账 {kw_close_sum}: 大写 SHALL {kw_shall_u} ⇎ MUST 全库 {must_upper_all4} ⇎ 小写 must {kw_must_l} ⇎ 差额 {kw_gap}; 同条禁令 SHOULD NOT {comp_shouldnot}→SHALL NOT {comp_shallnot}; '
         u'blocklist 只在草案 {mc_blocklist}（定义行 {blk_def_lines}）⇎ blacklist {bl_blacklist} ⇎ 分写 {bl_spaced}（black 族 {bl_black}, 两族 {bl_word_any}, 闭合 {bl_word_close}）; 位数集 {bit_set[0]}→{bit_set[2]}（丢 {bit_lost} 增 {bit_new}）; '
         u'搬运三口径 整行 {share_TF} ⇎ 子串再现 {carry_sub_overlap}（口径差 {carry_caliber_gap}）⇎ 句子 {sent_shared_TF}, 共用行体裁 {carry_ref}⇎{carry_toc}⇎{carry_prose}; '
         u'两家 OWASP 整行 {share_ON} ⇎ 句子 {sent_shared_ON}; 引用形态 URL {cite_url_nist[1]} ⇎ 带空格 {cite_spaced} ⇎ 无空格 {cite_unspaced[3]} ⇎ 前缀 Sec. {sec_cite_sec[2]} ⇎ Section {sec_cite_word}; '
         u'同形 2.1.1 在 {id_211_docs} 份 {id_211_occ} 处 ⇎ 5.1.1.2 {asvs_5112}; 形状 最长行 {maxlen} ⇎ 标签 {lt_tags} ⇎ 实体 {ent_all} ⇎ 竖线 {pipe_cells} ⇎ 两口径差 {js_gap}; '
         u'锚池 {ln} 条穿四源 {poolF} ⇎ 三源 {pool_3}; 同数共键复合式 {coll} 组、零项 {zeros} 枚折成一条算式; 门槛侧 {deriv_keys} 枚推导键／{deriv_points} 处 B59V 引用点（建条目侧按“值→算式”去重记 {dedup_points}）, '
         u'五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对 {anchor_distinct} 条锚逐字全命中, 工具侧 atomcheck 另核 ok={anchor_distinct} bad=0） |\n')
anchor_row = (u'五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对 18 条锚逐字全命中, 工具侧 atomcheck 另核 ok=18 bad=0） |\n')
assert S.count(anchor_row) == 1
S = sub(anchor_row, anchor_row + ROW59.format(**K), S)

lin = (u'第二代（B11–B58）锚内字母 **119 788**、锚外 **13 372**；全库合计 **119 909／15 567**'
       u'（B58 一枚条目贡献 994／606, 由建条目侧现数）')
S = sub(lin, (u'第二代（B11–B59）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
              u'（B59 一枚条目贡献 %s／%s, 由建条目侧现数）'
              % (fmt(119788 + CH[u'letters_in']), fmt(13372 + CH[u'letters_out']),
                 fmt(119909 + CH[u'letters_in']), fmt(15567 + CH[u'letters_out']),
                 fmt(CH[u'letters_in']), fmt(CH[u'letters_out']))), S)

RAW59 = (u'| B59 | `raw/pwd/nist_63b_rev3.html`（旧规范 ⟦T⟧：{bytesT} 字节／行数 {lines[0]}／非空行 {nbT}／渲染 {chT} 字符／表行 {tr_rows[0]} 条／“8 characters” {th_digit8[0]} 处） ⇎ '
         u'`raw/pwd/asvs_40_v2.md`（验证标准 ⟦O⟧：{bytesO} 字节／{lines[1]}／{nbO}／{chO}／竖线 {pipe_cells[1]} 枚／粗体对 {bold_marks[1]}／“12 characters” {th_digit12[1]} 处） ⇎ '
         u'`raw/pwd/nist_63b_rev4.html`（新草案 ⟦F⟧：{bytesF} 字节／行数 {linesF}／{nbF}／{chF}／表行 {tr_rows[2]} 条／“eight characters” {th_word_eight[2]} 处／blocklist {mc_blocklist[2]} 处） ⇎ '
         u'`raw/pwd/owasp_auth_cs.html`（备忘单 ⟦N⟧：{bytesN} 字节／{lines[3]}／{nbN}／{chN}／表行 {tr_rows[3]} 条／“15 characters” {th_digit15[3]} 处／SP800-63B {cite_unspaced[3]} 处） | '
         u'同一个口令门槛问四份文书 ⇒ 旧规范 8（数字）⇎ 验证标准 12（并写“超过 128 拒收”）⇎ 草案 15 且把 8 写成英文词并首次请出 blocklist ⇎ 备忘单把 8 与 15 一起归给 “NIST SP800-63B” 而不说哪一版；'
         u'验证标准的 {asvs_ref_distinct} 枚映射号命中旧版标题集 {asvs_ref_inT} ⇎ 命中草案 {asvs_ref_inF}, 两代 NIST 整行只共用 {share_TF} 条|\n')
anchor2 = (u'抽样 29 条两代公式都复算得出（29⇎29）|\n')
assert S.count(anchor2) == 1
S = sub(anchor2, anchor2 + RAW59.format(**K), S)

row_tot = (u'| **合计（{nent} 条）** | **{enct}** | **{rett}**（摘要段合计 {digt}） | — | **{unqt}** | — |\n').format(
    nent=NENT, enct=fmt(enc_all).replace(u',', u' '), rett=ret_tot,
    digt=fmt(dig_all).replace(u',', u' '), unqt=fmt(uniq_all).replace(u',', u' '))
old_tot = re.search(u'[|] [*]{2}合计（58 条）[*]{2}[^\n]*\n', S)
assert old_tot
S = S.replace(old_tot.group(0), row_tot)

tail_old = (u'新建的 B54 ⇎ B56 ⇎ B57 ⇎ B58 同样为空——B58 把两位以内的结构计数全部折进了 DERIV'
            u'（0 项 112 枚并成一条算式，由 _b58_scan 照样复算；另有 35 处跨值复合式））未逐位核验，')
assert S.count(tail_old) == 1
S = sub(tail_old, (u'新建的 B54 ⇎ B56 ⇎ B57 ⇎ B58 ⇎ B59 同样为空——B59 把两位以内的结构计数全部折进了 DERIV'
                   u'（0 项 %d 枚并成一条算式，由 _b59_scan 照样复算；另有 %d 处跨值复合式））未逐位核验，'
                   % (CH[u'zero_terms'], len(CH[u'collisions']))), S)
S = sub(u'残余提示（不计 FAIL）：20 个', u'残余提示（不计 FAIL）：%d 个' % soft_all, S)

WL, WR = 160, 200
CMD = (u'python -X utf8 corpus/_mkB59.py                  # 建条目: 扁平契约 %d 枚键／DERIV %d 枚算式, 占位符未替换 0 个\n'
       u'python -X utf8 corpus/_mkdigest3.py B59 <entry> T corpus/raw/pwd/nist_63b_rev3.html %d %d '
       u'O corpus/raw/pwd/asvs_40_v2.md %d %d F corpus/raw/pwd/nist_63b_rev4.html %d %d '
       u'N corpus/raw/pwd/owasp_auth_cs.html %d %d   # 四源分节摘要(%s 字符, 窗口按 %d⇎%d 取句边界)\n'
       u'python -X utf8 corpus/_wire59.py                    # 把 SCAN 段机械切进 audit.py::_b59_scan 并插 DERIV[\'B59\']\n'
       u'python -X utf8 corpus/_fill59.py                    # 第四遍: 现取注数并把 ⛓解读注 写回条目(与契约 %d 键逐一对表)\n'
       u'python -X utf8 corpus/atomcheck.py B59 corpus/_atoms59.txt   # 工具侧独立逐字校验: ok=%d bad=0\n'
       % (len(FLAT), CH[u'deriv_keys'], WL, WR, WL, WR, WL, WR, WL, WR,
          fmt(dig59).replace(u',', u' '), WL, WR, len(FLAT), m(u'anchor_distinct')))
anchor3 = u'python -X utf8 corpus/atomcheck.py B58 corpus/_atoms58.txt   # 工具侧独立逐字校验: ok=18 bad=0' + NL
assert S.count(anchor3) == 1
S = sub(anchor3, anchor3 + CMD, S)

io.open(FM, 'w', encoding='utf-8', newline=NL).write(S)
print(u'README 已记账: %d 条 ｜ 编码合计 %s ⇎ 摘要合计 %s ⇎ 合计保留率 %s ｜ 唯一码点 %d ｜ 推导 %d 条 ｜ 提示 %d（清单 %s） ｜ '
      u'B59 %s 字符／%d 锚(%d 串, T %d⇎O %d⇎F %d⇎N %d, 单源 %d⇎穿二三 %d⇎四源 %d, 检查 %d) ｜ '
      u'第五遍: 现量 %d 个键全等契约⇎快照（未复量的 %d 键直接取契约） ｜ 门槛四集 %s ⇎ 记法 %s⇎%s ⇎ 映射命中 %d⇎%d ⇎ 整行共用 %d ⇎ 句子共用 %d ⇎ '
      u'两口径差 %s ⇎ 最长行 %s ⇎ 锚池 %s ｜ blake2b 签名 %d 种 ｜ 共用源 %d 处 ｜ 复合式 %d 组⇎零项 %d 枚 ｜ 仅本遍新键 %s'
      % (NENT, fmt(enc_all), fmt(dig_all), ret_tot, uniq_all, proofs, soft_all,
         u' '.join(sorted(HINT)), fmt(enc59), m(u'anchor_total'), m(u'anchor_distinct'),
         tc[u'T'], tc[u'O'], tc[u'F'], tc[u'N'], m(u'anchor_single'), m(u'anchor_cross'),
         m(u'anchor_all4'), m(u'checks'), len(Q5), len(MISS),
         u' ⇎ '.join(u'[%s]' % u', '.join(str(y) for y in x) for x in m(u'ctx_set')),
         m(u'ctx_digit_form'), m(u'ctx_word_form'), m(u'asvs_ref_inT'), m(u'asvs_ref_inF'),
         m(u'share_TF'), m(u'sent_shared_TF'), u'⇎'.join(str(x) for x in m(u'js_gap')),
         u'⇎'.join(str(x) for x in m(u'maxlen')), fmt(m(u'pool_n')), m(u'sig_distinct'),
         len(shared), len(CH[u'collisions']), CH[u'zero_terms'],
         u' '.join(sorted(k2 for k2 in Q5 if k2 not in FLAT and k2 not in SNAP))))
