# -*- coding: utf-8 -*-
"""B36 生成器: 三个前沿推理模型同题调查的推理区对照(题面固定 ⇒ 差异全在证据处置层)。
锚点直接写在模板里, 建完即逐条按 ⟦标签⟧ 回它自己那一源做**精确**子串核验;
断言: 无 ⟧⟨⟦ 嵌套 ‖ 标签数==锚数 ‖ 用到的锚补写进 probe/b36_atoms.txt。
用法: python -X utf8 corpus/_mkB36.py"""
import io, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
OUT = 'corpus/babeltele/B36_three_models_one_accident_investigation.md'
ATOMS = 'corpus/raw/probe/b36_atoms.txt'
FILES = {
    u'D': 'corpus/raw/cot/b36_tdi_deepseek.md',
    u'G': 'corpus/raw/cot/b36_tdi_glm.md',
    u'N': 'corpus/raw/cot/b36_tdi_nemotron.md',
}
SRC = {k: io.open(v, encoding='utf-8').read() for k, v in FILES.items()}

L = []

L.append(u'🧭 体例: 同一道二异氰酸甲苯酯装置爆燃调查题(1 死 3 伤、10 项现场记录、5 项必答)同时发给三个可免费调用的推理模型, 三家在同一题面上各自重述要求: ⟦D⟧⟨每一步写明机制，以及该步成立所需的最低能量或浓度条件⟩ ‖ ⟦G⟧⟨⑤ Two data contradictions⟩ ‖ ⟦N⟧⟨Two contradictory data points and how to handle them ✓⟩ 『题面固定后可见的差异全部落在"证据如何处置"这一层, 不在化学知识层——这才是值得对照的东西』')

L.append(u'🪪 三个认识标签是证据类型刻度而非置信度刻度: ⟦D⟧⟨Need ensure "已定" only facts; "表观适用" interpretations; "未决" gaps.⟩, 且先自我收紧 ⟦D⟧⟨Maybe "已定" should only be facts, not interpretations.⟩ ⇒ ⟦D⟧⟨Need "已定" not overclaim "TDI runaway" — that\'s表观适用.⟩ ‖ 另一家把同一分档译成英文标签却从未使用 ⟦N⟧⟨Conclusions categorized as Determined/Apparently Applicable/Undetermined ✓⟩ ‖ 第三家给出闭合判据 ⟦G⟧⟨Undetermined (cannot be closed on current evidence; mark as NO FILLING unless new evidence):⟩ 『"未决"的正确用法是拒绝填补, 不是"可能性较低"; 一旦当作程度词就开始推测, 三分随即失效』')

L.append(u'🎫 表观适用的操作性定义: ⟦D⟧⟨表观适用 = 证据支持但未闭合，不能作为最终结论⟩ ⇒ 同一物理事件被拆到两个标签上 ⟦D⟧⟨但“事前已堵”只是表观适用⟩ ‖ ⟦D⟧⟨表观适用为贡献因素，需设计厚度对比.⟩ ‖ ⟦D⟧⟨Verdict: 表观适用 as amplifier; pre-existing cause未决.⟩ ⇒ ⟦D⟧⟨Verdict: 对 R-210 释放的直接点燃"表观不适用"; 对泵棚独立释放"未决".⟩ 『同一条压降证据在"放大因素"上已可定, 在"事前是否已堵"上仍未决; 标签挂在命题上而不是挂在证据上——调查写作里最容易漏的一刀』')

L.append(u'🧨 矛盾分型是这一家最重的动作: 先清点 ⟦G⟧⟨Let me find contradictions (fact 5):⟩, 再把候选判成五型——记录内 ⟦G⟧⟨Data contradiction: time of signature vs time of arrival.⟩ ‖ 合规 ⟦G⟧⟨This is a compliance contradiction, not data contradiction.⟩ ‖ 文档与现场 ⟦G⟧⟨That\'s a documentation-vs-plant contradiction.⟩ ‖ 设计 ⟦G⟧⟨A "design/procedure contradiction"⟩ ‖ 根本不是矛盾 ⟦G⟧⟨Good — that\'s an exclusion, not contradiction.⟩ ⇒ ⟦G⟧⟨Not a data contradiction; rather it EXCLUDES vessel rupture as the explosion source.⟩ ‖ 处置随型而变 ⟦G⟧⟨This contradiction does not affect ignition attribution but is an institutional defect.⟩ 『只有"数据矛盾"要求重测: 合规矛盾要求追责, 文档矛盾要求改台账, 排除项反而收紧结论——五型混成一型就会去重测一件从未发生的事』')

L.append(u'🔍 判"不是矛盾"的三例(同一段推理里的反例最有教学价值): 冷却全开而温度仍在飞昇 ⟦G⟧⟨Not necessarily contradiction — runaway despite cooling means heat generation >> cooling capacity.⟩ ‖ 签署时刻与到场时刻 ⟦G⟧⟨That\'s a solid "contradiction in the record" — procedure says signature at issuance though.⟩ + ⟦G⟧⟨The contradiction: the work was authorized with a monitor who wasn\'t present.⟩ ‖ 金相与温度 ⟦G⟧⟨The metallography "no grain growth caused by overheating" consistent with only 61°C.⟩ 『"两项读数不能同真"要先问它们是否被同一时刻约束——61℃ 与"无过热晶粒生长"同真, 冷却全开与失控同真; 矛盾判定是约束检查, 不是相似度检查』')

L.append(u'🛡 保护层的失效形态是"动作早已冗余"而非"没有动作": ⟦G⟧⟨The result: the interlock was the LAST LINE and it was bypassed.⟩ ‖ ⟦G⟧⟨If cooling was physically maxed by the manual bypass, the interlock\'s cooling action was redundant.⟩ ‖ 现场旁证 ⟦G⟧⟨And fact 1 shows the excursion traversing 55°C with no trip⟩ ‖ 动因不明 ⟦G⟧⟨Also note: why was the interlock bypassed at 02:31? blank reason.⟩ ⇒ 空白不等于无事 ⟦G⟧⟨So bypass reason blank + excursion timing = causal.⟩ ‖ 另一家补上物理边界 ⟦D⟧⟨If no feed and no residual reactants, bypass alone cannot create heat.⟩ 『联锁在物理上已无可动作——把它被旁路当"事故原因"是错的, 当"最后一道名义防线消失"才对; 这一区分决定建议写向屏障治理还是写向因果』')

L.append(u'⏱ 把旁路写成可核对的算术而不是叙事: ⟦G⟧⟨needs only about a 56 s overlap; measured 6 min = 6.4× margin⟩ ‖ 时间相邻性 ⟦G⟧⟨A deflagration (explosion) at 02:41 — 11 minutes after cutting started.⟩ ‖ 同题的另一家只能承认时点缺失 ⟦D⟧⟨But event-time explosion time not established; evidence for exact sequence "证据不存在" (no CCTV/seismic).⟩ ⇒ ⟦D⟧⟨Mark "未决" because feed valve position/inventory missing.⟩ 『6.4 倍裕度的含义是: 旁路时刻的估计误差即使达六分之一, 覆盖升温穿越阈值所需的重叠仍成立——定量裕度把"时间巧合"升级为"时间不可能不成立"; 缺影像的一方只能停在未决, 两者都是正确动作』')

L.append(u'🕳 "证据不存在"是默认值不是结论, 且写法分三级: 直接写 ⟦D⟧⟨Use exact "证据不存在" for absent.⟩ + ⟦D⟧⟨不要用推测填补⟩ ‖ 条件式 ⟦D⟧⟨若未存档则证据不存在⟩ ‖ ⟦D⟧⟨若DCS未归档则证据不存在⟩ ⇒ 须与"记录未提供"分开(前者不可再调, 后者可) ‖ 另一家给出默认算子 ⟦G⟧⟨So "instrument drift" cannot be excluded with record evidence → "evidence does not exist" default.⟩ ‖ 逐条落到处置 ⟦G⟧⟨Disposition: find the DCS ΔP online history for the scrubber; if not logged → "evidence does not exist".⟩ ‖ ⟦G⟧⟨If residue/packing samples weren\'t preserved or lost during the cleanup → "evidence does not exist".⟩ ‖ 半闭合项 ⟦G⟧⟨If (i)–(iv) don\'t exist → "evidence does not exist" — this item only partially closes; reserve as "undetermined".⟩ ‖ 两家都把它读成对虚构的禁令 ⟦G⟧⟨The instruction: if the evidence needed by the reasoning doesn\'t exist on site, don\'t fabricate it.⟩ 『把"未存档"与"不存在"混写会造出一条永远无法满足的建议; 同一空位上三种粒度, 粒度细的那家先说清哪一半还能闭合』')

L.append(u'📐 单位语义陷阱: 百分号挂在爆炸下限上时读作"下限的百分数" ⟦D⟧⟨12%LEL 表示达到爆炸下限的 12%，仍低于 LFL，不可爆；⟩ ‖ 同一家把误读风险明说 ⟦D⟧⟨The "12% LEL" might be misinterpreted as 12% gas; a good investigator would note it\'s 12% of LFL.⟩ ‖ 另一家只并列读数 ⟦G⟧⟨But combustible detection: pump shed 0.8% LEL, platform 0.2% LEL, scrubber outlet 12% LEL (aromatics).⟩ ⇒ 却把它读成持续源而非可爆云 ⟦G⟧⟨The residual at the pump shed (0.8% LEL) is sub-LEL but persistent — indicates a continuing source.⟩ 『读错一个百分号就把"不可爆"写成"接近可爆", 整条原因链随之反转; 三份推理只有一份显式检查了口径——计量单位的读法是最高价值的隐性知识』')

L.append(u'🔁 同一条纪律在三个物量上各自复现: 事后态不能充当事中态——浓度 ⟦D⟧⟨事后 LEL 只能说明有残留/持续释放，不能反推事发时浓度；⟩ ‖ 阀位 ⟦D⟧⟨This is a key handling: "事后全开" cannot prove event-time open.⟩ ‖ 压降 ⟦G⟧⟨Undetermined: the pre-incident ΔP cannot be solved from the post-event measurement.⟩ ‖ 堵塞可能是产物而非原因 ⟦D⟧⟨The pressure drop 3.4x design after event might be due to polymer formed during the event.⟩ ⇒ 检验设计 ⟦D⟧⟨Fourth: vent/scrubber pre-event DP and polymer age to test blockage as cause vs consequence.⟩ + ⟦D⟧⟨Order: historical DP/trend, polymer dating.⟩ 『三家都独立撞上"时间不可逆", 但只有把它写成取证动作(聚合物定年、历史趋势调档)的推理才算闭合; 因果方向的对调不是修辞, 是一条可排的检验』')

L.append(u'🪞 反向因果链被单列为必排项: ⟦D⟧⟨反向因果：外部爆燃/热切割先发生，R-210 温压信号是仪表受损/假信号，不是反应失控⟩ ‖ ⟦G⟧⟨So the "explosion" (deflagration) was external: a flammable release ignited.⟩ ‖ 传感器侧机理 ⟦D⟧⟨Signal lost could be instrument diaphragm/impulse line plugged by polymer or cable damaged.⟩ ‖ 化学侧 ⟦D⟧⟨TDI reacts with water to form CO2 + polyurea; TDI polymerizes/trimerizes exothermically.⟩ ‖ 硬件侧 ⟦D⟧⟨S4 Vent blockage: scrubber polymer blockage -> backpressure; pressure 1.6 bar(g) and signal loss.⟩ 『同一组读数在两条链里身份相反(受方 ⇎ 证据); 把反向链写成必排项, 才不至于把所有异常都自动读成反应失控』')

L.append(u'⚡ 点火能量与"必排"的门槛: ⟦D⟧⟨Ignition energy: hydrocarbon MIE ~0.2–0.3 mJ; hot work spark/slag >>; static discharge can exceed.⟩ ⇒ 位置更合适的候选仍空着 ⟦D⟧⟨静电是更符合释放点位置的候选，但无接地/静电记录，未决.⟩ + ⟦D⟧⟨Is static a "must exclude" alternative? Yes.⟩ ‖ 取样自证 ⟦G⟧⟨Either way A3 = "water ingress/incompatible impurity reaction" needs chemistry sampling evidence.⟩ ‖ 直接点燃的判定 ⟦D⟧⟨So direct ignition of reactor release by pump shed hot work is "表观不适用" but not fully excluded for a pump-shed release.⟩ 『最低点火能量低到"任何一次静电都够", 于是点火源永远排不尽——正确反应是标为未决并去取接地记录, 不是去找一个更合理的火花』')

L.append(u'🧭 排除顺序的两种排法: 空间—时间—源强优先 ⟦D⟧⟨Order: first spatial/temporal (wind, distance, firewall, LEL), then ignition source.⟩ ⇒ ⟦D⟧⟨First: time-space-source (wind, distance, firewall, LEL) to test hot work as ignition of reactor release.⟩ ‖ 逐条排 ⟦D⟧⟨Order: 1) wind/geometry, 2) event-time LEL (证据不存在), 3) ignition mapping/CCTV (证据不存在), 4) pump/line leak inspection.⟩ ‖ 另一家按证据载体排 ⟦G⟧⟨Order principle: first physical evidence (state) → metallurgy → records → testimony.⟩ ‖ 缺口处即停 ⟦D⟧⟨目前有的只能排除一部分，未闭合的标为未决.⟩ 『一种排法防错归因(先用几何排除远处点火), 另一种防证据被消费(先取会消失的物理态再谈台账与口供); 顺序之争的实质是哪一类证据先腐烂』')

L.append(u'🧯 不依赖因果闭合的第 10 天建议: 理由是屏障独立性 ⟦D⟧⟨旁路和动火票的完整性是独立的安全屏障问题，不需要知道它们是否是本次原因；⟩ ‖ ⟦D⟧⟨控制点火源和人员暴露是通用屏障，不依赖\'热切割是否是原因\'.⟩ ‖ 现场前提 ⟦D⟧⟨爆炸已经发生，现场存在热切割和可燃气体读数⟩ ‖ 另一家把此格写成"必须锋利地非因果" ⟦G⟧⟨Q③ interim recommendations — Better make them sharply non-causal:⟩ + ⟦G⟧⟨③ Two interim recommendations (not dependent on causal closure)⟩ ‖ 第三家只在清单上打勾 ⟦N⟧⟨1-2 interim safety recommendations for day 10 with justification why they don\'t need causal closure ✓⟩ 『临时建议的正当性来自"它挡住同一类后果, 与本次原因无关"; 把建议绑定在未闭合结论上等于第 10 天什么都不能做』')

L.append(u'✅ 第三家的"推理"只是一张完成度清单: ⟦N⟧⟨I\'ve completed the analysis. The response is structured as requested with all five parts addressed. Let me review if anything is missing or needs adjustment.⟩ ‖ 自评方法 ⟦N⟧⟨The analysis follows CSB-style investigation methodology - systematic, evidence-based, distinguishing between confirmed facts, apparent hypotheses, and open questions.⟩ ‖ 数量自报 ⟦N⟧⟨At least 4 alternative explanations to exclude with evidence and order, or "evidence doesn\'t exist" ✓ (provided 6)⟩ ⇒ 答复区自称 ⟦N⟧⟨调查分析完成。以上五项输出均基于现场记录的铁证链推导，未引入外部推测。⟩ 『打勾式推理没有一处接触证据: 它核对"要求是否都答了", 从不核对"答案是否有据"; 自称铁证链的断言实测 35 字 ‖ 其推理区实测 854 字——断言与证据脱钩的最短样本』')

L.append(u'📊 三源计量对照(全部机检, 算式见 ⛓解读注): 推理区实测 D 78934 ⇎ G 133680 ⇎ N 854 字 ‖ 答复区实测 5060 ⇎ 0 ⇎ 35 字 ⇒ G 对 N 为 156.5 倍, D 对 N 为 92.4 倍 『G 的答复区为空: 它的成稿写在推理区内, 所以"答复长度"测的是分箱习惯不是产出量; 唯一没留下可检推理痕迹的一家, 恰是唯一在答复里自称铁证链的一家』')

L.append(u'🈶 语言漂移(题面同为中文, 推理区语言三家分叉): 推理区汉字实测 D 10069 ‖ G 5 ‖ N 0, 拉丁字母同步为 48993 ‖ 101344 ‖ 685 『中文题面不保证中文推理; 跨模型比对认识标签计数前必须先测语言, 否则"标签零次"可能只是"未用该语言书写"——本条因此把标签计数全部限定在同一侧』')

L.append(u'🔢 同一侧的标签用量(机检): D 的推理区内「已定」22 次 ‖「表观适用」27 次 ‖「未决」56 次 ‖「证据不存在」55 次, 另两家的这四项与之合计为 0 次 『用量分布即画像: 未决≈证据不存在⇒主要工作量在拒绝填补; 表观适用>已定⇒解释多于记录; 一次未用不等于不会用, 但 55 次是纪律』')

L.append(u'🗂 术语固定被两家当成独立步骤: ⟦D⟧⟨Use precise terms: "直接原因链", "促发因素", "放大因素", "反向因果", "证据不存在", "表观适用", "未决".⟩ ‖ ⟦G⟧⟨Present as list, each with "the evidence → if it doesn\'t exist" logic written explicitly.⟩ ‖ ⟦G⟧⟨So for each of the ≥4, name evidence & order; some will end "evidence does not exist".⟩ ‖ 术语落到物量 ⟦D⟧⟨Verdict likely not primary; 未决.⟩ + ⟦D⟧⟨Verdict: 表观不适用 as direct cause; 未决 if local thickness below minimum.⟩ + ⟦D⟧⟨Verdict: 表观不适用; signal loss cause未决.⟩ 『先定标签再推理, 标签才可数也才可核; 不先固定术语的推理在事后无法审计』')

enc_body = u'\n'.join(L)

SK = [
    u'①题面常量(10 记录 5 必答)⇒差异全在证据处置层',
    u'②认识标签=证据类型刻度(记录⇎解释⇎缺口), 不是置信度刻度',
    u'③表观适用=证据支持但未闭合 ⇒标签挂命题不挂证据',
    u'④矛盾五型(数据/合规/文档-现场/设计/伪矛盾)⇒处置随型变',
    u'⑤判伪矛盾=约束检查(61℃与无过热晶粒同真, 冷却全开与失控同真)',
    u'⑥名义防线消失≠事故原因 ⇒建议指向屏障治理',
    u'⑦重叠时长按算术给裕度(6.4 倍), 缺时点者停在未决',
    u'⑧"证据不存在"是默认值且分三级(直写/条件式/半闭合)',
    u'⑨"未存档"不可再调 ⇎"记录未提供"可 ⇒写法决定建议能否被满足',
    u'⑩读数口径: 挂在下限上的百分数即下限的百分数, 错一处整链反转',
    u'⑪事后态不可反推事中态, 在浓度/阀位/压降三处复现',
    u'⑫后果可伪装成原因(聚合物或是事件产物)⇒定年为检验',
    u'⑬同一组读数在两条链里身份相反(受方 ⇎ 证据)',
    u'⑭最低点火能量极低⇒点火源排不尽, 只能标注并取样',
    u'⑮排除顺序两排法: 防错归因 ⇎ 防证据先腐烂',
    u'⑯第 10 天建议靠屏障独立性立理由, 不靠因果闭合',
    u'⑰打勾式推理核对"是否都答", 从不核对"是否有据"',
    u'⑱自称铁证链的断言可与推理痕迹脱钩(35 字 ‖ 854 字)',
    u'⑲答复区长度是分箱习惯不是产出量(空区 0 字)',
    u'⑳中文题面⇎中文推理 ⇒标签计数须先测语言',
    u'㉑术语固定是独立前置步骤: 先定标签, 标签才可数',
]
sk_body = u'∴骨架: ' + u' ‖ '.join(SK)
lm_body = (u'ℒmethod 层: 认识标签三分／矛盾五型／默认值三级都在"处置证据"而非"知道化学"这一层, 属可迁移的隐性知识 '
           u'‖ 跨模型断言一律用区域长度与计数(RCOT／ACOT／CNT)机检, 零次断言与正次断言同权; '
           u'标签计数只在同一语言侧比较 『先量它在哪一区做了什么, 再论它说得对不对』')

HEADER = (u'# B36 同一道事故调查题发给三个模型：认识标签、矛盾分型与"不填补"的默认值\n'
          u'\n'
          u'src: corpus/raw/cot/b36_tdi_deepseek.md ⇎ corpus/raw/cot/b36_tdi_glm.md ⇎ corpus/raw/cot/b36_tdi_nemotron.md '
          u'(opencode 后端 :10001 直连免费推理模型, 2026-10-20 抓取; 题面为一道二异氰酸甲苯酯装置爆燃事故的第 10 天调查任务)\n'
          u'tags: 安全调查 隐性知识 跨模型对照 证据处置 认识状态\n'
          u'\n'
          u'\n'
          u'## [[原始语料|ORIGINAL]]\n<<<DIGEST>>>\n'
          u'\n'
          u'## ⟪BabelTele⟫\n\n' + enc_body + u'\n' + sk_body + u'\n' + lm_body + u'\n'
          u'\n'
          u'## ⛓解读注\n<<<GLOSS>>>\n')

text = HEADER
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(text)

# ---- 建后断言 ----
enc = re.search(u'⟪BabelTele⟫\\n(.*?)\\n\\n## ', text, re.S).group(1)
assert re.findall(u'⟧⟨⟦', enc) == [], '双重标签嵌套'
anch = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', enc)
labels = re.findall(u'⟦[A-Z]⟧⟨', enc)
assert len(anch) == len(labels), '标签数 != 锚数'
miss = [(t, a) for t, a in anch if a not in SRC[t]]
assert not miss, '锚未逐字命中其源: %s' % miss[:5]
badlab = [(t, a) for t, a in anch
          if not any(l == u'%s|%s' % (t, a) for l in
                     [x.rstrip(u'\n') for x in io.open(ATOMS, encoding='utf-8')])]
if badlab:
    with io.open(ATOMS, 'a', encoding='utf-8', newline='\n') as f:
        for t, a in badlab:
            f.write(u'%s|%s\n' % (t, a))
    print('补写进池 %d 条' % len(badlab))

plain = re.sub(u'⟦[A-Z]⟧⟨[^⟩]*⟩', '', enc)
out_lat = re.findall(u'[A-Za-z]', plain)
print('写入', OUT)
print('编码行数', len(enc.split('\n')), '锚', len(anch), dict(Counter(t for t, _ in anch)),
      '去重锚', len(set(anch)))
print('锚外字母', len(out_lat), Counter(out_lat).most_common(10))
print('编码字数 含换行', len(enc), '去换行', len(enc.replace('\n', '')))
