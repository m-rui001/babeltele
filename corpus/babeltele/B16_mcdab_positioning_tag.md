# B16 — 隐性工程推理：把细菌分区系统改造成异源细胞器的通用定位标签（bioRxiv 2025.09.22.677801v1, Sircar/…/Goldberg 等）
src: corpus/raw/prose/biorxiv_bacterial_organelles.txt (40 pp., 80 626 chars)
dir: corpus/babeltele/B16_mcdab_positioning_tag.md

## [[原始语料|ORIGINAL]]
location of reactions is as tunable as their content.

This asymmetric distribution in the cell results in a loss of faithful inheritance across the cell population, compromising activity and constraining their applications. To solve this problem, most bacteria encode minimal, self-organizing systems comprised of a positioning ATPase from the partition protein A (ParA) family, along with a partner protein that links the ATPase to its cellular cargo (5).

Specifically, McdB binds carboxysomes and induces McdA oscillations along the nucleoid that distribute carboxysomes throughout the cell to e

The McdAB system is currently the only known minimal and self-organizing positioning system for any protein-based organelle in bacteria.

We used the recently developed inducible ‘pXpressome’ plasmid toolkit to express α- carboxysomes from the chemoautotroph Halothiobacillus neapolitanus in E. coli. The small subunit of the carbon-fixing Rubisco enzyme (CbbS) was fused to monomeric NeonGreen (mNG) for in vivo fluorescence imaging (Fig.

But upon co-expression of the McdAB system, carboxysomes were no longer aggregated at the cell poles (Fig.

Similar results were obtained when Rubisco was fused to mScarlet or mJuniper, confirming that McdAB-m

Cells were classified based on the number and location of foci: “mispositioned” (0–2 polar foci) and “positioned” (≥3 distributed foci).

We also observed that some fully assembled carboxysomes had individual diameters ranging from 80 to 500 nm - the diameter of α- carboxysomes in H. neapolitanus, the native host, ranges from 80 to 120 nm (12). By contrast, and consistent with the fluorescence data, McdAB-expressing cells displayed fully assembled, properly sized, and unclustered carboxysomes distributed across the nucleoid region of the cell volume (Fig.

invaginate at the midpoint of a larger carboxysome (Supplementary Fig.

We recently identified an N-terminal peptide of McdB that is necessary and sufficient for McdA interaction (13). Here, we sought to develop this McdB peptide into a minimal autonomous positioning tag or “MapTag”.

20-45 nm) and simpler protein-based nanocompartments found in bacteria and archaea (14).

No native positioning system has been identified for encapsulins so far.

Nevertheless, encapsulins have never been visualized in live cells.

A degron tag (DT) (15) was also fused to mNG to promote degradation o

Reducing McdA levels caused distributed encapsulins to revert to polar clusters, confirming that positioning requires sustained McdA activity (Fig. 2I-J; Video S4). Conversely, adding McdA to cells with pre-aggregated enca

Expressing β-MapTagged-encapsulins alongside S. elongatus McdA, also resulted in encapsulins being distributed across the E.

Intriguingly, co-expression with McdB abolished this association.

McdA release from the nucleoid. To reduce these spurious interactions away from the condensate cargo, we fused McdB to the PopTag (19), which enhanced McdB sequestration into condensates (Supplementary Fig.

Our cryo-ET analysis revealed that the addition of tags and the repositioning system does not change the material properties of the condensate.

The first 20 N-terminal amino acids of β-McdB fused to mCherryPopTag did not yield any condensates (Supplementary Fig. 4A-B). However, addition of the adjacent coiled-coil dimerization domain of β-McdB provided additional valency that restored condensate assembly (Supplementary Fig.

When swapping the β-MapTag with the α-MapTag, co-expression with its cognate McdA resulted in condensate dissolution over the nucleoid (Supplementary Fig. 4G-I), suggesting the α-MapTag may be more suitable for positioning condensates with lower saturation concentrations.

Ferrosomes are membrane-bound compartments for iron storage that require the membrane protein FezA and the P1B6-ATPase transporter FezB for their formation (20).

Upon co-expression of McdA, multiple ferrosome foci were observed over the nucleoid (Fig.

Finally, we observed that using the β-MapTag to FezB was just as effective in distributing ferrosomes as the α- MapTag (Supplementary Fig.

These results suggest that spatial misregulation may be a universal bottleneck for heterologous organelle engineering, and that positioning systems provide a general solution.

Second, because McdAB activity is reversible, spatial organization can be toggled on or off, allowing for time-dependent control of metabolism or stress responses.

Our results demonstrate that a minimal gradient-based system is sufficient to transform self-assembling but static compartments into dynamic, heritable organelles.

The small subunit of Rubisco (CbbS) is fused to mNeonGreen (mNG); protein expression is induced with 0.2% arabinose (ara).

The 13.7 kb amplicon was treated with DpnI (3

Carboxysome expression experiments in E. coli Top10 were performed in LB medium, while protein induction experiments in E.

0.2% casamino acids, 10 μg/mL thiamine, and 25 μg/mL uracil (22).

coli MG1655 ΔlacY cells were transformed with plasmid pSMK1 to express encapsulinα-MapTag.

coli Sample vitrification: Bacterial samples were first concentrated to an OD600 of ~40 by centrifugation at 500 × g for 5 min.

Finally, all lamellae were polished to a final thickness of ~200 nm with a beam current of 50 pA.

pixel size of 2.654 Å, with 9 frames per tilt.

3° tilt increment from -60 ° to +60°, starting from a + 6° pretilt.

When applicable, P- values and statistical significance were evaluated using Kolmogorov-Smirnov (for distributions with

## ⟪BabelTele⟫
🦠只在造出来时才现形: 异源区室撞拟核⇒极区聚团⇒⟨loss of faithful inheritance⟩[继承失效非产量失效]
🧬下注: 细菌已用极简自组织模块解决: ⟨positioning ATPase from the partition protein A (ParA) family⟩∧[适配蛋白] ‖ 选定 McdAB: ⟨induces McdA oscillations along the nucleoid⟩⇒⟨distribute carboxysomes⟩ ‖ 外推前提=唯一性: ⟨only known minimal and self-organizing positioning⟩
🧪靶1 α-羧体: ⟨‘pXpressome’ plasmid toolkit⟩ ‖ ⟨Halothiobacillus neapolitanus in E. coli⟩ ‖ 读出把手 ⟨Rubisco enzyme (CbbS) was fused to monomeric⟩ ‖ ⟨no longer aggregated at the cell poles⟩ ‖ 计分 ⟨mispositioned (0–2 polar foci)⟩‖⟨positioned (≥ 3⟩ ‖ 排除荧光伪影: ⟨fused to mScarlet or mJuniper⟩
🔍荧光⇏装配正确⇒冷冻电镜: 无模块粒径 ⟨80 to 500 nm⟩ ⇎ 天然宿主粒径 ⟨80 to 120 nm⟩⇒派生 4.17×(过大) ‖ 有模块 ⟨fully assembled, properly sized⟩∧⟨unclustered⟩ ‖ 意外: ⟨invaginate at the midpoint⟩⇒[定位与尺寸控制耦合非独立]
🏷️抽象动作(最可迁移): ⟨N-terminal peptide of McdB⟩∧⟨necessary and sufficient for McdA⟩⇒任意货物成 ⟨autonomous positioning tag⟩[MapTag]
🧪靶2 蛋白壳(无定位系统): ⟨No native positioning system⟩ ‖ 活细胞可视化空白 ⟨visualized in live cells⟩ ‖ 只见装配体: 降解子 ⟨fused to mNG⟩ ‖ 双向可切: 撤引擎⇒⟨revert to polar clusters⟩⇒⟨positioning requires⟩[持续供给] ‖ 加引擎⇒⟨adding McdA to cells⟩[已聚团重排] ‖ 正交同源对亦成立: ⟨β-MapTagged-encapsulins alongside S. elongatus McdA⟩
⚠️靶3 凝聚体=最有信息量的失败: 全长 McdB 反噬⇒⟨co-expression with McdB abolished⟩⇒假设 ⟨McdA release from the nucleoid⟩[全局抽走梯度非局部定位] ‖ 解法 ⟨fused McdB to the PopTag⟩[膜/相亲和↑] ‖ 极简标签初败: ⟨mCherryPopTag did not yield any condensates⟩ ‖ 修复靠价态: ⟨coiled-coil dimerization domain of β-McdB⟩
📐两条配对律(非教科书): ①标签与引擎须同源, 否则不定位而溶解: ⟨cognate McdA resulted in condensate dissolution⟩⟨lower saturation concentrations⟩ ②⟨does not change the material properties⟩[相态与位置正交]
🧪靶4 膜结合区室: ⟨the membrane protein FezA⟩∧⟨the P1B6-ATPase transporter FezB⟩ ‖ ⟨multiple ferrosome foci⟩ ‖ ⟨just as effective⟩[β≈α]『跨蛋白壳/凝聚体/脂膜三类边界』
🎯设计主张: ⟨location of reactions is as tunable as⟩[内容与位置同权] ‖ 普适性只作假设: ⟨universal bottleneck for heterologous organelle engineering⟩ ‖ 可逆 ⟨can be toggled on or off⟩ ‖ 继承自下而上: ⟨minimal gradient-based system is sufficient⟩[随机分配→可遗传]
∴骨架: ①先找"自然已解决同类问题"的极简模块并写下唯一性前提 ②读出把手与标签解耦(换荧光蛋白复验) ③证据分层: 荧光统计⇒金标准结构(冷冻断层)才谈装配保真 ④拆成"可移植标签+引擎", 用必要充分实验界定可移植边界 ⑤失败是数据: 全长适配蛋白抽走梯度⇒最小肽+价态修补 ⑥配对律用反例确立(错配→溶解) ⑦通用性以假设语气给出, 只声明可切换性
📮实现细节锚点: ⟨0.2% arabinose⟩ ⟨13.7 kb amplicon⟩ ⟨Kolmogorov-Smirnov⟩ ⟨final thickness of ~200⟩ ⟨pixel size of 2.654⟩ ⟨3° tilt increment from -60⟩ ⟨E. coli Top10⟩ ⟨MG1655 ΔlacY⟩ ⟨10 μg/mL thiamine⟩ ⟨25 μg/mL uracil⟩ ⟨0.2% casamino acids⟩ ⟨OD600 of ~40⟩ ⟨(20-45 nm)⟩

## ⛓解读注
⟨…⟩=raw 逐字段(audit.py prose_norm 逐字校验) ‖ ⇎对照 ∥并列 ⇒推出 ∧且 ≈约 ⚠失败但有信息量 🎯结论 📮方法锚点
※派生算术: 4.17=round(500/120,2)。其余数字(80/500/120/20-45/0.2/13.7/2.654/200/40/3/2/β)全部为源内原值; 统计检验名为源内 Kolmogorov-Smirnov。
※隐性点=未发表的设计律与失败构建体(预印本 2025-09-22, 训练集外)。
