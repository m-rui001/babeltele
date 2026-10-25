# -*- coding: utf-8 -*-
"""B59 建条目(第二遍现算, 四源): T = raw/pwd/nist_63b_rev3.html (NIST SP 800-63B 修订 3, 2017)
⇎ O = asvs_40_v2.md (OWASP ASVS 4.0 §V2) ⇎ F = nist_63b_rev4.html (SP 800-63B 修订 4, 2025 初稿)
⇎ N = owasp_auth_cs.html (OWASP Authentication Cheat Sheet)。工程技术学科, 四份一手文书。
主轴: 同一个口令该多长, 四份给了四个数——8 ⇎ 12 ⇎ 15(单因子) ⇎ 8 与 15 并列; 且草案把 8 写成英文单词
"eight characters"(数字写法 0 处), 备忘单把这两个数一并归给 "NIST SP800-63B"(该串命中两份在库文书)。
配套轴: ASVS 的 48 枚 NIST 条款号在旧规范里 48/48 逐字命中、在草案里 0/48; 术语换代 memorized secret⇎password;
强度词大写/小写/首字母三账(MUST 大写四份全 0, 小写 6⇎2⇎16⇎6); 同一条禁令从 SHOULD NOT 升为 SHALL NOT;
blocklist 整套机制只出现在草案; 112/32/64/20 bits 的熵账里草案删 20 增 40。
第二遍的独立性: 强度词换成"整篇一次性切词进 Counter 再回查四种写法"(pick 逐词四次正则扫描),
门槛数字换成 str.count 子句柄(pick 用 findall 计数), 引用命中换成"末格集合与整篇 pnorm 求交"(pick 逐枚 in 判断),
句子档与体裁档是本遍新增; 每个共有量在末尾与 _pick59.py 逐量对账(不符只报不停机)。
抓取时刻与磁盘 mtime、草案是否已定稿、备忘单引的到底是哪一版只在本机或站外成立, 不进门槛。"""
import io, os, re, sys, json, hashlib
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
C = u'corpus'
NL = u'\n'
ENTRY = u'%s/babeltele/B59_one_password_four_answers.md' % C
M = json.load(io.open(u'corpus/_b59meas.json', encoding='utf-8'))
PATH = [u'corpus/raw/pwd/nist_63b_rev3.html', u'corpus/raw/pwd/asvs_40_v2.md',
        u'corpus/raw/pwd/nist_63b_rev4.html', u'corpus/raw/pwd/owasp_auth_cs.html']
TAGS = [u'T', u'O', u'F', u'N']
LB = dict(zip(TAGS, [u'旧规范', u'验证标准', u'新草案', u'备忘单']))
RD = lambda p: io.open(p, encoding='utf-8', errors='replace').read()
IDX = dict((t, i) for i, t in enumerate(TAGS))

# --- SCAN BEGIN --- (corpus/_wire59.py 把这一段机械切进 audit.py::_b59_scan)
ENT = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'), (u'&sect;', u'S'),
       (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'), (u'&#215;', u'x'),
       (u'&rarr;', u'->'), (u'&rsquo;', u"'"), (u'&lsquo;', u"'"), (u'&mdash;', u'-'), (u'&ndash;', u'-'),
       (u'&deg;', u'deg'), (u'&infin;', u'inf')]
UNI = [(u' ', u' '), (u'−', u'-'), (u'–', u'-'), (u'—', u'-'), (u'×', u'x'),
       (u'‘', u"'"), (u'’', u"'"), (u'“', u'"'), (u'”', u'"'), (u'→', u'->'), (u'–', u'-')]
WORDNUM = {u'six': 6, u'eight': 8, u'twelve': 12, u'fifteen': 15, u'four': 4, u'ten': 10,
           u'twenty': 20, u'sixty-four': 64, u'one hundred': 100}
NORMW = [u'SHALL', u'SHOULD', u'MAY', u'MUST']


def unscript(s):
    return re.sub(u'(?is)<(script|style)\\b.*?</\\1>', u'', s)


def strip(s, br=u' '):
    """转码层: 注释 -> <br> -> 标签 -> 实体 -> unicode 折 ASCII -> 并空白(颠倒会吃掉含 &lt; 的整行)."""
    s = re.sub(u'(?s)<!--.*?-->', u'', s)
    s = re.sub(u'(?is)<br[^>]*>', br, s)
    s = re.sub(u'(?s)<[^>]+>', u'', s)
    for a, b in ENT + UNI:
        s = s.replace(a, b)
    return re.sub(u'[ \t]+', u' ', s).strip()


RAW = [RD(p) for p in PATH]
RAWNS = [unscript(r) for r in RAW]
TXT = [strip(RAWNS[i]) for i in range(4)]
TXTF = [strip(RAW[i]) for i in range(4)]
LST = [[strip(l) for l in RAWNS[i].split(NL)] for i in range(4)]
RL = [RAW[i].split(NL) for i in range(4)]
F = {}
NN4 = 4


def four(name, f):
    F[name] = [f(k) for k in range(NN4)]


# ---------- 形状档 ----------
four(u'bytes', lambda i: os.path.getsize(PATH[i]))
four(u'chars', lambda i: len(TXT[i]))
four(u'chars_untagged', lambda i: len(TXTF[i]))
four(u'js_gap', lambda i: len(TXTF[i]) - len(TXT[i]))
four(u'script_tags', lambda i: len(re.findall(u'(?i)<script', RAW[i])))
four(u'style_tags', lambda i: len(re.findall(u'(?i)<style', RAW[i])))
four(u'lt_tags', lambda i: RAW[i].count(u'<'))
four(u'lines', lambda i: len(RL[i]) - 1)
four(u'nonblank', lambda i: len([l for l in RL[i] if l.strip()]))
four(u'rlines', lambda i: len(LST[i]) - 1)
four(u'rnonblank', lambda i: len([l for l in LST[i] if l]))
four(u'tabs', lambda i: TXT[i].count(u'\t'))
four(u'nonascii', lambda i: len([c for c in RAW[i] if ord(c) > 127]))
four(u'bom', lambda i: 1 if RAW[i][:1] == u'﻿' else 0)
four(u'maxlen', lambda i: max(len(l) for l in LST[i]))
four(u'sha16', lambda i: hashlib.sha256(io.open(PATH[i], 'rb').read()).hexdigest()[:16])
four(u'pipe_cells', lambda i: RAW[i].count(u'|'))
four(u'bold_marks', lambda i: RAW[i].count(u'**') // 2)
four(u'md_links', lambda i: len(re.findall(u'\\]\\(http', RAW[i])))
four(u'table_tags', lambda i: len(re.findall(u'(?is)<table', RAW[i])))
four(u'tr_rows', lambda i: len(re.findall(u'(?is)<tr', RAW[i])))
four(u'ent_all', lambda i: len(re.findall(u'&[a-zA-Z#0-9]+;', RAW[i])))
F[u'pipe_vs_row'] = F[u'pipe_cells'][1] - (F[u'tr_rows'][0] + F[u'tr_rows'][2])
F[u'sig_distinct'] = len(set(F[u'sha16']))

# ---------- 门槛数字: 数字写法 ⇎ 英文词写法 ----------
RE_CTX = re.compile(u'(?i)\\b(\\d{1,3}|six|eight|twelve|fifteen|four|ten)[- ]characters?\\b')


def ctx_vals(i):
    out = []
    for m in RE_CTX.finditer(TXT[i]):
        t = m.group(1).lower()
        out.append(int(t) if t.isdigit() else WORDNUM[t])
    return out


four(u'th_digit8', lambda i: TXT[i].count(u'8 characters'))
four(u'th_word_eight', lambda i: TXT[i].count(u'eight characters'))
four(u'th_digit12', lambda i: TXT[i].count(u'12 characters'))
four(u'th_digit15', lambda i: TXT[i].count(u'15 characters'))
four(u'th_digit64', lambda i: TXT[i].count(u'64 characters'))
four(u'th_digit128', lambda i: TXT[i].count(u'128 characters'))
four(u'th_digit6', lambda i: TXT[i].count(u'6 characters'))
four(u'ctx_occ', lambda i: len(ctx_vals(i)))
four(u'ctx_distinct', lambda i: len(set(ctx_vals(i))))
four(u'ctx_set', lambda i: sorted(set(ctx_vals(i))))
four(u'ctx_word_form', lambda i: len([x for x in RE_CTX.findall(TXT[i]) if not x.isdigit()]))
four(u'ctx_digit_form', lambda i: len([x for x in RE_CTX.findall(TXT[i]) if x.isdigit()]))
F[u'ctx_form_close'] = [F[u'ctx_word_form'][i] + F[u'ctx_digit_form'][i] - F[u'ctx_occ'][i]
                        for i in range(4)]
F[u'ctx_eight_docs'] = len([i for i in range(4) if u'eight characters' in TXT[i]])
F[u'ctx_d8_docs'] = len([i for i in range(4) if F[u'th_digit8'][i]])
F[u'ctx_815_docs'] = len([i for i in range(4) if 8 in ctx_vals(i) and 15 in ctx_vals(i)])
F[u'ctx_12_only'] = len([i for i in range(4) if 12 in ctx_vals(i)])
F[u'ctx_128_only'] = len([i for i in range(4) if 128 in ctx_vals(i)])
four(u'th_line_norm', lambda i: len([l for l in LST[i]
                                     if re.search(u'(?i)\\d+[- ]characters?', l) and u'SHALL' in l]))
four(u'th_line_bare', lambda i: len([l for l in LST[i]
                                     if re.search(u'(?i)\\d+[- ]characters?', l)
                                     and not any(w in l for w in NORMW)]))

# ---------- 强度词: 一次切词进 Counter, 再查四档写法 ----------
def toks(s):
    return re.split(u'[^A-Za-z]+', s)


CNT = [Counter(toks(TXT[i])) for i in range(4)]


def kw(word, i, mode):
    if mode == u'u':
        return CNT[i][word]
    if mode == u'l':
        return CNT[i][word.lower()]
    if mode == u't':
        return CNT[i][word[0] + word[1:].lower()]
    return sum(v for k, v in CNT[i].items() if k.upper() == word)


for W in NORMW:
    four(u'kw_%s_u' % W.lower(), lambda i, W=W: kw(W, i, u'u'))
    four(u'kw_%s_l' % W.lower(), lambda i, W=W: kw(W, i, u'l'))
    four(u'kw_%s_t' % W.lower(), lambda i, W=W: kw(W, i, u't'))
    four(u'kw_%s_ci' % W.lower(), lambda i, W=W: kw(W, i, u'ci'))
F[u'kw_close'] = dict((W, [kw(W, i, u'u') + kw(W, i, u'l') + kw(W, i, u't') - kw(W, i, u'ci')
                           for i in range(4)]) for W in NORMW)
F[u'kw_close_sum'] = sum(sum(v) for v in F[u'kw_close'].values())
F[u'must_upper_all4'] = sum(F[u'kw_must_u'])
F[u'kw_upper_total'] = [sum(F[u'kw_%s_u' % W.lower()][i] for W in NORMW) for i in range(4)]
F[u'kw_ci_total'] = [sum(F[u'kw_%s_ci' % W.lower()][i] for W in NORMW) for i in range(4)]
F[u'kw_gap'] = [F[u'kw_ci_total'][i] - F[u'kw_upper_total'][i] for i in range(4)]
four(u'kw_shallnot_u', lambda i: TXT[i].count(u'SHALL NOT'))
four(u'kw_shallnot_ci', lambda i: len(re.findall(u'(?i)shall not', TXT[i])))
four(u'kw_shouldnot_u', lambda i: TXT[i].count(u'SHOULD NOT'))
four(u'kw_shouldnot_ci', lambda i: len(re.findall(u'(?i)should not', TXT[i])))
F[u'kw_shallnot_gap'] = [F[u'kw_shallnot_ci'][i] - F[u'kw_shallnot_u'][i] for i in range(4)]
F[u'kw_shouldnot_gap'] = [F[u'kw_shouldnot_ci'][i] - F[u'kw_shouldnot_u'][i] for i in range(4)]

# ---------- 术语换代 ----------
four(u'tm_memorized', lambda i: len(re.findall(u'(?i)memorized secret', TXT[i])))
four(u'tm_memorized_caps', lambda i: TXT[i].count(u'Memorized Secrets'))
four(u'tm_pw_sing', lambda i: len(re.findall(u'(?i)\\bpassword\\b', TXT[i])))
four(u'tm_pw_plural', lambda i: len(re.findall(u'(?i)\\bpasswords\\b', TXT[i])))
four(u'tm_pw_any', lambda i: len(re.findall(u'(?i)\\bpasswords?\\b', TXT[i])))
four(u'tm_bridge', lambda i: len(re.findall(u'(?i)called .{0,3}Memorized Secrets', TXT[i])))
four(u'tm_defline', lambda i: len([l for l in LST[i] if u'intended to be memorized' in l]))
F[u'tm_close'] = [F[u'tm_pw_sing'][i] + F[u'tm_pw_plural'][i] - F[u'tm_pw_any'][i]
                  for i in range(4)]

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
F[u'comp_norm_free'] = [F[u'mc_composition_lines'][i] - F[u'comp_shouldnot'][i] - F[u'comp_shallnot'][i]
                        for i in range(4)]
F[u'chg_shallnot'] = [len([l for l in LST[i] if re.search(u'(?i)change (passwords|memorized secrets)', l)
                           and u'SHALL NOT' in l]) for i in range(4)]
F[u'chg_shouldnot'] = [len([l for l in LST[i] if re.search(u'(?i)change (passwords|memorized secrets)', l)
                            and u'SHOULD NOT' in l]) for i in range(4)]
F[u'blk_def_lines'] = len([l for l in LST[2] if u'blocklist' in l and u'SHALL' in l])
four(u'bl_blacklist', lambda i: len(re.findall(u'(?i)blacklist', TXT[i])))
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
F[u'sup_openid'] = len([l for l in LST[3] if u'superseded' in l.lower() and u'OpenID' in l])
F[u'sup_nist'] = len([l for l in LST[0] if u'superseded' in l.lower() and u'63-4' in l])
F[u'cite_63b_docs'] = len([i for i in range(4) if re.search(u'(?i)800-63b', TXT[i])])
F[u'cite_forms'] = len([x for x in (F[u'cite_url_nist'][1], F[u'cite_unspaced'][3], F[u'cite_spaced'][0]) if x])

# ---------- ASVS 的条款号映射: 旧规范 ⇎ 草案 ----------
RE_SEC = re.compile(u'(?m)^\\s*((?:\\d+\\.){2,3}\\d+)\\s')
ASVS_ROWS = [l for l in LST[1] if re.match(u'^\\|\\s*\\*\\*2\\.\\d+\\.\\d+\\*\\*', l)]
four(u'sec_head_n', lambda i: len(RE_SEC.findall(TXT[i])))
F[u'sec_T_set'] = sorted(set(RE_SEC.findall(TXT[0])))
F[u'sec_F_set'] = sorted(set(RE_SEC.findall(TXT[2])))
F[u'sec_T_n'] = len(F[u'sec_T_set'])
F[u'sec_F_n'] = len(F[u'sec_F_set'])
F[u'sec_shared'] = len([x for x in F[u'sec_T_set'] if x in F[u'sec_F_set']])
F[u'sec_T_inF_text'] = len([x for x in F[u'sec_T_set'] if x in TXT[2]])
F[u'asvs_req_rows'] = len(ASVS_ROWS)
F[u'asvs_bold_ids'] = RAW[1].count(u'**2.')
CELLS = [[c.strip() for c in r.split(u'|')] for r in ASVS_ROWS]
F[u'asvs_refs'] = sorted(set(c[7] for c in CELLS if re.match(u'^\\d+(\\.\\d+){1,3}$', c[7])))
F[u'asvs_ref_occ'] = len([c[7] for c in CELLS if re.match(u'^\\d+(\\.\\d+){1,3}$', c[7])])
F[u'asvs_ref_distinct'] = len(F[u'asvs_refs'])
F[u'asvs_rows_noref'] = F[u'asvs_req_rows'] - F[u'asvs_ref_occ']
F[u'asvs_ref_inT'] = len([x for x in F[u'asvs_refs'] if x in F[u'sec_T_set']])
F[u'asvs_ref_inF'] = len([x for x in F[u'asvs_refs'] if x in F[u'sec_F_set']])
F[u'asvs_ref_inT_text'] = len([x for x in F[u'asvs_refs'] if x in TXT[0]])
F[u'asvs_ref_inF_text'] = len([x for x in F[u'asvs_refs'] if x in TXT[2]])
F[u'asvs_ref_missT'] = [x for x in F[u'asvs_refs'] if x not in F[u'sec_T_set']]
F[u'asvs_ref_missF'] = [x for x in F[u'asvs_refs'] if x not in F[u'sec_F_set']]
F[u'asvs_ref_close'] = F[u'asvs_ref_inT'] + len(F[u'asvs_ref_missT']) - F[u'asvs_ref_distinct']
F[u'asvs_tick_cols'] = [len([c for c in CELLS if c[k] == u'✓']) for k in (3, 4, 5)]
F[u'asvs_tick_total'] = sum(F[u'asvs_tick_cols'])
F[u'asvs_tick_legend'] = len([l for l in LST[1] if u'✓' in l and l not in ASVS_ROWS])
F[u'asvs_tick_glyph'] = RAW[1].count(u'✓')
F[u'asvs_tick_close'] = F[u'asvs_tick_total'] + F[u'asvs_tick_legend'] - F[u'asvs_tick_glyph']
F[u'asvs_cwe'] = sorted(set(c[6] for c in CELLS if c[6].isdigit()))
F[u'asvs_cwe_distinct'] = len(F[u'asvs_cwe'])
F[u'asvs_url_head'] = len(re.findall(u'pages\\.nist\\.gov/800-63-3', RAW[1]))
F[u'asvs_5112'] = [TXT[i].count(u'5.1.1.2') for i in range(4)]
F[u'id_211_bold'] = RAW[1].count(u'**2.1.1**')
F[u'id_211_occ'] = [TXT[i].count(u'2.1.1') for i in range(4)]
F[u'id_211_docs'] = len([i for i in range(4) if u'2.1.1' in TXT[i]])
four(u'sec_cite_sec', lambda i: len(re.findall(u'Sec\\. ?\\d', TXT[i])))
four(u'sec_cite_word', lambda i: len(re.findall(u'(?i)\\bSection \\d', TXT[i])))
four(u'sec_cite_any', lambda i: len(re.findall(u'(?i)(?:sec\\.?|section)[ \\t]+\\d', TXT[i])))
F[u'sec_cite_close'] = [F[u'sec_cite_sec'][i] + F[u'sec_cite_word'][i] - F[u'sec_cite_any'][i]
                        for i in range(4)]

# ---------- 熵/位 ----------
for b in (u'20', u'32', u'40', u'64', u'112'):
    four(u'bit_%s' % b, lambda i, b=b: TXT[i].count(b + u' bits'))
four(u'bit_any', lambda i: len(re.findall(u'(?i)\\d+\\s*bits', TXT[i])))
four(u'bit_set', lambda i: sorted(set(m.group(1) for m in re.finditer(u'(?i)(\\d+)\\s*bits', TXT[i]))))
F[u'bit_close'] = [F[u'bit_any'][i] - sum(F[u'bit_%s' % b][i] for b in (u'20', u'32', u'40', u'64', u'112'))
                   for i in range(4)]
F[u'bit_lost'] = sorted(set(F[u'bit_set'][0]) - set(F[u'bit_set'][2]))
F[u'bit_new'] = sorted(set(F[u'bit_set'][2]) - set(F[u'bit_set'][0]))

# ---------- 跨文书整行共用(两代 NIST ⇎ 两家 OWASP) ----------
def pnorm(s):
    return re.sub(u'[^a-z0-9]', u'', s.lower())


FAN = [pnorm(TXT[i]) for i in range(4)]
LN = [set(pnorm(l) for l in LST[i] if len(l) >= 20 and pnorm(l)) for i in range(4)]
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


def sents(i):
    out = []
    buf = u''
    for l in LST[i]:
        if not l:
            continue
        buf += (u' ' if buf else u'') + l
        parts = buf.split(u'. ')
        buf = parts.pop()
        out += [p for p in parts if len(p) >= 12]
    if len(buf) >= 12:
        out.append(buf)
    return [pnorm(x) for x in out if pnorm(x)]


SE = [sents(i) for i in range(4)]
four(u'sent_n', lambda i: len(set(SE[i])))
F[u'sent_shared_TF'] = len(set(SE[0]) & set(SE[2]))
F[u'sent_shared_ON'] = len(set(SE[1]) & set(SE[3]))
F[u'sent_union_TF'] = len(set(SE[0]) | set(SE[2]))
F[u'sent_only_T'] = len(set(SE[0]) - set(SE[2]))
F[u'sent_only_F'] = len(set(SE[2]) - set(SE[0]))
F[u'sent_close_TF'] = F[u'sent_shared_TF'] + F[u'sent_only_T'] + F[u'sent_only_F'] - F[u'sent_union_TF']
F[u'sent_share_th'] = len([x for x in (set(SE[0]) & set(SE[2]))
                           if re.search(u'(8|15|64|eight|fifteen) ?character', x)])
GEN = [sorted(set(pnorm(l) for l in LST[0] if len(l) >= 20 and pnorm(l)) &
                set(pnorm(l) for l in LST[2] if len(l) >= 20 and pnorm(l)))]
F[u'carry_shared'] = F[u'share_TF']
F[u'carry_ref'] = len([x for x in GEN[0] if u'sp800' in x or u'doiorg' in x or u'nistgov' in x])
F[u'carry_toc'] = len([x for x in GEN[0] if re.match(u'^\\d', x)])
F[u'carry_prose'] = F[u'carry_shared'] - F[u'carry_ref'] - F[u'carry_toc']
F[u'carry_split_close'] = F[u'carry_ref'] + F[u'carry_toc'] + F[u'carry_prose'] - F[u'carry_shared']

# ---------- 锚池 ----------
SPECIAL = (u'8 characters', u'eight characters', u'12 characters', u'15 characters', u'64 characters',
           u'128 characters', u'memorized secret', u'blocklist', u'composition rules',
           u'pages.nist.gov', u'SP8210', u'superseded', u'initial public draft', u'2.1.1',
           u'Memorized Secrets', u'112 bits', u'multi-factor', u'copy and paste', u'single-factor')
POOL = set()
for i, t in enumerate(TAGS):
    for l in LST[i]:
        if len(l) < 20 and not any(x in l for x in SPECIAL):
            continue
        if pnorm(l):
            POOL.add((t, l))
POOL = sorted(POOL)
CROSS = dict(((t, x), sum(1 for k in range(4) if pnorm(x) in FAN[k])) for (t, x) in POOL)
POOLC = [(t, CROSS[(t, x)], x) for (t, x) in POOL]
F[u'pool_n'] = len(POOLC)
four(u'pool_tag_n', lambda i: len([p for p in POOLC if p[0] == TAGS[i]]))
for n in (1, 2, 3, 4):
    F[u'pool_%d' % n] = len([p for p in POOLC if p[1] == n])
F[u'pool_tiers'] = [F[u'pool_1'], F[u'pool_2'], F[u'pool_3'], F[u'pool_4']]
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
FN = u'B59V'


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
        nums = [eval(e, {u'B59V': BB59}) for e in exprs]
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


BB59 = lambda name, i=None: (F[name] if i is None else F[name][i])
BCALL = re.compile(r"B59V\('([a-z0-9_]+)'(?:,\s*(\d+))?\)")
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
        val = eval(args[0], {u'F': F, u'B59V': BB59, u'len': len, u'max': max, u'round': round,
                             u'repr': repr})
        reg(str(val), _unlit(args[1]), _unlit(args[2]))
        t = t[:i] + str(val) + t[k + 2:]

    def rep(m):
        c = m.group(1).strip()
        if HELP.match(c):
            return eval(c, {u'V': V, u'JOIN': JOIN, u'CLOS': CLOS, u'CLOS4': CLOS4, u'TOK': TOK, u'AT': AT})
        if u'B59V(' not in c:
            return m.group(0)
        assert BARE.match(BCALL.sub(u'0', c)), c
        val = eval(c, {u'B59V': BB59})
        reg(str(val), c.strip(), c.strip())
        return str(val)
    return re.sub(r'\{([^{}]*)\}', rep, t)


class _Ctx(dict):
    def __missing__(self, k):
        MISSING.append(k)
        return u'§' + k


def LINE(em, tmpl, /, **kw):
    LINES.append((em + u' ' + _inline(tmpl)).format_map(_Ctx(dict(G, **kw))))


# ---------- 正文 ----------
LINE(u'🧭', u"四源字节 {JOIN('bytes')}: 旧规范 ⇎ 验证标准 ⇎ 新草案 ⇎ 备忘单; 渲染后 {JOIN('chars')} 字符 ⇎ 原文件行 {JOIN('lines')} ⇎ 非空行 {JOIN('nonblank')}。"
     u"同一把剥壳刀走两遍得两种口径: 连脚本内容一起删 ⇎ 只删标签留下脚本正文, 差额 {CLOS4('js_gap', '两口径字数差')} 字, "
     u"脚本 {JOIN('script_tags')} 枚 ⇎ 样式 {JOIN('style_tags')} 枚——前三份是 HTML, 第二份是 Markdown, 它在两口径下差 {V('js_gap',1,u'Markdown 无脚本')} 字(刀在它身上只折实体)。"
     u"表格有两种序列化: HTML 侧表行 {JOIN('tr_rows')} 条(表 {JOIN('table_tags')} 枚) ⇎ Markdown 侧靠竖线分格, 该字符 {V('pipe_cells',1,u'MD 竖线')} 枚, "
     u"两份 NIST 的表行相加 {EXPR(F['tr_rows'][0]+F['tr_rows'][2], u\"B59V('tr_rows',0)+B59V('tr_rows',2)\", '两代表行之和')} 条, 与 MD 竖线相差 {CLOS('pipe_vs_row', '竖线与表行之差')}; "
     u"粗体标记只在这份里有 {V('bold_marks',1)} 对, 链接 {V('md_links',1)} 条。最长行 {JOIN('maxlen')} 列。"
     u"四份字节 {EXPR(len(set(F['sha16'])), u\"len(set(B59V('sha16')))\", '四份签名种数')} 种签名(本遍用 sha256 前 16 位)。")

LINE(u'📏', u"主轴一: “用户自己定的口令最短多长”。四份各给一个数——旧规范 {AT('own', 'T', u'at least 8 characters in length if chosen')} ⇎ "
     u"验证标准 {AT('own', 'O', u'at least 12 characters in length')} ⇎ 新草案单因子 {AT('own', 'F', u'minimum of 15 characters')} ⇎ 备忘单 {AT('own', 'N', u'shorter than 8 characters')}。"
     u"把每份里“数+characters”的语境全收进来: 命中处数 {JOIN('ctx_occ')} ⇎ 不同数值 {JOIN('ctx_distinct')} 个 ⇎ 集合 {JOIN('ctx_set')}。"
     u"草案的 8 不写成数字: “8 characters” 在旧规范 {V('th_digit8',0)} 处 ⇎ 草案 {V('th_digit8',2)} 处, 而 “eight characters” 只在草案 {V('th_word_eight',2)} 处——"
     u"同一个门槛换了记法, 两份 NIST 的分档词数因此互不可见: 草案里数字写法 {V('ctx_digit_form',2)} 处 ⇎ 词面写法 {V('ctx_word_form',2)} 处(相加校住 {EXPR(F['ctx_occ'][2], u\"B59V('ctx_digit_form',2)+B59V('ctx_word_form',2)\", '草案两写法之和')}, 四份闭合差 {CLOS4('ctx_form_close', '写法闭合')})。"
     u"上界另有一本账: “64 characters” {JOIN('th_digit64')} 处四份都在, “128 characters” 只在验证标准 {V('th_digit128',1)} 处(它是唯一写“超过多少就拒收”的那份), "
     u"而备忘单给的下界措辞是 {AT('own', 'N', u'reasonable maximum password length')}。"
     u"随机生成的口令另有更低的门: 旧规范 {AT('own', 'T', u'at least 6 characters in length and SHALL be generated')} ⇎ 草案把 4 与 6 都写成单词 {AT('own', 'F', u'the secrets to be at least four characters')}。"
     u"15 出现两份: 草案 {V('th_digit15',2)} 处 ⇎ 备忘单 {V('th_digit15',3)} 处, 旧规范与验证标准 {V('th_digit15',0)}⇎{V('th_digit15',1)} 处; 同时含 8 与 15 两个门槛的文书 {V('ctx_815_docs')} 份。")

LINE(u'📐', u"主轴二: 谁在替谁说话。验证标准每条要求末格填一个 NIST 条款号: 要求 {V('asvs_req_rows')} 条 ⇎ 带号 {V('asvs_ref_occ')} 处 ⇎ 无号 {V('asvs_rows_noref')} 条 ⇎ 不同号 {V('asvs_ref_distinct')} 枚。"
     u"把这些号拿去逐字撞两份 NIST: 撞旧规范的条款标题集({V('sec_T_n')} 个号)命中 {V('asvs_ref_inT')} 枚, 撞新草案的标题集({V('sec_F_n')} 个号)命中 {V('asvs_ref_inF')} 枚; "
     u"换成整篇正文再撞仍是 {V('asvs_ref_inT_text')} ⇎ {V('asvs_ref_inF_text')}——映射整列跟着旧版失效, 未命中清单 {V('asvs_ref_missT')} 空 ⇎ {EXPR(len(F['asvs_ref_missF']), u\"len(B59V('asvs_ref_missF'))\", '草案侧未命中枚数')} 枚全空。"
     u"闭合账: 命中+未命中−去重 {CLOS('asvs_ref_close', '条款号命中闭合')} ⇎ 勾号字符与三列相加差 {CLOS('asvs_tick_close', '勾选闭合')}。"
     u"引用形态有三种: 直连 URL “pages.nist.gov” 只在验证标准 {V('cite_url_nist',1)} 处(且 {V('asvs_url_head')} 处写着 63-3) ⇎ 带空格 “NIST SP 800-63” {JOIN('cite_spaced')} ⇎ 无空格 “SP800-63B” 只在备忘单 {V('cite_unspaced',3)} 处——"
     u"而 “SP800-63B” 这个串在库里同时指旧规范与草案({V('cite_63b_docs')} 份文书自带 800-63B 字样), 它归给 NIST 的那句里 15 这个数只在草案有。"
     u"自我标注也各写各的: 旧规范页里写着被 “800-63-4” 废止 {V('cite_rev4num',0)} 处 ⇎ 草案自标 initial public draft {V('cite_draftself',2)} 处 ⇎ 草案里 800-63-3 {V('cite_rev3num',2)} 处(反指旧版)。"
     u"“superseded” 一词两份各说一事: 旧规范说自己的 {V('sup_nist')} 句 ⇎ 备忘单说 OpenID 2.0 的 {V('sup_openid')} 句。")

LINE(u'🪢', u"主轴三: 同一样东西换名字。旧规范通篇 “memorized secret” {V('tm_memorized',0)} 处(大写标题形 {V('tm_memorized_caps',0)} 处) ⇎ 草案只剩 {V('tm_memorized',2)} 处 ⇎ 验证标准 {V('tm_memorized',1)} 处 ⇎ 备忘单 {V('tm_memorized',3)} 处; "
     u"反过来 “password” 单数 {JOIN('tm_pw_sing')} ⇎ 复数 {JOIN('tm_pw_plural')} ⇎ 合并后全数 {JOIN('tm_pw_any')}(单复相加校住全数, 闭合差 {CLOS4('tm_close', '术语账闭合')})。"
     u"唯一的显式换算在验证标准: {AT('own', 'O', u'called')} —— 它一句话把两套术语钉在一起, 并给出定义 {AT('own', 'O', u'unlock patterns')}; "
     u"草案则重写定义 {AT('own', 'F', u'intended to be memorized')}(“intended to be memorized” 这句话在四份里出现 {JOIN('tm_defline')} 处)。"
     u"旧规范一侧的旧定义把两个名字并排写着: {AT('own', 'T', u'commonly referred to as a password')}——它就是 {V('tm_memorized_caps',0)} 处大写标题形里被解释的那个词。"
     u"名字换了, 整行也跟着换: 两代 NIST 逐字共用的长行 {V('share_TF')} 条(旧独有 {V('only_T')} ⇎ 新独有 {V('only_F')}, 并集 {V('union_TF')}, 闭合差 {CLOS('share_close_TF', '整行共用闭合')}) ⇎ "
     u"两家 OWASP 文书共用整行 {V('share_ON')} 条(独有 {V('only_O')}⇎{V('only_N')}, 并集 {V('union_ON')}, 闭合差 {CLOS('share_close_ON', 'OWASP 侧整行闭合')}) ⇎ 四份全同 {V('share_all4')} 条。")

LINE(u'🧱', u"强度词分三档写法分开数(全大写/全小写/首字母大写), 相加校住忽略大小写那一档, 四词×四份的闭合差合计 {V('kw_close_sum')}。"
     u"大写 SHALL {JOIN('kw_shall_u')} ⇎ SHOULD {JOIN('kw_should_u')} ⇎ MAY {JOIN('kw_may_u')} ⇎ 而 MUST 大写 {JOIN('kw_must_u')} 处——四份文书没有一个全大写 MUST, "
     u"可“必须”这件事照样在: 小写 must {JOIN('kw_must_l')} 处(草案另有首字母大写 {V('kw_must_t',2)} 处); 按空白切词看得见小写, 按“规范词表只认大写”切就全看不见。"
     u"四份大写规范词合计 {JOIN('kw_upper_total')} ⇎ 忽略大小写 {JOIN('kw_ci_total')}(差额 {JOIN('kw_gap')} 全来自小写与首字母)。"
     u"禁令也分两套: SHALL NOT {JOIN('kw_shallnot_u')} ⇎ SHOULD NOT {JOIN('kw_shouldnot_u')}(与 NOT 连写的忽略大小写数比大写多出 {CLOS4('kw_shallnot_gap', '禁令口径差')})。"
     u"同一句禁令在两版之间换档: “composition rules” 出现的行里带 SHOULD NOT 的行数 {JOIN('comp_shouldnot')} ⇎ 带 SHALL NOT 的 {JOIN('comp_shallnot')}, 无强度词的 {CLOS4('comp_norm_free', '同条无强度行')}; "
     u"旧规范那一行 {AT('own', 'T', u'impose other composition rules')} ⇎ 草案改口后的那一行 {AT('own', 'F', u'impose other composition rules')} ⇎ 验证标准把同一条排成要求 {AT('own', 'O', u'no password composition rules')}。"
     u"周期改口令那句同样: SHOULD NOT {JOIN('chg_shouldnot')} ⇎ SHALL NOT {JOIN('chg_shallnot')}, 另加“发现泄露才强制改”{JOIN('mc_forcechange')} 处——旧规范写禁令的原文是 {AT('own', 'T', u'be changed arbitrarily')}。")

LINE(u'🗣', u"机制的增删也落在词面上: “blocklist” 旧规范 {V('mc_blocklist',0)} 处 ⇎ 草案 {V('mc_blocklist',2)} 处(其中含 SHALL 的定义行 {V('blk_def_lines')} 行) ⇎ 备忘单 {V('mc_blocklist',3)} 处 ⇎ 验证标准 {V('mc_blocklist',1)} 处; "
     u"草案给这个词下了定义 {AT('own', 'F', u'historically been known as a')}, 旧规范说同一件事用 “blacklist” 一词(blocklist {V('mc_blocklist',0)} 处 ⇎ blacklist {V('bl_blacklist',0)} 处 ⇎ 带空格的 “black list” {V('bl_spaced',0)} 处, 后两种相加校住 black 词族 {V('bl_black',0)} 枚, 闭合差 {CLOS4('bl_black_close', 'black 词形闭合')}; 全库 block+black 词族 {JOIN('bl_word_any')} 枚, 与两词形相加的闭合差 {CLOS4('bl_word_close', '两词族闭合')}), 旧规范那一行 {AT('own', 'T', u'black list')}; "
     u"草案的比对照式是 {AT('own', 'F', u'against a blocklist that contains')}, 备忘单的劝告是 {AT('own', 'N', u'raise the number of guesses')}。"
     u"“breach” {JOIN('mc_breach')} ⇎ 限流词 {JOIN('mc_ratelimit')} ⇎ 锁定词 {JOIN('mc_lockout')} ⇎ 项目符无关的 “copy and paste” {JOIN('mc_copypaste')} 处(两家 OWASP 文书 {EXPR(F['mc_copypaste'][1]+F['mc_copypaste'][3], u\"B59V('mc_copypaste',1)+B59V('mc_copypaste',3)\", 'OWASP 侧复制粘贴之和')} 处)。"
     u"熵的位账换代: 出现的位数集合 旧规范 {V('bit_set',0)} ⇎ 草案 {V('bit_set',2)} ⇎ 验证标准 {V('bit_set',1)} ⇎ 备忘单 {V('bit_set',3)}(空集); "
     u"草案丢掉 {V('bit_lost')} ⇎ 新增 {V('bit_new')}; 112 bits {JOIN('bit_112')} 处 ⇎ 64 bits {JOIN('bit_64')} ⇎ 32 bits {JOIN('bit_32')} ⇎ 20 bits {JOIN('bit_20')} ⇎ 40 bits {JOIN('bit_40')}, 五种位数相加校住 “N bits” 全数(余量 {CLOS4('bit_close', '位数账闭合')})。"
     u"多因子词面 {JOIN('mc_multifactor')} 处——备忘单把 8 与 15 两个门槛挂在“是否开多因子”上, 而这句话在旧规范里没有对应的数字。")

LINE(u'🧵', u"验证标准把口令要求排成矩阵: 要求 {V('asvs_req_rows')} 行 ⇎ 三列勾数 L1 {V('asvs_tick_cols',0)} ⇎ L2 {V('asvs_tick_cols',1)} ⇎ L3 {V('asvs_tick_cols',2)}(合计 {V('asvs_tick_total')} ⇎ 要求行外还有一枚勾号在图例行 {V('asvs_tick_legend')} 行里, 文件里勾号字符共 {V('asvs_tick_glyph')} 枚, 闭合差 {CLOS('asvs_tick_close', '勾选闭合')}) ⇎ CWE 号 {V('asvs_cwe_distinct')} 种。"
     u"编号同形不同物: 串 2.1.1 逐字出现在 {V('id_211_docs')} 份文书、共 {EXPR(sum(F['id_211_occ']), u\"B59V('id_211_occ',0)+B59V('id_211_occ',1)+B59V('id_211_occ',2)+B59V('id_211_occ',3)\", '四份出现处之和')} 处; "
     u"验证标准里它是带粗体的要求号(**2.1.1** {V('id_211_bold')} 处, 该份 {V('id_211_occ',1)} 处全是这一族要求号), 草案里它只是一枚更长条款号的尾巴(Sec. 4.2.1.1, 该份 {V('id_211_occ',2)} 处), 旧规范与备忘单 {V('id_211_occ',0)}⇎{V('id_211_occ',3)} 处。"
     u"指向条款的写法也换代: Sec. 体例 旧规范 {V('sec_cite_sec',0)} 处 ⇎ 草案 {V('sec_cite_sec',2)} 处, Section 全称 {JOIN('sec_cite_word')}——"
     u"两种写法相加校住指向一个号的引用全数 {JOIN('sec_cite_any')}(闭合差 {CLOS4('sec_cite_close', '条款引用闭合')})。"
     u"5.1.1.2 这一枚 {JOIN('asvs_5112')} 处——它是验证标准末格用得最多的号, 也是旧规范的真条款, 在草案里 {V('asvs_5112',2)} 处。"
     u"同一份草案的标题号只 {V('sec_F_n')} 个(旧规范 {V('sec_T_n')} 个), 两版标题号集相交 {V('sec_shared')} 个, 而旧版号在草案正文里以别的面貌出现的有 {V('sec_T_inF_text')} 个。")

LINE(u'🧬', u"两代 NIST 之间的搬运记三口径: 整行集交 {V('carry_shared')} 条 ⇎ “在对方正文里逐字再现一次”口径 {V('carry_sub_TF')}＋{V('carry_sub_FT')}＝{V('carry_sub_overlap')} "
     u"(比集交多 {V('carry_caliber_gap')} 条, 因为它把别人的子串也算搬走) ⇎ 句子档共用 {V('sent_shared_TF')} 句(旧 {V('sent_n',0)} 句 ⇎ 新 {V('sent_n',2)} 句, 并集 {V('sent_union_TF')}, 独有 {V('sent_only_T')}⇎{V('sent_only_F')}, 闭合差 {CLOS('sent_close_TF', '句子档闭合')}; "
     u"其中含门槛数字的共用句只有 {V('sent_share_th')} 句——两份各写各的门限)。"
     u"共用那 {V('carry_shared')} 行的体裁: 参考条目 {V('carry_ref')} ⇎ 章节号行 {V('carry_toc')} ⇎ 正文行 {V('carry_prose')}(相加校住, 差 {CLOS('carry_split_close', '体裁拆分闭合')}——真正“同一条声明原样搬过去”的只有 {V('carry_prose')} 行)。"
     u"两家 OWASP 文书之间句子档共用 {V('sent_shared_ON')} 句(备忘单 {V('sent_n',3)} 句 ⇎ 验证标准 {V('sent_n',1)} 句)。")

LINE(u'🧪', u"这条的可核事实分三档。第一档全部由四份在库字节现推: {AT('own', 'T', u'SHALL be at least 8 characters')} ⇎ {AT('own', 'F', u'as a single-factor authentication mechanism')} ⇎ "
     u"{AT('own', 'O', u'2.1.1')} ⇎ {AT('own', 'N', u'15 characters are considered to be weak')}; "
     u"跨文书锚 {AT('m2', 'T', u'64 characters in length to support')} ⇎ {AT('m2', 'N', u'at least 64 characters')}; "
     u"锚候选池 {EXPR('%.1f' % (F['pool_n'] / 1000.0), u\"round(B59V('pool_n')/1000*10)/10\", '池千位')} 千条(每源 {JOIN('pool_tag_n')}), 穿一源 {V('pool_1')} ⇎ 两源 {V('pool_2')} ⇎ 三源 {V('pool_3')} ⇎ 四源 {V('pool_4')}(相加校住池, 差 {CLOS('pool_close', '池分层闭合')}), 池内最长行 {V('pool_maxlen')} 列。"
     u"登记锚 {TOK('anchor_total')} 处／{TOK('anchor_distinct')} 个不同串(每标签 T {TOK('tag_T')} ⇎ O {TOK('tag_O')} ⇎ F {TOK('tag_F')} ⇎ N {TOK('tag_N')}; 单源 {TOK('anchor_single')} ⇎ 穿二或三源 {TOK('anchor_cross')} ⇎ 四源全现 {TOK('anchor_all4')}, 归属检查 {TOK('checks')} 次, 错配 {TOK('anchor_err')})。"
     u"第二档是本条自己复算出来的关系量: 条款号命中 {V('asvs_ref_inT')}⇎{V('asvs_ref_inF')}、整行共用 {V('share_TF')}、位数集增删、强度词三账闭合——都要按上面写明的口径重跑才成立。"
     u"第三档不进门槛: 备忘单那句 “(NIST SP800-63B)” 究竟指 2017 定稿还是 2025 草案、草案此刻是否已定稿、旧规范页的废止横幅何时挂上、"
     u"四份文件各自的抓取时刻与磁盘 mtime——不可由在库文件判定, 判词按第三档写、门槛不背书。")

LINE(u'∴', u"骨架 ⇒ ① 四源 {JOIN('bytes')} 字节 ⇎ 渲染 {JOIN('chars')} 字符 ⇎ 两口径差 {CLOS4('js_gap', '脚本差额')}; "
     u"② 门槛四答 {JOIN('ctx_set')}, 草案的 8 是单词 {V('th_word_eight',2)} 处 ⇎ 数字 {V('th_digit8',2)} 处; "
     u"③ 上界 64 四份都在 {JOIN('th_digit64')} ⇎ 128 只在验证标准 {V('th_digit128',1)}; "
     u"④ ASVS 条款号 {V('asvs_ref_occ')} 枚/{V('asvs_ref_distinct')} 不同, 命中旧 {V('asvs_ref_inT')} ⇎ 命中新 {V('asvs_ref_inF')}; "
     u"⑤ 术语 memorized secret {JOIN('tm_memorized')} ⇎ password 单数 {JOIN('tm_pw_sing')}; "
     u"⑥ 强度词大写 SHALL {JOIN('kw_shall_u')} ⇎ MUST {JOIN('kw_must_u')} ⇎ 小写 must {JOIN('kw_must_l')}; "
     u"⑦ 同条禁令 SHOULD NOT {V('comp_shouldnot',0)} 行(旧) → SHALL NOT {V('comp_shallnot',2)} 行(新); "
     u"⑧ blocklist {V('mc_blocklist',0)}⇎{V('mc_blocklist',2)} ⇎ 位数集 {V('bit_set',0)}→{V('bit_set',2)}; "
     u"⑨ 整行共用 两代 {V('share_TF')} ⇎ 两家 OWASP {V('share_ON')} ⇎ 四份 {V('share_all4')}; "
     u"⑩ 引用形态 URL {V('cite_url_nist',1)} ⇎ 无空格 {V('cite_unspaced',3)} ⇎ 带空格 {JOIN('cite_spaced')}; "
     u"⑪ 锚 {EXPR(F['pool_4'], u\"B59V('pool_4')\", '四源池条数')} 条四源候选里取用。"
     u"判词: “口令该多长”没有同一种答法——问旧规范, 它说 8 并把这条写成 memorized secret 的 SHALL; "
     u"问草案, 它把 8 写成英文单词、另给单因子 15, 还第一次请出 blocklist; 问验证标准, 它要 12 并附“超过 128 就拒收”, 再把每条要求钉在旧规范的条款号上; "
     u"问备忘单, 它把 8 与 15 一起归给 “NIST SP800-63B” 而不说是哪一版。四份都在回答, 四份答的不是同一道题的同一个口径。")

LINE(u'ℒ', u"方法 ⇒ 遇到“同一个数字被几家机构各写一遍”的原料, 先问每个数在库里能不能被逐字撞到: 本条把门槛数字做成“数+characters”语境的取值集合({JOIN('ctx_set')}), "
     u"再单列记法账(数字 ⇎ 英文词), 于是“草案换了写法”这一条不必靠外部知识就能落到 {V('ctx_word_form',2)} 处上; "
     u"第三方给的映射表不去信它的名号, 而是把末格号码抽成集合去撞两版规范的标题号集({V('asvs_ref_inT')}⇎{V('asvs_ref_inF')}), 命中账与未命中清单一起登记({V('asvs_ref_missF')} 枚); "
     u"强度词按大写/小写/首字母三档分开数并与忽略大小写那档做闭合({V('kw_close_sum')}), 因为“四份都没有大写 MUST”和“四份都在说必须”同时成立; "
     u"跨文书搬运记三口径(整行集交 ⇎ 子串再现 ⇎ 句子档), 并把共用行按体裁拆成参考/章节号/正文三档({V('carry_ref')}⇎{V('carry_toc')}⇎{V('carry_prose')}), "
     u"免得把目录与参考文献当成共识。引用形态分 URL/带空格/无空格三档各数一遍, 才看得见 “SP800-63B” 这个串在库里同时指两版。")

LINE(u'✂️', u"为什么这份编码比摘要窗口长 ⇒ 四源各 {JOIN('chars')} 字符, 窗口只能取锚点触到的行; 而本条的结论几乎全是跨文书的量: "
     u"条款号 {V('asvs_ref_occ')} 枚命中 {V('asvs_ref_inT')}⇎{V('asvs_ref_inF')} 要同时读两份才算得出, 整行共用 {V('share_TF')} 行与句子档共用 {V('sent_shared_TF')} 句要两份并排比, "
     u"术语账 {V('tm_memorized',0)}⇎{V('tm_memorized',2)} 要两份同数, 强度词三账闭合要四份全量。"
     u"尤其“草案把 8 改写成 eight”这一条, 任何单源窗口都看不见——它要旧规范一侧 “8 characters” {V('th_digit8',0)} 处与草案一侧 {V('th_digit8',2)} 处、"
     u"“eight characters” {V('th_word_eight',2)} 处同时成立才读得出来。读它请按“这个数由哪份文书、在哪一格、用哪种记法给出”来读, 而不是按“少抄了多少原文”。", **{})

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
HITC = dict((a, tuple(i for i in range(4) if pnorm(a) in FAN[i])) for a in ANCH)
CLS = {u'single': len([a for a in ANCH if len(HITC[a]) == 1]),
       u'cross': len([a for a in ANCH if 1 < len(HITC[a]) < 4]),
       u'all4': len([a for a in ANCH if len(HITC[a]) == 4])}
AMETA = {u'anchor_total': USED, u'anchor_distinct': DIST, u'anchor_err': len(ERR),
         u'anchor_single': CLS[u'single'], u'anchor_cross': CLS[u'cross'],
         u'anchor_all4': CLS[u'all4'], u'checks': DIST * 4}
for t in TAGS:
    AMETA[u'tag_' + t] = TAGN[t]
assert not ERR, ERR[:3]
assert CLS[u'single'] + CLS[u'cross'] + CLS[u'all4'] == DIST
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
json.dump(DERIV, io.open(u'corpus/_deriv59.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
json.dump(F, io.open(u'corpus/_b59flat.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, sort_keys=True)
io.open(u'corpus/_atoms59.txt', 'w', encoding='utf-8', newline=NL).write(
    NL.join(sorted(ANCH, key=len, reverse=True)) + NL)

CH = {u'anchor_total': USED, u'anchor_distinct': DIST, u'tag_counts': TAGN, u'ameta': AMETA,
      u'letters_in': len(re.findall(u'[A-Za-z]', u''.join(ANCH))),
      u'letters_out': len(re.findall(u'[A-Za-z]', re.sub(u'⟨[^⟨⟩]*⟩', u'', body))),
      u'tagn': len(re.findall(u'⟦[TOFN]⟧', body)),
      u'classes': dict((c, sorted([a for a in ANCH if len(HITC[a]) == n]))
                       for c, n in ((u'single', 1), (u'two', 2), (u'three', 3), (u'four', 4))),
      u'collisions': dict((k, v) for k, v in COLL.items()),
      u'zero_terms': len(ZERO), u'deriv_keys': len(DERIV),
      u'deriv_points': sum(len(v) for v in SEENX.values()),
      u'notes': NOTES, u'pool_used': len(set(USEDATOM) & set(ANCH)),
      u'enc_chars': len(body.replace(NL, u'')), u'nsrc': 4, u'flat': F,
      u'closure_keys': [k for k in F if k.endswith(u'close')]}
json.dump(CH, io.open(u'corpus/_b59checks.json', 'w', encoding='utf-8'), indent=1)

srcline = (u'src: ' + u' ⇎ '.join(
    u'%s (%d 字节／渲染 %d 字符／非空行 %d／表行 %d／“%s” %d 处)' % (
        PATH[i], F[u'bytes'][i], F[u'chars'][i], F[u'nonblank'][i], F[u'tr_rows'][i],
        (u'8 characters' if i in (0,) else u'12 characters' if i == 1 else
         u'eight characters' if i == 2 else u'15 characters'),
        F[u'th_digit8'][i] if i == 0 else F[u'th_digit12'][i] if i == 1 else
        F[u'th_word_eight'][i] if i == 2 else F[u'th_digit15'][i]) for i in range(4)) +
    u' (两份 NIST 官方 HTML ⇎ 两份 OWASP 文档, 其中一份是 Markdown; 数字与条款号一律从渲染正文与表格末格现读, 一个都不手填; '
    u'抓取时刻与磁盘 mtime、草案是否已定稿、备忘单引的是哪一版只在本机或站外成立, 不进门槛)\n')
联结 = (u"；联结不是“同一份数据的两种序列化”, 而是同一个口令问题在两家机构的四份文书里的四种答法: "
        u"最短门槛 数字 8 ⇎ 12 ⇎ 15 ⇎ 8 与 15 并列, 草案把 8 写成英文词(%d 处)而数字写法 %d 处; "
        u"验证标准给每条要求钉上 NIST 条款号, %d 枚里 %d 枚逐字命中旧规范的标题号集、%d 枚命中草案的(草案标题号只 %d 个); "
        u"术语从 memorized secret(%d 处)换成 password(单数 %d 处); 全大写 MUST 四份共 %d 处而小写 must %d⇎%d⇎%d⇎%d 处; "
        u"同一条 composition rules 禁令从 SHOULD NOT(%d 行)升为 SHALL NOT(%d 行); blocklist 整套机制只在草案(%d 处)。\n") % (
    F[u'th_word_eight'][2], F[u'th_digit8'][2], F[u'asvs_ref_occ'], F[u'asvs_ref_inT'],
    F[u'asvs_ref_inF'], F[u'sec_F_n'], F[u'tm_memorized'][0], F[u'tm_pw_sing'][2],
    F[u'must_upper_all4'], F[u'kw_must_l'][0], F[u'kw_must_l'][1], F[u'kw_must_l'][2],
    F[u'kw_must_l'][3], F[u'comp_shouldnot'][0], F[u'comp_shallnot'][2], F[u'mc_blocklist'][2])
title = (u'# B59 同一个口令该多长，四份规范四种答法：数字 8 ⇎ 12 ⇎ 15 ⇎ 并列（%d 处）⇎ 草案把 8 写成单词 ⇎ 第三方的 %d 枚条款号只在新版里全体落空\n' % (
    F[u'sent_share_th'], F[u'asvs_ref_distinct']))
text = (title + srcline + 联结 +
        u'tags: 门槛数字取值集合 记法两档(数字⇎英文词) 第三方条款号撞两版 术语换代单复数三账闭合 '
        u'强度词大写⇎小写⇎首字母三账 同条禁令换档 blocklist 只在草案 位数集增删 整行⇎子串⇎句子三口径 '
        u'共用行体裁拆分 引用形态三档 同形不同物编号 自我标注 锚归属由正文现推 闭合账 %d 项\n' % F[u'scalar_clos_n'] +
        u'## [[原始语料|ORIGINAL]]\n（此段由 corpus/_mkdigest3.py 现算覆盖）\n\n' +
        u'## ⟪BabelTele⟫\n' + body + u'\n\n' +
        u'## ⛓解读注\n\n（此段由 corpus/_fill59.py 从 corpus/_b59checks.json 与 corpus/_b59meas.json 现算写入）\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=NL).write(text)
print(u'条目已写 %s ｜ 编码区 %d 字符' % (ENTRY, len(body.replace(NL, u''))))
print(u'锚 正文 %d 处 ⇎ 去重 %d ｜ 每标签 %s' % (USED, DIST, TAGN))
print(u'一源 %d ⇎ 两或三源 %d ⇎ 四源 %d ⇎ 错配 %d ｜ 池内取用 %d／池 %d' % (
    CLS[u'single'], CLS[u'cross'], CLS[u'all4'], len(ERR), CH[u'pool_used'], F[u'pool_n']))
print(u'DERIV %d 键 ⇎ 引用点 %d ｜ 同数共键 %d 组 ｜ 0 键折 %d 项 ｜ 扁平键 %d' % (
    len(DERIV), CH[u'deriv_points'], len(COLL), len(ZERO), len(F)))
print(u'门槛集 %s ｜ 草案记法 词 %d⇎数 %d ｜ 引用命中 %d⇎%d ｜ 整行共用 %d⇎%d⇎%d' % (
    F[u'ctx_set'], F[u'ctx_word_form'][2], F[u'ctx_digit_form'][2], F[u'asvs_ref_inT'],
    F[u'asvs_ref_inF'], F[u'share_TF'], F[u'share_ON'], F[u'share_all4']))
BAD = [bk for bk in sorted(F) if bk in M and F[bk] != M[bk]]
for bk in BAD:
    print(u'  与采集侧不符: %s 建条目=%s 采集=%s' % (bk, F[bk], M[bk]))
print(u'对账: 共有键 %d ／ 不符 %d' % (len([b for b in F if b in M]), len(BAD)))
