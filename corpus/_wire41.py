# -*- coding: utf-8 -*-
"""幂等接线: 把 B41 注册进 audit.py 的 SRC/ATOM/DERIV 与 atomcheck.py 的 SRC。"""
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')

A = 'corpus/audit.py'
s = io.open(A, encoding='utf-8').read()

SRC41 = (u"SRC['B41'] = ['corpus/raw/prose/fr_fda_ish_proposed_order.txt',\n"
         u"          'corpus/raw/prose/fr_fda_ish_final_order.txt']\n")
if "SRC['B41']" not in s:
    i = s.index(u'\nATOM = {')
    s = s[:i + 1] + SRC41 + s[i + 1:]

if u"'B40'}" in s and u"'B41'}" not in s:
    s = s.replace(u"'B40'}", u"'B40', 'B41'}", 1)


def PH(p):
    """audit 的 CNT 跑在未规范化原文上, 公报正文有硬换行 ⇒ 词组里的空格换成 \\s+。"""
    if p.startswith(u'(?') or u'\\' in p:
        return p
    return u'\\s+'.join(re.escape(w) for w in p.split(u' '))


# 0 键: 折叠全部“该词形在这份文件里根本不出现”的断言
ABSENT_PHRASES = [
    (u'must be included', 0), (u'analytical sensitivity from studies', 0),
    (u'surrogate', 0), (u'AI/ML', 0), (u'machine learning', 0), (u'artificial intelligence', 0),
    (u'digital pathology', 0), (u'(?<![a-z])algorithms(?![a-z])', 0), (u'device-specific', 0),
    (u'the Agency, or we', 0), (u'(?<![a-z])our(?![a-z])', 0), (u'renumber', 0),
    (u'must obtain', 0), (u'object to', 0), (u'not support', 0), (u'(?<![a-z])oppose(?![a-z])', 0),
    (u'(Comment 13)', 0), (u'fewer than 5', 0), (u'One comment', 0),
    (u'All commenters provided support', 0), (u'section IV', 0), (u'FDA agrees', 0),
    (u'FDA disagrees', 0), (u'FDA declines', 0), (u'we decline', 0), (u'section V of the final', 0),
    (u'photostability', 1), (u'post-hybridization', 1), (u'[verbar]', 1), (u'Dated:', 1),
    (u'must be provided', 1), (u'analytical sensitivity provided from', 1),
    (u'@', 0), (u'@', 1),
]
ABSENT = [(PH(p), i) for p, i in ABSENT_PHRASES]
assert len(ABSENT) == 34, len(ABSENT)
ZERO = '+'.join(u'CNT(%r,%d)' % (p, i) for p, i in ABSENT)

TAIL = PH(u'stability based on the intended use specimen type(s) of the device, as applicable')
CMT = PH(u'(?i)\\(Comment \\d+\\)') if False else u'\\(Comment\\s+\\d+\\)'
RSP = u'\\(Response\\s+\\d+\\)'
SV = u'section\\s+V(?!\\s*[IVX])'
OUR = PH(u'(?<![a-z])our(?![a-z])')

D = [
    ('0', ZERO),
    ('1', u'CNT(%r,1)' % PH(u'[s]pecification')),
    ('2', u'CNT(%r,0)+CNT(%r,1)' % (TAIL, TAIL)),
    ('3', u'CNT(%r,1)+CNT(%r,1)' % (PH(u'must be included'), PH(u'analytical sensitivity from studies'))),
    ('4', u'CNT(%r,1)' % OUR),
    ('6', u'CNT(%r,1)+CNT(%r,1)+CNT(%r,1)' % (PH(u'AI/ML'), PH(u'machine learning'), PH(u'artificial intelligence'))),
    ('8', u'L("53191")-L("53184")+1'),
    ('9', u'CNT(%r,0)' % SV),
    ('10', u'CNT(%r,0)+CNT(%r,1)' % (SV, SV)),
    ('12', u'CNT(%r,1)' % PH(u'One comment')),
    ('13', u'CNT(%r,1)' % CMT),
    ('14', u'round((L("2026")-L("2025"))*12+(L("8")-L("6")),0)'),
    ('18', u'(L("53191")-L("53184")+1)+(L("24549")-L("24540")+1)'),
    ('22', u'CNT(%r,0)' % PH(u'Agency')),
    ('26', u'CNT(%r,1)+CNT(%r,1)' % (CMT, RSP)),
    ('36', u'CNT(%r,1)' % PH(u'Agency')),
    ('44', u'CNT(%r,0)+CNT(%r,1)' % (PH(u'510(k)'), PH(u'510(k)'))),
    ('2.6', u'round(CNT(%r,1)/L("5"),1)' % CMT),
]
assert len(set(k for k, _ in D)) == len(D), u'DERIV 键重复'
BLK = u"DERIV['B41'] = {\n" + u'\n'.join(u" %r: %r," % (k, v) for k, v in D) + u"\n}\n"
if "DERIV['B41']" in s:
    j0 = s.index(u"DERIV['B41']")
    k0 = s.index(u'\n}\n', j0) + 3
    s = s[:j0] + s[k0:]
j = s.index(u"DERIV['B40']")
k = s.index(u'\n}\n', j) + 3
s = s[:k] + BLK + s[k:]
io.open(A, 'w', encoding='utf-8').write(s)

C = 'corpus/atomcheck.py'
c = io.open(C, encoding='utf-8').read()
if u"'B41'" not in c:
    m = re.search(r"^SRC = \{", c, re.M)
    ins = (u"SRC['B41'] = ['corpus/raw/prose/fr_fda_ish_proposed_order.txt',\n"
           u"             'corpus/raw/prose/fr_fda_ish_final_order.txt']\n")
    d = c.index(u'\n}\n', m.start()) + 3
    c = c[:d] + ins + c[d:]
    io.open(C, 'w', encoding='utf-8').write(c)
print(u"wired B41: audit SRC/ATOM/DERIV(%d keys, 零值键折 %d 处缺席) + atomcheck SRC" % (len(D), len(ABSENT)))
