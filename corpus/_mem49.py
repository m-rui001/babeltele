# -*- coding: utf-8 -*-
"""项目记忆记账: 追加 §27 (B49)。库级数字现取 audit, 条目级现取 _f49stats/正文/电池/awk 源码, 不手填。"""
import io, os, re, sys, json, subprocess, collections

sys.stdout.reconfigure(encoding='utf-8')
MEMDIR = os.path.expanduser(u'~/.qoder-cn/projects/E--BabelTele/memory')
MEMF = os.path.join(MEMDIR, u'corpus-selection-and-proof-rule.md')
IDXF = os.path.join(MEMDIR, u'MEMORY.md')
ENTRY = u'corpus/babeltele/B49_table_checker_and_checked_data.md'
STAT = u'corpus/_f49stats.txt'

# ---------- 库级: 从 audit 现读 ----------
p = subprocess.run([sys.executable, u'-X', u'utf-8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-600:]
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
b49c = [x.strip() for x in row[u'B49'].split(u'|') if x.strip()]
NENT = 49
dig_all, enc_all, ret_all, uniq_all = (int(allc[0].replace(u' ', u'')), int(allc[1].replace(u' ', u'')),
                                       allc[2], int(allc[4]))
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
soft_all = int(re.search(u'提示\\(不计入 FAIL, 1-2 位结构计数未逐位核验\\): 共 (\\d+) 个', p.stdout).group(1))
assert (NENT, proofs, soft_all) == (49, 581, 17), (NENT, proofs, soft_all)

# ---------- 条目级: 现读 stats + 正文 ----------
BST = {}
for l in io.open(STAT, encoding='utf-8').read().split(u'\n'):
    if re.search(u'[ \t]', l):
        k, v = l.split(None, 1)
        BST[k] = v.strip()
NUM = lambda k: int(BST[k])
md = io.open(ENTRY, encoding='utf-8').read()
body = re.search(u'⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', body)
labels = re.findall(u'⟦([TCZ])⟧⟨', body)
NOCC, DIST = len(atoms), len(set(atoms))
NLAB = dict((c, labels.count(c)) for c in u'TCZ')
REG = [x.rstrip(u'\n') for x in io.open(u'corpus/_atoms49.txt', encoding='utf-8') if x.strip()]
UNCITED = len([x for x in REG if x not in set(atoms)])
NKEY = NUM(u'deriv_keys')
b49_enc, b49_dig = int(b49c[1].replace(u' ', u'')), int(b49c[0].replace(u' ', u''))
b49_uniq, b49_blocks = int(b49c[4]), int(b49c[5])
assert (NOCC, DIST, UNCITED, NKEY) == (118, 49, 2, 69), (NOCC, DIST, UNCITED, NKEY)
assert (len(REG), b49_enc, b49_dig) == (51, 13279, 3400)
BAT = json.load(io.open(u'corpus/_b49battery.json', encoding='utf-8'))

# ---------- 0 键三口径: 现读 audit.py ----------
AUD = io.open(u'corpus/audit.py', encoding='utf-8').read()
ZEXP = re.search(r"'B49': \{\n  '0': ('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"),", AUD).group(1)
import ast
ZEXP = ast.literal_eval(ZEXP)
PR = tuple(int(x) for x in BST[u'printf'].split())  # 语句数 文本数 带行号 只报名字 stderr stdout status


def _split_depth0(e):
    out, buf, depth, q, esc = [], [], 0, None, False
    for ch in e:
        if q:
            buf.append(ch)
            if esc:
                esc = False
            elif ch == u'\\':
                esc = True
            elif ch == q:
                q = None
            continue
        if ch in (u'"', u"'"):
            q = ch
        elif ch == u'(':
            depth += 1
        elif ch == u')':
            depth -= 1
        elif ch == u'+' and depth == 0:
            out.append(u''.join(buf))
            buf = []
            continue
        buf.append(ch)
    out.append(u''.join(buf))
    return out


NDEP0 = len(_split_depth0(ZEXP))
NLEAF = ZEXP.count(u'CNT(') + ZEXP.count(u'CNTF(') + ZEXP.count(u'B49V(') + ZEXP.count(u'L(') \
    + ZEXP.count(u'B49_LINES(') + ZEXP.count(u'B49_DROP(') + ZEXP.count(u'B49_BYTES(')
assert NLEAF == 234 and NDEP0 == 129 and NUM(u'n_term0') == 120, (NLEAF, NDEP0)
_fold = lambda s: re.sub(u'\\s+', u' ', s)
DIG = md[:md.index(u'## ⟪BabelTele⟫')]
DIGHIT = len([a for a in atoms if _fold(a) in _fold(DIG)])
EXACT = len([a for a in atoms if a in DIG])
assert (DIGHIT, NOCC, EXACT) == (104, 118, 1)
NCLS = dict((k, len([x for x in BAT if x.startswith(k + u'_')])) for k in (u'd', u'c', u'crlf', u'base'))
NCLS[u'restore'] = len([x for x in BAT if x == u'restore'])
NCLS[u'warn'] = len(BAT) - sum(NCLS.values())
assert NCLS == {u'd': 17, u'c': 12, u'crlf': 5, u'base': 2, u'restore': 1, u'warn': 1}, NCLS
assert u'warn_off_flag' in BAT

# 正文里出现的每一个源侧/执行侧字面数, 都在此与实测对齐(记忆条目不许手填)
NL = tuple(int(x) for x in BST[u'lines'].split())
EL = NUM(u'el')
ZT = tuple(int(x) for x in BST[u'zone_tab'].split())
assert (NUM(u'rows'), NUM(u'c4'), NUM(u'c3')) == (312, 201, 111)
assert NL == (375, 228, 4212) and EL == 1020
assert ZT == (418, 336, 337)
assert (BAT[u'c_cc_lt'][u'nerr'], BAT[u'c_iso_lt'][u'nerr'], BAT[u'c_seen_off'][u'nerr']) == (158, 0, 312)
assert (BAT[u'c_exempt_dead'][u'nerr'], BAT[u'c_backward'][u'nerr']) == (1, 0)
assert (BAT[u'd_duprow'][u'exit'], BAT[u'd_duprow'][u'nerr'], BAT[u'd_duprow'][u'nout']) == (1, 0, 1)
assert max(BAT[k][u'nerr'] + BAT[k][u'nout'] for k in BAT if k.startswith(u'crlf')) == 0

# printf 站点: 把反斜杠续行折成逻辑行再按(流, 是否置失败码)分类, 与 stats 记录对齐
BS = chr(92)
AWKL = io.open(u'corpus/raw/tz/checktab.awk', encoding='utf-8').read().split(u'\n')
LOG, jj = [], 0
while jj < len(AWKL):
    st, pp = jj, [AWKL[jj]]
    while pp[-1].rstrip().endswith(BS) and st + len(pp) < len(AWKL):
        pp.append(AWKL[st + len(pp)])
    LOG.append(u' '.join(x.strip().rstrip(BS).strip() for x in pp))
    jj = st + len(pp)
SITE = [(k, s) for k, s in enumerate(LOG) if u'printf' in s]
SETST = lambda k: u'status = 1' in u' '.join(LOG[k:k + 3])
NST = len(SITE)
NERR = len([1 for k, s in SITE if u'stderr' in s])
NSTAT = len([1 for k, s in SITE if SETST(k)])
NOUTERR = len([1 for k, s in SITE if u'stderr' not in s and SETST(k)])
assert (NST, NERR, NST - NERR, NSTAT, NOUTERR) == (PR[0], PR[4], PR[5], PR[6], 3), (NST, NERR, NSTAT, NOUTERR)

# 登记表 ⇎ 正文引用: atomcheck 真跑一次
ac = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/atomcheck.py', u'B49', u'corpus/_atoms49.txt'],
                    capture_output=True, text=True, encoding='utf-8')
AK, ABAD = (int(x) for x in re.search(u'ok=(\\d+) bad=(\\d+)', ac.stdout).groups())
assert (AK, ABAD) == (len(REG), 0), ac.stdout[-300:]
NAIVE = len(ZEXP.split(u'+'))
assert (NAIVE, NDEP0, NUM(u'n_term0')) == (131, 129, 120), (NAIVE, NDEP0)
assert (NUM(u'coin'), NUM(u'gloss_lines')) == (31, 14)

TXT = io.open(MEMF, encoding='utf-8').read()
SP = lambda v: format(v, u',').replace(u',', u' ') if v >= 1000 else str(v)
RETALL = ret_all.strip(u'*')

NEW = (u'''
## 27. What B49 taught (a table ⇎ the program that checks it ⇎ the data it checks: emptiness as the product, 2026-10-21)

B49 = `corpus/babeltele/B49_table_checker_and_checked_data.md`, 3 raw sources: `tz/zone1970.tab` (%d data rows =
%d four-column ⇎ %d three-column) ⇎ `tz/checktab.awk` (%s lines, %d printf sites) ⇎ `tz/europe` (%s lines,
%s non-comment under the checker's own definition). %d anchor slots / %d distinct strings (⟦T⟧ %d ⇎ ⟦C⟧ %d ⇎ ⟦Z⟧ %d),
%d judgement lines, %d DERIV keys whose `0` holds %d primitive calls, %d coincident-value groups folded into
machine-checked equalities, retention %s (vs-raw %s), %d unique codepoints, %d blocks, 待核 = 0.
A %d-cell mutation battery (数据侧 %d ⇎ 程序侧 %d ⇎ CRLF %d ⇎ 基线 %d ⇎ 还原 %d ⇎ 警告开关 %d) is the entry's evidence layer;
its raw outputs live in `corpus/_b49battery.json` and every 工具侧 number in ⛓解读注 is rendered from that file.
Library now **%d entries / %d machine-checked derivations** (enc %s ⇎ digest %s ⇒ corpus retention **%s**,
%s unique codepoints, %d tolerated hints).

Five methodology facts that generalize beyond tz data:

- **The entry's own bookkeeping has three 口径 for the same 0-key, and none of them is a naive `split('+')`.**
  The audit expression text splits into %d pieces on a literal `+`, %d pieces when `+` inside string literals and
  inside parentheses are excluded, and the builder emitted %d `+`-joined terms — the last two differ because some
  terms are themselves sums. Report all three numbers with their cause; a single "N additive terms" claim is
  unverifiable by construction. Same class of trap as B46's escape ladder: the counting *scope* is the claim.
- **A registered anchor is not a cited anchor.** atomcheck proves %d registered strings verbatim-in-raw (ok=%d bad=%d),
  while the body tags %d occurrences / %d distinct strings — %d registered strings were never cited. Keep the two
  counts separate in README and in memory; conflating them claims coverage the entry does not have. (B47 already
  demanded "every registered anchor appears in the body" — B49 shows the converse bookkeeping must be published too.)
- **Digest ⇎ body comparison needs whitespace folding, not substring search.** Table rows are tab-delimited and the
  digest re-indents them, so an exact substring test matches only %d of %d atoms; folding runs of whitespace to one
  space matches %d. Never report a digest hit-rate without naming the normalizer (and never let it be the same
  number as atomcheck's `prose_norm` rate — different normalizers, different claims).
- **A validator's golden path is emptiness.** Clean runs gave `exit 0` with 0 bytes on both streams (%d baseline cells
  in this battery; §26 records the third table configuration behaving the same), so every invariant had to be
  *named by breakage*: flipping one comparison operator (`cc < cc0` →
  `<=`) emitted %d diagnostics = the independently recomputed count of adjacent equal country codes; the symmetric
  flip on the iso loop emitted 0 (repeated codes are legal there, and that tolerance lives in one character);
  breaking one guard condition emitted %d = the whole table. CRLF is **not** an invariant here (all %d CRLF cells
  went silent) — an earlier dramatic CRLF result was an artifact of text-mode writes, see §26.
- **Error ⇎ stream and 局部 ⇎ 全局 remain separate axes.** Of %d printf sites, %d write to stderr, %d do not, and
  %d of those %d non-stderr ones are failures rather than warnings: duplicating a table row gave `exit %d` with 0
  bytes on stderr. Exemptions are per-invocation: killing the `zone.tab` waiver emits exactly %d diagnostic
  (line %d of %d), killing the `backward` waiver emits %d — dead code is only dead relative to a chosen invocation,
  so always name it.

Three accounting-script bugs worth remembering (each cost one run):

- **Never reuse a short variable name across sections of a bookkeeping script.** `for t in EL:` over the europe lines
  overwrote the README text variable `t`, and the next `re.search` died with "expected string, got list". Statement-level
  loops leak their loop variable; comprehensions do not — that asymmetry is what made this hard to see.
- **Multi-value stat lines cannot go through `int()`.** The stats file stores `rdef 30 29 13`; asserting with a scalar
  parser raised `invalid literal`. Compare whole tuples (`sp(u'rdef') == (30, 29, 13)`) — this is the tuple-vs-list
  trap from §26 again, now on the read side.
- **Parse the audit 0-key with `ast`, not with regex counts alone.** The expression contains `Sub` and `Mult` nodes and
  four primitive families beyond CNT/CNTF/B49V (`L`, `B49_LINES`, `B49_DROP`, `B49_BYTES`), so any hand-count of
  "additive terms" is wrong; `ast.parse` + a leaf walk gives the truth and the operator-count identity
  `leaves - 1 == Add + Sub + Mult` is a free consistency check. A second instance of the same trap: joining
  backslash-continued awk lines stops after one step if you test the *accumulated* string for a trailing backslash —
  strip it per line and test the source line, or printf-site tallies silently read 10/8 instead of 14/4.

**How to apply:** for any artifact ⇎ validator pair (linter, schema checker, CI script), (1) record the clean run's
exit + both stream byte counts as the baseline claim; (2) enumerate emitters by (stream, locator shape, error-or-warning);
(3) mutate one field per case on BOTH sides and classify each response as 局部 ⇎ 关系 ⇎ 全局聚合; (4) publish the three
口径 of any folded 0-key (naive split / depth-aware split / builder term count) instead of one number; (5) publish
registered-anchor vs cited-anchor counts separately; (6) in bookkeeping scripts, give every section its own variable
names and re-derive every README claim from a live tool run — `corpus/_readme49.py` re-runs the battery's gawk cells
and asserts byte-equality with the stored battery, and this script re-runs `audit.py` + `atomcheck.py` and re-classifies
the printf sites from the awk source. B49 consumes the tz `checker ⇎ tables` axis; still unused:
`tz/zonenow.tab` as a primary source, `langsubtag.txt`, the fips202 pdf ⇎ txt ⇎ html trio,
`codata_table.html` ⇎ `codata_all.html`, `cot/prompts/*`, and the `probe/` HTML⇎XML pairs.
''' % (NUM(u'rows'), NUM(u'c4'), NUM(u'c3'), NL[1], PR[0], SP(NL[2]), SP(EL),
       NOCC, DIST, NLAB[u'T'], NLAB[u'C'], NLAB[u'Z'], NUM(u'gloss_lines'), NKEY, NLEAF, NUM(u'coin'),
       b49c[2], b49c[3], b49_uniq, b49_blocks, len(BAT),
       NCLS[u'd'], NCLS[u'c'], NCLS[u'crlf'], NCLS[u'base'], NCLS[u'restore'], NCLS[u'warn'],
       NENT, proofs, format(enc_all, u',').replace(u',', u' '), format(dig_all, u',').replace(u',', u' '),
       RETALL, SP(uniq_all), soft_all,
       NAIVE, NDEP0, NUM(u'n_term0'),
       len(REG), AK, ABAD, NOCC, DIST, UNCITED,
       EXACT, NOCC, DIGHIT,
       NCLS[u'base'], BAT[u'c_cc_lt'][u'nerr'], BAT[u'c_seen_off'][u'nerr'], NCLS[u'crlf'],
       NST, NERR, NST - NERR, NOUTERR, NST - NERR, BAT[u'd_duprow'][u'exit'],
       BAT[u'c_exempt_dead'][u'nerr'], ZT[2], ZT[0], BAT[u'c_backward'][u'nerr']))

# 只保留一处新段: 若已存在 §27 则整体替换(幂等)
mark = u'## 27. What B49 taught'
if mark in TXT:
    TXT = TXT[:TXT.index(mark)].rstrip() + u'\n'
TXT = TXT.rstrip(u'\n') + NEW

# 索引行只改计数那一小段(现取, 可重跑)
IDX = io.open(IDXF, encoding='utf-8').read()
IDX2, NIDXSUB = re.subn(u'\\d+ 条 PASS \\(\\d+ DERIV 条\\)', u'%d 条 PASS (%d DERIV 条)' % (NENT, proofs), IDX)
assert NIDXSUB == 1, IDX[:200]
io.open(IDXF, u'w', encoding='utf-8').write(IDX2)
io.open(MEMF, u'w', encoding='utf-8').write(TXT)

print(u'memory §27 written: %d 条／%d 推导／enc %s⇎digest %s⇒%s／码点 %s／提示 %d｜B49 %d 标注／%d 串／%d 键／0 键 %d 调用'
      % (NENT, proofs, format(enc_all, ',').replace(',', ' '), format(dig_all, ',').replace(',', ' '),
         RETALL, SP(uniq_all), soft_all, NOCC, DIST, NKEY, NLEAF))
print(u'size: %d chars; index → %s' % (len(TXT), [l for l in IDX2.split(u'\n') if u'%d 条 PASS' % NENT in l][0][:130]))
