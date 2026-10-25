# -*- coding: utf-8 -*-
"""B59 采集侧(第一遍): 四份口令规范的结构化现量, 产 corpus/_b59meas.json 供 _mkB59.py 逐量对账。
⟪T⟧=NIST SP 800-63B-3(2017) ⇎ ⟪O⟧=OWASP ASVS 4.0 §V2(Markdown) ⇎ ⟪F⟧=NIST SP 800-63B-4(2025 初稿)
⇎ ⟪N⟧=OWASP Authentication Cheat Sheet。
定义以建条目侧为准(剥壳次序、行口径、末格口径), 本遍只换算法:
剥壳用 '<' 游标分段器(建条目侧用三条 re.sub), 计数用 str.find 游标(建条目侧用 findall/count),
强度词用字母边界正则逐词扫四遍(建条目侧一次切词进 Counter 回查), password 族反过来用 Counter 汇总,
ASVS 表格按从右数第几格取(建条目侧从左数), 章节号按行首 token 的段数与全数字判(建条目侧用 (?m) 正则)。
两条口径差单列为键: 只删标签 ⇎ 连 script/style 内容一起删(js_gap), 原文件行 ⇎ 转码后行(rlines)。"""
import io, os, re, json, hashlib
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
NL = u'\n'
PATH = [u'corpus/raw/pwd/nist_63b_rev3.html', u'corpus/raw/pwd/asvs_40_v2.md',
        u'corpus/raw/pwd/nist_63b_rev4.html', u'corpus/raw/pwd/owasp_auth_cs.html']
TAGS = [u'T', u'O', u'F', u'N']
ENT = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'), (u'&sect;', u'S'),
       (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'), (u'&#215;', u'x'),
       (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"), (u'&mdash;', u'-'), (u'&ndash;', u'-'),
       (u'&deg;', u'deg'), (u'&infin;', u'inf')]
UNI = [(u'\u00a0', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
       (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->'), (u'–', u'-')]
WORDNUM = {u'six': 6, u'eight': 8, u'twelve': 12, u'fifteen': 15, u'four': 4, u'ten': 10,
           u'twenty': 20, u'sixty-four': 64, u'one hundred': 100}
NORMW = [u'SHALL', u'SHOULD', u'MAY', u'MUST']
SPECIAL = (u'8 characters', u'eight characters', u'12 characters', u'15 characters', u'64 characters',
           u'128 characters', u'memorized secret', u'blocklist', u'composition rules',
           u'pages.nist.gov', u'SP8210', u'superseded', u'initial public draft', u'2.1.1',
           u'Memorized Secrets', u'112 bits', u'multi-factor', u'copy and paste', u'single-factor')


def cut(s, br=u' '):
    """'<' 游标分段器: 注释 -> <br> -> 标签, 与建条目侧的三条 re.sub 同定义不同实现.
    '<' 无闭合与 '<>' 两种情形都保留 '<', 因为 (?s)<[^>]+> 至少要吃一个字符."""
    out = []
    i, n = 0, len(s)
    while i < n:
        k = s.find(u'<', i)
        if k < 0:
            out.append(s[i:])
            break
        out.append(s[i:k])
        if s.startswith(u'<!--', k):
            j = s.find(u'-->', k + 4)
            i = n if j < 0 else j + 3
            continue
        j = s.find(u'>', k + 1)
        if j < 0 or j == k + 1:
            out.append(u'<')
            i = k + 1
            continue
        if s[k + 1:k + 3].lower() == u'br':
            out.append(br)
        i = j + 1
    s = u''.join(out)
    for a, b in ENT + UNI:
        s = s.replace(a, b)
    return re.sub(u'[ \t]+', u' ', s).strip()


def occ(hay, needle):
    c, i = 0, hay.find(needle)
    while i >= 0:
        c += 1
        i = hay.find(needle, i + len(needle))
    return c


RAW = [io.open(p, encoding=u'utf-8', errors=u'replace').read() for p in PATH]


def unscript(s):
    return re.sub(u'(?is)<(script|style)[^>]*>.*?</(script|style)>', u'', s)


RAWNS = [unscript(r) for r in RAW]
TXT = [cut(RAWNS[i]) for i in range(4)]
TXTF = [cut(RAW[i]) for i in range(4)]
LST = [[cut(l) for l in RAWNS[i].split(NL)] for i in range(4)]
RL = [r.split(NL) for r in RAW]
F = {}


def four(name, f):
    F[name] = [f(k) for k in range(4)]


def lb(word):
    """字母边界: 与建条目侧按非字母切词等价, 但不走 Counter."""
    return u'(?<![A-Za-z])' + word + u'(?![A-Za-z])'


# ---------- 形状档 ----------
four(u'bytes', lambda i: os.path.getsize(PATH[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'chars_untagged', lambda i: len(TXTF[i]))
four(u'js_gap', lambda i: len(TXTF[i]) - len(TXT[i]))
four(u'script_tags', lambda i: occ(RAW[i].lower(), u'<script'))
four(u'style_tags', lambda i: occ(RAW[i].lower(), u'<style'))
four(u'lt_tags', lambda i: occ(RAW[i], u'<'))
four(u'lines', lambda i: occ(RAW[i], NL))
four(u'nonblank', lambda i: len([l for l in RL[i] if l.strip()]))
four(u'rlines', lambda i: len(LST[i]) - 1)
four(u'rnonblank', lambda i: len([l for l in LST[i] if l]))
four(u'tabs', lambda i: occ(TXT[i], u'\t'))
four(u'nonascii', lambda i: len([c for c in RAW[i] if ord(c) > 127]))
four(u'bom', lambda i: 1 if RAW[i][:1] == u'\ufeff' else 0)
four(u'maxlen', lambda i: max([len(l) for l in LST[i]]))
four(u'sha16', lambda i: hashlib.sha256(io.open(PATH[i], 'rb').read()).hexdigest()[:16])
four(u'pipe_cells', lambda i: occ(RAW[i], u'|'))
four(u'bold_marks', lambda i: occ(RAW[i], u'**'))
F[u'bold_marks'] = [v // 2 for v in F[u'bold_marks']]
four(u'md_links', lambda i: occ(RAW[i], u'](http'))
four(u'table_tags', lambda i: occ(RAW[i].lower(), u'<table'))
four(u'tr_rows', lambda i: occ(RAW[i].lower(), u'<tr'))
four(u'ent_all', lambda i: len(re.findall(u'&[a-zA-Z#0-9]+;', RAW[i])))

# ---------- 门槛数字: 数字写法 ⇎ 英文词写法 ----------
RE_CTX = re.compile(u'(?i)\\b(\\d{1,3}|six|eight|twelve|fifteen|four|ten)[- ]characters?\\b')


def ctx_vals(i):
    return [(int(t), True) if t.isdigit() else (WORDNUM[t.lower()], False)
            for t in RE_CTX.findall(TXT[i])]


def ctx_nums(i):
    return [v for v, d in ctx_vals(i)]


four(u'th_digit8', lambda i: occ(TXT[i], u'8 characters'))
four(u'th_word_eight', lambda i: occ(TXT[i], u'eight characters'))
four(u'th_digit12', lambda i: occ(TXT[i], u'12 characters'))
four(u'th_digit15', lambda i: occ(TXT[i], u'15 characters'))
four(u'th_digit64', lambda i: occ(TXT[i], u'64 characters'))
four(u'th_digit128', lambda i: occ(TXT[i], u'128 characters'))
four(u'th_digit6', lambda i: occ(TXT[i], u'6 characters'))
four(u'ctx_occ', lambda i: len(ctx_vals(i)))
four(u'ctx_distinct', lambda i: len(set(ctx_nums(i))))
four(u'ctx_set', lambda i: sorted(set(ctx_nums(i))))
four(u'ctx_word_form', lambda i: len([x for x in ctx_vals(i) if not x[1]]))
F[u'ctx_digit_form'] = [F[u'ctx_occ'][i] - F[u'ctx_word_form'][i] for i in range(4)]
F[u'ctx_form_close'] = [F[u'ctx_word_form'][i] + F[u'ctx_digit_form'][i] - F[u'ctx_occ'][i]
                        for i in range(4)]
F[u'ctx_eight_docs'] = len([i for i in range(4) if u'eight characters' in TXT[i]])
F[u'ctx_d8_docs'] = len([i for i in range(4) if F[u'th_digit8'][i] > 0])
F[u'ctx_815_docs'] = len([i for i in range(4) if 8 in ctx_nums(i) and 15 in ctx_nums(i)])
F[u'ctx_12_only'] = len([i for i in range(4) if 12 in ctx_nums(i)])
F[u'ctx_128_only'] = len([i for i in range(4) if 128 in ctx_nums(i)])
four(u'th_line_norm', lambda i: len([l for l in LST[i]
                                     if re.search(u'(?i)\\d+[- ]characters?', l) and u'SHALL' in l]))
four(u'th_line_bare', lambda i: len([l for l in LST[i]
                                     if re.search(u'(?i)\\d+[- ]characters?', l)
                                     and not any(w in l for w in NORMW)]))

# ---------- 强度词: 逐词四次边界正则扫描 ----------
for W in NORMW:
    four(u'kw_%s_u' % W.lower(), lambda i, W=W: len(re.findall(lb(W), TXT[i])))
    four(u'kw_%s_l' % W.lower(), lambda i, W=W: len(re.findall(lb(W.lower()), TXT[i])))
    four(u'kw_%s_t' % W.lower(), lambda i, W=W: len(re.findall(lb(W[0] + W[1:].lower()), TXT[i])))
    four(u'kw_%s_ci' % W.lower(), lambda i, W=W: len(re.findall(u'(?i)' + lb(W), TXT[i])))
F[u'kw_close'] = dict((W, [F[u'kw_%s_u' % W.lower()][i] + F[u'kw_%s_l' % W.lower()][i]
                           + F[u'kw_%s_t' % W.lower()][i] - F[u'kw_%s_ci' % W.lower()][i]
                           for i in range(4)]) for W in NORMW)
F[u'kw_close_sum'] = sum(sum(v) for v in F[u'kw_close'].values())
F[u'must_upper_all4'] = sum(F[u'kw_must_u'])
F[u'kw_upper_total'] = [sum(F[u'kw_%s_u' % W.lower()][i] for W in NORMW) for i in range(4)]
F[u'kw_ci_total'] = [sum(F[u'kw_%s_ci' % W.lower()][i] for W in NORMW) for i in range(4)]
F[u'kw_gap'] = [F[u'kw_ci_total'][i] - F[u'kw_upper_total'][i] for i in range(4)]
four(u'kw_shallnot_u', lambda i: occ(TXT[i], u'SHALL NOT'))
four(u'kw_shallnot_ci', lambda i: occ(TXT[i].lower(), u'shall not'))
four(u'kw_shouldnot_u', lambda i: occ(TXT[i], u'SHOULD NOT'))
four(u'kw_shouldnot_ci', lambda i: occ(TXT[i].lower(), u'should not'))
F[u'kw_shallnot_gap'] = [F[u'kw_shallnot_ci'][i] - F[u'kw_shallnot_u'][i] for i in range(4)]
F[u'kw_shouldnot_gap'] = [F[u'kw_shouldnot_ci'][i] - F[u'kw_shouldnot_u'][i] for i in range(4)]

# ---------- 术语换代: password 族按 Counter 汇总 ----------
CNT = [Counter(re.split(u'[^0-9A-Za-z_]+', TXT[i])) for i in range(4)]
four(u'tm_memorized', lambda i: len(re.findall(u'(?i)memorized secret', TXT[i])))
four(u'tm_memorized_caps', lambda i: occ(TXT[i], u'Memorized Secrets'))
four(u'tm_pw_sing', lambda i: sum(v for k, v in CNT[i].items() if k.lower() == u'password'))
four(u'tm_pw_plural', lambda i: sum(v for k, v in CNT[i].items() if k.lower() == u'passwords'))
four(u'tm_pw_any', lambda i: F[u'tm_pw_sing'][i] + F[u'tm_pw_plural'][i])
four(u'tm_bridge', lambda i: len(re.findall(u'(?i)called .{0,3}Memorized Secrets', TXT[i])))
four(u'tm_defline', lambda i: len([l for l in LST[i] if u'intended to be memorized' in l]))
F[u'tm_close'] = [F[u'tm_pw_sing'][i] + F[u'tm_pw_plural'][i] - F[u'tm_pw_any'][i] for i in range(4)]

# ---------- 机制词 ----------
MECH = ((u'blocklist', u'(?i)block\\s?-?list'), (u'breach', u'(?i)breach'),
        (u'composition', u'(?i)composition rules'), (u'hint', u'(?i)\\bhint'),
        (u'copypaste', u'(?i)copy and paste'), (u'ratelimit', u'(?i)rate.?limit|throttl'),
        (u'lockout', u'(?i)\\block\\w*'), (u'periodic', u'(?i)periodic|regular change'),
        (u'entropy', u'(?i)entropy'), (u'multifactor', u'(?i)\\bmfa\\b|multi.?factor'),
        (u'arbitrary', u'(?i)arbitrary'), (u'forcechange', u'(?i)force a change'))
for k, p in MECH:
    four(u'mc_%s' % k, lambda i, p=p: len(re.findall(p, TXT[i])))
    four(u'mc_%s_lines' % k, lambda i, p=p: len([l for l in LST[i] if re.search(p, l)]))
F[u'comp_shouldnot'] = [len([l for l in LST[i] if u'composition rules' in l and u'SHOULD NOT' in l])
                        for i in range(4)]
F[u'comp_shallnot'] = [len([l for l in LST[i] if u'composition rules' in l and u'SHALL NOT' in l])
                       for i in range(4)]
F[u'comp_norm_free'] = [F[u'mc_composition_lines'][i] - F[u'comp_shouldnot'][i]
                        - F[u'comp_shallnot'][i] for i in range(4)]
F[u'blk_def_lines'] = len([l for l in LST[2] if u'blocklist' in l and u'SHALL' in l])
LOW = [t.lower() for t in TXT]
four(u'bl_blacklist', lambda i: occ(LOW[i], u'blacklist'))
four(u'bl_spaced', lambda i: len(re.findall(u'(?i)black[ \t]+list', TXT[i])))
four(u'bl_black', lambda i: len(re.findall(u'(?i)black[ \t-]?list', TXT[i])))
four(u'bl_word_any', lambda i: len(re.findall(u'(?i)(?:block|black)[ \t-]?list', TXT[i])))
F[u'bl_word_close'] = [F[u'mc_blocklist'][i] + F[u'bl_black'][i] - F[u'bl_word_any'][i]
                       for i in range(4)]
F[u'bl_black_close'] = [F[u'bl_blacklist'][i] + F[u'bl_spaced'][i] - F[u'bl_black'][i]
                        for i in range(4)]

# ---------- 引用形态与谱系 ----------
CITE = ((u'url_nist', u'pages\\.nist\\.gov'), (u'spaced', u'NIST SP 800-63'),
        (u'unspaced', u'SP800-63B'), (u'rev4num', u'800-63-4'), (u'rev3num', u'800-63-3'),
        (u'superseded', u'(?i)superseded'), (u'draftself', u'(?i)initial public draft'),
        (u'http_any', u'https?://'))
for k, p in CITE:
    four(u'cite_%s' % k, lambda i, p=p: len(re.findall(p, TXT[i])))
F[u'cite_63b_docs'] = len([i for i in range(4) if re.search(u'(?i)800-63b', TXT[i])])
F[u'cite_forms'] = len([x for x in (F[u'cite_url_nist'][1], F[u'cite_unspaced'][3],
                                    F[u'cite_spaced'][0]) if x])

# ---------- 章节号与 ASVS 末格 ----------
def heads(i):
    """行首 token 的段数与全数字判; 建条目侧用 (?m)^\\s*((?:\\d+\\.){2,3}\\d+)\\s.
    编号独占一行也算(\\s 能吃行末换行), 所以只有正文最末一行要求编号后还有词."""
    out = []
    ls = TXT[i].split(NL)
    for j, l in enumerate(ls):
        p = l.split()
        if not p:
            continue
        sg = p[0].split(u'.')
        if 3 <= len(sg) <= 4 and all(x and x.isdigit() for x in sg):
            if len(p) > 1 or j < len(ls) - 1:
                out.append(p[0])
    return out


four(u'sec_head_n', lambda i: len(heads(i)))
HEAD = [set(heads(i)) for i in (0, 2)]
F[u'sec_T_set'] = sorted(HEAD[0])
F[u'sec_F_set'] = sorted(HEAD[1])
F[u'sec_T_n'] = len(HEAD[0])
F[u'sec_F_n'] = len(HEAD[1])
F[u'sec_shared'] = len(HEAD[0] & HEAD[1])
ASVS_ROWS = [l for l in LST[1] if re.match(u'^\\|\\s*\\*\\*2\\.\\d+\\.\\d+\\*\\*', l)]
F[u'asvs_req_rows'] = len(ASVS_ROWS)
F[u'asvs_bold_ids'] = occ(RAW[1], u'**2.')
CELLS = [[c.strip() for c in r.split(u'|')] for r in ASVS_ROWS]
F[u'asvs_row_widths'] = sorted(set(len(c) for c in CELLS))
NUMRE = re.compile(u'^\\d+(\\.\\d+){1,3}$')
F[u'asvs_refs'] = sorted(set(c[-2] for c in CELLS if NUMRE.match(c[-2])))
F[u'asvs_ref_occ'] = len([c[-2] for c in CELLS if NUMRE.match(c[-2])])
F[u'asvs_ref_distinct'] = len(F[u'asvs_refs'])
F[u'asvs_rows_noref'] = F[u'asvs_req_rows'] - F[u'asvs_ref_occ']
F[u'asvs_ref_inT'] = len([x for x in F[u'asvs_refs'] if x in HEAD[0]])
F[u'asvs_ref_inF'] = len([x for x in F[u'asvs_refs'] if x in HEAD[1]])
F[u'asvs_ref_inT_text'] = len([x for x in F[u'asvs_refs'] if x in TXT[0]])
F[u'asvs_ref_inF_text'] = len([x for x in F[u'asvs_refs'] if x in TXT[2]])
F[u'asvs_ref_missT'] = [x for x in F[u'asvs_refs'] if x not in HEAD[0]]
F[u'asvs_ref_missF'] = [x for x in F[u'asvs_refs'] if x not in HEAD[1]]
F[u'asvs_ref_close'] = F[u'asvs_ref_inT'] + len(F[u'asvs_ref_missT']) - F[u'asvs_ref_distinct']
F[u'asvs_tick_cols'] = [len([c for c in CELLS
                             if c[len(c) - 1 - k] == u'\u2713']) for k in (5, 4, 3)]
F[u'asvs_tick_total'] = sum(F[u'asvs_tick_cols'])
F[u'asvs_tick_legend'] = len([l for l in LST[1] if u'\u2713' in l and not l.startswith(u'| **2.')])
F[u'asvs_tick_glyph'] = occ(RAW[1], u'\u2713')
F[u'asvs_tick_close'] = F[u'asvs_tick_total'] + F[u'asvs_tick_legend'] - F[u'asvs_tick_glyph']
F[u'asvs_cwe'] = sorted(set(c[-3] for c in CELLS if c[-3].isdigit()))
F[u'asvs_cwe_distinct'] = len(F[u'asvs_cwe'])
F[u'asvs_url_head'] = len(re.findall(u'pages\\.nist\\.gov/800-63-3', RAW[1]))
F[u'asvs_5112'] = [occ(TXT[i], u'5.1.1.2') for i in range(4)]
F[u'id_211_bold'] = occ(RAW[1], u'**2.1.1**')
F[u'id_211_occ'] = [occ(TXT[i], u'2.1.1') for i in range(4)]
F[u'id_211_docs'] = len([i for i in range(4) if u'2.1.1' in TXT[i]])


def seccites(s):
    """'Sec.' 体例按游标推进: 撞到 'Sec.' 后看下一格是不是数字."""
    n, i, low = 0, s.find(u'Sec.'), s
    while i >= 0:
        j = i + 4
        if j < len(low) and low[j:j + 1] == u' ' and low[j + 1:j + 2].isdigit():
            j += 1
        if j < len(low) and low[j:j + 1].isdigit():
            n += 1
        i = s.find(u'Sec.', i + 4)
    return n


four(u'sec_cite_sec', lambda i: seccites(TXT[i]))
four(u'sec_cite_word', lambda i: len(re.findall(u'(?i)(?<![A-Za-z])Section \\d', TXT[i])))
four(u'sec_cite_any', lambda i: len(re.findall(u'(?i)(?:sec\\.?|section)[ \t]+\\d', TXT[i])))
F[u'sec_cite_close'] = [F[u'sec_cite_sec'][i] + F[u'sec_cite_word'][i] - F[u'sec_cite_any'][i]
                        for i in range(4)]

# ---------- 熵/位 ----------
for b in (u'20', u'32', u'40', u'64', u'112'):
    four(u'bit_%s' % b, lambda i, b=b: occ(TXT[i], b + u' bits'))
four(u'bit_any', lambda i: len(re.findall(u'(?i)\\d+\\s*bits', TXT[i])))
four(u'bit_set', lambda i: sorted(set(m.group(1) for m in re.finditer(u'(?i)(\\d+)\\s*bits', TXT[i]))))
F[u'bit_close'] = [F[u'bit_any'][i] - sum(F[u'bit_%s' % b][i] for b in (u'20', u'32', u'40', u'64', u'112'))
                   for i in range(4)]
F[u'bit_lost'] = sorted(set(F[u'bit_set'][0]) - set(F[u'bit_set'][2]))
F[u'bit_new'] = sorted(set(F[u'bit_set'][2]) - set(F[u'bit_set'][0]))

# ---------- 跨文书整行共用 ----------
def pnorm(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


FAN = [pnorm(TXT[i]) for i in range(4)]
LN = []
for i in range(4):
    seen = {}
    for l in LST[i]:
        x = pnorm(l)
        if len(l) >= 20 and x:
            seen[x] = 1
    LN.append(set(seen))
four(u'lines_ge20', lambda i: len(LN[i]))
for a, b in ((0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3)):
    F[u'share_%s%s' % (TAGS[a], TAGS[b])] = len(LN[a] & LN[b])
F[u'share_all4'] = len(LN[0] & LN[1] & LN[2] & LN[3])
F[u'only_T'] = len(LN[0] - LN[2])
F[u'only_F'] = len(LN[2] - LN[0])
F[u'union_TF'] = len(LN[0] | LN[2])
F[u'share_close_TF'] = F[u'share_TF'] + F[u'only_T'] + F[u'only_F'] - F[u'union_TF']
F[u'only_O'] = len(LN[1] - LN[3])
F[u'only_N'] = len(LN[3] - LN[1])
F[u'union_ON'] = len(LN[1] | LN[3])
F[u'share_close_ON'] = F[u'share_ON'] + F[u'only_O'] + F[u'only_N'] - F[u'union_ON']
F[u'carry_sub_TF'] = len([l for l in LN[0] if l in FAN[2]])
F[u'carry_sub_FT'] = len([l for l in LN[2] if l in FAN[0]])
F[u'carry_sub_overlap'] = F[u'carry_sub_TF'] + F[u'carry_sub_FT']
F[u'carry_caliber_gap'] = F[u'carry_sub_overlap'] - F[u'share_TF']

# ---------- 锚池 ----------
POOL = []
SEEN = {}
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if not pnorm(l):
            continue
        if (t, l) not in SEEN:
            SEEN[(t, l)] = 1
            POOL.append((t, l))
POOL.sort()
F[u'pool_n'] = len(POOL)
four(u'pool_tag_n', lambda i: len([p for p in POOL if p[0] == TAGS[i]]))
CRS = {}
for t, x in POOL:
    n = 0
    px = pnorm(x)
    for k in range(4):
        n += 1 if px in FAN[k] else 0
    CRS[(t, x)] = n
for n in (1, 2, 3, 4):
    F[u'pool_%d' % n] = len([p for p in POOL if CRS[p] == n])
F[u'pool_tiers'] = [F[u'pool_1'], F[u'pool_2'], F[u'pool_3'], F[u'pool_4']]
F[u'pool_close'] = sum(F[u'pool_tiers']) - F[u'pool_n']
F[u'pool_maxlen'] = max([len(p[1]) for p in POOL])

json.dump(F, io.open(u'corpus/_b59meas.json', u'w', encoding=u'utf-8'), ensure_ascii=False,
          indent=1, sort_keys=True)
print(u'采集侧 %d 键 ｜ 形状 %s ⇎ %s ⇎ %s ⇎ %s 字符 ｜ js_gap %s' % (
    len(F), F[u'chars'][0], F[u'chars'][1], F[u'chars'][2], F[u'chars'][3], F[u'js_gap']))
print(u'原文件行 %s ⇎ 转码行 %s ｜ 门槛数字集 %s ⇎ %s ｜ 词面(草案) %d ⇎ 数字 %d' % (
    F[u'lines'], F[u'rlines'], F[u'ctx_set'][0], F[u'ctx_set'][2],
    F[u'ctx_word_form'][2], F[u'ctx_digit_form'][2]))
print(u'ASVS 条款号 %d 枚/%d 不同 ⇎ 命中旧 %d ⇎ 命中草案 %d ｜ 勾选 %s/%s ｜ 行宽 %s' % (
    F[u'asvs_ref_occ'], F[u'asvs_ref_distinct'], F[u'asvs_ref_inT'], F[u'asvs_ref_inF'],
    F[u'asvs_tick_cols'], F[u'asvs_tick_total'], F[u'asvs_row_widths']))
print(u'强度词 SHALL %s ⇎ MUST 大写 %s ⇎ must 小写 %s ｜ password 单/复 %s/%s' % (
    F[u'kw_shall_u'], F[u'kw_must_u'], F[u'kw_must_l'], F[u'tm_pw_sing'], F[u'tm_pw_plural']))
print(u'整行共用 T⇎F %d ⇎ O⇎N %d ｜ 四份 %d ｜ 池 %d 分层 %s ⇎ 每标签 %s' % (
    F[u'share_TF'], F[u'share_ON'], F[u'share_all4'], F[u'pool_n'], F[u'pool_tiers'],
    F[u'pool_tag_n']))
