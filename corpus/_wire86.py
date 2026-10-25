# -*- coding: utf-8 -*-
"""把 B86 的独立复算器(_b86_scan / B86V)接进 audit.py, 并生成 DERIV['B86']。
幂等: 重复运行先摘旧块再插新块; 只动 B86 自己的区域, 并行 agent 的其它条与已进门各条行段原样保留。
_b86_scan 的量测段从两处逐行机械抽出: corpus/_mkB86.py 的 SCAN BEGIN ⇎ SCAN END(五份面、四档口径,
与采集侧 _b86meas.json 的逐键对账段就嵌在这段之内) ⇎ corpus/_mk86emit.py 的 SCAN2 BEGIN ⇎ SCAN2 END
(第二遍的九处换机制: 逐字符行号表 ⇎ 累积长度表+bisect、finditer 切句 ⇎ 逐字符扫句界、枚举每次命中并量跨行
⇎ 只问该行含不含针、逐对相邻非空行现拼短语 ⇎ 两档总量之差、按 token 判形状丢编号 ⇎ 两条正则整串替换、
段窗(量测段没有的一档)、按四条正则级联现读默认值 ⇎ 逐字符扫描、现列 2 的幂清单求和 ⇎ 逐次倍增值累加、
游标 find 环在自导摘壳面上重数反向针 ⇎ 整串正则计数; SCAN2 END 之后只是要打印的读数与探针后门, 不切进门),
只在头部换成 audit 自己的路径常量与模块别名。
量测段里那 38 条 print 是建条目那遍的读数汇报, 门内不需要出声: 函数头把 print 换成本函数作用域里的空操作,
所以切进来的行一字不改, 读数仍照跑、断言仍照判。
真正的独立性来自十处:
①采集侧 corpus/_pick86.py 是先于建条目写好的另一套实现(游标 find 环、邻居字符手扫、整行序列正则判壳、
  (?<=[.!?]) 正则切句、一条 RXU 选择支抽数值、节号正则取块、splitlines−split(\\n) 行式对账), 建条目侧九处
  全换机制而不换定义, 两边在口径一致的 44 枚键上逐量对账;
②插门之前把 _b86flat.json 的每个键与 DERIV['B86'] 的每条表达式各重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 五份都按整份归一面判成员、
  按原文件行面(逐行归一后以正文不可能出现的 \\x01 相连)判落点;
④数字读数一律从面内现读: 抬头年份/页壳形/键值表头由正则现采, 段落起止由剥引文偏移映回原行号,
  节窗由 SECHDR 同级标题识别器现定界, 一个不手填;
⑤行号尺是往返的: 段窗与切开针的首末行每枚都拿行号回原文件取那一行、看针是否真在这一行内,
  再配反向对照——跨行针的整串拿到它的首字行应当一枚也不读通, 两半各自回自己那一行才读得通;
⑥四档口径阶梯(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳+去编号折平)单调, 逐份增益按枚分账后与总差闭合;
  第三⇎第四档之差只由 9293 的编号族贡献, 而它只让一枚判词针由读不通变读得通(净 +1, 无一枚回落);
⑦本遍新登记的键由"进 SCAN2 时的键名快照 ⇎ 结束时再取一次"的差集数出, 前缀尺单用会多捞建条遍的
  ans_page_rows ⇎ ans_shell_rows 两枚, 所以门内以差集为准并把多捞清单也登记成键;
⑧跨行义务词两把尺(逐对相邻非空行现拼 ⇎ 两档总量之差)逐份对上, 大写 ⇎ 小写分档另数;
⑨内核默认值四式级联 ⇎ 采集侧 'Default:' 一把正则, 逐键同值, 三枚"逐行读不到 ⇎ 整块读得到"的键两遍同名单;
⑩恒等式与布尔门全归零送门槛重算, DERIV 的字面数是复合式: 同一字面的每条算式都在括号里,
  只有全部相符才等于该字面。
锚的五源同形分账与 B82 相反: 命中五份的 7 枚里有 2 枚含空格('must not' ⇎ 'SHOULD NOT'),
  因为义务词形在五份里都印 —— 所以"五份同形"在 B86 不是单词锚的专属属性; 命中数只有 1、2、5 三档(3、4 档 0 枚)。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB86.py', encoding='utf-8').read()
EM = io.open(u'corpus/_mk86emit.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/tcpRetr/rfc793.txt', u'corpus/raw/tcpRetr/rfc1122.txt',
        u'corpus/raw/tcpRetr/rfc9293.txt', u'corpus/raw/tcpRetr/rfc6298.txt',
        u'corpus/raw/tcpRetr/ip-sysctl.txt']
MARK = u'# B86: 重传几次、多久之后该放弃'
# 门槛驱动段(逐条目跑 check_proof)是本文件里最靠后的模块级语句; 摘旧块与插新块都只认它的首行。
ANCHOR = u'rows, fails, proofs, soft_all = [], [], [], []'
SRCBLK = (u"SRC['B86'] = ['corpus/raw/tcpRetr/rfc793.txt', 'corpus/raw/tcpRetr/rfc1122.txt',\n"
          u"              'corpus/raw/tcpRetr/rfc9293.txt', 'corpus/raw/tcpRetr/rfc6298.txt',\n"
          u"              'corpus/raw/tcpRetr/ip-sysctl.txt']\n"
          u"ATOM.add('B86')\n\n\n")


def cut(src, a, b):
    i = src.index(a)
    j = src.index(b, i)
    return src[i:j]


def drop_marker(seg):
    return seg[seg.index(NL) + 1:]


SCAN = drop_marker(cut(MK, u'# --- SCAN BEGIN ---', u'# --- SCAN END ---'))
PICK = drop_marker(cut(MK, u'# --- PICK BEGIN ---', u'# --- PICK END ---'))
SCAN2 = drop_marker(cut(EM, u'# --- SCAN2 BEGIN ---', u'# --- SCAN2 END ---'))
assert SCAN.count(u'PK = json.load') == 1 and PICK in SCAN, u'PICK 段应嵌在 SCAN 段之内'
assert SCAN2.count(u'print(') == 0 and SCAN2.count(u'json.load') == 0
assert SCAN.count(u'json.load') == 1 and u'ENTRY' not in SCAN and u'DERIV' not in SCAN
# ZV 表由 _mkB86.py 的登记尾段建立, 那一段不切进门; SCAN2 里只有 ZV.append, 门内先立空表让它跑通。
SCAN2 = u'ZV = []' + NL + SCAN2
MEAS = SCAN.rstrip() + NL + NL + SCAN2.rstrip() + NL

NAMES = (u'rd pnorm fold cnt_cur cnt_re cnt_ovl _tabs ub_tab ub_cur ub_re is_shell_pick _yearish '
         u'sh_blank sh_ff sh_foot sh_hdr793 sh_hdr1122 sh_ietf sh_hdrnew shell_shape tag_runs tag_strip '
         u'sent_cuts sent_at cum_line_raw cum_line _bnd_word kw_union _occ tag_token_scan num_pairs '
         u'np2 face_of off_line sents sents_char canon lfind bisect_idx face_of_win cut_at _tok_at '
         u'_after_kw _borrow defval defval_lines sum_last sum_kill geo_sum eq_face neg_rows K _cb Z '
         u'rowfold face_rows ln_of ln_span occ_at sent_spans tag_shape tag_eat straddle word_edge '
         u'row_anchor shrink_anchor AN AO AF blk letter_runs tone_count tag_count dv2 dv2_rows '
         u'num_run num_after dbl dbl_kill mat2 ZEXP '
         u'B T RAWL L TAGR TAGBR NAOFF RAWCUM FOOT HDR793 HDR1122 IETF HDRNEW SHPREDS OB OBL '
         u'FOL SHP SHTAG FOLDX SHPX SHTAGX HEADS HEADSL LOWT FOLDX_LOW TAGKIND TAGSHAPE TT NOSPC '
         u'GRP UNIT UNITS GLUE F0 FU FW RXN DUR NEEDLES NK ROWSN CUM FACE OFFS PAGESH TAGRE '
         u'BLKS OPS OSH EV KEYRE KEYS BODY REL REL2 PKSUB RELP RELX UNIV TAIL WS DVP DVL DVS DV EQ '
         u'DOC8 P9246 RTO NEG RP KW KWS KWPAIR PK PAIRS N3D CLOSE CLOSE2 G GK ZID NEGEX RPEX IDX '
         u'PROBE K0 TAGS FAN LIMW ATOMFAIL BLKFAIL BADREAD ALLROWS NSROWS SP_P SC SCROWS '
         u'TAGSHAPE2 TWO_TAG TC ST_UP ST_LO STSH ROWSRAW ANSET ALOG PINS PB ANSW SEGRT OVW S2T '
         u'SECHDR OVHDR OVOVN OVNEXT2 NEWIDX OVLNEW OSROW KEY2 HD2 KN2 BLK2 HIST2 DUP2 NB2 RL2N '
         u'SUB2 RL2P UN2 BOTH2 DVR2 DV2 DVL2 EQ2 HYP IDX2 NG2 RP2 KWS2 KWP2 EG2 GK2 Z2 ADDED EMITKEYS '
         u'NSRC PATH F').split()
for nm in NAMES:
    assert re.search(u'(?<![._a-zA-Z0-9])%s(?![a-zA-Z0-9_])' % nm, MEAS), nm

HEAD = u'''
# B86: 重传几次、多久之后该放弃——五份一手文书五种答法:
# raw/tcpRetr/rfc793.txt(A 793/1981 TCP: 事件表把 RETRANSMISSION TIMEOUT 写成无条件循环——再发一次、
#   重置定时器、返回, 全文一枚阈值也没有, 只在 OPEN 调用里留一句 “The present global default is five minutes”)
# ⇎ raw/tcpRetr/rfc1122.txt(B 1122/1989 主机需求: 立 R1 ⇎ R2 双阈值, R2 SHOULD ≥100 秒 ⇎ SYN 的 R2 MUST ≥3 分钟,
#   到 R2 必须 close the connection, 并把设 R2 的权利交给应用)
# ⇎ raw/tcpRetr/rfc9293.txt(C 9293/2022 STD 1: 逐句重印 1122 那段并挂 (MUST-n)(SHLD-n) 编号,
#   独家把 R2 写成 "infinity", 同时原样保留 793 的无限循环并把 “the TCP will” 改成 “the TCP endpoint will”)
# ⇎ raw/tcpRetr/rfc6298.txt(D 6298/2011 RTO 计算: 只封顶单次超时 at least 60 seconds, 通篇不谈总放弃)
# ⇎ raw/tcpRetr/ip-sysctl.txt(E Linux 实现文档: R1/R2 落成 tcp_retries1=3 ⇎ tcp_retries2=15,
#   给 (N, N+1) 错位口径、倍增等式 6→63→127 ⇎ 5→31→63、924.6 秒的 hypothetical timeout,
#   和一整组 SCTP 纯次数阈值).
# 本函数从五份字节独立复算: 判词针的四档口径阶梯与逐份增益(换行 ⇎ 页壳 ⇎ 编号三笔分账)、
# 9293 编号族切开那一枚判词针的两把尺对账(去编号面短 677 码位 = 本遍 token 尺 ⇎ 建条遍正则尺吃字之差)、
# 1122 ⇎ 9293 同段对照的句数/同句数/新句数与新句可定位性闭合、两块节号由 SECHDR 现读而截断串只认下一节标题、
# 段窗(量测段没有的一档: 行区间切片 ⇎ 保形 ⇎ 摘壳两把 ⇎ 端点逐枚回原文件自验 ⇎ 窗内语气词逐 token 读)、
# 义务词五轨三把尺(邻居手扫 ⇎ 负向断言正则 ⇎ 逐对相邻行现拼)同值、跨行大写 ⇎ 小写分档、
# 内核键名重名 ⇎ 两把名尺容斥 ⇎ 默认值四式级联 ⇎ 逐行读不到而整块读得的三枚键、
# 倍增等式三轨(幂清单求和 ⇎ 逐次累加 ⇎ 闭式)与面上印出的秒数、924.6 秒的五枚候选算法逐格差账、
# 反向独占针在他份零命中 ⇎ 本份全读通、模板段两把尺的共头共尾、
# 与采集遍 _b86meas.json 的逐键对账(换机制不换定义)。
# 不可由在库文件判定的: 五份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页
# (9293 那两句 MUST 有没有被 errata 改过、1122 的 R1/R2 是否又被更新)、现网内核装机值
# (sysctl 里 tcp_retries2 此刻实际是多少)、Linux 版本间该文档的措辞改动——只进解读注, 不进门槛。
def _b86_scan():
    import io, re, glob, os, json as _js
    P5 = SRC['B86']
    NSRC = 5
    LBL = [u'793', u'1122', u'9293', u'6298', u'lin']
    FAM = [u'old', u'old', u'new', u'new', u'tbl']
    IDS = [u'793', u'1122', u'9293', u'6298', u'ip-sysctl']
    OLD = [i for i in range(NSRC) if FAM[i] == u'old']
    NEW = [i for i in range(NSRC) if FAM[i] == u'new']
    TBL = [i for i in range(NSRC) if FAM[i] == u'tbl']
    PATH = P5
    NL = chr(10)
    F = {}
    DER = {}
    LITK = {}
    print = lambda *a, **k: None

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
assert BODYTXT.count(u'json.load') == 1 and u'_js.load' not in BODYTXT
assert BODYTXT.count(u"(u'B86PROBE' in os.environ)") == 1
BODYTXT = BODYTXT.replace(u'json.', u'_js.')
# 门内不给试针后门: B86PROBE 只在建条目那遍有意义, 门槛这一遍落空的锚与段针必须立刻停机
BODYTXT = BODYTXT.replace(u"(u'B86PROBE' in os.environ)", u"(u'B86PROBE' in {})")
assert BODYTXT.count(u'_js.load') == 1 and u'difflib' in BODYTXT
assert u'print = lambda *a, **k: None' in HEAD and BODYTXT.count(u'print(') == 38

FLAT = json.load(io.open(u'corpus/_b86flat.json', encoding='utf-8'))
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
    ep = glob.glob(u'corpus/babeltele/B86_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    USED = len(re.findall(u'\\u27e8', enc))
    ANCHS = set(re.findall(u'\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc))
    CITES = re.findall(u'\\u27e6(' + u'|'.join(TAGS) + u')\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B86: 正文里没有带标签的锚'
    assert len(CITES) == USED, u'B86: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B86: 标签嵌套'
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
    F[u'anchor_multi_all5'] = len([a for a in MULTI if len(HITC[a]) == NSRC])
    F[u'anchor_multi_max'] = max([len(HITC[a]) for a in MULTI])
    F[u'anchor_hits_hist'] = [len([a for a in ANCHS if len(HITC[a]) == h]) for h in range(1, NSRC + 1)]
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
    assert F[u'anchor_word_all5'] + F[u'anchor_multi_all5'] == F[u'anchor_all5']
    assert sum(F[u'anchor_hits_hist']) == F[u'anchor_distinct']
    assert F[u'anchor_total'] == sum(F[u'tag_' + t] for t in TAGS)
    # 与 B82 相反: 本条的五源同形锚里有两枚含空格(must not ⇎ SHOULD NOT 五份都印),
    # 所以“五份同形”不是单词锚的专属属性; 命中数只落在 1、2、5 三档, 3、4 档一枚也没有。
    assert F[u'anchor_multi_all5'] == 2, u'B86: 五源同形的多词锚枚数挪动了'
    assert F[u'anchor_word_all5'] == F[u'anchor_word'] - 2, u'B86: 单词锚里没落进五源的恰是 2 枚'
    assert F[u'anchor_multi_max'] == NSRC, u'B86: 多词锚的最高命中数不再是五份'
    assert F[u'anchor_hits_hist'][2] == 0 and F[u'anchor_hits_hist'][3] == 0, u'B86: 出现了三、四源锚'
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


NSP = {'SRC': {'B86': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
CALL = u"    return F" + NL + NL + u"_B86 = _b86_scan()" + NL
_run(HEAD + BODYTXT + ANCH + CALL, u'<b86 probe>', NSP)
PF = NSP['_B86']
MISS = [k for k in sorted(FLAT) if k not in PF]
for k in MISS:
    SKIP.add(k)
print(u'门内跳过的非复算键 %d 枚: %s' % (len(MISS), MISS))
# contract_n 是"本遍登记到第几键"的自计量: 门内的键集与建条目那遍不必同, 只作软量
if u'contract_n' in FLAT:
    SKIP.add(u'contract_n')

BLK = HEAD + BODYTXT + ANCH + gen_asserts() + u'    return F' + NL + NL + \
    u"_B86 = _b86_scan()" + NL + \
    u"B86V = lambda k, i=None: (_B86[k] if i is None else _B86[k][i])" + NL + NL + \
    u"# ---- B86 DERIV (generated by corpus/_wire86.py from corpus/_deriv86.json; do not hand-edit) ----" + NL
J = json.load(io.open(u'corpus/_deriv86.json', encoding='utf-8'))
BLK += u"DERIV['B86'] = " + repr(J) + NL + u"# ---- /B86 DERIV ----" + NL
compile(BLK, u'<b86 block>', u'exec')

# 幂等: 先摘掉上一版的整段 B86 区域(SRC 行 ⇎ 注释头 → 门槛驱动段首行), 再插新块。
if SRCBLK in S:
    S = S.replace(SRCBLK, u'', 1)
i0 = S.find(MARK)
while i0 >= 0:
    nxt = S.find(NL + ANCHOR, i0)
    assert nxt >= 0, u'anchor scan'
    S = S[:i0] + S[nxt + 1:]
    i0 = S.find(MARK)
S = re.sub(u",\\n\\s*B86V=B86V(?=\\))", u"", S)
ME = re.search(u"(?m)^(\\s*)(B\\d+V=B\\d+V)\\)$", S)
assert ME, u'anchor env'
S = S[:ME.end(2)] + u',\n' + ME.group(1) + u'B86V=B86V' + S[ME.end(2):]

assert u"SRC['B86']" not in S
SPOT = S.find(NL + ANCHOR)
assert SPOT >= 0, u'anchor splice'
S = S[:SPOT + 1] + SRCBLK + BLK + NL + S[SPOT + 1:]
assert S.count(u'B86V=B86V') == 1, S.count(u'B86V=B86V')
compile(S, u'<audit.py wired>', u'exec')

NS = {'SRC': {'B86': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob, 'DERIV': {}}
_run(BLK, u'<b86 block>', NS)
env = NS['B86V']
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
def same(got, kk):
    if str(got) == kk or repr(got) == kk:
        return True
    # 恒等式总账里混着浮点账(924.6 那一族), 求和必带 .0: 0 与 0.0 是同一读数, 不是口径放宽
    if isinstance(got, bool) or not isinstance(got, (int, float)):
        return False
    try:
        return float(got) == float(kk)
    except ValueError:
        return False


for kk, v in J.items():
    try:
        got = eval(v, dict(NS), {'B86V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if not same(got, kk):
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b85_scan' in S and u'_b86_scan' in S
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b86_scan+B86V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ '
      u'锚 %d 处／去重 %d 串／归属检查 %d 次／五源同形 %d 枚(其中多词 %d 枚)／命中数分布 %s'
      % (len(J), len(FLAT) - len(SKIP), len(J), env('anchor_total'), env('anchor_distinct'),
         env('checks'), env('anchor_all5'), env('anchor_multi_all5'), env('anchor_hits_hist')))
