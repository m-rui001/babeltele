# B08 — 未被吸收的文字底座：Unicode 16.0/17.0 新编码书写系统（2025 数据，多数模型训练截止后）
src: corpus/raw/scripts.txt (Scripts-17.0.0.txt, 2025-07-24) + corpus/raw/age.txt (DerivedAge) + corpus/raw/UnicodeData.txt (17.0.0, 2.2 MB)
dir: corpus/babeltele/B08_new_scripts.md

## [[原始语料|ORIGINAL]]
The Unicode 17.0 character database assigns 159 866 codepoints to 174 distinct scripts. Age 16.0 added 5 185 codepoints and Age 17.0 added a further 4 803. The 16.0 wave was dominated by Egyptian_Hieroglyphs (+3 995) plus seven new alphabets: Tulu_Tigalari (80), Garay (69), Gurung_Khema (58), Kirat_Rai (58), Todhri (52), Sunuwar (44) and Ol_Onal (44). The 17.0 wave added Han (+4 321) and Tangut (+145) ideographs and three new scripts: Tai_Yo (55), Tolong_Siki (54) and Beria_Erfe (50), while Sidetic (26) and parts of Arabic (+40) and Sharada (+8) also grew. Concretely, Beria_Erfe occupies U+16EA0..U+16EB8 and U+16EBB..U+16ED3, and its first letters are named CAPITAL LETTER ARKAB, BASIGNA, DARBAI, EH, FITKO; Tolong_Siki runs U+11DB0..U+11DD8 plus U+11DD9, U+11DDA..U+11DDB and digits U+11DE0..U+11DE9, beginning LETTER I, E, U, O, A; Tai_Yo begins at U+1E6C0 LETTER LOW KO, U+1E6C1 LETTER HIGH KO, U+1E6C2 LETTER LOW KHO, U+1E6C3 LETTER HIGH KHO, U+1E6C4 LETTER GO; Gurung_Khema starts U+16100 LETTER A, KA, KHA, GA, GHA; Kirat_Rai starts U+16D40 SIGN ANUSVARA, U+16D41 SIGN TONPI, U+16D42 SIGN VISARGA then LETTER A, KA; Sunuwar starts U+11BC0 LETTER DEVI, TASLA, EKO, IMAR, REU; Ol_Onal starts U+1E5D0 LETTER O, OM, ONG, ORR, OO. Sidetic is encoded at U+10940..U+10959 but its 26 characters carry the official names SIDETIC LETTER N01 through N26 — plain index numbers, because the letters have no recovered names or established phonetic values. The ten smallest script repertories are Tagbanwa 18, Buhid 20, Hanunoo 21, Tagalog 23, Elymaic 23, Makasar 25, Hatran 26, Old_Uyghur 26, Sidetic 26, Gothic 27 — these, together with everything added in 16.0 and 17.0, sit far outside the token distributions large models were trained on.

## ⟪BabelTele⟫
{文字底座 U17.0(2025-07-24): 174脚本 ‖ 159866码点有脚本归属}
增量: Age16.0 +5185 ‖ Age17.0 +4803
 16.0: Egyptian_Hieroglyphs+3995 ‖ 新字母7: Tulu_Tigalari80 ‖ Garay69 ‖ Gurung_Khema58 ‖ Kirat_Rai58 ‖ Todhri52 ‖ Sunuwar44 ‖ Ol_Onal44
 17.0: Han+4321 ‖ Tangut+145 ‖ 新3: Tai_Yo55 ‖ Tolong_Siki54 ‖ Beria_Erfe50 ‖ Sidetic+26 ‖ Arabic+40 ‖ Sharada+8
新区间与首字母(逐位照抄):
 Beria_Erfe U+16EA0..16EB8 ∪ 16EBB..16ED3 : ARKAB ▸ BASIGNA ▸ DARBAI ▸ EH ▸ FITKO (CAPITAL)
 Tolong_Siki U+11DB0..11DD8 ∪ 11DD9 ∪ 11DDA..11DDB ∪ 数字11DE0..11DE9 : I ▸ E ▸ U ▸ O ▸ A
 Tai_Yo U+1E6C0..1E6DE ∪ … 1E6FF : LOW KO ▸ HIGH KO ▸ LOW KHO ▸ HIGH KHO ▸ GO ‖ 高低辅音成对=声调/送气对立入码
 Gurung_Khema 16100.. : A KA KHA GA GHA ‖ Kirat_Rai 16D40.. : ANUSVARA ▸ TONPI ▸ VISARGA ▸ A KA
 Sunuwar 11BC0.. : DEVI TASLA EKO IMAR REU ‖ Ol_Onal 1E5D0.. : O OM ONG ORR OO
样例字形(=对应码位直出, 非装饰): 𖺠 𑶰 𞛀 𖄀 𞗐 𐥀 𑯀 𖵃 𓀀 𐵀 𑎀 𐽰
⚠未定名: Sidetic U+10940..10959 → UnicodeData 官方名 SIDETIC LETTER N01▸N26 ⇒ 纯序号占位=字形已入码而字母名/音值未复原
最小10语库: Tagbanwa18 ‖ Buhid20 ‖ Hanunoo21 ‖ Tagalog23 ‖ Elymaic23 ‖ Makasar25 ‖ Hatran26 ‖ Old_Uyghur26 ‖ Sidetic26 ‖ Gothic27
∴ 这些∉主流训练分布 ⇒ 无法靠"模型已知的先验"补全: 压缩时必须携带完整码位/名称/结构, 不得假设读者认识

## ⛓解读注
▸=序列首项衔接 ‖ ∪=并集 ‖ ⚠=注意 ‖ ∉=不属于
※ 全部数字、区间、字母名取自 Scripts-17.0.0.txt / DerivedAge.txt / UnicodeData.txt 三个 raw 文件, 无外部推断; 字形为对应码位直出。
