# B37 同一份活检队列的三种读法：原作者的自证、已刊批评的作废句与模型的盲评清单

src: corpus/raw/prose/pmc_ards_chang_phases.txt ⇎ corpus/raw/prose/pmc_ards_dad.txt ⇎ corpus/raw/cot/b37_dad_review_deepseek.md (J Intensive Care 2026 研究正文 ⇎ 同期通信批评 ⇎ 未读批评的模型思维链, 题面只给设计与数据, 不给结论)
tags: 医学研究批评 统计隐性知识 幸存者入组 分母与效应量 人评⇎机评

## [[原始语料|ORIGINAL]]
### ⟦C⟧ ⟸ corpus/raw/prose/pmc_ards_chang_phases.txt

Rapid progression was defined as the presence of the proliferative phase within 7 days or the fibrotic phase within 21 days from ARDS diagnosis to lung biopsy. Results A total of 90 patients were included in the analysis.

Results General characteristics During the study period, 121 patients underwent open lung biopsy, of whom 81 (66.9%) were diagnosed with DAD. All patients underwent lung biopsy only once. In comparison, 52 patients underwent TBLC, and DAD was identified in 11 patients (21.2%).

In the fibrotic phase, 21 (84.0%) patients underwent lung biopsy within 21 days of diagnosis.

However, there was no significant difference in the duration from ARDS onset to biopsy between 60-day survivors and non-survivors (8.1 ± 6.0 vs.

Univariate and multivariate analyses for 60-day mortality predictors Univariate Cox regression analysis identified several significant predictors of 60-day mortality: platelet count (hazard ratio [HR]: 0.994, p &lt; 0.001), serum creatinine level (HR: 1.138, p = 0.050), driving pressure on the day of ARDS diagnosis (HR: 0.932, p = 0.047), lung compliance on the

Optimal biopsy day cutoffs for predicting 28-day mortality We used ROC curves and the Youden index to determine optimal cutoffs for predicting 28-day mortality.

Univariate and multivariate analyses for rapid progression predictors Univariate logistic regression identified the following predictors of rapid progression: hemoglobin level (relative risk [RR]: 1.342, p = 0.023), PaCO 2 level on the day of biopsy (RR: 0.967, p = 0.046), and ventilatory ratio on the day of biopsy (RR: 0.514, p = 0.041).

To date, no study has directly compared open lung biopsy with TBLC.

Although sampling bias in TBLC may lead to underdiagnosis of DAD in this study, we restricted our analysis to patients with histologically confirmed DAD, allowing our results to be generalized to patients with DAD.

In addition, the small number of patients in the exudative phase may have influenced the statistical comparisons. Second, accurate determination of the timing of the initial pulmonary insult and the onset of DAD—central to our primary analysis—was inherently challenging and may have led to timing bias, as each patient underwent only a single biopsy.

Fourth, because the study population was highly selected and limited to patients who underwent lung biopsy, selection bias is present and the generalizability of our findings is limited.

### ⟦H⟧ ⟸ corpus/raw/prose/pmc_ards_dad.txt

We highlight four interpretive concerns: phenotype status was assigned at biopsy after follow-up began, creating potential immortal-time bias; a single biopsy cannot measure pathological velocity; sparse and imbalanced phase-by-timing cells limit component-specific inference; and concurrent physiological measurements complicate causal interpretation.

Several issues warrant clarification. First, survival was measured from ARDS diagnosis, whereas rapid status was assigned only at biopsy, performed a mean of 5.4 days after diagnosis in the rapid group and 11.3 days in the non-rapid group. All included patients had to survive until biopsy, so the later-biopsied non-rapid group accrued about 5.9 additional days of guaranteed survival before classification. Starting follow-up at diagnosis while assigning groups using later information may introduce immortal-time bias, which would be expected to favor the later-biopsied non-rapid group and could bias the hazard ratio away from the null, although the net direction after accounting for other selection mechanisms cannot be determined without reanalysis [ 2 , 3 ]. Similar biopsy intervals among survivors and non-survivors do not resolve this risk-set problem. A left-truncated Cox model using ARDS diagnosis as the time scale and biopsy date as delayed entry, supplemented by an analysis re-anchored at biopsy or a restricted biopsy-window analysis within the proliferative phase around the 7-day threshold, would better align eligibility, classification, and follow-up. Second, a single biopsy provides a cross-sectional snapshot, not an intra-individual measure of pathological velocity. DAD features overlap temporally and may coexist within one lung [ 4 , 5 ]. The composite is also structurally imbalanced: the rapid group contained 27 proliferative and 21 fibrotic cases, whereas the non-rapid group contained 36 proliferative, 2 fibrotic, and 4 exudative cases. The fibrotic non-rapid cell was, therefore, limited to two patients; its 28-day and 60-day mortality estimates (0/2 and 1/2) illustrate the resulting instability, precluding any reliable within-phase inference.

In the final cohort, 21 of 23 fibrotic cases represents 91.3%; we would welcome clarification of the denominator used for the reported 84.0%. Within the fibrotic stratum, the prespecified 21-day cutoff produced nonsignificant mortality contrasts, whereas a 10-day cutoff selected by receiver operating characteristic analysis in the same cohort produced a significant 28-day, but not 60-day, contrast. The prespecified and data-driven definitions should be distinguished. Reporting events and exact confidence intervals in the phase-by-status table, phase-specific estimates, an interaction test, and a sensitivity analysis excluding exudative cases would clarify whether the pooled association is consistent across components.

The Methods do not specify whether a unified blinded re-review was performed, how a dominant phase was assigned when features coexisted, or whether interobserver agreement was quantified.

Because modality is linked to sampling adequacy, patient selection, and calendar period [ 6 ], reporting modality by progression group and an open-lung-biopsy-only sensitivity analysis would be informative. If feasible, dual blinded review with an agreement statistic would further strengthen reproducibility [ 7 ].

Ventilatory ratio includes PaCO2 in its numerator [ 8 ]; entering both variables in one model creates mathematical coupling. Separate models with collinearity diagnostics would be preferable. Table 6 labels exponentiated logistic-regression coefficients as relative risks, although they are odds ratios. With 48 of 90 patients classified as rapid, this distinction is material; the estimates should be relabelled or risk ratios estimated with modified Poisson regression [ 9 ]. Similar tidal volumes and numerically lower driving pressure and mechanical power in the rapid group do not support a specific ventilator-mediated mechanism.

Until delayed-entry and component-specific analyses are reported, "rapid progression" is better interpreted as early detection of advanced-phase histology among selected patients who survived to biopsy, rather than directly observed pathological acceleration. Clarifying these boundaries is essential before this uncommon cohort informs prognostic enrichment or trial eligibility criteria.

### ⟦D⟧ ⟸ corpus/raw/cot/b37_dad_review_deepseek.md

The rapid group contained 27 proliferative and 21 fibrotic cases; the non-rapid group contained 36 proliferative, 2 fibrotic and 4 exudative cases; the two fibrotic non-rapid patients had 28-day and 60-day mortality of 0/2 and 1/2, and there were no 60-day deaths among the four exudative cases.

The interval between diagnosis and biopsy is immortal in both groups but longer in non-rapid. Standard fix: landmark analysis at a fixed time (e.g., biopsy or day 7), or time-dependent covariates, or measure survival from biopsy date.

So direction of confounding by baseline severity is not determinable; but the reported covariates suggest the rapid group was not obviously sicker on respiratory mechanics, which argues against severity confounding inflating the association — yet unmeasured confounding remains.

**Lack of blinded unified re-review / observer bias**: Pathologists may not be blinded to clinical course, timing, or outcome; phase assignment not standardized (no stated unified blinded re-review).

**Table 6 mislabels odds ratios as "relative risk"**: Logistic regression exponentiated coefficients are odds ratios, not RR.

Adjusting for post-exposure variables (biopsy-day PaCO2) that may be affected by the exposure (histologic progression) induces collider/overadjustment bias.

Let me target ~25.

Also, the question says "Where the direction of bias cannot be determined from the information given, say so explicitly rather than guessing." I'll do that.

Early deaths before the (shorter) rapid biopsy window could partially offset this, so the net magnitude is not determinable, but the structural bias is away from the null." Good.

### ⟦G⟧ ⟸ corpus/raw/cot/b37_dad_review_glm.md

The rapid group contained 27 proliferative and 21 fibrotic cases; the non-rapid group contained 36 proliferative, 2 fibrotic and 4 exudative cases; the two fibrotic non-rapid patients had 28-day and 60-day mortality of 0/2 and 1/2, and there were no 60-day deaths among the four exudative cases.

If you start follow-up at diagnosis but the exposure is not determined until biopsy, you have immortal time for the non-rapid group: to be classified non-rapid, a patient had to survive long enough to have a biopsy at a late time (≥ mean 11.3 days) with proliferative/fibrotic phase.

The classic immortal time problem: mortality measured from diagnosis date.

The standard re-analyses: (i) define exposure purely histologically (phase at biopsy) and stratify by biopsy-day; (ii) landmark at a fixed day; (iii) Cox with time origin = diagnosis, entry time = biopsy time (delayed entry), adjust for biopsy time; (iv) restrict to patients biopsied at similar times.

Say cannot determine; but note the bias is toward survival bias / prevalence-incidence (length-biased) sampling.

Direction cannot be determined.

Also the task: "Where the direction of bias cannot be determined from the information given, say so explicitly rather than guessing." So careful: For most confounding items: indeterminate.

they could die between day 22-28; so "0/2" not literally impossible but has ~6 days of risk max — small-denominator artifact; plus ROC cutoff chosen on the data → guaranteed upward bias.

## ⟪BabelTele⟫
🧭体例 ⟦C⟧＝同一 90 例急呼窘活检队列的原作者正文 ⇎ ⟦H⟧＝同年同刊针对 ⟦C⟧ 的通信批评 ⇎ ⟦D⟧＝只读到 ⟦C⟧ 的设计与数据、未读 ⟦H⟧ 的模型推理链; 三源写的是一次活检定相位这件事。
📋锚点纪律 ⟦C⟧⟨A total of 90 patients were included in the analysis⟩ ⇎ ⟦H⟧⟨Several issues warrant clarification⟩ ⇒ 每个 `⟨⟩` 逐字回自己标签的源, 归属由前贴单字母标签决定, 不靠语序。
⏱时间零点 ⟦C⟧⟨Rapid progression was defined as the presence of the proliferative phase within 7 days or the fibrotic phase within 21 days from ARDS diagnosis to lung biopsy⟩ ⇎ ⟦H⟧⟨performed a mean of 5.4 days after diagnosis in the rapid group and 11.3 days in the non-rapid group⟩ ⇎ ⟦H⟧⟨All included patients had to survive until biopsy⟩ ⇒ 分组要用到活检之后才知道的信息, 随访却从诊断起算。
🕳命名的缺席 ⟦C⟧ 通篇没有这个诊断词(⟦C⟧⟨may have led to timing bias, as each patient underwent only a single biopsy⟩ 是它能到达的最远处) ⇎ ⟦H⟧⟨may introduce immortal-time bias⟩ ⇎ ⟦D⟧⟨The interval between diagnosis and biopsy is immortal in both groups but longer in non-rapid⟩ ⇎ ⟦G⟧⟨The classic immortal time problem: mortality measured from diagnosis date⟩ ⇒ 术语能被局外人立刻叫出, 作者自己只用邻词绕开；⟦D⟧ 侧 33 次, ⟦G⟧ 侧 57 次(机检)。
🛠修法的精度 ⟦H⟧⟨A left-truncated Cox model using ARDS diagnosis as the time scale and biopsy date as delayed entry⟩ ⇎ ⟦D⟧⟨Standard fix: landmark analysis at a fixed time⟩ ⇎ ⟦G⟧⟨Cox with time origin = diagnosis, entry time = biopsy time (delayed entry)⟩ ⇎ ⟦D⟧ 侧这条术语 0 命中(机检) ⇒ 同一病灶, 人给的是把入组时刻写进风险集, 两个模型一个复述了它, 一个换成通用套路。
🚧被作废的自证 ⟦C⟧⟨no significant difference in the duration from ARDS onset to biopsy between 60-day survivors and non-survivors⟩ ⇎ ⟦H⟧⟨Similar biopsy intervals among survivors and non-survivors do not resolve this risk-set problem⟩ ⇒ 同一组统计量, 作者当作回应, 批评者指出它答的不是被问的问题。
🎯方向的断言与保留 ⟦H⟧⟨the net direction after accounting for other selection mechanisms cannot be determined without reanalysis⟩ ⇎ ⟦D⟧⟨so the net magnitude is not determinable, but the structural bias is away from the null⟩ ⇎ ⟦G⟧⟨Direction cannot be determined⟩ ⇒ 同样拒绝给数值, ⟦D⟧ 却把方向的符号先固定下来, ⟦G⟧ 与 ⟦H⟧ 一样停在符号未定; 保留范围之差本身可机检。
🧮分母之争 ⟦C⟧⟨21 (84.0%) patients underwent lung biopsy within 21 days of diagnosis⟩ ⇎ ⟦H⟧⟨21 of 23 fibrotic cases represents 91.3%⟩ ⇎ ⟦H⟧⟨we would welcome clarification of the denominator used for the reported 84.0%⟩ ⇎ ⟦D⟧ 全篇没有提到分母(机检 0 次) ⇎ ⟦G⟧⟨small-denominator artifact⟩ ⇒ 一个分子相同的分数换分母就换结论, 这件事只有拿全表的人看得见。
🧱复合结构的稀疏 ⟦H⟧⟨the rapid group contained 27 proliferative and 21 fibrotic cases⟩ ‖ ⟦H⟧⟨the non-rapid group contained 36 proliferative, 2 fibrotic, and 4 exudative cases⟩ ⇎ ⟦H⟧⟨its 28-day and 60-day mortality estimates (0/2 and 1/2) illustrate the resulting instability⟩ ⇎ ⟦C⟧⟨small number of patients in the exudative phase may have influenced the statistical comparisons⟩ ⇒ 同一段数据, 作者写成"可能有影响", 批评者写成"任何分层内推断都不成立"。
📐预设 ⇎ 数据驱动 ⟦C⟧⟨We used ROC curves and the Youden index to determine optimal cutoffs for predicting 28-day mortality⟩ ⇎ ⟦H⟧⟨a 10-day cutoff selected by receiver operating characteristic analysis in the same cohort produced a significant 28-day, but not 60-day, contrast⟩ ⇎ ⟦H⟧⟨The prespecified and data-driven definitions should be distinguished⟩ ⇒ 阈值来源决定哪个终点显著, 而显著性报告不区分这两种来源。
🔬取样方式决定病理 ⟦C⟧⟨of whom 81 (66.9%) were diagnosed with DAD⟩ ⇎ ⟦C⟧⟨DAD was identified in 11 patients (21.2%)⟩ ⇎ ⟦C⟧⟨no study has directly compared open lung biopsy with TBLC⟩ ⇎ ⟦H⟧⟨Because modality is linked to sampling adequacy, patient selection, and calendar period⟩ ⇒ 检出率差 3 倍被当作技术差异陈述, 而不是分组的混杂来源。
👁盲法与观察者 ⟦C⟧ 全文没有"盲法"一词(机检 0 次) ⇎ ⟦H⟧⟨whether a unified blinded re-review was performed⟩ ‖ ⟦H⟧⟨whether interobserver agreement was quantified⟩ ⇎ ⟦D⟧⟨no stated unified blinded re-review⟩ ⇒ 两路读者都从"方法部分没写"推出"可能没做", 这是缺席证据的标准用法。
🔄定义性耦合 ⟦H⟧⟨Ventilatory ratio includes PaCO2 in its numerator⟩ ⇎ ⟦H⟧⟨entering both variables in one model creates mathematical coupling⟩ ⇎ ⟦D⟧ 没有"定义耦合"这一说法(机检 0 次), 它给的是另一诊断 ⟦D⟧⟨Adjusting for post-exposure variables⟩ ⇒ 同两个变量, 一个是"分子里含着它"的代数问题, 一个是"调整后变量在因果路上"的设计问题。
🏷被误标的效应量 ⟦C⟧⟨hemoglobin level (relative risk [RR]: 1.342, p = 0.023)⟩ ⇎ ⟦C⟧ 正文从不出现"比值比"一词(机检 0 次) ⇎ ⟦H⟧⟨Table 6 labels exponentiated logistic-regression coefficients as relative risks, although they are odds ratios⟩ ⇎ ⟦D⟧⟨Logistic regression exponentiated coefficients are odds ratios, not RR⟩ ⇒ 表头自称风险度的表, 其模型名就在同一行表题里; 错标对内部读者不可见。
🧭自我矛盾的泛化 ⟦C⟧⟨we restricted our analysis to patients with histologically confirmed DAD⟩ ⇎ ⟦C⟧⟨allowing our results to be generalized to patients with DAD⟩ ‖ ⟦C⟧⟨the study population was highly selected and limited to patients who underwent lung biopsy, selection bias is present⟩ ⇒ 同一句里"限制"既被当作外部效度的代价, 又被当作它的保证。
⚙️机制的方向 ⟦C⟧⟨driving pressure on the day of ARDS diagnosis (HR: 0.932, p = 0.047)⟩ ⇎ ⟦H⟧⟨Similar tidal volumes and numerically lower driving pressure and mechanical power in the rapid group do not support a specific ventilator-mediated mechanism⟩ ⇎ ⟦D⟧⟨the reported covariates suggest the rapid group was not obviously sicker on respiratory mechanics⟩ ⇒ 两组都拒绝呼吸机机制, 但 ⟦H⟧ 停在"不支持", ⟦D⟧ 前进到"说明不更重"——后者多走了一步推断。
📏清单的规模 ⟦C⟧ 的自述局限共 5 段, ⟦H⟧ 的异议是 4 条, ⟦D⟧ 的答复编号条目 30 条 ⇎ ⟦G⟧⟨to be classified non-rapid, a patient had to survive long enough to have a biopsy⟩ ⇎ ⟦D⟧⟨Let me target ~25⟩ ⇒ 条目数不是质量的度量: 最多条的那份从未算过一次数, 最少条的那份把分母改了。
🔁一次活检测速度 ⟦C⟧⟨All patients underwent lung biopsy only once⟩ ⇎ ⟦H⟧⟨a single biopsy provides a cross-sectional snapshot, not an intra-individual measure of pathological velocity⟩ ⇎ ⟦H⟧⟨DAD features overlap temporally and may coexist within one lung⟩ ⇒ "快速进展"这个名字需要一个变化率, 而设计只供给一次快照。
⚠️结论的换写 ⟦H⟧⟨early detection of advanced-phase histology among selected patients who survived to biopsy⟩ ⇎ ⟦H⟧⟨rather than directly observed pathological acceleration⟩ ⇎ ⟦H⟧⟨before this uncommon cohort informs prognostic enrichment or trial eligibility criteria⟩ ⇒ 批评不以推翻关联为终点, 而以限制它被用在哪一处为终点。
🧯修法清单的层级 ⟦H⟧⟨reporting modality by progression group and an open-lung-biopsy-only sensitivity analysis would be informative⟩ ‖ ⟦H⟧⟨phase-specific estimates, an interaction test, and a sensitivity analysis excluding exudative cases⟩ ⇎ ⟦H⟧⟨the estimates should be relabelled or risk ratios estimated with modified Poisson regression⟩ ⇒ 每条异议都配一个能直接执行的替代分析, 措辞本身按可执行性分档：⟦H⟧⟨would be informative⟩ ⇎ ⟦H⟧⟨would be preferable⟩ ⇎ ⟦H⟧⟨is material⟩。
🈳强度词 ⟦H⟧⟨If feasible, dual blinded review with an agreement statistic would further strengthen reproducibility⟩ ⇎ ⟦H⟧⟨Separate models with collinearity diagnostics would be preferable⟩ ⇎ ⟦H⟧⟨this distinction is material⟩ ⇒ 同一份批评里三种力度的建议词共存, 力度本身编码了作者对可执行性的判断。
🧭偏倚家族的名称 ⟦G⟧⟨prevalence-incidence (length-biased) sampling⟩ ⇎ ⟦H⟧⟨creating potential immortal-time bias⟩ ⇎ ⟦C⟧ 侧这两个词都不存在(机检 0 次) ⇒ 同一处缺陷在 ⟦G⟧ 那里属于患病率—发病率偏倚家族, 在 ⟦H⟧ 那里被专门称作不朽时间; 命名口径不同但都不可从 ⟦C⟧ 内部读出。
🪞回读题面 ⟦G⟧⟨Also the task: "Where the direction of bias cannot be determined from the information given, say so explicitly rather than guessing."⟩ ⇎ ⟦D⟧⟨the question says "Where the direction of bias cannot be determined from the information given, say so explicitly rather than guessing."⟩ ⇒ 两份推理链都停下来重读指令再决定如何措辞; 指令里的"不要猜"是它们保留态度的外源。
📊计量对照 ⟦C⟧正文 62261 ⇎ ⟦H⟧正文 14683 ⇎ ⟦D⟧推理 63864 成稿 18046 ⇎ ⟦G⟧推理 116213 成稿 11188 ⇒ 两条链的推理区都比它所评论的两份人类文本长, 而成稿比原文短; 想得多的那一条写得更克制。
🈳语言漂移 ⟦C⟧ 41899 个字母 ⇎ ⟦H⟧ 10953 ⇎ ⟦D⟧ 49907 ⇎ ⟦G⟧ 90560, ⟦G⟧ 的推理区实测 2 个汉字 ⇎ 其余三源 0 个 ⇒ 四源同为英文, 但跨源比术语计数前必须先量书写系统: 一次"0 次命中"可能只是"没用这种语言写"。
∴骨架 ① 分组信息晚于随访起点 ⇒ 风险集被"活到活检"筛过; ② 两组的活检间隔之差就是被保证存活的之差, 但作者用"存活者与死亡者间隔无差异"回应, 这两件事不在同一维度上; ③ 复合定义把两种时相合起来 ⇒ 稀疏格子的估计不稳, 而合并本身在报告里不可见(分母换了); ④ 阈值有预设与搜索两种来源, 后者在同一队列里会挑出显著的那个; ⑤ 检出率随取材方式变 ⇒ 相位与结局共享一个取材通道; ⑥ 两变量在代数上相关时, 多元模型给出的不是两个独立效应; ⑦ 表头标签与模型族不符, 错标对作者不可见, 对读者放大; ⑧ 未写的流程只能作缺席证据, 缺席证据的措辞要用"可能"; ⑨ 结论的用途(试验富集/入组标准)比结论本身更需要被限制; ⑩ 模型的长处是穷举、命名与回读指令; 短板是算术复核 ⑪ 同一模型族内, 一个复述了延迟入组, 另一个从未听过它——模型间方差大于人⇎机之差的一部分, 短处是把方向符号固定得太早, 且从不复核数字。
ℒmethod 面对一份把分组定义在随访中后段才确定的研究报告: 先把"分组用了哪一天的信息"与"随访从哪一天起算"并排放, 若晚于起算, 则不论组间间隔差是否显著都存在风险集问题; 修法是把晚到的信息写成入组时刻而不是协变量。判定一个复合表型是否被"合并"偷走了信息: 把每个时相的例数与事件数按组摊开, 任一格小于 10 例即禁止做层内推断, 并对每个百分数追问分母。见到两个共享分子的生理指标同入一模型, 先查代数耦合再谈混杂。表头效应量名称必须与模型族核对——正文没有出现的那个词就是错标的信号。对"方法里没写"的质控, 用"可能未做"而不是"未做"。批评一份研究时, 把结论能支持的用途写出来, 而不是只写效应量大小。给一份盲评清单时, 检查它是否算过一次数: 条目数与算术复核次数不成正比。

## ⛓解读注
※体例 ⟦C⟧＝J Intensive Care 2026《The relationship between the chronological phases of diffuse alveolar damage and clinical outcomes in ARDS》研究正文（PMC13520162，62261 字符）⇎ ⟦H⟧＝同刊同期通信《Rapid progression of diffuse alveolar damage in ARDS…》（PMC13625332，14683 字符，逐条针对 ⟦C⟧）⇎ ⟦D⟧与 ⟦G⟧＝把 ⟦C⟧ 的设计与数据改写成题面、不附 ⟦H⟧，发给两个免费推理模型的思维链（deepseek-v4.1-flash ⇎ glm-5.3-flash，题面哈希 c083d5f58453de1e，两份文件一致）。每个 `⟨⟩` 须逐字回自己标签的源（T3 机检，`corpus/raw/probe/_b37check.py`），前贴单字母出处标签；⟦C⟧⟦H⟧ 按 Europe PMC fullTextXML 剥标签后的原样正文，⟦D⟧⟦G⟧ 按 fetch_cot 原样落盘的推理区与成稿区，均未改写。
※派生算术与计数（机器复核，`corpus/audit.py` DERIV[B37]） 0＝CNT("immortal",⟦C⟧)＋CNT("blinded",⟦C⟧)＋CNT("odds ratio",⟦C⟧)＋CNT("delayed entry",⟦C⟧)＋CNT("mathematical coupling",⟦C⟧)＋CNT("denominator",⟦C⟧)＋CNT("prevalence-incidence",⟦H⟧)＋CNT("length-biased",⟦H⟧)（被批评的那篇论文叫不出这四个诊断名词，而批评侧也不借用流行病学课本的家族名——两侧各自的术语缺席都是断言）‖ 33＝CNT("immortal",⟦D⟧) ⇎ 57＝CNT("immortal",⟦G⟧) ⇎ 0＝⟦C⟧ 侧（模型把术语叫了几十次，作者一次也没有）‖ 44＝CNT("guaranteed",⟦G⟧)‖ 4＝⟦H⟧ 的 First/Second/Third/Finally 四段 ⇎ 5＝⟦C⟧ 的 First…Finally 五段自述局限 ⇎ 30＝⟦D⟧ 成稿的编号条目数（ACNT）‖ 25＝round(21÷84.0%×100)（"84.0%"只可能来自分母 25）⇎ 23＝21＋2（表内合计）⇎ 91.3＝round(21÷23×100,1)——三个百分数之间的裂缝是 ⟦H⟧ 的全部力气所在‖ 5.9＝11.3−5.4‖ 90＝27＋21＋36＋2＋4‖ 66.9＝round(81÷121×100,1) ⇎ 21.2＝round(11÷52×100,1) ⇎ 3＝round(66.9÷21.2)（两个模型都写了这两个百分数，都没有做过这道除法：CNT("5.9",⟦D⟧)＝CNT("5.9",⟦G⟧)＝0）。
※隐性知识的所在 十一处，没有一处能在 ⟦C⟧ 单份文件里读到：①分组信息晚于随访起点这件事，作者用"存活者与非存活者的活检间隔无差异"（p＝0.914 那一类比较）来回应，而 ⟦H⟧ 指出比较的不是被问的问题——同一统计量在两源中的证明力相反；②不朽时间偏倚的术语能被两个局外人立刻叫出（33、57 次），作者通篇用"timing bias"绕开；③修法有精度差：⟦H⟧⟨left-truncated Cox…delayed entry⟩ 把入组时刻写进风险集，⟦D⟧ 只给"landmark／time-dependent"的通用套路（该术语 0 命中），⟦G⟧ 却复述了一次——同一模型族内的方差大于人⇎机之差的一部分；④方向的保留也有精度差：⟦H⟧ 连符号都不给（"net direction…cannot be determined"），⟦D⟧ 拒绝给数值却固定了符号（"structural bias is away from the null"），⟦G⟧ 写"Direction cannot be determined"；⑤同一个百分数换分母即换结论（84.0% ⇎ 91.3%），而 ⟦D⟧ 全篇不提分母、⟦G⟧ 只称"small-denominator artifact"；⑥预设阈值与同一队列里 ROC 搜出的阈值在报告中同形，显著性来源不可辨；⑦检出率随取材方式变（66.9% ⇎ 21.2%），作者把它写成技术差异，⟦H⟧ 把它写成分组共享的混杂通道；⑧"方法里没写"在两源都只作缺席证据用（措辞是"可能"与"if feasible"），不是定罪；⑨表头自称 Relative risk 而模型族写在同一行表题里，正文从不出现比值比一词——错标对内部读者结构性不可见；⑩两个模型都会停下来回读题面里"不要猜"那句指令，并把保留态度写成对指令的执行；⑪⟦C⟧ 在同一句里让"限制"既充当外部效度的代价又充当它的保证。
※抓取与失真 ⟦C⟧⟦H⟧ 走 Europe PMC `…/rest/PMC…/fullTextXML`，`corpus/fetch_prose.py pmc <PMCID> <slug>`；⟦C⟧ 原为 ⟪H⟧ 篇引文（参考文献 1）经检索取得。剥标签保留了 JATS 的下标拆行（写作「PaCO 2」「PaO 2 )/F I O 2」）与未解码实体（`p &lt; 0.001`），因此 ⟦C⟧ 侧锚点一律避开含实体的片段，含拆行的分子式锚取 ⟦H⟧ 侧（那里写作 PaCO2 无空格）——同一术语在两源的字面形状不同，逐字核验必须按标签回自己的文件，跨源比对会假命中。⟦D⟧⟦G⟧ 走 `corpus/fetch_cot.py`（opencode 后端 :10001 直连，取回 reasoning 与 text 两类 part），题面由 ⟦C⟧ 的设计与数据改写而成，不含 ⟦H⟧ 的任何结论；题面原文完整保存在两份 raw 的 `## [[PROMPT]]` 段，两份的 prompt_sha256 实测一致。`chars`／`text_sha256` 按剥标签后的正文重算，推理区与成稿区的长度取自 raw 头部自记字段并与实算比对。
※四源对齐 68 个锚全部逐字命中自己标签的源（`_b37check.py`：ok=68 bad=0）；⟪摘要段⟫按标签分节，⟦C⟧2436 ⇎ ⟦H⟧4401 ⇎ ⟦D⟧1655 ⇎ ⟦G⟧1485 字符，共 35 个命中窗口。2 个锚在多个源里都能作为子串命中（数字与套语一类），归属仍由前贴标签决定。独有段＝⟦C⟧ 的表 4／表 6 数值与五段自述局限 ⇎ ⟦H⟧ 的四条异议与替代分析清单 ⇎ ⟦D⟧⟦G⟧ 的推理区独白（含"让我先想清楚方向""目标 25 条"一类的自我调度）。
※实况: 编码 7896(含换行; audit 去换行口径 7870) ⇎ 分源摘要 C 2436／H 4401／D 1655／G 1485(合 10183, 68 个锚落 35 个窗口) ⇎ raw 正文 286263 字符／293787 字节; 保留率 77.3%(÷摘要段) ⇎ 2.749%(÷四源正文) ⇎ 2.679%(字节口径＝audit 表列÷raw 源); 锚 68 个(⟦C⟧16 ⇎ ⟦H⟧36 ⇎ ⟦D⟧9 ⇎ ⟦G⟧7), 锚内字母 4074 ⇎ 锚内汉字 0, 锚外字母 109 = 出处标签 103 + 其余 6(仅 ℒmethod 自身); 判词层 0 ‖ 骨架与 ℒmethod 778; 推理区 C 62261 ⇎ H 14683 ⇎ D 63864 ⇎ G 116213, 成稿区 D 18046 ⇎ G 11188; T1／T2／T3 失配 0, 待核小整数 0 条。
※保留率口径 表列 77.3%＝编码 7870÷摘要段 10183；换成源正文口径＝2.749%(编码 7870 ÷ 四源 286263)，字节口径 2.679%。这里的低密度不是裁剪出来的：四源正文共 286263 字符（其中两条模型推理链就占 180077），编码只取 68 个锚引用了 4074 个字母，占四源字母总量 1.9%——绝大多数源文本（表格数字、参考文献、逐条复述的定义、模型的自我调度）根本没有被引用。编者层(判词 0 + 骨架与 ℒmethod 778 ＝778 字)是新增推理，行文动词层 7092 字。密度在"三源并置才成立"的断言里而不是在篇幅里：术语在场与缺席（0 ⇎ 33 ⇎ 57）、方向是否被固定（符号未定 ⇎ away from the null）、分母之差（25 ⇎ 23 ⇎ 91.3% ⇎ 84.0%）、减法是否发生过（5.9 ＝ 11.3−5.4，两模型各 0 次）这四组结论都必须跨源才成立，且全部可机检。
