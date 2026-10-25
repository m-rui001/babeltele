# -*- coding: utf-8 -*-
"""B56 ⛓解读注: 这段里的每个数由本脚本现测并 assert, 不手填。
四套实现: 采集侧 corpus/_pick56.py(先于条目写成, 落 corpus/_b56meas.json) ⇎ 建条目侧 corpus/_mkB56.py(落扁平契约
corpus/_b56flat.json, 与采集侧在 TIE 表上逐量对账) ⇎ 审计器侧 corpus/audit.py::_b56_scan()(快照落 corpus/_b56audit.json)
⇎ 本注自己从三份 raw 现取的第四遍。
必须披露的一处非独立性: _b56_scan 的量测段是从 _mkB56.py 的 SCAN 段机械抽出后插进门槛的(见 corpus/_wire56.py),
所以它的独立性不来自“另写一遍”, 而来自 ①采集侧与本注是两套真独立实现, ②插门前 _b56flat.json 的每个键与 DERIV['B56']
的每条算式都在抽出体上预演过, 值不符即停机。
三份字节的磁盘 mtime 与各文件自写的日期谁新谁旧只在本机成立: 本注测它、写它、并写明它不进门槛。"""
import glob, io, json, os, re, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B56_three_tables_one_code_batch.md')
M = json.load(io.open(os.path.join(C, u'_b56meas.json'), encoding='utf-8'))
CH = json.load(io.open(C + u'/_b56checks.json', encoding='utf-8'))
DJ = json.load(io.open(C + u'/_deriv56.json', encoding='utf-8'))
FLAT = json.load(io.open(C + u'/_b56flat.json', encoding='utf-8'))
B55 = json.load(io.open(C + u'/_b55flat.json', encoding='utf-8'))
ATOMP = os.path.join(C, u'_atoms56.txt')
ATOMS = [x for x in io.open(ATOMP, encoding='utf-8').read().split(NL) if x.strip()]
MEAS, TAGS, PATHS = M[u'meas'], M[u'tags'], M[u'paths']
AMET = CH[u'ameta']
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATHS]
IV, ZV, RV = TXT

# ---------- 审计器自己的快照 ----------
SNAP = os.path.join(C, u'_b56audit.json')
code = (u"import sys,json,io;sys.path.insert(0,'corpus');import audit;"
        u"A=[x.rstrip(chr(10)) for x in io.open(sys.argv[2],encoding='utf-8') if x.strip()];"
        u"json.dump({'B56':audit._B56,'SRC':dict((k,list(v)) for k,v in audit.SRC.items()),"
        u"'PN':[audit.prose_norm(a) for a in A]},"
        u"open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False)")
r = subprocess.run([sys.executable, u'-X', u'utf8', u'-c', code, SNAP, ATOMP],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-800:]
A = json.load(io.open(SNAP, encoding='utf-8'))[u'B56']
SRCALL = json.load(io.open(SNAP, encoding='utf-8'))[u'SRC']


def rnd(v):
    if isinstance(v, (dict, list)):
        return [rnd(x) for x in v] if isinstance(v, list) else dict((k, rnd(x)) for k, x in v.items())
    if isinstance(v, str):
        return v
    return round(float(v), 4)


MISS = [k for k in sorted(FLAT) if k not in A]
DIFF = [(k, FLAT[k], A[k]) for k in sorted(FLAT) if rnd(FLAT[k]) != rnd(A[k])]
assert not MISS, MISS
assert not DIFF, DIFF[:6]

# ---------- 本注的第四遍: 换一套解析器从三份字节现取 ----------
pn = lambda s: re.sub(u'[^a-z0-9]', u'', s.lower())
IL, ZL, RL = [t.split(NL) for t in TXT]
# 码表: 用“切制表符并数格”而不是逐行套正则
I3 = [l.split(u'\t') for l in IL if l.strip() and not l.startswith(u'#')]
assert len(I3) == FLAT[u'i_rows_strict'] == FLAT[u'i_rows_data']
assert set(len(x) for x in I3) == {2}
CODE = [x[0] for x in I3]
NAME = [x[1] for x in I3]
# 注册表: 用逐行状态机切段, 而不是 re.split
SEGS, cur = [], []
for l in RL:
    if l.strip() == u'%%':
        SEGS.append(cur)
        cur = []
    else:
        cur.append(l)
SEGS.append(cur)
NSEG = len([s for s in SEGS if any(x.strip() for x in s)])
assert NSEG == FLAT[u'r_segs_nonempty'] and len(SEGS) == FLAT[u'r_recs']


def fold(b):
    d = {}
    for line in b:
        m = re.match(u'^([A-Za-z][A-Za-z-]*):[ ]?(.*)$', line)
        if m:
            d[m.group(1)] = m.group(2)
    return d


FD = [fold(s) for s in SEGS]
REG = dict((d[u'Subtag'], d.get(u'Description', u'')) for d in FD if d.get(u'Type') == u'region')
DEPD = set(d[u'Subtag'] for d in FD if d.get(u'Type') == u'region' and u'Deprecated' in d)
assert len(REG) == FLAT[u'r_region_n'] and len(DEPD) == FLAT[u'dep_total']
Z3 = [l.split(u'\t') for l in ZL if l.strip() and not l.startswith(u'#')]
CC = [c for x in Z3 for c in x[0].split(u',')]
IS, ZS, RS = set(CODE), set(CC), set(REG)
assert len(IS & ZS & RS) == FLAT[u'inter3'] and len(RS - IS) == FLAT[u'r_only_i']
assert len([c for c in RS - ZS if len(c) == 2]) == FLAT[u'rz_alpha']
assert FLAT[u'rz_alpha'] == B55[u'reg_alpha_only']
N = dict(zip(CODE, NAME))
SH = sorted(IS & RS)
EQ = [c for c in SH if N[c] == REG[c]]
DIF = [c for c in SH if N[c] != REG[c]]
assert (len(EQ), len(DIF)) == (FLAT[u'name_eq'], FLAT[u'name_dif'])


# 换写法 ⇎ 换词: 先把两份名串各自投影成“字母数字流”, 投影相同即只换写法(与建条目侧先换 & 再删标点的路子不同)
def proj(s):
    return re.sub(u'[^a-z0-9]', u'', re.sub(u'(?i)&', u' and ', s.replace(u'\u2019', u"'")).lower())


LEX = [c for c in DIF if proj(N[c]) == proj(REG[c])]
assert (len(LEX), len(DIF) - len(LEX)) == (FLAT[u'name_lex'], FLAT[u'name_sem'])
# 名字在时区表里的三档: 先建“末段集合/全部段集合”, 再判每枚名落在哪一档
TAIL, PART, FREE = set(), set(), set()
for x in Z3:
    if len(x) > 2:
        ps = x[2].split(u'/')
        TAIL.add(ps[-1])
        PART.update(ps)
    for c in x[3:]:
        FREE.add(c.strip())
HN = [n for n in sorted(set(NAME)) if n in ZV]
t1 = len([n for n in HN if n in TAIL])
t2 = len([n for n in HN if n not in TAIL and n in PART])
t3 = len([n for n in HN if n not in PART])
t4 = len([n for n in HN if n not in PART and any(n in f for f in FREE)])
CMTN = [n for n in HN if n not in PART and n not in u' '.join(FREE)]
HOSTS = [sorted([p for p in PART if n in p and p != n]) for n in CMTN]
FRAG = [u'%s 嵌在 %s' % (n, u'、'.join(h)) for n, h in zip(CMTN, HOSTS)]
assert all(len(h) >= 1 for h in HOSTS), zip(CMTN, HOSTS)
assert (len(HN), t1, t2, t3) == (FLAT[u'z_name_hits'], FLAT[u'z_tail_comp'], FLAT[u'z_mid_comp'],
                                 FLAT[u'z_cmt_only'])
# 注释共用句: 第三口径——只把句号后的大写当断点, 不接行
IC = [l for l in IL if l.startswith(u'#')]
ZC = [l for l in ZL if l.startswith(u'#')]
SENT3 = lambda ls: set(s.strip() for l in ls for s in re.split(u'(?<=[.]) (?=[A-Z])', l.lstrip(u'#').strip())
                     if len(s.strip()) >= 8)
S3 = sorted(SENT3(IC) & SENT3(ZC))
# 三份自写的日期与磁盘 mtime(只在本机)
FDATE = re.search(u'^File-Date:[ ]?(\\S+)', RV, re.M).group(1)
EDATE = re.search(u'From Paul Eggert \\((\\S+)\\)', ZV).group(1)
IDATE = max(FLAT[u'i_dates'])
assert IDATE == u'2025-07-01' and len(FLAT[u'i_dates']) == 3
MT = [os.path.getmtime(p) for p in PATHS]
DAYS = [(time.mktime(time.strptime(x, u'%Y-%m-%d')) - m) / 86400.0
        for m, x in zip(MT, [IDATE, EDATE, FDATE])]
SHA = [__import__('hashlib').sha256(io.open(p, 'rb').read()).hexdigest() for p in PATHS]
CP = [len(set(pn(a) for a in ATOMS if pn(a) in pn(TXT[i]))) for i in range(3)]
VB = [len([a for a in ATOMS if a in TXT[i]]) for i in range(3)]
assert all(VB) and len(ATOMS) == AMET[u'anchor_distinct']

NT = []
add = lambda s: NT.append(s)

add(u'- 四套实现与一处非独立: 采集侧 _pick56.py ⇎ 建条目侧 _mkB56.py(扁平契约 %d 键, 与采集侧在 %d 个量上对过账) ⇎ '
    u'门槛内 _b56_scan()。本注是第四遍: 上面 %d 个键逐个与审计器快照对齐(不符即停机), 另自行从三份字节重取了 '
    u'码表行 %d(用“切制表符数格”而非逐行正则)、注册表段 %d／%d(用逐行状态机而非 re.split)、'
    u'region %d 枚、三向交 %d 枚、名全等 %d ⇎ 不等 %d、只换写法 %d、名字在时区表的三档 %d／%d／%d——'
    u'十二个数与契约逐一相同。换解析路子不是为了让数不同, 而是为了证明这些数不依赖某一种切法。'
    u'另有一档契约里没有的: 那 %d 枚“不在任何路径段里”的名只有 %d 枚整串落在第四列自由文本内, '
    u'余下 %d 枚(%s)连第 4 格也不进——它们只以碎片嵌在更长的标识符段里(%s)。'
    % (len(FLAT), len(CH[u'meas_tie_keys']), len(FLAT), len(I3), NSEG, FLAT[u'r_recs'], len(REG),
       len(IS & ZS & RS), len(EQ), len(DIF), len(LEX), t1, t2, t3, t3, t4, len(CMTN),
       u' ／ '.join(CMTN), u' ⇎ '.join(FRAG)))
add(u'- _b56_scan 的量测段由 _wire56.py 从 _mkB56.py 的 SCAN 段逐行抽出(只改路径常量与模块别名), '
    u'插门前把 _b56flat.json 的 %d 个键与 DERIV[\'B56\'] 的 %d 条算式在抽出体上跑过; '
    u'因此真正独立的两遍是 _pick56.py 与本注: 采集侧按 split 制表符解析码表、按逐行状态机切注册表、'
    u'把注释共用句的“在 I 连续”与“在 Z 连续”按非互斥口径数(得 %d ⇎ %d ⇎ %d ⇎ %d), '
    u'建条目侧改成互斥四档(得 %d ⇎ %d ⇎ %d ⇎ %d, 相加校住 %d)——同一件事的两种分法都登记成键, 不靠断言假设相等。'
    % (len(FLAT), len(DJ), MEAS[u'cmt_contig_both'], MEAS[u'cmt_contig_i'], MEAS[u'cmt_contig_z'],
       MEAS[u'cmt_contig_none'], FLAT[u'cmt_contig_both'], FLAT[u'cmt_contig_i'], FLAT[u'cmt_contig_z'],
       FLAT[u'cmt_contig_none'], FLAT[u'cmt_sent_shared']))
CL2 = dict((k, v) for k, v in CH[u'collisions'].items() if len(v) > 1)
add(u'- 门槛的账: DERIV 键 %d 个 ⇎ 引用点 %d 处 ⇎ 同数共键 %d 组(两名以上 %d 组) ⇎ 0 键折 %d 项。'
    u'同数的字面不取第一条算式, 而是复合式 LIT*(1-(max(全部算式)-min(全部算式))): 每条算式都等于该字面时括号才为 1。'
    % (len(DJ), sum(v.count(u'B56V') for v in DJ.values()), len(CH[u'collisions']), len(CL2),
       DJ[u'0'].count(u'+') + 1))
for k, v in sorted(CL2.items(), key=lambda x: (-len(x[1]), x[0]))[:6]:
    add(u'  - 同数 %s(%d 条): %s' % (k, len(v), u' ⇎ '.join(v)))
add(u'- 主轴的来历(必须写, 因为它一度给出错的头条数): “这两个名字是否一致”按 join 键有三种问法, 三个数不同——'
    u'按码 join 得全等 %d 条(可比 %d 枚), 按名串 join 得 %d 条(其中 %d 条按码也对齐, 余 %d 条是同名挂在别枚码上: %s), '
    u'问时区表只得碎片级存活 %d 条(它一个名字列都没有, 列数只有 %s)。'
    u'采集侧第一版把“不等”只分成两档(%d ⇎ %d), 没管谁的名字更长; 建条目侧补了长名三档(%d ⇎ %d ⇎ %d, 相加校住 %d) '
    u'与字符数净差 %d, 因为“注册表把名写长了 %d 个字符”是这条里唯一能算出来的取词倾向。'
    % (FLAT[u'name_eq'], FLAT[u'name_cmp'], FLAT[u'name_str_pool'], FLAT[u'name_eq'], FLAT[u'name_cross'],
       u' ／ '.join(u'%s 名 %s ⇎ R 侧另挂在 %s' % (c, n, u','.join(v)) for (c, n, v) in FLAT[u'name_cross_v']),
       FLAT[u'z_name_hits'], u' ⇎ '.join(str(x) for x in FLAT[u'z_cols']),
       MEAS[u'name_lex'], MEAS[u'name_sem'], FLAT[u'name_longer_r'], FLAT[u'name_longer_i'],
       FLAT[u'name_samelen'], FLAT[u'name_dif'], FLAT[u'name_dif_chars'], FLAT[u'name_dif_chars']))
add(u'- 跨条目那笔桥账是算出来的, 不是抄来的: 本条现量 region 两位 %d 枚 = 与码表共有 %d ＋ 码表没有 %d(差 %d); '
    u'时区表国家列之外的两位 region %d 枚 = 本条的 %d ＋ 码表有时区表没用的 %d 枚(桥差 %d)。'
    u'B55 那份契约里同一个量登记成 reg_alpha_only = %d, 两处相等才允许写“接得上”——'
    u'而它成立的前提(Z 的码全在码表里 ⇎ 码表的两位码全在注册表里)也由本条数出来: %d ＋ %d。'
    % (FLAT[u'r_alpha'], FLAT[u'r_alpha_in_i'], FLAT[u'r_only_i_alpha'], FLAT[u'r_alpha_close'],
       FLAT[u'rz_alpha'], FLAT[u'r_only_i_alpha'], FLAT[u'i_only_z'], FLAT[u'bridge'],
       B55[u'reg_alpha_only'], FLAT[u'z_only_i'], FLAT[u'i_only_r']))
add(u'- 注释口径的第三层(本注自己数, 不进门槛): 接行归一再断句得共用句 %d 条(%s 是全部四条); '
    u'若“不接行、只在单行内断句”, 共用句只剩 %d 条, 因为两份表都把同一条声明折在不同长度的行上; '
    u'若按整行逐字判, 共用 %d 行, 而那唯一一行是 %s——一个拆行残片, 不是规则。'
    u'三种口径的数各登记成键(接行 %d ⇎ 不接行 %d ⇎ 整行 %d), 判词报的是后者与接行那两档。'
    % (FLAT[u'cmt_sent_shared'], u' ⇎ '.join(u'“%s”' % s[:52] for s in FLAT[u'cmt_sent_shared_v']),
       len(S3), FLAT[u'cmt_line_shared'], FLAT[u'cmt_line_shared_v'][0],
       FLAT[u'cmt_sent_shared'], len(S3), FLAT[u'cmt_line_shared']))
add(u'- 码表注释自写的命名理由是可判的, 而且两头都判: 它点名该用的 %d 串全在场 ⇎ 点名该避的 %d 串全不在场'
    u'(相加 %d, 差 %d), “该避却反而在场”%d 串; 它自写“按码排序”却把列名注释拆成两行(%d), '
    u'连写的 country-code 出现 %d 次——这条律由它自己的排版违反。'
    u'注释里 %d 个日期按行序 %s 与值序逆 %d 处, 被压在后面那条恰是闰日(%d 枚)——文件没说自己按日期排序, 所以这是观察不是违约。'
    % (FLAT[u'i_claim_used'], FLAT[u'i_claim_avoided'], FLAT[u'i_claim_total'], FLAT[u'i_claim_open'],
       FLAT[u'i_claim_avoided_in'], FLAT[u'i_hdr_split'], FLAT[u'i_hdr_cc'],
       len(FLAT[u'i_dates']), u' ⇎ '.join(FLAT[u'i_dates_byline']), FLAT[u'i_date_unsorted'], FLAT[u'i_leap']))
add(u'- 三份文件的指纹(旁证, 判词里只报“种数”而不报串, 因为串里的数字段无法由字节直接命中): %s; '
    u'sha16 种数 %d ⇎ 非 ASCII 枚 %s ⇎ 字节减字符 %s ⇎ 弯引号四类 %s——三份都不是纯 ASCII, 所以“字符数=字节数”在 %d 份上成立。'
    % (u' ⇎ '.join(SHA), FLAT[u'sha_distinct'], u' ⇎ '.join(str(x) for x in FLAT[u'nonascii']),
       u' ⇎ '.join(str(x) for x in FLAT[u'bytegap']), u' ⇎ '.join(str(x) for x in FLAT[u'curly']), FLAT[u'eqc']))
add(u'- 只在本机成立的一笔(不进门槛): 三份字节自写的日期分别是码表的 %s ⇎ 时区表的 %s ⇎ 注册表 File-Date 的 %s, '
    u'而磁盘 mtime 与这些日期相差 %+.2f ⇎ %+.2f ⇎ %+.2f 天; 谁抓到、抓于何时, 在库文件里没有依据。'
    % (IDATE, EDATE, FDATE, -DAYS[0], -DAYS[1], -DAYS[2]))
SH = []
for src_i, p in enumerate(PATHS):
    for f in glob.glob(u'corpus/babeltele/B*.md'):
        t = os.path.basename(f).split(u'_')[0]
        if t == u'B56' or SRCALL.get(t) and p not in SRCALL[t]:
            continue
        ep = glob.glob(u'corpus/babeltele/%s_*.md' % t)
        AT2 = set()
        if ep:
            TT2 = io.open(ep[0], encoding='utf-8').read()
            mm = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT2, re.S)
            AT2 = set(re.findall(u'⟨([^⟨⟩]+)⟩', mm.group(1))) if mm else set()
        SH.append((t, src_i, len(AT2), len(AT2 & set(ATOMS))))
SH.sort()
MX = max([x[3] for x in SH]) if SH else 0
add(u'- 同一份字节被几代条目各压过一次: 共用源 %d 处 %s。本条与它们不重叠也不冲突——交叠最多的那条也只共用 %d 串锚, '
    u'共用的是同一句原文而不是同一个论断: B55 量注册表⇎时区表的借码与值域两种判法, B49 量检查这张表的 awk, '
    u'B52 量时效分区, B45 量同一个名字的三种对象, B10 量版本账; 而 iso3166.tab 此前从未被任一条目当过源, '
    u'本条第一次把“码表自己的注释律”与“它借给时区表当列值的那批码”接成三向账。'
    % (len(SH), u' ／ '.join(u'%s(源%s, 锚%d, 交%d)' % x for x in SH), MX))
add(u'- 锚的可核性: %d 串去重锚按标签判成员, 归一只属一源 %d ⇎ 两源 %d ⇎ 三源 %d(相加校住 %d), '
    u'逐源判成员共 %d 次; 按码位归一后各源命中的锚串数 %s ⇎ 逐字命中 %s。'
    u'不可由在库文件判定而写在这里的: ISO 官方此刻在用的名串(库里只有两份表各自的写法, 没第三份参照), '
    u'注册表把 “East Timor” 留在已弃码 TP 而把 TL 另立的流程理由, %d 枚 R 独有两位码为何没进时区表, '
    u'以及时区表第一列该不该用 UN 数字区码(它只自写“用 ISO 3166 两字母码”)。'
    % (AMET[u'anchor_distinct'], AMET[u'anchor_single'], AMET[u'anchor_two'], AMET[u'anchor_three'],
       AMET[u'anchor_distinct'], AMET[u'checks'], u' ⇎ '.join(str(x) for x in CP),
       u' ⇎ '.join(str(x) for x in VB), len(FLAT[u'r_i_alpha_v'])))

body = NL.join(NT)
T = io.open(ENTRY, encoding='utf-8').read()
head = u'## ⛓解读注'
i = T.index(head)
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(T[:i] + head + NL + NL + body + NL)
print(u'注已写: %d 行 ｜ 契约 %d 键全对齐 ｜ 共用源 %d 处(锚集交集 %s) ｜ mtime 与自写日期差 %+.2f ⇎ %+.2f ⇎ %+.2f 天(只在本机)' % (
    len(NT), len(FLAT), len(SH), [x[3] for x in SH], -DAYS[0], -DAYS[1], -DAYS[2]))
