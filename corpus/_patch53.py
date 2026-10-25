# -*- coding: utf-8 -*-
"""B53 文案返修: 按外部审阅(两路模型)挑出的六处口径/算术/张冠李戴逐条改判词, 并把 Step 折行成因写成可复算量。"""
import io

NL = '\n'
p = 'corpus/_mkB53.py'
s = io.open(p, encoding='utf-8').read()
Q = chr(34)


def rep(old, new, tag):
    global s
    assert s.count(old) == 1, tag
    s = s.replace(old, new)


# 采集侧写错的转义
rep(u"four(u'stepsoft', lambda k: len(re.findall(u'Step\\s*\\d', BODY[k])))",
    u"four(u'stepsoft', lambda k: len(re.findall(u'Step\\\\s*\\\\d', BODY[k])))", 'ESC')
rep(u"G[u'astep'] = AT(u'own', u'P', u'The dot in the right side')",
    u"G[u'astep'] = AT(u'any', u'P', u'The dot in the right side')", 'ANY')

rep(u"""LINE(u'🧱', u"“同一行”有四级判法(基数 {pt2} 行) ⇒ 官方 txt 的骨架行在按版式抽取里原样逐字 {tlr} ⇎ 去掉行首尾空白 {tls} ⇎ 再抹掉所有非字母数字 {tlk}; "
        u"在无版式层 {pTP}, 在落地页 {pTH}。逐字与骨架之间差 {gaptl} 行(无版式 {gaptp}, 落地页 {gapth})——"
        u"那 {gaptl} 行是“话还是那句话, 字已经不是那些字”, 例如 {adash}: 官方 txt 在这一处写作一个破折号, 本机两层各写作两个连字符, 逐字判不上而抹平后判得上。四级命中数只能逐级不减, 这条单调性由同一份 {pt2} 行基数当场校住。", **G)""",
    u"""LINE(u'🧱', u"“同一行”有四级判法 ⇒ 第一级是基数本身: 官方 txt 里骨架长度 ≥{skm} 的行共 {pt2} 行; 拿这批行去按版式抽取里配——"
        u"第二级原样逐字 {tlr}, 第三级去掉行首尾空白 {tls}(多配 {g01} 行), 第四级再抹掉所有非字母数字 {tlk}(再多配 {gaptl} 行), "
        u"从原样到骨架共多配 {dtl} 行; 无版式层 {pTP}, 落地页 {pTH}, 逐级多配 {gaptp}⇎{gapth}。多出来那些行是“话还是那句话, 字已经不是那些字”: "
        u"例如 {atdash} 在按版式层成了 {adash}——官方 txt 在这一处写作一个破折号, 本机两层各写作两个连字符, 逐字判不上而抹平后判得上。"
        u"四级命中数逐级不减, 这条单调性由同一份 {pt2} 行基数当场校住。", **G)""", 'B')

rep(u"""        u"Step 引用在无版式层多出 {stpd} 处——不是标准改了, 是抽取把跨行内容并成一行后把 “Step 2a”⇎“Step 2b” 这类引用数给了不同的行 {st2}。"
        u"版面与合并的证据: {stab}(按版式独有的表头行) ‖ {salg}(无版式独有的并行)。", **G)""",
    u"""        u"Step 引用在无版式层多出 {stpd} 处, 成因当场可查: 把模式放宽成“Step＋任意空白＋数字”后四层是 {sof}, "
        u"官方 txt 里被折行切开(行尾停在 Step, 编号落在下一行)的正是 {swr} 处, 无版式层把它们并回一行, 严格模式因此多数出一处。"
        u"版面与合并的证据: {stab}(按版式独有的表头行) ‖ {salg}(无版式独有的并行) ‖ {astep}(并回来的那一处) ‖ {st2} ‖ {atab}。", **G)""", 'P')

rep(u"""        u"而减号一类既可能变成 U+FFFD 也可能直接不见(锚句里的 (x−1) 在按版式层成了 (x1), 同一行的 ′ 一并消失, "
        u"{aell} 那行的省略号点在本机两层里也一个不剩)。""",
    u"""        u"而减号一类既可能变成 U+FFFD 也可能直接不见(锚句里的 (x−1) 在按版式层成了 (x1)); "
        u"′ 只住在 {aprime} 那一行, 在本机两层里同样一个不剩(′ {prm}, 省略号 … {ldt}), {aell} 那行的省略号点也一样。""", 'T')

rep(u"而“FIPS PUB 202”在四层里各只出现在行首 1 次",
    u"而“FIPS PUB 202”在三种文本序列化里各只出现在行首 {phv} 次、在落地页 {phh} 次", 'U')

rep(u"零层那枚是 uswds; 四层的 {h4} 枚全是标题、DOI、算法名这类骨架词。",
    u"零层那枚是 uswds(矩阵按去标签正文判, 它在整份文件⇎正文 {usw} 次); 四层的 {h4} 枚在注里逐枚列出, 都是标题、DOI、算法名这类骨架词。"
    + Q + "\n        u" + Q + """口径披露两笔: 穿层矩阵对四层都用去标签正文, 而正文锚的命中判定对落地页改用原文件的行——去标签后并成一段的话在原文件里被标签切成几处, 两种口径都写在这里, 不留给读者猜。", **G)""", 'W')

rep(u"而正文三种序列化都写作 August 2015。",
    u"而正文三种序列化都写作 August 2015。" + Q + "\n        u" + Q +
    """八个关键词家族(algorithm／fips／keccak／nist／sha3／shake／sponge／step)在整份文件 {kwr} 次、去标签正文 {kwb} 次, """
    """{kwl} 次随标签一起被删掉——单看 fips 字样是 {fpr} ⇎ {fpb}; {aredir} 这类告警行只住在容器里。", **G)""", 'V')

rep(u"去空白 {tls} ⇎ 抹非 ASCII {tlk}", u"去空白 {tls} ⇎ 骨架 {tlk}(逐级多配 {g01}⇎{gaptl})", 'S2')
rep(u"而 Step 层多 {stpd} 处, 断栏行", u"而 Step 层多 {stpd} 处(放宽空白后 {sof}, 被折行切开 {swr} 处), 断栏行", 'S6')
rep(u"SHA3 {sha3h}, 标签 {ht} 枚;", u"SHA3 {sha3h}, 标签 {ht} 枚, 八个关键词家族随标签丢掉 {kwl} 次;", 'S5')
rep(u"骨架四级配对/结构计数/穿层矩阵", u"骨架四级配对/结构计数与折行成因/穿层矩阵/关键词家族两种正文", 'S9')

io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
print('wording ok')
