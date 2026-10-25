# -*- coding: utf-8 -*-
"""把 B52 的独立复算器(_b52_scan / B52V)接进 audit.py, 并留出 DERIV['B52'] 的生成块位。
幂等: 重复运行先摘旧块再插新块。
_b52_scan 与采集侧 corpus/_pick52.py、建条目侧 corpus/_mkB52.py 各写一遍同一套算法
(组标签机器 ⇎ 三层排序逆序 ⇎ 缩写闭合三口径 ⇎ 四种粒度集合交 ⇎ 检查器字段引用 ⇎ 构建配方跨度 ⇎ 锚归属由正文现推),
两边不符就证明失败。插门之前先把 DERIV['B52'] 的每条表达式在刚写好的扫描器里预演一遍。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = u'corpus/audit.py'
S = io.open(P, encoding='utf-8').read()

BLK = r'''
# B52: 时效表 ⇎ 检查它的 awk ⇎ 造出它真值输入的配方 ⇎ 姊妹表。四份 raw 的行/列/字节口径、91 枚组标签的机器、
# 表自述的三层排序键、缩写闭合的三种口径、四种粒度的逐字复现量、检查器读了哪几列、配方的跨度与生删,
# 以及正文锚的归属, 全部由本函数从四份 raw 与条目正文独立复算; 采集侧 corpus/_pick52.py 与建条目侧 corpus/_mkB52.py 各写一遍,
# 三边不符就证明失败。“从现在起一致”这一谓词不在本函数的能力范围内: 它要的那份 zdump 表在库里 0 份, 本函数只数得出“0 份”。
def _b52_scan():
    import datetime as _dt
    import glob as _gl
    import os as _os
    P4 = SRC['B52']
    N = len(P4)
    TXT = [open(P4[i], encoding='utf-8', errors='replace').read() for i in range(N)]
    TAB = open(u'corpus/raw/tz/zone.tab', encoding='utf-8', errors='replace').read()
    TG = [u'N', u'Z', u'K', u'M']
    NL = chr(10)

    def pn(s):
        s = s.lower().replace(u'’', u"'").replace(u'‘', u"'").replace(u'“', u'"').replace(u'”', u'"')
        s = re.sub(u'[’\'"`´]+', u'', s)
        s = re.sub(u'[\u2010\u2011\u2012\u2013\u2014\u2015\u2212-]', u'-', s)
        s = re.sub(u'[^0-9a-z\u4e00-\u9fff. -]', u' ', s)
        return re.sub(u'\\s+', u' ', s).strip()

    def lns(x):
        return [l.rstrip(u'\r') for l in x.split(NL) if l.strip()]

    L = [lns(TXT[i]) for i in range(N)]
    COM = [[x for x in L[i] if x.startswith(u'#')] for i in range(N)]
    DAT = [[x for x in L[i] if not x.startswith(u'#')] for i in range(N)]
    TL = lns(TAB)
    TD = [x for x in TL if not x.startswith(u'#')]
    d = {}
    for key, f in ((u'bytes', lambda i: _os.path.getsize(P4[i])),
                   (u'chars', lambda i: len(TXT[i])),
                   (u'nonempty', lambda i: len(L[i])),
                   (u'com', lambda i: len(COM[i])),
                   (u'dat', lambda i: len(DAT[i])),
                   (u'tabline', lambda i: sum(1 for x in L[i] if u'\t' in x)),
                   (u'nonascii', lambda i: sum(1 for ch in TXT[i] if ord(ch) > 127))):
        d[key] = [f(i) for i in range(N)]
    for i in range(N):
        assert d[u'nonempty'][i] == d[u'com'][i] + d[u'dat'][i], i

    def fldcount(rows):
        c = {}
        for x in rows:
            n = len(x.split(u'\t'))
            c[n] = c.get(n, 0) + 1
        return c

    d[u'fldn4'] = fldcount(DAT[0])[4]
    d[u'fldz3'] = fldcount(DAT[1])[3]
    d[u'fldz4'] = fldcount(DAT[1])[4]
    d[u'fldt3'] = fldcount(TD)[3]
    d[u'fldt4'] = fldcount(TD)[4]
    d[u'trows'] = d[u'fldt3'] + d[u'fldt4']
    d[u'nowrows'] = d[u'dat'][0]
    d[u'zrows'] = d[u'dat'][1]

    # ---- ⟦N⟧ 组标签机器: 排序键住在注释层 ----
    def parse_tag(line):
        m = re.match(u'^# ([-+]\\d{2}(?::\\d{2})?)(?:/([-+]\\d{2}(?::\\d{2})?))?(.*)$', line)
        if not m:
            return None
        rest = m.group(3)
        ab = u''
        if rest.startswith(u' - '):
            ab = rest[3:]
            ab = u'' if ab.startswith(u'(') else ab.split(u' (')[0]
        return (m.group(1), m.group(2), ab, rest)

    def hh(o):
        s = -1 if o[0] == u'-' else 1
        p = o[1:].split(u':')
        return s * (int(p[0]) + (int(p[1]) / 60.0 if len(p) > 1 else 0))

    GRP, BARE, OTHER = [], 0, 0
    for x in L[0]:
        if x.startswith(u'#'):
            p = parse_tag(x)
            if p:
                GRP.append([x, p[0], p[1], p[2], []])
            elif x.strip() == u'#':
                BARE += 1
            else:
                OTHER += 1
        elif GRP:
            GRP[-1][4].append(x.split(u'\t'))
    assert len(GRP) == sum(len(c[4]) for c in GRP), u'B52: 标签⇎行不再 1:1'
    R0 = [c[4][0] for c in GRP]
    SEQ = [hh(c[1]) for c in GRP]
    SZ = {}
    for c in GRP:
        SZ[len(c[4])] = SZ.get(len(c[4]), 0) + 1
    d[u'tags'] = len(GRP)
    d[u'rows'] = sum(len(c[4]) for c in GRP)
    d[u'grpmax'] = max(SZ)
    d[u'duptag'] = len(GRP) - len(set(c[0] for c in GRP))
    d[u'inv'] = sum(1 for i in range(len(SEQ) - 1) if SEQ[i] > SEQ[i + 1])
    d[u'offfirst'] = int(SEQ[0])
    d[u'offlast'] = int(SEQ[-1])
    OK = {}
    for v in SEQ:
        OK[v] = OK.get(v, 0) + 1
    d[u'offkinds'] = len(OK)
    d[u'repeated'] = len([k for k, v in OK.items() if v > 1])
    d[u'maxperoff'] = max(OK.values())
    d[u'dstg'] = sum(1 for c in GRP if c[2])
    d[u'abg'] = sum(1 for c in GRP if c[3])
    d[u'barehash'] = BARE
    d[u'othercom'] = OTHER
    d[u'offpairkinds'] = len(set((c[1], c[2] or u'') for c in GRP))
    d[u'nonint'] = sum(1 for c in GRP if u':' in c[1] or (c[2] and u':' in c[2]))
    d[u'minutes'] = len(set(int(o.split(u':')[1]) for c in GRP for o in [c[1], c[2] or u''] if u':' in o))
    STEP = {}
    for c in GRP:
        if c[2]:
            k = round(hh(c[2]) - hh(c[1]), 2)
            STEP[k] = STEP.get(k, 0) + 1
    d[u'step1'] = STEP[1.0]
    d[u'stepneg1'] = STEP[-1.0]
    d[u'step05'] = STEP[0.5]
    d[u'step2'] = STEP[2.0]
    d[u'k2inv'] = sum(1 for i in range(len(GRP) - 1)
                      if GRP[i][1] == GRP[i + 1][1] and GRP[i][2] and not GRP[i + 1][2])
    K3 = [(GRP[i][3], GRP[i + 1][3]) for i in range(len(GRP) - 1)
          if GRP[i][1] == GRP[i + 1][1] and (GRP[i][2] or u'') == (GRP[i + 1][2] or u'')
          and GRP[i][3] and GRP[i + 1][3]]
    d[u'k3pairs'] = len(K3)
    d[u'k3inv'] = sum(1 for a, b in K3 if a > b)

    def parens(c):
        return re.findall(u'\\(([^()]*)\\)', c)

    def first_ab(c):
        p = parens(c)
        return p[0] if p else u''

    WITH_TAG = [c for c in GRP if c[3]]
    d[u'withpar'] = sum(1 for c in GRP if parens(c[4][0][3]) and parens(c[4][0][3])[-1])
    d[u'withfirst'] = sum(1 for c in GRP if first_ab(c[4][0][3]))
    d[u'eqfirst'] = sum(1 for c in WITH_TAG if c[3] == first_ab(c[4][0][3]))
    d[u'eqlast'] = sum(1 for c in WITH_TAG if parens(c[4][0][3]) and c[3] == parens(c[4][0][3])[-1])
    d[u'inany'] = sum(1 for c in WITH_TAG if c[3] in parens(c[4][0][3]))
    GAPL = [(c[4][0][2], c[3], parens(c[4][0][3])) for c in WITH_TAG if c[3] not in parens(c[4][0][3])]
    EXPZ = set(c[4][0][2] for c in GRP if u'until' in c[0])
    d[u'gaps'] = len(GAPL)
    d[u'gapnopar'] = sum(1 for g in GAPL if not g[2])
    d[u'gaptense'] = sum(1 for g in GAPL if g[0] in EXPZ)
    d[u'gapspace'] = sum(1 for g in GAPL if g[2] and g[0] not in EXPZ
                         and u''.join(g[1].split()) in [u''.join(p.split()) for p in g[2]])
    assert d[u'gapnopar'] + d[u'gaptense'] + d[u'gapspace'] == d[u'gaps']
    d[u'reverse'] = sum(1 for c in GRP if not c[3] and parens(c[4][0][3]))
    d[u'nparen'] = sum(len(parens(c[4][0][3])) for c in GRP)
    d[u'twopar'] = sum(1 for c in GRP if len(parens(c[4][0][3])) > 1)
    d[u'expire'] = len(EXPZ)

    OFFSHAPE = re.compile(u'(?<![0-9:+-.])[-+]\\d{2}(?::\\d{2})?(?![0-9])')
    d[u'rowoffany'] = sum(1 for f in R0 if any(OFFSHAPE.search(x) for x in f[1:]))
    d[u'rowoffcmt'] = sum(1 for f in R0 if OFFSHAPE.search(f[3]))
    d[u'rowoffzone'] = sum(1 for f in R0 if OFFSHAPE.search(f[2]))

    def latlon(c):
        m = re.match(u'^([-+]\\d+)([-+]\\d+)$', c)
        return (m.group(1)[1:], m.group(2)[1:]) if m else (None, None)

    CW = {}
    for f in R0:
        CW[len(f[1])] = CW.get(len(f[1]), 0) + 1
    d[u'cw11'] = CW[11]
    d[u'cw15'] = CW[15]
    d[u'lead0'] = sum(1 for f in R0 if re.search(u'[-+]0\\d', f[1]))
    d[u'lead0c'] = sum(1 for f in R0 for c in latlon(f[1]) if c and c[0] == u'0')
    d[u'mixed'] = sum(1 for f in R0 if (len(latlon(f[1])[0]) == 4) != (len(latlon(f[1])[1]) == 5))

    C4 = [f[3] for f in R0]
    assert all(C4), u'B52: 第四列出现空值'
    d[u'c4semi'] = sum(1 for x in C4 if u';' in x)
    d[u'c4par'] = sum(1 for x in C4 if u'(' in x)
    d[u'c4both'] = sum(1 for x in C4 if u';' in x and u'(' in x)
    d[u'c4_kind'] = len(set(C4))

    ISO = re.compile(u'\\d{4}-\\d{2}-\\d{2}')
    ISOL = [(x.startswith(u'#'), ISO.search(x).group(0), x) for x in L[0] if ISO.search(x)]
    d[u'iso'] = len(ISOL)
    d[u'isoc'] = sum(1 for x in ISOL if x[0])
    d[u'isod'] = len(ISOL) - d[u'isoc']
    d[u'dateskinds'] = len(set(x[1] for x in ISOL))
    UNT = [x[2] for x in ISOL if u'until' in x[2]]
    d[u'untillines'] = len(UNT)
    BD = [x[2] for x in ISOL if u'Eggert' in x[2]]
    ZD = [ISO.search(x).group(0) for x in L[1] if ISO.search(x)]
    ZB = [x for x in L[1] if u'Eggert' in x]
    D = lambda s: _dt.date(*[int(v) for v in s.split(u'-')])
    U0 = D(ISO.search(UNT[0]).group(0))
    B0 = D(ISO.search(BD[0]).group(0))
    Z0 = D(ISO.search(ZB[0]).group(0))
    d[u'gapday'] = (U0 - B0).days
    d[u'gapbir'] = (Z0 - B0).days
    d[u'bdyear'] = B0.year
    d[u'pred'] = len([x for x in L[0] if u'agree from now on' in x])
    d[u'pred70'] = len([x for x in L[1] if u'agreed since 1970' in x])
    d[u'nowph'] = len([x for x in L[0] if u'now' in x])
    d[u'predyear'] = int(re.search(u'agreed since (\\d{4})', TXT[1]).group(1))

    d[u'col1kind'] = len(set(f[0] for f in R0))
    ZROWS = [x.split(u'\t') for x in DAT[1]]
    Z1 = [f[0] for f in ZROWS]
    d[u'zmulti'] = sum(1 for c in Z1 if u',' in c)
    d[u'zkind'] = len(set(Z1))
    ZS = [c.split(u',')[0] for c in Z1]
    d[u'zinv'] = sum(1 for i in range(len(ZS) - 1) if ZS[i] > ZS[i + 1])
    d[u'z4empty'] = sum(1 for f in ZROWS if len(f) < 4 or not f[3].strip())
    d[u'z4kind'] = len(set(pn(f[3]) for f in ZROWS if len(f) > 3 and f[3].strip()))
    ZN = dict((f[2], f) for f in ZROWS)
    TROWS = [x.split(u'\t') for x in TD]
    EX_NOW = [f[2] for f in R0]
    EX_70 = [f[2] for f in ZROWS]
    EX_TAB = [f[2] for f in TROWS]
    NZ = [f for f in R0 if f[2] in ZN]
    d[u'shared'] = len(NZ)
    d[u'coordeq'] = sum(1 for f in NZ if f[1] == ZN[f[2]][1])
    d[u'cceq'] = sum(1 for f in NZ if f[0] == ZN[f[2]][0])
    d[u'c4eq'] = sum(1 for f in NZ if len(ZN[f[2]]) > 3 and pn(f[3]) == pn(ZN[f[2]][3]))
    d[u'z4has'] = sum(1 for f in NZ if len(ZN[f[2]]) > 3 and ZN[f[2]][3].strip())
    d[u'only70'] = len(set(EX_70) - set(EX_NOW))
    d[u'onlytab'] = len(set(EX_TAB) - set(EX_NOW))
    d[u'dupn'] = len(EX_NOW) - len(set(EX_NOW))
    d[u'dup70'] = len(EX_70) - len(set(EX_70))

    def shingle(ls, n=5):
        w = [t for l in ls for t in re.findall(u'[a-z0-9]+', l.lower())]
        return set(tuple(w[i:i + n]) for i in range(len(w) - n + 1))

    NRAW = [u'\t'.join(f) for f in R0]
    ZRAW = [u'\t'.join(f) for f in ZROWS]
    TRAW = [u'\t'.join(f) for f in TROWS]
    COMT = [x.lstrip(u'#').strip() for x in COM[0]]
    d[u'grainline'] = len(set(pn(x) for x in NRAW) & set(pn(x) for x in ZRAW))
    d[u'graincoord'] = d[u'coordeq']
    d[u'grainzone'] = len(set(EX_NOW) & set(EX_70))
    d[u'grainc4'] = len(set(pn(x) for x in C4)
                       & set(pn(f[3]) for f in ZROWS if len(f) > 3 and f[3].strip()))
    d[u'grainshang'] = len(shingle(NRAW) & shingle(ZRAW))
    d[u'shnt'] = len(shingle(NRAW) & shingle(TRAW))
    d[u'shself'] = len(shingle(NRAW) & shingle(COMT))
    d[u'shn'] = len(shingle(NRAW))
    d[u'shz'] = len(shingle(ZRAW))
    d[u'sht'] = len(shingle(TRAW))
    d[u'sh3n'] = len(shingle(NRAW, 3))
    d[u'sh3c'] = len(shingle(COMT, 3))
    d[u'sh3nc'] = len(shingle(NRAW, 3) & shingle(COMT, 3))
    d[u'sh2nc'] = len(shingle(NRAW, 2) & shingle(COMT, 2))
    d[u'sh3zc'] = len(shingle(ZRAW, 3) & shingle(COMT, 3))

    # ---- ⟦K⟧ 检查器 ----
    KD = NL.join(L[2])
    d[u'klines'] = len(L[2])
    d[u'kcom'] = len([x for x in L[2] if x.startswith(u'#')])
    for n in (u'0', u'1', u'2', u'3', u'4'):
        d[u'kref' + n] = len(re.findall(u'\\$%s(?![0-9])' % n, KD))
    FS = [i + 1 for i, x in enumerate(L[2]) if re.search(u'^\\s*FS = ', x)]
    GT = [i + 1 for i, x in enumerate(L[2]) if u'getline <zdump_table' in x]
    assert len(FS) == 1 and len(GT) == 1 and GT[0] < FS[0], u'B52: 列口径两套的次序变了'
    d[u'kfsline'] = FS[0]
    d[u'kgtline'] = GT[0]
    d[u'kext'] = 3
    d[u'kunset'] = len([v for v in (u'now', u'now_out', u'zdump_table')
                        if not re.search(u'^\\s*%s\\s*=' % v, KD, re.M)])
    PR = re.findall(u'printf "([^"]*)"', KD)
    d[u'kprintf'] = len(PR)
    d[u'kprintfk'] = len(set(PR))
    d[u'kstatus'] = len(re.findall(u'status = 1', KD))
    d[u'kexit'] = len(re.findall(u'exit status', KD))
    d[u'kskip'] = len(re.findall(u'\\[\\^#\\]', KD))
    d[u'kzdumpnow'] = len(re.findall(u'zdump-now', KD))
    d[u'kzonedata'] = len(re.findall(u'zone_data\\[zone\\]', KD))
    d[u'kzonenowd'] = len(re.findall(u'zonenow\\[data\\]', KD))
    d[u'kident'] = len(re.findall(u'identical from now on', KD))
    d[u'knodata'] = len(re.findall(u'no data', KD))

    # ---- ⟦M⟧ 构建器 ----
    BLK2 = TXT[3].split(u'now.ck:', 1)[1].split(u'\ntables.ck:', 1)[0]
    MKPR = re.findall(u'^now\\.ck: (.*)$', TXT[3], re.M)[0].split()
    OKP = [p for p in MKPR if _os.path.exists(u'corpus/raw/tz/' + p)]
    d[u'mprereq'] = len(MKPR)
    d[u'mprereqok'] = len(OKP)
    d[u'mprereqmiss'] = len(set(MKPR) - set(OKP))
    d[u'mck'] = len(re.findall(u'^([\\w.]+\\.ck):', TXT[3], re.M))
    d[u'mrm'] = len(re.findall(u'rm -fr \\$@d', BLK2))
    d[u'mmkdir'] = len(re.findall(u'mkdir \\$@d', BLK2))
    d[u'mzic'] = len(re.findall(u'\\./zic -d \\$@d', BLK2))
    d[u'mhorizons'] = len(re.findall(u'\\./zdump -i -t ([^ \\)]*)', BLK2))
    d[u'mfinds'] = len(re.findall(u'\\$\\(find ', BLK2))
    d[u'mzdfiles'] = len(_gl.glob(u'corpus/raw/**/*zdump*', recursive=True))
    d[u'mckfiles'] = len(_gl.glob(u'corpus/**/now.ck', recursive=True))
    d[u'mmvout'] = len(re.findall(u'mv \\$@\\.out \\$@', BLK2))
    d[u'mdollarnow'] = len(re.findall(u'\\$\\$now', BLK2))
    d[u'mnontab'] = len(re.findall(u"! -name '\\*\\.tab'", BLK2))
    d[u'mawkcall'] = len(re.findall(u'-f checknow\\.awk', BLK2))
    d[u'mtablearg'] = len(re.findall(u'-f checknow\\.awk zonenow\\.tab', BLK2))
    d[u'msysv'] = len(re.findall(u'SysVzone\\[', BLK2))
    Y = int(re.findall(u'^CHECK_NOW_FUTURE_YEARS = (\\d+)$', TXT[3], re.M)[0])
    d[u'myears'] = Y
    d[u'msecs'] = Y * 366 * 86400
    d[u'msecs365'] = Y * 365 * 86400
    d[u'mdiff'] = d[u'msecs'] - d[u'msecs365']
    BIG = int(re.findall(u'(\\d{4})\\+ years', TXT[3])[0])
    d[u'mbig'] = BIG
    d[u'mratio'] = BIG // Y

    # ---- 同名穿层: 原样计数 + 折叠命中 ----
    OCC = dict((t, [TXT[i].count(t) for i in range(N)])
               for t in (u'XX', u'zdump-now.tab', u'zdump_table', u'from now on', u'1970',
                         u'until', u'irrelevant', u'zone1970.tab', u'zonenow.tab', u'checknow.awk',
                         u'now.ck'))
    d[u'xx_n'] = OCC[u'XX'][0]
    d[u'xx_m'] = OCC[u'XX'][3]
    d[u'zdumpnow_m'] = OCC[u'zdump-now.tab'][3]
    d[u'zdumptable_k'] = OCC[u'zdump_table'][2]
    d[u'zdumptable_m'] = OCC[u'zdump_table'][3]
    d[u'nowon_n'] = OCC[u'from now on'][0]
    d[u'nowon_k'] = OCC[u'from now on'][2]
    d[u'until_n'] = OCC[u'until'][0]
    d[u'irr_n'] = OCC[u'irrelevant'][0]
    d[u'selfname_z'] = OCC[u'zone1970.tab'][1]
    d[u'selfname_n'] = OCC[u'zone1970.tab'][0]
    d[u'selfname_m'] = OCC[u'zone1970.tab'][3]
    d[u'ntab_k'] = OCC[u'zonenow.tab'][2]
    d[u'ntab_m'] = OCC[u'zonenow.tab'][3]
    d[u'cknow_m'] = OCC[u'checknow.awk'][3]
    d[u'y1970_n'] = OCC[u'1970'][0]
    d[u'y1970_m'] = OCC[u'1970'][3]
    d[u'nsrc'] = N
    FULL = [pn(t) for t in TXT]
    CROSS = [u'zdump_table', u'zdump-now.tab', u'zdump-1970.tab', u'from now on',
             u'agree from now on', u'irrelevant and ignored', u'XX', u'Pacific/Kiritimati',
             u'-1416-17042', u'+12:45/+13:45', u'zone1970.tab', u'zonenow.tab',
             u'checknow.awk', u'now.ck', u'until 2026-11-01']
    HS = [tuple(i for i in range(N) if pn(t) in FULL[i]) for t in CROSS]
    d[u'hitkinds'] = len(CROSS)
    d[u'hitsingle'] = len([h for h in HS if len(h) == 1])
    d[u'hitcross'] = len([h for h in HS if len(h) > 1])
    d[u'hitnone'] = len([h for h in HS if not h])

    # ---- 锚归属: 从条目正文的“源标签紧接原子引文”配对现推, 不读旁注文件 ----
    ep = _gl.glob(u'corpus/babeltele/B52_*.md')
    assert len(ep) == 1, ep
    T = open(ep[0], encoding='utf-8').read()
    enc = re.search(u'⟪BabelTele⟫' + chr(10) + u'(.*?)' + chr(10) + chr(10) + u'## ', T, re.S).group(1)
    CITES = re.findall(u'⟦([' + u''.join(TG) + u'])⟧⟨([^⟨⟩]+)⟩', enc)
    assert CITES, u'B52: 正文里没有带标签的锚'

    def hitset(a):
        n = pn(a)
        return tuple(i for i in range(N) if n and n in FULL[i])

    DIS = []
    for _, a in CITES:
        if a not in DIS:
            DIS.append(a)
    HC = [hitset(a) for a in DIS]
    d[u'anchor_total'] = len(CITES)
    d[u'anchor_distinct'] = len(DIS)
    d[u'anchor_err'] = len([h for h in HC if not h])
    d[u'anchor_single'] = len([h for h in HC if len(h) == 1])
    d[u'anchor_cross'] = len([h for h in HC if 1 < len(h) < N])
    d[u'anchor_all4'] = len([h for h in HC if len(h) == N])
    d[u'checks'] = len(DIS) * N
    assert d[u'anchor_single'] + d[u'anchor_cross'] + d[u'anchor_all4'] + d[u'anchor_err'] == len(DIS)
    return d

_B52 = _b52_scan()
B52V = lambda k, i=None: (_B52[k] if i is None else _B52[k][i])
'''

compile(BLK, u'<b52 block>', 'exec')
o = u'\n_B51 = _b51_scan()'
o2 = u'B51V=B51V)'
o2b = u'B51V=B51V,\n               B52V=B52V)'
if BLK in S:
    S = S.replace(BLK, u'')
if o2b in S:
    S = S.replace(o2b, o2)
assert S.count(o) == 1
S = S.replace(o, BLK + o)
assert S.count(o2) == 1
S = S.replace(o2, o2b)

# SRC['B52'] ⇎ ATOM 名单
PS = u"SRC['B51'] = ["
blk = (u"SRC['B52'] = ['corpus/raw/tz/zonenow.tab', 'corpus/raw/tz/zone1970.tab',\n"
       u"            'corpus/raw/tz/checknow.awk', 'corpus/raw/tz/Makefile']\n")
if blk in S:
    S = S.replace(blk, u'')
assert S.count(PS) == 1
S = S.replace(PS, blk + PS)
OLD = u"'B49', 'B50', 'B51'}"
NEW = u"'B49', 'B50', 'B51', 'B52'}"
if NEW not in S:
    assert S.count(OLD) == 1
    S = S.replace(OLD, NEW)

M1 = u'# ---- B52 DERIV (generated by corpus/_mkB52.py; do not hand-edit) ----'
M2 = u'# ---- /B52 DERIV ----'
pat = re.compile(re.escape(M1) + u'.*?' + re.escape(M2) + u'\\n', re.S)
if pat.search(S):
    S = pat.sub(u'', S)
o3 = u"DERIV['B38'] = {"
assert S.count(o3) == 1
J = __import__('json').load(io.open(u'corpus/_deriv52.json', encoding='utf-8'))
body = M1 + u'\n' + u"DERIV['B52'] = " + repr(J) + u'\n' + M2 + u'\n'
S = S.replace(o3, body + o3)

# 预演: 用刚写好的扫描器把 DERIV 的每一条算一遍, 值不符就当场停机, 别让门槛去猜
NS = {'SRC': {'B52': ['corpus/raw/tz/zonenow.tab', 'corpus/raw/tz/zone1970.tab',
                      'corpus/raw/tz/checknow.awk', 'corpus/raw/tz/Makefile']},
      're': re, 'os': __import__('os'), 'glob': __import__('glob')}
exec(compile(BLK, u'<b52 block>', 'exec'), NS)
env = NS['B52V']
BAD = []
FLAT = __import__('json').load(io.open(u'corpus/_b52flat.json', encoding='utf-8'))
MISMATCH = []
for k, v in FLAT.items():
    try:
        got = env(k)
    except Exception as e:
        BAD.append((k, repr(e)))
        continue
    if got != v:
        MISMATCH.append((k, v, got))
assert not BAD, BAD
assert not MISMATCH, MISMATCH
for kk, v in J.items():
    try:
        got = eval(v, dict(NS), {'B52V': env})
    except Exception as e:
        BAD.append((kk, v, repr(e)))
        continue
    if str(got) != kk and repr(got) != kk:
        BAD.append((kk, v, str(got)))
assert not BAD, BAD
assert len(S) > 100000 and u'_b51_scan' in S
compile(S, u'<audit.py wired>', 'exec')
T = P + u'.tmp'
io.open(T, 'w', encoding='utf-8', newline=u'\012').write(S)
__import__('os').replace(T, P)
print(u'audit.py wired: scan+env+DERIV(%d keys, 扁平键 %d 个逐一对账, 预演全对)' % (len(J), len(FLAT)))
