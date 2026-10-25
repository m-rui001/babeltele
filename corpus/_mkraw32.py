# -*- coding: utf-8 -*-
import re, hashlib, io

def norm(s):
    s = s.replace(u'　', u' ')
    s = re.sub(u'[ \\t]+', u' ', s)
    # pass1: drop ascii space adjacent to Han
    s = re.sub(u'(?<=[\u4e00-\u9fff]) +| +(?=[\u4e00-\u9fff])', u'', s)
    # pass2: drop newline whose neighbours are Han
    s = re.sub(u'(?<=[\u4e00-\u9fff，。、；：）】”])[ \t]*\n[ \t]*(?=[\u4e00-\u9fff“（])', u'', s)
    s = re.sub(u'\n{2,}', u'\n', s)
    return s.strip()

def body(path, stop):
    lines = io.open(path, encoding='utf-8').read().split(u'\n')
    out = []
    for l in lines:
        l = l.strip()
        if not l:
            continue
        if l.startswith(stop):
            break
        out.append(l)
    return out

HDR = u'''# raw prose / src: %s
# title: 中国证券监督管理委员会行政处罚决定书 %s
# author: 中国证监会（%s，官方公布）
# chars: %d
# text_sha256: %s
# retrieved: 2026-10-20
# note: %s
'''

def emit(dst, url, wh, date, note, paras, join):
    if join:
        txt = norm(u'\n'.join(paras))
    else:
        txt = u'\n'.join(norm(p) for p in paras)
    h = hashlib.sha256(txt.encode('utf-8')).hexdigest()[:16]
    head = HDR % (url, wh, date, len(txt), h, note)
    io.open(dst, 'w', encoding='utf-8', newline='\n').write(head + u'\n' + txt + u'\n')
    print(dst, 'chars=', len(txt), 'sha=', h)

A = body(u'corpus/raw/probe/c7646037.body.txt', u'【打印】')
emit(u'corpus/raw/prose/cn_csrc_manipulation_fourmen.txt',
     u'https://www.csrc.gov.cn/csrc/c101928/c7646037/content.shtml',
     u'〔2026〕25号', u'2026-06-24 作出',
     u'赵杨、全寿山、王立华、班学钦四人操纵案全文(资金方与操作方分工+共同故意推定+4:1责任切分)。网页正文按段落保留, 站点导航与【打印】尾部已剔除; 汉字逐字未改。',
     A, False)

B = body(u'corpus/raw/probe/c7619967.body.txt', u'【打印】')
emit(u'corpus/raw/prose/cn_csrc_manipulation_tenmen.txt',
     u'https://www.csrc.gov.cn/csrc/c101928/c7619967/content.shtml',
     u'〔2024〕140号', u'2024-12-06 作出',
     u'谢文轩等10人操纵“飞力达”等11只股票案全文(5组/27账户+逐股盈亏列举+盈亏不互抵口径+申辩四条与复核四条)。网页正文按段落保留, 站点导航与【打印】尾部已剔除; 汉字逐字未改。',
     B, False)
