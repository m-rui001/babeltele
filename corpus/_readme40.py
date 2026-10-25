# -*- coding: utf-8 -*-
"""README 记账: 39 条 → 40 条。每条替换都断言命中 1 次, 合计数字由 audit 表复算。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

F = 'corpus/README.md'
t = io.open(F, encoding='utf-8').read()

# 由 audit 输出复算全库合计(不手填)
au = io.open(u'corpus/babeltele/B40_fda_three_de_novo_orders.md', encoding='utf-8').read()
enc_n = len(au.split(u'## ⟪BabelTele⟫')[1].split(u'## ⛓解读注')[0].strip(u'\n').replace(u'\n', u''))
dig = len(re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', au, re.S).group(1))
assert (enc_n, dig) == (10077, 15293), (enc_n, dig)

R = []

R.append((u'共 **39 条**（`babeltele/B01..B39`）', u'共 **40 条**（`babeltele/B01..B40`）'))

R.append((u'而这些数字几乎全是复述对方的。',
          u'而这些数字几乎全是复述对方的。\n\n'
          u'**B40 换了体裁**：不再读争论，改读三份同一机关、同一文书类型、三种介质的监管分类令'
          u'（91 FR 57785 ⇎ 91 FR 36522 ⇎ 91 FR 39459，都是面向新增 II 类器械的类别划分令，'
          u'`raw/prose/fr_fda_{cardio_ml_notification,radiology_ml_pccp,opioid_impairment_monitor}.txt`，每份 17 000 字上下）。'
          u'这里没有对手，可读的是**模板与差集**：套语段落的关键词逐份计数完全相同（第一人称各 13 次、二级短语各 14 次、'
          u'新类别认定各 12 次、控制号各 5 次，机检均值即整数 ⇒ 复制），所以信息全在差集里——同一项人在环路的验证'
          u'在一份叫人因子、在另一份叫可用性、在第三份两个名字都不出现；同一条“测试集不得与训练集重叠”写作独立 ⇎ 分离；'
          u'风险表的行按介质换掉（生物相容／电磁／无线只在传感设备那份，模型偏见只在软件那份，“过度依赖”在带变更控制计划的那份为 0）；'
          u'三份义务词总量相近（合计 31 次）而只有拿到自变更授权的那份出现第二人称 ⇒ **义务可以没有受话人**；'
          u'两份脚注对同一个词一个加引号一个不加，而规范化把这一差别抹平 ⇒ 引号级飘移只能靠逐字锚保留。'))

R.append((u'| B40 | 10 077', u'| B40 | 10 077'))  # 占位, 不存在则下面单独插入

rows = t.split(u'\n')
i39 = [k for k, l in enumerate(rows) if l.startswith(u'| B39 | 11 318（新建')]
assert len(i39) == 1, i39
rows.insert(i39[0] + 1,
            u'| B40 | 10 077（新建, 三源 91 锚: 三份同族分类令 ⟦C⟧⇎⟦R⟧⇎⟦M⟧; '
            u'**25 个串跨文件同命中**——那是套语的证据而不是误标; 一个零键担保 35 处缺席断言; '
            u'同一保证句带／不带冠词两种写法各用一份 `CNT` 之和（10 ⇎ 8）证明“按短语检索必漏一半”; '
            u'判词里的数字全部落在 20 个键内, 同值断言改写成缺席断言以免一键两义） | 91 | 4 845 | '
            u'149（其中 143 为出处标签, 余 6 为记号 `ℒmethod` 自身） | 65.9% | 15 293 |')
t = u'\n'.join(rows)
R = R[:2] + R[3:]

R.append((u'第二代（B11–B39）锚内字母 **66 122**、锚外 **2 487**；全库合计 66 243／4 682',
          u'第二代（B11–B40）锚内字母 **70 967**、锚外 **2 636**；全库合计 **71 088／4 831**'))

# 长条目表: 在 B39 行之后插入 B40 行
rows = t.split(u'\n')
i39 = [k for k, l in enumerate(rows) if l.startswith(u'| B39 | `raw/prose/pmc_mobilization_dose_study.txt`')]
assert len(i39) == 1, i39
rows.insert(i39[0] + 1,
            u'| B40 | `raw/prose/fr_fda_cardio_ml_notification.txt`（91 FR 57785–57787, 文件号 2026-18612, '
            u'案号 FDA-2026-N-9907, 规章号 870.2380, 17 480 字符）⇎ `raw/prose/fr_fda_radiology_ml_pccp.txt`'
            u'（91 FR 36522–36524, 2026-12166, FDA-2026-N-6535, 892.2055, 17 587 字符, 附带预定变更控制计划）⇎ '
            u'`raw/prose/fr_fda_opioid_impairment_monitor.txt`（91 FR 39459–39461, 2026-13140, FDA-2026-N-6707, '
            u'868.2250, 16 944 字符） | 三份同族监管令的模板与差集：三个日期谁被引用（适用 2023-08-03 ⇎ 刊发 2026-09-11 ⇎ 生效同日）；'
            u'120 日只管决定不管公布（3 年 ≈ 期限 9.1 倍）；套语逐份计数相同 ⇒ 信息全在差集；同一保证句带／不带冠词（10 ⇎ 8）；'
            u'人因子 ⇎ 可用性 ⇎ 两者皆无；机器学习条款藏在非机器学习的令里（那唯一一次）；独立 ⇎ 分离；'
            u'指标清单按介质分家（骰度／豪斯多夫距离／布蓝-阿特曼只在放射那份）；否定式边界写在认定段 ⇎ 写在标签里；'
            u'风险表的行是“这个介质能怎么伤人”的清单；人口学在传感器那份为 0 而它改用亚群／使用环境／阿片类型三轴；'
            u'“警告” ⇎ “描述可能失效的情形”；预定变更控制全称加缩写合计 17 次只在带计划的那份；'
            u'第一人称各 13 ⇎ 第二人称合计 2 ⇎ 义务词合计 31 ⇒ 义务可以没有受话人；'
            u'签发人逐字相同而联系人电话前缀分组、房间号 2108／3672／1232 不同；案号同系列而流水号无序不可排序；'
            u'登记日恰为生效前一天（排版而非审查）；文件自解标题写法且两份写法互不相同 |')
t = u'\n'.join(rows)

R.append((u'`python corpus/audit.py` → **PASS**（39 条）', u'`python corpus/audit.py` → **PASS**（40 条）'))
R.append((u'当前 **28 个 tag／229 条**推导全部通过', u'当前 **29 个 tag／249 条**推导全部通过'))
R.append((u'| **合计（39 条）** | **162 146** | **69.0%**（摘要段合计 235 111） | — | **2 092** | — |',
          u'| **合计（40 条）** | **172 223** | **68.8%**（摘要段合计 250 404） | — | **2 101** | — |'))

rows = t.split(u'\n')
im39 = [k for k, l in enumerate(rows) if l.startswith(u'| B39 | 11 318 | 88.3% |')]
assert len(im39) == 1, im39
rows.insert(im39[0] + 1,
            u'| B40 | 10 077 | 65.9% | 18.323%（字节口径; 正文口径编码为三源 52 011 字的 19.4%——'
            u'套语三份逐字相同而每条只引一次, 故为三源条最低） | 582 | 6.67 |')
t = u'\n'.join(rows)

R.append((u'（4 837 字编码 vs 6 071 字摘要 vs 9 334 字源文）。',
          u'（4 837 字编码 vs 6 071 字摘要 vs 9 334 字源文）。B40 是唯一的反方向样本：它的低保留率不来自删论证，'
            u'而来自**三份文书的套语逐字相同，一条套语只需引用一次**（65.9%／18.323%, 全库最强），'
            u'判词一句没少——保留率因此要按“重复文本存了几份”来读，而不是按“少说了多少话”来读。'))

R.append((u'Latin 70 925 · Han 45 959 · Gen-Punct 1 428 · Arrows 1 251 · CJK-Punct 899 · Fullwidth 541 · Emoji 432 · Math 241 · Greek 71 · Misc-Symbols 47 · Dingbats 31 · Geometric 30 · Hiragana 18 · Katakana 13',
          u'Latin 75 919 · Han 48 236 · Gen-Punct 1 548 · Arrows 1 311 · CJK-Punct 948 · Fullwidth 618 · Emoji 449 · Math 243 · Greek 71 · Misc-Symbols 48 · Dingbats 31 · Geometric 30 · Hiragana 18 · Katakana 13'))

R.append((u'唯一码点 2 092 / 162 146 ≈ 1.3%', u'唯一码点 2 101 / 172 223 ≈ 1.2%'))

R.append((u'B32／B33／B34／B35／B36／B37／B38／B39 是仅有的八条**待核列为 0** 的条目',
          u'B32／B33／B34／B35／B36／B37／B38／B39／B40 是仅有的九条**待核列为 0** 的条目'))
R.append((u'B39 的 0／2／4／5／7／10／20／40／59／87／392／1.59／2.03／5.38／0.02／0.03／0.1／1.14／1.31／2.7／16.6／25.8／64.3',
          u'B39 的 0／2／4／5／7／10／20／40／59／87／392／1.59／2.03／5.38／0.02／0.03／0.1／1.14／1.31／2.7／16.6／25.8／64.3，'
          u'B40 的 0／1／2／3／4／5／6／7／8／9.1／10／11／12／13／14／15／17／31／36／42'))

R.append((u'python -X utf8 corpus/_fill39.py               # ⛓解读注, 含 64/64 跨源核验与"两文件正文之和命中 2 次"的逐字引文证明',
          u'python -X utf8 corpus/_fill39.py               # ⛓解读注, 含 64/64 跨源核验与"两文件正文之和命中 2 次"的逐字引文证明\n'
          u'python -X utf8 corpus/_mkraw40.py              # govinfo 三份 FR HTML → raw/prose/（同一剥标签脚本, 各自重算 chars/text_sha256）\n'
          u'python -X utf8 corpus/_mkB40.py                # 建条目: 91 锚逐条按标签回源做规范化子串断言（锚允许写在判词内, 生成后统一抽取核对）\n'
          u'python -X utf8 corpus/_mkdigest3.py B40 <entry> C <cardio raw> 340 270 R <radiology raw> 340 270 M <monitor raw> 340 270   # 三源分节摘要 union_hit 91/91\n'
          u'python -X utf8 corpus/_wire40.py               # 幂等接线: SRC/ATOM/DERIV(20 键, 一个零键折 35 处缺席)+atomcheck; DERIV 先删后插; audit 的 CNT 跑在**未规范化原文**上⇒词组须用 \\s+ 跨硬换行\n'
          u'python -X utf8 corpus/_fill40.py               # ⛓解读注: 所有计数先量后断言（91＝42＋23＋26、跨文件同命中 25、键 20、缺席 35）'))

for old, new in R:
    if old == new:
        continue
    n = t.count(old)
    assert n == 1, (n, old[:60])
    t = t.replace(old, new, 1)

io.open(F, 'w', encoding='utf-8').write(t)
left = [l for l in t.split(u'\n') if re.search(r'39 条|B01\.\.B39|2 092|162 146|235 111|八条', l)]
print(u'README 40 条完成; 残留旧计数行 %d' % len(left))
for l in left:
    print(u'  ' + l[:120])
