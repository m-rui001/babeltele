# -*- coding: utf-8 -*-
# B98 落盘遍(与 _mkB98.py 同进程 exec, 用建条遍自带的 V()/J()/EXPR() 注册器):
# 一枚数字都不手打——正文数字全由 F 现值插值, 派生数走 EXPR 当场把复算式登记进契约;
# 锚一律从 corpus/_atoms98.txt(机械产出的词表)按标签取串, 词表里没有的串即 MISS 报错;
# 落盘前逐条自校: 标签数=锚数 ⇎ 正文无未插值的注册调用 ⇎ 契约每条表达式现算必须回键 ⇎
# 三位以上数字要么在契约里要么在面上(无着落即红)。
import io, json, re

CT_PATH = u'corpus/_b98contract.json'
MD_PATH = u'corpus/babeltele/B98_retry_after_delay_and_who_may_omit.md'
TAGP_ORDER = [u'A', u'B', u'C', u'D', u'E']
ORDI = dict((t, i) for i, t in enumerate(TAGP_ORDER))

ATOMS = []
for _l in io.open(u'corpus/_atoms98.txt', encoding='utf-8'):
    if u'\t' in _l:
        _t, _a = _l.rstrip(u'\n').split(u'\t', 1)
        ATOMS.append((_t, _a))
MISS, USED = [], []


def AN(tg, sub):
    hit = [a for (t, a) in ATOMS if t == tg and sub in a]
    if not hit:
        MISS.append((tg, sub))
        return u'⟦%s⟧⟨?%s?⟩' % (tg, sub)
    USED.append((tg, hit[0]))
    return u'⟦%s⟧⟨%s⟩' % (tg, hit[0])


# 合账类: 值恒为零的面内恒等式, 登记后与正文里的 0 同键(契约 '0' 取全部零式之和)
BODYID = EXPR(0, u"sum([B98V('n_nonempty', i) - B98V('shell_rows', i) - B98V('toc_rows', i)"
              u" - B98V('body_rows', i) for i in range(5)])", u'正文行=非空减壳减目录')
D34 = EXPR(F['face_bytes'][3] - F['face_cp'][3],
           u"B98V('face_bytes', 3) - B98V('face_cp', 3)", u'9110 字节面减字符面')
NNA = EXPR(len(F['nonascii_cp'][3]), u"len(B98V('nonascii_cp', 3))", u'9110 非 ASCII 码位枚数')
NPROBE = EXPR(F['needle_n'] * NSRC, u"B98V('needle_n') * 5", u'判词针×五份=探针次')
RPROBE = EXPR(F['risk_n'] * NSRC, u"B98V('risk_n') * 5", u'风险针×五份=探针次')
NEGOTH = EXPR(sum(x[2] for x in F['neg_excl']),
              u"sum([B98V('neg_excl', i)[2] for i in range(5)])", u'独占针在别家的合计枚数')
RISKFOLD_T = EXPR(sum([sum(r) for r in F['risk_fold']]),
                  u"sum([sum(r) for r in B98V('risk_fold')])", u'风险针折平档命中格总')
RISKROW_T = EXPR(sum([sum(r) for r in F['risk_row']]),
                 u"sum([sum(r) for r in B98V('risk_row')])", u'风险针逐行档命中格总')
RISKSHELL_T = EXPR(sum([sum(r) for r in F['risk_shell']]),
                   u"sum([sum(r) for r in B98V('risk_shell')])", u'风险针摘壳档命中格总')
RISKMK_T = EXPR(sum([sum(r) for r in F['risk_mkfree']]),
                u"sum([sum(r) for r in B98V('risk_mkfree')])", u'风险针去标记档命中格总')
CUTSHELL_T = EXPR(sum(F['risk_cut_shell']), u"sum(B98V('risk_cut_shell'))", u'摘壳刀吃进的针次合计')
CUTROW_T = EXPR(sum(F['risk_cut_row']), u"sum(B98V('risk_cut_row'))", u'硬换行刀吃进的针次合计')
DIFFK_N = EXPR(len(F['pick_diffk']), u"len(B98V('pick_diffk'))", u'与采集遍不符键数')
RED_N = EXPR(len(F['bool_red']), u"len(B98V('bool_red'))", u'布尔门红项数')
GK_N = EXPR(len(F['gate_keys']), u"len(B98V('gate_keys'))", u'布尔门键数')
BLOFF = EXPR(sum([F['win_end'][i] - F['win_start'][i] for i in range(NSRC)]),
             u"sum([B98V('win_end', i) - B98V('win_start', i) for i in range(5)])", u'五扇定义窗行跨度合')
BIGSMALL = EXPR(F['face_bytes'][3] // F['face_bytes'][4],
               u"B98V('face_bytes', 3) // B98V('face_bytes', 4)", u'9110 字节面对 curl 字节面的倍')
LOG2 = EXPR(F['curl_cap_secs'] // F['curl_first_secs'],
            u"B98V('curl_cap_secs') // B98V('curl_first_secs')", u'curl 封顶对起步的倍数')
RA4 = EXPR(sum(F['ra_total']), u"sum(B98V('ra_total'))", u'Retry-After 五面出现合计')

E = []
E.append(u'🧭 同一句“服务器让你多久之后再回来”被五份一手文书各写一遍, 先把面尺摆开(字节 ⇎ 字符 ⇎ 三把行尺): '
         u'字节面 %s ⇎ 字符面 %s——两把尺只在 9110 分开, 差 %s 字节, 因它面上有 %s 枚非 ASCII 码位(含 BOM 与中日韩), '
         u'其余四面字节数=字符数; 行尺三轨同摆: splitlines 档 %s ⇎ split(换行) 档 %s ⇎ 逐字符数换行 %s, '
         u'前两轨之差 %s 恰等于换页符 %s 枚减去「文件以换行收尾」的那一枚(五面 ends_lf 全 %s); '
         u'最长行 %s 码位(三面压在 72, 7231 放到 75, 实现侧 78); '
         u'空行 %s ⇎ 非空行 %s ⇎ 壳行 %s ⇎ 目录行 %s ⇎ 正文行 %s, 四列相减的合账 %s。'
         u'最大的面 9110 是最小面 curl 的 %s 倍, 而答句都落在千字符级的窗内(窗面字符 %s, 窗行跨度合 %s 行)。'
         % (J('face_bytes'), J('face_cp'), D34, NNA, J('n_splitlines'), J('n_splitnl'), J('n_lf'),
            J('splitlines_minus_splitnl'), J('n_ff'), J('ends_lf'), J('maxlen_row'), J('n_blank'),
            J('n_nonempty'), J('shell_rows'), J('toc_rows'), J('body_rows'), BODYID,
            BIGSMALL, J('win_cp'), BLOFF))

E.append(u'📏 “写多久”的答值分三档且互斥: 面上 Retry-After 出现 %s 枚(五面 %s)⇎ 把大小写几种形一起数仍是 %s'
         u'(四形相加只多零枚) ⇎ 按行只数到 %s 行 ⇎ 定义窗内 %s 枚、窗外 %s 枚, 窗内外相加逐格等于总数(差 %s); '
         u'窗内现读的样例秒数 %s——curl 那一面记 %s(哨兵: 它窗内根本没有秒例, 不是零秒), '
         u'同窗现读的分钟数 %s, 面上写明的分钟→秒换算词 %s(6585 与 curl 取不到该词, 记 %s); '
         u'分钟档三面同现 %s ⇎ 小时档只在 6585 一面 %s ⇎ 日期档 %s 三面同现 %s; '
         u'把两例并列那句面上枚数 %s——6585 与 curl 各只演示一档。'
         u'6585 的小时档还能从它窗内那句话推: 面上写着每 %s 请求一小时, 乘上同面读出的每分钟秒数 %s 即得 %s; '
         u'另一条账是 %s 倍于分钟档 %s 得同一枚 %s, 两式各自当场乘、当场除。'
         % (RA4, J('ra_total'), J('ra_caseless'), J('ra_rows'), J('ra_win'), J('ra_out'), J('ra_decomp_diff'),
            J('ex_ra_secs'), V('ex_ra_secs', 4), J('ex_ra_mins'), J('unit_minute_from_doc'),
            V('unit_minute_from_doc', 1), J('nd_retry_after_120'), J('nd_retry_after_3600'),
            AN(u'A', u'Retry-After: Fri, 31 Dec 1999'), J('nd_retry_after_fri_31_dec_1999_23_59_59_gmt'),
            J('two_examples'), V('num_hour_rate'), V('unit_minute_from_doc', 3), V('ex_ra_secs', 1),
            V('ratio_6585_over_120'), V('ex_ra_secs', 2), V('ex_ra_secs', 1)))

E.append(u'⚖ 单位名分流就是版本印记: 秒那一档在 2616 叫 %s(整词面上 %s 枚), 7231 与 9110 改叫 %s(各面 %s 枚), '
         u'6585 与 curl 两名都不出现; 值域写法 %s 由 2616 起、7231/9110 承袭(%s), '
         u'而 "(in decimal)" 这半句只 2616 一面有, 词面在此 %s, 面上 %s 枚; '
         u'ABNF 两式: 2616 的旧式(值以 ":" 引出、以竖线并列)五面 %s 处, 7231/9110 的新式(斜杠选值)五面 %s 处, '
         u'两式各只在自家版本成句——同一值域两种语法方言; '
         u'时刻锚三句互不相弄: 2616 说 %s ⇎ 7231 说 %s ⇎ 9110 说 %s, 三面各一枚而别家零枚; '
         u'HTTP-date 这个词面上 %s 枚、定义窗内(去壳) %s 枚, 6585 两把尺皆零——它不承认日期档; '
         u'"1999" 串面上 %s 枚(2616 的过期样例满天飞), 9110 只有 %s 枚, 差一个量级。'
         % (AN(u'A', u'delta-seconds'), J('nd_delta_seconds'), AN(u'C', u'delay-seconds'), J('nd_delay_seconds'),
            AN(u'A', u'non-negative decimal integer'), J('nd_non_negative_decimal_integer'),
            AN(u'A', u'(in decimal)'), V('nd_in_decimal', 0), J('gram_colon'), J('gram_slash'),
            AN(u'A', u'after the time of the response'), AN(u'C', u'after the response is received'),
            AN(u'D', u'after receiving the response'), J('nd_http_date'), J('hd_win'), J('num_1999'),
            V('num_1999', 3)))

E.append(u'🪜 语气档位: 定义窗内(去壳行)大写规范词枚数 MAY %s ⇎ SHOULD %s ⇎ MUST %s ⇎ ought %s——'
         u'窗内唯一那枚大写 MUST 落在 6585, 而它属于同段的缓存禁存句(不是对 Retry-After 的义务); '
         u'三句成词的强制式 "MUST send / include / generate a Retry-After" 在五面全数零枚(%s ⇎ %s ⇎ %s), '
         u'所以“谁能省掉它”的规范答案是: 四面 RFC 里没有一个 MUST 指向这枚头。'
         u'同一句 MAY 判词换了三个动词: 2616 写 %s(窗内 %s 枚)⇎ 6585 写 %s(%s)⇎ 7231 与 9110 写 %s(%s); '
         u'SHOULD generate 只在 7231/9110 %s, 6585 正面否认义务 %s, 7231 改写为 %s——这句 9110 面上不成形(%s), '
         u'两版虽同族却不互引; 弱化措辞三形: 7231/9110 用 %s 与 %s, 2616 用同义的残句 %s(少一枚 to)。'
         % (J('win_caps_may'), J('win_caps_should'), J('win_caps_must'), J('win_caps_ought'),
            J('nd_must_send_a_retry_after'), J('nd_must_include_a_retry_after'),
            J('nd_must_generate_a_retry_after'),
            AN(u'A', u'MAY be indicated'), V('nd_may_be_indicated_in_a_retry_after', 0),
            AN(u'B', u'MAY include a Retry-After'), V('nd_may_include_a_retry_after', 1),
            AN(u'C', u'MAY send a Retry-After'), J('nd_may_send_a_retry_after'),
            J('nd_should_generate_a_retry_after'), AN(u'B', u'optional; servers cannot be required'),
            AN(u'C', u'does not imply that a server has to use it'),
            J('nd_does_not_imply_that_a_server_has_to_use_it'),
            AN(u'C', u'ought to wait'), AN(u'C', u'is asked to wait'), AN(u'A', u'is asked wait')))

E.append(u'🔁 反向对照: 判词针 %s 枚在五份面上各扫一遍 = 探针 %s 次, 游标 find 环与整串正则两把尺逐枚相符(差 %s); '
         u'独占候选 %s 枚, 逐枚查「本家>0 且其余四家合计=0」, 成立 %s 枚 ⇎ 别家合计 %s 枚——'
         u'即 %s ⇎ %s ⇎ %s 这类句子谁也读不到谁的; '
         u'同宗对照走 7231 ⇎ 9110 两扇定义窗: 窗内句数 %s ⇎ %s, 同句 %s 枚 ⇎ 只 7231 有 %s 枚 ⇎ 只 9110 有 %s 枚 ⇎ '
         u'并集 %s 格, 容斥账(两窗句数相加减并集减同句)%s, 两窗各自的重句数 %s ⇎ %s; '
         u'三面共享的样例句确实同现: %s 各面 %s 枚 ⇎ %s 各面 %s 枚。'
         % (V('needle_n'), NPROBE, V('needle_ruler_diff'), V('neg_n'), V('neg_clean'), NEGOTH,
            AN(u'A', u'delta-seconds'), AN(u'B', u'Retry-After: 3600'), AN(u'D', u'after receiving the response'),
            V('cmp_sents_a'), V('cmp_sents_b'), V('cmp_same'), V('cmp_only_a'), V('cmp_only_b'), V('cmp_union'),
            V('cmp_incl_excl_diff'), V('dup7'), V('dup9'),
            AN(u'A', u'the delay is 2 minutes'), J('nd_the_delay_is_2_minutes'),
            AN(u'A', u'Retry-After: Fri, 31 Dec 1999'),
            J('nd_retry_after_fri_31_dec_1999_23_59_59_gmt')))

E.append(u'🧮 风险针四档(判词到底在哪一档才读得到): 风险针 %s 枚 × 五份 = 探针 %s 次, '
         u'四档命中格总数 逐行档 %s ⇎ 折平档 %s ⇎ 摘壳档 %s ⇎ 去标记档 %s; '
         u'三把刀各吃进: 硬换行(折平读到而逐行读不到)%s 枚次(逐份 %s)⇎ '
         u'摘壳(判词只在壳行才读得到)逐份 %s 枚 ⇎ '
         u'markdown 标记(去标记读到而摘壳读不到)逐份 %s 枚, 即只落 9110 面的 %s 枚; '
         u'摘壳那一刀合计 %s——判词全在正文行里, 壳行不吃新读, 这是本条唯一能由面自身证伪的档位陈述; '
         u'换尺对账: 风险针游标档 ⇎ 正则档差 %s。'
         % (V('risk_n'), RPROBE, RISKROW_T, RISKFOLD_T, RISKSHELL_T, RISKMK_T,
            CUTROW_T, J('risk_cut_row'), J('risk_cut_shell'), J('risk_cut_mk'), V('risk_cut_mk', 3),
            CUTSHELL_T, V('risk_ruler_diff')))

E.append(u'🧱 实现侧把规范留的空档填成状态机: curl 手册说它 %s ⇎ 但 %s, '
         u'默认 %s 秒起步然后逐次翻倍直至封顶 %s 秒 = %s 分钟, 与窗内现读的每分钟秒数 %s 相乘即得; '
         u'封顶对起步的倍数 %s, 那句里逐枚数出的瞬时 HTTP 响应码 %s 枚, 另有 %s 一句(总时长上限); '
         u'正文 %s 字符 ⇎ 定义窗 %s 字符 ⇎ front matter %s 行(连两道 --- 一起算)⇎ 剥掉它之后窗内非空正文 %s 行; '
         u'状态码记法在面上的枚数: 3xx 类 %s ⇎ 413 %s ⇎ 429 %s ⇎ 503 %s——429 只在 6585 成段(%s 枚)与 curl 举例(%s 枚), '
         u'9110 通篇不写 429, 而 503 三面都在(2616 %s ⇎ 7231 %s ⇎ 9110 %s)。'
         % (AN(u'E', u'complies with the Retry-After'), AN(u'E', u'can override the retry delay'),
            V('curl_first_secs'), V('curl_cap_secs'), V('curl_cap_minutes'), V('unit_minute_from_doc', 2),
            LOG2, V('curl_transient_codes'), AN(u'E', u'limit the total retry time'),
            V('curl_body_cp'), V('win_cp', 4), V('curl_fm_rows'), V('curl_head_rows_after_fm'),
            J('n3xx'), J('n413'), J('n429'), J('n503'), V('n429', 1), V('n429', 4),
            V('n503', 0), V('n503', 2), V('n503', 3)))

E.append(u'🧬 谱系与壳: 9110 面上引用旧版 2616 %s 次; 壳行 %s 行 ⇎ 目录行 %s 行(只有 2616 带目录 %s 行), '
         u'换页符 %s 枚而 9110 与 curl 面上为零——2616 面把 %s 枚换页界当行首, splitlines 档就比 split 档净多 %s 行(吃的界减掉「尾换行收尾」的那一枚); '
         u'9110 的表两档: 原面 %s 条 markdown 表 ⇎ 去标记面 %s 条(表是 RFC XML 继承的排版, 不是内容)。'
         % (V('rfcref_2616_in_9110'), J('shell_rows'), J('toc_rows'), V('toc_rows', 0), J('n_ff'),
            V('n_ff', 0), V('splitlines_minus_splitnl', 0), V('tbl_9110_raw'), V('tbl_9110_mkfree')))

E.append(u'🧾 对账与收据: 与采集遍 _pick98 逐键对账 %s 项符 ⇎ %s 项不符(不符键 %s 枚); '
         u'布尔门 %s 枚全绿(红项 %s)——门里含「窗块两把尺同串」「壳档不吃新读」「6585 不写 HTTP-date」'
         u'「6585 通篇无 503」「9110 通篇无 429」这类可失败判词; 恒等式 %s 条逐条归零(样例秒数与分钟换算互推 ⇎ '
         u'RA 四形只多零枚 ⇎ 正文行=非空减壳减目录 ⇎ 独占针标志相加=清数); 现量键 %s 枚(该计数在自计量键落位前取, '
         u'故它本身与恒等式计数 %s 都不在它数内); 判词针 %s 枚 ⇎ 风险针 %s 枚 ⇎ 独占候选 %s 枚。'
         u'ℒ 方法 ⇒ 这道题的隐性知识分四键: ①答案键 120 ⇎ 3600 ⇎ HTTP-date 三档在不同版本里互斥出现, '
         u'分钟/秒/小时/日期四把尺没有一把被写成换算表; ②尺键 窗内(去壳) ⇎ 整面 ⇎ 逐行三把尺数同一枚词给出三个数, '
         u'取哪把决定“服务器是否被要求”; ③档键 判词可读性分四档(逐行/折平/摘壳/去标记), 硬换行与 markdown '
         u'是两把互不相干的刀, 而壳行那把证明为空; ④层键 规范面只给“要么日期要么秒”并把等待算法留给实现, '
         u'curl 面反过来越过规范给出起步/倍增/封顶三个数——每键都是可机检的 count, 零项照占键位。'
         % (V('pick_agree'), V('pick_diff'), DIFFK_N, GK_N, RED_N, V('zid_scan_n'), V('scan_key_n'),
            V('zid_scan_n'), V('needle_n'), V('risk_n'), V('neg_n')))

enc = u'\n\n'.join(E)
assert not MISS, u'锚不在词表: %s' % MISS[:4]
assert enc.count(u'⟦') == enc.count(u'⟨'), (enc.count(u'⟦'), enc.count(u'⟨'))
assert u"V('" not in enc and u'EXPR(' not in enc and u'J(' not in enc, u'正文里有未插值的注册调用'

# —— 契约: 面值→复算式(dump_deriv 已把同值多派生的键折成复合式), 再补 '0' 的合计式 ——
CT = dump_deriv()
assert u'0' not in CT and ZERO, u'零式表异常'
CT[u'0'] = u"sum([%s])" % u','.join(ZERO)
for k, v in DER.items():
    CT.setdefault(k, v)
DER.clear()
DER.update(CT)

# 复算契约用的环境刻意不给 F ⇎ 只给门内也有的东西(B98V ⇎ 内建聚合 ⇎ range),
# 否则本地过、进门后 eval 不出 F 就白搭。
_EVENV = {u'B98V': BB98, u'range': range, u'sum': sum, u'len': len, u'max': max, u'min': min,
          u'abs': abs, u'sorted': sorted, u'round': round}
assert eval(CT[u'0'], _EVENV) == 0, u'零式合计不为零'


def _ck(k, v):
    try:
        got = eval(v, _EVENV)
    except Exception as e:
        return u'%s ⇒ %s (%s)' % (k, v, repr(e)[:50])
    if u'%s' % got != k:
        return u'%s ⇒ %s 现值 %r' % (k, v, got)
    return None


BAD = [x for x in [_ck(k, v) for k, v in CT.items()] if x]
assert not BAD, u'契约现值不符: %s' % BAD[:5]

SRALL = u'!'.join(T)
toks = set(re.findall(u'\\d[\\d,]{2,}', enc))
# 尾巴上的中文句读逗号不算千位分隔(逐数并列时 "1025, " 会被贪婪吃进串), 先剥再查
missing = [t for t in toks
           if t not in CT and t.strip(u',') not in CT and t.strip(u',') not in SRALL]
assert not missing, u'无着落数字: %s' % sorted(missing)[:8]

by_tag = {}
for tg, a in USED:
    by_tag.setdefault(tg, [])
    if a not in by_tag[tg]:
        by_tag[tg].append(a)
orig = []
for tg in TAGP_ORDER:
    if tg not in by_tag:
        continue
    orig.append(u'### ⟦%s⟧ ⟸ %s\n\n' % (tg, PATH[ORDI[tg]]) + u'\n\n'.join(by_tag[tg]))
orig_sec = u'## [[原始语料|ORIGINAL]]\n' + u'\n\n'.join(orig)

n_anchor = sum(len(v) for v in by_tag.values())
head = (u'# B98 Retry-After 该写多久、谁能省掉它: 2616⇎6585⇎7231⇎9110⇎curl 五份一手文书各答一遍 '
        u'120⇎3600⇎HTTP-date, 秒档两名(delta-seconds⇎delay-seconds)⇎成词 MUST 三式全零⇎实现侧 1 秒起步翻倍到 600 秒封顶\n'
        u'src: ' + u' ⇎ '.join(u'%s(%d B)' % (PATH[i], F['face_bytes'][i]) for i in range(NSRC)) +
        u' (五份均一手: RFC 2616 §14.37 ⇎ RFC 6585 的 429/503 段 ⇎ RFC 7231 §7.1.3 ⇎ RFC 9110 §10.2.3 ⇎ '
        u'curl 手册 retry 段; 数字一律从面内现读, 一个都不手填; 本条问“值写多久、谁可省”, 与 B80 的'
        u'“失败请求能否自动重来”、B92 的“重定向最多跳几次”同族语料而不同题; 上游改版后的现值只在本机或站外成立, 不进门槛)\n'
        u'; tags: 答案键(120⇎3600⇎HTTP-date 三档互斥) 尺键(秒⇎分钟⇎小时⇎日期 四把) '
        u'档键(逐行⇎折平⇎摘壳⇎去标记 四档可读性) 层键(规范面⇎实现面) 哨兵键(-1=该面窗内无秒例) '
        u'反向对照键(独占针⇎7231/9110 句集容斥) 锚归属由正文现推 闭合账 标量档 清单档\n')

md = head + orig_sec + u'\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n'
io.open(MD_PATH, 'w', encoding='utf-8', newline=u'\n').write(md)
io.open(CT_PATH, 'w', encoding='utf-8', newline=u'\n').write(
    json.dumps(CT, ensure_ascii=False, indent=1, sort_keys=True))
print(u'B98 落盘: 编码区 %d 字符 ⇎ 原文区锚 %d 枚(正文标签 %d 枚) ⇎ 契约 %d 键全可复算 ⇎ 零式 %d 条并入 '
      u'⇎ 三面共享针 %d ⇎ 无着落 0'
      % (len(enc), n_anchor, enc.count(u'⟦'), len(CT), len(ZERO), len(toks)))
