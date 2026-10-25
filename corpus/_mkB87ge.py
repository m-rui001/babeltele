# -*- coding: utf-8 -*-
# B87 建条目: 单文本压缩(FAA GE CF34 适航指令 2026-21590 → BabelTele)。数值/版本/型号逐字保真。
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

F = json.load(io.open('corpus/_b87meas.json', encoding='utf-8'))
REG = {}


def V(name):
    v = F[name][0]
    REG.setdefault(str(v), u"B87V('%s')" % name)
    return v


def pnorm(s):
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


raw = io.open('corpus/raw/faa/ad_2026ge.txt', encoding='utf-8', errors='replace').read()
FACE = pnorm(u' '.join(raw.partition(u'\n\n')[2].split()))

ATOMS = [l.strip() for l in io.open('corpus/_atoms87ge.txt', encoding='utf-8').read().splitlines() if l.strip()]
for a in ATOMS:
    assert pnorm(a) in FACE, u'锚未命中: %s' % a[:60]

E = []
E.append(u'🧭 源账: FAA AD 2026-21590(91 FR 66631, 2026-10-22, 修 14 CFR part 39), FR pre 剥壳折平 %d 字符⇎%d 词; docket %d 处、this AD %d 处、cost %d 处(成本章被 Citizen Rulemaking Alliance 依 Executive Order 追问后补登 docket 并公开征求意见)。'
         % (V('chars'), V('words'), V('n_docket'), V('n_this_ad'), V('n_cost')))

E.append(u'⚡ 缺陷链: 起因=VG(variable geometry, 可调几何系统)作动筒腐蚀 ⟦B⟧⟨corrosion of the variable geometry system actuator⟩⇒飞行中 EICAS 报 "Engine Degraded"(engine degraded %d 处)⇒不处理则 EEC FADEC 自动把发动机锁在慢车直至重启, 后果=一台或多台发动机失效+推力控制丢失+飞机操控下降。'
         % (V('n_engine_degraded')))

E.append(u'🔧 要求=纯软件召回: 拆役特定 EEC FADEC 软件版本并装合格版 ⟦A⟧⟨This AD requires removing certain electronic engine control (EEC) full authority digital electronic control (FADEC) software versions from service⟩——生效后 12 个月内完成; 合格判据按组分版本门槛: 组一(换掉 V6.50 及更早, 合格=V6.60 及以后已批版本)⇎组二(换掉 V5.60 及更早, 合格=V5.70 及以后已批版本)。'
         )
E.append(u'🧩 型号两组: 组一=CF34-8C1⇎CF34-8C5⇎CF34-8C5A1⇎CF34-8C5A2⇎CF34-8C5B1; 组二=⟦E⟧⟨GE Model CF34-8E2, CF34-8E2A1, CF34- 8E5, CF34-8E5A1, CF34-8E5A2, CF34-8E5A2HA, CF34-8E6, and CF34-8E6A1 engines⟩(cf34 全文 %d 处, eec fadec %d 处)——同族支线发动机按子型号分两套软件门槛。'
         % (V('n_cf34'), V('n_eec_fadec')))

E.append(u'🧾 程序侧: amends 既有 part 39 条款(amends %d 处); AMOC 备选合规由 AIR-520 Continued Operational Safety Branch 经理审批; Horizon Air 提请纳入服务材料(Service Material)入引用, Citizen Rulemaking Alliance 追问成本估算的 EO 12866 显著性判定——两意见都进了正文(horizon air %d 处)。'
         % (V('n_amends'), V('n_horizon_air')))

E.append(u'ℒ 方法 ⇒ 截止后监管文本的压缩判据: 缺陷链(腐蚀⇒信息⇒锁慢车⇒失控)逐环保留, 型号⇎软件版本门槛逐字保真(V6.50/V6.60⇎V5.60/V5.70 是可执行判据, 压缩不碰数字), 程序词频做成键(this ad %d⇎cost %d⇎unsafe condition %d)。'
         % (V('n_this_ad'), V('n_cost'), V('n_unsafe_condition')))

enc = u'\n'.join(E)

assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)
SRC_ALL = FACE.replace(u' ', u'')
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok) in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))

orig = u'### ⟦A⟧ ⟸ corpus/raw/faa/ad_2026ge.txt\n\n' + u'\n\n'.join(ATOMS)

title = (u'# B87 单文本压缩: FAA 适航指令 2026-21590(GE CF34, %d 词, 截止后冷门专业信息)→算子中文——'
         u'缺陷链逐环保留, 两组发动机两套软件版本门槛逐字保真\n' % F['words'][0])
srcline = (u'src: corpus/raw/faa/ad_2026ge.txt (%d 字符) '
           u'(单文本压缩: 源=Federal Register 2026-10-22 刊出的 GE 发动机 AD, FR pre 剥壳折平, 发布仅两天即入库; '
           u'数字与版本号一律逐字保留)\n' % F['chars'][0])
tagsline = (u'tags: 单文本压缩 截止后专业信息 缺陷链逐环保真键(腐蚀⇒EICAS⇒锁慢车⇒失控) 两组两门槛键(CF34-8C⇎8E, V6.x⇎V5.x) 程序词频键 锚归属由正文现推 闭合账 标量 2⇎清单 6 项\n')

md = (title + srcline + u'; ' + tagsline
      + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc
      + u'\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n')

out = u'corpus/babeltele/B87_ge_cf34_ad_compression.md'
io.open(out, 'w', encoding='utf-8', newline='\n').write(md)
json.dump(REG, io.open('corpus/_b87flat.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(u'B87 建条目: %s' % out)
print(u'编码区 %d 字符(不含换行), 编码区锚 %d 处, 扁平契约 %d 枚键' % (len(enc.replace(u'\n', u'')), n_atoms, len(REG)))
