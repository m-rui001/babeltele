# -*- coding: utf-8 -*-
"""项目记忆记账: 追加 B46 一节, 并把 MEMORY.md 索引行改成 46 条 / audit 自报推导数。
全部数字取自 _f46stats.txt、raw 现算与 audit 现跑结果, 不手填。"""
import io, re, sys, ast, json, subprocess

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


ST = loadstat(u'corpus/_f46stats.txt')
NUM = lambda k: ast.literal_eval(ST[k]) if ST[k].strip().startswith(u'[') else int(ST[k])
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-400:]
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
enc_all, dig_all, uniq_all = int(allc[1].replace(u' ', u'')), int(allc[0].replace(u' ', u'')), int(allc[4])
NENT = len(row) - 1
b46 = [x.strip() for x in row[u'B46'].split(u'|')]
assert NENT == 46 and int(b46[1]) == int(ST[u'enc']) and int(b46[10]) == 0, (NENT, b46)
assert (NUM(u'deriv_keys'), NUM(u'n_terms0'), NUM(u'n_term0'), NUM(u'n_diff')) == (29, 46, 59, 4)
assert (NUM(u'anchors'), NUM(u'uniq_anchor'), NUM(u'gloss_lines')) == (67, 22, 13)

RJ = u'corpus/raw/api/bio_recent_2026w01.json'
RP = u'corpus/raw/prose/biorxiv_bacterial_organelles.txt'
HEADRX = re.compile(r'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
BS = u'\\'
TXT = [io.open(x, encoding='utf-8', errors='replace').read() for x in (RJ, RP)]
SRC = [u'\n'.join(l for l in x.split(u'\n') if not HEADRX.match(l.strip())) for x in TXT]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
RCOT = lambda i: len(SRC[i].strip())
DOI_E = u'10.1101' + BS + u'/2025.09.22.677801'
DOI_P = u'10.1101/2025.09.22.677801'
ROWS = json.loads(SRC[0])[u'collection']
ENVD = json.loads(SRC[0])[u'messages'][0]
PUBS = [r[u'published'] for r in ROWS if str(r[u'published']).startswith(u'10.')]
REG = len(set(x.split(u'/')[0] for x in PUBS))
CHP = int(re.search(u'chars: (\\d+)', TXT[1]).group(1))
ESC_J, PLAIN_P = CNT(re.escape(DOI_E), 0), CNT(re.escape(DOI_P), 1)
CROSS_J, CROSS_P = CNT(re.escape(DOI_P), 0), CNT(re.escape(DOI_E), 1)
SL, NA_P = CNT(BS + BS + u'/', 0), CNT(u'[^' + BS + u'x00-' + BS + u'x7f]', 1)
UESC, BARE, QUOT = CNT(BS + BS + u'u', 0), CNT(u'":' + BS + u'd', 0), CNT(u'"[0-9]', 0)
NA_N, PD_N = CNT(u'"published":"NA"', 0), CNT(u'"published":"10\\.', 0)
LIC_J, LIC_P = CNT(u'"license":"cc_by_nc_nd"', 0), CNT(u'CC-BY-NC-ND', 1)
NEWP, TOT = int(ENVD[u'count_new_papers']), int(ENVD[u'total'])
assert (ESC_J, PLAIN_P, CROSS_J, CROSS_P) == (1, 41, 0, 0)
assert (len(ROWS), NA_N, PD_N, REG) == (30, 22, 8, 6)
assert (SL, NA_P, UESC, BARE, QUOT) == (303, 331, 6, 1, 103)
assert (LIC_J, LIC_P) == (11, 40) and ENVD[u'count'] == 30
assert (RCOT(0), RCOT(1), CHP) == (69657, 80699, 80626) and RCOT(1) - CHP == 73

EARLY = CNT(u'content' + BS + BS + u'/early', 0)
assert EARLY == 30

SEC = u'''
## 23. What B46 taught (a catalogue row ⇎ the paper it names: the join key never shares a spelling, and a `0` can be an escape layer, 2026-10-20)

B46 = `corpus/babeltele/B46_catalog_row_vs_the_paper_it_names.md`, 2 raw sources
(`api/bio_recent_2026w01.json` — bioRxiv recent-API catalogue page, one line of JSON — ⇎
`prose/biorxiv_bacterial_organelles.txt` — the extracted text of the paper one of its rows names, the B16 raw).
%d anchor slots / %d distinct strings, %d judgement lines, %d DERIV keys whose `0` holds %d additive terms
(%d absence classes + %d equality/"exactly-N" claims, %d CNT primitives in total, %d subtractive keys),
retention %s (vs-raw %s), 0 items in 待核, cross-source literal anchors = %d. Library now **%d entries /
%d machine-checked derivations** (enc %s ⇎ digest %s, %d unique codepoints).

Five durable methodology facts:

- **`re.sub(pattern, BLOCK, s)` treats BLOCK as a replacement template and halves every backslash.** A builder
  that splices regex-bearing DERIV text into `audit.py` must pass `lambda m: BLOCK`. The failure is quiet: the
  builder's own recompute (using the un-halved string) passed while audit evaluated a different regex, showing
  up only as bogus 提示 values (11.0 / 0.0), not as an error. Same trap fixed in `_mkB45.py`.
- **Count the escape ladder before believing a `0`.** This file writes every slash as `\\/`, so a pattern for
  `content/early` scored 0 and looked like a path fact; with the layer added (`content\\\\/early`, i.e. Python
  `BS+BS+'/'`) the same place hit %d times. Only then did the real 0 appear: `jatsxml` URLs **drop the registry
  prefix** and put the delivery date in its place. Every `0` in a JSON/XML source should be re-run one escape
  level deeper first.
- **Metadata ⇎ the object it describes: test the join key in four cells.** Escaped DOI in the catalogue %d,
  plain DOI in the paper %d, and both cross directions %d/%d ⇒ no spelling is shared, so "these two files are
  about one thing" is a reconstruction, never a literal join. Corollaries that all became machine checks: the
  catalogue's `%d` rows carry %d placeholder `NA` + %d journal DOIs from %d registries in `published` (a field
  whose name promises a date and delivers an identifier), and a five-day declared interval delivered only day
  one.
- **Self-reports split by "can this file check it".** `count`=%d equals the row count ⇒ keep the equation;
  `%d` and `%d` speak about files outside this one ⇒ keep only their differences as subtractive keys
  (%d/%d/%d) and say in the gloss they are unverifiable. Likewise the three char scopes (%d ⇎ %d ⇎ %d, diff %d
  = the `url:` line) and the byte size are tool-side, as is sha256: name the algorithm and put the 64 hex
  digits in the `src:` line, never in ⟪BabelTele⟫ where `256` would become a hard anchor.
- **Literal comparison goes blind at the encoding layer.** %d escaped slashes with 0 bare ones, %d `\\u`
  escapes (5 combining diacritics + 1 Greek letter) against %d non-ASCII codepoints written directly,
  `cc_by_nc_nd` %d ⇎ `CC-BY-NC-ND` %d, glued `University of Michigan-Ann Arbor` ⇎ `Michigan; Ann Arbor, …`,
  the 12-name semicolon author string 0 times in the paper. Sentence-level alignment of the abstract (7
  sentences, %d verbatim, %d rewritten) is Python set work; CNT only proves the two literals on each side, and
  that split must be disclosed.

**How to apply:** for any "index vs the thing indexed" pair, (1) prove the key cannot be joined literally before
claiming the pair is a pair; (2) fold all equality claims into `0` (key name == value, so same-valued claims
collide) and state the term counts from the expression itself (`split0()` here) rather than re-typing them;
(3) let anchor-uniqueness-within-source do the discovery work — it rejected `"published":"NA","server":"bioRxiv"`
(%d repetitions) and forced every anchor onto the joined row's own literals; (4) stats files must be **merged**
on rewrite (`dict(BST, **ST)`), and downstream scripts should recompute differences from raw instead of reading
fields a later step may overwrite. Housekeeping: `raw/probe/bio_recent.json` is byte-identical to
`raw/api/bio_recent_2026w01.json` (same sha256, %d bytes) — §22 listed it as reuse material; B46 consumes that
axis, so treat the probe copy as superseded. Remaining candidates: `cot/prompts/*` (instruction ⇎ produced
reasoning), `UnicodeData.txt`/`scripts.txt`, `tz/zonenow.tab` + `iso3166.tab`, the `probe/` HTML⇎XML pairs
(`_f_2026-*.htm`, `fr_2026-21376.xml`), and the sanctioned `E:/tools` OpenCode2API sub-agent route (still untested).
''' % (NUM(u'anchors'), NUM(u'uniq_anchor'), NUM(u'gloss_lines'), NUM(u'deriv_keys'), NUM(u'n_terms0'),
       NUM(u'n_absent'), NUM(u'n_equ'), NUM(u'n_term0'), NUM(u'n_diff'), b46[2], b46[3], NUM(u'cross_atoms'),
       NENT, proofs, format(enc_all, u',').replace(u',', u' '), format(dig_all, u',').replace(u',', u' '),
       uniq_all,
       EARLY, ESC_J, PLAIN_P, CROSS_J, CROSS_P, len(ROWS),
       NA_N, PD_N, REG, ENVD[u'count'], NEWP, TOT, NEWP - len(ROWS), TOT - NEWP, TOT - len(ROWS),
       CHP, RCOT(1), len(TXT[1]), RCOT(1) - CHP,
       SL, UESC, NA_P, LIC_J, LIC_P, NUM(u'n_sent_hit'), NUM(u'n_sent_out'),
       CNT(u'"published":"NA"', 0), len(TXT[0]))

t = io.open(FILE, encoding='utf-8').read()
assert u'## 23.' not in t, u'B46 一节已存在'
io.open(FILE, 'w', encoding='utf-8').write(t.rstrip() + u'\n' + SEC)

idx = io.open(IDX, encoding='utf-8').read()
new_line = (u'- [Corpus selection & proof rule](corpus-selection-and-proof-rule.md) — v2: compress reasoning '
            u'not lookups; %d 条 PASS (%d DERIV 条); 锚点从折叠原文切片⇒逐字由构造保证; 计数一律用 audit 口径; '
            u'DERIV 键名即数值⇒等式折进 0 键; 三态可核性(机检 ⇎ 外部哈希 ⇎ 工具侧)不混谈; 0 有两种成因(注释行被剔 '
            u'⇎ 转义层遮蔽); re.sub 会把 BLOCK 当模板减半反斜杠⇒用 lambda' % (NENT, proofs))
idx2 = re.sub(u'^- \\[Corpus selection & proof rule\\].*$', new_line, idx, count=1, flags=re.M)
assert idx2 != idx, u'索引行未替换'
io.open(IDX, 'w', encoding='utf-8').write(idx2)
print(u'memory 追加 §23 完成: %d 条 / %d 推导; 索引行已更新(长度 %d)' % (NENT, proofs, len(new_line)))
