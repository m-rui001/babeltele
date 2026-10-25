# -*- coding: utf-8 -*-
"""回改 B80 的三处 README 记账行(判词段 ⇎ 门槛表行 ⇎ 语料表行): 只换这三行, 其余字节不动。

改文的三处“数对但话错”:
① 把 `shell_lines`(剥壳谓词剥掉的行数)写成“页壳行”, 于是 9110 读成“零页壳 ⇎ 壳行 2127 行”自相矛盾
   ——本遍现数五份账成立: 剥壳行 = 空行数 + 紧排抬头行数(逐份差 0), 9110 被剥的全是空行;
② 语料表把 9110 名下 11 枚针(含 3 枚反向对照针)说成“全在 §9.2.2 之内”, 门槛表同一句用的却是 8 枚内容针——
   改成同一把尺(8 枚内容针), 另把 3 枚反向针单独申报;
③ 判词段说“其余全是 ABNF 与裸 URL 的尖括号伪法”, 把 2616 的 25 枚 ⇎ 9110 的 6 枚开名形一并归进余数——
   本遍把开名形再分 ABNF 值占位 ⇎ 真标签名两档, 行文改按实测分档写, 点名的每一枚尖括号片段都回自己那一源核验。

三行文本仍由 _readme80.py 的那一段构建代码现算(取到“落盘”标记前为止), 不手打数字。
"""
import io
import os
import re

SRC = io.open(u'corpus/_readme80.py', encoding=u'utf-8').read()
HEAD = SRC.split(u"# ---------- 落盘")[0]
# README 已落过一次 B80: 复算遍把上一遍的记账视为未记账, 其余逻辑照跑
HEAD = HEAD.replace(u"assert u'B80' not in LISTED0 and S.count(u'| B80 |') == 0 "
                    u"and S.count(u'**B80 问的是') == 0",
                    u"LISTED0 = [x for x in LISTED0 if x != u'B80']")
assert u"LISTED0 = [x for x in LISTED0 if x != u'B80']" in HEAD
NS = {'__name__': u'__patch80__'}
exec(compile(HEAD, u'_readme80.py[head]', u'exec'), NS)
NL, HEADROW, C80, PARA = NS[u'NL'], NS[u'HEADROW'], NS[u'C80'], NS[u'PARA']
OLD = io.open(u'corpus/README.md', encoding=u'utf-8').read()
SL = OLD.split(NL)


def repl(pred, new, label, n=1):
    idx = [i for i, l in enumerate(SL) if pred(l)]
    assert len(idx) == n, (label, idx)
    for i in idx:
        SL[i] = new
    return idx


a = repl(lambda l: l.startswith(u'**B80 问的是'), PARA, u'判词段')
b = repl(lambda l: l.startswith(u'| B80 | 12 954（新建'), HEADROW, u'门槛表行')
c = repl(lambda l: l.startswith(u'| B80 | `raw/'), C80, u'语料表行')
assert [SL[i].count(u'|') for i in (b[0], c[0])] == [3, 4]
assert SL[a[0]].count(u'`') % 2 == 0 and SL[b[0]].count(u'`') % 2 == 0
NEW = NL.join(SL)
print(u'三行净变化: %+d 字符' % (len(NEW) - len(OLD)))
T = u'corpus/README.md.tmp80p'
io.open(T, u'w', encoding=u'utf-8', newline=NL).write(NEW)
os.replace(T, u'corpus/README.md')
print(u'回改三行: 判词段@%d ⇎ 门槛表@%d ⇎ 语料表@%d ｜ 剥壳行账 %s ｜ 9110 内容针 %d ⇎ 反向 %d'
      % (a[0], b[0], c[0],
         [NS[u'gk'](u'shell_lines')[i] - (NS[u'LN'][i] - NS[u'NB'][i]) - NS[u'gk'](u'hdr_lines_tight')[i]
          for i in range(5)],
         NS[u'gk'](u'k9110_tot'), NS[u'gk'](u'neg_own_nd')[4]))
for k in (u'shell_lines', u'hdr_lines_tight', u'tag_open', u'tag_pseudo'):
    print(u'  %s = %s' % (k, NS[u'gk'](k)))
print(u'  ABNF 值占位 ⇎ 真标签名 = %s ⇎ %s ｜ `<\">` %s ｜ 成因四档 词头无字母 %s ⇎ 撞连字符 %s ⇎ 撞逗号 %s ⇎ 撞冒号 %s'
      % (NS[u'ABNFN'], NS[u'HTMO'], NS[u'DQ'], NS[u'HEADP'], NS[u'HYPF'], NS[u'CMMA'], NS[u'CLON']))
print(u'  最短样例 %s' % NS[u'EXSTR'])
