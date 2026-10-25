# -*- coding: utf-8 -*-
"""把 B44 的教训写进项目记忆(幂等): 同一篇文章两种序列化的口径 + 装配期的三个新坑。"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8')
P = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory/corpus-selection-and-proof-rule.md'
s = io.open(P, encoding='utf-8').read()

SEC = u'''## 21. What B44 taught (same article, two serializations, 2026-10-20)

B44 = one Europe PMC `fullTextXML` response kept twice: JATS/XML as returned (30 652 chars, tag ⟦X⟧) ⇎ the
same endpoint stripped to rendered text (14 683 body chars, 9 lines, tag ⟦D⟧). Same article, word-for-word
identical, so the axis moved off "different documents" onto **different serializations of one document**.
Numbers: enc 16 523, digest 5 932 (51 anchor positions / 21 distinct strings, X 34 ⇎ D 17; 22 atoms to check,
atomcheck ok=22 bad=0), 21 DERIV keys with 42 CNT terms folded into the single `0` key, byte density 36.222%,
retention-vs-digest 278.5% (corpus max — a container/contrast entry again).

What the pair actually proves (reuse this framing, not the counts):

- **格式转换不产生新事实, 但销毁信息的住址.** Eight 70–300-char sentences hit equally in both layers
  (cross-layer difference folded into `0`) ⇒ content is loss-free by construction; yet `<` 1085 ⇎ `</` 536 ⇎
  unbalanced 549 ⇎ lowercase tag starts 541, and keyword/article-id/contrib/affiliation/funding/xref/
  custom-meta counts all reduce to 0 in the render layer. Structure is what the length difference is made of.
- **剥标记会造出另一层里根本不存在的词元.** Boundary glue: "J Intensive Care 2646" (journal title ⇎ volume)
  exists only in the stripped text (layer difference 1, machine-checked). So the same query returns different
  result sets in the two formats — the first *checkable* statement of "format matters" in this corpus.
- **存活由住址决定, 不由重要程度决定.** DOI prefix (element content) is 5 ⇎ 5; ISSN / `pub-id-type`
  (attribute values) are 0 in the render layer. Same for `<article-type>` and `<license>`: attributes die.
- **同一个 0 有两种成因.** fig / table / disp-formula are 0 in BOTH layers — here that is the genre
  (`article-type="letter"`), whereas in B42 a missing figure was a conversion loss. So a 0 must always be read
  together with the genre attribute, never as a blanket "crawl loss".
- 双向缺席 ⇒ 两份都得存: 4 render-only traces (Europe PMC / ebi.ac.uk / fullTextXML / glued token) ⇎
  14 XML-only tag families; container and content do not contain each other.

Three build-time traps hit this time:

- **Pre-assert DERIV value uniqueness.** Key name == value, so `<license>` 2 and `<aff>` 2 collide: drop the
  weaker claim and say "同值故不另立机检键" in the gloss instead of inventing a fake key or rewriting a number.
  `assert len(set(VALS)) == len(VALS)` before writing the block.
- **The anchor locator must be regex-aware** (escape only when the key has no backslash). Escaping every
  candidate made tag lookups miss wholesale (`ALL MISS: <kwd-group>`) because the whitespace-collapse breaks tag
  spellings; look tags up by prefix with escaped metachars (`u'<kwd\\-group'`, `u'<aff\\s'`, `u'<p\\s'`).
- **Bundle counts inside the encoding use Chinese numerals** (`CN` dict) — "十四类缺席", "八条长句" — so no
  unregistered 1–2-digit Arabic number lands in the body. And when 待核 still shows digits that come from inside
  long identifiers (PMED `42816885`, GRID `grid.443382.a`), disclose them in 解读注 + README as anchor-borne
  noise; never trim an anchor to make the counter read prettier (待核 does not gate FAIL).

Bookkeeping scripts (`_readmeNN.py`): recompute everything from audit + metrics + raw inside the script
(no hand-typed totals), and note that spaced numbers come out of `fmt()` as **strings** — pair them with `%s`,
not `%d`. Escape markdown `**` in any regex that looks up the 第二代 line.

'''
if u'## 21. What B44 taught' not in s:
    i = s.index(u'**How to apply:**')
    s = s[:i] + SEC + s[i:]
    io.open(P, 'w', encoding='utf-8').write(s)
    print(u'memory §21 inserted')
else:
    print(u'memory §21 already present')

M = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory/MEMORY.md'
m = io.open(M, encoding='utf-8').read()
new = (u'- [Corpus selection & proof rule](corpus-selection-and-proof-rule.md) — v2: compress reasoning not '
       u'lookups; 44 条 PASS (404 DERIV 条); 锚点从折叠原文切片⇒逐字由构造保证; 计数一律用 audit 口径(含 url 行); '
       u'DERIV 键名即数值⇒写前断言数值互不相同; 同文两序列化条: 剥标记会造出新词元, 0 要连体裁读')
if u'44 条 PASS' not in m:
    m = u'\n'.join([l for l in m.split(u'\n') if not l.startswith(u'- [Corpus selection')]).strip() + u'\n' + new + u'\n'
    io.open(M, 'w', encoding='utf-8').write(m)
    print(u'MEMORY.md index updated')
else:
    print(u'MEMORY.md already updated')
