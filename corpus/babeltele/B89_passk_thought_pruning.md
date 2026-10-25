# B89 论文压缩: Direct Pass@k 思维剪枝(测试时推理, 质量-多样性权衡)→算子中文——pass@k 直接优化 + 八模型超越两类剪枝
src: corpus/raw/papers/arxiv_2610.31667.txt (arXiv:2610.31667v1, Salmani/Javanmard/Gupta/Razaviyayn, 提交 2026-10-22)
dir: corpus/babeltele/B89_passk_thought_pruning.md
; tags: 论文压缩 测试时扩展 思维剪枝 质量-多样性权衡 pass@k 探索-利用 锚归属由摘要现推 闭合账

## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/papers/arxiv_2610.31667.txt

Test-time scaling has emerged as a key inference strategy for reasoning models, where a model generates a large number of candidate solutions in the hope of finding at least one correct solution. Running all candidate solutions to completion can be computationally demanding, so recent work prunes the candidate pool after generating only a short prefix, committing further computation only to the surviving candidates. Existing pruning strategies divide broadly into two categories: Quality-based methods assign a score to each partial solution and discard those predicted to ultimately lead to an incorrect final solution, while diversity-based methods select partial solutions that follow different reasoning trajectories and are therefore likely to cover different final solutions. The tension between these two objectives is an instance of exploration versus exploitation, yet little to no prior work on pruning exposes this trade-off directly, let alone optimizes it. In this paper, we introduce a pruning procedure that addresses this trade-off directly by optimizing pass@k over the selected solution pool. In particular, it chooses the pool to maximize the probability that at least one of its partial solutions, when continued to completion, yields a correct answer. Because this objective simultaneously rewards high-quality partial solutions and penalizes redundancy among them, quality and diversity are naturally balanced by the criterion itself rather than through separate ad-hoc design choices. On eight open-weight reasoning models, our method outperforms existing quality-based and diversity-based pruning strategies. The gains are particularly pronounced when the pruning procedure keeps a moderate number of partial solutions for continued generation, highlighting the value of directly balancing quality and diversity during pruning.

## ⟪BabelTele⟫
🧭 arXiv:2610.31667v1《Direct Pass@k Optimization for Thought Pruning》(Salmani+, 2026-10-22, cs.AI/CL)—测试时扩展下候选解剪枝; 摘要1855c/262w; 贡献=质量-多样性张力显式化为 pass@k 目标。
🎯 测试时扩展=撒大量候选解赌至少一正确⟦A⟧⟨a model generates a large number of candidate solutions in the hope of finding at least one correct solution⟩; 全跑贵⇒短前缀即剪枝、仅存活者续算。
📖 旧两类: ①质量型打分丢预测错者⟦A⟧⟨assign a score to each partial solution and discard those predicted to ultimately lead to an incorrect final solution⟩; ②多样型选异轨迹者⟦A⟧⟨select partial solutions that follow different reasoning trajectories⟩。张力=探索⇿利用, 此前无人直接优化。
🔧 本文: 直接优化 pass@k=最大化⟦A⟧⟨maximize the probability that at least one of its partial solutions, when continued to completion, yields a correct answer⟩; 同奖高质量∧罚冗余⇒质/多自然平衡, 免 ad-hoc。
📊 八开放权重推理模型上超两类剪枝; 增益在留中等数部分解续生成时最显⟦A⟧⟨keeps a moderate number of partial solutions for continued generation⟩。
ℬ 判据: 探索-利用为主干(二分+pass@k), 数字术语逐字锚, 读区即复原「为何剪枝⇿旧两类⇿本文单一目标」。


## ⛓解读注

### 压缩账(本注现算)

| 量 | 值 |
|---|---|
| 源(摘要) | 1855 字符 / 262 词 |
| 编码(BabelTele 算子中文) | 913 字符 |
| 体积比 | 49.2% |
| 事实覆盖 | 9 项 assert 全过 |
| 锚 | 编码区 5 处(工具侧逐字校验 ok=5 bad=0) |

### 读法
(见编码区主干五段闭环: 背景/旧法/本文/结果/判据; 锚回源可逐字核。)

### 本条不能由在库文件判定的(只登记, 不进门槛)
全文方法算法细节、逐模型数值、与更近期剪枝工作对比; 在摘要外, 需拉 PDF 正文。

### 编码与门的账
编码区 913 字符(不含换行); 编码区锚 5 处(工具侧逐字校验 ok=5 bad=0); 事实覆盖 9 项 assert。门槛三遍: T1 字面逐锚回源 ⇿ T2 词级事实覆盖 ⇿ T3 码位与字母账。
