# -*- coding: utf-8 -*-
# 造外派任务清单: 每个条目若干路并发(同题不同温度/不同切法), 返回件由 corpus/_api_test.py 现跑现判。
# 用法: python -X utf8 corpus/_api_tasks9x.py            → corpus/_api9x_tasks.json
import io, json, os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


SYS = (u'你在维护一个语料保真审计库(Python 2 风格字符串一律 u 前缀, 只用标准库)。硬契约:\n'
       u'1) 建条目遍 _mkBNN.py 发射条目 .md: 编码区(## ⟪BabelTele⟫ 之后)里的每个数字都必须由 V(\'key\') '
       u'从量测字典 F 插值, 零手填; V() 把面值→"BNNV(\'key\')" 记进 REG, 遍末 REG 落 corpus/_bNNflat.json。\n'
       u'2) 编码锚 ⟨原文片段⟩ 必须能在最宽档(小写+撇号删+连字符族归一+非 [0-9a-z汉字.-空格] 换空格+空白折一) '
       u'里从对应 ⟦X⟧ 块穿到; 标签 ⟦X⟧ 只准引第 X 块的字面串。\n'
       u'3) 采集遍 _pickNN.py 与建条目遍 _mkBNN.py 是同一套定义的两套机制(换算路不换口径), 逐键对账; '
       u'某键口径确实不同时, 要么改成同定义, 要么显式列入该遍的"口径不同不对账"清单并写明差在哪把尺。\n'
       u'4) 任何 *closure/gap/diff* 类键必须现算自同一遍的其它键, 不许硬填 0。\n'
       u'输出格式(严格): 只输出一个 ```python 代码块, 块前一行注释点名"替换 corpus/xxx.py 的哪几行/新增到哪段之后", '
       u'块内是可直接粘贴的完整段落; 不要任何解释文字、不要 markdown 小节、不要用中文写代码注释以外的说明。')

T = []


def add(tid, body, temp, mt=24000):
    T.append({u'id': tid, u'system': SYS, u'prompt': body, u'temperature': temp,
              u'max_tokens': mt})


# —— B95: 两把壳谓词逐行不同集 ——
mk95 = rd('corpus/_mkB95.py')
p95 = rd('corpus/_tmp95_mklog.txt')
for i, cut in enumerate([u'把两把尺对齐成同一口径(只留一条判据, 另一条改为由它现推的复算)',
                         u'保留两条独立判据, 但把硬 assert 改成现算分歧键并在条目编码区登记(键名 shell_pred_gap), '
                         u'同时给出一段一次性诊断把分歧行的形状印出来',
                         u'先判定分歧到底出在哪一类行(页壳/签名行/空行/换页符), 再只改谓词里出错的那一支定义, '
                         u'使两尺逐行同集且 assert 原样保留']):
    add(u'B95fix%d' % i,
        u'文件 corpus/_mkB95.py 运行到 `assert F[\'shell_pred_diff\'] == [0] * NSRC, u\'两把壳尺逐行不同集\'` 就断。\n'
        u'报错尾迹:\n' + p95[-1200:] + u'\n\n全文如下:\n```python\n' + mk95 + u'\n```\n\n要求' + cut + u'。',
        [0.2, 0.6, 0.95][i])

# —— B99: 四键对账不符 ——
mk99 = rd('corpus/_mkB99.py')
p99 = rd('corpus/_tmp99_mklog.txt')
for i, cut in enumerate([u'逐个把不符键的两侧定义改成同一把尺(改的那一侧要说明换了哪一步机制)',
                         u'不改定义, 把这四键移进"口径不同而不对账"清单并补一句差在哪, 保证对账件仍能落盘、条目仍能发射',
                         u'先印出四键两侧读数与差, 再判断是数据面差异还是口径差异; 若属口径差异就给对齐后的代码']):
    add(u'B99fix%d' % i,
        u'文件 corpus/_mkB99.py 是 B99 的第二套实现, 跑完打印 "PICK 对账: 87 键符 ⇎ 4 键不符 [\'cut_lf⇎cut_lf\', '
        u'\'efb_len⇎face_sh\', \'needle_src⇎needle_src\', \'pgnum_pick?pgnum\']" 之后没有发射条目。\n'
        u'尾迹:\n' + p99[-1500:] + u'\n\n全文如下:\n```python\n' + mk99 + u'\n```\n\n要求' + cut + u'。',
        [0.2, 0.6, 0.95][i])

# —— B93 / B94 / B97: 只有采集遍, 缺建条目遍 ——
TMPL = rd('corpus/_mkB96.py')
for tag, pick in ((u'B93', u'corpus/_pick93.py'), (u'B94', u'corpus/_pick94.py'),
                  (u'B97', u'corpus/_pick97.py')):
    pk = rd(pick)
    meas = rd(u'corpus/_%smeas.json' % tag.lower())
    n = len(json.loads(meas)) if meas.strip().startswith(u'{') else 0
    for i, cut in enumerate([u'照 corpus/_mkB96.py 的骨架逐段移植(READ ⇎ 常量 ⇎ SCAN 段 ⇎ 闭合断言 ⇎ 读对账件 ⇎ '
                             u'V() 插值发射 ⇎ REG 落 corpus/_%sflat.json), SCAN 段要换一套机制而不是照抄 %s 的算路'
                             % (tag.lower(), tag),
                             u'同上骨架, 但编码区的行文按"问题⇎五份文书各答一遍⇎每答挂一枚原文锚"的次序组织, '
                             u'数字一律 V() 插值',
                             u'同上骨架, 但把 %s 采集遍里所有 *gap/diff/close* 类键在发射前逐条断言归零, '
                             u'并把门槛表/语料表两行的口径注写成条目 .md 的固定段落' % tag]):
        add(u'%s_mk%d' % (tag, i),
            u'条目 %s 只有采集遍 corpus/%s, 它把逐源读数落盘成 corpus/_%smeas.json(键→逐源读数列表或标量, '
            u'共 %d 枚键); 现在缺建条目遍 corpus/_mkB%s.py(第二套实现 + 发射条目 .md)。\n'
            u'范本(已进门, 门槛 PASS)corpus/_mkB96.py 全文:\n```python\n' + TMPL + u'\n```\n\n'
            u'%s 采集遍全文:\n```python\n' % tag + pk + u'\n```\n\n'
            u'读数件(截断):\n' + meas[:14000] + u'\n\n要求' + cut + u'。',
            [0.2, 0.6, 0.95][i], mt=30000)

json.dump(T, io.open('corpus/_api9x_tasks.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(u'任务 %d 路; 提示词总字节 %d' % (len(T), sum(len(json.dumps(z, ensure_ascii=False)) for z in T)))
for z in T:
    print(u' ', z[u'id'], len(z[u'prompt']), z[u'temperature'])
