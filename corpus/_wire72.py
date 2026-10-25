# -*- coding: utf-8 -*-
"""把 B72 的独立复算器(_b72_scan / B72V)接进 audit.py, 并生成 DERIV['B72']。
幂等: 重复运行先摘旧块再插新块; 只动 B72 自己的区域, 并行 agent 的 B65/B67/B69/B70/B71 行段原样保留。
_b72_scan 的量测段从 corpus/_mkB72.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间 ⇎
corpus/_mk72emit.py 的 SCAN2 BEGIN ⇎ SCAN2 END 之间逐行机械抽出, 只在头部换成 audit 自己的
路径常量与模块别名; 真正的独立性来自六处:
①采集侧 corpus/_pick72.py 是先于建条目写好的另一套实现(正则字面轨、按行取值档), 建条目侧改立
  非重叠游标档、集合代数档与四档口径阶梯(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 剥引文竖线折平),
  两边在口径一致的键上逐量对账(12 键符 ⇎ 0 不符);
②插门之前把 _b72flat.json 的每个键与 DERIV['B72'] 的每条表达式各重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 四源一律按归一串判成员;
④数字读数一律从面内现读: 30x 小节号由小节标题正则现采, 年份从标题页行尾读, 段落起止由剥引文偏移映回原行号,
  清单条目号 1..5 从两份注之间的顶层编号行现读, "is now deprecated" 的 305 归属按小节区间切片, 一个不手填;
⑤引文块这一层是显式的: dequote 只剥行首 `| ` 与行尾 `|`, 9110 的 "For historical reasons…MAY change"
  只在剥后面上读得到, 于是"序列化对照针"(带竖线那枚)与"内容针"分家, 最宽档落空 5 枚 = 反向对照 4 + 序列化对照 1;
⑥两遍壳谓词逐行对拍后把差分解到行(本遍多判 ⇎ 采集多判), 恒等式只允许由字面针与折面导出。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB72.py', encoding='utf-8').read()
EM = io.open(u'corpus/_mk72emit.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/httpRedir/rfc2616.txt', u'corpus/raw/httpRedir/rfc7231.txt',
        u'corpus/raw/httpRedir/rfc7538.txt', u'corpus/raw/httpRedir/rfc9110.txt']


def cut(src, a, b):
    i = src.index(a)
    j = src.index(b, i)
    return src[i:j]


MEAS = cut(MK, u'# --- SCAN BEGIN ---', u'# --- SCAN END ---')
MEAS = MEAS[MEAS.index(NL) + 1:]
MEAS2 = cut(EM, u'# --- SCAN2 BEGIN ---', u'# --- SCAN2 END ---')
MEAS2 = MEAS2[MEAS2.index(NL) + 1:]
MEAS = MEAS.rstrip() + NL + NL + MEAS2.rstrip() + NL
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
for nm in (u'pnorm', u'cnt_cur', u'dequote', u'ub', u'is_shell', u'shell_line', u'FOLD', u'SHF',
           u'QUOT', u'GN', u'SN', u'hit_face', u'Z', u'ZID', u'CLOSE', u'F', u'T', u'L', u'B',
           u'ln_of', u'AN', u'fmap', u'line_of', u'blk', u'IDX', u'TAGS', u'FAN', u'PTXT',
           u'pool_n', u'needle_n', u'dead_widest', u'mod_step_nums', u'tierq_may_change'):
    assert nm in MEAS, nm

HEAD = u'''
# B72: 收到 30x 之后 POST 到底能不能改成 GET——四份 HTTP 一手规范四种答法:
# raw/httpRedir/rfc2616.txt(A 2616/1999: 正文 "the user agent MUST NOT automatically redirect the request
#   unless it can be confirmed by the user"(确认门在本条里只此一份), 注释自认 "RFC 1945 and RFC 2068 specify
#   that the method is not allowed to change" 而 "some existing HTTP/1.0 user agents will erroneously change
#   it into a GET request"; 303 给的通往 GET 的正门是 "SHOULD be retrieved using a GET method")
# ⇎ raw/httpRedir/rfc7231.txt(B 7231/2014, Obsoletes: 2616 ⇎ Updates: 2817: 确认门整句不见, 换成
#   "Note: For historical reasons, a user agent MAY change the request method from POST to GET"; 307 才
#   "MUST NOT change the request method if the user does not confirm the redirect")
# ⇎ raw/httpRedir/rfc7538.txt(C 7538/2015, Obsoletes: 7238(自己的草案期号): 不争 302, 另立 308——
#   "it does not allow changing the request method from POST to GET", 又把使用限于 "the server has
#   sufficient confidence in the client's understanding"; 全篇只有 2 枚大写 MUST, 义务常用散文 ought to 写)
# ⇎ raw/httpRedir/rfc9110.txt(D 9110/2022, Obsoletes: 2818 7230 7231 7232 7233 7235 ⇎ Updates: 3864:
#   收下那句历史原因注(一字未动, 共尾 19 ⇎ 共头 19, 全篇唯一被楔进 "| *Note:*" 引文块的一种行——
#   带竖线面读 2 ⇎ 剥后 0), 另给叙述式 "eventually converged on changing the method" 与五条编号清单里第 4 条
#   "Change the request method according to the redirecting status code", 并顺手把 305 判 "is now deprecated")。
# 本函数从四份字节独立复算: 25 枚答句针的四档口径阶梯(原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 剥引文折平)、
# 六族"改写方法"说法在折平⇎剥引文两档的逐份读数与增益、30x 小节清单(8⇎7⇎1⇎9)与 304/308 的在场缺席、
# 数字 302/307/308 与 3xx 全族串的面枚数、9110 顶层编号清单 1..5 及改写条目是否落在区间内、"is now deprecated"
# 总数与其中属 305 的一枚、答句段的段界/行/词/字符与逐词共头共尾及词集容斥、段落语气与全篇语气四轨两账归零、
# Obsoletes ⇎ Updates 对象并集与链条、标题页年份/月序/倒序、引用三式与互引方向、答句邻域窗 ±band 五轨带内外、
# 共用长行池分档与六对(逐字节 ⇎ 仅归一)及写法分家四桶、序列化对照针与竖线两尺(字面尺 ⇎ 行尺)、
# 换页符/页壳/两遍壳谓词分解、BOM ⇎ 非 ASCII ⇎ 多余字节。
# 恒等式(四档单调 ⇎ 六族增益=剥引文新增针数 ⇎ 小节数=清单长度 ⇎ 段独有+交集=段词表 ⇎ 大写+小写=不分大小写 ⇎
# 裸+NOT+小写=全计 ⇎ 带内+带外=全篇 ⇎ Σ单份−Σ两两+Σ三三−Σ四份=并集 ⇎ 归一交=逐字节交+仅归一 ⇎ 分档之和=池条数 ⇎
# 独有+共有=词表 ⇎ 最宽档落空=反向对照+序列化对照 ⇎ 行距+其绝对值符号账 ⇎ 锚按标签账=按份数账)全归零送门槛重算。
# 不可由在库文件判定的: 四份的抓取时刻与磁盘 mtime 谁新谁旧、RFC Editor 此刻的现行状态页与勘误页、
# 2616/7231 此刻被标 Historic 还是 Current、此后是否又有勘误改动这几句、现网浏览器与客户端实际怎么改写方法——
# 只进解读注, 不进门槛。
def _b72_scan():
    import io, re, itertools, glob, hashlib as _hl
    from collections import Counter, defaultdict
    P2 = SRC['B72']
    NSRC = 4
    LBL = [u'2616', u'7231', u'7538', u'9110']
    TAGS = LBL
    YR = [u'99', u'14', u'15', u'22']
    PATH = P2
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
BODYTXT = re.sub(u'(?<![.\\w])hashlib\\.', u'_hl.', BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
BODYTXT = BODYTXT.replace(u'print(', u'_sil(')
EVSRC = u"eval(e.strip().replace(u'\\n', u''))"
assert BODYTXT.count(EVSRC) >= 1, BODYTXT.count(EVSRC)
BODYTXT = BODYTXT.replace(EVSRC, u"eval(e.strip().replace(u'\\n', u''), "
                                u"dict(globals(), F=F, CLOSE=CLOSE, NSRC=NSRC, "
                                u"len=len, sum=sum, max=max, min=min, abs=abs, range=range, re=re))")

ANCHORK = {u'anchor_total', u'anchor_distinct', u'anchor_err', u'anchor_single',
           u'anchor_cross', u'anchor_all4', u'checks', u'tag_2616', u'tag_7231',
           u'tag_7538', u'tag_9110', u'enc_chars', u'nsrc', u'contract_n'}
FLAT = json.load(io.open(u'corpus/_b72flat.json', encoding='utf-8'))
FAM = sorted({k.split(u'_')[0] for k in FLAT})


def fam(k):
    h = k.split(u'_')[0]
    return FAM.index(h) if h in FAM else len(FAM)


def lit(v):
    return repr(v).replace(u'u+', u'')


def gen_asserts(keys=None):
    ks = sorted([k for k in (keys if keys is not None else FLAT)
                 if k not in SKIP], key=lambda k: (fam(k), k))
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


# 结构横比由两处承担: 每个扁平键都按建条目侧落盘值逐一对账(gen_asserts),
# DERIV 的 176 条表达式在插门之前先预演一遍(下文的 J 循环); 这里不再另抄一份常数表。
HAND = u''


ANCH = u'''
    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 四源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B72_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'\\u27eaBabelTele\\u27eb' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'\\u27e6(' + u'|'.join(TAGS) + u')\\u27e7\\u27e8([^\\u27e8\\u27e9]+)\\u27e9', enc)
    assert CITES, u'B72: 正文里没有带标签的锚'
    assert len(re.findall(u'\\u27e8', enc)) == len(CITES), u'B72: 有锚没带源标签'
    assert re.findall(u'\\u27e7\\u27e8\\u27e6', enc) == [], u'B72: 标签嵌套'
    ERR = [x for x in CITES if not pnorm(x[1]) or pnorm(x[1]) not in [pnorm(y) for y in L[IDX[x[0]]]]]
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
    F[u'anchor_all4'] = len([h for h in HC if len(h) == NSRC])
    F[u'checks'] = len(DIS) * NSRC
    F[u'nsrc'] = NSRC
    F[u'enc_chars'] = len(enc.replace(NL, u''))
    for t in TAGS:
        F[u'tag_' + t] = len(re.findall(u'\\u27e6%s\\u27e7' % t, enc))
    assert F[u'enc_chars'] == 8503 and F[u'nsrc'] == 4
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all4'] == len(DIS)
    assert all(F[u'tag_' + t] > 0 for t in TAGS), u'有四源标签没锚'
    assert F[u'tag_2616'] == 6 and F[u'tag_7231'] == 3 and F[u'tag_7538'] == 8 and F[u'tag_9110'] == 6
    assert F[u'anchor_total'] == 23 and F[u'anchor_distinct'] == 17 and F[u'anchor_err'] == 0
    assert F[u'checks'] == 68 and F[u'anchor_all4'] == 0
    assert F[u'anchor_single'] == 13 and F[u'anchor_cross'] == 4
    assert all(len(h) < NSRC for h in HC)
    return F

_B72 = _b72_scan()
B72V = lambda k, i=None: (_B72[k] if i is None else _B72[k][i])
'''

# 采集侧对账段: 与 _mkB72.py 里 SCAN END 之后那段逐行同定义(换的是宿主——这里在 audit 的复算
# namespace 里重跑), 所以门内的 pick_* 键不是抄来的常数, 而是拿 _b72meas.json 与本轮现读量再对一次。
PICKTXT = u"""    import json as _js
    MEA = _js.load(io.open(u'corpus/_b72meas.json', encoding='utf-8'))
    AGREE = []
    DIFF = []
    for k in (u'bytes', u'chars', u'lines', u'nonblank', u'ff', u'cr', u'nonascii', u'bom', u'maxlen',
              u'byte_cp_delta', u'nonascii_extra', u'pipe_lines'):
        (AGREE if F[k] == MEA[k] else DIFF).append((k, F[k], MEA[k]))
    F['shell_pick_measured'] = MEA[u'shell_n']
    F['shell_close_vs_pick'] = [1 if F['shell_pick'][i] == MEA[u'shell_n'][i] else 0 for i in range(NSRC)]
    F['needle_table_pick'] = MEA[u'needle_n']
    F['needle_table_mk'] = F['needle_n']
    PKEY = dict((w, j) for j, w in enumerate(MEA[u'tier_pats']))
    SHARED = [(k, w) for k, w in TIER.items() if w in PKEY]
    F['tier_shared'] = sorted(w for k, w in SHARED)
    F['tier_shared_n'] = len(F['tier_shared'])
    F['tier_pick_only'] = sorted(w for w in MEA[u'tier_pats'] if w not in TIER.values())
    F['tier_mk_only'] = sorted(w for k, w in TIER.items() if w not in PKEY)
    TC = []
    for k, w in SHARED:
        j = PKEY[w]
        TC.append(1 if [MEA[u'tier_faces'][i][j] for i in range(NSRC)] == F[u'tierq_' + k] else 0)
    F['tier_cross_agree'] = TC
    F['tier_cross_n'] = len(TC)
    STRICT2 = F['sn_strict_docs']
    F['pick_vs_mk_ladder'] = [STRICT2, F['sn_fold_docs'], F['sn_sh_docs'], F['sn_quot_docs']]
    F['pick_ladder'] = [MEA[u'sn_strict_docs'], MEA[u'sn_fold_docs'], MEA[u'sn_sh_docs'], MEA[u'sn_quote_docs']]
    F['pick_agree'] = len(AGREE)
    F['pick_diff'] = len(DIFF) + (F['tier_cross_n'] - sum(F['tier_cross_agree']))
    assert sum(F['shell_close_vs_pick']) == NSRC, F['shell_close_vs_pick']
    assert sum(F['tier_cross_agree']) == F['tier_cross_n'], (F['tier_shared'], F['tier_cross_agree'])
    assert F['tier_shared_n'] == 4 and len(F['tier_pick_only']) == len(F['tier_mk_only']) == 2
    assert F['pick_diff'] == 0, (AGREE, DIFF)
    assert F['pick_agree'] == 12
    assert F['needle_table_pick'] == 24 and F['needle_table_mk'] == 25
    assert F['pick_ladder'][0] == [4, 3, 4, 7] and F['pick_vs_mk_ladder'][0] == [1, 1, 0, 2]
"""
# 先试跑一遍(不带扁平键断言), 找出只在建条目侧扫描段之外算出的键(对采集侧的横比、条目文件元数据):
# 这些键不在 audit 的复算 namespace 里成立, 门内如实跳过, 不假装核对。
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
NS0 = {'SRC': {'B72': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
_run(HEAD + SILH + BODYTXT + PICKTXT + HAND + ANCH, u'<b72 probe>', NS0)
_probe = NS0[u'_B72']
SKIP = set(ANCHORK)
MISS = []
for k in sorted(FLAT):
    if k in _probe:
        continue
    MISS.append(k)
    SKIP.add(k)
print(u'门内跳过的非复算键 %d 枚: %s' % (len(MISS), MISS))

ANCH_A, ANCH_B = ANCH.split(u'    return F')
BLK = (HEAD + SILH + BODYTXT + PICKTXT + HAND + ANCH_A
       + gen_asserts() + u'    return F' + ANCH_B)
compile(BLK, u'<b72 block>', u'exec')

assert S.count(NL + u"_B71 = _b71_scan()") == 1, u'anchor _b71_scan'
i0 = S.find(u'# B72: 收到 30x 之后 POST')
while i0 >= 0:
    i1 = S.index(u'_B71 = _b71_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B72: 收到 30x 之后 POST')
if u'B72V=B72V,' in S:
    S = S.replace(u'B72V=B72V,' + NL, NL)
S = S.replace(NL + u"_B71 = _b71_scan()", BLK + NL + u"_B71 = _b71_scan()")
if u'B72V=B72V' not in S:
    ME = re.search(u'B71V=B71V((?:,\\s*\\w+=\\w+)*)\\)', S)
    assert ME, u'anchor env'
    S = S[:ME.end(1)] + u',\n               B72V=B72V' + S[ME.end(1):]

PS = u"SRC['B71'] = ["
blk = (u"SRC['B72'] = ['corpus/raw/httpRedir/rfc2616.txt', 'corpus/raw/httpRedir/rfc7231.txt', "
       u"'corpus/raw/httpRedir/rfc7538.txt', 'corpus/raw/httpRedir/rfc9110.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
if u"'B72'" not in S:
    m = re.search(u'(?m)^ATOM = \\{(.*)\\}$', S)
    assert m and u"'B72'" not in m.group(1), u'anchor ATOM'
    S = S[:m.start(1)] + m.group(1) + u", 'B72'" + S[m.end(1):]

M1 = u'# ---- B72 DERIV (generated by corpus/_wire72.py from corpus/_deriv72.json; do not hand-edit) ----'
M2 = u'# ---- /B72 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o4 = u'# ---- B71 DERIV (generated by corpus/_wire71.py'
assert S.count(o4) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv72.json', encoding='utf-8'))
S = S.replace(o4, M1 + NL + u"DERIV['B72'] = " + repr(J) + NL + M2 + NL + o4)

NS = {'SRC': {'B72': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
try:
    exec(compile(BLK, u'<b72 block>', u'exec'), NS)
except AssertionError:
    import traceback
    tb = sys.exc_info()[2]
    while tb.tb_next:
        tb = tb.tb_next
    ls = BLK.split(NL)
    print(u'块内断言失败于第 %d 行:\n%s' % (tb.tb_lineno, ls[tb.tb_lineno - 1]))
    raise
env = NS['B72V']
BAD, MISMATCH = [], []


def deep(x):
    return [deep(y) for y in x] if isinstance(x, list) else list(x) if isinstance(x, tuple) else x


for k, v in FLAT.items():
    if k in SKIP:
        continue
    try:
        got = env(k)
    except Exception as e:
        BAD.append((k, repr(e)))
        continue
    if deep(got) != deep(v):
        MISMATCH.append((k, v, got))
assert not BAD, BAD[:6]
assert not MISMATCH, MISMATCH[:6]
for kk, v in J.items():
    try:
        got = eval(v, dict(NS), {'B72V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b71_scan' in S and u'_b72_scan' in S
compile(S, u'<audit.py wired>', u'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b72_scan+B72V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), len(J), env('anchor_total'), env('anchor_distinct'), env('checks')))
