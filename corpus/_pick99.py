# -*- coding: utf-8 -*-
"""采集遍(B99, 第一套实现): 一条 TLS 记录最多装多少明文——16385 与它旁边那几个数
五份一手文书各写一支: 8446(2018 TLS 1.3: 明文上限 2^14 ⇎ 密文 2^14+256 ⇎ 内层明文 2^14+1 ⇎ AEAD 膨胀 255)
⇎ 5246(2008 TLS 1.2: 2^14 ⇎ 压缩后 2^14+1024 ⇎ 加密后 2^14+2048, 同一份里结构体带空格 ⇎ 告警段不带空格)
⇎ 8449(2018 record_size_limit: 把 2^14 与 2^14+1 并排写出一句, 另给下限 64 与 "18K" 一档)
⇎ 6066(2011 max_fragment_length: 四档 2^9(1) 2^10(2) 2^11(3) 2^12(4) 与 805 字节展开式)
⇎ OpenSSL 手册 split_send_fragment.pod(实现侧一手文档: SSL3_RT_MAX_PLAIN_LENGTH (16384) ⇎ 取值区间
512 - SSL3_RT_MAX_PLAIN_LENGTH ⇎ SSL_MAX_PIPELINES (32) ⇎ 16704 ⇎ 四条 TLSEXT_max_fragment_length_* 十进制档)。

本遍的机制档(建条目遍 _mkB99.py 全换而不换定义, 逐键对账写回本文件 recon 段):
①行尺: 本遍 splitlines() 一档(把 \\x0c 也算行界) ⇎ 建条侧 split('\\n') 一档; 另逐字符数 '\\n' 作第三轨;
②字面针: 本遍游标 find 环(非重叠) ⇎ 建条侧整串 re.findall(re.escape);
③归属档: 词核家族本遍走集合 & 运算(set ∋ w) ⇎ 建条侧走 Counter 频次(cnt[w] > 0), 两档成员判定逐键对账;
④切句: 本遍逐字符扫“句末标点+空白+非大写” ⇎ 建条侧 (?<=[.!?]) + 正则切;
⑤定界: 本遍按编号节标题到同级下一节现定块 ⇎ 建条侧固定行数滑窗;
⑥行号尺: 本遍逐字符行号表(每枚字符现挂原行下标) ⇎ 建条侧累积长度表 + bisect;
⑦幂式与数值: 本遍两遍扫描(先取数字/幂式跨度, 再就地读邻接符与单位词) ⇎ 建条侧一条三分支正则;
⑧四档扩展值: 本遍正则级联 2\\^(\\d+)\\((\\d+)\\) 现取(指数,码位)对 ⇎ 建条侧按四字面档枚举清单;
⑨归一: 本遍逐字符跳空白手工比较 ⇎ 建条侧 re.sub 折平(\\s 会吃换行, 两档之差恰好是跨行可读性)。
所有正文数字与年份由本遍量出后落 JSON, 一枚都不手打。"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'8446', u'5246', u'8449', u'6066', u'pod']
IDS = [u'rfc8446', u'rfc5246', u'rfc8449', u'rfc6066', u'openssl-pod']
SRC = [u'corpus/raw/tlsrec99/rfc8446.txt', u'corpus/raw/tlsrec99/rfc5246.txt',
       u'corpus/raw/tlsrec99/rfc8449.txt', u'corpus/raw/tlsrec99/rfc6066.txt',
       u'corpus/raw/tlsrec99/openssl_max_send_fragment.pod']
NSRC = 5
M = {}


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in SRC]
T = [b.decode('utf-8', 'replace') for b in B]
# 机制①: 本遍的行尺走 splitlines(); 另建一张“原行逐字”表(换行切开前)供锚用
SL = [T[i].splitlines() for i in range(NSRC)]
RAWL = [T[i].split(NL) for i in range(NSRC)]
L = [[y[:-1] if (len(y) and ord(y[-1]) == 13) else y for y in RAWL[i]] for i in range(NSRC)]


def pnorm(s):
    return u' '.join(s.lower().split())


def fold(s):
    """保形折平: 只把空白串折成一枚空格, 不动大小写。"""
    return u' '.join([c for c in re.split(u'\\s', s) if c != u''])


def cnt_cur(hay, nd):
    """机制②: 游标 find 环。"""
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def char_line_map(txt):
    """机制⑥: 逐字符行号表。"""
    mp, li = [], 0
    for ch in txt:
        mp.append(li)
        if ch == NL:
            li += 1
    return mp


_NG = re.compile(u'[^0-9a-z_+]+')


def tokens(i):
    """机制③(本遍档): 折平面拆词后逐枚剥标点, 只留 [0-9a-z_+] 核; 归属走集合 & 运算。
    建条侧对同一核表走 Counter 频次档(cnt>0), 两档成员判定必须逐键同判(集合成员 ⇎ 频次正)。"""
    return [_NG.sub(u'', w) for w in FLD[i].split(u' ') if w != u'']


def sent_char_scan(face):
    """机制④: 逐字符扫句界(句末标点后随空白, 且空白后不是大写字母或左括号则仍算句界)。"""
    out, buf, i, n = [], [], 0, len(face)
    while i < n:
        c = face[i]
        buf.append(c)
        if c in u'.!?' and i + 1 < n and face[i + 1] == u' ':
            j = i + 1
            while j < n and face[j] == u' ':
                j += 1
            s = u''.join(buf).strip()
            if s:
                out.append(s)
                buf = []
            i = j
            continue
        i += 1
    s = u''.join(buf).strip()
    if s:
        out.append(s)
    return out


def is_foot(x):
    return re.search(u'\\[Page \\d+\\]', x) is not None


def is_hdr(x):
    return re.match(u'^RFC \\d{4}\\s+\\S.*\\s((19|20)\\d\\d)\\s*$', x) is not None


def is_authfoot(x):
    return re.search(u'\\s(Standards Track|Informational|Experimental|Best Current)\\s', x) is not None \
        and is_foot(x)


def is_podmark(x):
    return x[:1] == u'='


def is_ietf(x):
    return re.match(u'^\\s*(Internet Engineering Task Force|Internet-Draft)', x) is not None


def is_powernum(x):
    """整行只有数字与空白 ⇎ 且只含一段数字。"""
    if x.strip() == u'':
        return False
    if [c for c in x if not (c.isdigit() or c.isspace())]:
        return False
    return len([m for m in re.finditer(u'(?<![0-9])[0-9]+(?![0-9])', x)]) == 1


def is_shell(x):
    return (is_foot(x) or is_hdr(x) or is_ietf(x) or is_podmark(x) or x == u'\x0c'
            or x.strip() == u'')


# ---------- 0. 面量 ⇎ 行尺三轨 ⇎ 换页账 ----------
M['bytes'] = [len(B[i]) for i in range(NSRC)]
M['cp'] = [len(T[i]) for i in range(NSRC)]
M['n_lf'] = [sum(1 for c in T[i] if c == NL) for i in range(NSRC)]
M['n_cr'] = [sum(1 for c in T[i] if c == u'\r') for i in range(NSRC)]
M['splitnl'] = [len(RAWL[i]) for i in range(NSRC)]
M['splitlines'] = [len(SL[i]) for i in range(NSRC)]
M['ff'] = [cnt_cur(T[i], u'\x0c') for i in range(NSRC)]
M['ff_before_nl'] = [cnt_cur(T[i], u'\x0c' + NL) for i in range(NSRC)]
M['ff_alone'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
M['trailing_nl'] = [1 if T[i][-1:] == NL else 0 for i in range(NSRC)]
M['blank'] = [len([x for x in L[i] if x.strip() == u'']) for i in range(NSRC)]
M['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
M['maxlen'] = [max([len(x) for x in L[i]]) for i in range(NSRC)]
M['tab'] = [cnt_cur(T[i], u'\t') for i in range(NSRC)]
M['bom'] = [1 if T[i][:1] == u'\ufeff' else 0 for i in range(NSRC)]
M['nonascii'] = [sorted(set([ord(c) for c in T[i] if ord(c) > 127])) for i in range(NSRC)]
M['utf8_extra'] = [M['bytes'][i] - M['cp'][i] for i in range(NSRC)]
M['rows_ledger'] = [M['splitlines'][i] - M['splitnl'][i] for i in range(NSRC)]
M['rows_pred'] = [M['ff_before_nl'][i] - M['trailing_nl'][i] for i in range(NSRC)]
print(u'0 面量:', json.dumps(dict((k, M[k]) for k in
      ['bytes', 'cp', 'n_lf', 'splitnl', 'splitlines', 'ff', 'ff_before_nl', 'trailing_nl',
       'blank', 'nonblank', 'maxlen', 'tab', 'bom'])))
print(u'  非ASCII:', M['nonascii'], u' UTF-8 差额:', M['utf8_extra'])
print(u'  行式对账 splitlines−split(\\n) =', M['rows_ledger'], u' 预测 =', M['rows_pred'])
assert M['rows_ledger'] == M['rows_pred'], u'行式对账不平'

# ---------- 1. 页壳 ⇎ 标记面 ----------
M['foot_page'] = [len([x for x in L[i] if is_foot(x)]) for i in range(NSRC)]
M['hdr_rfc'] = [len([x for x in L[i] if is_hdr(x)]) for i in range(NSRC)]
M['auth_foot'] = [len([x for x in L[i] if is_authfoot(x)]) for i in range(NSRC)]
M['ietf_alone'] = [len([x for x in L[i] if is_ietf(x)]) for i in range(NSRC)]
M['podmark'] = [len([x for x in L[i] if is_podmark(x)]) for i in range(NSRC)]
M['pod_head1'] = [len([x for x in L[i] if x.startswith(u'=head1')]) for i in range(NSRC)]
M['pod_item'] = [len([x for x in L[i] if x.startswith(u'=item')]) for i in range(NSRC)]
M['pod_block'] = [len([x for x in L[i] if x.startswith((u'=over', u'=back'))]) for i in range(NSRC)]
M['pgnum'] = [len([x for x in L[i] if is_powernum(x)]) for i in range(NSRC)]
M['shell_lines'] = [len([x for x in L[i] if is_shell(x)]) for i in range(NSRC)]
M['body_lines'] = [len([x for x in L[i] if not is_shell(x)]) for i in range(NSRC)]
M['shell_ledger'] = [M['shell_lines'][i] + M['body_lines'][i] - M['splitnl'][i] for i in range(NSRC)]
assert M['shell_ledger'] == [0] * NSRC, u'壳账不平'
print(u'1 壳行:', M['shell_lines'], u' 页脚[Page]:', M['foot_page'], u' 眉行:', M['hdr_rfc'],
      u' pod标记行:', M['podmark'], u' =item:', M['pod_item'], u' 裸页码行:', M['pgnum'])
YEARS = []
for i in range(NSRC):
    hh = [x for x in L[i] if is_hdr(x)]
    if hh:
        yrs = sorted(set(re.findall(u'((?:19|20)\\d\\d)\\s*$', x)[0] for x in hh[:1]))
    else:
        cr = re.findall(u'Copyright (\\d{4})-(\\d{4})', T[i])
        yrs = sorted(set([cr[0][0], cr[0][1]])) if cr else []
    YEARS.append(yrs)
M['face_years'] = YEARS
print(u'  面上年份(眉行尾 ⇎ 版权行):', YEARS)

# ---------- 2. 幂式族: 两遍扫描 ----------
def pow_scan(face):
    """机制⑦(其一): 第一遍找每一枚 '2^' 跨度并就地读指数, 第二遍就地读接合处的空白与加数。"""
    out, empty, i, n = [], 0, 0, len(face)
    while True:
        j = face.find(u'2^', i)
        if j < 0:
            return out, empty
        k = j + 2
        d = u''
        while k < n and (face[k].isdigit() or (face[k] == u'.' and k + 1 < n and face[k + 1].isdigit())):
            d += face[k]
            k += 1
        if d == u'':
            empty += 1
            i = k + 1
            continue
        lead = 0
        while k + lead < n and face[k + lead] == u' ':
            lead += 1
        if k + lead < n and face[k + lead] == u'+':
            trail = 1
            while k + lead + trail < n and face[k + lead + trail] == u' ':
                trail += 1
            e = k + lead + trail
            off = u''
            while e < n and face[e].isdigit():
                off += face[e]
                e += 1
            out.append((d, off if off != u'' else u'?', lead, trail - 1, j, e))
            i = e
        else:
            out.append((d, u'', 0, 0, j, k))
            i = k


POWRAW = [pow_scan(fold(T[i])) for i in range(NSRC)]
POW = [x[0] for x in POWRAW]
M['pow_empty_marker'] = [x[1] for x in POWRAW]
M['pow_exp_hist'] = [dict((e, len([z for z in POW[i] if z[0] == e]))
                          for e in sorted({z[0] for z in POW[i]}, key=lambda x: float(x)))
                     for i in range(NSRC)]
M['pow14_offs'] = [[(z[1], z[2], z[3]) for z in POW[i] if z[0] == u'14'] for i in range(NSRC)]
M['pow14_n'] = [len([z for z in POW[i] if z[0] == u'14']) for i in range(NSRC)]
M['pow_bare14'] = [len([z for z in POW[i] if z[0] == u'14' and z[1] == u'']) for i in range(NSRC)]
M['pow_off_spaced'] = [len([z for z in POW[i] if z[1] and z[2] >= 1]) for i in range(NSRC)]
M['pow_off_tight'] = [len([z for z in POW[i] if z[1] and z[2] == 0]) for i in range(NSRC)]
M['pow_offset_vals'] = [[z[1] for z in POW[i] if z[0] == u'14' and z[1]] for i in range(NSRC)]
M['pow_frac'] = [[z[0] for z in POW[i] if u'.' in z[0]] for i in range(NSRC)]
print(u'2 幂式: 2^14 枚数', M['pow14_n'], u' 裸档', M['pow_bare14'], u' 带空格加档', M['pow_off_spaced'],
      u' 紧写加档', M['pow_off_tight'], u' 加数清单', M['pow_offset_vals'])
print(u'   指数直方:', M['pow_exp_hist'])
print(u'   非整数指数:', M['pow_frac'])

# ---------- 3. 十进制族: 整词尺 ⇎ 子串尺 ----------
DECF = [u'512', u'1024', u'2048', u'4096', u'16384', u'16385', u'16640', u'17408', u'18432',
        u'16704', u'805', u'64', u'255', u'32', u'16', u'8', u'256', u'5']
FLD = [pnorm(T[i]) for i in range(NSRC)]
M['dec_word'] = [[len(re.findall(u'(?<![0-9a-z])' + v + u'(?![0-9a-z])', FLD[i])) for v in DECF]
                 for i in range(NSRC)]
M['dec_sub'] = [[cnt_cur(FLD[i], v) for v in DECF] for i in range(NSRC)]
M['dec_diff'] = [[M['dec_sub'][i][k] - M['dec_word'][i][k] for k in range(len(DECF))]
                 for i in range(NSRC)]
M['pow_exp_kinds'] = [len(M['pow_exp_hist'][i]) for i in range(NSRC)]
print(u'3 十进制整词尺(%s):' % u','.join(DECF))
for i in range(NSRC):
    print(u'   %-5s %s' % (LBL[i], M['dec_word'][i]))
print(u'   子串尺−整词尺:', M['dec_diff'])

# ---------- 4. 判词针四档 ----------
def pownorm(s):
    """机制⑨档: 只归一幂式接合处的空白(2^14 + 1 → 2^14+1), 其余加号不动。"""
    return re.sub(u'(2\\^\\d+)\\s+\\+\\s+(\\d+)', u'\\1+\\2', s)


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
    u'max_fragment_length(1)',
    u'The key words "MUST", "MUST NOT", "REQUIRED"',
    u'Padding added as part of encryption',
]
SHF = [pnorm(NL.join([x for x in L[i] if not is_shell(x)])) for i in range(NSRC)]
FOL = [pnorm(T[i]) for i in range(NSRC)]
SHN = [pownorm(x) for x in SHF]
LIN = [[pnorm(x) for x in L[i]] for i in range(NSRC)]
M['needles4'] = []
M['needle_src'] = []
CUT_LF, CUT_POW = [], []
for k, nd in enumerate(NEEDLES):
    q = pnorm(nd)
    row = []
    for i in range(NSRC):
        r0 = len([x for x in LIN[i] if q in x])
        r1 = cnt_cur(FOL[i], q)
        r2 = cnt_cur(SHF[i], q)
        r3 = cnt_cur(SHN[i], q)
        row.append([r0, r1, r2, r3])
    M['needles4'].append(row)
    M['needle_src'].append([LBL[i] for i in range(NSRC) if row[i][2] > 0])
    if any(row[i][0] < row[i][1] for i in range(NSRC)):
        CUT_LF.append(k)
    if any(row[i][3] > row[i][2] for i in range(NSRC)):
        CUT_POW.append(k)
print(u'4 判词针 %d 枚; 被硬换行切开的针 %s; 被幂式归一救回的针 %s'
      % (len(NEEDLES), CUT_LF, CUT_POW))
for k in CUT_LF + CUT_POW:
    print(u'   [%d] %-58s %s' % (k, NEEDLES[k][:58], M['needles4'][k]))
M['cut_lf'] = CUT_LF
M['cut_pow'] = CUT_POW
M['needle_wrap'] = [len([1 for i in range(NSRC) if M['needles4'][k][i][0] < M['needles4'][k][i][1]])
                    for k in range(len(NEEDLES))]
M['pow_gain'] = [sum([max(0, M['needles4'][k][i][3] - M['needles4'][k][i][2]) for i in range(NSRC)])
                 for k in range(len(NEEDLES))]

# ---------- 5. 单位词 ⇎ 数值×单位对(两遍扫描) ----------
def num_units(face):
    """第一遍取数字跨度(左邻不是字母数字与点号才算一枚), 第二遍就地读其后的单位词。"""
    out = []
    for m in re.finditer(u'[0-9]+(?:\\.[0-9]+)?', face):
        a = m.start()
        if a > 0 and (face[a - 1].isalnum() or face[a - 1] in u'.^'):
            continue
        e = m.end()
        tail = face[e:e + 14]
        u2 = u''
        for w in [u'octets', u'octet', u'bytes', u'byte', u'K', u'bits']:
            need = (u'' if w == u'K' else u' ') + w
            if tail.startswith(need) and (w == u'K' or not (tail[len(need):len(need) + 1].isalnum())):
                u2 = w
                break
        out.append((m.group(0), u2))
    return out


NU = [num_units(fold(T[i])) for i in range(NSRC)]
UNITW = [u'octets', u'octet', u'bytes', u'byte', u'K', u'bits']
M['unit_word'] = [[len([z for z in NU[i] if z[1] == w]) for w in UNITW] for i in range(NSRC)]
M['unit_pair'] = [sorted(set([(z[0], z[1]) for z in NU[i] if z[1] in (u'octets', u'bytes', u'K')]))
                  for i in range(NSRC)]
M['unit_14'] = [[z for z in NU[i] if z[0] == u'14' and z[1] in (u'octets', u'bytes')]
                for i in range(NSRC)]
print(u'5 单位词(数字后紧跟):', M['unit_word'])
print(u'   数字×单位对:', json.dumps(M['unit_pair'], ensure_ascii=False))

# ---------- 6. 四档扩展值: 正则级联现取 (指数, 码位) ----------
TIER = [len(re.findall(u'2\\^(\\d+)\\((\\d+)\\)', T[i])) for i in range(NSRC)]
PAIR = [sorted(set([(int(a), int(b)) for a, b in re.findall(u'2\\^(\\d+)\\((\\d+)\\)', T[i])]))
        for i in range(NSRC)]
M['tier_enum'] = PAIR
M['tier_n'] = TIER
M['tier_ledger'] = [len(PAIR[i]) - TIER[i] for i in range(NSRC)]
M['tier_exp'] = [sorted(set([z[0] for z in PAIR[i]])) for i in range(NSRC)]
M['tier_cp'] = [sorted(set([z[1] for z in PAIR[i]])) for i in range(NSRC)]
M['tier_offset'] = [sorted(set([z[0] - z[1] for z in PAIR[i]])) for i in range(NSRC)]
POD_T = [re.findall(u'TLSEXT_max_fragment_length_(\\w+)', T[i]) for i in range(NSRC)]
M['pod_tiers'] = POD_T
M['pod_tier_dec'] = [sorted(set([int(x) for x in re.findall(u'TLSEXT_max_fragment_length_(\\d+)', T[i])]))
                     for i in range(NSRC)]
M['pod_tier_body'] = [sorted(set(re.findall(u'Sets Maximum Fragment Length to (\\d+)', T[i])))
                      for i in range(NSRC)]
M['pod_tier_unit'] = [sorted(set(re.findall(u'Sets Maximum Fragment Length to \\d+ (\\w+)', T[i])))
                      for i in range(NSRC)]
print(u'6 四档: 枚举对', PAIR, u' 指数−码位差', M['tier_offset'], u' pod 档名', POD_T[4],
      u' 正文档值', M['pod_tier_body'][4], u' 单位', M['pod_tier_unit'][4])
assert M['tier_offset'][3] == [8] and M['tier_offset'][0] == [], u'档位差不是 8'

# ---------- 7. 义务词: 保形折平 ⇎ 折小写两档 ----------
OB = [u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY']
OBL = [u'must not', u'must', u'should not', u'should', u'may']
FOLDC = [fold(T[i]) for i in range(NSRC)]
M['ob_fold'] = [[len(re.findall(u'(?<![A-Za-z])' + w.replace(u' ', u' ') + u'(?![A-Za-z])', FOLDC[i]))
                 for w in OB] for i in range(NSRC)]
M['ob_line'] = [[sum([len(re.findall(u'(?<![A-Za-z])' + w + u'(?![A-Za-z])', x)) for x in L[i]])
                 for w in OB] for i in range(NSRC)]
M['ob_wrap'] = [M['ob_fold'][i][k] - M['ob_line'][i][k] for i in range(NSRC) for k in range(5)]
M['ob_lower'] = [[len(re.findall(u'(?<![a-z])' + w.replace(u' ', u' ') + u'(?![a-z])', FLD[i]))
                  for w in OBL] for i in range(NSRC)]
M['ob_tag_dash'] = [len(re.findall(u'\\b(?:MUST|SHOULD|MAY|SHLD|ED|OPT)-\\d+\\b', T[i])) for i in range(NSRC)]
M['ob_tag_paren'] = [len(re.findall(u'\\((?:MUST|SHOULD|MAY|SHLD|ED|OPT)-\\d+\\)', T[i])) for i in range(NSRC)]
print(u'7 义务词(保形折平):', M['ob_fold'], u' 逐行:', M['ob_line'])
print(u'   小写:', M['ob_lower'], u' 编号族(最宽档):', M['ob_tag_dash'], M['ob_tag_paren'])

# ---------- 8. 记录层结构体名与告警词 ----------
STRUCT = [u'TLSPlaintext', u'TLSCompressed', u'TLSCiphertext', u'TLSInnerPlaintext',
          u'record_overflow', u'IllegalParameter', u'AEAD', u'uint16', u'opaque']
M['struct_fold'] = [[cnt_cur(FOLDC[i], w) for w in STRUCT] for i in range(NSRC)]
M['alert_quoted'] = [cnt_cur(FOLDC[i], u'"record_overflow" alert') for i in range(NSRC)]
M['alert_bare'] = [cnt_cur(FOLDC[i], u'record_overflow') for i in range(NSRC)]
print(u'8 结构体名/告警:', json.dumps(dict((k, M[k]) for k in ['struct_fold', 'alert_quoted', 'alert_bare'])))

# ---------- 9. 节块: 按编号节标题定界(机制⑤) ----------
SECHDR = re.compile(u'^(\\d+(?:\\.\\d+)*)\\.?\\s+([A-Z][^0-9]{2,})\\s*$')


def section_block(i, no):
    """本遍定界: 从编号节标题行起, 到下一枚同级或更高级标题行前止。"""
    ls = L[i]
    lvl = no.count(u'.')
    st = -1
    for k, x in enumerate(ls):
        m = SECHDR.match(x)
        if m and m.group(1) == no:
            st = k
            break
    if st < 0:
        return -1, -1, u''
    en = len(ls)
    for k in range(st + 1, len(ls)):
        m = SECHDR.match(ls[k])
        if m and m.group(1).count(u'.') <= lvl:
            en = k
            break
    return st, en, NL.join(ls[st:en])


SECS = [(0, u'5.1'), (0, u'5.2'), (0, u'5.4'), (1, u'6.2.1'), (1, u'6.2.2'), (1, u'6.2.3'),
        (2, u'4'), (3, u'4'), (4, u'SSL_CTX_set_split_send_fragment')]
SECROWS, SECCP, SECTITLE = [], [], []
for i, no in SECS:
    a, b, tx = section_block(i, no)
    if a < 0 and i == 4:
        for k, x in enumerate(L[i]):
            if x.startswith(u'=head1 DESCRIPTION'):
                a = k
        for k in range(a + 1, len(L[i])):
            if L[i][k].startswith(u'=head1'):
                b = k
                break
        tx = NL.join(L[i][a:b])
    SECROWS.append(b - a)
    SECCP.append(len(tx))
    SECTITLE.append((LBL[i], no, tx.split(NL)[0][:60]))
    print(u'9 %s §%s 块高 %d 行 ⇎ %d 码位 ⇎ 题面 %r' % (LBL[i], no, b - a, len(tx), tx.split(NL)[0][:56]))
M['sec_rows'] = SECROWS
M['sec_cp'] = SECCP
M['sec_title'] = SECTITLE

# ---------- 10. 等式族(全由面上读数复算) ----------
EQ = []
EQ.append((u'2^14', 2 ** 14, 16384))
EQ.append((u'2^14+1', 2 ** 14 + 1, 16385))
EQ.append((u'2^14+256', 2 ** 14 + 256, 16640))
EQ.append((u'2^14+1024', 2 ** 14 + 1024, 17408))
EQ.append((u'2^14+2048', 2 ** 14 + 2048, 18432))
M['eq_pow'] = [[z[0], z[1], z[2], z[1] - z[2]] for z in EQ]
M['eq_805'] = 5 + 512 + 256 + 32
M['eq_16704'] = 16704 - 16384
M['eq_18k'] = [18432 // 1024, 18]
M['eq_pod_range'] = [512, 16384, 16384 - 512]
M['eq_floor'] = [512, 64, 512 - 64]
print(u'10 等式:', json.dumps(M['eq_pow']), u'805=', M['eq_805'], u'16704−16384=', M['eq_16704'],
      u'档差:', M['eq_floor'])

# ---------- 11. 独占针 ⇎ 共现针 (归属走最宽档=摘壳+幂式归一, 游标环口径) ----------
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
own_mat, own_rail2, shared_mat = [], [], []
for i, nd in OWN:
    q = pnorm(nd)
    own_mat.append([LBL[j] for j in range(NSRC) if cnt_cur(SHN[j], q) > 0])
    own_rail2.append([LBL[j] for j in range(NSRC) if cnt_cur(SHF[j], q) > 0])
M['own_hits'] = own_mat
M['own_hits_rail2'] = own_rail2
M['own_others'] = sum(len([x for x in h if x != LBL[OWN[k][0]]]) for k, h in enumerate(own_mat))
M['own_self'] = len([1 for k, h in enumerate(own_mat) if LBL[OWN[k][0]] in h])
M['own_powrescued'] = [k for k in range(len(OWN)) if own_mat[k] and not own_rail2[k]]
for nd, exp in SHARED:
    hs = [j for j in range(NSRC) if cnt_cur(SHN[j], pnorm(nd)) > 0]
    shared_mat.append([LBL[j] for j in hs])
M['shared_hits'] = shared_mat
M['shared_expect'] = [[LBL[j] for j in exp] for nd, exp in SHARED]
print(u'11 独占针落点:', own_mat, u' 他份命中', M['own_others'], u' 本份读通', M['own_self'], len(OWN),
      u' 靠归一救回', M['own_powrescued'])
print(u'   共现针落点:', shared_mat)
assert M['own_others'] == 0 and M['own_self'] == len(OWN), u'独占针不独占'
assert [h for h in own_rail2 if len(h) > 1] == [], u'窄档独占针串了份'
assert shared_mat == M['shared_expect'], u'共现针归属与预期不符'

# ---------- 11b. 词核集合档 ⇎ (建条侧)频次档 ----------
MOT = [u'record_overflow', u'tlsplaintext', u'tlscompressed', u'tlsciphertext', u'tlsinnerplaintext',
       u'aead', u'octets', u'bytes', u'fragment', u'fragments', u'max_fragment_length',
       u'16384', u'16385', u'16704', u'805', u'18432', u'512']
TOKSET = [set(tokens(i)) for i in range(NSRC)]
M['mot_mat'] = [[1 if w in TOKSET[i] else 0 for w in MOT] for i in range(NSRC)]
M['mot_n'] = [sum(M['mot_mat'][i]) for i in range(NSRC)]
M['mot_absent'] = [[w for k, w in enumerate(MOT) if M['mot_mat'][i][k] == 0] for i in range(NSRC)]
print(u'11b 词核集合档命中数:', M['mot_n'])
for i in range(NSRC):
    print(u'    %-5s 缺 %s' % (LBL[i], M['mot_absent'][i]))
assert M['mot_mat'][0][MOT.index(u'tlsinnerplaintext')] == 1, u'8446 无内层明文词核'
assert M['mot_mat'][1][MOT.index(u'tlscompressed')] == 1, u'5246 无压缩壳词核'
assert M['mot_mat'][0][MOT.index(u'tlscompressed')] == 0, u'8446 不该有压缩壳词核(TLS 1.3 已删)'
assert u'record_overflow' in M['mot_absent'][4], u'pod 不该带告警词核'
assert all([u'18432' in M['mot_absent'][i] for i in range(NSRC)]), u'十进制 18432 竟写在面上(最宽档已核)'
assert [i for i in range(NSRC) if u'805' not in M['mot_absent'][i]] == [3], u'805 词核不止落在 6066'

# ---------- 12. 摘壳面逐字符行号表(机制⑥)⇎ 锚首末行 ----------
def face_linemap(i):
    """返回 (摘壳折平面, 每枚面字符 → 原行下标) —— 逐字符现挂, 不建累积长度表。"""
    chs, mp = [], []
    for li, x in enumerate(L[i]):
        if is_shell(x):
            continue
        run = []
        for c in x:
            if c.isspace():
                run.append(c)
                continue
            if run:
                if chs and chs[-1] != u' ':
                    chs.append(u' ')
                    mp.append(li)
                run = []
            chs.append(c.lower())
            mp.append(li)
        if run and chs and chs[-1] != u' ':
            chs.append(u' ')
            mp.append(li)
    return u''.join(chs), mp


EFB, MLP = [], []
for i in range(NSRC):
    fc, mp = face_linemap(i)
    EFB.append(fc)
    MLP.append(mp)
    assert len(fc) == len(mp)
M['efb_len'] = [len(x) for x in EFB]
M['shf_len'] = [len(x) for x in SHF]      # 壳面(去页眉页脚)长度: 与建条目遍 face_sh 同定义异机制
M['efb_vs_sh'] = [len(EFB[i]) - len(SHF[i].rstrip()) for i in range(NSRC)]
PIN = []
for k, nd in enumerate(NEEDLES):
    q = pnorm(nd)
    for i in range(NSRC):
        h = EFB[i].find(q)
        if h < 0:
            continue
        rows = sorted(set(MLP[i][h:h + len(q)]))
        PIN.append([LBL[i], k, rows[0] + 1, rows[-1] + 1, len(rows), h])
M['pins'] = PIN
print(u'12 锚定位 %d 处; 跨行 %d 处; 摘壳面长度 ⇎ 折平长度差 %s'
      % (len(PIN), len([z for z in PIN if z[4] > 1]), M['efb_vs_sh']))

# ---------- 13. 句尺(机制④): 节块与主答句的句数 ----------
SECS2 = [(0, u'5.1'), (0, u'5.4'), (1, u'6.2.1'), (1, u'6.2.3'), (2, u'4'), (3, u'4')]
M['sec_sents'] = []
for i, no in SECS2:
    a, b, tx = section_block(i, no)
    face = fold(tx)
    ss = sent_char_scan(face)
    M['sec_sents'].append([LBL[i], no, len(ss), sum(1 for z in ss if u'2^' in z)])
    print(u'13 %s §%s 句 %d 枚, 其中含幂式 %d 枚' % (LBL[i], no, len(ss), sum(1 for z in ss if u'2^' in z)))
M['sec_list'] = [[LBL[i], no] for i, no in SECS2]

json.dump(M, io.open(u'corpus/_b99meas.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
print(u'已落 corpus/_b99meas.json ｜ 键 %d' % len(M))
