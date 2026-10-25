# -*- coding: utf-8 -*-
# B40 判词修订: 把所有数字断言限制在“唯一键可机检”的集合内, 重复值的断言改为缺席断言。
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
F = 'corpus/_mkB40.py'
t = io.open(F, encoding='utf-8').read()

R = [
 (u'相隔 6 周', u'前后相隔不足三个月'),
 (u'同一句义务在三源各出现 1 次（机检）, 而 ⟦C⟧⟨within 120 days⟩ 之外的公布距离决定 3 年 ≈ 期限的 9.1 倍',
  u'同一句义务在三份里逐字相同（机检 3, 即每份 1 次）, 而 ⟦C⟧⟨within 120 days⟩ 之外的公布距离约为期限的 9.1 倍'),
 (u'叫 ⟦C⟧⟨human factors⟩（3 次）, 在 ⟦M⟧ 叫 ⟦M⟧⟨usability⟩（2 次）',
  u'叫 ⟦C⟧⟨human factors⟩, 在 ⟦M⟧ 叫 ⟦M⟧⟨usability⟩'),
 (u'⟦C⟧⟨Overreliance⟩（过度依赖）在 ⟦C⟧/⟦M⟧ 各 1、2 次而在 ⟦R⟧ 为 0（机检 1）',
  u'⟦C⟧⟨Overreliance⟩（过度依赖）在 ⟦R⟧ 完全为 0（机检零值键）'),
 (u'⇒ ⟦C⟧⟨demographic⟩ 在 ⟦C⟧ 出现 4 次、⟦R⟧ 2 次、⟦M⟧ 0 次（机检零值键）,',
  u'⇒ ⟦C⟧⟨demographic⟩ 三份合计 6 次而 ⟦M⟧ 为 0（机检 6 与零值键）,'),
 (u'⇒ ⟦C⟧⟨Warning⟩ 在 ⟦C⟧ 出现 2 次、⟦M⟧ 4 次、⟦R⟧ 0 次（机检零值键）:',
  u'⇒ “警告”这个词在 ⟦R⟧ 一次也没出现（机检零值键）:'),
 (u'⇒ ⟦R⟧⟨predetermined change control⟩ 只在 ⟦R⟧ 出现, 在 ⟦C⟧/⟦M⟧ 为 0（机检零值键）',
  u'⇒ ⟦R⟧⟨predetermined change control⟩ 与其缩写 ⟦R⟧⟨PCCP⟩ 在 ⟦R⟧ 合计 17 次, 在 ⟦C⟧/⟦M⟧ 均为 0（机检 17 与零值键）'),
 (u'⟦R⟧⟨you⟩ 只在 ⟦R⟧ 出现 2 次而 ⟦C⟧/⟦M⟧ 为 0（机检 2）, 义务词 ⟦C⟧⟨must⟩ 三份合计 31 次（机检推导）',
  u'⟦R⟧⟨you⟩ 三份合计 2 次且只落在 ⟦R⟧（机检 2, ⟦C⟧ 与 ⟦M⟧ 归零值键）, 义务词 ⟦C⟧⟨must⟩ 三份合计 31 次、其中 ⟦C⟧ 15 次（机检 31、15）'),
 (u'⇒ 这条脚注在三份里各出现 2 次（标题行 + 脚注, 机检 2）, 内容与器械无关, 只与 2019 年 12 月起的一次编辑体例改动有关; 两份模板一个给 ⟦R⟧⟨ACTION⟩ 加引号一个不加（机检: 两串各自只在自己的文件里命中）⇒ 同一机关内部的模板也会在细节上飘移, 引用体例说明时不能假定逐字相同。',
  u'⇒ 这条脚注与 ⟦C⟧⟨Final amendment; final order⟩ 一起出现在每份的标题行与脚注, 内容与器械无关, 只与 2019 年 12 月起的一次编辑体例改动有关; 两份模板一个给 ⟦R⟧⟨ACTION⟩ 加引号一个不加——规范化把这一差别抹平, 两串在 ⟦C⟧ 与 ⟦R⟧ 命中同一文本 ⇒ 引号级飘移只能靠逐字锚保留, 同一机关内部的模板也会在细节上漂移。'),
]
for old, new in R:
    n = t.count(old)
    assert n == 1, (n, old[:48])
    t = t.replace(old, new)
io.open(F, 'w', encoding='utf-8').write(t)
print('patched %d' % len(R))
