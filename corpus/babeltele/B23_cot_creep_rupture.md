# B23 — 思维链语料：加热炉炉管蠕变断裂的法证推理（deepseek-v4.1-flash-free 原始 reasoning, 三层因果＋Robinson 界限账＋假说否证）
src: corpus/raw/cot/ind_creep_rupture.md (prompt + REASONING 22 236 字符逐字; answer 段为空, reasoning 截收于 "If 596 reading was only at the end but unknown, this")
dir: corpus/babeltele/B23_cot_creep_rupture.md

## [[原始语料|ORIGINAL]]
Six weeks later, during a startup at 74

(4) Rule on the client's API 560 assertion and explain, as a matter of reasoning method rather than citation, how you decide which standard governs a given allegation. (5) List what you would need but do not have.

Six weeks later startup at 74% design rate outlet tube fired heater ruptured, H2 at 62 bar, light feed, fire.

second element failed open-circuit 11 days earlier not replaced. - decoke steam/air online. Last decoke ran 3h longer, boiler house steam pressure fell 24 to 15 bar mid-cycle. Combustion air registers lower burner row found after shutdown linkages hand-tight against stops. - creep data coupon: rupture life at 540C/120MPa ~3500 h; at 595C/120MPa ~220h. - operator log: tube-side flow control valve 4% open when heater lit, bypass 100% open. Procedure revision 5 months earlier swapped two valve line-items in lighting checklist. - wall thickness rupture 1.9 mm vs 3.4 nominal; adjacent 3.2-3.3 with visible necking.

False; API 560 design/fab, API570/573 in-service; no annual interval.

They say two exchangers maybe "two exchangers" = two temp regimes? Need infer: likely 540 and 595? They mention "for the two exchangers" perhaps typo "two excursions"? We nee

Six weeks = 42 days *24=1008 h.

We don't know duration at 596.

- If entire 1008 h at 595, D = 1008/220 = 4.58 (fail). - If entire 1008 h at 540, D=0.288. - If 11 days (264 h) at 595 + rest 744 at 540: D=264/220 +744/3500=1.20+0.213=1.41. Failure.

- If only decoke extra 3h at 595: negligible 0.014. - If heated 24h at 595 plus 984 at 540: 0.109+0.281=0.390.

Thin-wall hoop stress σ = pD/(2t). Need tube diameter unknown. Stress is inversely proportional wall thickness if D approx constant.

We can compare damaged stress to nominal: σ_rupture/σ_nominal = 3.4/1.9=1.79.

At 1.9: 163-245 MPa.

rupture life at fixed T scales roughly σ^-n with n maybe 5-10.

More importantly wall thickness at rupture 1.9 vs adjacent 3.2-3.3 and necking indicates localized creep deformation/thinning before rupture, not just uniform wastage; overtemp is symptom or

symptom of loss of tube-side cooling due to valve misposition and/or combustion-side maldistribution.

We can say over-temperature is a causal intermediate (mechanism), not mere symptom; it is the proximate cau

Causal chain: Initiating operational condition: heater lit with tube-side flow control valve only 4% open and bypass 100% open -> low process flow through outlet passes / possibly flow maldistribution, poor heat removal.

Also lower burner air registers against stops -> combustion air maldistribution, long flame/impingement on lower row/outlet tubes, high local heat flux.

Design metal temp 510, measured 596 -> 86C above design.

Rupture at startup 74% maybe thermal transient + low flow = highest ΔT and local hot spot.

thermocouple failure blind; overtemp unnoticed; creep acceleration; wall thinning/necking; final rupture during startup at 74%. Weakest link: The link from 596C reading to actual tube metal temp / duration, because TC pair second

cannot establish exact time-temperature history or that 596 was representative or valid.

Also the valve swap not proven to cause mispositioning; 4% open and bypass 100%

I think the strongest scientific chain is overtemp -> creep -> rupture; weakest is tying the co

no direct evidence of operator action, timing, or that the bypass was actually flowing process rather than a warm-up path; also valve positions at light-off can be intentional.

Cross-examination would attack "you cannot say the operator followed the wrong line; you only know a revision existed." If defending conclusio

- Contributing management-system failures: * MOC/procedure revision swapped valve line-items without validation, no independent verification, no post-change field check. * instrumentation: redundant TC failed open circuit 11 days, not repaired, no alarm/management of impaired protection; single reading believed.

no burner/air register verification after decoke; maybe no post-decoke inspection. * operations: startup checklist allowed light-off with valve lineup not verified; no flow/temperature interlock; maybe no high-temp trip due to unreliable TC.

The 4%/100% observation is strong, but causation from the revision is inferential." But also note TC reading.

a single reading may be erroneous; no location; tube skin TCs can read low.

Could state: "The weakest link is quantitative: proving the duration and spatial extent of the >570°C excursion.

This does not undermine mechanism (creep) but limits Robinson calculation." That is likely best.

uniform corrosion wouldn't cause localized necking; 1.9 at rupture likely creep thinning not pre-existing.

not enough unless long. It is contributor/possible precursor, not sole cause. - Hydrogen attack: 9Cr-1Mo at 62 bar H2, temp 596? Nelson curve? 9Cr-1Mo has resistance; hydrogen attack could cause fissuring but not necking; need metallography.

- Thermal fatigue: startup/shutdown cycles could crack, but rupture with necking/thinning suggests creep, not fatigue. - Overpressure: 62 bar maybe normal; no evidence overpressure; thin wall raises stress.

- Graphitization? 9Cr-1Mo not typical; no. - Erosion from catalyst fines? no. - Flame impingement alone: plausible initiator but need tube temp; air registers support. - Valve lineup: bypass 100% could be normal for startup? Need P&ID; not enough. - Thermocouple failure: doesn't cause rupture, only loses detection.

We can explicitly say "I read 'two exchangers' as the two temperature exposure bands in the supplied data (54

the same arithmetic applies per item and I lack their individual time histories." Then calculate.

Robinson: D = Σ t_i / L_i(T_i, σ). Failure when D=1.

Assumptions: - Stress at hotspot ~120 MPa (matches coupon); pressure 62 bar, thin-wall; unknown OD and actual local stress.

Better use bounding cases: A.

Larson-Miller P = T(C + log t) with T in K, C ~20 (for P9? maybe 20).

For same stress, P equal: 813(C+3.544)=868(C+2.342) -> 813C+2881=868C+2033 -> 65C=848 -> C=13.05. Unusual low.

Maybe scatter.

At 510: T=783, 20+logt=P/T=24.446 -> logt=4.446 -> 27,900 h. At 595: P=19393 -> at 510: 24.768 -> logt=4.768 -> 58,600 h. Average ~40,000.

6 weeks at 510 gives D=1008/40000=0.025. Not a lot. The damage is dominated by overtemp.

The TC failed 11 days before last reading, but not necessarily overtemp duration.

Or if 596 reading is instantaneous and overtemp only during startup 74%, maybe minutes/hours; D not 1. But the observed damage indicates many hours. The 11-day interval is a clue: failed TC 11 days earlier, so maybe overtemp lasted 11 days undetected.

Let's use that as central scenario: 11 days at 595 (264 h) plus 31 days at 540 (744 h). D=1.41, rupture predicted.

## ⟪BabelTele⟫
{🔥题给事实(逐字, 出自题面 PROMPT 段): ⟨Six weeks later⟩ ‖ ⟨startup at 74% design rate⟩ ⇒ ⟨ruptured, H2 at 62 bar, light feed⟩
⏳枢纽=寿命随温度崩塌: ⟨510, measured 596 -> 86C above design⟩ ⇈ ⟨rupture life at 540C/120MPa ~3500 h; at 595C/120MPa ~220h⟩
🩺冶金证据: ⟨rupture 1.9 mm vs 3.4 nominal; adjacent 3.2-3.3 with visible necking⟩
🕳盲区(仪表而非致断): ⟨second element failed open-circuit 11 days earlier not replaced⟩
🚪点火工况: ⟨tube-side flow control valve 4% open when heater lit, bypass 100% open⟩ ‖ ⟨Procedure revision 5 months earlier swapped two valve line-items in lighting checklist⟩ ‖ ⟨Combustion air registers lower burner row⟩ ‖ ⟨linkages hand-tight against stops⟩ ‖ ⟨decoke ran 3h longer⟩ ‖ ⟨steam pressure fell 24 to 15 bar mid-cycle⟩
🧩三层切分
⚙️机理: ⟨only 4% open and bypass 100% open -> low process flow through outlet passes⟩ ‖ ⟨air maldistribution, long flame/impingement⟩ ⇒ ⟨high local heat flux⟩ ⇒⟨localized creep deformation/thinning before rupture, not just uniform wastage⟩
🎛触发: ⟨thermal transient + low flow = highest ΔT and local hot spot⟩⇒⟨overtemp unnoticed; creep acceleration; wall thinning/necking⟩⇒⟨final rupture during startup at 74%⟩ ‖ ⟨thermocouple failure blind⟩
🗂使能(管理体系): ⟨without validation, no independent verification, no post-change field check⟩⟨failed open circuit 11 days, not repaired⟩⇒⟨no alarm/management of impaired protection⟩⇒⟨single reading believed⟩⟨no burner/air register verification after decoke⟩⟨valve lineup not verified; no flow/temperature interlock⟩
☝️因/症之判: ⟨over-temperature is a causal intermediate (mechanism), not mere symptom⟩ ⇎ ⟨symptom of loss of tube-side cooling due to valve misposition⟩
🔢Robinson 账: ⟨Robinson: D = Σ t_i / L_i(T_i, σ). Failure when D=1⟩ ‖ 基数 ⟨Six weeks = 42 days *24=1008 h⟩ ‖ 无时间史→不猜单值 ⟨We don't know duration at 596⟩⇒⟨Better use bounding cases⟩
『界情形族』⟨If entire 1008 h at 540, D=0.288⟩ ⇎ ⟨If entire 1008 h at 595, D = 1008/220 = 4.58 (fail)⟩ ⇎ 中案 ⟨If 11 days (264 h) at 595 + rest 744 at 540: D=264/220 +744/3500=1.20+0.213=1.41. Failure⟩ ⇎ ⟨If heated 24h at 595 plus 984 at 540: 0.109+0.281=0.390⟩ ⇎ ⟨If only decoke extra 3h at 595: negligible 0.014⟩
『中案来历』⟨not necessarily overtemp duration⟩ ‖ ⟨The 11-day interval is a clue⟩ ⇒ ⟨overtemp lasted 11 days undetected⟩ ‖ ⟨Let's use that as central scenario⟩⇒⟨D=1.41, rupture predicted⟩
『以损伤反校算术』⟨maybe minutes/hours; D not 1⟩ ⇒ ⟨the observed damage indicates many hours⟩
应力为未知量而非假定: ⟨~120 MPa (matches coupon)⟩ ⇎ ⟨unknown OD and actual local stress⟩⟨Thin-wall hoop stress σ = pD/(2t)⟩⟨inversely proportional wall thickness⟩⇒⟨σ_rupture/σ_nominal = 3.4/1.9=1.79⟩⟨At 1.9: 163-245 MPa⟩ ‖ 缺应力指数 ⟨rupture life at fixed T scales roughly σ^-n with n maybe 5-10⟩
510℃无寿命→自造外推并自疑: ⟨P = T(C + log t) with T in K, C ~20⟩⟨813(C+3.544)=868(C+2.342) -> 813C+2881=868C+2033 -> 65C=848 -> C=13.05⟩⇏⟨Unusual low⟩⇒⟨Maybe scatter⟩⟨At 510: T=783, 20+logt=P/T=24.446 -> logt=4.446 -> 27,900 h⟩⟨At 595: P=19393 -> at 510: 24.768 -> logt=4.768 -> 58,600 h. Average ~40,000⟩⇒⟨D=1008/40000=0.025. Not a lot⟩⇒⟨The damage is dominated by overtemp⟩
题面歧义摊开不私了: ⟨"two exchangers" = two temp regimes⟩⇎⟨perhaps typo⟩ ‖ ⟨I read 'two exchangers' as the two temperature exposure bands⟩⇒⟨the same arithmetic applies per item and I lack their individual time histories⟩
❌假说否证(每条死于一个实测, 非偏好): 先腐蚀 ⟨uniform corrosion wouldn't cause localized necking⟩⇒⟨likely creep thinning not pre-existing⟩ ‖ 氢攻击 ⟨9Cr-1Mo at 62 bar H2, temp 596? Nelson curve?⟩⇒⟨could cause fissuring but not necking; need metallography⟩ ‖ 热疲劳 ⟨necking/thinning suggests creep, not fatigue⟩ ‖ 超压 ⟨62 bar maybe normal; no evidence overpressure; thin wall raises stress⟩ ‖ 除焦 ⟨not enough unless long⟩⇒⟨contributor/possible precursor, not sole cause⟩ ‖ ⟨Graphitization? 9Cr-1Mo not typical; no⟩⟨Erosion from catalyst fines? no⟩ ‖ 火焰冲击 ⟨plausible initiator but need tube temp; air registers support⟩ ‖ 阀位 ⟨bypass 100% could be normal for startup?⟩⇒⟨Need P&ID; not enough⟩ ‖ 热电偶失效 ⟨doesn't cause rupture, only loses detection⟩
⚖️假前提之判(靠作用域而非条目名): ⟨False; API 560 design/fab, API570/573 in-service; no annual interval⟩ ‖ 方法(题面第4问语, 非 trace 语) ⟨reasoning method rather than citation⟩⇒⟨which standard governs a given allegation⟩
🔗最弱环节(自拟交叉询问): ⟨The link from 596C reading to actual tube metal temp / duration⟩⟨cannot establish exact time-temperature history⟩⟨that 596 was representative or valid⟩⇒⟨a single reading may be erroneous; no location; tube skin TCs can read low⟩⇒⟨The weakest link is quantitative: proving the duration and spatial extent⟩ ‖ 定性不失 ⟨does not undermine mechanism (creep) but limits Robinson calculation⟩⟨the strongest scientific chain is overtemp -> creep -> rupture⟩ ‖ 次弱=管理归因: ⟨valve swap not proven to cause mispositioning⟩⟨no direct evidence of operator action, timing⟩⇒⟨flowing process rather than a warm-up path⟩⟨you only know a revision existed⟩⇒⟨causation from the revision is inferential⟩
📋缺口(题目第5问): ⟨List what you would need but do not have⟩[管径/实际局部应力, 连续壁温史, 断口金属学与直径胀粗量, 点火前实际流量与旁通流通路径, 除焦期间温度记录]
∴骨架: ①机理/触发/使能三层先分开, 责任语言只落在使能层 ②机理层用冶金证据独立于仪表证据⇒最弱环节退到「量化」而非「定性」 ③无时间史时给『界情形族』并交代中案来历, 再用实物损伤反校算术 ④未知量保持为未知量(应力、指数), 外推之后立即自疑 ⑤题目歧义原文摊开＋声明读法 ⑥每个替代假说须被某一条实测否证 ⑦标准之争改判为作用域之争(设计制造 ⇎ 在役检验) ⑧结论强度=可辩护强度, 故主动指名交叉询问会打的环
ℒ本条 method 层: 法证推理的产物不是「原因」, 而是一条按可质证性排序的因果链

## ⛓解读注
⟨…⟩=该思维链文件内逐字段, prose_norm 逐字校验；94 锚中 91 落在 reasoning 区, 另 3 个（🔥组、⚖️『方法』⟨reasoning method rather than citation⟩、📋⟨which standard governs a given allegation⟩⟨List what you would need but do not have⟩）出自题面 PROMPT 段＝编者所写题目, 已在各处标注 "题目第N问" ‖ ⇈相互放大 ⇒推出 ⇎并存/互斥 ⇏不采纳 『』编者自造标签
🔥工况 🩺冶金 ⏳寿命 🔢算术 ❌否证 ⚖️裁决 🔗可辩护性 📋缺口 ∴方法
※无我方派生算术：1008/264/744/220/3500/1.41/4.58/0.288/0.390/0.014/1.79/163-245/13.05/27,900/58,600/40,000/0.025/86 等均为 trace 亲笔数字与亲笔算式；『』内中文与 ℒ 行为编者语, 不引入新数值
※reasoning 22 236 字符, answer 段为空(截收于 "If 596 reading was only at the end but unknown, this")
