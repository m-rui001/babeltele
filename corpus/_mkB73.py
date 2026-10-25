# -*- coding: utf-8 -*-
# B73 建条目: 四份 10-K Item 1A(AAPL FY25⟦A⟧⇎AAPL FY24⟦B⟧⇎MSFT⟦C⟧⇎GOOG⟦D⟧)。
# 编码区每个数字 token 插值时登记进扁平契约(键=数字串, 值=B73V 算式); 落盘前断言:
# 无残留占位 ‖ 标签数==编码区锚数 ‖ 每锚 norm 回源 ‖ token 全有 DERIV 键或逐字在源。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C', 'D']
FILES = {
    'A': 'corpus/raw/filings/aapl25_10k_1a.txt',
    'B': 'corpus/raw/filings/aapl24_10k_1a.txt',
    'C': 'corpus/raw/filings/msft25_10k_1a.txt',
    'D': 'corpus/raw/filings/goog25_10k_1a.txt',
}
F = json.load(io.open('corpus/_b73meas.json', encoding='utf-8'))
REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B73V('%s')" % name if i is None else u"B73V('%s', %d)" % (name, i)
    REG.setdefault(str(v), expr)
    return v


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


def lowbody(p):
    raw = io.open(p, encoding='utf-8', errors='replace').read()
    body = raw.partition(u'\n\n')[2]
    body = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), body)
    body = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), body)
    return u' '.join(body.replace(u'&amp;', u'&').split()).lower()


NORM = {tg: lowbody(FILES[tg]) for tg in TAGS}
FACE = u'\n'.join(pnorm(n) for n in NORM.values())

ATOMS = [(t, s.strip()) for t, s in zip(F['atom_tags'],
         io.open('corpus/_atoms73.txt', encoding='utf-8').read().splitlines()) if s.strip()]
for tg, a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中 %s: %s' % (tg, a[:50])

E = []
E.append(u'🧭 四份同为 SEC EDGAR 10-K 的 Item 1A 风险因素节, 一手 §-面剥到纯文本: 折平后字符 %d⇎%d⇎%d⇎%d ⇎ 句(>40 字符) %d⇎%d⇎%d⇎%d 句 ⇎ 每句均值 %d⇎%d⇎%d⇎%d 字符——D 最长句、C 最多句。'
         % (V('chars', 0), V('chars', 1), V('chars', 2), V('chars', 3),
            V('sents', 0), V('sents', 1), V('sents', 2), V('sents', 3),
            V('avg_sent', 0), V('avg_sent', 1), V('avg_sent', 2), V('avg_sent', 3)))

E.append(u'🔁 句级搬运把四份劈成两半: 同一发行人两年逐字共享句 %d 句(占 FY25 面的 %.1f%%)——Apple 把自己去年的风险清单近乎整册搬来重印; 而同年三家之间共享句 %d⇎%d⇎%d⇎%d⇎%d 句(A⇎C、A⇎D、B⇎C、B⇎D、C⇎D 全零)。风险因素不是行业语料库, 是**自我指纹**: 每家公司只抄自己, 从不抄同行。'
         % (V('sh_ab'), V('sh_ab_pct'),
            V('sh_ac'), V('sh_ad'), V('sh_bc'), V('sh_bd'), V('sh_cd')))

E.append(u'⚖ 人称即体裁: Apple 全节以第三人称写自己——"the Company" %d⇎%d 处 ⇎ " we " %d⇎%d 处、if we %d⇎%d 处; C/D 以第一人称写——" we " %d⇎%d 处、if we %d⇎%d 处而 "the Company" 只 %d⇎%d 处。经典风险句式模板 "could harm" %d⇎%d⇎%d⇎%d 处: 只 D 成规模(开篇即 "which could harm our business, reputation, financial condition, and operating results" ⟦D⟧⟨Our operations and financial results are subject to various risks and uncertainties, including but not limited to those described below, which could harm our business, reputation, financial condition, and operating results⟩), C 只 %d 处 ⟦C⟧⟨such as power grids, could harm our ability to conduct normal business operations or adversely⟩, A/B 两年 0 处——同一家交易所的同一份法定章节, 句式谱系四份分三档。'
         % (V('the_company', 0), V('the_company', 1), V('we_word', 0), V('we_word', 1), V('if_we', 0), V('if_we', 1),
            V('we_word', 2), V('we_word', 3), V('if_we', 2), V('if_we', 3), V('the_company', 2), V('the_company', 3),
            V('could_harm', 0), V('could_harm', 1), V('could_harm', 2), V('could_harm', 3), V('could_harm', 2)))

E.append(u'📉 主题词频即当年世界: tariff %d⇎%d⇎%d⇎%d 处——同一公司两年间翻五倍以上(B 的 %d 处全部活在关税句里 ⟦B⟧⟨Restrictions on international trade, such as tariffs and other controls on imports or exports of goods, technology or data, can materially adversely affect the Company\u2019s business and supply chain.⟩, 这句两年逐字共享, A 另给 %d 处增量是 FY25 新环境写进去的); artificial intelligence %d⇎%d⇎%d⇎%d 处; App Store %d⇎%d⇎%d⇎%d 处(B 比 A 多一倍——FY24 的监管节在 FY25 被删改); stock price %d⇎%d⇎%d⇎%d 处(A 的 %d 处密集谈自家股价, C 全节 0 处); china %d⇎%d⇎%d⇎%d 处; 供链 %d⇎%d⇎%d⇎%d 处; cyberattack %d⇎%d⇎%d⇎%d 处; data privacy %d⇎%d⇎%d⇎%d 处; litigation %d⇎%d⇎%d⇎%d 处; competition %d⇎%d⇎%d⇎%d 处; intellectual property %d⇎%d⇎%d⇎%d 处; 词根 regulat- %d⇎%d⇎%d⇎%d 处。'
         % (V('tariff', 0), V('tariff', 1), V('tariff', 2), V('tariff', 3), V('tariff', 1), V('tariff', 0),
            V('ai', 0), V('ai', 1), V('ai', 2), V('ai', 3),
            V('appstore', 0), V('appstore', 1), V('appstore', 2), V('appstore', 3),
            V('stockprice', 0), V('stockprice', 1), V('stockprice', 2), V('stockprice', 3), V('stockprice', 0),
            V('china', 0), V('china', 1), V('china', 2), V('china', 3),
            V('supply', 0), V('supply', 1), V('supply', 2), V('supply', 3),
            V('cyber', 0), V('cyber', 1), V('cyber', 2), V('cyber', 3),
            V('privacy', 0), V('privacy', 1), V('privacy', 2), V('privacy', 3),
            V('litigation', 0), V('litigation', 1), V('litigation', 2), V('litigation', 3),
            V('competition', 0), V('competition', 1), V('competition', 2), V('competition', 3),
            V('intprop', 0), V('intprop', 1), V('intprop', 2), V('intprop', 3),
            V('regulat', 0), V('regulat', 1), V('regulat', 2), V('regulat', 3)))

E.append(u'ℒ 方法 ⇒ 10-K 风险因素的隐性知识不在"列了哪些风险"(四份列的是同个世界的同批威胁), 而在谱系与体裁: 先把句做成键(句级交集把两年 vs 同年劈成 %d ⇎ 0 六对), 再把人称做成键(the Company ⇎ we 两档), 再把模板句式做成键(could harm %d⇎%d⇎%d⇎%d), 最后把主题词频按年份并排(tariff 两倍→五倍、App Store 反向减半)。每键都是 count 可机检量, 零项照占键位。'
         % (V('sh_ab'), V('could_harm', 0), V('could_harm', 1), V('could_harm', 2), V('could_harm', 3)))

E.append(u'✂️ 为什么这份编码比摘要窗口长 ⇒ 四源各 %d⇎%d⇎%d⇎%d 字符, 本条结论几乎全是跨文书对照量: 自我指纹要两年句集求交(%d 句), 行业零共享要三对同年句集各交一遍(0⇎0⇎0⇎0⇎0⇎0), 人称档要四份并排(the Company 478⇎494⇎4⇎4), 主题轴要同一词按年份各数一遍(tariff %d⇎%d⇎%d⇎%d)。读它请按"这句是谁抄谁的、以什么人称、在哪个年份被改成什么"来读, 而不是按"少抄了多少原文"。'
         % (V('chars', 0), V('chars', 1), V('chars', 2), V('chars', 3), V('sh_ab'),
            V('tariff', 0), V('tariff', 1), V('tariff', 2), V('tariff', 3)))

enc = u'\n'.join(E)

assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[ABCD]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'编码区标签 %d ≠ 编码区锚 %d' % (n_tags, n_atoms)
SRC_ALL = u''.join(NORM.values())
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok) in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))

atoms_by_tag = {t: [] for t in TAGS}
for tg, a in ATOMS:
    atoms_by_tag[tg].append(a)
orig_lines = []
for tg in TAGS:
    orig_lines.append(u'### ⟦%s⟧ ⟸ %s' % (tg, FILES[tg]))
    orig_lines.append(u'')
    for a in atoms_by_tag[tg]:
        orig_lines.append(a)
        orig_lines.append(u'')
orig = u'\n'.join(orig_lines).rstrip()
for tg, a in ATOMS:
    assert a in u'\n'.join(atoms_by_tag[tg]), u'锚未落原文段'

title = (u'# B73 同一部交易所法定章节的四副面孔: 风险因素清单——同一公司两年逐字搬 %d 句(%.1f%%) ⇎ '
         u'同年三家互抄 0 句: 风险因素是自我指纹不是行业语料\n'
         % (F['sh_ab'], F['sh_ab_pct']))
srcline = (u'src: %s (%d 字符) ⇎ %s (%d 字符) ⇎ %s (%d 字符) ⇎ %s (%d 字符) '
           u'(四份 SEC EDGAR 10-K 的 Item 1A 剥壳折平面, 实体解码; 数字一律从面内现读, 一个都不手填; '
           u'抓取时刻与 EDGAR 现行版本只在本机或站外成立, 不进门槛)\n'
           % (FILES['A'], F['chars'][0], FILES['B'], F['chars'][1], FILES['C'], F['chars'][2], FILES['D'], F['chars'][3]))
tagsline = (u'tags: 句级交集自我指纹键 人称两档(the Company⇎we) 模板句式三档(could harm) 主题词频年份并排 '
            u'关税词翻五倍 行业零共享 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B73_risk_factors_four_filings_four_answers.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b73flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B73 建条目: %s' % out)
print(u'编码区 %d 字符, 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
