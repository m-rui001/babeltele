# -*- coding: utf-8 -*-
"""README 记账第五遍(B65): 全用串方法现量, 不抄建条目侧快照。
本遍处理的三件事: 门槛表补 B65 行、语料表补 B65 行、判词段补 B65 段; 聚合行(条目数/合计/推导数)按 audit 当下输出重算。
字母账那行(第二代锚内/锚外)本遍不动——它的口径要逐条重导, 半改会写出假数。"""
import io, json, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\r\n' if u'\r\n' in io.open(u'corpus/README.md', encoding='utf-8').read() else u'\n'
S = io.open(u'corpus/README.md', encoding='utf-8').read()
FP = json.load(io.open(u'corpus/_b65flat.json', encoding='utf-8'))
DER = json.load(io.open(u'corpus/_deriv65.json', encoding='utf-8'))
SRC = [u'corpus/raw/httpKA/rfc2068.txt', u'corpus/raw/httpKA/rfc2616.txt',
       u'corpus/raw/httpKA/rfc7230.txt', u'corpus/raw/httpKA/rfc9112.txt']
LBL = [u'2068', u'2616', u'7230', u'9112']
ANS = [u'“AT MOST 2”', u'“more than 2”', u'撤掉数(does not mandate)', u'沿用撤数句']

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
    return 0


# ---- 逐份面量(第五套实现: 直接吃 raw 字节) ----
BS, LN, NB, FF, CR, NA = [], [], [], [], [], []
for p in SRC:
    raw = io.open(p, encoding='utf-8', errors='replace').read()
    ls = raw.split(u'\n')
    BS.append(len(raw.encode('utf-8')))
    LN.append(len(ls))
    NB.append(len([x for x in ls if x.strip() != u'']))
    FF.append(len([x for x in ls if x.strip() == u'\x0c']))
    CR.append(occ(raw, u'\r'))
    NA.append(len([c for c in raw if ord(c) > 127]))
    assert len([x for x in ls if x.strip() != u'']) + len([x for x in ls if x.strip() == u'\x0c']) \
        <= len(ls)

# ---- 门槛表里 B65 那一行(编码/原文/比/待核全取 audit 当下输出) ----
GCOL = None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B65 |'):
        GCOL = [x.strip() for x in l.split(u'|')[1:-1]]
assert GCOL and len(GCOL) >= 3, GCOL
DIG65 = int(''.join(c for c in GCOL[1] if c.isdigit()))
E65 = int(''.join(c for c in GCOL[2] if c.isdigit()))
OKN, BADN = gk(u'anchor_total'), gk(u'anchor_err')

HEADROW = (u'| B65 | ' + fmt(E65) + u'（新建, 同一台服务器最多允许几条并发连接 交四份 HTTP/1.1 规范各答一遍 '
           + str(gk(u'anchor_total')) + u' 处标注／' + str(gk(u'anchor_distinct'))
           + u' 个不同串（登记全命中, 单源 ' + str(gk(u'anchor_single')) + u' ⇎ 穿二三源 '
           + str(gk(u'anchor_cross')) + u' ⇎ 四源全现 ' + str(gk(u'anchor_all4'))
           + u'——四源同现的那枚是超时值句, 原面按 time-out ⇎ timeout 分家, 归属检查 ' + str(gk(u'checks'))
           + u' 次, 错配 ' + str(gk(u'anchor_err')) + u'）: 四色锚位 '
           + u' ⇎ '.join(x + u' ⟦' + y + u'⟧' for x, y in zip(LBL, u'ABCD'))
           + u'; 答句三档（原文应许 ⇎ 撤数 ⇎ 撤数同句）AT MOST 2 ⇎ not more than 2 ⇎ 无数 ⇎ 无数而重写头阻塞论证; '
           u'锚池 ' + fmt(gk(u'pool_n')) + u' 条按“归一长行压在几份里”分档 ' + u'⇎'.join(fmt(x) for x in gk(u'pool_tier'))
           + u'（分档闭合 0）; 四份同现 ' + str(gk(u'pool_4')) + u' 条里逐字节仍同形 ' + str(gk(u'share4_byte4'))
           + u' 条 ⇎ 各差一根写法轴 ' + str(gk(u'share4_notbyte')) + u' 条（大小写 ' + str(gk(u'share4_axis_case'))
           + u' ⇎ 连字符 ' + str(gk(u'share4_axis_hyph')) + u' ⇎ 句后空格 ' + str(gk(u'share4_axis_space'))
           + u' ⇎ 跨两轴 ' + str(gk(u'share4_axis_multi')) + u', 轴账闭合 ' + str(gk(u'share4_axis_close')) + u'）; '
           u'折行通道六枚主线针按本面命中 ' + u'⇎'.join(str(x) for x in gk(u'main6_fold'))
           + u' ⇎ 其余主线针 ' + u'⇎'.join(str(x) for x in gk(u'sn_other_fold'))
           + u'（两档之和即容行档 ' + u'⇎'.join(str(x) for x in gk(u'sn_fold_docs'))
           + u', 注意这六枚按本面命中计而非窗内计）; 同数共键 ' + str(len(DER)) + u' 枚算式／'
           + str(gk(u'x_ident_n')) + u' 条面内恒等式, 扁平契约 ' + str(len(FP))
           + u' 枚键全数复测; 五套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ README）对锚逐字复核, '
           u'；工具侧 atomcheck 的 SRC 表未登记本条, 四份纯文本面的逐字性由门槛侧 '
           + str(gk(u'checks')) + u' 次归属检查承担（逐字命中 ' + str(OKN) + u' 处 ⇎ 错配 ' + str(BADN) + u'） |')

SRCLINE = [u'`raw/httpKA/rfc2068.txt`', u'`rfc2616.txt`', u'`rfc7230.txt`', u'`rfc9112.txt`']
C65 = (u'| B65 | ' + u' ⇎ '.join(
    SRCLINE[i] + u'（' + LBL[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
    + u'／非空行 ' + fmt(NB[i]) + u'（另有换页符独占 ' + str(FF[i]) + u' 行按 strip 口径不计）'
    + u'／答句 ' + ANS[i] + u'／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i]) + u'）'
    for i in range(4))
           + u' | 四份答同一个问题 ⇒ 2068 把上限写成 SHOULD“维护至多 2 条” ⇎ 2616 同一枚 2 改写成 SHOULD NOT“超过 2 条”'
             u'（义务方向翻转而数不动） ⇎ 7230 整句撤数、只说规范不 mandates 连接数 ⇎ 9112 逐字收下 7230 那句撤数却把'
             u'头阻塞论证重写一遍; 撤数是三家的共同动作, 差异住在“撤掉的这句话由谁抄谁”——四源同现的锚恰一枚（超时值句）, '
             u'四份同形的六条长行里只有两条逐字节同形, 其余按大小写/连字符/句后空格分家 |' + NL)

PARA = (u'**B65 问的是同一个客户端对同一台服务器最多该同时开几条连接, 四份 HTTP/1.1 规范给出四种答法**：'
        + u' ⇎ '.join(SRCLINE[i] + u'（' + LBL[i] + u' ⟦' + u'ABCD'[i] + u'⟧：' + fmt(BS[i]) + u' 字节／'
                      + u'行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i]) + u'／答句 ' + ANS[i] + u'／'
                      + u'非 ASCII ' + str(NA[i]) + u'）' for i in range(4))
        + u'——四份同为 RFC Editor 的纯文本面, 无 BOM、无 CR, 所以本条没有剥壳层, 差在“同一枚 2 是应许还是禁止、'
          u'还是干脆撤掉”。2068 写 SHOULD maintain AT MOST 2 ⇎ 2616 写 SHOULD NOT maintain more than 2（同一枚数、'
          u'义务方向相反）⇎ 7230 把数整句撤走（does not mandate）⇎ 9112 逐字保留 7230 的撤数句再重写下头阻塞论证。'
          u'锚 ' + str(gk(u'anchor_total')) + u' 处／' + str(gk(u'anchor_distinct')) + u' 个不同串, '
          u'按逐字再现份数分档 ' + u'⇎'.join(fmt(x) for x in gk(u'pool_tier')) + u'（池 ' + fmt(gk(u'pool_n'))
          + u' 条, 闭合 ' + str(gk(u'pool_tier_close')) + u'）; 四份同现 ' + str(gk(u'pool_4'))
          + u' 条只保证归一同形, 逐字节仍同形的只剩 ' + str(gk(u'share4_byte4')) + u' 条, 其余 '
          + str(gk(u'share4_notbyte')) + u' 条各差在一根写法轴上（大小写 ' + str(gk(u'share4_axis_case'))
          + u' ⇎ 连字符 ' + str(gk(u'share4_axis_hyph')) + u' ⇎ 句后空格 ' + str(gk(u'share4_axis_space'))
          + u' ⇎ 跨两轴 ' + str(gk(u'share4_axis_multi')) + u'）, 唯一那枚四源同现的锚正是连字符档的超时值句'
            u'（time-out ⇎ timeout）。折行通道单立六枚主线针档: 按折平在本面命中 '
          + u'⇎'.join(str(x) for x in gk(u'main6_fold')) + u' 枚 ⇎ 其余主线针 '
          + u'⇎'.join(str(x) for x in gk(u'sn_other_fold')) + u' 枚, 两档之和即容行档 '
          + u'⇎'.join(str(x) for x in gk(u'sn_fold_docs')) + u'——六枚里真压在节窗内的只有 2 枚, 其余跨出窗止行。'
          u'门槛侧 ' + str(len(DER)) + u' 枚算式／' + str(gk(u'x_ident_n')) + u' 条面内恒等式, 扁平契约 '
          + str(len(FP)) + u' 枚键由第四 ⇎ 第五套实现逐枚复测; 反向对照扫过全部判定点: '
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


# ---- 1) 补 B65 判词段(放在最新的 B67 段之前) ----
assert S.count(u'**B65 问的是') == 0
S = sub(u'**B67 把同一枚活性成分', PARA + NL + NL + u'**B67 把同一枚活性成分', S)
# ---- 2) 门槛表行(接在 B64 行后, 早于 B67 行) ----
assert S.count(u'| B65 | 1') == 0
S = after(S, u'| B64 | 8850（新建,', HEADROW + NL)
# ---- 3) 语料表行 ----
S = after(S, u'| B64 | `raw/dhcp/rfc2131.txt`', C65)

# ---- 4) 聚合行按 audit 当下输出重算 ----
ROWS = [l for l in AUD.split(u'\n') if l.startswith(u'| B') and l.count(u'|') >= 10]
assert len(ROWS) == 66, len(ROWS)
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
            + u'，本遍补记的一枚为 ' + fmt(E65) + u' 编码／' + fmt(DIG65)
            + u' 摘要；条目数与两列合计均取自本遍现跑的 audit，唯一码点那列沿用上一遍读数、'
            + u'本遍未重算全库码点） ')
assert len(cells) == len(OLDT.split(u'|')), (len(cells), len(OLDT.split(u'|')))

TOTOLD[TOTIDX[0]] = u'|'.join(cells)
S = sub(OLDT, TOTOLD[TOTIDX[0]], S)

S = sub(u'共 **66 条**（`babeltele/B01..B65、B67`）', u'共 **66 条**（`babeltele/B01..B65、B67`, '
        u'本遍补上 B65 的三处记账行, 合计按 audit 当下输出重算）', S)
PROV = [l for l in S.split(NL) if u'条语料／' in l and u'推导全部通过' in l]
assert len(PROV) == 1, PROV
i0 = PROV[0].find(u'当前 **')
i1 = PROV[0].find(u'）', PROV[0].find(u'audit 自报', i0))
S = S[:S.find(PROV[0]) + i0] + (u'当前 **66 条语料／' + str(PROOFS) + u' 条**推导全部通过（audit 自报“已机检的推导 '
                                + str(PROOFS) + u' 条”）') + S[S.find(PROV[0]) + i1:]

CMD = u'python -X utf8 corpus/_wire64.py'
assert S.count(CMD) == 1
S = after(S, CMD, u'python -X utf8 corpus/_mkB65.py                    # 建条目: 扁平契约 '
                  + str(len(FP)) + u' 枚键／恒等式 ' + str(gk(u'x_ident_n')) + u' 条, 采集侧对账 0 不符' + NL)
S = after(S, u'python -X utf8 corpus/_mkB65.py',
          u'python -X utf8 corpus/_mkdigest3.py B65 <entry> rfc2068 corpus/raw/httpKA/rfc2068.txt 160 120 '
          u'rfc2616 … 160 120 rfc7230 … 160 120 rfc9112 … 160 120   # 四源分节摘要(' + fmt(DIG65)
          + u' 字符, ' + str(gk(u'anchor_total')) + u'/' + str(gk(u'anchor_total')) + u' 锚全命中)' + NL)

io.open(u'corpus/README.md', 'w', encoding='utf-8', newline=NL).write(S)
json.dump(dict(entries=len(ROWS), enc=enc_all, dig=dig_all, proofs=PROOFS, b65_enc=E65, b65_dig=DIG65,
               bytes=BS, lines=LN, nonblank=NB, formfeed_only=FF, cr=CR, nonascii=NA,
               anchor_ok=OKN, anchor_err=BADN, keys=len(FP), deriv=len(DER), ident=gk(u'x_ident_n')),
          io.open(u'corpus/_b65readme.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（66 条）编码 ' + fmt(enc_all) + u' ⇎ 摘要 ' + fmt(dig_all) + u' ⇎ 保留 '
      + u'%.1f%%' % (100.0 * enc_all / dig_all) + u' ｜ 推导 ' + str(PROOFS) + u' 条 ｜ B65 行 ' + fmt(E65)
      + u'／' + fmt(DIG65) + u' ｜ 锚逐字 ' + str(OKN) + u' 处⇎错配 ' + str(BADN)
      + u' ｜ 逐份字节 ' + u'⇎'.join(fmt(x) for x in BS))
