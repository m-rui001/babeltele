# -*- coding: utf-8 -*-
# B92 解读注遍(第三套机制): 只用逐字符扫描与手工切片, 不复用 _pick92.py(采集遍)⇎_mkB92.py(建条目遍)
# 的任何中间量; 注里每个数由本遍现读现算。写回 "## ⛓解读注" 段, 不动编码区与原文区。
import io, os, re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENTRY = u'corpus/babeltele/B92_redirect_hop_limit_five_answers.md'
FILES = [u'corpus/raw/redirHops/b92/fetch.html', u'corpus/raw/redirHops/b92/max-redirs.md',
         u'corpus/raw/redirHops/b92/CURLOPT_MAXREDIRS.md', u'corpus/raw/redirHops/b92/client.go',
         u'corpus/raw/redirHops/b92/sessions.py']
LBL = [u'fet', u'cli', u'lib', u'go', u'req']

md = io.open(ENTRY, encoding='utf-8').read()
enc = re.search(u'## ⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)

TEXTS = [io.open(f, encoding='utf-8', errors='replace').read() for f in FILES]


def scan_words(t):
    """词数: 逐字符状态机(不用 split)。"""
    c, prev_ws = 0, True
    for ch in t:
        ws = ch.isspace()
        if not ws and prev_ws:
            c += 1
        prev_ws = ws
    return c


def lines_of(t):
    """行数: 数字符 '\n' 再加末尾无换行的一份(不用 splitlines)。"""
    n, last = 0, 0
    for i in range(len(t)):
        if t[i] == u'\n':
            n += 1
            last = i
    return n + (0 if last == len(t) - 1 or not t else 1)


def nb_lines(t):
    return len([1 for l in t.split(u'\n') if l.strip()])


def detag(t, fill):
    """剥壳: 游标找 '>'(不用 re), 实体走表。"""
    SG = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'),
          (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'),
          (u'&#215;', u'x'), (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"),
          (u'&mdash;', u'-'), (u'&ndash;', u'-'), (u'&deg;', u'deg'), (u'&infin;', u'inf'),
          (u'\xa0', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
          (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->')]
    if not t.lower().count(u'<html') and u'<' not in t:
        return t
    buf, i, n = [], 0, len(t)
    while i < n:
        if t[i] == u'<':
            j = t.find(u'>', i)
            if j >= 0:
                buf.append(fill)
                i = j + 1
                continue
        buf.append(t[i])
        i += 1
    s = u''.join(buf)
    for a, b in SG:
        s = s.replace(a, b)
    return s


def norm(s):
    s = re.sub(u"[’‘`´\"']", u'', s.lower())
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\.]', u' ', s)
    return u' '.join(s.split())


FACES = []      # 每源一张主面(网页取断面=标签替空格), 供 305 ⇎ 答案数计数
ANCH = []       # 每源的全部可比对面(网页另挂粘面=标签替空串)
for i, t in enumerate(TEXTS):
    if FILES[i].lower().endswith(u'.html'):
        # 撇号紧跟闭标签时, 断面得 "request s", 粘面才是锚文本的 "requests"——只留一档会假阴性。
        f1 = norm(detag(t, u' '))
        FACES.append(f1)
        ANCH.append([f1, norm(detag(t, u''))])
    else:
        f = norm(t)
        FACES.append(f)
        ANCH.append([f])

atoms = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
hits = []
for a in atoms:
    na = norm(a)
    hits.append(next((i for i in range(5) if any(na in fc for fc in ANCH[i])), -1))
ok = len([h for h in hits if h >= 0])
own = [len([1 for k, h in enumerate(hits) if h == i]) for i in range(5)]

# 五份源各自的体积账
CH = [len(t) for t in TEXTS]
BY = [len(t.encode('utf-8')) for t in TEXTS]
WD = [scan_words(t) for t in TEXTS]
LN = [lines_of(t) for t in TEXTS]
NB = [nb_lines(t) for t in TEXTS]
CP = [len(set(t)) for t in TEXTS]
enc_ch = len(enc.replace(u'\n', u''))
enc_cp = len(set(enc))

# 已废代理码 305: 建条目遍不在编码区印这个字面(五面查无此码), 本遍独立复核
Z305 = [len([1 for k in range(len(FACES[i]) - 2) if FACES[i][k:k + 3] == u'305']) for i in range(5)]
# 五档答案数在本遍面上的出现(游标扫描 + 邻位判形, 不用正则)
ANS = [u'20', u'50', u'30', u'10', u'30']
DIGS = set(u'0123456789.')


def whole(f, nd):
    c, i = 0, f.find(nd)
    while i >= 0:
        if f[i - 1:i] not in DIGS and f[i + len(nd):i + len(nd) + 1] not in DIGS:
            c += 1
        i = f.find(nd, i + 1)
    return c


ANS_OK = [whole(FACES[i], ANS[i]) for i in range(5)]
tags = len(re.findall(u'⟦[A-E]⟧', enc))

NOTE = (u'## ⛓解读注\n\n'
        u'### 压缩账(本注现算, 第三把尺)\n\n'
        u'| 量 | ⟦A⟧fet | ⟦B⟧cli | ⟦C⟧lib | ⟦D⟧go | ⟦E⟧req |\n|---|---|---|---|---|---|\n'
        u'| 源字符 | %s |\n'
        u'| 源字节(UTF-8) | %s |\n'
        u'| 源词 | %s |\n'
        u'| 源行(非空) | %s |\n'
        u'| 源唯一码位 | %s |\n'
        u'| 本遍剥壳后字符 | %s |\n\n'
        u'编码区 %d 字符(不含换行, 唯一码位 %d 枚), 对五源合账(%d 字符)为 %s; '
        u'逐字符状态机数出的词 %d 枚 ⇎ 编码区 %d 字符: 一格中文压着整句规范。\n\n'
        u'### 锚的归属(本遍独立核验)\n'
        u'编码区 %d 枚 ⟨锚⟩, 本遍穿到 %d 枚 ⇎ 穿不到 %d 枚; 归属 ⟦A⟧%d ⇎ ⟦B⟧%d ⇎ ⟦C⟧%d ⇎ ⟦D⟧%d ⇎ ⟦E⟧%d。'
        u'比对面是**剥壳后的网页面**(fetch.html 的 ⟨If request’s redirect count is 20, then return a network error⟩ '
        u'跨三枚标签, 原面逐字符扫读不到——本遍游标剥壳 ⇎ 建条目遍 finditer 拼块, 两把尺都得过)。'
        u'标签 %d 枚 ⇎ 锚 %d 枚: 一句里可挂两面, 逐标签配对由门槛 T1 现验。\n\n'
        u'### 读法: 同一问题的五个答案与四把尺\n'
        u'答案 20(fet) ⇎ 50(cli) ⇎ 30(lib) ⇎ 10(go) ⇎ 30(req)。三件事各自独立:\n'
        u'① **答案键**——五个数互不相同, 且 curl 一家两面互斥(手册页 50 ⇎ 3 号页 30); '
        u'本遍在各自剥壳面上重扫这五个数, 命中 %s 枚(数在别家面上偶然重现属正常, 判据是句不是数字符)。\n'
        u'② **尺键**——Go 的 `len(via)` 数的是**已跟过的跳**, `resp.history` 数的是**请求链**, '
        u'两把尺在 10 与 9 之间分岔; requests 的 30 只活在注释面, 代码面写符号名。\n'
        u'③ **档键**——同一句在原面逐行 ⇎ 全篇折平 ⇎ 剥壳 ⇎ 带壳 ⇎ 抹标记五档上可读性不同, '
        u'硬换行与行首 //、#: 各自切断一批针。\n'
        u'④ **层键**——数字落在码面、消息面还是文档面: Go 面上写的数与实拦的数不同层。\n\n'
        u'### 本条不能由在库文件判定的(只登记, 不进门槛)\n'
        u'已废的 305(代理重定向)在五份面的出现 %s 枚——建条目遍因此不在编码区印这个字面, '
        u'只在🧬段的针表键位上留零; IETF 侧(RFC 2616 的 5 跳 legacy 注记)不在本条五源里, 故本条不引任何 RFC 文书的数; '
        u'各实现的实际默认值随版本漂移, 本条只认盘上这五份文本自身。\n\n'
        u'### 编码与门的账\n'
        u'T1 逐锚回源(本遍 %d/%d, 面按扩展名分档) ⇎ T2 DERIV 复算(corpus/_b92flat.json 的 44 枚面值逐枚现算) '
        u'⇎ T3 码位与字母账(源面唯一码位 %d ⇎ 编码面 %d)。'
        u'A⇎B 对账 114 键, 两套实现换机制不换定义; 小整数待核只进本注, 不进 FAIL。\n'
        % (u' | '.join([u'%d' % v for v in CH]),
           u' | '.join([u'%d' % v for v in BY]),
           u' | '.join([u'%d' % v for v in WD]),
           u' | '.join([u'%d(%d)' % (LN[i], NB[i]) for i in range(5)]),
           u' | '.join([u'%d' % v for v in CP]),
           u' | '.join([u'%d' % len(FACES[i]) for i in range(5)]),
           enc_ch, enc_cp, sum(CH), u'%.1f%%' % (100.0 * enc_ch / sum(CH)),
           sum(WD), enc_ch,
           len(atoms), ok, len(atoms) - ok, own[0], own[1], own[2], own[3], own[4],
           tags, len(atoms),
           u'⇎'.join([u'%d' % v for v in ANS_OK]),
           u'⇎'.join([u'%d' % v for v in Z305]),
           ok, len(atoms), max(CP), enc_cp))

head, tail = md.split(u'## ⛓解读注', 1)
i2 = tail.find(u'\n## ')
new = head + NOTE + (tail[i2:] if i2 >= 0 else u'\n')
assert new.count(u'## ⟪BabelTele⟫') == 1, new.count(u'## ⟪BabelTele⟫')
assert new.count(u'## ⛓解读注') == 1
assert ok == len(atoms), u'有锚穿不到原文: %s' % [atoms[k][:50] for k, h in enumerate(hits) if h < 0]
io.open(ENTRY, 'w', encoding='utf-8', newline=u'\n').write(new)
print(u'B92 解读注已写入: 锚 %d/%d, 编码 %d 字符 ⇎ 五源合 %d 字符, 305 出现 %s'
      % (ok, len(atoms), enc_ch, sum(CH), Z305))
