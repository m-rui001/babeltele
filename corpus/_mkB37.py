# -*- coding: utf-8 -*-
# 生成 B37 条目: 同一 ARDS 活检队列的三份文本(原作者正文 ⇎ 已刊批评 ⇎ 未读批评的模型盲评)压成一段可机检编码。
# 纪律: 每个 ⟨⟩ 必须逐字命中它自己标签的源; 锚外只允许中文与记号(拉丁字母只出现在出处标签里)。
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ENTRY = u'corpus/babeltele/B37_ards_dad_author_critic_blindmodel.md'
RAW = {u'C': u'corpus/raw/prose/pmc_ards_chang_phases.txt',
       u'H': u'corpus/raw/prose/pmc_ards_dad.txt',
       u'D': u'corpus/raw/cot/b37_dad_review_deepseek.md',
       u'G': u'corpus/raw/cot/b37_dad_review_glm.md'}
SRC = {k: io.open(v, encoding=u'utf-8').read() for k, v in RAW.items()}

L = []
A = L.append

A(u'🧭体例 ⟦C⟧＝同一 90 例急呼窘活检队列的原作者正文 ⇎ ⟦H⟧＝同年同刊针对 ⟦C⟧ 的通信批评 ⇎ ⟦D⟧＝只读到 ⟦C⟧ 的设计与数据、未读 ⟦H⟧ 的模型推理链; 三源写的是一次活检定相位这件事。')
A(u'📋锚点纪律 ⟦C⟧⟨A total of 90 patients were included in the analysis⟩ ⇎ ⟦H⟧⟨Several issues warrant clarification⟩ ⇒ 每个 `⟨⟩` 逐字回自己标签的源, 归属由前贴单字母标签决定, 不靠语序。')

A(u'⏱时间零点 ⟦C⟧⟨Rapid progression was defined as the presence of the proliferative phase within 7 days or the fibrotic phase within 21 days from ARDS diagnosis to lung biopsy⟩ ⇎ ⟦H⟧⟨performed a mean of 5.4 days after diagnosis in the rapid group and 11.3 days in the non-rapid group⟩ ⇎ ⟦H⟧⟨All included patients had to survive until biopsy⟩ ⇒ 分组要用到活检之后才知道的信息, 随访却从诊断起算。')
A(u'🕳命名的缺席 ⟦C⟧ 通篇没有这个诊断词(⟦C⟧⟨may have led to timing bias, as each patient underwent only a single biopsy⟩ 是它能到达的最远处) ⇎ ⟦H⟧⟨may introduce immortal-time bias⟩ ⇎ ⟦D⟧⟨The interval between diagnosis and biopsy is immortal in both groups but longer in non-rapid⟩ ⇎ ⟦G⟧⟨The classic immortal time problem: mortality measured from diagnosis date⟩ ⇒ 术语能被局外人立刻叫出, 作者自己只用邻词绕开；⟦D⟧ 侧 33 次, ⟦G⟧ 侧 57 次(机检)。')
A(u'🛠修法的精度 ⟦H⟧⟨A left-truncated Cox model using ARDS diagnosis as the time scale and biopsy date as delayed entry⟩ ⇎ ⟦D⟧⟨Standard fix: landmark analysis at a fixed time⟩ ⇎ ⟦G⟧⟨Cox with time origin = diagnosis, entry time = biopsy time (delayed entry)⟩ ⇎ ⟦D⟧ 侧这条术语 0 命中(机检) ⇒ 同一病灶, 人给的是把入组时刻写进风险集, 两个模型一个复述了它, 一个换成通用套路。')
A(u'🚧被作废的自证 ⟦C⟧⟨no significant difference in the duration from ARDS onset to biopsy between 60-day survivors and non-survivors⟩ ⇎ ⟦H⟧⟨Similar biopsy intervals among survivors and non-survivors do not resolve this risk-set problem⟩ ⇒ 同一组统计量, 作者当作回应, 批评者指出它答的不是被问的问题。')
A(u'🎯方向的断言与保留 ⟦H⟧⟨the net direction after accounting for other selection mechanisms cannot be determined without reanalysis⟩ ⇎ ⟦D⟧⟨so the net magnitude is not determinable, but the structural bias is away from the null⟩ ⇎ ⟦G⟧⟨Direction cannot be determined⟩ ⇒ 同样拒绝给数值, ⟦D⟧ 却把方向的符号先固定下来, ⟦G⟧ 与 ⟦H⟧ 一样停在符号未定; 保留范围之差本身可机检。')

A(u'🧮分母之争 ⟦C⟧⟨21 (84.0%) patients underwent lung biopsy within 21 days of diagnosis⟩ ⇎ ⟦H⟧⟨21 of 23 fibrotic cases represents 91.3%⟩ ⇎ ⟦H⟧⟨we would welcome clarification of the denominator used for the reported 84.0%⟩ ⇎ ⟦D⟧ 全篇没有提到分母(机检 0 次) ⇎ ⟦G⟧⟨small-denominator artifact⟩ ⇒ 一个分子相同的分数换分母就换结论, 这件事只有拿全表的人看得见。')
A(u'🧱复合结构的稀疏 ⟦H⟧⟨the rapid group contained 27 proliferative and 21 fibrotic cases⟩ ‖ ⟦H⟧⟨the non-rapid group contained 36 proliferative, 2 fibrotic, and 4 exudative cases⟩ ⇎ ⟦H⟧⟨its 28-day and 60-day mortality estimates (0/2 and 1/2) illustrate the resulting instability⟩ ⇎ ⟦C⟧⟨small number of patients in the exudative phase may have influenced the statistical comparisons⟩ ⇒ 同一段数据, 作者写成"可能有影响", 批评者写成"任何分层内推断都不成立"。')
A(u'📐预设 ⇎ 数据驱动 ⟦C⟧⟨We used ROC curves and the Youden index to determine optimal cutoffs for predicting 28-day mortality⟩ ⇎ ⟦H⟧⟨a 10-day cutoff selected by receiver operating characteristic analysis in the same cohort produced a significant 28-day, but not 60-day, contrast⟩ ⇎ ⟦H⟧⟨The prespecified and data-driven definitions should be distinguished⟩ ⇒ 阈值来源决定哪个终点显著, 而显著性报告不区分这两种来源。')
A(u'🔬取样方式决定病理 ⟦C⟧⟨of whom 81 (66.9%) were diagnosed with DAD⟩ ⇎ ⟦C⟧⟨DAD was identified in 11 patients (21.2%)⟩ ⇎ ⟦C⟧⟨no study has directly compared open lung biopsy with TBLC⟩ ⇎ ⟦H⟧⟨Because modality is linked to sampling adequacy, patient selection, and calendar period⟩ ⇒ 检出率差 3 倍被当作技术差异陈述, 而不是分组的混杂来源。')
A(u'👁盲法与观察者 ⟦C⟧ 全文没有"盲法"一词(机检 0 次) ⇎ ⟦H⟧⟨whether a unified blinded re-review was performed⟩ ‖ ⟦H⟧⟨whether interobserver agreement was quantified⟩ ⇎ ⟦D⟧⟨no stated unified blinded re-review⟩ ⇒ 两路读者都从"方法部分没写"推出"可能没做", 这是缺席证据的标准用法。')
A(u'🔄定义性耦合 ⟦H⟧⟨Ventilatory ratio includes PaCO2 in its numerator⟩ ⇎ ⟦H⟧⟨entering both variables in one model creates mathematical coupling⟩ ⇎ ⟦D⟧ 没有"定义耦合"这一说法(机检 0 次), 它给的是另一诊断 ⟦D⟧⟨Adjusting for post-exposure variables⟩ ⇒ 同两个变量, 一个是"分子里含着它"的代数问题, 一个是"调整后变量在因果路上"的设计问题。')
A(u'🏷被误标的效应量 ⟦C⟧⟨hemoglobin level (relative risk [RR]: 1.342, p = 0.023)⟩ ⇎ ⟦C⟧ 正文从不出现"比值比"一词(机检 0 次) ⇎ ⟦H⟧⟨Table 6 labels exponentiated logistic-regression coefficients as relative risks, although they are odds ratios⟩ ⇎ ⟦D⟧⟨Logistic regression exponentiated coefficients are odds ratios, not RR⟩ ⇒ 表头自称风险度的表, 其模型名就在同一行表题里; 错标对内部读者不可见。')
A(u'🧭自我矛盾的泛化 ⟦C⟧⟨we restricted our analysis to patients with histologically confirmed DAD⟩ ⇎ ⟦C⟧⟨allowing our results to be generalized to patients with DAD⟩ ‖ ⟦C⟧⟨the study population was highly selected and limited to patients who underwent lung biopsy, selection bias is present⟩ ⇒ 同一句里"限制"既被当作外部效度的代价, 又被当作它的保证。')
A(u'⚙️机制的方向 ⟦C⟧⟨driving pressure on the day of ARDS diagnosis (HR: 0.932, p = 0.047)⟩ ⇎ ⟦H⟧⟨Similar tidal volumes and numerically lower driving pressure and mechanical power in the rapid group do not support a specific ventilator-mediated mechanism⟩ ⇎ ⟦D⟧⟨the reported covariates suggest the rapid group was not obviously sicker on respiratory mechanics⟩ ⇒ 两组都拒绝呼吸机机制, 但 ⟦H⟧ 停在"不支持", ⟦D⟧ 前进到"说明不更重"——后者多走了一步推断。')
A(u'📏清单的规模 ⟦C⟧ 的自述局限共 5 段, ⟦H⟧ 的异议是 4 条, ⟦D⟧ 的答复编号条目 30 条 ⇎ ⟦G⟧⟨to be classified non-rapid, a patient had to survive long enough to have a biopsy⟩ ⇎ ⟦D⟧⟨Let me target ~25⟩ ⇒ 条目数不是质量的度量: 最多条的那份从未算过一次数, 最少条的那份把分母改了。')
A(u'🔁一次活检测速度 ⟦C⟧⟨All patients underwent lung biopsy only once⟩ ⇎ ⟦H⟧⟨a single biopsy provides a cross-sectional snapshot, not an intra-individual measure of pathological velocity⟩ ⇎ ⟦H⟧⟨DAD features overlap temporally and may coexist within one lung⟩ ⇒ "快速进展"这个名字需要一个变化率, 而设计只供给一次快照。')
A(u'⚠️结论的换写 ⟦H⟧⟨early detection of advanced-phase histology among selected patients who survived to biopsy⟩ ⇎ ⟦H⟧⟨rather than directly observed pathological acceleration⟩ ⇎ ⟦H⟧⟨before this uncommon cohort informs prognostic enrichment or trial eligibility criteria⟩ ⇒ 批评不以推翻关联为终点, 而以限制它被用在哪一处为终点。')
A(u'🧯修法清单的层级 ⟦H⟧⟨reporting modality by progression group and an open-lung-biopsy-only sensitivity analysis would be informative⟩ ‖ ⟦H⟧⟨phase-specific estimates, an interaction test, and a sensitivity analysis excluding exudative cases⟩ ⇎ ⟦H⟧⟨the estimates should be relabelled or risk ratios estimated with modified Poisson regression⟩ ⇒ 每条异议都配一个能直接执行的替代分析, 措辞本身按可执行性分档：⟦H⟧⟨would be informative⟩ ⇎ ⟦H⟧⟨would be preferable⟩ ⇎ ⟦H⟧⟨is material⟩。')
A(u'🈳强度词 ⟦H⟧⟨If feasible, dual blinded review with an agreement statistic would further strengthen reproducibility⟩ ⇎ ⟦H⟧⟨Separate models with collinearity diagnostics would be preferable⟩ ⇎ ⟦H⟧⟨this distinction is material⟩ ⇒ 同一份批评里三种力度的建议词共存, 力度本身编码了作者对可执行性的判断。')

A(u'🧭偏倚家族的名称 ⟦G⟧⟨prevalence-incidence (length-biased) sampling⟩ ⇎ ⟦H⟧⟨creating potential immortal-time bias⟩ ⇎ ⟦C⟧ 侧这两个词都不存在(机检 0 次) ⇒ 同一处缺陷在 ⟦G⟧ 那里属于患病率—发病率偏倚家族, 在 ⟦H⟧ 那里被专门称作不朽时间; 命名口径不同但都不可从 ⟦C⟧ 内部读出。')
A(u'🪞回读题面 ⟦G⟧⟨Also the task: "Where the direction of bias cannot be determined from the information given, say so explicitly rather than guessing."⟩ ⇎ ⟦D⟧⟨the question says "Where the direction of bias cannot be determined from the information given, say so explicitly rather than guessing."⟩ ⇒ 两份推理链都停下来重读指令再决定如何措辞; 指令里的"不要猜"是它们保留态度的外源。')
A(u'📊计量对照 ⟦C⟧正文 62261 ⇎ ⟦H⟧正文 14683 ⇎ ⟦D⟧推理 63864 成稿 18046 ⇎ ⟦G⟧推理 116213 成稿 11188 ⇒ 两条链的推理区都比它所评论的两份人类文本长, 而成稿比原文短; 想得多的那一条写得更克制。')
A(u'🈳语言漂移 ⟦C⟧ 41899 个字母 ⇎ ⟦H⟧ 10953 ⇎ ⟦D⟧ 49907 ⇎ ⟦G⟧ 90560, ⟦G⟧ 的推理区实测 2 个汉字 ⇎ 其余三源 0 个 ⇒ 四源同为英文, 但跨源比术语计数前必须先量书写系统: 一次"0 次命中"可能只是"没用这种语言写"。')
A(u'∴骨架 ① 分组信息晚于随访起点 ⇒ 风险集被"活到活检"筛过; ② 两组的活检间隔之差就是被保证存活的之差, 但作者用"存活者与死亡者间隔无差异"回应, 这两件事不在同一维度上; ③ 复合定义把两种时相合起来 ⇒ 稀疏格子的估计不稳, 而合并本身在报告里不可见(分母换了); ④ 阈值有预设与搜索两种来源, 后者在同一队列里会挑出显著的那个; ⑤ 检出率随取材方式变 ⇒ 相位与结局共享一个取材通道; ⑥ 两变量在代数上相关时, 多元模型给出的不是两个独立效应; ⑦ 表头标签与模型族不符, 错标对作者不可见, 对读者放大; ⑧ 未写的流程只能作缺席证据, 缺席证据的措辞要用"可能"; ⑨ 结论的用途(试验富集/入组标准)比结论本身更需要被限制; ⑩ 模型的长处是穷举、命名与回读指令; 短板是算术复核 ⑪ 同一模型族内, 一个复述了延迟入组, 另一个从未听过它——模型间方差大于人⇎机之差的一部分, 短处是把方向符号固定得太早, 且从不复核数字。')
A(u'ℒmethod 面对一份把分组定义在随访中后段才确定的研究报告: 先把"分组用了哪一天的信息"与"随访从哪一天起算"并排放, 若晚于起算, 则不论组间间隔差是否显著都存在风险集问题; 修法是把晚到的信息写成入组时刻而不是协变量。判定一个复合表型是否被"合并"偷走了信息: 把每个时相的例数与事件数按组摊开, 任一格小于 10 例即禁止做层内推断, 并对每个百分数追问分母。见到两个共享分子的生理指标同入一模型, 先查代数耦合再谈混杂。表头效应量名称必须与模型族核对——正文没有出现的那个词就是错标的信号。对"方法里没写"的质控, 用"可能未做"而不是"未做"。批评一份研究时, 把结论能支持的用途写出来, 而不是只写效应量大小。给一份盲评清单时, 检查它是否算过一次数: 条目数与算术复核次数不成正比。')

enc = u'\n'.join(L)
labels = re.findall(u'⟦([A-Z])⟧⟨', enc)
atoms = re.findall(u'⟧⟨([^⟨⟩]+)⟩', enc)
assert not re.findall(u'⟧⟨⟦', enc), u'双重标签嵌套'
assert len(labels) == len(atoms), u'标签数 != 锚数'
lab_all = re.findall(u'⟦([A-Z])⟧', enc)
for m in re.finditer(u'⟦([A-Z])⟧⟨([^⟨⟩]*)⟩', enc):
    assert m.group(1) in RAW, u'未知标签 ' + m.group(1)
    if m.group(2) not in SRC[m.group(1)]:
        print(u'MISS [%s] %s' % (m.group(1), m.group(2)[:80]))
out = re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)
outlat = len(re.findall(u'[A-Za-z]', out))
print(u'编码行数 %d 锚 %d %s 标签总 %d 锚外字母 %d' % (
    len(L), len(atoms), {k: labels.count(k) for k in sorted(set(labels))}, len(lab_all), outlat))

head = (u'# B37 同一份活检队列的三种读法：原作者的自证、已刊批评的作废句与模型的盲评清单\n\n'
        u'src: corpus/raw/prose/pmc_ards_chang_phases.txt ⇎ corpus/raw/prose/pmc_ards_dad.txt ⇎ '
        u'corpus/raw/cot/b37_dad_review_deepseek.md (J Intensive Care 2026 研究正文 ⇎ 同期通信批评 ⇎ '
        u'未读批评的模型思维链, 题面只给设计与数据, 不给结论)\n'
        u'tags: 医学研究批评 统计隐性知识 幸存者入组 分母与效应量 人评⇎机评\n\n'
        u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n（待生成）\n')
io.open(ENTRY, u'w', encoding=u'utf-8').write(head)
print(u'wrote ' + ENTRY)
