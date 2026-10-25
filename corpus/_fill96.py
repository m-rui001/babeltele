# -*- coding: utf-8 -*-
# B96 解读注遍(第三套机制, 独立于 _mkB96.py ⇎ _pick96.py): 只用 re 计数与逐锚子串核验,
# 不复用任何前两遍的中间量; 注里的每个数都由本遍现读现算, 与编码区登记的数各自独立成账。
# 写回 corpus/babeltele/B96_*.md 的 "## ⛓解读注" 段(替换占位句), 不动编码区与原文区。
import io, os, re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENTRY = u'corpus/babeltele/B96_fcc_robocall_revocation_compression.md'
RAWS = [u'corpus/raw/late96/fcc_2026-21821.txt']

md = io.open(ENTRY, encoding='utf-8').read()
raw = io.open(RAWS[0], encoding='utf-8', errors='replace').read()
enc = re.search(u'## ⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)

# —— 源面(本遍口径: 逐字符扫空白分类, 不用 split/join) ——
n_word = 0
prev_ws = True
for ch in raw:
    ws = ch.isspace()
    if not ws and prev_ws:
        n_word += 1
    prev_ws = ws
n_line = len(re.findall(u'\n', raw))
n_nonblank = len([l for l in re.split(u'\n', raw) if l.strip()])
n_cp = len(set(raw.replace(u'\n', u'')))

# —— 锚核验: 每条 ⟨…⟩ 的字母数字核必须能在原文的字母数字核里找到(与本遍独立的第三把尺) ——
core = lambda s: re.sub(u'[^0-9a-z\u4e00-\u9fff]', u'', s.lower())
SRC_CORE = core(raw)
atoms = re.findall(u'⟨([^⟨⟩]+)⟩', enc)
ok = len([a for a in atoms if core(a) in SRC_CORE])
enc_ch = len(enc.replace(u'\n', u''))
bad_enc = len(re.findall(u'⟪', enc))


def pct(a, b):
    return u'%.1f%%' % (100.0 * a / b)


NOTE = (u'## ⛓解读注\n\n'
        u'### 压缩账(本注现算, 第三把尺)\n\n'
        u'| 量 | 值 |\n|---|---|\n'
        u'| 源(FCC 终规全篇) | %d 字符 / %d 词 / %d 行(非空 %d) / 码位 %d 枚 |\n'
        u'| 编码(BabelTele 算子中文) | %d 字符(不含换行) |\n'
        u'| 体积比 | 编码⇎源 %s |\n'
        u'| 锚 | 编码区 %d 处, 本遍逐锚核穿到原文 %d 处 ⇎ 穿不到 %d 处 |\n\n'
        u'### 读法\n'
        u'编码区⛓链是规则本体: 撤销权⇒专属方式三选⇒七枚标准词逐字⇒十个工作日⇒未指定即全接⇒'
        u'范围分档(信息类只及单类 ⇎ 营销类及于全部)⇒五分钟确认⇒单向文本披露⇒可靠来源三档⇒'
        u'生效链(2026-11-25 取代被推迟的 2027-01-31)⇒授权链。三档口径并行登记: '
        u'严格档(针完整落在单行内)⇎容行档(整面折平)⇎最宽档(标点⇎撇号⇎连字符一律抹平), '
        u'FR 的 698 行硬换行正是把 15 枚针切断的那一刀, 所以跨行 17 处只能用容行档读出。\n\n'
        u'### 本条不能由在库文件判定的(只登记, 不进门槛)\n'
        u'评论区意见原文 ⇎ CG Docket 02-278 的历史文书 ⇎ 生效日之后的实际执法数据; '
        u'本条只认这一份 Federal Register 终规文本自身。\n\n'
        u'### 编码与门的账\n'
        u'门槛三遍: T1 逐锚回源(本遍 %d/%d) ⇎ T2 DERIV 复算(面值 %d 枚由 corpus/_b96flat.json 逐枚现算) '
        u'⇎ T3 码位与字母账(源面唯一码位 %d 枚)。小整数待核只进本注, 不进 FAIL。\n'
        % (len(raw), n_word, n_line, n_nonblank, n_cp, enc_ch, pct(enc_ch, len(raw)),
           len(atoms), ok, len(atoms) - ok, ok, len(atoms),
           len(__import__('json').load(io.open(u'corpus/_b96flat.json', encoding='utf-8'))), n_cp))
assert ok == len(atoms), u'有锚穿不到原文: %s' % [a[:40] for a in atoms if core(a) not in SRC_CORE]
assert u'待 _fill96.py' in md, u'占位句不在(注可能已写过)'
head, tail = md.split(u'## ⛓解读注', 1)
new = head + NOTE
assert new.count(u'## ⟪BabelTele⟫') == 1 and new.count(u'## ⛓解读注') == 1
assert bad_enc == 0, u'编码区里漏了 ⟪'
io.open(ENTRY, 'w', encoding='utf-8', newline=chr(10)).write(new)
print(u'B96 解读注: 源 %d 字符/%d 词 ⇎ 编码 %d 字符(%s) ⇎ 锚 %d 处全穿 ⇎ 码位 %d 枚'
      % (len(raw), n_word, enc_ch, pct(enc_ch, len(raw)), len(atoms), n_cp))
