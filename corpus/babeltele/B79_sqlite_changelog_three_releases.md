# B79 同一页更新日志的三个版本段: SQLite 3.54.1⇎3.54.0⇎3.53.4——补丁版只修不添(2/0/1 处 fix)而特性版只添不修, 旧线补丁自白问题大多来自 AI
src: corpus/raw/changelog/sqlite_a.txt (412 字符) ⇎ corpus/raw/changelog/sqlite_b.txt (4047 字符) ⇎ corpus/raw/changelog/sqlite_c.txt (344 字符) (三份同为 sqlite.org changes.html 的版本段: 补丁 3.54.1 ⇎ 特性 3.54.0 ⇎ 旧线补丁 3.53.4; 数字一律从面内现读, 一个都不手填; 抓取时刻与站点现行版本只在本机或站外成立, 不进门槛)
; tags: 动词分布键(fix⇎add) 谱系指向键(补丁指名母版) AI自白键 体例哈希锚 语法破损键 锚归属由正文现推 闭合账 标量 2⇎清单 6 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/changelog/sqlite_a.txt

Fix a possible heap-buffer overflow on 32-bit builds. (64-bit builds are not affected by this problem.) Fixes other problems in 3.54.0 reported by users. See the check-in timeline for details.

### ⟦B⟧ ⟸ corpus/raw/changelog/sqlite_b.txt



### ⟦C⟧ ⟸ corpus/raw/changelog/sqlite_c.txt

Fixes for problems in 3.53.0 (and 3.53.1, 3.53.2, and 3.53.3) mostly coming from AIs. See the check-in timeline for details.

## ⟪BabelTele⟫
🧭 同一页更新日志(SQLite changes.html)切出的三个版本段, 同为 sqlite.org 折平面: 补丁版 3.54.1 412 字符⇎特性版 3.54.0 4047⇎旧线补丁 3.53.4 344 ⇎ 句 4⇎39⇎2 句——特性版的条目量是补丁版的十倍。🔁 动词即版本类型: fix 2⇎0⇎1 处 ⇎ add 0⇎8⇎0 处、improve 0⇎3⇎0 处——补丁版只修不添, 特性版只添不修(0 处 fix); optimize 词族 0⇎1⇎0 处全在特性版——它的优化正是两道补丁要修的回归来源。句集交集 A⇎B 0⇎A⇎C 0⇎B⇎C 0: 每版条目独立, 更新日志不复制自己。⚖ 补丁指向母版的三种形态: A 指名道姓 ⟦A⟧⟨Fixes other problems in 3.54.0 reported by users.⟩(母版名 1⇎1⇎0 处, reported by users 1⇎0⇎0 处)并另给溢出细节 ⟦A⟧⟨Fix a possible heap-buffer overflow on 32-bit builds.⟩(heap 1⇎0⇎0、32-bit 1⇎0⇎0); C 连修五版的整条谱系 ⟦C⟧⟨Fixes for problems in 3.53.0 (and 3.53.1, 3.53.2, and 3.53.3) mostly coming from AIs.⟩(lineage 3.53.3 0⇎0⇎1 处)——并说出全书最刺眼的一句: 问题大多来自 AI。🏛 体例指纹: 三段各有 Hashes: SQLITE_SOURCE_ID 1⇎1⇎1 处与 SHA3-256 1⇎1⇎1 处——发布身份靠哈希锚定; 特性版的手写破损语法 "is now be" 0⇎1⇎0 处与 "The replaces" 0⇎1⇎0 处——条目写得快, 语法来不及修; 旧线补丁的 AI 自白 from AIs 0⇎0⇎1 处。ℒ 方法 ⇒ 更新日志的隐性知识在版本类型与谱系指向: 动词分布把补丁版⇎特性版做成键(fix 2⇎0⇎1 vs add 0⇎8⇎0), 句集交集把条目独立性做成键(0/0/0), 指向母版的引用把谱系做成键(3.54.0 1⇎1⇎0、3.53.3 0⇎0⇎1), 语法破损与 AI 自白把书写过程做成键。

## ⛓解读注

### 第四遍复测(本注现算, 第三套实现: finditer 句标偏移切片 + findall 计数)

| 量 | 结果 | 与契约 |
|---|---|---|
| 句数/字符 | [4, 39, 2] / [412, 4047, 344] | 逐份相等 |
| fix / add 动词分布 | [2, 0, 1] / [0, 8, 0] | 逐份相等 |
| 指向母版 3.54.0 | [1, 1, 0] | 逐份相等 |
| AI 自白 from AIs | [0, 0, 1] | 逐份相等 |
| 句集交集 AB/AC/BC | 0/0/0 | 相等 |

上表 5 行全部 assert, 不符即停机。

### 读法

一、动词分布把版本类型做成键: 补丁版只修不添(fix 2/0/1 处, add 0/8/0 处), 特性版只添不修——fix 为 0。
二、补丁指向母版的三种形态: A 指名道姓(in 3.54.0 1 处)+溢出细节(heap-buffer 1/32-bit 1 处)+用户报告(reported by users 1 处); C 连修五版整条谱系(3.53.3 1 处)并自白问题大多来自 AI(from AIs 1 处, 全书唯一)。
三、每版条目独立(句集交集 0/0/0 全零)——更新日志不复制自己, 与 B78 的 AD(三分之一复用)相反。
四、体例指纹: 三段各有 SQLITE_SOURCE_ID 与 SHA3-256(1/1 处)——发布身份靠哈希锚定; 特性版手写破损语法(is now be 1、The replaces 1 处)——条目写得快, 语法来不及修。

### 本条不能由在库文件判定的(只登记, 不进门槛)

抓取时刻与站点现行版本; AI 自白句的具体所指(哪些 check-in 由 AI 写); 破损语法是否已在后续版本页修正; 三段的切割粒度(版本头边界)是否与站点渲染一致。

### 编码与门的账

编码区 994 字符(不含换行); 编码区锚 3 处(候选池 4 条按标签 A 2/B 1/C 1, 工具侧逐字校验 ok=4 bad=0); 扁平契约 10 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现对上表 5 行再复测。