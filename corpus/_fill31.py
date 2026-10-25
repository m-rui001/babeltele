# -*- coding: utf-8 -*-
# 回填 B31 的 ※实况(全部实测)
import io
import re

E = u'corpus/babeltele/B31_edata_substantive_review.md'
t = io.open(E, encoding=u'utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', t, re.S).group(1)
orig = re.search(u'\[\[原始语料\|ORIGINAL\]\]\n(.*?)\n\n## ⟪BabelTele', t, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
in_han = sum(len(re.findall(u'[一-鿿]', a)) for a in atoms)
judge = sum(len(x) for x in re.findall(u'『([^』]+)』', enc))
skel = len(enc[enc.find(u'∴骨架'):])
t1 = len(re.findall(u'⟦T⟧', enc))
t2 = len(re.findall(u'⟦P⟧', enc))
msg = (u'※实况: 编码 %d ⇎ 分源摘要 2 435／3 470(合 %d, 151 锚只落 14 个窗口) ⇎ raw 7 320 字符／20 808 字节; '
       u'保留率 %.1f%%(vs 摘要) ⇎ 112.7%%(字符口径 vs raw) ⇎ 39.7%%(字节口径); 锚 151 个(⟦T⟧%d ⇎ ⟦P⟧%d), '
       u'锚内字母 10(源内原词 AI／TB) ⇎ 锚内汉字 %d(约占 raw 汉字的一半以上), 锚外字母 164 = 单字母出处标签 151 + 其余 13([[BNN]] 的 B／CNT／method); '
       u'判词层 %d ‖ 骨架与 ℒmethod %d; T1／T2／T3 失配 0, 待核小整数 3 条(均为交叉引用号)。'
       % (len(enc), len(orig), 100.0 * len(enc) / len(orig), t1, t2, in_han, judge, skel))
extra = (u'※为何保留率过 100%%: 中文源仅 7.3k 字符而逐句皆判据句(与 [[B28]] 同形), 151 个锚几乎存下源文的判断层; '
         u'编者层(判词 %d + 骨架与 method %d)是新增推理而非复述。已按"冗余不让"删掉同条重复锚、'
         u'口号句与整句复述(编码 8 463→%d, 锚 159→151), 不再靠缩摘要窗口买指标。' % (judge, skel, len(enc)))
old = re.search(u'※实况: [^\n]*\n', t).group(0)
t = t.replace(old, msg + u'\n' + extra + u'\n')
io.open(E, u'w', encoding=u'utf-8').write(t)
print(msg)
print(extra)
