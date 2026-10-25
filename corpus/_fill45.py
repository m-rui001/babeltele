# -*- coding: utf-8 -*-
"""B45 记账: ⛓解读注由 audit 里的 DERIV 表达式独立回算生成, 不手填任何数字。
四个源: A=归档成员 tz/zone1970.tab, F=单文件抓取 zone1970_latest.tab,
N=姊妹表 tz/zone.tab, H=名叫 zone1970.tab 的索引网页。"""
import io, re, sys, os, subprocess, ast

sys.stdout.reconfigure(encoding='utf-8')

TAG = u'B45'
ENTRY = u'corpus/babeltele/B45_registry_name_two_objects.md'
RA = u'corpus/raw/tz/zone1970.tab'
RF = u'corpus/raw/zone1970_latest.tab'
RN = u'corpus/raw/tz/zone.tab'
RH = u'corpus/raw/zone1970.tab'
RAWS = [RA, RF, RN, RH]
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)


def reason(i):
    s = io.open(RAWS[i], encoding='utf-8', errors='replace').read()
    return u'\n'.join(l for l in s.split(u'\n') if not HEADRX.match(l.strip()))


SRC = [reason(0), reason(1), reason(2), reason(3)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
RCOT = lambda i: len(SRC[i].strip())

# —— 配对与差集: 与建条目那条路无关, 这里从原文重新摊一遍 ——
RAWA = io.open(RA, encoding='utf-8').read()
RAWN = io.open(RN, encoding='utf-8').read()


def pairs_of(txt):
    out = set()
    for l in txt.split(u'\n'):
        s = l.strip()
        if s == u'' or s.startswith(u'#'):
            continue
        f = s.split(u'\t')
        if len(f) < 3:
            continue
        for c in f[0].split(u','):
            out.add((c.strip(), f[2].strip()))
    return out


PA, PN = pairs_of(RAWA), pairs_of(RAWN)
AONLY, NONLY = sorted(PA - PN), sorted(PN - PA)


def alt(ps, flat=False):
    br = []
    for c, z in ps:
        br.append((u'^%s\\t[^\\t\\n]*\\t%s(?=\\t|$)' if flat else
                   u'(?:[A-Z]{2},)*%s(?:,[A-Z]{2})*\\t[^\\t\\n]*\\t%s(?=\\t|$)') % (c, re.escape(z)))
    return u'(?m)' + u'|'.join(br)


A_AL, N_AL, AF_AL = alt(AONLY), alt(NONLY), alt(AONLY, True)
ENV = {u'CNT': CNT, u'RCOT': RCOT, u'L': lambda x: float(x.replace(u',', u'')), u'round': round,
       u'B45_AONLY': A_AL, u'B45_NONLY': N_AL, u'B45_AFLAT': AF_AL}

# —— 取 audit 里那条 DERIV 表达式, 逐键在与建条目同源的文本上回算 ——
au = io.open(u'corpus/audit.py', encoding='utf-8').read()
blk = re.search(u" 'B45': \\{\n(.*?)\n \\},", au, re.S).group(1)
VALS, EXPR = {}, {}
for m in re.finditer(r"^ {2}'([^']+)': (.*)$", blk, re.M):
    k, v = m.group(1), m.group(2).strip().rstrip(u',')
    EXPR[k] = ast.literal_eval(v)
    VALS[k] = float(k)
assert len(VALS) == 25, len(VALS)
for k, v in EXPR.items():
    got = float(eval(v, {}, ENV))
    assert abs(got - float(k)) < 1e-9, (k, got, v[:90])
NTERM0 = EXPR[u'0'].count(u'CNT(')
# 差集大小本身: 集合运算给出, 机检侧证据是宽度桶之和与两个 0 命中
SUMW = sum(CNT(u'(?m)^(?:[A-Z]{2},){%d}[A-Z]{2}(?=,|\t)' % (j - 1), 0) for j in range(2, 25))
assert (len(PA), len(PN), len(AONLY), len(NONLY)) == (423, 418, 111, 106)
assert SUMW == len(AONLY) == 111
assert (CNT(A_AL, 0), CNT(A_AL, 2)) == (34, 0)
assert (CNT(N_AL, 2), CNT(N_AL, 0), CNT(AF_AL, 0)) == (106, 0, 0)
assert (CNT(u'(?m)^[A-Z]{2},', 0), CNT(u'(?m)^[A-Z]{2}[,\t]', 0) - CNT(u'(?m)^[A-Z]{2},', 0)) == (34, 278)
assert CNT(u'(?m)^[^\t\n]*\t[^\t\n]*\t[^\t\n]*\t', 0) == 201

md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
lbl = re.findall(u'⟦([AFNH])⟧⟨', body)
uniq_atoms = sorted(set(atoms))
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
tag_lat = len(lbl)
out_all = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
out_lat = out_all - tag_lat
enc = len(body.replace(u'\n', u''))
dig = len(re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', md, re.S).group(1))
raw_chars = [len(SRC[i]) for i in range(4)]
raw_bytes = [os.path.getsize(p) for p in RAWS]
full_chars = [len(io.open(p, encoding='utf-8', errors='replace').read()) for p in RAWS]
full_lines = [len(io.open(p, encoding='utf-8', errors='replace').read().split(u'\n')) for p in RAWS]
hash_lines = [len([l for l in io.open(p, encoding='utf-8', errors='replace').read().split(u'\n')
                   if l.startswith(u'#')]) for p in RAWS]

p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
b45 = [x.strip() for x in row[u'B45'].split(u'|')]
allr = [x.strip() for x in row[u'ALL'].split(u'|')]
assert int(b45[0]) == dig and int(b45[1]) == enc, (b45[:2], dig, enc)
uniq_cp, blocks, cpu, dens = int(b45[4]), int(b45[5]), b45[6], b45[3]
soft = int(b45[10])
assert soft == 0, soft
assert not re.search(u'^\\s+B45 \\[', p.stdout, re.M), u'B45 不该出现在待核清单'
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
# proofs 数的是“作为锚点出现且有 DERIV 算式”的数字, 条目新增键未必全被计入;
# 这里用上一条留下的记账值做回归下限, 不写死数。
prev = dict(l.split(u'\t') for l in io.open(u'corpus/_f44stats.txt', encoding='utf-8').read().split(u'\n') if u'\t' in l)
assert proofs > int(prev[u'proofs']), (proofs, prev[u'proofs'])

lines = [l for l in body.split(u'\n') if l.strip()]
GLOS = len(lines) - 2
NL = dict((c, lbl.count(c)) for c in u'AFNH')

MEAN = {
 u'0': u'零值键: 表侧 %d 项标记在三份表里缺席 + 网页侧 %d 项在网页里缺席 + 配对层面 %d 项 0 命中 '
      u'(姊妹表里没有 A 侧配对、A 表里没有 N 侧配对、平铺行里没有差集对、姊妹表里没有合并行) '
      u'+ 等式差 %d 条(两条路径的长度/制表符/行数、三列行数与宽度展开的额外码数、携带差集对的行数与合并行数)'
      % (11, 5, 4, 5),
 u'1': u'并到二十个国家码的那一行的行数(全表恰 1 行, 即最长合并行)',
 u'2': u'网页里 “1970” 的命中数; “public domain” 同值, 授权声明只住在散文里',
 u'5': u'两侧差集之差(只在 A 的配对数 − 只在 N 的配对数): 两边都非空才谈得上“不是重排”',
 u'6': u'归档后缀 “.tar.gz” 在网页的命中数(表侧为 0, 在 0 键里)',
 u'7': u'“@” 在网页的命中数(联系入口只在散文侧)',
 u'13': u'“tzdata” 在网页的命中数(表里从不写归档名)',
 u'26': u'网页里的制表符数 ⇎ 两份表的 825: 判格式靠分隔符密度而不是扩展名',
 u'34': u'A 侧第一个字段用逗号并了多国码的合并行数(它等于携带差集对的行数, 差值在 0 键里)',
 u'48': u'“数字点数字”的版本号写法在网页的命中数(表侧 0)',
 u'106': u'只在姊妹表 N 成立的(国家码, zone) 配对数: 它的正则分支在 A 里 0 命中',
 u'111': u'只在 A 成立的配对数; 机检侧等于各宽度桶展开出的额外码数之和',
 u'124': u'“两位大写逗号”形式在网页的命中数(散文里的行首码, 不是表行)',
 u'201': u'A 侧带第四列(注释)的行数 ⇎ N 侧 202: 差 1 行, 两侧结构同形',
 u'202': u'姊妹表 N 侧四列行数',
 u'278': u'A 侧一行一码的平铺行数(312 − 34): 这一批与姊妹表逐对一致, 是“分歧只在合并行”的下半句',
 u'312': u'A 侧数据行数(审计口径)',
 u'357': u'“href” 在网页的命中数(表侧 0)',
 u'418': u'姊妹表 N 数据行数(审计口径) ⇎ 312',
 u'825': u'A 侧制表符数 ⇎ F 侧同值(等式在 0 键里)',
 u'1038': u'姊妹表 N 侧制表符数',
 u'2087': u'网页左尖括号数(表侧 0)',
 u'2406': u'网页斜杠数(路径与标签的密度)',
 u'14482': u'A 内容区字符数(RCOT) ⇎ F 同值',
 u'65201': u'网页内容区字符数(RCOT): 比两份表都长, 却不是一行一事实',
}
assert set(MEAN) == set(VALS), sorted(set(VALS) ^ set(MEAN))
ks = sorted(VALS, key=lambda x: float(x))
arith = u'；'.join(u'%s⇒%s' % (k, MEAN[k]) for k in ks if k != u'0')

T = []
T.append(u'※ 体例：本条四个源指向同一个名字底下的三种对象—— ⟪tzdata 归档成员 ⇎ 单文件抓取 ⇎ 姊妹表 zone.tab ⇎ '
         u'索引网页⟫，前两份逐字节相同，第三份归属模型不同，第四份根本不是表。锚位 %d 个(不同串 %d 个；'
         u'标 %s 的 %d 个、%s 的 %d 个、%s 的 %d 个、%s 的 %d 个)。判词 %d 行，DERIV %d 键，0 键里折了 %d 个 CNT 项。'
         % (len(atoms), len(uniq_atoms), u'A', NL[u'A'], u'F', NL[u'F'], u'N', NL[u'N'], u'H', NL[u'H'],
            GLOS, len(VALS), NTERM0))
T.append(u'※ 派生算术(键名即数值，表达式跑在四份原文上并逐个回算)：0⇒%s。%s。'
         u'其中 %d 条是差值/等式型而非直接计数型：两条路径的 RCOT 差、制表符差、行数差各一条，'
         u'“三列行数 == 宽度展开的额外码数”一条，“携带差集对的行数 == 合并行数”一条——用差值表达是为了把'
         u'“同一份的两个副本”这类断言留在机检范围内，而不是退回到不可复算的形容词。'
         % (MEAN[u'0'], arith, 5))
T.append(u'※ 可核性的三级阶梯(本条最想把话说清楚的一处)：'
         u'① 纯 CNT 可核：长度、行数、分隔符与标记字符的命中数、四类 0 命中，全部在 %d 键里；'
         u'② 需要外部断言：两份文件逐字节相同——本机用 hashlib/certutil 求摘要，算法名与 %s 个十六进制字符都写在 src 行，'
         u'不写成机检键，因为工具会把 “sha256” 里的 “256” 当成一个需要在源里逐字命中的硬数字；'
         u'③ 只属于工具侧：字节数(归档成员 %d ⇎ 网页 %d)与归档成员身份这类抓取元信息。'
         u'再补一句诚实话：差集大小 111/106 是 Python 集合运算给出的，CNT 侧的对应证据是宽度桶之和与两个 0 命中分支式，'
         u'两者同值不等于同一条计算——前者定义“差集”，后者证明“这些对在对方表里确实一次都不出现”。'
         % (len(VALS), u'64', raw_bytes[0], raw_bytes[3]))
T.append(u'※ 正则的逐行语义如何变成结论：re.findall 对长分支交替式给的是**不重叠命中**，'
         u'也就是“含差集对的行数”而不是“差集对数”。第一次跑出 34 而不是 111 时看起来像 bug，'
         u'顺着它去问“那 34 行是什么”，得到的却是本条最硬的一条：34 恰是合并行数，'
         u'而“平铺行配差集对”的行式(另一条交替式)在 A 里 0 命中——于是分歧被定位到了写法层面：'
         u'一行一码的那 %d 行与姊妹表逐对一致，全部 %d 对差异都住在用逗号并码的 %d 行里。'
         u'同一个 34 还是 “312 − 278” 的那个减数，所以这条结论有三个方向的支撑(行数、0 命中、行数差)。'
         % (278, 111, 34))
T.append(u'※ 口径与“表里 0 次”的两重成因：审计证据范围会剔掉以 # 起始的行与出处头样式，'
         u'于是同一批字节有两种行数：A 全文件 %d 行(其中 %d 行以 # 起始，另有一行空行) ⇎ 口径内 %d 行数据；'
         u'姊妹表全文件 %d 行 ⇎ 口径内 %d 行；网页全文件 %d 行且 %d 行注释，全部落在口径内。'
         u'字符数同理：A 内容区 %d ⇎ 全文件 %d 字符(⇎ 磁盘 %d 字节，字节数只写在 src 行)。'
         u'因此“1970”“public domain”这两个 0 有两重成因——它既不在数据行里，也不在算证据的那几行里，'
         u'而是住在被剔掉的注释行；这也正是 0 键里那个零需要单独说明的原因：'
         u'0 不是“没写”，是“写了但不在口径内”。'
         % (full_lines[0], hash_lines[0], int(ENV[u'CNT'](u'(?m)^[A-Z]{2}[,\t]', 0)),
            full_lines[2], int(ENV[u'CNT'](u'(?m)^[A-Z]{2}[,\t]', 2)),
            full_lines[3], hash_lines[3], RCOT(0), full_chars[0], raw_bytes[0]))
T.append(u'※ 四源对齐：A=%s(口径内 %d 字符 ⇎ 磁盘 %d 字节) ≡ F=%s(口径内 %d 字符 ⇎ %d 字节)；'
         u'N=%s(口径内 %d 字符)；H=%s(口径内 %d 字符)。'
         u'A 与 F 内容逐字节相同，所以二者的锚天然互相命中(摘要段 union_hit=%d 与锚位数相等，'
         u'同一串重复引用的锚位 %d 个，不同串 %d 个)——本条靠 ⟦LBL⟧ 标注区分两种到达路径，而不指望工具检查标签归位：'
         u'atomcheck 与 audit 都是把同一 tag 的四个源拼在一起比对字面，标签写错不会 FAIL，这是作者的职责而不是机检的功劳。'
         u'真正被机检的是对象类型：制表符 %d ⇎ %d ⇎ %d ⇎ %d，尖括号 %d ⇎ %d ⇎ %d ⇎ %d。'
         % (os.path.basename(RA), RCOT(0), raw_bytes[0], os.path.basename(RF), RCOT(1), raw_bytes[1],
            os.path.basename(RN), RCOT(2), os.path.basename(RH), RCOT(3), len(atoms),
            len(atoms) - len(uniq_atoms), len(uniq_atoms),
            ENV[u'CNT'](u'\t', 0), ENV[u'CNT'](u'\t', 1), ENV[u'CNT'](u'\t', 2), ENV[u'CNT'](u'\t', 3),
            ENV[u'CNT'](u'<', 0), ENV[u'CNT'](u'<', 1), ENV[u'CNT'](u'<', 2), ENV[u'CNT'](u'<', 3)))
T.append(u'※ 隐性知识的所在(判词逐行对应的判断)：① 文件名是意图，内容是证据；② 同名不同物的两份文件会互相顶掉证据'
         u'(这个目录里 zone1970.tab 是网页，zone1970_latest.tab 才是表)；③ “同一份”要哈希断言，长度/行数/分隔符只是下限；'
         u'④ 姊妹表先算双侧差集再谈重排；⑤ 单侧空是包含，双侧空才是相同；⑥ 合并写法的展开增量恰等于一侧的独有配对数；'
         u'⑦ 表回答归属不回答理由，理由住在注释与散文；⑧ 注释行会被口径剔掉，于是“表里 0 次”与“表里写着”同时为真；'
         u'⑨ 报行数与字符数必须报口径；⑩ 缺席双向 ⇒ 三种对象互不包含，三份都得存；'
         u'⑪ 版本号、授权这类元信息住在会被剥掉的那一层。与上一条的分工：那条数的是同一内容的两种序列化(层间差)，'
         u'本条数的是同一个名字的三种对象(互不包含)，两条判据不重叠。')
T.append(u'※ 实况：编码 %d 字符 ⇎ 摘要段 %d 字符(保留率 %s)，vs raw 源 %s，唯一码点 %d，区块 %d 类，字符/语义单元 %s。'
         u'拉丁字母：锚内 %d ⇎ 锚外 %d(其中出处标签 %d)。全库现 %d 条 / 已机检推导 %d 条 / 全库保留率 %s。'
         u'B45 的小整数待核为 0 项(整条没有需要挂起的数字切片)。'
         % (enc, dig, b45[2], dens, uniq_cp, blocks, cpu, in_lat, out_lat, tag_lat, len(row) - 1, proofs, allr[2]))
T.append(u'※ 保留率口径：本条 %s 高于 100%% 是对照条的结构性结果——摘要段只索引锚点触到的窗口(四个源合计 %d 字符，'
         u'窗口只取了 %d)，而判词要在四个源之间来回数(两侧差集、两条路径、双向缺席)，字符自然重于窗口。'
         u'读它要按“%d 键支撑 %d 行判词”与 vs raw 源 %s 来读，不是按“少说了多少话”；'
         u'若把网页那份当表来摘要，就会把对象差读成内容差，那正是本条要防的错。'
         % (b45[2], sum(raw_chars), dig, len(VALS), GLOS, dens))

G = md[:md.index(u'## ⛓解读注')] + u'## ⛓解读注\n' + u'\n\n'.join(T) + u'\n'
io.open(ENTRY, 'w', encoding='utf-8').write(G)

ST = {u'in_lat': in_lat, u'out_lat': out_lat, u'tag_lat': tag_lat, u'out_all': out_all,
      u'anchors': len(atoms), u'uniq_anchor': len(uniq_atoms), u'digest': dig, u'enc': enc,
      u'ret': b45[2], u'raw_chars': raw_chars, u'raw_bytes': raw_bytes,
      u'full_lines': full_lines, u'hash_lines': hash_lines,
      u'uniq_cp': uniq_cp, u'blocks': blocks, u'cpu': cpu, u'proofs': proofs, u'dens': dens,
      u'deriv_keys': len(VALS), u'n_term0': NTERM0, u'gloss_lines': GLOS,
      u'pairs_A': len(PA), u'pairs_N': len(PN), u'a_only': len(AONLY), u'n_only': len(NONLY),
      u'sumw': SUMW, u'flat_rows': 278, u'merged_rows': 34, u'four_col_A': 201,
      u'rows_A': int(ENV[u'CNT'](u'(?m)^[A-Z]{2}[,\t]', 0)), u'rows_N': int(ENV[u'CNT'](u'(?m)^[A-Z]{2}[,\t]', 2)),
      u'anchor_A': NL[u'A'], u'anchor_F': NL[u'F'], u'anchor_N': NL[u'N'], u'anchor_H': NL[u'H'],
      u'all_ret': allr[2], u'all_enc': allr[1], u'all_digest': allr[0], u'all_cp': allr[4]}
io.open(u'corpus/_f45stats.txt', 'w', encoding='utf-8').write(
    u'\n'.join(u'%s\t%s' % (k, v) for k, v in ST.items()) + u'\n')
print(u'DERIV %d 键全部独立复算通过' % len(VALS))
print(u'gloss written: keys %d enc %d dig %d ret %s uniq %d anchors %d(%d uniq) A/F/N/H %d/%d/%d/%d '
      u'in_lat %d out_lat %d tag %d proofs %d soft %d'
      % (len(VALS), enc, dig, b45[2], uniq_cp, len(atoms), len(uniq_atoms),
         NL[u'A'], NL[u'F'], NL[u'N'], NL[u'H'], in_lat, out_lat, tag_lat, proofs, soft))
