# -*- coding: utf-8 -*-
"""项目记忆记账: 追加 B48 一节(§25), 并把 MEMORY.md 索引行改成 48 条 / audit 自报推导数。
全部数字取自 _f48stats.txt、三份 raw 现算、audit 现跑结果, 并在这里第三次真执行生成器, 不手填。"""
import io, re, sys, os, ast, hashlib, subprocess, tempfile, datetime

sys.stdout.reconfigure(encoding='utf-8')
MEMD = u'C:/Users/hp/.qoder-cn/projects/E--BabelTele/memory'
FILE = MEMD + u'/corpus-selection-and-proof-rule.md'
IDX = MEMD + u'/MEMORY.md'

RI = u'corpus/raw/tz/leap-seconds.list'
RA = u'corpus/raw/tz/leapseconds.awk'
RL = u'corpus/raw/tz/leapseconds'
RAWS = [RI, RA, RL]
HEADRX = re.compile(u'^(#|src:|title:|author:|chars:|text_sha256:|retrieved:|note:)', re.I)
NL, TAB, BS = u'\n', u'\t', u'\\'


def loadstat(fn):
    d = {}
    for l in io.open(fn, encoding='utf-8').read().split(NL):
        if u'\t' in l:
            k, v = l.split(u'\t')
            d[k] = v
    return d


ST = loadstat(u'corpus/_f48stats.txt')


def NUM(k):
    v = ST[k].strip()
    if v.startswith(u'[') or v.startswith(u'('):
        return ast.literal_eval(v)
    if u' ' in v:
        return [int(x) for x in v.split()]
    try:
        return int(v)
    except ValueError:
        return v


full = lambda i: io.open(RAWS[i], encoding='utf-8', errors='replace').read()
reason = lambda i: NL.join(l for l in full(i).split(NL) if not HEADRX.match(l.strip()))
SRC = [reason(i) for i in range(3)]
CNT = lambda pat, i: len(re.findall(pat, SRC[i], re.I))
CNTF = lambda pat, i: len(re.findall(pat, full(i), re.I))
RCOT = lambda i: len(SRC[i].strip())
BYTES = [os.path.getsize(p) for p in RAWS]
FULLN = [len(full(i)) for i in range(3)]
SHA = [hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in RAWS]
COM = lambda n: format(n, u',').replace(u',', u' ')
cut = lambda s, n=12: s[:n] + u'…'

# ---------- 与 _f48stats 对表(独立读文件) ----------
assert (FULLN, BYTES, SHA) == (NUM(u'full'), NUM(u'bytes'), [ST[u'sha_i'], ST[u'sha_a'], ST[u'sha_l']])
assert (NUM(u'lines'), NUM(u'dropped'), NUM(u'rcot')) == \
       ([len(full(i).split(NL)) - 1 for i in range(3)],
        [len([l for l in full(i).split(NL) if HEADRX.match(l.strip())]) for i in range(3)],
        [RCOT(i) for i in range(3)])
assert (NUM(u'rcot_sum'), NUM(u'bytes_sum')) == (sum(RCOT(i) for i in range(3)), sum(BYTES))
assert RCOT(0) == 1035 and RCOT(1) == 6464 and RCOT(2) == 809
assert [CNT(u'[^\x00-\x7f]', i) for i in range(3)] == [0, 0, 0]      # 纯 ASCII: 字符数=字节数

# ---------- audit 现跑: 条数 / 推导数 / 待核 ----------
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
assert u'保真门槛' in p.stdout and u'PASS' in p.stdout, p.stdout[-500:]
proofs = int(re.search(u'已机检的推导\\((\\d+) 条\\)', p.stdout).group(1))
row = dict((m.group(1), m.group(2)) for m in re.finditer(r'^\| (B\d+|ALL) \|(.*)\|$', p.stdout, re.M))
allc = [x.strip() for x in row[u'ALL'].split(u'|') if x.strip()]
dig_all, enc_all, uniq_all = int(allc[0].replace(u' ', u'')), int(allc[1].replace(u' ', u'')), int(allc[4])
NENT = len(row) - 1
b48 = [x.strip() for x in row[u'B48'].split(u'|')]
assert NENT == 48 and proofs == NUM(u'proofs') == 516, (NENT, proofs)
assert int(b48[1]) == NUM(u'enc') and int(b48[10]) == NUM(u'soft_b48') == 1, b48
assert (b48[2], b48[3]) == (ST[u'ret'], ST[u'dens'])
assert (int(b48[4]), b48[5], b48[6]) == (NUM(u'uniq_cp'), ST[u'blocks'], ST[u'cpu'])
assert (allc[2], allc[10]) == (ST[u'all_ret'], u'17')
assert (enc_all, dig_all, uniq_all) == (NUM(u'all_enc'), NUM(u'all_digest'), NUM(u'all_cp'))
assert re.search(u'^\\s+B48 \\[.48.\\]$', p.stdout, re.M), u'B48 的待核项应恰为条目号 48'
NHINT = int(re.search(u'共 (\\d+) 个', p.stdout).group(1))
assert NHINT == 17

# ---------- 第三次真执行: 生成器跑在输入上 ----------
GVER = subprocess.run([u'gawk', u'-W', u'version'], capture_output=True, text=True,
                      encoding='utf-8', errors='replace').stdout.split(NL)[0]
with tempfile.NamedTemporaryFile(suffix=u'.out', delete=False) as tf:
    tmp = tf.name
try:
    with open(tmp, 'wb') as fo:
        subprocess.run([u'gawk', u'-f', RA, RI], stdout=fo, check=True)
    RB = hashlib.sha256(open(tmp, 'rb').read()).hexdigest()
finally:
    os.unlink(tmp)
assert RB == SHA[2] == ST[u'repro_sha'] and GVER == ST[u'gawk'], (RB, GVER)

# ---------- 转义层: 同一 pattern 的两种拼法 ----------
TAB_REAL = [CNT(TAB, i) for i in range(3)]
TAB_LIT = [CNT(u'\\\\t', i) for i in range(3)]
Q_ALL = [CNT(u'"', i) for i in range(3)]
Q_LIT = [CNT(u'\\\\"', i) for i in range(3)]
N_LEAP = CNT(u'(?m)^Leap\t', 2)
TAB_PER = CNT(u'\t', 2) // N_LEAP
assert TAB_REAL == [0, 31, 162] and TAB_LIT == [0, NUM(u'esc_t'), 0], (TAB_REAL, TAB_LIT)
assert (Q_LIT[1], Q_ALL[1]) == (NUM(u'esc_q'), 166) and CNT(u'Leap\\\\t', 2) == 0
assert (CNTF(TAB, 0), TAB_PER, CNT(u'(?m)^Leap\\\\t', 2)) == (NUM(u'tab_if'), 6, 0)

# ---------- 语义挪位不留词面痕迹 ----------
N_JUL, N_JUN30 = CNT(u'Jul', 0), CNT(u'(?m)^Leap\t\\d{4}\tJun\t30\t', 2)
assert (N_JUL, N_JUN30, CNT(u'Jun', 0)) == (11, NUM(u'jun30'), 0)
assert (CNT(u'June', 0), CNT(u'June', 1), CNT(u'June', 2), CNTF(u'June', 0)) == (0, 0, 0, 5)
assert (N_LEAP, CNT(u'Jun', 2), CNT(u'Dec', 2)) == (NUM(u'leap_rows'), NUM(u'jun30'), NUM(u'dec31'))
assert CNT(u'\t', 2) == 6 * N_LEAP and CNT(u'Jan', 2) == CNT(u'Jul', 2) == 0

# ---------- 生成器语句 × 执行次数 ----------
blk = full(1).split(u'BEGIN {')[1].split(NL + u'}')[0]
EMIT = [l for l in blk.split(NL) if l.strip().startswith(u'print "')]
HEADOK = 0
for k, l in enumerate(EMIT):
    s = l.strip()
    lit = s[s.index(u'"') + 1:s.rindex(u'"')]
    for a, b in ((BS + u'n', NL), (BS + u't', TAB), (BS + u'"', u'"'), (BS + BS, BS)):
        lit = lit.replace(a, b)
    if full(2).split(NL)[k] == lit:
        HEADOK += 1
assert (len(EMIT), HEADOK) == (NUM(u'bprint'), NUM(u'headok')) == (40, 40)
ENDL = NUM(u'lines')[2] - NUM(u'bprint') - N_LEAP
P_PRINT, P_PRINTF = u'(?m)^[ \t]*print[ \t"]', u'(?m)^[ \t]*printf[ \t"]'
N_PCT, N_MOD = CNT(u'%', 1), CNT(u'% ', 1)
PCTK = [CNT(u'%' + k, 1) for k in (u'd', u's', BS + u'.4d', BS + u'.2d')]
assert (ENDL, NUM(u'endlines')) == (19, 19)
assert (CNT(u'print ""', 1), NUM(u'blankhead') + NUM(u'endblank')) == (NUM(u'pempty'), 7)
assert (CNT(P_PRINT, 1), CNT(P_PRINTF, 1)) == (NUM(u'print_stmts'), NUM(u'printf_stmts')) == (56, 5)
assert (NUM(u'sign'), NUM(u'dead'), NUM(u'tail_copy')) == (2, 3, 2)
assert NUM(u'tail_blank') - NUM(u'endblank') == 1 and CNT(u'\\\\n', 1) == NUM(u'esc_n') == 6
assert (CNT(u'23:59:59', 2), CNT(u'(?m)^#Expires ', 2), CNT(u'(?m)^Expires ', 2)) == (0, 0, 0)
assert (CNTF(u'(?m)^#Expires ', 2), CNTF(u'23:59:59', 2)) == (NUM(u'expires_line'), 1)
assert (N_PCT, sum(PCTK), N_MOD) == (30, 26, 4)
assert PCTK == [NUM(u'pctd'), NUM(u'pcts'), NUM(u'pct4'), NUM(u'pct2')] == [4, 5, 3, 14]

# ---------- 历元与散文 horizon(与 audit 不同的两条路: datetime + 年均长) ----------
EPOCH, GAP, SHORT = NUM(u'epoch'), NUM(u'gap'), NUM(u'short')
DAY1900 = 109513
GAPF = u'%.2f' % (GAP / 86400.0)
LEAPDAY = len([y for y in range(1900, 1970) if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)])
assert (EPOCH, GAP, SHORT) == (3992312697 - 1783323897, 4023129600 - 3992312697, 365 * 86400 - GAP)
assert EPOCH == ((1970 - 1900) * 365 + LEAPDAY) * 86400 == 2208988800
assert GAPF == ST[u'gap_days'] == u'356.68'
assert CNT(u'%d' % DAY1900, 1) == 1 and CNT(u'ss_NTP = 109513', 1) == 1
Y10, Y53 = 1900 + (10 ** 10 // 86400) // 365.2425, 1900 + (2 ** 53 // 86400) // 365.2425
assert (int(Y10), int(Y53)) == (NUM(u'y10'), NUM(u'y53')) == (2216, 285428681)
assert (datetime.date(1900, 1, 1) + datetime.timedelta(days=10 ** 10 // 86400)).year == int(Y10)
assert (CNT(u'10\\*\\*10', 1), CNT(u'2\\*\\*53', 1)) == (0, 0)
assert (CNTF(u'10\\*\\*10', 1), CNTF(u'2\\*\\*53', 1)) == (2, 3)

SEC = u'''
## 25. What B48 taught (input ⇎ the program that generates it ⇎ the program's product: a causal chain you can re-run, 2026-10-20)

B48 = `corpus/babeltele/B48_input_program_and_its_output.md`, 3 raw sources from one tarball:
`leap-seconds.list` (%s 口径 chars ⇎ %d lines, %d of them header comments) ⇎ `leapseconds.awk` (%s chars,
%d print + %d printf statements) ⇎ `leapseconds` (%s chars, %d Leap rows). %d anchor slots / %d distinct
strings (%d/%d/%d touched per label I/A/L), %d judgement lines, %d DERIV keys whose `0` holds %d additive
terms (%d pure absences + %d equalities/差值 claims, %d CNT/CNTF primitive calls), retention %s (vs-raw %s:
the digest is longer than the combined 口径 of all three sources, %s ⇎ %s bytes on disk), %d unique
codepoints, 待核 = %d (the entry number itself), cross-source literal anchors = %d. Library now
**%d entries / %d machine-checked derivations** (enc %s ⇎ digest %s, %s unique codepoints,
corpus retention %s).

Seven durable methodology facts:

- **Executing the transform is a checkability rung of its own.** When a generator ships next to its input and
  output, run it: `gawk -f leapseconds.awk leap-seconds.list` reproduces the product byte-for-byte
  (sha256 %s, re-asserted here a third time — build, fill and README each replayed it). That turns "who
  generates whom" from a reader's reconstruction into a tool-side fact, strictly stronger than any count.
  Name the engine in the note (`%s`), since the claim is only reproducible on it.
- **A generator's account is statements × executions, not lines.** BEGIN holds %d `print` statements and the
  product's first %d lines equal their unescaped literals *in emission order* (%d/%d verified); a single
  `printf "Leap⇥…"` statement runs %d times, one short of the input's %d data rows (its first row is the
  epoch anchor, not a leap record); END's share is %d lines of which %d are blank, and %d of those blanks
  comes from a `printf` carrying its own newline rather than from a `print ""` — so blank lines must be
  attributed to a statement, not merely counted. %d dead-branch `print`s emit nothing at all: **absence in
  the output is not incapacity in the program**, and that asymmetry earns its own judgement line.
- **The escape layer must be named on both sides of every ⇎, and it flips.** The awk 口径 holds %d literal
  backslash-t pairs ⇎ the product holds %d real tabs (= %d per row × %d rows) and %d literal ones; the input
  carries %d real tabs across its whole file but %d inside the 口径. Likewise %d literal backslash-quote ⇎
  %d real quotes. In an `audit.py`-style regex a single backslash matches a REAL tab (%d in the awk 口径)
  while a doubled one matches the literal text (%d) — a rebuild was burned on that pair. A number means
  nothing until its layer is stated; the layers are disjoint here, so both go into the 0-key as terms.
- **Semantic work can leave zero literal trace.** The generator moves every leap instant from "1 Jul"/"1 Jan"
  to the last second of the preceding month: %d `Jul` in the input ⇎ %d `Jun 30` rows in the product, while
  the word `June` appears %d times in each of the three 口径 (and %d times in the input's *dropped*
  comments), and `Jan`/`Jul` appear %d times on the product's data side. Substring search cannot see the
  move; only calendar replay can (%d/%d rows rebuilt from the input's NTP seconds match the product's four
  fields; month shifted %d, year shifted %d = exactly the %d `Dec 31` rows, day shifted %d). Report "no
  word-form trace" as a finding, not as a failed count.
- **Epoch arithmetic cross-checks stamps that never sit in the same file.** Both stamp pairs differ by the
  same %s seconds (1900-01-01 vs 1970-01-01 = ((1970−1900)×365+%d)×86400, where %d is the century's leap-day
  count — the term a naive year product omits); assert the equality on *both* pairs. The updated/expires
  interval is %s s = %s days, %s s short of a 365-day year, which is why it reads "almost 365". The
  generator's prose horizon (year %d after 10**10, %s after 2**53) recomputes from its own day-epoch
  constant %d via `1900 + N/86400/365.2425`, and an independent `datetime` walk lands in %d too — yet both
  numbers live only in dropped comments (口径 %d ⇎ whole-file %d/%d), so they can only be DERIV keys, never
  anchors.
- **Coincidental equal values must not share one proof key.** %d is the awk file's dropped-line count *and*,
  unrelatedly, its print+printf statement total (%d+%d): one value, two different proofs, two keys. The %d
  `%%` signs of the awk 口径 split as %d format specifiers (%d of `%%d`, %d of `%%s`, %d of `%%.4d`, %d of
  `%%.2d`) plus %d modulo uses, and only the specifier counts get keys. The value %d is kept out of the
  prose because it is simultaneously the century leap-day term above and the corpus-wide 待核 tally. Three
  pure-ASCII sources make chars == bytes == full length (%s ⇎ %s ⇎ %s per source), which retires the
  口径-vs-disk caveat B45–B47 had to carry.
- **Small materials cap the ratio, not the writing.** vs-raw density %s is what a 3-source entry over
  %s/%s/%s 口径 chars must look like; the honest reading is "%d DERIV keys support %d judgement lines".
  Do not narrow the window to buy a metric — record all three 口径 lengths in the note and say why the
  retention is high.

**How to apply:** when a `raw/` directory holds a program together with an input and a file that looks like
its output, prefer that triple over any two-file diff — (1) run the program into a temp file and compare
sha256 *before* writing a single judgement; (2) inventory its `print`/`printf` statements by block (BEGIN /
main / END), then map block→line-count and statement→execution-count onto the product, blanks and dead
branches included; (3) count escape-layer literals with doubled backslashes and real control characters
separately; (4) for every "the program does X to the data" claim, ask whether X has any word-form on the
output side, and if not, prove it by recomputation; (5) keep tool-side facts (bytes, sha, engine version,
dropped lines) in `src:`/⛓解读注, never as unexplained body numbers. Housekeeping still open: the duplicate
`raw/probe/bio_recent.json` (byte-identical to the api copy) awaits the user's delete confirmation. Remaining
candidates: `cot/prompts/*` (instruction ⇎ produced reasoning), `tz/zonenow.tab` + `iso3166.tab` (a table ⇎
the same keys re-sorted), the `probe/` HTML⇎XML pairs (`_f_2026-*.htm`, `fr_2026-21376.xml`),
`langsubtag.txt`, the fips202 pdf ⇎ txt ⇎ html trio, and `codata_table.html` ⇎ `codata_all.html`.
''' % (COM(RCOT(0)), NUM(u'lines')[0], NUM(u'dropped')[0], COM(RCOT(1)), NUM(u'print_stmts'),
       NUM(u'printf_stmts'), COM(RCOT(2)), N_LEAP,
       NUM(u'anchors'), NUM(u'uniq_anchor'), NUM(u'anchor_i'), NUM(u'anchor_a'), NUM(u'anchor_l'),
       NUM(u'gloss_lines'), NUM(u'deriv_keys'), NUM(u'n_terms0'), NUM(u'n_absent'), NUM(u'n_equ'),
       NUM(u'n_prim0'), b48[2], b48[3], COM(NUM(u'rcot_sum')), COM(NUM(u'bytes_sum')),
       NUM(u'uniq_cp'), NUM(u'soft_b48'), NUM(u'cross_atoms'),
       NENT, proofs, COM(enc_all), COM(dig_all), COM(uniq_all), allc[2],
       cut(ST[u'repro_sha'], 16), ST[u'gawk'].split(u',')[0],
       NUM(u'bprint'), NUM(u'bprint'), NUM(u'headok'), NUM(u'bprint'), N_LEAP, NUM(u'data_rows'),
       ENDL, NUM(u'tail_blank'), NUM(u'tail_blank') - NUM(u'endblank'), NUM(u'dead'),
       TAB_LIT[1], CNT(u'\t', 2), TAB_PER, N_LEAP, TAB_LIT[2], CNTF(TAB, 0), TAB_REAL[0],
       NUM(u'esc_q'), Q_ALL[1], TAB_REAL[1], TAB_LIT[1],
       N_JUL, N_JUN30, CNT(u'June', 0), CNTF(u'June', 0), CNT(u'Jan', 2),
       NUM(u'rows_ok'), N_LEAP, NUM(u'mshift'), NUM(u'yshift'), NUM(u'dec31'), NUM(u'dshift'),
       COM(EPOCH), LEAPDAY, LEAPDAY, COM(GAP), GAPF, COM(SHORT), int(Y10), COM(int(Y53)), DAY1900,
       int(Y10), CNT(u'10\\*\\*10', 1), CNTF(u'10\\*\\*10', 1), CNTF(u'2\\*\\*53', 1),
       NUM(u'dropped')[1], NUM(u'print_stmts'), NUM(u'printf_stmts'),
       N_PCT, sum(PCTK), PCTK[0], PCTK[1], PCTK[2], PCTK[3], N_MOD, LEAPDAY,
       COM(FULLN[0]), COM(FULLN[1]), COM(FULLN[2]),
       b48[3], COM(RCOT(0)), COM(RCOT(1)), COM(RCOT(2)), NUM(u'deriv_keys'), NUM(u'gloss_lines'))

t = io.open(FILE, encoding='utf-8').read()
assert u'## 25.' not in t, u'B48 一节已存在'
io.open(FILE, 'w', encoding='utf-8').write(t.rstrip() + u'\n' + SEC)

idx = io.open(IDX, encoding='utf-8').read()
new_line = (u'- [Corpus selection & proof rule](corpus-selection-and-proof-rule.md) — v2: compress reasoning '
            u'not lookups; %d 条 PASS (%d DERIV 条); 首选可执行复现的三元组(输入⇎程序⇎产物, sha 全等); '
            u'生成器按 语句×次数 记账(空行归属、死支); 转义层必须点名(真制表符 ⇎ 字面反斜杠 t); '
            u'语义挪位可零词面痕迹⇒只能复算; 巧合相等的数值不许共用一个键; 断言排序/最大之前先测量'
            % (NENT, proofs))
idx2 = re.sub(u'^- \\[Corpus selection & proof rule\\].*$', new_line, idx, count=1, flags=re.M)
assert idx2 != idx, u'索引行未替换'
io.open(IDX, 'w', encoding='utf-8').write(idx2)

print(u'memory 追加 §25 完成: %d 条 / %d 推导 / 待核提示 %d｜索引行长度 %d' % (NENT, proofs, NHINT, len(new_line)))
print(u'B48: enc %s dig %s ret %s dens %s uniq %d blocks %s cpu %s｜锚 %d(%d 串, I/A/L %d/%d/%d) 判词 %d｜'
      u'DERIV %d 键, 0 键 %d 项(缺席 %d + 等式 %d, 原语 %d 次)'
      % (b48[1], COM(NUM(u'digest')), b48[2], b48[3], NUM(u'uniq_cp'), b48[5], b48[6],
         NUM(u'anchors'), NUM(u'uniq_anchor'), NUM(u'anchor_i'), NUM(u'anchor_a'), NUM(u'anchor_l'),
         NUM(u'gloss_lines'), NUM(u'deriv_keys'), NUM(u'n_terms0'), NUM(u'n_absent'), NUM(u'n_equ'),
         NUM(u'n_prim0')))
print(u'执行复现(第 3 次) %s == 产物 sha｜引擎 %s｜转义层: 真制表符 %d/%d/%d ⇎ 字面 %d/%d/%d｜引号 %d ⇎ 字面 %d'
      % (cut(RB, 12), ST[u'gawk'].split(u',')[0], TAB_REAL[0], TAB_REAL[1], TAB_REAL[2],
         TAB_LIT[0], TAB_LIT[1], TAB_LIT[2], Q_ALL[1], Q_LIT[1]))
print(u'纪元 %s 间隔 %s=%s 天 短 %s｜horizon %d/%d（awk 自带日纪元 %d）｜百分号分层 %d=%d+%d'
      % (COM(EPOCH), COM(GAP), GAPF, COM(SHORT), int(Y10), int(Y53), DAY1900, N_PCT, sum(PCTK), N_MOD))
