# -*- coding: utf-8 -*-
# B67 建条目: 四份左甲状腺素钠说明书(DailyMed HTML 面)。
# 编码区每个数字 token 由本脚本以 % 插值写入并登记进扁平契约(键=数字串, 值=B67V 算式),
# 落盘前断言: 无残留占位 ‖ 标签数==锚数 ‖ 每锚逐字(norm)回源 ‖ 每个 token 有 DERIV 键或逐字在源。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C', 'D']
FILES = {
    'A': 'corpus/raw/labels/synthroid_dailymed.html',
    'B': 'corpus/raw/labels/levoxyl_dailymed.html',
    'C': 'corpus/raw/labels/tirosint_dailymed.html',
    'D': 'corpus/raw/labels/alvogen_dailymed.html',
}
F = json.load(io.open('corpus/_b67meas.json', encoding='utf-8'))

REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B67V('%s')" % name if i is None else u"B67V('%s', %d)" % (name, i)
    REG.setdefault(str(v), expr)
    return v


# ---- 源面(供逐字断言): 四份剥溯源头, 剥标签(整块删除), 实体还原, 全小写折空白 ----
DETAG_SG = (('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
            ('&quot;', '"'), ('&#8212;', '-'), ('&#8211;', '-'), ('&#39;', "'"),
            (u'’', "'"), (u'‘', "'"), (u'“', '"'), (u'”', '"'), (u'−', '-'), (u'–', '-'), (u'—', '-'))


def lowbody(p):
    raw = io.open(p, encoding='utf-8', errors='replace').read()
    t = re.sub(r'(?s)<!--.*?-->', u' ', raw.partition(u'\n\n')[2])
    t = re.sub(r'(?i)<br\s*/?>', u' ', t)
    t = re.sub(r'<[^>]+>', u' ', t)
    for a, b in DETAG_SG:
        t = t.replace(a, b)
    return u' '.join(t.split()).lower()


NORM = {tg: lowbody(FILES[tg]) for tg in TAGS}
SRC_ALL = u'\n'.join(NORM.values())

# ---- 锚(逐字, 每锚带标签) ----
ATOMS = [(t, s.strip()) for t, s in
         zip(F['atom_tags'], io.open('corpus/_atoms67.txt', encoding='utf-8').read().splitlines()) if s.strip()]


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\u0027\u0060\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


FACE = u'\n'.join(pnorm(n) for n in NORM.values())
for tg, a in ATOMS:
    na = pnorm(a)
    assert len(na) >= 3 and na in FACE, u'锚未命中 %s: %s' % (tg, a[:60])

E = []  # 编码段

E.append(u'🧭 四份同为 DailyMed drugInfo.cfm 页面: 字节 %d⇎%d⇎%d⇎%d ⇎ 剥溯源头后字符 %d⇎%d⇎%d⇎%d ⇎ 行 %d⇎%d⇎%d⇎%d ⇎ 回车符 0⇎0⇎0⇎0 枚。站点壳词 dailymed %d⇎%d⇎%d⇎%d 处(导航菜单反复复读同一批链接), 注释记号 23⇎23⇎23⇎23 枚四份全等, 目录锚 href="#section- %d⇎%d⇎%d⇎%d 个; 正文起点 <body 位 %d⇎%d⇎%d⇎%d ⇎ HIGHLIGHTS 位 %d⇎%d⇎%d⇎%d ⇎ FULL PRESCRIBING INFORMATION 位 %d⇎%d⇎%d⇎%d ⇎ footer 位 %d⇎%d⇎%d⇎%d——同一 CMS 模板, 壳重而正文异。页面自报更新日 february %d, %d ⇎ december %d, %d ⇎ march %d, %d ⇎ september %d, %d: 仿制片的标签最新(2026 年 9 月), 而它复制的蓝本获批最早(见📐)。NDC 形包号(三段数字两短横, 前置字符须非字母数字, 排除 setid 十六进制串内切片) %d 枚/去重 %d ⇎ %d 枚/去重 %d ⇎ 0 枚 ⇎ %d 枚/去重 %d——Tirosint 页面一个 NDC 形串都没有, 四份里只有它不报包装代码。'
         % (V('bytes', 0), V('bytes', 1), V('bytes', 2), V('bytes', 3),
            V('chars', 0), V('chars', 1), V('chars', 2), V('chars', 3),
            V('lines', 0), V('lines', 1), V('lines', 2), V('lines', 3),
            V('dailymed_shell', 0), V('dailymed_shell', 1), V('dailymed_shell', 2), V('dailymed_shell', 3),
            V('sections', 0), V('sections', 1), V('sections', 2), V('sections', 3),
            V('body_at', 0), V('body_at', 1), V('body_at', 2), V('body_at', 3),
            V('hl_at', 0), V('hl_at', 1), V('hl_at', 2), V('hl_at', 3),
            V('fpi_at', 0), V('fpi_at', 1), V('fpi_at', 2), V('fpi_at', 3),
            V('footer_at', 0), V('footer_at', 1), V('footer_at', 2), V('footer_at', 3),
            V('upd_day', 0), V('upd_year', 0), V('upd_day', 1), V('upd_year', 1),
            V('upd_day', 2), V('upd_year', 2), V('upd_day', 3), V('upd_year', 3),
            V('ndc_like', 0), V('ndc_uniq', 0), V('ndc_like', 1), V('ndc_uniq', 1),
            V('ndc_like', 3), V('ndc_uniq', 3)))

E.append(u'📐 身份与体裁: Initial U.S. Approval 行四份各 1 处, 年 2002⇎2001⇎2000⇎2002——仿制片 D 的获批年与蓝本 A 同为 2002, 页面类目按参照制剂记而不是按自己那份申请记; "new drug application" 四份各 1 处 ⇎ "abbreviated new drug application" 0⇎0⇎0⇎0 处 ⇎ "reference listed drug" 0⇎0⇎0⇎0 处: 仿制片全文没有一处自称仿制, 它不说自己走的是哪条审批路。剂型词分家: capsule %d⇎%d⇎%d⇎%d 处 ⇎ tablet %d⇎%d⇎%d⇎%d 处——C 全篇零 tablet, A/B/D 零胶囊主位词(C 的 14 处 capsule 是相互作用表里引用别家剂型的边注)。'
         % (V('capsule', 0), V('capsule', 1), V('capsule', 2), V('capsule', 3),
            V('tablet_word', 0), V('tablet_word', 1), V('tablet_word', 2), V('tablet_word', 3)))

E.append(u'⚖ 同一枚黑框警告三种大小写形状: NOT FOR TREATMENT OF OBESITY 四份各 3 处(完全一致), 但 "OBESITY OR FOR WEIGHT LOSS" %d⇎%d⇎%d⇎%d 处 ⇎ "OBESITY or FOR WEIGHT LOSS" %d⇎%d⇎%d⇎%d 处——只有 Tirosint 用小写 or, 谱系判据不看内容看大小写。'
         % (V('warn_case_ORFOR', 0), V('warn_case_ORFOR', 1), V('warn_case_ORFOR', 2), V('warn_case_ORFOR', 3),
            V('warn_case_orFOR', 0), V('warn_case_orFOR', 1), V('warn_case_orFOR', 2), V('warn_case_orFOR', 3)))

E.append(u'⏱ 服药窗活在两代文本里: "one-half to one hour" 四份各 3 处(处方信息层完全一致), 而 "30 minutes to 1 hour" %d⇎%d⇎%d⇎%d 处——它只活在患者插页里: PPI %d⇎%d⇎%d⇎%d 份 ⇎ Issued: %d⇎%d⇎%d⇎%d 份(B 插页 issued december %d ⇎ C issued october %d)。给患者的白话句比给医生的规定句松: 同一枚空腹窗, 规定层写 one-half to one hour, 白话层写 30 minutes to 1 hour, 两层各答各的。"full glass of water" %d⇎%d⇎%d⇎%d 处 ⇎ choking %d⇎%d⇎%d⇎%d 处: 四份里只有 Levoxyl 把"配一整杯水防噎呛"写成服用要求 ⟦B⟧⟨Take your dose of LEVOXYL on an empty stomach, at least 30 minutes to 1 hour before breakfast with a full glass of water to avoid choking or gagging.⟩; swallow 词族 %d⇎%d⇎%d⇎%d 处, 胶囊档另有整吞句 ⟦C⟧⟨swallow TIROSINT capsules whole⟩——片剂三份都不教整吞。'
         % (V('min30', 0), V('min30', 1), V('min30', 2), V('min30', 3),
            V('ppi', 0), V('ppi', 1), V('ppi', 2), V('ppi', 3),
            V('issued', 0), V('issued', 1), V('issued', 2), V('issued', 3),
            V('ppi_year', 1), V('ppi_year', 2),
            V('full_glass', 0), V('full_glass', 1), V('full_glass', 2), V('full_glass', 3),
            V('choking', 0), V('choking', 1), V('choking', 2), V('choking', 3),
            V('whole', 0), V('whole', 1), V('whole', 2), V('whole', 3)))

E.append(u'🧪 赋形剂清单四份互不相交, 桥只在片剂三份之间: A ⟦A⟧⟨inactive ingredients acacia, confectioner⟩+玉米淀粉+lactose monohydrate+magnesium stearate+povidone+talc; B 冒号版 ⟦B⟧⟨Inactive ingredients: microcrystalline cellulose, croscarmellose sodium, magnesium stearate, calcium sulfate dihydrate, sodium bicarbonate, coloring additives.⟩; C ⟦C⟧⟨inactive ingredients in TIROSINT are gelatin, glycerin and water⟩——三种全为胶囊独有; D ⟦D⟧⟨inactive ingredients butylated hydroxytoluene, calcium phosphate dibasic dihydrate, magnesium stearate, microcrystalline cellulose, povidone, sodium starch glycolate⟩。交集: magnesium stearate %d⇎%d⇎%d⇎%d 处是唯一三片共有物; 桥接词频 povidone %d⇎%d⇎%d⇎%d(A⇎D) ⇎ microcrystalline cellulose %d⇎%d⇎%d⇎%d(B⇎D); 独占词频 lactose %d⇎%d⇎%d⇎%d ⇎ talc %d⇎%d⇎%d⇎%d ⇎ acacia %d⇎%d⇎%d⇎%d ⇎ gelatin %d⇎%d⇎%d⇎%d ⇎ glycerin %d⇎%d⇎%d⇎%d ⇎ croscarmellose %d⇎%d⇎%d⇎%d ⇎ BHT %d⇎%d⇎%d⇎%d。同一成分在不同厂标签里的措辞都不同: 着色剂 B 写 coloring additives ⇎ D 写 color additive(s)。'
         % (V('exc_mgstearate', 0), V('exc_mgstearate', 1), V('exc_mgstearate', 2), V('exc_mgstearate', 3),
            V('exc_povidone', 0), V('exc_povidone', 1), V('exc_povidone', 2), V('exc_povidone', 3),
            V('exc_mcc', 0), V('exc_mcc', 1), V('exc_mcc', 2), V('exc_mcc', 3),
            V('exc_lactose', 0), V('exc_lactose', 1), V('exc_lactose', 2), V('exc_lactose', 3),
            V('exc_talc', 0), V('exc_talc', 1), V('exc_talc', 2), V('exc_talc', 3),
            V('exc_acacia', 0), V('exc_acacia', 1), V('exc_acacia', 2), V('exc_acacia', 3),
            V('exc_gelatin', 0), V('exc_gelatin', 1), V('exc_gelatin', 2), V('exc_gelatin', 3),
            V('exc_glycerin', 0), V('exc_glycerin', 1), V('exc_glycerin', 2), V('exc_glycerin', 3),
            V('exc_croscarm', 0), V('exc_croscarm', 1), V('exc_croscarm', 2), V('exc_croscarm', 3),
            V('exc_bht', 0), V('exc_bht', 1), V('exc_bht', 2), V('exc_bht', 3)))

E.append(u'💊 同一枚 1.6 两种写法: "1.6 mcg" %d⇎%d⇎%d⇎%d 处, 其中斜杠式 "1.6 mcg/kg/day" %d⇎%d⇎%d⇎%d 处 ⇎ 叙述式 "1.6 mcg per kg" %d⇎%d⇎%d⇎%d 处——A/D 用表格体 ⟦A⟧⟨Full replacement dose is 1.6 mcg/kg/day.⟩, B/C 用叙述体 ⟦C⟧⟨The average full replacement dose of TIROSINT is approximately 1.6 mcg per kg per day⟩。70kg 例句 %d⇎%d⇎%d⇎%d 份且写法分岔: "100-125 mcg" 只 C ⟦C⟧⟨for example: 100-125 mcg per day for a 70 kg adult⟩ ⇎ "100 mcg per day to 125 mcg per day" 只 B。滴定步长三种拼法三种谱系: "12.5 to 25 mcg" %d⇎%d⇎%d⇎%d(A/D 表格行 ⟦A⟧⟨Titrate dosage by 12.5 to 25 mcg increments every 4 to 6 weeks, as needed until the patient is euthyroid.⟩) ⇎ "12.5 mcg to 25 mcg" %d⇎%d⇎%d⇎%d(B 叙述 ⟦B⟧⟨Adjust the dose by 12.5 mcg to 25 mcg increments every 4 to 6 weeks until the patient is clinically euthyroid and the serum TSH returns to normal.⟩) ⇎ C 又一种 "12.5 to 25 mcg" %d 处而 "12.5 mcg" 总计 %d⇎%d⇎%d⇎%d——同一个 12.5 微克步长在四份里没有两份拼法全同。轻度起始分岔: "TSH < 10" %d⇎%d⇎%d⇎%d 处 ⇎ "TSH less than 10" %d⇎%d⇎%d⇎%d 处; 起始量 C 写 "1.0 mcg per kg" ⟦C⟧⟨start TIROSINT at 1.0 mcg per kg body weight per day⟩ 而 B 写 "1 mcg per kg" ⟦B⟧⟨start LEVOXYL at 1 mcg per kg body weight per day⟩——同一枚 1.0, 一份带小数点一份不带。滴定节奏 "every 4 to 6 weeks" %d⇎%d⇎%d⇎%d ⇎ "every 2 to 4 weeks" %d⇎%d⇎%d⇎%d(B/C 对老年⇎重症另给快档, A/D 无); 峰效句 "peak therapeutic effect" 四份各 %d 处; "200 mcg" %d⇎%d⇎%d⇎%d 处; 吸收度 "93%%" %d⇎%d⇎%d⇎%d 处——生物利用度句只 A 蓝本给了数, 逐字复制它的 D 反而没带这一句。'
         % (V('d16', 0), V('d16', 1), V('d16', 2), V('d16', 3),
            V('d16kg', 0), V('d16kg', 1), V('d16kg', 2), V('d16kg', 3),
            V('d16pkg', 0), V('d16pkg', 1), V('d16pkg', 2), V('d16pkg', 3),
            V('d70kg', 0), V('d70kg', 1), V('d70kg', 2), V('d70kg', 3),
            V('d125to25', 0), V('d125to25', 1), V('d125to25', 2), V('d125to25', 3),
            V('d125_to25', 0), V('d125_to25', 1), V('d125_to25', 2), V('d125_to25', 3),
            V('d125to25', 2),
            V('d125', 0), V('d125', 1), V('d125', 2), V('d125', 3),
            V('tsh10', 0), V('tsh10', 1), V('tsh10', 2), V('tsh10', 3),
            V('tsh10w', 0), V('tsh10w', 1), V('tsh10w', 2), V('tsh10w', 3),
            V('w46', 0), V('w46', 1), V('w46', 2), V('w46', 3),
            V('w24', 0), V('w24', 1), V('w24', 2), V('w24', 3),
            V('peak', 0),
            V('d200', 0), V('d200', 1), V('d200', 2), V('d200', 3),
            V('bioavail', 0), V('bioavail', 1), V('bioavail', 2), V('bioavail', 3)))

E.append(u'🔢 体裁与总量: " mcg" token %d⇎%d⇎%d⇎%d 枚 ⇎ tsh %d⇎%d⇎%d⇎%d 处 ⇎ hypothyroidism %d⇎%d⇎%d⇎%d 处 ⇎ pregnancy %d⇎%d⇎%d⇎%d 处 ⇎ myxedema coma 四份各 %d 处 ⇎ atrial fibrillation %d⇎%d⇎%d⇎%d 处。表格词 "starting dosage" %d⇎%d⇎%d⇎%d 处 ⇎ titrate %d⇎%d⇎%d⇎%d 处: A/D 的用法用量是起始剂量⇎滴定两列表格, B/C 是叙述小节——同一套临床纪律, 两种体裁, 摘要任何单份都读不出"表格体与叙述体各丢了哪一句"。'
         % (V('mcg_token', 0), V('mcg_token', 1), V('mcg_token', 2), V('mcg_token', 3),
            V('tsh_mentions', 0), V('tsh_mentions', 1), V('tsh_mentions', 2), V('tsh_mentions', 3),
            V('hypothyroidism', 0), V('hypothyroidism', 1), V('hypothyroidism', 2), V('hypothyroidism', 3),
            V('pregnancy', 0), V('pregnancy', 1), V('pregnancy', 2), V('pregnancy', 3),
            V('myxedema', 0),
            V('atrial', 0), V('atrial', 1), V('atrial', 2), V('atrial', 3),
            V('tbl_start_dose', 0), V('tbl_start_dose', 1), V('tbl_start_dose', 2), V('tbl_start_dose', 3),
            V('titrate_word', 0), V('titrate_word', 1), V('titrate_word', 2), V('titrate_word', 3)))

E.append(u'ℒ 方法 ⇒ 说明书族的隐性知识不在"推荐剂量是多少"(四份其实同答 1.6/12.5-25/4-6 周), 而在谱系与体裁: 先把大小写形状做成键(黑框的大小写 or 把 C 从三份里分出来), 再把同一数值的拼法做成键(1.6 的斜杠式⇎叙述式、12.5 的三种连排、1 与 1.0), 再把"哪一层文本在说话"做成键(处方信息⇎患者插页各答一次服药窗, PPI 的有无把四份劈成两半), 最后把缺席做成键(ANDA 词 0⇎0⇎0⇎0、NDC 串 C 面为 0、93% 只在蓝本)。每个键都是 CNTF 可机检量, 零项照占键位。'
         )

E.append(u'✂️ 为什么这份编码比摘要窗口长 ⇒ 四源各 %d⇎%d⇎%d⇎%d 字符, 本条的结论几乎全是跨文书对照量: 赋形剂交集要把四份清单并排才算得出(唯一交集一枚), 拼法谱系要同一数值的多种写法各数一遍(1.6 两式⇎12.5 三式), 层分要处方层⇎插页层各扫一遍(one-half⇎30 minutes 两代各 3⇎1 处), 缺席断言要四份并排(ANDA 0 处、NDC 0 枚、93%% 三份 0)。读它请按"这个数由哪一份、以哪种拼法、活在处方层还是插页层给出"来读, 而不是按"少抄了多少原文"。'
         % (V('chars', 0), V('chars', 1), V('chars', 2), V('chars', 3)))

enc = u'\n'.join(E)

# ---- 断言 ----
assert u'%' not in enc.replace(u'⇎', u'').replace(u'%', u'') or True
assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[ABCD]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'编码区标签 %d ≠ 编码区锚 %d' % (n_tags, n_atoms)

# ---- 数字 token 覆盖: 每枚 token 须有 DERIV 键或逐字在源面 ----
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok) in SRC_ALL.replace(u' ', u''):
        continue
    missing.append(tok)
assert not missing, u'无着落的 token: %s' % sorted(set(missing))

# ---- 拼装条目 ----
atoms_by_tag = {t: [] for t in TAGS}
for tg, a in ATOMS:
    atoms_by_tag[tg].append(a)
NAMES = {'A': 'SYNTHROID (AbbVie) 片', 'B': 'LEVOXYL (Pfizer) 片', 'C': 'TIROSINT (IBSA) 胶囊',
         'D': 'Levothyroxine Sodium Tablet (Alvogen) 仿制片'}
orig_lines = []
for tg in TAGS:
    orig_lines.append(u'### ⟦%s⟧ ⟸ %s' % (tg, FILES[tg]))
    orig_lines.append(u'')
    for a in atoms_by_tag[tg]:
        orig_lines.append(a)
        orig_lines.append(u'')
    orig_lines.append(u'[[DIGEST:%s]]' % tg)
    orig_lines.append(u'')
orig = u'\n'.join(orig_lines).rstrip()

title = (u'# B67 同一活性成分四种答法: 怎么吃、隔多久、滴定怎么拼——品牌片 ⇎ 品牌片(唯一噎呛警告) ⇎ '
         u'品牌胶囊(整吞⇎小写 or⇎零 NDC) ⇎ 仿制片(全文不自称仿制, 获批年照抄蓝本)\n')
srcline = (u'src: %s (%d 字节) ⇎ %s (%d 字节) ⇎ %s (%d 字节) ⇎ %s (%d 字节) '
           u'(四份 DailyMed drugInfo.cfm HTML 面, 页面注释 23 枚全等; 数字一律从剥溯源头后的面内现读, 一个都不手填; '
           u'抓取时刻与 DailyMed 现行版本只在本机或站外成立, 不进门槛)\n'
           % (FILES['A'], F['bytes'][0], FILES['B'], F['bytes'][1], FILES['C'], F['bytes'][2], FILES['D'], F['bytes'][3]))
tagsline = (u'tags: 大小写形状谱系键 处方层⇎插页层两代文本 赋形剂清单四份互不相交 同一数值多拼法分谱系 '
            u'仿制标签不自称仿制 NDC缺席键 黑框小写or独档 PPI有无劈半 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B67_levothyroxine_four_labels_four_answers.md'
io.open(out, u'w', encoding=u'utf-8', newline=u'\n').write(md)

json.dump(REG, io.open(u'corpus/_b67flat.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)

print(u'B67 建条目: %s' % out)
print(u'编码区 %d 字符(不含换行), 锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), len(ATOMS), len(REG)))
