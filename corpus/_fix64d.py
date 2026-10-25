# -*- coding: utf-8 -*-
"""B64 第二遍第四刀: dur_near/dur_tagged 两把跨行读数档、C 的答数取 NEW 行、表格档认竖线壳、正文两处键名纠偏。"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/_mkB64.py'
s = io.open(P, encoding='utf-8').read()

R = []
R.append((u"ANSN = {u'A': u'up to a maximum of ', u'B': u'SOL_MAX_RT      ', u'C': u'SOL_MAX_RT     ',\n"
          u"        u'D': u'| SOL_MAX_RT      | '}\nANS = [dur_after(TXT[i], ANSN[TAGS[i]]) for i in range(NSRC)]",
          u"ANSN = {u'A': u'up to a maximum of ', u'B': u'SOL_MAX_RT      ',\n"
          u"        u'D': u'| SOL_MAX_RT      | '}\n"
          u"ANS = [dur_after(TXT[i], ANSN[TAGS[i]]) for i in range(NSRC)]\n"
          u"ANS[2] = dur_tagged(TXT[2], u'NEW:', u'SOL_MAX_RT')"))
R.append((u"F[u'y_a_first'] = dur_after(TXT[0], u'the delay before the first retransmission SHOULD be ')[0]\n"
          u"F[u'y_a_next'] = dur_after(TXT[0], u'The delay before the next retransmission SHOULD')[0]",
          u"F[u'y_a_first'] = dur_near(TXT[0], u'the delay before the first retransmission SHOULD')[0]\n"
          u"F[u'y_a_next'] = dur_near(TXT[0], u'The delay before the next retransmission SHOULD')[0]\n"
          u"F[u'y_a_first_wrap'] = dur_near(TXT[0], u'the delay before the first retransmission SHOULD')[3]\n"
          u"F[u'y_a_next_wrap'] = dur_near(TXT[0], u'The delay before the next retransmission SHOULD')[3]"))
R.append((u"F[u'y_clamp_lit'] = [occ(TXT[i], u'60 <= \"value\" <= 86400') for i in range(NSRC)]",
          u"F[u'y_clamp_lit'] = [occ(TXT[i], u'60 <= \"value\" <= 86400') for i in range(NSRC)]\n"
          u"F[u'clamp_cd_lo_close'] = F[u'clamp_lo'][2] - F[u'clamp_lo'][3]\n"
          u"F[u'clamp_cd_hi_close'] = F[u'clamp_hi'][2] - F[u'clamp_hi'][3]"))
R.append((u"        if s.startswith(u'Parameter') and u'Default' in s:",
          u"        if (u'Parameter' in s and u'Default' in s and len(s) < 96):"))
R.append((u"        nm, v = g[0], g[1]",
          u"        nm = g[0]\n"
          u"        q = 0\n"
          u"        while q < len(g[1]) and g[1][q] in WCH:\n"
          u"            q += 1\n"
          u"        dig = u''\n"
          u"        while q < len(g[1]) and (g[1][q] in DIG or g[1][q] == u','):\n"
          u"            dig += g[1][q]\n"
          u"            q += 1\n"
          u"        v = dig"))
R.append((u"{JOIN('s120')}", u"{JOIN('lit_s120')}"))
R.append((u"       (u\"B64V('y_ignore_srt', 3)+B64V('y_ignore_inf', 3)-B64V('y_must_ignore_n', 3)\",\n"
          u"        u'D \u7684\u4e24\u53e5\u4e22\u5f03: SOL+INF=MUST ignore any \u5168\u6570'),",
          u"       (u\"B64V('clamp_cd_lo_close')\", u'\u5939\u8feb\u4e0b\u754c C\u21ceD \u540c\u503c'),\n"
          u"       (u\"B64V('clamp_cd_hi_close')\", u'\u5939\u8feb\u4e0a\u754c C\u21ceD \u540c\u503c'),"))
for old, new in R:
    if s.count(old) != 1:
        print(u'\u62d2\u7edd(\u51fa\u73b0 %d \u6b21): %s' % (s.count(old), old[:110].replace(u'\n', u'\\n')))
        sys.exit(1)
    s = s.replace(old, new)

HELPERS = (u"def dur_near(t, needle, span=64):\n"
           u"    \"\"\"needle \u547d\u4e2d\u540e\u5728 span \u4e2a\u5b57\u7b26\u5185\u8bfb\u7b2c\u4e00\u679a\u201c\u6570\u5b57+\u5355\u4f4d\u201d, \u8de8\u8fc7\u88ab\u6392\u5230\u4e0b\u4e00\u884c\u7684\u52a8\u8bcd\u4e0e\u7a7a\u767d\u3002\"\"\"\n"
           u"    p = t.find(needle)\n"
           u"    if p < 0:\n"
           u"        return (0, u'', u'', 0)\n"
           u"    w = t[p + len(needle):p + len(needle) + span]\n"
           u"    q = 0\n"
           u"    while q < len(w) and w[q] not in DIG:\n"
           u"        q += 1\n"
           u"    if q >= len(w):\n"
           u"        return (0, u'', u'', 0)\n"
           u"    return dur_after(w[q:], u'')\n"
           u"\n"
           u"\n"
           u"def dur_tagged(t, tag, word, span=96):\n"
           u"    \"\"\"\u4ece\u6bcf\u4e00\u5904 tag \u51fa\u53d1, \u5728 span \u4e2a\u5b57\u7b26\u5185\u627e word, \u627e\u5230\u5c31\u8bfb\u5b83\u540e\u9762\u7684\u7b2c\u4e00\u679a\u6570\u5b57+\u5355\u4f4d\u3002\"\"\"\n"
           u"    k = t.find(tag)\n"
           u"    while k >= 0:\n"
           u"        seg = t[k + len(tag):k + len(tag) + span]\n"
           u"        if word in seg:\n"
           u"            return dur_near(seg, word)\n"
           u"        k = t.find(tag, k + 1)\n"
           u"    return (0, u'', u'', 0)\n"
           u"\n"
           u"\n")
anchor = u"ANSN = {u'A': u'up to a maximum of '"
assert s.count(anchor) == 1
s = s.replace(anchor, HELPERS + anchor)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
try:
    compile(s, P, 'exec')
    print(u'\u7b2c\u56db\u5200\u5df2\u843d %d \u5904 \uff5c syntax OK' % len(R))
except SyntaxError as e:
    print(u'SyntaxError line %s: %s' % (e.lineno, e.msg))
