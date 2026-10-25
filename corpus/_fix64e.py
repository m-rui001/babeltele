# -*- coding: utf-8 -*-
"""B64 两遍对账修口径: 一次落 8 处(建条目侧 5 处 ⇎ 采集侧 3 处)。"""
import io

P = [(u'corpus/_mkB64.py',
      u"    return dict(bytes=len(RAWB[i]), chars=len(TXT[i]), lines=ln, nonblank=nb,",
      u"    return dict(bytes=len(RAWB[i]), chars=len(TXT[i]), lines=len(ls), nonblank=nb,"),
     (u'corpus/_mkB64.py',
      u"        if re.match(u'^\\d+\\.\\d+', s) and len(s) < 60 and cur[1]:",
      u"        if re.match(u'^\\d+\\.\\d+', s) and cur[1]:"),
     (u'corpus/_mkB64.py',
      u"        ca, cb = cell(wa.split(NL)[0] if NL in wa else wa), cell(wb.split(NL)[0])\n"
      u"        nm = ca[0] if ca and ca[0] not in LBL else (u'' if not ca else ca[0])",
      u"        ca, cb = cell(wa.split(NL)[0] if NL in wa else wa), cell(wb.split(NL)[0])\n"
      u"        if ca:\n"
      u"            nm = ca[0]\n"
      u"        else:\n"
      u"            jj = 0\n"
      u"            while jj < len(wa) and not (u'A' <= wa[jj] <= u'Z'):\n"
      u"                jj += 1\n"
      u"            run = u''\n"
      u"            while jj < len(wa) and (u'A' <= wa[jj] <= u'Z' or wa[jj] in DIG or wa[jj] == u'_'):\n"
      u"                run += wa[jj]\n"
      u"                jj += 1\n"
      u"            nm = run if len(run) >= 3 else u''"),
     (u'corpus/_mkB64.py',
      u"F[u'a_seq'] = seq\nF[u'a_seq_n'] = len(seq)",
      u"F[u'a_seq_ms'] = seq\nF[u'a_seq'] = [x // 1000 for x in seq]\nF[u'a_seq_n'] = len(seq)"),
     (u'corpus/_mkB64.py',
      u"u'\u2192'.join([str(x // 1000) for x in F[u'a_seq']])",
      u"u'\u2192'.join([str(x) for x in F[u'a_seq']])"),
     (u'corpus/_pick64.py',
      u"TN = [(u'p50', u'50%'), (u'p875', u'87.5'), (u'p05', u'0.5'), (u'p08', u'0.8'), (u'ld', u'lease duration'),\n"
      u"      (u'spl', u'shortest preferred lifetime'), (u'userval', u'MUST use the'), (u'zerorule', u'are set to 0')]",
      u"TN = [(u'p05', u'0.5'), (u'p08', u'0.8'), (u'ld', u'lease duration'),\n"
      u"      (u'spl', u'shortest preferred lifetime'), (u'userval', u'MUST use the'), (u'zerorule', u'are set to 0')]"),
     (u'corpus/_pick64.py',
      u"SN = [(u'max64full', u'The retransmission delay SHOULD be doubled with\\n   subsequent retransmissions up to a maximum of 64 seconds.'),\n"
      u"      (u'c120', u'values of SOL_MAX_RT and INF_MAX_RT to be 120 seconds.'),\n"
      u"      (u'c3600', u'every 3600 seconds rather than every'),\n"
      u"      (u'clampfull', u'MUST be in this range: 60 <= \"value\" <= 86400'),\n"
      u"      (u'ignorefull', u'MUST ignore any SOL_MAX_RT option values that are less'),\n"
      u"      (u'retainfull', u'this value is expected to be retained for as long as practically possible'),\n"
      u"      (u'samefull', u'The T1/T2 times set in each applicable IA option for a Reply MUST be'),\n"
      u"      (u'discfull', u'If a client receives an IA_NA with T1 greater than T2')]",
      u"SN = [(u'c120', u'values of SOL_MAX_RT and INF_MAX_RT to be 120 seconds.'),\n"
      u"      (u'c3600', u'every 3600 seconds rather than every'),\n"
      u"      (u'clampfull', u'MUST be in this range: 60 <= \"value\" <= 86400'),\n"
      u"      (u'ignorefull', u'MUST ignore any SOL_MAX_RT option values that are less'),\n"
      u"      (u'max64full', u'The retransmission delay SHOULD be doubled with\\n   subsequent retransmissions up to a maximum of 64 seconds.'),\n"
      u"      (u'max64sp', u'The retransmission delay SHOULD be doubled with subsequent retransmissions up to a maximum of 64 seconds.'),\n"
      u"      (u'retainfull', u'this value is expected to be retained for as long as practically possible'),\n"
      u"      (u'samefull', u'The T1/T2 times set in each applicable IA option for a Reply MUST be'),\n"
      u"      (u'discfull', u'If a client receives an IA_NA with T1 greater than T2'),\n"
      u"      (u'reback', u'client MUST adopt a retransmission strategy that incorporates a'),\n"
      u"      (u'ifacefull', u'An updated SOL_MAX_RT value applies only to the network interface')]"),
     (u'corpus/_pick64.py',
      u"u'leasedur': u'lease duration', u'retain': u'retained for as long as practically possible',",
      u"u'leasedur': u'lease duration', u'retain': u'this value is expected to be retained',")]

for p, old, new in P:
    t = io.open(p, encoding='utf-8').read()
    n = t.count(old)
    assert n == 1, (p, n, old[:60])
    io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
    print(u'OK %s <- %s' % (p, old[:52].replace(u'\n', u'\\n')))
