# -*- coding: utf-8 -*-
# 2026 年 FDA 三份 De Novo 分类令(同一法律文书, 三种器械): ML 通知软件 ⇎ ML 定量影像软件(带预定变更控制计划) ⇎ 阿片类氧合损害监测仪
import io, re, hashlib

SRC = {
    u'fr_fda_cardio_ml_notification': (
        u'corpus/raw/probe/_f_2026-18612.htm',
        u'FR-2026-09-11', u'2026-18612',
        u'91 FR 57785 (2026-09-11, Rules and Regulations; final amendment; final order) '
        u'FDA "Medical Devices; Cardiovascular Devices; Classification of the Cardiovascular Machine '
        u'Learning-Based Notification Software", 21 CFR 870, Docket FDA-2026-N-9907'),
    u'fr_fda_radiology_ml_pccp': (
        u'corpus/raw/probe/_f_2026-12166.htm',
        u'FR-2026-06-17', u'2026-12166',
        u'91 FR 36522 (2026-06-17, Rules and Regulations; final amendment; final order) '
        u'FDA "Medical Devices; Radiology Devices; Classification of the Radiological Machine '
        u'Learning-Based Quantitative Imaging Software With Predetermined Change Control Plan", '
        u'21 CFR 892, Docket FDA-2026-N-6535'),
    u'fr_fda_opioid_impairment_monitor': (
        u'corpus/raw/probe/_f_2026-13140.htm',
        u'FR-2026-06-30', u'2026-13140',
        u'91 FR 39459 (2026-06-30, Rules and Regulations; final amendment; final order) '
        u'FDA "Medical Devices; Anesthesiology Devices; Classification of the Monitor for Opioid '
        u'Induced Impairment of Oxygenation", 21 CFR 868, Docket FDA-2026-N-6707'),
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
    head = (u'# src: govinfo %s (HTML <pre> 转文本, 标签与实体已剥离, 页眉页脚保留原样)\n'
            u'# url: https://www.govinfo.gov/content/pkg/%s/html/%s.htm\n'
            u'# title: %s\n# chars: %d\n# text_sha256: %s\n'
            u'# retrieved: 2026-10-20\n'
            u'# note: FDA De Novo 分类令三份之一; 三份同为 "Final amendment; final order"、同卷(91 FR)、均为 class II 特殊控制, 相隔 6 周\n\n'
            % (day, day, docno, title, len(body), h))
    io.open(out, 'w', encoding='utf-8').write(head + body)
    print(out, len(body), h)
