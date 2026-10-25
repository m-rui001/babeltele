# -*- coding: utf-8 -*-
"""把 §18(B41 的教训)插入项目记忆文件; 幂等: 先删旧 §18 再插在 **How to apply:** 之前。"""
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8')
P = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory/corpus-selection-and-proof-rule.md'
NEW = u'''## 18. What B41 taught (one docket's proposed ⇎ final pair as a 2-source diff, 2026-10-20)

- Route that works: `federalregister.gov/api/v1/documents.json` to find the pair, then
  `/documents/full_text/text/YYYY/MM/DD/<docno>.txt` — the `.txt` is HTML, text lives in `<body><pre>`;
  fetch with `curl -s --noproxy '*'`. API gotchas: the agency object has `raw_name`/`name` (no `raw_long_name`),
  and passing `fields[]` silently drops `citation` ⇒ request the whole document object.
- New axis = time, not opponents. The machine-checkable core of a rulemaking pair is
  **announced changes ⇎ measured diff**: B41's final order self-reports 2 revisions while verbatim alignment shows
  3 word-level edits + 1 deleted item + 1 whole-column numeral shift + 1 unannounced bracket rewrite.
  Corollary worth reusing everywhere: after any "item X was removed", re-read what now prints as X —
  `Sec. 864.1890(b)(1)(viii)` means reagent stability in the proposal and specimen stability in the final order.
- Anchors may only quote text that EXISTS. Absence claims get no anchor; their exact word forms go into the
  single `'0'` DERIV key (34 folded assertions here). The builder must reject, not warn — it did, 13 times first run.
- Cross-file identical anchor strings mean different things by genre: B40 (same template, 3 orders) ⇒ boilerplate;
  B41 (two stages of one docket) ⇒ "this provision was never touched". Say which one in the gloss.
- The digest reports cross-label hits by **anchor position** (13), not distinct strings (8). Reproduce the digest's
  own `pairs()` normalization in `_fillNN.py` or the two numbers silently disagree; quote both.
- Digest window radii are a 口径 knob, not a detail: 80/160 gave digest 8 147 < encoding 10 379 ⇒ retention >100%.
  240/320 (≈ whole sentences) gave 12 742 ⇒ 81.5%. Pick radii first, then write the gloss numbers.
- Scrubbing Latin→CJK outside anchors leaves stray spaces between CJK chars and can double-substitute
  (`Dated 行` → `日期行行`). Fix with one regex pass `(?<=[CJK-punct]) +(?=[CJK-punct])` inside `scrub()`,
  and never let the substitution table collide with prose you already translated.
- FR full-text artifacts to expect (all measured, all worth asserting): `[[Page N]]` count (10 ⇎ 7) ≠ page span
  (10 ⇎ 8) because page 1 carries no marker; `\\N\\` footnote markers land inside words; `` … '' quote pairs;
  two-column tables flattened with `[verbar]` — its presence/absence (2 ⇎ 0) proves which document carried the table;
  emails survive as the undecoded Cloudflare entity `[email&#160;protected]` with `@` at 0 in both sources;
  hard wrap (median line 67 cols, 735–864 lines ending in a space, 9–43 lines ending in a hyphen) ⇒
  every multi-word `CNT` pattern needs `\\s+`.
- Metrics hygiene: if you cannot recompute a README number's definition (e.g. "29 个 tag"), replace it with what the
  tool actually prints (`audit.py`: 已机检的推导 333 条) instead of carrying a guessed increment forward.
- The measure-then-assert loop also kills overstatement: B41's first gloss claimed the 79 non-shared anchors "are the
  diff" — most are simply document-unique sections. Alignment finds the diff; the response paragraphs only announce it.'''

t = io.open(P, encoding='utf-8').read()
t = re.sub(u'\\n?## 18\\. What B41 taught.*?(?=\\n\\*\\*How to apply:\\*\\*)', u'', t, flags=re.S)
assert u'## 17. What B40 taught' in t
i = t.index(u'**How to apply:**')
io.open(P, 'w', encoding='utf-8').write(t[:i] + NEW + u'\n\n' + t[i:])
print(u'§18 inserted; file chars %d' % (len(t) + len(NEW)))
