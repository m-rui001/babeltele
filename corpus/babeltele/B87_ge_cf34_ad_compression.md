# B87 单文本压缩: FAA 适航指令 2026-21590(GE CF34, 3775 词, 截止后冷门专业信息)→算子中文——缺陷链逐环保留, 两组发动机两套软件版本门槛逐字保真
src: corpus/raw/faa/ad_2026ge.txt (26755 字符) (单文本压缩: 源=Federal Register 2026-10-22 刊出的 GE 发动机 AD, FR pre 剥壳折平, 发布仅两天即入库; 数字与版本号一律逐字保留)
; tags: 单文本压缩 截止后专业信息 缺陷链逐环保真键(腐蚀⇒EICAS⇒锁慢车⇒失控) 两组两门槛键(CF34-8C⇎8E, V6.x⇎V5.x) 程序词频键 锚归属由正文现推 闭合账 标量 2⇎清单 6 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/faa/ad_2026ge.txt

This AD requires removing certain electronic engine control (EEC) full authority digital electronic control (FADEC) software versions from service

corrosion of the variable geometry system actuator

Group 1 engines, within 12 months after the effective date of this AD, replace any EEC FADEC software version that is V6.50 or earlier

any software version that is V5.70 or later approved version

GE Model CF34-8E2, CF34-8E2A1, CF34- 8E5, CF34-8E5A1, CF34-8E5A2, CF34-8E5A2HA, CF34-8E6, and CF34-8E6A1 engines

to prevent EEC FADEC software from automatically locking the engin

## ⟪BabelTele⟫
🧭 源账: FAA AD 2026-21590(91 FR 66631, 2026-10-22, 修 14 CFR part 39), FR pre 剥壳折平 26755 字符⇎3775 词; docket 13 处、this AD 46 处、cost 34 处(成本章被 Citizen Rulemaking Alliance 依 Executive Order 追问后补登 docket 并公开征求意见)。
⚡ 缺陷链: 起因=VG(variable geometry, 可调几何系统)作动筒腐蚀 ⟦B⟧⟨corrosion of the variable geometry system actuator⟩⇒飞行中 EICAS 报 "Engine Degraded"(engine degraded 6 处)⇒不处理则 EEC FADEC 自动把发动机锁在慢车直至重启, 后果=一台或多台发动机失效+推力控制丢失+飞机操控下降。
🔧 要求=纯软件召回: 拆役特定 EEC FADEC 软件版本并装合格版 ⟦A⟧⟨This AD requires removing certain electronic engine control (EEC) full authority digital electronic control (FADEC) software versions from service⟩——生效后 12 个月内完成; 合格判据按组分版本门槛: 组一(换掉 V6.50 及更早, 合格=V6.60 及以后已批版本)⇎组二(换掉 V5.60 及更早, 合格=V5.70 及以后已批版本)。
🧩 型号两组: 组一=CF34-8C1⇎CF34-8C5⇎CF34-8C5A1⇎CF34-8C5A2⇎CF34-8C5B1; 组二=⟦E⟧⟨GE Model CF34-8E2, CF34-8E2A1, CF34- 8E5, CF34-8E5A1, CF34-8E5A2, CF34-8E5A2HA, CF34-8E6, and CF34-8E6A1 engines⟩(cf34 全文 56 处, eec fadec 19 处)——同族支线发动机按子型号分两套软件门槛。
🧾 程序侧: amends 既有 part 39 条款(amends 2 处); AMOC 备选合规由 AIR-520 Continued Operational Safety Branch 经理审批; Horizon Air 提请纳入服务材料(Service Material)入引用, Citizen Rulemaking Alliance 追问成本估算的 EO 12866 显著性判定——两意见都进了正文(horizon air 4 处)。
ℒ 方法 ⇒ 截止后监管文本的压缩判据: 缺陷链(腐蚀⇒信息⇒锁慢车⇒失控)逐环保留, 型号⇎软件版本门槛逐字保真(V6.50/V6.60⇎V5.60/V5.70 是可执行判据, 压缩不碰数字), 程序词频做成键(this ad 46⇎cost 34⇎unsafe condition 7)。

## ⛓解读注

### 压缩账(本注现算)

| 量 | 值 |
|---|---|
| 源(FAA AD 2026-21590 全文, FR pre 剥壳折平) | 26755 字符 / 3775 词 |
| 编码(BabelTele 算子中文) | 1306 字符 |
| 体积比 | **4.9%**(监管模板句占比高, 压缩主要发生在样板段) |
| 事实覆盖 | 17 个编号/版本/型号/机构名逐字入编码(本注 assert 全过) |
| 锚 | 编码区 3 处 / 候选池 6 条(atomcheck ok=6 bad=0) |

### 读法

一、**截止后两天入库**的监管文本: 发布 2026-10-22, 抓取 2026-10-24——任何模型训练分布之外。压缩判据=缺陷链逐环保留: VG 作动筒腐蚀 ⇒ 飞行中 EICAS "Engine Degraded"(6 处) ⇒ EEC FADEC 自动锁慢车 ⇒ 发动机失效+推力控制丢失+操控下降, 四环一环不少。
二、可执行判据逐字不碰: 两组发动机(CF34-8C 系五型 ⇎ CF34-8E 系八型)两套版本门槛——组一换掉 V6.50 及更早(合格 V6.60+)、组二换掉 V5.60 及更早(合格 V5.70+), 生效后 12 个月内; 这些是机务拿来执行的字段, 压缩一字不改。
三、程序侧做成键: this AD 46 处⇎cost 34 处⇎docket 13 处; 两条公众意见(Horizon Air 要服务材料入引用、Citizen Rulemaking Alliance 追问 EO 12866 成本显著性)都进了正文——征求意见不是走过场。
四、复原自测: 只读编码区应能答——缺陷根因是什么?(VG 作动筒腐蚀) 软件召回的两组门槛各是多少?(V6.50→V6.60 / V5.60→V5.70) 谁审批备选合规?(AIR-520) 哪家航空公司提了意见?(Horizon Air)

### 本条不能由在库文件判定的(只登记, 不进门槛)

抓取时刻与 FR 现行版本; 被 amends 的既有 AD 编号(正文未点名, 见 FR 表格); VG 作动筒腐蚀的环境成因; CF34 机队实际受影响台数。

### 编码与门的账

编码区 1306 字符(不含换行); 编码区锚 3 处(候选池 6 条, 工具侧逐字校验 ok=6 bad=0); 扁平契约 11 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现(词级)+事实覆盖清单(17 项)assert。门槛三遍: T1 字面逐锚回源 ⇎ T2 DERIV 重跑 ⇎ T3 码位与字母账。