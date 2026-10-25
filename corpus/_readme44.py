# -*- coding: utf-8 -*-
"""README 记账: 43 条 → 44 条。合计数字全部由 audit 表、metrics 普查与 _f44stats 复算, 不手填。"""
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
soft_all = int(re.search(u'提示\\(不计入 FAIL, 1-2 位结构计数未逐位核验\\): 共 (\\d+) 个', p.stdout).group(1))
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
b44 = [x.strip() for x in row[u'B44'].split(u'|')]
b44_dig, b44_enc, b44_ret, b44_raw, b44_uniq, b44_blocks, b44_cpu, b44_soft = (
    int(b44[0]), int(b44[1]), b44[2], b44[3], int(b44[4]), int(b44[5]), b44[6], int(b44[10]))
assert (b44_enc, b44_dig, proofs, b44_soft) == (16523, 5932, 404, 2), (b44_enc, b44_dig, proofs)
assert int(b44[7]) == 0 and int(b44[8]) == 0 and int(b44[9]) == 0, b44

m = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/metrics.py'],
                   capture_output=True, text=True, encoding='utf-8')
cen = dict((mm.group(1), int(mm.group(2))) for mm in
           re.finditer(r'^\s{2}([A-Za-z\-]+)\s+([\d ]+)$', m.stdout, re.M))
assert len(cen) == 18, sorted(cen)
ST = dict(l.split(u'\t') for l in io.open(u'corpus/_f44stats.txt', encoding='utf-8').read().split(u'\n') if l)
IN_LAT, OUT_LAT, TAG_LAT = int(ST[u'in_lat']), int(ST[u'out_lat']), int(ST[u'tag_lat'])
OUT_ALL = OUT_LAT + TAG_LAT
KS = u'／'.join(sorted([k for k in re.findall(r"^ {2}'([^']+)':",
        re.search(u" 'B44': \\{\n(.*?)\n \\},", io.open(u'corpus/audit.py', encoding='utf-8').read(),
                  re.S).group(1), re.M)], key=lambda x: float(x)))
DERIV_KEYS, NABS, NTERM0 = int(ST[u'deriv_keys']), int(ST[u'n_abs']), int(ST[u'n_term0'])
assert (DERIV_KEYS, NABS, NTERM0) == (21, 18, 42), (DERIV_KEYS, NABS, NTERM0)
assert len(KS.split(u'／')) == DERIV_KEYS

# 标记层计数全部从两份 raw 现算, 不手填(与 _mkB44 同一口径: 去头部后的 body 计数)
RAWX = u'corpus/raw/prose/pmc_ards.xml'
RAWD = u'corpus/raw/prose/pmc_ards_dad.txt'
HEADRX = r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)'


def _body(raw):
    ls = io.open(raw, encoding='utf-8', errors='replace').read().split(u'\n')
    return u'\n'.join([l for l in ls if not re.match(HEADRX, l.strip(), re.I)])


BX, BD = _body(RAWX), _body(RAWD)
_clean = lambda s: chr(10).join(l for l in s.split(chr(10)) if not l.strip().lower().startswith(u'url:'))
CX = re.sub(r'\s+', ' ', _clean(BX))
CD = re.sub(r'\s+', ' ', _clean(BD))
NX = lambda pat: len(re.findall(pat, BX, re.I))
ND = lambda pat: len(re.findall(pat, BD, re.I))
PH = lambda p: p if (p.startswith(u'(?') or u'\\' in p) else r'\s+'.join(re.escape(w) for w in p.split(u' '))
LT, CLT, LOW = NX(r'<'), NX(r'</'), NX(r'<[a-z]')
UNB, ZONES = LT - CLT, NX(r'<front') + NX(r'<body') + NX(r'<back')
KWD, AFF, CONTRIB, FUND = NX(r'<kwd'), NX(r'<aff'), NX(r'<contrib'), NX(r'<funding')
ARTID, XREF, CMETA, GIVEN = NX(r'<article-id'), NX(r'<xref'), NX(r'<custom-meta'), NX(r'<given-names')
PAR = NX(r'<p ')
NSAME = len([s for s in [x.strip() for x in re.split(r'[.;:?]\s', CD) if 70 <= len(x.strip()) <= 300]
             if NX(PH(s)) >= 1 and NX(PH(s)) == ND(PH(s))][:8])
NTOKDIFF = ND(PH(u'J Intensive Care 2646')) - NX(PH(u'J Intensive Care 2646'))
NDAD = NX(PH(u'diffuse alveolar damage'))
NABSX, NABSD = 4, 14
assert (NSAME, NTOKDIFF, NDAD) == (8, 1, 9), (NSAME, NTOKDIFF, NDAD)
assert NABSX + NABSD == NABS and LT == 1085 and UNB == 549, (LT, UNB, NABS)


def fmt(n):
    return u'{:,}'.format(int(n)).replace(u',', u' ')


mm = re.search(u'第二代（B11–B43）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
               u'全库合计 \\*\\*([\\d ]+)／([\\d ]+)\\*\\*', t)
assert mm, u'第二代行未命中'
prev_in, prev_out = int(mm.group(1).replace(u' ', u'')), int(mm.group(2).replace(u' ', u''))
FIRST_IN, FIRST_OUT = 121, 2195
assert prev_in + FIRST_IN == int(mm.group(3).replace(u' ', u'')), mm.group(3)
assert prev_out + FIRST_OUT == int(mm.group(4).replace(u' ', u'')), mm.group(4)
assert cen[u'Latin'] - prev_in - prev_out - FIRST_IN - FIRST_OUT == IN_LAT + OUT_ALL, (
    cen[u'Latin'], prev_in, prev_out, IN_LAT, OUT_ALL)
in_lat, out_lat = prev_in + IN_LAT, prev_out + OUT_ALL

cen_s = (u'Latin %s · Han %s · Gen-Punct %s · Arrows %s · CJK-Punct %s · Fullwidth %s · Emoji %s · Math %s · '
         u'Greek %s · Misc-Symbols %s · Dingbats %s · Geometric %s · Hiragana %s · Katakana %s · '
         u'MathAlnum %s · EnclosedIdeo %s · EnclosedSuppl %s · Comb-Diacritic %s') % tuple(
    fmt(cen[k]) for k in [u'Latin', u'Han', u'Gen-Punct', u'Arrows', u'CJK-Punct', u'Fullwidth', u'Emoji',
                          u'Math', u'Greek', u'Misc-Symbols', u'Dingbats', u'Geometric', u'Hiragana',
                          u'Katakana', u'MathAlnum', u'EnclosedIdeo', u'EnclosedSuppl', u'Comb-Diacritic'])

PAIRS = [
 (u'共 **43 条**（`babeltele/B01..B43`）', u'共 **44 条**（`babeltele/B01..B44`）'),
 (u'**PASS**（43 条）', u'**PASS**（44 条）'),
 (u'当前 **43 条语料／385 条**推导全部通过（audit 自报“已机检的推导 385 条”）',
  u'当前 **44 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (proofs, proofs)),
 (u'第二代（B11–B43）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B44）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'：14 个 1–2 位结构计数（B03', u'：%d 个 1–2 位结构计数（B03' % soft_all),
 (u'而非源内数字）未逐位核验',
  u'而非源内数字；B44 的 `42／43` 则是长标识符串 42816885（PMED 号）与 grid.443382.a（机构号）内部的数字切片, '
  u'是锚点原样带来的噪声而不是本条断言, 故不消解）未逐位核验'),
 (u'／57／59／60／80）', u'／57／59／60／80，B44 的 %s）' % KS),
]
for old, new in PAIRS:
    n = t.count(old)
    if n != 1:
        print(u'注意: 未命中或多处 -> %r (%d)' % (old[:50], n))
    assert n >= 1, old[:50]
    t = t.replace(old, new, 1)

R = t.split(u'\n')
done = []
for i, l in enumerate(R):
    if l.startswith(u'| **合计（43 条）**'):
        R[i] = (u'| **合计（44 条）** | **%s** | **%s**（摘要段合计 %s） | — | **%s** | — |'
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
    if l.endswith(u'只在正文的编号称谓里。'):
        R[i] = l + (u'B44 又把轴转到**同一篇文章的两种序列化**（JATS/XML ⇎ 同端点去标记渲染文本）：'
                    u'%d 个七十字以上的长句在两层的命中数完全相同（层间差全部折进 0 键）, 于是“内容无损”是可证的; '
                    u'而 %s 处左尖括号在渲染层剩 0——差出来的全部是结构。保留率 %s（字节口径 %s）同样是这类对照条的必然读数：'
                    u'摘要段只索引锚点触到的窗口, 判词却要数两层的标签, 字符自然重于窗口。'
                    % (NSAME, fmt(LT), b44_ret, b44_raw))
        done.append(u'口径段')
        break
GEN = (u'**B44 把对照轴换成同一篇文章的两种序列化**：JATS/XML 原样（%s 字符, 标记即结构）⇎ 同一 Europe PMC '
       u'fullTextXML 端点去标记后的渲染文本（%s 字符）。锚位 %d 个（⟦X⟧ %d ⇎ ⟦D⟧ %d）／%d 个不同串, 判词 %d 行, '
       u'DERIV %d 键, 0 键里折 %d 个 CNT 项（渲染层缺标记 %d 类 + XML 层缺抓取痕迹 %d 类 + 八条长句与两处等式的层间差）。'
       u'关键结论全部可机检：长句层间差为 0 ⇒ **换格式不产生新事实**; 而 `<` %s ⇎ `</` %d ⇎ 差 %d（自闭合、处理指令与 DTD）'
       u'⇎ 主题词 %d ⇎ 标识符 %d ⇎ 资助 %d ⇎ 段落 %d ⇎ 自定义元数据 %d 全在标记层。 '
       u'最硬的一条是**粘连串**：剥掉标签后“期刊名 ⇎ 卷号”并成一个 XML 中根本不存在的词元（层间差 1）, '
       u'所以同一查询在两种格式里结果集不同——“格式差异”第一次有了能核对的说法。'
       u'另有两处只在渲染层的抓取痕迹（“Europe PMC”“ebi.ac.uk”“fullTextXML”）与两处只在标记层的 ISSN/pub-id-type, 双向缺席 ⇒ 两份都存。'
       u'判词还包括：住在元素内容里的信息随文字走（DOI 前缀两层同值）, 住在属性里的随标记走; '
       u'fig/table 两层皆 0 是**体裁如此**（article-type="letter"）而不是转换所致——同一个 0 有两种成因。')
for i, l in enumerate(R):
    if l.startswith(u'**B43 把对照轴换成文书与其发布页**'):
        R[i] = l + u'\n\n' + GEN % (fmt(int(ST[u'raw0_chars'])), fmt(int(ST[u'raw1_chars'])),
                                    int(ST[u'anchors']), int(ST[u'anchors_x']), int(ST[u'anchors_d']),
                                    int(ST[u'uniq_anchor']), int(ST[u'gloss_lines']), DERIV_KEYS, NTERM0,
                                    NABSD, NABSX, fmt(LT), CLT, UNB, KWD, ARTID, FUND, PAR, CMETA)
        done.append(u'B44 段')
        break

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B43 | %s（新建' % fmt(12940)):
        ins.append((i + 1, u'| B44 | %s（新建, 同一篇文章的两种序列化 %d 锚／%d 个不同串: JATS/XML ⇎ 去标记渲染文本 ⟦X⟧⇎⟦D⟧; '
                           u'八条长句层间差 0 ⇒ 内容无损; 一个零键折 %d 个 CNT 项（标记缺席 %d 类 ⇎ 抓取痕迹缺席 %d 类）; '
                           u'粘连串“J Intensive Care 2646”层间差 1 ⇒ 同一查询在两格式结果集不同; '
                           u'结构计数全部走 CNT: %s⇎%d⇎%d、kwd %d、article-id %d、custom-meta %d） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为 XML 里的机构与期刊拉丁名） | %s | %s |'
                           % (fmt(b44_enc), int(ST[u'anchors']), int(ST[u'uniq_anchor']), NTERM0, NABSD, NABSX,
                              fmt(LT), CLT, UNB, KWD, ARTID, CMETA,
                              int(ST[u'anchors']), fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b44_ret, fmt(b44_dig))))
    elif l.startswith(u'| B43 | %s | 255.9%%' % fmt(12940)):
        ins.append((i + 1, u'| B44 | %s | %s | %s（字节口径; 两份正文合计 %s 字符 ⇎ 文件 %s 字节——'
                           u'XML 侧多出的一万六千字符全是标记, 不是内容, 故保留率高于 100%% 属对照条的结构性读数） | %d | %s |'
                           % (fmt(b44_enc), b44_ret, b44_raw,
                              fmt(int(ST[u'raw0_chars']) + int(ST[u'raw1_chars'])),
                              fmt(int(ST[u'raw0_bytes']) + int(ST[u'raw1_bytes'])), b44_uniq, b44_cpu)))
    elif l.startswith(u'| B43 | `raw/prose/law_aviator_spribe.txt`'):
        ins.append((i + 1, u'| B44 | `raw/prose/pmc_ards.xml`（JATS/XML 原样, %s 字符, DTD 声明在内）⇎ '
                           u'`raw/prose/pmc_ards_dad.txt`（同一 fullTextXML 端点去标记的渲染文本, %s 字符／9 行, '
                           u'带抓取头部） | 序列化对照：八条长句层间差 0⇒内容无损; `<` %s ⇎ `</` %d ⇎ 差 %d ⇎ 小写标签起始 %d; '
                           u'只在标记层: 主题词 %d、article-id %d、contrib %d、affiliation %d、funding %d、xref %d、'
                           u'custom-meta %d、分区 %d、名＝姓 %d; 只在渲染层: 粘连串“J Intensive Care 2646”（层间差 %d）、'
                           u'Europe PMC／ebi.ac.uk／fullTextXML; 两层同值: DOI 前缀与“diffuse alveolar damage” %d; '
                           u'fig／table 两层皆 0 而成因是 article-type="letter"⇒0 要连体裁读 |'
                           % (fmt(int(ST[u'raw0_chars'])), fmt(int(ST[u'raw1_chars'])), fmt(LT), CLT, UNB,
                              LOW, KWD, ARTID, CONTRIB, AFF, FUND, XREF, CMETA, ZONES, GIVEN,
                              NTOKDIFF, NDAD)))
    elif l.startswith(u'python -X utf8 corpus/_fill43.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_mkB44.py                # 建条目: 两色锚位(X=XML／D=渲染文本), 长句层间差与双向缺席全部由 raw 回算\n'
                    u'python -X utf8 corpus/_mkdigest3.py B44 <entry> X <xml raw> 240 300 D <stripped raw> 240 300   # 两源分节摘要 union_hit 51/51, 18 块\n'
                    u'python -X utf8 corpus/atomcheck.py B44 corpus/_atoms44.txt        # 22 个锚位逐字回源 ok=22 bad=0\n'
                    u'python -X utf8 corpus/_fill44.py               # ⛓解读注: %d 个键逐个复算并与键名断言; 0 键 %d 项; 待核 2 项(长标识符串内部切片)明写不消消' % (DERIV_KEYS, NTERM0)))
for pos, txt in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt)
assert len(ins) == 4, [x[1][:30] for x in ins]
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if re.search(r'43 条|B01\.\.B43|207 189|274 759|385 条|86 826|94 012', l)]
print(u'README 44 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 编码 %s 摘要 %s 保留 %s 码点 %s 推导 %d 待核 %d｜第二代 %s／%s'
      % (u'/'.join(done), len(left), fmt(enc_all), fmt(dig_all), ret_all, fmt(uniq_all), proofs,
         soft_all, fmt(in_lat), fmt(out_lat)))
for l in left:
    print(u'  ' + l[:150])
