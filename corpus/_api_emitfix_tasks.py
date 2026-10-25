# -*- coding: utf-8 -*-
# 把语法坏掉的发射段草稿交给 API 修(只修语法, 一字内容不许动)。
# 用法: python -X utf8 corpus/_api_emitfix_tasks.py   → 落 corpus/_api9x_emitfix.json
import io
import json
import os
import re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 试跑器报出的语法错(文件, 行, 报错)
BAD = [
    (u'B95', u'0', 212, u"unmatched ')'"),
    (u'B95', u'1', 124, u"invalid syntax. Perhaps you forgot a comma? —— 中文正文里的裸双引号把 u\"…\" 字符串截断了"),
    (u'B98', u'0', 203, u"closing parenthesis ')' does not match opening parenthesis '[' on line 202"),
]

SYS = (u'你是 Python 3 语法修理工。给你一段发射段代码和一个编译报错行号。\n'
       u'铁律: 只许动语法(括号配对 ⇎ 字符串边界 ⇎ 逗号 ⇎ 文件名拼写), 内容 ⇎ 措辞 ⇎ 数字 ⇎ 插值一律不许改;\n'
       u'中文正文里若要引用短语, 一律用「」或转义, 不许让裸双引号截断 u"…" 字符串。\n'
       u'输出(严格): 只输出一个 ```python 代码块 = 修好的整段全文, 不要任何解释。')

T = []
for tg, k, ln, note in BAD:
    p = u'corpus/_api9x_emit_out/%s_em%s.md' % (tg, k)
    s = io.open(p, encoding='utf-8').read()
    m = re.search(u'```python\n(.*?)\n```', s, re.S)
    code = m.group(1)
    ctx = u'\n'.join([u'%3d| %s' % (i + 1, l) for i, l in enumerate(code.split(u'\n'))
                      if ln == 0 or abs(i + 1 - ln) <= 6])
    T.append({
        u'id': u'%s_em%s_fx' % (tg, k),
        u'system': SYS,
        u'temperature': 0.2,
        u'max_tokens': 24000,
        u'prompt': (u'# 报错\nline %d: %s\n\n# 报错行上下文(带行号)\n%s\n\n# 全文(需原样返回, 只改语法)\n%s'
                   % (ln, note, ctx, code)),
    })

io.open(u'corpus/_api9x_emitfix.json', 'w', encoding='utf-8').write(
    json.dumps(T, ensure_ascii=False, indent=1) if (json := __import__('json')) else u'')
print(u'发射段修语法任务 %d 路; 提示词长度 %s' % (len(T), [len(t[u'prompt']) for t in T]))
