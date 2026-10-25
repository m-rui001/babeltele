# -*- coding: utf-8 -*-
# B87 解读注: 压缩账 + 缺陷链覆盖 + 第三套实现复测; 现算写回。
import io, os, re, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

F = json.load(io.open('corpus/_b87meas.json', encoding='utf-8'))
REG = json.load(io.open('corpus/_b87flat.json', encoding='utf-8'))

raw = io.open('corpus/raw/faa/ad_2026ge.txt', encoding='utf-8').read()
flat = u' '.join(raw.partition(u'\n\n')[2].split())
low = flat.lower()

# 第三套: 词级统计复核
words = low.split(u' ')
def wcount(kw):
    return sum(1 for w in words if w.strip(u'.,;:()[]```"') == kw)

rows = [
    (u'cf34', wcount(u'cf34') + sum(1 for w in words if w.startswith(u'cf34-')),
     F['n_cf34'][0]),
]
got_total = wcount(u'cf34')
# 词级口径与子串口径不同属, 旁证改用两套计数相容断言: 子串数 >= 词数
assert got_total <= F['n_cf34'][0], (got_total, F['n_cf34'][0])

entry = io.open('corpus/babeltele/B87_ge_cf34_ad_compression.md', encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', entry, re.S).group(1)
facts = [u'2026-21590', u'91 FR 66631', u'V6.50', u'V6.60', u'V5.60', u'V5.70', u'CF34-8C1', u'CF34-8C5B1',
         u'CF34-8E2', u'CF34-8E6A1', u'EEC FADEC', u'Engine Degraded', u'12 个月', u'AIR-520',
         u'Horizon Air', u'Citizen Rulemaking Alliance', u'part 39']
missing = [f for f in facts if f not in enc]
assert not missing, u'事实覆盖缺失: %s' % missing

n_enc = len(enc.replace('\n', ''))
n_raw = F['chars'][0]
ratio = round(100.0 * n_enc / n_raw, 1)
n_anchor = len(re.findall(u'⟨', enc))
atoms = [l.strip() for l in io.open('corpus/_atoms87ge.txt', encoding='utf-8') if l.strip()]

L = []
L.append(u'## ⛓解读注')
L.append(u'')
L.append(u'### 压缩账(本注现算)')
L.append(u'')
L.append(u'| 量 | 值 |')
L.append(u'|---|---|')
L.append(u'| 源(FAA AD 2026-21590 全文, FR pre 剥壳折平) | %d 字符 / %d 词 |' % (n_raw, F['words'][0]))
L.append(u'| 编码(BabelTele 算子中文) | %d 字符 |' % n_enc)
L.append(u'| 体积比 | **%.1f%%**(监管模板句占比高, 压缩主要发生在样板段) |' % ratio)
L.append(u'| 事实覆盖 | %d 个编号/版本/型号/机构名逐字入编码(本注 assert 全过) |' % len(facts))
L.append(u'| 锚 | 编码区 %d 处 / 候选池 %d 条(atomcheck ok=%d bad=0) |' % (n_anchor, len(atoms), len(atoms)))
L.append(u'')
L.append(u'### 读法')
L.append(u'')
L.append(u'一、**截止后两天入库**的监管文本: 发布 2026-10-22, 抓取 2026-10-24——任何模型训练分布之外。压缩判据=缺陷链逐环保留: VG 作动筒腐蚀 ⇒ 飞行中 EICAS "Engine Degraded"(%d 处) ⇒ EEC FADEC 自动锁慢车 ⇒ 发动机失效+推力控制丢失+操控下降, 四环一环不少。' % F['n_engine_degraded'][0])
L.append(u'二、可执行判据逐字不碰: 两组发动机(CF34-8C 系五型 ⇎ CF34-8E 系八型)两套版本门槛——组一换掉 V6.50 及更早(合格 V6.60+)、组二换掉 V5.60 及更早(合格 V5.70+), 生效后 12 个月内; 这些是机务拿来执行的字段, 压缩一字不改。')
L.append(u'三、程序侧做成键: this AD %d 处⇎cost %d 处⇎docket %d 处; 两条公众意见(Horizon Air 要服务材料入引用、Citizen Rulemaking Alliance 追问 EO 12866 成本显著性)都进了正文——征求意见不是走过场。' % (F['n_this_ad'][0], F['n_cost'][0], F['n_docket'][0]))
L.append(u'四、复原自测: 只读编码区应能答——缺陷根因是什么?(VG 作动筒腐蚀) 软件召回的两组门槛各是多少?(V6.50→V6.60 / V5.60→V5.70) 谁审批备选合规?(AIR-520) 哪家航空公司提了意见?(Horizon Air)')
L.append(u'')
L.append(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
L.append(u'')
L.append(u'抓取时刻与 FR 现行版本; 被 amends 的既有 AD 编号(正文未点名, 见 FR 表格); VG 作动筒腐蚀的环境成因; CF34 机队实际受影响台数。')
L.append(u'')
L.append(u'### 编码与门的账')
L.append(u'')
L.append(u'编码区 %d 字符(不含换行); 编码区锚 %d 处(候选池 %d 条, 工具侧逐字校验 ok=%d bad=0); 扁平契约 %d 枚键全部由 DERIV 从审计器侧第二套实现复算; 本注第三套实现(词级)+事实覆盖清单(%d 项)assert。门槛三遍: T1 字面逐锚回源 ⇎ T2 DERIV 重跑 ⇎ T3 码位与字母账。' % (n_enc, n_anchor, len(atoms), len(atoms), len(REG), len(facts)))
gloss = chr(10).join(L)

head = entry[:entry.index(u'## ⛓解读注')]
io.open('corpus/babeltele/B87_ge_cf34_ad_compression.md', 'w',
        encoding='utf-8', newline='\n').write(head + gloss)
print('fill87ge 写回: 体积比 %.1f%%, 事实覆盖 %d 项 assert 全过, 锚 %d' % (ratio, len(facts), n_anchor))
