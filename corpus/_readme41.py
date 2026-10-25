# -*- coding: utf-8 -*-
"""README 记账: 40 条 → 41 条。合计数字全部由 audit 表与 metrics 普查复算, 不手填。"""
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
t = io.open(F, encoding='utf-8').read()

# --- 由 audit 输出复算全库合计与 B41 指标(不手填) ---
import subprocess
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-400:]
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
assert len(allc) >= 5, allc
dig_all, enc_all, ret_all, uniq_all = (int(allc[0].replace(u' ', u'')), int(allc[1].replace(u' ', u'')),
                                       allc[2], int(allc[4]))
assert u'PASS' in p.stdout
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
b41 = [x.strip() for x in row[u'B41'].split(u'|')]
b41_dig, b41_enc, b41_ret, b41_raw, b41_uniq, b41_cps = (int(b41[0]), int(b41[1]), b41[2], b41[3],
                                                          int(b41[4]), b41[6])
assert b41_enc == 10379 and b41_dig == 12742 and uniq_all == 2116, (b41_enc, b41_dig, uniq_all)
assert proofs == 333, proofs

m = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/metrics.py'],
                   capture_output=True, text=True, encoding='utf-8')
cen = dict((mm.group(1), int(mm.group(2))) for mm in
           re.finditer(r'^\s{2}([A-Za-z\-]+)\s+([\d ]+)$', m.stdout, re.M))
assert len(cen) == 18, sorted(cen)
assert cen[u'Latin'] - 75919 == 5084 + 175, cen[u'Latin']


def fmt(n):
    return u'{:,}'.format(n).replace(u',', u' ')


cen_s = (u'Latin %s · Han %s · Gen-Punct %s · Arrows %s · CJK-Punct %s · Fullwidth %s · Emoji %s · Math %s · '
         u'Greek %s · Misc-Symbols %s · Dingbats %s · Geometric %s · Hiragana %s · Katakana %s · '
         u'MathAlnum %s · EnclosedIdeo %s · EnclosedSuppl %s · Comb-Diacritic %s') % tuple(
    fmt(cen[k]) for k in [u'Latin', u'Han', u'Gen-Punct', u'Arrows', u'CJK-Punct', u'Fullwidth', u'Emoji',
                          u'Math', u'Greek', u'Misc-Symbols', u'Dingbats', u'Geometric', u'Hiragana',
                          u'Katakana', u'MathAlnum', u'EnclosedIdeo', u'EnclosedSuppl', u'Comb-Diacritic'])

# 第一代(B01–B10)的锚内/锚外差额沿用 README 既有值: 71 088−70 967=121, 4 831−2 636=2 195
FIRST_IN, FIRST_OUT = 71088 - 70967, 4831 - 2636
in_lat = 70967 + 5084
out_lat = 2636 + 175

R = []
R.append((u'共 **40 条**（`babeltele/B01..B40`）', u'共 **41 条**（`babeltele/B01..B41`）'))
R.append((u'**PASS**（40 条）', u'**PASS**（41 条）'))
R.append((u'当前 **29 个 tag／249 条**推导全部通过',
          u'当前 **41 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (proofs, proofs)))
R.append((u'第二代（B11–B40）锚内字母 **70 967**、锚外 **2 636**；全库合计 **71 088／4 831**',
          u'第二代（B11–B41）锚内字母 **%d**、锚外 **%d**；全库合计 **%d／%d**'
          % (in_lat, out_lat, in_lat + FIRST_IN, out_lat + FIRST_OUT)))
R.append((u'| **合计（40 条）** | **172 223** | **68.8%**（摘要段合计 250 404） | — | **2 101** | — |',
          u'| **合计（41 条）** | **%s** | **%s**（摘要段合计 %s） | — | **%s** | — |'
          % (fmt(enc_all), ret_all.strip('*'), fmt(dig_all), fmt(uniq_all))))
R.append((u'唯一码点 2 101 / 172 223 ≈ 1.2%',
          u'唯一码点 %s / %s ≈ %.1f%%' % (fmt(uniq_all), fmt(enc_all), 100.0 * uniq_all / enc_all)))
R.append((u'Latin 75 919 · Han 48 236 · Gen-Punct 1 548 · Arrows 1 311 · CJK-Punct 948 · Fullwidth 618 · '
          u'Emoji 449 · Math 243 · Greek 71 · Misc-Symbols 48 · Dingbats 31 · Geometric 30 · Hiragana 18 · Katakana 13',
          cen_s))
R.append((u'B39／B40 是仅有的九条**待核列为 0** 的条目',
          u'B39／B40／B41 是仅有的十条**待核列为 0** 的条目'))
R.append((u'B40 的 0／1／2／3／4／5／6／7／8／9.1／10／11／12／13／14／15／17／31／36／42）',
          u'B40 的 0／1／2／3／4／5／6／7／8／9.1／10／11／12／13／14／15／17／31／36／42，'
          u'B41 的 0／1／2／3／4／6／8／9／10／12／13／14／18／22／26／36／44／2.6）'))
R.append((u'而不是按“少说了多少话”来读。',
          u'而不是按“少说了多少话”来读。B41 是这一口径的对照组：两源之间跨文件同命中只有 8 个串／13 个锚位（占锚数 14.1%%），'
          u'重复文本几乎无可省，所以它的保留率 %s 表示的是“两段文本各自都得存”；'
          u'它省下来的是**判定**——机关宣布 2 项改动，逐字对齐看到的是 4 类（3 处字级＋1 项删除＋1 列前移＋1 处方括号改写），'
          u'而这类差额是通读回应段永远看不见的。' % b41_ret))

# B41 体裁段(接在 B40 段之后)
R.append((u'两份脚注对同一个词一个加引号一个不加，而规范化把这一差别抹平 ⇒ 引号级飘移只能靠逐字锚保留。',
          u'两份脚注对同一个词一个加引号一个不加，而规范化把这一差别抹平 ⇒ 引号级飘移只能靠逐字锚保留。\n\n'
          u'**B41 把对照轴换成时间**：同一个案号（FDA-2025-N-1243）的两端——拟议令 90 FR 24540 ⇎ 最终令 91 FR 53184，'
          u'相隔 14 个月（机检：年份差折月加月序差）。这里没有对手，可读的是**宣布的改动 ⇎ 实测的差集**：'
          u'最终令自我清单只写 2 项，逐字对齐看到的是 3 处字级改动（“提供”→“包含”2 处＋删净的“提供自研究”1 处）、'
          u'1 项整条删除、1 列序号整体前移、1 处没人宣布的方括号改写；删除不留缺口，于是同一个 '
          u'`Sec. 864.1890(b)(1)(viii)` 在两份里指不同条文（试剂稳定性 ⇎ 标本稳定性）⇒ **引条文号必须附文件身份**；'
          u'被删的那一项带走了它专属的测量词（光稳定性／杂交后信号在最终令各 0 次）⇒ 此后再检索这两个词就找不到该要求，'
          u'因为它被并进了通用质量体系条款；记录一边倒（反对式／不支持／反对三式两源皆 0）仍产生未宣布的改动；'
          u'13 条编号意见 ⇎ 不足 5 名进言者（比值 2.6 由机关的拆分规则产生）⇒ 按条数统计立场会把一个人的四件事读成四家公司；'
          u'第一人称的许可写在摘要段的定义括号里（括号写了才有 4 次“我们的”，否则 0）；'
          u'义务强度按“谁已在市场上”分档（同一节里“须取得许可” ⇎ “机关预期”）；'
          u'“第五节”在两源不是同一节（风险 ⇎ 环境影响，裸用 9 次 ⇎ 1 次）；'
          u'风险表只留在拟议令，而抓取痕迹替我们作证：表格竖线 2 处 ⇎ 0 处；'
          u'算法词汇（人工智能／机器学习／数字病理／算法／器械专属）只从程序段进来，控制条文一字未改；'
          u'联系人块逐字相同而邮箱位置是不可读的混淆实体串（at 符号两源 0 次）⇒ “可核”与“可联系”是两件事。'))

rows = t.split(u'\n')

# 条目明细表
i = [k for k, l in enumerate(rows) if l.startswith(u'| B40 | 10 077（新建')]
assert len(i) == 1, i
rows.insert(i[0] + 1,
            u'| B41 | %s（新建, 两源 92 锚: 同一案号的拟议令 ⇎ 最终令 ⟦P⟧⇎⟦F⟧; '
            u'**8 个串／13 个锚位跨文件同命中**——那是“两端一字未动”的条文而不是误标; '
            u'一个零键折 %d 处缺席断言（⟦P⟧ 27 ⇎ ⟦F⟧ 7）; 序号漂移用一对“只差一个罗马号”的同串锚证明, '
            u'自述改动数 2 ⇎ 实测 4 类全部落在 %d 个键内） | 92 | 5 084 | '
            u'175（其中 132 为出处标签, 余 43 为条文号与 FR 页码标识） | %s | %s |'
            % (fmt(b41_enc), 34, 18, b41_ret, fmt(b41_dig)))

# 长条目表(保留率表)
i = [k for k, l in enumerate(rows) if l.startswith(u'| B40 | 10 077 | 65.9%')]
assert len(i) == 1, i
rows.insert(i[0] + 1,
            u'| B41 | %s | %s | %s（字节口径; 两源正文合计 128 840 字, 编码为其 8.1%%——'
            u'同命中的串只占锚位 14.1%%, 几乎无重复可省, 故保留率高于同族条目） | %d | %s |'
            % (fmt(b41_enc), b41_ret, b41_raw, b41_uniq, b41_cps))

# 详解表
i = [k for k, l in enumerate(rows) if l.startswith(u'| B40 | `raw/prose/fr_fda_cardio_ml_notification.txt`')]
assert len(i) == 1, i
rows.insert(i[0] + 1,
            u'| B41 | `raw/prose/fr_fda_ish_proposed_order.txt`（90 FR 24540–24549, 2025-06-11 刊发, '
            u'文件号 2025-10549, 案号 FDA-2025-N-1243, 21 CFR 864.1890, 意见期止 2025-08-11, 72 600 字符）⇎ '
            u'`raw/prose/fr_fda_ish_final_order.txt`（91 FR 53184–53191, 2026-08-17 刊发, 2026-16727, 同案号, '
            u'新设同一条, 生效 2026-09-16＝刊发后 30 日, 56 240 字符） | '
            u'同一案号两端的差集：程序状态只写在类型行；署名行逐字相同而签署日期块整行消失；'
            u'多出一整节回应的最终令反而少 2 页（10⇎8）；13 条编号意见⇎不足 5 名进言者（2.6＝13÷5）；'
            u'支持记录一边倒仍改 3 处字、删 1 项、整列前移 1 位；(ix)⇎(viii) 同串⇒同一个号在两份里指不同条文；'
            u'自我清单 2 项⇎实测 4 类；“须取得许可”⇎“机关预期”按是否在market分档；'
            u'“第五节”两源所指不同（裸用 9⇎1）；风险表只在拟议令（竖线残留 2⇎0）；'
            u'方括号改写全库唯一 1 处；算法措辞 6 处全在程序段而控制条文 0；'
            u'替代样本让步句尾挂“由机关判定”⇒放宽只写在逗号前；'
            u'“一条意见”起句 12 次＋“机关”别称 22⇎36 次⇒第一人称由定义括号授权；'
            u'两源上市前通知缩写合计 44 次；14 个月两份文件而联系块逐字复用、邮箱是不可读实体串（at 两源 0） |')

# 复核方式命令
i = [k for k, l in enumerate(rows) if l.startswith(u'python -X utf8 corpus/_fill40.py')]
assert len(i) == 1, i
rows.insert(i[0] + 1,
            u'python -X utf8 corpus/_mkraw41.py              # federalregister.gov 的 full_text .txt(实为 HTML 的 body 内 pre) → 两份 raw, 各自重算 chars/text_sha256\n'
            u'python -X utf8 corpus/_mkB41.py                # 建条目: 92 锚装配后逐条按标签回源做规范化子串断言; 锚外 Latin 一律 scrub 成中文(保留 175 字母=132 标签+43 条文号)\n'
            u'python -X utf8 corpus/_mkdigest3.py B41 <entry> P <proposed raw> 240 320 F <final raw> 240 320   # 两源分节摘要 union_hit 92/92\n'
            u'python -X utf8 corpus/_wire41.py               # 幂等接线: SRC/ATOM/DERIV(18 键, 零键折 34 处缺席; 缺席短语一律按词组写 \\s+ 以跨硬换行)+atomcheck\n'
            u'python -X utf8 corpus/_fill41.py               # ⛓解读注: 18 个键逐个复算并与键名断言, 抓取痕迹(分页记号/脚注标记/硬换行/竖线/实体串)全部实测')
t = u'\n'.join(rows)

for old, new in R:
    n = t.count(old)
    assert n == 1, (n, old[:70])
    t = t.replace(old, new, 1)

io.open(F, 'w', encoding='utf-8').write(t)
left = [l for l in t.split(u'\n')
        if re.search(r'40 条|B01\.\.B40|2 092|2 101|172 223|250 404|75 919|48 236|九条|70 967|29 个 tag', l)]
print(u'README 41 条完成; 残留旧计数行 %d｜audit: 编码 %s 摘要 %s 保留 %s 码点 %s 推导 %d'
      % (len(left), fmt(enc_all), fmt(dig_all), ret_all, fmt(uniq_all), proofs))
for l in left:
    print(u'  ' + l[:130])
