# B50 同一模型 ⇎ 六个领域的难题思维链：会打断自己是机器的习惯，会写等号是题目的习惯
src: corpus/raw/cot/math_subsets.md (推理区 23309 字符 ⇎ 题面 575 ⇎ 回答 0) ⇎ corpus/raw/cot/med_gitalb.md (推理区 22985 字符 ⇎ 题面 961 ⇎ 回答 0) ⇎ corpus/raw/cot/law_ewca_method.md (推理区 64995 字符 ⇎ 题面 1387 ⇎ 回答 0) ⇎ corpus/raw/cot/fin_credit_cmte.md (推理区 68874 字符 ⇎ 题面 1284 ⇎ 回答 0) ⇎ corpus/raw/cot/ind_creep_rupture.md (推理区 22236 字符 ⇎ 题面 2815 ⇎ 回答 0) ⇎ corpus/raw/cot/str_quake_slab.md (推理区 65139 字符 ⇎ 题面 3241 ⇎ 回答 0) (sha256 见各文件头部, 六枚互不相同)
；联结不是“同一份材料的三种载体”, 而是“同一台机器的六个断面”: 六段出自同一模型(串 2 种写法)、六道互不相干的难题(题面哈希 6 种), 回答区六段皆空而推理区六段全断在半句上; 可核性走六格矩阵——六格全正者属机器, 有零有正者属题目, 每个数由 audit.py 的 B50V 从六份 raw 整段复算
tags: 六格矩阵 同模型⇎换题 区段三口径 截断即口径 就地打补丁从不重来 记号密度=领域函数 每万字归一翻名次 权威词只在有权威处 粗体分域 检索腔⇎计算腔 六源互斥锚 词形口径漏项 restart假阳性 回答区为空
## [[原始语料|ORIGINAL]]
### ⟦M⟧ ⟸ corpus/raw/cot/math_subsets.md

## [[REASONING]] We need solve math problem. Need rigorous, research style, small n, conjecture, proof, dead ends, key invariant. Need characterize extremal sets.

Actually a+b | ab iff 1/a + 1/b = (a+b)/ab is reciprocal integer? Since ab/(a+b) integer iff 1/a+1/b = 1/m where m=ab/(a+b)? Wait ab/(a+b) integer iff (a+b)|ab. Then 1/a + 1/b = (a+b)/ab = 1/m with m=ab/(a+b).

Try small n. n=1: 0.

Thus all cliques are essentially scaled primitive sets. That is a clean characterization: S is extrem ## [[ANSWER]]

### ⟦D⟧ ⟸ corpus/raw/cot/med_gitalb.md

## [[REASONING]] We need answer clinical reasoning. Need be thorough. Need reason as nephrologist. We need enumerate every cause of hypokalemic metabolic alkalosis with normal-to-low BP, eliminate by explicit numbers.

Need enumerate every cause of hypokalemic metabolic alkalosis with normal-to-low BP. Categories: - GI losses:

Let's include GI: - Vomiting/NG suction: low urine Cl (<20), low urine Na, hypokalemia, metabolic alkalosis; but urine Cl 104 eliminates. - Pyloric stenosis etc same.

Wait, how does Gitelman cause hypocalciuria? Need explain correctly. In DCT, thiazide inhibit

- DCT (Gitelman, thiazides) reabsorbs ~5 ## [[ANSWER]]

### ⟦L⟧ ⟸ corpus/raw/cot/law_ewca_method.md

## [[REASONING]] All tools disabled. I must answer from reasoning. Let me thoroughly analyze the legal question and craft a comprehensive answer that meets the user's request.

I don't have it in my training data. But the reasoning method described is quite specific and could be drawn from a judgment about the recognition of foreign judgments in IP cases.

- *Kookmin Bank v Rainy Sky*? No. - *Joint Stock Co "Aeroflot - Russian Airlines" v Berezovsky*? No.

Wait: If both are English law, is the answer "English law" too obvious? The question may expect a more nuanced answer: the plea is determined by English law because the forum is England and the right is English.

Let me recall: The 2019 Hague Judgments Convention excludes, inter alia, "i

- The English Court of Appeal held that the plea of issue estoppel was governed by **English law** because the recognition of foreign judgments is a matter of the lex fori, and the foreign judgment did not create an estoppel as to the English copyright because the issue was not the same (the foreign court applied foreign law).

### ⟦F⟧ ⟸ corpus/raw/cot/fin_credit_cmte.md

## [[REASONING]] Websearch disabled. Need rely knowledge. Let's think more.

Under 12 CFR 32, a national bank's loans to one borrower cannot exceed 15% of unimpaired capital and surplus; with 10% additional for readily marketable collateral.

The premise is wrong. It would need no charter change.

Could there be a **unit error**: $480m loan, EBITDA $36m, but "5.5x EBITDA leverage" maybe $480m / 5.5 = $87.3m EBITDA, not $36m.

**Leverage**: 480/36 = 13.3333. 540/36 = 15.0.

### ⟦I⟧ ⟸ corpus/raw/cot/ind_creep_rupture.md

## [[REASONING]] We need answer complex forensic engineering. Need details, calculations. Need no tools really. Need produce working.

Renewable diesel hydroprocessing unit, restart after 21-day turnaround. Six weeks later startup at 74% design rate outlet tube fired heater ruptured, H2 at 62 bar, light feed, fire.

Maybe they expect: D = t1/L1 + t2/L2. Six weeks = 1008 h.

Wait 6 weeks plus 11 days? The TC failed 11 days before last reading, but not necessarily overtemp duration.

### ⟦S⟧ ⟸ corpus/raw/cot/str_quake_slab.md

## [[REASONING]] We need answer forensic structural engineering. Need work, not clean conclusion. Must be concise? User asks detailed multi-part.

Residual storey drift 45 mm over 3.6 m = 1.25%. Total drift unknown, no record.

Wait owner says diagonal cosmetic; we must rule. The slab depression may indicate punching, but 22 mm could be from slab deflection due to column settlement? Hmm.

Maybe "not rejected until verified." 5.

Maybe phrase "The only alternative I cannot reject is punching shear; that is the point." This is good forensic reasoning.

- Medium: base hinge governs over diagonal shear; slab ## [[ANSWER]]

## ⟪BabelTele⟫
🧭 体例 ⟦M⟧⟨We need solve math problem. Need rigorous, research style, small n, conjecture, proof, dead ends, key invariant.⟩ ‖ ⟦D⟧⟨We need answer clinical reasoning. Need be thorough. Need reason as nephrologist.⟩ ‖ ⟦L⟧⟨All tools disabled. I must answer from reasoning.⟩ ‖ ⟦F⟧⟨Websearch disabled. Need rely knowledge.⟩ ‖ ⟦I⟧⟨We need answer complex forensic engineering.⟩ ‖ ⟦S⟧⟨We need answer forensic structural engineering. Need work, not clean conclusion.⟩ ⇒ 六个源不是六份材料, 是同一台机器在六道难题上的六次运行: 模型串有两种写法(带 `opencode/` 前缀 ⇎ 不带), 去掉前缀后是 1 种; 题面哈希 6 种, 其中 6/6 枚能在“空行分节”的口径下逐字节复算命中; 抓取时刻 4 组。区段有三套长度: 题面字符 575 ⇎ 961 ⇎ 1387 ⇎ 1284 ⇎ 2815 ⇎ 3241 ⇎ 推理区字符 23309 ⇎ 22985 ⇎ 64995 ⇎ 68874 ⇎ 22236 ⇎ 65139 ⇎ 回答区 0 字符(六段皆空); 整份文件 24108 ⇎ 24168 ⇎ 66609 ⇎ 70385 ⇎ 25271 ⇎ 68606 字符 ⇎ 磁盘 24162 ⇎ 24177 ⇎ 66641 ⇎ 70425 ⇎ 25310 ⇎ 68707 字节。本库已有同题 ⇎ 换模型的对照(B27/B36), 这条把箭头反过来: 同模型 ⇎ 换题, 于是“哪些推理习惯属于机器、哪些属于题目”成了可数的对照。
✂️ 六段思维链全部断在半句上 ⟦M⟧⟨ sets. That is a clean characterization: S is extrem⟩ ‖ ⟦D⟧⟨- DCT (Gitelman, thiazides) reabsorbs ~5⟩ ‖ ⟦S⟧⟨Medium: base hinge governs over diagonal shear; slab⟩ ⇒ 六个推理区的最后一个词是 extrem、~5、different、drawn,、this、slab: 6/6 段不以句子终符收尾, 而回答区六段实测各 0 字符。头部自报与区段实长一致, 但“按节标直找”与“按空行分节”两种口径恒差 2 个字符(两端各一枚换行)——题面也有两套: 哈希覆盖含末尾换行的 576 字符, 报出来的长度是去掉首尾空白的 575, 恒差 1。报数时不写口径, 这些数就会看着像几个不同的长度。后果是一条纪律: 这批原料只能证明模型怎样想, 不能证明它最后答了什么; 连“结论”这个词都不站在源里——final/conclusion/recommend 一类计数是 0 ⇎ 0 ⇎ 13 ⇎ 8 ⇎ 7 ⇎ 12, 其中两段的计数为 0, 而那两段的区段末尾也确实断在推导中间。
🔁 自我修正只用三个词, 而且从不重来 ⟦M⟧⟨Wait ab/(a+b) integer iff (a+b)|ab.⟩ ‖ ⟦D⟧⟨Wait, how does Gitelman cause hypocalciuria? Need explain correctly.⟩ ‖ ⟦L⟧⟨Wait: If both are English law⟩ ‖ ⟦I⟧⟨Wait 6 weeks plus 11 days?⟩ ⇒ 同一台机器在六个领域里打断自己的方式高度一致: Wait 7 ⇎ 1 ⇎ 3 ⇎ 4 ⇎ 1 ⇎ 5 ⇎ actually 6 ⇎ 4 ⇎ 8 ⇎ 4 ⇎ 4 ⇎ 10 ⇎ Hmm 1 ⇎ 1 ⇎ 2 ⇎ 6 ⇎ 5 ⇎ 8, 三样在六段里都至少出现一次; 核心 19 条模式里有 9 条六源皆有。反过来, redo/start over/let me recompute 一类“推倒重来”的说法在六段里是 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0: 修正永远是一句“等一下”追加在后面, 不清账。两处词形口径必须点名。其一, 数 restart 会误判: 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 6 ⇎ 0, 非零那一段的六枚全在说装置本身重启(⟦I⟧⟨restart after 21-day turnaround.⟩), 与推理重来无关; 其二, 只按 not sure/unclear/I think 数“承认不确定”会得 0 ⇎ 0 ⇎ 4 ⇎ 1 ⇎ 1 ⇎ 0, 而 uncertain 一族是 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 3, 其中震后段明说 0 次、词形 3 次——同一件事的两种词形, 模式写窄了就整段漏掉。
🧮 写不写算式是领域习惯 ⟦M⟧⟨Actually a+b | ab iff 1/a + 1/b = (a+b)/ab is reciprocal integer?⟩ ‖ ⟦F⟧⟨480/36 = 13.3333.⟩ ‖ ⟦I⟧⟨D = t1/L1 + t2/L2.⟩ ‖ ⟦S⟧⟨Residual storey drift 45 mm over 3.6 m = 1.25%.⟩ ⇒ 等号密度 368 ⇎ 2 ⇎ 0 ⇎ 265 ⇎ 79 ⇎ 246, 归一到每万字是 157.9 ⇎ 0.9 ⇎ 0.0 ⇎ 38.5 ⇎ 35.5 ⇎ 37.8: 数论段每万字一枚接一枚, 判例段一整篇 0 枚都不写, 肾病段 0.9 枚。工程两段的因果链用箭头而不是等号: -> 计数 9 ⇎ 6 ⇎ 0 ⇎ 0 ⇎ 34 ⇎ 17(判例与信贷两段是 0), 单位记号 231 ⇎ 16 ⇎ 82 ⇎ 123 ⇎ 49 ⇎ 241, 带数字的句子 277 ⇎ 66 ⇎ 85 ⇎ 322 ⇎ 168 ⇎ 348。判词: “这台机器会不会做算术”是题目的函数而不是机器的函数; 跨领域比风格时必须先把记号除上长度, 否则写得长的那段永远看着更勤快。
📜 义务词、条款号与粗体只长在有权威的地方 ⟦L⟧⟨Let me recall: The 2019 Hague Judgments Convention⟩ ‖ ⟦F⟧⟨12 CFR 32, a national bank's loans to one borrower cannot exceed 15% of unimpaired capital and surplus⟩ ‖ ⟦L⟧⟨held that the plea of issue estoppel was governed by **English law**⟩ ‖ ⟦S⟧⟨owner says diagonal cosmetic; we must rule.⟩ ⇒ 条款词 article/section/§/clause/paragraph: 0 ⇎ 0 ⇎ 33 ⇎ 13 ⇎ 0 ⇎ 12, 其中数论与肾病两段为 0 ⇎ 炉管段也是 0; must: 3 ⇎ 0 ⇎ 24 ⇎ 12 ⇎ 0 ⇎ 11, 肾病段 0、炉管段同样为零; markdown 粗体对 0 ⇎ 0 ⇎ 97 ⇎ 169 ⇎ 0 ⇎ 0——只有判例与信贷两段用, 数论段是 0。检索腔与计算腔也分得开: let me 0 ⇎ 0 ⇎ 29 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ let's 30 ⇎ 14 ⇎ 3 ⇎ 29 ⇎ 10 ⇎ 24, 判例段把 let me 用 29 次而 let's 只 3 次, 因为它在往记忆里查案名(⟦L⟧⟨Let me recall: The 2019 Hague Judgments Convention⟩), 别段在往下算。题面没给权威时它就不引用权威; 题面给了条款号时它把条款号抄进推理里(⟦F⟧⟨12 CFR 32, a national bank's loans to one borrower cannot exceed 15% of unimpaired capital and surplus⟩), 甚至怀疑题面自己抄错了单位(⟦F⟧⟨Could there be a **unit error**⟩)。
❓ 犹豫的形状: 泛化的 maybe ⇎ 少见的自认 ⟦M⟧⟨Try small n.⟩ ‖ ⟦D⟧⟨but urine Cl 104 eliminates.⟩ ‖ ⟦S⟧⟨The only alternative I cannot reject is punching shear; that is the point.⟩ ⇒ maybe/perhaps 63 ⇎ 18 ⇎ 12 ⇎ 108 ⇎ 50 ⇎ 78 六段皆有, 是这台机器最便宜的 hedge; 明说不确定(not sure/unclear/I think)则是 0 ⇎ 0 ⇎ 4 ⇎ 1 ⇎ 1 ⇎ 0。两者的比在六段里差得最远: 数论段 maybe 63 次而明说不确定 0 次(推不动只叫 Hmm), 震后段 maybe 78 次、认 0 次, 而且它把“不认”写进判决(⟦S⟧⟨not rejected until verified⟩)。引号回述题面与原文的密度 20 ⇎ 31 ⇎ 78 ⇎ 229 ⇎ 39 ⇎ 56: 信贷段 229 处为六段最高, 它靠把题面措辞抄回来找漏洞(⟦F⟧⟨The premise is wrong.⟩); 法条段的回述则是把待引的案名原样括出来(⟦L⟧⟨Kookmin Bank v Rainy Sky*? No.⟩)。
📏 长度是混淆项: 原始计数与每万字归一会翻名次 ⟦D⟧⟨Need enumerate every cause of hypokalemic metabolic alkalosis with normal-to-low BP.⟩ ‖ ⟦I⟧⟨Need no tools really.⟩ ⇒ 句子数 591 ⇎ 311 ⇎ 584 ⇎ 760 ⇎ 295 ⇎ 825 ⇎ 非空段数 92 ⇎ 102 ⇎ 208 ⇎ 349 ⇎ 74 ⇎ 221。核心 19 条模式里, 按原始计数排第一的领域与按每万字排第一的领域不一致的有 6 条(actually、final、however、maybe、unit、verif)。maybe 那一例最直白: 信贷段原始 108 枚高于数论段 63 枚, 归一后反而是数论段每万字 27.0 ⇎ 信贷段 15.7。而推理区长度本身最长段是最短段的 3.1 倍(六段合计 267538 字符, 各段 23309 ⇎ 22985 ⇎ 64995 ⇎ 68874 ⇎ 22236 ⇎ 65139), 所以本条每个“谁更怎样”的说法都带口径二字——只抄原始计数就等于把“写得长”读成“想得多”。
⚖ 怎么把“机器的习惯”与“题目的习惯”分开 ⟦L⟧⟨I don't have it in my training data.⟩ ‖ ⟦S⟧⟨We need answer forensic structural engineering. Need work, not clean conclusion.⟩ ⇒ 三步。① 先钉住不变量: 同一模型(去前缀 1 种)、同一抓取器、同一区段口径(6 段哈希 6/6 自校验)。② 再对每个候选习惯问“六格是不是都≥1”: 六源皆有的核心模式 9 条(actually、however、maybe、prob、quote、therefore、unit、verif、wait), 六源皆空的 1 条(redo)——这两列才是机器常量。③ 剩下的算领域函数: 等号在判例段 0、条款词在数论段 0、粗体在数论段 0、must 在肾病段 0、明说不确定在肾病段 0。锚的可核性也走六源: 注册 54 条(去重 54 条), 每条只在标注那一段逐字命中, 跨源命中的 0 条, 共 324 次成员检查——六段都以“We need …/… disabled.”起手, 若锚只取半句套话, 对照立刻被共享套话抹平。
∴ 骨架 ⇒ ① 同一模型六道难题, 推理区 23309 ⇎ 22985 ⇎ 64995 ⇎ 68874 ⇎ 22236 ⇎ 65139 ⇎ 回答区六段 0; ② 六段末字符全非句终(6/6), 故“结论”不在源内; ③ 打断自己的三个词六段皆有: Wait 7 ⇎ 1 ⇎ 3 ⇎ 4 ⇎ 1 ⇎ 5 ⇎ actually 6 ⇎ 4 ⇎ 8 ⇎ 4 ⇎ 4 ⇎ 10 ⇎ Hmm 1 ⇎ 1 ⇎ 2 ⇎ 6 ⇎ 5 ⇎ 8; ④ 推倒重来六段皆零(0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0); ⑤ 等号 368 ⇎ 2 ⇎ 0 ⇎ 265 ⇎ 79 ⇎ 246; ⑥ 条款词 0 ⇎ 0 ⇎ 33 ⇎ 13 ⇎ 0 ⇎ 12; ⑦ must 3 ⇎ 0 ⇎ 24 ⇎ 12 ⇎ 0 ⇎ 11; ⑧ 粗体 0 ⇎ 0 ⇎ 97 ⇎ 169 ⇎ 0 ⇎ 0; ⑨ 箭头 9 ⇎ 6 ⇎ 0 ⇎ 0 ⇎ 34 ⇎ 17; ⑩ 明说不确定 0 ⇎ 0 ⇎ 4 ⇎ 1 ⇎ 1 ⇎ 0; ⑪ 引号回述 20 ⇎ 31 ⇎ 78 ⇎ 229 ⇎ 39 ⇎ 56; ⑫ 核心 19 条模式中六源皆有 9 条、皆空 1 条, 原始计数与每万字归一名次不一致 6 条。判词: 思维链的“风格”可拆两层——跨题不变的词法习惯(打断、hedge、不重来)属机器, 记号选择(等号、条款号、粗体、箭头)属题目; 两层混谈就会把“这道题是数学”误读成“这个模型会数学”。
ℒ 方法 ⇒ 读这种六源矩阵先读口径再读内容: 区段怎么切(空行分节 ⇎ 标记直找, 恒差 2 字符)、模型串算几种(2 种写法 ⇎ 1 种实体)、回答区算不算文本(六段 0)。然后把每个候选习惯摊成六格, 只问三种问题: 六格全正(机器常量)、六格全零(机器从不做)、有零有正(领域函数); 不问“哪段更有条理”这类没有分母的话。第三步给每个计数配一个归一版本, 并公布两者名次不一致的模式数(6)。第四步核验锚互斥: 每条锚原子只允许命中其标注那一段(注册 54 条, 跨源 0 条)。第五步记住原料是被切断的中间态: 任何“模型最终认为”的句子都该退回源里找, 找不到就删。
✂️ 为什么这份编码比摘要窗口长 ⇒ 六段推理区合计 267538 字符(各段 23309 ⇎ 22985 ⇎ 64995 ⇎ 68874 ⇎ 22236 ⇎ 65139, 最长是最短段的 3.1 倍), 而摘要只能取锚点触到的窗口: 注册 54 条(去重 54 条)锚各触一段; 正文引用了几处、漏引几枚, 那些是工具侧计数, 写在 ⛓解读注里才算得准。本条的结论不住在窗口里——“等号密度差三个数量级”“推倒重来六段皆零”“粗体只在两段出现”是六格矩阵上的形状, 要整段复算才看得见, 截若干行原文看不到。读它请按“哪几格为零、哪几格为正”来读, 而不是按“少说了多少原文”。

## ⛓解读注

**这套数是怎么来的**: 六道题的同一次批量抓取(抓取器 `corpus/fetch_cot.py`, 模型 `opencode/deepseek-v4.1-flash-free`, 抓取时刻 4 组)。
每条数都由两套独立实现的脚本各算一遍再对齐: 采集侧 `corpus/_pick50.py` ⇎ 审计器侧 `corpus/audit.py::_b50_scan()`。
本注写这行时又比对了一次: 可比键 54 个、键内数值 234 枚, 全部相等(快照 `corpus/_b50audit.json`)。
审计器另算另证的推导键 99 枚(README 表里写的 DERIV 104 键是同一个字典的总键数, 多出的 5 枚以名单本身为键, 机检逐条打勾的是这 99 枚数值键), 其中 `0` 一枚键折 40 个零项: 六源皆零的 redo 类、跨源命中数、以及各段为零的等号/条款词/粗体/箭头/明说不确定/restart/uncertain/let me/结论标记/回答区。

**锚的三口径**(注册 54 条 ⇎ 正文引用 35 处、去重 32 串、未引用 22 条, 每标签 M:5 D:5 L:7 F:6 I:5 S:7):
① 完全逐字(连空格与引号字形都不动)命中其标注那一段的 54/54 条;
② 只折叠空白(把连续空白压成一格)后命中 54/54 条;
③ 再加撇号/引号剔除、连接号归一与大小写归一(即 `atomcheck.py`/`audit.py` 的 `prose_norm`)后 54/54 条。三口径在这批上完全重合: 门槛按③判, 但①②也无缺口——六段的锚都落在原文自己的字形上, 没有靠归一才救回来的引号或连接号。留着三口径是为了换一批抓取时能立刻量出字形问题的条数。
互斥性按③复核: 54 条锚 × 6 段 = 324 次成员检查, 命中数≠1 的 0 条(即没有任何原子在别的段里也能逐字找到)。

**digest 侧**: 六段各出一节(`### ⟦标签⟧ ⟸ 文件`), 共 6 节。摘要段含换行 4097 字符(审计表“摘要段”一栏取的就是这个数), 去掉换行 4027; 编码区不含换行 6369。于是“vs 摘要段”按表口径是 155.5% ⇎ 按“两侧都去换行”是 158.2%——两栏之差只是 70 枚换行的归属, 在此两个数都登记, 免得读作两套不同的量。这条编码比窗口长, 因为要表达的是六格矩阵的形状(哪几格为零)而不是摘录句子。

**同一数的不同含义**(同值冲突 16 组, DERIV 一个值只留一枚键, 所以这些说法必须靠注里的上下文区分): 1=Hmm·数论、Hmm·肾病、Wait·炉管、Wait·肾病、六源皆空的核心模式数、去前缀后模型种数、明说不确定·信贷、明说不确定·炉管、题面·两种口径之差；10=actually·震后、let's·炉管；12=maybe·判例、must·信贷、条款词·震后、结论标记·震后；13=条款词·信贷、结论标记·判例；2=Hmm·判例、两种区段口径之差、模型串写法数、等号·肾病；24=let's·震后、must·判例；29=let me·判例、let's·信贷；3=Wait·判例、let's·判例、must·数论、uncertain 词形·震后；4=Wait·信贷、actually·信贷、actually·炉管、actually·肾病、抓取时刻组数、明说不确定·判例；5=Hmm·炉管、Wait·震后；54=注册锚去重、注册锚数；6=Hmm·信贷、actually·数论、restart 词形·炉管、名次翻转模式数、末字符非句终的段数、源数、箭头·肾病、题面哈希种数、题面哈希自校验命中；7=Wait·数论、结论标记·炉管；78=maybe·震后、引号回述·判例；8=Hmm·震后、actually·判例、结论标记·信贷；9=六源皆有的核心模式数、箭头·数论

**跑法**: `python -X utf8 corpus/audit.py` ⇒ B50 行 T1/T2 编码失配 0 ⇎ 原文失配 0 ⇎ T3 码位 0 ⇎ 小整数待核 0; 门槛 PASS, 全库 50 条, 软提示 17 枚未增长, 本条被点名的推导 99 枚全部成立。
`python -X utf8 corpus/atomcheck.py B50 corpus/_atoms50.txt` ⇒ ok=54 bad=0。