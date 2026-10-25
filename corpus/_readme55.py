# -*- coding: utf-8 -*-
"""README 记账: 54 条 → 55 条。合计取自 audit 的当下输出; 条目侧的数由本文件第五遍从两份 raw 现量,
再与建条目侧契约 corpus/_b55flat.json、门槛快照 corpus/_b55audit.json 逐键对表。
一次写成后条目又改过一轮(🧱 补“同一个值只计一枚”的口径 ⇒ 编码区 7456 → 7473, 合计随之 +17), 那笔差额在本文件跑完后按判词逐处回改,
所以 README 里“29 按不同值 ⇎ 52 按出现处”这一句是回改后的文本; 门槛侧的数仍全部现取, 不手填。
本文件不转述建条目侧的话: 两种判法(整码 ⇎ 拆片)、两种字段口径(逐行 ⇎ 折叠)、时区表自写规则的核对
都在这里各自重数一遍——因为本条的头条数(29)到底属于哪一种口径, 只有现量才看得出来。
任一标量对不上就当场停机。"""
import io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
NL = chr(10)
TAG, ENTRY = u'B55', u'corpus/babeltele/B55_subtag_registry_and_zone1970_tab.md'
PATHS = [u'corpus/raw/langsubtag.txt', u'corpus/raw/tz/zone1970.tab']
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')


def sub(old, new, s):
    assert s.count(old) == 1, (u'锚不唯一', s.count(old), old[:50])
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
assert NENT == 55, NENT
b55, b54, A = row[u'B55'], row[u'B54'], row[u'ALL']
dig_all, enc_all = int(A[0].replace(u' ', u'')), int(A[1].replace(u' ', u''))
ret_all = A[2].strip(u'*')
uniq_all = int(re.sub(u'[^0-9]', u'', A[4]))
soft_all = proofs = None
for l in OUT.split(NL):
    if l.startswith(u'提示') and u'共' in l:
        soft_all = int(l.split(u'共')[1].split(u' 个')[0])
    if l.startswith(u'已机检的推导'):
        proofs = int(l.split(u'(')[1].split(u' 条)')[0])
assert soft_all == 20 and proofs == 1144, (soft_all, proofs)
dig55, enc55, ret55, rawp55, uniq55, cwu55 = (int(b55[0]), int(b55[1]), b55[2], b55[3],
                                              int(b55[4]), b55[5])
dig54, enc54 = int(b54[0]), int(b54[1])

# ---------- 2) 条目侧第五遍: 自己从两份字节现量 ----------
RD = lambda q: io.open(q, encoding='utf-8', errors='replace').read()
TXT = [RD(q) for q in PATHS]
LS = [t.split(NL) for t in TXT]
CH = json.load(io.open(u'corpus/_b55checks.json', encoding='utf-8'))
FLAT = json.load(io.open(u'corpus/_b55flat.json', encoding='utf-8'))
SNAP = json.load(io.open(u'corpus/_b55audit.json', encoding='utf-8'))[u'B55']
SRCALL = json.load(io.open(u'corpus/_b55audit.json', encoding='utf-8'))[u'SRC']


def segs(li):
    out, cur = [], []
    for l in li:
        if l.strip() == u'%%':
            out.append(cur); cur = []
        else:
            cur.append(l)
    out.append(cur)
    return [s for s in out if any(x.strip() for x in s)]


SEGS = segs(LS[0])
SEP = sum(1 for l in LS[0] if l.strip() == u'%%')


KEYL = re.compile(u'([A-Za-z][A-Za-z-]*):[ ]?(.*)$')


def fields(seg):
    return [(m.group(1), m.group(2)) for m in (KEYL.match(l) for l in seg) if m]


FD = [dict(fields(s)) for s in SEGS]
F4 = (u'Suppress-Script', u'Macrolanguage', u'Preferred-Value', u'Prefix')
OCC = {}
for s in SEGS:
    for k, v in fields(s):
        OCC[k] = OCC.get(k, 0) + 1
FOLDN = sum(len(set(k for k, v in fields(s))) for s in SEGS)
SUBS = [d[u'Subtag'] for d in FD if u'Subtag' in d]
VW = {}
PIECE = set()
VL = []
for s in SEGS:
    for k, v in fields(s):
        if k in F4 and v.strip():
            VL.append((k, v.strip()))
POOL_SUB = set(SUBS)
POOL_SCR = set(d[u'Subtag'] for d in FD if d.get(u'Type') == u'script')
POOL_LANG = set(d[u'Subtag'] for d in FD if d.get(u'Type') == u'language')
POOL_PREF = set(v for k, v in VL if k == u'Preferred-Value')
DOM = {u'Suppress-Script': POOL_SCR, u'Macrolanguage': POOL_LANG,
       u'Preferred-Value': POOL_SUB, u'Prefix': POOL_SUB | POOL_PREF}
for k, v in VL:
    if v not in DOM[k]:
        VW.setdefault(k, set()).add(v)
        for part in v.split(u'-'):
            if part not in DOM[k]:
                PIECE.add((k, part))
VW_TOTAL = sum(len(x) for x in VW.values())
COMP = len(set((k, v) for k, v in VL if u'-' in v))
ZC = [l.split(u'\t') for l in LS[1] if l.strip() and not l.startswith(u'#')]
CC = [c for l in ZC for c in l[0].split(u',')]
REG = set(d[u'Subtag'] for d in FD if d.get(u'Type') == u'region')
ADDE = [(d[u'Added'], d.get(u'Deprecated'), d.get(u'Type'), d.get(u'Subtag') or d.get(u'Tag'))
        for d in FD if u'Added' in d]
DEPD = [x[1] for x in ADDE if x[1]]
REV = [x for x in ADDE if x[1] and x[1] < x[0]]
FD_ = [l for l in LS[0] if l.startswith(u'File-Date')]
PREFIXV = [v for k, v in VL if k == u'Prefix']
DESC_L = [v for s in SEGS for k, v in fields(s) if k == u'Description' and v.strip()]
DESC_F = [d[u'Description'] for d in FD if u'Description' in d]
AT = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', io.open(ENTRY, encoding='utf-8').read())

# ---------- 3) 三套数对表(本注 ⇎ 契约 ⇎ 门槛快照) ----------
assert SEP == FLAT[u'sep_occ'] == SNAP[u'sep_occ'] == FLAT[u'records'] - 1
assert len(SEGS) == FLAT[u'records'] == SNAP[u'records'] == 9297
assert FOLDN == FLAT[u'field_folded'] == SNAP[u'field_folded']
assert sum(OCC.values()) == FLAT[u'field_lines'] == SNAP[u'field_lines'] == FLAT[u'colon'][0]
assert FLAT[u'colon'][1] == SNAP[u'colon'][1] == 0
assert len(OCC) == FLAT[u'field_kinds'] == FLAT[u'key_kinds'] == 13
assert OCC == FLAT[u'field_line_n']
FOLDD = {}
for s in SEGS:
    for k in set(x[0] for x in fields(s)):
        FOLDD[k] = FOLDD.get(k, 0) + 1
assert FOLDD == FLAT[u'key_n']
assert len(SUBS) == FLAT[u'subrec'] == SNAP[u'subrec'] == 9203
assert len(POOL_SUB) == FLAT[u'x_dom'][2] == 8945
assert len(REG) == FLAT[u'region_n'] == SNAP[u'region_n'] == 305
assert len(POOL_SCR) == FLAT[u'x_dom'][0] == 225 and len(POOL_LANG) == FLAT[u'x_dom'][1] == 8276
assert len(VL) == FLAT[u'x_occ_total'] == SNAP[u'x_occ_total'] == 1546
assert VW_TOTAL == FLAT[u'viol_whole'] == SNAP[u'viol_whole'] == 29
assert len(PIECE) == FLAT[u'viol_piece'] == SNAP[u'viol_piece'] == 0
assert COMP == FLAT[u'compound'] == 29 and VW_TOTAL - COMP == FLAT[u'viol_minus_comp'] == 0
assert len(VW.get(u'Prefix', ())) == FLAT[u'x_vw'][3] == 26
assert len(VW.get(u'Preferred-Value', ())) == FLAT[u'x_vw'][2] == 3
assert [len(VW.get(k, ())) for k in F4] == FLAT[u'x_vw']
assert [len(set(v for k, v in VL if k == x and u'-' in v)) for x in F4] == FLAT[u'x_comp']
assert len(PREFIXV) == FLAT[u'x_occ'][3] == 444
assert len([d for d in FD if u'Prefix' in d]) == FLAT[u'x_field_n'][3] == 390
assert len(POOL_PREF - POOL_SUB) == FLAT[u'pref_out'] == SNAP[u'pref_out'] == 3
assert len(POOL_SUB | POOL_PREF) == FLAT[u'x_dom'][3] == 8948
assert len(ZC) == FLAT[u'z_rows'] == SNAP[u'z_rows'] == 312
assert len(set(CC)) == FLAT[u'z_countries'] == SNAP[u'z_countries'] == 247
assert len(set(CC) - REG) == FLAT[u'z_only'] == 0 and len(REG - set(CC)) == FLAT[u'reg_only'] == 58
GAPR = REG - set(CC)
assert len([c for c in GAPR if len(c) == 2 and c.isalpha()]) == FLAT[u'reg_alpha_only'] == 25
assert len([c for c in GAPR if c.isdigit()]) == FLAT[u'reg_digit_only'] == 31
assert len([c for c in GAPR if u'..' in c]) == FLAT[u'reg_range_only'] == 2
assert len(GAPR) == 25 + 31 + 2
assert TXT[1].count(u'\t') == FLAT[u'tabs'][1] == SNAP[u'tabs'][1] == 833
assert TXT[0].count(u'\t') == FLAT[u'tabs'][0] == 0
assert TXT[0].count(u'<') == FLAT[u'lt'][0] == 0 and TXT[1].count(u'<') == FLAT[u'lt'][1] == 3
assert len(FD_) == 1 and FD_[0] == u'File-Date: 2026-09-17' and FLAT[u'file_date'] == u'2026-09-17'
assert [len(t) for t in TXT] == FLAT[u'chars'] and [os.path.getsize(q) for q in PATHS] == FLAT[u'bytes']
assert [sum(1 for c in t if ord(c) > 127) for t in TXT] == FLAT[u'nonascii'] == SNAP[u'nonascii']
assert len([x for x in REV]) == FLAT[u'dep_before'] == SNAP[u'dep_before'] == 13
assert all(x[0] == u'2005-10-16' for x in REV)
assert len(DEPD) == FLAT[u'dep_n'] == 302 and len(set(DEPD)) == FLAT[u'dep_days'] == 45
assert len([x[0] for x in ADDE]) == FLAT[u'added_n'] == 9296 and len(set(x[0] for x in ADDE)) == FLAT[u'added_dist'] == 152
assert max(x[0] for x in ADDE) == FLAT[u'added_max'] and min(x[0] for x in ADDE) == FLAT[u'added_min']
assert len([x for x in ADDE if x[0] > FLAT[u'file_date']]) == FLAT[u'added_after'] == 0
assert len(DESC_F) == FLAT[u'desc_fold'] == 9296
assert len(DESC_L) == FLAT[u'desc_lines'] == SNAP[u'desc_lines'] == 9846
assert len(set(DESC_L)) == FLAT[u'desc_dist'] == 9413
assert len(set(DESC_F)) == FLAT[u'desc_folddist'] == 8911
CCT = [l[0].split(u',') for l in ZC]
CNT = {}
for l in CCT:
    for c in l:
        CNT[c] = CNT.get(c, 0) + 1
assert len([i for i, l in enumerate(ZC) if len(l) > 3]) == FLAT[u'z_col4'] == 201
assert len([l for l in CCT if any(CNT[c] > 1 for c in l)]) == FLAT[u'z_shared_rows'] == 201
assert len(set(x[3] for x in REV if x[2] == u'language')) == 4
assert len(set(x[3] for x in REV if x[2] == u'region')) == 9
assert len(AT) == CH[u'anchor_total'] == SNAP[u'anchor_total'] == 41
assert len(set(a[1] for a in AT)) == CH[u'anchor_distinct'] == 29
tagc = {}
for t, _ in AT:
    tagc[t] = tagc.get(t, 0) + 1
assert tagc == CH[u'tag_counts'] == {u'R': 30, u'Z': 11}
DJO = json.load(io.open(u'corpus/_deriv55.json', encoding='utf-8'))
DP = sum(v.count(u'B55V') for v in DJO.values())
assert CH[u'deriv_keys'] == len(DJO) == 101 and CH[u'deriv_points'] == 178
shared = []
for k, v in sorted(SRCALL.items()):
    if k == TAG:
        continue
    hits = [i for i, q in enumerate(v) if any(q.replace(u'\\', u'/') == p.replace(u'\\', u'/') for p in PATHS)]
    if hits:
        shared.append((k, hits[0]))
assert len(shared) == 5, shared
assert enc55 == CH[u'enc_chars'] and dig55 == 1838

# ---------- 4) 逐处替换 ----------
S = io.open(F, encoding='utf-8').read()
S = sub(u'共 **54 条**（`babeltele/B01..B54`）',
        u'共 **55 条**（`babeltele/B01..B55`）', S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（54 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（55 条）', S)
S = sub(u'当前 **54 条语料／1047 条**推导全部通过（audit 自报“已机检的推导 1047 条”）',
        u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs), S)

NEWPAR = (u'**B55 把对照轴换成一张表 ⇎ 一张借它的码当列值的表**：`raw/langsubtag.txt`（BCP 47 子标签注册表 ⟦R⟧: '
          u'%d 字节／%d 段／每段以一行两个 %% 字符分隔／`<` 0 枚／制表符 0 枚／非 ASCII %d 枚） ⇎ '
          u'`raw/tz/zone1970.tab`（把同一批 ISO 3166 两位码当国家列 ⟦Z⟧: %d 字节／%d 数据行／`<` %d 枚⇔全住注释里的 ‘<tab>’ 记法／'
          u'制表符 %d 枚／非 ASCII %d 枚）。字节比 %d 倍而“字符数=字节数”在 0 份上成立。主轴是判法: '
          u'四个交叉引用字段逐行取到 %d 个值, 整码判越界 %d 枚 ⇎ 拆片判越界 %d 枚(29 按“不同的值”计, 按出现处数是 52 处, '
          u'越界减复合值枚数差 %d)——越界的全是复合标签, 所以“这张表有没有越界值”取决于先问哪一种; 值域宽度不对称 %d ⇎ %d ⇎ %d ⇎ %d, '
          u'Prefix 那 %d 枚只作 Preferred-Value 出现、从未登记成 Subtag。跨文件那笔账带方向: region %d 枚 '
          u'⇎ 国家列去重 %d 枚, 交集 %d ⇎ 时区表有而注册表无 %d ⇎ 反向缺 %d(拆成两位码 %d ⇎ 数字码 %d ⇎ 区间 %d, '
          u'“缺 58”里只有 25 枚是真缺口); 时区表把规则写在注释里再交给数据判: 第 4 列的“当且仅当”核对 %d／%d 行'
          u'(多余 %d ⇎ 缺失 %d), 排序声明整列口径 %d 行不守 ⇎ 去掉每行首国 %d 行不守(注释只承诺后一种, 前一种读法是过度解读), '
          u'失守那行正是 %d 国共行的 ⟨America/Puerto_Rico⟩; 坐标两档 %d ⇎ %d 相加校住 %d; 制表符 %d 枚由列结构反推完全对上(差 %d)。'
          u'日期账另出 %d 条弃用日早于本段登用日(Added 全在同一天 %s, Deprecated 最早 %s) ⇎ %d 处 Preferred-Value 指向已弃码。'
          u'锚的口径也分两层: 归一键(只留字母数字并小写)判出穿两源的池内候选 %d 条, 逐字复核对 %d 条——三条假同现 '
          u'(Description: Sô ⇎ Antarctica/ ⇎ Atlantic/)全由“ô”与尾斜杠被吃掉造成, '
          u'于是池内同现 %d 条 ⇎ 逐字同现 %d 条 ⇎ 关键串两源同现 %d 枚各占一键。'
          u'共用源 5 处: zone1970.tab 已服务 B10／B45／B49／B52, langsubtag.txt 已服务 B09; 与本条锚集交叠最多的是 B49 的 2 串, '
          u'共用的是同一句原文而不是同一个论断。“RFC 5646 正文如何表述这些值域约束”“那 49 处遗留是已知还是有意”'
          u'不可由在库文件判定, 判词按第三档写、门槛不背书。\n')
ANCHOR_OLD = (u'本机两份由 pdftotext 现生两遍字节相同（这一句入门槛），抽取器版本与两份产物的 sha 只进解读注；'
              u'“哪一种序列化才算这份标准的正文”与“⊕ 在 PDF 里本来画的是什么”不可由在库文件判定，判词按第三档写、门槛不背书。\n')
S = sub(ANCHOR_OLD, ANCHOR_OLD + (NEWPAR % (
    FLAT[u'bytes'][0], FLAT[u'records'], FLAT[u'nonascii'][0],
    FLAT[u'bytes'][1], FLAT[u'z_rows'], FLAT[u'lt'][1], FLAT[u'tabs'][1], FLAT[u'nonascii'][1],
    FLAT[u'ratio'], FLAT[u'x_occ_total'], FLAT[u'viol_whole'], FLAT[u'viol_piece'], FLAT[u'viol_minus_comp'],
    FLAT[u'x_dom'][0], FLAT[u'x_dom'][1], FLAT[u'x_dom'][2], FLAT[u'x_dom'][3], FLAT[u'pref_out'],
    FLAT[u'region_n'], FLAT[u'z_countries'], FLAT[u'reg_shared'], FLAT[u'z_only'], FLAT[u'reg_only'],
    FLAT[u'reg_alpha_only'], FLAT[u'reg_digit_only'], FLAT[u'reg_range_only'],
    FLAT[u'z4_agree'], FLAT[u'z_rows'], FLAT[u'z4_pos'], FLAT[u'z4_neg'],
    FLAT[u'z_whole_un'], FLAT[u'z_tail_un'], FLAT[u'z_maxm'],
    FLAT[u'z_lat4'], FLAT[u'z_lat6'], FLAT[u'z_rows'], FLAT[u'tabs'][1], FLAT[u'z_tab_diff'],
    FLAT[u'dep_before'], u'2005-10-16', u'1989-01-01', FLAT[u'pref_dep'],
    FLAT[u'x_normonly'], FLAT[u'x_verbatim'],
    FLAT[u'x_normonly'], FLAT[u'x_verbatim'], FLAT[u'hitboth'])), S)

ROW55 = (u'| B55 | %d（新建, 一张注册表 ⇎ 一张借它的码当国家列的时区表 %d 处标注／%d 个不同串（登记 %d 条锚全命中，'
         u'每标签 R %d ⇎ Z %d）: 两色锚位 注册表 ⟦R⟧ ⇎ 时区表 ⟦Z⟧; 最强一环是判法而非数据: 四字段 %d 个值 '
         u'整码判越界 %d ⇎ 拆片判越界 %d(越界减复合值枚数差 %d——越界全是含 \'-\' 的复合标签) ⇎ 值域 %d ⇎ %d ⇎ %d ⇎ %d '
         u'(Prefix 有 %d 枚从未登记成 Subtag) ⇎ 跨文件双向差 时区表独占 %d ⇎ 注册表独占 %d(其中两位码真缺口只有 %d, 另 %d 枚是数字码与区间); '
         u'字段两口径 逐行 %d ⇎ 折叠 %d(差 %d, 不在三名之外 0 处) ⇎ 段三档闭合 9203 ⇎ 93 ⇎ 1; 长度签名 8 档闭合 %d, '
         u'私用区间 4 枚各为其类型最长; 注释自写规则交给数据判: 第 4 列充要 %d／%d(多余 %d ⇎ 缺失 %d) ⇎ 排序整列 %d ⇎ 去首国 %d '
         u'⇎ 坐标两档 %d ⇎ %d ⇎ 制表符由列结构反推差 %d; 日期 登用 %d 处／%d 日 ⇎ 弃用 %d 条／%d 日, 反向时序 %d ⇎ 指向已弃 %d; '
         u'锚 归一穿两源 %d ⇎ 逐字 %d ⇎ 关键串两源同现 %d／单源 %d／不中 %d; 同数共键复合式 %d 组、零项 %d 枚折成一条算式; '
         u'门槛侧 %d 枚推导键／%d 处 B55V 复算点，四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 %d 条锚逐字全命中） |\n')
anchor_row = (u'门槛侧 81 枚推导键／243 处 B54V 复算点，四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 26 条锚逐字全命中） |\n')
assert S.count(anchor_row) == 1
S = sub(anchor_row, anchor_row + (ROW55 % (
    enc55, CH[u'anchor_total'], CH[u'anchor_distinct'], CH[u'anchor_distinct'],
    CH[u'tag_counts'][u'R'], CH[u'tag_counts'][u'Z'],
    FLAT[u'x_occ_total'], FLAT[u'viol_whole'], FLAT[u'viol_piece'], FLAT[u'viol_minus_comp'],
    FLAT[u'x_dom'][0], FLAT[u'x_dom'][1], FLAT[u'x_dom'][2], FLAT[u'x_dom'][3], FLAT[u'pref_out'],
    FLAT[u'z_only'], FLAT[u'reg_only'], FLAT[u'reg_alpha_only'], FLAT[u'reg_digit_only'] + FLAT[u'reg_range_only'],
    FLAT[u'field_lines'], FLAT[u'field_folded'], FLAT[u'field_extra'], FLAT[u'sl_sum'],
    FLAT[u'z4_agree'], FLAT[u'z_rows'], FLAT[u'z4_pos'], FLAT[u'z4_neg'],
    FLAT[u'z_whole_un'], FLAT[u'z_tail_un'], FLAT[u'z_lat4'], FLAT[u'z_lat6'], FLAT[u'z_tab_diff'],
    FLAT[u'added_n'], FLAT[u'added_dist'], FLAT[u'dep_n'], FLAT[u'dep_days'],
    FLAT[u'dep_before'], FLAT[u'pref_dep'],
    FLAT[u'x_normonly'], FLAT[u'x_verbatim'], FLAT[u'hitboth'], FLAT[u'hitsingle'], FLAT[u'hitnone'],
    len(CH[u'collisions']), CH[u'zero_terms'],
    CH[u'deriv_keys'], DP, CH[u'anchor_distinct'])), S)

lin = (u'第二代（B11–B54）锚内字母 **116 467**、锚外 **11 009**；全库合计 **116 588／13 204**'
       u'（B54 一枚条目贡献 1 792／497, 由建条目侧现数）')
S = sub(lin, (u'第二代（B11–B55）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
              u'（B55 一枚条目贡献 %s／%d, 由建条目侧现数）'
              % (fmt(116467 + CH[u'letters_in']), fmt(11009 + CH[u'letters_out']),
                 fmt(116588 + CH[u'letters_in']), fmt(13204 + CH[u'letters_out']),
                 fmt(CH[u'letters_in']), CH[u'letters_out'])), S)

RAW55 = (u'| B55 | `raw/langsubtag.txt`（子标签注册表 ⟦R⟧: %d 字节／%d 字符／%d 段／分隔符 %d 行／`<` 0 枚／制表符 0 枚／'
         u'字段行 %d ⇎ 折叠 %d） ⇎ `raw/tz/zone1970.tab`（时区表 ⟦Z⟧: %d 字节／%d 字符／%d 数据行／制表符 %d 枚／'
         u'国家码去重 %d 枚／坐标两档 %d ⇎ %d） | 一张表 ⇎ 一张借它的码当列值的表 ⇒ 同一个问题的两种判法: '
         u'四个值域字段整码判越界 %d ⇎ 拆片判 0, 规则写在注释里而由数据判(第 4 列 %d／%d, 排序整列 %d ⇎ 去首国 %d) |\n')
anchor2 = (u'| 一份标准 ⇎ 四种序列化 ⇒ 行数、行长、分页符、行尾空格、词集包含、符号存活全部随抽取器改口，'
           u'能确定的只有可复算的那部分（骨架四级配对 ⇎ 码点存活表 ⇎ 本机产物重跑字节相同） |\n')
assert S.count(anchor2) == 1
S = sub(anchor2, anchor2 + (RAW55 % (
    FLAT[u'bytes'][0], FLAT[u'chars'][0], FLAT[u'records'], FLAT[u'sep_occ'],
    FLAT[u'field_lines'], FLAT[u'field_folded'],
    FLAT[u'bytes'][1], FLAT[u'chars'][1], FLAT[u'z_rows'], FLAT[u'tabs'][1],
    FLAT[u'z_countries'], FLAT[u'z_lat4'], FLAT[u'z_lat6'],
    FLAT[u'viol_whole'], FLAT[u'z4_agree'], FLAT[u'z_rows'],
    FLAT[u'z_whole_un'], FLAT[u'z_tail_un'])), S)

row56 = (u'| **合计（%d 条）** | **%s** | **%s**（摘要段合计 %s） | — | **%s** | — |\n'
         % (NENT, fmt(dig_all).replace(u',', u' '), ret_all, fmt(enc_all).replace(u',', u' '),
            fmt(uniq_all).replace(u',', u' ')))
old_tot = re.search(u'[|] [*]{2}合计（54 条）[*]{2}[^\n]*\n', S)
assert old_tot
S = S.replace(old_tot.group(0), row56)

CMD = (u'python -X utf8 corpus/_mkB55.py                  # 建条目: 扁平契约 %d 枚键／DERIV %d 枚算式, 占位符未替换 0 个\n'
       u'python -X utf8 corpus/_mkdigest3.py B55 <entry> R raw/langsubtag.txt 12 25 Z raw/tz/zone1970.tab 12 25   '
       u'# 两源分节摘要(%s 字符, 窗口按 12⇎25 取锚点行)\n'
       u'python -X utf8 corpus/_wire55.py                    # 把 SCAN 段机械切进 audit.py::_b55_scan 并插 DERIV[\'B55\']\n'
       u'python -X utf8 corpus/atomcheck.py B55 corpus/_atoms55.txt   # 工具侧独立逐字校验: ok=%d bad=0\n')
anchor3 = u'python -X utf8 corpus/atomcheck.py B54 corpus/_atoms54.txt   # 工具侧独立逐字校验: ok=26 bad=0' + NL
assert S.count(anchor3) == 1
S = sub(anchor3, anchor3 + (CMD % (len(FLAT), CH[u'deriv_keys'], fmt(dig55).replace(u',', u' '),
                                   CH[u'anchor_distinct'])), S)

io.open(F, 'w', encoding='utf-8', newline=NL).write(S)
print(u'README 已记账: %d 条 ｜ 摘要段 %s ⇎ 编码 %s ｜ 保留率 %s ｜ 唯一码点 %s ｜ 推导 %d 条 ｜ 提示 %d ｜ '
      u'B55 %s 字符／%d 锚(%d 串) ｜ 第五遍: 段 %d 整码越界 %d 拆片 %d 逐行字段 %d 折叠 %d Z行 %d 制表符 %d 反向时序 %d ｜ 共用源 %d 处'
      % (NENT, fmt(dig_all), fmt(enc_all), ret_all, uniq_all, proofs, soft_all,
         fmt(enc55), CH[u'anchor_total'], CH[u'anchor_distinct'],
         len(SEGS), VW_TOTAL, len(PIECE), sum(OCC.values()), FOLDN,
         len(ZC), TXT[1].count(u'\t'), len(REV), len(shared)))
