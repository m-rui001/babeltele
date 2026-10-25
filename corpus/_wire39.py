# -*- coding: utf-8 -*-
"""幂等接线: 把 B39 注册进 audit.py 的 SRC/ATOM/DERIV 与 atomcheck.py 的 SRC。"""
import io, re

A = 'corpus/audit.py'
s = io.open(A, encoding='utf-8').read()

SRC39 = (u"SRC['B39'] = ['corpus/raw/prose/pmc_mobilization_dose_study.txt',\n"
         u"          'corpus/raw/prose/pmc_mobilization_targettrial_letter.txt']\n")
if "SRC['B39']" not in s:
    i = s.index(u'\nATOM = {')
    s = s[:i + 1] + SRC39 + s[i + 1:]

if u"'B38'}" in s and u"'B39'}" not in s:
    s = s.replace(u"'B38'}", u"'B38', 'B39'}", 1)

ZERO = ('CNT("immortal",0)+CNT("E value",0)+CNT("marginal structural",0)+CNT("g-methods",0)'
        '+CNT("STROBE",0)+CNT("MCID",0)+CNT("minimal clinically",0)+CNT("power",0)'
        '+CNT("hypothesis",0)+CNT("C-statistic",0)+CNT("designated",0)+CNT("AUROC",0)'
        '+CNT("Fine\u2013Gray",0)+CNT("not intended",0)+CNT("guarantee",0)+CNT("1[.]85",0)'
        '+CNT("reimbursement",1)+CNT("minute",1)+CNT("weekend",1)+CNT("2774",1)+CNT("25[.]8",1)'
        '+CNT("overadjust",1)+CNT("directed acyclic",1)+CNT("Post-Barthel",1)+CNT("Pre-Barthel",1)'
        '+CNT("AUC",1)+CNT("has been considered",1)+CNT("First,",1)+CNT("Second,",1)+CNT("Third,",1)'
        '+CNT("survivor",1)+CNT("cerebrovascular",1)+CNT("chronic kidney",1)+CNT("CRRT",1)+CNT("continuous renal",1)'
        '+CNT("2[.]65",1)+CNT("1[.]58",1)+CNT("4[.]46",1)')

D = [
 ('0', ZERO),
 ('2', 'CNT("should be interpreted as a time-varying exposure",0)+CNT("should be interpreted as a time-varying exposure",1)'),
 ('4', 'CNT("Anchoring",1)+CNT("treating ICU death",1)+CNT("conducting adequately powered",1)+CNT("applying formal target-trial",1)'),
 ('5', 'CNT("First,",0)+CNT("Second,",0)+CNT("Third,",0)+CNT("Fourth,",0)+CNT("Finally,",0)'),
 ('10', 'CNT("196",0)'),
 ('392', 'round(L("196")*2)'),
 ('64.3', 'round(L("196")*2/L("610")*100,1)'),
 ('16.6', 'round(L("101")/L("610")*100,1)'),
 ('25.8', 'round(L("101")/(L("196")*2)*100,1)'),
 ('1.59', 'round(L("31.6")/L("19.9"),2)'),
 ('2.03', 'round((L("1.19")*L("3.45"))**0.5,2)'),
 ('5.38', 'round((L("9.14")+L("1.62"))/2,2)'),
 ('1.14', 'round(L("2.32")/L("2.03"),2)'),
 ('1.31', 'round(L("2.65")/L("2.03"),2)'),
 ('2.7', 'round(L("5")/L("1.85"),1)'),
 ('0.02', 'round(L("0.68")-L("0.66"),2)'),
 ('0.03', 'round(L("0.66")-L("0.63"),2)'),
 ('0.1', 'round(L("2")-L("1.9"),1)'),
 ('7', 'round((L("2.2")-L("1.5"))/(L("1.8")-L("1.7")))'),
 ('20', 'round(L("100")/L("5"))'),
 ('40', 'L("2")*L("20")'),
 ('59', 'round(CNT("[0-9]",0)/CNT("[A-Za-z]",0)*1000)'),
 ('87', 'round(CNT("[0-9]",1)/CNT("[A-Za-z]",1)*1000)'),
]
BLK = u"DERIV['B39'] = {\n" + u'\n'.join(u" %r: %r," % (k, v) for k, v in D) + u"\n}\n"
if "DERIV['B39']" in s:
    j0 = s.index(u"DERIV['B39']")
    k0 = s.index(u'\n}\n', j0) + 3
    s = s[:j0] + s[k0:]
j = s.index(u"DERIV['B38']")
k = s.index(u'\n}\n', j) + 3
s = s[:k] + BLK + s[k:]

io.open(A, 'w', encoding='utf-8').write(s)

C = 'corpus/atomcheck.py'
c = io.open(C, encoding='utf-8').read()
if "B39" not in c:
    m = re.search(r"^SRC = \{", c, re.M)
    ins = (u"SRC['B39'] = ['corpus/raw/prose/pmc_mobilization_dose_study.txt',\n"
           u"             'corpus/raw/prose/pmc_mobilization_targettrial_letter.txt']\n")
    d = c.index(u'\n}\n', m.start()) + 3
    c = c[:d] + ins + c[d:]
io.open(C, 'w', encoding='utf-8').write(c)
print('wired B39: audit SRC/ATOM/DERIV + atomcheck SRC')
