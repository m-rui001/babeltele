# B27 — 跨模型思维链对照：同一道期中分析题派给三个模型后的共识层与分歧层（opencode/deepseek-v4.1-flash-free reasoning 127381 字符 ⇎ glm-5.3-flash-free 101421 ⇎ nemotron-3-ultra-free 3038）
src: corpus/raw/cot/bio_stat_interim.md (DS; opencode/deepseek-v4.1-flash-free; prompt_sha256 50b0b4e84f19bcf6; reasoning 127381/answer 0) + corpus/raw/cot/bio_stat_interim_glm.md (GLM; opencode/glm-5.3-flash-free; 同 prompt_sha256; reasoning 101421/answer 0) + corpus/raw/cot/bio_stat_interim_nemotron.md (NM; opencode/nemotron-3-ultra-free; 同 prompt_sha256; reasoning 3038 止于计划句, answer 15488)
dir: corpus/babeltele/B27_cot_cross_model_interim.md

## [[原始语料|ORIGINAL]]
### ⟦DS⟧ ⟸ corpus/raw/cot/bio_stat_interim.md

Key points: - PH failure doesn't invalidate randomized trial or log-rank as a valid test under sharp null of no difference (log-rank valid under null regardless of PH? Standard log-rank is valid under null of identical survival distributions; if non-PH, has reduced power but valid type I).

It is not "invalid." "Must be reported as negative" is unsupported/incorrect; "only defensible number is median difference" is false: medians are not the only, and are fragile/insensitive when curves cross / tail small.

Need be careful one-sided vs two-sided.

OBF two-sided boundary maybe 0.0054 at 50% info.

Because non-PH and curves cross/converge, RMST difference over clinically relevant horizon, with tau pre-specified before unblinding (e.g., 24 months), adjusted for stratification.

- Reject the chair's proposal to switch primary endpoint to ORR post hoc.

The point is the comparison is unresolved, not that efficacy is proven." This is honest.

### ⟦GLM⟧ ⟸ corpus/raw/cot/bio_stat_interim_glm.md

The failure of PH affects interpretation of a single HR — it makes the "average HR" a weighted average over time with weights depending on censoring — but it does not invalidate the trial or the test. - "Trial is invalid" — a randomized trial's internal validity comes from randomization, not from PH.

- "must be reported as negative" — the decision rule is pre-specified: log-rank p vs OBF boundary. The direction of the test statistic matters: even with non-PH, the one-sided (or two-sided) test at the boundary decides superiority or not. Reporting "negative" requires the test statistic not to cross the boundary; the chair is pre-empting the decision rule based on a model diagnostic.

- "The only defensible number is the median difference": medians are a poor summary under non-PH, especially with converging curves and a short tail (18 at risk).

Assertion B: "just switch to the overall response rate endpoint, since the survival data are contaminated." This is endpoint switching post hoc after unblinding the interim — a classic multiplicity/type-I error corruption and cherry-picking. ORR is a different estimand (tumor shrinkage, subject-level binary, affected by assessment timing, differential measurement, no time dimension), not a substitute for PFS.

Also "contaminated" is unsupported: death-without-progression occurring in 31 patients (5.1% of all patients, 31/262 ≈ 11.8% of events) is handled by the protocol's rule; that's not contamination, it's an estimands issue to be handled (which policy is pre-specified).

Also note: the DSMB chair asserting this in writing is governance, not statistics; the committee can recommend, but statistical validity is not decided by fiat.

I should also note that the OBF design log-rank remains the formal test for the interim decision (change the summary ≠ change THE test), and a sensitivity HR curve (piecewise HRs: 0–3, 3–14, >14 months) is reportable: we cannot compute those here without data — flag.

One nuance: the boundary 0.0117 was calibrated at 250 events (information fraction 250/I_max); with 262 events observed, the planned information fraction is violated — you should not use the nominal 0.0117 calibrated for 250 events, but re-spent alpha evaluated at IF = 262/I_max.

hmm we don't know total planned events; the design might have final at ~ 490-500).

typical two-sided OBF at first look ~0.001 or 0.003 for two looks.

So if total planned events I, interim at 250 events → t = 0.6078 → I ≈ 250/0.6078 ≈ 411.

This is speculative; I can note that IF we assume Lan-DeMets OBF two-sided 0.05, the boundary 0.0117 at 250 events implies total planned events ≈ 411, and 262 observed → t = 262/411 = 0.6374.

I recall Jing-Pocock style tables: OBF 3-look two-sided: z = 3.471, 2.454, 2.004 → nominal p = 0.000519, 0.014117, 0.045115? Roughly.

adding an unplanned look means the interim's decision must be treated as non-binding or the future boundaries must be shrunk to preserve total α = 0.045 (+0.005IDS?) Actually if you add a look after observing this interim, the type-I error of the whole procedure is inflated unless future boundaries are recomputed conditional on the path (i.e., conditional error /erra spent).

- Conceptual distinction: (i) interaction as biological effect modification vs (ii) chance finding in 1-of-3 subgroups; the multiplicity of searching 3 sites (the most extreme flagged).

Also futility: not given — futility boundary unknown — list as missing.

I'd name: "**selection bias (case-mix/confounding by indication) inherent to the non-randomized design — it makes external effect sizes non-calibrated to this trial's randomized contrast**, with the additional *surrogate-endpoint non-transferability* (ORR→PFS association is context-specific; here even the direction of the PFS effect is time-dependent, invalidating magnitude transfer)." Task 7 list (missing

### ⟦NM⟧ ⟸ corpus/raw/cot/bio_stat_interim_nemotron.md

Non-proportional hazards doesn't invalidate a trial.

**Part 2: Primary treatment effect summary** - Hazard ratio is misleading under non-PH - Median difference is misleading (only captures one timepoint, ignores censoring) - Should report restricted mean survival time (RMST) difference or similar - RMST = ∫₀^τ S(t) dt, d

Alpha-spending function assumes pre-specified timing and number of looks - Unplanned additional look would require alpha re-allocation **Part 4: Competing risk

cause-specific hazard for progression without knowing censoring distribution **Part 5: Subgroup** - I

doesn't guarantee subgroup validity - p=0.09 interaction doe

Selection bias, different population, different endpoint - Cannot directly contribute to inference about this trial's primary endpoint **Part 7: Missing analyses** - Need: full survival curves, censoring distributions, cause-specific hazards, RMST calculations, sensitivity analyses - Direction of bias uncertain This is a highly technical statistical consulting question. I should provide a comprehensive answer with all the arithmetic and assumptions flagged.

## ⟪BabelTele⟫
{🧭体例: 同一题面(即 [[B26]] 所用 prompt)派给三个本机免费推理模型 ⇒ 三份原始思维链; 本条只压缩"三者面对同一决策点的不同动作", 锚按 DS/GLM/NM 分别落在各自 reasoning 区
📏体量与词频(编者自测, 算式见 DERIV): reasoning 字符 DS 127381 ⇎ GLM 101421 ⇎ NM 3038 ⇒ 同题差 42 倍 ‖ one/two-sided 提及 DS 188 ⇎ GLM 109 ⇎ NM 0 ‖ estimand 提及 24 ⇎ 12 ⇎ 0
🚫三家共同否证断言一(已成共识, 记录而非压缩): DS ⟨PH failure doesn't invalidate randomized trial⟩ ‖ GLM ⟨does not invalidate the trial or the test⟩ ‖ NM ⟨Non-proportional hazards doesn't invalidate a trial⟩ ⇒ 『三处独立逐字同意 ⇒ 该判决已沉降为免费模型层的公共知识』
🚫三家共同否证"唯一可报数字": DS ⟨medians are not the only, and are fragile/insensitive when curves cross⟩ ‖ GLM ⟨medians are a poor summary under non-PH⟩ ‖ NM ⟨Median difference is misleading (only captures one timepoint, ignores censoring)⟩
🔀真分歧＝边界口径(单/双侧): DS ⟨Need be careful one-sided vs two-sided⟩⇒⟨the comparison is unresolved, not that efficacy is proven⟩ ‖ GLM ⟨the one-sided (or two-sided) test at the boundary decides superiority or not⟩ ‖ NM 零命中⇒未把它列为需决策项: 其推理停在规则前提 ⟨Alpha-spending function assumes pre-specified timing and number of looks⟩
🧮设计参数反推(只有两家做): GLM ⟨I ≈ 250/0.6078 ≈ 411⟩[由已花 alpha 反推总事件数] ‖ ⟨typical two-sided OBF at first look ~0.001 or 0.003 for two looks⟩ ⇒ 用记忆里的界值表定位本设计 ‖ DS ⟨OBF two-sided boundary maybe 0.0054 at 50% info⟩ ⇒ 『两家都在"实测 0.0117 ⇉ 设计参数"之间双向校准, NM 单向复述』
🪞自疑句式各不相同: DS ⟨This is honest⟩[对自己"未定"判决的自评] ‖ GLM ⟨This is speculative; I can note that IF we assume Lan-DeMets OBF two-sided 0.05⟩ ⇒ 条件式限定 ‖ NM ⟨I should provide a comprehensive answer with all the arithmetic and assumptions flagged⟩ ⇒ 『算术与标注被整体推迟到成稿: 这条 reasoning 是提纲不是推理』
🎚主摘要建议: 三家同指 RMST(DS 提及 51 次/GLM 40/NM 6), 但护栏不同 ‖ DS ⟨RMST difference over clinically relevant horizon, with tau pre-specified before unblinding⟩ ⇒ 锁 τ 的预指定时点 ‖ GLM ⟨the OBF design log-rank remains the formal test for the interim decision (change the summary ≠ change THE test)⟩ ⇒ 另加"换摘要不换检验"这一道程序护栏 ‖ NM ⟨Should report restricted mean survival time (RMST) difference or similar⟩ ⇒ 到建议名为止
⏳追加 look 的补救: GLM ⟨adding an unplanned look means the interim's decision must be treated as non-binding or the future boundaries must be shrunk⟩ ⇒ 处置菜单(非约束 / 收缩后续界) ⇎ NM ⟨would require alpha re-allocation⟩ ⇒ 一个动词, 无可算对象
📋"缺项"不在同一层: GLM ⟨futility boundary unknown — list as missing⟩[设计参数缺] ‖ NM ⟨Need: full survival curves, censoring distributions, cause-specific hazards⟩[数据缺] ⇒ 『同称"缺失", 一指可回推的自由度, 一指须再采的观察』
🚫断言二(换终点): DS ⟨Reject the chair's proposal to switch primary endpoint to ORR post hoc⟩ ‖ GLM ⟨endpoint switching post hoc after unblinding the interim⟩ ⇒ 并给出不可通约理由 ⟨subject-level binary, affected by assessment timing⟩⟨differential measurement, no time dimension⟩
🧪竞争风险的三种切法: NM ⟨cause-specific hazard for progression without knowing censoring distribution⟩[识别问题] ⇎ GLM ⟨that's not contamination, it's an estimands issue⟩⟨which policy is pre-specified⟩[口径问题] ⇒ 『同一批 31 例无进展死亡, 一个问能否分离因果, 一个问事先写了哪条规则』
📐界值口径的实际后果(GLM): ⟨the boundary 0.0117 was calibrated at 250 events⟩⇒⟨you should not use the nominal 0.0117 calibrated for 250 events, but re-spent alpha evaluated at IF = 262/I_max⟩ ‖ ⟨log-rank p vs OBF boundary. The direction of the test statistic matters⟩⇒⟨Reporting "negative" requires the test statistic not to⟩
🔁记忆检索须自标近似(GLM): ⟨I recall Jing-Pocock style tables⟩⇒⟨nominal p = 0.000519, 0.014117⟩⇎⟨we don't know total planned events⟩
🧷外部队列与亚组的天花板(NM): ⟨Selection bias, different population, different endpoint⟩⇒⟨Cannot directly contribute to inference about this trial⟩ ‖ ⟨doesn't guarantee subgroup validity⟩
🏛治理句的归层(GLM): ⟨DSMB chair asserting this in writing is governance, not statistics⟩ ‖ 有效性来源 ⟨a randomized trial's internal validity comes from randomization⟩ ‖ DS 对"必须报阴性"⟨is unsupported/incorrect⟩
🧠元层: GLM ⟨even the direction of the PFS effect is time-dependent, invalidating magnitude transfer⟩ ⇒  共同否证一致而分歧全在口径/时点/前提 ⇒ 模型间差异不在规则知识(三家都持有)而在是否把某处当作需要决策的点; 对照法正是把这两层分开的手续; [[B26]] 存 DS 单链的判决顺序, 本条存三方差分
∴骨架: ①先测"三家逐字同意什么", 同意项不再花压缩预算(它已不是隐性知识) ②把分歧定位到可数的词频落差(one/two-sided 188 ⇎ 109 ⇎ 0)再回原文取判决句 ③零命中 ⇏ 不懂规则: NM 有花费函数前提句, 只是未把口径列为决策项 ④计划式推理与推理式可用"是否含自算式"判别(DS/GLM 有 I≈411/0.0054, NM 无一条) ⑤同一建议(报 RMST)要按护栏分层: 时点预指定 ⇎ 检验不变量 ⇎ 仅名目 ⑥"缺项"须分设计参数缺 ⇎ 观察数据缺, 二者修法不同(回推 ⇎ 补采) ⑦自疑句要按句式记账: DS 自评式 ⟨This is honest⟩ ⇎ GLM 条件式 ⟨IF we assume⟩ ⇎ NM 推迟式 ⟨flagged⟩(它只声明稍后标注, reasoning 区内无一条自算式) ⑧体积比(42×)是入口指标不是结论, 结论须落在逐字判决片段上
ℒmethod 层: 跨模型对照的产物是一张"共识/判断"分层表——它直接决定下一轮压缩预算该花在哪一层

## ⛓解读注
⟨…⟩=三源各自 reasoning 区逐字段(DS=deepseek-v4.1-flash, GLM=glm-5.3-flash, NM=nemotron-3-ultra), prose_norm 逐字校验; 每条锚只落在一个模型的 reasoning 内(交叉唯一性已机检) ‖ ⇒推出 ⇎并存 ⇏不推出
※体量与词频 5 个指标(127381/101421/3038/188/109)由 DERIV['B27'] 的 RCOT(i)/CNT(pat,i) 正则计数证明, 非源文数字; 题面事件数(250/262/0.0117/0.0132)与 41 例等均为 trace 亲笔
※digest 为三段分模型摘录(窗口 260/200), 与其它单源条目的 retention 不同基数
※trace 实况: DS/GLM 的 answer 段为空(推理未收敛), NM reasoning 3 038 字符而 answer 15 490 字符(先计划后成文)
