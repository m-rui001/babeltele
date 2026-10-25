# -*- coding: utf-8 -*-
"""建条目第二遍(B99): 一条 TLS 记录最多装多少明文——16385 与它旁边那几个数
五份一手文书同答一副记录尺寸题, 各取一支幂式分叉:
8446(2018 TLS 1.3: 明文 2^14 ⇎ 内层明文 2^14+1 ⇎ 密文 2^14+256, 并把 256 拆成 “1 octet for ContentType
+ 最大 AEAD 膨胀 255 octets”; 2^14+1 那式被 72 列硬换行切成 “2^14” 与 “+ 1 octets” 两段)
⇎ 5246(2008 TLS 1.2: 明文 2^14 ⇎ 压缩后 2^14+1024 ⇎ 加密后 2^14+2048; 同一份里结构体定义带空格写
“2^14 + 1024” ⇎ record_overflow 告警段不带空格写 “2^14+2048”, 是同一族常量的两种序列化)
⇎ 8449(2018 record_size_limit: 把 1.2 的 2^14 与 1.3 的 2^14+1 并排写进一句, 另给下限 64 ⇎ “18K” 内存档
⇎ 6066 四档最高只到 2^12)
⇎ 6066(2011 max_fragment_length: 四档 2^9(1) 2^10(2) 2^11(3) 2^12(4) 与 (255) 保留位, 指数−码位恒等于 8;
805 字节展开式 5+512+256+32)
⇎ OpenSSL split_send_fragment.pod(实现侧一手文档: SSL3_RT_MAX_PLAIN_LENGTH (16384) ⇎ 取值区间
512 - SSL3_RT_MAX_PLAIN_LENGTH ⇎ SSL_MAX_PIPELINES (32) ⇎ 读缓冲至少 16704 ⇎ 四条
TLSEXT_max_fragment_length_* 十进制档, 只有 512 那一档写了单位 bytes)。

本遍与采集遍(_pick99.py)换机制而不换定义, 九处:
①行尺: 采集侧 splitlines()(把 \\x0c 也算行界) ⇎ 本遍 split('\\n') 一档另加逐行读入第三轨;
②字面针: 采集侧游标 find 环 ⇎ 本遍整串 re.findall(re.escape), 另立重叠档 (?=针);
③词核归属: 采集侧集合 & 运算(set ∋ w) ⇎ 本遍 Counter 频次档(cnt[w] > 0), 成员判定逐键对账;
④切句: 采集侧逐字符扫“句末标点+空白” ⇎ 本遍 (?<=[.!?]) + 一条正则切;
⑤定界: 采集侧按编号节标题现定界(标题→下一枚同级或更高级标题) ⇎ 本遍固定 260 行滑窗开窗后在窗内截;
⑥行号尺: 采集侧逐字符行号表(每枚字符现挂原行下标) ⇎ 本遍累积长度表 + bisect 由面偏移直映原行;
⑦幂式与数值: 采集侧两遍扫描(先取跨度再就地读邻接空白与加数) ⇎ 本遍一条三分支正则(裸幂/带加数/带码位)现分叉;
⑧四档扩展值: 采集侧正则级联 2\\^(\\d+)\\((\\d+)\\) 现取 ⇎ 本遍按四字面档枚枚举并用手工切片(不经正则)拆出(指数,码位);
⑨归一口径: 采集侧幂式接合处用 re.sub 折平 ⇎ 本遍逐字符跳空白手工接合, 两档面串必须逐字符同;
另: 整词尺采集侧用负向断言正则 ⇎ 本遍先把全串翻成三张布尔表再查表读左右邻(第三轨才是邻居字符手扫)。
四档口径: 原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳+幂式归一折平(第三⇎第四档之差只由被硬换行推开的加号贡献)。
所有正文数字由 V()/J()/EXPR() 注册后插值, 一枚都不手打; 锚一律由面上位置导出。"""
import io, json, os, re, sys
import bisect
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'8446', u'5246', u'8449', u'6066', u'pod']
IDS = [u'rfc8446', u'rfc5246', u'rfc8449', u'rfc6066', u'openssl-pod']
PATH = [u'corpus/raw/tlsrec99/rfc8446.txt', u'corpus/raw/tlsrec99/rfc5246.txt',
        u'corpus/raw/tlsrec99/rfc8449.txt', u'corpus/raw/tlsrec99/rfc6066.txt',
        u'corpus/raw/tlsrec99/openssl_max_send_fragment.pod']
NSRC = 5
FAM = [u'tls13', u'tls12', u'ext', u'ext', u'impl']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN ---


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
# 机制①: 本遍的行尺走 split('\n'); splitlines 只作为对账的另一轨(它把 \x0c 也当行界)
RAWL = [T[i].split(NL) for i in range(NSRC)]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]


def pnorm(s):
    """整串折平一把尺: re.sub 一次成串(采集侧是 ' '.join(s.split()) 的词表法)。"""
    return re.sub(u'\\s+', u' ', s.lower()).strip()


def fold(s):
    return u' '.join([x for x in re.split(u'\\s+', s) if x != u''])


def cnt_cur(hay, nd):
    """采集侧那一把(游标 find 环), 本遍只用于对拍。"""
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def cnt_re(hay, nd):
    """本遍的字面针轨: 转义后整串正则扫描(采集侧是游标环)。"""
    return len(re.findall(re.escape(nd), hay))


def cnt_ovl(hay, nd):
    """重叠档: 同一处允许被后面那次命中起点复用。"""
    return len(re.findall(u'(?=%s)' % re.escape(nd), hay))


def _tabs(s):
    return ([c.isalpha() for c in s], [c.isdigit() for c in s], [c.isalnum() for c in s])


def ub_tab(s, w, fl, kind=u'alpha'):
    """本遍的整词尺: 命中后查布尔表读左右邻(采集侧是负向断言正则)。"""
    al, dg, an = fl
    t = al if kind == u'alpha' else dg if kind == u'digit' else an
    c, i, n, m = 0, 0, len(w), len(s)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if not (a >= 0 and t[a]) and not (b < m and t[b]):
            c += 1
        i = j + 1


def ub_cur(s, w, kind=u'alpha'):
    """第三轨: 邻居字符手扫(既不是本遍也不是采集侧那把, 用来第三方定数)。"""
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        a, b = j - 1, j + n
        if kind == u'alpha':
            ok = not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha())
        elif kind == u'digit':
            ok = not (a >= 0 and s[a].isdigit()) and not (b < len(s) and s[b].isdigit())
        else:
            ok = not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())
        if ok:
            c += 1
        i = j + 1


def ub_re(s, w, kind=u'alpha'):
    """采集侧那一把(负向断言正则), 本遍只用于对拍。"""
    a = u'(?<![A-Za-z])' if kind == u'alpha' else u'(?<![0-9a-z])'
    b = u'(?![A-Za-z])' if kind == u'alpha' else u'(?![0-9a-z])'
    return len(re.findall(a + re.escape(w) + b, s))


def is_shell_pick(x):
    """采集侧壳谓词的逐字照抄(整行序列正则), 供两遍壳集对拍用。"""
    if re.search(u'\\[Page \\d+\\]', x):
        return True
    if re.match(u'^RFC \\d{4}\\s+\\S.*\\s((19|20)\\d\\d)\\s*$', x):
        return True
    if re.match(u'^\\s*(Internet Engineering Task Force|Internet-Draft)', x):
        return True
    if x[:1] == u'=':
        return True
    if x == u'\x0c':
        return True
    return x.strip() == u''


def _yearish(w):
    return len(w) == 4 and w.isdigit() and (w[:2] == u'19' or w[:2] == u'20')


def sh_blank(x):
    return x.strip() == u''


def sh_ff(x):
    return x == u'\x0c'


def sh_foot(x):
    t = x.strip().split()
    return len(t) >= 2 and t[-2] == u'[Page' and t[-1].endswith(u']') and t[-1][:-1].isdigit()


def sh_hdr(x):
    """眉行的 token 尺: 首 token 是 RFC + 一枚四位数, 末 token 是年形, 且中间还有正文列。"""
    t = x.strip().split()
    return len(t) >= 4 and t[0] == u'RFC' and len(t[1]) == 4 and t[1].isdigit() and _yearish(t[-1])


def sh_ietf(x):
    t = x.strip().split()
    return t[:4] == [u'Internet', u'Engineering', u'Task', u'Force'] or t[:1] == [u'Internet-Draft']


def sh_podmark(x):
    return x[:1] == u'='


def is_powernum_pick(x):
    """采集侧那一把(整行只有数字与空白 + 只含一段数字)。"""
    if x.strip() == u'':
        return False
    if [c for c in x if not (c.isdigit() or c.isspace())]:
        return False
    return len([m for m in re.finditer(u'(?<![0-9])[0-9]+(?![0-9])', x)]) == 1


def sh_barenum(x):
    """本遍的裸页码尺: strip 后按 token 拆, 每一枚 token 都是纯数字才算一枚裸数。"""
    t = x.strip().split()
    return bool(t) and all([w.isdigit() for w in t]) and len(t) == 1


def shell_shape(x):
    """本遍壳谓词: strip 后按 token 形状判, 一枚序列正则也不跑。"""
    return (sh_blank(x) or sh_ff(x) or sh_foot(x) or sh_hdr(x) or sh_ietf(x) or sh_podmark(x))


# ---------- 0. 面量 ⇎ 行式三轨 ⇎ 换页账 ----------
F['bytes'] = [len(B[i]) for i in range(NSRC)]
F['bytes_stat'] = [os.path.getsize(p) for p in PATH]
F['cp'] = [sum(1 for _ in T[i]) for i in range(NSRC)]        # 逐字符计数, 不用 len()
F['n_lf'] = [len([m.start() for m in re.finditer(u'\\n', T[i])]) for i in range(NSRC)]
F['n_cr'] = [len([m.start() for m in re.finditer(u'\\r', T[i])]) for i in range(NSRC)]
F['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
F['splitlines'] = [len(T[i].splitlines()) for i in range(NSRC)]
F['readlines'] = [sum(1 for _ in io.StringIO(T[i])) for i in range(NSRC)]
F['ff'] = [cnt_re(T[i], u'\x0c') for i in range(NSRC)]
F['ff_before_nl'] = [cnt_ovl(T[i], u'\x0c' + NL) for i in range(NSRC)]
F['ff_alone'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
F['trailing_nl'] = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
F['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
F['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
F['tab'] = [cnt_re(T[i], u'\t') for i in range(NSRC)]
F['bom'] = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
NAOFF = [[m.start() for m in re.finditer(u'[^\\x00-\\x7f]', T[i])] for i in range(NSRC)]
F['na_total'] = [len(NAOFF[i]) for i in range(NSRC)]
F['nonascii'] = [sorted(set(ord(T[i][k]) for k in NAOFF[i])) for i in range(NSRC)]
F['utf8_extra'] = [F['bytes'][i] - F['cp'][i] for i in range(NSRC)]
F['rows_ledger'] = [F['splitlines'][i] - F['splitnl'][i] for i in range(NSRC)]
F['rows_pred'] = [F['ff_before_nl'][i] - F['trailing_nl'][i] for i in range(NSRC)]
F['rows_ledger_diff'] = [F['rows_ledger'][i] - F['rows_pred'][i] for i in range(NSRC)]
F['line_split_ledger'] = [F['nonblank'][i] + F['blank'][i] - F['splitnl'][i] for i in range(NSRC)]
F['bytes_vs_stat'] = 0 if F['bytes'] == F['bytes_stat'] else 1
F['lf_vs_readlines'] = [F['readlines'][i] + F['trailing_nl'][i] - F['splitnl'][i] for i in range(NSRC)]
F['rows_scale_diff'] = [F['splitlines'][i] - F['splitnl'][i] - F['ff_before_nl'][i] + F['trailing_nl'][i]
                       for i in range(NSRC)]
print(u'0 面量:', json.dumps(dict((k, F[k]) for k in
      ['bytes', 'cp', 'n_lf', 'splitnl', 'splitlines', 'readlines', 'ff', 'ff_before_nl', 'trailing_nl',
       'blank', 'nonblank', 'maxlen', 'tab', 'bom', 'rows_ledger', 'rows_pred'])))
print(u'  非ASCII:', F['na_total'], u' 行尺三轨分差:', F['lf_vs_readlines'])

# ---------- 1. 壳账: 页壳 ⇎ pod 标记壳 ----------
F['foot_page'] = [len([x for x in L[i] if sh_foot(x)]) for i in range(NSRC)]
F['hdr_rfc'] = [len([x for x in L[i] if sh_hdr(x)]) for i in range(NSRC)]
F['ietf_alone'] = [len([x for x in L[i] if sh_ietf(x)]) for i in range(NSRC)]
F['podmark'] = [len([x for x in L[i] if sh_podmark(x)]) for i in range(NSRC)]
F['pod_head1'] = [len([x for x in L[i] if x.startswith(u'=head1')]) for i in range(NSRC)]
F['pod_item'] = [len([x for x in L[i] if x.startswith(u'=item')]) for i in range(NSRC)]
F['pod_block'] = [len([x for x in L[i] if x.startswith((u'=over', u'=back'))]) for i in range(NSRC)]
F['pgnum'] = [len([x for x in L[i] if sh_barenum(x)]) for i in range(NSRC)]
F['pgnum_pick'] = [len([x for x in L[i] if is_powernum_pick(x)]) for i in range(NSRC)]
F['pgnum_ruler_diff'] = [F['pgnum'][i] - F['pgnum_pick'][i] for i in range(NSRC)]
F['shell_pick'] = [len([1 for x in L[i] if is_shell_pick(x)]) for i in range(NSRC)]
F['shell_shape'] = [len([1 for x in L[i] if shell_shape(x)]) for i in range(NSRC)]
F['shell_pred_diff'] = [len([1 for x in L[i] if is_shell_pick(x) != shell_shape(x)]) for i in range(NSRC)]
F['shell_lines'] = F['shell_shape']
F['body_lines'] = [len([1 for x in L[i] if not shell_shape(x)]) for i in range(NSRC)]
SHPREDS = [sh_blank, sh_ff, sh_foot, sh_hdr, sh_ietf, sh_podmark]
F['shape_hits'] = [sum([len([1 for x in L[i] if g(x)]) for g in SHPREDS]) for i in range(NSRC)]
F['shape_ovl'] = [sum([max(0, len([1 for g in SHPREDS if g(x)]) - 1) for x in L[i]]) for i in range(NSRC)]
F['shell_ledger'] = [F['shell_lines'][i] - (F['shape_hits'][i] - F['shape_ovl'][i]) for i in range(NSRC)]
F['body_shell_ledger'] = [F['body_lines'][i] + F['shell_lines'][i] - F['splitnl'][i] for i in range(NSRC)]
YEARS = []
for i in range(NSRC):
    hh = [x.strip().split() for x in L[i] if sh_hdr(x)]
    if hh:
        yrs = sorted(set([z[-1] for z in hh]))
    else:
        cr = re.findall(u'Copyright (\\d{4})-(\\d{4})', T[i])
        yrs = sorted(set([cr[0][0], cr[0][1]])) if cr else []
    YEARS.append(yrs)
F['face_years'] = YEARS
F['hdr_year_set'] = [len(set(Y)) for Y in YEARS]
print(u'1 壳行(正则尺/形状尺):', F['shell_pick'], F['shell_shape'], u' 逐行分歧', F['shell_pred_diff'],
      u' 页脚', F['foot_page'], u' 眉行', F['hdr_rfc'], u' pod标记', F['podmark'], u' 裸数行', F['pgnum'])
print(u'  面上年份:', YEARS)

# ---------- 2. 幂式族: 一条三分支正则(机制⑦) ⇎ 采集侧两遍扫描 ----------
RX_POW = re.compile(u'2\\^(\\d+(?:\\.\\d+)?)'
                    u'(?: \\+ (\\d+)|\\+(\\d+)|\\((\\d+)\\))?')


def pow_all(face):
    """本遍的幂式尺: 一条正则三叉(空叉=裸幂 ⇎ 空格加数 ⇎ 紧写加数 ⇎ 括号码位)现取;
       空白档由命中串自身判(采集侧是两遍扫描逐字符读邻接空白)。"""
    out = []
    for m in RX_POW.finditer(face):
        g0 = m.group(0)
        d = m.group(1)
        tail = g0[2 + len(d):]
        if m.group(2):
            out.append((d, m.group(2), u'', u' ', tail))
        elif m.group(3):
            out.append((d, m.group(3), u'', u'', tail))
        elif m.group(4):
            out.append((d, u'', m.group(4), u'', tail))
        else:
            out.append((d, u'', u'', u'', tail))
    return out


POW = [pow_all(fold(T[i])) for i in range(NSRC)]
F['pow_all'] = [[list(z[:4]) for z in POW[i]] for i in range(NSRC)]
F['pow2_mark'] = [cnt_re(fold(T[i]), u'2^') for i in range(NSRC)]
F['pow_empty_marker'] = [F['pow2_mark'][i] - len(POW[i]) for i in range(NSRC)]
F['pow_exp_hist'] = [dict((e, len([z for z in POW[i] if z[0] == e]))
                          for e in sorted({z[0] for z in POW[i]}, key=lambda x: float(x)))
                     for i in range(NSRC)]
F['pow_exp_kinds'] = [len(F['pow_exp_hist'][i]) for i in range(NSRC)]
F['pow14_n'] = [len([z for z in POW[i] if z[0] == u'14']) for i in range(NSRC)]
F['pow_bare14'] = [len([z for z in POW[i] if z[0] == u'14' and z[1] == u'']) for i in range(NSRC)]
F['pow_off_spaced'] = [len([z for z in POW[i] if z[1] and z[3] == u' ']) for i in range(NSRC)]
F['pow_off_tight'] = [len([z for z in POW[i] if z[1] and z[3] == u'']) for i in range(NSRC)]
F['pow_offset_vals'] = [[z[1] for z in POW[i] if z[0] == u'14' and z[1]] for i in range(NSRC)]
F['pow_enum'] = [[(z[0], z[2]) for z in POW[i] if z[2]] for i in range(NSRC)]
F['pow_frac'] = [[z[0] for z in POW[i] if u'.' in z[0]] for i in range(NSRC)]
F['pow_off_all'] = [sorted(set([z[1] for z in POW[i] if z[1]])) for i in range(NSRC)]
F['pow_mark_ledger'] = [F['pow2_mark'][i] - len(POW[i]) - F['pow_empty_marker'][i] for i in range(NSRC)]
print(u'2 幂式(三分支): 2^14 枚数', F['pow14_n'], u' 裸档', F['pow_bare14'], u' 空格加档', F['pow_off_spaced'],
      u' 紧写加档', F['pow_off_tight'], u' 加数清单', F['pow_offset_vals'])
print(u'   指数直方:', F['pow_exp_hist'], u' 空标记', F['pow_empty_marker'])

# ---------- 3. 折平面族 ⇎ 十进制整词尺(布尔表 ⇎ 断言正则 ⇎ 邻居手扫, 三轨) ----------
ALLR = [[(k, L[i][k]) for k in range(len(L[i]))] for i in range(NSRC)]
NSR = [[(k, L[i][k]) for k in range(len(L[i])) if not shell_shape(L[i][k])] for i in range(NSRC)]


def face_from(rows):
    """行区间 → 折平面 + 累积长度表(机制⑥: 面偏移由 bisect 映回原行, 采集侧是逐字符行号表)。"""
    parts, ends = [], []
    tot = 0
    for r, x in rows:
        fx = pnorm(x)
        if fx == u'':
            continue
        if parts:
            parts.append(u' ')
            tot += 1
        parts.append(fx)
        tot += len(fx)
        ends.append((tot, r))
    return u''.join(parts), ends


FOL, ENDA = zip(*[face_from(ALLR[i]) for i in range(NSRC)])
SHF, ENDB = zip(*[face_from(NSR[i]) for i in range(NSRC)])
FOL, ENDA, SHF, ENDB = list(FOL), list(ENDA), list(SHF), list(ENDB)
OFFA = [[z[0] for z in ENDA[i]] for i in range(NSRC)]
OFFB = [[z[0] for z in ENDB[i]] for i in range(NSRC)]


def row_of(i, off, whole=1):
    """本遍行号尺: 累积长度表 + bisect(采集侧那把是逐字符现挂行下标)。"""
    os_ = OFFA[i] if whole else OFFB[i]
    tab = ENDA[i] if whole else ENDB[i]
    k = bisect.bisect_right(os_, off)
    return tab[k][1] if k < len(tab) else -1


def pownorm_char(s):
    """机制⑨: 逐字符接合幂式加号(采集侧是一条 re.sub 整串替换)。"""
    out, i, n = [], 0, len(s)
    while i < n:
        if s[i] == u'2' and s[i + 1:i + 2] == u'^' and s[i + 2:i + 3].isdigit():
            j = i + 2
            while j < n and s[j].isdigit():
                j += 1
            out.append(s[i:j])
            k = j
            while k < n and s[k] == u' ':
                k += 1
            if s[k:k + 1] == u'+':
                m = k + 1
                while m < n and s[m] == u' ':
                    m += 1
                d = u''
                while m < n and s[m].isdigit():
                    d += s[m]
                    m += 1
                if d != u'':
                    out.append(u'+' + d)
                    i = m
                    continue
            i = j
            continue
        out.append(s[i])
        i += 1
    return u''.join(out)


def pownorm_re(s):
    """采集侧那一把: 只归一幂式接合处的空白。"""
    return re.sub(u'(2\\^\\d+)\\s+\\+\\s+(\\d+)', u'\\1+\\2', s)


SHN = [pownorm_char(SHF[i]) for i in range(NSRC)]
F['face_all'] = [len(FOL[i]) for i in range(NSRC)]


def sh_edgeface(i):
    """同一张摘壳面的第二种构法: 逐行折平后按“邻行皆收口才补空格”拼接(采集侧的行号表走的就是这一张)."""
    out = u''
    for x in L[i]:
        if shell_shape(x):
            continue
        head = u' ' if (x[:1] != u'' and x[0].isspace()) else u''
        tail = u' ' if (x[-1:] != u'' and x[-1:].isspace()) else u''
        out += head + fold(x) + tail
    return re.sub(u' +', u' ', out)


F['face_sh'] = [len(SHF[i]) for i in range(NSRC)]
F['face_sh_edge'] = [sh_edgeface(i) for i in range(NSRC)]
F['face_sh_edge_len'] = [len(z) for z in F['face_sh_edge']]
F['face_sh_two_len_diff'] = [F['face_sh_edge_len'][i] - F['face_sh'][i] for i in range(NSRC)]
F['face_sh_two_cp_diff'] = [len([1 for k in range(min(len(F['face_sh_edge'][i]), len(SHF[i])))
                                 if F['face_sh_edge'][i][k] != SHF[i][k]]) for i in range(NSRC)]
F['face_rows_kept'] = [len(NSR[i]) for i in range(NSRC)]
F['face_rows_all'] = [len(ALLR[i]) for i in range(NSRC)]
F['face_rows_ledger'] = [F['face_rows_kept'][i] + F['shell_lines'][i] - F['face_rows_all'][i]
                         for i in range(NSRC)]
F['pow_ruler_same'] = [1 if pownorm_char(SHF[i]) == pownorm_re(SHF[i]) else 0 for i in range(NSRC)]
F['pow_gain_cells'] = [cnt_re(SHN[i], u'2^14+1') - cnt_re(SHF[i], u'2^14+1') for i in range(NSRC)]
F['pow_spread'] = [F['face_sh'][i] - len(SHN[i]) for i in range(NSRC)]
DECF = [u'512', u'1024', u'2048', u'4096', u'16384', u'16385', u'16640', u'17408', u'18432',
        u'16704', u'805', u'64', u'255', u'32', u'16', u'8', u'256', u'5']
TB = [_tabs(FOL[i]) for i in range(NSRC)]
F['dec_word'] = [[ub_tab(FOL[i], v, TB[i], u'alnum') for v in DECF] for i in range(NSRC)]
F['dec_re'] = [[ub_re(FOL[i], v, u'digit') for v in DECF] for i in range(NSRC)]
F['dec_sub'] = [[cnt_cur(FOL[i], v) for v in DECF] for i in range(NSRC)]
F['dec_ruler_diff'] = [sum([abs(F['dec_word'][i][k] - F['dec_re'][i][k]) for k in range(len(DECF))])
                       for i in range(NSRC)]
F['dec_diff'] = [[F['dec_sub'][i][k] - F['dec_word'][i][k] for k in range(len(DECF))]
                 for i in range(NSRC)]
F['dec_third'] = [sum([abs(ub_cur(FOL[i], v, u'alnum') - F['dec_word'][i][k])
                       for k, v in enumerate(DECF)]) for i in range(NSRC)]
print(u'3 十进制整词尺(布尔表):')
for i in range(NSRC):
    print(u'   %-5s %s' % (LBL[i], F['dec_word'][i]))
print(u'   子串尺−整词尺:', F['dec_diff'])
print(u'   三轨分歧(本遍 ⇎ 采集正则):', F['dec_ruler_diff'], u' 第三轨手扫差:', F['dec_third'])

# ---------- 4. 判词针四档 ----------
NEEDLES = [
    u'records carrying data in chunks of 2^14 bytes or less',
    u'The length MUST NOT exceed 2^14 bytes',
    u'The length MUST NOT exceed 2^14.',
    u'The length MUST NOT exceed 2^14 + 1024.',
    u'The length MUST NOT exceed 2^14 + 2048.',
    u'The length MUST NOT exceed 2^14 + 256 bytes',
    u'the full encoded TLSInnerPlaintext MUST NOT exceed 2^14 + 1 octets',
    u'TLS 1.3 uses a limit of 2^14+1 octets',
    u'that limit is 2^14 octets',
    u'permit senders to generate records 16384 octets in size',
    u'up to 2048 octets',
    u'the allowance for expansion to 256 octets',
    u'Allocating up to 18K of memory for ciphertext',
    u'The maximum value that the extension permits is 2^12',
    u'fragments of 2^14 octets',
    u'a value smaller than 64',
    u'2^9(1), 2^10(2), 2^11(3), 2^12(4)',
    u'2^9, 2^10, 2^11, and 2^12',
    u'fixed maximum plaintext fragment length of 2^14 bytes',
    u'Once a maximum fragment length other than 2^14 has been successfully',
    u'the negotiated length is 2^9=512',
    u'at most 805 bytes: 5 bytes of headers, 512 bytes of application data',
    u'larger than 805 bytes MUST discard the message',
    u'By default its value is SSL3_RT_MAX_PLAIN_LENGTH (16384)',
    u'only accept a value in the range 512 - SSL3_RT_MAX_PLAIN_LENGTH',
    u'SSL3_RT_MAX_PLAIN_LENGTH + SSL3_RT_MAX_ENCRYPTED_OVERHEAD (16704) bytes',
    u'Sets Maximum Fragment Length to 512 bytes',
    u'Sets Maximum Fragment Length to 1024.',
    u'Sets Maximum Fragment Length to 2048.',
    u'Sets Maximum Fragment Length to 4096.',
    u'must be in the range 1 - SSL_MAX_PIPELINES (32)',
    u'A TLSCiphertext record was received that had a length more than 2^14+2048 bytes',
    u'A TLSCiphertext record was received that had a length more than 2^14+256 bytes',
    u'or a record decrypted to a TLSCompressed record with more than 2^14+1024 bytes',
    u'or a record decrypted to a TLSPlaintext record with more than 2^14 bytes',
    u'MUST NOT produce an expansion greater than 255 octets',
    u'the maximum AEAD expansion of 255 octets',
    u'1 octet for ContentType',
    u'terminate the connection with a "record_overflow" alert',
    u'terminate the connection with an "illegal_parameter" alert',
    u'max_fragment_length(1)',
    u'The key words "MUST", "MUST NOT", "REQUIRED"',
    u'Padding added as part of encryption',
]
NK = [pnorm(z) for z in NEEDLES]
LIN = [[pnorm(x) for x in L[i]] for i in range(NSRC)]
F['needles4'] = []
F['needle_src'] = []
CUT_LF, CUT_POW = [], []
for k, q in enumerate(NK):
    row = []
    for i in range(NSRC):
        hs = [m.start() for m in re.finditer(re.escape(q), FOL[i])]
        sp = [h for h in hs if len(set([row_of(i, o, 1) for o in range(h, h + len(q))])) > 1]
        r0 = len(hs) - len(sp)
        r1 = len(hs)
        r2 = cnt_re(SHF[i], q)
        r3 = cnt_re(SHN[i], q)
        row.append([r0, r1, r2, r3])
    F['needles4'].append(row)
    F['needle_src'].append([LBL[i] for i in range(NSRC) if row[i][2] > 0])
    if any(row[i][0] < row[i][1] for i in range(NSRC)):
        CUT_LF.append(k)
    if any(row[i][3] > row[i][2] for i in range(NSRC)):
        CUT_POW.append(k)
F['cut_lf'] = CUT_LF
F['cut_pow'] = CUT_POW
F['needle_n'] = len(NEEDLES)
F['needle_probes'] = len(NEEDLES) * NSRC
F['needle_wrap'] = [len([1 for i in range(NSRC) if F['needles4'][k][i][0] < F['needles4'][k][i][1]])
                    for k in range(len(NEEDLES))]
F['pow_gain'] = [sum([max(0, F['needles4'][k][i][3] - F['needles4'][k][i][2]) for i in range(NSRC)])
                 for k in range(len(NEEDLES))]
F['wrap_gain'] = [sum([F['needles4'][k][i][1] - F['needles4'][k][i][0] for k in range(len(NEEDLES))])
                  for i in range(NSRC)]
F['cold_needles'] = [k for k in range(len(NEEDLES))
                     if all([F['needles4'][k][i][3] == 0 for i in range(NSRC)])]
print(u'4 判词针 %d 枚 × 五份 = %d 格; 被硬换行切开 %s; 被幂式归一救回 %s'
      % (len(NEEDLES), F['needle_probes'], CUT_LF, CUT_POW))
print(u'   逐份换行涨量:', F['wrap_gain'], u' 全冷针:', F['cold_needles'])

# ---------- 5. 单位词 ⇎ 数值×单位对(一条多选正则) ----------
RX_UNIT = re.compile(u'([0-9]+(?:\\.[0-9]+)?)(?: (octets|octet|bytes|byte|bits)|(K)(?![A-Za-z]))')
UNITW = [u'octets', u'octet', u'bytes', u'byte', u'K', u'bits']


def num_units(face, tab):
    """本遍: 整串正则一次取出(数字,单位), 再用布尔表验左邻(采集侧是两遍扫描就地读单位词)。"""
    al, dg, an = tab
    out = []
    for m in RX_UNIT.finditer(face):
        a = m.start()
        if a > 0 and an[a - 1]:
            continue
        out.append((m.group(1), m.group(2) or m.group(3) or u''))
    return out


TBX = [_tabs(fold(T[i])) for i in range(NSRC)]
NU = [num_units(fold(T[i]), TBX[i]) for i in range(NSRC)]
F['unit_word'] = [[len([z for z in NU[i] if z[1] == w]) for w in UNITW] for i in range(NSRC)]
F['unit_pair'] = [sorted(set([tuple(z) for z in NU[i] if z[1] in (u'octets', u'bytes', u'K')]))
                  for i in range(NSRC)]
F['unit_num_n'] = [len(NU[i]) for i in range(NSRC)]
F['unit_pow14'] = [[z for z in NU[i] if z[0] == u'14'] for i in range(NSRC)]
print(u'5 单位词:', F['unit_word'], u' 数值×单位对 %d 组' % sum([len(x) for x in F['unit_pair']]))
print(u'   与 14 结对的单位:', F['unit_pow14'])

# ---------- 6. 四档扩展值: 四字面档枚枚举 + 手工切片(机制⑧) ----------
TIER4 = [u'2^9(1)', u'2^10(2)', u'2^11(3)', u'2^12(4)']
POD4 = [u'512', u'1024', u'2048', u'4096']


def split_pair(t):
    """手工切片拆 (指数,码位): 不经任何正则(采集侧是 2\\^(\\d+)\\((\\d+)\\) 级联现取)。"""
    a = t.index(u'^')
    b = t.index(u'(')
    c = t.index(u')', b)
    return (int(t[a + 1:b]), int(t[b + 1:c]))


PAIR2 = [split_pair(t) for t in TIER4]
F['tier_enum'] = [[], [], [], [list(z) for z in PAIR2], []]
F['tier_n'] = [sum([cnt_cur(T[i], t) for t in TIER4]) for i in range(NSRC)]
F['tier_once'] = [[cnt_cur(T[i], t) for t in TIER4] for i in range(NSRC)]
F['tier_exp'] = [[], [], [], sorted(set([z[0] for z in PAIR2])), []]
F['tier_cp'] = [[], [], [], sorted(set([z[1] for z in PAIR2])), []]
F['tier_offset'] = [[], [], [], sorted(set([z[0] - z[1] for z in PAIR2])), []]
F['tier_dec'] = [[], [], [], [2 ** z[0] for z in PAIR2], []]
F['tier_cp_dec'] = [[], [], [], [2 ** z[1] for z in PAIR2], []]
F['tier_face_dec'] = [[], [], [], [cnt_cur(FOL[3], str(2 ** z[0])) for z in PAIR2], []]
POD_T = [x for x in re.findall(u'TLSEXT_max_fragment_length_(\\w+)', T[4])]
F['pod_tiers'] = [[], [], [], [], POD_T]
F['pod_tier_dec'] = [[], [], [], [], sorted(set([int(x) for x in POD4]))]
F['pod_tier_body'] = [[], [], [], [], sorted([z for z in POD4
                                              if cnt_cur(T[4], u'Sets Maximum Fragment Length to ' + z) > 0])]
F['pod_tier_counts'] = [sorted(set([cnt_cur(T[4], u'Sets Maximum Fragment Length to ' + z) for z in POD4]))]
F['pod_tier_unit'] = [[], [], [], [], sorted(set([z for z in [u'bytes']
                                                  if cnt_cur(T[4], u'Fragment Length to 512 ' + z) > 0]))]
F['pod_tier_nounit'] = [len([z for z in POD4 if cnt_cur(T[4], u'Sets Maximum Fragment Length to ' + z + u'.') > 0
                             and cnt_cur(T[4], u'Sets Maximum Fragment Length to ' + z + u' bytes') == 0])]
F['tier_cross'] = [1 if F['tier_dec'][3] == sorted(F['pod_tier_dec'][4]) else 0]
F['tier_pow_face'] = [cnt_cur(FOL[3], u'2^9=512'), cnt_cur(FOL[3], u'2^9')]
print(u'6 四档(枚举尺): 指数', F['tier_exp'][3], u' 码位', F['tier_cp'][3], u' 差', F['tier_offset'][3],
      u' 幂值', F['tier_dec'][3], u' pod 档名', POD_T, u' 正文档', F['pod_tier_dec'][4])
print(u'   四档逐枚印数:', F['tier_once'][3], u' 无单位档数:', F['pod_tier_nounit'])

# ---------- 7. 义务词: 布尔表尺 ⇎ 断言正则尺 ⇎ 邻居手扫 ----------
OB = [u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY']
OBL = [u'must not', u'must', u'should not', u'should', u'may']
FOLDC = [fold(T[i]) for i in range(NSRC)]
TBC = [_tabs(FOLDC[i]) for i in range(NSRC)]
TBZ = [_tabs(pnorm(T[i])) for i in range(NSRC)]
F['ob_fold'] = [[ub_tab(FOLDC[i], w, TBC[i]) for w in OB] for i in range(NSRC)]
F['ob_line'] = [[sum([ub_tab(x, w, _tabs(x)) for x in L[i]]) for w in OB] for i in range(NSRC)]
F['ob_wrap'] = [F['ob_fold'][i][k] - F['ob_line'][i][k] for i in range(NSRC) for k in range(5)]
F['ob_lower'] = [[ub_tab(FOL[i], w, TB[i]) for w in OBL] for i in range(NSRC)]
F['ob_re_rail'] = [[ub_re(FOLDC[i], w) for w in OB] for i in range(NSRC)]
F['ob_cur_rail'] = [[ub_cur(FOLDC[i], w) for w in OB] for i in range(NSRC)]
F['ob_ruler_diff'] = [sum([abs(F['ob_fold'][i][k] - F['ob_re_rail'][i][k])
                           + abs(F['ob_fold'][i][k] - F['ob_cur_rail'][i][k])
                           for k in range(5)]) for i in range(NSRC)]
F['ob_fold_tot'] = [sum(F['ob_fold'][i]) for i in range(NSRC)]
F['ob_line_tot'] = [sum(F['ob_line'][i]) for i in range(NSRC)]
F['ob_lower_tot'] = [sum(F['ob_lower'][i]) for i in range(NSRC)]
F['ob_tag_dash'] = [len(re.findall(u'\\b(?:MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHLD|ED|OPT)-\\d+\\b', T[i]))
                    for i in range(NSRC)]
F['ob_tag_paren'] = [len(re.findall(u'\\((?:MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|SHLD|ED|OPT)-\\d+\\)', T[i]))
                     for i in range(NSRC)]
print(u'7 义务词(布尔表折平):', F['ob_fold'], u' 逐行:', F['ob_line'])
print(u'   三轨分歧:', F['ob_ruler_diff'], u' 编号族(最宽档):', F['ob_tag_dash'], F['ob_tag_paren'])

# ---------- 8. 结构体名 ⇎ 告警词 ⇎ 词核频次档(机制③) ----------
STRUCT = [u'TLSPlaintext', u'TLSCompressed', u'TLSCiphertext', u'TLSInnerPlaintext',
          u'record_overflow', u'IllegalParameter', u'illegal_parameter', u'AEAD', u'uint16', u'opaque']
F['struct_fold'] = [[cnt_re(FOLDC[i], w) for w in STRUCT] for i in range(NSRC)]
F['alert_quoted'] = [cnt_re(FOLDC[i], u'"record_overflow" alert') for i in range(NSRC)]
F['alert_bare'] = [cnt_re(FOLDC[i], u'record_overflow') for i in range(NSRC)]
F['alert_illegal'] = [cnt_re(FOLDC[i], u'"illegal_parameter" alert') for i in range(NSRC)]
MOT = [u'record_overflow', u'tlsplaintext', u'tlscompressed', u'tlsciphertext', u'tlsinnerplaintext',
       u'aead', u'octets', u'bytes', u'fragment', u'fragments', u'max_fragment_length',
       u'16384', u'16385', u'16704', u'805', u'18432', u'512']
STRIP = re.compile(u'[^0-9a-z_+]+')


def toks(face):
    return [STRIP.sub(u'', w) for w in face.split(u' ') if w != u'']


CNT = [Counter(toks(FOL[i])) for i in range(NSRC)]
F['mot_mat'] = [[1 if CNT[i].get(w, 0) > 0 else 0 for w in MOT] for i in range(NSRC)]
F['mot_n'] = [sum(F['mot_mat'][i]) for i in range(NSRC)]
F['mot_cnt'] = [[CNT[i].get(w, 0) for w in MOT] for i in range(NSRC)]
F['mot_absent'] = [[w for k, w in enumerate(MOT) if F['mot_mat'][i][k] == 0] for i in range(NSRC)]
print(u'8 结构体名:', json.dumps(dict((k, F[k]) for k in ['struct_fold', 'alert_quoted', 'alert_bare',
                                                          'alert_illegal'])))
print(u'  词核频次档命中数:', F['mot_n'])

# ---------- 9. 节块: 固定行数滑窗 + 窗内按 token 形状截断(机制⑤) ----------
WIN = 260


def num_tok(w):
    """首 token 像不像节号: 逐段手工拆(不经正则), 每段都是数字才算。"""
    t = w.rstrip(u'.')
    if t == u'' or u'.' in t:
        ps = [p for p in t.split(u'.') if p == u'']
        if ps:
            return False
    return all([p.isdigit() and p != u'' for p in t.split(u'.')]) and t != u''


def lvl_of(w):
    return w.rstrip(u'.').count(u'.')


def is_toc(x):
    """目录行: 首 token 之后带点引线(连点成串, 或散点各自成 token)。"""
    t = x.strip().split()
    return len([z for z in t[1:] if (z != u'' and all([c == u'.' for c in z]))
                or u'.....' in z]) >= 1


def head_row(i, no):
    h = -1
    for k, x in enumerate(L[i]):
        t = x.strip().split()
        if not t or is_toc(x):
            continue
        if i == 4:
            if t[0] == u'=head1' and t[1:2] == [no]:
                h = k
        elif num_tok(t[0]) and t[0].rstrip(u'.') == no and len(t) > 1 and t[1][:1].isupper():
            h = k
            break
    return h


def sec_end2(i, h, no):
    for k in range(h + 1, min(len(L[i]), h + 1 + WIN)):
        t = L[i][k].strip().split()
        if not t or is_toc(L[i][k]):
            continue
        if i == 4:
            if t[0] == u'=head1':
                return k
            continue
        if num_tok(t[0]) and lvl_of(t[0]) <= lvl_of(no) and len(t) > 1 and t[1][:1].isupper():
            return k
    return min(len(L[i]), h + WIN)


SECS = [(0, u'5.1'), (0, u'5.2'), (0, u'5.4'), (1, u'6.2.1'), (1, u'6.2.2'), (1, u'6.2.3'),
        (2, u'4'), (3, u'4'), (4, u'DESCRIPTION')]
# pod 那一份没有编号标题, 采集遍把登记号换成它的首个被评函数名(同一枚块, 同一口径)
PODREG = {u'DESCRIPTION': u'SSL_CTX_set_split_send_fragment'}
SEC2 = []
for i, no in SECS:
    h = head_row(i, no)
    e = sec_end2(i, h, no)
    tx = NL.join(L[i][h:e])
    SEC2.append([LBL[i], PODREG.get(no, no), h, e, e - h, len(tx), L[i][h].strip()[:60]])
    print(u'9 %s §%s 首行 %d 末行 %d 块高 %d 行 ⇎ %d 码位 ⇎ 题面 %r'
          % (LBL[i], no, h, e - 1, e - h, len(tx), L[i][h].strip()[:56]))
F['sec_head'] = [z[2] for z in SEC2]
F['sec_end'] = [z[3] for z in SEC2]
F['sec_rows'] = [z[4] for z in SEC2]
F['sec_cp'] = [z[5] for z in SEC2]
F['sec_title'] = [[z[0], z[1], z[6]] for z in SEC2]
F['sec_win_hit'] = len([z for z in SEC2 if z[4] == WIN])
SECSHELL = []
for t, (i, no) in enumerate(SECS):
    SECSHELL.append(len([1 for x in L[i][F['sec_head'][t]:F['sec_end'][t]] if shell_shape(x)]))
F['sec_shell'] = SECSHELL
SECP = []
for t, (i, no) in enumerate(SECS):
    fc = fold(NL.join(L[i][F['sec_head'][t]:F['sec_end'][t]]))
    SECP.append([len([z for z in pow_all(fc) if z[0] == u'14']), len(pow_all(fc))])
F['sec_pow'] = SECP
F['sec_cp_tot'] = sum(F['sec_cp'])
F['sec_rows_tot'] = sum(F['sec_rows'])

# ---------- 10. 等式族(每一项都由面读数现算, 由 V()/EXPR() 注册) ----------
OFF14 = sorted(set([int(z[1]) for z in POW[0] + POW[1] + POW[2] if z[0] == u'14' and z[1]]))
F['off14_set'] = OFF14
F['eq_pow'] = [[(u'2^14' if k == 0 else u'2^14+%d' % k), 2 ** 14 + k, 16384 + k, 2 ** 14 + k - (16384 + k)]
               for k in [0] + OFF14]
F['eq_pow_ledger'] = sum([z[3] for z in F['eq_pow']])
F['eq_dec14'] = [cnt_re(FOL[2], u'16384') + cnt_re(FOL[4], u'16384'), 2 ** 14]
F['eq_256_split'] = [1, 255, 1 + 255, 256, 1 + 255 - 256]
F['read_1octet'] = cnt_re(FOL[0], u'1 octet for ContentType')
F['read_255'] = ub_tab(FOLDC[0], u'255', TBX[0], u'digit')
F['read_off256'] = len([z for z in POW[0] if z[0] == u'14' and z[1] == u'256'])
RX_805 = re.compile(u'([0-9]+) bytes of ([a-z]+)')
S805 = SHF[3][SHF[3].find(pnorm(u'at most 805 bytes')):SHF[3].find(pnorm(u'bytes: 5 bytes')) + 200]
P805 = [(int(a), b) for a, b in RX_805.findall(S805)]
F['face_805'] = 805
F['read_805'] = [sum([z[0] for z in P805 if z[1] != u'message']), len(P805), P805]
F['eq_805'] = sum([z[0] for z in P805 if z[1] != u'message'])
F['eq_805_ledger'] = F['eq_805'] - F['face_805']
F['eq_805_over'] = F['eq_805'] - 512
F['eq_805_parts'] = [len([z for z in P805 if z[1] != u'message'])]
RX_18K = re.compile(u'([0-9]+)K')
F['read_18k'] = [int(x) for x in RX_18K.findall(fold(T[2]))]
F['eq_18k'] = [F['read_18k'][0], F['read_18k'][0] * 1024, 2 ** 14 + 2048]
F['eq_18k_ledger'] = F['eq_18k'][1] - F['eq_18k'][2]
RX_16704 = re.compile(u'\\(([0-9]+)\\) bytes')
F['read_16704'] = [int(x) for x in RX_16704.findall(fold(T[4]))]
F['eq_16704'] = F['read_16704'][0] - 16384
F['face_320'] = cnt_re(FOL[4], u' 320 ')
F['read_pipe'] = [int(x) for x in re.findall(u'SSL_MAX_PIPELINES \\(([0-9]+)\\)', T[4])]
F['eq_pod_range'] = [512, 16384, 16384 - 512, 16384 // 512]
F['eq_floor'] = [512, 64, 512 - 64, 512 // 64]
F['eq_enc_gap'] = [2048, 1024, 2048 - 1024]
F['eq_overhead_cmp'] = [F['eq_16704'], F['eq_805_over'], F['eq_16704'] - F['eq_805_over']]
# 与采集遍同口径的三枚别名(本遍多算了商与档差, 采集遍只登差)
F['eq_18k_pair'] = [F['read_18k'][0], F['eq_18k'][1] // 1024]
F['eq_floor3'] = F['eq_floor'][:3]
F['eq_pod_range3'] = F['eq_pod_range'][:3]
print(u'10 等式: 2^14 加数集', OFF14, u' 幂值表', json.dumps(F['eq_pow']))
print(u'   805 复算=%d 面上=%d 项 %s' % (F['eq_805'], F['face_805'], json.dumps(F['read_805'][2])))
print(u'   18K 复算', F['eq_18k'], u' 16704−16384=%d 面上有无 320:%d pipelines=%s 区间账 %s'
      % (F['eq_16704'], F['face_320'], F['read_pipe'], F['eq_pod_range']))

# ---------- 11. 独占针 ⇎ 共现针(整串正则档) ----------
OWN = [(0, u'1 octet for ContentType'),
       (0, u'A TLSCiphertext record was received that had a length more than 2^14+256 bytes'),
       (1, u'The length MUST NOT exceed 2^14.'),
       (1, u'A TLSCiphertext record was received that had a length more than 2^14+2048 bytes'),
       (2, u'TLS 1.3 uses a limit of 2^14+1 octets'),
       (2, u'a value smaller than 64'),
       (2, u'Allocating up to 18K of memory for ciphertext'),
       (3, u'2^9(1), 2^10(2), 2^11(3), 2^12(4)'),
       (3, u'the negotiated length is 2^9=512'),
       (4, u'SSL3_RT_MAX_PLAIN_LENGTH + SSL3_RT_MAX_ENCRYPTED_OVERHEAD (16704) bytes'),
       (4, u'must be in the range 1 - SSL_MAX_PIPELINES (32)'),
       (4, u'By default its value is SSL3_RT_MAX_PLAIN_LENGTH (16384)')]
SHARED = [(u'records carrying data in chunks of 2^14 bytes or less', [0, 1]),
          (u'The key words "MUST", "MUST NOT", "REQUIRED"', [0, 1, 2, 3]),
          (u'max_fragment_length(1)', [0, 3])]
own_mat, own_r2, shared_mat = [], [], []
for i, nd in OWN:
    q = pnorm(nd)
    own_mat.append([LBL[j] for j in range(NSRC) if cnt_re(SHN[j], q) > 0])
    own_r2.append([LBL[j] for j in range(NSRC) if cnt_re(SHF[j], q) > 0])
F['own_mat'] = [[len(x) for x in h] for h in own_mat]
F['own_hits'] = own_mat
F['own_r2_lbl'] = own_r2
F['own_others'] = sum(len([x for x in h if x != LBL[OWN[k][0]]]) for k, h in enumerate(own_mat))
F['own_self'] = len([1 for k, h in enumerate(own_mat) if LBL[OWN[k][0]] in h])
F['own_n'] = len(OWN)
F['own_probes'] = len(OWN) * NSRC
F['own_powrescued'] = [k for k in range(len(OWN)) if own_mat[k] and not own_r2[k]]
for nd, exp in SHARED:
    hs = [j for j in range(NSRC) if cnt_re(SHN[j], pnorm(nd)) > 0]
    shared_mat.append([LBL[j] for j in hs])
F['shared_hits'] = shared_mat
F['shared_expect'] = [[LBL[j] for j in exp] for nd, exp in SHARED]
F['shared_n'] = len(SHARED)
F['shared_cells'] = sum([len(x) for x in shared_mat])
print(u'11 独占针落点:', own_mat, u' 他份命中', F['own_others'], u' 本份读通', F['own_self'],
      u' 靠归一救回', F['own_powrescued'])
print(u'   共现针落点:', shared_mat)

# ---------- 12. 锚定位: 累积长度表 + bisect 映回原行(机制⑥) ----------
PIN = []
for k, q in enumerate(NK):
    for i in range(NSRC):
        h = SHF[i].find(q)
        if h < 0:
            continue
        rows = sorted(set([row_of(i, o, 0) for o in range(h, h + len(q))]))
        PIN.append([LBL[i], k, rows[0] + 1, rows[-1] + 1, len(rows), h])
F['pins'] = PIN
F['pin_n'] = len(PIN)
F['pin_cross'] = len([z for z in PIN if z[4] > 1])
F['pin_max_span'] = max([z[4] for z in PIN])
F['pin_offset'] = [sum([z[5] for z in PIN])]
print(u'12 锚定位 %d 处 ⇎ 跨行 %d 处 ⇎ 最长跨 %d 行' % (F['pin_n'], F['pin_cross'], F['pin_max_span']))

#RX_SENT = re.compile(u'(?<=[.!?]) +')
RX_SENT = re.compile(u'(?<=[.!?])\\s+')


def sents2(face):
    """机制④: 一条正则切句(采集侧是逐字符扫“句末标点+空白”), 同一批面串逐句同列表才入账。"""
    return [x for x in RX_SENT.split(face) if x.strip() != u'']


F['sec_sents'] = []
for t, (i, no) in enumerate([(0, u'5.1'), (0, u'5.4'), (1, u'6.2.1'), (1, u'6.2.3'), (2, u'4'), (3, u'4')]):
    tx = NL.join(L[i][head_row(i, no):sec_end2(i, head_row(i, no), no)])
    ss = sents2(fold(tx))
    F['sec_sents'].append([LBL[i], no, len(ss), len([z for z in ss if u'2^' in z])])
    print(u'13 %s §%s 句 %d 枚, 其中含幂式 %d 枚'
          % (LBL[i], no, len(ss), len([z for z in ss if u'2^' in z])))
F['sec_list'] = [[z[0], z[1]] for z in F['sec_sents']]
F['sents_tot'] = sum([z[2] for z in F['sec_sents']])
F['sents_pow_tot'] = sum([z[3] for z in F['sec_sents']])

# ---------- 14. 五份主答句(由面导偏移现取整句) ----------
ANSK = [u'records carrying data in chunks of 2^14 bytes or less',
        u'The length MUST NOT exceed 2^14.',
        u'TLS 1.3 uses a limit of 2^14+1 octets',
        u'fixed maximum plaintext fragment length of 2^14 bytes',
        u'By default its value is SSL3_RT_MAX_PLAIN_LENGTH (16384)']
A1 = []
for i in range(NSRC):
    q = pnorm(ANSK[i])
    hs = [m.start() for m in re.finditer(re.escape(q), SHF[i])]
    assert len(hs) == 1, (LBL[i], len(hs))
    s0 = hs[0]
    face = SHF[i]
    st = face.rfind(u'. ', 0, s0) + 1
    en = face.find(u'. ', s0)
    if en < 0:
        en = len(face)
    en += 1
    sent = face[st:en]
    A1.append([s0, st, en, row_of(i, st, 0), row_of(i, en - 1, 0), sent])
F['ans_off'] = [z[0] for z in A1]
F['ans_sent'] = [z[5] for z in A1]
F['ans_chars'] = [len(z[5]) for z in A1]
F['ans_words'] = [len(z[5].split()) for z in A1]
F['ans_sent_line'] = [z[3] for z in A1]
F['ans_sent_end'] = [z[4] for z in A1]
F['ans_sent_span'] = [z[4] - z[3] + 1 for z in A1]
ANS_K = [NEEDLES.index(z) for z in ANSK]
F['ans_needle_line'] = [1 if len(set([row_of(i, o, 0) for o in
                                      range(A1[i][0], A1[i][0] + len(NK[ANS_K[i]]))])) == 1 else 0
                       for i in range(NSRC)]
F['ans_needle_k'] = ANS_K
F['ans_pow'] = [len([z for z in pow_all(F['ans_sent'][i]) if z[0] == u'14']) for i in range(NSRC)]
F['ans_dec'] = [[int(x) for x in re.findall(u'(?<![0-9])([0-9]{3,})(?![0-9])', F['ans_sent'][i])]
                for i in range(NSRC)]
F['ans_dec_tot'] = [len(x) for x in F['ans_dec']]
print(u'14 五答: 词', F['ans_words'], u' 字符', F['ans_chars'], u' 跨行', F['ans_sent_span'],
      u' 幂式', F['ans_pow'], u' 十进制', json.dumps(F['ans_dec']))

# ---------- 14b. 发射段用的扁平标量档(每一项都由上面的现量再切一刀, 逐个闭合) ----------
F['eq_pow_v'] = [z[1] for z in F['eq_pow']]
F['eq_pow_d'] = [z[2] for z in F['eq_pow']]
assert len(F['eq_pow_v']) == 1 + len(OFF14) == len(F['eq_pow'])
assert sum([abs(z[3]) for z in F['eq_pow']]) == F['eq_pow_ledger'] == 0
F['pow_spread_ledger'] = [F['pow_spread'][i] - 2 * F['pow_off_spaced'][i] for i in range(NSRC)]
assert F['pow_spread_ledger'] == [0] * NSRC
F['maxlen_kinds'] = len(set(F['maxlen']))
F['off14_n'] = len(OFF14)
assert F['off14_n'] + 1 == len(F['eq_pow'])
F['cold_n'] = len(F['cold_needles'])
assert F['cold_n'] == len(set(F['cold_needles'])) <= F['needle_n']
F['wrap_tot'] = sum(F['wrap_gain'])
assert F['wrap_tot'] == sum([row[1] - row[0] for r in F['needles4'] for row in r])
F['sec_n'] = len(F['sec_title'])
assert F['sec_n'] == len(F['sec_cp']) == len(F['sec_rows']) == len(SECS)
assert sum(F['sec_cp']) == F['sec_cp_tot'] and sum(F['sec_rows']) == F['sec_rows_tot']
F['year_list'] = [int(y) for grp in YEARS for y in grp]
F['year_src'] = [i for i in range(NSRC) for y in YEARS[i]]
assert len(F['year_list']) == len(F['year_src']) == sum([len(y) for y in YEARS])
F['year_n'] = len(set(F['year_list']))
F['year_tot'] = len(F['year_list'])
assert F['year_n'] == sum(F['hdr_year_set']) - 1
F['tier_exp_list'] = F['tier_exp'][3]
F['tier_cp_list'] = F['tier_cp'][3]
assert len(F['tier_exp_list']) == len(F['tier_cp_list']) == 4
assert len(F['tier_offset'][3]) == 1
F['tier_gap'] = F['tier_offset'][3][0]
assert F['tier_gap'] == F['tier_exp_list'][0] - F['tier_cp_list'][0]
assert len(set([e - c for e, c in zip(F['tier_exp_list'], F['tier_cp_list'])])) == 1
F['pod_tier_dec_list'] = F['pod_tier_dec'][4]
assert sorted(F['pod_tier_dec_list']) == F['tier_dec'][3] == [2 ** e for e in F['tier_exp_list']]
F['pod_tier_nounit_n'] = F['pod_tier_nounit'][0]
F['pod_tier_unit_rows'] = cnt_cur(T[4], u'Sets Maximum Fragment Length to 512 bytes')
assert F['pod_tier_unit_rows'] + F['pod_tier_nounit_n'] == len(POD4) == 4
F['pod_tier_unit_n'] = len(F['pod_tier_unit'][4])
F['eq_805_parts_n'] = F['eq_805_parts'][0]
P805D = dict([(b, a) for a, b in F['read_805'][2]])
assert len(P805D) == F['eq_805_parts_n'] == len(F['read_805'][2])
F['h805_hdr'] = P805D[u'headers']
F['h805_app'] = P805D[u'application']
F['h805_pad'] = P805D[u'padding']
F['h805_mac'] = P805D[u'mac']
assert F['h805_hdr'] + F['h805_app'] + F['h805_pad'] + F['h805_mac'] == F['eq_805']
assert F['eq_805'] == F['face_805'] == 805
F['read_16704_n'] = F['read_16704'][0]
assert len(F['read_16704']) == 1
assert F['read_16704_n'] == F['eq_pod_range'][1] + F['eq_16704']
assert F['eq_16704'] == F['eq_overhead_cmp'][0]
F['own_powrescued_n'] = len(F['own_powrescued'])
assert F['own_powrescued_n'] <= F['own_n'] == F['own_self'] + F['own_others']
assert F['own_probes'] == F['own_n'] * NSRC
print(u'14b 扁平标量: 幂值 %d 档 ⇎ 加数 %d ⇎ 冷针 %d ⇎ 节 %d ⇎ 档差 %d ⇎ 805=%d+%d+%d+%d ⇎ 16704=%d ⇎ '
      u'救回 %d' % (len(F['eq_pow_v']), F['off14_n'], F['cold_n'], F['sec_n'], F['tier_gap'],
                    F['h805_hdr'], F['h805_app'], F['h805_pad'], F['h805_mac'],
                    F['read_16704_n'], F['own_powrescued_n']))
sys.stdout.flush()
# --- SCAN END ---

# ---------- 15. 与采集遍逐键对账(同一把定义 ⇎ 另一套机制) ----------
# --- PICK BEGIN --- (corpus/_wire99.py 把这一段连同 SCAN/SCAN2 一起切进 audit.py::_b99_scan)
PK = json.load(io.open(u'corpus/_b99meas.json', encoding='utf-8'))
PK_CROP = [39]
assert NEEDLES[39] == u'terminate the connection with an "illegal_parameter" alert'
PKI = [k for k in range(len(NEEDLES)) if k not in PK_CROP]
assert len(PKI) == len(PK[u'needles4'])
PAIRS = [
    (u'bytes', u'bytes'), (u'cp', u'cp'), (u'utf8_extra', u'utf8_extra'),
    (u'n_lf', u'n_lf'), (u'n_cr', u'n_cr'), (u'splitnl', u'splitnl'),
    (u'splitlines', u'splitlines'), (u'ff', u'ff'), (u'ff_before_nl', u'ff_before_nl'),
    (u'ff_alone', u'ff_alone'), (u'trailing_nl', u'trailing_nl'), (u'blank', u'blank'),
    (u'nonblank', u'nonblank'), (u'maxlen', u'maxlen'), (u'tab', u'tab'), (u'bom', u'bom'),
    (u'rows_ledger', u'rows_ledger'), (u'rows_pred', u'rows_pred'),
    (u'nonascii', u'nonascii'),
    (u'foot_page', u'foot_page'), (u'auth_foot', u'foot_page'), (u'hdr_rfc', u'hdr_rfc'),
    (u'ietf_alone', u'ietf_alone'), (u'podmark', u'podmark'), (u'pod_head1', u'pod_head1'),
    (u'pod_item', u'pod_item'), (u'pod_block', u'pod_block'), (u'pgnum', u'pgnum'),
    (u'pgnum', u'pgnum_pick'), (u'shell_lines', u'shell_lines'), (u'body_lines', u'body_lines'),
    (u'shell_ledger', u'shell_ledger'), (u'face_years', u'face_years'),
    (u'pow14_n', u'pow14_n'), (u'pow_bare14', u'pow_bare14'),
    (u'cut_pow', u'cut_pow'),
    (u'pow_off_spaced', u'pow_off_spaced'), (u'pow_off_tight', u'pow_off_tight'),
    (u'pow_offset_vals', u'pow_offset_vals'), (u'pow_empty_marker', u'pow_empty_marker'),
    (u'pow_exp_hist', u'pow_exp_hist'), (u'pow_exp_kinds', u'pow_exp_kinds'),
    (u'pow_frac', u'pow_frac'),
    (u'dec_word', u'dec_word'), (u'dec_sub', u'dec_sub'), (u'dec_diff', u'dec_diff'),
    (u'shf_len', u'face_sh'), (u'tier_enum', u'tier_enum'), (u'tier_n', u'tier_n'),
    (u'tier_exp', u'tier_exp'), (u'tier_cp', u'tier_cp'), (u'tier_offset', u'tier_offset'),
    (u'pod_tiers', u'pod_tiers'), (u'pod_tier_dec', u'pod_tier_dec'),
    (u'pod_tier_body', u'pod_tier_body'), (u'pod_tier_unit', u'pod_tier_unit'),
    (u'ob_fold', u'ob_fold'), (u'ob_line', u'ob_line'), (u'ob_lower', u'ob_lower'),
    (u'ob_wrap', u'ob_wrap'), (u'ob_tag_dash', u'ob_tag_dash'), (u'ob_tag_paren', u'ob_tag_paren'),
    (u'alert_quoted', u'alert_quoted'), (u'alert_bare', u'alert_bare'),
    (u'mot_mat', u'mot_mat'), (u'mot_n', u'mot_n'), (u'mot_absent', u'mot_absent'),
    (u'sec_rows', u'sec_rows'), (u'sec_cp', u'sec_cp'), (u'sec_title', u'sec_title'),
    (u'sec_list', u'sec_list'), (u'sec_sents', u'sec_sents'),
    (u'eq_pow', u'eq_pow'), (u'eq_805', u'eq_805'), (u'eq_16704', u'eq_16704'),
    (u'eq_18k', u'eq_18k_pair'), (u'eq_floor', u'eq_floor3'), (u'eq_pod_range', u'eq_pod_range3'),
    (u'own_hits', u'own_hits'), (u'own_hits_rail2', u'own_r2_lbl'), (u'own_others', u'own_others'),
    (u'own_self', u'own_self'), (u'own_powrescued', u'own_powrescued'),
    (u'shared_hits', u'shared_hits'), (u'shared_expect', u'shared_expect'),
]
AGREE, DIFFK = [], []
COMP = []
for pk_k, mk_k in PAIRS:
    if mk_k not in F or pk_k not in PK:
        DIFFK.append(pk_k + u'?' + mk_k)
        continue
    (AGREE if F[mk_k] == PK[pk_k] else DIFFK).append(pk_k + u'⇎' + mk_k)
N4D = []
for kp in range(len(PK[u'needles4'])):
    kb = PKI[kp]
    for i in range(NSRC):
        for t in range(4):
            if F['needles4'][kb][i][t] != PK[u'needles4'][kp][i][t]:
                N4D.append([kp, NEEDLES[kb][:24], LBL[i], t, F['needles4'][kb][i][t],
                            PK[u'needles4'][kp][i][t]])
F['n4_diff'] = N4D
COMP.append(u'needles4')
(AGREE if not N4D else DIFFK).append(u'needles4')
for pk_k, mk_k, kk in [(u'needle_wrap', u'needle_wrap', PKI), (u'pow_gain', u'pow_gain', PKI),
                      (u'needle_src', u'needle_src', PKI)]:
    a = [F[mk_k][z] for z in kk]
    (AGREE if a == PK[pk_k] else DIFFK).append(pk_k)
    F[mk_k + u'_crop'] = a
    COMP.append(pk_k)
# cut_lf 是针下标表(不是逐针列表), 按 PKI 剔掉采集遍未登的那枚再比
a = [z for z in F['cut_lf'] if z in PKI]
F['cut_lf_crop'] = a
COMP.append(u'cut_lf(裁后)')
(AGREE if a == PK['cut_lf'] else DIFFK).append(u'cut_lf(裁后)')
PIND = []
for zp in PK[u'pins']:
    m = [z for z in F['pins'] if z[0] == zp[0] and z[2] == zp[2] and z[3] == zp[3] and z[4] == zp[4]]
    if not m:
        PIND.append(zp)
F['pin_diff'] = PIND
COMP.append(u'pins(按行号对)')
(AGREE if not PIND else DIFFK).append(u'pins(按行号对)')
EXCLUDED = [
    (u'struct_fold', u'本遍 STRUCT 多一枚 illegal_parameter, 档位不齐'),
    (u'unit_word', u'本遍要求左邻不是字母数字(整词档) ⇎ 采集遍只要数字后紧跟单位'),
    (u'eq_dec14', u'采集遍无此键(本遍新添: 面读 16384 的枚数对上 2^14)'),
    (u'ans_sent', u'采集遍未登答句尺'),
    (u'eq_pow_v⇎eq_pow_d⇎h805_*⇎tier_*_list⇎year_*⇎pod_tier_*_n', u'采集遍只登整表(STRUCT/等式表), '
     u'本遍发射段按单枚标量现插故另切扁平档, 切法本身由上面的闭合断言把关'),
]
F['pick_agree'] = len(AGREE)
F['pick_diff'] = len(DIFFK)
F['pick_diffk'] = sorted(DIFFK)
F['pick_pairs_n'] = len(PAIRS)
F['pick_comp_n'] = len(COMP)
assert F['pick_pairs_n'] + F['pick_comp_n'] == F['pick_agree'] + F['pick_diff']
assert F['pick_comp_n'] == len([z for z in COMP if z in (u'needles4', u'cut_lf(裁后)', u'pins(按行号对)')]) + 3
F['pick_excl_n'] = len(EXCLUDED)
F['pick_pairs_sum'] = F['pick_pairs_n'] + F['pick_comp_n']
assert F['pick_pairs_sum'] == F['pick_agree'] + F['pick_diff']
F['pick_excl'] = [[a, b] for a, b in EXCLUDED]
print(u'PICK 对账: %d 键符 ⇎ %d 键不符 %s' % (F['pick_agree'], F['pick_diff'], sorted(DIFFK)))
if N4D:
    print(u'   needles4 逐格不符(针, 前24字, 份, 档 0行/1折/2壳/3壳+幂, 本遍, 采集):', N4D[:8])
for zp in PIND[:6]:
    print(u'   锚行号对不上:', zp)
print(u'   口径不同而不对账的键:', json.dumps(F['pick_excl'], ensure_ascii=False))
# --- PICK END ---
sys.stdout.flush()

io.open(u'corpus/_b99flat.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True) + chr(10))
print(u'扁平键 %d 已落 corpus/_b99flat.json' % len(F))

exec(io.open(u'corpus/_mk99emit.py', encoding='utf-8').read())
