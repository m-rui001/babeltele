# -*- coding: utf-8 -*-
"""B55 ⛓解读注: 这段里的每个数由本脚本现测并 assert, 不手填。
四套实现: 采集侧 corpus/_pick55.py(先于条目写成, 落 corpus/_b55meas.json) ⇎ 建条目侧 corpus/_mkB55.py(落扁平契约
corpus/_b55flat.json, 与采集侧在 TIE 表上逐量对账) ⇎ 审计器侧 corpus/audit.py::_b55_scan()(快照落 corpus/_b55audit.json)
⇎ 本注自己从两份 raw 现取的第三遍。
必须披露的一处非独立性: _b55_scan 的量测段是从 _mkB55.py 的 SCAN 段机械抽出后插进门槛的(见 corpus/_wire55.py),
所以它的独立性不来自“另写一遍”, 而来自 ①采集侧与本注是两套真独立实现, ②插门前 _b55flat.json 的每个键与 DERIV['B55']
的每条算式都在抽出体上预演过, 值不符即停机。
磁盘 mtime 与文件里写的两个日期谁新谁旧只在本机成立: 本注测它、写它、并写明它不进门槛。"""
import glob, io, json, os, re, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B55_subtag_registry_and_zone1970_tab.md')
M = json.load(io.open(os.path.join(C, u'_b55meas.json'), encoding='utf-8'))
CH = json.load(io.open(C + u'/_b55checks.json', encoding='utf-8'))
DJ = json.load(io.open(C + u'/_deriv55.json', encoding='utf-8'))
FLAT = json.load(io.open(C + u'/_b55flat.json', encoding='utf-8'))
ATOMP = os.path.join(C, u'_atoms55.txt')
ATOMS = [x for x in io.open(ATOMP, encoding='utf-8').read().split(NL) if x.strip()]
MEAS, TAGS, PATHS = M[u'meas'], M[u'tags'], M[u'paths']
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
TXT = [RD(p) for p in PATHS]
R, Z = TXT

# ---------- 审计器自己的快照 ----------
SNAP = os.path.join(C, u'_b55audit.json')
code = (u"import sys,json,io;sys.path.insert(0,'corpus');import audit;"
        u"A=[x.rstrip(chr(10)) for x in io.open(sys.argv[2],encoding='utf-8') if x.strip()];"
        u"json.dump({'B55':audit._B55,'SRC':dict((k,list(v)) for k,v in audit.SRC.items()),"
        u"'PN':[audit.prose_norm(a) for a in A]},"
        u"open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False)")
r = subprocess.run([sys.executable, u'-X', u'utf8', u'-c', code, SNAP, ATOMP],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-800:]
SN = json.load(io.open(SNAP, encoding='utf-8'))
A = SN[u'B55']
SRCALL = SN[u'SRC']


def rnd(v):
    if isinstance(v, dict):
        return dict((k, rnd(x)) for k, x in v.items())
    if isinstance(v, list):
        return [rnd(x) for x in v]
    if isinstance(v, str):
        return v
    return round(float(v), 4)


MISS = [k for k in sorted(FLAT) if k not in A]
DIFF = [(k, FLAT[k], A[k]) for k in sorted(FLAT) if rnd(FLAT[k]) != rnd(A[k])]
assert not MISS, MISS
assert not DIFF, DIFF[:6]

# ---------- 本注的第三遍: 自己从两份字节现取 ----------
pn = lambda s: re.sub(u'[^a-z0-9]', u'', s.lower())
RL = R.split(NL)
SEGS = [b for b in R.split(NL + u'%%' + NL)]
assert len(SEGS) == FLAT[u'records']


def fold(b):
    d = {}
    for line in b.split(NL):
        m = re.match(u'^([A-Z][A-Za-z-]*):[ \t]*(.*)$', line) if line[:1] not in u' \t' else None
        if m:
            d[m.group(1)] = m.group(2).strip()
    return d


FD = [fold(b) for b in SEGS]
LN = [(m.group(1), m.group(2).strip()) for b in SEGS for line in b.split(NL)
      for m in [re.match(u'^([A-Z][A-Za-z-]*):[ \t]*(.*)$', line)] if line[:1] not in u' \t' and m]
assert len(LN) == FLAT[u'field_lines']
PRE_LN = [v for k, v in LN if k == u'Prefix']
PRE_FOLD = [d[u'Prefix'] for d in FD if u'Prefix' in d]
SUB = set(v for k, v in LN if k == u'Subtag') | set(v for k, v in LN if k == u'Preferred-Value')
vw_line = len(set(v for v in PRE_LN for p in [v] if p not in SUB))
vw_fold = len(set(v for v in PRE_FOLD if v not in SUB))
assert len(PRE_LN) == FLAT[u'x_occ'][3] and len(PRE_FOLD) == FLAT[u'x_field_n'][3]
assert vw_line == FLAT[u'x_vw'][3]
PV_LINE = [v for k, v in LN if k == u'Preferred-Value']
ALLSUB = set(v for k, v in LN if k == u'Subtag')
assert len(set(v for v in PV_LINE if v not in ALLSUB)) == FLAT[u'x_vw'][2]
# 折叠口径下的四字段整码越界总数(采集侧第一版用的就是这个口径)
SCR = set()
LANG = set()
for b in SEGS:
    d = fold(b)
    if u'Subtag' not in d:
        continue
    if d.get(u'Type') == u'script':
        SCR.add(d[u'Subtag'])
    if d.get(u'Type') == u'language':
        LANG.add(d[u'Subtag'])
assert len(SCR) == FLAT[u'x_dom'][0] and len(LANG) == FLAT[u'x_dom'][1]
PREF = set(d[u'Preferred-Value'] for d in FD if u'Preferred-Value' in d)
DOMF = {u'Suppress-Script': SCR, u'Macrolanguage': LANG, u'Preferred-Value': ALLSUB,
        u'Prefix': ALLSUB | PREF}
assert len(LANG) == FLAT[u'x_dom'][1] and len(PREF) == FLAT[u'pref_distinct']
FOLDV = dict((k, len(set(d[k] for d in FD if k in d) - DOMF[k])) for k in DOMF)
FOLD_TOTAL = sum(FOLDV.values())
assert FOLD_TOTAL + (FLAT[u'x_vw'][3] - FOLDV[u'Prefix']) == FLAT[u'viol_whole']
assert FOLDV[u'Preferred-Value'] == FLAT[u'x_vw'][2]
# 头条数 29 是“不同值”口径: 同一复合值在几段里重复登记只计一枚。按出现处数判是另一个数。
VWLN = dict((k, [v for kk, v in LN if kk == k and v.strip() and v not in DOMF[k]]) for k in DOMF)
OCCV = dict((k, len(VWLN[k])) for k in DOMF)
DISTV = dict((k, len(set(VWLN[k]))) for k in DOMF)
F4ORD = [u'Suppress-Script', u'Macrolanguage', u'Preferred-Value', u'Prefix']
assert [DISTV[k] for k in F4ORD] == FLAT[u'x_vw']
assert OCCV[u'Prefix'] + OCCV[u'Preferred-Value'] == sum(OCCV.values())
assert sum(OCCV.values()) - sum(DISTV.values()) == OCCV[u'Prefix'] - DISTV[u'Prefix']
assert OCCV[u'Preferred-Value'] == DISTV[u'Preferred-Value']
ZL = [l for l in Z.split(NL) if l.strip() and not l.startswith(u'#')]
assert len(ZL) == FLAT[u'z_rows'] and Z.count(u'\t') == FLAT[u'tabs'][1]
ZC = sorted(set(len(l.split(u'\t')) for l in ZL))
COLNAME = [l for l in Z.split(NL) if l.startswith(u'#') and u'\t' in l and not l.startswith(u'#@')]
HDR = COLNAME[0].count(u'\t')
assert ZC == [3, 4] and len(COLNAME) == 1 and HDR == 3
TAILBAD = [l.split(u'\t') for l in ZL
           if l.split(u'\t')[0].split(u',')[1:] != sorted(l.split(u'\t')[0].split(u',')[1:])]
assert len(TAILBAD) == FLAT[u'z_tail_un']
BADZONE, BADCC = TAILBAD[0][2], TAILBAD[0][0].split(u',')
assert len(BADCC) == FLAT[u'z_maxm']
DBA = MEAS[u'dep_before_add']
assert len(DBA) == FLAT[u'dep_before']
DBT = {}
for b in SEGS:
    d = fold(b)
    if u'Deprecated' in d and u'Subtag' in d:
        DBT[d[u'Subtag']] = d.get(u'Type', u'')
DBTYPE = {}
for c, dep, add in DBA:
    DBTYPE.setdefault(DBT.get(c, u'?'), []).append(c)
DBADD = sorted(set(a for c, d_, a in DBA))
DBDEPMIN = min(d_ for c, d_, a in DBA)
assert sum(len(v) for v in DBTYPE.values()) == len(DBA) and len(DBADD) == 1
assert DBDEPMIN < DBADD[0] and DBADD[0] == u'2005-10-16'
FIRST = [l.split(u'\t')[0].split(u',')[0] for l in ZL]
assert sum(1 for i in range(1, len(FIRST)) if FIRST[i] < FIRST[i - 1]) == FLAT[u'z_first_desc']
MT = [os.path.getmtime(p) for p in PATHS]
FDATE = re.search(u'^File-Date:[ \t]*(\\S+)', R, re.M).group(1)
EDATE = re.search(u'From Paul Eggert \\((\\S+)\\)', Z).group(1)
assert FDATE == FLAT[u'file_date']
DAYS = [(time.mktime(time.strptime(x, u'%Y-%m-%d')) - m) / 86400.0 for m, x in
        [(MT[0], FDATE), (MT[1], EDATE)]]
SHA = [__import__('hashlib').sha256(io.open(p, 'rb').read()).hexdigest() for p in PATHS]
CP = [len(set(pn(a) for a in ATOMS if pn(a) in pn(TXT[i]))) for i in range(2)]
VB = [len([a for a in ATOMS if a in TXT[i]]) for i in range(2)]
INPOOL = len([a for a in ATOMS if any(a in t for t in TXT)])
assert INPOOL == len(ATOMS)

NT = []
add = lambda s: NT.append(s)

add(u'- 四套实现与一处非独立: 采集侧 _pick55.py ⇎ 建条目侧 _mkB55.py(扁平契约 %d 键, 与采集侧在 %d 个量上对过账) ⇎ '
    u'门槛内 _b55_scan()。本注是第四遍: 上面 %d 个键逐个与审计器快照对齐(不符即停机), 另自行从两份字节重取了 '
    u'段数 %d、字段行 %d、Z 数据行 %d、制表符 %d、File-Date %s ——五个数与契约逐一相同。'
    % (len(FLAT), len(CH[u'meas_tie_keys']), len(FLAT), len(SEGS), len(LN), len(ZL),
       Z.count(u'\t'), FDATE))
add(u'- _b55_scan 的量测段由 _wire55.py 从 _mkB55.py 的 SCAN 段逐行抽出(只改路径常量与模块别名), '
    u'插门前把 _b55flat.json 的 %d 个键与 DERIV[\'B55\'] 的 %d 条算式在抽出体上跑过; '
    u'因此真正独立的两遍是 _pick55.py 与本注: 采集侧用“每段同名只留一格”的解析器起步, 本注自己写了两套解析器(折叠 ⇎ 逐行) '
    u'并把两种口径的差异当成被测量本身, 而不是当成噪声。' % (len(FLAT), len(DJ)))
CL2 = dict((k, v) for k, v in CH[u'collisions'].items() if len(v) > 1)
add(u'- 门槛的账: DERIV 键 %d 个 ⇎ 引用点 %d 处 ⇎ 同数共键 %d 组(两名以上 %d 组) ⇎ 0 键折 %d 项。'
    u'同数的字面不取第一条算式, 而是复合式 LIT*(1-(max(全部算式)-min(全部算式))): 每条算式都等于该字面时括号才为 1。'
    % (len(DJ), sum(v.count(u'B55V') for v in DJ.values()), len(CH[u'collisions']), len(CL2),
       DJ[u'0'].count(u'+') + 1))
for k, v in sorted(CL2.items(), key=lambda x: (-len(x[1]), x[0]))[:8]:
    add(u'  - 同数 %s(%d 条): %s' % (k, len(v), u' ⇎ '.join(v)))
add(u'- 主轴的来历(必须写, 因为它一度给出错的头条数): 四个交叉引用字段按“整码判”给 %d 个越界值, 按“拆片判”给 %d 个, '
    u'且越界减复合型 = %d, 所以越界的那 %d 枚全是含连字符的复合标签。采集侧第一版把字段值按每段只留一格来收, '
    u'Prefix 因此只收到 %d 个值(逐行口径是 %d 个, 少 %d 个, 全在 %d 段里出现第二条以上的 Prefix 之中, 单段最多 %d 行); '
    u'本注自己写两套解析器现算复现: 折叠口径下四字段整码越界合计 %d 枚(Prefix %d ⇎ Preferred-Value %d ⇎ 另两个各 0), '
    u'逐行口径 %d 枚(Prefix %d), 头条数取逐行——差 %d 枚恰好等于 Prefix 那一栏少收的 %d 枚。'
    u'再说一层口径: 头条数 %d 是“不同值”数(同一复合值在几段里重复登记只计一枚), 按出现处数判则是 %d 处'
    u'(Prefix %d ⇎ Preferred-Value %d ⇎ 另两个各 0), 多出的 %d 处全来自同一个复合值的重复登记——判词写的是前者。'
    % (FLAT[u'viol_whole'], FLAT[u'viol_piece'], FLAT[u'viol_minus_comp'], FLAT[u'viol_whole'],
       len(PRE_FOLD), len(PRE_LN), len(PRE_LN) - len(PRE_FOLD), FLAT[u'pf_multi'], FLAT[u'pf_max'],
       FOLD_TOTAL, FOLDV[u'Prefix'], FOLDV[u'Preferred-Value'],
       FLAT[u'viol_whole'], FLAT[u'x_vw'][3], FLAT[u'viol_whole'] - FOLD_TOTAL, vw_line - vw_fold,
       FLAT[u'viol_whole'], sum(OCCV.values()), OCCV[u'Prefix'], OCCV[u'Preferred-Value'],
       sum(OCCV.values()) - FLAT[u'viol_whole']))
add(u'- 同一件事的第三处口径差: Comments 段数 %d ⇎ 行数 %d, 字符数按折叠口径 %d ⇎ 按逐行 %d(差 %d)——'
    u'有一段真带两行 Comments, 所以“折叠只留最后一格”在别处也少收: Description 逐行 %d 处 ⇎ 折叠 %d 处, '
    u'不同串 %d ⇎ %d(差 %d)。这两笔都在门槛里各占键, 不是靠断言假设相等。'
    % (FLAT[u'cm_n'], FLAT[u'cm_lines'], FLAT[u'cm_chars'], FLAT[u'cm_chars_line'], FLAT[u'cm_caldiff'],
       FLAT[u'desc_lines'], FLAT[u'desc_fold'], FLAT[u'desc_dist'], FLAT[u'desc_folddist'],
       FLAT[u'desc_distgap']))
add(u'- 时区表自写的规则由它自己的数据判: 第 4 列的充要条件核对到 %d／%d 行, 两个方向的反例各 %d ⇎ %d; '
    u'“先按国家码排”在整列口径下 %d 行不守 ⇎ 去掉每行首国的口径下 %d 行不守(剩下那一行正是 %s: 首国之外 %d 枚码没按字母排, '
    u'而它同时是 %d 国共行的那一格); '
    u'制表符枚数 %d 由列结构反推(%d 列 %d 行×%d ⇎ %d 列 %d 行×%d, 加那条列名注释行的 %d 枚与 %d 行 \'#@\' 各 1 枚)完全对上, 差 %d。'
    % (FLAT[u'z4_agree'], FLAT[u'z_rows'], FLAT[u'z4_pos'], FLAT[u'z4_neg'],
       FLAT[u'z_whole_un'], FLAT[u'z_tail_un'], BADZONE, len(BADCC), FLAT[u'z_maxm'], FLAT[u'tabs'][1],
       ZC[0], FLAT[u'z_col3'], ZC[0] - 1, ZC[1], FLAT[u'z_col4'], ZC[1] - 1, HDR, FLAT[u'z_at'],
       FLAT[u'z_tab_diff']))
add(u'- 跨文件那笔账的方向性: Z 国家列 %d 枚码全部在注册表 region 池 %d 枚里(Z 有而 R 无 %d 枚), 反向缺 %d 枚 = '
    u'两位码 %d ⇎ UN 数字码 %d ⇎ 区间 %d(三档相加与 %d 差 %d)。真正“没被用到”的只有那 %d 枚两位码, '
    u'另外 %d 枚本就不是 zone1970 能写的形状——判词把这两类分开写, 合起来说“缺 %d”会夸大。'
    % (FLAT[u'z_countries'], FLAT[u'region_n'], FLAT[u'z_only'], FLAT[u'reg_only'],
       FLAT[u'reg_alpha_only'], FLAT[u'reg_digit_only'], FLAT[u'reg_range_only'],
       FLAT[u'reg_only'], FLAT[u'reg_only_sum'],
       FLAT[u'reg_alpha_only'], FLAT[u'reg_digit_only'] + FLAT[u'reg_range_only'], FLAT[u'reg_only']))
add(u'- 两份文件的指纹(旁证, 判词里只报“种数”而不报串, 因为串里的数字段无法由字节直接命中): %s ⇎ %s; '
    u'字节 %d ⇎ %d(比 %d 倍), 非 ASCII %d ⇎ %d 枚, 所以“字符数=字节数”在 %d 份上成立。'
    % (SHA[0], SHA[1], FLAT[u'bytes'][0], FLAT[u'bytes'][1], FLAT[u'ratio'],
       FLAT[u'nonascii'][0], FLAT[u'nonascii'][1], FLAT[u'eqc']))
add(u'- 时间分两档(第二档只在本机): 内容侧两个日期各写在各的文件里且逐字可锚——注册表 %s, 时区表 From Paul Eggert (%s); '
    u'磁盘 mtime(换 UTC)是 %s ⇎ %s, 各自减去内容日期 = %+.2f ⇎ %+.2f 天(正为 mtime 落在内容日期之后)。'
    u'“注册表比它自己声明的版本更新得勤”这件事在库里只能由 Added 最晚 %s 与 File-Date %s 的先后判, mtime 那条拷贝一次就失效, 所以只写在这里。'
    % (FDATE, EDATE,
       time.strftime(u'%Y-%m-%d %H:%M:%S', time.gmtime(MT[0])),
       time.strftime(u'%Y-%m-%d %H:%M:%S', time.gmtime(MT[1])), -DAYS[0], -DAYS[1],
       FLAT[u'added_max'], FDATE))
add(u'- 反向时序不是数据错, 而是两件事共用一个字段: 弃用日期早于登用日期的 %d 段, 本注逐段回查类型得 %s, '
    u'它们的 Added 全落在同一天 %s(注册表收编 ISO 已撤码的那批), 而 Deprecated 最早 %s——那是 ISO 那边撤码的日子, 早于注册表登记 %d 年。'
    u'另一侧: Added 晚于 File-Date 的 %d 段(无), 弃用日期共 %d 个不同日 ⇎ 登用日期 %d 个不同日。判词按内容判, 不替注册表的编辑顺序作保。'
    % (FLAT[u'dep_before'], u' ⇎ '.join(u'%s 型 %d 枚(%s)' % (k, len(v), u','.join(sorted(v)))
                                        for k, v in sorted(DBTYPE.items())),
       DBADD[0], DBDEPMIN, int(DBADD[0][:4]) - int(DBDEPMIN[:4]),
       FLAT[u'added_after'], FLAT[u'dep_days'], FLAT[u'added_dist']))
add(u'- 锚的账: 去重 %d 串 ⇎ 正文 %d 处 ⇎ 每标签 %s ⇎ 单源 %d ⇎ 两源同现 %d ⇎ 成员检查 %d 次 ⇎ 错配 %d 处; '
    u'本注另按“整串在该源字节里逐字出现”复查: 归一后覆盖 R %d ⇎ Z %d 串, 逐字命中 R %d ⇎ Z %d, 两源之一命中 %d／%d。'
    % (CH[u'anchor_distinct'], CH[u'anchor_total'], CH[u'tag_counts'], A[u'anchor_single'],
       A[u'anchor_both'], A[u'checks'], A[u'anchor_err'], CP[0], CP[1], VB[0], VB[1], INPOOL, len(ATOMS)))
add(u'- 假同现三枚(必须单写, 因为归一键会把它们判成穿两源的锚): %s——归一(只留字母数字并小写)后两源都现, '
    u'逐字复核对 %d 枚, 所以候选池里“穿两源”的 %d 条一条都不是真同现, 门槛里 x_verbatim = %d ⇎ x_normonly = %d 各占一键。 '
    u'关键串矩阵那 %d 枚用的是同一归一键, 两源同现 %d ⇎ 单源 %d(R 独占 %d, Z 独占 %d) ⇎ 不中 %d, 同现名单: %s。'
    % (FLAT[u'x_names'], FLAT[u'x_verbatim'], FLAT[u'pool_cross'], FLAT[u'x_verbatim'],
       FLAT[u'x_normonly'], FLAT[u'hitkinds'], FLAT[u'hitboth'], FLAT[u'hitsingle'],
       FLAT[u'hitR'], FLAT[u'hitZ'], FLAT[u'hitnone'], FLAT[u'bothw']))
add(u'- 锚的口径(与 B53/B54 不同, 必须单写): 两源都用原文件行判成员, 不设“去标签正文”这一层——'
    u"注册表 0 枚 '<' 也 0 枚制表符, 时区表的 3 枚 '<' 全住在注释写的 '<tab>' 记法里, 若去掉注释行, "
    u"'#@' 那 %d 行与它声明的规则一起消失, 而“注释自写规则 ⇎ 数据核对”正是本条的一条主轴。"
    u'候选池 %d 条(R %d ⇎ Z 片段 %d)是按“去掉首尾空白且不含制表符、长度≥12”现建的, 抽 code 侧另建一套同样规则的池, 两边条数相同(%d)。'
    % (FLAT[u'z_at'], FLAT[u'pool_n'], FLAT[u'poolR'], FLAT[u'poolZ'], A[u'pool_n']))
SH = []
for t in sorted(SRCALL):
    if t == u'B55':
        continue
    for si, p in enumerate(SRCALL[t]):
        for src_i, srcp in enumerate(PATHS):
            if p == srcp:
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
    u'共用的是同一句原文而不是同一个论断: 本条量段结构、值域两种判法与时区表自写规则的核对, '
    u'B45 量同一个名字的三种对象, B49 量检查这张表的 awk, B52 量时效分区, B10 量版本账, B09 只量单源里的记法。'
    u'反过来 langsubtag.txt 那一份此前只在 B09 被单源用过, 本条把它与 zone1970.tab 配成对照, 才第一次量到“借码”这一层。'
    % (len(SH), u' ／ '.join(u'%s(源%s, 锚%d, 交%d)' % x for x in SH), MX))
add(u'- 不可核清单(库里无相应字节, 写成判词即越界): 这些值域约束在 RFC 5646 正文里如何表述(库里只有注册表本身); '
    u'zone1970.tab 的三条自写规则是否由上游 checktab.awk 校验(该文件在库, 但它对本表校的不是这三条); '
    u'区间码 QM..QZ ⇎ XA..XZ 的名义归属是“保留”还是“私用”(文件只给码与 Description); '
    u'%d 处 Preferred-Value 指向已弃码是注册表的已知遗留还是有意为之; 下一版注册表会不会改动那 %d 枚越界复合标签。'
    % (FLAT[u'pref_dep'], FLAT[u'viol_whole']))

body = NL.join(NT)
T = io.open(ENTRY, encoding='utf-8').read()
head = u'## ⛓解读注'
i = T.index(head)
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(
    T[:i] + head + NL + NL + body + NL)
print(u'注已写: %d 行 ｜ 契约 %d 键全对齐 ｜ 共用源 %d 处(锚集交集 %s) ｜ mtime 与内容日期差 %+.2f ⇎ %+.2f 天(只在本机)' % (
    len(NT), len(FLAT), len(SH), [x[3] for x in SH], -DAYS[0], -DAYS[1]))
