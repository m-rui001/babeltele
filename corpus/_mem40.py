# -*- coding: utf-8 -*-
"""把 §17 插入 memory(幂等: 已存在则整体替换该节)。"""
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
P = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory/corpus-selection-and-proof-rule.md'
t = io.open(P, encoding='utf-8').read()
SEC = u'## 17. What B40 taught (three FDA de novo orders as a 3-source diff, 2026-10-20)'
NEW = SEC + u"""

**The thesis had to be re-expressed until it was provable.** B40 = three Federal Register de novo classification orders
(cardio-ML notification, radiology-ML with PCCP, opioid-impairment monitor): 52 011 raw chars ⇎ 15 293 digest ⇎ 10 077 encoding,
65.9% vs digest / 18.323% vs bytes, 91 anchors (C 49 shared-hit ⇎ R ⇎ M tags 61/39/43), 0 Han inside anchors, 149 outside-anchor
letters of which 143 are provenance tags. Lessons that generalize:

(a) **DERIV keys are the numeric value strings themselves**, so two different claims that share a number cannot both be evidenced by
one key. Resolution that worked: fold every "word X never appears" claim into ONE `'0'` key (B40's zero key carries 35 `CNT` absence
assertions), and express any duplicated value as a mean/sum composite (`mean(p)=round((CNT(p,0)+CNT(p,1)+CNT(p,2))/3)`,
`tot(p)=CNT(p,0)+CNT(p,1)+CNT(p,2)`). Never invent a padding derivation to reuse a number.

(b) **`_reason()` returns RAW, newline-preserving source.** FR prose is hard-wrapped, so a multi-word `CNT` pattern written with
literal spaces returns 0 — and an "absent" claim then passes *trivially*. That is the dangerous direction (a green gate proving
nothing). Always join words with `\\s+` (B40's `PH()` helper) and positively verify a phrase you expect to exist returns ≥1.

(c) **`prose_norm`'s class must be copied exactly**: audit uses `[^0-9a-z\\u4e00-\\u9fff\\-\\. ]`. Writing it as `[^0-9a-z\\u4e00-\\u9fff -.]`
turns ` -.` into the range U+0020–U+002E, which silently *keeps* parentheses instead of spacing them ⇒ a builder-side check passes text
the auditor would reject. Unescaped `-.` inside a class is a bug, not a shorthand.

(d) **Verbatim anchors make "boilerplate vs medium-driven difference" machine-checkable.** 25 anchor strings hit identically in ≥2 of the
3 files ⇒ the shared phrasing is provably copied, not mislabeled; the differing rows (human factors ⇎ usability ⇎ neither, risk-table rows
selected by medium) are then provably *not* copy. A cross-file identical-string count is a cheap and strong proof device for any
multi-source template genre (regulatory orders, judgment templates, journal letter formats).

(e) **Measure before claiming; most of my draft claims died on counts.** Killed examples: `510(k)` counted 0 under the wrong normalizer;
`usability` absent from the radiology order; `shall` absent everywhere; `you must` absent from the opioid order; `independent` ⇎ `separate`
are NOT mutually absent (one file has both). Also: the quote-vs-no-quote difference in one ACTION sentence is unprovable because
normalization erases both quote styles — reframe such a claim as "normalization erases the distinction" instead of dropping the line.

(f) **Flattened two-column tables dictate anchor shape.** govinfo's HTML tables interleave cell text line-by-line, so a logical row
`A | B` lands as `A-word B-word A-word B-word`. Anchors must follow the *interleaved token order* (or be split into two anchors), never
the row as read by a human. Related drafting rule learned here: a footnote-style gloss attached to a quote is fine, but it must not
assert a verbatim property the auditor cannot check.

(g) **Governance text has a licensable absence structure worth auditing directly**: `must` 31 hits against `you` 2 and `we` 13 ⇒ obligations
can be written with no addressee. Counting modals against pronouns is a two-line check that yields a real tacit-knowledge claim about
regulatory drafting.

(h) **Never hand-escape CJK.** A builder written with `\\uXXXX` sequences shipped corrupted glyphs (编纁 / 晃患 / 偏倝 / 两神) and an invented
arrow (⇤). Write literal UTF-8 in source files and in gloss text; `python -X utf8` everywhere.

(i) **Verify anchors AFTER the whole encoding is assembled**, including anchors embedded inside gloss lines — B40's miss-collector loop
(`want:`/`have:` context windows for every miss) replaced the abort-on-first-miss pattern and found 4 real mismatches in one pass.

(j) **Tool I/O shapes**: `atomcheck.py` wants one anchor per line (feeding it entry lines gave ok=59 bad=30; a generated
`corpus/_atomsNN.txt` gave ok=91 bad=0). `audit.py`'s encoder count is `len(enc.replace('\\n',''))` while its digest count is the text
between `[[原始语料|ORIGINAL]]` and `## ⟪BabelTele⟫` — quote both 口径, never mix.

**Canonical build order per entry (keep it, it is load-bearing):** `_mkrawNN.py` (fetch + self-recorded `chars`/`text_sha256` header)
→ `_mkBNN.py` (anchors, per-tag verbatim assertion after assembly) → `_mkdigest3.py <tag> <entry> <lbl> <raw> <wl> <wr> ...`
(window per source, `### ⟦X⟧ ⟸ path` sections, exits 1 on any unmatched anchor) → `_wireNN.py` (delete-and-reinsert
`SRC`/`ATOM`/`DERIV` in audit.py + atomcheck SRC) → `python -X utf8 corpus/audit.py` → `_fillNN.py` gloss (every number measured then
asserted) → `_readmeNN.py` (each replacement asserted to match exactly once; library totals recomputed from audit's own table) → memory.

**Warm pool after B40.** govinfo FR HTML is proven and cheap — good next pairs: an FR final rule ⇎ its proposing NPRM (same doc number
family, `FR-YYYY-MM-DD/html/<docno>.htm`), or an FR rule ⇎ the public comment it answers. Non-FR candidates on routes already verified
from this box: UK judgment pair (first instance ⇎ appeal, `curl -L` PDF), NBER working paper ⇎ its published journal version,
a frontier-model technical report ⇎ its erratum/version update (for CoT-shaped reasoning text), and a retraction notice ⇎ the retracted
paper (a dispute pair where the *silence* side is on the record this time). `raw/prose/law_aviator_spribe.txt` stays rejected (nav chrome).
"""

t = re.sub(u'\\n?## 17\\. What B40 taught.*?(?=\\n\\*\\*How to apply:\\*\\*)', u'', t, flags=re.S)
i = t.index(u'**How to apply:**')
io.open(P, 'w', encoding='utf-8').write(t[:i] + NEW + u'\n\n' + t[i:])
print(u'§17 written; file chars %d' % len(io.open(P, encoding='utf-8').read()))
