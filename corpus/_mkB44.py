# -*- coding: utf-8 -*-
# B44 两序列化条: 同一篇文章(JATS/XML ⇎ 同端点去标记渲染文本)。内容层逐字相同, 差的全是标记与边界。
# 锚点从“空白折叠+剔 url 行”的正文切片(逐字由构造保证); 计数一律走 audit 的 _reason 口径(含 url 行)。
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')

RAWX = u'corpus/raw/prose/pmc_ards.xml'
RAWDS = u'corpus/raw/prose/pmc_ards_dad.txt'
ENTRY = u'corpus/babeltele/B44_jats_xml_vs_stripped_text_same_article.md'
LX, LD = u'X', u'D'
HEADRX = r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)'
CN = {0: u'零', 1: u'一', 2: u'两', 3: u'三', 4: u'四', 5: u'五', 6: u'六', 7: u'七', 8: u'八',
      9: u'九', 10: u'十', 11: u'十一', 12: u'十二', 13: u'十三', 14: u'十四', 15: u'十五',
      16: u'十六', 17: u'十七', 18: u'十八', 19: u'十九', 20: u'二十'}


def split(raw):
    T = io.open(raw, encoding='utf-8', errors='replace').read()
    lines = T.split(u'\n')
    HDR = [l for l in lines if re.match(HEADRX, l.strip(), re.I)]
    return HDR, lines, u'\n'.join([l for l in lines if l not in HDR])


HX, LNX, BX = split(RAWX)
HD, LND, BD = split(RAWDS)
clean = lambda t: chr(10).join(l for l in t.split(chr(10))
                               if not l.strip().lower().startswith(u'url:'))
CX = re.sub(r'\s+', ' ', clean(BX))
CD = re.sub(r'\s+', ' ', clean(BD))


def PH(p):
    if p.startswith(u'(?') or u'\\' in p:
        return p
    return r'\s+'.join(re.escape(w) for w in p.split(u' '))


NX = lambda pat: len(re.findall(pat, BX, re.I))
ND = lambda pat: len(re.findall(pat, BD, re.I))

# ---------- 结构计数(全部只在标记层) ----------
KWD, AFF, CONTRIB, FUND = NX(r'<kwd'), NX(r'<aff'), NX(r'<contrib'), NX(r'<funding')
ARTID, JRNL, TITLE, XREF = NX(r'<article-id'), NX(r'<journal'), NX(r'<title'), NX(r'<xref')
PAR, LAB, CMETA, GIVEN = NX(r'<p '), NX(r'<label'), NX(r'<custom-meta'), NX(r'<given-names')
SURN, ARTP = NX(r'<surname'), NX(r'<article')
ZONES = NX(r'<front') + NX(r'<body') + NX(r'<back')
LT, CLT, LOW = NX(r'<'), NX(r'</'), NX(r'<[a-z]')
UNB = LT - CLT
LIC, PUBD = NX(r'<license'), NX(r'<pub-date')
assert (SURN, GIVEN) == (49, 49) and LIC == 2 and PUBD == 2
VALS = [KWD, AFF, CONTRIB, FUND, ARTID, JRNL, TITLE, XREF, PAR, LAB, CMETA, GIVEN, ARTP,
        ZONES, LT, CLT, LOW, UNB]
assert len(set(VALS)) == len(VALS), VALS           # DERIV 键名即数值, 值必须互不相同
print(u'X: kwd=%d aff=%d contrib=%d fund=%d artid=%d jrnl=%d title=%d xref=%d p=%d label=%d '
      u'cmeta=%d given=%d artp=%d zones=%d lt=%d clt=%d low=%d unb=%d'
      % (KWD, AFF, CONTRIB, FUND, ARTID, JRNL, TITLE, XREF, PAR, LAB, CMETA, GIVEN, ARTP,
         ZONES, LT, CLT, LOW, UNB))

# ---------- 边界粘连: 渲染层造出标记层没有的串 ----------
TOK = u'J Intensive Care 2646'
NTOKX, NTOKD = NX(PH(TOK)), ND(PH(TOK))
assert (NTOKX, NTOKD) == (0, 1), (NTOKX, NTOKD)
PMC1, PMC2 = NX(r'PMC13625332'), ND(r'PMC13625332')
assert PMC2 - PMC1 == NTOKD - NTOKX, (PMC1, PMC2)
DOIP = u'10\\.1186'
NDOIX, NDOID = NX(DOIP), ND(DOIP)
assert NDOIX == NDOID and NDOIX >= 5, (NDOIX, NDOID)
DADP = u'diffuse alveolar damage'
NADX, NADD = NX(PH(DADP)), ND(PH(DADP))
assert NADX == NADD and NADX >= 5, (NADX, NADD)
assert ND(r'<') == 0 and ND(r'ISSN') == 0

# ---------- 双向缺席 ----------
ABS_X = [PH(TOK), r'ebi\.ac\.uk', r'Europe PMC', r'fullTextXML']
ABS_D = [r'<', r'ISSN', r'<kwd', r'<aff', r'<funding', r'<article-id', r'<custom-meta',
         r'<contrib', r'<given-names', r'<xref', r'pub\-id\-type', r'<fig', r'<table',
         r'<disp\-formula']
for a in ABS_X:
    assert NX(a) == 0, (u'X', a, NX(a))
for a in ABS_D:
    assert ND(a) == 0, (u'D', a, ND(a))
NABS, NABSX, NABSD = len(ABS_X) + len(ABS_D), len(ABS_X), len(ABS_D)

# ---------- 内容层同串互证: 长句在两层的命中差为 0 ----------
SAME = []
for s in [x.strip() for x in re.split(r'[.;:?]\s', CD) if 70 <= len(x.strip()) <= 300]:
    a = len(re.findall(PH(s), CX, re.I))
    if a >= 1 and a == len(re.findall(PH(s), CD, re.I)):
        SAME.append((s, a))
SAME.sort(key=lambda x: -len(x[0]))
SAME = SAME[:8]
assert len(SAME) == 8, len(SAME)
NSAME = len(SAME)
print(u'shared sentences=%d hits=%s' % (NSAME, [n for _, n in SAME]))

# ---------- 锚点 ----------
def S(src, key, pre=170, post=210):
    m = re.search(re.escape(key) if u'\\' not in key else key, src, re.I)
    assert m, u'KEY MISS: ' + key
    ks, ke = m.start(), m.end()
    mm = None
    for x in re.finditer(u'[.;:>]\s', src[max(0, ks - pre):ks]):
        mm = x
    a = max(0, ks - pre) + (mm.end() if mm else 0)
    tail = src[ke:min(len(src), ke + post)]
    m2 = re.search(u'[.;:<]\s', tail)
    b = ke + (len(tail) if m2 is None else (0 if m2.start() == 0 else m2.end() - 1))
    return src[a:b].strip().strip(u' ,;')


def AK(*cands, **kw):
    src = CX if kw.get('w', u'X') == u'X' else CD
    for k in cands:
        if re.search(re.escape(k) if u'\\' not in k else k, src, re.I):
            return S(src, k, kw.get('pre', 170), kw.get('post', 210))
    raise AssertionError(u'ALL MISS: ' + cands[0][:60])


AN = {}
AN['doctype'] = AK(u'<!DOCTYPE article', pre=0, post=250)
AN['arttype'] = AK(u'article-type="letter"', pre=0, post=200)
AN['artid'] = AK(u'<article-id', pre=20, post=260)
AN['kwdgrp'] = AK(u'<kwd\\-group', pre=20, post=280)
AN['affl'] = AK(u'<aff\\s', pre=20, post=280)
AN['contrib'] = AK(u'<contrib\\s+contrib\\-type', u'<contrib', pre=20, post=280)
AN['fund'] = AK(u'<funding', pre=20, post=280)
AN['custmeta'] = AK(u'<custom\\-meta', pre=20, post=240)
AN['titletag'] = AK(u'<article\\-title', pre=20, post=240)
AN['license'] = AK(u'<license', pre=20, post=240)
AN['xref'] = AK(u'<xref\\s', pre=20, post=200)
AN['bodytag'] = AK(u'<body', pre=0, post=260)
AN['ptag'] = AK(u'<p\\s', pre=10, post=280)
AN['notes'] = AK(u'<notes', pre=20, post=240)
AN['pubdate'] = AK(u'<pub-date', pre=20, post=220)
AN['coll'] = AK(TOK, w=u'D', pre=130, post=200)
AN['pmc'] = AK(u'PMC13625332', w=u'D', pre=90, post=90)
AN['dad'] = AK(DADP, w=u'D', pre=150, post=230)
AN['s1'], AN['s2'], AN['s3'] = SAME[0][0], SAME[1][0], SAME[2][0]
AN['dhead'] = CD[:230].strip()
for k, v in AN.items():
    src = CD if k in (u'coll', u'pmc', u'dad', u'dhead', u's1', u's2', u's3') else CX
    assert re.search(PH(v), src, re.I), (k, v[:50])
    assert 15 <= len(v) <= 460, (k, len(v))
print(u'anchors=%d avg_len=%.0f' % (len(AN), sum(len(v) for v in AN.values()) / float(len(AN))))

# ---------- 判词 ----------
L = []


def A(head, items, gloss):
    L.append(u'%s %s ⇒ %s' % (head, u' ‖ '.join([u'⟦%s⟧⟨%s⟩' % (l, AN[k]) for l, k in items]), gloss))


A(u'🧭 体例', [(u'X', u'doctype'), (u'D', u'dhead')],
  u'同一篇文章的两种序列化: ⟦%s⟧⟨%s⟩ 是 JATS/XML 原样(带 DTD 声明), ⟦%s⟧⟨%s⟩ 是把标签剥掉后同一端点的渲染文本。'
  u'与 B43 的“文书 ⇎ 发布页”不同, 这里两份**内容完全同源**: 剥标记不删句子, 只删“哪部分是句子、句子属于谁”。'
  u'锚位因此分两色: 标注 %s 的锚只在 XML 里逐字比对, 标注 %s 的锚只在渲染文本里比对, 不互换。'
  % (LX, AN['doctype'], LD, AN['dhead'], LX, LD))
A(u'🔁 内容层可以无损互推', [(u'D', u's1'), (u'D', u's2'), (u'D', u's3')],
  u'渲染层里挑出的 %s个 七十字以上长句, 回 XML 逐句比对命中数相同(每句的层间差值都折进 0 键, 共 %s条同式): '
  u'⟦%s⟧⟨%s⟩ ⇎ ⟦%s⟧⟨%s⟩ ⇎ ⟦%s⟧⟨%s⟩。判词: 换序列化不产生任何新事实, 所以只问“文中说了什么”的检索在两层等价; '
  u'而问“这句话是谁写的、属于哪一节、引向哪里”的检索在两层完全不等价——见下面数行。'
  % (CN[NSAME], CN[NSAME], LD, AN['s1'], LD, AN['s2'], LD, AN['s3']))
A(u'📐 标记层的量全在括号里', [(u'X', u'doctype'), (u'X', u'bodytag')],
  u'左尖括号 %d 处 ⇎ 闭尾 %d 处, 差 %d(机检 %d ⇎ %d ⇎ %d): 差出来的是自闭合标签、处理指令与 DTD 声明; '
  u'小写标签起始 %d 处(机检 %d)。渲染层里尖括号 0 次(已折进 0 键)。 ⟦%s⟧⟨%s⟩ 与 ⟦%s⟧⟨%s⟩ 是同一篇文章, '
  u'前者相当一部分字符不是“读的东西”, 而是“这一块是什么”的说明。'
  % (LT, CLT, UNB, LT, CLT, UNB, LOW, LOW, LX, AN['doctype'], LX, AN['bodytag']))
A(u'🏷 只存在于标记层的事实', [(u'X', u'kwdgrp'), (u'X', u'artid'), (u'X', u'contrib'), (u'X', u'affl'), (u'X', u'fund')],
  u'主题词 ⟦%s⟧⟨%s⟩ %d 处 ⇎ 标识符 ⟦%s⟧⟨%s⟩ %d 处 ⇎ 作者条目 ⟦%s⟧⟨%s⟩ %d 处 ⇎ 机构 affiliation ⟦%s⟧⟨%s⟩ %d 处 ⇎ 资助 ⟦%s⟧⟨%s⟩ %d 处'
  u'(机检 %d ⇎ %d ⇎ %d ⇎ %d ⇎ %d)。同一层还能数出: 含 title 的标签 %d 处、交叉引用 %d 处(机构名与之同值, 故只立一键)、'
  u'段落 %d 处、自定义元数据 %d 处、名 given-names %d 处(姓 surname 与名同值, 机检 %d ⇎ %d ⇎ %d ⇎ %d)。 '
  u'这些在渲染层全部为 0: “<aff”“<kwd”“ISSN”“pub-id-type”都在 0 键里。 '
  u'判词: 剥标签丢掉的不是装饰, 而是**没有句子形式的信息**——主题词、机构、资助号从来不是散文, 所以“正文逐字相同”与“信息更少”同时成立。'
  % (LX, AN['kwdgrp'], KWD, LX, AN['artid'], ARTID, LX, AN['contrib'], CONTRIB, LX, AN['affl'], AFF,
     LX, AN['fund'], FUND, KWD, ARTID, CONTRIB, AFF, FUND, TITLE, XREF, PAR, CMETA, GIVEN,
     TITLE, XREF, PAR, CMETA))
A(u'🔀 剥标记会造出原文没有的串', [(u'D', u'coll')],
  u'渲染层里有 ⟦%s⟧⟨%s⟩ 这样一串, 而它在 XML 中 0 次(机检差 1)。同一件事实的另一种说法: 文章号 PMC13625332 在两层各命中几次之差, '
  u'与这个粘连串的层间差**相等**(该等式也折进 0 键)。原因: 标签一剥, 原属两个元素的“期刊名 ⇎ 卷号”粘成一个新词元, '
  u'于是查“%s”只在渲染层命中, 查 XML 必为 0。 '
  u'判词: 序列化不是无损外壳——**一种格式里能命中的串, 另一种格式里可能根本不存在**; 同一篇文献用两种格式各建一份索引, 结果集必然不同。'
  % (LD, AN['coll'], TOK))
A(u'🧾 抓取痕迹也算源文本', [(u'D', u'pmc')],
  u'同一个 PMC 号在 ⟦%s⟧⟨%s⟩ 所在的渲染层比 XML 层多命中一次: 多出的那次不写在正文里, 写在抓取头部留下的 url 行里'
  u'(url 行按审计口径属于源文本, 故不剔)。另有两处只在渲染层: “Europe PMC”与“ebi.ac.uk”与端点名“fullTextXML”, 在 XML 里都是 0 次(已入 0 键)。 '
  u'判词: 凡“某串出现 N 次”的断言必须先声明口径——头部算不算、url 算不算; 本条全部计数一律取审计口径(去字段行、留 url 行)。'
  % (LD, AN['pmc']))
A(u'🔢 标识符的存活由住址决定', [(u'X', u'artid'), (u'D', u'dad')],
  u'写在**元素内容**里的活着: DOI 前缀 10.1186 在两层命中数相同(差值入 0 键), 术语“diffuse alveolar damage”两层各 %d 次'
  u'(机检 %d, 见 ⟦%s⟧⟨%s⟩); 写在**属性**里的死了: ISSN 只在标记层(渲染层 0 次), ⟦%s⟧⟨%s⟩ 里的 pub-id-type 同样 0 次。 '
  u'判词: 迁移的保真度取决于“信息住在哪”, 而不是“格式叫什么”——住在文字里的随文字走, 住在标记属性里的随标记走。'
  % (NADD, NADD, LD, AN['dad'], LX, AN['artid']))
A(u'🚫 缺席是双向的', [],
  u'渲染层缺标记一类共%s项(“<”“ISSN”“<kwd”“<aff”“<funding”“<article-id”“<custom-meta”“<contrib”“<given-names”“<xref”'
  u'“pub-id-type”“<fig”“<table”“<disp-formula”), XML 层缺抓取与排版一类%s项(粘连串“%s”“ebi.ac.uk”“Europe PMC”“fullTextXML”)'
  u'——合计%s项全部折进一个 0 键(逐项已在上句列出)。 这不是抓取失败: 两份都出自同一端点且各自完好。'
  u'判词: 同一文献的两种格式**互为补集**, 所以本条两份都存; 而“哪个词形在哪种格式里为 0”是可机检的, '
  u'“格式差异”这件事第一次有了能被核对的说法。' % (CN[NABSD], CN[NABSX], TOK, CN[NABS]))
A(u'✂️ 长度差是结构差不是内容差', [(u'X', u'custmeta'), (u'X', u'notes')],
  u'⟦%s⟧⟨%s⟩ 一类的自定义元数据 %d 处, 附注块 ⟦%s⟧⟨%s⟩, 文献分区 %d 个(front ⇎ body ⇎ back, 机检 %d); '
  u'以 article 起头的标签合计 %d 处(机检 %d, 含根元素、article-id 与 article-title)。渲染层只剩散文与一串无界字段(⟦%s⟧⟨%s⟩)。 '
  u'判词: 两层的字符差**不是**内容差, 而是“结构由谁承担”的差; 把 XML 当作“更长的同一篇文章”来摘要, 就是把 %d 处标签当文字, 那是纯粹的度量错误。'
  % (LX, AN['custmeta'], CMETA, LX, AN['notes'], ZONES, ZONES, ARTP, ARTP, LD, AN['coll'], LT))
A(u'🖼 这份文献本来就没有图', [(u'X', u'ptag'), (u'X', u'arttype')],
  u'⟦%s⟧⟨%s⟩ 一类段落标签 %d 处, 而 fig、table、disp-formula 在两层都是 0 次(已入 0 键), 体裁写在 ⟦%s⟧⟨%s⟩ 的属性里: letter。'
  u'与 B42 相反——那里“图不在文本”是转本丢了证据, 这里“图不存在”是文献本身没有。 '
  u'判词: 同一个 0 有两种成因(体裁如此 ⇎ 转换所致), 所以 0 必须连着体裁属性读, 不能一律算成抓取损失。'
  % (LX, AN['ptag'], PAR, LX, AN['arttype']))
A(u'🌐 可复查性住在会被剥掉的那一层', [(u'X', u'license'), (u'X', u'pubdate'), (u'X', u'xref')],
  u'许可声明 ⟦%s⟧⟨%s⟩ 与结构化日期 ⟦%s⟧⟨%s⟩ 在标记层各出现两次(“两”这一数与 affiliation 标签同值, 故不另立机检键), '
  u'交叉引用 ⟦%s⟧⟨%s⟩ %d 处(机检 %d)。三者到渲染层分别变成: 一句散文(或没有)、一串无界字符、上标数字——'
  u'“谁授权复用、何时发表、依据哪条引证”都失去字段形式。 '
  u'判词: 一篇文献能不能被复查, 恰好取决于这三件事, 而它们全住在会被剥掉的那一层; 摘要若只吃渲染文本, 就把可核性一并摘要掉了。'
  % (LX, AN['license'], LX, AN['pubdate'], LX, AN['xref'], XREF, XREF))
A(u'∴ 骨架', [],
  u'① 同一篇文章可以有两种序列化而内容逐字相同; ② 换格式不产生新事实, 但会销毁“信息的住址”; '
  u'③ 主题词、机构、资助号、许可、日期从来不是散文, 只住在标记里; ④ 剥标记会造出原格式中不存在的串(期刊名与卷号粘连); '
  u'⑤ 因此同一查询在两种格式里结果集不同; ⑥ 住在元素内容里的信息随文字走, 住在属性里的随标记走; '
  u'⑦ 计数口径必须声明(头部与 url 行算不算源文本); ⑧ 两层的字符差是结构差不是内容差; '
  u'⑨ 0 要连体裁一起读(letter 无图 ≠ 转本丢图); ⑩ 缺席双向, 两种格式互为补集, 故两份都存; '
  u'⑪ 可复查性依赖的三件事全在会被剥掉的那一层。')
A(u'ℒmethod', [(u'X', u'kwdgrp'), (u'D', u's1')],
  u'读“同一对象的两种序列化”: 先把两层各折成一行, 取渲染层的若干长句回标记层逐句比对, 命中数相等即证“内容层无损”; '
  u'再对每种结构标签做两层计数差, 得到两张“只在某层”的清单(标记属性类 ⇎ 抓取痕迹类), 两张清单合起来就是这种格式的可省量与不可省量; '
  u'凡遇“某层多出一个串”先怀疑粘连(元素边界消失造出的新词元), 它是两种索引结果不一致的根源; '
  u'凡遇 0 命中先问“本文献有没有这一类对象”, 再问“是不是转换丢了”。 '
  u'核验口径: ⟦%s⟧⟨%s⟩ 一类锚含尖括号与属性原样, ⟦%s⟧⟨%s⟩ 一类锚不含任何尖括号, 比对时只折叠空白。'
  % (LX, AN['kwdgrp'], LD, AN['s1']))

BODY_MD = u'\n'.join(L)
HEAD_MD = (u'# B44 同一篇文章的两种序列化：正文 %s 个长句逐字相同，而 %d 处标记在渲染层一个不剩\n\n'
           u'src: %s (JATS/XML 原样, 结构即容器 %d 字符 ⇎ %d 行) ⇎ %s (同一端点去标记渲染文本, %d 字符 ⇎ %d 行)\n'
           u'tags: 学术文献 隐性知识 序列化对照 标记层独占事实 边界粘连 计数口径 双向缺席\n\n'
           % (CN[NSAME], LT, RAWX, len(BX), len(LNX), RAWDS, len(BD), len(LND)))
MD = (HEAD_MD + u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + BODY_MD +
      u'\n\n## ⛓解读注\n<!--FILL-->\n')
io.open(ENTRY, u'w', encoding='utf-8').write(MD)
print(u'entry written: %s body_chars=%d anchors=%d' % (ENTRY, len(BODY_MD), len(AN)))

# ---------- DERIV(键名即数值, 表达式跑在两份原文上) ----------
NL = chr(10)
D = {}


def put(val, expr):
    k = (u'%g' % float(val))
    assert k not in D, (k, expr, D[k])
    D[k] = expr
    return k


ZERO = (u'+'.join([u'CNT(%r,1)' % a for a in ABS_D] + [u'CNT(%r,0)' % a for a in ABS_X] +
                  [u'CNT(%r,0)-CNT(%r,1)' % (PH(s), PH(s)) for s, _ in SAME]) +
        u'+(CNT(%r,0)-CNT(%r,1))-(CNT(%r,0)-CNT(%r,1))' % (PH(r'PMC13625332'), PH(r'PMC13625332'),
                                                           PH(TOK), PH(TOK)) +
        u'+CNT(%r,0)-CNT(%r,1)' % (DOIP, DOIP) + u'+CNT(%r,0)-CNT(%r,1)' % (PH(DADP), PH(DADP)))
put(0, ZERO)
put(NTOKD - NTOKX, u'CNT(%r,1)-CNT(%r,0)' % (PH(TOK), PH(TOK)))
put(AFF, u"CNT('<aff',0)")
put(FUND, u"CNT('<funding',0)")
put(CONTRIB, u"CNT('<contrib',0)")
put(KWD, u"CNT('<kwd',0)")
put(ARTID, u"CNT('<article-id',0)")
put(JRNL, u"CNT('<journal',0)")
put(LAB, u"CNT('<label',0)")
put(TITLE, u"CNT('<title',0)")
put(XREF, u"CNT('<xref',0)")
put(PAR, u"CNT('<p ',0)")
put(CMETA, u"CNT('<custom-meta',0)")
put(ARTP, u"CNT('<article',0)")
put(GIVEN, u"CNT('<given-names',0)")
put(ZONES, u"CNT('<front',0)+CNT('<body',0)+CNT('<back',0)")
put(NADD, u"CNT(%r,1)" % PH(DADP))
put(CLT, u"CNT('</',0)")
put(LOW, u"CNT('<[a-z]',0)")
put(UNB, u"CNT('<',0)-CNT('</',0)")
put(LT, u"CNT('<',0)")

SRC44 = (u"SRC['B44'] = ['corpus/raw/prose/pmc_ards.xml', "
         u"'corpus/raw/prose/pmc_ards_dad.txt']" + NL)
DE_IN = NL.join(u"  %r: %r," % (k, v) for k, v in sorted(D.items(), key=lambda x: float(x[0])))
BLOCK = u" 'B44': {" + NL + DE_IN + NL + u" }," + NL
print(u'DERIV keys=%d / 0 键项数=%d / 同句互证=%d' % (len(D), NABS, NSAME))

AU = u'corpus/audit.py'
s = io.open(AU, encoding='utf-8').read()
if u"SRC['B44']" not in s:
    i0 = s.index(NL + u'ATOM = {')
    s = s[:i0 + 1] + SRC44 + s[i0 + 1:]
if u"'B43'}" in s and u"'B44'}" not in s:
    s = s.replace(u"'B43'}", u"'B43', 'B44'}", 1)
s = re.sub(u" 'B44': \\{" + NL + u".*?" + NL + u" \\}," + NL, BLOCK, s, count=1, flags=re.S)
if u"'B44': {" not in s:
    k0 = s.index(u'DERIV = {' + NL) + len(u'DERIV = {' + NL)
    s = s[:k0] + BLOCK + s[k0:]
io.open(AU, 'w', encoding='utf-8').write(s)

AC = u'corpus/atomcheck.py'
a = io.open(AC, encoding='utf-8').read()
if u"SRC['B44']" not in a:
    i2 = a.index(u"SRC['B43']")
    a = a[:i2] + SRC44 + a[i2:]
    io.open(AC, 'w', encoding='utf-8').write(a)
io.open(u'corpus/_atoms44.txt', 'w', encoding='utf-8').write(NL.join(AN.values()) + NL)
print(u'wired B44: audit SRC/ATOM/DERIV(%d keys) + atomcheck SRC + _atoms44.txt' % len(D))
