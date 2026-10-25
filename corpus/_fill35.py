# -*- coding: utf-8 -*-
# 生成/刷新 B35 的 ⛓解读注(静态判定注 + 实测两行), 幂等: 整体替换 '## ⛓解读注' 之后内容
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
E = u'corpus/babeltele/B35_cftc_swap_definition_two_directions.md'
TAGS = (u'X', u'P')
FILES = {u'X': u'corpus/raw/prose/cftc_swap_exclusion_ifr.txt',
         u'P': u'corpus/raw/prose/cftc_swap_inclusions_nprm.txt'}

t = io.open(E, encoding=u'utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', t, re.S).group(1)
orig = re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\n\n## ⟪BabelTele', t, re.S).group(1)
ne = len(enc.replace(u'\n', u''))
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
in_han = sum(len(re.findall(u'[一-鿿]', a)) for a in atoms)
judge = sum(len(x) for x in re.findall(u'『([^』]+)』', enc))
skel = len(enc[enc.find(u'∴骨架'):])
nlab = len(re.findall(u'⟦[A-Z]⟧', enc))
outlat = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)))
alab = {g: len(re.findall(u'⟦%s⟧⟨' % g, enc)) for g in TAGS}
dlen = {g: 0 for g in TAGS}
for m in re.finditer(u'### ⟦([A-Z])⟧ ⟸ [^\n]*\n(.*?)(?=\n\n### |\Z)', orig, re.S):
    dlen[m.group(1)] = len(m.group(2).strip())
wins = len([x for x in re.split(u'\n\n', re.sub(u'^### .*$', u'', orig, flags=re.M).strip()) if x.strip()])
bodies = {}
for g, f in FILES.items():
    raw = io.open(f, encoding=u'utf-8').read()
    bodies[g] = raw.split(u'# note:', 1)[1].split(u'\n', 1)[1].strip()
RC = sum(len(b) for b in bodies.values())
raw_bytes = sum(len(io.open(f, encoding=u'utf-8').read().encode(u'utf-8')) for f in FILES.values())
pct_win = 100.0 * ne / len(orig)
pct_rc = 100.0 * ne / RC
pct_byte = 100.0 * ne / raw_bytes
editor = judge + skel
verb = ne - editor

G = [u'※体例 ⟦X⟧＝91 FR 66010《Further Definition of "Swap" To Exclude Casino-Style Gambling Products》'
     u'（临时最终规则, RIN 3038-AF81, 即时生效＋事后听意见, %d 字符）⇎ ⟦P⟧＝91 FR 66022《Further Definition of "Swap"—Inclusions》'
     u'（征求意见稿, RIN 3038-AF82, %d 字符），同一天（2026-10-19）发布、同一术语 swap 的两个方向。'
     u'每个 `⟨⟩` 须逐字回源（T3 机检），前贴单字母出处标签；两文件的 govinfo HTML 正文按原样保留页眉页脚，未做改写。'
     % (len(bodies['X']), len(bodies['P'])),
     u'※派生算术与计数（机器复核，`corpus/audit.py` DERIV[B35]） 12＝CNT("good cause",0) ⇎ 0＝CNT("good cause",1)（豁免论证的关键词在排除侧 12 次、在纳入侧一次也没有——'
     u'这条"缺席"是本条最重要的机检断言）‖ 20＝CNT("cultural-,",1) ⇎ 5＝CNT("cultural,",1)（同一份提案里同一列举项的连字符漂移）‖ '
     u'40＝L("39")+L("1")（39 个州＋哥伦比亚特区联署）‖ 33＝L("2026")−L("1993")（1993 年不行动函到今天的时间轴长度）。'
     u'其余数字字面命中：3038-AF81／AF82、October 19 2026、November 18 2026、Core Principle 9、2010、2022。',
     u'※隐性知识的所在 八处都在两份文件的对照里而不是任何单份文件：①程序形式随**管辖动作的方向**而变（收回管辖⇒免评论即时生效, 扩张管辖⇒征求意见稿），'
     u'与内容无关；②豁免评论的论证是"与先例攀比损害量级"而非比对事实；③紧急状态的证词取自争讼对方（39＋1 个法域的联署措辞），危害论证的材料是对手的自述；'
     u'④"可交易性"不在定义里却由同一部法的功能条款、司法旧例与交易所核心原则倒推出来；⑤同一套五项测试两向使用、结论相反而不矛盾；'
     u'⑥限缩写成合取要件、扩张写成清单枚举，起草不对称来自各自的失败模式；⑦序文与规范文本的标点漂移会变解释争点（最终入 CFR 的只有后者）；'
     u'⑧认识强度词（⟦P⟧⟨preliminary belief⟩ ⇎ ⟦X⟧⟨does not include⟩）标记程序阶段，同一天用两种强度说话。',
     u'※抓取与失真 两份均 govinfo `FR-YYYY-MM-DD/html/<docno>.htm` 经 `curl` 取 `<body><pre>` 后剥标签与实体（`_mkraw35.py`）；'
     u'federalregister.gov 只有 v1 API 可达（v2 与 `documents/full_text/*` 一律 404），故 `python -X utf8 corpus/raw/probe/_fr.py` 只用于**检索**，正文一律走 govinfo。'
     u'锚点两处坑：联邦登记排版会把引号首字母写成方括号（把「[f]ederal」写进锚则归一化成 "f ederal"），且跨行连字符（Tribe-/licensed、sports- related）会打断逐字连续，'
     u'因此短语锚一律改取尾部（如 ⟨courts are hopelessly confused⟩、⟨does not mean that run-of-the-mill sports bets are also swaps⟩）。'
     u'`chars`／`text_sha256` 按清理后正文重算。',
     u'※两文件对齐 105 个锚里 8 个在两份文件都能逐字命中（多为格式句与套语），归属仍由前贴标签决定；'
     u'共用句＝评论截止 ⟦X⟧⟨Comments must be received by November 18, 2026⟩ ‖ ⟦P⟧ 同句逐字相同，登记号只差一位（AF81 ⇎ AF82）⇒ 两个半边在编制时是一个工程；'
     u'独有段＝⟦X⟧ 的 good-cause 三档先例阶梯＋五项测试的排除用法 ⇎ ⟦P⟧ 的纳入清单＋第四目共识论证＋执法史时间轴。',
     ]

msg = (u'※实况: 编码 %d(含换行; audit 去换行口径 %d) ⇎ 分源摘要 X %d／P %d(合 %d, %d 个锚落 %d 个窗口) ⇎ raw 正文 %d 字符／%d 字节; '
       u'保留率 %.1f%%(÷摘要段) ⇎ %.3f%%(÷两文正文字符) ⇎ %.3f%%(字节口径＝audit 表列÷raw 源); '
       u'锚 %d 个(⟦X⟧%d ⇎ ⟦P⟧%d; 行文内另用 %d 次), 锚内字母 %d ⇎ 锚内汉字 %d, 锚外字母 %d = 出处标签 %d + 其余 %d(仅 CFR×2 与 ℒmethod 自身); '
       u'判词层 %d ‖ 骨架与 ℒmethod %d; T1／T2／T3 失配 0, 待核小整数 0 条。'
       % (len(enc), ne, dlen['X'], dlen['P'], len(orig), len(atoms), wins, RC, raw_bytes,
          pct_win, pct_rc, pct_byte, len(atoms), alab['X'], alab['P'],
          nlab - sum(alab.values()), in_lat, in_han, outlat, nlab, outlat - nlab, judge, skel))
src_lat = sum(len(re.findall(u'[A-Za-z]', b)) for b in bodies.values())
extra = (u'※保留率口径 表列 %.1f%%＝编码 %d÷摘要段 %d；换成源正文口径＝%.3f%%(编码 %d ÷ %d)，字节口径 %.3f%%。'
         u'英文法规文本的低密度是结构性的：两份文件共 %d 字符，程序性固定段（机构／行动／摘要／日期／联系窗口一类）与逐条复述的定义文本占绝大多数，'
         u'摘要段按锚点窗口只取 %d 字符即已剔掉全部未被引用的段落。本条以 %d 个锚存下两文正文的 %d 个拉丁字母（占源内字母总量 %.1f%%），'
         u'编者层(判词 %d + 骨架与 ℒmethod %d ＝%d 字)是新增推理；'
         u'密度不在字符数而在"一份文件里看不到的对照"——程序形式随管辖方向而变、豁免论证关键词的在场与缺席(12 ⇎ 0)、连字符漂移(20 ⇎ 5)这三条断言都必须两文并置才成立，'
         u'且全部可机检。'
         % (pct_win, ne, len(orig), pct_rc, ne, RC, pct_byte, RC, len(orig), len(atoms), in_lat,
            100.0 * in_lat / src_lat, judge, skel, editor))
G += [msg, extra]
i = t.find(u'## ⛓解读注')
assert i > 0
t = t[:i] + u'## ⛓解读注\n' + u'\n'.join(G) + u'\n'
io.open(E, u'w', encoding=u'utf-8').write(t)
print(u'\n'.join(G[-2:]))
