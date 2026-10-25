# -*- coding: utf-8 -*-
# 回填 B32 的 ※实况 与 ※保留率口径(全部实测)
import io
import re

E = u'corpus/babeltele/B32_csrc_market_manipulation_inference.md'
t = io.open(E, encoding=u'utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', t, re.S).group(1)
orig = re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\n\n## ⟪BabelTele', t, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
in_han = sum(len(re.findall(u'[一-鿿]', a)) for a in atoms)
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
judge = sum(len(x) for x in re.findall(u'『([^』]+)』', enc))
skel = len(enc[enc.find(u'∴骨架'):])
tags = {g: len(re.findall(u'⟦%s⟧' % g, enc)) for g in 'NOK'}
nlab = len(re.findall(u'⟦[A-Z]⟧', enc))
outlat = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', '', enc)))
wins = len([x for x in re.split(u'\n\n', re.sub(u'^### .*$', u'', orig, flags=re.M).strip()) if x.strip()])
dlen = {}
for m in re.finditer(u'### ⟦([A-Z])⟧ ⟸ [^\n]*\n(.*?)(?=\n\n### |\\Z)', orig, re.S):
    dlen[m.group(1)] = len(m.group(2).strip())

FILES = (u'corpus/raw/prose/cn_csrc_manipulation_fourmen.txt',
         u'corpus/raw/prose/cn_csrc_manipulation_tenmen.txt',
         u'corpus/raw/prose/cn_csrc_fake_info_lurunkai.txt')
bodies = [io.open(f, encoding=u'utf-8').read().split(u'# note:', 1)[1].split(u'\n', 1)[1].strip()
          for f in FILES]
raw_all = u''.join(io.open(f, encoding=u'utf-8').read() for f in FILES)
raw_bytes = sum(len(io.open(f, encoding=u'utf-8').read().encode(u'utf-8')) for f in FILES)
RC = sum(len(b) for b in bodies)
# 三源共用的模板段(缴款·备案·复议·诉讼·不停止执行)所占字数
TAIL = u'具体缴款方式见本处罚决定书所附说明'
tpl = 0
for b in bodies:
    i = b.find(u'上述当事人应自收到本处罚决定书之日起15日内')
    if i >= 0:
        tpl += len(b[i:])
ne = len(enc.replace(u'\n', u''))
pct_win = 100.0 * ne / len(orig)
pct_rc = 100.0 * ne / RC
pct_all = 100.0 * ne / len(raw_all)
pct_byte = 100.0 * ne / raw_bytes

alab = {g: len(re.findall(u'⟦%s⟧⟨' % g, enc)) for g in 'NOK'}
msg = (u'※实况: 编码 %d(含换行; audit 去换行口径 %d) ⇎ 分源摘要 N %d／O %d／K %d(合 %d, %d 个锚只落 %d 个窗口) ⇎ raw 正文 %d 字符／含出处头 %d 字符／%d 字节; '
       u'保留率 %.1f%%(vs 摘要段) ⇎ %.1f%%(vs raw 正文字符) ⇎ %.1f%%(vs 含头字符) ⇎ %.1f%%(字节口径＝audit 表列 vs raw源); '
       u'锚 %d 个,每个自带出处标签(⟦N⟧%d ⇎ ⟦O⟧%d ⇎ ⟦K⟧%d; 行文内另用 %d 次), 锚内字母 %d(源内原词 APP×2) ⇎ 锚内汉字 %d, '
       u'锚外字母 %d = 单字母出处标签 %d + 其余 %d(ℒmethod 记号); 判词层 %d ‖ 骨架与 ℒmethod %d; T1／T2／T3 失配 0, 待核小整数 0 条。'
       % (len(enc), len(enc.replace(u'\n', u'')), dlen['N'], dlen['O'], dlen['K'], len(orig), len(atoms), wins, RC, len(raw_all), raw_bytes,
          pct_win, pct_rc, pct_all, pct_byte, len(atoms), alab['N'], alab['O'], alab['K'], nlab - sum(alab.values()),
          in_lat, in_han, outlat, nlab, outlat - nlab, judge, skel))
editor = judge + skel
verb = ne - editor
extra = (u'※保留率口径(三种都给,不用摘要窗口买指标): 表列 %.1f%%＝编码÷摘要段——%d 个锚在三源中只合并成 %d 个窗口(250／200 字), '
         u'小中文源该比值必然过 100%%; 换成 raw 正文字符口径＝%.1f%%(编码 %d ÷ 正文 %d),即长度上本条并未压缩。'
         u'压缩发生在逐字层: 编者层(判词 %d + 骨架与 ℒmethod %d ＝%d 字)是新增推理,逐字与连接层只占 %d 字＝原文的 %.1f%%; '
         u'被删掉的是三源逐字重复的缴款·备案·复议·诉讼段(共 %d 字)与 ⟦O⟧ 案的 11 个股票名、10 人×2 组金额名录, '
         u'省下的额度换成了 16 条机检派生算术与跨案对照——这三样在任何单一源里都不存在。'
         % (pct_win, len(atoms), wins, pct_rc, ne, RC, judge, skel, editor, verb, 100.0 * verb / RC, tpl))
pat = re.compile(u'※实况(?: ⟪待填⟫|[^\n]*\n※保留率口径[^\n]*)')
assert pat.search(t)
t = pat.sub(lambda m: msg + u'\n' + extra, t, count=1)
io.open(E, u'w', encoding=u'utf-8').write(t)
print(msg)
print(extra)
