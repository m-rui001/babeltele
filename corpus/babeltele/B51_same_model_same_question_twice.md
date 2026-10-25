# B51 同一模型 ⇎ 同一道题的两次采样：逐字复现的是题面与清单, 判序每次都得重做
src: corpus/raw/cot/math_subsets.md (推理区 23309 字符 ⇎ 回答区 0) ⇎ corpus/raw/cot/math_subsets_s2.md (推理区 81286 字符 ⇎ 回答区 6908) ⇎ corpus/raw/cot/med_gitalb.md (推理区 22985 字符 ⇎ 回答区 0) ⇎ corpus/raw/cot/med_gitalb_s2.md (推理区 101356 字符 ⇎ 回答区 6748) (题面 sha 只有两枚: c2940de92453fb06 ⇎ 5044e4bde9246083, 各覆盖两份)
；联结不是“四份材料”, 而是“两次抽签”: 同一模型、两道题、每题各采一次于十月十九日、再采一次于十月二十一日凌晨, 推理区最长是最短段的 4.41 倍, 两次第一次都没写完答案(回答区 0 ⇎ 0 字符); 可核性走四种粒度的集合交与 >=40 字公共片段, 每个数由 audit.py 的 B51V 从四份 raw 整段复算
tags: 两次采样 四种粒度共有量 题面中段复读 极大公共片段 纯题面与推理复用 判序不可复现 回答区从无到有 末字符非句终 绝对数与每万字口径分岔 重来词族四源皆零 跨题对打平同题对 五词串跨题归零 锚归属由正文现推 三口径可核性
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/cot/math_subsets.md

Determine, with proof, the largest possible number of pairs (a, b) of elements of a set S of n positive integers with a < b such that a + b divides a*b. Give the exact extremal value as a function of n and characterize the sets attaining it. Solve it the way a research mathematician would: search for structure, try small n by hand, form a conjecture, then prove it.

State any lemma you use and prove it. Reason out loud, showing every arithmetic check you make. ## [[REASONING]] We need solve math problem. Need rigorous, research style, small n, conjecture, proof, dead ends, key invariant.

8 divides12 no. Let's find pair: x=1,y=2,k=1 => a=1*1*3=3, b=1*2*3=6; 9 divides18 yes.

If choose L divisible by all pair sums, then yes! Wait for any finite set R of positive integers, choose L = lcm_{i<j}(r_i+r_j). Then for a=L r_i,b=L r_j, condition requires r_i+r_j | L r_i r_j, and if r_i+r_j | L then true.

For n=4, choose R={1,2,3,4}, L=lcm(3,4,5,5,6,7)=420. S={420,840,1260,1680}. Check 420+840=1260 divides352800=280 yes; 420+1680=2100 divides705600=336; etc.

Need exact extremal value C(n,2), characterization likely all sets satisfying pairwise condition, but perhaps can give structural characterization. Maybe problem intended nontrivial? Wait maximum number of pairs is trivially all if construction. Maybe there is hidden restriction: "elements of a set S of n positive integers" no bound indeed.

Let's read wording: "Determine, with proof, the largest possible number of pairs (a, b) of elements of a set S of n positive integers with a < b such that a + b divides a*b. Give the exact extremal value as a function of n and characterize the sets attaining it." If all pairs attainable, extremal value C(n,2), characterize all pairwise-good sets.

Hmm. Let's analyze pairwise condition with a+b | ab.

Thus all cliques are essentially scaled primitive sets. That is a clean characterization: S is extrem ## [[ANSWER]]

### ⟦B⟧ ⟸ corpus/raw/cot/math_subsets_s2.md

Determine, with proof, the largest possible number of pairs (a, b) of elements of a set S of n positive integers with a < b such that a + b divides a*b. Give the exact extremal value as a function of n and characterize the sets attaining it. Solve it the way a research mathematician would: search for structure, try small n by hand, form a conjecture, then prove it.

State any lemma you use and prove it. Reason out loud, showing every arithmetic check you make. ## [[REASONING]] No web.

Alternative interpretation: "largest possible number of pairs (a,b) of elements of a set S of n positive integers with a<b such that a+b divides a*b" Maybe they ask max over S, and since C(n,2) trivial, maybe the "characterize sets attaining it" means characterize complete sets. Could be answer is simply all sets S satisfying pairwise property; not satisfying maybe not asked.

Hmm. Let's see if maximum all

Wait our triangle {20,30,60}: minimum 20; other b from divisors of 400: 30 (sum50), 60 (sum80). So yes possible.

T={1,2,3,4}, L=lcm(3,4,5,5,6,7)=420. S={420,840,1260,1680}. Is minimal 420; other b correspond to divisors of 420^2? b=840,1260,1680; sums 1260,1680,2100; are these divisors of 420^2=176400? 1260*140=176400 yes; 1680*105=176400; 2100*84=176400.

So no. Could characterize maximal K_n construction by an integer L and ratios: Let S={L/r_i}.

Determine, with proof, the largest possible number of pairs (a, b) of elements of a set S of n positive integers with a < b such that a + b divides a*b. Give the exact extremal value as a function of n and characterize the sets attaining it." It indeed doesn't say bounded.

We can produce maybe 1500-2500 words? Desired oververbosity 5, but complex request.

### Dead end 1: guessing a Turán-type answer A natural guess from extremal graph theory might be \(\lfloor n^2/4\rfloor\), but \(n=3\) already disproves it: \(\lfloor9/4\rfloor=2\), while the triangle above has \(3\) good pairs. ### Dead end 2: trying to bound the clique size by divisor counting The condition \(a+b\mid a^2\) suggests counting divisors of \(a^2\).

Trying to extend \(\{20,30,60\}\) by hand also dead-ends: any fourth element \(d\) must satisfy \(d+20\mid400\), so, apart from \(30,60\), the candidates are \(5,80,180,380\); direct checks against \(30\) eliminate all of them. This temporarily suggested that \(K_4\) might be impossible.

\] This is the key invariant: every finite configuration can be made admissible by one common dilation, because the obstructions are just finitely many divisibility conditions on \(M\). --- ## 3.

Thus, for the problem as stated, the extremal number is the full binomial coefficient, and the extremal sets are governed only by the finite scaling obstruction \(\Lambda(T)\).

### ⟦C⟧ ⟸ corpus/raw/cot/med_gitalb.md

Work through the differential diagnosis as a nephrologist would: enumerate every cause of hypokalemic metabolic alkalosis with normal-to-low blood pressure, then eliminate each one by explicit reference to a specific number or finding above, and state the single most likely diagnosis plus the confirmatory test. Explain the mechanistic reason behind each elimination step, including why the urinary chloride and the fractional calcium excretion discriminate the way they do, and why Mg is low. Reason out loud; show false leads you consider and reject. ## [[REASONING]] We need answer clinical reasoning. Need be thorough.

Diagnosis likely Gitelman syndrome? Let's parse.

- Gitelman syndrome: DCT thiazide-sensitive NaCl cotransporter (SLC12A3); hypokalemia, metabolic alkalosis, hypomagnesemia, hypocalciuria, high renin/aldosterone, low/normal BP, salt craving, cramps; urine Cl high due salt wasting.

no. - Renin-secreting tumor: hypertension, high renin, hypokalemia; no.

- Congenital adrenal hyperplasia (11β-hydroxylase, 17α-hydroxylase): hypertension, low renin/aldosterone; exclude.

In DCT, thiazide inhibits NCC, causing decreased intracellular Na and increased basolateral Na/Ca exchange? Let's recall: Thiazides

Need accurate mechanism. Gitelman hypomagnesemia due to impaired DCT magnesium reabsorption, likely secondary to reduced NCC activity and altered membrane voltage/TRPM6 regulation; also chronic secondary hyperaldosteronism and K/Mg wasting.

Hmm. 2.

Need enumerate and eliminate each with specific numbers: BP 104/66 no HTN; renin elevated eliminates low-renin states; aldosterone elevated eliminates low-aldosterone states; primary aldosteronism would have suppressed renin and usually HTN. But "normal-to-low BP" could include normotensive primary aldosteronism rare, but renin elevated excludes.

Could state "Gitelman is far more likely; CLCNKB-related Bartter III is the main genetic mimic and can be covered by a tubulopathy gene panel." Confirmatory test: SLC12A3 sequencing; if negative, CLCNKB. Need maybe mention "urine diuretic screen by mass spectrometry" to exclude thiazide; negative screen is reassuring but not 100% (some screens miss).

- Urine Cl 104 also excludes vomiting/NG suction because in those, Cl loss is extrarenal, urine Cl low; excludes post-diuretic state because after diuretic effect wanes, urine Cl low; excludes congenital chloride diarrhea (stool Cl high, urine Cl low); excludes laxative abuse (usually acidosis, low urine Cl). - It does not by itself distinguish diuretic vs Bartter vs Gitelman; FeCa and Mg do.

- DCT (Gitelman, thiazides) reabsorbs ~5 ## [[ANSWER]]

### ⟦D⟧ ⟸ corpus/raw/cot/med_gitalb_s2.md

Work through the differential diagnosis as a nephrologist would: enumerate every cause of hypokalemic metabolic alkalosis with normal-to-low blood pressure, then eliminate each one by explicit reference to a specific number or finding above, and state the single most likely diagnosis plus the confirmatory test. Explain the mechanistic reason behind each elimination step, including why the urinary chloride and the fractional calcium excretion discriminate the way they do, and why Mg is low. Reason out loud; show false leads you consider and reject. ## [[REASONING]] We need answer medical diagnostic reasoning. Need be careful.

Likely Gitelman syndrome vs Bartter.

- Congenital adrenal hyperplasia (11β-hydroxylase, 17α-hydroxylase): hypertension, low renin/aldo, excluded; 17α-hydroxylase may low sex steroids.

Need accurate mechanism. In DCT, NCC reabsorbs NaCl; calcium reabsorption via apical TRPV5 and basolateral NCX1.

Mechanism: decreased intracellular Na and increased basolateral Na/Ca exchange driving Ca reabsorption; also reduced cell Ca? Need be precise.

Could mention "genetic testing of SLC12A3" is confirmatory; if unavailable, clinical diagnosis with hypokalemic metabolic alkalosis, hypomagnesemia, hypocalciuria, high renin/aldo, normal BP.

Hmm. Primary Mg deficiency can cause hypokalemia and metabolic alkalosis, but the alkalosis is due to K depletion.

- "Hypercalcemia" etc no. Need discuss "urinary chloride and fractional excretion of calcium discriminate the way they do" in detail.

Wait urine anion gap = (Na+ + K+) - Cl-; if positive, unmeasured anions (HCO3-) present; if negative, NH4+ high. Here +70 due to high HCO3? But we don't have urine pH.

We can produce maybe 1500-2500 words? User asks "reason out loud" and enumerate every cause.

Mention "this is the one mimic that survives the biochemistry; it is excluded by the negative screen/history, but clinically one would confirm with SLC12A3 testing and/or a supervised diuretic screen." This shows false lead. Need maybe discuss "why not vomiting" as false lead: - Vomiting also causes hypokalemic alkalosis, low Mg, high renin/aldo, normal/low BP; can cause salt craving? But urine Cl should be low (<20), urine Na low, and patient would have history.

| | **Gitelman syndrome** | Fits every finding: K 2.7, HCO3 34, urine K 78, urine Na 96, urine Cl 104, high renin/aldo, BP 104/66, Mg 0.58, FeCa 0.8%, cramps, and salt craving. | | **Liddle syndrome** | Hypokalemic alkalosis with high urine Cl, but **hypertension** and **suppressed renin/aldo**.

### Final synthesis The high urine Cl and Na exclude GI chloride loss; the low FeCa excludes Bartter and loop diuretic; the negative diuretic screen excludes thiazide; the normal BP and elevated renin/aldo exclude Liddle, AME, primary aldosteronism, Cushing, CAH, and reninoma/renal artery stenosis. The remaining diagnosis is **Gitelman syndrome**, confirmed by ***SLC12A3* sequencing**.

## ⟪BabelTele⟫
🧭 体例 ⟦A⟧⟨We need solve math problem.⟩ ‖ ⟦C⟧⟨We need answer clinical reasoning.⟩ ‖ ⟦D⟧⟨We need answer medical diagnostic reasoning.⟩ ⇒ 四份思维链只出自一道题吗? 不: 出自两道题, 每题两次。同一模型(串 1 种写法, 去前缀 1 种)、同一抓取器、同一区段口径; 题面哈希只有 2 种(自校验 4/四份), 抓取时刻跨 2 个日子: 第一次在十月十九日 18:12, 第二次在十月二十一日凌晨 04:53 与 04:55。区段长度有三套口径: 按标记直找与按空行分节恒差 2 字符(两端各一枚换行), 严格正则与前者差 0, 题面也有 1 之差。这条与 B50 箭头相反: B50 是同模型⇎换题, 这条是同模型⇎同题⇎换一次采样, 于是“可复现”第一次成了被测量的量而不是默认前提。
📏 长度就不复现 ⟦A⟧⟨sets. That is a clean characterization: S is extrem⟩ ‖ ⟦C⟧⟨- DCT (Gitelman, thiazides) reabsorbs ~5⟩ ⇒ 同一道题两次推理 23309 ⇎ 81286 ⇎ 22985 ⇎ 101356 字符(第二次是第一次的 3.49 倍／肾病侧 4.41 倍), 非空行 92 ⇎ 554 ⇎ 102 ⇎ 639, 句子 592 ⇎ 1491 ⇎ 312 ⇎ 1299, 单行句 612 ⇎ 1681 ⇎ 341 ⇎ 1445, 五词串 4874 ⇎ 15432 ⇎ 3050 ⇎ 13520, 数字符 1975 ⇎ 3488 ⇎ 239 ⇎ 1014, 词 4165 ⇎ 14557 ⇎ 3077 ⇎ 14766。更硬的一条在末尾: 四段末字符码位 109 ⇎ 46 ⇎ 53 ⇎ 46, 其中 2 段不以句子终符收尾——恰好是两次第一次(本条开头那两枚尾锚, 一枚停在被切断的半词上, 一枚停在约数的一半), 两次第二次都以句号收。回答区 0 ⇎ 6908 ⇎ 0 ⇎ 6748: 两次第一次实测各 0 与 0 字符(根本没写出成稿), 两次第二次各写出 6908 与 6748 字符。整份文件 24108 ⇎ 88999 ⇎ 24168 ⇎ 109294 字符 ⇎ 磁盘 24162 ⇎ 89367 ⇎ 24177 ⇎ 109336 字节。判词: 采样先不复现“长度”, 再不复现“内容”; 拿一次思维链当模型的定论来引用, 连它有多长都是抽签结果。
🔁 逐字复现的主体是题面 ⟦A⟧⟨Determine, with proof, the largest possible number of pairs (a, b) of elements of a set S of n positive integers with a < b such that a + b divides a*b. Give the exact extremal value as a function of n and characterize the sets attaining it.⟩ ‖ ⟦C⟧⟨enumerate every cause of hypokalemic metabolic alkalosis with normal-to-low blood pressure, then eliminate each one by explicit reference to a specific number or finding above, and state the single most likely diagnosis plus the confirmatory test. Explain the mechanistic reason behind each elimination step, including why the urinary chloride and the fractional calcium excretion discriminate the way they do, and why Mg is low.⟩ ⇒ 四份推理里都嵌着一段原样的题面: 长度 241 ⇎ 270 ⇎ 429 ⇎ 111, 在推理区里的起点 17343 ⇎ 38453 ⇎ 7674 ⇎ 56316。两个数合起来才是要点: 引用不在开头而在中段(数论一推到 17343 字符处才回头重读题面, 肾病二推到 56316 处), 可见复读是收尾动作而不是起手动作; 四段引用长度互不相等——数论两次分别截出 241 与 270 字符, 肾病两次截出 429 与 111 字符, 同一条题面被两次采样各抄走不同的一截: 数论一那截 241 字符在两处都原样出现(所以它同时是同题对的公共片段), 数论二那一整截 270 字符只多了一句开头, 却只在这一份里出现。连“复读了题面”都不必是同一句复读。
✂️ 扣掉题面之后还剩什么 ⟦A⟧⟨Determine, with proof, the largest possible number of pairs (a, b) of elements of a set S of n positive integers with a < b such that a + b divides a*b. Give the exact extremal value as a function of n and characterize the sets attaining it." I⟩ ‖ ⟦C⟧⟨- Congenital adrenal hyperplasia (11β-hydroxylase, 17α-hydroxylase): hypertension, low renin/aldo⟩ ⇒ 同题两次之间 >=40 字符的极大公共片段, 数论 ⇎ 肾病四格口径依次是: 块数 14 ⇎ 57, 合计字符 981 ⇎ 2903, 最长块 244 ⇎ 97, 纯题面 8 ⇎ 11 块。扣掉题面后剩下的不是“同一番思考”, 而是三类不用想也能写对的东西: 其一, 被算术逼死的构造 ⟦A⟧⟨={1,2,3,4}, L=lcm(3,4,5,5,6,7)=420. S={420,840,1260,1680}.⟩(两次都在 n=4 上写出同一行 lcm 与同一组四个数); 其二, 教科书级条目与机制句, 连措辞都不变 ⟦C⟧⟨decreased intracellular Na and increased basolateral Na/Ca exchange⟩ ‖ ⟦C⟧⟨metabolic alkalosis, hypomagnesemia, hypocalciuria, high renin/aldo⟩; 其三, 指令的尾巴换了载体又出现一次 ⟦A⟧⟨. Reason out loud, showing every arithmetic check you make."⟩ ‖ ⟦C⟧⟨"enumerate every cause of hypokalemic metabolic alkalosis with normal-to-low blood pressure⟩。反过来看数论侧最长那块 244 字符: 它比数论一的题面引用 241 只多三枚尾字符(一枚引号、一枚空格、下一个词的首字母), 所以“块层”测到的最长复现仍然只是题面。判词: 能逐字复现的段落几乎都是查得到、或推得出唯一写法的段落; 复现率是检索能力的指标, 不是推理能力的指标。
🧱 句子级的“复现”是假象 ⟦C⟧⟨Need accurate mechanism.⟩ ⇒ 共有量按四种粒度各测一遍(行⇎整段句⇎单行句⇎五词串): 同题数论对 1 ⇎ 17 ⇎ 18 ⇎ 245, 同题肾病对 0 ⇎ 12 ⇎ 21 ⇎ 179; 而跨题的“第二次⇎第二次”那一对 2 ⇎ 12 ⇎ 21 ⇎ 9 在两档粒度上与同题肾病对完全打平, 连“共有行数”一项还反超它。另三对跨题的共有量是 5/5/10(单行句口径), 五词串口径则是 0/0/0/9——除了那一对外凡跨题就归零。两种粒度讲两个相反的故事: 词串级复现的是本题术语(只有同题才会撞), 句子级复现的是阶段套话(与题无关, 只与“这是第几次运行”有关, 例如 ⟦B⟧⟨We can produce maybe 1500-2500 words?⟩)。至于“四份同文”的句子, 一共 2 枚, 全是语气词 (⟦A⟧⟨Hmm.⟩ ‖ ⟦A⟧⟨no.⟩), 其中只有 1 组连四份的大小写都不动。判词: “两份思维链逐句相同”这种说法必须带粒度, 否则等于什么都没测; 把粒度钉死之后剩下的只有感叹词。
📈 第二次不是重放, 是重想 ⟦A⟧⟨Wait maximum number of pairs is trivially all if construction.⟩ ‖ ⟦B⟧⟨Wait our triangle {20,30,60}: minimum 20; other b from divisors of 400: 30 (sum50), 60 (sum80).⟩ ⇒ 同题两次之间, 犹豫与算式的绝对数一律上涨: 设想词 63→205(肾病侧 18→438), 转折词 30→163／43→254, 需求句 38→440／38→440, 等号 368→995／2→29, 问号 189→238／75→172。可一旦除以长度就分岔: 设想词每万字 27.0→25.2 反而回落, 肾病侧 7.8→43.2 才上涨; 等号 157.9→122.4 回落, 0.9→2.9 上涨。判词上半: 数论的第二次只是更长, 肾病的第二次才是更密; 把“想得更谨慎”当成两次采样的共同结论, 在一侧是被长度骗的。结论标记词族在两次第一次里是 0 ⇎ 0, 第二次里是 22 与 18——与回答区从无到有同步。纹丝不动的有 2 族(“让我重算”词族、“重来／推倒”词族): 四份里一次也没有说“重来”; 模型永远在当前句后面追加, 从不删账, 所以第二次读起来更像第一次的思路被继续摊开, 而不是被重新做过。
⚖️ 判断顺序每次都重排 ⟦A⟧⟨Need exact extremal value C(n,2), characterization likely all sets satisfying pairwise condition, but perhaps can give structural characterization.⟩ ‖ ⟦B⟧⟨A natural guess from extremal graph theory might be \(\lfloor n^2/4\rfloor\), but \(n=3\) already disproves it: \(\lfloor9/4\rfloor=2\), while the triangle above has \(3\) good pairs.⟩ ⇒ 数论侧: 第一次停在猜想与构造之间, 把“所有对都可达成”当候选答案写在推导里; 第二次先在推导里怀疑题面 ⟦B⟧⟨Alternative interpretation: "largest possible number of pairs (a,b) of elements of a set S of n positive integers with a<b such that a+b divides a*b" Maybe they ask max over S, and since C(n,2) trivial, maybe the "characterize sets attaining it" means characterize complete sets.⟩, 最后在答案区判定题面缺约束 ⟦B⟧⟨Thus, for the problem as stated, the extremal number is the full binomial coefficient, and the extremal sets are governed only by the finite scaling obstruction \(\Lambda(T)\).⟩ ‖ ⟦B⟧⟨Trying to extend \(\{20,30,60\}\) by hand also dead-ends: any fourth element \(d\) must satisfy \(d+20\mid400\), so, apart from \(30,60\), the candidates are \(5,80,180,380\); direct checks against \(30\) eliminate all of them.⟩, 并把不变量写成判词 ⟦B⟧⟨This is the key invariant: every finite configuration can be made admissible by one common dilation, because the obstructions are just finitely many divisibility conditions on \(M\).⟩. 同一个想法在第一次只是草稿 ⟦A⟧⟨Wait for any finite set R of positive integers, choose L = lcm_{i<j}(r_i+r_j).⟩: 两边写着等价的构造, 但一次没有结论, 一次有结论, 且结论是“这题没界”。判词: 采样可复现的是术语与构造, 不可复现的是“把哪一步当作判决”这一步; 这也是 B50 那条“判序属题目”的说法在这里的加强版——同题之下判序仍不可复现。
🩺 排除链换了依据但换了结论吗 ⟦C⟧⟨Need enumerate and eliminate each with specific numbers: BP 104/66 no HTN; renin elevated eliminates low-renin states; aldosterone elevated eliminates low-aldosterone states; primary aldosteronism would have suppressed renin and usually HTN.⟩ ‖ ⟦D⟧⟨The high urine Cl and Na exclude GI chloride loss; the low FeCa excludes Bartter and loop diuretic; the negative diuretic screen excludes thiazide; the normal BP and elevated renin/aldo exclude Liddle, AME, primary aldosteronism, Cushing, CAH, and reninoma/renal artery stenosis.⟩ ⇒ 肾病侧两次都落到同一诊断 ⟦C⟧⟨Gitelman⟩ 上, 但排除的顺序不同: 第一次把尿氯当总闸 ⟦C⟧⟨- Urine Cl 104 also excludes vomiting/NG suction because in those, Cl loss is extrarenal, urine Cl low; excludes post-diuretic state because after diuretic effect wanes, urine Cl low; excludes congenital chloride diarrhea (stool Cl high, urine Cl low); excludes laxative abuse (usually acidosis, low urine Cl).⟩, 并把遗传学模仿者留在最后 ⟦C⟧⟨Could state "Gitelman is far more likely; CLCNKB-related Bartter III is the main genetic mimic and can be covered by a tubulopathy gene panel." Confirmatory test: SLC12A3 sequencing; if negative, CLCNKB.⟩; 第二次先算阴离子间隙 ⟦D⟧⟨Wait urine anion gap = (Na+ + K+) - Cl-; if positive, unmeasured anions (HCO3-) present; if negative, NH4+ high.⟩, 再用钙排泄分数与利尿剂筛查收尾 ⟦D⟧⟨| **Gitelman syndrome** | Fits every finding: K 2.7, HCO3 34, urine K 78, urine Na 96, urine Cl 104, high renin/aldo, BP 104/66, Mg 0.58, FeCa 0.8%, cramps, and salt craving.⟩, 并把“唯一能在生化上存活的模仿者”交给阴性筛查 ⟦D⟧⟨Mention "this is the one mimic that survives the biochemistry; it is excluded by the negative screen/history, but clinically one would confirm with SLC12A3 testing and/or a supervised diuretic screen." This shows false lead.⟩。两次的机制解释逐字复现(见上条), 两次的排除次序一处也不复现。判词: 诊断知识分两层——“哪些病因属于同一族”是可复读的表, “先用哪个数杀哪个假设”是每次重做的判决; 只复现前者而丢失后者, 读起来就像同一次思考, 其实只是同一份清单。
🧪 两次采样给出的可核事实怎么分档 ⟦D⟧⟨We need answer medical diagnostic reasoning.⟩ ⇒ 三档。第一档 B51V 可复算: 四段区长度、行/句/单行句/五词串集合交、>=40 字公共片段、题面引用长度与起点、22 族词法计数、末字符码位——全部由 audit.py 的 _b51_scan 从四份 raw 重算。第二档只能由集合运算得出: 逐字复现的百分比、名次随分母翻转(27.0 ⇎ 25.2 ⇎ 7.8 ⇎ 43.2 一类的每万字口径)。第三档是工具侧: difflib 的整段对齐量(命中字符总数与 ratio)与抓取时刻, 前者慢到不能进门槛, 只在 _probe51.py 里量并如实注明。锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 36 处／35 条去重串, 命中列分布是同题对 11 ⇎ 跨题 1 ⇎ 单源 21 ⇎ 四源皆有 2, 每条去重串对四份源逐一判成员, 共 140 次检查, 错配 0 处——归属由正文现推, 不由旁注文件说了算。
∴ 骨架 ⇒ ① 四份一模型两题(哈希 2 种), 推理区 23309 ⇎ 81286 ⇎ 22985 ⇎ 101356 ⇎ 回答区 0 ⇎ 6908 ⇎ 0 ⇎ 6748; ② 第二次是第一次的 3.49/4.41 倍, 两次第一次末字符非句终(2/4); ③ 题面引用 241 ⇎ 270 ⇎ 429 ⇎ 111, 起点 17343 ⇎ 38453 ⇎ 7674 ⇎ 56316; ④ 同题 >=40 字公共片段 14 ⇎ 57 块 981 ⇎ 2903 字, 纯题面 8 ⇎ 11 块; ⑤ 共有量四种粒度同题 1 ⇎ 17 ⇎ 18 ⇎ 245 ⇎ 0 ⇎ 12 ⇎ 21 ⇎ 179, 跨题第二次对 2 ⇎ 12 ⇎ 21 ⇎ 9, 五词串跨题近乎归零; ⑥ 四份同文的句子只有语气词 2 枚; ⑦ 设想词 63→205 ⇎ 18→438, 等号 368→995, “让我重算”与“重来／推倒”两族四份皆零; ⑧ 数论判词只出现在第二次, 肾病的排除依据在两次之间换掉。判词: 思维链的“可复现部分”= 题面回声 + 术语条目 + 被算术逼死的构造, “不可复现部分”= 长度、判序、中间量与结论形状; 把一次采样当证据来引用, 能引用的只有前半部分, 而后半部分恰好是这条语料的价值所在。
ℒ 方法 ⇒ 读“同一模型同一题的两次采样”先问粒度再问比例: 字符层(difflib 侧, 工具量)、块层(>=40 字极大公共片段, 可复算)、句子层(单行句集合交)、词组层(五词串集合交)。四层的结论并不一致, 混用就会得出“复现率两成”这类无分母、无粒度、也没扣题面回声的话。第二步把公共片段按“能否在原样题面里找到”分成两堆, 只有第二堆才算推理的复现。第三步用跨题对作对照: 同题对的共有量若不比跨题对高, 那份共有就是套话; 本条正是靠 2 ⇎ 12 ⇎ 21 ⇎ 9 与 0 ⇎ 12 ⇎ 21 ⇎ 179 打平这件事, 把句子级复现否掉。第四步注意锚的归属由正文标签现推, 共有锚要在两份源里各命中一枚, 单源锚要在其余三份里零命中。第五步永远先测“第一次有没有写完”: 两次第一次的回答区都是 0 与 0 字符, 于是任何“模型最终答案”的说法在这里只能引用第二次。
✂️ 为什么这份编码比摘要窗口长 ⇒ 四段推理区合计 228936 字符, 最长段是最短段的 4.41 倍, 而摘要只能取锚点触到的窗口; 本条的锚特意选了长片段(题面引用一条就 241/270/429 字符), 因为它们要被两份源同时命中才算数。真正的结论不住在窗口里——“同题对的句子级共有不比跨题对高”“纯题面块数与总块数之比”“犹豫计数膨胀而重来词族恒零”都是四格矩阵上的形状, 要整段复算才看得见。读它请按“哪一格与哪一格打平”来读, 而不是按“少抄了多少原文”。

## ⛓解读注

**这套数是怎么来的**: 两道题各采两次(同一模型、同一抓取器 `corpus/fetch_cot.py`): 数论题 `math_subsets.md` ⇎ `math_subsets_s2.md`, 肾病题 `med_gitalb.md` ⇎ `med_gitalb_s2.md`; 题面 sha 只有 2 种(各自校验 4/4), 抓取跨 2 个日子——第一次在 2026-10-19T18:12:48, 第二次在 2026-10-21T04:53:31 与 2026-10-21T04:55:50, 同题两次之间隔 34.68 与 34.72 小时。
每条数由三套独立实现各算一遍再对齐: 采集侧 `corpus/_pick51.py` ⇎ 建条目侧 `corpus/_mkB51.py` ⇎ 审计器侧 `corpus/audit.py::_b51_scan()`。
本注写这行时又比对了一次: 可比键 72 个、键内数值 222 枚(四段长度、四种粒度集合交、公共片段四格、题面引用长度与起点、22 族词法计数、末字符码位、锚统计), 三边全部相等(快照 `corpus/_b51audit.json`)。
审计器另算另证的推导键 128 枚, 其中 `0` 一枚折 31 个零项: 四份皆零的 let me 与 redo 两族、跨题对归零的行/五词串交集、以及各段为零的回答区/结论标记/粗体/犹豫/明说不确定/必须/假设/推翻; 锚归属错配也在这枚键里(实测 0)。

**锚的三口径**(正文引用 36 处 ⇎ 去重 35 串 ⇎ 注册 35 条, 每标签 A:11 B:7 C:12 D:6):
① 完全逐字(连空格与引号字形都不动)命中其标注那一段的 35/35 条;
② 只折叠空白后命中 35/35 条;
③ 再加撇号/引号剔除、连接号归一与大小写归一(即 `audit.py` 的 `prose_norm`)后 35/35 条。三口径在这批上完全重合: 门槛按③判, 但①②也无缺口——四段的锚都落在原文自己的字形上, 没有靠归一才救回来的引号或连接号。留着三口径是为了换一批抓取时能立刻量出字形问题的条数。
命中列分布(按③对四份源逐一判成员, 共 140 次检查): 恰命中 1 份 21 条 ⇎ 恰命中 2 份 12 条(同题对 11 ⇎ 跨题 1)⇎ 恰命中 3 份 0 条 ⇎ 四份皆命中 2 条; 错配 0 条。
“恰命中 3 份 = 0”不是巧合而是构造约束: 一截文字若同时出现在同题两次采样里, 它就与第三道题无关。

**三档可核性**: 第一档进门槛(`_b51_scan` 秒级复算)——块层用 >=40 字极大公共片段滑窗(同题对 14 ⇎ 57 块, 合计 981 ⇎ 2903 字), 句子层与词组层用集合交。第二档由集合运算得出(名次随分母翻转的每万字口径)。第三档只能靠工具侧整段对齐: `difflib.SequenceMatcher(autojunk=False)` 在 23309 字 × 81286 字上量得逐字命中 3580 字符(占前一份 15.4%, ratio 0.068, 最长连续 244 字), 肾病对 4794 字符(20.9%, ratio 0.077, 最长 97 字); 拆成两档后, 数论对 102 块 1790 字符里题面回声 324 ⇎ 推理复用 1466, 肾病对 154 块 2842 字符里回声 791 ⇎ 复用 2051。这一档慢到不能进门槛(分钟级), 所以只在 `corpus/_probe51.py` 里量并如实注明——条目正文里凡是“复现了多少字符”的说法都改写成块层可复算的数, 而不是这个比例。

**digest 侧**: 四段各出一节(`### ⟦标签⟧ ⟸ 文件`), 共 4 节。摘要段含换行 10429 字符(审计表“摘要段”一栏取的就是这个数), 去掉换行 10329; 编码区不含换行 9340。于是“vs 摘要段”按表口径是 89.6% ⇎ 按“两侧都去换行”是 90.4%——两栏之差只是 100 枚换行的归属, 两个数在此都登记。这条的编码/原文整段比是 4.08%: 四段推理区合计 228936 字符, 摘要只能取锚点触到的窗口, 而本条的锚特意选了长片段(题面引用一枚就 241/270/429/111 字符), 因为它们要被同题两份源同时命中才算数。真正的结论不住在窗口里——“同题对的句子级共有不比跨题对高”“纯题面块数与总块数之比”“犹豫计数同向膨胀而 redo 恒零”都是四格矩阵上的形状, 要整段复算才看得见。

**同一数的不同含义**(同值冲突 22 组, DERIV 一个值只留一枚键, 所以这些说法必须靠注里的上下文区分): 1=caveat·肾病一、hmm·数论一、hmm·肾病一、ov_l·A⇎B、wait·肾病一、wrong·数论二、去前缀后模型种数、命中列跨题的锚、四源同文里四份表面写法全同的组数、模型串写法数、题面两口径差；10=bold·数论二、prob·肾病一、单行句·数论二⇎肾病一；11=verif·数论一、命中列恰为同题对的锚、纯题面块数·肾病；12=ov_s·B⇎D、ov_s·C⇎D；14=lets·肾病一、公共片段块数·数论；18=final·肾病二、maybe·肾病一、ov_ls·A⇎B、结论标记·肾病二；2=assume·数论二、bold·肾病二、equality·肾病一、ov_l·B⇎D、prob·数论一、unsure·肾病二、区段两口径差、四份皆零的模式族数、四源同文单行句、四源同文整段句、四源皆命中的锚、抓取日数、末字符非句终的段数、等号·肾病一、题面哈希种数；21=ov_ls·B⇎D、ov_ls·C⇎D、verif·肾病二、只命中一份源的锚；22=final·数论二、词法模式族数；3=assume·肾病二、must·数论一；30=however·数论一、lets·数论一、wait·数论二；38=need·数论一、need·肾病一、需求句·肾病一；4=actually·肾病一、hmm·肾病二、verif·肾病一、wait·肾病二、源数、题面哈希自校验命中；46=末字符码位·数论二、末字符码位·肾病二；5=caveat·数论二、prob·数论二、单行句·数论一⇎肾病一、单行句·数论一⇎肾病二；53=need·数论二、末字符码位·肾病一；575=题面字符·数论一、题面字符·数论二；6=actually·数论一、arrow·肾病一、caveat·肾病二、hmm·数论二；7=therefore·肾病一、wait·数论一；8=arrow·数论二、must·数论二、纯题面块数·数论；9=arrow·数论一、ov_sg·B⇎D、五词串·数论二⇎肾病二；961=题面字符·肾病一、题面字符·肾病二
最扎眼的一组是题面长度: 同一道题两次采样的题面字符数相同(575 ⇎ 575), 于是“推理区长度”“题面长度”“词法计数”在同值键上会互相顶掉——这也是本条把每种口径都单独登记成 B51V 表达式而不是只写数字的原因。

**跑法**: `python -X utf8 corpus/audit.py` ⇒ B51 行 T1/T2 编码失配 0 ⇎ 原文失配 0 ⇎ T3 码位 0 ⇎ 小整数待核 0; 门槛 PASS, 全库 51 条, 软提示 17 枚未增长, 本条被点名的推导 108 枚全部成立(另 20 枚登记在同值折等里、正文没有把它们写成独立数字, 但 `_b51_scan` 照样复算它们)。
`python -X utf8 corpus/atomcheck.py B51 corpus/_atoms51.txt` ⇒ ok=35 bad=0。
`python -X utf8 corpus/_wire51.py` 重复运行会先摘旧块再插新块(幂等), 且插门前先把 DERIV 的 128 条算式在刚写好的扫描器上预演一遍, 值不符就当场停机。