# B10 — 未被吸收的时间坐标变动：tzdb 2026a–2026e（活法源，2026 年内 5 次发布）
src: corpus/raw/tz/{NEWS,version,zone1970.tab,zonenow.tab,leap-seconds.list}（data.iana.org/time-zones/tzdata-latest.tar.gz, 481 989 B）
dir: corpus/babeltele/B10_tz_live_deltas.md

## [[原始语料|ORIGINAL]]
The tz database release named in its version file is 2026e, and its NEWS log lists 313 releases in total; 2026 alone accounts for five: 2026a on 2026-03-01, 2026b on 2026-04-22, 2026c on 2026-07-08, 2026d on 2026-09-11 and 2026e on 2026-09-29 — 212 days from the first to the fifth. Each of 2026b through 2026e records a jurisdiction abolishing seasonal clock change: British Columbia moved to permanent -07 legally on 2026-03-09 (2026b), Alberta to permanent -06 on 2026-06-18 (2026c), Canada's Northwest Territories to permanent -06 on 2026-08-21 (2026d, affecting only America/Inuvik) and Manitoba to permanent -05 on 2026-10-31 (2026e, America/Winnipeg plus the obsolescent Canada/Central link). Morocco, and with it Western Sahara, plans to move back to permanent UTC with no daylight saving transitions on 2026-09-20 at 02:00 (2026c). Because Unicode CLDR 48.1 (2026-01-08) cannot model the change at its legal date, the Canadian releases deliberately model the switch at 2026-11-01 at 02:00 as a temporary hack that is to be removed once CLDR is fixed, and the abbreviations revert to traditional ones (MST for -07 in America/Vancouver, CST for Alberta and the Northwest Territories, EST for Manitoba). The hack requires a zic fix: without it, zic versions 2023d through 2026a in default slim mode emit a TZif file that violates Internet RFC 9636 section 3.3, so readers may ignore the 2026-11-01 02:00 PDT-to-MST transition; the workaround for those versions is 'zic -b fat'. Past timestamps were also corrected: in 1925 Ireland fell back on 09-20 rather than 10-04 (2026e), and the spring-forward transitions of Colombia 1992-05-02 and Iran 1979-05-26 were at 00:00 rather than 24:00 (2026d). The backward-compatibility names EST5EDT, CST6CDT, MST7MDT and PST8PDT now conform better to POSIX, always using EST/EDT-style abbreviations, which affects timestamps before 1966-10-30 at 01:00 standard time. 2026a stopped installing the "right" TZif files by default, added -DTZ_RUNTIME_LEAPS=0 to disable runtime leap-second support, removed the 50-byte limit on TZif abbreviation data, and noted that Moldova has used EU transition times since 2022. Two distribution tables coexist: zone1970.tab has 312 rows while zonenow.tab, "for users who do not care about old timestamps", has 91. leap-seconds.list carries 28 entries whose last is NTP 3692217600 with TAI-UTC = 37 seconds from 1 Jan 2017, and the file states it expires on 28 June 2027.

## ⟪BabelTele⟫
{时间坐标=活法源: tzdb@⟨2026e⟩ ｜ 2026 年内 5 发(a:2026-03-01 b:04-22 c:07-08 d:09-11 e:09-29) ⇒ 3-9 月间隔¬年更}
NEWS 全史 313 发 ‖ 首末 2026a→2026e 跨 212 日
2026 主题=废除季节钟(4 个法域转向永久偏移):
 BC ⟨2026-03-09⟩→permanent -07 (America/Vancouver, 缩写 MST) ‖ Alberta ⟨2026-06-18⟩→-06 (Edmonton, CST)
 ‖ NWT ⟨2026-08-21⟩→-06 (仅 Inuvik, CST) ‖ Manitoba ⟨2026-10-31⟩→-05 (Winnipeg ∧ Canada/Central, EST)
 ‖ Morocco∧W.Sahara ⟨2026-09-20⟩02:00→permanent +00(¬DST)
建模谎言(必须随文声明, 否则读者误推): 加拿大 4 案法律日≠建模日 ⇒ 统一 hack 至 ⟨2026-11-01⟩ 02:00
 ∵ Unicode CLDR 48.1 (⟨2026-01-08⟩) 无法表达 ‖ 该 hack 计划于 CLDR 修复后移除
 连带: zic 若为 2023d..2026a 默认 slim 模式 ⇒ 产出 TZif 违反 RFC 9636 §3.3 ⇒ 读者丢 PDT→MST 转换 ⇒ 规避 'zic -b fat'
过去时刻亦被改写(¬不可缓存的历史): Ireland 1925 回钟 09-20 而非 10-04 ‖ Colombia 1992-05-02 ∧ Iran 1979-05-26 春进 00:00 而非 24:00
 EST5EDT/CST6CDT/MST7MDT/PST8PDT 改依 POSIX(恒用 EST/EDT 类缩写) ⇒ 影响 ⟨1966-10-30⟩ 01:00 之前全部时戳
2026a 结构变更: "right" TZif ¬默认安装 ‖ -DTZ_RUNTIME_LEAPS=0 ‖ TZif 缩写区 ¬限 50 字节 ‖ Moldova 自 2022 用 EU 转换时刻
双表并存: zone1970.tab 312 行(含历史) ‖ zonenow.tab 91 行("do not care about old timestamps") ⇒ 同一地球 2 套坐标系
闰秒账: leap-seconds.list 28 条 ‖ 末条 NTP 3692217600 ⇒ TAI−UTC=37 s @ ⟨2017-01-01⟩ ‖ 文件自陈过期 ⟨2027-06-28⟩
∴ π(🤖↔🤖): 时刻必须携带 {tzdb 版本, zone id} 二件, ¬可只传 UTC/偏移
 单传 "Vancouver 2026-07-01 10:00" ⇒ 在 2026a 视图与 2026e 视图下差 1 小时 ⇒ 语义依赖发布号而非时钟本身
⌛🧑t: 人类无需再核对"该地今年是否改钟"; 但"版本¬可省"⇒ 时间沟通的成本从记忆移至版本号

## ⛓解读注
⟨X⟩=日期/版本号原子, 逐位照抄 NEWS/version(与 B09 的 ⟨subtag⟩ 同一约定) ‖ ∵=因为 ‖ ¬=不 ‖ §=条款 ‖ hack=官方临时建模近似 ‖ 缩写 MST/CST/EST=标准时字母
※ 313=NEWS 中 `^Release` 行数; 5=其中以 2026 开头的行数; 212=DAYS("2026a","2026e")=NEWS 内两 release 日期之差; 312=zone1970.tab 行数;
 91=zonenow.tab 行数; 28=leap-seconds.list 数据行数; 37=该表末条第二列 —— 全部由 audit.py 现算, 非引用二手统计。
