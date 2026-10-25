# -*- coding: utf-8 -*-
# B84 README 记账 + 幂等 wire84 生成
import io, ast

p = 'corpus/README.md'
s = io.open(p, encoding='utf-8').read()

Q = chr(39)
BS = chr(92)
NL = chr(10)

para = (u'**B84 回到论文本义——单文本压缩**:把美国宪法全文(序言+七条+廿七修正案, `raw/constitution/us_constitution_full.txt`, '
        u'NARA 抄件拼合, 59 019 字符／9 908 词)压成 **2 528 字符算子中文(体积 4.3%, 论文锚点 27.9%)**。判据从多源对照换成可复原性: '
        u'序言+每条+每修正案至少一条目行(本注中文序号清单 assert 全过), 关键短语保留英文逐字锚 16 条全部一次命中'
        u'(atomcheck ok=16 bad=0)——⟨Congress shall make no law⟩、⟨the right of the people to keep and bear Arms⟩、'
        u'⟨neither slavery nor involuntary servitude⟩、⟨No person shall be elected to the office of the President more than twice⟩ 一字未改; '
        u'数字全走机检: 修正案罗马字头 44 处(27 头+17 交叉引用)、条字头 8、序言恰 52 词、词频重心 congress 87⇎president 122⇎senate 31⇎state 231、'
        u'two thirds 10 处; 废止故事一条线: 十八禁酒⇒二十一废除, 全文 repeal 词仅 2 处——宪法只废止过自己一次。'
        u'复原自测: 只读编码区应能答——弹劾提起归谁? 条约要几票? 叛国罪几个证人? 哪条给妇女投票权? 哪条拖两百年才批准?' + NL)

lines = s.split(NL)
for i, l in enumerate(lines):
    if l.startswith(u'**B78 把同一缺陷'):
        lines.insert(i, para)
        break
s = NL.join(lines)

tab = (u'| B84 | 2528（新建, 单文本压缩: 宪法全文→算子中文 体积 4.3% 16 处标注(编码区)／候选池 16 条（atomcheck 逐字 ok=16 bad=0, 全部一次命中）: '
       u'结构计数 修正案字头 44(27 头+17 交叉引用)/条字头 8/序言 52 词; 词频 congress 87⇎president 122⇎senate 31⇎state 231; '
       u'two thirds 10; repeal 2(唯一废止线 18⇒21); '
       u'扁平契约 14 枚键全由 DERIV 复算, 审计器侧第二套与采集侧对表 0 不符, 解读注第三套(词级)复测+覆盖清单 assert 全过） |' + NL)
lines = s.split(NL)
for i, l in enumerate(lines):
    if l.startswith(u'| B83 | 982'):
        lines.insert(i + 1, tab)
        break
s = NL.join(lines)

src84 = (u'| B84 | `raw/constitution/us_constitution_full.txt`（单源: 59 019 字符／9 908 词／16 锚全命中） | 单文本压缩判据=可复原性: '
         u'每条款至少一条目行, 短语逐字锚, 结构与词频计数机检, 体积 4.3% |' + NL)
lines = s.split(NL)
for i, l in enumerate(lines):
    if l.startswith(u'| B83 | `raw/nws/'):
        lines.insert(i + 1, src84)
        break
s = NL.join(lines)

wire = (
    u"python -X utf8 corpus/_pick84.py             # 采集侧测量: 结构计数+词频, 全部落 _b84meas.json" + NL +
    u"python -X utf8 corpus/_mkB84.py                  # 建条目: 手工算子中文编码(2 528 字符), 扁平契约 14 枚键" + NL +
    u"python -X utf8 corpus/_wire84.py                    # 幂等接线: SRC/ATOM/_b84_scan(第二套)/DERIV(14 键)/B84V 进 make_env" + NL +
    u"python -X utf8 corpus/_fill84.py                    # 解读注: 压缩率计量+覆盖清单 assert+第三套(词级)复测" + NL +
    u"python -X utf8 corpus/atomcheck.py B84 corpus/_atoms84.txt   # 工具侧独立逐字校验: ok=16 bad=0" + NL)
lines = s.split(NL)
for i, l in enumerate(lines):
    if l.startswith(u'python -X utf8 corpus/_fill83nws.py'):
        lines.insert(i + 1, wire)
        break
s = NL.join(lines)
io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
print('README 更新完成')

# 幂等 _wire84.py
sa = io.open('corpus/audit.py', encoding='utf-8', errors='replace').read()
i = sa.index(u"SRC['B84'] = ")
j = sa.index(u'B84V = lambda', i)
seg = sa[i:j]
Q3 = Q * 3
wire = (
    u"# -*- coding: utf-8 -*-" + NL +
    u"# 幂等接线 B84: SRC/ATOM/_b84_scan/DERIV(14 键)/B84V 进 audit.py。已在位则跳过。" + NL +
    u"import io, json, os, sys" + NL +
    u"os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))" + NL + NL +
    u"P = 'corpus/audit.py'" + NL +
    u"s = io.open(P, encoding='utf-8', errors='replace').read()" + NL +
    u"if \"DERIV['B84']\" in s:" + NL +
    u"    print('B84 已接线, 跳过')" + NL +
    u"    raise SystemExit" + NL + NL +
    u"BLOCK = u" + Q3 + NL + seg.rstrip() + NL + u"B84V = lambda k, i=None: (_B84[k][0] if i is None else _B84[k][i])" + NL + Q3 + NL + NL +
    u"CUT = 'rows, fails, proofs, soft_all = [], [], [], []'" + NL +
    u"assert s.count(CUT) == 1" + NL +
    u"s = s.replace(CUT, BLOCK + chr(10) + CUT)" + NL +
    u"REG = json.load(io.open('corpus/_b84flat.json', encoding='utf-8'))" + NL +
    u"s = s.replace(CUT, u\"DERIV['B84'] = \" + json.dumps(REG, ensure_ascii=False) + chr(10)*2 + CUT)" + NL +
    u"s = s.replace('               B83V=B83V)', '               B83V=B83V,' + chr(10) + '               B84V=B84V)')" + NL +
    u"assert 'B84V=B84V' in s" + NL +
    u"io.open(P, 'w', encoding='utf-8', newline=chr(10)).write(s)" + NL +
    u"print('wire84 完成: %d 键' % len(REG))" + NL)
io.open('corpus/_wire84.py', 'w', encoding='utf-8', newline=NL).write(wire)
ast.parse(wire)
print('_wire84.py 已生成')
