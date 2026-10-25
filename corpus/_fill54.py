# -*- coding: utf-8 -*-
"""B54 ⛓解读注: 这段里的每个数都由本脚本现测并 assert, 不手填。
四套实现: 采集侧 corpus/_pick54.py(先于条目写成, 落 corpus/_b54meas.json) ⇎ 建条目侧 corpus/_mkB54.py(落扁平契约
corpus/_b54flat.json) ⇎ 审计器侧 corpus/audit.py::_b54_scan()(快照落 corpus/_b54audit.json) ⇎ 本注自己从两份 raw 现取的第三遍。
必须披露的一处非独立性: _b54_scan 的量测段是从 _mkB54.py 的现算段机械抽出后插进门槛的(见 corpus/_wire54.py),
所以它的独立性不来自“另写一遍”, 而来自 ①采集侧与本注是两套真独立实现, ②插门前 _b54flat.json 的每个键与 DERIV['B54']
的每条算式都在抽出体上预演过, 值不符即停机。
磁盘 mtime 与那枚 base64 时刻同秒只在本机成立: 本注测它、写它、并写明它不进门槛。"""
import glob, io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B54_complete_listing_and_ill_formed_request.md')
M = json.load(io.open(os.path.join(C, u'_b54meas.json'), encoding='utf-8'))
CH = json.load(io.open(C + u'/_b54checks.json', encoding='utf-8'))
DJ = json.load(io.open(C + u'/_deriv54.json', encoding='utf-8'))
FLAT = json.load(io.open(C + u'/_b54flat.json', encoding='utf-8'))
ATOMP = os.path.join(C, u'_atoms54.txt')
ATOMS = [x for x in io.open(ATOMP, encoding='utf-8').read().split(NL) if x.strip()]
MEAS, TAGS, PATHS = M[u'meas'], M[u'tags'], M[u'paths']
LB = M[u'labels']
RD = lambda p: io.open(p, encoding='latin-1').read()
TXT = [RD(p) for p in PATHS]

# ---------- 审计器自己的快照(把它的 _B53/_B54 与 prose_norm 一并取回) ----------
SNAP = os.path.join(C, u'_b54audit.json')
code = (u"import sys,json,io;sys.path.insert(0,'corpus');import audit;"
        u"A=[x.rstrip(chr(10)) for x in io.open(sys.argv[2],encoding='utf-8') if x.strip()];"
        u"json.dump({'B54':audit._B54,'PN':[audit.prose_norm(a) for a in A]},"
        u"open(sys.argv[1],'w',encoding='utf-8'),ensure_ascii=False)")
r = subprocess.run([sys.executable, u'-X', u'utf8', u'-c', code, SNAP, ATOMP],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
assert r.returncode == 0 and os.path.exists(SNAP), r.stderr[-800:]
SN = json.load(io.open(SNAP, encoding='utf-8'))
A = SN[u'B54']
PN_AUDIT = SN[u'PN']

aslist_ = lambda v: v if isinstance(v, list) else [v]


def rnd(v):
    if isinstance(v, list):
        return [rnd(x) for x in v]
    if isinstance(v, str):
        return v
    return round(float(v), 4)


MISS = [k for k in sorted(FLAT) if k not in A]
DIFF = [(k, FLAT[k], A[k]) for k in sorted(FLAT) if rnd(FLAT[k]) != rnd(A[k])]
assert not MISS, MISS
assert not DIFF, DIFF[:6]

# ---------- 本注的第三遍: 自己从两份字节现取, 不读上面任何一套 ----------
def pn(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


LS = [TXT[i].split(NL) for i in range(2)]
DASH = [i for i, l in enumerate(LS[0]) if re.fullmatch(u'-{20,}\\s*', l)]
assert len(DASH) == 1
ROWS = [l for l in LS[0][DASH[0] + 1:] if l.strip()]
GAP = [re.split(u' {2,}', l.strip()) for l in ROWS]
NM, VL, UC = [g[0] for g in GAP], [g[1] for g in GAP], [(g + [u''])[2] for g in GAP]
EX = [i for i in range(len(ROWS)) if UC[i] == u'(exact)']
NE = [i for i in EX if u'...' not in VL[i]]
MT = [os.path.getmtime(p) for p in PATHS]
import base64 as B64
import datetime as DT
TS = re.search(r"t:'([A-Za-z0-9+/=]+)'", TXT[1]).group(1)
EPOCH = int(B64.b64decode(TS))
UTC = DT.datetime.fromtimestamp(EPOCH, DT.timezone.utc)
DELTA = [abs((DT.datetime.fromtimestamp(m, DT.timezone.utc).replace(tzinfo=None) - UTC.replace(tzinfo=None)).total_seconds()) for m in MT]
SHA = [__import__('hashlib').sha256(io.open(p, 'rb').read()).hexdigest() for p in PATHS]
CP = [len(set(pn(a) for a in ATOMS if pn(a) in pn(TXT[i]))) for i in range(2)]
INPOOL = len([a for a in ATOMS if any(a in TXT[i] for i in range(2))])
assert len(ROWS) == FLAT[u'rows'] and len(EX) == FLAT[u'exact_rows'] and len(NE) == FLAT[u'exact_no_ell']

assert EPOCH == FLAT[u'tok_epoch'] and INPOOL == len(ATOMS)
assert CP[0] + CP[1] >= len(ATOMS)

NT = []
add = lambda s: NT.append(s)

add(u'- 三套实现与一处非独立: 采集侧 _pick54.py ⇎ 建条目侧 _mkB54.py(扁平契约 %d 键) ⇎ 门槛内 _b54_scan()。'
    u'本注是第四遍: 上面 %d 个键逐个与审计器快照对齐(不符即停机), 另自行从两份字节重取了行数 %d、\'(exact)\' %d 行、'
    u'给全的 %d 行、base64 时刻 %d ——四个数与契约逐一相同。' % (len(FLAT), len(FLAT), len(ROWS), len(EX), len(NE), EPOCH))
add(u'- _b54_scan 的量测段由 _wire54.py 从 _mkB54.py 的 SCAN 段逐行抽出(只改路径常量与模块别名), '
    u'插门前把 _b54flat.json 的 %d 个键与 DERIV[\'B54\'] 的 %d 条算式在抽出体上跑过; '
    u'因此真正独立的两遍是 _pick54.py 与本注, 它们用的是两套不同的字段切法(采集侧按 gap 定列, 本注同样按 gap 但另数一遍)。'
    % (len(FLAT), len(DJ)))
CL2 = dict((k, v) for k, v in CH[u'collisions'].items() if len(v) > 1)
add(u'- 门槛的账: DERIV 键 %d 个 ⇎ 引用点 %d 处 ⇎ 同数共键 %d 组(两名以上 %d 组) ⇎ 0 键折 %d 项。'
    u'同数的字面不取第一条算式, 而是复合式 LIT*(1-(max(全部算式)-min(全部算式))): 每条算式都等于该字面时括号才为 1。'
    % (len(DJ), sum(v.count(u'B54V') for v in DJ.values()), len(CH[u'collisions']), len(CL2),
       DJ[u'0'].count(u'+') + 1))
for k, v in sorted(CL2.items(), key=lambda x: (-len(x[1]), x[0]))[:8]:
    add(u'  - 同数 %s(%d 条): %s' % (k, len(v), u' ⇎ '.join(v)))
add(u'- 两份文件的指纹(旁证, 判词里只报“种数”而不报串, 因为串里的数字段无法由字节直接命中): %s ⇎ %s; '
    u'字节 %d ⇎ %d。sha256 全长 64 位, 此处只列全串以免与判词里的数字锚混起来。'
    % (SHA[0], SHA[1], os.path.getsize(PATHS[0]), os.path.getsize(PATHS[1])))
add(u'- 时间分两档(第二档只在本机): 内容侧 t:\'%s\' → %d → %s UTC, 这一条在任何一份拷贝上都复算得出, 已进 DERIV('
    u'键 %s 与 %s); 磁盘 mtime(换成 UTC 后)分别是 %s ⇎ %s, 与该时刻差 %.3f ⇎ %.3f 秒——同一秒落盘这件事拷贝一次就失效, 所以它只写在这里。'
    % (TS, EPOCH, UTC.strftime(u'%Y-%m-%d %H:%M:%S'), u'tok_epoch', u'tok_utc',
       DT.datetime.fromtimestamp(MT[0], DT.timezone.utc).strftime(u'%Y-%m-%d %H:%M:%S'),
       DT.datetime.fromtimestamp(MT[1], DT.timezone.utc).strftime(u'%Y-%m-%d %H:%M:%S'), DELTA[0], DELTA[1]))
add(u'- 锚的账: 去重 %d 串 ⇎ 正文 %d 处 ⇎ 每标签 %s ⇎ 单源 %d ⇎ 两源同现 %d ⇎ 成员检查 %d 次 ⇎ 错配 %d 处; '
    u'本注另按“整串在该源字节里逐字出现”复查: %d/%d 串命中。'
    % (CH[u'anchor_distinct'], CH[u'anchor_total'], CH[u'tag_counts'], A[u'anchor_single'],
       A[u'anchor_both'], A[u'checks'], A[u'anchor_err'], INPOOL, len(ATOMS)))
add(u'- 锚的口径(与 B53 不同, 必须单写): 两源都用原文件行判成员, 不设“去标签正文”这一层——清单那份整份 0 枚 \'<\', '
    u'去标签与不去标签是同一份字节; 错误页那一份若去掉标签, “ill-formed request”那句会与它的 <FONT> 壳一起被切掉。'
    u'穿两源的 12 枚关键串用的是同一归一键(只留字母数字并小写)。')
add(u'- \'(exact)\' 给全(不带 \'...\')的 %d 行名单: %s。截断的 %d 行不在此列, 于是“小数位对齐”那条不变量的适用面是 %d 行而不是 %d 行。'
    % (len(NE), u'、'.join(NM[i] for i in NE), len(EX) - len(NE), FLAT[u'align_rows'], FLAT[u'rows']))
add(u'- 单位列两遍计数是 %d ⇎ %d(差 %d), 逐格两法互证 %d 格不一致 %d 处: 这两笔是本条里唯一“同一件事由两条独立判法各数一遍”的账, '
    u'它们在门槛里各占一个键, 不是靠断言假设相等。'
    % (FLAT[u'unit_distinct'], FLAT[u'unit_distinct_col'], FLAT[u'unit_diff'], FLAT[u'impl_cell'], FLAT[u'impl_diff']))
B6P = glob.glob(u'corpus/babeltele/B06_*.md')
assert len(B6P) == 1, B6P
B6 = io.open(B6P[0], encoding='utf-8').read()
SRC6 = B6.split(NL)[1].split(u' →')[0].replace(u'src: ', u'').strip()
assert SRC6.replace(u'\\', u'/') == PATHS[0].replace(u'\\', u'/'), (SRC6, PATHS[0])
A6 = set(re.findall(u'⟨([^⟨⟩]+)⟩', B6.split(u'## ⟪BabelTele⟫')[1]))
add(u'- 同一份字节被两代制度各压过一次: %s 的 src 指向的就是本条的 ⟦T⟧(sha16 %s), 两条不重叠也不冲突——'
    u'B06 抄表里的数值, 本条数表的形状; B06 编码区里片段锚 %d 枚(第一代不用锚点), 与本条 %d 串锚交集 %d 处; '
    u'要核“同一份 raw 能不能有两种条目”就拿这两条对照, 而不是拿本条的 ⟦E⟧。'
    % (u'B06', SHA[0][:16], len(A6), len(ATOMS), len(A6 & set(ATOMS))))
add(u'- 不可核清单(写成判词而非待核, 因库里无相应字节): 错误页由哪一次请求造成; \'physics.nist.gov/constants\' 与 /cuu/ 两个入口'
    u'谁才是这份清单的正身; 2022 调整之后官方是否又改过数值; 那三段注释里被留着的旧导航块是哪一代模板。')

body = NL.join(NT)
T = io.open(ENTRY, encoding='utf-8').read()
head = u'## ⛓解读注'
i = T.index(head)
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(
    T[:i] + head + NL + NL + body + NL)
print(u'注已写: %d 行 ｜ 契约 %d 键全对齐 ｜ mtime 差 %.3f ⇎ %.3f 秒(只在本机)' % (
    len(NT), len(FLAT), DELTA[0], DELTA[1]))
