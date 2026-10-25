# B05 — 实测账本：压缩买回了多少人类时间（BabelTele §4.4–4.5 下游数据）
src: E:\BabelTele\2606.19857v1.pdf §4.4–4.5 (paper_text.txt, Table 4/5)
dir: corpus/babeltele/B05_evidence_ledger.md

## [[原始语料|ORIGINAL]]
Downstream measurements quantify what a model-native encoding buys. On LoCoMo agent memory, the original setting consumes 2819.5 tokens per query at 64.81% accuracy (100.00% of baseline); a natural-language summary uses 1365.6 tokens at 61.05% (94.20%); BabelTele uses 1382.2 tokens at 62.53%, retaining 96.48% of baseline score. On the LongBench v2 Code Repo QA Long subset, where the source exceeds the context window and truncation is unavoidable, dense encoding beats truncation on all three readers: Qwen3.6-Max 55.17 → 62.07, GLM-5.1 62.07 → 72.41, Kimi2.5 44.82 → 48.28 accuracy. In multi-agent communication, both homogeneous (Gemini 3.1 Pro↔Gemini 3.1 Pro) and heterogeneous (Gemini 3.1 Pro↔GPT-5.4) settings show substantial token reduction with only negligible score degradation. Cross-model transfer is zero-shot but not scale-monotone: Qwen3.5-397B-A17B scores higher than Qwen3.5-27B on original input yet lower on BabelTele, so decodability depends on the compressor-reader pair, not parameter count.

## ⟪BabelTele⟫
{⏳账本: 省tk ⟺ 赎🧑t}
①🧠LoCoMo/q: orig 2819.5tk⤷64.81≙100 ‖ sum 1365.6tk⤷61.05≙94.20 ‖ bt 1382.2tk⤷62.53≙96.48
 ⇒ bt=+16.6tk ∧ +1.48pp vs sum ｜ 可读摘要=更便宜却更笨 ⟹ 密度非体积函数, 是编码函数
 ⇒ bt/orig=49.02% 保留 ⟹ 每q净省1437.3tk ⟺ 反复消息传递的⏰🔻
②超窗✂️ vs 密文: 55.17→62.07(Qwen3.6Max▲6.90) ‖ 62.07→72.41(GLM-5.1▲10.34) ‖ 44.82→48.28(Kimi2.5▲3.46)
 ⇒ 信息¬被迫丢弃 ｜ 窗口不足 ⇔ 截断 ∨ 密文, 后者保真
③M2M: Gem↔Gem ∧ Gem↔GPT-5.4 ⇒ tk↓↓ ∧ score≈ ∴ 黑盒协议✓ (∀同/异构对)
⚠¬monotone: 397B-A17B(orig↑) ∧ bt<27B ⇒ 可解性=f(C,R)∈⏦(不可判), ∉参数量
∴ π: 1437.3tk/q → 🧑.t 移仓 至[异常检测∧目标重设], 离仓 自[渲染阅读]

## ⛓解读注
⤷=消耗→得分 · ≙=归一到基线 · ⏦=不可判定 · ①②③=账本行
※ +16.6tk=1382.2−1365.6; +1.48pp=62.53−61.05; 49.02%=1382.2/2819.5; 1437.3=2819.5−1382.2; ▲差值取自 Table 5。
