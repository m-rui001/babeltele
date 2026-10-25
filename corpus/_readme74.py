# -*- coding: utf-8 -*-
"""README 记账(B74): 判词段 ⇎ 门槛表行 ⇎ 语料表行 ⇐ 转化指标机械行 ⇐ 合计行 ⇐ 命令块, 六个落点全部
按本遍现跑的 audit 与 raw 字节现量, 一个数不抄建条目侧快照; 条数陈述按本遍现读的 audit 行集与文件系统现算。

本遍的第六套实现(与采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注四遍换轨, 定义一律照抄):
① 面量走字节平面(`bytes.count(b'\\n')` ⇎ `b'\\x0c')` ⇎ `b'\\r')` ⇎ BOM 看前三字节), 再 `decode` 取码位,
   与建条目侧(文本平面 `str.split`)⇎ 解读注侧(手写索引循环)三轨并立, 逐枚与扁平契约对拍;
② 行数档另用 `re.split('\\n')` 数切格, splitlines 档与换页符各自另数, 三档关系按
   切格数=字节平面 `\\n` 枚数+1 ⇎ splitlines 档=切格数−末行换行+换页符 现算
   (建条目侧 `lines` ⇎ `lines_nl` 两枚键给的其实都是切格数, 真换行枚数由本遍另数);
③ 标签枚数用“枚 `<` 的后继字符是否字母”的逐枚判定(建条目侧是 `<[A-Za-z]` 正则, 解读注侧是三趟字符串扫描),
   闭标签与 `<br>` 同法; 实体枚数不重算法, 只从契约取并声明其口径;
④ 锚不再用正则配对: 本遍按 `⟦` 分段, 段内取首个 `⟨…⟩`, 与编码区原文逐枚切片回验;
⑤ 唯一码点不抄 audit 的 ALL 行: 逐条现数并与 audit 的编码列对拍后取本表所列条目的并集;
⑥ 条数三处陈述(共 N 条 ⇎ PASS（N 条）⇎ 当前 N 条语料／M 条推导)全部由本遍现读的文件系统行集与
   audit 自报数现算, 不做硬编码加减。
"""
import glob
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
C = u'corpus'
NSRC = 5
LBL = [u'821', u'1123', u'5321', u'exim', u'postfix']
YR = [u'82', u'89', u'08', u'12', u'25']
SRC = [C + u'/raw/mailRetry/rfc821.txt', C + u'/raw/mailRetry/rfc1123.txt',
       C + u'/raw/mailRetry/rfc5321.txt', C + u'/raw/mailRetry/exim4_retry_spec.html',
       C + u'/raw/mailRetry/postfix_postconf5.html']
SHW = [u'`raw/mailRetry/rfc821.txt`', u'`raw/mailRetry/rfc1123.txt`', u'`raw/mailRetry/rfc5321.txt`',
       u'`raw/mailRetry/exim4_retry_spec.html`', u'`raw/mailRetry/postfix_postconf5.html`']
KIND = [u'82 年协议定义', u'89 年主机要求', u'08 年协议标准', u'Exim 手册', u'Postfix manpage']
ANS5 = [u'只分 4yz/5yz 两类、自认难定 transient、全份零大写 MUST 零 retry 零 queue',
        u'定下限“SHOULD be at least 30 minutes”、给弃窗“at least 4-5 days”、参数“MUST be configurable”',
        u'把同一段搬进协议标准、术语换成 SMTP client、补一句 MAY 可以少试几次',
        u'一个义务词也不给, 只给阶梯规则串 F,2h,15m; G,16h,1h,1.5; F,4d,6h 与 24h 封顶、四天截止',
        u'只列参数默认 5d/5d/300s/4000s/300s/60s, 外加“0=只试一次”这一档']
ENTRY = glob.glob(u'corpus/babeltele/B74_*.md')[0]
FP = json.load(io.open(u'corpus/_b74flat.json', encoding=u'utf-8'))
DER = json.load(io.open(u'corpus/_deriv74.json', encoding=u'utf-8'))
CH = json.load(io.open(u'corpus/_b74checks.json', encoding=u'utf-8'))

AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                     text=True, encoding=u'utf-8').stdout
VERD = [l for l in AUD.split(u'\n') if l.startswith(u'保真门槛(T1 字面 + T2 推导 + T3 码位):')]
assert len(VERD) == 1, VERD
# 本遍只对本条负责: 总判若为 FAIL, 失配清单必须只含他人未完的条目, 且不得出现 B74
FAILED = [l.split(u':')[0].strip() for l in AUD.split(u'\n')
          if re.match(u'^  B\\d+: ', l) or re.match(u'^  B\\d+:', l)]
assert (u'B74' not in FAILED) and all(x != u'B74' for x in FAILED), FAILED
GATE_PASS = VERD[0].endswith(u'PASS')
S = io.open(u'corpus/README.md', encoding=u'utf-8').read()
NL = u'\r\n' if u'\r\n' in S else u'\n'


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


def num(x):
    return int(u''.join(c for c in x if c.isdigit()))


def L4(v):
    return u' ⇎ '.join(u'—' if x is None else fmt(x) for x in v)


def V4(v):
    return u'⇎'.join(str(x) for x in v)


# ---------- ①② 字节平面面量(第六轨), 逐枚与契约对拍 ----------
BS, LN, NB, ML, CH_, FFC, EFO, CR, NA, DELTA, BOM, SPL, TAIL, NLC = ([] for _ in range(14))
for p in SRC:
    b = io.open(p, u'rb').read()
    t = b.decode(u'utf-8')
    ls = re.split(u'\n', t)
    BS.append(len(b))
    CH_.append(len(t))
    LN.append(len(ls))
    NLC.append(b.count(b'\n'))
    SPL.append(len(t.splitlines()))
    TAIL.append(1 if t.endswith(u'\n') else 0)
    NB.append(len([x for x in ls if x.strip()]))
    ML.append(max(len(x) for x in ls))
    FFC.append(b.count(b'\x0c'))
    EFO.append(len([x for x in ls if x == u'\x0c']))
    CR.append(b.count(b'\r'))
    NA.append(len([c for c in t if ord(c) > 127]))
    DELTA.append(len(b) - len(t))
    BOM.append(1 if b[:3] == b'\xef\xbb\xbf' else 0)
for k, v in ((u'bytes', BS), (u'chars', CH_), (u'nonblank', NB),
             (u'maxlen', ML), (u'ff', FFC), (u'cr', CR), (u'nonascii', NA),
             (u'bom', BOM), (u'byte_cp_delta', DELTA), (u'lines_split', SPL),
             (u'tail_nl', TAIL), (u'ff_exact', EFO), (u'lines', LN), (u'lines_nl', LN)):
    assert v == gk(k), (k, v, gk(k))
# 建条目侧的 `lines` ⇎ `lines_nl` 两枚都是 `split('\n')` 的切格数, 本遍在字节平面另数真换行枚数
for i in range(NSRC):
    assert LN[i] == NLC[i] + 1, (i, LN[i], NLC[i])
    assert SPL[i] == LN[i] - TAIL[i] + FFC[i], (i, SPL[i], LN[i])
assert sum(gk(u'nul')) == 0 and sum(CR) == sum(gk(u'cr'))

# ---------- ③ 标签枚数: 逐枚 `<` 判定后继 ----------
TOPEN, TCLOSE, TBR = [], [], []
for i in range(NSRC):
    t = io.open(SRC[i], u'rb').read().decode(u'utf-8')
    if i < 3:
        TOPEN.append(0)
        TCLOSE.append(0)
        TBR.append(0)
        continue
    o = c = b = 0
    for m in re.finditer(u'<', t):
        nx = t[m.end():m.end() + 1]
        if nx.isalpha():
            o += 1
        elif nx == u'/':
            c += 1
        if t[m.end():m.end() + 2].lower() == u'br':
            b += 1
    TOPEN.append(o)
    TCLOSE.append(c)
    TBR.append(b)
assert TOPEN == gk(u'tag_open'), (TOPEN, gk(u'tag_open'))
assert TCLOSE == gk(u'tag_close')
assert TBR == gk(u'br_tag')

# ---------- ④ 锚: 按 ⟦ 分段手吃 ⟨…⟩, 逐枚切片回验 ----------
TT = io.open(ENTRY, encoding=u'utf-8').read()
_m = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', TT, re.S)
ENC = _m.group(1)
FLATENC = ENC.replace(u'\n', u'')
assert len(FLATENC) == gk(u'enc_chars')
cites, parts = [], TT[TT.index(u'⟪BabelTele⟫'):TT.index(u'## ⛓解读注')].split(u'⟦')
# 扫描止于注前: ⛓ 注里也写着 ⟦标签⟨…⟩ 的形状(那里只是行文, 不是锚), 越界会把 31 枚读成 39 枚
for seg in parts[1:]:
    if u'⟧' not in seg:
        continue
    y = seg.index(u'⟧')
    lab = seg[:y]
    if lab not in LBL or seg[y + 1:y + 2] != u'⟨':
        continue
    a = y + 2
    z = seg.index(u'⟩', a)
    cites.append((lab, seg[a:z]))
    assert seg[z:z + 1] == u'⟩'
    assert FLATENC.find(seg[a:z]) >= 0
assert len(cites) == gk(u'anchor_total'), (len(cites), gk(u'anchor_total'))
assert len(set([x[1] for x in cites])) == gk(u'anchor_distinct')
assert dict((t, len([x for x in cites if x[0] == t])) for t in LBL) == dict(
    (t, gk(u'tag_' + t)) for t in LBL)
CLS1 = len(set([x[1] for x in cites if len(set(y[0] for y in cites if y[1] == x[1])) == 1]))
CLS5 = len(set([x[1] for x in cites if len(set(y[0] for y in cites if y[1] == x[1])) == NSRC]))
# 本遍的三分类量的是“同一串被几个源标签引用”, 门槛侧量的是“同一串落在几个面”——两把尺不同, 各自闭合:
assert CLS1 + CLS5 <= gk(u'anchor_distinct')
assert gk(u'anchor_single') + gk(u'anchor_cross') + gk(u'anchor_all5') == gk(u'anchor_distinct')
# 成员尺自己走一遍(只 txt 三份: html 那两面要先剥标签, 归第五遍的三趟扫描管): 归一后的整份原文必须含该标签名下每一枚锚
P3 = [u' '.join(io.open(SRC[i], u'rb').read().decode(u'utf-8').lower().split()) for i in range(3)]
IN3 = [len([t for lab, t in cites if lab == LBL[i] and u' '.join(t.lower().split()) in P3[i]])
       for i in range(3)]
assert IN3 == [gk(u'tag_' + LBL[i]) for i in range(3)], (IN3, [gk(u'tag_' + x) for x in LBL[:3]])
assert gk(u'checks') == gk(u'anchor_distinct') * NSRC

# ---------- ⑤ 转化指标: 逐条现数, 列内并集 ----------
GROW, ALLR = [], None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        GROW.append([x.strip() for x in l.split(u'|')[1:-1]])
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR and len(GROW) == 77
IDS = [c[0] for c in GROW]
ROWS = dict((c[0], c) for c in GROW)
SL = S.split(NL)
hh = [i for i, l in enumerate(SL) if l.startswith(u'| entry | 编码字符 |')]
assert len(hh) == 1
tt0 = [i for i in range(hh[0], len(SL)) if SL[i].startswith(u'| **合计（')]
assert len(tt0) == 1
LISTED0 = [l.split(u'|')[1].strip() for l in SL[hh[0] + 2:tt0[0]]]
assert all(x.startswith(u'B') for x in LISTED0)
assert u'B74' not in LISTED0 and S.count(u'| B74 |') == 0 and S.count(u'**B74 问的是') == 0
LISTED = sorted(LISTED0 + [u'B74'], key=lambda k: int(k[1:]))
UNACC = [c for c in GROW if c[0] not in LISTED]
ENCS, EN, DG = [], [], []
for t in LISTED:
    f = glob.glob(u'corpus/babeltele/%s_*.md' % t)
    assert len(f) == 1, t
    tt = io.open(f[0], encoding=u'utf-8').read()
    mm = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', tt, re.S)
    e = mm.group(1).replace(u'\n', u'')
    assert len(e) == num(ROWS[t][2]), (t, len(e), ROWS[t][2])
    assert len(set(e)) == num(ROWS[t][5]), t
    ENCS.append(set(e))
    EN.append(len(e))
    DG.append(num(ROWS[t][1]))
UNI = set().union(*ENCS)
enc_all, dig_all = sum(EN), sum(DG)
assert enc_all + sum(num(c[2]) for c in UNACC) == num(ALLR[2])
assert dig_all + sum(num(c[1]) for c in UNACC) == num(ALLR[1])
E74, D74 = num(ROWS[u'B74'][2]), num(ROWS[u'B74'][1])
assert E74 == gk(u'enc_chars'), (E74, gk(u'enc_chars'))
# 摘要长度不自己另定口径(本遍切段得 5 604, audit 口径 5 583, 差在其节题行): 只由 audit 自报的保留率反推校验
assert ROWS[u'B74'][3] == u'%.1f%%' % (100.0 * E74 / D74), (ROWS[u'B74'][3], E74, D74)
assert ROWS[u'B74'][4] == u'%.3f%%' % (100.0 * E74 / sum(BS)), ROWS[u'B74'][4]
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])
CLOSEK = len([k for k in FP if u'close' in k])
DKEYS = len(set(re.findall(u"B74V\\('([a-z0-9_]+)'", json.dumps(DER, ensure_ascii=False))) & set(FP))

# ---------- 门槛表 B74 行 ----------
HEADROW = (u'| B74 | ' + fmt(E74) + u'（新建, 投递失败的邮件到底多久再试一次、什么时候不再试 交一份 SMTP 协议定义 ⇎ 两份主机要求 ⇎ '
           u'两份 MTA 手册各答一遍 ' + str(gk(u'anchor_total')) + u' 处标注／' + str(gk(u'anchor_distinct'))
           + u' 个不同串（登记全命中, 单源 ' + str(gk(u'anchor_single')) + u' ⇎ 穿二至四源 ' + str(gk(u'anchor_cross'))
           + u' ⇎ 五源全现 ' + str(gk(u'anchor_all5')) + u'——一枚答话不可能五份同源, 因为三份 RFC 是 72 列硬换行面、两份手册是无换行长行面; 编码区 '
           + fmt(E74) + u' 字符, 归属检查 ' + str(gk(u'checks')) + u' 次, 错配 ' + str(gk(u'anchor_err'))
           + u'）: 五色锚位 ' + u' ⇎ '.join(x + u' ⟦' + y + u'⟧' for x, y in zip(LBL, LBL))
           + u'; 五档阶梯（原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 标签替空格的断面 ⇎ 标签替空串的粘面）读到 '
           + V4(gk(u'sn_strict_docs')) + u' ／ ' + V4(gk(u'sn_fold_docs')) + u' ／ ' + V4(gk(u'sn_sh_docs'))
           + u' ／ ' + V4(gk(u'sn_ds_docs')) + u' ／ ' + V4(gk(u'sn_dj_docs')) + u' 枚（在册针 '
           + str(gk(u'needle_n')) + u' 枚, 归各份 ' + V4(gk(u'needles_owned')) + u' 枚, 折行一次救回 '
           + str(gk(u'fold_minus_strict_n')) + u' 枚, 剥标签断面新读 ' + str(gk(u'ds_only_n')) + u' 枚, 换成粘面再多 '
           + str(gk(u'dj_only_n')) + u' 枚而同时丢 ' + str(gk(u'ds_no_dj_n')) + u' 枚, 摘壳档比折平档一粒不少（差 '
           + V4(gk(u'sh_minus_fold')) + u'）, 阶梯单调 ' + str(gk(u'ladder_monotone')) + u'）; 最宽档落空 '
           + str(len(gk(u'dead_needles'))) + u' 枚内容死针 ⇎ 反向对照 ' + str(gk(u'neg_n')) + u' 枚合计命中 '
           + str(gk(u'neg_hit_widest')) + u' 枚; 十二族措辞针（' + u'⇎'.join(gk(u'tier_words')) + u'）命中族数 '
           + V4(gk(u'tier_hit_fams')) + u' ⇎ 零枚族数 ' + V4(gk(u'tier_zero_fams')) + u' ⇎ 族内合计 '
           + V4(gk(u'tier_tot')) + u' 枚——唯一在剥标签后掉枚的是 Postfix（' + str(gk(u'tier_fold_tot')[4])
           + u' ⇎ ' + str(gk(u'tier_tot')[4]) + u', 默认值成对印在目录项的 title 属性里, 属性内文本随标签一起被替成空格）; '
           + u'语气五轨（MUST NOT ⇎ MUST ⇎ SHOULD NOT ⇎ SHOULD ⇎ MAY）合计 ' + V4(gk(u'tone_tot')) + u' ⇎ 裸 MUST '
           + V4(gk(u'must_bare')) + u' ⇎ 小写 must ' + V4(gk(u'tone_must_lc')) + u'——零大写 MUST 的恰是 821 与 Exim 两份'
             u'（判定 ' + str(gk(u'tone_zero_must_pair')) + u'）, 而 821 的小写 must 有 ' + str(gk(u'tone_must_lc')[0])
             + u' 枚; 主答段内三轨 MTA 全零（判定 ' + str(gk(u'blk_tone_none_exim_pf')) + u'）⇎ 5321 段内那枚 MAY 是十二段里唯一一枚; '
           + u'换算表 ' + str(len(gk(u'cv_sec'))) + u' 档秒 ' + V4(gk(u'cv_sec')) + u'（' + u' ⇎ '.join(gk(u'cv_names'))
             + u'）: 低于 1123 下限 30 分钟的 ' + str(gk(u'cv_below_n')) + u' 档 ⇎ 不低于 ' + str(gk(u'cv_above_n'))
             + u' 档（相加−表长 ' + str(gk(u'cv_close')) + u'）, 4-5 天窗两端 345 600 ⇎ 432 000 各被一份 MTA 的默认踩住（命中 '
             + str(gk(u'band_edge_hits')) + u' 处）, Exim 默认规则串 ' + gk(u'ex_def_rule') + u' 分 '
             + str(gk(u'ex_def_sets')) + u' 段 ' + str(gk(u'ex_attempts_tot')) + u' 档、封顶 ' + fmt(gk(u'ex_rim_cap'))
             + u' ⇎ 截止 ' + fmt(gk(u'ex_def_span')) + u' ⇎ 过期 ' + fmt(gk(u'ex_expire_days')) + u' 秒; Postfix 六参数默认 '
             + u'/'.join(gk(u'pf_def_tok')) + u' = ' + V4(gk(u'pf_def_sec')) + u' 秒; '
           + u'搬字两把尺: 行尺长行池 ' + fmt(gk(u'pool_n')) + u' 条分档 ' + V4(gk(u'pool_tier')) + u'（闭合 '
           + str(gk(u'pool_tier_close')) + u'）⇎ 最大一对 ' + gk(u'pair_max_lbl') + u' ' + str(gk(u'pair_max'))
           + u' 条, 其中逐字节同 ' + str(gk(u'pair_max_byte')) + u' 条 ⇎ 只归一同 ' + str(gk(u'pair_max_norm_only'))
           + u' 条, 写法分家四桶 ' + gk(u'axis_str') + u'（桶账闭合 ' + str(gk(u'axis_close')) + u'）; 换成句尺池 '
           + fmt(gk(u's_pool_n')) + u' 句 ⇎ 最大一对 ' + str(gk(u's_pair_max')) + u' 句, 同两对增益 '
           + str(gk(u's_ruler_gain_821_5321')) + u' ⇎ ' + str(gk(u's_ruler_gain_1123_5321')) + u' 句（72 列硬换行把一句切成多行）⇎ '
           + u'两份 MTA 与三份 RFC 之间共用句 ' + str(gk(u's_pair_html')) + u' 句 ⇎ 共用行 ' + str(gk(u'pool_html_shared'))
           + u' 条——两套尺子都读出零重叠，手册改述规范而非抄写原句; '
           + u'答段十二段共 ' + str(gk(u'blk_rows_tot')) + u' 行 ⇎ ' + fmt(gk(u'blk_words_tot')) + u' 词, 五段主答句 '
           + str(gk(u'blk_five_rows')) + u' 行 ⇎ ' + str(gk(u'blk_five_words')) + u' 词; 1123 段 ⇎ 5321 段词集 独有 '
           + str(gk(u'w_only_1123')) + u' ⇎ ' + str(gk(u'w_only_5321')) + u' 词 ⇎ 共有 ' + str(gk(u'w_common_12'))
           + u' ⇎ 对称差 ' + str(gk(u'w_sym_diff')) + u', 共头 ' + str(gk(u'pre_1123_5321')) + u' 词 ⇎ 共尾 '
           + str(gk(u'suf_1123_5321')) + u' 词（同头同尾而中间改写）⇎ 两段行号位移 ' + str(gk(u'delay_shift_5321'))
           + u' ⇎ ' + str(gk(u'giveup_shift_5321')) + u' 行（差 ' + str(gk(u'shift_delta')) + u' 行, 故非整段平移）; '
           u'硬换行把答案本身切开: 行针复核 ' + str(gk(u'pin_rt_ok')) + u'／' + str(gk(u'pin_rt_n')) + u' 枚回原行命中 ⇎ '
           + u'错行反向 ' + str(gk(u'pin_wrongline')) + u' ⇎ 收束短语被切 ' + str(gk(u'conf_straddle_1123')) + u' ⇎ '
           + str(gk(u'conf_straddle_5321')) + u' 处; 组面⇎非空行⇎壳行三本账逐份 ' + V4(gk(u'grp_close')) + u'（闭合判定位 '
           + str(gk(u'grp_ledger_close')) + u'：该位取 1 才是逐份全平，不平记 0）⇎ Postfix 唯一一枚跨行组（' + V4(gk(u'grp_glued')) + u'）⇎ “HTML 没有页壳”不成立'
             u'只因其壳全是空行; 两遍壳谓词分解到行: 采集多判 ' + str(gk(u'shell_pick_only')[0]) + u' 行全在抬头 ⇎ 本遍多判 '
           + str(sum(gk(u'shell_mk_only'))) + u' 行, 两遍账逐份相平（采集数＋本遍多判−采集多判＝本遍数, 五份绝对差合计 '
           + str(gk(u'shell_ledger_close')) + u'）; 引用三式并计（空格式 ⇎ 连写式 ⇎ 短横式）逐份闭合 '
           + V4(gk(u'cite_forms_close')) + u', 关键不对称: 1123 面上 “RFC 821” 空格式 ' + str(gk(u'cite_821_in_1123'))
           + u' 枚 ⇎ “RFC-821” 短横式 ' + str(gk(u'cite_821_hy_in_1123')) + u' 枚; 谱系 5321 ⟦5321⟧ '
           + gk(u'obs_line')[2] + u' ⇎ ' + gk(u'upd_line')[2] + u', 821 一行 Replaces ' + u' ⇎ '.join(str(x) for x in gk(u'repl_ids'))
           + u', 对象并集 ' + str(gk(u'target_n')) + u' 个; 抬头年 ' + V4(gk(u'years')) + u'（三份 RFC 的月份 '
           + u' ⇎ '.join([x for x in gk(u'months_txt') if x]) + u' ⇎ 两份手册抬头不带月份）跨 ' + str(gk(u'year_span')) + u' 年, 逆序 ' + str(gk(u'year_inversions')) + u' 处; 术语换代 sender-SMTP '
           + V4(gk(u'sender_smtp')) + u' ⇎ receiver-SMTP ' + V4([x[3] for x in gk(u'terms')]) + u' ⇎ SMTP client '
           + V4(gk(u'smtp_client')) + u', 新名在“新名+旧名”里占的千分位 ' + V4(gk(u'term_new_per_mille'))
           + u'（-1 是 Exim 两个词面各 ' + str(gk(u'smtp_client')[3]) + u' ⇎ ' + str(gk(u'sender_smtp')[3])
           + u' 枚、分母为零时登记的哨兵，不是负千分比）; '
           + u'扁平契约 ' + str(len(FP)) + u' 枚键（键数自证 ' + str(gk(u'contract_n')) + u'=' + str(len(FP) - 1)
           + u'+1）⇎ 标量恒等式 ' + str(gk(u'scalar_clos_n')) + u' 条通过 ' + str(gk(u'scalar_clos_sum')) + u' ⇎ 含 close 的键 '
           + str(CLOSEK) + u' 枚其中逐份清单 ' + str(gk(u'list_clos_n')) + u' 枚 ⇎ DERIV ' + str(len(DER))
           + u' 枚算式／面内恒等式共键 ' + str(gk(u'x_ident_n')) + u' 条; 采集侧同定义标量 ' + str(gk(u'pick_agree'))
           + u'/' + str(gk(u'pick_agree')) + u' 枚相符 ⇎ ' + str(gk(u'pick_diff')) + u' 枚不符（壳账与针表不横比: 采集数 '
           + str(gk(u'needle_table_pick')) + u' 枚字面针 ⇎ 本库两遍数 ' + str(gk(u'needle_table_mk')) + u' 枚面上导出的锚句）; '
           + u'工具侧 atomcheck 的 SRC 表未登记本条, 五份面的逐字性由门槛侧 ' + str(gk(u'checks')) + u' 次归属检查承担（逐字命中 '
           + str(gk(u'anchor_total')) + u' 处 ⇎ 错配 ' + str(gk(u'anchor_err')) + u'） |')

# ---------- 语料表 B74 行 ----------
C74 = (u'| B74 | ' + u' ⇎ '.join(
    SHW[i] + u'（' + YR[i] + u' ⟦' + LBL[i] + u'⟧：' + fmt(BS[i]) + u' 字节／面内码位 ' + fmt(CH_[i])
    + u'／行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i])
    + u'／换页符 ' + str(FFC[i]) + u' 枚（独占整行 ' + str(EFO[i]) + u' 行）'
    + (u'／最长行 ' + str(ML[i]) + u' 列' if i < 3 else
       u'／开闭标签 ' + fmt(TOPEN[i]) + u' ⇎ ' + fmt(TCLOSE[i]) + u' 枚（其中 `<br>` ' + str(TBR[i]) + u' 枚）／实体 '
       + fmt(gk(u'ent_total')[i]) + u' 枚／最长行 ' + str(ML[i]) + u' 列')
    + u'／答句 ' + ANS5[i] + u'／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i]) + u'／BOM ' + str(BOM[i]) + u'）'
    for i in range(NSRC))
           + u' | 五份答同一个问题 ⇒ 答的是五种东西: 类别(821, 全篇零 retry 零 queue 零大写 MUST 而小写 must '
             + str(gk(u'tone_must_lc')[0]) + u' 枚) ⇎ 数字下限(1123, “SHOULD be at least 30 minutes” ⇎ “at least 4-5 days” ⇎ '
             + u'“MUST be configurable”) ⇎ 逐字搬家并放宽一句(5321, 与 1123 共头 ' + str(gk(u'pre_1123_5321')) + u' 词 ⇎ 共尾 '
             + str(gk(u'suf_1123_5321')) + u' 词, 新词 ' + str(gk(u'w_only_5321')) + u' 枚) ⇎ 可解析阶梯(Exim, 零语气词只给 '
             + gk(u'ex_def_rule') + u') ⇎ 参数表(Postfix, 六参数默认 ' + u'/'.join(gk(u'pf_def_tok')) + u'); '
             + u'“什么时候不再试”只有两份答到秒: ' + fmt(gk(u'ex_def_span')) + u' ⇎ ' + fmt(gk(u'pf_def_sec')[0])
             + u' 秒, 正踩在 1123 那句“4-5 天”的两端 ⇎ 三份 RFC 一个也不给（“cutoff”字样 ' + V4(gk(u'word_cutoff')) + u' 枚） |')

# ---------- 判词段 ----------
PARA = (u'**B74 问的是投递失败的邮件到底多久再试一次、什么时候不再试，五份一手文书给出五种答法**：'
        + u' ⇎ '.join(SHW[i] + u'（' + YR[i] + u' ⟦' + LBL[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
                      + u'／非空行 ' + fmt(NB[i]) + u'／最长行 ' + str(ML[i]) + u' 列／答句 ' + ANS5[i]
                      + u'／回车 ' + str(CR[i]) + u'／非 ASCII ' + str(NA[i]) + u'／BOM ' + str(BOM[i]) + u'）'
                      for i in range(NSRC))
        + u'——三份 RFC 同为 72 列硬换行面且换页符独占整行 ' + u' ⇎ '.join(str(EFO[i]) for i in range(3))
          + u' 行, 两份 MTA 手册是 ' + u' ⇎ '.join(str(ML[i]) for i in range(3, 5)) + u' 列长行面且零枚换页符; 全库回车 '
          + V4(CR) + u' 枚 ⇎ NUL ' + V4(gk(u'nul')) + u' 枚 ⇎ BOM ' + V4(BOM) + u' 枚, 非 ASCII ' + V4(NA)
          + u' 枚全部落在两份 HTML 上, 字节−码位差 ' + V4(DELTA) + u'（三份 RFC 恒零）; Postfix 一页 '
          + fmt(gk(u'tag_open')[4] + gk(u'tag_close')[4]) + u' 枚标签里 `<br>` 独占 ' + str(TBR[4])
          + u' 枚 ⇎ 实体 ' + fmt(gk(u'ent_total')[4]) + u' 枚, 数字实体剥后仍留 ' + fmt(gk(u'ent_numeric_left')[4])
          + u' 枚——默认值就成对印在目录项的 title 属性里, 措辞族在剥标签前后因此差 '
          + str(gk(u'tier_fold_tot')[4] - gk(u'tier_tot')[4]) + u' 枚。五种答法不是措辞差异而是类型差: 821 只把失败分成 4yz/5yz 两类'
            u'（两枚类别定义相距 ' + str(gk(u'yz_gap')) + u' 行）并当场自认“两个站点很难对 transient 取一致”（距定义句 '
            + str(gk(u'hard_4yz_gap')) + u' 行, 经验法则再后 ' + str(gk(u'thumb_hard_gap')) + u' 行）, 全篇 retry 族 '
            + str(gk(u'retry_word')[0]) + u' 枚 ⇎ queue 族 ' + str(gk(u'queue_word')[0]) + u' 枚 ⇎ 大写 MUST '
            + str(gk(u'tone_MUST')[0]) + u' 枚而小写 must ' + str(gk(u'tone_must_lc')[0]) + u' 枚 ⇎ 1123 第一次给出数字'
              u'（下限“SHOULD be at least 30 minutes”、给弃窗“at least 4-5 days”、参数“MUST be configurable”, 外加 DNS 指数退避与 5 秒下限）⇎ '
              + u'5321 把同一段逐字搬进协议标准（共头 ' + str(gk(u'pre_1123_5321')) + u' 词 ⇎ 共尾 '
              + str(gk(u'suf_1123_5321')) + u' 词——两头按词位比 ⇎ 5321 段独有的新词 ' + str(gk(u'w_only_5321'))
              + u' 枚——那把尺是去重词集, 两段行号后移同为 '
              + str(gk(u'delay_shift_5321')) + u' ⇎ ' + str(gk(u'giveup_shift_5321')) + u' 行）并把主语换成 SMTP client'
                u'（旧名 sender-SMTP 只剩 ' + str(gk(u'sender_smtp')[2]) + u' 枚 ⇎ 新名起 ' + str(gk(u'smtp_client')[2])
                + u' 枚）, 还补一句 MAY: 目的地地址可以少试几次 ⇎ Exim 一枚义务词也不给（全篇语气 ' + str(gk(u'tone_tot')[3])
                + u' 枚）, 给的是阶梯 ' + gk(u'ex_def_rule') + u'（' + str(gk(u'ex_attempts_tot')) + u' 档、封顶 '
                + fmt(gk(u'ex_rim_cap')) + u' 秒、截止 ' + fmt(gk(u'ex_def_span')) + u' 秒）⇎ Postfix 只列默认值 '
                + u'/'.join(gk(u'pf_def_tok')) + u' 六档, 另立“设 0 就只试一次”这一档（该短语在面上 '
                + str(gk(u'pf_zero_once')) + u' 枚）。给弃时刻五份只有两份给全: ' + fmt(gk(u'ex_def_span')) + u' ⇎ '
                + fmt(gk(u'pf_def_sec')[0]) + u' 秒各踩住 1123 那句“4-5 天”的一端（窗内命中 ' + str(gk(u'band_edge_hits'))
                + u' 处）, 三份 RFC 一个也不给——“cutoff”字样在五份面上 ' + V4(gk(u'word_cutoff')) + u' 枚, 只在 Exim 存活; '
                + u"低于 30 分钟下限的档位 " + str(gk(u'cv_below_n')) + u" 档（60 ⇎ 300 ⇎ 300 ⇎ 900 秒）全是两份 MTA 的首档, "
                  u"即手册比主机要求勤得多, 差别被阶梯吃掉。谁抄谁可量而且随尺翻倍: 行尺最大一对 " + gk(u'pair_max_lbl') + u" "
                  + str(gk(u'pair_max')) + u" 条（逐字节同 " + str(gk(u'pair_max_byte')) + u" 条）换成句尺 "
                  + str(gk(u's_pair_max')) + u" 句, 而 5321 与它抬头没提的 821 共用 " + str(gk(u's_pair_821_5321'))
                  + u" 句 ⇎ 与它声明更新的 1123 只共用 " + str(gk(u's_pair_1123_5321')) + u" 句; 两份 MTA 与三份 RFC 之间共用行 "
                  + str(gk(u'pool_html_shared')) + u" 条 ⇎ 共用句 " + str(gk(u's_pair_html')) + u" 句, 但 Exim 自家面上就印着两条"
                                          u"不同的 `* *` 规则行（" + str(gk(u'ex_star_star_rules')) + u" 枚 ⇎ 去重 "
                                          + str(gk(u'ex_star_star_distinct')) + u" 枚, 前两段逐字同只差末档）而默认那一条只印一处。"
                                          u"版式还会吃掉答案: 在册 " + str(gk(u'needle_n')) + u" 枚针里只有 "
                                          + str(sum(gk(u'sn_strict_docs'))) + u" 枚能在单行读全（逐份 "
                                          + V4(gk(u'sn_strict_docs')) + u"）, " + str(gk(u'fold_minus_strict_n'))
                                          + u" 枚靠折行救回, 剥标签再救 " + str(gk(u'ds_only_n')) + u" 枚（粘面多 "
                                          + str(gk(u'dj_only_n')) + u" 枚而丢 " + str(gk(u'ds_no_dj_n')) + u" 枚）, 摘壳档一粒不少"
                                                                                                       u"（差 " + V4(gk(u'sh_minus_fold'))
                                          + u"）; 72 列硬换行正切在给弃句的收束短语里, 反向对照把末字拿到首字行去验命中 "
                                          + str(gk(u'pin_wrongline')) + u" 枚。门槛侧 " + str(len(DER)) + u" 枚算式／"
                                          + str(gk(u'x_ident_n')) + u" 条面内恒等式（标量 " + str(gk(u'scalar_clos_n'))
                                          + u" 项通过 " + str(gk(u'scalar_clos_sum')) + u"）, 扁平契约 " + str(len(FP))
                                          + u" 枚键由建条目 ⇎ 解读注两套实现逐枚复测（采集侧同定义标量 "
                                          + str(gk(u'pick_agree')) + u"/" + str(gk(u'pick_agree')) + u" 枚相符 ⇎ 逐值不符 "
                                          + str(gk(u'pick_diff'))
                                          + u" ⇎ 本遍独有 0）; 其中 " + str(DKEYS) + u" 枚进得了 DERIV 算式 ⇎ 余下 "
                                          + str(len(FP) - DKEYS) + u" 枚是形状清单、字符串表与段窗切片。")

# ---------- 落盘: 定点插入, 不整体重写 ----------
def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:60])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


def after_row(s, eid, needle, text):
    """在唯一一行(以 `| eid | ` 开头且含 needle)之后插一行, 不靠邻居条目的具体读数定位。"""
    hits = [l for l in s.split(NL) if l.startswith(u'| ' + eid + u' | ') and needle in l]
    assert len(hits) == 1, (eid, needle, len(hits))
    return after(s, hits[0], text)


def subn(pat, mk, s, n=1):
    ms = list(re.finditer(pat, s))
    assert len(ms) == n, (pat, len(ms))
    m = ms[0]
    return s[:m.start()] + mk(m) + s[m.end():]


S2 = after(S, u'**B72 问的是收到 302 之后', PARA + NL + NL)
S2 = after_row(S2, u'B72', u'（新建,', HEADROW + NL)                        # 门槛表
S2 = after_row(S2, u'B72', u'`raw/httpRedir/rfc2616.txt`', C74 + NL)        # 语料表

L2 = S2.split(NL)
h2 = [i for i, l in enumerate(L2) if l.startswith(u'| entry | 编码字符 |')]
assert len(h2) == 1
t2 = [i for i in range(h2[0], len(L2)) if L2[i].startswith(u'| **合计（')]
assert len(t2) == 1
T0 = t2[0]
present = [l.split(u'|')[1].strip() for l in L2[h2[0] + 2:T0]]
assert present == LISTED0, present[:3]
L2[T0:T0] = [(u'| B74 | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
              % (fmt(E74), ROWS[u'B74'][3], ROWS[u'B74'][4], ROWS[u'B74'][5], ROWS[u'B74'][7]))]
HC = len(L2[h2[0]].split(u'|'))
cells = L2[T0 + 1].split(u'|')
assert len(cells) == HC, (len(cells), HC)
UN = sorted(set(c[0] for c in UNACC), key=lambda k: int(k[1:]))
HAsROW = [t for t in UN if any(l.startswith(u'| ' + t + u' | ') for l in SL)]
cells[1] = u' **合计（' + str(len(LISTED)) + u' 条）** '
cells[2] = u' **' + fmt(enc_all) + u'** '
cells[3] = (u' **%.1f%%**（摘要段合计 ' % (100.0 * enc_all / dig_all) + fmt(dig_all)
            + u'，本遍补记的一枚为 ' + fmt(E74) + u' 编码／' + fmt(D74)
            + u' 摘要；两列合计与本表所列 ' + str(len(LISTED)) + u' 条一致，故不取 audit 的 ALL 行'
              + u'（它多含已接线而未在本表记账的 ' + u'⇎'.join(UN) + u'：编码 '
              + fmt(num(ALLR[2]) - enc_all) + u' ⇎ 摘要 ' + fmt(num(ALLR[1]) - dig_all)
              + u'，其中 B77 同码两册故并集按行计）；唯一码点那格由本遍按 audit 的编码区正则逐条现数取列内并集，'
                u'逐条与 audit 现算值对拍） ')
cells[5] = u' **%s** ' % fmt(len(UNI))
assert len(cells) == len(L2[T0 + 1].split(u'|')), (len(cells), len(L2[T0 + 1].split(u'|')))
L2[T0 + 1] = u'|'.join(cells)
NOTE = [i for i, l in enumerate(L2) if l.startswith(u'（B54 起的 ') and u'机械行' in l]
assert len(NOTE) == 1, NOTE
L2[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与字符/语义单元五格, '
               u'不重写各条的口径注; 本遍再直补 B74 一枚, 合计行只列本表已记账条目, 唯一码点由本遍逐条现数取并集, '
               u'不再抄 ALL 行。）'
               % len([x for x in present + [u'B74'] if int(x[1:]) >= 54]))
S2 = NL.join(L2)

FIDS = sorted(set(int(re.match(r'B(\d+)_', os.path.basename(x)).group(1))
                  for x in glob.glob(u'corpus/babeltele/B*.md') if re.match(r'B\d+_', os.path.basename(x))))
assert [u'B%02d' % x for x in FIDS] == [c[0] for c in GROW], (len(FIDS), len(GROW))


def runs(ns):
    out, a, b = [], ns[0], ns[0]
    for x in ns[1:]:
        if x == b + 1:
            b = x
        else:
            out.append((a, b))
            a = b = x
    out.append((a, b))
    return u'、'.join(u'B%02d..B%02d' % (a, b) if b > a else u'B%02d' % a for a, b in out)


# 总判若是 FAIL, 只能如实写: 本遍只保证 B74 那行 0 错配, 并点名失配条目与其 audit 自报的失配数
FAILD = dict((u'B' + m.group(1), len([x for x in m.group(2).split(u',') if x.strip()]))
             for m in re.finditer(u'^  B(\\d+): 编码侧=\\[(.*?)\\]', AUD, re.M))
assert (not GATE_PASS) == bool(FAILD) and u'B74' not in FAILD, (GATE_PASS, FAILD)

S2 = subn(u'共 \\*\\*\\d+ 条\\*\\*（`babeltele/[^`]*`, 本遍补上 B\\d+ 的四处记账行[^）]*）',
          lambda m: (u'共 **%d 条**（`babeltele/%s`, 本遍补上 B74 的四处记账行, 合计按本表所列 %d 条现算, '
                     u'唯一码点逐条现数；已接线而未进本表合计行的 %s 中, %s 已记了门槛表⇎语料表两行, %s 连门槛行也没有）'
                     % (len(FIDS), runs(FIDS), len(LISTED), u'／'.join(UN), u'／'.join(HAsROW),
                        u'／'.join([t for t in UN if t not in HAsROW]) or u'无')), S2)
S2 = subn(u'## 保真门槛：`python corpus/audit.py` → \\*\\*PASS\\*\\*（\\d+ 条）',
          lambda m: (u'## 保真门槛：`python corpus/audit.py` → **PASS**（%d 条）' % len(FIDS)
                     if GATE_PASS else
                     u'## 保真门槛：`python corpus/audit.py` → 本遍复跑总判 **FAIL**：失配只落在未记账的 %s'
                     u'（audit 报其 %d 枚编码侧数字锚在原文侧读不到）；本遍记账的 B74 错配 %d 枚, 本表所列 %d 条不受影响'
                     % (u'／'.join(sorted(FAILD)), sum(FAILD.values()), gk(u'anchor_err'), len(LISTED))), S2)
S2 = subn(u'当前 \\*\\*\\d+ 条语料／\\d+ 条\\*\\*推导全部通过（audit 自报“已机检的推导 \\d+ 条”）',
          lambda m: (u'当前 **%d 条语料／%d 条**推导%s（audit 自报“已机检的推导 %d 条”，行集与文件数相符 %d ⇎ %d）'
                     % (len(FIDS), PROOFS,
                        u'全部通过' if GATE_PASS else u'除 %s 外全部通过' % u'／'.join(sorted(FAILD)),
                        PROOFS, len(GROW), len(FIDS))), S2)

assert S2.count(u'python -X utf8 corpus/_fill72.py') == 1
L74 = [(u'python -X utf8 corpus/_mkB74.py',
        u'                    # 建条目(前半, 与 _mk74emit.py 同场 exec): 扁平契约 ' + str(len(FP))
        + u' 枚键／标量恒等式 ' + str(gk(u'scalar_clos_n')) + u' 条 ⇎ DERIV ' + str(len(DER))
        + u' 枚算式, 五档面(原行⇎折平⇎摘壳⇎断面⇎粘面)⇎游标针 ⇎ 正则针两尺, 采集侧同定义标量 '
        + str(gk(u'pick_agree')) + u'/' + str(gk(u'pick_agree')) + u' 枚相符'),
       (u'python -X utf8 corpus/_mkdigest3.py B74 <entry> '
        + u' '.join(u'%s %s 300 200' % (LBL[i], SRC[i]) for i in range(NSRC)),
        u'   # 五源分节摘要(' + fmt(D74) + u' 字符, ' + str(gk(u'anchor_total'))
        + u' 枚锚全命中, 五份各开一窗 300/200)'),
       (u'python -X utf8 corpus/_wire74.py',
        u'                    # 幂等接线: SRC/ATOM/SCAN(审计器侧第三套实现)/DERIV/B74V 进 audit.py, 落盘前复跑 '
        + str(len(FP)) + u' 枚扁平键 ⇎ ' + str(len(DER)) + u' 枚算式 ⇎ ' + str(gk(u'checks')) + u' 次归属检查'),
       (u'python -X utf8 corpus/_fill74.py',
        u'                    # 第五遍(注区): 字节平面 ⇎ 手写剥标签三趟 ⇎ bisect 行号尺 ⇎ token 语气轨各重导一次, '
        + str(gk(u'scalar_clos_n')) + u' 条恒等式现算归零后写回 ⛓解读注（14 行复测表 ⇎ 复算 ' + str(len(FP))
        + u' 键对账 0 不符 ⇎ 独有 0 枚）')]
CUR = u'python -X utf8 corpus/_fill72.py'
for head, tail in L74:
    S2 = after(S2, CUR, head + tail + NL)
    CUR = head

T3 = u'corpus/README.md.tmp74'
io.open(T3, u'w', encoding=u'utf-8', newline=NL).write(S2)
os.replace(T3, u'corpus/README.md')
json.dump(dict(listed=LISTED, listed_n=len(LISTED), enc=enc_all, dig=dig_all, uniq=len(UNI),
               proofs=PROOFS, b74_enc=E74, b74_dig=D74, unaccounted=UN, audit_rows=len(GROW),
               entries_files=len(FIDS), gate_pass=GATE_PASS, gate_failed=FAILD,
               bytes=BS, chars=CH_, lines=LN, newlines=NLC, nonblank=NB,
               maxlen=ML, ff=FFC, ff_only=EFO, cr=CR, nonascii=NA, bom=BOM, delta=DELTA,
               tag_open=TOPEN, tag_close=TCLOSE, br=TBR, keys=len(FP), deriv=len(DER),
               close_keys=CLOSEK, dkeys=DKEYS, anchors=gk(u'anchor_total'), checks=gk(u'checks')),
          io.open(u'corpus/_b74readme.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（%d 条）编码 %s ⇎ 摘要 %s ⇎ 保留 %.1f%% ｜ 唯一码点(列内并集) %s ｜ 未记账 %s ｜ '
      u'audit 行 %d ⇎ 文件 %d ｜ 推导 %d 条 ｜ 本遍总判 %s%s ｜ B74 行 %s 编码／%s 摘要 ｜ 锚 %d 处⇎归属检查 %d 次⇎错配 %d'
      % (len(LISTED), fmt(enc_all), fmt(dig_all), 100.0 * enc_all / dig_all, fmt(len(UNI)),
         u'⇎'.join(UN), len(GROW), len(FIDS), PROOFS, u'PASS' if GATE_PASS else u'FAIL',
         u'' if GATE_PASS else u'（只落在 %s）' % u'⇎'.join(sorted(FAILD)),
         fmt(E74), fmt(D74), gk(u'anchor_total'), gk(u'checks'), gk(u'anchor_err')))
