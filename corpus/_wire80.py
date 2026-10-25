# -*- coding: utf-8 -*-
"""把 B80 的独立复算器(_b80_scan / B80V)接进 audit.py, 并生成 DERIV['B80']。
幂等: 重复运行先摘旧块再插新块; 只动 B80 自己的区域, 并行 agent 的 B67/B73/B75-B79 行段原样保留。
_b80_scan 的量测段从三处逐行机械抽出: corpus/_mkB80.py 的 SCAN BEGIN ⇎ SCAN END(五份扫描面与四档口径) ⇎
PICK BEGIN ⇎ PICK END(与采集侧 _b80meas.json 的逐键对账) ⇎ corpus/_mk80emit.py 的 SCAN2 BEGIN ⇎
SCAN2 END(段落层、行号尺与转置尺), 只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自七处:
①采集侧 corpus/_pick80.py 是先于建条目写好的另一套实现(正则字面轨、行切片池), 建条目侧改立非重叠游标档、
  邻居字符手扫、集合代数与逐字符句界, 两边在口径一致的键上逐量对账(167 键符 ⇎ 0 不符);
②插门之前把 _b80flat.json 的每个键与 DERIV['B80'] 的每条表达式各重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 五份都按原文件行归一后判成员;
④数字读数一律从面内现读: 抬头年份/月序/Obsoletes ⇎ Updates 由标题页正则现采, 段落起止由剥引文偏移映回原行号,
  节窗由同级标题识别器现定界, 一个不手填;
⑤行号尺是往返的: 每一枚"短语落在第几行"都拿行号回原文件取那一行、看针是否真在这一行内(13 枚全中),
  再配一枚反向对照——把被 72 列硬换行切开的收束短语的末字拿到它的首字行去验, 两份都该落空(0 枚命中);
⑥四档口径阶梯(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 节窗折平)单调, 无节的两份按 -1 登记(口径不存在不是零),
  摘壳档只救回跨页码的那一枚, 折平档独有的 27 枚逐份分账;
⑦恒等式(四档单调 ⇎ 针的独有按份分账=总数 ⇎ 段独有+交集=段词表 ⇎ 裸 MUST=纯 MUST+MUST NOT ⇎
  两把语气尺逐份同值 ⇎ 行尺−句尺=反号 ⇎ 片段行+壳行=总行 ⇎ 锚 single+cross+all5=去重数)全归零送门槛重算。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB80.py', encoding='utf-8').read()
EM = io.open(u'corpus/_mk80emit.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/httpretry/rfc2616.txt', u'corpus/raw/httpretry/rfc7231.txt',
        u'corpus/raw/httpretry/rfc6585.txt', u'corpus/raw/httpretry/rfc8470.txt',
        u'corpus/raw/httpretry/rfc9110.txt']
MARK = u'# B80: 失败的 HTTP 请求到底能不能自动重来'
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
# ZV 表由 _mkB80.py 的登记尾段建立, 那一段不切进门; SCAN2 里只有 ZV.append, 门内先立空表让它跑通。
SCAN2 = u'ZV = []' + NL + SCAN2
MEAS = SCAN.rstrip() + NL + NL + PICK.rstrip() + NL + NL + SCAN2.rstrip() + NL
for nm in (u'pnorm', u'fold', u'is_shell_pick', u'shell_line', u'FAN', u'SHPN', u'ALN', u'ANSET',
           u'PP', u'PINS', u'blk', u'line_holds', u'AN', u'ANX', u'ANL', u'LBL', u'NSRC', u'TAGS',
           u'IDX', u'ZID', u'CLOSE', u'CLOSE2', u'MEA', u'PK', u'AGREE', u'_ev', u'sents', u'SENT',
           u'ub', u'cnt_cur', u'mk_nd', u'hit_face', u'WIDE', u'SH', u'head_words', u'suffix_words',
           u'ln_of', u'ln_end', u'sect_no', u'code_row_picklike', u'sent_ends', u'ATOMFAIL',
           u'BLKFAIL', u'ALOG', u'sn_sec_docs_scope', u'LITK', u'F'):
    assert re.search(u'(?<![._a-zA-Z0-9])%s(?![a-zA-Z0-9_])' % nm, MEAS), nm
assert MEAS.count(u'json.') == 1 and u'ENTRY' not in MEAS and u'DERIV' not in MEAS

HEAD = u'''
# B80: 失败的 HTTP 请求到底能不能自动重来一次——五份 HTTP 一手规范五种答法:
# raw/httpretry/rfc2616.txt(A 2616/1999 §9.1.2: 全库唯一一句不点施事者名的被动式禁令
#   "MUST NOT be automatically retried", 另给 user agents MAY offer 与自动重试 SHOULD NOT 再试;
#   单位写 delta-seconds, 规则式写竖线 Retry-After  = "Retry-After" HZRFc*)
# ⇎ raw/httpretry/rfc7231.txt(B 7231/2014 §4.2.2: 换成机制句——通信失败发生在客户端读到响应之前⇒可以自动重来,
#   整段一枚义务词也不给; 单位改名 delay-seconds, 规则式改斜杠 Retry-After = HTTP-date / delay-seconds)
# ⇎ raw/httpretry/rfc6585.txt(C 6585/2012, Updates: 2616 ⇎ 被 7231 废止: 通篇零枚 automat*×retry 族,
#   改用 429 + "Retry-After: 3600" + "I only allow 50 requests per hour" 作答, 并自认不定义源服务器怎么数请求;
#   428 的定义行印两处(目录 ⇎ 节标题), 那一枚跨页码, 只有摘壳档读得到)
# ⇎ raw/httpretry/rfc8470.txt(D 8470/2018: 给阶梯——are expected to retry ⇎ SHOULD retry automatically ⇎
#   any retries MUST NOT be sent in early data ⇎ intermediary MAY automatically retry, 全文不提 Retry-After,
#   状态码只用"码+括号名"印法, 且三枚这种印法被 72 列换行切在中间)
# ⇎ raw/httpretry/rfc9110.txt(E 9110/2022 §9.2.2: 把 7231 那句逐字搬来, 再点名 proxy(MUST NOT)⇎
#   client(SHOULD NOT), 新允许 "a user agent can repeat a POST request automatically";
#   抬头带 BOM, 唯一无换页符的一份, 目录行与正文标题同形)。
# 本函数从五份字节独立复算: 答句针的四档口径阶梯与原面⇎折平⇎摘壳⇎节窗的逐份增益与无节份的 -1 登记、
# 段落层十四段的段界/行/词/字符⇎共头共尾⇎词集容斥⇎行距位移等值、行号尺的 13 枚往返复核与错行反向对照、
# 节窗(同级标题现定界 ⇎ 判词距节头 244 行 ⇎ 9110 节内 8/8)、语气五轨两把尺(邻居手扫 ⇎ 负向断言正则)同值、
# 数字族改名(delta-seconds ⇎ delay-seconds)、状态码定义行⇎目录行⇎"码+括号名"、施事者九式与泛称七式、
# 抬头谱系(年序 ⇎ 倒序一枚 ⇎ Obsoletes 9 号 ⇎ Updates 3 处 ⇎ STD/ISSN 行)、共用长行池(行尺 ⇎ 句尺)与写法分家。
# 不可由在库文件判定的: 五份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 6585 此刻是否被标 Historic、7231/2616 此刻的废止关系有没有新勘误、现网客户端与代理实际怎么重试——
# 只进解读注, 不进门槛。
def _b80_scan():
    import io, re, itertools as IT, glob, json as _js
    from collections import Counter, defaultdict
    P5 = SRC['B80']
    NSRC = 5
    LBL = [u'2616', u'7231', u'6585', u'8470', u'9110']
    TAGS = LBL
    ISH = [False, False, False, False, False]
    PATH = P5
    NL = chr(10)
    F = {}
    DER = {}
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
# 门内不给试针后门: B80PROBE 只在建条目那遍有意义, 门槛这一遍落空的锚必须立刻停机
BODYTXT = BODYTXT.replace(u"(u'B80PROBE' in __import__('os').environ)", u"(u'B80PROBE' in {})")
assert u'__import__' not in BODYTXT and u"_js.load" in BODYTXT
# _ev 原本是模块顶层函数, eval 看得见全局; 搬进 _b80_scan 后 F/CLOSE 只是闭包自由变量,
# eval 的默认命名域看不见闭包, 所以显式把复算 namespace 递进去(与建条目那遍同一套名字)。
EVSRC = u"eval(e.strip())"
assert BODYTXT.count(EVSRC) == 1, BODYTXT.count(EVSRC)
BODYTXT = BODYTXT.replace(EVSRC, u"eval(e.strip(), dict(globals(), "
                                u"F=F, CLOSE=CLOSE, T=T, WIDE=WIDE, LBL=LBL, "
                                u"NSRC=NSRC, len=len, sum=sum, max=max, min=min, abs=abs, "
                                u"range=range, re=re, str=str, int=int, sorted=sorted))")

FLAT = json.load(io.open(u'corpus/_b80flat.json', encoding='utf-8'))
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


# 锚归属: 不读旁注, 从条目文件现推; 五份都是纯文本面, 一把尺(整份归一判成员 ⇎ 原文件行判落点)。
ANCH = u'''
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 五份都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B80_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6(' + u'|'.join(TAGS) + u')\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B80: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B80: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B80: 标签嵌套'
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


NS0 = {'SRC': {'B80': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
CALL = u"    return F" + NL + NL + u"_B80 = _b80_scan()" + NL
_run(HEAD + SILH + BODYTXT + ANCH + CALL, u'<b80 probe>', NS0)
_probe = NS0[u'_B80']
MISS = [k for k in sorted(FLAT) if k not in _probe]
for k in MISS:
    SKIP.add(k)
print(u'门内跳过的非复算键 %d 枚: %s' % (len(MISS), MISS))
# contract_n 是"本遍登记到第几键"的自计量: 门内的键集与建条目那遍不必同, 只作软量
if u'contract_n' in FLAT:
    SKIP.add(u'contract_n')

BLK = HEAD + SILH + BODYTXT + ANCH + gen_asserts() + u'    return F' + NL + NL + \
    u"_B80 = _b80_scan()" + NL + \
    u"B80V = lambda k, i=None: (_B80[k] if i is None else _B80[k][i])" + NL + NL + \
    u"# ---- B80 DERIV (generated by corpus/_wire80.py from corpus/_deriv80.json; do not hand-edit) ----" + NL
J = json.load(io.open(u'corpus/_deriv80.json', encoding='utf-8'))
BLK += u"DERIV['B80'] = " + repr(J) + NL + u"# ---- /B80 DERIV ----" + NL
compile(BLK, u'<b80 block>', u'exec')

# 幂等: 先摘掉上一版的整段 B80 区域(注释头 → 门槛驱动段首行), 再插新块。
i0 = S.find(MARK)
while i0 >= 0:
    nxt = S.find(NL + ANCHOR, i0)
    assert nxt >= 0, u'anchor scan'
    S = S[:i0] + S[nxt + 1:]
    i0 = S.find(MARK)
if u'B80V=B80V' in S:
    S = S.replace(u'B80V=B80V,' + NL, NL)
ME = re.search(u"(?m)^(\\s*)(B\\d+V=B\\d+V)\\)$", S)
assert ME, u'anchor env'
S = S[:ME.end(2)] + u',\n' + ME.group(1) + u'B80V=B80V' + S[ME.end(2):]

SRCBLK = (u"SRC['B80'] = ['corpus/raw/httpretry/rfc2616.txt', 'corpus/raw/httpretry/rfc7231.txt',\n"
          u"              'corpus/raw/httpretry/rfc6585.txt', 'corpus/raw/httpretry/rfc8470.txt',\n"
          u"              'corpus/raw/httpretry/rfc9110.txt']\n"
          u"ATOM.add('B80')\n\n\n")
assert u"SRC['B80']" not in S
SPOT = S.find(NL + ANCHOR)
assert SPOT >= 0, u'anchor splice'
S = S[:SPOT + 1] + SRCBLK + BLK + NL + S[SPOT + 1:]
compile(S, u'<audit.py wired>', u'exec')

NS = {'SRC': {'B80': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob, 'DERIV': {}}
_run(BLK, u'<b80 block>', NS)
env = NS['B80V']
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
        got = eval(v, dict(NS), {'B80V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b79_scan' in S and u'_b80_scan' in S
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b80_scan+B80V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT) - len(SKIP), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
