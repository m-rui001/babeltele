# -*- coding: utf-8 -*-
"""项目记忆记账: 追加 B47 一节(§24), 并把 MEMORY.md 索引行改成 47 条 / audit 自报推导数。
全部数字取自 _f47stats.txt、raw 现算与 audit 现跑结果, 不手填。"""
import io, re, sys, os, ast, subprocess

sys.stdout.reconfigure(encoding='utf-8')
MEMD = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory'
FILE = MEMD + u'/corpus-selection-and-proof-rule.md'
IDX = MEMD + u'/MEMORY.md'


def loadstat(fn):
    d = {}
    for l in io.open(fn, encoding='utf-8').read().split(u'\n'):
        if u'\t' in l:
            k, v = l.split(u'\t')
            d[k] = v
    return d


ST = loadstat(u'corpus/_f47stats.txt')
NUM = lambda k: ast.literal_eval(ST[k]) if ST[k].strip().startswith(u'[') else int(ST[k])
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-500:]
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
enc_all, dig_all, uniq_all = int(allc[1].replace(u' ', u'')), int(allc[0].replace(u' ', u'')), int(allc[4])
NENT = len(row) - 1
b47 = [x.strip() for x in row[u'B47'].split(u'|')]
assert NENT == 47 and int(b47[1]) == NUM(u'enc') and int(b47[10]) == 0, (NENT, b47)
assert (NUM(u'deriv_keys'), NUM(u'n_terms0'), NUM(u'n_term0'), NUM(u'n_diff')) == (37, 50, 61, 0)
assert (NUM(u'anchors'), NUM(u'uniq_anchor'), NUM(u'gloss_lines')) == (62, 18, 12)

RU = u'corpus/raw/UnicodeData.txt'
RS = u'corpus/raw/scripts.txt'
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
TXT = [io.open(x, encoding='utf-8', errors='replace').read() for x in (RU, RS)]
SRC = [u'\n'.join(l for l in x.split(u'\n') if not HEADRX.match(l.strip())) for x in TXT]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
RCOT = lambda i: len(SRC[i].strip())
DROPCH = [sum(len(l) + 1 for l in TXT[i].split(u'\n') if HEADRX.match(l.strip())) for i in range(2)]
TAILWS = [len(SRC[i]) - len(SRC[i].strip()) for i in range(2)]
FULL = [len(x) for x in TXT]
BYTES = [os.path.getsize(x) for x in (RU, RS)]
assert (DROPCH[1], TAILWS[1], DROPCH[1] + TAILWS[1]) == (13946, 9, FULL[1] - RCOT(1)), (DROPCH, TAILWS)
assert (DROPCH[0], TAILWS[0]) == (0, 1) and FULL[0] == BYTES[0] == RCOT(0) + 1
DROPL = [len(TXT[i].split(u'\n')) - len(SRC[i].split(u'\n')) for i in range(2)]
assert (DROPL[0], DROPL[1]) == (0, 368)
assert (CNT(u';Cn;', 0), CNT(u'U\\+', 0), CNT(u'U\\+', 1)) == (0, 0, 0)
assert (CNT(u'_', 0), CNT(u'_', 1), CNT(u'<', 0), CNT(u'<', 1)) == (0, 307, 3938, 4)
assert (CNT(u'Han', 0), CNT(re.escape(u'; Han #'), 0)) == (1391, 0)
assert (CNT(u'HYPHEN', 0), CNT(u';HYPHEN;', 0), CNT(u'HYPHEN', 1)) == (21, 1, 17)
K4E00 = re.escape(u'CJK UNIFIED IDEOGRAPH-4E00')
assert (CNT(K4E00, 0), CNT(K4E00, 1)) == (1, 1)
assert (CNT(re.escape(u'# L& '), 1), CNT(u'L&', 0), CNT(re.escape(u'# Co '), 1)) == (157, 0, 0)
# 体量排位(判词里不许出现未经测量的“全库最大”)
SIZES = sorted(((os.path.getsize(os.path.join(r, f)), os.path.relpath(os.path.join(r, f), u'corpus/raw')
                 .replace(os.sep, u'/'))
                for r, _d, fs in os.walk(u'corpus/raw') for f in fs), reverse=True)
RANK_U = [i for i, (_, nm) in enumerate(SIZES) if nm == u'UnicodeData.txt'][0] + 1
RANK_S = [i for i, (_, nm) in enumerate(SIZES) if nm == u'scripts.txt'][0] + 1
assert SIZES[0][0] > BYTES[0] and RANK_U > 1 and RANK_S > 1, (SIZES[:3], RANK_U, RANK_S)
assert (NUM(u'assign'), NUM(u'norow'), NUM(u'noucd')) == (159866, 119303, 12)
assert (NUM(u'markcov'), NUM(u'uncovered'), NUM(u'scripts_n')) == (258847, 954246, 174)
assert (NUM(u'single_named_ok'), NUM(u'range_both_ok'), NUM(u'range_bad')) == (827, 1446, 14)
assert (NUM(u'rcot_u'), NUM(u'rcot_s'), NUM(u'dropped_s')) == (2198208, 178503, 368)

SEC = u'''
## 24. What B47 taught (a definition table ⇎ the classification derived from it: same key spelling, yet 100k+ codepoints have no row, 2026-10-20)

B47 = `corpus/babeltele/B47_definition_table_vs_derived_table.md`, 2 raw sources
(`UnicodeData.txt` — per-codepoint definition table, %s data rows × 14 semicolons, no header at all — ⇎
`scripts.txt` — Scripts-17.0.0 derived classification, %s data rows = %d ranges ⇎ %d singles, %d script values).
%d anchor slots / %d distinct strings, %d judgement lines, %d DERIV keys whose `0` holds %d additive terms
(%d absence classes + %d equality/"exactly-N" claims, %d CNT primitives, %d subtractive keys), retention
%s (vs-raw %s), 0 items in 待核, cross-source literal anchors = %d. Library now **%d entries /
%d machine-checked derivations** (enc %s ⇎ digest %s, %d unique codepoints).

Six durable methodology facts:

- **A join key can match on both sides and still not connect the tables.** No `U+` prefix anywhere (%d/%d), so
  the hex codepoint is the same literal in both files — yet of %s classified points %s have no definition row,
  because the definition table defines ranges by absence: `%s`-class rows 0, ranges carried by %d marker rows
  forming %d First/Last pairs speaking for %s positions. The converse差集 is sharper still: %d codepoints have a
  row but claim no script, and they are exactly the endpoints of %d of those pairs (surrogate + private-use).
  %s positions are covered only by the single `# @missing: 0000..10FFFF; Unknown` fallback line — which the
  auditor's own scope deletes. **Two identical `0`s, different causes, must be reported separately.**
- **Substring search builds a machine of true numbers that are all wrong.** `Han` (case-folded) hits %d times in
  the definition table — inside character names (HANGUL, YI) — while the field pattern `; Han #` hits %d.
  Same event at the other size: `HYPHEN` %d ⇎ as a field exactly %d ⇎ %d in the derived table's name column.
  And "exactly one hit" is its own trap: the derived table's generated string
  `CJK UNIFIED IDEOGRAPH-4E00` hits the definition table %d time, but it lives in the *name of another character*
  (`1F229 SQUARED CJK UNIFIED IDEOGRAPH-4E00`, whose compatibility-decomposition field points back). For
  cross-table matching: ask not "does it occur" but "in which column".
- **Report three rungs of checkability, never as one list.** Rung 1 = CNT-countable tokens (folded into DERIV,
  incl. the bracket self-report %d = range rows and `..` %d = twice that). Rung 2 = conclusions that only
  expansion arithmetic yields: entry-scoped helpers are injected into `audit.py` (`_b47_scan()` +
  `B47_ASSIGN/B47_NOROW/B47_NOUCD/B47_MARKCOV/B47_SELFN/B47_SCRIPTS`, whitelist tail extended idempotently) and
  recomputed from scratch in `_fill47.py`. Rung 3 = tool-side only (bytes %d ⇎ %d, whole-file chars %d ⇎ %d,
  dropped lines %d ⇎ %d, two sha256s, the row-by-row name check %d/%d singles ⇎ %d/%d ranges with all %d
  exceptions attributable to the control/Hangul/ideograph naming devices) — named in the `src:` line and the
  gloss, never smuggled into ⟪BabelTele⟫.
- **A "difference equals the dropped lines" claim needs the whitespace term.** Scope removed %d comment lines
  worth %d chars (each with its newline) while the file/RCOT gap is %d — the missing %d is trailing whitespace
  eaten by `.strip()`. Assert `DROPCH + TAILWS == FULL - RCOT` before writing the sentence.
- **Builder discipline that cost a rebuild each:** (a) DERIV key names must be formatted `%%d` when integral —
  `%%g` turned 2198208 into `2.19821e+06`; (b) every registered anchor must actually appear in the body
  (18 registered ⇎ 17 used until the A–Z row was cited); (c) never assert a corpus-wide ranking without
  measuring it — "the two largest sources" was false, `UnicodeData.txt` ranks %d by bytes behind PDFs; (d) a
  regex spliced into `audit.py` needs its backslashes doubled once more at emission time, else Python warns
  `invalid escape sequence` and evaluates something else than the builder tested.
- **Independent replication by a free model confirmed the parsing trap.** The sanctioned `E:/tools` sub-agent
  route (`python -X utf8 E:/tools/oc2a_ask.py --model opencode/<model> --session <id> task.txt`, proxy at
  127.0.0.1:10000) worked with
  `opencode/glm-5.3-flash-free`; `codebuddy` returned `429 Credits exhausted` and one model returned HTTP 500
  with an empty body. The model wrote its own scripts.txt checker whose row regex omitted the optional
  `..HEX` group, so it saw only %d of %d rows — exactly the error class B47's judgement line warns about. After
  a one-line patch all %d quantities matched the auditor's values. Cheapest fix in the corpus: a row pattern
  must be tested against **both** row shapes before any count is trusted.

**How to apply:** for any "table ⇎ table derived from it" pair, (1) count the delimiter density per row first
(14 ⇎ 1 here) — it classifies the table before you read any content; (2) expand ranges into point sets and take
the差集 in **both** directions, reporting counted tokens ⇎ expansion-only quantities ⇎ tool-side facts as three
separate lists; (3) use field-shaped patterns, never substrings, and interrogate every single hit for its
column; (4) remember that a derived table *generates* strings the source format cannot write (range name
ellipses, the synthetic class `L&`), so pre-exclude them from reverse checks; (5) `CNT` is case-insensitive in
`audit.py`, `norm()` strips spaces and commas (so "119 303" matches key `119303`), 1–2 digit anchors are only
soft-checked — prefer Chinese numerals or DERIV keys for small counts. Housekeeping still open: the duplicate
`raw/probe/bio_recent.json` (byte-identical to the api copy) awaits the user's delete confirmation. Remaining
candidates: `cot/prompts/*` (instruction ⇎ produced reasoning), `tz/zonenow.tab` + `iso3166.tab`, the `probe/`
HTML⇎XML pairs (`_f_2026-*.htm`, `fr_2026-21376.xml`), `langsubtag.txt`, the fips202 pdf ⇎ txt ⇎ html trio, and
`codata_table.html` ⇎ `codata_all.html`.
''' % (format(NUM(u'rows_u'), u',').replace(u',', u' '), format(NUM(u'rows_s'), u',').replace(u',', u' '),
       NUM(u'rng'), NUM(u'sgl'), NUM(u'scripts_n'), NUM(u'anchors'), NUM(u'uniq_anchor'), NUM(u'gloss_lines'),
       NUM(u'deriv_keys'), NUM(u'n_terms0'), NUM(u'n_absent'), NUM(u'n_equ'), NUM(u'n_term0'), NUM(u'n_diff'),
       b47[2], b47[3], NUM(u'cross_atoms'), NENT, proofs,
       format(enc_all, u',').replace(u',', u' '), format(dig_all, u',').replace(u',', u' '), uniq_all,
       CNT(u'U\\+', 0), CNT(u'U\\+', 1), format(NUM(u'assign'), u',').replace(u',', u' '),
       format(NUM(u'norow'), u',').replace(u',', u' '), u'Cn', NUM(u'mark'), NUM(u'pairs'),
       format(NUM(u'markcov'), u',').replace(u',', u' '), NUM(u'noucd'), 6,
       format(NUM(u'uncovered'), u',').replace(u',', u' '),
       NUM(u'han_sub'), CNT(re.escape(u'; Han #'), 0), NUM(u'hyp_u'), NUM(u'hypf_u'), NUM(u'hyp_s'),
       NUM(u'endpoint_u'), NUM(u'brk'), NUM(u'dotdot'),
       NUM(u'bytes_u'), NUM(u'bytes_s'), NUM(u'full_u'), NUM(u'full_s'), DROPL[0], DROPL[1],
       NUM(u'single_named_ok'), NUM(u'sgl'), NUM(u'range_both_ok'), NUM(u'rng'), NUM(u'range_bad'),
       NUM(u'dropped_s'), DROPCH[1], FULL[1] - RCOT(1), TAILWS[1], RANK_U,
       NUM(u'sgl'), NUM(u'rows_s'), 21)

t = io.open(FILE, encoding='utf-8').read()
assert u'## 24.' not in t, u'B47 一节已存在'
io.open(FILE, 'w', encoding='utf-8').write(t.rstrip() + u'\n' + SEC)

idx = io.open(IDX, encoding='utf-8').read()
new_line = (u'- [Corpus selection & proof rule](corpus-selection-and-proof-rule.md) — v2: compress reasoning '
            u'not lookups; %d 条 PASS (%d DERIV 条); 键同拼法⇎对方无行⇒双向差集; 子串造假阳性机器⇒用字段式模式; '
            u'计数一律用 audit 口径; DERIV 键名即数值(整数用 %%d)⇒等式折进 0 键; 三级可核性(记号 ⇎ 展开 ⇎ 工具侧); '
            u'0 有两种成因(注释被剔 ⇎ 真没有), 差值要加尾部空白项; 排序/最大类断言必须先测量' % (NENT, proofs))
idx2 = re.sub(u'^- \\[Corpus selection & proof rule\\].*$', new_line, idx, count=1, flags=re.M)
assert idx2 != idx, u'索引行未替换'
io.open(IDX, 'w', encoding='utf-8').write(idx2)
print(u'memory 追加 §24 完成: %d 条 / %d 推导; 索引行长度 %d｜raw 排位 U=%d S=%d 最大 %d 字节｜差 %d/%d/%d'
      % (NENT, proofs, len(new_line), RANK_U, RANK_S, SIZES[0][0], FULL[1] - RCOT(1), DROPCH[1], TAILWS[1]))
