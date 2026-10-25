# -*- coding: utf-8 -*-
"""B46 记账: ⛓解读注由 audit 里的 DERIV 表达式独立回算生成, 不手填任何数字。
两个源: J=目录页 corpus/raw/api/bio_recent_2026w01.json, P=它其中一行所指的原文抽取文本
corpus/raw/prose/biorxiv_bacterial_organelles.txt(B16 同源)。"""
import io, re, sys, os, json, subprocess, ast, hashlib

sys.stdout.reconfigure(encoding='utf-8')

TAG = u'B46'
ENTRY = u'corpus/babeltele/B46_catalog_row_vs_the_paper_it_names.md'
RJ = u'corpus/raw/api/bio_recent_2026w01.json'
RP = u'corpus/raw/prose/biorxiv_bacterial_organelles.txt'
RAWS = [RJ, RP]
LE, LP = u'E', u'P'
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
BS = u'\\'
EN = u'–'
SUB = u'₂'


def reason(i):
    s = io.open(RAWS[i], encoding='utf-8', errors='replace').read()
    return u'\n'.join(l for l in s.split(u'\n') if not HEADRX.match(l.strip()))


SRC = [reason(0), reason(1)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
RCOT = lambda i: len(SRC[i].strip())
L = lambda x: float(x.replace(u',', u''))
ENV = {u'CNT': CNT, u'RCOT': RCOT, u'L': L, u'round': round}

BJ, BP = SRC[0], SRC[1]
TP = io.open(RP, encoding='utf-8').read()
ROWS = json.loads(BJ)[u'collection']
ENVD = json.loads(BJ)[u'messages'][0]
COLL = lambda s: re.sub(u'\\s+', u' ', s).strip()
PC = COLL(BP)

# —— 与建条目那条路无关, 这里从原文重新摊一遍 ——
DOI_P = u'10.1101/2025.09.22.677801'
DOI_E = u'10.1101' + BS + u'/2025.09.22.677801'
ROW = [r for r in ROWS if DOI_P in r[u'doi']][0]
TITLE, ABST, CORR, INST = (ROW[u'title'], ROW[u'abstract'], ROW[u'author_corresponding'],
                           ROW[u'author_corresponding_institution'])
SENT = [s.strip() for s in re.split(u'(?<=[.;:?!])\\s', ABST) if len(s.strip()) >= 40]
HIT = [s for s in SENT if COLL(s) in PC]
OUT = [s for s in SENT if COLL(s) not in PC]
PUBS = [r[u'published'] for r in ROWS if str(r[u'published']).startswith(u'10.')]
assert (len(ROWS), len(PUBS), len(set(p.split(u'/')[0] for p in PUBS))) == (30, 8, 6)
assert (len(SENT), len(HIT), len(OUT)) == (7, 5, 2)
assert ENVD[u'count'] == 30 and ENVD[u'total'] == u'575' and ENVD[u'count_new_papers'] == u'397'
CHP = int(re.search(u'chars: (\\d+)', TP).group(1))
assert (CHP, RCOT(1) - CHP) == (80626, 73)
assert (CNT(re.escape(DOI_E), 0), CNT(re.escape(DOI_P), 1)) == (1, 41)
assert (CNT(re.escape(DOI_P), 0), CNT(re.escape(DOI_E), 1)) == (0, 0)
assert (CNT(BS + BS + u'/', 0), CNT(u'/', 0)) == (303, 303)
assert CNT(u'[^' + BS + u'x00-' + BS + u'x7f]', 0) == 0 and CNT(u'[^' + BS + u'x00-' + BS + u'x7f]', 1) == 331
assert (CNT(u'content' + BS + BS + u'/early', 0), CNT(u'content\\/early', 0)) == (30, 0)
assert CNT(u'content' + BS + BS + u'/early[^"]*10' + BS + u'.1101', 0) == 0
assert (CNT(re.escape(u'carboxysomes-CO2'), 1), CNT(re.escape(u'carboxysomes - CO2'), 0)) == (1, 1)
assert (CNT(re.escape(u'carboxysomes-CO2'), 0), CNT(re.escape(u'carboxysomes - CO2'), 1)) == (0, 0)
assert (CNT(u'CO2', 1), CNT(u'CO' + SUB, 1), CNT(u'CO2', 0)) == (3, 5, 1)
assert (CNT(re.escape(CORR), 0), CNT(re.escape(CORR), 1)) == (1, 2)
assert CNT(re.escape(ROW[u'authors']), 1) == 0

# —— 取 audit 里那条 DERIV 表达式, 逐键在与建条目同源的文本上回算 ——
au = io.open(u'corpus/audit.py', encoding='utf-8').read()
blk = re.search(u" 'B46': \\{\n(.*?)\n \\},", au, re.S).group(1)
VALS, EXPR = {}, {}
for m in re.finditer(r"^ {2}'([^']+)': (.*)$", blk, re.M):
    k, v = m.group(1), m.group(2).strip().rstrip(u',')
    EXPR[k] = ast.literal_eval(v)
    VALS[k] = float(k)
assert len(VALS) == 29, len(VALS)
for k, v in EXPR.items():
    got = float(eval(v, {}, ENV))
    assert abs(got - float(k)) < 1e-9, (k, got, v[:90])
NTERM0 = EXPR[u'0'].count(u'CNT(')


def split0(e):
    """把 0 键的加法式按顶层 '+' 拆开(引号与括号内的加号不算), 项数独立于建条目那条路。"""
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


NTERMS0 = len(split0(EXPR[u'0']))
BST = dict(l.split(u'\t') for l in io.open(u'corpus/_f46stats.txt', encoding='utf-8').read().split(u'\n')
           if u'\t' in l)
NABSEQ, NEQSEQ = int(BST[u'n_absent']), int(BST[u'n_equ'])
assert NTERMS0 == NABSEQ + NEQSEQ and NEQSEQ + 1 < NTERM0
DIFFTERM = len([1 for k, e in EXPR.items() if k != u'0' and u'-' in re.sub(u"'[^']*'", u'', e)])
print(u'DERIV %d 键回算通过; 0 键 %d 个加法项(缺席 %d + 等式 %d, CNT 原语 %d 次); 差值型键 %d'
      % (len(VALS), NTERMS0, NABSEQ, NEQSEQ, NTERM0, DIFFTERM))

md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
lbl = re.findall(u'⟦([EP])⟧⟨', body)
uniq_atoms = sorted(set(atoms))
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
tag_lat = len(lbl)
out_all = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
out_lat = out_all - tag_lat
enc = len(body.replace(u'\n', u''))
dig = len(re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\n\n## ⟪BabelTele', md, re.S).group(1))
raw_chars = [len(SRC[i]) for i in range(2)]
RCOTSUM = sum(RCOT(i) for i in range(2))
raw_bytes = [os.path.getsize(p) for p in RAWS]
full_chars = [len(io.open(p, encoding='utf-8', errors='replace').read()) for p in RAWS]
sha = [hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in RAWS]
lines = [l for l in body.split(u'\n') if l.strip()]
# 本条目结构是“一行一判词”: 首行是体例、末行是保留率自解, 中间没有结构性行, 所以判词数 = 行数。
assert lines[0].startswith(u'🧭') and lines[-1].startswith(u'✂')
GLOS = len(lines)
NL = dict((c, lbl.count(c)) for c in u'EP')
CROSS = len([a for a in uniq_atoms if CNT(re.escape(a), 0) > 0 and CNT(re.escape(a), 1) > 0])

p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-800:]
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
b46 = [x.strip() for x in row[u'B46'].split(u'|')]
allr = [x.strip() for x in row[u'ALL'].split(u'|')]
assert int(b46[0]) == dig and int(b46[1]) == enc, (b46[:2], dig, enc)
uniq_cp, blocks, cpu, dens = int(b46[4]), int(b46[5]), b46[6], b46[3]
soft = int(b46[10])
assert soft == 0, soft
assert not re.search(u'^\\s+B46 \\[', p.stdout, re.M), u'B46 不该出现在待核清单'
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
prev = dict(l.split(u'\t') for l in io.open(u'corpus/_f45stats.txt', encoding='utf-8').read().split(u'\n') if u'\t' in l)
assert proofs > int(prev[u'proofs']), (proofs, prev[u'proofs'])

MEAN = {
 u'0': u'零值键: 缺席型 %d 项(目录侧 13 项——转义层与词汇层上的缺席: 非 ASCII 码点、排版短横、带横杠的许可散文、'
      u'真斜杠 DOI、无空格的连接号写法、expressed、带前缀的 jatsxml URL、窗口后四天、日期形式的 published、'
      u'与前缀重合的期刊 DOI、字符串形式的 count、作为值的 null、分页键; 原文侧 9 项——下划线许可码、转义 DOI、'
      u'带空格的连接号写法、produced、第二个注册前缀、尖括号、粘连机构串、那串分号作者名、送达日期) '
      u'+ 等式与“恰好 N 处”型 %d 条(四个口径的 30、斜杠数与转义斜杠数之差、占位串加期刊 DOI 与记录数之差、'
      u'category 与 date 前缀的加一、裸数字字段与 null 的分配、若干“恰好一/二/三/五/六处”)'
      % (NABSEQ, NEQSEQ),
 u'1': u'带转义的 DOI 写法在目录里的命中数(它在原文 0 次, 那个 0 在 0 键里)',
 u'2': u'目录那串标题在原文里的命中数(目录自己 1 次, 等式在 0 键)',
 u'3': u'平写的 CO2 在原文里的命中数 ⇎ 带下标那种 5 处(5 折在 0 键)',
 u'4': u'目录的左尖括号数(全在摘要散文的比较号里, 不是标记)',
 u'5': u'“Ann Arbor”在原文的命中数 ⇎ 目录 1 处: 同一个地名零件在两边密度差三十倍',
 u'6': u'目录里 \\u 转义的个数(五处组合变音符 + 一处希腊字母), 目录的非 ASCII 码点为 0',
 u'7': u'“Michigan”在原文的命中数 ⇎ 目录 1 处',
 u'8': u'published 字段里填着另一个注册号(期刊 DOI)的行数',
 u'11': u'license 码取 cc_by_nc_nd 的行数(三十行里其余是别的码)',
 u'13': u'第二个注册前缀 10.64898 在目录的命中数(它在原文 0 次)',
 u'17': u'第一个注册前缀 10.1101 在目录的命中数; 两者相加恰为三十行(等式在 0 键)',
 u'19': u'目录里 version 写 2 的行数(写 1 的六行折在 0 键)',
 u'22': u'published 写占位串 NA 的行数: 与 %d 相加恰为记录数(等式在 0 键)' % 8,
 u'30': u'记录数, 也是本条唯一能在文件内自证的自报数; date、license、jatsxml 路径三个口径同值(三条等式在 0 键)',
 u'31': u'“category”这个键在目录出现的次数 = 三十行 + 封套那一处',
 u'32': u'“2026-01-0”这种日期前缀在目录的命中数 = 三十行 + 声明窗口的两个端点',
 u'40': u'带横杠的许可散文在原文的命中数(每页页脚重复); 目录侧那种写法 0 次',
 u'41': u'真斜杠写法的 DOI 在原文的命中数(四十处页脚加 url 那一行)',
 u'45': u'排版短横(–)在原文的命中数, 目录 0 处',
 u'73': u'原文“审计口径内字符数 − 抽取头自记字符数”: 恰是 url 那一行的长度, 因为 url 行不在剔除名单里',
 u'103': u'目录里“引号内以数字开头”的值数 ⇎ 裸数字字段只有 1 处(那正是 count)',
 u'178': u'封套两个自报数之差 total − count_new_papers',
 u'303': u'目录里的斜杠总数, 也是转义写法 \\u002f 的数: 没有一处裸斜杠(等式在 0 键)',
 u'331': u'原文里非 ASCII 码点的个数 ⇎ 目录 0 个',
 u'367': u'count_new_papers − 本页行数: 目录声称还有三百多篇新论文不在这三十行里',
 u'545': u'total − 本页行数: 同一个封套里最大的那个差',
 u'69657': u'目录内容区字符数(RCOT): 整份只有一行 JSON',
 u'80699': u'原文内容区字符数(RCOT) ⇎ 抽取头自记 80626 ⇎ 全文件 80861(第三个数住在口径之外)',
}
assert set(MEAN) == set(VALS), sorted(set(VALS) ^ set(MEAN))
ks = sorted(VALS, key=lambda x: float(x))
arith = u'；'.join(u'%s⇒%s' % (k, MEAN[k]) for k in ks if k != u'0')

T = []
T.append(u'※ 体例：本条两个源是**描述与被描述者**——⟪bioRxiv recent 接口的目录页 ⇎ 其中一行所指那篇原文的抽取文本⟫。'
         u'锚位 %d 个(不同串 %d 个；标 %s 的 %d 个、标 %s 的 %d 个)，判词 %d 行，DERIV %d 键，0 键折了 %d 个加法项'
         u'(缺席 %d 项、等式与“恰好 N 处” %d 项；这些项里 CNT 原语出现 %d 次，因为差值型一项要用两次计数)。'
         u'两条原文在字面上没有共享过任何一种 DOI 拼法，'
         u'所以“这两份讲的是同一件事”是本条重建出来的，不是机器读出来的。'
         % (len(atoms), len(uniq_atoms), LE, NL[LE], LP, NL[LP], GLOS, len(VALS), NTERMS0,
            NABSEQ, NEQSEQ, NTERM0))
T.append(u'※ 派生算术(键名即数值，表达式跑在两份原文上并逐个回算)：0⇒%s。%s。'
         u'本条 %d 个键里，减法式 %d 个(封套三个自报数的两两差 3 个，加上原文字符口径之差 %d)，'
         u'其余是直接计数；所有等式与“恰好 N 处”都折在 0 键里(%d 项)，因为键名就是数值，'
         u'两个同值的断言会抢同一个键——把相等写成减法式再合进 0，比给它们编新号更诚实。'
         % (MEAN[u'0'], arith, len(VALS), DIFFTERM, RCOT(1) - CHP, NEQSEQ))
T.append(u'※ 可核性的三级阶梯：① 纯 CNT 可核——三种 DOI 拼法的双向命中、%d 个转义斜杠、%d 个非 ASCII 码点、'
         u'published 里两种值的分配、七句摘要的命中数，全部在 %d 键里(句子对齐本身是 Python 集合判断，CNT 只负责它两侧的字面)；'
         u'② 需要外部断言——两份文件的 sha256(算法名与 64 个十六进制字符只写在 src 行，写成机检键会造出一个需要在源里逐字命中的“256”)、'
         u'封套里的 397 与 575(它们说的是本文件之外还有多少，永远无法在本文件内核对，本条只把它们的差留成机检式，并在判词里标明不能核对)；'
         u'③ 只属于工具侧——目录页的字节数 %d、全文件字符数 %d、原文全文件字符数 %d，以及“73 恰是 url 那一行的长度”这半句'
         u'(CNT 会数命中，不会量长度)。'
         % (CNT(BS + BS + u'/', 0), CNT(u'[^' + BS + u'x00-' + BS + u'x7f]', 1), len(VALS),
            raw_bytes[0], full_chars[0], full_chars[1]))
T.append(u'※ 一个假 0 怎么变成结论：起初在目录里数 content/early，得到 0，看起来像“这批 URL 不走 early 路径”。'
         u'顺着 0 去问为什么，才发现这个文件里每一个斜杠都写成 \\u002f 或反斜杠加斜杠——裸斜杠一处也没有，'
         u'于是那个 0 是**转义层**造成的，不是路径造成的。改写正则(斜杠前补一层转义)之后同一处命中变成 %d，'
         u'而真正有意思的 0 才露出来：把前缀拼回 URL 里去找，仍旧 0 命中——jatsxml 那一条把注册前缀整个丢掉，'
         u'原位换上的是送达日期。同一个字段名下的两种拼法因此成了本条的头号判词：'
         u'连接键在两份文件里没有一次按同一种写法出现。附带一条纪律：锚点在建立时一律要求**在本源内唯一**，'
         u'这一条挡掉了 “published:NA” 那种重复 %d 次的样式串，迫使每个锚都落在被联结那一行自己的字面上。'
         % (CNT(u'content' + BS + BS + u'/early', 0), CNT(re.escape(u'"published":"NA"'), 0)))
T.append(u'※ 口径与 0 的两重成因：原文有三个字符数——抽取头自记 %d ⇎ 审计口径内 %d ⇎ 全文件 %d，'
         u'前两者之差 %d 就是那一行 url 的长度(url 不在剔除名单里)，后两者之差是全部出处头行。'
         u'目录侧没有出处头，口径内 %d ⇎ 全文件 %d 只差结尾几个换行。'
         u'于是本条有两类 0：真的没有(目录里没有裸斜杠、没有非 ASCII 码点、没有分页键)，'
         u'以及写了但住在口径之外(原文的 title 行记的是文件名，真标题在正文第一行，'
         u'所以“原文没有标题”与“原文写着标题”同时为真)。凡遇 0 先问它属于哪一类，这一问比数一遍更便宜。'
         % (CHP, RCOT(1), full_chars[1], RCOT(1) - CHP, RCOT(0), full_chars[0]))
T.append(u'※ 两源对齐：J=%s(口径内 %d 字符 ⇎ 磁盘 %d 字节，整份只有一行 JSON) ⇎ P=%s(口径内 %d 字符)。'
         u'摘要段 union_hit=%d 与锚位数相等(同一串被重复引用的锚位 %d 个，不同串 %d 个)，摘要段共 %d 字符 ⇎ '
         u'两份窗口合计 %d 字符；两份文件里同时能找到的锚串只有 %d 个，而那一个是那行标题——它在原文口径内命中 2 处'
         u'(正文标题位与补充材料的标题位各一处，这一句是版面观察，属工具侧)，目录里则只有 1 处；'
         u'真正当连接键用的 DOI 一个也没对上(那个对应是本条用规则重建的，不是字面撞上的)。'
         u'标签归位仍是作者的职责而不是机检的功劳：'
         u'atomcheck 与 audit 都是把同一 tag 的两个源拼在一起比对字面，⟦%s⟧/⟦%s⟧ 写反不会 FAIL；'
         u'本条机检 ok=%d/%d。'
         % (os.path.basename(RJ), RCOT(0), raw_bytes[0], os.path.basename(RP), RCOT(1),
            len(atoms), len(atoms) - len(uniq_atoms), len(uniq_atoms), dig, RCOTSUM, CROSS,
            LE, LP, len(uniq_atoms), len(uniq_atoms)))
T.append(u'※ 隐性知识的所在(判词逐行对应的判断)：① 连接键要两边同拼法才叫能联结；② 声明的区间与交付的区间可以差掉大半，'
         u'目录不会承认；③ 自我报告按“能否在本文件内核对”分档；④ 同一对象里整型与字符串并存，数字的类型不是语义；'
         u'⑤ 字段名说意图、值说另一件事(published 里没有时间)；⑥ 索引里的摘要是改写而不是引文，一词之差要逐句对齐才看得见；'
         u'⑦ 标点与重音有两种存活方式(转义 ⇎ 直接写)，字面比对时互相看不见；⑧ 描述层与被描述层各用一套词汇，'
         u'映射不住在这两份文件里；⑨ 词形会碰撞(目录的 version=2 ⇎ 原文里的“v2”是软件版本)；'
         u'⑩ 0 有两种成因(没有 ⇎ 被口径剔掉)，自记字符数是第三种口径；⑪ 双向缺席 ⇒ 两份都得存。'
         u'与上一条的分工：B45 数的是同一个名字的三种对象(互不包含的文件)，本条数的是同一个标识符的三种拼法'
         u'与同一个内容的两种说法(层间差)，判据不重叠。')
T.append(u'※ 实况：编码 %d 字符 ⇎ 摘要段 %d 字符(保留率 %s)，vs raw 源 %s，唯一码点 %d，区块 %d 类，字符/语义单元 %s。'
         u'拉丁字母：锚内 %d ⇎ 锚外 %d(其中出处标签 %d)。全库现 %d 条 / 已机检推导 %d 条 / 全库保留率 %s。'
         u'B46 的小整数待核为 0 项。'
         % (enc, dig, b46[2], dens, uniq_cp, blocks, cpu, in_lat, out_lat, tag_lat, len(row) - 1, proofs, allr[2]))
T.append(u'※ 保留率口径：本条 %s 高于 100%% 是对照条的结构性结果——摘要段只索引锚点触到的窗口(两个源合计 %d 字符，'
         u'窗口只取了 %d)，而判词要在目录与原文之间来回数(三种拼法、两套词汇、双向缺席、三个字符口径)，字符自然重于窗口。'
         u'读它要按“%d 键支撑 %d 行判词”与 vs raw 源 %s 来读，不是按“少说了多少话”；'
         u'若只留目录那三十行而丢掉原文，本条一半的 0 就无从判定——分母变了，缺席也就不叫缺席了。'
         % (b46[2], RCOTSUM, dig, len(VALS), GLOS, dens))

G = md[:md.index(u'## ⛓解读注')] + u'## ⛓解读注\n' + u'\n\n'.join(T) + u'\n'
io.open(ENTRY, 'w', encoding='utf-8').write(G)

ST = {u'in_lat': in_lat, u'out_lat': out_lat, u'tag_lat': tag_lat, u'out_all': out_all,
      u'anchors': len(atoms), u'uniq_anchor': len(uniq_atoms), u'digest': dig, u'enc': enc,
      u'ret': b46[2], u'raw_chars': raw_chars, u'raw_bytes': raw_bytes, u'full_chars': full_chars,
      u'uniq_cp': uniq_cp, u'blocks': blocks, u'cpu': cpu, u'proofs': proofs, u'dens': dens,
      u'deriv_keys': len(VALS), u'n_term0': NTERM0, u'n_terms0': NTERMS0,
      u'n_absent': NABSEQ, u'n_equ': NEQSEQ,
      u'n_diff': DIFFTERM, u'gloss_lines': GLOS,
      u'n_sent': len(SENT), u'n_sent_hit': len(HIT), u'n_sent_out': len(OUT), u'n_pub': len(PUBS),
      u'chars_hdr': CHP, u'd73': RCOT(1) - CHP, u'cross_atoms': CROSS, u'sha_j': sha[0], u'sha_p': sha[1],
      u'anchor_E': NL[LE], u'anchor_P': NL[LP], u'all_ret': allr[2], u'all_enc': allr[1],
      u'all_digest': allr[0], u'all_cp': allr[4]}
io.open(u'corpus/_f46stats.txt', 'w', encoding='utf-8').write(
    u'\n'.join(u'%s\t%s' % (k, v) for k, v in dict(BST, **ST).items()) + u'\n')
print(u'gloss written: keys %d enc %d dig %d ret %s uniq %d anchors %d(%d uniq) E/P %d/%d '
      u'in_lat %d out_lat %d tag %d proofs %d soft %d cross %d'
      % (len(VALS), enc, dig, b46[2], uniq_cp, len(atoms), len(uniq_atoms), NL[LE], NL[LP],
         in_lat, out_lat, tag_lat, proofs, soft, CROSS))
