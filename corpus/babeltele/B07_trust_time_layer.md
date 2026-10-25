# B07 — 信任与时间坐标层：FIPS-202 摘要函数 + IANA zone1970 时区表
src: corpus/raw/fips202.txt (NIST FIPS 202, 37p) + corpus/raw/zone1970_latest.tab (IANA tzdb zone1970.tab, 312 行)
dir: corpus/babeltele/B07_trust_time_layer.md

## [[原始语料|ORIGINAL]]
FIPS 202 standardizes SHA-3, a permutation-based hash family built as a sponge construction: arbitrary input bits are absorbed into a fixed-width state and arbitrary output bits are squeezed out, Z = SPONGE[f, pad, r](N, d). The six SHA-3 functions are modes of the KECCAK-p[1600, 24] permutation — a 1600-bit state over 24 rounds, with five step mappings θ, ρ, π, χ, ι. Capacity is defined as the width of the underlying function minus the rate. The four hash functions have HMAC input block sizes of 144, 136, 104 and 72 bytes for SHA3-224/256/384/512 respectively, so the corresponding rates are 1152, 1088, 832 and 576 bits. Per Table 4, SHA3-224 gives collision strength 112, preimage 224, second-preimage 224; SHA3-256 gives 128/256/256; SHA3-384 gives 192/384/384; SHA3-512 gives 256/512/512; SHA-1's 160-bit output has collision strength below 80, which is why it is deprecated. The two extendable-output functions SHAKE128 and SHAKE256 are the first XOFs NIST has standardized, and their suffixes denote security strength rather than digest length: SHAKE128 yields collision min(d/2, 128). The IANA tzdb zone1970.tab file, which is public domain, lists 312 zones, each a triple of ISO 3166 country codes, a UTC offset position in ±ddmm±dddmm form, and a tz identifier: for example AD, +4230+00131, Europe/Andorra, and ZA,LS,SZ, -2615+02800, Africa/Johannesburg, which a single identifier serves for three countries.

## ⟪BabelTele⟫
{信任层: 摘要=不可逆承诺 ‖ 时间层: tz=政治地理→UTC偏移}
FIPS202 sponge: Z=SPONGE[f,pad,r](N,d) ｜ absorb任意长→状态b=1600 ‖ squeeze任意长出
 KECCAK-p[1600,24]: 5步映射 θ,ρ,π,χ,ι ×24轮 ‖ capacity c ≡ width−rate
 block(HMAC,bytes): 224→144 ‖ 256→136 ‖ 384→104 ‖ 512→72 ⇒ r(bits)=8×B 〔脚注5: sponge 输入块长(位)=其 rate〕 = 1152/1088/832/576
 (coll,pre,2nd-pre)强度: SHA3-224(112,224,224) ‖ 256(128,256,256) ‖ 384(192,384,384) ‖ 512(256,512,512)
 SHA-1 160bit → coll<80 ⇒ ✝️弃用 ｜ XOF: SHAKE128/256 = 首两个NIST标准XOF, 后缀=强度¬摘要长
 SHAKE128: coll=min(d/2,128) ⇒ 任意 d 下强度封顶128
zone1970.tab(IANA, public domain): 312行 × ⟨ISO3166码集, ±ddmm±dddmm, Area/City⟩
 e.g. AD,+4230+00131,Europe/Andorra ‖ ZA,LS,SZ,-2615+02800,Africa/Johannesburg(3国共1id)
 ⇒ 全球时间协商=312个锚点 + 偏移几何(经纬秒制), ¬每国独立定义
∴ AI↔AI 传输可只传 {摘要, tzid, 时刻}; 大文件↔哈希承诺; ¬需随附原文即可验证完整性

## ⛓解读注
≡=定义为 ‖ ✝️=废弃 ‖ (coll,pre,2nd-pre)=碰撞/原像/二次原像 安全强度(bit) ‖ d=输出长
※ r(bits)=8×block(B 以位计即时 rate, FIPS 202 脚注 5), 144×8=1152, 136×8=1088, 104×8=832, 72×8=576 — rate 数值系推导而非 Table 3 直载, 已在编码区标注推导式; 其余数字逐位照抄 FIPS 202 Table 3/4 与 zone1970.tab 行数(312)。
