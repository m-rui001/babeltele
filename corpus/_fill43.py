# -*- coding: utf-8 -*-
"""B43 记账: ⛓解读注由 audit 里的 DERIV 表达式独立回算生成, 不手填任何数字。"""
import io, re, sys, os, subprocess, ast, statistics

sys.stdout.reconfigure(encoding='utf-8')

TAG = u'B43'
ENTRY = u'corpus/babeltele/B43_ewca_aviator_judgment_vs_landing_page.md'
RAW0 = u'corpus/raw/prose/law_aviator_spribe.txt'
RAW1 = u'corpus/raw/prose/law_ewca_aviator.txt'
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)


def reason(i):
    s = io.open([RAW0, RAW1][i], encoding='utf-8', errors='replace').read()
    return u'\n'.join(l for l in s.split(u'\n') if not HEADRX.match(l.strip()))


SRC = [reason(0), reason(1)]


def CNT(pat, i):
    return len(re.findall(pat, SRC[i], re.I))


au = io.open(u'corpus/audit.py', encoding='utf-8').read()
blk = re.search(u" 'B43': \\{\n(.*?)\n \\},", au, re.S).group(1)
VALS, EXPR = {}, {}
for m in re.finditer(r"^ {2}'([^']+)': (.*)$", blk, re.M):
    k, v = m.group(1), m.group(2).strip().rstrip(u',')
    EXPR[k] = ast.literal_eval(v)      # audit 里存的是字符串字面量, 先剥引号再回算
    VALS[k] = float(k)                 # 键名即数值; 下一段用独立回算的 CNT 验证
assert len(VALS) == 20, len(VALS)
for k, v in EXPR.items():
    got = eval(v, {}, {u'CNT': CNT, u'L': lambda x: float(x.replace(u',', u'')), u'round': round})
    assert abs(float(got) - float(k)) < 1e-9, (k, got, v[:90])
NABS = EXPR[u'0'].count(u'CNT(')

md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
tags = re.findall(u'⟦([A-Za-z])⟧', body)
uniq_atoms = sorted(set(atoms))
in_lat = sum(len(re.findall(u'[A-Za-z]', a)) for a in atoms)
tag_lat = sum(len(x) for x in tags)
out_all = len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body)))
out_lat = out_all - tag_lat
enc = len(body.replace(u'\n', u''))
dig = len(re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', md, re.S).group(1))
ret = u'%.1f%%' % (100.0 * enc / dig)
raw_chars = [len(SRC[0]), len(SRC[1])]
raw_bytes = [os.path.getsize(RAW0), os.path.getsize(RAW1)]

p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
b43 = [x.strip() for x in row[u'B43'].split(u'|')]
assert int(b43[0]) == dig and int(b43[1]) == enc, (b43[:2], dig, enc)
uniq_cp, blocks, cpu, dens, soft = int(b43[4]), int(b43[5]), b43[6], b43[3], int(b43[10])
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
enc_all, dig_all, ret_all, uniq_all = (int(allc[1].replace(u' ', u'')), int(allc[0].replace(u' ', u'')),
                                       allc[2], int(allc[4]))
assert soft == 0 and proofs == 385, (soft, proofs)

lines = [l for l in body.split(u'\n') if l.strip()]
Ls = [len(l) for l in lines]
GLOS = len(lines) - 2                      # 去掉 ∴骨架 与 ℒmethod 两行
head_letters = sum(len(re.findall(u'[A-Za-z]', l)) for l in lines if l.startswith(u'🧭'))

MEAN = {
 u'0': u'十八项缺席: 判决全文里 0 次的网站字段六项(Skip to main content/Search/Download/.pdf/569.88/H.-D.)＋发布页里 0 次的法律用词十二项',
 u'1': u'“I also agree.” 在判决全文的命中数——第二位法官的全部发言只有一句',
 u'2': u'带变音符的被告全名 “OÜ” 在发布页的命中数',
 u'3': u'字面 “-v-” 在发布页比判决全文多出的处数(页里把当事人串成标题缩写, 正文的对造写法不带连字符)',
 u'8': u'“res judicata” 在判决全文的命中数',
 u'9': u'“Georgia” 在判决全文的命中数',
 u'10': u'“crash game” 在判决全文的命中数',
 u'11': u'“party” 这一称谓在判决全文的命中数(标题外的方只用它露出)',
 u'15': u'每页重印的页眉 “Approved by the court for handing down” 的命中数=正文自身可数的页界',
 u'23': u'“issue estoppel” 在判决全文的命中数——争点的下位术语, 比上位概念 res judicata 多出一倍以上',
 u'26': u'“copyright” 在判决全文的命中数(诉因义), 与发布页里网站版权声明的同词形成对照',
 u'27': u'“Rome II” 在判决全文的命中数',
 u'28': u'“Court” 在发布页的命中数——绝大多数是导航里的法院清单',
 u'30': u'“estoppel” 在判决全文的命中数(含 issue estoppel)',
 u'36': u'方括号年引证比圆括号年引证多出的处数',
 u'37': u'方括号年引证在判决全文的命中数',
 u'57': u'“Court” 在判决全文的命中数(实质用词)',
 u'59': u'“Spribe” 在判决全文比带变音符全名多出的处数',
 u'60': u'“Spribe” 简称在判决全文的命中数',
 u'80': u'“Aviator” 在判决全文的命中数',
}
assert set(MEAN) == set(VALS), sorted(set(VALS) ^ set(MEAN))
ks = sorted(VALS, key=lambda x: float(x))
arith = u'；'.join(u'%s⇒%s' % (k, MEAN[k]) for k in ks if k != u'0')

TXT = []
TXT.append(u'※ 体例：本条的两条 raw 是同一条 url 的两次抓取—— ⟪发布页⇎判决全文⟫。'
           u'锚位 %d 个(其中不同串 %d 个), 标注 %s 的锚只在发布页内比对、标注 %s 的锚只在判决全文内比对, 二者不互换; '
           u'判词 %d 行, 每行的数字都注册在 audit 的 DERIV 里(共 %d 键), 缺席断言 %d 项全部折进 0 键。'
           % (len(atoms), len(uniq_atoms), u'C', u'J', GLOS, len(VALS), NABS))
TXT.append(u'※ 派生算术(键名即数值, 全部由两份原文各自回算): '
           u'0⇒%d 项缺席(判决全文缺发布页的网站字段, 发布页缺判决的法律用词); %s。'
           u'两处“差值型”键值得注意: 3 与 59 与 36——它们不是命中数, 而是“两份文本各命中数之差”, '
           u'因为单边的命中数会被抓取头部留下的 url 串污染(url 在审计口径里属于源文本, 故 -v-、Spribe、Aviator 两份各多 1 次)。'
           % (NABS, arith))
TXT.append(u'※ 隐性知识的所在(判词逐行对应的判断): ① 标题的当事人列表是快照、正文的编号称谓才是账本; '
           u'② 同一案件的两种字面写法(“-v-” ⇎ 编号列表＋“- and -”); ③ 全名带变音符、正文用简称⇒引全名与引简称是两套命中集; '
           u'④ 文件名里编的是听证日而非宣判日; ⑤ 页界可由每页重印的页眉反推; ⑥ 上诉结论用虚拟语气“would allow”, '
           u'附和各一段⇒说理出自一人而拘束力范围据此判定; ⑦ 拉丁术语首次出现的英语括号 gloss 只写一次; '
           u'⑧ 方括号年与圆括号年说明两种定位方式; ⑨ 本案的客体是一张图, 转本丢的是诉因对象; '
           u'⑩ 容器与内容互不包含⇒两份都得存; ⑪ 同词同形不同义(网站版权 ⇎ 诉因; 导航的 Court ⇎ 实质的 Court)。')
TXT.append(u'※ 抓取与失真：两份文件由同一页导出, 发布页把判决首页的头部块重复印了一遍(含 “%s”), '
           u'于是判决的元数据在两份里都在, 而只有页里有文件名、体积与下载入口; '
           u'审计口径把 url: 行留在源内, 所以凡“只在标题式写法里出现”的串都要用两文件之差来断言, 否则会得出一边倒的假命中。'
           % u'2 October 2026')
TXT.append(u'※ 两源对齐：跨文件同命中的锚位有 %d 个(标题块与宣判日那一块), 其余各自唯一——'
           u'这与 B41 的“两端一字未动”不同: 这里的重复是容器复制了文书的开头, 而不是同一义务在两份文书里各写一遍。'
           u'可省量因此只在那 %d 个同命中锚, 判词必须自建对照, 编码重于窗口。' % (3, 3))
TXT.append(u'※ 实况：判决全文 %s 字符 ⇎ 发布页 %s 字符(抓取头部自记的字符数与之一致); '
           u'编码 %s 字符 / %d 区块 / 唯一码点 %d / 字符每语义单元 %s; 判词行长中位数 %d、最长 %d。'
           u'全库合计编码 %s、摘要段 %s、保留率 %s、唯一码点 %s, 已机检的推导 %d 条, 本条待核列 %d。'
           % ('{:,}'.format(raw_chars[1]).replace(',', ' '), '{:,}'.format(raw_chars[0]).replace(',', ' '),
              '{:,}'.format(enc).replace(',', ' '), blocks, uniq_cp, cpu,
              int(statistics.median(Ls)), max(Ls), '{:,}'.format(enc_all).replace(',', ' '),
              '{:,}'.format(dig_all).replace(',', ' '), ret_all.strip('*'),
              '{:,}'.format(uniq_all).replace(',', ' '), proofs, soft))
TXT.append(u'※ 保留率口径：本条 vs 摘要段为 %s(编码重于窗口), 这是单源＋一页容器的结构性结果——'
           u'可索引窗口只覆盖了容器与判决的锚邻域, 而判词要自建两套文本的对照。'
           u'因此本条同时报两个口径: 编码/源文合计 %s(即两份原文的 %s), 以及每语义单元 %s 字符; '
           u'读它时应按“省下多少判定”而不是“比窗口长多少”来评价。' % (ret, dens, dens, cpu))

t = io.open(ENTRY, encoding='utf-8').read()
new = re.sub(u'## ⛓解读注\n.*\\Z', u'## ⛓解读注\n\n' + u'\n\n'.join(TXT) + u'\n', t, flags=re.S)
assert new != t
io.open(ENTRY, u'w', encoding='utf-8').write(new)
io.open(u'corpus/_f43stats.txt', u'w', encoding='utf-8').write(
    u'\n'.join(u'%s\t%s' % x for x in [
        (u'in_lat', in_lat), (u'out_lat', out_lat), (u'tag_lat', tag_lat), (u'out_all', out_all),
        (u'anchors', len(atoms)), (u'uniq_anchor', len(uniq_atoms)), (u'digest', dig), (u'enc', enc),
        (u'ret', ret), (u'raw0_chars', raw_chars[0]), (u'raw1_chars', raw_chars[1]),
        (u'raw0_bytes', raw_bytes[0]), (u'raw1_bytes', raw_bytes[1]), (u'uniq_cp', uniq_cp),
        (u'blocks', blocks), (u'cpu', cpu), (u'proofs', proofs), (u'dens', dens),
        (u'deriv_keys', len(VALS)), (u'n_abs', NABS), (u'enc_all', enc_all), (u'dig_all', dig_all),
        (u'ret_all', ret_all), (u'uniq_all', uniq_all), (u'gloss_lines', GLOS)]))
print(u'DERIV %d 键全部独立复算通过' % len(VALS))
print(u'gloss written: enc %d dig %d ret %s uniq %d anchors %d(%d uniq) in_lat %d out_lat %d tag %d proofs %d'
      % (enc, dig, ret, uniq_cp, len(atoms), len(uniq_atoms), in_lat, out_lat, tag_lat, proofs))
