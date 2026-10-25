# -*- coding: utf-8 -*-
# 由 pymupdf 抽取文本生成 B33 的三份 raw(剥页眉页脚与页码, 段落不合并以免破坏连续性)
import io
import hashlib
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

JOBS = [
    (u'clairton_final.txt', u'corpus/raw/prose/csb_clairton_final.txt',
     u'https://www.csb.gov/assets/1/20/us_steel_clairton_investigation_report_publication_copy_(1).pdf',
     u'CSB Investigation Report No. 2025-03-I-PA（2026-08 公布, 86 页）: U.S. Steel Clairton Coke Works 焦炉煤气爆炸（事故日期 2025-08-11）最终调查报告',
     u'PDF 文本层抽取; 逐页页眉"Investigation Report"/"CSB Public Record"/页码已按整行精确匹配删除, 正文行序不变'),
    (u'clairton_interim.txt', u'corpus/raw/prose/csb_clairton_interim.txt',
     u'https://www.csb.gov/assets/1/6/us_steel_interim_recommendations_publication.pdf',
     u'CSB Interim Recommendations No. 2025-03-I-PA（2025-12 公布, 12 页）: 同一事故的临时建议, 主题为 Facility Siting',
     u'PDF 文本层抽取; 页眉"Interim Recommendations"/"CSB Public Record"/页码整行删除'),
    (u'clairton_update.txt', u'corpus/raw/prose/csb_clairton_update.txt',
     u'https://www.csb.gov/assets/1/6/us_steel_investigation_update.pdf',
     u'CSB Investigation Update No. 2025-03-I-PA（2025-09 公布, 10 页）: 事故后一个月的调查进展与初步陈述',
     u'PDF 文本层抽取; 页眉"Investigation Update"/"CSB Public Record"/页码整行删除'),
]

DROP = {u'Investigation Report', u'Investigation Report '.strip(), u'CSB Public Record',
        u'Interim Recommendations', u'Investigation Update', u'CSB Public Record ',
        u'U.S. Chemical Safety and', u'Hazard Investigation Board',
        u'U.S. Chemical Safety and Hazard Investigation Board'}


def clean(t):
    out = []
    for ln in t.split(u'\n'):
        s = ln.strip()
        if s in DROP or re.match(u'^\\d{1,3}$', s) or s == u'':
            continue
        out.append(s)
    return u'\n'.join(out)


for src_txt, dst, url, title, note in JOBS:
    t = clean(io.open(u'corpus/raw/probe/' + src_txt, encoding=u'utf-8').read())
    sha = hashlib.sha256(t.encode(u'utf-8')).hexdigest()[:16]
    hdr = (u'# raw prose / src: %s\n# title: %s\n# chars: %d\n# text_sha256: %s\n'
           u'# retrieved: 2026-10-20\n# note: %s\n\n') % (url, title, len(t), sha, note)
    io.open(dst, u'w', encoding=u'utf-8').write(hdr + t + u'\n')
    print(dst, len(t))
