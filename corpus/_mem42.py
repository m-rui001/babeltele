# -*- coding: utf-8 -*-
"""把 B42 的教训写进项目记忆(幂等): 单源条的内部冗余口径 + 装配期的四个坑。"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8')
P = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory/corpus-selection-and-proof-rule.md'
s = io.open(P, encoding='utf-8').read()

SEC = u'''## 19. What B42 taught (single-source entry, intra-document reuse, 2026-10-20)

B42 = one CSB accident-investigation report (88-page PDF → text, 213 726 chars, tag ⟦M⟧). No second
file to diff, so the compression target moved **inside** the document: nine long recommendation
clauses occur 35 times, 26 of those are verbatim copies (DERIV 35 / 26 / 0.74) because the same duty
sentence is re-issued per addressee. Numbers: enc 11 647, digest 6 556 (52 anchor positions, only 23
distinct strings, atomcheck ok=52 bad=0), 33 DERIV keys + 13 absences folded into one `0` key,
byte density 5.411%, uniq codepoints 528, chars/unit 7.55, retention-vs-digest 177.7% (corpus max).

Four build-time traps found the hard way (all now the standard method):

- **Slice anchors from the whitespace-collapsed source instead of typing them.** `S(key)` returns a
  span of `C = re.sub(r'\\s+', ' ', body)` bounded by sentence punctuation, so every anchor is
  verbatim-by-construction and T1 cannot fail. Search case-insensitively — the sentences are
  title-cased at the start while the counted patterns are lowercase.
- **Count on the scope audit uses.** `CNT` reads the header-stripped body: a count taken over the
  whole file (fetch header included) gave `]` 376 vs audit's 375 and `http` 51 vs 50. Header-only
  facts (`pages=88`) are NOT CNT-provable → keep them in prose as provenance, never as a DERIV key.
- **DERIV keys are the value, so equal-valued claims collide.** RAGAGEP 5 vs the ×5 clause, Table 15
  vs "may include" 15, EPA 9 vs OSHA 9 — each collision forced dropping or merging a claim. Plan the
  number set before writing prose.
- **Register per-tag DERIV inside the big `DERIV = {` literal** (entries with 2-space indent, values
  as quoted strings). A standalone `DERIV['B42'] = {...}` placed before `ATOM = {` NameErrors at
  import because `DERIV`/`CNT` are defined later; and its values must be strings, not bare
  expressions, or they evaluate at import.

Also: an entry whose value is *judgment* can legitimately exceed 100% retention-vs-digest — the
digest only indexes what anchors touch. Say so in the gloss (保留率口径 paragraph) and lead with the
byte-level density and the key count instead. And absences are conclusions: hot work / permit /
lockout / tagout / MOC / PTW / 29 CFR are all 0 in an actual refinery explosion report — the 0 is the
finding about which causal mechanism the board did NOT adopt.

'''
if u'## 19. What B42 taught' not in s:
    i = s.index(u'**How to apply:**')
    s = s[:i] + SEC + s[i:]
    io.open(P, 'w', encoding='utf-8').write(s)
    print(u'memory §19 inserted')
else:
    print(u'memory §19 already present')

M = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory/MEMORY.md'
m = io.open(M, encoding='utf-8').read()
new = (u'- [Corpus selection & proof rule](corpus-selection-and-proof-rule.md) — v2: compress reasoning not '
       u'lookups; 42 条 PASS (365 DERIV 条, audit 自报数为准); 锚点从折叠原文切片⇒逐字由构造保证; '
       u'计数一律用 audit 口径(去头部正文); 单源条可保留率>100%(另报字节密度)')
if u'42 条 PASS' not in m:
    m = u'\n'.join([l for l in m.split(u'\n') if not l.startswith(u'- [Corpus selection')]) .strip() + u'\n' + new + u'\n'
    io.open(M, 'w', encoding='utf-8').write(m)
    print(u'MEMORY.md index updated')
else:
    print(u'MEMORY.md already updated')

E = u'C:/Users/hp/.qoder-cn/memory/env-windows-toolchain.md'
e = io.open(E, encoding='utf-8').read()
ADD = (u'\n- Local model proxy for sub-agent work: `E:/tools/OpenCode2API-main` serves an OpenAI-compatible '
       u'API at `http://127.0.0.1:10000`; dispatch with '
       u'`python -X utf8 E:/tools/oc2a_ask.py --model opencode/<model> --session <id> task.txt [system.txt]`. '
       u'Key lives only in `E:/tools/OpenCode2API-main/config.json` (`API_KEY`); `--session` is required for '
       u'parallel calls (no user name ⇒ all requests queue on one backend session); reasoning content is kept '
       u'out of stdout (stderr notes it), timeout default 600 s.\n')
if u'OpenCode2API' not in e:
    io.open(E, 'a', encoding='utf-8').write(ADD)
    print(u'env memory appended')
else:
    print(u'env memory already present')
