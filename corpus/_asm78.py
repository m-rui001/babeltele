# -*- coding: utf-8 -*-
# 由 _mkB77.py 组装 _mkB78.py
import io, json, ast

s = io.open('corpus/_mkB77.py', encoding='utf-8').read()
s = s.replace('B77', 'B78')
s = s.replace('arxiv/llama3_a.txt', 'faa/ad_a.txt')
s = s.replace('arxiv/llama3_b.txt', 'faa/ad_b.txt')
s = s.replace('arxiv/llama3_c.txt', 'faa/ad_b.txt')
s = s.replace("TAGS = ['A', 'B', 'C']", "TAGS = ['A', 'B']")
s = s.replace('corpus/_b77meas.json', 'corpus/_b78meas.json')
s = s.replace('corpus/_b77flat.json', 'corpus/_b78flat.json')
s = s.replace('_atoms77.txt', '_atoms78.txt')
s = s.replace('B77_llama3_versions_immutable_body.md', 'B78_faa_two_ads_same_defect.md')

head, rest = s.split(u'E = []', 1)
tail = rest[rest.index(u'enc = '):]

E = u"""E = []
E.append(u'🧭 同一缺陷(LPSOV 线束防护不足⇒不可包容转子破裂 UERF 失火)的两次 FAA 适航指令, 同为 Federal Register 纯文本面: 初始 AD 2023-01-09 %d 字符⇎整改 AD 2023-10-05 %d ⇎ 句 %d⇎%d 句, 每句均值 %d⇎%d 字符。'
         % (V('chars', 0), V('chars', 1),
            V('sents', 0), V('sents', 1),
            V('avg_sent', 0), V('avg_sent', 1)))

E.append(u'🔁 监管文体是半成品组装件: 句集交集 A⇎B %d 句(占 A 的 %.1f%%), 去重句各 %d⇎%d——整改 AD 的三分之一逐字来自初始 AD: 同一段 prompted-by ⟦A⟧⟨This AD was prompted by a safety review of the airplane fuel system, which identified that the electrical harness routing of the engine low pressure shut off valve (LPSOV) is not adequately protected against uncontained engine rotor failure (UERF).⟩ 两份各 %d⇎%d 处, 适用范围句 ⟦B⟧⟨This AD applies to the Airbus SAS airplanes specified in paragraphs (c)(1) through (3) of this AD⟩ 亦逐字共享。'
         % (V('sh_ab'), round(100.0 * V('sh_ab') / V('sent_uniq', 0), 1), V('sent_uniq', 0), V('sent_uniq', 1),
            V('prompted', 0), V('prompted', 1)))

E.append(u'⚖ 处置升级的两步: A 只记录风险——混装机型的旁注句 ⟦A⟧⟨unsafe condition may exist on airplanes with two different types of engines installed⟩, B 直接要求改装 ⟦B⟧⟨This AD requires modification of the LPSOV electrical harness routing on either the left-hand engine or the right-hand engine⟩ 并给出后果句 ⟦B⟧⟨loss of engine fuel isolation capability in case of UERF, possibly resulting in an uncontrolled fire⟩; unsafe condition 词族 %d⇎%d 处、modif- 词族 %d⇎%d 处、inspect- 词族 %d⇎%d 处、fire %d⇎%d 处。'
         % (V('unsafe', 0), V('unsafe', 1),
            V('modification', 0), V('modification', 1),
            V('inspect', 0), V('inspect', 1),
            V('fires', 0), V('fires', 1)))

E.append(u'🏛 引用走页码不走编号: B 提初始 AD 用纸面页码——"88 FR 5817" 在 B 面 %d 处而 "2023-01702" 编号在 B 面 %d 处; MCAI(别国适航信息)采纳件身份两份相同(EASA %d⇎%d 处、MCAI %d⇎%d 处、EASA AD 2022-0185 %d⇎%d 处); 程序差异: 征求意见 comment %d⇎%d 处(A 走了征求意见期, B 收紧处置少听意见)、docket %d⇎%d 处、cost %d⇎%d 处。'
         % (V('fr5817', 1), V('other_ad', 1),
            V('easa', 0), V('easa', 1), V('mcai', 0), V('mcai', 1), V('2022_0185', 0), V('2022_0185', 1),
            V('comments', 0), V('comments', 1),
            V('docket', 0), V('docket', 1),
            V('cost', 0), V('cost', 1)))

E.append(u'ℒ 方法 ⇒ 同一缺陷两次指令的隐性知识在处置升级与文体组装: 句集交集把模板复用做成键(%d 句), prompted-by 同句把同因做成键(%d⇎%d), 引用方式做成键(FR 页码 %d 处⇎AD 编号 %d 处), 程序词频做成键(comment %d⇎%d)。'
         % (V('sh_ab'), V('prompted', 0), V('prompted', 1), V('fr5817', 1), V('other_ad', 1), V('comments', 0), V('comments', 1)))

"""

# fr5817 补测进 meas(flat 契约由 mkB78 的 V() 登记自动生成)
F = json.load(io.open('corpus/_b78meas.json', encoding='utf-8'))
lows = [u' '.join(io.open(f, encoding='utf-8').read().partition(u'\n\n')[2].split()).lower()
        for f in ('corpus/raw/faa/ad_a.txt', 'corpus/raw/faa/ad_b.txt')]
F['fr5817'] = [t.count(u'88 fr 5817') for t in lows]
F['other_ad'] = [lows[0].count(u'2023-01702') - 1, lows[1].count(u'2023-01702')]
io.open('corpus/_b78meas.json', 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))

out = head + E + tail

# title / srcline / tagsline 重写(定位行块)
lines = out.split(u'\n')
i = next(k for k, l in enumerate(lines) if l.startswith(u'title = (u'))
j = next(k for k in range(i, len(lines)) if lines[k].strip().startswith(u'% (F['))
BS = chr(92)
lines[i:j + 1] = [
    u"title = (u'# B78 同一缺陷的两次适航指令: FAA LPSOV——整改版逐字复制初始版 %d 句(占 %.1f%%), " + BS + "n'",
    u"         u'但引用走纸面页码不走编号; 处置从\"记录风险\"升级到\"强制改装\", 征求意见处数 %d⇎%d" + BS + "n'",
    u"         % (F['sh_ab'], round(100.0 * F['sh_ab'] / F['sent_uniq'][0], 1), F['comments'][0], F['comments'][1]))",
]
i = next(k for k, l in enumerate(lines) if l.startswith(u'srcline = (u'))
j = next(k for k in range(i, len(lines)) if u"FILES['B'], F['chars'][1]" in lines[k] and lines[k].strip().endswith('))'))
lines[i:j + 1] = [
    u"srcline = (u'src: %s (%d 字符) ⇎ %s (%d 字符) '",
    u"           u'(两份同为 Federal Register 纯文本面: FAA AD 2023-01702 ⇎ AD 2023-22080, 同因 LPSOV 线束/UERF; '",
    u"           u'数字一律从面内现读, 一个都不手填; 抓取时刻与 FR 现行版本只在本机或站外成立, 不进门槛)" + BS + "n'",
    u"           % (FILES['A'], F['chars'][0], FILES['B'], F['chars'][1]))",
]
i = next(k for k, l in enumerate(lines) if l.startswith(u'tagsline = (u'))
j = next(k for k in range(i, len(lines)) if lines[k].strip().endswith(u"6 项" + chr(92) + "n')")) or i + 1
lines[i:j + 1] = [
    u"tagsline = (u'tags: 模板复用键(句集交集三分之一) 处置升级键(记录⇎改装) 引用页码键(FR页码⇎编号) 程序词频键(comment) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项" + BS + "n')",
]
out = chr(10).join(lines)
io.open('corpus/_mkB78.py', 'w', encoding='utf-8', newline='\n').write(out)
ast.parse(out)
print('mkB78 assembled, syntax OK')
