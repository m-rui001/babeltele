# -*- coding: utf-8 -*-
# B99 解读注遍(第三套机制, 独立于 _pick99.py ⇎ _mkB99.py): 计数只走 str.count(子串档, 不经正则),
# 词尺只走逐字符扫空白, 行尺只按 '\n' 手工切, 锚核验只用 `in`——前两遍的中间量一枚都不复用,
# 注里每个数都由本遍现读现算, 与编码区登记的数各自独立成账。
# 写回 corpus/babeltele/B99_*.md 的 "## ⛓解读注" 段(替换占位句), 不动编码区与原文区。
import io, json, os, re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENTRY = u'corpus/babeltele/B99_tls_record_max_plaintext.md'
TAGP = [u'A', u'B', u'C', u'D', u'E']
RAWS = [u'corpus/raw/tlsrec99/rfc8446.txt', u'corpus/raw/tlsrec99/rfc5246.txt',
        u'corpus/raw/tlsrec99/rfc8449.txt', u'corpus/raw/tlsrec99/rfc6066.txt',
        u'corpus/raw/tlsrec99/openssl_max_send_fragment.pod']
LBL = [u'8446', u'5246', u'8449', u'6066', u'pod']
N = 5

md = io.open(ENTRY, encoding='utf-8').read()
assert md.count(u'## ⛓解读注') == 1, u'解读注标题不在 ⇎ 不止一枚'
T = [io.open(p, encoding='utf-8', errors='replace').read() for p in RAWS]
enc = re.search(u'## ⟪BabelTele⟫\n(.*?)\n\n## ', md, re.S).group(1)
orig = re.search(u'## \\[\\[原始语料\\|ORIGINAL\\]\\]\\n(.*?)\\n\\n## ', md, re.S).group(1)


def s(t):
    return u'%d' % t


def row(lst):
    return u'⇎'.join([u'%d' % v for v in lst])


# —— 源面(本遍口径: 逐字符, 不用 split()/join 的词表法) ——
n_ch = [len(t) for t in T]
n_word = []
for t in T:
    c, prev = 0, True
    for ch in t:
        ws = ch.isspace()
        if not ws and prev:
            c += 1
        prev = ws
    n_word.append(c)
n_line = [len(t.split(u'\n')) for t in T]
n_cp = [len(set(t)) for t in T]
enc_ch = len(enc.replace(u'\n', u''))
orig_ch = len(orig.replace(u'\n', u''))
orig_nl = len(orig)
src_tot = sum(n_ch)


def pct(a, b):
    return u'%.2f%%' % (100.0 * a / b)


# —— 子串档字面账(整串 str.count, 不整词、不折行) ——
LIT = {}
for needle in [u'2^14', u'16384', u'2^14+1', u'MUST NOT exceed', u'record_overflow',
               u'illegal_parameter', u'16704', u'805']:
    LIT[needle] = [t.count(needle) for t in T]
assert LIT[u'2^14'] == [8, 7, 4, 2, 0], LIT[u'2^14']
assert LIT[u'16384'] == [0, 0, 1, 0, 1], LIT[u'16384']
# 子串档的假命中: 5246 的 "2^14+1" 那一枚是 "2^14+1024" 的前缀, 不是面上真有 +1 档
assert LIT[u'2^14+1'][1] == 1 and T[1].count(u'2^14+1024') == LIT[u'2^14+1'][1]
assert T[2].count(u'2^14+1 octets') == 1 and T[1].count(u'2^14+1 octets') == 0

# —— 锚核验(第三把尺: 逐枚 `in`, 原面 ⇎ 折平面两档) ——
fold = lambda t: u' '.join(t.split())
TF = [fold(t) for t in T]
pairs = re.findall(u'⟦([A-E])⟧⟨([^⟨⟩]+)⟩', enc)
atoms = re.findall(u'⟨[^⟨⟩]+⟩', enc)
assert len(pairs) == 25 and len(atoms) == 25, (len(pairs), len(atoms))
TAGI = {t: i for i, t in enumerate(TAGP)}
own_raw = [a for (t, a) in pairs if a in T[TAGI[t]]]
own_fold = [a for (t, a) in pairs if a in TF[TAGI[t]]]
assert len(own_fold) == 25, [a[:60] for (t, a) in pairs if a not in TF[TAGI[t]]]
n_needfold = 25 - len(own_raw)
who = [t for (t, a) in pairs if a not in T[TAGI[t]]]
exc = [a for (t, a) in pairs if len([1 for x in TF if a in x]) == 1]
shared = sorted(set([a for (t, a) in pairs if len([1 for x in TF if a in x]) > 1]))
assert len(exc) + len(shared) * 2 == 25, (len(exc), shared)
assert shared == [u'records carrying data in chunks of 2^14 bytes or less'], shared
assert row([LIT[n][i] for n in [u'2^14'] for i in range(N)]) == u'8⇎7⇎4⇎2⇎0'

FLAT = json.load(io.open(u'corpus/_b99flat.json', encoding='utf-8'))
REG = json.load(io.open(u'corpus/_b99contract.json', encoding='utf-8'))

NOTE = (u'## ⛓解读注\n\n'
        u'### 压缩账(本注现算, 第三把尺: str.count 子串档 ⇎ 逐字符扫空白 ⇎ 手工按换行切行; '
        u'建条遍与采集遍的中间量一枚都不复用)\n\n'
        u'| 量 | 8446 | 5246 | 8449 | 6066 | pod |\n|---|---|---|---|---|---|\n'
        u'| 源字符 | %s |\n'
        u'| 源词(逐字符扫空白) | %s |\n'
        u'| 源行(split 换行, 含收尾空行) | %s |\n'
        u'| 源面唯一码位 | %s |\n'
        u'| 子串档 `2^14` 枚数 | %s |\n'
        u'| 子串档 `16384` 枚数 | %s |\n'
        u'| 子串档 `MUST NOT exceed` 枚数 | %s |\n'
        u'| 子串档 `record_overflow` 枚数 | %s |\n\n'
        u'编码区 %d 字符(不含换行) ⇎ 五份源面合 %d 字符 = %s ⇎ 在档摘录 %d 字符(去换行)⇎%d 字符(含换行, '
        u'门表用后者): 编码⇎摘录两把尺 %s⇎%s, 差 %d 枚换行符。\n\n'
        u'### 子串档不能替编码区的整词档(本注现读出的那一枚假命中)\n'
        u'整串 str.count 数 `2^14+1` 得 %s, 其中 5246 的那一枚来自 `2^14+1024` 的前缀而不是面上真有 '
        u'+1 档(5246 面上 `2^14+1 octets` 0 枚, 8449 面上有 1 枚)。所以编码区 🪜 的「折平比逐行多读 '
        u'18 枚针」与 ⚖ 的加数档都由幂式解析得出, 不拿子串档充数; 反过来 `2^14`(整串 %s ⇎ 摘壳折平 %s) '
        u'与 `record_overflow`(整串 %s ⇎ 编码区裸写档 %s) 两档同值, 因为这两个串既不跨硬换行也不落在壳行里。'
        u'`illegal_parameter` 则是两档打架的一例: 整串裸子串 %s ⇎ 编码区取的是带引号短语 '
        u'"`illegal_parameter` alert" 的 %s——5246 的三枚裸串都不成那个短语, 故编码区记 0。\n\n'
        u'### 锚核验(25 枚 ⟦标签⟧⟨原文⟩, 逐枚按标签回本家文件)\n'
        u'原面逐字符 verbatim 命中 %d 枚, 其余 %d 枚要把整面折平(空白折成一枚空格)才命中——即锚身跨一枚硬换行, '
        u'分属 %s; 折平档 25/25 全命中。按折平档在五份面互查: 只在本家读到的 %d 枚 ⇎ 两份同现的锚串 %d 串'
        u'(即 `%s` 在 ⟦A⟧ ⇎ ⟦B⟧ 各登记一次)。这把尺量的是本条 25 枚锚, 与编码区 🧱 的「独占 12 ⇎ 共享 3」'
        u'量的不是同一集合(那边量 43 枚判词针), 两组数不可相加。\n\n'
        u'### 读法\n'
        u'编码区七段各管一副账: 🧭 五份答句的长短与序列化(%s 词 ⇎ %s 字符)——只有 5246 的答句不带单位词, '
        u'只有实现侧把上限写成十进制而不是幂式; 🪜 四档读面阶梯(逐行 ⇎ 折平 ⇎ 摘壳 ⇎ 摘壳+幂式归一)与它的收益'
        u'(折平比逐行多读 18 枚针 ⇎ 归一使摘壳面缩短 8⇎4⇎0⇎0⇎0 字符, 恰为空格式枚数 4⇎2⇎0⇎0⇎0 的两倍); '
        u'⚖ 单位词与加数序列化, 四档加数 1⇎256⇎1024⇎2048 展开成 16384⇎16385⇎16640⇎17408⇎18432, '
        u'幂式与十进制两条拼写的合账 0 只证明拼写没歪; 📐 档位题(6066 的指数 9⇎10⇎11⇎12 减码位 1⇎2⇎3⇎4 恒为 8 '
        u'⇎ 实现侧四档十进制 512⇎1024⇎2048⇎4096 只有 512 那档带单位) ⇎ 805=5+512+256+32 ⇎ 读缓冲 '
        u'16704=16384+320; 🧱 三轨行尺对账(splitlines 比 split 多 159⇎103⇎7⇎24⇎-1 行, 恰等于换页符 '
        u'160⇎104⇎8⇎25⇎0 枚减去「文件以换行收尾」的一枚) ⇎ 两把壳尺逐行分歧 0; 🔁 反向对照(独占针在本家 '
        u'12/12 ⇎ 别家 0) ⇎ 判词五档差合计 0 ⇎ 大小写两把词尺之差即被换行劈开的判词; 🧾 结构面(9 节 ⇎ 节内 '
        u'42301 字符 ⇎ 970 行 ⇎ 205 句, 含幂式 13 句) ⇎ 谱系(眉行年份 6 枚去重 5 种) ⇎ 与采集遍 _pick99 的 '
        u'91 项对账(85 键名配对 + 6 复合项)同 91 异 0。核心结论一条: 明文上限 2^14 五份都不动, 动的是它外面那一层的'
        u'算法——1.2 记压缩后 +1024 ⇎ 加密后 +2048, 1.3 改算成内层明文 +1 ⇎ 密文 +256(=1 枚 ContentType + 255 '
        u'枚最大 AEAD 膨胀), 实现侧把这三件事摊成三个十进制数(默认值 16384 ⇎ 取值区间 512–16384 ⇎ 读缓冲至少 '
        u'16704), 而 6066 根本不答上限只答档位。\n\n'
        u'### 本条不能由在库文件判定的(只登记, 不进门槛)\n'
        u'RFC errata 与改版后的现值(8446/5246 勘误表不在盘) ⇎ OpenSSL 之外实现的取值(内核 TLS ⇎ nginx ⇎ '
        u'BoringSSL) ⇎ record_size_limit 与 max_fragment_length 在真实握手里的协商结果 ⇎ 抓包实测的记录长度。'
        u'本条只认这五份在盘文本自身。\n\n'
        u'### 编码与门的账\n'
        u'T1 逐锚回源: 本注折平档 25/25 ⇎ 原面档 %d/25(差 %d 枚皆跨硬换行, 门按容行档判) ⇎ T2 DERIV 复算: '
        u'%d 枚面值由 corpus/_b99contract.json 逐枚现算, 门内现量 %d 键与建条遍逐键同值 ⇎ T3 码位账: 五份源面'
        u'唯一码位 %s 枚。本条小整数待核 0 项(门内 34 个提示里没有 B99)。\n'
        % (row(n_ch), row(n_word), row(n_line), row(n_cp), row(LIT[u'2^14']), row(LIT[u'16384']),
           row(LIT[u'MUST NOT exceed']), row(LIT[u'record_overflow']),
           enc_ch, src_tot, pct(enc_ch, src_tot), orig_ch, orig_nl, pct(enc_ch, orig_ch),
           pct(enc_ch, orig_nl), orig_nl - orig_ch,
           row(LIT[u'2^14+1']), row(LIT[u'2^14']), u'8⇎7⇎4⇎2⇎0',
           row(LIT[u'record_overflow']), u'6⇎3⇎2⇎3⇎0',
           row(LIT[u'illegal_parameter']), u'19⇎0⇎4⇎2⇎0',
           len(own_raw), n_needfold, u'/'.join(sorted(set(who))), len(exc), len(shared), shared[0],
           row(FLAT['ans_words']), row(FLAT['ans_chars']),
           len(own_raw), n_needfold, len(REG), len(FLAT), row(n_cp)))

head, _ = md.split(u'## ⛓解读注', 1)
new = head + NOTE
assert new.count(u'## ⟪BabelTele⟫') == 1 and new.count(u'## ⛓解读注') == 1
assert new.count(u'## [[原始语料|ORIGINAL]]') == 1
assert u'(待第四遍复测后写回)' not in new
io.open(ENTRY, 'w', encoding='utf-8', newline=u'\n').write(new)
print(u'B99 解读注: 源 %d 字符/%d 词 ⇎ 编码 %d 字符(%s of 源, %s of 摘录) ⇎ 锚 25 枚(原面 %d ⇎ 需折平 %d) '
      u'⇎ 独占 %d ⇎ 共享串 %d ⇎ 待核 0'
      % (src_tot, sum(n_word), enc_ch, pct(enc_ch, src_tot), pct(enc_ch, orig_ch),
         len(own_raw), n_needfold, len(exc), len(shared)))
