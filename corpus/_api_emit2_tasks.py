# -*- coding: utf-8 -*-
# 外派写稿第二轮(发射段): 上一轮六路里四路语法坏、一路截断、一路把提示词抄进了正文。
# 病根: 只给了范例条目 md(产物), 没给机制(产物是怎么由量测字典 F 拼出来的)。
# 本轮改给三段实料: ①B92 发射段真码(机制) ②锚词汇表全文(引文只准按索引取) ③F 键值全表(列表截 12 项)。
# 另加三条可机检的自证: 编码区不许出现字面 "V(" ⇎ 每个数字 token 要么在 REG 里要么是锚原文里的数 ⇎
# ⟦标签⟧ 枚数必须等于 ⟨锚⟩ 枚数。用法: python -X utf8 corpus/_api_emit2_tasks.py
import io
import json
import os
import re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = [u'B95', u'B98', u'B99']
MECH = u'corpus/_mkB92.py'

mk = io.open(MECH, encoding='utf-8').read().split(u'\n')
i0 = [i for i, l in enumerate(mk) if l.startswith(u'# ---- 扁平契约登记')][0]
M = u'\n'.join(mk[i0:685])
M = M.replace(u'B92', u'BNN').replace(u'_b92flat', u'_bNNcontract').replace(u'_atoms92', u'_atomsNN')


def fshape(path):
    d = json.load(io.open(path, encoding='utf-8'))
    out = {}
    for k, v in d.items():
        if isinstance(v, list):
            if v and isinstance(v[0], list):
                out[k] = u'[[%d项/格]×%d格]' % (len(v[0]), len(v))
                continue
            s = [x if (not isinstance(x, str) or len(x) <= 10) else u'«%d字»' % len(x) for x in v[:12]]
            out[k] = s if len(v) <= 12 else s + [u'…共 %d 项' % len(v)]
        elif isinstance(v, str) and len(v) > 60:
            out[k] = u'«字符串 %d 字»' % len(v)
        else:
            out[k] = v
    return out


SYS = (u'你在为"推理密度语料压缩库"写一条新条目的**发射段**(Python 3, 在 _mkNN.py 末尾被 exec, '
       u'因此 F ⇎ DER ⇎ FILES ⇎ LBL ⇎ io ⇎ json ⇎ re 已在场)。这是全库唯一的写稿动作: 中文编码区里每一枚数字'
       u'都由量测字典现插, 一个都不手填。\n'
       u'铁律(违背即废稿):\n'
       u'1) 数字: 一律 V(\'key\') 或 V(\'key\', i) 插值。V 把面值登记进 REG[str(v)] = "BNNV(\'key\')" / '
       u'"BNNV(\'key\', i)" 并返回该值。REG 的枚数必须 ≥ 30, 否则视为手填。V 只插**数值**键(整/浮点), '
       u'表里标 «字符串 N 字» ⇎ «共 N 项» ⇎ […] 的键不要拿来当数字用。\n'
       u'2) 锚: 只准从 corpus/_atomsNN.txt 读出的 ATOMS 表里**按索引**取文本(ATOMS[i][1]), 标签取 ATOMS[i][0]; '
       u'写编码区时拼成 ⟦标签⟧⟨锚原文⟩。词汇表以外的句子一律不许引, 也不许自己改写锚文本。\n'
       u'3) 自检(必须原样写进代码并 assert): 编码区里 ⟦⟧ 枚数 == ⟨⟩ 枚数; 编码区文本里不得出现字面 "V("; '
       u'每个 \\d[\\d.]* token 要么已在 REG 的键里, 要么出现在被引锚原文里, 否则报"无着落"并失败。\n'
       u'4) 写盘: md 落 corpus/babeltele/BNN_<英文短名>.md(结构照范例: # 标题 ⇎ src: ⇎ tags: ⇎ '
       u'## [[原始语料|ORIGINAL]] 按标签分组的锚块 ⇎ ## ⟪BabelTele⟫ 编码区 ⇎ ## ⛓解读注 占位一行); '
       u'REG 落 corpus/_bNNcontract.json(紧凑 json)。除这两类路径外不许写任何文件, 不许 print 无关内容, '
       u'结尾 print 一行收据(编码区字符数 ⇎ 锚枚数 ⇎ REG 枚数)。\n'
       u'5) 只准 io/json/re; 不许 import subprocess; 不许改 F; 正文里若要引用中文短语用「」, 别用裸双引号; '
       u'整段代码 ≤ 220 行, 不要把本提示词的任何一句抄进正文或注释。\n'
       u'输出(严格): 只输出一个 ```python 代码块 = corpus/_mkNNemit.py 全文。')

T = []
for tg in TAGS:
    NN = tg[1:]
    flat = u'corpus/_b%sflat.json' % NN
    F = fshape(flat)
    atoms = io.open(u'corpus/_atoms%s.txt' % NN, encoding='utf-8').read()
    pick = io.open(u'corpus/_pick%s.py' % NN, encoding='utf-8').read()
    doc = pick[pick.find(u'"""') + 3:pick.find(u'"""', pick.find(u'"""') + 3)] if u'"""' in pick else pick[:400]
    theme = doc[:1500]
    T.append({
        u'id': u'%s_e2a' % tg,
        u'system': SYS,
        u'temperature': 0.35,
        u'max_tokens': 30000,
        u'prompt': (u'# 目标条目 %s\n%s\n\n# 机制范例(B92 发射段全文, 名字里的 BNN/NN 要换成 %s/%s)\n```python\n%s\n```\n\n'
                    u'# 锚词汇表 corpus/_atoms%s.txt 全文(标签<TAB>原文)\n%s\n\n# 量测字典 F(%d 键, 列表最多截示 12 项)\n%s\n'
                    % (tg, theme, tg, NN, M, NN, atoms, len(F),
                       json.dumps(F, ensure_ascii=False, sort_keys=True, separators=(u',', u':')))),
    })
    T[-1][u'id'] = u'%s_e2a' % tg
    T.append(dict(T[-1], id=u'%s_e2b' % tg, temperature=0.8))

io.open(u'corpus/_api9x_emit2.json', 'w', encoding='utf-8').write(
    json.dumps(T, ensure_ascii=False, indent=1))
print(u'第二轮发射段任务 %d 路; 提示词长度 %s' % (len(T), [len(t[u'prompt']) for t in T]))
