# -*- coding: utf-8 -*-
"""B64 第二遍第三刀: 保留句 needle 换成面内整行档、加单空格档跨行针、⛓段照实重写。"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/_mkB64.py'
s = io.open(P, encoding='utf-8').read()

R = []
R.append((u"F[u'lit_retain'] = [occ(TXT[i], u'retained for as long as practically possible') for i in range(NSRC)]",
          u"F[u'lit_retain'] = [occ(TXT[i], u'this value is expected to be retained') for i in range(NSRC)]\n"
          u"F[u'lit_retain_sp'] = [occ(TXT[i], u'retained for as long as practically possible') for i in range(NSRC)]"))
R.append((u"G[u'D_retain'] = AT(u'own', u'D', u'retained for as long as practically possible')",
          u"G[u'D_retain'] = AT(u'own', u'D', u'this value is expected to be retained')"))
R.append((u"      (u'retainfull', u'this value is expected to be retained for as long as practically possible'),",
          u"      (u'max64sp', u'The retransmission delay SHOULD be doubled with ' + NL.join([u'', u'   ']) + u'subsequent retransmissions up to a maximum of 64 seconds.'),\n"
          u"      (u'retainfull', u'this value is expected to be retained for as long as practically possible'),"))
for old, new in R:
    if s.count(old) != 1:
        print(u'拒绝(出现 %d 次): %s' % (s.count(old), old[:110]))
        sys.exit(1)
    s = s.replace(old, new)

# 单空格针: face 用整句单空格, fold 同串——写成面内两行拼接的反向档
s = s.replace(u"      (u'max64sp', u'The retransmission delay SHOULD be doubled with ' + NL.join([u'', u'   ']) + u'subsequent retransmissions up to a maximum of 64 seconds.'),\n",
              u"      (u'max64sp', u'The retransmission delay SHOULD be doubled with subsequent retransmissions up to a maximum of 64 seconds.'),\n")

i = s.find(u'折行通道: 本遍')
j = s.find(u'页眉是隐形通道')
assert 0 < i < j
NEW = (u'折行通道: 本遍 {V(\'wrap_sn_n\')} 枚主线针里 {V(\'wrap_sn_hit\')} 枚有差, 逐档合计 {V(\'wrap_sn_total\')} 处'
       u'——97 的封顶句被排版从 “doubled with” 处劈到下一行: 把换行照抄进 needle 才命中 {V(\'s_max64full\',0)} 处, '
       u'按单空格搜整句则原面 {V(\'s_max64sp\',0)} 处 ⇎ 折平 {V(\'s_max64sp_fold\',0)} 处; '
       u'18 的保留句同样劈行(原面 {V(\'s_retainfull\',3)} ⇎ 折平 {V(\'s_retainfull_fold\',3)}), '
       u'而 13 的 OLD:/NEW: 行、03 的表行、18 的夹逼⇎丢弃句都整行连着写。'
       u'次轴 {V(\'wrap_pin_n\')} 枚针里 {V(\'wrap_pin_hit\')} 枚有差, 合计 {V(\'wrap_total\')} 处: '
       u'97 的 T2 缺省式 “0.875 * duration_of_lease” 把乘数留在上一行、基准词挪到下一行'
       u'(原面 {V(\'lit_durdef875\',0)} 处 ⇎ 折平 {V(\'lit_durdef875_fold\',0)} 处, 逐份差 {JOIN(\'lit_durdef875_gap\')}, '
       u'合计 {V(\'lit_durdef875_gap_sum\')}), 按行搜该字面的复算者读不到它。"')
s = s[:i] + NEW + s[j:]

old = u"(u\"B64V('wrap_sn_total')-B64V('wrapgap_max64full', 0)\", u'主线跨行差只落在 A 的那一句上'),"
new = (u"(u\"B64V('wrap_sn_total')-B64V('wrapgap_max64sp', 0)-B64V('wrapgap_retainfull', 3)\",\n"
       u"        u'主线跨行差只在 A 的封顶句 ⇎ D 的保留句'),")
if s.count(old) != 1:
    print(u'拒绝: %s' % old[:100])
    sys.exit(1)
s = s.replace(old, new)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
try:
    compile(s, P, 'exec')
    print(u'第三刀已落 ｜ syntax OK')
except SyntaxError as e:
    print(u'SyntaxError line %s: %s' % (e.lineno, e.msg))
