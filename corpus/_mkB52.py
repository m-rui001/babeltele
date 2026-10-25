# -*- coding: utf-8 -*-
"""B52 建条目: 一张会过期的分区表 ⇎ 检查它的 awk ⇎ 生成它真值输入的 Makefile ⇎ 它的姊妹表。
锚全部由 _pick52.py 从四个源按行规则切出并存进 _b52meas.json, 本脚本只按特征子串取用(不手抄);
每个数字都现算并登记成 audit.py 里 B52V 的复算式, 零值一律折进 '0' 键。
“从现在起一致”不可由在库文件判定: 本脚本把这句话如实写进判词, 只把它的成因(真值输入在库 0 份、依赖墙钟)登记成可复算的数。"""
import io, os, re, sys, json

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = u'corpus'
ENTRY = u'%s/babeltele/B52_perishable_table_vs_its_checker.md' % C
NL = u'\n'
J = json.load(io.open(os.path.join(ROOT, C, u'_b52meas.json'), encoding='utf-8'))
M = dict(J[u'meas'])
TAGS = J[u'tags']
LB = dict(zip(TAGS, [u'时效表', u'姊妹表', u'检查器', u'构建器']))
PATH = J[u'paths']
POOL = J[u'pool']
RD = lambda p: io.open(os.path.join(ROOT, p), encoding='utf-8').read()
FULL = [RD(p) for p in PATH]


def pnorm(s):
    """与 audit.py 的 prose_norm 同一套折叠, 所以这里判定的命中列在门槛里可复算。"""
    s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
    s = re.sub(u'[’\'"\u2018\u2019`´]+', u'', s)
    s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff\-\. ]+', u' ', s)
    return re.sub(r'\s+', u' ', s).strip()


FN = [pnorm(t) for t in FULL]


def hitset(a):
    n = pnorm(a)
    return tuple(i for i in range(4) if n and n in FN[i])


def cls_of(h):
    return u'all4' if len(h) == 4 else (u'single' if len(h) == 1 else u'cross')


S, GR, SH3, OCC, HIT = M[u'stat'], M[u'grain'], M[u'sh3'], M[u'occ'], M[u'hit']
F = {}
for k in (u'bytes', u'chars', u'nonempty', u'com', u'dat', u'tabline', u'nonascii'):
    F[k] = [S[t][k] for t in TAGS]
F.update({
    u'nsrc': 4,
    u'fldn4': M[u'fld'][u'N'][u'4'], u'fldz3': M[u'fld'][u'Z'][u'3'], u'fldz4': M[u'fld'][u'Z'][u'4'],
    u'fldt3': M[u'fld'][u'T'][u'3'], u'fldt4': M[u'fld'][u'T'][u'4'],
    u'tags': M[u'grp'], u'rows': M[u'rows'], u'grpmax': max(int(x) for x in M[u'grp_sizes']),
    u'inv': M[u'inv'], u'zinv': M[u'zinv'], u'k2inv': M[u'k2inv'], u'k3pairs': M[u'k3pairs'],
    u'k3inv': M[u'k3inv'], u'offfirst': int(M[u'off_first']), u'offlast': int(M[u'off_last']),
    u'offkinds': M[u'off_kinds'], u'repeated': M[u'off_repeat'], u'maxperoff': M[u'max_per_off'],
    u'offpairkinds': M[u'off_pair_kinds'], u'dstg': M[u'dst_groups'], u'abg': M[u'ab_groups'],
    u'duptag': M[u'dup_tag'], u'barehash': M[u'bare_hash'], u'othercom': M[u'other_com'],
    u'withpar': M[u'with_par'], u'withfirst': M[u'with_first'], u'eqfirst': M[u'eq_first'],
    u'eqlast': M[u'eq_last'], u'inany': M[u'in_any'], u'gaps': len(M[u'gap_list']),
    u'gapspace': M[u'gap_space'], u'gapnopar': M[u'gap_nopar'], u'gaptense': M[u'gap_tense'],
    u'reverse': M[u'reverse_gap'], u'nparen': M[u'nparen'], u'twopar': M[u'two_par'],
    u'expire': len(M[u'expire']), u'nonint': M[u'nonint'], u'minutes': len(M[u'minutes']),
    u'rowoffany': M[u'row_off_any'], u'rowoffcmt': M[u'row_off_cmt'], u'rowoffzone': M[u'row_off_zone'],
    u'cw11': M[u'coord_w'][u'11'], u'cw15': M[u'coord_w'][u'15'],
    u'lead0': M[u'lead0'], u'lead0c': M[u'lead0c'], u'mixed': M[u'mixed'],
    u'c4semi': M[u'c4_semi'], u'c4par': M[u'c4_par'], u'c4both': M[u'c4_both'], u'c4_kind': M[u'c4_kind'],
    u'iso': M[u'iso'], u'isoc': M[u'iso_c'], u'isod': M[u'iso_d'], u'dateskinds': len(M[u'dates']),
    u'untillines': M[u'until'], u'gapday': M[u'gap_day'], u'gapbir': M[u'gap_bir'],
    u'pred': M[u'pred'], u'pred70': M[u'pred70'], u'nowph': M[u'nowph'], u'col1kind': M[u'col1_kind'],
    u'zmulti': M[u'z_multi'], u'zkind': M[u'z_kind'], u'z4empty': M[u'z4_empty'],
    u'z4kind': M[u'z4_kind'], u'z4has': M[u'z4_has'], u'c4eq': M[u'c4_eq'], u'coordeq': M[u'coord_eq'],
    u'cceq': M[u'cc_eq'], u'shared': M[u'n_shared'], u'only70': M[u'only70'], u'onlytab': M[u'onlytab'],
    u'dupn': M[u'dupn'], u'dup70': M[u'dup70'], u'trows': M[u'fld'][u'T'][u'3'] + M[u'fld'][u'T'][u'4'],
    u'nowrows': S[u'N'][u'dat'], u'zrows': S[u'Z'][u'dat'],
    u'grainline': GR[u'line'], u'graincoord': GR[u'coord'], u'grainzone': GR[u'zone'],
    u'grainc4': GR[u'c4'], u'grainshang': GR[u'shang'],
    u'shn': M[u'sh_n'], u'shz': M[u'sh_z'], u'sht': M[u'sh_t'], u'shnt': GR[u'shang_nt'],
    u'shself': GR[u'shang_self'], u'sh3n': SH3[u'n_c3'], u'sh3c': SH3[u'c_c3'], u'sh3nc': SH3[u'nc3'],
    u'sh2nc': SH3[u'nc2'], u'sh3zc': SH3[u'zc3'],
    u'klines': M[u'k_lines'], u'kcom': M[u'k_com'],
    u'kref0': M[u'k_frefc'][u'0'], u'kref1': M[u'k_frefc'][u'1'], u'kref2': M[u'k_frefc'][u'2'],
    u'kref3': M[u'k_frefc'][u'3'], u'kref4': M[u'k_frefc'][u'4'],
    u'kfsline': M[u'k_fsline'], u'kgtline': M[u'k_gtline'], u'kprintf': M[u'k_printf'],
    u'kprintfk': M[u'k_printf_kinds'], u'kstatus': M[u'k_status'], u'kexit': M[u'k_exit'],
    u'kskip': M[u'k_skip'], u'kzdumpnow': M[u'k_zdumpnow'], u'kzonedata': M[u'k_zone_data'],
    u'kzonenowd': M[u'k_zonenowd'], u'kident': M[u'k_ident'], u'knodata': M[u'k_nodata'],
    u'kext': len(M[u'k_ext']), u'kunset': len(M[u'k_unset']),
    u'mprereq': M[u'm_prereq'], u'mprereqok': M[u'm_prereq_ok'], u'mprereqmiss': len(M[u'm_prereq_missing']),
    u'mck': M[u'm_ck'], u'mrm': M[u'm_rm'], u'mmkdir': M[u'm_mkdir'], u'mzic': M[u'm_zic'],
    u'myears': M[u'm_years'], u'msecs': M[u'm_secs'], u'msecs365': M[u'm_secs365'],
    u'mdiff': M[u'm_secs'] - M[u'm_secs365'], u'mbig': M[u'm_big_years'], u'mratio': M[u'm_ratio'],
    u'mfinds': M[u'm_finds'], u'mzdfiles': M[u'm_zdump_files'], u'mckfiles': M[u'm_ck_files'],
    u'mmvout': M[u'm_mvout'], u'mdollarnow': M[u'm_dollarnow'], u'mnontab': M[u'm_nontab'],
    u'mawkcall': M[u'm_awkcall'], u'mtablearg': M[u'm_tablearg'], u'msysv': M[u'm_sysv'],
    u'mhorizons': len(M[u'm_horizon']), u'cknow_m': OCC[u'checknow.awk'][3],
    u'predyear': int(re.search(u'agreed since (\\d{4})', FULL[1]).group(1)),
    u'bdyear': int(re.search(u'# From Paul Eggert \\((\\d{4})', FULL[0]).group(1)),
})
STEP = dict((float(k), v) for k, v in M[u'step'].items())
F[u'step1'] = STEP[1.0]
F[u'stepneg1'] = STEP[-1.0]
F[u'step05'] = STEP[0.5]
F[u'step2'] = STEP[2.0]
IDX = {u'n': 0, u'z': 1, u'k': 2, u'm': 3}
for nm, tok in ((u'xx_n', u'XX'), (u'xx_m', u'XX'), (u'zdumpnow_m', u'zdump-now.tab'),
                (u'zdumptable_k', u'zdump_table'), (u'zdumptable_m', u'zdump_table'),
                (u'nowon_n', u'from now on'), (u'nowon_k', u'from now on'),
                (u'y1970_n', u'1970'), (u'y1970_m', u'1970'), (u'until_n', u'until'),
                (u'irr_n', u'irrelevant'), (u'selfname_z', u'zone1970.tab'),
                (u'selfname_n', u'zone1970.tab'), (u'selfname_m', u'zone1970.tab'),
                (u'ntab_k', u'zonenow.tab'), (u'ntab_m', u'zonenow.tab')):
    F[nm] = OCC[tok][IDX[nm[-1]]]
F[u'hitcross'] = sum(1 for t in HIT.values() if len(t) > 1)
F[u'hitsingle'] = sum(1 for t in HIT.values() if len(t) == 1)
F[u'hitnone'] = sum(1 for t in HIT.values() if t == u'—')
F[u'hitkinds'] = len(HIT)
assert F[u'trows'] == 418 and F[u'step1'] == 30 and F[u'xx_n'] == 92, (F[u'trows'], F[u'step1'], F[u'xx_n'])

K, ZERO, COLL = {}, [], []


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K and K[s][0] != expr:
        COLL.append((s, note))
    K.setdefault(s, (expr, note))


def V(name, i=None, note=u''):
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"B52V('%s'%s)" % (name, u'' if i is None else u', %d' % i), note or name)
    return s


USEDATOM = []
TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


def ATOMSEL(kind, tag, *needles):
    got = [x for x in POOL if x[0] == kind and x[1] == tag and all(n in x[2] for n in needles)]
    assert got, (kind, tag, needles)
    return max(got, key=lambda x: len(x[2]))


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    USEDATOM.append(x[2])
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


def RAWAT(tag, s):
    assert pnorm(s) in FN[TAGS.index(tag)], s
    USEDATOM.append(s)
    return u'⟦%s⟧⟨%s⟩' % (tag, s)


def JOIN(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LB[t])) for i, t in enumerate(TAGS))


G = {}
for nm in (u'fldn4', u'fldz3', u'fldz4', u'fldt3', u'fldt4', u'tags', u'rows', u'grpmax', u'inv', u'zinv',
           u'k2inv', u'k3pairs', u'k3inv', u'offfirst', u'offlast', u'offkinds', u'repeated', u'maxperoff',
           u'offpairkinds', u'dstg', u'abg', u'duptag', u'barehash', u'othercom', u'withpar', u'withfirst',
           u'eqfirst', u'eqlast', u'inany', u'gaps', u'gapspace', u'gapnopar', u'gaptense',
           u'reverse', u'nparen', u'twopar', u'expire',
           u'step1', u'stepneg1', u'step05', u'step2', u'nonint', u'minutes', u'rowoffany', u'rowoffcmt',
           u'rowoffzone', u'cw11', u'cw15', u'lead0', u'lead0c', u'mixed', u'c4semi', u'c4par', u'c4both',
           u'c4_kind', u'iso', u'isoc', u'isod', u'dateskinds', u'untillines', u'gapday', u'gapbir',
           u'pred', u'pred70', u'nowph', u'col1kind', u'zmulti', u'zkind', u'z4empty', u'z4kind', u'z4has',
           u'c4eq', u'coordeq', u'cceq', u'shared', u'only70', u'onlytab', u'dupn', u'dup70', u'trows',
           u'nowrows', u'zrows', u'grainline', u'graincoord', u'grainzone', u'grainc4', u'grainshang',
           u'shn', u'shz', u'sht', u'shnt', u'shself', u'sh3n', u'sh3c', u'sh3nc', u'sh2nc', u'sh3zc',
           u'klines', u'kcom', u'kref0', u'kref1', u'kref2', u'kref3', u'kref4', u'kfsline', u'kgtline',
           u'kprintf', u'kprintfk', u'kstatus', u'kexit', u'kskip', u'kzdumpnow', u'kzonedata',
           u'kzonenowd', u'kident', u'knodata', u'kext', u'kunset', u'mprereq', u'mprereqok',
           u'mprereqmiss', u'mck', u'mrm', u'mmkdir', u'mzic', u'myears', u'msecs', u'msecs365', u'mdiff',
           u'mbig', u'mratio', u'mfinds', u'mzdfiles', u'mckfiles', u'mmvout', u'mdollarnow', u'mnontab',
           u'mawkcall', u'mtablearg', u'msysv', u'mhorizons', u'cknow_m', u'predyear', u'bdyear',
           u'hitcross', u'hitsingle', u'hitnone', u'hitkinds',
           u'xx_n', u'xx_m', u'zdumpnow_m', u'zdumptable_k', u'zdumptable_m', u'nowon_n', u'nowon_k',
           u'y1970_n', u'y1970_m', u'until_n', u'irr_n', u'selfname_z', u'selfname_n', u'selfname_m',
           u'ntab_k', u'ntab_m'):
    G[nm] = V(nm)
G[u'c4kind'] = G[u'c4_kind']
G[u'nsrc'] = V(u'nsrc', None, u'源数')
G[u'nb'] = JOIN(u'bytes', u'磁盘字节')
G[u'nc'] = JOIN(u'chars', u'字符数')
G[u'ne'] = JOIN(u'nonempty', u'非空行')
G[u'no'] = JOIN(u'com', u'注释行')
G[u'nd'] = JOIN(u'dat', u'数据行')
G[u'nt'] = JOIN(u'tabline', u'含制表符行')
G[u'na'] = JOIN(u'nonascii', u'非 ASCII 字符')
G[u'nat'] = TOK(u'anchor_total', u'正文引用锚位')
G[u'ndist'] = TOK(u'anchor_distinct', u'去重锚串')
G[u'nsgl'] = TOK(u'anchor_single', u'只命中一份源的锚')
G[u'ncross'] = TOK(u'anchor_cross', u'命中多份源的锚')
G[u'nall'] = TOK(u'anchor_all4', u'四源皆命中的锚')
G[u'aerr'] = TOK(u'anchor_err', u'锚归属错配数')
G[u'checked'] = TOK(u'checks', u'成员检查次数')

LINES = []


def LINE(em, tmpl, **kw):
    LINES.append((em + u' ' + tmpl).format(**kw))


LINE(u'🧭', u"体例 {aHead} ‖ {aPredN} ‖ {aPredZ} ⇒ 四份材料是同一套时区分区的三个层次加它的姊妹表: "
        u"字节 {nb}, 字符 {nc}, 非空行 {ne}, 其中注释行 {no} ⇎ 数据行 {nd}(顺序始终是时效表⇎姊妹表⇎检查器⇎构建器)。"
        u"四份都算“文本”, 但只有表有字段数这件事: 时效表 {fldn4}/91 行齐四列(连列头那行一起数, 含制表符的是 {ntn} 行), "
        u"姊妹表 {fldz3} 行只有三列 ⇎ {fldz4} 行四列, 第三份姊妹表 {fldt3} ⇎ {fldt4}。"
        u"检查器 {klines} 行里只有 {kcom} 行是注释, 构建器的注释行比时效表的数据行还多——注释层最厚的那份最不像表。"
        u"谓词只写在表的注释里: 时效表有 {pred} 句现在时(含 now 的行共 {nowph} 行), 姊妹表只有 {pred70} 句过去时。"
        u"这条的箭头不是文体对照, 而是“同一套分区在两时态下的两份产物”加“判它们的那段程序”与“调用那段程序的那份配方”。",
     aHead=AT(u'header_rule', u'N', u'experimental'),
     aPredN=AT(u'predicate', u'N', u'predicted to agree'),
     aPredZ=AT(u'pred_z', u'Z', u'agreed since'),
     ntn=str(F[u'tabline'][0]), **G)

LINE(u'🧱', u"排序键住在检查器跳过的那一层 {aTag} ‖ {aColhdr} ‖ {aSkip} ⇒ 时效表的 91 行由 {tags} 行组标签分组, "
        u"标签与数据行严格 1:1 交错(组内行数只有 {grpmax} 这一种取值), 沿标签读下去偏移从 {offfirst} 单调升到 {offlast}(逆序 {inv} 对), "
        u"偏移只有 {offkinds} 种却有 {tags} 组, 同一偏移最多被拆成 {maxperoff} 组, 加上夏令时另一端共 {offpairkinds} 种偏移对。"
        u"可是这个把整张表撑起来的偏移值, 在 91 行数据的任何一列里出现 {rowoffany} 次(注释列 {rowoffcmt} ⇎ 时区名列 {rowoffzone}): 它只活在注释层。"
        u"而检查器给这一层的待遇是 {kskip} 枚“非注释才处理”的谓词, 整层跳过; 它对数据行做的事从 {aSkip} 起笔: "
        u"整行引用 {kref0} 处 ⇎ 第三列 {kref3} 处, 第一/二/四列各被引用 {kref1}/{kref2}/{kref4} 次。"
        u"于是表自述的第一列 {aIrr} 被反向证实: 时效表第一列只有 {col1kind} 种取值(共 {xx_n} 处占位码, 含列头那枚), 姊妹表同一列有 {zkind} 种、其中 {zmulti} 行是多码; "
        u"两表共有的 {shared} 个时区里坐标一致 {coordeq} 个 ⇎ 国码一致 {cceq} 个。判词: 把表组织起来的那个量, 恰好是校表程序按定义不去读的那个量。",
     aTag=AT(u'tag_head', u'N', u'-08/-07 - PST/PDT'),
     aColhdr=AT(u'colhdr', u'N', u'coordinates'),
     aSkip=AT(u'awk_rule', u'K', u'zone = $3'),
     aIrr=AT(u'header_rule', u'N', u'irrelevant'), **G)

LINE(u'⏳', u"一张把自己写在有效期内的表 {aUntil} ‖ {aBday} ⇒ 整份文件的 ISO 日期共 {iso} 处, 全在注释层(注释 {isoc} ⇎ 数据 {isod}), 只有 {dateskinds} 个取值; "
        u"其中 {untillines} 行组标签自带“到某一刻就改组”的条款, 三条指向同一时刻同一小时({aThen} 是其一), 而它们名下的 {expire} 行恰好是这张表里唯一“标签⇎注释指着两个时刻”的行: "
        u"{aVan} 的标签里写 {aVanTag} ⇎ 注释里写 {aVanCmt}; {aEdm} 同构(标签 {aEdmTag} ⇎ 注释 {aEdmCmt}); {aWin} 亦然(标签 {aWinTag} ⇎ 注释 {aWinCmt})。"
        u"两个年份之差可算: 条款时刻比这份文件的落款({bdyear} 年)晚 {gapday} 天, 而姊妹表的落款比这份落款晚 {gapbir} 天。"
        u"一旦条款生效, 这 {expire} 行要换组、缩写要与标签对齐、第二条里那条 {inv} 逆序的单调性也要重测——但这一步不可由在库文件判定: "
        u"能判它的那份 zdump 表只在构建目录里出现(见第七条), 所以本条只登记“条款在库内有 {untillines} 处”与“它落在未来 {untillines} 处”, 不假装检验它会不会生效。",
     aUntil=AT(u'predicate', u'N', u'until 2026-11-01 02:00; then MST'),
     aBday=AT(u'predicate', u'N', u'Eggert'),
     aVan=RAWAT(u'N', u'America/Vancouver'),
     aVanTag=RAWAT(u'N', u'PST/PDT'), aVanCmt=AT(u'expire_pair', u'N', u'Mountain Standard'),
     aEdm=RAWAT(u'N', u'America/Edmonton'), aEdmTag=RAWAT(u'N', u'MST/MDT'),
     aEdmCmt=AT(u'expire_pair', u'N', u'Central Standard'),
     aWin=RAWAT(u'N', u'America/Winnipeg'), aWinTag=RAWAT(u'N', u'CST/CDT'),
     aWinCmt=AT(u'expire_pair', u'N', u'Eastern Standard'),
     aThen=AT(u'predicate', u'N', u'then MST'), **G)

LINE(u'🧵', u"缩写在三条层里的闭合度 {aAdak} ‖ {aHav} ⇒ 组标签带缩写的 {abg} 组 ⇎ 名下那行注释里带括号的 {withpar} 行 ⇎ 括号总数 {nparen} 枚(一枚以上括号的只有 {twopar} 行)。"
        u"两边写法对得上的: 与第一个括号逐字同 {eqfirst} 处, 与末括号同 {eqlast} 处, 只要出现在任一括号里 {inany} 处——三种口径给出同一个数, 说明分歧不来自“取哪一枚括号”。"
        u"缺口 {gaps} 处分三类, 三类都能各举一枚: 只差空白 {gapspace} 处 {aAdak}(标签里缩写带空格 ⇎ 注释里不带), "
        u"时态差 {gaptense} 处(上一条那 {expire} 行, 例如 {aTense}), 注释里根本没有括号 {gapnopar} 处({aHav} 一类); "
        u"反方向(标签不写缩写而注释里有括号) {reverse} 行, 即 {aNz} ⇎ {aSam}——一枚是标签只肯给规则名, 一枚是括号里装的其实地区限定词。"
        u"第四列本身干净: {rows} 行非空(表自述 {aC4rule}), 取值 {c4kind} 种即行行互不相同, 带分号的 {c4semi} ⇎ 带括号的 {c4par} ⇎ 两者都带的 {c4both}。"
        u"判词: 同一层信息(缩写)在标签⇎注释两处各写一遍, 十之八九对得上; 剩下的对不上处正好是这张表“会在未来变化”的位置——不一致不是抄错, 是两处写的是不同时刻的事实。",
     aAdak=AT(u'tag_longest', u'N', u'HST / HDT'),
     aHav=RAWAT(u'N', u'America/Havana'),
     aTense=RAWAT(u'N', u'America/Edmonton'),
     aNz=RAWAT(u'N', u'New Zealand (NZST/NZDT)'),
     aSam=RAWAT(u'N', u'Samoa (western)'),
     aC4rule=AT(u'header_rule', u'N', u'nonempty comments column'), **G)

LINE(u'📐', u"表自述的三层排序键全部可机检、全部成立 {aSort} ⇒ 时效表头部声明排序是“标准偏移→夏令时偏移→缩写”三级。"
        u"逐级复算: 第一级逆序 {inv} 对; 第二级(同标准偏移下, 有 DST 的组该排在哪里)逆序 {k2inv} 对; 第三级可比较的相邻对 {k3pairs} 组, 逆序 {k3inv} 对。"
        u"三级之外还能查出偏移自己的形状: 非整点偏移 {nonint} 组, 分钟位只有 {minutes} 种取值; DST 步长分布是 +1 小时 {step1} 组 ⇎ "
        u"反向(所谓“夏令时”比标准时更西) {stepneg1} 组 ⇎ 半小时 {step05} 组 ⇎ 两小时 {step2} 组——"
        u"半小时那枚出自 {aHalf}(注释 {aHalfTag}), 两小时那枚出自 {aTroll2}(给南极考察站); "
        u"反向的两枚是 {aIsr}(欧洲/以色列一侧回拨)与 {aMorTag}(摩洛哥只写规则名而不写缩写)。"
        u"姊妹表按另一套自述排序(按国码), 复算其首码逆序也是 {zinv} 对。判词: 写在注释里的排序规则不是修辞, {tags} 行全数可验且零违例; "
        u"而同一份注释里那句“第一列无关”同样可验, 却只在检查器那侧成立(第二条)。",
     aSort=AT(u'header_rule', u'N', u'sorted in a different way'),
     aTroll2=RAWAT(u'N', u'Troll DST'), aHalf=RAWAT(u'N', u'+10:30/+11'),
     aHalfTag=RAWAT(u'N', u'Lord Howe Island'),
     aIsr=RAWAT(u'N', u'IST/GMT (EU DST in reverse)'), aMorTag=RAWAT(u'N', u'(Morocco DST)'), **G)

LINE(u'🧲', u"两时态的分区差多少, 差在哪一列 {aZ70} ‖ {aZmulti} ⇒ 集合上是真子集: 时效表 {nowrows} 行 ⇎ 姊妹表 {zrows} 行 ⇎ 第三表 {trows} 行, "
        u"后两者分别多出 {only70} 与 {onlytab} 个时区名, 时效表自己 {dupn} 处重名。共有的 {shared} 个时区逐列比: "
        u"坐标一致 {coordeq}/{shared} ⇎ 国码一致 {cceq}/{shared} ⇎ 注释列一致 {c4eq}/{shared}, 而姊妹表名下有注释的只有 {z4has} 行(它允许第四列整列缺失: 三列行 {fldz3} 处 ⇎ 四列行 {fldz4} 处, 注释为空 {z4empty} 行)。"
        u"按粒度量复现: 整行级 {grainline} 处 ⇎ 坐标级 {graincoord} ⇎ 时区名级 {grainzone} ⇎ 五词串级 {grainshang}(两侧串库 {shn} ⇎ {shz}); "
        u"与第三表的五词串共有 {shnt}/{sht}, 而时效表的数据层与它自己的注释层共有五词串 {shself} 处、三元组 {sh3nc} 处、二元组只有 {sh2nc} 处(层内串库 {sh3n} ⇎ {sh3c})。"
        u"判词: 两张表说的是同一批钟, 但“同一批”只到坐标与时区名为止; 注释列各自新写(共 {z4kind} 种 ⇎ {c4kind} 种), 于是换了时态就等于换了一次撰稿。",
     aZ70=AT(u'row_z', u'Z', u'Africa/Abidjan'),
     aZmulti=AT(u'row_z', u'Z', u'PR,AG'), **G)

LINE(u'🔬', u"检查器的真值输入不在库里, 而且每次构建都换个起点 {aGet} ‖ {aFs} ⇒ 那段 awk 只认 {kext} 个外部变量, 它们在文件里被赋值 {kunset} 次——全靠调用方喂: "
        u"{aVZ} ⇎ {aVNow} ⇎ {aVOut}。喂进去的头一枚就是那份 zdump 表: 它的变量名在检查器里出现 {zdumptable_k} 次, 而“zdump-now”这个文件名在检查器里出现 {kzdumpnow} 次"
        u"(表名不由检查器说出口, 只由调用方给), 在构建器里出现 {zdumpnow_m} 次(一次写出、一次当输入), 而整个语料库里名字含 zdump 的文件 {mzdfiles} 份、产物 now.ck {mckfiles} 份。"
        u"配方 {aDeps} 声明 {mprereq} 项前置, 库内实有 {mprereqok} 项、缺 {mprereqmiss} 项(日期程序、打包后的数据、zdump、zic 都要现造); "
        u"它先 {aMkdir} 再 {aZic} 造出临时目录, 用两条 zdump 各跑一遍地平线({mhorizons} 种: 一条自“此刻”起 ⇎ 一条自姊妹表自述的 {predyear} 年起), 最后 {aRm} 连真值输入一起删净——建 {mmkdir} 次 ⇎ 删 {mrm} 次, 结论只以 {aMv} 留下一枚时间戳。"
        u"更硬的一点在时间基准: {aNowTs} 让整趟检查的起点取自构建当天的墙钟(同一段里 $$now 被引用 {mdollarnow} 次), 于是同一份表在不同日子检查的是不同的“从现在”; 检查器被调用 {mawkcall} 遍, 其中 {mtablearg} 遍显式给它表名。"
        u"跨度也写着妥协: 前瞻 {myears} 年 ⇎ 注释自认“理论上要 {mbig} 年以上”, 相差 {mratio} 倍; 秒数按 366 天/年取整 {msecs}, 比 365 天口径多 {mdiff} 秒(恰为 {myears} 天)。"
        u"判词: “从今往后一致”是一个必须由外部真值判定的谓词, 而那份真值既不入库又随日期漂移; 所以这条不能像 B49 那样把不变量交回机检, 只能交回构建系统。",
     aGet=AT(u'awk_rule', u'K', u'getline <zdump_table'),
     aFs=AT(u'awk_rule', u'K', u'FS = '),
     aVZ=AT(u'make_rule', u'M', u'-v zdump_table=$@d/zdump-now.tab'),
     aVNow=RAWAT(u'M', u'-v now=$$now'),
     aVOut=RAWAT(u'M', u'-v now_out=$@.out'),
     aDeps=AT(u'make_rule', u'M', u'now.ck: checknow.awk'),
     aMkdir=RAWAT(u'M', u'mkdir $@d'),
     aZic=AT(u'make_rule', u'M', u'./zic'),
     aRm=RAWAT(u'M', u'rm -fr $@d'),
     aMv=AT(u'make_rule', u'M', u'mv $@.out'),
     aNowTs=AT(u'make_rule', u'M', u'CHECK_NOW_TIMESTAMP'), **G)

LINE(u'🧩', u"判定动作只有四类, 而它比的不是行而是“输出序列” {aD3} ‖ {aD2} ⇒ 检查器一共 {kprintf} 条 printf({kprintfk} 种格式), "
        u"判失败的赋值 {kstatus} 处, 出口 {kexit} 处: 其一“无数据”{aD0}(某时区在真值输入里查不到), 其二“两个时区的钟从现在起一样”{aD2}, "
        u"其三“主表里还有一组没人收录的序列”{aDZ}, 其四把对照写进旁出文件{aD4}(仅当调用方给了输出路径)。"
        u"关键在键的选择: 按名字取真值 {kzonedata} 处 ⇎ 按“那段输出文本”建索引 {kzonenowd} 处——所以它查的是“互不相同的未来序列各有一行”, 不是“行与行文字不同”。"
        u"两套列口径也不同: 读真值输入时(非空行序第 {kgtline} 行)仍是默认空白分隔, 制表符口径要到同一序的第 {kfsline} 行才装上, 于是同一份 awk 内部对“什么是一列”有两份答案。"
        u"判词: 检查器测的是等价类的个数, 而等价类由不在库里的文件决定; 这比 B49 那条“不变量只写在代码里”又退一步——这里连代码里的不变量都要等外部数据才能取值。",
     aD0=AT(u'awk_rule', u'K', u'no data'),
     aD2=AT(u'awk_rule', u'K', u'identical from now on'),
     aD3=AT(u'awk_rule', u'K', u'Zone table should have one of'),
     aDZ=AT(u'awk_rule', u'K', u'zonenow[data]'),
     aD4=AT(u'awk_rule', u'K', u'now_out'), **G)

LINE(u'🗂', u"同一个名字能穿过几层 {aSelf} ‖ {aNowOn} ⇒ 把 {hitkinds} 枚关键串各按折叠后的原样判一遍: 命中一层 {hitsingle} 枚 ⇎ 命中多层 {hitcross} 枚 ⇎ 一枚不中 {hitnone} 枚。"
        u"三处最见层次: 姊妹表的名字在它自己体内出现 {selfname_z} 次(它从不提名自己) ⇎ 在时效表里 {selfname_n} 次 ⇎ 在构建器里 {selfname_m} 次; "
        u"“从现在起一致”这句谓词在时效表 {nowon_n} 次 ⇎ 检查器 {nowon_k} 次 ⇎ 姊妹表与构建器各 0 次; "
        u"占位国码在时效表 {xx_n} 次 ⇎ 构建器 {xx_m} 次。真值输入的名字只在构建器 {zdumpnow_m} 次, 而它的变量名在检查器 {zdumptable_k} 次 ⇎ 构建器 {zdumptable_m} 次。"
        u"时效表的名字在检查器里出现 {ntab_k} 次(全在它自己那行注释), 在构建器 {ntab_m} 次。"
        u"判词: 一份文件提到自己的次数为 0({selfname_z}), 而别的层里有人提它 {selfname_m} 次——名字住在别人嘴里; 谓词同理, “从现在起一致”从没在被检表的任何一列里被检验过。",
     aSelf=AT(u'header_z', u'Z', u'public domain'),
     aNowOn=AT(u'cross_phrase', u'N', u'agree from now on'), **G)

LINE(u'🧪', u"这条的可核事实分三档 {aAny}(最西一档的时区名, 它 ⇎ 姊妹表里那一枚逐字同写) ⇒ 第一档 B52V 可复算: 四份源的字节/行/列口径、组标签机器({tags}⇎{rows} 的 1:1)、"
        u"三层排序键的逆序数({inv}/{k2inv}/{k3inv})、缩写闭合的三口径({eqfirst}/{eqlast}/{inany})、坐标两种宽度({cw11}⇎{cw15})、"
        u"集合差({only70}/{onlytab})、四种粒度的共有量、检查器与构建器的每一处计数, 全部由 audit.py 的 _b52_scan 从四份 raw 重算。"
        u"第二档只能由集合运算得出: 谁是谁的子集、共有时区的逐列比对、穿层命中矩阵。"
        u"第三档不可核, 也是本条与 B48/B49 的分界: “从现在起这些钟一致”这一谓词要靠一份 zdump 输出表来判, 而这样的文件在库里 {mzdfiles} 份, 检查起点又取自构建当天的墙钟——"
        u"所以它写进判词而不写成待核, 门槛里没有一项替它背书。"
        u"锚的可核性只有一条: 正文里“源标签紧接原子引文”的配对共 {nat} 处／{ndist} 条去重串, 命中列分布是一源 {nsgl} ⇎ 多源 {ncross} ⇎ 四源 {nall}, "
        u"每条去重串对四份源逐一判成员, 共 {checked} 次检查, 错配 {aerr} 处; 归属由正文现推, 不由旁注文件说了算——"
        u"采集侧为挑引文切的候选锚池不写进判词, 门槛也就无从核它。",
     aAny=AT(u'cross_zone', u'N', u'Pacific/Pago_Pago'), **G)

LINE(u'∴', u"骨架 ⇒ ① 四源 {nb} 字节 ⇎ 非空行 {ne} ⇎ 数据行 {nd}, 齐四列的只有 {fldn4} 行; "
           u"② 排序键 {tags} 枚组标签撑起 {rows} 行、偏移 {offkinds} 种、逆序 {inv}, 而该键在数据列出现 {rowoffany} 次、被检查器以 {kskip} 条规则整层跳过; "
           u"③ 第一列 {col1kind} 种取值 ⇎ 姊妹表 {zkind} 种, 共有 {shared} 个时区坐标一致 {coordeq} ⇎ 国码一致 {cceq}; "
           u"④ 缩写闭合三口径同为 {eqfirst}, 缺口 {gaps} 分三类, 其中 {expire} 行标签⇎注释指向两个时刻, 条款比落款晚 {gapday} 天; "
           u"⑤ 三层排序全部可验全部零违例({inv}/{k2inv}/{k3inv}), DST 步长 {step1}⇎{stepneg1}⇎{step05}⇎{step2}; "
           u"⑥ 真值输入在库 {mzdfiles} 份 ⇎ 配方前置缺 {mprereqmiss} 项 ⇎ 起点取自墙钟, 故“从现在起一致”不可由在库文件判定; "
           u"⑦ 检查器按输出文本建索引({kzonenowd} 处)而非按行文, 内部还用两套列口径(非空行序第 {kgtline} ⇎ 第 {kfsline} 行); "
           u"⑧ 姊妹表从不提名自己({selfname_z} 次), 谓词也不在数据层({nowon_n}⇎{nowon_k})。"
           u"判词: 一张表的组织键、有效期与判据分别住在注释层、未来与库外三处, 三处都不在“可机检的现在”里; "
           u"而能机检的部分(排序、列口径、集合、闭合度)在本条全部交出零违例, 这恰好反衬出剩下那部分为什么不可核。", **G)

LINE(u'ℒ', u"方法 ⇒ 读“会过期的表”先分层再读数: 把每一句话按它住在哪一层归类(数据列⇎组标签注释⇎头部注释⇎程序⇎配方), "
        u"然后逐层问“谁读它”。本条的做法是拿检查器的字段引用表({kref0}/{kref3}⇎{kref1}/{kref2}/{kref4})当“可见性”的判据, 而不是拿人眼。"
        u"第二步测声明式不变量: 头部说了三级排序就分三级各算逆序数, 说了第四列非空就数它 {c4kind}/{rows} 种取值。"
        u"第三步把时间当口径而不是当背景: 同一份文件里的 {dateskinds} 个日期各属哪一层、条款距本表落款 {gapday} 天⇎两份落款相距 {gapbir} 天, 以及自认的前瞻跨度 {myears}⇎{mbig}。"
        u"第四步给“不可核”留位置并写明成因(真值输入在库 {mzdfiles} 份 ⇎ 墙钟变量 {mdollarnow} 处), 绝不用漂亮的比例凑数。"
        u"第五步注意同名不同层: 同一个缩写、同一个文件名、同一个谓词, 在标签层⇎注释层⇎程序层各写一遍, 逐字对不上时先问“是不是在说不同时刻”, 再判谁错了。", **G)

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 四份源各自 {nc} 字符, 而摘要只能取锚点触到的窗口; "
        u"本条的结论不住在窗口里——“组织键住在被跳过的那一层”“三级排序零违例”“缺口 {gaps} 分三类”“真值输入在库 {mzdfiles} 份”"
        u"都是跨四份文件、跨两层集合运算的形状, 要整段复算才看得见。尤其 {iso} 处日期⇎{untillines} 处条款⇎{pred} 句谓词这三样, 任何单窗口都装不下它们的对照。"
        u"读它请按“这句话住在哪一层、谁去读它”来读, 而不是按“少抄了多少原文”。", **G)

body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([NZKM])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FN[TAGS.index(x[0])]]
HITC = dict((a, hitset(a)) for a in ANCH)
CLS = dict((c, len([a for a in ANCH if cls_of(HITC[a]) == c])) for c in (u'single', u'cross', u'all4'))
AMETA = {u'anchor_total': len(CITES), u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'],
         u'anchor_all4': CLS[u'all4'], u'checks': DIST * 4}
assert not ERR, ERR[:3]
for k, v in sorted(AMETA.items()):
    reg(str(v), u"B52V('%s')" % k, TOKV.get(k, k))
for k, v in sorted(AMETA.items()):
    body = body.replace(u'◘%s◙' % k, str(v))
assert u'◘' not in body, u'锚统计量占位符未回填'
assert sum(AMETA[u'anchor_' + c] for c in (u'single', u'cross', u'all4')) == DIST
DERIV = dict((k, v[0]) for k, v in K.items())
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(os.path.join(ROOT, C, u'_deriv52.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(os.path.join(ROOT, C, u'_b52flat.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(os.path.join(ROOT, C, u'_atoms52.txt'), 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[NZKM]⟧', body)),
      u'classes': dict((c, [a for a in sorted(ANCH) if cls_of(HITC[a]) == c])
                       for c in (u'single', u'cross', u'all4')),
      u'collisions': COLL, u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV), u'notes': NOTES,
      u'pool_used': len(set(USEDATOM) & set(ANCH)), u'enc_chars': len(body.replace(NL, u'')),
      u'nsrc': 4, u'flat': F}
json.dump(CH, io.open(os.path.join(ROOT, C, u'_b52checks.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

srcline = (u'src: ' + u' ⇎ '.join(u'%s (%s 字节／数据行 %s)' % (PATH[i], str(F[u'bytes'][i]), str(F[u'dat'][i]))
                                 for i in range(4)) +
           u' (同目录另有 zone.tab 与 version 两份, 只用于集合与口径对照, 不作锚源)\n')
联结 = (u'；联结不是“四份材料”, 而是“一张表与它的三个层次”: 分区表按偏移排序(%d 枚组标签⇎%d 行, 逆序 %d), '
        u'检查器按定义跳过那一层注释, 它要比的输出序列由构建配方现造现删(库内 %d 份), 谓词“从现在起一致”因此不可在库判定; '
        u'姊妹表把同一批钟按 %d 年重说一遍, 共有时区坐标全同而国码全不同(%d⇎%d)\n') % (
    F[u'tags'], F[u'rows'], F[u'inv'], F[u'mzdfiles'], F[u'predyear'], F[u'coordeq'], F[u'cceq'])
text = (u'# B52 时效表 ⇎ 检查它的 awk ⇎ 它要的那份不存在的 zdump 表：组织键住在被跳过的那一层\n' + srcline + 联结 +
        u'tags: 三级排序零违例 偏移只活在注释层 检查器只读两列 占位码与真国码 自述过期条款 标签与注释指向两个时刻 '
        u'缩写闭合三口径 真值输入在库为零 前瞻跨度自认不足 墙钟决定检查起点 按输出序列建索引 同名不同层 穿层命中矩阵 锚归属由正文现推\n' +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill52.py 从 corpus/_b52checks.json 与 corpus/_b52meas.json 现算写入）\n')
io.open(os.path.join(ROOT, ENTRY), 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d 串 ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'DERIV %d 键(0 键折 %d 项) ｜ 同数冲突 %d 组' % (len(DERIV), len(ZERO), len(COLL)))
for k, n in COLL[:12]:
    print(u'  同数 %s ← %s' % (k, n))
print(u'残留未替换占位符 %d' % len(re.findall(u'\\{[a-zA-Z_]+\\}', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))))
print(u'锚内拉丁 %d ｜ 锚外拉丁 %d ｜ 标签 %d 枚 ｜ 池内取用 %d ｜ 扁平键 %d 个' % (
    CH[u'letters_in'], CH[u'letters_out'], CH[u'tagn'], CH[u'pool_used'], len(F)))
