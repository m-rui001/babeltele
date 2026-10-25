# B57 四份规范判同一个哈希：枚举值 ⇎ 连拼写都不提 ⇎ 关进遗留块还留豁免 ⇎ 与 MD5 并列禁死（共用 299 行 ⇎ 改判句 2 处）
src: corpus/raw/ietf/rfc5246.txt (222395 字节／非空行 3979／'[Page N]' 104 枚／'SHA-1' 13 次／'Rationale:' 0 条) ⇎ corpus/raw/ietf/rfc7525.txt (60283 字节／非空行 979／'[Page N]' 27 枚／'SHA-1' 0 次／'Rationale:' 19 条) ⇎ corpus/raw/ietf/rfc8446.txt (337736 字节／非空行 5848／'[Page N]' 160 枚／'SHA-1' 8 次／'Rationale:' 0 条) ⇎ corpus/raw/ietf/rfc9325.txt (96608 字节／非空行 1592／'[Page N]' 0 枚／'SHA-1' 2 次／'Rationale:' 21 条) (四份都来自 rfc-editor.org 的 .txt 序列化; 页眉自写日期 August 2008 ⇎ May 2015 ⇎ August 2018 ⇎ November 2022, 新建议无页眉故取其首部块的那一行; 抓取时刻与磁盘 mtime 只在本机成立, 不进门槛)
；联结不是“同一份数据的两种序列化”, 而是同一个签名哈希在四份文书里的四种身份: 1.2 协议把它写成枚举值与默认 MAC('SHA-1' 13 次 ⇎ 小写 9 次), 旧建议连 'SHA-1' 这个拼写都不写(非零拼写种数 0, 只留 'HMAC-SHA1' 1 处当 MAC 下限), 1.3 协议把它关进 Legacy 注释块(枚举行 32 处含 4 枚)并对证书⇎握手消息给两种 MUST NOT, 新建议写下不留从句的 'SHA-1 or MD5 MUST NOT'(判禁同行 1 处); 两版建议之间整行共用 299 ⇎ 句子共用 66, 而门限那句从 192 SHOULD NOT 改成 224 MUST NOT; 两份协议的套件名交集 0 枚(整套换了名)
tags: 排他口径闭合差 三档拼写可见度 判决行同现⇎豁免从句 门限同时改数值与强度 理由条数 Rationale 项目符两版换记号 套件名跨代零交集 桥闭合 引用⇎时间方向 在库取代关系 搬运率整行⇎句子两口径 共用句里改判句 0 命中 遗留集与必支持集交 0 页式两代 BOM 锚归属由正文现推
## [[原始语料|ORIGINAL]]
### ⟦T⟧ ⟸ corpus/raw/ietf/rfc5246.txt

Obsoletes: 3268, 4346, 4366 E. Rescorla Updates: 4492 RTFM, Inc.

RFC 5246 TLS August 2008 6.2.2.

SHA-1, etc.) are used for MAC computations. The Record Protocol can operate without a MA

This pseudorandom function (PRF) takes as input a secret, a seed, and an identifying label and

none(0), md5(1), sha1(2), sha224(3), sha256(4), sha384(5), sha512(6), (255) } Has

supports MD5 and SHA-1. Note: this extension is

signatures to be used with digest algorithms other than SHA-1, provided such use is co

### ⟦O⟧ ⟸ corpus/raw/ietf/rfc7525.txt

RFC 7525 TLS Recommendations May 2015 Copyright Notice Copyrig

Implementations MUST NOT negotiate SSL version 2. Rationale: Today, SSLv2 is considered insecure [RFC6176]. o Implementations MUST N

o Implementations MUST NOT negotiate RC4 cipher suites. Rationale: The RC4 strea

Rationale: Based on [RFC3766], at least 112 bits of security is needed.

TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 and TLS_ECDHE_ECDSA_WITH_AES

less than 192 bits SHOULD NOT be used. When using RSA, servers

MAC) algorithm stronger than HMAC-SHA1 [RFC5289] 2.

### ⟦F⟧ ⟸ corpus/raw/ietf/rfc8446.txt

Obsoletes: 5077, 5246, 6961 August 2018 Updates: 5705, 6066 Cate

Legacy algorithms */ rsa_pkcs1_sha1(0x0201), ecdsa_sha1(0x0203), /*

Legacy algorithms: Indicates algorithms which are being deprecated because they use algorit

TLS 1.3 servers MUST NOT offer a SHA-1 signed certificate unless no valid certificate cha

MUST NOT be used in any signatures of CertificateVerify messages. Rescorla Standards Track

All SHA-1 signature algorithms in this specification are defined solely for use in legacy

A TLS-compliant application MUST support digital signatures with rsa_pkcs1_sha256 (for ce

### ⟦N⟧ ⟸ corpus/raw/ietf/rfc9325.txt

Obsoletes: 7525 Independent Updates: 5288, 6066 T. Fossati Category: Best Current P

Implementations MUST NOT negotiate SSL version 2. Rationale: Today, SSLv2 is considered insecure [RFC6176]. * Implementations MUST N

Rationale: Based on [RFC3766], at least 112 bits of security is needed.

Curves of less than 224 bits MUST NOT be used. This recommendation is in line with the late

the SHA-256 hash algorithm is RECOMMENDED and SHA-1 or MD5 MUST NOT be used [RFC9155] (for m

## ⟪BabelTele⟫
🧭 四源字节 222395 ⇎ 60283 ⇎ 337736 ⇎ 96608: 1.2 协议 222395 ⇎ 旧建议 60283 ⇎ 1.3 协议 337736 ⇎ 新建议 96608。换行 5827 ⇎ 1515 ⇎ 8963 ⇎ 1994, 非空行 3979 ⇎ 979 ⇎ 5848 ⇎ 1592, 最长行 72 ⇎ 72 ⇎ 72 ⇎ 72(四份同为 72 列), 平均行长 54 ⇎ 60 ⇎ 56 ⇎ 59, 制表符 0 ⇎ 0 ⇎ 0 ⇎ 0(四份一个不用, 排版靠折行), 行尾空白 0⇎0⇎0⇎0。非 ASCII 0 ⇎ 0 ⇎ 0 ⇎ 14, 字节减字符 0 ⇎ 0 ⇎ 0 ⇎ 15, BOM 0 ⇎ 0 ⇎ 0 ⇎ 1: 只有新建议带 BOM 与非 ASCII(共 14 枚), 它的字符数比字节数少 15; 严格 UTF-8 解码 1 ⇎ 1 ⇎ 1 ⇎ 1 四份全过; 字符数=字节数在 3 份上成立; 四份 sha16 是 4 个不同的串(串本身只进解读注)。
📏 同一出版社的两种页式: '[Page N]' 页标 104 ⇎ 27 ⇎ 160 ⇎ 0 ⇎ 页眉行 103 ⇎ 26 ⇎ 159 ⇎ 0, 两者之差 1 ⇎ 1 ⇎ 1 ⇎ 0(前三份页标比页眉多 1, 即首页无顶栏), 页眉里作者姓列种数 1 ⇎ 1 ⇎ 1 ⇎ 0。新建议两头都是 0——它整份不重复页眉页标, 是改版后的序列化; 页眉样例: 1.2 协议的顶栏 ⟦T⟧⟨RFC 5246                          TLS                        August 2008⟩ ⇎ 新建议一份页眉也不写。四份的日期自写为 August 2008 ⇎ May 2015 ⇎ August 2018 ⇎ November 2022, 文档号 5246⇎7525⇎8446⇎9325 与日期同序 3／3 段, 相邻月差 81 ⇎ 39 ⇎ 51(三段相加校住 171, 与首尾跨度 171 一致), 单调段数 3／3。
📐 判词用什么强度的词写成, 是可数的: 排他口径 MUST NOT 19 ⇎ 8 ⇎ 74 ⇎ 14 ⇎ 纯 MUST 119 ⇎ 13 ⇎ 256 ⇎ 38 ⇎ SHOULD NOT 6 ⇎ 7 ⇎ 15 ⇎ 18 ⇎ 纯 SHOULD 21 ⇎ 16 ⇎ 61 ⇎ 31 ⇎ MAY 34 ⇎ 1 ⇎ 58 ⇎ 4 ⇎ RECOMMENDED 2 ⇎ 5 ⇎ 7 ⇎ 7 ⇎ NOT RECOMMENDED 0 ⇎ 0 ⇎ 3 ⇎ 1(排他闭合差 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0, 六档全 0)。体制差别: 两份协议共写 MUST 119＋256 枚而两份建议只 13＋38 枚, 但显式理由 'Rationale:' 是 0 ⇎ 19 ⇎ 0 ⇎ 21——两份协议一条不写(0 条), 两版建议合计 40 条(2 份文书在写), 理由是建议文体的本职。项目符号: 'o' 行 0 ⇎ 49 ⇎ 0 ⇎ 0 ⇎ '*' 行 0 ⇎ 0 ⇎ 0 ⇎ 62, 两种混用的文件 0 份, 只用一种的 2／4——同一份 BCP 的两版换了列表记号而各自不混用: 同一条禁令在旧建议写作 ⟦O⟧⟨o  Implementations MUST NOT negotiate RC4 cipher suites.⟩, 在新建议把 'o' 换成 '*' 而整句其余逐字不变; 'SSLv2 禁令'那一行在两版建议里各 1 处(0 ⇎ 1 ⇎ 0 ⇎ 1), 新建议一侧是 ⟦N⟧⟨*  Implementations MUST NOT negotiate SSL version 2.⟩。
🪢 本条主轴: 同一个哈希在四份文书里是四种东西。带连字符的 'SHA-1' 13 ⇎ 0 ⇎ 8 ⇎ 2 ⇎ 标识符里的小写 'sha1' 9 ⇎ 0 ⇎ 5 ⇎ 0 ⇎ 'HMAC-SHA1' 2 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 'SHA1' 刨掉 HMAC 后净 1 ⇎ 0 ⇎ 0 ⇎ 0; 三种拼写非零的种数 3 ⇎ 0 ⇎ 2 ⇎ 1——旧建议 0 种都不写, 它唯一一次提到 SHA-1 是给 MAC 定强度下限 ⟦O⟧⟨(MAC) algorithm stronger than HMAC-SHA1 [RFC5289]⟩, 不是签名判词。四档相加 25 ⇎ 1 ⇎ 13 ⇎ 2。判决句定位: 含 'SHA-1' 或 'MD5' 且含 'MUST NOT' 的同一行 0 ⇎ 0 ⇎ 1 ⇎ 1(合计 2 处), 一处是 1.3 协议 ⟦F⟧⟨TLS 1.3 servers MUST NOT offer a SHA-1 signed certificate unless⟩(带豁免从句: 除非产不出有效证书链), 另一处是新建议 ⟦N⟧⟨the SHA-256 hash algorithm is RECOMMENDED and SHA-1 or MD5 MUST NOT⟩(不留从句); 1.3 协议另有 ⟦F⟧⟨MUST NOT be used in any signatures of CertificateVerify messages.⟩——握手消息里的签名一律不用, 而 ⟦F⟧⟨All SHA-1 signature algorithms in this specification are defined⟩ 只准用于遗留证书; 同一份文件对“证书里的签名”和“握手消息里的签名”给了两种强度。小写 sha1 落在枚举行 0 ⇎ 0 ⇎ 5 ⇎ 0; 1.2 协议把它写成枚举值 ⟦T⟧⟨none(0), md5(1), sha1(2), sha224(3), sha256(4), sha384(5),⟩ 与 MAC 清单 ⟦T⟧⟨SHA-1, etc.) are used for MAC computations.  The Record Protocol⟩, 那时的默认是 ⟦T⟧⟨This pseudorandom function (PRF) takes as input a secret, a seed, and⟩ ⇎ ⟦T⟧⟨supports MD5 and SHA-1.⟩; 它甚至留了一句 ⟦T⟧⟨signatures to be used with digest algorithms other than SHA-1,⟩——四种身份里只有这一份给 SHA-1 开了“可以换掉”的口子。
🧱 门限同时改数值与强度: 旧建议 ⟦O⟧⟨less than 192 bits SHOULD NOT be used.⟩ ⇎ 新建议 ⟦N⟧⟨Curves of less than 224 bits MUST NOT be used.  This recommendation⟩——同族判据从 192 升到 224, 从 SHOULD NOT 升到 MUST NOT。字面计数 '192 bits' 0 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ '224 bits' 0 ⇎ 0 ⇎ 0 ⇎ 1 ⇎ 'less than 224 bits' 0 ⇎ 0 ⇎ 0 ⇎ 1, 两值在四份里各只 1⇎1 处; 其余门限 '112 bits' 1 ⇎ 3 ⇎ 1 ⇎ 3 ⇎ '128 bits' 1 ⇎ 1 ⇎ 0 ⇎ 2 ⇎ '2048-bit' 0 ⇎ 4 ⇎ 1 ⇎ 5 ⇎ '1024' 1 ⇎ 5 ⇎ 0 ⇎ 3 ⇎ 'forward secrecy' 0 ⇎ 7 ⇎ 7 ⇎ 15。判据后面的理由跟得多快也可数: 'MUST NOT' 行之后 6 行内出现 'Rationale:' 的行数 0 ⇎ 7 ⇎ 0 ⇎ 8(建议两份 7＋8 ⇎ 协议两份 0＋0); 112/2048 那一档的理由两版建议共用同一行 ⟦N⟧⟨Rationale: Based on [RFC3766], at least 112 bits of security is⟩, 而门限那一行不共用。
🗣 套件名的跨代存活是零: 完整套件名(同一行内一次到位)种数 31 ⇎ 9 ⇎ 6 ⇎ 10, 出现处 67 ⇎ 13 ⇎ 9 ⇎ 12, 而 1.2 协议与 1.3 协议的交集 0 枚——整套换了名(T 独有 29 ⇎ F 独有 6)。两份建议点名的套件里能在库内协议文本找到的: 新建议 2／10 枚在 1.2 协议 ⇎ 0 枚在 1.3 协议 ⇎ 8 枚两份都不在(三档相加校住 10, 差 0); 旧建议 2⇎0⇎7, 校住 9, 差 0。两份建议自己的交集 7 枚。那 8 枚的正式出处是库里没有的另外几份规范(AES-GCM 与 ECDHE 那一族, 本库只收这四份), 所以“建议点名的套件是否合法存在”不可由本条四份文件判定, 只进注; 旧建议点首选时写的一行是 ⟦O⟧⟨TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 and⟩——它在协议文本里逐字出现与否, 就是上面那两笔桥账。以裸 '_SHA' 结尾=SHA-1 套件的套件名 36 ⇎ 2 ⇎ 0 ⇎ 2 处, 1.2 协议里这样的名有 17 种; 72 列折行切出的悬空下划线碎片 0 ⇎ 1 ⇎ 0 ⇎ 1 枚(旧建议 1 ⇎ 新建议 1)。
🧵 引用方向与时间方向互不违反: 四份文件两两配成 12 个有序对, 非零 5 ⇎ 零 7, 且非零者全部指向比自己早的文件(违例 0 处)。RFC 号出现处 153 ⇎ 159 ⇎ 498 ⇎ 333, 不同号 22 ⇎ 36 ⇎ 50 ⇎ 66, 方括号引用 23 ⇎ 97 ⇎ 183 ⇎ 194。谱系行: Obsoletes 列 3 ⇎ 0 ⇎ 3 ⇎ 1 枚 ⇎ Updates 列 1 ⇎ 0 ⇎ 2 ⇎ 2 枚; 其中在库的 0 ⇎ 0 ⇎ 1 ⇎ 1(1.3 协议废 1.2 协议 ⟦F⟧⟨Obsoletes: 5077, 5246, 6961                                  August 2018⟩ ⇎ 新建议废旧建议 ⟦N⟧⟨Obsoletes: 7525                                              Independent⟩), 合计 2／2 对取代关系全可在库内验(不在库的 3 ⇎ 0 ⇎ 2 ⇎ 0); 1.2 协议自己废的三枚 ⟦T⟧⟨Obsoletes: 3268, 4346, 4366                                  E. Rescorla⟩ 在库里 0 命中。新建议的谱系行是 ⟦N⟧⟨Obsoletes: 7525                                              Independent⟩ ⇎ ⟦N⟧⟨Updates: 5288, 6066                                           T. Fossati⟩(Updates 列它自己不废的那批); 新建议引用它废掉的旧建议 9 处——废掉不等于不提; 反向为零: 1.3 协议提新建议 0 处 ⇎ 旧建议提新建议 0 处(时间不可能倒流)。
🗂 两版建议之间的搬运, 按三种口径数: 归一后长度 ≥20 的整行种数 876 ⇎ 1447, 按行集交得共用 299 行(旧版一侧独有 577 ⇎ 新版一侧独有 1148, 三档相加校住并集 2024, 差 0); 换成“只要在新文里逐字再现一次就算搬走”(允许成为别人更长行的一段)得 407 ⇎ 431, 相加 838, 比行集交多 539; 接行归一再断句得句 326 ⇎ 488, 共用 66 句(三档校住并集 748, 差 0)。两档相差 233: 句口径只认“接行后成文的声明”, 行口径还认目录行与参考文献行。把行口径那 299 条按体裁拆开——参考文献行 41 ⇎ 章节号行 1 ⇎ 正文行 257(三档校住 299, 差 0): 只有 257 行是“同一条声明原样搬过去”的那批。共用的 66 条句里带 'Rationale:' 字样的 0 条、含 '192 bits' 的 0 条 ⇎ 含 '224 bits' 的 0 条——后两组为 0 就是这条的结论: 门限那句没被搬走而是被换掉(⟦O⟧⟨less than 192 bits SHOULD NOT be used.⟩ ⇎ ⟦N⟧⟨Curves of less than 224 bits MUST NOT be used.  This recommendation⟩ 互不逐字相等), 而同一句 SSLv2 判词 ⟦O⟧⟨Rationale: Today, SSLv2 is considered insecure [RFC6176].⟩ 在两版里逐字相同; 'Rationale:' 字样为 0 则来自断句口径本身——冒号后的首字母大写, 标签被切进了上一句的尾部, 所以“理由是否成批搬走”只能按整行口径判, 那一档共用的是 299 行。
🧬 码位仍然定义着, 但不在强制清单里: 1.3 协议的 SignatureScheme 式枚举行 32 处(含码位括号的枚举行, 正文与附录各一份清单, 合计 28 枚), 其中名里含 sha1 的 4 枚(⟦F⟧⟨rsa_pkcs1_sha1(0x0201),⟩ ⇎ ecdsa_sha1(0x0203)), 全部落在 ⟦F⟧⟨/* Legacy algorithms */⟩ 注释块内(块内 4 枚); 明文“必须支持”的签名 2 枚(⟦F⟧⟨A TLS-compliant application MUST support digital signatures with⟩), 其中含 sha1 的 0 枚——遗留集与必支持集的交是 0。1.3 协议里 rsa_pkcs1_sha256 3 枚 ⇎ rsa_pss_rsae_sha256 4 枚; DSA 系一枚不中(0 枚, 只作 RESERVED 注释)。遗留身份的正式定义在 ⟦F⟧⟨Legacy algorithms:  Indicates algorithms which are being deprecated⟩——它写明“因已知弱算法而被废弃”, 且这些值“只指证书里的签名”, 握手消息里不定义。
🧪 这条的可核事实分三档, 第一档全部由四份在库字节现推(⟦T⟧⟨SHA-1, etc.) are used for MAC computations.  The Record Protocol⟩ ⇎ ⟦O⟧⟨RFC 7525                   TLS Recommendations                  May 2015⟩ ⇎ ⟦F⟧⟨/* Legacy algorithms */⟩ ⇎ ⟦N⟧⟨the SHA-256 hash algorithm is RECOMMENDED and SHA-1 or MD5 MUST NOT⟩) ⇒ B57V 可复算: 四源字节/换行/最长行/制表符/非 ASCII/BOM/sha 种数, 页标与页眉差 1 ⇎ 1 ⇎ 1 ⇎ 0, 关键词六档排他闭合差 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0, 项目符单用 2／4, SHA-1 三种拼写的非零种数 3 ⇎ 0 ⇎ 2 ⇎ 1 与四档相加 25 ⇎ 1 ⇎ 13 ⇎ 2, 判决行共现合计 2, 门限 192⇎224 各 1 处, 套件名零交集 0 与两条桥差 0 ⇎ 0, 引用 12 对违例 0, 在库取代关系 2／2, 搬运两口径三档闭合 0 ⇎ 0, 共用句里改判句 0＋0, 遗留集与必支持集交 0, 池四档闭合 0。第二档只在本机成立: 四份字节的磁盘 mtime 与页眉自写的 August 2008 ⇎ May 2015 ⇎ August 2018 ⇎ November 2022 谁新谁旧、抓到的是否该号当前版本——进注不进门槛。第三档不可由在库文件判定: 新建议点名的 8 枚套件出自库里没有的规范, IANA 注册表里这些码位当前的弃用标记, 以及“为什么 1.3 要给证书里的 SHA-1 留豁免”的具体部署理由(正文只给 unless 从句, 不给数据)。锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 33 处／27 条去重串, 归属由正文现推, 每条对四源逐一判成员共 108 次检查, 归一属一源 24 ⇎ 两或三源 3 ⇎ 四源 0, 错配 0 处。
∴ 骨架 ⇒ ① 四源字节 222395 ⇎ 60283 ⇎ 337736 ⇎ 96608, 最长行 72 ⇎ 72 ⇎ 72 ⇎ 72, 非 ASCII 0 ⇎ 0 ⇎ 0 ⇎ 14, 页标 104 ⇎ 27 ⇎ 160 ⇎ 0 ⇎ 页眉 103 ⇎ 26 ⇎ 159 ⇎ 0; ② 体制: MUST NOT 19 ⇎ 8 ⇎ 74 ⇎ 14 ⇎ MUST 119 ⇎ 13 ⇎ 256 ⇎ 38 ⇎ 'Rationale:' 0 ⇎ 19 ⇎ 0 ⇎ 21 ⇎ 项目符 'o'0 ⇎ 49 ⇎ 0 ⇎ 0／'*'0 ⇎ 0 ⇎ 0 ⇎ 62; ③ 主轴: 'SHA-1' 13 ⇎ 0 ⇎ 8 ⇎ 2 ⇎ 'sha1' 9 ⇎ 0 ⇎ 5 ⇎ 0 ⇎ 'HMAC-SHA1' 2 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 判禁同行 0 ⇎ 0 ⇎ 1 ⇎ 1; ④ 门限: 192 SHOULD NOT ⇎ 224 MUST NOT, 字面 0 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 1, 理由跟随 0 ⇎ 7 ⇎ 0 ⇎ 8; ⑤ 套件: 种数 31 ⇎ 9 ⇎ 6 ⇎ 10, T∩F=0, 新建议桥 2＋0＋8−10=0; ⑥ 引用: 12 对里非零 5, 时序违例 0, 在库取代 2; ⑦ 搬运: 整行 299／并集 2024 ⇎ 句子 66／并集 748, 改判句共用 0＋0; ⑧ 枚举: sha1 枚举行 0 ⇎ 0 ⇎ 5 ⇎ 0, 遗留块 4, 必支持∩sha1 0。判词: “TLS 还能不能用 SHA-1 签名”没有单一答案——问 1.2 协议, 它是枚举值与默认 MAC; 问旧建议, 它连名字都没出现, 只作为 MAC 下限被越过; 问 1.3 协议, 它在证书里是“MUST NOT 除非别无选择”、在握手消息里是绝对 MUST NOT; 问新建议, 它与 MD5 并列为不留从句的 MUST NOT。四种身份都能数出来: 拼写 13 ⇎ 0 ⇎ 8 ⇎ 2, 同行共现 0 ⇎ 0 ⇎ 1 ⇎ 1, 强度词 19 ⇎ 8 ⇎ 74 ⇎ 14／119 ⇎ 13 ⇎ 256 ⇎ 38, 理由 0 ⇎ 19 ⇎ 0 ⇎ 21, 门限一句改数值一句改强度。
ℒ 方法 ⇒ 遇到“同一个算法在多份规范性文本里被反复改判”的原料, 把“禁不禁”拆成三层可数码再判: 点名层(SHA-1 的三种拼写各自计数, 旧建议 0 种都不写)、共现层('SHA-1' 与 'MUST NOT' 是否同一行: 0 ⇎ 0 ⇎ 1 ⇎ 1)、从句层(禁令是否带豁免: 1.3 有 ⇎ 新建议无)。两版建议的关系同时按整行(299 行)与接行断句(66 句)两种口径数, 并把它们的差 233 登记成键——只报“搬运率”会把唯一要紧的改判句盖掉, 所以还要单独报“共用句里含 192⇎224 的枚数”(0＋0); 跨文档命名关系写成零交集(0)与两条桥的闭合差(0 ⇎ 0), 而不是断言“1.3 换了名”; 引用方向做成 12 个有序对的违例计数(0), 让“不会引用未来的文件”成为算出来的性质。
✂️ 为什么这份编码比摘要窗口长 ⇒ 四源各 222395 ⇎ 60283 ⇎ 337736 ⇎ 96593 字符, 窗口只能取锚点触到的行; 而本条的结论几乎全是跨文档量: T∩F=0 的套件名零交集、12 对引用方向、两版建议 299 行 ⇎ 66 句的两口径搬运、以及“改判那句在共用池里 0 命中”。尤其“同一份文件对证书与握手消息给两种强度”这一条, 任何单源窗口都只看得见它问的那半。读它请按“这个判词是哪一份文书、对哪一类签名位置、用哪个强度词说的”来读, 而不是按“少抄了多少原文”。

## ⛓解读注

- 四套实现与一处非独立: 采集侧 _pick57.py ⇎ 建条目侧 _mkB57.py(扁平契约 192 键, 与采集侧共有 115 个量, 本注重跑仍是不符 0 个) ⇎ 门槛内 _b57_scan()。本注是第四遍: 契约 192 键逐个与审计器快照对齐(不符即停机), 另自行从四份字节现取 123 个量(共 324 个数)并与契约逐一对账: 形状档走 splitlines 与字节 decode, 强度词八档走 lookaround 正则(建条目侧是逐次 find 扫描, 采集侧是 TXT.count), 拼写九档走 str.count, 页标走“逐行含 [Page ”, 页眉走 ^RFC \d{4}, 判决行走逐行布尔积, 套件名走 TLS_[A-Z0-9_]{8,} 量词正则 (建条目侧手工扩字符), 引用 12 对走号码 lookaround, 搬运的整行集先建字典再取键、断句改用 (?<=[.:;]) (?=[A-Z]) 的正则切, 遗留块按 “下一个 /*” 定界。换路子不是为了让数不同, 而是为了证明这些数不依赖某一种切法。
- _b57_scan 的量测段由 _wire57.py 从 _mkB57.py 的 SCAN 段逐行抽出(只改路径常量与模块别名), 插门前把 _b57flat.json 的 192 个键与 DERIV['B57'] 的 104 条算式(532 个复算点)在抽出体上跑过, 值不符即停机; 因此真正独立的两遍是 _pick57.py 与本注。采集侧与建条目侧在 115 个共有量上一开始有 20 处不符, 查到底分成两种性质: ①定义不同——页标(整篇字符扫描, 因为 “[Page N]” 缀在页眉行右端而不单独成行)、词边界是否把下划线算词字符 (小写 sha1 落在 ecdsa_sha1 里就不该计)、'optional' 的大小写两档、'Rationale:' 少写冒号、门限的两种拼法 (2048-bit ⇎ 2048 bits)、月份年的剥离口径、锚池的页眉窗口(40 字符)／触发词表(六枚)／下限(只有整行档要 ≥20 字符) ／归一后为空的行(纯 +---+ 分隔线在每个源都“命中”, 必须剔出池); ②同名不同形的假不符——池的 per-tag 列表与全局标量曾共用 pool_1 一个键名, 时间单调曾一处返 4 元一处返 3 元, 这两处不改判而是改名(pool_tag_1 ⇎ pool_1, date_seg_ok ⇎ 旧名), 因为把两种口径压进同一个键名只会让门槛假装它们相同。
- 门槛的账: DERIV 键 105 个 ⇎ 引用点 239 处 ⇎ 同数共键 30 组(两名以上 13 组) ⇎ 0 键折 109 项。同数的字面不取第一条算式, 而是复合式 LIT*(1-(max(全部算式)-min(全部算式))): 每条算式都等于该字面时括号才为 1。这一档在插门前抓到一条真错: “在写理由的文书份数”登记的字面由非零源数出来是对的, 而配给它的算式误写成 B57V('kw_rationale',0)+B57V('kw_rationale',2)——那是两份协议的理由条合计=0, 于是复合式对出 -2 并停机; 改成逐源 >0 求和后算式与字面才同指一物。字面一直没错, 错的是“哪条算式支持这个字面”, 复合式的作用就在这里。
  - 同数 1(38 条): 页标减页眉·1.2 协议 ⇎ 页标减页眉·旧建议 ⇎ 页标减页眉·1.3 协议 ⇎ 页眉署名串种数·1.2 协议 ⇎ 页眉署名串种数·旧建议 ⇎ 页眉署名串种数·1.3 协议 ⇎ 严格 UTF-8 解码·1.2 协议 ⇎ 严格 UTF-8 解码·旧建议 ⇎ 严格 UTF-8 解码·1.3 协议 ⇎ 严格 UTF-8 解码·新建议 ⇎ MAY·旧建议 ⇎ NOT RECOMMENDED·新建议 ⇎ SSLv2 禁令行·旧建议 ⇎ SSLv2 禁令行·新建议 ⇎ 'HMAC-SHA1'·旧建议 ⇎ 'SHA1' 净·1.2 协议 ⇎ 非零拼写种数·新建议 ⇎ 四档相加·旧建议 ⇎ 悬空下划线碎片·旧建议 ⇎ 悬空下划线碎片·新建议 ⇎ Obsoletes 列出的号·新建议 ⇎ Updates 列出的号·1.2 协议 ⇎ 废掉的号里在库的枚·1.3 协议 ⇎ 废掉的号里在库的枚·新建议 ⇎ SHA/MD5 与 MUST NOT 同行·1.3 协议 ⇎ SHA/MD5 与 MUST NOT 同行·新建议 ⇎ 'SHA-1' 与 MUST NOT 同行·1.3 协议 ⇎ 'SHA-1' 与 MUST NOT 同行·新建议 ⇎ '112 bits'·1.2 协议 ⇎ '112 bits'·1.3 协议 ⇎ '128 bits'·1.2 协议 ⇎ '128 bits'·旧建议 ⇎ '192 bits'·旧建议 ⇎ '224 bits'·新建议 ⇎ '2048-bit'·1.3 协议 ⇎ '1024'·1.2 协议 ⇎ 'less than 224 bits'·新建议 ⇎ 共用行里的章节号行
  - 同数 2(23 条): 只用一种项目符的份数 ⇎ 'Rationale:' 非零的份数 ⇎ 'SHA-1'·新建议 ⇎ 'HMAC-SHA1'·1.2 协议 ⇎ 非零拼写种数·1.3 协议 ⇎ 四档相加·新建议 ⇎ 'MD5'·新建议 ⇎ 'SHA-256'·旧建议 ⇎ 'SHA-256'·新建议 ⇎ 'GCM_SHA256'·1.3 协议 ⇎ '_SHA' 结尾套件·旧建议 ⇎ '_SHA' 结尾套件·新建议 ⇎ 新建议点名且在 1.2 协议 ⇎ 旧建议点名且在 1.2 协议 ⇎ Updates 列出的号·1.3 协议 ⇎ Updates 列出的号·新建议 ⇎ 废掉的号里不在库的枚·1.3 协议 ⇎ 在库取代关系合计 ⇎ '128 bits'·新建议 ⇎ rsa_pkcs1_sha1 枚 ⇎ ecdsa_sha1 枚 ⇎ 明文必支持的签名枚 ⇎ 两份判禁行合计
  - 同数 3(14 条): NOT RECOMMENDED·1.3 协议 ⇎ 非零拼写种数·1.2 协议 ⇎ 'MD5'·1.3 协议 ⇎ 'GCM_SHA256'·新建议 ⇎ Obsoletes 列出的号·1.2 协议 ⇎ Obsoletes 列出的号·1.3 协议 ⇎ 废掉的号里不在库的枚·1.2 协议 ⇎ 日期单调段数 ⇎ 文档号与日期同序段数 ⇎ '112 bits'·旧建议 ⇎ '112 bits'·新建议 ⇎ '1024'·新建议 ⇎ rsa_pkcs1_sha256 枚 ⇎ 归一属两或三源
  - 同数 7(8 条): RECOMMENDED 排他·1.3 协议 ⇎ RECOMMENDED 排他·新建议 ⇎ 两版建议套件名交集 ⇎ 旧建议点名而两份协议都没有 ⇎ 零引用对 ⇎ MUST NOT 后 6 行内有 Rationale·旧建议 ⇎ 'forward secrecy'·旧建议 ⇎ 'forward secrecy'·1.3 协议
  - 同数 4(7 条): MAY·新建议 ⇎ 小写 'md5'·1.2 协议 ⇎ 'SHA-256'·1.3 协议 ⇎ '2048-bit'·旧建议 ⇎ 枚举项名含 sha1 ⇎ 遗留块内枚举项 ⇎ rsa_pss_rsae_sha256 枚
- 主轴的来历(必须写, 因为它一度给出两个不可能的数): 搬运那档最早把“共用行数”按逐字子串再现来数(407 枚), 又把“独有”按整行归一集合去减, 闭合差算出 -108 这种不可能的负数——同一个键名里混了两种口径。 现在三口径各自登记并各自校住: 整行归一集合交 299(独有 577⇎1148, 并集 2024, 三档相加减并集=0), 再现口径旧行在新文再现 407 ⇎ 反向 431(合计 838), 句子口径共用 66(并集 748, 闭合 0), 两口径之差 233 单独立键。 共用那批整行的体裁是本注现数的: 参考文献行 41 ⇎ 章节号行 1 ⇎ 正文行 257(相加校住 299)——只有第三类才是“同一条声明原样搬过去”。另一处: “共用句里含门限那句”数出 0⇎0 两个 0 像是巧合, 其实是断句口径的产物, 它成立的真理由是这两行互不等价: less than 192 bits SHOULD NOT be used. ⇎ Curves of less than 224 bits MUST NOT be used.; 而同一批共用池里 'Rationale:' 也 0 命中(0), 说明搬走的是理由、改掉的是门限——这两句都能由字节复算, 而“改判”这个判断本身只在正文的对照里成立。
- 四档身份的账本(全由在库字节复算): 点名层 'SHA-1' 13 ⇎ 0 ⇎ 8 ⇎ 2 ⇎ 小写 9 ⇎ 0 ⇎ 5 ⇎ 0 ⇎ 净 SHA1(刨 HMAC-SHA1) 1 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ HMAC-SHA1 2 ⇎ 1 ⇎ 0 ⇎ 0, 非零拼写种数 3 ⇎ 0 ⇎ 2 ⇎ 1(旧建议 0 种都不写, 它唯一一次提到是给 MAC 定强度下限), 四档相加 25 ⇎ 1 ⇎ 13 ⇎ 2; 共现层 “MUST NOT 与 SHA-1⇎MD5 同一行” 0 ⇎ 0 ⇎ 1 ⇎ 1(合计 2 处); 从句层 1.3 那份带 unless 从句而新建议那份不带(不可数, 只进正文); 强度层 MUST NOT 19 ⇎ 8 ⇎ 74 ⇎ 14 ⇎ 纯 MUST 119 ⇎ 13 ⇎ 256 ⇎ 38 ⇎ SHOULD NOT 6 ⇎ 7 ⇎ 15 ⇎ 18 ⇎ 纯 SHOULD 21 ⇎ 16 ⇎ 61 ⇎ 31 ⇎ MAY 34 ⇎ 1 ⇎ 58 ⇎ 4 ⇎ NOT RECOMMENDED 0 ⇎ 0 ⇎ 3 ⇎ 1, 六档排他闭合差 0 ⇎ 0 ⇎ 0 ⇎ 0／0 ⇎ 0 ⇎ 0 ⇎ 0／0 ⇎ 0 ⇎ 0 ⇎ 0 全 0; 理由层 'Rationale:' 0 ⇎ 19 ⇎ 0 ⇎ 21(协议两份共 0 条 ⇎ 建议两份共 40 条 ⇎ 在写的文书 2 份)。身份层: 1.3 的枚举行 32 处共 28 枚, 名里含 sha1 的 4 枚全在 Legacy 块内(块内 4 枚), 而明文“必须支持”的 2 枚里含 sha1 的 0 枚——两集交 0。
- 套件名的跨代零交集与两条桥(本注用第三种切法复算): 1.2 与 1.3 的套件名集合交 0 枚(T 独有 29 ⇎ F 独有 6), 以裸 _SHA 结尾的在 1.2 有 17 种(出现 36 处)而在 1.3 为 0 枚; 两版建议点名的套件在库内协议文本里的落点三档闭合: 新建议 2＋0＋8−10=0 ⇎ 旧建议 2＋0＋7−9=0, 两版建议自己的交集 7 枚。 那 8⇎7 枚两份协议都不在的套件, 其正式出处是库里没有的规范(AES-GCM 与 ECDHE 那一族, 本库只收这四份): “它们是否合法存在”不可由在库文件判定, 能判的只有“这四份文件里点没点名”——所以这条只进注不进门槛。
- 引用与时间方向: 12 个有序对里非零 5 ⇎ 零 7 ⇎ 出现处 17, 本注按“被引者出版月晚于引用者”判违例得 0 处(契约 0); 方向全对不是假设: 非零的 5 对是 旧建议→1.2 协议 2 处 ／ 1.3 协议→1.2 协议 3 处 ／ 新建议→1.2 协议 2 处 ／ 新建议→旧建议 9 处 ／ 新建议→1.3 协议 1 处。谱系行 Obsoletes 列 3 ⇎ 0 ⇎ 3 ⇎ 1 ⇎ Updates 列 1 ⇎ 0 ⇎ 2 ⇎ 2, 其中在库可验的取代关系 2 对(1.3 废 1.2 ⇎ 新建议废旧建议), 库里没有对应文件的那批是 3 ⇎ 0 ⇎ 2 ⇎ 0 枚; 新建议提它自己废掉的旧建议 9 处——废掉不等于不提。门限那句的数值与强度同时迁移: 字面 '192 bits' 0 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ '224 bits' 0 ⇎ 0 ⇎ 0 ⇎ 1 ⇎ “less than 224 bits” 0 ⇎ 0 ⇎ 0 ⇎ 1, 而 'less than 192 bits' 只在旧建议出现; MUST NOT 行之后 6 行内出现 'Rationale:' 的行数 0 ⇎ 7 ⇎ 0 ⇎ 8——建议两份各 7＋8 枚, 协议两份 0＋0 枚。
- 四份字节的指纹与两代页式(旁证, 判词里只报“种数”而不报串, 因为串里的数字段无法由字节直接命中): 2ebe1b8e651696aeacc8ab3848bedb465505737901ea3b691acf40c392958feb ⇎ 728e0c3fd07d4307f02c22971c285f6f9c0a03334136ca5ed32f2a54d52ed7d2 ⇎ 47871bc8820a2c3b6ea89f061055577058862cf543686b82d10131239702b3bd ⇎ e3475381d056bde1eed65252954cce68250168454387f6799b38660806f215bc; sha16 种数 4 ⇎ 最长行四份同为 72 列 ⇎ 平均行长 54 ⇎ 60 ⇎ 56 ⇎ 59 ⇎ 制表符 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 行尾空白 0 ⇎ 0 ⇎ 0 ⇎ 0——四份一个制表符都不用, 排版全靠 72 列折行, 这就是折行残片(悬空下划线 0 ⇎ 1 ⇎ 0 ⇎ 1 枚)与“整行口径虚高”的来源。前三份是带页标的旧式序列化(页标 104 ⇎ 27 ⇎ 160 ⇎ 0 ⇎ 页眉 103 ⇎ 26 ⇎ 159 ⇎ 0, 差恒 1 ⇎ 1 ⇎ 1 ⇎ 0, 即首页无顶栏 ⇎ 页眉姓列种数 1 ⇎ 1 ⇎ 1 ⇎ 0), 新建议页眉页标各 0 而带 BOM(1)与非 ASCII(14 枚, 字节减字符 15): 严格 UTF-8 解码四份全过(1 ⇎ 1 ⇎ 1 ⇎ 1), 所以“字符数=字节数”只在 3 份上成立。项目符也换了记号: 'o' 行 0 ⇎ 49 ⇎ 0 ⇎ 0 ⇎ '*' 行 0 ⇎ 0 ⇎ 0 ⇎ 62, 同一份里两种混用 0 份, 只用一种的 2／4——同一条 SSLv2 禁令在旧建议以 'o' 开头、在新建议换成 '*' 而整句其余逐字不变(禁令行两份各 1 处)。
- 只在本机成立的一笔(不进门槛): 四份字节的磁盘 mtime 与它们自写的 “月份 年份” 相差 +6641.81 ⇎ +4177.81 ⇎ +2989.81 ⇎ +1436.81 天(自写日期 August 2008 ⇎ May 2015 ⇎ August 2018 ⇎ November 2022, 本注取每月 15 日为中点算差; 新建议无页眉, 其日期由前 6000 字符里最频繁的月份年推出, 这一档与建条目侧“取首个匹配”是两种取法而结果相同)。谁抓到的、抓于何时, 在库文件里没有依据; 同理不可判的还有: 这四份 .txt 是否各号的当前版本(rfc-editor 会在改版后重发序列化, 库里没有第二个版本可比), 以及 “1.3 为什么对证书里的 SHA-1 留 unless 从句” 的部署数据(正文只给从句不给数字)。
- 同一份字节是否还被别的条目当过源: 按门槛里的 SRC 表逐份查, 共用处 0 处。这四份 IETF 规范此前没有进过任何条目, 本条是第一次——所以本条没有“同料不同问”的历史包袱, 也没有需要与旧条目对齐的量; 而“72 列折行＋页眉页标这套旧式序列化 ⇎ 新式序列化”这一档是 B53(同一份 FIPS 202 的四种序列化)的量法在这批原料上的延伸, 但那里量的是载体而这里量的是判词, 两处不共用键。
- 锚的可核性: 33 处带标签锚 ⇎ 27 串去重, 按标签判成员得只属一源 24 ⇎ 属两或三源 3 ⇎ 四源全在 0(相加校住 27), 逐源判成员共 108 次检查(=去重串×4), 错配 0 处; 标签按源分 1.2 协议 8 枚 ⇎ 旧建议 7 枚 ⇎ 1.3 协议 9 枚 ⇎ 新建议 9 枚。归属不读旁注文件, 由正文里“源标签紧接原子引文”的配对现推。 不可由在库文件判定因而只写在本注的: IANA 注册表此刻对这些码位的弃用标记, 库里没有的规范里那批套件名的合法性, 以及“新建议为什么把 MAC 下限从 HMAC-SHA1 抬走”的取词过程(正文只给强度判据)。
