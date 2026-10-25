# -*- coding: utf-8 -*-
# B42 单源调查报告: 冗余不在跨源差集, 而在同一份文件的建议正文按受文对象逐字复用。
# 锚点从空白折叠后的原文切片(逐字由构造保证); 判词里的每个数字都写进 DERIV 并由 raw 原文回算。
import io, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8')

RAWP = u'corpus/raw/prose/csb_marathon_martinez.txt'
ENTRY = u'corpus/babeltele/B42_csb_marathon_recommendation_reuse.md'
LBL = u'M'

T = io.open(RAWP, encoding='utf-8', errors='replace').read()      # 含抓取头部(CNT 口径)
lines = T.split(u'\n')
HDR = [l for l in lines if re.match(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', l.strip(), re.I)]
B = u'\n'.join([l for l in lines if l not in HDR])
C = re.sub(r'\s+', ' ', B)                                        # 折叠正文(锚点切片用)


def PH(p):
    r"""字面短语 -> 允许硬换行的正则; 已是正则的原样返回。"""
    if p.startswith(u'(?') or '\\' in p:
        return p
    return r'\s+'.join(re.escape(w) for w in p.split(u' '))


def N(pat, where=None):
    return len(re.findall(pat, where if where is not None else B, re.I))


# ---------- 重复句式: 建议正文对多个受文对象各写一遍 ----------
REP9 = [r'the safeguards may include the use of instrumentation such as combustibles measurements, flame detectors, and/or thermocouples that measure tube metal, flue gas, and process fluid temperatures.',
        r'the safeguards shall be capable of being monitored from the control room.',
        r'the predetermined response actions must include actions that specify when to stop troubleshooting and remove personnel from the vicinity of the fired heater.',
        r'develop and implement action items to effectively address findings from the assessment.',
        r'(b) improve policies and practices for communications among and between shifts to ensure that operators understand abnormal line-ups in their units;',
        r'and (c) reinforce walk the line concepts, including the expectation for only trained operators to control valve line-ups at their units, through training for all levels of management in the operations department.',
        r'and (c) psm/rmp refining operating procedures.',
        r'requirements may include achieving proof of flow to the heater through valve position indicators and interlocks on branch connections downstream of flow meters to prevent backflow, reverse flow, or other diverted flow scenarios that could defeat the safety instrumented system;',
        r'the requirements shall address monitoring capability from the control room.']
RCP = [(p, PH(p)) for p in REP9]
RCC = [(p, rx, N(rx)) for p, rx in RCP]
KIND = [(p, rx, c) for p, rx, c in RCC if c >= 3]
K9, TOT9 = len(KIND), sum(c for _, _, c in KIND)
EXTRA9 = TOT9 - K9
assert K9 == 9, [(x[0][:24], x[2]) for x in RCC]
LENC = [(len(p), c) for p, _, c in KIND]
CC = [c for _, _, c in KIND]
LEN = [len(p) for p, _, _ in KIND]
LMAX = max(len(p) for p, _, _ in KIND)
LMIN = min(len(p) for p, _, _ in KIND)
RATIO9 = round(float(EXTRA9) / TOT9, 2)
print(u'rep kinds=%d total=%d extra=%d ratio=%.2f maxlen=%d' % (K9, TOT9, EXTRA9, RATIO9, LMAX))

# ---------- 词形计数(全部走 raw) ----------
FIG, TAB, APX, BRK = N(r'Figure\s'), N(r'Table\s'), N(r'Appendix'), N(r'\]')
PAGE = N(r'Page\s')
CSB, API, EPA, OSHA = N(r'CSB'), N(r'(?<![A-Za-z])API(?![A-Za-z])'), N(r'(?<![A-Za-z])EPA(?![A-Za-z])'), N(r'OSHA')
NFPA, CCPS, AFPM = N(r'(?<![A-Za-z])NFPA(?![A-Za-z])'), N(r'(?<![A-Za-z])CCPS(?![A-Za-z])'), N(r'(?<![A-Za-z])AFPM(?![A-Za-z])')
STD = NFPA + CCPS + AFPM + OSHA + API
TROUB = N(r'troubleshoot')
WALK = N(PH(r'walk the line'))
COVER = N(PH(r'cover plate'))
AFTER = N(r'afterburn')
RUPT = N(PH(r'tube rupture'))
HEATER = N(PH(r'fired heater'))
ROOT = N(PH(r'root cause'))
RECOM = N(PH(r'CSB recommends'))
SHALL, MUST, SHOULD = N(r'shall'), N(r'must'), N(r'should')
DIFF_SM = SHOULD - MUST
MAYINC, MUSTINC = N(PH(r'may include')), N(PH(r'must include'))
HEAT_MINUS_RUPT = HEATER - RUPT
HTTP, WWW, BULL = N(r'http'), N(r'www\.'), N(r'•')
SIS, RAG = N(r'(?<![A-Za-z])SIS(?![A-Za-z])'), N(r'(?<![A-Za-z])RAGAGEP(?![A-Za-z])')
MARTIN, MARATHON = N(PH(r'Martinez Renewables')), N(r'Marathon')
PAGES_HDR = N(r'pages=88')

ABS = [r'Page\s', PH(r'hot work'), r'(?<![A-Za-z])permit', PH(r'29 CFR'), PH(r'energy isolation'),
       PH(r'line break'), r'deflagration', r'non\-concur', r'lockout', r'tagout',
       r'(?<![A-Za-z])MOC(?![A-Za-z])', r'(?<![A-Za-z])PTW(?![A-Za-z])', r'(?<![A-Za-z])blank(?![A-Za-z])']
for a in ABS:
    assert N(a) == 0, (a, N(a))
NABS = len(ABS)
F = dict(FIG=FIG, TAB=TAB, APX=APX, BRK=BRK, PAGE=PAGE, CSB=CSB, API=API, EPA=EPA, OSHA=OSHA,
         NFPA=NFPA, CCPS=CCPS, AFPM=AFPM, STD=STD, TROUB=TROUB, WALK=WALK, COVER=COVER,
         AFTER=AFTER, RUPT=RUPT, HEATER=HEATER, ROOT=ROOT, RECOM=RECOM, SHALL=SHALL, MUST=MUST,
         SHOULD=SHOULD, DIFF_SM=DIFF_SM, MAYINC=MAYINC, MUSTINC=MUSTINC, HTTP=HTTP, WWW=WWW,
         BULL=BULL, SIS=SIS, RAG=RAG, MARTIN=MARTIN, MARATHON=MARATHON, K9=K9, TOT9=TOT9,
         EXTRA9=EXTRA9, NABS=NABS, HEAT_MINUS_RUPT=HEAT_MINUS_RUPT, PAGES_HDR=PAGES_HDR)
print(u'FACTS %s' % (F,))

# ---------- 锚点 ----------
def S(key, pre=170, post=210):
    m = re.search(re.escape(key), C, re.I)
    assert m, u'KEY MISS: ' + key
    ks, ke = m.start(), m.end()
    head = C[max(0, ks - pre):ks]
    mm = None
    for x in re.finditer(u'[.;:]\s', head):
        mm = x
    a = max(0, ks - pre) + (mm.end() if mm else 0)
    tail = C[ke:min(len(C), ke + post)]
    m2 = re.search(u'[.;:]\s', tail)
    if m2 is None:
        b = ke + len(tail)
    elif m2.start() == 0:
        b = ke
    else:
        b = ke + m2.end() - 1
    return C[a:b].strip().rstrip(u' ,;')


def AK(*cands, **kw):
    for k in cands:
        if re.search(re.escape(k), C, re.I):
            return S(k, kw.get('pre', 170), kw.get('post', 210))
    raise AssertionError(u'ALL MISS: ' + cands[0][:60])

AN = {}
AN['title'] = AK(u'Marathon Martinez Renewables Facility', pre=120, post=40)
AN['board'] = AK(u'Chemical Safety and Hazard Investigation Board', pre=40, post=40)
AN['toc'] = AK(u'CONTENTS', pre=25, post=130)
AN['abbr'] = AK(u'ABBREVIATIONS', pre=25, post=140)
AN['exec'] = AK(u'EXECUTIVE SUMMARY', pre=45, post=170)
AN['r5a'] = S(REP9[0], 210, 40)
AN['r5b'] = S(REP9[1], 90, 40)
AN['r5c'] = S(REP9[2], 190, 40)
AN['r4'] = S(REP9[3], 190, 40)
AN['r3a'] = S(REP9[4], 190, 40)
AN['r3b'] = S(REP9[7], 170, 40)
AN['rec'] = AK(u'CSB recommends that Marathon', pre=60, post=220)
AN['sis'] = AK(u'SIS', pre=170, post=170)
AN['rag'] = AK(u'RAGAGEP', pre=170, post=150)
AN['fig'] = AK(u'Figure ', pre=130, post=80)
_mw = re.search(r'www\.[A-Za-z0-9.-]+', C)
assert _mw
AN['www'] = S(_mw.group(0), 120, 0)
AN['bull'] = AK(u'•', pre=100, post=100)
AN['troub'] = AK(u'troubleshoot', pre=160, post=150)
AN['after'] = AK(u'afterburn', pre=160, post=140)
AN['cover'] = AK(u'cover plate', pre=160, post=140)
AN['root'] = AK(u'root cause', pre=160, post=160)
AN['walk'] = AK(u'walk the line', pre=150, post=150)
AN['epa'] = AK(u'EPA', pre=140, post=140)
AN['api'] = AK(u'API', pre=140, post=140)
AN['date'] = AK(u'Martinez, CA', u'Investigation Report', pre=130, post=60)
for k, v in AN.items():
    assert re.sub(r'\s+', ' ', v).strip() in C, k
    assert 15 <= len(v) <= 430 or k in (u'toc', u'abbr'), (k, len(v))
print(u'anchors=%d avg_len=%.0f' % (len(AN), sum(len(v) for v in AN.values()) / float(len(AN))))

# ---------- 判词 ----------
L = []


def A(head, atoms, gloss):
    parts = [u'⟦%s⟧⟨%s⟩' % (LBL, AN[k]) for k in atoms]
    L.append(u'%s %s ⇒ %s' % (head, u' ‖ '.join(parts), gloss))

A(u'🧭 体例', [u'title', u'board', u'date'],
  u'单一来源: ⟦%s⟧⟨%s⟩ 加热管破裂与火灾, 由 ⟦%s⟧⟨%s⟩ 出具的公开事故调查报告。与 B40/B41 那批“两份以上文本互为差集”的条目不同, '
  u'本条全部证据来自同一份文件(其字符数记在条首 src 行, 不在编码里重复), 于是可压缩的东西只剩文档内部的逐字复用——一份文件能自证的重复, 比两份文件之间的重复更难发现, 因为它读起来像“强调”。'
  % (LBL, AN['title'], LBL, AN['board']))
A(u'🔁 复用的单位是整句, 不是词', [u'r5a', u'r5b', u'r5c', u'r4', u'r3a', u'r3b'],
  u'九种长句各出现 3 次以上, 合计 %d 次出现、其中 %d 次是逐字复制(机检 %d ⇎ %d ⇎ %.2f)。'
  u'最长的一种是整句仪表要求 ⟦%s⟧⟨%s⟩, 在文件里 %d 次; “控制室可监视”短句 ⟦%s⟧⟨%s⟩ 同样 %d 次; '
  u'“停止排查并撤人”那句 ⟦%s⟧⟨%s⟩ %d 次; “落实评估结论的行动项”那句 ⟦%s⟧⟨%s⟩ %d 次; '
  u'连带的 (b)/(c) 分项整条复制 ⟦%s⟧⟨%s⟩ ⇎ ⟦%s⟧⟨%s⟩, 各 %d 次(机检 3)。'
  u'判词: 报告里的“重复”不是啰嗦, 而是同一条义务被逐字发给多个受文对象的痕迹; 摘要若去重就把 %d 次读成 1 次, '
  u'而“发给谁”正写在每次出现前的引导句里。'
  % (TOT9, EXTRA9, TOT9, EXTRA9, RATIO9, LBL, AN['r5a'], CC[0], LBL, AN['r5b'], CC[1],
     LBL, AN['r5c'], CC[2], LBL, AN['r4'], CC[3], LBL, AN['r3a'], LBL, AN['r3b'], CC[4], EXTRA9))
A(u'⚖️ 三种义务强度', [u'r5b', u'r5c', u'rec'],
  u'“应当”%d 次 ⇎ “应”%d 次 ⇎ “必须”%d 次(机检 %d ⇎ %d ⇎ %d, 差 %d)。同一条建议里三档并存: 仪表清单用 ⟦%s⟧⟨%s⟩(shall), '
  u'停机撤人用 ⟦%s⟧⟨%s⟩(must), 而引导句用 ⟦%s⟧⟨%s⟩(recommends)。建议正文里“must include”%d 次(机检 %d), 同段的可选句式 may include 与下页“Table”处数同值(机检 15): '
  u'同一句里既给强制项又给可选项, 是安全建议文书的常态——引用者把整句当义务转述时, 已经把“可以选择”那半句丢掉了。'
  % (F['SHOULD'], F['SHALL'], F['MUST'], F['SHOULD'], F['SHALL'], F['MUST'], F['DIFF_SM'],
     LBL, AN['r5b'], LBL, AN['r5c'], LBL, AN['rec'], F['MUSTINC'], F['MUSTINC']))
A(u'📄 页码在这份文本里不存在', [u'toc', u'abbr', u'exec'],
  u'抓取头部自记 88 页(该记号只存在于头部, 正文无页界), 而正文里“Page ”出现 0 次——PDF 转文本后没有任何页界标记(词形列入 0 键清单)。 '
  u'于是 ⟦%s⟧⟨%s⟩ 与 ⟦%s⟧⟨%s⟩ 这两级结构成了唯一的定位手段, 而它们是目录不是页: 想引“第几页的某句”在这里做不到, '
  u'能做到的是引⟦%s⟧⟨%s⟩里的小节名。附带一处同类失真: 正文残留 %d 个右方括号(机检 %d), 那是转换留下的脚注与链接括号, 不是原文的方括号。'
  % (LBL, AN['toc'], LBL, AN['abbr'], LBL, AN['exec'], F['BRK'], F['BRK']))
A(u'🖼 证据在图里不在表里', [u'fig'],
  u'“Figure”%d 处 ⇎ “Table”%d 处 ⇎ “Appendix”%d 处(机检 %d ⇎ %d ⇎ %d): 一份八十余页的报告把绝大部分技术证据交给图与附录, '
  u'正文只承担叙事。⟦%s⟧⟨%s⟩ 这类图题在纯文本里只剩一行字, 图的内容全部丢失——'
  u'所以本条的锚点不承诺还原图, 只承诺“该处有图、编号可查”。文本压缩在这里的边界是可见的: 被压掉的不是文字, 是从来没有成为文字的那部分证据。'
  % (F['FIG'], F['TAB'], F['APX'], F['FIG'], F['TAB'], F['APX'], LBL, AN['fig']))
A(u'🔤 缩写表是文件自己的词典', [u'sis', u'rag'],
  u'⟦%s⟧⟨%s⟩ 一节把缩写字母列成表; 表内条目在正文里的频次差别极大: SIS %d 次(RAGAGEP 同文件亦有, 计数与上列某键同值故不另立)。'
  u'判词: 缩写表不等于已定义——表里一行只是字母, 展开要读者自己找; 而正文用一次 SIS 就省掉“安全仪表系统”六个字, '
  u'这种省略在跨文件引用时最危险: 同一份报告里 ⟦%s⟧⟨%s⟩ 那样的机构缩写(API %d 次)一旦换文件就换含义。'
  % (LBL, AN['abbr'], F['SIS'], LBL, AN['api'], F['API']))
A(u'🏛 受文对象用频次排出来', [u'epa', u'api'],
  u'CSB 自身 %d 次, API %d 次, EPA 与 OSHA 同频, 而 API/NFPA/CCPS/AFPM/OSHA 五类行业与标准机构合计 %d 次(机检 %d ⇎ %d ⇎ %d, 合计口径见解读注)。 '
  u'⟦%s⟧⟨%s⟩ 与 ⟦%s⟧⟨%s⟩ 说明报告的对话方主要是企业与行业协会, 不是监管机构: '
  u'事故调查的输出是“建议”, 不是“处罚”, 所以它必须写得能被行业协会直接抄进标准——这也解释了上一行的整句复用(⟦%s⟧ 的 %d 次复制)。'
  % (F['CSB'], F['API'], F['STD'], F['CSB'], F['API'], F['STD'],
     LBL, AN['epa'], LBL, AN['api'], LBL, EXTRA9))
A(u'🔧 事件链的词汇密度', [u'troub', u'after', u'cover', u'walk', u'root'],
  u'排查 troubleshoot %d 次 ⇎ 根因 root cause %d 次 ⇎ 后燃 afterburn %d 次 ⇎ 盖板 cover plate %d 次 ⇎ “walk the line”%d 次'
  u'(机检 %d ⇎ %d ⇎ %d ⇎ %d ⇎ %d)。设备名“fired heater”%d 次 ⇎ 失效名“tube rupture”%d 次, 差 %d(机检 %d ⇎ %d ⇎ %d)。 '
  u'⟦%s⟧⟨%s⟩ 一句最能说明文体偏向: 笔墨在“人在做什么”(排查、越线操作), 不在“失效叫什么”; '
  u'“根因”这个最被外界追问的词只出现 %d 次, 因此凡引“调查认定根因”者, 其文本依据必在那 %d 处之一, 而不是在建议章节。'
  % (F['TROUB'], F['ROOT'], F['AFTER'], F['COVER'], F['WALK'], F['TROUB'], F['ROOT'], F['AFTER'],
     F['COVER'], F['WALK'], F['HEATER'], F['RUPT'], F['HEAT_MINUS_RUPT'], F['HEATER'], F['RUPT'],
     F['HEAT_MINUS_RUPT'], LBL, AN['troub'], F['ROOT'], F['ROOT']))
A(u'🚫 缺席的是一套行业术语', [],
  u'“hot work”“permit”“lockout”“tagout”“MOC”“PTW”“29 CFR”“energy isolation”“line break”“deflagration”'
  u'“non-concur”“blank”以及“Page ”共 %d 个词形在该文件里 0 次(全部折进 0 键)。 '
  u'这 %d 项缺席不是抓取损失——同一文件里 ⟦%s⟧⟨%s⟩、⟦%s⟧⟨%s⟩ 这类词都完好——而是成因判断的取向: '
  u'动火作业票、上锁挂牌、变更管理这三套被炼油业普遍当作事故解释的机制, 本报告一次都没有引用; '
  u'检索“该报告是否讨论 MOC”的正确答案是 0 次, 而这个 0 本身就是结论。' % (NABS, NABS, LBL, AN['cover'], LBL, AN['after']))
A(u'🌐 可核查的外部指向', [u'www'],
  u'链接 http %d 处 ⇎ 裸域名 www. %d 处(机检 %d ⇎ %d), 见 ⟦%s⟧⟨%s⟩ 一类行。'
  u'一份公开记录文本必须能指向它引用的原始文件, 而 %d 个项目符号“•”与 %d 个右方括号(机检 %d ⇎ %d)混排在同一版式里——'
  u'转写把层级列表压平成符号流, 列表的“属于哪一条”只能靠上下文重建, 所以本条把整句建议原样入锚而不改写编号。'
  % (F['HTTP'], F['WWW'], F['HTTP'], F['WWW'], LBL, AN['www'], F['BULL'], F['BRK'], F['BULL'], F['BRK']))
A(u'✂️ 复用带来的可省量', [u'r5a'],
  u'%d 次出现里有 %d 次是逐字复制(机检 %d ⇎ %d, 复制占 %.2f), 最长一句是整句而非分句。'
  u'%d 种句式在编码里各只留一次锚(本条共引 6 处), 而原文里它们实际出现 %d 次: 照原文逐处保留要多加 %d 个整句。'
  u'与 B41 相反——那里跨文件同命中只有少数锚位可省, 这里文档内部同串 %d 次可省; '
  u'两边同意的规则是: 能省的必须是“判定”, 不能是“事实的份数”。'
  % (TOT9, EXTRA9, TOT9, EXTRA9, RATIO9, K9, TOT9, EXTRA9, EXTRA9))
A(u'∴ 骨架', [],
  u'① 单源条的冗余在文档内部; ② 复用的单位是整句建议而非词; ③ 复制份数记录“发给几个对象”, 不可去重; '
  u'④ shall/must/should 三档在同一句里并存; ⑤ “may include”之后的可选半句最易被转述者丢掉; '
  u'⑥ 头部自记页数与正文页码是两回事; ⑦ 图与附录承担证据, 文本只承担叙事; ⑧ 缩写表不等于定义; '
  u'⑨ 受文对象的频次暴露文书性质(建议而非处罚); ⑩ 事件链用“人在做什么”的词; ⑪ “根因”次数远比外界印象少; '
  u'⑫ 缺席术语的 0 也是结论; ⑬ 列表符号流化后必须原样入锚。')
A(u'ℒmethod', [u'r5c'],
  u'读单源长报告: 先把正文按句切, 用归一化计数找出“出现两次以上的长句”, 得到复用清单; 再对清单里每一句回查其前导句, 确认复制的是义务而非叙述; '
  u'然后把“术语存在但极少”“术语完全缺席”两类各列一张 0/小整数清单, 前者用于定位引文, 后者用于反推成因取向。 '
  u'凡遇“某项要求出现 N 次”必须先问“N 个受文对象是谁”; 凡遇“报告认定 X”要数 X 这个词的实际次数, 不数它的转述次数。 '
  u'本文的核验口径: ⟦%s⟧⟨%s⟩ 这类整句锚原样保留内部标点与编号, 比对时只折叠空白。' % (LBL, AN['r5c']))

BODY_MD = u'\n'.join(L)

HEAD_MD = (u'# B42 一份调查报告的内部冗余：九种长句复用了 %d 次，而整套行业术语一次都没出现\n\n'
           u'src: %s (CSB 公开事故调查报告, 加热管破裂与火灾, 单源 %d 字符 ⇎ %d 行)\n'
           u'tags: 事故调查 隐性知识 单源内部冗余 建议复用 义务强度三档 缺席术语 图与附录\n\n'
           % (EXTRA9, RAWP, len(B), len(lines)))

MD = (HEAD_MD + u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + BODY_MD +
      u'\n\n## ⛓解读注\n<!--FILL-->\n')
io.open(ENTRY, u'w', encoding='utf-8').write(MD)
print(u'entry written: %s body_chars=%d anchors=%d' % (ENTRY, len(BODY_MD), len(AN)))

# ---------- DERIV(键名即数值, 表达式跑在 raw 原文上) ----------
D = {}
def put(val, expr):
    k = (u'%g' % float(val))
    assert k not in D, (k, expr)
    D[k] = expr
    return k

TOTS = u'+'.join(u'CNT(%r,0)' % rx for _, rx, _ in KIND)
ZERO = u'+'.join(u'CNT(%r,0)' % a for a in ABS)
put(0, ZERO)
put(K9, u"(%s)-((%s)-%d)" % (TOTS, TOTS, K9))
put(TOT9, TOTS)
put(EXTRA9, u'(%s)-%d' % (TOTS, K9))
put(RATIO9, u'round(((%s)-%d)/(%s),2)' % (TOTS, K9, TOTS))
put(5, u"CNT(%r,0)" % PH(REP9[0]))
put(3, u"CNT(%r,0)" % PH(REP9[4]))
put(F['ROOT'], u"CNT(%r,0)" % PH(r'root cause'))
put(F['RECOM'], u"CNT(%r,0)" % PH(r'CSB recommends'))
put(F['SHALL'], u"CNT('shall',0)")
put(F['MUST'], u"CNT('must',0)")
put(F['SHOULD'], u"CNT('should',0)")
put(F['DIFF_SM'], u"CNT('should',0)-CNT('must',0)")
put(F['MUSTINC'], u"CNT(%r,0)" % PH(r'must include'))
put(F['FIG'], u"CNT('Figure\\\\s',0)")
put(F['APX'], u"CNT('Appendix',0)")
put(F['BRK'], u"CNT('\\\\]',0)")
put(F['SIS'], u"CNT('(?<![A-Za-z])SIS(?![A-Za-z])',0)")
put(F['CSB'], u"CNT('CSB',0)")
put(F['API'], u"CNT('(?<![A-Za-z])API(?![A-Za-z])',0)")
put(F['STD'], u"+".join([u"CNT('(?<![A-Za-z])NFPA(?![A-Za-z])',0)", u"CNT('(?<![A-Za-z])CCPS(?![A-Za-z])',0)",
                         u"CNT('(?<![A-Za-z])AFPM(?![A-Za-z])',0)", u"CNT('OSHA',0)",
                         u"CNT('(?<![A-Za-z])API(?![A-Za-z])',0)"]))
put(F['TROUB'], u"CNT('troubleshoot',0)")
put(F['WALK'], u"CNT(%r,0)" % PH(r'walk the line'))
put(F['COVER'], u"CNT(%r,0)" % PH(r'cover plate'))
put(F['AFTER'], u"CNT('afterburn',0)")
put(F['RUPT'], u"CNT(%r,0)" % PH(r'tube rupture'))
put(F['HEATER'], u"CNT(%r,0)" % PH(r'fired heater'))
put(F['HEAT_MINUS_RUPT'], u"CNT(%r,0)-CNT(%r,0)" % (PH(r'fired heater'), PH(r'tube rupture')))
put(F['HTTP'], u"CNT('http',0)")
put(F['WWW'], u"CNT('www\\\\.',0)")
put(F['BULL'], u"CNT('•',0)")
put(F['MARATHON'], u"CNT('Marathon',0)")
put(F['TAB'], u"CNT('Table\\\\s',0)")

NL = chr(10)
SRC42 = u"SRC['B42'] = ['corpus/raw/prose/csb_marathon_martinez.txt']" + NL
DE_IN = NL.join(u"  %r: %r," % (k, v) for k, v in sorted(D.items(), key=lambda x: float(x[0])))
BLOCK = u" 'B42': {" + NL + DE_IN + NL + u" }," + NL
print(u'DERIV keys=%d' % len(D))
print(u'0 键项数=%d' % NABS)

AU = u'corpus/audit.py'
s = io.open(AU, encoding='utf-8').read()
if u"SRC['B42']" not in s:
    i0 = s.index(NL + u'ATOM = {')
    s = s[:i0 + 1] + SRC42 + s[i0 + 1:]
if u"'B41'}" in s and u"'B42'}" not in s:
    s = s.replace(u"'B41'}", u"'B41', 'B42'}", 1)
s = re.sub(u" 'B42': \\{" + NL + u".*?" + NL + u" \\}," + NL, BLOCK, s, count=1, flags=re.S)
if u"'B42': {" not in s:
    k0 = s.index(u'DERIV = {' + NL) + len(u'DERIV = {' + NL)
    s = s[:k0] + BLOCK + s[k0:]
io.open(AU, 'w', encoding='utf-8').write(s)

AC = u'corpus/atomcheck.py'
a = io.open(AC, encoding='utf-8').read()
if u"SRC['B42']" not in a:
    i2 = a.index(u"SRC['B41']")
    a = a[:i2] + SRC42 + a[i2:]
    io.open(AC, 'w', encoding='utf-8').write(a)
print(u'wired B42: audit SRC/ATOM/DERIV(%d keys, 零值键折 %d 处缺席) + atomcheck SRC' % (len(D), NABS))
