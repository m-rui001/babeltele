# -*- coding: utf-8 -*-
# 2026-10-19 CFTC 同日两份: 2026-21376 过渡期最终规则(排除) ⇎ 2026-21377 拟议规则(纳入)
import io, re, hashlib

SRC = {
    u'corpus/raw/prose/cftc_swap_exclusion_ifr.txt': (
        u'corpus/raw/probe/fr_2026-21376.htm',
        u'https://www.govinfo.gov/content/pkg/FR-2026-10-19/html/2026-21376.htm',
        u'91 FR 66010 (2026-10-19, Interim final rule; request for comments) '
        u'CFTC "Further Definition of \u201cSwap\u201d To Exclude Casino-Style Gambling Products", RIN 2026-21376'),
    u'corpus/raw/prose/cftc_swap_inclusions_nprm.txt': (
        u'corpus/raw/probe/fr_2026-21377.htm',
        u'https://www.govinfo.gov/content/pkg/FR-2026-10-19/html/2026-21377.htm',
        u'91 FR 66022 (2026-10-19, Notice of proposed rulemaking) '
        u'CFTC "Further Definition of \u201cSwap\u201d\u2014Inclusions", RIN 2026-21377'),
}

for out, (htm, url, title) in SRC.items():
    t = io.open(htm, encoding='utf-8', errors='replace').read()
    m = re.search(u'<body[^>]*>\\s*<pre>(.*?)</pre>', t, re.S)
    body = m.group(1) if m else t
    body = re.sub(u'<[^>]+>', u'', body)
    body = (body.replace(u'&lt;', u'<').replace(u'&gt;', u'>').replace(u'&amp;', u'&')
                .replace(u'&nbsp;', u' ').replace(u'&#39;', u"'").replace(u'&quot;', u'"'))
    body = body.replace(u'\r\n', u'\n').replace(u'\r', u'\n')
    body = re.sub(u'\n{3,}', u'\n\n', body).strip()
    h = hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]
    head = (u'# src: govinfo FR-2026-10-19 (HTML <pre> 转文本, 标签与实体已剥离, 页眉页脚保留原样)\n'
            u'# url: %s\n# title: %s\n# chars: %d\n# text_sha256: %s\n'
            u'# retrieved: 2026-10-20\n# note: 同日两份, 同一术语 swap 的两个方向——排除走即时生效的临时最终规则, 纳入只发征求意见稿\n\n'
            % (url, title, len(body), h))
    io.open(out, 'w', encoding='utf-8').write(head + body)
    print(out, len(body), h)
