# B49 表 ⇎ 检查这张表的程序 ⇎ 它检查的数据：规矩写在程序里，程序写在破坏里

src: corpus/raw/tz/zone1970.tab (zone1970.tab, 312 行数据 = 四列 201 ⇎ 三列 111; 首码相邻 相等 158 ⇎ 变大 153 ⇎ 变小 0, 整列字面乱序 6 处而首码全相等; 坐标 分形式 265+秒形式 47+不合 0, 国家码引用 423 次去重 247 种, 码表 249 行里未被引用 2 种; 口径内 14482 字符 ⇎ 全文 17536 ⇎ 磁盘 17592 字节, 注释 63 行被口径剔掉(其中“当且仅当”等散文在口径内 0 处), 非 ASCII 38 枚其中 18 枚在注释, 真制表符 833 ⇎ 口径 825, sha256 5f23781702bf51408ff1581daa109ab3b9257fb433b1554e579d92172892c0cf) ⇎ corpus/raw/tz/checktab.awk (checktab.awk, 228 行 awk: printf 18 条 ⇎ 拼全相邻字面量 17 种诊断文本 ⇎ 17 条置失败码 ⇎ 14 条走 stderr ⇎ 4 条走 stdout ⇎ 15 条带“表名:行号”而 3 条只带名字; FS 两次赋值 ⇎ 两张表用 getline 在循环外读入并自建计数器; 口径内 4967 字符 ⇎ 全文 5377 ⇎ 磁盘 5377 字节(纯 ASCII: 字符=字节), sha256 e7d73e141ce815779d42d05ba71dcd88bcdc62f87542f2e15f78ec8207e6112c) ⇎ corpus/raw/tz/europe (europe, 4212 行 = 行首注释 2890 ⇎ 缩进注释 7 ⇎ 空行 295 ⇎ 非注释 1020(Zone 65 ⇎ Rule 515 ⇎ 续行 440 ⇎ Link 0); STDOFF 受检 505 值全合, 规则名定义 30 种全无未用、带字母 29 种全有 % 用法、恰用一次 13 种, 幻影键 3 枚; 口径内 40303 字符 ⇎ 全文 187806 ⇎ 磁盘 188472 字节, 非 ASCII 666 枚, sha256 fec11bf6c6bd0619a8777bbdaa2ecd184fde291cb4b97efa87d334c7145ba3c2)
；联结是“定义权”而非因果: 本机 gawk 5.3.2 对十份数据跑基线得 exit 0 且两条流各 0 字节; 反向对照逐条破坏(表侧 7 ⇎ 码表侧 5 ⇎ 数据侧 5 ⇎ 还原 1)与码侧变异 12 类(换比较符 / 改豁免串 / 坏守卫条件 / 关记录) 分别得 0 ⇎ 1 ⇎ 2 ⇎ 3 ⇎ 158 ⇎ 249 ⇎ 312 行诊断, 其中 158 = 相邻相等首码对数 ⇎ 249 = 码表行数 ⇎ 312 = 表行数——执行结果属工具侧断言, 逐条见 ⛓解读注; 形状数由 audit.py 里的 B49_* 从三份 raw 复算
tags: 定义权 ⇎ 不变量 判决即空输出 反向对照 码侧变异 比较符=容忍度 iff贴边 两种定位符宽度 stdout上的错误 聚合键 豁免按配置分死活 FS两层 注释三口径 字符⇎字节⇎口径

## [[原始语料|ORIGINAL]]
### ⟦T⟧ ⟸ corpus/raw/tz/zone1970.tab

civil timestamps have agreed since 1970. Columns are separated by # a single tab. Lines beginning with ‘#’ are comments. All text uses # UTF-8 encoding.

# 4. Comments; present if and only if countries have multiple timezones, # and useful only for those countries.

# # If a timezone covers multiple countries, the most-populous city is used, # and that country is l

are listed alphabetically by country code. The table is sorted # first by country code,

# #country- #codes coordinates TZ comments AD +4230+00131 Europe/Andorra AE,OM,RE,SC,TF +2518+05518 Asia/Dubai Crozet AF +3431+06912 Asia/Kabu

AQ -6736+06253 Antarctica/Mawson Mawson AQ -6448-06406 Antarctic

AQ -720041+0023206 Antarctica/Troll Troll AQ -7824+10654 Antarctic

CH,DE,LI +4723+00832 Europe/Zurich Büsingen CI,BF,GH,GM,GN,IS,ML,MR,

ZA,LS,SZ -2615+02800 Africa/Johannesburg # # The next section con

### ⟦C⟧ ⟸ corpus/raw/tz/checktab.awk

Check tz tables for consistency. # Contributed by Paul Eggert.

BEGIN { FS = "\t" if (!iso_table) iso_tab

if (!want_warnings) want_warnings = -1 monthabbr["Jan"] = 1 monthabbr["Feb"] = 1 mon

while (getline <iso_table) { iso_NR++ if ($0 ~ /^#/) continue if (NF != 2) { printf "%

if (cc <= cc0) { if (cc == cc0) { s =

while (getline <zone_table) { zone_NR++ if ($0 ~ /^#/) continue if (NF != 3 && NF != 4) { printf "%s:%d: wrong

printf "%s:%d: %s: duplicate Zone from line %d\n", \ zone_table, zone_NR, tz, tz2NR[tz] status = 1 } # Don't complain about a special case for Crimea in zone.tab.

if (cc < cc0 \ && !(zone_table == "zone.tab" \ && tz0 == "Europe/Simferopol")) { printf "%s:%d: coun

tz2NR[tz] = zone_NR for (i in cca) { cc = cc

printf "%s:%d: %s: unknown country code\n", \ zone_table, zone_NR,

printf "%s:%d: %s: invalid coordinates\n", \ zone_table, zone_NR,

if (used_max <= 1 && comments && zone_table != "zonenow.tab") { printf "%s:%d: unnec

printf "%s:%d: missing comment for %s\n", \ zone_table, i, used_

1 ~ /^#/ { next } { tz = rules = stdoff

printf "%s:%d: tricky month: %s\n", FILENAME, FNR, $6 \ >>"/dev/stderr" status

printf "%s:%d: unlikely STDOFF: %s\n", FILENAME, FNR, stdoff \ >>"/dev/stderr" status = 1 } if (tz && tz ~ /\// && tz !~ /^Etc\//) { if (!tztab[tz] && FILENAME != "backward" \ && zone_table != "zonenow.tab") { printf "%s: no data for '%s'\n", zone_table, tz \ >>"/dev/stderr" status

printf "%s: Rule never used\n", tz status = 1 } } for (tz i

printf "%s: Rule contains letters never used\n", tz status = 1 } } for (tz i

printf "%s:%d: no Zone table for '%s'\n", \ zone_table, tz2NR[tz

no Zone entries for %s (%s)\n", \ iso_table, cc2NR[cc], cc, cc2name[cc] } } } exit status }

### ⟦Z⟧ ⟸ corpus/raw/tz/europe

Zone Europe/London -0:01:15 - LMT 1847 Dec 1 0:00 GB-Eire %s 1968 Oct

fsets are correct and this often # suffices....

Rule Eire 1971 only - Oct 31 2:00u -1:00 - Rule Eire 1972 1980 - Ma

Rule Albania 1940 only - Jun 16 0:00 1:00 S Rule Albania 1942 only -

Zone Europe/Tirane 1:19:20 - LMT 1914 1:00 - CET 1940 Jun 16 1

Zone Atlantic/Faroe -0:27:04 - LMT 1908 Jan 11 # Tórshavn 0:00 - WET 1981 0:00 EU

Rule SovietZone 1945 only - May 24 2:00 2:00 M # Midsummer Rule SovietZone 1945 onl

Zone Europe/Athens 1:34:52 - LMT 1895 Sep 14 1:34:52 - AMT 1916 Jul 2

2:00 - EET 2001 Jan 2 2:00 EU EE%sT # Lithuania # From Paul Eggert (2016-03-18): # The 1989 transition is from USSR act No.

## ⟪BabelTele⟫
🧭 体例 ⟦T⟧⟨#codes	coordinates	TZ	comments⟩ ‖ ⟦C⟧⟨	exit status⟩ ‖ ⟦Z⟧⟨Zone	Europe/London	-0:01:15 -	LMT	1847 Dec  1⟩ ⇒ 三个源不是同一条链上的三站, 而是同一件事的三个角色: 表 ⟦T⟧⟨#codes	coordinates	TZ	comments⟩(312 行数据: 带注释 201 ⇎ 不带注释 111, 即四列 ⇎ 三列两种形状) ⇎ 检查器 ⟦C⟧⟨	exit status⟩(228 行 awk, 18 条 printf, 拼全续行后 17 种诊断文本) ⇎ 被它检查的数据 ⟦Z⟧⟨Zone	Europe/London	-0:01:15 -	LMT	1847 Dec  1⟩(4212 行 = 行首注释 2890 ⇎ 缩进注释 7 ⇎ 空行 295 ⇎ 非注释 1020, 其中 Zone 65 ⇎ Rule 515 ⇎ 续行 440 ⇎ Link 0)。与上一条“输入 ⇎ 程序 ⇎ 产物”不同: 这里的程序**不产出文件**, 它的唯一输出是判决, 而判决的正常形态是空——干净运行 exit 0 且两条流各 0 字节(命令、版本与逐条破坏的输出写在 ⛓解读注, 属工具侧断言)。于是可核性又长出一环: 记号可数 ⇎ 展开复算 ⇎ 执行复现 ⇎ **反向对照**(原料逐字节复制进临时目录, 既破坏数据也破坏程序, 看它精确报出哪一行、走哪条流)。审计口径从三份原料各剔注释 63 ⇎ 7 ⇎ 2897 行, 口径内留 14482 ⇎ 4967 ⇎ 40303 字符(数据侧那个“缩进注释 7”与检查器被剔的 7 行同数, 是巧合不是同一件事)。
✂️ 表把语法写在被口径剔掉的那 63 行里 ⟦T⟧⟨# civil timestamps have agreed since 1970.  Columns are separated by⟩ ‖ ⟦T⟧⟨# 4.  Comments; present if and only if countries have multiple timezones,⟩ ‖ ⟦T⟧⟨# are listed alphabetically by country code.  The table is sorted⟩ ‖ ⟦C⟧⟨		if (cc <= cc0) {⟩ ⇒ 表的注释把自己的写法讲得很清楚: ⟦T⟧⟨# civil timestamps have agreed since 1970.  Columns are separated by⟩(列用单个制表符分隔) ⇎ ⟦T⟧⟨# 4.  Comments; present if and only if countries have multiple timezones,⟩(第 4 列“当且仅当”) ⇎ ⟦T⟧⟨# are listed alphabetically by country code.  The table is sorted⟩(按国家码排序) ⇎ ⟦T⟧⟨# If a timezone covers multiple countries, the most-populous city is used,⟩(取最大城市)。这些句子在**审计口径里全是 0**, 在全文里各 1 处(“populous” 那组 2 处); 而程序里它们的字面也全是 0——程序不引用表的散文, 它另写一套: 制表符写成真制表符(全文件 404 枚, 口径 394 枚), “当且仅当”拆成两条支路 ⟦C⟧⟨	  if (used_max <= 1 && comments && zone_table != "zonenow.tab") {⟩ 与 ⟦C⟧⟨	    printf "%s:%d: missing comment for %s\n", \⟩, 排序只剩一个比较符 ⟦C⟧⟨		if (cc <= cc0) {⟩。反方向也空: 拼全后的 17 种诊断文本没有一个字面出现在表的口径里; 只有 ⟦C⟧⟨		if (NF != 3 && NF != 4) {⟩ 这种通用句在程序里写了 2 遍(两条循环各一遍)——它正是“文本 17 种 ⇎ 发射点 18 个”那 1 之差的全部来源。判词: 一份表有两种规格——散文版给人读, 运算符版给机器执行, 两者用词互不见; 要证明“程序真的照散文检查”, 搜词一行也证不了, 只能复算或破坏。
📐 排序的宽容住在一枚比较符里 ⟦T⟧⟨AQ	-6736+06253	Antarctica/Mawson	Mawson⟩ ‖ ⟦T⟧⟨AE,OM,RE,SC,TF	+2518+05518	Asia/Dubai	Crozet⟩ ‖ ⟦C⟧⟨		if (cc < cc0 \⟩ ‖ ⟦C⟧⟨		if (cc <= cc0) {⟩ ⇒ 程序对“排好序”的要求只有这么多: ⟦C⟧⟨		if (cc < cc0 \⟩ —— 取每行**第一个**国家码, 只报“比上一行小”。在这份表上相邻首码是 相等 158 ⇎ 变大 153 ⇎ 变小 0(312 行给出 311 个相邻对, 三数之和的等式在 0 键)。整列字面比较却有 6 处“乱序”: 例如 ⟦T⟧⟨AQ	-6736+06253	Antarctica/Mawson	Mawson⟩ 排在 ⟦T⟧⟨AE,OM,RE,SC,TF	+2518+05518	Asia/Dubai	Crozet⟩ 之后——首码同为 AQ, 整列字面反而小; 这 6 处的首码无一例外全部相等(两个数在 0 键相等), 所以程序一行也没报。散文还写着后半句(国家内部按人口与地理), 那半句在程序里没有任何诊断文本接待。同一个程序紧挨着的另一条循环写的是 ⟦C⟧⟨		if (cc <= cc0) {⟩: 码表侧不许相等(相等即 duplicate), 表侧允许。两枚比较符谁也不能换成对方, 只能做实验量(工具侧): 把表侧的 < 改成 <=, 干净库当场报 158 行——恰是那 158 对相等首码; 把码表侧的 <= 改成 <, 一行不报(码表本无重复码)。判词: “这张表排好序了”至少有两种读数(首码非降 ⇎ 整列升序), 程序实现的是较弱那种; 较弱那种正是散文里“国家内部次序”自由度的容身之处——**运算符的必要性是数据的性质, 不是代码的性质**。
🔗 第 4 列是引用数的函数, 而且贴边无余量 ⟦T⟧⟨CH,DE,LI	+4723+00832	Europe/Zurich	Büsingen⟩ ‖ ⟦T⟧⟨ZA,LS,SZ	-2615+02800	Africa/Johannesburg⟩ ‖ ⟦C⟧⟨	  if (used_max <= 1 && comments && zone_table != "zonenow.tab") {⟩ ‖ ⟦C⟧⟨	    printf "%s:%d: missing comment for %s\n", \⟩ ⇒ 散文 ⟦T⟧⟨# 4.  Comments; present if and only if countries have multiple timezones,⟩ 说第 4 列“当且仅当国家有多时区时才出现”; 程序把它拆成两条: ⟦C⟧⟨	  if (used_max <= 1 && comments && zone_table != "zonenow.tab") {⟩(该无而有 ⇒ unnecessary) 与 ⟦C⟧⟨	    printf "%s:%d: missing comment for %s\n", \⟩(该有而无 ⇒ missing), 判据是“本行某个码被几行引用”。不看程序独立复算: 国家码共被引用 423 次、去重 247 种, 码表 249 行里未被任何表行引用的 2 种; 至少一个码跨多行的行 201 ⇎ 带注释的行 201 ⇎ 无注释的行 111, 两个方向的违规各 0 ⇎ 0; 更狠的是**余量** 0 —— 带注释而引用数不足的行数为 0, 即这条不变量在真数据上是贴边的, “unnecessary” 那一支在整份库上从未被走到, 只有凭空给 ⟦T⟧⟨ZA,LS,SZ	-2615+02800	Africa/Johannesburg⟩ 那样的行加一枚注释它才开口(注里有那次运行)。跨行引用与注释还差一层: 程序要**读完整个表循环**才知道引用数, 于是这段判断写在循环之外, 用 input_ccs / input_comments 两张数组整表回填, 行号取自自建的 zone_NR 而不是文件行号。判词: iff 型不变量要报三件事——两边各几枚违规、单侧余量几行、以及实现它需要多少事后状态; 只报“201 ⇎ 201 相等”会把“贴边”与“宽松”混为一谈。
🗂 发射点、文本种数与流向是三套账 ⟦C⟧⟨		  printf "%s:%d: %s: duplicate Zone from line %d\n", \⟩ ‖ ⟦C⟧⟨			printf "%s: no data for '%s'\n", zone_table, tz \⟩ ‖ ⟦C⟧⟨			printf "%s: Rule never used\n", tz⟩ ‖ ⟦C⟧⟨		tz2NR[tz] = zone_NR⟩ ⇒ 18 条 printf 分三层数: 拼全相邻字面量后是 17 种文本(差的 1 条就是 ⟦C⟧⟨		if (NF != 3 && NF != 4) {⟩, 两条循环各写一遍); 按流分 ⟦C⟧⟨			printf "%s: no data for '%s'\n", zone_table, tz \⟩ 那 14 条 ⇎ 直接进 stdout 的 4 条; 按失败码分 17 条写 status = 1 ⇎ 1 条不写。“错”与“走哪条流”因此无关: 原地复制一行表(工具侧) ⇒ 失败码 1、stderr 0 行、stdout 1 行, 那句是 ⟦C⟧⟨		  printf "%s:%d: %s: duplicate Zone from line %d\n", \⟩ ——只读 stderr 的调用方会看见“毫无诊断却失败”。定位符分两种宽度: 15 条带“表名:行号” ⇎ 3 条只带名字(⟦C⟧⟨			printf "%s: no data for '%s'\n", zone_table, tz \⟩ 与 END 的 ⟦C⟧⟨			printf "%s: Rule never used\n", tz⟩); 前者里数据侧错误用 FILENAME/FNR(⟦C⟧⟨		  printf "%s:%d: tricky month: %s\n", FILENAME, FNR, $6 \⟩、⟦C⟧⟨		printf "%s:%d: unlikely STDOFF: %s\n", FILENAME, FNR, stdoff \⟩), 表侧用自建 zone_NR, 还有一支在 END 里回查 ⟦C⟧⟨		tz2NR[tz] = zone_NR⟩ 才凑出行号, 码表侧同构地用 cc2NR。判词: “程序说了什么”按文本种数记账, “怎么找到说话对象”按定位符宽度记账, “送到哪里”按流记账; 三套账混成一套就会得出“错误都到 stderr”这种错话。
🧪 一条不变量一枚诊断: 破坏分三档 ⟦C⟧⟨			printf "%s:%d: %s: invalid coordinates\n", \⟩ ‖ ⟦C⟧⟨		printf "%s:%d: unlikely STDOFF: %s\n", FILENAME, FNR, stdoff \⟩ ‖ ⟦C⟧⟨		  printf "%s:%d: tricky month: %s\n", FILENAME, FNR, $6 \⟩ ‖ ⟦T⟧⟨AQ	-720041+0023206	Antarctica/Troll	Troll⟩ ⇒ 把 17 种诊断文本当作不变量的枚举, 每种各造一次破坏(破坏串一律取自真实行, 原料逐字节复制进临时目录), 结果按三档分: **局部形状类**一触一报——秒形式坐标 ⟦C⟧⟨			printf "%s:%d: %s: invalid coordinates\n", \⟩ 那种(表里 47 行用秒形式 ⇎ 265 行用分形式 ⇎ 不合式 0 行)里插一位、表的第 4 列加一枚野注释、码表某行多一列, 各报一行 ⟦C⟧⟨		if (NF != 3 && NF != 4) {⟩ 型; STDOFF 改坏报的是**数据文件**的行号(本文件受检的 STDOFF 值 505 个全部合式, 见 ⟦Z⟧⟨Zone	Europe/Athens	1:34:52 -	LMT	1895 Sep 14⟩); 月列改成非月名 ⇒ ⟦C⟧⟨		  printf "%s:%d: tricky month: %s\n", FILENAME, FNR, $6 \⟩。**关系类**会级联: 把一个码换成不存在的 QQ, 除了 ⟦C⟧⟨			printf "%s:%d: %s: unknown country code\n", \⟩ 还连带把下一行挤成乱序; 把码表首字母改小写同时触发码形与排序两条。**全局聚合类**要挑对下手点(见下条)。还原之后重新运行仍是两条流各 0 字节——电池没留下痕迹。判词: 诊断行数与破坏大小不成比例, “报了几行”不能当严重度, 必须按不变量的类型分列报告; 而“哪些形状根本没被检查”要反过来问: 表 312 行里四列 201 ⇎ 三列 111, 列数只被允许这两种, 第五种形状在程序里没有文本接待它。
📏 聚合型不变量的可破坏点是“最后一根支持者” ⟦Z⟧⟨Rule	Albania	1940	only	-	Jun	16	0:00	1:00	S⟩ ‖ ⟦Z⟧⟨Rule	Eire	1971	only	-	Oct	31	 2:00u	-1:00	-⟩ ‖ ⟦C⟧⟨			printf "%s: Rule contains letters never used\n", tz⟩ ‖ ⟦C⟧⟨			printf "%s: Rule never used\n", tz⟩ ⇒ END 的三条支路按**名字**聚合: 十份数据共定义规则名 135 种, 全部被用到(定义未用 0 种); 带字母的 103 种全部有带 % 的用法(字母而无 % 者 0 种; 定义与带字母之差 32 枚就是不带字母的规则名)。本文件单看: 定义 30 种 ⇎ 带字母 29 种 ⇎ 恰被用一次 13 种, 其中不带字母的只有一个, 就是 ⟦Z⟧⟨Rule	Eire	1971	only	-	Oct	31	 2:00u	-1:00	-⟩ 那一族。我第一次破坏选的是定义行: 把某条 Rule 的字母列改成别的字母 ⇒ 不报错, 因为同名规则的另一行早已把字母登记进 ruleLetters, 聚合表看不出差别——**破坏一个聚合不变量不能改它的任意一支支持者**。正确的点是它唯一那次用法: ⟦Z⟧⟨Rule	Albania	1940	only	-	Jun	16	0:00	1:00	S⟩ 这类行的格式列里 %s 换成普通串 ⇒ stdout 一行 ⟦C⟧⟨			printf "%s: Rule contains letters never used\n", tz⟩; 再把一个恰用一次且不带字母的名字换成 - ⇒ ⟦C⟧⟨			printf "%s: Rule never used\n", tz⟩, 两条都只报名字不报行号。顺带: 程序把**每一行续行**的第 2 列都当规则名登记, 于是 ruleUsed 里混进 3 枚从未定义过的幻影键(本文件续行 440 行, 大多是年份或 -); 这不是 bug, 因为 END 只遍历 ruleDefined ——“幻影键无害”依赖另一条不变量, 这层依赖只在读代码时才看得见。判词: 行级编辑与名级聚合之间隔着一张哈希表; 逐行读原文与搜词都找不到“谁是最后一根支持者”, 只能把聚合关系复算出来。
🫥 程序替另外两张表写着豁免, 而它们在当前配置下是死的 ⟦C⟧⟨			 && tz0 == "Europe/Simferopol")) {⟩ ‖ ⟦C⟧⟨		if (!tztab[tz] && FILENAME != "backward" \⟩ ‖ ⟦C⟧⟨	if (tz && tz ~ /\// && tz !~ /^Etc\//) {⟩ ‖ ⟦T⟧⟨AE,OM,RE,SC,TF	+2518+05518	Asia/Dubai	Crozet⟩ ⇒ 程序里点名了别的表: ⟦C⟧⟨			 && tz0 == "Europe/Simferopol")) {⟩ 型判断 2 处(zone.tab 的 Crimea 特例与 Link 支)、zonenow.tab 3 处(XX 码豁免、注释规则豁免、zoneSeen 豁免)、⟦C⟧⟨		if (!tztab[tz] && FILENAME != "backward" \⟩ 1 处、特例名 ⟦C⟧⟨			 && tz0 == "Europe/Simferopol")) {⟩ 1 处。三张表都真跑过(工具侧): 配 zone1970.tab ⇎ zone.tab ⇎ zonenow.tab 的基线**各**是两条流 0 字节; 把特例字符串改坏并以 zone.tab 运行 ⇒ 恰好 1 行, 报在第 337 行, 而 ⟦T⟧⟨AE,OM,RE,SC,TF	+2518+05518	Asia/Dubai	Crozet⟩ 那行住在第 336 行——豁免写在**前一行**身上, 报的是**后一行**(RU 排在 UA 之后, 全表 418 行仅此一处需要它); 把 ⟦C⟧⟨		if (!tztab[tz] && FILENAME != "backward" \⟩ 的豁免改坏 ⇒ 0 行, 因为在 zone1970 配置下 Link 支整条不执行(它自己也被 zone.tab 守卫): 本文件的 Link 行 0 处, 于是这条支路在两个层面上都是死的。更狠的一枚: ⟦C⟧⟨	if (tz && tz ~ /\// && tz !~ /^Etc\//) {⟩ 那条件同时守着数据→表与表→数据两个方向, 把它改坏后 zoneSeen 不再登记, END 对表里全部 312 个名字各报一次 ⟦C⟧⟨			printf "%s:%d: no Zone table for '%s'\n", \⟩, 而“no data for”同时归零——一条条件, 一灭整个方向。判词: 死支要按**当前调用配置**说, 不能按文件全局说; 一条豁免的价值等于它救下的行数, 而这个数只能执行出来, 读代码只会得到“这里有特例”而不知其权重。
🔀 两次 FS 切换、注释的三种口径与数据的两种分隔符 ⟦C⟧⟨	FS = "\t"⟩ ‖ ⟦C⟧⟨	FS = " "⟩ ‖ ⟦C⟧⟨$1 ~ /^#/ { next }⟩ ‖ ⟦Z⟧⟨			2:00	-	EET	2001 Jan  2⟩ ⇒ 程序里有 2 次 FS 赋值: BEGIN 开头 ⟦C⟧⟨	FS = "\t"⟩, BEGIN 结尾 ⟦C⟧⟨	FS = " "⟩。两张表用 ⟦C⟧⟨	while (getline <iso_table) {⟩ ⇎ ⟦C⟧⟨	while (getline <zone_table) {⟩ 在循环外读入, 并自建计数器(1 处 ⇎ 1 处)——因为 NR 要留给 10 份数据文件。切换的后果是 NF 的含义翻面: 表侧 NF 是形状不变量(201 行四列 ⇎ 111 行三列, 口径内制表符 825 枚 = 201×3+111×2), 数据侧 NF 毫无意义——行尾注释也是字段; 而“空白成串即一列”的劈法给了数据写法自由度: 本文件 65 个 Zone 行里 29 个用制表符分开首两列 ⇎ 36 个用空格, 515 个 Rule 行是 503 ⇎ 12(⟦Z⟧⟨Rule SovietZone	1945	only	-	May	24	2:00	2:00	M # Midsummer⟩ 那行就用空格), 把这些行挪到表侧的 FS 下立刻不满足 ⟦C⟧⟨		if (NF != 3 && NF != 4) {⟩; 行首带制表符的线共 447 条 = 续行 440 + 缩进注释 7。注释的定义也不止一种: 表循环用 ⟦C⟧⟨		if ($0 ~ /^#/) continue⟩ 那种整行行首式 2 处(同一条语句在两处逐字重复), 主规则用 ⟦C⟧⟨$1 ~ /^#/ { next }⟩ 第一列式 1 处; 本文件里以制表符缩进再以 # 开头的注释恰好 7 行——按第一列它们仍是注释, 按行首它们不是。我第一版复算就按行首过滤, 得到 1027 行非注释 ⇎ 照程序的定义 1020 行, 差的正是这 7 行; 而审计口径(去掉前导空白再匹配)与程序一致: 剔除 2897 = 行首 2890 + 缩进 7。顺带一枚同名不同命: 程序的月表 ⟦C⟧⟨	monthabbr["Jan"] = 1⟩ 定 12 个名字, 本文件的 Rule 行只用 11 个(缺 Jan), 十份数据合起来才用满 12 个——而 ⟦Z⟧⟨			2:00	-	EET	2001 Jan  2⟩ 那种 Jan 坐在续行的 until 段里(续行的第 4 列起才是日期), 程序只对 Rule 行的第 6 列查月名, 于是那一次也没被看过。判词: 同一份数据在不同 FS 下是两种文本; “注释行”有三种彼此不同的口径, 复算前必须选定一种并写明, 否则 1027 与 1020 都会“正确”, 只是不在同一件事上正确。
🌐 字符 ⇎ 字节 ⇎ 口径: 三层各有各的差 ⟦T⟧⟨# a single tab.  Lines beginning with ‘#’ are comments.  All text uses⟩ ‖ ⟦C⟧⟨	if (!want_warnings) want_warnings = -1⟩ ‖ ⟦T⟧⟨#codes	coordinates	TZ	comments⟩ ⇒ 表的散文 ⟦T⟧⟨# a single tab.  Lines beginning with ‘#’ are comments.  All text uses⟩ 声明“全部文本用 UTF-8”, 而程序对此 0 处校核(“UTF” 在程序内 0 处)。字节层能核: 检查器 5377 字符 ⇎ 5377 字节(纯 ASCII, 两层相等); 表 17536 字符 ⇎ 17592 字节, 差 56, 而全文非 ASCII 字符 38 枚 ⇒ 差不等于枚数, 因为里面混着三字节排版符: 设双字节 x 枚、三字节 y 枚, x+y=38 ⇎ x+2y=56 ⇒ y 由这两数相减得出(等式在 0 键); 数据 187806 字符 ⇎ 188472 字节差 666 而它恰有非 ASCII 666 枚 ⇒ 每枚多 1 字节, 全为双字节。同一批字符再切一层: 表的非 ASCII 口径内只剩 18(其余住在注释里), 数据剩 2 枚、只住在 2 行的**行尾**注释里(⟦Z⟧⟨Zone Atlantic/Faroe	-0:27:04 -	LMT	1908 Jan 11 # Tórshavn⟩ 那两行的地名带 ó 与 å)——搜“人名里的重音字母”在口径内几乎搜不到, 而它正是这份语料被采集的理由(口径内那两个数各与别的量巧合同值, 是三回事)。转义层照例要点名: 程序里真制表符 404 枚(缩用) ⇎ 口径 394 枚 ⇎ 字面反斜杠 t 仅 1 枚(就是 ⟦C⟧⟨	FS = "\t"⟩ 那一行); 格式符 %s 35 枚 ⇎ %d 16 枚, 报文文本都靠它们拼装。判词: “同一份文件”至少有三层长度(口径 ⇎ 全文字符 ⇎ 磁盘字节), 每层的差各有各的成因(注释 ⇎ 编码宽度); 报数时哪一层要写出来, 否则 666 与 56 会看着像同一种东西。
⚖ 告警是唯一不置失败码的输出, 而其默认值让整条支路死掉 ⟦C⟧⟨					"no Zone entries for %s (%s)\n", \⟩ ‖ ⟦C⟧⟨	if (!want_warnings) want_warnings = -1⟩ ‖ ⟦T⟧⟨AD	+4230+00131	Europe/Andorra⟩ ⇒ 18 条发射里只有 ⟦C⟧⟨					"no Zone entries for %s (%s)\n", \⟩ 不写 status = 1(其余 17 条都写), 它也就不参与 ⟦C⟧⟨	exit status⟩。把开关打开(want_warnings=1)后运行仍 exit 0, 只是 stdout 多 2 行——内容恰好是“码表里没被任何表行引用的码”: 独立复算 2 枚, 与程序输出的行数相等(等式在 0 键; 其中一枚的表行形如 ⟦T⟧⟨CH,DE,LI	+4723+00832	Europe/Zurich	Büsingen⟩ 那样的多码行才把 BV 之外的码带进引用数)。而默认值 ⟦C⟧⟨	if (!want_warnings) want_warnings = -1⟩ 让整条支路在常规调用里 0 行: 同一个变量在程序里出现 3 次(缺省赋值、判断、循环各一)。更深一层: 告警的行号来自 cc2NR[cc] —— 那是码表循环结束时替每枚码记住的行号, 而 END 里遍历的是 `for (cc in cc2name)`: 哈希序, 于是两行告警的先后不保证与文件序一致(逐字节比较时要把这两行排序)。判词: 程序把“规矩”分成两级——违反即失败 ⇎ 只是提示, 而提示级默认关闭; “码表里有整行没人引用”正住在提示级, 所以只跑默认配置的读者会以为码表 249 行全都被用上了。
∴ 骨架 ⟦C⟧⟨	exit status⟩ ‖ ⟦T⟧⟨# 4.  Comments; present if and only if countries have multiple timezones,⟩ ‖ ⟦C⟧⟨		if (cc < cc0 \⟩ ‖ ⟦Z⟧⟨Zone	Europe/London	-0:01:15 -	LMT	1847 Dec  1⟩ ⇒ ① 检查器的产物是**空**: 干净运行两条流各 0 字节、exit 0, 所以它的“正确输出”没有正面证据, 只能靠反向对照取证; ② 表的语法有散文版与运算符版两套(全文 1 处 ⇎ 口径 0 处 ⇎ 程序内 0 处), 用词交集为空; ③ 排序读数有两层(首码非降 158+153 ⇎ 整列升序还多出 6 处), 程序实现较弱那层; ④ iff 型不变量要报违规数与**余量**(此处两个方向与余量皆 0), 贴边的真分支在只读数据的审计里隐形; ⑤ 报文三套账: 文本种数 17 ⇎ 发射点 18 ⇎ 流向 14/4, 错误可以走 stdout; ⑥ 定位符两种宽度 15/3, 同一句“列数不对”在两条循环里各写一次, 而“no data for”丢弃了行号; ⑦ 豁免按调用配置分死活(zone.tab 特例值 1 行 ⇎ backward 特例值 0 行), 一条条件可同时守两个方向(坏之则 312 行齐发); ⑧ 聚合型不变量只能破坏“最后一根支持者”(名而无行号), 且其无害性依赖另一条不变量(幻影键 3 枚); ⑨ FS 换两次 ⇒ NF 的含义翻面, 注释行三种口径差 7 行; ⑩ 字符/字节/口径三层, 差各有成因(666 ⇎ 56 的成因不同); ⑪ 提示级默认关(2 枚未引用码), 只跑默认配置会把提示级的账整个漏掉。判词: “表 ⇎ 检查表的程序”之间没有生成关系, 只有**定义权**: 哪一列合法、什么算有序、注释该不该在, 全由那 228 行里的 17 枚 ⟦C⟧⟨		  printf "%s:%d: %s: duplicate Zone from line %d\n", \⟩ 与几枚比较符决定; 报告它们必须同时报“代码写了什么 ⇎ 数据满足到什么程度”。
ℒ 方法 ⟦T⟧⟨# civil timestamps have agreed since 1970.  Columns are separated by⟩ ‖ ⟦C⟧⟨		if (cc <= cc0) {⟩ ‖ ⟦C⟧⟨		  printf "%s:%d: %s: duplicate Zone from line %d\n", \⟩ ‖ ⟦Z⟧⟨Zone	Europe/Tirane	1:19:20 -	LMT	1914⟩ ⇒ 读“表 ⇎ 检查这张表的程序 ⇎ 它检查的数据”: 第一步**先跑**, 不要先读——干净运行的 0 字节确立了基准, 此后每个数都是相对基准的偏离; 第二步把程序的发射点列成三套账(文本种数 17 / 发射点 18 / 流向 14+4), “17 种诊断文本”就是不变量的枚举, 比读控制流可靠; 第三步为每种不变量造一次破坏, 破坏串一律从真实行里取, 并按“局部 ⇎ 关系 ⇎ 全局聚合”分档记录它报几行、报哪一行、走哪条流; 第四步反过来破坏**程序**: 换一枚比较符、改一个字符串字面量、坏掉一条守卫条件, 数报文行数——这一步量出的是“数据对代码的容忍度”(相等首码 158 对 ⇎ 改符后报 158 行, 同一个数在 raw 侧与执行侧各得一遍) 与“每条豁免的权重”(1 行 ⇎ 0 行); 第五步所有形状数(行数列数、引用数、坐标两型、STDOFF 受检值)一律在**不看程序**的情况下复算, 再与程序的红绿灯对照, 差集就是散文与代码的分歧处。核验口径: ⟦T⟧⟨# civil timestamps have agreed since 1970.  Columns are separated by⟩ 一类表内散文按“全文”数(口径为 0), ⟦C⟧⟨		if (cc <= cc0) {⟩ 一类程序记号按口径数, ⟦C⟧⟨		  printf "%s:%d: %s: duplicate Zone from line %d\n", \⟩ 一类数据记号要注意缩进注释那 7 行(与审计口径的剔法一致, 与“行首字符”的剔法差 7)。
✂️ 为什么这份编码比摘要窗口长 ⟦C⟧⟨# Check tz tables for consistency.⟩ ‖ ⟦T⟧⟨#codes	coordinates	TZ	comments⟩ ‖ ⟦Z⟧⟨Rule SovietZone	1945	only	-	May	24	2:00	2:00	M # Midsummer⟩ ⇒ 三份原料的口径长度是 14482 ⇎ 4967 ⇎ 40303 字符: 检查器最小(228 行), 却独家持有全部 17 种诊断文本与两枚比较符; 表与数据都很大, 而它们**说出规矩**的部分恰是审计口径剔掉的注释行(63 行 ⇎ 2897 行)。摘要段只能取锚点触到的窗口 ⟦C⟧⟨# Check tz tables for consistency.⟩、⟦T⟧⟨#codes	coordinates	TZ	comments⟩, 但本条的结论不住在窗口里: “158 对相等首码恰好被 < 放过”“注释与引用两个方向各 0 违规且余量 0”“一条守卫条件同时决定两个方向的 312 行”, 这些要么要复算, 要么要执行, 要么要破坏。读它请按“四种可核性各占几项”来读, 而不是按“少说了多少原文”。与上一条同为 tz 材料而不同题: 那条比同一时刻上的三个角色(输入/程序/产物, 程序**产出字节**), 本条比同一份表上的**定义权归属**(程序只产出判决); 与本库另一条比同一名字在不同载体里的形态也不同——这里没有名字的形状, 只有形状的合法性。

## ⛓解读注
**怎么跑**: 本机 gawk 5.3.2(API 4.0) 按程序 BEGIN 里的默认取名——`gawk -f checktab.awk -v iso_table=iso3166.tab -v zone_table=<表名> -v want_warnings=0` 再跟十份数据文件 (africa antarctica asia australasia europe northamerica southamerica etcetera factory backward)。`iso_table ⇎ zone_table ⇎ want_warnings` 三个变量都有默认值, 命令行只决定"给哪张表定性"; 数据文件走 ARGV 由主规则逐行读, 两张表走 getline 在 BEGIN 里读。基线: zone1970.tab 与 zone.tab 都是 exit 0、stderr 0 字节、stdout 0 字节——判决的正常形态是空, 所以后面每张表都得先把东西改坏才看得见。

**数据侧逐条破坏**(每次只改一处, 其余还原; 表侧改 zone1970.tab, 码表侧改 iso3166.tab, 数据侧改 europe):

| 场景 | exit | stderr 行 | stdout 行 | 首条诊断 |
|---|---|---|---|---|
| oord | 1 | 1 | 0 | zone1970.tab:39: +4230+0013: invalid coordinates |
| order | 1 | 1 | 0 | zone1970.tab:40: country code 'AD' is out of order |
| misscomment | 1 | 1 | 0 | zone1970.tab:40: missing comment for TF |
| extracomment | 1 | 1 | 0 | zone1970.tab:39: unnecessary comment 'probe note' |
| unknowncc | 1 | 2 | 0 | zone1970.tab:42: QQ: unknown country code |
| fivecol | 1 | 2 | 0 | zone1970.tab:41: wrong number of columns |
| uprow | 1 | 0 | 1 | zone1970.tab:45: Antarctica/Casey: duplicate Zone from line 44 |
| extracol | 1 | 1 | 0 | iso3166.tab:35: wrong number of columns |
| lower | 1 | 3 | 0 | iso3166.tab:37: invalid country code 'am' |
| upcode | 1 | 2 | 0 | iso3166.tab:40: country code 'AQ' is duplicate |
| samename | 1 | 1 | 0 | iso3166.tab:41: 'AF' and 'AS' have the same name |
| swap | 1 | 1 | 0 | iso3166.tab:33: country code 'AE' is out of order |
| rename | 1 | 2 | 0 | zone1970.tab: no data for 'Europe/LondonX' |
| stdoff | 1 | 1 | 0 | europe:522: unlikely STDOFF: 44:00 |
| month | 1 | 1 | 0 | europe:417: tricky month: Foo |
| ruleunused | 1 | 0 | 2 | AlbaniaX: Rule never used |
| ruleletters | 1 | 0 | 1 | EireX: Rule never used |
| restore | 0 | 0 | 0 | — |

共 17 类(表侧 7 ⇎ 码表侧 5 ⇎ 数据侧 5)再加还原一次(还原: exit 0、两条流 0+0 字节)。多数场景只落 1 行诊断; 两处例外: 把首码换成码表里没有的 `QQ` 得 2 行(zone1970.tab:42: QQ: unknown country code), 多塞两列也得 2 行——一处破坏常同时踩中两条检查; 复制整行则得 1 行, 且它走 stdout 而非 stderr: zone1970.tab:45: Antarctica/Casey: duplicate Zone from line 44。

**码侧变异**(只动程序里的比较符与常量, 数据一律不动; 比较符就是数据被容忍的程度):

| 改动 | exit | stderr 行 | stdout 行 | 首条诊断 |
|---|---|---|---|---|
| lt | 1 | 158 | 0 | zone1970.tab:45: country code 'AQ' is out of order |
| lt zonetab | 1 | 169 | 0 | zone.tab:37: country code 'AQ' is out of order |
| lt noexempt | 1 | 170 | 0 | zone.tab:37: country code 'AQ' is out of order |
| exempt dead | 1 | 1 | 0 | zone.tab:337: country code 'RU' is out of order |
| backward | 0 | 0 | 0 | — |
| so lt | 0 | 0 | 0 | — |
| usedmax | 0 | 0 | 0 | — |
| nf3 | 1 | 249 | 0 | iso3166.tab:31: wrong number of columns |
| main etc | 1 | 28 | 0 | zone1970.tab: no data for 'Etc/UTC' |
| end etc | 0 | 0 | 0 | — |
| seen off | 1 | 312 | 0 | zone1970.tab:351: no Zone table for 'Africa/Johannesburg' |
| warn on | 0 | 0 | 2 | iso3166.tab:64: warning: no Zone entries for BV (Bouvet Island) |

一枚 `<` 换成 `<=` 把相邻相等的首码全判成越序: 158 行(zone1970.tab, top US×28 RU×26 CA×19 BR×15)。同一条改动落在 zone.tab 上是 169 行, 再把豁免串改成 `zone.tabZ` 就是 170 行——那条 Crimea 豁免的重量正好 1 行; 不动比较符、只改死豁免串仍得 1 行(zone.tab:337: country code 'RU' is out of order), 因为 zone.tab 本身严格递增, 豁免在此刻是空转的保险。
三处"改坏守卫却一行都不要"的对照: `FILENAME != "backward"` 改死 ⇒ 0 行; 码表顺序检查 `cc <= cc0` 收回 `cc < cc0` ⇒ 0 行(码表严格递增, 一枚比较符的余量为 0); `used_max <= 1` 收成 `< 1` ⇒ 0 行(注释的"多余"与"缺失"两检查一起哑火)。
两枚 Etc 守卫分居两地, 效果完全不对称: 主循环放行 Etc ⇒ 28 行 `no data for`(top Etc×28; 数据里有 Etc 名而表里没有); END 放行 Etc ⇒ 0 行(表里没有 Etc 名, 白改); 把主循环整个记录块关掉(`if (0 && ...)`, 于是 `zoneSeen[tz] = 1` 永不执行) ⇒ 312 行 `no Zone table for`, 恰为表行数, 前缀分布 America×121 Asia×74 Europe×38 Pacific×30, 首条 zone1970.tab:351: no Zone table for 'Africa/Johannesburg'——此时 `no data for` 一并消失, 因为它就写在同一个块里。
`want_warnings` 不改代码、只拧命令行开关(0 ⇒ 1): exit 0、stderr 0 行、stdout 2 行, 首条 iso3166.tab:64: warning: no Zone entries for BV (Bouvet Island)。警告不参与 `exit status`, 所以"全绿"的运行里可以已经躺着 2 行未命中的点位符——这一类是判决之外的旁白。

**行尾不是不变量**: 把副本改成 CRLF(zone1970.tab: exit 0、0+0 行 ⇎ iso3166.tab: exit 0、0+0 行 ⇎ europe: exit 0、0+0 行 ⇎ ALL3: exit 0、0+0 行 ⇎ checktab.awk: exit 0、0+0 行)——诊断全为 0。在 `FS="\t"` 之下每行末尾多出的 `\r` 会并进最后一列, 于是"顺序"比较变成带尾巴的比较, 所有检查一起哑火; 程序自身换成 CRLF 也一样哑(它照跑, 只是再也判不出坏)。顺带一个 Windows 陷阱: 变异副本必须二进制读写, 用文本模式写就等于每一步都先替上面这组实验铺好 `\r`。

**为什么这些数字只写在注里**: 执行结果不属于任何一份 raw, 它属于"这台机器上的 gawk 与这份副本"; 正文与 src 行里的每个形状数(158 ⇎ 249 ⇎ 312 ⇎ 1020⇎1027 ⇎ 29⇎36 ⇎ 503⇎12 ⇎ 447=440+7 ⇎ 18⇎17⇎15⇎14)都由 audit.py 里 B49V/B49_LINES/B49_DROP/B49_BYTES 从三份 raw 现算复验, 而上面两张表只由本注的 JSON 供数——两边一旦互相冒充(把 158 行诊断当成表形状, 或把 312 当成执行结果), 门槛立刻断。
