# B52 时效表 ⇎ 检查它的 awk ⇎ 它要的那份不存在的 zdump 表：组织键住在被跳过的那一层
src: corpus/raw/tz/zonenow.tab (8425 字节／数据行 91) ⇎ corpus/raw/tz/zone1970.tab (17592 字节／数据行 312) ⇎ corpus/raw/tz/checknow.awk (1212 字节／数据行 52) ⇎ corpus/raw/tz/Makefile (56501 字节／数据行 759) (同目录另有 zone.tab 与 version 两份, 只用于集合与口径对照, 不作锚源)
；联结不是“四份材料”, 而是“一张表与它的三个层次”: 分区表按偏移排序(91 枚组标签⇎91 行, 逆序 0), 检查器按定义跳过那一层注释, 它要比的输出序列由构建配方现造现删(库内 0 份), 谓词“从现在起一致”因此不可在库判定; 姊妹表把同一批钟按 1970 年重说一遍, 共有时区坐标全同而国码全不同(91⇎0)
tags: 三级排序零违例 偏移只活在注释层 检查器只读两列 占位码与真国码 自述过期条款 标签与注释指向两个时刻 缩写闭合三口径 真值输入在库为零 前瞻跨度自认不足 墙钟决定检查起点 按输出序列建索引 同名不同层 穿层命中矩阵 锚归属由正文现推
## [[原始语料|ORIGINAL]]
### ⟦N⟧ ⟸ corpus/raw/tz/zonenow.tab

This file is in the public domain. # # From Paul Eggert (2023-12-18): # This file contains a

where civil timestamps are predicted to agree from now on. # This file is like zone

# 2. The first column is irrelevant and ignored. # 3. The table is sorted in a different way: # first by standard tim

# 4. Every timezone has a nonempty comments column, with wording # distinguishing the tim

# # The format of this table is experimental, and may change in future versions. # # This table is intend

# #XX coordinates TZ comments # # -11 - SST XX -1416-17042 Pacific/Pago_Pago Midway; Samoa (SST) # #

-10/-09 - HST / HDT (North America DST) XX +515248-1763929 Amer

-08/-07 - PST/PDT (North America DST) XX +340308-1181434 Amer

-08/-07 - PST/PDT (North America DST) until 2026-11-01 02:00; then MST XX +4916-12307 America/Vancouver Mountain Standard (MST) - British Columbia (most areas) # # -07 - MST XX +33265

MST/MDT (North America DST) XX +

America/Edmonton Central Standard (CST) - Alberta, NWT, and some neighbors # # -06 XX -0054-08936 P

CST/CDT (North America DST) XX +

America/Winnipeg Eastern Standard (EST) - Manitoba, northwestern Ontario # # -05 XX -1203-07703 A

America/Havana Cuba # # -05/-04 - EST/E

Troll DST XX -720041+0023206 Antar

IST/GMT (EU DST in reverse) XX +5320-00615 Europe/D

Morocco DST) XX +3339-00735 Africa/C

10:30/+11 XX -3133+15905 Australia/Lord_Howe Lord Howe Island # # +11 XX -0613+15534 P

New Zealand (NZST/NZDT) # # +12:45/+13:45 (Chat

Samoa (western); Tonga # # +14 XX +0152

### ⟦Z⟧ ⟸ corpus/raw/tz/zone1970.tab

This file is in the public domain. # # From Paul Eggert (20

civil timestamps have agreed since 1970. Columns are separated by # a single tab.

Pacific/Pago_Pago Midway AT +4813+01620 Eu

Lord Howe Island AU -5430+15857 Antarctic

America/Winnipeg EST - Manitoba, ON (nort

America/Edmonton CST - AB, BC(E), NT(E),

America/Vancouver MST - BC (most areas) CA

CI,BF,GH,GM,GN,IS,ML,MR,SH,SL,SN,TG +0519-00402 Africa/Abidjan CK -2114-15946 Pacific/R

America/Havana CV +1455-02331 Atlantic/

PR,AG,CA,AI,AW,BL,BQ,CW,DM,GD,GP,KN,LC,MF,MS,SX,TT,VC,VG,VI +182806-0660622 America/Puerto_Rico AST - QC (Lower North Shore) PS +3130+03428 Asia/Gaz

### ⟦K⟧ ⟸ corpus/raw/tz/checknow.awk

This file is in the public domain. function record_zone(zon

while (getline <zdump_table) { if ($0 ~ /^TZ/) { rec

FS = "\t" } /^[^#]/ { zone = $3 data = zone_data[zone] if (!data) { printf "%s: no data\n", zone status = 1 } else { zone

printf "zones %s and %s identical from now on\n", zone, zone2 status = 1 } else zoneno

printf "Zone table should have one of:%s\n", zones[data] zonenow[data] = zone # This suppresses duplicate diagnostics. status = 1 } } if (now_out) { for (data in zones) { printf "%s=%s\n", now, zones[data] >>now_out } } exit status }

### ⟦M⟧ ⟸ corpus/raw/tz/Makefile

mv $@.out $@ # These files can be tailored by setting BACKWARD, PACKRATDATA, PACKRATLIST.

right_posix: right_only rm -fr '$(DESTDIR)$(TZDIR)-leaps' ln

CHECK_NOW_TIMESTAMP = $$(./date +%s) CHECK_NOW_FUTURE_YEARS

now.ck: checknow.awk date tzdata.zi zdump zic zone1970.tab zonenow.tab rm -fr $@d mkdir $@d ./zic -d $@d tzdata.zi now=$(CHECK_NOW_TIMESTAM

-v now=$$now \ -v now_out=$@.out \ -v zdump_table=$@d/zdump-now.tab \ -f checknow.awk zoneno

## ⟪BabelTele⟫
🧭 体例 ⟦N⟧⟨# The format of this table is experimental, and may change in future versions.⟩ ‖ ⟦N⟧⟨# where civil timestamps are predicted to agree from now on.⟩ ‖ ⟦Z⟧⟨# civil timestamps have agreed since 1970.  Columns are separated by⟩ ⇒ 四份材料是同一套时区分区的三个层次加它的姊妹表: 字节 8425 ⇎ 17592 ⇎ 1212 ⇎ 56501, 字符 8417 ⇎ 17536 ⇎ 1212 ⇎ 56466, 非空行 302 ⇎ 375 ⇎ 54 ⇎ 1305, 其中注释行 211 ⇎ 63 ⇎ 2 ⇎ 546 ⇎ 数据行 91 ⇎ 312 ⇎ 52 ⇎ 759(顺序始终是时效表⇎姊妹表⇎检查器⇎构建器)。四份都算“文本”, 但只有表有字段数这件事: 时效表 91/91 行齐四列(连列头那行一起数, 含制表符的是 92 行), 姊妹表 111 行只有三列 ⇎ 201 行四列, 第三份姊妹表 216 ⇎ 202。检查器 54 行里只有 2 行是注释, 构建器的注释行比时效表的数据行还多——注释层最厚的那份最不像表。谓词只写在表的注释里: 时效表有 2 句现在时(含 now 的行共 2 行), 姊妹表只有 1 句过去时。这条的箭头不是文体对照, 而是“同一套分区在两时态下的两份产物”加“判它们的那段程序”与“调用那段程序的那份配方”。
🧱 排序键住在检查器跳过的那一层 ⟦N⟧⟨# -08/-07 - PST/PDT (North America DST)⟩ ‖ ⟦N⟧⟨#XX	coordinates	TZ	comments⟩ ‖ ⟦K⟧⟨zone = $3⟩ ⇒ 时效表的 91 行由 91 行组标签分组, 标签与数据行严格 1:1 交错(组内行数只有 1 这一种取值), 沿标签读下去偏移从 -11 单调升到 14(逆序 0 对), 偏移只有 37 种却有 91 组, 同一偏移最多被拆成 8 组, 加上夏令时另一端共 56 种偏移对。可是这个把整张表撑起来的偏移值, 在 91 行数据的任何一列里出现 0 次(注释列 0 ⇎ 时区名列 0): 它只活在注释层。而检查器给这一层的待遇是 1 枚“非注释才处理”的谓词, 整层跳过; 它对数据行做的事从 ⟦K⟧⟨zone = $3⟩ 起笔: 整行引用 4 处 ⇎ 第三列 1 处, 第一/二/四列各被引用 0/0/0 次。于是表自述的第一列 ⟦N⟧⟨# 2.  The first column is irrelevant and ignored.⟩ 被反向证实: 时效表第一列只有 1 种取值(共 92 处占位码, 含列头那枚), 姊妹表同一列有 160 种、其中 34 行是多码; 两表共有的 91 个时区里坐标一致 91 个 ⇎ 国码一致 0 个。判词: 把表组织起来的那个量, 恰好是校表程序按定义不去读的那个量。
⏳ 一张把自己写在有效期内的表 ⟦N⟧⟨# -08/-07 - PST/PDT (North America DST) until 2026-11-01 02:00; then MST⟩ ‖ ⟦N⟧⟨# From Paul Eggert (2023-12-18):⟩ ⇒ 整份文件的 ISO 日期共 4 处, 全在注释层(注释 4 ⇎ 数据 0), 只有 2 个取值; 其中 3 行组标签自带“到某一刻就改组”的条款, 三条指向同一时刻同一小时(⟦N⟧⟨# -08/-07 - PST/PDT (North America DST) until 2026-11-01 02:00; then MST⟩ 是其一), 而它们名下的 3 行恰好是这张表里唯一“标签⇎注释指着两个时刻”的行: ⟦N⟧⟨America/Vancouver⟩ 的标签里写 ⟦N⟧⟨PST/PDT⟩ ⇎ 注释里写 ⟦N⟧⟨Mountain Standard (MST) - British Columbia (most areas)⟩; ⟦N⟧⟨America/Edmonton⟩ 同构(标签 ⟦N⟧⟨MST/MDT⟩ ⇎ 注释 ⟦N⟧⟨Central Standard (CST) - Alberta, NWT, and some neighbors⟩); ⟦N⟧⟨America/Winnipeg⟩ 亦然(标签 ⟦N⟧⟨CST/CDT⟩ ⇎ 注释 ⟦N⟧⟨Eastern Standard (EST) - Manitoba, northwestern Ontario⟩)。两个年份之差可算: 条款时刻比这份文件的落款(2023 年)晚 1049 天, 而姊妹表的落款比这份落款晚 514 天。一旦条款生效, 这 3 行要换组、缩写要与标签对齐、第二条里那条 0 逆序的单调性也要重测——但这一步不可由在库文件判定: 能判它的那份 zdump 表只在构建目录里出现(见第七条), 所以本条只登记“条款在库内有 3 处”与“它落在未来 3 处”, 不假装检验它会不会生效。
🧵 缩写在三条层里的闭合度 ⟦N⟧⟨# -10/-09 - HST / HDT (North America DST)⟩ ‖ ⟦N⟧⟨America/Havana⟩ ⇒ 组标签带缩写的 52 组 ⇎ 名下那行注释里带括号的 48 行 ⇎ 括号总数 49 枚(一枚以上括号的只有 1 行)。两边写法对得上的: 与第一个括号逐字同 42 处, 与末括号同 42 处, 只要出现在任一括号里 42 处——三种口径给出同一个数, 说明分歧不来自“取哪一枚括号”。缺口 10 处分三类, 三类都能各举一枚: 只差空白 1 处 ⟦N⟧⟨# -10/-09 - HST / HDT (North America DST)⟩(标签里缩写带空格 ⇎ 注释里不带), 时态差 3 处(上一条那 3 行, 例如 ⟦N⟧⟨America/Edmonton⟩), 注释里根本没有括号 6 处(⟦N⟧⟨America/Havana⟩ 一类); 反方向(标签不写缩写而注释里有括号) 2 行, 即 ⟦N⟧⟨New Zealand (NZST/NZDT)⟩ ⇎ ⟦N⟧⟨Samoa (western)⟩——一枚是标签只肯给规则名, 一枚是括号里装的其实地区限定词。第四列本身干净: 91 行非空(表自述 ⟦N⟧⟨# 4.  Every timezone has a nonempty comments column, with wording⟩), 取值 91 种即行行互不相同, 带分号的 25 ⇎ 带括号的 48 ⇎ 两者都带的 12。判词: 同一层信息(缩写)在标签⇎注释两处各写一遍, 十之八九对得上; 剩下的对不上处正好是这张表“会在未来变化”的位置——不一致不是抄错, 是两处写的是不同时刻的事实。
📐 表自述的三层排序键全部可机检、全部成立 ⟦N⟧⟨# 3.  The table is sorted in a different way:⟩ ⇒ 时效表头部声明排序是“标准偏移→夏令时偏移→缩写”三级。逐级复算: 第一级逆序 0 对; 第二级(同标准偏移下, 有 DST 的组该排在哪里)逆序 0 对; 第三级可比较的相邻对 20 组, 逆序 0 对。三级之外还能查出偏移自己的形状: 非整点偏移 13 组, 分钟位只有 2 种取值; DST 步长分布是 +1 小时 30 组 ⇎ 反向(所谓“夏令时”比标准时更西) 2 组 ⇎ 半小时 1 组 ⇎ 两小时 1 组——半小时那枚出自 ⟦N⟧⟨+10:30/+11⟩(注释 ⟦N⟧⟨Lord Howe Island⟩), 两小时那枚出自 ⟦N⟧⟨Troll DST⟩(给南极考察站); 反向的两枚是 ⟦N⟧⟨IST/GMT (EU DST in reverse)⟩(欧洲/以色列一侧回拨)与 ⟦N⟧⟨(Morocco DST)⟩(摩洛哥只写规则名而不写缩写)。姊妹表按另一套自述排序(按国码), 复算其首码逆序也是 0 对。判词: 写在注释里的排序规则不是修辞, 91 行全数可验且零违例; 而同一份注释里那句“第一列无关”同样可验, 却只在检查器那侧成立(第二条)。
🧲 两时态的分区差多少, 差在哪一列 ⟦Z⟧⟨CI,BF,GH,GM,GN,IS,ML,MR,SH,SL,SN,TG	+0519-00402	Africa/Abidjan⟩ ‖ ⟦Z⟧⟨PR,AG,CA,AI,AW,BL,BQ,CW,DM,GD,GP,KN,LC,MF,MS,SX,TT,VC,VG,VI	+182806-0660622	America/Puerto_Rico	AST - QC (Lower North Shore)⟩ ⇒ 集合上是真子集: 时效表 91 行 ⇎ 姊妹表 312 行 ⇎ 第三表 418 行, 后两者分别多出 221 与 327 个时区名, 时效表自己 0 处重名。共有的 91 个时区逐列比: 坐标一致 91/91 ⇎ 国码一致 0/91 ⇎ 注释列一致 6/91, 而姊妹表名下有注释的只有 54 行(它允许第四列整列缺失: 三列行 111 处 ⇎ 四列行 201 处, 注释为空 111 行)。按粒度量复现: 整行级 0 处 ⇎ 坐标级 91 ⇎ 时区名级 91 ⇎ 五词串级 49(两侧串库 777 ⇎ 2367); 与第三表的五词串共有 42/2802, 而时效表的数据层与它自己的注释层共有五词串 0 处、三元组 0 处、二元组只有 16 处(层内串库 770 ⇎ 474)。判词: 两张表说的是同一批钟, 但“同一批”只到坐标与时区名为止; 注释列各自新写(共 201 种 ⇎ 91 种), 于是换了时态就等于换了一次撰稿。
🔬 检查器的真值输入不在库里, 而且每次构建都换个起点 ⟦K⟧⟨while (getline <zdump_table) {⟩ ‖ ⟦K⟧⟨FS = "\t"⟩ ⇒ 那段 awk 只认 3 个外部变量, 它们在文件里被赋值 3 次——全靠调用方喂: ⟦M⟧⟨-v zdump_table=$@d/zdump-now.tab \⟩ ⇎ ⟦M⟧⟨-v now=$$now⟩ ⇎ ⟦M⟧⟨-v now_out=$@.out⟩。喂进去的头一枚就是那份 zdump 表: 它的变量名在检查器里出现 1 次, 而“zdump-now”这个文件名在检查器里出现 0 次(表名不由检查器说出口, 只由调用方给), 在构建器里出现 2 次(一次写出、一次当输入), 而整个语料库里名字含 zdump 的文件 0 份、产物 now.ck 0 份。配方 ⟦M⟧⟨now.ck: checknow.awk date tzdata.zi zdump zic zone1970.tab zonenow.tab⟩ 声明 7 项前置, 库内实有 3 项、缺 4 项(日期程序、打包后的数据、zdump、zic 都要现造); 它先 ⟦M⟧⟨mkdir $@d⟩ 再 ⟦M⟧⟨./zic -d $@d tzdata.zi⟩ 造出临时目录, 用两条 zdump 各跑一遍地平线(2 种: 一条自“此刻”起 ⇎ 一条自姊妹表自述的 1970 年起), 最后 ⟦M⟧⟨rm -fr $@d⟩ 连真值输入一起删净——建 1 次 ⇎ 删 2 次, 结论只以 ⟦M⟧⟨mv $@.out $@⟩ 留下一枚时间戳。更硬的一点在时间基准: ⟦M⟧⟨CHECK_NOW_TIMESTAMP = $$(./date +%s)⟩ 让整趟检查的起点取自构建当天的墙钟(同一段里 $$now 被引用 3 次), 于是同一份表在不同日子检查的是不同的“从现在”; 检查器被调用 2 遍, 其中 1 遍显式给它表名。跨度也写着妥协: 前瞻 28 年 ⇎ 注释自认“理论上要 2800 年以上”, 相差 100 倍; 秒数按 366 天/年取整 885427200, 比 365 天口径多 2419200 秒(恰为 28 天)。判词: “从今往后一致”是一个必须由外部真值判定的谓词, 而那份真值既不入库又随日期漂移; 所以这条不能像 B49 那样把不变量交回机检, 只能交回构建系统。
🧩 判定动作只有四类, 而它比的不是行而是“输出序列” ⟦K⟧⟨printf "Zone table should have one of:%s\n", zones[data]⟩ ‖ ⟦K⟧⟨printf "zones %s and %s identical from now on\n", zone, zone2⟩ ⇒ 检查器一共 4 条 printf(4 种格式), 判失败的赋值 3 处, 出口 1 处: 其一“无数据”⟦K⟧⟨printf "%s: no data\n", zone⟩(某时区在真值输入里查不到), 其二“两个时区的钟从现在起一样”⟦K⟧⟨printf "zones %s and %s identical from now on\n", zone, zone2⟩, 其三“主表里还有一组没人收录的序列”⟦K⟧⟨zonenow[data] = zone # This suppresses duplicate diagnostics.⟩, 其四把对照写进旁出文件⟦K⟧⟨printf "%s=%s\n", now, zones[data] >>now_out⟩(仅当调用方给了输出路径)。关键在键的选择: 按名字取真值 3 处 ⇎ 按“那段输出文本”建索引 4 处——所以它查的是“互不相同的未来序列各有一行”, 不是“行与行文字不同”。两套列口径也不同: 读真值输入时(非空行序第 10 行)仍是默认空白分隔, 制表符口径要到同一序的第 22 行才装上, 于是同一份 awk 内部对“什么是一列”有两份答案。判词: 检查器测的是等价类的个数, 而等价类由不在库里的文件决定; 这比 B49 那条“不变量只写在代码里”又退一步——这里连代码里的不变量都要等外部数据才能取值。
🗂 同一个名字能穿过几层 ⟦Z⟧⟨# This file is in the public domain.⟩ ‖ ⟦N⟧⟨agree from now on⟩ ⇒ 把 15 枚关键串各按折叠后的原样判一遍: 命中一层 8 枚 ⇎ 命中多层 7 枚 ⇎ 一枚不中 0 枚。三处最见层次: 姊妹表的名字在它自己体内出现 0 次(它从不提名自己) ⇎ 在时效表里 3 次 ⇎ 在构建器里 5 次; “从现在起一致”这句谓词在时效表 2 次 ⇎ 检查器 1 次 ⇎ 姊妹表与构建器各 0 次; 占位国码在时效表 92 次 ⇎ 构建器 2 次。真值输入的名字只在构建器 2 次, 而它的变量名在检查器 1 次 ⇎ 构建器 2 次。时效表的名字在检查器里出现 1 次(全在它自己那行注释), 在构建器 5 次。判词: 一份文件提到自己的次数为 0(0), 而别的层里有人提它 5 次——名字住在别人嘴里; 谓词同理, “从现在起一致”从没在被检表的任何一列里被检验过。
🧪 这条的可核事实分三档 ⟦N⟧⟨Pacific/Pago_Pago⟩(最西一档的时区名, 它 ⇎ 姊妹表里那一枚逐字同写) ⇒ 第一档 B52V 可复算: 四份源的字节/行/列口径、组标签机器(91⇎91 的 1:1)、三层排序键的逆序数(0/0/0)、缩写闭合的三口径(42/42/42)、坐标两种宽度(75⇎16)、集合差(221/327)、四种粒度的共有量、检查器与构建器的每一处计数, 全部由 audit.py 的 _b52_scan 从四份 raw 重算。第二档只能由集合运算得出: 谁是谁的子集、共有时区的逐列比对、穿层命中矩阵。第三档不可核, 也是本条与 B48/B49 的分界: “从现在起这些钟一致”这一谓词要靠一份 zdump 输出表来判, 而这样的文件在库里 0 份, 检查起点又取自构建当天的墙钟——所以它写进判词而不写成待核, 门槛里没有一项替它背书。锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 56 处／50 条去重串, 命中列分布是一源 43 ⇎ 多源 7 ⇎ 四源 0, 每条去重串对四份源逐一判成员, 共 200 次检查, 错配 0 处; 归属由正文现推, 不由旁注文件说了算——采集侧为挑引文切的候选锚池不写进判词, 门槛也就无从核它。
∴ 骨架 ⇒ ① 四源 8425 ⇎ 17592 ⇎ 1212 ⇎ 56501 字节 ⇎ 非空行 302 ⇎ 375 ⇎ 54 ⇎ 1305 ⇎ 数据行 91 ⇎ 312 ⇎ 52 ⇎ 759, 齐四列的只有 91 行; ② 排序键 91 枚组标签撑起 91 行、偏移 37 种、逆序 0, 而该键在数据列出现 0 次、被检查器以 1 条规则整层跳过; ③ 第一列 1 种取值 ⇎ 姊妹表 160 种, 共有 91 个时区坐标一致 91 ⇎ 国码一致 0; ④ 缩写闭合三口径同为 42, 缺口 10 分三类, 其中 3 行标签⇎注释指向两个时刻, 条款比落款晚 1049 天; ⑤ 三层排序全部可验全部零违例(0/0/0), DST 步长 30⇎2⇎1⇎1; ⑥ 真值输入在库 0 份 ⇎ 配方前置缺 4 项 ⇎ 起点取自墙钟, 故“从现在起一致”不可由在库文件判定; ⑦ 检查器按输出文本建索引(4 处)而非按行文, 内部还用两套列口径(非空行序第 10 ⇎ 第 22 行); ⑧ 姊妹表从不提名自己(0 次), 谓词也不在数据层(2⇎1)。判词: 一张表的组织键、有效期与判据分别住在注释层、未来与库外三处, 三处都不在“可机检的现在”里; 而能机检的部分(排序、列口径、集合、闭合度)在本条全部交出零违例, 这恰好反衬出剩下那部分为什么不可核。
ℒ 方法 ⇒ 读“会过期的表”先分层再读数: 把每一句话按它住在哪一层归类(数据列⇎组标签注释⇎头部注释⇎程序⇎配方), 然后逐层问“谁读它”。本条的做法是拿检查器的字段引用表(4/1⇎0/0/0)当“可见性”的判据, 而不是拿人眼。第二步测声明式不变量: 头部说了三级排序就分三级各算逆序数, 说了第四列非空就数它 91/91 种取值。第三步把时间当口径而不是当背景: 同一份文件里的 2 个日期各属哪一层、条款距本表落款 1049 天⇎两份落款相距 514 天, 以及自认的前瞻跨度 28⇎2800。第四步给“不可核”留位置并写明成因(真值输入在库 0 份 ⇎ 墙钟变量 3 处), 绝不用漂亮的比例凑数。第五步注意同名不同层: 同一个缩写、同一个文件名、同一个谓词, 在标签层⇎注释层⇎程序层各写一遍, 逐字对不上时先问“是不是在说不同时刻”, 再判谁错了。
✂️ 为什么这份编码比摘要窗口长 ⇒ 四份源各自 8417 ⇎ 17536 ⇎ 1212 ⇎ 56466 字符, 而摘要只能取锚点触到的窗口; 本条的结论不住在窗口里——“组织键住在被跳过的那一层”“三级排序零违例”“缺口 10 分三类”“真值输入在库 0 份”都是跨四份文件、跨两层集合运算的形状, 要整段复算才看得见。尤其 4 处日期⇎3 处条款⇎2 句谓词这三样, 任何单窗口都装不下它们的对照。读它请按“这句话住在哪一层、谁去读它”来读, 而不是按“少抄了多少原文”。

## ⛓解读注

**这四份数是怎么来的**: 时效表 `corpus/raw/tz/zonenow.tab` ⇎ 姊妹表 `zone1970.tab` ⇎ 检查器 `checknow.awk` ⇎ 构建配方 `Makefile`, 字节 8425 ⇎ 17592 ⇎ 1212 ⇎ 56501; 同目录的 `zone.tab`(418 行数据)与 `version` 只进集合与口径对照, 不作锚源。同一个数由三套独立实现各算一遍再对齐: 采集侧 `corpus/_pick52.py`(落 `corpus/_b52meas.json`, 附候选锚池 115 条供挑引文), 建条目侧 `corpus/_mkB52.py`(把要写进正文的每个数落成扁平契约 `corpus/_b52flat.json`, 172 枚键), 审计器侧 `corpus/audit.py::_b52_scan()`(只读四份 raw 与条目正文, 快照落 `corpus/_b52audit.json`)。
本注写这行时把三方又对齐了一次: 扁平契约 172 枚键(7 枚是逐源列表, 合计 193 个标量)在审计器快照里逐键等值, 无一失配; 审计器另算 7 枚只它自己有的键(`anchor_all4`、`anchor_cross`、`anchor_distinct`、`anchor_err`、`anchor_single`、`anchor_total`、`checks`), 其中锚统计由建条目侧从正文现推的 50 条去重串独立对账。`corpus/_wire52.py` 在把扫描器插进门槛之前先跑这同一场对账, 不符就当场停机, 所以门槛里那份 `_b52_scan` 与正文里的数不会是两套口径。
第四遍是本注自己写的: 不读上面任何 JSON, 直接从四份 raw 现取现算 68 组量(89 个标量——字节、行、列、集合交差、词频、配方片段内的字面计数), 与扁平契约逐一对上; 三遍互不相读而结果相同, 才敢说这些数没有口径漂移。

**第三档: 只能现跑, 不能进门槛**: 正文里那句“从现在起一致”要靠一份 zdump 输出表来判, 而库里 `*zdump*` 0 份、产物 `now.ck` 0 份, 门槛只能数出这两个零。判词本身到底会怎么走, 只有把 `checknow.awk` 真的跑一遍才知道, 于是本注现跑四遍(`GNU Awk 5.3.2, API 4.0, PMA Avon 8-g1, (GNU MPFR 4.2.2, GNU MP 6.3.0)`, 记账落 `corpus/_probe52_run.txt`):
① 照配方的样子把 `zdump_table` 指到一个不存在的路径(= 此刻这份库的真实状态)——gawk 6 秒内不返回, 强杀, 一行判词都没打印: 检查器的 BEGIN 写的是 `while (getline <zdump_table)`, 文件打不开时每次得 -1, 循环根本不退。这是“缺真值”的第二个含义: 不是判不出, 而是连判都不启动。
② 换成存在的空表——退出码 1, 打印 91 行“`%s: no data`”, 即 91 枚钟一枚也没被看过; 旁出文件不创建。
③ 换成本注现造的两钟表(Vancouver ⇎ Edmonton 从现在起同一串输出, `corpus/_probe52_syn2.tab`)——退出码 1, `no data` 89 行(=91-2) ⇎ `identical from now on` 1 行, 旁出文件 1 行。这一遍才看见它真正在比什么: 不是行与行的文字, 而是“输出序列的等价类”。
④ 换成 91 枚钟各一串互不相同输出的合成表(`corpus/_probe52_full.tab`)——退出码 0, 输出 0 行: 检查器本身完好, 库里跑不出判词纯粹因为缺那份真值输入。
这四遍依赖外部解释器与本机路径, 换机器就可能换结果, 所以一律不写进判词、不进门槛; 两份合成表是假数据, 不在四份源之列。

**锚的三口径**(正文“源标签紧接原子引文”的配对 56 处 ⇎ 跨标签去重 50 条 ⇎ 候选清单 50 条, 每标签 N:33 Z:4 K:10 M:9):
① 连空格与字形都不改的逐字命中其标注那一层的 50/50;
② 只折叠空白后命中 50/50;
③ 再加撇号引号剔除、连接号归一与大小写归一(即 `audit.py` 的 `prose_norm`)后命中 50/50。三口径在这批上完全重合(锚全部落在原文自己的字形与排版上), 留三口径是为了换一批抓取时能立刻量出引号/连接号/空白造成的失配条数。
命中列分布(按③对四份源逐一判成员, 共 200 次检查): 恰落一层 43 条 ⇎ 落多层 7 条 ⇎ 四层全落 0 条 ⇎ 错配 0 条。
“四层全落 = 0”是结构而不是巧合: 四份源是同一套分区的四层不同文体, 一条串若能同时落在表、姊妹表、awk 与配方里, 它必短到没有信息量; 反过来, 那 7 条多层串(`America/Vancouver` ⇎ `America/Edmonton` ⇎ `America/Winnipeg` ⇎ `America/Havana` ⇎ `Lord Howe Island` ⇎ `Pacific/Pago_Pago` 等)正是“同名不同层”的实证——同一个 `zdump_table`、同一句 from now on、同一个表名在标签层、程序层与配方层各写一遍, 正文按标签分别引用, 归属由正文现推而不是由旁注文件说了算。

**三档可核性落在哪**: 第一档 73 枚推导在门槛里逐枚复算(本条 DERIV 共 80 键, 其中 7 枚登记着没有单独写成数字的量, 审计器照样复算它们), 四份源的字节/行/列口径、组标签机器的 1:1、三层排序键的逆序(0/0/0)、缩写闭合三口径(42/42/42)、坐标两种宽度(75⇎16)、检查器与配方的每处计数都在这一档。第二档只能由集合运算得出: 时效表的 91 枚时区名是姊妹表 `zone1970.tab` 的真子集(后者多 221 枚, 反向一枚也不多), 同样是 `zone.tab` 的子集(它多 327 枚); 两表与时效表共有的 91 枚里坐标全同 91 枚而国码全不同 0 枚; 四种粒度的共有量 0⇎91⇎91⇎49(依次是逐行 ⇎ 坐标 ⇎ 时区名 ⇎ 上行串)。第三档就是上面那四遍现跑——它与 B48/B49 的分界正在于此: B48 的产物可重建、B49 的不变量可回交机检, 本条的谓词既不入库又随墙钟漂移(3 处 `$$now`, 起点 4 项前置在库里缺着), 所以正文把它写成判词而不是待核项, 门槛里也没有一项替它背书。

**digest 侧**: 摘要段四节(`### ⟦标签⟧ ⟸ 文件`), 含换行 3320 字符(审计表“摘要段”一栏就是这个数), 去换行 3234; 编码区去换行 8044。于是“vs 摘要段”按表口径 242.3% ⇎ 按两侧都去换行 248.7%——两栏之差只是 86 枚换行的归属, 两个数在此都登记; 而编码区对四份源全文(83631 字符)是 9.62%。这个比例是本条的形状所在: 结论不住在窗口里——“组织键住在被跳过的那一层”“三级排序零违例”“缺口 10 分三类”“真值输入在库 0 份”都要跨四层做集合运算才成立, 摘要窗口只装得下它们的引文证据, 而且窗口把制表符折成空格——87 行里带制表符的 0 枚, 两份表原文却有 410 行带制表符; 于是列结构在 digest 里根本看不见, 两种坐标宽度、组标签与三层排序键都只能靠编码区的引文加集合运算复算, 而不是靠读窗口看出来的。

**同一个数的不同含义**(同值冲突 92 次登记、铺在 24 个值上, DERIV 一个值只留一枚键, 所以下面这些说法在门槛里会互相顶掉, 只能靠注里的上下文区分): 值 1 由 21 处不同事实共用(gapspace、twopar、step05、step2、pred70、col1kind…)；值 2 由 16 处不同事实共用(stepneg1、minutes、dateskinds、pred、nowph、kcom…)；值 3 由 11 处不同事实共用(expire、untillines、kstatus、kzonedata、kext、kunset…)；值 91 由 10 处不同事实共用(tags、rows、c4_kind、coordeq、shared、nowrows…)。最扎眼的是 值 1, 上面那串键名翻成事实就是: 它在 21 处不同的事实现场成立(半小时 DST 步长 1 组 ⇎ 两小时步长 1 组 ⇎ 一枚以上括号的行 1 处 ⇎ 非注释才处理的谓词 1 枚 ⇎ mkdir 1 次 ⇎ 表名在检查器里 1 次……)。零同样拥挤: `%s` 一枚键折 29 个零项(三层逆序 0 ⇎ 偏移出现在数据列 0 次 ⇎ 国码一致 0 ⇎ 层内五词串 0 ⇎ zdump 表在库 0 份 ⇎ now.ck 0 份 ⇎ 检查器里 “zdump-now” 0 次 ⇎ 锚四源全中 0 ⇎ 锚错配 0 等), 它们合起来才是本条最硬的一句“能判它的那份文件不存在”。

**跑法**: `python -X utf8 corpus/audit.py` ⇒ B52 行 T1 编码失配 0 ⇎ T2 原文失配 0 ⇎ T3 码位 0 ⇎ 小整数待核 0; 门槛 PASS, 全库 52 条, 软提示 17 枚。
`python -X utf8 corpus/atomcheck.py B52 corpus/_atoms52.txt` ⇒ ok=50 bad=0(工具侧独立实现的逐字校验)。
`python -X utf8 corpus/_wire52.py` 重复运行先摘旧块再插新块(幂等), 且插门前把扁平契约 172 枚键与 DERIV 80 条算式在刚写好的扫描器上预演一遍, 值不符就当场停机。
`python -X utf8 corpus/_fill52.py` 即本注: 每次都重跑三遍对齐、四遍现跑与门槛, 所以这段里的数不是手填的, 也不能过期。