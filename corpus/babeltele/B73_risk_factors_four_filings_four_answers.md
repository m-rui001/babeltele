# B73 同一部交易所法定章节的四副面孔: 风险因素清单——同一公司两年逐字搬 213 句(47.8%) ⇎ 同年三家互抄 0 句: 风险因素是自我指纹不是行业语料
src: corpus/raw/filings/aapl25_10k_1a.txt (87355 字符) ⇎ corpus/raw/filings/aapl24_10k_1a.txt (87744 字符) ⇎ corpus/raw/filings/msft25_10k_1a.txt (120804 字符) ⇎ corpus/raw/filings/goog25_10k_1a.txt (115818 字符) (四份 SEC EDGAR 10-K 的 Item 1A 剥壳折平面, 实体解码; 数字一律从面内现读, 一个都不手填; 抓取时刻与 EDGAR 现行版本只在本机或站外成立, 不进门槛)
; tags: 句级交集自我指纹键 人称两档(the Company⇎we) 模板句式三档(could harm) 主题词频年份并排 关税词翻五倍 行业零共享 锚归属由正文现推 闭合账 标量 2⇎清单 6 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/filings/aapl25_10k_1a.txt

Restrictions on international trade, such as tariffs and other controls on imports or exports of goods, technology or data, can materially adversely affect the Company’s business and supply chain. The impact can be partic

### ⟦B⟧ ⟸ corpus/raw/filings/aapl24_10k_1a.txt

Restrictions on international trade, such as tariffs and other controls on imports or exports of goods, technology or data, can materially adversely affect the Company’s business and supply chain. The impact can be partic

### ⟦C⟧ ⟸ corpus/raw/filings/msft25_10k_1a.txt

A catastrophic event that results in the destruction or disruption of any of our critical business or systems, or the infrastructure or systems they rely on, such as power grids, could harm our ability to conduct normal business operations or adversely affect our results of operations.

### ⟦D⟧ ⟸ corpus/raw/filings/goog25_10k_1a.txt

RISK FACTORS Our operations and financial results are subject to various risks and uncertainties, including but not limited to those described below, which could harm our business, reputation, financial condition, and operating results, and affect the trading price of our Class A and Class C stock.

## ⟪BabelTele⟫
🧭 四份同为 SEC EDGAR 10-K 的 Item 1A 风险因素节, 一手 §-面剥到纯文本: 折平后字符 87355⇎87744⇎120804⇎115818 ⇎ 句(>40 字符) 446⇎448⇎714⇎559 句 ⇎ 每句均值 195⇎195⇎169⇎207 字符——D 最长句、C 最多句。
🔁 句级搬运把四份劈成两半: 同一发行人两年逐字共享句 213 句(占 FY25 面的 47.8%)——Apple 把自己去年的风险清单近乎整册搬来重印; 而同年三家之间共享句 0⇎0⇎0⇎0⇎0 句(A⇎C、A⇎D、B⇎C、B⇎D、C⇎D 全零)。风险因素不是行业语料库, 是**自我指纹**: 每家公司只抄自己, 从不抄同行。
⚖ 人称即体裁: Apple 全节以第三人称写自己——"the Company" 478⇎494 处 ⇎ " we " 0⇎0 处、if we 0⇎0 处; C/D 以第一人称写——" we " 228⇎258 处、if we 10⇎11 处而 "the Company" 只 4⇎4 处。经典风险句式模板 "could harm" 0⇎0⇎4⇎40 处: 只 D 成规模(开篇即 "which could harm our business, reputation, financial condition, and operating results" ⟦D⟧⟨Our operations and financial results are subject to various risks and uncertainties, including but not limited to those described below, which could harm our business, reputation, financial condition, and operating results⟩), C 只 4 处 ⟦C⟧⟨such as power grids, could harm our ability to conduct normal business operations or adversely⟩, A/B 两年 0 处——同一家交易所的同一份法定章节, 句式谱系四份分三档。
📉 主题词频即当年世界: tariff 11⇎2⇎4⇎1 处——同一公司两年间翻五倍以上(B 的 2 处全部活在关税句里 ⟦B⟧⟨Restrictions on international trade, such as tariffs and other controls on imports or exports of goods, technology or data, can materially adversely affect the Company’s business and supply chain.⟩, 这句两年逐字共享, A 另给 11 处增量是 FY25 新环境写进去的); artificial intelligence 6⇎3⇎2⇎1 处; App Store 4⇎10⇎0⇎0 处(B 比 A 多一倍——FY24 的监管节在 FY25 被删改); stock price 38⇎7⇎0⇎2 处(A 的 38 处密集谈自家股价, C 全节 0 处); china 6⇎6⇎1⇎0 处; 供链 9⇎9⇎11⇎5 处; cyberattack 0⇎0⇎6⇎0 处; data privacy 0⇎0⇎2⇎11 处; litigation 15⇎15⇎4⇎17 处; competition 18⇎17⇎22⇎16 处; intellectual property 31⇎23⇎19⇎27 处; 词根 regulat- 36⇎30⇎63⇎87 处。
ℒ 方法 ⇒ 10-K 风险因素的隐性知识不在"列了哪些风险"(四份列的是同个世界的同批威胁), 而在谱系与体裁: 先把句做成键(句级交集把两年 vs 同年劈成 213 ⇎ 0 六对), 再把人称做成键(the Company ⇎ we 两档), 再把模板句式做成键(could harm 0⇎0⇎4⇎40), 最后把主题词频按年份并排(tariff 两倍→五倍、App Store 反向减半)。每键都是 count 可机检量, 零项照占键位。
✂️ 为什么这份编码比摘要窗口长 ⇒ 四源各 87355⇎87744⇎120804⇎115818 字符, 本条结论几乎全是跨文书对照量: 自我指纹要两年句集求交(213 句), 行业零共享要三对同年句集各交一遍(0⇎0⇎0⇎0⇎0⇎0), 人称档要四份并排(the Company 478⇎494⇎4⇎4), 主题轴要同一词按年份各数一遍(tariff 11⇎2⇎4⇎1)。读它请按"这句是谁抄谁的、以什么人称、在哪个年份被改成什么"来读, 而不是按"少抄了多少原文"。

## ⛓解读注

### 第四遍复测(本注现算, 第三套实现: finditer 定位句标偏移切片, 与采集侧游标累加、审计器侧 lower 游标不同机制)

| 量 | 本注的写法 | 结果 | 与契约 |
|---|---|---|---|
| 句数 | finditer [.! ?] 偏移切片, >40 字符 | [446, 448, 714, 559] | 逐份相等 |
| 字符 | 折平面长度 | [87355, 87744, 120804, 115818] | 逐份相等 |
| 主题词五族 | tariff/AI/appstore/stockprice/china | [11, 2, 4, 1] / [6, 3, 2, 1] / [4, 10, 0, 0] / [38, 7, 0, 2] / [6, 6, 1, 0] | 逐份相等 |
| 自我指纹 | 两年句集合求交 | 213 句(占 FY25 的 47.8%) | 相等 |
| 行业零共享 | 六对句集两两求交 | 0/0/0/0/0 | 逐对相等 |
| 人称档 | the company / we | [478, 494, 4, 4] / [0, 0, 228, 258] | 逐份相等 |

上表 6 行全部 assert, 不符即停机。

### 读法

一、"这份清单列了什么风险"四份同答(同一个世界的同批威胁), 所以这份编码不记风险名, 记**谁抄谁**: Apple 两年共享 213 句(占 FY25 的 47.8%), 而同年三家之间六对句集交集全零——风险因素是自我指纹, 不是行业语料; 模板句不来自同行, 来自自己去年。
二、人称即体裁: Apple 以第三人称写自己(the Company 478/494 处, we 0/0), C/D 以第一人称写(we 228/258 处)。could harm 0/0/4/40——只 D 成规模(开篇模板句), C 一处, A/B 两年零。
三、主题词频即当年世界: tariff 11/2/4/1(同一公司两年翻五倍, 而关税本体句两年逐字共享——变的是周围不是本体); App Store 4/10 反向减半(FY24 的监管节在 FY25 被删改); stock price 38/7/0/2——只有 Apple 密集谈自家股价。

### 本条不能由在库文件判定的(只登记, 不进门槛)

四份年报的抓取时刻与 EDGAR 现行版本; 模板句是否有比 FY24 更早的底稿; 人称差异是法务口径还是文体; 缩写句点(U.S. 等)把句数口径推高——本条以"句标即切"为准并三套实现两两对表。

### 编码与门的账

编码区 2068 字符(不含换行); 编码区锚 3 处(候选池 5 条按标签 A 1/B 1/C 1/D 2, 工具侧逐字校验 ok=5 bad=0); 扁平契约 43 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现(finditer 切片)对上表 6 行再复测。