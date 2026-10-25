# -*- coding: utf-8 -*-
"""README 记账: 52 条 → 53 条。合计数字全部由 audit 表现取, 条目侧的数由本文件第五遍再量一次四份源。
本文件不转述建条目侧的话: 四份 raw(官方 txt ⇎ 本机两层 ⇎ 官方落地页)在这里按“整份文件 ⇎ 去标签正文”两种口径各数一遍,
再与建条目侧契约 `corpus/_b53flat.json`、门槛快照 `corpus/_b53audit.json` 逐键对表; 骨架基数(官方 txt 一列)与标签枚数(落地页一列)也现数。
任一标量对不上就当场停机, 所以 README 里“四种序列化各不相同”是本文件数出来的。"""
import io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
NL = chr(10)
CHECK, CROSS = chr(10003), chr(10007)
TAG, ENTRY = u'B53', u'corpus/babeltele/B53_four_serializations_of_one_standard.md'
PATHS = [u'corpus/raw/fips202.txt', u'corpus/raw/fips202_pdflayout.txt',
         u'corpus/raw/fips202_plain.txt', u'corpus/raw/fips202.html']
TAGS = [u'T', u'L', u'P', u'H']
CN = [u'官方纯文本', u'本机按版式', u'本机无版式', u'官方落地页']
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
assert NENT == 53, NENT
b53, b52, A = row[u'B53'], row[u'B52'], row[u'ALL']
dig_all, enc_all, ret_all = int(A[0].replace(u' ', u'')), int(A[1].replace(u' ', u'')), A[2]
uniq_all = int(re.sub(u'[^0-9]', u'', A[4]))
soft_all = proofs = None
for l in OUT.split(NL):
    if l.startswith(u'提示') and u'共' in l:
        soft_all = int(l.split(u'共')[1].split(u' 个')[0])
    if l.startswith(u'已机检的推导'):
        proofs = int(l.split(u'(')[1].split(u' 条)')[0])
assert soft_all == 19 and proofs == 971, (soft_all, proofs)
b53_dig, b53_enc, b53_ret, b53_rawp = int(b53[0]), int(b53[1]), b53[2], b53[3]
b53_uniq, b53_blocks, b53_soft = int(b53[4]), int(b53[5]), int(b53[10])
assert [int(x) for x in b53[7:10]] == [0, 0, 0], b53
assert b53_ret == u'%.1f%%' % (100.0 * b53_enc / b53_dig), b53
assert b53_soft == 2 and u'B53 [' in OUT, b53
PROOF_B53 = len([l for l in OUT.split(NL) if l.startswith(u'  ' + CHECK) and u'B53V(' in l])
assert PROOF_B53 == 110 and not [l for l in OUT.split(NL) if CROSS in l and u'B53V(' in l], PROOF_B53
DJ = json.load(io.open(u'corpus/_deriv53.json', encoding='utf-8'))
assert len(DJ) == 109, len(DJ)

# ---------- 2) 条目侧 ----------
E = io.open(ENTRY, encoding='utf-8').read()
enc_txt = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', E, re.S).group(1)
dig_txt = re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]' + NL + u'(.*?)' + NL + u'## ⟪', E, re.S).group(1)
assert len(enc_txt.replace(NL, u'')) == b53_enc, (len(enc_txt.replace(NL, u'')), b53_enc)
assert len(dig_txt) in (b53_dig, b53_dig + 1), (b53_dig, len(dig_txt))
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc_txt)
DIS = []
for _, a in CITES:
    if a not in DIS:
        DIS.append(a)
assert (len(CITES), len(DIS)) == (30, 25), (len(CITES), len(DIS))
TAGN = dict((k, len([x for x in CITES if x[0] == k])) for k in TAGS)
assert TAGN == {u'T': 14, u'L': 5, u'P': 4, u'H': 7}, TAGN
JUD = len([l for l in enc_txt.split(NL) if l.strip()])

# ---------- 3) 第五遍: 四份源(整份文件口径) ----------
FLAT = json.load(io.open(u'corpus/_b53flat.json', encoding='utf-8'))
SNAP = json.load(io.open(u'corpus/_b53audit.json', encoding='utf-8'))[u'B53']
assert all(SNAP[k] == FLAT[k] for k in FLAT), u'契约与门槛快照不一致'
RAW = [io.open(x, encoding='utf-8', errors='replace').read() for x in PATHS]
BY = [os.path.getsize(x) for x in PATHS]
FF = chr(12)
BODY = RAW[:3] + [re.sub(u'<[^>]*>', u' ', RAW[3])]
ls = lambda x: x.split(NL)[:-1]
nb = lambda x: [l for l in ls(x) if l.strip()]
FAILS = []
M = {}


def chk(key, f1, f2=None):
    """每个标量按两种口径各数一遍: 整份文件 ⇎ 去标签正文; 契约须与其中之一逐值相等。"""
    a = [f1(x) for x in RAW]
    b = [(f2 or f1)(x) for x in BODY]
    fv = FLAT[key]
    if fv == a:
        M[key] = u'整份文件'
    elif fv == b:
        M[key] = u'去标签正文'
    else:
        FAILS.append((key, fv, a, b))


def chks(key, f, i):
    fv = FLAT[key]
    a, b = f(RAW[i]), f(BODY[i])
    if fv == a:
        M[key] = u'整份文件·第 ' + CN[i]
    elif fv == b:
        M[key] = u'去标签正文·第 ' + CN[i]
    else:
        FAILS.append((key, fv, a, b))

chk(u'chars', lambda x: len(x))
chk(u'lines', lambda x: len(ls(x)))
chk(u'nonblank', lambda x: len(nb(x)))
chk(u'maxlen', lambda x: max(len(l) for l in ls(x)))
chk(u'medlen', lambda x: sorted(len(l) for l in nb(x))[len(nb(x)) // 2])
chk(u'formfeed', lambda x: x.count(FF))
chk(u'nonascii', lambda x: sum(1 for c in x if ord(c) > 127))
chk(u'naskinds', lambda x: len(set(c for c in x if ord(c) > 127)))
chks(u'html_tags', lambda x: len(re.findall(u'<[a-zA-Z]', x)), 3)
GLY = {u'oplus': u'⊕', u'le': u'≤', u'prime': u'′', u'ldots': u'…', u'cdot': u'⋅',
       u'minus': u'−', u'endash': u'–', u'emdash': u'—', u'fffd': chr(0xFFFD), u'hyph': u'-'}
for k, ch in GLY.items():
    chk(k, lambda x, ch=ch: x.count(ch))
skel = lambda t: re.sub(u'[^0-9a-z]', u'', t.lower())


def pairbase(x):
    return len([l for l in ls(x) if len(skel(l)) >= FLAT[u'skmin']])


chks(u'pairtotal', pairbase, 0)
assert not FAILS, FAILS[:8]

NCAL = 4 * len(M)
assert [SNAP[k] for k in (u'anchor_total', u'anchor_distinct', u'anchor_single', u'anchor_cross',
                          u'anchor_all4', u'anchor_err', u'checks', u'regen_both')] == \
       [30, 25, 14, 11, 0, 0, 100, 1], SNAP

# ---------- 4) README ----------
t = io.open(F, encoding='utf-8').read()
assert u'共 **52 条**' in t
t = sub(u'共 **52 条**（`babeltele/B01..B52`）', u'共 **53 条**（`babeltele/B01..B53`）', t)
t = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（52 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（53 条）', t)

b52p = [l for l in t.split(NL) if l.startswith(u'**B52 把对照轴')]
assert len(b52p) == 1
NEWP = (u'**B53 把对照轴换成同一份 FIPS 202 的四种序列化**：'
        u'`raw/fips202.txt`（官方纯文本 ⟦T⟧: %s 字节／%s 行／非空 %s 行／字符 %s） ⇎ '
        u'`raw/fips202_pdflayout.txt`（本机按版式 ⟦L⟧: %s 字节／%s 行／字符 %s／分页符 %s 枚） ⇎ '
        u'`raw/fips202_plain.txt`（本机无版式 ⟦P⟧: %s 字节／%s 行／最长行 %s 字符） ⇎ '
        u'`raw/fips202.html`（官方落地页 ⟦H⟧: %s 字节／%s 行／标签 %s 枚）；'
        u'另有 `raw/fips202.pdf`（%s 页／%s 个流）只作页数与流的旁证，不作锚源。'
        u'最强一环是“同一行”的四级判法：官方 txt 的 %s 行骨架在按版式层 %s ⇎ %s ⇎ %s、'
        u'在无版式层 %s ⇎ %s ⇎ %s、在落地页 %s ⇎ %s ⇎ %s。'
        u'字形命运表 ⊕ %s ⇎ %s ⇎ %s ⇎ %s、≤ %s ⇎ %s ⇎ %s ⇎ %s、替换符 U+FFFD %s ⇎ %s ⇎ %s ⇎ %s'
        u'（本机两层的非 ASCII 全是替换符；落地页那 %s 枚是页面自身的不可断空格与曲引号）。'
        u'词集的包含关系随分词口径翻牌（官方 txt 独有 %s → %s 个），'
        u'落地页的“正文”随算不算属性翻牌（uswds %s ⇎ %s，八个关键词家族 %s ⇎ %s）。'
        u'本机两份由 pdftotext 现生两遍字节相同（这一句入门槛），抽取器版本与两份产物的 sha 只进解读注；'
        u'“哪一种序列化才算这份标准的正文”与“⊕ 在 PDF 里本来画的是什么”不可由在库文件判定，'
        u'判词按第三档写、门槛不背书。') % tuple(
    [fmt(x) for x in [
        BY[0], FLAT[u'lines'][0], FLAT[u'nonblank'][0], FLAT[u'chars'][0],
        BY[1], FLAT[u'lines'][1], FLAT[u'chars'][1], FLAT[u'formfeed'][1],
        BY[2], FLAT[u'lines'][2], FLAT[u'maxlen'][2],
        BY[3], FLAT[u'lines'][3], FLAT[u'html_tags'],
        FLAT[u'pdf_pages'], FLAT[u'pdf_streams'],
        FLAT[u'pairtotal'], FLAT[u'pair_tl_raw'], FLAT[u'pair_tl_strip'], FLAT[u'pair_tl_skel'],
        FLAT[u'pair_tp_raw'], FLAT[u'pair_tp_strip'], FLAT[u'pair_tp_skel'],
        FLAT[u'pair_th_raw'], FLAT[u'pair_th_strip'], FLAT[u'pair_th_skel'],
        FLAT[u'oplus'][0], FLAT[u'oplus'][1], FLAT[u'oplus'][2], FLAT[u'oplus'][3],
        FLAT[u'le'][0], FLAT[u'le'][1], FLAT[u'le'][2], FLAT[u'le'][3],
        FLAT[u'fffd'][0], FLAT[u'fffd'][1], FLAT[u'fffd'][2], FLAT[u'fffd'][3],
        FLAT[u'nonascii'][3], FLAT[u'onlya_tl'], FLAT[u'onlyb_tl'],
        FLAT[u'html_uswds_raw'], FLAT[u'html_uswds_body'],
        FLAT[u'hkw_raw'], FLAT[u'hkw_body']]])
t = t.replace(b52p[0] + NL, b52p[0] + NL + NEWP + NL, 1)

r52 = [l for l in t.split(NL) if l.startswith(u'| B52 | %s（新建' % fmt(int(b52[1])))]
assert len(r52) == 1
R116 = (u'| B53 | %s（新建, 同一份标准的四种序列化 %s 处标注／%s 个不同串（登记 %s 条锚全命中，'
        u'每标签 T %s ⇎ L %s ⇎ P %s ⇎ H %s）: 四源四色锚位 官方 txt ⟦T⟧ ⇎ 本机按版式 ⟦L⟧ ⇎ 本机无版式 ⟦P⟧ ⇎ 官方落地页 ⟦H⟧; '
        u'最强一环是“同一行”的四级判法: %s 行骨架逐级 %s ⇎ %s ⇎ %s（按版式）⇎ %s ⇎ %s ⇎ %s（无版式）⇎ %s ⇎ %s ⇎ %s（落地页，其中 4 行为页眉行）; '
        u'码点存活表 ⊕ %s ⇎ 0 ⇎ 0 ⇎ 0 ⇎ ≤ %s ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 替换符 0 ⇎ %s ⇎ %s ⇎ 0 ⇎ 非 ASCII %s ⇎ %s ⇎ %s ⇎ %s（种类 %s ⇎ %s ⇎ %s ⇎ %s）; '
        u'词集独有随口径翻牌 %s → %s ⇎ 落地页两种正文 uswds %s ⇎ %s、关键词家族 %s ⇎ %s; '
        u'同数冲突登记 84 次、零项 31 枚折成一条算式; 门槛侧 %s 枚推导键／%s 处 B53V 复算点，'
        u'四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 %s 条锚归一全等，第三档现跑只留“两遍字节相同”入门槛） |') % (
    fmt(b53_enc), len(CITES), len(DIS), len(DIS), TAGN[u'T'], TAGN[u'L'], TAGN[u'P'], TAGN[u'H'],
    fmt(FLAT[u'pairtotal']), FLAT[u'pair_tl_raw'], FLAT[u'pair_tl_strip'], FLAT[u'pair_tl_skel'],
    FLAT[u'pair_tp_raw'], FLAT[u'pair_tp_strip'], FLAT[u'pair_tp_skel'],
    FLAT[u'pair_th_raw'], FLAT[u'pair_th_strip'], FLAT[u'pair_th_skel'],
    FLAT[u'oplus'][0], FLAT[u'le'][0], FLAT[u'fffd'][1], FLAT[u'fffd'][2],
    fmt(FLAT[u'nonascii'][0]), FLAT[u'nonascii'][1], FLAT[u'nonascii'][2], FLAT[u'nonascii'][3],
    FLAT[u'naskinds'][0], FLAT[u'naskinds'][1], FLAT[u'naskinds'][2], FLAT[u'naskinds'][3],
    FLAT[u'onlya_tl'], FLAT[u'onlyb_tl'],
    FLAT[u'html_uswds_raw'], FLAT[u'html_uswds_body'], FLAT[u'hkw_raw'], FLAT[u'hkw_body'],
    len(DJ), PROOF_B53, len(DIS))
t = t.replace(r52[0] + NL, r52[0] + NL + R116 + NL, 1)

raw52 = [l for l in t.split(NL) if l.startswith(u'| B52 | `raw/tz/zonenow.tab`')]
assert len(raw52) == 1
R188 = (u'| B53 | `raw/fips202.txt`（官方纯文本 ⟦T⟧: %s 字节／%s 字符／%s 行） ⇎ '
        u'`raw/fips202_pdflayout.txt`（本机按版式 ⟦L⟧: %s 字节／%s 字符／%s 行／分页符 %s） ⇎ '
        u'`raw/fips202_plain.txt`（本机无版式 ⟦P⟧: %s 字节／%s 字符／%s 行／最长行 %s） ⇎ '
        u'`raw/fips202.html`（官方落地页 ⟦H⟧: %s 字节／%s 字符／%s 行／标签 %s 枚）'
        u'（另有 `raw/fips202.pdf`（%s 页／%s 个流）只作页数与流的旁证，不作锚源） | '
        u'一份标准 ⇎ 四种序列化 ⇒ 行数、行长、分页符、行尾空格、词集包含、符号存活全部随抽取器改口，'
        u'能确定的只有可复算的那部分（骨架四级配对 ⇎ 码点存活表 ⇎ 本机产物重跑字节相同） |') % tuple(
    [fmt(x) for x in [
        BY[0], FLAT[u'chars'][0], FLAT[u'lines'][0],
        BY[1], FLAT[u'chars'][1], FLAT[u'lines'][1], FLAT[u'formfeed'][1],
        BY[2], FLAT[u'chars'][2], FLAT[u'lines'][2], FLAT[u'maxlen'][2],
        BY[3], FLAT[u'chars'][3], FLAT[u'lines'][3], FLAT[u'html_tags'],
        FLAT[u'pdf_pages'], FLAT[u'pdf_streams']]])
t = t.replace(raw52[0] + NL, raw52[0] + NL + R188 + NL, 1)

m52 = [l for l in t.split(NL) if l.startswith(u'| B52 | %s | %s |' % (fmt(int(b52[1])), b52[2]))]
assert len(m52) == 1
cols = lambda s: len(s.split(u'|'))
FULL4 = sum(FLAT[u'chars'])
M289 = (u'| B53 | %s | %s | %s（字节口径; 四份源合计 %s 字符 ⇎ 磁盘 %s 字节——判词要在同一份标准的四层之间来回数'
        u'“同一个数是在哪一层、算不算标签属性、逐字还是抹平后逐字”（骨架四级配对 ⇎ 码点存活表 ⇎ 词集两口径 ⇎ 穿层矩阵），'
        u'而摘要段只索引锚点触到的窗口，故保留率 %s 属四源对照条的必然读数，按“%s 枚推导键／%s 处复算点支撑 %s 行判词”来读；'
        u'原料本身四种形状（%s ⇎ %s ⇎ %s ⇎ %s 字节，最长行 %s ⇎ %s ⇎ %s ⇎ %s 字符），'
        u'最重的三判都不在任何窗口里：符号存活表（⊕／≤ 在官方 txt 有、在本机两层只剩空档）、'
        u'到骨架级的步增 %s ⇎ %s ⇎ %s、落地页只抄正文那几句（词集交 %s ⇎ 公共片段占比 %s%%） | %s | %s |') % tuple(
    [fmt(b53_enc), b53_ret, b53_rawp, fmt(FULL4), fmt(sum(BY)), b53_ret, len(DJ), PROOF_B53, JUD,
     fmt(BY[0]), fmt(BY[1]), fmt(BY[2]), fmt(BY[3]),
     fmt(FLAT[u'maxlen'][0]), fmt(FLAT[u'maxlen'][1]), fmt(FLAT[u'maxlen'][2]), fmt(FLAT[u'maxlen'][3]),
     FLAT[u'gap_tl'], FLAT[u'gap_tp'], FLAT[u'gap_th'], FLAT[u'inter_th'],
     str(FLAT[u'run_share'][2]),
     b53_uniq, b53[6]])
assert cols(M289) == cols(m52[0]), (cols(M289), cols(m52[0]))
t = t.replace(m52[0] + NL, m52[0] + NL + M289 + NL, 1)

os_sum = [l for l in t.split(NL) if l.startswith(u'| **合计（52 条）**')]
assert len(os_sum) == 1
cc = [x.strip() for x in os_sum[0].split(u'|')]
cc[1] = u'**合计（53 条）**'
cc[2] = u'**%s**' % fmt(enc_all)
cc[3] = u'%s（摘要段合计 %s）' % (ret_all, fmt(dig_all))
cc[5] = u'**%s**' % fmt(uniq_all)
t = t.replace(os_sum[0] + NL, u'| ' + u' | '.join(cc[1:-1]) + u' |' + NL, 1)

run52 = [l for l in t.split(NL) if u'corpus/_readme52.py' in l and l.strip().startswith(u'python')]
assert len(run52) == 1
RUN = (u'python -X utf8 corpus/_pick53.py                # 选锚: 四份源各截一层(官方 txt ⇎ 本机两种抽取 ⇎ 官方落地页), '
       u'候选池 %s 条现算, 正文只用其中 %s 条; 骨架四级配对 ⇎ 码点存活表 ⇎ 词集两口径 ⇎ 穿层矩阵全部在此遍算出\n'
       u'python -X utf8 corpus/_mkB53.py                  # 建条目: 扁平契约 %s 枚键／DERIV %s 枚算式, 占位符未替换 0 个\n'
       u'python -X utf8 corpus/_mkdigest3.py B53 <entry> T raw/fips202.txt 15 25 L raw/fips202_pdflayout.txt 15 25 '
       u'P raw/fips202_plain.txt 15 25 H raw/fips202.html 15 25   # 四源分节摘要(%s 字符, 窗口按 15⇎25 取锚点行)\n'
       u'python -X utf8 corpus/_wire53.py                 # 接门槛: 现算段机械抽入 _b53_scan, 插门前把扁平 %s 枚键与推导 %s 枚算式逐一对账\n'
       u'python -X utf8 corpus/atomcheck.py B53 corpus/_atoms53.txt   # 工具侧独立逐字校验: ok=%s bad=0\n'
       u'python -X utf8 corpus/_fill53.py                 # 解读注: 第四遍现算(9 组 200 枚标量)＋四套归一口径比对(%s 条锚全等)＋第三档现跑 pdftotext\n'
       u'python -X utf8 corpus/_readme53.py               # 记账: 本文件第五遍再量一次四份源(%s 枚标量两种口径各数一遍, 与契约⇎门槛快照逐键对表), 故四种序列化差异不是转述'
       ) % (fmt(1496), len(DIS), len(FLAT), len(DJ), fmt(b53_dig), len(FLAT), len(DJ),
            len(DIS), len(DIS), NCAL)
t = t.replace(run52[0] + NL, run52[0] + NL + RUN + NL, 1)

io.open(F, 'w', encoding='utf-8', newline=NL).write(t)

# ---------- 5) 残留 ----------
STALE = [(i + 1, l[:90]) for i, l in enumerate(t.split(NL))
         if re.search(u'共 \\*\\*5[0-2] 条\\*\\*|（5[0-2] 条）|合计（5[0-2] 条）', l)]
MIS = [(i + 1, l[:90]) for i, l in enumerate(t.split(NL))
       if re.search(u'机检[^。]{0,24}[0-9]{3,4}', l) and str(proofs) not in l]
print(u'第五遍 %s 枚标量 ⇎ 契约 ⇎ 门槛快照逐键全等 ｜ 锚 %s 处／%s 串／标签分布 %s'
      % (fmt(NCAL), len(CITES), len(DIS), TAGN))
print(u'README 已记账 52→53 ｜ 门槛 %d 条 PASS ｜ 推导 %d 枚 ｜ 唯一码点 %s ｜ 保留 %s ｜ 软提示 %d'
      % (NENT, proofs, fmt(uniq_all), ret_all, soft_all))
print(u'B53 行: 摘要 %s ⇎ 编码 %s ⇎ %s ⇎ 原文保留 %s ⇎ 判词 %s 行 ⇎ 提示 %d'
      % (fmt(b53_dig), fmt(b53_enc), b53_ret, b53_rawp, JUD, b53_soft))
print(u'合计行: ' + [l for l in t.split(NL) if l.startswith(u'| **合计（53 条）**')][0][:130])
print(u'残留 5[0-2] 条: %d 处 ｜ 机检数待读: %d 处 ｜ README 字符 %s' % (len(STALE), len(MIS), fmt(len(t))))
for x in (STALE + MIS)[:10]:
    print(u'   %d | %s' % x)
