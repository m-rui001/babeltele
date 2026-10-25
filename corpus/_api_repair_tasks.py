# -*- coding: utf-8 -*-
# 二遍外派(修稿): 把首遍落回的整件候选现跑一遍抓trace, 连代码一起再扔回给同一批免费模型修,
# 每件两路(低温只改报错处 ⇎ 高温允许删掉无法成立的量测键)。落 corpus/_api9x_repair.json。
import io, json, os, subprocess, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANDS = [f for f in sorted(os.listdir(u'corpus')) if f.startswith(u'_apick_') and f.endswith(u'.py')]
SYS = (u'你在修一个 Python 3 脚本(语料保真审计库的建条目遍)。契约(不可违背):\n'
       u'1) 编码区的每个数字一律由 V(\'key\') 从量测字典插值, 零手填; 遍末把 REG 落 corpus/_bNNflat.json。\n'
       u'2) 锚 ⟨片段⟩ 必须逐字能在对应原文块里穿到(最宽档); 穿不到的锚就删掉这句, 不许改写成近似串。\n'
       u'3) 针(needle)在源里 0 命中时: 先确认是不是自己的档错了(硬换行切断/引号档/大小写档); '
       u'确实不在源里的, 把依赖它的键连同引用它的句子一起删, 不留假读数、不把 assert 改成 True。\n'
       u'4) 两套实现换机制不换定义; 对账不过就改定义, 不许把不符键静默剔出对账集。\n'
       u'5) 只用标准库; 字符串一律 u 前缀; 不要 print 无关内容。\n'
       u'输出(严格): 只输出一个 ```python 代码块 = 修好的整份文件全文(可整件替换), 不许只给片段/diff。')

T = []
for f in CANDS:
    p = u'corpus/' + f
    code = io.open(p, encoding='utf-8', errors='replace').read()
    if len(code) > 60000:
        continue
    try:
        r = subprocess.run([sys.executable, u'-X', u'utf8', p], capture_output=True,
                           text=True, encoding=u'utf-8', errors=u'replace', timeout=600)
        tr = ((r.stderr or u'')[-2500:])
        st = r.returncode
    except Exception as e:
        tr, st = repr(e), -1
    if st == 0:
        print(u'%s 已过, 不必修' % f)
        continue
    cid = f[len(u'_apick_'):-len(u'.py')]
    for i, cut in enumerate([u'只改报错处所在的那一段, 其余逐字符原样保留。',
                             u'允许删掉无法成立的量测键与引用它的句子(删要删干净: 键 ⇎ 断言 ⇎ 编码区句子一起删), '
                             u'其余原样保留。']):
        T.append({u'id': u'%s_rp%d' % (cid, i), u'system': SYS, u'temperature': [0.2, 0.8][i],
                  u'max_tokens': 30000,
                  u'prompt': u'文件 %s 跑到退出码 %d, 尾迹:\n%s\n\n全文:\n```python\n%s\n```\n\n要求%s'
                             % (p, st, tr, code, cut)})
json.dump(T, io.open(u'corpus/_api9x_repair.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(u'修稿任务 %d 路 ⇎ 候选 %d 件' % (len(T), len(CANDS)))
