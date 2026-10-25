# -*- coding: utf-8 -*-
"""把 B60 的独立复算器(_b60_scan / B60V)接进 audit.py, 并生成 DERIV['B60']。
幂等: 重复运行先摘旧块再插新块。
_b60_scan 的量测段从 corpus/_mkB60.py 的 SCAN BEGIN ⇎ SCAN END 两根标记之间逐行机械抽出,
只在头部换成 audit 自己的路径常量与模块别名; 真正的独立性来自四处:
①采集侧 corpus/_pick60.py 是先于建条目写好的另一套实现(它用 (?i)\\bday[s]?\\b 数词族、str.count 数大写强度词、
  按 "数字 + [-或空格] + day" 手拼天数正则、'<' 手工分段数标签、行集求交算搬运),
  两边在 53 个口径一致的键上逐量对账(网页那一份两边量在不同层, 采集侧读壳、建条目侧读去壳面, 故只取四份纯文本面;
  对账行由 _mkB60.py 末尾打印, 现况 53／不符 0);
②抽出的代码在插门之前要把 _b60flat.json 的每个键与 DERIV['B60'] 的每条表达式重跑一遍, 值不符当场停机;
③锚的归属不读旁注文件, 由条目正文里"源标签紧接原子引文"的配对现推, 五源一律按归一串判成员;
④上限句谓词与第一遍不同: 建条目侧容许 "Validity Period" 在排版行间断开(pick 用单空格逐字面),
  两档之差(ceil_wrap⇎day_wrap⇎vp_wrap)因此是门可复算的量, 不是注释里的解释。
DERIV 的字面数是复合式: 同一字面的每条算式都在括号里, 只有全部相符才等于该字面。"""
import io, os, re, sys, json, glob

sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()
MK = io.open(u'corpus/_mkB60.py', encoding='utf-8').read()
NL = chr(10)
RAWS = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt',
        u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.layout.txt',
        u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt',
        u'corpus/raw/cert/le_lifetimes.html',
        u'corpus/raw/cert/rfc5280.txt']


def cut(a, b):
    i = MK.index(a)
    j = MK.index(b, i)
    return MK[i:j]


MEAS = cut(u'ENT = [', u'# --- SCAN END ---')
assert u'F[u' in MEAS and u'POOL' in MEAS and u'ceil_tri' in MEAS and u'day_shell_close' in MEAS
assert u'json.' not in MEAS and u'ENTRY' not in MEAS and u'DERIV' not in MEAS
assert u'FAN' in MEAS and u'ATOMSEL' in MEAS and u'pnorm' in MEAS

HEAD = u'''
# B60: 同一张公签 TLS 服务器证书最长能活多久——五份文书五种答法:
# raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt(T 上限句三元组 {MUST NOT 398, MUST NOT 825, SHOULD NOT 397})
# ⇎ BR-1.8.7.layout.txt(O 同三档, 而那句 825 禁令被排版折在两行之间) ⇎ TLS-BRs-v2.0.2.layout.txt(F 上限句再无 825, 只剩 MUST NOT 398 ⇎ SHOULD NOT 397)
# ⇎ le_lifetimes.html(N 90 天默认 ⇎ 6 天可选 ⇎ 2028 年 2 月 45 天 ⇎ 2029-03-15 起 47 天, 并把 47 归给"行业规则")
# ⇎ rfc5280.txt(R 通篇不答时长, 只管 notBefore/notAfter 怎么写: UTCTime 到 2049 年 ⇎ GeneralizedTime)。
# 本函数从五份字节独立复算: 上限句三元组与宾语集、单空格档⇎容换行档之差(排版折行做成键),
# 825/398/397 的整句窗口四档划分(上限⇎复用⇎§1.6 条目名⇎其他)与四档相加闭合,
# 天数值域逐份集合与三档写法(连字⇎空格⇎单数)相加闭合, 带壳文档的壳⇎面两口径(差额坐实到两枚 meta),
# 术语四叫法(大写 Validity Period ⇎ 小写 ⇎ 忽略大小写 ⇎ 词根 validity)、强度词的词界⇎子串⇎表行/正文两半,
# PDF ⇎ -layout ⇎ -raw 三个面的字符差⇎行差⇎分页符闭合, 三代整行共用⇎与 RFC 5280 几乎不共用⇎容斥闭合,
# 锚候选池按逐字再现份数五层划分与锚归属由正文现推。
# 不可由在库文件判定的: 五份文件的抓取时刻与磁盘 mtime 谁新谁旧、cabforum.org 此刻挂的是哪一版、
# LE 页"最后更新"那一行的真伪、47 天那份行业规则出自哪份文书——只进解读注, 不进门槛。
def _b60_scan():
    import hashlib as _hl
    import os as _os
    P2 = SRC['B60']
    NSRC = 5
    TAGS = [u'T', u'O', u'F', u'N', u'R']
    LB = dict(zip(TAGS, [u'旧基准', u'中基准', u'新基准', u'CA 说明', u'X.509 规范']))
    PATH = P2
    RAWPDF = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.pdf',
              u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.pdf',
              u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.pdf']
    RAWFACE = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.raw.txt',
               u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.raw.txt',
               u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.raw.txt']
    IDX = dict((t, i) for i, t in enumerate(TAGS))
    RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
    TXT = [RD(p) for p in PATH]
    ROOT = u''
    C = u'corpus'
    NL = chr(10)
'''

BODYTXT = u'\n'.join(u'    ' + x if x.strip() else x for x in MEAS.split(NL))
for a, b in ((u'os.path.getsize(', u'_os.path.getsize('), (u'hashlib.', u'_hl.')):
    BODYTXT = re.sub(u'(?<![.\\w])' + re.escape(a), b, BODYTXT)
assert not re.search(u'(?<![._a-zA-Z])open\\(', BODYTXT.replace(u'io.open(', u'X')), u'仍有裸 open('
assert u'_os.open(' not in BODYTXT, u'裸 open( 被误改写'
assert u'_hl.blake2b' in BODYTXT and u'_os.path.getsize' in BODYTXT

TAIL = u'''
    # ---- 结构性自检: 五答、上限句谓词两档、窗口四档划分、壳面两口径、术语与强度词闭合、搬运容斥 ----
    assert F[u'bytes'] == [248273, 259837, 363180, 28488, 352580] and F[u'sig_distinct'] == 5
    assert len(set(F[u'sig'])) == 5 and F[u'chars'] == [243533, 255329, 356795, 4215, 352580]
    assert F[u'lines'] == [4741, 4509, 6386, 617, 8460] and F[u'nonblank'] == [3517, 3356, 4715, 86, 5991]
    assert F[u'maxlen'] == [117, 131, 161, 662, 72] and F[u'rec_close'] == [0, 0, 0, 0, 0]
    assert F[u'ceil_tri'][0] == [(u'MUST NOT', u'398'), (u'MUST NOT', u'825'), (u'SHOULD NOT', u'397')]
    assert F[u'ceil_tri'][1] == F[u'ceil_tri'][0]
    assert F[u'ceil_tri'][2] == [(u'MUST NOT', u'398'), (u'SHOULD NOT', u'397')]
    assert F[u'ceil_tri'][3] == [] and F[u'ceil_tri'][4] == []
    assert F[u'ceil_n'] == [5, 5, 4, 0, 0] and F[u'ceil_distinct'] == [3, 3, 2, 0, 0]
    assert F[u'ceil_vals'] == [[u'397', u'398', u'825'], [u'397', u'398', u'825'], [u'397', u'398'], [], []]
    assert F[u'ceil_strict_n'] == [1, 3, 3, 0, 0] and F[u'ceil_wrap'] == [4, 2, 1, 0, 0]
    assert F[u'd825_ceil'] == [1, 1, 0, 0, 0] and F[u'd825_strict'] == [1, 0, 0, 0, 0]
    assert F[u'validwin_825'] == [3, 3, 2, 0, 0] and F[u'reusewin_825'] == [1, 1, 1, 0, 0]
    assert F[u'titlewin_825'] == [1, 1, 1, 0, 0] and F[u'otherwin_825'] == [0, 0, 0, 0, 0]
    assert F[u'lines_825'] == [5, 5, 4, 0, 0]
    assert F[u'validwin_825'][0] + F[u'reusewin_825'][0] + F[u'titlewin_825'][0] + F[u'otherwin_825'][0] \\
        == F[u'lines_825'][0]
    assert F[u'validwin_397'] == [2, 2, 2, 0, 0] and F[u'otherwin_397'] == [0, 0, 0, 0, 0]
    assert F[u'titlewin_6'] == [0, 0, 0, 1, 0] and F[u'titlewin_90'] == [0, 0, 0, 4, 0]
    assert F[u'otherwin_90'] == [1, 1, 1, 0, 0] and F[u'otherwin_45'] == [0, 0, 0, 1, 0]
    assert F[u'otherwin_47'] == [0, 0, 0, 1, 0] and F[u'reusewin_398'] == [1, 1, 1, 0, 0]
    assert F[u'win_close'] == 0 and F[u'validwin_total'] == 20 and F[u'otherwin_total'] == 5
    assert F[u'day_num'] == [29, 29, 34, 7, 0] and F[u'day_num_flex'] == [31, 29, 34, 7, 0]
    assert F[u'day_wrap'] == [2, 0, 0, 0, 0] and F[u'day_num_close'] == [0, 0, 0, 0, 0]
    assert F[u'day_set'] == [[u'5', u'30', u'90', u'397', u'398', u'825'],
                             [u'5', u'30', u'90', u'397', u'398', u'825'],
                             [u'5', u'7', u'10', u'30', u'90', u'397', u'398', u'825', u'2922', u'9132'],
                             [u'6', u'45', u'47', u'90'], []]
    assert F[u'day_set_n'] == [6, 6, 10, 4, 0]
    assert F[u'set_only_F'] == [u'7', u'10', u'2922', u'9132'] and F[u'set_only_N'] == [u'6', u'45', u'47']
    assert F[u'set_shared_NF'] == [u'90'] and F[u'set_shared_TF'] == F[u'day_set'][0]
    assert F[u'num_45_in_brs'] == 0 and F[u'num_47_in_brs'] == 0
    assert F[u'vp_caps'] == [7, 7, 7, 0, 0] and F[u'vp_low'] == [20, 19, 22, 0, 12]
    assert F[u'vp_ci'] == [27, 26, 29, 0, 12] and F[u'vp_ci_close'] == [0, 0, 0, 0, 0]
    assert F[u'vp_flex_ci'] == [28, 28, 31, 0, 14] and F[u'vp_wrap'] == [1, 2, 2, 0, 2]
    assert F[u'validity_stem'] == [35, 34, 53, 0, 38] and F[u'vp_stem_gap'] == [7, 6, 22, 0, 24]
    assert F[u'lifetime_ci'] == [1, 1, 1, 15, 3] and F[u'day_word'] == [44, 41, 49, 9, 1]
    assert F[u'day_free'] == [F[u'day_word'][i] - F[u'day_num'][i] for i in range(5)]
    assert F[u'kw_must'] == [256, 282, 637, 0, 304] and F[u'u_must'] == [256, 282, 642, 0, 304]
    assert F[u'must_sub_gap'] == [0, 0, 5, 0, 0] and F[u'mustnot_sub_gap'] == [0, 0, 0, 0, 0]
    assert F[u'h_must'] == [4, 2, 8, 0, 0] and F[u'b_must'] == [252, 280, 629, 0, 304]
    assert F[u'h_must_close'] == [0, 0, 0, 0, 0] and F[u'h_shall_close'] == [0, 0, 0, 0, 0]
    assert F[u'h_sub_close'] == [0, 0, 0, 0, 0] and F[u'h_shall'] == [6, 11, 7, 0, 0]
    assert F[u'b_shall'] == [213, 202, 216, 0, 15] and F[u'kw_upper'] == [613, 629, 1052, 0, 451]
    assert F[u'shall_ci'] == [219, 213, 223, 0, 15] and F[u'must_ci'] == [269, 298, 659, 0, 308]
    assert F[u'ts_utctime'] == [0, 0, 0, 0, 28] and F[u'ts_generalizedtime'] == [0, 0, 0, 0, 25]
    assert F[u'ts_only_R'] == 28 and F[u'gt_only_R'] == 25 and F[u'ts_non_R'] == [0, 0, 0, 0]
    assert F[u'y2049'] == [0, 0, 0, 0, 3] and F[u'y2050'] == [0, 0, 0, 0, 3]
    assert F[u'notbefore'] == [2, 2, 8, 0, 7] and F[u'notafter'] == [1, 1, 6, 0, 11]
    assert F[u'nanb_gap'] == [F[u'notafter'][i] - F[u'notbefore'][i] for i in range(5)]
    assert F[u'shell_all'] == [4, 3, 3, 3] and F[u'face_all'] == [2, 1, 1, 1]
    assert F[u'dup_gap'] == [2, 2, 2, 2] and F[u'dup_kinds'] == 1
    assert F[u'shell_s90'] == 4 and F[u'face_s90'] == 2 and F[u'shell_s47'] == 3 and F[u'face_s47'] == 1
    assert F[u'day_shell'] == 17 and F[u'day_face'] == 7 and F[u'day_meta'] == 5
    assert F[u'day_shell_close'] == 0 and F[u'last_updated'] == [0, 0, 0, 1, 0]
    assert F[u'le_dropped'] == 24187 and F[u'le_tags'] == 446 and F[u'le_metas'] == 12
    assert F[u'le_ents'] == 15 and F[u'le_scripts'] == 5 and F[u'le_styles'] == 0 and F[u'le_hrefs'] == 63
    assert F[u'ent_listed'] == 5 and F[u'ent_unused'] == [] and F[u'ent_unnamed'] == []
    assert F[u'pdf_bytes'] == [289455, 287608, 972214]
    assert F[u'raw_chars'] == [218948, 229414, 286227] and F[u'raw_lines'] == [3539, 3330, 4985]
    assert F[u'face_gap'] == [24585, 25915, 70568] and F[u'line_gap'] == [1202, 1179, 1401]
    assert F[u'formfeed'] == [99, 87, 128, 0, 151] and F[u'raw_formfeed'] == [99, 87, 128]
    assert F[u'ff_close'] == [0, 0, 0]
    assert F[u'hist_n'] == [60, 74, 80, 0, 0] and F[u'hist_chars'] == [3925, 5576, 5855, 0, 0]
    assert F[u'sec_cite'] == [142, 154, 362, 0, 136] and F[u'sec_cite_low'] == [0, 2, 1, 0, 0]
    assert F[u'sec_head'] == [672, 679, 674, 0, 2] and F[u'sec_head_d'] == [348, 358, 372, 0, 2]
    assert F[u'rfc_n5280'] == [18, 22, 44, 0, 151] and F[u'rfc_hit_R'] == [2, 3, 4, 0, 38]
    assert F[u'rfc_set_n'] == [21, 25, 28, 0, 38] and F[u'rfc_miss_n'] == [19, 22, 24, 0, 0]
    assert F[u'ver_self'][0][0] == u'Version 1.7.7' and F[u'ver_self'][2][0] == u'Version 2.0.2'
    assert F[u'ver_self'][3] == [] and F[u'baseline_reqs'] == [15, 18, 27, 0, 0]
    assert F[u'share_TO'] == 601 and F[u'share_OF'] == 1086 and F[u'share_TF'] == 543
    assert F[u'share_TOF'] == 484 and F[u'union_TOF'] == 7239
    assert F[u'only_T'] == 2147 and F[u'only_O'] == 1517 and F[u'only_F'] == 2313
    assert F[u'tof_close'] == 0 and F[u'share_TR'] == 1 and F[u'share_OR'] == 2 and F[u'share_FR'] == 2
    assert F[u'share_any_R'] == 2 and F[u'share_N_any'] == 0 and F[u'share_TN'] == 0
    assert F[u'share_TR_lines'] == [u'CA      Certification Authority']
    assert F[u'share_FR_lines'] == [u'CA    Certification Authority',
                                    u'notBefore through notAfter, inclusive."']
    assert F[u'pool_n'] == 15405 and F[u'pool_tiers'] == [7932, 1409, 5786, 219, 59]
    assert F[u'pool_close'] == 0 and sum(F[u'pool_tiers']) == F[u'pool_n']
    assert F[u'pool_tag_n'] == [3101, 2980, 4103, 25, 5196] and sum(F[u'pool_tag_n']) == F[u'pool_n']
    assert F[u'pool_maxlen'] == 662 and F[u'lines_ge25'] == [2807, 2720, 3458, 20, 4619]
    assert F[u'scalar_clos_n'] == 4 and F[u'scalar_clos_sum'] == 0 and F[u'list_clos_n'] == 7
    assert F[u'scalar_clos_list'] == sorted([u'day_shell_close', u'pool_close', u'tof_close', u'win_close'])

    # ---- 锚归属: 从条目正文的"源标签紧接原子引文"配对现推, 五源都按归一串判成员 ----
    ep = glob.glob(u'corpus/babeltele/B60_*.md')
    assert len(ep) == 1, ep
    TT = io.open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B60: 正文里没有带标签的锚'
    assert len(re.findall(u'⟨', enc)) == len(CITES), u'B60: 有锚没带源标签'
    ERR = [x for x in CITES if not pnorm(x[1]) or pnorm(x[1]) not in FAN[IDX[x[0]]]]
    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [tuple(i for i in range(NSRC) if pnorm(a) and pnorm(a) in FAN[i]) for a in DIS]
    F[u'anchor_total'] = len(CITES)
    F[u'anchor_distinct'] = len(DIS)
    F[u'anchor_err'] = len(ERR)
    F[u'anchor_single'] = len([h for h in HC if len(h) == 1])
    F[u'anchor_cross'] = len([h for h in HC if 1 < len(h) < NSRC])
    F[u'anchor_all5'] = len([h for h in HC if len(h) == NSRC])
    F[u'checks'] = len(DIS) * NSRC
    for t in TAGS:
        F[u'tag_' + t] = len(re.findall(u'⟦%s⟧' % t, enc))
    assert sum(F[u'tag_' + t] for t in TAGS) == F[u'anchor_total']
    assert not ERR, ERR[:3]
    assert F[u'anchor_single'] + F[u'anchor_cross'] + F[u'anchor_all5'] == len(DIS)
    assert all(F[u'tag_' + t] > 0 for t in TAGS), u'有五源标签没锚'
    return F

_B60 = _b60_scan()
B60V = lambda k, i=None: (_B60[k] if i is None else _B60[k][i])
'''

BLK = HEAD + BODYTXT + TAIL
compile(BLK, u'<b60 block>', 'exec')

o = NL + u'_B60 = _b60_scan()'
assert S.count(NL + u'_B59 = _b59_scan()') == 1, u'anchor _b59_scan'
B60ENV = u'B59V=B59V,' + NL + u'               B60V=B60V)'
i0 = S.find(u'# B60: 同一张公签 TLS 服务器证书')
while i0 >= 0:
    i1 = S.index(u'_B59 = _b59_scan()', i0)
    S = S[:i0] + S[i1:]
    i0 = S.find(u'# B60: 同一张公签 TLS 服务器证书')
if B60ENV in S:
    S = S.replace(B60ENV, u'B59V=B59V)')
S = S.replace(NL + u'_B59 = _b59_scan()', BLK + NL + u'_B59 = _b59_scan()')
assert S.count(u'B59V=B59V)') == 1, u'anchor env'
S = S.replace(u'B59V=B59V)', B60ENV)

PS = u"SRC['B59'] = ["
blk = (u"SRC['B60'] = ['corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt', "
       u"'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.layout.txt', "
       u"'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt', "
       u"'corpus/raw/cert/le_lifetimes.html', 'corpus/raw/cert/rfc5280.txt']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1, u'anchor SRC'
S = S.replace(PS, blk + PS)
OLD, NEW = u"'B58', 'B59'}", u"'B58', 'B59', 'B60'}"
if NEW not in S:
    assert S.count(OLD) == 2, u'anchor ATOM/HTMLSRC'
    S = S.replace(OLD, NEW)

# 锚比对面: 逐份按扩展名去壳(混合介质条目不能整条去壳, 否则 RFC 5280 的 <尖括号> 伪法会被当标签删掉)
H1 = u'    # ---- atom_face (generated by corpus/_wire60.py; do not hand-edit) ----'
H2 = u'    # ---- /atom_face ----'
HELP = H1 + u'''
def _atom_face(tag, raw):
    """锚比对面: HTMLSRC 条目逐份按扩展名剥壳——B60 是四份纯文本面加一份网页, 整条剥壳会把 RFC 5280 的
    <尖括号> 伪法当标签删掉。转义层两档并记: 粘面(标签替空串)与断面(标签替空格)都送进比对,
    因为建条目侧本就分两代实现——B58/B59 用 '<' 游标分段得粘面, B60 用三条正则一次替换得断面;
    同一处 "</a>." 在前者是 "2028.", 在后者是 "2028 ."。锚文本换不出剥壳口径, 于是口径两侧都认。
    与 corpus/atomcheck.py 的 face('')/face(' ') 两面同构。"""
    fs = SRC.get(tag, [])
    if tag not in HTMLSRC or not fs:
        return raw
    out = []
    for fill in (u'', u' '):
        for f in fs:
            t = open(f, encoding='utf-8', errors='replace').read()
            if f.lower().endswith(('.html', u'.htm')):
                t = re.sub(r'(?s)<!--.*?-->', u' ', t)
                t = re.sub(r'(?i)<br\\s*/?>', u' ', t)
                t = re.sub(r'<[^>]+>', fill, t)
                for a, b in DETAG_SG:
                    t = t.replace(a, b)
            out.append(t)
        out.append(u'\\n')
    return u'\\n'.join(out)
''' + H2 + u'\n'
OLDP = u"    P = prose_norm(_detag(raw) if tag in HTMLSRC else raw)"
NEWP = u"    P = prose_norm(_atom_face(tag, raw))"
pat = re.compile(re.escape(H1) + u'.*?' + re.escape(H2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
assert S.count(u"def src_raw(tag):") == 1, u'anchor _atom_face'
S = S.replace(u"def src_raw(tag):", HELP + NL + u"def src_raw(tag):", 1)
if NEWP not in S:
    assert S.count(OLDP) == 1, u'anchor check_atoms detag'
    S = S.replace(OLDP, NEWP)

M1 = u'# ---- B60 DERIV (generated by corpus/_wire60.py from corpus/_deriv60.json; do not hand-edit) ----'
M2 = u'# ---- /B60 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + NL, re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B59'] = {"
assert S.count(o3) == 1, u'anchor DERIV'
J = json.load(io.open(u'corpus/_deriv60.json', encoding='utf-8'))
S = S.replace(o3, M1 + NL + u"DERIV['B60'] = " + repr(J) + NL + M2 + NL + o3)

# 预演: 用刚抽出的扫描器把扁平表与 DERIV 的每一条算一遍
NS = {'SRC': {'B60': RAWS}, 're': re, 'io': io, 'os': os, 'glob': glob}
exec(compile(BLK, u'<b60 block>', 'exec'), NS)
env = NS['B60V']
BAD, MISMATCH = [], []
FLAT = json.load(io.open(u'corpus/_b60flat.json', encoding='utf-8'))


def deep(x):
    return [deep(y) for y in x] if isinstance(x, list) else list(x) if isinstance(x, tuple) else x


for k, v in FLAT.items():
    try:
        got = env(k)
    except Exception as e:
        BAD.append((k, repr(e)))
        continue
    if deep(got) != deep(v):
        MISMATCH.append((k, v, got))
assert not BAD, BAD[:6]
assert not MISMATCH, MISMATCH[:6]
for kk, v in J.items():
    try:
        got = eval(v, dict(NS), {'B60V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD[:6]
assert u'_b59_scan' in S and u'_b60_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
os.replace(T, P)
print(u'audit.py wired: _b60_scan+B60V+DERIV(%d 键) ｜ 扁平键 %d 个逐一对账 ｜ 复算点 %d 条预演全对 ｜ 锚 %d 处／去重 %d 串／归属检查 %d 次'
      % (len(J), len(FLAT), sum(len(v.split('*')) for v in J.values()),
         env('anchor_total'), env('anchor_distinct'), env('checks')))
