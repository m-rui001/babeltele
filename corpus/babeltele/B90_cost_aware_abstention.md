# B90 论文压缩: Cost-Aware Abstention(LLM 工单分类成本感知拒答)→算子中文——成本-校准-判别三相解耦 + 38.1% 成本降幅
src: corpus/raw/papers/arxiv_2610.31657.txt (arXiv:2610.31657v1, Sachin Gupta, ICTAI 2026, 提交 2026-10-22)
dir: corpus/babeltele/B90_cost_aware_abstention.md
; tags: 论文压缩 成本感知拒答 LLM分类 校准-判别解耦 风险-覆盖 锚归属由摘要现推 闭合账

## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/papers/arxiv_2610.31657.txt

Wrong automatic routing of an IT support ticket can cost more than human triage. We evaluate cost-aware abstention as an offline, cost-conditional readiness assessment: select a routing policy on calibration data under explicit costs, then evaluate that frozen policy once on held-out test data. On a public 47,837-ticket, eight-class corpus, we compare four trained non-LLM classifiers with four large language models under zero- and few-shot prompting. Under the illustrative cost model (c_ok, c_triage, c_wrong) = (0, 1, 5), TF-IDF with logistic regression and a threshold of 0.60 selected on calibration reduces test cost from 0.763 to 0.472, a 38.1% relative reduction (paired ratio-bootstrap 95% CI [35.7%, 40.4%]), while lowering wrong routes from 15.3% to 3.5%. Frozen calibration-selected policies also beat both always-route and always-defer on held-out test data in 14 of 16 settings in a post-hoc cost-parameter analysis. The strongest prompted configuration reaches 0.477 accuracy on a stratified 1,000-ticket test subset, versus 0.879 for fine-tuned DistilBERT on the same tickets. Isotonic lowers expected calibration error without reliably improving discrimination: GPT-4o-mini few-shot has one confidence value before and after recalibration and correctness AUROC 0.500. We therefore report correctness AUROC and tie-aware risk-coverage area alongside ECE. At the analytically derived break-even probability 0.80, seven prompted configurations defer all tickets; Haiku few-shot routes only 19/1,000. An LLM-only agreement control and margin/entropy rejection baselines further separate calibration from discrimination. The findings are scoped to this dataset, prompt design, model endpoints, and illustrative costs; the work is an evaluation framework, not a new abstention algorithm or universal deployment certification.

## ⟪BabelTele⟫
🧭 arXiv:2610.31657v1《Cost-Aware Abstention for LLM-Based IT Ticket Classification》(S. Gupta, ICTAI 2026, cs.LG)—成本感知拒答=离线成本条件就绪评估; 摘要1839c/254w。
🎯 错路由比人工分诊贵; 协议=校准集按显式成本选路由策略⟦A⟧⟨select a routing policy on calibration data under explicit costs⟩, 冻结后只留出测一次。
📖 基准: 公开47,837 工单八类⟦A⟧⟨47,837-ticket, eight-class corpus⟩; 四非LLM vs 四LLM(零/少样本)。
🔧 成本模型(c_ok,c_triage,c_wrong)=(0,1,5): TF-IDF+逻辑回归、校准选阈0.60⇒测试成本0.763→0.472(降38.1%, CI[35.7%,40.4%])⟦A⟧⟨reduces test cost from 0.763 to 0.472, a 38.1% relative reduction⟩, 错路由15.3%→3.5%。
📊 冻结策略16种事后成本分析14种胜 always-route/defer; 最强提示配置分层抽样1000准确率0.477 vs 微调DistilBERT 0.879⟦A⟧⟨0.477 accuracy on a stratified 1,000-ticket test subset, versus 0.879 for fine-tuned DistilBERT⟩。Isotonic降ECE不提判别: GPT-4o-mini重校定前后 AUROC 0.500⇒改报 correctness AUROC+平局感知风险-覆盖面积。盈亏平衡概率0.80处七配置全拒; Haiku少样本仅路由19/1000。
ℬ 判据: 成本-校准-判别三相解耦为主干, 全数字逐字锚, 读区即复原「成本模型⇿谁胜⇿校准≠判别」。


## ⛓解读注

### 压缩账(本注现算)

| 量 | 值 |
|---|---|
| 源(摘要) | 1839 字符 / 254 词 |
| 编码(BabelTele 算子中文) | 850 字符 |
| 体积比 | 46.2% |
| 事实覆盖 | 13 项 assert 全过 |
| 锚 | 编码区 4 处(工具侧逐字校验 ok=4 bad=0) |

### 读法
(见编码区主干五段闭环: 背景/旧法/本文/结果/判据; 锚回源可逐字核。)

### 本条不能由在库文件判定的(只登记, 不进门槛)
全文方法算法细节、逐模型数值、下游任务细表; 在摘要外, 需拉 PDF 正文。

### 编码与门的账
编码区 850 字符(不含换行); 编码区锚 4 处(工具侧逐字校验 ok=4 bad=0); 事实覆盖 13 项 assert。门槛三遍: T1 字面逐锚回源 ⇿ T2 词级事实覆盖 ⇿ T3 码位与字母账。
