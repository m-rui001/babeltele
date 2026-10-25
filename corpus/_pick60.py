# -*- coding: utf-8 -*-
"""B60 现探: 五份源对“一张公签 TLS 服务器证书能活多久”的各答法。
源: 三代 CA/B BR(pdftotext 两口径) ⇎ Let's Encrypt 生命周期说明 ⇎ RFC 5280。
本遍只测量、不设门槛; 键名与口径留给 _mkB60.py。"""
import io
import json
import os
import re

D = u'corpus/raw/cert/'
TAGS = (u'T', u'O', u'F', u'N', u'R')
LAYOUT = [D + u'CA-Browser-Forum-BR-1.7.7.layout.txt',
          D + u'CA-Browser-Forum-BR-1.8.7.layout.txt',
          D + u'CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt',
          D + u'le_lifetimes.html',
          D + u'rfc5280.txt']
RAWPDF = [D + u'CA-Browser-Forum-BR-1.7.7.raw.txt',
          D + u'CA-Browser-Forum-BR-1.8.7.raw.txt',
          D + u'CA-Browser-Forum-TLS-BRs-v2.0.2.raw.txt']
PDFS = [D + u'CA-Browser-Forum-BR-1.7.7.pdf',
        D + u'CA-Browser-Forum-BR-1.8.7.pdf',
        D + u'CA-Browser-Forum-TLS-BRs-v2.0.2.pdf']


def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


T = [rd(p) for p in LAYOUT]
RW = [rd(p) for p in RAWPDF]
LOW = [t.lower() for t in T]


REC = {}


def show(name, vals):
    REC.setdefault(name, []).append(vals)
    print(u'%-22s %s' % (name, vals))


print(u'--- 字节/字符/行 ---')
for i, p in enumerate(LAYOUT):
    show(u'bytes ' + TAGS[i], os.path.getsize(p))
show(u'bytes pdf', [os.path.getsize(p) for p in PDFS])
show(u'chars', [len(x) for x in T])
show(u'chars no-nl', [len(x.replace(u'\n', u'')) for x in T])
show(u'lines', [len(x.split(u'\n')) for x in T])
show(u'nonblank', [len([l for l in x.split(u'\n') if l.strip()]) for x in T])
show(u'formfeed', [x.count(u'\x0c') for x in T])
show(u'formfeed_raw', [x.count(u'\x0c') for x in RW])
show(u'layout_minus_raw', [len(T[i]) - len(RW[i]) for i in range(3)])
show(u'maxlen', [max(len(l) for l in x.split(u'\n')) for x in T])
show(u'trailing_ws_lines', [len([l for l in x.split(u'\n') if l != l.rstrip()]) for x in T])

print(u'--- 天数字族 ---')
MDAY = re.compile(u'(\\d[\\d,]*)[ \\t]*(?:-|\\s)[ \\t]*(?:days?|day)\\b')
for i in range(5):
    ms = [m.group(1).replace(u',', u'') for m in MDAY.finditer(T[i])]
    show(u'day_hits ' + TAGS[i], len(ms))
    show(u'day_set ' + TAGS[i], sorted(set(ms), key=int))
show(u'dayword_any', [len(re.findall(u'(?i)\\bday[s]?\\b', x)) for x in T])

print(u'--- 关键数字逐份出现处 ---')
for n in (u'825', u'398', u'397', u'47', u'45', u'90', u'365', u'13', u'37', u'39', u'820'):
    show(n, [T[i].count(n + u' day') + T[i].count(n + u'-day') for i in range(5)])
for n in (u'825', u'398', u'397', u'47', u'45', u'90', u'365'):
    show(n + u'_bare', [T[i].count(n) for i in range(5)])

print(u'--- 术语叫法 ---')
for w in (u'Validity Period', u'validity period', u'Validity', u'lifetime', u'Lifetime',
          u'notBefore', u'notAfter', u'validity'):
    show(w, [T[i].count(w) for i in range(5)])
show(u'ValidityPeriod_camel', [T[i].count(u'Validity Period') + T[i].count(u'validity period') for i in range(5)])
show(u'lifetime_ci', [len(re.findall(u'(?i)lifetime', x)) for x in T])

print(u'--- 强度词 ---')
for w in (u'MUST', u'MUST NOT', u'SHOULD', u'SHOULD NOT', u'MAY', u'MUST24'):
    if w == u'MUST24':
        continue
    show(w, [T[i].count(w) for i in range(5)])
show(u'must_ci', [len(re.findall(u'(?i)\\bmust\\b', x)) for x in T])
show(u'must_lower', [len(re.findall(u'\\bmust\\b', T[i])) for i in range(5)])
show(u'will_ci', [len(re.findall(u'(?i)\\bwill\\b', x)) for x in T])
show(u'shall_ci', [len(re.findall(u'(?i)\\bshall\\b', x)) for x in T])

print(u'--- 时间语法(RFC 5280 的世纪窗口) ---')
for w in (u'UTCTime', u'GeneralizedTime', u'2049', u'2050', u'2000', u'1950', u'YYMMDD', u'YYYYMMDD'):
    show(w, [T[i].count(w) for i in range(5)])
for m in re.finditer(u'[^.\n]*UTCTime[^.\n]*\.', T[4]):
    show(u'R-utc', m.group(0).strip()[:150])

print(u'--- 日期写法族 ---')
show(u'iso_date', [len(re.findall(u'\\b\\d{4}-\\d{2}-\\d{2}\\b', x)) for x in T])
show(u'us_date', [len(re.findall(u'\\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \\d{1,2}, \\d{4}', x)) for x in T])
show(u'month_year', [len(re.findall(u'\\b(?:January|February|March|April|May|June|July|August|September|October|November|December) 2\\d{3}\\b', x)) for x in T])
show(u'yyyy', [len(re.findall(u'\\b20[1-3]\\d\\b', x)) for x in T])
for i in (0, 1, 2, 3, 4):
    show(u'dates ' + TAGS[i], sorted(set(re.findall(u'\\b20[1-3]\\d(?:-\\d{2})?(?:-\\d{2})?\\b', T[i])))[:14])

print(u'--- 条款引用体例 ---')
show(u'section_cap', [len(re.findall(u'\\bSection \\d', x)) for x in T])
show(u'section_low', [len(re.findall(u'\\bsection \\d', x)) for x in T])
show(u'sec_num_head', [len(re.findall(u'(?m)^\\s*((?:\\d+\\.){1,3}\\d+)\\s', x)) for x in T])
show(u'head_distinct', [len(set(re.findall(u'(?m)^\\s*((?:\\d+\\.){1,3}\\d+)\\s', x))) for x in T])
show(u'rfc_cite', [len(re.findall(u'\\b\\d{4}\\b', x)) for x in T])
for i in range(5):
    show(u'rfc_refs ' + TAGS[i], sorted(set(re.findall(u'\\bRFC\\s?(\\d{4})\\b', T[i])))[:20])

print(u'--- 自我标注 ---')
show(u'version_self', [re.findall(u'(?i)version\\s+\\d+\\.\\d+(?:\\.\\d+)?', T[i])[:3] for i in range(5)])
show(u'baseline_reqs', [T[i].count(u'Baseline Requirements') for i in range(5)])
show(u'tls_brs', [T[i].count(u'TLS BRs') + T[i].count(u'TLS Baseline Requirements') for i in range(5)])
show(u'last_updated', [len(re.findall(u'(?i)last updated', x)) for x in T])
show(u'status_approved', [len(re.findall(u'(?i)status:\\s*approved', x)) for x in T])
show(u'effective', [len(re.findall(u'(?i)effective date|this document', x)) for i, x in enumerate(T)])

print(u'--- 历史时间表行(layout 口径) ---')
show(u'daterow', [len(re.findall(u'(?m)^\\s*\\d{4}-\\d{2}-\\d{2}\\b', x)) for x in T])
show(u'daterow_raw', [len(re.findall(u'(?m)^\\s*\\d{4}-\\d{2}-\\d{2}\\b', x)) for x in RW])
show(u'bullet', [len(re.findall(u'(?m)^\\s*[o\\-*•]\\s', x)) for x in T])

print(u'--- 398/825 语句现场 ---')
for i in range(3):
    for m in re.finditer(u'[^.\n]*(?:398|825|397) days?[^.\n]*\\.', T[i]):
        show(u'%s-life' % TAGS[i], m.group(0).strip()[:170])

print(u'--- HTML 侧(LE)壳与实体 ---')
le = rd(LAYOUT[3])
show(u'le_script_blocks', len(re.findall(u'(?is)<script\\b.*?</script>', le)))
show(u'le_style_blocks', len(re.findall(u'(?is)<style\\b.*?</style>', le)))
show(u'le_lt_tags', len(re.findall(u'<[^>]+>', le)))
show(u'le_amp_ent', len(re.findall(u'&[a-z]+;|&#[0-9]+;', le)))
show(u'le_links', len(re.findall(u'href=', le)))

print(u'--- 跨版本整行搬运(layout) ---')


def pn(s):
    return u''.join(c for c in s.lower() if c.isalnum())


L = [set(pn(l) for l in x.split(u'\n') if len(l.strip()) >= 25 and pn(l)) for x in T]
for a in range(5):
    show(u'lines_ge25 ' + TAGS[a], len(L[a]))
for a, b in ((0, 1), (1, 2), (0, 2), (0, 3), (2, 3), (2, 4), (0, 4), (3, 4)):
    show(u'share %s%s' % (TAGS[a], TAGS[b]), len(L[a] & L[b]))
show(u'share_TOF', len(L[0] & L[1] & L[2]))
show(u'union_TOF', len(L[0] | L[1] | L[2]))
show(u'only_T', len(L[0] - L[1] - L[2]))
show(u'only_F', len(L[2] - L[0] - L[1]))

print(u'--- 锚池候选: 含天数的长行 ---')
for i in range(5):
    cands = [l.strip() for l in T[i].split(u'\n')
             if len(l.strip()) >= 60 and re.search(u'(398|825|397|47|45|90|6)[- ]?day', l)]
    show(u'lifetime-lines ' + TAGS[i], len(cands))
    for c in cands[:3]:
        show(u'  >', c[:190])

print(u'--- 对账表(采集侧): 只收两份口径一致的键 ----')
# 网页那一份两边量的层不同(采集侧读壳, 建条目侧读去壳面), 所以逐份清单只取四份纯文本面 (T,O,F,R)。
PLAIN = (0, 1, 2, 4)


def pl(name):
    if name + u' T' in REC:
        return [REC[name + u' ' + TAGS[i]][-1] for i in PLAIN]
    return [REC[name][-1][i] for i in PLAIN]


def pa(a, b):
    return REC[u'share %s%s' % (TAGS[a], TAGS[b])][-1]


G = {
    u'bytes': pl(u'bytes'), u'chars': pl(u'chars'), u'lines': pl(u'lines'),
    u'nonblank': pl(u'nonblank'), u'formfeed': pl(u'formfeed'), u'maxlen': pl(u'maxlen'),
    u'trail': pl(u'trailing_ws_lines'), u'day_word': pl(u'dayword_any'),
    u'vp_caps': pl(u'Validity Period'), u'vp_low': pl(u'validity period'),
    u'notbefore': pl(u'notBefore'), u'notafter': pl(u'notAfter'), u'lifetime_ci': pl(u'lifetime_ci'),
    u'u_must': pl(u'MUST'), u'u_must_not': pl(u'MUST NOT'), u'u_should': pl(u'SHOULD'),
    u'u_should_not': pl(u'SHOULD NOT'), u'u_may': pl(u'MAY'),
    u'must_ci': pl(u'must_ci'), u'must_l': pl(u'must_lower'), u'will_ci': pl(u'will_ci'),
    u'shall_ci': pl(u'shall_ci'), u'iso_date': pl(u'iso_date'), u'us_date': pl(u'us_date'),
    u'month_year': pl(u'month_year'), u'yyyy_any': pl(u'yyyy'),
    u'sec_cite': pl(u'section_cap'), u'sec_cite_low': pl(u'section_low'),
    u'sec_head': pl(u'sec_num_head'), u'sec_head_d': pl(u'head_distinct'),
    u'baseline_reqs': pl(u'baseline_reqs'), u'last_updated': pl(u'last_updated'),
    u'lines_ge25': pl(u'lines_ge25'),
    u'share_TO': pa(0, 1), u'share_OF': pa(1, 2), u'share_TF': pa(0, 2),
    u'share_TN': pa(0, 3), u'share_FN': pa(2, 3), u'share_TR': pa(0, 4),
    u'share_FR': pa(2, 4), u'share_NR': pa(3, 4),
    u'share_TOF': REC[u'share_TOF'][-1], u'union_TOF': REC[u'union_TOF'][-1],
    u'only_T': REC[u'only_T'][-1], u'only_F': REC[u'only_F'][-1],
    u'pdf_bytes': REC[u'bytes pdf'][-1], u'face_gap': REC[u'layout_minus_raw'][-1],
    u'raw_formfeed': REC[u'formfeed_raw'][-1],
    u'le_scripts': REC[u'le_script_blocks'][-1], u'le_styles': REC[u'le_style_blocks'][-1],
    u'le_tags': REC[u'le_lt_tags'][-1], u'le_ents': REC[u'le_amp_ent'][-1],
    u'le_hrefs': REC[u'le_links'][-1],
}
G[u'_plain_idx'] = list(PLAIN)
json.dump(G, io.open(u'corpus/_b60meas.json', u'w', encoding=u'utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
print(u'已写 corpus/_b60meas.json ｜ 键 %d' % (len(G) - 1))
