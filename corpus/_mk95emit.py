# -*- coding: utf-8 -*-
# B95 落盘遍(与 _mkB95.py 同进程 exec, 用建条遍自带的 V()/J()/EXPR() 注册器):
# 一枚数字都不手打——正文数字全由 F 现值插值, 派生数走 EXPR 当场把复算式登记进契约;
# 锚一律从 corpus/_atoms95.txt(机械产出的词表)按标签取串, 词表里没有的串即 MISS 报错;
# 落盘前逐条自校: 标签数=锚数 ⇎ 正文无未插值的注册调用 ⇎ 契约每条表达式现算必须回键 ⇎
# 三位以上数字要么在契约里要么在面上(无着落即红)。
import io, json, re

CT_PATH = u'corpus/_b95contract.json'
MD_PATH = u'corpus/babeltele/B95_certificate_serial_number_length_three_rulers.md'
TAGP_ORDER = [u'A', u'B', u'C', u'D', u'E']
ORDI = dict((t, i) for i, t in enumerate(TAGP_ORDER))

ATOMS = []
for _l in io.open(u'corpus/_atoms95.txt', encoding='utf-8'):
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


NN = F['needle_n']
NF = len(F['fam_sub'][0])
FI = {w: k for k, w in enumerate([u'octet', u'octets', u'byte', u'bytes', u'hex', u'hexadecimal',
                                  u'positive', u'non-negative', u'negitive', u'negative', u'zero',
                                  u'CSPRNG', u'entropy', u'random', u'sequential', u'non-sequential',
                                  u'unique', u'serialNumber', u'serial number', u'serialNumber values',
                                  u'20 octets', u'64 bits', u'63 bits', u'159', u'160', u'64',
                                  u'2\u00b9\u2075\u2079', u'positiveint', u'MUST be able to handle',
                                  u'Conformant', u'Conforming'])}
OI = {w: k for k, w in enumerate([u'MUST', u'MUST NOT', u'SHOULD', u'MAY', u'SHALL'])}
SHO = [k for k in range(NN) if u'gracefully handle such certificates' in NEEDLES[k]]
assert len(SHO) == 1, SHO
SHO = SHO[0]


def VC(name, a, b, note=u''):
    """二维表逐格登记(值必须是标量)。"""
    return EXPR(F[name][a][b], u"B95V('%s', %d)[%d]" % (name, a, b), note or u'%s·%d·%s' % (name, a, LBL[b]))


def JR(name, k, note=u''):
    return u' ⇎ '.join(VC(name, k, i, u'%s·%s·%s' % (note or name, k, LBL[i])) for i in range(NSRC))


def JFW(name, w, note=u''):
    """二维表(name[份][词])按词取一列, 五份成行(词族 ⇎ 义务词同形)。"""
    return u' ⇎ '.join(EXPR(F[name][i][w], u"B95V('%s', %d)[%d]" % (name, i, w),
                            u'%s·%s' % (note or name, LBL[i])) for i in range(NSRC))


def NEED_ROW(arr, k, note=u''):
    """某枚针在一把尺上的五份读数(逐格现加)。"""
    return u' ⇎ '.join(VC(arr, k, i, u'%s·%s' % (note or arr, LBL[i])) for i in range(NSRC))


def FACE_TOT(arr, i):
    """一把尺在一份面上的针命中总(逐枚相加, 门内复算同式)。"""
    return EXPR(sum([F[arr][k][i] for k in range(NN)]),
                u"sum([B95V('%s', k)[%d] for k in range(%d)])" % (arr, i, NN),
                u'%s·合计·%s' % (arr, LBL[i]))


def TOT_ROW(arr):
    return u' ⇎ '.join(FACE_TOT(arr, i) for i in range(NSRC))


FAMW = lambda i: EXPR(sum([F['fam_wrap'][i * NF + k] for k in range(NF)]),
                      u"sum(B95V('fam_wrap')[%d*%d:%d*%d])" % (i, NF, i + 1, NF), u'词族涨量·%s' % LBL[i])
OBW = lambda i: EXPR(sum([F['ob_wrap2'][i * 5 + k] for k in range(5)]),
                     u"sum(B95V('ob_wrap2')[%d*5:%d*5])" % (i, i + 1), u'义务词涨量·%s' % LBL[i])
WRAPT = EXPR(sum(F['ob_wrap'][k][i] for k in range(NN) for i in range(NSRC)),
             u"sum([sum(B95V('ob_wrap', k)) for k in range(%d)])" % NN, u'换行吃进的针次合计')
WRAPC = EXPR(len([1 for k in range(NN) for i in range(NSRC) if F['ob_wrap'][k][i]]),
             u"len([1 for k in range(%d) for i in range(5) if B95V('ob_wrap', k)[i]])" % NN,
             u'换行涨量非零格数')
FAMWT = EXPR(sum(F['fam_wrap']), u"sum(B95V('fam_wrap'))", u'词族涨量合计')
OBWT = EXPR(sum(F['ob_wrap2']), u"sum(B95V('ob_wrap2'))", u'义务词涨量合计')
PINN = EXPR(len(F['pin_lines']), u"len(B95V('pin_lines'))", u'锚定行条目数')
NEEDCELL = EXPR(F['needle_n'] * NSRC, u"B95V('needle_n') * 5", u'针×五份=探针次')
EXCL1 = EXPR(len([1 for x in F['needle_src'] if len(x) == 1]),
             u"len([1 for x in B95V('needle_src') if len(x) == 1])", u'只一面读到的针数')
EXCL2 = EXPR(len([1 for x in F['needle_src'] if len(x) == 2]),
             u"len([1 for x in B95V('needle_src') if len(x) == 2])", u'两面同现的针数')
EXCL3 = EXPR(len([1 for x in F['needle_src'] if len(x) >= 3]),
             u"len([1 for x in B95V('needle_src') if len(x) >= 3])", u'三面及以上同现的针数')
LEDG = EXPR(sum(F['byte_cp_ledger']) - sum(F['utf8_extra']),
            u"sum(B95V('byte_cp_ledger')) - sum(B95V('utf8_extra'))", u'字节减码位 ⇎ 逐枚 UTF-8 涨字节 两路差')
LSL = EXPR(sum(F['line_split_ledger']), u"sum(B95V('line_split_ledger'))", u'空行+非空行−总行 合计')
SHL = EXPR(sum(F['shell_ledger']), u"sum(B95V('shell_ledger'))", u'壳账容斥合计')
RLD = EXPR(sum(F['rows_ledger_diff']), u"sum(B95V('rows_ledger_diff'))", u'行式对账合计')
S159 = EXPR(F['der_159'] * 8 - 1, u"B95V('der_159') * 8 - 1", u'20 字节能装的位减符号位')
B63 = EXPR(F['der_63'] * 8 - 1, u"B95V('der_63') * 8 - 1", u'8 字节能装的位减符号位')
HEXL = EXPR(len(F['le_hex']), u"len(B95V('le_hex'))", u'LE 十六进制串字符数')
HEXOK = EXPR(F['le_hex'][:2], u"B95V('le_hex')[0:2]", u'LE 串前缀 tag')
P20 = EXPR(F['widest'][0][0] + F['widest'][0][1] + F['widest'][0][2] + F['widest'][0][3] + F['widest'][0][4],
           u"sum(B95V('widest', 0))", u'“20 octets”五面合')
BRFCH = u' ⇎ '.join(EXPR(F['br_faces'][x]['chars'],
                         u"B95V('br_faces')['%s']['chars']" % x, u'BR 面·%s' % x)
                   for x in [u'layout', u'raw', u'pypdf'])
BRF159 = u' ⇎ '.join(EXPR(F['br_faces'][x]['n159'],
                          u"B95V('br_faces')['%s']['n159']" % x, u'BR 2¹⁵⁹·%s' % x)
                    for x in [u'layout', u'raw', u'pypdf'])
BRFCSP = u' ⇎ '.join(EXPR(F['br_faces'][x]['csprng'],
                          u"B95V('br_faces')['%s']['csprng']" % x, u'BR CSPRNG·%s' % x)
                    for x in [u'layout', u'raw', u'pypdf'])
BRFCAP = u' ⇎ '.join(EXPR(F['br_faces'][x]['serial_cap'],
                          u"B95V('br_faces')['%s']['serial_cap']" % x, u'BR 值域句·%s' % x)
                    for x in [u'layout', u'raw', u'pypdf'])
BRFC159 = EXPR(F['brf_n159'][0] - F['brf_cap'][0], u"B95V('brf_n159', 0) - B95V('brf_cap', 0)", u'2¹⁵⁹ 多出的枚数')
DEPTHS = EXPR(sum([len(x) for x in F['der_pairs']]), u"sum([len(x) for x in B95V('der_pairs')])", u'DER 样例对总数')
DIFFK_N = EXPR(len(F['pick_diffk']), u"len(B95V('pick_diffk'))", u'与采集遍不符键数')
RED_N = EXPR(len(F['bool_red']), u"len(B95V('bool_red'))", u'布尔门红项数')
GK_N = EXPR(len(F['gate_keys']), u"len(B95V('gate_keys'))", u'布尔门键数')
NA_CP0 = EXPR(len(F['na_codepoints'][3]), u"len(B95V('na_codepoints', 3))", u'BR 非 ASCII 码位种类')
NA_CP1 = EXPR(len(F['na_codepoints'][4]), u"len(B95V('na_codepoints', 4))", u'LE 非 ASCII 码位种类')
HDRS_ROWS = EXPR(len(F['br_rows']), u"len(B95V('br_rows'))", u'BR 收进行数')
PRE2 = EXPR(F['br_bfb_secs'].count(u'7.1.2.9 Precertificate Profile'),
            u"B95V('br_bfb_secs').count('7.1.2.9 Precertificate Profile')", u'precert 的 byte-for-byte 行数')

E = []
E.append(u'🧭 同一句“证书序列号到底能有多长、什么算违规”被五份一手文书各答一遍, 先把面尺摆开(字节 ⇎ 码位 ⇎ 三把行尺): '
         u'字节面 %s ⇎ 码位面 %s——两把尺只在后两份分开, 差 %s, 而逐枚非 ASCII 字符按 UTF-8 多出的字节是 %s, '
         u'两路账相减 %s; 非 ASCII 码位枚数 %s(去重后 BR %s 种 ⇎ 实现侧 %s 种), 三面合一才有 2¹⁵⁹ 的上标; '
         u'行尺三轨同摆: splitlines 档 %s ⇎ split(换行) 档 %s ⇎ 逐字符数换行 %s, 前两轨之差 %s 恰等于八种非换行界符'
         u'合计减「面以界符收尾」的一枚(五面收尾界符标志全 %s, 逐份相减合账 %s); 换行 ⇎ 回车两把尺: %s ⇎ %s'
         u'——第四份 BR 是全份 CRLF 面(回车与换行同数), 另四面零回车; 最长行两把尺(split 档 ⇎ 逐字符扫档)逐份同值 %s, '
         u'实现侧那份 HTML 的行最长 %s 码位; 空行 %s ⇎ 非空行 %s ⇎ 壳行 %s ⇎ 剥壳正文行 %s: 前两者相加回总行(合账 %s), '
         u'后两者相加同样回总行, 而壳账容斥(六形之和减重数)逐份归零合计 %s。'
         % (J('bytes'), J('cp'), J('byte_cp_ledger'), J('utf8_extra'), LEDG,
            J('na_total'), NA_CP0, NA_CP1, J('splitlines'), J('splitnl'), J('n_lf'),
            J('rows_ledger'), J('trail_bound'), RLD, J('n_lf'), J('n_cr'), J('maxlen'),
            V('maxlen', 4), J('blank'), J('nonblank'), J('shell_lines'), J('body_lines'), LSL, SHL))

E.append(u'📏 答值分四代四把尺且互不译: 2459 一枚长度都不给——“20 octets” 最宽档 %s 枚 ⇎ “positive” 整词档 %s 枚, '
         u'它只写 %s 与 %s, 外加一句 %s(那是 cRLNumber 的下限不是序列号); '
         u'3280 起给字节尺 %s 枚 ⇎ 义务句 %s ⇎ %s ⇎ %s; 5280 同文而把上限词的旧拼写换掉(%s 只在 3280 %s 枚 ⇎ 5280 %s 枚), '
         u'它另在 %s 之外补上符号位规矩 %s ⇎ %s; BR v2.0.2 整个换成值域尺 %s 与 %s; 实现侧给 DER 编码尺 %s ⇎ %s。'
         u'三把尺当场互译: 20 字节去掉符号位是 %s 位, 即上界 2^%s−1——与 BR 那句 “less than 2¹⁵⁹” 同格; '
         u'内容长再大一枚要到 %s 字节才装得下 2^160−1, 而 8 字节只到 %s 位 ⇎ 2^63+1 要 %s 字节。'
         % (JR('widest', 0), JFW('fam_ub', FI[u'positive']),
            AN(u'A', u'The serial number is an integer assigned by the CA'),
            AN(u'A', u'the issuer name and serial number identify a unique certificate'),
            AN(u'A', u'As a minimum, 16 octets'),
            VC('widest', 0, 1, u'20 octets·3280'),
            AN(u'B', u'The serial number MUST be a positive integer'),
            AN(u'B', u'CAs MUST force the serialNumber to be a non-negative integer'),
            AN(u'B', u'Certificate users MUST be able to handle serialNumber values up to 20 octets'),
            AN(u'B', u'Conformant CAs MUST NOT use serialNumber values longer than 20 octets'),
            VC('fam_sub', 1, FI[u'Conformant'], u'Conformant·3280'),
            VC('fam_sub', 2, FI[u'Conformant'], u'Conformant·5280'),
            AN(u'C', u'Conforming CAs MUST NOT use serialNumber values longer than 20 octets'),
            AN(u'C', u'the sign bit in the DER encoding of the INTEGER value MUST be zero'),
            AN(u'C', u'This can be done by adding a leading (leftmost)'),
            AN(u'D', u'MUST be a non-sequential number greater than zero (0)'),
            AN(u'D', u'containing at least 64 bits of output from a CSPRNG'),
            AN(u'E', u'serial numbers encoded in DER as 8 bytes can be at most 63 bits long'),
            AN(u'E', u'Encoding a 64-bit positive serial number requires a 9-byte encoded value'),
            S159, S159, V('der_160'), B63, V('der_63p1')))

E.append(u'⚖ 单位词与极性词的三把尺(子串 ⇎ 布尔表词界 ⇎ 断言正则)三轨逐枚同数 %s 处分歧 ⇎ 子串尺比词界尺多读 %s 枚'
         u'(逐份 %s): “octet” 在 2459 子串 %s ⇎ 词界 %s, 差的 %s 枚全落在 “octets” 里; '
         u'“byte” 在 BR 面 %s ⇎ %s ⇎ 在实现侧 %s ⇎ %s; 极性词 “positive” 词界档 %s ⇎ 子串档 %s——2459 那两枚子串'
         u'全在 %s 里, 所以它其实一次都没把序列号说成“正整数”; “non-negative” 两档同 %s ⇎ 拼错的 “negitive” 五面 %s 枚; '
         u'“serialNumber” 驼峰形与 “serial number” 空格形各面 %s ⇎ %s; 上限三形: “20 octets” %s ⇎ “64 bits” %s ⇎ '
         u'“2¹⁵⁹” %s——只有 BR 认上标那形, 而十进制 159 ⇎ 160 两形字样各面 %s ⇎ %s。'
         % (V('fam_ruler_diff'), FAMWT, u' ⇎ '.join([FAMW(i) for i in range(NSRC)]),
            VC('fam_sub', 0, FI[u'octet'], u'octet 子串·2459'), VC('fam_ub', 0, FI[u'octet'], u'octet 词界·2459'),
            EXPR(F['fam_wrap'][FI[u'octet']], u"B95V('fam_wrap')[%d]" % FI[u'octet'], u'octet 涨量·2459'),
            VC('fam_sub', 3, FI[u'byte'], u'byte 子串·br'), VC('fam_ub', 3, FI[u'byte'], u'byte 词界·br'),
            VC('fam_sub', 4, FI[u'byte'], u'byte 子串·le'), VC('fam_ub', 4, FI[u'byte'], u'byte 词界·le'),
            JFW('fam_ub', FI[u'positive']), JFW('fam_sub', FI[u'positive']),
            AN(u'A', u'the construct "positiveint ::= INTEGER'),
            JFW('fam_ub', FI[u'non-negative']), JFW('fam_sub', FI[u'negitive']),
            JFW('fam_sub', FI[u'serialNumber']), JFW('fam_sub', FI[u'serial number']),
            JR('widest', 0), JR('widest', 3), JFW('fam_sub', FI[u'2\u00b9\u2075\u2079']),
            JFW('fam_sub', FI[u'159']), JFW('fam_sub', FI[u'160'])))

E.append(u'🪜 义务词两把尺: 逐行大写档 MUST %s ⇎ 全篇折平小写档 MUST %s——两档之差合计 %s 枚(逐份 %s), '
         u'因为折平小写档把句中助动词 may 全吃了进来: MAY 那一格从 %s 涨到 %s(2459) ⇎ 从 %s 涨到 %s(5280); '
         u'纯换行的涨量另算(判词针那一层, 见 🔁), 两者不可混。指到序列号头上的强制式各代不同: '
         u'3280/5280 有 %s ⇎ %s ⇎ %s 三句, 2459 一句都没有(它的 MUST 有 %s 枚但都不在这件事上); '
         u'BR 的强制式只出现在表行里(%s 行值域句各属一节); 那句弱义务 %s 折平档 %s ⇎ 逐行档合计 %s——锚身被硬换行劈开, '
         u'取哪一档决定它读不读得到。'
         u'实现侧那一份通篇只有 %s 枚 MUST(它讲编码不讲义务) ⇎ 却写着 %s。'
         % (JFW('ob_line', OI[u'MUST']), JFW('ob_fold', OI[u'MUST']), OBWT,
            u' ⇎ '.join([OBW(i) for i in range(NSRC)]),
            VC('ob_line', 0, OI[u'MAY'], u'MAY 行·2459'), VC('ob_fold', 0, OI[u'MAY'], u'MAY 折·2459'),
            VC('ob_line', 2, OI[u'MAY'], u'MAY 行·5280'), VC('ob_fold', 2, OI[u'MAY'], u'MAY 折·5280'),
            AN(u'B', u'The serial number MUST be a positive integer'),
            AN(u'B', u'CAs MUST force the serialNumber'),
            AN(u'B', u'Certificate users MUST be able to handle'),
            VC('ob_line', 0, OI[u'MUST'], u'MUST 行·2459'),
            V('br_cap_rows'), AN(u'C', u'Certificate users SHOULD be prepared to gracefully handle'),
            NEED_ROW('role_fold', SHO, u'弱义务折平档'),
            EXPR(sum(F['role_line'][SHO]), u"sum(B95V('role_line', %d))" % SHO, u'弱义务逐行档合计'),
            VC('ob_fold', 4, OI[u'MUST'], u'MUST 折·le'), AN(u'E', u'RFC 5280 requires that serial numbers be positive')))

E.append(u'🔁 反向对照: 判词针 %s 枚在五份面各扫一遍 = 探针 %s 次, 四档同摆(逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 重叠档); '
         u'逐行档合计 %s ⇎ 折平档 %s ⇎ 摘壳档 %s ⇎ 重叠档 %s——摘壳与折平逐份同数(壳行不吃判词也不吐判词), '
         u'重叠档与不重叠档逐格同数(差 %s); 折平比逐行多读 %s 枚次 ⇎ 落在 %s 格上, 即锚身被硬换行劈开的那些句子。'
         u'独占账: 只一面读到的针 %s 枚 ⇎ 两面同现 %s 枚 ⇎ 三面及以上 %s 枚, 其中上限句的拼写是最干净的一对照: '
         u'%s 只在 3280(%s 枚)⇎ %s 只在 5280(%s 枚), 两面其余三家皆零; 同一处逗号也分家: %s 只在 3280(%s)⇎ '
         u'%s 只在 5280(%s)。'
         % (V('needle_n'), NEEDCELL, TOT_ROW('role_line'), TOT_ROW('role_fold'), TOT_ROW('role_sh'),
            TOT_ROW('role_ovl'), V('ovl_eq_fold'), WRAPT, WRAPC, EXCL1, EXCL2, EXCL3,
            AN(u'B', u'Conformant CAs MUST NOT use serialNumber values longer than 20 octets'),
            NEED_ROW('role_sh', 6),
            AN(u'C', u'Conforming CAs MUST NOT use serialNumber values longer than 20 octets'),
            NEED_ROW('role_sh', 5),
            AN(u'B', u'that are negative, or zero'), NEED_ROW('role_sh', 8),
            AN(u'C', u'that are negative or zero'), NEED_ROW('role_sh', 7)))

E.append(u'🧮 同宗三代正文块(§4.1.2.2 从 “The serial number” 到 4.1.2.3, 剥壳行后逐字符扫句界): '
         u'句数 %s, 两把句界尺(逐字符扫 ⇎ 正则 re.split)逐句同列表 %s; 句集容斥: 2459 的句被 3280 收下 %s 枚 ⇎ '
         u'3280 与 5280 同句 %s 枚 ⇎ 只 5280 有的新句 %s 枚 ⇎ 只 3280 有而被删的句 %s 枚——'
         u'两式各自当场相加都回它自己的句数(合账零); BR 与实现侧没这段正文(句数 %s ⇎ %s)。'
         u'义务词在正文块外的分布也照同一把尺记: MUST NOT 逐行档 %s ⇎ 折平档 %s, SHOULD %s ⇎ %s。'
         % (J('sec_sents'), V('sec_ruler_same'), V('sec_2459_in_3280'), V('sec_3280_5280_same'),
            V('sec_5280_new'), V('sec_3280_dropped'), V('sec_sents', 3), V('sec_sents', 4),
            JFW('ob_line', OI[u'MUST NOT']), JFW('ob_fold', OI[u'MUST NOT']),
            JFW('ob_line', OI[u'SHOULD']), JFW('ob_fold', OI[u'SHOULD'])))

E.append(u'🧱 BR 把答案摊成表行: 一次枚出 7.1.2.x 标题 %s 枚建清单, 再按行号 bisect 归属, 收到表行 %s 行'
         u'(值域句 %s 行 ⇎ byte-for-byte 句 %s 行, 两式相加 %s), 八行值域句各属不同节 ⇎ 三行 bfb 分属 %s 节两行 + '
         u'一节一行; 同一份 BR 文书的三张提取面(layout ⇎ raw ⇎ pypdf)字符 %s ⇎ 2¹⁵⁹ 枚数 %s ⇎ CSPRNG %s ⇎ '
         u'值域句 %s——上标那形在三面同数, 而 CSPRNG 比值域句多的 %s 枚正是变更表里 Ballot 156 的旧句(只束熵不束上界)。'
         u'目录属性尺另在 RFC 两面印出: ub-serial-number 行种 %s ⇎ 现读值 %s(2459 那一面压根没这行)。'
         % (V('br_hdr_n'), HDRS_ROWS, V('br_cap_rows'), V('br_bfb_rows'),
            EXPR(F['br_cap_rows'] + F['br_bfb_rows'],
                 u"B95V('br_cap_rows') + B95V('br_bfb_rows')", u'BR 两类行之和'), PRE2,
            BRFCH, BRF159, BRFCSP, BRFCAP, BRFC159,
            J('ub_serial_n'), J('ub_serial_vals')))

E.append(u'🧬 DER 尺在两处落地: 5280 的 §7.1 样例把 (值, 内容长) 一并印出, 三代里只有它印——样例对总数 %s(逐份 %s), '
         u'token 判形 ⇎ 正则选择支两轨同表 %s, 闭式 bit_length ⇎ 逐次右移两把尺分歧 %s 处 ⇎ 与面内印出的长度逐枚核对错 %s 枚; '
         u'边界四枚现算: 2^159−1 → %s 字节 ⇎ 2^160−1 → %s ⇎ 2^63−1 → %s ⇎ 2^63+1 → %s。'
         u'实现侧那一份把同一件事写成串: 九字节实例回收作 %s(tag %s 起头 ⇎ 长度字节 %s ⇎ 值 %s = 2^63+1), '
         u'串长 %s 字符 = 2 + 2 + 2×9; 上标在 HTML 壳内作 %s 枚 <sup>63</sup> ⇎ 剥壳后散作 “value 2 63” %s 枚 ⇎ '
         u'“2 63 +1” %s 枚——尺子换了序列化就不在原地。'
         % (DEPTHS, J('der_pair_n'), V('der_pairs_ruler_same'), V('der_ruler_diff'), V('der_pair_fail'),
            V('der_159'), V('der_160'), V('der_63'), V('der_63p1'),
            V('le_hex'), HEXOK, V('le_hex_len_octet'), V('le_hex_val'), HEXL,
            V('le_sup_shell'), V('le_sup_stripped'), V('le_sup_fold')))

E.append(u'🧾 壳与对账: 页壳按世代分流——三份 RFC 走 [Page N] 页脚 %s 行 ⇎ RFC 眉 %s 行(成对差 %s)⇎ IETF 独占行 %s ⇎ '
         u'换页符独占行 %s; BR 走 “pg. N” %s 行而页脚为零 ⇎ 实现侧不剥(壳行 %s); '
         u'两把壳尺(整行序列正则 ⇎ 逐字符游标定形)逐行同集, 分歧合计 %s; 六形之和减重数回壳行数(容斥合账 %s)。'
         u'实现侧另有一层 HTML 壳: 标签 %s 枚 ⇎ 实体 %s 枚 ⇎ 壳面 %s 字符 ⇎ 剥壳面 %s 字符 ⇎ 吃掉 %s 字符; '
         u'制表符只在这份里 %s 枚(另四面零)。'
         u'与采集遍 _pick95 逐键对账 %s 项 ⇎ 符 %s 项 ⇎ 不符 %s 项(不符键名清单 %s 枚, 空表即两遍逐键同数); 布尔门 %s 枚全绿(红项 %s); '
         u'恒等式 %s 条逐条归零; 现量键 %s 枚(该计数在自计量键落位前取, 故它本身与恒等式计数 %s 都不在它数内); '
         u'判词针 %s 枚 ⇎ 锚定行条目 %s 条。ℒ 方法 ⇒ 这道题的隐性知识分四键: ①答案键 2459 不给数 ⇎ 3280/5280 给 '
         u'20 字节 ⇎ BR 给 <2¹⁵⁹ 的值域与 ≥64 位熵 ⇎ 实现侧给 DER 内容长——四把尺要当场互译才知道同不同; '
         u'②尺键 字节数 ⇎ 比特位 ⇎ 十六进制字符数三把尺各自成句, 而“20 字节”与“2¹⁵⁹”相差的正是符号位那一枚; '
         u'③档键 同一判词在逐行 ⇎ 折平 ⇎ 摘壳 ⇎ 重叠四档给出四个数, 取哪档决定“这句话读不读得到”; '
         u'④层键 规范面把上限写成值或字节, 实现面把它写成编码长度——并且只有实现面把上标序列化换掉。'
         % (J('foot_page'), J('hdr_rfc'), J('page_pair_gap'), J('ietf_alone'), J('ff_led'),
            J('br_pgnum'), V('shell_lines', 4), EXPR(sum(F['shell_pred_diff']), u"sum(B95V('shell_pred_diff'))",
                                                     u'两把壳尺分歧合计'), SHL,
            V('le_tags'), V('le_entities'), V('le_html_chars'), V('le_stripped_chars'), V('le_drop'),
            V('tab', 4), V('pick_pairs'), V('pick_agree'), V('pick_diff'), DIFFK_N, GK_N, RED_N,
            V('zid_scan_n'), V('scan_key_n'), V('zid_scan_n'), V('needle_n'), PINN))

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

# 复算契约用的环境刻意不给 F ⇎ 只给门内也有的东西(B95V ⇎ 内建聚合 ⇎ range),
_EVENV = {u'B95V': BB95, u'range': range, u'sum': sum, u'len': len, u'max': max, u'min': min,
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
head = (u'# B95 证书序列号到底能多长: 2459⇎3280⇎5280⇎CA/B TLS BR⇎LE 手册五份一手文书各答一遍 '
        u'不给数⇎20 octets⇎<2¹⁵⁹+64 位熵⇎8 字节=63 位, 上限词两拼(Conformant⇎Conforming)⇎符号位那枚字节⇎三张提取面同数\n'
        u'src: ' + u' ⇎ '.join(u'%s(%d B)' % (PATH[i], F['bytes'][i]) for i in range(NSRC)) +
        u' (五份均一手: RFC 2459 §4.1.2 ⇎ RFC 3280 §4.1.2.2 ⇎ RFC 5280 §4.1.2.2+§7.1+附录 B ⇎ '
        u'CA/Browser Forum TLS BR v2.0.2 的 7.1.2.x 表行 ⇎ Let\'s Encrypt《A Warm Welcome to ASN.1 and DER》; '
        u'数字一律从面内现读, 一个都不手填; BR 另附同文书 raw ⇎ pypdf 两张提取面只作对照不进正文归属; '
        u'上游改版后的现值只在本机或站外成立, 不进门槛)\n'
        u'; tags: 答案键(不给数⇎20 octets⇎<2¹⁵⁹⇎DER 内容长 四把尺) 尺键(字节⇎比特⇎十六进制字符 三把) '
        u'档键(逐行⇎折平⇎摘壳⇎重叠 四档可读性) 层键(规范面⇎实现面⇎同一文书的三张提取面) '
        u'哨兵键(None=该面无此属性行) 反向对照键(独占针⇎上限词两拼⇎逗号分家) 锚归属由正文现推 闭合账 标量档 清单档\n')

md = head + orig_sec + u'\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n\n## ⛓解读注\n\n(待第四遍复测后写回)\n'
io.open(MD_PATH, 'w', encoding='utf-8', newline=u'\n').write(md)
io.open(CT_PATH, 'w', encoding='utf-8', newline=u'\n').write(
    json.dumps(CT, ensure_ascii=False, indent=1, sort_keys=True))
print(u'B95 落盘: 编码区 %d 字符 ⇎ 原文区锚 %d 枚(正文标签 %d 枚) ⇎ 契约 %d 键全可复算 ⇎ 零式 %d 条并入 '
      u'⇎ 无着落 0' % (len(enc), n_anchor, enc.count(u'⟦'), len(CT), len(ZERO)))
