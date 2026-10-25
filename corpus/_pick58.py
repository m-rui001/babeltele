# -*- coding: utf-8 -*-
"""B58 第一遍(采集侧): 四份 FIRST 一手文书的机读量 + 可执行复现。

轴: 同一条向量该打几分。
  T = cvss_v30_spec.html  v3.0 规范: 闭式算术(Round up / 6.42 / 7.52 / 8.22 / 指数 15), 符号名 ISCBase/ISCModified,
      权重表把四个取值并排塞进同一格(用 <br> 分隔)
  O = cvss_v31_spec.html  v3.1 规范: 基础分与 v3.0 同式同系数(可复算证明), 符号名换成 ISS/MISS,
      Roundup 换成整数伪码并自陈浮点陷阱, 环境分把指数 15 改成 13 并乘 0.9731 且明文"differs from CVSS v3.0",
      权重表改成一格一取值(同一个度量族占多行, 首格留空)
  F = cvss_v40_spec.html  v4.0 规范: 全文一个算式都不给(无 Roundup/8.22/6.42), 换成 MacroVector + EQ1..EQ6
      布尔约束表 + 查表 + 插值; 另加 Safety/Provider Urgency 两套非数值档
  N = cvss_examples.html  算例文档: 同一个 CVE 的 v3.1 分数与 v4.0 分数并排列出, 列头自写口径(Base ⇎ Base+Threat ⇎
      Base+Threat+Environmental), 表式在块与块之间就不统一(2 列 ⇎ 3 列, 分数与向量同格 ⇎ 分行)

规则: 本遍全部系数与权重从文书自己的方程段与表内解析得到, 一个都不手填(手填就等于把记忆当成文档)。
转义层: 先剥标签与注释, 后解 HTML 实体, 再把 × − – NBSP 折成 ASCII; 顺序颠倒会让 &lt; 被当成开标签吃掉后半行。
输出 corpus/_b58meas.json。
"""
import io, json, os, re, sys, math, hashlib
from collections import Counter
from fractions import Fraction as Fr

sys.stdout.reconfigure(encoding='utf-8')
RAW = u'corpus/raw/cvss/'
PATHS = [RAW + u'cvss_v30_spec.html', RAW + u'cvss_v31_spec.html',
         RAW + u'cvss_v40_spec.html', RAW + u'cvss_examples.html']
TAGS = [u'T', u'O', u'F', u'N']
LBL = [u'v3.0 规范', u'v3.1 规范', u'v4.0 规范', u'算例文档']
NL = chr(10)
M = {}


def put(k, v):
    M[k] = v
    return v


ENT = [(u'&nbsp;', u' '), (u'&amp;', u'&'), (u'&lt;', u'<'), (u'&gt;', u'>'),
       (u'&quot;', u'"'), (u'&times;', u'x'), (u'&minus;', u'-'), (u'&#8722;', u'-'),
       (u'&#215;', u'x')]
UNI = [(u'\u00a0', u' '), (u'\u2212', u'-'), (u'\u2013', u'-'), (u'\u2014', u'-'),
       (u'\u00d7', u'x'), (u'\u2018', u"'"), (u'\u2019', u"'"), (u'\u201c', u'"'),
       (u'\u201d', u'"')]


def fold(s):
    for a, b in UNI:
        s = s.replace(a, b)
    return s


def strip(s, br=u' '):
    """剥注释→<br>换分隔→剥标签→解实体→折 Unicode→收空白(保留换行)。"""
    s = re.sub(u'(?s)<!--.*?-->', u'', s)
    s = re.sub(u'(?is)<br[^>]*>', br, s)
    s = re.sub(u'(?s)<[^>]+>', u'', s)
    for a, b in ENT:
        s = s.replace(a, b)
    s = fold(s)
    s = re.sub(u'[ \\t]+', u' ', s)
    return re.sub(u'(?m)^ +| +$', u'', s).strip()


def trs(html):
    return re.findall(u'(?is)<tr[^>]*>(.*?)</tr>', html)


def raw_cells(tr):
    return re.findall(u'(?is)<t[dh][^>]*>(.*?)</t[dh]', tr)


def tables(html):
    return re.findall(u'(?is)<table[^>]*>(.*?)</table>', html)


TXT = [io.open(p, encoding='utf-8', errors='replace').read() for p in PATHS]
RB = [io.open(p, 'rb').read() for p in PATHS]
LST = [t.split(NL) for t in TXT]
BLK = [[(raw_cells(tr), [strip(c) for c in raw_cells(tr)]) for tr in trs(TXT[i])]
       for i in range(4)]

# ---------- 形状档 ----------
put(u'bytes', [len(RB[i]) for i in range(4)])
put(u'chars', [len(TXT[i]) for i in range(4)])
put(u'lines', [len(LST[i]) - 1 for i in range(4)])
put(u'nonblank', [len([l for l in LST[i] if l.strip()]) for i in range(4)])
put(u'tabs', [TXT[i].count(chr(9)) for i in range(4)])
put(u'cr', [RB[i].count(b'\r') for i in range(4)])
put(u'trailws', [len([l for l in LST[i] if l[-1:] in (u' ', chr(9))]) for i in range(4)])
put(u'nonascii', [len([c for c in TXT[i] if not c.isascii()]) for i in range(4)])
put(u'bom', [1 if RB[i][:3] == b'\xef\xbb\xbf' else 0 for i in range(4)])
put(u'maxlen', [max(len(l) for l in LST[i]) for i in range(4)])
NB = [len([l for l in LST[i] if l.strip()]) for i in range(4)]
put(u'meanlen', [int(round(1.0 * sum(len(l) for l in LST[i] if l.strip()) / max(1, NB[i])))
                  for i in range(4)])
put(u'final_nl', [1 if TXT[i].endswith(NL) else 0 for i in range(4)])
MX = [max(len(l) for l in LST[i]) for i in range(4)]
put(u'maxline_hash', [hashlib.sha256([l for l in LST[i] if len(l) == MX[i]][0]
                                     .encode(u'utf-8')).hexdigest()[:12] for i in range(4)])
put(u'maxline_shared', len(set(M[u'maxline_hash'])))
put(u'maxline_n', [len([l for l in LST[i] if len(l) == MX[i]]) for i in range(4)])
SHA = [hashlib.sha256(RB[i]).hexdigest() for i in range(4)]
put(u'sha16', [x[:16] for x in SHA])
put(u'sha_distinct', len(set(M[u'sha16'])))
put(u'multisign', [TXT[i].count(u'\u00d7') for i in range(4)])
put(u'minusuni', [TXT[i].count(u'\u2212') for i in range(4)])
put(u'ent_lt', [TXT[i].count(u'&lt;') for i in range(4)])
put(u'bs_escape', [len(re.findall(u'\\\\[<>=&*_]', TXT[i])) for i in range(4)])
put(u'nbsp_ent', [TXT[i].count(u'&nbsp;') for i in range(4)])
put(u'td_open', [len(re.findall(u'<td', TXT[i])) for i in range(4)])
put(u'tr_rows', [len(BLK[i]) for i in range(4)])
put(u'table_tags', [len(tables(TXT[i])) for i in range(4)])
put(u'br_tags', [len(re.findall(u'(?is)<br[^>]*>', TXT[i])) for i in range(4)])
put(u'code_tags', [len(re.findall(u'(?is)<code[^>]*>', TXT[i])) for i in range(4)])
put(u'h_levels', [[len(re.findall(u'(?is)<%s[^>]*>' % h, TXT[i])) for h in (u'h1', u'h2', u'h3')]
                  for i in range(4)])
put(u'h_all', [len(re.findall(u'(?is)<h[1-6][^>]*>', TXT[i])) for i in range(4)])
put(u'sup_tags', [len(re.findall(u'(?is)<sup[^>]*>', TXT[i])) for i in range(4)])

# ---------- 版本自写 ----------
put(u'title_first', [strip(re.search(u'(?is)<title[^>]*>(.*?)</title>', TXT[i]).group(1))
                     for i in range(4)])
put(u'h1_first', [strip(re.findall(u'(?is)<h1[^>]*>(.*?)</h1>', TXT[i])[0]) if
                  re.findall(u'(?is)<h1[^>]*>(.*?)</h1>', TXT[i]) else u'' for i in range(4)])
for v in (u'3.0', u'3.1', u'4.0'):
    put(u'ver_%s' % v.replace(u'.', u''), [TXT[i].count(u'v' + v) for i in range(4)])
put(u'ver_self', [[TXT[i].count(u'CVSS version %s' % v) for v in (u'3.0', u'3.1', u'4.0')]
                  for i in range(4)])

# ---------- 判分机制的词面指纹: 算术档 ----------
ARITH = [(u'Roundup', u'ru'), (u'Round up', u'ru_up'), (u'Minimum', u'min'), (u'Maximum', u'max'),
         (u'ISS', u'iss'), (u'MISS', u'miss'), (u'ISCBase', u'iscbase'),
         (u'ISCModified', u'iscmod'), (u'BaseScore', u'basescore'),
         (u'EnvironmentalScore', u'envscore'), (u'ModifiedImpact', u'modimpact'),
         (u'M.Impact', u'mdotimpact'), (u'Impact', u'impact'), (u'Exploitability', u'expl'),
         (u'6.42', u'k642'), (u'7.52', u'k752'), (u'3.25', u'k325'), (u'8.22', u'k822'),
         (u'1.08', u'k108'), (u'0.029', u'k029'), (u'0.915', u'k915'), (u'0.9731', u'k9731'),
         (u'0.30000000000000004', u'floatbug'), (u'Appendix A', u'appxa'),
         (u'pseudocode', u'pseudocode'), (u'floating point', u'floatpoint')]
for w, k in ARITH:
    put(u'ar_%s' % k, [TXT[i].count(w) for i in range(4)])
put(u'ar_exp15', [len(re.findall(u'\\](15|\\^15)\\b', TXT[i])) + TXT[i].count(u')15') for i in range(4)])
put(u'ar_exp13', [TXT[i].count(u')13') + TXT[i].count(u'^13') for i in range(4)])
put(u'arith_any', [1 if (u'Roundup' in TXT[i] or u'Round up' in TXT[i]) else 0 for i in range(4)])

# ---------- 判分机制的词面指纹: 布尔/查表档 ----------
BOOLW = [(u'MacroVector', u'mv'), (u'interpolation', u'interp'), (u'lookup table', u'lookup'),
         (u'Constraints', u'cons'), (u'equivalence class', u'eqclass'),
         (u'Highest Severity Vector', u'hsv'), (u'worst case', u'worst'),
         (u'Negligible', u'negligible'), (u'Provider Urgency', u'provurg'),
         (u'Known Exploited Vulnerabilities', u'kev_full'), (u'CISA', u'cisa'),
         (u'Safety', u'safety'), (u'Attack Requirements', u'at'), (u'pass-through', u'passthru')]
for w, k in BOOLW:
    put(u'bl_%s' % k, [TXT[i].count(w) for i in range(4)])
put(u'eq_heads', [len(re.findall(u'\\bEQ[1-6]\\b', TXT[i])) for i in range(4)])
put(u'eq_with_levels', [len(re.findall(u'with (\\d+) levels', TXT[i])) for i in range(4)])
put(u'eq_determines', [len(re.findall(u'determines (\\d+) levels', TXT[i])) for i in range(4)])
put(u'eq_level_nums', [re.findall(u'(?:with|determines) (\\d+) levels', TXT[i]) for i in range(4)])
put(u'eq_tables', [len(re.findall(u'Table \\d+: (?:Joint )?EQ', TXT[i])) for i in range(4)])
put(u'tbl_captions', [[m2.group(0) for m2 in re.finditer(u'Table \\d+: [A-Za-z][^<]{0,44}', TXT[i])]
                      for i in range(4)])
put(u'tbl_n_refs', [len(re.findall(u'Table \\d+', TXT[i])) for i in range(4)])

# ---------- 方程段(按节切, 系数只从公式文字里取) ----------
def section(i, head, nxt):
    k = TXT[i].find(head)
    assert k >= 0, (i, head)
    e = TXT[i].find(nxt, k + len(head))
    assert e > k, (i, nxt)
    return strip(TXT[i][k:e], br=u' | ')


EQ0 = section(0, u'CVSS v3.0 Equations', u'8.4. Metrics Levels')
EQ1 = section(1, u'CVSS v3.1 equations', u'7.4. Metric Values')
put(u'eq0_len', len(EQ0))
put(u'eq1_len', len(EQ1))
put(u'eq0_lines', EQ0.count(NL) + 1)
put(u'eq1_lines', EQ1.count(NL) + 1)


def g1(seg, pat, who):
    r = re.findall(pat, seg)
    assert r, (who, pat, seg[:80])
    return r[0]


def one(seg, pat, who):
    x = g1(seg, pat, who)
    return float(x[0]) if isinstance(x, tuple) else float(x)


# v3.0: `Scope Unchanged 6.42 x ISCBase`, `Scope Changed 7.52 x [ISCBase-0.029] - 3.25 x [ISCBase-0.02]15`
BASE0 = re.compile(u'Scope Changed (\\d\\.\\d+) x \\[ISCBase-(\\d\\.\\d+)\\] - (\\d\\.\\d+) x '
                   u'\\[ISCBase-(\\d\\.\\d+)\\](\\d\\d)')
BASE1 = re.compile(u'Scope is Changed\\s*\\n?(\\d\\.\\d+) x \\(ISS - (\\d\\.\\d+)\\) - (\\d\\.\\d+) x '
                   u'\\(ISS - (\\d\\.\\d+)\\)(\\d\\d)')
p0 = BASE0.search(EQ0)
p1 = BASE1.search(EQ1)
assert p0 and p1, (bool(p0), bool(p1))
ENV0 = re.compile(u'Modified Scope Changed (\\d\\.\\d+) x \\[ISCModified-(\\d\\.\\d+)\\] - '
                  u'(\\d\\.\\d+) x \\[ISCModified-(\\d\\.\\d+)\\](\\d\\d)')
ENV1 = re.compile(u'ModifiedScope is Changed\\s*\\n?(\\d\\.\\d+) x \\(MISS - (\\d\\.\\d+)\\) - '
                  u'(\\d\\.\\d+) x \\(MISS x (\\d\\.\\d+) - (\\d\\.\\d+)\\)(\\d\\d)')
e0, e1 = ENV0.search(EQ0), ENV1.search(EQ1)
assert e0 and e1, (bool(e0), bool(e1))
C30 = {u'unch': one(EQ0, u'Scope Unchanged (-?\\d\\.\\d+) x ISCBase', u'0.unch'),
       u'c752': float(p0.group(1)), u'c325': float(p0.group(3)),
       u'p029': float(p0.group(2)), u'p02': float(p0.group(4)), u'exp': float(p0.group(5)),
       u'expl': one(EQ0, u'(\\d\\.\\d+) x AttackVector', u'0.expl'),
       u'f108': one(EQ0, u'Minimum \\[(\\d\\.\\d+) x \\(Impact', u'0.f108'),
       u'munch': one(EQ0, u'Modified Scope Unchanged (-?\\d\\.\\d+) x', u'0.munch'),
       u'm752': float(e0.group(1)), u'm325': float(e0.group(3)),
       u'mp029': float(e0.group(2)), u'mp02': float(e0.group(4)), u'mexp': float(e0.group(5)),
       u'mfactor': 1.0, u'cap': one(EQ0, u'\\],(\\d\\.\\d+)\\]', u'0.cap')}
C31 = {u'unch': one(EQ1, u'Scope is Unchanged\\s*\\n?(-?\\d\\.\\d+) x ISS', u'1.unch'),
       u'c752': float(p1.group(1)), u'c325': float(p1.group(3)),
       u'p029': float(p1.group(2)), u'p02': float(p1.group(4)), u'exp': float(p1.group(5)),
       u'expl': one(EQ1, u'(\\d\\.\\d+) x AttackVector', u'1.expl'),
       u'f108': one(EQ1, u'Minimum \\[(\\d\\.\\d+) x \\(Impact', u'1.f108'),
       u'munch': one(EQ1, u'ModifiedScope is Unchanged\\s*\\n?(-?\\d\\.\\d+) x MISS', u'1.munch'),
       u'm752': float(e1.group(1)), u'm325': float(e1.group(3)),
       u'mp029': float(e1.group(2)), u'mp02': float(e1.group(5)), u'mexp': float(e1.group(6)),
       u'mfactor': float(e1.group(4)), u'cap': one(EQ1, u'Minimum \\( 1 - \\[.*, (\\d\\.\\d+)\\)',
                                                    u'1.cap')}
put(u'coef_v30', C30)
put(u'coef_v31', C31)
BASEKEYS = (u'unch', u'c752', u'c325', u'expl', u'p029', u'p02', u'f108', u'exp')
put(u'coef_base_keynames', sorted(BASEKEYS))
put(u'coef_base_n', len(BASEKEYS))
put(u'coef_base_equal', [k for k in BASEKEYS if abs(C30[k] - C31[k]) < 1e-12])
put(u'coef_base_n_equal', len([k for k in BASEKEYS if abs(C30[k] - C31[k]) < 1e-12]))
put(u'coef_env_diff', [[k, C30[k], C31[k]] for k in sorted(C30)
                       if k in C31 and abs(C30[k] - C31[k]) > 1e-12])
put(u'coef_env_equal', [k for k in (u'munch', u'm752', u'm325', u'mp029', u'mp02', u'cap')
                        if abs(C30[k] - C31[k]) < 1e-12])
put(u'coef_all_keys', len(C30))
put(u'mfactor_absent_v30', [len(re.findall(u'MISS x \\d', EQ0)), len(re.findall(u'MISS x \\d', EQ1))])
put(u'selfdecl_diff', [len(re.findall(u'which differs from CVSS v3\\.0', TXT[i])) for i in range(4)])
put(u'diffnote_13', [TXT[i].count(u'exponent at the end') for i in range(4)])
put(u'symbol_iscbase', [TXT[i].count(u'ISCBase') for i in range(4)])
put(u'symbol_iss', [len(re.findall(u'\\bISS\\b', TXT[i])) for i in range(4)])
put(u'symbol_miss', [len(re.findall(u'\\bMISS\\b', TXT[i])) for i in range(4)])
put(u'symbol_round', [[TXT[i].count(u'Roundup'), TXT[i].count(u'Round up')] for i in range(4)])

# ---------- 权重表: 只认表头有 Numerical Value 的表 ----------
def is_numtab(trows):
    return any(len(c) == 3 and u'numerical value' in c[2].lower() for _, c in trows)


GRPKEY = [(u'attack vector', u'AV'), (u'attack complexity', u'AC'), (u'privilege', u'PR'),
          (u'user interaction', u'UI'), (u'c,i,a impact', u'CIA'),
          (u'confidentiality / integrity / availability', u'CIA'),
          (u'requirement', u'REQ'), (u'security requirements', u'REQ')]
VAL2AB = {u'network': u'N', u'adjacent': u'A', u'adjacent network': u'A', u'local': u'L',
          u'physical': u'P', u'none': u'N', u'low': u'L', u'medium': u'M', u'high': u'H',
          u'required': u'R', u'not defined': u'X'}
ALTRE = re.compile(u'^([0-9.]+)(?:\\s*\\(\\s*(?:or\\s+)?([0-9.]+)\\s+if Scope)?')


def wtables(i):
    out = []
    for t in tables(TXT[i]):
        rows = [(raw_cells(tr), [strip(c) for c in raw_cells(tr)]) for tr in trs(t)]
        if is_numtab(rows):
            out.append(rows)
    return out


def weights(i):
    out, nrows, ngrp, altrows, labels, unattr, lost = {}, 0, 0, 0, [], 0, []
    for rows in wtables(i):
        cur = None
        for raw, cells in rows:
            if len(cells) != 3:
                continue
            g = cells[0].lower()
            if g:
                labels.append(cells[0])
                hit = [ab for key, ab in GRPKEY if key in g]
                new = hit[-1] if hit else None
                if not hit:
                    unattr += 1
                if new != cur:
                    if new is not None:
                        ngrp += 1
                    cur = new
            if cur is None or not cells[1]:
                continue
            vs = [x.strip() for x in strip(raw[1], br=u'|').split(u'|') if x.strip()]
            ns = [x.strip() for x in strip(raw[2], br=u'|').split(u'|') if x.strip()]
            if len(vs) != len(ns):
                lost.append([cur, u'len', u'%d/%d' % (len(vs), len(ns))])
                continue
            for v, n in zip(vs, ns):
                ab = VAL2AB.get(v.lower())
                mm = ALTRE.match(n)
                if not ab or not mm:
                    lost.append([cur, v, n])
                    continue
                nrows += 1
                val = float(mm.group(1))
                alt = float(mm.group(2)) if mm.group(2) else val
                if mm.group(2):
                    altrows += 1
                if cur == u'CIA':
                    for p in (u'C', u'I', u'A'):
                        out[(p, ab, u'U')] = val
                        out[(p, ab, u'X')] = val
                elif cur == u'REQ':
                    out[(u'REQ', ab, u'U')] = val
                else:
                    out[(cur, ab, u'U')] = val
                    out[(cur, ab, u'X')] = alt if cur == u'PR' else val
    return out, nrows, ngrp, altrows, labels, unattr, lost


W30, NR30, NG30, ALT30, LB30, UA30, LO30 = weights(0)
W31, NR31, NG31, ALT31, LB31, UA31, LO31 = weights(1)
put(u'w_unattr_v30', UA30)
put(u'w_unattr_v31', UA31)
put(u'w_lost_v30', LO30)
put(u'w_lost_v31', LO31)
put(u'w_tab_n', [len(wtables(0)), len(wtables(1)), len(wtables(2)), len(wtables(3))])
put(u'w_rows_v30', NR30)
put(u'w_rows_v31', NR31)
put(u'w_groupheads_v30', NG30)
put(u'w_groupheads_v31', NG31)
put(u'w_altrows_v30', ALT30)
put(u'w_altrows_v31', ALT31)
put(u'w_triples_v30', len(W30))
put(u'w_triples_v31', len(W31))
put(u'w_common', len(set(W30) & set(W31)))
put(u'w_equal', len([k for k in set(W30) & set(W31) if abs(W30[k] - W31[k]) < 1e-12]))
put(u'w_unequal', [[list(k), W30[k], W31[k]] for k in sorted(set(W30) & set(W31))
                    if abs(W30[k] - W31[k]) > 1e-12])
put(u'w_unequal_n', len(M[u'w_unequal']))
put(u'w_only30', sorted([u'%s/%s/%s' % k for k in set(W30) - set(W31)]))
put(u'w_only31', sorted([u'%s/%s/%s' % k for k in set(W31) - set(W30)]))
put(u'w_cells_per_row_v30', [len([1 for _, c in r if len(c) == 3]) for r in
                             [rows for rows in wtables(0)]])
put(u'w_cells_per_row_v31', [len([1 for _, c in r if len(c) == 3]) for r in
                             [rows for rows in wtables(1)]])
put(u'w_label_variants', [[TXT[i].count(u'Privilege Required'), TXT[i].count(u'Privileges Required'),
                           TXT[i].count(u'Adjacent Network'), TXT[i].count(u'Adjacent'),
                           TXT[i].count(u'C,I,A Impact'), TXT[i].count(u'Confidentiality / Integrity')]
                           for i in range(4)])
put(u'w_alt_paren_or', [len(re.findall(u'\\(or [0-9.]+ if Scope', TXT[i])) for i in range(4)])
put(u'w_alt_paren_bare', [len(re.findall(u'\\([0-9.]+ if Scope', TXT[i])) for i in range(4)])
put(u'pr_alt_pair', [[W30.get((u'PR', u'L', u'U')), W30.get((u'PR', u'L', u'X')),
                      W30.get((u'PR', u'H', u'U')), W30.get((u'PR', u'H', u'X'))],
                     [W31.get((u'PR', u'L', u'U')), W31.get((u'PR', u'L', u'X')),
                      W31.get((u'PR', u'H', u'U')), W31.get((u'PR', u'H', u'X'))]])

# ---------- 分数实现 ----------
def roundup_pseudo(x):
    """v3.1 附录 A 的整数写法: 放大十万倍后向上进到 0.1。"""
    ii = int(round(x * 100000.0))
    if ii % 10000 == 0:
        return ii / 100000.0
    return (ii // 10000 + 1) / 10.0


def roundup_naive(x):
    import math
    return math.ceil(round(x, 10) * 10.0) / 10.0


AB2 = {u'N': u'N', u'A': u'A', u'L': u'L', u'P': u'P', u'M': u'M', u'H': u'H', u'R': u'R',
       u'X': u'X', u'U': u'U', u'C': u'C'}


def parse_vec(s):
    d = {}
    for part in s.split(u'/')[1:]:
        if u':' in part:
            k, v = part.split(u':', 1)
            d[k] = v
    return d


def _raw(vstr, W, C):
    """按文档公式算到取整之前: 返回 (状态, 未取整分数). 状态 ok/zero/bad."""
    d = parse_vec(vstr)
    sc = d.get(u'S')
    if sc not in (u'U', u'C'):
        return (u'bad', None)
    scope = u'X' if sc == u'C' else u'U'

    def wv(g):
        v = d.get(g)
        if v is None:
            return None
        return W.get((g, AB2.get(v, v), scope if g == u'PR' else u'U'))

    c, ii, a = wv(u'C'), wv(u'I'), wv(u'A')
    if None in (c, ii, a):
        return (u'bad', None)
    iss = 1.0 - (1 - c) * (1 - ii) * (1 - a)
    if sc == u'U':
        imp = C[u'unch'] * iss
    else:
        imp = C[u'c752'] * (iss - C[u'p029']) - C[u'c325'] * (iss - C[u'p02']) ** C[u'exp']
    av, ac, pr, ui = wv(u'AV'), wv(u'AC'), wv(u'PR'), wv(u'UI')
    if None in (av, ac, pr, ui):
        return (u'bad', None)
    expl = C[u'expl'] * av * ac * pr * ui
    if imp <= 0:
        return (u'zero', 0.0)
    return (u'ok', imp + expl if sc == u'U' else C[u'f108'] * (imp + expl))


def base_score(vstr, W, C, ru=roundup_pseudo):
    st, raw = _raw(vstr, W, C)
    if st == u'bad':
        return None
    if st == u'zero':
        return 0.0
    return ru(min(raw, 10.0))


def miss_of(cv, iv, av_, cr, ir, ar, C):
    return min(1.0 - (1 - cr * cv) * (1 - ir * iv) * (1 - ar * av_), C[u'cap'])


def mimp_changed(miss, C):
    """ModifiedScope=Changed 那一支(非单调就出在这里)。"""
    if miss <= 0:
        return 0.0
    return C[u'm752'] * (miss - C[u'mp029']) - C[u'm325'] * (miss * C[u'mfactor']
                                                             - C[u'mp02']) ** C[u'mexp']


CIA = [u'H', u'L', u'N']
REQ = [u'H', u'M', u'L']
combos = [(c, i, a, cr, ir, ar)
          for c in CIA for i in CIA for a in CIA for cr in REQ for ir in REQ for ar in REQ]
put(u'mono_combos', len(combos))
put(u'mono_cia', len(CIA) ** 3)
put(u'mono_req', len(REQ) ** 3)


def violations(C, W):
    """逐维把修改后影响升档 N→L→H, ModifiedImpact 不应下降; 返回违例组合集与统计。"""
    bad, pairs, worst = set(), 0, (0, None)
    bad_uncapped = set()
    order = {u'N': 0, u'L': 1, u'H': 2}
    nxt = {0: u'L', 1: u'H'}

    def missv(cb):
        return miss_of(*[W[(g, x, u'U')] for g, x in ((u'C', cb[0]), (u'I', cb[1]),
                                                     (u'A', cb[2]))],
                       *[W[(u'REQ', x, u'U')] for x in cb[3:6]], C=C)

    for cb in combos:
        m0 = missv(cb)
        f0 = mimp_changed(m0, C)
        for dim in range(3):
            if order[cb[dim]] == 2:
                continue
            nb = list(cb)
            nb[dim] = nxt[order[cb[dim]]]
            m1 = missv(tuple(nb))
            f1 = mimp_changed(m1, C)
            pairs += 1
            if f1 < f0 - 1e-12:
                bad.add((cb, dim))
                if m0 < C[u'cap'] - 1e-12 and m1 < C[u'cap'] - 1e-12:
                    bad_uncapped.add((cb, dim))
                if f0 - f1 > worst[0]:
                    worst = (f0 - f1, (cb, tuple(nb)))
    return bad, pairs, worst, bad_uncapped


b30, p30, w30x, u30 = violations(C30, W31)
b31, p31, w31x, u31 = violations(C31, W31)
put(u'mono_bad_v30formula', len(b30))
put(u'mono_bad_v31formula', len(b31))
put(u'mono_pairs', p30)
put(u'mono_pairs_close', p30 - p31)
put(u'mono_both', len(b30 & b31))
put(u'mono_only30', len(b30 - b31))
put(u'mono_only31', len(b31 - b30))
put(u'mono_ledger30', len(b30) - len(b30 & b31) - len(b30 - b31))
put(u'mono_uncapped30', len(u30))
put(u'mono_uncapped31', len(u31))
put(u'mono_capped30', len(b30) - len(u30))
put(u'mono_capped31', len(b31) - len(u31))
put(u'mono_worst_v30', [round(w30x[0], 6), list(w30x[1][0]), list(w30x[1][1])])
put(u'mono_worst_v31', [round(w31x[0], 6), list(w31x[1][0]), list(w31x[1][1])])
put(u'mono_req_from_doc', [W31[(u'REQ', x, u'U')] for x in REQ])
put(u'mono_cap', [C30[u'cap'], C31[u'cap']])

# ---------- 档位 ----------
SEVLABELS = (u'None', u'Low', u'Medium', u'High', u'Critical', u'Negligible')


def bands(i):
    out, vocab = [], set()
    for _, cells in BLK[i]:
        if cells and cells[0] in SEVLABELS:
            vocab.add(cells[0])
            m = re.match(u'^\\s*([0-9.]+)(?:\\s*(-|to)\\s*([0-9.]+))?\\s*$', cells[1] if len(cells) > 1 else u'')
            if m:
                lo = float(m.group(1))
                hi = float(m.group(3)) if m.group(3) else lo
                out.append((cells[0], lo, hi))
    return out, vocab


B, V = zip(*[bands(i) for i in range(4)])
B, V = list(B), list(V)
put(u'band_rows', [len(B[i]) for i in range(4)])
put(u'band_labels', [[x[0] for x in B[i]] for i in range(4)])
put(u'band_bounds', [[x[1:] for x in B[i]] for i in range(4)])
put(u'band_vocab', [sorted(V[i]) for i in range(4)])
put(u'band_vocab_n', [len(V[i]) for i in range(4)])
put(u'band_only40', sorted(set(x[0] for x in B[2]) - set(x[0] for x in B[1])))
put(u'band_only31', sorted(set(x[0] for x in B[1]) - set(x[0] for x in B[2])))
put(u'band_equal_30_31', 1 if [x for x in B[0]] == [x for x in B[1]] else 0)
put(u'band_equal_31_40', 1 if [x for x in B[1]] == [x for x in B[2]] else 0)
put(u'band_low_start', [[x[1] for x in B[i] if x[0] == u'Low'] for i in range(4)])
put(u'urgency_labels', [[len(re.findall(u'\\b%s\\b' % w, TXT[i]))
                         for w in (u'Red', u'Amber', u'Green', u'Clear')] for i in range(4)])
put(u'safety_labels', [[len(re.findall(u'\\b%s\\b' % w, TXT[i]))
                        for w in (u'Negligible', u'Moderate', u'Severe', u'Catastrophic')]
                       for i in range(4)])


def bandf(s, i):
    for name, lo, hi in B[i]:
        if lo <= s <= hi:
            return name
    return None


# ---------- 向量串与文法 ----------
VECRE = re.compile(u'CVSS:[34]\\.\\d(?:/[A-Z]{1,4}:[^/\\s"<>|&]+)+')
VEC = [VECRE.findall(TXT[i]) for i in range(4)]
put(u'vec_occ_raw', [len(VEC[i]) for i in range(4)])
put(u'vec_distinct_raw', [len(set(VEC[i])) for i in range(4)])
for v in (u'3.0', u'3.1', u'4.0'):
    put(u'vec_occ_raw_%s' % v.replace(u'.', u''), [len([x for x in VEC[i] if x.startswith(u'CVSS:' + v)])
                                               for i in range(4)])
    put(u'vec_distinct_raw_%s' % v.replace(u'.', u''),
        [len(set(x for x in VEC[i] if x.startswith(u'CVSS:' + v))) for i in range(4)])
put(u'vec_in_href', [len(re.findall(u'href="[^"]*CVSS:[34]\\.\\d/', TXT[i])) for i in range(4)])
put(u'vec_in_text', [len(re.findall(u'>CVSS:[34]\\.\\d/', TXT[i])) for i in range(4)])
put(u'vec_double_colon', [len(re.findall(u'[^:/]:/', TXT[i])) for i in range(4)])
put(u'vec_bad_slash', [len([x for x in VEC[i] if x.endswith(u'/') or u'//' in x]) for i in range(4)])
put(u'vec_pr_doublecolon', [len([x for x in VEC[i] if re.search(u':[A-Z]:[A-Z]:', x)])
                            for i in range(4)])
for g in (u'AV', u'AC', u'AT', u'PR', u'UI', u'S', u'C', u'I', u'A', u'VC', u'VI', u'VA',
          u'SC', u'SI', u'SA', u'E', u'T', u'K', u'R', u'V', u'CR', u'IR', u'AR', u'MAV',
          u'MAC', u'MPR', u'MVC', u'MSI', u'MVA', u'MSC', u'MSA', u'SP', u'CONF', u'INT',
          u'AVAIL'):
    put(u'grp_%s' % g, [len([x for x in VEC[i] if u'/' + g + u':' in x]) for i in range(4)])
put(u'vec_metric_kinds', [[len(set(p.split(u':')[0] for x in VEC[i]
                                    for p in x.split(u'/')[1:] if u':' in p))
                           for i in range(4)]][0])

# ---------- 算例文档: 按表头定列口径 ----------
SECT = re.compile(u'(?is)<h1[^>]*>(.*?)</h1>')
HDRRE = re.compile(u'^v([34]\\.\\d)(?:\\s+(.*))?$')
HITS = list(re.finditer(u'(?is)<(h[1-6])([^>]*)>(.*?)</h[1-6]>', TXT[3]))
put(u'h1_titles_n', len([h for h in HITS if h.group(1) == u'h1']))


def block_ranges():
    """标题文字里带 CVE 号的块: (CVE, 标题级别, 所属 h1 段, 正文)。"""
    rs = []
    for j, h in enumerate(HITS):
        if not re.search(u'CVE-\\d{4}-\\d+', h.group(3)):
            continue
        end = len(TXT[3])
        for k in HITS[j + 1:]:
            if int(k.group(1)[1]) <= int(h.group(1)[1]):
                end = k.start()
                break
        sect = u''
        for h2 in HITS[:j]:
            if h2.group(1) == u'h1':
                sect = strip(h2.group(3))
        rs.append((re.findall(u'CVE-\\d{4}-\\d+', strip(h.group(3)))[0], int(h.group(1)[1]),
                   sect, TXT[3][h.end():end]))
    return rs


RNG = block_ranges()
put(u'case_n', len(RNG))
put(u'case_h_level', [len([r for r in RNG if r[1] == lv]) for lv in (1, 2, 3, 4)])
put(u'case_sections', sorted(set(r[2] for r in RNG)))
put(u'case_by_section', [[s, len([r for r in RNG if r[2] == s])]
                         for s in sorted(set(r[2] for r in RNG))])


def cell_pair(x):
    """'7.0' 或 '8.1 CVSS:3.1/...' → (分数, 向量或 None)。"""
    m = re.match(u'^([0-9]\\.\\d)(?:\\s+(.*))?$', x)
    if not m:
        return None, None
    v = VECRE.search(m.group(2) or u'')
    return float(m.group(1)), (v.group(0) if v else None)


def pair_tables(body):
    """一张对照表 → 若干配对口径记录; 列的 v3.1/v4.0 身份只认表头。"""
    res = []
    for t in tables(body):
        rows = [[strip(c) for c in raw_cells(tr)] for tr in trs(t)]
        cols, hdr = {}, None
        for cells in rows:
            hits = [HDRRE.match(x) for x in cells]
            if sum(1 for h in hits if h) >= 2:
                hdr, cols = cells, {}
                for j, h in enumerate(hits):
                    if h:
                        cols[j] = (h.group(1), (h.group(2) or u'').strip())
                break
        if not hdr:
            continue
        n31 = len([1 for v in cols.values() if v[0] == u'3.1'])
        n40 = len([1 for v in cols.values() if v[0] == u'4.0'])
        labcol = 0 not in cols
        if not (n31 == 1 and n40 == 1):
            res.append({u'skip': u'multi31' if n31 > 1 else (u'multi40' if n40 > 1 else u'no31'),
                        u'ncols': len(hdr)})
            continue
        j1 = [j for j, v in cols.items() if v[0] == u'3.1'][0]
        j2 = [j for j, v in cols.items() if v[0] == u'4.0'][0]
        vecmap = {}
        for cells in rows:
            for j, x in enumerate(cells):
                if j < len(hdr) and x == hdr[j]:
                    continue
                vv = VECRE.search(x)
                if vv:
                    vecmap.setdefault(j, vv.group(0))
        for cells in rows:
            if cells == hdr:
                continue
            c1 = cell_pair(cells[j1]) if j1 < len(cells) else (None, None)
            c2 = cell_pair(cells[j2]) if j2 < len(cells) else (None, None)
            if c1[0] is None or c2[0] is None:
                continue
            lab = cells[0].strip() if (labcol and cells and cells[0]) else u''
            k1, k2 = cols[j1][1] or lab, cols[j2][1] or lab
            res.append({u'k31': k1, u's31': c1[0], u'v31': c1[1] or vecmap.get(j1),
                        u'k40': k2, u's40': c2[0], u'v40': c2[1] or vecmap.get(j2),
                        u'ncols': len(hdr),
                        u'spaced': bool(re.search(u'Base \\+', k2)),
                        u'nospace': bool(re.search(u'Base\\+', k2)),
                        u'samercell': bool(c1[1] or c2[1])})
    return res


RAWPT = [(cve, sect, p) for cve, lv, sect, body in RNG for p in pair_tables(body)]
SKIP = [p for _, _, p in RAWPT if u'skip' in p]
PT = [dict(p, cve=cve, sect=sect) for cve, sect, p in RAWPT if u'skip' not in p]
put(u'pair_tbl_n', len(PT) + len(SKIP))
put(u'pair_n', len(PT))
put(u'pair_skip', [[k, n] for k, n in sorted(Counter([p[u'skip'] for p in SKIP]).items())])
put(u'pair_with_both_vecs', len([p for p in PT if p[u'v31'] and p[u'v40']]))
put(u'pair_k31_blank', len([p for p in PT if p[u'k31'] == u'']))
put(u'pair_k31_base', len([p for p in PT if p[u'k31'] == u'Base']))
put(u'pair_k40_base', len([p for p in PT if p[u'k40'] == u'Base']))
put(u'pair_k40_composite', len([p for p in PT if u'+' in p[u'k40']]))
put(u'pair_k31blank_k40composite', len([p for p in PT if p[u'k31'] == u'' and u'+' in p[u'k40']]))
put(u'pair_kind_set', sorted(set((p[u'k31'], p[u'k40']) for p in PT)))
put(u'pair_40_spaced', len([p for p in PT if p[u'spaced']]))
put(u'pair_40_nospace', len([p for p in PT if p[u'nospace']]))
put(u'pair_score_vec_samecell', len([p for p in PT if p[u'samercell']]))
put(u'pair_ncols', sorted(set(p[u'ncols'] for p in PT)))
SP = [(p[u's31'], p[u's40']) for p in PT]
put(u'sp_n', len(SP))
D = [b - a for a, b in SP]
put(u'delta_pos', len([x for x in D if x > 1e-9]))
put(u'delta_neg', len([x for x in D if x < -1e-9]))
put(u'delta_zero', len([x for x in D if abs(x) <= 1e-9]))
put(u'delta_max', max(D))
put(u'delta_min', min(D))
put(u'delta_sum', round(sum(D), 6))
put(u'delta_absmean', round(sum(abs(x) for x in D) / len(D), 4))
BB = [(p[u's31'], p[u's40']) for p in PT if p[u'k40'] == u'Base' and p[u'k31'] in (u'', u'Base')]
DB = [b - a for a, b in BB]
put(u'delta_base_n', len(DB))
put(u'delta_base_sum', round(sum(DB), 6))
put(u'delta_base_up', len([x for x in DB if x > 1e-9]))
put(u'delta_base_down', len([x for x in DB if x < -1e-9]))
put(u'delta_base_same', len([x for x in DB if abs(x) <= 1e-9]))
put(u'delta_nonbase_n', len(SP) - len(DB))
put(u'delta_mix_minus_base', len(SP) - len(DB) - len(BB))
put(u'pair_k31_hist', sorted(Counter([p[u'k31'] for p in PT]).items()))
put(u'pair_k40_hist', sorted(Counter([p[u'k40'] for p in PT]).items()))
put(u'pair_k31_ledger', len(SP) - sum(n for _, n in M[u'pair_k31_hist']))
put(u'band_same', len([1 for (a, b) in SP if bandf(a, 1) and bandf(b, 1) and bandf(a, 1) == bandf(b, 1)]))
put(u'band_diff', len([1 for (a, b) in SP if bandf(a, 1) and bandf(b, 1) and bandf(a, 1) != bandf(b, 1)]))
put(u'band_unmapped', len([1 for (a, b) in SP if bandf(a, 1) is None or bandf(b, 1) is None]))
put(u'band_moves', sorted(set((bandf(a, 1), bandf(b, 1)) for (a, b) in SP
                              if bandf(a, 1) and bandf(b, 1) and bandf(a, 1) != bandf(b, 1))))

# ---------- 可执行复现: 两代公式跑算例里印出的 CVSS:3.1 Base 分数 ----------
CAND = [(p[u'cve'], p[u'k31'], p[u'v31'], p[u's31'], p[u's40'], p[u'k40']) for p in PT
        if p[u'v31'] and p[u'v31'].startswith(u'CVSS:3.1') and p[u'k31'] in (u'', u'Base')]
put(u'repro_cand', len(CAND))
put(u'repro_cand_no_vec', len([p for p in PT if not (p[u'v31'] and p[u'v31'].startswith(u'CVSS:3.1'))
                               and p[u'k31'] in (u'', u'Base')]))
V31U = sorted(set(x[2] for x in CAND))
put(u'repro_vec_distinct', len(V31U))
PRINTED = {}
for cve, k31, vec, s31, s40, k40 in CAND:
    PRINTED.setdefault(vec, set()).add(s31)
res = [(v, base_score(v, W31, C31), base_score(v, W30, C30),
        base_score(v, W31, C31, roundup_naive)) for v in sorted(PRINTED)]
put(u'repro_pts', len(res))


def hit(x, got):
    return got is not None and any(abs(got - p) < 1e-9 for p in PRINTED[x])


put(u'repro_ok', len([x for x in res if hit(x[0], x[1])]))
put(u'repro_bad', len([x for x in res if x[1] is not None and not hit(x[0], x[1])]))
put(u'repro_bad_ex', [[x[0][:46], x[1], sorted(PRINTED[x[0]])] for x in res
                      if x[1] is not None and not hit(x[0], x[1])])
put(u'repro_none', len([x for x in res if x[1] is None]))
put(u'repro_none_ex', [x[0] for x in res if x[1] is None])
put(u'repro_ok30', len([x for x in res if hit(x[0], x[2])]))
put(u'repro30_eq_31', len([x for x in res if x[1] is not None and x[2] is not None
                           and abs(x[1] - x[2]) < 1e-9]))
put(u'repro30_ne_31', [[x[0][:46], x[2], x[1]] for x in res if x[1] is not None and x[2] is not None
                       and abs(x[1] - x[2]) >= 1e-9])
put(u'repro_naive_eq', len([x for x in res if x[1] is not None and x[3] is not None
                            and abs(x[1] - x[3]) < 1e-9]))
put(u'repro_naive_ne', [[x[0][:46], x[1], x[3], sorted(PRINTED[x[0]])] for x in res
                        if x[1] is not None and x[3] is not None and abs(x[1] - x[3]) >= 1e-9])
put(u'repro_naive_matches_print', len([x for x in res if x[3] is not None and hit(x[0], x[3])]))
put(u'repro_print_distinct', len([v for v in PRINTED if len(PRINTED[v]) > 1]))
put(u'v40_score_printed', len([p for p in PT if p[u's40'] is not None]))
put(u'v40_vec_printed', len([p for p in PT if p[u'v40'] and p[u'v40'].startswith(u'CVSS:4.0')]))
put(u'v40_vec_distinct', len(set(p[u'v40'] for p in PT if p[u'v40'] and p[u'v40'].startswith(u'CVSS:4.0'))))

# ---------- 全向量空间: 两代 Base 逐一对照 + 三种"向上进到 0.1"的分裂 ----------
def ru_ceil(x):
    """最朴素的写法: 直接 ceil(x*10)/10, 不先修浮点噪声."""
    return math.ceil(x * 10.0) / 10.0


def vals31(g):
    vs = set(v for (gg, v, _s) in W31 if gg == g)
    return sorted(vs - {u'X', u'U'})


FULL = [u'CVSS:3.1/AV:%s/AC:%s/PR:%s/UI:%s/S:%s/C:%s/I:%s/A:%s'
        % (av, ac, pr, ui, s, c, i, a)
        for av in vals31(u'AV') for ac in vals31(u'AC') for pr in vals31(u'PR')
        for ui in vals31(u'UI') for s in (u'U', u'C')
        for c in vals31(u'C') for i in vals31(u'I') for a in vals31(u'A')]
put(u'full_vectors', len(FULL))
put(u'full_av', vals31(u'AV'))
FR = [_raw(v, W31, C31) for v in FULL]
put(u'full_zero', len([r for r in FR if r[0] == u'zero']))
put(u'full_capped', len([r for r in FR if r[0] == u'ok' and r[1] > 10.0]))
put(u'full_eq3031', len([v for v in FULL
                         if base_score(v, W30, C30) == base_score(v, W31, C31)]))
put(u'full_ne3031', len([v for v in FULL
                         if base_score(v, W30, C30) != base_score(v, W31, C31)]))
put(u'full_ne3031_ex', [[v[8:], base_score(v, W30, C30), base_score(v, W31, C31)]
                        for v in FULL if base_score(v, W30, C30) != base_score(v, W31, C31)][:8])

# 精确小数(分毫不动的十将有理数)向上进到 0.1: 判据
EX = {}
TOT = {}
for v, (st, raw) in zip(FULL, FR):
    if st != u'ok':
        EX[v] = (st, None, None, None, None)
        continue
    # 文档里每一位系数都是有限小数, 但 iss 在浮点里已经带噪声, 所以用分数重算一遍
    d = parse_vec(v)
    sc = d[u'S']
    scope = u'X' if sc == u'C' else u'U'
    g31 = lambda g: Fr(str(W31[(g, AB2.get(d[g], d[g]), scope if g == u'PR' else u'U')]))
    iss = 1 - (1 - g31(u'C')) * (1 - g31(u'I')) * (1 - g31(u'A'))
    if sc == u'U':
        imp = Fr(str(C31[u'unch'])) * iss
    else:
        imp = (Fr(str(C31[u'c752'])) * (iss - Fr(str(C31[u'p029'])))
               - Fr(str(C31[u'c325'])) * (iss - Fr(str(C31[u'p02']))) ** int(C31[u'exp']))
    ex = (Fr(str(C31[u'expl'])) * g31(u'AV') * g31(u'AC') * g31(u'PR') * g31(u'UI'))
    tot = min(imp + ex if sc == u'U' else Fr(str(C31[u'f108'])) * (imp + ex), Fr(10))
    if imp <= 0:
        EX[v] = (u'zero', 0.0, None, None, None)
        continue
    exact = -((-int(tot.numerator * 10) // int(tot.denominator)))   # ceil 到 0.1 的分子
    TOT[v] = tot
    EX[v] = (u'ok', float(Fr(exact, 10)), base_score(v, W31, C31),
             base_score(v, W31, C31, roundup_naive), base_score(v, W31, C31, ru_ceil))
okv = [v for v in FULL if EX[v][0] == u'ok']
put(u'full_ok', len(okv))
put(u'full_pseudo_eq_exact', len([v for v in okv if abs(EX[v][1] - EX[v][2]) < 1e-12]))
put(u'full_naive_eq_exact', len([v for v in okv if abs(EX[v][1] - EX[v][3]) < 1e-12]))
put(u'full_ceil_eq_exact', len([v for v in okv if abs(EX[v][1] - EX[v][4]) < 1e-12]))
put(u'full_pseudo_ne_exact', [[v[8:], EX[v][1], EX[v][2]] for v in okv
                              if abs(EX[v][1] - EX[v][2]) >= 1e-12][:6])
put(u'full_ceil_ne_exact', [[v[8:], EX[v][1], EX[v][4]] for v in okv
                            if abs(EX[v][1] - EX[v][4]) >= 1e-12][:6])
put(u'full_ceil_ne_exact_n', len([v for v in okv if abs(EX[v][1] - EX[v][4]) >= 1e-12]))
put(u'full_naive_ne_exact_n', len([v for v in okv if abs(EX[v][1] - EX[v][3]) >= 1e-12]))
# 浮点 raw 恰好落在 0.1 边界"高一线"的向量: 朴素 ceil 会跳档, 精确小数不会
BOUND = []
for v, (st, raw) in zip(FULL, FR):
    if st == u'ok' and raw <= 10.0:
        r = (raw * 10.0) % 1.0
        if r < 1e-9 or r > 1.0 - 1e-9:
            BOUND.append([v[8:], raw, EX[v][1], EX[v][4]])
put(u'full_raw_on_tenth', len(BOUND))
put(u'full_raw_on_tenth_jumps', len([b for b in BOUND if abs(b[2] - b[3]) >= 1e-12]))
put(u'full_raw_on_tenth_ex', BOUND[:6])
put(u'full_exact_on_tenth', len([v for v in okv if (TOT[v] * 10).denominator == 1]))
put(u'full_exact_on_half', len([v for v in okv if (TOT[v] * 2).denominator == 1]))
put(u'full_exact_den_max', max((TOT[v].denominator for v in okv)))
put(u'full_w30_full', len([v for v in FULL if base_score(v, W30, C30) is None]))

# ---------- v4.0 的 EQ 约束表 ----------
EQR = []
for t in tables(TXT[2]):
    rows = [[strip(c) for c in raw_cells(tr)] for tr in trs(t)]
    if not rows:
        continue
    head = rows[0]
    if len(head) >= 2 and head[0].lower().startswith(u'levels') and u'constraints' in u' '.join(head).lower():
        for cells in rows[1:]:
            if len(cells) >= 2 and re.match(u'^\\d{1,2}$', cells[0]):
                EQR.append((cells[0], cells[1], len(cells)))
put(u'eq_row_n', len(EQR))
put(u'eq_levels', sorted(set(x[0] for x in EQR), key=lambda s: int(s)))
put(u'eq_row_level_counts', [[lv, len([x for x in EQR if x[0] == lv])]
                             for lv in sorted(set(x[0] for x in EQR), key=lambda s: int(s))])
put(u'eq_row_cells', sorted(set(x[2] for x in EQR)))
put(u'eq_bool_ops', [[sum(len(re.findall(u'\\b%s\\b' % o, x[1])) for x in EQR)
                      for o in (u'and', u'or', u'not')] for _ in [0]][0])
put(u'eq_or_paren', len(re.findall(u'\\((?:AV|PR|UI|AC|AT|VC|VI|VA|SC|SI|SA|E)', u' '.join(x[1] for x in EQR))))

# ---------- 锚候选池 ----------
SPECIAL = (u'CVSS:3.0/', u'CVSS:3.1/', u'CVSS:4.0/', u'Roundup', u'Round up', u'MacroVector',
           u'6.42', u'7.52', u'1.08', u'0.9731', u'is 13', u'0.30000000000000004', u'0.915',
           u'Negligible', u'Provider Urgency', u'EQ1', u'EQ3+EQ6', u'lookup table',
           u'interpolation', u'Base + Threat', u'v4.0 Base', u'worst case')
POOL = {}
for i, t in enumerate(TAGS):
    for l in LST[i]:
        s = strip(l, br=u'|')
        if len(s) >= 20 or any(x in s for x in SPECIAL):
            POOL[(t, s)] = 1
put(u'pool_n', len(POOL))
put(u'pool_by_tag', [len([1 for k in POOL if k[0] == t]) for t in TAGS])

if __name__ == u'__main__':
    io.open(u'corpus/_b58meas.json', u'w', encoding='utf-8').write(
        json.dumps(M, ensure_ascii=False, indent=0, sort_keys=True))
    print(u'键数 %d' % len(M))
    for i in range(4):
        print(u'%s %-9s bytes=%d chars=%d lines=%d nonblank=%d maxlen=%d mean=%d nonascii=%d tbl=%d tr=%d' % (
            TAGS[i], LBL[i], M[u'bytes'][i], M[u'chars'][i], M[u'lines'][i], M[u'nonblank'][i],
            M[u'maxlen'][i], M[u'meanlen'][i], M[u'nonascii'][i], M[u'table_tags'][i],
            M[u'tr_rows'][i]))
    print(u'系数 v3.0 %s' % sorted(C30.items()))
    print(u'系数 v3.1 %s' % sorted(C31.items()))
    print(u'基础分系数 同 %d/%d 异 %s 环境分异 %s' % (
        M[u'coef_base_n_equal'], len(BASEKEYS),
        [k for k in BASEKEYS if abs(C30[k] - C31[k]) > 1e-12], M[u'coef_env_diff']))
    print(u'权重 行 %d⇎%d 组头 %d⇎%d 三元 %d⇎%d 共有 %d 等 %d 不等 %s' % (
        NR30, NR31, NG30, NG31, len(W30), len(W31), M[u'w_common'], M[u'w_equal'],
        M[u'w_unequal']))
    print(u'单调性违例 v3.0式 %d ⇎ v3.1式 %d (比较对 %d) 两式同违 %d 只30 %d 只31 %d 未封顶 %d⇎%d' % (
        len(b30), len(b31), p30, len(b30 & b31), len(b30 - b31), len(b31 - b30),
        len(u30), len(u31)))
    print(u'档位 %s ⇎ %s 词表 %s⇎%s⇎%s 行 %s' % (
        M[u'band_labels'][1], M[u'band_labels'][2], M[u'band_vocab'][0], M[u'band_vocab'][1],
        M[u'band_vocab'][2], M[u'band_rows']))
    print(u'向量 出现 %s 种 %s 3.1 %s 4.0 %s 双冒号 %s' % (
        M[u'vec_occ_raw'], M[u'vec_distinct_raw'], M[u'vec_occ_raw_31'], M[u'vec_occ_raw_40'], M[u'vec_pr_doublecolon']))
    print(u'算例块 %d 段 %s' % (M[u'case_n'], M[u'case_by_section']))
    print(u'对照表 %d 分数对 %d 列口径 %s 31空白 %d 40复合 %d 空白+复合 %d' % (
        M[u'pair_tbl_n'], M[u'sp_n'], M[u'pair_ncols'], M[u'pair_k31_blank'],
        M[u'pair_k40_composite'], M[u'pair_k31blank_k40composite']))
    print(u'差值 全 正%d 负%d 零%d 和%s | 仅Base n%d 和%s 升%d 降%d 平%d' % (
        M[u'delta_pos'], M[u'delta_neg'], M[u'delta_zero'], M[u'delta_sum'],
        M[u'delta_base_n'], M[u'delta_base_sum'], M[u'delta_base_up'], M[u'delta_base_down'],
        M[u'delta_base_same']))
    print(u'跨档 %d 同档 %d 无档 %d 档迁 %s' % (
        M[u'band_diff'], M[u'band_same'], M[u'band_unmapped'], M[u'band_moves']))
    print(u'复算 3.1: 候选 %d 去向量 %d 命中 %d 不符 %s 解析失败 %s' % (
        M[u'repro_cand'], M[u'repro_vec_distinct'], M[u'repro_ok'], M[u'repro_bad'],
        M[u'repro_none']))
    print(u'v3.0 公式对同向量 同分 %d 变分 %s' % (M[u'repro30_eq_31'], M[u'repro30_ne_31']))
    print(u'朴素 Roundup⇎伪码 同 %d 异 %s (异者仍与印出相符 %d)' % (
        M[u'repro_naive_eq'], M[u'repro_naive_ne'], M[u'repro_naive_matches_print']))
    print(u'v4.0: EQ行 %d 档位 %s and/or/not %s MacroVector %s 插值 %s' % (
        M[u'eq_row_n'], M[u'eq_levels'], M[u'eq_bool_ops'], M[u'bl_mv'], M[u'bl_interp']))
    print(u'算术词 Roundup %s RoundUp字样 %s 6.42 %s 8.22 %s 0.9731 %s 伪码 %s' % (
        M[u'ar_ru'], M[u'ar_ru_up'], M[u'ar_k642'], M[u'ar_k822'], M[u'ar_k9731'],
        M[u'ar_pseudocode']))
    print(u'口径表 31 %s 40 %s 同格分数向量 %d 空格表式 %s' % (
        M[u'pair_k31_hist'], M[u'pair_k40_hist'], M[u'pair_score_vec_samecell'], M[u'pair_ncols']))
    print(u'跳过表 %s 尾行换行 %s 最长行共享 %s' % (M[u'pair_skip'], M[u'final_nl'],
                                                   M[u'maxline_shared']))
    print(u'全向量 %d 可算 %d 影响为零 %d 超10 %d | 两代同分 %d 异 %s' % (
        M[u'full_vectors'], M[u'full_ok'], M[u'full_zero'], M[u'full_capped'],
        M[u'full_eq3031'], M[u'full_ne3031']))
    print(u'取整对照(精确小数为判据) 伪码 %d/%d 修round %d 直接ceil %d' % (
        M[u'full_pseudo_eq_exact'], M[u'full_ok'], M[u'full_naive_eq_exact'],
        M[u'full_ceil_eq_exact']))
    print(u'ceil 偏档 %d 例 %s' % (M[u'full_ceil_ne_exact_n'], M[u'full_ceil_ne_exact']))
    print(u'伪码偏档 %s' % M[u'full_pseudo_ne_exact'])
    print(u'浮点raw恰在0.1边界 %d 其中朴素ceil跳档 %d 例 %s' % (
        M[u'full_raw_on_tenth'], M[u'full_raw_on_tenth_jumps'], M[u'full_raw_on_tenth_ex']))
    print(u'精确小数落在0.1整倍 %d 0.5整倍 %d 分母最大 %d | W30 跑不了 %d' % (
        M[u'full_exact_on_tenth'], M[u'full_exact_on_half'], M[u'full_exact_den_max'],
        M[u'full_w30_full']))
    print(u'权重未映射 %d⇎%d 例 %s⇎%s 表头行 %d⇎%d' % (
        len(LO30), len(LO31), LO30[:3], LO31[:3], UA30, UA31))
    print(u'查表词 MacroVector %s lookup %s interp %s 约束 %s EQ头 %s' % (
        M[u'bl_mv'], M[u'bl_lookup'], M[u'bl_interp'], M[u'bl_cons'], M[u'eq_heads']))
