# B83 同一天的三份 NWS 预报讨论: 休斯敦两期七小时滚存 24/28 句而跨办公室交集 0——骨架全国统一(KEY MESSAGES/&&/AVIATION 三份全等), 文化办公室私有(confidence 只斯波坎)
src: corpus/raw/nws/afd_a.txt (3464 字符) ⇎ corpus/raw/nws/afd_b.txt (3367 字符) ⇎ corpus/raw/nws/afd_c.txt (4748 字符) (三份同为 api.weather.gov 的 Area Forecast Discussion 纯文本: KHGX 当期⇎KHGX 上期⇎KOTX 当期, 2026-10-23; 数字一律从面内现读, 一个都不手填; 抓取时刻与 NWS 现行产品只在本机或站外成立, 不进门槛)
; tags: 时间衰减键(同室滚存) 办公室文化键(confidence) 全国骨架键(KEY MESSAGES/&&/AVIATION 全等) 地理词键(gulf⇎front) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/nws/afd_a.txt

- Elevated fire weather conditions are possible over the next couple of days. - Potential change to a wetter pattern by the end of the month.

### ⟦B⟧ ⟸ corpus/raw/nws/afd_b.txt

- Elevated fire weather conditions are possible over the next couple of days. - Potential change to a wetter pattern by the end of the month.

### ⟦C⟧ ⟸ corpus/raw/nws/afd_c.txt

This is ushering drier air in to the region with moderate to high confidence for ongoing IFR/MVFR conditions to quickly lift between 12-14z in Washington and 14-16z in the Idaho Panhandle.

## ⟪BabelTele⟫
🧭 同一天(2026-10-23)的三份 NWS 区域预报讨论, 同为 api.weather.gov 纯文本: 休斯敦/加尔维斯顿当期(11:43Z) 3464 字符⇎同室上期(04:40Z) 3367⇎斯波坎当期(11:39Z) 4748 ⇎ 句 29⇎28⇎36 句。🔁 时间衰减: 同室相隔七小时的两期句集交集 24 句(去重句各 29⇎28)——上期的大部分句子逐字滚入当期, 逐段更新而非重写; 而跨办公室交集 A⇎C 0 句、B⇎C 0 句全零: 预报讨论的模板是办公室私产, 全国共享的只有骨架。⚖ 骨架是全国统一件: KEY MESSAGES 1⇎1⇎1 份、段分隔 && 6⇎6⇎6 枚、AVIATION 节 3⇎3⇎3 处、National Weather Service 1⇎1⇎1 处、Area Forecast Discussion 抬头 1⇎1⇎1 处——三份同构; 火情词 fire 2⇎2⇎2 处(休斯敦的干旱火险与斯波坎的火天气各自开场 ⟦A⟧⟨Elevated fire weather conditions are possible over the next couple of days.⟩)。🏛 文化即办公室: confidence 0⇎0⇎5 处只斯波坎成规模——它把确定性写进每个时段 ⟦C⟧⟨This is ushering drier air in to the region with moderate to high confidence for ongoing IFR/MVFR conditions⟩; front 0⇎0⇎3 处、short term 节 0⇎0⇎1 处、advisory 0⇎0⇎2 处、ensemble 0⇎0⇎2、model 0⇎0⇎1 处全是内陆平原办公室的词; 休斯敦的墨西哥湾词 gulf 2⇎2⇎1、coast 2⇎2⇎3——地理写进讨论, 不用看署名就知道是哪个办公室写的。ℒ 方法 ⇒ 预报讨论的隐性知识在三层分家: 时间衰减做成键(同室两期 24 句复用), 办公室文化做成键(confidence 0⇎0⇎5), 全国骨架做成键(KEY MESSAGES 1 份、&& 6 枚、AVIATION 3 处三份全等)。每键都是 count 可机检量, 零项照占键位。

## ⛓解读注

### 第四遍复测(本注现算, 第三套实现: finditer 句标偏移切片 + findall 计数)

| 量 | 结果 | 与契约 |
|---|---|---|
| 句数/字符 | [29, 28, 36] / [3464, 3367, 4748] | 逐份相等 |
| KEY MESSAGES / && / AVIATION(全国骨架) | [1, 1, 1] / [6, 6, 6] / [3, 3, 3] | 逐份相等 |
| confidence(办公室文化) | [0, 0, 5] | 逐份相等 |
| fire | [2, 2, 2] | 逐份相等 |
| 句集交集 AB/AC/BC | 24/0/0 | 相等 |

上表 5 行全部 assert, 不符即停机。

### 读法

一、时间衰减: 休斯敦两期相隔七小时, 句集交集 24 句(上期 28 句去重句的大半滚入当期)——预报讨论逐段更新而非重写; 跨办公室交集 0/0——模板是办公室私产。
二、骨架全国统一: KEY MESSAGES 三份各 1 份、&& 段分隔各 6 枚、AVIATION 各 3 处、Area Forecast Discussion 抬头各 1 处——NWS 的产品规范把结构钉死, 内容各自生长。
三、文化即办公室: confidence 只斯波坎成规模(0/0/5 处), 它把确定性写进每个时段(moderate to high confidence for ongoing IFR/MVFR conditions); front/short term/advisory/ensemble 也全是内陆平原办公室的词; 休斯敦的 gulf/coast 把墨西哥湾写进讨论——不用看署名就知道是谁写的。
四、火情同词不同义: fire [2, 2, 2] 处三份都有——休斯敦说干旱火险(elevated fire weather), 斯波坎说火天气——同一词在不同地理里指不同的天气。

### 本条不能由在库文件判定的(只登记, 不进门槛)

抓取时刻与 NWS 现行产品; 两期之间的预报验证评分; confidence 词表是否为该 WFO 的本地惯例; 产品在 NWS 站点上的渲染是否与 api.weather.gov 文本一致。

### 编码与门的账

编码区 982 字符(不含换行); 编码区锚 2 处(候选池 5 条按标签 A 3/C 2, 工具侧逐字校验 ok=5 bad=0); 扁平契约 13 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 5 行再复测。