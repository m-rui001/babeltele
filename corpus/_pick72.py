# -*- coding: utf-8 -*-
"""采集遍(B72, 第一套实现): “收到 30x 之后 POST 到底能不能改成 GET”交四份 HTTP 一手规范各答一遍
2616 ⇎ 7231 ⇎ 7538 ⇎ 9110。本遍只用一种机制(正则字面轨 + 行切片), 输出 _b72meas.json 给建条目侧
(_mkB72.py, 第二套实现: 非重叠游标 ⇎ 集合代数 ⇎ 段落双尺)逐键对账。

两条采集侧现读的形状差(都影响“逐字跨行”能不能读到, 必须在本遍就量出来):
(1) 9110 是这一族里唯一**不带换页符**的一份(也无页壳可剥), 且带 BOM 与若干非 ASCII;
(2) 9110 把历史注释排成竖线引文块——每行行首多一枚 `|`、行中间也可能夹 `|`,
    于是“原面 ⇎ 全篇折平 ⇎ 摘壳折平”三档都读不到那句 MAY, 只有再剥掉引文竖线的第四档读得到。
    本遍把这一档立成 quote 面并单列计数, 转义层如实点名。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
LBL = [u'2616', u'7231', u'7538', u'9110']
SRC = [u'corpus/raw/httpRedir/rfc2616.txt', u'corpus/raw/httpRedir/rfc7231.txt',
       u'corpus/raw/httpRedir/rfc7538.txt', u'corpus/raw/httpRedir/rfc9110.txt']
M = {}

# ---------- 面量 ----------
T, L, BYT = [], [], []
for p in SRC:
    b = io.open(p, 'rb').read()
    BYT.append(b)
    t = b.decode('utf-8', 'replace')
    assert not set(t) & set(u'\x1c\x1d\x1e\x1f'), p
    T.append(t)
    L.append(t.split(u'\n'))
M['bytes'] = [len(b) for b in BYT]
M['chars'] = [len(t) for t in T]
M['lines'] = [len(L[i]) for i in range(4)]
M['lines_nl'] = [T[i].count(u'\n') + 1 for i in range(4)]
M['nonblank'] = [len([x for x in L[i] if x.strip() != u'']) for i in range(4)]
M['cr'] = [T[i].count(u'\r') for i in range(4)]
M['ff'] = [T[i].count(u'\x0c') for i in range(4)]
M['ff_exact'] = [len([x for x in L[i] if x == u'\x0c']) for i in range(4)]
M['ff_only'] = [len([x for x in L[i] if x.strip() == u'\x0c']) for i in range(4)]
M['nonascii'] = [len([c for c in T[i] if ord(c) > 127]) for i in range(4)]
M['bom'] = [1 if BYT[i][:3] == b'\xef\xbb\xbf' else 0 for i in range(4)]
M['nonascii_extra'] = [sum(len(c.encode('utf-8')) - 1 for c in T[i] if ord(c) > 127) for i in range(4)]
M['byte_cp_delta'] = [M['bytes'][i] - M['chars'][i] for i in range(4)]
M['maxlen'] = [max(len(x) for x in L[i]) for i in range(4)]
M['ascii_all'] = sum(1 for i in range(4) if M['nonascii'][i] == 0)
M['pipe_lines'] = [len([x for x in L[i] if x.lstrip().startswith(u'|')]) for i in range(4)]
assert M['byte_cp_delta'] == [M['bytes'][i] - M['chars'][i] for i in range(4)]
assert M['cr'] == [0, 0, 0, 0]
assert M['ff'][3] == 0 and M['bom'][3] == 1 and M['ascii_all'] == 3


def is_shell(x):
    s = x.rstrip()
    if s == u'':
        return True
    if re.match(u'^[ \\t]*\\S.*\\[Page \\d+\\][ \\t]*$', s):
        return True
    if re.match(u'^[ \\t]*RFC \\d{4} ', s):
        return True
    return False


M['shell_n'] = [len([x for x in L[i] if is_shell(x)]) for i in range(4)]
M['shell_strip'] = [M['lines'][i] - M['shell_n'][i] for i in range(4)]
assert M['shell_n'][3] < M['shell_n'][0]

# ---------- 答句针(本遍用正则字面轨, 建条目侧改用字面针逐枚复现) ----------
PATS = [
    (0, u'p2616_301_must_not_auto', u'MUST NOT automatically redirect the request unless'),
    (0, u'p2616_301_note_erroneous', u'will erroneously change it into a GET request'),
    (0, u'p2616_302_note_not_allowed', u'specify that the client is not allowed'),
    (0, u'p2616_302_note_treat_as_303', u'treat 302 as if it were a 303'),
    (0, u'p2616_303_should_get', u'SHOULD be retrieved using a GET method'),
    (0, u'p2616_307_repeat_original', u'repeat the original request on the new URI'),
    (1, u'p7231_301_hist_may', u'MAY change the request method from POST to GET'),
    (1, u'p7231_302_hist_may', u'For historical reasons'),
    (1, u'p7231_307_must_not_change', u'MUST NOT change the request method'),
    (1, u'p7231_303_retrieval', u'perform a retrieval request targeting that URI'),
    (1, u'p7231_306_reserved', u'no longer used'),
    (2, u'p7538_308_indicates', u'The 308 \\(Permanent Redirect\\) status code indicates'),
    (2, u'p7538_308_not_allow_changing', u'does not allow changing the request method'),
    (2, u'p7538_cacheable_default', u'A 308 response is cacheable by default'),
    (2, u'p7538_restricted', u'the use of status code 308 is restricted'),
    (2, u'p7538_obsoletes_7238', u'Obsoletes: 7238'),
    (3, u'p9110_302_hist_may', u'MAY change the request method from POST to GET'),
    (3, u'p9110_historical_reasons', u'For historical reasons'),
    (3, u'p9110_converged', u'converged on changing the method to GET'),
    (3, u'p9110_step_change_method', u'Change the request method according to the redirecting status'),
    (3, u'p9110_307_must_not_change', u'MUST NOT change the request method'),
    (3, u'p9110_308_indicates', u'The 308 \\(Permanent Redirect\\) status code indicates'),
    (3, u'p9110_305_deprecated', u'is now deprecated'),
    (3, u'p9110_306_reserved', u'the code is reserved'),
]
PR = dict((k, p) for _, k, p in PATS)
M['needle_n'] = len(PATS)
FOLD = [re.sub(u'\\s+', u' ', t) for t in T]
SHF = [re.sub(u'\\s+', u' ', u'\n'.join([x for x in L[i] if not is_shell(x)])) for i in range(4)]
# 第四档: 剥竖线引文标记(9110 的注排版), 其余三份面上无引文竖线 ⇒ 该档与折平档同读数
QF = [re.sub(u'\\s+', u' ', u'\n'.join(re.sub(u'^\\s*\\| ?', u'', re.sub(u'\\|\\s*$', u'', x)) for x in L[i]))
      for i in range(4)]
M['p_strict'] = {}
M['p_fold'] = {}
M['p_sh'] = {}
M['p_quote'] = {}
M['p_lines'] = {}
for o, k, _ in PATS:
    pat = PR[k]
    M['p_strict'][k] = len([x for x in L[o] if re.search(pat, x)])
    M['p_fold'][k] = len(re.findall(pat, FOLD[o]))
    M['p_sh'][k] = len(re.findall(pat, SHF[o]))
    M['p_quote'][k] = len(re.findall(pat, QF[o]))
    hits = [n for n, x in enumerate(L[o], 1) if re.search(pat, x)]
    M['p_lines'][k] = hits[0] if hits else None
    if M['p_quote'][k] == 0:
        print(u'针落空(最宽档也 0): %s %s' % (LBL[o], k))
own = lambda i, f: len([k for o, k, _ in PATS if o == i and f[k]])
STRICT = [own(i, M['p_strict']) for i in range(4)]
FOLDT = [own(i, M['p_fold']) for i in range(4)]
SHT = [own(i, M['p_sh']) for i in range(4)]
QT = [own(i, M['p_quote']) for i in range(4)]
M['sn_strict_docs'] = STRICT
M['sn_fold_docs'] = FOLDT
M['sn_sh_docs'] = SHT
M['sn_quote_docs'] = QT
M['fold_only_own'] = [FOLDT[i] - STRICT[i] for i in range(4)]
M['fold_only_n'] = sum(M['fold_only_own'])
M['sh_minus_fold'] = [FOLDT[i] - SHT[i] for i in range(4)]
M['quote_minus_sh'] = [QT[i] - SHT[i] for i in range(4)]
M['quote_only_n'] = sum(M['quote_minus_sh'])
M['dead_needles'] = [k for o, k, _ in PATS if M['p_quote'][k] == 0]
assert all(STRICT[i] <= FOLDT[i] and SHT[i] <= FOLDT[i] and SHT[i] <= QT[i] for i in range(4))
M['ladder_monotone'] = 1
assert all(STRICT[i] + M['fold_only_own'][i] == FOLDT[i] for i in range(4))
assert M['quote_only_n'] > 0 and M['sh_minus_fold'] == [0, 0, 0, 0]

# ---------- 措辞档位(同一问题的四族答法, 按字面族全库计数) ----------
TIERP = [u'not allowed', u'MUST NOT automatically redirect', u'MAY change the request method',
         u'MUST NOT change the request method', u'does not allow changing', u'erroneously']
M['tier_pats'] = TIERP
M['tier_faces'] = [[len(re.findall(p, QF[i])) for p in TIERP] for i in range(4)]
M['tier_tot'] = [sum(M['tier_faces'][i]) for i in range(4)]
M['confirm_gate'] = [len(re.findall(u'MUST NOT automatically redirect', QF[i])) for i in range(4)]
assert M['confirm_gate'][0] > 0 and sum(M['confirm_gate'][1:]) == 0

# ---------- 30x 小节块界(标题行只取正文, TOC 由 Introduction 行之前的候选剔除) ----------
HDR = [u'^\\s*10\\.3\\.\\d+ 30\\d', u'^\\s*6\\.4\\.\\d+\\.?  30\\d', u'^\\s*3\\.  308 Permanent',
       u'^\\s*15\\.4\\.\\d+\\.?  30\\d']
M['sec_heads'] = []
for i in range(4):
    intro = [n for n, x in enumerate(L[i], 1) if re.match(u'^1\\.\\s+Introduction\\s*$', x.rstrip())]
    lo = intro[0] if intro else 0
    hd = [(n, x.strip()) for n, x in enumerate(L[i], 1) if re.search(HDR[i], x) and n > lo]
    M['sec_heads'].append(hd)
    print(u'%s 正文小节 %d 个: %s' % (LBL[i], len(hd), [h[1][:24] for h in hd]))
assert [len(x) for x in M['sec_heads']] == [8, 7, 1, 9], [len(x) for x in M['sec_heads']]
M['codes'] = [sorted(set(re.search(u'30\\d', h[1]).group(0) for h in M['sec_heads'][i])) for i in range(4)]
M['code_n'] = [len(x) for x in M['codes']]
assert M['code_n'] == [8, 7, 1, 9]

# ---------- 名分头与年份 ----------
M['obs'] = [(x.strip() if x else None) for x in
            [[y for y in L[i] if y.startswith(u'Obsoletes:')][0] if any(y.startswith(u'Obsoletes:') for y in L[i]) else u'' for i in range(4)]]
M['upd'] = [[y for y in L[i] if y.startswith(u'Updates:')] for i in range(4)]
M['obs_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{4}', (M['obs'][i] or u'').split(u'  ')[0]))) for i in range(4)]
M['upd_ids'] = [sorted(set(int(y) for y in re.findall(u'\\d{4}', (M['upd'][i][0] if M['upd'][i] else u'')))) for i in range(4)]
M['target_ids'] = sorted(set([x for i in range(4) for x in M['obs_ids'][i] + M['upd_ids'][i]]))
M['years'] = []
M['months'] = []
for i in range(4):
    g = None
    for x in L[i][:80]:
        m = re.search(u'(January|February|March|April|May|June|July|August|September|October|November|December) (\\d{4})', x)
        if m:
            g = m
            break
    assert g, LBL[i]
    M['years'].append(int(g.group(2)))
    M['months'].append(g.group(1))
M['year_inversions'] = len([1 for i in range(3) if M['years'][i + 1] < M['years'][i]])
M['year_gaps'] = [M['years'][i + 1] - M['years'][i] for i in range(3)]
assert M['year_inversions'] == 0 and M['years'] == [1999, 2014, 2015, 2022]

# ---------- 共用长行池(归一后取交, 逐字节同形另计) ----------


def pn(s):
    return u' '.join(s.lower().split())


PL = [set(pn(x) for x in L[i] if len(pn(x)) >= 40 and not is_shell(x)) for i in range(4)]
VARY = [{} for _ in range(4)]
for i in range(4):
    for y in L[i]:
        if len(pn(y)) >= 40 and not is_shell(y):
            VARY[i].setdefault(pn(y), set()).add(y.rstrip(u'\r'))
PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
M['pair_lbl'] = [u'%s·%s' % (LBL[a], LBL[b]) for a, b in PAIRS]
M['pair_share'] = [len(PL[a] & PL[b]) for a, b in PAIRS]
RAWS = [set(x.rstrip(u'\r') for x in L[i] if len(pn(x)) >= 40 and not is_shell(x)) for i in range(4)]
M['pair_byte'] = [len(RAWS[a] & RAWS[b]) for a, b in PAIRS]
M['pair_norm_only'] = [M['pair_share'][n] - M['pair_byte'][n] for n in range(6)]
assert all(M['pair_norm_only'][n] >= 0 for n in range(6))
M['pair_nonzero'] = len([x for x in M['pair_share'] if x])
PRES = dict((a, tuple(i for i in range(4) if a in PL[i])) for s in PL for a in s)
M['pool_n'] = len(PRES)
M['pool_tier'] = [len([a for a, v in PRES.items() if len(v) == k]) for k in range(1, 5)]
assert sum(M['pool_tier']) == M['pool_n']
M['pool_3'] = M['pool_tier'][2]
M['pool_4'] = M['pool_tier'][3]
M['pair_max'] = max(M['pair_share'])
M['pair_max_lbl'] = M['pair_lbl'][M['pair_share'].index(M['pair_max'])]

# 写法分家: 归一相同 ⇎ 逐字节不同 ⇒ 按最弱闭合档归一桶(case > hyph > space > multi)
BUCK = {u'case': 0, u'hyph': 0, u'space': 0, u'multi': 0}
CAND = set()
for a, b in PAIRS:
    for x in PL[a] & PL[b]:
        if any(p == q for p in VARY[a][x] for q in VARY[b][x]):
            continue
        CAND.add(x)
for x in sorted(CAND):
    cls = None
    for a, b in PAIRS:
        if x not in PL[a] & PL[b]:
            continue
        for p in VARY[a][x]:
            for q in VARY[b][x]:
                if p == q:
                    continue
                if p.lower() == q.lower():
                    w = u'case'
                elif re.sub(u'-\\s*', u'', p).lower() == re.sub(u'-\\s*', u'', q).lower():
                    w = u'hyph'
                elif p.strip() == q.strip():
                    w = u'space'
                else:
                    w = u'multi'
                rank = {u'case': 0, u'hyph': 1, u'space': 2, u'multi': 3}
                cls = w if cls is None else (cls if rank[cls] <= rank[w] else w)
    BUCK[cls] += 1
M['axis_distinct'] = len(CAND)
M['axis_counts'] = BUCK
assert sum(BUCK.values()) == len(CAND)
M['axis_str'] = u'case%d⇎hyph%d⇎space%d⇎multi%d' % (BUCK[u'case'], BUCK[u'hyph'], BUCK[u'space'], BUCK[u'multi'])

json.dump(M, io.open(u'corpus/_b72meas.json', 'w', encoding='utf-8'), indent=1, sort_keys=True)
print(u'采集遍: 字节 ' + u'⇎'.join(str(x) for x in M['bytes']) + u' ｜ 行 ' + u'⇎'.join(str(x) for x in M['lines'])
      + u' ｜ 换页 ' + u'⇎'.join(str(x) for x in M['ff']) + u' ｜ 壳行 ' + u'⇎'.join(str(x) for x in M['shell_n'])
      + u' ｜ 竖线行 ' + u'⇎'.join(str(x) for x in M['pipe_lines']))
print(u'针 ' + str(M['needle_n']) + u' 枚四档: 原面 ' + u'⇎'.join(str(x) for x in STRICT) + u' ｜ 折平 '
      + u'⇎'.join(str(x) for x in FOLDT) + u' ｜ 摘壳 ' + u'⇎'.join(str(x) for x in SHT) + u' ｜ 剥引文 '
      + u'⇎'.join(str(x) for x in QT) + u' ｜ 折行独有 ' + str(M['fold_only_n']) + u' ｜ 剥引文独有 '
      + str(M['quote_only_n']) + u' ｜ 死集 ' + str(M['dead_needles']))
print(u'措辞档 ' + u' ⇎ '.join(str(M['tier_tot'][i]) for i in range(4)) + u' ｜ 确认门 '
      + u'⇎'.join(str(x) for x in M['confirm_gate']) + u' ｜ 池 ' + str(M['pool_n']) + u' 档 '
      + u'⇎'.join(str(x) for x in M['pool_tier']) + u' ｜ 最大对 ' + M['pair_max_lbl'] + u' ' + str(M['pair_max']))
print(u'年份 ' + u'⇎'.join(str(x) for x in M['years']) + u' ｜ 废止 ' + u' ⇎ '.join(str(x) for x in M['obs_ids'])
      + u' ｜ 更新 ' + u' ⇎ '.join(str(x) for x in M['upd_ids']) + u' ｜ 轴 ' + M['axis_str'])
