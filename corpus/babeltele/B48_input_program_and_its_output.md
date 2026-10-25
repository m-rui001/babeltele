# B48 输入 ⇎ 生成它的程序 ⇎ 程序的产物：三份文件讲同一件事，可谁都不按对方的写法写它

src: corpus/raw/tz/leap-seconds.list (NIST/IERS 的 leap-seconds.list, 数据 28 行, 行格式“NTP 秒 ⇎ DTAI ⇎ # 日 月 年”, 口径内 1035 字符 ⇎ 全文件 5065 字符 ⇎ 磁盘 5065 字节, 注释行 92 行被口径剔掉, 纯 ASCII(转义制表符 0 处而真制表符 66 处全在注释里), sha256 db5a895f16853b03bfc865e8d68f9fc8710ef1740e3400c701cd46a5bbbc3433) ⇎ corpus/raw/tz/leapseconds.awk (把它转成 zic 格式的 leapseconds.awk, 256 行, 发射语句 61 条(print 56 ⇎ printf 5), 口径内 6464 字符 ⇎ 全文件 9448 字符 ⇎ 磁盘 9448 字节, sha256 76c289f5827119e40f1451a96b04e4333f3c8d8b218e170a03c8432e72b3638c) ⇎ corpus/raw/tz/leapseconds (产物 leapseconds, 86 行(数据 27 行 ⇎ 头部 40 行由 BEGIN 逐行发射 ⇎ 尾部 19 行由 END 产出), 口径内 809 字符 ⇎ 全文件 3694 字符 ⇎ 磁盘 3694 字节, sha256 8f066f297a37a798d5103321957c5f5f4f1c9dda0f3d05db30b77bec3491659e)
；联结可执行复现: 本机 gawk 把程序跑在输入上所得与在库产物逐字节相同(版本、命令与散列等式见 ⛓解读注, 属工具侧断言); 展开复算的十个数(吻合 27/27 ⇎ 月改 27 ⇎ 年改 16 ⇎ 日改 27 ⇎ DTAI 连续 28 ⇎ BEGIN 按序 40 ⇎ 空行 5 ⇎ 纪元差 2208988800 ⇎ 间隔 30816903)由 audit.py 里的 B48_* 函数独立复算
tags: 因果链 ⇎ 可执行复现 语句×次数 列投影 差分符号 减一秒换算 词汇表 转义层 口径⇎全文 三向缺席

## [[原始语料|ORIGINAL]]
### ⟦I⟧ ⟸ corpus/raw/tz/leap-seconds.list

theoretically possible to have a negative leap second (a second removed from UTC), but so far, # all leap seconds have

and September. Since the introduction of leap seconds in 1972, only dates in June and December were used. # # Questions or comment

This file is in the public domain. # # # VALIDITY OF THE FI

Updated through IERS Bulletin C (https://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat) # # The following line

3992312697 # # 2) Expiration date o

File expires on 28 June 2027 # # Expire date in NTP timestamp: # #@ 4023129600 # # # LIST OF LEAP SECON

MJD: The Modified Julian Day number. MJD = X/86400 + 15020 # # DTAI: The difference

NTP Time DTAI Day Month Year # 2272060800 10 # 1 Jan 1972 2287785600 11 # 1 Jul 1972 2303683200 12 # 1 Jan 19

3692217600 37 # 1 Jan 2017 # # A hash code has been

h a9bad145 84c31c70 758402aa b37bfd54 5923836a

### ⟦A⟧ ⟸ corpus/raw/tz/leapseconds.awk

Generate zic format 'leapseconds' from NIST/IERS format 'leap-seconds.list'. # This file is in the public domain. # This program uses awk

exact integer arithmetic only through 10**10, which means for NTP # timestamps this progra

print "# Allowance for leap seconds added to each time zone file." print "" print "# This file is in the public domain." print "" print "# This file is generated automatically from the data in the public-domain" print "# NIST/IERS form

rotation. The first (\"1 Jan 1972\") data line in leap-seconds.list" print "# does not denot

All leap-seconds are Stationary (S) at the given UTC time." print "# The correction

Leap YEAR MON DAY 23:59:59 - S" print "# Typical lines look like this:" print "# Leap YEAR MON DAY 23:59:60 + S" monthabbr[ 1] = "Jan" monthabbr[ 2] = "Feb" m

monthabbr[ 6] = "Jun" monthabbr[ 7] = "Jul" monthabbr[ 8] = "Aug" m

t]*[Uu]pdated through/ || /^#[ \t]*[Ff]ile expires on/ { last_lines = last_lin

if (old_TAI_minus_UTC) { if (old_TAI_minus_UTC < TAI_minus_UTC) { sign = "23:59:60\t+" } else { sign = "23:59:59\t-" } sstamp_to_ymdhMs(NTP_timestamp - 1, ss_NTP) printf "Leap\t%d\t%s\t%d\t%s\tS\n", \ ss_year, monthabbr[s

printf "%sExpires %.4d\t%s\t%.2d\t%.2d:%.2d:%.2d\n", \ EXPIRES_LINE ? "" :

print "# (No Expires line, since the expires time is unknown.)" } # The difference bet

epoch_minus_NTP = ((1970 - 1900) * 365 + 17) * 24 * 60 * 60 print "" print "# Here a

print "#(updated time unknown)" } if (expires) { sstam

printf "\n%s", last_lines } # sstamp_to_ymdhMs - c

ss_mon_days[ 9] = 31 ss_mon_days[10] = 31 # C

ss_NTP = 109513 } function sstamp_to_ymd

### ⟦L⟧ ⟸ corpus/raw/tz/leapseconds

Allowance for leap seconds added to each time zone file. # This file is in the public domain. # This file is generated automatically from the data in the public-domain # NIST/IERS format leap-

rotation. The first ("1 Jan 1972") data line in leap-seconds.list # does not denote a leap

All leap-seconds are Stationary (S) at the given UTC time. # The correction (+ or -

Leap YEAR MON DAY 23:59:59 - S # Typical lines look like this: # Leap YEAR MON DAY 23:59:60 + S Leap 1972 Jun 30 23:59:60 + S Leap 1972 Dec 31 23:59:6

Leap 2016 Dec 31 23:59:60 + S # UTC timestamp when thi

Expires 2027 Jun 28 00:00:00 # Here are POSIX timesta

this is typically a bit less than one year after "updated". #updated 1783323897 (2026-07-06 07:44:57 UTC) #expires 1814140800 (2027-06-28 00:00:00 UTC) # Updated through IERS Bulletin C (https://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat) # File expires on 28 June 2027

## ⟪BabelTele⟫
🧭 体例 ⟦I⟧⟨2272060800      10      # 1 Jan 1972⟩ ‖ ⟦A⟧⟨	printf "Leap\t%d\t%s\t%d\t%s\tS\n", \⟩ ‖ ⟦L⟧⟨Leap	1972	Jun	30	23:59:60	+	S⟩ ⇒ 三个源排在同一条因果链上: 输入 ⟦I⟧⟨2272060800      10      # 1 Jan 1972⟩(NIST/IERS 的 leap-seconds.list, 数据 28 行, 每行“NTP 秒 ⇎ DTAI 秒 ⇎ # 日 月 年”) ⇎ 程序 ⟦A⟧⟨	printf "Leap\t%d\t%s\t%d\t%s\tS\n", \⟩(256 行 awk, 全部数据行只由那一句 printf 发射) ⇎ 产物 ⟦L⟧⟨Leap	1972	Jun	30	23:59:60	+	S⟩(zic 格式的 leapseconds, 数据 27 行)。与上一条“目录行 ⇎ 它指着的原文”不同: 那里的联结要读者按字段重建, 这里的联结可以**执行**——本机用 gawk 把程序跑在输入上, 所得与在库那份逐字节相同(散列写在 src 行, 版本与命令写在解读注)。于是可核性升到四级: 能数的记号 ⇎ 能展开复算的 ⇎ 能执行复现的 ⇎ 只有工具知道的。审计口径把三份文件的注释行各剔掉 92/61/51 行(输入与产物的绝大部分都是注释), 口径内只剩可行文字: 1035 ⇎ 6464 ⇎ 809 字符。与本库另一条时区条(比同一份输入的不同时刻)也不同: 本条比同一时刻上的三个不同角色。
✂️ 一句程序撑起二十七行 ⟦A⟧⟨	printf "Leap\t%d\t%s\t%d\t%s\tS\n", \⟩ ‖ ⟦A⟧⟨    if (old_TAI_minus_UTC) {⟩ ‖ ⟦I⟧⟨2272060800      10      # 1 Jan 1972⟩ ‖ ⟦L⟧⟨Leap	1972	Jun	30	23:59:60	+	S⟩ ⇒ 产物的 27 行数据全部出自程序里**那一句** ⟦A⟧⟨	printf "Leap\t%d\t%s\t%d\t%s\tS\n", \⟩(整份文件它只出现一次, 0 键核对)。程序的行首发射语句: print ⟦A⟧⟨  print "# Allowance for leap seconds added to each time zone file."⟩ 起共 56 条, printf 共 5 条(两个数各自回源, 求和留给读者), 要交代 86 行产物: BEGIN 块 40 条 print 与产物头 40 行**按序逐行相等**(助手 B48_HEADOK 逐条比对), 其中 5 条是空行发射; 两端抽样: 产物首行 ⟦L⟧⟨# Allowance for leap seconds added to each time zone file.⟩ ⇎ 程序 ⟦A⟧⟨  print "# Allowance for leap seconds added to each time zone file."⟩, 产物 ⟦L⟧⟨# Typical lines look like this:⟩ ⇎ 程序 ⟦A⟧⟨  print "# Typical lines look like this:"⟩; 剩下的 19 行由 END 块产出, 而 19 = 86 − 40 − 27(减法即证, 写在 0 键里)。输入却有 28 行数据: 差额一行不丢, 是被守卫 ⟦A⟧⟨    if (old_TAI_minus_UTC) {⟩ 吃掉的——首行 ⟦I⟧⟨2272060800      10      # 1 Jan 1972⟩ 只标“现行 UTC 定义的起点”, 不是闰秒; 产物 ⟦L⟧⟨Leap	1972	Jun	30	23:59:60	+	S⟩ 那种“带真数值的行”在程序里 0 处(程序只持有带说明符的骨架)。判词: 生成器的压缩不在字符层而在**语句层**——“文件有多少行”要换成“多少条发射语句 × 各跑几次”, 而次数由守卫决定。
📉 一整列数字被压成一个符号 ⟦I⟧⟨3692217600      37      # 1 Jan 2017⟩ ‖ ⟦L⟧⟨Leap	1972	Jun	30	23:59:60	+	S⟩ ‖ ⟦A⟧⟨	    sign = "23:59:60\t+"⟩ ‖ ⟦A⟧⟨	    sign = "23:59:59\t-"⟩ ⇒ 输入的第二列是 TAI−UTC: ⟦I⟧⟨3692217600      37      # 1 Jan 2017⟩ 那行的 10 起、到 37 止, 28 个数**逐个连续**(要读完整列才知道, 助手 B48_TAISPAN 复算)。程序只问“比上一行大还是小”, 于是产物每行只留下那一个**符号**: ⟦L⟧⟨Leap	1972	Jun	30	23:59:60	+	S⟩ 里的加号 27 处, 减号写法 ⟦A⟧⟨	    sign = "23:59:59\t-"⟩ 在产物里 0 处(0 键)——不是不能有: 程序两种时刻各备一次(⟦A⟧⟨  print "# Leap	YEAR	MON	DAY	23:59:60	+	S"⟩ 那种正号形式 2 处 ⇎ 负号形式 2 处, 等式在 0 键), 只是 28 行数据里没有一次遇上。输入还专门写着 ⟦I⟧⟨#	theoretically possible to have a negative leap second (a second removed from UTC), but so far,⟩ 一句“理论上可以有负闰秒”。数值一个都没过去: 37 在产物口径内 0 处(0 键); 分隔符也换了层——输入数据行用空格(口径内制表符 0 处 ⇎ 整份文件 66 个全在注释行里), 产物用制表符 162 个 = 每行 6 个 × 27 行(等式在 0 键)。判词: 说“丢了信息”要具体到哪一列、留下了那一列的什么投影——这里留下一列的**差分符号**, 丢掉整列的**大小与刻度**。
📅 减一秒把每个日期的名字都改了 ⟦I⟧⟨2287785600      11      # 1 Jul 1972⟩ ‖ ⟦L⟧⟨Leap	1972	Jun	30	23:59:60	+	S⟩ ‖ ⟦A⟧⟨	sstamp_to_ymdhMs(NTP_timestamp - 1, ss_NTP)⟩ ‖ ⟦L⟧⟨# rotation.  The first ("1 Jan 1972") data line in leap-seconds.list⟩ ⇒ 第二行数据 ⟦I⟧⟨2287785600      11      # 1 Jul 1972⟩ 的注释写着“1 Jul 1972”, 产物对应行却是 ⟦L⟧⟨Leap	1972	Jun	30	23:59:60	+	S⟩——差在程序那句 ⟦A⟧⟨	sstamp_to_ymdhMs(NTP_timestamp - 1, ss_NTP)⟩: 它换算的是**端点前一秒**, 于是每一行都退回上一天。逐行核对 27 行(助手把 awk 自己的日历照抄进审计器复算): 月份标签 27/27 行被改掉、日 27/27 行被改掉、年 16/27 行被改掉, 而被改年的恰是那 16 个“1 Jan”开头的行(1 月 1 日减一秒退到前一年)。词汇因此整批换人: 输入口径内只有 Jan 17 处、Jul 11 处, Jun 0 处、Dec 0 处; 产物反过来只有 Jun 11 处、Dec 16 处, Jan/Jul 各 0 处(全在 0 键)。最硬的两枚证物是年份: 输入的“1 Jan 1980”与“1 Jan 2017”在口径内各 1 处, 而 1980 与 2017 在产物里各 0 处——它们被换算成了 1979 与 2016。产物里那条“形状示范”行 ⟦L⟧⟨# Leap	YEAR	MON	DAY	23:59:60	+	S⟩ 唯一, 而它写的时刻在数据行里逐字重演 27 次; 换号示范 ⟦L⟧⟨# Leap	YEAR	MON	DAY	23:59:59	-	S⟩ 那种时刻在数据行 0 处(全文件仅 1 处, 就是这条示范本身)。判词: 换算不改数据、只改**名字**, 而且改得逐行都是同一方向; 若按字符串把两份表的日期对齐, 会得到“零行相同”的假结论。
🗝 程序自带另一套月份词汇 ⟦A⟧⟨  monthabbr[ 1] = "Jan"⟩ ‖ ⟦A⟧⟨  monthabbr[ 6] = "Jun"⟩ ‖ ⟦A⟧⟨  monthabbr[ 7] = "Jul"⟩ ‖ ⟦A⟧⟨  ss_mon_days[ 9] = 31⟩ ⇒ 产物的月名不来自输入, 来自程序的表: ⟦A⟧⟨  monthabbr[ 1] = "Jan"⟩ 起共 12 条 monthabbr 定义(条数在 0 键核对), 产物只用到 Jun 与 Dec, 其余 10 个名字在产物口径内 0 处; 连输入自己写的 Jan/Jul 也是经这张表**翻译**后才可能进产物, 而翻译结果是别的名字(见上条)。程序还定义着输入用不到的 Jul ⟦A⟧⟨  monthabbr[ 7] = "Jul"⟩。另一张表更见结构: 月长表 ⟦A⟧⟨  ss_mon_days[ 9] = 31⟩ 只有 11 条(31 出现 7 次、30 出现 4 次, 28 一次也没有, 0 键), 因为程序把年从三月起算、二月被“闰四年多一天”吸收——十二个月名 ⇎ 十一个月长, 差的那一处也在 0 键。判词: 三份文件各有一套时间词汇, 交集近空; “谁的词进了产物”要看程序里那张表, 而不是输入里的写法。
🔀 同一个句子, 三份文件三种拼法 ⟦I⟧⟨#    	This file is in the public domain.⟩ ‖ ⟦A⟧⟨  print "# This file is in the public domain."⟩ ‖ ⟦L⟧⟨# This file is in the public domain.⟩ ‖ ⟦L⟧⟨# rotation.  The first ("1 Jan 1972") data line in leap-seconds.list⟩ ⇒ “公有领域”那句声明在三份文件里都在: 口径内 0 ⇎ 1 ⇎ 0(输入与产物那两处都是注释行, 被口径剔掉), 全文件 1 ⇎ 2 ⇎ 1 ⟦I⟧⟨#    	This file is in the public domain.⟩、⟦A⟧⟨  print "# This file is in the public domain."⟩、⟦L⟧⟨# This file is in the public domain.⟩。四份副本(程序两份)里审计口径只看见一份——口径 ⇎ 全文必须成对报。引号又是另一层: 程序把引号写成转义形式(转义引号 8 处), 于是“带引号的 1 Jan 1972”这个字面在输入与程序里 0 处、在产物里恰好 1 处 ⟦L⟧⟨# rotation.  The first ("1 Jan 1972") data line in leap-seconds.list⟩; 而这 1 处是程序对**输入格式**的描述, 不是任何一行数据。分隔符同理换层: 程序里 15 个转义制表符 ⇎ 产物 0 个(它只有真制表符 162 个); 百分号 30 枚: 说明符四型 %d 4、%s 5、%.4d 3、%.2d 14, 余下 4 枚是取余运算符(总数减五段为 0 写在 0 键) ⇎ 产物 0 枚——说明符全被值换掉。判词: 同一句话在链上每走一站就换一次拼法; 逐字比对必须先把“转义层”剥掉, 否则三处都在的句子会报成“两边都没有”。
🫥 拷贝的两行在口径里两边都是 0 ⟦I⟧⟨#h	a9bad145 84c31c70 758402aa b37bfd54 5923836a⟩ ‖ ⟦A⟧⟨    printf "\n%s", last_lines⟩ ‖ ⟦L⟧⟨#	Updated through IERS Bulletin C (https://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat)⟩ ‖ ⟦I⟧⟨#	and September. Since the introduction of leap seconds in 1972, only dates in June and December were used.⟩ ⇒ 产物末尾 2 行 ⟦L⟧⟨#	Updated through IERS Bulletin C (https://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat)⟩、⟦L⟧⟨#	File expires on 28 June 2027⟩ 逐字来自输入(助手在全文里比对, 命中 2 行), 由程序那句 ⟦A⟧⟨    printf "\n%s", last_lines⟩ 原样搬运; 而在审计口径里这两串在两份文件里**都是** 0——两个 0 数字相同, 关系却是拷贝; 数数看不到, 必须比全文。输入的完整性自证 ⟦I⟧⟨#h	a9bad145 84c31c70 758402aa b37bfd54 5923836a⟩ 那行哈希: 口径内 0 ⇎ 全文 1, 程序既不读也不写, 产物里 0 处(两条 0 成因不同)。程序用来“捡回这两行”的正则 ⟦A⟧⟨/^#[ \t]*[Uu]pdated through/ || /^#[ \t]*[Ff]ile expires on/ {⟩ 又是一种拼法(带方括号与 [Uu] 式类), 它的字面在输入里 0 处——规则与数据互不见对方的写法。输入还写着 ⟦I⟧⟨#	and September. Since the introduction of leap seconds in 1972, only dates in June and December were used.⟩(首选六月与十二月), 可它自己的数据行只有 Jan 与 Jul 两种标签, June 这个词在两份表的数据侧 0 处(全文 5 ⇎ 0 ⇎ 1)。判词: “两边都是 0”至少有三种成因(真没有 ⇎ 被口径剔掉 ⇎ 换了拼法), 本条把三种各自成对报出, 不让它们共用一个结论。
⏳ 程序说自己活到哪一年, 用它自己的日历能核 ⟦A⟧⟨# exact integer arithmetic only through 10**10, which means for NTP⟩ ‖ ⟦A⟧⟨  ss_NTP = 109513⟩ ‖ ⟦A⟧⟨    epoch_minus_NTP = ((1970 - 1900) * 365 + 17) * 24 * 60 * 60⟩ ‖ ⟦L⟧⟨#updated 1783323897 (2026-07-06 07:44:57 UTC)⟩ ‖ ⟦L⟧⟨#expires 1814140800 (2027-06-28 00:00:00 UTC)⟩ ⇒ 程序头部 ⟦A⟧⟨# exact integer arithmetic only through 10**10, which means for NTP⟩ 作两个断言: POSIX 要求 awk 精确整数只到 10**10 秒(即“只活到 2216 年”), 而实际的 double 实现到 2**53 秒(即 285428681 年)。这两个数不在产物里, 在程序里也只活在**被口径剔掉的注释**中(口径内 10**10 与 2**53 各 0 处, 全文 2 ⇎ 3 处; 2216 与 285,428,681 口径内也各 0, 全文 2 ⇎ 1)。但不必信权威: 把程序自带的日历(⟦A⟧⟨  ss_NTP = 109513⟩ 的 109513 日纪元 + 四百年/百年/四年/年降档)照抄进审计器, 10**10 秒落在 2216、2**53 秒落在 285428681, 与散文逐字相等(两条等式各是一个键)。同一套算术还核住封套: 输入的 #$ ⇎ #@ 两枚 NTP 秒 ⟦I⟧⟨#$	3992312697⟩ ⇎ ⟦I⟧⟨#@	4023129600⟩ 与产物 ⟦L⟧⟨#updated 1783323897 (2026-07-06 07:44:57 UTC)⟩ ⇎ ⟦L⟧⟨#expires 1814140800 (2027-06-28 00:00:00 UTC)⟩ 之间, 恰好差程序 ⟦A⟧⟨    epoch_minus_NTP = ((1970 - 1900) * 365 + 17) * 24 * 60 * 60⟩ 那行的 2208988800(=七十年 × 每天 86400 秒, 其中十七个闰日); 而两枚时间戳相隔 30816903 秒, 比整年少 719097 秒(356.68 天), 产物注释 ⟦L⟧⟨# this is typically a bit less than one year after "updated".⟩ 说的“略少于一年”在这一份数据上成立。判词: 程序对**自身寿命**的断言住在散文里, 却能用它自己的算法复算; 换掉算法就不再是同一份产物——可执行性正是这类条目的裁判。
🚫 三向缺席, 方向各不相同 ⟦A⟧⟨      print "# (No Expires line, since the expires time is unknown.)"⟩ ‖ ⟦A⟧⟨      print "#(updated time unknown)"⟩ ‖ ⟦A⟧⟨      printf "%sExpires %.4d\t%s\t%.2d\t%.2d:%.2d:%.2d\n", \⟩ ‖ ⟦L⟧⟨#Expires 2027	Jun	28	00:00:00⟩ ‖ ⟦I⟧⟨#NTP Time      DTAI    Day Month Year⟩ ⇒ 程序有而产物无: 2 条死支发射各 1 处 ⟦A⟧⟨      print "# (No Expires line, since the expires time is unknown.)"⟩、⟦A⟧⟨      print "#(updated time unknown)"⟩(外加第三句“expires 未知”), 产物 0 处——它们对应的条件在 28 行数据里没有一次成立; 标识符更是整批消失(EXPIRES_LINE 2 处、last_lines 3 处、monthabbr 定义 12 条, 产物全 0)。产物有而程序无: 27 行 ⟦L⟧⟨Leap	2016	Dec	31	23:59:60	+	S⟩ 的具体日期、162 个制表符、输入的列名头 ⟦I⟧⟨#NTP Time      DTAI    Day Month Year⟩(“Day Month Year”三个词程序从未写过, 三份文件的口径内都是 0)。输入有而两边无: 那行哈希、#$ 与 #@ 两枚秒的**写法**(程序只按行首字符匹配, 从不复写这两枚)。还有一处开关只能反推: 产物的到期行 ⟦L⟧⟨#Expires 2027	Jun	28	00:00:00⟩ 带着注释符, 而“不带注释符的 Expires 行”两份文件都 0 处——程序那句三元 ⟦A⟧⟨      printf "%sExpires %.4d\t%s\t%.2d\t%.2d:%.2d:%.2d\n", \⟩ 运行时取了加“#”的一支(调用时没给 EXPIRES_LINE), 这条**分支选择**在两份文件里都只留下结果、不留痕迹。判词: 三份文件互不包含, 连方向也不对称; 缺席要按“谁的哪种写法”分列, 一句“产物缺原文”会把三种缺席糊成一个。
∴ 骨架 ⟦I⟧⟨#	MJD: The Modified Julian Day number. MJD = X/86400 + 15020⟩ ‖ ⟦L⟧⟨# All leap-seconds are Stationary (S) at the given UTC time.⟩ ‖ ⟦A⟧⟨  print "# Typical lines look like this:"⟩ ⇒ ① 因果链可以执行复现, 这比“展开复算”更高一级: 跑上游工具得到同一散列, 联结就不靠读者重建; ② 生成器的账按**语句 × 次数**记, 不按行数记(56 条 print ⇎ 5 条 printf ⇒ 产物 86 行, 其中一句跑 27 次, 守卫吃掉一次); ③ 丢列 ≠ 丢全部: 28 个整数的列被压成 27 个差分符号, 说清“留下什么投影”才算说清压缩; ④ 一次换算(减一秒)能把 27/27 行的月名与 16/27 行的年名改掉, 而词汇来自程序的表不是输入; ⑤ 同一句话在链上换拼法(转义引号、转义制表符、说明符 ⇎ 真制表符与值), 逐字比对会在三份文件间全盘失明; ⑥ “两边都是 0”可能是拷贝(同被口径剔掉的行), 数数看不到, 要全文比; ⑦ 程序对自身的断言(活到 2216 年、七十年含十七闰日、略少于一年)可由它自己的算法复算, 不必引外部权威; ⑧ 死支与未取的三元支在产物里是 0, 而 0 不代表能力不存在; ⑨ 输入自带的完整性哈希不被搬运, 产物的可信度只剩外部散列——四级可核性要分开报。判词: “一个源 ⇎ 另一个源”在这里不够用; 要报的是“谁生成谁、生成时哪一列被投影、哪一层被换写、哪一支没被走到”。
ℒmethod ⟦I⟧⟨2287785600      11      # 1 Jul 1972⟩ ‖ ⟦A⟧⟨	printf "Leap\t%d\t%s\t%d\t%s\tS\n", \⟩ ‖ ⟦L⟧⟨Leap	2016	Dec	31	23:59:60	+	S⟩ ‖ ⟦A⟧⟨/^#[ \t]*[Uu]pdated through/ || /^#[ \t]*[Ff]ile expires on/ {⟩ ⇒ 读“输入 ⇎ 生成它的程序 ⇎ 程序的产物”: 第一步先确认联结**能不能执行**——若上游工具在本机可用, 就把它当作最强的核验(散列相等即可销案), 不能执行才退回“按程序算法复算 + 逐行对账”; 第二步把程序的发射语句列成表(每条 print 一次 ⇎ 每条在循环里的 printf 跑 n 次), 用“语句 × 次数 + 守卫”解释产物的行数, 而不是直接数行; 第三步对每一列数据问三个问题: 它过去了吗 ⇎ 它以什么投影过去(差分符号、常量、被丢弃) ⇎ 它的**写法**换没换(空格 ⇎ 制表符、字面 ⇎ 转义); 第四步凡跨三份文件搜词一律同时报“口径内 ⇎ 全文”, 并对每个“两边都是 0”查明是缺、是被剔、还是换拼法; 第五步把程序散文里的自述寿命/纪元拿它自己的算法复算一遍(⟦A⟧⟨	sstamp_to_ymdhMs(NTP_timestamp - 1, ss_NTP)⟩ 那种换算要连“-1”一起照抄)。核验口径: ⟦I⟧⟨2287785600      11      # 1 Jul 1972⟩ 一类标 I 只在输入内数, ⟦A⟧⟨	printf "Leap\t%d\t%s\t%d\t%s\tS\n", \⟩ 一类标 A 只在程序内数, ⟦L⟧⟨Leap	2016	Dec	31	23:59:60	+	S⟩ 一类标 L 只在产物内数; 程序用来抓注释的正则 ⟦A⟧⟨/^#[ \t]*[Uu]pdated through/ || /^#[ \t]*[Ff]ile expires on/ {⟩ 与它抓到的行是两套写法, 不可互推。
✂️ 为什么这份编码比摘要窗口长 ⟦L⟧⟨# This file is generated automatically from the data in the public-domain⟩ ‖ ⟦A⟧⟨# Generate zic format 'leapseconds' from NIST/IERS format 'leap-seconds.list'.⟩ ⇒ 三份原料都很小: 口径内 1035 ⇎ 6464 ⇎ 809 字符, 而判词要说的是**一条因果链上的对账**: 发射语句的账、列的投影、换算带来的改名、转义层、口径看不见的拷贝。摘要段只能取锚点触到的窗口 ⟦L⟧⟨# This file is generated automatically from the data in the public-domain⟩、⟦A⟧⟨# Generate zic format 'leapseconds' from NIST/IERS format 'leap-seconds.list'.⟩, 而“27 行逐行等于输入减一秒再走程序自带日历”“40 条发射与产物头 40 行按序相等”这类结论住在展开与执行里, 不住在任何窗口里。本条三份文件都很小(磁盘 5065 ⇎ 9448 ⇎ 3694 字节), 保留率因此天然偏高——读它要按“四级可核性各占几项”来读, 而不是按“少说了多少话”。

## ⛓解读注
※ 体例: 本条三个源排在一条因果链上——⟪leap-seconds.list(NIST/IERS 表) ⇎ leapseconds.awk(zic 转换器) ⇎ leapseconds(产物)⟫。锚位 102 个(不同串 49 个; 标 I 的 22、标 A 的 47、标 L 的 33, 平均长度 44 字符), 判词 12 行, DERIV 37 键, 0 键折 67 项(纯缺席 34 + 等式/差值 33, CNT/CNTF 原语出现 78 次)。与“目录行 ⇎ 原文”一类两源条不同: 这里的第一手联结可以执行(见下条), 不需要读者重建。

※ 可执行复现(工具侧, 本条最强的一环): GNU Awk 5.3.2, API 4.0, PMA Avon 8-g1, (GNU MPFR 4.2.2, GNU MP 6.3.0); 命令 `gawk -f corpus/raw/tz/leapseconds.awk corpus/raw/tz/leap-seconds.list`; 其输出与本库在库产物 sha256 逐字节相同: 8f066f297a37a798… == 8f066f297a37a798…。复算之外的第二条路: 把程序自带的日历照抄进审计器, 27/27 行逐行等于“输入第 k 行时间戳减一秒后走该日历”(吻合 27/27 ⇎ 月改 27/27 ⇎ 年改 16/27); 执行成功意味着“产物由这份输入经这个程序生成”不再是叙述, 而是可重演的事件。

※ DERIV 算术(键名即数值, 表达式跑在三份原文上并逐个回算, 本注是第二条独立路径): 0⇒零值键(67 项, 纯缺席 34 + 等式/差值 33): 缺席侧——输入的 Jun/Dec/“Day Month Year”、输入口径内制表符与 a9bad145、产物的 % 与转义串(t、引号)、产物 Leap+BS+t 骨架、#Expires/^Expires 各形、28 日数的表项、37、	-	S、23:59:59、Jan/Jul/1980/2017、程序内 ^Leap+t 行首、10**10 与 2**53 与 2216 与 285,428,681 与 June(程序与产物)、"1 Jan 1972" 字面与转义 t(输入与产物); 等式侧——输入数据行=DTAI 跨度、Jun30+Dec31=Leap 行、Dec 子串=Dec31 行、Jul(输入)=Jun30(产物)、23:59:60=Leap 行、	+	S=23:59:60、全文 23:59:60=口径+1(示范行)、产物 t=6×行、程序 60=59、+=-、公有领域三处“全文−口径=1”、30=4+5+3+14+4(取余)、monthabbr−ss_mon_days=1、31+30 表项=全表、print ""=头部空+尾部空、ROWSOK=27⇎MSHIFT⇎DSHIFT⇎YSHIFT=Dec31、HEADOK=BPRINT、86=40+27+19、纪元式、两枚封套秒差纪元、GAP+SHORT=365×86400、2216 与 285,428,681 对散文逐字。3⇒%.4d 说明符数(程序口径) ⇎ 产物 0 处——它们只活在程序的格式串里；4⇒%d 说明符数 ⇎ 取余运算符也是 4 枚(30−26=4, 拆法写在 0 键)；8⇒转义引号(\"")在程序里的个数——它引用的恰恰是输入注释行里的引号, 产物里 0；11⇒产物“Leap⇥年⇥Jun⇥30”行数 ⇎ 输入 Jul 1 行 11 个(0 键: Jul(输入)=Jun30(产物))；12⇒monthabbr 定义条数(整套 12 个月名的词汇表) ⇎ ss_mon_days 11 条(差 1 在 0 键)；14⇒%.2d 说明符数(四型里最多的一型)；15⇒转义制表符 \t 在程序口径内的个数 ⇎ 产物 0 处——制表符在程序里是“写法”, 在产物里才是字符；16⇒产物 Dec 31 行数 ⇎ 被改年的行数(等式 YSHIFT−16 在 0 键)；17⇒Jan 在输入口径内的次数(16 个“1 Jan”闰行 + 1 行 1972 起点)；19⇒END 块产出的行数 = 86 − 40 − 27; 其中空行 3 枚只有 2 枚来自 print "", 第三枚来自 printf "\n%s" 的转义换行(工具侧)；27⇒产物数据行数, 全部出自同一句 printf; 也等于逐行吻合数、月改数、日改数(三条等式在 0 键)；28⇒DTAI 跨度(10..37 逐个连续) ⇎ 输入数据行数(等式在 0 键; 首行不产闰秒)；30⇒程序里百分号总数 = 26 枚说明符 + 4 枚取余；40⇒BEGIN 块 print 发射条数 ⇎ 产物头部行数(按序逐条相等, HEADOK=40)；51⇒产物被口径剔掉的注释行数——86 行里 51 行, 数据只占 27；56⇒程序里 print 语句总数(发射 40 条在 BEGIN, 其余在 END 与死支)；61⇒程序被口径剔掉的行数(整份 61 行注释) ⇎ 巧合: print+printf 语句总数也是 61, 本键只证前者；66⇒输入全文件真制表符数, 口径内 0——66 枚全住在注释行；86⇒产物行数 = 40 头 + 27 数据 + 19 尾(减法在 0 键)；92⇒输入被口径剔掉的行数, 120 行里 92 行是注释——数据侧只占 28；120⇒输入行数；162⇒产物制表符总数 = 6 × 27(每行六个分隔, 等式在 0 键)；256⇒程序行数, 其中 45 行发射语句(56 print + 5 printf 减去重叠与死支不必拆干净——两数各自回源, 求和留给读者)；356.68⇒两枚封套秒相隔天数(30816903/86400, round 到两位)——“略少于一年”= 365 − 356.68 ≈ 8.3 天；809⇒产物口径内字符数 ⇎ 全文件 3694 ⇎ 磁盘 3694(纯 ASCII 才让后两者相等)；1035⇒输入口径内字符数 ⇎ 5065 ⇎ 5065；2216⇒程序散文断言“10**10 秒落在 2216 年”——用它自带的日历复算, 等式在 0 键；3694⇒产物磁盘字节数；5065⇒输入磁盘字节数；6464⇒程序口径内字符数 ⇎ 9448 ⇎ 9448；9448⇒程序磁盘字节数；86400⇒一天的秒数 = 24×60×60(三个因子逐字住在程序纪元那行)；719097⇒间隔比整年少掉的秒数(365×86400 − GAP)；30816903⇒#@ − #$ 两枚 NTP 秒之差(POSIX 侧 = #updated ⇎ #expires 之差)；285428681⇒2**53 秒落在的年份——散文里的“实际 double 上限”, 复算在 0 键；2208988800⇒NTP⇎POSIX 纪元差 = ((1970−1900)×365+17)×86400; 输入的 #$⇎#@ 与产物的 #updated⇎#expires 恰差它(两条等式在 0 键)。

※ 四级可核性各住在哪级: ① 记号可数(口径 CNT)——行数 120/256/86、被剔 92/61/51、t=162、说明符 30、print 56、% 全谱 30; ② 展开/复算——27 行逐日吻合、DTAI 10..37 连续、月年改名数、40 条发射按序相等、纪元与封套两差(助手 B48_*, 本注第二条路); ③ 本机执行——gawk 重跑得到同一 sha256(上条); ④ 只属于工具——字节 5065/9448/3694、全文件计数(哈希 1⇎0⇎0、June 5/0/1、Updated 1/0/1、输入全文 t 66)、#h 那行的语义(它是输入自带的完整性哈希, 程序不搬运它, 产物的可信度因此只剩外部散列)、END 空行 3 枚的来源拆分(2 枚 print "" + 1 枚 printf 转义换行)。

※ 口径与“两边都是 0”: 三份文件字符数三口径——口径 1035 ⇎ 全文件 5065 ⇎ 磁盘 5065(I), 6464 ⇎ 9448 ⇎ 9448(A), 809 ⇎ 3694 ⇎ 3694(L); 纯 ASCII 使后两列在三份文件上都相等(非 ASCII 计数两种口径都是 0)。“公有领域”一句四副本: 口径内 0 ⇎ 1 ⇎ 0、全文 1 ⇎ 2 ⇎ 1——口径只看见程序那句 print; “June”在两份表的数据侧口径内 0 ⇎ 全文 5 ⇎ 0 ⇎ 1; 末尾两行(#	Updated… ⇎ #	File expires…)从输入逐字拷进产物(全文命中 2 行), 可它们在两文件口径内同为 0——数数只看得到两个 0, 拷贝住在全文里。

※ 生成器的账(语句 × 次数): BEGIN 40 条 print 逐行 ⇎ 产物头 40 行(按序全等), 其中空行 5 枚; 主循环 1 条 printf 跑 27 次(守卫吃掉首行, 输入数据 28 行 ⇒ 产物 27 行); END 产 19 行(尾部 2 枚拷贝); 死支 3 条 print 与未取的三元支在产物里全是 0——0 不代表能力不存在。程序散文里 10**10⇎2**53 只活在注释(口径 0 ⇎ 全文 2⇎3), 而用它自己的日历能把“2216 年”“285,428,681 年”复算出来, 连“七十年含十七闰日”的 17 都住在纪元那行。

※ 摘要与联结: 摘要段 union_hit=102(=49 锚位, 无失锚), 三份文件互相能命中的锚 0 个; 标签归位仍是作者职责——atomcheck 把同 tag 三源拼起来比字面, ⟦I⟧/⟦A⟧ 写反不会 FAIL, 本条机检 ok=49/0。

※ 实况: 编码 10513 字符 ⇎ 摘要段 3513 字符(保留率 299.3%), vs raw 源 57.742%, 唯一码点 566, 区块 8 类, 字符/语义单元 5.76。拉丁字母: 锚内 2383 ⇎ 锚外 305(其中标签 102)。全库现 48 条 / 已机检推导 516 条 / 全库保留率 **89.2%**。B48 的小整数待核 1 项: 助手名 B48_* 里的条目号 48(不是量在源上的数)。

※ 保留率为什么天然偏高: 三份原料都小(口径内合计 8308 字符, 磁盘合计 18207 字节), 摘要段按锚取窗没有可展的长正文; 本条的密度住在“四级可核性各占几项”里——判词最重的几条(执行复现、逐日对账、纪元换算、转义层)都不在任何窗口里, 若只留输入而丢掉程序与产物, 联结就退回到读者脑补, 本级独有的那一级(可执行)整级消失。
