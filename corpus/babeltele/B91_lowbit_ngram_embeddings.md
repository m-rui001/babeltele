# B91 论文压缩: Low-Bit N-Gram Embeddings(语言模型 n-gram 嵌入低比特化)→算子中文——4-bit 省75% 表内存保>99% 改进
src: corpus/raw/papers/arxiv_2610.31646.txt (arXiv:2610.31646v1, Chung/Du, cs.CL, 提交 2026-10-22)
dir: corpus/babeltele/B91_lowbit_ngram_embeddings.md
; tags: 论文压缩 n-gram嵌入 低比特量化 内存-保真权衡 DeepSeek-V4.1-Flash 锚归属由摘要现推 闭合账

## [[原始语料|ORIGINAL]]
### ⟦A⟧ ⟸ corpus/raw/papers/arxiv_2610.31646.txt

Many recent open-weight language models use n-gram embedding tables to improve performance. These tables store learned representations of short token sequences, such as pairs or triples of consecutive tokens, which the model retrieves during processing. However, they can require substantial memory: DeepSeek-V4.1-Flash, for example, allocates 196 billion parameters to its Engram n-gram memory. We therefore investigate whether this memory cost can be reduced while preserving the performance improvement that the tables provide. We propose storing n-gram embeddings at low precision and systematically investigate different quantization methods and bit allocations across tables. Across nanochat-, Llama-, and GPT-2-family models trained from scratch, four-bit tables save approximately 75% of table memory while preserving more than 99% of the validation-loss improvement from adding the tables. Using fewer bits leads to a larger drop in performance, although we find that a short fine-tuning phase recovers a significant part of this loss. In addition, reinvesting the saved memory in larger tables can improve performance beyond that of the original full-precision tables while still using less memory. These table memory savings also extend to large existing models: on DeepSeek-V4.1-Flash and Qwen3.8-Flash-Next, low-bit tables save 47-55% of table memory, with perplexity increases of less than 1.2% and largely preserved downstream task performance. These findings establish low-bit precision as a practical way to reduce the memory requirements of n-gram embeddings and use the saved capacity to improve model performance.

## ⟪BabelTele⟫
🧭 arXiv:2610.31646v1《Low-Bit N-Gram Embeddings for Language Models》(Chung/Du, cs.CL, 2026-10-22)—n-gram 嵌入表低精度化; 摘要1633c/230w; 与 B01 同源生态(DeepSeek-V4.1-Flash 已现)。
🎯 近期开放权重模型用 n-gram 嵌入表(存短 token 序列如相邻对/三元表示, 处理时检索)提性能; 但极占内存⟦A⟧⟨DeepSeek-V4.1-Flash, for example, allocates 196 billion parameters to its Engram n-gram memory⟩。
📖 方法: 低精度存 n-gram 嵌入⟦A⟧⟨storing n-gram embeddings at low precision⟩, 系统扫量化法×比特分配。
🔧 从头训(nanochat-/Llama-/GPT-2-系): 4-bit 表省≈75% 表内存、保>99% 加表验证损失改进⟦A⟧⟨four-bit tables save approximately 75% of table memory while preserving more than 99% of the validation-loss improvement⟩; 更少比特掉更多, 短微调挑回大部。
📊 现模(DeepSeek-V4.1-Flash、Qwen3.8-Flash-Next)低比特省47-55% 表内存⟦A⟧⟨save 47-55% of table memory⟩, 困惑度增<1.2%、下游基本保住; 省下内存再投更大表可超原全精度表且仍更省。
ℬ 判据: 内存⇿保真为主干, 数字逐字锚(196B/75%/>99%/47-55%/<1.2%), 读区即复原「为何量化⇿4-bit 甜点⇿现模省多少⇿省容反哺」。


## ⛓解读注

### 压缩账(本注现算)

| 量 | 值 |
|---|---|
| 源(摘要) | 1633 字符 / 230 词 |
| 编码(BabelTele 算子中文) | 840 字符 |
| 体积比 | 51.4% |
| 事实覆盖 | 11 项 assert 全过 |
| 锚 | 编码区 4 处(工具侧逐字校验 ok=4 bad=0) |

### 读法
(见编码区主干五段闭环: 背景/旧法/本文/结果/判据; 锚回源可逐字核。)

### 本条不能由在库文件判定的(只登记, 不进门槛)
全文方法算法细节、逐模型数值、下游任务细表; 在摘要外, 需拉 PDF 正文。

### 编码与门的账
编码区 840 字符(不含换行); 编码区锚 4 处(工具侧逐字校验 ok=4 bad=0); 事实覆盖 11 项 assert。门槛三遍: T1 字面逐锚回源 ⇿ T2 词级事实覆盖 ⇿ T3 码位与字母账。
