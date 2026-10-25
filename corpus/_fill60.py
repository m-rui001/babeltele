# -*- coding: utf-8 -*-
"""B60 ⛓解读注(第四遍): 本注每个数都是现测并 assert 的, 不手填。
四套实现: 采集侧 corpus/_pick60.py(str.count 逐字面数词面 + 正则数形状, 网页那份量在壳层不剥壳)
⇎ 建条目侧 corpus/_mkB60.py(三条 re.sub 剥壳得断面 + 三元组谓词 + 整篇窗口折空白, 扁平契约 corpus/_b60flat.json)
⇎ 门槛侧 corpus/audit.py::_b60_scan()(由 corpus/_wire60.py 从 SCAN 段机械抽出, 插门前把 231 个扁平键与
164 条 DERIV 算式在抽出体上逐条预演) ⇎ 本注第四遍。
本注的读法与前三遍都不同: ①剥壳用一条手写逐字符状态机(注释整段跳过、标签整段跳过并补一个空格、五枚实体手工换),
与建条目侧的三条正则同果而不同路;
②上限句与术语折行都不用 \\s+ 正则: 动词与 have a/Validity/Period/greater/than/数字/days 逐词连排,
词间空白的原文整段记下, 全为单格的算严档、含换行或多格的算宽松档, 两档之差就是 ceil_wrap ⇎ vp_wrap;
③壳⇎面两口径在本注里由“整份字符串逐字面 count, 壳与面各数一次再求差”现推, 不切窗口;
④整行搬运的行集在本注按“逐字符过滤 alnum 后小写”归一(建条目侧用 re.sub, 采集侧用列表推导);
⑤强度词分“历史时间表行 ⇎ 其余正文”两半: 表行靠逐字符查行首是否形如 YYYY-MM-DD 或文中有 SC+数字,
词数靠字符边界手工扫, 不用正则(建条目侧两条正则相加)。
不可由在库文件判定的只写在本注: 五份文件的抓取时刻与磁盘 mtime 谁新谁旧、cabforum.org 此刻挂的是哪一版、
LE 页 “Last updated” 那一行的真伪、47 天所本的那份“industry rules”出自哪份文书、90 天是否已在所有 CA 生效。
"""
import io, os, re, sys, json

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = os.path.join(C, 'babeltele', 'B60_certificate_validity_five_answers.md')
FLAT = json.load(io.open(C + u'/_b60flat.json', encoding=u'utf-8'))
MEAS = json.load(io.open(C + u'/_b60meas.json', encoding=u'utf-8'))
CH = json.load(io.open(C + u'/_b60checks.json', encoding=u'utf-8'))
ATOMS = [x for x in io.open(os.path.join(C, u'_atoms60.txt'), encoding=u'utf-8').read().split(NL) if x.strip()]
PATH = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt',
        u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.layout.txt',
        u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt',
        u'corpus/raw/cert/le_lifetimes.html',
        u'corpus/raw/cert/rfc5280.txt']
PDFS = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.pdf',
        u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.pdf',
        u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.pdf']
RAWS = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.raw.txt',
        u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.raw.txt',
        u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.raw.txt']
TAGS = [u'T', u'O', u'F', u'N', u'R']
LBL = dict(zip(TAGS, [u'旧基准', u'中基准', u'新基准', u'CA 说明', u'X.509 规范']))
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
SRC = [RD(p) for p in PATH]

VERBS = (u'MUST NOT', u'MUST', u'SHOULD NOT', u'SHOULD')


def detag44(s):
    """本注的剥壳(与建条目侧的四步正则同定义而不同路): script/style 整段连同结束标签丢弃,
    注释整段丢弃且不留空格, 其余标签整段丢弃并补一个空格, 五枚实体手工换, 行内连续的空格/制表折成一格, 换行保留。"""
    out, k, n = [], 0, len(s)
    low = s.lower()
    while k < n:
        if s[k] != u'<':
            out.append(s[k])
            k += 1
            continue
        if s.startswith(u'<!--', k):
            e = s.find(u'-->', k)
            k = n if e < 0 else e + 3
            continue
        e = s.find(u'>', k)
        if e < 0:
            break
        nm = low[k + 1:e].lstrip(u'/ \t')
        if (nm.startswith(u'script') or nm.startswith(u'style')) and low[k + 1] != u'/':
            close = u'</' + (u'script' if nm.startswith(u'script') else u'style')
            j = low.find(close, e)
            if j < 0:
                break
            g = low.find(u'>', j)
            k = n if g < 0 else g + 1
            continue
        out.append(u' ')
        k = e + 1
    t = u''.join(out)
    for a, b in ((u'&#39;', "'"), (u'&#43;', '+'), (u'&amp;', '&'), (u'&rsquo;', u'’'), (u'&copy;', u'©')):
        t = t.replace(a, b)
    o, i = [], 0
    while i < len(t):
        c = t[i]
        if c in u' \t':
            o.append(u' ')
            while i + 1 < len(t) and t[i + 1] in u' \t':
                i += 1
        else:
            o.append(c)
        i += 1
    return u''.join(o).strip()


FACE = [SRC[i] if i != 3 else detag44(SRC[3]).strip() for i in range(5)]
FLINES = [f.split(NL) for f in FACE]


def norm44(s):
    o = []
    for ch in s.lower():
        if (ch.isalnum() and ord(ch) < 128):
            o.append(ch)
    return u''.join(o)


# ①上限句 ⇎ ②术语折行: 本注不写 \s+ 正则, 改为逐词找字面、把词间空白整段记下;
#   全为单个空格的即建条目侧"单空格档", 含换行或多空格的即折行档, 两档之差就是 vp_wrap / ceil_wrap。
def ws_seg(t, j):
    k = j
    while k < len(t) and t[k].isspace():
        k += 1
    return k, t[j:k]


def loose(t, seq, ci=False):
    """seq 的各词须以 >=1 个空白相隔地连排出现; 返回 [(起点, [词间空白原文])]。"""
    low = t.lower() if ci else t
    first = seq[0].lower() if ci else seq[0]
    out, i = [], 0
    while True:
        j = low.find(first, i)
        if j < 0:
            return out
        pos, seps, k = j + len(first), [], 1
        for w in seq[1:]:
            p, g = ws_seg(low, pos)
            if not g or not low.startswith(w.lower() if ci else w, p):
                break
            seps.append(g)
            pos = p + len(w)
            k += 1
        if k == len(seq):
            out.append((j, seps))
            i = pos
        else:
            i = j + 1


SEQ6 = (u'have', u'a', u'Validity', u'Period', u'greater', u'than')
ORD = (u'MUST NOT', u'SHOULD NOT', u'MUST', u'SHOULD')


def ceil44(t):
    tri, occ, one, nl = set(), 0, 0, 0
    for i in range(len(t)):
        if t[i] not in u'MS':
            continue
        v = [x for x in ORD if t.startswith(x, i)]
        if not v:
            continue
        pos, seps = i + len(v[0]), []
        ok = True
        for w in SEQ6:
            p, g = ws_seg(t, pos)
            if not g or not t.startswith(w, p):
                ok = False
                break
            seps.append(g)
            pos = p + len(w)
        if not ok:
            continue
        p, g = ws_seg(t, pos)
        if not g:
            continue
        seps.append(g)
        b = p
        while b < len(t) and (t[b].isdigit() or t[b] == u','):
            b += 1
        if b == p:
            continue
        p2, g2 = ws_seg(t, b)
        if not g2 or not t.startswith(u'days', p2):
            continue
        seps.append(g2)
        occ += 1
        if all(x == u' ' for x in seps):
            one += 1
        if any(NL in x for x in seps):
            nl += 1
        tri.add((v[0], t[p:b].replace(u',', u'')))
    return sorted(tri), occ, one, nl


TRI = [ceil44(SRC[i]) for i in range(5)]
assert [x[0] for x in TRI] == [[(u'MUST NOT', u'398'), (u'MUST NOT', u'825'), (u'SHOULD NOT', u'397')],
                               [(u'MUST NOT', u'398'), (u'MUST NOT', u'825'), (u'SHOULD NOT', u'397')],
                               [(u'MUST NOT', u'398'), (u'SHOULD NOT', u'397')], [], []], TRI
assert [x[1] for x in TRI] == FLAT[u'ceil_n'], ([x[1] for x in TRI], FLAT[u'ceil_n'])
assert [x[2] for x in TRI] == FLAT[u'ceil_strict_n'], ([x[2] for x in TRI], FLAT[u'ceil_strict_n'])
assert [x[1] - x[2] for x in TRI] == FLAT[u'ceil_wrap']
assert [list(map(list, x)) for x in FLAT[u'ceil_tri']] == [list(map(list, t[0])) for t in TRI]

VP = [loose(SRC[i], [u'validity', u'period'], ci=True) for i in range(5)]
VPC = [len(VP[i]) for i in range(5)]
VPO = [len([1 for _j, sp in VP[i] if all(x == u' ' for x in sp)]) for i in range(5)]
VPL = [len([1 for _j, sp in VP[i] if any(NL in x for x in sp)]) for i in range(5)]
assert VPC == FLAT[u'vp_flex_ci'], (VPC, FLAT[u'vp_flex_ci'])
assert VPO == FLAT[u'vp_ci'], (VPO, FLAT[u'vp_ci'])
assert [a - b for a, b in zip(VPC, VPO)] == FLAT[u'vp_wrap'], (FLAT[u'vp_wrap'], FLAT[u'vp_ci'], FLAT[u'vp_caps'])

# ③壳⇎面: 同一句在壳里与在面上各数一遍(建条目侧按窗口切, 本注直接用整份 str.count 之差)
SENT = [(u's90', u'certificates with 90-day lifetimes'), (u's6', u'Short-lived certificates with 6-day lifetimes'),
        (u's47', u'maximum of 47 days starting on March 15, 2029'), (u's45', u'45 days by February 2028')]


def numday44(t, flex=False):
    """天数写法逐字符扫: 数字串(可含逗号)后紧跟一格分隔(' ' 或 '-', 宽松档再放行换行/制表)再跟 day/days 且后面不是字母数字。"""
    out, k, n = [], 0, len(t)
    while k < n:
        if not t[k].isdigit():
            k += 1
            continue
        b = k + 1
        while b < n and (t[b].isdigit() or t[b] == u','):
            b += 1
        sep = t[b] if b < n else u''
        ok = bool(sep) and ((sep in u' -') if not flex else (sep.isspace() or sep == u'-'))
        if b < n and ok and t[b + 1:b + 5] == u'days' and not (b + 5 < n and t[b + 5].isalnum()):
            out.append(t[k:b].replace(u',', u''))
            k = b + 5
            continue
        if b < n and ok and t[b + 1:b + 4] == u'day' and not (b + 4 < n and t[b + 4].isalnum()):
            out.append(t[k:b].replace(u',', u''))
            k = b + 4
            continue
        k = b
    return out


def meta_args(t):
    """每枚 <meta …> 标签里 content="…" 的引数原样取出(逐字符找标签边界与引号, 不用正则)。"""
    out, k, low = [], 0, t.lower()
    while True:
        j = low.find(u'<meta', k)
        if j < 0:
            return out
        e = t.find(u'>', j)
        if e < 0:
            return out
        q = t.find(u'content="', j, e)
        if q >= 0:
            a = q + 10
            z = t.find(u'"', a, e + 200)
            if z > a:
                out.append(t[a:z])
        k = e + 1


SH = []
FA = []
for _nm, s in SENT:
    sh = SRC[3].lower().count(s.lower())
    fa = FACE[3].lower().count(s.lower())
    SH.append(sh)
    FA.append(fa)
assert SH == [FLAT[u'shell_s90'], FLAT[u'shell_s6'], FLAT[u'shell_s47'], FLAT[u'shell_s45']]
assert FA == [FLAT[u'face_s90'], FLAT[u'face_s6'], FLAT[u'face_s47'], FLAT[u'face_s45']]
assert [b - a for a, b in zip(FA, SH)] == [2, 2, 2, 2]
DAY_SH = len(numday44(SRC[3]))
DAY_FA = len(numday44(FACE[3]))
MD = sorted([len(numday44(x)) for x in meta_args(SRC[3])], reverse=True)
assert MD[:2] == [FLAT[u'day_meta'], FLAT[u'day_meta']], MD
assert DAY_SH - DAY_FA == 2 * FLAT[u'day_meta'] == FLAT[u'day_shell'] - FLAT[u'day_face']
assert DAY_SH == FLAT[u'day_shell'] and DAY_FA == FLAT[u'day_face']
assert [len(numday44(FACE[i])) for i in range(5)] == FLAT[u'day_num']
assert [len(numday44(FACE[i], flex=True)) - len(numday44(FACE[i])) for i in range(5)] == FLAT[u'day_wrap']

# ④整行搬运: 行集归一后用另一套过滤(本注逐字符滤 alnum, 建条目侧 re.sub)
LS = [set(norm44(l) for l in FLINES[i] if len(l.strip()) >= 25 and norm44(l)) for i in range(5)]
assert len(LS[0] & LS[1]) == FLAT[u'share_TO']
assert len(LS[1] & LS[2]) == FLAT[u'share_OF']
assert len(LS[0] & LS[2]) == FLAT[u'share_TF']
assert len(LS[0] & LS[1] & LS[2]) == FLAT[u'share_TOF']
assert len(LS[0] | LS[1] | LS[2]) == FLAT[u'union_TOF']
assert len(LS[0] & LS[4]) == FLAT[u'share_TR'] and len(LS[2] & LS[4]) == FLAT[u'share_FR']
assert len(LS[3] & (LS[0] | LS[1] | LS[2] | LS[4])) == FLAT[u'share_N_any'] == 0

# ⑤天数值域与 45/47 在 BR 里的缺席
DS = [sorted(set(numday44(FACE[i])), key=int) for i in range(5)]
assert DS == FLAT[u'day_set'], (DS, FLAT[u'day_set'])
assert [x for x in DS[2] if x not in DS[0] and x not in DS[1]] == FLAT[u'set_only_F']
assert sorted(set(DS[3]) - set(sum([DS[i] for i in range(3)], [])), key=int) == FLAT[u'set_only_N']
assert sorted(set(DS[2]) & set(DS[3]), key=int) == FLAT[u'set_shared_NF']
assert sum(DS[i].count(u'45') for i in range(3)) == FLAT[u'num_45_in_brs'] == 0
assert sum(DS[i].count(u'47') for i in range(3)) == FLAT[u'num_47_in_brs'] == 0

# ⑥强度词的“历史时间表行 ⇎ 其余正文”: 本注按行手工分类并按字符边界数词(建条目侧用两条正则)
def is_hist(l):
    k = 0
    while k < len(l) and l[k].isspace():
        k += 1
    head = l[k:k + 10]
    if (len(head) == 10 and head[0:4].isdigit() and head[4] == u'-'
            and head[5:7].isdigit() and head[7] == u'-' and head[8:10].isdigit()):
        return True
    j = l.find(u'SC')
    while j >= 0:
        if j + 2 < len(l) and l[j + 2].isdigit() and (j == 0 or not (l[j - 1].isalnum() or l[j - 1] == u'_')):
            return True
        j = l.find(u'SC', j + 1)
    return False


def tok(s, word):
    n, k = 0, 0
    while True:
        j = s.find(word, k)
        if j < 0:
            return n
        a = s[j - 1] if j else u' '
        b = s[j + len(word)] if j + len(word) < len(s) else u' '
        if not (a.isalnum() or a == u'_') and not (b.isalnum() or b == u'_'):
            n += 1
        k = j + 1


HM, BM, HS, BS, HN = [], [], [], [], []
for i in range(5):
    ls = FLINES[i]
    h = [l for l in ls if is_hist(l)]
    r = [l for l in ls if not is_hist(l)]
    HN.append(len(h))
    HM.append(sum(tok(l, u'MUST') for l in h))
    BM.append(sum(tok(l, u'MUST') for l in r))
    HS.append(sum(tok(l.lower(), u'shall') for l in h))
    BS.append(sum(tok(l.lower(), u'shall') for l in r))
assert HN == FLAT[u'hist_n'], (HN, FLAT[u'hist_n'])
assert HM == FLAT[u'h_must'] and BM == FLAT[u'b_must']
assert HS == FLAT[u'h_shall'] and BS == FLAT[u'b_shall']
assert [HM[i] + BM[i] - FLAT[u'kw_must'][i] for i in range(5)] == FLAT[u'h_must_close']
assert [HS[i] + BS[i] - FLAT[u'shall_ci'][i] for i in range(5)] == FLAT[u'h_shall_close']

# ⑦三个面的分页符闭合
FF = [SRC[i].count(u'\x0c') for i in range(3)]
assert FF == FLAT[u'formfeed'][:3] == FLAT[u'raw_formfeed']
assert [len(FACE[i]) - len(RD(RAWS[i])) for i in range(3)] == FLAT[u'face_gap']
assert [len(FLINES[i]) - len(RD(RAWS[i]).split(NL)) for i in range(3)] == FLAT[u'line_gap']
assert [os.path.getsize(PDFS[i]) for i in range(3)] == FLAT[u'pdf_bytes']

# ⑧锚归属: 由条目正文现推, 五源一律按本注的面(第④遍)判成员
TT = io.open(ENTRY, encoding='utf-8').read()
enc = re.search(u'⟪BabelTele⟫' + NL + u'(.*?)' + NL + NL + u'## ', TT, re.S).group(1)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
FAN4 = [norm44(f) for f in FACE]
IDX = dict((t, i) for i, t in enumerate(TAGS))
ERR4 = [x for x in CITES if norm44(x[1]) not in FAN4[IDX[x[0]]]]
assert not ERR4, ERR4[:3]
assert len(CITES) == FLAT[u'anchor_total'] == CH[u'anchor_total']
assert len(set(a for _t, a in CITES)) == FLAT[u'anchor_distinct']
assert sum(len(re.findall(u'⟦%s⟧' % t, enc)) for t in TAGS) == len(CITES)

# ⑨采集侧与建条目侧的对账在四份纯文本面上做(网页两份量在不同层)
PL = tuple(MEAS.pop(u'_plain_idx', [0, 1, 2, 4]))
BAD4 = []
for k in sorted(MEAS):
    if k not in FLAT:
        continue
    v = [FLAT[k][i] for i in PL] if isinstance(FLAT[k], list) and len(FLAT[k]) == 5 else FLAT[k]
    if v != MEAS[k]:
        BAD4.append(k)
assert not BAD4, BAD4[:6]

L = []
A = L.append
A(u'### 第四遍复测(本注现算, 与前三遍不同路)')
A(u'')
A(u'| 量 | 本注的写法 | 结果 | 与建条目侧 |')
A(u'|---|---|---|---|')
A(u'| 上限三元组 | 动词后六词“have a/Validity/Period/greater/than”加数字加 days 逐词连排, 词间空白整段记下 | '
  u'T={0} ⇎ O={0} ⇎ F={1} ⇎ N 空 ⇎ R 空 | 逐字一致 |'.format(
     u'/'.join(u'%s·%s' % x for x in TRI[0][0]), u'/'.join(u'%s·%s' % x for x in TRI[2][0])))
A(u'| 上限句的两档命中 | 同一连排: 空白全为单格记严档, 含换行或多格记宽松档 | 宽松 %s ⇎ 单空格 %s ⇎ 差 %s(其中含换行 %s) '
  u'| 与 ceil_n ⇎ ceil_strict_n ⇎ ceil_wrap 一致 |'
  % (u'⇎'.join(str(x[1]) for x in TRI), u'⇎'.join(str(x[2]) for x in TRI),
     u'⇎'.join(str(x[1] - x[2]) for x in TRI), u'⇎'.join(str(x[3]) for x in TRI)))
A(u'| Validity 与 Period 的接缝 | validity/period 两词忽略大小写连排, 空白整段记下后分档 | 宽松 %s ⇎ 单空格 %s ⇎ 差 %s'
  u'(含换行 %s) | 与 vp_flex_ci ⇎ vp_ci ⇎ vp_wrap 一致 |'
  % (u'⇎'.join(str(x) for x in VPC), u'⇎'.join(str(x) for x in VPO),
     u'⇎'.join(str(a - b) for a, b in zip(VPC, VPO)), u'⇎'.join(str(x) for x in VPL)))
A(u'| 同一句的壳内⇎面内 | 整份字面 count 在壳与面各数一遍再求差 | %s ⇎ %s, 每句恰差 2 份 | 与 shell/face 一致 |'
  % (u'⇎'.join(str(x) for x in SH), u'⇎'.join(str(x) for x in FA)))
A(u'| 天数在壳⇎面 | 数字串+分隔符+day(s) 逐字符扫, 壳与面各扫一遍; meta 的 content 引数按标签边界手工取出 | '
  u'壳 %d ⇎ 面 %d ⇎ 两枚描述 meta 各 %d 个, 差恰为 2×%d | 闭合 0 |'
  % (DAY_SH, DAY_FA, FLAT[u'day_meta'], FLAT[u'day_meta']))
A(u'| 三代整行共用 | 行集归一改成逐字符滤 alnum(建条目侧用 re.sub) | T∩O %d ⇎ O∩F %d ⇎ T∩F %d ⇎ 三代同现 %d ⇎ 并集 %d | 逐字一致 |'
  % (len(LS[0] & LS[1]), len(LS[1] & LS[2]), len(LS[0] & LS[2]), len(LS[0] & LS[1] & LS[2]), len(LS[0] | LS[1] | LS[2])))
A(u'| BR 与 RFC 5280 | 同上 | T∩R %d ⇎ F∩R %d ⇎ N 与其余四份 %d | 逐字一致 |'
  % (len(LS[0] & LS[4]), len(LS[2] & LS[4]), len(LS[3] & (LS[0] | LS[1] | LS[2] | LS[4]))))
A(u'| 天数值域 | 各份现切集合再求差 | 新基准独有 %s ⇎ CA 说明独有 %s ⇎ 两份共有 %s | 逐字一致 |'
  % (u','.join(x for x in DS[2] if x not in DS[0] and x not in DS[1]),
     u','.join(sorted(set(DS[3]) - set(sum([DS[i] for i in range(3)], [])), key=int)),
     u','.join(sorted(set(DS[2]) & set(DS[3]), key=int))))
A(u'| 45 与 47 作天数 | 三份基准的天数值域里查这两个值在不在 | 两份皆 %d⇎%d 处 | 逐字一致 |'
  % (FLAT[u'num_45_in_brs'], FLAT[u'num_47_in_brs']))
A(u'| 三个面 | 分页符逐个数、字符与行数用另一份面做差 | \\f %s(两面同数, 差 %s) ⇎ layout 比 raw 多字符 %s ⇎ 多行 %s ⇎ PDF 原字节 %s | 逐字一致 |'
  % (u'⇎'.join(str(x) for x in FF), u'⇎'.join(str(x) for x in FLAT[u'ff_close']),
     u'⇎'.join(str(x) for x in FLAT[u'face_gap']), u'⇎'.join(str(x) for x in FLAT[u'line_gap']),
     u'⇎'.join(str(x) for x in FLAT[u'pdf_bytes'])))
A(u'| 强度词分两半 | 表行按逐字符查行首 10 位形如 YYYY-MM-DD 或文中有 SC+数字(建条目侧是一条正则); 词数按字符边界手工扫 | '
  u'表行 MUST %s ⇎ 正文 MUST %s ⇎ 表行行 %s 行 | 与 h_must/b_must/hist_n 一致 |'
  % (u'⇎'.join(str(x) for x in HM), u'⇎'.join(str(x) for x in BM), u'⇎'.join(str(x) for x in HN)))
A(u'| 锚归属 | 由条目正文 ⟦标签⟧⟨引文⟩ 配对现推, 成员判据用本注的面 | %d 处／去重 %d 串／错配 %d | 与建条目侧、门槛侧同 |'
  % (len(CITES), len(set(a for _t, a in CITES)), len(ERR4)))
A(u'| 两侧对账 | 采集侧 53 键在四份纯文本面上比 | 共有 %d ／ 不符 %d | 网页那份两边量在不同层, 不入表 |'
  % (len(MEAS), len(BAD4)))
A(u'')
A(u'### 读法')
A(u'')
A(u'一、门槛的数只在 ⟦T⟧⟦O⟧ 的上限句里是禁令: 三元组 {0} 在旧代与中代逐字同现, 到新代只剩 {1}——'
  u'“825 还在不在禁令里”按三元组宾语判(旧 {2} ⇎ 中 {3} ⇎ 新 {4} 处), “825 这个词还在不在文书里”按整句窗口分档判'
  u'(上限 {5} ⇎ 复用 {6} ⇎ §1.6 条目名 {7} ⇎ 其他 {8}, 三代各自相加等于露面处数 {9})。{10}。'
  .format(u'/'.join(u'%s·%s' % x for x in TRI[0][0]), u'/'.join(u'%s·%s' % x for x in TRI[2][0]),
          FLAT[u'd825_ceil'][0], FLAT[u'd825_ceil'][1], FLAT[u'd825_ceil'][2],
          FLAT[u'validwin_825'][0], FLAT[u'reusewin_825'][0], FLAT[u'titlewin_825'][0],
          FLAT[u'otherwin_825'][0], FLAT[u'lines_825'][0],
          u'中代那句被排版折在两行之间, 所以单空格档只撞到 %d 处、容换行档 %d 处' % (FLAT[u'd825_strict'][1], FLAT[u'd825_ceil'][1])))
A(u'二、术语四套叫法是同一条禁令的四种载体: 大写 Validity Period {0}⇎{1}⇎{2}⇎{3}⇎{4} 处 ⇎ 小写 {5} ⇎ 忽略大小写 {6} ⇎ '
  u'词根 validity 全族 {7}(去掉两词组还剩 {8} 处是 validityDate 与 OCSP 语境) ⇎ lifetime {9} ⇎ notBefore/notAfter {10}⇎{11}。'
  .format(*FLAT[u'vp_caps'], FLAT[u'vp_low'], FLAT[u'vp_ci'], FLAT[u'validity_stem'], FLAT[u'vp_stem_gap'],
          FLAT[u'lifetime_ci'], FLAT[u'notbefore'], FLAT[u'notafter']))
A(u'三、强度词的分布要分两半读: 全大写 MUST 家族 {0}⇎{1}⇎{2}⇎{3}⇎{4} 处, 其中落在 §1.6 历史时间表行里的只有 '
  u'{5}⇎{6}⇎{7}⇎{8}⇎{9} 处, 正文那一半 {10}⇎{11}⇎{12}⇎{13}⇎{14} 处, 两半相加与全量对平(闭合 {15}⇎{16}⇎{17})。'
  .format(FLAT[u'kw_upper'][0], FLAT[u'kw_upper'][1], FLAT[u'kw_upper'][2], FLAT[u'kw_upper'][3], FLAT[u'kw_upper'][4],
          *FLAT[u'h_must'], *FLAT[u'b_must'],
          u'⇎'.join(str(x) for x in FLAT[u'h_must_close']), u'⇎'.join(str(x) for x in FLAT[u'h_shall_close']),
          u'⇎'.join(str(x) for x in FLAT[u'h_sub_close'])))
A(u'四、X.509 那一份不参与“多久”的争论: 带数的天数 {0} 处、上限句 {1} 条、大写 Validity Period {2} 处, 全部为零; '
  u'它只管时刻怎么写——UTCTime {3} 处 ⇎ GeneralizedTime {4} 处, 世纪窗口写到 {5} 年与 {6} 年各 {7}⇎{8} 处。'
  .format(FLAT[u'day_num'][4], FLAT[u'ceil_n'][4], FLAT[u'vp_caps'][4], FLAT[u'ts_utctime'][4],
          FLAT[u'ts_generalizedtime'][4], 2049, 2050, FLAT[u'y2049'][4], FLAT[u'y2050'][4]))
A(u'')
A(u'### 本条不能由在库文件判定的(只登记, 不进门槛)')
A(u'')
A(u'① 五份文件的抓取时刻与磁盘 mtime 谁新谁旧; ② cabforum.org 此刻挂的是哪一版基准要求; '
  u'③ LE 页 “Last updated” 那一行(库内 {0} 处)所指是否真的更新过; '
  u'④ 47 天所本的 “industry rules” 出自哪份文书——库内三份基准要求里 45 与 47 作天数各 {1}⇎{2} 处, 所以那句话在库里没有对照物; '
  u'⑤ 90 天默认是否已在全部 CA 生效。这些只能站外核验, 因此都不进判词与门槛。'
  .format(FLAT[u'last_updated'][3], FLAT[u'num_45_in_brs'], FLAT[u'num_47_in_brs']))
A(u'')
A(u'### 编码与门的账')
A(u'')
A(u'编码区 {0} 字符(不含换行); 锚 {1} 处 ⇎ 去重 {2} 串 ⇎ 归属检查 {3} 次 ⇎ 错配 {4}; '
  u'一源 {5} ⇎ 两至四源 {6} ⇎ 五源 {7}; 标签 T⇎O⇎F⇎N⇎R 各 {8}⇎{9}⇎{10}⇎{11}⇎{12} 处。'
  .format(CH[u'enc_chars'], FLAT[u'anchor_total'], FLAT[u'anchor_distinct'], FLAT[u'checks'], FLAT[u'anchor_err'],
          FLAT[u'anchor_single'], FLAT[u'anchor_cross'], FLAT[u'anchor_all5'],
          FLAT[u'tag_T'], FLAT[u'tag_O'], FLAT[u'tag_F'], FLAT[u'tag_N'], FLAT[u'tag_R']))
A(u'DERIV {0} 键 ⇎ 复算点 {1} 处 ⇎ 同数共键 {2} 组 ⇎ 0 折 {3} 项; 扁平键 {4} 个; '
  u'闭合账 标量 {5} 项(全 0)⇎ 清单 {6} 项; 锚候选池 {7} 条按逐字再现份数分 {8} 档({9}), 分档闭合 {10}。'
  .format(CH[u'deriv_keys'], CH[u'deriv_points'], len(CH[u'collisions']), CH[u'zero_terms'],
          len(FLAT), FLAT[u'scalar_clos_n'], FLAT[u'list_clos_n'], FLAT[u'pool_n'], 5,
          u'⇎'.join(str(x) for x in FLAT[u'pool_tiers']), FLAT[u'pool_close']))
A(u'门槛三遍: T1 字面逐锚回原文 ⇎ T2 DERIV 每条算式重跑 ⇎ T3 码位与字母账; '
  u'本注另加第四遍复测, 上表 13 行全部 assert, 不符即停机。')
NOTE = NL.join(L)
head = TT[:TT.index(u'## ⛓解读注') + len(u'## ⛓解读注')]
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(head + NL + NL + NOTE + NL)
print(u'⛓解读注已写 %d 字符 ｜ 第四遍 assert 全过 ｜ 采集对账 %d 键 0 不符' % (len(NOTE), len(MEAS)))
