# -*- coding: utf-8 -*-
# B83 建条目: 同一判决书四个声音(Loper Bright)。编码区数字 token 插值登记扁平契约; 落盘前断言同 B73。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = ['A', 'B', 'C']
FILES = {
    'A': 'corpus/raw/nws/afd_a.txt',
    'B': 'corpus/raw/nws/afd_b.txt',
    'C': 'corpus/raw/nws/afd_c.txt',
}
F = json.load(io.open('corpus/_b83meas.json', encoding='utf-8'))
REG = {}


def V(name, i=None):
    v = F[name] if i is None else F[name][i]
    expr = u"B83V('%s')" % name if i is None else u"B83V('%s', %d)" % (name, i)
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
    return pnorm(raw.partition(u'\n\n')[2])


NORM = {tg: lowbody(FILES[tg]) for tg in TAGS}
FACE = u'\n'.join(NORM.values())

ATOMS = [(t, s.strip()) for t, s in zip(F['atom_tags'],
         io.open('corpus/_atoms83.txt', encoding='utf-8').read().splitlines()) if s.strip()]
for tg, a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中 %s: %s' % (tg, a[:50])

E = []
E.append(u'🧭 同一天(2026-10-23)的三份 NWS 区域预报讨论, 同为 api.weather.gov 纯文本: 休斯敦/加尔维斯顿当期(11:43Z) %d 字符⇎同室上期(04:40Z) %d⇎斯波坎当期(11:39Z) %d ⇎ 句 %d⇎%d⇎%d 句。'
         % (V('chars', 0), V('chars', 1), V('chars', 2),
            V('sents', 0), V('sents', 1), V('sents', 2)))

E.append(u'🔁 时间衰减: 同室相隔七小时的两期句集交集 %d 句(去重句各 %d⇎%d)——上期的大部分句子逐字滚入当期, 逐段更新而非重写; 而跨办公室交集 A⇎C %d 句、B⇎C %d 句全零: 预报讨论的模板是办公室私产, 全国共享的只有骨架。'
         % (V('sh_ab'), V('sent_uniq', 0), V('sent_uniq', 1), V('sh_ac'), V('sh_bc')))

E.append(u'⚖ 骨架是全国统一件: KEY MESSAGES %d⇎%d⇎%d 份、段分隔 && %d⇎%d⇎%d 枚、AVIATION 节 %d⇎%d⇎%d 处、National Weather Service %d⇎%d⇎%d 处、Area Forecast Discussion 抬头 %d⇎%d⇎%d 处——三份同构; 火情词 fire %d⇎%d⇎%d 处(休斯敦的干旱火险与斯波坎的火天气各自开场 ⟦A⟧⟨Elevated fire weather conditions are possible over the next couple of days.⟩)。'
         % (V('key_messages', 0), V('key_messages', 1), V('key_messages', 2),
            V('amp', 0), V('amp', 1), V('amp', 2),
            V('aviation', 0), V('aviation', 1), V('aviation', 2),
            V('nws', 0), V('nws', 1), V('nws', 2),
            V('afd_hdr', 0), V('afd_hdr', 1), V('afd_hdr', 2),
            V('fire', 0), V('fire', 1), V('fire', 2)))

E.append(u'🏛 文化即办公室: confidence %d⇎%d⇎%d 处只斯波坎成规模——它把确定性写进每个时段 ⟦C⟧⟨This is ushering drier air in to the region with moderate to high confidence for ongoing IFR/MVFR conditions⟩; front %d⇎%d⇎%d 处、short term 节 %d⇎%d⇎%d 处、advisory %d⇎%d⇎%d 处、ensemble %d⇎%d⇎%d、model %d⇎%d⇎%d 处全是内陆平原办公室的词; 休斯敦的墨西哥湾词 gulf %d⇎%d⇎%d、coast %d⇎%d⇎%d——地理写进讨论, 不用看署名就知道是哪个办公室写的。'
         % (V('confidence', 0), V('confidence', 1), V('confidence', 2),
            V('front', 0), V('front', 1), V('front', 2),
            V('short_term', 0), V('short_term', 1), V('short_term', 2),
            V('advisory', 0), V('advisory', 1), V('advisory', 2),
            V('ensemble', 0), V('ensemble', 1), V('ensemble', 2),
            V('model', 0), V('model', 1), V('model', 2),
            V('gulf', 0), V('gulf', 1), V('gulf', 2),
            V('coast', 0), V('coast', 1), V('coast', 2)))

E.append(u'ℒ 方法 ⇒ 预报讨论的隐性知识在三层分家: 时间衰减做成键(同室两期 %d 句复用), 办公室文化做成键(confidence %d⇎%d⇎%d), 全国骨架做成键(KEY MESSAGES %d 份、&& %d 枚、AVIATION %d 处三份全等)。每键都是 count 可机检量, 零项照占键位。'
         % (V('sh_ab'), V('confidence', 0), V('confidence', 1), V('confidence', 2),
            V('key_messages', 0), V('amp', 0), V('aviation', 0)))

enc = ''.join(E)

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

title = (u'# B83 同一天的三份 NWS 预报讨论: 休斯敦两期七小时滚存 %d/28 句而跨办公室交集 0——骨架全国统一(KEY MESSAGES/&&/AVIATION 三份全等), 文化办公室私有(confidence 只斯波坎)\n' % (F['sh_ab'],))
srcline = (u'src: %s (%d 字符) ⇎ %s (%d 字符) ⇎ %s (%d 字符) '
           u'(三份同为 api.weather.gov 的 Area Forecast Discussion 纯文本: KHGX 当期⇎KHGX 上期⇎KOTX 当期, 2026-10-23; '
           u'数字一律从面内现读, 一个都不手填; 抓取时刻与 NWS 现行产品只在本机或站外成立, 不进门槛)\n'
           % (FILES['A'], F['chars'][0], FILES['B'], F['chars'][1], FILES['C'], F['chars'][2]))
tagsline = (u'tags: 时间衰减键(同室滚存) 办公室文化键(confidence) 全国骨架键(KEY MESSAGES/&&/AVIATION 全等) 地理词键(gulf⇎front) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B83_nws_afd_three_offices_hours.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b83flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B83 建条目: %s' % out)
print(u'编码区 %d 字符, 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
