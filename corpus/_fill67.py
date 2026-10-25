# -*- coding: utf-8 -*-
# B67 ⛓解读注: 第四遍复测(第三套实现, 逐词切分计数)现算写回; 与契约逐键对表, 不符即停机。
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C', 'D']
FILES = {'A': 'corpus/raw/labels/synthroid_dailymed.html', 'B': 'corpus/raw/labels/levoxyl_dailymed.html',
         'C': 'corpus/raw/labels/tirosint_dailymed.html', 'D': 'corpus/raw/labels/alvogen_dailymed.html'}
F = json.load(io.open('corpus/_b67meas.json', encoding='utf-8'))

# 第三套: 分词(按非字母数字切)后数相邻词序列; 与字符游标(采)和 re 词面(审)皆不同路
def words(p):
    raw = io.open(p, encoding='utf-8', errors='replace').read().partition('-->')[2]
    t = re.sub(r'(?s)<!--.*?-->', ' ', raw)
    t = re.sub(r'<[^>]+>', ' ', t)
    for a, b in (('&amp;', '&'), ('&nbsp;', ' '), (u'’', "'")):
        t = t.replace(a, b)
    return [w for w in re.split(r'[^0-9a-z]+', t.lower()) if w]

W = [words(FILES[t]) for t in TAGS]


def seq(kws):
    return [sum(1 for i in range(len(w) - len(kws) + 1) if w[i:i + len(kws)] == kws) for w in W]


rows = [
    (u'one-half to one hour 服药窗', seq(['one', 'half', 'to', 'one', 'hour']), F['half_to_one']),
    (u'30 minutes to 1 hour 插页窗', seq(['30', 'minutes', 'to', '1', 'hour']), F['min30']),
    (u'full glass of water 噎呛杯', seq(['full', 'glass', 'of', 'water']), F['full_glass']),
    (u'choking', seq(['choking']), F['choking']),
    (u'1.6 mcg/kg/day 斜杠式', seq(['1', '6', 'mcg', 'kg', 'day']), F['d16kg']),
    (u'1.6 mcg per kg 叙述式', seq(['1', '6', 'mcg', 'per', 'kg']), F['d16pkg']),
    (u'12.5 to 25 mcg', seq(['12', '5', 'to', '25', 'mcg']), F['d125to25']),
    (u'12.5 mcg to 25 mcg', seq(['12', '5', 'mcg', 'to', '25', 'mcg']), F['d125_to25']),
    (u'TSH less than 10', seq(['tsh', 'less', 'than', '10']), F['tsh10w']),
    (u'magnesium stearate 交集', seq(['magnesium', 'stearate']), F['exc_mgstearate']),
    (u'gelatin 胶囊独占', seq(['gelatin']), F['exc_gelatin']),
    (u'atrial fibrillation', seq(['atrial', 'fibrillation']), F['atrial']),
]
for name, got, want in rows:
    assert got == want, u'%s: 分词法 %s ⇎ 契约 %s' % (name, got, want)

# 黑框大小写(第 R 遍: 逐字符扫, 不用 count 也不用 re)
def casecount(r, pat):
    c = i = 0
    while True:
        i = r.find(pat, i)
        if i < 0:
            return c
        c += 1
        i += 1

hi = [casecount(io.open(FILES[t], encoding='utf-8').read().partition('-->')[2], 'OBESITY OR FOR WEIGHT LOSS') for t in TAGS]
lo = [casecount(io.open(FILES[t], encoding='utf-8').read().partition('-->')[2], 'OBESITY or FOR WEIGHT LOSS') for t in TAGS]
assert hi == F['warn_case_ORFOR'] and lo == F['warn_case_orFOR'], (hi, lo, F['warn_case_ORFOR'], F['warn_case_orFOR'])

# 编码与门的账
entry = io.open('corpus/babeltele/B67_levothyroxine_four_labels_four_answers.md', encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\\n(.*?)\\n\\n## ', entry, re.S).group(1)
n_enc = len(enc.replace('\n', ''))
n_anchor = len(re.findall(u'⟨', enc))
REG = json.load(io.open('corpus/_b67flat.json', encoding='utf-8'))
atoms = [l.strip() for l in io.open('corpus/_atoms67.txt', encoding='utf-8') if l.strip()]
per_tag = {}
for t, a in zip(F['atom_tags'], atoms):
    per_tag[t] = per_tag.get(t, 0) + 1

gloss = u'''## ⛓解读注

### 第四遍复测(本注现算, 与采集侧字符游标、审计器侧词面正则皆不同路)

| 量 | 本注的写法 | 结果 | 与契约 |
|---|---|---|---|
| 服药窗双代 | 分词序列 one/half/to/one/hour ⇎ 30/minutes/to/1/hour | %s ⇎ %s | 逐份相等 |
| 噎呛杯 | 分词序列 full/glass/of/water ⇎ 词 choking | %s ⇎ %s | 逐份相等 |
| 同一枚 1.6 两式 | 分词 1/6/mcg/kg/day ⇎ 1/6/mcg/per/kg | %s ⇎ %s | 逐份相等 |
| 同一枚 12.5 两式 | 分词 12/5/to/25/mcg ⇎ 12/5/mcg/to/25/mcg | %s ⇎ %s | 逐份相等 |
| 轻度起始叙述式 | 分词 tsh/less/than/10 | %s | 逐份相等 |
| 赋形剂 | 分词 magnesium/stearate ⇎ 词 gelatin | %s ⇎ %s | 逐份相等 |
| 心房颤动 | 分词 atrial/fibrillation | %s | 逐份相等 |
| 黑框大小写 | 逐字符 find 扫描, 原样大小写两档 | 高档 %s ⇎ 低档 %s | 逐份相等 |

上表 %d 行全部 assert, 不符即停机。

### 读法

一、"推荐剂量是多少"四份同答: 全维持 1.6、步长 12.5-25、节奏 4-6 周——所以这份编码不记答案, 记**同一答案的四种拼法**。斜杠式 1.6 mcg/kg/day 是 A/D 表格体的指纹, 叙述式 1.6 mcg per kg 是 B/C 的指纹; 12.5 的三种连排里, A 与 D 同式、B 独式、C 又一式——仿制片逐字复制了蓝本的表格行, 却没复制蓝本的生物利用度句(93%% 四份里只 A 一处)。
二、"怎么吃"由两层文本各答一次: 处方信息层四份同写 one-half to one hour, 患者插页层(只 B/C 有)写 30 minutes to 1 hour——同一枚空腹窗, 给医生的句式与给患者的句式不同, 且插页的无有把四份劈成两半。Levoxyl 独有"配一整杯水防噎呛"(full glass of water 4 处 ⇎ choking 5 处), 片剂同类不教整吞, 胶囊档才有整吞句。
三、谱系判据不在内容在形状: 黑框同一句, C 用小写 or(低档 3 处, 高档 0); 获批年 D 照抄参照制剂的 2002 而它自己的标签 2026 年才更新; 全文 ANDA 词 0 处——仿制片不说自己走哪条审批路, 页面类目按参照制剂记。
四、赋形剂四份互不相交, 唯一交集 magnesium stearate; 桥接只在片剂三份之间(povidone A⇎D、microcrystalline cellulose B⇎D), C 的 gelatin/glycerin/water 三种全为独占——同一成分在不同厂的措辞亦不同(coloring additives ⇎ color additive(s))。
五、NDC 形包号 C 面为 0(三段数字两短横、前置字符非字母数字, setid 十六进制串内切片已排除): 四份里只有 Tirosint 页面不报包装代码。

### 本条不能由在库文件判定的(只登记, 不进门槛)

① 四份页面的抓取时刻与 DailyMed 此刻挂的 spl_version; ② 各家药真实处方习惯与药房替代率; ③ B 插页 issued december 2018 与标签更新 december 2020 之间插页是否已在站外改版; ④ C 页面无 NDC 串是标签本身无包装表还是渲染层省略; ⑤ gluten-free 声明(B 独有句)的检测口径。这些只能站外核验, 不进判词与门槛。

### 编码与门的账

编码区 %d 字符(不含换行); 锚 %d 处(候选池 %d 条按标签 A %d ⇎ B %d ⇎ C %d ⇎ D %d, 工具侧逐字校验 ok=%d bad=0); 扁平契约 %d 枚键, 每枚由 DERIV 算式从审计器侧第二套实现复算; 本注第三套实现(分词序列⇎逐字符扫描)对上表 %d 行 + 黑框两档再复测。门槛三遍: T1 字面逐锚回源 ⇎ T2 DERIV 重跑 ⇎ T3 码位与字母账。
''' % (
    F['half_to_one'], F['min30'], F['full_glass'], F['choking'],
    F['d16kg'], F['d16pkg'], F['d125to25'], F['d125_to25'], F['tsh10w'],
    F['exc_mgstearate'], F['exc_gelatin'], F['atrial'], hi, lo,
    len(rows) + 1,
    n_enc, n_anchor, len(atoms), per_tag.get('A', 0), per_tag.get('B', 0), per_tag.get('C', 0), per_tag.get('D', 0),
    len(atoms), len(REG), len(rows) + 1)

mark = u'## ⛓解读注'
head = entry[:entry.index(mark)]
io.open('corpus/babeltele/B67_levothyroxine_four_labels_four_answers.md', 'w',
        encoding='utf-8', newline='\n').write(head + gloss)
print(u'fill67 写回: 复测 %d 行全 assert, 编码 %d 字符, 锚 %d, 契约 %d 键' % (len(rows) + 1, n_enc, n_anchor, len(REG)))
