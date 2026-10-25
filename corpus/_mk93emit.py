# -*- coding: utf-8 -*-
# B93 落盘遍(与 _mkB93.py 同进程 exec, 用建条遍自带的 V()/EXPR() 注册器):
# 一枚数字都不手打——正文数字全由 F 现值插值, 派生数走 EXPR 当场把复算式登记进契约;
# 锚一律从 corpus/_atoms93.txt(机械产出的词表)按标签取串, 词表里没有的串即 MISS 报错;
# 落盘前逐条自校: 标签数=锚数 ⇎ 正文无未插值的注册调用 ⇎ 契约每条表达式现算必须回键 ⇎
# 三位以上数字要么在契约里要么在面上(无着落即红)。
import io, json, re

CT_PATH = u'corpus/_b93contract.json'
MD_PATH = u'corpus/babeltele/B93_ipv6_dad_probe_count_and_retrans_timer_five_answers.md'
TAGP_ORDER = [u'A', u'B', u'C', u'D', u'E']
ORDI = dict((t, i) for i, t in enumerate(TAGP_ORDER))

ATOMS = []
for _l in io.open(u'corpus/_atoms93.txt', encoding='utf-8'):
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


NDL = F['needle_n']
OI = dict((w, k) for k, w in enumerate(OB))
FI = dict((w, k) for k, w in enumerate(NAMES))
SI = dict((w, k) for k, w in enumerate(F['shape_lbls']))
RLK = F['sysctl_rel_keys']


def VC(name, a, b, note=u''):
    """二维表逐格登记(值必须是标量)。"""
    return EXPR(F[name][a][b], u"B93V('%s', %d)[%d]" % (name, a, b),
                note or u'%s·%s·%s' % (name, LBL[a], LBL[b]))


def JR(name, k, note=u''):
    """某枚名/词在一把尺上的五份读数。"""
    return u' ⇎ '.join(VC(name, i, k, u'%s·%s·%s' % (note or name, LBL[i], NAMES[k]))
                       for i in range(NSRC))


def N4V(k, i, t, note=u''):
    return EXPR(F['needles4'][k][i][t], u"B93V('needles4', %d)[%d][%d]" % (k, i, t),
                note or u'针%d·%s·档%d' % (k, LBL[i], t))


def TTL(i, t, note=u''):
    """一档在一份面上的针命中总(逐枚相加, 门内复算同式)。"""
    return EXPR(sum([F['needles4'][k][i][t] for k in range(NDL)]),
                u"sum([B93V('needles4', k)[%d][%d] for k in range(%d)])" % (i, t, NDL),
                note or u'针合计·%s·档%d' % (LBL[i], t))


def TTA(t, note=u''):
    return EXPR(sum([F['needles4'][k][i][t] for k in range(NDL) for i in range(NSRC)]),
                u"sum([sum(B93V('needles4', k)[i][%d]) for k in range(%d) for i in range(5)])" % (t, NDL),
                note or u'针合计·全档%d' % (t))


SH = lambda a, b: EXPR(F['win_census'][a][b], u"B93V('win_census', %d)[%d]" % (a, b),
                       u'窗%s·列%d' % (F['win_census'][a][2][:20], b))
SLOTN = lambda tg, note=u'': EXPR(F['default_slot_n'][tg],
                                  u"len(B93V('default_slots')['%s'])" % tg, note or u'值位·%s' % tg)


def SLOTKIND(tg):
    return EXPR(len(F['default_slot_kinds'][tg]),
                u"len(set([z[1] for z in B93V('default_slots')['%s']]))" % tg, u'值位形状种·%s' % tg)


PROBES = EXPR(NDL * NSRC, u"B93V('needle_n') * 5", u'针×五份=探针次')
CONSTN = EXPR(len(F['const_rows']), u"len(B93V('const_rows'))", u'§10 窗内常量行')
CONSTDN = EXPR(len(F['const_rows_doc']), u"len(B93V('const_rows_doc'))", u'全篇常量行')
RELKEY = EXPR(len(RLK), u"len(B93V('sysctl_rel_keys'))", u'sysctl 相关键')
NUMLESS = EXPR(len(F['win_numless_with_var']), u"len(B93V('win_numless_with_var'))", u'只变量无严轨的窗')
WINSHELL = EXPR(sum([z[17] for z in F['win_census']]), u"sum([B93V('win_census', k)[17] for k in range(5)*0+range(%d)])" % len(F['win_census']), u'窗内混进的壳行合计')
KINDN = EXPR(len(F['const_unit_kinds']), u"len(B93V('const_unit_kinds'))", u'§10 单位口径种')
KEYSEC = EXPR(len(F['unit_in_keyname'][4]), u"len(B93V('unit_in_keyname', 4))", u'sysd 键名带单位')
KEYZERO = EXPR(sum([len(x) for x in F['unit_in_keyname'][:4]]),
               u"sum([len(B93V('unit_in_keyname', i)) for i in range(4)])", u'另四面键名带单位')
NOVAL3 = EXPR(len([k for k in RLK if F['sysctl_defaults'][k][0] is None]),
              u"len([k for k in B93V('sysctl_rel_keys') if B93V('sysctl_defaults')[k][0] is None])",
              u'逐行档读不到默认值的键')
FOLD3 = EXPR(len([k for k in RLK if u'Defaults to 3' in F['sysctl_rel_body'][k]]),
             u"len([k for k in B93V('sysctl_rel_keys') if 'Defaults to 3' in B93V('sysctl_rel_body')[k]])",
             u'整段档读得到 Defaults to 3 的键')
SLOTALL = EXPR(F['default_slot_all'], u"sum([len(B93V('default_slots')[x]) for x in B93V('default_slots')])",
               u'值位条数合计')
PINN = EXPR(len(F['pin_lines']), u"len(B93V('pin_lines'))", u'锚定行条目数')
ONLY1 = EXPR(len([x for x in F['needle_src'] if len(x) == 1]),
             u"len([x for x in B93V('needle_src') if len(x) == 1])", u'摘壳档只一面读到的针')
ONLY0 = EXPR(len([x for x in F['needle_src'] if len(x) == 0]),
             u"len([x for x in B93V('needle_src') if len(x) == 0])", u'摘壳档一面也不读到的针')
DEHYT = EXPR(sum([len(x) for x in F['needle_src_dehy']]),
             u"sum([len(x) for x in B93V('needle_src_dehy')])", u'去连字档命中面次合计')
NACPT = EXPR(len(F['nonascii'][4]), u"len(B93V('nonascii', 4))", u'sysd 非 ASCII 码位种类')
RLDIFF = EXPR(sum(F['row_ledger']), u"sum(B93V('row_ledger'))", u'空行+非空行−总行 合计')
SBLDIFF = EXPR(sum([F['shell_lines'][i] + F['body_lines'][i] - F['splitnl'][i] for i in range(NSRC)]),
               u"sum([B93V('shell_lines', i)+B93V('body_lines', i)-B93V('splitnl', i) for i in range(5)])",
               u'壳行+正文行−总行 合计')
SHL = EXPR(sum(F['shell_led']), u"sum(B93V('shell_led'))", u'壳账容斥合计')
FFL = EXPR(sum(F['lines_ruler_diff']), u"sum(B93V('lines_ruler_diff'))", u'两把行尺对账合计')
OBFOLD = EXPR(sum([sum(x) for x in F['ob_fold']]), u"sum([sum(B93V('ob_fold', i)) for i in range(5)])",
              u'折平档义务词合计')
OBLINE = EXPR(sum([sum(x) for x in F['ob_line']]), u"sum([sum(B93V('ob_line', i)) for i in range(5)])",
              u'逐行档义务词合计')
OBWT = EXPR(sum(F['ob_wrap']), u"sum(B93V('ob_wrap'))", u'义务词跨行涨量合计')
CONVT = EXPR(len(F['unit_conv']), u"len(B93V('unit_conv'))", u'数值×时长单位组')
CONVVAL = EXPR(len(F['conv_vals']), u"len(B93V('conv_vals'))", u'折秒后去重值')
GLUED = EXPR(len([1 for x in F['ref_only_glued'][3]]), u"len(B93V('ref_only_glued', 3))", u'sysctl 只粘连的引用')
GLUEDD = EXPR(len([1 for x in F['ref_only_glued'][4]]), u"len(B93V('ref_only_glued', 4))", u'sysd 只粘连的引用')
DUALN = EXPR(len(F['dual_unit_lines']), u"len(B93V('dual_unit_lines'))", u'面内自证双单位行')
IMPLN = EXPR(len(F['dual_implicit_lines']), u"len(B93V('dual_implicit_lines'))", u'隐式外单位行')
STRICTW = u"sum([B93V('win_census', k)[5] for k in range(%d)])" % len(F['win_census'])
STRICTWV = EXPR(sum([z[5] for z in F['win_census']]), STRICTW, u'窗内严轨合计')
DIGEAT = EXPR(F['win_dig_eaten'], u"B93V('win_dig_eaten')", u'摘壳吃掉的窗内数字枚')
DIFFK_N = EXPR(len(F['pick_diffk']), u"len(B93V('pick_diffk'))", u'与采集遍不符键数')
RED_N = EXPR(len(F['bool_red']), u"len(B93V('bool_red'))", u'布尔门红项数')
DIGH = EXPR(sum([z[0] for z in F['dig_all']]), u"sum([B93V('dig_all', i)[0] for i in range(5)])", u'五面数字普查总枚')
DIGN = EXPR(sum(F['dig_ipv_noise']), u"sum(B93V('dig_ipv_noise'))", u'其中 IP 版本号数字')

E = []
E.append(u'🧭 同一件“重复地址检测要试几次、每次隔多久”被五份一手文书各答一遍, 先把面尺摆开(字节 ⇎ 码位 ⇎ 四把行尺): '
         u'字节面 %s ⇎ 码位面 %s——前四面两把尺同值, 只在末一份(网页剥下来的那份)分开, 逐份差 %s(全在那一面, %s 枚), '
         u'那里非 ASCII 码位 %s 枚 ⇎ 去重 %s 种 ⇎ 另四面一枚也没有; 行尺四轨同摆: splitlines 档 %s ⇎ split(换行) 档 %s ⇎ '
         u'逐字符数换行 %s ⇎ readlines 档 %s: 第一轨比第二轨多出的枚数逐份恰等于「换页符紧跟换行」减「面以换行收尾」(合账 %s), '
         u'readlines 补回尾换行也合账(%s); 换页符只在三份 RFC 里 %s ⇎ 非换行的其他界符 %s(与换页符逐份同数, 即界符族里除换行只剩换页) ⇎ '
         u'回车五面 %s ⇎ 五面皆以换行收尾 %s; 最长行两把尺(切片求长 ⇎ 逐字符扫长)逐份同值 %s: 前三份卡在 %s 列硬限 ⇎ sysctl %s ⇎ '
         u'sysd 那份一行最长 %s 码位(它整篇被压成少数长行); 空行 %s ⇎ 非空行 %s ⇎ 壳行 %s ⇎ 剥壳正文行 %s: 前两者相加回总行(合账 %s), '
         u'后两者相加也回总行(合账 %s), 而壳账容斥(七形谓词之和减去一行命中两形的重数)逐份归零合计 %s。'
         % (J('bytes'), J('cp'), J('utf8_extra'), V('utf8_extra', 4), V('na_total', 4), NACPT,
            J('splitlines'), J('splitnl'), J('n_lf'), J('readlines'), FFL, V('read_vs_split', 0),
            J('ff'), J('othsep'), J('n_cr'), J('trailing_nl'), J('maxlen'), V('maxlen', 0), V('maxlen', 3),
            V('maxlen', 4), J('blank'), J('nonblank'), J('shell_lines'), J('body_lines'),
            RLDIFF, SBLDIFF, SHL))

E.append(u'📏 五把答尺互不译, 得当场对齐: 4862 把次数写成变量而不写成数——它通篇印 %s 枚「%s」, 值位上唯一一句是「%s」, '
         u'间隔写作「%s」(单位词在句里, 数值交给邻份); 所以它自己那份“数字×时长单位”严轨读数 %s 枚 ⇎ §5.4 整节窗内 %s 枚, '
         u'窗内只剩变量名 %s ⇎ 全篇数字 %s 枚(那些是编号与文献号); 它提间隔用驼峰名 %s 次 ⇎ 一次也不印常量名 %s。'
         u'4861 才把数印出来: 表行「%s」= %s ⇎「%s」= %s ⇎「%s」= %s, §10 窗内常量行 %s 行 ⇎ 全篇同正则 %s 行。'
         u'4429 一个数也不给(严轨 %s 枚), 它只说「%s」, 并把次数推回上一代文书:「%s」——它点名的是 2462 的变量, 面内该形 %s 枚。'
         u'sysctl 把同一件事收进内核键: 键块 %s 枚 ⇎ 相关键 %s 枚 ⇎ 默认位上给数的 %s 枚, 全是裸数(「%s」的默认位是 %s), '
         u'单位写在描述里而不写在数上(「%s」)。'
         u'systemd.network 最绕: IPv6 那两个选项都不填数而交回内核——「%s」⇎「%s」; 唯独 IPv4 那项给足: 「%s」⇎ 值域「%s」⇎ '
         u'随机区间「%s」, 而 IPv6 的探测次数选项在该面只出现 %s 次。'
         % (V('name_raw', 0, FI[u'DupAddrDetectTransmits']),
            AN(u'A', u'The number of consecutive Neighbor Solicitation messages sent while performing Duplicate Address'),
            AN(u'A', u'Default: 1, but may be overridden by a link-type specific value'),
            AN(u'A', u'each separated by RetransTimer milliseconds'),
            V('strict_n', 0), SH(0, 5), V('win_census', 0)[6], SH(0, 7),
            V('name_raw', 0, FI[u'RetransTimer']), V('name_raw', 0, FI[u'RETRANS_TIMER']),
            AN(u'B', u'RETRANS_TIMER 1,000 milliseconds'), VC('name_raw', 1, FI[u'RETRANS_TIMER']),
            AN(u'B', u'MAX_MULTICAST_SOLICIT 3 transmissions'), VC('name_raw', 1, FI[u'MAX_MULTICAST_SOLICIT']),
            AN(u'B', u'MAX_RTR_SOLICITATION_DELAY 1 second'), VC('name_raw', 1, FI[u'MAX_RTR_SOLICITATION_DELAY']),
            CONSTN, CONSTDN,
            V('strict_n', 2),
            AN(u'C', u'It is not sufficient to merely reduce RetransTimer in order to reduce'),
            AN(u'C', u'reduced by increasing the RFC 2462 DupAddrDetectTransmits variable to'),
            V('name_raw', 2, FI[u'DupAddrDetectTransmits']),
            V('sysctl_keys'), RELKEY, V('sysctl_rel_num'),
            AN(u'D', u'dad_transmits - INTEGER'),
            AN(u'D', u'1: Enable DAD (default)'),
            AN(u'D', u'The amount of Duplicate Address Detection probes to send'),
            AN(u'E', u'probes to send. When unset, the kernel\'s default will be'),
            AN(u'E', u'A value of zero is ignored and the kernel\'s current'),
            AN(u'E', u'If unset, defaults to 200 milliseconds'),
            AN(u'E', u'Must be a value between 1 millisecond and 60 seconds'),
            AN(u'E', u'randomized time between 57% (4/7) and 100% of the given value'),
            V('name_raw', 4, FI[u'IPv6DuplicateAddressDetection'])))

E.append(u'⚖ 义务词两把尺: 逐行大写档 ⇎ 全篇折平档。MUST 逐行 %s ⇎ 折平 %s ⇎ MUST NOT 逐行 %s ⇎ 折平 %s ⇎ '
         u'SHOULD 逐行 %s ⇎ 折平 %s: 两档总量 %s ⇎ %s, 涨出的 %s 枚次逐份为 %s(4862 在 MUST NOT 一格 %s→%s, '
         u'4861 在 MUST NOT %s→%s 与 MUST NOT be %s→%s 两格), 即锚身被硬换行劈到两行, 取哪一档决定这句话读不读得到。'
         u'指到这件事头上的强制式只有一句: 「%s」(4862 全篇 MUST %s 枚 ⇎ 4429 %s 枚 ⇎ sysctl %s 枚 ⇎ sysd %s 枚); '
         u'sysd 那一面通篇没有大写义务词(%s 枚) ⇎ 却有小写 must/should/may %s 枚(全份大写形 %s 枚 ⇎ 大小写不分合计 %s 枚)——'
         u'手册体裁把规范语气降成说明语气。另: 重叠尺与不重叠尺对同一批义务词同数(逐格差合计 %s), '
         u'而面内双空格被折平吃掉的枚数逐份 %s——同一件事在折平前后是两个数。'
         % (JFW('ob_line', OI[u'MUST']) if False else u' ⇎ '.join([VC('ob_line', i, OI[u'MUST'], u'MUST 行·%s' % LBL[i]) for i in range(NSRC)]),
            u' ⇎ '.join([VC('ob_fold', i, OI[u'MUST'], u'MUST 折·%s' % LBL[i]) for i in range(NSRC)]),
            u' ⇎ '.join([VC('ob_line', i, OI[u'MUST NOT'], u'MUST NOT 行·%s' % LBL[i]) for i in range(NSRC)]),
            u' ⇎ '.join([VC('ob_fold', i, OI[u'MUST NOT'], u'MUST NOT 折·%s' % LBL[i]) for i in range(NSRC)]),
            u' ⇎ '.join([VC('ob_line', i, OI[u'SHOULD'], u'SHOULD 行·%s' % LBL[i]) for i in range(NSRC)]),
            u' ⇎ '.join([VC('ob_fold', i, OI[u'SHOULD'], u'SHOULD 折·%s' % LBL[i]) for i in range(NSRC)]),
            OBLINE, OBFOLD, OBWT, u' ⇎ '.join([EXPR(F['ob_wrap2'][i], u"B93V('ob_wrap2', %d)" % i, u'涨量·%s' % LBL[i]) for i in range(NSRC)]),
            VC('ob_line', 0, OI[u'MUST NOT'], u'MUST NOT 行·4862'), VC('ob_fold', 0, OI[u'MUST NOT'], u'MUST NOT 折·4862'),
            VC('ob_line', 1, OI[u'MUST NOT'], u'MUST NOT 行·4861'), VC('ob_fold', 1, OI[u'MUST NOT'], u'MUST NOT 折·4861'),
            VC('ob_line', 1, OI[u'MUST NOT be'], u'MUST NOT be 行·4861'), VC('ob_fold', 1, OI[u'MUST NOT be'], u'MUST NOT be 折·4861'),
            AN(u'A', u'Duplicate Address Detection MUST be performed on all unicast'),
            VC('ob_line', 0, OI[u'MUST'], u'MUST 行·4862'), VC('ob_line', 2, OI[u'MUST'], u'MUST 行·4429'),
            VC('ob_line', 3, OI[u'MUST'], u'MUST 行·sysctl'), VC('ob_line', 4, OI[u'MUST'], u'MUST 行·sysd'),
            V('kw_caps', 4), V('kw_low_only', 4), V('kw_caps', 4), V('kw_all', 4),
            EXPR(sum([abs(x) for x in F['ob_ruler_diff']]), u"sum([abs(B93V('ob_ruler_diff', i)) for i in range(%d)])" % len(F['ob_ruler_diff']), u'两把出现尺分歧合计'),
            J('dbl_space_eaten')))

E.append(u'🪜 参数名三把尺(字面 ⇎ 忽略大小写 ⇎ 下划线折成空格再取词界): 驼峰名 %s 在三把尺上逐份 %s ⇎ %s ⇎ %s——'
         u'第三把尺在 4862 多读出 %s 枚、在 4861 少读出 %s 枚, 因为它把下划线族的形也算进同一串; '
         u'同族下划线名 %s 五份只 sysctl 一家 %s 枚 ⇎ 名族 %s 枚里 %s 枚五份一枚也不出(%s ⇎ %s ⇎ %s, 那是别家实现的拼写, 不进这五份面)。'
         u'名与单位的落位也分家: sysd 把秒写进键名(%s 枚带 Sec/NSec 后缀的键形, 例如 %s ⇎ %s)⇎ 另四面合计 %s 枚; '
         u'4861 把单位写在表行的第三列(%s 形 %s 枚 ⇎ %s 形 %s 枚 ⇎ %s 形 %s 枚 ⇎ 无量纲 %s 枚, 同表并排共 %s 种口径); '
         u'4862 则把单位留在散文里跟着变量名走(「%s」)。'
         % (NAMES[FI[u'DupAddrDetectTransmits']], JR('name_raw', FI[u'DupAddrDetectTransmits'], u'字面'),
            JR('name_ci', FI[u'DupAddrDetectTransmits'], u'忽略大小写'),
            JR('name_norm', FI[u'DupAddrDetectTransmits'], u'折形词界'),
            VC('name_norm', 0, FI[u'DupAddrDetectTransmits'], u'折形·4862'),
            VC('name_norm', 1, FI[u'DupAddrDetectTransmits'], u'折形·4861'),
            NAMES[FI[u'dad_transmits']], V('name_raw', 3, FI[u'dad_transmits']), V('name_n'),
            EXPR(len(F['name_absent']), u"len(B93V('name_absent'))", u'一枚不出的名数'),
            F['name_absent'][0], F['name_absent'][1], F['name_absent'][2],
            KEYSEC, NAMES[FI[u'IPv6RetransmissionTimeSec']], NAMES[FI[u'IPv4DuplicateAddressDetectionTimeoutSec']],
            KEYZERO,
            F['const_unit_kinds'][0], V('const_n_ms'), F['const_unit_kinds'][2], V('const_n_sec'),
            F['const_unit_kinds'][3], V('const_n_tr'), V('const_n_dim'), KINDN,
            AN(u'A', u'within RetransTimer milliseconds after having sent DupAddrDetectTransmits')))

E.append(u'🔁 反向对照: 判词针 %s 枚在五份面各扫一遍 = 探针 %s 次, 四档同摆(逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 摘壳去连字): '
         u'摘壳档合计 %s ⇎ 折平档 %s ⇎ 逐行档 %s ⇎ 去连字档 %s; 折平比逐行多读 %s 枚次 ⇎ 落在 %s 枚针上(逐份涨量 %s), '
         u'例如「%s」在 4862 逐行档 %s ⇎ 折平档 %s; 「%s」在 sysd 同样只在折平档读得到(%s ⇎ %s)。'
         u'去连字档比摘壳档多读 %s 枚次, 其中 %s 枚针只在去连字档读得到(它们的锚身在连字符处断词); '
         u'独占账: 摘壳档只在一面读到的针 %s 枚 ⇎ 一面也不读到的 %s 枚(后者全靠去连字档); '
         u'锚定行 %s 条里由去连字档定位的 %s 条 ⇎ 不同针 %s 枚(=针数减去只在他档现身的)。'
         % (V('needle_n'), PROBES, TTA(2), TTA(1), TTA(0), TTA(3),
            EXPR(TTA_V(1) - TTA_V(0), u"sum([sum(B93V('needles4', k)[i][1]) for k in range(%d) for i in range(5)]) - sum([sum(B93V('needles4', k)[i][0]) for k in range(%d) for i in range(5)])" % (NDL, NDL), u'折平比逐行多读'),
            V('needle_wrap_kinds'),
            u' ⇎ '.join([EXPR(F['ob_wrap2'][i], u"B93V('ob_wrap2', %d)" % i, u'针涨量·%s' % LBL[i]) for i in range(NSRC)]),
            AN(u'A', u'The number of consecutive Neighbor Solicitation messages sent while performing Duplicate Address'),
            N4V(0, 0, 0, u'针0·4862·逐行'), N4V(0, 0, 1, u'针0·4862·折平'),
            AN(u'E', u'Must be a value between 1 millisecond and 60 seconds'),
            N4V(40, 4, 0, u'针40·sysd·逐行'), N4V(40, 4, 1, u'针40·sysd·折平'),
            EXPR(TTA_V(3) - TTA_V(2), u"sum([sum(B93V('needles4', k)[i][3]) for k in range(%d) for i in range(5)]) - sum([sum(B93V('needles4', k)[i][2]) for k in range(%d) for i in range(5)])" % (NDL, NDL), u'去连字比摘壳多读'),
            V('needle_dehy_kinds'), ONLY1, ONLY0, PINN, V('pin_dh2'), V('pin_kinds')))

E.append(u'🧢 默认值的句式与值位形状: 十形标记逐份枚数 %s —— 4862 只用一形(%s 枚「%s」⇎ %s 形并用共 %s 枚), '
         u'4861 用 %s 枚 Default: ⇎ 1 枚 by default; sysctl 十形全用(%s 枚 Default: ⇎ %s 枚 Default : ⇎ %s 枚 Default value is ⇎ '
         u'%s 枚 Functional default: ⇎ %s 枚 (default) ⇎ %s 枚 Defaults to ⇎ %s 枚 By default ⇎ %s 枚 by default); '
         u'sysd 反过来只认动词形(%s 枚 Defaults to ⇎ %s 枚 defaults to ⇎ 零枚 Default:)。'
         u'值位上的形状种数: 4862 %s 种 ⇎ 4861 %s 种 ⇎ 4429 %s 种 ⇎ sysctl %s 种 ⇎ sysd %s 种, 全库值位 %s 行; '
         u'带括注的「Default: n (…」」只有 sysctl 印 %s 处。'
         u'同一份 sysctl 内部两档还打架: 相关键 %s 枚里逐行档一个默认值也读不到的 %s 枚(键 %s), 它的整段折平面却明明写着 Defaults to 3(%s 枚键命中)——'
         u'因为那句被硬换行劈成 “Defaults” ⇎ “to 3.” 两行。4429 整份 %s 枚默认句式也不用: 它只批评别人的默认值。'
         % (u' ⇎ '.join([EXPR(F['shape_n'][i][SI[u'Default:']], u"B93V('shape_n', %d)[%d]" % (i, SI[u'Default:']), u'Default:·%s' % LBL[i]) for i in range(NSRC)]),
            V('shape_face_kinds', 0), AN(u'A', u'Default: 1, but may be overridden by a link-type specific value'),
            V('shape_face_kinds', 3), SLOTN(u'sysctl'),
            V('shape_n', 1, SI[u'Default:']),
            V('shape_n', 3, SI[u'Default:']), V('shape_n', 3, SI[u'Default :']), V('shape_n', 3, SI[u'Default value']),
            V('shape_n', 3, SI[u'Functional default:']), V('shape_n', 3, SI[u'(default)']), V('shape_n', 3, SI[u'Defaults to']),
            V('shape_n', 3, SI[u'By default']), V('shape_n', 3, SI[u'by default']),
            V('shape_n', 4, SI[u'Defaults to']), V('shape_n', 4, SI[u'defaults to']),
            SLOTKIND(u'4862'), SLOTKIND(u'4861'), SLOTKIND(u'4429'), SLOTKIND(u'sysctl'), SLOTKIND(u'sysd'), SLOTALL,
            V('default_gloss', 3), RELKEY, NOVAL3, NAMES[FI[u'mcast_solicit']], FOLD3,
            EXPR(sum(F['shape_n'][2]), u"sum(B93V('shape_n', 2))", u'4429 默认句式合计')))

E.append(u'🧱 “这一段”怎么定界: 五种谓词并排(节号 ⇎ 段落 ⇎ 标签行 ⇎ 键行 ⇎ 选项行), 窗共 %s 个, 谓词族 %s 种; '
         u'窗内严轨(数字×时长单位)合计 %s 枚 ⇎ 摘壳后 %s 枚 ⇎ 被壳吃掉的 %s 枚, 而窗内数字合计 %s 枚 ⇎ 摘壳后 %s 枚(壳行里全是编号与页码); '
         u'只印变量名不印数的窗 %s 个: %s ⇎ %s ⇎ %s(节级窗里 %s 枚变量 ⇎ 严轨 %s 枚)。'
         u'同一张 §10 常量表两把定界尺也打架: 节级窗内 %s 行 ⇎ 全篇同正则 %s 行, 多出的两行是「%s」(在窗外 %s ⇎ %s 行); '
         u'RETRANS_TIMER 只有在这张表里才印成数(第 %s 行), 其余四份一律只写驼峰名。'
         u'窗内壳行合计 %s 枚——定界谓词不看壳, 所以摘壳必须另算一把。'
         % (V('win_n'), EXPR(len(F['win_kinds']), u"len(B93V('win_kinds'))", u'定界谓词种数'),
            STRICTWV, EXPR(sum([z[11] for z in F['win_census']]),
                           u"sum([B93V('win_census', k)[11] for k in range(%d)])" % len(F['win_census']), u'摘壳后窗内严轨'),
            V('win_strict_eaten'),
            EXPR(sum([z[7] for z in F['win_census']]), u"sum([B93V('win_census', k)[7] for k in range(%d)])" % len(F['win_census']), u'窗内数字合计'),
            DIGEAT, NUMLESS,
            F['win_numless_with_var'][0][2], F['win_numless_with_var'][1][2], F['win_numless_with_var'][4][2],
            SH(0, 6), SH(0, 5),
            CONSTN, CONSTDN, F['const_out_of_win'][0][0], F['const_out_of_win'][0][2], F['const_out_of_win'][1][2],
            V('const_rows', 13, u'RETRANS_TIMER 行序'), WINSHELL))

E.append(u'🧬 单位口径与换算自证: 严轨(数字紧跟时长单位)逐份 %s ⇎ 宽轨(连缩写 s/sec 与“数字. 复数单位”都算) %s ⇎ '
         u'宽轨里只走短单位的 %s——4862 与 4429 严轨零枚而宽轨各 %s ⇎ %s 枚, 差的全是“6 s”这种缩写与编号里的假命中; '
         u'数值×时长单位共 %s 组(带空格 %s ⇎ 粘连 %s), 折成秒后去重 %s 个值; 跨份换算后同值的 %s 组 %s 对, 例如 %s。'
         u'面内自证的双单位行 %s 枚全部自证成立(「%s」⇎「%s」⇎「%s」⇎「%s」), 括号侧单位形 %s 种 ⇎ '
         u'值为 1 仍写复数的 %s 枚; 另有隐式外单位行 %s 枚(数上不印单位, 靠正文一句「(in milliseconds)」定标, 如 %s)。'
         u'数字形状也分家: 千分位只在 4861(%s 枚)⇎ sysctl(%s 枚); 前导点小数只在 4861(%s 行)⇎ sysd(%s 处); '
         u'十六进制与 INT_MAX 形默认值只在 sysctl(%s); 分数与百分数只在 sysd(%s ⇎ %s)。'
         u'五面数字普查共 %s 枚, 其中 %s 枚其实是 IPv4/IPv6 里的版本号数字——按“有几个数”数数会把它们当成量。'
         % (J('strict_n'), J('loose_n'), J('loose_short_n'), V('loose_n', 0), V('loose_n', 2),
            CONVT, V('conv_spaced_n'), V('conv_glued_n'), CONVVAL,
            EXPR(len(F['conv_same']), u"len(B93V('conv_same'))", u'跨份同值组'), V('conv_same_n'),
            F['conv_same'][u'1.0'][0][0] + u' ⇎ ' + F['conv_same'][u'1.0'][0][1],
            DUALN, F['dual_unit_lines'][0][1], F['dual_unit_lines'][2][1], F['dual_unit_lines'][3][1],
            F['dual_unit_lines'][1][1],
            EXPR(len(F['dual_gloss_forms']), u"len(B93V('dual_gloss_forms'))", u'括号侧单位形种'),
            V('dual_plural_at_one'), IMPLN, F['dual_implicit_lines'][0][0],
            EXPR(len(F['comma_nums'][1]), u"len(B93V('comma_nums', 1))", u'4861 千分位'),
            EXPR(len(F['comma_nums'][3]), u"len(B93V('comma_nums', 3))", u'sysctl 千分位'),
            EXPR(len(F['const_dot_rows']), u"len(B93V('const_dot_rows'))", u'4861 前导点行'),
            EXPR(len(F['dotlead_unit'][1]), u"len(B93V('dotlead_unit', 1))", u'4861 前导点×单位'),
            EXPR(len(F['hex_default'][3]), u"len(B93V('hex_default', 3))", u'sysctl 十六进制默认值'),
            EXPR(len(F['fraction'][4]), u"len(B93V('fraction', 4))", u'sysd 分数'),
            EXPR(len(F['percent'][4]), u"len(B93V('percent', 4))", u'sysd 百分数'),
            DIGH, DIGN))

E.append(u'🧾 序列化层与对账: 末一份另有一层壳——同一份 systemd.network 的网页面 %s 字节 ⇎ %s 码位 ⇎ %s 行, '
         u'标签 %s 枚吃掉 %s 字符 ⇎ 实体 %s 枚; 盘上那份 .txt 剥壳面 %s 码位 ⇎ 本遍从 html 自剥 %s 码位, 差 %s——'
         u'两家剥壳器序列化不同(标签吃掉 %s ⇎ 盘面差 %s 对不上), 所以这一份的“面”必须先点名是哪一张。'
         u'页壳按体裁分流: 三份 RFC 走 [Page n] 页脚 %s 行 ⇎ 旧式眉 %s 行 ⇎ IETF 独占行 %s; sysctl 走键行 %s ⇎ '
         u'制表符打头 %s 行(制表符共 %s 枚, 其余四面零); sysd 走选项行 %s ⇎ “Added in version …” 行 %s。'
         u'引用边的写法也分家: 带空格 “RFC nnnn” 去重后逐份 %s ⇎ 粘连 “RFCnnnn” %s, 只在粘连里出现的: sysctl %s 枚 ⇎ sysd %s 枚。'
         u'与采集遍 _pick93 逐键对账 %s 项 ⇎ 符 %s 项 ⇎ 不符 %s 项(不符键名 %s 枚, 空表即两遍同数); 布尔门 %s 道全绿(红项 %s); '
         u'恒等式 %s 条逐条归零; 现量键 %s 枚(此计数取自自计量键落位前, 故它与 %s 本身都不在它数内); 判词针 %s 枚 ⇎ 锚定行 %s 条。'
         u'ℒ 方法 ⇒ 这道题的隐性知识分四键: ①答案键 4862 给变量名与“Default: 1” ⇎ 4861 给 1,000 milliseconds 与 3 transmissions ⇎ '
         u'4429 只批评默认值不给数 ⇎ sysctl 给裸数 1 ⇎ sysd 对 IPv6 交回内核而只对 IPv4 给数——四种“给法”不在同一把尺上; '
         u'②尺键 单位能落三处: 值位(1,000 milliseconds) ⇎ 表列(ms/秒/次数/无量纲并排) ⇎ 键名(*Sec/*NSec), 还可能不落(裸数+描述里的 probes); '
         u'③档键 同一句在逐行 ⇎ 折平 ⇎ 摘壳 ⇎ 去连字四档给出四个数, 硬换行与连字符断词各自吃掉一批命中(含 sysctl 那个读不到默认值的键); '
         u'④层键 规范面写次数与间隔, 内核面写开关与裸数, 实现面写“交回内核”, 而实现面的面本身有两张(html ⇎ 剥壳 txt)。'
         % (V('html_bytes'), V('html_cp'), V('html_lines'), V('tag_n'), V('tag_chars'), V('ent_n'),
            V('stripped_cp'), V('own_detag_cp'), V('disk_vs_own'), V('tag_chars'), V('html_minus_stripped'),
            J('foot_page'), J('hdr_old'), J('ietf_alone'), V('key_lines', 3), V('tab_led', 3), V('tab', 3),
            V('opt_lines', 4), V('added_lines', 4),
            u' ⇎ '.join([EXPR(len(F['ref_spaced'][i]), u"len(B93V('ref_spaced', %d))" % i, u'带空格引用·%s' % LBL[i]) for i in range(NSRC)]),
            u' ⇎ '.join([EXPR(len(F['ref_glued'][i]), u"len(B93V('ref_glued', %d))" % i, u'粘连引用·%s' % LBL[i]) for i in range(NSRC)]),
            GLUED, GLUEDD,
            V('pick_pairs'), V('pick_agree'), V('pick_diff'), DIFFK_N, V('gate_keys'), RED_N,
            V('zid_scan_n'), V('scan_key_n'), V('zid_scan_n'), V('needle_n'), PINN))


def TTA_V(t):
    return sum([F['needles4'][k][i][t] for k in range(NDL) for i in range(NSRC)])


enc = u'\n\n'.join(E)
assert not MISS, u'锚不在词表: %s' % MISS[:4]
assert enc.count(u'⟦') == enc.count(u'⟨'), (enc.count(u'⟦'), enc.count(u'⟨'))
assert u"V('" not in enc and u'EXPR(' not in enc and u'J(' not in enc, u'正文里有未插值的注册调用'

CT = dump_deriv()
assert u'0' not in CT and ZERO, u'零式表异常'
CT[u'0'] = u"sum([%s])" % u','.join(ZERO)
for k, v in DER.items():
    CT.setdefault(k, v)
DER.clear()
DER.update(CT)

# 复算契约用的环境刻意不给 F ⇎ 只给门内也有的东西(B93V ⇎ 内建聚合 ⇎ range),
_EVENV = {u'B93V': BB93, u'range': range, u'sum': sum, u'len': len, u'max': max, u'min': min,
          u'abs': abs, u'sorted': sorted, u'round': round, u'set': set, u'str': str, u'bytes': bytes}
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
head = (u'# B93 重复地址检测要试几次、每次隔多久: 4862 只给变量名与 Default: 1⇎4861 给 1,000 milliseconds 与 3 transmissions⇎'
        u'4429 只批评默认值不给数⇎sysctl 给裸数 1 而单位写在描述里⇎systemd.network 对 IPv6 交回内核而只对 IPv4 给 200 milliseconds, '
        u'单位三处落位(值位⇎表列⇎键名)⇎四档可读性(逐行⇎折平⇎摘壳⇎去连字)⇎一个默认值被硬换行劈开\n'
        u'src: ' + u' ⇎ '.join(u'%s(%d B)' % (PATH[i], F['bytes'][i]) for i in range(NSRC)) +
        u' (五份均一手: RFC 4862 §5 ⇎ RFC 4861 §10 常量表与 §7 ⇎ RFC 4429 §4.4 ⇎ Linux ip-sysctl 的 dad/solicit 族键 ⇎ '
        u'systemd.network(5) 的 IPv6DuplicateAddressDetection=/IPv6RetransmissionTimeSec=/IPv4DuplicateAddressDetectionTimeoutSec=; '
        u'数字一律从面内现读, 一个都不手填; systemd.network 另附同源 html 只作序列化对照, 不进正文归属; '
        u'上游改版后的现值只在本机或站外成立, 不进门槛)\n'
        u'; tags: 答案键(变量名⇎表行常量⇎只批评不给数⇎裸数键⇎交回内核 五把) 尺键(单位落值位⇎落表列⇎落键名 三处) '
        u'档键(逐行⇎折平⇎摘壳⇎去连字 四档可读性) 层键(规范面⇎内核文档面⇎实现面⇎同一实现面的 html⇎剥壳 txt 两张) '
        u'哨兵键(读不到默认值的键记 None) 反向对照键(独占针⇎跨份换算同值⇎粘连引用) 锚归属由正文现推 闭合账 标量档 清单档\n')

md = head + orig_sec + u'\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n'
io.open(MD_PATH, 'w', encoding='utf-8', newline=u'\n').write(md)
io.open(CT_PATH, 'w', encoding='utf-8', newline=u'\n').write(
    json.dumps(CT, ensure_ascii=False, indent=1, sort_keys=True))
print(u'B93 落盘: 编码区 %d 字符 ⇎ 原文区锚 %d 枚(正文标签 %d 枚) ⇎ 契约 %d 键全可复算 ⇎ 零式 %d 条并入 ⇎ 无着落 0'
      % (len(enc), n_anchor, enc.count(u'⟦'), len(CT), len(ZERO)))
