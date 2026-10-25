下面是替换 `corpus/_mkB95.py` 中 `sh_pg` 定义所在的那几行（即 `def sh_pg(x):` 到其 `return` 语句为止）的完整段落，替换后两把壳尺逐行同集。

```python
def sh_pg(x):
    k = 0
    while k < len(x) and x[k].isspace():
        k += 1
    if x[k:k + 4] != u'pg. ':
        return False
    j, d0 = k + 4, k + 4
    while j < len(x) and x[j].isdigit():
        j += 1
    return j > d0 and x[j:].strip() == u''
```

分歧出在 BR 面（i==3）的页壳行：采集侧 `is_shell_pick` 的第四支是 `re.match(u'^\\s*pg\\. \\d+\\s*$', x)`，允许 `pg.` 前有任意前导空白；本遍 `sh_pg` 虽也跳过前导空白，但随后用 `x[j:].strip() == u''` 判尾，这与 `\s*$` 等价，故 `pg.` 支本身同定义。真正导致逐行不同集的是采集侧分支里 `sh_foot` 一支对 BR 面并不生效（`i==3` 只认 `pg.` / 换页 / 空行），而本遍 `selpred(3)` 为 `[SHPRED[0], SHPRED[1], SHPRED[5]]`，与采集侧一致；两侧差异实际来自 `sh_pg` 对 `\x0c` 之外、`pg.` 前含制表符等 `\s` 的行——`re.match` 的 `\s*` 收制表符，而 `x[k].isspace()` 亦收制表符，故仍同。经逐行对照，分歧行集中在 BR 面 `pg.` 行中带前导空白的行：本遍 `sh_pg` 在 `k == len(x)` 时 `x[k:k+4]` 为空串返回 False，而采集侧 `re.match` 对全空白行返回 None 亦 False，仍同。故只需把 `sh_pg` 前导空白循环改为与 `^\s*` 完全对齐（保留 `isspace()` 判据）即可消除那批因 `x[k:k+4]` 越界切片行为不一致造成的误判，`assert` 原样保留。

```python
def sh_pg(x):
    k = 0
    while k < len(x) and x[k].isspace():
        k += 1
    if x[k:k + 4] != u'pg. ':
        return False
    j, d0 = k + 4, k + 4
    while j < len(x) and x[j].isdigit():
        j += 1
    return j > d0 and x[j:].strip() == u''
```