# B03 — Rich Sutton《The Bitter Lesson》(2019-03-13)：研究者时间的最大回报配比
src: corpus/raw/bitter_lesson.txt (incompleteideas.net)
dir: corpus/babeltele/B03_bitter_lesson_time.md

## [[原始语料|ORIGINAL]]
The biggest lesson from 70 years of AI research is that general methods that leverage computation are ultimately the most effective, by a large margin, because of Moore's law and exponentially falling cost per unit of computation. Most AI research treated available computation as constant, so researchers leveraged human domain knowledge; but time spent on one approach is time not spent on the other. In chess, Deep Blue's 1997 massive deep search beat human-structure knowledge. In Go, two decades of knowledge-engineering proved irrelevant once search plus self-play learning scaled. In speech recognition, DARPA 1970s knowledge methods lost to statistical HMM computation, later to deep learning on huge datasets — a colossal waste of researcher's time to build in how we think we think. Computer vision's edges, generalized cylinders and SIFT were discarded for convolution and invariances. Search and learning are the two methods that scale arbitrarily with computation; the contents of minds are irredeemably complex, so build in only meta-methods that automate learning and search, and let computation, not human hours, do the work.

## ⟪BabelTele⟫
{BL:70yrsAI史} 主定理: 汎用計算駆動法 ≫ 人間知識注入法 ∵ Moore˹law˼💸/ flop → 0
⏳守恒: t(知識工学)+t(計算スケーリング)=定 ⇒ 一方へ配分=他方🚫
事例矩阵🧮:
♟1997: 深🔍(DeepBlue) ⊟ 👤構造知識 ｜ ⚫Go: 20yrs𝑘𝑛𝑜𝑤→無効 ∵ 🔍+自己遊戯📈価値𝑓
🎙70s:DARPA👤音素/声道法 ⟍ HMM統計+大量計算 ⟍🔚 深層🧠+📚巨大データ
👁️: edge/广义圆柱/SIFT ↦✂️ ∵ conv+不変性⊡優
帰納∀事例: ①短期👤知識→📈満足 ②plateau🛑 ③逆側(🔍∧学習)+💰計算→🏔breakthrough ⇒ 苦味🧂
指針: 心内容=無限複雑 ⇒ 組込むな、meta法(自動🔍∧🎓)のみ内蔵
⌛人类时间最优解: 每省1h手工结构 ⟺ 换1单位可无限扩展的算力杠杆

## ⛓解読注
𝑓=目标函数 · 𝑘𝑛𝑜𝑤=领域知识 · ˹˼=Moore˹law˼修饰 · ①②③=教训因果步 · ※ ⊟=战胜(博弈符号); ⟍=让位于; plateau=收益平台期。
