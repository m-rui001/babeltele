# -*- coding: utf-8 -*-
"""项目记忆记账: 追加 B45 一节, 并把 MEMORY.md 索引行改成 45 条 / audit 自报推导数。
全部数字取自 _f45stats.txt 与 audit 现跑结果, 不手填。"""
import io, re, sys, ast, subprocess

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


ST = loadstat(u'corpus/_f45stats.txt')
NUM = lambda k: ast.literal_eval(ST[k]) if ST[k].strip().startswith(u'[') else int(ST[k])
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-400:]
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
enc_all, dig_all, uniq_all = int(allc[1].replace(u' ', u'')), int(allc[0].replace(u' ', u'')), int(allc[4])
NENT = len(row) - 1
b45 = [x.strip() for x in row[u'B45'].split(u'|')]
assert NENT == 45 and int(b45[1]) == int(ST[u'enc']) and int(b45[10]) == 0, (NENT, b45)
assert NUM(u'deriv_keys') == 25 and NUM(u'n_term0') == 73 and NUM(u'a_only') == 111 and NUM(u'n_only') == 106

RA = u'corpus/raw/tz/zone1970.tab'
RN = u'corpus/raw/tz/zone.tab'
RH = u'corpus/raw/zone1970.tab'
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
SRCA = u'\n'.join(l for l in io.open(RA, encoding='utf-8', errors='replace').read().split(u'\n')
                  if not HEADRX.match(l.strip()))
SRCH = u'\n'.join(l for l in io.open(RH, encoding='utf-8', errors='replace').read().split(u'\n')
                  if not HEADRX.match(l.strip()))
SRCN = u'\n'.join(l for l in io.open(RN, encoding='utf-8', errors='replace').read().split(u'\n')
                  if not HEADRX.match(l.strip()))
FULL_A = len(io.open(RA, encoding='utf-8', errors='replace').read())
RCOT_A = len(SRCA.strip())
CNT = lambda pat, s: len(re.findall(pat, s, re.I))
ROWS_A = CNT(u'(?m)^[A-Z]{2}[,\\t]', SRCA)
TABS_A, TABS_N, TABS_H = CNT(u'\\t', SRCA), CNT(u'\\t', SRCN), CNT(u'\\t', SRCH)
LT_H = CNT(u'<', SRCH)
assert (RCOT_A, FULL_A, ROWS_A, TABS_A, TABS_N, TABS_H, LT_H) == (14482, 17536, 312, 825, 1038, 26, 2087)

SEC = u'''
## 22. What B45 taught (one filename, three kinds of object: tz table ⇎ byte-identical twin ⇎ sibling table ⇎ HTML index page, 2026-10-20)

B45 = `corpus/babeltele/B45_registry_name_two_objects.md`, 4 raw sources under `corpus/raw/`
(`tz/zone1970.tab`, `zone1970_latest.tab`, `tz/zone.tab`, `zone1970.tab`), 50 anchor slots / %d distinct
strings, %d DERIV keys, %d CNT terms folded into the single `0` key, retention %s (vs-raw %s, tool table
column 4), 0 items left in 待核. Library now **%d entries / %d machine-checked derivations**
(enc %s ⇎ digest %s, %d unique codepoints).

Four durable methodology facts:

- **`%%r` already escapes.** Building a CNT expression with `u"CNT(%%r,%%d)" %% (pattern, i)` is correct;
  pre-escaping backslashes (`p.replace('\\\\','\\\\\\\\')`) double-escapes and silently changes regex
  semantics — it turned 111/201/312/418 into garbage keys and the failure only showed up as wrong DERIV
  values, not as an error. Same trap in single-quoted builder literals: `u',0)-CNT('` swallows the trailing
  apostrophe and writes a broken expression into audit.py. Repair scripts must be **written as a .py file**,
  not as a nested quoted heredoc — the quoting destroyed the fix itself.
- **Never write algorithm names or whole-file counts inside ⟪BabelTele⟫.** `sha256` puts the hard anchor
  `256` into the encoding, which cannot resolve in the source ⇒ FAIL; whole-file line counts (376 / 449 /
  1271) and byte sizes belong in the `src:` header or `## ⛓解读注` (neither is scanned). In the body use
  Chinese numerals for unkeyed counts, and keep the audited-scope numbers as DERIV keys.
- **`re.findall` over a long branch alternation counts non-overlapping hits ⇒ rows, not pairs.** That looks
  like a bug (34 instead of 111) and is actually the entry's hardest claim: the A-only ⇎ N-only pair
  disagreement lives exactly on the %d comma-merged rows, while the %d flat rows agree pair-by-pair. Turn the
  surprise into three assertions — the alternation scored 0 in the other table, its "flat row × diff pair"
  variant scored 0 in this table, and `CNT(AONLY-alternation, own table) == CNT(merged-row-count)` folded into
  `0` — instead of "fixing" the count.
- **Three rungs of checkability must be disclosed, not blended:** (1) CNT-provable (length, rows, separator
  and marker hits, four zero-hit claims); (2) external assertion only — byte-identity of the two copies needs
  a hash, so name the algorithm and paste the 64 hex chars in the `src:` line (the builder asserts equality
  with `hashlib` itself); (3) tool-side facts that no CNT can reach (byte size 17592 ⇎ 65372, "member of the
  tzdata archive"). And when a pair-set size comes from Python set arithmetic (111 / 106), say in 解读注 that
  the CNT-side evidence is the width-bucket sum plus the zero-hit alternations — same value, different
  computation.

Scope duality is now a first-class claim: the auditor's `_reason()` drops `#`-comment and `src:`-style lines,
so `1970` and `public domain` are **0 in scope yet present in the file**. A `0` must state which of the two
causes it has. Whole-file vs in-scope counts differ for the same bytes (%d ⇎ %d rows, %d ⇎ %d chars) — every
"N rows / N chars" claim has to name its scope.

**How to apply:** for any "same name, different object" or registry-vs-sibling-table entry, classify the
object first by separator/marker density (tabs %d ⇎ %d ⇎ %d vs angle brackets 0 ⇎ %d), then compute a **two-sided**
pair diff and require each side's alternation to score 0 in the other file; never trust ⟦LBL⟧ attribution to
the tools (both atomcheck and audit concatenate all sources of a tag, so a mislabeled label still passes —
byte-identical twins make this acute). Reuse material: `probe/bio_recent.json` (API index vs total counts),
`cot/prompts/*`, `UnicodeData.txt`, `tz/zonenow.tab` + `iso3166.tab` (kept out of B45 because B10 already
owns the 312 ⇎ 91 registry-vs-codebook axis).
''' % (NUM(u'uniq_anchor'), NUM(u'deriv_keys'), NUM(u'n_term0'), b45[2], b45[3], NENT, proofs,
       format(enc_all, u',').replace(u',', u' '), format(dig_all, u',').replace(u',', u' '), uniq_all,
       NUM(u'merged_rows'), NUM(u'flat_rows'),
       NUM(u'full_lines')[0], ROWS_A, RCOT_A, FULL_A,
       TABS_A, TABS_N, TABS_H, LT_H)

t = io.open(FILE, encoding='utf-8').read()
assert u'## 22.' not in t, u'B45 一节已存在'
io.open(FILE, 'w', encoding='utf-8').write(t.rstrip() + u'\n' + SEC)

idx = io.open(IDX, encoding='utf-8').read()
new_line = (u'- [Corpus selection & proof rule](corpus-selection-and-proof-rule.md) — v2: compress reasoning '
            u'not lookups; %d 条 PASS (%d DERIV 条); 锚点从折叠原文切片⇒逐字由构造保证; 计数一律用 audit 口径; '
            u'DERIV 键名即数值⇒写前断言互不相同; 三态可核性(机检 ⇎ 外部哈希 ⇎ 工具侧)必须分列不混谈; '
            u'0 有两种成因(口径剔注释行); findall 对交替式数的是行不是对' % (NENT, proofs))
idx2 = re.sub(u'^- \\[Corpus selection & proof rule\\].*$', new_line, idx, count=1, flags=re.M)
assert idx2 != idx, u'索引行未替换'
io.open(IDX, 'w', encoding='utf-8').write(idx2)
print(u'memory 追加 §22 完成: %d 条 / %d 推导; 索引行已更新(长度 %d)' % (NENT, proofs, len(new_line)))
