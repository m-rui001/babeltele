# -*- coding: utf-8 -*-
"""README 记账: 41 条 → 42 条。合计数字全部由 audit 表与 metrics 普查复算, 不手填。"""
import io, re, sys, subprocess

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
t = io.open(F, encoding='utf-8').read()

p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-400:]
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
dig_all, enc_all, ret_all, uniq_all = (int(allc[0].replace(u' ', u'')), int(allc[1].replace(u' ', u'')),
                                       allc[2], int(allc[4]))
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
b42 = [x.strip() for x in row[u'B42'].split(u'|')]
b42_dig, b42_enc, b42_ret, b42_raw, b42_uniq, b42_cps = (int(b42[0]), int(b42[1]), b42[2], b42[3], int(b42[4]), b42[6])
assert (b42_enc, b42_dig, proofs) == (11647, 6556, 365), (b42_enc, b42_dig, proofs)

m = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/metrics.py'],
                   capture_output=True, text=True, encoding='utf-8')
cen = dict((mm.group(1), int(mm.group(2))) for mm in
           re.finditer(r'^\s{2}([A-Za-z\-]+)\s+([\d ]+)$', m.stdout, re.M))
assert len(cen) == 18, sorted(cen)
ST = dict(l.split(u'\t') for l in io.open(u'corpus/_f42stats.txt', encoding='utf-8').read().split(u'\n') if l)
IN_LAT, OUT_LAT = int(ST[u'in_lat']), int(ST[u'out_lat'])
TAG_LAT = int(ST[u'tag_lat'])
# 锚外口径沿用 README 既有写法: 出处标签计入锚外(B41 的 175 含 132 标签), 故补回标签字母
OUT_ALL = OUT_LAT + TAG_LAT
assert cen[u'Latin'] - 81178 == IN_LAT + OUT_ALL, (cen[u'Latin'], IN_LAT, OUT_ALL)


def fmt(n):
    return u'{:,}'.format(int(n)).replace(u',', u' ')


cen_s = (u'Latin %s · Han %s · Gen-Punct %s · Arrows %s · CJK-Punct %s · Fullwidth %s · Emoji %s · Math %s · '
         u'Greek %s · Misc-Symbols %s · Dingbats %s · Geometric %s · Hiragana %s · Katakana %s · '
         u'MathAlnum %s · EnclosedIdeo %s · EnclosedSuppl %s · Comb-Diacritic %s') % tuple(
    fmt(cen[k]) for k in [u'Latin', u'Han', u'Gen-Punct', u'Arrows', u'CJK-Punct', u'Fullwidth', u'Emoji',
                          u'Math', u'Greek', u'Misc-Symbols', u'Dingbats', u'Geometric', u'Hiragana',
                          u'Katakana', u'MathAlnum', u'EnclosedIdeo', u'EnclosedSuppl', u'Comb-Diacritic'])
FIRST_IN, FIRST_OUT = 71088 - 70967, 4831 - 2636
prev_in, prev_out = 70967 + 5084, 2636 + 175                 # 截至 B41 的锚内 ⇎ 锚外(含出处标签)
in_lat = 70967 + 5084 + IN_LAT
out_lat = 2636 + 175 + OUT_ALL

PAIRS = [
 (u'共 **41 条**（`babeltele/B01..B41`）', u'共 **42 条**（`babeltele/B01..B42`）'),
 (u'**PASS**（41 条）', u'**PASS**（42 条）'),
 (u'当前 **41 条语料／333 条**推导全部通过（audit 自报“已机检的推导 333 条”）',
  u'当前 **42 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (proofs, proofs)),
 (u'第二代（B11–B41）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B42）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'B39／B40／B41 是仅有的十条**待核列为 0** 的条目',
  u'B39／B40／B41／B42 是仅有的十一条**待核列为 0** 的条目'),
]
for old, new in PAIRS:
    n = t.count(old)
    if n != 1:
        print(u'注意: 未命中或多处 -> %r (%d)' % (old[:60], n))
    assert n >= 1, old[:60]
    t = t.replace(old, new, 1)

# 行级替换(合计行 / 唯一码点行 / 普查行 / 键清单 / 判词段)
R = t.split(u'\n')
done = []
for i, l in enumerate(R):
    if l.startswith(u'| **合计（41 条）**'):
        R[i] = (u'| **合计（42 条）** | **%s** | **%s**（摘要段合计 %s） | — | **%s** | — |'
                % (fmt(enc_all), ret_all.strip(u'*'), fmt(dig_all), fmt(uniq_all)))
        done.append(u'合计')
    elif u'唯一码点 2 116 /' in l or (u'唯一码点' in l and u'≈' in l and u'条）**' not in l and l.startswith(u'唯一') is False and u'%' in l and u'码点' in l and u'/ ' in l and i > 0 and not R[i - 1].startswith(u'|')):
        pass
for i, l in enumerate(R):
    if re.match(u'^唯一码点 \\d+ \\d+ / \\d+ \\d+ ≈', l) or (u'唯一码点' in l and l.startswith(u'唯一码点')):
        R[i] = (u'唯一码点 %s / %s ≈ %.1f%%' % (fmt(uniq_all), fmt(enc_all), 100.0 * uniq_all / enc_all))
        done.append(u'唯一码点')
        break
for i, l in enumerate(R):
    if l.startswith(u'Latin ') and u'· Han ' in l:
        R[i] = cen_s
        done.append(u'普查')
        break
for i, l in enumerate(R):
    if u'B41 的 0／1／2／3／4／6／8' in l:
        R[i] = l.replace(u'）', u'，B42 的 0／3／4／5／8／13／15／17／20／21／23／26／33／35／36／40／49／50／53／54／57／60／72／77／108／202／280／374／375／0.74／9）', 1)
        done.append(u'键清单')
        break
for i, l in enumerate(R):
    if l.endswith(u'而这类差额是通读回应段永远看不见的。'):
        R[i] = l + (u'B42 又换了一根轴：它只有一份文件，于是没有“跨源差集”可算，'
                    u'可压缩的东西只剩**文档内部的逐字复用**——九种长句实际出现 35 次，其中 26 次是复制（机检 35⇎26，占 0.74），'
                    u'而复制的单位是整条义务句，不是词。它同时给出全库最高的“vs 摘要段”保留率 177.7%：'
                    u'单源条只有 23 个不同锚，可索引窗口小，判词必须自建对照，所以编码重于窗口；'
                    u'读这类条目要按字节口径 5.411% 与“33 键＋13 项缺席支撑 11 行判词”来读，而不是按窗口比。')
        done.append(u'口径段')
        break
for i, l in enumerate(R):
    if l.endswith(u'⇒ “可核”与“可联系”是两件事。'):
        R[i] = l + (u'\n\n'
            u'**B42 把对照轴转向文件内部**：一份 CSB 事故调查报告（88 页 PDF 转文本，213 726 字符，单源）。'
            u'没有第二份文件做差集，可读的是**同一份文本自己重复了什么**：九种建议长句共出现 35 次，26 次是逐字复制（机检 35／26／0.74），'
            u'其中一句 193 字符级的仪表要求与“控制室可监视”短句各 5 次（机检 5）——复制说明同一条义务被发给多个受文对象，'
            u'去重就会把“发给谁”读没了。义务强度三档在同一句里并存（should 57 ⇎ shall 21 ⇎ must 17，差 40；must include 8 次）；'
            u'页码在这份转本里为 0（“Page ”列入 0 键），所以“第几页”不可核，只能引目录级小节名；'
            u'证据交给图（Figure 72 ⇎ Table 15 ⇎ Appendix 23），文本只承担叙事；'
            u'缩写表只是字母（SIS 20 次）不等于定义；受文对象频次（CSB 202／API 77／五类机构合计 108）证明这是建议文书而非处罚文书；'
            u'事件链用“人在做什么”的词（troubleshoot 49／walk the line 33／cover plate 32／afterburn 53）而 root cause 只 4 次；'
            u'整套行业机制术语（hot work／permit／lockout／tagout／MOC／PTW／29 CFR／energy isolation）一次都没出现，'
            u'13 项缺席折进一个 0 键——检索“该报告是否讨论 MOC”的正确答案是 0，而这个 0 本身就是结论。')
        done.append(u'B42 段')
        break

# 三张表 + 命令表插入
ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B41 | %s（新建' % fmt(10379)):
        ins.append((i + 1, u'| B42 | %s（新建, 单源 52 锚位／23 个不同串: 建议正文按受文对象逐字复用, '
                           u'九种长句实际 35 次出现里 26 次是复制（机检 35⇎26⇎0.74）; '
                           u'一个零键折 13 处术语缺席断言; 义务三档 57⇎21⇎17 全部走 CNT; '
                           u'页码为 0 故“第几页”不可核, 图 72⇎表 15⇎附录 23 说明证据在图里） | 52 | %s | '
                           u'%d（其中 %d 为出处标签, 余 %d 为机构缩写与文件名） | %s | %s |'
                           % (fmt(b42_enc), fmt(IN_LAT), OUT_ALL, TAG_LAT,
                              OUT_ALL - TAG_LAT, b42_ret, fmt(b42_dig))))
    elif l.startswith(u'| B41 | %s | 81.5%%' % fmt(10379)):
        ins.append((i + 1, u'| B42 | %s | %s | %s（字节口径; 单源正文 213 726 字 ⇎ 文件 215 228 字节——'
                           u'保留率高于全库是单源条的结构性结果: 23 个不同锚可索引窗口小, 而判词自建对照, 故编码重于窗口） | %d | %s |'
                           % (fmt(b42_enc), b42_ret, b42_raw, b42_uniq, b42_cps)))
    elif l.startswith(u'| B41 | `raw/prose/fr_fda_ish_proposed_order.txt`'):
        ins.append((i + 1, u'| B42 | `raw/prose/csb_marathon_martinez.txt`（CSB 公开事故调查报告, '
                           u'Marathon Martinez Renewables 装置加热管破裂与火灾, 88 页 PDF 转文本, 正文 213 726 字符／3 884 行, '
                           u'抓取头部自记 pages=88 bytes=4 310 788） | '
                           u'单源内部冗余：九种长句 35 次出现（26 次逐字复制）；同一句 193 字符级仪表要求 5 次⇎“控制室可监视”5 次；'
                           u'should 57⇎shall 21⇎must 17（差 40）且同句混档；must include 8 次⇎may include 与表数同值 15；'
                           u'“Page ”0 次⇒页码不可核只能引小节；Figure 72⇎Table 15⇎Appendix 23⇒证据在图里；'
                           u'缩写表 SIS 20 次只是字母不等于定义；CSB 202⇎API 77⇎五类机构合计 108⇒建议文书而非处罚文书；'
                           u'troubleshoot 49⇎walk the line 33⇎cover plate 32⇎afterburn 53⇎tube rupture 54⇎root cause 4；'
                           u'fired heater 比失效名多 280 次；hot work／permit／lockout／tagout／MOC／PTW／29 CFR 等 13 式全 0；'
                           u'转写残留右括号 375 个⇎项目符号 60 个⇒列表结构被压平；http 50⇎www. 36；Marathon 374 次为主题信号 |'))
    elif l.startswith(u'python -X utf8 corpus/_fill41.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_mkB42.py                # 建条目: 锚点从空白折叠后的原文切片(逐字由构造保证, 且按大小写不敏感定位), 判词数字全部取 raw 计数\n'
                    u'python -X utf8 corpus/_mkdigest3.py B42 <entry> M <raw> 700 800   # 单源摘要 union_hit 52/52, 分节 16 块\n'
                    u'python -X utf8 corpus/atomcheck.py B42 corpus/_atoms42.txt        # 52 个锚位逐字回源 ok=52 bad=0\n'
                    u'python -X utf8 corpus/_fill42.py               # ⛓解读注: 33 个键逐个复算并与键名断言, 13 项缺席折进 0 键; 实况数取 audit/metrics 口径'))
for pos, txt in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt)
assert len(ins) == 4, [x[1][:30] for x in ins]
t = u'\n'.join(R)

for old, new in [(u'B40 的 0／1／2', u'B40 的 0／1／2')]:
    assert old in t

io.open(F, 'w', encoding='utf-8').write(t)
left = [l for l in t.split(u'\n')
        if re.search(r'41 条|B01\.\.B41|182 602|263 146|2 116|B39／B40／B41 是仅有', l)]
print(u'README 42 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 编码 %s 摘要 %s 保留 %s 码点 %s 推导 %d'
      % (u'/'.join(done), len(left), fmt(enc_all), fmt(dig_all), ret_all, fmt(uniq_all), proofs))
for l in left:
    print(u'  ' + l[:130])
