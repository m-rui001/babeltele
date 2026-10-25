# -*- coding: utf-8 -*-
"""README 记账: 44 条 → 45 条。合计数字全部由 audit 表、metrics 普查与 _f45stats 复算, 不手填。
顺带补上 B43 段里两个从未代入的 %s(取 _f43stats 的记账值)。"""
import io, re, sys, os, ast, subprocess

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


def cells(tag):
    return [x.strip() for x in row[tag].split(u'|')]


b45 = cells(u'B45')
b44 = cells(u'B44')
b45_enc, b45_dig, b45_ret, b45_raw, b45_uniq, b45_blocks, b45_cpu, b45_soft = (
    int(b45[1]), int(b45[0]), b45[2], b45[3], int(b45[4]), int(b45[5]), b45[6], int(b45[10]))
b44_enc, b44_dig, b44_ret = int(b44[1]), int(b44[0]), b44[2]
assert b45_soft == 0, b45
assert NENT == 45, NENT
assert int(b45[7]) == 0 and int(b45[8]) == 0 and int(b45[9]) == 0, b45

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


ST = loadstat(u'corpus/_f45stats.txt')
NUM = lambda k: ast.literal_eval(ST[k]) if ST[k].strip().startswith(u'[') else int(ST[k])
IN_LAT, OUT_LAT, TAG_LAT = int(ST[u'in_lat']), int(ST[u'out_lat']), int(ST[u'tag_lat'])
OUT_ALL = OUT_LAT + TAG_LAT
KS = u'／'.join(sorted([k for k in re.findall(r"^ {2}'([^']+)':",
        re.search(u" 'B45': \\{\n(.*?)\n \\},", io.open(u'corpus/audit.py', encoding='utf-8').read(),
                  re.S).group(1), re.M)], key=lambda x: float(x)))
DERIV_KEYS, NTERM0 = int(ST[u'deriv_keys']), int(ST[u'n_term0'])
NABS_T, NABS_H, NPAIRZ, NEQU = 11, 5, 4, 5
assert (DERIV_KEYS, NTERM0) == (25, 73), (DERIV_KEYS, NTERM0)
assert len(KS.split(u'／')) == DERIV_KEYS
S3 = loadstat(u'corpus/_f43stats.txt')

# —— 缺席/配对/口径的全部计数现算, 与 _mkB45 同一口径 ——
RA = u'corpus/raw/tz/zone1970.tab'
RF = u'corpus/raw/zone1970_latest.tab'
RN = u'corpus/raw/tz/zone.tab'
RH = u'corpus/raw/zone1970.tab'
RAWS = [RA, RF, RN, RH]
TXT = [io.open(x, encoding='utf-8', errors='replace').read() for x in RAWS]
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
SRC = [u'\n'.join(l for l in x.split(u'\n') if not HEADRX.match(l.strip())) for x in TXT]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
RCOT = lambda i: len(SRC[i].strip())
BYTES = [os.path.getsize(x) for x in RAWS]
ROWA, FOURA, MULTI = u'(?m)^[A-Z]{2}[,\t]', u'(?m)^[^\t\n]*\t[^\t\n]*\t[^\t\n]*\t', u'(?m)^[A-Z]{2},'
ROWS_A, ROWS_N = CNT(ROWA, 0), CNT(ROWA, 2)
FOUR_A = CNT(FOURA, 0)
MULTI_A = CNT(MULTI, 0)
FLAT_A = ROWS_A - MULTI_A
SUMW = sum(CNT(u'(?m)^(?:[A-Z]{2},){%d}[A-Z]{2}(?=,|\t)' % (j - 1), 0) for j in range(2, 25))
TABS = [CNT(u'\t', i) for i in range(4)]
LTS = [CNT(u'<', i) for i in range(4)]
assert (ROWS_A, ROWS_N, MULTI_A, FLAT_A, FOUR_A, SUMW) == (312, 418, 34, 278, 201, 111)
assert NUM(u'a_only') == SUMW and NUM(u'n_only') == 106 and NUM(u'merged_rows') == MULTI_A
assert (TABS[0], TABS[2], TABS[3]) == (825, 1038, 26) and LTS[0] == 0 and LTS[3] == 2087
assert RCOT(0) == RCOT(1) and BYTES[0] == BYTES[1]
assert (b45_enc, b45_dig) == (int(ST[u'enc']), int(ST[u'digest'])), (b45_enc, b45_dig)
assert (int(ST[u'uniq_cp']), int(ST[u'blocks'])) == (b45_uniq, b45_blocks)
assert float(ST[u'cpu']) == float(b45_cpu) and ST[u'dens'] == b45_raw and ST[u'ret'] == b45_ret


def fmt(n):
    return u'{:,}'.format(int(n)).replace(u',', u' ')


mm = re.search(u'第二代（B11–B44）锚内字母 \\*\\*([\\d ]+)\\*\\*、锚外 \\*\\*([\\d ]+)\\*\\*；'
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
 (u'共 **44 条**（`babeltele/B01..B44`）', u'共 **%d 条**（`babeltele/B01..B45`）' % NENT),
 (u'**PASS**（44 条）', u'**PASS**（%d 条）' % NENT),
 (u'当前 **44 条语料／404 条**推导全部通过（audit 自报“已机检的推导 404 条”）',
  u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs)),
 (u'第二代（B11–B44）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(prev_in), fmt(prev_out), fmt(prev_in + FIRST_IN), fmt(prev_out + FIRST_OUT)),
  u'第二代（B11–B45）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
  % (fmt(in_lat), fmt(out_lat), fmt(in_lat + FIRST_IN), fmt(out_lat + FIRST_OUT))),
 (u'：16 个 1–2 位结构计数（B03', u'：%d 个 1–2 位结构计数（B03' % soft_all),
 (u'（正文 %s 字符）⇎ [2026] EWCA Civ 1224 判决全文（%s 字符／810 行）',
  u'（正文 %s 字符）⇎ [2026] EWCA Civ 1224 判决全文（%s 字符／810 行）'
  % (fmt(int(S3[u'raw0_chars'])), fmt(int(S3[u'raw1_chars'])))),
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
    if l.startswith(u'| **合计（44 条）**'):
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
    if u'B44 又把轴转到**同一篇文章的两种序列化**' in l and l.rstrip().endswith(u'字符自然重于窗口。'):
        R[i] = l.rstrip() + (u'B45 把同一根轴推到**同一个名字底下的三种对象**（%d 锚 ⇎ %d 个不同串）：'
                             u'归档成员与单文件抓取的两份表在口径内长度/制表符/行数三项全等(%s／%s／%d)，'
                             u'但“同一份”这件事本身不在机检键里——它只能由外部摘要哈希断言，'
                             u'算法名与 %d 位十六进制写在 src 行；姊妹表的证据则是双侧差集 %d ⇎ %d，'
                             u'而全部分歧住在 %d 行合并行里、一行一码的 %d 行逐对一致。'
                             u'保留率 %s（字节口径 %s，四个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节）是对照条的必然读数：'
                             u'判词要在四个源之间来回数，而摘要段只索引锚点触到的窗口。'
                             % (int(ST[u'anchors']), int(ST[u'uniq_anchor']), fmt(RCOT(0)), fmt(TABS[0]), ROWS_A,
                                64, SUMW, NUM(u'n_only'), MULTI_A, FLAT_A, b45_ret, b45_raw,
                                fmt(sum(RCOT(i) for i in range(4))), fmt(sum(BYTES))))
        done.append(u'口径段')
        break
assert u'口径段' in done, u'口径段未命中'

GEN = (u'**B45 把对照轴换成同一个名字底下的三种对象**：tzdata 归档成员 `zone1970.tab`（口径内 %s 字符）⇎ '
       u'同一注册表的单文件抓取 `zone1970_latest.tab`（与前者逐字节相同）⇎ 姊妹表 `zone.tab`（口径内 %s 字符）⇎ '
       u'名叫 `zone1970.tab` 却根本不是表的索引网页（口径内 %s 字符）。锚位 %d 个（⟦A⟧ %d ⇎ ⟦F⟧ %d ⇎ ⟦N⟧ %d ⇎ ⟦H⟧ %d）／'
       u'%d 个不同串, 判词 %d 行, DERIV %d 键, 0 键里折 %d 个 CNT 项（表侧缺席 %d 类 + 网页侧缺席 %d 类 + '
       u'配对层面 %d 项 0 命中 + 等式差 %d 条）。关键结论全部可机检：姊妹表不是重排——双侧差集 %d ⇎ %d（两边都非空）, '
       u'而 %d 恰等于第一个字段逗号展开的额外码数（同因: 被并进来的属地码正是姊妹表另立自有名的那些对）; '
       u'最硬的一条是 %d ⇎ %d——分歧全部住在用逗号并码的 %d 行里, 一行一码的那 %d 行与姊妹表逐对一致'
       u'（“平铺行配差集对”的行式在表内 0 命中）。判格式先于读内容: 制表符 %d ⇎ %d ⇎ %d 与尖括号 0 ⇎ %d 定对象类型, '
       u'而名为 zone1970 的那份里“zone1970”0 次、“`.tab`”0 次。两处“同值不同因”的 0 也写进判词: '
       u'“1970”与“public domain”在表侧为 0 是因为它们住在被审计口径剔掉的注释行里——0 不等于没写。'
       u'逐字节相同则交给外部摘要哈希断言: 算法名与 %d 位十六进制写在 src 行而不是机检键, '
       u'因为工具会把哈希算法名里的数字当成需要在源里逐字命中的硬数字。')
for i, l in enumerate(R):
    if l.startswith(u'**B44 把对照轴换成同一篇文章的两种序列化**'):
        R[i] = l + u'\n\n' + GEN % (fmt(RCOT(0)), fmt(RCOT(2)), fmt(RCOT(3)),
                                    int(ST[u'anchors']), NUM(u'anchor_A'), NUM(u'anchor_F'),
                                    NUM(u'anchor_N'), NUM(u'anchor_H'), int(ST[u'uniq_anchor']),
                                    int(ST[u'gloss_lines']), DERIV_KEYS, NTERM0, NABS_T, NABS_H,
                                    NPAIRZ, NEQU, SUMW, NUM(u'n_only'), SUMW, MULTI_A, FLAT_A, MULTI_A, FLAT_A,
                                    TABS[0], TABS[2], TABS[3], LTS[3], 64)
        done.append(u'B45 段')
        break
assert u'B45 段' in done, u'B44 段未命中'

ins = []
for i, l in enumerate(R):
    if l.startswith(u'| B44 | %s（新建' % fmt(b44_enc)):
        ins.append((i + 1, u'| B45 | %s（新建, 同一个名字的三种对象 %d 锚／%d 个不同串: 归档成员 ⇎ 单文件抓取 ⟦A⟧⇎⟦F⟧ '
                           u'⇎ 姊妹表 ⟦N⟧ ⇎ 索引网页 ⟦H⟧; 双侧差集 %d⇎%d ⇒ 姊妹表不是重排; '
                           u'一个零键折 %d 个 CNT 项（表侧缺席 %d 类 ⇎ 网页侧缺席 %d 类 ⇎ 配对层面 %d 项 0 命中 ⇎ 等式差 %d 条）; '
                           u'分歧住在合并行: %d 行携带全部 %d 对差异, 平铺 %d 行逐对一致; '
                           u'对象类型全部走 CNT: 制表符 %d⇎%d⇎%d、尖括号 0⇎%d） | %d | %s | '
                           u'%s（其中 %d 为出处标签, 余 %s 为表里的 zone 名与网页里的 URL/标记拉丁名） | %s | %s |'
                           % (fmt(b45_enc), int(ST[u'anchors']), int(ST[u'uniq_anchor']),
                              SUMW, NUM(u'n_only'), NTERM0, NABS_T, NABS_H, NPAIRZ, NEQU,
                              MULTI_A, SUMW, FLAT_A, TABS[0], TABS[2], TABS[3], LTS[3],
                              int(ST[u'anchors']), fmt(IN_LAT), fmt(OUT_ALL), TAG_LAT, fmt(OUT_LAT),
                              b45_ret, fmt(b45_dig))))
    elif l.startswith(u'| B44 | %s | %s' % (fmt(b44_enc), b44_ret)):
        ins.append((i + 1, u'| B45 | %s | %s | %s（字节口径; 四个源口径内合计 %s 字符 ⇎ 磁盘 %s 字节——'
                           u'网页那一份比两份表都长却不是一行一事实, 故保留率高于 100%% 属对照条的结构性读数） | %d | %s |'
                           % (fmt(b45_enc), b45_ret, b45_raw, fmt(sum(RCOT(i) for i in range(4))),
                              fmt(sum(BYTES)), b45_uniq, b45_cpu)))
    elif l.startswith(u'| B44 | `raw/prose/pmc_ards.xml`'):
        ins.append((i + 1, u'| B45 | `raw/tz/zone1970.tab`（tzdata 归档成员, 口径内 %s 字符／全文件 %d 行, 数据 %d 行）⇎ '
                           u'`raw/zone1970_latest.tab`（同一注册表单文件抓取, 与前者逐字节相同: 哈希相同 ⇎ 磁盘 %d 字节）⇎ '
                           u'`raw/tz/zone.tab`（姊妹表, 一国一行, 数据 %d 行／口径内 %s 字符）⇎ '
                           u'`raw/zone1970.tab`（名叫 zone1970.tab 的索引网页, 全文件 %d 行／口径内 %s 字符） | '
                           u'三种对象对照: 数据行 %d ⇎ %d; (国家码, zone) 配对双侧差集 %d ⇎ %d(差 %d), '
                           u'两个方向各自编成分支正则均在对方 0 命中; 逗号合并行 %d 恰为携带差集对的行数, '
                           u'平铺行 %d 与姊妹表逐对一致; 四列行 %d ⇎ %d; 制表符 %d ⇎ %d ⇎ %d ⇎ 尖括号 0 ⇎ 0 ⇎ 0 ⇎ %d; '
                           u'“zone1970”“.tab”“tzdata”“1970”在表侧 0(后两者成因是注释行被口径剔掉), '
                           u'尖括号/href/mailto/@/.tar.gz/版本号写法这 11 类只在网页而三份表里 0——其中“zone1970”与“.tab”'
                           u'连那份冒充它们的网页里也 0; 两位码行式/坐标列/自身文件名/.tab/Etc/ 前缀这 5 类只在表里而网页里 0 '
                           u'⇒ 缺席双向, 三种对象互不包含, 三份都存 |'
                           % (fmt(RCOT(0)), NUM(u'full_lines')[0], ROWS_A, BYTES[0], ROWS_N, fmt(RCOT(2)),
                              NUM(u'full_lines')[3], fmt(RCOT(3)), ROWS_A, ROWS_N, SUMW, NUM(u'n_only'),
                              SUMW - NUM(u'n_only'), MULTI_A, FLAT_A, FOUR_A, CNT(FOURA, 2),
                              TABS[0], TABS[2], TABS[3], LTS[3])))
    elif l.startswith(u'python -X utf8 corpus/_fill44.py'):
        ins.append((i + 1,
                    u'python -X utf8 corpus/_mkB45.py                # 建条目: 四色锚位(A=归档成员／F=单文件抓取／N=姊妹表／H=网页), '
                    u'配对双侧差集、宽度分桶求和与双向缺席全部由 raw 回算\n'
                    u'python -X utf8 corpus/_mkdigest3.py B45 <entry> A <tz/zone1970.tab> 120 160 F <zone1970_latest.tab> 120 160 '
                    u'N <tz/zone.tab> 120 160 H <zone1970.tab> 120 160   # 四源分节摘要 union_hit %d/%d, 每源按命中锚各自分块\n'
                    u'python -X utf8 corpus/atomcheck.py B45 corpus/_atoms45.txt        # %d 个不同锚串逐字回源 ok=%d bad=0(条目内锚位 %d 个)\n'
                    u'python -X utf8 corpus/_fill45.py               # ⛓解读注: %d 个键逐个复算并与键名断言; 0 键 %d 项; '
                    u'待核 0 项; 逐字节相同归外部哈希、字节数归工具侧, 在注里明写不冒充机检'
                    % (int(ST[u'anchors']), int(ST[u'anchors']), int(ST[u'uniq_anchor']),
                       int(ST[u'uniq_anchor']), int(ST[u'anchors']), DERIV_KEYS, NTERM0)))
assert len(ins) == 4, [x[1][:30] for x in ins]
for pos, txt in sorted(ins, key=lambda x: -x[0]):
    R.insert(pos, txt)
t = u'\n'.join(R)
io.open(F, 'w', encoding='utf-8').write(t)

left = [l for l in t.split(u'\n')
        if re.search(u'44 条|B01\\.\\.B44|%s|280 691|404 条|%s|%s|%%s' % (
            re.escape(fmt(223712)), re.escape(fmt(prev_in)), re.escape(fmt(prev_out))), l)]
print(u'README %d 条完成; 已替换 %s; 残留旧计数行 %d｜audit: 编码 %s 摘要 %s 保留 %s 码点 %s 推导 %d 待核 %d｜第二代 %s／%s'
      % (NENT, u'/'.join(done), len(left), fmt(enc_all), fmt(dig_all), ret_all, fmt(uniq_all), proofs,
         soft_all, fmt(in_lat), fmt(out_lat)))
for l in left:
    print(u'  ' + l[:150])
print(u'B45: enc %s dig %s ret %s raw %s uniq %d blocks %d cpu %s｜缺席 %d+%d, 0命中 %d, 等式 %d｜'
      u'配对 %d/%d/%d/%d｜行 %d/%d 合并 %d 平铺 %d 四列 %d/%d｜制表符 %s 尖括号 %s'
      % (fmt(b45_enc), fmt(b45_dig), b45_ret, b45_raw, b45_uniq, b45_blocks, b45_cpu,
         NABS_T, NABS_H, NPAIRZ, NEQU, NUM(u'pairs_A'), NUM(u'pairs_N'), SUMW, NUM(u'n_only'),
         ROWS_A, ROWS_N, MULTI_A, FLAT_A, FOUR_A, CNT(FOURA, 2), TABS, LTS))
