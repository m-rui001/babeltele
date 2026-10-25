# -*- coding: utf-8 -*-
# B43 两份抓取同一 URL: 判决文书 ⇎ 该文书的发布页(容器)。锚点从空白折叠后的原文切片(逐字由构造保证),
# 判词里的每个数字都写进 DERIV 并由各自文件回算(发布页=索引 0, 判决=索引 1)。
# 计数口径与 audit 的 _reason() 一致: 只剔除 ^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:) 行, url: 行留在源内。
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')

RAW0 = u'corpus/raw/prose/law_aviator_spribe.txt'      # 发布页(容器)
RAW1 = u'corpus/raw/prose/law_ewca_aviator.txt'        # 判决全文
ENTRY = u'corpus/babeltele/B43_ewca_aviator_judgment_vs_landing_page.md'
LC, LJ = u'C', u'J'
HEADRX = r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)'


def split(p):
    lines = io.open(p, encoding='utf-8', errors='replace').read().split(u'\n')
    hdr = [l for l in lines if re.match(HEADRX, l.strip(), re.I)]
    return hdr, lines, u'\n'.join([l for l in lines if l not in hdr])


HDR0, L0, BC = split(RAW0)
HDR1, L1, BJ = split(RAW1)
# 锚点只从“连 url 行也剔掉”的纯正文切片, 免得锚跨进抓取留下的网址串; 计数仍走 audit 的口径(含 url 行)。
clean = lambda t: chr(10).join(l for l in t.split(chr(10)) if not l.strip().lower().startswith(u'url:'))
CC = re.sub(r'\s+', ' ', clean(BC))
CJ = re.sub(r'\s+', ' ', clean(BJ))


def PH(p):
    if p.startswith(u'(?') or u'\\' in p:
        return p
    return r'\s+'.join(re.escape(w) for w in p.split(u' '))


def NC(pat, where=BC):
    return len(re.findall(pat, where, re.I))


def NJ(pat):
    return NC(pat, BJ)



# ---------- 判决内部 ----------
FIFTH, SIXTH = NJ(PH('Fifth Party')), NJ(PH('Sixth Party'))
PARTY = NJ('Party')
assert FIFTH == SIXTH == 2, (FIFTH, SIXTH)
HDRMW, RUNHDR = NJ(PH('Approved by the court for handing down')), NJ(PH('Aviator v Spribe'))
assert HDRMW == RUNHDR, (HDRMW, RUNHDR)
AGREE, ALSO, WOULD = NJ(PH('I agree')), NJ(PH('I also agree')), NJ(PH('I would allow'))
assert AGREE == ALSO == WOULD == 1, (AGREE, ALSO, WOULD)
RESJ, ISSE, ESTP = NJ(PH('res judicata')), NJ(PH('issue estoppel')), NJ('estoppel')
ROME, COPR, CRASH = NJ(PH('Rome II')), NJ('copyright'), NJ(PH('crash game'))
GEO = NJ('Georgia')
BRK, PAR = NJ(r'\[\d{4}\]'), NJ(r'\(\d{4}\)')
DIF_BP = BRK - PAR
COURT_J, AVI_J, SPRI_J = NJ('Court'), NJ('Aviator'), NJ('Spribe')
OJ = NJ(PH(u'OÜ'))
DIF_NAME = SPRI_J - OJ
assert PAR == 1 and OJ == 1, (PAR, OJ)

# ---------- 发布页内部 ----------
COURT_C, SEARCH_C = NC('Court'), NC('Search')
VF, VFJ = NC('-v-'), NJ('-v-')
DIF_V = VF - VFJ
assert VF == 4 and VFJ == 1, (VF, VFJ)
ORS_C, ORS_J = NC('Ors'), NJ('Ors')
OC = NC(PH(u'OÜ'))

ABS_J = [PH('Skip to main content'), 'Download', r'\.pdf', r'569\.88', r'H\.-D\.', 'Search']
ABS_C = [PH('issue estoppel'), PH('Rome II'), PH('res judicata'), PH('I agree'), PH('would allow'),
         PH('Approved by the court'), PH('crash game'), 'estoppel', PH('lex fori'), PH('handing down'),
         PH('Fifth Party'), 'Georgia']
for a in ABS_J:
    assert NJ(a) == 0, (a, NJ(a))
for a in ABS_C:
    assert NC(a) == 0, (a, NC(a))
NABS = len(ABS_J) + len(ABS_C)
assert NABS == 18, NABS   # 判词里以中文数词“十九项”写出, 此处守护它与实际项数一致
F = dict(PARTY=PARTY, HDRMW=HDRMW, RUNHDR=RUNHDR, ALSO=ALSO, RESJ=RESJ, ISSE=ISSE, ESTP=ESTP,
         ROME=ROME, COPR=COPR, CRASH=CRASH, GEO=GEO, BRK=BRK, PAR=PAR, DIF_BP=DIF_BP,
         COURT_J=COURT_J, COURT_C=COURT_C, AVI_J=AVI_J, SPRI_J=SPRI_J, OJ=OJ, OC=OC,
         DIF_NAME=DIF_NAME, VF=VF, DIF_V=DIF_V, ORS_C=ORS_C, ORS_J=ORS_J, SEARCH_C=SEARCH_C, NABS=NABS)
print(u'FACTS %s' % (F,))


# ---------- 锚点(逐字由构造保证) ----------
def mk(Col):
    def S(key, pre=170, post=210):
        m = re.search(re.escape(key), Col, re.I)
        assert m, u'KEY MISS: ' + key
        ks, ke = m.start(), m.end()
        head = Col[max(0, ks - pre):ks]
        mm = None
        for x in re.finditer(u'[.;:]\\s', head):
            mm = x
        a = max(0, ks - pre) + (mm.end() if mm else 0)
        tail = Col[ke:min(len(Col), ke + post)]
        m2 = re.search(u'[.;:]\\s', tail)
        if m2 is None:
            b = ke + len(tail)
        elif m2.start() == 0:
            b = ke
        else:
            b = ke + m2.end() - 1
        return Col[a:b].strip().rstrip(u' ,;')

    def AK(*cands, **kw):
        for k in cands:
            if re.search(re.escape(k), Col, re.I):
                return S(k, kw.get('pre', 170), kw.get('post', 210))
        raise AssertionError(u'ALL MISS: ' + cands[0][:60])
    return S, AK


SJ, AJ = mk(CJ)
SC, AC2 = mk(CC)

AN = {}
AN['neutral'] = AJ(u'Neutral Citation Number', pre=25, post=90)
AN['caseno'] = AJ(u'Case No: CA-2026-001508', pre=25, post=90)
AN['lower'] = AJ(u'Michael Tappin KC sitting as a Deputy High Court Judge', pre=120, post=90)
AN['bench'] = AJ(u'LADY JUSTICE KING', pre=45, post=110)
AN['parties'] = AJ(u'(1) AVIATOR LLC', pre=45, post=200)
AN['defendant'] = AJ(u'SPRIBE OÜ', pre=90, post=60)
AN['andand'] = AJ(u'- and -', pre=60, post=120)
AN['hearing'] = AJ(u'Hearing date', pre=110, post=40)
AN['approved'] = AJ(u'Approved by the court for handing down', pre=90, post=90)
AN['date'] = AJ(u'Date: 2 October 2026', pre=25, post=90)
AN['issue1'] = AJ(u'The issue on this appeal is what law applies', pre=90, post=230)
AN['fifth'] = AJ(u'The Claimants and the Fifth Party', pre=90, post=140)
AN['bg3'] = AJ(u'The First Claimant and the Fifth Party are companies', pre=90, post=200)
AN['sixth'] = AJ(u'The Second and Third Claimants are companies', pre=120, post=170)
AN['crash'] = AJ(u'A crash game is an online gambling game', pre=70, post=200)
AN['logo'] = AJ(u'under the logo reproduced below', pre=140, post=120)
AN['loci'] = AJ(u'lex loci protectionis', pre=170, post=140)
AN['romeii'] = AJ(u'Rome II Regulation', pre=170, post=140)
AN['paren'] = AJ(u'(1843) 3 Hare 100', pre=140, post=110)
AN['concl'] = AJ(u'I would allow the appeal', pre=110, post=40)
AN['agree1'] = AJ(u'I agree.', pre=90, post=40)
AN['agree2'] = AJ(u'I also agree.', pre=90, post=40)
AN['skip'] = AC2(u'Skip to main content', pre=15, post=120)
AN['searchnav'] = AC2(u'Search on Courts and Tribunals Judiciary', pre=60, post=90)
AN['coroners'] = AC2(u'Coroners', pre=90, post=140)
AN['ctitle'] = AC2(u'Between :', u'Between:', pre=90, post=190)
AN['cvform'] = AC2(u'-v- SPRIBE', u'-v-', pre=140, post=60)
AN['cdate'] = AC2(u'2 October 2026', pre=120, post=120)
AN['filename'] = AC2(u'.pdf file', pre=190, post=25)
AN['size'] = AC2(u'569.88', pre=60, post=60)
AN['cright'] = AC2(u'Copyright Judiciary', pre=90, post=60)
C_SET = (u'skip', u'searchnav', u'coroners', u'ctitle', u'cvform', u'filename', u'size', u'cright',
         u'cdate')
LBL_OF = dict((k, LC) for k in AN if k in C_SET)
LBL_OF.update((k, LJ) for k in AN if k not in C_SET)
for k, v in AN.items():
    src = CC if LBL_OF[k] == LC else CJ
    assert re.sub(r'\s+', ' ', v).strip() in src, k
    assert 15 <= len(v) <= 430 or k in (u'agree1', u'agree2'), (k, len(v))
print(u'anchors=%d (页 %d / 判 %d)' % (len(AN), sum(1 for v in LBL_OF.values() if v == LC),
                                      sum(1 for v in LBL_OF.values() if v == LJ)))

# ---------- 判词 ----------
L = []


def A(head, atoms, gloss):
    parts = [u'⟦%s⟧⟨%s⟩' % (LBL_OF[k], AN[k]) for k in atoms]
    L.append(u'%s %s ⇒ %s' % (head, u' ‖ '.join(parts), gloss))


A(u'🧭 体例：同一网址的两份抓取', [u'neutral', u'ctitle'],
  u'两条 raw 的 url 相同、抓取时间相隔一分钟余(记在条首 src 行, 不入机检), 长度相差一个数量级。'
  u'一份是 ⟦{J}⟧{neu} 所在的判决全文, 另一份是发布它的那个网页 ⟦{C}⟧{ct} ——只有导航与元数据。'
  u'此前各条的“对照”都是两份同类文书互相比, 本条把对照轴换成**文书 ⇎ 文书的容器**: '
  u'容器不承载推理, 却承载文书自身没有的可下载标识。'.format(J=LJ, neu=AN['neutral'], C=LC, ct=AN['ctitle']))
A(u'🏛 标题里的当事人 ⇎ 正文里的当事人', [u'parties', u'fifth', u'bg3'],
  u'页与判决首页都只列三个 Aviator 实体加一个 Spribe ⟦{J}⟧{p}。判决正文里却出现 ⟦{J}⟧{f} 与 ⟦{J}⟧{b}, '
  u'“party”这一称谓在该文件 {party} 次(机检 {party}), 当事人名称 “Aviator” 本身 {avi} 次(机检 {avi})。 '
  u'判词: 首页的当事人列表是**诉讼地位的快照**, 正文的编号是**责任分配的账本**——页里那个 “and others” '
  u'把标题外的其余各方一并抹平(页里只保留标题级的缩写, 判决正文才把它们写成有编号的一方); '
  u'按标题统计“几方当事人”必然少数, 而本案的争点恰恰是“哪一方的判决可被援引为既判力”。'.format(
      J=LJ, p=AN['parties'], f=AN['fifth'], b=AN['bg3'], party=F['PARTY'], avi=F['AVI_J']))
A(u'🔖 同一案件的两种字面写法', [u'cvform', u'andand', u'defendant'],
  u'页里案件标题写作 ⟦{C}⟧{v}: “-v-” 这种标题式写法在发布页 {vf} 次, 比判决全文多 {vfd} 处(机检 {vfd})——判决里那一次是抓取留下的 url 串, 不是标题写法'
  u'判决把同一关系写成编号列表与 ⟦{J}⟧{aa}。 '
  u'同型飘移还有被告名称: 全名带爱沙尼亚变音符 ⟦{J}⟧{d}, 而正文几乎只用简称——Spribe {spi} 次, 比带变音符的全名多 {dif} 次'
  u'(机检 {spi} ⇎ {dif}); 页里则把全名印在标题上 ⟦{C}⟧{cd}。 '
  u'引“全名”与引“简称”是两套命中集; 规范化把 Ü 读成 U, 这两套就并成一套。'.format(
      C=LC, v=AN['cvform'], vf=F['VF'], vfd=F['DIF_V'], J=LJ, aa=AN['andand'], d=AN['defendant'],
      spi=F['SPRI_J'], dif=F['DIF_NAME'], cd=AN['cdate']))
A(u'🌐 文件名把判决首页压成一行', [u'filename', u'size', u'hearing', u'date'],
  u'判决全文里没有 “Download”、没有 “.pdf”、没有体积、没有文件名里的 “H.-D.”(全部折进 0 键), 而页里有 '
  u'⟦{C}⟧{fn} 与 ⟦{C}⟧{sz}。那行文件名把案号、当事人、日期编成一个串, 串里的日期对应判决的听证日 ⟦{J}⟧{h}, '
  u'而不是宣判日 ⟦{J}⟧{dt}——宣判日写在文书首页, 页面上以 ⟦{C}⟧{cd} 的形式重复印了同一块头部。 '
  u'判词: 用文件名给本案定日期会把宣判日写成听证日; 只有把两份抓取并置, 才看得见“文件名里没有宣判日”这件事。'.format(
      C=LC, fn=AN['filename'], sz=AN['size'], J=LJ, h=AN['hearing'], dt=AN['date'], cd=AN['cdate']))
A(u'📑 页界以页眉残留计数', [u'approved'],
  u'转本没有“Page ”页码标记, 但有每页重印的页眉: ⟦{J}⟧{a} 在判决全文 {hd} 次(机检 {hd}); '
  u'另一句每页重印的跑动标题 “Aviator v Spribe” 与它同值, 故不另立机检键。与 B42 相反——那份报告的页数只存在于抓取头部、'
  u'正文无法反推; 这里的页数**可以从正文数出来**, 因为排版把同一句话复印在每一页上。 '
  u'判词: 转换丢掉的版式会以残迹的方式回来; 凡“每页重印”的套语, 其次数就是页界计数, 而它同时是“本文为法院核准文本”的自我声明。'.format(
      J=LJ, a=AN['approved'], hd=F['HDRMW']))
A(u'⚖️ 结论是虚拟语气, 附和是一整段里的一句话', [u'concl', u'agree1', u'agree2'],
  u'判决末三段: ⟦{J}⟧{c} ⇎ ⟦{J}⟧{g1} ⇎ ⟦{J}⟧{g2}。前一句用 “would” 而不是 “do”, 因为上诉审只提出意见、'
  u'令文由下级按意见拟具; 后两句是另外两位法官在该文件里的全部发言, 其中 ⟦{J}⟧{g2} 计数 {al} 次(机检 {al})。 '
  u'判词: 合议制文书的“集体”只体现在署名行 ⟦{J}⟧{bn}, 推理全部出自一人; 摘要若一律写成“法院认为”, '
  u'就把“一人论证＋两人签字”这个结构读没了, 而这个结构决定了哪一段说理具有拘束力。'.format(
      J=LJ, c=AN['concl'], g1=AN['agree1'], g2=AN['agree2'], al=F['ALSO'], bn=AN['bench']))
A(u'🈚 争点由拉丁语命名, 括号解释只写一次', [u'issue1', u'loci', u'romeii'],
  u'首段 ⟦{J}⟧{i} 把争点定在 res judicata 与其下位概念 issue estoppel: 全篇 “issue estoppel” {isse} 次 '
  u'⇎ “res judicata” {resj} 次 ⇎ “estoppel” {estp} 次(机检 {isse} ⇎ {resj} ⇎ {estp}), '
  u'对方主张的依据 Rome II {rome} 次、诉因 copyright {copr} 次(机检 {rome} ⇎ {copr})。 '
  u'两个拉丁术语(⟦{J}⟧{lo} 与 lex fori)首次出现时各挂一个英语 gloss 括号, 之后不再解释: gloss 是一次性的, '
  u'术语的可读性却全靠它——引用者删掉括号, 这份判决对非本国法律人就成了缩写串。'.format(
      J=LJ, i=AN['issue1'], isse=F['ISSE'], resj=F['RESJ'], estp=F['ESTP'], rome=F['ROME'],
      copr=F['COPR'], lo=AN['loci']))
A(u'🔢 引证格式自己说明可核方式', [u'neutral', u'paren', u'lower'],
  u'判决里方括号年 {brk} 次, 比圆括号年多 {dif} 次(机检 {brk} ⇎ {dif}), 即差出来的那一处 ⟦{J}⟧{pa}: '
  u'一个 1843 年的旧报告引证——圆括号年意味着年份不是识别符, 必须连同卷号才定位得到; '
  u'而 ⟦{J}⟧{n} 与一审号 ⟦{J}⟧{lo} 这类方括号中性引用把年份编进编号本身, 无需任何报告卷。 '
  u'判词: 引用格式不是排版偏好, 而是“该文献靠什么被找到”的说明; 规范化把两种括号读成一种, 就把这条信息删了。'.format(
      brk=F['BRK'], dif=F['DIF_BP'], J=LJ, pa=AN['paren'], n=AN['neutral'], lo=AN['lower']))
A(u'🖼 被主张的客体是一张图, 不是一句陈述', [u'logo', u'crash'],
  u'本案是版权之诉, 而权利客体写在 ⟦{J}⟧{lg}: 图样在原文里“reproduced below”, 转本只留下这行字与一个名称 '
  u'“the Aviator Image”, 客体本身不在文本里。玩法说明 ⟦{J}⟧{cr} 倒是以文字给了 {crash} 次(机检 {crash}), '
  u'当事一方的注册地 Georgia {geo} 次(机检 {geo})。 '
  u'判词: B42 那里图是**证据**(丢了图还有文可读), 这里图是**诉因的客体**(丢了图就没有争议对象)——'
  u'同为“图不在文本”, 可压缩性完全不同; 后者只能改引段号与图名, 不能自称还原了图。'.format(
      J=LJ, lg=AN['logo'], cr=AN['crash'], crash=F['CRASH'], geo=F['GEO']))
A(u'🚫 缺席的是两份文本各自的全体', [u'searchnav', u'issue1'],
  u'“Skip to main content”“Search”“Download”“.pdf”“569.88”“H.-D.”在判决全文 0 次; '
  u'“issue estoppel”“Rome II”“res judicata”“I agree”“would allow”“Approved by the court”“crash game”“estoppel”'
  u'“lex fori”“handing down”“Fifth Party”“Georgia”在发布页 0 次——共十八项折进一个 0 键(逐项已在句上列出)。 '
  u'这不是抓取失败(两份各自完好 ⟦{C}⟧{s} ⇎ ⟦{J}⟧{i}), 而是**容器与内容互不包含**: '
  u'检索“本案涉及既判力”只能命中判决, 检索“判决文件的体积与下载入口”只能命中页。一份不能替代另一份, 所以本条两份都存。'.format(
      C=LC, s=AN['searchnav'], J=LJ, i=AN['issue1']))
A(u'✂️ 长度不是信息量, 关键词也不是', [u'coroners', u'cright', u'caseno'],
  u'发布页里导航词 Court {court} 次(机检 {court}), 那些是法院清单 ⟦{C}⟧{co} 一类, 与本案无关; '
  u'判决全文里 Court 同样出现 {courtd} 次(机检 {courtd} ⇎ {court}), 却是“上诉法院 ⇎ 一审判决”的实质用词。 '
  u'另一处同词不同义: 页尾 ⟦{C}⟧{cr} 的 “copyright” 是网站版权声明, 而判决里该词 {copr} 次指的是诉因(机检 {copr})。 '
  u'至于案件标识, 判决首页同时给 ⟦{J}⟧{cn} 与 ⟦{J}⟧{n} 两个号, 页里另给一个由文件名生成的第三个号——'
  u'三份标识彼此不可互推, 引用时必须指定用了哪一个。'.format(
      court=COURT_C, C=LC, co=AN['coroners'], courtd=COURT_J, cr=AN['cright'], copr=F['COPR'],
      J=LJ, cn=AN['caseno'], n=AN['neutral']))
A(u'∴ 骨架', [],
  u'① 对照轴可以是文书与其发布页, 不必是两份同类文书; ② 首页当事人列表是快照, 正文编号是账本, 按标题数当事人必少; '
  u'③ “-v-”与编号列表是同一案件的两种字面形式; ④ 全名带变音符而简称不带, 引全名与引简称是两套命中集; '
  u'⑤ 文件名里的日期是听证日, 宣判日只写在文书里; ⑥ 页界可由每页重印的页眉次数反推, 与抓取头部自记页数是两条独立证据; '
  u'⑦ 上诉结论用虚拟语气, 附和各一段⇒论证出自一人; ⑧ 拉丁术语的括号 gloss 只写一次; '
  u'⑨ 方括号年与圆括号年说明两种定位方式; ⑩ 版权案的客体是图, 转本丢的是诉因对象而非证据; '
  u'⑪ 容器与内容互不包含, 故两份都得存; ⑫ 同词在两份里可能同形不同义(网站版权 ⇎ 诉因); ⑬ 案件标识有三个, 彼此不可互推。')
A(u'ℒmethod', [u'filename', u'approved'],
  u'读“文书＋其网页”这一对: 先确认两份抓取的 url 是否相同(相同才构成容器对照, 不同就是两份文书), '
  u'再把页里的每个字段拿去判决全文做子串比对, 把“只在页里有”的列成一张清单(文件名、体积、下载入口), '
  u'把“只在文书里有”的列成另一张(推理、段号、引证格式); 两张清单的交集才是可省量, 并集才是本案的可核事实。 '
  u'凡遇每页重印的套语(⟦{J}⟧{a} 一类)先数次数, 它给出正文自身的页界; 凡遇“标题里的当事人”必须回正文找编号称谓, 不能停在标题。 '
  u'计数口径必须与审计一致: 抓取头部里只剔除非 url 的字段行, 否则同一条 url 会给两份文件各加一次命中。 '
  u'本条核验: 标注 {C} 的锚只在发布页内比对, 标注 {J} 的锚只在判决全文内比对, 两者不互换。'.format(
      J=LJ, a=AN['approved'], C=LC))

BODY_MD = u'\n'.join(L)

HEAD_MD = (u'# B43 判决与它的发布页：文件名里的日期是听证日，而“第几方”只写在正文里\n\n'
           u'src: {r0} (judiciary.uk 发布页, 容器) ⇎ {r1} ([2026] EWCA Civ 1224 Aviator LLC & Ors v Spribe OÜ, '
           u'判决全文 {n1} 字符 ⇎ {ln} 行; 同一 url, 两次抓取相隔 65 秒)\n'
           u'tags: 判例 引用完整性 文书⇎容器 当事人计数 页界残迹 变音符降级 虚拟语气 拉丁术语\n\n').format(
               r0=RAW0, r1=RAW1, n1=len(BJ), ln=len(L1))

MD = (HEAD_MD + u'## [[原始语料|ORIGINAL]]\n\n## ⟪BabelTele⟫\n' + BODY_MD + u'\n\n## ⛓解读注\n<!--FILL-->\n')
io.open(ENTRY, u'w', encoding='utf-8').write(MD)
ATOMS = re.findall(u'⟨([^⟨⟩]+)⟩', BODY_MD)
io.open(u'corpus/_atoms43.txt', u'w', encoding='utf-8').write(u'\n'.join(ATOMS) + u'\n')
print(u'entry written: %s body_chars=%d atoms=%d' % (ENTRY, len(BODY_MD), len(ATOMS)))

# ---------- DERIV(键名即数值; 0=发布页, 1=判决全文) ----------
D = {}


def put(val, expr):
    k = (u'%g' % float(val))
    assert k not in D, (k, expr)
    D[k] = expr
    return k


ZERO = u'+'.join([u"CNT(%r,1)" % a for a in ABS_J] + [u"CNT(%r,0)" % a for a in ABS_C])
put(0, ZERO)
put(F['ALSO'], u"CNT(%r,1)" % PH('I also agree'))
put(F['OC'], u"CNT(%r,0)" % PH(u'OÜ'))
put(DIF_V, u"CNT('-v-',0)-CNT('-v-',1)")
put(F['CRASH'], u"CNT(%r,1)" % PH('crash game'))
put(F['GEO'], u"CNT('Georgia',1)")
put(F['PARTY'], u"CNT('Party',1)")
put(F['RESJ'], u"CNT(%r,1)" % PH('res judicata'))
put(F['HDRMW'], u"CNT(%r,1)" % PH('Approved by the court for handing down'))
put(F['DIF_NAME'], u"CNT('Spribe',1)-CNT(%r,1)" % PH(u'OÜ'))
put(F['SPRI_J'], u"CNT('Spribe',1)")
put(F['ISSE'], u"CNT(%r,1)" % PH('issue estoppel'))
put(F['ROME'], u"CNT(%r,1)" % PH('Rome II'))
put(F['COPR'], u"CNT('copyright',1)")
put(F['COURT_C'], u"CNT('Court',0)")
put(F['ESTP'], u"CNT('estoppel',1)")
put(F['DIF_BP'], u"CNT(%r,1)-CNT(%r,1)" % (r'\[\d{4}\]', r'\(\d{4}\)'))
put(F['BRK'], u"CNT(%r,1)" % r'\[\d{4}\]')
put(F['COURT_J'], u"CNT('Court',1)")
put(F['AVI_J'], u"CNT('Aviator',1)")

NL = chr(10)
SRC43 = u"SRC['B43'] = ['%s', '%s']" % (RAW0, RAW1) + NL
DE_IN = NL.join(u"  %r: %r," % (k, v) for k, v in sorted(D.items(), key=lambda x: float(x[0])))
BLOCK = u" 'B43': {" + NL + DE_IN + NL + u" }," + NL
print(u'DERIV keys=%d' % len(D))
print(u'0 键项数=%d' % NABS)

AU = u'corpus/audit.py'
s = io.open(AU, encoding='utf-8').read()
if u"SRC['B43']" not in s:
    i0 = s.index(NL + u'ATOM = {')
    s = s[:i0 + 1] + SRC43 + s[i0 + 1:]
if u"'B42'}" in s and u"'B43'}" not in s:
    s = s.replace(u"'B42'}", u"'B42', 'B43'}", 1)
s = re.sub(u" 'B43': \\{" + NL + u".*?" + NL + u" \\}," + NL, BLOCK, s, count=1, flags=re.S)
if u"'B43': {" not in s:
    k0 = s.index(u'DERIV = {' + NL) + len(u'DERIV = {' + NL)
    s = s[:k0] + BLOCK + s[k0:]
io.open(AU, 'w', encoding='utf-8').write(s)

AC = u'corpus/atomcheck.py'
a = io.open(AC, encoding='utf-8').read()
if u"SRC['B43']" not in a:
    i2 = a.index(u"SRC['B42']")
    a = a[:i2] + SRC43 + a[i2:]
    io.open(AC, 'w', encoding='utf-8').write(a)
print(u'wired B43: audit SRC/ATOM/DERIV(%d keys, 零值键折 %d 处缺席) + atomcheck SRC' % (len(D), NABS))
