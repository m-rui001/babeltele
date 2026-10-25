# -*- coding: utf-8 -*-
# 生成 B38 条目: 脓毒症超声表型之争的两份已刊文本(读者评论 ⇎ 作者答辩)压成一段可机检编码。
# 纪律: 每个 ⟨⟩ 必须逐字命中它自己标签的源; 锚外只允许中文与记号(拉丁字母只出现在出处标签里)。
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ENTRY = u'corpus/babeltele/B38_sepsis_echo_phenotype_comment_response.md'
RAW = {u'K': u'corpus/raw/prose/pmc_sepsis_lpa_comment.txt',
       u'R': u'corpus/raw/prose/pmc_sepsis_lpa_response.txt'}
SRC = {k: io.open(v, encoding=u'utf-8').read() for k, v in RAW.items()}

L = []
A = L.append

A(u'🧭体例 ⟦K⟧＝2026 年 7 月刊出的读者评论(针对一份 2071 例脓毒症超声表型研究) ⇎ ⟦R⟧＝同月同刊紧随其后的作者答辩; 两源写的是一次解释之争，没有任何新数据进来。')
A(u'📋锚点纪律 ⟦K⟧⟨We read with great interest the study by Shvilkina et al.⟩ ⇎ ⟦R⟧⟨We thank Trieu and Nguyen for their thoughtful discussion and interest in our work⟩ ⇒ 每个 `⟨⟩` 逐字回自己标签的源; 双方开场都点名对方作者姓氏，争论保持在人身上而不是队列上。')

A(u'🕳让步的句式 ⟦R⟧⟨We agree that important questions remain in the definition and clinical implications⟩ ‖ ⟦R⟧⟨we agree that incorporation of systolic parameters⟩ ‖ ⟦R⟧⟨We agree that continued investigation is necessary to further validate and refine echocardiographic phenotypes in sepsis⟩ ⇒ 三处同意(机检)按句序代价递减: 先同意"领域仍有问题"(无主)，再同意"加入右室收缩参数本会更充分"(已做不到)，最后同意"需要继续验证"(零成本)。')
A(u'🚧拒绝不写不同意 ⟦R⟧⟨are not directly equivalent to classifications based solely on one parameter such as LVEF⟩ ⇎ ⟦K⟧⟨the absence of statistical significance should not be conflated with evidence of absence of harm⟩ ⇎ ⟦K⟧ 侧同意一词 0 次(机检) ⇒ 评论交出的是一条逻辑规则(不显著不等于无害)，答辩回应的是一次类别不可比; 两句错开一层，且通篇没有任何否定批评的措辞。')
A(u'🔄重新划界 ⟦R⟧⟨We intentionally avoided labeling cluster 3 as a phenotype specific to right ventricular systolic dysfunction and rather one of RV dilation and elevated tricuspid regurgitation gradient⟩ ⇎ ⟦K⟧⟨cluster 3 may more accurately represent a pattern of RV dilation with increased pulmonary afterload rather than true RV systolic dysfunction⟩ ⇒ 两句几乎同构，主语与时态之差就是让步之差: 批评者提出的替换名称被写成自己一开始的选择。')
A(u'🧱不可得作为终止条件 ⟦R⟧⟨our institution did not routinely measure these variables during the time period of this study and these were therefore largely unavailable⟩ ⇎ ⟦K⟧⟨despite their routine availability in echocardiographic assessment⟩ ⇒ 同一个"常规"在两源里互为证据; 这条异议被完整承认，也因此永远无法补做——承认＋不可得是争论的收束方式，不是弱点。')
A(u'🧮外部文献的双向引用 ⟦K⟧⟨Sato et al. [ 2 ] reported a meta-analysis of 3427 sepsis patients⟩ ⇎ ⟦R⟧⟨While existing literature certainly supports higher mortality in populations defined by an elevated LVEF [ 2 ], there may be heterogeneity within this population⟩ ⇒ 同一篇文献(机检: 两侧作者列项各出现)被评论用来支持结论、被答辩用来承认文献后立刻限定人群; "先肯定证据再改变适用人群"是答辩里唯一成形的反驳。')
A(u'🏷可复核强度差 ⟦K⟧ 给同一篇外部文献的刊名、年份、卷期、电子编号齐全(机检: 其检索号在 ⟦K⟧ 命中 2 次而在 ⟦R⟧ 为 0) ⇎ ⟦R⟧⟨Sato R, Sanfilippo F, Hasegawa D, Prasitlumkum N, Duggal A, Dugar S.⟩ ⇒ 答辩只给人名与卷页; 引用格式的机器可核对性也是举证责任的一部分。')
A(u'🧭借先例对冲 ⟦R⟧⟨Geri et al. identified a hyperkinetic cluster characterized by elevated LVEF and CI that was not associated with increased mortality⟩ ⇎ ⟦R⟧⟨Geri G, Vignon P, Aubry A, Fedou AL, Charron C, Silva S, et al.⟩ ⇒ 承认外部文献之后立刻引入一个形状相同、结局相反的先例; 反驳不靠自己重算，而靠选择可比对象——这个名字在 ⟦K⟧ 一侧 0 次(机检)。')
A(u'📐特异性靠合取而非阈值 ⟦K⟧⟨cluster 4, characterized by elevated cardiac index (6.6 L/min/m 2 ) and high left ventricular ejection fraction (LVEF) of mean 75%⟩ ⇎ ⟦R⟧⟨Our cohort was characterized not solely by elevated LVEF but in combination with elevated CI, normal mean RV diameter, and normal mean E/e′ ratio⟩ ⇒ 评论用两个数描述一个簇，答辩用四个条件描述同一个簇; 描述项数之差就是"是否可比"之争的全部实质，没有一个新数字被算出来。')
A(u'🌀机制清单的长度 ⟦K⟧⟨hyperdynamic LV function in sepsis is frequently a manifestation of severe vasodilation, catecholamine-driven sympathetic overstimulation, and a high-output shock state⟩ ⇎ ⟦R⟧⟨Given LVEF is highly load-dependent, it may be elevated in various physiologic states including vasoplegia, hypovolemia, right ventricular dysfunction, or driven by increased catecholamine stimulation⟩ ⇒ 同一份病理生理，评论列 3 项以说明危害，答辩列 4 项以说明不特异; 那个"负荷依赖"的说法只在 ⟦R⟧ 出现(机检)，它把批评的机制解释降级为众多成因之一。')
A(u'⏱时间线与裁决速度 ⟦K⟧⟨12 4 2026 12 5 2026⟩ ‖ ⟦K⟧⟨06 07 2026 07 07 2026⟩ ⇎ ⟦R⟧⟨Received 2026 Jun 5; Accepted 2026 Jun 5⟩ ‖ ⟦R⟧⟨6 7 2026 14 54 54 7 7 2026⟩ ⇒ 评论从收稿到接收跨一个自然月，答辩的收稿与接收写在同一天里; 两条首发日期串并排即见先后。公开的学术仲裁在答辩这一侧可以零评审周期完成。')
A(u'📏清单形式是批评的资产 ⟦K⟧⟨First, cluster 4⟩ ‖ ⟦K⟧⟨Second, the omission of standard right ventricular systolic function parameters⟩ ‖ ⟦K⟧⟨Third, beyond the authors’ brief acknowledgment of non-standardized echocardiographic timing at 14 days⟩ ⇎ ⟦R⟧ 侧三个序数词全部 0 次(机检) ⇒ 批评用编号交出议程，答辩用无编号段落按同一顺序逐条回应; 放弃清单形式的同时保留了清单顺序，这是"按条应战"的可见痕迹。')
A(u'🪞复述即接受 ⟦R⟧⟨The authors highlight ongoing challenges in sepsis phenotyping, including variable selection and capturing the dynamic nature of cardiovascular function over time⟩ ⇒ 答辩第一段把批评的三条异议压缩成"领域挑战"; 其中"变量选择"是评论原文没有的说法——复述时顺手把责任从本队列移到方法学。')
A(u'🈳术语借用 ⟦K⟧⟨the identified clusters may partly reflect distinct hemodynamic phases of sepsis rather than stable endotypes⟩ ⇎ ⟦R⟧⟨will be essential to delineate whether these phenotypes represent transient dynamic states, stable endotypes, or a combination of both⟩ ⇒ 那个"内型"词在评论一侧出现 1 次(机检)，答辩把它原样收进自己的未决清单: 接受批评者提出的二分，只把答案改成"两者兼有"。')
A(u'🈳答辩的缺席清单 ⟦R⟧ 通篇不出现"效力不足"与"错分"这两种说法，不提 36.9 也不提 2071，不写比值比、不用百分号、不引用带外部检索号的文献、三个序数词一个也不用，且没有任何生成式工具披露(机检全为 0) ⇎ ⟦K⟧⟨A cluster of only 41 patients is markedly underpowered to detect a mortality difference of the magnitude reported in larger cohorts⟩ ‖ "负荷依赖"这个说法与那位先例作者的名字都只在 ⟦R⟧ 出现，⟦K⟧ 侧各 0 次(机检) ⇒ 一份答辩的边界更多地由它不写什么决定。')
A(u'📊从不接战的数字 ⟦R⟧ 全文没有百分号(机检)， ⟦K⟧ 有 8 处(机检)含 ⟦K⟧⟨the interpretability of its observed highest mortality rate (36.9%)⟩ ⇎ ⟦R⟧⟨may have been due to the relatively small size of this cluster⟩ ⇒ 答辩承认"簇小"却一次也不给数; 41 例占 2071 例的 1.98% 是双方都没写出的量(机检推导)。')
A(u'🧮外部效应的量级差 ⟦K⟧⟨(OR 2.37; 95% CI 1.47–3.80)⟩ ⇎ ⟦K⟧⟨OR 1.42; 95% CI 1.07–1.87⟩ ⇒ 同一暴露(高射血分数)在两项外部研究里的效应量相差 1.67 倍(机检推导)，评论只报"显著更高"而不报两者之差; 下限 1.07 的那个区间几乎贴着无效值。')
A(u'🔢样本量的三次出场 ⟦K⟧⟨a retrospective cohort of 3151 sepsis and septic shock patients⟩ ‖ ⟦K⟧⟨in a meta-analysis of 65 studies comprising 17,008 patients⟩ ⇒ 评论按顺序摆出 2071、3427、3151 三个队列规模，两个外部队列合计是本研究人数的 3.18 倍(机检推导)，平均每项研究 262 例(机检推导); 批评用"别人的更大样本"说话，答辩不接这个数字。')
A(u'🏳披露方向相反 ⟦K⟧⟨The authors used ChatGPT (OpenAI) to assist with language editing and grammar.⟩ ⇎ ⟦R⟧ 侧这个词 0 次(机检) ‖ ⟦K⟧⟨No datasets were generated or analyzed during the current study.⟩ ⇎ ⟦R⟧⟨The data set used for this study is available from the corresponding author on request⟩ ⇒ 批评者声明无数据并披露语言经模型润色，作者声明数据可索取且不作任何披露; 同一段模板在两源里的填充方向相反。')
A(u'🧯建议句的同构 ⟦K⟧⟨Future studies incorporating larger prospective cohorts, standard right ventricular function parameters, and serial echocardiographic assessments relative to sepsis will be essential⟩ ⇎ ⟦R⟧⟨Further investigation incorporating prospective serial echocardiographic assessments and longitudinal data, as well as integration with biomarkers, will be essential⟩ ⇒ 两条结尾建议同形(三项＋同一谓词)，答辩保留批评要的两项、加一项生物标志物、去掉"扩大前瞻队列"这一项——最后一项恰是它无法承诺的。')
A(u'⚠️结论的换写 ⟦K⟧⟨the prognostic interpretation of individual clusters should be approached with caution⟩ ⇎ ⟦R⟧⟨moving the field from descriptive phenotyping toward individualized risk stratification and tailored therapy⟩ ⇒ 批评的终点是限制用途，答辩的终点是把争议升为愿景; 两份文本都没有撤下任何原结论。')
A(u'🔁动态性由缺陷改为难题 ⟦K⟧⟨is a highly dynamic process, influenced by volume status, fluid resuscitation, and vasoactive therapy⟩ ⇎ ⟦R⟧⟨A challenge in interpreting cardiac dysfunction in sepsis is its dynamic nature, and phenotypes may evolve throughout the clinical course⟩ ⇒ 同一事实: 评论用它推出"分组可能只是相位"，答辩把它写成"解读的困难"; 从缺陷到领域难题的改写不需要任何新证据。')
A(u'📊计量对照 ⟦K⟧ 正文 8710 字母／753 个数字字符 ⇎ ⟦R⟧ 正文 6376 字母／209 个数字字符(均为机检计数) ⇒ 答辩比评论短三成，数字用量却减到不足三分之一; 长度相当而数字密度不同，是"接战层次"之差的可见面。')
A(u'∴骨架 ① 让步是有句式的，且代价按句序递减: 无主的问题→已不可行的分析→零成本的未来; ② 拒绝不必否定，可写成"不可比"或"更特异"; ③ 承认批评者提出的名称而声称一开始就是这么命名的，是最小让步; ④ 承认＋数据不可得＝议题终止，双方都无成本; ⑤ 外部文献可以被同时承认与被同时限定人群; ⑥ 引用格式的机器可核对性也是举证; ⑦ 反驳可用同形状、反结局的他院先例替换自我重算; ⑧ 簇的定义项数增加即"不可比"论证的全部内容; ⑨ 机制列举加长是在削弱对方机制的唯一性，不是在增强自己; ⑩ 收稿与接收同日说明答辩可零评审周期; ⑪ 清单形式归批评者，顺序归答辩者; ⑫ 复述对方议程时会顺手改写责任归属; ⑬ 术语被借用意味着二分被接受; ⑭ 全程不用百分号与效应量就是不在数字层接战; ⑮ 结尾建议的增删暴露了哪些异议被真正接受; ⑯ 披露条款(数据/模型润色)的方向差是可机检的立场信号。')
A(u'ℒmethod 读一篇公开答辩时，先数"同意"类谓词的位置与宾语，再检查每个被承认的异议是否配得上一个可行的补救; 若补救被写成"机构未常规采集"，判定该议题已终止而不必再追。把双方对同一文献的引用串起来看: 同一篇被承认又被限定人群，即为让步式反驳。凡答辩通篇不出现百分号、效应量与分母，即可判定它没有在任何数字层面接战，其结论强度未变。比较簇的描述项数而不是描述用词，项数增加者在做重新划界。检查结尾建议清单的增删: 被删掉的那一项通常是承认了但补不上的。最后核对披露区两行(数据可得性、生成式工具使用)，方向相反即说明双方的举证地位不同。')

enc = u'\n'.join(L)
labels = re.findall(u'⟦([A-Z])⟧⟨', enc)
atoms = re.findall(u'⟧⟨([^⟨⟩]+)⟩', enc)
assert not re.findall(u'⟧⟨⟦', enc), u'双重标签嵌套'
assert len(labels) == len(atoms), u'标签数 != 锚数'
bad = []
for m in re.finditer(u'⟦([A-Z])⟧⟨([^⟨⟩]*)⟩', enc):
    assert m.group(1) in RAW, u'未知标签 ' + m.group(1)
    if m.group(2) not in SRC[m.group(1)]:
        bad.append((m.group(1), m.group(2)))
out = re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)
outlat = len(re.findall(u'[A-Za-z]', out))
inlat = len(re.findall(u'[A-Za-z]', u''.join(atoms)))
inhan = len(re.findall(u'[一-鿿]', u''.join(atoms)))
print(u'编码行数 %d 锚 %d %s 标签总 %d 锚外字母 %d 锚内字母 %d 锚内汉字 %d' % (
    len(L), len(atoms), {k: labels.count(k) for k in sorted(set(labels))},
    len(re.findall(u'⟦([A-Z])⟧', enc)), outlat, inlat, inhan))
for t, a in bad:
    print(u'MISS [%s] %s' % (t, a[:80]))
if bad:
    sys.exit(1)

head = (u'# B38 一篇评论与一封答辩：让步的句式、拒绝的换界与从不接战的数字\n\n'
        u'src: corpus/raw/prose/pmc_sepsis_lpa_comment.txt ⇎ corpus/raw/prose/pmc_sepsis_lpa_response.txt '
        u'(J Intensive Care 2026 读者评论 ⇎ 作者答辩, 同一脓毒症超声表型之争, 无新数据)\n'
        u'tags: 医学论文批评 隐性知识 让步与拒绝的句式 引用可复核性 披露不对称\n\n'
        u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n（待生成）\n')
io.open(ENTRY, u'w', encoding=u'utf-8').write(head)
print(u'wrote ' + ENTRY)
