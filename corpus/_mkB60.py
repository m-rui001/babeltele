# -*- coding: utf-8 -*-
"""B60 建条目(第二遍现算, 五源): T = raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt
⇎ O = BR-1.8.7.layout.txt ⇎ F = TLS-BRs-v2.0.2.layout.txt(三代 CA/Browser Forum 基准要求, pdftotext -layout 面)
⇎ N = le_lifetimes.html(Let's Encrypt 生命周期说明) ⇎ R = rfc5280.txt(X.509 规范)。
主轴: 一张公签 TLS 服务器证书最长能活多久——⟦T⟧/⟦O⟧ 两份都写着“2018-03-01 之后、2020-09-01 之前签发者 MUST NOT 超过 825 天”,
并同给现行 SHOULD NOT 397 ⇎ MUST NOT 398 两档; ⟦F⟧ 的上限句里再无 825, 它只活在 §1.6 历史时间表与“验证信息复用期”一侧;
⟦N⟧ 90 天默认 ⇎ 6 天可选 ⇎ 2028 年 2 月前降到 45 天, 并把“自 2029-03-15 起上限 47 天”归给“行业规则”——45/47 作天数在三份在库 BR 里为 0;
⟦R⟧ 通篇不出现“N days”, 只管这两个时刻怎么写(UTCTime 覆盖到 2049 年 ⇎ GeneralizedTime)。
配套轴: 同一句在上/中两代逐字同在, 而第一遍的单空格正则只撞到一份(排版把短语折在行间断了它); 术语四套叫法
(Validity Period ⇎ validity period ⇎ lifetime ⇎ notBefore/notAfter); 强度词的“正文 ⇎ 历史时间表行”分布与词界⇎子串两档;
三代 BR 的整行搬运 ⇎ BR 与 RFC 5280 的几乎不共用; LE 页同一句在 meta ⇎ og ⇎ <p> 里三份序列化(去壳只留一份)。
第二遍的独立性: 上限句改用“动词×数字×对象”三元组现抽并让短语容许换行(pick 用单空格逐字面, 于是漏判中代那份);
所指分解按整篇窗口并把窗口内空白折起来再判(pick 曾逐行漏判); day 写法分连字/空格/单数三档相加校住数字期限全数, 换行档另立一键;
壳内 ⇎ 面内的句数与天数各立一键并闭合(壳多出的两份正是 meta 与 og); 形状量另用独立算法复算(计数代 len, split 代 count)。
抓取时刻与磁盘 mtime、cabforum.org 是否已挂更新版、LE 页“最后更新”之真伪只在本机或站外成立, 不进门槛。"""
import io, os, re, sys, json, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
NSRC = 5
ENTRY = u'%s/babeltele/B60_certificate_validity_five_answers.md' % C
PATH = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.layout.txt',
        u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.layout.txt',
        u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.layout.txt',
        u'corpus/raw/cert/le_lifetimes.html',
        u'corpus/raw/cert/rfc5280.txt']
RAWPDF = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.pdf',
          u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.pdf',
          u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.pdf']
RAWFACE = [u'corpus/raw/cert/CA-Browser-Forum-BR-1.7.7.raw.txt',
           u'corpus/raw/cert/CA-Browser-Forum-BR-1.8.7.raw.txt',
           u'corpus/raw/cert/CA-Browser-Forum-TLS-BRs-v2.0.2.raw.txt']
TAGS = [u'T', u'O', u'F', u'N', u'R']
LB = dict(zip(TAGS, [u'旧基准', u'中基准', u'新基准', u'CA 说明', u'X.509 规范']))
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN --- (corpus/_wire60.py 把这一段机械切进 audit.py::_b60_scan)
ENT = [(u'&#39;', "'"), (u'&#43;', '+'), (u'&amp;', '&'), (u'&rsquo;', u'’'), (u'&copy;', u'©')]
pnorm = lambda s: re.sub(r'[^a-z0-9]', u'', s.lower())


def unscript(s):
    return re.sub(r'(?is)<(script|style)\b.*?</\1>', u'', s)


def striphtml(s, br=u' '):
    s = re.sub(r'(?is)<!--.*?-->', u'', s)
    s = re.sub(r'(?i)<br\s*/?>', br, s)
    s = re.sub(r'<[^>]+>', u' ', s)
    for a, b in ENT:
        s = s.replace(a, b)
    return re.sub(r'[ \t]+', u' ', s).strip()


RAW = [RD(p) for p in PATH]
# 只有第四份是带壳网页; 四份纯文本面原样使用(不去壳, 否则 RFC 的 <尖括号> 伪法会被当标签删掉)。
TXT = [RAW[i] if i != 3 else striphtml(unscript(RAW[i])) for i in range(NSRC)]
LST = [[l for l in TXT[i].split(NL)] for i in range(NSRC)]
LOW = [t.lower() for t in TXT]
FAN = [pnorm(t) for t in TXT]
RW = [RD(p) for p in RAWFACE]
PDFB = [os.path.getsize(p) for p in RAWPDF]
F = {}


def four(name, f, n=NSRC):
    F[name] = [f(k) for k in range(n)]
    return F[name]


def occ(s, sub):
    return s.count(sub)


def sha8(p):
    return hashlib.blake2b(io.open(p, 'rb').read(), digest_size=8).hexdigest()


# ---- 形状档 ----
four(u'bytes', lambda i: os.path.getsize(PATH[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'lines', lambda i: len(TXT[i].split(NL)))
four(u'nonblank', lambda i: len([l for l in TXT[i].split(NL) if l.strip()]))
four(u'formfeed', lambda i: TXT[i].count(u'\x0c'))
four(u'maxlen', lambda i: max(len(l) for l in TXT[i].split(NL)))
four(u'trail', lambda i: len([l for l in TXT[i].split(NL) if l != l.rstrip()]))
# 独立复算(计数代 len; split 的逆运算代 len(split)): 同义不同法, 相加须为 0
F[u'chars_rec'] = [sum(1 for _ in TXT[i]) for i in range(NSRC)]
F[u'lines_rec'] = [TXT[i].count(NL) + 1 for i in range(NSRC)]
four(u'rec_close', lambda i: F[u'chars_rec'][i] - F[u'chars'][i] + F[u'lines_rec'][i] - F[u'lines'][i])
F[u'pdf_bytes'] = PDFB
F[u'raw_chars'] = [len(x) for x in RW]
F[u'raw_lines'] = [len(x.split(NL)) for x in RW]
F[u'raw_formfeed'] = [x.count(u'\x0c') for x in RW]
F[u'face_gap'] = [len(TXT[i]) - len(RW[i]) for i in range(3)]
F[u'line_gap'] = [len(TXT[i].split(NL)) - len(RW[i].split(NL)) for i in range(3)]
F[u'ff_close'] = [F[u'formfeed'][i] - F[u'raw_formfeed'][i] for i in range(3)]
F[u'sig'] = [sha8(p) for p in PATH]
F[u'sig_distinct'] = len(set(F[u'sig']))
F[u'ent_listed'] = len(ENT)
F[u'ent_unused'] = [a for a, _b in ENT if a not in RAW[3]]
F[u'ent_unnamed'] = sorted(set(re.findall(r'&[A-Za-z]+;|&#[0-9]+;', RAW[3])) - set(a for a, _b in ENT))
F[u'le_scripts'] = len(re.findall(r'(?is)<script\b.*?</script>', RAW[3]))
F[u'le_styles'] = len(re.findall(r'(?is)<style\b.*?</style>', RAW[3]))
F[u'le_tags'] = len(re.findall(r'<[^>]+>', RAW[3]))
F[u'le_ents'] = len(re.findall(r'&[A-Za-z]+;|&#[0-9]+;', RAW[3]))
F[u'le_hrefs'] = len(re.findall(r'href=', RAW[3]))
F[u'le_metas'] = len(re.findall(r'(?i)<meta\b', RAW[3]))
F[u'le_dropped'] = len(RAW[3]) - len(TXT[3])

# ---- 天数族: 连字 ⇎ 空格 ⇎ 单数 相加校住数字期限全数; 换行档另立一键 ----
NUMDAY = re.compile(r'(\d[\d,]*)[ -]days?\b')
NUMDAYF = re.compile(r'(\d[\d,]*)[\s-]days?\b')
four(u'day_num', lambda i: len(NUMDAY.findall(TXT[i])))
four(u'day_set', lambda i: sorted(set(x.replace(u',', u'') for x in NUMDAY.findall(TXT[i])), key=int))
four(u'day_num_flex', lambda i: len(NUMDAYF.findall(TXT[i])))
four(u'day_hyph', lambda i: len(re.findall(r'\d[\d,]*-days?\b', TXT[i])))
four(u'day_spac', lambda i: len(re.findall(r'\d[\d,]* days\b', TXT[i])))
four(u'day_sing', lambda i: len(re.findall(r'\d[\d,]* day\b', TXT[i])))
four(u'day_word', lambda i: len(re.findall(r'(?i)\bdays?\b', TXT[i])))
F[u'day_set_n'] = [len(x) for x in F[u'day_set']]
F[u'day_wrap'] = [F[u'day_num_flex'][i] - F[u'day_num'][i] for i in range(NSRC)]
F[u'day_num_close'] = [F[u'day_hyph'][i] + F[u'day_spac'][i] + F[u'day_sing'][i] - F[u'day_num'][i]
                       for i in range(NSRC)]
F[u'day_free'] = [F[u'day_word'][i] - F[u'day_num'][i] for i in range(NSRC)]

# ---- 上限句: 动词×数字×对象 三元组(整篇扫描, 短语容许换行; 单空格档并记以显出折行损失) ----
CEIL = re.compile(r'(MUST NOT|MUST|SHOULD NOT|SHOULD)\s+have a\s+Validity\s+Period\s+greater\s+than\s+(\d+)\s+days')
CEILS = re.compile(r'(MUST NOT|MUST|SHOULD NOT|SHOULD) have a Validity Period greater than (\d+) days')
F[u'ceil_tri'] = [sorted(set(CEIL.findall(TXT[i]))) for i in range(NSRC)]
four(u'ceil_n', lambda i: len(CEIL.findall(TXT[i])))
four(u'ceil_strict_n', lambda i: len(CEILS.findall(TXT[i])))
four(u'ceil_vals', lambda i: sorted(set(x for _v, x in CEIL.findall(TXT[i])), key=int))
four(u'ceil_distinct', lambda i: len(set(CEIL.findall(TXT[i]))))
F[u'ceil_wrap'] = [F[u'ceil_n'][i] - F[u'ceil_strict_n'][i] for i in range(NSRC)]
F[u'd825_ceil'] = [len([1 for x in CEIL.findall(TXT[i]) if x[1] == u'825']) for i in range(NSRC)]
F[u'd825_strict'] = [len([1 for x in CEILS.findall(TXT[i]) if x[1] == u'825']) for i in range(NSRC)]


def swin(t, num, lo=140, hi=140):
    out = []
    for m in re.finditer(re.escape(num) + r'[\s-]+days?\b', t):
        a = max(0, m.start() - lo)
        b = min(len(t), m.end() + hi)
        out.append(u' '.join(t[a:b].split()))
    return out


def cls(win, *needles):
    return len([w for w in win if all(n.lower() in w.lower() for n in needles)])


def prio(ws, *needles):
    out, left = [], list(ws)
    for n in needles:
        hit = [w for w in left if n.lower() in w.lower()]
        out.append(len(hit))
        left = [w for w in left if w not in hit]
    out.append(len(left))
    return out


NUMS = (u'825', u'398', u'397', u'90', u'45', u'47', u'6')
for num in NUMS:
    F[u'lines_' + num] = [0] * NSRC
    F[u'validwin_' + num] = [0] * NSRC
    F[u'reusewin_' + num] = [0] * NSRC
    F[u'titlewin_' + num] = [0] * NSRC
    F[u'otherwin_' + num] = [0] * NSRC
    for i in range(NSRC):
        a, b, c, d = prio(swin(TXT[i], num), u'Validity Period', u'prior to issuing', u'%s-day' % num)
        F[u'validwin_' + num][i] = a
        F[u'reusewin_' + num][i] = b
        F[u'titlewin_' + num][i] = c
        F[u'otherwin_' + num][i] = d
        F[u'lines_' + num][i] = a + b + c + d
F[u'otherwin_total'] = sum(sum(F[u'otherwin_' + n]) for n in NUMS)
F[u'titlewin_total'] = sum(sum(F[u'titlewin_' + n]) for n in NUMS)
F[u'reusewin_total'] = sum(sum(F[u'reusewin_' + n]) for n in NUMS)
F[u'validwin_total'] = sum(sum(F[u'validwin_' + n]) for n in NUMS)
F[u'win_close'] = (F[u'validwin_total'] + F[u'reusewin_total'] + F[u'titlewin_total']
                   + F[u'otherwin_total'] - sum(sum(F[u'lines_' + n]) for n in NUMS))
F[u'num_45_in_brs'] = sum(F[u'day_set'][i].count(u'45') for i in range(3))
F[u'num_47_in_brs'] = sum(F[u'day_set'][i].count(u'47') for i in range(3))
F[u'set_shared_NF'] = sorted(set(F[u'day_set'][3]) & set(F[u'day_set'][2]), key=int)
F[u'set_only_N'] = sorted(set(F[u'day_set'][3]) - set(sum([F[u'day_set'][i] for i in range(3)], [])), key=int)
F[u'set_shared_TF'] = sorted(set(F[u'day_set'][0]) & set(F[u'day_set'][2]), key=int)
F[u'set_only_F'] = sorted(set(F[u'day_set'][2]) - set(F[u'day_set'][0]) - set(F[u'day_set'][1]), key=int)

# ---- 术语: 大小写档 × 逐字面/容换行档 ----
four(u'vp_caps', lambda i: occ(TXT[i], u'Validity Period'))
four(u'vp_low', lambda i: occ(TXT[i], u'validity period'))
four(u'vp_ci', lambda i: occ(LOW[i], u'validity period'))
four(u'vp_flex_ci', lambda i: len(re.findall(r'(?i)validity\s+period', TXT[i])))
four(u'validity_stem', lambda i: len(re.findall(r'(?i)validity', TXT[i])))
F[u'vp_wrap'] = [F[u'vp_flex_ci'][i] - F[u'vp_ci'][i] for i in range(NSRC)]
F[u'vp_ci_close'] = [F[u'vp_caps'][i] + F[u'vp_low'][i] - F[u'vp_ci'][i] for i in range(NSRC)]
F[u'vp_stem_gap'] = [F[u'validity_stem'][i] - F[u'vp_flex_ci'][i] for i in range(NSRC)]
four(u'lifetime_ci', lambda i: len(re.findall(r'(?i)lifetime', TXT[i])))
four(u'notbefore', lambda i: occ(TXT[i], u'notBefore'))
four(u'notafter', lambda i: occ(TXT[i], u'notAfter'))
F[u'nanb_gap'] = [F[u'notafter'][i] - F[u'notbefore'][i] for i in range(NSRC)]

# ---- 强度词: 词界档 ⇎ 子串档 ⇎ 忽略大小写档 ⇎ 小写档 ----
for w in (u'MUST NOT', u'SHOULD NOT', u'MUST', u'SHOULD', u'MAY'):
    four(u'u_' + w.replace(u' ', u'_').lower(), lambda i, w=w: occ(TXT[i], w))
four(u'kw_must', lambda i: len(re.findall(r'\bMUST\b', TXT[i])))
four(u'kw_must_not', lambda i: len(re.findall(r'\bMUST NOT\b', TXT[i])))
four(u'kw_should', lambda i: len(re.findall(r'\bSHOULD\b', TXT[i])))
F[u'u_must_gap'] = [F[u'u_must'][i] - F[u'u_must_not'][i] for i in range(NSRC)]
F[u'u_should_gap'] = [F[u'u_should'][i] - F[u'u_should_not'][i] for i in range(NSRC)]
F[u'must_sub_gap'] = [F[u'u_must'][i] - F[u'kw_must'][i] for i in range(NSRC)]
F[u'mustnot_sub_gap'] = [F[u'u_must_not'][i] - F[u'kw_must_not'][i] for i in range(NSRC)]
four(u'must_ci', lambda i: len(re.findall(r'(?i)\bmust\b', TXT[i])))
four(u'must_l', lambda i: len(re.findall(r'\bmust\b', TXT[i])))
four(u'shall_u', lambda i: len(re.findall(r'\bSHALL\b', TXT[i])))
four(u'shall_ci', lambda i: len(re.findall(r'(?i)\bshall\b', TXT[i])))
four(u'shall_l', lambda i: len(re.findall(r'\bshall\b', TXT[i])))
four(u'will_ci', lambda i: len(re.findall(r'(?i)\bwill\b', TXT[i])))
F[u'kw_upper'] = [F[u'kw_must'][i] + F[u'kw_should'][i] + F[u'u_may'][i] + F[u'shall_u'][i] for i in range(NSRC)]
F[u'kw_ci'] = [F[u'must_ci'][i] + F[u'shall_ci'][i] + len(re.findall(r'(?i)\bmay\b', TXT[i]))
               + len(re.findall(r'(?i)\bshould\b', TXT[i])) for i in range(NSRC)]

# ---- 强度词的“历史时间表行 ⇎ 其余正文”分布(同一谓词分两半, 相加须等于全量) ----
HISTROW = re.compile(r'^\s*\d{4}-\d{2}-\d{2}|\bSC\d')
HIST = [[l for l in TXT[i].split(NL) if HISTROW.search(l)] for i in range(NSRC)]
four(u'hist_n', lambda i: len(HIST[i]))
four(u'hist_chars', lambda i: len(NL.join(HIST[i])))


def hsplit(i, pred):
    h = NL.join(HIST[i])
    rest = NL.join([l for l in TXT[i].split(NL) if l not in HIST[i]])
    return pred(h), pred(rest)


P_MUST = lambda s: len(re.findall(r'\bMUST\b', s))
P_SHALL = lambda s: len(re.findall(r'(?i)\bshall\b', s))
P_SUB = lambda s: s.count(u'MUST')
for nm, pred, whole in ((u'must', P_MUST, u'kw_must'), (u'shall', P_SHALL, u'shall_ci'),
                        (u'sub', P_SUB, u'u_must')):
    F[u'h_' + nm] = [hsplit(i, pred)[0] for i in range(NSRC)]
    F[u'b_' + nm] = [hsplit(i, pred)[1] for i in range(NSRC)]
    F[u'h_%s_close' % nm] = [F[u'h_' + nm][i] + F[u'b_' + nm][i] - F[whole][i] for i in range(NSRC)]

# ---- 时间写法(RFC 5280 独有的轴) ----
for w in (u'UTCTime', u'GeneralizedTime', u'YYMMDDHHMMSSZ', u'YYYYMMDDHHMMSSZ'):
    four(u'ts_' + w.lower(), lambda i, w=w: occ(TXT[i], w))
four(u'y2049', lambda i: len(re.findall(r'\b2049\b', TXT[i])))
four(u'y2050', lambda i: len(re.findall(r'\b2050\b', TXT[i])))
F[u'ts_non_R'] = [F[u'ts_utctime'][i] for i in range(NSRC - 1)]
F[u'ts_only_R'] = F[u'ts_utctime'][NSRC - 1] - max(F[u'ts_non_R'])
F[u'gt_non_R'] = [F[u'ts_generalizedtime'][i] for i in range(NSRC - 1)]
F[u'gt_only_R'] = F[u'ts_generalizedtime'][NSRC - 1] - max(F[u'gt_non_R'])

# ---- 日期写法三档 ----
four(u'iso_date', lambda i: len(re.findall(r'\b\d{4}-\d{2}-\d{2}\b', TXT[i])))
four(u'us_date', lambda i: len(re.findall(
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}', TXT[i])))
four(u'month_year', lambda i: len(re.findall(
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) 2\d{3}\b', TXT[i])))
four(u'yyyy_any', lambda i: len(re.findall(r'\b20[1-3]\d\b', TXT[i])))
F[u'y2029'] = [occ(TXT[i], u'2029') for i in range(NSRC)]
F[u'y2028'] = [occ(TXT[i], u'2028') for i in range(NSRC)]
F[u'y2015'] = [occ(TXT[i], u'2015') for i in range(NSRC)]

# ---- LE 页: 同一句在壳(meta ⇎ og)与面(<p>)里各几份 ----
SENT = [(u's90', u'certificates with 90-day lifetimes'), (u's6', u'Short-lived certificates with 6-day lifetimes'),
        (u's47', u'maximum of 47 days starting on March 15, 2029'), (u's45', u'45 days by February 2028')]
for nm, lit in SENT:
    F[u'shell_' + nm] = RAW[3].count(lit)
    F[u'face_' + nm] = TXT[3].count(lit)
F[u'shell_all'] = [F[u'shell_' + nm] for nm, _l in SENT]
F[u'face_all'] = [F[u'face_' + nm] for nm, _l in SENT]
F[u'dup_gap'] = [F[u'shell_' + nm] - F[u'face_' + nm] for nm, _l in SENT]
F[u'dup_kinds'] = len(set(F[u'dup_gap']))
F[u'day_shell'] = len(NUMDAY.findall(RAW[3]))
F[u'day_face'] = len(NUMDAY.findall(TXT[3]))
_a = RAW[3].find(u'<meta property=')
F[u'day_meta'] = len(NUMDAY.findall(RAW[3][RAW[3].find(u'<meta name="description"'):_a]))
F[u'day_shell_close'] = F[u'day_shell'] - F[u'day_face'] - 2 * F[u'day_meta']

# ---- 条款引用体例 ----
four(u'sec_cite', lambda i: len(re.findall(r'\bSection \d', TXT[i])))
four(u'sec_cite_low', lambda i: len(re.findall(r'\bsection \d', TXT[i])))
four(u'sec_head', lambda i: len(re.findall(r'(?m)^\s*((?:\d+\.){1,3}\d+)\s', TXT[i])))
four(u'sec_head_d', lambda i: len(set(re.findall(r'(?m)^\s*((?:\d+\.){1,3}\d+)\s', TXT[i]))))
BRREFS = [sorted(set(re.findall(r'RFC\s?(\d{4})', TXT[i]))) for i in range(NSRC)]
RREFS = set(re.findall(r'RFC\s?(\d{4})', TXT[4]))
F[u'rfc_set_n'] = [len(x) for x in BRREFS]
F[u'rfc_hit_R'] = [len([x for x in BRREFS[i] if x in RREFS]) for i in range(NSRC)]
F[u'rfc_miss_n'] = [len(set(BRREFS[i]) - RREFS) for i in range(NSRC)]
F[u'rfc_n5280'] = [len(re.findall(r'\b5280\b', TXT[i])) for i in range(NSRC)]

# ---- 自我标注 ----
F[u'ver_self'] = [re.findall(r'Version \d+\.\d+(?:\.\d+)?', TXT[i])[:3] for i in range(NSRC)]
four(u'ver_any', lambda i: len(re.findall(r'(?i)version \d', TXT[i])))
four(u'baseline_reqs', lambda i: occ(TXT[i], u'Baseline Requirements'))
four(u'last_updated', lambda i: len(re.findall(r'(?i)last updated', TXT[i])))
four(u'asn1_mod', lambda i: len(re.findall(r'(?i)ASN\.?1', TXT[i])))
four(u'rfc2119', lambda i: len(re.findall(r'\b2119\b', TXT[i])))

# ---- 跨文书整行共用(只取足够长的行, 归一化后比集合) ----
LSETS = [set(pnorm(l) for l in LST[i] if len(l.strip()) >= 25 and pnorm(l)) for i in range(NSRC)]
four(u'lines_ge25', lambda i: len(LSETS[i]))
PAIRS = [(0, 1), (1, 2), (0, 2), (0, 4), (1, 4), (2, 4), (0, 3), (1, 3), (2, 3), (3, 4)]
for a, b in PAIRS:
    F[u'share_%s%s' % (TAGS[a], TAGS[b])] = len(LSETS[a] & LSETS[b])
F[u'share_TOF'] = len(LSETS[0] & LSETS[1] & LSETS[2])
F[u'union_TOF'] = len(LSETS[0] | LSETS[1] | LSETS[2])
F[u'only_T'] = len(LSETS[0] - LSETS[1] - LSETS[2])
F[u'only_O'] = len(LSETS[1] - LSETS[0] - LSETS[2])
F[u'only_F'] = len(LSETS[2] - LSETS[0] - LSETS[1])
F[u'tof_close'] = (F[u'only_T'] + F[u'only_O'] + F[u'only_F']
                   + F[u'share_TO'] + F[u'share_OF'] + F[u'share_TF']
                   - 2 * F[u'share_TOF'] - F[u'union_TOF'])
COMMON_TR = sorted(LSETS[0] & LSETS[4])
COMMON_FR = sorted(LSETS[2] & LSETS[4])


def line_of(i, key):
    for l in LST[i]:
        if pnorm(l) == key:
            return l.strip()
    return u''


F[u'share_TR_lines'] = [line_of(0, k) for k in COMMON_TR]
F[u'share_FR_lines'] = [line_of(2, k) for k in COMMON_FR]
F[u'share_any_R'] = len(set(COMMON_TR) | set(LSETS[1] & LSETS[4]) | set(COMMON_FR))
F[u'share_N_any'] = len(LSETS[3] & (LSETS[0] | LSETS[1] | LSETS[2] | LSETS[4]))

# ---- 锚池: 按“这条锚在几份文书里逐字再现”分层 ----
SPECIAL = (u'825 days', u'397 days', u'398 days', u'Validity Period', u'90-day', u'6-day', u'47 days',
           u'45 days', u'notBefore', u'notAfter', u'UTCTime', u'GeneralizedTime', u'Baseline Requirements',
           u'prior to issuing', u'MUST NOT have a Validity')
POOL = set()
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if pnorm(l):
            POOL.add((t, l))
POOL = sorted(POOL)
CROSS = dict(((t, x), sum(1 for k in range(NSRC) if pnorm(x) in FAN[k])) for (t, x) in POOL)
POOLC = [(t, CROSS[(t, x)], x) for (t, x) in POOL]
F[u'pool_n'] = len(POOLC)
four(u'pool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
for n in range(1, NSRC + 1):
    F[u'pool_%d' % n] = len([p for p in POOLC if p[1] == n])
F[u'pool_tiers'] = [F[u'pool_%d' % n] for n in range(1, NSRC + 1)]
F[u'pool_close'] = sum(F[u'pool_tiers']) - F[u'pool_n']
F[u'pool_maxlen'] = max(len(p[2]) for p in POOLC)


def ATOMSEL(kind, tag, *needles):
    ok = (lambda n: n == 1) if kind == u'own' else (lambda n: n == int(kind[1:]))
    got = [p for p in POOLC if p[0] == tag and ok(p[1]) and all(x in p[2] for x in needles)]
    if not got:
        got = [p for p in POOLC if p[0] == tag and all(x in p[2] for x in needles)]
    assert got, (kind, tag, needles)
    return max(got, key=lambda x: (len(x[2]), x[2]))


USEDATOM = []


def AT(kind, tag, *needles):
    x = ATOMSEL(kind, tag, *needles)
    USEDATOM.append(x[2])
    return u'⟦%s⟧⟨%s⟩' % (tag, x[2])


CLOSK = sorted([k for k in F if (u'_close' in k or k.endswith(u'_ledger'))
                and isinstance(F[k], (int, float)) and not isinstance(F[k], bool)])
F[u'scalar_clos_n'] = len(CLOSK)
F[u'scalar_clos_sum'] = sum(F[k] for k in CLOSK)
F[u'scalar_clos_list'] = CLOSK
F[u'list_clos_n'] = len([k for k in F if (u'_close' in k or k.endswith(u'_ledger')) and isinstance(F[k], list)])

# --- SCAN END ---

# ---------- DERIV 登记与正文模板 ----------
K, ZERO, COLL, SEENX = {}, [], {}, {}
G, LINES, MISSING = {}, [], []
FN = u'B60V'


def reg(s, expr, note):
    if s == u'0':
        if expr not in ZERO:
            ZERO.append(expr)
        return
    if s in K:
        if expr not in SEENX[s]:
            SEENX[s].append(expr)
            COLL.setdefault(s, []).append(note)
        return
    SEENX[s] = [expr]
    K.setdefault(s, (expr, note))


def dump_deriv():
    out = dict((k, v[0]) for k, v in K.items())
    for k, exprs in SEENX.items():
        if len(exprs) < 2:
            continue
        nums = [eval(e, {u'B60V': BB60}) for e in exprs]
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums):
            out[k] = u"%s*(1-(max([%s])-min([%s])))" % (k, u','.join(exprs), u','.join(exprs))
        else:
            out[k] = u"%s*(1-(len(set([tuple(y) for y in [%s]]))-1))" % (k, u','.join(exprs))
    return out


def V(name, i=None, note=u''):
    val = F[name][i] if i is not None else F[name]
    s = repr(val) if isinstance(val, float) else str(val)
    reg(s, u"%s('%s'%s)" % (FN, name, u'' if i is None else u', ' + repr(i)), note or name)
    return s


def EXPR(val, expr, note):
    reg(str(val), expr, note)
    return str(val)


def CLOS(key, note):
    return V(key, None, note)


def CLOS4(key, note):
    return u' ⇎ '.join(V(key, i, u'%s·%s' % (note, LB[t])) for i, t in enumerate(TAGS))


TOKV = {}


def TOK(name, note=u''):
    TOKV[name] = note
    return u'◘%s◙' % name


def JOIN(name, note=u''):
    return u' ⇎ '.join(V(name, i, u'%s·%s' % (note or name, LB[t])) for i, t in enumerate(TAGS))


BB60 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B60V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
BARE = re.compile(r'^[0-9+\-*/().,\s]*$')
HELP = re.compile(u"^(V|JOIN|CLOS|CLOS4|TOK|AT)\\(")
_Q = u'"\''


def _split_top(s):
    out, buf, d, q = [], u'', 0, None
    for ch in s:
        if q:
            buf += ch
            if ch == q:
                q = None
            continue
        if ch in _Q:
            q = ch
            buf += ch
            continue
        if ch in u'([{':
            d += 1
        elif ch in u')]})':
            d -= 1
        if ch == u',' and d == 0:
            out.append(buf)
            buf = u''
            continue
        buf += ch
    out.append(buf)
    return [x.strip() for x in out]


def _unlit(x):
    t = x[1:] if x[:1] == u'u' else x
    assert t[0] in _Q and t[-1] == t[0], x
    return t[1:-1]


def _inline(t):
    while True:
        i = t.find(u'{EXPR(')
        if i < 0:
            break
        j = t.index(u'(', i)
        d, k = 0, j
        q = None
        while True:
            c = t[k]
            if q:
                if c == q:
                    q = None
                k += 1
                continue
            if c in _Q:
                q = c
                k += 1
                continue
            if c == u'(':
                d += 1
            elif c == u')':
                d -= 1
                if d == 0:
                    break
            k += 1
        if t[k + 1] != u'}':
            raise AssertionError((u'EXPRSCAN', repr(t[i:k + 4]), repr(t[j + 1:k])))
        args = _split_top(t[j + 1:k])
        assert len(args) == 3, args
        val = eval(args[0], {u'F': F, u'B60V': BB60, u'len': len, u'max': max, u'round': round,
                             u'repr': repr})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]

    def rep(m):
        c = m.group(1).strip()
        if HELP.match(c):
            return eval(c, {u'V': V, u'JOIN': JOIN, u'CLOS': CLOS, u'CLOS4': CLOS4, u'TOK': TOK, u'AT': AT})
        if u'B60V(' not in c:
            return m.group(0)
        assert BARE.match(BCALL.sub(u'0', c)), c
        val = eval(c, {u'B60V': BB60})
        reg(str(val), c.strip(), c.strip())
        return str(val)
    return re.sub(r'\{([^{}]*)\}', rep, t)


class _Ctx(dict):
    def __missing__(self, k):
        MISSING.append(k)
        return u'§' + k


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + _inline(tmpl)).format_map(_Ctx(dict(G, **kw))))

# ---------- 锚(位置由池现推, 不手打) ----------
G[u'A_ceil'] = AT(u'own', u'T', u'MUST NOT have a Validity Period greater than 825 days')
G[u'A_ceilO'] = AT(u'own', u'O', u'Period greater than 825 days')
G[u'A_reuse'] = AT(u'own', u'T', u'no more than 825 days prior')
G[u'A_title'] = AT(u'own', u'T', u'825-day')
G[u'A_398title'] = AT(u'own', u'F', u'398-day')
G[u'A_10day'] = AT(u'own', u'F', u'10 days')
G[u'A_root'] = AT(u'own', u'F', u'2922')
G[u'A_90'] = AT(u'own', u'N', u'90-day lifetimes')
G[u'A_6'] = AT(u'own', u'N', u'Short-lived certificates')
G[u'A_47'] = AT(u'own', u'N', u'47 days starting on March 15, 2029')
G[u'A_45'] = AT(u'own', u'N', u'45 days by February 2028')
G[u'A_R_nb'] = AT(u'own', u'R', u'notAfter')
G[u'A_R_utc'] = AT(u'own', u'R', u'UTCTime')
G[u'A_R_gen'] = AT(u'own', u'R', u'GeneralizedTime')
G[u'A_ca'] = AT(u'own', u'T', u'Certification Authority')
G[u'A_incl'] = AT(u'own', u'F', u'notBefore through notAfter')

# ---------- 正文 ----------
LINE(u'🧭', u"五源字节 {JOIN('bytes')}: 旧基准 ⇎ 中基准 ⇎ 新基准 ⇎ CA 说明 ⇎ X.509 规范; 面内字符 {JOIN('chars')} ⇎ 原文件行 {JOIN('lines')} ⇎ 非空行 {JOIN('nonblank')} ⇎ 最长行 {JOIN('maxlen')} 列。"
     u"前三份各有孪生面: PDF 原字节 {V('pdf_bytes',0)}⇎{V('pdf_bytes',1)}⇎{V('pdf_bytes',2)} ⇎ -layout 面比 -raw 面多 {V('face_gap',0)}⇎{V('face_gap',1)}⇎{V('face_gap',2)} 字、"
     u"多 {V('line_gap',0)}⇎{V('line_gap',1)}⇎{V('line_gap',2)} 行, 而分页符 U+000C 两面各 {V('formfeed',0)}⇎{V('formfeed',1)}⇎{V('formfeed',2)} 枚, 差 {V('ff_close',0)}⇎{V('ff_close',1)}⇎{V('ff_close',2)}——"
     u"换的是行的位置, 不是页的边界。第四份带壳: 标签 {V('le_tags')} 枚 ⇎ 实体 {V('le_ents')} 枚 ⇎ 脚本 {V('le_scripts')} 枚 ⇎ 样式 {V('le_styles')} 枚 ⇎ href {V('le_hrefs')} 条 ⇎ meta {V('le_metas')} 枚, "
     u"剥壳丢 {V('le_dropped')} 字; 转义层只点名 {V('ent_listed')} 枚, 页内未登记的实体 {V('ent_unnamed')} 枚, 登记而未用到的 {V('ent_unused')} 枚。"
     u"形状量另用独立算法复算(逐字计数代 len, 数换行代 split), 两法之差合计 {CLOS('rec_close', '复算差')}。五份签名 {V('sig_distinct')} 种(blake2b 前 16 位)。")

LINE(u'📐', u"上限只认一个句式: 动词 + have a Validity Period greater than + 数字 + days。三元组现抽: 旧基准 {V('ceil_tri',0)} ⇎ 中基准 {V('ceil_tri',1)} ⇎ 新基准 {V('ceil_tri',2)} ⇎ CA 说明 {V('ceil_tri',3)} ⇎ 规范 {V('ceil_tri',4)}; "
     u"命中句数 {JOIN('ceil_n')} 条, 去重 {JOIN('ceil_distinct')} 种, 宾语集 {JOIN('ceil_vals')}。825 作该句宾语 {JOIN('d825_ceil')} 处——两代都在, 新代 0 处。"
     u"同一条禁令在旧代与中代逐字同在({A_ceil} ⇎ {A_ceilO}), 而第一遍用单空格逐字面搜只在旧代撞到 {V('d825_strict',0)} 处、中代 {V('d825_strict',1)} 处: 中代把 Validity 与 Period 折在两行之间。"
     u"容换行后各代补回 {JOIN('ceil_wrap')} 处, 全句级命中差同样多; 同一通道对天数写法成立: 逐字面 {JOIN('day_num')} ⇎ 容换行 {JOIN('day_num_flex')}, 差 {JOIN('day_wrap')} 处; "
     u"对词组写法亦然: 忽略大小写的逐字面 {JOIN('vp_ci')} ⇎ 容换行 {JOIN('vp_flex_ci')}, 差 {JOIN('vp_wrap')} 处。")

LINE(u'⚖', u"825 这一处的三种身份, 按整句窗口(先把窗口内空白折平)分档: 上限句 {A_ceil} ⇎ 复用期 {A_reuse} ⇎ §1.6 变更表条目名 {A_title}。"
     u"各代窗口数: 上限档 {JOIN('validwin_825')} ⇎ 复用档 {JOIN('reusewin_825')} ⇎ 条目名档 {JOIN('titlewin_825')} ⇎ 第四档 {JOIN('otherwin_825')}, 合计恰为 825 露面处数 {JOIN('lines_825')}。"
     u"398 同构: {JOIN('validwin_398')}⇎{JOIN('reusewin_398')}⇎{JOIN('titlewin_398')}⇎{JOIN('otherwin_398')}, 条目名 {A_398title}; "
     u"397 只在上限档 {JOIN('validwin_397')}。四档划分在全库剩第四档 {V('otherwin_total')} 处(如“MUST be made within 90 days”{JOIN('otherwin_90')}), 分档闭合 {CLOS('win_close', '四档相加差')}。"
     u"同一个数在旧中两代是禁令、在新代只剩史料与复用期——判它属于哪一档只能读整句窗口, 读行号判不出来。")

LINE(u'🔁', u"天数值域各一份: 旧基准 {V('day_set',0)} ⇎ 中基准 {V('day_set',1)} ⇎ 新基准 {V('day_set',2)} ⇎ CA 说明 {V('day_set',3)} ⇎ 规范 {V('day_set',4)}, 各 {JOIN('day_set_n')} 个不同值。"
     u"新代比前两代多出 {V('set_only_F')}: ≤10 天的短证 {A_10day} 与根 CA 的 2922/9132 天 {A_root}; CA 说明独有 {V('set_only_N')}(6 天可选、45 天计划、47 天归给“行业规则”), 两家只共用 {V('set_shared_NF')}。"
     u"45 与 47 作天数在三份在库基准要求里出现 {V('num_45_in_brs')}⇎{V('num_47_in_brs')} 次——CA 说明引的那个上限不在库里任何一份基准要求里。"
     u"写法三档相加校住全数: 连字 {JOIN('day_hyph')} + 空格 {JOIN('day_spac')} + 单数 {JOIN('day_sing')} = 逐字面 {JOIN('day_num')}(差 {CLOS4('day_num_close', '三档相加差')}); "
     u"词族 {JOIN('day_word')} 个 day/days 去掉带数的 {JOIN('day_num')} 个, 余 {JOIN('day_free')} 处不定时长用法。")

LINE(u'🧪', u"CA 说明把同一句话写三遍: {A_90} ⇎ {A_6} ⇎ {A_47} ⇎ {A_45}。逐句在壳里 {V('shell_all')} 份 ⇎ 去壳面内 {V('face_all')} 份, "
     u"每句恰多 {V('dup_gap')} 份(差额种类 {V('dup_kinds')} 种)——多出的两份是 meta name=description 与 meta property=og:description, 剥壳时随整枚标签一起删。"
     u"天数亦如此: 壳内 {V('day_shell')} 个 ⇎ 面内 {V('day_face')} 个, 一枚 meta 描述里就有 {V('day_meta')} 个, 壳面差恰为 2×{V('day_meta')}(闭合 {CLOS('day_shell_close', '壳面天数闭合')})。"
     u"于是“90 ⇎ 6 ⇎ 45 ⇎ 47”在正文里说一遍, 在分享卡片里说两遍; 去壳的量法读数少一半, 少的那一半正是搜索引擎与聊天软件拿到的那一半。")

LINE(u'⛓', u"同一个东西四套叫法: 大写 Validity Period 字面 {JOIN('vp_caps')} 处 ⇎ 小写 {JOIN('vp_low')} 处 ⇎ 忽略大小写 {JOIN('vp_ci')} 处, 两档相加与忽略档差 {CLOS4('vp_ci_close', '大小写两档相加')}; "
     u"词根 validity 全族 {JOIN('validity_stem')} 处, 去掉“validity period”两词组还剩 {JOIN('vp_stem_gap')} 处(validityDate 与 OCSP 语境)。"
     u"CA 说明通篇用 lifetime 而一次也不说 Validity Period: lifetime 忽略档 {JOIN('lifetime_ci')} 处 ⇎ 它 vp_ci {V('vp_ci',3)} 处; 规范用字段名 notBefore ⇎ notAfter: {JOIN('notbefore')} ⇎ {JOIN('notafter')} 处, "
     u"两者之差 {CLOS4('nanb_gap', 'notAfter 减 notBefore')}——规范里 notAfter 多 {V('nanb_gap',4)} 处, 因为“到 notAfter 为止”这类界定只提尾端 {A_R_nb}。")

LINE(u'📏', u"强度词四档并记: 子串 MUST {JOIN('u_must')} ⇎ 词界 {JOIN('kw_must')}(差 {CLOS4('must_sub_gap', '子串比词界多')}: 新基准 {V('must_sub_gap',2)} 处的 MUST 紧贴标点或被排版断开, 词界档不认), "
     u"MUST NOT 子串 {JOIN('u_must_not')} ⇎ 词界 {JOIN('kw_must_not')}(差 {CLOS4('mustnot_sub_gap', 'MUST NOT 两档差')}), 忽略大小写 must {JOIN('must_ci')} ⇎ 小写 must {JOIN('must_l')}, "
     u"SHALL 大写 {JOIN('shall_u')} ⇎ 忽略档 {JOIN('shall_ci')}, will 忽略档 {JOIN('will_ci')}; 全大写四词族 {JOIN('kw_upper')} ⇎ 忽略大小写全族 {JOIN('kw_ci')}。"
     u"同一词族按“历史时间表行 ⇎ 其余正文”分两半(谓词与全量同法): MUST 表行 {JOIN('h_must')} ⇎ 正文 {JOIN('b_must')}, 两半相加减全量 {CLOS4('h_must_close', 'MUST 两半闭合')}; "
     u"SHALL 表行 {JOIN('h_shall')} ⇎ 正文 {JOIN('b_shall')}, 差 {CLOS4('h_shall_close', 'SHALL 两半闭合')}; 表行只占 {JOIN('hist_n')} 行 ⇎ {JOIN('hist_chars')} 字。"
     u"CA 说明全大写强度词 {V('kw_upper',3)} 处而 will {V('will_ci',3)} 处: 它把义务写成“行业规则将要求”, 不写 MUST。")

LINE(u'🗓', u"规范这一份不答“多久”, 只答“怎么写”: 带数的天数 {V('day_num',4)} 处 ⇎ 上限句 {V('ceil_n',4)} 条 ⇎ 大写 Validity Period {V('vp_caps',4)} 处。"
     u"它说两套时间类型: UTCTime {V('ts_utctime',4)} 处 ⇎ GeneralizedTime {V('ts_generalizedtime',4)} 处, 另四份各 {V('ts_non_R')}⇎{V('gt_non_R')} 处; "
     u"两种 ASN.1 记法枚数 YYMMDDHHMMSSZ {V('ts_yymmddhhmmssz',4)} ⇎ YYYYMMDDHHMMSSZ {V('ts_yyyymmddhhmmssz',4)}; 分界见 {A_R_utc} 与 {A_R_gen}: "
     u"年 2049 {V('y2049',4)} 处 ⇎ 2050 {V('y2050',4)} 处——两位年只能表达到 2049, 越过它必须换 GeneralizedTime。"
     u"库里日期写法三档: ISO {JOIN('iso_date')} ⇎ 美式月日年 {JOIN('us_date')} ⇎ “月 年” {JOIN('month_year')}; CA 说明的正文用第三种, 一年只 {V('month_year',3)} 处。")

LINE(u'🧾', u"体例与自我标注: “Section 数字”引用 {JOIN('sec_cite')} 处 ⇎ 小写 section {JOIN('sec_cite_low')} 处; 章节号行 {JOIN('sec_head')} 行 ⇎ 去重 {JOIN('sec_head_d')} 个。"
     u"RFC 引用集 {JOIN('rfc_set_n')} 枚, 其中落在规范参考文献里的 {JOIN('rfc_hit_R')} 枚, 未命中 {JOIN('rfc_miss_n')} 枚; 号码 5280 本身各 {JOIN('rfc_n5280')} 处; 2119 各 {JOIN('rfc2119')} 处。"
     u"自我标注: 首现版本号 旧 {V('ver_self',0)} ⇎ 中 {V('ver_self',1)} ⇎ 新 {V('ver_self',2)} ⇎ 规范 {V('ver_self',4)}——规范里那枚 Version 2.0 是 ASN.1 模块版本而非文档版本(“version 数字”共 {V('ver_any',4)} 处), 同形不同物; "
     u"“Baseline Requirements”{JOIN('baseline_reqs')} 处而规范 0 处; “last updated”只在 CA 说明 {V('last_updated',3)} 处; 谈 ASN.1 各 {JOIN('asn1_mod')} 处。")

LINE(u'⇄', u"整行搬运(行长 ≥25 且归一化非空, 行集求交): 旧⇎中 {V('share_TO')} 行 ⇎ 中⇎新 {V('share_OF')} 行 ⇎ 旧⇎新 {V('share_TF')} 行, 三代同现 {V('share_TOF')} 行, 并集 {V('union_TOF')} 行, "
     u"只在本代 旧 {V('only_T')} ⇎ 中 {V('only_O')} ⇎ 新 {V('only_F')} 行; 容斥闭合 {CLOS('tof_close', '三代容斥闭合')}。候选行集大小 {JOIN('lines_ge25')}。"
     u"基准要求与规范之间几乎不共用整行: 旧⇎规范 {V('share_TR')} ⇎ 中⇎规范 {V('share_OR')} ⇎ 新⇎规范 {V('share_FR')} 行, 去重 {V('share_any_R')} 行——内容只是 {A_ca} 这类定义表表头与 {A_incl} 这类范围说明, 不含任何期限数字。"
     u"CA 说明与其余四份整行共用 {V('share_N_any')} 行: 它是唯一一份网页, 行文折成整段, 换行位置与 PDF 面不可能对齐。")

LINE(u'ℒ', u"方法 ⇒ 面对“同一问题五份文书五种答法”, 先问每个答案由哪个句式给出: 本条把上限做成三元组谓词(动词 × have a Validity Period × 数字), "
     u"于是“825 还在不在禁令里”有可判口径({JOIN('d825_ceil')} 处), 而“825 这个词还在不在”是另一回事({JOIN('lines_825')} 处窗口, 分上限/复用/条目名四档)。"
     u"其次把量测自身的失败做成键: 单空格档与容换行档的差({JOIN('ceil_wrap')}⇎{JOIN('day_wrap')}⇎{JOIN('vp_wrap')})逐档登记, 第一遍的漏判因此在库里可复算, 不靠注释解释; "
     u"带壳文档另立壳⇎面两口径, 用“每句恰多 {V('dup_kinds')} 份”把多出来源指认到两枚 meta, 再用天数把这两份坐实({V('day_shell')} 减 {V('day_face')} 等于 2×{V('day_meta')}); "
     u"谓词与全量同法(表行⇎正文两半相加闭合 {V('h_must_close')}⇎{V('h_shall_close')}), 词界与子串两档并记而不择一, 因新基准里两档差 {V('must_sub_gap',2)} 处。")

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 五源各 {JOIN('chars')} 字符, 窗口只能取锚点触到的行; 本条的结论几乎全是跨文书的量: "
     u"上限句集要三份基准并排({V('ceil_distinct',0)}⇎{V('ceil_distinct',1)}⇎{V('ceil_distinct',2)} 种), 壳面差要把同一页读两遍(壳 {V('day_shell')} ⇎ 面 {V('day_face')}), "
     u"分档要读整句窗口而非行(825 三档 {V('validwin_825',0)}⇎{V('reusewin_825',0)}⇎{V('titlewin_825',0)}), 容斥要三份行集全量({V('union_TOF')} 行)。"
     u"尤其“中代那句 825 禁令逐字与旧代同、只是被排版折行”这一条, 任何单源单档量测都看不见——它要单空格档 {V('d825_strict',1)} 处与容换行档 {V('d825_ceil',1)} 处同时成立才读得出来。"
     u"读它请按“这个天数由哪份文书、以哪个句式、在整句还是条目名里给出”来读, 而不是按“少抄了多少原文”。", **{})

assert not MISSING, u'缺占位符: %s' % (sorted(set(MISSING)),)
body = NL.join(LINES)
USED = len(re.findall(u'⟨', body))
ANCH = set(re.findall(u'⟨([^⟨⟩]+)⟩', body))
DIST = len(ANCH)
TAGN = dict((t, len(re.findall(u'⟦%s⟧' % t, body))) for t in TAGS)
CITES = re.findall(u'⟦([' + u''.join(TAGS) + u'])⟧⟨([^⟨⟩]+)⟩', body)
assert len(CITES) == USED, (len(CITES), USED)
assert re.findall(u'⟧⟨⟦', body) == [], u'嵌套发射'
ERR = [x for x in CITES if pnorm(x[1]) not in FAN[IDX[x[0]]]]
HITC = dict((a, tuple(i for i in range(NSRC) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCH if 1 < len(HITC[a]) < NSRC]),
       u'all5': len([a for a in ANCH if len(HITC[a]) == NSRC])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'],
         u'anchor_all5': CLS[u'all5'], u'checks': DIST * NSRC}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all5'] == DIST
for n, v in sorted(AMETA.items()):
    reg(str(v), u"%s('%s')" % (FN, n), TOKV.get(n, n))
for n in AMETA:
    body = body.replace(u'◘%s◙' % n, str(AMETA[n]))
assert u'◘' not in body, u'锚统计量占位符未回填'
for n, v in AMETA.items():
    F[n] = v
DERIV = dump_deriv()
NOTES = dict((k, v[1]) for k, v in K.items())
DERIV[u'0'] = u'+'.join(ZERO)
json.dump(DERIV, io.open(u'corpus/_deriv60.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b60flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms60.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[' + u''.join(TAGS) + u']⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == n]))
                       for c, n in ((u'single', 1), (u'two', 2), (u'three', 3),
                                    (u'four', 4), (u'five', 5))),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
      u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': NSRC, u'flat': F,
      u'closure_keys': [k for k in F if k.endswith(u'close')]}
json.dump(CH, io.open(u'corpus/_b60checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／面内 %d 字符／非空行 %d／上限句 %d 条／天数集 %s)' % (
        os.path.basename(PATH[i]), F[u'bytes'][i], F[u'chars'][i], F[u'nonblank'][i],
        F[u'ceil_n'][i], (u','.join(F[u'day_set'][i]) or u'空')) for i in range(NSRC)) +
    u' (三份 CA/Browser Forum 基准要求的 pdftotext -layout 面, 各配一份 .pdf 原文件与一份 -raw 面; 第四份是 CA 的说明页 HTML, 壳与面并记; 第五份是 RFC 5280 纯文本。'
    u"数字一律从面内现读, 一个都不手填; 抓取时刻与磁盘 mtime、官网是否已挂更新版、页面“last updated”之真伪只在本机或站外成立, 不进门槛)\n")
联结 = (u"；联结不是“同一份数据的两种序列化”, 而是同一张公签 TLS 证书的最长寿命在五份文书里的五种答法: "
        u"上限句宾语 旧 %s ⇎ 中 %s ⇎ 新 %s ⇎ CA 说明 %s ⇎ 规范 %s, "
        u"825 作宾语 %d⇎%d⇎%d⇎%d⇎%d 处而单空格逐字面只撞旧代 %d 处; "
        u"CA 说明另说 90 天默认 ⇎ 6 天可选 ⇎ 2028 年 2 月前降到 45 天, 并把 2029-03-15 起的 47 天归给“行业规则”——"
        u"45 与 47 作天数在三份在库基准要求里 %d⇎%d 次; "
        u"规范不谈时长(带数天数 %d 处)而谈写法: UTCTime %d ⇎ GeneralizedTime %d 处, 两位年止于 2049(%d 处); "
        u"术语四套: Validity Period 大写 %d⇎%d⇎%d⇎%d⇎%d 处 ⇎ lifetime 全库 %d 处 ⇎ notBefore 各 %d⇎%d⇎%d⇎%d⇎%d 处; "
        u"全大写强度词 %d⇎%d⇎%d⇎%d⇎%d 处, 其中落在历史时间表行的 %d⇎%d⇎%d⇎%d⇎%d 处; "
        u"整行共用 三代 %d 行 ⇎ 基准与规范 %d 行 ⇎ CA 说明 %d 行; "
        u"网页那一份同一句在壳里 %s 份 ⇎ 去壳面内 %s 份, 壳内天数 %d ⇎ 面内 %d。\n") % (
    u','.join(F[u'ceil_vals'][0]) or u'无', u','.join(F[u'ceil_vals'][1]) or u'无',
    u','.join(F[u'ceil_vals'][2]) or u'无', u','.join(F[u'ceil_vals'][3]) or u'无',
    u','.join(F[u'ceil_vals'][4]) or u'无',
    F[u'd825_ceil'][0], F[u'd825_ceil'][1], F[u'd825_ceil'][2], F[u'd825_ceil'][3], F[u'd825_ceil'][4],
    F[u'd825_strict'][0], F[u'num_45_in_brs'], F[u'num_47_in_brs'],
    F[u'day_num'][4], F[u'ts_utctime'][4], F[u'ts_generalizedtime'][4], F[u'y2049'][4],
    F[u'vp_caps'][0], F[u'vp_caps'][1], F[u'vp_caps'][2], F[u'vp_caps'][3], F[u'vp_caps'][4],
    sum(F[u'lifetime_ci']), F[u'notbefore'][0], F[u'notbefore'][1], F[u'notbefore'][2],
    F[u'notbefore'][3], F[u'notbefore'][4],
    F[u'kw_upper'][0], F[u'kw_upper'][1], F[u'kw_upper'][2], F[u'kw_upper'][3], F[u'kw_upper'][4],
    F[u'h_must'][0], F[u'h_must'][1], F[u'h_must'][2], F[u'h_must'][3], F[u'h_must'][4],
    F[u'share_TOF'], F[u'share_any_R'], F[u'share_N_any'],
    u','.join(str(x) for x in F[u'shell_all']), u','.join(str(x) for x in F[u'face_all']),
    F[u'day_shell'], F[u'day_face'])
title = (u'# B60 同一张公签 TLS 证书最长能活多久，五份文书五种答法：825 天 ⇎ 398 与 397 天 ⇎ 只剩史料 ⇎ 90／6／45 天 ⇎ 只谈写法（上限句 %d⇎%d⇎%d 条，%d 处被排版折行）\n' % (
    F[u'ceil_n'][0], F[u'ceil_n'][1], F[u'ceil_n'][2], sum(F[u'ceil_wrap'])))
text = (title + srcline + 联结 +
        u'tags: 上限句三元组谓词 单空格⇎容换行两档并记 整句窗口四档分类(上限⇎复用⇎条目名⇎其他) 天数三档相加闭合 '
        u'壳⇎面两口径 术语四叫法 强度词词界⇎子串⇎表行两半闭合 只写时刻不写时长 整行容斥 同形不同物版本号 '
        u'锚归属由正文现推 闭合账 标量 %d⇎清单 %d 项\n' % (F[u'scalar_clos_n'], F[u'list_clos_n']) +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill60.py 从 corpus/_b60checks.json 与 corpus/_deriv60.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两至四源 %d ⇎ 五源 %d ⇎ 错配 %d ｜ 池内取用 %d／池 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all5'], len(ERR), CH[u'pool_used'], F[u'pool_n']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(F)))
print(u'闭合键 %d 项 ⇎ 非零 %d ｜ 上限句 %s ⇎ 825 作宾语 %s ⇎ 单空格 %s' % (
    F[u'scalar_clos_n'], len([k for k in F[u'scalar_clos_list'] if F[k] != 0]),
    F[u'ceil_n'], F[u'd825_ceil'], F[u'd825_strict']))
print(u'分档闭合 %d ｜ 壳面天数 %d⇎%d ⇎ meta %d ｜ 整行 三代 %d ⇎ 与规范 %d ⇎ CA %d' % (
    F[u'win_close'], F[u'day_shell'], F[u'day_face'], F[u'day_meta'],
    F[u'share_TOF'], F[u'share_any_R'], F[u'share_N_any']))
MEASP = u'corpus/_b60meas.json'
if os.path.exists(MEASP):
    M = json.load(io.open(MEASP, encoding='utf-8'))
    PL = tuple(M.pop(u'_plain_idx', [0, 1, 2, 4]))
    TIE = []
    for k in sorted(M):
        if k not in F:
            TIE.append((k, u'建条目侧无此键'))
            continue
        got = [F[k][i] for i in PL] if isinstance(F[k], list) and len(F[k]) == NSRC else F[k]
        if got != M[k]:
            TIE.append((k, u'建=%s 采=%s' % (got, M[k])))
    print(u'两侧对账(四份纯文本面): 共有键 %d ／ 不符 %d ｜ %s' % (len(M), len(TIE), TIE[:6]))
else:
    print(u'两侧对账: 无 corpus/_b60meas.json(采集侧未跑)')
