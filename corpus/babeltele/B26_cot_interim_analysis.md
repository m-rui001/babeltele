# B26 — 模型思维链语料：期中分析的三态裁决（"未定"⇎"阴性"⇎"成立"）与 estimand 不可事后替换（deepseek-v4.1-flash, reasoning 127 381 字符, 题面=随机 III 期肿瘤研究 PFS/BICR, O'Brien-Fleming 边界）
src: corpus/raw/cot/bio_stat_interim.md (opencode/deepseek-v4.1-flash-free, prompt_sha256 50b0b4e84f19bcf6, reasoning_chars 127381, retrieved 2026-10-19T19:08:13)
dir: corpus/babeltele/B26_cot_interim_analysis.md

## [[原始语料|ORIGINAL]]
Crossover/curve convergence means average HR may dilute later benefit; early separation delayed.

The boundary p should correspond to actual information time, not fixed 0.0117? Need discuss.

O'Brien-Fleming alpha spending often Lan-DeMets: α(t)=2-2Φ(z_{α/2}/√t) two-sided or one-sided? Boundary 0.0117 at 250 events.

Because non-PH and curves cross/converge, RMST difference over clinically relevant horizon, with tau pre-specified before unblinding (e.g., 24 months), adjusted for stratification. Estimating expression: ΔRMST(τ)=∫_0^τ [S_exp(t)-S_ctrl(t)] dt, estimated via Kaplan-Meier ∫ \hat S dt; variance via Greenwood/influence functions; covariate adjustment stratified.

Need note RMST requires sufficient follow-up beyond τ; if τ is too long, estimate unstable.

Also Cox only covariate not stratified, so not the pre-specified stratified analysis; potential confounding due stratification factors (though randomization balances).

Actually under exponential, median exp = ln2/λ_exp = (λ_c/λ_e)*median_c = 5.1/0.71 = 7.18, difference 2.08, not 0.7.

So median difference and HR tell different stories, evidence of non-PH.

If protocol says death is event, the estimand is composite "time to progression or

Also among 262 events, 31 are deaths without progression = 11.83%; by arm? Need total events by arm not given. We cannot compute event counts per arm from HR/medians. Maybe can bound: overall events 262; deaths without progression 31; if all known, progression events 231.

Not recover because need event times and censoring.

The stratification variables site and prior therapy were used in randomization/stratified log-rank; they protect against imbalance in those factors and ensure valid stratified test, but do not make subgroup effects causal or provide power; stratification does not test interaction or control multiplicity.

The specific bias: "immortal time bias"? Or "spectrum bias"? Need identify. If comparing to historical controls or external cohort, "confounding by indication" and "selection bias." The phrase "specific bias that makes the comparison non-transferable" may expect "surrogate endpoint bias" or "measurement bias" d

Need state cannot contribute confirmatory evidence of PFS; can only generate hypothesis that biological activity exists and support consistency of direction, but not validate. It cannot answer whether PFS benefit is real.

Need be specific: - Final/planned total events and alpha-spending function details (one-/two-sided, Lan-DeMets OBF, information times, actual data cutoff); whether 262 is overrun or unplanned look; any prior/future looks; DMC charter; treatment-effect estimates at actual 262.

- Independent BICR audit and concordance; ORR definition and assessment; PFS event adjudication. - Cause-specific event times and death dates; whether deaths after progression; competing risk.

- OS data maturity. Two most important: (1) actual alpha-spending/information time and number of looks—direction could move con

Actually OBF boundary gets more stringent with more events; so p=0.0132 vs 0.0117 is not crossing; if boundary at actual 262 is maybe >0.0132? Wait OBF boundary decreases with more information, so at 262 boundary <0.0117, so still not crossing.

If one-sided p=0.0117: z1=2.266 (tail .0117). z2=2.214. One-sided p=0.0134. So 0.0132 is just below one-sided 0.0134, just above two-sided? Wait p=0.0132 < 0.0138, so crosses two-sided; <0.0134 crosses one-sided.

This suggests either fewer events in Cox (e.g., missing covariates) or CI not from 262? Wait Cox with treatment only, all events = 262; variance of log HR ≈ 1/d1+1/d0.

So events could be 190 vs 72.

The fact observed CI width implies ~208 events (effective) while 262 observed could indicate the HR/CI from a different dataset/look or unstratified model with missing data.

The median difference can be computed from KM but its CI needs Greenwood; not given.

But test has power dependent on events; p=0.0041 strong evidence of time-varying HR.

If the question is progression, death before progression is a competing event; cause-specific hazard for progression treats death as censoring (estimates hazard among those still progression-free and alive), while subdistribution hazard/Fine-Gray estimates cumulative incidence of progression with death as competing.

This can be valid but interpretation must be "time to progression or death," not "progression." Also "death is an event" avoids informative censoring by death for composite, but it may introduce treatment effect on mortality into PFS.

- Category error: PH is a property of a model/summary, not of trial validity. Randomization and log-rank test do not require PH for validity under sharp null; non-PH affects estimand/power, not internal validity. "Negative" is not equivalent to "did not cross interim boundary." A trial can be positive on a time-averaged or RMST scale even if PH fails; conversely, failure to reject at interim does not prove no effect.

- Assertion B: "Switch to ORR because survival data contaminated." - Category error: ORR is a different endpoint with different estimand; cannot be substituted post hoc for PFS. Changing primary endpoint after unblinding invalidates type I error and is outcome-dependent.

12 or 14 months based on clinical relevance and follow-up, not data.

Approx 1:1 => 44 per arm, ~20.5 events per arm.

The DSMB chair's statement "must be reported as negative" is wrong because a non-significant interim does not establish no effect; "negative" requires futility boundary or final analysis.

The chair's second assertion "switch to ORR because survival contaminated" is a category error: changing endpoint post hoc; ORR is not a survival endpoint; death is protocol event; contamination implies informative censoring, not death as event; no evidence data are contaminated.

Need discuss "overall response rate" as endpoint: ORR is binary, often assessed at a landmark; it ignores time, censoring, and durability.

It is not a surrogate for PFS unless validated.

Need maybe discuss "alpha spending assumes when and how often the look happens" explicitly: - Assumes look times are fixed in advance in terms of information (event counts), not chosen after seeing unblinded results.

This strengthens "cannot compare." We can say "the exact boundary cannot be computed; do not use .0117 as if it were the 262-event boundary." Good.

The point is the comparison is unresolved, not that efficacy is proven." This is honest. Let's verify the first-order formula for one-sided/two-sided: If p_boundary(t)=2[1-Φ(z_{α/2}/√t)], then p(t2) from p(t1) by z2=z1√(t1/t2).

Need maybe mention "tail based on 18 patients at risk" means the convergence after 14 months is based on very few patients; cannot claim late convergence/null.

We can say "I cannot verify scale; if .0117 is one-sided and .0132 is two-sided, the correct comparison is .0066 vs .0117 and the result crosses." This is a number we can compute.

Unplanned look later inflates type I unless boundaries recomputed; current result may no longer cross; multiple endpoints/subgroups not accounted. - Therefore the committee's reading "p=.0132 > .0117 so negative/just missed" is not warranted.

## ⟪BabelTele⟫
{🧭体例: 草稿态祈使句(⟨Need discuss⟩)即思维本身, 不通顺化 ‖ 锚只取 ⟪REASONING⟫ 区; 题面事实是我写的题目, 只以中文转述
🚫断言一(PH 失败⇒试验无效)=范畴错: ⟨PH is a property of a model/summary, not of trial validity⟩ ‖ ⟨Randomization and log-rank test do not require PH for validity under sharp null⟩ ‖ ⟨non-PH affects estimand/power, not internal validity⟩
🚫断言二(改用 ORR)=范畴错＋无支持: ORR≠PFS: ⟨cannot be substituted post hoc for PFS⟩ ‖ ⟨Changing primary endpoint after unblinding invalidates type I error⟩ ‖ 污染⇒informative censoring 而非死亡即事件: ⟨no evidence data are contaminated⟩
🛑三态: ⟨"Negative" is not equivalent to⟩ ‖ ⟨a non-significant interim does not establish no effect⟩ ‖ ⟨"negative" requires futility boundary or final analysis⟩ ⇒ 未定 ⇎ 阴性 ⇎ 成立
🔬estimand 由规程句锁定: ⟨the estimand is composite⟩ ⇒ ⟨interpretation must be "time to progression or death,"⟩ ‖ 两分叉 ⟨cause-specific hazard for progression treats death as censoring⟩ ⇎ ⟨subdistribution hazard/Fine-Gray⟩ 估 CIF(death 为 competing) ‖ 两面代价 ⟨avoids informative censoring by death for composite⟩ ⇎ ⟨may introduce treatment effect on mortality into PFS⟩
🧮可算 ⟨overall events 262; deaths without progression 31; if all known, progression events 231⟩ ‖ ⟨31 are deaths without progression 11.83%⟩ ‖ 不可算 ⟨We cannot compute event counts per arm from HR/medians⟩ ‖ ⟨not recover because need event times and censoring⟩ ‖ ⟨its CI needs Greenwood; not given⟩
🎚边界口径 ⟨The boundary p should correspond to actual information time, not fixed 0.0117⟩ ‖ ⟨O'Brien-Fleming alpha spending often Lan-DeMets: α(t)=2-2Φ(z_{α/2}/√t)⟩ ‖ 单边 ⟨If one-sided p=0.0117: z1=2.266 (tail .0117). z2=2.214. One-sided p=0.0134⟩ ⇎ 双边 0.0138 ‖ ⟨So 0.0132 is just below one-sided 0.0134⟩ ⇒ 越界与否取决于谁都没标的口径 ‖ ⟨I cannot verify scale⟩ ‖ ⟨the exact boundary cannot be computed; do not use⟩ ‖ 委员会读法 ⟨p=.0132 > .0117 so negative/just missed⟩ ⇏ ⟨The comparison is unresolved, not that efficacy is proven⟩
⏳花费函数前提 ⟨fixed in advance in terms of information (event counts)⟩ ‖ ⟨not chosen after seeing unblinded results⟩ ‖ ⟨OBF boundary gets more stringent with more events⟩ ‖ ⟨Unplanned look later inflates type I unless boundaries recomputed⟩ ‖ ⟨multiple endpoints/subgroups not accounted⟩
📏主摘要: 两尺互证否 ⟨5.1/0.71 = 7.18, difference 2.08, not 0.7⟩ ‖ ⟨median difference and HR tell different stories, evidence of non-PH⟩ ⇒ 结论落在共用前提 ‖ ⟨average HR may dilute later benefit; early separation delayed⟩ ‖ 应答 ⟨RMST difference over clinically relevant horizon⟩ ⟨∫ \hat S dt⟩ ‖ ⟨variance via Greenwood/influence functions⟩ ‖ ⟨covariate adjustment stratified⟩ ‖ ⟨tau pre-specified before unblinding (e.g., 24 months)⟩ ‖ ⟨sufficient follow-up beyond τ⟩ ‖ ⟨estimate unstable⟩ ‖ ⟨based on clinical relevance and follow-up, not data⟩
🔍自洽核查: CI 宽度 ⇒ 有效事件数 208 ⇎ 观测 262 ⇒ ⟨fewer events in Cox⟩ ‖ ⟨the HR/CI from a different dataset/look⟩ ‖ 分臂反解 ⟨So events could be 190 vs 72⟩
🪜尾部 ⟨cannot claim late convergence/null⟩ ⇒ 风险集 18 人时的合拢是方差
🧷口径错位 ⟨not the pre-specified stratified analysis⟩ ‖ GT p=0.0041 已拒 PH, 但 ⟨test has power dependent on events⟩
🔎亚组 ⟨20.5 events per arm⟩ ‖ ⟨protect against imbalance in those factors⟩ ⇎ ⟨do not make subgroup effects causal or provide power⟩
🧪外部队列上限 ⟨support consistency of direction, but not validate⟩ ‖ ⟨It cannot answer whether PFS benefit is real⟩ ‖ ⟨it ignores time, censoring, and durability⟩ ‖ ⟨it is not a surrogate for PFS unless validated⟩ ‖ 具名偏倚 ⟨immortal time bias or spectrum bias need identify⟩, 草稿另列 ⟨surrogate endpoint bias⟩
❓缺项 ⟨Final/planned total events and alpha-spending function details⟩ ‖ ⟨actual alpha-spending/information time and number of looks⟩ ‖ ⟨whether deaths after progression⟩ ‖ ⟨Independent BICR audit and concordance⟩ ‖ ⟨OS data maturity⟩
🪞元层 ⟨This is honest.⟩
∴骨架: ①断言先分范畴错／无支持再分对错 ②"阴性"需被授权(优效界值或终分析) ③规程一句定义即锁定 estimand, 换分析=换问题 ④可算/不可算逐条划界并点名不可回收量 ⑤边界绑信息时间, 口径未标则拒选 ⑥主摘要合法性来自揭盲前定的量, τ 由临床与随访长度定 ⑦两摘要互相否证时结论是前提被推翻 ⑧给定数字先做自洽核查, 不自洽就怀疑出处 ⑨复合终点的收益与污染同源 ⑩风险集过小时的曲线形状不是证据 ⑪非预设模型的输出不充当主摘要 ⑫外部同量级结果只贡献方向一致性, 判不可迁移需具名偏倚 ⑬分层保检验效度, 不保外推与功效
ℒ: 判决分级≠统计公式——检验效度／估计量定义／看数时机／数字自洽／措辞强度 五层独立, 任两层合并即让诚实的数说出不诚实的话

## ⛓解读注
⟨…⟩=该模型 ⟪REASONING⟫ 区逐字锚(audit.py prose_norm 机检; 只留命名／口径／自限句／算式原样) ‖ ⇎并存或互斥 ⇒推出 ⇏不推出 [ ]=我的补足
※锚全部落在 ⟪REASONING⟫ 起点之后(逐锚验过); 题面 corpus/prompts/p_bio.txt 是我写的事实清单, 只以中文转述, 不冒充模型输出。
※草稿形状按原样: 待办形(Need discuss / We can say)、术语嵌引号(“Negative”)、数学记号与 ASCII 混排(α(t)=2-2Φ(z_{α/2}/√t) ⇎ 后文写 tau 而题面写 τ)、自问自答并以 Hmm / Let's compute / This is honest 收尾。
※数字全为源 reasoning 逐字值: z1=2.266→z2=2.214→单边 0.0134 ⇎ 双边 0.0138; 有效事件 208 ⇎ 观测 262; 分臂 190 vs 72; 231=262−31; 11.83%; 指数假设下 5.1/0.71=7.18 ⇒ 差 2.08 ⇎ 实测 0.7。DERIV['B26'] 为空。
※同题跨模型对照已落盘: bio_stat_interim_nemotron.md(reasoning 3 038＋成稿 15 488) ⇎ bio_stat_interim_glm.md(reasoning 101 421, 无成稿) ⇎ 本条(127 381, 无成稿)。
※与 [[B22]]／[[B25]] 同动作: 拒绝把"未定"写成"阴性"——报告分层"谁的护层缺席", 本条分层"哪一层证据不足以支撑这句话"。
