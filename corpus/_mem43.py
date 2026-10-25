# -*- coding: utf-8 -*-
"""把 B43 的教训写进项目记忆(幂等): 容器 ⇎ 内容条 + 计数口径与 1–2 位数待核两条硬规则。"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8')
P = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory/corpus-selection-and-proof-rule.md'
s = io.open(P, encoding='utf-8').read()

SEC = u'''## 20. What B43 taught (document ⇎ its publication page, counting scope, 2026-10-20)

B43 = the same URL fetched twice: the judiciary.uk case page (3 245 body chars, tag ⟦C⟧) and the full
text of [2026] EWCA Civ 1224 *Aviator LLC & Ors v Spribe OÜ* (42 648 chars / 810 lines, tag ⟦J⟧).
Neither contains the other, so the pair is a genuine set-difference entry whose axis is
**container ⇎ content** rather than two versions of one document. Numbers: enc 12 940, digest 5 057
(31 anchor positions, 27 distinct strings, 13 digest blocks, atomcheck ok=31 bad=0), 20 DERIV keys,
18 absences folded into one `0` key (judgment lacks 6 web fields, page lacks 12 legal terms),
byte density 27.822%, retention-vs-digest 255.9% (a container entry indexes almost nothing),
uniq codepoints 508, chars/unit 6.54. Corpus after B43: 43 entries / 385 machine-checked derivations.

Three rules that only a failed gate could teach:

- **The `url:` line is inside audit's counting scope.** `_reason()` strips only
  `^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)`, so a shared URL adds one hit of
  `-v-`, `Spribe`, `Aviator` to *both* files and every single-sided count was off by one (待核 4).
  Fix: express such claims as **cross-file differences** (`CNT('-v-',0)-CNT('-v-',1)` = 3,
  `CNT('Spribe',1)-CNT('OÜ',1)` = 59) — they cancel the contamination and are stronger claims anyway.
- **Anchors and counts need two different slices.** Slice anchors from url-stripped, whitespace-collapsed
  body text (otherwise an anchor starts inside the fetcher's URL string, e.g.
  `-and-others-v-spribe-ou/`), but keep counts on audit's scope. Mixing these produced ok=28 bad=3.
- **Any 1–2 digit Arabic number in the encoding must be a registered DERIV key or a literal found in
  the source**, else it lands in 待核. Write "共十八项" (guarded by `assert NABS == 18`) not "共 18 项";
  a DERIV value string in audit.py is a *quoted* expression — a fill script must `literal_eval` it once
  to unescape, then `eval` it (double-escaping `r'569\\.88'` silently matched a literal backslash and
  faked a zero-claim).

Genre finding worth reusing: a publication page carries facts the judgment does not (file name, size,
download entry) and the **date encoded in the file name is the hearing date**, while the judgment date
appears only inside the text. Repeated running headers ("Approved by the court for handing down", 15×)
give the text's own page boundaries — independent of whatever the fetch header self-reports. Same word,
different sense in the two files (navigation `Court` 28 ⇎ substantive 57; footer `copyright` ⇎ cause of
action 26) is a compression hazard: keyword counts across a container/content pair are not comparable.

'''
if u'## 20. What B43 taught' not in s:
    i = s.index(u'**How to apply:**')
    s = s[:i] + SEC + s[i:]
    io.open(P, 'w', encoding='utf-8').write(s)
    print(u'memory §20 inserted')
else:
    print(u'memory §20 already present')

M = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory/MEMORY.md'
m = io.open(M, encoding='utf-8').read()
new = (u'- [Corpus selection & proof rule](corpus-selection-and-proof-rule.md) — v2: compress reasoning not '
       u'lookups; 43 条 PASS (385 DERIV 条); 锚点从“折叠+剔 url 行”切片而计数走 audit 口径(含 url 行)⇒单边计数用跨文件差值键; '
       u'编码里 1–2 位阿拉伯数必须有 DERIV 键或在源中逐字命中, 否则用中文数词')
if u'43 条 PASS' not in m:
    m = u'\n'.join([l for l in m.split(u'\n') if not l.startswith(u'- [Corpus selection')]).strip() + u'\n' + new + u'\n'
    io.open(M, 'w', encoding='utf-8').write(m)
    print(u'MEMORY.md index updated')
else:
    print(u'MEMORY.md already updated')
