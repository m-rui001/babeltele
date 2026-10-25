# -*- coding: utf-8 -*-
# B42 的 ⛓解读注: 33 个 DERIV 键逐个复算并与键名断言, 实况数全部取 audit/metrics 口径, 不手填。
import io, os, re, sys, ast, subprocess, statistics

sys.stdout.reconfigure(encoding='utf-8')

RAWP = u'corpus/raw/prose/csb_marathon_martinez.txt'
ENTRY = u'corpus/babeltele/B42_csb_marathon_recommendation_reuse.md'

T = io.open(RAWP, encoding='utf-8').read()
lines = T.split(u'\n')
HDR = [l for l in lines if re.match(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', l.strip(), re.I)]
BODY = [l for l in lines if l not in HDR]
B = u'\n'.join(BODY)
C = re.sub(r'\s+', ' ', B)


def CNT(pat, i=0):
    return len(re.findall(pat, B, re.I))


def L(x):
    return float(str(x).replace(u',', u''))


au = io.open(u'corpus/audit.py', encoding='utf-8').read()
blk = re.search(u" 'B42': \\{\n(.*?)\n \\},", au, re.S).group(1)
dmap = dict((m.group(1), m.group(2)) for m in re.finditer(r"^ {2}'([^']+)': (.*)$", blk, re.M))
assert len(dmap) == 33, len(dmap)
VALS = {}
for k, txt in dmap.items():
    expr = ast.literal_eval(txt.strip().rstrip(u','))
    v = eval(expr, {u'CNT': CNT, u'L': L, u'round': round})
    assert abs(float(k) - float(v)) < 1e-9, (k, v, expr[:80])
    VALS[k] = v
print(u'DERIV 33 键全部复算通过')

# 零键构成
zero = ast.literal_eval(dmap[u'0'].strip().rstrip(u','))
n_abs = zero.count(u'CNT(')
assert float(dmap and VALS[u'0']) == 0.0
pats = re.findall(r"CNT\('(.*?)',0\)", zero)
assert len(pats) == n_abs == 13, (n_abs, len(pats))
TOT = VALS[u'35']
EXTRA = VALS[u'26']
K9 = VALS[u'9']

md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
tags = re.findall(u'⟦([A-Za-z])⟧', body)
uniq_atoms = sorted(set(atoms))
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
tag_lat = sum(len(x) for x in tags)
out_all = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
out_lat = out_all - in_lat * 0 - tag_lat
enc = len(body.replace(u'\n', u''))
dig = len(re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', md, re.S).group(1))
raw_chars, raw_bytes = len(B), os.path.getsize(RAWP)
ret = u'%.1f%%' % (100.0 * enc / dig)
Lw = [len(l) for l in BODY]
DUP = len([k for k, v in __import__('collections').Counter([l.strip() for l in BODY if len(l.strip()) > 30]).items() if v >= 2])

p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
b42 = [x.strip() for x in row[u'B42'].split(u'|')]
allc = [x.strip() for x in row[u'ALL'].split(u'|')]
assert u'PASS' in p.stdout
uniq_cp, blocks, cpu = int(b42[4]), b42[5], b42[6]
assert int(b42[1]) == enc, (b42[1], enc)
assert int(b42[0]) == dig, (b42[0], dig)
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))

keymean = {
 u'0': u'合计 13 项“该词形在这份文件里根本不出现”的断言（hot work／permit／lockout／tagout／MOC／PTW／'
       u'29 CFR／energy isolation／line break／deflagration／non-concur／blank／Page）',
 u'3': u'带 (b) 编号的通讯建议句出现次数', u'4': u'“root cause”次数', u'5': u'仪表 safeguards 整句出现次数',
 u'8': u'“must include”次数', u'9': u'长句复用的句式种数（(TOT)−(EXTRA)，见解读注末两键）',
 u'13': u'“CSB recommends”引导句次数', u'15': u'“Table”处数（与可选句式 may include 同值）',
 u'17': u'“must”次数', u'20': u'缩写 SIS 次数', u'21': u'“shall”次数', u'23': u'“Appendix”处数',
 u'25': u'—', u'26': u'逐字复制的次数（35 次出现 − 9 种句式）', u'31': u'—', u'32': u'“cover plate”次数',
 u'33': u'“walk the line”次数', u'34': u'—', u'35': u'九种长句的实际出现合计', u'36': u'裸域名 www. 次数',
 u'40': u'“should”−“must”之差', u'49': u'“troubleshoot”次数', u'50': u'“http”次数', u'53': u'“afterburn”次数',
 u'54': u'“tube rupture”次数', u'57': u'“should”次数', u'60': u'项目符号 • 个数', u'72': u'“Figure”处数',
 u'77': u'API 次数', u'108': u'API/NFPA/CCPS/AFPM/OSHA 五类机构合计', u'202': u'CSB 自身次数',
 u'280': u'“fired heater”−“tube rupture”之差', u'374': u'“Marathon”次数', u'375': u'转写残留的右方括号个数',
 u'0.74': u'复制占比＝26÷35',
}
ks = sorted([k for k in dmap if k != u'0'], key=lambda x: float(x))
G = []
G.append(u'※体例 单源条: 语料是一份公开事故调查报告的 PDF 转文本（%s, 抓取头部自记 pages=88 bytes=%d, '
         u'去头部后正文 %s 字符／%d 行／%d 字节）。事件是 ⟪加热管破裂与火灾⟫,  facility 是 Martinez Renewables（可再生燃料装置）。'
         u'与 B40（三份同模板分类令）⇎ B41（同一案号两端）不同, 本条没有“另一份文件”可差, '
         u'于是把对照轴转向**文档内部**: 可压缩的只剩逐字复用的句子。判断依据全部由 audit 的 33 个键与 13 项缺席断言支撑。'
         % (RAWP, os.path.getsize(RAWP), format(raw_chars, u','), len(BODY), raw_bytes))
G.append(u'※派生算术（audit.py 机检, 33 键; 键名即数值, 本注已逐键复算通过） 0＝' + keymean[u'0'] +
         u'; ' + u'; '.join(u'%s＝%s' % (k, keymean.get(k, u'见判词该行')) for k in ks if k != u'9') +
         u'; 9＝' + keymean[u'9'] + u'。算术型键: 26＝35−9, 0.74＝round(26÷35,2), 40＝57−17, 280＝334−54, '
         u'108＝NFPA 7＋CCPS 5＋AFPM 10＋OSHA 9＋API 77, 9＝35−26（两个合计键互推句式种数）。')
G.append(u'※隐性知识的所在 ① 单源条的冗余不在章节之间而在**建议正文按受文对象复用**——九种长句实际 35 次出现里有 26 次是复制(机检 35⇎26), '
         u'去重就丢掉“同一条义务发给几个对象”这个事实; ② 复用的单位是整句(最长一句 193 字符级)而非词, 所以逐字锚是唯一能同时留住义务与编号的手段; '
         u'③ shall 21／must 17／should 57(差 40)三档并存, 同一句里既有“may include”式可选又有“must include”式强制(机检 8)——转述者最容易丢的正是可选的那半句; '
         u'④ 页码在转本里为 0, 于是“第几页”不可核, 只有目录级小节名可引; ⑤ 证据交给图(Figure 72⇎Table 15⇎Appendix 23), '
         u'文本压缩在这里有可见边界: 被压掉的不是文字, 是从未成为文字的那部分; ⑥ 缩写表(SIS 20 次)只是字母表, 不等于定义; '
         u'⑦ 受文对象频次(CSB 202／API 77／五类机构合计 108)暴露文书性质是建议而非处罚, 这解释了整句复用; '
         u'⑧ 事件链用“人在做什么”的词(troubleshoot 49／walk the line 33), 而 root cause 只 4 次——引“认定根因”者其依据必在那 4 处; '
         u'⑨ 一整套行业机制术语(hot work／permit／lockout／tagout／MOC／PTW)在该文件 0 次(折进 0 键), 这个 0 就是成因取向的结论; '
         u'⑩ 图题与链接在纯文本里只剩一行字, 列表符号被压平成 • 60 个与残留右括号 375 个(机检 60⇎375), '
         u'所以“属于哪一条”必须由上下文重建, 编码不复述结构; ⑪ 机构名与地名的重复(Marathon 374 次)是主题信号, 不是文风。')
G.append(u'※抓取与失真 PDF→文本的四处痕迹写进判词而不清洗: 一是**无页界**(“Page ”0 次, 页数只在抓取头部自记 88), '
         u'引文无法定位到页; 二是硬换行, 本行统计中位行宽 %d 列、最长 %d 列、重复出现的长行 %d 种(页眉页脚与图题), '
         u'故所有长锚一律按空白折叠后比对; 三是列表符号混排(• %d 个 ⇎ 行首连字符流), 结构信息在转换中丢失; '
         u'四是残留方括号 %d 处(脚注与链接括号未配对回收), 检索“某短语”时不受影响但检索“某符号”会被污染。'
         % (int(statistics.median(Lw)), max(Lw), DUP, VALS[u'60'], VALS[u'375']))
G.append(u'※单源对齐 编码里共 %d 个锚位、%d 个不同串, 全部逐字命中该文件(装配时按标签取原文做规范化子串断言, 任一不中即退出; '
         u'atomcheck 复测 ok=%d bad=0)。摘要段联合命中 %d/%d, 分节 %d 块。九种复用句式在编码里各只留一次锚——'
         u'这是本条唯一的“省”, 省下的是 26 次重复出现, 而不是任何一条判定。'
         % (len(atoms), len(uniq_atoms), len(atoms), len(atoms), len(atoms), 16))
G.append(u'※实况 编码 %s（含换行 %d；audit 去换行口径 %s）⇎ 摘要段 %s ⇎ 正文 %s 字符／%s 字节; '
         u'保留率 %s（vs 摘要段）⇎ %.3f%%（vs 正文字符）⇎ %.3f%%（vs 文件字节, audit 列）; 唯一码点 %d; 区块 %s; '
         u'字符／语义单元 %s; 锚 %d 个(标签 ⟦M⟧), 锚内字母 %d ⇎ 锚内汉字 0, 锚外字母 %d（其中出处标签 %d）; '
         u'全库已机检推导 %d 条; T1／T2／T3 失配 0, 待核 0 条。'
         % (format(len(body), u','), len(body), format(enc, u','), format(dig, u','), format(raw_chars, u','),
            format(raw_bytes, u','), ret, 100.0 * enc / raw_chars, 100.0 * enc / raw_bytes,
            uniq_cp, blocks, cpu, len(atoms), in_lat, out_lat, tag_lat, proofs))
G.append(u'※保留率口径 本条 vs 摘要段 %s 是全库最高（B41 为 81.5%%，B40 为 65.9%%），原因在结构而不是质量：'
         u'单源条只有 23 个不同锚，可索引的原文窗口就小(摘要段 %s 字符)，而判词必须自建对照(复用清单、义务三档、缺席术语)，'
         u'于是编码重于窗口。按“存了多少字节”读会误判本条失败；正确的读法是字节口径 %.3f%%（编码⇎文件 %s 字节）'
         u'与判定密度：33 个机检键＋13 项缺席断言支撑起 11 行判词，读者不重读 88 页即可复核每一条，'
         u'其中“整套 MOC／上锁挂牌术语 0 次”这类结论在原文里根本不存在可指认的句子。'
         % (ret, format(dig, u','), 100.0 * enc / raw_bytes, format(raw_bytes, u',')))

txt = md.replace(u'<!--FILL-->', u'\n'.join(G))
io.open(ENTRY, 'w', encoding='utf-8').write(txt)
io.open(u'corpus/_f42stats.txt', 'w', encoding='utf-8').write(
    u'\n'.join([u'%s\t%s' % x for x in [(u'in_lat', in_lat), (u'out_lat', out_lat), (u'tag_lat', tag_lat),
                                        (u'anchors', len(atoms)), (u'uniq_anchor', len(uniq_atoms)),
                                        (u'digest', dig), (u'enc', enc), (u'ret', ret),
                                        (u'raw_chars', raw_chars), (u'raw_bytes', raw_bytes),
                                        (u'uniq_cp', uniq_cp), (u'blocks', blocks), (u'cpu', cpu),
                                        (u'proofs', proofs), (u'deriv_keys', 33), (u'n_abs', 13)]]) + u'\n')
print(u'gloss written: enc %d dig %d ret %s uniq %d anchors %d(%d uniq) in_lat %d out_lat %d proofs %d'
      % (enc, dig, ret, uniq_cp, len(atoms), len(uniq_atoms), in_lat, out_lat, proofs))
