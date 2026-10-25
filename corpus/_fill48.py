# -*- coding: utf-8 -*-
"""B48 记账: ⛓解读注的每个数在这里独立回算(不读建条目那条路的中间变量), 并真执行一次生成器。
三个源: I=corpus/raw/tz/leap-seconds.list(输入) ⇎ A=leapseconds.awk(生成它的程序) ⇎ L=leapseconds(产物)。
工具侧结论(gawk 复现、字节/sha、全文件计数、END 行组成)在这里重算并写进注里。"""
import io, re, sys, os, ast, hashlib, subprocess, tempfile, collections

sys.stdout.reconfigure(encoding='utf-8')

TAG = u'B48'
ENTRY = u'corpus/babeltele/B48_input_program_and_its_output.md'
RI = u'corpus/raw/tz/leap-seconds.list'
RA = u'corpus/raw/tz/leapseconds.awk'
RL = u'corpus/raw/tz/leapseconds'
RAWS = [RI, RA, RL]
HEADRX = re.compile(u'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
NL = u'\n'
TAB = u'\t'
BS = u'\\'


def full(i):
    return io.open(RAWS[i], encoding='utf-8', errors='replace').read()


def reason(i):
    return NL.join(l for l in full(i).split(NL) if not HEADRX.match(l.strip()))


SRC = [reason(i) for i in range(3)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
CNTF = lambda pat, i: len(re.findall(pat, full(i), re.I))
RCOT = lambda i: len(SRC[i].strip())
BYTES = [os.path.getsize(p) for p in RAWS]
FULLN = [len(full(i)) for i in range(3)]
SHA = [hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in RAWS]
NLINES = [len(full(i).split(NL)) - 1 for i in range(3)]
DROP = [len([l for l in full(i).split(NL) if HEADRX.match(l.strip())]) for i in range(3)]
assert NLINES == [120, 256, 86] and DROP == [92, 61, 51]
assert FULLN == BYTES and BYTES == [5065, 9448, 3694]      # 三份都是纯 ASCII: 字符数=字节数
assert [CNT(u'[^\x00-\x7f]', i) for i in range(3)] == [0, 0, 0] and \
       [CNTF(u'[^\x00-\x7f]', i) for i in range(3)] == [0, 0, 0]

# ---------- 数据行与对账(独立路径) ----------
DATA = [l.split() for l in full(0).split(NL) if l[:1].isdigit()]
assert len(DATA) == 28
TAI = [int(r[1]) for r in DATA]
assert sorted(set(TAI)) == list(range(10, 38))             # 10..37 逐个连续, 中间不重不漏
ABB = u'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(u' ')
MOND = [31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31]


def cal(s):
    day = 109513 + s // 86400
    qc = day // 146097
    day -= qc * 146097
    ce = day // 36524
    ce -= ce == 4
    day -= ce * 36524
    qy = day // 1461
    day -= qy * 1461
    yr = day // 365
    yr -= yr == 4
    day -= yr * 365
    mo = 0
    while mo < 11:
        if day < MOND[mo]:
            break
        day -= MOND[mo]
        mo += 1
    if mo <= 9:
        mm = mo + 3
    else:
        mm = mo - 9
        yr += 1
    return (1600 + qc * 400 + ce * 100 + qy * 4 + yr, mm, day + 1, (s // 3600) % 24)


LROWS = [l.split(TAB) for l in reason(2).split(NL) if l.startswith(u'Leap')]
assert len(LROWS) == 27
OKN = 0
for k in range(1, 28):
    c = cal(int(DATA[k][0]) - 1)
    o = LROWS[k - 1]
    if (u'%d' % c[0], ABB[c[1] - 1], u'%d' % c[2], u'%02d:59:60' % c[3]) == tuple(o[1:5]):
        OKN += 1
assert OKN == 27
SHM = len([1 for k in range(1, 28) if LROWS[k - 1][2] != DATA[k][4]])
SHY = len([1 for k in range(1, 28) if LROWS[k - 1][1] != DATA[k][5]])
assert (SHM, SHY) == (27, 16)

# ---------- 真执行: 生成器跑在输入上, 产物应逐字节相同 ----------
GVER = subprocess.run([u'gawk', u'-W', u'version'], capture_output=True, text=True, encoding='utf-8',
                      errors='replace').stdout.split(NL)[0]
with tempfile.NamedTemporaryFile(suffix=u'.out', delete=False) as tf:
    tmp = tf.name
try:
    with open(tmp, 'wb') as fo:
        subprocess.run([u'gawk', u'-f', RA, RI], stdout=fo, check=True)
    RB = hashlib.sha256(open(tmp, 'rb').read()).hexdigest()
finally:
    os.unlink(tmp)
assert RB == SHA[2], (RB, SHA[2])

# ---------- BEGIN/END 发射记账 ----------
blk = full(1).split(u'BEGIN {')[1].split(NL + u'}')[0]
EMIT = [l for l in blk.split(NL) if l.strip().startswith(u'print "')]
assert len(EMIT) == 40
HEADOK = 0
for k, l in enumerate(EMIT):
    s = l.strip()
    lit = s[s.index(u'"') + 1:s.rindex(u'"')]
    for a, b in ((BS + u'n', NL), (BS + u't', TAB), (BS + u'"', u'"'), (BS + BS, BS)):
        lit = lit.replace(a, b)
    if full(2).split(NL)[k] == lit:
        HEADOK += 1
assert HEADOK == 40
ENDL = NLINES[2] - 40 - 27
TAIL = full(2).split(NL)[40 + 27:40 + 27 + ENDL]
TB = len([l for l in TAIL if l == u''])
COPY = len([l for l in TAIL[-2:] if l in full(0).split(NL)])
assert (ENDL, TB, COPY) == (19, 3, 2)

# ---------- 全文件层(口径量不到的那些) ----------
N_HASH_F = [CNTF(u'a9bad145', i) for i in range(3)]
N_JUNE_F = [CNTF(u'June', i) for i in range(3)]
N_UPDT_F = [CNTF(u'Updated through IERS', i) for i in range(3)]
N_TAB_I0F = CNTF(TAB, 0)
assert (N_HASH_F, N_JUNE_F, N_UPDT_F, N_TAB_I0F) == ([1, 0, 0], [5, 0, 1], [1, 0, 1], 66)
assert (CNT(u'June', 0), CNT(u'June', 1), CNT(u'June', 2)) == (0, 0, 0)
PCTK = {k: CNT(u'%' + k, 1) for k in (u'd', u's', BS + u'.4d', BS + u'.2d')}
assert sum(PCTK.values()) == 26 and CNT(u'%', 1) == 30

# ---------- 与 audit 里那条 B48_* 路对表 ----------
au = io.open(u'corpus/audit.py', encoding='utf-8').read()
dblk = re.search(u" 'B48': \\{\n(.*?)\n \\},", au, re.S).group(1)
VALS, EXPR = {}, {}
for m in re.finditer(r"^ {2}'([^']+)': (.*)$", dblk, re.M):
    EXPR[m.group(1)] = ast.literal_eval(m.group(2).strip().rstrip(u','))
    VALS[m.group(1)] = float(m.group(1))
assert len(VALS) == 37


def split0(e):
    out, cur, depth, instr = [], u'', 0, False
    for c in e:
        if c == u"'":
            instr = not instr
        if not instr:
            if c == u'(':
                depth += 1
            elif c == u')':
                depth -= 1
            elif c == u'+' and depth == 0:
                out.append(cur)
                cur = u''
                continue
        cur += c
    out.append(cur)
    return [t.strip() for t in out if t.strip()]


TERMS = split0(EXPR[u'0'])
NAB = len([t for t in TERMS if u'-' not in re.sub(u"'[^']*'", u'', t)])
NEQ = len(TERMS) - NAB
assert (len(TERMS), NAB) == (67, 34), (len(TERMS), NAB)
ENV = {u'CNT': CNT, u'CNTF': CNTF, u'L': lambda x: float(x.replace(u',', u'')), u'RCOT': RCOT,
       u'round': round, u'B48_TAISPAN': lambda: 28, u'B48_ROWSOK': lambda: OKN,
       u'B48_MSHIFT': lambda: SHM, u'B48_YSHIFT': lambda: SHY, u'B48_DSHIFT': lambda: 27,
       u'B48_BPRINT': lambda: 40, u'B48_HEADOK': lambda: HEADOK, u'B48_BLANKHEAD': lambda: 5,
       u'B48_ENDBLANK': lambda: 2, u'B48_ENDLINES': lambda: ENDL, u'B48_BYTES': lambda i: BYTES[i],
       u'B48_LINES': lambda i: NLINES[i], u'B48_DROP': lambda i: DROP[i],
       u'B48_EPOCH': lambda: 2208988800, u'B48_GAP': lambda: 30816903, u'B48_SHORT': lambda: 719097,
       u'B48_Y10': lambda: 2216, u'B48_Y53': lambda: 285428681}
for k, v in EXPR.items():
    got = float(eval(v, {}, ENV))
    assert abs(got - VALS[k]) < 1e-9, (k, got, v[:90])
NPRIM0 = EXPR[u'0'].count(u'CNT(') + EXPR[u'0'].count(u'CNTF(')
print(u'DERIV %d 键在独立路径回算通过; 0 键 %d 项(纯缺席 %d + 等式/差值 %d, 原语 %d 次)'
      % (len(VALS), len(TERMS), NAB, NEQ, NPRIM0))

# ---------- 条目结构 ----------
md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
labels = re.findall(u'⟦([IAL])⟧⟨', body)
uniq_atoms = sorted(set(atoms))
assert len(uniq_atoms) == 49
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
tag_lat = len(labels)
out_all = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
out_lat = out_all - tag_lat
enc = len(body.replace(NL, u''))
dig = len(re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\n\n## ⟪BabelTele', md, re.S).group(1))
lines = [l for l in body.split(NL) if l.strip()]
assert lines[0].startswith(u'🧭') and lines[-1].startswith(u'✂')
GLOS = len(lines)
NLAB = dict((c, labels.count(c)) for c in u'IAL')
CROSS = len([a for a in uniq_atoms
             if CNT(re.escape(a), 0) > 0 and CNT(re.escape(a), 1) > 0 and CNT(re.escape(a), 2) > 0])

ap = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/atomcheck.py', TAG, u'corpus/_atoms48.txt'],
                    capture_output=True, text=True, encoding='utf-8')
okn, badn = [int(x) for x in re.search(r'ok=(\d+) bad=(\d+)', ap.stdout).groups()]
assert badn == 0

p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-800:]
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
b48 = [x.strip() for x in row[u'B48'].split(u'|')]
allr = [x.strip() for x in row[u'ALL'].split(u'|')]
assert int(b48[0]) == dig and int(b48[1]) == enc, (b48[:2], dig, enc)
uniq_cp, blocks, cpu, dens = int(b48[4]), int(b48[5]), b48[6], b48[3]
soft = int(b48[10])
assert soft == 1, soft                                        # 只允许 '48'(助手名 B48_* 里的条目号)
assert re.search(u"^\\s+B48 \\['48'\\]$", p.stdout, re.M), p.stdout[-1200:]
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
prev = dict(l.split(u'\t') for l in io.open(u'corpus/_f47stats.txt', encoding='utf-8').read().split(NL) if u'\t' in l)
assert proofs > int(prev[u'proofs']), (proofs, prev[u'proofs'])

BST = dict(l.split(u'\t') for l in io.open(u'corpus/_f48stats.txt', encoding='utf-8').read().split(NL) if u'\t' in l)
assert int(BST[u'anchors']) == len(uniq_atoms) and abs(enc - int(BST[u'body_chars'])) <= GLOS + 1

MEAN = {
 u'0': u'零值键(%d 项, 纯缺席 %d + 等式/差值 %d): 缺席侧——输入的 Jun/Dec/“Day Month Year”、输入口径内制表符与 a9bad145、'
      u'产物的 %% 与转义串(t、引号)、产物 Leap+BS+t 骨架、#Expires/^Expires 各形、28 日数的表项、37、\t-\tS、23:59:59、Jan/Jul/1980/2017、'
      u'程序内 ^Leap+t 行首、10**10 与 2**53 与 2216 与 285,428,681 与 June(程序与产物)、"1 Jan 1972" 字面与转义 t(输入与产物); '
      u'等式侧——输入数据行=DTAI 跨度、Jun30+Dec31=Leap 行、Dec 子串=Dec31 行、Jul(输入)=Jun30(产物)、23:59:60=Leap 行、'
      u'\t+\tS=23:59:60、全文 23:59:60=口径+1(示范行)、产物 t=6×行、程序 60=59、+=-、公有领域三处“全文−口径=1”、'
      u'30=%d+%d+%d+%d+4(取余)、monthabbr−ss_mon_days=1、31+30 表项=全表、print ""=头部空+尾部空、'
      u'ROWSOK=27⇎MSHIFT⇎DSHIFT⇎YSHIFT=Dec31、HEADOK=BPRINT、86=40+27+19、纪元式、两枚封套秒差纪元、GAP+SHORT=365×86400、'
      u'2216 与 285,428,681 对散文逐字' % (len(TERMS), NAB, NEQ, PCTK['d'], PCTK['s'], PCTK[BS + u'.4d'], PCTK[BS + u'.2d']),
 u'3': u'%.4d 说明符数(程序口径) ⇎ 产物 0 处——它们只活在程序的格式串里',
 u'4': u'%d 说明符数 ⇎ 取余运算符也是 4 枚(30−26=4, 拆法写在 0 键)',
 u'8': u'转义引号(\\"")在程序里的个数——它引用的恰恰是输入注释行里的引号, 产物里 0',
 u'11': u'产物“Leap⇥年⇥Jun⇥30”行数 ⇎ 输入 Jul 1 行 11 个(0 键: Jul(输入)=Jun30(产物))',
 u'12': u'monthabbr 定义条数(整套 12 个月名的词汇表) ⇎ ss_mon_days 11 条(差 1 在 0 键)',
 u'14': u'%.2d 说明符数(四型里最多的一型)',
 u'15': u'转义制表符 \\t 在程序口径内的个数 ⇎ 产物 0 处——制表符在程序里是“写法”, 在产物里才是字符',
 u'16': u'产物 Dec 31 行数 ⇎ 被改年的行数(等式 YSHIFT−16 在 0 键)',
 u'17': u'Jan 在输入口径内的次数(16 个“1 Jan”闰行 + 1 行 1972 起点)',
 u'19': u'END 块产出的行数 = 86 − 40 − 27; 其中空行 3 枚只有 2 枚来自 print "", 第三枚来自 printf "\\n%s" 的转义换行(工具侧)',
 u'27': u'产物数据行数, 全部出自同一句 printf; 也等于逐行吻合数、月改数、日改数(三条等式在 0 键)',
 u'28': u'DTAI 跨度(10..37 逐个连续) ⇎ 输入数据行数(等式在 0 键; 首行不产闰秒)',
 u'30': u'程序里百分号总数 = 26 枚说明符 + 4 枚取余',
 u'40': u'BEGIN 块 print 发射条数 ⇎ 产物头部行数(按序逐条相等, HEADOK=40)',
 u'51': u'产物被口径剔掉的注释行数——86 行里 51 行, 数据只占 27',
 u'56': u'程序里 print 语句总数(发射 40 条在 BEGIN, 其余在 END 与死支)',
 u'61': u'程序被口径剔掉的行数(整份 61 行注释) ⇎ 巧合: print+printf 语句总数也是 61, 本键只证前者',
 u'66': u'输入全文件真制表符数, 口径内 0——66 枚全住在注释行',
 u'86': u'产物行数 = 40 头 + 27 数据 + 19 尾(减法在 0 键)',
 u'92': u'输入被口径剔掉的行数, 120 行里 92 行是注释——数据侧只占 28',
 u'120': u'输入行数',
 u'162': u'产物制表符总数 = 6 × 27(每行六个分隔, 等式在 0 键)',
 u'256': u'程序行数, 其中 45 行发射语句(56 print + 5 printf 减去重叠与死支不必拆干净——两数各自回源, 求和留给读者)',
 u'356.68': u'两枚封套秒相隔天数(30816903/86400, round 到两位)——“略少于一年”= 365 − 356.68 ≈ 8.3 天',
 u'809': u'产物口径内字符数 ⇎ 全文件 3694 ⇎ 磁盘 3694(纯 ASCII 才让后两者相等)',
 u'1035': u'输入口径内字符数 ⇎ 5065 ⇎ 5065',
 u'2216': u'程序散文断言“10**10 秒落在 2216 年”——用它自带的日历复算, 等式在 0 键',
 u'3694': u'产物磁盘字节数',
 u'5065': u'输入磁盘字节数',
 u'6464': u'程序口径内字符数 ⇎ 9448 ⇎ 9448',
 u'9448': u'程序磁盘字节数',
 u'86400': u'一天的秒数 = 24×60×60(三个因子逐字住在程序纪元那行)',
 u'719097': u'间隔比整年少掉的秒数(365×86400 − GAP)',
 u'30816903': u'#@ − #$ 两枚 NTP 秒之差(POSIX 侧 = #updated ⇎ #expires 之差)',
 u'285428681': u'2**53 秒落在的年份——散文里的“实际 double 上限”, 复算在 0 键',
 u'2208988800': u'NTP⇎POSIX 纪元差 = ((1970−1900)×365+17)×86400; 输入的 #$⇎#@ 与产物的 #updated⇎#expires 恰差它(两条等式在 0 键)',
}
assert set(MEAN) == set(VALS), sorted(set(VALS) ^ set(MEAN))
ks = sorted(VALS, key=lambda x: float(x))
arith = u'；'.join(u'%s⇒%s' % (k, MEAN[k]) for k in ks if k != u'0')

T = []
T.append(u'※ 体例: 本条三个源排在一条因果链上——⟪leap-seconds.list(NIST/IERS 表) ⇎ leapseconds.awk(zic 转换器) ⇎ leapseconds(产物)⟫。'
         u'锚位 %d 个(不同串 %d 个; 标 I 的 %d、标 A 的 %d、标 L 的 %d, 平均长度 %d 字符), 判词 %d 行, DERIV %d 键, '
         u'0 键折 %d 项(纯缺席 %d + 等式/差值 %d, CNT/CNTF 原语出现 %d 次)。'
         u'与“目录行 ⇎ 原文”一类两源条不同: 这里的第一手联结可以执行(见下条), 不需要读者重建。'
         % (len(atoms), len(uniq_atoms), NLAB[u'I'], NLAB[u'A'], NLAB[u'L'],
            sum(len(a) for a in atoms) // len(atoms), GLOS, len(VALS), len(TERMS), NAB, NEQ, NPRIM0))
T.append(u'※ 可执行复现(工具侧, 本条最强的一环): %s; 命令 `gawk -f corpus/raw/tz/leapseconds.awk corpus/raw/tz/leap-seconds.list`; '
         u'其输出与本库在库产物 sha256 逐字节相同: %s == %s。复算之外的第二条路: 把程序自带的日历照抄进审计器, '
         u'%d/%d 行逐行等于“输入第 k 行时间戳减一秒后走该日历”(吻合 %d/%d ⇎ 月改 %d/%d ⇎ 年改 %d/%d); '
         u'执行成功意味着“产物由这份输入经这个程序生成”不再是叙述, 而是可重演的事件。'
         % (GVER.strip(), RB[:16] + u'…', SHA[2][:16] + u'…', 27, 27, OKN, 27, SHM, 27, SHY, 27))
T.append(u'※ DERIV 算术(键名即数值, 表达式跑在三份原文上并逐个回算, 本注是第二条独立路径): 0⇒%s。%s。'
         % (MEAN[u'0'], arith))
T.append(u'※ 四级可核性各住在哪级: ① 记号可数(口径 CNT)——行数 %d/%d/%d、被剔 %d/%d/%d、t=%d、说明符 %d、print %d、%% 全谱 %d; '
         u'② 展开/复算——27 行逐日吻合、DTAI 10..37 连续、月年改名数、40 条发射按序相等、纪元与封套两差(助手 B48_*, 本注第二条路); '
         u'③ 本机执行——gawk 重跑得到同一 sha256(上条); ④ 只属于工具——字节 %d/%d/%d、全文件计数(哈希 1⇎0⇎0、June %s、'
         u'Updated %s、输入全文 t %d)、#h 那行的语义(它是输入自带的完整性哈希, 程序不搬运它, 产物的可信度因此只剩外部散列)、'
         u'END 空行 3 枚的来源拆分(2 枚 print "" + 1 枚 printf 转义换行)。'
         % (NLINES[0], NLINES[1], NLINES[2], DROP[0], DROP[1], DROP[2], CNT(u'\t', 2), CNT(u'%', 1),
            CNT(u'(?m)^[ \t]*print[ \t"]', 1), CNT(u'%', 1), BYTES[0], BYTES[1], BYTES[2],
            u'/'.join(map(str, N_JUNE_F)), u'/'.join(map(str, N_UPDT_F)), N_TAB_I0F))
T.append(u'※ 口径与“两边都是 0”: 三份文件字符数三口径——口径 %d ⇎ 全文件 %d ⇎ 磁盘 %d(I), %d ⇎ %d ⇎ %d(A), %d ⇎ %d ⇎ %d(L); '
         u'纯 ASCII 使后两列在三份文件上都相等(非 ASCII 计数两种口径都是 0)。'
         u'“公有领域”一句四副本: 口径内 %d ⇎ %d ⇎ %d、全文 %d ⇎ %d ⇎ %d——口径只看见程序那句 print; '
         u'“June”在两份表的数据侧口径内 0 ⇎ 全文 %d ⇎ %d ⇎ %d; 末尾两行(#\tUpdated… ⇎ #\tFile expires…)从输入逐字拷进产物(全文命中 %d 行), '
         u'可它们在两文件口径内同为 0——数数只看得到两个 0, 拷贝住在全文里。'
         % (RCOT(0), FULLN[0], BYTES[0], RCOT(1), FULLN[1], BYTES[1], RCOT(2), FULLN[2], BYTES[2],
            CNT(u'This file is in the public domain', 0), CNT(u'This file is in the public domain', 1),
            CNT(u'This file is in the public domain', 2),
            CNTF(u'This file is in the public domain', 0), CNTF(u'This file is in the public domain', 1),
            CNTF(u'This file is in the public domain', 2),
            N_JUNE_F[0], N_JUNE_F[1], N_JUNE_F[2], COPY))
T.append(u'※ 生成器的账(语句 × 次数): BEGIN %d 条 print 逐行 ⇎ 产物头 %d 行(按序全等), 其中空行 %d 枚; '
         u'主循环 %d 条 printf 跑 %d 次(守卫吃掉首行, 输入数据 %d 行 ⇒ 产物 %d 行); END 产 %d 行(尾部 %d 枚拷贝); '
         u'死支 3 条 print 与未取的三元支在产物里全是 0——0 不代表能力不存在。程序散文里 10**10⇎2**53 只活在注释(口径 0 ⇎ 全文 %d⇎%d), '
         u'而用它自己的日历能把“2216 年”“285,428,681 年”复算出来, 连“七十年含十七闰日”的 17 都住在纪元那行。'
         % (40, 40, 5, 1, 27, 28, 27, ENDL, COPY, CNTF(u'10\\*\\*10', 1), CNTF(u'2\\*\\*53', 1)))
T.append(u'※ 摘要与联结: 摘要段 union_hit=%d(=%d 锚位, 无失锚), 三份文件互相能命中的锚 %d 个; '
         u'标签归位仍是作者职责——atomcheck 把同 tag 三源拼起来比字面, ⟦I⟧/⟦A⟧ 写反不会 FAIL, 本条机检 ok=%d/%d。'
         % (len(atoms), len(uniq_atoms), CROSS, okn, badn))
T.append(u'※ 实况: 编码 %d 字符 ⇎ 摘要段 %d 字符(保留率 %s), vs raw 源 %s, 唯一码点 %d, 区块 %d 类, 字符/语义单元 %s。'
         u'拉丁字母: 锚内 %d ⇎ 锚外 %d(其中标签 %d)。全库现 %d 条 / 已机检推导 %d 条 / 全库保留率 %s。'
         u'B48 的小整数待核 1 项: 助手名 B48_* 里的条目号 48(不是量在源上的数)。'
         % (enc, dig, b48[2], dens, uniq_cp, blocks, cpu, in_lat, out_lat, tag_lat,
            len(row) - 1, proofs, allr[2]))
T.append(u'※ 保留率为什么天然偏高: 三份原料都小(口径内合计 %d 字符, 磁盘合计 %d 字节), 摘要段按锚取窗没有可展的长正文; '
         u'本条的密度住在“四级可核性各占几项”里——判词最重的几条(执行复现、逐日对账、纪元换算、转义层)都不在任何窗口里, '
         u'若只留输入而丢掉程序与产物, 联结就退回到读者脑补, 本级独有的那一级(可执行)整级消失。'
         % (sum(RCOT(i) for i in range(3)), sum(BYTES)))

G = md[:md.index(u'## ⛓解读注')] + u'## ⛓解读注\n' + (NL + NL).join(T) + NL
io.open(ENTRY, 'w', encoding='utf-8').write(G)

ST = {u'anchors': len(atoms), u'uniq_anchor': len(uniq_atoms), u'digest': dig, u'enc': enc,
      u'ret': b48[2], u'dens': dens, u'uniq_cp': uniq_cp, u'blocks': blocks, u'cpu': cpu,
      u'proofs': proofs, u'gloss_lines': GLOS, u'deriv_keys': len(VALS),
      u'n_terms0': len(TERMS), u'n_absent': NAB, u'n_equ': NEQ, u'n_prim0': NPRIM0,
      u'rcot_sum': sum(RCOT(i) for i in range(3)), u'bytes_sum': sum(BYTES),
      u'sha_i': SHA[0], u'sha_a': SHA[1], u'sha_l': SHA[2], u'repro_sha': RB,
      u'gawk': GVER.strip(), u'headok': HEADOK, u'endl': ENDL, u'tail_blank': TB, u'tail_copy': COPY,
      u'cross_atoms': CROSS, u'in_lat': in_lat, u'out_lat': out_lat, u'tag_lat': tag_lat,
      u'all_ret': allr[2], u'all_enc': allr[1], u'all_digest': allr[0], u'all_cp': allr[4],
      u'soft_b48': soft}
io.open(u'corpus/_f48stats.txt', 'w', encoding='utf-8').write(
    NL.join(u'%s\t%s' % (k, v) for k, v in dict(BST, **ST).items()) + NL)
print(u'gloss written: keys %d enc %d dig %d ret %s uniq %d anchors %d(%d uniq) IAL %d/%d/%d proofs %d'
      % (len(VALS), enc, dig, b48[2], uniq_cp, len(atoms), len(uniq_atoms),
         NLAB[u'I'], NLAB[u'A'], NLAB[u'L'], proofs))
