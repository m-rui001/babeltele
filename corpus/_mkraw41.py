# -*- coding: utf-8 -*-
# FDA 同一 docket(FDA-2025-N-1243)的拟议令 ⇎ 最终令: ISH 肿瘤伴随诊断试剂 III 类→II 类重新分类
import io, re, hashlib

SRC = {
    u'fr_fda_ish_proposed_order': (
        u'corpus/raw/probe/_f_2025-10549.htm',
        u'2025/06/11', u'2025-10549',
        u'90 FR 24540 (2025-06-11, Proposed Rules) FDA "Hematology and Pathology Devices; '
        u'Reclassification of In Situ Hybridization Test Systems for Use With a Corresponding '
        u'Approved Oncology Therapeutic Product; Request for Comments", 21 CFR 864, '
        u'Docket No. FDA-2025-N-1243, comment period closed 2025-08-11'),
    u'fr_fda_ish_final_order': (
        u'corpus/raw/probe/_f_2026-16727.htm',
        u'2026/08/17', u'2026-16727',
        u'91 FR 53184 (2026-08-17, Rules and Regulations; final amendment; final order) '
        u'FDA same title as the proposed order, 21 CFR 864 (new Sec. 864.1890), '
        u'Docket No. FDA-2025-N-1243, effective 2026-09-16'),
}

for slug, (htm, day, docno, title) in SRC.items():
    t = io.open(htm, encoding='utf-8', errors='replace').read()
    m = re.search(u'<body[^>]*>\\s*<pre>(.*?)</pre>', t, re.S)
    body = m.group(1) if m else t
    body = re.sub(u'<[^>]+>', u'', body)
    body = (body.replace(u'&lt;', u'<').replace(u'&gt;', u'>').replace(u'&amp;', u'&')
                .replace(u'&nbsp;', u' ').replace(u'&#39;', u"'").replace(u'&quot;', u'"'))
    body = body.replace(u'\r\n', u'\n').replace(u'\r', u'\n')
    body = re.sub(u'\n{3,}', u'\n\n', body).strip()
    h = hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]
    out = u'corpus/raw/prose/%s.txt' % slug
    head = (u'# src: federalregister.gov raw text (%s.htm 实为 HTML, <body><pre> 转文本, 标签与实体已剥离)\n'
            u'# url: https://www.federalregister.gov/documents/full_text/text/%s/%s.txt\n'
            u'# title: %s\n# chars: %d\n# text_sha256: %s\n'
            u'# retrieved: 2026-10-20\n'
            u'# note: 保留 [[Page N]] 分页记号与 \\N\\ 脚注标记与 ``...\'\' 式引号; 正文按公报版式硬换行(约 78 列)\n\n'
            % (docno, day, docno, title, len(body), h))
    io.open(out, u'w', encoding='utf-8').write(head + body)
    print(out, len(body), h, u'pages=%d' % len(re.findall(u'\\[\\[Page \\d+\\]\\]', body)))
