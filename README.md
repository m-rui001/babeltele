# BabelTele

把「同一道题被多份一手文书各答一遍」这类隐性知识压成高密度文本，并且**每个数字都能当场复算回源**。

协议出自论文 *Large Language Models Do Not Always Need Readable Language*（arXiv 2606.19857）：
以牺牲人类可读性换模型侧可复原的密度，三原则 = Omnilingual · Symbolic Collapse · Recoverable Semantic Density。
本仓库是该协议下的实际转化集，**95 条**，一条一个题目——例如「证书序列号到底能多长」由
RFC 2459 ⇎ 3280 ⇎ 5280 ⇎ CA/B TLS BR ⇎ Let's Encrypt 手册各答一遍，答案分别是「不给数」
⇎「20 octets」⇎「20 octets + 符号位规矩」⇎「< 2¹⁵⁹ 且 ≥ 64 位熵」⇎「8 字节 = 63 位」，
四把尺要现场互译才知道它们同不同。

细节账本在 [`corpus/README.md`](corpus/README.md)。

## 目录

```
corpus/
  babeltele/BNN_*.md      95 条条目（原始语料锚 + 编码区 + 解读注）
  audit.py                保真硬门槛（三层，只用标准库）
  _pickNN.py              第一遍：采集实现 → _bNNmeas.json
  _mkBNN.py               第二遍：同定义不同算法的复算实现 → _bNNflat.json
  _mkNNemit.py            落盘遍：条目 md + _bNNcontract.json
  _wireNN.py _applyNN.py  把新条目的复算段接进 audit.py
  _fillNN.py              第三遍：第三种机制回填解读注
  fetch_cot.py            取免费推理模型的思维链；代理配置读 `BABELTELE_CFG` 或 `~/.config/babeltele/config.json`
  _anchorlex.py           机械产出 _atomsNN.txt（锚词表，禁止手打锚）
  _readme_batch.py        README 记账遍
  _bNNmeas.json _bNNflat.json _bNNcontract.json _atomsNN.txt   量测/契约/词表
```

## 门槛

```sh
python -X utf8 corpus/audit.py     # 全量，数分钟
```

- **T1 字面**：编码区每个数字锚点（≥3 位或带小数）必须逐位命中源文件。
- **T2 推导**：命不中的必须在 DERIV 契约里给出算式；算式引用的每个常量同样要命中源，
  复算值按锚点小数位取整后必须相等——算式在 audit 侧的受限环境里求值，只给
  `BNNV` / `range` / `sum` / `len` / `max` / `min` / `abs`，**不给原始表**，所以它不能自证。
- **T3 码位**：结构性断言（码位账、行尺三轨、壳账容斥）逐条归零。

末行输出 `保真门槛(T1 字面 + T2 推导 + T3 码位): PASS` 才算进门。

一条条目走六遍：采集 → 词表 → 复算 → 落盘 → 接线进门 → 第三遍回填，另加 README 记账。
任一遍不过即红，不接受白名单，也不允许手打数字。

## 上游原文不在仓库里

条目引用的 RFC、CA/B BR、NIST、Federal Register、事故报告、论文等原文约 140 MB，
按各自授权分发，已整体 `.gitignore`。要复跑门槛就照条目头部 `src:` 行的端点抓取，
放回 `corpus/raw/` 下同名路径。详见 [`NOTICE`](NOTICE)。

## 许可

代码与条目：MIT（[`LICENSE`](LICENSE)）。所引一手文书：仍归各自上游（[`NOTICE`](NOTICE)）。
