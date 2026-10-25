# -*- coding: utf-8 -*-
"""把 B81 的独立复算器(_b81_scan / B81V)接进 audit.py, 并生成 DERIV['B81']。
幂等: 重复运行先摘旧块再插新块; 只动 B81 自己的区域, 并行 agent 的 B67 与已进门各条行段原样保留。
_b81_scan 的量测段从两处逐行机械抽出: corpus/_mkB81.py 的 SCAN BEGIN ⇎ SCAN END(五份扫描面、四档口径,
与采集侧 _b81meas.json 的逐键对账段就嵌在这段之内) ⇎ corpus/_mk81emit.py 的 SCAN2 BEGIN ⇎ SCAN2 END
(段落层、行号尺、切开判词与模板行池), 只在头部换成 audit 自己的路径常量与模块别名。
真正的独立性来自八处:
①采集侧 corpus/_pick81.py 是先于建条目写好的另一套实现(选择支正则、^\\s*\\d+\\s*$ 页码尺、缩进判标题档、
  \\.(?=[A-Z(“]) 句界前瞻), 建条目侧七处全换机制而不换定义: 整体正则扫描 ⇎ 游标 find 环、邻居字符手扫 ⇎
  (?<![A-Za-z]) 断言、逐 token 形状比首尾 ⇎ 整行序列正则、逐位判"只由数字与空格"、手工扫数字串就地读单位词、
  数前导空格与点号段数判档、逐字符扫"句点+空白+大写或左括号/引号"; 两边在口径一致的键上逐量对账
  (115 键符 ⇎ 0 不符);
②插门之前把 _b81flat.json 的每个键与 DERIV['B81'] 的每条表达式各重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 五份都按整份归一面判成员、
  按原文件行面(逐行归一后以正文不可能出现的 \\x01 相连)判落点;
④数字读数一律从面内现读: 抬头年份/BCP ⇎ Experimental/Obsoletes ⇎ Updates 由标题页正则现采,
  段落起止由剥引文偏移映回原行号, 节窗由"前导空格数+点号段数"同级标题识别器现定界, 一个不手填;
⑤行号尺是往返的: 十四段的首末行共 28 枚针, 每枚都拿行号回原文件取那一行、看针是否真在这一行内(28 枚全中,
  其中整针落在一行 23 枚 ⇎ 被 72 列硬换行推到相邻行 5 枚), 再配一枚反向对照——把被切开的收束短语的整串
  拿到它的首字行去验, 八枚跨行针一枚也不该读通(0 枚命中), 而两半各自回自己那一行 8/8 读通;
⑥四档口径阶梯(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳+拆字折平)单调, 无关键词模板段的两份论文按 -1 登记
  (口径不存在不是零), 拆字档在 27 根判词针上一枚也不新增(增益全归换行与页壳两档, 按枚分账后与总差闭合);
⑦模板行池的容斥(各份之和 − 两两共用 + 三三共用 = 并集 ⇎ 分档乘份数 = 各份之和 ⇎ 去重 = 原行 − 重复印次)
  与"凡牵进一份论文的配对共用长行为零"同时归零;
⑧恒等式 64 条(建条侧 34 ⇎ 段落侧 30)与 44 道布尔门全归零送门槛重算, DERIV 的字面数是复合式:
  同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB81.py', encoding='utf-8').read()
EM = io.open(u'corpus/_mk81emit.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/qdelay/rfc7567.txt', u'corpus/raw/qdelay/piehdp.txt',
        u'corpus/raw/qdelay/rfc8033.txt', u'corpus/raw/qdelay/cake.txt',
        u'corpus/raw/qdelay/rfc8289.txt']
MARK = u'# B81: 排队延迟该压到多少'
# 门槛驱动段(逐条目跑 check_proof)是本文件里最靠后的模块级语句; 摘旧块与插新块都只认它的首行。
ANCHOR = u'rows, fails, proofs, soft_all = [], [], [], []'


def cut(src, a, b):
    i = src.index(a)
    j = src.index(b, i)
    return src[i:j]


def drop_marker(seg):
    return seg[seg.index(NL) + 1:]


SCAN = drop_marker(cut(MK, u'# --- SCAN BEGIN ---', u'# --- SCAN END ---'))
PICK = drop_marker(cut(MK, u'# --- PICK BEGIN ---', u'# --- PICK END ---'))
SCAN2 = drop_marker(cut(EM, u'# --- SCAN2 BEGIN ---', u'# --- SCAN2 END ---'))
assert SCAN.count(u'PK = _js') == 0 and PICK in SCAN, u'PICK 段应嵌在 SCAN 段之内'
# ZV 表由 _mkB81.py 的登记尾段建立, 那一段不切进门; SCAN2 里只有 ZV.append, 门内先立空表让它跑通。
SCAN2 = u'ZV = []' + NL + SCAN2
MEAS = SCAN.rstrip() + NL + NL + SCAN2.rstrip() + NL
for nm in (u'pnorm', u'fold', u'delig', u'is_shell_pick', u'shell_by_shape', u'row_fd', u'LIGMAP',
           u'SHP', u'SH', u'SHLIG', u'FAN', u'ALN', u'ANSET', u'ROWSRAW', u'PP', u'PINS',
           u'blk', u'line_holds', u'ln_of', u'ln_end', u'loc', u'fmap', u'line_of', u'split_pieces',
           u'split_anchor', u'needle_at', u'pool_of', u'tone_straddle_pair', u'head_words',
           u'suffix_words', u'ub', u'cnt_cur', u'cnt_re', u'cnt_ovl', u'LBL', u'NSRC',
           u'TAGS', u'IDX', u'ZID', u'Z2', u'ZEXP', u'CLOSE', u'CLOSE2', u'PK', u'NUM', u'PAIRS',
           u'RFCI', u'PAPI', u'ATOMFAIL', u'BLKFAIL', u'ALOG', u'PROBE', u'F', u'IDS',
           u'YR', u'sent_end'):
    assert re.search(u'(?<![._a-zA-Z0-9])%s(?![a-zA-Z0-9_])' % nm, MEAS), nm
assert MEAS.count(u'json.load') == 1 and u'ENTRY' not in MEAS and u'DERIV' not in MEAS

HEAD = u'''
# B81: 排队延迟该压到多少——五份 AQM 一手文书五种答法:
# raw/qdelay/rfc7567.txt(A 7567/2015 BCP: 全文一枚带单位的时长也不给, 免配置写成规范性标题
#   "4.3.  AQM Algorithm Deployment SHOULD NOT Require Operational Tuning", 同一串在目录被 72 列硬换行切开)
# ⇎ raw/qdelay/piehdp.txt(B madp/2016 论文: 通篇不立自己的默认数, 两枚全住在引述句里
#   ——引别家假设 ⇎ 评 CoDel "its default 5 ms of maximum allowed queuing delay")
# ⇎ raw/qdelay/rfc8033.txt(C 8033/2017 Experimental, Obsoletes: 7768 + Updates: 7567: 双档默认 15 ms ⇎ 15 µs,
#   通篇不写 PIE 缩写, 免配置写成陈述句 "PIE is intended to be self-configuring")
# ⇎ raw/qdelay/cake.txt(D cake/2018 论文: 只报实测不作免配置宣称, 与 madp 之间共用长行为零)
# ⇎ raw/qdelay/rfc8289.txt(E 8289/2018 标准轨道: TARGET 定义成 RTT 的 5-10%, 由此导出 5 ms 下限 ⇎ INTERVAL 100 ms,
#   关键词模板段比另两份 RFC 多插一枚 NOT RECOMMENDED, 结论句 "parameter-free for consumer use" 跨行).
# 本函数从五份字节独立复算: 27 根判词针的四档口径阶梯与逐份增益、无关键词段份的 -1 登记、
# 段落层十四段的段界/行/词/字符 ⇎ 单行段只在两份论文 ⇎ 三轨对十四段差异为零、行号尺的 28 枚往返复核
# 与 8 枚跨行针的反向对照、节窗(前导空格数+点号段数现定界 ⇎ 标题四档目录/列表/节/游离)、
# 语气五轨两把尺(邻居手扫 ⇎ 负向断言正则)同值、数值族十七式按五份全冷/至少一份读通分家、
# 三份 RFC 的关键词模板段共头共尾三变体与 "as described in" 双候选行的下限消歧、
# 施事者角色行池两两/三三共用与容斥闭合(论文配对全冷)、抬头谱系(年序 ⇎ BCP ⇎ Experimental ⇎ Obsoletes/Updates)、
# 语态三尺(第一人称动词 ⇎ 非人称 ⇎ we 计数)与引用两式(方括号编号 ⇎ "RFC 编号").
# 不可由在库文件判定的: 五份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 7768 此刻是否真被 8033 废止、madp/cake 两文的会议录用与发表状态、现网路由器实际取哪个 target——
# 只进解读注, 不进门槛。
def _b81_scan():
    import io, re, glob, json as _js
    P5 = SRC['B81']
    NSRC = 5
    LBL = [u'7567', u'madp', u'8033', u'cake', u'8289']
    FAM = [u'rfc', u'paper', u'rfc', u'paper', u'rfc']
    IDS = [u'7567', u'', u'8033', u'', u'8289']
    YR = [2015, 2016, 2017, 2018, 2018]
    RFCI = [i for i in range(NSRC) if FAM[i] == u'rfc']
    PAPI = [i for i in range(NSRC) if FAM[i] == u'paper']
    PATH = P5
    NL = chr(10)
    F = {}
    DER = {}
    LITK = {}

    def _dv(x):
        if isinstance(x, tuple):
            return [_dv(y) for y in x]
        if isinstance(x, list):
            return [_dv(y) for y in x]
        if isinstance(x, dict):
            return dict((k, _dv(v)) for k, v in x.items())
        return x
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert BODYTXT.count(u'json.load') == 1 and u'__import__(' in BODYTXT and u'print(' not in BODYTXT
BODYTXT = BODYTXT.replace(u'json.', u'_js.')
# 门内不给试针后门: B81PROBE 只在建条目那遍有意义, 门槛这一遍落空的锚必须立刻停机
BODYTXT = BODYTXT.replace(u"(u'B81PROBE' in __import__('os').environ)", u"(u'B81PROBE' in {})")
assert u'__import__' not in BODYTXT and u"_js.load" in BODYTXT

FLAT = json.load(io.open(u'corpus/_b81flat.json', encoding='utf-8'))
FAMK = sorted({k.split(u'_')[0] for k in FLAT})


def fam(k):
    h = k.split(u'_')[0]
    return FAMK.index(h) if h in FAMK else len(FAMK)


def lit(v):
    return repr(v).replace(u'u+', u'')


SKIP = set()


def gen_asserts():
    ks = sorted([k for k in FLAT if k not in SKIP], key=lambda k: (fam(k), k))
    lines, buf = [], []
    for k in ks:
        piece = u"_dv(F[u'%s']) == %s" % (k, lit(FLAT[k]))
        if buf and sum(len(x) + 5 for x in buf) + len(piece) > 100:
            lines.append(u'    assert ' + u' and '.join(buf))
            buf = []
        buf.append(piece)
    if buf:
        lines.append(u'    assert ' + u' and '.join(buf))
    return NL.join(lines) + NL


# 锚归属: 不读旁注, 从条目文件现推; 五份都是纯文本面, 两把尺(整份归一判成员 ⇎ 原文件行判落点)。
ANCH = u'''
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 整份归一面判成员、逐行归一面判落点 ----
    ep = glob.glob(u'corpus/babeltele/B81_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    USED = len(re.findall(u'\\u27e8', enc))
    ANCHS = set(re.findall(u'\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc))
    CITES = re.findall(u'\\u27e6(' + u'|'.join(TAGS) + u')\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B81: 正文里没有带标签的锚'
    assert len(CITES) == USED, u'B81: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B81: 标签嵌套'
    ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
    MISSLINE = [x for x in CITES
                if x[1] not in ANSET[IDX[x[0]]] and pnorm(x[1]) not in ROWSRAW[IDX[x[0]]]]
    HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCHS)
    F[u'anchor_total'] = USED
    F[u'anchor_distinct'] = len(ANCHS)
    F[u'anchor_err'] = len(ERR)
    F[u'anchor_single'] = len([a for a in ANCHS if len(HITC[a]) == 1])
    F[u'anchor_cross'] = len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC])
    F[u'anchor_all5'] = len([a for a in ANCHS if len(HITC[a]) == NSRC])
    F[u'checks'] = len(ANCHS) * NSRC
    F[u'nsrc'] = NSRC
    F[u'enc_chars'] = len(enc.replace(NL, u''))
    for t in TAGS:
        F[u'tag_' + t] = len(re.findall(u'\\u27e6%s\\u27e7' % t, enc))
    F[u'contract_n'] = len(F) + 1
    assert not ERR, ERR[:3]
    assert not MISSLINE, MISSLINE[:3]
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert all(F[u'tag_' + t] > 0 for t in TAGS), u'有五源标签没锚'
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all5'] == F[u'anchor_distinct']
    assert F[u'checks'] == F[u'anchor_distinct'] * NSRC
    assert F[u'anchor_all5'] <= 1, u'B81: 五份同形的锚不止一枚, 分账口径要重立'
'''


def _run(code, nm, ns):
    try:
        exec(compile(code, nm, u'exec'), ns)
    except AssertionError:
        import traceback
        tb = sys.exc_info()[2]
        while tb.tb_next:
            tb = tb.tb_next
        ls = code.split(NL)
        print(u'%s 块内断言失败于第 %d 行: %s' % (nm, tb.tb_lineno, ls[tb.tb_lineno - 1]))
        raise


NSP = {'SRC': {'B81': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
CALL = u"    return F" + NL + NL + u"_B81 = _b81_scan()" + NL
_run(HEAD + BODYTXT + ANCH + CALL, u'<b81 probe>', NSP)
PF = NSP['_B81']
MISS = [k for k in sorted(FLAT) if k not in PF]
for k in MISS:
    SKIP.add(k)
print(u'门内跳过的非复算键 %d 枚: %s' % (len(MISS), MISS))
# contract_n 是"本遍登记到第几键"的自计量: 门内的键集与建条目那遍不必同, 只作软量
if u'contract_n' in FLAT:
    SKIP.add(u'contract_n')

CALL = u"    return F" + NL + NL + u"_B81 = _b81_scan()" + NL
BLK = HEAD + BODYTXT + ANCH + gen_asserts() + u'    return F' + NL + NL + \
    u"_B81 = _b81_scan()" + NL + \
    u"B81V = lambda k, i=None: (_B81[k] if i is None else _B81[k][i])" + NL + NL + \
    u"# ---- B81 DERIV (generated by corpus/_wire81.py from corpus/_deriv81.json; do not hand-edit) ----" + NL
J = json.load(io.open(u'corpus/_deriv81.json', encoding='utf-8'))
BLK += u"DERIV['B81'] = " + repr(J) + NL + u"# ---- /B81 DERIV ----" + NL
compile(BLK, u'<b81 block>', u'exec')

# 幂等: 先摘掉上一版的整段 B81 区域(注释头 → 门槛驱动段首行), 再插新块。
i0 = S.find(MARK)
while i0 >= 0:
    nxt = S.find(NL + ANCHOR, i0)
    assert nxt >= 0, u'anchor scan'
    S = S[:i0] + S[nxt + 1:]
    i0 = S.find(MARK)
if u'B81V=B81V' in S:
    S = S.replace(u'B81V=B81V,' + NL, NL)
ME = re.search(u"(?m)^(\\s*)(B\\d+V=B\\d+V)\\)$", S)
assert ME, u'anchor env'
S = S[:ME.end(2)] + u',\n' + ME.group(1) + u'B81V=B81V' + S[ME.end(2):]

SRCBLK = (u"SRC['B81'] = ['corpus/raw/qdelay/rfc7567.txt', 'corpus/raw/qdelay/piehdp.txt',\n"
          u"              'corpus/raw/qdelay/rfc8033.txt', 'corpus/raw/qdelay/cake.txt',\n"
          u"              'corpus/raw/qdelay/rfc8289.txt']\n"
          u"ATOM.add('B81')\n\n\n")
assert u"SRC['B81']" not in S
SPOT = S.find(NL + ANCHOR)
assert SPOT >= 0, u'anchor splice'
S = S[:SPOT + 1] + SRCBLK + BLK + NL + S[SPOT + 1:]
compile(S, u'<audit.py wired>', u'exec')

NS = {'SRC': {'B81': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob, 'DERIV': {}}
_run(BLK, u'<b81 block>', NS)
env = NS['B81V']
BAD, MISMATCH = [], []


def deep(x):
    return [deep(y) for y in x] if isinstance(x, list) else list(x) if isinstance(x, tuple) else x


for k in sorted(FLAT):
    if k in SKIP:
        continue
    try:
        got = env(k)
    except Exception as e:
        BAD.append((k, repr(e)))
        continue
    if deep(got) != deep(FLAT[k]):
        MISMATCH.append((k, FLAT[k], got))
assert not BAD, BAD[:6]
assert not MISMATCH, MISMATCH[:6]
for kk, v in J.items():
    try:
        got = eval(v, dict(NS), {'B81V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b80_scan' in S and u'_b81_scan' in S
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b81_scan+B81V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT) - len(SKIP), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
