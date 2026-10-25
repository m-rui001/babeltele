# -*- coding: utf-8 -*-
"""README 记账(B80): 判词段 ⇎ 门槛表行 ⇎ 语料表行 ⇐ 转化指标机械行 ⇐ 合计行 ⇐ 命令块, 六个落点全部
按本遍现跑的 audit 与 raw 字节现量, 一个数不抄建条目侧或解读注侧的快照; 条数陈述按本遍现读的文件系统
行集与 audit 自报数现算。

本遍的第七套实现(采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注 ⇎ 上一遍记账五轨之外, 定义一律照抄):
① 面量走字节平面(`bytes.count(b'\\n')` ⇎ `b'\\x0c'` ⇎ `b'\\r'` ⇎ BOM 看前三字节), 再 `decode` 取码位,
   与建条目侧(文本平面 `str.split`)⇎ 解读注侧(手写索引循环)三档并立, 逐枚与扁平契约对拍;
② 行数三档关系现算: 切格数=字节平面 `\\n` 枚数+1 ⇎ `splitlines()`=切格数−末行换行+换页符
   (建条目侧 `lines` ⇎ `lines_nl` 给的其实都是切格数);
③ 尖括号四把尺换“逐枚 `<` 起手索引扫描、吃到首个 `>` 后从其后续扫”的扫描轨(mk 用 `findall(r'<[^>\\n]+>')`,
   解读注用手写游标扫描; 按 `<` 切段的 naive 轨会把嵌套 `<` 另起一枚, 逐枚不等但总数相等, 故不可用),
   分类仍看首字符, 开名形再分 ABNF 值占位 ⇎ 真标签名两档; 实体与注释同法切段, 只从契约取数并声明口径;
④ 锚不用正则配对: 按 `⟦` 分段取首个 `⟨…⟩`, 逐枚切片回编码区原文, 再按标签回它自己那一源做
   归一子串核验(门槛侧的 195 次归属检查之外本遍另走一遍);
⑤ README 行文里的每一枚英文片段都要在它那一源的归一面上命中才允许落盘(不靠手打记忆);
⑥ 唯一码点不抄 audit 的 ALL 行: 逐条现数并与 audit 的编码列对拍后取本表所列条目的并集;
⑦ 条数三处陈述(共 N 条 ⇎ PASS（N 条）⇎ 当前 N 条语料／M 条推导)全部由本遍现读的文件系统行集与
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
LBL = [u'2616', u'7231', u'6585', u'8470', u'9110']
YR = [u'99', u'14', u'12', u'18', u'22']
SRC = [C + u'/raw/httpretry/rfc2616.txt', C + u'/raw/httpretry/rfc7231.txt',
       C + u'/raw/httpretry/rfc6585.txt', C + u'/raw/httpretry/rfc8470.txt',
       C + u'/raw/httpretry/rfc9110.txt']
SHW = [u'`' + p[len(C) + 1:] + u'`' for p in SRC]
KIND = [u'99 年 HTTP/1.1 全文', u'14 年消息语义分册', u'12 年状态码增补', u'18 年 early data',
        u'22 年消息语义现行版']
ANS5 = [u'判词是被动式“MUST NOT be automatically retried”，不点施事者的名，且住在幂等定义之外',
        u'把同一条款搬进 §4.2.2 却一个义务词也不给，只给“the request can be”这句机制句',
        u'不答能不能重来，给 429 ⇎ Retry-After: 3600 ⇎ “50 requests per hour”，并自认未定义服务器怎么数请求',
        u'一句给全三档义务：SHOULD retry automatically ⇎ 任何重来 MUST NOT 落在 early data ⇎ 中间人 MAY 自动重来',
        u'§9.2.2 逐字搬 7231 再点名两个施事者（proxy MUST NOT ⇎ client SHOULD NOT），另许 user agent 自动重发 POST']
FRAG = {u'2616': [u'MUST NOT be automatically retried', u'user agents MAY offer'],
        u'7231': [u'Idempotent methods are distinguished because the request can be'],
        u'6585': [u'The 429 status code indicates that the user has sent too many',
                  u'Note that this specification does not define how the origin server'],
        u'8470': [u'user agent SHOULD retry automatically, but any retries MUST NOT be'],
        u'9110': [u'a user agent can repeat a POST request automatically',
                  u'Like the definition of safe, the idempotent property only applies to']}
ENTRY = glob.glob(u'corpus/babeltele/B80_*.md')[0]
FP = json.load(io.open(u'corpus/_b80flat.json', encoding=u'utf-8'))
DER = json.load(io.open(u'corpus/_deriv80.json', encoding=u'utf-8'))
CH = json.load(io.open(u'corpus/_b80checks.json', encoding=u'utf-8'))

AUD = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'], capture_output=True,
                     text=True, encoding=u'utf-8').stdout
VERD = [l for l in AUD.split(u'\n') if l.startswith(u'保真门槛(T1 字面 + T2 推导 + T3 码位):')]
assert len(VERD) == 1, VERD
FAILED = [l.split(u':')[0].strip() for l in AUD.split(u'\n') if re.match(u'^  B\\d+: ', l)]
assert u'B80' not in FAILED, FAILED
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


def V4(v):
    return u'⇎'.join(u'—' if x is None else str(x) for x in v)


def pn(s):
    return u' '.join(s.lower().split())


# ---------- ①② 字节平面面量(第七轨), 逐枚与契约对拍 ----------
BS, CH_, LN, NLC, SPL, TAIL, NB, ML, FFC, EFO, CR, NA, DELTA, BOM, NUL = ([] for _ in range(15))
TS = []
for p in SRC:
    b = io.open(p, u'rb').read()
    t = b.decode(u'utf-8')
    TS.append(t)
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
    NUL.append(b.count(b'\x00'))
    NA.append(len([c for c in t if ord(c) > 127]))
    DELTA.append(len(b) - len(t))
    BOM.append(1 if b[:3] == b'\xef\xbb\xbf' else 0)
for k, v in ((u'bytes', BS), (u'chars', CH_), (u'nonblank', NB), (u'maxlen', ML), (u'ff', FFC),
             (u'ff_exact', EFO), (u'pg_lines', EFO), (u'cr', CR), (u'nul', NUL), (u'nonascii', NA),
             (u'bom', BOM), (u'byte_cp_delta', DELTA), (u'lines_split', SPL), (u'tail_nl', TAIL),
             (u'lines', LN), (u'lines_nl', LN)):
    assert v == gk(k), (k, v, gk(k))
assert gk(u'newlines') == NLC, (gk(u'newlines'), NLC)
for i in range(NSRC):
    assert LN[i] == NLC[i] + 1, (i, LN[i], NLC[i])
    assert SPL[i] == LN[i] - TAIL[i] + FFC[i], (i, SPL[i], LN[i])
assert sum(CR) == 0 and sum(NUL) == 0 and sum(BOM) == gk(u'bom')[4]
# 剥壳行账: 剥掉的 = 空行 + “RFC 编号 …” 紧排抬头行（首页那枚抬头非此式, 不占账）; 9110 无页可剥, 剥的恰全是空行
assert [gk(u'shell_lines')[i] - (LN[i] - NB[i]) - gk(u'hdr_lines_tight')[i]
        for i in range(NSRC)] == [0] * NSRC
assert LN[4] - NB[4] == gk(u'shell_lines')[4]
assert gk(u'txt_n') == NSRC and gk(u'html_n') == 0 and gk(u'all_txt_no_html') == 1
assert gk(u'over72') == [0, 1, 0, 0, 0] and gk(u'one_maxlen_outlier') == 1
assert gk(u'maxlen') == ML and ML[1] == 75

# ---------- ③ 尖括号四把尺: 索引扫描轨(第三套), 实体/注释同法 ----------
SHAPE, OPEN, CLOSE, URL, PSEU, ENT, COM = ([] for _ in range(7))
ABNFN, HTMO, DQ = ([] for _ in range(3))
HEADP, HYPF, CMMA, CLON, HCHD = ([] for _ in range(5))
EX = {}
for t in TS:
    # 枚 `<` 起手的索引扫描, 吃到第一个 `>` 后从其后续扫(与 naive 按 `<` 切段不同: 嵌套 `<` 不再另起一枚)
    toks = []
    i = 0
    while True:
        j = t.find(u'<', i)
        if j < 0:
            break
        k = j + 1
        while k < len(t) and t[k] != u'>' and t[k] != u'\n':
            k += 1
        if k >= len(t) or t[k] != u'>' or k == j + 1:
            i = j + 1
            continue
        toks.append(t[j + 1:k])
        i = k + 1
    o = len([x for x in toks if re.match(u'^[A-Za-z][A-Za-z0-9]*[ >/]', x + u'>')])
    c = len([x for x in toks if x.startswith(u'/')])
    u = len([x for x in toks if x.startswith(u'http')])
    # 开名形里再分两档: ABNF 值占位(<n> <m> <major> <minor> <any …> <base64 …>) ⇎ 真标签名
    ab = len([x for x in toks if x in (u'n', u'm', u'major', u'minor')
              or x.startswith(u'any') or x.startswith(u'base64')])
    ps = [x for x in toks if not re.match(u'^[A-Za-z][A-Za-z0-9]*[ >/]', x + u'>')
          and not x.startswith(u'/') and not x.startswith(u'http')]
    DQ.append(len([x for x in ps if x == u'"']))
    # 余数的成因尺: 词头没有字母(以 `"` ⇎ `=` 起手) ⇎ 词头有字母但名字在首个空格前先撞到一枚标点
    CAUSES = (u'head', u'hyp', u'comma', u'colon')
    CMAP = {u'head': u'head', u'-': u'hyp', u',': u'comma', u':': u'colon'}
    cnt = dict((k2, 0) for k2 in CAUSES)
    for x in ps:
        if not re.match(u'^[A-Za-z]', x):
            cz = u'head'
        else:
            cz = CMAP.get(x[len(re.match(u'^[A-Za-z0-9]*', x).group(0)):][:1], u'?')
        assert cz != u'?', x
        cnt[cz] += 1
        if cz not in EX or len(x) < len(EX[cz][1]):
            EX[cz] = (len(HEADP), x)
    HEADP.append(cnt[u'head'])
    HYPF.append(cnt[u'hyp'])
    CMMA.append(cnt[u'comma'])
    CLON.append(cnt[u'colon'])
    HCHD.append(set([x[:1] for x in ps if not re.match(u'^[A-Za-z]', x)]))
    SHAPE.append(len(toks))
    OPEN.append(o)
    CLOSE.append(c)
    URL.append(u)
    PSEU.append(len(toks) - o - c - u)
    ABNFN.append(ab)
    HTMO.append(o - ab)
    # 实体尺: 逐枚 `&` 手吃后至多 9 枚字符, 看这段是否以 `;` 收尾且中间全为字母数字
    e = 0
    i = 0
    while True:
        j = t.find(u'&', i)
        if j < 0:
            break
        w = t[j + 1:j + 10]
        k = w.find(u';')
        if 0 < k <= 8 and re.match(u'^[A-Za-z#0-9]+$', w[:k]):
            e += 1
        i = j + 1
    ENT.append(e)
    # 注释尺: 逐字符吃 `<!` 后紧跟 `--` 的形状
    cm = 0
    i = 0
    while True:
        j = t.find(u'<', i)
        if j < 0:
            break
        if t[j + 1:j + 4] == u'!--':
            cm += 1
        i = j + 1
    COM.append(cm)
for k, v in ((u'tag_shape', SHAPE), (u'tag_open', OPEN), (u'tag_close', CLOSE), (u'tag_url', URL),
             (u'tag_pseudo', PSEU), (u'ent_total', ENT), (u'comment', COM)):
    assert v == gk(k), (k, v, gk(k))
assert sum(ENT) == 0 and sum(COM) == 0 and gk(u'paren_only_8470') == 1
# 开名形里的两档(本遍新轨, 契约无键): ABNF 值占位 ⇎ 真标签名; 伪法余数再分 `<">` 与带连字符的 ABNF 引用
assert ABNFN == [25, 0, 0, 0, 6] and HTMO == [0, 0, 24, 0, 0]
assert [ABNFN[i] + HTMO[i] for i in range(NSRC)] == OPEN
assert [OPEN[i] + CLOSE[i] + URL[i] + PSEU[i] for i in range(NSRC)] == SHAPE
assert DQ == [10, 0, 0, 0, 0] and [DQ[i] <= PSEU[i] for i in range(NSRC)]
# 余数四档闭合: 词头无字母 ⇎ 撞连字符 ⇎ 撞逗号 ⇎ 撞冒号, 逐份相加恰等于余数
assert HEADP == [12, 0, 0, 0, 1] and HYPF == [7, 13, 0, 0, 14]
assert CMMA == [1, 14, 0, 0, 12] and CLON == [1, 0, 0, 0, 0]
assert [HEADP[i] + HYPF[i] + CMMA[i] + CLON[i] for i in range(NSRC)] == PSEU
# “词头一枚字母也没有”的首字符集合: 2616 全是引号, 9110 只有一枚等号
assert HCHD[0] == set([u'"']) and HCHD[4] == set([u'=']) and [len(x) for x in HCHD] == [1, 0, 0, 0, 1]

# ---------- ④⑤ 锚: 按 ⟦ 分段手吃 ⟨…⟩, 回编码区 ⇎ 回自己那一源 ----------
TT = io.open(ENTRY, encoding=u'utf-8').read()
_m = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', TT, re.S)
ENC = _m.group(1)
FLATENC = ENC.replace(u'\n', u'')
assert len(FLATENC) == gk(u'enc_chars')
cites, parts = [], TT[TT.index(u'⟪BabelTele⟫'):TT.index(u'## ⛓解读注')].split(u'⟦')
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
DIS = set([x[1] for x in cites])
assert len(DIS) == gk(u'anchor_distinct')
PER = dict((t, len([x for x in cites if x[0] == t])) for t in LBL)
assert PER == dict((t, gk(u'tag_' + t)) for t in LBL)
P5 = [pn(t) for t in TS]
IN5 = [len([q for l, q in cites if l == LBL[i] and pn(q) in P5[i]]) for i in range(NSRC)]
assert IN5 == [PER[t] for t in LBL], (IN5, [PER[t] for t in LBL])
# 三分类有两把尺: 门槛用面尺(同一串落在几个源面上), 引用尺(同一串被几个标签引)是另一件东西; 本遍两把都现数
FACEHIT = dict((q, [i for i in range(NSRC) if pn(q) in P5[i]]) for q in DIS)
REFHIT = dict((q, set(l for l, q2 in cites if q2 == q)) for q in DIS)
CLS1 = len([q for q in DIS if len(FACEHIT[q]) == 1])
CLSN = len([q for q in DIS if 1 < len(FACEHIT[q]) < NSRC])
CLS5 = len([q for q in DIS if len(FACEHIT[q]) == NSRC])
assert (CLS1, CLSN, CLS5) == (gk(u'anchor_single'), gk(u'anchor_cross'), gk(u'anchor_all5'))
assert CLS5 == 0
REF1 = len([q for q in DIS if len(REFHIT[q]) == 1])
REFN = len([q for q in DIS if 1 < len(REFHIT[q]) < NSRC])
assert all(len(FACEHIT[q]) >= len(REFHIT[q]) for q in DIS)
assert CLS1 + CLSN == gk(u'anchor_distinct')
CROSS_UNREF = len([q for q in DIS if len(FACEHIT[q]) > 1 and len(REFHIT[q]) == 1])
assert REF1 - CLS1 == CROSS_UNREF
assert REFN + CROSS_UNREF == CLSN
assert gk(u'checks') == gk(u'anchor_distinct') * NSRC and gk(u'anchor_err') == 0
for lab, frs in FRAG.items():
    for f in frs:
        assert pn(f) in P5[LBL.index(lab)], (lab, f)
# 行文里点名的每一枚尖括号片段都要在它那一源的归一面上命中
for f in (u'<n>', u'<m>', u'<major>', u'<minor>', u'<">'):
    assert pn(f) in P5[LBL.index(u'2616')], f
assert pn(u'<n>') in P5[LBL.index(u'9110')] and pn(u'<m>') in P5[LBL.index(u'9110')]
assert pn(u'<=>') in P5[LBL.index(u'9110')]
assert set(EX) == set((u'head', u'hyp', u'comma', u'colon'))
for cz2, (di2, tx2) in EX.items():
    assert pn(u'<' + tx2 + u'>') in P5[di2], (cz2, tx2)
EXSTR = u' ⇎ '.join(u'`<' + EX[cz2][1] + u'>`（' + LBL[EX[cz2][0]] + u'）'
                    for cz2 in (u'hyp', u'comma', u'colon'))
# ---------- 转化指标: 逐条现数, 列内并集 ----------
GROW, ALLR = [], None
for l in AUD.split(u'\n'):
    if l.startswith(u'| B') and l.count(u'|') >= 10:
        GROW.append([x.strip() for x in l.split(u'|')[1:-1]])
    elif l.startswith(u'| ALL |'):
        ALLR = [x.strip() for x in l.split(u'|')[1:-1]]
assert ALLR
ROWS = dict((c[0], c) for c in GROW)
SL = S.split(NL)
hh = [i for i, l in enumerate(SL) if l.startswith(u'| entry | 编码字符 |')]
assert len(hh) == 1
tt0 = [i for i in range(hh[0], len(SL)) if SL[i].startswith(u'| **合计（')]
assert len(tt0) == 1
LISTED0 = [l.split(u'|')[1].strip() for l in SL[hh[0] + 2:tt0[0]]]
assert all(x.startswith(u'B') for x in LISTED0)
assert u'B80' not in LISTED0 and S.count(u'| B80 |') == 0 and S.count(u'**B80 问的是') == 0
LISTED = sorted(LISTED0 + [u'B80'], key=lambda k: int(k[1:]))
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
E80, D80 = num(ROWS[u'B80'][2]), num(ROWS[u'B80'][1])
assert E80 == gk(u'enc_chars'), (E80, gk(u'enc_chars'))
assert ROWS[u'B80'][3] == u'%.1f%%' % (100.0 * E80 / D80), (ROWS[u'B80'][3], E80, D80)
assert ROWS[u'B80'][4] == u'%.3f%%' % (100.0 * E80 / sum(BS)), ROWS[u'B80'][4]
PROOFS = num(AUD.split(u'已机检的推导(')[1].split(u' 条)')[0])
CLOSEK = len([k for k in FP if u'close' in k])
DKEYS = len(set(re.findall(u"B80V\\('([a-z0-9_]+)'", json.dumps(DER, ensure_ascii=False))) & set(FP))
VFORM = len(CH[u'zid'])

# 行尺两档各自归到同一个总数: 原始行枚数档 ⇎ 折叠键数档
assert gk(u'pair_max_byte_lines') + gk(u'pair_max_norm_only_lines') == gk(u'pair_max')
assert gk(u'pair_max_byte_keys') + gk(u'axis_total') == gk(u'pair_max')
assert gk(u'pair_max_byte_lines') - gk(u'pair_max_byte_keys') == gk(u'pair_byte_unit_gap')
assert gk(u'code_7231_drops') == [u'401', u'416'] and gk(u'code_def_fams') == [11, 9, 4, 0, 11]

# ---------- 门槛表 B80 行 ----------
HEADROW = (u'| B80 | ' + fmt(E80) + u'（新建, 失败的 HTTP 请求到底能不能由程序自己重发 交五份 HTTP 一手文书各答一遍 '
           + str(gk(u'anchor_total')) + u' 处标注／' + str(gk(u'anchor_distinct')) + u' 个不同串（登记全命中, 单源 '
           + str(gk(u'anchor_single')) + u' ⇎ 穿二至四源 ' + str(gk(u'anchor_cross')) + u' ⇎ 五源全现 '
           + str(gk(u'anchor_all5')) + u'——一枚答话不可能五份同源, 因为 2616/6585/8470/9110 与 7231 是同一问题的不同版次文本, '
             u'限流码那一份通篇不谈幂等; 编码区 ' + fmt(E80) + u' 字符, 归属检查 ' + str(gk(u'checks')) + u' 次, 错配 '
           + str(gk(u'anchor_err')) + u'）: 五色锚位 ' + u' ⇎ '.join(x + u' ⟦' + y + u'⟧' for x, y in zip(LBL, LBL))
           + u'（' + u' ⇎ '.join(str(PER[t]) for t in LBL) + u' 处）; 四档口径（原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 节窗折平, '
             u'后两份无幂等节故节窗档登记 -1 而非 0）读到 ' + V4(gk(u'sn_strict_docs')) + u' ／ ' + V4(gk(u'sn_fold_docs'))
           + u' ／ ' + V4(gk(u'sn_sh_docs')) + u' ／ ' + V4(gk(u'sn_sec_docs_scope')) + u' 枚（在册针 ' + str(gk(u'needle_n'))
           + u' 枚, 归各份 ' + V4(gk(u'needles_owned')) + u' 枚, 折行一次救回 ' + str(gk(u'fold_minus_strict_n'))
           + u' 枚（逐份 ' + V4(gk(u'fold_minus_strict_own')) + u'）, 摘壳比折平新读 ' + str(sum(gk(u'sh_gains')))
           + u' 枚而一粒不丢（丢 ' + str(sum(gk(u'sh_loses'))) + u' 枚, 新读那枚是 6585 的 428 定义行被跨页页壳切开, 逐份 '
           + V4(gk(u'sh_gains')) + u'）, 节窗档比摘壳档少 ' + str(gk(u'sh_no_sec_n')) + u' 枚（逐份 ' + V4(gk(u'sh_no_sec_own'))
           + u'——2616 的三枚判词全在 §9.1.2 之外）, 阶梯单调位（取 1 为平）' + str(gk(u'ladder_monotone'))
           + u' ⇎ 四档账差位（取 0 为平）' + str(gk(u'ladder_close')) + u' ⇎ 四档全读不到的死针 ' + str(len(gk(u'dead_needles'))) + u' 枚 ⇎ 反向对照 '
           + str(gk(u'neg_n')) + u' 枚合计命中 ' + str(gk(u'neg_hit_widest')) + u' 枚（最宽档也零, 判定 '
           + str(gk(u'neg_all_cold')) + u'）; 语气五轨（MUST NOT ⇎ MUST ⇎ SHOULD NOT ⇎ SHOULD ⇎ MAY）最宽档合计 '
           + V4(gk(u'tone_tot')) + u' ⇎ 折平 ' + V4(gk(u'tone_fold_tot')) + u' ⇎ 纯 MUST ' + V4(gk(u'tone_must_pure'))
           + u' ⇎ 大小写差 ' + V4(gk(u'tone_case_gap')) + u' ⇎ 小写四词族 ' + V4(gk(u'tone_word_lc_tot'))
           + u'——alpha ⇎ alnum 两把边界尺逐份同值（差 ' + V4(gk(u'tone_alnum_gap')) + u' ⇎ 该账闭合位取 0 为平, 现值 '
           + str(gk(u'tone_wide_close')) + u'），被 72 列硬换行切开的大写义务词 ' + V4(gk(u'tone_straddle'))
           + u' 枚（9110 的 ' + str(gk(u'tone_straddle')[4]) + u' 枚分在 MUST NOT ⇎ SHOULD NOT 两式, 新版式去掉页壳反而切掉更多）; '
             u'节内义务词 ' + V4(gk(u'tone_sec_tot')) + u'——7231 节内零枚而 2616 节内仅 ' + str(gk(u'tone_sec_tot')[0])
           + u' 枚（判定 ' + str(gk(u'tone_zero_7231_sec')) + u' ⇎ 定义句在节内 ' + str(gk(u'defin_in_sec'))
           + u'），2616 的判词距节头 ' + str(gk(u'verdict_head_gap')) + u' 行且与指向 §9.1.2 的交叉引用同行（'
           + str(gk(u'xref_line')) + u' 行全库同条款引用, 判定 ' + str(gk(u'verdict_xref_same_line')) + u'）; '
           u'automat×retry 六式 ' + V4(gk(u'auto_tot_fold')) + u' ⇎ 裸 automat* ' + V4(gk(u'auto_bare'))
           + u'（差 ' + V4(gk(u'auto_bare_minus_union')) + u' 枚是“不在 retry 邻座”的 automatic/automatically, 故“自动化”词量不能替“自动重来”作证）'
             u'⇎ 重来八式 ' + V4(gk(u'reword_tot')) + u' ⇎ 去重 ' + V4(gk(u'reword_union')) + u' ⇎ 零枚族数 '
           + V4(gk(u'reword_zero_n')) + u'——6585 六式零枚（判定 ' + str(gk(u'no_auto_vocab_6585')) + u'）⇎ 九式施事者命中 '
           + V4(gk(u'subj_n')) + u' ⇎ 点名主动句 ' + V4(gk(u'subj_active')) + u' ⇎ 不点名被动句 ' + V4(gk(u'subj_passive'))
           + u'（全库恰一枚, 判定 ' + str(gk(u'subj_only_passive_2616')) + u'）⇎ 泛称七式 ' + V4(gk(u'act_tot'))
           + u' 枚; 数字七式总量 ' + V4(gk(u'num_tot')) + u', 换代净账 delay−delta ' + V4(gk(u'num_rename'))
           + u'（2616 只写 delta-seconds ' + str(gk(u'num_dsec_docs')[0]) + u' 枚 ⇎ 7231 与 9110 各只写 delay-seconds '
           + str(gk(u'num_delay_docs')[4]) + u' 枚, 判定 ' + str(gk(u'rename_delta_vs_delay')) + u'）, Retry-After 行 '
           + V4(gk(u'ra_count')) + u' 行（8470 通篇不提, 判定 ' + str(gk(u'no_retry_after_8470')) + u'）; '
           u'状态码定义行 ' + V4(gk(u'code_defined_n')) + u' 行 ⇎ 族数 ' + V4(gk(u'code_def_fams'))
           + u'——7231 比 2616 少 ' + str(gk(u'code_7231_drops_n')) + u' 族（' + u' '.join(gk(u'code_7231_drops'))
           + u' 搬走）⇎ 9110 的定义集与 2616 逐枚同（判定 ' + str(gk(u'code_set_2616_eq_9110')) + u'）但 428/429 两份都不定义'
             u'（判定 ' + str(gk(u'neither_428_429_in_2616')) + u' ⇎ ' + str(gk(u'neither_428_429_in_9110'))
           + u'）⇎ 8470 零定义（判定 ' + str(gk(u'no_code_def_8470')) + u'）只用“码+括号名”印法（全库唯一, '
           + str(sum(gk(u'paren')[3])) + u' 枚，且三式之中只印 425 一式（逐式 ' + V4(gk(u'paren')[3])
           + u'）⇎ 五份逐份 ' + V4([sum(x) for x in gk(u'paren')]) + u'（只有 8470 那份非零）, 其中 '
           + str(gk(u'paren_straddle')[3]) + u' 枚被换行切在中间）; '
           u'搬字两把尺: 行尺池 ' + fmt(gk(u'pool_n')) + u' 行 ⇎ 并集 ' + fmt(gk(u'pool_union')) + u' 分档 '
           + V4(gk(u'pool_tier')) + u'（容斥 ' + V4(gk(u'pool_incl')) + u' 归到并集, 归并账差取 0 为平, 现值 '
           + str(gk(u'union_close'))
           + u'）⇎ 最大一对 ' + gk(u'pair_max_lbl') + u' ' + str(gk(u'pair_max')) + u' 条, 其中逐字节同 '
           + str(gk(u'pair_max_byte_keys')) + u' ⇎ 只因归一同 ' + str(gk(u'pair_max_norm_only_keys'))
           + u'（写法分家四桶 ' + gk(u'axis_str') + u', 非空桶 ' + str(gk(u'axis_str_n'))
           + u' 个, 桶账差取 0 为平, 现值 '
           + str(gk(u'axis_close')) + u'）, 同一对换成原始行尺: 逐字节同的那部分占 '
           + str(gk(u'pair_max_byte_lines')) + u' 行 ⇎ ' + str(gk(u'pair_max_byte_keys'))
           + u' 枚键（差 ' + str(gk(u'pair_byte_unit_gap'))
           + u' 行, 因同一枚键在两处各印一次）, 加上只归一同的 ' + str(gk(u'pair_max_norm_only_lines'))
           + u' 行 ⇎ ' + str(gk(u'axis_total')) + u' 枚, 两档各自归到 ' + str(gk(u'pair_max')) + u' 条; 换成句尺池 '
           + fmt(gk(u's_pool_n')) + u' 句 ⇎ 最大一对 ' + str(gk(u's_pair_max')) + u' 句, 净差 '
           + str(gk(u's_ruler_drop_7231_9110')) + u' 枚（每句摊成 ' + str(gk(u'pair_row_per_sent'))
           + u' 行, 取 1172÷347 的整除位, 与上句同行尺同两对, 不是矛盾）; 两段搬字逐字同形: 幂等定义段共头 ⇎ 共尾各 ' + str(gk(u'pre_idem_7231_9110'))
           + u' ⇎ ' + str(gk(u'suf_idem_7231_9110')) + u' 词 ⇎ 只属一份 ' + str(gk(u'w_only_7231_idem')) + u' ⇎ '
           + str(gk(u'w_only_9110_idem')) + u' 词, 类比句段 ' + str(gk(u'pre_like_7231_9110')) + u' ⇎ '
           + str(gk(u'suf_like_7231_9110')) + u' 词, 两段在原文件的行距位移 ' + str(gk(u'idem_shift')) + u' ⇎ '
           + str(gk(u'like_shift')) + u' 行相等（差 ' + str(gk(u'blk_gap_delta')) + u'）; '
           u'主答段 14 段共 ' + str(gk(u'blk_rows_tot')) + u' 行 ⇎ ' + fmt(gk(u'blk_words_tot')) + u' 词, 五段答句 '
           + str(gk(u'blk_five_rows')) + u' 行 ⇎ ' + str(gk(u'blk_five_words')) + u' 词, 逐份跨行 '
           + V4(gk(u'ans_span')) + u' 行（合计 ' + str(gk(u'ans_span_tot')) + u'）⇎ 9110 那句 '
           + str(gk(u'ans_words')[4]) + u' 词独占 ' + str(gk(u'ans_span')[4]) + u' 行, 是全库唯一一行读全的答句（判定 '
           + str(gk(u'one_line_answer_only_9110')) + u'）, 答句从不被页壳切开（' + V4(gk(u'ans_page_break'))
           + u', 判定 ' + str(gk(u'no_page_break_in_answer')) + u'）, 行针复核 ' + str(gk(u'pin_rt_ok')) + u'／'
           + str(gk(u'pin_rt_n')) + u' 枚拿行号回原文件自验命中 ⇎ 错行反向 ' + str(gk(u'pin_wrongline')) + u' 枚; '
           u'版式三本账: 换页符 ' + V4(gk(u'ff')) + u' 枚全部独占整行 ⇎ [Page] 页码行 ' + V4(gk(u'pg_lines'))
           + u' 枚（两账逐份差 ' + V4(gk(u'ff_minus_pg')) + u'）⇎ 剥壳谓词剥掉 ' + V4(gk(u'shell_lines'))
           + u' 行, 逐份恰等于本遍现数的空行数加紧排抬头行数（被剥的非空行在枚数上全是 “RFC 编号 …” 紧排抬头那一式, '
           + u'首页那枚抬头不是此式故不占账; 五份账差 ' + V4([gk(u'shell_lines')[i] - (LN[i] - NB[i]) - gk(u'hdr_lines_tight')[i]
                                for i in range(NSRC)])
           + u'）⇎ 9110 无页壳（判定 ' + str(gk(u'pageless_9110_only')) + u': 它被剥的 '
           + fmt(gk(u'shell_lines')[4]) + u' 行恰等于它的空行数 ' + fmt(LN[4] - NB[4])
           + u', 剥掉的只是空行, 故摘壳面与折平面等长, 判定 '
           + str(gk(u'sh_equals_fold_for_9110')) + u'）, 采集壳谓词与建条目壳谓词逐份相平（本遍多判 '
           + str(sum(gk(u'shell_mk_only'))) + u' ⇎ 采集多判 ' + str(sum(gk(u'shell_pick_only')))
           + u' ⇎ 五份绝对差合计取 0 为平, 现值 '
           + str(gk(u'shell_ledger_close')) + u'）; 抬头年 ' + V4(gk(u'years')) + u' 跨 ' + str(gk(u'year_span'))
           + u' 年 ⇎ 逆序 ' + str(gk(u'year_inversions')) + u' 处（列表序 14 年在 12 年之后）, Obsoletes '
           + str(gk(u'obs_total')) + u' 号 ⇎ Updates ' + str(gk(u'upd_total')) + u' 处 ⇎ 谱系无出边的恰一份（第 '
           + str(gk(u'lineage_no_edge')[0] + 1) + u' 份=8470, 它既不停止也不更新任何号, 只新定义 425）⇎ 被 Updates 指向的那份恰也被别份 Obsoletes'
           + u'（6585 更新 2616 ⇎ 2616 又被 7231 废止, 判定 ' + str(sum(gk(u'upd_target_obsoleted'))) + u'）; '
           + u'目录行 ⇎ 缩进 ⇎ 紧排三档 ' + V4(gk(u'hdr_lines_tight'))
           + u' ⇎ ' + V4(gk(u'hdr_lines_indent')) + u' ⇎ 两点 ' + V4(gk(u'hdr_dot2sp')) + u' 枚, 同名幂等标题在 9110 面上命中 '
           + str(gk(u'sec_hit_n')[4]) + u' 行（正文第 ' + str(gk(u'sec_head_line_9110')) + u' 行 ⇎ 目录第 '
           + str(gk(u'sec_toc_line')[4]) + u' 行, 全库合计 ' + str(gk(u'sec_hit_tot')) + u' 行）; '
           u'扁平契约 ' + str(len(FP)) + u' 枚键（键数自证 ' + str(gk(u'contract_n')) + u'=' + str(len(FP) - 1)
           + u'+1）⇎ 布尔门 ' + str(gk(u'bool_clos_n')) + u' 道全绿 ' + str(gk(u'bool_clos_sum')) + u' ⇎ 标量恒等式 '
           + str(gk(u'scalar_clos_n')) + u' 条通过 ' + str(gk(u'scalar_clos_sum')) + u' ⇎ 含 close 的键 ' + str(CLOSEK)
           + u' 枚其中逐份清单 ' + str(gk(u'list_clos_n')) + u' 枚 ⇎ DERIV ' + str(len(DER)) + u' 枚算式 ⇎ `checks` 里 V 形恒等式 '
           + str(VFORM) + u' 条; 采集侧同定义标量 ' + str(gk(u'pick_agree')) + u'/' + str(gk(u'pick_agree'))
           + u' 枚相符 ⇎ ' + str(gk(u'pick_diff')) + u' 枚不符; 工具侧 atomcheck 的 SRC 表未登记本条, 五份面的逐字性由门槛侧 '
           + str(gk(u'checks')) + u' 次归属检查承担（逐字命中 ' + str(gk(u'anchor_total')) + u' 处 ⇎ 错配 '
           + str(gk(u'anchor_err')) + u'） |')
assert HEADROW.count(u'|') == 3 and HEADROW.count(u'`') % 2 == 0

# ---------- 语料表 B80 行 ----------
C80 = (u'| B80 | ' + u' ⇎ '.join(
    SHW[i] + u'（' + YR[i] + u' ⟦' + LBL[i] + u'⟧：' + fmt(BS[i]) + u' 字节／面内码位 ' + fmt(CH_[i])
    + u'／行数 ' + fmt(LN[i]) + u'／非空行 ' + fmt(NB[i])
    + u'／换页符 ' + str(FFC[i]) + u' 枚（独占整行 ' + str(EFO[i]) + u' 行, 剥壳行 ' + fmt(gk(u'shell_lines')[i])
    + u' 行' + (u', 恰等于空行数' if i == 4 else u'') + u'）／最长行 ' + str(ML[i]) + u' 列／尖括号形 ' + str(SHAPE[i]) + u' 枚（开名 ' + str(OPEN[i])
    + u' ⇎ 闭名 ' + str(CLOSE[i]) + u' ⇎ 裸 URL ' + str(URL[i]) + u' ⇎ 伪法余数 ' + str(PSEU[i])
    + u', 实体 0 ⇎ 注释 0）／答句 ' + ANS5[i] + u'／回车 0／非 ASCII ' + str(NA[i]) + u'／BOM ' + str(BOM[i]) + u'）'
    for i in range(NSRC))
    + u' | 五份答同一个问题 ⇒ 答的是五种东西: 禁令的位置(2616, 判词距 §9.1.2 节头 '
      + str(gk(u'verdict_head_gap')) + u' 行且是被动式, 节内义务词 ' + str(gk(u'tone_sec_tot')[0])
      + u' 枚) ⇎ 机制句(7231, 搬进 §4.2.2, 节内义务词 ' + str(gk(u'tone_sec_tot')[1])
      + u' 枚) ⇎ 一个码加一个头(6585, automat×retry 六式 ' + str(gk(u'auto_tot_fold')[2])
      + u' 枚 ⇎ idempotent 一词 ' + str(gk(u'idem_str')[2]) + u' 枚, 自认未定义服务器怎么数请求) ⇎ 三档义务同句(8470, '
      + u'SHOULD ⇎ MUST NOT ⇎ MAY) ⇎ 点名两施事者(9110, 名下 ' + str(gk(u'k9110_tot'))
      + u' 枚内容针全在 §9.2.2 之内（名下另有 ' + str(gk(u'neg_own_nd')[4])
      + u' 枚反向对照针, 四档全零）, 节外 ' + str(gk(u'k9110_no_sec')) + u' 枚); “能不能自动重发 POST”只有 9110 明许, '
      + u'而“重来不许落在 early data”只有 8470 提——它还是全库唯一用“码+括号名”印法的一份（'
      + str(gk(u'paren')[3][0]) + u' 枚, 全部是 425 一式, '
      + u'其余两份增补码它一个也不印） |')
assert C80.count(u'|') == 4 and C80.count(u'`') % 2 == 0

# ---------- 判词段 ----------
PARA = (u'**B80 问的是失败的 HTTP 请求到底能不能由程序自己重发，五份一手文书给出五种答法**：'
        + u' ⇎ '.join(SHW[i] + u'（' + YR[i] + u' ⟦' + LBL[i] + u'⟧：' + fmt(BS[i]) + u' 字节／行数 ' + fmt(LN[i])
                      + u'／非空行 ' + fmt(NB[i]) + u'／最长行 ' + str(ML[i]) + u' 列／换页符 ' + str(FFC[i])
                      + u' 枚／答句 ' + ANS5[i] + u'／非 ASCII ' + str(NA[i]) + u'／BOM ' + str(BOM[i]) + u'）'
                      for i in range(NSRC))
        + u'——四份同为 72 列硬换行面且换页符独占整行, 唯 7231 有 ' + str(ML[1]) + u' 列的超长行（超 72 列的行逐份 '
        + V4(gk(u'over72')) + u' 行）, 9110 是新版式：零页壳（换页符 ' + str(FFC[4]) + u' 枚 ⇎ 页码行 '
        + str(gk(u'pg_lines')[4]) + u' 枚 ⇎ 判定 ' + str(gk(u'pageless_9110_only'))
        + u'）, 它被剥壳谓词吃掉的 ' + fmt(gk(u'shell_lines')[4]) + u' 行恰等于本遍现数的空行数 '
        + fmt(LN[4] - NB[4]) + u'——新版式无页可剥, 剥掉的只是空行, 所以摘壳面与折平面等长（差 '
        + str(gk(u'sh_char_gap')[4]) + u' 字符, 判定 ' + str(gk(u'sh_equals_fold_for_9110')) + u'）; 全库回车 ⇎ NUL 各 '
        + V4(gk(u'cr')) + u' ⇎ ' + V4(gk(u'nul'))
        + u' 枚 ⇎ BOM ' + V4(gk(u'bom')) + u' 枚, 非 ASCII ' + V4(gk(u'nonascii')) + u' 枚全部落在 9110 的贡献者姓名行, '
          u'字节−码位差因此 ' + V4(gk(u'byte_cp_delta')) + u'（其余四份恒零）; 五份全是 .txt, 所以门槛对面只有一把尺（原样字节）, '
          u'尖括号形 ' + V4(SHAPE) + u' 枚分四把尺（开名 ' + V4(OPEN) + u' ⇎ 闭名 ' + V4(CLOSE) + u' ⇎ 裸 URL ' + V4(URL)
          + u' ⇎ 伪法余数 ' + V4(PSEU) + u', 逐份四档相加恰等于形数）; 开名形里只有 6585 的 ' + str(HTMO[2])
          + u' 枚是真标签名（配 ' + str(CLOSE[2]) + u' 枚闭名, 它的余数为 ' + str(PSEU[2]) + u'——它真带了一页示例 HTML）, '
          u'而 2616 的 ' + str(ABNFN[0]) + u' 枚 ⇎ 9110 的 ' + str(ABNFN[4]) + u' 枚开名全是 ABNF 值占位'
          u'（`<n>` ⇎ `<m>` ⇎ `<major>` ⇎ `<minor>` ⇎ `<any …>` ⇎ `<base64 …>`）; '
          u'余数非零的三份（2616 ⇎ 7231 ⇎ 9110）按成因分四档, 逐份相加恰等于余数: 词头一枚字母也没有的 ' + V4(HEADP)
          + u' 枚（2616 的 12 枚全以引号起手——恰好 `<">` ' + str(DQ[0]) + u' 枚, 另两枚是引号带连接词的形式; 9110 的 1 枚是 `<=>`）'
          + u' ⇎ 词头有字母但名字在首个空格前先撞到一枚标点的（撞连字符 ' + V4(HYPF) + u' 枚 ⇎ 撞逗号 ' + V4(CMMA)
          + u' 枚 ⇎ 撞冒号 ' + V4(CLON) + u' 枚）, 开名尺 `^[A-Za-z][A-Za-z0-9]*[ >/]` 就断在这枚标点上, 三档各取全库最短的一枚 '
          + EXSTR + u'; 一把 naive 剥壳会把这三份的余数连同 2616/9110 的 ABNF 值占位一起当标签吃掉; 全库零实体零注释。'
        + u' 五种答法不是措辞差异而是答的东西不同: 2616 给了禁令却不写在定义节里——§9.1.2 只给定义（节内义务词 '
          + str(gk(u'tone_sec_tot')[0]) + u' 枚 ⇎ 摘壳面 ' + str(gk(u'v_in_sh')) + u' 枚判词全在节外, 判定 '
          + str(gk(u'v2616_outside_own_sec')) + u'）, 判词距节头 ' + str(gk(u'verdict_head_gap')) + u' 行且与“see section 9.1.2”'
          + u'同一行（全库同条款交叉引用 ' + str(gk(u'xref_line')) + u' 行, 判定 ' + str(gk(u'verdict_xref_same_line'))
          + u'）, 用的还是全库唯一一枚不点施事者名的被动式（点名主动句 ' + V4(gk(u'subj_active')) + u' ⇎ 被动句 '
          + V4(gk(u'subj_passive')) + u'）⇎ 7231 把同一条款搬进 §4.2.2, 窗幅从 ' + str(gk(u'sec_chars')[0]) + u' 字符扩到 '
          + str(gk(u'sec_chars')[1]) + u' ⇎ 句数 ' + str(gk(u'sec_sents')[0]) + u' ⇎ ' + str(gk(u'sec_sents')[1])
          + u', 却一个义务词也不给, 给的是机制句（“请求能在读到响应前失败”）⇎ 9110 反向收成一处：名下 '
          + str(gk(u'k9110_tot')) + u' 枚内容针全在 §9.2.2 之内（节外 ' + str(gk(u'k9110_no_sec')) + u' 枚, 判定 '
          + str(gk(u'k9110_inside_sec')) + u'）, 两份禁令点名 proxy 与 client, 节窗最厚（' + str(gk(u'sec_chars')[4])
          + u' 字符 ⇎ ' + str(gk(u'sec_words')[4]) + u' 词 ⇎ ' + str(gk(u'sec_sents')[4]) + u' 句 ⇎ 占摘壳面千分比 '
          + str(gk(u'sec_share_permille')[4]) + u', 前两份 ' + str(gk(u'sec_share_permille')[0]) + u' ⇎ '
          + str(gk(u'sec_share_permille')[1]) + u'）⇎ 中间两份干脆换题: 6585 的 automat×retry 六式 '
          + str(gk(u'auto_tot_fold')[2]) + u' 枚 ⇎ idempotent ' + str(gk(u'idem_str')[2]) + u' 枚, 只给 429 ⇎ Retry-After: 3600 '
          + u'⇎ “50 requests per hour”, 并自认没定义源服务器怎么数请求 ⇎ 8470 一句给全三档义务（SHOULD ⇎ MUST NOT ⇎ MAY）, '
          + u'Retry-After 行 ' + str(gk(u'ra_count')[3]) + u' 行（它压根不提该头, 判定 ' + str(gk(u'no_retry_after_8470'))
          + u'）, 但把重来限制在 early data 之外。'
        + u' 单位与码表换代可由在库字节数出来: delta-seconds ' + str(gk(u'num_dsec_docs')[0]) + u' 枚只在 2616, '
          u'delay-seconds ' + str(gk(u'num_delay_docs')[1]) + u' ⇎ ' + str(gk(u'num_delay_docs')[4]) + u' 枚在 7231 ⇎ 9110, '
          u'净账 ' + V4(gk(u'num_rename')) + u'; 定义行 ' + V4(gk(u'code_defined_n')) + u' 行 ⇎ 族数 '
          + V4(gk(u'code_def_fams')) + u'——7231 比 2616 少 ' + str(gk(u'code_7231_drops_n')) + u' 族（'
          + u' '.join(gk(u'code_7231_drops')) + u'）⇎ 9110 回到 2616 的同一枚集（判定 '
          + str(gk(u'code_set_2616_eq_9110')) + u'）, 而 428 与 429 在 9110 ⇎ 2616 里都不定义（判定 '
          + str(gk(u'neither_428_429_in_9110')) + u' ⇎ ' + str(gk(u'neither_428_429_in_2616')) + u'）, 限流那一码住在本库之外的 6585。'
        + u' 谁抄谁可量: 行尺最大一对 ' + gk(u'pair_max_lbl') + u' ' + str(gk(u'pair_max')) + u' 条（逐字节同 '
          + str(gk(u'pair_max_byte_keys')) + u' ⇎ 只因归一同 ' + str(gk(u'pair_max_norm_only_keys'))
          + u' 条, 四桶 ' + gk(u'axis_str') + u'）, 其中 ' + str(gk(u'only2_7231_9110')) + u' 条只属这一对（搬家的正文）, '
          + u'换成句尺同对只剩 ' + str(gk(u's_pair_max')) + u' 句（净差 ' + str(gk(u's_ruler_drop_7231_9110'))
          + u' 枚, 每句摊成 ' + str(gk(u'pair_row_per_sent')) + u' 行——取 1172÷347 的整除位）; 幂等定义段 ⇎ 类比句段两段都逐字同形, 共头共尾各 '
          + str(gk(u'pre_idem_7231_9110')) + u' ⇎ ' + str(gk(u'pre_like_7231_9110')) + u' 词, 行距位移同为 '
          + str(gk(u'idem_shift')) + u' ⇎ ' + str(gk(u'like_shift')) + u' 行（差 ' + str(gk(u'blk_gap_delta'))
          + u', 故是整段平移）; 反过来 7231 那句类比句在 2616 的摘壳面上 ' + str(gk(u'like_absent_2616'))
          + u' 枚 ⇎ 2616 的定义句在 7231 的折平面上 ' + str(gk(u'defin_absent_7231')) + u' 枚——换代换了措辞, 不是漏印。'
        + u' 版式会吃掉答案: 在册 ' + str(gk(u'needle_n')) + u' 枚针里只有 ' + str(sum(gk(u'sn_strict_docs')))
          + u' 枚能在单行读全（逐份 ' + V4(gk(u'sn_strict_docs')) + u'）, ' + str(gk(u'fold_minus_strict_n'))
          + u' 枚靠折行救回, 摘壳再救 ' + str(sum(gk(u'sh_gains'))) + u' 枚（全库唯一一枚: 6585 的 428 定义行被跨页页壳切开）'
          + u' ⇎ 节窗档比摘壳档少 ' + str(gk(u'sh_no_sec_n')) + u' 枚; 切开答句的是换行而不是分页（逐份 '
          + V4(gk(u'ans_page_break')) + u' 枚）, 而被 72 列切开的大写义务词 ' + V4(gk(u'tone_straddle'))
          + u' 枚里 9110 占 ' + str(gk(u'tone_straddle')[4]) + u' 枚——去掉页壳的反而是新版式。'
          u'答句本身五段共 ' + str(gk(u'blk_five_rows')) + u' 行 ⇎ ' + str(gk(u'blk_five_words')) + u' 词, 只有 9110 那句 '
          + str(gk(u'ans_words')[4]) + u' 词能一行读全（判定 ' + str(gk(u'one_line_answer_only_9110')) + u'）。门槛侧 '
          + str(len(DER)) + u' 枚 DERIV 算式 ⇎ ' + str(VFORM) + u' 条 V 形恒等式（标量 ' + str(gk(u'scalar_clos_n'))
          + u' 项通过 ' + str(gk(u'scalar_clos_sum')) + u' ⇎ 布尔门 ' + str(gk(u'bool_clos_sum')) + u'／'
          + str(gk(u'bool_clos_n')) + u'）, 扁平契约 ' + str(len(FP)) + u' 枚键由建条目 ⇎ 解读注 ⇎ 本遍三套实现逐枚复测'
            u'（采集侧同定义标量 ' + str(gk(u'pick_agree')) + u'/' + str(gk(u'pick_agree')) + u' 枚相符 ⇎ 逐值不符 '
            + str(gk(u'pick_diff')) + u' ⇎ 本遍独有 0）; 其中 ' + str(DKEYS) + u' 枚进得了 DERIV 算式 ⇎ 余下 '
            + str(len(FP) - DKEYS) + u' 枚是形状清单、字符串表与段窗切片。')
for _s in (PARA,):
    assert _s.count(u'|') == 0 and _s.count(u'`') % 2 == 0

# ---------- 落盘: 定点插入, 不整体重写 ----------
def after(s, needle, text):
    i = s.find(needle)
    assert i >= 0 and s.find(needle, i + 1) < 0, (u'定位失败', needle[:60])
    j = s.find(NL, i)
    return s[:j + 1] + text + s[j + 1:]


def after_row(s, eid, needle, text):
    hits = [l for l in s.split(NL) if l.startswith(u'| ' + eid + u' | ') and needle in l]
    assert len(hits) == 1, (eid, needle, len(hits))
    return after(s, hits[0], text)


def subn(pat, mk, s, n=1):
    ms = list(re.finditer(pat, s))
    assert len(ms) == n, (pat, len(ms))
    m = ms[0]
    return s[:m.start()] + mk(m) + s[m.end():]


S2 = after(S, u'**B74 问的是投递失败的邮件到底多久再试一次', PARA + NL + NL)
S2 = after_row(S2, u'B74', u'（新建,', HEADROW + NL)
S2 = after_row(S2, u'B74', u'`raw/mailRetry/rfc821.txt`', C80 + NL)

L2 = S2.split(NL)
h2 = [i for i, l in enumerate(L2) if l.startswith(u'| entry | 编码字符 |')]
assert len(h2) == 1
t2 = [i for i in range(h2[0], len(L2)) if L2[i].startswith(u'| **合计（')]
assert len(t2) == 1
T0 = t2[0]
present = [l.split(u'|')[1].strip() for l in L2[h2[0] + 2:T0]]
assert present == LISTED0, present[:3]
L2[T0:T0] = [(u'| B80 | %s | %s | %s（字节口径; 本行为 audit 直出, 未再附逐条口径注） | %s | %s |'
              % (fmt(E80), ROWS[u'B80'][3], ROWS[u'B80'][4], ROWS[u'B80'][5], ROWS[u'B80'][7]))]
HC = len(L2[h2[0]].split(u'|'))
cells = L2[T0 + 1].split(u'|')
assert len(cells) == HC, (len(cells), HC)
UN = sorted(set(c[0] for c in UNACC), key=lambda k: int(k[1:]))
HAsROW = [t for t in UN if any(l.startswith(u'| ' + t + u' | ') for l in SL)]
cells[1] = u' **合计（' + str(len(LISTED)) + u' 条）** '
cells[2] = u' **' + fmt(enc_all) + u'** '
cells[3] = (u' **%.1f%%**（摘要段合计 ' % (100.0 * enc_all / dig_all) + fmt(dig_all)
            + u'，本遍补记的一枚为 ' + fmt(E80) + u' 编码／' + fmt(D80)
            + u' 摘要；两列合计与本表所列 ' + str(len(LISTED)) + u' 条一致，故不取 audit 的 ALL 行'
              + u'（它多含已接线而未在本表记账的 ' + u'⇎'.join(UN) + u'：编码 '
              + fmt(num(ALLR[2]) - enc_all) + u' ⇎ 摘要 ' + fmt(num(ALLR[1]) - dig_all)
              + u'，这 %d 条各自已在门槛表⇎语料表两行记账；唯一码点那格由本遍按 audit 的编码区正则逐条现数取列内并集，'
                u'逐条与 audit 现算值对拍） ' % len(UN))
cells[5] = u' **%s** ' % fmt(len(UNI))
assert len(cells) == len(L2[T0 + 1].split(u'|')), (len(cells), len(L2[T0 + 1].split(u'|')))
L2[T0 + 1] = u'|'.join(cells)
NOTE = [i for i, l in enumerate(L2) if l.startswith(u'（B54 起的 ') and u'机械行' in l]
assert len(NOTE) == 1, NOTE
L2[NOTE[0]] = (u'（B54 起的 %d 行是按 `audit.py` 当下输出直补的机械行——只登记编码字符、两档保留率、唯一码点与字符/语义单元五格, '
               u'不重写各条的口径注; 本遍再直补 B80 一枚, 合计行只列本表已记账条目, 唯一码点由本遍逐条现数取并集, '
               u'不再抄 ALL 行。）'
               % len([x for x in present + [u'B80'] if int(x[1:]) >= 54]))
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


FAILD = dict((u'B' + m.group(1), len([x for x in m.group(2).split(u',') if x.strip()]))
             for m in re.finditer(u'^  B(\\d+): 编码侧=\\[(.*?)\\]', AUD, re.M))
assert (not GATE_PASS) == bool(FAILD) and u'B80' not in FAILD, (GATE_PASS, FAILD)

S2 = subn(u'共 \\*\\*\\d+ 条\\*\\*（`babeltele/[^`]*`, 本遍补上 B\\d+ 的四处记账行[^）]*）',
          lambda m: (u'共 **%d 条**（`babeltele/%s`, 本遍补上 B80 的四处记账行, 合计按本表所列 %d 条现算, '
                     u'唯一码点逐条现数；已接线而未进本表合计行的 %s 均已记了门槛表⇎语料表两行, '
                     u'本遍不再重记其记账数（上一遍该行按 B74 现量写就, 未含 B79））'
                     % (len(FIDS), runs(FIDS), len(LISTED), u'／'.join(UN))), S2)
S2 = subn(u'## 保真门槛：`python corpus/audit.py` → \\*\\*PASS\\*\\*（\\d+ 条）',
          lambda m: (u'## 保真门槛：`python corpus/audit.py` → **PASS**（%d 条）' % len(FIDS)
                     if GATE_PASS else
                     u'## 保真门槛：`python corpus/audit.py` → 本遍复跑总判 **FAIL**：失配只落在未记账的 %s'
                     u'（audit 报其 %d 枚编码侧数字锚在原文侧读不到）；本遍记账的 B80 错配 %d 枚, 本表所列 %d 条不受影响'
                     % (u'／'.join(sorted(FAILD)), sum(FAILD.values()), gk(u'anchor_err'), len(LISTED))), S2)
S2 = subn(u'当前 \\*\\*\\d+ 条语料／\\d+ 条\\*\\*推导全部通过（audit 自报“已机检的推导 \\d+ 条”，行集与文件数相符 \\d+ ⇎ \\d+）',
          lambda m: (u'当前 **%d 条语料／%d 条**推导%s（audit 自报“已机检的推导 %d 条”，行集与文件数相符 %d ⇎ %d）'
                     % (len(FIDS), PROOFS,
                        u'全部通过' if GATE_PASS else u'除 %s 外全部通过' % u'／'.join(sorted(FAILD)),
                        PROOFS, len(GROW), len(FIDS))), S2)

assert S2.count(u'python -X utf8 corpus/_fill74.py') == 1
L80 = [(u'python -X utf8 corpus/_mkB80.py',
        u'                     # 建条目(前半, 与 _mk80emit.py 同场 exec): 扁平契约 ' + str(len(FP))
        + u' 枚键／标量恒等式 ' + str(gk(u'scalar_clos_n')) + u' 条 ⇎ DERIV ' + str(len(DER))
        + u' 枚算式, 四档面(原行⇎折平⇎摘壳⇎节窗)⇎游标针 ⇎ 正则针两尺, 采集侧同定义标量 '
        + str(gk(u'pick_agree')) + u'/' + str(gk(u'pick_agree')) + u' 枚相符'),
       (u'python -X utf8 corpus/_mkdigest3.py B80 <entry> '
        + u' '.join(u'%s %s 300 200' % (LBL[i], SRC[i]) for i in range(NSRC)),
        u'   # 五源分节摘要(' + fmt(D80) + u' 字符, ' + str(gk(u'anchor_total'))
        + u' 枚锚全命中, 五份各开一窗 300/200）'),
       (u'python -X utf8 corpus/_wire80.py',
        u'                    # 幂等接线: SRC/ATOM/SCAN(审计器侧第三套实现)/DERIV/B80V 进 audit.py, 落盘前复跑 '
        + str(len(FP)) + u' 枚扁平键 ⇎ ' + str(len(DER)) + u' 枚算式 ⇎ ' + str(gk(u'checks')) + u' 次归属检查'),
       (u'python -X utf8 corpus/_fill80.py',
        u'                    # 第五遍(注区): 手写索引循环行界 ⇎ `bisect` 行号尺 ⇎ lookahead 邻居尺 ⇎ ast 摘门右式各重导一次, '
        + str(gk(u'scalar_clos_n')) + u' 条恒等式 ⇎ ' + str(gk(u'bool_clos_n')) + u' 道布尔门 ⇎ ' + str(VFORM)
        + u' 条 V 形现算归零后写回 ⛓解读注（14 行复测表 ⇎ 复算 ' + str(len(FP)) + u' 键对账 0 不符 ⇎ 独有 0 枚）')]
CUR = u'python -X utf8 corpus/_fill74.py'
for head, tail in L80:
    S2 = after(S2, CUR, head + tail + NL)
    CUR = head

T3 = u'corpus/README.md.tmp80'
io.open(T3, u'w', encoding=u'utf-8', newline=NL).write(S2)
os.replace(T3, u'corpus/README.md')
json.dump(dict(listed=LISTED, listed_n=len(LISTED), enc=enc_all, dig=dig_all, uniq=len(UNI),
               proofs=PROOFS, b80_enc=E80, b80_dig=D80, unaccounted=UN, audit_rows=len(GROW),
               entries_files=len(FIDS), gate_pass=GATE_PASS, gate_failed=FAILD,
               bytes=BS, chars=CH_, lines=LN, newlines=NLC, nonblank=NB,
               maxlen=ML, ff=FFC, ff_only=EFO, shell_lines=gk(u'shell_lines'), cr=CR, nonascii=NA,
               bom=BOM, delta=DELTA, tag_shape=SHAPE, tag_open=OPEN, tag_close=CLOSE, tag_url=URL,
               tag_pseudo=PSEU, ent=ENT, comment=COM, keys=len(FP), deriv=len(DER), vform=VFORM,
               close_keys=CLOSEK, dkeys=DKEYS, bool_gates=gk(u'bool_clos_n'),
               anchors=gk(u'anchor_total'), anchor_face=(CLS1, CLSN, CLS5), anchor_ref=REF1,
               anchor_cross_unref=CROSS_UNREF, checks=gk(u'checks')),
          io.open(u'corpus/_b80readme.json', u'w', encoding=u'utf-8'), ensure_ascii=False, indent=1)
print(u'README 已记账: 合计（%d 条）编码 %s ⇎ 摘要 %s ⇎ 保留 %.1f%% ｜ 唯一码点(列内并集) %s ｜ 未记账 %s ｜ '
      u'audit 行 %d ⇎ 文件 %d ｜ 推导 %d 条 ｜ 本遍总判 %s%s ｜ B80 行 %s 编码／%s 摘要 ｜ 锚 %d 处⇎归属检查 %d 次⇎错配 %d'
      % (len(LISTED), fmt(enc_all), fmt(dig_all), 100.0 * enc_all / dig_all, fmt(len(UNI)),
         u'⇎'.join(UN), len(GROW), len(FIDS), PROOFS, u'PASS' if GATE_PASS else u'FAIL',
         u'' if GATE_PASS else u'（只落在 %s）' % u'⇎'.join(sorted(FAILD)),
         fmt(E80), fmt(D80), gk(u'anchor_total'), gk(u'checks'), gk(u'anchor_err')))
