# -*- coding: utf-8 -*-
"""README 记账: 45 条 → 46 条。合计数字全部由 audit 表、metrics 普查、raw 回算与 _f46stats 复算, 不手填。"""
import io, re, sys, os, ast, json, subprocess

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
NENT = len(row) - 1
cells = lambda tag: [x.strip() for x in row[tag].split(u'|')]
b46 = cells(u'B46')
b45 = cells(u'B45')
b46_enc, b46_dig, b46_ret, b46_raw, b46_uniq, b46_blocks, b46_cpu, b46_soft = (
    int(b46[1]), int(b46[0]), b46[2], b46[3], int(b46[4]), int(b46[5]), b46[6], int(b46[10]))
b45_enc, b45_dig, b45_ret, b45_raw = int(b45[1]), int(b45[0]), b45[2], b45[3]
assert b46_soft == 0, b46
assert NENT == 46, NENT
assert int(b46[7]) == 0 and int(b46[8]) == 0 and int(b46[9]) == 0, b46
assert not re.search(u'^\\s+B46 \\[', p.stdout, re.M), u'B46 不该出现在待核清单'

m = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/metrics.py'],
                   capture_output=True, text=True, encoding='utf-8')
cen = dict((mm.group(1), int(mm.group(2))) for mm in
           re.finditer(r'^\s{2}([A-Za-z\-]+)\s+([\d ]+)$', m.stdout, re.M))
assert len(cen) == 18, sorted(cen)


def loadstat(fn):
    d = {}
    for l in io.open(fn, encoding='utf-8').read().split(u'\n'):
        if u'\t' in l:
            k, v = l.split(u'\t')
            d[k] = v
    return d


ST = loadstat(u'corpus/_f46stats.txt')
NUM = lambda k: ast.literal_eval(ST[k]) if ST[k].strip().startswith(u'[') else int(ST[k])
IN_LAT, OUT_LAT, TAG_LAT = int(ST[u'in_lat']), int(ST[u'out_lat']), int(ST[u'tag_lat'])
OUT_ALL = OUT_LAT + TAG_LAT
ANCH, UANCH = int(ST[u'anchors']), int(ST[u'uniq_anchor'])
DERIV_KEYS, NTERM0, NTERMS0 = int(ST[u'deriv_keys']), int(ST[u'n_term0']), int(ST[u'n_terms0'])
NABS, NEQU, NDIFF, GLOS = int(ST[u'n_absent']), int(ST[u'n_equ']), int(ST[u'n_diff']), int(ST[u'gloss_lines'])
AESC, APAP = NABS - 13, 13          # 目录侧缺席 13 类, 原文侧 = 余下
assert AESC == 9 and APAP == 13 and NABS + NEQU == NTERMS0
KS = u'／'.join(sorted([k for k in re.findall(r"^ {2}'([^']+)':",
        re.search(u" 'B46': \\{\n(.*?)\n \\},", io.open(u'corpus/audit.py', encoding='utf-8').read(),
                  re.S).group(1), re.M)], key=lambda x: float(x)))
assert len(KS.split(u'／')) == DERIV_KEYS

# —— 两个源的全部计数现算, 与 _mkB46/_fill46 同一口径 ——
RJ = u'corpus/raw/api/bio_recent_2026w01.json'
RP = u'corpus/raw/prose/biorxiv_bacterial_organelles.txt'
RAWS = [RJ, RP]
TXT = [io.open(x, encoding='utf-8', errors='replace').read() for x in RAWS]
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
SRC = [u'\n'.join(l for l in x.split(u'\n') if not HEADRX.match(l.strip())) for x in TXT]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
RCOT = lambda i: len(SRC[i].strip())
BYTES = [os.path.getsize(x) for x in RAWS]
FULL = [len(x) for x in TXT]
BS = u'\\'
DOI_E = u'10.1101' + BS + u'/2025.09.22.677801'
DOI_P = u'10.1101/2025.09.22.677801'
ROWS = json.loads(SRC[0])[u'collection']
ENVD = json.loads(SRC[0])[u'messages'][0]
PUBS = [r[u'published'] for r in ROWS if str(r[u'published']).startswith(u'10.')]
CHP = int(re.search(u'chars: (\\d+)', TXT[1]).group(1))
N_PLAIN_P, N_PLAIN_J = CNT(re.escape(DOI_P), 1), CNT(re.escape(DOI_P), 0)
N_ESC_J, N_ESC_P = CNT(re.escape(DOI_E), 0), CNT(re.escape(DOI_E), 1)
SL = CNT(BS + BS + u'/', 0)
NA = CNT(u'[^' + BS + u'x00-' + BS + u'x7f]', 1)
EARLY = CNT(u'content' + BS + BS + u'/early', 0)
P_1101, P_64898 = CNT(u'10' + BS + u'.1101', 0), CNT(u'10' + BS + u'.64898', 0)
N_NA, N_PDOI = CNT(u'"published":"NA"', 0), CNT(u'"published":"10\\.', 0)
N_LICND, N_CC = CNT(u'"license":"cc_by_nc_nd"', 0), CNT(u'CC-BY-NC-ND', 1)
N_EN, N_QUOT, N_BARE = CNT(u'–', 1), CNT(u'"[0-9]', 0), CNT(u'":' + BS + u'd', 0)
N_V2, N_V1 = CNT(u'"version":"2"', 0), CNT(u'"version":"1"', 0)
SENT7 = 7
assert (ROWS and len(ROWS), len(PUBS), len(set(x.split(u'/')[0] for x in PUBS))) == (30, 8, 6)
assert ENVD[u'count'] == 30 and ENVD[u'total'] == u'575' and ENVD[u'count_new_papers'] == u'397'
assert (N_PLAIN_P, N_PLAIN_J, N_ESC_J, N_ESC_P) == (41, 0, 1, 0)
assert (SL, NA, EARLY, P_1101, P_64898) == (303, 331, 30, 17, 13)
assert (N_NA, N_PDOI, N_LICND, N_CC, N_EN) == (22, 8, 11, 40, 45)
assert (N_QUOT, N_BARE, N_V2, N_V1) == (103, 1, 19, 6)
assert (RCOT(0), BYTES[0], FULL[0], RCOT(1), FULL[1], CHP) == (69657, 69665, 69661, 80699, 80861, 80626)
assert RCOT(1) - CHP == 73 and P_1101 + P_64898 == len(ROWS)
NEWP, TOT = int(ENVD[u'count_new_papers']), int(ENVD[u'total'])
D367, D178, D545 = NEWP - len(ROWS), TOT - NEWP, TOT - len(ROWS)
UESC = CNT(BS + BS + u'u', 0)
NROW = len(ROWS)
assert (D367, D178, D545, UESC) == (367, 178, 545, 6)
DKEYS = set(KS.split(u'／'))
assert set([u'367', u'178', u'545', u'73']) <= DKEYS, sorted(DKEYS)
assert (b46_enc, b46_dig) == (int(ST[u'enc']), int(ST[u'digest'])), (b46_enc, b46_dig)
assert (int(ST[u'uniq_cp']), int(ST[u'blocks'])) == (b46_uniq, b46_blocks)
assert float(ST[u'cpu']) == float(b46_cpu) and ST[u'dens'] == b46_raw and ST[u'ret'] == b46_ret
assert NUM(u'n_sent') == SENT7 and NUM(u'n_sent_hit') == 5 and NUM(u'n_sent_out') == 2


def fmt(n):
    return u'{:,}'.format(int(n)).replace(u',', u' ')


mm = re.search(u'第二代（B11–B45）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
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

S45 = loadstat(u'corpus/_f45stats.txt')
PAIRS = [
 (u'共 **45 条**（`babeltele/B01..B45`）', u'共 **%d 条**（`babeltele/B01..B46`）' % NENT),
 (u'**PASS**（45 条）', u'**PASS**（%d 条）' % NENT),
 (u'当前 **45 条语料／%s 条**推导全部通过（audit 自报“已机检的推导 %s 条”）' % (S45[u'proofs'], S45[u'proofs']),
  u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs)),
 (u'第二代（B11–B45）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B46）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'：%d 个 1–2 位结构计数（B03' % soft_all, u'：%d 个 1–2 位结构计数（B03' % soft_all),
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
    if l.startswith(u'| **合计（45 条）**'):
        R[i] = (u'| **合计（%d 条）** | **%s** | **%s**（摘要段合计 %s） | — | **%s** | — |'
                % (NENT, fmt(enc_all), ret_all.strip(u'*'), fmt(dig_all), fmt(uniq_all)))
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
    if u'B45 把同一根轴推到**同一个名字底下的三种对象**' in l and l.rstrip().endswith(u'锚点触到的窗口。'):
        R[i] = l.rstrip() + (u'B46 把轴从“同一份文件的几种到达路径”换到**描述与被描述者**（%d 锚 ⇎ %d 个不同串，'
                             u'目录侧 %d ⇎ 原文侧 %d）：连接键那个 DOI 在两份文件里没有一次按同一种拼法出现'
                             u'（目录里转义写法 %d 处 ⇎ 原文里真斜杠写法 %d 处，另外两个方向全为 0），'
                             u'“同一件事”只能由读者重建；封套三个自报数两两之差 %d／%d／%d 只有 %d 能在文件内核对，'
                             u'“%d”这个字段名下 %d 处占位串加 %d 处别的注册号恰等于记录数；'
                             u'许可码 %d ⇎ 许可散文 %d、粘连机构串 ⇎ 分号地址、十二人作者串在原文 0 处——两套词汇双向缺席。'
                             u'保留率 %s（字节口径 %s，两个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节）仍是对照条的必然读数。'
                             % (ANCH, UANCH, NUM(u'anchor_E'), NUM(u'anchor_P'), N_ESC_J, N_PLAIN_P,
                                D367, D178, D545, NROW,
                                30, N_NA, N_PDOI, N_LICND, N_CC, b46_ret, b46_raw,
                                fmt(sum(RCOT(i) for i in range(2))), fmt(sum(BYTES))))
        done.append(u'口径段')
        break
assert u'口径段' in done, u'口径段未命中'

GEN = (u'**B46 把对照轴换成描述与被描述者**：bioRxiv recent 接口的目录页 `api/bio_recent_2026w01.json`'
       u'（口径内 %s 字符／磁盘 %d 字节，整份只有一行 JSON）⇎ 其中一行所指那篇原文的抽取文本 '
       u'`prose/biorxiv_bacterial_organelles.txt`（口径内 %s 字符⇎抽取头自记 %d⇎全文件 %d，三个口径差 %d）。'
       u'锚位 %d 个（⟦E⟧ %d ⇎ ⟦P⟧ %d）／%d 个不同串, 判词 %d 行, DERIV %d 键, 0 键折 %d 个加法项'
       u'（目录侧缺席 %d 类 + 原文侧缺席 %d 类 + 等式与“恰好 N 处” %d 条; 这些项里 CNT 原语出现 %d 次）。'
       u'关键结论全部可机检: 连接键那个 DOI 在两份文件里没有一次同拼法——目录里转义写法 %d 处、原文里真斜杠写法 %d 处, '
       u'而两个交叉方向各 0 次; 目录还有第三种拼法, 其 jatsxml 把注册前缀整个丢掉(带前缀写法在该字段 %d 条里 0 命中), '
       u'原位换上送达日期。封套三个自报数两两之差 %d／%d／%d, 只有 count=%d 能在本文件内核对(它等于记录数), '
       u'后两个是“本文件之外还有多少”的断言, 原样留着并标明不能核对; 全目录只有 %d 处裸数字字段(正是 count)而 '
       u'“引号里以数字开头”%d 处——同一对象里整型与字符串并存。“published 里没有时间”: %d 处占位串加 %d 处期刊 DOI '
       u'恰等于记录数, 日期形式 0 处, 那 %d 个号段分属 %d 家注册机构而与本页两个前缀(%d＋%d＝%d)无一重合。'
       u'两套词汇双向缺席: 许可码 %d 行 ⇎ 许可散文 %d 处、粘连机构串 ⇎ 分号地址、十二人作者串 0、'
       u'摘要七句里五句逐字命中而两句不命中(heterologously produced ⇎ expressed、连字符两侧空格), '
       u'所以索引里的摘要是改写而不是引文。字符系统: 目录 %d 个斜杠全部写成转义形式而裸斜杠 0 处、非 ASCII 码点 0 个, '
       u'六个非 ASCII 字符以 \\u 转义存活 ⇎ 原文 %d 个码点直接写在地上——按字面比对时两种存活互相看不见。'
       u'哈希、字节数、全文件字符数与“%d 恰是 url 那一行的长度”都归工具侧: 前者写在 src 行, 后者因为 CNT 只数命中不量长度。')
for i, l in enumerate(R):
    if l.startswith(u'**B45 把对照轴换成同一个名字底下的三种对象**'):
        R[i] = l + u'\n\n' + GEN % (fmt(RCOT(0)), BYTES[0], fmt(RCOT(1)), CHP, FULL[1], RCOT(1) - CHP,
                                    ANCH, NUM(u'anchor_E'), NUM(u'anchor_P'), UANCH, GLOS, DERIV_KEYS,
                                    NTERMS0, APAP, AESC, NEQU, NTERM0, N_ESC_J, N_PLAIN_P, NROW,
                                    D367, D178, D545, NROW, N_BARE, N_QUOT,
                                    N_NA, N_PDOI, N_PDOI, len(set(x.split(u'/')[0] for x in PUBS)),
                                    P_1101, P_64898, P_1101 + P_64898, N_LICND, N_CC,
                                    SL, NA, RCOT(1) - CHP)
        done.append(u'B46 段')
        break
assert u'B46 段' in done, u'B45 段未命中'

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B45 | %s（新建' % fmt(b45_enc)):
        ins.append((i + 1, u'| B46 | %s（新建, 描述与被描述者 %d 锚／%d 个不同串: 目录页 ⟦E⟧ ⇎ 它其中一行所指的原文 ⟦P⟧; '
                           u'连接键 DOI 两侧拼法交叉 0 命中(转义 %d ⇎ 真斜杠 %d) ⇒ 联结要靠重建; '
                           u'一个零键折 %d 个加法项（目录侧缺席 %d 类 ⇎ 原文侧缺席 %d 类 ⇎ 等式与“恰好 N 处” %d 条, '
                           u'CNT 原语 %d 次）; 封套三自报数两两差 %d／%d／%d, 只有 %d 可文件内核对; '
                           u'“published”里 %d 处占位串＋%d 处期刊 DOI＝记录数, 日期 0 处; '
                           u'词汇与字符系统全部走 CNT: 许可码 %d⇎散文 %d、斜杠 %d 全转义、非 ASCII 0⇎%d） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为目录里的字段名与原文里的拉丁词形） | %s | %s |'
                           % (fmt(b46_enc), ANCH, UANCH, N_ESC_J, N_PLAIN_P, NTERMS0, APAP, AESC, NEQU, NTERM0,
                              D367, D178, D545, NROW, N_NA, N_PDOI,
                              N_LICND, N_CC, SL, NA,
                              ANCH, fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b46_ret, fmt(b46_dig))))
    elif l.startswith(u'| B45 | %s | %s' % (fmt(b45_enc), b45_ret)):
        ins.append((i + 1, u'| B46 | %s | %s | %s（字节口径; 两个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节——'
                           u'目录那一页把整篇原文的信息量压成一行而原文比目录长, 故保留率高于 100%% 属对照条的结构性读数, '
                           u'按“%d 键支撑 %d 行判词”来读） | %d | %s |'
                           % (fmt(b46_enc), b46_ret, b46_raw, fmt(sum(RCOT(i) for i in range(2))),
                              fmt(sum(BYTES)), DERIV_KEYS, GLOS, b46_uniq, b46_cpu)))
    elif l.startswith(u'| B45 | `raw/tz/zone1970.tab`'):
        ins.append((i + 1, u'| B46 | `raw/api/bio_recent_2026w01.json`（bioRxiv recent 接口目录页, 口径内 %s 字符／磁盘 %d 字节／'
                           u'全文件 %d 字符, 单行 JSON, 数据 %d 行, 封套 count %d⇎count_new_papers %s⇎total %s）⇎ '
                           u'`raw/prose/biorxiv_bacterial_organelles.txt`（该行所指原文的抽取文本, B16 同源, '
                           u'口径内 %s 字符⇎抽取头自记 %d⇎全文件 %d） | '
                           u'目录 ⇎ 被目录命名的原文: DOI 三种拼法交叉 0 命中(目录转义 %d／原文真斜杠 %d／两个交叉方向 0), '
                           u'第三种拼法在 jatsxml 里丢前缀(带前缀 0 命中); 窗口声明五天而三十行 date 全在同一天(端点后四天 0); '
                           u'published 两类值 %d＋%d＝%d 而日期形式 0(那 %d 个号段分属 %d 家机构, 与本页前缀 %d／%d 无一重合, '
                           u'其中 2 处晚于窗口); 摘要七句五中两句不中(produced⇎expressed、连字符空格); '
                           u'词汇双向缺席(许可码 %d⇎散文 %d、下划线⇎横杠、粘连机构串⇎分号地址、作者串 0); '
                           u'字符两种存活(斜杠 %d 全转义、非 ASCII 0⇎%d、\\u 转义 %d 个、CO2 3⇎CO₂ 5); '
                           u'版本词形碰撞(目录 version=2 共 %d 行 ⇎ 原文“v2”三处全是别人的软件); '
                           u'三个字符口径(自记 %d ⇎ 口径内 %d ⇎ 全文件 %d, 差 %d 为 url 行) ⇒ 目录与原文互不包含, 两份都存 |'
                           % (fmt(RCOT(0)), BYTES[0], FULL[0], len(ROWS), ENVD[u'count'],
                              ENVD[u'count_new_papers'], ENVD[u'total'],
                              fmt(RCOT(1)), CHP, FULL[1], N_ESC_J, N_PLAIN_P, N_NA, N_PDOI, len(ROWS),
                              N_PDOI, len(set(x.split(u'/')[0] for x in PUBS)), P_1101, P_64898,
                              N_LICND, N_CC, SL, NA, UESC,
                              N_V2, CHP, RCOT(1), FULL[1], RCOT(1) - CHP)))
    elif l.startswith(u'python -X utf8 corpus/_fill45.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_mkB46.py                # 建条目: 双色锚位(E=目录页／P=原文), '
                    u'连接键拼法交叉命中、封套自报数差值、逐句对齐与双向缺席全部由 raw 回算\n'
                    u'python -X utf8 corpus/_mkdigest3.py B46 <entry> E <api/bio_recent_2026w01.json> 120 160 '
                    u'P <prose/biorxiv_bacterial_organelles.txt> 120 160   # 两源分节摘要 union_hit %d/%d, 每源按命中锚各自分块\n'
                    u'python -X utf8 corpus/atomcheck.py B46 corpus/_atoms46.txt       # %d 个不同锚串逐字回源 ok=%d bad=0(条目内锚位 %d 个)\n'
                    u'python -X utf8 corpus/_fill46.py               # ⛓解读注: %d 个键逐个复算并与键名断言; 0 键 %d 个加法项(CNT 原语 %d 次); '
                    u'待核 0 项; sha256 归外部断言、字节数与全文件字符数与“%d 恰是 url 行长”归工具侧, 在注里明写不冒充机检'
                    % (ANCH, ANCH, UANCH, UANCH, ANCH, DERIV_KEYS, NTERMS0, NTERM0, RCOT(1) - CHP)))
assert len(ins) == 4, [x[1][:30] for x in ins]
for pos, txt in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt)
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if re.search(u'45 条|B01\\.\\.B45|%s|423 条|%s|%s|%%s' % (
            re.escape(fmt(int(S45[u'enc']))), re.escape(fmt(prev_in)), re.escape(fmt(prev_out))), l)]
print(u'README %d 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 编码 %s 摘要 %s 保留 %s 码点 %s 推导 %d 待核 %d｜第二代 %s／%s'
      % (NENT, u'/'.join(done), len(left), fmt(enc_all), fmt(dig_all), ret_all, fmt(uniq_all), proofs,
         soft_all, fmt(in_lat), fmt(out_lat)))
for l in left:
    print(u'  ' + l[:150])
print(u'B46: enc %s dig %s ret %s raw %s uniq %d blocks %d cpu %s｜锚 %d(E %d/P %d)/%d 串 判词 %d｜'
      u'DERIV %d 键, 0 键 %d 项(缺席 %d+%d, 等式 %d, CNT %d 次), 差值键 %d｜'
      u'DOI %d/%d/%d｜封套 %d/%s/%s 差 %d/%d/%d｜published %d+%d｜词汇 %d⇎%d｜字符 %d/%d/%d｜口径 %d/%d/%d/%d'
      % (fmt(b46_enc), fmt(b46_dig), b46_ret, b46_raw, b46_uniq, b46_blocks, b46_cpu,
         ANCH, NUM(u'anchor_E'), NUM(u'anchor_P'), UANCH, GLOS,
         DERIV_KEYS, NTERMS0, APAP, AESC, NEQU, NTERM0, NDIFF,
         N_ESC_J, N_PLAIN_P, P_1101 + P_64898,
         NROW, NEWP, TOT, D367, D178, D545,
         N_NA, N_PDOI, N_LICND, N_CC, SL, NA, UESC,
         CHP, RCOT(1), FULL[1], RCOT(0)))
