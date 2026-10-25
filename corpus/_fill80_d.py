# ---------- 第四段: 布尔门 ⇎ 标量恒等式 ⇎ V 形 ⇎ DERIV 全在本遍读数上重 eval ----------
# 门与式的**右式**从 `_mkB80.py` 源码 `ast` 摘出, 一条都不抄第二遍的结论。
MSA = ast.parse(MS)

CLOSE_SRC = []
for _nd in MSA.body:
    if isinstance(_nd, ast.Assign) and isinstance(_nd.targets[0], ast.Subscript):
        _t = _nd.targets[0]
        if isinstance(_t.value, ast.Name) and _t.value.id == u'CLOSE' \
                and isinstance(_t.slice, ast.Constant) and isinstance(_t.slice.value, type(u'')):
            CLOSE_SRC.append((_t.slice.value, ast.get_source_segment(MS, _nd.value)))
assert len(CLOSE_SRC) == 28 and len(set(k for k, _ in CLOSE_SRC)) == 28, len(CLOSE_SRC)

ENV = {u'F': G, u'G': G, u'NSRC': NSRC, u'SN': SN, u'GN': GN, u'NEGND': NEGND, u'NL': NL,
       u'sum': sum, u'len': len, u'all': all, u'any': any, u'max': max, u'min': min,
       u're': re, u'sorted': sorted, u'tuple': tuple, u'set': set, u'str': str}
for _k, _e in CLOSE_SRC:
    G[_k] = 1 if eval(_e, ENV, ENV) else 0
G['bool_clos_n'] = len(CLOSE_SRC)
G['bool_clos_sum'] = sum(1 for _k, _ in CLOSE_SRC if G[_k])

ZSRC = []
for _nd in MSA.body:
    if isinstance(_nd, ast.Expr) and isinstance(_nd.value, ast.Call) \
            and isinstance(_nd.value.func, ast.Name) and _nd.value.func.id == u'Z':
        ZSRC.append((_nd.value.args[0].value, _nd.value.args[1].value))
assert len(ZSRC) == 139, len(ZSRC)
ZR = [(_e, _w, eval(_e, ENV, ENV)) for _e, _w in ZSRC]
G['zid_fail'] = [_w for _e, _w, _r in ZR if _r]
G['scalar_clos_n'] = len(ZR)
G['scalar_clos_sum'] = len([1 for _e, _w, _r in ZR if not _r])
G['x_ident_n'] = len(ZR)

# list_clos_n 的口径是“SCAN 段此刻已登记的键”: 按语句顺序收 F[...] 赋值目标,
# 收到 `F['list_clos_n'] =` 为止, 再把 CLOSE 的 28 枚门名并进来(它们由一条 for 动态落键)。
SCAN_KEYS = []
for _nd in MSA.body:
    if isinstance(_nd, ast.Assign) and isinstance(_nd.targets[0], ast.Subscript) \
            and getattr(_nd.targets[0].value, u'id', None) == u'F' \
            and getattr(_nd.targets[0].slice, u'value', None) == u'list_clos_n':
        break
    for _m in ast.walk(_nd):
        if isinstance(_m, ast.Assign) and isinstance(_m.targets[0], ast.Subscript) \
                and isinstance(_m.targets[0].value, ast.Name) and _m.targets[0].value.id == u'F' \
                and isinstance(_m.targets[0].slice, ast.Constant) \
                and isinstance(_m.targets[0].slice.value, type(u'')):
            SCAN_KEYS.append(_m.targets[0].slice.value)
SCAN_KEYS = set(SCAN_KEYS) | set(_k for _k, _ in CLOSE_SRC)
G['list_clos_n'] = len([_k for _k in SCAN_KEYS
                        if (u'_close' in _k or u'_ledger' in _k) and isinstance(G[_k], list)])
G['contract_n'] = len(G) + 1

# ---------- V 形恒等式 ⇎ DERIV 复算点: 只走查表通道, 不走 F 下标通道 ----------
NSV = dict(G)
B80V5 = lambda k, i=None: (NSV[k] if i is None else NSV[k][i])
ENVV = {u'B80V': B80V5, u'sum': sum, u'len': len, u'max': max, u'min': min, u'abs': abs,
        u'sorted': sorted, u'tuple': tuple, u'set': set, u'round': round, u'str': str,
        u'float': float, u'int': int}
ZV2 = [(_e, _w, eval(_e, ENVV, ENVV)) for _e, _w in CH[u'zid']]
ZVFAIL = [_w for _e, _w, _r in ZV2 if _r != 0]
assert not ZVFAIL, ZVFAIL[:3]

DFL = []
DCITE = 0
for _kk in sorted(DER, key=lambda x: (len(x), x)):
    _v = DER[_kk]
    DCITE += _v.count(u"B80V(")
    try:
        _got = eval(_v, ENVV, ENVV)
    except Exception as _e:
        DFL.append((_kk, repr(_e)[:80]))
        continue
    if str(_got) != _kk and repr(_got) != _kk:
        DFL.append((_kk, _v[:90], str(_got)))
assert not DFL, DFL[:4]

# ---------- 与扁平表逐值对账 ----------
_jr = lambda x: json.loads(json.dumps(x))
MISS = [k for k in G if k not in FLAT]
BAD = [(k, _jr(G[k]), _jr(FLAT[k])) for k in G if k in FLAT and _jr(G[k]) != _jr(FLAT[k])]
UNCOVER = [k for k in FLAT if k not in G]
assert not DFL, DFL[:4]
assert not MISS, MISS[:6]
assert not UNCOVER, UNCOVER[:6]
assert not BAD, BAD[:6]
assert G['contract_n'] == len(FLAT) == 583
assert not G['zid_fail'], G['zid_fail'][:3]

# ---------- 本遍硬断言: 全部由现读结果支, 不引第二遍的结论 ----------
assert G['all_txt_no_html'] == 1 and G['all_faces_read'] == 1
assert G['dead_needles_none'] == 1 and G['neg_all_cold'] == 1
assert G['sec_scope_three'] == 1 and G['v2616_outside_own_sec'] == 1
assert G['k9110_inside_sec'] == 1 and G['tone_zero_7231_sec'] == 1
assert G['subj_only_passive_2616'] == 1 and G['act_sec_only_two_docs'] == 1
assert G['no_auto_vocab_6585'] == 1 and G['no_retry_after_8470'] == 1
assert G['no_code_def_8470'] == 1 and G['neither_428_429_in_2616'] == 1
assert G['neither_428_429_in_9110'] == 1 and G['rename_delta_vs_delay'] == 1
assert G['ascii_except_9110'] == 1 and G['pageless_9110_only'] == 1
assert G['sh_equals_fold_for_9110'] == 1 and G['one_maxlen_outlier'] == 1
assert G['year_one_inversion'] == 1 and G['ph_straddle_except_6585'] == 1
assert G['ans_span_shape'] == 1 and G['no_page_break_in_answer'] == 1
assert G['axis_two_buckets_used'] == 1 and G['pair_all_share'] == 1
assert G['hyphen_break_only_two'] == 1 and G['dblspace_hidden_by_fold'] == 1
assert G['bool_clos_n'] == G['bool_clos_sum'] == 28
assert G['scalar_clos_n'] == G['scalar_clos_sum'] == G['x_ident_n'] == 139
assert G['list_clos_n'] == 3 and len(ZV2) == 163 and len(DER) == 198
assert G['anchor_err'] == 0 and G['pick_diff'] == 0 and G['pick_agree'] == 167
assert G['ladder_close'] == 0 and G['ladder_monotone'] == 1 and G['re_eq_cur'] == 1
assert G['overlap_extra'] == 0 and sum(G['sh_loses']) == 0
assert G['shell_ledger_close'] == 0 and G['pair_close'] == 0 and G['union_close'] == 0
assert G['pool_tier_close'] == 0 and G['axis_close'] == 0 and G['s_union_close'] == 0
assert G['s_pool_tier_close'] == 0 and G['apool_tier_close'] == 0 and G['apool_tag_close'] == 0
assert G['sec_sents_gap'] == [0, 0, 0, 0, 0] and sum(G['sh_no_sec_own']) == G['sh_no_sec_n']
assert G['blk_tone_ruler_close'] == 0 and G['pin_rt_all'] == 1 and G['pin_wrongline'] == 0
assert G['pp_gap_close'] == 0 and G['w_ledger_close'] == 1
assert G['neg_hit_widest'] == 0 and G['neg_hit_strict'] == 0
assert G['sn_sec_docs_scope'][2] == -1 and G['sn_sec_docs_scope'][3] == -1
assert G['tone_alnum_gap'] == [0, 0, 0, 0, 0] and G['tone_wide_close'] == 0
assert G['pool_incl'][0] - G['pool_incl'][1] + G['pool_incl'][2] - G['pool_incl'][3] \
    + G['pool_incl'][4] == G['pool_union'] == G['union_incl']
print(u"第四段完成: 布尔门 %d/%d ⇎ 标量恒等式 %d/%d ⇎ V 形 %d 条全真 ⇎ DERIV %d 键 ⇎ %d 处引用全对 ⇎ "
      u"扁平 %d 键全覆盖 ⇎ 不符 %d ⇎ 独有 %d ⇎ 未复算 %d" % (
          G['bool_clos_sum'], G['bool_clos_n'], G['scalar_clos_sum'], G['scalar_clos_n'],
          len(ZV2), len(DER), DCITE, len(FLAT), len(BAD), len(MISS), len(UNCOVER)))

# ---------- ⛓解读注 ----------
def QT(tag, s):
    assert s in ANSET[IDX[tag]], u'本遍锚平面读不到: ' + s[:50]
    return u'⟦%s⟧⟨%s⟩' % (tag, s)


def cell(c):
    assert u'|' not in c, c[:60]
    assert c.count(u'`') % 2 == 0, c[:60]
    return c


def NJ(xs):
    return u' ⇎ '.join(u'%s' % x for x in xs if x is not None)


L2 = []
A = L2.append
A(u"第四遍(`corpus/_fill80.py`)换算法不换定义地重跑一遍: 行界由手写索引循环按 `\\n` 切(第二遍是 `str.split`, 采集侧是"
  u" `re.split`), 行数三档(切格数 ⇎ 换行枚数 ⇎ `splitlines()`)互相对拍; 折平走 `re.sub` 的空白折叠档(第二遍是"
  u" `' '.join(s.split())`), 归一尺与 `pnorm` 逐份对拍, 词数走“手写吃档数非空白连续段”代 `len(s.split())`; 页壳谓词自起第三"
  u" 档——strip 后按空白切 token、逐段比首尾(第二遍是折平再切, 采集侧是三条整序正则), 在全部 %s 行上逐行对拍; 针计数起三档"
  u" `str.count` ⇎ `findall(re.escape)` ⇎ `findall('(?=针)')`, 边界尺换成 lookahead 重叠定位后由本遍自看的左右邻判定"
  u" (第二遍是游标 find 加 `_nb` 手扫), 另起一条断言正则档只用于对拍; 节号尺一条 `^(\\d+(\\.\\d+)*)(\\.?)` 代第二遍的逐字符"
  u" 吃档, 句界尺一条 `\\.(?=[ \\t\\n]*(?:[A-Z(]|$))` 的 finditer 代手扫, 施事 ⇎ 义务 ⇎ 数字 ⇎ 状态码 ⇎ ABNF ⇎ 抬头 ⇎ 编号标题"
  u" 各起一条本遍的正则或切片档并在全库逐行对拍; 偏移→原行号走 `bisect_right`, 并把“片段之间的一个空格”累加成显式数组"
  u" (第二遍在查表时现算), 段界定位把 `str.find` 换成编译一次转义针的 `search(hay, frm)`; 池代数: 归属向量走 `Counter` 直方图"
  u" ⇎ 容斥走“对文档下标的组合逐枚求交”(第二遍是 C(len(v),k) 元算式)⇎ 两两共用改扫一遍键域 ⇎ `dehyph` 换成"
  u" `re.sub('-[ \\t]*','')`; 句池切档用手写扫描代零宽 `re.split`; 实体 ⇎ `⟦…⟧⟨…⟩` 引文各用手写配对扫描代 `re.findall`;"
  u" 锚归属双轨(一轨对锚平面逐行 membership, 一轨对整篇归一串 substring), 两式同判才计数; 28 道布尔门 ⇎ 139 条标量恒等式的"
  u" **右式**从 `_mkB80.py` 源码用 `ast` 摘出后在本遍读数上 eval, 163 条 V 形 ⇎ 198 键 DERIV 从 `_b80checks.json` ⇎"
  u" `_deriv80.json` 回读 eval——一条都不抄第二遍的结论。 48 行针表 `SENT` ⇎ 14 段 `PINS` ⇎ `TONE` ⇎ `AUTOFAM` ⇎ `REWORD`"
  u" ⇎ `SUBJ` ⇎ `ACT` ⇎ `NUM` ⇎ `METH` ⇎ `NEG` ⇎ `CODES` ⇎ `RANK` 的**定义**从源码 `ast`/`exec` 复用——要换的是量, 不是定义。"
  % format(sum(G['lines']), u','))
A(u"本遍复算 %d 个键(扁平表 %d 键全覆盖 ⇎ 本遍独有 %d ⇎ 未复算 %d ⇎ 逐值不符 %d); SCAN 段登记的标量恒等式 %d 条在本遍读数上"
  u" 重跑全为真(通过 %d ⇎ 失败清单 %d 条) ⇎ `checks` 里的 V 形恒等式 %d 条(比 SCAN 段多 %d 条, 多的那批在 emit 段并进来)全真"
  u" ⇎ DERIV %d 键 ⇎ %d 处引用重跑全对 ⇎ 布尔门 %d 道在本遍现算全绿 ⇎ 清单式闭合 %d 项 ⇎ 与采集遍逐键横比 %d 键相符 ⇎ %d 键"
  u" 不符 ⇎ 门槛侧 %d 处引文锚逐枚回本遍锚平面验命中 %d 枚 ⇎ 去重 %d 串 ⇎ 编码区 %d 非换行字符 ⇎ 判词 %d 条。" % (
      len(G), len(FLAT), len(MISS), len(UNCOVER), len(BAD),
      G['scalar_clos_n'], G['scalar_clos_sum'], len(G['zid_fail']), len(ZV2),
      len(ZV2) - G['scalar_clos_n'], len(DER), DCITE, G['bool_clos_n'], G['list_clos_n'],
      G['pick_agree'], G['pick_diff'], G['anchor_total'],
      len([1 for t, x in CITES if x in ANSET[IDX[t]]]), G['anchor_distinct'], G['enc_chars'],
      G['checks']))
A(u"")
A(u"| 轴 | 本注口径(与前三遍的实现差异) | 现读结果 | 对账 |")
A(u"|---|---|---|---|")
rows = [
    (u"行界⇎换页⇎页壳",
     u"手写 `\\n` 索引循环 ⇎ `str.count` ⇎ `splitlines()` 三档并立; 壳谓词自起“strip 后切 token、逐段比首尾”的第三档",
     u"原行 %s ⇎ 换行枚 %s ⇎ splitlines %s ⇎ 收尾换行 %d 份 ⇎ 换页符 %s ⇎ [Page] 壳行 %s ⇎ 只剩换页符档 %s" % (
         J(G['lines']), J(G['lines_nl']), J(G['lines_split']), sum(G['tail_nl']),
         J(G['ff']), J(G['shell_lines']), J(G['ff_only'])),
     u"行数账 %d ⇎ 换页减页壳 %s ⇎ 行内混排 %s; 壳三本账 %d ⇎ 本遍多判 %s ⇎ 采集多判 %s ⇎ 换页档与采集行档同值判定 %d。" % (
         G['lines_split_close'], J(G['ff_minus_pg']), J(G['ff_inline']), G['shell_ledger_close'],
         J(G['shell_mk_only']), J(G['shell_pick_only']), G['ff_only_vs_pick_lines'])),
    (u"折平⇎归一⇎字节",
     u"折平用 `re.sub` 空白折叠档 ⇎ 词数用手写连续段计数; 字节⇎码位差走 `utf-8` 编码长度减码位数",
     u"字节 %s ⇎ 面内码位 %s ⇎ 折平码位 %s ⇎ 字节−码位差 %s ⇎ 非 ASCII %s ⇎ BOM %s" % (
         J(G['bytes']), J(G['chars']), J(G['fold_chars']), J(G['byte_cp_delta']),
         J(G['nonascii']), J(G['bom'])),
     u"回车 %s ⇎ NUL %s ⇎ 折平后双空格 %s(所以标题形状只能在原行上量, 判定 %d); 9110 的 %d 枚非 ASCII 全在姓名行 %s。" % (
         J(G['cr']), J(G['nul']), J(G['dblspace_in_fold']), G['dblspace_hidden_by_fold'],
         G['nonascii'][4],
         QT(u'9110', u'   D. Lawrence, Paul J. Leach, Håkon W. Lie, Ari Luotonen, Larry'))),
    (u"标签四把尺⇎实体",
     u"`<…>` 形由手写扫描给区间(换行不吃), 四把尺在区间上按首字符切片分类; 实体尺手写吃 `&…;` 至多 9 字符",
     u"尖括号形 %s ⇎ 开名形 %s ⇎ 闭名形 %s ⇎ 裸 URL 形 %s ⇎ 伪法余数 %s ⇎ 实体 %s ⇎ 注释 %s" % (
         J(G['tag_shape']), J(G['tag_open']), J(G['tag_close']), J(G['tag_url']),
         J(G['tag_pseudo']), J(G['ent_total']), J(G['comment'])),
     u"6585 的 %d 枚被三把尺分完(判定 %d⇔%d+%d+%d, 它真带了一页示例 HTML: %s); 8470 的 %d 枚名形两把尺全零 ⇎ 全库零实体零注释。" % (
         G['tag_shape'][2], G['tag_shape'][2], G['tag_open'][2], G['tag_close'][2], G['tag_url'][2],
         QT(u'6585', u'         <p>I only allow 50 requests per hour to this Web site per'),
         G['tag_shape'][3])),
    (u"四档面⇎48 枚针",
     u"面构造换 `re.sub` 折平 ⇎ `bisect` 映行 ⇎ 三档计数(非重叠 ⇎ 转义 findall ⇎ lookahead 重叠)逐枚并立",
     u"名下读到的枚数 %s ⇎ 逐行 %s ⇎ 折平 %s ⇎ 摘壳 %s ⇎ 节窗 %s(-1=无这一档) ⇎ 针 %d 枚(反向 %d)" % (
         J(G['needles_owned']), J(G['sn_strict_docs']), J(G['sn_fold_docs']), J(G['sn_sh_docs']),
         J(G['sn_sec_docs_scope']), G['needle_n'], G['neg_n']),
     u"阶梯账 %d ⇎ 单调 %d ⇎ 正则轨=游标轨 %d ⇎ 重叠不多吃 %d ⇎ 折行救回 %d 枚按份 %s ⇎ 摘壳掉 %d 枚 ⇎ 新开 %d 枚(按份 %s) ⇎ 节外 %d 枚按份 %s ⇎ 死集 %d。" % (
         G['ladder_close'], G['ladder_monotone'], G['re_eq_cur'], G['overlap_extra'],
         G['fold_minus_strict_n'], J(G['fold_minus_strict_own']), sum(G['sh_loses']),
         sum(G['sh_gains']), J(G['sh_gains']), G['sh_no_sec_n'], J(G['sh_no_sec_own']), len(G['dead_needles']))),
    (u"节窗⇎节界",
     u"节号尺一条正则代逐字符吃档; 定界由“下一个同级标题”在原行面上前缀匹配, 且不早于节头那一行",
     u"有节 %d 份 ⇎ 节头 %s ⇎ 窗幅字符 %s ⇎ 行 %s ⇎ 词 %s ⇎ 句 %s ⇎ 占摘壳面千分比 %s" % (
         G['sec_found_n'], NJ(G['sec_head_line']), J(G['sec_chars']), J(G['sec_lines']),
         J(G['sec_words']), J(G['sec_sents']), J(G['sec_share_permille'])),
     u"句数两把尺(finditer ⇎ 逐字符扫)逐份同值 %s ⇎ 同名标题命中 %s(合计 %d=有节 %d 份各一行正文+目录 %d 行) ⇎ 节尾收束式 %s ⇎ 正文行 %s。" % (
         J(G['sec_sents_gap']), J(G['sec_hit_n']), G['sec_hit_tot'], G['sec_found_n'],
         G['sec_row_dup'][4], NJ(G['sec_end_kind']), NJ(G['sec_body_line']))),
    (u"义务词五式⇎两把边界尺",
     u"边界尺=lookahead 重叠定位后验左右邻(alpha ⇎ alnum 两档), 另起断言正则档只用于对拍; 大写族⇎小写族分账",
     u"最宽档合计 %s ⇎ 折平 %s ⇎ 纯 MUST %s ⇎ 大小写差 %s ⇎ 小写四词族 %s ⇎ 被 72 列切开 %s" % (
         J(G['tone_tot']), J(G['tone_fold_tot']), J(G['tone_must_pure']), J(G['tone_case_gap']),
         J(G['tone_word_lc_tot']), J(G['tone_straddle'])),
     u"alpha 与 alnum 两尺逐份同值 %s ⇎ 手扫轨=正则轨判定 %d ⇎ MUST 账 %s ⇎ 节窗内义务词 %s ⇎ 7231 节内 %d 枚(判定 %d)。" % (
         J(G['tone_alnum_gap']), G['tone_wide_close'], J(G['tone_must_ledger']),
         J(G['tone_sec_tot']), G['tone_sec_tot'][1], G['tone_zero_7231_sec'])),
    (u"automat×retry⇎重来八式",
     u"六式 ⇎ 八式的定义照抄 `AUTOFAM` ⇎ `REWORD`; 计数走三档, 族内互含由本遍的逐对子串判定现算",
     u"automat×retry 折平 %s ⇎ 逐行 %s ⇎ 去重 %s ⇎ 裸 automat* %s ⇎ 重来八式 %s ⇎ 去重 %s ⇎ 零枚族数 %s ⇎ idempotent %s" % (
         J(G['auto_tot_fold']), J(G['auto_tot_line']), J(G['auto_union_fold']), J(G['auto_bare']),
         J(G['reword_tot']), J(G['reword_union']), J(G['reword_zero_n']), J(G['idem_str'])),
     u"两档逐份同枚(差合计 %d) ⇎ 摘壳不多不少 %s ⇎ 6585 六式零枚(判定 %d) ⇎ 族内互含只在 9110 %d 处 ⇎ 只属一份的说法 %d 枚 ⇎ 八式全库无 “make a new request”: %s。" % (
         sum(G['auto_gain']), J(G['auto_sh_minus_fold']), G['no_auto_vocab_6585'],
         G['auto_fam_overlap'][4], len(G['reword_own'][0]) + len(G['reword_own'][4]),
         QT(u'6585', u'   to wait before making a new request.'))),
    (u"施事者⇎主被动",
     u"九式 `SUBJ` ⇎ 七式 `ACT` 定义照抄; 点名与否由本遍在针前取“冠词+名词”切片判定, 不重算第二遍的句式函数",
     u"九式命中 %s ⇎ 点名主动句 %s ⇎ 不点名被动句 %s ⇎ 泛称七式 %s ⇎ 节窗内点名 %s ⇎ 被切开 %d 枚" % (
         J(G['subj_n']), J(G['subj_active']), J(G['subj_passive']), J(G['act_tot']),
         J(G['act_sec_tot']), G['subj_straddle_tot']),
     u"被动判词全库恰一枚(判定 %d) ⇎ 7231 与 6585 一个施事者也不点(判定 %d) ⇎ POST 在节窗被点名只在 9110: %d 次 ⇎ 切开两枚都在 9110(判定 %d)。" % (
         G['subj_only_passive_2616'], G['subj_active'][1] + G['subj_active'][2] == 0,
         G['meth_post_sec'][4], G['only_9110_straddle'])),
    (u"数字七式⇎单位换代",
     u"`NUM` 七式定义照抄; 带边界尺与裸串尺并立, 被长数吃进的假阳性单独落账; 换代净账由本遍现算 delay−delta",
     u"七式(3600 ⇎ 120 ⇎ 50 req/h ⇎ 2 min ⇎ delay ⇎ delta ⇎ HTTP-date)逐份 %s ⇎ 总量 %s ⇎ 数字字符 %s ⇎ Retry-After 行 %s ⇎ 净账 %s" % (
         J(G['num']), J(G['num_tot']), J(G['digit_chars']), J(G['ra_count']), J(G['num_rename'])),
     u"delta⇎delay 完全分家(判定 %d): 2616 %d 枚 delta ⇎ 7231 与 9110 各 %d/%d 枚 delay ⇎ 假阳性 %s ⇎ 8470 不提 Retry-After(判定 %d) ⇎ 只属一份的数字族 %d 族 ⇎ 两分钟例 %s。" % (
         G['rename_delta_vs_delay'], G['num'][0][5], G['num'][1][4], G['num'][4][4],
         J(G['num_sub']), G['no_retry_after_8470'],
         len([x for x in G['num_own'] if x]), J(G['ra_two_minutes']))),
    (u"状态码定义行⇎ABNF",
     u"定义行尺一条正则取编号、再手工吃空白、看码后一字符(第二遍是节号函数加两段下标); ABNF 三式各一条前缀尺",
     u"定义行 %s ⇎ 目录行 %s ⇎ 族数 %s ⇎ 9110 失踪族 %s ⇎ 7231 失踪 %s ⇎ 8470 括号印法 %d 枚 ⇎ 其中被切开 %d" % (
         J(G['code_defined_n']), J(G['code_toc']), J(G['code_def_fams']),
         u'%d 族' % len(G['code_absent_lbl'][4]), u' '.join(G['code_7231_drops']),
         G['paren'][3][0], G['paren_straddle'][3]),
     u"2616 与 9110 定义集逐枚同(判定 %d) ⇎ 8470 零定义(判定 %d) ⇎ 9110 既不定义 428 也不定义 429(判定 %d) ⇎ 6585 的 428 定义行印两处(目录 ⇎ 节头) ⇎ ABNF 竖线⇎斜杠⇎引号 %s ⇎ 账 %s。" % (
         G['code_set_2616_eq_9110'], G['no_code_def_8470'], G['neither_428_429_in_9110'],
         J(G['ra_abnf_forms']), J(G['ra_abnf_ledger']))),
    (u"搬字两把尺⇎容斥",
     u"归属向量走 `Counter` 直方图 ⇎ 容斥走“文档下标组合逐枚求交” ⇎ 两两共用改扫键域; 句池切档用手写扫描代零宽 `re.split`",
     u"行尺池 %s 行 ⇎ 并集 %s ⇎ 分档 %s(共用 1..5 份的行数) ⇎ 最大对 %d(%s) ⇎ 逐字节 %d+只归一 %d ⇎ 原始行枚 %d ⇎ 句尺池 %d ⇎ 句尺最大对 %d" % (
         format(G['pool_n'], u','), format(G['pool_union'], u','), str(G['pool_tier']),
         G['pair_max'], G['pair_max_lbl'], G['pair_max_byte_keys'], G['pair_max_norm_only_keys'],
         G['pair_max_byte_lines'], G['s_pool_n'], G['s_pair_max']),
     u"容斥 %s 归到并集判定 %d ⇎ 分档账 %d ⇎ 归一因由四桶 %s(非空桶 %d 个 ⇎ “恰两桶”门 %d) ⇎ 行尺→句尺差 %d 枚(一句由 %d 行摊开) ⇎ 单位差 %d 行 ⇎ 最大对里只属这一对 %d 枚。" % (
         str(G['pool_incl']), G['union_close'], G['pool_tier_close'], G['axis_str'],
         G['axis_str_n'], G['axis_two_buckets_used'], G['s_ruler_drop_7231_9110'], G['pair_row_per_sent'],
         G['pair_byte_unit_gap'], G['only2_7231_9110'])),
    (u"抬头谱系⇎年份",
     u"抬头字段尺走 `startswith` 加双空格切档, 年份走“月名 token 紧跟四位数字 token”的相邻对档; 号表手工按逗号切",
     u"年 %s ⇎ 首末年距 %d ⇎ 倒退 %d 处 ⇎ Obsoletes %d 号 ⇎ 空段 %s ⇎ Updates %d 处 ⇎ 出边为零的份 %s ⇎ ISSN 行 %s ⇎ STD 行 %d" % (
         J(G['years']), G['year_span'], G['year_inversions'], G['obs_total'],
         J(G['obs_blank_segs']), G['upd_total'], str(G['lineage_no_edge']), J(G['issn_hdr']), G['std_n']),
     u"谱系账 %d ⇎ 被 Updates 指向者恰也被 Obsoletes: 判定 %d ⇎ 库内命中 %s ⇎ 编号标题三式 两点 %s ⇎ 一点 %s ⇎ 无点 %s ⇎ 顶格⇎缩进差 %s。" % (
         G['lineage_close'], G['upd_target_obsoleted'][2], J(G['obs_target_in_lib']),
         J(G['hdr_dot2sp']), J(G['hdr_dot1sp']), J(G['hdr_nodot']), J(G['hdr_indent_minus_tight']))),
    (u"段窗⇎行号尺",
     u"段界在摘壳折平面按字面针 `search(hay, frm)` 定位, 偏移映回原行走 `bisect_right`; 复核针拿行号回原文件取那一行逐枚自验",
     u"14 段起行 %s ⇎ 止行 %s ⇎ 行数 %s ⇎ 字符 %s ⇎ 词 %s ⇎ 五段主答句合计 %d 字符 ⇎ %d 词 ⇎ %d 行" % (
         J(G['blk_lo']), J(G['blk_hi']), J(G['blk_rows']), J(G['blk_chars']), J(G['blk_words']),
         G['blk_five_chars'], G['blk_five_words'], G['blk_five_rows']),
     u"行针 %d 枚自验 %d(判定 %d) ⇎ 反向把整段拿到首字那一行验 %d 枚 ⇎ 答句跨行 %s ⇎ 每行词数 %s ⇎ 一行读全只有 9110(判定 %d) ⇎ 片段序列减非空行 %s=壳行 %s。" % (
         G['pin_rt_n'], G['pin_rt_ok'], G['pin_rt_all'], G['pin_wrongline'],
         J(G['ans_span']), J(G['blk_words_per_row']), G['one_line_answer_only_9110'],
         J(G['pp_gap_rows']), J(G['pp_shell_nonblank']))),
    (u"锚归属双轨⇎编码区",
     u"引文对由手写配对扫描取自编码区(代一条 `findall`); 一轨对锚平面逐行 membership ⇎ 一轨对整篇归一串 substring, 两式同判才计数",
     u"引文 %d 处 ⇎ 去重 %d 串 ⇎ 单源 %d ⇎ 跨源 %d ⇎ 五源同现 %d ⇎ 读不到 %d ⇎ 判词 %d 条 ⇎ 编码区 %d 非换行字符" % (
         G['anchor_total'], G['anchor_distinct'], G['anchor_single'], G['anchor_cross'],
         G['anchor_all5'], G['anchor_err'], G['checks'], G['enc_chars']),
     u"本遍独立复核 %d/%d 处全在本遍锚平面 ⇎ 同串在两处印的歧义 %d 枚(只进本注不进 T1) ⇎ 五份全为纯文本面, 所以门槛对面只有一把尺: 原样字节, 锚一律抛回原文件那一行。" % (
         len([1 for t, x in CITES if x in ANSET[IDX[t]]]), G['anchor_total'], CH[u'anchor_ambiguous']))
]
for _a, _b, _c, _d in rows:
    A(u"| %s | %s | %s | %s |" % (cell(_a), cell(_b), cell(_c), cell(_d)))
A(u"")
A(u"五份文书对同一个问题的五种答法, 在本遍全部落到可复算的四把尺上(义务词式 ⇎ 施事者 ⇎ 答句跨几行 ⇎ 答句住在节内还是节外)。"
  u" 2616 给了禁令却不写在定义节里: §9.1.2 只给定义(节窗内 %d 枚), “能不能自动重来”的三枚判词全在别处——节窗档 %d 枚 ⇎ 摘壳档"
  u" %d 枚, 三枚一律记进节外账(%d); 判词印在第 %d 行, 节头正文行在第 %d 行, 相距 %d 行, 判词在节头之上, 而且它自己就把读者指"
  u" 回去: %s。全文两处指向 §9.1.2(%s), 后一处就是判词行。 7231 把同一条款搬进 §4.2.2, 窗幅从 %d 字符扩到 %d 字符 ⇎ 句数 %d"
  u" ⇎ %d, 却一个义务词也不给(节窗内 %d 枚 ⇎ 2616 %d 枚 ⇎ 9110 %d 枚): 它给的是机制句 %s。 9110 反向收成一处——名下 %d 枚内容针"
  u" 全在 §9.2.2 之内(节外 %d), 两份禁令点名两个施事者, 主答句压到 %d 词独占 %d 行, 是全库唯一能在一行读全的答句(判定 %d)。"
  u" 中间两份干脆换题: 6585 不答“能不能重来”, automat×retry 六式 %d 枚 ⇎ idempotent 一词 %d 枚, 只给一个码加一个头加一个例子,"
  u" 并自认没定义怎么数请求: %s; 8470 一句给全三档义务: %s。" % (
      G['defin_in_sec'], G['v_in_sec'], G['v_in_sh'], G['v_sh_no_sec'], G['ln_verdict_2616'],
      G['sec_body_line'][0], G['verdict_head_gap'],
      QT(u'2616', u'   idempotent (see section 9.1.2). Non-idempotent methods or sequences'),
      str(G['xref_lines_abs']), G['sec_chars'][0], G['sec_chars'][1], G['sec_sents'][0],
      G['sec_sents'][1], G['tone_sec_tot'][1], G['tone_sec_tot'][0], G['tone_sec_tot'][4],
      QT(u'7231', u'   Idempotent methods are distinguished because the request can be'),
      G['k9110_in_sec'], G['k9110_no_sec'], G['ans_words'][4], G['ans_span'][4],
      G['one_line_answer_only_9110'], G['auto_tot_fold'][2], G['idem_str'][2],
      QT(u'6585', u'   Note that this specification does not define how the origin server'),
      QT(u'8470', u'   user agent SHOULD retry automatically, but any retries MUST NOT be')))
A(u"四档口径不是装饰: 全库唯一一枚“只有摘壳档才读得到”的针是 6585 的 428 定义行——逐行档与折平档都读不到, 摘壳档读出 %d 枚且全落在 6585"
  u"(%s), 它被跨页的页壳正好切开; 而摘壳一档"
  u" 一枚也不丢(逐份 %s, 合计 %d)。节窗档对 6585 与 8470 根本不存在, 于是按 -1 登记而不是 0(%s)——口径不存在与读不到是两件事, 这一格若填 0"
  u" 就会把“这两份没有幂等节”误读成“这两份的幂等节里没有答句”。 9110 无分页壳, 所以它的摘壳面与折平面等长(差 %d 字符, 判定 %d),"
  u" 而 2616 名下 %d 枚针里 %d 枚跨行, 逐行档只剩 %d 枚可读——同一句话在四档里的最大落差就在这一份。被 72 列硬换行切开的大写"
  u" 义务词逐份 %s 枚, 其中 9110 的 %d 枚分在 MUST NOT ⇎ SHOULD NOT 两式上(%s): 新版式去掉页壳, 反而切掉更多禁令短语。答句本身"
  u" 从不被页壳切开(%s 枚), 切开答句的是换行而不是分页。" % (
      G['sh_gains'][2], u' ⇎ '.join(str(x) for x in G['sh_gains']), J(G['sh_loses']), sum(G['sh_loses']),
      str(G['sn_sec_docs_scope']),
      G['sh_char_gap'][4], G['sh_equals_fold_for_9110'], G['needles_owned'][0],
      G['fold_minus_strict_own'][0], G['sn_strict_docs'][0], J(G['tone_straddle']),
      G['tone_straddle'][4], str(G['tone_straddle_k'][4]), J(G['ans_page_break'])))
A(u"措辞 ⇎ 单位 ⇎ 码表三层换代都能由在库字节数出来。说法层: automat×retry 六式逐份 %s, 6585 一份零枚而 9110 独占 %d 枚; 裸"
  u" automat* 逐份 %s 枚, 9110 一份的差 %d 枚就是“不在 retry 邻座”的 automatic/automatically(%d 减 %d)——所以“自动化”一词的出现量"
  u" 并不能替“自动重来”作证。单位层: 2616 只写 delta-seconds(%d 枚 ⇎ delay 0 枚), 7231 与 9110 只写 delay-seconds(各 %d ⇎ %d 枚 ⇎"
  u"  delta 全零), 换代净账 %s; 两族在带边界尺与裸串尺上逐枚相等(%s), 没有短数被长数吃进的假阳性。码表层: 定义行 %s 行 ⇎ 族数 %s,"
  u" 7231 比 2616 少两枚(%s 搬去同族分册), 9110 又回到 2616 的同一枚集(判定 %d), 但 428 与 429 在 9110 与两份 HTTP/1.1 里都不定义"
  u" (判定 %d ⇎ %d)——限流那一码住在本库之外的 6585: %s。 8470 一枚也不定义(判定 %d), 它只用“码+括号名”的印法引用(%d 枚,"
  u" 其余四份 %d ⇎ %d ⇎ %d ⇎ %d), 这种印法全库只有它用, 且 %d 枚被换行切在中间: %s。" % (
      J(G['auto_tot_fold']), G['auto_tot_fold'][4], J(G['auto_bare']), G['auto_bare_minus_union'][4],
      G['auto_bare'][4], G['auto_union_fold'][4], G['num'][0][5], G['num'][1][4], G['num'][4][4],
      J(G['num_rename']), J(G['num_sub']), J(G['code_defined_n']), J(G['code_def_fams']),
      u' '.join(G['code_7231_drops']), G['code_set_2616_eq_9110'], G['neither_428_429_in_9110'],
      G['neither_428_429_in_2616'],
      QT(u'6585', u'   The 429 status code indicates that the user has sent too many'),
      G['no_code_def_8470'], G['paren'][3][0], G['paren'][0][0], G['paren'][1][0],
      G['paren'][2][0], G['paren'][4][0], G['paren_straddle'][3],
      QT(u'8470', u'   A 425 (Too Early) status code indicates that the server is unwilling')))
A(u"搬字要挑明单位。 7231 与 9110 是同一份正文的两次排版: 行尺上折叠键共用 %d 条, 其中逐字节同形 %d 条 ⇎ 只因归一而同形 %d 条;"
  u" 同一对换成“原始行枚”是 %d 行(判定 %d: 行枚不少于折叠键), 差 %d 行是同一折叠键在两处各印一次(壳行吃掉 %d 行)。换成句尺, 同"
  u" 一对只剩 %d 句 ⇎ 从行尺到句尺净差 %d 枚——不是矛盾, 是一句由 %d 行摊开; 句尺池 %d 句 ⇎ 分档 %s(共用 1..5 份的句数) ⇎ 容斥 %s 归到并集(判定 %d)。"
  u" 归一因由四桶 %s(两桶为零 ⇎ 两桶有值 %d ⇎ 池内相加账平 %d), 例: %s 与 9110 的同句只差一处空格。最大对的 %d 枚里 %d 枚只属于"
  u" 这一对(搬家的正文), 其余被三份以上共用(模板行); 而 8470·9110 一对 %d 枚里只属这一对 %d ⇎ 更多份共用 %d 枚。两段搬字都是"
  u" 逐字同形: 幂等定义段共头 %d 词 ⇎ 共尾 %d 词 ⇎ 词集账 %d ⇎ 只属 7231 %d ⇎ 只属 9110 %d, 类比句段共头 %d 词 ⇎ 共尾 %d 词;"
  u" 两段在原文件里的行距位移相等(%d ⇎ %d, 差 %d)——搬得整整齐齐。反过来 7231 那句类比句在 2616 摘壳面上 %d 枚 ⇎ 2616 的定义句在"
  u" 7231 折平面上 %d 枚: 换代换了措辞, 不是漏印。 %s 一句在两份里各印一次。" % (
      G['pair_max'], G['pair_max_byte_keys'], G['pair_max_norm_only_keys'], G['pair_max_byte_lines'],
      G['pair_byte_lines_ge_keys'], G['pair_byte_unit_gap'], G['pair_byte_shell_gap'],
      G['s_pair_max'], G['s_ruler_drop_7231_9110'], G['pair_row_per_sent'], G['s_pool_n'],
      str(G['s_pool_tier']), str(G['s_incl']), G['s_union_close'], G['axis_str'], G['axis_str_n'], G['axis_close'],
      QT(u'7231', u'     Accept: text/plain; q=0.5, text/html,'), G['pb_7231_9110'],
      G['only2_7231_9110'], G['pb_8470_9110'], G['only2_8470_9110'], G['multi_8470_9110'],
      G['pre_idem_7231_9110'], G['suf_idem_7231_9110'], G['w_ledger_idem'], G['w_only_7231_idem'],
      G['w_only_9110_idem'], G['pre_like_7231_9110'], G['suf_like_7231_9110'],
      G['idem_shift'], G['like_shift'], G['blk_gap_delta'], G['like_absent_2616'],
      G['defin_absent_7231'],
      QT(u'9110', u'   Like the definition of safe, the idempotent property only applies to')))
A(u"幂等节只在三份文书里存在, 第四遍在这一格上显出两个坑。第一个是目录: 同名标题在 9110 的面上命中 %d 行(目录第 %d 行 ⇎ 正文第"
  u" %d 行), 因为新版式把目录也排成同样的缩进标题; 2616 与 7231 的目录行带点引线与页码, 标题面认不出它(%s), 所以全库命中合计"
  u" %d 行=有节 %d 份各一行正文+那唯一一行目录。第二个是定界: 节尾由下一个同级标题给出(%s), 三份都以标题式收束而没有撞到串尾,"
  u" 而“9.2.3.  Methods and Caching”这一串在 9110 也印两次, 定界必须取不早于节头的那一行, 否则窗宽会算成负数(行距 %s)。 6585 与"
  u" 8470 没有这一节, 节内义务词 ⇎ 节内点名 ⇎ 节内句数三本账对它们全是空集, 不是零集。 9110 的节窗最厚: %d 字符 ⇎ %d 词 ⇎ %d 句"
  u" ⇎ 占摘壳面千分比 %d(2616 %d ⇎ 7231 %d), 同一个问题的答案密度是前两份的两到三倍。" % (
      G['sec_hit_n'][4], G['sec_toc_line'][4], G['sec_body_line'][4],
      QT(u'2616', u'   9.1.2    Idempotent Methods .......................................51'),
      G['sec_hit_tot'], G['sec_found_n'], NJ(G['sec_end_head']), str(G['sec_end_head_gap']),
      G['sec_chars'][4], G['sec_words'][4], G['sec_sents'][4], G['sec_share_permille'][4],
      G['sec_share_permille'][0], G['sec_share_permille'][1]))
A(u"两处在换算法时才显形, 记在这里。其一: 大写尺不能用 `str.isupper()`——它承认非 ASCII 的大写字母, 而第二遍的句界尺只认 ASCII 的"
  u" `[A-Z0-9*<(]`; 9110 面内正有 %d 枚非 ASCII 码位(全在贡献者姓名行), 用 `isupper()` 就会把姓名行切成额外的句, 本遍与第二遍的"
  u" 句池在 9110 上第一拍就对不齐, 改回 ASCII 档后逐份同值。其二: 邻居尺的“重叠”口径要跟着实现走——第二遍的游标 find 每步前进"
  u" 一枚字符, 等价于 lookahead 定位, 本遍若改用非重叠的 `findall` 就会在紧邻重复的形状上少吃(试针 “MUST MUST” 两枚 ⇎“MUSTMUST”"
  u" 一枚都要按 alpha 边界判), 状态码行尺同理: 一条正则若把编号后的空白一并吃掉, “码后必须紧跟空白”这条判据就永远成立, 400 会被"
  u" 当成 4001 的形状多算——本遍第一版就栽在这里。两轨都改到在全库 %s 行上逐行同值才落账, 而这两处对拍本身就是第三档存在的理由。" % (
      G['nonascii'][4], format(sum(G['lines']), u',')))
A(u"### 不可由在库文件判定(只写在这里, 不进判词与门槛)")
A(u"五份文件在 RFC Editor 上的此刻状态(2616 此刻是否仍挂 Historic、6585 与 8470 是否有后续勘误改过这些判词、被 7231 废止的 2616"
  u" 之外的分册现行文本) ⇎ 被 Updates 指向但不在本库的 2817 ⇎ 3864 ⇎ 2818 的正文 ⇎ 现网客户端与代理到底会不会自动重发(规范给的"
  u" 义务词不等于装机行为; 8470 谈的 early data 重放在部署里是否真的发生) ⇎ 429 之外服务器实际怎么数请求(6585 自己就写了没定义)"
  u" ⇎ 镜像页的时间戳与本版号之外的修订 ⇎ 9110 姓名行那 %d 枚非 ASCII 在别的序列化里落成什么——这些都要在库外字节或实时状态, 本库"
  u" 五份文件给不出判据; 在库只给得出抬头里的 Obsoletes ⇎ Updates 清单与面上字节的四档读数。" % G['nonascii'][4])

NEW = u"## ⛓解读注" + NL + NL + NL.join(L2) + NL
_i2 = TT.index(u"## ⛓解读注")
out = TT[:_i2] + NEW
assert out.count(u"## ⛓解读注") == 1
T2 = ENTRY + u'.tmp'
io.open(T2, 'w', encoding='utf-8', newline=NL).write(out)
os.replace(T2, ENTRY)
print(u"⛓解读注 已写入 %s ｜ 表 %d 行 ⇎ 注区 %d 字符 ⇎ 复算 %d 键 ⇎ 不符 %d ⇎ 独有 %d ⇎ 未复算 %d ⇎ "
      u"恒等式 %d/%d ⇎ V 形 %d 条 ⇎ DERIV %d 键 ⇎ 门 %d/%d ⇎ 编码区 %d 字符未动"
      % (ENTRY, len(rows), len(NEW), len(G), len(BAD), len(MISS), len(UNCOVER),
         G['scalar_clos_sum'], G['scalar_clos_n'], len(ZV2), len(DER),
         G['bool_clos_sum'], G['bool_clos_n'], G['enc_chars']))
