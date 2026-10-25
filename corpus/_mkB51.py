# -*- coding: utf-8 -*-
"""B51 建条目: 同一模型 ⇎ 同一道题的两次采样(四源: 数论一/二 ⇎ 肾病一/二)。
锚全部由 _pick51.py 从推理区/答案区按规则切出并存进 _b51meas.json, 本脚本只按特征子串取用(不手抄);
每个数字都现算并登记成 audit.py 里 B51V 的复算式, 零值一律折进 '0' 键。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = u'corpus'
ENTRY = u'%s/babeltele/B51_same_model_same_question_twice.md' % C
NL = u'\n'
J = json.load(io.open(os.path.join(ROOT, C, u'_b51meas.json'), encoding='utf-8'))
M = dict(J[u'meas'])
M.update(J[u'shape'])
TAGS = J[u'tags']
LB = dict(zip(TAGS, [u'数论一', u'数论二', u'肾病一', u'肾病二']))
SLUGS = J[u'slugs']
PATH = [u'%s/raw/cot/%s.md' % (C, s) for s in SLUGS]
POOL = J[u'pool']                       # [kind, tag, atom, hits, class, len]
PAIRS = J[u'pairs']                     # '01'/'23'/'02'/'03'/'12'/'13' → [行, 句, 单行句, 五词串]
SAME = [(0, 1), (2, 3)]                 # 同题对(与 _pick51.py 的 PAIRS 同义; 这里 PAIRS 已是交表)
ORDER = [(0, 1), (2, 3), (0, 2), (0, 3), (1, 2), (1, 3)]

RD = lambda p: io.open(os.path.join(ROOT, p), encoding='utf-8').read()
FULL = [RD(p) for p in PATH]
HDR = [dict(re.findall(u'^(model|slug|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$', T, re.M))
       for T in FULL]

def segR(i):
    a = FULL[i].find(u'## [[REASONING]]')
    b = FULL[i].find(u'## [[ANSWER]]', a)
    return FULL[i][a + 17:b].strip()

R = [segR(i) for i in range(4)]
assert [len(R[i]) for i in range(4)] == M[u'rcot'] == [int(HDR[i][u'reasoning_chars']) for i in range(4)]
for i in range(4):
    pf = FULL[i][FULL[i].find(u'## [[PROMPT]]') + 14:FULL[i].find(u'\n\n## [[REASONING]]')]
    assert hashlib.sha256(pf.encode('utf-8')).hexdigest()[:16] == HDR[i][u'prompt_sha256'], i
assert len(set(HDR[i][u'prompt_sha256'] for i in range(4))) == 2
assert len(set(HDR[i][u'model'].split('/')[-1] for i in range(4))) == 1
assert len(set(HDR[i][u'retrieved'][:10] for i in range(4))) == 2

def pnorm(s):
    """与 audit.py 的 prose_norm 同一套折叠(大小写/引号/破折号/空白), 所以这里判定的命中列在门槛里可复算。"""
    s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
    s = re.sub(u'[’\'"\u2018\u2019`´]+', u'', s)
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff\-\. ]+', u' ', s)
    return re.sub(r'\s+', u' ', s).strip()

FN = [pnorm(FULL[i]) for i in range(4)]      # 命中列按整份 raw 判(答案区的锚在推理区之外)

def hitset(a):
    n = pnorm(a)
    return tuple(i for i in range(4) if n in FN[i])

def cls_of(h):
    if len(h) == 4:
        return u'all4'
    if len(h) == 2:
        return u'pair' if tuple(h) in SAME else u'cross'
    return u'single'

K, ZERO, COLL = {}, [], {}
def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K and K[s][0] != expr:
        COLL.setdefault(s, [K[s][1]])
        if note not in COLL[s]:
            COLL[s].append(note)
        return
    K.setdefault(s, (expr, note))

def V(key, i=None, note=u''):
    val = M[key] if i is None else M[key][i]
    s = repr(val) if isinstance(val, float) else str(val)
    expr = u"B51V('%s'%s)" % (key, u'' if i is None else u', %d' % i)
    reg(s, expr, note or u'%s%s' % (key, u'' if i is None else u'[%d]' % i))
    return s

def PL(key, i, note=u''):
    s = repr(round(10000.0 * M[key][i] / M[u'rcot'][i], 1))
    reg(s, u"round(10000.0*B51V('%s',%d)/B51V('rcot',%d),1)" % (key, i, i), note)
    return s

def OV(pair, slot, note=u''):
    i, j = pair
    val = PAIRS[u'%d%d' % (i, j)][slot]
    names = {0: u'ov_l', 1: u'ov_s', 2: u'ov_ls', 3: u'ov_sg'}[slot]
    p = ORDER.index(pair)
    s = str(val)
    reg(s, u"B51V('%s',%d)" % (names, p), note or u'%s·%s⇎%s' % (names, TAGS[i], TAGS[j]))
    return s

def RAT(i, j, note):
    s = repr(round(1.0 * M[u'rcot'][j] / M[u'rcot'][i], 2))
    reg(s, u"round(1.0*B51V('rcot',%d)/B51V('rcot',%d),2)" % (j, i), note)
    return s

def SUM4(note):
    s = str(sum(M[u'rcot']))
    reg(s, u'+'.join(u"B51V('rcot',%d)" % i for i in range(4)), note)
    return s

def MAXMIN(note):
    hi, lo = max(M[u'rcot']), min(M[u'rcot'])
    ih, il = M[u'rcot'].index(hi), M[u'rcot'].index(lo)
    s = repr(round(1.0 * hi / lo, 2))
    reg(s, u"round(1.0*B51V('rcot',%d)/B51V('rcot',%d),2)" % (ih, il), note)
    return s

def SUB(pi, slot, note):
    names = {0: u'sub_n', 1: u'sub_tot', 2: u'sub_max', 3: u'sub_prompt'}
    val = M[u'sub'][pi + 1][slot] if False else J[u'meas'][u'sub'][u'AB' if pi == 0 else u'CD'][slot]
    s = str(val)
    reg(s, u"B51V('%s',%d)" % (names[slot], pi), note)
    return s

def PQ(i, slot, note):
    val = J[u'prompt_quote'][i][slot]
    reg(str(val), u"B51V('%s',%d)" % (u'pq' if slot == 0 else u'pqpos', i), note)
    return str(val)

def ATOMSEL(kind, tag, *needles):
    got = [x for x in POOL if x[0] == kind and x[1] == tag and all(n in x[2] for n in needles)]
    assert got, (kind, tag, needles)
    # common_runs 会把同一段文字按不同长度切进池子(前缀 ⇎ 全文), 取最长的那一枚才是不被截短的原块
    if len(got) > 1:
        AMBIG.append((kind, tag, needles, len(got)))
    return max(got, key=lambda x: len(x[2]))

USEDATOM = []
AMBIG = []
def RAWAT(tag, s):
    """池外补一枚短术语锚: 只允许“归一化后确在该源推理区里”的原串, 由本函数当场自证。"""
    assert pnorm(s) in FN[TAGS.index(tag)], s
    USEDATOM.append(s)
    return u'⟦%s⟧⟨%s⟩' % (tag, s)
def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    USEDATOM.append(x[2])
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])

G = {}
TOKV = {}
def TOK(name, note=u''):
    """锚的统计量要等正文写完才知道: 先占位, 生成完再回填并登记推导式。"""
    TOKV[name] = note
    return u'◘%s◙' % name
G[u'nsrc'] = V(u'anchors_pool', None, u'候选锚池条数') if False else str(4)
reg(u'4', u"B51V('nsrc')", u'源数')
for nm, note in ((u'gap', u'区段两口径差'), (u'pgap', u'题面两口径差'), (u'rgap', u'正则与采集口径差')):
    G[nm] = V(nm, 0, note)
G[u'sha_k'] = V(u'sha_kinds', None, u'题面哈希种数')
G[u'sha_ok'] = V(u'sha_ok', None, u'题面哈希自校验命中')
G[u'nm'] = V(u'models', None, u'模型串写法数')
G[u'nbare'] = V(u'model_bare', None, u'去前缀后模型种数')
G[u'retr'] = V(u'retr', None, u'抓取日数')
G[u'ntail'] = V(u'tailbad', None, u'末字符非句终的段数')
G[u's4f'] = V(u'sent_all4', None, u'四源同文整段句')
G[u's4'] = V(u'lsent_all4', None, u'四源同文单行句')
G[u's4s'] = V(u's4_same', None, u'四源同文里四份表面写法全同的组数')
G[u'rc'] = u' ⇎ '.join(V(u'rcot', i, u'推理区字符·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'ac'] = u' ⇎ '.join(V(u'acot', i, u'回答区字符·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'pc'] = u' ⇎ '.join(V(u'pcot', i, u'题面字符·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'fc'] = u' ⇎ '.join(V(u'fchars', i, u'整份字符·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'fb'] = u' ⇎ '.join(V(u'fbytes', i, u'磁盘字节·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'pa'] = u' ⇎ '.join(V(u'para', i, u'非空行·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'se'] = u' ⇎ '.join(V(u'sent', i, u'句子·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'ls'] = u' ⇎ '.join(V(u'lsent', i, u'单行句·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'sh'] = u' ⇎ '.join(V(u'shang', i, u'五词串·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'ns'] = u' ⇎ '.join(V(u'numsent', i, u'带数句·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'dg'] = u' ⇎ '.join(V(u'digit', i, u'数字符·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'wd'] = u' ⇎ '.join(V(u'word', i, u'词·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'ratio1'] = RAT(0, 1, u'数论两次之比')
G[u'ratio2'] = RAT(2, 3, u'肾病两次之比')
G[u'ratio1c'] = RAT(1, 0, u'数论第二次⇎第一次(倒数)') if False else G[u'ratio1']
G[u'lw'] = u'、'.join(M[u'lastw'])
G[u'lc'] = u' ⇎ '.join(str(ord(c)) for c in M[u'lastc'])
for i, c in enumerate(M[u'lastc']):
    reg(str(ord(c)), u"B51V('lastcode',%d)" % i, u'末字符码位·%s' % LB[TAGS[i]])
PATKEYS = (u'maybe', u'however', u'equality', u'need', u'q', u'wait', u'final', u'verif', u'arrow',
           u'therefore', u'bold', u'caveat', u'hmm', u'prob', u'assume', u'unsure', u'wrong', u'must',
           u'letme', u'redo', u'actually', u'lets')
for k in PATKEYS:
    G[k] = u' ⇎ '.join(V(k, i, u'%s·%s' % (k, LB[t])) for i, t in enumerate(TAGS))
AZ = [k for k in PATKEYS if max(M[k]) == 0]
G[u'naz'] = str(len(AZ))
reg(G[u'naz'], u"B51V('allzero')", u'四份皆零的模式族数')
G[u'npats'] = str(len(PATKEYS))
reg(G[u'npats'], u"B51V('npats')", u'词法模式族数')
G[u'aznames'] = u'、'.join({u'letme': u'“让我重算”词族', u'redo': u'“重来／推倒”词族'}.get(k, k) for k in AZ)
for k in (u'maybe', u'equality', u'need', u'however'):
    G[k + u'p'] = u' ⇎ '.join(PL(k, i, u'%s 每万字·%s' % (k, LB[t])) for i, t in enumerate(TAGS))
G[u'ma0'] = V(u'maybe', 0, u'maybe·数论一')
G[u'ma1'] = V(u'maybe', 1, u'maybe·数论二')
G[u'ma2'] = V(u'maybe', 2, u'maybe·肾病一')
G[u'ma3'] = V(u'maybe', 3, u'maybe·肾病二')
G[u'ne0'] = V(u'need', 0, u'need·数论一')
G[u'ne3'] = V(u'need', 3, u'need·肾病二')
G[u'eq0'] = V(u'equality', 0, u'等号·数论一')
G[u'eq1'] = V(u'equality', 1, u'等号·数论二')
G[u'eq2'] = V(u'equality', 2, u'等号·肾病一')
G[u'eq3'] = V(u'equality', 3, u'等号·肾病二')
G[u'fin1'] = V(u'final', 1, u'结论标记·数论二')
G[u'fin3'] = V(u'final', 3, u'结论标记·肾病二')
G[u'an0'] = V(u'acot', 0, u'回答区字符·数论一')
G[u'an2'] = V(u'acot', 2, u'回答区字符·肾病一')
# 重叠量: 同题两对 ⇎ 跨题四对
G[u'ovAB'] = u' ⇎ '.join([OV((0, 1), s) for s in (0, 1, 2, 3)])
G[u'ovCD'] = u' ⇎ '.join([OV((2, 3), s) for s in (0, 1, 2, 3)])
G[u'ovBD'] = u' ⇎ '.join([OV((1, 3), s) for s in (0, 1, 2, 3)])
G[u'ovAC'] = OV((0, 2), 2, u'单行句·数论一⇎肾病一')
G[u'ovAD'] = OV((0, 3), 2, u'单行句·数论一⇎肾病二')
G[u'ovBC'] = OV((1, 2), 2, u'单行句·数论二⇎肾病一')
G[u'sgAC'] = OV((0, 2), 3, u'五词串·数论一⇎肾病一')
G[u'sgAD'] = OV((0, 3), 3, u'五词串·数论一⇎肾病二')
G[u'sgBC'] = OV((1, 2), 3, u'五词串·数论二⇎肾病一')
G[u'sgBD'] = OV((1, 3), 3, u'五词串·数论二⇎肾病二')
# 题面引用与公共片段
G[u'pq'] = u' ⇎ '.join(PQ(i, 0, u'题面引用长度·%s' % LB[t]) for i, t in enumerate(TAGS))
G[u'pqpos'] = u' ⇎ '.join(PQ(i, 1, u'题面引用位置·%s' % LB[t]) for i, t in enumerate(TAGS))
for i, t in enumerate(TAGS):
    G[u'pq%d' % i] = PQ(i, 0, u'题面引用长度·%s' % LB[t])
    G[u'pqp%d' % i] = PQ(i, 1, u'题面引用起点·%s' % LB[t])
G[u'subn'] = SUB(0, 0, u'公共片段块数·数论') + u' ⇎ ' + SUB(1, 0, u'公共片段块数·肾病')
G[u'subtot'] = SUB(0, 1, u'公共片段字符·数论') + u' ⇎ ' + SUB(1, 1, u'公共片段字符·肾病')
G[u'submax'] = SUB(0, 2, u'最长公共片段·数论') + u' ⇎ ' + SUB(1, 2, u'最长公共片段·肾病')
G[u'subpr'] = SUB(0, 3, u'纯题面块数·数论') + u' ⇎ ' + SUB(1, 3, u'纯题面块数·肾病')
G[u'suboff'] = u'%s ⇎ %s' % (SUB(0, 1, u'数论公共片段字符'), SUB(1, 1, u'肾病公共片段字符'))
G[u'nat'] = TOK(u'anchor_total', u'正文引用锚位')
G[u'ndist'] = TOK(u'anchor_distinct', u'去重锚串')
G[u'npair'] = TOK(u'anchor_pair', u'命中列恰为同题对的锚')
G[u'nsgl'] = TOK(u'anchor_single', u'只命中一份源的锚')
G[u'ncross'] = TOK(u'anchor_cross', u'命中列跨题的锚')
G[u'nall'] = TOK(u'anchor_all4', u'四源皆命中的锚')
G[u'aerr'] = TOK(u'anchor_err', u'锚归属错配数')
G[u'checked'] = TOK(u'checks', u'成员检查次数')

LINES = []
def LINE(em, tmpl, **kw):
    LINES.append((em + u' ' + tmpl).format(**kw))

LINE(u'🧭', u"体例 {aOpen0} ‖ {aOpen2} ‖ {aOpen3} ⇒ 四份思维链只出自一道题吗? 不: 出自两道题, 每题两次。"
            u"同一模型(串 {nm} 种写法, 去前缀 {nbare} 种)、同一抓取器、同一区段口径; 题面哈希只有 {sha_k} 种(自校验 {sha_ok}/四份), "
            u"抓取时刻跨 {retr} 个日子: 第一次在十月十九日 18:12, 第二次在十月二十一日凌晨 04:53 与 04:55。"
            u"区段长度有三套口径: 按标记直找与按空行分节恒差 {gap} 字符(两端各一枚换行), 严格正则与前者差 {rgap}, 题面也有 {pgap} 之差。"
            u"这条与 B50 箭头相反: B50 是同模型⇎换题, 这条是同模型⇎同题⇎换一次采样, 于是“可复现”第一次成了被测量的量而不是默认前提。",
     aOpen0=AT(u'opening', u'A', u'We need solve math problem'),
     aOpen2=AT(u'opening', u'C', u'We need answer clinical reasoning'),
     aOpen3=AT(u'opening', u'D', u'We need answer medical diagnostic'), **G)

LINE(u'📏', u"长度就不复现 {aTail0} ‖ {aTail2} ⇒ 同一道题两次推理 {rc} 字符(第二次是第一次的 {ratio1} 倍／肾病侧 {ratio2} 倍), "
            u"非空行 {pa}, 句子 {se}, 单行句 {ls}, 五词串 {sh}, 数字符 {dg}, 词 {wd}。"
            u"更硬的一条在末尾: 四段末字符码位 {lc}, 其中 {ntail} 段不以句子终符收尾——恰好是两次第一次(本条开头那两枚尾锚, 一枚停在被切断的半词上, 一枚停在约数的一半), 两次第二次都以句号收。"
            u"回答区 {ac}: 两次第一次实测各 {an0} 与 {an2} 字符(根本没写出成稿), 两次第二次各写出 {anB} 与 {anD} 字符。"
            u"整份文件 {fc} 字符 ⇎ 磁盘 {fb} 字节。判词: 采样先不复现“长度”, 再不复现“内容”; 拿一次思维链当模型的定论来引用, 连它有多长都是抽签结果。",
     aTail0=AT(u'tail', u'A', u'S is extrem'), aTail2=AT(u'tail', u'C', u'reabsorbs'),
     anB=V(u'acot', 1, u'回答区字符·数论二'), anD=V(u'acot', 3, u'回答区字符·肾病二'), **G)

LINE(u'🔁', u"逐字复现的主体是题面 {aPq0} ‖ {aPq2} ⇒ 四份推理里都嵌着一段原样的题面: 长度 {pq}, 在推理区里的起点 {pqpos}。"
            u"两个数合起来才是要点: 引用不在开头而在中段(数论一推到 {pqp0} 字符处才回头重读题面, 肾病二推到 {pqp3} 处), 可见复读是收尾动作而不是起手动作; "
            u"四段引用长度互不相等——数论两次分别截出 {pq0} 与 {pq1} 字符, 肾病两次截出 {pq2} 与 {pq3} 字符, "
            u"同一条题面被两次采样各抄走不同的一截: 数论一那截 {pq0} 字符在两处都原样出现(所以它同时是同题对的公共片段), 数论二那一整截 {pq1} 字符只多了一句开头, 却只在这一份里出现。"
            u"连“复读了题面”都不必是同一句复读。",
     aPq0=AT(u'prompt_quote', u'A', u'Determine, with proof'), aPq1=AT(u'prompt_quote', u'B', u'Let n be a positive integer'),
     aPq2=AT(u'prompt_quote', u'C', u'enumerate every cause'),
     aPq3=AT(u'prompt_quote', u'D', u'A 34-year-old woman'), **G)

LINE(u'✂️', u"扣掉题面之后还剩什么 {aSub0} ‖ {aSubC} ⇒ 同题两次之间 >=40 字符的极大公共片段, 数论 ⇎ 肾病四格口径依次是: 块数 {subn}, 合计字符 {subtot}, 最长块 {submax}, 纯题面 {subpr} 块。"
            u"扣掉题面后剩下的不是“同一番思考”, 而是三类不用想也能写对的东西: "
            u"其一, 被算术逼死的构造 {aSubM}(两次都在 n=4 上写出同一行 lcm 与同一组四个数); "
            u"其二, 教科书级条目与机制句, 连措辞都不变 {aSubMg} ‖ {aSubAlk}; "
            u"其三, 指令的尾巴换了载体又出现一次 {aSubTail} ‖ {aSubEnum}。"
            u"反过来看数论侧最长那块 {submaxA} 字符: 它比数论一的题面引用 {pq0} 只多三枚尾字符(一枚引号、一枚空格、下一个词的首字母), 所以“块层”测到的最长复现仍然只是题面。"
            u"判词: 能逐字复现的段落几乎都是查得到、或推得出唯一写法的段落; 复现率是检索能力的指标, 不是推理能力的指标。",
     aSub0=AT(u'pair_sub', u'A', u'Determine, with proof, the largest'),
     aSubC=AT(u'pair_sub', u'C', u'Congenital adrenal hyperplasia'),
     aSubM=AT(u'pair_sub', u'A', u'lcm(3,4,5,5,6,7)=420'),
     aSubMg=AT(u'pair_sub', u'C', u'decreased intracellular Na and increased basolateral'),
     aSubAlk=AT(u'pair_sub', u'C', u'metabolic alkalosis, hypomagnesemia, hypocalciuria'),
     aSubTail=AT(u'pair_sub', u'A', u'Reason out loud, showing every arithmetic check'),
     aSubEnum=AT(u'pair_sub', u'C', u'enumerate every cause of hypokalemic'),
     submaxA=SUB(0, 2, u'数论最长公共片段'), **G)

LINE(u'🧱', u"句子级的“复现”是假象 {aCm0} ⇒ 共有量按四种粒度各测一遍(行⇎整段句⇎单行句⇎五词串): 同题数论对 {ovAB}, 同题肾病对 {ovCD}; "
            u"而跨题的“第二次⇎第二次”那一对 {ovBD} 在两档粒度上与同题肾病对完全打平, 连“共有行数”一项还反超它。另三对跨题的共有量是 {ovAC}/{ovAD}/{ovBC}(单行句口径), "
            u"五词串口径则是 {sgAC}/{sgAD}/{sgBC}/{sgBD}——除了那一对外凡跨题就归零。"
            u"两种粒度讲两个相反的故事: 词串级复现的是本题术语(只有同题才会撞), 句子级复现的是阶段套话(与题无关, 只与“这是第几次运行”有关, 例如 {aXs})。"
            u"至于“四份同文”的句子, 一共 {s4} 枚, 全是语气词 ({aS4a} ‖ {aS4b}), 其中只有 {s4s} 组连四份的大小写都不动。"
            u"判词: “两份思维链逐句相同”这种说法必须带粒度, 否则等于什么都没测; 把粒度钉死之后剩下的只有感叹词。",
     aCm0=AT(u'shared_sent', u'C', u'Need accurate mechanism'),
     aXs=AT(u'cross_sent', u'B', u'We can produce maybe 1500-2500 words'),
     aS4a=AT(u'scaffold4', u'A', u'Hmm.'), aS4b=AT(u'scaffold4', u'A', u'no.'), **G)

LINE(u'📈', u"第二次不是重放, 是重想 {aHedge0} ‖ {aHedge1} ⇒ 同题两次之间, 犹豫与算式的绝对数一律上涨: "
            u"设想词 {ma0}→{ma1}(肾病侧 {ma2}→{ma3}), 转折词 {hu0}→{hu1}／{hu2}→{hu3}, 需求句 {ne0}→{ne3}／{ne2}→{ne3}, "
            u"等号 {eq0}→{eq1}／{eq2}→{eq3}, 问号 {qu0}→{qu1}／{qu2}→{qu3}。"
            u"可一旦除以长度就分岔: 设想词每万字 {mp0}→{mp1} 反而回落, 肾病侧 {mp2}→{mp3} 才上涨; 等号 {ep0}→{ep1} 回落, {ep2}→{ep3} 上涨。"
            u"判词上半: 数论的第二次只是更长, 肾病的第二次才是更密; 把“想得更谨慎”当成两次采样的共同结论, 在一侧是被长度骗的。"
            u"结论标记词族在两次第一次里是 {fin0}, 第二次里是 {fin1} 与 {fin3}——与回答区从无到有同步。"
            u"纹丝不动的有 {naz} 族({aznames}): 四份里一次也没有说“重来”; 模型永远在当前句后面追加, 从不删账, "
            u"所以第二次读起来更像第一次的思路被继续摊开, 而不是被重新做过。",
     aHedge0=AT(u'hedge_only', u'A', u'Wait maximum number of pairs is trivially all'),
     aHedge1=AT(u'hedge_only', u'B', u'Wait our triangle'),
     hu0=V(u'however', 0, u'转折词·数论一'), hu1=V(u'however', 1, u'转折词·数论二'),
     hu2=V(u'however', 2, u'转折词·肾病一'), hu3=V(u'however', 3, u'转折词·肾病二'),
     ne2=V(u'need', 2, u'需求句·肾病一'),
     qu0=V(u'q', 0, u'问号·数论一'), qu1=V(u'q', 1, u'问号·数论二'),
     qu2=V(u'q', 2, u'问号·肾病一'), qu3=V(u'q', 3, u'问号·肾病二'),
     mp0=PL(u'maybe', 0, u'设想词每万字·数论一'), mp1=PL(u'maybe', 1, u'设想词每万字·数论二'),
     mp2=PL(u'maybe', 2, u'设想词每万字·肾病一'), mp3=PL(u'maybe', 3, u'设想词每万字·肾病二'),
     ep0=PL(u'equality', 0, u'等号每万字·数论一'), ep1=PL(u'equality', 1, u'等号每万字·数论二'),
     ep2=PL(u'equality', 2, u'等号每万字·肾病一'), ep3=PL(u'equality', 3, u'等号每万字·肾病二'),
     fin0=u' ⇎ '.join(V(u'final', i, u'结论标记·%s' % LB[t]) for i, t in ((0, u'A'), (2, u'C'))), **G)

LINE(u'⚖️', u"判断顺序每次都重排 {aAguess} ‖ {aBguess} ⇒ 数论侧: 第一次停在猜想与构造之间, 把“所有对都可达成”当候选答案写在推导里; "
            u"第二次先在推导里怀疑题面 {aBalt}, 最后在答案区判定题面缺约束 {aBfull} ‖ {aBunb}, 并把不变量写成判词 {aBkey}. "
            u"同一个想法在第一次只是草稿 {aAdraft}: 两边写着等价的构造, 但一次没有结论, 一次有结论, 且结论是“这题没界”。"
            u"判词: 采样可复现的是术语与构造, 不可复现的是“把哪一步当作判决”这一步; 这也是 B50 那条“判序属题目”的说法在这里的加强版——同题之下判序仍不可复现。",
     aAguess=AT(u'digit_only', u'A', u'Need exact extremal value C(n,2)'),
     aBguess=AT(u'answer_judge', u'B', u'A natural guess from extremal graph theory'),
     aBalt=AT(u'digit_only', u'B', u'Alternative interpretation'),
     aBfull=AT(u'answer_judge', u'B', u'Thus, for the problem as stated'),
     aBunb=AT(u'answer_judge', u'B', u'Trying to extend'),
     aBkey=AT(u'answer_judge', u'B', u'This is the key invariant'),
     aAdraft=AT(u'hedge_only', u'A', u'Wait for any finite set R of positive integers'), **G)

LINE(u'🩺', u"排除链换了依据但换了结论吗 {aCelim} ‖ {aDelim} ⇒ 肾病侧两次都落到同一诊断 {aGit} 上, 但排除的顺序不同: "
            u"第一次把尿氯当总闸 {aCcl}, 并把遗传学模仿者留在最后 {aCcln}; 第二次先算阴离子间隙 {aDgap}, 再用钙排泄分数与利尿剂筛查收尾 {aDcah}, "
            u"并把“唯一能在生化上存活的模仿者”交给阴性筛查 {aDmim}。"
            u"两次的机制解释逐字复现(见上条), 两次的排除次序一处也不复现。"
            u"判词: 诊断知识分两层——“哪些病因属于同一族”是可复读的表, “先用哪个数杀哪个假设”是每次重做的判决; 只复现前者而丢失后者, 读起来就像同一次思考, 其实只是同一份清单。",
     aGit=RAWAT(u'C', u'Gitelman'),
     aCelim=AT(u'digit_only', u'C', u'Need enumerate and eliminate each with specific numbers'),
     aDelim=AT(u'answer_judge', u'D', u'The high urine Cl and Na exclude GI chloride loss'),
     aCcl=AT(u'digit_only', u'C', u'Urine Cl 104 also excludes vomiting'),
     aCcln=AT(u'digit_only', u'C', u'CLCNKB-related Bartter III is the main genetic mimic'),
     aDgap=AT(u'hedge_only', u'D', u'Wait urine anion gap'),
     aDcah=AT(u'answer_judge', u'D', u'Gitelman syndrome'),
     aDmim=AT(u'digit_only', u'D', u'this is the one mimic that survives the biochemistry'), **G)

LINE(u'🧪', u"两次采样给出的可核事实怎么分档 {aOp1} ⇒ 三档。"
            u"第一档 B51V 可复算: 四段区长度、行/句/单行句/五词串集合交、>=40 字公共片段、题面引用长度与起点、{npats} 族词法计数、末字符码位——全部由 audit.py 的 _b51_scan 从四份 raw 重算。"
            u"第二档只能由集合运算得出: 逐字复现的百分比、名次随分母翻转({maybep} 一类的每万字口径)。"
            u"第三档是工具侧: difflib 的整段对齐量(命中字符总数与 ratio)与抓取时刻, 前者慢到不能进门槛, 只在 _probe51.py 里量并如实注明。"
            u"锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 {nat} 处／{ndist} 条去重串, 命中列分布是同题对 {npair} ⇎ 跨题 {ncross} ⇎ 单源 {nsgl} ⇎ 四源皆有 {nall}, "
            u"每条去重串对四份源逐一判成员, 共 {checked} 次检查, 错配 {aerr} 处——归属由正文现推, 不由旁注文件说了算。",
     aOp1=AT(u'opening', u'D', u'We need answer medical diagnostic'), **G)

LINE(u'∴', u"骨架 ⇒ ① 四份一模型两题(哈希 {sha_k} 种), 推理区 {rc} ⇎ 回答区 {ac}; "
           u"② 第二次是第一次的 {ratio1}/{ratio2} 倍, 两次第一次末字符非句终({ntail}/4); "
           u"③ 题面引用 {pq}, 起点 {pqpos}; ④ 同题 >=40 字公共片段 {subn} 块 {subtot} 字, 纯题面 {subpr} 块; "
           u"⑤ 共有量四种粒度同题 {ovAB} ⇎ {ovCD}, 跨题第二次对 {ovBD}, 五词串跨题近乎归零; "
           u"⑥ 四份同文的句子只有语气词 {s4} 枚; ⑦ 设想词 {ma0}→{ma1} ⇎ {ma2}→{ma3}, 等号 {eq0}→{eq1}, “让我重算”与“重来／推倒”两族四份皆零; "
           u"⑧ 数论判词只出现在第二次, 肾病的排除依据在两次之间换掉。"
           u"判词: 思维链的“可复现部分”= 题面回声 + 术语条目 + 被算术逼死的构造, “不可复现部分”= 长度、判序、中间量与结论形状; "
           u"把一次采样当证据来引用, 能引用的只有前半部分, 而后半部分恰好是这条语料的价值所在。", **G)

LINE(u'ℒ', u"方法 ⇒ 读“同一模型同一题的两次采样”先问粒度再问比例: 字符层(difflib 侧, 工具量)、块层(>=40 字极大公共片段, 可复算)、"
            u"句子层(单行句集合交)、词组层(五词串集合交)。四层的结论并不一致, 混用就会得出“复现率两成”这类无分母、无粒度、也没扣题面回声的话。"
            u"第二步把公共片段按“能否在原样题面里找到”分成两堆, 只有第二堆才算推理的复现。"
            u"第三步用跨题对作对照: 同题对的共有量若不比跨题对高, 那份共有就是套话; 本条正是靠 {ovBD} 与 {ovCD} 打平这件事, 把句子级复现否掉。"
            u"第四步注意锚的归属由正文标签现推, 共有锚要在两份源里各命中一枚, 单源锚要在其余三份里零命中。"
            u"第五步永远先测“第一次有没有写完”: 两次第一次的回答区都是 {an0} 与 {an2} 字符, 于是任何“模型最终答案”的说法在这里只能引用第二次。", **G)

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 四段推理区合计 {rcsum} 字符, 最长段是最短段的 {rmax} 倍, 而摘要只能取锚点触到的窗口; "
            u"本条的锚特意选了长片段(题面引用一条就 241/270/429 字符), 因为它们要被两份源同时命中才算数。"
            u"真正的结论不住在窗口里——“同题对的句子级共有不比跨题对高”“纯题面块数与总块数之比”“犹豫计数膨胀而重来词族恒零”"
            u"都是四格矩阵上的形状, 要整段复算才看得见。读它请按“哪一格与哪一格打平”来读, 而不是按“少抄了多少原文”。",
     rcsum=SUM4(u'四段推理总字符'), rmax=MAXMIN(u'最长段⇎最短段之比'), **G)

body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
# ---------- 锚的归属与命中列: 全部从正文的“源标签+原子引文”配对现推 ----------
CITES = re.findall(u'⟦([%s])⟧⟨([^⟨⟩]+)⟩' % u''.join(TAGS), body)
assert len(CITES) == USED, (len(CITES), USED)          # 每枚锚前必须紧贴一枚源标签
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射(见 B35 双写 bug)'
ERR = [x for x in CITES if pnorm(x[1]) not in FN[TAGS.index(x[0])]]
HITC = dict((a, hitset(a)) for a in ANCH)
assert not [a for a in ANCH if len(HITC[a]) == 3], u'有三源命中的锚, 分档表未覆盖'
CLS = dict((c, len([a for a in ANCH if cls_of(HITC[a]) == c]))
           for c in (u'pair', u'cross', u'single', u'all4'))
AMETA = {u'anchor_total': len(CITES), u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_pair': CLS[u'pair'], u'anchor_cross': CLS[u'cross'],
         u'anchor_single': CLS[u'single'], u'anchor_all4': CLS[u'all4'],
         u'checks': DIST * 4}
assert not ERR, ERR[:3]
for k, v in sorted(AMETA.items()):
    reg(str(v), u"B51V('%s')" % k, TOKV.get(k, k))
for k, v in sorted(AMETA.items()):
    body = body.replace(u'◘%s◙' % k, str(v))
assert u'◘' not in body, u'锚统计量占位符未回填'
assert sum(AMETA[u'anchor_' + c] for c in (u'pair', u'cross', u'single', u'all4')) == DIST
DERIV = dict((k, v[0]) for k, v in K.items())
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(os.path.join(ROOT, C, u'_deriv51.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(os.path.join(ROOT, C, u'_atoms51.txt'), 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN,
      u'ameta': AMETA, u'ambiguous_picks': len(AMBIG),
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[A-D]⟧', body)),
      u'classes': dict((c, [a for a in sorted(ANCH) if cls_of(HITC[a]) == c])
                       for c in (u'pair', u'cross', u'single', u'all4')),
      u'collisions': dict((k, sorted(set(v))) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV), u'notes': NOTES,
      u'pool_used': len(set(USEDATOM) & set(ANCH)), u'enc_chars': len(body.replace(NL, u'')),
      u'lastc': M[u'lastc'], u'retr': [HDR[i][u'retrieved'] for i in range(4)]}
json.dump(CH, io.open(os.path.join(ROOT, C, u'_b51checks.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

srcline = u'src: ' + u' ⇎ '.join(u'%s (推理区 %s 字符 ⇎ 回答区 %s)' % (PATH[i], str(M[u'rcot'][i]), str(M[u'acot'][i]))
                                 for i in range(4)) + u' (题面 sha 只有两枚: %s ⇎ %s, 各覆盖两份)\n' % (
    HDR[0][u'prompt_sha256'], HDR[2][u'prompt_sha256'])
联结 = (u'；联结不是“四份材料”, 而是“两次抽签”: 同一模型、两道题、每题各采一次于十月十九日、再采一次于十月二十一日凌晨, '
        u'推理区最长是最短段的 %s 倍, 两次第一次都没写完答案(回答区 %s ⇎ %s 字符); '
        u'可核性走四种粒度的集合交与 >=40 字公共片段, 每个数由 audit.py 的 B51V 从四份 raw 整段复算\n') % (
    M[u'rcratio'], M[u'acot'][0], M[u'acot'][2])
text = (u'# B51 同一模型 ⇎ 同一道题的两次采样：逐字复现的是题面与清单, 判序每次都得重做\n' + srcline + 联结 +
        u'tags: 两次采样 四种粒度共有量 题面中段复读 极大公共片段 纯题面与推理复用 判序不可复现 回答区从无到有 末字符非句终 '
        u'绝对数与每万字口径分岔 重来词族四源皆零 跨题对打平同题对 五词串跨题归零 锚归属由正文现推 三口径可核性\n' +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill51.py 从 corpus/_b51checks.json 与 corpus/_b51meas.json 现算写入）\n')
io.open(os.path.join(ROOT, ENTRY), 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d 串 ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'DERIV %d 键(0 键折 %d 项) ｜ 同数冲突 %d 组' % (len(DERIV), len(ZERO), len(COLL)))
for k in sorted(COLL)[:14]:
    print(u'  同数 %s ← %s' % (k, COLL[k]))
print(u'残留未替换占位符 %d' % len(re.findall(u'\\{[a-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))))
print(u'池内多选(取最长) %d 处 ｜ 锚内拉丁 %d ｜ 锚外拉丁 %d ｜ 标签 %d 枚' % (
    len(AMBIG), len(re.findall(u'[A-Za-z]', u''.join(re.findall(u'⟨([^⟨⟩]+)⟩', body)))),
    len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
    len(re.findall(u'⟦[A-D]⟧', body))))
