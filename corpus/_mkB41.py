# -*- coding: utf-8 -*-
# B41 同一 docket 的拟议令 ⇎ 最终令: 锚点可出现在判词内, 生成后统一与对应原文逐字核对。
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')

ENTRY = u'corpus/babeltele/B41_fda_proposed_vs_final_order.md'
RAW = {
    u'P': u'corpus/raw/prose/fr_fda_ish_proposed_order.txt',
    u'F': u'corpus/raw/prose/fr_fda_ish_final_order.txt',
}


def pn(s):
    s = s.lower()
    s = re.sub(u'[’‘“”´`\'"]', '', s)
    s = re.sub(u'[‐‑‒–—―−]', '-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]', ' ', s)
    return re.sub(u' +', ' ', s).strip()


SRC = {}
for k, p in RAW.items():
    t = io.open(p, encoding='utf-8').read()
    body = u'\n'.join(l for l in t.split(u'\n')
                      if not re.match(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', l))
    SRC[k] = pn(body)

lines = []


def A(arg):
    head, ats, gloss = arg
    parts = [u'⟦%s⟧⟨%s⟩' % (k, a) for k, a in ats]
    if parts:
        lines.append(u'%s %s ⇒ %s' % (head, u' ‖ '.join(parts), gloss))
    else:
        lines.append(u'%s %s' % (head, gloss))


TAIL = u'Device performance data demonstrating appropriate specimen stability based on the intended use specimen type(s) of the device, as applicable.'
SPEC = u'Specification for risk mitigation elements intended to mitigate risks associated with testing and results interpretation, including controls, procedures, and user training requirements, as appropriate.'
CONTACT = (u'Soma Ghosh, Center for Devices and Radiological Health, Food and Drug Administration, '
           u'10903 New Hampshire Ave., Bldg. 66, Rm. 3316, Silver Spring, MD 20993, 240-402-5333, [email&#160;protected]')

A((u'🧭 体例', [
    (u'P', u'Proposed amendment; proposed order; request for comments.'),
    (u'F', u'Final amendment; final order.'),
    (u'P', u'[Docket No. FDA-2025-N-1243]'),
    (u'F', u'[Docket No. FDA-2025-N-1243]'),
    (u'P', u'Grace R. Graham, Deputy Commissioner for Policy, Legislation, and International Affairs.'),
    (u'F', u'Grace R. Graham, Deputy Commissioner for Policy, Legislation, and International Affairs.'),
], u'⟦P⟧＝90 FR 24540（2025-06-11，拟议把肿瘤伴随诊断用的原位杂交检测系统从三级降为二级）⇎ ⟦F⟧＝91 FR 53184（2026-08-17，最终令），'
  u'同一 ⟦P⟧⟨[Docket No. FDA-2025-N-1243]⟩ 与 ⟦F⟧ 同号，相隔 14 个月（机检 14＝年份差折成月再加月序差），'
  u'并由同一位副委员长签发——两份的署名行逐字相同，于是“同一件事的两个阶段”有了可核对的锚。文书类型行是唯一写明程序状态的地方：'
  u'⟦P⟧⟨Proposed amendment; proposed order; request for comments.⟩ ⇎ ⟦F⟧⟨Final amendment; final order.⟩，少掉的是征求动作本身。'))

A((u'📄 版面：加了整节回应的文件反而更短', [
    (u'P', u'[Pages 24540-24549]'),
    (u'F', u'[Pages 53184-53191]'),
    (u'F', u'II. Comments on the Proposed Order and FDA Responses'),
    (u'F', u'FDA received comments from fewer than 5 commenters'),
], u'页码区间算出 ⟦P⟧ 占 10 页 ⇎ ⟦F⟧ 占 8 页（机检 8；两文件合计 18 页），而 ⟦F⟧ 多出整节 ⟦F⟧⟨II. Comments on the Proposed Order and FDA Responses⟩。'
  u'省下的篇幅来自 ⟦F⟧⟨FDA received comments from fewer than 5 commenters⟩ 这一行所代表的那批人：'
  u'最终令不再自证科学依据，它只回应——记录越薄，回应的行数越多，正文的论证越少。'))

A((u'🗣 第一人称是定义括号授权的', [
    (u'P', u'The Food and Drug Administration (FDA) is proposing to reclassify'),
    (u'F', u'The Food and Drug Administration (FDA, the Agency, or we) is issuing a final order'),
    (u'F', u'The order of the comments and our response to them is purely for organizational purposes'),
], u'⟦F⟧⟨the Agency, or we⟩ 这一串在 ⟦P⟧ 为 0（0 键）；同一别名一旦写进摘要段的定义括号，第一人称所有格在 ⟦P⟧ 0 次 ⇎ ⟦F⟧ 4 次就成立（机检 4）。'
  u'而 ⟦F⟧ 用第一人称的那一句是 ⟦F⟧⟨The order of the comments and our response to them is purely for organizational purposes⟩——'
  u'机关说“我们”的时刻，是它声明排序不代表分量的时刻；其余整节回应全部用第三人称（⟦F⟧⟨FDA agrees with the comments supporting this reclassification⟩、⟦F⟧⟨FDA declines to adopt the proposed revisions⟩）。'))

A((u'🗩 编号意见数与进言者数是两个量', [
    (u'F', u'we separated different issues discussed by the same commenter and designate them as distinct comments'),
    (u'F', u'One comment'),
    (u'F', u'One commenter'),
    (u'F', u'FDA received numerous comments supporting the proposed reclassification'),
    (u'F', u'(Comment 13)'),
], u'编号意见 13 条（机检 13，与 ⟦F⟧⟨(Comment 13)⟩ 的号一致）⇎ 进言者不足 5 名，比值 2.6（机检 13÷5）；起句 ⟦F⟧⟨One comment⟩ 12 次（机检 12）＋⟦F⟧⟨One commenter⟩，'
  u'唯一的复数起句见末锚（numerous comments）。拆分规则写在首锚——'
  u'“意见条数”是编排产物，按条数统计行业立场就会把一个人拆成的四件事读成四家公司的四件事。'))

A((u'🤝 没有反对记录的修订', [
    (u'F', u'All commenters provided support for the proposed reclassification with some comments also providing recommendations or proposed modifications for clarity'),
], u'整份记录是一边倒的支持（见上锚），而 object to、not support、oppose 三式在两源均为 0（0 键）。'
  u'即便如此，最终文本仍改了 3 处字、删了 1 项控制、并让整列序号前移一位——无反对的协商程序并不产出无改动的文本，这是“协商式立法”最省事的误读。'))

A((u'🔀 序号漂移：删除留下的不是缺口', [
    (u'P', u'(ix) ' + TAIL),
    (u'F', u'(viii) ' + TAIL),
    (u'P', u'(x) Clinical data generated using well-characterized clinical specimens'),
    (u'F', u'(ix) Clinical data generated using well-characterized clinical specimens'),
], u'上列两对逐字相同、只差一个号：(ix)⇎(viii) 与 (x)⇎(ix)；'
  u'同串在两源各命中 1 次＝机检 2。后果是 ⟦F⟧ 里“已移除 (b)(1)(viii)”与 ⟦F⟧ 印出的 (viii) 指的是两条不同条文：号相同、内容不同，跨文引用者无法从号反推内容。'))

A((u'🗑 被删掉的那一项带走了它专属的测量词', [
    (u'P', u'(viii) Device performance data demonstrating appropriate reagent stability for real-time and in-use stability; post-hybridization signal stability; and photostability of probe, as applicable.'),
    (u'F', u'the Agency is removing proposed Sec. 864.1890(b)(1)(viii)'),
    (u'F', u'quality system requirements set forth under part 820 (21 CFR part 820) are sufficient to ensure that reagents are appropriately assessed and labeled'),
], u'『杂交后信号』与『探针光稳定性』两个词形在 ⟦F⟧ 均为 0（词形列入 0 键清单）：拟议令用这两个词写明的稳定性要求，被整项交还给 ⟦F⟧⟨quality system requirements set forth under part 820 (21 CFR part 820) are sufficient to ensure that reagents are appropriately assessed and labeled⟩。'
  u'删除的代价不是“少一份数据”，而是这一类测量词此后再没有文本引用它——查“光稳定性要求”的人翻遍最终令也找不到，因为该要求现在归入通用条款。'))

A((u'🤐 三处没人宣布的字级改动', [
    (u'P', u'criteria for all applicable signals must be provided'),
    (u'F', u'criteria for all applicable signals must be included'),
    (u'P', u'analytical sensitivity provided from studies'),
    (u'F', u'analytical sensitivity from studies'),
], u'对齐 ⟦P⟧ 与 ⟦F⟧ 的特殊控制段后，除已宣布的两项外还剩三处：『提供』改『包含』共 2 处，另一处是把 ⟦P⟧⟨analytical sensitivity provided from studies⟩ 中间的 provided 删净成为 ⟦F⟧⟨analytical sensitivity from studies⟩——'
  u'三处的字号即机检 3（两个「包含」＋一个删净的「提供」）。它们不在任何一条回应里，也不在 ⟦F⟧⟨FDA has revised the design verification and validation special controls⟩ 那句自我清单里。'))

A((u'🚫 拒绝重编号的那句与已经动过的编号', [
    (u'F', u'nor is FDA renumbering the identification and classification paragraphs as proposed'),
    (u'F', u'FDA is not adding the proposed paragraph to Sec. 864.1890'),
], u'⟦F⟧ 唯一一次谈到“重编号”是拒绝：⟦F⟧⟨nor is FDA renumbering the identification and classification paragraphs as proposed⟩，而“重编号”这个词在 ⟦P⟧ 为 0（0 键）。'
  u'它拒绝的是 (a)/(b) 段编号，而同一份文件把 (b)(1) 列的序号整体前移了一位（见“序号漂移”行）——同一机关对编号有两种态度，所以“不许改号”这句不能用来推断条文号是稳定的。'))

A((u'🧪 让步同时是裁量的扩张', [
    (u'F', u'to consider surrogate samples that adequately represent the intended use specimen type(s) and intended use biomarker(s), as appropriate, as determined by FDA, to supplement clinical specimens'),
    (u'F', u'FDA will determine the appropriateness of surrogate samples based on clinical and scientific data and/or justification available to the Agency'),
    (u'P', u'Device performance data demonstrating appropriate precision and reproducibility of the device using clinical specimens representing the intended use specimen type(s)'),
], u'唯一被接受的实质让步写在 ⟦P⟧⟨Device performance data demonstrating appropriate precision and reproducibility of the device using clinical specimens representing the intended use specimen type(s)⟩ 中间，'
  u'插入的就是上列 ⟦F⟧ 首锚那句（surrogate samples … as determined by FDA, to supplement clinical specimens）；'
  u'替代样本一词只在 ⟦F⟧ 出现，⟦P⟧ 侧为 0（0 键）。让步句尾挂着 ⟦F⟧⟨as determined by FDA⟩，第二锚又写明由谁判定：'
  u'允许替代样本的代价是替代样本是否合格由机关逐案判定——“放宽”只写在逗号前。'))

A((u'📝 自我清单只有两项', [
    (u'F', u'FDA has revised the design verification and validation special controls to add to the existing proposed Sec. 864.1890(b)(1)(v) requirement the consideration of surrogate samples'),
    (u'F', u'FDA has removed the proposed Sec. 864.1890(b)(1)(viii) requiring device performance data demonstrating reagent stability'),
    (u'F', u'is finalizing the identification language in this final order without change'),
], u'⟦F⟧ 用两句话概括改动（加 surrogate、删 reagent stability），其余写作 ⟦F⟧⟨is finalizing the identification language in this final order without change⟩。'
  u'自述数是 2，逐字对齐看到的是 3 处字级改动＋1 次整列前移——叙述句不可当 diff 用，机关对自己文本的总结同样是叙述。'))

A((u'⚖️ 同一节里两种强度的义务', [
    (u'F', u'manufacturers must obtain 510(k) clearance before marketing the device'),
    (u'F', u'FDA expects that manufacturers will submit a 510(k) premarket notification'),
    (u'F', u'such devices may continue to be marketed under the previously issued PMA approval'),
    (u'F', u'IV. Implementation Strategy'),
], u'新器械那句用⟦F⟧⟨manufacturers must obtain 510(k) clearance⟩，老器械那句用⟦F⟧⟨FDA expects that manufacturers will submit a 510(k) premarket notification⟩，其前提是第三锚的“可继续按原批准上市”。两种强度并存在同一个 ⟦F⟧⟨IV. Implementation Strategy⟩ 内，而 ⟦P⟧ 侧「须先取得许可」的句式为 0（词形列入 0 键清单）：义务强度按“谁已在市场上”分档，不按风险分档；引用“重新分类后要上市前通知”时必须先问产品是否在生效日前已卖过。'))

A((u'📅 承诺兑现，期限换了语法', [
    (u'P', u'FDA proposes that any final order based on this proposed order become effective 30 days after'),
    (u'F', u'This final order is effective 30 days after the date of its publication in the Federal Register'),
    (u'P', u'must be submitted by August 11, 2025'),
    (u'F', u'The comment period on the proposed order closed on August 11, 2025'),
    (u'P', u'Dated: June 5, 2025.'),
], u'同一个 30 日与同一个 2025-08-11：在 ⟦P⟧ 里是义务与提议，到 ⟦F⟧ 变成过去式的事实——上面四锚按 ⟦P⟧⇎⟦F⟧ 成对，只差时态与情态。'
  u'另有一处只有文书习惯能解释：⟦P⟧ 文末有 ⟦P⟧⟨Dated: June 5, 2025.⟩ 这一行，⟦F⟧ 末尾没有对应的签署日期块（0 键），最终令的日期只剩页眉与投稿戳——比两份文件的正文更早的那个日期，恰恰是拟议令里写了、最终令里没写的那一行。'))

A((u'📑 同一个“section V”在两份文件里不是同一节', [
    (u'P', u'V. Risks to Health'),
    (u'F', u'V. Analysis of Environmental Impact'),
    (u'F', u'the risks to health identified in section V of the proposed order'),
], u'⟦P⟧ 的第五节是 ⟦P⟧⟨V. Risks to Health⟩，⟦F⟧ 的第五节是 ⟦F⟧⟨V. Analysis of Environmental Impact⟩；⟦P⟧ 裸用 ⟦P⟧⟨section V⟩ 9 次（机检 9），'
  u'⟦F⟧ 只用 1 次且必须补上第三锚的 of the proposed order（两源合计 10，机检 10）。'
  u'同一份文件里 ⟦F⟧⟨IV. Implementation Strategy⟩ 与 ⟦F⟧⟨section II.B⟩ 是自指，指别份文件的节号时“第几节”必须带文件名——最终令做到了，读者复述时通常做不到。'))

A((u'🧯 风险表只存在于拟议令', [
    (u'P', u'Table 1--Risks to Health and Mitigation Measures for Oncology Therapeutic ISH-Based Test Systems'),
    (u'F', u'in table 1 of the proposed order'),
    (u'P', u'[verbar]'),
], u'上列 ⟦F⟧ 引表句之后并未重排该表——它确认风险“已在拟议令第五节列出”，却把表格留在另一份文件里。'
  u'抓取痕迹恰好把这件事写成可核对的形式：表格竖线在 ⟦P⟧ 里写作 ⟦P⟧⟨[verbar]⟩，在 ⟦F⟧ 里 0 处（0 键）——最终令没有携带表格，连转换残留的竖线都没有。'))

A((u'📛 引文里的方括号改写', [
    (u'F', u'``[s]pecification for risk mitigation elements intended to mitigate risks associated with testing and results interpretation, including controls, procedures, and user training requirements, as appropriate.'),
    (u'P', SPEC),
], u'同一条文在 ⟦P⟧ 起句大写，被 ⟦F⟧ 引作方括号里的小写式——方括号替换首字母是全库唯一的一处（机检 1）。'
  u'规范化比对会同时吞掉方括号与引号样式，所以这类改写必须原样写进锚点才测得到：引号未动、句未删，只把大写 S 关进括号，法律引文的“忠实”正是靠这种痕迹标示。'))

A((u'🧲 人工智能词汇只从程序段进来', [
    (u'F', u'artificial intelligence (AI)/machine learning (ML) driven digital pathology (DP) algorithms'),
    (u'F', u'device-specific PCCPs'),
    (u'F', u'FDA encourages manufacturers to leverage the Q-Submission program'),
], u'五个算法相关词形（机器学习、人工智能、数字病理、算法、器械专属计划）在 ⟦P⟧ 全为 0（词形列入 0 键清单）；'
  u'⟦F⟧ 的全部 AI 措辞都落在首锚那条被转述的意见里，答复则是次锚的程序性一句，'
  u'通篇算法措辞在 ⟦F⟧ 合计 6 处（机检 6＝三种缩写的并计，构成见解读注）。特殊控制条文对此一字未改：一条关于算法器械的意见，落到文本只是新增一个咨询通道（⟦F⟧⟨device-specific PCCPs⟩）。'))

A((u'👤 联系人相同，联系方式不可读', [
    (u'P', CONTACT),
    (u'F', CONTACT),
], u'两份的联系人块逐字相同（同一位、同一号楼房间、同一直线电话），邮箱位置在两份里都是首锚末尾那一串 ⟦P⟧⟨[email&#160;protected]⟩——混淆脚本留下的实体串，@ 符号两源各 0 次（0 键）。'
  u'可核的事实是：14 个月、两份文件、责任落在同一名雇员身上，而公开文本没有留下任何能联系到她的字符。'))

A((u'∴ 骨架', [],
  u'① 程序状态写在文书类型那一行，取消也写在同一行；② 署名行可跨文件逐字相同而签署日期块整行消失；③ 页数不是内容量的证据；'
  u'④ 第一人称的许可写在定义括号里；⑤ 编号意见数由机关编排，不等于进言者数；⑥ 一边倒的支持记录仍会产生未宣布的改动；'
  u'⑦ 删除一项控制会带走它专属的测量词；⑧ 删除不留缺口，序号整体前移；⑨ 同一号码在两份文件里指不同条文；⑩ 自我清单是叙述不是 diff；'
  u'⑪ 让步句的后半句常是裁量句；⑫ must 与 expects 在同节里按市场状态分档；⑬ 提议里的义务句式到最终令变成事实句式；'
  u'⑭ “第几节”必须带文件名才安全；⑮ 表格留在哪一份文件里是可机检的；⑯ 引文的方括号改写只有原样入锚才测得到；'
  u'⑰ AI 词汇可以只进程序段而不进控制条文；⑱ 联系块逐字复用而联系方式不可读。'))

A((u'ℒmethod', [],
  u'读“拟议 ⇎ 最终”这一对：先把两份的条文段按序号逐字对齐取差集，再用类型行／页码区间／联系人三块确认它们在同一条立法链上；'
  u'差集里的每一处都要回查该改动是否在回应段被宣布过——没被宣布的字级改动（provided→included、删掉的 provided）只能靠对齐发现，通读回应是看不见的。'
  u'凡遇“某项已被移除”，立刻检查同一号码在最终文本里是否另有其物，并把该列后续序号逐个核一遍是否前移。'
  u'机关自述的改动数与实测不等时以实测为准。判断意见是否被听见，不要数回应条数，要数被接受的实词改动字号；'
  u'判断算法是否进入监管文本，不要检索 AI 词，要检索控制条文那一段有没有与算法有关的名词——本文两处都没有。'
  u'引用条文号时永远附文件身份，因为号在两份之间会漂。'))


# 锚点外的 Latin 词形换成中文(锚点内逐字不动); 条文号与 90/91 FR 页码标识保留。
OUT_REPL = [
    (u'surrogate samples', u'替代样本'), (u'surrogate', u'替代样本'), (u'renumbering', u'重编号'),
    (u'object to', u'反对式'), (u'not support', u'不支持'), (u'oppose', u'反对'),
    (u'analytical sensitivity provided from studies', u'分析灵敏度“提供自研究”原句'),
    (u'analytical sensitivity from studies', u'分析灵敏度“自研究”新句'),
    (u'provided', u'“提供”'), (u'included', u'“包含”'), (u'numerous comments', u'大量意见'),
    (u'reagent stability', u'试剂稳定性'), (u'section V', u'第五节'), (u'section II.B', u'第二节 B 款'),
    (u'FDA expects', u'机关“预期”'), (u'expectations', u'预期'), (u'expects', u'“预期”'),
    (u'must obtain', u'“须取得”'), (u'must', u'“须”'), (u'filing', u'投稿'), (u'ACTION', u'类型行'),
    (u'diff', u'差集'), (u'Dated', u'日期行'), (u'determined', u'判定'), (u'supplement', u'补充'),
    (u'stability', u'稳定性'), (u'specimens', u'标本'), (u'clinical', u'临床'), (u'proposed', u'拟议'),
    (u'support', u'支持'), (u'samples', u'样本'), (u'comments', u'意见'), (u'order', u'令'),
    (u'FDA', u'机关'), (u'AI/ML', u'算法'), (u'AI', u'算法'), (u'class III', u'三级'),
    (u'PMA', u'上市前批准'), (u'III', u'三级'), (u'II', u'二级'),
]


CJKP = u'\\u4e00-\\u9fff、，。；：“”（）—《》'


def scrub(line):
    parts = re.split(u'(⟨[^⟨⟩]*⟩)', line)
    for i, s in enumerate(parts):
        if s.startswith(u'⟨'):
            continue
        for a, b in OUT_REPL:
            s = s.replace(a, b)
        s = re.sub(u'(?<=[%s]) +(?=[%s])' % (CJKP, CJKP), u'', s)
        parts[i] = s
    return u''.join(parts)

lines = [scrub(l) for l in lines]

enc = u'\n'.join(lines)

assert u'⟧⟨⟦' not in enc, u'锚嵌套'
assert u'》' not in enc and u'《' not in enc, u'括号污染'
anch = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', enc)
miss = []
for tag, atom in anch:
    if pn(atom) not in SRC[tag]:
        ws = pn(atom).split()
        i = SRC[tag].find(u' '.join(ws[:4]))
        miss.append((tag, atom[:70], pn(atom)[:110], SRC[tag][i:i + 220] if i >= 0 else u'<no prefix>'))
if miss:
    for m in miss:
        print(u'MISS %s | %s\n  want: %s\n  have: %s' % m)
    sys.exit(1)

labels = re.findall(u'⟦([A-Z])⟧', enc)
out = re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)
inlat = len(re.findall(u'[A-Za-z]', u''.join(a for _, a in anch)))
inhan = len(re.findall(u'[一-鿿]', u''.join(a for _, a in anch)))
print(u'行数 %d 锚 %d %s 锚内字母 %d 锚内汉字 %d 锚外字母 %d' % (
    len(lines), len(anch), {k: labels.count(k) for k in sorted(set(labels))},
    inlat, inhan, len(re.findall(u'[A-Za-z]', out))))

head = (u'# B41 拟议令 ⇎ 最终令：宣布 2 项改动，逐字对齐看到的是 3 处字与 1 次整列前移\n\n'
        u'src: ' + u' ⇎ '.join(RAW[k] for k in (u'P', u'F')) +
        u' (联邦公报 90 FR 24540 ⇎ 91 FR 53184, 同一 Docket No. FDA-2025-N-1243, 相隔 14 个月)\n'
        u'tags: 监管立法 隐性知识 拟议⇎最终 条文差集 序号漂移 宣布与未宣布 义务强度\n\n'
        u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n（待生成）\n')
io.open(ENTRY, u'w', encoding=u'utf-8').write(head)
print(u'wrote ' + ENTRY)
