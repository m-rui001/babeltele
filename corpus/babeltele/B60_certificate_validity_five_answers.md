# B60 同一张公签 TLS 证书最长能活多久，五份文书五种答法：825 天 ⇎ 398 与 397 天 ⇎ 只剩史料 ⇎ 90／6／45 天 ⇎ 只谈写法（上限句 5⇎5⇎4 条，7 处被排版折行）
src: CA-Browser-Forum-BR-1.7.7.layout.txt (248273 字节／面内 243533 字符／非空行 3517／上限句 5 条／天数集 5,30,90,397,398,825) ⇎ CA-Browser-Forum-BR-1.8.7.layout.txt (259837 字节／面内 255329 字符／非空行 3356／上限句 5 条／天数集 5,30,90,397,398,825) ⇎ CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt (363180 字节／面内 356795 字符／非空行 4715／上限句 4 条／天数集 5,7,10,30,90,397,398,825,2922,9132) ⇎ le_lifetimes.html (28488 字节／面内 4215 字符／非空行 86／上限句 0 条／天数集 6,45,47,90) ⇎ rfc5280.txt (352580 字节／面内 352580 字符／非空行 5991／上限句 0 条／天数集 空) (三份 CA/Browser Forum 基准要求的 pdftotext -layout 面, 各配一份 .pdf 原文件与一份 -raw 面; 第四份是 CA 的说明页 HTML, 壳与面并记; 第五份是 RFC 5280 纯文本。数字一律从面内现读, 一个都不手填; 抓取时刻与磁盘 mtime、官网是否已挂更新版、页面“last updated”之真伪只在本机或站外成立, 不进门槛)
；联结不是“同一份数据的两种序列化”, 而是同一张公签 TLS 证书的最长寿命在五份文书里的五种答法: 上限句宾语 旧 397,398,825 ⇎ 中 397,398,825 ⇎ 新 397,398 ⇎ CA 说明 无 ⇎ 规范 无, 825 作宾语 1⇎1⇎0⇎0⇎0 处而单空格逐字面只撞旧代 1 处; CA 说明另说 90 天默认 ⇎ 6 天可选 ⇎ 2028 年 2 月前降到 45 天, 并把 2029-03-15 起的 47 天归给“行业规则”——45 与 47 作天数在三份在库基准要求里 0⇎0 次; 规范不谈时长(带数天数 0 处)而谈写法: UTCTime 28 ⇎ GeneralizedTime 25 处, 两位年止于 2049(3 处); 术语四套: Validity Period 大写 7⇎7⇎7⇎0⇎0 处 ⇎ lifetime 全库 21 处 ⇎ notBefore 各 2⇎2⇎8⇎0⇎7 处; 全大写强度词 613⇎629⇎1052⇎0⇎451 处, 其中落在历史时间表行的 4⇎2⇎8⇎0⇎0 处; 整行共用 三代 484 行 ⇎ 基准与规范 2 行 ⇎ CA 说明 0 行; 网页那一份同一句在壳里 4,3,3,3 份 ⇎ 去壳面内 2,1,1,1 份, 壳内天数 17 ⇎ 面内 7。
tags: 上限句三元组谓词 单空格⇎容换行两档并记 整句窗口四档分类(上限⇎复用⇎条目名⇎其他) 天数三档相加闭合 壳⇎面两口径 术语四叫法 强度词词界⇎子串⇎表行两半闭合 只写时刻不写时长 整行容斥 同形不同物版本号 锚归属由正文现推 闭合账 标量 4⇎清单 7 项
## [[原始语料|ORIGINAL]]
### ⟦旧基准⟧ ⟸ corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt

193 825-day Certificate Lifetimes 17-Mar-2017 189 Amend Section 6.1.7

Subordinate CA: A Certification Authority whose Certificate is signed by the Root CA, or another Subordinate CA.

notBefore through notAfter, inclusive. WHOIS: Information retri

no more than 825 days prior to issuing the Certificate. Effective 2021-10-01, for validation of Domain Names and IP A

Subscriber Certificates issued after 1 March 2018, but prior to 1 September 2020, MUST NOT have a Validity Period greater than 825 days. Subscriber Certificates issued after 1 July 2016 but prior to 1 March 2018 MUST NOT have a Validity Period greater than 39 months.

### ⟦中基准⟧ ⟸ corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.layout.txt

Subordinate CA: A Certification Authority whose Certificate is signed by the Root CA, or another Subordinate CA.

Validity Period: From RFC 5280 (http://tools.ietf.org/html/rfc5280): "The period of time from notBefore through notAfter, inclusive." WHOIS: Information retr

Subscriber Certificates issued after 1 March 2018, but prior to 1 September 2020, MUST NOT have a Validity Period greater than 825 days. Subscriber Certificates issued after 1 July 2016 but prior to 1 March 2018 MUST NOT have a Validity Period greater than 39 months.

### ⟦新基准⟧ ⟸ corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt

1.7.1 SC31 398-day Re-use Period 2020 2-Jun-2021 Clarify Acceptable Statu

Short-lived Subscriber Certificate: For Certificates issued on or after 15 March 2024 and prior to 15 March 2026, a Subscriber Certificate with a Validity Period less than or equal to 10 days (864,000 seconds).

Subordinate CA: A Certification Authority whose Certificate is signed by the Root CA, or another Subordinate CA.

Validity Period: From RFC 5280 (http://tools.ietf.org/html/rfc5280): "The period of time from notBefore through notAfter, inclusive." WHOIS: Information retr

25 years) notAfter 2922 days (approx. 8 years) Note: This restriction

### ⟦CA 说明⟧ ⟸ corpus/raw/cert/le_lifetimes.html（渲染层: 注释删除, 分段/格标签各换成一个空格, 行内标签换成一个空格, 实体还原, 空白并列一个——本面按此档取到 4/17 枚锚）

Short-lived certificates with 6-day lifetimes are optionally available to all of our subscribers. See our certificate profiles documentation for more information. Future Plans Industry rules will limit certificate lifetimes to a maximum of 47 days starting on March 15, 2029. As such, we will be reducing the maximum lifetime of our certificates to 45 days by February 2028 . Why shorter lifetimes? W

We chose 90-day lifetimes for our initial offering because ninety days was short enough to strongly encourage automation, but long enough to make it possible to do things manually. While we wanted to encourage automation, that goal was subordinate to making it possible for everyone to enable HTTPS. At the time, automation wasn't as common as it is today, in part because the ecosystem of tools to enable it (e.g. ACME clients) was young. Today things are very different - automation is far more common and the ecosystem of tools to enable it is much more mature. As such, we are more comfortable with offerings shorter than ninety days now than we were then. Let's Encrypt is a free,

### ⟦X.509 规范⟧ ⟸ corpus/raw/cert/rfc5280.txt

notAfter). Both notBefore and notAfter may be encoded as UTCTime or GeneralizedTime. CAs conforming to this profile MUST always encode certificate validity dates through the year 2049 as UTCTime; certificate validity dates in 2050 or later MUST be encoded as GeneralizedTime.

The validity period for a certificate is the period of time from notBefore through notAfter, inclusive. In some situations, devices are given certificates for which no good expiration date can be assigned.

is zero. GeneralizedTime values MUST NOT include fractional seconds. 4.1.2.6.

## ⟪BabelTele⟫
🧭 五源字节 248273 ⇎ 259837 ⇎ 363180 ⇎ 28488 ⇎ 352580: 旧基准 ⇎ 中基准 ⇎ 新基准 ⇎ CA 说明 ⇎ X.509 规范; 面内字符 243533 ⇎ 255329 ⇎ 356795 ⇎ 4215 ⇎ 352580 ⇎ 原文件行 4741 ⇎ 4509 ⇎ 6386 ⇎ 617 ⇎ 8460 ⇎ 非空行 3517 ⇎ 3356 ⇎ 4715 ⇎ 86 ⇎ 5991 ⇎ 最长行 117 ⇎ 131 ⇎ 161 ⇎ 662 ⇎ 72 列。前三份各有孪生面: PDF 原字节 289455⇎287608⇎972214 ⇎ -layout 面比 -raw 面多 24585⇎25915⇎70568 字、多 1202⇎1179⇎1401 行, 而分页符 U+000C 两面各 99⇎87⇎128 枚, 差 0⇎0⇎0——换的是行的位置, 不是页的边界。第四份带壳: 标签 446 枚 ⇎ 实体 15 枚 ⇎ 脚本 5 枚 ⇎ 样式 0 枚 ⇎ href 63 条 ⇎ meta 12 枚, 剥壳丢 24187 字; 转义层只点名 5 枚, 页内未登记的实体 [] 枚, 登记而未用到的 [] 枚。形状量另用独立算法复算(逐字计数代 len, 数换行代 split), 两法之差合计 [0, 0, 0, 0, 0]。五份签名 5 种(blake2b 前 16 位)。
📐 上限只认一个句式: 动词 + have a Validity Period greater than + 数字 + days。三元组现抽: 旧基准 [('MUST NOT', '398'), ('MUST NOT', '825'), ('SHOULD NOT', '397')] ⇎ 中基准 [('MUST NOT', '398'), ('MUST NOT', '825'), ('SHOULD NOT', '397')] ⇎ 新基准 [('MUST NOT', '398'), ('SHOULD NOT', '397')] ⇎ CA 说明 [] ⇎ 规范 []; 命中句数 5 ⇎ 5 ⇎ 4 ⇎ 0 ⇎ 0 条, 去重 3 ⇎ 3 ⇎ 2 ⇎ 0 ⇎ 0 种, 宾语集 ['397', '398', '825'] ⇎ ['397', '398', '825'] ⇎ ['397', '398'] ⇎ [] ⇎ []。825 作该句宾语 1 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0 处——两代都在, 新代 0 处。同一条禁令在旧代与中代逐字同在(⟦T⟧⟨MUST NOT have a Validity Period greater than 825 days. Subscriber Certificates issued⟩ ⇎ ⟦O⟧⟨Period greater than 825 days. Subscriber Certificates issued after 1 July 2016 but prior to 1 March⟩), 而第一遍用单空格逐字面搜只在旧代撞到 1 处、中代 0 处: 中代把 Validity 与 Period 折在两行之间。容换行后各代补回 4 ⇎ 2 ⇎ 1 ⇎ 0 ⇎ 0 处, 全句级命中差同样多; 同一通道对天数写法成立: 逐字面 29 ⇎ 29 ⇎ 34 ⇎ 7 ⇎ 0 ⇎ 容换行 31 ⇎ 29 ⇎ 34 ⇎ 7 ⇎ 0, 差 2 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 处; 对词组写法亦然: 忽略大小写的逐字面 27 ⇎ 26 ⇎ 29 ⇎ 0 ⇎ 12 ⇎ 容换行 28 ⇎ 28 ⇎ 31 ⇎ 0 ⇎ 14, 差 1 ⇎ 2 ⇎ 2 ⇎ 0 ⇎ 2 处。
⚖ 825 这一处的三种身份, 按整句窗口(先把窗口内空白折平)分档: 上限句 ⟦T⟧⟨MUST NOT have a Validity Period greater than 825 days. Subscriber Certificates issued⟩ ⇎ 复用期 ⟦T⟧⟨no more than 825 days prior to issuing the Certificate. Effective 2021-10-01, for validation⟩ ⇎ §1.6 变更表条目名 ⟦T⟧⟨       193  825-day Certificate Lifetimes       17-Mar-2017⟩。各代窗口数: 上限档 3 ⇎ 3 ⇎ 2 ⇎ 0 ⇎ 0 ⇎ 复用档 1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 条目名档 1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 第四档 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0, 合计恰为 825 露面处数 5 ⇎ 5 ⇎ 4 ⇎ 0 ⇎ 0。398 同构: 2 ⇎ 2 ⇎ 2 ⇎ 0 ⇎ 0⇎1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0⇎1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0⇎0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0, 条目名 ⟦F⟧⟨1.7.1 SC31   398-day Re-use Period                                  2020        2-Jun-2021⟩; 397 只在上限档 2 ⇎ 2 ⇎ 2 ⇎ 0 ⇎ 0。四档划分在全库剩第四档 5 处(如“MUST be made within 90 days”1 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0), 分档闭合 0。同一个数在旧中两代是禁令、在新代只剩史料与复用期——判它属于哪一档只能读整句窗口, 读行号判不出来。
🔁 天数值域各一份: 旧基准 ['5', '30', '90', '397', '398', '825'] ⇎ 中基准 ['5', '30', '90', '397', '398', '825'] ⇎ 新基准 ['5', '7', '10', '30', '90', '397', '398', '825', '2922', '9132'] ⇎ CA 说明 ['6', '45', '47', '90'] ⇎ 规范 [], 各 6 ⇎ 6 ⇎ 10 ⇎ 4 ⇎ 0 个不同值。新代比前两代多出 ['7', '10', '2922', '9132']: ≤10 天的短证 ⟦F⟧⟨March 2026, a Subscriber Certificate with a Validity Period less than or equal to 10 days (864,000⟩ 与根 CA 的 2922/9132 天 ⟦F⟧⟨notAfter 2922 days (approx. 8 years)⟩; CA 说明独有 ['6', '45', '47'](6 天可选、45 天计划、47 天归给“行业规则”), 两家只共用 ['90']。45 与 47 作天数在三份在库基准要求里出现 0⇎0 次——CA 说明引的那个上限不在库里任何一份基准要求里。写法三档相加校住全数: 连字 2 ⇎ 2 ⇎ 2 ⇎ 5 ⇎ 0 + 空格 27 ⇎ 27 ⇎ 32 ⇎ 2 ⇎ 0 + 单数 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 = 逐字面 29 ⇎ 29 ⇎ 34 ⇎ 7 ⇎ 0(差 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0); 词族 44 ⇎ 41 ⇎ 49 ⇎ 9 ⇎ 1 个 day/days 去掉带数的 29 ⇎ 29 ⇎ 34 ⇎ 7 ⇎ 0 个, 余 15 ⇎ 12 ⇎ 15 ⇎ 2 ⇎ 1 处不定时长用法。
🧪 CA 说明把同一句话写三遍: ⟦N⟧⟨ We chose 90-day lifetimes for our initial offering because ninety days was short enough to strongly encourage automation, but long enough to make it possible to do things manually. While we wanted to encourage automation, that goal was subordinate to making it possible for everyone to enable HTTPS. At the time, automation wasn’t as common as it is today, in part because the ecosystem of tools to enable it (e.g. ACME clients) was young. Today things are very different - automation is far more common and the ecosystem of tools to enable it is much more mature. As such, we are more comfortable with offerings shorter than ninety days now than we were then. ⟩ ⇎ ⟦N⟧⟨ Short-lived certificates with 6-day lifetimes are optionally available to all of our subscribers. ⟩ ⇎ ⟦N⟧⟨ Industry rules will limit certificate lifetimes to a maximum of 47 days starting on March 15, 2029. As such, we will be reducing the maximum lifetime of our certificates to 45 days by February 2028 . ⟩ ⇎ ⟦N⟧⟨ Industry rules will limit certificate lifetimes to a maximum of 47 days starting on March 15, 2029. As such, we will be reducing the maximum lifetime of our certificates to 45 days by February 2028 . ⟩。逐句在壳里 [4, 3, 3, 3] 份 ⇎ 去壳面内 [2, 1, 1, 1] 份, 每句恰多 [2, 2, 2, 2] 份(差额种类 1 种)——多出的两份是 meta name=description 与 meta property=og:description, 剥壳时随整枚标签一起删。天数亦如此: 壳内 17 个 ⇎ 面内 7 个, 一枚 meta 描述里就有 5 个, 壳面差恰为 2×5(闭合 0)。于是“90 ⇎ 6 ⇎ 45 ⇎ 47”在正文里说一遍, 在分享卡片里说两遍; 去壳的量法读数少一半, 少的那一半正是搜索引擎与聊天软件拿到的那一半。
⛓ 同一个东西四套叫法: 大写 Validity Period 字面 7 ⇎ 7 ⇎ 7 ⇎ 0 ⇎ 0 处 ⇎ 小写 20 ⇎ 19 ⇎ 22 ⇎ 0 ⇎ 12 处 ⇎ 忽略大小写 27 ⇎ 26 ⇎ 29 ⇎ 0 ⇎ 12 处, 两档相加与忽略档差 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0; 词根 validity 全族 35 ⇎ 34 ⇎ 53 ⇎ 0 ⇎ 38 处, 去掉“validity period”两词组还剩 7 ⇎ 6 ⇎ 22 ⇎ 0 ⇎ 24 处(validityDate 与 OCSP 语境)。CA 说明通篇用 lifetime 而一次也不说 Validity Period: lifetime 忽略档 1 ⇎ 1 ⇎ 1 ⇎ 15 ⇎ 3 处 ⇎ 它 vp_ci 0 处; 规范用字段名 notBefore ⇎ notAfter: 2 ⇎ 2 ⇎ 8 ⇎ 0 ⇎ 7 ⇎ 1 ⇎ 1 ⇎ 6 ⇎ 0 ⇎ 11 处, 两者之差 -1 ⇎ -1 ⇎ -2 ⇎ 0 ⇎ 4——规范里 notAfter 多 4 处, 因为“到 notAfter 为止”这类界定只提尾端 ⟦R⟧⟨   (notAfter).  Both notBefore and notAfter may be encoded as UTCTime or⟩。
📏 强度词四档并记: 子串 MUST 256 ⇎ 282 ⇎ 642 ⇎ 0 ⇎ 304 ⇎ 词界 256 ⇎ 282 ⇎ 637 ⇎ 0 ⇎ 304(差 0 ⇎ 0 ⇎ 5 ⇎ 0 ⇎ 0: 新基准 5 处的 MUST 紧贴标点或被排版断开, 词界档不认), MUST NOT 子串 60 ⇎ 73 ⇎ 146 ⇎ 0 ⇎ 34 ⇎ 词界 60 ⇎ 73 ⇎ 146 ⇎ 0 ⇎ 34(差 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0), 忽略大小写 must 269 ⇎ 298 ⇎ 659 ⇎ 0 ⇎ 308 ⇎ 小写 must 13 ⇎ 16 ⇎ 22 ⇎ 0 ⇎ 4, SHALL 大写 206 ⇎ 200 ⇎ 207 ⇎ 0 ⇎ 10 ⇎ 忽略档 219 ⇎ 213 ⇎ 223 ⇎ 0 ⇎ 15, will 忽略档 18 ⇎ 20 ⇎ 37 ⇎ 2 ⇎ 52; 全大写四词族 613 ⇎ 629 ⇎ 1052 ⇎ 0 ⇎ 451 ⇎ 忽略大小写全族 706 ⇎ 726 ⇎ 1182 ⇎ 0 ⇎ 816。同一词族按“历史时间表行 ⇎ 其余正文”分两半(谓词与全量同法): MUST 表行 4 ⇎ 2 ⇎ 8 ⇎ 0 ⇎ 0 ⇎ 正文 252 ⇎ 280 ⇎ 629 ⇎ 0 ⇎ 304, 两半相加减全量 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0; SHALL 表行 6 ⇎ 11 ⇎ 7 ⇎ 0 ⇎ 0 ⇎ 正文 213 ⇎ 202 ⇎ 216 ⇎ 0 ⇎ 15, 差 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0; 表行只占 60 ⇎ 74 ⇎ 80 ⇎ 0 ⇎ 0 行 ⇎ 3925 ⇎ 5576 ⇎ 5855 ⇎ 0 ⇎ 0 字。CA 说明全大写强度词 0 处而 will 2 处: 它把义务写成“行业规则将要求”, 不写 MUST。
🗓 规范这一份不答“多久”, 只答“怎么写”: 带数的天数 0 处 ⇎ 上限句 0 条 ⇎ 大写 Validity Period 0 处。它说两套时间类型: UTCTime 28 处 ⇎ GeneralizedTime 25 处, 另四份各 [0, 0, 0, 0]⇎[0, 0, 0, 0] 处; 两种 ASN.1 记法枚数 YYMMDDHHMMSSZ 2 ⇎ YYYYMMDDHHMMSSZ 1; 分界见 ⟦R⟧⟨   validity dates through the year 2049 as UTCTime; certificate validity⟩ 与 ⟦R⟧⟨   is zero.  GeneralizedTime values MUST NOT include fractional seconds.⟩: 年 2049 3 处 ⇎ 2050 3 处——两位年只能表达到 2049, 越过它必须换 GeneralizedTime。库里日期写法三档: ISO 53 ⇎ 47 ⇎ 51 ⇎ 0 ⇎ 0 ⇎ 美式月日年 16 ⇎ 18 ⇎ 18 ⇎ 2 ⇎ 6 ⇎ “月 年” 17 ⇎ 21 ⇎ 24 ⇎ 1 ⇎ 173; CA 说明的正文用第三种, 一年只 1 处。
🧾 体例与自我标注: “Section 数字”引用 142 ⇎ 154 ⇎ 362 ⇎ 0 ⇎ 136 处 ⇎ 小写 section 0 ⇎ 2 ⇎ 1 ⇎ 0 ⇎ 0 处; 章节号行 672 ⇎ 679 ⇎ 674 ⇎ 0 ⇎ 2 行 ⇎ 去重 348 ⇎ 358 ⇎ 372 ⇎ 0 ⇎ 2 个。RFC 引用集 21 ⇎ 25 ⇎ 28 ⇎ 0 ⇎ 38 枚, 其中落在规范参考文献里的 2 ⇎ 3 ⇎ 4 ⇎ 0 ⇎ 38 枚, 未命中 19 ⇎ 22 ⇎ 24 ⇎ 0 ⇎ 0 枚; 号码 5280 本身各 18 ⇎ 22 ⇎ 44 ⇎ 0 ⇎ 151 处; 2119 各 2 ⇎ 2 ⇎ 2 ⇎ 0 ⇎ 1 处。自我标注: 首现版本号 旧 ['Version 1.7.7', 'Version 1.0', 'Version 1.1'] ⇎ 中 ['Version 1.8.7', 'Version 1.0', 'Version 1.1'] ⇎ 新 ['Version 2.0.2', 'Version 1.0', 'Version 1.1'] ⇎ 规范 ['Version 2.0']——规范里那枚 Version 2.0 是 ASN.1 模块版本而非文档版本(“version 数字”共 28 处), 同形不同物; “Baseline Requirements”15 ⇎ 18 ⇎ 27 ⇎ 0 ⇎ 0 处而规范 0 处; “last updated”只在 CA 说明 1 处; 谈 ASN.1 各 0 ⇎ 0 ⇎ 8 ⇎ 0 ⇎ 66 处。
⇄ 整行搬运(行长 ≥25 且归一化非空, 行集求交): 旧⇎中 601 行 ⇎ 中⇎新 1086 行 ⇎ 旧⇎新 543 行, 三代同现 484 行, 并集 7239 行, 只在本代 旧 2147 ⇎ 中 1517 ⇎ 新 2313 行; 容斥闭合 0。候选行集大小 2807 ⇎ 2720 ⇎ 3458 ⇎ 20 ⇎ 4619。基准要求与规范之间几乎不共用整行: 旧⇎规范 1 ⇎ 中⇎规范 2 ⇎ 新⇎规范 2 行, 去重 2 行——内容只是 ⟦T⟧⟨Subordinate CA: A Certification Authority whose Certificate is signed by the Root CA, or⟩ 这类定义表表头与 ⟦F⟧⟨notBefore through notAfter, inclusive."⟩ 这类范围说明, 不含任何期限数字。CA 说明与其余四份整行共用 0 行: 它是唯一一份网页, 行文折成整段, 换行位置与 PDF 面不可能对齐。
ℒ 方法 ⇒ 面对“同一问题五份文书五种答法”, 先问每个答案由哪个句式给出: 本条把上限做成三元组谓词(动词 × have a Validity Period × 数字), 于是“825 还在不在禁令里”有可判口径(1 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0 处), 而“825 这个词还在不在”是另一回事(5 ⇎ 5 ⇎ 4 ⇎ 0 ⇎ 0 处窗口, 分上限/复用/条目名四档)。其次把量测自身的失败做成键: 单空格档与容换行档的差(4 ⇎ 2 ⇎ 1 ⇎ 0 ⇎ 0⇎2 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0⇎1 ⇎ 2 ⇎ 2 ⇎ 0 ⇎ 2)逐档登记, 第一遍的漏判因此在库里可复算, 不靠注释解释; 带壳文档另立壳⇎面两口径, 用“每句恰多 1 份”把多出来源指认到两枚 meta, 再用天数把这两份坐实(17 减 7 等于 2×5); 谓词与全量同法(表行⇎正文两半相加闭合 [0, 0, 0, 0, 0]⇎[0, 0, 0, 0, 0]), 词界与子串两档并记而不择一, 因新基准里两档差 5 处。
✂️ 为什么这份编码比摘要窗口长 ⇒ 五源各 243533 ⇎ 255329 ⇎ 356795 ⇎ 4215 ⇎ 352580 字符, 窗口只能取锚点触到的行; 本条的结论几乎全是跨文书的量: 上限句集要三份基准并排(3⇎3⇎2 种), 壳面差要把同一页读两遍(壳 17 ⇎ 面 7), 分档要读整句窗口而非行(825 三档 3⇎1⇎1), 容斥要三份行集全量(7239 行)。尤其“中代那句 825 禁令逐字与旧代同、只是被排版折行”这一条, 任何单源单档量测都看不见——它要单空格档 0 处与容换行档 1 处同时成立才读得出来。读它请按“这个天数由哪份文书、以哪个句式、在整句还是条目名里给出”来读, 而不是按“少抄了多少原文”。

## ⛓解读注

### 第四遍复测(本注现算, 与前三遍不同路)

| 量 | 本注的写法 | 结果 | 与建条目侧 |
|---|---|---|---|
| 上限三元组 | 动词后六词“have a/Validity/Period/greater/than”加数字加 days 逐词连排, 词间空白整段记下 | T=MUST NOT·398/MUST NOT·825/SHOULD NOT·397 ⇎ O=MUST NOT·398/MUST NOT·825/SHOULD NOT·397 ⇎ F=MUST NOT·398/SHOULD NOT·397 ⇎ N 空 ⇎ R 空 | 逐字一致 |
| 上限句的两档命中 | 同一连排: 空白全为单格记严档, 含换行或多格记宽松档 | 宽松 5⇎5⇎4⇎0⇎0 ⇎ 单空格 1⇎3⇎3⇎0⇎0 ⇎ 差 4⇎2⇎1⇎0⇎0(其中含换行 4⇎2⇎1⇎0⇎0) | 与 ceil_n ⇎ ceil_strict_n ⇎ ceil_wrap 一致 |
| Validity 与 Period 的接缝 | validity/period 两词忽略大小写连排, 空白整段记下后分档 | 宽松 28⇎28⇎31⇎0⇎14 ⇎ 单空格 27⇎26⇎29⇎0⇎12 ⇎ 差 1⇎2⇎2⇎0⇎2(含换行 1⇎2⇎2⇎0⇎2) | 与 vp_flex_ci ⇎ vp_ci ⇎ vp_wrap 一致 |
| 同一句的壳内⇎面内 | 整份字面 count 在壳与面各数一遍再求差 | 4⇎3⇎3⇎3 ⇎ 2⇎1⇎1⇎1, 每句恰差 2 份 | 与 shell/face 一致 |
| 天数在壳⇎面 | 数字串+分隔符+day(s) 逐字符扫, 壳与面各扫一遍; meta 的 content 引数按标签边界手工取出 | 壳 17 ⇎ 面 7 ⇎ 两枚描述 meta 各 5 个, 差恰为 2×5 | 闭合 0 |
| 三代整行共用 | 行集归一改成逐字符滤 alnum(建条目侧用 re.sub) | T∩O 601 ⇎ O∩F 1086 ⇎ T∩F 543 ⇎ 三代同现 484 ⇎ 并集 7239 | 逐字一致 |
| BR 与 RFC 5280 | 同上 | T∩R 1 ⇎ F∩R 2 ⇎ N 与其余四份 0 | 逐字一致 |
| 天数值域 | 各份现切集合再求差 | 新基准独有 7,10,2922,9132 ⇎ CA 说明独有 6,45,47 ⇎ 两份共有 90 | 逐字一致 |
| 45 与 47 作天数 | 三份基准的天数值域里查这两个值在不在 | 两份皆 0⇎0 处 | 逐字一致 |
| 三个面 | 分页符逐个数、字符与行数用另一份面做差 | \f 99⇎87⇎128(两面同数, 差 0⇎0⇎0) ⇎ layout 比 raw 多字符 24585⇎25915⇎70568 ⇎ 多行 1202⇎1179⇎1401 ⇎ PDF 原字节 289455⇎287608⇎972214 | 逐字一致 |
| 强度词分两半 | 表行按逐字符查行首 10 位形如 YYYY-MM-DD 或文中有 SC+数字(建条目侧是一条正则); 词数按字符边界手工扫 | 表行 MUST 4⇎2⇎8⇎0⇎0 ⇎ 正文 MUST 252⇎280⇎629⇎0⇎304 ⇎ 表行行 60⇎74⇎80⇎0⇎0 行 | 与 h_must/b_must/hist_n 一致 |
| 锚归属 | 由条目正文 ⟦标签⟧⟨引文⟩ 配对现推, 成员判据用本注的面 | 17 处／去重 15 串／错配 0 | 与建条目侧、门槛侧同 |
| 两侧对账 | 采集侧 53 键在四份纯文本面上比 | 共有 53 ／ 不符 0 | 网页那份两边量在不同层, 不入表 |

### 读法

一、门槛的数只在 ⟦T⟧⟦O⟧ 的上限句里是禁令: 三元组 MUST NOT·398/MUST NOT·825/SHOULD NOT·397 在旧代与中代逐字同现, 到新代只剩 MUST NOT·398/SHOULD NOT·397——“825 还在不在禁令里”按三元组宾语判(旧 1 ⇎ 中 1 ⇎ 新 0 处), “825 这个词还在不在文书里”按整句窗口分档判(上限 3 ⇎ 复用 1 ⇎ §1.6 条目名 1 ⇎ 其他 0, 三代各自相加等于露面处数 5)。中代那句被排版折在两行之间, 所以单空格档只撞到 0 处、容换行档 1 处。
二、术语四套叫法是同一条禁令的四种载体: 大写 Validity Period 7⇎7⇎7⇎0⇎0 处 ⇎ 小写 [20, 19, 22, 0, 12] ⇎ 忽略大小写 [27, 26, 29, 0, 12] ⇎ 词根 validity 全族 [35, 34, 53, 0, 38](去掉两词组还剩 [7, 6, 22, 0, 24] 处是 validityDate 与 OCSP 语境) ⇎ lifetime [1, 1, 1, 15, 3] ⇎ notBefore/notAfter [2, 2, 8, 0, 7]⇎[1, 1, 6, 0, 11]。
三、强度词的分布要分两半读: 全大写 MUST 家族 613⇎629⇎1052⇎0⇎451 处, 其中落在 §1.6 历史时间表行里的只有 4⇎2⇎8⇎0⇎0 处, 正文那一半 252⇎280⇎629⇎0⇎304 处, 两半相加与全量对平(闭合 0⇎0⇎0⇎0⇎0⇎0⇎0⇎0⇎0⇎0⇎0⇎0⇎0⇎0⇎0)。
四、X.509 那一份不参与“多久”的争论: 带数的天数 0 处、上限句 0 条、大写 Validity Period 0 处, 全部为零; 它只管时刻怎么写——UTCTime 28 处 ⇎ GeneralizedTime 25 处, 世纪窗口写到 2049 年与 2050 年各 3⇎3 处。

### 本条不能由在库文件判定的(只登记, 不进门槛)

① 五份文件的抓取时刻与磁盘 mtime 谁新谁旧; ② cabforum.org 此刻挂的是哪一版基准要求; ③ LE 页 “Last updated” 那一行(库内 1 处)所指是否真的更新过; ④ 47 天所本的 “industry rules” 出自哪份文书——库内三份基准要求里 45 与 47 作天数各 0⇎0 处, 所以那句话在库里没有对照物; ⑤ 90 天默认是否已在全部 CA 生效。这些只能站外核验, 因此都不进判词与门槛。

### 编码与门的账

编码区 8400 字符(不含换行); 锚 17 处 ⇎ 去重 15 串 ⇎ 归属检查 75 次 ⇎ 错配 0; 一源 11 ⇎ 两至四源 4 ⇎ 五源 0; 标签 T⇎O⇎F⇎N⇎R 各 5⇎1⇎4⇎4⇎3 处。
DERIV 164 键 ⇎ 复算点 348 处 ⇎ 同数共键 45 组 ⇎ 0 折 143 项; 扁平键 231 个; 闭合账 标量 4 项(全 0)⇎ 清单 7 项; 锚候选池 15405 条按逐字再现份数分 5 档(7932⇎1409⇎5786⇎219⇎59), 分档闭合 0。
门槛三遍: T1 字面逐锚回原文 ⇎ T2 DERIV 每条算式重跑 ⇎ T3 码位与字母账; 本注另加第四遍复测, 上表 13 行全部 assert, 不符即停机。
