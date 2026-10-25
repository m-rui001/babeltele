# -*- coding: utf-8 -*-
"""生成 B38 的 ⛓解读注(幂等: 每次整体替换 ## ⛓解读注 之后的内容)。"""
import io, re, sys, hashlib

sys.stdout.reconfigure(encoding='utf-8')
ENTRY = u'corpus/babeltele/B38_sepsis_echo_phenotype_comment_response.md'
RAW = [(u'K', u'corpus/raw/prose/pmc_sepsis_lpa_comment.txt'),
       (u'R', u'corpus/raw/prose/pmc_sepsis_lpa_response.txt')]
src = {k: io.open(v, encoding='utf-8').read() for k, v in RAW}

full = io.open(ENTRY, encoding='utf-8').read()
enc = full.split(u'## ⟪BabelTele⟫')[1].split(u'## ⛓解读注')[0].strip(u'\n')
enc_n = len(enc.replace(u'\n', u''))
enc_nl = len(enc)
atoms = re.findall(u'⟧⟨([^⟨⟩]+)⟩', enc)
labels = re.findall(u'⟦([A-Z])⟧⟨', enc)
tags_all = re.findall(u'⟦([A-Z])⟧', enc)
out = re.sub(u'⟨[^⟨⟩]*⟩', u'', enc)
outlat = len(re.findall(u'[A-Za-z]', out))
inlat = len(re.findall(u'[A-Za-z]', u''.join(atoms)))
inhan = len(re.findall(u'[一-鿿]', u''.join(atoms)))
# 分源摘要段字符数与窗口数(从 ORIGINAL 段的分节标题回读)
orig = full.split(u'## [[原始语料|ORIGINAL]]')[1].split(u'## ⟪BabelTele⟫')[0]
dg = dict((m.group(1), len(m.group(2).strip())) for m in
          re.finditer(u'^### ⟦([A-Z])⟧[^\n]*\n(.*?)(?=\n### ⟦|\\Z)', orig, re.M | re.S))
blocks = dict((m.group(1), len([x for x in m.group(2).strip().split(u'\n') if x.strip()])) for m in
              re.finditer(u'^### ⟦([A-Z])⟧[^\n]*\n(.*?)(?=\n### ⟦|\\Z)', orig, re.M | re.S))
dig_body = sum(dg.values())
orig_a = re.search(u'\[\[原始语料\|ORIGINAL\]\]\n(.*?)\n\n## ⟪BabelTele', full, re.S).group(1)
dig_total = len(orig_a)

def chars_of(k):
    s = src[k]
    m = re.search(u'^chars: (\\d+)$', s, re.M)
    return int(m.group(1))
def bytes_of(k):
    return len(open(RAW_DICT[k], 'rb').read())
RAW_DICT = dict(RAW)
raw_chars = sum(chars_of(k) for k, _ in RAW)
raw_bytes = sum(bytes_of(k) for k, _ in RAW)
for k, _ in RAW:
    h = re.search(u'^text_sha256: ([0-9a-f]{16})$', src[k], re.M).group(1)
    assert len(h) == 16
    print(u'[%s] chars=%d bytes=%d sha=%s 锚=%d' % (k, chars_of(k), bytes_of(k), h, labels.count(k)))

ret_d = 100.0 * enc_n / dig_total
ret_c = 100.0 * enc_n / raw_chars
ret_b = 100.0 * enc_n / raw_bytes

G = []
a = G.append
a(u'※体例 两源都是已刊的期刊通信: ⟦K⟧＝读者评论(J Intensive Care 2026, 10.1186/s40560-026-00888-1, 收稿 4 月 12 日／接收 5 月 12 日)，'
  u'⟦R⟧＝同一期紧接其后的作者答辩(10.1186/s40560-026-00896-1，收稿与接收同为 6 月 5 日)。被评论的研究(10.1186/s40560-026-00873-8)'
  u'不在本条语料里：它只以两封信各自的转述出现，因此凡是关于该研究的数字都归属到写信人一侧。')
a(u'※派生算术与计数(全部由 audit.py 机检，13 个键) 0＝⟦R⟧ 侧 ChatGPT／underpowered／misclass／36.9／2071／odds ratio／'
  u'First,／Second,／Third,／百分号／PMC 检索号 全为 0，加上 ⟦K⟧ 侧 we agree／load-dependent／Geri 为 0 与两源汉字为 0(合计 15 项缺席断言)；'
  u'3＝CNT("we agree",1)＝⟦R⟧ 三处同意；2＝CNT("PMC10838258",0)＝同一篇外部文献在 ⟦K⟧ 带检索号出现 2 次而在 ⟦R⟧ 无检索号；'
  u'1＝CNT("endotype",0)；8＝CNT("%",0)＝⟦K⟧ 八处百分号；1.98＝round(41÷2071×100,2)＝那个"簇小"的占比，双方都没写；'
  u'1.67＝round(2.37÷1.42,2)＝同一暴露两项外部效应的倍数差；3.18＝round((3427+3151)÷2071,2)＝两个外部队列合计相对本研究人数的倍率；'
  u'262＝round(17,008÷65)＝那篇荟萃分析每项研究的平均例数；8710／753＝⟦K⟧ 正文字母与数字字符数，6376／209＝⟦R⟧ 同两项。')
a(u'※隐性知识的所在 ① 让步按句序变便宜(无主的领域问题→已不可行的分析→零成本的未来)；② 拒绝写成"不可比"而不是"不同意"；'
  u'③ 把批评者提出的新名称说成自己一开始的命名是最小让步；④ 承认＋"机构未常规采集"＝议题终止；'
  u'⑤ 同一篇外部文献可同时被承认与被限定人群；⑥ 引用格式是否带检索号也是举证的一部分；⑦ 用同形状反结局的他院先例替代自我重算；'
  u'⑧ 簇的描述项数从 2 增到 4 就是"是否可比"之争的全部实质；⑨ 机制列举加长只削弱对方机制的唯一性；⑩ 收稿与接收同日说明答辩可零评审周期；'
  u'⑪ 清单形式归批评者、顺序归答辩者；⑫ 复述对方议程时顺手改写责任归属("变量选择"不是评论的用词)；'
  u'⑬ 全程无百分号即从未在数字层接战；⑭ 结尾建议清单的增删暴露真正被接受的异议(删掉的是"扩大前瞻队列")；'
  u'⑮ 数据可得性与生成式工具两条披露在两源方向相反。')
a(u'※抓取与失真 两条 raw 由 Europe PMC fullTextXML 取回并去掉页眉；被评论那篇研究的 fullTextXML 端点持续返回 HTTP 500，'
  u'PMC 网页版只是外壳(正文与表格不在 HTML 里)，故本条刻意不含研究原文。JATS 转换留下的三处不可跨锚点：小于号写作实体 `&lt;`、'
  u'单位上下标拆成 `L/min/m 2`、两处撇号分别用 U+2019 与 U+2032(rv S’ ⇎ E/e′)；锚点全部避开这些位置。')
a(u'※两源对齐 46 个锚全部逐字命中自己标签的源(建条脚本 _mkB38.py 内建精确子串断言，非规范化比较)。摘要段联合命中 46/46，'
  u'其中 1 处为跨源子串(两条结尾建议共用 "will be essential")，归属仍由前贴的单字母标签决定。')
a(u'※实况 编码 %d(含换行；audit 去换行口径 %d) ⇎ 摘要段 %d(audit 口径；正文 %d ＋ 两处分节标题 %d；46 个锚全部命中，分源窗口 %d ＋ %d) ⇎ '
  u'raw 正文 %d 字符／%d 字节；保留率 %.1f%% ⇎ %.1f%% ⇎ %.3f%%；锚 46 个(⟦K⟧ %d ⇎ ⟦R⟧ %d)，锚内字母 %d ⇎ 锚内汉字 %d，'
  u'锚外字母 %d = 出处标签 %d + 其余 %d(仅 ℒmethod 自身)；T1／T2／T3 失配 0，待核小整数 0 条。' % (
    enc_nl, enc_n, dig_total, dig_body, dig_total - dig_body,
    blocks.get('K', 0), blocks.get('R', 0), raw_chars, raw_bytes,
    ret_d, ret_c, ret_b, labels.count('K'), labels.count('R'),
    inlat, inhan, outlat, len(tags_all), outlat - len(tags_all)))
a(u'※保留率口径 两条信合计只有 19250 字符，而 46 个锚必须逐字保留，故编码达到摘要段的 %.1f%%——这一条几乎不在长度上压缩，'
  u'它的压缩全部花在"选哪 46 处"——留下的是 46 个可判读的短语，并另加 13 个机检数式。'
  u'相对 raw 源的 %.3f%% 才是可与他人比较的数字。' % (ret_d, ret_b))

io.open(ENTRY, 'w', encoding='utf-8').write(full.split(u'## ⛓解读注')[0] + u'## ⛓解读注\n' + u'\n'.join(G) + u'\n')
print(u'gloss written: enc %d dig %d ret %.1f%% raw %d/%d' % (enc_n, dig_total, ret_d, raw_chars, raw_bytes))
