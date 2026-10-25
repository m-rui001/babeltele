# -*- coding: utf-8 -*-
# 外派写稿(发射段): 三条待发射的条目(B95 证书序列号长度 ⇎ B98 Retry-After ⇎ B99 TLS 记录明文上限),
# 每条两路(低温守契约 ⇎ 高温放开句式), 把 量测字典 F ⇎ 锚词汇表 ⇎ 已进门条目 B92 的编码区范例
# 一并喂给免费 API, 收回整份 corpus/_mkNNemit.py。
import io
import json
import os
import re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TAGS = [u'B95', u'B98', u'B99']
EXEMP = u'corpus/babeltele/B92_redirect_hop_limit_five_answers.md'

SYS = (u'你在为一个"推理密度语料压缩库"写**编码区发射段**(Python 3)。这个库的条目把五份一手文书里\n'
       u'同一个问题的不同答案压成一格中文, 每个数字都必须由量测字典插值, 零手填。\n'
       u'硬契约(违背即废稿):\n'
       u'1) 编码区文本里的**每一个数字**都写成 V(\'key\') 或 V(\'key\', i) 的插值, 不准出现手打的量值。\n'
       u'   V(name, i=None): i 为 None 时取 F[name](须是标量), 否则取 F[name][i]; 同时把该面值登记进\n'
       u'   REG[str(返回值)] = "BNNV(\'name\')" 或 "BNNV(\'name\', i)"。两个不同键读出同一个数时后登者覆盖, 不必处理。\n'
       u'2) 锚 ⟨片段⟨…⟩⟩ 只能逐字取自给你的**锚词汇表**(每行 "标签<TAB>原文片段"); 一条锚前挂它自己的 ⟦标签⟧。\n'
       u'   词汇表里没有的句子一律不许引。编码区里 ⟦X⟧ 的枚数必须等于 ⟨…⟩ 的枚数(一句可挂两面, 但每面都算一枚标签)。\n'
       u'3) 写盘: 条目 md 落 corpus/babeltele/BNN_<英文短名>.md, 结构照范例(## [[原始语料|ORIGINAL]] 各源锚块\n'
       u'   ⇎ ## ⟪BabelTele⟫ 编码区 ⇎ ## ⛓解读注 占位一行)。REG 落 corpus/_bNNcontract.json(紧凑 json, 键=面值字符串)。\n'
       u'4) 只准 io/json/re/os; 字符串一律 u 前缀; 不许 open(..., \'w\') 上述两类以外的路径;\n'
       u'   不许 subprocess; 不许改 F; 不许 print 无关内容(结尾 print 一行收据即可)。\n'
       u'5) 量测键的**名字**不解释口径, 句子里要把口径写明白(逐行档⇎折平档⇎剥壳面⇎码面⇎注释面…),\n'
       u'   数值为零也照占键位; 不许把不符的键绕过。\n'
       u'输出(严格): 只输出一个 ```python 代码块 = corpus/_mkNNemit.py 的全文。它是在 _mkNN.py 末尾被 exec 的片段,\n'
       u'因此可直接使用已存在的全局名 F ⇎ DER ⇎ json ⇎ io ⇎ re ⇔ 以及你自己新建的 V/REG/E。')


def trim_F(path, tag):
    d = json.load(io.open(path, encoding='utf-8'))
    keep = {}
    for k, v in d.items():
        r = json.dumps(v, ensure_ascii=False)
        if len(r) > 110:
            continue
        keep[k] = v
    return u'# %s 量测字典 F(共 %d 键, 此处给 %d 键; 未列出的长表键不要引用)\n' % (
        tag, len(d), len(keep)) + json.dumps(keep, ensure_ascii=False, sort_keys=True, separators=(u',', u':'))


ex = io.open(EXEMP, encoding='utf-8').read()
m = re.search(u'## ⟪BabelTele⟫\n(.*?)\n\n## ', ex, re.S)
head = ex[:ex.find(u'## ⟪BabelTele⟫')]
EX = (u'# 范例(已进门条目 B92 的头部 ⇎ 编码区全文)\n' + head + u'## ⟪BabelTele⟫\n' + m.group(1) + u'\n')

T = []
for tg in TAGS:
    NN = tg[1:]
    pick = io.open(u'corpus/_pick%s.py' % NN, encoding='utf-8').read()
    doc = pick[:pick.find(u'"""', 5) + 3] if u'"""' in pick[:600] else pick[:400]
    lbl = re.search(u'^LBL = .*$', pick, re.M).group(0)
    paths = re.search(u'^(?:SRC|FILES|PATH) = \\[(?:.|\\n)*?\\]', pick, re.M).group(0)
    anchors = io.open(u'corpus/_atoms%s.txt' % NN, encoding='utf-8').read()
    if len(anchors) > 9000:
        anchors = anchors[:9000]
    theme = {u'B95': u'证书序列号能多长: 字节 ⇎ 十六进制字符 ⇎ 比特熵三把尺(rfc2459/3280/5280 ⇎ 浏览器 ⇎ Let\'s Encrypt)',
             u'B98': u'Retry-After 该写多久、谁能省掉它(rfc2616/6585/7231/9110 ⇎ curl)',
             u'B99': u'一条 TLS 记录最多装多少明文: 16384 与它旁边那几个数(rfc8446/5246/8449/6066 ⇎ openssl pod)'}[tg]
    for i, (temp, extra) in enumerate([
            (0.3, u'句式照范例的段序(源账 ⇎ ⛓规则链 ⇎ ①…⑪ 各段 ⇎ 🧾程序侧 ⇎ 📊小实体账), 段落数 10~14。'),
            (0.85, u'段落数 10~14, 段序自定但必须覆盖: 五源体积账 ⇎ 答案值互斥 ⇎ 单位/尺子差异 ⇎ 序列化档位差 ⇎ 反向对照(别家的句子在本家读不到) ⇎ 程序侧常量。')]):
        T.append({u'id': u'%s_em%d' % (tg, i), u'system': SYS, u'temperature': temp,
                  u'max_tokens': 30000,
                  u'prompt': (u'# 任务: 写 corpus/_mk%semit.py(条目 %s)\n%s\n\n%s\n\n'
                              u'# 采集遍头信息与源表(只读, 原始语料段要按标签把锚列成 ### ⟦X⟧ ⟸ 路径 的块)\n%s\n%s\n%s\n\n'
                              u'# 锚词汇表(唯一可引的原文片段)\n%s\n\n%s\n\n'
                              u'# 侧重点\n%s\n'
                              % (NN[0] if False else NN, tg, theme, trim_F(u'corpus/_b%sflat.json' % NN, tg),
                                 doc, lbl, paths, anchors, EX, extra))})
json.dump(T, io.open(u'corpus/_api9x_emit.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(u'发射段任务 %d 路; 提示词长度 %s' % (len(T), [len(t['prompt']) for t in T]))
