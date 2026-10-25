# -*- coding: utf-8 -*-
# B33 装配: 每个锚都就地断言"逐字命中它自己那份 raw"(比 atomcheck 更强: 归属在写作时就锁死)
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

FILES = {u'U': u'corpus/raw/prose/csb_clairton_update.txt',
         u'I': u'corpus/raw/prose/csb_clairton_interim.txt',
         u'F': u'corpus/raw/prose/csb_clairton_final.txt'}
OUT = u'corpus/babeltele/B33_csb_clairton_staged_findings.md'
TITLE = (u'# B33 · 同一场爆炸的三次表态：CSB Clairton 焦炉煤气爆炸案的时间切片'
         u'（⟦U⟧⟨September 2025⟩ ⇎ ⟦I⟧⟨December 2025⟩ ⇎ ⟦F⟧⟨Published: August 2026⟩）\n')


def norm(s):
    s = s.lower()
    for a, b in ((u'’', "'"), (u'‘', "'"), (u'“', '"'), (u'”', '"'), (u'´', '')):
        s = s.replace(a, b)
    s = re.sub(u'[’\'"\u2018\u2019`´]+', u'', s)
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]+', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


N = {}
for k, p in FILES.items():
    N[k] = norm(io.open(p, encoding=u'utf-8').read())


def Q(tag, txt):
    assert norm(txt) in N[tag], u'MISS ⟦%s⟧ %s' % (tag, txt[:70])
    return u'⟦%s⟧⟨%s⟩' % (tag, txt)

L = []
A = L.append

A(u'🧭 体例: 同一事故三份文件 ⟦U⟧⟨September 2025⟩ ⇎ ⟦I⟧⟨December 2025⟩ ⇎ ⟦F⟧⟨Published: August 2026⟩, '
  u'同号 ⟦F⟧⟨No. 2025-03-I-PA⟩ 『读法不是读最终结论, 是读同一机关在证据陆续到位时怎么说三次话: '
  u'⟦U⟧ 只报事实与口径, ⟦I⟧ 在未定因果时下临时建议, ⟦F⟧ 才给 cause 与反事实; '
  u'⟦F⟧⟨2025-03-I-PA-R1 (previously issued as an interim recommendation in December 2025)⟩ '
  u'⇒ 建议台账跨文档不断号, 撤回与新增都留痕』')

A(u'🔗 规模与后果解耦: ⟦F⟧⟨approximately 19 pounds of coke oven gas⟩ ⇒ ⟦F⟧⟨fatally injured two U.S. Steel employees, '
  u'injured 11 people, five of them seriously, and caused an estimated $52.5 million in property damage⟩ '
  u'[总数 13=2+11, 轻伤 6=11-5] 『十数公斤可燃物足以定两死——风险量不按泄漏质量折算, 只按"人是否在波及面内"折算; '
  u'⟦I⟧⟨Both fatally injured U.S. Steel employees were in or near a reversing room at the time of the explosion.⟩』')

A(u'🧪 排除式取证靠"对照片元": ⟦F⟧⟨The Battery 14 isolation valve was found intact after the incident.⟩ ⇒ 同一套检测在完好阀上重跑 ‖ '
  u'⟦F⟧⟨Magnetic particle inspection did not detect any crack or failure indications⟩ ⇒ '
  u'[事前裂纹／腐蚀减薄／几何变形／材质四种备选解释逐一被负结果删掉, 只剩过压] '
  u'『没有正证据, 只有删到只剩一个的解释——对照片元是"删解释"的装置, 不是"证假设"的装置』')

A(u'⛭ 无仪器时的界限推理: ⟦F⟧⟨There were no pressure gauges or sensors attached to the valve at the time of the incident⟩ ‖ '
  u'⟦F⟧⟨mechanically capable of producing pressures significantly greater than the valve’s 50 psig design⟩ ⇒ '
  u'[不必知压力值, 只需知"能力上限超过额定值"; ⟦F⟧⟨The CSB did not correlate those mechanical settings to any specific output pressure or flowrate⟩ 仍出结论] '
  u'『额定 ⟦U⟧⟨rated for 50 pounds per square inch⟩ ÷ 许可 ⟦U⟧⟨maximum steam pressure of 10 psig⟩ = 5 倍: 界限法用的是两个已知数的比值, 不是未知数本身』')

A(u'🔒 机理只需一个必要条件: ⟦F⟧⟨Normally, with the valve gates raised, pumping water into the valve would not cause the valve to fail⟩ + '
  u'⟦F⟧⟨water had to have been pumped into the valve without an adequate path to flow out⟩ ⇒ [两道闸板落下 ⇎ 清洗口正对两闸之间 ⇒ 封闭空腔] '
  u'『从结果反推必要前提, 比还原动作序列弱一档但足够定因; ⟦F⟧⟨The CSB could not fully determine the precise sequence of actions taken by the workers during the incident.⟩ '
  u'与"原因已定"并存, 不是矛盾』')

A(u'✂️ 破坏本身开出泄漏路径: ⟦F⟧⟨there was sufficient horizontal clearance in the valve to enable the gates not to seal fully against the seats⟩ ⇒ '
  u'[阀体裂开→闸板密封失效→煤气绕过闸板经裂缝外泄] 『隔离装置的失效不是"停止隔离"而是"变成泄漏点": '
  u'关阀这一个动作在事故链里同时是清洗步骤与释放步骤, 正常态与破坏态不可线性外推』')

A(u'🕐 点火延迟的读法: ⟦U⟧⟨lower explosive limit of about 4.4 percent⟩ ‖ ⟦U⟧⟨The ovens are kept oxygen-free in order to prevent the coal from burning⟩ ‖ '
  u'⟦U⟧⟨approximately 2,000 degrees Fahrenheit⟩ vs ⟦U⟧⟨The autoignition temperature of hydrogen, the most prominent component of coke oven gas, is 1,065 °F⟩ ⇒ '
  u'炉温是氢自燃点的 2 倍(2,000÷1,065) ⇒ [不需要电火花, 热表面即点火源; "无点火源"这种抗辩自动失效] ‖ '
  u'⟦F⟧⟨Twenty-four seconds after an evacuation order was issued via radio⟩ ⇒ [二十四秒是云团从漏点长到爆炸下限的扩散时间, 不是寻找火源的时间] '
  u'⟦F⟧⟨ignited at or near the Battery 14 coke oven closest to the transfer area.⟩ 与"炉子正在烤"同址』')

A(u'🏚 布局是 severity 的唯一开关: ⟦F⟧⟨less than 20 feet directly above the coke oven gas piping system that was the source of the release⟩ + '
  u'⟦F⟧⟨None of the buildings were designed or constructed to withstand an explosion.⟩ ‖ ⟦I⟧⟨at least three rooms that were routinely occupied by people⟩ ⇒ '
  u'⟦F⟧⟨the two fatal injuries and two of the five serious injuries would have been prevented or reduced in severity⟩ '
  u'[两本账: 释放←阀, 死亡←房间位置] 『⟦I⟧⟨freed himself from the rubble, crawled out of the debris, and found help⟩ ⇎ 另一人 ⟦I⟧⟨roughly nine hours after the explosion⟩ 才寻获: '
  u'同一次爆炸的生还差别在建筑不在运气; ⟦F⟧⟨U.S. Steel affirmatively chose not to do so, based on the company’s belief that it was not required to do so⟩ '
  u'⇒ 认定是"明知而不做", 不是"没想到"』')

A(u'📋 程序缺位的三条独立证据: ⟦F⟧⟨U.S. Steel had no procedure for how to safely conduct this operation⟩ + '
  u'⟦F⟧⟨for at least three years prior to the incident, U.S. Steel employees had utilized pressurized water to clean valve seats on an ad hoc basis⟩ + '
  u'⟦U⟧⟨The procedure did not mention the use of water at all.⟩ ⇒ '
  u'[书面许可 10 psig 蒸汽 ⇎ 实操泵压远超 50 psig 水: 介质被换掉而风险评审没跟着换] '
  u'『"管理层知情且默许"把违规做法转成事实规程——规程真空不是无作为, 是让现场自己填; '
  u'⟦F⟧⟨the facility’s water washing expert⟩ 这个称号本身就是缺程序的证人』')

A(u'🗓 计划漂移与承包商缺席: ⟦U⟧⟨planned for August 19, 2025⟩ ⇎ ⟦U⟧⟨On August 11, 2025, the day of the incident, U.S. Steel decided to exercise the Battery 13 gas isolation valve⟩ ⇒ 提前 8 天(19-11) ‖ '
  u'⟦U⟧⟨MPW was not a participant in the meeting.⟩ + ⟦U⟧⟨A U.S. Steel supervisor called an MPW employee and asked MPW to provide a pump⟩ ⇒ '
  u'[危害评审只在旧会上做过, 被叫来的人不在评审里] 『临时召唤使"评审过"与"做过"失去同一批参与者; '
  u'⟦U⟧⟨planned to opportunistically replace at least three other valves⟩: 顺带扩范围把隔离操作从"必要"变成"更多次"』')

A(u'⚖️ 作用域由定义词决定, 不由装置决定: ⟦F⟧⟨coke oven gas does not qualify for the hydrocarbon fuels exemption because it does not meet the definition of⟩ ⟨hydrocarbon⟩ ‖ '
  u'⟦U⟧⟨hydrogen (40 to 60 weight percent), methane (20 to 30 weight percent), nitrogen (3 to 15 weight percent), and carbon monoxide (3 to 6 weight percent)⟩ ⇒ '
  u'区间上界之和 111 ⇎ 下界之和 66 [组成只给区间, 无法归一, 也就无法由单一数值回答"是不是烃"] ⇒ '
  u'[混合物含氮／一氧化碳即不"仅由碳和氢组成", 可燃气体反因"不是烃"而失去豁免] '
  u'『豁免判定挂在化学定义而非可燃性上; ⟦I⟧⟨Neither coke oven gas, nor hydrogen or methane, the two largest components of coke oven gas, are listed in Appendix A⟩ '
  u'⇒ 两条覆盖路线: 列名路线天然不适用, 只剩数量路线可争』')

A(u'🕰 解释文件的时效是隐形义务: ⟦F⟧⟨In the King Letter, OSHA wrote that coke oven gas used as fuel is included within the fuels exemption⟩(1992) ⇎ '
  u'⟦F⟧⟨OSHA explicitly rescinded the 1992 King Letter⟩(2013) ⇒ 旧解释被采信 21 年(2013-1992) ‖ '
  u'⟦F⟧⟨Company management, including the Clairton PSM manager, were unaware of the 2013 Wilkins Letter.⟩ ⇒ [岗位名含 PSM 却不掌握适用性依据] '
  u'『机关立场改变不发"生效告示", 守法义务包含追踪解释; ⟦F⟧⟨The 2013 Wilkins Letter has not been rescinded or archived⟩ 是其唯一存续证据』')

A(u'🧮 阈值之争的三层破口: ⟦F⟧⟨the company estimated the inventory of these parts of the process to be roughly 7,000 pounds⟩ ⇎ 门槛 10,000 磅(缺口 30%) ‖ '
  u'⟦F⟧⟨the 2010 calculations were incomplete and excluded the entire coke oven gas byproduct recovery unit⟩ ‖ '
  u'⟦F⟧⟨it had no documents indicating the quantity of coke oven gas in those portions⟩ ⇒ '
  u'[反驳一个数量主张先查它的边界与年份, 不查它的精度: 算法距今 15 年(2025-2010) ⇎ 无文档 ⇒ 主张不成立] '
  u'『⟦F⟧⟨decommissioned four coke batteries and had commissioned just a single new one⟩ 是用单调性推理代替实测——拆了旧组不等于管存量下降; '
  u'⟦F⟧⟨assessing the feasibility of updating⟩ 把"没有数"包装成"正在办"』')

A(u'🧭 互联即单一 process: ⟦F⟧⟨any group of vessels which are interconnected and separate vessels which are located such that a highly hazardous chemical could be involved in a potential release shall be considered a single process⟩ ⇒ '
  u'[企业按装置边界算存量, 法规按连通性算存量: 同一套管网的两种切法] 『阈值之争的实质是切割规则而非磅数; '
  u'按连通性切则被排除的那块(⟦F⟧⟨excluded the entire coke oven gas byproduct recovery unit⟩)必计入』')

A(u'🛃 两套监管同词不同范围: ⟦F⟧⟨the RMP exclusion applies to any flammable substance covered by the RMP rule that is used or held for sale as a fuel⟩ ⇎ OSHA 豁免仅限 ⟨hydrocarbon⟩ ⇒ EPA 更宽 ‖ '
  u'⟦F⟧⟨if you hold a listed flammable substance for purposes other than on-site use⟩ ⟨you are potentially covered by [the RMP Rule]⟩ ⇒ '
  u'[同一物质按"用途+去向"三分: 自制／作原料／外送即覆盖, 只有本厂烧掉的部分可能排除] 本厂烧掉 ⟦F⟧⟨approximately only 1,600 pounds⟩ = 门槛的 16% '
  u'『更宽的规则因"用途"条款把大部分物料捞回来, 宽豁免 ⇎ 宽捞回; 企业 2026 年申报 ⟦F⟧⟨all coke oven gas is used as a fuel⟩ 是全称命题, 一个反例即破』')

A(u'🚦 表态的三种认识状态: ⟦I⟧⟨potentially unmitigated hazards⟩ + ⟦I⟧⟨need to be addressed promptly even as the CSB’s investigation continues⟩(因果未定即发建议) ⇎ '
  u'⟦F⟧⟨based on information currently available to the CSB, the OSHA PSM standard appears to apply⟩(表观适用) ⇎ '
  u'⟦F⟧⟨U.S. Steel has contested OSHA’s citations, and the final resolution has not yet been determined as of the date of this report⟩(未决) ⇒ '
  u'[已定 ⇎ 表观 ⇎ 未决 三态并存于同一份报告] 『临时建议的合法性来自"危害可识别", 与"因果已确定"解耦——先动的手不必知道全部答案; '
  u'把自己说了不算的部分(别的机关的裁决)如实留白, 而不是等它落槌』')

A(u'🔬 反事实是因果句的真实形态: ⟦F⟧⟨Had the water washing practice been proceduralized⟩ ⇒ '
  u'⟦F⟧⟨the work performed on the day of the incident could have been accomplished in a manner that would not have caused the valve to catastrophically fail⟩ ‖ '
  u'⟦F⟧⟨Had either company conducted a hazard analysis and addressed the hazards appropriately, the incident could have been prevented.⟩ ⇒ '
  u'[每条成因都是一句"若…本可不发生", 其可检验性取决于替代路径是否被承认为可行] '
  u'『⟦F⟧⟨could have been prevented⟩ ⇎ ⟦F⟧⟨could have been prevented or reduced in severity⟩ 两种措辞差一档: 前者绑因果, 后者只绑严重度; '
  u'混用会把布局问题伪装成成因问题』')

A(u'🧱 被错过的前两次: ⟦F⟧⟨The 2003 PHA recommendation and the 2010 coke oven gas explosion both presented key opportunities⟩ ⇎ '
  u'⟦F⟧⟨but neither event prompted the company to do so⟩ ‖ ⟦U⟧⟨identified a coke oven gas leak from a valve downstream⟩ + '
  u'⟦U⟧⟨the downstream valve was cracked near one of its flanges⟩ + ⟦U⟧⟨applied a temporary repair⟩ ⇒ '
  u'[事故前一个月已有裂阀先兆, 处置是"临时"两字, 而为换它才去隔离的那台阀正是爆源] '
  u'『组织记忆的证据不是"没人想到", 而是"想到过并且留下文件却没做"; 临时修复入档＝风险已被承认的量度』')

A(u'🧑‍🏫 教训的泛化方向: ⟦F⟧⟨If a task can be performed incorrectly and in a way that could result in harm⟩ ⇒ [程序的存在判据是"可错性", 不是危险量级] ‖ '
  u'⟦F⟧⟨The potential for overpressure should always be considered and appropriately controlled when connecting an external pressure source⟩ ⇒ '
  u'[把"两闸夹水"这一具体陷阱抽象为"外来压力源+可能封死"] ‖ ⟦F⟧⟨Regulation only establishes minimum expectations⟩ + '
  u'⟦F⟧⟨There is no prohibition from exceeding minimum requirements⟩ + ⟦F⟧⟨regardless of whether any regulation requires it to do so⟩ ⇒ '
  u'[合规抗辩在建议层被撤回, 却从未在责任层成立过] 『⟦F⟧⟨The CSB is not making any recommendations to the American Society of Mechanical Engineers⟩ 却记下 '
  u'⟦F⟧⟨it does not explicitly prohibit the use of cast iron⟩: 把"标准不禁止"作为缺陷入档而不越权发建议——监督者对标准制定者的边界感』')

A(u'∴骨架 ①后果按"人与爆心的相对位置"计, 不按泄漏质量计; ②先用对照片元删除备选解释, 再谈正证; '
  u'③无实测时用界限比值(额定÷许可)代替未知量; ④从结果反推必要前提足以定因, 不足以还原动作序列; '
  u'⑤隔离设施破坏后自身变成泄漏通道; ⑥换介质＝换风险, 须重走评审; ⑦临时召唤使评审人与操作人不重叠; '
  u'⑧豁免判定挂在定义词上, 可因化学组成反转; ⑨解释性文件有时效, 守法义务含追踪; ⑩阈值之争的实质是切割规则(连通性⇎装置边界); '
  u'⑪同词在不同规则下范围可反(更宽豁免⇎更宽捞回); ⑫危害可识别即可行动, 无需等因果闭合; '
  u'⑬反事实句要分辨"防住发生"与"减轻后果"; ⑭留档未做的旧建议＝组织记忆的直接证据; ⑮标准不禁止≠合规。')

A(u'ℒmethod 层 读"分期发布的调查类文件"=读一个机构的认识状态迁移, 三步复现: '
  u'①把同一命题在三份文件里的措辞按强度排序(报事实 ⇎ 临时建议 ⇎ 定因 ⇎ 表观适用 ⇎ 未决), 措辞升级处即新证据到达处; '
  u'②跨源做同谓词核对: 伤情 ⟦U⟧ 四人+一人 ⇎ ⟦F⟧ 十一伤五重, 13=2+11 闭合即无口径损失; '
  u'⟦U⟧⟨employs approximately 1,300 people⟩ ⇎ ⟦F⟧⟨employed approximately 1,150 people⟩ 差 150 且谓词同为"大约在职"⇒ 口径漂移须标注; '
  u'⟦U⟧⟨began operations in 1916⟩ ⇎ ⟦F⟧⟨began producing coke for steel production in 1918⟩ 谓词不同⇒ 不算矛盾; '
  u'[先判谓词同一性, 再判数字差异是不是不一致]; ③凡遇数值主张, 先查它排除了哪一段、距今多久, 再查精度。')

enc = u'\n'.join(L)
cur, n_ok = None, 0
for m in re.finditer(u'⟦([A-Z])⟧|⟨([^⟨⟩]+)⟩', TITLE + enc):
    if m.group(1):
        cur = m.group(1)
        continue
    assert cur in N, u'无标签锚: %s' % m.group(2)[:60]
    assert norm(m.group(2)) in N[cur], u'归属不符 ⟦%s⟧ %s' % (cur, m.group(2)[:80])
    n_ok += 1
assert (TITLE + enc).count(u'⟩') == n_ok
enc = re.sub(u'⟦([A-Z])⟧ ?(?=⟦\\1⟧⟨)', u'', enc)
assert enc.count(u'《') == 0 and enc.count(u'》') == 0
io.open(OUT, u'w', encoding=u'utf-8').write(
    TITLE + u'\n## [[原始语料|ORIGINAL]]\n\n⟪待生成⟫\n\n## ⟪BabelTele⟫\n\n' + enc +
    u'\n\n## ⛓解读注\n※实况 ⟪待填⟫\n')
io.open(u'corpus/raw/probe/b33_entry_atoms.txt', u'w', encoding=u'utf-8').write(
    u'\n'.join(re.findall(u'⟨([^⟨⟩]+)⟩', enc)) + u'\n')
print(u'lines=%d enc_chars=%d anchors=%d' % (len(L), len(enc), enc.count(u'⟩')))
