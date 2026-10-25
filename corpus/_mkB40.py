# -*- coding: utf-8 -*-
# B40 三份同族 FDA 分类令: 锚点允许出现在判词内, 生成后统一从编码文本抽取并逐条与对应原文核对。
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')

ENTRY = u'corpus/babeltele/B40_fda_three_de_novo_orders.md'
RAW = {
    u'C': u'corpus/raw/prose/fr_fda_cardio_ml_notification.txt',
    u'R': u'corpus/raw/prose/fr_fda_radiology_ml_pccp.txt',
    u'M': u'corpus/raw/prose/fr_fda_opioid_impairment_monitor.txt',
}


def pn(s):
    s = s.lower()
    s = re.sub(u'[’‘“”´`\'"]', '', s)
    s = re.sub(u'[‐‑‒–—―−−]', '-', s)
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


A((u'🧭体例', [
    (u'C', u'Viz.ai, Inc'),
    (u'R', u'Caption Health'),
    (u'M', u'Masimo SafetyNet Opioid System'),
], u'⟦C⟧＝心血管机器学习通知软件（⟦C⟧⟨Viz.ai, Inc⟩, 规章号 870.2380）⇎ ⟦R⟧＝放射学机器学习定量影像软件, 且带预定变更控制计划（⟦R⟧⟨Caption Health⟩, 规章号 892.2055）⇎ ⟦M⟧＝阿片类引起的氧合损害监测仪（⟦M⟧⟨Masimo SafetyNet Opioid System⟩, 规章号 868.2250）; 三份同为 ⟦C⟧⟨Final amendment; final order⟩、同写 ⟦C⟧⟨class II (special controls)⟩, 前后相隔不足三个月, 没有争论可读——可读的是同一个法定模板被三种介质填满的方式。'))

A((u'📅 令的日期不是决定的日期', [
    (u'C', u'This order is effective September 11, 2026. The classification was applicable on August 3, 2023.'),
    (u'M', u'On February 19, 2020, FDA received Masimo Corporation’s request for De Novo classification of the Masimo SafetyNet Opioid System.'),
], u'⇒ 生效日与“适用日”差三年（2026−2023, 三份同）, 而 ⟦M⟧ 的请求落在 2020 年——决定、公布、生效是三个时间, 引用者把联邦登记日期当决定日期就丢了其中两个。'))

A((u'📐 法定 120 日在三份文件里都是一句话', [
    (u'C', u'FDA is required to classify the device by written order within 120 days'),
], u'⇒ 同一句义务在三份里逐字相同（机检 3, 即每份 1 次）, 而 ⟦C⟧⟨within 120 days⟩ 之外的公布距离约为期限的 9.1 倍（机检推导 3×365÷120）⇒ 法定期限管决定的那一段, 不管登记与公布。'))

A((u'🧱 自动三级的语法三源逐字相同', [
    (u'C', u'Any device that was not in commercial distribution before May 28, 1976, is automatically classified into, and remains within, class III and requires premarket approval unless and until FDA takes an action to classify or reclassify the device (21 U.S.C. 360c(f)(1)).'),
    (u'R', u'We refer to these devices as ``postamendments devices’’'),
], u'⇒ 风险等级在这里不是事实, 是默认值 ⇒ 分类令的功能是把一个法律默认改写掉, 不是给风险定级; 后一句里的引号排成双反引号（机检: 规范化后仍逐字命中）。'))

A((u'🔁 套语是模板: 逐份计数相同', [
    (u'C', u'At this time FDA has not made this determination for cardiovascular machine learning-based notification software.'),
    (u'C', u'OMB control number'),
], u'⇒ ⟦C⟧⟨De Novo⟩ 各 12 次、三份合计 36 次（机检 12、36）, ⟦C⟧⟨class II⟩ 各 14 次、合计 42（机检 14、42）, ⟦C⟧⟨510(k)⟩ 各 7 次（机检 7）, ⟦C⟧⟨OMB control number⟩ 各 5 次（机检 5）——每份相同即总数必被 3 整除 ⇒ 套语段落是直接复制的, 于是信息只在差异段; 套语也包括上面这句“我们目前还没有做这个判定”: 二级不等于免上市前通知, 连这句免责声明也是模板。'))

A((u'🗣️ 同一保证句的冠词漂移', [
    (u'C', u'will provide a reasonable assurance of the safety and effectiveness of the device'),
    (u'R', u'will provide a reasonable assurance of safety and effectiveness of the device'),
], u'⇒ 带定冠词的写法在 ⟦C⟧ 出现 6 次、在 ⟦R⟧ 与 ⟦M⟧ 各 2 次（机检推导合计 10）, 不带冠词的写法在 ⟦C⟧ 为 0 次、在 ⟦R⟧ 与 ⟦M⟧ 各 4 次（机检推导合计 8）⇒ 同一份文件里两种形式并存; 按完整短语检索 ⟦R⟧⟨reasonable assurance of safety⟩ 会漏掉 ⟦C⟧ 的 6 处。'))

A((u'🏷 同一项评估的两个名字与第三份的空白', [
    (u'C', u'Human factors assessment of the intended users in the intended use environment must evaluate the risk of misinterpretation of device output.'),
    (u'M', u'(4) Usability assessment must be provided to demonstrate that intended device users can safely and correctly use the device.'),
    (u'C', u'Device used in unsupported patient'),
    (u'C', u'population or with unsupported input'),
], u'⇒ 人在环路的验证在 ⟦C⟧ 叫 ⟦C⟧⟨human factors⟩, 在 ⟦M⟧ 叫 ⟦M⟧⟨usability⟩, 两个名字在 ⟦R⟧ 都是 0 次, 而它们也各自不在对方文件里出现（机检零值键）⇒ 缺的那一份不是忘了写: 它的风险表把“患者不懂输出”写成理解问题而不是操作问题, 于是 ⟦C⟧ 要评估的是 ⟦C⟧⟨misinterpretation of device output⟩ 的风险, 而不是正确使用能力的证明。'))

A((u'🧠 机器学习条款藏在一份非机器学习的令里', [
    (u'M', u'For devices using algorithms based on machine learning, the clinical validation must be completed using a dataset that is separate from the training dataset'),
    (u'C', u'The test dataset must be independent from data used in training/development and contain sufficient numbers of cases from important cohorts'),
    (u'R', u'The test dataset must be independent from data used in training/development and contain sufficient numbers of cases from important cohorts'),
], u'⇒ ⟦C⟧⟨machine learning⟩ 在 ⟦C⟧/⟦R⟧ 各 11 次而在 ⟦M⟧ 只 1 次（机检 11、1）, 而那一次恰恰是上面这条引用句 ⇒ 非机器学习器械的特殊控制也可能预留机器学习要求; 同一条“测试集不得与训练集重叠”在两份软件令里写作 ⟦C⟧⟨independent⟩、在 ⟦M⟧ 写作 ⟦M⟧⟨separate⟩, 两个词互不出现在对方文件（机检零值键）。'))

A((u'📊 指标词汇按介质分家', [
    (u'R', u'The performance assessment must be based on objective performance measures (e.g., error metrics, Bland-Altman plots, dice similarity coefficient, Hausdorff distance, sensitivity, specificity, predictive value).'),
    (u'C', u'Objective performance measures (e.g., sensitivity, specificity, positive predictive value or negative predictive value) must be reported with relevant descriptive or developmental performance measures.'),
], u'⇒ 图像专有的三个名词只在 ⟦R⟧ 出现: ⟦R⟧⟨dice⟩、⟦R⟧⟨Hausdorff⟩、⟦R⟧⟨Bland-Altman⟩ 在 ⟦C⟧ 与 ⟦M⟧ 各 0 次（机检零值键）; 灵敏度/特异度/阳阴预测值这套流行病学指标则写在 ⟦C⟧ 与 ⟦M⟧ 的标签段 ⇒ 同叫“客观性能指标”, 括号里的东西完全不同 ⇒ 指标清单是介质的函数, 不是风险的函数。'))

A((u'🚫 边界写在定义里还是写在警告里', [
    (u'C', u'It is intended as the basis for further testing and is not intended to provide diagnostic quality output. It is not intended to identify or detect arrhythmias.'),
    (u'M', u'Warnings identifying that the device is not designed to differentiate between the target condition (e.g., opioid-induced respiratory depression) and other conditions that may cause a false reading (e.g., obstructive sleep apnea);'),
], u'⇒ 否定式适应证在 ⟦C⟧ 写进设备认定段（⟦C⟧⟨not intended⟩ 在 ⟦C⟧ 4 次, 在 ⟦R⟧/⟦M⟧ 为 0, 机检 4）, 在 ⟦M⟧ 写进标签警告（⟦M⟧⟨not designed⟩）; 同一个“不能区分”的语义换了段落就换了效力层级 ⇒ 定义里的否定管准入范围, 标签里的否定管用户行为。'))

A((u'⚖️ 风险表的行是介质决定的', [
    (u'M', u'Adverse tissue reaction................ Biocompatibility evaluation.'),
    (u'M', u'Sensor induced injury.................. Electrical, thermal, and mechanical safety testing.'),
    (u'M', u'Failure to function as intended due to Electromagnetic compatibility electromagnetic and wireless radio testing; and frequency interference.'),
    (u'C', u'Incorrect treatment or diagnosis due to Clinical performance testing; model bias or failure to adequately'),
    (u'C', u'generalize to the intended use population.'),
    (u'C', u'Overreliance on device output for Human factors assessment; and follow-up.'),
], u'⇒ 硬件专有的三行只在 ⟦M⟧ 出现: ⟦M⟧⟨biocompatible⟩、⟦M⟧⟨electromagnetic⟩、⟦M⟧⟨wireless⟩ 在 ⟦C⟧、⟦R⟧ 各 0 次（机检零值键）; 而“模型偏见不够推广”只在 ⟦C⟧ 出现; ⟦C⟧⟨Overreliance⟩（过度依赖）在 ⟦R⟧ 完全为 0（机检零值键） ⇒ 风险表不是风险的清单, 它是“这个介质能怎么伤人”的清单; 表体在抓取时被压平, 上述行只能按整行引用。'))

A((u'🕯 人群代表性的词汇也按介质分家', [
    (u'C', u'contain sufficient numbers of cases from important cohorts (e.g., demographic populations, subsets defined by clinically relevant confounders, comorbidities, and subsets defined by hardware and acquisition characteristics)'),
    (u'M', u'including sensitivity, specificity, positive predictive value, and negative predictive value for each of the subpopulations, use environments, and opioid types'),
], u'⇒ ⟦C⟧⟨demographic⟩ 三份合计 6 次而 ⟦M⟧ 为 0（机检 6 与零值键）, ⟦M⟧ 把同一件事拆成 ⟦M⟧⟨subpopulations⟩、⟦M⟧⟨use environments⟩、⟦M⟧⟨opioid types⟩ 三轴 ⇒ 数据驱动的器械按人群取样, 传感器按环境与药物取样; 不报告“按人群分层”不一定是忽略, 也可能是它的变量根本不在人群上。'))

A((u'🧯 失效披露的两种句式', [
    (u'R', u'(vi) A description of situations in which the device may fail or may not operate at its expected performance level (e.g., poor image quality or for certain subpopulations), as applicable; and'),
    (u'C', u'(iii) Warning that the user should not rely on the lack of a suspected finding to rule out follow-up;'),
    (u'M', u'(v) Warnings against overreliance on the device; and'),
], u'⇒ “警告”这个词在 ⟦R⟧ 一次也没出现（机检零值键）: ⟦R⟧ 把同样的内容写成“描述可能失效的情形”而不打警告标签 ⇒ 三份令的标签段项数相同（都列到第七项）, 但“警告”与“描述”的选择决定了谁来承担失效的语义。'))

A((u'📛 预定变更控制计划的实质是把上市后的变更预先授权', [
    (u'R', u'The design specifications include planned modifications that may be made to the device consistent with an established predetermined change control plan.'),
    (u'R', u'Implementation of modifications agreed Special controls (2)-(3) and in the authorized predetermined change 4(vii); and Certain activities control plan (PCCP) leads to algorithm identified in special controls producing inaccurate output,'),
    (u'R', u'A version history, a description of how device modification(s) will be implemented, and a description of how users will be informed of device modification(s) made in accordance with the PCCP.'),
], u'⇒ ⟦R⟧⟨predetermined change control⟩ 与其缩写 ⟦R⟧⟨PCCP⟩ 在 ⟦R⟧ 合计 17 次, 在 ⟦C⟧/⟦M⟧ 均为 0（机检 17 与零值键） ⇒ “模型会改, 改到哪里算已批准”被拆成三处落点: 认定段写进设计规格, 风险表写进“变更导致输出不准”, 标签段写进版本史与告知用户的方式; 一份允许自身变化的分类令必须同时锁住“告知”。'))

A((u'🎪 拟人化与其他人称不写在同一段', [
    (u'C', u'Upon request, FDA (the Agency or we) has classified the cardiovascular machine learning-based notification software into class II (special controls)'),
    (u'R', u'As part of the design verification and validation activities, you must document the planned device modifications'),
    (u'M', u'All components of the device that contact the skin must be demonstrated to be biocompatible.'),
], u'⇒ ⟦C⟧⟨we⟩ 在三份里各出现 13 次（机检 13, 模板逐字相同的证据）, ⟦R⟧⟨you⟩ 三份合计 2 次且只落在 ⟦R⟧（机检 2, ⟦C⟧ 与 ⟦M⟧ 归零值键）, 义务词 ⟦C⟧⟨must⟩ 三份合计 31 次、其中 ⟦C⟧ 15 次（机检 31、15） ⇒ 只有拿到 ⟦R⟧⟨PCCP⟩（允许上市后自行变更）的那份才出现一个受话人 ⇒ 分类令可以通篇施加义务而没有一个被命令的人, 这不是文风差异, 是授权结构差异。'))

A((u'👤 签发人相同而联系人不同', [
    (u'C', u'Grace R. Graham, Deputy Commissioner for Policy, Legislation, and International Affairs.'),
    (u'C', u'Hetal Odobasic, Center for Devices and Radiological Health, Food and Drug Administration, 10903 New Hampshire Ave., Bldg. 66, Rm. 2108'),
    (u'M', u'Neel Patel, Center for Devices and Radiological Health, Food and Drug Administration, 10903 New Hampshire Ave., Bldg. 66, Rm. 1232'),
], u'⇒ 三份的签名行逐字相同且均为政策副局长（机检: 各 1 次, 即不是器械中心的人签的）; 联系人电话前缀把 ⟦C⟧ 与 ⟦R⟧/⟦M⟧ 分开（⟦C⟧⟨240-402-6540⟩ 只在 ⟦C⟧, ⟦R⟧⟨301-796-6167⟩ 与 ⟦M⟧⟨301-796-6274⟩ 同前缀）; 住址与楼号逐字相同, 只有房间号 2108 / 3672 / 1232 不同 ⇒ “谁签的”在这类文书里可机检但不可推断。'))

A((u'📄 文书层的三个编号与一个排版事实', [
    (u'C', u'[Docket No. FDA-2026-N-9907]'),
    (u'R', u'[Docket No. FDA-2026-N-6535]'),
    (u'M', u'[Docket No. FDA-2026-N-6707]'),
    (u'M', u'[FR Doc. 2026-13140 Filed 6-29-26; 8:45 am]'),
], u'⇒ 案号同一年度同一系列而流水号无序（9907 / 6535 / 6707, 早发的 ⟦R⟧ 反拿小号）⇒ 案号不能排序; 而三份的 ⟦M⟧⟨Filed⟩ 日都恰好是生效前一天（9-10→9-11、6-16→6-17、6-29→6-30, 机检: 两个日期均在同一文件内） ⇒ 这个差是联邦登记的排版惯例, 不是实体审查周期。'))

A((u'🖊️ 文件解释自己的标题', [
    (u'C', u'FDA notes that the ``ACTION’’ caption for this final order is styled as ``Final amendment; final order,’’ rather than ``Final order.’’'),
    (u'R', u'FDA notes that the ACTION caption for this final order is styled as ``Final amendment; final order,’’ rather than ``Final order.’’'),
], u'⇒ 这条脚注与 ⟦C⟧⟨Final amendment; final order⟩ 一起出现在每份的标题行与脚注, 内容与器械无关, 只与 2019 年 12 月起的一次编辑体例改动有关; 两份模板一个给 ⟦R⟧⟨ACTION⟩ 加引号一个不加——规范化把这一差别抹平, 两串在 ⟦C⟧ 与 ⟦R⟧ 命中同一文本 ⇒ 引号级飘移只能靠逐字锚保留, 同一机关内部的模板也会在细节上漂移。'))

A((u'∴骨架', [],
   u'① 分类令的联邦登记日期不是决定日期（三份均差三年）; ② 法定 120 日只管决定那一段, 不管公布; ③ 套语段落逐份计数相同即证明它们是复制的, 信息全在差异段; ④ 同一保证句可以带或不带定冠词, 按短语检索会漏; ⑤ 同一项验证在不同文件里叫“人因子”或“可用性”, 甚至两个名字都不出现; ⑥ 机器学习要求可以藏在非机器学习的令里, 同一要求写作“独立”或“分离”; ⑦ 指标清单是介质的函数（图像度量 ⇎ 流行病度量）; ⑧ 否定式边界写在认定段管准入, 写在标签里管用户; ⑨ 风险表的行是“这个介质能怎么伤人”的清单; ⑩ 人群分层词汇的缺失可能只是变量不在人群上; ⑪ “警告”与“描述可能失效的情形”是同一件事的两种责任划分; ⑫ 预定变更控制计划把上市后的变更预先授权, 并把“告知用户”写进同一个分类; ⑬ 人称切换标出自限与监管要求的边界——义务可以没有受话人; ⑭ 签发人与联系人可机检但不可推断; ⑮ 案号不可排序, 登记日与生效日差一天是排版而非审查; ⑯ 文件会解释自己的标题写法, 而该解释本身也会飘移。'))

A((u'ℒmethod', [],
   u'读“同一机关、同一文书类型、不同产品”的多份文件时, 先把套语段落的关键词逐份计数, 计数相同的部分直接当模板跳过; 再把“风险表”与“特殊控制”两段按行对齐取差集——差集里的每一行都是介质的证据。凡遇“某项要求在这一份里没有”, 先查它是不是换了名字（人因子/可用性、独立/分离、警告/描述）, 再才判定为缺失。凡引用联邦登记文书, 先抄“适用日”与“生效日”两个日期, 二者不同时以“适用日”为决定日。要判断一份文书是否允许产品自变更, 只查它有没有出现第二人称: 义务词密集而无受话人, 说明要求是由机关代读者保有的。'))

enc = u'\n'.join(lines)

assert u'⟧⟨⟦' not in enc, u'锚嵌套'
assert u'》' not in enc and u'《' not in enc, u'括号污染'
anch = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', enc)
miss = []
for tag, atom in anch:
    if pn(atom) not in SRC[tag]:
        ws = pn(atom).split()
        i = SRC[tag].find(u' '.join(ws[:4]))
        miss.append((tag, atom[:70], pn(atom)[:110], SRC[tag][i:i + 200] if i >= 0 else u'<no prefix>'))
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

head = (u'# B40 三份同族分类令：模板逐字相同，差异全在介质\n\n'
        u'src: ' + u' ⇎ '.join(RAW[k] for k in (u'C', u'R', u'M')) +
        u' (联邦公报 91 FR 57785 ⇎ 91 FR 36522 ⇎ 91 FR 39459, 三份同为面向新增 II 类器械的分类令)\n'
        u'tags: 监管分类 隐性知识 模板与差集 风险表 介质决定措辞 义务与受话人\n\n'
        u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n（待生成）\n')
io.open(ENTRY, u'w', encoding=u'utf-8').write(head)
print(u'wrote ' + ENTRY)
