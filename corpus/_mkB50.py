# -*- coding: utf-8 -*-
"""B50 建条目: 同一模型 ⇎ 六个领域的难题思维链(六源对照)。
每个数字都现算并登记进 DERIV(键=该数值, 值=audit.py 里 B50V 的复算式); 每个锚由 _pick50.py 从推理区逐字截出。
零值一律折进 '0' 键(所有零项之和); 同数的不同含义记进 _b50checks.json 供 ⛓解读注列出。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = u'corpus'
ENTRY = u'%s/babeltele/B50_one_model_six_domains.md' % C
M = json.load(io.open(os.path.join(ROOT, C, u'_b50meas.json'), encoding='utf-8'))
SLUGS, TAGS = M[u'slugs'], M[u'tags']
LB = dict(zip(TAGS, [u'数论', u'肾病', u'判例', u'信贷', u'炉管', u'震后']))
PATH = [u'%s/raw/cot/%s.md' % (C, s) for s in SLUGS]
NL = u'\n'
RD = lambda p: io.open(os.path.join(ROOT, p), encoding='utf-8').read()
FULL = [RD(p) for p in PATH]
HDR = [dict(re.findall(u'^(model|slug|prompt_sha256|reasoning_chars|answer_chars|retrieved): (.*)$', T, re.M)) for T in FULL]

def segR(i):
    a = FULL[i].find(u'## [[REASONING]]')
    b = FULL[i].find(u'## [[ANSWER]]', a)
    return FULL[i][a + 17:b].strip()
R = [segR(i) for i in range(6)]
assert [len(R[i]) for i in range(6)] == M[u'rcot'] == [int(HDR[i][u'reasoning_chars']) for i in range(6)]
CORE = [u'wait', u'actually', u'maybe', u'prob', u'assume', u'unsure', u'verif', u'redo', u'wrong',
        u'therefore', u'however', u'must', u'caveat', u'final', u'quote', u'equality', u'unit', u'cfr', u'study']
assert len(CORE) == 19
for k in CORE + [u'restart_word', u'uncertain_word', u'bold', u'hmm', u'lets', u'letme', u'arrow']:
    assert len(M[k]) == 6
assert min(M[u'wait']) >= 1 and min(M[u'actually']) >= 1 and min(M[u'hmm']) >= 1
assert M[u'redo'] == [0] * 6 and M[u'acot'] == [0] * 6
SHAOK = 0
for i in range(6):
    pa = FULL[i].find(u'## [[PROMPT]]')
    pf = FULL[i][pa + 14:FULL[i].find(u'\n\n## [[REASONING]]', pa)]
    if hashlib.sha256(pf.encode('utf-8')).hexdigest()[:16] == HDR[i][u'prompt_sha256']:
        SHAOK += 1
assert SHAOK == M[u'sha_ok'] == 6, SHAOK
ATOMS = M[u'atomlist']
assert sum(len(v) for v in ATOMS.values()) == M[u'anchor_total'] == 54

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
    expr = u"B50V('%s'%s)" % (key, u'' if i is None else u', %d' % i)
    reg(s, expr, note or u'%s%s' % (key, u'' if i is None else u'[%d]' % i))
    return s
def PL(key, i, note=u''):
    s = repr(round(10000.0 * M[key][i] / M[u'rcot'][i], 1))
    reg(s, u"round(10000.0*B50V('%s',%d)/B50V('rcot',%d),1)" % (key, i, i), note)
    return s
def L6(key, label):
    return u' ⇎ '.join(V(key, i, u'%s·%s' % (label, LB[t])) for i, t in enumerate(TAGS))
def A(tag, *needles):
    got = [x for x in ATOMS[tag] if all(n in x for n in needles)]
    assert len(got) == 1, (tag, needles, len(got))
    return got[0]
def AT(tag, *n):
    return u'⟦%s⟧⟨%s⟩' % (tag, A(tag, *n))

G = {}
G[u'nsrc'] = V(u'nsrc', None, u'源数')
G[u'n6'] = V(u'hashes', None, u'题面哈希种数')
G[u'nm'] = V(u'models', None, u'模型串写法数')
G[u'mbare'] = V(u'model_bare', None, u'去前缀后模型种数')
G[u'sha'] = V(u'sha_ok', None, u'题面哈希自校验命中')
G[u'np'] = V(u'npats', None, u'核心模式数')
G[u'retr'] = V(u'retr', None, u'抓取时刻组数')
G[u'gap'] = V(u'gap', 0, u'两种区段口径之差')
G[u'pr0'] = V(u'praw', 0, u'题面·哈希覆盖字符')
G[u'pc0'] = V(u'pcot', 0, u'题面·去空白后字符')
G[u'pgap'] = V(u'pgap', None, u'题面·两种口径之差')
G[u'flip'] = V(u'flip', None, u'名次翻转模式数')
G[u'allpos'] = V(u'allpos', None, u'六源皆有的核心模式数')
G[u'sixz'] = V(u'sixzero', None, u'六源皆空的核心模式数')
G[u'ntail'] = V(u'tailbad', None, u'末字符非句终的段数')
G[u'nat'] = V(u'anchor_total', None, u'注册锚数')
G[u'ndist'] = V(u'anchor_distinct', None, u'注册锚去重')
G[u'cross'] = V(u'cross', None, u'跨源命中的锚数')
G[u'checks'] = V(u'checks', None, u'成员检查次数')
G[u'rc'] = L6(u'rcot', u'推理区字符')
G[u'pc'] = L6(u'pcot', u'题面字符')
G[u'fc'] = L6(u'fchars', u'文件字符')
G[u'fb'] = L6(u'fbytes', u'磁盘字节')
G[u'rcsum'] = V(u'rcotsum', None, u'六段推理总字符')
G[u'rcratio'] = V(u'rcratio', None, u'最长段⇎最短段之比')
G[u'eq'] = L6(u'equality', u'等号')
G[u'eqp'] = u' ⇎ '.join(PL(u'equality', i, u'等号每万字') for i in range(6))
G[u'w'] = L6(u'wait', u'Wait')
G[u'ac'] = L6(u'actually', u'actually')
G[u'h'] = L6(u'hmm', u'Hmm')
G[u'cfr'] = L6(u'cfr', u'条款词')
G[u'must'] = L6(u'must', u'must')
G[u'bold'] = L6(u'bold', u'粗体对')
G[u'ar'] = L6(u'arrow', u'箭头')
G[u'un'] = L6(u'unsure', u'明说不确定')
G[u'ma'] = L6(u'maybe', u'maybe')
G[u'qu'] = L6(u'quote', u'引号回述')
G[u'ut'] = L6(u'unit', u'单位记号')
G[u'ns'] = L6(u'numsent', u'带数句子')
G[u'rest'] = L6(u'restart_word', u'restart 词形')
G[u'unc'] = L6(u'uncertain_word', u'uncertain 词形')
G[u'lm'] = L6(u'letme', u'let me')
G[u'ls'] = L6(u'lets', u'let\'s')
G[u'se'] = L6(u'sent', u'句子数')
G[u'pa'] = L6(u'para', u'非空段数')
G[u'fi'] = L6(u'final', u'结论标记')
G[u'an0'] = V(u'acot', 0, u'回答区字符')
G[u'ma0'] = V(u'maybe', 0, u'maybe·数论')
G[u'ma3'] = V(u'maybe', 3, u'maybe·信贷')
G[u'map0'] = PL(u'maybe', 0, u'maybe 每万字·数论')
G[u'map3'] = PL(u'maybe', 3, u'maybe 每万字·信贷')
G[u'eq2'] = V(u'equality', 2, u'等号·判例')
G[u'cfr0'] = V(u'cfr', 0, u'条款词·数论')
G[u'cfr1'] = V(u'cfr', 4, u'条款词·炉管')
G[u'must1'] = V(u'must', 1, u'must·肾病')
G[u'bold0'] = V(u'bold', 0, u'粗体·数论')
G[u'ar2'] = V(u'arrow', 2, u'箭头·判例')
G[u'un0'] = V(u'unsure', 1, u'明说不确定·肾病')
G[u'fin0'] = V(u'final', 0, u'结论标记·数论')
G[u'lm2'] = V(u'letme', 2, u'let me·判例')
G[u'ls2'] = V(u'lets', 2, u"let's·判例")
G[u'qu3'] = V(u'quote', 3, u'引号回述·信贷')
G[u'un5'] = V(u'unsure', 5, u'明说不确定·震后')
G[u'unc5'] = V(u'uncertain_word', 5, u'uncertain 词形·震后')

LINES = []
G[u'lw'] = u'、'.join(M[u'lastw'])
G[u'apn'] = u'、'.join(M[u'allpos_names'])
G[u'szn'] = u'、'.join(M[u'sixzero_names'])
G[u'fpn'] = u'、'.join(M[u'flip_names'])

def LINE(em, tmpl, **kw):
    LINES.append((em + u' ' + tmpl).format(**kw))

LINE(u'🧭', u"体例 {aM} ‖ {aD} ‖ {aL} ‖ {aF} ‖ {aI} ‖ {aS} ⇒ 六个源不是六份材料, 是同一台机器在六道难题上的六次运行: "
            u"模型串有两种写法(带 `opencode/` 前缀 ⇎ 不带), 去掉前缀后是 {mbare} 种; 题面哈希 {n6} 种, 其中 {sha}/{nsrc} 枚能在“空行分节”的口径下逐字节复算命中; "
            u"抓取时刻 {retr} 组。区段有三套长度: 题面字符 {pc} ⇎ 推理区字符 {rc} ⇎ 回答区 {an0} 字符(六段皆空); 整份文件 {fc} 字符 ⇎ 磁盘 {fb} 字节。"
            u"本库已有同题 ⇎ 换模型的对照(B27/B36), 这条把箭头反过来: 同模型 ⇎ 换题, 于是“哪些推理习惯属于机器、哪些属于题目”成了可数的对照。",
     aM=AT(u'M', u'We need solve math problem'), aD=AT(u'D', u'We need answer clinical reasoning'),
     aL=AT(u'L', u'All tools disabled'), aF=AT(u'F', u'Websearch disabled'),
     aI=AT(u'I', u'We need answer complex forensic'), aS=AT(u'S', u'We need answer forensic structural'), **G)

LINE(u'✂️', u"六段思维链全部断在半句上 {aM} ‖ {aD} ‖ {aS} ⇒ 六个推理区的最后一个词是 {lw}: "
            u"{ntail}/{nsrc} 段不以句子终符收尾, 而回答区六段实测各 {an0} 字符。头部自报与区段实长一致, 但“按节标直找”与“按空行分节”两种口径恒差 {gap} 个字符(两端各一枚换行)——"
            u"题面也有两套: 哈希覆盖含末尾换行的 {pr0} 字符, 报出来的长度是去掉首尾空白的 {pc0}, 恒差 {pgap}。"
            u"报数时不写口径, 这些数就会看着像几个不同的长度。后果是一条纪律: 这批原料只能证明模型怎样想, 不能证明它最后答了什么; "
            u"连“结论”这个词都不站在源里——final/conclusion/recommend 一类计数是 {fi}, 其中两段的计数为 {fin0}, 而那两段的区段末尾也确实断在推导中间。",
     aM=AT(u'M', u'S is extrem'), aD=AT(u'D', u'reabsorbs'), aS=AT(u'S', u'base hinge governs over diagonal'), **G)

LINE(u'🔁', u"自我修正只用三个词, 而且从不重来 {aM} ‖ {aD} ‖ {aL} ‖ {aI} ⇒ 同一台机器在六个领域里打断自己的方式高度一致: "
            u"Wait {w} ⇎ actually {ac} ⇎ Hmm {h}, 三样在六段里都至少出现一次; 核心 {np} 条模式里有 {allpos} 条六源皆有。"
            u"反过来, redo/start over/let me recompute 一类“推倒重来”的说法在六段里是 {z6}: 修正永远是一句“等一下”追加在后面, 不清账。"
            u"两处词形口径必须点名。其一, 数 restart 会误判: {rest}, 非零那一段的六枚全在说装置本身重启({aI2}), 与推理重来无关; "
            u"其二, 只按 not sure/unclear/I think 数“承认不确定”会得 {un}, 而 uncertain 一族是 {unc}, 其中震后段明说 {un5} 次、词形 {unc5} 次——同一件事的两种词形, 模式写窄了就整段漏掉。",
     aM=AT(u'M', u'Wait ab/(a+b)'), aD=AT(u'D', u'Wait, how does Gitelman'), aL=AT(u'L', u'Wait: If both are English law'),
     aI=AT(u'I', u'Wait 6 weeks plus 11 days'), aI2=AT(u'I', u'restart after 21-day'),
     z6=u' ⇎ '.join(V(u'redo', i, u'推倒重来·%s' % LB[t]) for i, t in enumerate(TAGS)), **G)

LINE(u'🧮', u"写不写算式是领域习惯 {aM} ‖ {aF} ‖ {aI} ‖ {aS} ⇒ 等号密度 {eq}, 归一到每万字是 {eqp}: 数论段每万字一枚接一枚, "
            u"判例段一整篇 {eq2} 枚都不写, 肾病段 {eqp1} 枚。工程两段的因果链用箭头而不是等号: -> 计数 {ar}(判例与信贷两段是 {ar2}), 单位记号 {ut}, 带数字的句子 {ns}。"
            u"判词: “这台机器会不会做算术”是题目的函数而不是机器的函数; 跨领域比风格时必须先把记号除上长度, 否则写得长的那段永远看着更勤快。",
     aM=AT(u'M', u'reciprocal integer?'), aF=AT(u'F', u'480/36 = 13.3333'),
     aI=AT(u'I', u'D = t1/L1'), aS=AT(u'S', u'Residual storey drift'),
     eqp1=PL(u'equality', 1, u'等号每万字·肾病'), **G)

LINE(u'📜', u"义务词、条款号与粗体只长在有权威的地方 {aL} ‖ {aF} ‖ {aL2} ‖ {aS} ⇒ 条款词 article/section/§/clause/paragraph: {cfr}, "
            u"其中数论与肾病两段为 {cfr0} ⇎ 炉管段也是 {cfr1}; must: {must}, 肾病段 {must1}、炉管段同样为零; "
            u"markdown 粗体对 {bold}——只有判例与信贷两段用, 数论段是 {bold0}。"
            u"检索腔与计算腔也分得开: let me {lm} ⇎ let's {ls}, 判例段把 let me 用 {lm2} 次而 let's 只 {ls2} 次, 因为它在往记忆里查案名({aL3}), 别段在往下算。"
            u"题面没给权威时它就不引用权威; 题面给了条款号时它把条款号抄进推理里({aF2}), 甚至怀疑题面自己抄错了单位({aF3})。",
     aL=AT(u'L', u'Hague Judgments Convention'), aL2=AT(u'L', u'issue estoppel was governed by'),
     aL3=AT(u'L', u'Let me recall'), aS=AT(u'S', u'we must rule'),
     aF=AT(u'F', u'12 CFR 32'), aF2=AT(u'F', u'12 CFR 32'), aF3=AT(u'F', u'unit error'), **G)

LINE(u'❓', u"犹豫的形状: 泛化的 maybe ⇎ 少见的自认 {aM} ‖ {aD} ‖ {aS} ⇒ maybe/perhaps {ma} 六段皆有, 是这台机器最便宜的 hedge; "
            u"明说不确定(not sure/unclear/I think)则是 {un}。两者的比在六段里差得最远: 数论段 maybe {ma0} 次而明说不确定 {un_math} 次(推不动只叫 Hmm), "
            u"震后段 maybe {ma5} 次、认 {un5} 次, 而且它把“不认”写进判决({aSP})。"
            u"引号回述题面与原文的密度 {qu}: 信贷段 {qu3} 处为六段最高, 它靠把题面措辞抄回来找漏洞({aF}); 法条段的回述则是把待引的案名原样括出来({aL4})。",
     aM=AT(u'M', u'Try small n'), aD=AT(u'D', u'urine Cl 104 eliminates'), aS=AT(u'S', u'cannot reject is punching shear'),
     aSP=AT(u'S', u'not rejected until verified'), aF=AT(u'F', u'premise is wrong'),
     aL4=AT(u'L', u'Kookmin Bank'), ma5=V(u'maybe', 5, u'maybe·震后'),
     un_math=V(u'unsure', 0, u'明说不确定·数论'), **G)

LINE(u'📏', u"长度是混淆项: 原始计数与每万字归一会翻名次 {aD} ‖ {aI} ⇒ 句子数 {se} ⇎ 非空段数 {pa}。"
            u"核心 {np} 条模式里, 按原始计数排第一的领域与按每万字排第一的领域不一致的有 {flip} 条({fpn})。"
            u"maybe 那一例最直白: 信贷段原始 {ma3} 枚高于数论段 {ma0} 枚, 归一后反而是数论段每万字 {map0} ⇎ 信贷段 {map3}。"
            u"而推理区长度本身最长段是最短段的 {rcratio} 倍(六段合计 {rcsum} 字符, 各段 {rc}), 所以本条每个“谁更怎样”的说法都带口径二字——"
            u"只抄原始计数就等于把“写得长”读成“想得多”。",
     aD=AT(u'D', u'Need enumerate every cause'), aI=AT(u'I', u'Need no tools really'), **G)

LINE(u'⚖', u"怎么把“机器的习惯”与“题目的习惯”分开 {aL} ‖ {aS} ⇒ 三步。"
            u"① 先钉住不变量: 同一模型(去前缀 {mbare} 种)、同一抓取器、同一区段口径({nsrc} 段哈希 {sha}/{nsrc} 自校验)。"
            u"② 再对每个候选习惯问“六格是不是都≥1”: 六源皆有的核心模式 {allpos} 条({apn}), 六源皆空的 {sixz} 条({szn})——这两列才是机器常量。"
            u"③ 剩下的算领域函数: 等号在判例段 {eq2}、条款词在数论段 {cfr0}、粗体在数论段 {bold0}、must 在肾病段 {must1}、明说不确定在肾病段 {un0}。"
            u"锚的可核性也走六源: 注册 {nat} 条(去重 {ndist} 条), 每条只在标注那一段逐字命中, 跨源命中的 {cross} 条, 共 {checks} 次成员检查——"
            u"六段都以“We need …/… disabled.”起手, 若锚只取半句套话, 对照立刻被共享套话抹平。",
     aL=AT(u'L', u'training data'), aS=AT(u'S', u'Need work, not clean conclusion'), **G)

LINE(u'∴', u"骨架 ⇒ ① 同一模型六道难题, 推理区 {rc} ⇎ 回答区六段 {an0}; "
           u"② 六段末字符全非句终({ntail}/{nsrc}), 故“结论”不在源内; "
           u"③ 打断自己的三个词六段皆有: Wait {w} ⇎ actually {ac} ⇎ Hmm {h}; ④ 推倒重来六段皆零({z6b}); "
           u"⑤ 等号 {eq}; ⑥ 条款词 {cfr}; ⑦ must {must}; ⑧ 粗体 {bold}; ⑨ 箭头 {ar}; ⑩ 明说不确定 {un}; ⑪ 引号回述 {qu}; "
           u"⑫ 核心 {np} 条模式中六源皆有 {allpos} 条、皆空 {sixz} 条, 原始计数与每万字归一名次不一致 {flip} 条。"
           u"判词: 思维链的“风格”可拆两层——跨题不变的词法习惯(打断、hedge、不重来)属机器, 记号选择(等号、条款号、粗体、箭头)属题目; "
           u"两层混谈就会把“这道题是数学”误读成“这个模型会数学”。",
     z6b=u' ⇎ '.join(V(u'redo', i, u'推倒重来·%s' % LB[t]) for i, t in enumerate(TAGS)), **G)

LINE(u'ℒ', u"方法 ⇒ 读这种六源矩阵先读口径再读内容: 区段怎么切(空行分节 ⇎ 标记直找, 恒差 {gap} 字符)、模型串算几种({nm} 种写法 ⇎ {mbare} 种实体)、回答区算不算文本(六段 {an0})。"
            u"然后把每个候选习惯摊成六格, 只问三种问题: 六格全正(机器常量)、六格全零(机器从不做)、有零有正(领域函数); 不问“哪段更有条理”这类没有分母的话。"
            u"第三步给每个计数配一个归一版本, 并公布两者名次不一致的模式数({flip})。第四步核验锚互斥: 每条锚原子只允许命中其标注那一段(注册 {nat} 条, 跨源 {cross} 条)。"
            u"第五步记住原料是被切断的中间态: 任何“模型最终认为”的句子都该退回源里找, 找不到就删。", **G)

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 六段推理区合计 {rcsum} 字符(各段 {rc}, 最长是最短段的 {rcratio} 倍), 而摘要只能取锚点触到的窗口: "
            u"注册 {nat} 条(去重 {ndist} 条)锚各触一段; 正文引用了几处、漏引几枚, 那些是工具侧计数, 写在 ⛓解读注里才算得准。"
            u"本条的结论不住在窗口里——“等号密度差三个数量级”“推倒重来六段皆零”“粗体只在两段出现”是六格矩阵上的形状, 要整段复算才看得见, 截若干行原文看不到。"
            u"读它请按“哪几格为零、哪几格为正”来读, 而不是按“少说了多少原文”。", **G)

body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
DIST = len(set(re.findall(u'⟨([^⟨⟩]+)⟩', body)))
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
REGS = set(x.strip() for x in io.open(os.path.join(ROOT, C, u'_atoms50.txt'), encoding='utf-8').read().split(NL) if x.strip())
AS_ = set(x.strip() for x in ANCH)
UNCITED = len(REGS - AS_)
assert not [x for x in AS_ if x not in REGS], [x for x in AS_ if x not in REGS][:2]
DERIV = dict((k, v[0]) for k, v in K.items())
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(os.path.join(ROOT, C, u'_deriv50.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
CH = {u'anchor_total': M[u'anchor_total'], u'used': USED, u'distinct': DIST, u'uncited': UNCITED,
      u'tag_counts': TAGN, u'collisions': dict((k, sorted(set(v))) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV), u'sha_ok': SHAOK, u'notes': NOTES,
      u'redo_zero': M[u'redo'] == [0] * 6, u'maxmin': [max(M[u'rcot']), min(M[u'rcot'])],
      u'enc_chars': len(body.replace(NL, u''))}
json.dump(CH, io.open(os.path.join(ROOT, C, u'_b50checks.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

SRCBITS = []
for i in range(6):
    SRCBITS.append(u'%s (推理区 %s 字符 ⇎ 题面 %s ⇎ 回答 %s)' % (
        PATH[i], V(u'rcot', i, u'推理区字符·%s' % LB[TAGS[i]]),
        V(u'pcot', i, u'题面字符·%s' % LB[TAGS[i]]),
        V(u'acot', i, u'回答区字符·%s' % LB[TAGS[i]])))
srcline = u'src: ' + u' ⇎ '.join(SRCBITS) + u' (sha256 见各文件头部, 六枚互不相同)\n'
联结 = (u'；联结不是“同一份材料的三种载体”, 而是“同一台机器的六个断面”: 六段出自同一模型(串 {nm} 种写法)、六道互不相干的难题(题面哈希 {n6} 种), '
        u'回答区六段皆空而推理区六段全断在半句上; 可核性走六格矩阵——六格全正者属机器, 有零有正者属题目, 每个数由 audit.py 的 B50V 从六份 raw 整段复算\n').format(**G)
text = (u'# B50 同一模型 ⇎ 六个领域的难题思维链：会打断自己是机器的习惯，会写等号是题目的习惯\n' + srcline + 联结 +
        u'tags: 六格矩阵 同模型⇎换题 区段三口径 截断即口径 就地打补丁从不重来 记号密度=领域函数 每万字归一翻名次 '
        u'权威词只在有权威处 粗体分域 检索腔⇎计算腔 六源互斥锚 词形口径漏项 restart假阳性 回答区为空\n' +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill50.py 从 corpus/_b50checks.json 与 corpus/_b50meas.json 现算写入）\n')
io.open(os.path.join(ROOT, ENTRY), 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body)))
print(u'锚 注册 %d ⇎ 正文 %d 处／%d 串／未引用 %d ｜ 每标签 %s' % (M[u'anchor_total'], USED, DIST, UNCITED, TAGN))
print(u'DERIV %d 键(0 键折 %d 个零项) ｜ 同数冲突 %d 组' % (len(DERIV), len(ZERO), len(COLL)))
for k in sorted(COLL)[:12]:
    print(u'  同数 %s ← %s' % (k, COLL[k]))
print(u'残留未替换占位符 %d' % len(re.findall(u'\\{[a-z]', body)))
