# -*- coding: utf-8 -*-
# B88 建条目: 单文本压缩(12 CFR part 15 Subpart A, GENIUS Act 实施, 2026-10-23)。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

F = json.load(io.open('corpus/_b88meas.json', encoding='utf-8'))
REG = {}


def V(name):
    v = F[name][0]
    REG.setdefault(str(v), u"B88V('%s')" % name)
    return v


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


raw = io.open('corpus/raw/fintech/part15_subparta.txt', encoding='utf-8', errors='replace').read()
FACE = pnorm(u' '.join(raw.partition(u'\n\n')[2].split()))

ATOMS = [l.strip() for l in io.open('corpus/_atoms88.txt', encoding='utf-8').read().splitlines() if l.strip()]
for a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中: %s' % a[:60]

E = []
E.append(u'🧭 源账: 12 CFR part 15 Subpart A(GENIUS Act 实施终规, 91 FR 67000, 2026-10-23, OCC)——宗旨/适用/定义/可分性, 折平 %d 字符⇎%d 词; 定义词条 %d 条(permitted payment stablecoin issuer %d 处, reserve %d 处)。'
         % (V('chars'), V('words'), V('term_count'), V('n_ppsi'), V('n_reserve')))

E.append(u'🎯 15.1 宗旨与适用: 本部分实施 GENIUS Act(12 U.S.C. 5901 et seq.)中 OCC 有权立规⇎执法的部分; 适用六类主体的稳定币相关活动⇎特定托管活动 ⟦A⟧⟨(1) National banks and their subsidiaries; (2) Federal savings associations and their subsidiaries; (3) Federal branches and their subsidiaries; (4) Foreign payment stablecoin issuers; (5) Nonbank entities that seek to be or are approved as Federal qualified payment stablecoin issuers; and (6) State qualified payment stablecoin issuers for which the OCC has regulatory or enforcement authority⟩——国民银行系三档+外国发行人+非银行申请人+州合格发行人(OCC 有权者)。')

E.append(u'📖 15.2 定义 %d 条, 核心八条: ①Payment stablecoin=数字资产(用作支付⇎结算手段)且发行人有义务 ⟦B⟧⟨That is, or is designed to be, used as a means of payment or settlement⟩——可赎回⇎稳定机制; ②Permitted payment stablecoin issuer=美国境内组建的 (a)受保国民银行/FSA 已批子公司⇎(b)Federal qualified issuer(OCC 按 §15.30 批准: 非银行实体⇎无保险国民银行)⇎(c)State qualified issuer; ③Reserve asset=按 §15.11(b) 枚举类型维持的资产; Reserve asset value=储备公允价值(除美国铸币货币)净负债+面值之和; ④Outstanding issuance value=全部已发稳定币票面总值; ⑤Tokenized form 两要件: 权威记录用分布式账本维护∧法律权利与非代币化工具完全一致; ⑥Digital asset=记录在密码学保护分布式账本上的价值数字表示; ⑦Distributed ledger 两要件: 数据跨网共享成公共账本∧密码学链接保完整性; ⑧Sensitive customer information=可还原身份⇎可入账户的信息组合——含公钥+私钥组合。'
         % (V('term_count')))

E.append(u'🗂 其余词条按主题归堆(均逐字在源): 监管关联 = Bank Secrecy Act(三源: FDIA §21⇎P.L. 91-508 章 2⇎31 U.S.C. 5311)⇎FDIC⇎Federal Reserve⇎OCC⇎State payment stablecoin regulator; 人员治理 = Board of directors⇎Director(无投票权的顾问董事除外)⇎Executive officer⇎Insider⇎Principal shareholder⇎Immediate family⇎Affiliate(控制/被控制/同受控制); 金融工具 = Deposit⇎Depository institution⇎Insured depository institution⇎Share account⇎Money⇎Monetary value⇎National currency⇎GAAP⇎Fair value; 加密原生 = Digital asset⇎Distributed ledger⇎Private key⇎Publicly available information⇎Tokenized form; 主体资格 = Customer⇎United States customer⇎Eligible financial institution⇎Nonbank entity⇎Foreign payment stablecoin issuer⇎Payment stablecoin holder。')

E.append(u'🔧 15.3 可分性: 任一条款失效不连坐其余; 15.4 权力保留: OCC 保留按 GENIUS Act 必要时再立规的权力(金融稳定⇎及时赎回⇎持有人债权保护三目的)。')

E.append(u'ℒ 方法 ⇒ 新规章定义节的压缩判据: 词条完备做成键(%d 条全部归堆入编码), 核心定义逐字锚(八条), 结构节(宗旨/可分性/权力保留)各自成行——读编码区即可复原"谁被监管⇎关键术语何义⇎OCC 保留了什么"。'
         % (V('term_count'),))

enc = u'\n'.join(E)

assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)
SRC_ALL = pnorm(u' '.join(raw.split())).replace(u' ', u'')
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok) in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))

orig = u'### ⟦A⟧ ⟸ corpus/raw/fintech/part15_subparta.txt\n\n' + u'\n\n'.join(ATOMS)

title = (u'# B88 单文本压缩: 12 CFR part 15 Subpart A(GENIUS Act 稳定币实施终规, %d 词, 截止后冷门专业信息)→算子中文——'
         u'六类适用主体+42 条定义归堆, 核心八定义逐字锚\n' % F['words'][0])
srcline = (u'src: corpus/raw/fintech/part15_subparta.txt (%d 字符) '
           u'(单文本压缩: 源=Federal Register 2026-10-23 刊出的 OCC 稳定币终规条文, FR pre 剥壳折平, 发布即入库; '
           u'数字与法条引用一律逐字保留)\n' % F['chars'][0])
tagsline = (u'tags: 单文本压缩 截止后专业信息 定义完备键(42 条归堆) 核心定义逐字锚(八条) 适用主体键(六类) 条款结构键(可分性/权力保留) 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B88_stablecoin_part15_compression.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b88flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B88 建条目: %s' % out)
print(u'编码区 %d 字符(不含换行), 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
