# B20 — 思维链语料：把 EWCA Civ 1224 的定性方法迁移到假设案（deepseek-v4.1-flash-free 原始 reasoning, 外国判决×争点禁反言）
src: corpus/raw/cot/law_ewca_method.md (prompt+REASONING 64 995 字符, reasoning 段逐字)
dir: corpus/babeltele/B20_cot_foreign_judgment_estoppel.md

## [[原始语料|ORIGINAL]]
The Dutch licensor now sues in England, claiming copyright in the same UI for England and for France, and HanPlay pleads the Korean judgment as an issue estoppel on ownership.

## [[REASONING]] All tools disabled. I must answer from reasoning.

Let me think: [2026] EWCA Civ 1224 is a future citation (2026).

I don't have it in my training data.

Let me try to recall recent cases on foreign copyright and issue estoppel: - *Lucasfilm v Ainsworth* [2011] UKSC 39: foreign copyright claims justiciable; lex loci protectionis.

- *Carl Zeiss* [1967] 1 AC 853: foreign judgment and issue estoppel; the foreign judgment must be final and conclusive; the issue must be the same.

- *Kookmin Bank v Rainy Sky*? No. - *Joint Stock Co "Aeroflot - Russian Airlines" v Berezovsky*? No.

- *Lucasfilm* changed the position for copyright.

Maybe the case is about "Aviator" the game, and the Dutch licensor is a company like "Spribe" (actually Estonian/Ukrainian).

The Korean court held that the Korean licensee owns the copyright in the mobile game UI under Korean law (perhaps because of the "work made for hire" doctrine or because the licensee contributed to the UI).

The answer likely turns on the distinction between the *lex fori* (recognition) and the *lex loci protectionis* (ownership).

It could be a fabricated case for the exercise.

So we don't need the actual case; we need to apply the described method.

For example, don't say "this is a procedural estoppel, so English law applies" because the question whether it is procedural is itself the question.

You must not confuse the procedural nature of the recognition rule with its substantive effect.

- If the UK is bound by neither Brussels I nor Lugano, the recognition and enforcement of third-State judgments is governed by the common law, not by any harmonised instrument. The "scheme" of the common law is that foreign judgments in personam are recognised under certain conditions, and foreign judgments in rem are recognised only if the property was situated in the foreign country (lex situs). - For IP, the situs of the right is the country of protection (lex loci protectionis).

The common law's recognition rules are narrower. 4. **The absurdity check.** - If the Korean judgment were held to determine ownership of the English and French copyrights, a Korean court could, in effect, legislate for the world and alter property rights in England and France.

It would also allow forum shopping: a party could choose a favourable foreign court to determine global ownership. That is absurd. - If, on the other hand, the Korean judgment were given no effect at all, the parties could relitigate the same issue in every jurisdiction, with inconsistent results.

The absurdity check favours applying French law to the French claim.

The Korean judgment determined ownership under Korean law. The issue is not the same.

Under the territoriality principle, only English law can determine who owns the English copyright.

Wait: If both are English law, is the answer "English law" too obvious? The question may expect a more nuanced answer: the plea is determined by English law because the forum is England and the right is English.

The Korean judgment's effect is not determined by Korean law because recognition is a matter of the forum.

The result is the same: the plea fails.

The English court's recognition rules are only a threshold; the substantive effect on the French right is governed by French law.

For the French claim, the forum (England) and the locus protectionis (France) diverge, so the analogy does not hold; the court must apply French law to the effect of the Korean judgment on the French right.

But wait: Is it correct that French law governs the recognition of the Korean judgment in an English court? Let me think carefully.

The plea of issue estoppel is a procedural device of the English court.

The result is the same, but the reasoning is different.

The Aviator judgment's method probably rejects the procedural characterisation and adopts the substantive characterisation, at least for the foreign copyright claim.

Let me look at the four elements again and see which way they cut.

- A non-circular characterisation would avoid saying "estoppel is procedural, so lex fori" because that assumes the conclusion.

You must not let the procedural label obscure the substantive effect.

The scheme tells you to separate the two: recognition by the forum's law, effect by the lex loci protectionis.

The question "by which law must the plea be determined" might be answered by saying the plea is determined at the recognition stage by English law and at the effect stage by the lex loci protectionis.

- If the Korean judgment were given global effect, absurd; if given no effect, also problematic. The middle ground: territorial effect.

But there's a twist: The Korean judgment is a judgment *in personam* between the parties. Even if it cannot determine the proprietary right in France, it might estop the licensor from denying HanPlay's ownership *as a matter of the parties' contractual relationship*.

The licensor is bound by it in personam, even in France.

Article 24(4) gives exclusive jurisdiction for registered IP, not copyright).

That would flip the result from "no estoppel" to "estoppel".

The user says "identify the two places where your answer would flip if a harmonised instrument on recognition of judgments came into force." This likely refers to two points in the analysis, not two claims.

I need to reason from the description.

But the question's emphasis on (a) and (b) suggests the answer might be different.

The difference between (a) and (b) is not the governing law of the plea, but the substantive result: for (a), English law is

The user also asks "where the analogy to the Aviator judgment breaks down rather than holds" — this suggests that the Aviator judgment provides a rule for one claim but not the other.

The analogy breaks down because the foreign judgment is not from the locus protectionis for the English/French claims.

This is a classic exam technique: apply the case by analogy, but identify the limits.

The analogy "breaks down" on the choice-of-law point, not the result.

This is the "extended effect" approach used in some civil law systems.

This is the most sophisticated and likely the Aviator method.

It might lead to a mixed approach.

The English court's recognition rules are not the law governing the plea; they are merely the gateway.

If IP is excluded, a harmonised instrument would not apply to the Korean judgment on copyright ownership at all, so the answer would not flip; it would remain under the common law.

The absurdity is avoided by treating the Korean judgment as conclusive only as to the Korean copyright.

The CJEU's *Duijnstee v Goderbauer* (1983) held that a dispute concerning the ownership of a patent is not a matter of contract but falls under the exclusive jurisdiction of the courts of the State where the patent is granted (Article 16(4) of the Brussels Convention).

But the prompt says "holding that a Korean licensee, HanPlay, owns the copyright in a mobile game UI as Korean law requires." This sounds like a judgment *in rem* or a declaration of ownership, not a contract claim.

The phrase "as Korean law requires" is important.

For example, if the Korean court found that HanPlay's employees created the UI, that finding might estop the licensor from denying it in England.

So the plea fails under both English recognition law and French copyright law.

no, that would include copyright, which is the opposite.

If a harmonised instrument excludes IP, then it would not apply to our case, and the answer would not flip.

## ⟪BabelTele⟫
{🚦先做权威/资源审计再答题: ⟨All tools disabled⟩‖⟨I must answer from reasoning⟩ ‖ ⟨[2026] EWCA Civ 1224 is a future citation⟩ ‖ ⟨I don't have it in my training data⟩ ‖ 试探记忆 ⟨foreign copyright⟩‖⟨issue estoppel⟩ ‖ 改框: ⟨could be a fabricated case⟩⇒⟨need to apply the described method⟩‖⟨reason from the description⟩
📚先重建确知的场域: ⟨must be final and conclusive⟩ ‖ 承认依⟨lex fori⟩⇎归属依⟨lex loci protectionis⟩ ‖ 普通法基线⟨governed by the common law, not by any harmonised instrument⟩‖⟨recognition rules are narrower⟩ ‖ 对物承认⟨only if the property was situated in the foreign country (lex situs)⟩⇒转译⟨the situs of the right is the country of protection⟩
🧭反循环禁令: ⟨don't say⟩⟨this is a procedural estoppel, so English law applies⟩‖⟨it is procedural is itself the question⟩⇒⟨assumes the conclusion⟩ ‖ ⟨must not confuse⟩⟨procedural nature⟩⟨recognition rule⟩⟨its substantive effect⟩ ‖ ⟨must not let⟩⟨the procedural label obscure⟩⟨the substantive effect⟩
🚪体系论证⇒两段式: ⟨recognition by the forum's law, effect by the lex loci protectionis⟩ ‖ 承认规则⟨are not the law governing the plea⟩⇒⟨merely the gateway⟩ ‖ ⟨only a threshold⟩⇒⟨substantive effect on the French right is governed by French law⟩ ⇎ 对手立场⟨issue estoppel is a procedural device⟩‖⟨recognition is a matter of the forum⟩
🌀荒谬性检验(两侧都定价): 全球效力⇒⟨could, in effect, legislate for the world⟩⟨alter property rights⟩英法 ‖⟨choose a favourable foreign court⟩⇒⟨determine global ownership⟩⇒⟨That is absurd⟩ ‖ 零效力⇒⟨the parties could relitigate⟩⟨with inconsistent results⟩ ‖ 解: ⟨favours applying French law to the French claim⟩⟨conclusive only as to the Korean copyright⟩‖⟨global effect, absurd; if given no effect, also problematic⟩⇒⟨middle ground: territorial effect⟩
🔍同一争点判定: ⟨ownership under Korean law⟩⇒⟨issue is not the same⟩ ‖⟨only English law can determine who owns the English copyright⟩
📝题面即证据: ⟨emphasis on (a) and (b)⟩⇒⟨the answer might be different⟩ ‖ ⟨not the governing law of the plea⟩⇒⟨the substantive result⟩ ‖ ⟨provides a rule for one claim but not the other⟩
⚡被"对人性"翻盘的风险: ⟨there's a twist⟩: ⟨a judgment 'in personam' between the parties⟩ ‖ 许可人⟨is bound by it in personam⟩⇒⟨even in France⟩⇒⟨would flip the result from 'no estoppel' to 'estoppel'⟩ ‖ 定性回读⟨'in rem' or a declaration of ownership⟩⇒⟨not a contract claim⟩ ‖ ⟨"as Korean law requires" is important⟩⇒⟨might estop the licensor⟩⟨from denying it in England⟩
🔁自查: ⟨If both are English law⟩⇒⟨too obvious?⟩ ‖ 韩判在英庭承认⟨Is it correct that French law governs the recognition⟩⟨in an English court⟩ ‖ ⟨no, that would include copyright⟩⇒⟨the opposite⟩ ‖ ⟨If a harmonised instrument excludes IP⟩⇒⟨the answer would not flip⟩ ‖⟨It might lead to a mixed approach⟩ ‖⟨The result is the same⟩‖⟨the reasoning is different⟩
🎯两翻转点=⟨recognition stage⟩‖⟨effect stage⟩ ‖ 语义核对⟨two points in the analysis, not two claims⟩
💔类比边界: 法院地英⇎保护地法⟨diverge⟩⇒⟨analogy does not hold⟩ ‖ 韩判决于英法请求⟨not from the locus protectionis⟩ ‖⟨'breaks down' on the choice-of-law point, not the result⟩ ‖ 元技巧: 类比⟨but identify the limits⟩
🏗️对未知判决的重建及强度标注: ⟨look at the four elements again⟩⇒⟨which way they cut⟩ ‖ 大陆法系⟨'extended effect' approach⟩ ‖ ⟨the most sophisticated⟩⇒⟨likely the Aviator method⟩ ‖ 推测⟨probably rejects⟩⟨the procedural characterisation⟩⇒⟨substantive characterisation⟩[限外国版权请求] ‖ 猜测标记⟨'Aviator' the game⟩‖荷兰许可人≈⟨a company like 'Spribe'⟩‖⟨the 'work made for hire' doctrine⟩
📌可确证记忆点: ⟨*Kookmin Bank v Rainy Sky*? No.⟩ ‖ 版权⟨*Lucasfilm* changed the position⟩ ‖ ⟨(1983) held that a dispute⟩⟨ownership of a patent is not a matter of contract⟩ ‖ ⟨Article 24(4)⟩⇒⟨exclusive jurisdiction for registered IP⟩⇎⟨not copyright⟩
✅底线结论: ⟨So the plea fails under both⟩承认法‖版权法
∴骨架: ①缺权威时先判"题目要方法还是判例", 把未知判例改框为方法载体 ②先枚举确知规则, 再叠加推测 ③定性第一戒: 不得用结论回答前提 ④体系论证=把"承认"与"效力"分置不同法源 ⑤荒谬性检验两侧同价⇒取地域效力为中间解 ⑥题面措辞(强调/a/b/两处分歧)自带信息 ⑦找到能翻盘的例外(对人性)比给干净答案更重要 ⑧类比标明破裂处 ⑨只引可确证者, 臆测显式降调

## ⛓解读注
⟨…⟩=该思维链文件 reasoning 段内逐字段(audit.py prose_norm 逐字校验; 引号/斜体标记 *…* 与 ' ' 差异已忽略) ‖ ⇒推出 ⇎对立立场 ‖ 并列 ∴可迁移骨架
※本条目无派生算术: 1224/2026/1983/24(4) 等均为 trace 原值(案号年份与条文号), 未改写。
※思维链由 opencode/deepseek-v4.1-flash-free 于 2026-10 生成; 假设案与 [2026] EWCA Civ 1224 均不在训练集内。
