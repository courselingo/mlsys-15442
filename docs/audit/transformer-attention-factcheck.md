# 事实核对 · CMU 15-442 / 15-642 Machine Learning Systems 第 8 讲 Transformer、注意力与优化

- 核对人：**非作者**（本讲任何一轮写作我都没有参与，也没有与作者 `mlsys-author` 讨论过本讲内容）
- 核对日期：2026-09-29
- 被核对版本：`content/08-transformer-attention/index.md`
  归一化 SHA256 前16 = **37F88D9EEF7D7C5A**
  （全 64 位 `37F88D9EEF7D7C5A1F93310DFB23D45D4DED70E93FDC07EF2E214646AED7F5BA`，**19,591 B**；
  文件本身已是 LF，`\r\n` 归一化后长度与哈希都不变；最后写入 2026-09-29 10:35:25）
  - 14 张配图（`figures/transformer-attention-1.svg` … `-14.svg`）
- 源材料（本次实际依据的，逐个列出，并说明我怎么用它）：

| # | 文件 | 用途 / 说明 |
| --- | --- | --- |
| 1 | `_sources/mlsys-15442/evidence/mlsys-slide-07-transformers-attention.pdf`（**1,877,431 B，30 页**） | 权威源。**取件校验**：体积 1,877,431 B、尾部为 `%%EOF`（`startxref 1877243`）、大小**不是** 2 的整数次幂（本项目有两次「HTTP 200 却截断」的记录，`16384 = 2^14` 就是一次）⇒ 判定为完整件 |
| 2 | 同目录 `.faithful.txt`（14,320 B，29 个 `===== PAGE =====` 分隔符 ⇒ **30 页**文本块） | **主要依据**（按项目约定用 faithful）。原件含 89 个 NUL；我为阅读做了去 NUL / 控制字符替换空格的只读副本（未改源文件，副本在 `%TEMP%`）。按「幻灯片标题 + 逐字原文 + 页码」定位，**行号不作坐标** |
| 3 | 同目录 `.embedded.txt` | **不存在**，因此本轮没有可误用的字体二进制；`text-clean/*.txt` 我也**未使用**（按规则） |
| 4 | 同一份 PDF 的文本矩阵坐标（`Tm` 的 e/f 分量） | **补充手段**，只用在 p11 那一页：核「19 TB/s (20 MB)」到底配给哪一行。这不是另一份抽取产物，是同一份 PDF 的同一批内容流 |
| 5 | `_sources/mlsys-15442/evidence/mlsys-site-lectures.yml` | 核本讲的**周次与日期**（`02/09 Mon`、`Week 5`、`slides: /slides/07-transformers-attention.pdf`） |
| 6 | `content/03-deep-learning-abstraction/index.md`、`content/05-optimizing-linear-algebra/index.md`、`glossary.toml` | 核本页的**跨讲指路**（L20／L26／L88／L132／L144／L172）与 7 个不同的 `[[term:…]]` |

> **页码约定**：下文一律用「**pN**」表示 **PDF 页码**。这一份课件的页脚与 PDF 页码**一一对应**
> （p1 页脚 1、p3 页脚 3、p11 页脚 11、p18 页脚 18、p30 页脚 30），**没有**未编号的动画帧，
> 所以「pN」既是 PDF 页码也是课件自己的页脚号。页数与文本块数都是 **30**，两者一致。

> **文本层说明**：faithful 对这份课件的正文是完整的（`Refer to approach where individual states are combined using weights`、
> `Benefits: more parallelism, reduced computation cost`、`Large intermediate results`、`65504`、`66.6`／`75.2`、
> `40.3 GB`／`4.4 GB`、`41.7`／`7.3`、`108 SMMs`、`2-4x speedup, 10-20x memory reduction`、
> `attention is associative and commutative`、`up to 8x faster than prior work` 等都能原样检索到）。
> 少量数学字形（p2 的 `Σ α_i D_i`、p14 的 softmax 公式）仍以控制码残留，我用同一份 PDF 的内嵌 `ToUnicode` CMap 解了
> 可以确定归属的部分（例如 p12 的 ` G R Q ¶ W   V W R U H …` 按 −3 位移解出 `Don't store attention matrix from forward`，
> 与页面 L104 逐字一致）；**解不出的那几个字形我不下结论**（见「我核不到的」第 1 条）。

---

## 结论

**P0（事实错误）：0 条 ｜ P1（易误解/依据不足）：1 条 ｜ P2（措辞）：4 条**

这一讲数字密集（10 组数字、4 组形状、1 组带宽对照、1 个浮点上界），而且**全部在页面上出现了**。
我逐个回源核过：**10 组数字逐字命中，四组形状与 `O = Softmax(QK^T)V` 的乘法方向也对**，
没有找到与课件相冲突的断言。唯一一条 P1 是**归属写反了**（把课件自己写的术语说成是我们的提法）。

> **我针对 Lead 点名的那类错误专门查过**（第 13 讲那条「公式错一个符号而读起来毫无破绽」）：
> 这一讲页面上出现的每一个式子我都逐字对过一次源，见下面「式子与形状的逐条核对」。
> 最需要小心的一处是 `QK^T` 的**转置方向**（写成 `KQ^T` 在方阵时也读得通，而 p10 的 `N x N` 在两边都不变，
> 光看形状抓不出来）——**页面写对了**（L74「Q 与 K 各是 N 乘 d，**转置相乘**之后得到的是一个 N 乘 N 的矩阵」，
> 且 L48 明确是「**Q 乘 K 的转置**」）；另一处是 `O = AV` 里 **A 是 softmax 之后的那个**（页面 L74
> 「对它做 softmax 还是 N 乘 N，再乘 V」✅ 顺序对）。

---

## P0 · 事实错误

**0 条。**

逐条回源范围内，没有找到与课件相冲突的断言。数字、形状、方向、外部署名、跨讲指路都对得上
（见「已逐条回源、未发现问题的」那一节）。

---

## P1 · 易误解或依据不足

### P1-1 L172 与溯源 L212 把 `kv-cache` 说成「我们的提法 / 后面几讲的提法」——课件 p26 自己就写着 `Key-value cache`

- **正文 L172**：「解码阶段要读的那一段历史，正是**后面几讲反复提到的** [[term:kv-cache]]。」
- **溯源 L212（末尾）**：「…其中 **[[term:kv-cache]] 这个词是我们在讲解时的提法**，课件那一页写的是
  「前面所有 token 的键与值」。」
- **源（p26，标题 `Generative LLM Inference: Autoregressive Decoding`）逐字**：
  ```
  Pre-filling phase (0-th iteration):
    Process all input tokens at once
  Decoding phase (all other iterations):
    Process a single token generated from previous iteration
    Use attention keys & values of all previous tokens
  Key-value cache:
    Save attention keys and values for the following iterations to avoid recomputation
  ```
  ⇒ 课件**自己就有一条独立的小节标题** `Key-value cache:`，还给了它的用途
  （`Save attention keys and values for the following iterations to avoid recomputation`）。
- **判定**：这不是「漏声明」，是**把归属写反了**——页面把一个**课件已经写出来的术语**记成了我们的提法，
  同时又把课件的原话缩窄成「前面所有 token 的键与值」那一句（那句确实在，逐字是
  `Use attention keys & values of all previous tokens`，引用本身没错，但它**不是那一页的全部**）。
  读者据此会以为课件没有引入键值缓存这个概念。
  （检索：faithful 全文 `key-value` **0** 命中，但那是因为课件把它**逐字母分开了**（`K e y` / `-` / `v a l u e   ca ch e`）；
  改用 `c a ch e`／`a t t e n t i o n   k e y s` 就命中 ⇒ 这正是「否定性结论必须写清检索词、并说明换了哪些写法」的用例。）
- **建议**：把 L212 末尾那句改成「课件 p26 有一条独立小节 `Key-value cache`，正文按它的原话讲解」，
  L172 的「后面几讲反复提到的」改为「课件在这里就引入了它，后面几讲会反复用到」。

---

## P2 · 措辞

### P2-1 L86／图 6：「每块的共享内存约 20 MB」是课件的原话，但 20 MB 其实是整片 SRAM 的量级（建议加一句注明）

- **正文 L86**：「课件给的两个数字是：**每块的共享内存约 20 MB**，带宽 19 TB/s；设备全局显存 80 GB 量级，带宽 1.5 TB/s。」
- **图 6 可见文字**：`共享内存 / 约 20 MB，19 TB/s`、`全局显存 / 80 GB 量级，1.5 TB/s`、`带宽差了十几倍`
- **源（p11，标题 `Revisit: GPU Memory Hierarchy`）**——配对关系我用该页的**文本矩阵坐标**核过，是**同列**的：

  | 原文（逐字） | x | y |
  | --- | --- | --- |
  | `Per-block shared memory` | 40.866 / 68.897 / 74.88 / 121.9 | 223.72 |
  | `(readable/writable by all threads in a block)` | 53.379 / 74.88 | 202.07 / 180.45 |
  | `Device global memory` | **730.13** | 261.06 |
  | `(readable/writable by all threads)` | 730.63 / 792.65 | 239.41 / 217.79 |
  | `19 TB/s (20 MB)` | **55.961** | 144.7 |
  | `1.5 TB/s (80 GB)` | **759.6** | 87.095 |

  ⇒ `19 TB/s (20 MB)` 在**左列**、`1.5 TB/s (80 GB)` 在**右列**，与行标签 `Per-block shared memory` / `Device global memory`
  同侧；而括号里的 `(20 MB)` / `(80 GB)` 本身就把容量与带宽锁在一起。
  **所以页面这组配对是对的**（不是把 20 MB 配给了全局显存那种方向错误）。
- **但**：20 MB 是**整片 A100 的 SRAM 量级**（108 个 SMM × 192 KB ≈ 20.7 MB），单个块能用的共享内存是 192 KB 量级。
  课件把它记在 `Per-block shared memory` 这一行，是课件自己对层级的简化。页面照录**不算错**
  （与第 6 讲 p36 那处「示意参数」同类），但建议补一句「课件把整片的 SRAM 记在『每块共享内存』这一行」，
  免得读者把这个数当成一个块的额度。附带：页面 L88 的「片上存储快十几倍」= 19 ÷ 1.5 = 12.7 ✅ 算术对。

### P2-2 L94「**三次**经过慢的那一级」是页面自己的计数，课件只写了「反复读写」没有次数

- **正文 L94**：「它被写出来、被读回去做 softmax、再被读一遍去乘 V。**三次经过慢的那一级**…」
- **源（p10）** 逐字只有 `Repeated reads/writes from GPU device memory`，**没有次数**。
- **问题**：按同一页中间矩阵的生命周期数，softmax 的**结果也要写回一次** ⇒ 更像是四次（写 A、读 A、
  写 softmax(A)、读 softmax(A)）。「三次」是页面自己的数法，而它读起来像课件给了个数。
- **建议**：去掉具体次数（「要反复经过慢的那一级」），或写明「按我们的数法，至少四次」。

### P2-3 L146 头优先的**顺序理由**是我们自己的；课件 p19 自己的答案是另一句，页面在这一层没有出现

- **正文 L146**：「这里有一个顺序上的讲究：为什么不先切查询、再切头。因为切头是天生的、不用额外开销…
  如果反过来，先切查询也能得到足够的块数，但那就浪费了头这一份免费的并行度。」
- **源（p19，标题 `FlashAttention: Threadblock-level Parallelism`）逐字**：
  ```
  Step 1: assign different heads to different thread blocks (16-64 heads)
  Step 2: assign different queries to different thread blocks (Why?)
  Thread blocks cannot communicate; cannot perform softmax when partitioning keys/values
  ```
  ⇒ 课件对那个 `(Why?)` 的答案是**通信**：块之间不能通信，所以**不能沿键值切**。
  页面的这句话给的是**另一个**理由（头是免费并行度），而课件这一页的那句回答
  在页面的**线程块**那一层没有出现（页面把它放在了 warp 层，见 L154–L156）。
- **判定**：页面 L146 的内容是合理推断，但它出现在课件写着「(Why?)」的位置上，读者会以为那就是课件的答案。
  按 L212 的非穷尽条款我记 **P2**。
- **建议**：在 L146 前补上课件那句（「课件这里的回答是：块之间不能通信，所以不能沿键值切，只能沿查询切」），
  把我们那条「头是免费并行度」的分析标成我们的。

### P2-4 L158 与图 11、溯源 L211 把「2 到 4 倍加速、10 到 20 倍显存下降」记在 warp 级切分那一节

- **正文 L158**（在「## warp 级切分」一节里）：「课件给的收益是 2 到 4 倍加速、10 到 20 倍显存下降…」
- **图 11（`transformer-attention-11.svg`）可见文字末行**：`课件给的收益是 2 到 4 倍加速、10 到 20 倍显存下降`
- **溯源 L211**：「…warp 级沿查询切不用通信、**2 到 4 倍加速与 10 到 20 倍显存下降**」
- **源**：这是**单独一页**——**p22**，标题就是 `FlashAttention: 2-4x speedup, 10-20x memory reduction`，
  正文另一行 `Memory linear in sequence length`；它排在 warp 级那一页（p21）**之后**，是一个整讲层面的结论页，
  不是 warp 级切分的收益。
- **判定**：内容都对（数字逐字命中 ✅），只是**挂的位置**会让读者把整讲结论当成 warp 切分的局部收益。
- **建议**：把这一句移到 FlashAttention 那一块的收束处（或注明「课件在这一页之后单独用一页给出整体收益」）。

---

## 不算 P 项、但请 Lead 看的一处：**掩码注意力**的跨讲缺口

- **课件 p10** 在形状表里有一行逐字：`A = mask(A)`（就在 `A = softmax(A) : N x N` 同一页）。
- **本讲页面从头到尾没有出现「掩码 / mask」**（检索：正文 `掩码` **0**、`mask` **0**）。
- **但第 3 讲的页面 L112 明确承诺过**：「这一页还列了后面会展开的三个概念：自注意力、**掩码注意力**与多头注意力。
  **第 8 讲会把它们讲透**。」
- ⇒ 这是**跨讲承诺的缺口**（第 3 讲说第 8 讲会讲透，第 8 讲讲了自注意力与多头注意力，漏了掩码注意力；
  而且第 8 讲的源页 p10 上就有 `A = mask(A)`）。
- **我为什么没记成 P 项**：P0/P1/P2 三档是对**页面与源材料的关系**判的，而这是**漏讲**而不是**讲错**
  （页面没有说任何与源冲突的话）。是否要为它开一条，请 Lead 按覆盖率策略裁决。

---

## 已逐条回源、未发现问题的（抽样清单）

页码后为逐字原文；行号为正文行号。

### 式子与形状的逐条核对（针对「错一个符号」那一类）

| # | 正文 | 源（逐字） | 结果 |
| --- | --- | --- | --- |
| 1 | L48／L74：`第二步，Q 乘 K 的转置`；`转置相乘之后得到的是一个 N 乘 N 的矩阵，记为 A` | p10（标题 `How to Compute Attention on GPUs?`）：`O = Softmax(QK` `T` `) V`、`A = QK` `T` `: N x N` | ✅ **方向对**（是 `QK^T` 不是 `KQ^T`；页面 L48 明确写了「Q 乘 K 的转置」） |
| 2 | L74：`对它做 softmax 还是 N 乘 N，再乘 V 得到 N 乘 d 的输出` | p10：`A = softmax(A) : N x N`、`V: N x d`、`O = AV: N x d` | ✅ 顺序对（先 softmax 再乘 V） |
| 3 | L52：`第一步是个线性投影，每个位置独立算，形状是 N 乘 d` | p10：`Q: N x d`、`K: N x d`、`V: N x d` | ✅ 三个都是 `N x d` |
| 4 | L52：`第二步与第三步都作用在那个 N 乘 N 的分数矩阵上` | p10：两行 `N x N`（`A = QK^T` 与 `A = softmax(A)`） | ✅ 两步都是 `N x N` |
| 5 | L128：`前向只保存 softmax 的归一化因子，它的大小正比于 N 而不是 N 的平方` | p17：`By storing softmax normalization factors from forward (size N)` | ✅ 逐字（`size N`） |
| 6 | L92：`Q、K、V、O 四个矩阵，每个都是 N 乘 d，合起来是 4Nd 个元素；而中间那个 N 乘 N 的注意力矩阵是 N² 个元素` | 由 p10 的六个形状推出 | ✅ 算术对（4Nd 与 N²；`N²/Nd = N/d`，N 几千、d 几十 ⇒ 一到两个数量级 ✅） |
| 7 | L118：`16 位浮点能表示的最大值只有 65504` | p14：`Issue: maximum value for 16-bit floating point is 65504` | ✅ 逐字 |
| 8 | L192：`注意力运算满足结合律与交换律` | p29：`Key insight: attention is associative and commutative` | ✅ 逐字 |

### 数字（10 组，全部逐字命中）

| 正文 | 源（页码 · 逐字） | 结果 |
| --- | --- | --- |
| L86 共享内存 `约 20 MB`、`19 TB/s` | p11：`19 TB/s (20 MB)` | ✅（配对经坐标核过，见 P2-1） |
| L86 全局显存 `80 GB 量级`、`1.5 TB/s` | p11：`1.5 TB/s (80 GB)` | ✅ |
| L88 `片上存储快十几倍` | 19 ÷ 1.5 = 12.67 | ✅ 算术对 |
| L130 计算量 `66.6 GFLOPs 涨到 75.2`／`多算了大约一成` | p17：`GFLOPs` `66.6` `75.2` | ✅ 75.2/66.6 = 1.129 ⇒ 约一成 ✅ |
| L130 全局访存 `40.3 GB 降到 4.4 GB`／`少搬了近九成` | p17：`Global mem access` `40.3 GB` `4.4 GB` | ✅ 1 − 4.4/40.3 = 89.1% ✅ |
| L130 运行时间 `41.7 毫秒降到 7.3 毫秒`／`大约六分之一` | p17：`Runtime` `41.7` `ms` `7.3` `ms` | ✅ 41.7/7.3 = 5.71 ✅ |
| L140 `一块 A100 有 108 个 SMM，也就是大约 108 个线程块的位置` | p18：`(An A100 has 108 SMMs -> 108 thread blocks)` | ✅ 逐字 |
| L142 `头数通常在 16 到 64 之间` | p18：`(16-64 heads)` | ✅ 逐字 |
| L158 `2 到 4 倍加速、10 到 20 倍显存下降`／`显存占用与序列长度是线性关系` | p22：`2-4x speedup, 10-20x memory reduction`／`Memory linear in sequence length` | ✅ 逐字（挂的位置见 P2-4） |
| L194 `比之前的工作快最多 8 倍` | p30：`Flash-Decoding is up to 8x faster than prior work` | ✅ 逐字 |

### 其余逐条

- **p2**：`Refer to approach where individual states are combined using weights` ✅（L30 的「按权重组合起来」逐字对应）；
  `Hidden states from previous layer` ✅（L34「状态来自上一层」）；`Attention output` ✅；
  `There are different methods to decide how attention score is being computed` ✅（L36 说权重不是固定值、由匹配算出，与这页的语境一致）
- **p3**：标题 `Transformer: Self-Attention Mechanism for Language Models` + `Encoder` / `Decoder` +
  `Ashish Vaswani et. al. Attention is all you need.` ✅（L56 三处逐字对应）
- **p4／p5**：`Slide credit: Jay Allamar` + `Mapping a query and a set of key-value pairs to an output` ✅
  （L44 的「核心说法」逐字对应；**课件把 `Alammar` 拼成了 `Allamar`**，页面 L44／L210 跟着课件写，✅ 不算错，此处留痕）
- **p6**：`Multiple matrix multiplications` ✅（L50「课件在这里标了一句」）
- **p8**：`Parallelize attention layers with different linear transformations on input and output`／
  `Benefits: more parallelism, reduced computation cost` ✅（L62／L64／L66 逐字对应）
- **p10**：`Challenges:` / `Large intermediate results` / `Repeated reads/writes from GPU device memory` /
  `Cannot scale to long sequences due to O(N^2) intermediate results` ✅
  （L24「随序列长度平方增长」、L76「挑战一栏写的是：中间结果很大」、L78「要被搬很多次」✅）
- **p12**：`Key idea: compute attention by blocks to reduce global memory access` /
  `Two main Techniques:` / `1. Tiling: restructure algorithm to load query/key/value block by block from global to shared memory` /
  `2. Recomputation: Don't store attention matrix from forward, recompute it in backward` /
  `FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness` ✅
  （L98／L102／L104／L106 逐字对应；`Don't store…` 那行是控制码残留，按 −3 位移解出后逐字一致 ✅）
- **p13**：`Tiling: Decompose Large Softmax into smaller ones by Scaling` /
  `1. Load inputs by blocks from global to shared memory` / `2. On chip, compute attention output wrt the block` /
  `3. Update output in device memory by scaling` ✅（L102 的「搬进共享内存 / 片上算完再写回」✅）
- **p14**：标题 `Safe Softmax and Online Softmax` ✅（L116「课件的解法叫在线 softmax」、L120「放在数值稳定性那一节里讲」✅）；
  `For two vectors x1 and x2, we compute the softmax of [x1 x2]` ✅（L116 的「滚动」✅）
- **p15**：`Animation credit: Francisco Massa` ✅（L210 逐字对应）
- **p17**：`Recomputation: Backward Pass` / `By storing softmax normalization factors from forward (size N), recompute attention in the backward from inputs in shared memory` /
  `Speed up backward pass with increased FLOPs` ✅（L128／L132 逐字对应）
- **p18／p19**：`How to partition FlasshAttention across thread blocks?`（**课件把 `FlashAttention` 拼成了 `FlasshAttention`**，
  页面没有跟着抄错 ✅）、`Step 1: assign different heads to different thread blocks`、
  `Step 2: assign different queries to different thread blocks (Why?)` ✅（L140／L142 逐字对应；`(Why?)` 的回答见 P2-3）
- **p20**：`Do we need to handle workload imbalance?` / `No. GPU scheduler automatically loads the next block once the current one completes.` ✅
  （L144 逐字对应）；`Queries` / `Keys/Values` / `Block 1`…`Block 5` / `Forward pass` ✅（L142 的切法图 ✅）
- **p21**：`FlashAttention: Warp-Level Parallelism` / `How to partition FlashAttention across warps within a thread block?` /
  `Splitting across K/V requires communication to add results` / `Splitting across Q avoids communications` ✅（L154／L156 逐字对应）
- **p26**：`Pre-filling phase (0-th iteration): Process all input tokens at once` /
  `Decoding phase (all other iterations): Process a single token generated from previous iteration` /
  `Use attention keys & values of all previous tokens` / `Key-value cache: Save attention keys and values for the following iterations to avoid recomputation` ✅
  （L166 逐字对应；**`Key-value cache` 这一行是 P1-1 的依据**）
- **p27**：`Pre-filling phase: Yes, compute different queries using different thread blocks/warps` /
  `Decoding phase: No, there is a single query in the decoding phase` ✅（L180／L182 逐字对应）
- **p28**：`FlashAttention Processes K/V Sequentially` / `Inefficient for requests with long context (many keys/values)` ✅
  （L182「它只能沿键值顺序处理，于是上下文一长，这一步就成了瓶颈」逐字对应）
- **p29**：`1. Split keys/values into small chunks` / `2. Compute attention with these splits using FlashAttention` /
  `3. Reduce overall all splits` / `Key insight: attention is associative and commutative` ✅（L190／L192 三步逐字对应）
- **p30**：`Flash-Decoding is up to 8x faster than prior work` ✅（L194 逐字对应）
- **跨讲指路**：L20「第 3 讲把注意力当作一个概念讲过一次」✅（第 3 讲 L98–L112 是「## 注意力：把序列内部的并行打开」，
  L108 就有「中间结果的规模随序列长度平方增长」，L112 还写了「第 8 讲会把它们讲透」）；
  L132「这句话在第 5 讲以「分块」的形式出现过」✅（第 5 讲 L120–L156 是寄存器分块／缓存行分块／复用的规律）；
  L144「第 6 讲讲过的「线程块可以任意顺序执行」」✅（第 6 讲 L147）；L88「和第 5 讲的内存层级是同一件事」✅（第 5 讲 L92–L106）
- **7 个不同的 `[[term:…]]` 全部在 `glossary.toml` 里有定义**：`ml framework`／`machine learning system`／`latency`／
  `compute`／**`KV cache`**／`throughput`／`hardware accelerator`（**7/7 命中**；正文引用共 9 次，`latency` 与 `kv-cache` 各 2 次）✅
  （**注意**：`[[term:kv-cache]]` 能解析，说明 glossary 里有 `key = "KV cache"` —— 这一点也让 P1-1 更值得改：
  页面的术语表承认这个词，而页面的溯源却说它来自我们）
- **14 张配图与正文引用一一对应**（正文 14 条 `](figures/…)`，目录内 14 个文件，无「引用了不存在」也无「存在但未引用」）✅
- **周次／日期** ✅（`mlsys-site-lectures.yml`：`02/09 Mon`、`Week 5: Case study: Transformer, Attention, Optimizations`、
  `slides: /slides/07-transformers-attention.pdf`；与页面 L8／L13／L207 一致）；
  溯源 L209「课程仓库根 LICENSE，19,342 B」✅（`mlsys-webrepo-LICENSE.bin` 正好 19,342 B）

---

## 我核不到的（诚实记录）

> **「我没找到」不等于「源里没有」。** 下面是我**没有**找到依据、或我**没有**条件核的部分。

1. **p2 与 p14 的数学字形我没有全部解出来。**
   - p2 有一行长串（faithful 里是 `]   ^   v ] } v …  Z     }  ]  ] } v` 这种），位置在 `Intuitively` 与
     `to this current hidden output` 之间，按 −3 位移**解不出可读句子**（字符位移量不一致）。
     ⇒ 我**不知道**课件这一行在说什么，因此**没有**在这一行上对页面的 L36 下任何结论。
   - p14 的 softmax 公式（`softmax(x) = …`）同样残留控制码，我只核到 `65504` 这个数与
     `For two vectors x1 and x2, we compute the softmax of [x1 x2]` 这一行。⇒ 公式的**具体形式我没有逐字核**。
   - 我**没有**用外部文献去补这两处（按规则只核「课件有没有这么说」）。
2. **图片对象里的文字读不到。** faithful 只给文本对象；p7（`Self-Attention` 7 页）、p9（`Multi-Head Self-Attention`）、
   p15（`Tiling` 动画）、p16（`FlashAttention 2 Algorithm`）、p23–p25（自回归解码的三页图）
   这些页的正文主要或全部在图形里。⇒ 这几页**没有可核的文本**，我对它们**不作任何结论**；
   页面对它们的讲解（L64/L166/L168）我按可核到的文字部分判断。
3. **配图只核了文本层。** 14 张 SVG 我都读了全部 `<text>`／`<title>`／`<desc>` 节点（这一讲的 SVG **有** `<desc>`/`<title>`），
   但**几何（对齐、间距、箭头指向、颜色语义）没有逐条复核**。
4. **`text-clean/*.txt` 我未使用**（按规则）；这份课件在 evidence 目录里**没有** `.embedded.txt`，所以不存在误用它的风险。
5. **检索范围与词（否定性结论一律附范围）**：
   - 正文 `content/08-transformer-attention/index.md` **L1–L212 全读**；源 faithful **30 页逐页读完**。
   - P1-1：我先搜 `key-value`（**0** 命中），换成 `Key` `cache` `ca ch e` `attention keys` 才命中 p26 —— 课件把字母逐个分开了。
   - P2-2：搜 `Repeated` `reads/writes` `device memory`（只有那一行，无次数）。
   - P2-4：逐页核了 `2-4x`／`10-20x`（信实文本里是 `2` / `-` / `4x` 分行的形式）只出现在 **p22**。
   - 「掩码缺口」：搜正文 `掩码`（0）、`mask`（0）；源里 `mask` 恰 **1** 处（p10 的 `A = mask(A)`）；
     并回读了 `content/03-deep-learning-abstraction/index.md` 的 L98–L112 与 L234–L235。
6. **我换成别的写法找过的**：`FlasshAttention`（课件的拼写错误，2 处，页面未跟抄）；
  `Allamar` 与 `Alammar`（课件是 `Allamar`，3 处，页面跟课件写 ✅）；
  `N x N` 与 `L x L`（源里两种都出现：p10 用 `N x N`（2 处）、p6 的 Alammar 插图用 `L x L`（1 处）；
  页面统一用 `N`，与 p10 一致 ✅）。

---

## 覆盖面

- **正文**：`content/08-transformer-attention/index.md` **L1–L212 全读**（含 front matter、6 道自测题、溯源）。
  **断言命中数**：7 个不同的 `[[term:…]]`（引用 9 次）、**14 条** `](figures/…)`、**16 个** `##` 小节标题、
  正文出现「课件」**38 处**（我**逐处**核了它后面那句话在不在源里 —— P1-1 与 P2-3／P2-4 就是从这 38 处里挑出来的）、
  「第 5 讲」4 处、「第 3 讲」1 处、「第 6 讲」1 处。
- **源**：`07-transformers-attention.pdf` 的 faithful **30 页逐页读完**；为核 p11 的配对另读了该页的文本矩阵坐标
  （**补充手段，已在上文声明**）。
- **配图（两件事分开写）**：
  - **逐张通读：14 / 14 张**——每张 SVG 的**全部 `<text>` 文本节点 + `<title>` + `<desc>`** 都读了。
  - **定向检索：14 / 14 张**——逐张查 `20 MB`／`80 GB`／`19 TB/s`／`1.5 TB/s`／`65504`／`66.6`／`40.3`／`41.7`／`108`／
    `2 到 4`／`10 到 20`／`8 倍`／`掩码`／`结合律`／`kv-cache` 的命中
    （例如 `2 到 4 倍加速、10 到 20 倍显存下降` 在图 11 的可见文字与 desc 里各一次 ⇒ P2-4）。
  - **未做**：几何／箭头／位置／颜色的逐条复核（见「我核不到的」第 3 条）。
- **跨讲与元数据**：`mlsys-site-lectures.yml`（周次、日期、课件路径）、`content/03-deep-learning-abstraction/index.md`
  （注意力那一节 + 「第 8 讲会把它们讲透」那句承诺）、`content/05-optimizing-linear-algebra/index.md`（分块与内存层级）、
  `glossary.toml`（7/7 命中，含 `KV cache`）。
- **哈希**：正文 SHA256 已钉在文首（前 16 = `37F88D9EEF7D7C5A`，19,591 B）。源 PDF 的**取件三查**（体积 + `%%EOF` + 非 2 的幂）
  记在源材料表第 1 行。14 张配图本轮**只做文本层核对**，**没有**逐个钉哈希（若要钉，建议由 Lead 统一做，避免口径不一）。

---

**核对人声明**：本记录只覆盖基线前16 `37F88D9EEF7D7C5A`（19,591 B）。页面或配图再改动，结论不自动成立。
本记录**只读正文**，**不修改**任何 `content/` 下的文件，也不涉及 `status`（那是 Lead 的事）。
