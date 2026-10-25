# B61 一条链路至少要装多少字节、一个 IPv6 包最大能多大，五份规范五种答法：576 ⇎ 1280 ⇎ 只留一句“已改成 1280” ⇎ 拆掉 65 535 上限 ⇎ 通篇不提任何下限（下限句 1⇎1⇎1 句，3 处读数被排版折行）
src: rfc1883.txt (82089 字节／面内 82089 字符／非空行 1315／下限句 1 处／576×1280 9⇎0 处) ⇎ rfc2460.txt (85890 字节／面内 85890 字符／非空行 1387／下限句 1 处／576×1280 1⇎10 处) ⇎ rfc8200.txt (93162 字节／面内 93162 字符／非空行 1488／下限句 1 处／576×1280 0⇎8 处) ⇎ rfc2675.txt (17320 字节／面内 17320 字符／非空行 303／下限句 0 处／576×1280 0⇎0 处) ⇎ rfc8201.txt (42751 字节／面内 42751 字符／非空行 682／下限句 0 处／576×1280 0⇎0 处) (五份 RFC Editor 纯文本面, 全 LF、全 ASCII。数字一律从面内现读, 一个都不手填; 抓取时刻、官网现行状态与勘误表是否已挂新版只在本机或站外成立, 不进门槛)
；联结不是“同一份数据的两种序列化”, 而是“一条链路至少要装多少字节、一个包最大能多大”在五份一手规范里的五种答法: 下限句现读 95 初版 576 ⇎ 98 标准 1280 ⇎ 17 现行 1280 ⇎ 超大包档 无 ⇎ PMTUD 档 无; 576 字面 9⇎1⇎0⇎0⇎0 处 ⇎ 1280 0⇎10⇎8⇎0⇎0 处, 而 98 标准那一枚 576 只活在变更记录窗 1 处(正文 0 处): 那句“把最小 MTU 从 576 改成 1280”就是它的全部残留; 净载荷算式成对读数 528/576⇎1232/1280⇎无; 包顶写法只有带千分位一种: 65,535 5⇎1⇎1⇎17⇎0 处 ⇎ 无逗号 65535 全库 0, 超大包档另给 4,294,967,295 1 处; 超大包选项: 定义逐字面 10⇎0⇎0⇎26⇎0 处 ⇎ jumbo 全族 15⇎4⇎0⇎63⇎0 处, 98 标准用一句 1 处“全部移除”说明它; 分片主语三份逐字同现(原面搜后半截 0 处 ⇎ 折平 1⇎1⇎1 处); 义务词体例: 全大写 MUST/SHOULD/MAY 五份 0⇎0⇎0⇎0⇎0 处, 小写 must 62⇎56⇎52⇎8⇎28 处, PMTUD 档两处自陈“只用小写、不引 2119 定义”(2119 引用 7 次); 整行共用 95⇎98 576 行 ⇎ 98⇎17 424 行 ⇎ 17⇎超大包 0 行 ⇎ 三份同现 343 行。
tags: 最小链路 MTU 句式谓词 正文⇎变更记录两窗分档 数 token 后邻符号分档闭合 带千分位⇎无逗号两档 超大包定义⇎自我移除⇎实验档接走 原面⇎折平双档(分片后半截查无) 全大写义务词五份皆零 小写自陈体例 整行容斥 无一下限数字的 MTU 专文 锚归属由正文现推 闭合账 标量 2⇎清单 6 项
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/ipv6/rfc1883.txt

The Jumbo Payload option is used to send IPv6 packets with payloads longer than 65,535 octets.

(Note: unlike IPv4, fragmentation in IPv6 is performed only by source nodes, not by routers along a packet's

Note that this means the payload may have to be reduced to 528 octets (576 minus 40 for the IPv6 header and 8 for the Fragment header), and smaller still if additional extension headers are used.

### ⟦B⟧ ⟸ corpus/raw/ipv6/rfc2460.txt

(Note: unlike IPv4, fragmentation in IPv6 is performed only by source nodes, not by routers along a packet's

On any link that cannot convey a 1280-octet packet in one piece, link-specific fragmentation and reassembly must be provided at a layer below IPv6. Links that have a configurable MTU (for example, PPP links [RFC- 1661]) must be configured to have an MTU of at least 1280 octets; it is recommended that they be configured with an MTU of 1500 octets or greater, to accommodate possible encapsulations (i.e., tunneling) without incurring IPv6-layer fragmentation.

Note that this means the payload may have to be reduced to 1232 octets (1280 minus 40 for the IPv6 header and 8 for the Fragment header), and smaller still if additional extension headers are used.

02) Removed all references to jumbograms and the Jumbo Payload option (moved to a separate document).

01) In section 5, changed the minimum IPv6 MTU from 576 to 1280 octets, and added a recommendation that links with configurable MTU (e.g., PPP links) be configured to have an MTU of at least 1500 octets.

### ⟦C⟧ ⟸ corpus/raw/ipv6/rfc8200.txt

(Note: unlike IPv4, fragmentation in IPv6 is performed only by source nodes, not by routers along a packet's

On any link that cannot convey a 1280-octet packet in one piece, link- specific fragmentation and reassembly must be provided at a layer below IPv6. Links that have a configurable MTU (for example, PPP links [RFC1661]) must be configured to have an MTU of at least 1280 octets; it is recommended that they be configured with an MTU of 1500 octets or greater, to accommodate possible encapsulations (i.e., tunneling) without incurring IPv6-layer fragmentation.

### ⟦D⟧ ⟸ corpus/raw/ipv6/rfc2675.txt

Abstract A "jumbogram" is an IPv6 packet containing a payload longer than 65,535 octets.

This document specifies an IPv6 hop-by-hop option, called the Jumbo Payload option, that carries a 32-bit length field in order to allow transmission of IPv6 packets with payloads between 65,536 and 4,294,967,295 octets in length.

### ⟦E⟧ ⟸ corpus/raw/ipv6/rfc8201.txt

Consequently, although RFC 1981 used the "should/must" style language in upper and lower case, this document does not cite the RFC 2119 definitions and only uses lower case for these words.

When source fragmentation is available, EMTU_S is set to EMTU_R, as indicated by the receiver using an upper-layer protocol or based on protocol requirements (1500 octets for IPv6). When a message larger than PMTU is to be transmitted, the source creates fragments, each limited by PMTU.

o Added a "Note" to the introduction to document that this specification doesn't cite RFC 2119 and only uses lower case "should/must" language.

## ⟪BabelTele⟫
🧭 五源字节 82089 ⇎ 85890 ⇎ 93162 ⇎ 17320 ⇎ 42751: 95 初版 ⇎ 98 标准 ⇎ 17 现行 ⇎ 超大包档 ⇎ PMTUD 档; 面内字符 82089 ⇎ 85890 ⇎ 93162 ⇎ 17320 ⇎ 42751 ⇎ 原文件行 2076 ⇎ 2188 ⇎ 2356 ⇎ 508 ⇎ 1068 ⇎ 非空行 1315 ⇎ 1387 ⇎ 1488 ⇎ 303 ⇎ 682 ⇎ 最长行 73 ⇎ 72 ⇎ 72 ⇎ 72 ⇎ 72 列 ⇎ 图框行(两端竖线) 99 ⇎ 97 ⇎ 86 ⇎ 2 ⇎ 0 行。五份全是 LF 面: 回车符 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 枚、非 ASCII 字符 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 枚, 而行尾空格 37 ⇎ 39 ⇎ 42 ⇎ 9 ⇎ 19 处——排版只在行内动, 不换行序。形状量另用独立算法复算(逐字符计数代 len, 数换行代 split), 两法之差逐份 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0。五份签名 5 种(blake2b 前 16 位)。
📐 最小链路 MTU 只由一个句式给出: every link … have an MTU of + 数字 + octets or greater。折叠面现读: 95 初版 ['576'] ⇎ 98 标准 ['1280'] ⇎ 17 现行 ['1280'] ⇎ 超大包档 [] ⇎ PMTUD 档 []; 该句式命中 1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0 句。字面出现处 576 9 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 1280 0 ⇎ 10 ⇎ 8 ⇎ 0 ⇎ 0: 576 九处全在 95 初版的 §5 里(§5 内 9 处 ⇎ 正文他处 0 处), 而 98 标准的 1280 十处中 §5 占 9 处、17 现行的 1280 八处中 §5 占 6 处——同一节被整体重写了一次。净载荷下限由括号算式给出: 95 初版 528=576−48 ⟦A⟧⟨   payload may have to be reduced to 528 octets (576 minus 40 for the⟩ ⇎ 98 标准 1232=1280−48 ⟦B⟧⟨   payload may have to be reduced to 1232 octets (1280 minus 40 for the⟩; 成对读数 1⇎1⇎ 17 现行 0 对——现行版把“至少要能装多少净载荷”这句删了, 只留 1280 本身 ⟦C⟧⟨   any link that cannot convey a 1280-octet packet in one piece, link-⟩。PMTUD 档不答这题: 576 0 处 ⇎ 1280 0 处 ⇎ 528 0 处, 它只引用别处的 ⟦E⟧⟨   requirements (1500 octets for IPv6).  When a message larger than PMTU⟩。
⚖ 墓碑在哪个窗口: 变更记录附录的定位行按“整行扫、两支同收(“Appendix 字母.  Changes…” ⇎ “This memo has the following changes from…”)、取最后一处命中”定位(目录页也印着同一枚标题), 行号 0 ⇎ 1985 ⇎ 2137 ⇎ 0 ⇎ 923(0=无此附录), 命中 0 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 1。以该行为界把整篇切成 正文 ⇎ 变更记录 两窗, 五份分别读: 576 正文 9 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 变更记录 0 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0, 1280 正文 0 ⇎ 9 ⇎ 7 ⇎ 0 ⇎ 0 ⇎ 变更记录 0 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0, 两半相加减全量 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0。于是 98 标准里 576 只剩一处, 且落在变更记录窗内: ⟦B⟧⟨    01) In section 5, changed the minimum IPv6 MTU from 576 to 1280⟩——它不是链路要求, 是“本节把 576 改成 1280”的自我说明; 而 17 现行连这一处也没有(正文 0 ⇎ 变更记录 0)。同一枚附录窗对超大包同样成立: Jumbo 大写 95 初版正文 15 处 ⇎ 98 标准正文 0 处、变更记录 2 处 ⟦B⟧⟨    02) Removed all references to jumbograms and the Jumbo Payload⟩ ⇎ 17 现行 0⇎0 处。判“这条要求还在不在”只能先判窗口: 数出现处会把 98 标准读成仍然要求 576 的一份文书。
🔁 数 token 的后邻符号分档(逐字符判, 窗口九字符): 576 在 95 初版的九处 = 连字符单位 1 + 空格单位 3 + 折行单位 2 + 逗号 1 + 句号 1 + 其余 1, 合计 9(闭合 0); 1280 在 98 标准的十处 = 1+3+2+1+1+2 = 10(闭合 0), 17 现行 8 处同构 3⇎2。两代用的是同一套句式骨架, 换的只有数字: 单位后缀的四种相邻符号在两代里各自成对出现。值域写法只有一种: 65,535 带千分位 5 ⇎ 1 ⇎ 1 ⇎ 17 ⇎ 0 处 ⇎ 无逗号 65535 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处 ⇎ 差 5 ⇎ 1 ⇎ 1 ⇎ 17 ⇎ 0; 独立 token 档 5 ⇎ 1 ⇎ 1 ⇎ 17 ⇎ 0(其余被行尾标点或非数字隔开)。576 的子串档 9 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 独立 token 档 9 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0, 差 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处; 4,294,967,295 只在超大包档 1 处 ⟦D⟧⟨   IPv6 packets with payloads between 65,536 and 4,294,967,295 octets in⟩。
🧪 超大包的一条生命线: jumbo 忽略大小写 15 ⇎ 4 ⇎ 0 ⇎ 63 ⇎ 0 处 ⇎ 大写 Jumbo 15 ⇎ 2 ⇎ 0 ⇎ 49 ⇎ 0 处 ⇎ “Jumbo Payload option”逐字面 10 ⇎ 0 ⇎ 0 ⇎ 26 ⇎ 0 处。95 初版把它写进正文选项定义 ⟦A⟧⟨       The Jumbo Payload option is used to send IPv6 packets with⟩; 98 标准正文 0 处, 只在变更记录留一句移除说明 ⟦B⟧⟨    02) Removed all references to jumbograms and the Jumbo Payload⟩(选项定义逐字面 0 处); 17 现行 0 处——整词也不提; 超大包档把它接回去: 63 处、选项定义 26 处, 定义句 ⟦D⟧⟨   A "jumbogram" is an IPv6 packet containing a payload longer than⟩, 载荷值域 ⟦D⟧⟨   IPv6 packets with payloads between 65,536 and 4,294,967,295 octets in⟩。PMTUD 档 0 处。同一件事在“标准正文 ⇎ 标准的变更记录 ⇎ 现行标准 ⇎ 实验档”四个位置各有读数: 98 标准的 Jumbo 大写 2 处里有 2 处落在变更记录窗内(正文 0 处)。分档合计: jumbo 小写窗内 0 ⇎ 0 ⇎ 0 ⇎ 14 ⇎ 0 ⇎ 窗外 0 ⇎ 2 ⇎ 0 ⇎ 0 ⇎ 0, 大写 15 ⇎ 0 ⇎ 0 ⇎ 49 ⇎ 0 ⇎ 0 ⇎ 2 ⇎ 0 ⇎ 0 ⇎ 0, 闭合 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0。
⛓ 折行通道(原面逐字面 ⇎ 整篇空白折平后逐字面): “not by routers”原面 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处 ⇎ 折平 1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0 处, 差 1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0; 三文书逐字共有的分片主语句 ⟦A⟧⟨   IPv4, fragmentation in IPv6 is performed only by source nodes, not by⟩ 里, 后半截“not by routers”一律被排到下一行行首——用单空格短语搜这份库, 五份全部报“没有这句话”, 而它恰是 IPv6 与 IPv4 最关键的一条分片差别。同一通道对单位写法成立: “1280 octets”原面 0 ⇎ 3 ⇎ 3 ⇎ 0 ⇎ 0 ⇎ 折平 0 ⇎ 6 ⇎ 5 ⇎ 0 ⇎ 0, 差 0 ⇎ 3 ⇎ 2 ⇎ 0 ⇎ 0; 对选项名亦然: “Jumbo Payload option”原面 10 ⇎ 0 ⇎ 0 ⇎ 26 ⇎ 0 ⇎ 折平 10 ⇎ 1 ⇎ 0 ⇎ 27 ⇎ 0, 差 0 ⇎ 1 ⇎ 0 ⇎ 1 ⇎ 0。分片词族本身不受此通道影响: “performed only by source nodes”原面 1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 折平 1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0 处, 差 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0; fragment 忽略档 139 ⇎ 137 ⇎ 209 ⇎ 3 ⇎ 18 ⇎ 词界档 91 ⇎ 87 ⇎ 140 ⇎ 3 ⇎ 2 ⇎ “fragment header”21 ⇎ 18 ⇎ 33 ⇎ 3 ⇎ 1 ⇎ “fragmentation and reassembly”1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 2。
📏 义务词体例反了: 2119 规定的四枚全大写词在库里一处也没有——MUST 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ SHOULD 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ MAY 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ MUST NOT 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处, 全大写族 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处; 小写词界档 must 62 ⇎ 56 ⇎ 52 ⇎ 8 ⇎ 28 ⇎ should 16 ⇎ 14 ⇎ 27 ⇎ 1 ⇎ 25 ⇎ may 28 ⇎ 26 ⇎ 32 ⇎ 7 ⇎ 33 ⇎ required 11 ⇎ 13 ⇎ 14 ⇎ 2 ⇎ 1, 三词合计 106 ⇎ 96 ⇎ 111 ⇎ 16 ⇎ 86 处。首字母大写档 Must 0 ⇎ 0 ⇎ 0 ⇎ 1 ⇎ 0 ⇎ Should 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ May 0 ⇎ 0 ⇎ 2 ⇎ 1 ⇎ 1——超大包档 1 处 Must 出现在例句里而非规定语。PMTUD 档自己说明了体例: 它引用 2119 7 次 ⇎ 另四份 0⇎0⇎0⇎0 次, 并在引言写明 ⟦E⟧⟨   document does not cite the RFC 2119 definitions and only uses lower⟩, 在变更记录写明 ⟦E⟧⟨      specification doesn't cite RFC 2119 and only uses lower case⟩——“only uses lower case”两窗各计 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 1 处, “不引用 2119 定义”之说 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 2 处。关键词样板(key words)另 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 1 处 ⇎ 规定全大写体例的那份编号文书在此库被引用 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 次。
🗓 MTU 语汇密度与题量不成比例: MTU 忽略档 24 ⇎ 27 ⇎ 27 ⇎ 11 ⇎ 219 ⇎ 大写 MTU 24 ⇎ 27 ⇎ 27 ⇎ 11 ⇎ 219 ⇎ “link mtu”3 ⇎ 3 ⇎ 5 ⇎ 2 ⇎ 16 ⇎ “path mtu”9 ⇎ 10 ⇎ 6 ⇎ 2 ⇎ 65 ⇎ PMTU 缩写 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 109 ⇎ “packet too big”1 ⇎ 3 ⇎ 3 ⇎ 0 ⇎ 28。PMTUD 档 219 处 MTU 而 0 处任何 MTU 下限数字: 576 0 ⇎ 1280 0 ⇎ 65,535 0——它整篇只讲“怎么量到路径上最小的一环”, 那个最小的环是多少字节由别人规定。缩写档在两代标准里 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 109 处, 只在 PMTUD 档 109 处; “path mtu”折行档比原面多 0 ⇎ 1 ⇎ 3 ⇎ 0 ⇎ 0 处。“at least + 数字”句式 2 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0 处(95 初版 2 ⇎ 98 标准 1 ⇎ 17 现行 1), 后接数字者才计——它把下限句与推荐句(“MTU of 1500 octets or greater”⟦B⟧⟨   is recommended that they be configured with an MTU of 1500 octets or⟩)同形并列, 只能读数字不能读句式。
🧾 体例与身份: Obsoletes 头 0 ⇎ 1 ⇎ 1 ⇎ 1 ⇎ 1 行 ⇎ Updates 头 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 行 ⇎ “obsoleted by”0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 1 处 ⇎ Experimental 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处 ⇎ 勘误提及 0 ⇎ 0 ⇎ 6 ⇎ 0 ⇎ 1 处。变更记录条目行(缩进至多四空格后接“0N) ”) 0 ⇎ 24 ⇎ 0 ⇎ 0 ⇎ 0 行——98 标准 24 行自我说明, 另四份 0 行; 附录标题行命中 0 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 1 份, 行号 0 ⇎ 1985 ⇎ 2137 ⇎ 0 ⇎ 923。章节号行 20 ⇎ 21 ⇎ 26 ⇎ 15 ⇎ 17 行 ⇎ 去重 18 ⇎ 21 ⇎ 26 ⇎ 15 ⇎ 17 个; “section 数字”引用 10 ⇎ 29 ⇎ 33 ⇎ 4 ⇎ 21 处; RFC 引用去重 8 ⇎ 9 ⇎ 29 ⇎ 7 ⇎ 18 枚。“Standards Track”印记 38 ⇎ 40 ⇎ 44 ⇎ 10 ⇎ 21 处 ⇎ 抬头类目行 1 ⇎ 1 ⇎ 1 ⇎ 1 ⇎ 1 行 ⇎ “Experimental”字样 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处: 五份面内一个实验轨标记都没有, 连把上限写成 ⟦D⟧⟨   IPv6 packets with payloads between 65,536 and 4,294,967,295 octets in⟩ 的超大包档也只印标准轨——类目由抬头一行给死, 正文不复述。
⇄ 整行搬运(行长 ≥40 且归一化非空, 排序后两指针求交): 95⇎98 576 行 ⇎ 98⇎17 424 行 ⇎ 95⇎17 357 行 ⇎ 95⇎超大包 6 行 ⇎ 98⇎超大包 25 行 ⇎ 17⇎超大包 0 行 ⇎ 17⇎PMTUD 36 行; 三份同现 343 行, 三份并集 1737 行, 只在本代 95 262 ⇎ 98 230 ⇎ 17 574 行; 容斥闭合 0。候选行集大小 852 ⇎ 887 ⇎ 1012 ⇎ 197 ⇎ 549。17 现行与超大包档整行共用 0 行、与 PMTUD 档只共用 36 行——它换了抬头与页宽排版, 而 §5 那句 1280 要求与 98 标准逐字同现(归一化后同为共用行)。含关键数字的长行(≥55 字符) 95 22 ⇎ 98 14 ⇎ 17 7 ⇎ 超大包 53 ⇎ PMTUD 0 行——PMTUD 档一行也没有: 它的每一个 MTU 数都指回别的文书。
ℒ 方法 ⇒ 面对“同一问题五份文书”, 先问答案由哪个句式给出: 本条把下限做成“every link … have an MTU of × 数字 × octets or greater”谓词, 于是“还要不要 576”有可判口径(['576'] ⇎ ['1280'] ⇎ ['1280'] ⇎ [] ⇎ [] 现读), 而“576 这个词还在不在”是另一回事(9 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0 处, 再按窗口分正文⇎变更记录两档)。其次把窗口判据定死在字节上: 附录标题按整行扫、取最后一处命中, 因为目录页也印着同一枚标题——2137 行才是 17 现行的附录起点, 取首处会读出 7 处为零的假象。再次把量测自身的失败做成键: 原面⇎折平两档的差(1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0⇎0 ⇎ 3 ⇎ 2 ⇎ 0 ⇎ 0⇎0 ⇎ 1 ⇎ 0 ⇎ 1 ⇎ 0)逐档登记, 分片主语句“后半截查无”因此在库里可复算, 不靠注释解释; 数 token 的后邻符号分档相加闭合(0⇎0⇎0), 两窗相减闭合(0⇎0), 容斥闭合(0)——恒零项也占键位, 读得出“这里本可能出错”。义务词全大写档与分片主语句同为“定义上该有、字面上全无”: 前者五份 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处, 后者原面 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处, 两者都不是漏读, 而是体例与排版的真实状态。
✂️ 为什么这份编码比摘要窗口长 ⇒ 五源各 82089 ⇎ 85890 ⇎ 93162 ⇎ 17320 ⇎ 42751 字符, 窗口只能取锚点触到的行; 本条的结论几乎全是跨文书的量: 下限句集要三份标准并排(['576']⇎['1280']⇎['1280']), 墓碑判读要把同一数按两窗分档(576 正文 0 ⇎ 变更记录 1), 超大包命运要四个位置并排(选项定义 10 ⇎ 0 ⇎ 0 ⇎ 26 ⇎ 0 ⇎ 移除说明 0 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 实验档 63 处), 值域写法要逗号档与无逗号档各数一遍(5 ⇎ 1 ⇎ 1 ⇎ 17 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0), 容斥要三份行集全量(1737 行)。尤其“三份文书逐字同写‘分片只由源节点做, 不由路由器做’, 而后半截在每一份里都被折到下一行”这一条, 任何单源单档量测都看不见——它要原面档 0 处与折平档 1 处同时成立才读得出来。读它请按“这个数由哪份文书、以哪个句式、落在正文还是变更记录里给出”来读, 而不是按“少抄了多少原文”。

## ⛓解读注

### 第四遍复测(本注现算, 与前三遍不同路)

| 量 | 本注的写法 | 结果 | 与建条目侧 |
|---|---|---|---|
| 下限句谓词 | have/an/MTU/of/数字/octets/or/greater 逐词连排, 词间空白整段记下; 全单格算严档, 含换行或多格算宽松档 | 宽松 1⇎1⇎1⇎0⇎0 句(读数 [576] ⇎ [1280] ⇎ [1280] ⇎ [空] ⇎ [空]) ⇎ 严档 0⇎0⇎0⇎0⇎0 ⇎ 差 1⇎1⇎1⇎0⇎0(其中含换行 1⇎1⇎1⇎0⇎0) | 与 w_floor_sent ⇎ s_floor_sent ⇎ wrap_gap_floor_sent ⇎ floor_vals 一致 |
| 分片主语句 | 前半截 performed/only/by/source/nodes 连排, 后半截 not/by/routers 连排, 各分严宽两档 | 前半截 1⇎1⇎1⇎0⇎0 处(两档同数, 三份逐字同现) ⇎ 后半截 严 0⇎0⇎0⇎0⇎0 ⇎ 宽 1⇎1⇎1⇎0⇎0 ⇎ 差 1⇎1⇎1⇎0⇎0 | 与 s_frag_src ⇎ s_routers ⇎ w_routers ⇎ wrap_gap_routers 一致 |
| 净载荷括号算式 | 数字 + “ octets (” + 数字 + “ minus” 逐字符走位(建条目侧只走到括号) | 成对读数 [576=528] ⇎ [1280=1232] ⇎ [] ⇎ [] ⇎ [] | 与 pfloor_pair 一致, 17 现行 0 对 |
| 附录定位 | 整行逐字符判, 两支同收: “Appendix”+大写字母+“.”+一到两格空格+“Changes” ⇎ “This memo has the following changes from”(98 标准走第二支); 取**最后一处**命中 | 行号 0⇎1985⇎2137⇎0⇎923 ⇎ 命中 0⇎1⇎1⇎0⇎1 份 | 与 clo_line ⇎ clo_found 一致 |
| 两窗分档 | 以该行切正文⇎变更记录, 逐行 count 相加(建条目侧按字符偏移切面) | 576 9⇎0⇎0⇎0⇎0⇎0⇎1⇎0⇎0⇎0 ⇎ 1280 0⇎9⇎7⇎0⇎0⇎0⇎1⇎1⇎0⇎0 ⇎ 65,535 5⇎1⇎1⇎17⇎0⇎0⇎0⇎0⇎0⇎0 ⇎ Jumbo 15⇎0⇎0⇎49⇎0⇎0⇎2⇎0⇎0⇎0, 两半相加闭合 0⇎0⇎0⇎0⇎0(四枚 close 键按份相加) | 与 body_ ⇎ tail_ ⇎ close_ 一致 |
| 数 token 后邻七档 | 切片比对 tail.startswith(“-octet”/“ octets”/空白后 octets/逗号/句号/括号) | 576 在 95 初版 1+3+2+1+1+0+1 合计 9 ⇎ 1280 在 98 标准 1+3+2+1+1+0+2 合计 10 ⇎ 65,535 在 超大包档 0+4+0+5+2+0+6 合计 17, 三档闭合皆 0 | 与 sk_* 全部一致 |
| 义务词三档 | 先按非字母数字手工切词, 整词全大写⇎全小写⇎首字母大写分派(采集侧 str.count 子串、建条目侧词界正则) | 全大写 MUST 0⇎0⇎0⇎0⇎0 ⇎ 小写 must 62⇎56⇎52⇎8⇎28 ⇎ 小写 should 16⇎14⇎27⇎1⇎25 ⇎ 小写 may 28⇎26⇎32⇎7⇎33 ⇎ required 11⇎13⇎14⇎2⇎1 ⇎ 首字母 Must 0⇎0⇎0⇎1⇎0 | 五份全大写皆 0, 与 u_/l_/c_ 各档一致 |
| 整行搬运 | 归一同为逐字符滤 alnum, 但交并按小集合建表大集合查表、并集按逐个 add(采集侧用集合运算符 & 与求交并) | 95⇎98 576 ⇎ 98⇎17 424 ⇎ 95⇎17 357 ⇎ 三份同现 343 ⇎ 并集 1737 ⇎ 17⇎超大包 0 | 逐字一致 |
| 锚归属 | 由条目正文 ⟦标签⟧⟨引文⟩ 配对现推, 成员判据用本注的面; 五份都不剥壳(全是纯文本) | 16 处／去重 13 串／一源 10 ⇎ 两至四源 3 ⇎ 五源 0 ⇎ 错配 0 | 与建条目侧、门槛侧同 |
| 两侧对账 | 采集侧 95 键在五份纯文本面上比 | 共有 95 ／ 不符 0 | 五份同为文本面, 无需按介质分流 |

### 读法

一、“还要不要 576”只有下限句谓词能答: 三份标准的句式读数依次是 [576] ⇎ [1280] ⇎ [1280] ⇎ [无] ⇎ [无], 而 576 这个字面在 B 里还剩 1 处、在 C 里 0 处——那一处不在链路要求里, 在变更记录的自我说明里(附录起点取该行 1985, 正文窗 0 处 ⇎ 变更记录窗 1 处)。把两份并排读才看得见“同一代要求换过一次数”: 95 初版 528=576−48 ⇎ 98 标准 1232=1280−48 ⇎ 17 现行成对读数 0 对——括号算式整句被删。
二、包顶只有一个写法: 65,535 一律带千分位。字面 65535 在五份里 0⇎0⇎0⇎0⇎0 处 ⇎ 带逗号写法 5⇎1⇎1⇎17⇎0 处 ⇎ 差 5⇎1⇎1⇎17⇎0 处; 超大包档另给 4,294,967,295 一枚(1 处, 其余四份皆 0)——上限被“拆掉”而不是被“改小”: 同一个带逗号的分片顶在 95 初版 ⇎ 98 标准 ⇎ 17 现行 ⇎ 超大包档 ⇎ PMTUD 档分别是 5⇎1⇎1⇎17⇎0 处。
三、超大包的一条生命线有四个读数: 选项定义逐字面 10 处 ⇎ 98 标准的移除说明 1 处 ⇎ 17 现行 0 处 ⇎ 超大包档 26 处; jumbo 全族 15⇎4⇎0⇎63⇎0 处, 其中 98 标准的 Jumbo 大写 2 处里有 2 处落在变更记录窗内(正文 0 处)。“标准里删掉了 ⇎ 实验档接走了”这两件事各自由一个窗口给出, 合起来才是一条完整的时间线。
四、PMTUD 档不参与“至少要装多少”: 576 0 处 ⇎ 1280 0 处 ⇎ 65,535 0 处, 而 MTU 一词 219 处、PMTU 缩写 109 处、“packet too big”28 处——它把“最小的一环是多少”整项让给别的文书, 自己只答“怎么量到”。体例也反着: 2119 规定的四枚全大写词五份皆 0 处, 小写 must 28 处; 它引用 2119 达 7 次(另四份 0⇎0⇎0⇎0 次), 并在 2 处写明“只用小写、不引 2119 的定义”。
五、同一通道还压在分片主语上: “not by routers”在三份标准里逐字存在, 却一律被排到下一行——严档(单空格)五份全 0⇎0⇎0⇎0⇎0 处 ⇎ 宽松档 1⇎1⇎1⇎0⇎0 处 ⇎ 差 1⇎1⇎1⇎0⇎0 处。任何只用单空格短语的检索都会把 IPv6 与 IPv4 最关键的一条差别读成“文书里没写”。

### 本条不能由在库文件判定的(只登记, 不进门槛)

① 五份 .txt 的抓取时刻与磁盘 mtime 谁新谁旧; ② rfc-editor.org 此刻给 RFC 2675 挂的类目——库内抬头只印 “Category: Standards Track”(五份各 1 行)而 “Experimental” 字样 0⇎0⇎0⇎0⇎0 处, 官网若标 Experimental 属站外事实; ③ 勘误表(errata)是否已挂新版——库内提及 0⇎0⇎6⇎0⇎1 处只是文书自我引用; ④ 17 现行是否已在部署侧全面生效; ⑤ 现实链路的 MTU 分布——1500 是以太网的举例而非测量值, 库内 1500 作独立数 token 各 3⇎6⇎4⇎0⇎1 处。这些只能站外核验, 因此都不进判词与门槛。

### 编码与门的账

编码区 7641 字符(不含换行); 锚 16 处 ⇎ 去重 13 串 ⇎ 归属检查 65 次 ⇎ 错配 0; 一源 10 ⇎ 两至四源 3 ⇎ 五源 0; 标签 A⇎B⇎C⇎D⇎E 各 3⇎5⇎1⇎4⇎3 处。
DERIV 94 键 ⇎ 复算点 290 处 ⇎ 同数共键 38 组 ⇎ 0 折 235 项; 扁平键 316 个; 闭合账 标量 2 项(全 0)⇎ 清单 6 项; 锚候选池 4169 条按逐字再现份数分 5 档(1652⇎719⇎1620⇎121⇎57), 分档闭合 0。
门槛三遍: T1 字面逐锚回原文 ⇎ T2 DERIV 每条算式重跑 ⇎ T3 码位与字母账; 本注另加第四遍复测, 上表 10 行全部 assert, 不符即停机。
