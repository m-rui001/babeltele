# B17 — 隐性评审推理：AI 再定位药物的八步证据闸门与"不可补偿"评分（Front Pharmacol 2026, PMC13631471）
src: corpus/raw/prose/pmc_mechaware_ai_drug.txt (Europe PMC, 175 396 chars)
dir: corpus/babeltele/B17_mechanism_ai_gatekeeping.md

## [[原始语料|ORIGINAL]]
The core gap: Prediction is not pharmacological evidence Although AI has substant

does not establish therapeutic plausibility ( Liu et al., 2021 ; Yan et al., 2024 ).

target trial emulation” OR translational OR val

expert-assisted hypothesis-generation and evidence-synthesis tools whose outputs require source verification, uncertainty assessment, and human oversight ( Huaneg et al., 2024 ;

This problem is particularly consequential in pharmacology because a fabricated drug–target interaction, pathway relationship, dose, contraindication, or safety signal could create a mechanistically plausible but erroneous repurposing hypothesis. Importantly, linguistic confidence should not be interpreted as epistemic confidence.

uncertainty estimation does not detect all systematic errors and therefore cannot itself guarantee factual reliability ( Farquhar et al., 2024 ).

may provide incomplete measures of uncertainty.

employed the NLP screening of ∼1.3 million MEDLINE abstracts to prioritize a list of 3,539 already available drugs for testing in l-DOPA in

These methods are therefore complementary, but they are implemented at different steps, and do not constitute a single candidate-level pathway from computational predi

a clear next translational action. Figure 2 presents an idealized sequence to explain the proposed framework, but it is not meant to be interpreted as linear.

an adverse pharmacovigilance signal might lead to a re-evaluation of earlier evidence, or

While favorable evidence elsewhere may support a progression, the safety concerns can stop the progression, and missing or conflicting evidence can lead to further validation instead of the progression. The figure is, therefore, not a validated universal pathway of development but rather an organizing decision architecture, whose gates and priorit

Infographic illustrating an eight-step workflow for AI-driven drug candidate evaluation, including prediction, m

drug→target→pathway→biomarker/phenotype mapping plus causal plausibility

The vast majority of current computational and graph-based approaches tackle what drug to prioritize and to a lesser extent, why a model predicts to prioritize that drug.

This is important because biological plausibility does not constitute causal proof. A target may be associated with a disease without necessarily representing a therapeutically actionable target.

A biomarker could be related to outcome but not influence treatment response. Thus, future re-purposing based on AI should not be entirely based on association-based evidence; it should also consider causal evidence.

Safety assessment should not come after candidate ranking, as the value of an unsafe candidate, whatever computational score it has, is limited. While repurposed drugs may have well-established safety profiles, the profile could differ in another population, with a different dose, for more extended periods of time, or when combined with other treatments. The safety screening should encompass assessment of the drug’s ADMET profile, organ-specific

The structured review should then generate domain scores, as well as a documented rationale, and a recommended disposition (e.g., experimental test

This allows for human oversight of concerns not captured in the AI-generated content such as ethical, patient acceptability, unusual contraindications, monitoring needs, and regulatory constraints.

Evidence gathered over the course of the framework helps stakeholders decide on next steps. The results should not be a ranked list of drugs. Instead, the candidates should be sorted by the strength of the mech

Mechanism, safety, feasibility and clinical relevance can be scored 0–2 for each candidate, giving a maximum total score of 8 points. These are suggested thresholds that can be used as practical decision criteria for the framework and not as validated regulatory thresholds. More importantly, there is no “compensation” for major safety issues in the aggregate score, that is, the exposure s

High priority candidates tend to score 6–8 overall, with no outstanding major safety concern and no domain that scores 0 as a result of substantive adverse evidence.

Candidates scoring 6–8, with no score of 0 or major safety concern, are high priority; those scoring ≤5 due to weak or adverse evidence are low priority, while substantial missing or conflicting evidence indicates insufficient evidence. Major safety or feasibility concerns override the total score. These thresholds are proposed decision aids, not validated regulatory cut-offs The framework represents

Instead of the workflow ending with a candidate’s score or an explanatory path, evidence gathered is converted into the next action in the workflow.

In ACTT-2, 1,033 hospitalized patients were randomized to baricitinib plus remd

The difference in mortality between baricitinib and placebo observed over 28 days (8% versus 13%, respectively; HR 0.57, 95% CI 0.41–0.78) is therefore also a sec

Metformin produced the strongest and most consistent signal, with a meta-analytic HR of approximately 0.67, corresponding to a 33%

## ⟪BabelTele⟫
{🚪核心命题: ⟨Prediction is not pharmacological evidence⟩ ‖ ⟨does not establish therapeutic plausibility⟩[预测≠药理证据] ‖ 缺口: ⟨do not constitute a single candidate-level pathway⟩⇒⟨a clear next translational action⟩
🧰工具定位: ⟨expert-assisted hypothesis-generation and evidence-synthesis tools⟩⇒⟨source verification, uncertainty assessment, and human oversight⟩ ‖ 幻觉危害: ⟨a fabricated drug–target interaction, pathway relationship, dose, contraindication, or safety signal⟩⇒⟨erroneous repurposing hypothesis⟩ ‖ ⟨linguistic confidence should not be interpreted as epistemic confidence⟩[流利≠可信] ‖ ⟨uncertainty estimation does not detect all systematic errors⟩ ‖ ⟨may provide incomplete measures of uncertainty⟩[三代理=词元概率/模型自评/表面置信 ⇒ 不确定性代理不完备]
🧱八闸门: ⟨eight-step workflow for AI-driven drug candidate evaluation⟩[预测→机制→因果→安全→药物警戒→真实世界→专家评审→优先级] ‖ 机制映射写法 ⟨drug→target→pathway→biomarker/phenotype mapping⟩
⚖️两条设计律: ①⟨Safety assessment should not come after candidate ranking⟩⇒⟨the value of an unsafe candidate⟩[分数再高亦有限; 安全=前置闸门非后置扣分] ‖ 老药特性随 ⟨another population, with a different dose⟩‖⟨more extended periods of time, or when combined with other treatments⟩ 改变 ‖ 筛查面 ⟨safety screening should encompass assessment of the drug’s ADMET⟩[器官毒/相互作用/禁忌/剂量可行/人群特异] ②⟨evidence gathered is converted into the next action in the workflow⟩⇒输出是动作不是分数
🎯优先级=分箱: ⟨should not be a ranked list of drugs⟩ ‖ 排序五维 ⟨the candidates should be sorted by⟩[机制强度·机制安全·因果可信·真实世界支持·可行] ‖ 打分 ⟨can be scored 0–2 for each candidate, giving a maximum total score of 8 points⟩ ‖ 高档 ⟨tend to score 6–8 overall, with no outstanding major safety concern⟩[占比派生 0.75] ‖ ⟨those scoring ≤5 due to weak or adverse evidence are low priority⟩ ‖ ⟨substantial missing or conflicting evidence indicates insufficient evidence⟩[第三箱=证据缺失非阴性]
🚫不可补偿律(全文最可迁移): ⟨there is no “compensation” for major safety issues in the aggregate score⟩ ‖ ⟨concerns override the total score⟩[否决权优先于加权和]
🏷️数字状态标注: ⟨suggested thresholds⟩ ‖ ⟨practical decision criteria for the framework and not as validated regulatory thresholds⟩ ‖ ⟨proposed decision aids, not validated regulatory cut-offs⟩[地位=决策架构]
🔁非线性回炉: ⟨not meant to be interpreted as linear⟩ ‖ ⟨an adverse pharmacovigilance signal might lead to a re-evaluation⟩ ‖ ⟨the safety concerns can stop the progression⟩⇒⟨further validation instead of the progression⟩ ‖ 自我降级 ⟨organizing decision architecture⟩
🧭因果闸门: ⟨biological plausibility does not constitute causal proof⟩ ‖ ⟨associated with a disease without necessarily representing a therapeutically actionable target⟩ ‖ ⟨related to outcome but not influence treatment response⟩[关联≠可行动] ‖ ⟨target trial emulation⟩[随机试验不可得时的替代法] ‖ 人审 ⟨a recommended disposition⟩ ‖ ⟨ethical, patient acceptability, unusual contraindications⟩ ‖ ⟨and regulatory constraints⟩[覆盖模型未捕捉项]
📊定位对照: ⟨approaches tackle what drug to prioritize⟩[只答选谁不答能否用] ‖ 漏斗 ⟨1.3 million MEDLINE abstracts⟩⇒⟨3,539 already available drugs⟩⇒筛出率 0.27% ‖ ⟨1,033 hospitalized patients were randomized⟩ ‖ ⟨8% versus 13%, respectively⟩ ‖ ⟨HR 0.57, 95% CI 0.41–0.78⟩[次要终点·多重校正后不显著] ‖ ⟨a meta-analytic HR of approximately 0.67⟩[残余/未测混杂]
∴骨架: ①先命名失败模式(预测≠证据), 再一句话定义缺口 ②能力声明降级为须核验的假设生成 ③安全/可行性=否决门而非权重项⇒评分须可被单域 0 分推翻 ④输出由排名改动作分箱(高/低/证据不足) ⑤阈值自标"未验证"⇒框架=决策架构 ⑥后阶段证据可回炉前阶段 ⑦关联强度与因果可行动性分闸
📮术语/位置锚点: ⟨it should also consider causal evidence⟩ ‖ ⟨Evidence gathered over the course of the framework helps stakeholders decide on next steps⟩

## ⛓解读注
⟨…⟩=raw 逐字段(audit.py prose_norm 逐字校验) ‖ ⇎对照 ∥并列 ⇒推出 ∧且 ≈约 🎯分箱 🚫否决门 🔁回炉 🧭因果闸 📮锚点
※派生算术: 0.75=round(6/8,2)(高档阈值占满分比), 0.27=round(3539/(1.3×10^6)×100,2)(筛出率)。其余数字(8/0–2/6–8/≤5/0/1,033/8%/13%/0.57/0.41–0.78/0.67/1.3/3,539)全为源内原值。
※隐性知识=评审判断习惯(安全前置/拒排名/阈值自标未验证/证据缺失独立成箱); 2026 Front Pharmacol, DOI 10.3389/fphar.2026.1915973。
