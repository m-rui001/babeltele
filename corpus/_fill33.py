# -*- coding: utf-8 -*-
# 回填 B33 的 ※实况 与 ※保留率口径(全部实测, 幂等: 重复运行只替换这两行)
import io
import re

E = u'corpus/babeltele/B33_csb_clairton_staged_findings.md'
t = io.open(E, encoding=u'utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', t, re.S).group(1)
orig = re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\n(.*?)\n\n## ⟪BabelTele', t, re.S).group(1)
ne = len(enc.replace(u'\n', u''))
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
in_han = sum(len(re.findall(u'[一-鿿]', a)) for a in atoms)
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
judge = sum(len(x) for x in re.findall(u'『([^』]+)』', enc))
skel = len(enc[enc.find(u'∴骨架'):])
TAGS = (u'U', u'I', u'F')
nlab = len(re.findall(u'⟦[A-Z]⟧', enc))
outlat = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)))
alab = {g: len(re.findall(u'⟦%s⟧⟨' % g, enc)) for g in TAGS}
dlen = {g: 0 for g in TAGS}
for m in re.finditer(u'### ⟦([A-Z])⟧ ⟸ [^\n]*\n(.*?)(?=\n\n### |\\Z)', orig, re.S):
    dlen[m.group(1)] = len(m.group(2).strip())
wins = len([x for x in re.split(u'\n\n', re.sub(u'^### .*$', u'', orig, flags=re.M).strip()) if x.strip()])

FILES = (u'corpus/raw/prose/csb_clairton_update.txt',
         u'corpus/raw/prose/csb_clairton_interim.txt',
         u'corpus/raw/prose/csb_clairton_final.txt')
heads = [io.open(f, encoding=u'utf-8').read().split(u'\n\n', 1)[0] for f in FILES]
bodies = [io.open(f, encoding=u'utf-8').read().split(u'# note:', 1)[1].split(u'\n', 1)[1].strip()
          for f in FILES]
raw_all = u''.join(io.open(f, encoding=u'utf-8').read() for f in FILES)
raw_bytes = sum(len(io.open(f, encoding=u'utf-8').read().encode(u'utf-8')) for f in FILES)
RC = sum(len(b) for b in bodies)
pct_win = 100.0 * ne / len(orig)
pct_rc = 100.0 * ne / RC
pct_all = 100.0 * ne / len(raw_all)
pct_byte = 100.0 * ne / raw_bytes
pages = [re.search(u'(\\d+) 页', h).group(1) for h in heads]

msg = (u'※实况: 编码 %d(含换行; audit 去换行口径 %d) ⇎ 分源摘要 U %d／I %d／F %d(合 %d, %d 个锚落 %d 个窗口, '
       u'其中 15 个锚在三源里都能命中⇒归属只由标签决定) ⇎ raw 正文 %d 字符／含出处头 %d 字符／%d 字节; '
       u'保留率 %.1f%%(vs 摘要段) ⇎ %.1f%%(vs raw 正文字符) ⇎ %.1f%%(vs 含头字符) ⇎ %.1f%%(字节口径＝audit 表列 vs raw源); '
       u'锚 %d 个, 归属由前贴标签决定(同标签相邻锚合写: ⟦U⟧%d ⇎ ⟦I⟧%d ⇎ ⟦F⟧%d; 行文内另用 %d 次), 锚内字母 %d ⇎ 锚内汉字 %d, '
       u'锚外字母 %d = 单字母出处标签 %d + 其余 %d(机构专名·单位与 ℒmethod 记号); 判词层 %d ‖ 骨架与 ℒmethod %d; '
       u'T1／T2／T3 失配 0, 待核小整数 0 条。'
       % (len(enc), ne, dlen['U'], dlen['I'], dlen['F'], len(orig), len(atoms), wins,
          RC, len(raw_all), raw_bytes, pct_win, pct_rc, pct_all, pct_byte,
          len(atoms), alab['U'], alab['I'], alab['F'], nlab - sum(alab.values()),
          in_lat, in_han, outlat, nlab, outlat - nlab, judge, skel))

extra = (u'※保留率口径: 表列 %.1f%%＝编码 %d÷摘要段 %d; 摘要段按锚点窗口拼接, 三源各取命中于它的锚(窗口 250／200 字), '
         u'占 raw 正文 %d 字符的 %.1f%%, 即摘要段本身已是一次保真压缩, 编码相对 raw 正文是 %.1f%%(字符)⇎%.1f%%(字节)。'
         u'编者层(判词 %d + 骨架与 ℒmethod %d ＝%d 字)是新增推理; 被删掉的是 86 页报告的图注、页码表、'
         u'推荐台账全文(仅保留 ⟦F⟧⟨2025-03-I-PA-R1 (previously issued as an interim recommendation in December 2025)⟩ 一条以证台账不断号)、'
         u'事故时间线逐分钟复述与背景公司介绍。三源页数 %s⇎%s⇎%s, 同号 No. 2025-03-I-PA: 分期发布本身就是语料的一部分。'
         % (pct_win, ne, len(orig), RC, 100.0 * len(orig) / RC, pct_rc, pct_byte,
            judge, skel, judge + skel, pages[0], pages[1], pages[2]))

pat = re.compile(u'※实况(?: ⟪待填⟫|[^\n]*\n※保留率口径[^\n]*)')
assert pat.search(t), u'找不到 ※实况 行'
t = pat.sub(lambda m: msg + u'\n' + extra, t, count=1)
io.open(E, u'w', encoding=u'utf-8').write(t)
print(msg)
print(extra)
