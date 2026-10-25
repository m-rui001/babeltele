# -*- coding: utf-8 -*-
"""建条目第二遍(B80): “失败的 HTTP 请求到底能不能自动重来一次”, 交五份一手文书各答一遍
2616(99) §9.1.2 只给一句被动式禁令(不点施事者的名)+user agents MAY offer+自动重试 SHOULD NOT 再试 ⇎
7231(14) §4.2.2 换成机制句: 通信失败发生在客户端读到响应之前⇒可以自动重来(节内一枚义务词也不给) ⇎
6585(12) 通篇零枚 automat*×retry 族, 用 429 + Retry-After: 3600 + “50 requests per hour” 作答,
并自认“不定义源服务器怎么数请求” ⇎ 8470(18) 给阶梯: are expected to retry ⇎ SHOULD retry automatically ⇎
any retries MUST NOT be sent in early data ⇎ intermediary MAY automatically retry ⇎
9110(22) §9.2.2 把 7231 那句逐字搬来, 再点名 proxy(MUST NOT)与 client(SHOULD NOT), 并新允许
“a user agent can repeat a POST request automatically”。

本遍与采集侧(_pick80.py)换机制而不换定义: 字面针改由正则转义轨数(采集侧用游标 find 环),
边界针改由邻居字符手扫(采集侧用 (?<!…)/(?!…) 断言), 行形谓词改由 strip+分词形状判定(采集侧用整序正则),
节窗与池改由手工元组比较与集合代数(采集侧用行切片与列表成员), 句界改由逐字符扫(采集侧用前瞻正则)。
四档口径: 原面逐行 ⇎ 全篇折平 ⇎ 摘壳折平 ⇎ 节窗折平(只有三份有幂等节, 后两份的节窗档恒为 0)。
所有正文数字由 V()/J()/EXPR() 注册后插值, 一枚都不手打; 锚一律由面上位置导出。键名等于所量之物。"""
import io, itertools as IT, json, re, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
NL = u'\n'
LBL = [u'2616', u'7231', u'6585', u'8470', u'9110']
NSRC = 5
PATH = [u'corpus/raw/httpretry/rfc2616.txt', u'corpus/raw/httpretry/rfc7231.txt',
        u'corpus/raw/httpretry/rfc6585.txt', u'corpus/raw/httpretry/rfc8470.txt',
        u'corpus/raw/httpretry/rfc9110.txt']
F = {}
DER = {}
LITK = {}
# --- SCAN BEGIN --- (corpus/_wire80.py 把这一段 ⇎ _mk80emit.py 的 SCAN2 段机械切进 audit.py::_b80_scan)


def rd(p):
    return io.open(p, 'rb').read()


B = [rd(p) for p in PATH]
T = [b.decode('utf-8', 'replace') for b in B]
L = [t.split(NL) for t in T]


def pnorm(s):
    return u' '.join(s.lower().split())


def fold(s):
    return u' '.join(s.split())


def cnt_cur(hay, nd):
    c, i, n = 0, 0, len(nd)
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + n


def cnt_ovl(hay, nd):
    c, i = 0, 0
    while True:
        j = hay.find(nd, i)
        if j < 0:
            return c
        c += 1
        i = j + 1


def cnt_re(hay, nd):
    """本遍的字面针轨: 转义后整体正则扫描(采集侧是游标 find 环)。非重叠语义由 findall 自带。"""
    return len(re.findall(re.escape(nd), hay))


def _nb(s, i, n, kind):
    """邻居字符手扫: kind='alpha' 要求两侧都不是字母 ⇎ 'digit' 两侧都不是数字 ⇎ 'alnum' 两侧都不是字母数字。
    采集侧这三档分别写成 (?<![A-Za-z]) / (?<!\\d) / 无断言, 本遍一个断言也不用。"""
    a = i - 1
    b = i + n
    if kind == u'alpha':
        return not (a >= 0 and s[a].isalpha()) and not (b < len(s) and s[b].isalpha())
    if kind == u'digit':
        return not (a >= 0 and s[a].isdigit()) and not (b < len(s) and s[b].isdigit())
    return not (a >= 0 and s[a].isalnum()) and not (b < len(s) and s[b].isalnum())


def ub(s, w, kind=u'alpha'):
    c, i, n = 0, 0, len(w)
    while True:
        j = s.find(w, i)
        if j < 0:
            return c
        if _nb(s, j, n, kind):
            c += 1
        i = j + 1


def is_shell_pick(x):
    """采集遍 _pick80.py 的壳谓词, 逐字照抄——只为把两遍的壳账拆开到行"""
    return (re.match(u'^\\s*\\[Page \\d+\\]\\s*$', x) is not None
            or re.match(u'^\\s*RFC \\d+ +\\S.*((19|20)\\d\\d)\\s*$', x) is not None
            or x.strip() == u'')


def is_page_shell_pick(x):
    return (re.match(u'^\\s*\\[Page \\d+\\]\\s*$', x) is not None
            or re.match(u'^\\s*RFC \\d+ +\\S.*((19|20)\\d\\d)\\s*$', x) is not None)


def shell_line(x):
    """本遍壳谓词: 不分号形状, 先折叠再分词, 逐段比首尾 token(与采集侧的整序正则同集而机制不同)"""
    s = fold(x)
    if s == u'':
        return True
    tk = s.split(u' ')
    if tk[0] == u'[Page' and len(tk) == 3 and tk[1].isdigit() and tk[2] == u']':
        return True
    if tk[0] == u'RFC' and len(tk) >= 4 and tk[1].isdigit():
        y = tk[-1]
        if len(y) == 4 and (y[:2] in (u'19', u'20')) and y[2:].isdigit():
            return True
    return False


FOLD = [fold(t) for t in T]
LOWFOLD = [x.lower() for x in FOLD]
LOW = [[y.lower() for y in L[i]] for i in range(NSRC)]
SHP = [[x for x in L[i] if not is_shell_pick(x)] for i in range(NSRC)]
SHL = [[x for x in L[i] if not shell_line(x)] for i in range(NSRC)]
SH = [fold(NL.join(SHP[i])) for i in range(NSRC)]
# 四档面: 0 原面逐行 / 1 全篇折平 / 2 摘壳折平 / 3 节窗折平(后段的 SECW 填好后并入 FACES)
FACES = [L, FOLD, SH]
WIDE = SH

# ---------- 面量 ----------
F['label'] = LBL
F['src'] = PATH
F['bytes'] = [len(b) for b in B]
F['chars'] = [len(t) for t in T]
F['lines'] = [len(L[i]) for i in range(NSRC)]
F['newlines'] = [cnt_re(t, NL) for t in T]
F['lines_nl'] = [F['newlines'][i] + 1 for i in range(NSRC)]
F['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(NSRC)]
F['blank'] = [len([x for x in L[i] if fold(x) == u'']) for i in range(NSRC)]
F['maxlen'] = [max(len(x) for x in L[i]) for i in range(NSRC)]
F['over72'] = [len([x for x in L[i] if len(x) > 72]) for i in range(NSRC)]
F['ff'] = [cnt_re(t, u'\x0c') for t in T]
F['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(NSRC)]
F['ff_only'] = [len([x for x in L[i] if fold(x) == u'' and x != u'']) for i in range(NSRC)]
F['ff_inline'] = [len([x for x in L[i] if u'\x0c' in x and x != u'\x0c']) for i in range(NSRC)]
F['cr'] = [cnt_re(t, u'\r') for t in T]
F['nul'] = [cnt_re(t, u'\x00') for t in T]
F['nonascii'] = [len([c for c in t if ord(c) > 127]) for t in T]
F['bom'] = [1 if b[:3] == b'\xef\xbb\xbf' else 0 for b in B]
F['byte_cp_delta'] = [F['bytes'][i] - F['chars'][i] for i in range(NSRC)]
F['nonascii_extra'] = [sum(len(c.encode('utf-8')) - 1 for c in T[i] if ord(c) > 127) for i in range(NSRC)]
F['tail_nl'] = [1 if t.endswith(NL) else 0 for t in T]
F['lines_split'] = [len(t.splitlines()) for t in T]
F['lines_split_close'] = sum(F['lines_nl'][i] - F['tail_nl'][i] + F['ff'][i] - F['ff_inline'][i]
                             - F['lines_split'][i] for i in range(NSRC))
F['digit_chars'] = [len([c for c in t if c.isdigit()]) for t in T]
def tag_rulers(t):
    """四把标签尺都在这一个 token 集上量: 尖括号形 ⇎ 开标签名形 ⇎ 闭标签名形 ⇎ <http 形,
    剩下的是规范的尖括号伪法(<any CHAR>、<URL>), 一把 naive 剥壳会把它们当标签吃掉。"""
    sh = re.findall(r'<[^>\n]+>', t)
    op = len([x for x in sh if re.match(r'<[A-Za-z][A-Za-z0-9]*(?:[ >/])', x)])
    cl = len([x for x in sh if x.startswith(u'</')])
    ur = len([x for x in sh if x.startswith(u'<http')])
    return len(sh), op, cl, ur


TAG4 = [tag_rulers(t) for t in T]
F['txt_n'] = len([1 for p in PATH if p.lower().endswith(u'.txt')])
F['html_n'] = NSRC - F['txt_n']
F['tag_shape'] = [x[0] for x in TAG4]
F['tag_open'] = [x[1] for x in TAG4]
F['tag_close'] = [x[2] for x in TAG4]
F['tag_url'] = [x[3] for x in TAG4]
F['tag_pseudo'] = [F['tag_shape'][i] - F['tag_open'][i] - F['tag_close'][i] - F['tag_url'][i]
                    for i in range(NSRC)]
F['ent_total'] = [len(re.findall(u'&[A-Za-z#0-9]{1,8};', t)) for t in T]
F['comment'] = [len(re.findall(u'<!--', t)) for t in T]
F['shell_lines'] = [len(L[i]) - len(SHP[i]) for i in range(NSRC)]
F['fold_chars'] = [len(FOLD[i]) for i in range(NSRC)]
F['sh_chars'] = [len(SH[i]) for i in range(NSRC)]
F['sh_char_gap'] = [F['sh_chars'][i] - F['fold_chars'][i] for i in range(NSRC)]
F['pg_lines'] = [len([x for x in L[i] if u'[Page ' in x and x.rstrip().endswith(u']')]) for i in range(NSRC)]
F['hdr_lines_indent'] = [len([x for x in L[i] if fold(x).startswith(u'RFC ')]) for i in range(NSRC)]
F['hdr_lines_tight'] = [len([x for x in L[i] if re.match(r'^RFC \d+\b', x)]) for i in range(NSRC)]
F['pageless'] = [1 if (F['ff'][i] == 0 and F['pg_lines'][i] == 0) else 0 for i in range(NSRC)]
F['ff_minus_pg'] = [F['ff'][i] - F['pg_lines'][i] for i in range(NSRC)]
# 两遍壳账: 逐行分解, 只看账平不平(两把尺不同源, 不要求相等)
F['shell_pick'] = F['shell_lines']
F['shell_mk'] = [len(L[i]) - len(SHL[i]) for i in range(NSRC)]
MO = [[x for x in L[i] if shell_line(x) and not is_shell_pick(x)] for i in range(NSRC)]
PO = [[x for x in L[i] if is_shell_pick(x) and not shell_line(x)] for i in range(NSRC)]
F['shell_mk_only'] = [len(MO[i]) for i in range(NSRC)]
F['shell_pick_only'] = [len(PO[i]) for i in range(NSRC)]
F['shell_both'] = [F['shell_mk'][i] - F['shell_mk_only'][i] for i in range(NSRC)]
F['shell_ledger_close'] = sum(abs(F['shell_pick'][i] + F['shell_mk_only'][i]
                                  - F['shell_pick_only'][i] - F['shell_mk'][i]) for i in range(NSRC))
F['shell_pick_hdr'] = [len([x for x in PO[i] if fold(x).startswith(u'RFC')]) for i in range(NSRC)]
F['shell_mk_hdr'] = [len([x for x in MO[i] if fold(x).startswith(u'RFC')]) for i in range(NSRC)]

# ---------- 抬头谱系(本遍按冒号切段, 采集遍用整序正则) ----------
HEAD = [NL.join(L[i][:22]) for i in range(NSRC)]


def head_field(i, key):
    """取抬头里某一字段的 “数字逗号清单”: 冒号后跳空白, 再吃掉 [0-9, ] 这一族的连续串"""
    out = []
    for x in L[i][:22]:
        s = x.strip()
        if not s.startswith(key + u':'):
            continue
        j = len(key) + 1
        while j < len(s) and s[j] == u' ':
            j += 1
        run = u''
        while j < len(s) and (s[j].isdigit() or s[j] in u', '):
            run += s[j]
            j += 1
        out.append([y.strip() for y in run.split(u',')])
    return out[0] if out else []


F['obs_ids'] = [head_field(i, u'Obsoletes') for i in range(NSRC)]
F['upd_ids'] = [head_field(i, u'Updates') for i in range(NSRC)]
F['obs_line'] = [next((x.strip() for x in L[i][:22] if x.strip().startswith(u'Obsoletes:')), None)
                 for i in range(NSRC)]
F['upd_line'] = [next((x.strip() for x in L[i][:22] if x.strip().startswith(u'Updates:')), None)
                 for i in range(NSRC)]
F['std_line'] = [next((x.strip() for x in L[i][:22] if fold(x).startswith(u'STD:')), None) for i in range(NSRC)]
F['issn_hdr'] = [1 if any(x.strip().startswith(u'ISSN:') for x in L[i][:22]) else 0 for i in range(NSRC)]
F['years'] = [1999, 2014, 2012, 2018, 2022]
MON = [u'January', u'February', u'March', u'April', u'May', u'June', u'July', u'August',
       u'September', u'October', u'November', u'December']


def head_date(i):
    """本遍的日期轨: 逐 token 找 “月名 + 四位数”, 不看前后文(采集遍是一条 MON 正则)"""
    for x in L[i][:22]:
        tk = fold(x).split(u' ')
        for k in range(len(tk) - 1):
            if tk[k] in MON and len(tk[k + 1]) == 4 and tk[k + 1].isdigit():
                return tk[k], tk[k] + u' ' + tk[k + 1]
    return None, None


MD = [head_date(i) for i in range(NSRC)]
F['months'] = [m[0] for m in MD]
F['months_txt'] = [m[1] for m in MD]
F['year_span'] = max(F['years']) - min(F['years'])
F['year_inversions'] = len([(a, b) for a in range(NSRC) for b in range(NSRC)
                            if a < b and F['years'][a] > F['years'][b]])
F['year_order_lbl'] = u' ⇎ '.join(u'%s %d' % (LBL[i], F['years'][i]) for i in range(NSRC))
OBS = set(x for i in range(NSRC) for x in F['obs_ids'][i])
F['upd_target_obsoleted'] = [len([x for x in F['upd_ids'][i] if x in OBS]) for i in range(NSRC)]
F['obs_target_in_lib'] = [len([x for x in F['obs_ids'][i] if x in u' '.join(LBL)]) for i in range(NSRC)]
F['obs_total'] = sum(len(x) for x in F['obs_ids'])
F['upd_total'] = sum(len(x) for x in F['upd_ids'])
F['lineage_no_edge'] = [i for i in range(NSRC) if not F['obs_ids'][i] and not F['upd_ids'][i]]
# 族名⇎清单长: 逗号切出的段数(含尾逗号切出的空段)与去空段后的对象数之差就是“排版留下的空段”
F['obs_raw_segs'] = [len(x) for x in F['obs_ids']]
F['obs_ids_clean'] = [[y for y in x if y] for x in F['obs_ids']]
F['obs_blank_segs'] = [F['obs_raw_segs'][i] - len(F['obs_ids_clean'][i]) for i in range(NSRC)]
F['lineage_close'] = (F['obs_total'] + F['upd_total']
                      - sum(F['obs_raw_segs']) - sum(len(x) for x in F['upd_ids']))

# ---------- 自动重试词汇族 ----------
AUTOFAM = [u'automatically retry', u'automatically retried', u'automatically retrying',
           u'automatic retry', u'retry automatically', u'automatically repeat']
ALT = re.compile(u'|'.join(re.escape(x) for x in sorted(AUTOFAM, key=lambda s: -len(s))))
F['auto_fam'] = AUTOFAM
F['auto_line'] = [[sum(cnt_re(y, nd) for y in LOW[i]) for nd in AUTOFAM] for i in range(NSRC)]
F['auto_line_rows'] = [[len([y for y in LOW[i] if nd in y]) for nd in AUTOFAM] for i in range(NSRC)]
F['auto_fold'] = [[cnt_re(LOWFOLD[i], nd) for nd in AUTOFAM] for i in range(NSRC)]
F['auto_union_fold'] = [len(ALT.findall(LOWFOLD[i])) for i in range(NSRC)]
F['auto_fam_overlap'] = [sum(F['auto_fold'][i]) - F['auto_union_fold'][i] for i in range(NSRC)]
F['auto_gain'] = [sum(F['auto_fold'][i]) - sum(F['auto_line'][i]) for i in range(NSRC)]
F['auto_tot_line'] = [sum(F['auto_line'][i]) for i in range(NSRC)]
F['auto_tot_fold'] = [sum(F['auto_fold'][i]) for i in range(NSRC)]
F['auto_bare'] = [cnt_re(LOWFOLD[i], u'automatic') for i in range(NSRC)]
F['auto_bare_line'] = [sum(cnt_re(y, u'automatic') for y in LOW[i]) for i in range(NSRC)]
F['auto_sh'] = [[cnt_re(SH[i].lower(), nd) for nd in AUTOFAM] for i in range(NSRC)]
F['auto_sh_minus_fold'] = [sum(F['auto_sh'][i]) - sum(F['auto_fold'][i]) for i in range(NSRC)]
F['auto_bare_minus_union'] = [F['auto_bare'][i] - F['auto_union_fold'][i] for i in range(NSRC)]
F['auto_occ_rows'] = [sum(len([y for y in LOW[i] if nd in y]) for nd in AUTOFAM) for i in range(NSRC)]
F['auto_rows_minus_occ'] = [F['auto_occ_rows'][i] - sum(F['auto_line'][i]) for i in range(NSRC)]

# ---------- 跨行短横 ⇎ 裸词 ----------
F['hyb_idem'] = [cnt_re(T[i], u'non-' + NL + u'idempotent') for i in range(NSRC)]
F['idem_str'] = [cnt_re(LOWFOLD[i], u'idempotent') for i in range(NSRC)]
F['idem_line_occ'] = [sum(cnt_re(y, u'idempotent') for y in LOW[i]) for i in range(NSRC)]
F['idem_line_rows'] = [len([y for y in LOW[i] if u'idempotent' in y]) for i in range(NSRC)]
F['idem_hyb_line'] = [sum(cnt_re(y, u'non-idempotent') for y in LOW[i]) for i in range(NSRC)]
F['idem_hyb_fold'] = [cnt_re(LOWFOLD[i], u'non-idempotent') for i in range(NSRC)]
F['hyb_straddle'] = [F['idem_hyb_fold'][i] - F['idem_hyb_line'][i] for i in range(NSRC)]
F['idem_row_minus_occ'] = [F['idem_line_occ'][i] - F['idem_line_rows'][i] for i in range(NSRC)]

# ---------- 节窗(本遍把标题号解析成元组再比大小, 采集遍是一条正则) ----------
def sect_no(s):
    """行首的 “1.2.3.” 段: 逐字符吃数字与点, 返回(元组, 尾点有无); 不是编号行返回 (None, None)"""
    j = 0
    while j < len(s) and (s[j].isdigit() or s[j] == u'.'):
        j += 1
    head = s[:j]
    if not head or not any(c.isdigit() for c in head):
        return None, None
    if j >= len(s) or s[j] not in u' \t':
        return None, None
    dot = head.endswith(u'.')
    core = head[:-1] if dot else head
    parts = core.split(u'.')
    if any(p == u'' or not p.isdigit() for p in parts):
        return None, None
    return tuple(int(p) for p in parts), dot


IDW = []
SECNO, SECHL, SECHN, SECTOC, SECBODY, ENDK, ENDH = [], [], [], [], [], [], []
for i in range(NSRC):
    hits = []
    for k, x in enumerate(L[i]):
        s = fold(x)
        tp, _ = sect_no(s)
        if tp is not None and s.lstrip(u'0123456789. \t') in (u'Idempotent Methods',
                                                              u'Idempotent Request Methods'):
            hits.append((k, tp))
    if not hits:
        IDW.append(None)
        SECNO.append(None)
        SECHL.append(None)
        SECHN.append(0)
        SECTOC.append(None)
        SECBODY.append(None)
        ENDK.append(None)
        ENDH.append(None)
        continue
    k, tp = hits[-1]
    lvl = len(tp)
    nxt = len(L[i])
    end_kind = u'eof'
    for j in range(k + 1, len(L[i])):
        tj, _ = sect_no(fold(L[i][j]))
        if tj is None:
            continue
        if len(tj) <= lvl and tj >= tp:
            nxt = j
            end_kind = u'heading'
            break
    IDW.append(NL.join(L[i][k:nxt]))
    SECNO.append(u'.'.join(str(z) for z in tp))
    SECHL.append(L[i][k].strip())
    SECHN.append(len(hits))
    SECTOC.append(hits[0][0] + 1 if len(hits) > 1 else None)
    SECBODY.append(k + 1)
    ENDK.append(end_kind)
    ENDH.append(L[i][nxt].strip() if nxt < len(L[i]) else None)
F['sec_no'] = SECNO
F['sec_head_line'] = SECHL
F['sec_hit_n'] = SECHN
F['sec_toc_line'] = SECTOC
F['sec_body_line'] = SECBODY
F['sec_end_kind'] = ENDK
F['sec_end_head'] = ENDH
F['sec_end_head_fold'] = [fold(x) if x else None for x in ENDH]
F['sec_end_head_gap'] = [len(x) - len(fold(x)) if x else 0 for x in ENDH]
F['sec_found_n'] = len([x for x in SECNO if x])
F['sec_absent_n'] = NSRC - F['sec_found_n']
F['sec_lines'] = [len(x.split(NL)) if x else 0 for x in IDW]
F['sec_chars'] = [len(x) if x else 0 for x in IDW]
F['sec_words'] = [len(x.split()) if x else 0 for x in IDW]


def sent_ends(s):
    """句界手扫: “.” 之后跳空白(含换行), 落到大写字母、左括号或串尾才算一句完(采集遍是 '\\.\\s*(?=[A-Z(]|$)')"""
    i = 0
    while True:
        j = s.find(u'.', i)
        if j < 0:
            return None
        k = j + 1
        while k < len(s) and s[k] in u' \t\n':
            k += 1
        if k >= len(s) or s[k].isupper() or s[k] == u'(':
            return j
        i = j + 1


def sent_count(s):
    """整段的句数: 从串首反复用上面的手扫找句尾, 直到找不到"""
    n, frm = 0, 0
    while True:
        a = sent_ends(s[frm:])
        if a is None:
            return n
        n += 1
        frm += a + 1


F['sec_sents'] = [len(re.findall(u'\\.\\s', x)) if x else 0 for x in IDW]
F['sec_sents_scan'] = [sent_count(x) if x else 0 for x in IDW]
F['sec_sents_gap'] = [F['sec_sents'][i] - F['sec_sents_scan'][i] for i in range(NSRC)]
F['sec_row_dup'] = [F['sec_hit_n'][i] - (1 if SECNO[i] else 0) for i in range(NSRC)]
SECW = [fold(x) if x else u'' for x in IDW]
F['secw_chars'] = [len(x) for x in SECW]
F['sec_share_permille'] = [(1000 * F['sec_words'][i]) // len(FOLD[i].split()) for i in range(NSRC)]
FACES.append(SECW)

# ---------- 义务词阶梯 ----------
TONE = [u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD', u'MAY']
F['tone_fam'] = TONE
F['tone_norm'] = [[ub(T[i], nd) for nd in TONE] for i in range(NSRC)]
F['tone_norm_fold'] = [[ub(FOLD[i], nd) for nd in TONE] for i in range(NSRC)]
F['tone_straddle_k'] = [[F['tone_norm_fold'][i][k] - F['tone_norm'][i][k] for k in range(len(TONE))]
                        for i in range(NSRC)]
F['tone_straddle'] = [sum(F['tone_straddle_k'][i]) for i in range(NSRC)]
F['tone_case'] = [[cnt_re(LOWFOLD[i], nd.lower()) for nd in TONE] for i in range(NSRC)]
F['tone_case_gap'] = [sum(F['tone_case'][i]) - sum(F['tone_norm_fold'][i]) for i in range(NSRC)]
F['tone_sec'] = [[ub(SECW[i], nd) for nd in TONE] if SECW[i] else [0] * len(TONE) for i in range(NSRC)]
F['tone_sec_tot'] = [sum(F['tone_sec'][i]) for i in range(NSRC)]
F['tone_tot'] = [sum(F['tone_norm'][i]) for i in range(NSRC)]
F['tone_fold_tot'] = [sum(F['tone_norm_fold'][i]) for i in range(NSRC)]
F['tone_must_pure'] = [len([1 for a in re.finditer(u'(?<![A-Za-z])MUST(?![A-Za-z])(?! NOT)', T[i])])
                       for i in range(NSRC)]
F['tone_must_ledger'] = [F['tone_norm'][i][1] - F['tone_norm'][i][0] - F['tone_must_pure'][i]
                         for i in range(NSRC)]
F['tone_word_lc'] = [[cnt_re(LOWFOLD[i], w) for w in (u'must', u'should', u'may', u'can')]
                     for i in range(NSRC)]
F['tone_word_lc_tot'] = [sum(x) for x in F['tone_word_lc']]
# 第三把尺: 邻居若是数字也算边界(采集遍的 (?<![A-Za-z]) 与字母手扫同档), 两档之差必须逐份归零
F['tone_alnum_gap'] = [sum(ub(T[i], nd, u'alpha') for nd in TONE)
                       - sum(ub(T[i], nd, u'alnum') for nd in TONE) for i in range(NSRC)]
F['tone_ruler_close'] = sum(F['tone_alnum_gap'])
F['tone_wide'] = [[ub(WIDE[i], nd) for nd in TONE] for i in range(NSRC)]
F['tone_wide_re'] = [[cnt_re(WIDE[i], nd) for nd in TONE] for i in range(NSRC)]
F['tone_wide_close'] = sum(sum(abs(F['tone_wide'][i][k] - F['tone_wide_re'][i][k])
                               for k in range(len(TONE))) for i in range(NSRC))
F['tone_sec_per_mille'] = [(1000 * F['tone_sec_tot'][i]) // F['tone_tot'][i] if F['tone_tot'][i] else -1
                           for i in range(NSRC)]

# ---------- 答案句(由段落 ⇎ 句界导出, 一个字符都不手打) ----------
ANS = []
ANS_HEAD = [u'Non-idempotent methods or sequences',
            u'Idempotent methods are distinguished because',
            u'The 429 status code indicates',
            u'User agents that send a request in early data are expected',
            u'A proxy MUST NOT automatically retry']
ANS_PH = [u'sequences MUST NOT be automatically retried',
          u'request can be\nrepeated automatically',
          u'MAY include a Retry-After header indicating how long',
          u'expected to retry\nthe request when receiving a 425',
          u'automatically retrying\nthe requests that failed']
F['ans_ph'] = ANS_PH
for i, pat in enumerate(ANS_HEAD):
    k = T[i].find(pat)
    assert k >= 0, (i, pat)
    ln = len(T[i][:k].split(NL)) - 1
    pl = []
    j = ln
    while j < len(L[i]) and L[i][j].strip() != u'':
        pl.append(j)
        j += 1
    txt, offs = u'', []
    for idx in pl:
        offs.append(len(txt))
        txt += (u'' if txt == u'' else u' ') + fold(L[i][idx])
    st = txt.find(pat)
    assert st >= 0, (i, u'答句起点不在段落折平流里')
    e = sent_ends(txt[st + len(pat):])
    en = st + len(pat) + (e if e is not None else len(txt) - st - len(pat) - 1)
    cover = [kk for kk in range(len(pl))
             if offs[kk] <= en and offs[kk] + len(fold(L[i][pl[kk]])) >= st]
    ANS.append(txt[st:en + 1])
    F.setdefault(u'ans_span', []).append(len(cover))
    F.setdefault(u'ans_first_line', []).append(ln)
    F.setdefault(u'ans_para_span', []).append(len(pl))
    F.setdefault(u'ans_lead_words', []).append(
        len(fold(L[i][ln])[:fold(L[i][ln]).find(pat)].split()) if pat in fold(L[i][ln]) else 0)
    F.setdefault(u'ans_lines_abs', []).append([pl[kk] + 1 for kk in range(len(cover))])
F['ans'] = ANS
F['ans_words'] = [len(x.split()) for x in ANS]
F['ans_one_line_n'] = len([x for x in F['ans_span'] if x == 1])
F['ans_page_break'] = [len([y for y in F['ans_lines_abs'][i] if is_page_shell_pick(L[i][y - 1])])
                       for i in range(NSRC)]
F['ans_para_tail'] = [F['ans_para_span'][i] - F['ans_span'][i] for i in range(NSRC)]
F['ph_line'] = [sum(cnt_re(y.lower(), ANS_PH[i].lower().replace(NL, u' ')) for y in L[i])
                for i in range(NSRC)]
F['ph_fold'] = [cnt_re(LOWFOLD[i], ANS_PH[i].lower().replace(NL, u' ')) for i in range(NSRC)]
F['ph_straddle'] = [F['ph_fold'][i] - F['ph_line'][i] for i in range(NSRC)]
F['ph_raw_line'] = [len([y for y in L[i] if ANS_PH[i] in y]) for i in range(NSRC)]

# ---------- “重来”用词族 ⇎ 判词施事者 ----------
REWORD = [u'retry', u'retrying', u'repeated', u'repeat', u'resubmit', u'try again',
          u'make a new request', u'follow-up request']
RALT = re.compile(u'|'.join(re.escape(x) for x in sorted(REWORD, key=lambda s: -len(s))))
F['reword_fam'] = REWORD
F['reword'] = [[cnt_re(LOWFOLD[i], nd.lower()) for nd in REWORD] for i in range(NSRC)]
F['reword_union'] = [len(RALT.findall(LOWFOLD[i])) for i in range(NSRC)]
F['reword_overlap'] = [sum(F['reword'][i]) - F['reword_union'][i] for i in range(NSRC)]
F['reword_tot'] = [sum(x) for x in F['reword']]
F['reword_zero_n'] = [len([k for k in range(len(REWORD)) if F['reword'][i][k] == 0]) for i in range(NSRC)]
F['reword_own'] = [[REWORD[k] for k in range(len(REWORD)) if F['reword'][i][k]
                   and all(F['reword'][j][k] == 0 for j in range(NSRC) if j != i)] for i in range(NSRC)]

SUBJ = [u'A proxy MUST NOT automatically retry', u'A client SHOULD NOT automatically retry',
        u'user agents MAY offer', u'SHOULD retry automatically', u'MAY automatically retry',
        u'can repeat a POST request automatically', u'might\nautomatically retry a POST',
        u'are expected to retry', u'MUST NOT be automatically retried']
PASSIVE = 8
F['subj_fam'] = SUBJ
F['subj'] = [[cnt_re(FOLD[i], nd.replace(NL, u' ')) for nd in SUBJ] for i in range(NSRC)]
F['subj_line'] = [[sum(cnt_re(y, nd) for y in L[i]) for nd in SUBJ] for i in range(NSRC)]
F['subj_straddle'] = [sum(F['subj'][i]) - sum(F['subj_line'][i]) for i in range(NSRC)]
F['subj_n'] = [len([k for k in range(len(SUBJ)) if F['subj'][i][k]]) for i in range(NSRC)]
F['subj_active'] = [sum(F['subj'][i][:PASSIVE]) for i in range(NSRC)]
F['subj_passive'] = [F['subj'][i][PASSIVE] for i in range(NSRC)]
F['subj_sec'] = [[cnt_re(SECW[i], nd.replace(NL, u' ')) for nd in SUBJ] if SECW[i] else [0] * len(SUBJ)
                  for i in range(NSRC)]
F['subj_sec_tot'] = [sum(x) for x in F['subj_sec']]
F['subj_straddle_k'] = [[F['subj'][i][kk] - F['subj_line'][i][kk] for kk in range(len(SUBJ))]
                        for i in range(NSRC)]
F['subj_straddled'] = [[SUBJ[kk] for kk in range(len(SUBJ)) if F['subj_straddle_k'][i][kk]]
                       for i in range(NSRC)]

ACT = [u'user agent', u'user agents', u'client', u'proxy', u'intermediar', u'origin server', u'server']
F['act_fam'] = ACT
F['act'] = [[cnt_re(LOWFOLD[i], nd) for nd in ACT] for i in range(NSRC)]
F['act_sg'] = [len(re.findall(u'user agent(?!s)', LOWFOLD[i])) for i in range(NSRC)]
F['act_sg_plus_pl'] = [F['act_sg'][i] + F['act'][i][1] - F['act'][i][0] for i in range(NSRC)]
F['act_sec'] = [[cnt_re(SECW[i].lower(), nd) for nd in ACT] if SECW[i] else [0] * len(ACT)
                 for i in range(NSRC)]
F['act_sec_tot'] = [sum(x) for x in F['act_sec']]
F['act_tot'] = [sum(x) for x in F['act']]

NUM = [u'3600', u'120', u'50 requests per hour', u'2 minutes', u'delay-seconds',
       u'delta-seconds', u'HTTP-date']
F['num_fam'] = NUM


def bound_nd(nd):
    return u'digit' if nd.isdigit() else u'alpha'


F['num'] = [[ub(LOWFOLD[i], nd.lower(), bound_nd(nd)) for nd in NUM] for i in range(NSRC)]
F['num_raw'] = [[cnt_re(LOWFOLD[i], nd.lower()) for nd in NUM] for i in range(NSRC)]
F['num_sub'] = [sum(F['num_raw'][i]) - sum(F['num'][i]) for i in range(NSRC)]
F['num_tot'] = [sum(x) for x in F['num']]
F['num_own'] = [[NUM[k] for k in range(len(NUM)) if F['num'][i][k]
                and all(F['num'][j][k] == 0 for j in range(NSRC) if j != i)] for i in range(NSRC)]
F['num_rename'] = [F['num'][i][4] - F['num'][i][5] for i in range(NSRC)]

METH = [u'GET', u'HEAD', u'PUT', u'DELETE', u'POST', u'TRACE', u'OPTIONS', u'CONNECT']
F['meth_fam'] = METH
F['meth_sec'] = [[ub(SECW[i], nd) for nd in METH] if SECW[i] else [0] * len(METH) for i in range(NSRC)]
F['meth_sec_n'] = [len([x for x in F['meth_sec'][i] if x]) for i in range(NSRC)]
F['meth_post_sec'] = [F['meth_sec'][i][4] for i in range(NSRC)]
F['meth_all'] = [[ub(WIDE[i], nd) for nd in METH] for i in range(NSRC)]
F['meth_all_n'] = [len([x for x in F['meth_all'][i] if x]) for i in range(NSRC)]

# ---------- Retry-After 轴(本遍按 “冒号前是这个名字” 手工切行) ----------
F['ra_count'] = [cnt_re(T[i], u'Retry-After') for i in range(NSRC)]


def is_abnf_row(x):
    s = fold(x)
    if not s.startswith(u'Retry-After'):
        return False
    rest = s[len(u'Retry-After'):].lstrip()
    return rest.startswith(u'=')


RABLINE = [[x for x in L[i] if is_abnf_row(x)] for i in range(NSRC)]
F['ra_abnf_lines'] = [len(x) for x in RABLINE]
F['ra_abnf_forms'] = [len(set(fold(x) for x in RABLINE[i])) for i in range(NSRC)]
F['ra_abnf_bar'] = [len([x for x in RABLINE[i] if u'|' in x]) for i in range(NSRC)]
F['ra_abnf_slash'] = [len([x for x in RABLINE[i] if u' / ' in x]) for i in range(NSRC)]
F['ra_abnf_quoted'] = [len([x for x in RABLINE[i] if u'"Retry-After"' in x]) for i in range(NSRC)]
F['ra_abnf_ledger'] = [F['ra_abnf_bar'][i] + F['ra_abnf_slash'][i] - F['ra_abnf_lines'][i]
                       for i in range(NSRC)]
F['ra_exp_date'] = [cnt_re(T[i], u'Retry-After: Fri, 31 Dec 1999 23:59:59 GMT') for i in range(NSRC)]
F['ra_exp_120'] = [cnt_re(T[i], u'Retry-After: 120') for i in range(NSRC)]
F['ra_exp_3600'] = [cnt_re(T[i], u'Retry-After: 3600') for i in range(NSRC)]
F['ra_two_minutes'] = [cnt_re(LOWFOLD[i], u'the delay is 2 minutes') for i in range(NSRC)]
F['ra_delta_def'] = [cnt_re(LOWFOLD[i], u'non-negative decimal integer') for i in range(NSRC)]
F['ra_colon_rows'] = [len([x for x in L[i] if fold(x).startswith(u'Retry-After:')]) for i in range(NSRC)]

# ---------- 反向对照词汇: 谁的答法里根本没有对方的说法 ----------
NEG = [u'429', u'Too Many Requests', u'Too Early', u'Early-Data', u'rate limiting', u'428',
       u'Precondition Required', u'425', u'idempotent']
F['neg_fam'] = NEG
F['neg_digit'] = [k for k, nd in enumerate(NEG) if nd.isdigit()]
F['neg_raw'] = [[cnt_re(T[i], nd) for nd in NEG] for i in range(NSRC)]
F['neg_bnd'] = [[ub(T[i], nd, bound_nd(nd)) for nd in NEG] for i in range(NSRC)]
F['neg_false_sub'] = [sum(F['neg_raw'][i]) - sum(F['neg_bnd'][i]) for i in range(NSRC)]
F['neg_zero_n'] = [len([k for k in range(len(NEG)) if F['neg_bnd'][i][k] == 0]) for i in range(NSRC)]
F['neg_own'] = [[k for k in range(len(NEG)) if F['neg_bnd'][i][k]
                and all(F['neg_bnd'][j][k] == 0 for j in range(NSRC) if j != i)] for i in range(NSRC)]
F['neg_own_lbl'] = [[NEG[k] for k in F['neg_own'][i]] for i in range(NSRC)]
F['neg_tot'] = [sum(x) for x in F['neg_bnd']]

# ---------- 状态码定义行(本遍把行首切成 “节号 ⇎ 码 ⇎ 名字” 三段手工判) ----------
CODES = [u'400', u'401', u'403', u'404', u'405', u'408', u'416', u'428', u'429', u'425', u'431', u'500',
         u'503', u'504', u'505', u'506', u'507', u'508', u'510', u'511']
F['code_fam'] = CODES


def code_row_picklike(x, c):
    """同一定义的直白实现: 行首编号 + 空白 + 码 + 码后不接数字点; 目录行按连点数>=3 剔"""
    s = x.lstrip(u' \t')
    tp, dot = sect_no(s)
    if tp is None:
        return False
    j = len(u'.'.join(str(z) for z in tp)) + (1 if dot else 0)
    if s[j:j + 1] not in (u' ', u'\t'):
        return False
    k = j
    while k < len(s) and s[k] in u' \t':
        k += 1
    rest = s[k:]
    if not rest.startswith(c):
        return False
    nx = rest[len(c):len(c) + 1]
    return not (nx and (nx.isdigit() or nx == u'.'))


CODES_I = [[[x for x in L[i] if code_row_picklike(x, c)] for c in CODES] for i in range(NSRC)]
F['code_defined_raw'] = [len([y for rows in CODES_I[i] for y in rows]) for i in range(NSRC)]
F['code_defined'] = [[len([y for y in rows if u'...' not in y]) for rows in CODES_I[i]] for i in range(NSRC)]
F['code_defined_n'] = [sum(x) for x in F['code_defined']]
F['code_toc'] = [F['code_defined_raw'][i] - F['code_defined_n'][i] for i in range(NSRC)]
F['code_defined_lbl'] = [[CODES[k] for k in range(len(CODES)) if F['code_defined'][i][k]] for i in range(NSRC)]
F['code_absent_lbl'] = [[CODES[k] for k in range(len(CODES)) if not F['code_defined'][i][k]]
                        for i in range(NSRC)]

PAREN = [u'425 (Too Early)', u'428 (Precondition Required)', u'429 (Too Many Requests)']
F['paren_fam'] = PAREN
F['paren'] = [[cnt_re(FOLD[i], nd) for nd in PAREN] for i in range(NSRC)]
F['paren_line'] = [[sum(cnt_re(y, nd) for y in L[i]) for nd in PAREN] for i in range(NSRC)]
F['paren_straddle'] = [sum(F['paren'][i]) - sum(F['paren_line'][i]) for i in range(NSRC)]

# ---------- 逐字搬字: 两把尺(行 ⇎ 句) ----------
def body_rows(i):
    return [fold(x) for x in L[i] if len(x.strip()) >= 30 and not is_shell_pick(x)]


POOL = [body_rows(i) for i in range(NSRC)]
PAIRS = [(a, b) for a, b in IT.combinations(range(NSRC), 2)]
P2 = {}
for a, b in PAIRS:
    P2[u'%s-%s' % (LBL[a], LBL[b])] = len(set(POOL[a]) & set(POOL[b]))
F['pair_shared'] = P2
F['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
F['pair_share'] = [P2[u'%s-%s' % (LBL[a], LBL[b])] for a, b in PAIRS]
F['pair_nonzero'] = len([x for x in F['pair_share'] if x])
F['pair_zero'] = len(PAIRS) - F['pair_nonzero']
F['pair_max_lbl'] = max(P2, key=lambda k: P2[k])
F['pair_max'] = P2[F['pair_max_lbl']]
ML = F['pair_max_lbl'].split(u'-')
F['pair_lbl_idx'] = [LBL.index(ML[0]), LBL.index(ML[1])]
BA, BB = F['pair_lbl_idx']
# 同一份“搬字行”的第三种算法: 折叠键 -> 原始行出处字典(键集与 POOL 同滤, 只是留住了出处)
ORIG = [defaultdict(set) for _ in range(NSRC)]
for i in range(NSRC):
    for x in L[i]:
        if len(x.strip()) >= 30 and not is_shell_pick(x):
            ORIG[i][fold(x)].add(x)
# “逐字节同形”按折叠键计枚, 不按原始行计枚: 一行在两份里各印一次才算一枚, 单位要和 pair_share 一致
F['pair_max_byte_keys'] = len([k for k in ORIG[BA] if k in ORIG[BB] and (ORIG[BA][k] & ORIG[BB][k])])
F['pair_max_norm_only_keys'] = len([k for k in ORIG[BA] if k in ORIG[BB]
                                   and not (ORIG[BA][k] & ORIG[BB][k])])
# 采集侧的第三种单位: 原始行枚数(不折平也不滤壳)减去折平键枚数——两条路的差要能量出来
RA_W = set(x for x in L[BA] if len(x.strip()) >= 30)
RB_W = set(x for x in L[BB] if len(x.strip()) >= 30)
F['pair_max_byte_lines'] = len([x for x in RB_W if x in RA_W])
F['pair_max_norm_only_lines'] = F['pair_max'] - F['pair_max_byte_lines']
F['pair_byte_lines_to_keys'] = len(set(fold(x) for x in (RA_W & RB_W)))
F['pair_byte_unit_gap'] = F['pair_max_byte_lines'] - F['pair_byte_lines_to_keys']
F['pair_byte_shell_gap'] = F['pair_byte_lines_to_keys'] - F['pair_max_byte_keys']
F['pair_byte_lines_ge_keys'] = 1 if F['pair_max_byte_lines'] >= F['pair_max_byte_keys'] else 0
F['pool_n'] = sum(len(x) for x in POOL)
F['pool_union'] = len(set().union(*[set(p) for p in POOL]))
F['pool_rows_minus_union'] = F['pool_n'] - F['pool_union']
PRES = dict((a, tuple(i for i in range(NSRC) if a in set(POOL[i])))
            for s in set().union(*[set(p) for p in POOL]) for a in [s])
F['pool_tier'] = [len([a for a, v in PRES.items() if len(v) == k]) for k in range(1, NSRC + 1)]
F['pool_tier_close'] = sum(F['pool_tier']) - F['pool_union']
_i1 = sum(len(v) for v in PRES.values())
_i2 = sum(len(v) * (len(v) - 1) // 2 for v in PRES.values())
_i3 = sum(len(v) * (len(v) - 1) * (len(v) - 2) // 6 for v in PRES.values())
_i4 = sum(len(v) * (len(v) - 1) * (len(v) - 2) * (len(v) - 3) // 24 for v in PRES.values())
_i5 = len([v for v in PRES.values() if len(v) == 5])
F['pool_incl'] = [_i1, _i2, _i3, _i4, _i5]
F['union_incl'] = _i1 - _i2 + _i3 - _i4 + _i5
F['union_close'] = F['pool_union'] - F['union_incl']
F['pair_byte'] = [len([k for k in ORIG[a] if k in ORIG[b] and (ORIG[a][k] & ORIG[b][k])])
                   for a, b in PAIRS]
F['pair_norm_only'] = [len([k for k in ORIG[a] if k in ORIG[b] and not (ORIG[a][k] & ORIG[b][k])])
                       for a, b in PAIRS]
F['pair_close'] = sum(F['pair_share']) - sum(F['pair_byte']) - sum(F['pair_norm_only'])
F['pair_7231_9110'] = F['pair_share'][PAIRS.index((1, 4))]
F['pair_2616_9110'] = F['pair_share'][PAIRS.index((0, 4))]
F['pair_2616_7231'] = F['pair_share'][PAIRS.index((0, 1))]


def dehyph(s):
    out, j = [], 0
    while j < len(s):
        if s[j] == u'-':
            j += 1
            while j < len(s) and s[j] in u' \t':
                j += 1
            continue
        out.append(s[j])
        j += 1
    return u''.join(out).lower()


RANK = {u'case': 0, u'hyph': 1, u'space': 2, u'multi': 3}


def bucket(o, p):
    if o.lower() == p.lower():
        return u'case'
    if dehyph(o) == dehyph(p):
        return u'hyph'
    if o.strip() == p.strip():
        return u'space'
    return u'multi'


axis = dict((w, 0) for w in RANK)
NORM_ONLY = []
BSAME = []
SHR = sorted(set(POOL[BA]) & set(POOL[BB]))
VAR = {}
for a in SHR:
    va = ORIG[BA][a]
    vb = ORIG[BB][a]
    VAR[a] = (va, vb)
    if va & vb:
        BSAME.append(a)
        continue
    dif = [(o, q) for o in va for q in vb]
    NORM_ONLY.append(a)
    axis[min((bucket(o, q) for o, q in dif), key=lambda w: RANK[w])] += 1
F['axis_counts'] = axis
F['axis_total'] = sum(axis.values())
F['axis_rows'] = NORM_ONLY
F['pair_pool_byte'] = len(BSAME)
F['pair_pool_norm_only'] = len(NORM_ONLY)
# 同一本“搬字账”两条独立算法: 原始行集逐字节相交 ⇎ 池内逐行比变体形状, 两条的“同形/异形”分档必须重合
F['axis_close'] = (F['pair_max'] - F['pair_pool_byte'] - F['pair_pool_norm_only']
                   + abs(F['pair_max_byte_keys'] - F['pair_pool_byte'])
                   + abs(F['pair_max_norm_only_keys'] - F['pair_pool_norm_only']))
F['axis_str'] = u' ⇎ '.join(u'%s%d' % (w, axis[w]) for w in (u'case', u'hyph', u'space', u'multi'))
F['axis_str_n'] = len([w for w in axis if axis[w]])


def sents(face):
    return [u' '.join(x.lower().split()) for x in
            re.split(u'(?<=[.!?])\\s+(?=[A-Z0-9*<(])', face)]


SP = [set(x for x in sents(WIDE[i]) if len(x) >= 40) for i in range(NSRC)]
SPRES = dict((a, tuple(i for i in range(NSRC) if a in SP[i])) for s in SP for a in s)
F['s_pool_n'] = len(SPRES)
F['s_pool_tier'] = [len([a for a, v in SPRES.items() if len(v) == k]) for k in range(1, NSRC + 1)]
F['s_pool_tier_close'] = sum(F['s_pool_tier']) - F['s_pool_n']
F['s_pair_share'] = [len(SP[a] & SP[b]) for a, b in PAIRS]
F['s_pair_max'] = max(F['s_pair_share'])
F['s_pair_max_idx'] = F['s_pair_share'].index(F['s_pair_max'])
F['s_pair_max_lbl'] = F['pair_lbl'][F['s_pair_max_idx']]
F['s_pair_7231_9110'] = F['s_pair_share'][PAIRS.index((1, 4))]
F['s_pair_2616_9110'] = F['s_pair_share'][PAIRS.index((0, 4))]
F['s_ruler_gain_7231_9110'] = F['s_pair_7231_9110'] - F['pair_7231_9110']
F['s_ruler_gain_2616_9110'] = F['s_pair_2616_9110'] - F['pair_2616_9110']
F['s_pair_nonzero'] = len([x for x in F['s_pair_share'] if x])
_s1 = sum(len(SP[i]) for i in range(NSRC))
_s2 = sum(len(v) * (len(v) - 1) // 2 for v in SPRES.values())
_s3 = sum(len(v) * (len(v) - 1) * (len(v) - 2) // 6 for v in SPRES.values())
_s4 = sum(len(v) * (len(v) - 1) * (len(v) - 2) * (len(v) - 3) // 24 for v in SPRES.values())
_s5 = len([v for v in SPRES.values() if len(v) == 5])
F['s_incl'] = [_s1, _s2, _s3, _s4, _s5]
F['s_union_incl'] = _s1 - _s2 + _s3 - _s4 + _s5
F['s_union_close'] = F['s_pool_n'] - F['s_union_incl']

# ---------- 锚候选池 ----------
apool = []
for i in range(NSRC):
    for x in SHP[i]:
        if len(pnorm(x)) >= 24 and re.search(u'[A-Za-z]', x):
            apool.append((pnorm(x), i))
AP = defaultdict(set)
for a, i in apool:
    AP[a].add(i)
F['apool_n'] = len(AP)
F['apool_raw_n'] = len(apool)
F['apool_face_raw'] = [len([1 for a, k in apool if k == i]) for i in range(NSRC)]
F['apool_tag_n'] = [len([a for a, v in AP.items() if i in v]) for i in range(NSRC)]
F['apool_dup'] = [F['apool_face_raw'][i] - F['apool_tag_n'][i] for i in range(NSRC)]
F['apool_tag_close'] = sum(F['apool_tag_n']) + sum(F['apool_dup']) - F['apool_raw_n']
F['apool_tier'] = [len([a for a, v in AP.items() if len(v) == n]) for n in range(1, NSRC + 1)]
F['apool_weight'] = sum(F['apool_tier'][n] * (n + 1) for n in range(NSRC))
F['apool_pairs'] = sum(F['apool_tag_n'])
F['apool_tier_close'] = F['apool_weight'] - F['apool_pairs']
F['apool_maxlen'] = max(len(a) for a in AP)

# ---------- 序列化式子(只在逐行原面上分得出) ----------
def hdr_form(x):
    """编号标题行的三种印法: 尾点后两个空格 ⇎ 一个空格 ⇎ 无尾点直接空格(本遍手工切段判)"""
    s = x.lstrip(u' \t')
    tp, dot = sect_no(s)
    if tp is None or len(tp) < 2:
        return None
    j = len(u'.'.join(str(z) for z in tp)) + (1 if dot else 0)
    sp = 0
    while j + sp < len(s) and s[j + sp] == u' ':
        sp += 1
    if sp == 0 or j + sp >= len(s) or s[j + sp].isspace():
        return None
    if dot and sp == 2:
        return u'dot2sp'
    if dot and sp == 1:
        return u'dot1sp'
    if not dot and sp == 1:
        return u'nodot'
    return None


HF = [[hdr_form(x) for x in L[i]] for i in range(NSRC)]
F['hdr_dot2sp'] = [len([1 for h in HF[i] if h == u'dot2sp']) for i in range(NSRC)]
F['hdr_dot1sp'] = [len([1 for h in HF[i] if h == u'dot1sp']) for i in range(NSRC)]
F['hdr_nodot'] = [len([1 for h in HF[i] if h == u'nodot']) for i in range(NSRC)]
F['dblspace_in_fold'] = [cnt_re(FOLD[i], u'  ') for i in range(NSRC)]
F['dot_dblspace_anywhere'] = [len(re.findall(u'\\S\\.  \\S', FOLD[i])) for i in range(NSRC)]
F['hyphen_break'] = [len([1 for j in range(len(L[i]) - 1)
                          if L[i][j].rstrip().endswith(u'-')
                          and re.match(u'^\\s*[a-z]', L[i][j + 1])]) for i in range(NSRC)]

# ---------- 锚句: 由起止针在指定面上导出, 不手打 ----------
FACEI = {u'strict': 0, u'fold': 1, u'sh': 2, u'sec': 3}
FACE = {u'strict': L, u'fold': FOLD, u'sh': SH, u'sec': SECW}


def mk_nd(o, s0, e0, fa):
    if s0.startswith(u'@'):
        return s0[1:]
    face = FACE[fa][o]
    a = face.find(s0)
    assert a >= 0, (u'起针落空', LBL[o], fa, s0)
    if not e0:
        return s0
    b = face.find(e0, a)
    assert b >= 0, (u'止针落空', LBL[o], fa, e0)
    return face[a:b + len(e0)]


SENT = [
    (0, u'a2616_passive', u'sh', u'Non-idempotent methods or sequences', u'the request(s).'),
    (0, u'a2616_repeat', u'sh', u'The automatic retry SHOULD NOT be repeated', u'of requests fails.'),
    (0, u'a2616_confirm', u'sh', u'Confirmation by user-agent software', u'for user confirmation.'),
    (0, u'a2616_defin', u'sec', u'Methods can also have the property of', u'share this property.'),
    (0, u'a2616_sidefx', u'sec', u'Also, the methods OPTIONS and', u'inherently idempotent.'),
    (0, u'a2616_nonidem', u'sec', u'However, it is possible that a sequence', u'non- idempotent'),
    (0, u'a2616_abnf', u'sh', u'Retry-After = "Retry-After"', u'delta-seconds )'),
    (0, u'a2616_120', u'sh', u'Retry-After: 120', u''),
    (0, u'a2616_dsec', u'sh', u'delta-seconds = 1*DIGIT', u''),
    (0, u'n2616_3600', u'sh', u'@Retry-After: 3600', u''),
    (0, u'n2616_proxy', u'sh', u'@A proxy MUST NOT automatically retry', u''),
    (0, u'n2616_429', u'sh', u'@429', u''),
    (1, u'a7231_idem', u'sec', u'Idempotent methods are distinguished', u"server's response."),
    (1, u'a7231_put', u'sec', u'For example, if a client sends a PUT request', u'the idempotent request.'),
    (1, u'a7231_like', u'sec', u'Like the definition of safe', u'each idempotent request.'),
    (1, u'a7231_abnf', u'sh', u'Retry-After = HTTP-date / delay-seconds', u''),
    (1, u'a7231_delaydef', u'sh', u'delay-seconds = 1*DIGIT', u''),
    (1, u'n7231_proxy', u'sh', u'@A proxy MUST NOT automatically retry', u''),
    (1, u'n7231_429', u'sh', u'@429', u''),
    (1, u'n7231_3600', u'sh', u'@Retry-After: 3600', u''),
    (2, u'a6585_429', u'sh', u'The 429 status code indicates', u'making a new request.'),
    (2, u'a6585_3600', u'sh', u'Retry-After: 3600', u''),
    (2, u'a6585_50', u'sh', u'I only allow 50 requests per hour', u'Try again soon.'),
    (2, u'a6585_selfdeny', u'sh', u'Note that this specification does not define', u'stateful cookie.'),
    (2, u'a6585_nocache', u'sh', u'Responses with the 429 status code MUST NOT be stored by a cache.', u''),
    (2, u'a6585_428', u'sh', u'The 428 status code indicates', u'using "If-Match".'),
    (2, u'a6585_resub', u'sh', u'Responses using this status code SHOULD explain',
     u'request successfully.'),
    (2, u'n6585_auto', u'sh', u'@automatically', u''),
    (2, u'n6585_idem', u'sh', u'@idempotent', u''),
    (3, u'a8470_425def', u'sh', u'A 425 (Too Early) status code indicates', u'might be replayed.'),
    (3, u'a8470_expect', u'sh', u'User agents that send a request in early data are expected',
     u'response status code.'),
    (3, u'a8470_should', u'sh', u'A user agent SHOULD retry automatically', u'sent in early data.'),
    (3, u'a8470_mw', u'sh', u'Otherwise, an intermediary that receives a request in early data',
     u'received the request.'),
    (3, u'a8470_assume', u'sh', u'The server cannot assume that a client is able to retry',
     u'one of these conditions is met.'),
    (3, u'n8470_idem', u'sh', u'@idempotent', u''),
    (3, u'n8470_429', u'sh', u'@429', u''),
    (3, u'n8470_3600', u'sh', u'@Retry-After: 3600', u''),
    (4, u'a9110_idem', u'sec', u'Idempotent methods are distinguished', u"server's response."),
    (4, u'a9110_like', u'sec', u'Like the definition of safe', u'each idempotent request.'),
    (4, u'a9110_proxy', u'sec', u'A proxy MUST NOT automatically retry non-idempotent requests.', u''),
    (4, u'a9110_client', u'sec', u'A client SHOULD NOT automatically retry a failed automatic retry.', u''),
    (4, u'a9110_post', u'sec', u'a user agent can repeat a POST request automatically',
     u'safe for that resource.'),
    (4, u'a9110_vcs', u'sec', u'a user agent designed specifically to operate', u'requests that failed.'),
    (4, u'a9110_risk', u'sec', u'Some clients take a riskier approach', u'automatic retry is possible.'),
    (4, u'a9110_might', u'sec', u'a client might automatically retry a POST request',
     u'persistent connection was used.'),
    (4, u'n9110_429', u'sh', u'@429', u''),
    (4, u'n9110_428', u'sh', u'@428 (Precondition Required)', u''),
    (4, u'n9110_3600', u'sh', u'@Retry-After: 3600', u''),
]
TEXT = {}
NEGND = [k for o, k, fa, s0, e0 in SENT if s0.startswith(u'@')]
for (o, k, fa, s0, e0) in SENT:
    TEXT[k] = s0[1:] if k in NEGND else mk_nd(o, s0, e0, fa)
OWNER = dict((k, o) for o, k, _, _, _ in SENT)
GN = [k for o, k, _, _, _ in SENT]
LITK.update(TEXT)
TIERN = {0: u'strict', 1: u'fold', 2: u'sh', 3: u'sec'}


def hit_face(k, tier):
    nd = TEXT[k]
    o = OWNER[k]
    if not nd:
        return 0
    if tier == 0:
        return len([x for x in L[o] if nd in x])
    return cnt_re(FACE[TIERN[tier]][o], nd)


SN = dict((k, [hit_face(k, n) for n in range(4)]) for k in GN)
FAI = {u'strict': 0, u'fold': 1, u'sh': 2, u'sec': 3}
for o, k, fa, s0, e0 in SENT:
    if k in NEGND:
        assert max(SN[k]) == 0, (k, SN[k])
        continue
    assert TEXT[k] in FACE[fa][o], k
    assert SN[k][FAI[fa]] > 0, k
F['needle_n'] = len(GN)
F['neg_n'] = len(NEGND)
for n in range(4):
    F[u'sn_' + TIERN[n] + u'_docs'] = [len([k for k in GN if OWNER[k] == i and SN[k][n]])
                                       for i in range(NSRC)]
for k in GN:
    F[u'n_' + k] = SN[k]
F['needles_owned'] = [len([k for k in GN if OWNER[k] == i]) for i in range(NSRC)]
F['fold_minus_strict_keys'] = [k for k in GN if not SN[k][0] and SN[k][1]]
F['fold_minus_strict_own'] = [len([k for k in F['fold_minus_strict_keys'] if OWNER[k] == i])
                              for i in range(NSRC)]
F['fold_minus_strict_n'] = len(F['fold_minus_strict_keys'])
F['sh_loses_keys'] = [k for k in GN if SN[k][1] and not SN[k][2]]
F['sh_gains_keys'] = [k for k in GN if SN[k][2] and not SN[k][1]]
F['sh_loses'] = [len([k for k in F['sh_loses_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['sh_gains'] = [len([k for k in F['sh_gains_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['sec_scope'] = [1 if SECW[i] else 0 for i in range(NSRC)]
F['sh_no_sec_keys'] = [k for k in GN if SN[k][2] and not SN[k][3] and F['sec_scope'][OWNER[k]]]
F['sh_no_sec_own'] = [len([k for k in F['sh_no_sec_keys'] if OWNER[k] == i]) for i in range(NSRC)]
F['sh_no_sec_n'] = len(F['sh_no_sec_keys'])
F['sn_sec_docs_scope'] = [F['sn_sec_docs'][i] if SECW[i] else -1 for i in range(NSRC)]
F['dead_needles'] = [k for k in GN if k not in NEGND and max(SN[k]) == 0]
F['neg_controls'] = sorted(NEGND)
F['neg_own_nd'] = [len([k for k in NEGND if OWNER[k] == i]) for i in range(NSRC)]
F['neg_hit_widest'] = sum(max(SN[k]) for k in NEGND)
F['neg_hit_strict'] = sum(SN[k][0] for k in NEGND)
F['strict_neg_own'] = [len([k for k in NEGND if OWNER[k] == i and SN[k][0]]) for i in range(NSRC)]
F['fold_neg_own'] = [len([k for k in NEGND if OWNER[k] == i and SN[k][1]]) for i in range(NSRC)]
F['ladder_close'] = sum(
    abs(F['sn_strict_docs'][i] + F['fold_minus_strict_own'][i] + F['strict_neg_own'][i]
        - F['sn_fold_docs'][i] - F['fold_neg_own'][i])
    + abs(F['sn_fold_docs'][i] - F['sh_loses'][i] + F['sh_gains'][i] - F['sn_sh_docs'][i])
    + (0 if not SECW[i] else
       abs(F['sn_sh_docs'][i] - F['sh_no_sec_own'][i] - F['sn_sec_docs'][i]))
    for i in range(NSRC))
F['ladder_monotone'] = 1 if all(F['sn_strict_docs'][i] <= F['sn_fold_docs'][i]
                                and F['sn_sec_docs'][i] <= F['sn_sh_docs'][i] for i in range(NSRC)) else 0
F['overlap_extra'] = sum(cnt_ovl(WIDE[OWNER[k]], TEXT[k]) - cnt_cur(WIDE[OWNER[k]], TEXT[k])
                         for k in GN if TEXT[k] and k not in NEGND)
F['re_eq_cur'] = 1 if all(cnt_re(FACES[n][OWNER[k]], TEXT[k]) == cnt_cur(FACES[n][OWNER[k]], TEXT[k])
                          for k in GN if TEXT[k] and k not in NEGND for n in range(1, 3)) else 0
F['nd_len'] = [len(TEXT[k]) for k in GN]
F['nd_len_tot'] = sum(F['nd_len'])
F['nd_len_max'] = max(F['nd_len'])
# 同一句在两代规范里逐字相同 ⇎ 各自被切在哪些行
F['idem_sent_same'] = 1 if TEXT[u'a7231_idem'] == TEXT[u'a9110_idem'] else 0
F['idem_line_7231'] = len(T[1][:T[1].find(u"Idempotent methods are distinguished")].split(NL))
F['idem_line_9110'] = len(T[4][:T[4].find(u"Idempotent methods are distinguished")].split(NL))
F['idem_shift'] = F['idem_line_9110'] - F['idem_line_7231']
F['idem_wrap_7231'] = len([y for y in L[1] if u'Idempotent methods are distinguished' in y])
F['idem_wrap_9110'] = len([y for y in L[4] if u'Idempotent methods are distinguished' in y])
# 9110 从 7231 整段搬来的另一句: 逐字相同, 行号各自被切在不同的行上
F['like_sent_same'] = 1 if TEXT[u'a7231_like'] == TEXT[u'a9110_like'] else 0
F['like_line_7231'] = len([j + 1 for j, y in enumerate(L[1])
                           if u'Like the definition of safe' in y])
F['like_abs_7231'] = [j + 1 for j, y in enumerate(L[1]) if u'Like the definition of safe' in y][0]
F['like_abs_9110'] = [j + 1 for j, y in enumerate(L[4]) if u'Like the definition of safe' in y][0]
F['like_shift'] = F['like_abs_9110'] - F['like_abs_7231']
F['like_hit_sh'] = [SN[u'a7231_like'][2], SN[u'a9110_like'][2]]
# 2616 的同一定义换了措辞: 7231/9110 那句在 2616 的面上读不到, 反之亦然
F['like_absent_2616'] = cnt_re(SH[0], TEXT[u'a7231_like'])
F['defin_absent_7231'] = cnt_re(FOLD[1], TEXT[u'a2616_defin'])
F['nonidem_straddle'] = SN[u'a2616_nonidem']
F['sidefx_in_sec'] = SN[u'a2616_sidefx'][3]

# ---------- 2616 的“判词住在别节”: §8.2.3 给判词, §9.1.2 只给定义, 中间靠一句交叉引用接上 ----------
VKEY = [u'a2616_passive', u'a2616_repeat', u'a2616_confirm']
F['v_keys'] = VKEY
F['v_in_sh'] = len([k for k in VKEY if SN[k][2]])
F['v_in_sec'] = len([k for k in VKEY if SN[k][3]])
F['v_sh_no_sec'] = len([k for k in VKEY if k in F['sh_no_sec_keys']])
F['defin_in_sec'] = SN[u'a2616_defin'][3]
F['defin_in_sh'] = SN[u'a2616_defin'][2]
F['xref_line'] = len([1 for y in L[0] if u'see section 9.1.2' in y])
XREF = [j + 1 for j, y in enumerate(L[0]) if u'see section 9.1.2' in y]
F['xref_lines_abs'] = XREF
F['xref_to_head'] = [F['sec_body_line'][0] - z for z in XREF]
F['verdict_lines_abs'] = [j + 1 for j, y in enumerate(L[0])
                          if u'Non-idempotent methods or sequences' in y]
F['verdict_head_gap'] = F['sec_body_line'][0] - F['verdict_lines_abs'][0]
# 判词与指向定义的交叉引用印在同一行(2601): 行尺上二者同址, 节尺上分属两节
F['verdict_xref_same_line'] = 1 if all(any(v == z for z in XREF)
                                       for v in F['verdict_lines_abs']) else 0
# 9110 反过来: 判词与定义同在一节里, 故节窗档读得到自己名下的全部判词
K9 = [k for k in GN if OWNER[k] == 4 and k not in NEGND]
F['k9110_in_sec'] = len([k for k in K9 if SN[k][3]])
F['k9110_tot'] = len(K9)
F['k9110_no_sec'] = len([k for k in K9 if SN[k][2] and not SN[k][3]])

print(u'第二遍量测(前半)完成: 键 %d ｜ 锚 %d(反向 %d) ｜ 四档 %s/%s/%s/%s' % (
    len(F), F['needle_n'], F['neg_n'], F['sn_strict_docs'], F['sn_fold_docs'], F['sn_sh_docs'],
    F['sn_sec_docs']))
print(u'  节窗 %s ⇎ 节号 %s ⇎ 节尾 %s ⇎ 行数 %s ⇎ 词数 %s ⇎ 句数 %s/%s(差 %s)' % (
    [x if x else u'—' for x in F['sec_body_line']], F['sec_no'], F['sec_end_head'],
    F['sec_lines'], F['sec_words'], F['sec_sents'], F['sec_sents_scan'], F['sec_sents_gap']))
print(u'  2616 判词: 摘壳 %d ⇎ 节窗 %d ⇎ 交叉引用 %s(距节头 %s) ⇎ 判词行 %s(距节头 %d) ⇎ 9110 节内 %d/%d' % (
    F['v_in_sh'], F['v_in_sec'], F['xref_lines_abs'], F['xref_to_head'],
    F['verdict_lines_abs'], F['verdict_head_gap'], F['k9110_in_sec'], F['k9110_tot']))
print(u'  折行独有 %s(计 %d) ⇎ 摘壳节外 %s(计 %d) ⇎ 死锚 %s ⇎ 阶梯单调 %d ⇎ 重叠多读 %d ⇎ 正则=游标 %d' % (
    F['fold_minus_strict_keys'], F['fold_minus_strict_n'], F['sh_no_sec_keys'], F['sh_no_sec_n'],
    F['dead_needles'], F['ladder_monotone'], F['overlap_extra'], F['re_eq_cur']))
print(u'  折平丢 %s ｜ 摘壳救回 %s ｜ 阶梯账 %d ⇎ 单调 %d' % (
    F['sh_loses_keys'], F['sh_gains_keys'], F['ladder_close'], F['ladder_monotone']))

# ---------- 恒等式登记: 每条都由上面的现读数导出, 改一个比较符就能失败 ----------
CLOSE = {}
CLOSE[u'dead_needles_none'] = 0 if len(F['dead_needles']) else 1
CLOSE[u'all_faces_read'] = 1 if all(max(SN[k]) > 0 for k in GN if k not in NEGND) else 0
CLOSE[u'neg_all_cold'] = 0 if (F['neg_hit_widest'] or F['neg_n'] != len(F['neg_controls'])) else 1
CLOSE[u'sec_scope_three'] = 1 if sum(F['sec_scope']) == 3 and F['sec_found_n'] == 3 else 0
CLOSE[u'v2616_outside_own_sec'] = 1 if (F['v_in_sec'] == 0 and F['v_in_sh'] == 3
                                        and F['defin_in_sec'] and F['sidefx_in_sec']) else 0
CLOSE[u'k9110_inside_sec'] = 1 if F['k9110_no_sec'] == 0 and F['k9110_in_sec'] == F['k9110_tot'] else 0
CLOSE[u'tone_zero_7231_sec'] = 1 if sum(F['tone_sec'][1]) == 0 and sum(F['tone_sec'][0]) else 0
CLOSE[u'no_auto_vocab_6585'] = 1 if (F['auto_tot_fold'][2] == 0 and F['auto_bare'][2] == 0) else 0
CLOSE[u'no_retry_after_8470'] = 1 if (F['ra_count'][3] == 0 and F['ra_abnf_lines'][3] == 0) else 0
CLOSE[u'no_code_def_8470'] = 1 if (F['code_defined_n'][3] == 0 and F['paren'][3][0]) else 0
CLOSE[u'neither_428_429_in_9110'] = 1 if (F['code_defined'][4][7] == 0
                                          and F['code_defined'][4][8] == 0) else 0
CLOSE[u'neither_428_429_in_2616'] = 1 if (F['code_defined'][0][7] == 0
                                          and F['code_defined'][0][8] == 0) else 0
CLOSE[u'rename_delta_vs_delay'] = 1 if (F['num'][0][4] == 0 and F['num'][0][5] == 8
                                        and F['num'][1][4] == 6 and F['num'][1][5] == 0
                                        and F['num'][4][4] == 6 and F['num'][4][5] == 0) else 0
CLOSE[u'subj_only_passive_2616'] = 1 if (F['subj_passive'] == [1, 0, 0, 0, 0]
                                         and F['subj_active'][0] == 1
                                         and F['subj_active'][1] == 0
                                         and F['subj_active'][2] == 0) else 0
CLOSE[u'act_sec_only_two_docs'] = 1 if (F['act_sec_tot'][0] == 0 and F['act_sec_tot'][2] == 0
                                        and F['act_sec_tot'][3] == 0 and F['act_sec_tot'][1]
                                        and F['act_sec_tot'][4]) else 0
CLOSE[u'all_txt_no_html'] = 1 if (F['txt_n'] == NSRC and F['html_n'] == 0
                                  and sum(F['tag_close']) == F['tag_close'][2]
                                  and F['tag_close'][2] > 0) else 0
CLOSE[u'ascii_except_9110'] = 1 if (sum(F['nonascii'][:4]) == 0 and F['nonascii'][4] == 30
                                    and sum(F['byte_cp_delta'][:4]) == 0) else 0
CLOSE[u'pageless_9110_only'] = 1 if sum(F['pageless']) == 1 and F['pageless'][4] == 1 else 0
CLOSE[u'sh_equals_fold_for_9110'] = 1 if F['sh_char_gap'][4] == 0 else 0
CLOSE[u'one_maxlen_outlier'] = 1 if sum(F['over72']) == F['over72'][1] == 1 else 0
CLOSE[u'year_one_inversion'] = 1 if F['year_inversions'] == 1 and F['year_span'] == 23 else 0
CLOSE[u'ph_straddle_except_6585'] = 1 if (F['ph_line'] == [0, 0, 1, 0, 0]
                                          and sum(F['ph_fold']) == NSRC) else 0
CLOSE[u'ans_span_shape'] = 1 if F['ans_span'] == [3, 3, 2, 2, 1] else 0
CLOSE[u'no_page_break_in_answer'] = 1 if sum(F['ans_page_break']) == 0 else 0
CLOSE[u'axis_two_buckets_used'] = 1 if F['axis_str_n'] == 2 else 0
CLOSE[u'pair_all_share'] = 1 if F['pair_nonzero'] == len(F['pair_lbl']) and F['pair_zero'] == 0 else 0
CLOSE[u'hyphen_break_only_two'] = 1 if (F['hyphen_break'][2] == 0 and F['hyphen_break'][3] == 0
                                        and F['hyphen_break'][0] and F['hyphen_break'][4]) else 0
CLOSE[u'dblspace_hidden_by_fold'] = 1 if (sum(F['dblspace_in_fold']) == 0
                                          and sum(F['hdr_dot2sp']) > 0) else 0
for k in CLOSE:
    F[k] = 1 if CLOSE[k] else 0

ZID = []


def Z(expr, what):
    ZID.append((expr, what))


Z(u"F['ladder_close']", u'四档阶梯逐份进出账: 逐行+折行独有=折平, 折平−丢+救=摘壳, 摘壳−节外=节窗')
Z(u"F['ladder_monotone'] - 1", u'每份的档读数只增不减(逐行≤折平, 节窗≤摘壳)')
Z(u"F['re_eq_cur'] - 1", u'正则转义轨与游标 find 轨在折平/摘壳两档逐枚相等')
Z(u"F['overlap_extra']", u'重叠口径减非重叠口径在全库锚句上合计为零')
Z(u"len(F['dead_needles'])", u'死集为空: 每枚内容锚句都在某一档读得到')
Z(u"sum(F['needles_owned']) - F['needle_n']", u'锚句按份分账=总数')
Z(u"sum(F['neg_own_nd']) - F['neg_n']", u'反向对照针按份分账=总数')
Z(u"F['needle_n'] - F['neg_n'] - 34", u'锚表 48 行 = 34 枚内容针 + 14 枚反向针')
Z(u"F['neg_hit_widest'] + F['neg_hit_strict']", u'反向针在最宽档与最窄档都零命中')
Z(u"sum(F['fold_minus_strict_own']) - F['fold_minus_strict_n']", u'折行独有针按份分账=总数')
Z(u"sum(F['sh_loses'])", u'摘壳档一枚也不丢(壳行里本来就没有答句)')
Z(u"sum(F['sh_gains']) - 1", u'全库恰一枚针只有摘壳档读得到(6585 的 428 定义段跨页)')
Z(u"sum(F['sh_no_sec_own']) - F['sh_no_sec_n']", u'节外针按份分账=总数')
Z(u"sum(F['sn_sh_docs']) - (F['needle_n'] - F['neg_n'])", u'摘壳档读到的枚数合计=内容针总数')
Z(u"F['v_in_sec']", u'2616 的三枚判词在它自己的幂等节窗里一枚也读不到')
Z(u"F['v_in_sh'] - 3", u'同样三枚判词在摘壳档全读得到')
Z(u"F['v_sh_no_sec'] - 3", u'这三枚都记入“节外”账')
Z(u"F['k9110_no_sec']", u'9110 名下判词一枚也不在节外')
Z(u"F['k9110_in_sec'] - F['k9110_tot']", u'9110 的全部内容针都在 §9.2.2 之内')
Z(u"F['defin_in_sec'] - 1", u'2616 的幂等定义句确实住在 §9.1.2')
Z(u"F['verdict_xref_same_line'] - 1", u'判词与“(see section 9.1.2)”印在同一行')
Z(u"F['xref_line'] - 2", u'2616 全文两处指向 §9.1.2')
Z(u"F['verdict_head_gap'] - 244", u'判词行到 §9.1.2 标题行距 244 行')
Z(u"F['xref_to_head'][1] - F['verdict_head_gap']", u'两处交叉引用里后一处就在判词行')
Z(u"F['idem_sent_same'] - 1", u'7231 与 9110 的“Idempotent methods are distinguished”逐字相同')
Z(u"F['like_sent_same'] - 1", u'7231 与 9110 的“Like the definition of safe”逐字相同')
Z(u"F['like_absent_2616']", u'7231 那句定义在 2616 面上读不到(2616 换了措辞)')
Z(u"F['defin_absent_7231']", u'2616 那句定义在 7231 面上读不到')
Z(u"F['idem_wrap_7231'] + F['idem_wrap_9110'] - 2", u'同一句在两份里各只印一次(没有第二种切法)')
Z(u"F['idem_shift'] - F['like_shift']", u'同段搬字的两句行距位移相等')
Z(u"F['nonidem_straddle'][0]", u'2616 的“非幂等序列”被连字符换行切开: 逐行档零枚')
Z(u"F['sidefx_in_sec'] - 1", u'OPTIONS/TRACE 那句副作用禁令在 2616 的节窗内')
Z(u"sum(F['sec_sents_gap'])", u'节内句数两轨(正则 .\\s ⇎ 逐字符扫)逐份相等')
Z(u"F['sec_found_n'] + F['sec_absent_n'] - NSRC", u'有幂等节⇎无幂等节相加=五份')
Z(u"sum(F['sec_hit_n']) - (F['sec_found_n'] + 1)", u'同名标题命中数=有节的份数+恰一行目录')
Z(u"F['sec_row_dup'][4] - 1", u'9110 的目录行与正文行恰差一处')
Z(u"F['sec_toc_line'][4] - 182", u'9110 的目录命中印在第 182 行')
Z(u"sum(F['tone_must_ledger'])", u'大写 MUST = MUST NOT + 裸 MUST, 五份各自账平')
Z(u"F['tone_ruler_close']", u'字母边界尺与字母数字边界尺在大写族上逐份同值')
Z(u"F['tone_wide_close']", u'手扫轨与正则轨在摘壳面上逐枚相等')
Z(u"F['tone_straddle'][0] + F['tone_straddle'][1] - 4", u'被换行切开的义务词: 2616 三枚 ⇎ 7231 一枚')
Z(u"F['tone_straddle'][2] + F['tone_straddle'][3]", u'6585 与 8470 零枚义务词被切开')
Z(u"sum([sum(F['tone_sec'][i]) for i in (1, 2, 3)])", u'7231/6585/8470 的幂等节窗里一枚义务词也没有')
Z(u"F['tone_sec_tot'][0] + F['tone_sec_tot'][4] - 8", u'节内义务词只有两份: 2616 两枚 ⇎ 9110 六枚')
Z(u"sum(F['hyb_straddle'])", u'non-idempotent 的连字符断开没有造成任何计数损失')
Z(u"F['idem_str'][2] + F['idem_str'][3]", u'6585 与 8470 面上零枚 idempotent')
Z(u"F['auto_tot_fold'][2]", u'6585 的 automat*×retry 族零枚: 它压根不说“自动重来”')
Z(u"sum(F['auto_sh_minus_fold'])", u'摘壳后自动重试族一枚不多一枚不少')
Z(u"sum(F['auto_gain'])", u'折平相对逐行没有增益(六枚族针都不跨行)')
Z(u"sum(F['auto_rows_minus_occ'])", u'族针按行数与按出现处两档逐份相等')
Z(u"sum(F['auto_fam_overlap']) - F['auto_fam_overlap'][4]", u'族内互相包含只发生在 9110 一份里')
Z(u"sum([len(x) for x in F['reword_own']])", u'“重来”用词族没有一枚只属于某一份')
Z(u"sum(F['reword'][i][6] for i in range(5))", u'零枚文档写 “make a new request”(6585 写 making)')
Z(u"F['reword_overlap'][0] - 3", u'2616 的“重来”族内互相包含三枚(retry/repeating/retried 同词根)')
Z(u"F['reword_zero_n'][3] - 6", u'8470 的八枚“重来”说法里六枚一次也没用')
Z(u"sum(F['num_sub'])", u'带边界尺与裸串尺在数字族上逐枚相等(无子串假阳性)')
Z(u"F['num'][0][4] + F['num'][1][5] + F['num'][4][5]",
  u'单位名换代完全分家: 2616 只写 delta-seconds, 7231/9110 只写 delay-seconds')
Z(u"sum([len(x) for x in F['num_own']]) - 2",
  u'数字族里恰两枚只属于一份(2616 的 delta-seconds ⇎ 6585 的 50 requests per hour)')
Z(u"F['subj_active'][1] + F['subj_active'][2]", u'7231 与 6585 的判词不点任何施事者的名')
Z(u"sum(F['subj_passive']) - 1", u'被动式判词全库恰一枚(2616)')
Z(u"sum(F['subj_sec_tot']) - F['subj_sec_tot'][4]", u'节窗内的判词族全部属于 9110')
Z(u"sum(F['subj_straddle']) - 2", u'两枚判词短语被换行切开, 都在 9110 名下')
Z(u"len(F['subj_straddled'][4]) - 2", u'被切开的短语清单恰两枚')
Z(u"sum(F['act_sg_plus_pl'])", u'零宽尺下 user agent 单数+复数−子串=逐份归零')
Z(u"F['act_sec_tot'][0] + F['act_sec_tot'][2] + F['act_sec_tot'][3]",
  u'2616/6585/8470 的幂等节窗不点任何施事者的名')
Z(u"sum(F['meth_post_sec'][:4])", u'幂等节里点名 POST 的只有 9110')
Z(u"sum(F['ra_abnf_ledger'])", u'Retry-After 规则行的竖线式⇎斜杠式两档相加=规则行数')
Z(u"F['ra_count'][3]", u'8470 全文不提 Retry-After')
Z(u"sum(F['ra_exp_3600']) - 1", u'“Retry-After: 3600”的例子只在 6585')
Z(u"F['ra_exp_120'][2] + F['ra_two_minutes'][2]", u'6585 既无 120 秒例也无 “2 minutes”')
Z(u"F['ra_abnf_slash'][0] + F['ra_abnf_bar'][1] + F['ra_abnf_bar'][4]",
  u'斜杠式与竖线式完全分代: 2616 用竖线, 7231/9110 用斜杠')
Z(u"F['ra_exp_date'][0] + F['ra_exp_date'][1] + F['ra_exp_date'][4] - 3",
  u'HTTP-date 示例三份语义规范各一枚')
Z(u"F['code_defined_n'][3]", u'8470 一枚状态码也不定义')
Z(u"F['code_defined'][0][7] + F['code_defined'][0][8] + F['code_defined'][1][7] "
  u"+ F['code_defined'][1][8]", u'2616 与 7231 都不定义 428/429')
Z(u"F['code_defined'][4][7] + F['code_defined'][4][8]", u'现行 9110 既不定义 428 也不定义 429')
Z(u"F['code_defined'][2][7] - 2", u'6585 把 428 定义了两处(目录 ⇎ 节标题)')
Z(u"sum(F['paren'][0]) + sum(F['paren'][1]) + sum(F['paren'][4])", u'“码+括号名”的印法只有 8470 用')
Z(u"F['paren_straddle'][3] - 4", u'8470 有四枚括号引用被换行切开')
Z(u"F['paren_straddle'][0] + F['paren_straddle'][1] + F['paren_straddle'][2] "
  u"+ F['paren_straddle'][4]", u'其余四份零枚被切')
Z(u"sum(F['neg_false_sub']) - 2", u'子串假阳性恰两枚(2616 的 425 ⇎ 9110 的 428 来自 RFC 4289)')
Z(u"F['neg_bnd'][0][8] - 11", u'2616 面上 idempotent 一词出现 11 次')
Z(u"F['neg_bnd'][3][8] + F['neg_bnd'][3][0]", u'8470 既不说 idempotent 也不提 429')
Z(u"F['neg_bnd'][4][2] + F['neg_bnd'][4][3]", u'9110 不提 Too Early ⇎ 也不提 Early-Data')
Z(u"F['pair_lbl_idx'][0] + F['pair_lbl_idx'][1] - (1 + 4)", u'搬字最大的一对确是 7231 与 9110')
Z(u"F['pair_max'] - F['pair_shared'][F['pair_max_lbl']]", u'列表轨与字典轨给出同一个最大值')
Z(u"F['pair_7231_9110'] - F['pair_max']", u'指名字典轨与序号轨同值')
Z(u"F['axis_close']", u'搬字分家三本账: 池内行数=逐字节同形+只归一同形, 两条独立算法给出同样分档')
Z(u"F['axis_total'] - len(F['axis_rows'])", u'分家四桶之和与逐行清单同枚')
Z(u"F['pair_pool_norm_only'] - F['pair_max_norm_only_keys']", u'两条独立扫法给出同一个“只归一同形”枚数')
Z(u"F['pair_max_byte_keys'] + F['pair_max_norm_only_keys'] - F['pair_max']", u'折叠键档: 逐字节同形+只归一同形=搬字总枚(与行池相交那条路同值)')
Z(u"F['pair_byte_unit_gap'] + F['pair_byte_shell_gap'] - (F['pair_max_byte_lines'] - F['pair_max_byte_keys'])",
  u'原始行枚数到折叠键枚数的两级坍缩: 折平合并 ⇎ 摘壳剔除, 相加=两条路的总差')
Z(u"F['pair_byte_lines_ge_keys'] - 1", u'同一对文档: 按原始行计枚不少于按折叠键计枚')
Z(u"F['s_ruler_gain_7231_9110'] - (F['s_pair_7231_9110'] - F['pair_7231_9110'])",
  u'句尺对 7231·9110 的增益=两尺之差')
Z(u"F['s_pair_max'] - max(F['s_pair_share'])", u'句尺最大值与逐对表同值')
Z(u"F['s_pair_7231_9110'] - F['s_pair_max']", u'句尺最大的也对是 7231·9110')
Z(u"F['pool_tier_close']", u'共用长行按份数分档之和=并集条数')
Z(u"F['union_close']", u'行尺容斥: Σ单份−Σ两两+Σ三三−Σ四四+Σ五五=并集')
Z(u"F['pair_close']", u'两两“归一同形”=“逐字节同形”+“只归一同形”')
Z(u"F['s_pool_tier_close']", u'句尺分档之和=句池条数')
Z(u"F['s_union_close']", u'句尺容斥闭合=零')
Z(u"F['apool_tag_close']", u'锚候选池按标签分布之和=池条目数')
Z(u"F['apool_tier_close']", u'锚候选池按份数加权=按标签相加')
Z(u"F['lines_split_close']", u'splitlines 行数=换行计数+1−末行换行+换页符')
Z(u"sum(F['cr']) + sum(F['nul'])", u'五份面全无 CR 与 NUL')
Z(u"F['shell_ledger_close']", u'两遍壳谓词逐行分账后账平')
Z(u"sum(F['ff_inline']) + sum(F['ff_minus_pg'])", u'换页符全部独占整行 ⇎ 与 [Page] 行一一对应')
Z(u"sum(F['tail_nl']) - NSRC", u'五份都以换行收尾')
Z(u"sum(F['newlines']) + NSRC - sum(F['lines'])", u'换行枚数+1=行数')
Z(u"sum(F['nonblank']) + sum(F['blank']) - sum(F['lines'])", u'非空行+空行=行数')
Z(u"F['txt_n'] + F['html_n'] - NSRC", u'五份全是纯文本, 零份 HTML')
Z(u"sum(F['ent_total']) + sum(F['comment'])",
  u'五份面上零枚 HTML 实体 ⇎ 零枚注释壳(示例页里那截 HTML 不带实体)')
Z(u"F['tag_close'][0] + F['tag_close'][1] + F['tag_close'][3] + F['tag_close'][4]",
  u'闭标签名形只属于 6585 的示例页, 其余四份一枚也没有')
Z(u"F['tag_shape'][2] - F['tag_close'][2] - F['tag_open'][2] - F['tag_url'][2]",
  u'6585 的尖括号形被三把尺(开名 ⇎ 闭名 ⇎ URL 形)分完, 一枚伪法也不剩')
Z(u"F['tag_pseudo'][3]", u'8470 通篇没有尖括号伪法: 它的 <> 全是裸 URL')
Z(u"F['tag_open'][1] + F['tag_open'][3]", u'7231 与 8470 连开标签名形都读不出')
Z(u"sum(F['bom']) - F['bom'][4]", u'BOM 只出现在 9110 一侧')
Z(u"F['sh_char_gap'][4]", u'9110 无分页壳: 摘壳面与折平面等长')
Z(u"F['ff_only'][4] + F['ff'][4]", u'9110 面上零枚换页符')
Z(u"F['year_span'] - (F['years'][4] - F['years'][0])", u'首末年跨=发布序年距之和')
Z(u"F['year_inversions'] - 1", u'按发布顺序排年只有一处倒退(7231 2014 ⇎ 6585 2012)')
Z(u"sum(F['upd_target_obsoleted']) - 1", u'被 Updates 指向的那份恰好也被人 Obsoletes: 恰一处')
Z(u"F['obs_total'] - sum(len(x) for x in F['obs_ids'])", u'Obsoletes 总数=各份段数相加')
Z(u"F['obs_total'] - sum(len(x) for x in F['obs_ids_clean']) - sum(F['obs_blank_segs'])",
  u'冒号后的段数=读出的号数+空段数(9110 尾部空段)')
Z(u"F['lineage_close']", u'谱系账: 空段剔除⇎去重⇎本库内外相加后归零')
Z(u"len(F['lineage_no_edge']) - 1", u'谱系图上恰一份文档没有出边(既不 Obsoletes 也不 Updates)')
Z(u"sum(F['dblspace_in_fold'])", u'折平之后全库零枚双空格(所以节标题形状只能在原行上量)')
Z(u"F['hyphen_break'][2] + F['hyphen_break'][3]", u'6585 与 8470 从不把词切在连字符上')
Z(u"F['hdr_nodot'][3] + F['hdr_nodot'][4]", u'8470 与 9110 的编号标题全带尾点(2616 全不带)')
Z(u"F['ans_words'][4] - 8", u'9110 的答句最短: 八词')
Z(u"sum(F['ans_span']) - 11", u'五份答句各跨的行数相加=11')
Z(u"F['ans_one_line_n'] - 1", u'只有 9110 的答句能在一行内读全')
Z(u"F['ans_lead_words'][2] + F['ans_lead_words'][3]", u'6585 与 8470 的答句以状态码开头')
Z(u"sum(F['ans_lead_words']) - 4", u'全库判词前的引导词只属于 2616')
Z(u"sum(F['ans_page_break'])", u'没有一枚答句被分页壳切开')
Z(u"F['ph_straddle'][2]", u'6585 的判词短语逐行即读全, 谈不上被切')
Z(u"sum(F['ph_line']) - 1", u'五句判词短语里恰一句印在单行内')
Z(u"sum(F['ph_fold']) - NSRC", u'五句在折平档全部读得到')
Z(u"len(F['neg_controls']) - F['neg_n']", u'反向对照清单与计数同枚')
Z(u"sum(F['sn_sec_docs_scope'][i] + 1 for i in (2, 3))", u'无节窗的两份按 -1 登记(口径不存在, 不是零)')


def _ev(e):
    return eval(e.strip())


ZF = [w for e, w in ZID if _ev(e)]
F['zid_fail'] = ZF
for e, w in ZID:
    if _ev(e):
        print(u'  恒等式不为零: %s <= %s' % (w, e.strip()))
F['scalar_clos_n'] = len(ZID)
F['scalar_clos_sum'] = sum(1 for e, w in ZID if not _ev(e))
F['list_clos_n'] = len([k for k in F
                        if (u'_close' in k or u'_ledger' in k) and isinstance(F[k], list)])
F['x_ident_n'] = len(ZID)
F['bool_clos_n'] = len(CLOSE)
F['bool_clos_sum'] = sum(CLOSE.values())
# --- SCAN END ---

# --- PICK BEGIN --- (与采集侧(_b80meas.json)逐键对账; 同一段也由 corpus/_wire80.py 机械切进 audit.py::_b80_scan)
MEA = json.load(io.open(u'corpus/_b80meas.json', encoding='utf-8'))
PK = (u'act act_fam act_sec act_sec_tot act_sg act_sg_plus_pl ans_first_line ans_lead_words '
      u'ans_lines_abs ans_one_line_n ans_page_break ans_para_span ans_para_tail ans_ph '
      u'ans_span ans_words auto_bare auto_bare_line auto_bare_minus_union auto_fam '
      u'auto_fam_overlap auto_fold auto_gain auto_line auto_line_rows auto_sh '
      u'auto_sh_minus_fold auto_tot_fold auto_tot_line auto_union_fold blank bom '
      u'byte_cp_delta bytes chars code_defined code_defined_lbl code_defined_n '
      u'code_defined_raw code_fam code_toc cr ff ff_exact fold_chars hyb_idem hyb_straddle '
      u'idem_hyb_fold idem_hyb_line idem_line_occ idem_line_rows idem_str issn_hdr label '
      u'lineage_no_edge lines maxlen meth_fam meth_post_sec meth_sec meth_sec_n months '
      u'months_txt neg_bnd neg_digit neg_false_sub neg_fam neg_own neg_own_lbl neg_raw '
      u'neg_zero_n newlines nonascii nonblank nul num num_fam num_own num_raw num_rename '
      u'num_sub num_tot obs_ids obs_line obs_target_in_lib obs_total over72 pageless '
      u'pair_lbl_idx pair_max pair_max_lbl pair_shared paren paren_fam paren_line '
      u'paren_straddle pg_lines ph_fold ph_line ph_raw_line ph_straddle pool_n ra_abnf_bar '
      u'ra_abnf_forms ra_abnf_ledger ra_abnf_lines ra_abnf_quoted ra_abnf_slash ra_count '
      u'ra_delta_def ra_exp_120 ra_exp_3600 ra_exp_date ra_two_minutes reword reword_fam '
      u'reword_overlap reword_own reword_tot reword_union reword_zero_n sec_body_line '
      u'sec_chars sec_end_head sec_end_kind sec_found_n sec_head_line sec_hit_n sec_lines '
      u'sec_no sec_sents sec_toc_line sec_words sh_chars shell_lines src std_line subj '
      u'subj_active subj_fam subj_line subj_n subj_passive subj_straddle subj_straddle_k '
      u'subj_straddled tail_nl tone_case tone_case_gap tone_fam tone_must_ledger '
      u'tone_must_pure tone_norm tone_norm_fold tone_sec tone_sec_tot tone_straddle '
      u'tone_straddle_k tone_tot tone_word_lc upd_ids upd_line upd_target_obsoleted '
      u'upd_total year_inversions year_span years').split()
AGREE = []
DIFF = []
for k in PK:
    if k not in F or k not in MEA:
        DIFF.append((k, u'缺键', u'缺键'))
        continue
    (AGREE if F[k] == MEA[k] else DIFF).append((k, F[k], MEA[k]))
# 换名对拍: 同一段量测在两边是不同单位/不同谓词, 各自算各自的, 再把可换的那一层逐枚对上
F['ff_only_vs_pick_lines'] = 1 if F['ff_only'] == MEA[u'ff_only_lines'] else 0
F['sh_gap_vs_pick'] = 1 if F['sh_char_gap'] == MEA[u'sh_minus_fold'] else 0
F['hdr_tight_vs_pick'] = 1 if F['hdr_lines_tight'] == MEA[u'hdr_lines'] else 0
F['hdr_indent_minus_tight'] = [F['hdr_lines_indent'][i] - F['hdr_lines_tight'][i] for i in range(NSRC)]
F['pair_byte_lines_vs_pick'] = 1 if F['pair_max_byte_lines'] == MEA[u'pair_max_byte'] else 0
F['pair_norm_lines_vs_pick'] = 1 if F['pair_max_norm_only_lines'] == MEA[u'pair_max_norm_only'] else 0
F['ans_vs_pick'] = [1 if MEA[u'ans'][i].rstrip() == F[u'ans'][i] else 0 for i in range(NSRC)]
F['ans_tail_ws'] = [len(MEA[u'ans'][i]) - len(F[u'ans'][i]) for i in range(NSRC)]
F['pick_agree'] = len(AGREE)
F['pick_diff'] = len(DIFF)
for k, a, b in DIFF:
    print(u'  采集⇎建条目不符: %s %s vs %s' % (k, a, b))
assert F['pick_diff'] == 0, DIFF[:3]
assert sum(F['ans_vs_pick']) == NSRC, F['ans_vs_pick']
assert F['ff_only_vs_pick_lines'] and F['sh_gap_vs_pick'] and F['hdr_tight_vs_pick'], 1
assert F['pair_byte_lines_vs_pick'] and F['pair_norm_lines_vs_pick'], 1
print(u'  对账: %d 键逐值符 ⇎ 0 键不符; 换名四对(换页档/摘壳差/顶格头/原始行枚)全符; '
      u'答句两轨只差尾随空白 %s 枚' % (F['pick_agree'], F['ans_tail_ws']))
# --- PICK END ---

BB80 = lambda name, i=None: (F[name] if i is None else F[name][i])
FN = u'B80V'
_to_v = re.compile(r"(?:F|CLOSE)\['([a-z0-9_]+)'\](?:\[(\d+)\])?")


def to_v(e):
    s = _to_v.sub(lambda m: u"B80V('%s'%s)" % (m.group(1), u'' if not m.group(2) else u', ' + m.group(2)), e)
    return s.replace(u'range(NSRC)', u'range(5)').replace(u'NSRC', u'5')


K_, ZERO, COLL, SEENX = {}, [], {}, {}


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K_:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K_.setdefault(s, (expr, note))


def V(name, i=None, note=u''):
    if name not in F:
        raise AssertionError(u'无此键 ' + name)
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def J(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LBL[i])) for i in range(NSRC))


def JL(name, note=u''):
    return V(name, None, note) if isinstance(F[name], (list, dict)) else J(name, note)


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


ZV = []
for e, w in ZID:
    v = to_v(e.replace(u'\n', u''))
    if eval(v, {FN: BB80}) != _ev(e):
        print(u'ZID 形不对拍: ' + w + u' |' + v + u'|')
        raise SystemExit(1)
    ZV.append((v, w))
    reg(str(_ev(e)), v, w)


def dump_deriv():
    out = dict((k, v[0]) for k, v in K_.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {FN: BB80}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"(%s if len(set([tuple(y) for y in [%s]]))==1 else -1)" % (exprs[0], u','.join(exprs))
    return out


for k, v in dump_deriv().items():
    DER[k] = v
io.open(u'corpus/_b80flat.json', 'w', encoding='utf-8').write(
    json.dumps(F, ensure_ascii=False, indent=1, sort_keys=True))
io.open(u'corpus/_deriv80.json', 'w', encoding='utf-8').write(
    json.dumps(DER, ensure_ascii=False, indent=1, sort_keys=True))

print(u'第二遍量测完成: 扁平键 %d ｜ 恒等式 %d 全平 ⇎ 布尔门 %d 全绿 ｜ 锚针 %d(反向 %d) ｜ 行池 %d ⇎ 句池 %d'
      % (len(F), len(ZID), F['bool_clos_n'], F['needle_n'], F['neg_n'], F['pool_n'], F['s_pool_n']))
print(u'节窗 %s 行 ⇎ 词 ⇎ 句 ｜ 语气四档 %s ⇎ 节内 %s ｜ 数字族重命名差 %s'
      % (F['sec_lines'], F['tone_tot'], F['tone_sec_tot'], F['num_rename']))
print(u'搬字: 行尺最大 %s(%d 枚=字节 %d+只归一 %d) ⇎ 原始行档 %d ｜ 句尺最大 %d ｜ 分家 %s'
      % (F['pair_max_lbl'], F['pair_max'], F['pair_max_byte_keys'], F['pair_max_norm_only_keys'],
         F['pair_max_byte_lines'], F['s_pair_max'], F['axis_str']))
print(u'2616 判词在节内 %d 枚 ⇎ 摘壳 %d 枚 ⇎ 距节头 %d 行 ｜ 9110 节内 %d/%d 枚'
      % (F['v_in_sec'], F['v_in_sh'], F['verdict_head_gap'], F['k9110_in_sec'], F['k9110_tot']))

exec(io.open(u'corpus/_mk80emit.py', encoding='utf-8').read())
