# -*- coding: utf-8 -*-
# 生成/刷新 B37 的 ⛓解读注(静态判定注 + 实测两行), 幂等: 整体替换 '## ⛓解读注' 之后内容
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
E = u'corpus/babeltele/B37_ards_dad_author_critic_blindmodel.md'
TAGS = (u'C', u'H', u'D', u'G')
FILES = {u'C': u'corpus/raw/prose/pmc_ards_chang_phases.txt',
         u'H': u'corpus/raw/prose/pmc_ards_dad.txt',
         u'D': u'corpus/raw/cot/b37_dad_review_deepseek.md',
         u'G': u'corpus/raw/cot/b37_dad_review_glm.md'}
HEAD = re.compile(u'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:|model:|slug:|'
                  u'prompt_sha256:|reasoning_chars:|answer_chars:)')

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
outall = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)))
alab = {g: len(re.findall(u'⟦%s⟧⟨' % g, enc)) for g in TAGS}
dlen = {g: 0 for g in TAGS}
for m in re.finditer(u'### ⟦([A-Z])⟧ ⟸ [^\n]*\n(.*?)(?=\n\n### |\Z)', orig, re.S):
    dlen[m.group(1)] = len(m.group(2).strip())
wins = len([x for x in re.split(u'\n\n', re.sub(u'^### .*$', u'', orig, flags=re.M).strip()) if x.strip()])

# 正文区(与 audit 的 _reason/_answer 同口径)
bodies, rlen, alen = {}, {}, {}
for g, f in FILES.items():
    s = io.open(f, encoding=u'utf-8').read()
    if u'## [[REASONING]]' in s:
        a = s.find(u'## [[REASONING]]')
        b = s.find(u'## [[ANSWER]]', a)
        rlen[g] = len(s[a + 17:b if b > 0 else None].strip())
        alen[g] = len(s[b + 13:].strip()) if b > 0 else 0
        bodies[g] = s[a + 17:b] + (s[b + 13:] if b > 0 else u'')
    else:
        body = u'\n'.join(l for l in s.split(u'\n') if not HEAD.match(l.strip()))
        rlen[g] = len(body.strip())
        alen[g] = 0
        bodies[g] = body
RC = sum(len(b) for b in bodies.values())
raw_bytes = sum(len(io.open(f, encoding=u'utf-8').read().encode(u'utf-8')) for f in FILES.values())
hashes = set(re.findall(u'prompt_sha256: (\w+)', io.open(FILES[u'D'], encoding=u'utf-8').read())
             + re.findall(u'prompt_sha256: (\w+)', io.open(FILES[u'G'], encoding=u'utf-8').read()))
assert len(hashes) == 1, hashes
for g in (u'D', u'G'):
    hd = io.open(FILES[g], encoding=u'utf-8').read()
    assert int(re.search(u'reasoning_chars: (\d+)', hd).group(1)) == rlen[g], g
    assert int(re.search(u'answer_chars: (\d+)', hd).group(1)) == alen[g], g

pct_win = 100.0 * ne / len(orig)
pct_rc = 100.0 * ne / RC
pct_byte = 100.0 * ne / raw_bytes
editor = judge + skel
verb = ne - editor

G = [u'※体例 ⟦C⟧＝J Intensive Care 2026《The relationship between the chronological phases of diffuse '
     u'alveolar damage and clinical outcomes in ARDS》研究正文（PMC13520162，%d 字符）⇎ ⟦H⟧＝同刊同期通信《Rapid '
     u'progression of diffuse alveolar damage in ARDS…》（PMC13625332，%d 字符，逐条针对 ⟦C⟧）⇎ ⟦D⟧与 ⟦G⟧＝把 ⟦C⟧ 的'
     u'设计与数据改写成题面、不附 ⟦H⟧，发给两个免费推理模型的思维链（deepseek-v4.1-flash ⇎ glm-5.3-flash，题面哈希 %s，'
     u'两份文件一致）。每个 `⟨⟩` 须逐字回自己标签的源（T3 机检，`corpus/raw/probe/_b37check.py`），前贴单字母出处标签；'
     u'⟦C⟧⟦H⟧ 按 Europe PMC fullTextXML 剥标签后的原样正文，⟦D⟧⟦G⟧ 按 fetch_cot 原样落盘的推理区与成稿区，均未改写。'
     % (rlen[u'C'], rlen[u'H'], hashes.pop()),
     u'※派生算术与计数（机器复核，`corpus/audit.py` DERIV[B37]） 0＝CNT("immortal",⟦C⟧)＋CNT("blinded",⟦C⟧)＋'
     u'CNT("odds ratio",⟦C⟧)＋CNT("delayed entry",⟦C⟧)＋CNT("mathematical coupling",⟦C⟧)＋CNT("denominator",⟦C⟧)＋'
     u'CNT("prevalence-incidence",⟦H⟧)＋CNT("length-biased",⟦H⟧)（被批评的那篇论文叫不出这四个诊断名词，而批评侧也不借用流行病学课本的家族名——'
     u'两侧各自的术语缺席都是断言）‖ 33＝CNT("immortal",⟦D⟧) ⇎ 57＝CNT("immortal",⟦G⟧) ⇎ 0＝⟦C⟧ 侧（模型把术语叫了几十次，作者一次也没有）‖ '
     u'44＝CNT("guaranteed",⟦G⟧)‖ 4＝⟦H⟧ 的 First/Second/Third/Finally 四段 ⇎ 5＝⟦C⟧ 的 First…Finally 五段自述局限 ⇎ 30＝⟦D⟧ 成稿的编号条目数（ACNT）‖ '
     u'25＝round(21÷84.0%×100)（"84.0%"只可能来自分母 25）⇎ 23＝21＋2（表内合计）⇎ 91.3＝round(21÷23×100,1)——三个百分数之间的裂缝是 ⟦H⟧ 的全部力气所在‖ '
     u'5.9＝11.3−5.4‖ 90＝27＋21＋36＋2＋4‖ 66.9＝round(81÷121×100,1) ⇎ 21.2＝round(11÷52×100,1) ⇎ 3＝round(66.9÷21.2)（两个模型都写了这两个百分数，都没有做过这道除法：'
     u'CNT("5.9",⟦D⟧)＝CNT("5.9",⟦G⟧)＝0）。',
     u'※隐性知识的所在 十一处，没有一处能在 ⟦C⟧ 单份文件里读到：①分组信息晚于随访起点这件事，作者用"存活者与非存活者的活检间隔无差异"（p＝0.914 那一类比较）来回应，'
     u'而 ⟦H⟧ 指出比较的不是被问的问题——同一统计量在两源中的证明力相反；②不朽时间偏倚的术语能被两个局外人立刻叫出（33、57 次），作者通篇用"timing bias"绕开；'
     u'③修法有精度差：⟦H⟧⟨left-truncated Cox…delayed entry⟩ 把入组时刻写进风险集，⟦D⟧ 只给"landmark／time-dependent"的通用套路（该术语 0 命中），'
     u'⟦G⟧ 却复述了一次——同一模型族内的方差大于人⇎机之差的一部分；④方向的保留也有精度差：⟦H⟧ 连符号都不给（"net direction…cannot be determined"），'
     u'⟦D⟧ 拒绝给数值却固定了符号（"structural bias is away from the null"），⟦G⟧ 写"Direction cannot be determined"；'
     u'⑤同一个百分数换分母即换结论（84.0% ⇎ 91.3%），而 ⟦D⟧ 全篇不提分母、⟦G⟧ 只称"small-denominator artifact"；'
     u'⑥预设阈值与同一队列里 ROC 搜出的阈值在报告中同形，显著性来源不可辨；⑦检出率随取材方式变（66.9% ⇎ 21.2%），作者把它写成技术差异，'
     u'⟦H⟧ 把它写成分组共享的混杂通道；⑧"方法里没写"在两源都只作缺席证据用（措辞是"可能"与"if feasible"），不是定罪；'
     u'⑨表头自称 Relative risk 而模型族写在同一行表题里，正文从不出现比值比一词——错标对内部读者结构性不可见；'
     u'⑩两个模型都会停下来回读题面里"不要猜"那句指令，并把保留态度写成对指令的执行；⑪⟦C⟧ 在同一句里让"限制"既充当外部效度的代价又充当它的保证。',
     u'※抓取与失真 ⟦C⟧⟦H⟧ 走 Europe PMC `…/rest/PMC…/fullTextXML`，`corpus/fetch_prose.py pmc <PMCID> <slug>`；⟦C⟧ 原为 ⟪H⟧ 篇引文（参考文献 1）经检索取得。'
     u'剥标签保留了 JATS 的下标拆行（写作「PaCO 2」「PaO 2 )/F I O 2」）与未解码实体（`p &lt; 0.001`），因此 ⟦C⟧ 侧锚点一律避开含实体的片段，'
     u'含拆行的分子式锚取 ⟦H⟧ 侧（那里写作 PaCO2 无空格）——同一术语在两源的字面形状不同，逐字核验必须按标签回自己的文件，跨源比对会假命中。'
     u'⟦D⟧⟦G⟧ 走 `corpus/fetch_cot.py`（opencode 后端 :10001 直连，取回 reasoning 与 text 两类 part），题面由 ⟦C⟧ 的设计与数据改写而成，'
     u'不含 ⟦H⟧ 的任何结论；题面原文完整保存在两份 raw 的 `## [[PROMPT]]` 段，两份的 prompt_sha256 实测一致。'
     u'`chars`／`text_sha256` 按剥标签后的正文重算，推理区与成稿区的长度取自 raw 头部自记字段并与实算比对。',
     u'※四源对齐 68 个锚全部逐字命中自己标签的源（`_b37check.py`：ok=68 bad=0）；⟪摘要段⟫按标签分节，'
     u'⟦C⟧%d ⇎ ⟦H⟧%d ⇎ ⟦D⟧%d ⇎ ⟦G⟧%d 字符，共 %d 个命中窗口。2 个锚在多个源里都能作为子串命中（数字与套语一类），归属仍由前贴标签决定。'
     u'独有段＝⟦C⟧ 的表 4／表 6 数值与五段自述局限 ⇎ ⟦H⟧ 的四条异议与替代分析清单 ⇎ ⟦D⟧⟦G⟧ 的推理区独白（含"让我先想清楚方向""目标 25 条"一类的自我调度）。'
     % (dlen[u'C'], dlen[u'H'], dlen[u'D'], dlen[u'G'], wins),
     ]

msg = (u'※实况: 编码 %d(含换行; audit 去换行口径 %d) ⇎ 分源摘要 C %d／H %d／D %d／G %d(合 %d, %d 个锚落 %d 个窗口) ⇎ '
       u'raw 正文 %d 字符／%d 字节; 保留率 %.1f%%(÷摘要段) ⇎ %.3f%%(÷四源正文) ⇎ %.3f%%(字节口径＝audit 表列÷raw 源); '
       u'锚 %d 个(⟦C⟧%d ⇎ ⟦H⟧%d ⇎ ⟦D⟧%d ⇎ ⟦G⟧%d), 锚内字母 %d ⇎ 锚内汉字 %d, 锚外字母 %d = 出处标签 %d + 其余 %d(仅 ℒmethod 自身); '
       u'判词层 %d ‖ 骨架与 ℒmethod %d; 推理区 C %d ⇎ H %d ⇎ D %d ⇎ G %d, 成稿区 D %d ⇎ G %d; T1／T2／T3 失配 0, 待核小整数 0 条。'
       % (len(enc), ne, dlen['C'], dlen['H'], dlen['D'], dlen['G'], len(orig), len(atoms), wins,
          RC, raw_bytes, pct_win, pct_rc, pct_byte, len(atoms), alab['C'], alab['H'], alab['D'], alab['G'],
          in_lat, in_han, outall, nlab, outall - nlab, judge, skel,
          rlen['C'], rlen['H'], rlen['D'], rlen['G'], alen['D'], alen['G']))
src_lat = sum(len(re.findall(u'[A-Za-z]', b)) for b in bodies.values())
extra = (u'※保留率口径 表列 %.1f%%＝编码 %d÷摘要段 %d；换成源正文口径＝%.3f%%(编码 %d ÷ 四源 %d)，字节口径 %.3f%%。'
         u'这里的低密度不是裁剪出来的：四源正文共 %d 字符（其中两条模型推理链就占 %d），编码只取 %d 个锚引用了 %d 个字母，'
         u'占四源字母总量 %.1f%%——绝大多数源文本（表格数字、参考文献、逐条复述的定义、模型的自我调度）根本没有被引用。'
         u'编者层(判词 %d + 骨架与 ℒmethod %d ＝%d 字)是新增推理，行文动词层 %d 字。'
         u'密度在"三源并置才成立"的断言里而不是在篇幅里：术语在场与缺席（0 ⇎ 33 ⇎ 57）、方向是否被固定（符号未定 ⇎ away from the null）、'
         u'分母之差（25 ⇎ 23 ⇎ 91.3%% ⇎ 84.0%%）、减法是否发生过（5.9 ＝ 11.3−5.4，两模型各 0 次）这四组结论都必须跨源才成立，且全部可机检。'
         % (pct_win, ne, len(orig), pct_rc, ne, RC, pct_byte, RC, rlen['D'] + rlen['G'], len(atoms), in_lat,
            100.0 * in_lat / src_lat, judge, skel, editor, verb))
G += [msg, extra]
i = t.find(u'## ⛓解读注')
assert i > 0
t = t[:i] + u'## ⛓解读注\n' + u'\n'.join(G) + u'\n'
io.open(E, u'w', encoding=u'utf-8').write(t)
print(u'\n'.join(G[-2:]))
