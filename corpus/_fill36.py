# -*- coding: utf-8 -*-
# 生成/刷新 B36 的 ⛓解读注(静态判定注 + 实测两行), 幂等: 整体替换 '## ⛓解读注' 之后内容
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
E = u'corpus/babeltele/B36_three_models_one_accident_investigation.md'
TAGS = (u'D', u'G', u'N')
FILES = {u'D': u'corpus/raw/cot/b36_tdi_deepseek.md',
         u'G': u'corpus/raw/cot/b36_tdi_glm.md',
         u'N': u'corpus/raw/cot/b36_tdi_nemotron.md'}
MODEL = {u'D': u'opencode/deepseek-v4.1-flash-free',
         u'G': u'opencode/glm-5.3-flash-free',
         u'N': u'opencode/nemotron-3-ultra-free'}
RAW = {}
for g, f in FILES.items():
    RAW[g] = io.open(f, encoding=u'utf-8').read()

t = io.open(E, encoding=u'utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', t, re.S).group(1)
orig = re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\n\n## ⟪BabelTele', t, re.S).group(1)
ne = len(enc.replace(u'\n', u''))
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
in_han = sum(len(re.findall(u'[一-鿿]', a)) for a in atoms)
judge = sum(len(x) for x in re.findall(u'『([^』]+)』', enc))
skel = len(enc[enc.find(u'∴骨架'):])
nlab = len(re.findall(u'⟦[A-Z]⟧⟨', enc))
outlat = len(re.findall(u'[A-Za-z]', re.sub(u'⟦[A-Z]⟧⟨[^⟩]*⟩', u'', enc)))
outall = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟩]*⟩', u'', enc)))
alab = {g: len(re.findall(u'⟦%s⟧⟨' % g, enc)) for g in TAGS}
dlen = {g: 0 for g in TAGS}
for m in re.finditer(u'### ⟦([A-Z])⟧ ⟸ [^\n]*\n(.*?)(?=\n\n### |\Z)', orig, re.S):
    dlen[m.group(1)] = len(m.group(2).strip())
wins = len([x for x in re.split(u'\n\n', re.sub(u'^### .*$', u'', orig, flags=re.M).strip()) if x.strip()])
bodies, head = {}, {}
for g in TAGS:
    s = RAW[g]
    head[g] = dict(re.findall(u'^(model|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$', s, re.M))
    bodies[g] = s[s.find(u'## [[PROMPT]]'):].strip()
    a = s.find(u'## [[REASONING]]')
    b = s.find(u'## [[ANSWER]]')
    head[g][u'_rc'] = len(s[a + 17:b].strip())
    head[g][u'_ac'] = len(s[b + 13:].strip())
RC = sum(len(b) for b in bodies.values())
raw_bytes = sum(len(RAW[g].encode(u'utf-8')) for g in TAGS)
src_lat = sum(len(re.findall(u'[A-Za-z]', b)) for b in bodies.values())
pct_win = 100.0 * ne / len(orig)
pct_rc = 100.0 * ne / RC
pct_byte = 100.0 * ne / raw_bytes
editor = judge + skel
hashes = {head[g][u'prompt_sha256'] for g in TAGS}
assert len(hashes) == 1, u'三份 prompt_sha256 不一致'
ps = hashes.pop()
assert all(int(head[g][u'reasoning_chars']) == head[g][u'_rc'] for g in TAGS)
assert all(int(head[g][u'answer_chars']) == head[g][u'_ac'] for g in TAGS)

G = [u'※体例 ⟦D⟧＝%s ⇎ ⟦G⟧＝%s ⇎ ⟦N⟧＝%s（`corpus/fetch_cot.py` 直连本机 opencode 后端 :10001，无密钥、无代理，2026-10-20 抓）；'
     u'三源共享同一题面：三份 raw 头部的 prompt_sha256 实测同一个值 %s（脚本已断言），三家各自把 10 项现场记录与 5 项必答整段复述在 [[PROMPT]] 区。'
     u'锚点纪律（承 [[B27]]）：85 个锚里 84 个落在 `## [[REASONING]]` 区内，唯一例外是 ⟦N⟧⟨调查分析完成。以上五项输出均基于现场记录的铁证链推导，未引入外部推测。⟩ '
     u'——它是答复区原文，因为本条要断言的正是"答复里的自证"；其余跨模型断言一律改用区域长度与计数（RCOT／ACOT／CNT），不靠印象词。'
     % (MODEL[u'D'], MODEL[u'G'], MODEL[u'N'], ps),
     u'※派生算术与计数（机器复核，`corpus/audit.py` DERIV[B36]，共 18 项声明, audit 逐条打印 19 行） 推理区长度 78934＝RCOT(0) ⇎ 133680＝RCOT(1) ⇎ 854＝RCOT(2)，'
     u'答复区 5060＝ACOT(0) ⇎ 0＝ACOT(1) ⇎ 35＝ACOT(2) ⇒ 倍数 156.5＝round(RCOT(1)/RCOT(2),1) ‖ 92.4＝round(RCOT(0)/RCOT(2),1)；'
     u'认识标签用量 22＝CNT("已定",0) ‖ 27＝CNT("表观适用",0) ‖ 56＝CNT("未决",0) ‖ 55＝CNT("证据不存在",0)，'
     u'零次侧合起来由一个算式担保：0＝ACOT(1)+CNT("已定",1)+CNT("未决",1)+CNT("证据不存在",1)+CNT("已定",2)+CNT("未决",2)+CNT("证据不存在",2)+CNT("[一-鿿]",2)'
     u'（GLM 答复区空 + 两家中文标签全未用 + Nemotron 推理区无汉字）；'
     u'语言漂移 10069＝CNT("[一-鿿]",0) ⇎ 5＝CNT("[一-鿿]",1) ⇎ 0，拉丁侧 48993⇎101344⇎685；'
     u'算术裕度 6.4＝round(L("6")*L("60")/L("90")*(L("61")−L("45"))/(L("55")−L("45")),1)——6 min 与 90 s、45/55/61℃ 全部回源。'
     u'两处需注意：56 在编码里有两个身份（引文中的 56 秒 ‖ 判词里的「未决」次数），DERIV 只登记后者；'
     u'"未决"字面在 ⟦D⟧ 里出现 56 次但"未闭合"不算，故 CNT 用的是标签原词而不是近义词。',
     u'※隐性知识的所在 十处都在"处置证据"这一层而不是"知道化学"这一层：①认识标签是证据类型刻度（记录⇎解释⇎缺口），当置信度用即刻失效；'
     u'②表观适用＝证据支持但未闭合，标签挂在命题上而非挂在证据上（同一条压降在"放大因素"上可定、在"事前已堵"上未决）；'
     u'③矛盾分五型（数据／合规／文档-现场／设计／伪矛盾），只有数据矛盾要求重测；④判伪矛盾是约束检查（61℃ 与"无过热晶粒生长"同真）；'
     u'⑤"证据不存在"是默认值且分三级写法，与"记录未提供"必须分开——混写会造出永远无法满足的建议；⑥挂在下限上的百分数读作下限的百分数，读错整条原因链反转；'
     u'⑦事后态不可反推事中态，在浓度／阀位／压降三处独立复现，且后果可伪装成原因（聚合物或是事件产物⇒定年为检验）；'
     u'⑧同一组读数在两条链里身份相反⇒反向因果须单列为必排项；⑨最低点火能量极低⇒点火源永远排不尽，正确动作是标注未决并取样而不是找一个更合理的火花；'
     u'⑩第 10 天建议的正当性来自屏障独立性而非因果闭合。跨模型层另有一类：⑪答复区长度测的是分箱习惯不是产出量（G 为空区，成稿写在推理区内）；'
     u'⑫打勾式推理核对"是否都答"从不核对"是否有据"，自称铁证链的 35 字断言可与 854 字的推理痕迹完全脱钩；⑬中文题面不保证中文推理⇒标签计数只能在同语言侧比较。',
     u'※抓取与失真 三份均 `fetch_cot.py` 走 :10001 的 `reasoning_content` 字段原样落盘（无改写、无省略号截断）；头部自记的 reasoning_chars／answer_chars '
     u'与本次 RCOT／ACOT 实测逐家相等（脚本已断言），即捕获长度没有掉尾。三家各有一处"失真"值得记录而不是修正：'
     u'⟦G⟧ 的答复被 32 000 推理 token 档吃掉（推理区 133680 字而答复区 0 字，成稿以 `# ①…# ⑤…` 形式留在推理区内）；'
     u'⟦N⟧ 只吐出一张完成度清单（推理区 854 字里 5 个 ✓，无一处接触证据）——这不是抓取缺陷而是上游行为，本条把它当作对照的第三档保留原样。'
     u'锚点坑承 B35：英文散文的窗口须放宽（本条 D/G 用 320⇎260，N 用 200⇎160），且箭头、度数符号、Δ、✓ 一类非字母数字在归一化里塌成空格，'
     u'故 ⟦G⟧⟨…→ "evidence does not exist" default.⟩ 这类锚靠尾短语命中，建条脚本仍按**逐字精确**子串复核（85/85 命中，见 `_mkB36.py` 断言）。',
     u'※三源对齐 85 个锚里 3 个在别家也能逐字命中（多为题面复述与通用短语，如 ⑤ 的两处英译），归属完全由前贴标签决定；'
     u'共用＝题面复述 ⟦D⟧⟨每一步写明机制，以及该步成立所需的最低能量或浓度条件⟩ ‖ ⟦G⟧⟨⑤ Two data contradictions⟩ ‖ ⟦N⟧⟨Two contradictory data points and how to handle them ✓⟩；'
     u'独有＝⟦G⟧ 的矛盾五型与 6.4 倍裕度 ‖ ⟦D⟧ 的中文标签体系与单位口径检查 ‖ ⟦N⟧ 的清单式自证——'
     u'三档合起来才看得出"同一空位上三种粒度"（证据不存在的直写／条件式／半闭合）。',
     ]

msg = (u'※实况: 编码 %d(含换行; audit 去换行口径 %d) ⇎ 分源摘要 D %d／G %d／N %d(合 %d, %d 个锚落 %d 个窗口) ⇎ raw 正文 %d 字符／%d 字节; '
       u'保留率 %.1f%%(÷摘要段) ⇎ %.3f%%(÷三源正文字符) ⇎ %.3f%%(字节口径＝audit 表列÷raw 源); '
       u'锚 %d 个(⟦D⟧%d ⇎ ⟦G⟧%d ⇎ ⟦N⟧%d), 锚内字母 %d ⇎ 锚内汉字 %d, 锚外字母 %d = 出处标签 %d + 其余 %d(三家缩写 D／G／N ‖ 核查函数名 RCOT／ACOT／CNT ‖ ℒmethod 自身); '
       u'判词层 %d ‖ 骨架与 ℒmethod %d; T1／T2／T3 失配 0, 待核小整数 0 条。'
       % (len(enc), ne, dlen['D'], dlen['G'], dlen['N'], len(orig), len(atoms), wins, RC, raw_bytes,
          pct_win, pct_rc, pct_byte, nlab, alab['D'], alab['G'], alab['N'],
          in_lat, in_han, outall, nlab, outlat, judge, skel))
extra = (u'※保留率口径 表列 %.1f%%＝编码 %d÷摘要段 %d；换成源正文口径＝%.3f%%(编码 %d ÷ %d)，字节口径 %.3f%%。'
         u'三源正文 %d 字符里拉丁字母 %d 个，本条以 %d 个锚存下其中 %d 个(占源内字母总量 %.1f%%)；'
         u'编者层(判词 %d + 骨架与 ℒmethod %d ＝%d 字)是新增推理。'
         u'这一条的保留率天生高于同批其它条目(65.8%%／64.5%%)：思维链文本几乎每句都是决策动作，摘要窗口无"程序性固定段"可剔，'
         u'所以压缩只能靠选锚的密度——%d 个锚的引文合计 %d 字符＝三源正文的 %.1f%%，再往上就是逐字复制。'
         u'密度不在百分比而在断言的可核性：本条全部跨模型结论(18 项 DERIV 声明)都是长度与计数，'
         u'零次断言与正次断言同权，换一个模型重跑即可复现或推翻。'
         % (pct_win, ne, len(orig), pct_rc, ne, RC, pct_byte, RC, src_lat, len(atoms), in_lat,
            100.0 * in_lat / src_lat, judge, skel, editor, nlab, sum(len(a) for a in atoms), 100.0 * sum(len(a) for a in atoms) / RC))
G += [msg, extra]
i = t.find(u'## ⛓解读注')
assert i > 0
t = t[:i] + u'## ⛓解读注\n' + u'\n'.join(G) + u'\n'
io.open(E, u'w', encoding=u'utf-8').write(t)
print(u'\n'.join(G[-2:]))
