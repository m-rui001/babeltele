# -*- coding: utf-8 -*-
import re, hashlib, io

def norm(s):
    s = re.sub(u'[ \t]+', u' ', s)
    s = re.sub(u'(?<=[\u4e00-\u9fff]) +| +(?=[\u4e00-\u9fff])', u'', s)
    s = re.sub(u'\n{2,}', u'\n', s)
    return s.strip()

HDR = u'''# raw prose / src: https://www.csrc.gov.cn/csrc/c101928/c7658117/content.shtml
# title: 中国证券监督管理委员会行政处罚决定书 〔2026〕39号
# author: 中国证监会（2026-08-18 作出，官方公布）
# chars: %d
# text_sha256: %s
# retrieved: 2026-10-20
# note: 卢润凯编造、传播虚假信息案全文(某APP生成税率调整假文章+无违法所得+部分采纳申辩)。网页正文按段落保留, 站点导航与【打印】尾部已剔除; 汉字逐字未改。
'''

lines = [l.strip() for l in io.open(u'corpus/raw/probe/c7658117.body.txt', encoding='utf-8').read().split(u'\n')]
paras = []
for l in lines:
    if not l or l.startswith(u'【打印】'):
        if l.startswith(u'【打印】'):
            break
        continue
    paras.append(l)
txt = u'\n'.join(norm(p) for p in paras)
h = hashlib.sha256(txt.encode('utf-8')).hexdigest()[:16]
io.open(u'corpus/raw/prose/cn_csrc_fake_info_lurunkai.txt', 'w', encoding='utf-8', newline='\n').write(
    (HDR % (len(txt), h)) + u'\n' + txt + u'\n')
print('chars=', len(txt), 'sha=', h, 'paras=', len(paras))
