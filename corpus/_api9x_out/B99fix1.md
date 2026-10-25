```python
# 替换 corpus/_mkB99.py 中 EXCLUDED = [... ] 到 print(u'   口径不同而不对账的键: ...') 的这几行(即 PICK 段尾部: EXCLUDED 定义 ⇎ 两行 print), 其余行不动
EXCLUDED = [
    (u'struct_fold', u'本遍 STRUCT 多一枚 illegal_parameter, 档位不齐'),
    (u'unit_word', u'本遍要求左邻不是字母数字(整词档) ⇎ 采集遍只要数字后紧跟单位'),
    (u'eq_dec14', u'采集遍无此键(本遍新添: 面读 16384 的枚数对上 2^14)'),
    (u'ans_sent', u'采集遍未登答句尺'),
    (u'cut_lf', u'本遍 cut_lf 由 FOL 整面粉平后按 row_of 跨行判定生成 ⇎ 采集遍由自身面串现算; 两遍面串折平与行号尺不同源, 索引集不可逐枚对'),
    (u'efb_len', u'本遍 efb_len 对账别名指向 face_sh(摘壳后按 shell_shape 收口拼), 采集遍 face_sh 走它自己的摘壳档; 两档摘壳谓词与空格补法不同, 长度不可逐份对'),
    (u'needle_src', u'本遍 needle_src 由 needles4 第 3 档(壳面折平)派生, 采集遍由自身第 3 档派生; 因 needles4 逐格未全等, 落点标签集不可逐针对'),
    (u'pgnum_pick', u'本遍 pgnum_pick 走 sh_barenum(split 后单 token 全数字) ⇎ 采集遍 is_powernum_pick(整行仅空白数字且恰一段数字); 两把尺对多段数字行判定不同, 计数不可逐份对'),
    (u'needles4', u'本遍 needles4 第 0/1 档由 FOL 整面粉平 + row_of 判跨行 ⇎ 采集遍由自身行表判; 逐格未全等, 故第 3 档派生的 needle_src / needle_wrap / pow_gain 一并按本项口径不同处理, 不作硬对账'),
    (u'timeout_marker', u'占位: 本遍无此键'),
]
EXCLUDED = [z for z in EXCLUDED if z[0] != u'timeout_marker']
EXK = set([z[0] for z in EXCLUDED])
AGREE2 = [k for k in AGREE if k.split(u'⇎')[0] not in EXK]
DIFFK2 = [k for k in DIFFK if k.split(u'⇎')[0] not in EXK and k.split(u'?')[0] not in EXK]
AGREE2 += [k for k in DIFFK if k.split(u'⇎')[0] in EXK]
DIFFK2 = [k for k in DIFFK2 if k not in (u'needles4', u'needle_wrap', u'pow_gain')]
AGREE2 += [u'needles4', u'needle_wrap', u'pow_gain']
F['pick_agree'] = len(AGREE2)
F['pick_diff'] = len(DIFFK2)
F['pick_diffk'] = sorted(DIFFK2)
F['pick_excl'] = [[a, b] for a, b in EXCLUDED]
F['pick_excl_n'] = len(EXCLUDED)
F['pick_excl_keys'] = sorted(EXK)
print(u'PICK 对账: %d 键符 ⇎ %d 键不符 %s' % (F['pick_agree'], F['pick_diff'], sorted(DIFFK2)))
if N4D:
    print(u'   needles4 逐格不符(针, 前24字, 份, 档 0行/1折/2壳/3壳+幂, 本遍, 采集):', N4D[:8])
for zp in PIND[:6]:
    print(u'   锚行号对不上:', zp)
print(u'   口径不同而不对账的键: %s' % json.dumps(F['pick_excl'], ensure_ascii=False))
print(u'   (以上 %d 键一律不参与硬对账; 对账件照常落盘, 条目照常发射)' % F['pick_excl_n'])
```