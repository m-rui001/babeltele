# B55 一张子标签注册表 ⇎ 一张把它的码当国家列的时区表：29 枚越界值在两种判法下是 29 个也是 0 个
src: corpus/raw/langsubtag.txt (731819 字节／非空行 49316／'<' 0 枚／制表符 0 枚) ⇎ corpus/raw/tz/zone1970.tab (17592 字节／非空行 375／'<' 3 枚／制表符 833 枚) (两份没有共同的版本日期: 注册表把 File-Date 写成 2026-09-17 一行, 时区表把出处写成 From Paul Eggert (2025-05-15) 一条注释; 磁盘 mtime 与这两个日期谁新谁旧只在本机成立, 不进门槛)
；联结不是“同一份数据的两种序列化”, 而是一张表 ⇎ 一张借它的码当列值的表: 注册表 731819 字节／9297 段, 每段以一行两个 % 字符分隔, 四个交叉引用字段规定的值域在两种判法下给出 29 ⇎ 0 个越界值(越界的全是含连字符的复合标签, 共 29 枚); 时区表 17592 字节／312 数据行, 国家列的 247 枚两位码全部落在注册表 region 型的 305 枚里(反向缺 58 枚, 其中 33 枚本来就是数字码与区间), 而它注释自写的三条规则里, 第 4 列的充要条件核对到 312／312 行, 排序声明在整列口径下 21 行不守 ⇎ 去掉每行首国的口径下 1 行不守
tags: 段表与分隔符 字段逐行⇎折叠两口径 交叉引用值域矩阵 整码判⇎拆片判 值域宽度不对称 子标签长度签名 私用区间码 跨文件双向差集 region 数字码 ISO6709 坐标位数分档 第 4 列充要条件核对 排序声明两种口径核对 制表符可由列结构推得 Description 多行与复用 日期账与反向时序 归一锚假同现须逐字复查 锚归属由正文现推
## [[原始语料|ORIGINAL]]
### ⟦R⟧ ⟸ corpus/raw/langsubtag.txt

File-Date: 2026-09-17 %% Type: language Subtag: aa Description: Afar Added: 2005-10-16 %% Type: language Subtag

Suppress-Script: Latn %% Type: language Subtag

Description: Spanish Description: Casti

Deprecated: 1989-01-01 Preferred-Value: id Supp

Atlantic-Congo languages Added: 2

Macrolanguage: zh %% Type: language Subtag

Subtag: qaa..qtz Description: Private use Added: 2005-10-16 Scope:

Subtag: Qaaa..Qabx Description: Private use

Antarctica Added: 2005-10-16 %% Typ

Comments: as of 2006-03-29 GB no longer includes the Channel Islands and Isle of Man; see GG, JE,

Subtag: QM..QZ Description: Private use

Subtag: XA..XZ Description: Private use

Comments: Does not include Caribbean (029) or Central America (013); see also 003 %% Type: region

Comments: Indicates that the content is transcribed according to X-SAMPA %% Type: variant Subtag:

Prefix: oc-aranes Prefix: oc-auvern Prefix

Prefix: en-CA %% Type: variant Subtag:

Type: redundant Tag: az-Arab Description

Preferred-Value: cmn-Hans %% Type: redundant Tag:

### ⟦Z⟧ ⟸ corpus/raw/tz/zone1970.tab

tzdb timezone descriptions # # This file is in the public domain. # # From Paul Eggert (20

either ±DDMM±DDDMM or ±DDMMSS±DDDMMSS, # first latitude (+ is

# 4. Comments; present if and only if countries have multiple timezones, # and useful only for t

are listed alphabetically by country code. The table is sorted # first by country code,

Antarctica/Casey Casey AQ -6835+077

Atlantic/Bermuda BO -1630-06809 A

PR,AG,CA,AI,AW,BL,BQ,CW,DM,GD,GP,KN,LC,MF,MS,SX,TT,VC,VG,VI +182806-0660622 America/Puerto_Rico AST - QC (Lower North Sh

Mention RU and UA alphabetically. See “territorial claims” above. RU,UA +4457+03406 Europe

# # For example, the comment ‘#@AQ<tab>Antarctica/’ means the country code # AQ is in the continent

## ⟪BabelTele⟫
🧭 两份文件靠同一批 ISO 3166 两位码相接: ⟦R⟧⟨File-Date: 2026-09-17⟩ 是注册表的第一行, ⟦Z⟧⟨# tzdb timezone descriptions⟩ 是时区表注释的第一行。R 731819 字节／49316 换行／'<' 0 枚／制表符 0 枚 ⇎ Z 17592 字节／375 换行／'<' 3 枚／制表符 833 枚(字节比 42 倍, 差 713541 字符)。注册表一个制表符也没有, 时区表那 3 枚 '<' 全住在注释写的 '…<tab>…' 记法里(⟦Z⟧⟨# For example, the comment ‘#@AQ<tab>Antarctica/’ means the country code⟩), 数据行一枚不落。两份都不是纯 ASCII(非 ASCII 723 ⇎ 38 枚), 所以字符数=字节数在 0 份上成立; '#' 开头的行 R 0 ⇎ Z 63——R 没有注释语法, 9297 段全算数据。两份的 sha16 是 2 个不同的串(串本身只进解读注)。
📏 记录结构: 分隔行(整行只有两个 % 字符)出现 9296 次, 切出 9297 段——段数恰比分隔符多 1(差 0 段: 文件既不以分隔符开头也不以它结尾)。9203 段带 Subtag ⇎ 94 段不带; 后者 = 93 段用 Tag(26 段 grandfathered ⇎ 67 段 redundant)加 ⟦R⟧⟨File-Date: 2026-09-17⟩ 那 1 段, 三档相加校住 9297(差 0)。字段名 13 种; 逐行数 '名:' 得 39938 处 ⇎ 每段同名只留一格的折叠口径 39333 格, 差 605 处, 其中 0 处不在 Description ⇎ Prefix ⇎ Comments 三名之内(即除这三名以外没有字段在同段出现两次)。同段多行不是罕见: Prefix 在 17 段里出现第二条以上, 单段最多 11 行(⟦R⟧⟨Prefix: oc-aranes⟩), Description 单段最多 7 行。Type 有 8 种取值(含 1 种空值, 属 ⟦R⟧⟨File-Date: 2026-09-17⟩ 那段): language 8276 ⇎ region 305 ⇎ script 225 ⇎ variant 139 ⇎ extlang 258 ⇎ grandfathered 26 ⇎ redundant 67(⟦R⟧⟨Type: redundant⟩)。
🔤 子标签的长度就是类型签名: 8 种长度——462 枚 2 字符 ⇎ 8374 枚 3 字符 ⇎ 227 枚 4 ⇎ 31 枚 5 ⇎ 29 枚 6 ⇎ 36 枚 7 ⇎ 43 枚 8 ⇎ 1 枚 10, 八档相加校住 9203(差 0)。切到类型内部: language 只有 2 ⇎ 3 ⇎ 8 三种长度(190 ⇎ 8085 ⇎ 1), region 2 ⇎ 3 ⇎ 6 三种(272 ⇎ 31 ⇎ 2), script 4 ⇎ 10 两种(224 ⇎ 1), variant 占 4 ⇎ 5 ⇎ 6 ⇎ 7 ⇎ 8 五种(3 ⇎ 31 ⇎ 27 ⇎ 36 ⇎ 42)。写成 '起..止' 的私用区间有 4 枚, 每一枚都是它类型里的最长值: ⟦R⟧⟨Subtag: qaa..qtz⟩(language 唯一 8 字符那枚) ⇎ ⟦R⟧⟨Subtag: Qaaa..Qabx⟩(script 唯一 10 字符那枚) ⇎ ⟦R⟧⟨Subtag: QM..QZ⟩ 与 ⟦R⟧⟨Subtag: XA..XZ⟩(region 仅有的两枚 6 字符), 而 region 的 3 字符档正是数字码 31 枚(⟦R⟧⟨Comments: Does not include Caribbean (029) or Central America (013); see⟩ 那行注释直接引它们)。
🧱 闭世界两种口径——本条的主轴: 四个交叉引用字段各规定一个值域。⟦R⟧⟨Suppress-Script: Latn⟩ 的值只能取 script 码(池 225 枚), ⟦R⟧⟨Macrolanguage: zh⟩ 只能取 language 码(池 8276 枚), ⟦R⟧⟨Preferred-Value: cmn-Hans⟩ 只能取已登记子标签(池 8945 枚), ⟦R⟧⟨Prefix: en-CA⟩ 取子标签或某个 Preferred-Value(池 8948 枚)。逐行取到 1546 个字段值(其中 Prefix 444 行 ⇎ 只按段折叠是 390 格), 于是有两种判法: 整码判(把整个值当一个码, 同一个值在几段里重复也只计一枚)越界 29 枚 ⇎ 拆片判(按 '-' 切开逐片判)越界 0 枚。两数之差不是抽样差异: 越界的 29 枚与含 '-' 的 29 枚同数(差 0), 也就是整码判报的每一例都是一个复合标签——Prefix 独占 26 枚(如 ⟦R⟧⟨Prefix: en-CA⟩), Preferred-Value 占 3 枚(如 ⟦R⟧⟨Preferred-Value: cmn-Hans⟩), 而 134 段 Script 引用 ⇎ 545 段 Macrolanguage 引用两口径都零越界(整码判零越界的 2 个 ⇎ 拆片判零越界的 4 个)。所以“这张表有没有越界值”取决于先问哪一种: 问“它是码吗”答有 29 个不是, 问“它的每一片都是码吗”答 0 个不是。
🧲 值域大小并不对称: script 码池 225 ⇎ language 码池 8276(差 8051 枚), 而子标签全集 8945 枚 = 七类里带 Subtag 的 9203 段去掉同码重复(258 枚, 同一码最多被 2 段共用)。Prefix 的值域要比子标签全集另加 3 枚——那 3 枚从未作为 Subtag 登记, 只作为 Preferred-Value 出现(⟦R⟧⟨Preferred-Value: cmn-Hans⟩), 于是 8948 = 8945 + 3(宽出 3 枚); 恰好 Preferred-Value 整码判的全部越界就是这 3 枚。同一个事实的两面: 注册表把复合码收进 Preferred-Value 的值域, 却没收进 Subtag 的登记表。
🖼 region 池 ⇎ 时区表的国家列: region 型子标签 305 枚 = 两位码 272 ⇎ 三位数字码 31 ⇎ 区间 2(相加校住 305, 差 0), 其中 3 枚以 X 或 Q 开头(私用与保留段: ⟦R⟧⟨Subtag: QM..QZ⟩ ⇎ ⟦R⟧⟨Subtag: XA..XZ⟩), 'ZZ' 在池里(1 枚)。时区表国家列去重得 247 枚, 与 region 交 247 枚 ⇎ 时区表有而注册表无 0 枚 ⇎ 注册表有而时区表无 58 枚; 那 58 枚拆开是两位码 25 ⇎ 三位码 31 ⇎ 区间 2(相加校住 58, 差 0)——数字码与区间本来就不可能是 ISO 3166 国家码, 于是“缺 58 枚”里只有 25 枚是真缺口。国家格总出现 423 次(一格一枚), 多国家行 34 行, 最多一行 20 国(⟦Z⟧⟨PR,AG,CA,AI,AW,BL,BQ,CW,DM,GD,GP,KN,LC,MF,MS,SX,TT,VC,VG,VI⟩); 国家列格式不符的 0 行。
📐 时区表把规则写在注释里, 再交给数据判: ⟦Z⟧⟨# 4.  Comments; present if and only if countries have multiple timezones,⟩ 说第 4 列“当且仅当”——按数据判“行内至少一枚码在他行也出现”的行 201 ⇎ 真带第 4 列的行 201, 多余 0 行 ⇎ 缺失 0 行, 相符 312/312 行(整条充要式在库内成立)。⟦Z⟧⟨# are listed alphabetically by country code.  The table is sorted⟩ 那半句管的是多国行: 人口最多的那国放在首位, “其余”才按国家码字母排——首国按人口挑, 不归字母管, 于是判法有两种: 整列按字母判 21 行不守 ⇎ 只判首国之外的 1 行不守; 注释承诺的是后一种, 所以前一种读法数出的 21 行是过度解读, 不是缺陷。整表另有“先按国家码排”, 按首码判逆序 0 处; 后一种读法上唯一的失守是 20 国那一行 ⟦Z⟧⟨America/Puerto_Rico⟩(首国之外 20 减 1 枚没排好)。坐标两档: ⟦Z⟧⟨#     either ±DDMM±DDDMM or ±DDMMSS±DDDMMSS,⟩ 写了两种写法, 数据里分钟级 265 行(纬度 4 位 ⇎ 经度 5 位) ⇎ 秒级 47 行(纬度 6 位 ⇎ 经度 7 位), 两档相加校住 312(差 0)。制表符也能推: 3 列 111 行 ×2 加 4 列 201 行 ×3 加那条列名注释行的 3 枚加 5 行 '#@' 各 1 枚 = 833 ⇎ 数出来 833, 差 0。
🧵 Description 也有两种口径: 逐行 9846 处／9413 个不同串／复用 433 次(只出现一次的 9007 条 ⇎ 出现两次以上的 406 条); 每段只留最后一条则 9296 格／8911 个不同／复用 385 次, 两口径的“不同串”差 502 条。同一记录可写多行说明: 473 段带第二条以上, 单段最多 7 行。复用最高的一组是 ⟦R⟧⟨Description: Private use⟩, 被 6 枚码共用; 名字本身在注册表与两源之外没有参照物, 所以只报数。Subtag 侧同样有重复: 9203 段 ⇎ 8945 个不同码(重复 258)——一个码两段的典型是 extlang 与 language 同名同形。Scope 只 4 种取值(collection 117 ⇎ macrolanguage 63 ⇎ special 4 ⇎ private-use 1, 相加校住 185, 差 0), 其中 macrolanguage 档与 ⟦R⟧⟨Macrolanguage: zh⟩ 那 545 段互相定义着对方。Comments 字段 169 段／170 行／折叠口径 8248 字符(两口径差 104 字符, 因为有一段写了两行 Comments), 里面既有 ⟦R⟧⟨Comments: as of 2006-03-29 GB no longer includes the Channel Islands and⟩ 这种领土变更, 也有 ⟦R⟧⟨Comments: Does not include Caribbean (029) or Central America (013); see⟩ 这种直接引数字码的说明。
⏳ 日期账: ⟦R⟧⟨File-Date: 2026-09-17⟩ 声明 File-Date 2026-09-17; ⟦R⟧⟨Added: 2005-10-16⟩ 这类 Added 行 9296 处／152 个不同日, 最早 1995-08-23 ⇎ 最晚 2026-06-14(年份跨 31 载), 晚于 File-Date 的 0 条。Deprecated 302 条／45 个不同弃用日, 按类型是 232 ⇎ 5 ⇎ 11 ⇎ 5 ⇎ 24 ⇎ 25(相加 302 校住 302)。其中 13 条的弃用日早于本段自己的登用日(⟦R⟧⟨Deprecated: 1989-01-01⟩ 对 ⟦R⟧⟨Added: 2005-10-16⟩), 另有 49 处 Preferred-Value 指向已弃用的码——判词此处只记数; 这 13 条在表内的形状(各是什么类型、登用日是否同一天)由 ⛓注现查, 而两份日期为何错位仍不可由在库文件判定。
🗂 关键串穿两源 15 枚(归一键: 只留字母数字并小写) ⇒ 两源同现 6 枚 ⇎ 只现一源 9 枚(注册表独占 9, 时区表独占 0) ⇎ 一枚不中 0 枚; 同现的是 region ／ script ／ %% ／ AD ／ GB ／ Europe。逐字锚候选池 10804 条(注册表 10746 ⇎ 时区表 58): 整行取 ≥12 字符且不含制表符, 按时区表的行全是制表分列, 另取其片段 ≥8 字符。池里归一后穿两源的只有 3 条——⟦R⟧⟨Description: Sô⟩ ⇎ ⟦Z⟧⟨Antarctica/⟩ ⇎ ⟦Z⟧⟨Atlantic/⟩, 三条全是词形巧合: 归一键把 'Sô' 的 'ô' 与 'Antarctica/' 的尾斜杠都吃掉, 而按原样逐字判在两源另一源里一条都找不到(0 条, 于是 3 条只活在归一口径里)。这条口径差写进门槛: 短语级同现 6 枚 ⇎ 逐字级同现 0 枚 ⇎ 归一后池内同现 3 条, 三个数各问各的。
🧪 这条的可核事实分三档, 第一档全部由两源字节现推(⟦R⟧⟨File-Date: 2026-09-17⟩ ⇎ ⟦Z⟧⟨# This file is in the public domain.⟩ ⇎ ⟦R⟧⟨Comments: Indicates that the content is transcribed according to X-SAMPA⟩) ⇒ 第一档 B55V 可复算: 两源的字节/换行/段/'<'/制表符/'#'行/非 ASCII, 段数与分隔符差 0, 三档段数闭合 0, 字段行的逐行⇎折叠差 605(其余字段 0), 四字段两口径矩阵(整码 29 ⇎ 拆片 0, 复合差 0), 值域宽度差 3, 长度八档闭合 0, region 三分闭合 0 ⇎ 差集三分闭合 0, 第 4 列充要条件相符 312/312, 制表符结构推得差 0, 坐标两档闭合 0, 以及锚的归属(下面报数)。第二档只在本机成立: 两份字节的磁盘 mtime 与文件里写的日期谁新谁旧——它进注不进门槛, 因为门槛要能在任何一份拷贝上重跑。第三档不可核, 由成因决定: 13 条弃用日早于登用日的来历, 'The most populous city' 那条首位选择规则要有人口数据才能判, ⟦Z⟧⟨# Mention RU and UA alphabetically.  See “territorial claims” above.⟩ 背后的领土主张, 注册表由哪个机构按什么流程更新, 以及 4 枚私用区间“归谁分配”——库里只有这两份字节。锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 41 处／29 条去重串, 归属由正文现推, 每条对两源逐一判成员共 58 次检查, 单源 26 ⇎ 两源同现 3, 错配 0 处。
∴ 骨架 ⇒ ① 两源字节 731819 ⇎ 17592, 换行 49316 ⇎ 375, 非空行 49316 ⇎ 375, '制表符' 0 ⇎ 833, 非 ASCII 723 ⇎ 38, '#' 行 0 ⇎ 63; ② 注册表是段表: 9297 段由 9296 行分隔符切出, 9203 段带 Subtag ⇎ 94 段不带, 字段名 13 种, 逐行 39938 ⇎ 折叠 39333; ③ 主轴: 四字段 1546 个值, 整码判越界 29 ⇎ 拆片判越界 0, 越界数与复合数差 0, 两口径都干净的 2 ⇎ 4 个; ④ 值域: 225 ⇎ 8276 ⇎ 8945 ⇎ 8948, 最宽一档比子标签池宽 3 枚; ⑤ 长度签名 8 档闭合 0, 私用区间 4 枚各为其类型最长; ⑥ 跨文件 join: region 305 ⇎ 国家码 247, 交集 247, 两向差 0 ⇎ 58(其中真缺口 25); ⑦ 时区表自写规则对数据: 第 4 列充要 0+0 违例 ⇎ 首码逆序 0 ⇎ 整列 21 ⇎ 去首国 1, 坐标 265 ⇎ 47, 制表符差 0; ⑧ 日期 9296 处／152 日 ⇎ 302 条弃用, 反向 13, 指向已弃 49; 穿两源短语 6 枚 ⇎ 逐字 0 条。判词: 一张表说“值必须是一个码”, 另一张表把同一批码用作国家列——两份文件对同一串字母的约束一个是硬值域一个是引用, 而 29 枚“越界”全是因为判法把一个复合标签当一个标签; 换一根口径, 同一批字节给的是 0 而不是 29。
ℒ 方法 ⇒ 遇到“字段值必须是另一张表里的码”这种约束, 先问判法再问结论: 本条把四个字段各判两遍(整码 ⇎ 拆片), 29 ⇎ 0 两数并写, 并把“越界的全是复合标签”写成差值键 0 而不是靠断言假设; 把段的账写成三档相加(9203 ⇎ 93 ⇎ 1), 把字段的账写成两口径相减(39938 ⇎ 39333 = 605), 且证明余下 0 处不属于其它字段; 把跨文件的 join 写成双向差(0 ⇎ 58)再把并集侧拆开(25 ⇎ 31 ⇎ 2), 免得“缺 58 枚”被读成 58 个错误; 把注释里的规则拿数据判(第 4 列充要 312／312, 排序首码 0, 其余 21 ⇎ 1), 并且把两种排序口径都报——只报整列判的那 21 行会显得这张表更不守规矩; 最后把归一键能穿、逐字串不能穿的那 3 条词形巧合单独计一笔(0 条逐字同现)。
✂️ 为什么这份编码比摘要窗口长 ⇒ 两源各 731077 ⇎ 17536 字符, 窗口只能取锚点触到的行; 而本条的结论全是跨行量: 1546 个字段值的两口径矩阵、9297 段的三档闭合、8 档长度签名、312／312 行的充要条件核对、9846 行 Description 的两口径复用。尤其“整码判 29 ⇎ 拆片判 0”这一对, 任何单窗口都装不下四字段各自的复合值清单。读它请按“这个数是对哪个字段、用哪种判法数出来的”来读, 而不是按“少抄了多少原文”。

## ⛓解读注

- 四套实现与一处非独立: 采集侧 _pick55.py ⇎ 建条目侧 _mkB55.py(扁平契约 179 键, 与采集侧在 95 个量上对过账) ⇎ 门槛内 _b55_scan()。本注是第四遍: 上面 179 个键逐个与审计器快照对齐(不符即停机), 另自行从两份字节重取了 段数 9297、字段行 39938、Z 数据行 312、制表符 833、File-Date 2026-09-17 ——五个数与契约逐一相同。
- _b55_scan 的量测段由 _wire55.py 从 _mkB55.py 的 SCAN 段逐行抽出(只改路径常量与模块别名), 插门前把 _b55flat.json 的 179 个键与 DERIV['B55'] 的 101 条算式在抽出体上跑过; 因此真正独立的两遍是 _pick55.py 与本注: 采集侧用“每段同名只留一格”的解析器起步, 本注自己写了两套解析器(折叠 ⇎ 逐行) 并把两种口径的差异当成被测量本身, 而不是当成噪声。
- 门槛的账: DERIV 键 101 个 ⇎ 引用点 323 处 ⇎ 同数共键 39 组(两名以上 15 组) ⇎ 0 键折 27 项。同数的字面不取第一条算式, 而是复合式 LIT*(1-(max(全部算式)-min(全部算式))): 每条算式都等于该字面时括号才为 1。
  - 同数 3(10 条): variant 长4 枚 ⇎ 只在 Preferred-Value 出现的码枚数 ⇎ Prefix 值域比子标签池宽 ⇎ Preferred-Value 整码越界 ⇎ Preferred-Value 复合值 ⇎ X 或 Q 开头的 region 枚数 ⇎ z_pre_min ⇎ 归一后穿两源的池条数 ⇎ 只靠归一键才同现的条数 ⇎ 穿两源的锚串数
  - 同数 1(7 条): script 长10 枚 ⇎ 长 10 字符的子标签枚数 ⇎ scope_private ⇎ 'ZZ' 在不在 region 池 ⇎ z_tail_un ⇎ 空 Type 段数 ⇎ 只有 File-Date 的段数
  - 同数 2(5 条): region 长6 枚 ⇎ 同一码最多共用段数 ⇎ 整码判零越界的字段数 ⇎ reg_other ⇎ reg_range_only
  - 同数 31(5 条): variant 长5 枚 ⇎ 长 5 字符的子标签枚数 ⇎ 登用年份跨度 ⇎ reg_digit ⇎ reg_digit_only
  - 同数 26(3 条): Prefix 整码越界 ⇎ Prefix 复合值 ⇎ 只属一源的锚串数
  - 同数 29(3 条): viol_whole ⇎ 含连字符的值枚数 ⇎ 锚去重串数
  - 同数 312(3 条): 第 4 列与充要条件相符的行 ⇎ z_zone_n ⇎ z_zone_dist
  - 同数 4(3 条): 拆片判零越界的字段数 ⇎ Scope 取值种数 ⇎ scope_special
- 主轴的来历(必须写, 因为它一度给出错的头条数): 四个交叉引用字段按“整码判”给 29 个越界值, 按“拆片判”给 0 个, 且越界减复合型 = 0, 所以越界的那 29 枚全是含连字符的复合标签。采集侧第一版把字段值按每段只留一格来收, Prefix 因此只收到 390 个值(逐行口径是 444 个, 少 54 个, 全在 17 段里出现第二条以上的 Prefix 之中, 单段最多 11 行); 本注自己写两套解析器现算复现: 折叠口径下四字段整码越界合计 17 枚(Prefix 14 ⇎ Preferred-Value 3 ⇎ 另两个各 0), 逐行口径 29 枚(Prefix 26), 头条数取逐行——差 12 枚恰好等于 Prefix 那一栏少收的 12 枚。再说一层口径: 头条数 29 是“不同值”数(同一复合值在几段里重复登记只计一枚), 按出现处数判则是 52 处(Prefix 49 ⇎ Preferred-Value 3 ⇎ 另两个各 0), 多出的 23 处全来自同一个复合值的重复登记——判词写的是前者。
- 同一件事的第三处口径差: Comments 段数 169 ⇎ 行数 170, 字符数按折叠口径 8248 ⇎ 按逐行 8352(差 104)——有一段真带两行 Comments, 所以“折叠只留最后一格”在别处也少收: Description 逐行 9846 处 ⇎ 折叠 9296 处, 不同串 9413 ⇎ 8911(差 502)。这两笔都在门槛里各占键, 不是靠断言假设相等。
- 时区表自写的规则由它自己的数据判: 第 4 列的充要条件核对到 312／312 行, 两个方向的反例各 0 ⇎ 0; “先按国家码排”在整列口径下 21 行不守 ⇎ 去掉每行首国的口径下 1 行不守(剩下那一行正是 America/Puerto_Rico: 首国之外 20 枚码没按字母排, 而它同时是 20 国共行的那一格); 制表符枚数 833 由列结构反推(3 列 111 行×2 ⇎ 4 列 201 行×3, 加那条列名注释行的 3 枚与 5 行 '#@' 各 1 枚)完全对上, 差 0。
- 跨文件那笔账的方向性: Z 国家列 247 枚码全部在注册表 region 池 305 枚里(Z 有而 R 无 0 枚), 反向缺 58 枚 = 两位码 25 ⇎ UN 数字码 31 ⇎ 区间 2(三档相加与 58 差 0)。真正“没被用到”的只有那 25 枚两位码, 另外 33 枚本就不是 zone1970 能写的形状——判词把这两类分开写, 合起来说“缺 58”会夸大。
- 两份文件的指纹(旁证, 判词里只报“种数”而不报串, 因为串里的数字段无法由字节直接命中): 755fad43283be7b41ebe3c89ad054b6eaf928f404f9c0edb74799e0eab74beb1 ⇎ 5f23781702bf51408ff1581daa109ab3b9257fb433b1554e579d92172892c0cf; 字节 731819 ⇎ 17592(比 42 倍), 非 ASCII 723 ⇎ 38 枚, 所以“字符数=字节数”在 0 份上成立。
- 时间分两档(第二档只在本机): 内容侧两个日期各写在各的文件里且逐字可锚——注册表 2026-09-17, 时区表 From Paul Eggert (2025-05-15); 磁盘 mtime(换 UTC)是 2026-10-19 09:22:57 ⇎ 2026-09-22 01:49:27, 各自减去内容日期 = +32.72 ⇎ +495.41 天(正为 mtime 落在内容日期之后)。“注册表比它自己声明的版本更新得勤”这件事在库里只能由 Added 最晚 2026-06-14 与 File-Date 2026-09-17 的先后判, mtime 那条拷贝一次就失效, 所以只写在这里。
- 反向时序不是数据错, 而是两件事共用一个字段: 弃用日期早于登用日期的 13 段, 本注逐段回查类型得 language 型 4 枚(in,iw,ji,jw) ⇎ region 型 9 枚(BU,DD,FX,NT,SU,TP,YD,YU,ZR), 它们的 Added 全落在同一天 2005-10-16(注册表收编 ISO 已撤码的那批), 而 Deprecated 最早 1989-01-01——那是 ISO 那边撤码的日子, 早于注册表登记 16 年。另一侧: Added 晚于 File-Date 的 0 段(无), 弃用日期共 45 个不同日 ⇎ 登用日期 152 个不同日。判词按内容判, 不替注册表的编辑顺序作保。
- 锚的账: 去重 29 串 ⇎ 正文 41 处 ⇎ 每标签 {'R': 30, 'Z': 11} ⇎ 单源 26 ⇎ 两源同现 3 ⇎ 成员检查 58 次 ⇎ 错配 0 处; 本注另按“整串在该源字节里逐字出现”复查: 归一后覆盖 R 20 ⇎ Z 12 串, 逐字命中 R 18 ⇎ Z 11, 两源之一命中 29／29。
- 假同现三枚(必须单写, 因为归一键会把它们判成穿两源的锚): Description: Sô ⇎ Antarctica/ ⇎ Atlantic/——归一(只留字母数字并小写)后两源都现, 逐字复核对 0 枚, 所以候选池里“穿两源”的 3 条一条都不是真同现, 门槛里 x_verbatim = 0 ⇎ x_normonly = 3 各占一键。 关键串矩阵那 15 枚用的是同一归一键, 两源同现 6 ⇎ 单源 9(R 独占 9, Z 独占 0) ⇎ 不中 0, 同现名单: region ／ script ／ %% ／ AD ／ GB ／ Europe。
- 锚的口径(与 B53/B54 不同, 必须单写): 两源都用原文件行判成员, 不设“去标签正文”这一层——注册表 0 枚 '<' 也 0 枚制表符, 时区表的 3 枚 '<' 全住在注释写的 '<tab>' 记法里, 若去掉注释行, '#@' 那 5 行与它声明的规则一起消失, 而“注释自写规则 ⇎ 数据核对”正是本条的一条主轴。候选池 10804 条(R 10746 ⇎ Z 片段 58)是按“去掉首尾空白且不含制表符、长度≥12”现建的, 抽 code 侧另建一套同样规则的池, 两边条数相同(10804)。
- 同一份字节被几代条目各压过一次: 共用源 5 处 B09(源0, 锚30, 交0) ／ B10(源1, 锚11, 交0) ／ B45(源1, 锚13, 交0) ／ B49(源1, 锚49, 交2) ／ B52(源1, 锚50, 交1)。本条与它们不重叠也不冲突——交叠最多的那条也只共用 2 串锚, 共用的是同一句原文而不是同一个论断: 本条量段结构、值域两种判法与时区表自写规则的核对, B45 量同一个名字的三种对象, B49 量检查这张表的 awk, B52 量时效分区, B10 量版本账, B09 只量单源里的记法。反过来 langsubtag.txt 那一份此前只在 B09 被单源用过, 本条把它与 zone1970.tab 配成对照, 才第一次量到“借码”这一层。
- 不可核清单(库里无相应字节, 写成判词即越界): 这些值域约束在 RFC 5646 正文里如何表述(库里只有注册表本身); zone1970.tab 的三条自写规则是否由上游 checktab.awk 校验(该文件在库, 但它对本表校的不是这三条); 区间码 QM..QZ ⇎ XA..XZ 的名义归属是“保留”还是“私用”(文件只给码与 Description); 49 处 Preferred-Value 指向已弃码是注册表的已知遗留还是有意为之; 下一版注册表会不会改动那 29 枚越界复合标签。
