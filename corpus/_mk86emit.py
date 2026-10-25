# -*- coding: utf-8 -*-
"""B86 第二遍的发射段: 由 _mkB86.py 在顶层 exec 进来(# --- SCAN END --- 之后)。
本段与量测段(_mkB86.py 的 SCAN 段 ⇎ _pick86.py)换机制而不换定义:
①行号尺: 量测段用累积长度表 + bisect ⇎ 本遍给折平面的每一枚字符现挂原行下标, 命中区间取行集合;
②句界: 量测段逐字符扫“句末标点+空格” ⇎ 本遍用 finditer 的正则切点;
③切开针: 量测段只问“这一行含不含针” ⇎ 本遍枚举针在面上的每一次命中并量它跨几行, 命中/跨行/同行重枚三档要自相减等于量测档;
④跨行义务词: 量测段用两档总量之差 ⇎ 本遍逐对相邻非空行现拼短语, 大写档要与那三个差逐份对上, 小写档另数;
⑤去编号: 量测段用两条正则整串替换 ⇎ 本遍按 token 判形状丢弃并现挂行号, 再拿针逐枚数;
⑥段窗: 量测段没有这一档, 本遍由字面针开窗现导(行区间切片 ⇎ 保形折平块 ⇎ 逐 token 拆字母段读语气词);
⑦内核默认值: 量测段按四句式逐字符扫描 ⇎ 本遍按四条正则级联现读, 键块由键行行号下标切片现导;
⑧倍增第三轨: 量测段有逐次倍增值累加 ⇎ 本遍现列 2 的幂清单再求和, 读数由字符扫描器现取而非正则分组;
⑨反向针 ⇎ 模板段: 量测段用整串正则计数 ⇎ 本遍用游标 find 环在本遍自导的摘壳面上逐枚数并现推偏移。
所有正文数字先注册再插值; 锚一律由面上位置现取。
"""
# --- SCAN2 BEGIN ---
PROBE = (u'B86PROBE' in os.environ)
K0 = set(F)
TAGS = LBL
FAN = [pnorm(t) for t in T]
LIMW = 92
ATOMFAIL = []
BLKFAIL = []
BADREAD = []


def rowfold(raw):
    """折平一把尺: 逐词抄写 + 每枚字符挂原行下标(不经整串 split/join 压缩)。"""
    s, idx, k, n = [], [], 0, len(raw)
    while k < n:
        while k < n and raw[k].isspace():
            k += 1
        if k >= n:
            break
        if s:
            s.append(u' ')
            idx.append(k)
        while k < n and not raw[k].isspace():
            s.append(raw[k])
            idx.append(k)
            k += 1
    return u''.join(s), idx


def face_rows(rows):
    """给一批(原行号, 文本)现导折平面 + 逐字符原行表。"""
    parts, rmap = [], []
    for r, x in rows:
        f, _ix = rowfold(x)
        if not f:
            continue
        if parts:
            parts.append(u' ')
            rmap.append(r)
        parts.append(f)
        rmap.extend([r] * len(f))
    return u''.join(parts), rmap


ALLROWS = [[(k, L[i][k]) for k in range(len(L[i]))] for i in range(NSRC)]
NSROWS = [[(k, L[i][k]) for k in range(len(L[i])) if not shell_shape(L[i][k])] for i in range(NSRC)]
EFA, MRA = zip(*[face_rows([(k, x.lower()) for k, x in ALLROWS[i]]) for i in range(NSRC)])
EFB, MRB = zip(*[face_rows([(k, x.lower()) for k, x in NSROWS[i]]) for i in range(NSRC)])
EFC, _MRC = zip(*[face_rows(NSROWS[i]) for i in range(NSRC)])
EFD, _MRD = zip(*[face_rows(ALLROWS[i]) for i in range(NSRC)])
EFA, MRA, EFB, MRB = list(EFA), list(MRA), list(EFB), list(MRB)
EFC, EFD = list(EFC), list(EFD)
F['pp_face_all'] = 1 if EFA == FOL else 0
F['pp_face_shell'] = 1 if EFB == SHP else 0
F['pp_face_shell_case'] = 1 if EFC == SHPX else 0
F['pp_face_all_case'] = 1 if EFD == FOLDX else 0
F['pp_face_len'] = [len(EFB[i]) - len(SHP[i]) for i in range(NSRC)]
F['pp_rows_kept'] = [len(NSROWS[i]) for i in range(NSRC)]
F['pp_rows_all'] = [len(ALLROWS[i]) for i in range(NSRC)]
F['pp_rows_close'] = [F['pp_rows_kept'][i] + F['shell_lines'][i] - F['pp_rows_all'][i] for i in range(NSRC)]
F['pp_chars_shell'] = [len(EFB[i]) for i in range(NSRC)]


def ln_of(i, off, whole=0):
    """原行下标: 由逐字符行表现取(量测段那把是累积长度 + bisect)。"""
    m = MRA[i] if whole else MRB[i]
    return m[off] if 0 <= off < len(m) else -1


def ln_span(i, a, b, whole=0):
    m = MRA[i] if whole else MRB[i]
    return sorted(set(m[a:b]))


def occ_at(face, nd, frm=0):
    out, i = [], face.find(nd, frm)
    while i >= 0:
        out.append(i)
        i = face.find(nd, i + 1)
    return out


SP_P = re.compile(u'[.!?] +')


def sent_spans(face):
    """本遍句界: 正则切点现导句窗(量测段是逐字符扫同一形状)。"""
    out, start = [], 0
    for m in SP_P.finditer(face):
        p = m.start() + 1
        k = p
        while k < len(face) and face[k] == u' ':
            k += 1
        out.append((start, p))
        start = k
    if start < len(face):
        out.append((start, len(face)))
    return [(a, b) for a, b in out if face[a:b].strip() != u'']


F['pp_sent_close'] = len([i for i in range(NSRC)
                          if sent_spans(EFB[i]) != sent_cuts(EFB[i])])
F['pp_sent_n'] = [len(sent_spans(EFB[i])) for i in range(NSRC)]
# ---------- 答句: 由本遍的行号尺 ⇎ 句界尺现导 ----------
A2, ASP = [], []
for i in range(NSRC):
    q = pnorm(ANSK[i])
    hs = occ_at(EFB[i], q)
    assert len(hs) == 1, (LBL[i], len(hs))
    s0 = hs[0]
    sp = sent_spans(EFB[i])
    a, b = sent_at(sp, s0)
    A2.append([s0, a, b, ln_of(i, s0), ln_of(i, a), ln_of(i, b - 1), EFC[i][a:b]])
    ASP.append(sp)
F['ans2_off'] = [z[0] for z in A2]
F['ans2_sent_line'] = [z[4] for z in A2]
F['ans2_sent_end'] = [z[5] for z in A2]
F['ans2_span'] = [z[5] - z[4] + 1 for z in A2]
F['ans2_needle_line'] = [z[3] for z in A2]
F['ans2_chars'] = [len(z[6]) for z in A2]
F['ans2_words'] = [len(z[6].split()) for z in A2]
F['ans_line_close'] = [F['ans2_sent_line'][i] - F['ans_sent_line'][i] for i in range(NSRC)]
F['ans_end_close'] = [F['ans2_sent_end'][i] - F['ans_sent_end'][i] for i in range(NSRC)]
F['ans_span_close'] = [F['ans2_span'][i] - F['ans_sent_span'][i] for i in range(NSRC)]
F['ans_words_close'] = [F['ans2_words'][i] - F['ans_words'][i] for i in range(NSRC)]
F['ans_sent_same'] = [1 if A2[i][6] == F['ans_sent'][i] else 0 for i in range(NSRC)]
for i in range(NSRC):
    rk = ln_span(i, A2[i][1], A2[i][2], 0)
    rw = list(range(rk[0], rk[-1] + 1))
    F.setdefault(u'ans2_rows_whole', []).append(len(rw))
    F.setdefault(u'ans2_rows_kept', []).append(len(rk))
    F.setdefault(u'ans2_shell_rows', []).append(len(rw) - len(rk))
    F.setdefault(u'ans2_blank_span', []).append(
        len([x for x in rw if L[i][x].strip() == u'' and shell_shape(L[i][x])]))
    F.setdefault(u'ans2_page_span', []).append(
        len([x for x in rw if any(g(L[i][x]) for g in PAGESH)]))
F['ans_shell_close'] = [F['ans_shell_rows'][i] - F['ans2_shell_rows'][i] for i in range(NSRC)]
F['ans_page_close'] = [F['ans_page_rows'][i] - F['ans2_page_span'][i] for i in range(NSRC)]
# ---------- 切开针: 逐枚命中量它跨几行 ----------
SC = []
for k in range(len(NK)):
    for i in range(NSRC):
        hs = occ_at(EFB[i], NK[k])
        sp = [h for h in hs if len(ln_span(i, h, h + len(NK[k]))) > 1]
        ins = [h for h in hs if h not in sp]
        dup = len(ins) - len(set([ln_of(i, h) for h in ins]))
        mx = max([len(ln_span(i, h, h + len(NK[k]))) for h in sp] or [0])
        SC.append([k, i, len(hs), len(sp), dup, mx])
F['sc_occ'] = [[z[2] for z in SC if z[1] == i] for i in range(NSRC)]
F['sc_span'] = [[z[3] for z in SC if z[1] == i] for i in range(NSRC)]
F['sc_dup'] = [[z[4] for z in SC if z[1] == i] for i in range(NSRC)]
F['sc_max_span'] = max([z[5] for z in SC])
F['sc_occ_close'] = sum([abs(SC[t][2] - F['role_sh'][SC[t][0]][SC[t][1]]) for t in range(len(SC))])
F['sc_line_close'] = sum([abs(SC[t][2] - SC[t][3] - SC[t][4] - F['role_line'][SC[t][0]][SC[t][1]])
                          for t in range(len(SC))])
F['sc_span_tot'] = sum([z[3] for z in SC])
F['sc_needle_n'] = len(set([z[0] for z in SC if z[3] > 0]))
F['sc_doc_span'] = [sum([z[3] for z in SC if z[1] == i]) for i in range(NSRC)]
F['sc_cut_close'] = 1 if sorted(set([z[0] for z in SC if z[3] > 0])) == sorted(F['wrap_cut']) else 0
F['sc_gain_close'] = F['sc_span_tot'] - F['wrap_gain_tot']
F['sc_doc_gain_close'] = [F['sc_doc_span'][i] - F['wrap_gain'][i] for i in range(NSRC)]
SCROWS = dict(((z[0], z[1]), [h for h in occ_at(EFB[z[1]], NK[z[0]])
                              if len(ln_span(z[1], h, h + len(NK[z[0]]))) > 1])
              for z in SC if z[3])
# ---------- 去编号: 按 token 判形丢弃, 现挂行号再逐枚数针 ----------
TAGSHAPE2 = re.compile(u'^(must|should|may|shld|ed)-[0-9]+$', re.I)


def tag_shape(tok):
    return TAGSHAPE2.match(tok.strip(u'().,;:')) is not None


TWO_TAG = re.compile(u'^(must not|should not)-[0-9]+$')


def _res(tok, inner):
    """整枚被括号合住的编号连括号一起删(那把正则吃的是 “ (x-n)” 整串); 半开的只删编号串留下圈点。"""
    if tok.startswith(u'(') and tok.endswith(u')') and tok[1:-1] == inner:
        return u''
    return tok.replace(inner, u'')


def tag_eat(toks):
    """逐 token 吃编号: 先试两词式(must not-4), 再试单词式, 都不像就原样抄下。"""
    out, k = [], 0
    while k < len(toks):
        cur = toks[k].strip(u'().,;:')
        nxt = toks[k + 1].strip(u'().,;:') if k + 1 < len(toks) else u''
        if nxt and TWO_TAG.match((cur + u' ' + nxt).lower()):
            if toks[k].startswith(u'(') and toks[k + 1].endswith(u')'):
                k += 2
                continue
            out.append(_res(toks[k], cur))
            out.append(_res(toks[k + 1], nxt))
            k += 2
            continue
        if TAGSHAPE2.match(cur):
            out.append(_res(toks[k], cur))
            k += 1
            continue
        out.append(toks[k])
        k += 1
    return [t for t in out if t != u'']


TDF, TDM = [], []
for i in range(NSRC):
    parts, rmap = [], []
    for r, x in NSROWS[i]:
        f, _ix = rowfold(x.lower())
        keep = tag_eat(f.split(u' '))
        g = u' '.join(keep)
        if not g:
            continue
        if parts:
            parts.append(u' ')
            rmap.append(r)
        parts.append(g)
        rmap.extend([r] * len(g))
    TDF.append(u''.join(parts))
    TDM.append(rmap)
F['td_face_same'] = [1 if TDF[i] == SHTAG[i] else 0 for i in range(NSRC)]
F['td_face_gap'] = [len(TDF[i]) - len(SHTAG[i]) for i in range(NSRC)]
F['td_chars'] = [len(EFB[i]) - len(TDF[i]) for i in range(NSRC)]
TC = []
for k in range(len(NK)):
    for i in range(NSRC):
        hs = occ_at(TDF[i], NK[k])
        sp = [h for h in hs if len(set(TDM[i][h:h + len(NK[k])])) > 1]
        TC.append([k, i, len(hs), len(sp), F['role_tag'][k][i], F['role_sh'][k][i]])
F['tc_occ'] = [[z[2] for z in TC if z[1] == i] for i in range(NSRC)]
F['tc_occ_close'] = sum([abs(TC[t][2] - TC[t][4]) for t in range(len(TC))])
F['tc_gain_needles'] = sorted(set([TC[t][0] for t in range(len(TC)) if TC[t][2] > TC[t][5]]))
F['tc_gain_close'] = len(F['tc_gain_needles']) - len(F['tag_gain_needles'])
F['tc_span_after'] = sum([z[3] for z in TC])
F['tc_span_before'] = F['sc_span_tot']
F['dur_by_form'] = [sum([F['dur'][i][k] for i in range(NSRC)]) for k in range(len(F['dur'][0]))]
F['dur_by_doc'] = [sum(F['dur'][i]) for i in range(NSRC)]
# ---------- 跨行义务词: 逐对相邻非空行现拼短语 ----------
def straddle(rows, words, low=0):
    """相邻两行首尾拼出一个义务词短语: 大写档照字面比 ⇎ 小写档先折小写。"""
    out = []
    nz = [(r, x) for r, x in rows if x.strip() != u'']
    for t in range(len(nz) - 1):
        r1, x = nz[t]
        r2, y = nz[t + 1]
        tail = x.split()[-1].strip(u'().,;:')
        head = y.split()[0].strip(u'().,;:')
        cand = (tail + u' ' + head).lower() if low else tail + u' ' + head
        for w in words:
            if cand == w:
                out.append([r1, r2, w, x[-40:], y[:40]])
    return out


ST_UP = [straddle(ALLROWS[i], OB) for i in range(NSRC)]
ST_LO = [straddle(ALLROWS[i], OBL, 1) for i in range(NSRC)]
F['st_up'] = [len(x) for x in ST_UP]
F['st_low'] = [len(x) for x in ST_LO]
F['st_up_close'] = sum(F['st_up']) - sum(F['ob_wrap'])
F['st_by_doc'] = [sum([F['ob_wrap'][i * 5 + k] for k in range(5)]) - F['st_up'][i]
                  for i in range(NSRC)]
F['st_tot'] = sum(F['st_up']) + sum(F['st_low'])
F['st_words'] = sorted(set([z[2].lower() for x in ST_UP + ST_LO for z in x]))
F['st_docs'] = len([i for i in range(NSRC) if ST_UP[i] or ST_LO[i]])
STSH = [len([z for z in ST_UP[i] + ST_LO[i]
            if shell_shape(L[i][z[0]]) or shell_shape(L[i][z[1]])]) for i in range(NSRC)]
F['st_in_shell'] = sum(STSH)
# --- SCAN2 CONT ---
ROWSRAW = [u'\x01'.join(pnorm(x) for x in L[i]) for i in range(NSRC)]
ANSET = [set() for _ in range(NSRC)]
ALOG = []


def word_edge(fc, idxs, a, b):
    """把命中区间扩到整词: 左右各自走到字母数字边界为止。"""
    n = len(fc)
    while a > 0 and (fc[a - 1].isalnum() or fc[a - 1] in u'-_'):
        a -= 1
    while b < n and (fc[b].isalnum() or fc[b] in u'-_'):
        b += 1
    return a, b


def row_anchor(i, phrase, whole=0):
    """在原文件的某一行里找这一串: 命中→扩到整词→映回该行的字面切片。"""
    q = pnorm(phrase)
    rows = ALLROWS[i] if whole else NSROWS[i]
    for r, x in rows:
        f, ix = rowfold(x.lower())
        p = f.find(q)
        if p < 0:
            continue
        a, b = word_edge(f, ix, p, p + len(q))
        left = f[a - 1] if a > 0 else u' '
        right = f[b] if b < len(f) else u' '
        if (left.isalnum() or right.isalnum()):
            continue
        an = x[ix[a]:ix[b - 1] + 1]
        if pnorm(an) != q and q not in pnorm(an):
            continue
        return an, r
    return None, -1


def shrink_anchor(i, phrase):
    """整串落不进一行时退让: 先挑最长的词前缀, 再挑最长的词后缀, 各自回自己那一行。"""
    ws = pnorm(phrase).split()
    for t in range(len(ws), 0, -1):
        an, r = row_anchor(i, u' '.join(ws[:t]))
        if an:
            return an, r, u'头'
        an, r = row_anchor(i, u' '.join(ws[-t:]))
        if an:
            return an, r, u'尾'
    return None, -1, u''


def AN(i, phrase, tag=u''):
    an, r = row_anchor(i, phrase)
    if an is None:
        an, r, w = shrink_anchor(i, phrase)
        assert an, (LBL[i], phrase[:40])
        ALOG.append([LBL[i], phrase[:40], r, 1, w])
    else:
        ALOG.append([LBL[i], phrase[:40], r, 1, u'全'])
    ANSET[i].add(an)
    return an


def AO(phrase):
    """归属锚: 由“哪几份的摘壳面读得到”现推, 不读旁注。"""
    q = pnorm(phrase)
    hit = [i for i in range(NSRC) if q in EFB[i]]
    assert hit, phrase[:40]
    an = AN(hit[0], phrase)
    return an


def AF(i, phrase, off):
    """带偏移的读数锚: 锚由该份面内现取, 偏移只用于定位那一行。"""
    return AN(i, phrase)


def blk(i, a, b):
    """行区间 → 保形折平的窗文本(本遍的行号尺)。"""
    rows = [(r, x) for r, x in NSROWS[i] if a <= r <= b]
    return face_rows(rows)[0]


PINS = [
    (0, u'send the segment at the front of the retransmission queue again',
     u'reinitialize the retransmission timer, and return'),
    (0, u'The present global default is five minutes', u'The present global default is five minutes'),
    (1, u'The following procedure MUST be used to handle excessive', u'sooner, of course'),
    (2, u'The following procedure MUST be used to handle excessive', u'sooner, of course'),
    (2, u'For example, an interactive application might set R2', u'when to disconnect'),
    (3, u'A maximum value MAY be placed on RTO', u'at least 60 seconds'),
    (4, u'tcp_retries1 - integer', u'which is the default'),
    (4, u'tcp_retries2 - integer', u'a value of at least 8'),
    (4, u'tcp_syn_retries - integer', u'happen after 127seconds'),
    (4, u'tcp_synack_retries - integer', u'happen after 63seconds'),
    (4, u'association_max_retrans - integer', u'the association is terminated'),
    (4, u'RFC 1122 recommends at least 100 seconds', u'RFC 1122 recommends at least 100 seconds'),
    (4, u'path_max_retrans - integer', u'The maximum number of retransmissions that will be attempted on a given path'),
]
PB = []
for t, (i, s, e) in enumerate(PINS):
    ps = EFB[i].find(pnorm(s))
    pe = EFB[i].find(pnorm(e))
    assert ps >= 0 and pe >= 0 and pe >= ps, (LBL[i], s[:32], e[:32], ps, pe)
    ra, rb = ln_of(i, ps), ln_of(i, pe + len(pnorm(e)) - 1)
    txt = blk(i, ra, rb)
    ws = txt.split()
    PB.append([i, ps, pe, ra, rb, txt, len(ws), len(txt)])
F['pb_doc'] = [z[0] for z in PB]
F['pb_rows'] = [z[4] - z[3] + 1 for z in PB]
F['pb_words'] = [z[6] for z in PB]
F['pb_chars'] = [z[7] for z in PB]
F['pb_vocab'] = [len(set([pnorm(w) for w in z[5].split()])) for z in PB]
F['pb_rows_tot'] = sum(F['pb_rows'])
F['pb_words_tot'] = sum(F['pb_words'])
F['pb_chars_tot'] = sum(F['pb_chars'])
F['pb_five_rows'] = sum([F['pb_rows'][t] for t in range(5)])
F['pb_one_line'] = len([z for z in PB if z[4] == z[3]])


def letter_runs(tok):
    return [m.group(0) for m in re.finditer(u'[A-Za-z]+', tok)]


def tone_count(txt, w):
    """窗内义务词一把尺: 逐 token 拆字母段(量测段那把是查布尔表读左右邻)。
       单词档 = 某一枚字母段恰等于该词(两侧邻字符不是字母 ⇔ 拆出来的字母段完整等于它);
       短语档 = 前一 token 的末段 ⇎ 后一 token 的首段拼成该短语(折平面词间只一枚空格)。"""
    runs = [letter_runs(t) for t in txt.split(u' ')]
    if u' ' in w:
        a, b = w.split(u' ')
        return len([k for k in range(len(runs) - 1)
                    if runs[k] and runs[k + 1] and runs[k][-1] == a and runs[k + 1][0] == b])
    return sum(len([r for r in rr if r == w]) for rr in runs)


def tag_count(txt):
    """窗内编号一把尺: 逐 token 剥圈点后判形状(量测段是一条整串正则)。"""
    return len([t for t in txt.split(u' ') if tag_shape(t)])


F['pb_tone_must'] = [tone_count(z[5], u'MUST') for z in PB]
F['pb_tone_mustnot'] = [tone_count(z[5], u'MUST NOT') for z in PB]
F['pb_tone_should'] = [tone_count(z[5], u'SHOULD') for z in PB]
F['pb_tone_may'] = [tone_count(z[5], u'MAY') for z in PB]
F['pb_tone_tag'] = [tag_count(z[5]) for z in PB]
F['pb_tone_close'] = sum([abs(F[k][t] - ub_tab(PB[t][5], OB[j], _tabs(PB[t][5]), u'alpha'))
                          for k, j, t in [(u'pb_tone_must', 0, tt) for tt in range(len(PB))]
                          + [(u'pb_tone_should', 2, tt) for tt in range(len(PB))]
                          + [(u'pb_tone_may', 4, tt) for tt in range(len(PB))]])
F['pb_phrase_close'] = sum([abs(F[u'pb_tone_mustnot'][t]
                                - ub_tab(PB[t][5], u'MUST NOT', _tabs(PB[t][5]), u'alpha'))
                            for t in range(len(PB))])
F['pb_tag_block_close'] = [F['pb_tone_tag'][2] - F['tag_dash'][1],
                           F['pb_tone_tag'][3] - F['blk_tag_n']]
ANSW = [[t for t in range(len(PB)) if PB[t][0] == i and PB[t][3] <= A2[i][3] <= PB[t][4]]
        for i in range(NSRC)]
F['pb_ans_win'] = [z[0] if z else -1 for z in ANSW]
F['pb_ans_n'] = [len(z) for z in ANSW]
F['pb_ans_close'] = len([z for z in F['pb_ans_win'] if z < 0])
# 段窗首末行回原文件自验: 整串能在这一行读通 ⇎ 只能靠两半读通
SEGRT = []
for t, (i, s, e) in enumerate(PINS):
    an1, r1 = row_anchor(i, s)
    an2, r2 = row_anchor(i, e)
    head = (an1 is not None, s, r1, 0)
    tail = (an2 is not None, e, r2, 1)
    for iswhole, ph, rr, side in (head, tail):
        SEGRT.append([i, ph[:30], rr, 1 if iswhole else 0])
F['sr_n'] = len(SEGRT)
F['sr_whole'] = sum([z[3] for z in SEGRT])
F['sr_cut'] = F['sr_n'] - F['sr_whole']
F['sr_rows_close'] = sum([abs(SEGRT[t][2] - (PB[t // 2][3] if t % 2 == 0 else PB[t // 2][4]))
                          for t in range(len(SEGRT)) if SEGRT[t][3] == 1])
F['sr_cut_rows'] = len([z for z in SEGRT if z[3] == 0])
# ---------- 1122 ⇎ 9293 段落对照: 由本遍的窗与句界现导 ----------
OVW = [(1, PINS[2], u'4.2.3.6'), (2, PINS[3], u'3.8.4.')]
OVBLK, OVSENT = [], []
for i, pin, stopstr in OVW:
    ps = EFB[i].find(pnorm(pin[1]))
    pe = EFB[i].find(pnorm(pin[2]))
    ra, rb = ln_of(i, ps), ln_of(i, pe)
    stop = pnorm(stopstr)
    rows = [(r, x) for r, x in ALLROWS[i] if ra <= r <= rb]
    cutr = -1
    for q in range(len(rows)):
        if stop in pnorm(rows[q][1]):
            cutr = rows[q][0]
            rows = rows[:q]
            break
    face = face_rows([(r, x.lower()) for r, x in rows])[0]
    facec = face_rows(rows)[0]
    OVBLK.append([face, len(rows), rows[0][0], rows[-1][0], facec,
                  len([1 for r, x in rows if shell_shape(x)]), cutr])
    OVSENT.append([face[a:b].strip() for a, b in sent_spans(face)])
S1E, S2E = OVSENT[0], OVSENT[1]
S2T = [TAGRE.sub(u'', z).strip() for z in S2E]
F['ov2_rows'] = [z[1] for z in OVBLK]
F['ov2_sents'] = [len(S1E), len(S2E)]
F['ov2_same_raw'] = len([z for z in S2E if z in set(S1E)])
F['ov2_same_tag'] = len([z for z in S2T if z in set(S1E)])
F['ov2_same_canon'] = len([z for z in S2T if canon(z) in set([canon(y) for y in S1E])])
F['ov2_new'] = len(S2E) - F['ov2_same_tag']
F['ov2_rows_close'] = [F['ov2_rows'][t] - F['ovl_rows'][t] for t in range(2)]
F['ov2_shell'] = [z[5] for z in OVBLK]
F['ov2_shell_close'] = [F['ov2_shell'][t] - F['ovl_shell'][t] for t in range(2)]
F['ov2_sents_close'] = [F['ov2_sents'][t] - (F['ovl_s1'] if t == 0 else F['ovl_s2']) for t in range(2)]
F['ov2_same_close'] = [F['ov2_same_raw'] - F['ovl_same_raw'], F['ov2_same_tag'] - F['ovl_same_tag'],
                       F['ov2_same_canon'] - F['ovl_same_canon']]
F['ov2_new_close'] = F['ov2_new'] - F['ovl_new']
F['ov2_chars'] = [len(z[0]) for z in OVBLK]
F['ov2_sub'] = 1 if S2E and all([z in OVBLK[0][0] for z in S2E]) else 0
# ---------- 节题现导: 块首行上方最近的编号标题 = 这块所属的节 ----------
SECHDR = re.compile(u'^ *(?P<no>[0-9]+(?:\\.[0-9]+)+)\\.? {2,}(?P<ti>[A-Z].*)$')
OVHDR = [[(r, m.group(u'no'), re.sub(u' +', u' ', m.group(u'ti')).strip())
          for r, x in ALLROWS[i] for m in [SECHDR.match(x)] if m] for i, _, _ in OVW]
OVOVN = [([h for h in OVHDR[t] if h[0] < OVBLK[t][2]] or [(0, u'', u'')])[-1] for t in range(2)]
OVNEXT2 = [[h for h in OVHDR[t] if h[0] > OVBLK[t][2]] for t in range(2)]
F['ov_sec'] = [h[1] for h in OVOVN]
F['ov_sec_title'] = [h[2] for h in OVOVN]
F['ov_next_sec'] = [OVNEXT2[t][0][1] if OVNEXT2[t] else u'' for t in range(2)]
F['ov_next_row'] = [OVNEXT2[t][0][0] if OVNEXT2[t] else -1 for t in range(2)]
F['ov_title_same'] = 1 if F['ov_sec_title'][0] == F['ov_sec_title'][1] else 0
F['ov_sec_shift'] = 1 if F['ov_sec'][0] != F['ov_sec'][1] else 0
F['ov_hdr_rows'] = [len(h) for h in OVHDR]
F['ov_stop_str'] = [w[2] for w in OVW]
F['ov_cut_n'] = len([z for z in OVBLK if z[6] >= 0])
NEWIDX = [k for k in range(len(S2E)) if S2T[k] not in set(S1E)]
OVLNEW = [S2E[k] for k in NEWIDX]
OSROW = []
for z in OVLNEW:
    q = EFB[2].find(z[:44])
    hs = occ_at(EFB[2], z[:44])
    OSROW.append([ln_of(2, q) if q >= 0 else -1,
                  len(ln_span(2, q, q + len(z))) if q >= 0 else 0,
                  len(hs), tag_count(EFC[2][q:q + len(z)]) if q >= 0 else 0])
F['os_n'] = len(OVLNEW)
F['os_first_row'] = [z[0] for z in OSROW]
F['os_rows'] = [z[1] for z in OSROW]
F['os_located'] = len([z for z in OSROW if z[0] >= 0])
F['os_ambig'] = len([z for z in OSROW if z[2] > 1])
F['os_tag_in_window'] = sum([z[3] for z in OSROW])
F['os_len'] = [len(z) for z in OVLNEW]
# --- SCAN2 CONT2 ---
# ---------- 内核键值表: 键行行号切片 + 四式正则级联 ----------
KEY2 = re.compile(u'^([a-z_][a-z_0-9]*) - (integer|boolean|string|dword)$')
HD2 = []
for _r in range(len(L[4])):
    _m = KEY2.match(pnorm(L[4][_r]))
    if _m:
        HD2.append([_r, _m.group(1)])
KN2 = {}
for _t in range(len(HD2)):
    _lo = HD2[_t][0] + 1
    _hi = HD2[_t + 1][0] if _t + 1 < len(HD2) else len(L[4])
    KN2.setdefault(HD2[_t][1], []).append((_lo, _hi))
BLK2 = dict((k, pnorm(u' '.join([L[4][x] for x in range(v[-1][0], v[-1][1])]))) for k, v in KN2.items())
HIST2 = {}
for _t in range(len(HD2)):
    HIST2[HD2[_t][1]] = HIST2.get(HD2[_t][1], 0) + 1
DUP2 = sorted([k for k in HIST2 if HIST2[k] > 1])
NB2 = dict((k, v[-1][1] - v[-1][0]) for k, v in KN2.items())
RL2N = sorted([k for k in HIST2
               if re.search(u'retrans|retries|retry|rto|timeout', k) is not None
               and any([w in BLK2[k] for w in [u'retransmission', u'retransmit', u'timeout', u'attempts']])])
SUB2 = [u'retr', u'retry', u'timeout', u'_rto', u'rto_']
RL2P = sorted([k for k in HIST2 if any([s in k for s in SUB2])])
UN2 = sorted(set(RL2P) | set(RL2N))
BOTH2 = len(set(RL2P) & set(RL2N))
F['kn2_keys'] = len(HD2)
F['kn2_uniq'] = len(HIST2)
F['kn2_dups'] = DUP2
F['kn2_rel'] = RL2N
F['kn2_pick'] = RL2P
F['kn2_keys_close'] = F['kn2_keys'] - F['lin_keys_total']
F['kn2_dup_close'] = len(set(DUP2) ^ set(F['lin_key_dup_names']))
F['kn2_rel_close'] = len(set(RL2N) ^ set(F['lin_rel_names']))
F['kn2_pick_close'] = len(set(RL2P) ^ set(F['lin_rel_pick_names']))
F['kn2_body_close'] = sum([NB2[k] for k in RL2N]) - F['lin_body_lines']
F['kn2_union'] = len(UN2)
F['kn2_union_close'] = len(UN2) - F['lin_rel_union']
F['kn2_ie_close'] = len(UN2) - (len(RL2P) + len(RL2N) - BOTH2)
F['kn2_body_rows'] = sum([NB2[k] for k in RL2N])
F['kn2_hdr_rows'] = len(HD2)
F['kn2_last_hdr'] = HD2[-1][0]


DVR2 = [(re.compile(u'default: ?([^ .,;)]+)'), u'Default:'),
        (re.compile(u'default value is ?(\\S+)'), u'default value is'),
        (re.compile(u'default value of ?(\\S+)'), u'default value of'),
        (re.compile(u'at least ([0-9]+)[a-z ]*retransmissions, which is the default'), u'借参考句')]


def dv2(s):
    """同一四式级联, 但每式一条正则(量测段那把是游标 find + 就地扫字符)。"""
    sl = pnorm(s)
    for rx, sh in DVR2:
        m = rx.search(sl)
        if m:
            return (m.group(1), sh)
    return (None, u'无')


def dv2_rows(k):
    for x in L[4][KN2[k][-1][0]:KN2[k][-1][1]]:
        v, sh = dv2(x)
        if v:
            return (v, sh)
    return (None, u'无')


DV2 = dict((k, dv2(BLK2[k])) for k in UN2)
DVL2 = dict((k, dv2_rows(k)) for k in UN2)
F['kn2_dv'] = dict((k, (DV2[k][0] or u'').rstrip(u'.,;')) for k in RL2N)
F['kn2_shape'] = dict((k, DV2[k][1]) for k in RL2N)
F['kn2_shape_n'] = [len([k for k in RL2N if DV2[k][1] == s])
                    for s in [u'Default:', u'default value is', u'default value of', u'借参考句', u'无']]
F['kn2_dv_diff'] = sorted([k for k in RL2N if F['kn2_dv'][k] != F['lin_defaults'][k]
                           or F['kn2_shape'][k] != F['lin_shape'][k]])
F['kn2_shape_close'] = [a - b for a, b in zip(F['kn2_shape_n'], F['lin_shape_n'])]
F['kn2_default_str'] = tuple([F['kn2_dv'].get(u'tcp_retries1'), F['kn2_dv'].get(u'tcp_retries2'),
                              F['kn2_dv'].get(u'tcp_syn_retries'), F['kn2_dv'].get(u'tcp_synack_retries')])
F['kn2_wrap_gain'] = sorted([k for k in UN2 if DV2[k][0] and not DVL2[k][0]])
F['kn2_wrap_close'] = len(set(F['kn2_wrap_gain']) ^ set(F['lin_wrap_gain']))
F['kn2_none'] = len([k for k in RL2N if F['kn2_dv'][k] == u''])
F['kn2_numvals'] = sorted(set([v for v in F['kn2_dv'].values() if re.match(u'^[0-9]+$', v)]))
F['kn2_hex'] = sorted(set([v for v in [(DV2[k][0] or u'') for k in RL2P] if u'x' in v]))
# ---------- 倍增等式第三轨: 幂清单求和 ⇎ 字符扫描读数 ----------


def num_run(s, kw):
    """读数器: 定位短语后向后扫到第一枚数字, 吃掉整串数字(可含小数点), 回(字串, 结束偏移)。"""
    p = s.find(kw)
    assert p >= 0, kw
    k = p
    while k < len(s) and not s[k].isdigit():
        k += 1
    m = k
    while m < len(s) and (s[m].isdigit() or (s[m] == u'.' and m + 1 < len(s) and s[m + 1].isdigit())):
        m += 1
    return (s[k:m] if m > k else None), m


def num_after(s, kw):
    return num_run(s, kw)[0]


def dbl(N, rto=1):
    return sum([rto * 2 ** k for k in range(N)])


def dbl_kill(N, rto=1):
    return dbl(N + 1, rto)


EQ2 = []
for _nm, _k in [(u'syn', u'tcp_syn_retries'), (u'synack', u'tcp_synack_retries')]:
    _b = BLK2[_k]
    _N = int(num_after(_b, u'default value is'))
    _pa = int(num_after(_b, u'corresponds to'))
    _pb = int(num_after(_b, u'happen after'))
    _rto = int(num_after(_b, u'initial rto of'))
    EQ2.append([_nm, _N, dbl(_N, _rto), dbl_kill(_N, _rto), _pa, _pb, _rto])
F['eq2_rows'] = EQ2
F['eq2_close'] = [[EQ2[t][1] - F['eq_rows'][t][1], EQ2[t][2] - F['eq_rows'][t][2],
                   EQ2[t][3] - F['eq_rows'][t][3], EQ2[t][4] - F['eq_rows'][t][5],
                   EQ2[t][5] - F['eq_rows'][t][6], EQ2[t][6] - F['eq_rows'][t][7]] for t in range(2)]
F['eq2_ruler_gap'] = [[EQ2[t][2] - F['eq_rows'][t][2], EQ2[t][2] - F['eq_rows'][t][4],
                       EQ2[t][3] - F['eq_rows'][t][3]] for t in range(2)]
F['eq2_printed'] = [len(occ_at(EFA[4], u'%dseconds' % x)) for x in [31, 63, 127]]
F['eq2_printed_close'] = [F['eq2_printed'][t] - F['eq_printed'][t] for t in range(3)]
F['eq2_min_last'] = min([n for n in range(1, 20) if dbl(n) >= 100])
F['eq2_min_kill'] = min([n for n in range(1, 20) if dbl_kill(n) >= 100])
F['eq2_doc_says'] = int(num_after(EFA[4], u'a value of at least'))
F['eq2_off_by'] = [F['eq2_doc_says'] - F['eq2_min_last'], F['eq2_doc_says'] - F['eq2_min_kill']]
F['eq2_n15_last'] = dbl(15)
F['eq2_n15_kill'] = dbl_kill(15)
HYP = u'hypothetical timeout'
_V9246, _E9246 = num_run(EFA[4], HYP)
F['eq2_9246_face'] = float(_V9246)
F['eq2_9246_unit'] = 1 if EFA[4][_E9246:_E9246 + 8].lstrip().startswith(u'seconds') else 0
F['eq2_face_close'] = abs(F['eq2_9246_face'] - F['eq_9246_face'])
F['eq2_rto_face'] = [int(F['kn2_dv'][u'rto_min']) / 1000.0, int(F['kn2_dv'][u'rto_max']) / 1000.0,
                     int(F['kn2_dv'][u'rto_initial']) / 1000.0]
F['eq2_rto_close'] = [abs(F['eq2_rto_face'][t] - F['eq_rto_face'][t]) for t in range(3)]
F['eq2_cand'] = [dbl(15, F['eq2_rto_face'][0]), dbl_kill(15, F['eq2_rto_face'][0]),
                 dbl(15, F['eq2_rto_face'][2]), dbl(15, F['eq2_rto_face'][1]),
                 F['eq2_rto_face'][0] * ((1 << 15) - 1)]
F['eq2_cand_close'] = [abs(x - y) for x, y in zip(F['eq2_cand'], F['eq_9246_cand'])]
F['eq2_hit'] = len([x for x in F['eq2_cand'] if abs(x - F['eq2_9246_face']) < 0.05])
F['eq2_hit_close'] = F['eq2_hit'] - F['eq_9246_hit']
F['eq2_dev'] = [round(abs(x - F['eq2_9246_face']), 1) for x in F['eq2_cand']]
F['eq2_dev_close'] = sum([abs(x - y) for x, y in zip(F['eq2_dev'], F['eq_9246_gap'])])
F['eq2_9246_n'] = len(occ_at(EFA[4], u'924.6'))
# ---------- 反向针 ⇎ 共现针 ⇎ 模板段: 在本遍自导的摘壳面上用游标重数 ----------
IDX2 = dict((t, n) for n, t in enumerate(LBL))


def mat2(pool):
    out = []
    for own, p in pool:
        q = pnorm(p)
        row = [len(occ_at(EFB[j], q)) for j in range(NSRC)]
        me = IDX2[own]
        out.append((own, p, row, sum(row[j] for j in range(NSRC) if j != me), row[me],
                    sorted([LBL[j] for j in range(NSRC) if j != me and row[j] > 0])))
    return out


NG2 = mat2(NEG)
RP2 = mat2(RP)
F['ng2_mat'] = [z[2] for z in NG2]
F['ng2_close'] = sum([abs(F['ng2_mat'][t][j] - F['neg_mat'][t][j])
                      for t in range(len(NG2)) for j in range(NSRC)])
F['ng2_others'] = sum([z[3] for z in NG2])
F['ng2_self'] = sum([z[4] for z in NG2])
F['ng2_multi'] = [z[1] for z in NG2 if z[4] > 1]
F['ng2_multi_cnt'] = [z[4] for z in NG2 if z[4] > 1]
F['ng2_multi_close'] = len(F['ng2_multi']) - len(F['neg_multi'])
F['rp2_mat'] = [z[2] for z in RP2]
F['rp2_close'] = sum([abs(F['rp2_mat'][t][j] - F['rp_mat'][t][j])
                      for t in range(len(RP2)) for j in range(NSRC)])
F['rp2_others'] = sum([z[3] for z in RP2])
F['rp2_other_src'] = sorted(set([d for z in RP2 for d in z[5]]))
F['rp2_reprint'] = F['rp2_mat'][0][IDX2[u'9293']]
KWS2 = [EFB[i].find(pnorm(KW)) for i in range(NSRC)]
F['kw2_head'] = [EFA[i].find(pnorm(KW)) for i in range(NSRC)]
F['kw2_head_sh'] = KWS2
F['kw2_close'] = sum([abs(F['kw2_head'][i] - F['kw_head'][i]) + abs(KWS2[i] - F['kw_head_sh'][i])
                      for i in range(NSRC)])
F['kw2_docs'] = len([x for x in KWS2 if x >= 0])
KWP2 = [(a, b) for a in range(NSRC) for b in range(a + 1, NSRC) if KWS2[a] >= 0 and KWS2[b] >= 0]
F['kw2_pair_n'] = len(KWP2)
F['kw2_same'] = [1 if EFB[a][KWS2[a]:KWS2[a] + 200] == EFB[b][KWS2[b]:KWS2[b] + 200] else 0
                 for a, b in KWP2]
F['kw2_same_close'] = sum([abs(x - y) for x, y in zip(F['kw2_same'], F['kw_same'])])
# ---------- 本遍布尔门 ----------
EG2 = []
EG2.append((u'本遍折平四档与量测段同串',
            F['pp_face_all'] == 1 and F['pp_face_shell'] == 1 and F['pp_face_shell_case'] == 1
            and F['pp_face_all_case'] == 1))
EG2.append((u'本遍句界尺与量测段同切点', F['pp_sent_close'] == 0))
EG2.append((u'答句五份各只命中一枚', all([len(occ_at(EFB[i], pnorm(ANSK[i]))) == 1 for i in range(NSRC)])))
EG2.append((u'切开针三档自相减=行内档', F['sc_line_close'] == 0 and F['sc_occ_close'] == 0))
EG2.append((u'跨行枚数与涨量同数且针集同名单',
            F['sc_cut_close'] == 1 and F['sc_gain_close'] == 0))
EG2.append((u'去编号面上针数=第三档登记值', F['tc_occ_close'] == 0))
EG2.append((u'大写跨行逐份对上第三轨差',
            sum([abs(x) for x in F['st_by_doc']]) == 0 and F['st_up_close'] == 0))
EG2.append((u'段窗行号回原文件对得上', F['sr_rows_close'] == 0))
EG2.append((u'窗内语气词两把尺同数', F['pb_tone_close'] == 0 and F['pb_phrase_close'] == 0))
EG2.append((u'五份答句都落在自己那段窗里', F['pb_ans_close'] == 0))
EG2.append((u'段落对照六项与量测段同数',
            sum(F['ov2_rows_close']) == 0 and sum(F['ov2_sents_close']) == 0
            and sum(F['ov2_shell_close']) == 0))
EG2.append((u'新句只由编号差与归拼差解释',
            F['ov2_new_close'] == 0 and sum(F['ov2_same_close']) == 0))
EG2.append((u'内核键数 ⇎ 重名 ⇎ 相关键三档同名单',
            F['kn2_keys_close'] == 0 and F['kn2_dup_close'] == 0 and F['kn2_rel_close'] == 0
            and F['kn2_pick_close'] == 0))
EG2.append((u'内核容斥自证且与量测段同并集', F['kn2_ie_close'] == 0 and F['kn2_union_close'] == 0))
EG2.append((u'默认值四式级联逐键同值同式', F['kn2_dv_diff'] == [] and F['kn2_wrap_close'] == 0))
EG2.append((u'倍增第三轨与两把旧尺同数',
            sum([abs(y) for z in F['eq2_ruler_gap'] for y in z]) == 0
            and sum([abs(y) for z in F['eq2_close'] for y in z]) == 0))
EG2.append((u'印出的秒数与等式末两项逐格对上',
            all([EQ2[t][2] == EQ2[t][4] and EQ2[t][3] == EQ2[t][5] for t in range(2)])))
EG2.append((u'924.6 五候选现算仍不落', F['eq2_hit'] == 0 and F['eq2_hit_close'] == 0
                               and F['eq2_face_close'] == 0.0 and F['eq2_9246_unit'] == 1
                               and F['eq2_9246_n'] == 1
                               and sum(F['eq2_cand_close']) == 0.0))
EG2.append((u'独占针在他份零命中(本遍尺)', F['ng2_others'] == 0 and F['ng2_close'] == 0))
EG2.append((u'共现针张张在他份(本遍尺)', F['rp2_close'] == 0 and F['rp2_others'] > 0
                               and F['rp2_reprint'] == 1))
EG2.append((u'模板段偏移两档同值且配对同数', F['kw2_close'] == 0 and F['kw2_pair_n'] == F['kw_pair_n']
                                        and F['kw2_docs'] == 2))
EG2.append((u'块不越节而截串恰指着下一节号',
            all([OVNEXT2[t] and OVOVN[t][0] < OVBLK[t][2] and OVBLK[t][3] < OVNEXT2[t][0][0]
                 and (OVBLK[t][6] < 0 or OVBLK[t][6] == OVNEXT2[t][0][0])
                 and F[u'ov_stop_str'][t].startswith(F[u'ov_next_sec'][t]) for t in range(2)])
            and F['ov_hdr_rows'][0] > 1 and F['ov_hdr_rows'][1] > 1))
EG2.append((u'两块同节题而编号不同', F['ov_title_same'] == 1 and F['ov_sec_shift'] == 1
                                   and F['ov_sec'][0] in u''.join(T[1])
                                   and F['ov_sec'][1] in u''.join(T[2])))
GK2 = []
for _gi, (_nm, _v) in enumerate(EG2):
    _sl = re.sub(u'[^a-z0-9]', u'', _nm)[:12]
    _key = u'gc2_' + (_sl if _sl != u'' else u'%02d' % _gi)
    while _key in F:
        _key += u'x'
    F[_key] = 1 if _v else 0
    GK2.append([_key, _nm, 1 if _v else 0])
F['gate2_keys'] = GK2
F['bool2_all'] = len(EG2)
F['bool2_green'] = len([1 for _nm, _v in EG2 if _v])
F['bool2_red'] = [_nm for _nm, _v in EG2 if not _v]
F['bool2_red_count'] = len(F['bool2_red'])
F['bool_clos2_n'] = F['bool2_green'] - F['bool2_all']
if F['bool2_red']:
    DIAG2 = dict([(k, F[k]) for k in
                  [u'tc_occ_close', u'tc_gain_close', u'sc_occ_close', u'sc_line_close',
                   u'st_up', u'st_low', u'st_up_close', u'st_by_doc', u'sr_rows_close',
                   u'pb_ans_win', u'pb_ans_n', u'pb_ans_close', u'pb_tone_tag', u'tag_dash',
                   u'td_face_same', u'td_face_gap', u'eq2_cand_close',
                   u'ov2_rows', u'ov2_sents', u'ov2_shell', u'ov2_same_raw', u'ov2_same_tag',
                   u'ov2_same_canon', u'ov2_new', u'ov2_rows_close', u'ov2_sents_close',
                   u'ov2_shell_close', u'ov2_same_close', u'ov2_new_close', u'ov2_chars',
                   u'eq2_rows', u'eq2_close', u'eq2_ruler_gap', u'eq2_cand', u'eq2_hit',
                   u'eq2_9246_face', u'eq2_9246_face_', u'eq2_9246_n', u'eq2_9246_unit',
                   u'eq2_face_close', u'eq2_printed', u'eq2_printed_close']
                  if k in F])
    DIAG2[u'ovl'] = dict([(k, F[k]) for k in [u'ovl_rows', u'ovl_shell', u'ovl_s1', u'ovl_s2',
                                              u'ovl_same_raw', u'ovl_same_tag', u'ovl_new',
                                              u'blk_tag_n']])
    _p = ([k for k in range(min(len(TDF[2]), len(SHTAG[2]))) if TDF[2][k] != SHTAG[2][k]] or [-1])[0]
    DIAG2[u'td_diff_at'] = _p
    DIAG2[u'td_mine'] = TDF[2][max(0, _p - 60):_p + 60]
    DIAG2[u'td_his'] = SHTAG[2][max(0, _p - 60):_p + 60]
assert F['bool2_green'] == F['bool2_all'], (F['bool2_red'],
                                            json.dumps(DIAG2, ensure_ascii=False, sort_keys=True))
# ---------- 本遍恒等式(Z2: 每条都要减掉真量, 全归零才算平) ----------
Z2 = []


def ZEXP(expr, what):
    Z2.append((expr, what))
    ZV.append((expr, what))


ZEXP(u"B86V('pp_face_all') + B86V('pp_face_shell') + B86V('pp_face_shell_case') + B86V('pp_face_all_case') - 4",
     u'四档面逐档与本遍同串: 折平 ⇎ 摘壳 ⇎ 摘壳保形 ⇎ 折平保形')
ZEXP(u"sum(B86V('pp_face_len'))", u'本遍折出来的摘壳面与量测段的摘壳面一枚字符也不差')
ZEXP(u"sum(B86V('pp_rows_close'))", u'非壳行加壳行等于原行数(逐份, 空档不留一行)')
ZEXP(u"sum(B86V('pp_rows_all')) - sum(B86V('splitnl'))", u'本遍行表枚到的行 = split(\"\\n\") 的行数')
ZEXP(u"sum(B86V('pp_rows_kept')) - sum(B86V('body_lines'))", u'本遍摘下的非壳行 = 量测段的剥壳正文行')
ZEXP(u"B86V('pp_sent_close')", u'句界两把尺(正则切点 ⇎ 逐字符扫)在摘壳面上同切点')
ZEXP(u"sum(B86V('ans_line_close'))", u'答句首行由逐字符行表重导 = 累积长度表那把读数')
ZEXP(u"sum(B86V('ans_end_close'))", u'答句末行两把行号尺同值')
ZEXP(u"sum(B86V('ans_span_close'))", u'答句跨行枚数两把行号尺同值')
ZEXP(u"sum(B86V('ans_words_close'))", u'答句词数由本遍保形面重切 = 建条遍那把')
ZEXP(u"sum(B86V('ans_sent_same')) - 5", u'五份答句逐字符相同(本遍句界 ⇎ 建条遍句界)')
ZEXP(u"sum(B86V('ans_shell_close'))", u'答句跨度内的页壳行枚数: 本遍行号表重导 = 建条遍那一枚')
ZEXP(u"sum(B86V('ans_page_close'))", u'答句跨度里的页码页眉行两把谓词同数')
ZEXP(u"sum(B86V('ans2_rows_kept')) + sum(B86V('ans2_shell_rows')) - sum(B86V('ans2_rows_whole'))",
     u'答句整行尺行数 = 非壳行加壳行(同一窗两种筛法)')
ZEXP(u"B86V('sc_occ_close')", u'切开针三档: 本遍逐枚命中的总枚数 = 摘壳面正则计数')
ZEXP(u"B86V('sc_line_close')", u'每枚针: 总命中 − 跨行命中 − 同行重枚 = 行内尺命中')
ZEXP(u"B86V('sc_gain_close')", u'跨行命中总数 = 换行档相对行内档的增益(不登记第二次)')
ZEXP(u"sum(B86V('sc_doc_gain_close'))", u'逐份的换行增益也与按枚相加对上')
ZEXP(u"B86V('sc_needle_n') - B86V('wrap_cut_n')", u'被换行切开的针种数两遍同数(枚举命中 ⇎ 逐档比大小)')
ZEXP(u"B86V('tc_span_after') - B86V('tc_span_before')", u'去编号不吃掉任何一枚跨行针(前后同数)')
ZEXP(u"B86V('tc_occ_close')", u'去编号面上的逐枚命中 = 第三档登记值')
ZEXP(u"B86V('tc_gain_close')", u'去编号新读通的针种数两遍同名单')
ZEXP(u"sum(B86V('td_face_gap')) - sum(B86V('tag_chars')) + sum(B86V('td_chars'))",
     u'两把去编号尺吃字之差 = 面长之差(编号族只在 9293, 余四份零)')
ZEXP(u"B86V('st_up_close')", u'大写跨行义务词逐对现拼 = 第三轨差之和')
ZEXP(u"sum(B86V('st_by_doc'))", u'逐份的大写跨行账各自归零')
ZEXP(u"B86V('st_in_shell')", u'跨行义务词的那一对相邻行没有一枚落在页壳里')
ZEXP(u"sum(B86V('st_up')) + sum(B86V('st_low')) - B86V('st_tot')", u'跨行式按大小写分档相加=总数')
ZEXP(u"B86V('sr_rows_close')", u'段窗首末行回原文件逐枚对得上(整针那档)')
ZEXP(u"B86V('sr_whole') + B86V('sr_cut') - B86V('sr_n')", u'段端点两档相加=总数: 一行读通 ⇎ 被换行推开')
ZEXP(u"B86V('sr_n') - 2 * len(B86V('pb_rows'))", u'每枚段窗交两头行号自验: 端点探针数 = 窗数×2')
ZEXP(u"B86V('pb_words_tot') - sum(B86V('pb_words'))", u'段窗词数两遍枚举相加同值')
ZEXP(u"B86V('pb_chars_tot') - sum(B86V('pb_chars'))", u'段窗字符数两遍枚举相加同值')
ZEXP(u"B86V('pb_ans_close')", u'每份的答句都落在本份某一枚段窗内(无一份落空)')
ZEXP(u"B86V('pb_tone_close') + B86V('pb_phrase_close')", u'窗内义务词单词档与短语档两把尺同数')
ZEXP(u"sum(B86V('pb_tag_block_close'))", u'窗内编号枚数 = 整段 ⇎ 整份登记值(两处各归零)')
ZEXP(u"sum(B86V('ov2_rows_close'))", u'段落对照块高: 本遍字面针开窗 = 采集侧滑窗找端点')
ZEXP(u"sum(B86V('ov2_sents_close'))", u'块内句数两遍同数(正则句界 ⇎ 逐字符句界)')
ZEXP(u"sum(B86V('ov2_shell_close'))", u'块内页壳行数两遍同数')
ZEXP(u"sum(B86V('ov2_same_close'))", u'逐字同 ⇎ 去编号同 ⇎ 归拼同三档两遍同数')
ZEXP(u"B86V('ov2_new_close')", u'新句枚数两遍同数')
ZEXP(u"B86V('ov2_sents', 1) - B86V('ov2_same_tag') - B86V('ov2_new')", u'9293 的句 = 与 1122 同句 + 新句(无第三档)')
ZEXP(u"sum(B86V('ov2_chars')) - B86V('blk_chars', 0) - B86V('blk_chars', 1)",
     u'块字符数由行表重导 = 量测段整串折平的长度')
ZEXP(u"B86V('ov2_sub')", u'反向对照: 9293 那段整块不是 1122 那段的子串(逐句同 ⇎ 整块连读不通)')
ZEXP(u"B86V('os_located') - B86V('os_n')", u'每枚新句都能在 9293 面上定位')
ZEXP(u"B86V('os_ambig')", u'新句的四十码位前缀在本份面上没有一枚多解')
ZEXP(u"B86V('kn2_keys_close')", u'内核键行数 = 量测段键行计数')
ZEXP(u"B86V('kn2_keys') - B86V('kn2_uniq') - len(B86V('kn2_dups'))", u'键行 − 去重 = 重名键种数')
ZEXP(u"B86V('kn2_hdr_rows') - B86V('kn2_keys')", u'键行清单两处枚法同数(逐行匹配 ⇎ 建表)')
ZEXP(u"B86V('kn2_keys') - B86V('keylin', 4)", u'键行只在那份内核文档里印出')
ZEXP(u"B86V('kn2_dup_close')", u'重名键名单两遍同集')
ZEXP(u"B86V('kn2_rel_close')", u'相关键(名 ⇎ 正文双判)名单两遍同集')
ZEXP(u"B86V('kn2_pick_close')", u'相关键(只按名)名单两遍同集')
ZEXP(u"B86V('kn2_body_close')", u'相关键正文行合计两遍同数')
ZEXP(u"B86V('kn2_union_close') - B86V('kn2_ie_close')", u'两把名尺的并集与容斥同时归零')
ZEXP(u"B86V('kn2_wrap_close')", u'换行才丢默认值的那三枚键名两遍同名单')
ZEXP(u"len(B86V('kn2_dv_diff'))", u'默认值四式级联逐键与量测段同值(不同者列成清单, 清单为空)')
ZEXP(u"sum(B86V('kn2_shape_close'))", u'默认句式四档计数两遍同数')
ZEXP(u"sum([abs(y) for z in B86V('eq2_close') for y in z])", u'倍增等式逐格重算与印出的秒数全对上')
ZEXP(u"sum([abs(y) for z in B86V('eq2_ruler_gap') for y in z])", u'幂清单求和 ⇎ 闭式 ⇎ 逐次累加三轨同值')
ZEXP(u"sum(B86V('eq2_printed_close'))", u'面上印出的秒数枚数两遍同数')
ZEXP(u"B86V('eq2_n15_last') * 2 + 1 - B86V('eq2_n15_kill')", u'N=15 末次与杀死两式和: 2·(2^15−1)+1 = 2^16−1')
ZEXP(u"B86V('eq2_min_last') - B86V('eq_min_n_last')", u'达到 100 秒的最小 N(末次口径)两遍同值')
ZEXP(u"B86V('eq2_min_kill') - B86V('eq_min_n_kill')", u'最小 N(杀死口径)两遍同值')
ZEXP(u"B86V('eq2_doc_says') - B86V('eq_doc_says')", u'文书自己写的“at least 8”两遍同值')
ZEXP(u"sum(B86V('eq2_off_by')) - sum(B86V('eq_off_by'))", u'文书口径与复算口径的差两遍同数')
ZEXP(u"B86V('eq2_dev_close')", u'924.6 的五枚偏离两遍逐格同值')
ZEXP(u"B86V('td_face_gap', 2) + B86V('td_chars', 2) - B86V('tag_chars', 2)",
     u'9293 的去编号面差恰为两把尺吃字之差')
ZEXP(u"B86V('ov_title_same') + B86V('ov_sec_shift') - 2", u'两块的节题同词而编号不同')
ZEXP(u"B86V('eq2_9246_n') - sum(B86V('eq9246_by_src'))", u'924.6 只在一份面上印出(逐份相加 ⇎ 本遍枚举)')
ZEXP(u"B86V('eq2_face_close')", u'924.6 由面导偏移读出 = 量测段那把尺的读数')
ZEXP(u"sum(B86V('eq2_cand_close'))", u'924.6 的五枚候选两遍逐格同值')
ZEXP(u"B86V('eq2_hit') + B86V('eq2_hit_close')", u'五枚候选复算不出 924.6(两遍都判不落)')
ZEXP(u"sum(B86V('eq2_rto_close'))", u'面上三枚 RTO 参数由字符扫描器现取 = 量测段正则分组')
ZEXP(u"B86V('ng2_others')", u'独占针在被排除的那几份上零命中(本遍尺)')
ZEXP(u"B86V('ng2_close')", u'独占针矩阵逐格与量测段同数')
ZEXP(u"B86V('ng2_self') - B86V('neg_self_tot')", u'独占针在自己那份读得到的枚数两遍同值')
ZEXP(u"B86V('rp2_close')", u'共现针矩阵逐格同数')
ZEXP(u"B86V('rp2_others') - B86V('rp_others')", u'共现针在他份的命中总数两遍同值')
ZEXP(u"B86V('rp2_reprint') - B86V('rp_reprint_9293')", u'9293 恰好复印 793 那枚事件表句一次')
ZEXP(u"len(B86V('rp2_mat')) - B86V('rp_n')", u'共现针枚数两遍同数')
ZEXP(u"B86V('kw2_close')", u'模板段偏移两档(折平 ⇎ 摘壳)现推与量测段同值')
ZEXP(u"B86V('kw2_docs') - B86V('kw_docs')", u'印出模板段的份数两遍同值')
ZEXP(u"B86V('kw2_pair_n') - B86V('kw_pair_n')", u'模板段配对数两遍同值')
ZEXP(u"sum(B86V('kw2_same')) - sum(B86V('kw_same'))", u'模板段二百码位窗相同的对数两遍同判')
ZEXP(u"B86V('bool2_red_count')", u'发射遍布尔门的红数为零')
ZEXP(u"sum(B86V('dur_by_form')) - sum([sum(x) for x in B86V('dur')])", u'时长十式: 逐式合计 = 逐份总和')
ZEXP(u"sum(B86V('dur_by_doc')) - sum(B86V('dur_by_form'))", u'时长十式: 两把聚合尺同值')
ZEXP(u"B86V('bool2_green') - B86V('bool2_all')", u'发射遍布尔门全绿')
ZEXP(u"B86V('ng2_multi_close')", u'反向多解的式数两遍同判')
ZEXP(u"len(B86V('ng2_multi_cnt')) - len(B86V('neg_multi'))", u'多解枚数清单与建条名单同长')
ZEXP(u"B86V('scan2_src_n') - B86V('scan_key_n') - 1",
     u'建条遍快照键数 = 它的自计数键 + 1')
ZEXP(u"len(B86V('scan2_unprefixed'))", u'本遍新登记的键全在白名单前缀里')
ZEXP(u"len(B86V('scan2_prefixed_old')) - 2",
     u'前缀尺多捞的恰是建条遍那两枚 ans_(page|shell)_rows')
F['zid_scan2_n'] = len(Z2)
ADDED = sorted([k for k in F if k not in K0])
EMITKEYS = sorted([k for k in F if re.match(u'^(pp_|ans2_|ans_line_|ans_end_|ans_span_|ans_words_|ans_sent_same|ans_shell_|ans_page_|sc_|tc_|td_|st_|pb_|sr_|ov2_|ov_(sec|next|title|hdr|cut|stop)|os_|kn2_|eq2_|ng2_|rp2_|kw2_|gc2_|gate2_|bool2_|bool_clos2|scan2_|zid_scan2|dur_)', k)])
F['scan2_unprefixed'] = sorted(set(ADDED) - set(EMITKEYS))
F['scan2_prefixed_old'] = sorted(set(EMITKEYS) - set(ADDED))
F['scan2_src_n'] = len(K0)
F['scan2_key_n'] = len(ADDED)
F['scan2_self_n'] = 5
# --- SCAN2 END ---
if PROBE:
    print(u'  前缀尺多捞 %s ⇎ 本遍键漏前缀 %s' % (F['scan2_prefixed_old'], F['scan2_unprefixed']))
print(u'发射段: 本遍键 %d 枚 ⇎ 门 %d/%d 绿 ⇎ 恒等式 %d 条 ⇎ 红 %s'
      % (F['scan2_key_n'], F['bool2_green'], F['bool2_all'], F['zid_scan2_n'], F['bool2_red']))
if PROBE:
    for e, w in Z2:
        vv = _ev(e)
        if vv != 0:
            print(u'   不平 %s = %s (%s)' % (e, vv, w))
    print(json.dumps(dict([(k, F[k]) for k in sorted(set(F) - K0)]), ensure_ascii=False, sort_keys=True, default=str))

# --- 段二 BEGIN --- (编码区正文: 每枚三位以上的数都由 V()/J()/C()/EXPR() 登记过算式, 锚一律由面导位置)
PLBL = [u'%s#%d' % (LBL[i], n + 1) for n, (i, s, e) in enumerate(PINS)]
WLBL2 = [u'1122', u'9293']
if PROBE:
    _V0, _J0, _JL0 = V, J, JL

    def V(name, i=None, note=u''):
        try:
            return _V0(name, i, note)
        except Exception as e:
            BADREAD.append((u'V', name, i, repr(e)[:70]))
            return u'?'

    def J(name, note=u''):
        try:
            return _J0(name, note)
        except Exception as e:
            BADREAD.append((u'J', name, None, repr(e)[:70]))
            return u'?'

    def JL(name, note=u''):
        try:
            return _JL0(name, note)
        except Exception as e:
            BADREAD.append((u'JL', name, None, repr(e)[:70]))
            return u'?'


def _try(tag, name, pos, thunk):
    if PROBE:
        try:
            return thunk()
        except Exception as e:
            BADREAD.append((tag, name, pos, repr(e)[:60]))
            return u'?'
    return thunk()


def _q(i, seg):
    return u'⟦%s⟧⟨%s⟩' % (LBL[i], seg)


def QA(i, phrase):
    """单份锚: 由该份摘壳面现取行内片段, 包上归属标签。"""
    if PROBE:
        try:
            return _q(i, AN(i, phrase))
        except Exception as e:
            BADREAD.append((u'QA', LBL[i], phrase[:40], repr(e)[:60]))
            return u'⟦%s⟧⟨?%s⟩' % (LBL[i], phrase[:18])
    return _q(i, AN(i, phrase))


def QM(phrase):
    """归属锚: 哪几份的摘壳面读得到这一式, 就给哪几份各一枚行内锚。"""
    q = pnorm(phrase)
    hits = [i for i in range(NSRC) if q in EFB[i]]
    assert hits, phrase[:40]
    return u' ⇎ '.join(QA(i, phrase) for i in hits)


def pieces(i, h, nd):
    """跨行命中的针按行表切成逐行片段(每段都是原行的逐字片段)。"""
    m = MRB[i]
    q = h + len(nd)
    out = []
    for r in sorted(set(m[h:q])):
        ps = [p for p in range(h, q) if m[p] == r]
        out.append(EFB[i][ps[0]:ps[-1] + 1])
    return out


def AQ(i, phrase):
    """答句/判词针锚: 被硬换行切开的给逐行两半, 否则给整串那一行。"""
    q = pnorm(phrase)
    hs = occ_at(EFB[i], q)
    assert hs, (LBL[i], phrase[:40])
    sp = [h for h in hs if len(ln_span(i, h, h + len(q))) > 1]
    if not sp:
        return QA(i, phrase)
    return u' ⇎ '.join(QA(i, z) for z in pieces(i, sp[0], q))


def ACUT(k, cap=3):
    """第 k 枚判词针: 每个被换行切开的(份, 命中)给一对逐行片段锚。"""
    out = []
    for i in range(NSRC):
        for h in (SCROWS.get((k, i), []) or [])[:cap]:
            out.append(u'%s: ' % LBL[i] + u' ⇎ '.join(QA(i, z)
                                                      for z in pieces(i, h, NK[k])))
    return u' ‖ '.join(out)


def JT(name, note=u''):
    """只有 1122 ⇎ 9293 两份的段落键。"""
    return u' ⇎ '.join(V(name, n, u'%s·%s' % (note or name, WLBL2[n])) for n in range(2))


def PJ(name, note=u''):
    """逐扇段窗的键(窗号由 PINS 现导)。"""
    return u' ⇎ '.join(V(name, n, u'%s·%s' % (note or name, PLBL[n])) for n in range(len(PINS)))


def C(name, i, j, note=u''):
    return _try(u'C', name, u'%d,%d' % (i, j),
                lambda: EXPR(F[name][i][j], u"%s('%s', %d)[%d]" % (FN, name, i, j),
                             note or u'%s·%s' % (name, LBL[i])))


def JO(name, note=u''):
    """按清单自身长度逐项登记(两轨 ⇎ 三轨 ⇎ 五份都由清单现导, 不假定 NSRC)。"""
    v = F[name]
    if PROBE and not isinstance(v, list):
        BADREAD.append((u'JO', name, u'', u'标量'))
        return u'?'
    return u' ⇎ '.join(EXPR(x, u"%s('%s')[%d]" % (FN, name, n), u'%s·[%d]' % (note or name, n))
                       for n, x in enumerate(v))


def CM(name, n, j, note=u''):
    """扁清单里那一行的第 j 列: 行号与列号都由清单现取。"""
    return _try(u'CM', name, u'%d,%d' % (n, j),
                lambda: EXPR(F[name][n][j], u"%s('%s')[%d][%d]" % (FN, name, n, j),
                             note or u'%s·[%d]' % (name, n)))


def LEN5(name, note=u''):
    """五份的“清单长度”一把尺: 把 len() 现算写进算式, 不另设键。"""
    return u' ⇎ '.join(EXPR(len(F[name][i]), u"len(%s('%s', %d))" % (FN, name, i),
                           u'%s·%s' % (note or name, LBL[i])) for i in range(NSRC))


def SUM5(name, what, note=u''):
    return EXPR(sum(F[name]), u"sum([%s])" % u','.join(
        [u"%s('%s', %d)" % (FN, name, i) for i in range(NSRC)]), note or what)


LINES = []
LINES.append(
    u'📜 五份一手文书同一副纯文本面: 最长行 ' + J(u'maxlen', u'最长行') + u' 列(逐字符扫 ⇎ 逐行 max 两把尺的分歧合计 '
    + EXPR(sum([abs(F[u'maxlen'][i] - F[u'maxlen_scan'][i]) for i in range(NSRC)]),
           u"sum([abs(%s('maxlen', %d)-%s('maxlen_scan', %d)) for %s in range(5)])" % (FN, 0, FN, 0, u'i'), u'最长行两尺分歧')
    + u' 列), 字节 ' + J(u'bytes', u'字节') + u'(与 os.stat 同值 '
    + V(u'bytes_vs_stat', None, u'字节对账') + u') ⇎ 面内码位 ' + J(u'cp', u'码位') + u', 差额账 '
    + J(u'byte_cp_ledger', u'字节码位账') + u' 全平: 只有 9293 两数不等, 差在它带着 BOM 与非 ASCII。 '
    + u'行数三把尺各读一遍: split("\\n") ' + J(u'splitnl', u'split尺') + u' ⇎ splitlines() '
    + J(u'splitlines', u'splitlines尺') + u' ⇎ 逐行读入 ' + J(u'readlines', u'逐行尺') + u', 结尾换行 '
    + J(u'trailing_nl', u'尾换行') + u' 枚 ⇎ 逐行读入与 split("\\n") 的分歧 ' + J(u'lf_vs_readlines', u'逐行分歧')
    + u'; splitlines 多出的 ' + J(u'rows_ledger', u'行尺差') + u' 行正是换页符 ' + J(u'ff', u'换页枚')
    + u' 枚吃出来的(它把 \\x0c 也当行界, 另两把尺不认), 这一档两遍谓词同数 ' + J(u'rows_pred', u'行尺差复算')
    + u' ⇎ 分歧 ' + J(u'rows_ledger_diff', u'行尺差分') + u'。 换页 ' + J(u'ff', u'换页枚') + u' 枚里独占整行的 '
    + J(u'ff_alone', u'FF独占') + u' ⇎ 紧接换行的 ' + J(u'ff_before_nl', u'FF贴换行') + u' ⇎ 落在文件尾的 '
    + J(u'ff_at_eof', u'FF在EOF') + u', 账 ' + J(u'ff_led', u'换页账') + u'。 回车 ' + J(u'n_cr', u'CR枚')
    + u' 枚: 五份全 LF 面; 制表符只在 ip-sysctl(' + J(u'tab', u'TAB枚') + u' 枚), 其余四份靠 72 列硬换行排版。')

LINES.append(
    u'🧾 页壳七路谓词并起来判(空行 ⇎ 独占行换页 ⇎ 页脚 ⇎ 793 眉 ⇎ 1122 眉 ⇎ IETF 独立行 ⇎ 新式眉): 壳行两把尺各数一遍 '
    + J(u'shell_pick', u'壳行采集尺') + u' ⇎ ' + J(u'shell_shape', u'壳行形状尺') + u', 逐行分歧 '
    + J(u'shell_pred_diff', u'壳谓词分歧') + u' 行; 账 ' + J(u'shell_ledger', u'壳账') + u' 全平 ⇎ 剥壳正文行 '
    + J(u'body_lines', u'剥壳正文行') + u' 行。 成分: 空行 ' + J(u'blank', u'空行') + u' ⇎ 页脚 ' + J(u'foot', u'页脚')
    + u' ⇎ 793 式眉行 ' + J(u'hdr793', u'793眉') + u' ⇎ 1122 式眉行 ' + J(u'hdr1122', u'1122眉') + u' ⇎ 新式眉行 '
    + J(u'hdrnew', u'新式眉') + u' ⇎ IETF 独立行 ' + J(u'ietf_alone', u'IETF独立') + u'。 页码另拿一把 naive 尺(整行只有数字与空格 ⇎ '
    + u'只含一段数字): 报 ' + J(u'pgnum', u'naive页码') + u' 行, 其中合壳形的 ' + J(u'pgnum_in_shell', u'壳内页码')
    + u' 行 ⇎ 裸的 ' + J(u'pgnum_naked', u'裸页码') + u' 行——9293 那 ' + V(u'pgnum', 2, u'naive页码9293')
    + u' 枚全落在事件表的数字列里, 一枚也不合壳形。 内核那份的“壳”换了物种: 键行 ' + J(u'keylin', u'键行')
    + u' 行 ⇎ 印 “Default” 的行 ' + J(u'default_lines', u'Default行') + u' 行, 只在第五份有值。 '
    + u'非 ASCII ' + J(u'na_total', u'非ASCII枚') + u' 枚 ⇎ 所在行 ' + J(u'na_lines', u'非ASCII行') + u' 行 ⇎ 码位清单 '
    + JL(u'na_codepoints', u'非ASCII码位') + u' ⇎ UTF-8 多出的字节 ' + J(u'utf8_extra', u'UTF8多字节') + u'; BOM '
    + J(u'bom', u'BOM') + u' 枚在折平时被当空白吃掉(折平后剩 ' + J(u'bom_after_fold', u'BOM折平后') + u' 枚)。 '
    + u'保形 ⇎ 折小写两档的关系点名: ' + V(u'shpx_eq_pnorm', None, u'保形折小写同折平') + u' —— 摘壳保形面再折小写就是摘壳折平面, '
    + u'所以四档口径之间只差大小写与编号两件事, 不差空白。')

LINES.append(
    u'🪜 同一个问题——重传几次、多久之后该放弃——五份各答一次, 答句逐字取面: ' + AQ(0, ANSK[0]) + u' ⇎ '
    + AQ(1, ANSK[1]) + u' ⇎ ' + AQ(2, ANSK[2]) + u' ⇎ ' + AQ(3, ANSK[3]) + u' ⇎ ' + AQ(4, ANSK[4]) + u'。 '
    + u'词 ' + J(u'ans_words', u'答句词') + u' ⇎ 字符 ' + J(u'ans_chars', u'答句字符') + u' ⇎ 整句跨 '
    + J(u'ans_sent_span', u'答句跨行') + u' 行 ⇎ 首行 ' + J(u'ans_sent_line', u'答句首行') + u' ⇎ 末行 '
    + J(u'ans_sent_end', u'答句末行') + u'; 锚针整串在一行内读得到的 ' + J(u'ans_needle_line', u'答句行内')
    + u' 份(793 那句被 72 列换行切开, 只能给两半)。 这两排行号由建条遍的累积长度表 + bisect 导出, 发射遍改用逐字符行表'
    + u'(每枚字符现挂原行下标)重导一遍: 首行 ' + J(u'ans2_sent_line', u'本遍答句首行') + u' ⇎ 末行 '
    + J(u'ans2_sent_end', u'本遍答句末行') + u' ⇎ 面内偏移 ' + J(u'ans2_off', u'本遍答句偏移') + u', 逐格差 '
    + J(u'ans_line_close', u'首行两遍差') + u' ⇎ 末行 ' + J(u'ans_end_close', u'末行两遍差') + u' ⇎ 跨度 '
    + J(u'ans_span_close', u'跨度两遍差') + u' ⇎ 词数 ' + J(u'ans_words_close', u'词数两遍差') + u' 全平 ⇎ '
    + u'句串逐字符相同 ' + EXPR(sum(F[u'ans_sent_same']), u"sum(%s('%s'))" % (FN, u'ans_sent_same'), u'答句逐字符同') + u'/5。 同一区间再按“整行 ⇎ 摘壳行”两把尺量: '
    + u'整区间 ' + J(u'ans2_rows_whole', u'答句整行') + u' 行 ⇎ 非壳 ' + J(u'ans2_rows_kept', u'答句非壳行')
    + u' 行 ⇎ 壳 ' + J(u'ans2_shell_rows', u'答句壳行') + u' 行, 壳里空行占 ' + J(u'ans2_blank_span', u'答句空行')
    + u' ⇎ 页码页眉 ' + J(u'ans2_page_span', u'答页码行') + u', 与建条侧 ' + J(u'ans_shell_rows', u'建条答句壳行')
    + u'/' + J(u'ans_page_rows', u'建条答页码行') + u' 的差 壳 ' + J(u'ans_shell_close', u'壳行两遍差') + u' ⇎ '
    + J(u'ans_page_close', u'页码两遍差') + u'。 答句里印出的编号: ' + J(u'ans_tag_n', u'答句内编号')
    + u' 枚 ⇎ 大写义务词 ' + JL(u'ans_ob', u'答句义务词') + u' ⇎ 非 ASCII ' + J(u'na_in_ans', u'答句非ASCII') + u' 枚。')

LINES.append(
    u'🪏 同一个问题在五份里被说成 ' + V(u'needle_n', None, u'判词针数') + u' 枚判词, 每枚在四张面串上各数一遍: 逐行 '
    + J(u'role_line_n', u'行内尺') + u' ⇎ 全篇折平 ' + J(u'role_fold_n', u'折平尺') + u' ⇎ 摘壳折平 '
    + J(u'role_sh_n', u'摘壳尺') + u' ⇎ 摘壳去编号 ' + J(u'role_tag_n', u'去编号尺') + u' 枚, 逐档增益(换行 ⇎ 页壳 ⇎ 编号三轨) '
    + JL(u'role_gain', u'逐档增益') + u'。 被硬换行切开的 ' + V(u'wrap_cut_n', None, u'换行切开') + u' 枚 ⇎ 被页壳切开的 '
    + EXPR(len(F[u'shell_cut']), u"len(%s('shell_cut'))" % FN, u'壳切针') + u' 枚 ⇎ 被编号切开 '
    + EXPR(len(F[u'tag_cut']), u"len(%s('tag_cut'))" % FN, u'编号切开') + u' 枚(针号 ' + JL(u'tag_cut', u'编号切针') + u')。 探针总数 ' + V(u'role_probes', None, u'针探针数') + u' 格。 '
    + u'发射遍不问“这一行含不含针”, 而是枚举针在摘壳面上的每一次命中并量它跨几行: 总命中 ⇎ 跨行命中 ⇎ 同行重枚 三档自相减 '
    + u'= 行内尺读数(差 ' + V(u'sc_line_close', None, u'三档自相减') + u'), 总命中与整串正则计数同值(差 '
    + V(u'sc_occ_close', None, u'命中两把尺') + u'), 跨行合计 = 换行增益(差 ' + V(u'sc_gain_close', None, u'跨行即增益')
    + u') ⇎ 逐份差 ' + J(u'sc_doc_gain_close', u'逐份增益差') + u' ⇎ 最长跨 ' + V(u'sc_max_span', None, u'最长跨行')
    + u' 行 ⇎ 切开针种数两遍同数 ' + V(u'sc_needle_n', None, u'本遍切开针种') + u'/' + V(u'wrap_cut_n', None, u'切开针种')
    + u'。 三枚被切开的针给逐行片段锚(每段都是原行逐字): ' + ACUT(F[u'wrap_cut'][0]) + u' ‖ '
    + ACUT(F[u'wrap_cut'][8]) + u' ‖ ' + ACUT(F[u'wrap_cut'][18]) + u'。')

LINES.append(
    u'🔪 义务词编号族只在 9293: 连字符式 ' + V(u'tag_dash', 2, u'编号连字') + u' 枚 ⇎ 括号内 ' + V(u'tag_in_paren', 2, u'编号括号')
    + u' ⇎ 裸形 ' + V(u'tag_bare', 2, u'编号裸形') + u', 两形状之差 ' + V(u'tag_form_ledger', 2, u'形状差')
    + u' = 括号被整对拉开的那一枚; token 尺 ' + V(u'tag_token', 2, u'编号token') + u' ⇎ 与连字尺缺口 '
    + V(u'tag_token_ledger', 2, u'token缺口') + u' = 方括号套住的两枚 ' + V(u'tag_bracket', 2, u'编号套括')
    + u'; 粘连无空白 ' + V(u'tag_nospace', 2, u'编号粘连') + u' ⇎ 最大号 ' + V(u'tag_max_no', 2, u'编号最大号')
    + u' ⇎ 抹掉编号吃掉的字符 ' + V(u'tag_chars', 2, u'编号吃字') + u'。 按词种分 ' + JL(u'tag_kind', u'编号词种')
    + u'。 被换行切开的编号 ' + V(u'tag_split_manual', 2, u'编号换行切') + u' 枚 = 数字推到下一行 '
    + V(u'tag_num_nextline', 2, u'编号推下行') + u' + 括号整对拉开 ' + V(u'tag_paren_apart', 2, u'括号拉开')
    + u'(账 ' + EXPR(sum([F[u'tag_split_manual'][i] - F[u'tag_num_nextline'][i] - F[u'tag_paren_apart'][i]
                         for i in range(NSRC)]),
                     u"sum([%s('%s', %d)-%s('%s', %d)-%s('%s', %d) for %s in range(5)])"
                     % (FN, u'tag_split_manual', 0, FN, u'tag_num_nextline', 0, FN, u'tag_paren_apart', 0, u'i'),
                     u'切开编号账') + u'), 那一枚的上下文 ' + JL(u'tag_apart_ctx', u'拉开上下文') + u'。 第三档为判词针新增读数 '
    + V(u'tag_gain_tot', None, u'去编号增益') + u' 枚 ⇎ 减 ' + EXPR(sum(F[u'tag_drop_cells']),
                                                                   u"sum(%s('tag_drop_cells'))" % FN, u'去编号跌格')
    + u' 枚, 挪动清单 ' + JL(u'tag_move', u'去编号挪动') + u': 第 ' + CM(u'tag_move', 0, 0, u'挪动针号')
    + u' 枚针在 9293 由 ' + CM(u'tag_move', 0, 2, u'挪动前') + u' 变 ' + CM(u'tag_move', 0, 3, u'挪动后')
    + u' 可读(涨针清单 ' + JL(u'tag_gain_needles', u'涨针清单') + u')。 发射遍按 token 判形状丢弃再逐枚数针: 面串与量测段逐字符同 '
    + J(u'td_face_same', u'去编号面同串') + u' 份 ⇎ 9293 的本遍去编号面比建条面短 '
    + EXPR(F[u'td_chars'][2] - F[u'tag_chars'][2],
           u"%s('td_chars', 2)-%s('tag_chars', 2)" % (FN, FN), u'去编号面短')
    + u' 码位 = 两把尺吃字之差(本遍 ' + V(u'td_chars', 2, u'本遍吃字') + u' ⇎ 建条 ' + V(u'tag_chars', 2, u'编号吃字')
    + u'); 逐枚命中账 ' + V(u'tc_occ_close', None, u'去编号命中账') + u' ⇎ 新读通针种账 ' + V(u'tc_gain_close', None, u'去编号针种账')
    + u' ⇎ 去编号前后跨行枚数 ' + V(u'tc_span_after', None, u'去编号后跨行') + u'/' + V(u'tc_span_before', None, u'去编号前跨行')
    + u'。 义务词声明句 ' + QA(2, u'individually labeled') + u' 只在 9293(' + J(u'labeled_decl', u'声明句') + u' 枚)。')

LINES.append(
    u'⚖ 大写义务词五式(MUST ⇎ MUST NOT ⇎ SHOULD ⇎ SHOULD NOT ⇎ MAY)逐份 ' + JL(u'ob_fold', u'大写折平')
    + u' ⇎ 合计 ' + J(u'ob_fold_tot', u'大写合计') + u'; 小写散文式 ' + JL(u'ob_lower', u'小写折平') + u' ⇎ 合计 '
    + J(u'ob_lower_tot', u'小写合计') + u'。 793 一份大写 ' + V(u'ob_fold_tot', 0, u'大写793') + u' 枚也没有, 全靠 '
    + V(u'ob_lower_tot', 0, u'小写793') + u' 枚小写; 6298 只有 ' + V(u'ob_fold_tot', 3, u'大写6298') + u' 枚。 '
    + u'并集尺(整词)与大写尺的差: ' + J(u'kw_allcaps', u'并集大写') + u' ⇎ ' + J(u'kw_ci', u'并集大小写') + u' ⇎ 只小写 '
    + J(u'kw_lowercase', u'只小写') + u', 账 ' + J(u'ob_nest_ledger', u'嵌套账') + u' 全平。 行内尺与折平尺之差 = 被换行切成两半的短语: 逐(份×式) '
    + EXPR(len(F[u'ob_wrap']), u"len(%s('ob_wrap'))" % FN, u'跨行格数') + u' 格共涨 '
    + EXPR(sum(F[u'ob_wrap']), u"sum(%s('ob_wrap'))" % FN, u'跨行涨量合计')
    + u' 格。 摘壳 ⇎ 折平 ⇎ 去编号三档逐式同数(壳切 ' + V(u'ob_ruler_diff', None, u'壳与折平差') + u' ⇎ 去编号让 9293 的 MAY 由 '
    + V(u'ob_sh', 2, u'9293摘壳MAY') + u' 变 ' + V(u'ob_tag', 2, u'9293去编号MAY') + u' 枚——编号尾巴把 “MAY” 从粘连里解放出来)。 '
    + u'发射遍不拿两档相减, 而是逐对相邻非空行现拼首尾 token: 大写跨行 ' + J(u'st_up', u'本遍大写跨行') + u' 对 ⇎ 小写跨行 '
    + J(u'st_low', u'本遍小写跨行') + u' 对 ⇎ 词种 ' + JL(u'st_words', u'跨行词种') + u' ⇎ 涉及 ' + V(u'st_docs', None, u'跨行份数')
    + u' 份 ⇎ 落在页壳里的 ' + V(u'st_in_shell', None, u'跨行落壳') + u' 对; 与量测段逐份差 ' + J(u'st_by_doc', u'跨行逐份差')
    + u' ⇎ 合计差 ' + V(u'st_up_close', None, u'跨行合计差') + u'。 例: ' + QA(1, u'MUST NOT') + u' ⇎ '
    + QA(2, u'SHOULD NOT') + u' 的跨行那一类只能靠两半读。')

LINES.append(
    u'🔢 带单位数值项 严 ' + J(u'numval_n', u'数值项严') + u' ⇎ 宽 ' + J(u'numval_wide_n', u'数值项宽') + u'(宽多出 '
    + JL(u'numval_extra', u'宽多出') + u'), 两轨差 ' + V(u'numunit_ruler_diff', None, u'数值两轨差') + u'; 只在折平后才读得到的(数字与单位被换行分到两行) '
    + LEN5(u'numunit_wrap', u'只折面数值') + u' 组。 粘连写法只在内核那份: ' + J(u'glued_n', u'粘连枚') + u' 枚 ⇎ 去重 '
    + J(u'glued_vari', u'粘连去重') + u' 式 ⇎ 样本 ' + JL(u'glued_all', u'粘连样本') + u' ⇎ 带空格写法 '
    + J(u'spaced_n', u'带空格') + u' 处; 次数式(“N times”“3 retransmissions”) ' + JL(u'numtimes', u'次数式') + u'。 '
    + u'时长十式逐份合计 ' + J(u'dur_by_doc', u'时长逐份') + u' 枚 ⇎ 逐式(五分 ⇎ 三分 ⇎ 百秒 ⇎ 六十秒 ⇎ 924.6 秒 ⇎ '
    + u'1second ⇎ 63seconds ⇎ 127seconds ⇎ 31seconds ⇎ 两小时)跨五份合计 ' + JL(u'dur_by_form', u'时长逐式') + u' 枚。 '
    + u'面锚: ' + QA(0, u'The present global default is five minutes') + u' ⇎ ' + QA(3, u'at least 60 seconds')
    + u' ⇎ ' + QA(4, u'127seconds') + u' ⇎ ' + AQ(1, u'The value of R2 SHOULD correspond to at least 100 seconds') + u'。')

LINES.append(
    u'📖 语形族 ' + EXPR(len(F[u'spell'][0]), u"len(%s('spell')[0])" % FN, u'语形式种') + u' 列 × 五份: 总量 '
    + J(u'spell_tot', u'语形总量') + u' ⇎ 出现的式种数 ' + J(u'spell_vari', u'语形式种') + u' 种 ⇎ 一枚也不出的式 '
    + JL(u'spell_cold', u'语形全冷') + u'(三份 TCP 文书都写 “time out” 或 “timeout”, 没有连字式)。 子串尺比整词尺多读 '
    + EXPR(sum(F[u'spell_diff']), u"sum(%s('spell_diff'))" % FN, u'子串多读') + u' 枚 = 两把尺合计之差(整词尺 '
    + EXPR(sum(F[u'spell_word_tot']), u"sum(%s('spell_word_tot'))" % FN, u'整词尺合计') + u' 枚 ⇎ 账 '
    + EXPR(sum(F[u'spell_tot']) - sum(F[u'spell_word_tot']) - sum(F[u'spell_diff']),
           u"sum(%s('spell_tot'))-sum(%s('spell_word_tot'))-sum(%s('spell_diff'))" % (FN, FN, FN), u'两尺账平')
    + u' 归零, 同一族上两把尺不能混用)。 独有式清单 ' + JL(u'spell_excl', u'独有式') + u' ⇎ 合计 ' + V(u'excl_n', None, u'独有式枚')
    + u' 枚: “the TCP will” 只在 793 ' + J(u'tcp_will', u'the TCP will') + u' 枚 ⇎ “the TCP endpoint will” 只在 9293 '
    + J(u'tcp_endpoint_will', u'the TCP endpoint will') + u' 枚——9293 把 “TCP endpoint” 立成术语, 793 说 “the TCP”。 锚 '
    + QA(0, u'the tcp will') + u' ⇎ ' + QA(2, u'the tcp endpoint will') + u' ⇎ ' + QM(u'rfc 1122 recommends') + u'。')

LINES.append(
    u'🧩 1122 §' + F[u'ov_sec'][0] + u'(“' + F[u'ov_sec_title'][0] + u'”)与 9293 §' + F[u'ov_sec'][1]
    + u'(“' + F[u'ov_sec_title'][1] + u'”)题面逐字同词 ⇎ 编号不同(同一道题在两份文书里挂在不同节号下), 是同一段落的两次回答: 块高 '
    + JT(u'ovl_rows', u'段行') + u' 行(含页壳 '
    + JT(u'ovl_shell', u'段壳行') + u' 行) ⇎ 字符 ' + JT(u'blk_chars', u'段字符') + u' ⇎ 词 ' + JT(u'blk_words', u'段词')
    + u' ⇎ 句 ' + V(u'ovl_s1', None, u'1122句数') + u'/' + V(u'ovl_s2', None, u'9293句数') + u'(两把句界尺逐句同列表: 差 '
    + V(u'ovl_splitter_diff', None, u'句界尺差') + u' ⇎ 列表同 ' + V(u'ovl_splitter_list', None, u'句界同列') + u')。 '
    + u'逐字同 ' + V(u'ovl_same_raw', None, u'逐字同句') + u' 句 ⇎ 剥编号后同 ' + V(u'ovl_same_tag', None, u'剥编号同句')
    + u' ⇎ 归拼后同 ' + V(u'ovl_same_canon', None, u'归拼同句') + u' ⇎ 新句 ' + V(u'ovl_new', None, u'段落新句') + u' 句; '
    + u'词面差分: 相同 ' + V(u'blk_equal_words', None, u'相同词') + u' 词/' + V(u'blk_equal_runs', None, u'相同段')
    + u' 段, 最长连跑 ' + V(u'blk_longest', None, u'最长连跑') + u' 词 ⇎ 删 ' + V(u'blk_drop_words', None, u'删词')
    + u' ⇎ 插 ' + V(u'blk_insert_words', None, u'插词') + u' ⇎ 替换 ' + V(u'blk_replace', None, u'替换段') + u' 段 ⇎ '
    + u'三条词账 ' + JL(u'blk_form_ledger', u'词账三条') + u' 全平 ⇎ autojunk 无差 ' + V(u'blk_autojunk_diff', None, u'autojunk差')
    + u'; 9293 段内编号 ' + V(u'blk_tag_n', None, u'段内编号') + u' 枚吃 ' + V(u'blk_tag_chars', None, u'段内编号字符')
    + u' 字符; 整块作子串读不通 ' + V(u'blk_is_substring', None, u'整块子串') + u'。 '
    + u'节位由块首行上方最近的编号标题现读: 1122 §' + F[u'ov_sec'][0] + u' ⇎ 9293 §' + F[u'ov_sec'][1]
    + u'(题面逐字同词 ⇎ 两串编号无一对应), 块末行之后第一个编号标题正是截断串所指的那一节(§' + F[u'ov_next_sec'][0]
    + u' ⇎ §' + F[u'ov_next_sec'][1] + u'), 两窗因越界而真被截断的 ' + V(u'ov_cut_n', None, u'截断触发块数')
    + u' 扇(即窗本身就收在本节内)。 '
    + u'发射遍由字面针重开这两扇窗(端点由 4 行滑窗找 ⇎ 本遍用 find 现取, 截断照同一根 stop 串): 行 ' + JT(u'ov2_rows', u'本遍段行')
    + u' ⇎ 壳 ' + JT(u'ov2_shell', u'本遍段壳') + u' ⇎ 句 ' + JT(u'ov2_sents', u'本遍段句') + u' ⇎ 字符 ' + JT(u'ov2_chars', u'本遍段字符')
    + u' ⇎ 三档同句 ' + V(u'ov2_same_raw', None, u'本遍逐字同') + u'/' + V(u'ov2_same_tag', None, u'本遍剥编号同') + u'/'
    + V(u'ov2_same_canon', None, u'本遍归拼同') + u' ⇎ 新句 ' + V(u'ov2_new', None, u'本遍新句') + u', 与建条侧逐格差 '
    + JT(u'ov2_rows_close', u'段行两遍差') + u' ⇎ 句 ' + JT(u'ov2_sents_close', u'段句两遍差') + u' ⇎ 壳 '
    + JT(u'ov2_shell_close', u'段壳两遍差') + u' ⇎ 同句三档 ' + JO(u'ov2_same_close', u'同句三档差') + u' ⇎ '
    + V(u'ov2_new_close', None, u'新句两遍差') + u' 全平 ⇎ 整块子串同样读不通 ' + V(u'ov2_sub', None, u'本遍整块子串') + u'。 '
    + u'七枚新句逐枚定位回 9293 面: 首行 ' + JL(u'os_first_row', u'新句首行') + u' ⇎ 跨行 ' + JL(u'os_rows', u'新句跨行')
    + u' ⇎ 长度 ' + JL(u'os_len', u'新句长度') + u' ⇎ 定位到 ' + V(u'os_located', None, u'新句定位') + u'/' + V(u'os_n', None, u'新句枚数')
    + u' 枚 ⇎ 前缀多解 ' + V(u'os_ambig', None, u'新句多解') + u' 枚 ⇎ 窗内带编号 ' + V(u'os_tag_in_window', None, u'新句内编号')
    + u' 枚。 逗号也换了: “closed state and return”(不带牛津逗号)在 793 ' + V(u'oxford_old', 0, u'旧逗号793')
    + u' ⇎ 在 9293 ' + V(u'oxford_old', 1, u'旧逗号9293') + u' 枚; 带逗号的 “closed state, and return” 793 '
    + V(u'oxford_new', 0, u'新逗号793') + u' ⇎ 9293 ' + V(u'oxford_new', 1, u'新逗号9293')
    + u' —— ' + QA(0, u'closed state, and return') + u' ⇎ ' + QA(2, u'closed state, and return') + u'。')

LINES.append(
    u'🔁 793 的事件表条目在 9293 被逐字重印: 该句在面上 ' + J(u'ev_n', u'事件表枚数') + u' 枚 ⇎ 读得到的份 '
    + J(u'ev_same', u'事件表同句') + u'; 共现针 ' + V(u'rp_n', None, u'共现针数') + u' 式 ⇎ 他份命中 ' + V(u'rp_others', None, u'共现他份')
    + u' 枚 ⇎ 落点 ' + EXPR(len(F[u'rp_other_src']), u"len(%s('rp_other_src'))" % FN, u'共现落点') + u' 份('
    + JL(u'rp_other_src', u'共现落点名') + u') ⇎ 9293 复印 ' + V(u'rp_reprint_9293', None, u'9293复印') + u' 枚, 逐格矩阵 '
    + JL(u'rp_mat', u'共现矩阵') + u'。 发射遍在本遍摘壳面上重数: 逐格差 ' + V(u'rp2_close', None, u'共现两遍差') + u' ⇎ 他份 '
    + V(u'rp2_others', None, u'本遍共现他份') + u' ⇎ 复印 ' + V(u'rp2_reprint', None, u'本遍复印') + u' ⇎ 落点名单与建条同 '
    + EXPR(len(F[u'rp2_other_src']), u"len(%s('rp2_other_src'))" % FN, u'共现落点数') + u' 份 ⇎ 两遍名单差 '
    + EXPR(len([x for x in F[u'rp2_other_src'] if x not in F[u'rp_other_src']]),
           u"len([x for x in %s('rp2_other_src') if x not in %s('rp_other_src')])" % (FN, FN), u'落点两遍差') + u'。 锚: '
    + AQ(0, EV) + u' ⇎ ' + AQ(2, EV) + u'。 反过来, 独占针 ' + V(u'neg_n', None, u'反向针数') + u' 式 ⇎ '
    + V(u'neg_probes', None, u'反向探针') + u' 次探针: 在自己那份读得到 ' + V(u'neg_self', None, u'反向有主') + u'/'
    + V(u'neg_n', None, u'反向针数') + u' ⇎ 在被排除的那几份上命中 ' + V(u'neg_others', None, u'反向他份') + u' 枚 ⇎ 一枚全冷的也没有 '
    + EXPR(len(F[u'neg_cold']), u"len(%s('neg_cold'))" % FN, u'全冷反向') + u'; 本遍用游标 find 环在本遍自导的摘壳面上重数: 他份 '
    + V(u'ng2_others', None, u'本遍反向他份') + u' ⇎ 逐格差 ' + V(u'ng2_close', None, u'反向两遍差') + u' ⇎ 本份合计 '
    + V(u'ng2_self', None, u'本遍反向本份') + u'/' + V(u'neg_self_tot', None, u'建条反向本份') + u'。 同一格上有多解的三式 '
    + JL(u'neg_multi', u'反向多解') + u' 式 ⇎ 本遍同判 ' + JL(u'ng2_multi', u'本遍反向多解') + u' 式(名单差 '
    + V(u'ng2_multi_close', None, u'多解两遍差') + u'), 本份枚数逐式 ' + JL(u'ng2_multi_cnt', u'多解枚数') + u'——'
    + u'多解只影响给哪一行挂锚, 不影响门槛读数。 例: ' + QM(u'the present global default is five minutes') + u' ⇎ '
    + QM(u'set r2 to') + u' ⇎ ' + QM(u'would retransmit n times before killing the connection') + u'。')

LINES.append(
    u'🐧 ip-sysctl 把答案交回内核参数表: 键行 ' + V(u'kn2_keys', None, u'键行本遍') + u'/' + V(u'lin_keys_total', None, u'键行建条')
    + u' 行 ⇎ 去重名 ' + V(u'kn2_uniq', None, u'去重本遍') + u'/' + V(u'lin_keys_uniq', None, u'去重建条') + u' 个 ⇎ 重名 '
    + EXPR(len(F[u'kn2_dups']), u"len(%s('kn2_dups'))" % FN, u'重名种数') + u' 个: ' + JL(u'kn2_dups', u'重名清单')
    + u'(同一份文档里两次登记同名键, 账 ' + V(u'lin_key_dup_ledger', None, u'重名账') + u' 平)。 相关键两把名尺: 名 ⇎ 正文双判 '
    + EXPR(len(F[u'kn2_rel']), u"len(%s('kn2_rel'))" % FN, u'双判键数') + u' 枚 ⇎ 只按名 '
    + EXPR(len(F[u'kn2_pick']), u"len(%s('kn2_pick'))" % FN, u'单判键数') + u' 枚 ⇎ 并集 ' + V(u'kn2_union', None, u'两尺并集')
    + u' ⇎ 两两交集 ' + V(u'lin_rel_both', None, u'两尺交') + u' ⇎ 容斥账 ' + V(u'kn2_ie_close', None, u'容斥账') + u' ⇎ 名单同集 '
    + V(u'kn2_rel_close', None, u'双判两遍差') + u'/' + V(u'kn2_pick_close', None, u'单判两遍差') + u'; 双判落选的六枚 '
    + JL(u'lin_rel_dropped', u'落选键') + u'(名字带 retries/timeout 而正文不谈重传)。 键正文行合计 '
    + V(u'kn2_body_rows', None, u'键正文行') + u'/' + V(u'lin_body_lines', None, u'键正文行建条') + u' 行。 '
    + u'默认句式四档(Default: ⇎ default value is ⇎ default value of ⇎ 借参考句) ' + J(u'kn2_shape_n', u'句式档') + u' ⇎ 读不到值 '
    + V(u'kn2_none', None, u'无默认值') + u'/' + V(u'lin_dv_none', None, u'无默认值建条') + u' 枚 ⇎ 十六进制 '
    + JL(u'kn2_hex', u'十六进制') + u' ⇎ 带句点尾 ' + V(u'lin_val_punct', None, u'带尾点') + u' 处 ⇎ 数值面 '
    + JL(u'kn2_numvals', u'默认值数值面') + u'。 四式级联逐键与量测段同值(不同者 ' + EXPR(len(F[u'kn2_dv_diff']), u"len(%s('kn2_dv_diff'))" % FN, u'默认值分歧')
    + u' 空) ⇎ 句式档同数(差 ' + J(u'kn2_shape_close', u'句式档两遍差') + u')。 四个直接答这题的键: tcp_retries1='
    + V(u'lin_default_str', 0, u'retries1') + u' ⇎ tcp_retries2=' + V(u'lin_default_str', 1, u'retries2') + u' ⇎ syn='
    + V(u'lin_default_str', 2, u'syn') + u' ⇎ synack=' + V(u'lin_default_str', 3, u'synack') + u'(锚 '
    + QA(4, u'tcp_retries2 - integer') + u' ⇎ ' + QA(4, u'a value of at least 8') + u')。 三枚键的默认值逐行读不到 ⇎ 整块才读得到 '
    + JL(u'kn2_wrap_gain', u'换行丢值键') + u'(两遍同名单 ' + V(u'kn2_wrap_close', None, u'换行丢值两遍差') + u')。')

LINES.append(
    u'✖ 内核那份给的不是一枚数而是一条等式: “N 次重传, 初始 RTO = TCP_RTO_MIN” ⇒ 末次重传发生在 Σ2^k ⇎ 杀死连接要到 2^(N+1)−1。 '
    + u'syn_retries=' + CM(u'eq2_rows', 0, 1, u'syn N') + u' ⇒ 末次 ' + CM(u'eq2_rows', 0, 2, u'syn 末次')
    + u' ⇎ 杀死 ' + CM(u'eq2_rows', 0, 3, u'syn 杀死') + u' 秒; synack_retries=' + CM(u'eq2_rows', 1, 1, u'synack N')
    + u' ⇒ 末次 ' + CM(u'eq2_rows', 1, 2, u'synack 末次') + u' ⇎ 杀死 ' + CM(u'eq2_rows', 1, 3, u'synack 杀死')
    + u' 秒(面上文书自己印的两个数 ' + CM(u'eq2_rows', 0, 4, u'syn 印一') + u'/' + CM(u'eq2_rows', 0, 5, u'syn 印二')
    + u' ⇎ ' + CM(u'eq2_rows', 1, 4, u'synack 印一') + u'/' + CM(u'eq2_rows', 1, 5, u'synack 印二') + u' 与复算同值)。 三轨求和同值(幂清单求和 ⇎ 逐次累加 ⇎ 闭式): 差 '
    + JL(u'eq2_ruler_gap', u'三轨差') + u' ⇎ 与面上印出的秒数逐格对上 ' + JL(u'eq2_close', u'等式对印出') + u'. '
    + u'印出的粘连秒数 ' + JO(u'eq2_printed', u'印出三式') + u' 枚(' + JL(u'eq_printed_all', u'印出样本') + u'), 与建条侧差 '
    + JO(u'eq2_printed_close', u'印出两遍差') + u'。 面上三枚 RTO 参数由字符扫描器现取(而非正则分组): rto_min='
    + V(u'eq2_rto_face', 0, u'rto_min') + u' ⇎ rto_max=' + V(u'eq2_rto_face', 1, u'rto_max') + u' ⇎ rto_initial='
    + V(u'eq2_rto_face', 2, u'rto_initial') + u'(与建条 ' + JL(u'eq_rto_face', u'建条RTO') + u' 同值, 差 '
    + JO(u'eq2_rto_close', u'RTO两遍差') + u'; 建条侧另有 ' + V(u'eq_rto_min_ms', None, u'rto最小毫秒') + u' 毫秒一档)。 '
    + u'“多久达到 100 秒”的最小 N: 末次口径 ' + V(u'eq2_min_last', None, u'最小N末次') + u' ⇎ 杀死口径 ' + V(u'eq2_min_kill', None, u'最小N杀死')
    + u' ⇎ 文书自己写 “at least ' + V(u'eq2_doc_says', None, u'文书说N') + u'” ⇎ 差 末次 ' + JO(u'eq2_off_by', u'文书口径差')
    + u'(建条侧 ' + JO(u'eq_off_by', u'建条口径差') + u' 同数)——文书给的 8 比按等式复算的 7 多一枚, 因为文档把 “杀死” 与 “末次” 混在一句里。')

LINES.append(
    u'🚫 “924.6 秒”这一枚印在 ip-sysctl 的 tcp_retries2 条目里(面上 ' + V(u'eq2_9246_n', None, u'本遍924.6枚') + u'/'
    + V(u'eq_9246_printed', None, u'建条924.6枚') + u' 枚 ⇎ 逐份 ' + J(u'eq9246_by_src', u'924.6逐份') + u'), '
    + u'单位由数后八码位现验(' + V(u'eq2_9246_unit', None, u'924.6带秒') + u' 枚紧跟 seconds)。 它不可由面上的参数复算出来: '
    + u'五枚候选(2^N−1 ⇎ 2^(N+1)−1 ⇎ N·rto ⇎ 线性段 ⇎ N=15 闭式) ' + J(u'eq2_cand', u'本遍候选') + u' 与 924.6 逐格差 '
    + J(u'eq2_cand_close', u'候选两遍差') + u' 全平 ⇎ 命中 ' + V(u'eq2_hit', None, u'候选命中') + u' ⇎ 建条侧差 '
    + V(u'eq2_hit_close', None, u'命中两遍差') + u' ⇎ 与 924.6 的偏离 ' + J(u'eq2_dev', u'候选偏离') + u' 秒。 '
    + u'所以这一枚只能登记成“文书印出的数”(锚 ' + QA(4, u'924.6') + u' ⇎ ' + AQ(4, u'The default value of 15 yields a hypothetical timeout of 924.6 seconds')
    + u'), 不进任何门槛等式——它的算法不在这份文档里。')

LINES.append(
    u'🪟 段窗是发射遍新增的一档(量测段没有): ' + EXPR(len(PINS), u"len(%s('pb_rows'))" % FN, u'段窗枚数')
    + u' 扇窗, 窗界一律由字面针在摘壳折平面上现取偏移、经逐字符行表映回原行, 窗文本再由行区间切片重折(保形档 ⇎ 摘壳档两把)。 行 '
    + PJ(u'pb_rows', u'窗行') + u' 合计 ' + V(u'pb_rows_tot', None, u'窗行合计') + u' ⇎ 五份主答句窗 ' + V(u'pb_five_rows', None, u'五窗行')
    + u' 行 ⇎ 词 ' + PJ(u'pb_words', u'窗词') + u' 合计 ' + V(u'pb_words_tot', None, u'窗词合计') + u' ⇎ 字符 '
    + PJ(u'pb_chars', u'窗字符') + u' 合计 ' + V(u'pb_chars_tot', None, u'窗字符合计') + u' ⇎ 不同词 ' + PJ(u'pb_vocab', u'窗词汇')
    + u' ⇎ 单行成窗 ' + V(u'pb_one_line', None, u'单行窗') + u' 扇。 每扇交两端共 ' + V(u'sr_n', None, u'端点探针') + u' 枚端点回原文件自验('
    + EXPR(len(PINS), u"len(%s('pb_rows'))" % FN, u'段窗枚数复算') + u'×2): 整串就在那一行读通 ' + V(u'sr_whole', None, u'端点整串') + u' ⇎ '
    + u'被换行推到下一行 ' + V(u'sr_cut', None, u'端点切开') + u' ⇎ 所报行号对得上 ' + V(u'sr_rows_close', None, u'端点行号账') + u'。 '
    + u'五份答句各自落在本份某一扇窗内: 窗号 ' + J(u'pb_ans_win', u'答句所在窗') + u' ⇎ 可选窗 ' + J(u'pb_ans_n', u'答句窗候选')
    + u' ⇎ 落空 ' + V(u'pb_ans_close', None, u'答句窗落空') + u' 份。 窗内语气词逐 token 拆字母段读(量测段那把查布尔表读左右邻): '
    + u'MUST ' + PJ(u'pb_tone_must', u'窗MUST') + u' ⇎ SHOULD ' + PJ(u'pb_tone_should', u'窗SHOULD') + u' ⇎ MAY '
    + PJ(u'pb_tone_may', u'窗MAY') + u' ⇎ MUST NOT ' + PJ(u'pb_tone_mustnot', u'窗MUSTNOT') + u' ⇎ 编号 '
    + PJ(u'pb_tone_tag', u'窗编号') + u', 与整串正则尺同数 ' + V(u'pb_tone_close', None, u'窗语气词账') + u'/'
    + V(u'pb_phrase_close', None, u'窗短语账') + u'; 9293 主答句窗与 1122 讨论窗的编号枚数对整份登记值的差 '
    + JT(u'pb_tag_block_close', u'窗编号差') + u' 归零(窗内 ' + V(u'pb_tone_tag', 3, u'9293窗编号') + u' = 段内 '
    + V(u'blk_tag_n', None, u'段内编号') + u' ⇎ 全文 ' + V(u'tag_dash', 1, u'1122编号全文') + u'/' + V(u'tag_dash', 2, u'9293编号全文') + u')。')

LINES.append(
    u'🧭 “RFC 1122 recommends …” 这一式只在 9293 与 ip-sysctl 两份印出(份数 ' + V(u'kw2_docs', None, u'模板段份数') + u'/'
    + V(u'kw_docs', None, u'模板段份数建条') + u', 标志尺逐份判在面 ' + J(u'kw_present', u'模板段在面') + u'(合计 '
    + EXPR(sum(F[u'kw_present']), u"sum(%s('kw_present'))" % FN, u'模板段标志和') + u' 份 ⇎ 与偏移尺同判): 折平面偏移 '
    + J(u'kw2_head', u'模板段偏移') + u' ⇎ 摘壳面偏移 ' + J(u'kw2_head_sh', u'模板段摘壳偏移') + u', 两档差 '
    + V(u'kw2_close', None, u'模板段两档差') + u' 与建条侧同值; -1 是口径不存在, 不是零命中。 配对 ' + V(u'kw2_pair_n', None, u'模板段配对')
    + u'/' + V(u'kw_pair_n', None, u'模板段配对建条') + u' 对, 二百码位窗逐字相同 ' + JL(u'kw2_same', u'模板段同窗') + u' 对(建条 '
    + JL(u'kw_same', u'模板段同窗建条') + u' ⇎ 差 ' + V(u'kw2_same_close', None, u'模板段同窗两遍差') + u') —— 同一句推荐在两份文书里被抄成'
    + u'各自的措辞, 不是复制粘贴。 锚 ' + QM(u'rfc 1122 recommends at least 100 seconds') + u' ⇎ ' + QM(u'rfc 1122 recommends at least 3 retransmissions') + u'。 '
    + u'6298 那份把 RTO 上限写成 ' + AQ(3, ANSK[3]) + u', 它既不给出次数也不给出放弃时刻, 只把下限钉在 '
    + C(u'dur', 3, 3, u'六十秒6298') + u' 枚 “60 seconds” 上。')

LINES.append(
    u'🧮 闭合账: 布尔门 建条遍 ' + V(u'bool_all_n', None, u'建条门') + u' 道全绿(' + V(u'bool_green', None, u'建条绿')
    + u') ⇎ 发射遍 ' + V(u'bool2_all', None, u'本遍门') + u' 道全绿(' + V(u'bool2_green', None, u'本遍绿') + u', 红 '
    + V(u'bool2_red_count', None, u'本遍红数') + u' 道红)⇎ 合计 ' + EXPR(F[u'bool_all_n'] + F[u'bool2_all'],
                                                                   u"%s('bool_all_n')+%s('bool2_all')" % (FN, FN), u'门合计')
    + u' 道, 每道都能红; 恒等式 建条 ' + V(u'zid_scan_n', None, u'建条恒等式') + u' + 本遍 ' + V(u'zid_scan2_n', None, u'本遍恒等式')
    + u' = ' + EXPR(F[u'zid_scan_n'] + F[u'zid_scan2_n'],
                    u"%s('zid_scan_n')+%s('zid_scan2_n')" % (FN, FN), u'恒等式合计') + u' 条全平, 每条都减掉了真量。 '
    + u'与采集遍逐键对账 ' + V(u'pick_agree', None, u'对账符') + u' 键符 ⇎ ' + V(u'pick_diff', None, u'对账不符') + u' 键不符('
    + JL(u'pick_diffk', u'不符清单') + u' 空清单)。 本遍新登记键 ' + V(u'scan2_key_n', None, u'本遍键数')
    + u' 枚(口径: 进本遍时先快照 F 的键名集, 在落账自计数键之前取差集, 所以另有 '
    + V(u'scan2_self_n', None, u'自计数键') + u' 枚自计数键不计)⇎ 建条遍 '
    + V(u'scan2_src_n', None, u'建条遍快照键数') + u' 枚(含它自己那枚 scan_key_n ⇎ 与建条遍的自计数读法 '
    + V(u'scan_key_n', None, u'建条遍自计数') + u' 差 1), 两遍合计 '
    + EXPR(F[u'scan2_src_n'] + F[u'scan2_key_n'],
           u"%s('scan2_src_n')+%s('scan2_key_n')" % (FN, FN), u'两遍键合计')
    + u' 枚 ⇎ 单靠前缀尺会把建条遍的 ' + JL(u'scan2_prefixed_old', u'前缀多捞')
    + u' 这 ' + str(len(F[u'scan2_prefixed_old'])) + u' 枚也算作本遍键(多捞清单 ⇎ 本遍键漏前缀清单 '
    + JL(u'scan2_unprefixed', u'漏前缀') + u' 空)。 判词针 ' + V(u'needle_n', None, u'针总数') + u' 枚 × 五份 = '
    + V(u'role_probes', None, u'针探针数') + u' 格四档读数, 反向针 ' + V(u'neg_n', None, u'反向针数') + u' 枚 × 五份 = '
    + V(u'neg_probes', None, u'反向探针') + u' 格。 谱系: ' + J(u'ff', u'换页枚') + u' 换页符只在 RFC 侧四份 ⇎ 页壳行 '
    + SUM5(u'shell_lines', u'壳行合计', u'壳行五份和') + u' 行 ⇎ 剥壳正文 ' + SUM5(u'body_lines', u'正文行合计', u'正文五份和')
    + u' 行——同一问题的五份答法换代不换题: 793 说 “five minutes” ⇎ 1122 给 R1/R2 两阈值 ⇎ 9293 照登并给义务词编号 ⇎ '
    + u'6298 只钉 RTO 下限 ⇎ 内核给参数与等式。')

# --- 段三 BEGIN --- (自 replay 恒等式 → 复核锚归属 → 落盘 flat/deriv/atoms/checks 与条目文件)
BADZID = []
for v, w in Z2:
    got = eval(v, {FN: BB86})
    if got != 0:
        BADZID.append((v, w, got))
assert not BADZID, BADZID[:3]
for v, w in Z2:
    reg(u'0', v, w)

body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCHS = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCHS)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦(' + u'|'.join(TAGS) + u')⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
MISSLINE = [x for x in CITES
            if x[1] not in ANSET[IDX[x[0]]] and pnorm(x[1]) not in ROWSRAW[IDX[x[0]]]]
assert not ATOMFAIL, ATOMFAIL[:3]
if not PROBE:
    assert not ERR, ERR[:3]
    assert not MISSLINE, MISSLINE[:3]
AMB = [x for x in ALOG if x[3] > 1]
if PROBE:
    for x in sorted(set(BADREAD)):
        print(u'  读数针落空: %s %s[%s] %s' % x)
    for x in sorted(set(BLKFAIL)):
        print(u'  段针落空: %s %s @%s' % (x[0], x[2], x[1]))
    for x in sorted(set(ATOMFAIL)):
        print(u'  锚针落空: %s %s' % x)
    print(u'探针汇总: 读数 %d ⇎ 段针 %d ⇎ 锚针 %d ｜ 正文 %d 字符 ｜ 多行可读针 %d' % (
        len(BADREAD), len(BLKFAIL), len(ATOMFAIL), len(body), len(AMB)))
    for x in AMB:
        print(u'  针多解: %s 针=%s 首行=%d 候选=%d 全针=%s' % (x[0], x[1], x[2], x[3], x[4][:70]))
    for t in sorted(set([x[0] for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]])):
        print(u'  归属待核: %s' % t)
    raise SystemExit(0)
HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCHS)
CLS = {u'single': len([a for a in ANCHS if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCHS if 1 < len(HITC[a]) < NSRC]),
       u'all5': len([a for a in ANCHS if len(HITC[a]) == NSRC])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'], u'anchor_all5': CLS[u'all5'],
         u'checks': DIST * NSRC, u'enc_chars': len(body.replace(NL, u'')), u'nsrc': NSRC}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all5'] == DIST
F.update(AMETA)
for n, v in sorted(AMETA.items()):
    reg(str(v), u"%s('%s')" % (FN, n), n)


def _walk(v, path):
    if isinstance(v, list):
        for i, x in enumerate(v):
            for it in _walk(x, path + (i,)):
                yield it
    elif isinstance(v, int) and not isinstance(v, bool):
        yield v, path


def _expr(k, path):
    head = u"%s('%s'%s)" % (FN, k, (u', ' + repr(path[0])) if path else u'')
    return head + u''.join(u'[%d]' % i for i in path[1:])


ELEMS = {}
for kk, vv in F.items():
    for num, pp in _walk(vv, ()):
        if num >= 100:
            ELEMS.setdefault(str(num), []).append(_expr(kk, pp))
SRC_HARD = set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', u''.join(T)))
BODY_HARD = sorted(set(m.group(0).rstrip(u'.') for m in re.finditer(u'\\d[\\d.]*', body)
                       if len(m.group(0).rstrip(u'.')) >= 3), key=lambda x: (len(x), x))
NOEXPR = []
for s in BODY_HARD:
    if s in K_ or s in SRC_HARD:
        continue
    got = [e for e in ELEMS.get(s, []) if eval(e, {FN: BB86}) == int(s)]
    if not got:
        NOEXPR.append(s)
        continue
    for e in got[:2]:
        reg(s, e, u'列表元素·' + s)
assert not NOEXPR, [(x, body[max(0, body.index(x) - 90):body.index(x) + 30]) for x in NOEXPR[:3]]
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K_.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv86.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
F['contract_n'] = len(F) + 1
json.dump(F, io.open(u'corpus/_b86flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms86.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCHS, key=len, reverse=True)) + NL)

CH = dict(AMETA)
CH.update({u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCHS))),
           u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
           u'classes': dict((c, sorted([a for a in ANCHS if len(HITC[a]) == n]))
                            for c, n in ((u'single', 1), (u'cross', 2), (u'three', 3), (u'four', 4), (u'five', 5))),
           u'collisions': dict((k, v) for k, v in COLL.items()),
           u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
           u'deriv_points': sum(len(v) for v in SEENX.values()), u'notes': NOTES,
           u'anchor_ambiguous': len(AMB), u'anchor_lines': [[x[0], x[1], x[2], x[3]] for x in ALOG],
           u'needle_n': F[u'needle_n'], u'needles': [z[:60] for z in NEEDLES],
           u'neg': [[z[0], z[1][:60], z[2], z[3], z[4]] for z in NEGEX],
           u'rp': [[z[0], z[1][:60], z[2], z[5]] for z in RPEX],
           u'gates_scan': [[nm, 1 if v else 0] for nm, v in G],
           u'gates_emit': [[nm, 1 if v else 0] for nm, v in EG2],
           u'zid': [[v, w] for v, w in ZV], u'zid2': [[v, w] for v, w in Z2],
           u'litk': LITK,
           u'blk': [[PLBL[t], LBL[PB[t][0]], PB[t][3], PB[t][4], PB[t][6], PB[t][7], PB[t][5][:70]]
                    for t in range(len(PINS))],
           u'pins': [[LBL[i], s, e] for i, s, e in PINS],
           u'scut': [[LBL[SC[t][1]], NEEDLES[SC[t][0]][:44], SC[t][2], SC[t][3], SC[t][4], SC[t][5]]
                     for t in range(len(SC)) if SC[t][3]],
           u'tdgain': [[LBL[TC[t][1]], NEEDLES[TC[t][0]][:44], TC[t][2], TC[t][5]]
                       for t in range(len(TC)) if TC[t][2] > TC[t][5]],
           u'straddle': [[LBL[i], ST_UP[i][t][0], ST_UP[i][t][2], ST_UP[i][t][3][-38:], ST_UP[i][t][4][:38]]
                         for i in range(NSRC) for t in range(len(ST_UP[i]))]
           + [[LBL[i], ST_LO[i][t][0], ST_LO[i][t][2], ST_LO[i][t][3][-38:], ST_LO[i][t][4][:38]]
              for i in range(NSRC) for t in range(len(ST_LO[i]))],
           u'os': [[OSROW[t][0], OSROW[t][1], OSROW[t][2], OSROW[t][3], len(OVLNEW[t]),
                    OVLNEW[t][:60]] for t in range(len(OVLNEW))],
           u'numunit_wrap': F[u'numunit_wrap'], u'glued': F[u'glued_all'],
           u'lin_dv': F[u'kn2_dv'], u'lin_rel': F[u'kn2_rel'], u'lin_dropped': F[u'lin_rel_dropped'],
           u'eq': [[str(x) for x in z] for z in F[u'eq2_rows']], u'eq_cand': [str(x) for x in F[u'eq2_cand']],
           u'kw_head': F[u'kw2_head'], u'kw_head_sh': F[u'kw2_head_sh'],
           u'closure_keys': sorted([k for k in F if u'close' in k or u'ledger' in k]),
           u'flat': F})
json.dump(CH, io.open(u'corpus/_b86checks.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

ANS5 = [u'翻倍重传到超时即止: 只给“不超五分钟”的默认上限, 一次也不数',
        u'立 R1 ⇎ R2 两阈值: 到 R1 考虑放弃(至少 3 次), 到 R2 必须关(至少 100 秒)',
        u'照登 1122 两句并给义务词编号, 又许 R2 设成无穷把取舍交给应用',
        u'不谈次数: 只钉 RTO 的下限(最大 RTO 可设, 但不得低于 60 秒)',
        u'交给内核参数与等式: retries1=3 ⇎ retries2=15, 面上另印“924.6 秒”']
ENTRY = u'corpus/babeltele/B86_retransmission_limit_five_answers.md'
srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 码位／原行 %d／非空行 %d／最长行 %d 列／换页 %d 枚／壳行 %d／答法: %s)' % (
        PATH[i].split('/')[-1], F[u'bytes'][i], F[u'cp'][i], F[u'splitlines'][i], F[u'nonblank'][i],
        F[u'maxlen'][i], F[u'ff'][i], F[u'shell_lines'][i], ANS5[i]) for i in range(NSRC))
    + u' (四份 RFC Editor 纯文本 ⇎ 一份内核文档: 回车 ' + str(sum(F[u'n_cr'])) + u' 枚 ⇎ 换页 '
    + str(sum(F[u'ff'])) + u' 枚只在 RFC 侧四份 ⇎ 制表符 ' + str(sum(F[u'tab']))
    + u' 枚只在 ip-sysctl ⇎ BOM ' + str(sum(F[u'bom'])) + u' 枚 ⇎ 非 ASCII ' + str(sum(F[u'na_total']))
    + u' 枚全在 9293; 五份都是 72 列硬换行(内核那份最长 ' + str(max(F[u'maxlen'])) + u' 列)。 '
    + str(F[u'needle_n']) + u' 枚判词针 × 五份 = ' + str(F[u'role_probes']) + u' 格四档读数 ⇎ 反向 '
    + str(F[u'neg_n']) + u' 式 ' + str(F[u'neg_probes']) + u' 次探针 ⇎ 段窗 ' + str(len(PINS))
    + u' 扇 ⇎ 五份答句 ' + str(sum(F[u'ans2_span'])) + u' 行, 全部由面上位置导出, 一个都不手填。 '
    + u'RFC Editor 的现行状态页与勘误页(9293 那两句 MUST 有没有被 errata 改过、1122 的 R1/R2 是否又被更新)、'
    + u'现网内核装机值(sysctl 里 tcp_retries2 此刻实际是多少)、Linux 版本间该文档的措辞改动, '
    + u'都不可由在库文件判定, 只进解读注, 不进门槛)\n')
link = (u"；联结不是“同一份数据的两种序列化”, 而是“重传几次、多久之后该放弃”在五份一手文书里的五种答法: "
        u"793 只写“the present global default is five minutes”(时长十式在它面上 " + str(F['dur_by_doc'][0])
        + u" 枚 ⇎ 带单位数值项 " + str(F['numval_n'][0]) + u" 项, 一次数也不给); "
        u"⇎ 1122 把放弃拆成两阈值 R1 ⇎ R2(“at least” " + str(F['spell'][1][GRP.index(u'at least')]) + u" 枚 ⇎ 100 seconds "
        + str(F['dur'][1][2]) + u" 枚), 并规定到 R2 就 close the connection; "
        u"⇎ 9293 逐字照登同一 procedure 并给义务词缀上编号(编号族 " + str(F['tag_dash'][2])
        + u" 枚 ⇎ 只在它一份), 又添一句把 R2 设成 “infinity”; "
        u"⇎ 6298 只管计时: 次数一字不提, 只把 RTO 上限的下限钉在 60 秒(带单位数值 " + str(F['numval_n'][3])
        + u" 项); ⇎ ip-sysctl 把答案写成内核参数与等式(tcp_retries2 默认 " + F['lin_default_str'][1]
        + u" ⇎ 面上印 924.6 秒 " + str(F['eq2_9246_n']) + u" 枚而五枚候选算法都对不上它, 差 "
        + str(round(min([abs(x - 924.6) for x in F['eq2_cand']]), 1)) + u" 秒)。 三条换代同时可见: 义务词是否编号("
        + u'⇎'.join(str(x) for x in F['tag_dash']) + u")⇎ 是否给次数(" + u'⇎'.join(str(len(x)) for x in F['numtimes'])
        + u")⇎ 判词在四档面上的读法(28 枚针逐份合计: 行 "
        + u'⇎'.join(str(x) for x in F['role_line_n']) + u" ⇎ 折 "
        + u'⇎'.join(str(x) for x in F['role_fold_n']) + u" ⇎ 去编号 "
        + u'⇎'.join(str(x) for x in F['role_tag_n']) + u" 枚)。\n")
tags = (u'五答: 793 五分钟默认上限(%d 词跨 %d 行) ⇎ 1122 R1/R2 两阈值(%d 词跨 %d 行) ⇎ '
        u'9293 照登+编号+无穷选项(%d 词跨 %d 行, 编号族 %d 枚) ⇎ 6298 只钉 RTO 下限(%d 词跨 %d 行) ⇎ '
        u'ip-sysctl 参数表(%d 词跨 %d 行, 键 %d 个) '
        u'四档口径(逐份): 行 %s ⇎ 折 %s ⇎ 摘壳 %s ⇎ 去编号 %s 枚, 换行切开 %d ⇎ 壳切 %d ⇎ 编号切 %d '
        u'切开针跨行枚数合计 %d ⇎ 最长跨 %d 行 ⇎ 三档自相减=行内尺(差 %d) '
        u'跨行义务词现拼 大写 %d ⇎ 小写 %d 对(词种 %s ⇎ 与量测段逐份差 %d) '
        u'反向 %d 枚针 %d 次探针: 被排除份上 %d 枚 ⇎ 本份 %d/%d 式 ⇎ 全冷 %d 式 '
        u'段窗 %d 扇 %d 行 ⇎ 端点自验 %d/%d ⇎ 窗内语气词 MUST %d ⇎ SHOULD %d ⇎ 编号 %d '
        u'1122⇎9293 同段对照: 行 %d⇎%d ⇎ 句 %d⇎%d ⇎ 逐字同 %d ⇎ 去编号同 %d ⇎ 归拼同 %d ⇎ 新句 %d '
        u'内核: 键行 %d ⇎ 去重 %d ⇎ 双判 %d 枚 ⇎ 句式档逐份 %s ⇎ 读不到值 %d ⇎ 换行丢值 %d 键 '
        u'等式: syn %d 次⇒末次 %d ⇎ 杀死 %d 秒 ⇎ 100 秒的最小 N %d/%d ⇎ 文书说 %d '
        u'924.6 秒: 候选 %d 枚 ⇎ 命中 %d ⇎ 最小差 %s 秒 '
        u'闭合账 布尔门 %d+%d ⇎ 恒等式 %d+%d ⇎ 对账 %d 键符 %d 不符 ⇎ 锚 %d 处去重 %d '
        u'谱系: 793→1122→9293 三份 TCP 文书的语形族合计 %d 枚(%d 式)⇎ 6298 只管计时 ⇎ 内核交参数与等式\n'
        % (F[u'ans_words'][0], F[u'ans_sent_span'][0], F[u'ans_words'][1], F[u'ans_sent_span'][1],
           F[u'ans_words'][2], F[u'ans_sent_span'][2], F[u'tag_dash'][2],
           F[u'ans_words'][3], F[u'ans_sent_span'][3], F[u'ans_words'][4], F[u'ans_sent_span'][4], F[u'kn2_uniq'],
           u'⇎'.join(str(x) for x in F[u'role_line_n']), u'⇎'.join(str(x) for x in F[u'role_fold_n']),
           u'⇎'.join(str(x) for x in F[u'role_sh_n']), u'⇎'.join(str(x) for x in F[u'role_tag_n']),
           F[u'wrap_cut_n'], len(F[u'shell_cut']), len(F[u'tag_cut']),
           F[u'sc_span_tot'], F[u'sc_max_span'], F[u'sc_line_close'],
           sum(F[u'st_up']), sum(F[u'st_low']), u'⇎'.join(F[u'st_words']), sum(F[u'st_by_doc']),
           F[u'neg_n'], F[u'neg_probes'], F[u'neg_others'], F[u'neg_self'], F[u'neg_n'], len(F[u'neg_cold']),
           len(PINS), F[u'pb_rows_tot'], F[u'sr_n'], F[u'sr_whole'],
           sum(F[u'pb_tone_must']), sum(F[u'pb_tone_should']), sum(F[u'pb_tone_tag']),
           F[u'ovl_rows'][0], F[u'ovl_rows'][1], F[u'ovl_s1'], F[u'ovl_s2'],
           F[u'ovl_same_raw'], F[u'ovl_same_tag'], F[u'ovl_same_canon'], F[u'ovl_new'],
           F[u'kn2_keys'], F[u'kn2_uniq'], len(F[u'kn2_rel']),
           u'⇎'.join(str(x) for x in F[u'kn2_shape_n']), F[u'kn2_none'],
           len(F[u'kn2_wrap_gain']),
           F[u'eq2_rows'][0][1], F[u'eq2_rows'][0][2], F[u'eq2_rows'][0][3], F[u'eq2_min_last'], F[u'eq2_min_kill'],
           F[u'eq2_doc_says'],
           len(F[u'eq2_cand']), F[u'eq2_hit'], str(round(min([abs(x - 924.6) for x in F['eq2_cand']]), 1)),
           F[u'bool_all_n'], F[u'bool2_all'], F[u'zid_scan_n'], F[u'zid_scan2_n'],
           F[u'pick_agree'], F[u'pick_diff'], USED, DIST,
           sum([sum(F[u'spell'][i]) for i in range(3)]), len(GRP), ))
title = (u'# B86 重传几次、多久之后该放弃，五份一手文书五种答法：'
         u'793 只给“五分钟”的默认上限（时长式 %d 枚 ⇎ 带单位数值 %d 项，一次数也不给） ⇎ '
         u'1122 立 R1 ⇎ R2 两阈值（“at least” %d 枚 ⇎ 到 R2 必须关） ⇎ '
         u'9293 照登同一 procedure 并给义务词缀 %d 枚编号（另许 R2 为无穷） ⇎ '
         u'6298 只钉 RTO 下限（“60 seconds” %d 枚 ⇎ 不提次数） ⇎ '
         u'ip-sysctl 交回内核参数（tcp_retries2=%s ⇎ 面上印 “924.6 秒” %d 枚 ⇎ 五枚候选算法复算全不中，最小差 %s 秒）'
         u'（判词在四档面可读 %s ⇎ 换行切开 %d 枚 ⇎ 编号切开 %d 枚；'
         u'1122 ⇎ 9293 同段逐字同 %d 句 ⇎ 去编号同 %d ⇎ 归拼同 %d ⇎ 新句 %d）\n') % (
             F[u'dur_by_doc'][0], F[u'numval_n'][0], F[u'spell'][1][GRP.index(u'at least')], F[u'tag_dash'][2],
             F[u'dur'][3][3], F[u'lin_default_str'][1], F[u'eq2_9246_n'],
             str(round(min([abs(x - 924.6) for x in F['eq2_cand']]), 1)),
             u'⇎'.join(str(x) for x in F[u'role_tag_n']), F[u'wrap_cut_n'], len(F[u'tag_cut']),
             F[u'ovl_same_raw'], F[u'ovl_same_tag'], F[u'ovl_same_canon'], F[u'ovl_new'])
text = (title + srcline + link + tags +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n'
        + u'## ⟪BabelTele⟫\n' + body + u'\n\n'
        + u'## ⛓解读注\n\n（此段由 corpus/_fill86.py 从 corpus/_b86checks.json 与 corpus/_deriv86.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s ｜ 归属错配 %d ⇎ 非锚面线 %d ｜ 多行可读针 %d' % (
    USED, DIST, TAGN, len(ERR), len(MISSLINE), len(AMB)))
for x in AMB[:20]:
    print(u'  针多解: %s 针=%s 首行=%d 候选=%d' % (x[0], x[1], x[2], x[3]))
print(u'一源 %d ⇎ 二至四源 %d ⇎ 五源 %d ｜ 段窗 %d 行合计 %d ⇎ 端点 %d(整 %d ⇎ 切 %d) ⇎ 单行窗 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all5'], len(PINS), F['pb_rows_tot'],
    F['sr_n'], F['sr_whole'], F['sr_cut'], F['pb_one_line']))
print(u'切开 %d 枚(换行 %d ⇎ 壳 %d ⇎ 编号 %d) ⇎ 跨行合计 %d ⇎ 反向他份 %d ⇎ 本份 %d ⇎ 义务词跨行 %d 对' % (
    F['wrap_cut_n'] + len(F['shell_cut']) + len(F['tag_cut']), F['wrap_cut_n'], len(F['shell_cut']),
    len(F['tag_cut']), F['sc_span_tot'], F['ng2_others'], F['ng2_self'], sum(F['st_up']) + sum(F['st_low'])))
print(u'1122⇎9293 段 行 %d⇎%d ⇎ 句 %d⇎%d ⇎ 同 %d/%d/%d ⇎ 新句 %d ⇎ 定位 %d/%d ⇎ 内核 键 %d 去重 %d 正文行 %d' % (
    F['ov2_rows'][0], F['ov2_rows'][1], F['ov2_sents'][0], F['ov2_sents'][1],
    F['ov2_same_raw'], F['ov2_same_tag'], F['ov2_same_canon'], F['ov2_new'],
    F['os_located'], F['os_n'], F['kn2_keys'], F['kn2_uniq'], F['kn2_body_rows']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ⇎ 恒等式 %d ⇎ 扁平键 %d' % (
    len(DERIV), sum(len(v) for v in SEENX.values()), len(COLL), len(ZERO), len(ZV), len(F)))
print(u'判定 %s' % (dict((k, v) for k, v in CLOSE2.items() if v == 0),))
# --- 段三 END ---

