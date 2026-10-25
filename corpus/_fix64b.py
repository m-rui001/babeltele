# -*- coding: utf-8 -*-
"""B64 第二遍第二刀: ZID 换真恒等式、正文模板去嵌套引号、联结段改纯 % 档。"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/_mkB64.py'
s = io.open(P, encoding='utf-8').read()


def span(start_marker, end_marker, new, label):
    global s
    i = s.find(start_marker)
    j = s.find(end_marker, i)
    assert i >= 0 and j > i, label
    s = s[:i] + new + s[j:]
    print(u'整段换刀: %s' % label)


ZIDNEW = u"""ZID = [(u"B64V('y_ans_max')-B64V('y_ans_ratio')*B64V('y_ans_min')-B64V('y_ans_rem')",
        u'跨度: 3 600 000=56×64 000+16 000'),
       (u"B64V('y_cd_ans_close')", u'C 的 NEW 行 ⇎ D 的缺省表行同值'),
       (u"B64V('cap_ratio_d_b')*B64V('y_ans_ms', 1)-B64V('y_ans_ms', 3)", u'表间之比×03 值=18 值'),
       (u"B64V('bd_close')", u'B ⇎ D 同名参数: 同+异=总数'),
       (u"B64V('on_ratio_cap_close')", u'C 的 OLD→NEW 比值=D 表对 B 表的比值'),
       (u"B64V('al_close')", u'夹逼句对照三分档穷尽'),
       (u"B64V('a_ratio')-2**B64V('a_doublings')", u'末项/首项=2^(翻倍次数)'),
       (u"B64V('a_seq_close')", u'仿真末项=A 面内现读的封顶 64 秒'),
       (u"B64V('a_seq_next_close')", u'仿真第二项=A 面内现读的下次重传 8 秒'),
       (u"B64V('a_cap_x_first_close')", u'首值×末首比=封顶'),
       (u"B64V('a_seq_n')-B64V('a_doublings')-1", u'序列项数=翻倍次数+1'),
       (u"B64V('nb_ff_sum')", u'两口径非空行之差=换页符独占行数'),
       (u"B64V('ff_foot_sum')", u'换页符总数=页脚行数'),
       (u"B64V('pg_foot_sum')", u'“[Page ” 子串处数=页脚行数'),
       (u"B64V('hdr_ledger_sum')", u'页眉两档之和=页眉总数'),
       (u"B64V('abcd_close')", u'四份长行容斥=并集实数'),
       (u"B64V('pool_close')", u'锚池分层穷尽'),
       (u"B64V('y_cite_ledger_3315_sum')", u'3315 引用两式相加=引用总数(四份)'),
       (u"B64V('bd_unproposed_n')-2", u'D 自改的两枚恰是 C 没提的 REL/DEC'),
       (u"B64V('on_changed_n')-2", u'C 只改动 SOL/INF 两枚'),
       (u"B64V('lit_durdef875_gap', 0)-B64V('lit_durdef875_fold', 0)", u'A 的 T2 式只在折平档命中(原面 0)'),
       (u"B64V('clamp_span_close')", u'夹逼上下界之比×下界=上界'),
       (u"B64V('y_clamp_lit', 2)-B64V('y_clamp_lit', 3)", u'C ⇎ D 的夹逼字面同现枚数'),
       (u"B64V('wrap_sn_total')-B64V('wrapgap_max64full', 0)", u'主线跨行差只落在 A 的那一句上'),
       (u"B64V('y_ignore_srt', 3)+B64V('y_ignore_inf', 3)-B64V('y_must_ignore_n', 3)",
        u'D 的两句丢弃: SOL+INF=MUST ignore any 全数'),
       (u"B64V('tbl_row_delta')-B64V('tbl_rows', 3)+B64V('tbl_rows', 1)", u'D 表比 B 表多出的行数')]
"""
span(u"ZID = [(", u"F[u'x_ident_n']", ZIDNEW, u'ZID')

T = []
T.append((u"{EXPR('max(F[\"bytes\"])-min(F[\"bytes\"])', 'max(F[\"bytes\"])-min(F[\"bytes\"])', '字节极差')}",
          u"{V('bytes_span')}"))
T.append((u"{EXPR(\"F['a_seq'][-1]-F['y_ans_ms'][0]//1000\", 'F[\\'a_seq\\'][-1]-F[\\'y_ans_ms\\'][0]//1000', '序列末项⇎答数')} )",
          u"{CLOS('a_seq_close','仿真末项⇎封顶')}"))
T.append((u"{EXPR('F[\"tbl_rows\"][3][0]-F[\"tbl_rows\"][1][0]', 'F[\"tbl_rows\"][3][0]-F[\"tbl_rows\"][1][0]', '表行增量')}",
          u"{V('tbl_row_delta')}"))
T.append((u"(闭合 {CLOS('y_ans_max','跨度')} )", u"(闭合 {CLOS('y_ans_span_close','跨度')}))"))
T.append((u"含 '60 <= \"value\" <= 86400' 的行 13", u"含夹逼式的行 13"))
T.append((u"(闭合 {CLOS('lit_durdef875_gap','T2 式折行')})",
          u"(逐份差 {JOIN('lit_durdef875_gap')}, 合计 {V('lit_durdef875_gap_sum')})"))
T.append((u"{EXPR('sum(F[\"y_cite_ledger_3315\"])', 'sum(F[\\'y_cite_ledger_3315\\'])', '3315 引用残余')} )",
          u"{V('y_cite_ledger_3315_sum')} )"))
T.append((u"97 的 0xffffffff 用于“无限租约”{A_t1def} 同页", u"97 把它用在“无限租约”那一行"),)
T.append((u"两者闭合 {CLOS('cap_ratio_d_b','提案⇎标准之比')}", u"两者闭合 {CLOS('on_ratio_cap_close','提案⇎标准之比')}"))
for old, new in T:
    n = s.count(old)
    if n != 1:
        print(u'拒绝(出现 %d 次): %s' % (n, old[:100]))
        sys.exit(1)
    s = s.replace(old, new)
print(u'模板刀已落 %d 处' % len(T))

LJNEW = u"""联结 = (u"；联结不是“同一份数据的两种序列化”, 而是“报文发出去没人应答时重传退避封顶多久”在四份一手规范里的四种答法: "
        u"面内现读 97 六十四 %d 秒 ⇎ 03 一百二 %d 秒 ⇎ 13 倍三十 %d 秒 ⇎ 18 可下发 %d 秒"
        u"(单位 %s ⇎ %s ⇎ %s ⇎ %s, 去重 %d 枚, 两端比 %d 倍余 %d); "
        u"97 的 64 秒是翻倍序列的末项: 首值现读 %d 秒, 下次重传 %d 秒, 序列 %s 共 %d 项 ⇎ 翻倍 %d 次 ⇎ 末/首=%d=2^%d, "
        u"它连 SOL_MAX_RT 这个词都只出现 %d 处; 03 把答数钉成参数表里的一行(“120 secs”全文 %d 处, 恰是 SOL ⇎ INF 两行), 客户端无从改变; "
        u"13 用 OLD:/NEW: 把同一行重印成 %d→%d 秒(比值 %d, 改动 %d 枚), 另开出可下发的选项、值域 %d..%d(上下界比 %d); "
        u"18 收下同一枚 %d 秒却另有来历: 与 03 同名的参数 %d 枚里 %d 枚逐字同值 ⇎ %d 枚改动 %s, 其中 %d 枚是 18 自己改的、13 通篇没提; "
        u"可下发不等于照收: 18 的夹逼句与 13 逐行对照 %d 行, 字节全等 %d ⇎ 仅标点差 %d ⇎ 归一也不同 %d(闭合 %d), 字符净差 %+d; "
        u"“越界即弃”句 18 %d 处 ⇎ 13 %d 处, 而覆盖的存活期与接口作用域只有 18 写(%d⇎%d 处); "
        u"次轴“多久去续租”: 97 用 T1=0.5×duration_of_lease ⇎ T2=0.875×(同一标识符全篇 %d 处), 其 T2 式被排版劈在两行(原面 %d ⇎ 折平 %d); "
        u"v6 三份改用 shortest preferred lifetime 作基准(%d⇎%d⇎%d 处)并把 T1/T2 交给服务器下发; "
        u"整行搬运: 03⇎18 归一 %d 行(逐字节 %d ⇎ 仅归一同 %d) ⇎ 13⇎18 归一 %d 行(逐字节 %d)——提案的复写在句内不在整行; "
        u"版式: 四份全靠换页符分页(%d⇎%d⇎%d⇎%d 页), 非空行两口径差 %d⇎%d⇎%d⇎%d 行恰为换页符独占行。\\n") % (
    F[u'y_ans_s'][0], F[u'y_ans_s'][1], F[u'y_ans_s'][2], F[u'y_ans_s'][3],
    F[u'y_ans_unit'][0], F[u'y_ans_unit'][1], F[u'y_ans_unit'][2], F[u'y_ans_unit'][3],
    F[u'y_ans_distinct'], F[u'y_ans_ratio'], F[u'y_ans_rem'],
    F[u'y_a_first'] // 1000, F[u'y_a_next'] // 1000, u'→'.join([str(x // 1000) for x in F[u'a_seq']]),
    F[u'a_seq_n'], F[u'a_doublings'], F[u'a_ratio'], F[u'a_doublings'], F[u'lit_solmaxrt'][0],
    F[u'lit_s120'][1],
    F[u'on_pair_c'][0][1], F[u'on_pair_c'][0][2], F[u'on_ratio'][0], F[u'on_changed_n'],
    F[u'clamp_lo'][2], F[u'clamp_hi'][2], F[u'clamp_span'],
    F[u'y_ans_s'][3], F[u'bd_n'], F[u'bd_same'], len(F[u'bd_diff']),
    u' ⇎ '.join([u'%s %d→%d' % (x[0], x[1], x[2]) for x in F[u'bd_diff']]), F[u'bd_unproposed_n'],
    F[u'al_n'], F[u'al_same_bytes'], F[u'al_punct_only'], F[u'al_norm_diff'], F[u'al_close'],
    F[u'al_char_delta'],
    F[u'y_ignore_srt'][3], F[u'y_ignore_srt'][2], F[u'lit_retain'][3], F[u'lit_iface'][3],
    F[u'lit_durword'][0], F[u'lit_durdef875'][0], F[u'lit_durdef875_fold'][0],
    F[u'lit_preferre'][1], F[u'lit_preferre'][2], F[u'lit_preferre'][3],
    F[u'share_bd'], F[u'y_bd_byte_shared'], F[u'y_bd_norm_only'],
    F[u'share_cd'], F[u'y_cd_byte_shared'],
    F[u'pages_est'][0], F[u'pages_est'][1], F[u'pages_est'][2], F[u'pages_est'][3],
    F[u'nb_gap'][0], F[u'nb_gap'][1], F[u'nb_gap'][2], F[u'nb_gap'][3])
"""
span(u"联结 = (", u"title = (", LJNEW, u'联结')
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
try:
    compile(s, P, 'exec')
    print(u'syntax OK')
except SyntaxError as e:
    print(u'SyntaxError line %s: %s' % (e.lineno, e.msg))
