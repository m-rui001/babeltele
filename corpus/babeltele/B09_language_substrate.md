# B09 — 未被吸收的语言标识底座：IANA BCP-47 语言子标签注册表（活数据，File-Date 2026-09-17）
src: corpus/raw/langsubtag.txt (language-subtag-registry, 731 819 B, File-Date: 2026-09-17)
dir: corpus/babeltele/B09_language_substrate.md

## [[原始语料|ORIGINAL]]
The IANA language subtag registry (BCP 47) with File-Date 2026-09-17 holds 9296 records: 8276 of Type language, 305 region, 258 extlang, 225 script, 139 variant, 67 redundant and 26 grandfathered. Shapes are bounded: language subtags are 2 letters (190 records) or 3 letters (8085), plus one private-use range qaa..qtz; every extlang is 3 letters; script subtags are 4 letters (224) plus the private-use range Qaaa..Qabx; region subtags are 2 characters (272), 3 digits (31, e.g. 001 World, 002 Africa, 003 North America) or private ranges QM..QZ and XA..XZ; variants run 4 to 8 characters and 132 of the 139 require a Prefix. Grouping is explicit: 63 language subtags carry Scope macrolanguage (sh Serbo-Croatian, zh Chinese, gon Gondi) and 545 records point back to a macrolanguage through a Macrolanguage field; 134 language records carry Suppress-Script (ab Cyrl, af Latn, am Ethi, ar Arab, as Beng). 302 records are Deprecated and redirect through Preferred-Value: in to id and iw to he (both Deprecated 1989-01-01), mo (Moldavian) to ro (2008-11-22). Registration is still growing: 7552 records carry Added 2009, 18 carry 2024, 18 carry 2025 and 15 carry 2026, among them language subtags dyl Bhutanese Sign Language, lfb Buu (Cameroon), olb Oli-Bodiman, osd Digor Ossetic, scz Shaetlan and zhk Kurdish Sign Language, plus the collection subtag bih Bihari languages (Scope collection, Added 2026-06-14) and the variants taglish (Tagalog-English code-switching), radikalt and moderat (Bokmal spelling variants), stadi (a Helsinki dialect of Finnish) and slepe (a Sorbian dialect of Schleife). A language subtag averages 3 characters against a mean primary English name of 8.69 characters, so the register is already a 2.9-fold compression of human language names, at the cost of ambiguity that only the registry itself can resolve.

## ⟪BabelTele⟫
{标识底座 IANA-registry @File-Date 2026-09-17 ｜ 9296条记录=活数据¬可凭先验复现}
型分布: language8276 ‖ region305 ‖ extlang258 ‖ script225 ‖ variant139 ‖ redundant67 ‖ grandfathered26
形状界: lang=2字母190 ∪ 3字母8085 ∪ 私用域⟨qaa..qtz⟩ ‖ extlang≡3字母(258/258) ‖ script=4字母224 ∪ 私用域⟨Qaaa..Qabx⟩
 region=2字符272 ∪ 3数字31(⟨001⟩=World,⟨002⟩=Africa,⟨003⟩=NorthAmerica) ∪ 范围⟨QM..QZ⟩,⟨XA..XZ⟩ ‖ variant=4-8字符, 其中132条强制Prefix
聚合: Scope:macrolanguage 63 (⟨sh⟩=Serbo-Croatian ‖ ⟨zh⟩=Chinese ‖ ⟨gon⟩=Gondi) ⇐ 545条以 Macrolanguage: 字段回指
 Suppress-Script 134 (⟨ab⟩⤷Cyrl ⟨af⟩⤷Latn ⟨am⟩⤷Ethi ⟨ar⟩⤷Arab ⟨as⟩⤷Beng) ⇒ 默认书写系统亦为注册事实, 非模型常识
废弃账: 302条 Deprecated∧Preferred-Value ‖ ⟨in⟩⤷id ∧ ⟨iw⟩⤷he (Deprecated 1989-01-01) ‖ ⟨mo⟩(Moldavian)⤷ro (2008-11-22)
增长: Added 2009=7552 ‖ 2024=18 ‖ 2025=18 ‖ 2026=15 ⇒ 注册未冻结 ⇒ 任何模型的知识截止即=失效点
 2026新增(训练截止后, 无法外推): ⟨dyl⟩=Bhutanese SignLanguage ‖ ⟨lfb⟩=Buu(Cameroon) ‖ ⟨olb⟩=Oli-Bodiman ‖ ⟨osd⟩=Digor Ossetic ‖ ⟨scz⟩=Shaetlan ‖ ⟨zhk⟩=Kurdish SignLanguage ‖ ⟨bih⟩=Bihari languages(Scope:collection, 2026-06-14)
 2026 variant: ⟨taglish⟩=Tagalog↔English code-switch ‖ ⟨radikalt⟩/⟨moderat⟩=Bokmål拼写两派(2026-04-21) ‖ ⟨stadi⟩=Helsinki slang(Fin) ‖ ⟨slepe⟩=Sorbian dialect(Schleife)
密度核算: subtag均长3 ‖ 英语主名均长8.69 ⇒ 标识=名长的2.9倍压缩, 且无歧义(唯一权威=注册表)
∴ π(🤖↔🤖): 传 {subtag, File-Date} ¬传 英语名 ⇒ 名称歧义(⟨sh⟩已废 ∨ 63个macrolanguage ∨ 302条deprecated)不进传输
⌛🧑t: 语言名书写/核对⏱→0; 但"该 subtag 在截止后是否变更"¬可省 ⇒ 必须随文携带 File-Date

## ⛓解读注
≡=恒等 ‖ ⇐=被回指 ‖ ⤷=重定向/默认 ‖ ∪=并集 ‖ ¬=不 ‖ π=协议建议 ‖ 数字口径=记录条数(records), 非语言数

※ ⟨⟩ 内的每个 subtag 均已对照注册表核验存在；全部计数由 langsubtag.txt 现场重算(audit.py: RS/RC/SCOPE/FIELD/DEPR/SUPPR/ADDED/VARPREF/LEN), 非引用二手统计; 8.69=language 记录 Description 主名平均字符长, 2.9=8.69/3(四舍五入1位); 2026-06-14 与 2026-04-21 为记录内 Added 字段逐位照抄。
