# -*- coding: utf-8 -*-
# 生成 B39 条目: 早期下床活动剂量-反应研究(被批评方) ⇎ 同刊目标试验框架批评信(批评方)。
# 纪律: 每个 ⟨⟩ 必须逐字命中它自己标签的源; 锚外只允许中文与记号(拉丁字母只出现在出处标签里)。
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ENTRY = u'corpus/babeltele/B39_mobilization_targettrial_letter_response.md'
RAW = {u'S': u'corpus/raw/prose/pmc_mobilization_dose_study.txt',
       u'L': u'corpus/raw/prose/pmc_mobilization_targettrial_letter.txt'}
SRC = {k: io.open(v, encoding=u'utf-8').read() for k, v in RAW.items()}

L = []
A = L.append

A(u'🧭体例 ⟦S⟧＝日本单中心心血管重症监护病房的回顾性队列(610 例, 术后需 ≥3 日重症监护)是该卷第 59 号文章 ⇎ ⟦L⟧＝同卷第 63 号的方法学批评信; 与上一条目相反，被批评的一方在本对里全程沉默，指控没有答辩。')

A(u'📋锚点纪律 ⟦S⟧⟨, it should be interpreted as a time-varying exposure rather than a baseline intervention assigned at a single time point⟩ ⇎ ⟦L⟧⟨clinical status…should be interpreted as a time-varying exposure rather than a baseline intervention assigned at a single time point⟩ ⇒ 每串各回自己的源; 同一段话在两文件的正文之和命中 2 次(机检推导)，即引文逐字，只在省略号处截断。')

A(u'🔍引文的瘦身与升格 ⟦S⟧⟨Because mobilization dose accumulated over time during ICU stay and was influenced by patients’ evolving clinical status⟩ ⇎ ⟦L⟧⟨acknowledge that “mobilization dose accumulated over time during ICU stay⟩ ‖ ⟦S⟧⟨A 5-point decrease in the BI has been considered to represent a clinically meaningful deterioration in functional independence⟩ ⇎ ⟦L⟧⟨A 5-point decrease in the BI is designated⟩ ⇒ 引文从原句的从属连词之后起头，原因从句被引成被承认的断言; 原句的"被认为"在信里换成"被规定"(机检: 这个动词在 ⟦S⟧ 0 次)。')

A(u'🏷同一指标的两个名字 ⟦S⟧⟨The AUC for the PS model was 0.68 (95% confidence interval [CI] 0.63–0.72).⟩ ⇎ ⟦L⟧⟨The reported PS model achieved a C-statistic of only 0.68 (95% CI 0.63–0.72)⟩ ⇒ 数值与区间一字不差，缩写换名(机检: 两个缩写互不出现在对方，见零值键) ⇒ 按缩写字检索这条指控会在被批评文献里一无所获。')

A(u'⚖️借来的阈值落在自己的区间里 ⟦L⟧⟨cause beneficial treatments to be falsely labeled harmful, with measured odds ratios for mortality of 1.4 or higher produced when the true beneficial effect was an OR of 0.6–0.8⟩ ⇎ ⟦S⟧⟨The AUC for the PS model was 0.68⟩ ⇒ 外部模拟的失效线 0.66: 研究的点估计高出它 0.02(机检推导)，而同一区间的下限低于它 0.03(机检推导) ⇒ 阈值落在报告区间内部，两源都不指出; 引用别人的阈值者应当一并给出自己估计的区间。')

A(u'🧮粗率、校正比与两种中点 ⟦S⟧⟨19.9%, p = 0.008) (Fig.⟩ ‖ ⟦S⟧⟨low-dose mobilization remained significantly associated with functional decline (odds ratio [OR] 2.03; 95% CI 1.19–3.45; p = 0.009)⟩ ⇎ ⟦S⟧⟨( β − 5.38; 95% CI − 9.14 to − 1.62; p = 0.005)⟩ ⇎ ⟦L⟧⟨with a lower BI change score (β −5.38; 95% CI − 9.14 to − 1.62)⟩ ⇒ 同一对比在正文里有两个概率值; 两率之比 1.59(机检推导)对报告比值比 2.03; 比值型区间的中点是几何的(1.19×3.45 的平方根＝2.03，机检推导)，连续型结局的中点是算术的(9.14 与 1.62 的一半＝5.38，机检推导); 信复述同一数时负号后少一个空格。')

A(u'📉分母在段内被替换 ⟦S⟧⟨A total of 610 patients were included in the analysis.⟩ ‖ ⟦S⟧⟨Functional decline occurred in 101 patients (25.8%)⟩ ⇒ 匹配后两组合计 392 例(机检推导)，为 610 的 64.3%(机检推导); 101÷392＝25.8(机检推导) 而 101÷610＝16.6(机检推导) ⇒ 印出的 25.8% 属于匹配后队列，句子却紧跟在"610 例入组"之后。')

A(u'🚪分组线穿过自己的组 ⟦S⟧⟨ICU 2.2 (2.0, 2.7) 1.5 (1.3, 1.7)⟩ ‖ ⟦S⟧⟨Ward 1.8 (1.5, 2.0) 1.7 (1.4, 2.0)⟩ ‖ ⟦S⟧⟨Total 1.9 (1.7, 2.1) 1.6 (1.4, 1.8)⟩ ⇎ ⟦S⟧⟨The cutoff of two units per day (approximately 40 min) was selected⟩ ⇒ 高剂量组的合计暴露 1.9 低于定义它的 2.0 达 0.1(机检推导); 病房阶段两组几乎相同，而监护期组间差是病房期组间差的 7 倍(机检推导) ⇒ 分组分离全部来自监护期，两单位换算 2×20＝40 分钟(机检推导)。')

A(u'⏱分母本身不等长 ⟦S⟧⟨ICU stay, days 5 (4, 7) 7 (5, 9) 2 (1, 2)⟩ ⇎ ⟦L⟧⟨compares the average ICU exposure between groups—a snapshot precisely unsuited to a continuously updated intervention⟩ ⇒ 低剂量组在监护室多留 2 日，而暴露按"每重症监护日均"折算 ⇒ 信指控的"时变"有一条现成的表格证据，它没有引用这一行(机检: 三张表的行标签在 ⟦L⟧ 各 0 次)。')

A(u'🧱结局测在天花板上 ⟦S⟧⟨Pre-Barthel Index, points 100 (100, 100) 100 (100, 100)⟩ ‖ ⟦S⟧⟨Post-Barthel Index, points 100 (100, 100) 100 (90, 100) 0 (0, 0)⟩ ⇎ ⟦L⟧⟨particularly for patients near the floor or ceiling of the 0–100 range⟩ ⇒ 信的天花板之忧被这两行直接证实而未遭引用: 两组基线与出院中位数都贴着满分，组间差写作 0 与 (0, 0) 而概率值列报 <0.01; 100÷5＝20(机检推导) ⇒ 走完整张量表要 20 个"有临床意义的下降"。')

A(u'📏结局阈值等于量表的最小步长 ⟦S⟧⟨The BI assesses independence in 10 activities of daily living, with total scores ranging from 0 to 100⟩ ‖ ⟦S⟧⟨Each item is scored in increments of 0, 5, 10, or 15 points⟩ ⇎ ⟦L⟧⟨the BI’s step sizes of 0/5/10/15 mean that a 5-point swing can cross either a meaningful or a chance threshold depending on the item affected⟩ ⇒ 全表的结局判定值恰等于单个条目最小非零步长: 一次条目级抖动就能构成"临床意义"，两源的书写方式让这一点要到表里才看得见。')

A(u'🪦外部阈值的量级差 ⟦S⟧⟨A 5-point decrease in the BI has been considered to represent⟩ ⇎ ⟦L⟧⟨a mean change of only 1.85 points already exceeds measurement error and is perceived by stroke patients as important⟩ ‖ ⟦L⟧⟨No analogous MCID has been derived for postcardiac surgical patients⟩ ⇒ 5 是卒中人群阈值的 2.7 倍(机检推导); 信借的是别的人群的尺，同时承认本人群没有自己的尺(机检: 该缩写字在 ⟦S⟧ 0 次)。')

A(u'🗒两文的清单方式 ⟦S⟧⟨It must be acknowledged that this study has several limitations. First, because mobilization dose was influenced by patients’ evolving clinical status, reverse causality and time-varying confounding cannot be completely excluded.⟩ ⇎ ⟦L⟧⟨We respectfully raise four methodological points that, taken together, suggest these findings should be interpreted as exploratory and hypothesis-generating⟩ ⇒ 原文用五个序数标记自陈限制(机检推导)，信用一段无编号的四点清单(其序数标记在 ⟦L⟧ 全 0 次) ⇒ 被批评者已经把大部分指控写进自己的限制段，批评只是把它们换到文章外面重说一遍。')

A(u'🔄指控共用的词 ⟦S⟧⟨reverse causality and time-varying confounding cannot be completely excluded⟩ ⇎ ⟦L⟧⟨cannot fully account for reverse causality, temporal alignment between exposure and outcome, treatment-affected time-varying confounding, or potential immortal-time bias⟩ ⇒ 四项指控里前三项复用原文措辞(同一短语两侧各出现两次)，只有"永生时间"是新增名词(机检: 该词在 ⟦S⟧ 0 次而在 ⟦L⟧ 3 次) ⇒ 一篇批评的新增量往往只有一个词，其余是重新排布。')

A(u'🥷同一偏倚的两种命名 ⟦S⟧⟨However, worst-case sensitivity analyses classifying these patients as having functional decline yielded consistent associations, suggesting that survivor bias alone is unlikely to fully explain the findings.⟩ ⇎ ⟦L⟧⟨because patients must survive long enough in the ICU to accrue “high-dose” exposure and is not eliminated simply by narrowing the analytic window⟩ ⇒ 原文说"幸存者偏倚"并用最坏情形分析回击，信用"永生时间"把同一排除标准重述为设计缺陷(机检: 两个词各只在一侧出现) ⇒ 换个名字就能让一个已被处理的问题重新变成未处理。')

A(u'⏳替对方澄清一个未声称的用途 ⟦S⟧⟨To mitigate reverse causality and ensure appropriate temporal alignment, a sensitivity analysis was performed using mobilization dose during the first 72 h after ICU admission, adjusted for the same covariates as in the primary analysis.⟩ ⇎ ⟦L⟧⟨it was not intended to address the structural immortal-time bias that arises in the primary contrast⟩ ‖ ⟦L⟧⟨readers should not interpret the existing 72 h sensitivity analysis as already resolving the guarantee-time/immortal-time issue we raise here⟩ ⇒ 信替作者否认了一个作者没有声称的用途(机检: "并非旨在"这个说法在 ⟦S⟧ 0 次) ⇒ 预防性让步: 先挡掉读者可能替原文做出的辩护，再维持指控。')

A(u'📐被限定窗口后效应量反而更大 ⟦S⟧⟨low-dose mobilization remained significantly associated with postoperative functional decline (OR 2.65, 95% CI 1.58–4.46⟩ ⇎ ⟦L⟧⟨the authors report that a mobilization dose of⟩ ⇒ 72 小时口径下的报告值是主分析的 1.31 倍(机检推导)，而信复述结论时只取主分析的数(机检: 这三个数在 ⟦L⟧ 各 0 次) ⇒ 批评者可以引用对自己不利数值的存在而不引用其数值。')

A(u'⚠️批评自己撤回一种标准做法 ⟦L⟧⟨Mortality, postoperative transfer, and functional decline are, however, qualitatively distinct outcomes, and reclassifying death as functional decline conflates two different events.⟩ ⇎ ⟦L⟧⟨Fine–Gray or cause-specific hazards modeling would require redefinition of the outcome and follow-up structure and is not directly applicable to the present analysis⟩ ‖ ⟦S⟧⟨in which in-hospital deaths and early transfers were classified as functional decline, the association remained statistically significant (OR 2.32; 95% CI 1.60–3.35⟩ ⇒ 信先说"把死亡并入功能下降混淆两类事件"，随即承认自己的竞争风险工具在此用不上(机检: 该方法名在 ⟦S⟧ 0 次); 并入死亡的实测效果只是把效应量抬高 1.14 倍(机检推导)。')

A(u'🧱不可得作为终止条件的批评版 ⟦L⟧⟨Anchoring the primary outcome to a population-derived MCID⟩ ‖ ⟦L⟧⟨treating ICU death and early postoperative transfer as distinct from functional decline through hierarchical or composite outcome definitions in future prospective work⟩ ‖ ⟦L⟧⟨conducting adequately powered confirmatory replication⟩ ‖ ⟦L⟧⟨applying formal target-trial emulation or marginal structural models for genuinely time-varying interventions in subsequent studies⟩ ⇒ 四项补救全部以动名词起句且全部指向未来的数据(机检推导: 四个短语各命中 1 次) ⇒ 没有一项要求对已有队列重算; 批评的代价由后来的研究者支付，因此永远不会被这篇批评本身证伪。')

A(u'📐过度校正由原文自己承认 ⟦L⟧⟨matches only on baseline covariates (age, sex, BMI, preoperative BI, APACHE II, duration of mechanical ventilation, and postoperative days to standing)⟩ ⇎ ⟦S⟧⟨Second, inclusion of early invasive mechanical ventilation duration in the propensity score model may have introduced overadjustment because this variable may partly reflect post-exposure processes rather than a pure baseline confounder⟩ ⇎ ⟦S⟧⟨adjusting for age, sex, BMI, cerebrovascular disease, CKD, preoperative BI score, APACHE II score, day of surgery (weekend), duration of mechanical ventilation, postoperative days to the initiation of standing, and use of continuous renal replacement therapy⟩ ⇒ 信把通气时长列为基线协变量，原文却自己把它标为可能的暴露后过程(机检: "过度校正"一词在 ⟦L⟧ 0 次); 信的清单比模型少几项，少的两项与那个日历变量在 ⟦L⟧ 全 0 次(机检); 匹配前失衡最大的一行 ⟦S⟧⟨CRRT, n (%) 29 (7.4) 39 (18.0) 0.32⟩ 落在一个只进结局回归、不进匹配名单的变量上，信对它同样一字未提(机检: 该缩写与其全名在 ⟦L⟧ 各 0 次) ⇒ 复述对方模型时最容易丢掉的恰是对方已经自我批评的那一项，而指控的强度也取决于批评者没看的那一行。')

A(u'🧯一个副词就是全部争议 ⟦S⟧⟨and was conceptually framed as an emulation of a hypothetical target trial⟩ ⇎ ⟦L⟧⟨The paper states that the analysis was “conceptually framed as an emulation of a hypothetical target trial”⟩ ‖ ⟦L⟧⟨The published framework, however, demands explicit specification of eligibility criteria, treatment strategies, assignment procedures, follow-up start, and outcome ascertainment⟩ ⇒ 引文与原句同串(机检: 这个副词两侧各 1 次): 指控不否认框架被提到，只否认它被执行 ⇒ "概念上框架"与"显式指定"之间的差距，就是整篇批评的靶子，而靶子只有一个词。')

A(u'🏳披露的方向相反 ⟦S⟧⟨The datasets generated and/or analysed during the current study are not publicly available due to privacy and ethical restrictions, but are available from the corresponding author on reasonable request⟩ ⇎ ⟦L⟧⟨No datasets were generated or analyzed during the current study.⟩ ⇒ 被批评者持有可索取的数据，批评者声明自己无数据(机检: 两种声明各只在一侧出现) ⇒ 可复核性全落在被批评的一方; 指控里每个数字都要回到对方的表里去验，而指控本身不可验。')

A(u'🕳剂量单位的来源无人复述 ⟦S⟧⟨Moreover, one rehabilitation unit corresponded to 20 min of exercise according to the Japanese medical reimbursement system.⟩ ‖ ⟦S⟧⟨The duration of IMS ≥ 4 activities was not recorded minute-by-minute within each unit; thus, mobilization dose represents a pragmatic estimate rather than a precise measure of physical loading.⟩ ⇎ ⟦L⟧⟨(each unit = 20 min of out-of-bed activity at IMS ≥ 4)⟩ ⇒ 暴露单位来自计费规则而非生理学，且原文自认它是权宜估计(机检: 这两个词在 ⟦L⟧ 各 0 次) ⇒ 信把定义压缩成一句括号，顺手删掉了原文最自我限制的两句话。')

A(u'🪞限定再限定 ⟦L⟧⟨Because the original study was a retrospective single-center cohort that did not claim to provide definitive causal evidence, the most balanced interpretation is that the causal implications of the reported associations should be drawn cautiously⟩ ⇎ ⟦L⟧⟨rather than as a reason to dismiss the findings themselves⟩ ‖ ⟦L⟧⟨the present study reports neither an a priori sample-size estimation nor a post hoc power assessment, despite a matched cohort of only 196 per group and multiple subgroup and restricted-cubic-spline analyses⟩ ⇒ 信在指出"没有样本量估算"之后立刻声明这不应被当作否定结论的理由(机检: 效力/假说二词在 ⟦S⟧ 各 0 次而在 ⟦L⟧ 多次) ⇒ 批评的最后一层自限是把"你的缺陷不能用来推翻你"写进同一段。')

A(u'📊计量对照 ⟦S⟧ 正文每千字母 59 个数字字符 ⇎ ⟦L⟧ 87 个(机检推导) ⇒ 批评信的数字密度比被批评的论文高四成，而这些数字几乎全部是复述对方的; 短文本靠搬运数字变密，长文本的密度被方法与讨论稀释。')

A(u'∴骨架 ① 逐字引文可以在省略号处断句、在从属连词处起头，把原因从句变成断言; ② 引述对方用词时升级动词("被认为"→"被规定")是隐性增责; ③ 同一统计量换名后，按缩写字检索查不到指控; ④ 借用外部阈值时，若自己的点估计区间横跨该阈值，指控在数值上不自洽; ⑤ 比值型区间的中心是几何的，连续型是算术的，两者都等于点估计; ⑥ 粗率比≠报告比值比，摘要可以把未校正的概率值与校正后的效应量并排; ⑦ 结果百分比的分母可能在同一段内从全队列换成匹配后队列; ⑧ 分组阈值可能与该组自己的合计暴露矛盾(阶段均值与合计均值不同口径); ⑨ 组间分离全部来自某一阶段时，"每阶段日均"的分母就承载了结论; ⑩ 暴露窗不等长是时变混杂的可见证据; ⑪ 量表天花板在表格行里可见，而批评只在正文点名概念; ⑫ 结局阈值若等于条目最小步长，则结局与噪声同尺寸; ⑬ 被批评者的限制段常已包含指控的多数条目; ⑭ 换一种命名(幸存者→永生时间)可让已处理问题重新变成未处理; ⑮ 批评者会替作者否认一个作者没声称的用途，以堵住读者的自行辩护; ⑯ 限定窗口后效应量更大这一事实可以被不引用; ⑰ 方法学批评里允许出现"我提的工具不适用"的自限; ⑱ 全部补救指向未来数据时，批评永不可证伪; ⑲ 复述对方模型清单时最容易丢掉对方已自我批评的那一项; ⑳ 争议可以只落在一个副词上; ㉑ 持有数据的一方承担可复核性，声明无数据的一方不承担; ㉒ 定义被压缩进括号时，原文的自我限制句会被删掉; ㉓ 批评的最后一段常自限"缺陷不等于结论错误"。')

A(u'ℒmethod 读"论文 ⇎ 批评信"这类不成对的文本时，先把批评的每个指控词回查被批评文的限制段: 已存在者只是重排，新增者往往只有一个名词。凡引文都做一次逐字比对，注意起头是否落在从属连词之后、动词是否被替换。凡引用外部阈值，立即把它与被批评文自己报告的区间上下限比较，看阈值是否落在区间内。凡效应量，分别重算粗率比与区间中点(比值取几何、均值取算术)，两者不一致即为口径之差而非数据之差。凡百分比，检查其分母是全队列还是匹配后队列(用两个分母各算一次，看哪个能复现印出的数)。凡分组阈值，回查暴露各阶段的表行，看阈值是否穿过本组的合计值; 再看两组随访窗是否等长。凡批评者提出的补救，按"是否要求重算已有队列"分类: 全部指向未来数据者，该争议无法在本文献对内闭合。最后读披露区两行，判定谁承担可复核性。')

enc = u'\n'.join(L)
labels = re.findall(u'⟦([A-Z])⟧⟨', enc)
atoms = re.findall(u'⟧⟨([^⟨⟩]+)⟩', enc)
assert not re.findall(u'⟧⟨⟦', enc), u'双重标签嵌套'
assert len(labels) == len(atoms), u'标签数 != 锚数'
bad = []
for m in re.finditer(u'⟦([A-Z])⟧⟨([^⟨⟩]*)⟩', enc):
    assert m.group(1) in RAW, u'未知标签 ' + m.group(1)
    if m.group(2) not in SRC[m.group(1)]:
        bad.append((m.group(1), m.group(2)))
out = re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)
outlat = len(re.findall(u'[A-Za-z]', out))
inlat = len(re.findall(u'[A-Za-z]', u''.join(atoms)))
inhan = len(re.findall(u'[一-鿿]', u''.join(atoms)))
print(u'编码行数 %d 锚 %d %s 标签总 %d 锚外字母 %d 锚内字母 %d 锚内汉字 %d' % (
    len(L), len(atoms), {k: labels.count(k) for k in sorted(set(labels))},
    len(re.findall(u'⟦([A-Z])⟧', enc)), outlat, inlat, inhan))
for t, a in bad:
    print(u'MISS [%s] %s' % (t, a[:90]))
if bad:
    sys.exit(1)
assert not re.findall(u'》|占位|待生成.*⟩', enc), u'括号/占位污染'

head = (u'# B39 一封没有答辩的批评：逐字引文、换名指控与被删掉的自我限制\n\n'
        u'src: corpus/raw/prose/pmc_mobilization_dose_study.txt ⇎ corpus/raw/prose/pmc_mobilization_targettrial_letter.txt '
        u'(J Intensive Care 2026 早期下床活动剂量-反应研究 ⇎ 同刊目标试验框架批评信, 单方指控无答辩)\n'
        u'tags: 方法学批评 隐性知识 目标试验 时变暴露 逐字引文 表格里的反证\n\n'
        u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n（待生成）\n')
io.open(ENTRY, u'w', encoding=u'utf-8').write(head)
print(u'wrote ' + ENTRY)
