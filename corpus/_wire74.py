# -*- coding: utf-8 -*-
"""把 B74 的独立复算器(_b74_scan / B74V)接进 audit.py, 并生成 DERIV['B74']。
幂等: 重复运行先摘旧块再插新块; 只动 B74 自己的区域, 并行 agent 的 B73/B75/B76 行段原样保留。
_b74_scan 的量测段从三处逐行机械抽出: corpus/_mkB74.py 的 SCAN BEGIN ⇎ SCAN END(四份扫描面) ⇎
PICK BEGIN ⇎ PICK END(与采集侧 _b74meas.json 的逐键对账) ⇎ corpus/_mk74emit.py 的 SCAN2 BEGIN ⇎
SCAN2 END(段落层与行号尺), 只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自七处:
①采集侧 corpus/_pick74.py 是先于建条目写好的另一套实现(正则字面轨、按行取值), 建条目侧改立非重叠游标档、
  集合代数档、按分词切的 Exim 规则解析与手扫邻居字符的语气尺, 两边在口径一致的键上逐量对账(51 键符 ⇎ 0 不符);
②插门之前把 _b74flat.json 的每个键与 DERIV['B74'] 的每条表达式各重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 三份 txt 按原文件行判成员、
  两份 html 按"标签/注释不切开"的组读数判成员, 与 audit.py::_atom_face 的按扩展名分派同一口径;
④数字读数一律从面内现读: 抬头年份/月序由标题页正则现采, 段落起止由剥引文偏移映回原行号,
  Exim 的档数由规则串 F,2h,15m; G,16h,1h,1.5; F,4d,6h 现算, Postfix 的六个默认值由 postconf 条目现取, 一个不手填;
⑤行号尺是往返的: 每一枚"短语落在第几行"都拿行号回原文件取那一行、看针是否真在这一行内(12 枚全中),
  再配一枚反向对照——把被 72 列硬换行切开的收束短语的末字拿到它的首字行去验, 两份都该落空(0 枚命中);
⑥五档口径阶梯(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 断面 ⇎ 粘面)单调, Exim/Postfix 才有的断面/粘面增益
  逐份进出台账, txt 不剥壳(RFC 的 ASCII 图里有 <尖括号> 伪标签)⇎ html 不摘页壳(它没有页眉)两把尺同门;
⑦两遍壳谓词逐行对拍后把差分解到行(本遍多判 ⇎ 采集多判, 采集多的全在抬头页壳里),
  恒等式只允许由字面针与折面导出。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB74.py', encoding='utf-8').read()
EM = io.open(u'corpus/_mk74emit.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/mailRetry/rfc821.txt', u'corpus/raw/mailRetry/rfc1123.txt',
        u'corpus/raw/mailRetry/rfc5321.txt', u'corpus/raw/mailRetry/exim4_retry_spec.html',
        u'corpus/raw/mailRetry/postfix_postconf5.html']
MARK = u'# B74: 投递失败的邮件到底多久再试一次'
# 并行 agent 会把 audit.py 的尾部不断往后推; 摘旧块与插新块都只认"最先出现的那枚 scan 调用锚"。
ANCHOR_CANDS = [u'_B7%d = _b7%d_scan()' % (n, n) for n in (6, 5, 3, 2)]


def cut(src, a, b):
    i = src.index(a)
    j = src.index(b, i)
    return src[i:j]


def drop_marker(seg):
    return seg[seg.index(NL) + 1:]


SCAN = drop_marker(cut(MK, u'# --- SCAN BEGIN ---', u'# --- SCAN END ---'))
PICK = drop_marker(cut(MK, u'# --- PICK BEGIN ---', u'# --- PICK END ---'))
SCAN2 = drop_marker(cut(EM, u'# --- SCAN2 BEGIN ---', u'# --- SCAN2 END ---'))
MEAS = SCAN.rstrip() + NL + NL + PICK.rstrip() + NL + NL + SCAN2.rstrip() + NL
for nm in (u'pnorm', u'cnt_cur', u'cnt_ovl', u'occ_at', u'ub', u'detag', u'fold', u'is_shell_pick',
           u'shell_line', u'FACES', u'WIDE', u'SH', u'DS', u'DJ', u'hit_face', u'mk_nd', u'SENT',
           u'TIER', u'UNIT', u'parse_rule', u'pf_defs', u'in_tag', u'hdr_year', u'pool_lines',
           u'FAN', u'IDX', u'TAGS', u'ZID', u'CLOSE', u'sents', u'MEA', u'PMAP', u'tag_groups',
           u'GRP', u'SHPN', u'ALN', u'PP', u'fmap', u'line_of', u'AN', u'blk',
           u'ln_of', u'ln_end', u'ANSET', u'line_holds', u'WRAPND', u'PINS', u'suffix_words',
           u'head_words', u'CLOSE2', u'ISH', u'NSRC', u'LBL'):
    assert nm in MEAS, nm
assert MEAS.count(u'json.') == 1 and u'ENTRY' not in MEAS and u'DERIV' not in MEAS

HEAD = u'''
# B74: 投递失败的邮件到底多久再试一次、什么时候不再试——五份一手文书五种答法:
# raw/mailRetry/rfc821.txt(A 821/1982: 只分类不定时——"4yz   Transient Negative Completion reply" ⇎
#   "5yz   Permanent Negative Completion reply", 自认 "It is difficult to assign a meaning to the phrase
#   transient failure"(原文作 "It is difficult to assign a meaning"), 还留一句 "A rule of thumb";
#   全份零大写 MUST、零 retry、零 queue 词汇)
# ⇎ raw/mailRetry/rfc1123.txt(B 1123/1989, Requirements: 822 821: 下限三件套——"SHOULD be at least 30 minutes"
#   ⇎ "give-up time ... at least 4-5 days" ⇎ "algorithm MUST be configurable", 另有一条 DNS 指数退避与 5 秒下限;
#   72 列硬换行正把这句答案的收束短语切成两行)
# ⇎ raw/mailRetry/rfc5321.txt(C 5321/2008, Updates: 1123 ⇎ Obsoletes: 2821: 同段搬进协议标准, 术语从
#   sender-SMTP 换成 SMTP client, 再加一句 NDN 可以少试几次的 MAY 例外)
# ⇎ raw/mailRetry/exim4_retry_spec.html(D Exim: 不给义务词, 给阶梯规则串 "* * F,2h,15m; G,16h,1h,1.5;
#   F,4d,6h" 与 retry_interval_max 封顶, cutoff 那句 "the cutoff time is four days")
# ⇎ raw/mailRetry/postfix_postconf5.html(E Postfix 镜像: 只列参数默认——maximal_queue_lifetime 5d ⇎
#   minimal_backoff_time 300s ⇎ maximal_backoff_time 4000s, 加一句 "Specify 0 when mail delivery should be
#   tried only once"; manpage 离了 "seconds" 就不能说话)。
# 本函数从五份字节独立复算: 答句针的五档口径阶梯与原面⇎折平⇎摘壳⇎断面⇎粘面的逐份增益、
# 段落层五段的段界/行/词/字符与共头共尾与词集容斥、行号尺的 12 枚往返复核与错行反向对照、
# Exim 规则串的三段档数(现算=跨度)⇎ Postfix 六参数的默认值与链式大小、语气五轨两把尺(手扫邻居 ⇎ 负向断言正则)
# 同值、30 分钟下限的五档换算与低于地板值计数、抬头年份/月序/倒序、Obsoletes ⇎ Updates 与互引方向、
# 共用长行池(字面尺 ⇎ 剥标签尺)与写法分家、组面⇎壳账(html 的壳全是空行)、BOM ⇎ 非 ASCII ⇎ 换页符 ⇎ 断词。
# 恒等式(五档单调 ⇎ 针的独有按份分账=总数 ⇎ 段独有+交集=段词表 ⇎ 大写=裸+NOT ⇎ 两把语气尺逐份同值 ⇎
# 档数×间隔=该段跨度 ⇎ 组数−非空行=被标签粘走的行 ⇎ 本遍壳−采集壳=两侧多判之差 ⇎ 换算的地板计数 ⇎
# 锚 single+cross+all5=去重数)全归零送门槛重算。
# 不可由在库文件判定的: 五份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 821/1123 此刻被标 Historic 还是 Current、Exim 与 Postfix 此刻的默认参数、现网 MTA 实际怎么排重试——
# 只进解读注, 不进门槛。
def _b74_scan():
    import io, re, itertools as IT, glob, json as _js
    from collections import Counter, defaultdict
    P4 = SRC['B74']
    NSRC = 5
    LBL = [u'821', u'1123', u'5321', u'exim', u'postfix']
    TAGS = LBL
    ISH = [False, False, False, True, True]
    PATH = P4
    NL = chr(10)
    F = {}
    LITK = {}
    IDX = dict((t, n) for n, t in enumerate(LBL))

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
assert BODYTXT.count(u'json.') == 1 and u'__import__(' in BODYTXT
BODYTXT = BODYTXT.replace(u'json.', u'_js.')
BODYTXT = BODYTXT.replace(u'print(', u'_sil(')
# 门内不给试针后门: B74PROBE 只在建条目那遍有意义, 门槛这一遍落空的锚必须立刻停机
BODYTXT = BODYTXT.replace(u"(u'B74PROBE' in __import__('os').environ)", u"(u'B74PROBE' in {})")
assert u'__import__' not in BODYTXT and u"_js.load" in BODYTXT
# _ev 原本是模块顶层函数, eval 看得见全局; 搬进 _b74_scan 后 F/CLOSE 只是闭包自由变量,
# eval 的默认命名域看不见闭包, 所以显式把复算 namespace 递进去(与建条目那遍同一套名字)。
EVSRC = u"eval(e.strip().replace(u'\\n', u''))"
assert BODYTXT.count(EVSRC) == 1, BODYTXT.count(EVSRC)
BODYTXT = BODYTXT.replace(EVSRC, u"eval(e.strip().replace(u'\\n', u''), "
                                u"dict(globals(), F=F, CLOSE=CLOSE, T=T, WIDE=WIDE, LBL=LBL, "
                                u"NSRC=NSRC, len=len, sum=sum, max=max, min=min, abs=abs, "
                                u"range=range, re=re, str=str, int=int, sorted=sorted))")

FLAT = json.load(io.open(u'corpus/_b74flat.json', encoding='utf-8'))
FAM = sorted({k.split(u'_')[0] for k in FLAT})


def fam(k):
    h = k.split(u'_')[0]
    return FAM.index(h) if h in FAM else len(FAM)


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


# 锚归属: 不读旁注, 从条目文件现推; txt 抛回原文件行, html 抛回剥标签后的组读数(两把尺同 FAN/ANSET)。
ANCH = u'''
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 五源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B74_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6(' + u'|'.join(TAGS) + u')\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B74: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B74: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B74: 标签嵌套'
    ERR = [x for x in CITES if not pnorm(x[1]) or pnorm(x[1]) not in FAN[IDX[x[0]]]]
    MISSLINE = [x for x in CITES if x[1] not in ANSET[IDX[x[0]]]]
    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [tuple(i for i in range(NSRC) if pnorm(a) and pnorm(a) in FAN[i]) for a in DIS]
    F[u'anchor_total'] = len(CITES)
    F[u'anchor_distinct'] = len(DIS)
    F[u'anchor_err'] = len(ERR)
    F[u'anchor_single'] = len([h for h in HC if len(h) == 1])
    F[u'anchor_cross'] = len([h for h in HC if 1 < len(h) < NSRC])
    F[u'anchor_all5'] = len([h for h in HC if len(h) == NSRC])
    F[u'checks'] = len(DIS) * NSRC
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
    assert all(len(h) < NSRC for h in HC), u'一句答话不可能五份同源'
'''

SILH = u'    def _sil(*a):' + NL + u'        pass' + NL


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


NS0 = {'SRC': {'B74': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
CALL = u"    return F" + NL + NL + u"_B74 = _b74_scan()" + NL
_run(HEAD + SILH + BODYTXT + ANCH + CALL, u'<b74 probe>', NS0)
_probe = NS0[u'_B74']
MISS = [k for k in sorted(FLAT) if k not in _probe]
for k in MISS:
    SKIP.add(k)
print(u'门内跳过的非复算键 %d 枚: %s' % (len(MISS), MISS))

BLK = HEAD + SILH + BODYTXT + ANCH + gen_asserts() + u'    return F' + NL + NL + \
    u"_B74 = _b74_scan()" + NL + \
    u"B74V = lambda k, i=None: (_B74[k] if i is None else _B74[k][i])" + NL + NL + \
    u"# ---- B74 DERIV (generated by corpus/_wire74.py from corpus/_deriv74.json; do not hand-edit) ----" + NL
J = json.load(io.open(u'corpus/_deriv74.json', encoding='utf-8'))
BLK += u"DERIV['B74'] = " + repr(J) + NL + u"# ---- /B74 DERIV ----" + NL
compile(BLK, u'<b74 block>', u'exec')

# 幂等: 先摘掉上一版的整段 B74 区域(注释头 → 下一个 scan 调用锚), 再插新块。
i0 = S.find(MARK)
while i0 >= 0:
    nxt = -1
    for cand in ANCHOR_CANDS:
        k = S.find(NL + cand, i0)
        if k >= 0 and (nxt < 0 or k < nxt):
            nxt = k
    assert nxt >= 0, u'anchor scan'
    S = S[:i0] + S[nxt + 1:]
    i0 = S.find(MARK)
if u'B74V=B74V' in S:
    S = S.replace(u'B74V=B74V,' + NL, NL)
ME = re.search(u"(?m)^(\\s*)(B7\\dV=B7\\dV)\\)$", S)
assert ME, u'anchor env'
S = S[:ME.end(2)] + u',\n' + ME.group(1) + u'B74V=B74V' + S[ME.end(2):]

SRCBLK = (u"SRC['B74'] = ['corpus/raw/mailRetry/rfc821.txt', 'corpus/raw/mailRetry/rfc1123.txt',\n"
          u"              'corpus/raw/mailRetry/rfc5321.txt',\n"
          u"              'corpus/raw/mailRetry/exim4_retry_spec.html',\n"
          u"              'corpus/raw/mailRetry/postfix_postconf5.html']\n"
          u"ATOM.add('B74')\nHTMLSRC.add('B74')\n\n\n")
assert u"SRC['B74']" not in S and u"HTMLSRC.add('B74')" not in S
SPOT = -1
for cand in ANCHOR_CANDS:
    k = S.find(NL + cand)
    if k >= 0:
        SPOT = k + 1
        break
assert SPOT >= 0, u'anchor splice'
S = S[:SPOT] + SRCBLK + BLK + NL + S[SPOT:]
compile(S, u'<audit.py wired>', u'exec')

NS = {'SRC': {'B74': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob, 'DERIV': {}}
_run(BLK, u'<b74 block>', NS)
env = NS['B74V']
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
        got = eval(v, dict(NS), {'B74V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b73_scan' in S and u'_b74_scan' in S
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b74_scan+B74V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
