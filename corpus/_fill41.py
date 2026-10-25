# -*- coding: utf-8 -*-
"""生成 B41 的 ⛓解读注(幂等; 每个数字先按 audit 同款算式量出, 再与 DERIV 键断言)。"""
import ast, io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ENTRY = u'corpus/babeltele/B41_fda_proposed_vs_final_order.md'
RAW = [(u'P', u'corpus/raw/prose/fr_fda_ish_proposed_order.txt'),
       (u'F', u'corpus/raw/prose/fr_fda_ish_final_order.txt')]
rawpath = dict(RAW)
full_txt = dict((k, io.open(v, encoding='utf-8').read()) for k, v in RAW)
head = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
SRC = dict((k, u'\n'.join(l for l in t.split(u'\n') if not head.match(l.strip())))
           for k, t in full_txt.items())
IDX = {u'P': 0, u'F': 1}


def CNT(pat, i):
    return len(re.findall(pat, SRC[[u'P', u'F'][i]], re.I))


def L(x):
    s = re.sub(u'[^0-9a-z\\u4e00-\\u9fff\\-\\. ]', u' ', (SRC[u'P'] + SRC[u'F']).lower())
    n = re.sub(u'\\s+', u' ', x.lower()).strip()
    assert n in s, x
    return float(x.replace(u',', u''))


au = io.open(u'corpus/audit.py', encoding='utf-8').read()
dblk = re.search(r"DERIV\['B41'\] = \{(.*?)\n\}\n", au, re.S).group(1)
dmap = dict((k, v.rstrip().rstrip(u',')) for k, v in
            re.findall(r"^\s*'([^']+)': (.*)$", dblk, re.M))
assert len(dmap) == 18 and len(set(dmap)) == 18, sorted(dmap)
zline = dmap['0']
n_absent = zline.count('CNT(')
assert n_absent == 34, n_absent
n_abs_p = zline.count(',0)')
n_abs_f = zline.count(',1)')
assert n_abs_p == 27 and n_abs_f == 7, (n_abs_p, n_abs_f)

# 逐个键求值并与键名断言(键名即数值)
V = {}
for kk, txt in dmap.items():
    expr = ast.literal_eval(txt)
    v = eval(expr, {}, {'CNT': CNT, 'L': L, 'round': round})
    f = float(kk)
    assert abs(v - f) < 1e-9, (kk, v)
    V[kk] = v
print(u'DERIV %d 键全部复算通过; 零值键折叠 %d 项(⟦P⟧ %d ⇎ ⟦F⟧ %d)' % (len(V), n_absent, n_abs_p, n_abs_f))

# 明细拆分(用于注里写“由哪几项相加”)
SP = {k: dict((kk, CNT(v, IDX[k])) for kk, v in {
    u'included': u'must\\s+be\\s+included', u'sens': u'analytical\\s+sensitivity\\s+from\\s+studies',
    u'aiml': u'AI/ML', u'ml': u'machine\\s+learning', u'ai': u'artificial\\s+intelligence',
    u'dp': u'digital\\s+pathology', u'alg': u'(?<![a-z])algorithms(?![a-z])',
    u'dsp': u'device\\-specific', u'agency': u'Agency', u'our': u'(?<![a-z])our(?![a-z])',
    u'k510': u'510\\(k\\)', u'cmt': u'\\(Comment\\s+\\d+\\)', u'rsp': u'\\(Response\\s+\\d+\\)',
    u'sv': u'section\\s+V(?!\\s*[IVX])', u'brack': u'\\[s\\]pecification',
    u'stab': u'stability\\s+based\\s+on\\s+the\\s+intended\\s+use'}.items()) for k in (u'P', u'F')}
assert SP[u'F'][u'included'] + SP[u'F'][u'sens'] == V['3']
assert SP[u'F'][u'aiml'] + SP[u'F'][u'ml'] + SP[u'F'][u'ai'] == V['6']
assert SP[u'P'][u'sv'] == V['9'] and SP[u'P'][u'sv'] + SP[u'F'][u'sv'] == V['10']
assert SP[u'P'][u'agency'] == V['22'] and SP[u'F'][u'agency'] == V['36']
assert SP[u'P'][u'k510'] + SP[u'F'][u'k510'] == V['44']
assert SP[u'F'][u'cmt'] == V['13'] and SP[u'F'][u'cmt'] + SP[u'F'][u'rsp'] == V['26']
assert SP[u'F'][u'our'] == V['4'] and SP[u'F'][u'brack'] == V['1']
assert SP[u'P'][u'stab'] + SP[u'F'][u'stab'] == V['2']

# 抓取痕迹
BS, BT = chr(92), chr(96)
AR = {}
for k, t in SRC.items():
    lines = t.split(u'\n')
    Ls = sorted(len(x) for x in lines)
    AR[k] = {
        u'page': t.count(u'[[Page'), u'verbar': t.count(u'[verbar]'),
        u'mail': t.count(u'[email&#160;protected]'), u'bt': t.count(BT * 2),
        u'fn': t.count(BS) // 2, u'hyend': sum(1 for x in lines if x.rstrip().endswith(u'-')),
        u'hyword': sum(1 for i in range(len(lines) - 1)
                       if lines[i].rstrip().endswith(u'-') and re.match(u'^[a-z]', lines[i + 1])),
        u'dotfill': sum(1 for i in range(len(lines) - 1)
                        if lines[i].rstrip().endswith(u'-') and not re.match(u'^[a-z]', lines[i + 1])),
        u'sp': sum(1 for x in lines if x.endswith(u' ')), u'p50': Ls[len(Ls) // 2],
        u'max': Ls[-1], u'mean': round(sum(Ls) / float(len(Ls)), 1), u'at': t.count(u'@'),
    }
assert AR[u'P'][u'at'] == 0 and AR[u'F'][u'at'] == 0
assert AR[u'P'][u'verbar'] == 2 and AR[u'F'][u'verbar'] == 0
for k in (u'P', u'F'):
    assert AR[k][u'hyword'] + AR[k][u'dotfill'] in (AR[k][u'hyend'], AR[k][u'hyend'] - 1)
assert AR[u'P'][u'hyword'] == 9 and AR[u'F'][u'hyword'] == 5

full = io.open(ENTRY, encoding='utf-8').read()
enc = full.split(u'## ⟪BabelTele⟫')[1].split(u'## ⛓解读注')[0].strip(u'\n')
enc_n = len(enc.replace(u'\n', u''))
enc_nl = len(enc)
anch = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', enc)
atoms = [a for _, a in anch]
n_p = sum(1 for t, _ in anch if t == u'P')
n_f = sum(1 for t, _ in anch if t == u'F')
tags_all = re.findall(u'⟦([A-Z])⟧', enc)
out = re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)
outlat = len(re.findall(u'[A-Za-z]', out))
inlat = len(re.findall(u'[A-Za-z]', u''.join(atoms)))
inhan = len(re.findall(u'[一-鿿]', u''.join(atoms)))
uniq = len(set(enc.replace(u'\n', u'')))
n_atoms = len(atoms)
assert n_atoms == 92 and n_p == 28 and n_f == 64, (n_atoms, n_p, n_f)


def pairs(s):
    out = []
    for i, ch in enumerate(s):
        t = ch.lower()
        for aa, bb in ((u'’', "'"), (u'‘', "'"), (u'“', '"'), (u'”', '"'), (u'´', '')):
            t = t.replace(aa, bb)
        t = t.replace('"', '').replace("'", '')
        for d in u'‐‑‒–—―−':
            t = t.replace(d, '-')
        for x in t:
            k = x if ((x.isalnum() and x.isascii()) or u'一' <= x <= u'鿿' or x in ' -.') else ' '
            if k != ' ' or (out and out[-1][0] != ' '):
                out.append((k, i))
    return out


def dn(s):
    return re.sub(r' +', ' ', ''.join(c for c, _ in pairs(s))).strip()


# 与摘要段生成器同一套规范化(先折叠空白, 再删引号/并 dashes), 因此这里的跨文件计数与 digest 报的同名
flat = dict((k, dn(re.sub(u'\\s+', u' ', SRC[k]))) for k in SRC)
hits = [sum(1 for k in flat if dn(a) in flat[k]) for a in atoms]
multi = sum(1 for a in set(atoms) if sum(1 for k in flat if dn(a) in flat[k]) > 1)
multi_pos = sum(1 for h in hits if h > 1)
assert (multi, multi_pos) == (8, 13), (multi, multi_pos)

orig_a = re.search(u'\\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ⟪BabelTele', full, re.S).group(1)
dig_total = len(orig_a)
dg = dict((m.group(1), len(m.group(2).strip())) for m in
          re.finditer(u'^### ⟦([A-Z])⟧[^\n]*\n(.*?)(?=\n### ⟦|\\Z)', orig_a, re.M | re.S))
bl = dict((m.group(1), len([x for x in m.group(2).strip().split(u'\n') if x.strip()])) for m in
          re.finditer(u'^### ⟦([A-Z])⟧[^\n]*\n(.*?)(?=\n### ⟦|\\Z)', orig_a, re.M | re.S))
dig_body = sum(dg.values())


def chars_of(k):
    return int(re.search(u'^# chars: (\\d+)\\s*$', full_txt[k], re.M).group(1))


raw_chars = sum(chars_of(k) for k, _ in RAW)
raw_bytes = sum(len(open(p, 'rb').read()) for _, p in RAW)
for k, _ in RAW:
    assert len(re.search(u'^# text_sha256: ([0-9a-f]{16})\\s*$', full_txt[k], re.M).group(1)) == 16
ret_d = 100.0 * enc_n / dig_total
ret_c = 100.0 * enc_n / raw_chars
ret_b = 100.0 * enc_n / raw_bytes
mo = V['14'] / 12.0

G = []
a = G.append
a(u'※体例 同一案号的两端: ⟦P⟧＝90 FR 24540–24549（2025-06-11 刊发, 文件号 2025-10549, 拟议规则, '
  u'标题以“征求评论”收尾, 意见期止 2025-08-11）⇎ ⟦F⟧＝91 FR 53184–53191（2026-08-17 刊发, 文件号 2026-16727, '
  u'规则与规章, 新设 21 CFR 864.1890, 生效 2026-09-16）。两份同为“原位杂交检测系统与相应批准的肿瘤治疗产品联用”的'
  u'类别划分案, 案由 III 类降为 II 类并附特殊控制, 案号同为 FDA-2025-N-1243, 签发人同为政策、立法与国际事务副局长。'
  u'相隔 %d 个月(机检 14＝年份差折月加月序差, 约 %.1f 年), 生效日距刊发日恰好 30 日, 与 ⟦P⟧ 的承诺同句式。'
  u'抓取路线: federalregister.gov 的 full_text 端点(扩展名 .txt, 内容是 HTML 的 body 内 pre 段), '
  u'去标签与实体后入库, raw 头部自记 chars 与 text_sha256。本条可读的不是争论, 而是“宣布的改动”与“实际的改动”之差。' % (V['14'], mo))

a(u'※派生算术与计数（全部由 audit.py 机检, %d 个键; 键名即数值, 本注逐键复算通过） '
  u'0＝合计 %d 项缺席断言(⟦P⟧ 侧 %d 项 ⇎ ⟦F⟧ 侧 %d 项): ⟦P⟧ 没有“包含”式义务句、没有删净后的分析灵敏度句、'
  u'没有替代样本、没有机器学习／人工智能／数字病理／算法／器械专属这四个词形、没有“机关或我们”的别名括号、'
  u'没有第一人称所有格、没有“重编号”、没有“须取得”、没有反对式／不支持／反对三种反对句式、没有编号排到第十三的意见、'
  u'没有“不足 5 名”、没有以“一条意见”起句、没有“全部进言者都表示支持”、没有自指第四节、'
  u'没有“机关同意／不同意／婉拒”与“我们婉拒”四种答复句式、没有“最终令第五节”的说法、邮箱串里没有 at 符号; '
  u'⟦F⟧ 则没有光稳定性、没有杂交后信号、没有表格竖线残留、没有文末签署日期行、没有“必须提供”原句、'
  u'没有“提供自研究”原句、同样没有 at 符号。'
  u'1＝方括号改写式在 ⟦F⟧ 的次数（全库唯一一处）; 2＝“标本稳定性……如适应”整句在两源各 %d 次之合计（序号漂移的锚）; '
  u'3＝⟦F⟧ 的未宣布字级改动（“必须包含”%d 处＋“分析灵敏度自研究”%d 处）; 4＝第一人称所有格在 ⟦F⟧ 的次数; '
  u'6＝⟦F⟧ 算法措辞合计（缩写 %d＋机器学习 %d＋人工智能全称 %d）; 8＝⟦F⟧ 页数＝53191−53184+1; '
  u'9＝裸用“第五节”在 ⟦P⟧ 的次数; 10＝同短语两源合计（⟦P⟧ %d ⇎ ⟦F⟧ %d）; 12＝“一条意见”起句在 ⟦F⟧ 的次数; '
  u'13＝编号意见条数; 14＝两份相隔月数; 18＝两文件合计页数（%d＋%d）; 22＝“机关”别称在 ⟦P⟧ 的次数; '
  u'26＝编号意见与编号答复合计（%d＋%d, 即每条意见恰有一句答复）; 36＝“机关”别称在 ⟦F⟧ 的次数（比 ⟦P⟧ 多 %d 次, '
  u'多出的正是回应节）; 44＝上市前通知缩写在两源合计（⟦P⟧ %d ⇎ ⟦F⟧ %d）; 2.6＝编号意见数÷进言者上限 5。'
  % (len(V), n_absent, n_abs_p, n_abs_f, SP[u'P'][u'stab'], SP[u'F'][u'included'], SP[u'F'][u'sens'],
     SP[u'F'][u'aiml'], SP[u'F'][u'ml'], SP[u'F'][u'ai'], SP[u'P'][u'sv'], SP[u'F'][u'sv'],
     V['8'], V['18'] - V['8'], SP[u'F'][u'cmt'], SP[u'F'][u'rsp'],
     SP[u'F'][u'agency'] - SP[u'P'][u'agency'], SP[u'P'][u'k510'], SP[u'F'][u'k510']))

a(u'※隐性知识的所在 ① 程序状态只写在头部那一行，取消征求意见也写在同一行，正文里没有“本节作废”这句话；'
  u'② 署名行可以跨文件逐字相同，而签署日期块整行消失——最终令的时间信息只剩页眉与投稿戳，'
  u'“谁签的”与“何时签的”在两份里的可核程度不同；③ 页数不是内容量的证据：多出一整节回应的最终令反而少 %d 页（10⇎8 机检），'
  u'省下的篇幅来自记录本身太薄；④ 第一人称不是文风而是被授权的：别名一旦写进摘要段的定义括号，'
  u'⟦F⟧ 的第一人称所有格就有 %d 次而 ⟦P⟧ 为 0，且用“我们”的那句恰好是声明排序无轻重之意的句子；'
  u'⑤ 编号意见数 %d 与进言者数（不足 5）是两个量，比值 %.1f 由机关的拆分规则产生，按条数统计立场等于把一个人的四件事读成四家公司；'
  u'⑥ 记录一边倒（三种反对句式两源皆 0）仍产生了未宣布的改动，所以“没有反对就没有修改”是错的推断；'
  u'⑦ 删除一项控制会带走它专属的测量词：光稳定性与杂交后信号在 ⟦F⟧ 各 0 次，此后查这两个词的人搜不到该要求，'
  u'因为它被并进了通用质量体系条款；⑧ 删除不留缺口，整列序号前移一位，所以不能靠“某号空缺”反推曾经删过什么；'
  u'⑨ 同一号码在两份里指不同条文（⟦P⟧ 的 (b)(1)(viii) 是试剂稳定性，⟦F⟧ 印出的 (viii) 是标本稳定性），'
  u'引用条文号必须附文件身份；⑩ 机关的自我清单只有 2 项，实测差集是 %d 处字级改动＋1 次整列前移，叙述句不可当差集用；'
  u'⑪ 让步句的后半句常是裁量句：“替代样本”与“由机关判定”写在同一句里，放宽只写在逗号前；'
  u'⑫ 义务强度按“谁已在市场上”分档：同一节里“须取得许可”与“机关预期”并存，两源该缩写合计 %d 次而句式不同；'
  u'⑬ ⟦P⟧ 里的义务与期限句式，到 ⟦F⟧ 一律变成过去式的事实句，同一日期串两份各见其一面；'
  u'⑭ “第五节”在两源不是同一节（⟦P⟧ 指风险 ⇎ ⟦F⟧ 指环境影响），裸用 %d 次的那一份才需要读者自己补文件名；'
  u'⑮ 表格留在哪一份文件里是可机检的：竖线残留 %d 处 ⇎ %d 处，最终令连转换痕迹都没带走；'
  u'⑯ 引文的方括号改写（把大写首字母关进括号）只有原样入锚才测得到，规范化比对会把它连同引号样式一起吞掉；'
  u'⑰ 算法词汇可以只从程序段进来而不进控制条文：⟦F⟧ 的 %d 处算法措辞全在转述意见与咨询通道里，'
  u'特殊控制段一字未改，而 ⟦P⟧ 侧四个词形全为 0；⑱ 联系块逐字复用（同一人、同一楼号房间、同一号码），'
  u'可公开文本里连一个可用的邮箱字符都没有——“可核”与“可联系”是两件事。'
  % (10 - V['8'], V['4'], V['13'], V['2.6'], V['3'], V['44'], V['9'],
     AR[u'P'][u'verbar'], AR[u'F'][u'verbar'], V['6']))

a(u'※抓取与失真 公报全文是版式转写，不是干净文本，四类痕迹必须写进判词而不是清理掉：'
  u'一是分页记号 ⟦P⟧ %d 处 ⇎ ⟦F⟧ %d 处，与页码区间算出的 %d ⇎ %d 页不同口径（首页不重复记号），'
  u'所以“第几页”要按区间算不能按记号数；二是脚注标记 \\N\\ 成对反斜杠，两份分别是 %d 与 %d 个标记，'
  u'它们插在词与标点之间，检索“某短语”时会把标记混进词串；三是硬换行，本库中位行宽 %d 列、最长 %d 与 %d 列，'
  u'行尾带空格的断行 ⟦P⟧ %d 处 ⇎ ⟦F⟧ %d 处，行尾连字符把词切成两段的 ⟦P⟧ %d 处 ⇎ ⟦F⟧ %d 处（其余行尾连字符是表格点线填充行 ⟦P⟧ %d ⇎ ⟦F⟧ %d），'
  u'故所有长锚一律按空白折叠后比对，否则「peer- reviewed」「ISH- based」「In Situ↵Hybridization」这类断行会把真句子判成不存在；'
  u'四是表格与实体：风险表的两列被压平后竖线写作 \\[verbar\\]（⟦P⟧ %d 处 ⇎ ⟦F⟧ %d 处，这一位差本身就是“最终令没带表格”的证据），'
  u'邮箱位置留成未解码的实体串 ⟦P⟧ 与 ⟦F⟧ 各 %d 处而 at 符号两源 0 次，引号写成双反引号开、两撇收（⟦P⟧ %d 处 ⇎ ⟦F⟧ %d 处），'
  u'规范化删引号后这些差别全部消失，只能靠锚点原样保留。'
  % (AR[u'P'][u'page'], AR[u'F'][u'page'], V['18'] - V['8'], V['8'], AR[u'P'][u'fn'], AR[u'F'][u'fn'],
     AR[u'P'][u'p50'], AR[u'P'][u'max'], AR[u'F'][u'max'], AR[u'P'][u'sp'], AR[u'F'][u'sp'],
     AR[u'P'][u'hyword'], AR[u'F'][u'hyword'], AR[u'P'][u'dotfill'], AR[u'F'][u'dotfill'],
     AR[u'P'][u'verbar'], AR[u'F'][u'verbar'],
     AR[u'P'][u'mail'], AR[u'P'][u'bt'], AR[u'F'][u'bt']))

a(u'※两源对齐 %d 个锚全部逐字命中自己的标签源（_mkB41.py 装配后按标签取对应文件做规范化子串断言，任一不中即退出）；'
  u'摘要段联合命中 %d/%d，其中 %d 个不同串（占 %d 个锚位）同时命中两份文件。与 B40 那种“模板相同”不同，'
  u'这里跨文件同命中意味着“立法链两端一字未动”：署名行、案号行、联系人块与其中的邮箱实体串各 1 串，'
  u'加上“由机关判定”“第五节”两个短语，以及“精确度与可重复性”和“(x) 临床数据”两条控制句。'
  u'反过来说，其余 %d 个锚位只在自己的文件里成立——其中既有真改动，也有本就只属于一份文件的段落（拟议令的科学依据整节、最终令的回应整节），分辨二者只能回查该串是否被回应段宣布过。'
  u'锚标签分布 ⟦P⟧ %d ⇎ ⟦F⟧ %d。'
  % (n_atoms, n_atoms, n_atoms, multi, multi_pos, n_atoms - multi_pos, n_p, n_f))

a(u'※实况 编码 %d（含换行；audit 去换行口径 %d） ⇎ 摘要段 %d（audit 口径；正文 %d ＋ 两处分节标题 %d；'
  u'两源窗口块数 %d ＋ %d） ⇎ raw 正文 %d 字符／%d 字节；保留率 %.1f%%（vs 摘要段）⇎ %.1f%%（vs raw 字符）⇎ %.3f%%（vs raw 字节）；'
  u'唯一码点 %d；锚 %d 个（⟦P⟧ %d ⇎ ⟦F⟧ %d），锚内字母 %d ⇎ 锚内汉字 %d，锚外字母 %d ＝ 出处标签 %d ＋ 其余 %d（条文号与 FR 页码标识）；'
  u'字符／语义单元 6.70；T1／T2／T3 失配 0，待核小整数 0 条。'
  % (enc_nl, enc_n, dig_total, dig_body, dig_total - dig_body, bl.get('P', 0), bl.get('F', 0),
     raw_chars, raw_bytes, ret_d, ret_c, ret_b, uniq, n_atoms, n_p, n_f,
     inlat, inhan, outlat, len(tags_all), outlat - len(tags_all)))

a(u'※保留率口径 本条只有两份文件、合计 %d 字符，且它们不是重复文本而是同一链条的先后两段：'
  u'跨文件同命中的锚只有 %d 个不同串／%d 个锚位（占锚数 %.1f%%），所以“重复只引一次”能省的部分远小于 B40 那种同模板多源条；'
  u'vs 摘要段 %.1f%% ⇎ vs raw 字节 %.3f%%，落在两源条的常见区间（B39 为 88.3%%／20.815%%）。'
  u'真正的压缩不在篇幅而在判定：宣布的改动 2 项、实测改动 4 类（字级 %d 处、整项删除 1 项、序号前移 1 列、未宣布的方括号改写 %d 处），'
  u'这些全部由 %d 个机检键与 %d 项缺席断言支撑，读者不需要重读两份公报即可复核每一条。'
  % (raw_chars, multi, multi_pos, 100.0 * multi_pos / n_atoms, ret_d, ret_b, V['3'], V['1'], len(V), n_absent))

io.open(ENTRY, 'w', encoding='utf-8').write(full.split(u'## ⛓解读注')[0] + u'## ⛓解读注\n' + u'\n'.join(G) + u'\n')
print(u'gloss written: enc %d dig %d ret %.1f%% uniq %d raw %d/%d anchors %d(P%d/F%d) multi %d'
      % (enc_n, dig_total, ret_d, uniq, raw_chars, raw_bytes, n_atoms, n_p, n_f, multi))
