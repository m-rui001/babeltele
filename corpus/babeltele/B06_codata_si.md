# B06 — 物理底座：SI 定义常数 + 关键实测常数（2022 CODATA 全表）
src: corpus/raw/codata_table.html → physics.nist.gov/cuu/Constants/Table/allascii.txt (2022 CODATA adjustment)
dir: corpus/babeltele/B06_codata_si.md

## [[原始语料|ORIGINAL]]
The 2022 CODATA adjustment lists the constants that define the SI system and the ones still measured. Exact (defined, zero uncertainty): the speed of light in vacuum c = 299 792 458 m s^-1; the Planck constant h = 6.626 070 15e-34 J Hz^-1; the elementary charge e = 1.602 176 634e-19 C; the Boltzmann constant k = 1.380 649e-23 J K^-1; the Avogadro constant N_A = 6.022 140 76e23 mol^-1; the hyperfine transition frequency of Cs-133 Δν_Cs = 9 192 631 770 Hz; and the luminous efficacy K_cd = 683 lm W^-1. Derived exact values include the molar gas constant R = 8.314 462 618... J mol^-1 K^-1, the Faraday constant F = 96 485.332 12... C mol^-1, the Stefan-Boltzmann constant σ = 5.670 374 419...e-8 W m^-2 K^-4, and the Loschmidt constant at 273.15 K and 100 kPa, 2.651 645 804...e25 m^-3. Still measured, with relative uncertainty: the Newtonian gravitational constant G = 6.674 30e-11 m^3 kg^-1 s^-2 (0.000 15e-11, i.e. ~2.2e-5 relative — the least precisely known); the fine-structure constant α = 7.297 352 5643e-3 (0.000 000 0011e-3), inverse 137.035 999 177(21); the Rydberg constant R_∞ = 10 973 731.568 157 m^-1 (0.000 012); the proton-electron mass ratio 1836.152 673 426(32); the electron mass 9.109 383 7139e-31 kg (0.000 000 0028e-31); the Bohr radius 5.291 772 105 44e-11 m; and the alpha particle-electron mass ratio 7294.299 541 71(17). Because the seven defining constants are exact by definition, every unit of measurement humans use is now anchored to invariant quantum and relativistic frequencies rather than artifacts.

## ⟪BabelTele⟫
{SI基座: 7定义常数=exact ∧ ¬ artifacts}
c 299792458 m s⁻¹ ‖ h 6.62607015e⁻³⁴ J Hz⁻¹ ‖ e 1.602176634e⁻¹⁹ C ‖ k 1.380649e⁻²³ J K⁻¹
‖ N_A 6.02214076e²³ mol⁻¹ ‖ Δν_Cs 9192631770 Hz ‖ 发光效能 683 lm W⁻¹ ⇒ 7/7 exact, 相对不确定度=0
派生(exact): R 8.314462618… J mol⁻¹K⁻¹ ‖ F 96485.33212… C mol⁻¹ ‖ σ 5.670374419…e⁻⁸ W m⁻²K⁻⁴ ‖ L₀ 2.651645804…e²⁵ m⁻³ @(273.15K,100kPa) ‖ ħ 1.054571817…e⁻³⁴ J s
实测(带不确定度 u_rel): α 7.2973525643(11)e⁻³ ⇔ α⁻¹ 137.035999177(21) ‖ R∞ 10973731.568157(12) m⁻¹
 m_e 9.1093837139(28)e⁻³¹ kg ‖ a₀ 5.29177210544(82)e⁻¹¹ m ‖ m_p/m_e 1836.152673426(32) ‖ m_α/m_e 7294.29954171(17)
 G 6.67430(15)e⁻¹¹ m³kg⁻¹s⁻² → u_rel≈2.2e⁻⁵ ⇒ 最弱环节: 引力¬量子化测准
∴ 单位制↔不变频率/量子数 ⟹ 任何模型↔模型传输可省略"度量约定"协商成本
⌚人类世界公地=此7元; 压缩时 ¬可丢 (exact 值逐位保真, 舍入即失真)

## ⛓解読注
(11)=末尾两位标准不确定度, 如 7.2973525643(11) ⇒ u=1.1e⁻¹³ ‖ ⁻¹=负一次幂 ‖ L₀=Loschmidt ‖ u_rel=相对不确定度 ‖ ⇔=等价于 ‖ ¬=非
※ 保真约束: 数字逐位照抄 raw 表; … = 源表本身以 "..." 省略尾位(未自行补全); 不确定度(11)等为源表括号位数。
