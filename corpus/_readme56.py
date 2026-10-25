# -*- coding: utf-8 -*-
"""README 记账: 55 条 → 56 条。合计、唯一码点、推导条数全部取自 audit 的当下输出, 不手填。
本文件是第五套实现: I／Z 用 csv.reader(采集侧 split 制表符、建条目侧严格正则), R 的段用 str.find 扫分隔符下标
(采集侧逐行状态机、建条目侧 re.split), 名字归一用 str.translate(建条目侧正则抹平), 路径末段用 rpartition(建条目侧 split[-1]),
注释“是否被折行”按整行是否原样出现来判(建条目侧按句串连排判), 锚的穿源档按条目正文的 ⟦⟧⟨⟩ 直读(建条目侧按池位置推)。
每个数与两份快照对表: 建条目侧扁平契约 corpus/_b56flat.json ⇎ 门槛侧 corpus/_b56audit.json。
任一标量对不上就当场停机。"""
import csv, io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
NL = chr(10)
TAG = u'B56'
ENTRY = u'corpus/babeltele/B56_three_tables_one_code_batch.md'
PATHS = [u'corpus/raw/tz/iso3166.tab', u'corpus/raw/tz/zone1970.tab', u'corpus/raw/langsubtag.txt']
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')
RD = lambda q: io.open(q, encoding='utf-8', errors='replace').read()


def sub(old, new, s):
    assert s.count(old) == 1, (u'锚不唯一', s.count(old), old[:60])
    return s.replace(old, new)


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
assert NENT == 56, NENT
b56, A = row[u'B56'], row[u'ALL']
dig_all, enc_all = int(A[0].replace(u' ', u'')), int(A[1].replace(u' ', u''))
uniq_all = int(re.sub(u'[^0-9]', u'', A[4]))
assert (sum(int(v[0]) for k, v in row.items() if k != u'ALL'),
        sum(int(v[1]) for k, v in row.items() if k != u'ALL')) == (dig_all, enc_all)
soft_all = proofs = None
for l in OUT.split(NL):
    if l.startswith(u'提示') and u'共' in l:
        soft_all = int(l.split(u'共')[1].split(u' 个')[0])
    if l.startswith(u'已机检的推导'):
        proofs = int(l.split(u'(')[1].split(u' 条)')[0])
assert soft_all == 20 and proofs == 1215, (soft_all, proofs)
dig56, enc56 = int(b56[0]), int(b56[1])
ret_tot = u'%.1f%%' % (100.0 * dig_all / enc_all)

# ---------- 2) 第五遍: 自己从三份字节现量 ----------
TXT = [RD(q) for q in PATHS]
CH = json.load(io.open(u'corpus/_b56checks.json', encoding='utf-8'))
FLAT = json.load(io.open(u'corpus/_b56flat.json', encoding='utf-8'))
SN = json.load(io.open(u'corpus/_b56audit.json', encoding='utf-8'))
SNAP, SRCALL = SN[u'B56'], SN[u'SRC']
assert enc56 == CH[u'enc_chars'] and dig56 == 1814, (enc56, CH[u'enc_chars'], dig56)


def rows_csv(i):
    with io.open(PATHS[i], encoding='utf-8', newline=NL) as fh:
        return [r for r in csv.reader(fh, delimiter=u'\t', quoting=csv.QUOTE_NONE) if r]


IALL, ZALL = rows_csv(0), rows_csv(1)
ICODE = [(r[0], r[1]) for r in IALL if r[0][:1] != u'#']
N = dict(ICODE)
CODE = [c for c, _ in ICODE]
ZD = [r for r in ZALL if r[0][:1] != u'#']
CC = [c for r in ZD for c in r[0].split(u',')]
IS, ZS = set(CODE), set(CC)

GAP = NL + u'%%' + NL
SEP = TXT[2].count(GAP)
IDX = [-1]
while True:
    j = TXT[2].find(GAP, IDX[-1] + 1)
    if j < 0:
        break
    IDX.append(j)
IDX.append(len(TXT[2]))
SEGS = [TXT[2][(0 if i == 0 else IDX[i] + len(GAP)):IDX[i + 1]] for i in range(len(IDX) - 1)]
SEGS = [s for s in SEGS if s.strip()]
assert len(SEGS) == SEP + 1 == FLAT[u'r_segs_nonempty'] == SNAP[u'r_segs_nonempty'] == 9297
assert SEP == FLAT[u'r_sep'] == SNAP[u'r_sep'] == 9296


def flds(seg):
    d = {}
    for l in seg.split(NL):
        k, sepa, v = l.partition(u': ')
        if sepa and k[:1].isalpha() and l[:1] not in u' \t':
            d[k] = v.strip()
    return d


FD = [flds(s) for s in SEGS]
REG = dict((d[u'Subtag'], d[u'Description']) for d in FD if d.get(u'Type') == u'region')
ALPHA = set(c for c in REG if c.isalpha() and len(c) == 2)
DIGIT = set(c for c in REG if c.isdigit())
RNG = set(c for c in REG if u'..' in c)
DEPS = set((d.get(u'Subtag') or d.get(u'Tag')) for d in FD
           if d.get(u'Deprecated') and d.get(u'Type') == u'region')
assert len(REG) == FLAT[u'r_region_n'] == SNAP[u'r_region_n'] == 305
assert (len(ALPHA), len(DIGIT), len(RNG)) == (FLAT[u'r_alpha'], FLAT[u'r_digit'], FLAT[u'r_range'])
assert (len(ICODE), len(ZD)) == (FLAT[u'i_rows_data'], FLAT[u'z_rows']) == (SNAP[u'i_rows_data'], SNAP[u'z_rows'])
assert len(set(CC)) == FLAT[u'z_cc_dist'] == SNAP[u'z_cc_dist'] == 247
inter3, izon, zio, rio = IS & ZS, IS - ZS, ZS - IS, set(REG) - IS
assert (len(inter3), len(izon), len(zio), len(rio)) == (FLAT[u'inter3'], FLAT[u'i_only_z'],
                                                        FLAT[u'z_only_i'], FLAT[u'r_only_i'])
assert sorted(izon) == FLAT[u'z_i_pairs'] == [u'BV', u'HM'] and len(zio) == 0
assert (len(rio & ALPHA), len(rio & DIGIT), len(rio & RNG)) == (FLAT[u'r_only_i_alpha'],
                                                                FLAT[u'r_only_i_digit'], FLAT[u'r_only_i_range'])
assert len(ALPHA - IS) == FLAT[u'r_only_i_alpha'] == 23 and len(IS - set(REG)) == FLAT[u'i_only_r'] == 0
assert len(ALPHA & IS) == FLAT[u'r_alpha_in_i'] == 249 and IS <= ALPHA
BR = ALPHA - ZS
assert len(BR) == FLAT[u'rz_alpha'] == 25 and len(BR) == len(rio & ALPHA) + len(izon)
assert len(DEPS & set(REG)) == FLAT[u'dep_total'] == 11
assert len(DEPS & rio) == FLAT[u'r_only_dep'] and len(DEPS & inter3) == FLAT[u'shared_dep'] == 0

SH = [c for c in CODE if c in REG]
EQ = [c for c in SH if N[c] == REG[c]]
DIF = [c for c in SH if N[c] != REG[c]]
TRANS = {ord(u'&'): u'and', ord(u'’'): u"'"}


def n3(s):
    return ''.join(ch for ch in n3.pre(s) if (u'a' <= ch <= u'z') or ch.isdigit())


n3.pre = lambda s: s.lower().translate(TRANS).replace(u'.', u'')
LEX = [c for c in DIF if n3(N[c]) == n3(REG[c])]
SEM = [c for c in DIF if n3(N[c]) != n3(REG[c])]
assert (len(SH), len(EQ), len(DIF), len(LEX), len(SEM)) == (FLAT[u'name_cmp'], FLAT[u'name_eq'],
                                                            FLAT[u'name_dif'], FLAT[u'name_lex'],
                                                            FLAT[u'name_sem']) == (249, 202, 47, 10, 37)
assert sum(len(REG[c]) - len(N[c]) for c in DIF) == FLAT[u'name_dif_chars'] == 355
assert (len([c for c in DIF if len(REG[c]) > len(N[c])]), len([c for c in DIF if len(N[c]) > len(REG[c])]),
        len([c for c in DIF if len(N[c]) == len(REG[c])])) == (FLAT[u'name_longer_r'], FLAT[u'name_longer_i'],
                                                               FLAT[u'name_samelen']) == (39, 5, 3)
assert (len([c for c in CODE if u'&' in N[c]]),
        len([c for c in CODE if u'&' in N[c] and u' and ' in REG.get(c, u'')]),
        len([c for c in LEX if u'&' in N[c]])) == (FLAT[u'i_amp'], FLAT[u'name_amp_both'], FLAT[u'name_lex_amp'])
VSET = set(REG.values())
assert len(set(N.values()) & VSET) == FLAT[u'name_str_pool'] == 204
XCR = [c for c in CODE if N[c] in VSET and N[c] != REG.get(c)]
assert len(XCR) == FLAT[u'name_cross'] == 2

TAIL, COMP, C4 = set(), set(), []
for r in ZD:
    if len(r) > 2:
        for x in r[2].split(u'/'):
            COMP.add(x)
        TAIL.add(r[2].rpartition(u'/')[2])
    if len(r) > 3:
        C4.extend(r[3:])
HN = sorted(set(n for n in N.values() if n in TXT[1]))
t1 = [n for n in HN if n in TAIL]
t2 = [n for n in HN if n not in TAIL and n in COMP]
t3 = [n for n in HN if n not in COMP]
assert len(HN) == FLAT[u'z_name_hits'] == SNAP[u'z_name_hits'] == 47
assert (len(t1), len(t2), len(t3)) == (FLAT[u'z_tail_comp'], FLAT[u'z_mid_comp'], FLAT[u'z_cmt_only']) == (22, 3, 22)
assert (len([r for r in ZD if len(r) == 3]), len([r for r in ZD if len(r) > 3])) == (FLAT[u'z_col3'],
                                                                                    FLAT[u'z_col4']) == (111, 201)
assert (len(CC), len(set(CC)), len([r for r in ZD if u',' in r[0]]),
        max(len(r[0].split(u',')) for r in ZD)) == (FLAT[u'z_cc_occ'], FLAT[u'z_cc_dist'],
                                                   FLAT[u'z_multi_rows'], FLAT[u'z_maxm']) == (423, 247, 34, 20)
IN4 = [n for n in t3 if any(n in x for x in C4)]
CMTL = set()
for r in ZALL:
    if r[0][:1] == u'#':
        CMTL.add(r[0])
NOT4 = [n for n in t3 if n not in IN4]
assert len(IN4) == 19 and len(NOT4) == 3
assert all([p for p in COMP if n in p and p != n] for n in NOT4)
assert not any(n in x for n in NOT4 for x in CMTL)
SP = [n for n in set(N.values()) if u' ' in n]
assert len(SP) == FLAT[u'z_space_names'] == 73
assert (len([n for n in SP if n in TXT[1]]),
        len([n for n in SP if n.replace(u' ', u'_') in TXT[1] and n not in TXT[1]])) == (FLAT[u'z_us_plain'],
                                                                                        FLAT[u'z_us_only']) == (2, 5)

IL, ZL = TXT[0].split(NL), TXT[1].split(NL)
ICL = [l for l in IL if l[:1] == u'#']
ZCL = [l for l in ZL if l[:1] == u'#']
assert (len(ICL), len(ZCL)) == (FLAT[u'i_cmt_lines'], FLAT[u'cmt_lines'][1]) == (30, 63)
share = sorted(set(l for l in ICL if l in ZCL and l.strip() != u'#'))
assert len(share) == FLAT[u'cmt_line_shared'] == 1 and share[0] == FLAT[u'cmt_line_shared_v'][0]


HEAD = set(u'ABCDEFGHIJKLMNOPQRSTUVWXYZ(#')
STOP = set(u'.:')


def sents(cl):
    b = u' '.join(u' '.join(c.lstrip(u'#').split()) for c in cl if c.strip(u'#'))
    cut = [0] + [i + 1 for i in range(1, len(b) - 1)
                 if b[i] == u' ' and b[i - 1] in STOP and b[i + 1] in HEAD] + [len(b)]
    return [u' '.join(x.split()) for x in (b[a:z].strip() for a, z in zip(cut, cut[1:]))
            if len(x) >= 8]


ISent, ZSent = sents(ICL), sents(ZCL)
if (len(ISent), len(ZSent)) != tuple(FLAT[u'cmt_sent_n']):
    print(len(ISent), len(ZSent), FLAT[u'cmt_sent_n'])
    print([s for s in ZSent if s not in ISent][:8])
assert (len(ISent), len(ZSent)) == tuple(FLAT[u'cmt_sent_n']) == (14, 25)
both = sorted(set(ISent) & set(ZSent))
assert both == sorted(FLAT[u'cmt_sent_shared_v'])
assert len(both) == FLAT[u'cmt_sent_shared'] == 4
ct = [s in TXT[0] for s in both]
cz = [s in TXT[1] for s in both]
cb = sum(1 for i in range(len(both)) if ct[i] and cz[i])
ci = sum(1 for i in range(len(both)) if ct[i] and not cz[i])
czz = sum(1 for i in range(len(both)) if cz[i] and not ct[i])
cn = sum(1 for i in range(len(both)) if not ct[i] and not cz[i])
assert (cb, ci, czz, cn) == (FLAT[u'cmt_contig_both'], FLAT[u'cmt_contig_i'], FLAT[u'cmt_contig_z'],
                             FLAT[u'cmt_contig_none']) == (1, 1, 0, 2)
CURLY = (u'‘', u'’', u'“', u'”')
assert [sum(t.count(x) for x in CURLY) for t in TXT] == FLAT[u'curly'] == SNAP[u'curly'] == [25, 18, 5]
assert [t.count(u'\t') for t in TXT] == FLAT[u'tabs'] == SNAP[u'tabs'] == [250, 833, 0]
assert [sum(1 for l in t.split(NL) if l[:1] == u'#') for t in TXT] == FLAT[u'hash'] == SNAP[u'hash'] == [30, 63, 0]
assert [len(t) for t in TXT] == FLAT[u'chars'] and [os.path.getsize(q) for q in PATHS] == FLAT[u'bytes']
assert [sum(1 for c in t if ord(c) > 127) for t in TXT] == FLAT[u'nonascii'] == SNAP[u'nonascii']
IDAT = re.findall(u'[0-9]{4}-[0-9]{2}-[0-9]{2}', NL.join(ICL))
assert len(IDAT) == 3 and sorted(IDAT) == sorted(FLAT[u'i_dates'])
assert sum(1 for i in range(len(IDAT) - 1) if IDAT[i + 1] < IDAT[i]) == FLAT[u'i_date_unsorted'] == 1
assert IDAT.count(u'2024-02-29') == FLAT[u'i_leap'] == 1
assert FLAT[u'i_claim_used'] + FLAT[u'i_claim_avoided'] == FLAT[u'i_claim_total'] == 11
assert FLAT[u'i_claim_open'] == 0 and FLAT[u'i_hdr_cc'] == 0 and FLAT[u'i_hdr_split'] == 1
assert (FLAT[u'key_3'], FLAT[u'key_2'], FLAT[u'key_1'], FLAT[u'key_0']) == (3, 15, 7, 0)
assert FLAT[u'key_IZ'] + FLAT[u'key_IR'] + FLAT[u'key_ZR'] == FLAT[u'key_2']
assert len(FLAT[u'key_3names']) == FLAT[u'key_3']

AT = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', RD(ENTRY))
assert len(AT) == CH[u'anchor_total'] == SNAP[u'anchor_total'] == 33
assert len(set(a[1] for a in AT)) == CH[u'anchor_distinct'] == 26
tc = {}
for t, _ in AT:
    tc[t] = tc.get(t, 0) + 1
assert tc == CH[u'tag_counts'] == {u'I': 18, u'Z': 6, u'R': 9}
ALNUM = frozenset(u'abcdefghijklmnopqrstuvwxyz0123456789')


def pn(s):
    return u''.join([ch for ch in s.lower() if ch in ALNUM])


FN = [pn(t) for t in TXT]
DIS = []
for a in AT:
    if a[1] not in DIS:
        DIS.append(a[1])
u1 = len([a for a in DIS if sum(1 for k in range(3) if pn(a) in FN[k]) == 1])
u2 = len([a for a in DIS if sum(1 for k in range(3) if pn(a) in FN[k]) == 2])
u3 = len([a for a in DIS if sum(1 for k in range(3) if pn(a) in FN[k]) == 3])
assert (u1, u2, u3) == (SNAP[u'anchor_single'], SNAP[u'anchor_two'], SNAP[u'anchor_three']) == (18, 7, 1)
assert u1 + u2 + u3 == len(DIS) == 26 and len(DIS) * 3 == SNAP[u'checks']
err = len([a for a in AT if pn(a[1]) not in FN[{u'I': 0, u'Z': 1, u'R': 2}[a[0]]]])
assert err == SNAP[u'anchor_err'] == 0
VER = [a for a in DIS if sum(1 for k in range(3) if pn(a) in FN[k]) == 3
       and sum(1 for k in range(3) if a in TXT[k]) < 3]
DJO = json.load(io.open(u'corpus/_deriv56.json', encoding='utf-8'))
OCC = sum(v.count(u'B56V') for v in DJO.values())
COMPOS = [v for v in DJO.values() if u'max([' in v]
assert CH[u'deriv_keys'] == len(DJO) == 72 and CH[u'zero_terms'] == 46
assert OCC == 274 and len(COMPOS) == len(CH[u'collisions']) == 23
DP = OCC
shared = []
for k, v in sorted(SRCALL.items()):
    if k == TAG:
        continue
    for i, q in enumerate(v):
        if any(q.replace(u'\\', u'/') == x.replace(u'\\', u'/') for x in PATHS):
            shared.append((k, i))
assert len(shared) == 7, shared
assert sorted(set(k for k, _ in shared)) == [u'B09', u'B10', u'B45', u'B49', u'B52', u'B55']


# ---------- 3) 逐处替换(占位符一律按名取, 不靠参数顺序) ----------
K = dict(FLAT)
K.update({u'IDAT_n': len(IDAT), u'IDAT_s': u' ⇎ '.join(sorted(IDAT)),
          u'u1': u1, u'u2': u2, u'u3': u3, u'tI': tc[u'I'], u'tZ': tc[u'Z'], u'tR': tc[u'R'],
          u'IN4': len(IN4), u'NOT4': len(NOT4), u'nshared': len(shared),
          u'anchor_total': CH[u'anchor_total'], u'anchor_distinct': CH[u'anchor_distinct'],
          u'anchor_err': err, u'deriv_keys': CH[u'deriv_keys'], u'deriv_points': DP,
          u'coll': len(CH[u'collisions']), u'zeros': CH[u'zero_terms'],
          u'enc': enc56, u'dig': dig56, u'proofs': proofs, u'nent': NENT})
for kx in (u'bytes', u'chars', u'tabs', u'hash', u'nonascii', u'curly', u'ratio', u'cmt_lines',
           u'cmt_sent_n', u'z_cols', u'lt'):
    K[kx] = list(FLAT[kx])
K[u'z_i_pairs'] = FLAT[u'z_i_pairs']
K[u'key_3names'] = FLAT[u'key_3names']

S = io.open(F, encoding='utf-8').read()
S = sub(u'共 **55 条**（`babeltele/B01..B55`）', u'共 **{nent} 条**（`babeltele/B01..B56`）'.format(**K), S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（55 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（{nent} 条）'.format(**K), S)
S = sub(u'当前 **55 条语料／1144 条**推导全部通过（audit 自报“已机检的推导 1144 条”）',
        u'当前 **{nent} 条语料／{proofs} 条**推导全部通过（audit 自报“已机检的推导 {proofs} 条”）'.format(**K), S)

NEWPAR = (
    u'**B56 把同一批两位码的“名字层”摊在三张表上各查一遍**：`raw/tz/iso3166.tab`（码表 ⟦I⟧: {bytes[0]} 字节／{i_rows_data} 行，名字写成第二列） ⇎ '
    u'`raw/tz/zone1970.tab`（时区表 ⟦Z⟧: {bytes[1]} 字节／{z_rows} 数据行，没有名字列） ⇎ `raw/langsubtag.txt`'
    u'（注册表 ⟦R⟧: {bytes[2]} 字节／region 型 {r_region_n} 枚，名字写成 Description）。字节比 {ratio[0]} ⇎ {ratio[1]} ⇎ {ratio[2]}，'
    u'制表符 {tabs[0]} ⇎ {tabs[1]} ⇎ {tabs[2]}，弯引号四类 {curly[0]} ⇎ {curly[1]} ⇎ {curly[2]}，非 ASCII {nonascii[0]} ⇎ {nonascii[1]} ⇎ {nonascii[2]}。'
    u'按码比名：可比 {name_cmp} 对里逐字相等 {name_eq} ⇎ 不等 {name_dif}；不等的那 {name_dif} 枚再分档——把 & 写成 and、把弯撇号写成直撇号这类'
    u'“只换写法”{name_lex} ⇎ 换了词的 {name_sem}（前者举 ⟨Antigua & Barbuda⟩→Antigua and Barbuda，后者举 I 的 ⟨Samoa (American)⟩⇎ R 的 ⟨American Samoa⟩）；'
    u'名长一侧 R 更长 {name_longer_r} ⇎ I 更长 {name_longer_i} ⇎ 等长 {name_samelen}（三档校住 {name_dif}，差 {name_len_close}），字符净差 +{name_dif_chars}；'
    u'码表带 & 的 {i_amp} 枚在注册表全部写作 and（{name_amp_both} 枚，差 {name_amp_close}），“只换写法”一档里带 & 的 {name_lex_amp} 枚；'
    u'{i_code_n} 个名有 {name_str_pool} 个原样出现在 Description 值集里，其中 {name_cross} 枚同名挂在别枚码上'
    u'（FM 的名分给数字区 057 ⇎ TL 的名留在已弃码 TP）——所以按名 join 比按码 join 多算 {name_cross} 条。'
    u'名字在时区表里的活法（它一个名字列都没有，列数只有 {z_cols[0]} ⇎ {z_cols[1]} 种：{z_col3} 行三列 ⇎ {z_col4} 行四列）：'
    u'码表 {i_name_dist} 个名里逐字能在时区表找到的 {z_name_hits} 个 = 等于某个标识符末段 {z_tail_comp} ⇎ 等于中间段 {z_mid_comp} ⇎ '
    u'不等于任何路径段 {z_cmt_only}（三档校住 {z_name_hits}，差 {z_tier_close}；再数一层：那 {z_cmt_only} 个里 {IN4} 个整串落在第 4 格内，'
    u'余下 {NOT4} 个（Georgia ⇎ India ⇎ Tonga）连第 4 格也不进, 只以碎片嵌在更长的标识符段里（South_Georgia ⇎ Indian ⇎ Tongatapu））；含空格的名 {z_space_names} 个只有 {z_us_plain} 个原样活着、'
    u'{z_us_only} 个要把空格写成下划线才活着；国家码本身在时区表出现 {z_cc_occ} 次于 {z_cc_dist} 枚不同码，多国行 {z_multi_rows} 行，最多一行 {z_maxm} 国。'
    u'集含三向闭合：三源共有 {inter3} ⇎ 码表有时区表无 {i_only_z}（⟨{z_i_pairs[0]}⟩ ⇎ ⟨{z_i_pairs[1]}⟩）⇎ 时区表有码表无 {z_only_i} ⇎ '
    u'注册表有码表无 {r_only_i}（两位 {r_only_i_alpha} ⇎ 三位数字 {r_only_i_digit} ⇎ 区间 {r_only_i_range}，差 {r_only_i_close}）；'
    u'注册表 {r_alpha} 枚两位字母码有 {r_alpha_in_i} 枚进了码表 ⇎ 反向缺 {i_only_r}；不在时区表国家列的 {rz_alpha} 枚 = 码表没有的 {r_only_i_alpha} '
    u'＋ 时区表没用的 {i_only_z}（桥差 {bridge}），这个 {rz_alpha} 与 B55 登记的 reg_alpha_only 同值；弃用 {dep_total} 枚全落在注册表独有侧'
    u'（{r_only_dep}）⇎ 共有侧 {shared_dep}。注释三条口径：整行逐字共用 {cmt_line_shared} 行（⟨#country-⟩，它是拆行残片） ⇎ '
    u'接行断句后共用 {cmt_sent_shared} 句（码表 {cmt_sent_n[0]} 句 ⇎ 时区表 {cmt_sent_n[1]} 句） ⇎ 这四句再按“整行是否原样出现”判：'
    u'两源都在 {cmt_contig_both} ⇎ 只在码表 {cmt_contig_i} ⇎ 只在时区表 {cmt_contig_z} ⇎ 两边都被折行 {cmt_contig_none}。'
    u'码表注释自写 {i_claim_total} 条主张交给数据判：点名该用的在场 {i_claim_used} ⇎ 该避的缺席 {i_claim_avoided} ⇎ 该避却在场 {i_claim_avoided_in}'
    u'（两账相加校住 {i_claim_total}，开口 {i_claim_open}）；自记日期 {IDAT_n} 枚（{IDAT_s}），按行序 {i_date_unsorted} 处不递增 ⇎ '
    u'被压在后面那条恰是闰日 {i_leap} 枚；它声明按码排序而码序逆 {i_sorted_desc} 处，列名说明被折成 {i_hdr_split} 处、这两行里数得出的国家码 {i_hdr_cc} 枚。'
    u'关键串矩阵：三源同现 {key_3}（{key_3names[0]} ⇎ {key_3names[1]} ⇎ {key_3names[2]}）⇎ 两源 {key_2} ⇎ 单源 {key_1} ⇎ 不中 {key_0}'
    u'（两源再分配对 I⇎Z {key_IZ} ⇎ I⇎R {key_IR} ⇎ Z⇎R {key_ZR}）；锚候选池 {pool_n} 条（I {poolI} ⇎ Z {poolZ} ⇎ R {poolR}），'
    u'穿一源 {pool_1} ⇎ 两源 {pool_2} ⇎ 三源 {pool_3}。锚 {anchor_total} 处／{anchor_distinct} 个不同串（单源 {u1} ⇎ 两源 {u2} ⇎ 三源 {u3}，'
    u'错配 {anchor_err}），每标签 I {tI} ⇎ Z {tZ} ⇎ R {tR}。共用源 {nshared} 处（同一批字节此前已服务 B09／B10／B45／B49／B52／B55，'
    u'交叠最多的是 B55 的 2 串），共用的是同一句原文而不是同一个论断，而 iso3166.tab 此前没被任何条目当过源。'
    u'“ISO 官方此刻在用哪一个名串”“注册表把 East Timor 留在已弃码 TP 而把 TL 另立的流程理由”不可由在库文件判定，判词按第三档写、门槛不背书。\n')
ANCHOR_OLD = (u'共用的是同一句原文而不是同一个论断。“RFC 5646 正文如何表述这些值域约束”“那 49 处遗留是已知还是有意”'
              u'不可由在库文件判定, 判词按第三档写、门槛不背书。\n')
S = sub(ANCHOR_OLD, ANCHOR_OLD + NEWPAR.format(**K), S)

ROW56 = (u'| B56 | {enc}（新建, 三张表管同一批两位码 {anchor_total} 处标注／{anchor_distinct} 个不同串（登记 {anchor_distinct} 条锚全命中, '
         u'每标签 I {tI} ⇎ Z {tZ} ⇎ R {tR}）: 三色锚位 码表 ⟦I⟧ ⇎ 时区表 ⟦Z⟧ ⇎ 注册表 ⟦R⟧; 头条是“名字住在哪儿”——'
         u'码表把名写成列 {i_rows_data} 行 ⇎ 时区表没有名字列（列数 {z_cols[0]} ⇎ {z_cols[1]}）却逐字装着码表来的名 {z_name_hits} 个'
         u'（末段 {z_tail_comp} ⇎ 中间段 {z_mid_comp} ⇎ 非路径段 {z_cmt_only}, 相加校住差 {z_tier_close}） ⇎ 注册表把名写成 Description {r_region_n} 枚; '
         u'按码比名 {name_cmp} 双 全等 {name_eq} ⇎ 不等 {name_dif}, 不等再拆两口径 只换写法 {name_lex} ⇎ 换了词 {name_sem}(净差 +{name_dif_chars} 字符, '
         u'R 长 {name_longer_r} ⇎ I 长 {name_longer_i} ⇎ 等长 {name_samelen}), 带 & 的 {i_amp} 枚两处对齐(差 {name_amp_close}) ⇎ 只换写法档带 & {name_lex_amp}, '
         u'同名挂别码 {name_cross} 枚(按名 join 多算这么多); 含空格名 {z_space_names} 个只 {z_us_plain} 个原样活 ⇎ {z_us_only} 个要下划线; '
         u'三向集含闭合 共有 {inter3} ⇎ I 有 Z 无 {i_only_z} ⇎ Z 有 I 无 {z_only_i} ⇎ R 有 I 无 {r_only_i}(两位 {r_only_i_alpha} ⇎ 数字 {r_only_i_digit} ⇎ 区间 {r_only_i_range}), '
         u'桥 {r_only_i_alpha}＋{i_only_z}={rz_alpha} 与 B55 的 reg_alpha_only 同数(差 {bridge}) ⇎ 弃用 {dep_total} 枚全在 R 独有侧 ⇎ 共有侧 {shared_dep}; '
         u'注释三档口径 整行逐字 {cmt_line_shared} ⇎ 接行断句 {cmt_sent_shared} ⇎ 整行原样 {cmt_contig_both}／{cmt_contig_i}／{cmt_contig_z}／{cmt_contig_none}(I {cmt_sent_n[0]} 句 ⇎ Z {cmt_sent_n[1]} 句); '
         u'码表自写主张 {i_claim_total} 条 在场 {i_claim_used} ⇎ 缺席 {i_claim_avoided} ⇎ 违背 {i_claim_avoided_in}, 日期 {IDAT_n} 枚⇎行序逆 {i_date_unsorted} ⇎ 闰日 {i_leap} ⇎ 折行列名国家码 {i_hdr_cc}; '
         u'关键串 {key_3}⇎{key_2}⇎{key_1}⇎{key_0} ⇎ 锚池 {pool_n} 条穿三源 {pool_3}; 同数共键复合式 {coll} 组、零项 {zeros} 枚折成一条算式; '
         u'门槛侧 {deriv_keys} 枚推导键／{deriv_points} 处 B56V 引用点，四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 {anchor_distinct} 条锚逐字全命中） |\n')
anchor_row = (u'门槛侧 101 枚推导键／323 处 B55V 复算点，四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 29 条锚逐字全命中） |\n')
assert S.count(anchor_row) == 1
S = sub(anchor_row, anchor_row + ROW56.format(**K), S)

lin = (u'第二代（B11–B55）锚内字母 **117 192**、锚外 **11 695**；全库合计 **117 313／13 890**'
       u'（B55 一枚条目贡献 725／686, 由建条目侧现数）')
S = sub(lin, (u'第二代（B11–B56）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
              u'（B56 一枚条目贡献 %s／%s, 由建条目侧现数）'
              % (fmt(117192 + CH[u'letters_in']), fmt(11695 + CH[u'letters_out']),
                 fmt(117313 + CH[u'letters_in']), fmt(13890 + CH[u'letters_out']),
                 fmt(CH[u'letters_in']), fmt(CH[u'letters_out']))), S)

RAW56 = (u'| B56 | `raw/tz/iso3166.tab`（码表 ⟦I⟧: {bytes[0]} 字节／{i_rows_data} 行名字成列／制表符 {tabs[0]} 枚／注释 {i_cmt_lines} 行／非 ASCII {nonascii[0]} 枚） ⇎ '
         u'`raw/tz/zone1970.tab`（时区表 ⟦Z⟧: {bytes[1]} 字节／{z_rows} 数据行／没有名字列／国家码去重 {z_cc_dist} 枚出现 {z_cc_occ} 次／#@ 注释 {z_at} 行） ⇎ '
         u'`raw/langsubtag.txt`（注册表 ⟦R⟧: {bytes[2]} 字节／region {r_region_n} 枚／其中两位字母码 {r_alpha} 枚／Description 不同值 {r_desc_dist} 个） | '
         u'三张表管同一批两位码 ⇒ 名字层各有存在形态: 写成列 {i_rows_data} ⇎ 只在标识符碎片与自由文本里活 {z_name_hits} ⇎ 写成 Description {r_region_n}, '
         u'同名对 {name_cmp} 双里逐字等 {name_eq} ⇎ 不等 {name_dif}（只换写法 {name_lex} ⇎ 换词 {name_sem}）|\n')
anchor2 = (u'四个值域字段整码判越界 29 ⇎ 拆片判 0, 规则写在注释里而由数据判(第 4 列 312／312, 排序整列 21 ⇎ 去首国 1) |\n')
assert S.count(anchor2) == 1
S = sub(anchor2, anchor2 + RAW56.format(**K), S)

row_tot = (u'| **合计（{nent} 条）** | **{enct}** | **{rett}**（摘要段合计 {digt}） | — | **{unqt}** | — |\n').format(
    nent=NENT, enct=fmt(enc_all).replace(u',', u' '), rett=ret_tot,
    digt=fmt(dig_all).replace(u',', u' '), unqt=fmt(uniq_all).replace(u',', u' '))
old_tot = re.search(u'[|] [*]{2}合计（55 条）[*]{2}[^\n]*\n', S)
assert old_tot
S = S.replace(old_tot.group(0), row_tot)

CMD = (u'python -X utf8 corpus/_mkB56.py                  # 建条目: 扁平契约 %d 枚键／DERIV %d 枚算式, 占位符未替换 0 个\n'
       u'python -X utf8 corpus/_mkdigest3.py B56 <entry> I raw/tz/iso3166.tab 12 25 Z raw/tz/zone1970.tab 15 25 '
       u'R raw/langsubtag.txt 12 25   # 三源分节摘要(%s 字符, 窗口按 12⇎25 取锚点行)\n'
       u'python -X utf8 corpus/_wire56.py                    # 把 SCAN 段机械切进 audit.py::_b56_scan 并插 DERIV[\'B56\']\n'
       u'python -X utf8 corpus/atomcheck.py B56 corpus/_atoms56.txt   # 工具侧独立逐字校验: ok=%d bad=0\n'
       % (len(FLAT), CH[u'deriv_keys'], fmt(dig56).replace(u',', u' '), CH[u'anchor_distinct']))
anchor3 = u'python -X utf8 corpus/atomcheck.py B55 corpus/_atoms55.txt   # 工具侧独立逐字校验: ok=29 bad=0' + NL
assert S.count(anchor3) == 1
S = sub(anchor3, anchor3 + CMD, S)

io.open(F, 'w', encoding='utf-8', newline=NL).write(S)
print(u'README 已记账: %d 条 ｜ 编码合计 %s ⇎ 摘要合计 %s ⇎ 合计保留率 %s ｜ 唯一码点 %d ｜ 推导 %d 条 ｜ 提示 %d ｜ '
      u'B56 %s 字符／%d 锚(%d 串, I %d⇎Z %d⇎R %d, 单源 %d⇎两源 %d⇎三源 %d) ｜ 第五遍: 名对 %d 等 %d 不等 %d(写法 %d ⇎ 词 %d, 净差 %+d) '
      u'｜ 三向 %d⇎%d⇎%d⇎%d 桥 %d ｜ 注释三档 %d⇎%d⇎%d ｜ 自由文本档整段 %d⇎只在注释 %d ｜ 主张 %d⇎%d⇎%d ｜ 共用源 %d 处'
      % (NENT, fmt(enc_all), fmt(dig_all), ret_tot, uniq_all, proofs, soft_all,
         fmt(enc56), CH[u'anchor_total'], CH[u'anchor_distinct'], tc[u'I'], tc[u'Z'], tc[u'R'], u1, u2, u3,
         len(SH), len(EQ), len(DIF), len(LEX), len(SEM), FLAT[u'name_dif_chars'],
         len(inter3), len(izon), len(zio), len(rio), len(BR),
         len(share), len(both), cb, len(IN4), len(NOT4),
         FLAT[u'i_claim_total'], FLAT[u'i_claim_used'], FLAT[u'i_claim_avoided'], len(shared)))
