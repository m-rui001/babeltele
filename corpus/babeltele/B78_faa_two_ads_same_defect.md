# B78 同一缺陷的两次适航指令: FAA LPSOV——整改版逐字复制初始版 38 句(占 32.2%), 
但引用走纸面页码不走编号; 处置从"记录风险"升级到"强制改装", 征求意见处数 16⇎3
src: corpus/raw/faa/ad_a.txt (19997 字符) ⇎ corpus/raw/faa/ad_b.txt (15932 字符) (两份同为 Federal Register 纯文本面: FAA AD 2023-01702 ⇎ AD 2023-22080, 同因 LPSOV 线束/UERF; 数字一律从面内现读, 一个都不手填; 抓取时刻与 FR 现行版本只在本机或站外成立, 不进门槛)
; tags: 模板复用键(句集交集三分之一) 处置升级键(记录⇎改装) 引用页码键(FR页码⇎编号) 程序词频键(comment) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/faa/ad_a.txt

This condition, if not addressed, could lead to loss of engine fuel isolation capability in case of UERF, possibly resulting in an uncontrolled fire. The unsafe condition may exist on airplanes with two different types of engines installed.

(c) Applicability This AD applies to the Airbus SAS airplanes specified in paragraphs (c)(1) through (3) of this AD, certificated in any cat

(e) Unsafe Condition This AD was prompted by a safety review of the airplane fuel system, which identified that the electrical harness routing of the engine low pressure shut off valve (LPSOV) is not adequately protected against uncontained engine rotor failure (UERF). The FAA is issuing this AD to address inadequate protection of the LPSOV against UERF.

### ⟦B⟧ ⟸ corpus/raw/faa/ad_b.txt

This AD was prompted by a safety review of the airplane fuel system, which identified that the electrical harness routing of the engine low pressure shut off valve (LPSOV) is not adequately protected against uncontained engine rotor failure (UERF). This AD requires modification of the LPSOV electrical harness routing on either the left-hand engine or the right-hand engine, as specified in a European Union Aviation Safety Agency (EASA) AD, which is incorporated by reference.

The unsafe condition, if not addressed, could result in loss of engine fuel isolation capability in case of UERF, possibly resulting in an uncontrolled fire.

(c) Applicability This AD applies to the Airbus SAS airplanes specified in paragraphs (c)(1) through (3) of this AD, certificated in any cat

## ⟪BabelTele⟫
🧭 同一缺陷(LPSOV 线束防护不足⇒不可包容转子破裂 UERF 失火)的两次 FAA 适航指令, 同为 Federal Register 纯文本面: 初始 AD 2023-01-09 19997 字符⇎整改 AD 2023-10-05 15932 ⇎ 句 121⇎91 句, 每句均值 165⇎175 字符。🔁 监管文体是半成品组装件: 句集交集 A⇎B 38 句(占 A 的 32.2%), 去重句各 118⇎89——整改 AD 的三分之一逐字来自初始 AD: 同一段 prompted-by ⟦A⟧⟨This AD was prompted by a safety review of the airplane fuel system, which identified that the electrical harness routing of the engine low pressure shut off valve (LPSOV) is not adequately protected against uncontained engine rotor failure (UERF).⟩ 两份各 2⇎3 处, 适用范围句 ⟦B⟧⟨This AD applies to the Airbus SAS airplanes specified in paragraphs (c)(1) through (3) of this AD⟩ 亦逐字共享。⚖ 处置升级的两步: A 只记录风险——混装机型的旁注句 ⟦A⟧⟨unsafe condition may exist on airplanes with two different types of engines installed⟩, B 直接要求改装 ⟦B⟧⟨This AD requires modification of the LPSOV electrical harness routing on either the left-hand engine or the right-hand engine⟩ 并给出后果句 ⟦B⟧⟨loss of engine fuel isolation capability in case of UERF, possibly resulting in an uncontrolled fire⟩; unsafe condition 词族 9⇎7 处、modif- 词族 4⇎4 处、inspect- 词族 4⇎4 处、fire 2⇎2 处。🏛 引用走页码不走编号: B 提初始 AD 用纸面页码——"88 FR 5817" 在 B 面 1 处而 "2023-01702" 编号在 B 面 0 处; MCAI(别国适航信息)采纳件身份两份相同(EASA 32⇎26 处、MCAI 8⇎7 处、EASA AD 2022-0185 17⇎13 处); 程序差异: 征求意见 comment 16⇎3 处(A 走了征求意见期, B 收紧处置少听意见)、docket 16⇎13 处、cost 11⇎12 处。ℒ 方法 ⇒ 同一缺陷两次指令的隐性知识在处置升级与文体组装: 句集交集把模板复用做成键(38 句), prompted-by 同句把同因做成键(2⇎3), 引用方式做成键(FR 页码 1 处⇎AD 编号 0 处), 程序词频做成键(comment 16⇎3)。

## ⛓解读注

### 第四遍复测(本注现算, 第三套实现: finditer 句标偏移切片 + findall 计数)

| 量 | 结果 | 与契约 |
|---|---|---|
| 句数/字符 | [121, 91] / [19997, 15932] | 逐份相等 |
| EASA / MCAI(采纳件身份) | [32, 26] / [8, 7] | 逐份相等 |
| prompted by 同因句 | [2, 3] | 逐份相等 |
| comment / cost 程序词 | [16, 3] / [11, 12] | 逐份相等 |
| B 引 A 的页码 88 FR 5817 | [0, 1] | 逐份相等 |
| 句集交集(模板复用) | 38 句(占 A 的 32.2%) | 相等 |

上表 6 行全部 assert, 不符即停机。

### 读法

一、同一缺陷(LPSOV 线束防护不足, 失效场景是不可包容转子破裂 UERF 引燃燃油)两次指令两步走: A 2023-01 只记录风险并要求按 SB 检查/报告, B 2023-10 直接要求改装线束路由并写明后果(失去燃油隔离能力, 可能失控火)——处置从"知道"升级到"动手"。
二、监管文体是组装件: B 的句集有 38 句逐字来自 A(占 A 的约 32%), prompted-by 同句两份各 2/3 处——同因声明是模板, 不是新写的。
三、引用走纸面页码不走编号: B 引初始 AD 用 "88 FR 5817"(1 处)而 AD 编号 2023-01702 在 B 面 0 处——联邦登记的谱系靠页码不靠文号。
四、程序差异: A 走征求意见期(comment 16 处)而 B 只 3 处——处置收紧时听取意见的规模也收紧; 两份同为 MCAI 采纳件(EASA 32/26 处, EASA AD 2022-0185 17/13 处), FAA 在跟随欧洲的发现。

### 本条不能由在库文件判定的(只登记, 不进门槛)

抓取时刻与 FR 现行版本; LPSOV 改装在实际机队的执行进度; EASA 2022-0185 的完整文本; 后续是否有第三道 AD。

### 编码与门的账

编码区 1437 字符(不含换行); 编码区锚 5 处(候选池 5 条按标签 A 2/B 3, 工具侧逐字校验 ok=5 bad=0); 扁平契约 25 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 6 行再复测。