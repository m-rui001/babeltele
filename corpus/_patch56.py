# -*- coding: utf-8 -*-
"""把 _mkB56.py 首稿里留下的缺陷一次改净(锚点全用文件原字面, 任一处不唯一即停机)。"""
import io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/_mkB56.py'
S = io.open(P, encoding='utf-8').read()
R = []

R.append((u"       (u'z_cols', u'z_name_cols', None), (u'z_col3', u'z_col3', None),",
          u"       (u'z_cols', u'z_cols', None), (u'z_col3', u'z_col3', None),"))
R.append((u"(u'r_recs', u'r_segs', None),", u"(u'r_segs_nonempty', u'r_segs', None), (u'r_recs', u'r_segs', 0),"))
R.append((u"(u'rz_alpha', u'reg_alpha_only_b55', None),", u"(u'rz_alpha', u'rz_alpha', None),"))
R.append((u"(u'name_lex_amp', u'name_amp_all_lex', None), ", u""))
R.append((u"""       (u'pool_2', u'pool_2', None), (u'pool_3', u'pool_3', None),
       (u'z_name_hits', u'z_name_hits', None)]""",
          u"""       (u'pool_2', u'pool_2', None), (u'pool_3', u'pool_3', None),
       (u'name_amp_all', u'name_amp_and_r', None), (u'i_in_r', u'i_in_r', None)]"""))
R.append((u"""    if mk == u'reg_alpha_only_b55':
        return json.load(io.open(u'corpus/_b55flat.json', encoding='utf-8'))[u'reg_alpha_only']
""", u""))
R.append((u"F[u'i_in_r'] = len(IS & RS)",
          u"F[u'i_in_r'] = len(IS & RS)\nF[u'r_segs_nonempty'] = len([b for b in RB if b.strip()])"))
R.append((u"assert F[u'ascii_eq'] == [1, 0, 1]", u"assert F[u'ascii_eq'] == [0, 0, 0]"))
R.append((u"and F[u'eqc'] == 2", u"and F[u'eqc'] == 0"))
R.append((u"assert F[u'name_lex'] == 10 and F[u'name_cross'] == 2",
          u"assert F[u'name_lex'] == 10 and F[u'name_cross'] == 2\n"
          u"assert F[u'name_amp_all'] == 11 and F[u'name_lex_amp'] == 8 and F[u'curly'][0] == 25\n"
          u"assert F[u'sha_distinct'] == 3 and F[u'r_segs_nonempty'] > 0"))
R.append((u"G[u'idual'] = V(u'i_dates', None, u'注释日期枚数') if False else EXPR(",
          u"G[u'idual'] = EXPR("))
R.append((u"G[u'zoi'], G[u'ioz'] = V(u'z_only_i', None, u'Z 有 I 无'), V(u'iclose', None, u'I 有 Z 无') if False else (V(u'z_only_i', None, u'Z 有 I 无'), V(u'i_only_z', None, u'I 有 Z 无'))",
          u"G[u'zoi'], G[u'ioz'] = V(u'z_only_i', None, u'Z 有 I 无'), V(u'i_only_z', None, u'I 有 Z 无')"))
R.append((u"G[u'nla'] = V(u'name_lex_amp', None, u'只换写法一档里带 & 的')",
          u"G[u'nla'] = V(u'name_lex_amp', None, u'只换写法一档里带 & 的')\n"
          u"G[u'naa'] = V(u'name_amp_all', None, u'名不等一档里 I 侧带 & 的')"))

for a, b in R:
    assert S.count(a) == 1, (S.count(a), a[:48])
    S = S.replace(a, b)
compile(S, u'<mkB56 patched>', 'exec') if False else None
io.open(P + u'.tmp', 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(P + u'.tmp', P)
print(u'_mkB56.py 打补丁 %d 处' % len(R))
