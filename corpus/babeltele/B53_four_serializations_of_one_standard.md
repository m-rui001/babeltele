# B53 同一份标准的四种序列化：行数、字形与词集都随抽取器改口，只有可复算的部分不变
src: corpus/raw\fips202.txt (72542 字节／非空行 1426) ⇎ corpus/raw\fips202_pdflayout.txt (77812 字节／非空行 1060) ⇎ corpus/raw\fips202_plain.txt (68458 字节／非空行 581) ⇎ corpus/raw\fips202.html (48779 字节／非空行 577) (本机两份由 pdftotext 现生, 重跑两遍字节相同; 官方两份为下载; 另有 raw/fips202.pdf 只作页数与流的旁证, 不作锚源)
；联结不是“四份材料”, 而是“同一份 FIPS 202 的四种序列化”: 官方纯文本留着 306 个非 ASCII 字形(共 25 种), 本机两种抽取把它们变成静默消失或 18 枚替换符, 而官方 html 其实是只抄了摘要的落地页(与正文的骨架行配对 6⇎843); “同一行”在原样／去空白／抹非 ASCII 三种口径下分别配出 452／556／692 行
tags: 骨架四口径配对 字形三层命运 码点存活表 词集包含随口径翻牌 落地页只抄摘要 标签与属性两种正文 断栏痕迹 页眉非每页 本机产物字节可复现 穿层命中矩阵 归一口径须披露 锚归属由正文现推
## [[原始语料|ORIGINAL]]
### ⟦T⟧ ⟸ corpus/raw/fips202.txt

http://dx.doi.org/10.6028/NIST.FIPS.202 August 2015 U.S.

FOREWORD The Federal Information Processing Standards (FIPS) Publication Series of the National Institute of Standards and Technology (NIST) is the official series of publications relating to standards and guidelines adopted and promulgated under the provisions of the Federal Information Security Management Act (FISMA) of 2002. Comments concerning FIPS publications are welcomed and should be addressed to the Director, Information Technology Laboratory, National Institute of Standards and Technology, 100 Bureau Drive, Stop 8900, Gaithersburg, MD 20899-8900. Charles H.

1. Name of Standard: SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions (FIPS PUB 202)

13 Table 3: Input block sizes for HMAC.........................

SHAKE128 The SHA-3 XOF that generally supports 128 bits of security strength, if 7 the output is sufficie

Lane (0, 0) = A[0, 0, 0] || A[0, 0, 1] || A[0, 0, 2] || … || A[0, 0, 62] || A[0, 0, 63] Lane (1, 0) = A[1, 0, 0

C[x, z] = A[x, 0, z] ⊕ A[x, 1, z] ⊕ A[x, 2, z] ⊕ A[x, 3, z] ⊕ A[x, 4, z]. 2.

D[x, z] = C[(x1) mod 5, z] ⊕ C[(x+1) mod 5, (z – 1) mod w]. 3.

a. for all z such that 0 ≤ z < w, let A′[x, y, z] = A[x, y, (z – (t + 1)(t + 2)/2) mod w]; b.

concatenating and/or truncating digests from hash functions—generally do exhibit this property. The possibility of close

In Step 1, the indices are defined for the hexadecimal digits. In Step 2a, each pair of hexadecimal digits is converted to t

Version 3, January 2011, http://keccak.noekeon.org/Keccak-submission-3.pdf. [3] The SHA-3 Cryptograp

### ⟦L⟧ ⟸ corpus/raw/fips202_pdflayout.txt

http://dx.doi.org/10.6028/NIST.FIPS.202 August 2015 U.S.

FOREWORD The Federal Information Processing Standards (FIPS) Publication Series of the National Institute of Standards and Technology (NIST) is the official series of publications relating to standards and guidelines adopted and promulgated under the provisions of the Federal Information Security Management Act (FISMA) of 2002. Comments concerning FIPS publications are welcomed and should be addressed to the Director, Information Technology Laboratory, National Institute of Standards and Technology, 100 Bureau Drive, Stop 8900, Gaithersburg, MD 20899-8900. Charles H.

1. Name of Standard: SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions (FIPS PUB 202)

13 Table 3: Input block sizes for HMAC.........................

SHAKE128 The SHA-3 XOF that generally supports 128 bits of security strength, if 6 the output is sufficie

A[0, 0, 1] = S [1] A[1, 0, 1] = S [65] A[4, 0, 2] = S [258] A[0, 0, 2] = S [2] A[1,

C[x, z] = A[x, 0, z] A[x, 1, z] A[x, 2, z] A[x, 3, z] A[x, 4, z]. 2.

D[x, z] = C[(x1) mod 5, z] C[(x+1) mod 5, (z � 1) mod w]. 3.

2. Return A. The dot in the right side of the assignment for Step 1 indicates integer multiplication, which in this case is equivalent to the intended Boolean "AND" operation. The effect of is to XOR each bit with a non-linear function of two other bits in its row, as illustrated in Figure 6 below. Figure 6: Illustration o

Function Output Security Strengths in Bits Size SHA-1 Collision Pre

concatenating and/or truncating digests from hash functions--generally do exhibit this property. The possibility of close

In Step 1, the indices are defined for the hexadecimal digits. In Step 2a, each pair of hexadecimal digits is converted to t

Version 3, January 2011, http://keccak.noekeon.org/Keccak-submission-3.pdf. [3] The SHA-3 Cryptograp

### ⟦P⟧ ⟸ corpus/raw/fips202_plain.txt

http://dx.doi.org/10.6028/NIST.FIPS.202 August 2015 U.S.

FOREWORD The Federal Information Processing Standards (FIPS) Publication Series of the National Institute of Standards and Technology (NIST) is the official series of publications relating to standards and guidelines adopted and promulgated under the provisions of the Federal Information Security Management Act (FISMA) of 2002. Comments concerning FIPS publications are welcomed and should be addressed to the Director, Information Technology Laboratory, National Institute of Standards and Technology, 100 Bureau Drive, Stop 8900, Gaithersburg, MD 20899-8900. Charles H.

1. Name of Standard: SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions (FIPS PUB 202)

The KECCAK-p permutations were designed to be suitable as the main components for a variety of cryptographic functions, including keyed functions for authentication and/or encryption. The six SHA-3 functions can be considered as modes of operation (modes) of the KECCAKp[1600,24] permutation. In the future, additional modes of this permutation or other KECCAK-p permutations may be specified and approved in FIPS publications or in NIST Special Publications. 4.

13 Table 3: Input block sizes for HMAC.........................

SHAKE128 The SHA-3 XOF that generally supports 128 bits of security strength, if 6 the output is sufficie

C[x, z] = A[x, 0, z] A[x, 1, z] A[x, 2, z] A[x, 3, z] A[x, 4, z]. 2.

D[x, z] = C[(x1) mod 5, z] C[(x+1) mod 5, (z � 1) mod w]. 3.

2. Return A. The dot in the right side of the assignment for Step 1 indicates integer multiplication, which in this case is equivalent to the intended Boolean "AND" operation. The effect of is to XOR each bit with a non-linear function of two other bits in its row, as illustrated in Figure 6 below. Figure 6: Illustration o

Function SHA-1 SHA-224 SHA-512/224 SHA-256 SHA-512/256 SHA-384 SHA-512 SHA3-224 SHA3-256 SHA3-384 SHA3-512 SHAKE128 SHAKE256 Output Size 160 224 224

concatenating and/or truncating digests from hash functions--generally do exhibit this property. The possibility of close

In Step 1, the indices are defined for the hexadecimal digits. In Step 2a, each pair of hexadecimal digits is converted to t

Version 3, January 2011, http://keccak.noekeon.org/Keccak-submission-3.pdf. [3] The SHA-3 Cryptograp

### ⟦H⟧ ⟸ corpus/raw/fips202.html

title>FIPS 202, SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions | CSRC</title> <meta http-equiv="conte

script> window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'G-TSQ0PLGJZP'); </script> <!-- Google Tag Manager

strong style="font-size: 1.6rem;">You are viewing this page in an unauthorized frame window.</strong> <p>This is a potential security issue, you are being redirected to <a href="https://csrc.nist.gov">https://csrc.nist.gov</a>.</p> </div> <section class="

An official website of the United States government </p> <p class="usa-banne

div class="hidden-sm hidden-xs hidden-xxs" id="pub-detail-abstract-info"><p>This Standard specifies the Secure Hash Algorithm-3 (SHA-3) family of functions on binary data. Each of the SHA-3 functions is based on an instance of the K<small>ECCAK</small> algorithm that NIST selected as the winner of the SHA-3 Cryptographic Hash Algorithm Competition. This Standard also specifies the K<small>ECCAK</small>-p family of mathematical permutations, including the permutation that underlies K<small>ECCAK</small>, in order to facilitate the development of additional permutation-based cryptographic functions. The SHA-3 family consists of four cryptographic hash functions, called SHA3-224, SHA3-256, SHA3-384, and SHA3-512, and two extendable-output functions (XOFs), called SHAKE128 and SHAKE256. Hash functions are components for many important information security applications, including 1) the generation and verification of digital signatures, 2) key derivation, and 3) pseudorandom bit generation. The hash functions specified in this Standard supplement the SHA-1 hash function and the SHA-2 family of hash functions that are specified in FIPS 180-4, the Secure Hash Standard. Extendable-output functions are different from hash functions, but it is possible to use them in similar ways, with the flexibility to be adapted directly to the requirements of individual applications, subject to additional security considerations.</p></div> <div class="hidden-lg h

## ⟪BabelTele⟫
🧭 体例 ⟦T⟧⟨1. Name of Standard: SHA-3 Standard: Permutation-Based Hash and Extendable-Output⟩ ‖ ⟦H⟧⟨<div class="hidden-sm hidden-xs hidden-xxs" id="pub-detail-abstract-info"><p>This Standard specifies the Secure Hash Algorithm-3 (SHA-3) family of functions on binary data. Each of the SHA-3 functions is based on an instance of the K<small>ECCAK</small> algorithm that NIST selected as the winner of the SHA-3 Cryptographic Hash Algorithm Competition. This Standard also specifies the K<small>ECCAK</small>-p family of mathematical permutations, including the permutation that underlies K<small>ECCAK</small>, in order to facilitate the development of additional permutation-based cryptographic functions. The SHA-3 family consists of four cryptographic hash functions, called SHA3-224, SHA3-256, SHA3-384, and SHA3-512, and two extendable-output functions (XOFs), called SHAKE128 and SHAKE256. Hash functions are components for many important information security applications, including 1) the generation and verification of digital signatures, 2) key derivation, and 3) pseudorandom bit generation. The hash functions specified in this Standard supplement the SHA-1 hash function and the SHA-2 family of hash functions that are specified in FIPS 180-4, the Secure Hash Standard. Extendable-output functions are different from hash functions, but it is possible to use them in similar ways, with the flexibility to be adapted directly to the requirements of individual applications, subject to additional security considerations.</p></div>⟩ ‖ ⟦H⟧⟨An official website of the United States government⟩ ⇒ 四份材料是同一份 FIPS 202 的四种序列化: 官方纯文本、本机 pdftotext 的两种抽取(留版式 ⇎ 不留版式)、官网那页 html。其中 2 份由本机现生、2 份由官网取来; 四份的 sha 4 种全不同, 字节 72542 ⇎ 77812 ⇎ 68458 ⇎ 48779, 行数 1925 ⇎ 1458 ⇎ 915 ⇎ 676, 非空行 1426 ⇎ 1060 ⇎ 581 ⇎ 577, 字符 70069 ⇎ 76354 ⇎ 67543 ⇎ 48089——所以“同一份标准”这句话在这里只能由内容重叠支撑, 不能由“同一个文件”支撑。
📏 同一页内容在四层里各是几种行 1925 ⇎ 1458 ⇎ 915 ⇎ 676 ‖ 非空 1426 ⇎ 1060 ⇎ 581 ⇎ 577 ‖ 中位行长 36 ⇎ 81 ⇎ 47 ⇎ 47 ‖ 最长行 167 ⇎ 168 ⇎ 1946 ⇎ 1465 ⇒ 无版式抽取把整段并成一条 1946 字的行(⟦P⟧⟨The KECCAK-p permutations were designed to be suitable as the main components for a variety of cryptographic functions, including keyed functions for authentication and/or encryption. The six SHA-3 functions can be considered as modes of operation (modes) of the KECCAKp[1600,24] permutation. In the future, additional modes of this permutation or other KECCAK-p permutations may be specified and approved in FIPS publications or in NIST Special Publications.⟩——这一行本身就长过官方 txt 的最长行 167 字), 分页符 0 ⇎ 37 ⇎ 37 ⇎ 0 与行尾空格 1780 ⇎ 10 ⇎ 3 ⇎ 25 恰好相反: 官方 txt 一个分页符都不留却留着 1780 行行尾空格, 本机两份各留 37 个分页符、只留 10⇎3 行行尾空格。行数、行长、分页、行尾空格都是抽取器的属性, 不是这份标准的属性。
🔤 关键字形只活在官方 txt 一层 ⟦T⟧⟨C[x, z] = A[x, 0, z] ⊕ A[x, 1, z] ⊕ A[x, 2, z] ⊕ A[x, 3, z] ⊕ A[x, 4, z].⟩(这一行在官方 txt 里有 4 枚 ⊕) ‖ ⟦T⟧⟨D[x, z] = C[(x1) mod 5, z] ⊕ C[(x+1) mod 5, (z – 1) mod w].⟩(同一行的减号、en-dash 与 ⊕) ‖ ⟦L⟧⟨D[x, z] = C[(x1) mod 5, z]  C[(x+1) mod 5, (z � 1) mod w].⟩(这两句在按版式抽取里) ‖ ⟦T⟧⟨a. for all z such that 0 ≤ z < w, let A′[x, y, z]  =  A[x, y, (z – (t + 1)(t + 2)/2) mod w];⟩ ‖ ⟦T⟧⟨Lane (0, 0) = A[0, 0, 0] || A[0, 0, 1] || A[0, 0, 2] || … || A[0, 0, 62] || A[0, 0, 63]⟩ ⇒ ⊕ 15 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ ≤ 39 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 替换符 U+FFFD 0 ⇎ 18 ⇎ 18 ⇎ 0 ⇎ 非 ASCII 总个数 306 ⇎ 18 ⇎ 18 ⇎ 11(种类 25 ⇎ 1 ⇎ 1 ⇎ 2)。三种命运同时存在: 官方 txt 原样留着; 本机两份里 ⊕ 与 ≤ 静默消失、只在原位留下空档(那一行在按版式层数得出 4 处双空格); 而减号一类既可能变成 U+FFFD 也可能直接不见(锚句里的 (x−1) 在按版式层成了 (x1)); ′ 只住在 ⟦T⟧⟨a. for all z such that 0 ≤ z < w, let A′[x, y, z]  =  A[x, y, (z – (t + 1)(t + 2)/2) mod w];⟩ 那一行, 在本机两层里同样一个不剩(′ 21 ⇎ 0 ⇎ 0 ⇎ 0, 省略号 … 29 ⇎ 0 ⇎ 0 ⇎ 0), ⟦T⟧⟨Lane (0, 0) = A[0, 0, 0] || A[0, 0, 1] || A[0, 0, 2] || … || A[0, 0, 62] || A[0, 0, 63]⟩ 那行的省略号点也一样。这 11 族(连同 U+FFFD)的码点合计 193 ⇎ 18 ⇎ 18 ⇎ 0: 本机两层的 18 枚全在替换符那一项, 上面 ⊕／≤／′／… 各行的本机两列本就都是 0; 破折号码点种类 5 ⇎ 1 ⇎ 1 ⇎ 1, ASCII 连字符 399 ⇎ 422 ⇎ 417 ⇎ 52。官方 txt 的 306 枚与按版式的 18 枚是同一口径下的两份文件, 相减只得 288, 而 288 不是“丢掉的字形个数”——本机两层的 18 枚非 ASCII 全是 U+FFFD。落地页那 11 枚与这份标准的字形无关: 是页面自身的不可断空格与曲引号。
🧱 “同一行”有四级判法 ⇒ 第一级是基数本身: 官方 txt 里骨架长度 ≥12 的行共 843 行; 拿这批行去按版式抽取里配——第二级原样逐字 452, 第三级去掉行首尾空白 556(多配 104 行), 第四级再抹掉所有非字母数字 692(再多配 136 行), 从原样到骨架共多配 240 行; 无版式层 98 ⇎ 107 ⇎ 135, 落地页 0 ⇎ 4 ⇎ 6, 到骨架这一级的步增依次是 136 ⇎ 28 ⇎ 2。多出来那些行是“话还是那句话, 字已经不是那些字”: 例如 ⟦T⟧⟨concatenating and/or truncating digests from hash functions—generally do exhibit this property.⟩ 在按版式层成了 ⟦L⟧⟨concatenating and/or truncating digests from hash functions--generally do exhibit this property.⟩——官方 txt 在这一处写作一个破折号, 本机两层各写作两个连字符, 逐字判不上而抹平后判得上。四级命中数逐级不减, 这条单调性由同一份 843 行基数当场校住。
🧲 词集的包含关系随分词口径翻牌 先分词 1268 ⇎ 1281 ⇎ 1285 ⇎ 442 ⇎ 先压掉全部空白再分词 1584 ⇎ 1588 ⇎ 1586 ⇎ 274 ⇒ 口径一: 官方 txt 独有 0 个、按版式抽取独有 13 个(前者是后者的子集); 口径二: 官方 txt 独有 114 个、按版式独有 118 个——同一个“独有”换了口径就从 0 跳到 114。落地页与官方 txt 的词集交只有 231(按版式层与它是 1268, 无版式层与它是 1268, 两抽取层之间 1280), 它的词汇总数 1249 ⇎ 11525 也说明它不是正文。
🖼 落地页的“正文”取决于算不算属性 ⟦H⟧⟨<title>FIPS 202, SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions | CSRC</title>⟩ ‖ ⟦H⟧⟨<script>   window.dataLayer = window.dataLayer || [];   function gtag(){dataLayer.push(arguments);}   gtag('js', new Date());   gtag('config', 'G-TSQ0PLGJZP'); </script>⟩ ‖ ⟦H⟧⟨<strong style="font-size: 1.6rem;">You are viewing this page in an unauthorized frame window.</strong>⟩ ⇒ 整份文件 494 枚标签／38 种／锚 92 枚／图 8 张／src 16 处／外链 36 处; 把标签连同属性一起去掉再数: uswds 9 ⇎ 0, DOI 4 ⇎ 1, SHA3 21 ⇎ 8。uswds 在文件里出现 9 次而正文里 0 次——它只住在 class 与 src 的值里; 页面另用 Date Published 字段写日期(1 处), 而正文三种序列化都写作 August 2015。八个关键词家族(algorithm／fips／keccak／nist／sha3／shake／sponge／step)在整份文件 173 次、去标签正文 44 次, 129 次随标签一起被删掉——单看 fips 字样是 31 ⇎ 9; ⟦H⟧⟨<p>This is a potential security issue, you are being redirected to <a href="https://csrc.nist.gov">https://csrc.nist.gov</a>.</p>⟩ 这类告警行只住在容器里。
📐 结构计数在同一份标准里给出四组数 Algorithm 24 ⇎ 24 ⇎ 24 ⇎ 1 ⇎ Step 10 ⇎ 10 ⇎ 11 ⇎ 0 ⇎ Figure 25 ⇎ 25 ⇎ 25 ⇎ 0 ⇎ Table 22 ⇎ 22 ⇎ 22 ⇎ 0 ⇎ Appendix 字样 0 ⇎ 0 ⇎ 0 ⇎ 1 ⇒ 算法号种类 11 ⇎ 11 ⇎ 11 ⇎ 1, 最大号 11 ⇎ 11 ⇎ 11 ⇎ 10: 三层抽取的算法号集合完全一致, 落地页只提到一个号。Step 引用在无版式层多出 1 处, 成因当场可查: 把模式放宽成“Step＋任意空白＋数字”后四层是 11 ⇎ 11 ⇎ 11 ⇎ 0, 官方 txt 里被折行切开(行尾停在 Step, 编号落在下一行)的正是 1 处, 无版式层把它们并回一行, 严格模式因此多数出一处。版面与合并的证据: ⟦L⟧⟨Function  Output             Security Strengths in Bits⟩(按版式独有的表头行) ‖ ⟦P⟧⟨SHA-1 SHA-224 SHA-512/224 SHA-256 SHA-512/256 SHA-384 SHA-512 SHA3-224 SHA3-256 SHA3-384 SHA3-512 SHAKE128 SHAKE256⟩(无版式独有的并行) ‖ ⟦P⟧⟨2. Return A. The dot in the right side of the assignment for Step 1 indicates integer multiplication, which in this case is equivalent to the intended Boolean "AND" operation. The effect of  is to XOR each bit with a non-linear function of two other bits in its row, as illustrated in Figure 6 below.⟩(并回来的那一处) ‖ ⟦T⟧⟨In Step 1, the indices are defined for the hexadecimal digits. In Step 2a, each pair of hexadecimal⟩ ‖ ⟦T⟧⟨Table 3:  Input block sizes for HMAC⟩。
🧵 版式留下的痕迹可以数 ⟦L⟧⟨A[0, 0, 1] = S [1]     A[1, 0, 1] = S [65]                       A[4, 0, 2] = S [258]⟩ ‖ ⟦L⟧⟨SHAKE128         The SHA-3 XOF that generally supports 128 bits of security strength, if⟩ ‖ ⟦P⟧⟨FOREWORD The Federal Information Processing Standards (FIPS) Publication Series of the National Institute of Standards and Technology (NIST) is the official series of publications relating to standards and guidelines adopted and promulgated under the provisions of the Federal Information Security Management Act (FISMA) of 2002. Comments concerning FIPS publications are welcomed and should be addressed to the Director, Information Technology Laboratory, National Institute of Standards and Technology, 100 Bureau Drive, Stop 8900, Gaithersburg, MD 20899-8900.⟩(抬头三行被并成一行) ‖ 断栏 1 ⇎ 120 ⇎ 0 ⇎ 7 ⇎ 超 72 字行 518 ⇎ 593 ⇎ 215 ⇎ 191 ⇎ 页首页眉 1 ⇎ 1 ⇎ 1 ⇎ 0 ⇒ 三空格以上断栏的行: 官方 txt 只有 1 行, 按版式抽取 120 行——那是双栏页被拉直后剩下的空档, 上一句的锚就是它造出来的; 而“FIPS PUB 202”在三种文本序列化里各只出现在行首 1 次、在落地页 0 次, 这份 PDF 有 44 页／198 个流——每页是否都印着页眉不可由在库文件判定, “数页眉校页数”这种想当然在这里不成立。
⏳ 时间与出处在四层的写法 August 2015 2 ⇎ 2 ⇎ 2 ⇎ 1 ⇎ DOI 串 1 ⇎ 1 ⇎ 1 ⇎ 1 ⇎ 网页字段 1 ⇒ DOI 在三种文本层各 1 次(⟦T⟧⟨http://dx.doi.org/10.6028/NIST.FIPS.202⟩), 参考文献的 URL 同样留到三层(⟦T⟧⟨Version 3, January 2011, http://keccak.noekeon.org/Keccak-submission-3.pdf.⟩), 但它在落地页正文 0 次、在整份文件里 4 次(住在 href 里)。折叠空白后的最长公共片段(四段依序为 按版式⇎官方、无版式⇎官方、落地页⇎官方、两抽取层之间): 段数 154 ⇎ 158 ⇎ 6 ⇎ 26 ⇎ 合计字符 53100 ⇎ 52317 ⇎ 2689 ⇎ 54913 ⇎ 最长 2660 ⇎ 2660 ⇎ 1135 ⇎ 4000 ⇎ 占该层比例 95 ⇎ 93 ⇎ 36 ⇎ 98, 落地页对官方 txt 只占 36, 而两份本机抽取之间占 98——它抄的是摘要那几句, 不是正文。
🗂 同名穿层: 20 枚关键串按两种口径判 18 ⇎ 2(归一后子串 ⇎ 归一函数会抹成空串的字形改判原样), 命中四层 13 枚 ⇎ 命中二三层次多层 3 枚 ⇎ 只命中单层 3 枚 ⇎ 一枚不中 1 枚。单层的三枚里两枚是 ⊕ 与 π——若不披露这层口径, 空串对谁都算命中, 单层就数不出 3 枚; 零层那枚是 uswds(矩阵按去标签正文判, 它在整份文件⇎正文 9 ⇎ 0 次); 四层的 13 枚在注里逐枚列出, 都是标题、DOI、算法名这类骨架词。口径披露两笔: 穿层矩阵对四层都用去标签正文, 而正文锚的命中判定对落地页改用原文件的行——去标签后并成一段的话在原文件里被标签切成几处, 两种口径都写在这里, 不留给读者猜。
🧪 这条的可核事实分三档 ⟦T⟧⟨C[x, z] = A[x, 0, z] ⊕ A[x, 1, z] ⊕ A[x, 2, z] ⊕ A[x, 3, z] ⊕ A[x, 4, z].⟩ ‖ ⟦H⟧⟨<strong style="font-size: 1.6rem;">You are viewing this page in an unauthorized frame window.</strong>⟩ ‖ ⟦T⟧⟨http://dx.doi.org/10.6028/NIST.FIPS.202⟩ ⇒ 第一档 B53V 可复算: 四份源的字节/行/行长/词集两级口径/码点存活表/骨架四级配对/结构计数与折行成因/穿层矩阵/关键词家族两种正文, 以及本机两份重跑两遍字节相同(命令两条; 入门槛的只有“两遍字节相同”这一句, 抽取器版本与产物 sha 只进注)。第二档只能对账不能对源: 官方两份与本机产物互不相同核得动, “它们与官网现在那份相同”核不动。第三档不可核, 也是本条与 B48 的分界: ⊕ 在 PDF 里本来是什么(字体码位还是图形对象)、哪一种序列化才算这份标准的正文——库里只有 44 页与 198 个流的字节统计, 没有渲染物, 所以这句话写进判词而不写成待核, 门槛里没有一项替它背书。锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 30 处／25 条去重串, 命中列分布是一源 14 ⇎ 多源 11 ⇎ 四源 0, 每条去重串对四份源逐一判成员共 100 次检查, 错配 0 处; 归属由正文现推, 不由旁注文件说了算。
∴ 骨架 ⇒ ① 四源 72542 ⇎ 77812 ⇎ 68458 ⇎ 48779 字节 ⇎ 非空行 1426 ⇎ 1060 ⇎ 581 ⇎ 577 ⇎ 行 1925 ⇎ 1458 ⇎ 915 ⇎ 676, 中位行长 36 ⇎ 81 ⇎ 47 ⇎ 47, 最长行 167 ⇎ 168 ⇎ 1946 ⇎ 1465; ② 官方 txt 的 843 个骨架行在按版式层原样 452 ⇎ 去空白 556 ⇎ 骨架 692(逐级多配 104⇎136), 在无版式层 135, 在落地页 6; ③ 字形只在官方 txt 活着: ⊕ 15 ⇎ ≤ 39 ⇎ 非 ASCII 种 25 ⇎ 1 ⇎ 1 ⇎ 2, 本机两份换成替换符 0 ⇎ 18 ⇎ 18 ⇎ 0; ④ 词集包含关系随口径翻牌: 官方 txt 独有由 0 变 114, 落地页与正文词交 231; ⑤ 落地页的正文随算不算属性而变: uswds 9 ⇎ 0 ⇎ DOI 4 ⇎ 1 ⇎ SHA3 21 ⇎ 8, 标签 494 枚, 八个关键词家族随标签丢掉 129 次; ⑥ 结构计数三层一致(11 ⇎ 11 ⇎ 11 ⇎ 1 种／最大号 11 ⇎ 11 ⇎ 11 ⇎ 10)而 Step 层多 1 处(放宽空白后 11 ⇎ 11 ⇎ 11 ⇎ 0, 被折行切开 1 处), 断栏行 120 ⇎ 页首页眉 1 ⇎ 1 ⇎ 1 ⇎ 0; ⑦ 本机两份重跑字节相同(2 份), 官方两份无此证据(2 份), 四份 sha 全不同(4); ⑧ 20 枚关键串穿层 13⇎3⇎3⇎1, 口径两式 18 ⇎ 2。判词: 一份文件“是什么”在四种序列化里没有单一答案——行数、行长、分页、词集包含、符号存活全部随抽取器改口; 能确定的只有可复算的那部分: 同一句话逐字对不上的行数、同一码点在四层各剩几个、以及本机产物重跑仍字节相同。
ℒ 方法 ⇒ 读“同一份文件的几种序列化”先定口径再读数: 每个数都写清三件事——在哪一层数、算不算标签与属性、逐字还是抹平后逐字。本条把“同一行”拆成四级(原样⇎去空白⇎抹非 ASCII⇎骨架长度门槛), 单调性当场可查。第二步给符号单独建码点表: 不数“有没有丢”, 而是逐码点数它在四层各剩几个, 于是同一行的三种命运(原样／替换符／静默空档)分得开。第三步把容器与内容分开: 落地页只抄摘要这件事用词集交 231、骨架配对 6(这 6 行的页眉／正文之分见注)、公共片段占比 36 三种独立量各说一遍, 不用一个比例糊过去。第四步给不可核留位置并写成因(PDF 的符号表示不在库内), 顺手记下四份文件的 sha 互不相同——“同一份标准”是内容层的主张, 不是文件层的事实。
✂️ 为什么这份编码比摘要窗口长 ⇒ 四份源各自 70069 ⇎ 76354 ⇎ 67543 ⇎ 48089 字符, 窗口只能取锚点触到的行; 而本条的结论全是跨层量: 骨架四级配对的 ladder、11 个码点在四层的存活表、落地页对正文的三种重合率(6／231／36)。尤其 843 行的四级配对与码点命运表, 任何单窗口都装不下它们的对照。读它请按“这个数是在哪一层、用哪种逐字口径数出来的”来读, 而不是按“少抄了多少原文”。

## ⛓解读注

**这四份数是怎么来的**: 官方纯文本 `corpus/raw/fips202.txt` ⇎ 本机按版式 `fips202_pdflayout.txt` ⇎ 本机无版式 `fips202_plain.txt` ⇎ 官方落地页 `fips202.html`, 字节 72542 ⇎ 77812 ⇎ 68458 ⇎ 48779, 行数 官方纯文本 1925 ⇎ 本机按版式 1458 ⇎ 本机无版式 915 ⇎ 官方落地页 676; 另有 `raw/fips202.pdf`(44 页／198 个流)只作页数与流的旁证, 不作锚源。同一个数由四套实现各算一遍再对齐: 采集侧 `corpus/_pick53.py`(先于条目写成, 落 `corpus/_b53meas.json`, 附候选锚池 1496 条), 建条目侧 `corpus/_mkB53.py`(落扁平契约 `corpus/_b53flat.json`, 110 枚键), 审计器侧 `corpus/audit.py::_b53_scan()`(快照落 `corpus/_b53audit.json`), 以及本注——它不读上面任何 JSON, 直接从四份 raw 现取现算 9 组量(200 个标量: 行与字数 24 ⇎ 版式痕迹 24 ⇎ 字形存亡 60 ⇎ 结构计数 32 ⇎ 词集两口径 24 ⇎ 落地页两种正文 17 ⇎ 骨架四口径 13 ⇎ 穿层矩阵 5 ⇎ 四份指纹 1)。
本注写这行时把三方又对齐了一次: 扁平契约 110 枚键(50 枚是逐源列表, 合计 260 个标量)在审计器快照里逐键等值, 无一失配; 审计器另算 8 枚只它自己有的键(`anchor_all4`、`anchor_cross`、`anchor_distinct`、`anchor_err`、`anchor_single`、`anchor_total`、`checks`、`regen_both`)——锚统计与“现跑两遍字节相同”那一项由正文现推, 建条目侧不预先写死。

**一处必须披露的重构**: 门槛里那份 `_b53_scan` 的量测段不是手写的第二套, 而是 `corpus/_mkB53.py` 现算段被逐行机械抽出后插进去的(`corpus/_wire53.py` 用两个切片边界取段、缩进四格、把 `os.path.join(ROOT, C, ...)` 改写为审计器的相对路径)。所以它的独立性不来自“另写一遍”, 而来自两道真独立的对账: ①采集侧与本注是两套各写一遍的实现, 建条目侧另与采集侧在 15 个量(每个四元, 共 60 个标量)上逐值 assert; ②插门前 `_wire53.py` 把扁平契约的 110 枚键与 DERIV 的 109 条算式在刚抽出的扫描器上原样重跑, 值不符就当场停机——因此门槛里的数与正文里的数不会是两套口径, 但也确实是同一套代码跑了两遍。这一点与 B48/B52 不同: 那两条的审计侧是手写的第二套实现。

**归一口径四套同写**: 建条目、采集、审计与本注各写一遍散文归一(小写、弯直引号剔除、连接号类折成 ASCII 连字符、数字／拉丁／汉字／`. -` 之外的字符折成空格、连续空白折一格)。本注把四份实现从三个源文件里按函数名抽出来现 exec, 加自己那一份共四份, 对 25 条锚逐一比对归一结果, 25 条全等、0 条分歧; 其中 7 条本身含弯引号、连接号类或非 ASCII 字形, 是这场比对的受力点。口径不同就会当场露: 穿层矩阵与锚归属都靠这一个函数, 四套不一致则同一串在一边命中、在另一边失配。

**两套“正文”口径与它的代价**: 量测(字形存活、结构计数、词集、公共片段)一律在去标签正文上判, 落地页去标签后是 20104 字符; 而锚的归属按原文件的行判成员——去标签后的那一段摘要在 html 原文件里根本不成行, 若按去标签正文收锚, 摘要段就会被切成任意宽度的“行”, 逐字口径失去意义。于是本条的披露是: 锚命中判定: T/L/P 用去标签正文, H 用原文件行, 对 T/L/P 三层两者本就是同一份文本。代价写在数上: 整份文件 494 枚标签／38 种, uswds 在整份 9 次而去标签正文 0 次, DOI 串 4⇎1, SHA3 一词族 21⇎8, fips 31⇎9, 八个关键词合计 173⇎44(去掉属性就少 129 处)。锚 30 处里 7 处标 H, 全部逐字命中原文件的行。

**锚的三口径**(正文“源标签紧接原子引文”的配对 30 处 ⇎ 按标签去重 25 条 ⇎ 候选清单 25 条, 每标签 T:14 L:5 P:4 H:7; 候选清单由 `corpus/atomcheck.py` 独立逐字校过, ok=25 bad=0):
① 连空格与字形都不改的逐字命中其标注那层 25/25; ② 只折叠空白后命中 25/25; ③ 再加归一后命中 25/25。三口径在这批上完全重合: 每条锚整行取自它标注的那一层, 逐字包含自然成立。留三口径不是为了这批, 而是因为命中列分布与穿层矩阵必须走③判跨层成员——本条正文里“官方 txt 的一个破折号 ⇎ 本机两层的两个连字符”那一类行, 逐字判不上而抹平后判得上, 数量记在骨架第三级比第二级多配的 136 行上。
命中列分布(按③对四份源逐一判成员, 共 100 次检查): 恰落一层 14 条 ⇎ 落两层或三层 11 条 ⇎ 四层全落 0 条 ⇎ 错配 0 条。“四层全落 = 0”由结构决定而不是巧合: 这里判的是整行, 而落地页抄来的那段摘要在原文件里是一整行(带标签的 1465 字符), 正文那 843 行没有一行在 html 里单独成行——能在四层之间配上的只到子串级(上面矩阵里那 13 枚关键串), 到不了整行级。那 11 条多层锚分两类: 8 条同时落在三层正文(`1. Name of Standard: SHA-3 Standar…` ⇎ `C[x, z] = A[x, 0, z] ⊕ A[x, 1, z] …` ⇎ `In Step 1, the indices are defined…` ⇎ `Table 3:  Input block sizes for HM…` ⇎ `http://dx.doi.org/10.6028/NIST.FIP…` ⇎ `Version 3, January 2011, http://ke…` ⇎ `SHAKE128         The SHA-3 XOF tha…` ⇎ `FOREWORD The Federal Information P…`); 3 条只落在本机两层, 它们是“两种抽取彼此一致而都与官方 txt 不同”的实证: `D[x, z] = C[(x1) mod 5, z]  C[(x+1…` ⇎ `concatenating and/or truncating di…` ⇎ `2. Return A. The dot in the right …`。分类由③从四份源现推, 不来自旁注文件。

**关键串的穿层矩阵**(与锚是两批东西: 20 枚手工挑定的关键串, 判法同样两套口径——归一后子串 18 枚 ⇎ 归一会把 ⊕／π 抹成空串、故这 2 枚改判原样字形): 命中四层 13 枚 ⇎ 恰落一层 3 枚 ⇎ 落二三层次多层 3 枚 ⇎ 一枚不中 1 枚。四层全中的 13 枚逐枚是: `10.6028/NIST.FIPS.202`、`Algorithm 1`、`August 2015`、`Extendable-Output Functions`、`Information Technology Laboratory`、`Keccak`、`Permutation-Based Hash`、`SHA-3 Standard`、`Step 1`、`rate`、`sha3-256`、`shake256`、`sponge function`。恰落一层的 3 枚: `CSRC MENU`(只在 官方落地页) ⇎ `π`(只在 官方纯文本) ⇎ `⊕`(只在 官方纯文本)。一枚不中的那枚是 `uswds`——它只住在 class 与 src 的属性值里, 正文四层都没有。矩阵的口径也记在数里: 若把改判那 2 枚一并按归一判, 它们会被判成“命中全部四层”, 因为归一后是空串, 而空串是任何串的子串; 这正是“口径必须披露”的现场版本。

**三档可核性落在哪**: 第一档在门槛里逐枚复算——本条 DERIV 共 109 枚键, 门槛打印出 110 处 B53V 复算点, 键集合与复算点值集合完全相等(109 枚一枚没漏), 其中值 `100` 由两处不同事实各自复算一遍, 而 '0' 那一枚把 31 个零量折成一条算式(全库已机检推导 971 枚)。骨架四级配对——按版式 452⇎556⇎692 ⇎ 无版式 98⇎107⇎135 ⇎ 落地页 0⇎4⇎6(三级依次是原样／去首尾空白／抹掉非字母数字, 基数 843 行, 落地页里其中 4 行是页眉行而非正文)、字形存活 306⇎18⇎18⇎11 枚非 ASCII(种类 25)、其中 18⇎18 枚是 U+FFFD、词集两口径的独有数翻牌(0⇎114 对 13⇎118)、落地页对正文的四种重合率(L⇎T 94.5% ⇎ P⇎T 93.1% ⇎ H⇎T 35.5% ⇎ L⇎P 97.7%)——全在这一档。第二档只能由集合运算得出: 官方 txt 的词集在按版式口径下是抽取层的真子集(反向独有 13 枚), 换口径后独有 114 枚; 843 行骨架里“逐字配不上而抹平配得上”的 136 行, 靠的是集合差而不是计数。第三档是本注现跑的两遍 `pdftotext`(抽取器 pdftotext version 4.00, 记账 `corpus/_probe53_run.txt`): 本机两层各由 PDF 现生两遍, 每遍 sha 与在库文件相同, 两份产物彼此不同——差别只来自 `-layout` 这一个开关。它与 B48/B52 的分界在此: B48 的产物可重建且入门槛, 本条的产物可重建但版本敏感, 所以门槛里只留“两遍字节相同”这一句(`regen_both`), 版本号与 sha 只进本注。
另有两句谓词在库内不可判, 正文按判词写、门槛不背书: “四种序列化里哪一种才算这份标准的正文”要一份渲染物或标准办公室的裁定, 库里只有 44 页 198 个流的字节统计; “`⊕` 在 PDF 里本来画的是什么”要图形层, 官方 txt 留着它而本机两层只在原位留下空档(那一行数得出 4 处双空格), 空档不是证据。

**digest 侧**: 摘要段四节(`### ⟦标签⟧ ⇐ 文件`, 4 节), 含换行 8091 字符(审计表“摘要段”一栏就是这个数), 去换行 7999; 编码区去换行 10533。于是“vs 摘要段”按表口径 130.2% ⇎ 按两侧都去换行 131.7%——两栏之差只是 92 枚换行的归属; 而编码区对四份源全文(262055 字符)是 4.02%。本条的形状尤其吃这一栏: 本机两层之间只差 8811 字符, 官方 txt 与这两层各差 6285 ⇎ 2526 字符, 而落地页那份只有 48089 字符、676 行——它是抄摘要的页面, 不是缩写的正文; 摘要窗口按 15⇎25 的宽度取锚点触到的行, 装不下骨架四级配对、码点存活表与四种重合率, 这三样都是跨层集合运算。最长行就是最直观的一处: 无版式层最长 1946 字符(整段并成一行), 官方 txt 最长 167——窗口若切在长行上, 一条锚就吃掉整段; 所以本条的窗口只作引文证据, 不作结论来源。

**同一个数的不同含义**(同值冲突 84 次登记、铺在 22 个值上, DERIV 一个值只留一枚键, 所以下面这些说法在门槛里会互相顶掉, 只能靠注里的上下文区分): 值 1 由 24 处不同事实共用(页首页眉·官方纯文本、页首页眉·本机按版式、页首页眉·本机无版式、非 ASCII 种·本机按版式、非 ASCII 种·本机无版式…)；值 11 由 12 处不同事实共用(Step 引用·本机无版式、算法号种·官方纯文本、算法号种·本机按版式、算法号种·本机无版式、最大算法号·官方纯文本…)；值 18 由 8 处不同事实共用(替换符·本机无版式、非 ASCII 个·本机按版式、非 ASCII 个·本机无版式、这些码点合计·本机按版式、这些码点合计·本机无版式…)；值 2 由 8 处不同事实共用(gap_th、August 2015·官方纯文本、August 2015·本机按版式、August 2015·本机无版式、hitraw…)。零同样拥挤: DERIV 的 '0' 键折了 31 个零项(官方 txt 的分页符 0 ⇎ 本机两层的 ⊕／≤／′／… 各 0 ⇎ 落地页的 Step／Figure／Table 引用 0 ⇎ 落地页逐字配上的骨架行 0 ⇎ uswds 在去标签正文 0 ⇎ 锚四源全中 0 ⇎ 锚错配 0 等), 这一串零合起来才是判词里“静默消失”那半句的机器形态。

**跑法**: `python -X utf8 corpus/_pick53.py && python -X utf8 corpus/_mkB53.py && python -X utf8 corpus/_mkdigest3.py B53 corpus/babeltele/B53_four_serializations_of_one_standard.md T corpus/raw/fips202.txt 15 25 L corpus/raw/fips202_pdflayout.txt 15 25 P corpus/raw/fips202_plain.txt 15 25 H corpus/raw/fips202.html 15 25` ⇒ 候选池 1496 条、锚 30 处／25 串、digest 30 条锚全部命中(union_hit=25); 再 `python -X utf8 corpus/_wire53.py` 重接门槛(幂等, 插门前逐键预演)。
`python -X utf8 corpus/audit.py` ⇒ B53 行 T1 编码失配 0 ⇎ T2 原文失配 0 ⇎ T3 码位 0 ⇎ 小整数待核 2; 门槛 PASS, 全库 53 条, 软提示 19 枚。本行的 2 枚是 `48 ⇎ 53`——两条都是条目自指(与 B48 的分界那句 ⇎ 审计侧环境名 `B53V`), 不是量, 所以门槛只列提示不判失配。
`python -X utf8 corpus/atomcheck.py B53 corpus/_atoms53.txt` ⇒ ok=25 bad=0(工具侧独立实现的逐字校验)。
`python -X utf8 corpus/_fill53.py` 即本注: 每次都重跑三方对齐、四套口径比对、第三档现跑与门槛, 所以这段里的数不是手填的, 也不能过期。