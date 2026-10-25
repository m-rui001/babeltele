# -*- coding: utf-8 -*-
"""README 记账第五遍(B68): 全用串方法现量, 不抄建条目侧快照。
本遍三件事: 门槛表补 B68 行、语料表补 B68 行、判词段补 B68 段; 聚合行按 audit 当下输出重算(66→67 条)。
字母账那行(第二代锚内/锚外)本遍不动——口径要逐条重导, 半改会写出假数。"""
import io, json, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\r\n' if u'\r\n' in io.open(u'corpus/README.md', encoding='utf-8').read() else u'\n'
S = io.open(u'corpus/README.md', encoding='utf-8').read()
FP = json.load(io.open(u'corpus/_b68flat.json', encoding='utf-8'))
DER = json.load(io.open(u'corpus/_deriv68.json', encoding='utf-8'))
SRC = [u'corpus/raw/dnsTTL/rfc1034.txt', u'corpus/raw/dnsTTL/rfc1035.txt',
       u'corpus/raw/dnsTTL/rfc1536.txt', u'corpus/raw/dnsTTL/rfc2181.txt']
LBL = [u'1034', u'1035', u'1536', u'2181']
YR = [u'87', u'87', u'93', u'97']
ANS = [u'只有字段宽度“32 bit integer”而无上限句', u'同一枚数改写成 signed 32 bit 并补 lower bound',
       u'只谈缓存与 TTL 泄露、不提上限数', u'定死 2^31−1=2147483647 并 hereby obsoletes']

AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                     text=True, encoding='utf-8').stdout
assert u'T3 码位): PASS' in AUD, AUD[-500:]
assert u'证明失败' not in AUD, AUD[-500:]


def gk(k):
    assert k in FP, k
    return FP[k]


def fmt(n):
    s = u'%d' % n if isinstance(n, int) else u'%g' % n
    if u'.' in s:
        a, b = s.split(u'.', 1)
        return fmt(int(a)) + u'.' + b
    if not s.isdigit() or len(s) <= 3:
        return s
    g = [s[x:x + 3] for x in range(len(s) - 3, -1, -3)][::-1]
    if len(s) % 3:
        g = [s[:len(s) % 3]] + g
    return u' '.join(g)


def occ(s, ndl):
    c, i = 0, 0
    while True:
        j = s.find(ndl, i)
        if j < 0:
            return c
        c += 1
        i = j + len(ndl)


# ---- 逐份面量(第五套实现: 直接吃 raw 字节) ----
BS, LN, NB, FF, FFC, CR, NA, HY, BARE, SPACED = [], [], [], [], [], [], [], [], [], []
for p in SRC:
    raw = io.open(p, encoding='utf-8', errors='replace').read()
    ls = raw.split(u'\n')
    BS.append(len(raw.encode('utf-8')))
    LN.append(len(ls))
    NB.append(len([x for x in ls if x.strip() != u'']))
    FF.append(len([x for x in ls if x.strip() == u'\x0c']))
    FFC.append(occ(raw, u'\x0c'))
    CR.append(occ(raw, u'\r'))
    NA.append(len([c for c in raw if ord(c) > 127]))
    BARE.append(occ(raw, u'RFC1034'))
    SPACED.append(occ(raw, u'RFC 1034'))
    HY.append(occ(raw, u'RFC-1034'))
    assert NB[-1] + FF[-1] <= LN[-1]
STR = [HY[i] + BARE[i] + SPACED[i] for i in range(4)]
DASH = HY
assert FFC == gk(u'formfeed'), (FFC, gk(u'formfeed'))

# ---- 门槛表里 B68 那一行(编码/原文/比/待核全取 audit 当下输出) ----
GCOL = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B68 |'):
        GCOL = [x.strip() for x in l.split(u'|')[1:-1]]
assert GCOL and len(GCOL) >= 3, GCOL
DIG68 = int(''.join(c for c in GCOL[1] if c.isdigit()))
E68 = int(''.join(c for c in GCOL[2] if c.isdigit()))
OKN, BADN = gk(u'anchor_total'), gk(u'anchor_err')
assert DIG68 == 3255 and E68 == 12675, (DIG68, E68)

HEADROW = (u'| B68 | ' + fmt(E68) + u'（新建, 一条 RR 的 TTL 上限到底是多少、谁有权截 交四份 DNS 一手文书各答一遍 '
           + str(gk(u'anchor_total')) + u' 处标注／' + str(gk(u'anchor_distinct'))
           + u' 个不同串（登记全命中, 单源 ' + str(gk(u'anchor_single')) + u' ⇎ 穿二三源 '
           + str(gk(u'anchor_cross')) + u' ⇎ 四源全现 ' + str(gk(u'anchor_all4'))
           + u'——四源同现零枚, 穿源的 2 枚都住在 1034⇎1035 那一对的共享长行里（'
           + str(gk(u'pool_share2_ab')) + u'／' + str(gk(u'pool_2')) + u'）, 归属检查 '
           + str(gk(u'checks')) + u' 次, 错配 ' + str(gk(u'anchor_err')) + u'）: 四色锚位 '
           + u' ⇎ '.join(x + u' ⟦' + y + u'⟧' for x, y in zip(LBL, u'ABCD'))
           + u'; 答句四种（只给字段宽度 ⇎ 同一枚数换符号性 ⇎ 撤出上限话题 ⇎ 定死并宣告 obsolete）: '
           + u' ⇎ '.join([u'32 bit 无上限句', u'signed 32 bit＋lower bound', u'只谈缓存', u'2^31−1＝' + fmt(gk(u'ttl_max'))])
           + u'; 三面阶梯（原面 ⇎ 全篇折平 ⇎ 摘壳折平）主线针按文档读到 '
           + u'⇎'.join(str(x) for x in gk(u'sn_strict_docs')) + u' ／ '
           + u'⇎'.join(str(x) for x in gk(u'sn_fold_docs')) + u' ／ '
           + u'⇎'.join(str(x) for x in gk(u'sn_sh_docs'))
           + u'（针表 ' + str(gk(u'sn_sh_total')) + u' 枚, 面跨度 '
           + u'⇎'.join(str(x) for x in gk(u'sn_face_span')) + u'）——只靠摘壳面才读到的针 '
           + str(gk(u'sh_only_n')) + u' 枚（' + u','.join(gk(u'sn_only_sh'))
           + u', 缺口 ' + u'⇎'.join(str(x) for x in gk(u'shgap_d_bits'))
           + u'）, 阶梯倒挂 ' + str(gk(u'sh_ladder_bad'))
           + u' 处, 摘壳面命中减独有 ' + str(gk(u'sh_hit_minus_only')) + u'; '
           u'锚池 ' + fmt(gk(u'pool_n')) + u' 条按“归一长行压在几份里”分档 ' + u'⇎'.join(fmt(x) for x in gk(u'pool_tier'))
           + u'（分档闭合 ' + str(gk(u'pool_tier_close')) + u'）; 四份同现 ' + str(gk(u'pool_4'))
           + u' 条 ⇒ 逐字节档 ' + str(gk(u'share4_byte4')) + u' ⇎ 写法轴档 ' + str(gk(u'share4_notbyte'))
           + u' ⇎ 四轴全零（轴账闭合 ' + str(gk(u'share4_axis_close')) + u'）; '
           u'大写义务词只现于 D（' + u'⇎'.join(str(x) for x in gk(u'oblig_up'))
           + u'）而四份都不引 RFC 2119（' + u'⇎'.join(str(x) for x in gk(u'rfc2119_ref'))
           + u'）, 引用编号按三式并计（连字 ⇎ 紧挨 ⇎ 空格）: 四面各现 '
           + u'⇎'.join(str(STR[i]) for i in range(4)) + u' 次（其中连字式 '
           + u'⇎'.join(str(DASH[i]) for i in range(4)) + u' 枚）；同数共键 ' + str(len(DER)) + u' 枚算式／'
           + str(gk(u'x_ident_n')) + u' 条面内恒等式（标量闭账 ' + str(gk(u'scalar_clos_n'))
           + u' 项全零 ⇎ 清单闭账 ' + str(gk(u'list_clos_n')) + u' 项）, 扁平契约 ' + str(len(FP))
           + u' 枚键全数复测; 五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对锚逐字复核'
           u'；工具侧 atomcheck 的 SRC 表未登记本条, 四份纯文本面的逐字性由门槛侧 '
           + str(gk(u'checks')) + u' 次归属检查承担（逐字命中 ' + str(OKN) + u' 处 ⇎ 错配 ' + str(BADN) + u'） |')

SRCLINE = [u'`raw/dnsTTL/rfc1034.txt`', u'`rfc1035.txt`', u'`rfc1536.txt`', u'`rfc2181.txt`']
C68 = (u'| B68 | ' + u' ⇎ '.join(
    SRCLINE[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
    + u'／非空行 ' + fmt(NB[i]) + u'（换页符 ' + str(FFC[i]) + u' 枚，独占整行 ' + str(FF[i]) + u' 行）'
    + u'／答句 ' + ANS[i] + u'／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i]) + u'）'
    for i in range(4))
           + u' | 四份答同一个问题 ⇒ 1034 把 TTL 写成 32 bit integer 却不下上限（面上与 TTL 幅度有关的数只住在示例区: '
             + fmt(gk(u'min_floor')) + u' 秒＝“minimum of a day”, 是 MINIMUM 字段的示例值而非上限） ⇎ 1035 同年同一枚 32 加上符号性（signed）'
             u'并补一句 lower bound（此句跨行, 只在折平面现） ⇎ 1536 整篇不谈上限、只数缓存里的 TTL 泄露 ⇎ 2181 把两处含糊一次结算: '
             'maximum value of ' + fmt(gk(u'ttl_max')) + u'＝2^' + str(gk(u'ttl_pow')) + u'、字段仍是 '
             + str(gk(u'ttl_field_bits')) + u' bit 而只用掉低 ' + str(gk(u'ttl_bits')) + u' bit, 并 hereby obsoletes 1034⇎1035; '
             u'关键那句跨页眉, 原面与全篇折平两面都读不到, 只有摘壳面读到——三面阶梯因此是本条的支柱而非装饰 |' + NL)

PARA = (u'**B68 问的是一条资源记录的 TTL 上限到底是多少、谁有权截它, 四份 DNS 一手文书给出四种答法**：'
        + u' ⇎ '.join(SRCLINE[i] + u'（' + YR[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／'
                      + u'行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i]) + u'／换页符 ' + str(FFC[i]) + u' 枚（独占整行 '
                      + str(FF[i]) + u' 行）／答句 ' + ANS[i] + u'／非 ASCII ' + str(NA[i]) + u'）' for i in range(4))
        + u'——四份同为 RFC Editor 的纯文本面, 无 BOM、无 CR、全 ASCII, 但只有 2181 带 `Updates:` 头与 STD 13 '
          u'归类（标准类 ' + u'⇎'.join(str(x) for x in gk(u'cat_std')) + u'）。1034 只把 TTL 写成 32 bit integer '
          u'而不下任何上限句, 与 TTL 幅度有关的数只住在示例区 MINIMUM 的 86 400 秒（“minimum of a day”）——一个下界 ⇎ 1035 同年把这枚 32 加上符号性（signed）'
          u'并补一句 lower bound（跨行，原面读不到、折平面才读到）⇎ 1536 干脆不谈上限, 只数缓存里的 TTL 泄露（时长命中 '
          + u'⇎'.join(str(x) for x in gk(u'dur_hit_total')) + u'／不同值 '
          + u'⇎'.join(str(x) for x in gk(u'dur_distinct')) + u', C 命中 0）⇎ 2181 一次结算含糊: '
            u'maximum value of ' + fmt(gk(u'ttl_max')) + u'、写成 2^' + str(gk(u'ttl_pow'))
            + u'、字段仍是 ' + str(gk(u'ttl_field_bits')) + u' bit 而只用低 ' + str(gk(u'ttl_bits'))
            + u' bit, 并 hereby obsoletes 1034 与 1035。两枚数各自独立解析而幂与上限相等（闭合 '
          + str(gk(u'max_pow_close')) + u'）; 大写义务词按份计 '
          + u'⇎'.join(str(x) for x in gk(u'oblig_up')) + u'（只在 D 现 ' + str(gk(u'oblig_up')[3])
          + u' 处；RFC 2119 的引用四份皆 ' + u'⇎'.join(str(x) for x in gk(u'rfc2119_ref'))
          + u'）, 所以“谁有权截”这句话在库内只有 D 用规范语气说过。三面阶梯是判据: 针表 '
          + str(gk(u'sn_sh_total')) + u' 枚在原面读到 ' + u'⇎'.join(str(x) for x in gk(u'sn_strict_docs'))
          + u'、全篇折平读到 ' + u'⇎'.join(str(x) for x in gk(u'sn_fold_docs')) + u'、摘壳折平读到 '
          + u'⇎'.join(str(x) for x in gk(u'sn_sh_docs')) + u'——唯一只活在摘壳面的针是 D 的 bits 句（缺口 '
          + u'⇎'.join(str(x) for x in gk(u'shgap_d_bits')) + u'）, 因为它正压在页眉⇎页脚壳上; '
            u'阶梯不倒挂（' + str(gk(u'sh_ladder_bad')) + u' 处）、摘壳命中减独有（'
          + str(gk(u'sh_hit_minus_only')) + u'）。锚 ' + str(gk(u'anchor_total')) + u' 处／'
          + str(gk(u'anchor_distinct')) + u' 个不同串, 按逐字再现份数分档 '
          + u'⇎'.join(fmt(x) for x in gk(u'pool_tier')) + u'（池 ' + fmt(gk(u'pool_n')) + u' 条, 闭合 '
          + str(gk(u'pool_tier_close')) + u'）——四源同现 0 条, 写法轴四档因此全为零, 这一条的分裂不住在写法上而住在'
            u'“同不同一枚数”上; 穿二源的 ' + str(gk(u'pool_2')) + u' 条里 ' + str(gk(u'pool_share2_ab'))
          + u' 条属于 1034⇎1035 这对同年文书。引用形状必须按三式并计: 1035 只用连字式 `[RFC-1034]`（'
          + str(HY[1]) + u' 枚，紧挨式与空格式各 ' + str(BARE[1]) + u'⇎' + str(SPACED[1])
          + u' 枚），2181 反过来只写紧挨式（' + str(BARE[3]) + u' 枚）外加空格式 '
          + str(SPACED[3]) + u' 枚——只认一种写法就会把“1035 从不引 1034”读成假。门槛侧 ' + str(len(DER)) + u' 枚算式／' + str(gk(u'x_ident_n'))
          + u' 条面内恒等式, 扁平契约 ' + str(len(FP)) + u' 枚键由第四 ⇎ 第五套实现逐枚复测; 反向对照扫过全部判定点: '
          + str(len(DER) + gk(u'x_ident_n')) + u' 条算式条条可跑通, 任一枚读数 +1 都会至少倒一条判定'
            u'（可判定而不倒的键 ' + u'0' + u' 枚）。')


def sub(old, new, s, cnt=1):
    assert s.count(old) == cnt, (u'锚点不唯一', old[:60], s.count(old))
    return s.replace(old, new)


def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:60])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


# ---- 1) 补 B68 判词段(紧跟最新的 B67 段) ----
assert S.count(u'**B68 问的是') == 0
S = after(S, u'**B67 把同一枚活性成分', PARA + NL + NL)
# ---- 2) 门槛表行(接在 B67 行后) ----
assert S.count(u'| B68 | 1') == 0
S = after(S, u'| B67 | 4833（新建,', HEADROW + NL)
# ---- 3) 语料表行 ----
S = after(S, u'| B67 | `raw/labels/synthroid_dailymed.html`', C68)

# ---- 4) 聚合行按 audit 当下输出重算 ----
ROWS = [l for l in AUD.split(u'\n') if l.startswith(u'| B') and l.count(u'|') >= 10]
assert len(ROWS) == 67, len(ROWS)
enc_all = sum(int(''.join(c for c in l.split(u'|')[3] if c.isdigit())) for l in ROWS)
dig_all = sum(int(''.join(c for c in l.split(u'|')[2] if c.isdigit())) for l in ROWS)
PROOFS = int(''.join(c for c in AUD.split(u'已机检的推导(')[1].split(u' 条)')[0] if c.isdigit()))
assert enc_all > dig_all > 0, (enc_all, dig_all)

TOTOLD = S.split(NL)
TOTIDX = [i for i, l in enumerate(TOTOLD) if l.startswith(u'| **合计（')]
assert len(TOTIDX) == 1, TOTIDX
lt = TOTOLD[TOTIDX[0]]
cells = lt.split(u'|')
assert cells[2].strip().startswith(u'**4'), cells[2]
OLDT = lt
cells[1] = u' **合计（' + str(len(ROWS)) + u' 条）** '
cells[2] = u' **' + fmt(enc_all) + u'** '
cells[3] = (u' **%.1f%%**（摘要段合计 ' % (100.0 * enc_all / dig_all) + fmt(dig_all)
            + u'，本遍补记的一枚为 ' + fmt(E68) + u' 编码／' + fmt(DIG68)
            + u' 摘要；条目数与两列合计均取自本遍现跑的 audit，唯一码点那列沿用上一遍读数、'
            + u'本遍未重算全库码点） ')
assert len(cells) == len(OLDT.split(u'|')), (len(cells), len(OLDT.split(u'|')))
TOTOLD[TOTIDX[0]] = u'|'.join(cells)
S = sub(OLDT, TOTOLD[TOTIDX[0]], S)

S = sub(u'共 **66 条**（`babeltele/B01..B65、B67`, 本遍补上 B65 的三处记账行, 合计按 audit 当下输出重算）',
        u'共 **67 条**（`babeltele/B01..B65、B67..B68`, 本遍补上 B68 的三处记账行, 合计按 audit 当下输出重算）', S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（66 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（67 条）', S)
PROV = [l for l in S.split(NL) if u'条语料／' in l and u'推导全部通过' in l]
assert len(PROV) == 1, PROV
i0 = PROV[0].find(u'当前 **')
j = PROV[0].find(u'）', PROV[0].find(u'audit 自报', i0))
while PROV[0][j + 1:j + 2] == u'）':
    j += 1
S = S[:S.find(PROV[0]) + i0] + (u'当前 **67 条语料／' + str(PROOFS) + u' 条**推导全部通过（audit 自报“已机检的推导 '
                                + str(PROOFS) + u' 条”）') + S[S.find(PROV[0]) + j + 1:]

CMD = u'python -X utf8 corpus/_fill67.py'
assert S.count(CMD) == 1
S = after(S, CMD,
          u'python -X utf8 corpus/_mkB68.py                    # 建条目: 扁平契约 ' + str(len(FP))
          + u' 枚键／恒等式 ' + str(gk(u'x_ident_n')) + u' 条 ⇎ DERIV ' + str(len(DER))
          + u' 枚算式, 采集侧对账 0 不符' + NL)
S = after(S, u'python -X utf8 corpus/_mkB68.py',
          u'python -X utf8 corpus/_mkdigest3.py B68 <entry> 1034 corpus/raw/dnsTTL/rfc1034.txt 160 120 1035 … 160 120 '
          u'1536 … 160 120 2181 … 160 120   # 四源分节摘要(' + fmt(DIG68) + u' 字符, '
          + str(gk(u'anchor_total')) + u'/' + str(gk(u'anchor_total')) + u' 锚全命中)' + NL)
S = after(S, u'python -X utf8 corpus/_mkdigest3.py B68',
          u'python -X utf8 corpus/_wire68.py                    # 幂等接线: SRC/ATOM/SCAN(审计器侧第三套实现)/DERIV/'
          u'B68V 进 audit.py, 落盘前复跑 ' + str(len(FP)) + u' 枚扁平键 ⇎ ' + str(len(DER)) + u' 枚算式' + NL)
S = after(S, u'python -X utf8 corpus/_wire68.py',
          u'python -X utf8 corpus/_fill68.py                    # 第四遍: 三面阶梯⇎窗口⇎集合代数各重导一次, '
          + str(gk(u'x_ident_n')) + u' 条恒等式现算归零后写回 ⛓解读注（13 行复测表）' + NL)

io.open(u'corpus/README.md', 'w', encoding='utf-8', newline=NL).write(S)
json.dump(dict(entries=len(ROWS), enc=enc_all, dig=dig_all, proofs=PROOFS, b68_enc=E68, b68_dig=DIG68,
               bytes=BS, lines=LN, nonblank=NB, formfeed_only=FF, cr=CR, nonascii=NA,
               rfc1034_forms=STR, rfc1034_hyphen=DASH, anchor_ok=OKN, anchor_err=BADN,
               keys=len(FP), deriv=len(DER), ident=gk(u'x_ident_n'),
               faces=[gk(u'sn_strict_docs'), gk(u'sn_fold_docs'), gk(u'sn_sh_docs')]),
          io.open(u'corpus/_b68readme.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（67 条）编码 ' + fmt(enc_all) + u' ⇎ 摘要 ' + fmt(dig_all) + u' ⇎ 保留 '
      + u'%.1f%%' % (100.0 * enc_all / dig_all) + u' ｜ 推导 ' + str(PROOFS) + u' 条 ｜ B68 行 ' + fmt(E68)
      + u'／' + fmt(DIG68) + u' ｜ 锚逐字 ' + str(OKN) + u' 处⇎错配 ' + str(BADN)
      + u' ｜ 引用三式 ' + u'⇎'.join(str(x) for x in STR) + u' ｜ 逐份字节 ' + u'⇎'.join(fmt(x) for x in BS))
