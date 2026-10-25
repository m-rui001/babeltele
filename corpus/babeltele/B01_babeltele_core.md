# B01 — BabelTele 核心论点（模型原生表示 ↔ 人类时间再分配）
src: E:\BabelTele\2606.19857v1.pdf (arXiv:2606.19857, Zhu et al., SJTU et al.)
dir: corpus/babeltele/B01_babeltele_core.md

## [[原始语料|ORIGINAL]]
Large language models are commonly prompted and interfaced with human-readable natural language, even when the intended reader is another model. BabelTele is a model-centric textual representation that sacrifices human readability while remaining recoverable by LLMs. It maintains 99.5% semantic fidelity when text volume is condensed to 27.9% of the original length. Human QA accuracy drops from 56.10% to 35.80% on BabelTele, while Gemini 3.1 Pro rises from 90.00% to 96.70%. BabelTele's perplexity is order-of-magnitude higher (perplexity rises from 9.63 to 176.60 on Llama-3-8B (+1,733.9%), and across eight base models the increase spans +1,320.5% (DeepSeek V4 Pro) to +2,061.1% (Qwen2-7B)), and Dale-Chall readability reaches 16.70 with 80.19% difficult words. It transfers zero-shot across proprietary and open-weight model families, and reduces context overhead in document QA, agent memory, and multi-agent communication. Human readability, natural-language typicality, and model-side semantic recoverability are partially decoupled.

## ⟪BabelTele⟫
{ctx:LLM↔LLM⏟読者≠人類}
人類可読性🥀 ⇒ 圧縮C: 文本→高密度語符図
⚡忠実99.5% @ 体積27.9%｜token↓≈4/5
🧑QA 56.10→35.80 ▼ vs 🤖Gem3.1P 90.00→96.70 ▲ ∴ 可読性⊥可解読性
PPL: Llama3-8B 9.63→176.60=+1733.9% ‖ 8base全距+1320.5(DSV4P)~+2061.1(Qwen2-7B) ‖ DaleChall16.70 ‖ 難語80.19% ⇒ ¬自然言語分布∈BabelTele
zeroShot跨 proprietary+openWeight 📦 ⇒ ∀R∃解碼(無码本)
適応: DocQA ∧ agent記憶 ∧ 多agent通信 ⇒ context开销↓ ⇒ 🧑t 由「解码通信」释出→判断/目标

## ⛓解読注(无码本自足)
※ 读法: C=compressor, R=reader, ⏟=共享上下文, ⊥=统计独立(可解码性⟂可读性), ᐁ=被释放出来的(时间), ≈4/5=token 削减量。
