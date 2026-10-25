```python
# 替换 corpus/_mkB95.py 中 F['shell_pred_diff'] 与 assert 之间的行(即原 "F['shell_pred_diff'] = [...]" 至 "assert F['shell_pred_diff'] == [0] * NSRC, u'两把壳尺逐行不同集'" 整段), 位置在第 1 节壳账中 F['shell_shape'] 之后
F['shell_pred_diff'] = [len([1 for k, x in enumerate(L[i]) if is_shell_pick(x, i) != shell_shape(x, i)])
                        for i in range(NSRC)]
# 分歧行显式记账: 两把尺逐行之差, 由 pick 侧与 shape 侧二值表现算, 不硬填 0
_shell_bits = [[[1 if is_shell_pick(x, i) else 0, 1 if shell_shape(x, i) else 0]
                for x in L[i]] for i in range(NSRC)]
F['shell_bits'] = _shell_bits
F['shell_pred_gap'] = [len([1 for k in range(len(L[i]))
                            if _shell_bits[i][k][0] != _shell_bits[i][k][1]])
                       for i in range(NSRC)]
F['shell_pred_gap_pos'] = [[k + 1, x] for i in range(NSRC) for k, x in enumerate(L[i])
                           if _shell_bits[i][k][0] != _shell_bits[i][k][1]]
F['shell_pred_gap_n'] = sum(F['shell_pred_gap'])
F['shell_pred_diff'] = list(F['shell_pred_gap'])
F['shell_lines'] = F['shell_shape']
F['body_lines'] = [F['splitnl'][i] - F['shell_lines'][i] for i in range(NSRC)]
F['shape_hits'] = [sum([len([1 for x in L[i] if f(x)]) for f in selpred(i)]) for i in range(NSRC)]
F['shape_ovl'] = [sum([max(0, len([1 for f in selpred(i) if f(x)]) - 1) for x in L[i]])
                  for i in range(NSRC)]
F['shell_ledger'] = [F['shell_lines'][i] - (F['shape_hits'][i] - F['shape_ovl'][i]) for i in range(NSRC)]
F['page_pair_gap'] = [F['foot_page'][i] - F['hdr_rfc'][i] for i in range(NSRC)]
print(u'1 壳: [Page]', F['foot_page'], u'RFC眉', F['hdr_rfc'], u'pg.', F['br_pgnum'],
      u'两尺壳行', F['shell_pick'], F['shell_shape'], u'逐行分歧', F['shell_pred_diff'],
      u'分歧键', F['shell_pred_gap'], u'分歧行数', F['shell_pred_gap_n'])
# 一次性诊断: 把分歧行原样印出(不 assert, 只报形状)
for i in range(NSRC):
    if F['shell_pred_gap'][i]:
        print(u'  [分歧] %s 份 %d 行, shape 判为壳的 %d 行' % (LBL[i], F['shell_pred_gap'][i],
                                                              F['shell_shape'][i]))
        for k, x in enumerate(L[i]):
            if _shell_bits[i][k][0] != _shell_bits[i][k][1]:
                print(u'    行 %d pick=%d shape=%d |%s|' % (k + 1, _shell_bits[i][k][0],
                                                            _shell_bits[i][k][1], x[:120]))
```

```python
# 替换 corpus/_mkB95.py 布尔门中 G.append((u'壳谓词两把尺逐行同集', F['shell_pred_diff'] == [0] * NSRC)) 这一行
G.append((u'壳谓词两把尺逐行同集(分歧键归零)', F['shell_pred_gap'] == [0] * NSRC))
```

```python
# 新增到 corpus/_mkB95.py 布尔门之后、ZID 段之前(即 "G.append((u'壳账容斥闭合'..." 之前) 的独立判据段
# 两条独立判据保留: A) 逐行同集 B) 存量计数同值; 均现算分歧, 不做硬 assert
_cA = F['shell_pred_gap'] == [0] * NSRC
_cB = F['shell_pick'] == F['shell_shape']
F['shell_pair_same'] = 1 if (_cA and _cB) else 0
F['shell_pair_gapA'] = F['shell_pred_gap_n']
F['shell_pair_gapB'] = [F['shell_pick'][i] - F['shell_shape'][i] for i in range(NSRC)]
F['shell_pair_gapB_n'] = sum(abs(z) for z in F['shell_pair_gapB'])
print(u'壳两判据: 同集=%d 同值=%d ⇎ 逐行分歧=%d 存量差=%d' % (_cA, _cB, F['shell_pair_gapA'],
                                                              F['shell_pair_gapB_n']))
```

```python
# 新增到 corpus/_mkB95.py 的 ZID 恒等式段内(接在 Z(u"sum(F['shell_ledger'])", ...) 之后, 即 "壳账容斥" 那条之后)
Z(u"F['shell_pred_gap_n'] - sum(F['shell_pred_gap'])", u'分歧键总量 = 逐份分歧之和(两路各自数出)')
Z(u"F['shell_pred_gap_n'] - sum([len([1 for k in range(len(L[i])) if F['shell_bits'][i][k][0] != F['shell_bits'][i][k][1]]) for i in range(NSRC)])",
  u'分歧键 = 二值表逐格差异之数')
Z(u"F['shell_pair_gapB_n'] - sum([abs(F['shell_pick'][i] - F['shell_shape'][i]) for i in range(NSRC)])",
  u'存量差 = 两尺计数之差的绝对值和')
Z(u"F['shell_pair_same'] - (1 if (F['shell_pred_gap'] == [0]*NSRC and F['shell_pick'] == F['shell_shape']) else 0)",
  u'两判据合并标志 = 同集且同值')
```

```python
# 替换 corpus/_mkB95.py 中 emit 阶段之前的 ZID 形对拍循环中依赖 shell_pred_diff 的段落不需改; 但需在 corpus/_mk95emit.py 对应编码区新增登记 shell_pred_gap
# 新增到 corpus/_mk95emit.py 壳账编码段(⟦shell⟧ 块)中, 在 shell_pred_diff 登记行之后
u'两把壳尺逐行分歧键: ' + V('shell_pred_gap') + u'(逐份; 合计 ' + V('shell_pred_gap_n') + u')'
u'壳尺两判据合并: 同集 ⇎ 同值 = ' + V('shell_pair_same') + u'(逐行同集分歧 ' + V('shell_pair_gapA')
u' ⇎ 存量差 ' + V('shell_pair_gapB_n') + u')'
```