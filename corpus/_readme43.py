# -*- coding: utf-8 -*-
"""README 记账: 42 条 → 43 条。合计数字全部由 audit 表、metrics 普查与 _f43stats 复算, 不手填。"""
import io, re, sys, os, subprocess

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
b43 = [x.strip() for x in row[u'B43'].split(u'|')]
b43_dig, b43_enc, b43_ret, b43_raw, b43_uniq, b43_cps, b43_cpu = (
    int(b43[0]), int(b43[1]), b43[2], b43[3], int(b43[4]), b43[5], b43[6])
assert (b43_enc, b43_dig, proofs) == (12940, 5057, 385), (b43_enc, b43_dig, proofs)
assert int(b43[9]) == 0 and int(b43[10]) == 0, b43        # T1/T2 与待核都必须为零

m = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/metrics.py'],
                   capture_output=True, text=True, encoding='utf-8')
cen = dict((mm.group(1), int(mm.group(2))) for mm in
           re.finditer(r'^\s{2}([A-Za-z\-]+)\s+([\d ]+)$', m.stdout, re.M))
assert len(cen) == 18, sorted(cen)
ST = dict(l.split(u'\t') for l in io.open(u'corpus/_f43stats.txt', encoding='utf-8').read().split(u'\n') if l)
IN_LAT, OUT_LAT = int(ST[u'in_lat']), int(ST[u'out_lat'])
TAG_LAT = int(ST[u'tag_lat'])
OUT_ALL = OUT_LAT + TAG_LAT                     # 出处标签计入锚外(沿用 B41／B42 口径)
assert cen[u'Latin'] - 86826 == IN_LAT + OUT_ALL, (cen[u'Latin'], IN_LAT, OUT_ALL)

FIRST_IN, FIRST_OUT = 121, 2195                 # 第一代(B01..B10)的锚内 ⇎ 锚外字母


def fmt(n):
    return u'{:,}'.format(int(n)).replace(u',', u' ')


# 第二代累计: 从 README 现行读回, 再加本条增量
mm = re.search(u'第二代（B11–B42）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
               u'全库合计 \\*\\*([\\d ]+)／([\\d ]+)\\*\\*', t)
assert mm, u'第二代行未命中'
prev_in, prev_out = (int(mm.group(1).replace(u' ', u'')), int(mm.group(2).replace(u' ', u'')))
assert prev_in + FIRST_IN == int(mm.group(3).replace(u' ', u'')), mm.group(3)
assert prev_out + FIRST_OUT == int(mm.group(4).replace(u' ', u'')), mm.group(4)
in_lat, out_lat = prev_in + IN_LAT, prev_out + OUT_ALL

cen_s = (u'Latin %s · Han %s · Gen-Punct %s · Arrows %s · CJK-Punct %s · Fullwidth %s · Emoji %s · Math %s · '
         u'Greek %s · Misc-Symbols %s · Dingbats %s · Geometric %s · Hiragana %s · Katakana %s · '
         u'MathAlnum %s · EnclosedIdeo %s · EnclosedSuppl %s · Comb-Diacritic %s') % tuple(
    fmt(cen[k]) for k in [u'Latin', u'Han', u'Gen-Punct', u'Arrows', u'CJK-Punct', u'Fullwidth', u'Emoji',
                          u'Math', u'Greek', u'Misc-Symbols', u'Dingbats', u'Geometric', u'Hiragana',
                          u'Katakana', u'MathAlnum', u'EnclosedIdeo', u'EnclosedSuppl', u'Comb-Diacritic'])

KS = u'／'.join(sorted([k for k in re.findall(r"^ {2}'([^']+)':",
        re.search(u" 'B43': \\{\n(.*?)\n \\},", io.open(u'corpus/audit.py', encoding='utf-8').read(),
                  re.S).group(1), re.M)], key=lambda x: float(x)))
NABS = int(ST[u'n_abs'])
DERIV_KEYS = int(ST[u'deriv_keys'])
assert NABS == 18 and DERIV_KEYS == 20 and len(KS.split(u'／')) == DERIV_KEYS, (NABS, DERIV_KEYS, KS)

PAIRS = [
 (u'共 **42 条**（`babeltele/B01..B42`）', u'共 **43 条**（`babeltele/B01..B43`）'),
 (u'**PASS**（42 条）', u'**PASS**（43 条）'),
 (u'当前 **42 条语料／365 条**推导全部通过（audit 自报“已机检的推导 365 条”）',
  u'当前 **43 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (proofs, proofs)),
 (u'第二代（B11–B42）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B43）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'B39／B40／B41／B42 是仅有的十一条**待核列为 0** 的条目',
  u'B39／B40／B41／B42／B43 是仅有的十二条**待核列为 0** 的条目'),
 (u'／375／0.74／9）', u'／375／0.74／9，B43 的 %s）' % KS),
]
for old, new in PAIRS:
    n = t.count(old)
    if n != 1:
        print(u'注意: 未命中或多处 -> %r (%d)' % (old[:60], n))
    assert n >= 1, old[:60]
    t = t.replace(old, new, 1)

R = t.split(u'\n')
done = []
for i, l in enumerate(R):
    if l.startswith(u'| **合计（42 条）**'):
        R[i] = (u'| **合计（43 条）** | **%s** | **%s**（摘要段合计 %s） | — | **%s** | — |'
                % (fmt(enc_all), ret_all.strip(u'*'), fmt(dig_all), fmt(uniq_all)))
        done.append(u'合计')
        break
for i, l in enumerate(R):
    if l.startswith(u'Latin ') and u'· Han ' in l:
        R[i] = cen_s
        done.append(u'普查')
        break
for i, l in enumerate(R):
    if l.startswith(u'唯一码点 '):
        R[i] = u'唯一码点 %s / %s ≈ %.1f%%' % (fmt(uniq_all), fmt(enc_all), 100.0 * uniq_all / enc_all)
        done.append(u'唯一码点')
        break
for i, l in enumerate(R):
    if l.endswith(u'而不是按窗口比。'):
        R[i] = l + (u'B43 把对照轴再挪一格：两份 raw 是**同一条 url 的两次抓取**——判决书与它的发布页。'
                    u'容器只有 %s 字符，判词却必须两边都数，于是保留率 %s 是这套体裁的必然读数（字节口径 %s，两份合计 %s 字 ⇎ %s 字节）；'
                    u'它省下的是“把网页当成文书引用”这件事：文件名里的日期是听证日、宣判日只在文书里，'
                    u'页眉套语 %d 次给出正文自身的页界，而“第几方”只在正文的编号称谓里。'
                    % (fmt(int(ST[u'raw0_chars'])), b43_ret, b43_raw,
                       fmt(int(ST[u'raw0_chars']) + int(ST[u'raw1_chars'])), fmt(46510), 15))
        done.append(u'口径段')
        break
GEN = (u'**B43 把对照轴换成文书与其发布页**：同一条 url 的两次抓取——judiciary.uk 的发布页（正文 %s 字符）'
       u'⇎ [2026] EWCA Civ 1224 判决全文（%s 字符／810 行）。锚位 %d 个／%d 个不同串（⟦C⟧ %d ⇎ ⟦J⟧ %d），'
       u'判词 %d 行、DERIV %d 键，缺席断言 %d 项折进一个 0 键（判决全文缺 6 项网站字段：Skip to main content／Search／'
       u'Download／.pdf／569.88／H.-D.；发布页缺 12 项法律用词：res judicata／issue estoppel／estoppel／Rome II／'
       u'would allow／handing down／Fifth Party／Georgia…）。三个差值键是这一对文本的签名：'
       u'-v- 的连字写法页 4 ⇎ 文 1（差 3，正文用 “A v B”），全名 OÜ 页 2 而正文只用简称 Spribe（60 次，差 59），'
       u'方括号年 37 比圆括号年多 36（那唯一一处圆括号年是 1843 年的旧报告引证——年份不是识别符）。'
       u'同词同形不同义两处：Court 在页 28 次全是导航清单、在文 57 次是实质用词；页尾 copyright 是网站声明、'
       u'文内 26 次是诉因。每页重印的页眉“Approved by the court for handing down”15 次⇒正文自身可数页界，'
       u'与抓取头部自记页数是两条独立证据。附和第二位法官只一句“I also agree.”（1 次），'
       u'结论用虚拟语气 would allow⇒说理出自一人而拘束力据此判定。客体是一张图（crash game 的 logo，'
       u'“reproduced below”只剩这行字）：B42 那里图是证据，这里图是诉因的对象，丢了图就没有争议标的——'
       u'同为“图不在文本”，可压缩性完全不同。⇒ 容器与内容互不包含，一份不能替代另一份，所以两条 raw 都存。')
for i, l in enumerate(R):
    if l.startswith(u'**B42 把对照轴转向文件内部**'):
        R[i] = l + u'\n\n' + GEN
        done.append(u'B43 段')
        break

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B42 | %s（新建' % fmt(b43_enc if False else 11647)):
        ins.append((i + 1, u'| B43 | %s（新建, 同一 url 的两次抓取 %d 锚／%d 个不同串: 发布页(容器) ⇎ 判决全文; '
                           u'一个零键折 %d 处缺席断言(文缺 6 项网站字段 ⇎ 页缺 %d 项法律用词); '
                           u'三个差值键 -v- 4⇎1、Spribe−OÜ＝%d、方括号年−圆括号年＝%d; '
                           u'同词不同义 Court %d(导航)⇎%d(实质)、copyright 页尾声明⇎诉因 %d; '
                           u'页眉套语 %d 次给出正文自身页界, 文件名里的日期是听证日） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为机构名与引用格式） | %s | %s |'
                           % (fmt(b43_enc), int(ST[u'anchors']), int(ST[u'uniq_anchor']), NABS, NABS - 6,
                              59, 36, 28, 57, 26, 15,
                              int(ST[u'anchors']), fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b43_ret, fmt(b43_dig))))
    elif l.startswith(u'| B42 | %s | 177.7%%' % fmt(11647)):
        ins.append((i + 1, u'| B43 | %s | %s | %s（字节口径; 发布页正文 %s 字 ⇎ 判决全文 %s 字, 合计 %s 字 ⇎ 文件 %s 字节——'
                           u'保留率高于全库是容器条的结构性结果: 页侧只 %s 字可索引, 判词必须自建对照） | %d | %s |'
                           % (fmt(b43_enc), b43_ret, b43_raw, fmt(int(ST[u'raw0_chars'])),
                              fmt(int(ST[u'raw1_chars'])),
                              fmt(int(ST[u'raw0_chars']) + int(ST[u'raw1_chars'])),
                              fmt(os.path.getsize(u'corpus/raw/prose/law_aviator_spribe.txt') +
                                   os.path.getsize(u'corpus/raw/prose/law_ewca_aviator.txt')),
                              fmt(int(ST[u'raw0_chars'])), b43_uniq, b43_cpu)))
    elif l.startswith(u'| B42 | `raw/prose/csb_marathon_martinez.txt`'):
        ins.append((i + 1, u'| B43 | `raw/prose/law_aviator_spribe.txt`（judiciary.uk 案件发布页, 容器: 标题里的当事人串、'
                           u'Related content／Download／文件名 2026-EWCA-Civ-1224-…-H.-D.-22nd-September-2026.pdf／'
                           u'体积 569.88 kb, 正文 %s 字符）⇎ `raw/prose/law_ewca_aviator.txt`'
                           u'（[2026] EWCA Civ 1224 Aviator LLC & Ors v Spribe OÜ 判决全文, %s 字符／810 行, '
                           u'同一 url、两次抓取） | 容器 ⇎ 内容互不包含：%d 项缺席折进 0 键（文缺网站字段 6 项、'
                           u'页缺法律用词 %d 项）; 文件名里编的是听证日而宣判日只在文书里; '
                           u'页眉 “Approved by the court for handing down” %d 次⇒正文自身页界; '
                           u'当事人写法三套（标题 -v- 4 次 ⇎ 正文 A v B ⇎ 编号称谓 Fifth Party %d 次）; '
                           u'争点术语 issue estoppel %d ⇎ res judicata %d ⇎ estoppel %d、Rome II %d、诉因 copyright %d; '
                           u'拉丁术语首现各挂一次英语 gloss(lex loci protectionis／lex fori); '
                           u'方括号年 %d ⇎ 圆括号年 1（1843 旧报告）⇒引用格式自述定位方式; '
                           u'客体是一张图（crash game 在 Georgia, %d／%d 次）, 转本丢的是诉因对象; '
                           u'附和 1 次＋虚拟语气 would allow⇒说理出自一人 |'
                           % (fmt(int(ST[u'raw0_chars'])), fmt(int(ST[u'raw1_chars'])), NABS, NABS - 6,
                              15, 11, 23, 8, 30, 27, 26, 37, 10, 9)))
    elif l.startswith(u'python -X utf8 corpus/_fill42.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_mkB43.py                # 建条目: 锚点从“空白折叠＋剔 url 行”的正文切片(逐字由构造保证), 计数一律走 audit 的 _reason 口径(含 url 行)\n'
                    u'python -X utf8 corpus/_mkdigest3.py B43 <entry> C <page raw> 260 300 J <judgment raw> 260 300   # 两源分节摘要 union_hit 31/31, 13 块\n'
                    u'python -X utf8 corpus/atomcheck.py B43 corpus/_atoms43.txt        # 31 个锚位逐字回源 ok=31 bad=0\n'
                    u'python -X utf8 corpus/_fill43.py               # ⛓解读注: 20 个键逐个复算并与键名断言, %d 项缺席折进 0 键; 实况数取 audit/metrics 口径' % NABS))
for pos, txt in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt)
assert len(ins) == 4, [x[1][:30] for x in ins]
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if re.search(r'42 条|B01\.\.B42|194 249|269 702|2 122|B39／B40／B41／B42 是仅有|365 条|86 826', l)]
print(u'README 43 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 编码 %s 摘要 %s 保留 %s 码点 %s 推导 %d｜第二代 %s／%s'
      % (u'/'.join(done), len(left), fmt(enc_all), fmt(dig_all), ret_all, fmt(uniq_all), proofs,
         fmt(in_lat), fmt(out_lat)))
for l in left:
    print(u'  ' + l[:150])
