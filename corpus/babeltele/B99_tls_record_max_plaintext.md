# B99 一条 TLS 记录最多装多少明文: 8446⇎5246⇎8449⇎6066⇎OpenSSL 五份一手文书各答一遍 2^14⇎2^14(+1/+256/+1024/+2048)⇎档位四制⇎16384 十进制, 单位词与换行决定哪一档读得到
src: corpus/raw/tlsrec99/rfc8446.txt(337736 B 折平 282980 字符) ⇎ corpus/raw/tlsrec99/rfc5246.txt(222395 B) ⇎ corpus/raw/tlsrec99/rfc8449.txt(18932 B) ⇎ corpus/raw/tlsrec99/rfc6066.txt(55079 B) ⇎ corpus/raw/tlsrec99/openssl_max_send_fragment.pod(8693 B) (五份均为 TLS/实现侧一手文本: RFC 8446 TLS 1.3 ⇎ RFC 5246 TLS 1.2 ⇎ RFC 8449 record_size_limit ⇎ RFC 6066 max_fragment_length ⇎ OpenSSL split_send_fragment.pod; 数字一律从面内现读, 一个都不手填; "记录能装多大"在 1.2→1.3 之间换了口径(明文上限不动 ⇎ 内层加 1 ⇎ 密文膨胀从 1024/2048 改算成 256), 与 B57 的签名算法裁决不成同题对照; 上游改版后的现值只在本机或站外成立, 不进门槛)
; tags: 答案键(2^14 的五种序列化) 尺键(加数尺⇎膨胀尺⇎档位尺) 档键(四档读面阶梯+行尺三轨) 单位键(bytes/octets/裸数/带码位) 层键(规范面⇎实现面) 反向对照键(独占⇎共享) 锚归属由正文现推 闭合账 标量档 清单档
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/tlsrec99/rfc8446.txt

records carrying data in chunks of 2^14 bytes or less

The length MUST NOT exceed 2^14 bytes

The length MUST NOT exceed 2^14 + 256 bytes

the full encoded TLSInnerPlaintext MUST NOT exceed 2^14 + 1 octets

A TLSCiphertext record was received that had a length more than 2^14+256 bytes

or a record decrypted to a TLSPlaintext record with more than 2^14 bytes

MUST NOT produce an expansion greater than 255 octets

the maximum AEAD expansion of 255 octets

1 octet for ContentType

terminate the connection with a "record_overflow" alert

max_fragment_length(1)

The key words "MUST", "MUST NOT", "REQUIRED"

### ⟦B⟧ ⟸ corpus/raw/tlsrec99/rfc5246.txt

records carrying data in chunks of 2^14 bytes or less

The length MUST NOT exceed 2^14.

The length MUST NOT exceed 2^14 + 1024.

The length MUST NOT exceed 2^14 + 2048.

A TLSCiphertext record was received that had a length more than 2^14+2048 bytes

or a record decrypted to a TLSCompressed record with more than 2^14+1024 bytes

The key words "MUST", "MUST NOT", "REQUIRED"

### ⟦C⟧ ⟸ corpus/raw/tlsrec99/rfc8449.txt

TLS 1.3 uses a limit of 2^14+1 octets

that limit is 2^14 octets

permit senders to generate records 16384 octets in size

up to 2048 octets

the allowance for expansion to 256 octets

Allocating up to 18K of memory for ciphertext

The maximum value that the extension permits is 2^12

fragments of 2^14 octets

a value smaller than 64

The key words "MUST", "MUST NOT", "REQUIRED"

Padding added as part of encryption

### ⟦D⟧ ⟸ corpus/raw/tlsrec99/rfc6066.txt

2^9(1), 2^10(2), 2^11(3), 2^12(4)

2^9, 2^10, 2^11, and 2^12

fixed maximum plaintext fragment length of 2^14 bytes

Once a maximum fragment length other than 2^14 has been successfully

the negotiated length is 2^9=512

at most 805 bytes: 5 bytes of headers, 512 bytes of application data

larger than 805 bytes MUST discard the message

max_fragment_length(1)

The key words "MUST", "MUST NOT", "REQUIRED"

### ⟦E⟧ ⟸ corpus/raw/tlsrec99/openssl_max_send_fragment.pod

By default its value is SSL3_RT_MAX_PLAIN_LENGTH (16384)

only accept a value in the range 512 - SSL3_RT_MAX_PLAIN_LENGTH

SSL3_RT_MAX_PLAIN_LENGTH + SSL3_RT_MAX_ENCRYPTED_OVERHEAD (16704) bytes

Sets Maximum Fragment Length to 512 bytes

Sets Maximum Fragment Length to 1024.

Sets Maximum Fragment Length to 2048.

Sets Maximum Fragment Length to 4096.

must be in the range 1 - SSL_MAX_PIPELINES (32)

max_fragment_length(1)

## ⟪BabelTele⟫
🧭 一条 TLS 记录到底能装多少明文, 五份一手文书给出五副尺子, 且答句本身长短不一: RFC 8446(TLS 1.3)答句 20 词 132 字符跨 4 行 ⟦A⟧⟨The length MUST NOT exceed 2^14 bytes⟩, 同篇另有两句把上限抬成 +1 octets ⇎ +256 bytes ⟦A⟧⟨the full encoded TLSInnerPlaintext MUST NOT exceed 2^14 + 1 octets⟩ 与 ⟦A⟧⟨The length MUST NOT exceed 2^14 + 256 bytes⟩ ⇎ RFC 5246(TLS 1.2)答句只 6 词 33 字符跨 2 行 ⟦B⟧⟨The length MUST NOT exceed 2^14.⟩, 同族另两句一律不带单位词 ⟦B⟧⟨The length MUST NOT exceed 2^14 + 1024.⟩ ⟦B⟧⟨The length MUST NOT exceed 2^14 + 2048.⟩ ⇎ RFC 8449(record_size_limit)答句 8 词 39 字符 ⟦C⟧⟨TLS 1.3 uses a limit of 2^14+1 octets⟩, 同页另一句写旧上限 ⟦C⟧⟨that limit is 2^14 octets⟩ ⇎ RFC 6066(max_fragment_length)答句最长 18 词 131 字符跨 4 行, 它不答上限而答档位 ⟦D⟧⟨2^9(1), 2^10(2), 2^11(3), 2^12(4)⟩ ⇎ OpenSSL split_send_fragment.pod 7 词 58 字符跨 1 行, 唯一把上限写成十进制而不是幂式的一句 ⟦E⟧⟨By default its value is SSL3_RT_MAX_PLAIN_LENGTH (16384)⟩——五份全文里 2^14 式子的枚数 8⇎7⇎4⇎2⇎0, 答句里带幂式的枚数 1⇎1⇎1⇎1⇎0, 答句里带三位以上十进制的枚数 0⇎0⇎0⇎0⇎1(只有实现侧那份把 16384 写进答句)。
🪜 同一副上限在不同读面阶梯上数出来不一样: 逐行档 ⇎ 全篇折平档 ⇎ 摘壳折平档 ⇎ 摘壳+幂式归一档。把逐行档拼到折平档, 针多读得 6⇎3⇎4⇎4⇎1 枚(硬换行把 ⟦A⟧⟨the full encoded TLSInnerPlaintext MUST NOT exceed 2^14 + 1 octets⟩ 这类式子的加号推到下一行), 幂式归一(只改写带空格的加数式)后摘壳面缩短 8⇎4⇎0⇎0⇎0 字符, 恰为空格式枚数 4⇎2⇎0⇎0⇎0 的两倍(每处删掉加号两侧各一枚空格, 账平 0⇎0⇎0⇎0⇎0)——所以只有前两份有得缩; 五份的行宽上限 72⇎72⇎72⇎72⇎94 码位, 去重 2 种(RFC 一律 72, 实现侧放宽到 94); 壳行取六种形状的并(空行 ⇎ 整行换页符 ⇎ RFC 眉 ⇎ 页脚 ⇎ IETF 行 ⇎ =pod 标记): 逐形相加 3596⇎2160⇎170⇎531⇎72 次 ⇎ 同中两形的重叠 160⇎104⇎8⇎25⇎0 ⇎ 得壳行 3436⇎2056⇎162⇎506⇎72 ⇎ 正文行 5528⇎3772⇎290⇎898⇎129, 容斥账 0⇎0⇎0⇎0⇎0 ⇎ 壳+正对行尺的合账 0⇎0⇎0⇎0⇎0; 折平面 282980⇎188852⇎16816⇎48564⇎8623 字符 ⇎ 壳面 273302⇎181705⇎16236⇎46491⇎8277 字符。四档全读不到的冷针 4 枚(编号 3/4/5/6) ⇎ 判词针共 43 枚 × 五份 = 探针 215 次。
⚖ 单位词就是口径: 同一句 "The length MUST NOT exceed 2^14" 在 8446 带 bytes ⟦A⟧⟨The length MUST NOT exceed 2^14 bytes⟩, 在 5246 什么都不带 ⟦B⟧⟨The length MUST NOT exceed 2^14.⟩; 数字—单位对 35⇎49⇎14⇎11⇎4 枚。加数写法两种序列化: 带空格 "2^14 + k" 4⇎2⇎0⇎0⇎0 枚 ⇎ 紧写 "2^14+k" 0⇎2⇎1⇎0⇎0 枚, 5246 一份里两种并存(同一族常量的两种序列化: 结构体定义带空格, record_overflow 告警段不带空格 ⟦B⟧⟨A TLSCiphertext record was received that had a length more than 2^14+2048 bytes⟩); 裸幂(不带加数)4⇎3⇎3⇎2⇎0 枚。8449 把 256 拆成 1+255, 与它自己写的允许膨胀 256 对账差 0 ⟦C⟧⟨the allowance for expansion to 256 octets⟩; 三份规范面加数集合起来共 4 个档: 1⇎256⇎1024⇎2048; 把每档按两种拼写各算一遍——幂式 2^14+k 得 16384⇎16385⇎16640⇎17408⇎18432 ⇎ 十进制 16384+k 得 16384⇎16385⇎16640⇎17408⇎18432, 合账 0 只证明拼写没写歪, 不证明面上有数; 面上真读到的是: 摘壳折平面上十进制 16384 在 8449 ⇎ 实现侧两份共 2 枚 ⇎ 幂式 2^14 五份共 8⇎7⇎4⇎2⇎0 枚。
📐 档位题只 RFC 6066 与实现侧答: 6066 的指数 9⇎10⇎11⇎12 配码位 1⇎2⇎3⇎4, 指数减码位恒等于 8 (四档一把尺)⟦D⟧⟨the negotiated length is 2^9=512⟩ ⇎ 面上写全等号的只有 1 枚而写裸幂的 3 枚 ⟦D⟧⟨2^9, 2^10, 2^11, and 2^12⟩; 实现侧四档给十进制 512⇎1024⇎2048⇎4096, 其中 3 档不写单位 ⇎ 写单位的那档现读 1 枚, 词面在此 ⟦E⟧⟨Sets Maximum Fragment Length to 512 bytes⟩, 取值区间下界 512 上界 16384 差 15872, 管道数上界 32 ⟦E⟧⟨must be in the range 1 - SSL_MAX_PIPELINES (32)⟩, 读缓冲至少 16704(= 上限 + 加密膨胀 320) ⟦E⟧⟨SSL3_RT_MAX_PLAIN_LENGTH + SSL3_RT_MAX_ENCRYPTED_OVERHEAD (16704) bytes⟩。6066 的 805 字节展开式 4 项相加(5 headers ⇎ 512 application ⇎ 256 padding ⇎ 32 mac), 超出的膨胀 293 与实现侧的 320 差 27 ⟦D⟧⟨larger than 805 bytes MUST discard the message⟩。规范侧下限 512 ⇎ 8449 建议的最小值 64, 差 448 ⇎ 商 8 ⟦C⟧⟨a value smaller than 64⟩。
🧱 行尺本身也要对账: 把换页符当行界的 splitlines 档 9123⇎5931⇎459⇎1428⇎200 行 ⇎ split(换行) 档 8964⇎5828⇎452⇎1404⇎201 行 ⇎ 逐字符数换行 8963⇎5827⇎451⇎1403⇎200 行, 前两轨之差 159⇎103⇎7⇎24⇎-1 恰等于换页符 160⇎104⇎8⇎25⇎0 枚减去「文件以换行收尾」的那一枚 1⇎1⇎1⇎1⇎1(实现侧一份没有换页符, 所以差是负的), 逐格账平 0⇎0⇎0⇎0⇎0。同一份上另有两把壳尺打架: 采集遍的编号档 3436⇎2056⇎162⇎506⇎72 行 ⇎ 本遍形状档 3436⇎2056⇎162⇎506⇎72 行, 逐行分歧 0⇎0⇎0⇎0⇎0 行。六形各自的枚数: RFC 眉 159⇎103⇎7⇎24⇎0 行 ⇎ 页脚 160⇎104⇎8⇎25⇎0 行 ⇎ 整行换页符 160⇎104⇎8⇎25⇎0 行 ⇎ 实现侧的 =pod 标记 0⇎0⇎0⇎0⇎17 行 ⇎ 裸页码行 6⇎0⇎0⇎0⇎0 ⇎ =item 行 0⇎0⇎0⇎0⇎5。
🔁 反向对照: 只在一份面上读得到的独占判词针 12 枚 ⇎ 其中在本家读到的 12 枚 ⇎ 竟在别家也读到的 0 枚 (探针 60 次), 换行归一才救回的独占针 1 枚; 两份以上共享的针 3 枚, 共享格 8 格 ⟦A⟧⟨records carrying data in chunks of 2^14 bytes or less⟩ 一句在 8446⇎5246 两面同现 ⟦B⟧⟨records carrying data in chunks of 2^14 bytes or less⟩。告警名三种写法: 裸写 record_overflow 6⇎3⇎2⇎3⇎0 枚 ⇎ 带引号 3⇎0⇎2⇎1⇎0 ⟦A⟧⟨terminate the connection with a "record_overflow" alert⟩ ⇎ 而 illegal_parameter 告警 19⇎0⇎4⇎2⇎0——1.3 把超限与非法参数分两个告警, 1.2 只提前者。判词五档(折平/逐行/正则轨/游标轨)在同一份上的计数差合计 0⇎0⇎0⇎0⇎0, 小写档 must not/must/should not/should/may 合计 717⇎384⇎35⇎124⇎6 ⇎ 大写档 must not/must/should not/should/may 合计 553⇎227⇎29⇎77⇎0 ⇎ 逐行档 553⇎224⇎29⇎75⇎0, 两把词尺的差即被换行劈开的判词。
🧾 结构面与谱系: 定界进去的节 9 对(编号×篇名), 节内字符合 42301 ⇎ 节内行合 970 ⇎ 节内句合 205, 其中含幂式的句 13 句; 年份取自眉行末格(实现侧无眉行, 退回版权行的起止年) 共 6 枚 ⇎ 去重 5 种, 逐份种数 1⇎1⇎1⇎1⇎2: 2018 ⇎ 2008 ⇎ 2018 ⇎ 2011 ⇎ 2016 2026。锚定位 47 处, 其中跨行 17 处, 最长跨 2 行; 与采集遍 _pick99 的键对账 91 项 = 键名配对 85 条 + 复合对账 6 项(逐针四档表 ⇎ 三档逐针表 ⇎ 裁后 cut_lf ⇎ 游标 pins), 同 91 ⇎ 异 0 ⇎ 口径另立 5 对, 差异键 []。ℒ 方法 ⇒ 这副上限题的隐性知识分四键: ①答案键 20⇎6⇎8⇎18⇎7 是同一 2^14 的五种序列化(幂式 ⇎ 幂式+1 ⇎ 幂式+加数 ⇎ 十进制 ⇎ 只写档位不写上限); ②尺键 加数尺 4 个档 ⇎ 膨胀尺拆成 1+255 ⇎ 档位尺指数减码位恒 8, 三尺互不换算; ③档键 同一句在逐行/折平/摘壳/摘壳+归一四档上的可读性各不同(冷针 4 枚 ⇎ 折平涨 18 枚); ④层键 数值落在规范面(告警段 ⇎ 结构体定义 ⇎ NOTE)还是实现面(默认值 ⇎ 取值区间 ⇎ 读缓冲), 每键都是可机检的 count, 零项照占键位。


## ⛓解读注

### 压缩账(本注现算, 第三把尺: str.count 子串档 ⇎ 逐字符扫空白 ⇎ 手工按换行切行; 建条遍与采集遍的中间量一枚都不复用)

| 量 | 8446 | 5246 | 8449 | 6066 | pod |
|---|---|---|---|---|---|
| 源字符 | 337736⇎222395⇎18932⇎55079⇎8693 |
| 源词(逐字符扫空白) | 40349⇎27513⇎2638⇎7000⇎1098 |
| 源行(split 换行, 含收尾空行) | 8964⇎5828⇎452⇎1404⇎201 |
| 源面唯一码位 | 93⇎93⇎81⇎88⇎77 |
| 子串档 `2^14` 枚数 | 8⇎7⇎4⇎2⇎0 |
| 子串档 `16384` 枚数 | 0⇎0⇎1⇎0⇎1 |
| 子串档 `MUST NOT exceed` 枚数 | 3⇎3⇎0⇎0⇎0 |
| 子串档 `record_overflow` 枚数 | 6⇎3⇎2⇎3⇎0 |

编码区 4727 字符(不含换行) ⇎ 五份源面合 642835 字符 = 0.74% ⇎ 在档摘录 2373 字符(去换行)⇎2477 字符(含换行, 门表用后者): 编码⇎摘录两把尺 199.20%⇎190.84%, 差 104 枚换行符。

### 子串档不能替编码区的整词档(本注现读出的那一枚假命中)
整串 str.count 数 `2^14+1` 得 0⇎1⇎1⇎0⇎0, 其中 5246 的那一枚来自 `2^14+1024` 的前缀而不是面上真有 +1 档(5246 面上 `2^14+1 octets` 0 枚, 8449 面上有 1 枚)。所以编码区 🪜 的「折平比逐行多读 18 枚针」与 ⚖ 的加数档都由幂式解析得出, 不拿子串档充数; 反过来 `2^14`(整串 8⇎7⇎4⇎2⇎0 ⇎ 摘壳折平 8⇎7⇎4⇎2⇎0) 与 `record_overflow`(整串 6⇎3⇎2⇎3⇎0 ⇎ 编码区裸写档 6⇎3⇎2⇎3⇎0) 两档同值, 因为这两个串既不跨硬换行也不落在壳行里。`illegal_parameter` 则是两档打架的一例: 整串裸子串 22⇎3⇎4⇎3⇎0 ⇎ 编码区取的是带引号短语 "`illegal_parameter` alert" 的 19⇎0⇎4⇎2⇎0——5246 的三枚裸串都不成那个短语, 故编码区记 0。

### 锚核验(25 枚 ⟦标签⟧⟨原文⟩, 逐枚按标签回本家文件)
原面逐字符 verbatim 命中 14 枚, 其余 11 枚要把整面折平(空白折成一枚空格)才命中——即锚身跨一枚硬换行, 分属 A/B/C/D/E; 折平档 25/25 全命中。按折平档在五份面互查: 只在本家读到的 23 枚 ⇎ 两份同现的锚串 1 串(即 `records carrying data in chunks of 2^14 bytes or less` 在 ⟦A⟧ ⇎ ⟦B⟧ 各登记一次)。这把尺量的是本条 25 枚锚, 与编码区 🧱 的「独占 12 ⇎ 共享 3」量的不是同一集合(那边量 43 枚判词针), 两组数不可相加。

### 读法
编码区七段各管一副账: 🧭 五份答句的长短与序列化(20⇎6⇎8⇎18⇎7 词 ⇎ 132⇎33⇎39⇎131⇎58 字符)——只有 5246 的答句不带单位词, 只有实现侧把上限写成十进制而不是幂式; 🪜 四档读面阶梯(逐行 ⇎ 折平 ⇎ 摘壳 ⇎ 摘壳+幂式归一)与它的收益(折平比逐行多读 18 枚针 ⇎ 归一使摘壳面缩短 8⇎4⇎0⇎0⇎0 字符, 恰为空格式枚数 4⇎2⇎0⇎0⇎0 的两倍); ⚖ 单位词与加数序列化, 四档加数 1⇎256⇎1024⇎2048 展开成 16384⇎16385⇎16640⇎17408⇎18432, 幂式与十进制两条拼写的合账 0 只证明拼写没歪; 📐 档位题(6066 的指数 9⇎10⇎11⇎12 减码位 1⇎2⇎3⇎4 恒为 8 ⇎ 实现侧四档十进制 512⇎1024⇎2048⇎4096 只有 512 那档带单位) ⇎ 805=5+512+256+32 ⇎ 读缓冲 16704=16384+320; 🧱 三轨行尺对账(splitlines 比 split 多 159⇎103⇎7⇎24⇎-1 行, 恰等于换页符 160⇎104⇎8⇎25⇎0 枚减去「文件以换行收尾」的一枚) ⇎ 两把壳尺逐行分歧 0; 🔁 反向对照(独占针在本家 12/12 ⇎ 别家 0) ⇎ 判词五档差合计 0 ⇎ 大小写两把词尺之差即被换行劈开的判词; 🧾 结构面(9 节 ⇎ 节内 42301 字符 ⇎ 970 行 ⇎ 205 句, 含幂式 13 句) ⇎ 谱系(眉行年份 6 枚去重 5 种) ⇎ 与采集遍 _pick99 的 91 项对账(85 键名配对 + 6 复合项)同 91 异 0。核心结论一条: 明文上限 2^14 五份都不动, 动的是它外面那一层的算法——1.2 记压缩后 +1024 ⇎ 加密后 +2048, 1.3 改算成内层明文 +1 ⇎ 密文 +256(=1 枚 ContentType + 255 枚最大 AEAD 膨胀), 实现侧把这三件事摊成三个十进制数(默认值 16384 ⇎ 取值区间 512–16384 ⇎ 读缓冲至少 16704), 而 6066 根本不答上限只答档位。

### 本条不能由在库文件判定的(只登记, 不进门槛)
RFC errata 与改版后的现值(8446/5246 勘误表不在盘) ⇎ OpenSSL 之外实现的取值(内核 TLS ⇎ nginx ⇎ BoringSSL) ⇎ record_size_limit 与 max_fragment_length 在真实握手里的协商结果 ⇎ 抓包实测的记录长度。本条只认这五份在盘文本自身。

### 编码与门的账
T1 逐锚回源: 本注折平档 25/25 ⇎ 原面档 14/25(差 11 枚皆跨硬换行, 门按容行档判) ⇎ T2 DERIV 复算: 120 枚面值由 corpus/_b99contract.json 逐枚现算, 门内现量 242 键与建条遍逐键同值 ⇎ T3 码位账: 五份源面唯一码位 93⇎93⇎81⇎88⇎77 枚。本条小整数待核 0 项(门内 34 个提示里没有 B99)。
