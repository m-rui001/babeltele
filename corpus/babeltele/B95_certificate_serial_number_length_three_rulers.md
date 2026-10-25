# B95 证书序列号到底能多长: 2459⇎3280⇎5280⇎CA/B TLS BR⇎LE 手册五份一手文书各答一遍 不给数⇎20 octets⇎<2¹⁵⁹+64 位熵⇎8 字节=63 位, 上限词两拼(Conformant⇎Conforming)⇎符号位那枚字节⇎三张提取面同数
src: corpus/raw/serialLen/rfc2459.txt(278438 B) ⇎ corpus/raw/serialLen/rfc3280.txt(295556 B) ⇎ corpus/raw/serialLen/rfc5280.txt(352580 B) ⇎ corpus/raw/serialLen/br_v202.layout.txt(366098 B) ⇎ corpus/raw/serialLen/le_asn1_der.html(83392 B) (五份均一手: RFC 2459 §4.1.2 ⇎ RFC 3280 §4.1.2.2 ⇎ RFC 5280 §4.1.2.2+§7.1+附录 B ⇎ CA/Browser Forum TLS BR v2.0.2 的 7.1.2.x 表行 ⇎ Let's Encrypt《A Warm Welcome to ASN.1 and DER》; 数字一律从面内现读, 一个都不手填; BR 另附同文书 raw ⇎ pypdf 两张提取面只作对照不进正文归属; 上游改版后的现值只在本机或站外成立, 不进门槛)
; tags: 答案键(不给数⇎20 octets⇎<2¹⁵⁹⇎DER 内容长 四把尺) 尺键(字节⇎比特⇎十六进制字符 三把) 档键(逐行⇎折平⇎摘壳⇎重叠 四档可读性) 层键(规范面⇎实现面⇎同一文书的三张提取面) 哨兵键(None=该面无此属性行) 反向对照键(独占针⇎上限词两拼⇎逗号分家) 锚归属由正文现推 闭合账 标量档 清单档
## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/serialLen/rfc2459.txt

The serial number is an integer assigned by the CA to each certificate

the issuer name and serial number identify a unique certificate

As a minimum, 16 octets

the construct "positiveint ::= INTEGER

### ⟦B⟧ ⟸ corpus/raw/serialLen/rfc3280.txt

The serial number MUST be a positive integer assigned by the CA

CAs MUST force the serialNumber to be a non-negative integer

Certificate users MUST be able to handle serialNumber values up to 20 octets

Conformant CAs MUST NOT use serialNumber values longer than 20 octets

that are negative, or zero

### ⟦C⟧ ⟸ corpus/raw/serialLen/rfc5280.txt

Conforming CAs MUST NOT use serialNumber values longer than 20 octets

the sign bit in the DER encoding of the INTEGER value MUST be zero

This can be done by adding a leading (leftmost) 

Certificate users SHOULD be prepared to gracefully handle such certificates

that are negative or zero

### ⟦D⟧ ⟸ corpus/raw/serialLen/br_v202.layout.txt

MUST be a non-sequential number greater than zero (0) and less than 2¹⁵⁹

containing at least 64 bits of output from a CSPRNG

### ⟦E⟧ ⟸ corpus/raw/serialLen/le_asn1_der.html

serial numbers encoded in DER as 8 bytes can be at most 63 bits long

Encoding a 64-bit positive serial number requires a 9-byte encoded value

RFC 5280 requires that serial numbers be positive

## ⟪BabelTele⟫
🧭 同一句“证书序列号到底能有多长、什么算违规”被五份一手文书各答一遍, 先把面尺摆开(字节 ⇎ 码位 ⇎ 三把行尺): 字节面 278438 ⇎ 295556 ⇎ 352580 ⇎ 366098 ⇎ 83392 ⇎ 码位面 278438 ⇎ 295556 ⇎ 352580 ⇎ 363639 ⇎ 83252——两把尺只在后两份分开, 差 0 ⇎ 0 ⇎ 0 ⇎ 2459 ⇎ 140, 而逐枚非 ASCII 字符按 UTF-8 多出的字节是 0 ⇎ 0 ⇎ 0 ⇎ 2459 ⇎ 140, 两路账相减 0; 非 ASCII 码位枚数 0 ⇎ 0 ⇎ 0 ⇎ 1234 ⇎ 112(去重后 BR 11 种 ⇎ 实现侧 50 种), 三面合一才有 2¹⁵⁹ 的上标; 行尺三轨同摆: splitlines 档 7356 ⇎ 7356 ⇎ 8610 ⇎ 6513 ⇎ 1705 ⇎ split(换行) 档 7228 ⇎ 7228 ⇎ 8460 ⇎ 6386 ⇎ 1706 ⇎ 逐字符数换行 7227 ⇎ 7227 ⇎ 8459 ⇎ 6385 ⇎ 1705, 前两轨之差 128 ⇎ 128 ⇎ 150 ⇎ 127 ⇎ -1 恰等于八种非换行界符合计减「面以界符收尾」的一枚(五面收尾界符标志全 1 ⇎ 1 ⇎ 1 ⇎ 1 ⇎ 1, 逐份相减合账 0); 换行 ⇎ 回车两把尺: 7227 ⇎ 7227 ⇎ 8459 ⇎ 6385 ⇎ 1705 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 6385 ⇎ 0——第四份 BR 是全份 CRLF 面(回车与换行同数), 另四面零回车; 最长行两把尺(split 档 ⇎ 逐字符扫档)逐份同值 134 ⇎ 72 ⇎ 72 ⇎ 161 ⇎ 1955, 实现侧那份 HTML 的行最长 1955 码位; 空行 2300 ⇎ 2110 ⇎ 2469 ⇎ 1671 ⇎ 298 ⇎ 非空行 4928 ⇎ 5118 ⇎ 5991 ⇎ 4715 ⇎ 1408 ⇎ 壳行 2557 ⇎ 2367 ⇎ 2770 ⇎ 1797 ⇎ 0 ⇎ 剥壳正文行 4671 ⇎ 4861 ⇎ 5690 ⇎ 4589 ⇎ 1706: 前两者相加回总行(合账 0), 后两者相加同样回总行, 而壳账容斥(六形之和减重数)逐份归零合计 0。

📏 答值分四代四把尺且互不译: 2459 一枚长度都不给——“20 octets” 最宽档 0 ⇎ 8 ⇎ 8 ⇎ 0 ⇎ 0 枚 ⇎ “positive” 整词档 0 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 4 枚, 它只写 ⟦A⟧⟨The serial number is an integer assigned by the CA to each certificate⟩ 与 ⟦A⟧⟨the issuer name and serial number identify a unique certificate⟩, 外加一句 ⟦A⟧⟨As a minimum, 16 octets⟩(那是 cRLNumber 的下限不是序列号); 3280 起给字节尺 8 枚 ⇎ 义务句 ⟦B⟧⟨The serial number MUST be a positive integer assigned by the CA⟩ ⇎ ⟦B⟧⟨CAs MUST force the serialNumber to be a non-negative integer⟩ ⇎ ⟦B⟧⟨Certificate users MUST be able to handle serialNumber values up to 20 octets⟩; 5280 同文而把上限词的旧拼写换掉(⟦B⟧⟨Conformant CAs MUST NOT use serialNumber values longer than 20 octets⟩ 只在 3280 6 枚 ⇎ 5280 0 枚), 它另在 ⟦C⟧⟨Conforming CAs MUST NOT use serialNumber values longer than 20 octets⟩ 之外补上符号位规矩 ⟦C⟧⟨the sign bit in the DER encoding of the INTEGER value MUST be zero⟩ ⇎ ⟦C⟧⟨This can be done by adding a leading (leftmost) ⟩; BR v2.0.2 整个换成值域尺 ⟦D⟧⟨MUST be a non-sequential number greater than zero (0) and less than 2¹⁵⁹⟩ 与 ⟦D⟧⟨containing at least 64 bits of output from a CSPRNG⟩; 实现侧给 DER 编码尺 ⟦E⟧⟨serial numbers encoded in DER as 8 bytes can be at most 63 bits long⟩ ⇎ ⟦E⟧⟨Encoding a 64-bit positive serial number requires a 9-byte encoded value⟩。三把尺当场互译: 20 字节去掉符号位是 159 位, 即上界 2^159−1——与 BR 那句 “less than 2¹⁵⁹” 同格; 内容长再大一枚要到 21 字节才装得下 2^160−1, 而 8 字节只到 63 位 ⇎ 2^63+1 要 9 字节。

⚖ 单位词与极性词的三把尺(子串 ⇎ 布尔表词界 ⇎ 断言正则)三轨逐枚同数 0 处分歧 ⇎ 子串尺比词界尺多读 358 枚(逐份 65 ⇎ 69 ⇎ 61 ⇎ 97 ⇎ 66): “octet” 在 2459 子串 47 ⇎ 词界 38, 差的 9 枚全落在 “octets” 里; “byte” 在 BR 面 124 ⇎ 112 ⇎ 在实现侧 93 ⇎ 40; 极性词 “positive” 词界档 0 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 4 ⇎ 子串档 2 ⇎ 3 ⇎ 2 ⇎ 0 ⇎ 4——2459 那两枚子串全在 ⟦A⟧⟨the construct "positiveint ::= INTEGER⟩ 里, 所以它其实一次都没把序列号说成“正整数”; “non-negative” 两档同 0 ⇎ 2 ⇎ 2 ⇎ 0 ⇎ 0 ⇎ 拼错的 “negitive” 五面 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 枚; “serialNumber” 驼峰形与 “serial number” 空格形各面 25 ⇎ 25 ⇎ 25 ⇎ 25 ⇎ 2 ⇎ 16 ⇎ 23 ⇎ 24 ⇎ 8 ⇎ 4; 上限三形: “20 octets” 0 ⇎ 8 ⇎ 8 ⇎ 0 ⇎ 0 ⇎ “64 bits” 0 ⇎ 0 ⇎ 0 ⇎ 10 ⇎ 0 ⇎ “2¹⁵⁹” 0 ⇎ 0 ⇎ 0 ⇎ 9 ⇎ 0——只有 BR 认上标那形, 而十进制 159 ⇎ 160 两形字样各面 0 ⇎ 1 ⇎ 4 ⇎ 0 ⇎ 0 ⇎ 2 ⇎ 2 ⇎ 3 ⇎ 2 ⇎ 1。

🪜 义务词两把尺: 逐行大写档 MUST 129 ⇎ 232 ⇎ 304 ⇎ 642 ⇎ 5 ⇎ 全篇折平小写档 MUST 133 ⇎ 235 ⇎ 308 ⇎ 664 ⇎ 24——两档之差合计 931 枚(逐份 254 ⇎ 141 ⇎ 367 ⇎ 134 ⇎ 35), 因为折平小写档把句中助动词 may 全吃了进来: MAY 那一格从 7 涨到 174(2459) ⇎ 从 55 涨到 381(5280); 纯换行的涨量另算(判词针那一层, 见 🔁), 两者不可混。指到序列号头上的强制式各代不同: 3280/5280 有 ⟦B⟧⟨The serial number MUST be a positive integer assigned by the CA⟩ ⇎ ⟦B⟧⟨CAs MUST force the serialNumber to be a non-negative integer⟩ ⇎ ⟦B⟧⟨Certificate users MUST be able to handle serialNumber values up to 20 octets⟩ 三句, 2459 一句都没有(它的 MUST 有 129 枚但都不在这件事上); BR 的强制式只出现在表行里(8 行值域句各属一节); 那句弱义务 ⟦C⟧⟨Certificate users SHOULD be prepared to gracefully handle such certificates⟩ 折平档 0 ⇎ 1 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 逐行档合计 0——锚身被硬换行劈开, 取哪一档决定它读不读得到。实现侧那一份通篇只有 24 枚 MUST(它讲编码不讲义务) ⇎ 却写着 ⟦E⟧⟨RFC 5280 requires that serial numbers be positive⟩。

🔁 反向对照: 判词针 24 枚在五份面各扫一遍 = 探针 120 次, 四档同摆(逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 重叠档); 逐行档合计 4 ⇎ 9 ⇎ 8 ⇎ 20 ⇎ 2 ⇎ 折平档 6 ⇎ 18 ⇎ 17 ⇎ 20 ⇎ 4 ⇎ 摘壳档 6 ⇎ 18 ⇎ 17 ⇎ 20 ⇎ 4 ⇎ 重叠档 6 ⇎ 18 ⇎ 17 ⇎ 20 ⇎ 4——摘壳与折平逐份同数(壳行不吃判词也不吐判词), 重叠档与不重叠档逐格同数(差 0); 折平比逐行多读 22 枚次 ⇎ 落在 18 格上, 即锚身被硬换行劈开的那些句子。独占账: 只一面读到的针 12 枚 ⇎ 两面同现 9 枚 ⇎ 三面及以上 3 枚, 其中上限句的拼写是最干净的一对照: ⟦B⟧⟨Conformant CAs MUST NOT use serialNumber values longer than 20 octets⟩ 只在 3280(0 ⇎ 2 ⇎ 0 ⇎ 0 ⇎ 0 枚)⇎ ⟦C⟧⟨Conforming CAs MUST NOT use serialNumber values longer than 20 octets⟩ 只在 5280(0 ⇎ 0 ⇎ 2 ⇎ 0 ⇎ 0 枚), 两面其余三家皆零; 同一处逗号也分家: ⟦B⟧⟨that are negative, or zero⟩ 只在 3280(0 ⇎ 1 ⇎ 0 ⇎ 0 ⇎ 0)⇎ ⟦C⟧⟨that are negative or zero⟩ 只在 5280(0 ⇎ 0 ⇎ 1 ⇎ 0 ⇎ 0)。

🧮 同宗三代正文块(§4.1.2.2 从 “The serial number” 到 4.1.2.3, 剥壳行后逐字符扫句界): 句数 2 ⇎ 8 ⇎ 8 ⇎ 0 ⇎ 0, 两把句界尺(逐字符扫 ⇎ 正则 re.split)逐句同列表 1; 句集容斥: 2459 的句被 3280 收下 1 枚 ⇎ 3280 与 5280 同句 6 枚 ⇎ 只 5280 有的新句 2 枚 ⇎ 只 3280 有而被删的句 2 枚——两式各自当场相加都回它自己的句数(合账零); BR 与实现侧没这段正文(句数 0 ⇎ 0)。义务词在正文块外的分布也照同一把尺记: MUST NOT 逐行档 9 ⇎ 24 ⇎ 34 ⇎ 146 ⇎ 0 ⇎ 折平档 10 ⇎ 26 ⇎ 36 ⇎ 150 ⇎ 1, SHOULD 25 ⇎ 47 ⇎ 82 ⇎ 45 ⇎ 0 ⇎ 45 ⇎ 58 ⇎ 112 ⇎ 54 ⇎ 8。

🧱 BR 把答案摊成表行: 一次枚出 7.1.2.x 标题 12 枚建清单, 再按行号 bisect 归属, 收到表行 11 行(值域句 8 行 ⇎ byte-for-byte 句 3 行, 两式相加 11), 八行值域句各属不同节 ⇎ 三行 bfb 分属 2 节两行 + 一节一行; 同一份 BR 文书的三张提取面(layout ⇎ raw ⇎ pypdf)字符 363639 ⇎ 291813 ⇎ 292250 ⇎ 2¹⁵⁹ 枚数 9 ⇎ 9 ⇎ 9 ⇎ CSPRNG 11 ⇎ 11 ⇎ 11 ⇎ 值域句 8 ⇎ 8 ⇎ 8——上标那形在三面同数, 而 CSPRNG 比值域句多的 1 枚正是变更表里 Ballot 156 的旧句(只束熵不束上界)。目录属性尺另在 RFC 两面印出: ub-serial-number 行种 0 ⇎ 2 ⇎ 2 ⇎ 0 ⇎ 0 ⇎ 现读值 None ⇎ 64 ⇎ 64 ⇎ None ⇎ None(2459 那一面压根没这行)。

🧬 DER 尺在两处落地: 5280 的 §7.1 样例把 (值, 内容长) 一并印出, 三代里只有它印——样例对总数 11(逐份 0 ⇎ 0 ⇎ 11 ⇎ 0 ⇎ 0), token 判形 ⇎ 正则选择支两轨同表 1, 闭式 bit_length ⇎ 逐次右移两把尺分歧 0 处 ⇎ 与面内印出的长度逐枚核对错 0 枚; 边界四枚现算: 2^159−1 → 20 字节 ⇎ 2^160−1 → 21 ⇎ 2^63−1 → 8 ⇎ 2^63+1 → 9。实现侧那一份把同一件事写成串: 九字节实例回收作 0209008000000000000001(tag 02 起头 ⇎ 长度字节 9 ⇎ 值 9223372036854775809 = 2^63+1), 串长 22 字符 = 2 + 2 + 2×9; 上标在 HTML 壳内作 1 枚 <sup>63</sup> ⇎ 剥壳后散作 “value 2 63” 1 枚 ⇎ “2 63 +1” 1 枚——尺子换了序列化就不在原地。

🧾 壳与对账: 页壳按世代分流——三份 RFC 走 [Page N] 页脚 129 ⇎ 129 ⇎ 151 ⇎ 0 ⇎ 0 行 ⇎ RFC 眉 128 ⇎ 128 ⇎ 150 ⇎ 1 ⇎ 2 行(成对差 1 ⇎ 1 ⇎ 1 ⇎ -1 ⇎ -2)⇎ IETF 独占行 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 0 ⇎ 换页符独占行 129 ⇎ 129 ⇎ 151 ⇎ 1 ⇎ 0; BR 走 “pg. N” 0 ⇎ 0 ⇎ 0 ⇎ 126 ⇎ 0 行而页脚为零 ⇎ 实现侧不剥(壳行 0); 两把壳尺(整行序列正则 ⇎ 逐字符游标定形)逐行同集, 分歧合计 0; 六形之和减重数回壳行数(容斥合账 0)。实现侧另有一层 HTML 壳: 标签 1436 枚 ⇎ 实体 201 枚 ⇎ 壳面 83252 字符 ⇎ 剥壳面 41053 字符 ⇎ 吃掉 42199 字符; 制表符只在这份里 432 枚(另四面零)。与采集遍 _pick95 逐键对账 60 项 ⇎ 符 60 项 ⇎ 不符 0 项(不符键名清单 0 枚, 空表即两遍逐键同数); 布尔门 27 枚全绿(红项 0); 恒等式 20 条逐条归零; 现量键 139 枚(该计数在自计量键落位前取, 故它本身与恒等式计数 20 都不在它数内); 判词针 24 枚 ⇎ 锚定行条目 39 条。ℒ 方法 ⇒ 这道题的隐性知识分四键: ①答案键 2459 不给数 ⇎ 3280/5280 给 20 字节 ⇎ BR 给 <2¹⁵⁹ 的值域与 ≥64 位熵 ⇎ 实现侧给 DER 内容长——四把尺要当场互译才知道同不同; ②尺键 字节数 ⇎ 比特位 ⇎ 十六进制字符数三把尺各自成句, 而“20 字节”与“2¹⁵⁹”相差的正是符号位那一枚; ③档键 同一判词在逐行 ⇎ 折平 ⇎ 摘壳 ⇎ 重叠四档给出四个数, 取哪档决定“这句话读不读得到”; ④层键 规范面把上限写成值或字节, 实现面把它写成编码长度——并且只有实现面把上标序列化换掉。


## ⛓解读注

本遍是第三套机制, 与前两遍只换机制不换定义: 面一律按 rb 读出再 `decode('utf-8','replace')`(文本模式会把 BR 那面 6385 枚回车静悄悄归一掉: 同一份文件文本模式落 357254 字符, 逐字节档读到 363639 字符), 行一律手工 `split('\n')`(不 splitlines, 不 readlines), 词与句一律逐字符扫, 字面针一律 `str.count`, 窗定界一律整行等值, HTML 剥壳一律 `'<'` 游标状态机, DER 内容长一律十六进制字符路。前两遍的中间量一枚都不复用。

### 压缩账(五份一律 rb 逐字节读出, 本遍现读)
| 量 | 2459 ⇎ 3280 ⇎ 5280 ⇎ br ⇎ le |
|---|---|
| 字节面 ⇎ 码位面 | 278438⇎295556⇎352580⇎366098⇎83392 ⇎ 278438⇎295556⇎352580⇎363639⇎83252 |
| UTF-8 多出的字节(=码位差) | 0⇎0⇎0⇎2459⇎140 |
| 手工切行 ⇎ 逐字符数换行 ⇎ 数回车 | 7228⇎7228⇎8460⇎6386⇎1706 ⇎ 7227⇎7227⇎8459⇎6385⇎1705 ⇎ 0⇎0⇎0⇎6385⇎0 |
| 逐字符扫词 | 34970⇎39871⇎45190⇎40210⇎8692 |
| 唯一码位 ⇎ 非 ASCII 枚 ⇎ 非 ASCII 去重 | 92⇎93⇎96⇎105⇎143 ⇎ 0⇎0⇎0⇎1234⇎112 ⇎ 0⇎0⇎0⇎11⇎50 |
| 子串档 `20 octets`(敏感 ⇎ 不敏感 ⇎ 整词三档同值) | 0⇎8⇎8⇎0⇎0 ⇎ 0⇎8⇎8⇎0⇎0 ⇎ 0⇎8⇎8⇎0⇎0 |
| `serialNumber` 敏感子串 ⇎ 不敏感子串 ⇎ 整词 | 3⇎9⇎9⇎22⇎1 ⇎ 25⇎25⇎25⇎25⇎2 ⇎ 3⇎11⇎11⇎22⇎1 |
| `2¹⁵⁹` 枚数 | 0⇎0⇎0⇎9⇎0 |
| §4.1.2.2 窗字符(正文首行起, 原面 ⇎ 剥壳面) | 219⇎899⇎743⇎—⇎— ⇎ 217⇎740⇎739⇎—⇎— |

编码区 6524 字符(不含换行) ⇎ 五份源面合 1373465 字符(字节合 1376064, 差 2599 恰为后两份各 2459 ⇎ 140 枚非 ASCII 的 UTF-8 余量) = 0.48% ⇎ 在档摘录 1305 字符(去换行)⇎1351(含换行): 编码⇎摘录两把尺 499.92%⇎482.90%。

### 四处只有换尺子才看得见的岔口(本注现读出)
① 行尺: 手工 `split('\n')` 在 br 那面把 6385 枚回车留在行尾, 于是"最长行"这格本遍读 162, 而建条遍先把行尾回车剥掉再量得 161——其余四面两档同值(134⇎72⇎72⇎1955 ⇎ 134⇎72⇎72⇎1955)。同一枚"行"在三份 RFC 面上没有回车, 差别只发生在那份全 CRLF 面上。
② 定界档: 只对整个面用纯 `find('4.1.2.2')` 起、`find('4.1.2.3')` 止, 三份 RFC 全落在目录行(面偏移 4231 ⇎ 3530 ⇎ 3875), 窗长只有 73 ⇎ 68 ⇎ 73 字符, 里面一枚答值都读不到; 换成本遍的整行等值定界, 窗起于第 966–973 ⇎ 941–968 ⇎ 1039–1056 行(1 基, 含头不含尾), 原窗 242 ⇎ 922 ⇎ 767 字符。建条遍之所以没踩这个坑, 是因为它的题面针取的是正文首句 'The serial number' 而不是节号——目录行里没有 'the'。
③ 窗内句数的两处档差(与注册 [2,8,8] 相对): 5280 的节号写作 '4.1.2.2.  Serial Number', 末尾那枚句号加空格在折平面上自造一处断点, 于是含题面行的窗给 9 句, 从正文首行起给 8 句; 3280 含题面不剥壳给 10 句, 同窗剥壳后给 8 句——枚数差只有 2, 集合差却有 3 句(['housley, et.', 'al.', 'standards track [pag']): 页眉行折进断面之后 'et. al.' 里的两枚句点各造一处断点, 另一句是整行页眉被当成一句。本遍剥壳+正文起档逐格回 [2,8,8], 句集容斥也逐格回 2459∩3280 1 ⇎ 3280∩5280 同句 6 ⇎ 5280 新句 2 ⇎ 3280 被删 2(前两遍用集合 & ⇎ Counter 直方图, 本遍用多重集手工双重循环)。
④ 大小写档与词界档: `serialNumber` 敏感子串 3⇎9⇎9⇎22⇎1 ⇎ 不敏感 25⇎25⇎25⇎25⇎2 ⇎ 不敏感面上加整词边界 3⇎11⇎11⇎22⇎1, 差的那 22⇎16⇎16⇎3⇎1 枚几乎全长在 ASN.1 结构名 `CertificateSerialNumber` 里(逐份 16⇎11⇎11⇎0⇎1 枚)——所以编码区给 25 那一格记的是不敏感子串档, 不是"驼峰那个拼法写了 3 次"。`octet` 在 2459 子串 47 ⇎ 整词 38, 差的 9 枚全在 `octets` 内; `positive` 整词 0⇎1⇎1⇎0⇎4 ⇎ 子串 2⇎3⇎2⇎0⇎4, 2459 那两枚子串都长在 `positiveInt`(它 2 枚)里, 这正是"它一次都没把序列号说成正整数"的根据; `Conformant` 敏感 4 ⇎ 不敏感 6(3280 面内另有 2 枚小写)。义务词两档同摆: MUST 逐行 129⇎232⇎304⇎642⇎5 ⇎ 折平 133⇎235⇎308⇎664⇎24, MAY 逐行 7⇎56⇎55⇎164⇎0 ⇎ 折平 174⇎180⇎381⇎247⇎5——折平档把句中助动词 may 全吃进来。

### DER 这把尺的第三条路(本遍)
边界四枚现算 20 ⇎ 21 ⇎ 8 ⇎ 9 与登记同值(依次是 2^159−1 ⇎ 2^160−1 ⇎ 2^63−1 ⇎ 2^63+1 所需的 DER 内容字节数)。但这把尺一上手就错了 7 枚: 样例里补零前后结果不同的值([1, 2, 256, 65537])——十六进制位数是奇数时不先补前导零, 那半枚字节在整除时被丢掉, 内容长就少算一枚; 补零后与面上印出的长度逐枚核对, 全五份共收 11 对(错 0 枚), 这些对全部落在 §7.1 那串样例里, 回收的样例对表与前两遍同一条 [(2, 1), (17, 1), (65537, 3), (2, 1), (18, 1), (65537, 3), (2, 1), (256, 2), (1, 1), (18, 1), (12, 1)]。§7.1 的抽取路数是"冒号左侧末 token 即内容长"(建条遍是 token 判形, 采集遍是正则选择支)。实现侧那面本遍收出 9 条 hex 长串(串长 8 字节组起收), 以 02 起头的那条是唯一取用的一条: `02 09 00 80 00 00 00 00 00 00 01` ⇎ tag 2 ⇎ 内容长 9 ⇎ 值 9223372036854775809 = 2^63+1, 紧凑串长 22 字符。

### 序列化换了, 针就不在原地(BR 三面 ⇎ 实现侧壳内)
同一份 CA/B TLS BR 的三张提取面(layout ⇎ raw ⇎ pypdf)字符 363639⇎291813⇎292250 ⇎ 2¹⁵⁹ 9⇎9⇎9 ⇎ CSPRNG 11⇎11⇎11 ⇎ 值域句 8⇎8⇎8——三面同数, 上标那形没被任何一张面拆散。实现侧那一份是带标签网页: 同一个 2^63 在壳内作 1 枚 <sup>63</sup>, 在剥出的断面上散作 'value 2 63' 1 枚 ⇎ '2 63 +1' 1 枚, 在粘面(标签替空串)上作 'value 263' 1 枚 ⇎ '263+1' 1 枚——枚数没变, 字面针却要跟着档换形。本遍自己游标剥壳得 断面 50312 字符/1539 行 ⇎ 粘面 48876 字符, 与盘上那份预剥文件 41053 字符/909 行不是同一把尺, 所以 ⟦E⟧ 的 3 枚锚一律在本遍断面上比, 不复用预剥文件。

### 锚核验(24 处 ⟦标签⟧⟨原文⟩ ⇎ 去重 19 串, 逐枚按标签回本家文件)
本家面逐字符 verbatim 命中 11 处; 另有 12 处要把空白折成一枚空格才命中(锚身被硬换行劈开); 把面与锚同时小写后再比则 24/24 全命中——多出来的那 1 处只与大小写有关, 是 ⟦A⟧⟨the construct "positiveint ::= INTEGER⟩ 一枚: 面上作 `The construct "positiveInt ::= INTEGER`, 词表按小写收进来, 门里的比对面(prose_norm 归一大小写与引号)认它, 逐字符档不认。⟦E⟧ 那 3 处锚在未剥的壳面上命中 1 处、在本遍断面上命中 1 处: 挡住它们的不是标签而是硬换行。去重后 19 串里有 9 串在别家面上也读得到(按引用算是跨家同现 12 处), 其中最干净的是 `Conformant`/`Conforming` 那一对与逗号那一对, 各自只在一面成句。

### 读法
编码区九段各管一副账: 🧭 五份面尺三轨行账 ⇎ 码位与字节两把尺只在后两份分开(差 2459 ⇎ 140), 逐枚非 ASCII 多出的字节两路相减归零; 📏 答值四代四把尺互不译(2459 一枚长度都不给: `20 octets` 最宽档 0 枚, `positive` 整词档 0 枚), 3280 给 20 字节, BR 给 <2¹⁵⁹ 值域与 ≥64 位熵, 实现侧给 DER 内容长; ⚖ 单位词三轨(子串 ⇎ 布尔表词界 ⇎ 断言正则)逐枚同数, 子串尺比词界尺多读的那 358 枚是复数词尾与驼峰内嵌; 🪜 义务词两档 ⇎ 那句弱义务折平档 0⇎1⇎1⇎0⇎0 ⇎ 逐行档合计 0; 🔁 判词针 24 枚×五份的四档可读性 ⇎ 独占账 12 枚只一面读到; 🧮 同宗三代正文块句数 [2,8,8] 与句集容斥; 🧱 BR 表行按节归属(八行值域句各属一节 ⇎ 三行 byte-for-byte 分属两节)与 ub-serial-number 的 64(第三种尺: 字符数); 🧬 DER 样例对与边界四枚; 🧾 壳账与对账 60 项 ⇎ 逐键符 60 ⇎ 不符 0 ⇎ 布尔门 27/27。核心结论一条: 这道题的四代答案不在同一把尺上——字节数 ⇎ 比特位 ⇎ 值域 ⇎ 编码内容长, 只有把 20 字节去掉符号位换成 159 位, 才能看出 3280/5280 与 BR 那两句其实同格, 而 8 字节只能到 63 位这件事只有实现面写了出来。

### 本条不能由在库文件判定的(只登记, 不进门槛)
现网证书里实际用到的序列号长度分布 ⇎ CA 实现是否真按 BR 的 ≥64 位熵发号(本条只认规范面自身) ⇎ RFC 勘误表与改版后的现值 ⇎ BR 版本号 v2.0.2 之后是否仍写 2¹⁵⁹。上游一旦改版, 编码区里由面上现读的数就只在本机这份快照成立。

### 编码与门的账
T1 逐锚回源: 本注逐字符档 11/24 ⇎ 折空白档 23/24 ⇎ 折平小写档 24/24(门按 prose_norm 档判, 与本遍折平小写档同族) ⇎ T2 DERIV 复算: 128 枚键由 corpus/_b95contract.json 逐枚现算(其中 58 枚是复合式或聚合式而非直取值), 门内现量 140 键与建条遍逐键同值 ⇎ T3 码位账: 五份源面唯一码位 92⇎93⇎96⇎105⇎143(并集另计)。对账 60 项 ⇎ 符 60 ⇎ 不符 0 ⇎ 布尔门 27/27 全绿。
