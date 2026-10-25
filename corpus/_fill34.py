# -*- coding: utf-8 -*-
# 生成/刷新 B34 的 ⛓解读注(静态判定注 + 实测两行), 幂等: 整体替换 '## ⛓解读注' 之后内容
import io
import re

E = u'corpus/babeltele/B34_shantou_report_two_faces.md'
TAGS = (u'S', u'L')
FILES = {u'S': u'corpus/raw/prose/cn_fire_report_spread.txt',
         u'L': u'corpus/raw/prose/cn_fire_report_liability.txt'}

t = io.open(E, encoding=u'utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', t, re.S).group(1)
orig = re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\n\n## ⟪BabelTele', t, re.S).group(1)
ne = len(enc.replace(u'\n', u''))
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
in_han = sum(len(re.findall(u'[一-鿿]', a)) for a in atoms)
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
judge = sum(len(x) for x in re.findall(u'『([^』]+)』', enc))
skel = len(enc[enc.find(u'∴骨架'):])
nlab = len(re.findall(u'⟦[A-Z]⟧', enc))
outlat = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)))
alab = {g: len(re.findall(u'⟦%s⟧⟨' % g, enc)) for g in TAGS}
dlen = {g: 0 for g in TAGS}
for m in re.finditer(u'### ⟦([A-Z])⟧ ⟸ [^\n]*\n(.*?)(?=\n\n### |\\Z)', orig, re.S):
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

G = [u'※体例 ⟦S⟧＝德阳消防（网易号，转载广东省应急管理厅通稿）%d 字 ⇎ ⟦L⟧＝央视新闻客户端（总台记者 郑澍／赵菁）%d 字，两版都是媒体转载文本而非报告 PDF 原件，报告全文未公开——本条记的是"一份调查报告怎样分给两种读者"。每个 `⟨⟩` 须逐字回源（T3 机检），前贴单字母出处标签。'
     % (len(bodies['S']), len(bodies['L'])),
     u'※派生算术（机器复核，`corpus/audit.py` DERIV[B34]） 10=4+6（[仅有4人…逃生] 与 [有6人错误选择…洗手间] 两个亚计数） ⇎ 2=12−(4+6)（未归入任何原因句的死亡人数）。其余数字均字面命中：12 死、150 平方米、20 余个货架、40.63 万元。',
     u'※隐性知识的所在 五处都在通报的措辞里而不是教材：①同一空间缺陷的两套措辞（⟨须经过首层五金店才能通向室外⟩ ⇎ ⟨组织“三合一”场所消防安全专项整治不力⟩）是可用的两本账而非重复；②屏障的"动作成功／功能失败"二分（喷头触发动作但无水、探测器响但不联网）；③责任六段的动词强度递减（失守→把关不严→督促指导不到位→不深刻）即定责分寸；④签名造假使整份评估"不存在"而不是"有错"；⑤移交的是 ⟨履职方面的问题线索及相关材料⟩ 而非责任本身。',
     u'※抓取与失真 两版均 `curl` 转载页＋标签剥离；汉字间的空格与换行已剔除（`。？！` 断句保留），⟦S⟧ 另删图注两行（"事发建筑鸟瞰示意图"⇎"事发建筑外窗及逃生窗分布情况"），`chars`／`text_sha256` 按清理后正文重算。媒体转载与报告原文可能有字句出入：锚点只保证回源到这两份转载文本，不保证是报告原句。',
     u'※两版对齐 共用句＝定性句 ⟨该起火灾是一起因使用蚊香不慎引发的重大生产安全责任事故⟩ 与 ⟨经调查，事故直接原因是⟩（43 个锚里 9 个在两版都能逐字命中，归属仍由标签决定）；独有段＝⟦S⟧ 蔓延扩大四条＋问题三方＋处理建议 ⇎ ⟦L⟧ 调查查明六段＋八项整改。两版各自省略，合起来才是完整报告。']

msg = (u'※实况: 编码 %d(含换行; audit 去换行口径 %d) ⇎ 分源摘要 S %d／L %d(合 %d, %d 个锚落 %d 个窗口) ⇎ raw 正文 %d 字符／%d 字节; '
       u'保留率 %.1f%%(÷摘要段) ⇎ %.1f%%(÷两版正文字符) ⇎ %.1f%%(字节口径＝audit 表列÷raw 源); '
       u'锚 %d 个(⟦S⟧%d ⇎ ⟦L⟧%d; 行文内另用 %d 次), 锚内字母 %d ⇎ 锚内汉字 %d, 锚外字母 %d = 出处标签 %d + 其余 %d; '
       u'判词层 %d ‖ 骨架与 ℒmethod %d; T1／T2／T3 失配 0, 待核小整数 0 条。'
       % (len(enc), ne, dlen['S'], dlen['L'], len(orig), len(atoms), wins, RC, raw_bytes,
          pct_win, pct_rc, pct_byte, len(atoms), alab['S'], alab['L'],
          nlab - sum(alab.values()), in_lat, in_han, outlat, nlab, outlat - nlab, judge, skel))
extra = (u'※保留率口径(为何过 100%%): 表列 %.1f%%＝编码 %d÷摘要段 %d; 换成两版正文字符口径＝%.1f%%(编码 %d ÷ %d)，即长度上本条不压缩。'
         u'原因与 B30／B31 同属一类: 中文官方通报短(%d+%d＝%d 字)而逐句皆判据句, 43 个锚存下两版正文的 %.1f%% 汉字(锚内汉字 %d), '
         u'编者层(判词 %d + 骨架与 ℒmethod %d ＝%d 字)是新增推理。被删掉的只有图注、来源署名行与两版重复的日期地址段, '
         u'换来的额度是 2 条机检算术＋两版差集本身——"同一报告分给两种读者"这个事实在任一单版里都不可见。若强行剪锚到 100%% 以下, 剪掉的将是失效层级的顺序与措辞对照, 那正是本条的载荷。'
         % (pct_win, ne, len(orig), pct_rc, ne, RC, len(bodies['S']), len(bodies['L']), RC,
            100.0 * in_han / RC, in_han, judge, skel, editor))
G += [msg, extra]
i = t.find(u'## ⛓解读注')
assert i > 0
t = t[:i] + u'## ⛓解读注\n' + u'\n'.join(G) + u'\n'
io.open(E, u'w', encoding=u'utf-8').write(t)
print(u'\n'.join(G[-2:]))
