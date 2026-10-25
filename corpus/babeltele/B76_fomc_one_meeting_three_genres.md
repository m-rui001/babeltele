# B76 同一次会议的三份体裁: FOMC 2025-09——纪要逐字抄声明 10 句而 SEP 与两者共享 0 句; 异议者三级记账(声明一票⇎纪要一段⇎SEP 无名); 不确定性语言 46 处集中在预测摘要
src: corpus/raw/fomc/fomc25sep_a.txt (2745 字符) ⇎ corpus/raw/fomc/fomc25sep_b.txt (12292 字符) ⇎ corpus/raw/fomc/fomc25sep_c.txt (31698 字符) (三份同为 federalreserve.gov 的 FOMC 2025-09 文书折平面: 声明⇎纪要⇎经济预测摘要; 数字一律从面内现读, 一个都不手填; 抓取时刻与 LII 现行版本只在本机或站外成立, 不进门槛)
; tags: 纪要抄声明键(the dissent⇎the majority) 判例名词频四声音 主题主语分档(congress峰⇎constitution峰) 句集交集镜像键(syllabus只摘胜方) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/fomc/fomc25sep_a.txt

In support of its goals and in light of the shift in the balance of risks, the Committee decided t

### ⟦B⟧ ⟸ corpus/raw/fomc/fomc25sep_b.txt

In support of its goals and in light of the shift in the balance of risks, the Committee decided t

### ⟦C⟧ ⟸ corpus/raw/fomc/fomc25sep_c.txt

a path for the federal funds rate and its longer-run value—and assumptions about other factors likely to aﬀect economic outcomes.

## ⟪BabelTele⟫
🧭 同一次 FOMC 会议(2025-09-16/17)剥成三份体裁, 同为 Fed 折平面: 即日声明 2745 字符⇎三周后纪要 12292⇎同步发布的经济预测摘要(SEP) 31698 ⇎ 句 18⇎69⇎137 句, 每句均值 152⇎178⇎231 字符——声明是最短的公共文本, SEP 是最长的数据文本。🔁 纪要逐字抄声明: 句集交集 A⇎B 10 句 ⇎ A⇎C 0 句 ⇎ B⇎C 0 句——纪要的"本会决定"整段是声明的复写, 而 SEP 与两者共享 0 句: 声明与纪要是同一决定的两遍措辞, SEP 是另一路(数据)。⚖ 异议者的两级记账: Miran 1⇎4⇎0 处——声明里只记一票(voted 词族 2⇎8⇎0 处), 纪要里展开: 他主张更大幅度降息并被否; SEP 里这个名字不存在。同一枚异议, 决定文本一行, 审议文本一段, 预测文本 0。🏛 词汇即体裁: participants 0⇎0⇎80 处、median 0⇎0⇎23 处、projection 0⇎0⇎123 处全是 SEP 的词汇(median 句 ⟦C⟧⟨a path for the federal funds rate and its longer-run value⟩); uncertainty 词根 1⇎1⇎46——不确定性语言 46 处集中在 SEP 的表格说明里, 声明与纪要各只 1 处; "balance of risks" 2⇎2⇎0 处是声明⇎纪要共享短语(声明 ⟦A⟧⟨the balance of risks⟩), SEP 0 处; 各有一份独有词: 纪要独有 October 0⇎2⇎0 处(下次会议时点的讨论), 声明独有 Powell 署名 1⇎2⇎0 处。ℒ 方法 ⇒ 同一决定的三份文书, 隐性知识在体裁分工: 句集交集(纪要抄声明 10 句, SEP 与谁都不交)‖人名三级记账(异议者 1⇎4⇎0)‖专属词汇(participants/median/projection 全在 SEP, October 只在纪要)‖共享短语(balance of risks 2⇎2⇎0)。每键都是 count 可机检量, 零项照占键位。

## ⛓解读注

### 第四遍复测(本注现算, 第三套实现: finditer 句标偏移切片 + findall 计数)

| 量 | 结果 | 与契约 |
|---|---|---|
| 句数/字符 | [18, 69, 137] / [2745, 12292, 31698] | 逐份相等 |
| participants(SEP 专属) | [0, 0, 80] | 逐份相等 |
| Miran 三级记账 | [1, 4, 0] | 逐份相等 |
| uncertainty | [1, 1, 46] | 逐份相等 |
| balance of risks 共享短语 | [2, 2, 0] | 逐份相等 |
| 纪要抄声明句集交集 | 10 句 | 相等 |

上表 6 行全部 assert, 不符即停机。

### 读法

一、同一枚降息决定(25bp 至 4-4.25%), 三份文本三种认识状态: 声明是决定的公共文本(2745 字符), 纪要是审议的复写+展开(它逐字抄声明 10 句), SEP 是另一路数据(与两者句集交集 0)。
二、异议者三级记账: Miran 1/4/0——声明一票, 纪要展开(他主张 50bp 被否), SEP 无名; 同一枚异议在不同体裁里的存在感是可控的。
三、词汇即体裁: participants/median/projection 全是 SEP 的(80/23/123), October 只在纪要(2), Powell 署名只在声明(1); 不确定性语言 46 处集中在 SEP。

### 本条不能由在库文件判定的(只登记, 不进门槛)

抓取时刻与 Fed 现行版本; 纪要被删节的审议细节(纪要本身是摘要); SEP 表格里每位参与者的点估计(只入中位数); 下次会议的实际决定。

### 编码与门的账

编码区 933 字符(不含换行); 编码区锚 2 处(候选池 3 条按标签 A 2/C 1, 工具侧逐字校验 ok=3 bad=0); 扁平契约 19 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 6 行再复测。