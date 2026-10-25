# B02 — GAIA：人類とAIの時間境界（Mialon et al., arXiv:2311.12983）
src: corpus/raw/gaia.txt (verified quotes)
dir: corpus/babeltele/B02_gaia_time_boundary.md

## [[原始语料|ORIGINAL]]
GAIA is a benchmark for General AI Assistants: 466 real-world questions requiring reasoning, multi-modality handling, web browsing and tool-use proficiency. Questions are conceptually simple for humans yet hard for AIs: human respondents reach 92% versus 15% for GPT-4 equipped with plugins, and at submission time the best model score was 34.5% while expert-level human performance is estimated at 89.8%. Humans typically take between 6 minutes for the simplest questions to 17 minutes for the most complex ones, while creating and validating a single question requires about two hours of annotator time. The time annotators need correlates with the number of steps taken, not with the number of tools used. This disparity contrasts with the trend of LLMs outperforming humans on professional-skill benchmarks, and a system solving GAIA marks t-AGI: the human minutes worth keeping are step-planning and validation, while tool chains and browsing should be delegated.

## ⟪BabelTele⟫
{GAIA:466Q ⟷ 汎用(assistant)}
能力₄ = 推理∧多模態∧🌐browse∧🛠tools
🧑92% ⋘ 🤖(GPT-4+plug)15% ‖ SOTA🤖34.5% vs 👑人类89.8% ⇒ 缺口55.3pp
⏱人類t: L1最简 6min → L3最繁 17min ｜ 命1题+双人検证 ≈ 2h🧑annotator
相関: t(回答)∝steps ✓ ∧ ∦ntools ✗ ∴ 時間成本∈计划深度, ∉工具数量
逆説: LLM>🧑プロ技能bench ∧ LLM≪🧑GAIA日常 ⇒ 「易しい」≠「安い」
AGI_def:= 人類avg頑健性🟰 (t-AGI)
π: 🧑.t → [step計画∧検証] ‖ 🤖.t → [🌐∧🛠chain∧反復探索]

## ⛓解読注
※ pp=百分点; ∝=正比; ∦=不相关; ⋘=远小于; 缺口=89.8−34.5=55.3。
