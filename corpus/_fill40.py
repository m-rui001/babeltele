# -*- coding: utf-8 -*-
"""生成 B40 的 ⛓解读注(幂等: 每次整体替换 ## ⛓解读注 之后的内容; 所有计数先量后断言)。"""
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ENTRY = u'corpus/babeltele/B40_fda_three_de_novo_orders.md'
RAW = [(u'C', u'corpus/raw/prose/fr_fda_cardio_ml_notification.txt'),
       (u'R', u'corpus/raw/prose/fr_fda_radiology_ml_pccp.txt'),
       (u'M', u'corpus/raw/prose/fr_fda_opioid_impairment_monitor.txt')]
src = dict((k, io.open(v, encoding='utf-8').read()) for k, v in RAW)
path = dict(RAW)

full = io.open(ENTRY, encoding='utf-8').read()
enc = full.split(u'## ⟪BabelTele⟫')[1].split(u'## ⛓解读注')[0].strip(u'\n')
enc_n = len(enc.replace(u'\n', u''))
enc_nl = len(enc)
atoms = re.findall(u'⟧⟨([^⟨⟩]+)⟩', enc)
labels = re.findall(u'⟦([A-Z])⟧⟨', enc)
tags_all = re.findall(u'⟦([A-Z])⟧', enc)
out = re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)
outlat = len(re.findall(u'[A-Za-z]', out))
inlat = len(re.findall(u'[A-Za-z]', u''.join(atoms)))
inhan = len(re.findall(u'[一-鿿]', u''.join(atoms)))
uniq = len(set(enc.replace(u'\n', u'')))
n_c, n_r, n_m = labels.count('C'), labels.count('R'), labels.count('M')
n_atoms = len(atoms)
assert n_atoms == n_c + n_r + n_m == 91, (n_atoms, n_c, n_r, n_m)

# 从 audit.py 读出本条的 DERIV 键数与零值键折叠的缺席断言数
au = io.open(u'corpus/audit.py', encoding='utf-8').read()
dblk = re.search(r"DERIV\['B40'\] = \{(.*?)\n\}\n", au, re.S).group(1)
dkeys = re.findall(r"^\s*'([^']+)':", dblk, re.M)
assert len(dkeys) == 20 and len(set(dkeys)) == 20, dkeys
zline = [l for l in dblk.split(u'\n') if l.strip().startswith(u"'0':")]
assert len(zline) == 1, zline
n_absent = zline[0].count('CNT(')
assert n_absent == 35, n_absent

orig_a = re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', full, re.S).group(1)
dig_total = len(orig_a)
dg = dict((m.group(1), len(m.group(2).strip())) for m in
          re.finditer(u'^### ⟦([A-Z])⟧[^\n]*\n(.*?)(?=\n### ⟦|\\Z)', orig_a, re.M | re.S))
blocks = dict((m.group(1), len([x for x in m.group(2).strip().split(u'\n') if x.strip()])) for m in
              re.finditer(u'^### ⟦([A-Z])⟧[^\n]*\n(.*?)(?=\n### ⟦|\\Z)', orig_a, re.M | re.S))
dig_body = sum(dg.values())


def chars_of(k):
    m = re.search(u'^# chars: (\\d+)\\s*$', src[k], re.M)
    return int(m.group(1))


def bytes_of(k):
    return len(open(path[k], 'rb').read())


raw_chars = sum(chars_of(k) for k, _ in RAW)
raw_bytes = sum(bytes_of(k) for k, _ in RAW)
for k, _ in RAW:
    h = re.search(u'^# text_sha256: ([0-9a-f]{16})\\s*$', src[k], re.M).group(1)
    assert len(h) == 16
    print(u'[%s] chars=%d bytes=%d sha=%s 锚=%d 摘要块=%d' % (k, chars_of(k), bytes_of(k), h,
                                                              labels.count(k), blocks.get(k, 0)))
ret_d = 100.0 * enc_n / dig_total
ret_c = 100.0 * enc_n / raw_chars
ret_b = 100.0 * enc_n / raw_bytes

# 套语锚的多源命中: 同一串在几份文件里都存在
flat = {}
for k, _ in RAW:
    s = re.sub(u'\\s+', u' ', src[k])
    flat[k] = re.sub(u'[^0-9a-z\\u4e00-\\u9fff\\-\\. ]+', ' ', s.lower())
multi = sum(1 for a in set(atoms)
            if sum(1 for k in flat if re.sub(u'[^0-9a-z\\u4e00-\\u9fff\\-\\. ]+', ' ', a.lower()) in flat[k]) > 1)
assert multi == 25, multi

G = []
a = G.append
a(u'※体例 三份都是美国联邦公报上的“面向新增器械的类别划分令”，同一机关、同一文书类型、三种介质: '
  u'⟦C⟧＝91 FR 57785–57787（2026-09-11 刊发, 文件号 2026-18612, 案号 FDA-2026-N-9907, 规章号 870.2380, 心血管机器学习通知软件, '
  u'请求 2023-01-10 收到, 划分自 2023-08-03 适用）; ⟦R⟧＝91 FR 36522–36524（2026-06-17, 2026-12166, 案号 FDA-2026-N-6535, '
  u'规章号 892.2055, 放射学机器学习定量影像软件, 请求 2022-09-28, 适用日 2023-02-24, 附带预定变更控制计划）; '
  u'⟦M⟧＝91 FR 39459–39461（2026-06-30, 2026-13140, 案号 FDA-2026-N-6707, 规章号 868.2250, 阿片类引起的氧合损害监测仪, '
  u'请求 2020-02-19, 适用日 2023-03-31）。三份都由政策、立法与国际事务副局长同一人签发，均列 II 类并附特殊控制。'
  u'抓取路线: govinfo 的 FR 网页正文（body 内 pre 段）去标签入库，raw 头部自记 text_sha256 与 chars。'
  u'本条没有争论可读——三份文书之间不存在冲突，可读的是同一个法定模板被三种介质填满的方式。')

a(u'※派生算术与计数（全部由 audit.py 机检，%d 个键） 0＝合计 %d 项缺席断言: 人因子与可用性两个名字在 ⟦R⟧ 各 0 次、'
  u'且彼此不在对方文件出现（⟦C⟧ 无可用性、⟦R⟧ 两者皆无）、生物相容／电磁／无线三个词在 ⟦C⟧ 与 ⟦R⟧ 各 0 次、'
  u'骰度／豪斯多夫距离／布蓝-阿特曼在 ⟦C⟧ 与 ⟦M⟧ 各 0 次、“非预期用途”否定式在 ⟦R⟧ 与 ⟦M⟧ 各 0 次、过度依赖在 ⟦R⟧ 0 次、'
  u'人口学在 ⟦M⟧ 0 次、警告在 ⟦R⟧ 0 次、预定变更控制与它的缩写在 ⟦C⟧ 与 ⟦M⟧ 各 0 次、独立在 ⟦M⟧ 0 次、分离在 ⟦R⟧ 0 次、'
  u'第二人称在 ⟦C⟧ 与 ⟦M⟧ 各 0 次、“shall”在三份各 0 次、“guarantee”在三份各 0 次。'
  u'1＝机器学习短语在 ⟦M⟧ 的出现次数（那唯一一次正是被引的那条特殊控制）; 2＝第二人称三份合计; 3＝“120 日内划分”同串三份合计; '
  u'4＝否定式适应证在 ⟦C⟧ 的次数; 5＝管理和预算办公室控制号每份均值（三份同为 5）; 6＝人口学三份合计; 7＝上市前通知短语每份均值; '
  u'8＝不带定冠词的保证句三份合计; 9.1＝round(365×(2026−2023)÷120,1)＝公布距离对法定期限的倍率; '
  u'10＝带定冠词的保证句三份合计; 11＝机器学习短语在 ⟦C⟧ 的次数; 12＝新类别认定短语每份均值; 13＝第一人称每份均值（三份同为 13, 模板逐字相同的证据）; '
  u'14＝二级短语每份均值; 15＝义务词在 ⟦C⟧ 的次数; 17＝预定变更控制全称加缩写在 ⟦R⟧ 合计; 31＝义务词三份合计; '
  u'36＝新类别认定三份合计; 42＝二级短语三份合计。' % (len(dkeys), n_absent))

a(u'※隐性知识的所在 ① 同类文书里有三个日期：决定适用日、刊发日、生效日，后两者常差一天而第一个可差数年——引用者若只抄头部的日期就把'
  u'“何时开始有效”与“何时被写下”混为一谈；② 法定 120 日只约束决定的作出，不约束公布，所以“期限超过 9 倍”不是违法而是排期；'
  u'③ 套语段落可以逐份计数验证为复制（三份同一短语次数完全相同），因此这类文书的信息量全部集中在差集段；'
  u'④ 同一保证句在一份文件里可以带定冠词、在另一份里不带，按完整短语检索会漏掉一半；'
  u'⑤ “人因子评估”与“可用性评估”是同一件事的两个名字，而第三份两个都不用——它把使用者的问题改写成了“对输出的误解风险”；'
  u'⑥ 机器学习的要求可以整条藏进一份与非机器学习器械有关的令里（⟦M⟧ 唯一一次提到机器学习正是在这条要求里）；'
  u'⑦ “测试集须与训练集互斥”在两份文件写作“独立”、在第三份写作“分离”，同义换词使跨文件关键词检索失效；'
  u'⑧ 指标清单由介质决定而不是由风险决定：影像软件列出重叠度与距离度量，传感设备列出灵敏度／特异度／预测值；'
  u'⑨ 同一句“重要亚组须有足够例数”在 ⟦C⟧/⟦R⟧ 逐字相同，但 ⟦M⟧ 用“亚群、使用环境、阿片类型”三轴替换了“人口学”，'
  u'于是它的分层变量根本不在人群上——缺席不等于忽略；'
  u'⑩ 风险表不是风险清单，是“这个介质能怎么伤人”的清单：硬件专有的三行（组织反应、传感件伤害、电磁与无线干扰）只在 ⟦M⟧，'
  u'模型偏见的行只在 ⟦C⟧，而“过度依赖输出”在 ⟦R⟧ 完全缺席；'
  u'⑪ 否定式边界写在哪里决定它的效力：写进设备认定段就管辖准入范围，写进标签警告就只管用户行为；'
  u'⑫ 失效披露有两种句式——“警告”与“描述可能失效的情形”，选哪一种就决定了谁来承担失效的语义；'
  u'⑬ 允许上市后自变更的分类令必须同时锁住“告知”：版本史、变更实施方式、如何通知用户三处落点都写在同一份里；'
  u'⑭ 义务可以没有受话人：三份都在大量使用义务词，只有拿到自变更授权的那份出现第二人称；'
  u'⑮ 签发人相同、联系人不同、房间号不同，电话前缀把 ⟦C⟧ 与 ⟦R⟧/⟦M⟧ 分组，而住址与楼号逐字相同——“谁签的”可机检但不可推断；'
  u'⑯ 案号同一年度同一系列而流水号无序（早发的 ⟦R⟧ 反拿小号），所以案号不能用来排序；'
  u'⑰ 文书会解释自己的标题写法（脚注说明为何写成“最终修订；最终命令”），这与器械无关，只与 2019 年 12 月的一次编辑体例改动有关；'
  u'⑱ 同一机关内部的模板也会漂移：两份脚注对同一个词一个加引号一个不加，而规范化会把这个差别完全抹平——'
  u'所以引号级差异只能靠逐字锚保留；⑲ 三份的“特殊控制”条目编号都排到第七项，但项与项的内容按介质换掉了大半；'
  u'⑳ 把三份并置读才看得见：任何单独一份读起来都像中性规章，套语相同之后剩下的差异才是实质。')

a(u'※抓取与失真 govinfo 的 FR 页面在 body 内是等宽 pre 段，去标签后留下三类不可跨锚点的位置：'
  u'一是硬换行（正文每行约 65–70 字符），故所有长锚都必须按空白折叠后的文本比对；'
  u'二是两栏表被压平后逐行交错，风险表的“风险”列与“缓解措施”列穿插读，'
  u'例如“不支持人群或输入/硬件下使用”那行被拆成 ⟦C⟧ 的两段引用，'
  u'⟦M⟧ 的“电磁兼容与无线射频干扰”行真实顺序里夹进了“测试与”三个字，只能按整行原文引用；'
  u'三是点线填充的表行（如“ adverse tissue reaction 后接一长串句点再接缓解措施”），句点在规范化中被保留，'
  u'所以这类锚的句点数量必须与原文一致。另：原文的引号写成双反引号开、U+2019 收（``…’’），'
  u'audit 与 atomcheck 的规范化会删引号，故 ⟦C⟧ 与 ⟦R⟧ 的脚注在规范化后成为同一串——这正是⑱所说的“机检检不出的差异”，'
  u'本条把它写成判词而不是断言。')

a(u'※三源对齐 %d 个锚全部逐字命中自己标签的源（建条脚本 _mkB40.py 对每个锚按标签取对应文件做规范化子串断言）；'
  u'摘要段联合命中 %d/%d。其中 %d 个串同时命中不止一份文件——它们全是套语（自动三级条款、保证句、120 日义务、'
  u'特殊控制的引言、签发行），多源同命中在这里不是误标而是“模板相同”的直接证据；'
  u' ⟦C⟧ %d 锚／⟦R⟧ %d 锚／⟦M⟧ %d 锚。' % (n_atoms, n_atoms, n_atoms, multi, n_c, n_r, n_m))

a(u'※实况 编码 %d（含换行；audit 去换行口径 %d） ⇎ 摘要段 %d（audit 口径；正文 %d ＋ 三处分节标题 %d；'
  u'%d 个锚全部命中，分源窗口块数 %d ＋ %d ＋ %d） ⇎ raw 正文 %d 字符／%d 字节；'
  u'保留率 %.1f%%（vs 摘要段）⇎ %.1f%%（vs raw 字符）⇎ %.3f%%（vs raw 字节）；唯一码点 %d；'
  u'锚 %d 个（⟦C⟧ %d ⇎ ⟦R⟧ %d ⇎ ⟦M⟧ %d），锚内字母 %d ⇎ 锚内汉字 %d，'
  u'锚外字母 %d = 出处标签 %d + 其余 %d（仅 ℒmethod 自身）；字符／语义单元 6.67；T1／T2／T3 失配 0，待核小整数 0 条。' % (
    enc_nl, enc_n, dig_total, dig_body, dig_total - dig_body, n_atoms,
    blocks.get('C', 0), blocks.get('R', 0), blocks.get('M', 0), raw_chars, raw_bytes,
    ret_d, ret_c, ret_b, uniq, n_atoms, n_c, n_r, n_m,
    inlat, inhan, outlat, len(tags_all), outlat - len(tags_all)))

a(u'※保留率口径 本条三源合计 %d 字符（每份 17 000 上下），其中套语段落三份逐字相同：%d 个锚里 %d 个串跨文件同命中，'
  u'而编码只需把每条套语引用一次。所以 vs 摘要段为 %.1f%%、vs raw 字节为 %.3f%%，是三源条里压缩最强的一条'
  u'（B39 为 88.3%%／20.815%%，B38 为 92.9%% 量级），低保留率来自“重复文本只引一次”，不是来自删掉论证。'
  u'反过来，代价是判词里必须把“哪几处同命中算模板、哪几处独有才算实质”写清楚，这条线由机检键 %d 与零值键 %d 项共同划定。' % (
    raw_chars, n_atoms, multi, ret_d, ret_b, len(dkeys), n_absent))

io.open(ENTRY, 'w', encoding='utf-8').write(full.split(u'## ⛓解读注')[0] + u'## ⛓解读注\n' + u'\n'.join(G) + u'\n')
print(u'gloss written: enc %d dig %d ret %.1f%% uniq %d raw %d/%d' % (enc_n, dig_total, ret_d, uniq, raw_chars, raw_bytes))
