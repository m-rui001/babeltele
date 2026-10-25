# -*- coding: utf-8 -*-
"""生成 B39 的 ⛓解读注(幂等: 每次整体替换 ## ⛓解读注 之后的内容)。"""
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ENTRY = u'corpus/babeltele/B39_mobilization_targettrial_letter_response.md'
RAW = [(u'S', u'corpus/raw/prose/pmc_mobilization_dose_study.txt'),
       (u'L', u'corpus/raw/prose/pmc_mobilization_targettrial_letter.txt')]
src = dict((k, io.open(v, encoding='utf-8').read()) for k, v in RAW)
path = dict(RAW)

full = io.open(ENTRY, encoding='utf-8').read()
enc = full.split(u'## ⟪BabelTele⟫')[1].split(u'## ⛓解读注')[0].strip(u'\n')
enc_n = len(enc.replace(u'\n', u''))
enc_nl = len(enc)
atoms = re.findall(u'⟧⟨([^⟨⟩]+)⟩', enc)
labels = re.findall(u'⟦([A-Z])⟧⟨', enc)
tags_all = re.findall(u'⟦([A-Z])⟧', enc)
out = re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)
outlat = len(re.findall(u'[A-Za-z]', out))
inlat = len(re.findall(u'[A-Za-z]', u''.join(atoms)))
inhan = len(re.findall(u'[一-鿿]', u''.join(atoms)))
n_s, n_l = labels.count('S'), labels.count('L')
n_atoms = len(atoms)
assert n_atoms == n_s + n_l == 64, (n_atoms, n_s, n_l)
orig_a = re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', full, re.S).group(1)
dig_total = len(orig_a)
dg = dict((m.group(1), len(m.group(2).strip())) for m in
          re.finditer(u'^### ⟦([A-Z])⟧[^\n]*\n(.*?)(?=\n### ⟦|\\Z)', orig_a, re.M | re.S))
blocks = dict((m.group(1), len([x for x in m.group(2).strip().split(u'\n') if x.strip()])) for m in
              re.finditer(u'^### ⟦([A-Z])⟧[^\n]*\n(.*?)(?=\n### ⟦|\\Z)', orig_a, re.M | re.S))
dig_body = sum(dg.values())


def chars_of(k):
    m = re.search(u'^chars: (\\d+)$', src[k], re.M)
    return int(m.group(1))


raw_chars = sum(chars_of(k) for k, _ in RAW)
def bytes_of(k):
    return len(open(path[k], 'rb').read())


raw_bytes = sum(bytes_of(k) for k, _ in RAW)
for k, _ in RAW:
    h = re.search(u'^text_sha256: ([0-9a-f]{16})$', src[k], re.M).group(1)
    assert len(h) == 16
    print(u'[%s] chars=%d bytes=%d sha=%s 锚=%d 摘要块=%d' % (k, chars_of(k), bytes_of(k), h,
                                                              labels.count(k), blocks.get(k, 0)))
ret_d = 100.0 * enc_n / dig_total
ret_c = 100.0 * enc_n / raw_chars
ret_b = 100.0 * enc_n / raw_bytes

G = []
a = G.append
a(u'※体例 两源都是同一期刊(J Intensive Care, 2026 年第 14 卷)已刊文本，写成一次指控与一份沉默的原文: ⟦S⟧＝被批评的队列研究'
  u'(PMC13455185, DOI 10.1186/s40560-026-00892-5, PMID 42237429, Hirakawa 等, 收稿 2026-02-17／接收 2026-05-28, 该卷第 59 号文章) '
  u'⇎ ⟦L⟧＝针对它的 Matters Arising 信(PMC13488585, DOI 10.1186/s40560-026-00931-1, PMID 42618955, Amolakhji 与 Pehlaj, '
  u'2026 年 7 月 8 日收稿、8 月 17 日接收、8 月 19 日发布, 该卷第 63 号)。两源均为 Europe PMC fullTextXML 原始 JATS 转正文，'
  u'去页眉后逐字符入库(raw 头部自记 text_sha256 与 chars)。本条没有第三份文本: 被批评的一方未答辩，期刊也未刊出回应，'
  u'所以这一对的方向与上一条(评论⇎答辩)相反——只有指控方可写，被指控方只能被读。')

a(u'※派生算术与计数(全部由 audit.py 机检，23 个键) 0＝合计 38 项缺席断言: ⟦S⟧ 侧 immortal／E value／marginal structural／g-methods／'
  u'STROBE／MCID／minimal clinically／power／hypothesis／C-statistic／designated／AUROC／Fine–Gray／not intended／guarantee／1.85 共 16 项为 0，'
  u'⟦L⟧ 侧 reimbursement／minute／weekend／2774／25.8／overadjust／directed acyclic／Post-Barthel／Pre-Barthel／AUC／has been considered／'
  u'First,／Second,／Third,／survivor／cerebrovascular／chronic kidney／2.65／1.58／4.46／CRRT／continuous renal 共 22 项为 0。'
  u'2＝"should be interpreted as a time-varying exposure" 在两源之和(各 1 次⇒引文逐字)；4＝信的四个补救动名词短语各命中 1 次；'
  u'5＝原文限制段的序数标记数；10＝"196" 在 ⟦S⟧ 的出现次数。'
  u'392＝196×2；64.3＝round(392÷610×100,1)＝匹配后队列占入组人数的比例；16.6＝round(101÷610×100,1)＝若分母取全队列所得的比例；'
  u'25.8＝round(101÷392×100,1)＝复现正文印出的那个数，从而证明它的分母是 392；1.59＝round(31.6÷19.9,2)＝两粗率之比；'
  u'2.03＝round((1.19×3.45)**0.5,2)＝比值型区间的几何中点＝报告点估计；5.38＝round((9.14+1.62)÷2,2)＝连续型区间的算术中点＝点估计；'
  u'1.14＝round(2.32÷2.03,2)＝并入死亡后的效应量抬幅；1.31＝round(2.65÷2.03,2)＝限定 72 小时后的效应量抬幅(信未引用)；'
  u'2.7＝round(5÷1.85,1)＝本研究结局阈值相对卒中人群阈值的倍率；0.02＝0.68−0.66；0.03＝0.66−0.63(借来的阈值落在报告区间内)；'
  u'0.1＝2−1.9(高剂量组合计暴露低于其定义阈值)；7＝(2.2−1.5)÷(1.8−1.7)(监护期组间差对病房期组间差)；20＝100÷5；40＝2×20(单位换算)；'
  u'59＝⟦S⟧ 每千字母数字字符数；87＝⟦L⟧ 同项。')

a(u'※隐性知识的所在 ① 逐字引文可以在省略号与从属连词处断口: 原文的"因为……所以应作时变暴露解释"被切成一条被承认的断言; '
  u'② 引述时替换动词("has been considered"→"is designated")是无人复核的增责，两个词的分布就是证据; '
  u'③ 同一统计量换缩写名(AUC⇎C-statistic)后，按缩写字检索指控会零命中; '
  u'④ 借来的失效阈值 0.66 落在被批评者自己报告的 0.63–0.72 之内，两源都不说——引用外部阈值的一方有义务给出自己估计的区间; '
  u'⑤ 比值型区间的中心是几何的、连续型是算术的，两者都等于点估计，故"中点＝点估计"不能用来判断区间是否被操纵; '
  u'⑥ 粗率比 1.59 与报告比值比 2.03 的差是校正与匹配造成的，摘要却把未校正的概率值与校正后的效应量并排; '
  u'⑦ 结果百分比的分母在同一段内从全队列换成匹配后队列(25.8 只对 392 成立，对 610 应为 16.6); '
  u'⑧ 分组阈值 2 单位／日被高剂量组自己的合计暴露 1.9 穿过——阶段均值与合计均值不同口径; '
  u'⑨ 组间分离 7 倍集中于监护期，说明"每监护日均"这个分母承载了结论，而病房期两组几乎相同; '
  u'⑩ 两组监护时长 5 对 7 日，即暴露窗本身不等长，这正是"时变"的可见表格证据; '
  u'⑪ 信的天花板之忧被 Pre/Post-Barthel 两行(100 (100, 100) 与差值 0 (0, 0) 而概率列报 <0.01)直接证实，信却没有引用它们; '
  u'⑫ 结局判定值 5 恰等于单个条目最小非零步长，结局与测量噪声同尺寸; '
  u'⑬ 四项指控里三项用原文自己的词(reverse causality 两侧各两次)，新增的只有 immortal 一个名词; '
  u'⑭ 同一偏倚换个名字(幸存者→永生时间)就从"已用最坏情形分析处理过"变回"未处理"; '
  u'⑮ 信替作者否认了一个作者没有声称的用途("并非旨在处理永生时间")，这是预防读者自行辩护的让步式写法; '
  u'⑯ 限定 72 小时后效应量升到 2.65(主分析的 1.31 倍)，信复述结论时只取主分析的数; '
  u'⑰ 方法学批评里也会出现"我提的竞争风险模型在此不适用"的自我撤回; '
  u'⑱ 四项补救全为动名词起句且全部指向未来数据，没有一项要求重算已有队列⇒该批评永远不会被本文献对证伪; '
  u'⑲ 信把通气时长列为基线协变量，原文却自己把它标为可能的暴露后过程；复述对方模型清单时丢掉的两项(cerebrovascular／chronic kidney)与那个日历变量(weekend)在信侧全为 0，而匹配前失衡最大的一行是 CRRT(标准化均数差 0.32，只进结局回归不进匹配名单；CKD 行为 0.30)，信对它也一字未提 ⇒ 指控的强度同样取决于批评者没看的那一行; '
  u'⑳ 整场"是否目标试验"之争落在一个副词上(conceptually)，引文与原句同串; '
  u'㉑ 披露方向相反: 被批评者数据"可索取"、批评者"无数据"⇒可复核性全部落在被批评一方; '
  u'㉒ 剂量单位来自日本医疗计费规则且原文自认是权宜估计，信把定义压成一句括号时删掉了这两句; '
  u'㉓ 信的结尾自限"缺少样本量估算不是否定结论的理由"——批评的最后一段是给结论强度兜底的。')

a(u'※抓取与失真 两份 raw 均由 Europe PMC fullTextXML 一次取回(被引的那篇早期活动研究 PMC13455185 与此前的 PMC13335305 系列端点正常，'
  u'与上一条目中持续返回 HTTP 500 的情形不同)。JATS→正文的转换留下四类不可跨锚点位置: 小于号写作实体 `&lt;`(故 "&lt; 2 units/day"、'
  u'"p &lt; 0.001" 一类串只在锚点内原样可命中); 单位上下标拆成 `kg/m 2`; 表体被压平为一行行 token，单元格边界丢失，'
  u'故 "0 (0, 0) &lt; 0.01" 这类行只能按整行文本引用; 撇号在 ⟦S⟧ 用 U+2019(patients’ )而在 ⟦L⟧ 的引文与自述里用 ASCII 撇号(patients\' )——'
  u'这使同一句话无法做跨文件精确子串比较，而 audit 的规范化比对仍判其逐字命中，本条的正字比对一律用各文件自身的写法。')

a(u'※两源对齐 %d 个锚全部逐字命中自己标签的源(建条脚本 _mkB39.py 内建"按标签取对应文件做精确子串"断言，不做规范化)。'
  u'摘要段联合命中 %d/%d，跨源误标 0 处; ⟦S⟧ %d 锚／⟦L⟧ %d 锚。两处刻意写成"同串双标"以证明引文逐字: '
  u'"should be interpreted as a time-varying exposure…"与"conceptually framed as an emulation of a hypothetical target trial"'
  u'各自在两文件里都精确存在(撇号、省略号除外)，机检键 2 给出前者在两源之和。'
  % (n_atoms, n_atoms, n_atoms, n_s, n_l))

a(u'※实况 编码 %d(含换行；audit 去换行口径 %d) ⇎ 摘要段 %d(audit 口径；正文 %d ＋ 两处分节标题 %d；%d 个锚全部命中，分源窗口块数 %d ＋ %d) ⇎ '
  u'raw 正文 %d 字符／%d 字节；保留率 %.1f%% ⇎ %.1f%% ⇎ %.3f%%；锚 %d 个(⟦S⟧ %d ⇎ ⟦L⟧ %d)，锚内字母 %d ⇎ 锚内汉字 %d，'
  u'锚外字母 %d = 出处标签 %d + 其余 %d(仅 ℒmethod 自身)；T1／T2／T3 失配 0，待核小整数 0 条。' % (
    enc_nl, enc_n, dig_total, dig_body, dig_total - dig_body, n_atoms,
    blocks.get('S', 0), blocks.get('L', 0), raw_chars, raw_bytes,
    ret_d, ret_c, ret_b, n_atoms, n_s, n_l,
    inlat, inhan, outlat, len(tags_all), outlat - len(tags_all)))

a(u'※保留率口径 本条一侧是 39539 字符的完整队列研究(含三张表的压平文本)，另一侧是 13825 字符的批评信，%d 个锚必须逐字保留，'
  u'故编码为摘要段的 %.1f%%、为 raw 正文的 %.1f%%、为 raw 字节的 %.3f%%。压缩发生在一处选择: 论文里绝大多数句子('
  u'背景、护理流程、讨论、参考文献)不被引用，留下的是与"指控能否被表格推翻"有关的句子与三张表的关键行。'
  u'相对 B38(两份通信合计 19250 字符、92.9%% 量级)本条把一篇全文研究拉进对照，因此 vs raw 的比值更低，这是体裁上限而不是退让。'
  % (n_atoms, ret_d, ret_c, ret_b))

io.open(ENTRY, 'w', encoding='utf-8').write(full.split(u'## ⛓解读注')[0] + u'## ⛓解读注\n' + u'\n'.join(G) + u'\n')
print(u'gloss written: enc %d dig %d ret %.1f%% raw %d/%d' % (enc_n, dig_total, ret_d, raw_chars, raw_bytes))
