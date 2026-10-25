# -*- coding: utf-8 -*-
"""B64 第二遍首刀: 修语法、修假恒等式、把硬填的 60/86400 改成面内现读、联结段改纯 % 档。"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/_mkB64.py'
s = io.open(P, encoding='utf-8').read()

R = []
R.append((u"F[u'nb_gap'] = [F[u'nonblank_asciib'][i] - F[u'nonblank'][i] for i in range(NSRC)]",
          u"F[u'nb_gap'] = [F[u'nonblank_asciib'][i] - F[u'nonblank'][i] for i in range(NSRC)]\n"
          u"F[u'bytes_span'] = max(F[u'bytes']) - min(F[u'bytes'])"))
R.append((u"F[u'lit_durdef875_gap'] = [F[u'lit_durdef875_fold'][i] - F[u'lit_durdef875'][i] for i in range(NSRC)]",
          u"F[u'lit_durdef875_gap'] = [F[u'lit_durdef875_fold'][i] - F[u'lit_durdef875'][i] for i in range(NSRC)]\n"
          u"F[u'lit_durdef875_gap_sum'] = sum(F[u'lit_durdef875_gap'])"))
R.append((u"F[u'tbl_start'] = [[st for st, _ in TB[i]] for i in range(NSRC)]",
          u"F[u'tbl_start'] = [[st for st, _ in TB[i]] for i in range(NSRC)]\n"
          u"F[u'tbl_row_delta'] = (F[u'tbl_rows'][3][0] - F[u'tbl_rows'][1][0]) "
          u"if (F[u'tbl_rows'][1] and F[u'tbl_rows'][3]) else 0"))
R.append((u"F[u'on_cover'] = len([k for k in F[u'bd_unproposed'] if False])",
          u"F[u'on_changed_n'] = len(F[u'on_changed'])\n"
          u"F[u'on_ratio_cap_close'] = (F[u'on_ratio'][0] - F[u'cap_ratio_d_b']) if F[u'on_ratio'] else 1"))
R.append((u"F[u'y_a_next'] = dur_after(TXT[0], u'The delay before the next retransmission SHOULD\\n   be ')[0]\n"
          u"F[u'y_a_next2'] = dur_after(TXT[0], u'The delay before the next retransmission SHOULD be ')[0]",
          u"F[u'y_a_next'] = dur_after(TXT[0], u'The delay before the next retransmission SHOULD')[0]"))
R.append((u"F[u'a_ratio'] = seq[-1] // seq[0] if seq else 0",
          u"F[u'a_ratio'] = seq[-1] // seq[0] if seq else 0\n"
          u"F[u'a_seq_close'] = (seq[-1] - F[u'y_ans_ms'][0]) if seq else 1\n"
          u"F[u'a_seq_next_close'] = (seq[1] - F[u'y_a_next']) if len(seq) > 1 else 1\n"
          u"F[u'a_ratio_pow_close'] = F[u'a_ratio'] - 2 ** F[u'a_doublings']\n"
          u"F[u'a_cap_x_first_close'] = F[u'y_a_first'] * F[u'a_ratio'] - F[u'y_ans_ms'][0]"))
R.append((u"F[u'clamp_span'] = 86400 // 60",
          u""
          u"def num_before(t, needle):\n"
          u"    p = t.find(needle)\n"
          u"    if p < 0:\n"
          u"        return 0\n"
          u"    j = p\n"
          u"    while j and t[j - 1] in WCH:\n"
          u"        j -= 1\n"
          u"    k = j\n"
          u"    while k and t[k - 1] in DIG:\n"
          u"        k -= 1\n"
          u"    return int(t[k:j]) if j > k else 0\n"
          u"\n"
          u"\n"
          u"def num_after(t, needle):\n"
          u"    p = t.find(needle)\n"
          u"    if p < 0:\n"
          u"        return 0\n"
          u"    j = p + len(needle)\n"
          u"    while j < len(t) and t[j] in WCH:\n"
          u"        j += 1\n"
          u"    k = j\n"
          u"    while k < len(t) and t[k] in DIG:\n"
          u"        k += 1\n"
          u"    return int(t[j:k]) if k > j else 0\n"
          u"\n"
          u"\n"
          u"F[u'clamp_lo'] = [num_before(TXT[i], u' <= \"value\" <= ') for i in range(NSRC)]\n"
          u"F[u'clamp_hi'] = [num_after(TXT[i], u' <= \"value\" <= ') for i in range(NSRC)]\n"
          u"F[u'clamp_span'] = max(F[u'clamp_hi']) // max([x for x in F[u'clamp_lo'] if x])\n"
          u"F[u'clamp_span_close'] = F[u'clamp_span'] * max([x for x in F[u'clamp_lo'] if x]) - max(F[u'clamp_hi'])"))
R.append((u"F[u'y_ans_rem'] = F[u'y_ans_max'] - F[u'y_ans_ratio'] * F[u'y_ans_min']",
          u"F[u'y_ans_rem'] = F[u'y_ans_max'] - F[u'y_ans_ratio'] * F[u'y_ans_min']\n"
          u"F[u'y_ans_span_close'] = F[u'y_ans_max'] - F[u'y_ans_ratio'] * F[u'y_ans_min'] - F[u'y_ans_rem']"))
R.append((u"F[u'y_self_lit'] = [occ(TXT[i], n) for i, n in ((0, u'2131'), (1, u'3315'), (2, u'7083'), (3, u'8415'))]",
          u"F[u'y_cite_ledger_3315_sum'] = sum(F[u'y_cite_ledger_3315'])\n"
          u"F[u'y_self_lit'] = [occ(TXT[i], n) for i, n in ((0, u'2131'), (1, u'3315'), (2, u'7083'), (3, u'8415'))]"))
R.append((u"                   + len(m_iset(m_iset(GE40[0], GE40[1]), GE40[3]))\n"
          u"                   + len(m_iset(m_iset(GE40[0], GE40[1]), GE40[2]))",
          u"                   + len(m_iset(m_iset(GE40[0], GE40[1]), GE40[3]))\n"
          u"                   + len(m_iset(m_iset(GE40[0], GE40[2]), GE40[3]))"))
R.append((u"F[u'tbl_rows'][i] or u'—'", u"(F[u'tbl_rows'][i][0] if F[u'tbl_rows'][i] else u'—')"))

for old, new in R:
    n = s.count(old)
    if n != 1:
        print(u'拒绝(出现 %d 次): %s' % (n, old[:120].replace(u'\n', u'\\n')))
        sys.exit(1)
    s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print(u'SCAN 刀已落 %d 处' % len(R))
