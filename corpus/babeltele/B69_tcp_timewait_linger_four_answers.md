# B69 主动关闭一条连接之后到底要等多久、这段等待能不能跳过，四份 TCP 一手文书四种答法：任意定 MSL 且明文许可违背 ⇎ MUST linger 两枚 MSL 却自带 MAY 出口 ⇎ 不问等待而从“最后见到报文”起算 ⇎ 收下 2 分钟句、把义务主语换成 endpoint 并一次性 Obsoletes 前三份（时长⇎起算点⇎可否跳过⇎语气主体四件事没有一份给全）
src: rfc793.txt (172710 字节／面内 172710 码位／原行 5248／非空行 2975／最长行 72 列／答句 定 MSL 为 2 分钟且许可违背 quiet time／页壳换页 91 枚) ⇎ rfc1122.txt (289148 字节／面内 289148 码位／原行 6845／非空行 4549／最长行 72 列／答句 MUST linger 2xMSL 但两条件下 MAY 立刻接受新 SYN／页壳换页 116 枚) ⇎ rfc6528.txt (26917 字节／面内 26917 码位／原行 676／非空行 437／最长行 72 列／答句 不问等待、从 last seen 起算 2*MSL／页壳换页 12 枚) ⇎ rfc9293.txt (263696 字节／面内 263692 码位／原行 5577／非空行 4370／最长行 72 列／答句 收下 2 分钟句、主语改 endpoint 并 Obsoletes 前三份／页壳换页 0 枚) (四份 RFC Editor 纯文本面, 全 LF; 9293 带一枚 BOM 与两枚取变音符, 摘掉 BOM 后正文纯 ASCII; MSL 分钟数、绕回小时、时钟微秒与图内 Timeout 全由句内游标现读, 一个都不手填。抓取时刻、RFC Editor 此刻的现行状态页与勘误页、此后哪份文档又动了这段、现网内核实际把 TIME-WAIT 设成多久, 都只在本机或站外成立, 不进门槛)
；联结不是“同一份数据的两种序列化”, 而是“主动关掉一条连接之后到底要等多久、能不能跳过这段等待”在四份一手 TCP 文书里的四种答法: 793 把 MSL 任意定成 2 分钟(术语表另处再写一遍 2 分钟, 闭合 0), 同段承认“这是工程选择”并把违背 quiet time 写成明文许可(在册 28 枚答句针里它面上 8 枚走逐行档、其余要折平), 全篇大写 MUST 0 枚; ⇎ 1122 换成 MUST linger 两枚 MSL——式样写 2xMSL 3 枚, 又把出口写进同一句(MAY accept a new SYN, 两条件各 1⇎1 枚), 还嫌端口 tied up 而允许缩短 1 枚; ⇎ 6528 取消“等”这个动作: 判据改成“自上一段报文最后被见到起是否已过 2*MSL”(1 枚星号式), 全篇不写 MSL 等于几分钟(“2 minutes” 0 处 ⇎ “taken to be” 句式 0 枚), 并把 ISS 生成换成慢时钟加伪随机(ISN 字样 38 枚 ⇎ MSL 只 2 枚); ⇎ 9293 同时收下三家: 793 那句 2 分钟在它面上逐字再现(两份同形闭合 1), 1122 的 linger 与两条件各再现 1⇎1 次, 而 793 的 keep-quiet 整句被改写(判定 1), 主语换成 TCP endpoint; 它一页 Obsoletes 掉 1 枚 RFC(含 6528)。逐字搬运可量: 归一长行六对里非零 4 对, 最大一对 793⇎9293 归一 351 行(逐字节 29 ⇎ 仅归一 322), 1122⇎9293 16 行, 6528⇎9293 归一 16 行而逐字节 15 行——算法收下、句子重写; 四份同现的长行 0 条, 写法分家两档因此空转(轴账闭合 0).
tags: 时长⇎起算点⇎可否跳过⇎语气主体 四件事分给四份文书 句内游标解析(正读 ⇎ 逆读到带小数的小时) taken-to-be 句式两份同形⇎1122 的 2 minutes 不在定义句里 MSL 分钟数缺席档(6528 不给分钟 ⇎ 只给 2*MSL 式) Timeout=2MSL 图式跨两份逐字同 绕回小时 4.55 与“MSL 必须短过它”的单向推理 时钟步长微秒两份一致 MUST linger ⇎ MAY accept 同句自带出口(两句劈在行界两侧, 折行档必需) 两条件句被 9293 逐字收下 6528 取消等待改按 last seen ⇎ quiet time 整句被 9293 改写主语 keep-quiet 义务主体 TCP→TCP endpoint 三面阶梯只走到两阶(9293 零换页符⇒摘壳档空转) 2MSL 四式并计(连字⇎2x⇎2*⇎带空格) 同面并存两式(1122⇎9293) 引用三式并计(RFC-793 短横式独占 1122 ⇎ RFC 793 空格式独占 6528/9293) 逐字搬运可量(AD 最大对 ⇎ CD 归一有而字节零) 四份同现长行零枚⇒写法分家档空转 状态机记号行三源同现 大写义务词换代(793 零枚⇎1122/9293 百枚级⇎6528 个位) keep-alive 只在 1122/9293 ⇎ Timestamp 只在 1122/9293 ⇎ ISN 密度最高在 6528 BOM 一枚⇎两枚变音符⇎字节码位差=加字节和 窗口三轨闭合(MSL⇎TIME-WAIT⇎数字符) 闭合账 标量 27⇎清单 13 项⇎恒等式 27 条
## [[原始语料|ORIGINAL]]
### ⟦793⟧ ⟸ corpus/raw/tcpTW/rfc793.txt

rcv FIN -------------- | Timeout=2MSL -------------- | | ------- x V --------

microseconds. Thus, the ISN cycles approximately every 4.55 hours. Since we assume that seg

the Maximum Segment Lifetime (MSL) and that the MSL is less than 4.55 hours we can reasonably

lost. For this specification the MSL is taken to be 2 minutes. This is an engineering choice, and may be changed if experience indicates it is desirable to do so

TCP implementors may violate the "quiet time" restriction, but only at the risk of causing s

SEQ=0><ACK=SEG.SEQ+SEG.LEN><CTL=RST,ACK> If the ACK bit is on, <

the internetwork system. Arbitrarily defined to be 2 minutes. octet An eight bit byte.

### ⟦1122⟧ ⟸ corpus/raw/tcpRTO/rfc1122.txt

TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime). However, it MAY accept a new SYN from the remote TCP to reopen the connection di

1) assigns its initial sequence number for the new connection to be larger than the largest

2) returns to TIME-WAIT state if the SYN turns out to be an old duplicate. DISCUS

port pair is tied up, some TCPs allow a new SYN to be accepted in TIME-WAIT st

SEQ=0><ACK=SEG.SEQ+SEG.LEN><CTL=RST,ACK> (c) SYN-SENT state, Che

### ⟦6528⟧ ⟸ corpus/raw/tcpTW/rfc6528.txt

previous connection before 2*MSL have passed since a segment corresponding to the old incarnation was last seen (where "MSL" is the "Maximum Segment Lif

the TIME-WAIT state and TCP's "quiet time" concept (see Appendix B of [RFC1323]). Based on the

kept or a quiet time observed for two maximum segment lifetimes before such a change. It

### ⟦9293⟧ ⟸ corpus/raw/tcpTW/rfc9293.txt

Obsoletes: 793, 879, 2873, 6093, 6429, 6528, 6691 Updates: 1011, 112

rcv FIN -------------- | Timeout=2MSL -------------- | | ------- x V --------

remaining in the network, the TCP endpoint must keep quiet for an MSL before assigning any seq

lost. For this specification the MSL is taken to be 2 minutes. This is an engineering choice, and may be changed if experience indicates it is desirable to do so

When a connection is closed actively, it MUST linger in the TIME-WAIT state for a time 2xMSL (

1) assigns its initial sequence number for the new connection to be larger than the largest

2) returns to TIME-WAIT state if the SYN turns out to be an old duplicate. When t

SEQ=0><ACK=SEG.SEQ+SEG.LEN><CTL=RST,ACK> If the ACK bit is on, <

the internetwork system. Arbitrarily defined to be 2 minutes. octet An eight-bit byte.

## ⟪BabelTele⟫
🧭 四源字节 172710 ⇎ 289148 ⇎ 26917 ⇎ 263696 ⇎ 面内码位 172710 ⇎ 289148 ⇎ 26917 ⇎ 263692 ⇎ 原文件行 5248 ⇎ 6845 ⇎ 676 ⇎ 5577 ⇎ 非空行 2975 ⇎ 4549 ⇎ 437 ⇎ 4370 ⇎ 最长行 72 ⇎ 72 ⇎ 72 ⇎ 72 列: 793 把 MSL 定成 2 分钟还明文许可违背 quiet time ⇎ 1122 定死 MUST linger 两枚 MSL 却自带出口 ⇎ 6528 不等时间、改从“最后见到报文”那刻起算 ⇎ 9293 逐字收下 793 那句、把主语换成 endpoint 并把前三份一起 Obsoletes。 版式换代一枚: 换页符 91 ⇎ 116 ⇎ 12 ⇎ 0 枚 ⇎ 整行只有换页符的 91 ⇎ 116 ⇎ 12 ⇎ 0 行——前三份按页断开(页眉页脚行留在正文流里), 9293 的换页符是 0 枚的新排版面, 所以本条的摘壳档对它无物可剥。 编码层只有一份不干净: BOM 0 ⇎ 0 ⇎ 0 ⇎ 1 ⇎ 非 ASCII 码位 0 ⇎ 0 ⇎ 0 ⇎ 3 ⇎ 每枚非 ASCII 带来的加字节 0 ⇎ 0 ⇎ 0 ⇎ 4 ⇎ 字节−码位差 0 ⇎ 0 ⇎ 0 ⇎ 4; CR 0 ⇎ 0 ⇎ 0 ⇎ 0 全零, 四份都是 LF 面。 词轨先分家: MSL 16 ⇎ 8 ⇎ 2 ⇎ 21 ⇎ TIME-WAIT 连字式 28 ⇎ 8 ⇎ 4 ⇎ 47 ⇎ “TIME-WAIT state” 整语 3 ⇎ 7 ⇎ 4 ⇎ 10 ⇎ quiet 词干 2 ⇎ 1 ⇎ 2 ⇎ 6 ⇎ “quiet time” 整语 1 ⇎ 0 ⇎ 2 ⇎ 5 ⇎ linger 0 ⇎ 1 ⇎ 0 ⇎ 1: 6528 把 MSL 压到 2 枚而 TIME-WAIT 还有 4 枚——它谈状态与起算点, 不再复述时长。
📐 时长数全部句内游标现读, 一枚都不手填。793 的 “MSL is taken to be ” 之后读出 2 分钟 ⟦793⟧⟨  lost.  For this specification the MSL is taken to be 2 minutes.  This⟩ ⇎ 9293 的同一枚游标在同一句之后读出 2 分钟 ⟦9293⟧⟨   For this specification the MSL is taken to be 2 minutes.  This is an⟩——两份读数对账闭合 0; 793 的术语表另有 ⟦793⟧⟨          the internetwork system.  Arbitrarily defined to be 2 minutes.⟩, “Arbitrarily defined to be ” 之后读出 2 分钟, 与正文那句一致(闭合 0)。状态图里那枚超时器 ⟦793⟧⟨   |  rcv FIN       -------------- |    Timeout=2MSL -------------- |  ⟩ 的 “Timeout=” 之后读出 2(闭合 0), 同一枚式样在 9293 的图里再现 1 次。绕回周期由逆向游标自 “approximately every ” 之后取到带小数的全数 4.55 ⟦793⟧⟨  microseconds.  Thus, the ISN cycles approximately every 4.55 hours.⟩, 793 用它反推“只要 MSL 短过绕回周期就安全” ⟦793⟧⟨  the Maximum Segment Lifetime (MSL) and that the MSL is less than 4.55⟩ ⇎ 9293 把同一句重写一遍 4.55(同现份数 2)。时钟步长: 793 的 “incremented roughly every ” 之后读出 4 ⇎ 9293 的 “once every roughly ” 之后读出 4(闭合 0)。谁没给分钟数: “taken to be” 那条定 MSL 的句式在 1 ⇎ 0 ⇎ 0 ⇎ 1 份面上出现 ⇎ “2 minutes” 字样 2 ⇎ 1 ⇎ 0 ⇎ 1 处 ⇎ 分钟数缺席份数 0 ⇎ 1 ⇎ 1 ⇎ 0——6528 全篇不写 MSL 等于几分钟(它把时长推给 “last seen” 1 枚式) ⟦6528⟧⟨   corresponding to the old incarnation was last seen (where "MSL" is⟩ ⇎ 1122 面上有 1 处 “2 minutes”, 但那枚数不在 MSL 定义句里(6528 无分钟定义句的闭合 1)。时长字面账: 逐份“数字+单位”命中 7 ⇎ 16 ⇎ 2 ⇎ 14 处 ⇎ 不同取值 5 ⇎ 11 ⇎ 1 ⇎ 12 枚。
⚖ 头条不是“哪个数更大”, 而是“要不要等、等多久、从哪一刻起算、能不能跳过”: 793 先定数再自毁 ⟦793⟧⟨    TCP implementors may violate the "quiet time" restriction, but only⟩——它明文允许实现者违背自己刚立的 quiet time 限制, 并把 MSL 说成任意取的 2 分钟, 同段还留一句“可由经验改动” ⟦793⟧⟨  is an engineering choice, and may be changed if experience indicates⟩(整句要折平才读得到, 见 ⚙ 行) ⇎ 1122 换成命令式并把出口写进同一句 ⟦1122⟧⟨            TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime).⟩ ⇎ ⟦1122⟧⟨            However, it MAY accept a new SYN from the remote TCP to⟩, 两个条件分别在 ⟦1122⟧⟨            (1)  assigns its initial sequence number for the new⟩ ⇎ ⟦1122⟧⟨            (2)  returns to TIME-WAIT state if the SYN turns out to be⟩ 两行里(重开连接时另发初始号 ⇎ 若那枚 SYN 出自对方已关的死连接就退回 TIME-WAIT), 它还嫌端口占用太久而允许缩短 ⟦1122⟧⟨                 port pair is tied up, some TCPs allow a new SYN to be⟩ ⇎ 6528 干脆取消“等”: 窗口锚在上一段报文最后被见到的时刻 ⟦6528⟧⟨   corresponding to the old incarnation was last seen (where "MSL" is⟩, 判据 ⟦6528⟧⟨   previous connection before 2*MSL have passed since a segment⟩, 并显式挂回旧文的概念与附录 ⟦6528⟧⟨   the TIME-WAIT state and TCP's "quiet time" concept (see Appendix B of⟩; 它同时换了序列号生成法(慢时钟加伪随机) ⟦6528⟧⟨   kept or a quiet time observed for two maximum segment lifetimes⟩ ⇎ 9293 同时收下两家: 逐字保留 793 那句 2 分钟(两份该句逐字同形, 闭合 1), 又收下 1122 的 linger 与两条件 ⟦9293⟧⟨   When a connection is closed actively, it MUST linger in the TIME-WAIT⟩ ⇎ ⟦9293⟧⟨   (1)  assigns its initial sequence number for the new connection to be⟩(该条件句在 9293 面上再现 1 次); 但 793 那句 “the TCP must keep quiet for a maximum segment lifetime” 在 9293 面上按原句读不到(改写判定 1), 主语换成端点 ⟦9293⟧⟨   remaining in the network, the TCP endpoint must keep quiet for an MSL⟩。四份对同一件事给的是四种句式: 许可句 ⇎ 命令句带出口 ⇎ 判据式 ⇎ 命令句+废止声明。
🔁 谁抄谁可以逐字量出来: 归一长行的两两交集 1 ⇎ 0 ⇎ 351 ⇎ 0 ⇎ 逐字节同形 0 ⇎ 0 ⇎ 29 ⇎ 0 ⇎ 仅归一同形 1 ⇎ 0 ⇎ 322 ⇎ 0(配对闭合 0 ⇎ 非零对 4): 最大一对是 793⇎9293 的 29 行(归一 351 ⇎ 仅归一 322 ⇎ 只此两份 350 ⇎ 还压在第三份 1 ⇎ 拆账闭合 0 ⇎ 与配对档闭合 0 ⇎ 闭合 0), 第二对是 6528⇎9293 的逐字节 15 行(归一 16 ⇎ 仅归一 1); 1122⇎9293 归一 16 行却逐字节 0 行——9293 近乎逐字收下 6528 的算法句, 对 1122 只搬走内容、把句子重写。跨两份逐字共现的在册针: a_msl2 ⇎ a_fig ⇎ b_cond1 ⇎ b_cond2 ⇎ d_msl2(旧面在册 1 枚 ⇎ 9293 面上 1 枚), 其中定 MSL 那句 ⇎ Timeout=2MSL 图式 ⇎ 1122 的两条件句全部同时活在旧面与 9293 面上。 名分账: Obsoletes 头 0 ⇎ 0 ⇎ 1 ⇎ 1 ⇎ Updates 头 0 ⇎ 0 ⇎ 1 ⇎ 1 ⇎ STD 头 0 ⇎ 0 ⇎ 0 ⇎ 1 ⇎ ISSN 头 0 ⇎ 0 ⇎ 1 ⇎ 1 ⇎ Standards Track 0 ⇎ 0 ⇎ 1 ⇎ 1: 9293 ⟦9293⟧⟨Obsoletes: 793, 879, 2873, 6093, 6429, 6528,                            ⟩ 一次点名 1 枚 RFC(含 6528 与 6093)——它把“要不要等”的三份答案全部废止, 却又逐字收下第一份那句 2 分钟。引用写法必须三式并计: “RFC-793” 短横式 0 ⇎ 34 ⇎ 0 ⇎ 0 ⇎ “RFC 793” 空格式 0 ⇎ 0 ⇎ 5 ⇎ 60 ⇎ “RFC-1122” 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ “RFC 1122” 0 ⇎ 0 ⇎ 0 ⇎ 25——只认空格式就会把“1122 引 793”读成 34 次为零; 只认短横式则 9293 引 793 的 60 次全读漏。6528 那份被引 8 次只出现在 9293 的废止清单里(旧两份零枚: 闭合另见 ⛓)。
🧪 答句邻域带(以答句行为心、两侧各取 40 行; 带内首行 1812 ⇎ 5119 ⇎ 91 ⇎ 1067 ⇎ 末行 1892 ⇎ 5199 ⇎ 171 ⇎ 1147 ⇎ 答句行 1852 ⇎ 5159 ⇎ 131 ⇎ 1107 ⇎ 带长 3750 ⇎ 3388 ⇎ 3808 ⇎ 4719 ⇎ 带内行 81 ⇎ 81 ⇎ 81 ⇎ 81): 四份的答句各自所属的编号节(向上找最近一枚不含目录引导点的标题) Sequence Numbers ⇎ Closing a Connection: RFC-793 Section 3.5 ⇎ Generation of Initial Sequence Numbers ⇎ Knowing When to Keep Quiet, 四份里定位到编号节的 4 份 ⇎ 与状态图/连接状态同名的 1 份。带内外分账: MSL 带内 3 ⇎ 2 ⇎ 2 ⇎ 5 ⇎ 带外 13 ⇎ 6 ⇎ 0 ⇎ 16(逐份闭合 0 ⇎ 0 ⇎ 0 ⇎ 0) ⇎ TIME-WAIT 带内 0 ⇎ 3 ⇎ 3 ⇎ 0 ⇎ 带外 28 ⇎ 5 ⇎ 1 ⇎ 47(闭合 0 ⇎ 0 ⇎ 0 ⇎ 0) ⇎ 数字符带内 23 ⇎ 38 ⇎ 113 ⇎ 26 ⇎ 带外 1376 ⇎ 5334 ⇎ 776 ⇎ 5059(闭合 0 ⇎ 0 ⇎ 0 ⇎ 0, 三轨合计 0)。带口径下的密度对照: 6528 的答句行在第 131 行、带内 MSL 2 枚 ⇎ 793 的答句行在第 1852 行、带内 MSL 3 枚 ⇎ 9293 同一句却落在第 1107 行——四份都把答案埋在正文中段, 带外余量 16 枚 MSL 说明 9293 通篇仍在别处反复引用这个时长。
⚙ 三面阶梯在本条只走到两阶, 而这两阶必需: 在册 28 枚答句针按原面(逐行)读到 8 ⇎ 7 ⇎ 4 ⇎ 6 枚 ⇎ 全篇折平读到 9 ⇎ 8 ⇎ 4 ⇎ 7 ⇎ 摘壳折平读到 9 ⇎ 8 ⇎ 4 ⇎ 7(只增不减 1, 摘壳−折平 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 被壳挡住的针 0 枚): 9293 零换页符, 剥壳对它是空操作, 所以本条第三档没有新增句。真正的通道是折行: 3 枚针只在折平面存在 ⟦793⟧⟨  is an engineering choice, and may be changed if experience indicates⟩ ⇎ ⟦1122⟧⟨            TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime).⟩ ⇎ ⟦9293⟧⟨   remaining in the network, the TCP endpoint must keep quiet for an MSL⟩——它们所属的整句(“is an engineering choice, and may be changed if experience indicates it is desirable to do so.” ⇎ “it MUST linger in TIME-WAIT state for a time 2xMSL (Maximum Segment Lifetime). However, it MAY accept a new SYN” ⇎ “the TCP endpoint must keep quiet for an MSL before assigning any sequence numbers upon starting up or recovering from a situation where memory of sequence numbers in use was lost.”) 全被行界劈开, 逐行口径一律零命中(闭合 0), 按份新增 1 ⇎ 1 ⇎ 0 ⇎ 1 枚(清单 a_eng_whole ⇎ b_two_both ⇎ d_quiet_whole)。最锋利的一处: 1122 把“MUST 等两枚 MSL”与“MAY 立刻接受新 SYN”写进同一句而中间隔着行界——只按行搜 “MUST linger” 就读不到它自带的出口; 793 的“这是工程选择”被劈在 “is an engineering choice, and” 与后半句之间, 而那半句正是它允许违背 quiet time 的免责根据。
📏 义务语气换代是第二根轴: 大写 MUST 全形 0 ⇎ 200 ⇎ 4 ⇎ 228 ⇎ 裸 MUST(不含 MUST NOT) 0 ⇎ 180 ⇎ 2 ⇎ 221 ⇎ MUST NOT 0 ⇎ 20 ⇎ 2 ⇎ 7 ⇎ SHOULD 0 ⇎ 73 ⇎ 3 ⇎ 40 ⇎ MAY 0 ⇎ 41 ⇎ 1 ⇎ 58(逐份账闭合 0 ⇎ 0 ⇎ 0 ⇎ 0): 793 面上大写义务词 0 枚——整篇用小写 must/should 与 “may violate” 这类许可句, 那套大写词表比它晚十年; 1122 ⇎ 9293 把命令式抬到 200 ⇎ 228 枚, 而 6528 只有 4 枚——它是实验性提案而不是要求。同一条 linger 规则的语气换代可读: 793 用许可(“may violate”) ⇎ 1122 用 MUST linger + MAY accept ⇎ 9293 用同一枚 MUST 但把 quiet 的义务主体改成 endpoint。词面密度: “TIME-WAIT state” 整语 3 ⇎ 7 ⇎ 4 ⇎ 10 ⇎ 连字式减整语余量 25 ⇎ 1 ⇎ 0 ⇎ 37 ⇎ 无连字符写法 1 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ keep-alive 0 ⇎ 10 ⇎ 0 ⇎ 6 ⇎ Timestamp 0 ⇎ 34 ⇎ 0 ⇎ 11 ⇎ ISS 25 ⇎ 10 ⇎ 1 ⇎ 25 ⇎ ISN 12 ⇎ 1 ⇎ 38 ⇎ 20 ⇎ “32 bit/32-bit” 6 ⇎ 2 ⇎ 1 ⇎ 5 ⇎ reboot 0 ⇎ 0 ⇎ 0 ⇎ 14: 6528 一份里 ISN 字样 38 枚 ⇎ MSL 只有 2 枚——它把论证重心从“等多久”挪到“怎么发号”。9293 的 reboot 14 处是四份里唯一把这当作时钟丢失场景来讲的一份。
🧩 写法轴与池代数: 归一长行池 9149 条按“压在几份里”分档 8767 ⇎ 381 ⇎ 1 ⇎ 0(分档闭合 0 ⇎ 容斥并集闭合 0 ⇎ 并集 9149 ⇎ 只在本份 1633 ⇎ 3804 ⇎ 358 ⇎ 2972), 三份同现 1 条 ⇎ 四份同现 0 条——四份同现零枚, 所以“逐字节同形 ⇎ 只差一根写法轴”那两档在本条空转(轴账闭合 0, 分档 1 枚非零: case0⇎hyph0⇎space1⇎multi0); 唯一那条三源同现的长行是状态机记号 ⟦793⟧⟨        <SEQ=0><ACK=SEG.SEQ+SEG.LEN><CTL=RST,ACK>⟩(归一长度对账 0, 实际压在 3 份面上), 它在三三交 0 ⇎ 1 ⇎ 0 ⇎ 0 里占 793⇎1122⇎9293 那一枚(1)——三份共抄同一张状态转换记号行而各写散文。锚候选池 10737 条按标签 2357 ⇎ 4200 ⇎ 405 ⇎ 3775 ⇎ 按出现份数 8128 ⇎ 2450 ⇎ 123 ⇎ 36(标签闭合 0 ⇎ 份数闭合 0)。2MSL 四式并计: 连字式 1 ⇎ 0 ⇎ 0 ⇎ 2 ⇎ 乘号式 0 ⇎ 3 ⇎ 0 ⇎ 1 ⇎ 星号式 0 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 带空格 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 合计 1 ⇎ 4 ⇎ 1 ⇎ 3 ⇎ 同面并存式数 1 ⇎ 2 ⇎ 1 ⇎ 2 ⇎ 各式出现的份数 2 ⇎ 2 ⇎ 2 ⇎ 0——1122 与 9293 各自同时写两种式样(并存 2 ⇎ 2 式), 6528 只用星号式, 793 只在图里用连字式; 只按一种式样搜就会把另外三份读成“没有这条规则”。

## ⛓解读注

第四遍(`corpus/_fill69.py`)换算法不换定义地重跑一遍: 读面走 bytes 再 decode ⇎ 行数按 `count('\n')+1` ⇎ 针计数按 `len(re.findall(re.escape(针), 面))` ⇎ 归一走空白类整体替换 ⇎ 五枚读数由带捕获组的正则一次到位 ⇎ 带的定位先找答句行再取 ±40 行切片 ⇎ 搬运算账走 set 代数 ⇎ 义务语气走词界正则。
本遍共复算 233 个键(扁平表 224 键中覆盖 223 枚, 缺 1 ⇎ 多 10 ⇎ 不符 0); 面内恒等式 27 条按本注读数重跑全部为真; DERIV 101 条复算点在本注的读数上重跑全对(引用 624 处)。

| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |
|---|---|---|---|
| 行数⇎换行 | `split('\n')` 计格 ⇎ `count('\n')+1` 计枚 ⇎ `splitlines()` 第三式 | 5248 ⇎ 6845 ⇎ 676 ⇎ 5577 ⇎ splitlines 多出 90 ⇎ 115 ⇎ 11 ⇎ -1 | 三式在 LF 面一致 ⇎ 差值恰为换页符 91 ⇎ 116 ⇎ 12 ⇎ 0 枚——splitlines 认 \x0c 为换行, 谁用它数行数就会把版式读成内容 |
| 编码层 | 字节面看 BOM ⇎ 码位面数非 ASCII ⇎ utf-8 逐字符加字节 | BOM 0 ⇎ 0 ⇎ 0 ⇎ 1 ⇎ 非 ASCII 0 ⇎ 0 ⇎ 0 ⇎ 3 ⇎ 加字节 0 ⇎ 0 ⇎ 0 ⇎ 4 ⇎ 字节−码位 0 ⇎ 0 ⇎ 0 ⇎ 4 | 只有 9293 不干净: 一枚 BOM(+2) ⇎ 两枚 U+00FC(+1 each) ⇒ 3 枚码位带来 4 枚加字节——“非 ASCII 数=字节差”这条默认等式在这里差 1, 所以本条把加字节另立一列 |
| 三面阶梯 | 逐行 in ⇎ 全篇折平成员 ⇎ 自己筛掉页壳行再折平 | 原面 8 ⇎ 7 ⇎ 4 ⇎ 6 ⇎ 折平 9 ⇎ 8 ⇎ 4 ⇎ 7 ⇎ 摘壳 9 ⇎ 8 ⇎ 4 ⇎ 7 | 只增不减(1), 新增的三枚是 a_eng_whole、b_two_both、d_quiet_whole; 摘壳档相对折平 0 ⇎ 0 ⇎ 0 ⇎ 0——9293 零换页符, 剥壳对它是空操作, 这恰好是 B68 的反面(那边第三档才是唯一读到关键句的一档) |
| 句内读数 | 捕获组正则 `(\d+) minutes` ⇎ `(\d+)MSL` ⇎ `(\d+)\.(\d+) hours` | 分钟 2⇎2 ⇎ 术语表 2 ⇎ Timeout 2 ⇎ 微秒 4⇎4 ⇎ 小时整数部分 4 | 四本闭合全归零(分钟 0 ⇎ 术语表 0 ⇎ 微秒 0 ⇎ Timeout 0)。绕回小时本注按 `every (\d+\.\d+) hours` 读到 4.55 ⇎ None ⇎ None ⇎ 4.55——它把 “4.55” 当整枚小数收, 而不是像 793 那句 “less than 4.55” 那样只当字面 |
| 分钟数的缺席档 | “2 minutes” 字样枚数 ⇎ “taken to be” 句式枚数 两式并计 | 2 minutes 2 ⇎ 1 ⇎ 0 ⇎ 1 ⇎ taken-to-be 1 ⇎ 0 ⇎ 0 ⇎ 1 ⇎ 分钟数缺席面 0 ⇎ 1 ⇎ 1 ⇎ 0 | 1122 面上有 1 处 “2 minutes”, 但那枚数不是 MSL 的定义值(它给的是 2xMSL 的式); 6528 面上 1 处分钟字样且 taken-to-be 句式 0 枚 ⇒ 本条的“谁没给时长”不是搜不到字面, 而是搜到了也不构成答案 |
| 2MSL 四式 | 四个独立子串针 + 同面并存计数 | 连字 1 ⇎ 0 ⇎ 0 ⇎ 2 ⇎ 乘号 0 ⇎ 3 ⇎ 0 ⇎ 1 ⇎ 星号 0 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 带空格 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 合计 1 ⇎ 4 ⇎ 1 ⇎ 3 ⇎ 并存 1 ⇎ 2 ⇎ 1 ⇎ 2 | 1122 ⇎ 9293 各自同面并存两式(2 ⇎ 2), 6528 只用星号式, 793 只在状态图里用连字式; 单式搜索会把另外三份读成“没有这条规则” |
| 义务语气 | 本注走词界正则 `\bMUST\b` ⇎ `\bMUST NOT\b`, 与建条目侧的子串档对账 | 大写 MUST 0 ⇎ 200 ⇎ 4 ⇎ 228 ⇎ 裸 0 ⇎ 180 ⇎ 2 ⇎ 221 ⇎ MUST NOT 0 ⇎ 20 ⇎ 2 ⇎ 7 ⇎ MAY 0 ⇎ 41 ⇎ 1 ⇎ 58 ⇎ SHOULD 0 ⇎ 73 ⇎ 3 ⇎ 40 | 逐份账 0 ⇎ 0 ⇎ 0 ⇎ 0(正则档与子串档必须互相咬合才归零)。793 面上大写义务词 0 枚——它比 RFC 2119 的语气表早十年, 同一条规则在 793 是许可句(“may violate”), 到 1122 变 MUST, 到 9293 仍是 MUST 但义务主体换成 endpoint |
| 改写判定 | 把 793 的 keep-quiet 整句归一后在 9293 折平面上查成员 | 读到原句=0(0=读到, 即失败态) | 9293 收下 793 的“MSL=2 分钟”却把 “the TCP must keep quiet for a maximum segment lifetime” 换成 endpoint 说法——逐字搬运与语气改写在同一份文档里同时发生, 所以“9293 只是排版重写”这个读法站不住 |
| 搬运⇎重写 | 长行集合代数(MINLEN=24): 逐字节交 ⇎ 归一交 ⇎ 仅归一 ⇎ 只此两份 ⇎ 三份同压 | 归一 1 ⇎ 0 ⇎ 351 ⇎ 0 ⇎ 16 ⇎ 16 ⇎ 逐字节 0 ⇎ 0 ⇎ 29 ⇎ 0 ⇎ 0 ⇎ 15 ⇎ 仅归一 1 ⇎ 0 ⇎ 322 ⇎ 0 ⇎ 16 ⇎ 1 ⇎ 非零对 4 | 793⇎9293 归一 351(逐字节 29 ⇎ 只此两份 350 ⇎ 三份同压 1) ⇎ 6528⇎9293 逐字节 15 ⇎ 1122⇎9293 逐字节 0——同一份 9293 对三家做了三种不同的事: 逐字搬   搬了重写   几乎不搬 |
| 池代数 | dict-of-set 计数 ⇎ 集合差算“只在本份” | 池 9149 ⇎ 分档 8767 ⇎ 381 ⇎ 1 ⇎ 0 ⇎ 只在本份 1633 ⇎ 3804 ⇎ 358 ⇎ 2972 ⇎ 并集 9149 | 容斥闭合 0 ⇎ 分档闭合 0; 四份同现 0 枚⇒“只差一根写法轴”的对照档空转, 三源同现那枚是状态机记号行 <seq=0><ack=seg.seq+seg.len><ctl=rst,ack> |
| 带内外三轨 | ±40 行邻域带, 先定位答句行再切片, 标题按归属口径自答句行向上扫 | 带起 1812 ⇎ 5119 ⇎ 91 ⇎ 1067 ⇎ 带止 1892 ⇎ 5199 ⇎ 171 ⇎ 1147 ⇎ 答句行 1852 ⇎ 5159 ⇎ 131 ⇎ 1107 ⇎ 带长 3750 ⇎ 3388 ⇎ 3808 ⇎ 4719 | 三轨闭合合计 0; 带内 MSL 3 ⇎ 2 ⇎ 2 ⇎ 5 ⇎ 带外 13 ⇎ 6 ⇎ 0 ⇎ 16——9293 把同一句埋在比 793 早得多的位置(第 1107 行 ⇎ 第 1852 行), 而 6528 的带外 MSL 余量为 0 枚: 它全篇只在那一句里用 MSL; 标题若改从带首行向下扫, 四份里只有 793 改口——归属口径给第 1597 行(§Sequence Numbers), 向下扫给第 1979 行(§Establishing a connection), 因为带是等长的行窗而不是节界 |
| 锚双轨 | 一枚锚同时按“等于某原文件行”⇎“其归一式落在折平面里”两种成员判 | 正文 26 处 ⇎ 去重 22 串 ⇎ 两轨同判 13 ⇎ 分歧 9 | 归属错配 0 ⇎ 一源 13 ⇎ 跨源 9 ⇎ 四源 0; 跨源那批全部落在 9293 面上(逐字收下的句子只存在于被抄的那一侧) |
| 引用写法族 | 短横族 ⇎ 空格式分开数, 不把 “RFC-793” 折成 “RFC 793” | RFC-793 0 ⇎ 34 ⇎ 0 ⇎ 0 ⇎ RFC 793 0 ⇎ 0 ⇎ 5 ⇎ 60 ⇎ RFC 1122 0 ⇎ 0 ⇎ 0 ⇎ 25 | 1122 引 793 全走短横式(34 枚), 9293 引 793 全走空格式(60 枚)——规范化一次就会把两代文书的引用网读成一团; 数“被引了几次”时数字串轨与 RFC 前缀轨不等: 6528 在自己面上 13 ⇎ 11 枚 ⇎ 在 9293 面上 8 ⇎ 4 枚(DOI 里的 RFC6528 ⇎ URL 里的 rfc6528 不带空格), 所以本注把两轨分开记 |
| 针的口径 | 建条目侧用有序三选一(“32 bit ISN” ⇎ “32-bit counter” ⇎ “32 bit”), 本注用逐枚游标扫描复现它, 另记字符类 `32[ -]bit` 一档 | 三选一口径 6 ⇎ 2 ⇎ 1 ⇎ 5 ⇎ 字符类口径 6 ⇎ 7 ⇎ 2 ⇎ 10 | 两式在 793 上同值(6 ⇎ 6), 在另外三份上字符类多读 5 ⇎ 1 ⇎ 5 枚——有序选一会把 “32-bit” 里非 counter 的那些枚整个放过; 本注另用逐枚游标扫描(命中即跳过整枚针)复现了有序选一, 两式读数与建条目侧逐份全等 |
| 名分账 | 头部字段按 `^Obsoletes:` ⇎ `^Updates:` ⇎ `^STD:` ⇎ `^ISSN:` 逐行正则 | Obsoletes 0 ⇎ 0 ⇎ 1 ⇎ 1 ⇎ Updates 0 ⇎ 0 ⇎ 1 ⇎ 1 ⇎ STD 0 ⇎ 0 ⇎ 0 ⇎ 1 ⇎ ISSN 0 ⇎ 0 ⇎ 1 ⇎ 1 ⇎ Standards Track 0 ⇎ 0 ⇎ 1 ⇎ 1 | 6528 自己挂着 Obsoletes/Updates 头(它废止旧文并被 9293 再废止), 9293 一页点名含 6528 的清单; STD: 头只有 9293 有, 但 “Category: Standards Track” 两枚都有(0 ⇎ 0 ⇎ 1 ⇎ 1)——名分字段与类别行不能互相代读 |

### 本注的判断
四份文书对“主动关掉一条连接之后”给的不是同一个问题的四个答案, 而是四个问题的各一个答案: 793 回答“等多久”(2 枚 MSL, 且 MSL=2 分钟是任意取的工程常数)并顺手承认可以不回答“要不要等”(明文许可违背 quiet time); 1122 回答“必须等”(MUST linger)却把“能不能跳过”写进同一句的两个条件里; 6528 拒绝回答“等多久”, 把问题换成“从上一段报文最后被见到起过了几枚 MSL”; 9293 回答“谁承担这个义务”(TCP endpoint 而非 TCP), 同时把前三份一起废止。所以任何“取最大值/取最新”式的合并都会丢东西: 按时间最新取 9293, 就丢掉 6528 的起算点改法; 按字面最全取 793, 就丢掉 1122 那两条件出口——而 9293 恰恰同时收下 793 的分钟句与 1122 的条件句, 却在 keep-quiet 那句上做了主语手术。逐字节交(29 枚 ⇎ 1122 方向 0 枚 ⇎ 6528 方向 15 枚)与归一交(351 ⇎ 16 ⇎ 16) 分成两套账, 正是这场“收内容 ⇎ 改语气”双轨操作的量证。
另有两处容易被读成矛盾而其实不是: 其一, 793 全篇大写 MUST 零枚, 不是它没有义务语句, 而是它用小写 must 与许可句写义务, 所以“按 RFC 2119 关键词搜 793 得零命中”是搜索口径的产物而非规范的产物; 其二, 6528 面上 “2 minutes” 零枚而 “MSL” 只 2 枚, 不是它不谈时长, 而是它把时长写成乘法式 `2*MSL` 并把 MSL 的值推给被引文书——时长字面的缺席与判据的存在可以同时为真。
### 不可由在库文件判定(只写在这里, 不进判词与门槛)
四份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; rfc-editor.org 此刻给这四份挂的现行状态页与勘误页(6528 现在被标成 Historic 还是 Experimental, 在库字节里读不出来); 此后哪份在途草案又动了 TIME-WAIT 这一段; 现网内核实际把 TIME-WAIT 设成多久(“2MSL ⇎ 5 秒 ⇎ 可 sysctl 覆盖”这类都是实现事实, 不是文书事实); RFC 2119 关键词表相对 793 的年代差只能由常识给出, 在库四份文件自身不写“793 早于 2119”; 9293 的 BOM 是抓取链条上哪一环加上去的, 还是 RFC Editor 的原版面自带。
以上量要么在本机之外、要么随实现与站点漂移, 复算通道里没有它们的位置; 门槛只认在库字节。
