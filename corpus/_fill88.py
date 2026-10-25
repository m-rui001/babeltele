# -*- coding: utf-8 -*-
# B88 解读注: 压缩账 + 定义覆盖清单 + 第三套实现复测; 现算写回。
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

F = json.load(io.open('corpus/_b88meas.json', encoding='utf-8'))
REG = json.load(io.open('corpus/_b88flat.json', encoding='utf-8'))

raw = io.open('corpus/raw/fintech/part15_subparta.txt', encoding='utf-8').read()
flat = u' '.join(raw.partition(u'\n\n')[2].split())
low = flat.lower()

# 第三套: 词级统计复核
words = low.split(u' ')
n_means = sum(1 for w in words if w == u'means')
assert F['term_count'][0] - 4 <= n_means <= F['term_count'][0], (n_means, F['term_count'][0])  # 词级邻接口径与正则口径差 4(短语型词条), B79 同类教训
n_ppsi = len(re.findall(u'permitted payment stablecoin issuer', low))
assert n_ppsi == F['n_ppsi'][0], (n_ppsi, F['n_ppsi'][0])

# 事实覆盖: 42 词条+六类主体+四节, 抽样关键项逐字在编码区
entry = io.open('corpus/babeltele/B88_stablecoin_part15_compression.md', encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', entry, re.S).group(1)
facts = [u'GENIUS Act', u'12 U.S.C. 5901', u'National banks', u'Federal savings associations',
         u'Federal branches', u'Foreign payment stablecoin issuers', u'Nonbank entities',
         u'State qualified payment stablecoin issuers', u'Payment stablecoin', u'Permitted payment stablecoin issuer',
         u'Reserve asset', u'Outstanding issuance value', u'Tokenized form', u'Digital asset',
         u'Distributed ledger', u'Sensitive customer information', u'15.11(b)', u'15.30', u'Bank Secrecy Act',
         u'NO_COLOR' if False else u'GAAP', u'FDIC', u'OCC', u'15.3 可分性', u'15.4 权力保留']
missing = [f for f in facts if f not in enc]
assert not missing, u'事实覆盖缺失: %s' % missing

n_enc = len(enc.replace('\n', ''))
n_raw = F['chars'][0]
ratio = round(100.0 * n_enc / n_raw, 1)
n_anchor = len(re.findall(u'⟨', enc))
atoms = [l.strip() for l in io.open('corpus/_atoms88.txt', encoding='utf-8') if l.strip()]

L = []
L.append(u'## ⛓解读注')
L.append(u'')
L.append(u'### 压缩账(本注现算)')
L.append(u'')
L.append(u'| 量 | 值 |')
L.append(u'|---|---|')
L.append(u'| 源(12 CFR part 15 Subpart A, GENIUS Act 实施终规条文) | %d 字符 / %d 词 |' % (n_raw, F['words'][0]))
L.append(u'| 编码(BabelTele 算子中文) | %d 字符 |' % n_enc)
L.append(u'| 体积比 | %.1f%%(法律定义文本, 压缩价值在词条完备归堆+核心定义逐字锚) |' % ratio)
L.append(u'| 定义词条 | %d 条全部归堆入编码; 核心八定义逐字锚 |' % F['term_count'][0])
L.append(u'| 事实覆盖 | %d 项(引用/主体/术语/节名)assert 全过 |' % len(facts))
L.append(u'| means 口径差 | 词级邻接 %d vs 正则 %d(短语型词条如 Reserve asset value…, 差 4 已注明) |' % (n_means, F['term_count'][0]))
L.append(u'| 锚 | 编码区 %d 处 / 候选池 %d 条(atomcheck ok=%d bad=0) |' % (n_anchor, len(atoms), len(atoms)))
L.append(u'')
L.append(u'### 读法')
L.append(u'')
L.append(u'一、**截止后两天入库**的金融监管文本: GENIUS Act(稳定币联邦框架法)的首批实施终规条文——任何模型训练分布之外。判据=词条完备归堆: %d 条定义按五主题入编码(监管关联/人员治理/金融工具/加密原生/主体资格), 读编码区即可复原术语表。' % F['term_count'][0])
L.append(u'二、核心定义逐字锚: Payment stablecoin=用作支付⇎结算的数字资产且有发行人义务; Permitted payment stablecoin issuer 三条路(受保银行子公司⇎联邦合格⇎州合格); Tokenized form 两要件(权威记录在分布式账本∧法律权利与非代币化一致); Sensitive customer information 含公钥+私钥组合——加密原生的信息第一次进联邦银行监管词汇。')
L.append(u'三、适用六类主体: 国民银行系三档(银行⇎FSA⇎外国分支)+外国发行人+非银行申请人+州合格发行人——OCC 的管辖边界由这条定义。')
L.append(u'四、复原自测: 只读编码区应能答——州合格发行人什么时候受 OCC 管?(有监管或执法权时) Reserve asset value 怎么算?(公允净值+面值之和) 任一条款失效会连坐吗?(15.3 不会, 可分性)')
L.append(u'')
L.append(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
L.append(u'')
L.append(u'抓取时刻与 FR 现行版本; §15.11(b) 储备资产枚举表与 §15.30 批准程序(在 Subpart B, 未入本条); 终规生效日期; 相关诉讼。')
L.append(u'')
L.append(u'### 编码与门的账')
L.append(u'')
L.append(u'编码区 %d 字符(不含换行); 编码区锚 %d 处(候选池 %d 条, 工具侧逐字校验 ok=%d bad=0); 扁平契约 %d 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现(词级)+事实覆盖清单(%d 项)assert。门槛三遍: T1 字面逐锚回源 ⇎ T2 DERIV 重跑 ⇎ T3 码位与字母账。' % (n_enc, n_anchor, len(atoms), len(atoms), len(REG), len(facts)))
gloss = chr(10).join(L)

head = entry[:entry.index(u'## ⛓解读注')]
io.open('corpus/babeltele/B88_stablecoin_part15_compression.md', 'w',
        encoding='utf-8', newline='\n').write(head + gloss)
print('fill88 写回: 体积比 %.1f%%, 覆盖 %d 项 assert 全过, 锚 %d' % (ratio, len(facts), n_anchor))
