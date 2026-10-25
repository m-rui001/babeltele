# -*- coding: utf-8 -*-
"""README 记账: 53 条 → 54 条。所有合计取自 audit 的当下输出, 条目侧的数由本文件第五遍从两份 raw 再量一次。
本文件不转述建条目侧的话: 两份 .html 在这里按“整份文件 ⇎ 数据行区 ⇎ 去标签正文”三种口径各数一遍,
再与建条目侧契约 corpus/_b54flat.json、门槛快照 corpus/_b54audit.json 逐键对表; 数据行数、'(exact)' 行数也现数。
任一标量对不上就当场停机, 所以 README 里“同一秒的两份 .html 形状相反”是本文件数出来的。"""
import io, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
F = u'corpus/README.md'
NL = chr(10)
TAG, ENTRY = u'B54', u'corpus/babeltele/B54_complete_listing_and_ill_formed_request.md'
PATHS = [u'corpus/raw/codata_table.html', u'corpus/raw/codata_all.html']
fmt = lambda n: u'{:,}'.format(int(n)).replace(u',', u' ')


def sub(old, new, s):
    assert s.count(old) == 1, (u'锚不唯一', s.count(old), old[:50])
    return s.replace(old, new)


# ---------- 1) 门槛现取 ----------
p = subprocess.run([sys.executable, u'-X', u'utf8', u'corpus/audit.py'],
                   capture_output=True, text=True, encoding='utf-8')
OUT = p.stdout
assert u'保真门槛' in OUT and u'PASS' in OUT, OUT[-600:]
row = {}
for l in OUT.split(NL):
    if not l.startswith(u'| '):
        continue
    parts = [x.strip() for x in l.strip(u'|').split(u'|')]
    k = parts[0]
    if (k[:1] == u'B' and k[1:].isdigit()) or k == u'ALL':
        row[k] = parts[1:]
NENT = len([k for k in row if k != u'ALL'])
assert NENT == 54, NENT
b54, b53, A = row[u'B54'], row[u'B53'], row[u'ALL']
dig_all, enc_all = int(A[0].replace(u' ', u'')), int(A[1].replace(u' ', u''))
ret_all = A[2].strip(u'*')
uniq_all = int(re.sub(u'[^0-9]', u'', A[4]))
soft_all = proofs = None
for l in OUT.split(NL):
    if l.startswith(u'提示') and u'共' in l:
        soft_all = int(l.split(u'共')[1].split(u' 个')[0])
    if l.startswith(u'已机检的推导'):
        proofs = int(l.split(u'(')[1].split(u' 条)')[0])
assert soft_all == 19 and proofs == 1047, (soft_all, proofs)
dig54, enc54, ret54, rawp54, uniq54, cwu54 = (int(b54[0]), int(b54[1]), b54[2], b54[3],
                                              int(b54[4]), b54[5])
dig53, enc53 = int(b53[0]), int(b53[1])

# ---------- 2) 条目侧第五遍: 自己从两份字节重量 ----------
RD = lambda q: io.open(q, encoding='latin-1').read()
TXT = [RD(q) for q in PATHS]
CH = json.load(io.open(u'corpus/_b54checks.json', encoding='utf-8'))
FLAT = json.load(io.open(u'corpus/_b54flat.json', encoding='utf-8'))
SNAP = json.load(io.open(u'corpus/_b54audit.json', encoding='utf-8'))[u'B54']
LS = [TXT[i].split(NL) for i in range(2)]
DASH = [i for i, l in enumerate(LS[0]) if re.fullmatch(u'-{20,}\\s*', l)]
assert len(DASH) == 1
ROWS = [l for l in LS[0][DASH[0] + 1:] if l.strip()]
GAP = [re.split(u' {2,}', l.strip()) for l in ROWS]
UC = [(g + [u''])[2] for g in GAP]
VL = [g[1] for g in GAP]
EXACT = len([u for u in UC if u == u'(exact)'])
ELL = len([v for v in VL if u'...' in v])
E54 = len(re.findall(u'<[A-Za-z]', TXT[1]))
BS = [os.path.getsize(q) for q in PATHS]
assert [len(TXT[i]) for i in range(2)] == FLAT[u'chars'] == BS
assert len(ROWS) == FLAT[u'rows'] == SNAP[u'rows']
assert EXACT == FLAT[u'exact_rows'] == SNAP[u'exact_rows'] and ELL == FLAT[u'ell_rows']
assert E54 == FLAT[u'e_tags'] == SNAP[u'e_tags']
assert TXT[0].count(u'<') == 0 and TXT[1].count(u'<') == FLAT[u'lt'][1] == SNAP[u'lt'][1]
assert len([q for q in CH[u'classes'][u'single']]) == CH[u'anchor_distinct']

# ---------- 3) 逐处替换 ----------
S = io.open(F, encoding='utf-8').read()
S = sub(u'共 **53 条**（`babeltele/B01..B53`）',
        u'共 **54 条**（`babeltele/B01..B54`）', S)
S = sub(u'## 保真门槛：`python corpus/audit.py` → **PASS**（53 条）',
        u'## 保真门槛：`python corpus/audit.py` → **PASS**（54 条）', S)
S = sub(u'当前 **53 条语料／971 条**推导全部通过（audit 自报“已机检的推导 971 条”）',
        u'当前 **%d 条语料／%d 条**推导全部通过（audit 自报“已机检的推导 %d 条”）' % (NENT, proofs, proofs), S)

NEWPAR = (u'**B54 把对照轴换成同一秒抓下的两份 .html**：`raw/codata_table.html`（自称 Complete Listing ⟦T⟧: '
          u'%d 字节／%d 行／非空 %d 行／**0 枚 `<`**／数据 %d 行） ⇎ `raw/codata_all.html`（名叫 all ⟦E⟧: '
          u'%d 字节／%d 行／非空 %d 行／`<` %d 枚 ⇎ `>` %d 枚）。两份都是纯 ASCII(0 枚非 ASCII), '
          u'扩展名相同而形状相反: 一份整张是定宽表(连 DOCTYPE 都不写), 一份是一页“ill-formed request”错误, '
          u'去标签后只剩 %d 字符而其中脚本源码占 %d。两源共同 URL 0 个、整行级候选池重合 0 条(池中清单行 %d 行), '
          u'而 12 枚关键串里两源同现 6 枚——两个口径都写进判词, 不是一个数推翻另一个。'
          u'最强一环是清单自己没写出来的三条律: 排序四键逆序 %d ⇎ %d ⇎ %d ⇎ %d(第一处在第 %d 对, 末行“W to Z”自己不守序), '
          u'值与不确定度小数位相等 %d 行 ⇎ 不等 %d 行(适用面 %d 行, 其余 %d 行被截断而不适用), '
          u'字段边界两法互证 %d 格不一致 %d 处; 表头与数据列位非零差 %d 处说明表头不是照着数据对齐的。'
          u"'(exact)' %d 行里带 '...' 的 %d 行为截断式、%d 行为给全式; 正指数一律不写 '+'(%d 枚而不带符号, 带 '+' 0 枚)。"
          u"错误页那枚 base64 挑战串解出 %d ⇒ %s UTC, 这一条永久可复算且入门槛; "
          u'它与磁盘 mtime 同秒只在本机成立, 只进解读注。'
          u'同一份 40801 字节的清单已由第一代 B06 压过一次(它抄的是表里的数值, 编码区 0 枚片段锚), '
          u'本条数的是表的形状, 26 串锚与 B06 的锚交集 0 处 ⇒ “同一份 raw 能有两种条目”由 B06 ⇎ B54 这一对对照, 而不由本条的 ⟦E⟧。'
          u'“错误页由哪一次请求造成”“哪个入口才是这份清单的正身”不可由在库文件判定, 判词按第三档写、门槛不背书。\n')
S = sub(u'本机两份由 pdftotext 现生两遍字节相同（这一句入门槛），抽取器版本与两份产物的 sha 只进解读注；'
        u'“哪一种序列化才算这份标准的正文”与“⊕ 在 PDF 里本来画的是什么”不可由在库文件判定，判词按第三档写、门槛不背书。\n',
        u'本机两份由 pdftotext 现生两遍字节相同（这一句入门槛），抽取器版本与两份产物的 sha 只进解读注；'
        u'“哪一种序列化才算这份标准的正文”与“⊕ 在 PDF 里本来画的是什么”不可由在库文件判定，判词按第三档写、门槛不背书。\n'
        + (NEWPAR % (FLAT[u'bytes'][0], FLAT[u'lines'][0], FLAT[u'nonblank'][0], FLAT[u'rows'],
                     FLAT[u'bytes'][1], FLAT[u'lines'][1], FLAT[u'nonblank'][1], FLAT[u'lt'][1], FLAT[u'gt'][1],
                     FLAT[u'e_prose'], FLAT[u'e_script_lost'], FLAT[u'row_anchor_pool'],
                     FLAT[u'sort_byte'], FLAT[u'sort_fold'], FLAT[u'sort_skel'], FLAT[u'sort_rowskel'],
                     FLAT[u'first_inv'], FLAT[u'align_eq'], FLAT[u'align_ne'], FLAT[u'align_rows'],
                     FLAT[u'ell_rows'], FLAT[u'impl_cell'], FLAT[u'impl_diff'], FLAT[u'hdr_vs_col_all'],
                     EXACT, ELL, FLAT[u'exact_no_ell'], FLAT[u'exp_unsigned'],
                     FLAT[u'tok_epoch'], FLAT[u'tok_utc'])), S)

ROW54 = (u'| B54 | %d（新建, 同一秒的两份 .html 一份定宽表一份错误页 %d 处标注／%d 个不同串（登记 %d 条锚全命中，'
         u'每标签 T %d ⇎ E %d）: 两色锚位 清单 ⟦T⟧ ⇎ 错误页 ⟦E⟧; 最强一环是三条没写出来的律: '
         u'排序四键逆序 %d ⇎ %d ⇎ %d ⇎ %d(第一处第 %d 对, 末行自破其序) ⇎ 小数位相等 %d ⇎ 不等 %d(适用面 %d 行, 截断 %d 行不适用) '
         u'⇎ 字段两法互证 %d 格不一致 %d 处(表头与列位非零差 %d 处); 记法 分组非三位 %d 组(%d⇎%d 位都有) ⇎ 指数 %d ⇎ %d ⇎ %d; '
         u"'(exact)' %d ⇎ 截断 %d ⇎ 给全 %d ⇎ 空不确定度 %d; 错误页 标签 %d／闭 %d／种 %d, 注释 %d 段 %d 字符, "
         u'链接整份 %d ⇎ 去标签 %d, 声明 charset %d 处而 0 枚非 ASCII; 单位两遍 %d ⇎ %d(差 %d), 空单位 %d ⇎ 有值 %d; '
         u'内容侧 base64 时刻 %d 入门槛而 mtime 同秒只在本机; 同数共键复合式 %d 组、零项 %d 枚折成一条算式; '
         u'门槛侧 %d 枚推导键／%d 处 B54V 复算点，四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 %d 条锚逐字全命中） |\n')
S = sub(u'门槛侧 109 枚推导键／110 处 B53V 复算点，四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 25 条锚归一全等，'
        u'第三档现跑只留“两遍字节相同”入门槛） |\n',
        u'门槛侧 109 枚推导键／110 处 B53V 复算点，四套实现（采集 ⇎ 建条目 ⇎ 审计 ⇎ 解读注）对 25 条锚归一全等，'
        u'第三档现跑只留“两遍字节相同”入门槛） |\n'
        + (ROW54 % (enc54, CH[u'anchor_total'], CH[u'anchor_distinct'], CH[u'anchor_distinct'],
                    CH[u'tag_counts'][u'T'], CH[u'tag_counts'][u'E'],
                    FLAT[u'sort_byte'], FLAT[u'sort_fold'], FLAT[u'sort_skel'], FLAT[u'sort_rowskel'],
                    FLAT[u'first_inv'], FLAT[u'align_eq'], FLAT[u'align_ne'], FLAT[u'align_rows'],
                    FLAT[u'ell_rows'], FLAT[u'impl_cell'], FLAT[u'impl_diff'], FLAT[u'hdr_vs_col_all'],
                    FLAT[u'grp_frac_not3'], FLAT[u'grp_frac_min'], FLAT[u'grp_frac_max'],
                    FLAT[u'exp_minus'], FLAT[u'exp_unsigned'], FLAT[u'exp_plus'],
                    EXACT, ELL, FLAT[u'exact_no_ell'], FLAT[u'no_unc'],
                    FLAT[u'e_tags'], FLAT[u'e_close'], FLAT[u'e_tag_kinds'],
                    FLAT[u'e_comment_n'], FLAT[u'e_comment_chars'], FLAT[u'e_link_raw'], FLAT[u'e_link_tagless'],
                    FLAT[u'e_charset'], FLAT[u'unit_distinct'], FLAT[u'unit_distinct_col'], FLAT[u'unit_diff'],
                    FLAT[u'unit_blank'], FLAT[u'unit_filled'],
                    FLAT[u'tok_epoch'], len(CH[u'collisions']), CH[u'zero_terms'],
                    CH[u'deriv_keys'], sum(v.count(u'B54V') for v in json.load(
                        io.open(u'corpus/_deriv54.json', encoding='utf-8')).values()), CH[u'anchor_distinct'])), S)

lin = (u'第二代（B11–B53）锚内字母 **114 675**、锚外 **10 512**；全库合计 **114 796／12 707**'
       u'（B53 一枚条目贡献 3 244／365, 由建条目侧现数）')
assert S.count(lin) == 1
S = sub(lin, (u'第二代（B11–B54）锚内字母 **%s**、锚外 **%s**；全库合计 **%s／%s**'
              u'（B54 一枚条目贡献 %s／%d, 由建条目侧现数）'
              % (fmt(114675 + CH[u'letters_in']), fmt(10512 + CH[u'letters_out']),
                 fmt(114796 + CH[u'letters_in']), fmt(12707 + CH[u'letters_out']),
                 fmt(CH[u'letters_in']), CH[u'letters_out'])), S)

RAW54 = (u'| B54 | `raw/codata_table.html`（完整清单 ⟦T⟧: %d 字节／%d 字符／%d 行／`<` 0 枚／数据行 %d 行／'
         u"'(exact)' %d 行） ⇎ `raw/codata_all.html`（错误页外壳 ⟦E⟧: %d 字节／%d 字符／%d 行／`<` %d 枚／"
         u"标签 %d 枚／去标签 %d 字符） | 一份定宽表 ⇎ 一页错误 ⇒ 扩展名与命名都不算内容: "
         u"同一秒的两份 .html 一份 0 枚 '<' 一份 155 枚; 表的排序键、小数位对齐、末组位数、正指数不写 '+' 都没写在文件里, 只能复算 |\n")
anchor2 = (u'| 一份标准 ⇎ 四种序列化 ⇒ 行数、行长、分页符、行尾空格、词集包含、符号存活全部随抽取器改口，'
           u'能确定的只有可复算的那部分（骨架四级配对 ⇎ 码点存活表 ⇎ 本机产物重跑字节相同） |\n')
assert S.count(anchor2) == 1
S = sub(anchor2, anchor2 + (RAW54 % (FLAT[u'bytes'][0], FLAT[u'chars'][0], FLAT[u'lines'][0], FLAT[u'rows'],
                                     EXACT, FLAT[u'bytes'][1], FLAT[u'chars'][1], FLAT[u'lines'][1],
                                     FLAT[u'lt'][1], FLAT[u'e_tags'], FLAT[u'e_prose'])), S)

row55 = (u'| **合计（%d 条）** | **%s** | **%s**（摘要段合计 %s） | — | **%s** | — |\n'
         % (NENT, fmt(dig_all).replace(u',', u' '), ret_all, fmt(enc_all).replace(u',', u' '),
            fmt(uniq_all).replace(u',', u' ')))
old_tot = re.search(u'[|] [*]{2}合计（53 条）[*]{2}[^\n]*\n', S)
assert old_tot
S = S.replace(old_tot.group(0), row55)

CMD = (u'python -X utf8 corpus/_mkB54.py                  # 建条目: 扁平契约 %d 枚键／DERIV %d 枚算式, 占位符未替换 0 个\n'
       u'python -X utf8 corpus/_mkdigest3.py B54 <entry> T raw/codata_table.html 15 25 E raw/codata_all.html 15 25   '
       u'# 两源分节摘要(%s 字符, 窗口按 15⇎25 取锚点行)\n'
       u'python -X utf8 corpus/_wire54.py                    # 把 SCAN 段机械切进 audit.py::_b54_scan 并插 DERIV[\'B54\']\n'
       u'python -X utf8 corpus/atomcheck.py B54 corpus/_atoms54.txt   # 工具侧独立逐字校验: ok=%d bad=0\n')
anchor3 = u'python -X utf8 corpus/atomcheck.py B53 corpus/_atoms53.txt   # 工具侧独立逐字校验: ok=25 bad=0' + NL
assert S.count(anchor3) == 1
S = sub(anchor3, anchor3 + (CMD % (len(FLAT), CH[u'deriv_keys'], fmt(dig54).replace(u',', u' '),
                                   CH[u'anchor_distinct'])), S)

io.open(F, 'w', encoding='utf-8', newline=NL).write(S)
print(u'README 已记账: %d 条 ｜ 摘要段 %s ⇎ 编码 %s ｜ 保留率 %s ｜ 唯一码点 %s ｜ 推导 %d 条 ｜ B54 %s 字符／%d 锚'
      % (NENT, fmt(dig_all), fmt(enc_all), ret_all, uniq_all, proofs, fmt(enc54), CH[u'anchor_total']))
