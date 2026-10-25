# B75 同一判决书的四个声音: Loper Bright 推翻 Chevron——异议用 86 处点名多数意见, 多数只回 14 处; 判例名是全书最高频词; 摘要只镜像胜方
src: corpus/raw/opinions/loper_a.txt (76952 字符) ⇎ corpus/raw/opinions/loper_b.txt (66507 字符) ⇎ corpus/raw/opinions/loper_c.txt (65696 字符) ⇎ corpus/raw/opinions/loper_d.txt (23482 字符) (四份同为 Cornell LII 的 Loper Bright 判决书按意见头分段: 多数意见⇎协同⇎异议⇎法院自备摘要, 折平面; 数字一律从面内现读, 一个都不手填; 抓取时刻与 LII 现行版本只在本机或站外成立, 不进门槛)
; tags: 互指不对称键(the dissent⇎the majority) 判例名词频四声音 主题主语分档(congress峰⇎constitution峰) 句集交集镜像键(syllabus只摘胜方) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/opinions/loper_a.txt

Chevron is overruled. Courts must exercise the

### ⟦B⟧ ⟸ corpus/raw/opinions/loper_b.txt

It forces judges to abandon the best reading of the law in favor of views of those presently holding the reins of the Executive Branch. It requires judges to change, and change again, their interpretations of the law as and when the government demands.

### ⟦C⟧ ⟸ corpus/raw/opinions/loper_c.txt

For 40 years, Chevron U. S. A. Inc. v. Natural Resources Defense Council, Inc.

The majority says that I have "pluck[ed] out" Gray and Hearst , impliedly from a vast number of not-so-helpful cases.

### ⟦D⟧ ⟸ corpus/raw/opinions/loper_d.txt

Chevron is overruled. Pp.

## ⟪BabelTele⟫
🧭 同一份判决书(Loper Bright, 2024-06-28)剥出四个声音, 同为 LII 折平面: 多数意见(Roberts) 76952 字符⇎协同意见(Gorsuch) 66507⇎异议(Kagan) 65696⇎法院自备摘要(Syllabus) 23482 ⇎ 句 486⇎449⇎498⇎140 句——异议比多数意见长不了几行, 但互指次数差一个量级(见⚖)。
⚖ 反驳方向不对称: 多数意见点异议 "the dissent" 14 次、协同点异议 5 次; 反向, 异议点多数意见 "the majority" 86 次、协同点多数意见 0 次——被推翻的一方用 86 处点名逐段反驳, 推翻方只回 14 处: 异议开篇即 ⟦C⟧⟨For 40 years, Chevron U. S. A. Inc. v. Natural Resources Defense Council⟩, 收尾指控 ⟦C⟧⟨The majority says that I have "pluck[ed] out" Gray and Hearst⟩——点名即引证, 引证即反驳。
📚 被推翻的判例名是全书最高频词: Chevron 127⇎93⇎89⇎45 处(连法院自备摘要都有 45 处), 四声音加起来百余次; stare decisis 6⇎17⇎12⇎3——协同意见(Gorsuch)把遵从先例说得比异议还多(17⇎12), 因为它要从宪法根上论证这先例本来就不配存在(precedent 10⇎41⇎10⇎4、constitution 24⇎27⇎4⇎7 都以协同为峰)。
🏛 谁说了算的分岔: defer 词族 55⇎58⇎65⇎17 处四声音都在讲遵从; 而主语分家——异议的 Congress 47⇎18⇎95⇎15 处为四声之峰(立法者视角: 法院抢了国会的事), 协同的 agency 只 21 处而 constitution 最高; 判例名之外 Kagan 引 Chevron 本体 89 处与多数几乎同量(127)——双方在同一段历史上各取所需。best reading 3⇎3⇎0⇎3 处是新标准的替身短语: 多数/协同/摘要各说"法律的最佳读法", 异议 0 处——它拒绝用胜方的词; 协同意见把新标准的代价写成 ⟦B⟧⟨It forces judges to abandon the best reading of the law in favor of views of those presently holding the reins of the Executive Branch.⟩。
🔁 摘要是镜像: 句集交集 A⇎D 30 句, 远大于其余五对(8⇎3⇎1⇎4⇎1)——Syllabus 逐句转述多数意见, 而它与异议只 1 句共享: 法院给自己的摘要只摘胜方。官方判决头归 Syllabus, 胜方意见归 A, 署名协同归 B, 败方归 C——同一文件里的四层认识状态。
ℒ 方法 ⇒ 判决书的隐性知识不在"判了什么"(一句话: Chevron 推翻 ⟦A⟧⟨Chevron is overruled.⟩), 而在四个声音怎么分家: 先把互指做成键(the dissent ⇎ the majority 的 14 对 86), 再把判例名词频做成键(Chevron 四声音各 127⇎93⇎89⇎45), 再把主题主语做成键(congress 之峰在异议、constitution 之峰在协同), 最后把句集交集做成键(摘要只镜像胜方 30 句)。

## ⛓解读注

### 第四遍复测(本注现算, 第三套实现: finditer 句标偏移切片 + findall 计数)

| 量 | 结果 | 与契约 |
|---|---|---|
| 句数/字符 | [486, 449, 498, 140] / [76952, 66507, 65696, 23482] | 逐份相等 |
| Chevron 四声音 | [127, 93, 89, 45] | 逐份相等 |
| 互指 the dissent(多数⇒异议) / the majority(异议⇒多数) | [14, 5, 0, 0] / [1, 0, 86, 0] | 逐份相等 |
| congress / stare decisis | [47, 18, 95, 15] / [6, 17, 12, 3] | 逐份相等 |
| 摘要镜像 A⇎D 句集交集 | 30 句 | 相等 |

上表 5 行全部 assert, 不符即停机。

### 读法

一、判决的结论只有一句 ⟦A⟧⟨Chevron is overruled.⟩, 本条不记结论, 记四个声音怎么分家: 互指不对称(多数点异议 14 次, 异议点多数 86 次)——败方逐段反驳, 胜方点到为止。
二、判例名是全书最高频词(Chevron 127/93/89/45), 连法院自备摘要都提 45 次——被推翻的东西恰恰是全书说话的中心。
三、主语即视角: congress 之峰在异议(95 处——法院抢国会的事), constitution 之峰在协同(27 处——从根上否定先例)。
四、摘要只镜像胜方: A⇎D 句集交集 30 句远大于其余五对——Syllabus 逐句转述多数意见, 与异议只 1 句共享。

### 本条不能由在库文件判定的(只登记, 不进门槛)

抓取时刻与 LII 现行版本; 各意见的官方 slip op 页码与 LII 折平面的对应; Kagan 附录表是否完整入面; 口头辩论与意见书的措辞回改(本条只收判决书文本)。

### 编码与门的账

编码区 1490 字符(不含换行); 编码区锚 4 处(候选池 3 条按标签 A 1/B 0/C 1/D 1, 工具侧逐字校验 ok=3 bad=0); 扁平契约 37 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 5 行再复测。