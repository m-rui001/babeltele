# -*- coding: utf-8 -*-
# ============================================================================
# B96 建条目侧(第一套实现, A 侧): 单文本压缩 · 截止后专业信息
#   源 = FCC《Enhancing the Ability of Consumers To Control the Robocalls》
#        (91 FR 67214, 2026-10-26 刊出, CG Docket No. 02-278; FCC 26-67)
#   本文件只做两件事: ①SCAN 段量出全部判词读数(第二套实现见 corpus/_pick96.py,
#     两套在口径一致的键集上逐键对账, 对账件由 _pick96.py 写 corpus/_b96meas.json);
#   ②按 B87/B88 版式发射条目(编码区数字全部由 V() 从对账件插值, 零手填)。
# 机制档位(A 侧): 整串 split/join 折平 ⇎ split(chr(10)) 行面 ⇎ str.count 子串档 ⇎
#   lookaround 正则 token 档 ⇎ (?<=[.!?]) 正则切句 ⇎ 两条整串正则剥壳 ⇎
#   单行布尔判严格档 ⇎ 两档总量之差推跨行 ⇎ set() 去重 ⇎ 一条正则解段落号。
# 运行次序: python -X utf8 corpus/_mkB96.py  ⇎ python -X utf8 corpus/_pick96.py
#           ⇎ 再跑一遍 _mkB96.py(读对账件发射) ⇎ _mk96emit.py ⇎ _wire96.py ⇎ _fill96.py
# ============================================================================
import io, json, os, re, sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAWS = [u'corpus/raw/late96/fcc_2026-21821.txt']
ATOMFILE = u'corpus/_atoms96.txt'
MEASA = u'corpus/_tmp96_measA.json'
MEAS = u'corpus/_b96meas.json'
ENTRY = u'corpus/babeltele/B96_fcc_robocall_revocation_compression.md'

# --- SCAN BEGIN ---
def rd(p):
    return io.open(p, encoding='utf-8', errors='replace').read()


def pnorm(s):
    """最宽档: 小写 + 引号撇音符整枚删除 + 连字符族归一 + 只留 [0-9a-z 汉字 . - 空格] + 空白折一。"""
    s = s.lower()
    s = re.sub(u'[' + u'\u2019\u2018\'`\u00b4' + u']+', u'', s)
    s = re.sub(u'[\u2010-\u2015\u2212-]', u'-', s)
    s = re.sub(u'[^0-9a-z\u4e00-\u9fff\\-\\. ]+', u' ', s)
    return re.sub(u'\\s+', u' ', s).strip()


raw = rd(RAWS[0])
HEAD, BODY = raw.partition(u'\n\n')[0], raw.partition(u'\n\n')[2]
LINES = BODY.split(chr(10))
FLAT = u' '.join(BODY.split())
LOW = FLAT.lower()
PN = pnorm(FLAT)
ROWF = [pnorm(u' '.join(l.split())) for l in LINES]      # 单行最宽档面
ROWSL = [u' '.join(l.split()) for l in LINES]            # 单行折空白档面


def cnt_sub(needle, face):
    return face.count(needle)


def occ_in_line(needle):
    """严格档: 针完整落在某一行(行内空白折一)内的出现次数, 逐行用游标环数, 非重叠。"""
    n = needle.lower()
    tot = 0
    for l in ROWSL:
        k, m = 0, l.lower()
        while True:
            j = m.find(n, k)
            if j < 0:
                break
            tot += 1
            k = j + len(n)
    return tot


def cnt_tok(needle, face):
    """token 档: 前后邻字不得是 [0-9a-z](下划线连字符都算边界; 与 \\b 不同档)。"""
    return len(re.findall(u'(?<![0-9a-z])' + re.escape(needle.lower()) + u'(?![0-9a-z])', face))


# —— 面尺(字符 ⇎ 词位 两把尺, 原文面 ⇎ 终规条文面分档) ——
F = {}
F['chars_body'] = [len(BODY)]
F['chars_flat'] = [len(FLAT)]
F['ws_body'] = [sum(1 for ch in BODY if ch.isspace())]
runs, prev = 0, True
for ch in BODY:
    w = ch.isspace()
    if w and not prev:
        runs += 1
    prev = w
F['ws_runs'] = [runs]
F['ws_runs_interior'] = [runs - (1 if BODY[:1].isspace() else 0) - (1 if BODY[-1:].isspace() else 0)]
F['flat_identity_gap'] = [F['chars_body'][0] - F['ws_body'][0] + F['ws_runs_interior'][0] - F['chars_flat'][0]]
F['words_flat'] = [len(FLAT.split())]
F['words_line_sum'] = [sum(len(l.split()) for l in LINES)]
F['words_line_gap'] = [F['words_line_sum'][0] - F['words_flat'][0]]
F['lines_nl'] = [len(LINES)]
F['lines_sl'] = [len(BODY.splitlines())]
F['lines_tail_nl'] = [1 if BODY.endswith(chr(10)) else 0]
F['lines_nonblank'] = [len([l for l in LINES if l.strip()])]
F['lines_blank'] = [F['lines_nl'][0] - F['lines_nonblank'][0]]
F['line_longest'] = [max(len(l) for l in LINES)]
F['tokens_total'] = [len(re.findall(u"[0-9a-z']+", LOW))]
F['tokens_distinct'] = [len(set(re.findall(u"[0-9a-z']+", LOW)))]
F['tokens_repeat'] = [F['tokens_total'][0] - F['tokens_distinct'][0]]
F['tokens_vs_words_gap'] = [F['tokens_total'][0] - F['words_flat'][0]]
F['tokens_sum_close'] = [sum(Counter(re.findall(u"[0-9a-z']+", LOW)).values()) - F['tokens_total'][0]]
_wcls = {'alpha': 0, 'num': 0, 'mixed': 0, 'punct': 0}
for w in FLAT.split():
    ha = bool(re.search(u'[a-z]', w.lower()))
    hd = bool(re.search(u'[0-9]', w))
    _wcls['mixed' if (ha and hd) else ('num' if hd else ('alpha' if ha else 'punct'))] += 1
F['word_alpha'] = [_wcls['alpha']]
F['word_num'] = [_wcls['num']]
F['word_mixed'] = [_wcls['mixed']]
F['word_punct'] = [_wcls['punct']]
F['word_shape_gap'] = [sum(_wcls.values()) - F['words_flat'][0]]

# —— 区域档: 序文 ⇎ 终规条文(以独占一行的 'Final Rules' 为界) ——
ir = next(i for i, l in enumerate(LINES) if l.strip() == u'Final Rules')
PRE = u' '.join(chr(10).join(LINES[:ir]).split()).lower()
RULE = u' '.join(chr(10).join(LINES[ir:]).split()).lower()
F['rule_start_line'] = [ir]
F['lines_pre'] = [ir]
F['lines_rule'] = [len(LINES) - ir]
F['lines_region_gap'] = [F['lines_pre'][0] + F['lines_rule'][0] - len(LINES)]
F['chars_flat_pre'] = [len(PRE)]
F['chars_flat_rule'] = [len(RULE)]
F['words_flat_rule'] = [len(RULE.split())]

SUB_KW = [u'consent', u'revocation', u'revoke', u'revocations', u'revocation request', u'revoke all',
          u'exclusive means', u'exclusive', u'caller', u'callers', u'called party', u'text message',
          u'robocall', u'informational', u'telemarketing', u'advertisement', u'business days',
          u'ten business days', u'reasonable time', u'reasonable means', u'reasonable manner',
          u'rebuttable presumption', u'totality of circumstances', u'financial institution',
          u'reliable source', u'prior express consent', u'prior express written consent',
          u'64.1200', u'tcpa', u'commission', u'cgb', u'enforcement bureau',
          u'reassigned numbers database', u'paperwork reduction act', u'congressional review act',
          u'regulatory flexibility act', u'small business administration', u'delegate', u'delegation',
          u'standardized words', u'confirmation', u'effective', u'synopsis', u'commenter',
          u'amend', u'revising', u'supersede', u'further notice of proposed rulemaking', u'end']
for k in SUB_KW:
    F['n_sub_' + k.replace(u' ', u'_')] = [cnt_sub(k, LOW)]
REG_KW = [u'consent', u'revocation request', u'exclusive means', u'caller', u'text message',
          u'financial institution', u'revoke', u'robocall']
for k in REG_KW:
    a, b = cnt_sub(k, PRE), cnt_sub(k, RULE)
    F['n_pre_' + k.replace(u' ', u'_')] = [a]
    F['n_rule_' + k.replace(u' ', u'_')] = [b]
    F['n_region_gap_' + k.replace(u' ', u'_')] = [a + b - F['n_sub_' + k.replace(u' ', u'_')][0]]
TOK_KW = [u'caller', u'callers', u'text', u'stop', u'quit', u'end', u'revoke', u'cancel',
          u'unsubscribe', u'opt out', u'consent', u'robocall', u'robocalls', u'telemarketing']
for k in TOK_KW:
    F['n_tok_' + k.replace(u' ', u'_')] = [cnt_tok(k, LOW)]
# 同一枚词的两把尺(子串档 ⇎ 词形档)之差: 子串档里 end 会把 amend/extend/send 的词尾也算进来
F['end_word_gap'] = [F['n_sub_end'][0] - F['n_tok_end'][0]]

# —— 三档口径的针池: 严格档(单行内) ⇎ 容行档(整面折平) ⇎ 最宽档(去标点) ——
CHAIN = [
    u'A called party may revoke prior express consent, including prior express written consent',
    u'Callers may designate any of the following methods as the exclusive means to revoke consent',
    u'an automated, interactive voice or key press-activated opt-out mechanism on a call',
    u'must be honored within a reasonable time not to exceed ten business days from receipt of such request',
    u'The use of any means to revoke consent not listed in paragraph (a)(10) of this section creates a rebuttable presumption',
    u'a totality of circumstances analysis will determine whether the caller can demonstrate',
    u'Callers that do not designate an exclusive means to revoke consent pursuant to paragraph (a)(10)',
    u'must process revocation requests made by any reasonable means',
    u'Callers may interpret a revocation request made in response to an informational call',
    u'Revocation requests made in response to calls or text messages that contain an advertisement',
    u'If the confirmation text is sent within five minutes of receipt',
    u'two-way texting is not available due to technical limitations of the texting protocol',
    u'supplied by a spouse or other family member who is authorized to be on the account',
    u'The revised rule amendments contained herein become effective November 25, 2026',
    u'previously extended to January 31, 2027',
    u'We make clear that substantive changes to these rules are excluded from this delegation of authority',
]
F['chain_n'] = [len(CHAIN)]
F['chain_strict_occ'] = [sum(occ_in_line(x) for x in CHAIN)]
F['chain_flat_occ'] = [sum(LOW.count(x.lower()) for x in CHAIN)]
F['chain_xline_occ'] = [F['chain_flat_occ'][0] - F['chain_strict_occ'][0]]
F['chain_needles_noline'] = [len([x for x in CHAIN if occ_in_line(x) == 0])]
F['chain_needles_oneline'] = [len([x for x in CHAIN if occ_in_line(x) > 0])]
F['chain_needles_hit'] = [len([x for x in CHAIN if LOW.count(x.lower()) > 0])]
F['chain_pnorm_occ'] = [sum(PN.count(pnorm(x)) for x in CHAIN)]
F['chain_shell_only'] = [len([x for x in CHAIN if LOW.count(x.lower()) == 0 and pnorm(x) in PN])]

NEG = [u'must be honored within ten business days', u'within ten business days from receipt',
       u'two business days', u'five business days', u'thirty business days', u'ten calendar days',
       u'immediately upon receipt', u'within 24 hours', u'one revocation request revokes all consent',
       u'revoke all categories of robocalls', u'must provide a revoke all method',
       u'effective january 31, 2027', u'opt-in', u'revocation must be processed within one business day',
       u'callers are required to honor every revocation regardless of method',
       u'confirmation text may include marketing information']
F['neg_n'] = [len(NEG)]
F['neg_strict'] = [sum(occ_in_line(x) for x in NEG)]
F['neg_flat'] = [sum(LOW.count(x.lower()) for x in NEG)]
F['neg_pnorm'] = [sum(PN.count(pnorm(x)) for x in NEG)]
F['neg_checks'] = [F['neg_n'][0] * 3]

ATOMS = [
    u'A called party may revoke prior express consent, including prior express written consent, to receive calls or text messages made pursuant to paragraphs (a)(1) through (3) and (c)(2) of this section',
    u'Callers may designate any of the following methods as the exclusive means to revoke consent',
    u'an automated, interactive voice or key press-activated opt-out mechanism on a call',
    u'must be honored within a reasonable time not to exceed ten business days from receipt of such request',
    u'The use of any means to revoke consent not listed in paragraph (a)(10) of this section creates a rebuttable presumption that the consumer has revoked consent when the called party satisfies their obligation to produce evidence that such a request has been made, absent evidence to the contrary',
    u'a totality of circumstances analysis will determine whether the caller can demonstrate that a request to revoke consent has not been conveyed in a reasonable manner',
    u'Callers may interpret a revocation request made in response to an informational call or text message (i.e., a call or text message that does not contain any advertising or telemarketing) as applying only to the specific category of informational robocalls and text messages to which the revocation was directed and not to all communications',
    u'Revocation requests made in response to calls or text messages that contain an advertisement or constitute telemarketing revoke consent to all future calls or text messages containing an advertisement or constitute telemarketing from that caller',
    u'If the confirmation text is sent within five minutes of receipt, it will be presumed to fall within the consumer\u2019s prior express consent',
    u'Callers that do not designate an exclusive means to revoke consent pursuant to paragraph (a)(10) of this section must process revocation requests made by any reasonable means',
    u'supplied by a spouse or other family member who is authorized to be on the account; obtained when the customer calls the financial institution; or included in records obtained from another financial institution',
    u'The revised rule amendments contained herein become effective November 25, 2026',
    u'previously extended to January 31, 2027',
    u'supersede the delayed effective date of the relevant portion of that rule that was previously extended to January 31, 2027',
    u'We make clear that substantive changes to these rules are excluded from this delegation of authority',
    u'two-way texting is not available due to technical limitations of the texting protocol',
    u"following standardized words: ``stop,'' ``quit,'' ``end,'' ``revoke,'' ``opt out,'' ``cancel,'' or ``unsubscribe''",
    u'Text senders that designate a reply text message as the exclusive means to revoke consent can satisfy the disclosure obligation by including at least one of the standardized words',
    u'The Chief Counsel did not file any comments in response to the proposed rules in this proceeding',
]
F['atom_pool'] = [len(ATOMS)]
F['atom_flat_hit'] = [len([a for a in ATOMS if LOW.count(a.lower()) > 0])]
F['atom_pnorm_hit'] = [len([a for a in ATOMS if pnorm(a) in PN])]
F['atom_strict'] = [len([a for a in ATOMS if occ_in_line(a) > 0])]
F['atom_xline'] = [F['atom_pnorm_hit'][0] - F['atom_strict'][0]]
F['atom_shell_only'] = [len([a for a in ATOMS if LOW.count(a.lower()) == 0 and pnorm(a) in PN])]
F['atom_bad'] = [F['atom_pool'][0] - F['atom_pnorm_hit'][0]]
F['atom_checks'] = [F['atom_pool'][0] * 3]

# —— 结构档: 表格行 ⇎ 枚举措 ⇎ 标题字母 ⇎ 句节 ——
t1 = next(i for i, l in enumerate(LINES) if u'Table 1--' in l)
t2 = next(i for i, l in enumerate(LINES) if u'Table 2--' in l)
SEG1 = LINES[t1:t2]
SEG2 = LINES[t2:]
rows1 = [l for l in SEG1 if re.search(u'\\s\\d{6}\\s', l)]
F['t1_rows'] = [len(rows1)]
F['t1_naics'] = [len(set(re.findall(u'\\s(\\d{6})\\s', chr(10).join(rows1))))]


def pct_close(row):
    """行尾三格(总家数 ⇎ 小家数 ⇎ 百分比)现算: round(100*小/总,2) 与印出的百分比是否同值。"""
    nums = re.findall(u'\\d[\\d,]*(?:\\.\\d+)?', row)
    if len(nums) < 3:
        return None
    tot, small, pc = nums[-3], nums[-2], nums[-1]
    calc = round(100.0 * int(small.replace(u',', u'')) / int(tot.replace(u',', u'')), 2)
    return abs(calc - float(pc.replace(u',', u''))) < 0.005


def judge(rows, tag):
    j = [pct_close(l) for l in rows]
    F[tag + u'_pct_ok'] = [len([x for x in j if x is True])]
    F[tag + u'_pct_bad'] = [len([x for x in j if x is False])]
    F[tag + u'_pct_na'] = [len([x for x in j if x is None])]


judge(rows1, u't1')
rows2dot = [l for l in SEG2 if re.search(u'\\.{5,}\\s+[\\d,]+\\s+[\\d,]+\\s+[\\d.]+\\s*$', l)]
rows2tail = [l for l in SEG2 if re.search(u'\\s([\\d,]{2,})\\s+([\\d,]{2,})\\s+(\\d{2,3}\\.\\d{2})\\s*$', l)]
judge(rows2tail, u't2')
F['t2_rows_dot'] = [len(rows2dot)]
F['t2_rows_tail'] = [len(rows2tail)]
F['t2_rows_nodot'] = [F['t2_rows_tail'][0] - F['t2_rows_dot'][0]]
F['naics_cells'] = [len(re.findall(u'\\s\\d{6}\\s', chr(10).join(SEG1)))]
F['dollars_distinct'] = [len(set(re.findall(u'\\$[\\d,.]+ million', chr(10).join(SEG1))))]
F['pct_two_dp'] = [len(re.findall(u'\\d{2}\\.\\d{2}', FLAT))]
m = re.search(u'standardized words: (.*?)and/or', FLAT, re.S)
F['std_words'] = [len(re.findall(u'``([^\'\u2019]+?)\'\'', m.group(1)))] if m else [0]
PHRASE = re.search(u'revising paragraphs (.*?) to read as follows', FLAT).group(1)
_items = [x for x in re.split(u', and |, ', PHRASE) if re.search(u'\\d', x)]
F['para_items'] = [len(_items)]
F['para_cells'] = [PHRASE.count(u')')]
F['amend_instr'] = [len([l for l in LINES if re.match(u'^\\d+\\. \\S', l.strip())])]
_HL = [l for l in LINES if re.match(u'^[A-L]\\. [A-Z][a-z]', l.strip())]
_HR = [l for l in LINES if re.match(u'^(I|II|III)\\. [A-Z]', l.strip())]
F['heads_letters'] = [len(_HL)]
F['heads_roman'] = [len(_HR)]
F['heads_overlap'] = [len([l for l in _HL if re.match(u'^I\\. ', l.strip())])]
F['heads_union'] = [F['heads_letters'][0] + F['heads_roman'][0] - F['heads_overlap'][0]]
F['page_shells'] = [len([l for l in LINES if re.match(u'^\\[\\[Page \\d+\\]\\]$', l.strip())])]
_pg = re.findall(u'\\[\\[Page (\\d+)\\]\\]', BODY)
F['page_first'] = [int(re.search(u'Pages (\\d+)-', BODY).group(1))]
F['page_last'] = [int(re.findall(u'Pages \\d+-(\\d+)', BODY)[0])]
F['pages_span'] = [F['page_last'][0] - F['page_first'][0] + 1]
F['zero_lines'] = [len([l for l in LINES if l.strip() == u'0'])]
F['sents_flat'] = [len([s for s in re.split(u'(?<=[.!?]) ', FLAT) if s.strip()])]
_spre = [s for s in re.split(u'(?<=[.!?]) ', PRE) if s.strip()]
_srule = [s for s in re.split(u'(?<=[.!?]) ', RULE) if s.strip()]
F['sents_pre'] = [len(_spre)]
F['sents_rule'] = [len(_srule)]
F['sents_region_gap'] = [F['sents_pre'][0] + F['sents_rule'][0] - F['sents_flat'][0]]
F['sents_ten_days'] = [len([s for s in _srule if u'ten business days' in s.lower()])]
F['sents_five_min'] = [len([s for s in _srule if u'five minutes' in s.lower()])]
F['sents_must'] = [len([s for s in _srule if re.search(u'\\bmust\\b', s.lower())])]
F['date_nov25'] = [LOW.count(u'november 25, 2026')]
F['date_jan27'] = [LOW.count(u'january 31, 2027')]
F['months_12'] = [LOW.count(u'12 months')]
F['usc_cites'] = [len(re.findall(u'U\\.S\\.C\\.', FLAT))]
F['sec_cites'] = [cnt_tok(u'sec', LOW)]
# --- SCAN END ---

for k in (u'flat_identity_gap', u'words_line_gap', u'word_shape_gap', u'tokens_sum_close',
          u'lines_region_gap', u'chain_shell_only', u'atom_bad', u't1_pct_bad', u't1_pct_na',
          u't2_pct_bad', u't2_pct_na', u'neg_strict', u'neg_flat', u'neg_pnorm',
          u'sents_region_gap'):
    assert F[k][0] == 0, u'B96 SCAN 闭合差非零: %s = %s' % (k, F[k][0])
assert F['t1_pct_ok'][0] + F['t1_pct_na'][0] == F['t1_rows'][0], u'表一判定的行数与行数尺不合'
assert F['t2_pct_ok'][0] + F['t2_pct_na'][0] == F['t2_rows_tail'][0], u'表二判定的行数与行数尺不合'
assert F['heads_union'][0] == F['heads_letters'][0] + F['heads_roman'][0] - F['heads_overlap'][0], u'标题两档容斥不合'
assert F['chain_needles_noline'][0] + F['chain_needles_oneline'][0] == F['chain_n'][0], u'链针的两档枚数不合'
assert F['tokens_repeat'][0] == F['tokens_total'][0] - F['tokens_distinct'][0], u'词次与唯一词形之差挪动'
for k in REG_KW:
    g = F[u'n_region_gap_' + k.replace(u' ', u'_')][0]
    assert g == 0, u'区域闭合差非零: %s = %d' % (k, g)
assert F['atom_pnorm_hit'][0] == F['atom_pool'][0], u'锚池里有穿不到最宽档的串'
assert F['chain_needles_hit'][0] == F['chain_n'][0], u'规则链里有穿不到折平档的针'
assert F['lines_nl'][0] == F['lines_sl'][0] + F['lines_tail_nl'][0], u'行式两档差不等于尾换行枚数'
assert F['chain_strict_occ'][0] + F['chain_xline_occ'][0] == F['chain_flat_occ'][0], u'跨行差不闭合'
assert F['atom_strict'][0] + F['atom_xline'][0] == F['atom_pnorm_hit'][0], u'锚的跨行账不闭合'
assert F['t2_pct_ok'][0] == F['t2_rows_tail'][0], u'表二有行的百分比复算不上'
assert F['t1_pct_ok'][0] == F['t1_rows'][0], u'表一有行的百分比复算不上'

io.open(MEASA, 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
print(u'A 侧量测: %d 枚键 → %s' % (len(F), MEASA))
for k in sorted(F):
    print(u'  %-28s %s' % (k, F[k][0]))

# ---- 对账件读取(第二套实现 _pick96.py 写的逐键对账; 没有它就只用 A 侧读数) ----
A = F
if os.path.exists(MEAS):
    M = json.load(io.open(MEAS, encoding='utf-8'))
    assert set(M) == set(A), u'对账件与本遍键集不合: 缺 %s 多 %s' % (
        sorted(set(A) - set(M))[:6], sorted(set(M) - set(A))[:6])
    for k in sorted(A):
        assert A[k][0] == M[k][0], u'A 侧重跑读数挪动: %s %s ⇎ %s' % (k, M[k][0], A[k][0])
        assert M[k][0] == M[k][1], u'对账件里两套读数不合: %s' % k
    F = M
    print(u'对账件已复核: %d 枚键, A 侧重跑逐键同值' % len(F))
else:
    print(u'对账件未生成(先跑 corpus/_pick96.py), 本遍用 A 侧读数发射')

# ---- 发射条目 ----
REG = {}


def V(name):
    v = F[name][0]
    REG.setdefault(str(v), u"B96V('%s')" % name)
    return v


io.open(ATOMFILE, 'w', encoding='utf-8', newline=chr(10)).write(
    chr(10).join(ATOMS) + chr(10))

E = []
E.append(u'🧭 源账: FCC 终规 2026-21821(91 FR 67214-67219, 2026-10-26 刊出; CG Docket No. 02-278; '
         u'FCC 26-67; 47 CFR part 64; Effective November 25, 2026)——撤销 robocall 同意的终规+序文+FRFA, '
         u'govinfo pre 剥标签留硬换行 %d 行(非空 %d), 折平 %d 字符⇎%d 词⇎词次 %d(唯一词形 %d); '
         u'句 %d(序文 %d ⇎ 终规条文 %d), 表 2 张 ⇎ 页壳 %d 枚 ⇎ 跨页 %d 页。'
         % (V('lines_sl'), V('lines_nonblank'), V('chars_flat'), V('words_flat'), V('tokens_total'),
            V('tokens_distinct'), V('sents_flat'), V('sents_pre'), V('sents_rule'),
            V('page_shells'), V('pages_span')))
E.append(u'⛓ 规则链 %d 环逐环留针: 严格档(针完整落在单行内)只读通 %d 处, 容行档(整面折平)读通 %d 处, '
         u'跨行 %d 处——FR 硬换行把 %d 枚针切断, 唯一完整落在一行内的是 ⟦M⟧⟨previously extended to January 31, 2027⟩。'
         % (V('chain_n'), V('chain_strict_occ'), V('chain_flat_occ'), V('chain_xline_occ'),
            V('chain_needles_noline')))
E.append(u'① 撤销权: 被叫方撤的是 (a)(1)-(3) 与 (c)(2) 段下的同意 '
         u'⟦A⟧⟨A called party may revoke prior express consent, including prior express written consent, '
         u'to receive calls or text messages made pursuant to paragraphs (a)(1) through (3) and (c)(2) of this '
         u'section⟩——prior express consent %d 处 ⇎ 带 written 的那档 %d 处。'
         % (V('n_sub_prior_express_consent'), V('n_sub_prior_express_written_consent')))
E.append(u'② 专属方式三选: 主叫可指定唯一撤销途径 ⟦B⟧⟨Callers may designate any of the following methods as the '
         u'exclusive means to revoke consent⟩——(i) 自动语音或按键 opt-out 装置 ⟦C⟧⟨an automated, interactive voice or '
         u'key press-activated opt-out mechanism on a call⟩⇎(ii) 回标准词 ⇎(iii) 指定网站或电话; '
         u'exclusive means %d 处(序文 %d ⇎ 条文 %d)。'
         % (V('n_sub_exclusive_means'), V('n_pre_exclusive_means'), V('n_rule_exclusive_means')))
E.append(u'③ 标准词 %d 枚逐字: ⟦Q⟧⟨following standardized words: ``stop,\x27\x27 ``quit,\x27\x27 ``end,\x27\x27 '
         u'``revoke,\x27\x27 ``opt out,\x27\x27 ``cancel,\x27\x27 or ``unsubscribe\x27\x27\x27\x27⟩——词形档(前后非字母数字) '
         u'stop %d ⇎ quit %d ⇎ end %d ⇎ revoke %d ⇎ cancel %d ⇎ unsubscribe %d ⇎ opt out %d; '
         u'子串档 end %d 处⇎词形档 %d 处, 差 %d(amend ⇎ extend ⇎ send 这类词尾被子串档计入, 词形档只认独立成词的 end); '
         u'只回一条文本的主叫可以只嵌其中一枚 '
         u'⟦R⟧⟨Text senders that designate a reply text message as the exclusive means to revoke consent can satisfy '
         u'the disclosure obligation by including at least one of the standardized words⟩。'
         % (V('std_words'), V('n_tok_stop'), V('n_tok_quit'), V('n_tok_end'), V('n_tok_revoke'),
            V('n_tok_cancel'), V('n_tok_unsubscribe'), V('n_tok_opt_out'), V('n_sub_end'),
            V('n_tok_end'), V('end_word_gap')))
E.append(u'④ 时限: 撤销请求须在合理时间内且不超过十个工作日办理 ⟦D⟧⟨must be honored within a reasonable time '
         u'not to exceed ten business days from receipt of such request⟩——同一句在 (a)(10) ⇎ (a)(11) 各印一次'
         u'(ten business days %d 处 ⇎ business days %d 处 ⇎ 条文句 %d 句含它)。'
         % (V('n_sub_ten_business_days'), V('n_sub_business_days'), V('sents_ten_days')))
E.append(u'⑤ 未指定即全接: 不指定专属方式的主叫须处理任何合理方式的撤销 ⟦J⟧⟨Callers that do not designate an '
         u'exclusive means to revoke consent pursuant to paragraph (a)(10)⟩; 用未列举方式撤销 ⇒ 可反驳推定已撤销'
         u'⟦E⟧⟨The use of any means to revoke consent not listed in paragraph (a)(10) of this section creates a '
         u'rebuttable presumption⟩(rebuttable presumption %d 处)⇎ 再按情境整体判定 ⟦F⟧⟨a totality of circumstances '
         u'analysis will determine whether the caller can demonstrate⟩(totality of circumstances %d 处)。'
         % (V('n_sub_rebuttable_presumption'), V('n_sub_totality_of_circumstances')))
E.append(u'⑥ 范围分档(新规的心脏): 信息类通话的撤销只及于所指类别 ⟦G⟧⟨Callers may interpret a revocation request '
         u'made in response to an informational call⟩⇎含广告或构成电话营销的撤销及于该主叫全部未来营销 ⟦H⟧⟨Revocation '
         u'requests made in response to calls or text messages that contain an advertisement⟩——'
         u'revocation request %d 处(序文 %d ⇎ 条文 %d)⇎ revoke all %d 处 ⇎ 撤销只及单类的 informational %d 处。'
         % (V('n_sub_revocation_request'), V('n_pre_revocation_request'), V('n_rule_revocation_request'),
            V('n_sub_revoke_all'), V('n_sub_informational')))
E.append(u'⑦ 确认短信: 五分钟内发出的确认推定在既有同意内 ⟦I⟧⟨If the confirmation text is sent within five minutes '
         u'of receipt⟩, 更久须自证延迟合理; 确认文本只准确认 ⇎ 不得含营销或促销信息(sents 含 five minutes %d 句)。'
         % V('sents_five_min'))
E.append(u'⑧ 单向文本协议: 不能用回信文本者须在每条文本里显著披露两向文本不可用并给出合理替代撤销途径 '
         u'⟦P⟧⟨two-way texting is not available due to technical limitations of the texting protocol⟩。')
E.append(u'⑨ 金融机构豁免的可靠来源三档 ⟦K⟧⟨supplied by a spouse or other family member who is authorized to be on '
         u'the account; obtained when the customer calls the financial institution; or included in records obtained '
         u'from another financial institution⟩——reliable source %d 处 ⇎ financial institution %d 处(序文 %d ⇎ 条文 %d)。'
         % (V('n_sub_reliable_source'), V('n_sub_financial_institution'),
            V('n_pre_financial_institution'), V('n_rule_financial_institution')))
E.append(u'⑩ 生效链: 新规 %d 处印 November 25, 2026 生效 ⟦L⟧⟨The revised rule amendments contained herein become '
         u'effective November 25, 2026⟩, 并取代此前被推迟到 January 31, 2027 的那部分 ⟦N⟧⟨supersede the delayed '
         u'effective date of the relevant portion of that rule that was previously extended to January 31, 2027⟩; '
         u'延长至刊发后 12 个月的请求被拒(months_12 %d 处), 一键全撤的义务没写进本终规而是转 FNPRM 再征意见'
         u'(further notice %d 处)。'
         % (V('date_nov25'), V('months_12'), V('n_sub_further_notice_of_proposed_rulemaking')))
E.append(u'⑪ 授权链: CGB 会同 Enforcement Bureau 重排 64.1200 的可读性 ⇎ 实质变更明确排除在授权之外 '
         u'⟦O⟧⟨We make clear that substantive changes to these rules are excluded from this delegation of authority⟩'
         u'(delegate %d 处 ⇎ delegation %d 处 ⇎ enforcement bureau %d 处)。'
         % (V('n_sub_delegate'), V('n_sub_delegation'), V('n_sub_enforcement_bureau')))
E.append(u'🧾 程序侧: PRA 非实质修改(Public Law 104-13, paperwork reduction act %d 处)⇎ RFA 已备 FRFA 且 IRFA 零意见 '
         u'(regulatory flexibility act %d 处)⇎ CRA 已送国会与 GAO(5 U.S.C. 801(a)(1)(A), congressional review act %d 处)'
         u'⇎ 法律授权 = 通信法 sections 1-5 与 section 227; 署名 Marlene Dortch Secretary; '
         u'首席顾问对拟规零意见 ⟦S⟧⟨The Chief Counsel did not file any comments in response to the proposed rules in '
         u'this proceeding⟩; '
         u'修正指令 %d 条 ⇎ 被改段落 %d 项(括号格 %d 枚)⇎ 字母标题 %d 枚 ⇎ 罗马号标题 %d 枚 ⇎ 并集 %d 枚(交叠 %d 枚是 I.)。'
         % (V('n_sub_paperwork_reduction_act'), V('n_sub_regulatory_flexibility_act'),
            V('n_sub_congressional_review_act'), V('amend_instr'), V('para_items'), V('para_cells'),
            V('heads_letters'), V('heads_roman'), V('heads_union'), V('heads_overlap')))
E.append(u'📊 小实体账(本条现算): 全美 34.75 million businesses ⇎ 99.9%% 为小企业 ⇎ '
         u'48,724 out of 90,835 地方政府人口不足 fifty thousand; 表一 %d 行(唯一 NAICS %d 枚 ⇎ 六位码格 %d 枚), '
         u'行尾三格复算 round(100×小家/总家, 2) 对 %d 行 ⇎ 错 %d 行; 表二按末三格取行 %d 行 ⇎ 按点线引导取行 %d 行'
         u'(差 %d 行: Satellite 那行没有点线), 复算对 %d 行 ⇎ 错 %d 行; 两位小数百分比全篇 %d 枚。'
         % (V('t1_rows'), V('t1_naics'), V('naics_cells'), V('t1_pct_ok'), V('t1_pct_bad'),
            V('t2_rows_tail'), V('t2_rows_dot'), V('t2_rows_nodot'), V('t2_pct_ok'), V('t2_pct_bad'),
            V('pct_two_dp')))
E.append(u'🚫 反向 %d 枚针 × 三档 = %d 次全部零命中(最宽档也零): 裸式 within ten business days 读不通(十个工作日只是上限, '
         u'原文必带 a reasonable time not to exceed)⇎ 没有两/五/三十个工作日档 ⇎ 没有 immediately upon receipt ⇎ '
         u'没有 24 小时档 ⇎ 没有强制一键全撤义务 ⇎ 确认短信可含营销——原文明文禁止。'
         % (V('neg_n'), V('neg_checks')))
E.append(u'ℒ 方法 ⇒ 截止后规章文本的压缩判据: 规则链 %d 环逐环留针并给两把尺(严格档 %d ⇎ 容行档 %d), '
         u'可执行字段逐字不碰(十个工作日 ⇎ 五分钟 ⇎ 七枚标准词 ⇎ November 25, 2026), 表格行按行尾三格现算复验, '
         u'程序词频与区域档(序文 %d ⇎ 条文 %d 字符)做成键。'
         % (F['chain_n'][0], F['chain_strict_occ'][0], F['chain_flat_occ'][0],
            V('chars_flat_pre'), V('chars_flat_rule')))

enc = u'\n'.join(E)
assert not re.search(u'%[sd]', enc), u'残留占位符'
n_tags = len(re.findall(u'⟦[A-Z]⟧', enc))
n_atoms = len(re.findall(u'⟨', enc))
assert n_tags == n_atoms, u'标签 %d ≠ 锚 %d' % (n_tags, n_atoms)
SRC_ALL = PN.replace(u' ', u'')
missing = []
for m in re.finditer(u'\\d[\\d.]*', enc):
    tok = m.group(0).rstrip(u'.')
    if tok in REG or pnorm(tok).replace(u' ', u'') in SRC_ALL:
        continue
    missing.append(tok)
assert not missing, u'无着落 token: %s' % sorted(set(missing))
_used = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
for a in _used:
    assert pnorm(a) in PN, u'编码锚穿不到最宽档: %s' % a[:50]
# 标签 ⇎ 原文块的绑定: ⟦X⟧ 只准引原始区第 X 块里的字面串(位置由 ATOMS 次序定)
LET = {chr(65 + i): ATOMS[i] for i in range(len(ATOMS))}
assert sorted(LET) == [chr(65 + i) for i in range(len(ATOMS))], u'标签字母表溢出 26 或次序乱'
_pairs = re.findall(u'⟦([A-Z])⟧⟨([^⟨⟩]+)⟩', enc)
assert len(_pairs) == n_atoms, u'有锚没紧跟标签(或标签在前): 配对 %d ⇎ 锚 %d' % (len(_pairs), n_atoms)
for t, a in _pairs:
    assert t in LET, u'标签 %s 没有对应的原文块' % t
    assert pnorm(a) in pnorm(LET[t]), u'锚 ⟦%s⟧ 引的串不在第 %s 块内: %s' % (t, t, a[:60])
assert set(t for t, _ in _pairs) == set(LET), u'候选锚池里有条块没被编码区引用: %s' % sorted(
    set(LET) - set(t for t, _ in _pairs))

orig = u'### ⟦A⟧ ⟸ ' + RAWS[0] + u'\n\n' + u'\n\n'.join(ATOMS)
title = (u'# B96 单文本压缩: FCC 撤销 robocall 同意终规 2026-21821(%d 词, 截止后专业信息)→算子中文——'
         u'规则链 %d 环逐环留针, 七枚标准词与两档时限逐字保真\n' % (F['words_flat'][0], F['chain_n'][0]))
srcline = (u'src: %s (%d 字符, 硬换行 %d 行) '
           u'(单文本压缩: 源=Federal Register 2026-10-26 刊出的 FCC 终规, govinfo pre 剥标签+实体还原, '
           u'刊发次日即入库; 数字/段落号/日期一律逐字保留)\n'
           % (RAWS[0], F['chars_flat'][0], F['lines_sl'][0]))
tagsline = (u'tags: 单文本压缩 截止后专业信息 规则链逐环保真键(撤销⇒专属方式⇒七词⇒十日⇒五分钟⇒推定⇒范围⇒生效⇒授权) '
            u'三档口径键(严格档⇎容行档⇎最宽档) 表格行现算键(19+13 行百分比复算) 反向零命中键(%d 枚×三档) '
            u'锚归属由正文现推 闭合账 标量 3⇎清单 %d 项\n' % (F['neg_n'][0], F['chain_n'][0]))
md = (title + srcline + u'; ' + tagsline + u'## [[原始语料|ORIGINAL]]\n' + orig
      + u'\n\n## ⟪BabelTele⟫\n' + enc + u'\n\n## ⛓解读注\n\n(待 _fill96.py 第二遍独立复算后写回)\n')
io.open(ENTRY, 'w', encoding='utf-8', newline=chr(10)).write(md)
print(u'B96 建条目: %s' % ENTRY)
print(u'编码区 %d 字符(不含换行), 编码区锚 %d 处, 候选锚 %d 条, 登记面值 %d 枚'
      % (len(enc.replace(chr(10), u'')), n_atoms, len(ATOMS), len(REG)))
assert REG, u'REG 空——V() 没登记任何面值'
io.open(u'corpus/_b96flat.json', 'w', encoding='utf-8').write(
    json.dumps(REG, ensure_ascii=False, sort_keys=True) + chr(10))
print(u'DERIV 键表: corpus/_b96flat.json %d 键' % len(REG))
