# -*- coding: utf-8 -*-
"""幂等接线: 把 B40 注册进 audit.py 的 SRC/ATOM/DERIV 与 atomcheck.py 的 SRC。
DERIV 块先删后插——只判存在会留下旧键集而审计照样过。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

A = 'corpus/audit.py'
s = io.open(A, encoding='utf-8').read()

SRC40 = (u"SRC['B40'] = ['corpus/raw/prose/fr_fda_cardio_ml_notification.txt',\n"
         u"          'corpus/raw/prose/fr_fda_radiology_ml_pccp.txt',\n"
         u"          'corpus/raw/prose/fr_fda_opioid_impairment_monitor.txt']\n")
if "SRC['B40']" not in s:
    i = s.index(u'\nATOM = {')
    s = s[:i + 1] + SRC40 + s[i + 1:]

if u"'B39'}" in s and u"'B40'}" not in s:
    s = s.replace(u"'B39'}", u"'B39', 'B40'}", 1)

# audit 的 CNT 跑在**未规范化的原文**上, 而联邦公报正文有硬换行 ⇒ 词组必须把空格换成 \s+
def PH(p):
    if p.startswith(u'(?'):
        return p
    if p == u'510(k)':
        return u'510\\(k\\)'
    return u'\\s+'.join(re.escape(w) for w in p.split(u' '))


# 三份里的“这个词根本不出现”断言: 折叠成单个零值键, 逐项核对确实为 0
ABSENT_PHRASES = [
    (u'human factors', 1), (u'human factors', 2), (u'usability', 0), (u'usability', 1),
    (u'biocompatib', 0), (u'biocompatib', 1), (u'electromagnetic', 0), (u'electromagnetic', 1),
    (u'wireless', 0), (u'wireless', 1), (u'dice', 0), (u'dice', 2),
    (u'hausdorff', 0), (u'hausdorff', 2), (u'bland-alt', 0), (u'bland-alt', 2),
    (u'not intended', 1), (u'not intended', 2), (u'overreliance', 1), (u'demographic', 2),
    (u'warning', 1), (u'predetermined change control', 0), (u'predetermined change control', 2),
    (u'pccp', 0), (u'pccp', 2), (u'independent', 2), (u'separate', 1),
    (u'(?<![a-z])you(?![a-z])', 0), (u'(?<![a-z])you(?![a-z])', 2),
    (u'(?<![a-z])shall(?![a-z])', 0), (u'(?<![a-z])shall(?![a-z])', 1), (u'(?<![a-z])shall(?![a-z])', 2),
    (u'guarantee', 0), (u'guarantee', 1), (u'guarantee', 2),
]
ABSENT = [(PH(p), i) for p, i in ABSENT_PHRASES]
assert len(ABSENT) == 35, len(ABSENT)
ZERO = '+'.join(u'CNT(%r,%d)' % (p, i) for p, i in ABSENT)


def mean(p):
    p = PH(p)
    return u'round((CNT(%r,0)+CNT(%r,1)+CNT(%r,2))/3)' % (p, p, p)


def tot(p):
    p = PH(p)
    return u'CNT(%r,0)+CNT(%r,1)+CNT(%r,2)' % (p, p, p)


W = PH(u'(?<![a-z])we(?![a-z])')
Y = PH(u'(?<![a-z])you(?![a-z])')
MUST = PH(u'(?<![a-z])must(?![a-z])')

D = [
    ('0', ZERO),
    ('1', u'CNT(%r,2)' % PH(u'machine learning')),
    ('2', tot(Y)),
    ('3', tot(u'within 120 days')),
    ('4', u'CNT(%r,0)' % PH(u'not intended')),
    ('5', mean(u'OMB control number')),
    ('6', tot(u'demographic')),
    ('7', mean(u'510(k)')),
    ('8', tot(u'reasonable assurance of safety')),
    ('9.1', u'round(365*(L("2026")-L("2023"))/L("120"),1)'),
    ('10', tot(u'reasonable assurance of the safety')),
    ('11', u'CNT(%r,0)' % PH(u'machine learning')),
    ('12', mean(u'de novo')),
    ('13', mean(W)),
    ('14', mean(u'class II')),
    ('15', u'CNT(%r,0)' % MUST),
    ('17', u'CNT(%r,1)+CNT(%r,1)' % (PH(u'predetermined change control'), PH(u'pccp'))),
    ('31', tot(MUST)),
    ('36', tot(u'de novo')),
    ('42', tot(u'class II')),
]
assert len(set(k for k, _ in D)) == len(D), u'DERIV 键重复'
BLK = u"DERIV['B40'] = {\n" + u'\n'.join(u" %r: %r," % (k, v) for k, v in D) + u"\n}\n"
if "DERIV['B40']" in s:
    j0 = s.index(u"DERIV['B40']")
    k0 = s.index(u'\n}\n', j0) + 3
    s = s[:j0] + s[k0:]
j = s.index(u"DERIV['B39']")
k = s.index(u'\n}\n', j) + 3
s = s[:k] + BLK + s[k:]

io.open(A, 'w', encoding='utf-8').write(s)

C = 'corpus/atomcheck.py'
c = io.open(C, encoding='utf-8').read()
if "B40" not in c:
    m = re.search(r"^SRC = \{", c, re.M)
    ins = (u"SRC['B40'] = ['corpus/raw/prose/fr_fda_cardio_ml_notification.txt',\n"
           u"             'corpus/raw/prose/fr_fda_radiology_ml_pccp.txt',\n"
           u"             'corpus/raw/prose/fr_fda_opioid_impairment_monitor.txt']\n")
    d = c.index(u'\n}\n', m.start()) + 3
    c = c[:d] + ins + c[d:]
io.open(C, 'w', encoding='utf-8').write(c)
print(u"wired B40: audit SRC/ATOM/DERIV(%d keys, 零值键折 %d 处缺席) + atomcheck SRC" % (len(D), len(ABSENT)))
