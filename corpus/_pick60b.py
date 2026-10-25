# -*- coding: utf-8 -*-
"""B60 现探补遗: 修 _pick60.py 尾部被 heredoc 吃掉的反斜杠(\b 在 str 字面量里是退格符, 不是 \b)。
本遍一律用 raw 字符串, 并把 825/398 的所指、历史表行与正文的强度词、RFC 5280 参考文献段分开现算。"""
import io
import re

D = u'corpus/raw/cert/'
TAGS = (u'T', u'O', u'F', u'N', u'R')
LAYOUT = [D + u'CA-Browser-Forum-BR-1.7.7.layout.txt',
          D + u'CA-Browser-Forum-BR-1.8.7.layout.txt',
          D + u'CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt',
          D + u'le_lifetimes.html',
          D + u'rfc5280.txt']
T = [io.open(p, encoding='utf-8', errors='replace').read() for p in LAYOUT]


def show(name, vals):
    print(u'%-24s %s' % (name, vals))


print(u'--- day 写法两档(连字 ⇎ 空格) ---')
for i in range(5):
    h = len(re.findall(r'\d+-day', T[i]))
    s = len(re.findall(r'\d+ days', T[i]))
    u1 = len(re.findall(r'\d+ day\b', T[i]))
    show(u'day_hyph/sp/sing ' + TAGS[i], (h, s, u1, h + s + u1))

print(u'--- 825 与 398 的所指分解(逐行判从句) ---')
for i in range(3):
    for num in (u'825', u'398', u'397'):
        lines = [l.strip() for l in T[i].split(u'\n') if num + r' day' in l]
        val = len([l for l in lines if r'Velidity Period' in l])
        reuse = len([l for l in lines if r'prior to issuing' in l])
        show(u'%s lines %s' % (TAGS[i], num), (len(lines), val, reuse, len(lines) - val - reuse))

print(u'--- 动词×数字×对象 ---')
PAT = re.compile(r'(MUST NOT|MUST|SHOULD NOT|SHOULD)\s+have a\s+Validity Period\s+greater than\s+(\d+)\s+days')
for i in range(5):
    show(u'ceil-triples ' + TAGS[i], sorted(set(PAT.findall(T[i]))))

print(u'--- 历史时间表行 ⇎ 正文里的强度词 ---')
for i in range(3):
    rows = [l for l in T[i].split(u'\n')
            if re.match(r'\s*\d{4}-\d{2}-\d{2}', l) or re.search(r'\bSC\d', l)]
    hist = u'\n'.join(rows)
    body = u'\n'.join(l for l in T[i].split(u'\n') if l not in rows)
    show(u'hist rows/chars ' + TAGS[i], (len(rows), len(hist)))
    for w in (r'\bMUST\b', r'\bSHALL\b', r'(?i)\bshall\b', r'(?i)\bmust\b'):
        show(u'  %s / %s' % (w, TAGS[i]), (len(re.findall(w, hist)), len(re.findall(w, body))))

print(u'--- RFC 5280: Month YYYY 落在正文还是参考文献段 ---')
m = re.search(r'(?m)^9\.\s+References', T[4])
idx = m.start() if m else -1
MY = r'(?:January|February|March|April|May|June|July|August|September|October|November|December) 2\d{3}'
show(u'R refs idx', idx)
show(u'R month_year refs', len(re.findall(MY, T[4][idx:])))
show(u'R month_year body', len(re.findall(MY, T[4][:idx])))
for w in (r'\bUTCTime\b', r'\bGeneralizedTime\b', r'\b2049\b', r'\b2050\b', r'\bvalidity period\b'):
    show(u'R %s' % w, (len(re.findall(w, T[4][:idx])), len(re.findall(w, T[4][idx:]))))

print(u'--- LE: 四个数各配什么名词 ---')
for mm in re.finditer(r'[^.\n]*(?:90|45|47|6)[ -]day[^.\n]*\.', T[3]):
    show(u'N-life', mm.group(0).strip()[:150])
show(u'N per-day', len(re.findall(r'(?i)per day|renew', T[3])))

print(u'--- 五份里 “day” 这个词的非期限用法 ---')
for i in range(5):
    allw = len(re.findall(r'(?i)\bdays?\b', T[i]))
    num = len(re.findall(r'\d[ -]days?\b', T[i]))
    show(u'day word/numeric ' + TAGS[i], (allw, num, allw - num))
