# -*- coding: utf-8 -*-
"""幂等接线: 把 B38 注册进 audit.py 的 SRC/ATOM/DERIV 与 atomcheck.py 的 SRC。"""
import io, re

A = 'corpus/audit.py'
s = io.open(A, encoding='utf-8').read()

SRC38 = (u"SRC['B38'] = ['corpus/raw/prose/pmc_sepsis_lpa_comment.txt',\n"
         u"          'corpus/raw/prose/pmc_sepsis_lpa_response.txt']\n")
if "SRC['B38']" not in s:
    i = s.index(u'\nATOM = {')
    s = s[:i + 1] + SRC38 + s[i + 1:]

if u"'B37'}" in s and u"'B38'}" not in s:
    s = s.replace(u"'B37'}", u"'B37', 'B38'}", 1)

DERIV38 = u"""DERIV['B38'] = {
 '0': 'CNT("ChatGPT",1)+CNT("underpowered",1)+CNT("misclass",1)+CNT("36.9",1)+CNT("2071",1)+CNT("odds ratio",1)+CNT("First,",1)+CNT("Second,",1)+CNT("Third,",1)+CNT("%",1)+CNT("Geri",1)+CNT("we agree",0)+CNT("load-dependent",0)+CNT("PMC10838258",1)+CNT("[\\u4e00-\\u9fff]",0)+CNT("[\\u4e00-\\u9fff]",1)',
 '3': 'CNT("we agree",1)',
 '2': 'CNT("PMC10838258",0)',
 '1': 'CNT("endotype",0)',
 '8': 'CNT("%",0)',
 '1.98': 'round(L("41")/L("2071")*100,2)',
 '1.67': 'round(L("2.37")/L("1.42"),2)',
 '3.19': 'round((L("3427")+L("3151"))/L("2071"),2)',
 '262': 'round(L("17,008")/L("65"))',
 '8710': 'CNT("[A-Za-z]",0)',
 '753': 'CNT("[0-9]",0)',
 '6376': 'CNT("[A-Za-z]",1)',
 '209': 'CNT("[0-9]",1)',
}
"""
if "DERIV['B38']" not in s:
    j = s.index(u"'B37': {'0':")
    k = s.index(u'\n}\n', j) + 3
    s = s[:k] + DERIV38 + s[k:]

io.open(A, 'w', encoding='utf-8').write(s)

C = 'corpus/atomcheck.py'
c = io.open(C, encoding='utf-8').read()
if "B38" not in c:
    m = re.search(r"^SRC = \{", c, re.M)
    ins = (u"SRC['B38'] = ['corpus/raw/prose/pmc_sepsis_lpa_comment.txt',\n"
           u"             'corpus/raw/prose/pmc_sepsis_lpa_response.txt']\n")
    # 在 SRC 字面量结束处追加
    d = c.index(u'\n}\n', m.start()) + 3
    c = c[:d] + ins + c[d:]
io.open(C, 'w', encoding='utf-8').write(c)
print('wired B38: audit SRC/ATOM/DERIV + atomcheck SRC')
