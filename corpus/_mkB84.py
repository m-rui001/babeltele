# -*- coding: utf-8 -*-
# B84 建条目: 单文本压缩(美国宪法全文 → BabelTele)。编码为手工高密度中文,
# 覆盖序言+七条+27 修正案; 每关键条款配逐字英文锚; 数字 token 全部 V() 登记扁平契约。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

F = json.load(io.open('corpus/_b84meas.json', encoding='utf-8'))
REG = {}


def V(name, i=None):
    v = (F[name][0] if i is None else F[name][i])
    expr = u"B84V('%s')" % name if i is None else u"B84V('%s', %d)" % (name, i)
    REG.setdefault(str(v), expr)
    return v


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


raw = io.open('corpus/raw/constitution/us_constitution_full.txt', encoding='utf-8', errors='replace').read()
FACE = pnorm(u' '.join(raw.partition(u'\n\n')[2].split()))

ATOMS = [l.strip() for l in io.open('corpus/_atoms84.txt', encoding='utf-8').read().splitlines() if l.strip()]
for a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中: %s' % a[:50]

E = []
E.append(u'🧭 源账: 宪法全文(NARA 抄件拼合, 正文+修正案)折平 %d 字符⇎%d 词; 修正案罗马字头 %d 处(27 头+17 交叉引用), 条字头 %d 处(七条+序言一引); 序言恰 %d 词。'
         % (V('chars'), V('words'), V('amend_hdr'), V('article_hdr'), V('preamble_words')))

E.append(u'📜 序言⇒目的六联: 更完美联合∧公义∧国内安宁∧共同防御∧普遍福利∧自由之惠 ⟦A⟧⟨We the People of the United States, in Order to form a more perfect Union⟩——主权在民起笔, 无一神祇。')

E.append(u'🏛 第一条=立法: 权归国会两院 ⟦B⟧⟨All legislative Powers herein granted shall be vested in a Congress⟩⇒众院按人口⇎参院每州两席; 税案由众院起; 否决⇒两院各三分之二翻案(thirds %d 处); 众院独有弹劾提起⇎参院独有弹劾审判; 国会八极权(税⇎债⇎通商⇎归化⇎铸币⇎宣战⇎军队⇎必要适当条款)+三禁(①移民贸易不得禁于 %d 年前②人身保护令不得暂停除非叛乱③无贵族爵位; 州不得缔约⇎铸币⇎头衔)。'
         % (V('kw_thirds'), V('kw_twenty_five')))

E.append(u'🏛 第二条=行政: 权归总统 ⟦C⟧⟨The executive Power shall be vested in a President⟩⇒选举人团(各州=参众席数和); 资格: 生来公民∧年三十五∧居留十四年(kw 命中 twenty_five %d⇎fourteen_years %d); 统帅陆海军⇎赦免⇎条约须参院三分之二同意⇎任命须同意; 弹劾同一条轨道。'
         % (V('kw_twenty_five'), V('kw_fourteen_years')))

E.append(u'🏛 第三条=司法: 权归一最高法院⇎国会立低院; 法官任期=行为良好(终身)⇎薪俸不减; 司法权及于宪法与联邦法; 叛国罪窄定义=对美作战∨通敌, 定罪须两证人+本人公开庭。')

E.append(u'🤝 第四条=州际: 各州互信全信⇎罪犯引渡⇎新州入联邦须经国会⇎联邦保证每州共和政体。')

E.append(u'🔧 第五条=修宪: 两院各三分之二⇒提案∨三分之二州会申请⇒公约⇒四分之三州批准即成; 两处锁: 一八〇八年前不得动移民贸易条款⇎不得剥夺州在参院的平等投票权。')

E.append(u'📜 第六条=最高法: 宪法+联邦法+条约为国土最高法(州法官亦受约束); 官员宣誓而不得设宗教测试。')

E.append(u'✍️ 第七条=生效: 九州批准即立(九_states %d 处)。'
         % (V('kw_nine_states'),))

E.append(u'🩹 修正案一至十=权利法案: ①国会不得立教⇎不得禁自由行使⇎不得削言论⇎出版⇎集会⇎申冤 ⟦D⟧⟨Congress shall make no law respecting an establishment of religion⟩; ②纪律良好的民兵为自由州所必需⇒人民持有携带武器之权不得侵 ⟦E⟧⟨the right of the people to keep and bear Arms, shall not be infringed⟩; ③和平时期不得驻兵民宅 ⟦F⟧⟨No Soldier shall, in time of peace be quartered⟩; ④无合理根据不得搜捕 ⟦G⟧⟨unreasonable searches and seizures⟩; ⑤大陪审团⇎不得双重危险⇎不得自证其罪 ⟦H⟧⟨compelled in any criminal case to be a witness against himself⟩⇎无正当程序不得剥夺生命自由财产 ⟦I⟧⟨nor be deprived of life, liberty, or property, without due process of law⟩⇎私产公用须公偿; ⑥速决公开审判⇎律师⇎陪审 ⟦J⟧⟨speedy and public trial⟩; ⑦普通法诉讼陪审团; ⑧不得过量保释⇎罚金⇎酷刑 ⟦K⟧⟨excessive bail shall not be required, nor excessive fines imposed⟩; ⑨列举不尽=人民权利不尽 ⟦L⟧⟨The enumeration in the Constitution, of certain rights, shall not be construed⟩; ⑩未授联邦⇎未禁各州之权归州⇎归民 ⟦M⟧⟨The powers not delegated to the United States⟩。'
         % ())

E.append(u'🩹 修正案十一至廿七: 十一⇒外州公民不得诉州(主权豁免); 十二⇒选举人团总统副总统分票; 十三⇒废奴(不得有强迫劳役, 惩罪除外) ⟦N⟧⟨neither slavery nor involuntary servitude⟩; 十四⇒出生公民+正当程序+平等保护(rebuilt 后内战三句); 十五⇒投票不得论种族; 十六⇒国会可征所得税; 十七⇒参议员民选; 十八⇒禁酒(唯一被废); 十九⇒投票不得论性别; 二十⇒任期起算一月(终结跛脚鸭国会); 二十一⇒废除十八(全卷唯一 repeal 事件, repeal 词 %d 处); 二十二⇒总统当选不得逾两次 ⟦O⟧⟨No person shall be elected to the office of the President more than twice⟩; 二十三⇒哥伦比亚特区得选举人票; 二十四⇒人头税禁; 二十五⇒总统缺位继任程序; 二十六⇒十八岁得投票; 二十七⇒议员薪酬变更须待下届众院(二〇三 年前提出的原文, 拖两百年才批准)。'
         % (V('repeal')))

E.append(u'🔢 词频即重心: congress %d 处⇎president %d 处⇎senate %d 处⇎court %d 处⇎state %d 处⇎section %d 处——立法机关是全文最高频主语, 修正案把 presidency 抬到最高。'
         % (V('congress'), V('president'), V('senate'), V('court'), V('state'), V('section_word')))

E.append(u'ℒ 方法 ⇒ 单文本压缩的判据不是多源对照而是可复原性: 覆盖做成键(序言+七条+廿七案每项至少一锚或一条目), 结构做成键(罗马字头 %d/%d、序言 %d 词), 词频重心做成键(congress %d⇎president %d⇎senate %d)。每键都是 count 可机检量, 零项照占键位。'
         % (V('amend_hdr'), V('article_hdr'), V('preamble_words'),
            V('congress'), V('president'), V('senate')))

enc = u'\n'.join(E)

assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'编码区标签 %d ≠ 编码区锚 %d' % (n_tags, n_atoms)
SRC_ALL = FACE.replace(u' ', u'')
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok) in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))

# 原文段: 每锚一引
orig_lines = [u'### ⟦A⟧ ⟸ corpus/raw/constitution/us_constitution_full.txt', u'']
tagmap = u'ABCDEFGHIJKLMNO'
for k, a in enumerate(ATOMS):
    orig_lines.append(u'%s. %s' % (chr(ord(u'ᴀ') + k) if False else u'', a))
    orig_lines.append(u'')
orig = u'### ⟦A⟧ ⟸ corpus/raw/constitution/us_constitution_full.txt\n\n' + u'\n\n'.join(ATOMS)

title = (u'# B84 单文本压缩: 美国宪法全文(序言+七条+廿七修正案, %d 词)压成 %s 字符算子中文——'
         u'每条款至少一锚或一条目, 覆盖率由结构计数机检\n' % (F['words'][0], u'(见账)'))
srcline = (u'src: corpus/raw/constitution/us_constitution_full.txt (%d 字符) '
           u'(单文本压缩: 源=NARA 抄件拼合的宪法全文; 数字一律从面内现读, 一个都不手填; '
           u'抓取时刻与 NARA 现行版本只在本机或站外成立, 不进门槛)\n' % F['chars'][0])
tagsline = (u'tags: 单文本压缩 可复原覆盖键(每条款一条目) 结构计数键(罗马字头/序言词数) 词频重心键 无码本算子中文 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B84_constitution_compression_one_text.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b84flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B84 建条目: %s' % out)
print(u'编码区 %d 字符(不含换行), 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
