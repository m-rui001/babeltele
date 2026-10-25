# -*- coding: utf-8 -*-
"""把 B82 的独立复算器(_b82_scan / B82V)接进 audit.py, 并生成 DERIV['B82']。
幂等: 重复运行先摘旧块再插新块; 只动 B82 自己的区域, 并行 agent 的其它条与已进门各条行段原样保留。
_b82_scan 的量测段从两处逐行机械抽出: corpus/_mkB82.py 的 SCAN BEGIN ⇎ SCAN END(五份面、四档口径,
与采集侧 _b82meas.json 的逐键对账段就嵌在这段之内) ⇎ corpus/_mk82emit.py 的 SCAN2 BEGIN ⇎ 发射段 print
(段落层 ⇎ 行号尺 ⇎ 切开判词 ⇎ 模板行池; 933 行以后只是要打印的读数与探针后门, 不切进门),
只在头部换成 audit 自己的路径常量与模块别名。
真正的独立性来自八处:
①采集侧 corpus/_pick82.py 是先于建条目写好的另一套实现(游标 find 环、邻居字符手扫、整行序列正则判壳、
  (?<=[.!?]) 正则切句、一条 RXU 选择支抽数值、节号正则取块、splitlines−split(\\n) 行式对账), 建条目侧七处
  全换机制而不换定义: re.findall(re.escape(nd)) 整体扫描 ⇎ 游标环、(?<![A-Za-z]) 断言 ⇎ 邻居手扫、
  折叠后逐段比 token 形状 ⇎ 整行正则、逐字符扫“句点/问号/叹号+空白+小写或左括号”、手工扫数字串就地读单位词、
  按“节号点段数 ⇎ 前导空格数”整数量判档、逐行是否以 \\x0c 起头现读行式; 两边在口径一致的键上逐量对账;
②插门之前把 _b82flat.json 的每个键与 DERIV['B82'] 的每条表达式各重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 五份都按整份归一面判成员、
  按原文件行面(逐行归一后以正文不可能出现的 \\x01 相连)判落点;
④数字读数一律从面内现读: 抬头年份/BCP ⇎ Experimental/Obsoletes ⇎ Updates 由标题页正则现采,
  段落起止由剥引文偏移映回原行号, 节窗由"前导空格数+点号段数"同级标题识别器现定界, 一个不手填;
⑤行号尺是往返的: 段窗与切开针的首末行每枚都拿行号回原文件取那一行、看针是否真在这一行内,
  再配反向对照——跨行针的整串拿到它的首字行应当一枚也不读通, 两半各自回自己那一行才读得通;
⑥四档口径阶梯(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳+去编号折平)单调, 逐份增益按枚分账后与总差闭合;
  页码壳针 “[Page 1]” 在第三档读到零枚不是口径失效, 而是它整行被壳尺吃掉, 所以它只登记为读数、进不了锚;
⑦模板行池的容斥与关键词模板段的两把尺(折平相同 ⇎ 原行相同 ⇎ 词同分行不同)同时闭合;
⑧恒等式与布尔门全归零送门槛重算, DERIV 的字面数是复合式: 同一字面的每条算式都在括号里,
  只有全部相符才等于该字面。
锚的五源同形分账: 命中五份的锚全是不含空格的单词锚(9 枚单词锚里 6 枚五中、3 枚不中),
  含空格的锚最多命中四份——所以"五份同形"是单词尺的属性, 不是这五份文书在这句话上一致。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB82.py', encoding='utf-8').read()
EM = io.open(u'corpus/_mk82emit.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/tcpRTO/rfc1122.txt', u'corpus/raw/tcpTW/rfc9293.txt',
        u'corpus/raw/httpKA/rfc9112.txt', u'corpus/raw/idle/rfc9113.txt',
        u'corpus/raw/idle/rfc9000.txt']
MARK = u'# B82: 一条空闲连接多久该关掉'
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
SCAN2 = drop_marker(cut(EM, u'# --- SCAN2 BEGIN ---', u"print(u'发射段"))
assert SCAN.count(u'PK = _js') == 0 and PICK in SCAN, u'PICK 段应嵌在 SCAN 段之内'
assert SCAN2.count(u'print(') == 0 and SCAN2.count(u'json.load') == 0
assert SCAN.count(u'json.load') == 1 and u'ENTRY' not in SCAN and u'DERIV' not in SCAN
# ZV 表由 _mkB82.py 的登记尾段建立, 那一段不切进门; SCAN2 里只有 ZV.append, 门内先立空表让它跑通。
SCAN2 = u'ZV = []' + NL + SCAN2
MEAS = SCAN.rstrip() + NL + NL + SCAN2.rstrip() + NL

NAMES = (u'rd pnorm fold is_shell_pick shell_by_shape ub ub_re cnt_cur cnt_re digit_runs num_pairs '
         u'num_pairs_re sent_bounds sents canon tag_strip sh_line_of _after _nb _prev Z '
         u'row_fd LMAPC L LOW LOW_SHLIG LOW_TAG FOLDC SHC SHTAGC FACEK RXU_PICK PK PKND NUMAGREE '
         u'NUMLIT UNITW UNITW_S UNIT_IDX UORD DUR SPELL TAGRE TAGR TAGBRK TAGPR SHP SECND SECTTL '
         u'REFH REFH WIN ROLEN ROLEPK WRAPK NEEDLEN SAMEK SAMEK2 CITED NEG PINP RAWL '
         u'PARA TONE T1W CLOSE ZID LIMW PROBE _anline AN ANX ANL grow word_left word_right off_last '
         u'blk line_of fmap ln_of ln_end loc split_pieces split_anchor pair_anchor needle_at '
         u'line_holds straddle_pair face_window pool_of head_words head_words_all suffix_words '
         u'TONED pres_n raw_span row_of_fd difflib '
         u'ROWS FD ALN ANSET ROWSRAW KEEP PP PINS PB SEGRT SPLITREC TAGCUTK TAGCUTREC NEWPAIR NEWSET '
         u'OLDPAIR OLDSET OPC OSHAL OVLNEW QUADS TRIPS TSK TSP UNION UNION25 WRAPK2 KWPAIR KWPOS KWK '
         u'POOL POOL25 PTXT PW Z2 ZEXP CLOSE2 FAN TAGS IDX ATOMFAIL BLKFAIL ALOG LBL NSRC FAM IDS YR '
         u'OLD NEW PATH F B T L').split()
for nm in NAMES:
    assert re.search(u'(?<![._a-zA-Z0-9])%s(?![a-zA-Z0-9_])' % nm, MEAS), nm

HEAD = u'''
# B82: 一条空闲连接多久该关掉——五份一手文书五种答法:
# raw/tcpRTO/rfc1122.txt(A 1122/1989 Requirements: 保活写成 MAY、MUST 默认关闭、间隔 MUST 不小于 two hours,
#   数值以英文单词拼出而不是 7200, 页脚 “[Page 1]” 整行是壳)
# ⇎ raw/tcpTW/rfc9293.txt(B 9293/2022 TCP: 同一句逐字重印, 只多插两枚编号 (MUST-27)(MUST-28),
#   并把该节归为本地事项——四档口径的第三⇎第四档之差只由这一份贡献)
# ⇎ raw/httpKA/rfc9112.txt(C 9112/2022 HTTP/1.1: 超时长度与是否存在一枚要求都不提, 只说连接可以被丢弃)
# ⇎ raw/idle/rfc9113.txt(D 9113/2022 HTTP/2: 鼓励长开但允许终止空闲连接, 关前先发 GOAWAY)
# ⇎ raw/idle/rfc9000.txt(E 9000/2021 QUIC: max_idle_timeout 两端各自宣告、生效值取两者最小,
#   0/省略即关闭, 且 MUST 不小于 3×PTO——唯一将超时写成协商量的一份).
# 本函数从五份字节独立复算: 判词针的四档口径阶梯与逐份增益(换行 ⇎ 页壳 ⇎ 编号三笔分账)、
# “[Page 1]” 被壳尺吃掉所以只作读数不作锚的三键复核、1122 ⇎ 9293 逐句对照的句数/同句数/新句数与新句
# 可定位性闭合、编号切开针被吃掉的字符宽度账、段窗(前导空格数+点号段数现定界 ⇎ 目录与正文各印一次)、
# 语气五轨两把尺(邻居手扫 ⇎ 负向断言正则)同值、数值族按五份全冷/至少一份读通分家、
# 关键词模板段四变体的共头共尾与两把尺判法、施事者角色行池的容斥闭合、
# 抬头谱系(年序 ⇎ BCP ⇎ Experimental ⇎ Obsoletes/Updates)、行号尺的往返复核与跨行针的反向对照、
# 与采集遍 _b82meas.json 的逐键对账(换机制不换定义)。
# 不可由在库文件判定的: 五份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 1122 的保活节此刻是否仍算"本地事项"、9112/9113/9000 相互引用此刻的现行版本、
# 现网服务器与浏览器实际取多少秒空闲超时——只进解读注, 不进门槛。
def _b82_scan():
    import io, re, glob, json as _js
    P5 = SRC['B82']
    NSRC = 5
    LBL = [u'1122', u'9293', u'9112', u'9113', u'9000']
    FAM = [u'old', u'new', u'new', u'new', u'new']
    IDS = [u'1122', u'9293', u'9112', u'9113', u'9000']
    YR = [1989, 2022, 2022, 2022, 2021]
    MON = [u'October', u'August', u'June', u'June', u'May']
    OLD = [i for i in range(NSRC) if FAM[i] == u'old']
    NEW = [i for i in range(NSRC) if FAM[i] == u'new']
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
            # 扁平件是 JSON 回读的: 整型键已被转成字符串, 现算的整数键先归同侧再比
            return dict((str(k), _dv(v)) for k, v in x.items())
        return x
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert BODYTXT.count(u'json.load') == 1 and u'__import__(' in BODYTXT and u'print(' not in BODYTXT
BODYTXT = BODYTXT.replace(u'json.', u'_js.')
# 门内不给试针后门: B82PROBE 只在建条目那遍有意义, 门槛这一遍落空的锚与段针必须立刻停机
BODYTXT = BODYTXT.replace(u"(u'B82PROBE' in __import__('os').environ)", u"(u'B82PROBE' in {})")
assert BODYTXT.count(u'__import__') == 1 and u'difflib' in BODYTXT and u"_js.load" in BODYTXT

FLAT = json.load(io.open(u'corpus/_b82flat.json', encoding='utf-8'))
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
    ep = glob.glob(u'corpus/babeltele/B82_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    USED = len(re.findall(u'\\u27e8', enc))
    ANCHS = set(re.findall(u'\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc))
    CITES = re.findall(u'\\u27e6(' + u'|'.join(TAGS) + u')\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B82: 正文里没有带标签的锚'
    assert len(CITES) == USED, u'B82: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B82: 标签嵌套'
    ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
    MISSLINE = [x for x in CITES
                if x[1] not in ANSET[IDX[x[0]]] and pnorm(x[1]) not in ROWSRAW[IDX[x[0]]]]
    HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCHS)
    WORD = [a for a in ANCHS if u' ' not in pnorm(a)]
    MULTI = [a for a in ANCHS if u' ' in pnorm(a)]
    F[u'anchor_total'] = USED
    F[u'anchor_distinct'] = len(ANCHS)
    F[u'anchor_err'] = len(ERR)
    F[u'anchor_single'] = len([a for a in ANCHS if len(HITC[a]) == 1])
    F[u'anchor_cross'] = len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC])
    F[u'anchor_all5'] = len([a for a in ANCHS if len(HITC[a]) == NSRC])
    F[u'anchor_word'] = len(WORD)
    F[u'anchor_word_all5'] = len([a for a in WORD if len(HITC[a]) == NSRC])
    F[u'anchor_multi_max'] = max([len(HITC[a]) for a in MULTI])
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
    # 五源同形的分账口径: 全部由单词锚贡献, 含空格的锚最多命中四份 ⇒ 共有是尺的属性不是引用的属性
    assert F[u'anchor_word_all5'] == F[u'anchor_all5'], u'B82: 有五源同形的锚含空格, 口径要重立'
    assert F[u'anchor_all5'] <= F[u'anchor_word'], u'B82: 五源同形数不可能超过单词锚数'
    assert F[u'anchor_multi_max'] == NSRC - 1, u'B82: 多词锚的最高命中数挪动了'
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


NSP = {'SRC': {'B82': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
CALL = u"    return F" + NL + NL + u"_B82 = _b82_scan()" + NL
_run(HEAD + BODYTXT + ANCH + CALL, u'<b82 probe>', NSP)
PF = NSP['_B82']
MISS = [k for k in sorted(FLAT) if k not in PF]
for k in MISS:
    SKIP.add(k)
print(u'门内跳过的非复算键 %d 枚: %s' % (len(MISS), MISS))
# contract_n 是"本遍登记到第几键"的自计量: 门内的键集与建条目那遍不必同, 只作软量
if u'contract_n' in FLAT:
    SKIP.add(u'contract_n')

CALL = u"    return F" + NL + NL + u"_B82 = _b82_scan()" + NL
BLK = HEAD + BODYTXT + ANCH + gen_asserts() + u'    return F' + NL + NL + \
    u"_B82 = _b82_scan()" + NL + \
    u"B82V = lambda k, i=None: (_B82[k] if i is None else _B82[k][i])" + NL + NL + \
    u"# ---- B82 DERIV (generated by corpus/_wire82.py from corpus/_deriv82.json; do not hand-edit) ----" + NL
J = json.load(io.open(u'corpus/_deriv82.json', encoding='utf-8'))
BLK += u"DERIV['B82'] = " + repr(J) + NL + u"# ---- /B82 DERIV ----" + NL
compile(BLK, u'<b82 block>', u'exec')

# 幂等: 先摘掉上一版的整段 B82 区域(注释头 → 门槛驱动段首行), 再插新块。
i0 = S.find(MARK)
while i0 >= 0:
    nxt = S.find(NL + ANCHOR, i0)
    assert nxt >= 0, u'anchor scan'
    S = S[:i0] + S[nxt + 1:]
    i0 = S.find(MARK)
if u'B82V=B82V' in S:
    S = S.replace(u'B82V=B82V,' + NL, NL)
ME = re.search(u"(?m)^(\\s*)(B\\d+V=B\\d+V)\\)$", S)
assert ME, u'anchor env'
S = S[:ME.end(2)] + u',\n' + ME.group(1) + u'B82V=B82V' + S[ME.end(2):]

SRCBLK = (u"SRC['B82'] = ['corpus/raw/tcpRTO/rfc1122.txt', 'corpus/raw/tcpTW/rfc9293.txt',\n"
          u"              'corpus/raw/httpKA/rfc9112.txt', 'corpus/raw/idle/rfc9113.txt',\n"
          u"              'corpus/raw/idle/rfc9000.txt']\n"
          u"ATOM.add('B82')\n\n\n")
assert u"SRC['B82']" not in S
SPOT = S.find(NL + ANCHOR)
assert SPOT >= 0, u'anchor splice'
S = S[:SPOT + 1] + SRCBLK + BLK + NL + S[SPOT + 1:]
compile(S, u'<audit.py wired>', u'exec')

NS = {'SRC': {'B82': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob, 'DERIV': {}}
_run(BLK, u'<b82 block>', NS)
env = NS['B82V']
BAD, MISMATCH = [], []


def deep(x):
    if isinstance(x, dict):
        return dict((str(k), deep(y)) for k, y in x.items())
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
        got = eval(v, dict(NS), {'B82V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b81_scan' in S and u'_b82_scan' in S
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b82_scan+B82V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次／五源同形 %d 枚(全为单词锚)'
      % (len(J), len(FLAT) - len(SKIP), len(J), env('anchor_total'), env('anchor_distinct'),
         env('checks'), env('anchor_all5')))
