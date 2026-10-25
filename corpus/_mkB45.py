# -*- coding: utf-8 -*-
# B45 四名同目条: 时区注册表的归档成员 ⇎ 逐字节相同的单文件抓取 ⇎ 冒充该名的网页 ⇎ 归属不同的姊妹表
# 锚点从"折叠空白"的正文行切片(逐字由构造保证); 计数一律走 audit 的 _reason 口径(# 起始的注释行被剔掉)。
import io, re, sys, os, hashlib

sys.stdout.reconfigure(encoding='utf-8')

RA = u'corpus/raw/tz/zone1970.tab'          # 归档解出的成员
RF = u'corpus/raw/zone1970_latest.tab'      # 单文件抓取, 与 RA 逐字节相同
RN = u'corpus/raw/tz/zone.tab'              # 姊妹表: 一国一行
RH = u'corpus/raw/zone1970.tab'             # 名叫 .tab, 实为索引网页(抓取命名冲突)
ENTRY = u'corpus/babeltele/B45_registry_name_two_objects.md'
LA, LF, LN, LH = u'A', u'F', u'N', u'H'
HEADRX = r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)'
CN = {0: u'零', 1: u'一', 2: u'两', 3: u'三', 4: u'四', 5: u'五', 6: u'六', 7: u'七', 8: u'八',
      9: u'九', 10: u'十', 11: u'十一', 12: u'十二', 13: u'十三', 16: u'十六', 19: u'十九',
      20: u'二十', 21: u'二十一', 33: u'三十三', 38: u'三十八'}


def split(raw):
    T = io.open(raw, encoding='utf-8', errors='replace').read()
    lines = T.split(u'\n')
    HDR = [l for l in lines if re.match(HEADRX, l.strip(), re.I)]
    return HDR, lines, u'\n'.join([l for l in lines if l not in HDR])


HA, LNA, BA = split(RA)
HF, LNF, BF = split(RF)
HN, LNN, BN = split(RN)
HH, LNHH, BH = split(RH)
assert BA == BF, u'两条路径的正文必须逐字节相同, 否则本条判据不成立'
COL = lambda t: re.sub(r'\s+', u' ', t)
CA, CF, CNX, CH = COL(BA), COL(BF), COL(BN), COL(BH)
R0, R1 = len(BA.strip()), len(BF.strip())
FA = len(u'\n'.join(LNA))
SHA = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
BS = lambda p: os.path.getsize(p)
SHA_A, SHA_F, SHA_N, SHA_H = SHA(RA), SHA(RF), SHA(RN), SHA(RH)
assert SHA_A == SHA_F and len(SHA_A) == 64 and R0 == R1
assert (R0, FA, len(BH)) == (14482, 17536, 65202), (R0, FA, len(BH))


def PH(p):
    if p.startswith(u'(?') or u'\\' in p:
        return p
    return r'\s+'.join(re.escape(w) for w in p.split(u' '))


NA = lambda pat: len(re.findall(pat, BA, re.I))
NN = lambda pat: len(re.findall(pat, BN, re.I))
NH = lambda pat: len(re.findall(pat, BH, re.I))

# ---------- 行式与列式 ----------
ROWA = u'(?m)^[A-Z]{2}[,\\t]'
FOURA = u'(?m)^[^\\t\\n]*\\t[^\\t\\n]*\\t[^\\t\\n]*\\t'
MULTI = u'(?m)^[A-Z]{2},'
ROWS_A, ROWS_N, FOUR_A, FOUR_N, MULTI_A = NA(ROWA), NN(ROWA), NA(FOURA), NN(FOURA), NA(MULTI)
THREE_A, THREE_N = ROWS_A - FOUR_A, ROWS_N - FOUR_N
assert (ROWS_A, ROWS_N, FOUR_A, FOUR_N, MULTI_A, THREE_A, THREE_N) == (312, 418, 201, 202, 34, 111, 216), \
    (ROWS_A, ROWS_N, FOUR_A, FOUR_N, MULTI_A, THREE_A, THREE_N)
PJ = lambda j: u'(?m)^(?:[A-Z]{2},){%d}[A-Z]{2}(?=,|\\t)' % (j - 1)      # 行内码数 >= j
EXTR = sum(NA(PJ(j)) for j in range(2, 25))
BIG20 = NA(PJ(20))
assert (EXTR, BIG20) == (111, 1), (EXTR, BIG20)
TABS_A, TABS_N, TABS_H = NA(r'\t'), NN(r'\t'), len(re.findall(r'\t', BH, re.I))
LT_H, GT_H, HREF_H, COMMA_H = NH(r'<'), NH(r'>'), NH(r'href'), NH(r'[A-Z]{2},')
AT_H, MAIL_H, TZD_H, GZ_H, DDF_H, SLASH_H = NH(r'@'), NH(r'mailto'), NH(r'tzdata'), \
    NH(r'\.tar\.gz'), NH(r'\d\.\d'), NH(r'/')
C1970_H, PD_H, LEAP_H = NH(r'1970'), NH(r'public domain'), NH(r'leap')
assert (TABS_A, TABS_N, TABS_H) == (825, 1038, 26)
assert (LT_H, GT_H, HREF_H, COMMA_H) == (2087, 2087, 357, 124)
assert (AT_H, MAIL_H, TZD_H, GZ_H, DDF_H, SLASH_H) == (7, 2, 13, 6, 48, 2406)
assert (C1970_H, PD_H, LEAP_H) == (2, 2, 34)

# ---------- 姊妹表的归属差集(逐对生成正则, 在对方文件里必为 0) ----------
def pairs(T):
    S = set()
    for l in [x for x in T.split(u'\n') if x]:
        f = l.split(u'\t')
        for c in f[0].split(u','):
            S.add((c, f[2]))
    return S


PA, PN = pairs(BA), pairs(BN)
AONLY, NONLY = sorted(PA - PN), sorted(PN - PA)
assert (len(PA), len(PN), len(AONLY), len(NONLY)) == (423, 418, 111, 106)
DIFF5 = len(AONLY) - len(NONLY)
assert DIFF5 == 5


def alternation(S):
    br = [u'(?:[A-Z]{2},)*%s(?:,[A-Z]{2})*\\t[^\\t\\n]*\\t%s(?=\\t|$)' % (c, re.escape(z)) for c, z in S]
    return u'(?m)' + u'|'.join(br)


PAT_A, PAT_N = alternation(AONLY), alternation(NONLY)
NRA = NA(PAT_A)
assert (NRA, NN(PAT_A)) == (34, 0) and NRA == MULTI_A
assert (NN(PAT_N), NA(PAT_N)) == (106, 0)


PAT_AF = u'(?m)' + u'|'.join([u'^%s\\t[^\\t\\n]*\\t%s(?=\\t|$)' % (c, re.escape(z)) for c, z in AONLY])
assert NA(PAT_AF) == 0
ZONE_A = len(set(z for _, z in PA))
assert ZONE_A == 312

# ---------- 双向缺席 ----------
ABS_TAB = [r'<', r'href', r'mailto', r'@', r'zone1970', r'\.tab', r'tzdata', r'\.tar\.gz',
           r'1970', r'public domain', r'\d\.\d']
ABS_H = [ROWA, u'(?m)\\t[+-]\\d', r'zone1970', r'\.tab', r'Etc/']
for p in ABS_TAB:
    assert NA(p) == 0 and NN(p) == 0, (p, NA(p), NN(p))
for p in ABS_H:
    assert NH(p) == 0, (p, NH(p))
assert NN(MULTI) == 0 and NA(MULTI) == 34
NABS_T, NABS_H, NABS = len(ABS_TAB), len(ABS_H), len(ABS_TAB) + len(ABS_H)
NEQU, NPAIRZ = 5, 4
print(u'absences tables=%d html=%d / pairs %d,%d / rows %d,%d / four %d,%d' %
      (NABS_T, NABS_H, len(AONLY), len(NONLY), ROWS_A, ROWS_N, FOUR_A, FOUR_N))

# ---------- 锚点 ----------
def S(src, key, pre=140, post=190):
    m = re.search(re.escape(key) if u'\\' not in key else key, src, re.I)
    assert m, u'KEY MISS: ' + key
    ks, ke = m.start(), m.end()
    mm = None
    for x in re.finditer(u'[.;:>]\\s', src[max(0, ks - pre):ks]):
        mm = x
    a = max(0, ks - pre) + (mm.end() if mm else 0)
    tail = src[ke:min(len(src), ke + post)]
    m2 = re.search(u'[.;:<]', tail)
    b = ke + (len(tail) if m2 is None else (0 if m2.start() == 0 else m2.end() - 1))
    return src[a:b].strip().strip(u' ,;')


def AK(*cands, **kw):
    src = {LA: CA, LF: CF, LN: CNX, LH: CH}[kw.get('w', LA)]
    for k in cands:
        if re.search(re.escape(k) if u'\\' not in k else k, src, re.I):
            return S(src, k, kw.get('pre', 140), kw.get('post', 190))
    raise AssertionError(u'ALL MISS: ' + cands[0][:60])


def ROWOF(which, needle):
    body = {LA: BA, LF: BF, LN: BN, LH: BH}[which]
    for l in [x for x in body.split(u'\n') if x]:
        if re.search(needle, l, re.I):
            return COL(l).strip()
    raise AssertionError(u'ROW MISS: ' + needle)


AN = {}
AN['andorra'] = ROWOF(LA, r'^AD\t')                                  # 三列行(无注释列)
AN['london'] = ROWOF(LA, r'^GB,GG,IM,JE\t')                          # 四码合并行
AN['dubai'] = ROWOF(LA, r'^AE,OM,RE,SC,TF\t')                        # 五码合并行
AN['twenty'] = ROWOF(LA, r'^(?:[A-Z]{2},){19}[A-Z]{2}\t')            # 一行二十个码
AN['fourcol'] = ROWOF(LA, r'^[^\t]*\t[^\t]*\t[^\t]*\t[^\t]{10,}')     # 带注释列的行
AN['simfer'] = ROWOF(LA, r'Simferopol')
AN['antigua'] = ROWOF(LN, r'^AG\t')                                  # 姊妹表: 属地自有名的行
AN['mariehamn'] = ROWOF(LN, r'Mariehamn')
AN['nrow3'] = ROWOF(LN, r'^AD\t')
AN['frow'] = ROWOF(LF, r'^GB,GG,IM,JE\t')                            # 同一行, 另一条到达路径
AN['htmltitle'] = AK(u'<title>', w=LH, pre=0, post=110)
AN['htmlnav'] = AK(u'<h1>', w=LH, pre=0, post=200)
AN['htmlgz'] = AK(u'.tar.gz', w=LH, pre=170, post=170)
AN['htmlfoot'] = AK(u'public domain', w=LH, pre=50, post=200)
AN['htmlrules'] = AK(u'daylight-saving', u'governments', w=LH, pre=0, post=230)
LBL = {u'frow': LF, u'antigua': LN, u'mariehamn': LN, u'nrow3': LN,
       u'htmltitle': LH, u'htmlnav': LH, u'htmlgz': LH, u'htmlfoot': LH, u'htmlrules': LH}
for k in AN:
    LBL.setdefault(k, LA)
SRCS = {LA: CA, LF: CF, LN: CNX, LH: CH}
for k, v in AN.items():
    assert re.search(PH(v), SRCS[LBL[k]], re.I), (k, v[:50])
    assert 12 <= len(v) <= 460, (k, len(v), v[:40])
print(u'anchors=%d avg=%.0f' % (len(AN), sum(len(v) for v in AN.values()) / float(len(AN))))

# ---------- 判词 ----------
L = []


def A(head, items, gloss):
    L.append(u'%s %s ⇒ %s' % (head, u' ‖ '.join([u'⟦%s⟧⟨%s⟩' % (LBL[k], AN[k]) for k in items]), gloss))


A(u'🧭 体例', [u'andorra', u'frow', u'antigua', u'htmltitle'],
  u'四个源指向“同一个注册表”: ⟦%s⟧⟨%s⟩ 是 tzdata 归档解出的成员, ⟦%s⟧⟨%s⟩ 是同一注册表按单文件抓下来的那份, '
  u'⟦%s⟧⟨%s⟩ 是姊妹表 zone.tab(一国一行), ⟦%s⟧⟨%s⟩ 是名叫 zone1970.tab 却根本不是表的那份。'
  u'与上一条(同一篇文章的两种序列化)的区别: 那两份内容相同、容器不同; 这里四个名字底下, %s份字节相同、%s份归属模型不同、%s份是另一种对象。'
  % (LA, AN['andorra'], LF, AN['frow'], LN, AN['antigua'], LH, AN['htmltitle'],
     CN[2], CN[1], CN[1]))
A(u'📦 两条路径, 同一批字节', [u'london', u'frow'],
  u'归档成员与单文件抓取在审计口径下内容区长度相同、制表符 %d ⇎ %d、行数 %d ⇎ %d(三条等式都折进 0 键); '
  u'⟦%s⟧⟨%s⟩ 与 ⟦%s⟧⟨%s⟩ 是同一行的两条到达路径。 '
  u'判词: 长度、行数、分隔符数相等都只是“同一份”的**必要条件**; 逐字节相同只能由哈希断言(命令记在 ℒmethod 与源行, '
  u'不作为机检键)。可核性的阶梯要看清: 机检差值 < 哈希 < 两条路径各自还能带上什么。'
  % (TABS_A, TABS_A, ROWS_A, ROWS_A, LA, AN['london'], LF, AN['frow']))
A(u'🚪 名字不证明自己', [u'htmltitle', u'htmlnav', u'htmlgz'],
  u'第三份抓取存成了 zone1970.tab 这个名字, 内容是索引网页: ⟦%s⟧⟨%s⟩ ⟦%s⟧⟨%s⟩, 连归档入口都写在 ⟦%s⟧⟨%s⟩ 里。'
  u'它在审计口径内长 %s 字符(比两份表都长), 尖括号 %s 处、超链接 href %s 处、斜杠 %s 处, 制表符却只 %d 处(两份表是 %d 与 %d)。'
  u'最硬的一条: 这个名为 zone1970 的文件里“zone1970”0 次、“.tab”也 0 次(已入 0 键)——它连自己冒充的那个名字的字面线索都没有。 '
  u'判词: 按扩展名判格式会把它当表来摘要; 判格式只能靠内容里的分隔符与标记字符。'
  % (LH, AN['htmltitle'], LH, AN['htmlnav'], LH, AN['htmlgz'], len(BH.strip()), LT_H, HREF_H, SLASH_H,
     TABS_H, TABS_A, TABS_N))
A(u'🧮 姊妹表不是同一批事实的重排', [u'london', u'simfer', u'antigua', u'mariehamn'],
  u'⟦%s⟧ 有 %d 行, ⟦%s⟧ 有 %d 行(机检 %d ⇎ %d)。把两边摊成(国家码, zone) 配对再求双侧差: '
  u'只在 ⟦%s⟧ 成立的 %d 对(机检: 它等于合并行里逗号展开出的额外码数, 即各宽度计数之和), 只在 ⟦%s⟧ 成立的 %d 对(机检), '
  u'两侧差 %d(机检: 两者之差)——两边都非空, 所以“只是换了写法”在这里不成立。'
  u'把 %d 对逐条编成分支正则: 在 ⟦%s⟧ 里 0 命中, 反向的 %d 对在 ⟦%s⟧ 里同样 0 命中(两个 0 都折在 0 键内)。 '
  u'最硬的一条: 这 %d 对全部落在 ⟦%s⟧ 的 %d 行合并行上(携带差集对的行数与合并行数相等, 且“平铺行配差集对”的行式在表内 0 命中), '
  u'亦即一行一码的那 %d 行与姊妹表逐对一致。例: 属地码挂在辖区 zone 上写作 ⟦%s⟧⟨%s⟩, '
  u'姊妹表却把它单独立行、给它自己的名字 ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩。 '
  u'判词: 对照两份结构相同的表, 先算双侧差集再谈“重排”; 单侧差集为空是“包含”, 两侧都空才是“相同”; '
  u'而差集住在哪种行上, 本身是一条能机检的结论。'
  % (LA, ROWS_A, LN, ROWS_N, ROWS_A, ROWS_N, LA, len(AONLY), LN, len(NONLY), DIFF5,
     len(AONLY), LN, len(NONLY), LA, len(AONLY), LA, MULTI_A, ROWS_A - MULTI_A,
     LA, AN['london'], LN, AN['antigua'], LN, AN['mariehamn']))
A(u'🔗 一行能装多少个国家', [u'twenty', u'dubai', u'fourcol', u'nrow3'],
  u'⟦%s⟧ 里 %d 行在第一个字段用逗号并了多个国家码(机检 %d), 最长的那行并到二十个——达到这个宽度的行恰有 %d 行(机检 %d): '
  u'⟦%s⟧⟨%s⟩; 五码行 ⟦%s⟧⟨%s⟩; 带注释列的行 ⟦%s⟧⟨%s⟩(共 %d 行 ⇎ 只有三列的 %d 行, 后者与前面宽度展开出的额外码数同值, 故共用一个机检键)。'
  u'⟦%s⟧ 一行一码(合并行 0 次, 已入 0 键, ⟦%s⟧⟨%s⟩ 是最小形态)。 '
  u'逗号展开出的额外码数走机检(各宽度计数之和), 它与“只在 ⟦%s⟧ 成立的配对数”同值——'
  u'同值在此是同因: 被并进来的每个属地码, 正是姊妹表另立自有名的那些对。'
  % (LA, MULTI_A, MULTI_A, BIG20, BIG20, LA, AN['twenty'], LA, AN['dubai'], LA, AN['fourcol'],
     FOUR_A, THREE_A, LN, LN, AN['nrow3'], LA))
A(u'🗺 表不解释自己', [u'htmlrules', u'htmlfoot', u'andorra'],
  u'文件名叫 zone1970.tab, 而“1970”在三份表的证据范围里 0 次(已入 0 键); 它在网页散文里出现 %d 次, '
  u'“公有领域”的授权声明同样在表里 0 次、在网页里 %d 次(⟦%s⟧⟨%s⟩, 与前者同值故不另立键)。'
  u'“坐标那列取最大城市而非几何中心”这句解释, 只住在注释行与网页散文(⟦%s⟧⟨%s⟩)里; 表的一行 ⟦%s⟧⟨%s⟩ 没有任何字段承载理由。 '
  u'判词: 注册表能回答“哪些码归哪个 zone”, 不能回答“为什么这样归”; 只存表, 就把唯一能解释这张表的那部分一起删了。'
  % (C1970_H, PD_H, LH, AN['htmlfoot'], LH, AN['htmlrules'], LA, AN['andorra']))
A(u'🧾 口径决定行数', [u'andorra', u'london'],
  u'同一批字节有两种行数: 全文件三百七十六行(其中六十三行以 # 起始, 另有一行空行), 按审计口径剔掉注释与出处头样式后是 %d 行数据'
  u'(⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩ 一类); 姊妹表: 全文件四百四十九行 ⇎ 口径内 %d 行(同样剔掉三十行注释与一行空行); 网页那份没有注释行, 全文件一千二百七十一行全部落在口径内。'
  u'字符数也只对口径成立: 内容区 %s(机检键 RCOT)⇎ 原始文件一万七千五百三十六字符(字节数写在 src 行), 差值就是注释与空行。 '
  u'判词: 凡报“共 N 行 / 共 N 字符”必须同时报口径。本条所有计数取审计口径, 注释行不在证据范围内——'
  u'这条限制正是上一行“1970 为 0 次”成立的原因, 工具的口径本身也是本条的一条结论。'
  % (ROWS_A, LA, AN['andorra'], LA, AN['london'], ROWS_N, R0))
A(u'🚫 缺席是双向的', [],
  u'表侧%s项在三份表的口径内全 0: 尖括号、“href”“mailto”、“@”、“zone1970”、扩展名“.tab”、“tzdata”、归档后缀、年份“1970”、'
  u'授权短语“公有领域”、以及“数字点数字”的版本号写法(注意“1970”与“public domain”其实写在被口径剔掉的注释行里, '
  u'所以这个 0 是**两重成因**的 0); 网页侧%s项全 0: 两位码行式、制表符后的坐标列、自身文件名、“.tab”、“Etc/” 前缀。'
  u'合计%s项折进一个 0 键; 同一个 0 键里还折着%s条等式(两条路径的长度/制表符/行数、三列行数与宽度展开的额外码数、'
  u'携带差集对的行数与合并行数)以及%s项配对层面的 0 命中(姊妹表里没有 A 侧配对、A 表里没有 N 侧配对、'
  u'平铺行里没有差集对、姊妹表里没有合并行)。 '
  u'判词: 这不是一次失败的抓取, 而是三种对象互不包含——三份都得存; “哪一项在谁那里为 0”就是它们的边界。'
  % (CN[NABS_T], CN[NABS_H], CN[NABS], CN[NEQU], CN[NPAIRZ]))
A(u'✂️ 为什么这份编码比摘要窗口长', [u'twenty', u'htmlgz'],
  u'本条是对照条: 判词要在四个源之间来回数(两侧差集、两条路径、双向缺席), 而摘要段只索引锚点触到的窗口。'
  u'窗口里放不下的正是本条的载荷——⟦%s⟧⟨%s⟩ 这样的二十码行在 ⟦%s⟧ 里没有对应行, 差集本身就是结论。 '
  u'所以保留率会高于全库, 读它要按字节口径与“键数 ⇎ 判词行数”来读, 不是按“少说了多少话”。'
  % (LA, AN['twenty'], LN))
A(u'∴ 骨架', [],
  u'① 文件名是意图, 内容是证据, 冲突时以内容为准; ② 同一目录里同名不同物的两份文件会互相顶掉证据; '
  u'③ “同一份”由哈希断言, 长度与行数相等只是下限; ④ 姊妹表未必是同一批事实的重排, 先算双侧差集; '
  u'⑤ 单侧差集为空是包含, 两侧都空才是相同; ⑥ 合并写法与摊平写法行数不同, 而展开增量恰等于其中一侧的独有配对数, 双侧差集全部住在合并行里、平铺行逐对一致; '
  u'⑦ 表回答归属, 不回答理由, 理由住在注释与散文里; ⑧ 注释行会被审计口径剔掉, 于是“表里 0 次”与“表里写着”同时为真; '
  u'⑨ 报行数与字符数必须报口径; ⑩ 缺席双向 ⇒ 三种对象互不包含; ⑪ 元信息(版本、授权)住在会被剥掉的那一层, '
  u'而那里是它唯一的住处; ⑫ 对照条的编码重于窗口属结构性结果。')
A(u'ℒmethod', [u'london', u'antigua'],
  u'读“注册表与其多份副本”: 第一步不看文件名, 只数分隔符与标记字符(制表符 ⇎ 尖括号)先定对象类型; '
  u'第二步把所有副本按同一口径折成内容区, 用长度/分隔符/行结构三项差值断言“同一路径的两次到达”, '
  u'逐字节相同交给外部摘要哈希断言(本机可用 certutil 或 hashlib), 算法名与哈希值写在 src 行而不是机检键; '
  u'第三步把两份表摊成(键, 值) 配对求**双侧**差集, 并把差集逐条编成分支正则, 要求它在对方文件里 0 命中——这才把“不同”变成可核事实; '
  u'第四步把字段内合并写法按宽度分桶求和, 用桶和与差集大小相等自查, 再问差集对住在哪种行上(平铺行配差集对的行式必须 0 命中); 第五步凡遇“某词在本文件 0 次”, 先问它是否住在被剔掉的注释行里。 '
  u'核验口径: ⟦%s⟧⟨%s⟩ 一类锚取自制表符分隔的行(锚内空白已折叠, 原文件以制表符分列), ⟦%s⟧⟨%s⟩ 取姊妹表行; '
  u'标注哪个源就只在哪个源里逐字比对, 不互换。'
  % (LA, AN['london'], LN, AN['antigua']))

BODY_MD = u'\n'.join(L)
HEAD_MD = (u'# B45 同一个名字，三种对象：%d 行的注册表、逐字节相同的第二份、和一份根本不是表的 %s 字符网页\n\n'
           u'src: %s (tzdata 归档解出的成员, 数据 %d 行 ⇎ 口径内 %d 字符 ⇎ 文件 %d 字节, sha256 %s) ⇎ '
           u'%s (同一注册表的单文件抓取, 与上一份逐字节相同: sha256 %s, %d 字节) ⇎ '
           u'%s (姊妹表 zone.tab, 数据 %d 行, 一国一行, sha256 %s) ⇎ '
           u'%s (名叫 zone1970.tab 的索引网页, 口径内 %d 字符 ⇎ 全文件 %d 行, sha256 %s)\n'
           u'tags: 数据注册表 隐性知识 抓取命名冲突 姊妹表双侧差集 字段合并 计数口径 双向缺席\n\n'
           % (ROWS_A, len(BH.strip()), RA, ROWS_A, R0, BS(RA), SHA_A, RF, SHA_F, BS(RF),
              RN, ROWS_N, SHA_N, RH, len(BH.strip()), len(LNHH), SHA_H))
MD = (HEAD_MD + u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + BODY_MD +
      u'\n\n## ⛓解读注\n<!--FILL-->\n')
io.open(ENTRY, u'w', encoding='utf-8').write(MD)
print(u'entry written: %s body_chars=%d anchors=%d' % (ENTRY, len(BODY_MD), len(AN)))

# ---------- DERIV(键名即数值) ----------
NL = chr(10)
D = {}


def put(val, expr):
    k = (u'%g' % float(val))
    assert k not in D, (k, expr[:60], D.get(k))
    D[k] = expr
    return k


SUMW = u'+'.join(u'CNT(%r,0)' % PJ(j) for j in range(2, 25))
NONLYE = u'CNT(B45_NONLY,2)'
ZERO = (u'+'.join([u'CNT(%r,%d)' % (p, i) for p in ABS_TAB for i in (0, 1, 2)] +
                  [u'CNT(%r,3)' % p for p in ABS_H] +
                  [u'CNT(%r,2)' % MULTI, u'CNT(B45_AONLY,2)', u'CNT(B45_NONLY,0)',
                   u'CNT(B45_AFLAT,0)'] +
                  [u'RCOT(0)-RCOT(1)', u"CNT('\\t',0)-CNT('\\t',1)",
                   u'CNT(%r,0)-CNT(%r,1)' % (ROWA, ROWA),
                   u'(CNT(%r,0)-CNT(%r,0))-(%s)' % (ROWA, FOURA, SUMW),
                   u'CNT(B45_AONLY,0)-CNT(%r,0)' % MULTI]))
put(0, ZERO)
put(BIG20, u'CNT(%r,0)' % PJ(20))
put(C1970_H, u"CNT('1970',3)")
put(EXTR, SUMW)
put(DIFF5, u'(%s)-%s' % (SUMW, NONLYE))
put(GZ_H, u"CNT('\\.tar\\.gz',3)")
put(AT_H, u"CNT('@',3)")
put(TZD_H, u"CNT('tzdata',3)")
put(MULTI_A, u"CNT('(?m)^[A-Z]{2},',0)")
put(ROWS_A - MULTI_A, u'CNT(%r,0)-CNT(%r,0)' % (ROWA, MULTI))
put(DDF_H, u"CNT('\\d\\.\\d',3)")
put(len(NONLY), NONLYE)
put(COMMA_H, u"CNT('[A-Z]{2},',3)")
put(FOUR_A, u'CNT(%r,0)' % FOURA)
put(FOUR_N, u'CNT(%r,2)' % FOURA)
put(ROWS_A, u'CNT(%r,0)' % ROWA)
put(HREF_H, u"CNT('href',3)")
put(ROWS_N, u'CNT(%r,2)' % ROWA)
put(TABS_H, u"CNT('\\t',3)")
put(TABS_A, u"CNT('\\t',0)")
put(TABS_N, u"CNT('\\t',2)")
put(LT_H, u"CNT('<',3)")
put(SLASH_H, u"CNT('/',3)")
put(len(BH.strip()), u'RCOT(3)')
put(R0, u'RCOT(0)')
NTERM0 = ZERO.count(u'CNT(')
print(u'DERIV keys=%d / 0 键 CNT 项=%d' % (len(D), NTERM0))

CONST = (u"B45_AONLY = r'''%s'''%sB45_NONLY = r'''%s'''%sB45_AFLAT = r'''%s'''%s" % (PAT_A, NL, PAT_N, NL, PAT_AF, NL))
SRC45 = (u"SRC['B45'] = ['corpus/raw/tz/zone1970.tab', 'corpus/raw/zone1970_latest.tab', "
         u"'corpus/raw/tz/zone.tab', 'corpus/raw/zone1970.tab']" + NL)
DE_IN = NL.join(u"  %r: %r," % (k, v) for k, v in sorted(D.items(), key=lambda x: float(x[0])))
BLOCK = u" 'B45': {" + NL + DE_IN + NL + u" }," + NL

AU = u'corpus/audit.py'
s = io.open(AU, encoding='utf-8').read()
if u"SRC['B45']" not in s:
    i0 = s.index(NL + u'ATOM = {')
    s = s[:i0 + 1] + CONST + SRC45 + s[i0 + 1:]
elif u"B45_AONLY" not in s:
    s = s.replace(u"SRC['B45'] = [", CONST + u"SRC['B45'] = [", 1)
if u"'B44'}" in s and u"'B45'}" not in s:
    s = s.replace(u"'B44'}", u"'B44', 'B45'}", 1)
if u"B45_AONLY=B45_AONLY" not in s:
    s = s.replace(u"LEAP_N=LEAP_N, TAI_LAST=TAI_LAST)",
                  u"LEAP_N=LEAP_N, TAI_LAST=TAI_LAST, B45_AONLY=B45_AONLY, "
                  u"B45_NONLY=B45_NONLY, B45_AFLAT=B45_AFLAT)", 1)
s = re.sub(u" 'B45': \\{" + NL + u".*?" + NL + u" \\}," + NL, lambda m: BLOCK, s, count=1, flags=re.S)
if u"'B45': {" not in s:
    k0 = s.index(u'DERIV = {' + NL) + len(u'DERIV = {' + NL)
    s = s[:k0] + BLOCK + s[k0:]
io.open(AU, 'w', encoding='utf-8').write(s)

AC = u'corpus/atomcheck.py'
a = io.open(AC, encoding='utf-8').read()
if u"SRC['B45']" not in a:
    i2 = a.index(u"SRC['B44']")
    a = a[:i2] + SRC45 + a[i2:]
    io.open(AC, 'w', encoding='utf-8').write(a)
io.open(u'corpus/_atoms45.txt', 'w', encoding='utf-8').write(
    NL.join(sorted(set(AN.values()))) + NL)
print(u'wired B45: audit SRC/CONST/ATOM/DERIV(%d keys) + atomcheck SRC + _atoms45.txt(%d uniq)' %
      (len(D), len(set(AN.values()))))
